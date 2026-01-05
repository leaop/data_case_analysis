# 📘 Dicionário de Dados — Processos Regulatórios

Este documento descreve os principais campos utilizados no projeto,
seus significados, origem e uso analítico.

---

## 🔹 Tabela FATO_PROCESSO_REGULATORIO

| Campo | Tipo | Descrição | Origem |
|-----|-----|----------|--------|
| id_processo | string | Identificador único do processo | Sistema regulatório |
| id_ies | string | Identificador da instituição | Cadastro IES |
| modalidade_norm | string | Modalidade normalizada (EAD, Presencial) | Campo Modalidade |
| tempo_tramitacao_dias | int | Tempo total do processo em dias | Calculado |
| is_sede_ead_flag | int (0/1) | Indica se o processo envolve sede EAD | IS_SEDE_EAD |
| endereco_divergente_flag | int (0/1) | Indica divergência entre endereços | ENDERECO_DIVERGENTE |
| cine_area_geral | string | Área CINE geral do curso | Enriquecimento CINE |
| ano_do_protocolo | int | Ano de entrada do processo | ANO_DO_PROTOCOLO |

## 🔹 DIM_IES — Instituições de Ensino

| Campo | Tipo | Descrição |
|-----|-----|----------|
| id_ies | string | Identificador único da IES |
| nome_ies | string | Nome da instituição (anonimizado) |
| categoria_administrativa | string | Pública ou Privada |
| ambito_administrativo | string | Federal, Estadual, Municipal |
| organizacao_academica | string | Universidade, Centro Universitário etc |
| uf | string | Unidade da Federação |

## 🔹 DIM_CURSO — Cursos

| Campo | Tipo | Descrição |
|-----|-----|----------|
| id_curso | string | Identificador do curso |
| nome_curso | string | Nome do curso |
| grau | string | Grau acadêmico |
| carga_horaria | int | Carga horária total |
| cine_area_geral | string | Área CINE geral |

## 🔹 DIM_LOCAL — Localização

| Campo | Tipo | Descrição |
|-----|-----|----------|
| id_local | int | Identificador da localidade |
| uf | string | Unidade da Federação |
| municipio | string | Município |

## 🔹 DIM_MODALIDADE — Modalidade de Oferta

| Campo | Tipo | Descrição |
|-----|-----|----------|
| id_modalidade | int | Identificador da modalidade |
| modalidade_norm | string | EAD, Presencial, Semipresencial |


## 🔹 DIM_TEMPO — Tempo

| Campo | Tipo | Descrição |
|-----|-----|----------|
| id_data | int | Chave da data (YYYYMMDD) |
| data | date | Data calendário |
| ano | int | Ano |
| mes | int | Mês |
| trimestre | int | Trimestre |

