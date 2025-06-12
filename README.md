# 🏗️ IFC Ontology para Modelagem da Informação da Construção (BIM)

<div align="center">
  <img src="https://img.shields.io/badge/Python-3.x-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python Version Badge"/>
  <img src="https://img.shields.io/badge/Tecnologias-RDF%2C%20SHACL%2C%20Neo4j%2C%20LLMs-blueviolet?style=for-the-badge" alt="Technologies Badge"/>
  <img src="https://img.shields.io/badge/Status-Em%20Desenvolvimento-orange?style=for-the-badge" alt="Status Badge"/>
  <img src="https://img.shields.io/badge/Licença-MIT-blue?style=for-the-badge" alt="License Badge"/>
</div>

## 📋 Sobre o Projeto

Este repositório apresenta um projeto inovador focado na aplicação de ontologias para a validação e análise de modelos IFC (Industry Foundation Classes) no contexto de Building Information Modeling (BIM). O objetivo central é demonstrar como a integração de dados IFC com ontologias pode significativamente aprimorar a detecção de conflitos e a garantia de conformidade em modelos BIM. Para isso, o projeto faz uso de tecnologias de ponta como RDF, SHACL e Neo4j, e ainda incorpora capacidades de Large Language Models (LLMs) para oferecer sugestões inteligentes de correção para os problemas identificados.

## ✨ Funcionalidades Principais

- 🔄 **Conversão de IFC para Grafo de Conhecimento:** Processa arquivos IFC, transformando-os em um grafo de conhecimento RDF. Isso permite uma representação semântica rica das entidades do modelo e seus relacionamentos, facilitando análises complexas.
- ✅ **Validação de Conformidade SHACL:** Utiliza regras SHACL (Shapes Constraint Language) para validar a conformidade dos modelos IFC. Este processo identifica automaticamente inconsistências e potenciais conflitos em relação a ontologias predefinidas, garantindo a integridade do modelo.
- 📊 **Integração com Banco de Dados de Grafo Neo4j:** O grafo de conhecimento gerado é persistido em um banco de dados de grafo Neo4j. Isso otimiza a capacidade de realizar consultas complexas e explorar as relações entre os elementos do modelo de forma eficiente.
- 🔍 **Detecção Inteligente de Conflitos e Sugestões:** Além de identificar conflitos ontológicos, o projeto emprega um Large Language Model (LLM) para gerar sugestões de correção contextuais e acionáveis, auxiliando na resolução rápida dos problemas.
- 📄 **Geração de Relatórios Detalhados:** Produz relatórios de validação abrangentes, que incluem descrições claras dos conflitos encontrados, mensagens de erro específicas e as sugestões de correção fornecidas pelo LLM, facilitando o processo de depuração e melhoria do modelo.




## 🛠️ Tecnologias Utilizadas

Este projeto foi desenvolvido utilizando as seguintes tecnologias e bibliotecas:

- **Python 3.8+**: A linguagem de programação principal que orquestra todas as operações.
- **ifcopenshell**: Uma poderosa biblioteca Python para a manipulação, leitura e escrita de arquivos IFC, essencial para a extração de dados do modelo BIM.
- **rdflib**: Biblioteca fundamental para trabalhar com RDF (Resource Description Framework), permitindo a criação e manipulação do grafo de conhecimento.
- **pyshacl**: Implementação Python da SHACL (Shapes Constraint Language), utilizada para definir e aplicar regras de validação sobre o grafo RDF, garantindo a conformidade ontológica.
- **py2neo**: Uma biblioteca robusta para a interação com o banco de dados de grafo Neo4j, facilitando a persistência e consulta dos dados do grafo de conhecimento.
- **Neo4j**: Um banco de dados de grafo de alto desempenho, empregado para armazenar o grafo de conhecimento IFC, otimizando a exploração de relacionamentos complexos entre os elementos do modelo.
- **Ollama**: Um framework que permite a execução e gerenciamento de Large Language Models (LLMs) localmente. É utilizado para gerar sugestões inteligentes de correção para os conflitos detectados, adicionando uma camada de inteligência artificial ao processo de validação.
- **Jupyter Notebook**: Ferramenta interativa amplamente utilizada para prototipagem, análise exploratória de dados e visualização dos resultados do processamento e validação.




## 🚀 Como Utilizar

Para configurar e executar este projeto em seu ambiente local, siga os passos detalhados abaixo:

### Pré-requisitos

Certifique-se de que os seguintes softwares estão instalados em seu sistema:

- **Python 3.8+**: A versão do Python recomendada para a execução do projeto.
- **Docker**: Essencial para a orquestração e execução dos serviços de banco de dados Neo4j e do framework Ollama.

### Configuração do Ambiente

1.  **Clone o repositório:**

    Comece clonando o projeto para o seu ambiente local utilizando o Git:

    ```bash
    git clone https://github.com/AntiKevin/ifc-ontology.git
    cd ifc-ontology
    ```

2.  **Crie e ative um ambiente virtual:**

    É altamente recomendável utilizar um ambiente virtual para gerenciar as dependências do projeto, evitando conflitos com outras instalações Python:

    ```bash
    python3 -m venv venv
    # Para Linux/macOS:
    source venv/bin/activate
    # Para Windows PowerShell:
    # .\venv\Scripts\activate
    ```

3.  **Instale as dependências:**

    Com o ambiente virtual ativado, instale todas as bibliotecas Python necessárias listadas no arquivo `requirements.txt`:

    ```bash
    pip install -r requirements.txt
    ```

