# streamlit/app.py
import streamlit as st
import pandas as pd

from utils.data import load_model
from utils.metrics import (
    resolve_col,
    safe_mean_pct,
    safe_median,
    unique_sorted_int_list,
    unique_sorted_str_list,
)

# ---------------------------------------------------------
# Configuração da página
# ---------------------------------------------------------
st.set_page_config(
    page_title="Pipeline Regulatória (MEC/SERES) — Dashboard",
    layout="wide",
)

st.title("📊 Pipeline Regulatória (MEC/SERES) — Dashboard")
st.caption(
    "Base anonimizada • Camadas Bronze/Silver/Gold • Indicadores regulatórios-operacionais"
)

# ---------------------------------------------------------
# Carregar modelo (dimensões + fato)
# ---------------------------------------------------------
dims, fato = load_model()

if fato is None or len(fato) == 0:
    st.error(
        "⚠️ A tabela FATO_PROCESSO_REGULATORIO não está disponível.\n\n"
        "Ela não é versionada no GitHub por boas práticas e limite de tamanho.\n"
        "➡️ Gere localmente o CSV e coloque em: gold/output/fato_processo_regulatorio.csv"
    )
    st.stop()

df_base = fato.copy()

# ---------------------------------------------------------
# Dimensões (podem ser None)
# ---------------------------------------------------------
dim_modalidade = dims.get("dim_modalidade")
dim_ies = dims.get("dim_ies")
dim_tempo = dims.get("dim_tempo")

# ---------------------------------------------------------
# Resolver colunas reais da FATO
# ---------------------------------------------------------
COL_ANO = resolve_col(df_base, ["AnoProtocolo", "ANO_DO_PROTOCOLO", "ano_protocolo"])
COL_UF = resolve_col(df_base, ["uf", "UF"])

# ✅ SUA FATO TEM modalidade_norm
COL_MOD_TXT = resolve_col(df_base, ["modalidade_norm", "Modalidade_norm"])

# Pública/Privada normalmente NÃO está na FATO
COL_PP_TXT = resolve_col(df_base, ["PublicaPrivada", "publica_privada"])

# IDs para fallback
COL_ID_MOD = resolve_col(df_base, ["id_modalidade"])
COL_ID_IES = resolve_col(df_base, ["id_ies"])

# Métricas
COL_TEMPO = resolve_col(df_base, ["tempo_tramitacao_dias"])
COL_ENC = resolve_col(df_base, ["processo_encerrado"])
COL_RISCO = resolve_col(df_base, ["flag_risco_alto"])

# ---------------------------------------------------------
# Sidebar — Filtros
# ---------------------------------------------------------
with st.sidebar:
    st.header("🎛️ Filtros")

    # Ano
    anos = unique_sorted_int_list(df_base, COL_ANO) if COL_ANO else []
    ano_default = anos[-5:] if len(anos) > 5 else anos
    ano_sel = st.multiselect("Ano do Protocolo", anos, default=ano_default)

    # UF
    ufs = unique_sorted_str_list(df_base, COL_UF) if COL_UF else []
    uf_sel = st.multiselect("UF", ufs, default=[])

    # Modalidade (vem direto da FATO)
    mods = unique_sorted_str_list(df_base, COL_MOD_TXT) if COL_MOD_TXT else []
    mod_sel = st.multiselect("Modalidade", mods, default=[])

    # Pública / Privada (vem da DIM_IES)
    if isinstance(dim_ies, pd.DataFrame) and len(dim_ies) > 0:
        col_pp_dim = resolve_col(dim_ies, ["PublicaPrivada", "publica_privada"])
        pps = unique_sorted_str_list(dim_ies, col_pp_dim) if col_pp_dim else []
    else:
        pps = []
    pp_sel = st.multiselect("Pública / Privada", pps, default=[])

# ---------------------------------------------------------
# Aplicar filtros
# ---------------------------------------------------------
df = df_base.copy()

# Ano
if COL_ANO and ano_sel:
    df["_ano"] = pd.to_numeric(df[COL_ANO], errors="coerce")
    df = df[df["_ano"].isin(ano_sel)]

# UF
if COL_UF and uf_sel:
    df = df[df[COL_UF].isin(uf_sel)]

# Modalidade
if COL_MOD_TXT and mod_sel:
    df = df[df[COL_MOD_TXT].isin(mod_sel)]

# Pública / Privada (via DIM_IES)
if pp_sel and COL_ID_IES and isinstance(dim_ies, pd.DataFrame):
    col_pp_dim = resolve_col(dim_ies, ["PublicaPrivada", "publica_privada"])
    col_id_ies_dim = resolve_col(dim_ies, ["id_ies"])
    if col_pp_dim and col_id_ies_dim:
        ids_ies = (
            dim_ies[dim_ies[col_pp_dim].isin(pp_sel)][col_id_ies_dim]
            .astype(str)
            .unique()
            .tolist()
        )
        df = df[df[COL_ID_IES].astype(str).isin(ids_ies)]

# ---------------------------------------------------------
# KPIs
# ---------------------------------------------------------
c1, c2, c3, c4 = st.columns(4)

total = len(df)
pct_enc = safe_mean_pct(df, COL_ENC) if COL_ENC else 0.0
med_tempo = safe_median(df, COL_TEMPO) if COL_TEMPO else None
pct_risco = safe_mean_pct(df, COL_RISCO) if COL_RISCO else 0.0

c1.metric("Registros (filtrados)", f"{total:,}".replace(",", "."))
c2.metric("% Encerrados (proxy)", f"{pct_enc:.1f}%")
c3.metric(
    "Tempo mediano (dias)",
    "-" if med_tempo is None else f"{int(med_tempo):,}".replace(",", "."),
)
c4.metric("% Risco alto (proxy)", f"{pct_risco:.1f}%")

st.divider()

# ---------------------------------------------------------
# Volume por Ano
# ---------------------------------------------------------
st.subheader("📈 Volume por ano de protocolo")

if COL_ANO:
    by_year = (
        df.assign(_ano=pd.to_numeric(df[COL_ANO], errors="coerce"))
        .dropna(subset=["_ano"])
        .assign(_ano=lambda x: x["_ano"].astype(int))
        .groupby("_ano")
        .size()
        .reset_index(name="qtd")
        .sort_values("_ano")
    )
    st.bar_chart(by_year, x="_ano", y="qtd")
else:
    st.info("Ano do protocolo não disponível.")

# ---------------------------------------------------------
# Distribuição por UF
# ---------------------------------------------------------
st.subheader("🗺️ Distribuição por UF")

if COL_UF:
    by_uf = (
        df.groupby(COL_UF)
        .size()
        .reset_index(name="qtd")
        .sort_values("qtd", ascending=False)
        .head(27)
    )
    st.dataframe(by_uf, use_container_width=True)
else:
    st.info("UF não disponível.")

# ---------------------------------------------------------
# Distribuição por Modalidade
# ---------------------------------------------------------
st.subheader("🏷️ Distribuição por Modalidade")

if COL_MOD_TXT:
    by_mod = (
        df.groupby(COL_MOD_TXT)
        .size()
        .reset_index(name="qtd")
        .sort_values("qtd", ascending=False)
    )
    st.dataframe(by_mod, use_container_width=True)
else:
    st.info("Modalidade não disponível na FATO.")

# ---------------------------------------------------------
# DEBUG (pode remover depois)
# ---------------------------------------------------------
st.write("DEBUG — Colunas da FATO:", list(df_base.columns))

