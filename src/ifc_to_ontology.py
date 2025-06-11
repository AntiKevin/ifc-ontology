import ifcopenshell
from rdflib import Graph, Namespace, URIRef, Literal, RDF, RDFS, OWL
import re
from rdflib.namespace import SH
from pyshacl import validate
from py2neo import Graph as Neo4jGraph, Node, Relationship
from ollama import chat, ChatResponse

IFC_FILE = "./data/Building-Architecture.ifc"
model = ifcopenshell.open(IFC_FILE)
produtos = model.by_type("IfcProduct")

NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "ifc123456"
NEO4J_DATABASE = "ifctest"

IFC_NS = Namespace("http://example.org/ifc/")
PROP_NS = Namespace("http://example.org/ifc/property#")
SHACL_NS = Namespace("http://www.w3.org/ns/shacl#")

# Inicializar grafo RDF
rdf_graph = Graph()
rdf_graph.bind("ifc", IFC_NS)
rdf_graph.bind("prop", PROP_NS)

neo4j_graph = Neo4jGraph(
    uri=NEO4J_URI,
    auth=(NEO4J_USER, NEO4J_PASSWORD),
)

# Limpar o grafo Neo4j antes de inserir novos dados
neo4j_graph.delete_all()

# Função auxiliar para converter GlobalId para URI
def globalid_to_uri(global_id):
    return URIRef(IFC_NS[global_id])

# Função para adicionar entidades ao grafo Neo4j
def add_entity_to_neo4j(entity):
    uri = globalid_to_uri(entity.GlobalId)
    node = Node("IfcProduct", global_id=entity.GlobalId, name=entity.Name or "")
    neo4j_graph.create(node)
    
    for key, value in entity.get_info(recursive=False).items():
        if key not in ['GlobalId', 'OwnerHistory', 'Name', 'type']:
            if isinstance(value, ifcopenshell.entity_instance):
                # Only create relationship if the referenced entity has a GlobalId
                if hasattr(value, "GlobalId") and value.GlobalId:
                    rel = Relationship(node, key, Node("IfcProduct", global_id=value.GlobalId))
                    neo4j_graph.create(rel)
            elif isinstance(value, (list, tuple)):
                for item in value:
                    if isinstance(item, ifcopenshell.entity_instance):
                        if hasattr(item, "GlobalId") and item.GlobalId:
                            rel = Relationship(node, key, Node("IfcProduct", global_id=item.GlobalId))
                            neo4j_graph.create(rel)

for produto in produtos:
    if not produto.GlobalId:
        continue
    add_entity_to_neo4j(produto)


# 1. Popular entidades e propriedades básicas
for element in produtos:
    if not element.GlobalId:
        continue
        
    uri = URIRef(IFC_NS[element.GlobalId])
    
    # Adicionar tipo da entidade
    rdf_graph.add((uri, RDF.type, URIRef(IFC_NS[element.is_a()])))
    
    # Adicionar nome se existir
    if element.Name:
        rdf_graph.add((uri, IFC_NS["name"], Literal(element.Name)))
    
    # Adicionar propriedades de relacionamento
    info = element.get_info(recursive=False)
    for key, value in info.items():
        # Pular atributos já processados ou não relevantes
        if key in ['GlobalId', 'OwnerHistory', 'Name', 'type']:
            continue
            
        # Processar referências para outras entidades
        if isinstance(value, ifcopenshell.entity_instance):
            if value.is_a("IfcProduct"):
                ref_uri = URIRef(IFC_NS[value.GlobalId])
                rdf_graph.add((uri, PROP_NS[key], ref_uri))
                
        elif isinstance(value, (list, tuple)):
            for item in value:
                if isinstance(item, ifcopenshell.entity_instance) and item.is_a("IfcProduct"):
                    ref_uri = URIRef(IFC_NS[item.GlobalId])
                    rdf_graph.add((uri, PROP_NS[key], ref_uri))

