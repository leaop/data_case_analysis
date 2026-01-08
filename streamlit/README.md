# 📊 Streamlit — Pipeline Regulatória (MEC/SERES)

Este app em Streamlit consome as tabelas da camada **Gold** (modelagem dimensional)
para disponibilizar um dashboard interativo de indicadores regulatórios-operacionais.

## 🎯 Objetivo
Permitir leitura gerencial e operacional do acervo regulatório, destacando:
- volume por ano de protocolo
- distribuição por UF
- backlog (ativos vs encerrados)
- visão de risco regulatório (score baixo/médio/alto)
- gargalos por fase / órgão

## 🧱 Fonte de dados
O app lê arquivos **CSV** gerados no pipeline (camada Gold), tipicamente em:

- `gold/output/dim_curso.csv`
- `gold/output/dim_ies.csv`
- `gold/output/dim_tempo.csv`
- `gold/output/dim_modalidade.csv`
- `gold/output/dim_local.csv`
- `gold/output/fato_processo_regulatorio.csv` *(pode não estar versionado)*

### ⚠️ Observação sobre dados grandes
A tabela fato e outros arquivos derivados podem **não ser versionados no GitHub** por:
- excederem o limite de 100MB
- boas práticas de engenharia (evitar versionar dados pesados e derivados)
- reprodutibilidade via pipeline local

➡️ O pipeline de geração está documentado no repositório e pode ser reproduzido localmente.

## 🧠 Métricas do dashboard
- **% encerrados (proxy)**: média do campo `processo_encerrado`
- **tempo mediano (dias)**: mediana de `tempo_tramitacao_dias`
- **backlog ativos vs encerrados**: agregado por ano do protocolo
- **score regulatório** (baixo/médio/alto): derivado em Python a partir de:
  - tempo de tramitação / tempo em aberto (quando disponível)
  - divergências (endereço/vagas)
  - criticidade do ato/categoria e fase

## ▶️ Como rodar localmente
Na raiz do repositório:

```bash
python -m pip install -r streamlit/requirements.txt
python -m streamlit run streamlit/app.py
