# streamlit/pages/1_📌_Risco_Regulatorio.py
import streamlit as st
import pandas as pd
import numpy as np

from utils.data import load_model
from utils.metrics import (
    resolve_col,
    coerce_numeric,
    coerce_int,
    parse_date_key_yyyymmdd,
    safe_value_counts,
    add_risk_score,
)

st.set_page_config(page_title="Risco Regulatório", layout="wide")

st.title("🎯 Visão de Risco Regulatório")
st.caption("Processos ativos • tempo em aberto • gargalos por fase/órgão • score regulatório")

dims, fato = load_model()

if fato is None or len(fato) == 0:
    st.error(
        "⚠️ Não foi possível carregar a FATO_PROCESSO_REGULATORIO.\n\n"
        "Gere localmente e coloque em: gold/output/fato_processo_regulatorio.csv"
    )
    st.stop()

df = fato.copy()

# ----------------------------
# Resolver colunas
# ----------------------------
COL_ENC = resolve_col(df, ["processo_encerrado", "PROCESSO_ENCERRADO"])
COL_TTR = resolve_col(df, ["tempo_tramitacao_dias", "TEMPO_TRAMITACAO_DIAS"])
COL_TEA = resolve_col(df, ["tempo_em_aberto_dias", "TEMPO_EM_ABERTO_DIAS"])
COL_ANO = resolve_col(df, ["AnoProtocolo", "ANO_DO_PROTOCOLO", "ano_protocolo"])

COL_FASE = resolve_col(df, ["FASE_ATUAL", "fase_atual"])
COL_ORGAO = resolve_col(df, ["ORGAO", "ORGÃO", "ORGAO_PROCESSO", "ÓRGÃO", "ORGAO"])
COL_ATO = resolve_col(df, ["ATO", "ato"])
COL_CAT_ATO = resolve_col(df, ["CATEGORIA_ATO", "categoria_ato"])

# flags de divergência
COL_END_DIV = resolve_col(df, ["endereco_divergente_flag", "ENDERECO_DIVERGENTE_FLAG"])
COL_VAG_DIV = resolve_col(df, ["tem_divergencia_vagas", "TEM_DIVERGENCIA_VAGAS"])
COL_SEDE_EAD = resolve_col(df, ["is_sede_ead_flag", "IS_SEDE_EAD_FLAG"])

COL_DT_PROTO_KEY = resolve_col(df, ["dt_protocolo_key", "DT_PROTOCOLO_KEY"])
COL_DT_FASE_KEY = resolve_col(df, ["dt_entrada_fase_key", "DT_ENTRADA_FASE_KEY"])
COL_DT_ULT_KEY = resolve_col(df, ["dt_ultimo_ato_key", "DT_ULTIMO_ATO_KEY"])

# ----------------------------
# Tipos / Normalizações
# ----------------------------
if COL_ENC:
    df["_enc"] = coerce_int(df[COL_ENC]).fillna(0).astype(int)
else:
    df["_enc"] = 0

df["_ativo"] = (df["_enc"] == 0).astype(int)

if COL_TTR:
    df["_tempo_tram"] = coerce_numeric(df[COL_TTR])
else:
    df["_tempo_tram"] = np.nan

if COL_TEA:
    df["_tempo_aberto"] = coerce_numeric(df[COL_TEA])
else:
    df["_tempo_aberto"] = np.nan

# datas (se existirem)
if COL_DT_PROTO_KEY:
    df["_dt_protocolo"] = parse_date_key_yyyymmdd(df[COL_DT_PROTO_KEY])
else:
    df["_dt_protocolo"] = pd.NaT

if COL_DT_FASE_KEY:
    df["_dt_entrada_fase"] = parse_date_key_yyyymmdd(df[COL_DT_FASE_KEY])
else:
    df["_dt_entrada_fase"] = pd.NaT

if COL_DT_ULT_KEY:
    df["_dt_ultimo_ato"] = parse_date_key_yyyymmdd(df[COL_DT_ULT_KEY])
else:
    df["_dt_ultimo_ato"] = pd.NaT

# ----------------------------
# Score regulatório (Baixo/Médio/Alto)
# ----------------------------
df = add_risk_score(
    df,
    tempo_tramit_col="_tempo_tram",
    tempo_aberto_col="_tempo_aberto",
    fase_col=COL_FASE,
    ato_col=COL_ATO,
    cat_ato_col=COL_CAT_ATO,
    end_div_col=COL_END_DIV,
    vagas_div_col=COL_VAG_DIV,
    sede_ead_col=COL_SEDE_EAD,
)

# ----------------------------
# Sidebar: filtros básicos
# ----------------------------
with st.sidebar:
    st.header("🎛️ Filtros (Risco)")

    # ano
    anos = []
    if COL_ANO:
        anos = (
            coerce_int(df[COL_ANO])
            .dropna()
            .astype(int)
            .sort_values()
            .unique()
            .tolist()
        )
    ano_sel = st.multiselect("Ano do Protocolo", anos, default=anos[-5:] if len(anos) > 5 else anos)

    # risco
    riscos = ["Baixo", "Médio", "Alto"]
    risco_sel = st.multiselect("Faixa de risco", riscos, default=riscos)

    # ativo
    ativo_sel = st.selectbox("Situação", ["Todos", "Ativos", "Encerrados"], index=1)

# aplica filtros
df_view = df.copy()

if COL_ANO and len(ano_sel) > 0:
    ano_num = coerce_int(df_view[COL_ANO])
    df_view = df_view[ano_num.isin(ano_sel)]

