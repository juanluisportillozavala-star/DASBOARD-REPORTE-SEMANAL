"""
=========================================================
FILTROS DEL DASHBOARD
=========================================================
El AÑO es el filtro maestro: se aplica primero y mes/semana
operan dentro del año seleccionado.
"""

import pandas as pd


# =========================================================
# FILTRAR POR AÑO
# =========================================================

def filtrar_anio(df, anio):

    if df is None:
        return df

    if anio is None:
        return df

    if "Año" not in df.columns:
        return df

    return df[df["Año"] == int(anio)]


# =========================================================
# SEMANAS DISPONIBLES
# =========================================================

def obtener_semanas(df, meses, anio=None):

    if df is None or len(df) == 0:
        return []

    if not meses:
        return []

    df = df.copy()

    # respetar el año seleccionado
    df = filtrar_anio(df, anio)

    df = df[df["Mes"].isin(meses)]

    return sorted(

        df["Semana"]

        .dropna()

        .astype(int)

        .unique()

        .tolist()

    )


# =========================================================
# MESES DISPONIBLES (de un año)
# =========================================================

def obtener_meses(df, anio=None):

    if df is None or len(df) == 0:
        return []

    df = filtrar_anio(df, anio)

    return sorted(

        df["Mes"].dropna().astype(int).unique().tolist()

    )


# =========================================================
# AÑOS DISPONIBLES
# =========================================================

def obtener_anios(df):

    if df is None or len(df) == 0 or "Año" not in df.columns:
        return []

    return sorted(

        df["Año"].dropna().astype(int).unique().tolist(),

        reverse=True,   # más reciente primero

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

def filtrar_dataframe(df, meses=None, semanas=None, anio=None):

    """
    Aplica todos los filtros disponibles.
    El AÑO se aplica primero (filtro maestro).
    """

    if df is None:
        return df

    df = filtrar_anio(df, anio)

    df = filtrar_mes(df, meses)

    df = filtrar_semana(df, semanas)

    return df