4.  **Inicie o Neo4j e o Ollama com Docker Compose:**

    O projeto utiliza Neo4j para persistência do grafo de conhecimento e Ollama para as funcionalidades de LLM. Ambos podem ser facilmente iniciados via Docker Compose. Certifique-se de ter um arquivo `docker-compose.yml` configurado na raiz do projeto. Se não houver, você pode criar um com o conteúdo abaixo:

    ```yaml
    version: '3.8'

    services:
      neo4j:
        image: neo4j:latest
        hostname: neo4j
        ports:
          - "7474:7474"
          - "7687:7687"
        environment:
          - NEO4J_AUTH=neo4j/ifc123456  # Usuário e senha padrão
          - NEO4J_db_name=ifctest
        volumes:
          - ./neo4j_data:/data  # Mapeia um volume para persistência dos dados do Neo4j

      ollama:
        image: ollama/ollama:latest
        hostname: ollama
        ports:
          - "11434:11434"
        volumes:
          - ./ollama_data:/root/.ollama  # Mapeia um volume para persistência dos modelos do Ollama
    ```

    Após configurar o `docker-compose.yml`, inicie os serviços:

    ```bash
    docker-compose up -d
    ```

    **Importante:** Para o Ollama, você precisará baixar o modelo `gemma3:4b` antes de executar o script principal. Faça isso com o seguinte comando:

    ```bash
    ollama pull gemma3:4b
    ```

### Execução do Projeto

1.  **Execute o script principal:**

    Com todas as dependências instaladas e os serviços Docker em execução, você pode iniciar o processamento e a validação do modelo IFC:

    ```bash
    python src/ifc_to_ontology.py
    ```

    Este script realizará as seguintes operações:
    - Processará o arquivo IFC de entrada (`./data/Building-Architecture.ifc`).
    - Gerará o grafo RDF correspondente.
    - Executará a validação de conformidade SHACL.
    - Armazenará os dados no banco de dados Neo4j.
    - Gerará um relatório de validação detalhado, incluindo sugestões de correção fornecidas pelo LLM.

2.  **Explore os notebooks Jupyter (Opcional):**

    Para uma análise mais aprofundada e interativa dos dados e do processo de validação, você pode explorar os notebooks Jupyter incluídos no projeto:

    ```bash
    jupyter notebook
    ```

    Abra os notebooks `ifc_conflict_detection.ipynb` e `ifc_to_graph.ipynb` localizados na pasta `notebooks` para visualizar e interagir com os resultados.

## 📁 Estrutura do Projeto

A organização do repositório segue uma estrutura clara para facilitar a navegação e o entendimento do projeto:

```
ifc-ontology/
├── data/                            # Contém arquivos de dados e saídas
│   ├── Building-Architecture.ifc    # Exemplo de arquivo IFC para processamento
│   ├── ifc-ontology.ttl             # Definição da ontologia IFC em formato Turtle
│   └── output/                      # Diretório para arquivos de saída gerados
│       ├── ifc_graph.ttl            # Grafo RDF resultante da conversão do IFC
│       └── validation_report.txt    # Relatório detalhado dos resultados da validação
├── notebooks/                       # Notebooks Jupyter para análise e exploração
│   ├── ifc_conflict_detection.ipynb # Notebook para detecção e análise de conflitos
│   └── ifc_to_graph.ipynb           # Notebook para visualização da conversão IFC para grafo
├── src/                             # Código-fonte principal do projeto
│   └── ifc_to_ontology.py           # Script principal de processamento e validação
├── .gitignore                       # Define arquivos e diretórios a serem ignorados pelo Git
├── README.md                        # Este arquivo de documentação do projeto
└── requirements.txt                 # Lista de dependências Python do projeto
```

## 🤝 Contribuição

Contribuições são muito bem-vindas! Se você tiver sugestões de melhoria, encontrar algum bug ou quiser adicionar novas funcionalidades, sinta-se à vontade para:

- Abrir uma *issue* para relatar problemas ou propor ideias.
- Enviar um *pull request* com suas alterações. Certifique-se de descrever claramente as modificações e o problema que elas resolvem.

## 👨‍💻 Colaboradores

<div align="center">
  <img src="https://avatars.githubusercontent.com/u/7960296?v=4" width="100px" style="border-radius: 50%" alt="Foto de AntiKevin"/>
  <br/>
  <strong>AntiKevin</strong>
  <br/>
  <a href="https://github.com/AntiKevin">
    <img src="https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white" alt="GitHub Badge"/>
  </a>
</div>

<div align="center">
  <img src="https://avatars.githubusercontent.com/u/149385663?v=4" width="100px" style="border-radius: 50%" alt="Foto de xthgo19"/>
  <br/>
  <strong>xthgo19</strong>
  <br/>
  <a href="https://github.com/xthgo19">
    <img src="https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white" alt="GitHub Badge"/>
  </a>
</div>

<div align="center">
  <img src="https://avatars.githubusercontent.com/u/100000000?v=4" width="100px" style="border-radius: 50%" alt="Foto de IsaqueCostaa"/>
  <br/>
  <strong>IsaqueCostaa</strong>
  <br/>
  <a href="https://github.com/IsaqueCostaa">
    <img src="https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white" alt="GitHub Badge"/>
  </a>
</div>

---

<div align="center">
  <p>⭐ Se este projeto foi útil, considere dar uma estrela no repositório! ⭐</p>
  <p>Desenvolvido com Python 🐍 e o poder das Ontologias e LLMs</p>
</div>

