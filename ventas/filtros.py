"""
=========================================================
FILTROS DEL DASHBOARD
=========================================================
"""

import pandas as pd


# =========================================================
# SEMANAS DISPONIBLES
# =========================================================

def obtener_semanas(df, meses):
    
    if df is None or len(df) == 0:

        return []

    if not meses:

        return []

    df = df.copy()

    df = df[df["Mes"].isin(meses)]

    return sorted(

        df["Semana"]

        .dropna()

        .astype(int)

        .unique()

        .tolist()

    )


# =========================================================
# FILTRAR POR MESES
# =========================================================

def filtrar_mes(df, meses):

    if df is None:

        return df

    if meses is None:

        return df

    if len(meses) == 0:

        return df

    return df[df["Mes"].isin(meses)]


# =========================================================
# FILTRAR POR SEMANAS
# =========================================================

def filtrar_semana(df, semanas):

    if df is None:

        return df

    if semanas is None:

        return df

    if len(semanas) == 0:

        return df

    return df[df["Semana"].isin(semanas)]


# =========================================================
# FILTRO GENERAL
# =========================================================

def filtrar_dataframe(df, meses=None, semanas=None):

    """
    Aplica todos los filtros disponibles.
    """

    if df is None:

        return df

    df = filtrar_mes(df, meses)

    df = filtrar_semana(df, semanas)

    return df