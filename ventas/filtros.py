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

    """
    Devuelve todas las semanas correspondientes
    a los meses seleccionados.
    """

    if df is None or len(df) == 0:

        return []

    if meses is None:

        return []

    if not isinstance(meses, list):

        meses = [meses]

    df = df[df["Mes"].isin(meses)]

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