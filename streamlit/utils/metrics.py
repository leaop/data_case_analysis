# streamlit/utils/metrics.py
from __future__ import annotations

from typing import Iterable, Optional, Sequence
import numpy as np
import pandas as pd


# -----------------------------
# Helpers de colunas
# -----------------------------
def resolve_col(df: pd.DataFrame, candidates: Sequence[str]) -> Optional[str]:
    """Retorna o primeiro nome de coluna existente no df, dado uma lista de candidatos."""
    for c in candidates:
        if c in df.columns:
            return c
    return None


# -----------------------------
# Conversões numéricas seguras
# -----------------------------
def to_numeric_series(s: pd.Series) -> pd.Series:
    """Converte série para numérico (float) de forma robusta."""
    # normaliza strings tipo "135,0" -> "135.0"
    if s.dtype == "object":
        s = s.astype(str).str.replace(",", ".", regex=False)
        # valores vazios / texto "nan"
        s = s.replace({"": np.nan, "nan": np.nan, "None": np.nan, "NONE": np.nan})
    return pd.to_numeric(s, errors="coerce")


def safe_median(df: pd.DataFrame, col: str) -> Optional[float]:
    if col not in df.columns:
        return None
    v = to_numeric_series(df[col]).dropna()
    return float(v.median()) if len(v) else None


def safe_mean_pct(df: pd.DataFrame, col: str) -> float:
    """Média * 100, assumindo coluna 0/1 (ou booleana)."""
    if col not in df.columns or len(df) == 0:
        return 0.0
    v = to_numeric_series(df[col]).dropna()
    return float(v.mean() * 100) if len(v) else 0.0


# -----------------------------
# Listas para filtros
# -----------------------------
def unique_sorted_int_list(df: pd.DataFrame, col: str) -> list[int]:
    """Extrai valores únicos (inteiros) ordenados para filtros."""
    if col not in df.columns:
        return []
    v = to_numeric_series(df[col]).dropna()
    if len(v) == 0:
        return []
    return sorted(v.astype(int).unique().tolist())


def unique_sorted_str_list(df: pd.DataFrame, col: str) -> list[str]:
    if col not in df.columns:
        return []
    v = (
        df[col]
        .astype(str)
        .str.strip()
        .replace({"": np.nan, "nan": np.nan, "None": np.nan})
        .dropna()
        .unique()
        .tolist()
    )
    return sorted(v)


# -----------------------------
# Filtros
# -----------------------------
def apply_filters(
    df: pd.DataFrame,
    col_ano: Optional[str],
    col_uf: Optional[str],
    col_mod: Optional[str],
    col_pp: Optional[str],
    ano_sel: Iterable[int],
    uf_sel: Iterable[str],
    mod_sel: Iterable[str],
    pp_sel: Iterable[str],
) -> pd.DataFrame:
    out = df.copy()

    if col_ano and ano_sel:
        ano_num = to_numeric_series(out[col_ano]).astype("Int64")
        out = out[ano_num.isin(list(ano_sel))]

    if col_uf and uf_sel:
        out = out[out[col_uf].isin(list(uf_sel))]

    if col_mod and mod_sel:
        out = out[out[col_mod].isin(list(mod_sel))]

    if col_pp and pp_sel:
        out = out[out[col_pp].isin(list(pp_sel))]

    return out
