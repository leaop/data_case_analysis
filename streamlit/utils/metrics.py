# streamlit/utils/metrics.py
from __future__ import annotations

import numpy as np
import pandas as pd


def resolve_col(df: pd.DataFrame, candidates: list[str]) -> str | None:
    """Retorna o primeiro nome de coluna existente no df dentre os candidatos."""
    if df is None or len(df.columns) == 0:
        return None
    cols = set(df.columns)
    for c in candidates:
        if c in cols:
            return c
    return None


def coerce_numeric(s: pd.Series) -> pd.Series:
    """
    Converte para número de forma tolerante.
    - Aceita strings com vírgula decimal e valores como '135.0'
    - Remove espaços
    """
    if s is None:
        return pd.Series(dtype="float64")

    x = s.astype(str).str.strip()

    # normaliza decimal BR -> EN quando fizer sentido
    # (ex: "12,5" -> "12.5")
    x = x.str.replace(".", "", regex=False).where(~x.str.contains(",", na=False), x)
    x = x.str.replace(",", ".", regex=False)

    # converte
    return pd.to_numeric(x, errors="coerce")


def coerce_int(s: pd.Series) -> pd.Series:
    x = coerce_numeric(s)
    return x.round(0)


def parse_date_key_yyyymmdd(s: pd.Series) -> pd.Series:
    """
    Converte chaves tipo 20240131 (YYYYMMDD) em datetime.
    Funciona com:
    - int
    - float "20240131.0"
    - string "20240131"
    """
    if s is None:
        return pd.Series([pd.NaT] * 0)

    key = coerce_int(s)
    key = key.dropna().astype(int).astype(str)

    # recria série alinhada
    out = pd.Series(pd.NaT, index=s.index, dtype="datetime64[ns]")
    parsed = pd.to_datetime(key, format="%Y%m%d", errors="coerce")
    out.loc[key.index] = parsed
    return out


def safe_value_counts(df: pd.DataFrame, col: str, top: int = 15, dropna: bool = True) -> pd.DataFrame:
    if col is None or col not in df.columns:
        return pd.DataFrame(columns=[col or "col", "qtd"])
    vc = df[col].dropna() if dropna else df[col]
    tab = (
        vc.astype(str)
        .str.strip()
        .replace({"": np.nan, "nan": np.nan, "None": np.nan})
        .dropna()
        .value_counts()
        .head(top)
        .rename_axis(col)
        .reset_index(name="qtd")
    )
    return tab


def safe_mean_pct(df: pd.DataFrame, col: str) -> float:
    if col is None or col not in df.columns or len(df) == 0:
        return 0.0
    x = coerce_numeric(df[col])
    return float(x.mean(skipna=True) * 100)


def safe_median(df: pd.DataFrame, col: str) -> float | None:
    if col is None or col not in df.columns or len(df) == 0:
        return None
    x = coerce_numeric(df[col])
    if x.dropna().empty:
        return None
    return float(x.median(skipna=True))


def unique_sorted_int_list(df: pd.DataFrame, col: str) -> list[int]:
    if col is None or col not in df.columns:
        return []
    x = coerce_int(df[col]).dropna().astype(int)
    return sorted(x.unique().tolist())


def unique_sorted_str_list(df: pd.DataFrame, col: str) -> list[str]:
    if col is None or col not in df.columns:
        return []
    x = (
        df[col]
        .astype(str)
        .str.strip()
        .replace({"": np.nan, "nan": np.nan, "None": np.nan})
        .dropna()
        .unique()
        .tolist()
    )
    return sorted(x)


def add_risk_score(
    df: pd.DataFrame,
    tempo_tramit_col: str = "tempo_tramitacao_dias",
    tempo_aberto_col: str = "tempo_em_aberto_dias",
    fase_col: str | None = None,
    ato_col: str | None = None,
    cat_ato_col: str | None = None,
    end_div_col: str | None = None,
    vagas_div_col: str | None = None,
    sede_ead_col: str | None = None,
) -> pd.DataFrame:
    """
    Cria:
    - risco_score (0..100)
    - risco_faixa (Baixo/Médio/Alto)

    Heurística prática (ajustável):
    + tempo (tramitação e/ou aberto)
    + divergências (endereço/vagas)
    + criticidade por ato/categoria (credenciamento/autorização)
    + fase sensível (gabinete, portaria etc)
    """
    out = df.copy()

    score = pd.Series(0.0, index=out.index)

    # 1) tempo de tramitação (proxy)
    if tempo_tramit_col in out.columns:
        ttr = coerce_numeric(out[tempo_tramit_col])
        score += np.select(
            [
                ttr.isna(),
                ttr < 365,
                (ttr >= 365) & (ttr < 730),
                ttr >= 730,
            ],
            [0, 10, 25, 40],
            default=0,
        )

    # 2) tempo em aberto (se existir)
    if tempo_aberto_col in out.columns:
        tea = coerce_numeric(out[tempo_aberto_col])
        score += np.select(
            [
                tea.isna(),
                tea < 365,
                (tea >= 365) & (tea < 730),
                tea >= 730,
            ],
            [0, 10, 25, 40],
            default=0,
        )

    # 3) divergências
    def _flag(colname: str | None, add_if_true: int):
        nonlocal score
        if colname and colname in out.columns:
            f = coerce_int(out[colname]).fillna(0).astype(int)
            score += np.where(f == 1, add_if_true, 0)

    _flag(end_div_col, 12)
    _flag(vagas_div_col, 12)
    _flag(sede_ead_col, 6)

    # 4) criticidade por ato/categoria
    crit_words = ["CREDENCI", "AUTORIZ", "RECONHEC", "PORTARIA", "GABINETE", "MINISTRO"]
    def _text_col(colname: str | None) -> pd.Series:
        if colname and colname in out.columns:
            return out[colname].astype(str).str.upper()
        return pd.Series([""] * len(out), index=out.index)

    ato_txt = _text_col(ato_col)
    cat_txt = _text_col(cat_ato_col)
    fase_txt = _text_col(fase_col)

    crit = ato_txt
    crit = crit + " " + cat_txt + " " + fase_txt

    score += np.where(crit.str.contains("CREDENCI", na=False), 10, 0)
    score += np.where(crit.str.contains("AUTORIZ", na=False), 10, 0)
    score += np.where(crit.str.contains("PORTARIA", na=False), 8, 0)
    score += np.where(crit.str.contains("GABINETE", na=False), 8, 0)
    score += np.where(crit.str.contains("MINISTRO", na=False), 6, 0)

    # cap 0..100
    score = score.clip(0, 100)

    out["risco_score"] = score

    out["risco_faixa"] = pd.cut(
        out["risco_score"],
        bins=[-0.1, 33, 66, 100],
        labels=["Baixo", "Médio", "Alto"],
    ).astype(str)

    return out
