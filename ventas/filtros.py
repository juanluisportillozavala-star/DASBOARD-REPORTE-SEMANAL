"""
=========================================================
FILTROS DEL DASHBOARD
=========================================================
"""

import pandas as pd


# =========================================================
# SEMANAS DISPONIBLES
# =========================================================

def obtener_semanas(df, mes):

    if df is None or len(df) == 0:

        return []

    df = df.copy()

    df = df[df["Mes"] == mes]

    semanas = (

        df["Semana"]

        .dropna()

        .astype(int)

        .sort_values()

        .unique()

        .tolist()

    )

    return semanas


# =========================================================
# FILTRAR POR MES
# =========================================================

def filtrar_mes(df, mes):

    if df is None:

        return df

    return df[df["Mes"] == mes]


# =========================================================
# FILTRAR POR SEMANA
# =========================================================

def filtrar_semana(df, semana):

    if df is None:

        return df

    return df[df["Semana"] == semana]