if len(risco_sel) > 0:
    df_view = df_view[df_view["risco_faixa"].isin(risco_sel)]

if ativo_sel == "Ativos":
    df_view = df_view[df_view["_ativo"] == 1]
elif ativo_sel == "Encerrados":
    df_view = df_view[df_view["_ativo"] == 0]

# ----------------------------
# KPIs topo
# ----------------------------
c1, c2, c3, c4 = st.columns(4)

total = len(df_view)
ativos = int(df_view["_ativo"].sum()) if total else 0
encerrados = total - ativos

tempo_aberto_med = df_view["_tempo_aberto"].median(skipna=True) if total else np.nan
tempo_tram_med = df_view["_tempo_tram"].median(skipna=True) if total else np.nan

c1.metric("Registros (filtrados)", f"{total:,}".replace(",", "."))
c2.metric("Ativos", f"{ativos:,}".replace(",", "."))
c3.metric("Tempo em aberto (mediano)", "-" if np.isnan(tempo_aberto_med) else f"{int(tempo_aberto_med):,}".replace(",", "."))
c4.metric("Tempo tramitação (mediano)", "-" if np.isnan(tempo_tram_med) else f"{int(tempo_tram_med):,}".replace(",", "."))

st.divider()

# ----------------------------
# Backlog: Ativo vs Encerrado (por ano)
# ----------------------------
# 1) Identificar colunas no seu df (ajuste se já existirem no seu código)
COL_ANO = "_ano" if "_ano" in df.columns else ("AnoProtocolo" if "AnoProtocolo" in df.columns else None)
COL_ATIVO = "processo_ativo" if "processo_ativo" in df.columns else None
COL_ENC = "processo_encerrado" if "processo_encerrado" in df.columns else None

if COL_ANO is None:
    st.info("Não foi possível montar backlog: coluna de ano não encontrada.")
else:
    tmp = df.copy()
    tmp["_ano"] = pd.to_numeric(tmp[COL_ANO], errors="coerce")
    tmp = tmp.dropna(subset=["_ano"])
    tmp["_ano"] = tmp["_ano"].astype(int)

    # 2) Criar flags se necessário (ativo = 1 quando encerrado == 0)
    if COL_ENC and "processo_ativo" not in tmp.columns:
        tmp["processo_encerrado"] = pd.to_numeric(tmp[COL_ENC], errors="coerce").fillna(0).astype(int)
        tmp["processo_ativo"] = (tmp["processo_encerrado"] == 0).astype(int)

    # Se não tiver encerrado, pelo menos garante ativo (não ideal, mas não quebra)
    if "processo_ativo" not in tmp.columns:
        tmp["processo_ativo"] = 1

    if "processo_encerrado" not in tmp.columns:
        tmp["processo_encerrado"] = 0

    # 3) Agregar por ano
    backlog = (
        tmp.groupby("_ano")
           .agg(Ativos=("processo_ativo", "sum"),
                Encerrados=("processo_encerrado", "sum"))
           .reset_index()
           .sort_values("_ano")
    )

    # 4) Garantir colunas e tipos numéricos
    for c in ["Ativos", "Encerrados"]:
        if c not in backlog.columns:
            backlog[c] = 0
        backlog[c] = pd.to_numeric(backlog[c], errors="coerce").fillna(0)

    # 5) Plot
    st.subheader("📊 Backlog: Ativos vs Encerrados (por ano)")
    st.bar_chart(backlog, x="_ano", y=["Ativos", "Encerrados"])
# ----------------------------
# Pressão regulatória: % Ativos por ano
# ----------------------------
st.subheader("📈 Pressão regulatória (% de ativos por ano)")

if COL_ANO and total:
    tmp = df_view.copy()
    tmp["_ano"] = coerce_int(tmp[COL_ANO])
    tmp = tmp.dropna(subset=["_ano"])
    tmp["_ano"] = tmp["_ano"].astype(int)

    pressao = (
        tmp.groupby("_ano")["_ativo"]
        .mean()
        .mul(100)
        .reset_index(name="pct_ativos")
        .sort_values("_ano")
    )
    st.line_chart(pressao, x="_ano", y="pct_ativos")
else:
    st.info("Sem dados suficientes para calcular pressão regulatória.")

st.divider()

# ----------------------------
# Gargalos: fase e órgão (top)
# ----------------------------
colA, colB = st.columns(2)

with colA:
    st.subheader("⛔ Gargalos por Fase Atual (top 15)")
    if COL_FASE:
        tab_fase = safe_value_counts(df_view, COL_FASE, top=15, dropna=True)
        st.dataframe(tab_fase, use_container_width=True)
    else:
        st.info("Coluna FASE_ATUAL não encontrada.")

with colB:
    st.subheader("🏛️ Gargalos por Órgão (top 15)")
    if COL_ORGAO:
        tab_org = safe_value_counts(df_view, COL_ORGAO, top=15, dropna=True)
        st.dataframe(tab_org, use_container_width=True)
    else:
        st.info("Coluna ORGAO/ÓRGÃO não encontrada.")

st.divider()

# ----------------------------
# Score regulatório: distribuição
# ----------------------------
st.subheader("🧠 Distribuição do Score Regulatório")

dist = (
    df_view["risco_faixa"]
    .value_counts(dropna=False)
    .rename_axis("faixa")
    .reset_index(name="qtd")
)

st.bar_chart(dist, x="faixa", y="qtd")

st.caption("ℹ️ O score é derivado em Python a partir de tempo, divergências e criticidade do ato/fase.")