shacl_shapes = f"""
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix sh: <{SH}> .
@prefix ifc: <{IFC_NS}> .
@prefix prop: <{PROP_NS}> .

# Regra 1: Paredes devem estar contidas em estruturas espaciais
ifc:WallContainmentRule
    a sh:NodeShape ;
    sh:targetClass ifc:IfcWall ;
    sh:property [
        sh:path prop:ContainedInStructure ;
        sh:class ifc:IfcSpatialStructureElement ;
        sh:minCount 1 ;
        sh:maxCount 1 ;
        sh:message "Paredes devem estar contidas em exatamente uma estrutura espacial (andar/edifício)" ;
    ] .

# Regra 2: Portas devem ser instaladas em paredes
ifc:DoorInstallationRule
    a sh:NodeShape ;
    sh:targetClass ifc:IfcDoor ;
    sh:property [
        sh:path prop:FillsVoids ;
        sh:class ifc:IfcWall ;
        sh:minCount 1 ;
        sh:message "Portas devem ser instaladas em paredes" ;
    ] .

# Regra 3: Pisos devem ter relações com edificações
ifc:SlabContainmentRule
    a sh:NodeShape ;
    sh:targetClass ifc:IfcSlab ;
    sh:property [
        sh:path prop:ContainedInStructure ;
        sh:class ifc:IfcBuilding ;
        sh:minCount 1 ;
        sh:message "Pisos devem estar contidos em edificações" ;
    ] .

# Regra 4: Relações espaciais devem ter tipos válidos
ifc:ValidRelationRule
    a sh:PropertyShape ;
    sh:path prop:RelatingSpace ;
    sh:class ifc:IfcSpace ;
    sh:message "Elementos só podem relacionar-se com espaços válidos" .
"""

# 3. Validar o grafo com as regras SHACL
shacl_graph = Graph().parse(data=shacl_shapes, format="turtle")
conforms, results_graph, results_text = validate(
    rdf_graph,
    shacl_graph=shacl_graph,
    ont_graph=None,
    inference='rdfs',
    abort_on_first=False,
    meta_shacl=False,
    advanced=True,
    debug=False
)

# 4. Analisar e reportar resultados
print("\n" + "="*50)
print("Resultado da Validação de Conformidade")
print("="*50)

if conforms:
    print("Nenhum conflito detectado: O modelo está em conformidade com a ontologia")
else:
    print(f"Foram encontrados {len(results_graph)} conflitos ontológicos:")
    
    conflicts = []
    for s in results_graph.subjects(SH.resultSeverity, SH.Violation):
        conflict = {
            "element": results_graph.value(s, SH.focusNode),
            "message": results_graph.value(s, SH.resultMessage),
            "path": results_graph.value(s, SH.resultPath),
            "severity": "Violação"
        }
        conflicts.append(conflict)
        
    for i, conflict in enumerate(conflicts, 1):
        print(f"\nConflito #{i}:")
        print(f"Elemento: {conflict['element']}")
        print(f"Mensagem: {conflict['message']}")
        print(f"Propriedade: {conflict['path']}")
        print(f"Severidade: {conflict['severity']}")
        
        # ===========================================
        # Sugestão de correção usando LLM
        # ===========================================
        
        prompt = f"""
        personalidade: Você é um especialista em validação de modelos IFC (Industry Foundation Classes) e ontologias que responde de forma bem bem curta mas precisa (menos de 4 linhas sempre).
        tarefa: Fornecer sugestões de correção para conflitos encontrados em um modelo IFC.
        Problema: {conflict['message']} 
        Elemento: {conflict['element']}
        Propriedade: {conflict['path']}
        Tarefa: Sugira uma correção técnica para este problema.
        """
        
        response: ChatResponse = chat(model='gemma3:4b', messages=[
        {
            'role': 'user',
            'content': prompt,
        },
        ])
        
        correction_suggestion = response.message.content
        if not correction_suggestion:
            correction_suggestion = "Nenhuma sugestão de correção disponível."
                
        
        print(f"Sugestão de Correção: {correction_suggestion}")
        conflict["sugestion"] = correction_suggestion
    
    conflicts_text = "\n".join(
        [f"Conflito #{i+1}: {conflict['message']} \n Sugestão: {conflict['sugestion']} \n Elemento: {conflict['element']} \n" for i, conflict in enumerate(conflicts)]
    )

rdf_graph.serialize("./data/output/ifc_graph.ttl", format="turtle")
with open("./data/output/validation_report.txt", "w") as f:
    f.write(conflicts_text)

print("\nValidação concluída. Relatório salvo em 'validation_report.txt'")