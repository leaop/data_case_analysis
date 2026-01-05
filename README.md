# data_case_analysis
# 📊 Case de Análise de Dados Regulatórios — MEC / SERES

Este repositório apresenta um **case completo de análise de dados regulatórios**, simulando uma **pipeline analítica real** para apoio à tomada de decisão no contexto do **MEC / SERES**, com foco em **regulação do ensino superior**.

O projeto foi desenvolvido com **dados anonimizados**, boas práticas de **engenharia de dados**, **análise exploratória**, **modelagem dimensional** e preparação para consumo em **Power BI**.

---

## 🎯 Objetivo do Projeto

Demonstrar, de ponta a ponta, como estruturar um projeto de dados que:

- Apoie decisões regulatórias e operacionais
- Organize dados complexos de processos administrativos
- Gere indicadores claros, rastreáveis e reproduzíveis
- Siga boas práticas esperadas de um **Data Analyst / Analytics Engineer (Jr–Pleno)**

Este case foi pensado para ser:
- Realista  
- Governamental  
- Rico em dados  
- Técnico  
- Explicável  
- Relevante para entrevistas e portfólio  

---

## 🧱 Arquitetura de Dados (Bronze / Silver / Gold)

O projeto segue uma arquitetura inspirada em **Data Lake / Medallion Architecture**:

### 🟤 Bronze — Dados Brutos
- Arquivos originais e intermediários
- Scripts de:
  - Anonimização
  - Troca de identificadores sensíveis
  - Enriquecimento CINE
- Notebooks de preparação inicial

📁 `bronze/`

---

### ⚪ Silver — Dados Tratados / Analíticos
- Bases anonimizadas e consolidadas (2018 e 2019+)
- Análises exploratórias (EDA)
- Indicadores regulatórios
- Comparações temporais (pré × pós)

📁 `silver/`

---

### 🟡 Gold — Modelo Analítico (Star Schema)
- Construção das **dimensões** e da **tabela fato**
- Dados prontos para consumo em BI

📁 `gold/`

Dimensões criadas:
- `DIM_IES`
- `DIM_CURSO`
- `DIM_TEMPO`
- `DIM_MODALIDADE`
- `DIM_LOCAL (UF / Município)`

Fato principal:
- `FATO_PROCESSO_REGULATORIO`

---

## ⭐ Modelagem Dimensional

O grão da tabela fato é:

> **1 linha = 1 processo regulatório**

A modelagem foi pensada para permitir análises como:
- Tempo médio de tramitação
- Volume de processos por UF, IES, modalidade e área CINE
- Diferenças entre EAD × Presencial
- Comparações pré e pós 2019
- Indicadores de risco e divergência regulatória

📐 O diagrama estrela pode ser facilmente recriado no **Power BI** ou **draw.io** a partir das tabelas da camada Gold.

---

## 🔐 Observação Importante sobre os Dados

⚠️ **Observação sobre versionamento de dados**

Os arquivos de saída da camada **Gold**, em especial a tabela:


**não são versionados no GitHub**, pelos seguintes motivos:

- Excedem o limite de 100MB do GitHub
- Seguem boas práticas de engenharia de dados
- Evitam versionamento de dados pesados e derivados

👉 **Todo o pipeline de geração dessas tabelas está documentado neste repositório**  
👉 As tabelas podem ser **reproduzidas localmente** a partir dos dados anonimizados da camada Silver  

> Esse tipo de decisão é comum em ambientes reais e bem avaliado por recrutadores técnicos.

---

## 🧰 Stack Tecnológica Utilizada

- **Python** (pandas, numpy, matplotlib)
- **Jupyter Notebooks**
- **Modelagem Dimensional**
- **Power BI** (consumo final)
- **Git & GitHub**
- **Excel** (QA e apoio)

---

## 📌 Observações Finais

- Nenhum dado sensível real é exposto
- O foco do projeto é **estrutura, lógica, clareza e reprodutibilidade**
- O case foi desenhado para refletir desafios reais do setor público e educacional

---

📬 Em caso de dúvidas ou interesse em discutir o projeto, fique à vontade para entrar em contato.



