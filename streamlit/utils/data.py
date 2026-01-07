from pathlib import Path
import pandas as pd
import streamlit as st

# =====================================================
# Paths
# =====================================================
BASE_DIR = Path(__file__).resolve().parents[2]  # raiz do repo
GOLD_DIR = BASE_DIR / "gold"
GOLD_OUTPUT_DIR = GOLD_DIR / "output"


# =====================================================
# Column normalization (semantic layer for Streamlit)
# =====================================================
# Ajuste este mapa conforme suas colunas reais do CSV da FATO.
# A ideia é: "nome do arquivo" -> "nome canônico esperado no app.py"
COLUMN_MAP_FATO = {
    # Tempo / Local / Modalidade
    "ANO_DO_PROTOCOLO": "AnoProtocolo",
    "UF_PROCESSO": "UF",
    "UF_CADASTRO": "UF",
    "MODALIDADE": "Modalidade_norm",

    # Métricas / Flags (se existirem no seu fato)
    "TEMPO_TRAMITACAO_DIAS": "tempo_tramitacao_dias",
    "PROCESSO_ENCERRADO": "processo_encerrado",
    "FLAG_RISCO_ALTO": "flag_risco_alto",

    # Público/Privado (se você já criou isso no pipeline)
    "PUBLICAPRIVADA": "PublicaPrivada",
    "PUBLICA_PRIVADA": "PublicaPrivada",
    "CATEGORIA_ADMINISTRATIVA": "PublicaPrivada",
}

COLUMN_MAP_DIM_TEMPO = {
    "ANO_DO_PROTOCOLO": "AnoProtocolo",
}

COLUMN_MAP_DIM_LOCAL = {
    "UF_PROCESSO": "UF",
    "UF_CADASTRO": "UF",
}

COLUMN_MAP_DIM_MODALIDADE = {
    "MODALIDADE": "Modalidade_norm",
}


def normalize_columns(df: pd.DataFrame, col_map: dict) -> pd.DataFrame:
    """Renomeia colunas conforme dicionário e padroniza trims básicos."""
    if df is None or df.empty:
        return df

    # Renomear somente as que existem
    rename = {c: col_map[c] for c in df.columns if c in col_map}
    df = df.rename(columns=rename)

    # Pequena limpeza: remover espaços em nomes de colunas
    df.columns = [c.strip() for c in df.columns]

    return df


# =====================================================
# Loaders
# =====================================================
def load_csv(filename: str) -> pd.DataFrame | None:
    """Carrega CSV procurando em caminhos padrão (gold/output e gold/)."""
    paths = [
        GOLD_OUTPUT_DIR / filename,
        GOLD_DIR / filename,
    ]

    for path in paths:
        if path.exists():
            return pd.read_csv(path, dtype=str, low_memory=False)

    return None


@st.cache_data
def load_model():
    """
    Carrega modelo dimensional.
    O fato pode não existir (intencional).
    Retorna: (dims: dict[str, DataFrame], fato: DataFrame|None)
    """
    dims = {}

    dims["dim_curso"] = load_csv("dim_curso.csv")
    dims["dim_ies"] = load_csv("dim_ies.csv")
    dims["dim_tempo"] = load_csv("dim_tempo.csv")
    dims["dim_modalidade"] = load_csv("dim_modalidade.csv")
    dims["dim_local"] = load_csv("dim_local.csv")

    # Normalizar dimensões (apenas se o app usar colunas diretas delas)
    dims["dim_tempo"] = normalize_columns(dims["dim_tempo"], COLUMN_MAP_DIM_TEMPO)
    dims["dim_local"] = normalize_columns(dims["dim_local"], COLUMN_MAP_DIM_LOCAL)
    dims["dim_modalidade"] = normalize_columns(dims["dim_modalidade"], COLUMN_MAP_DIM_MODALIDADE)

    # Fato
    fato = load_csv("fato_processo_regulatorio.csv")
    fato = normalize_columns(fato, COLUMN_MAP_FATO)

    if fato is None:
        st.warning(
            "⚠️ A tabela FATO_PROCESSO_REGULATORIO não está disponível no repositório.\n\n"
            "Ela não é versionada por tamanho e boas práticas.\n"
            "O pipeline completo para gerá-la está documentado."
        )

    return dims, fato
