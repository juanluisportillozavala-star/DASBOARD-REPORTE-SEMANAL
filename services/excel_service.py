"""
=========================================================
SERVICIO DE EXCEL
=========================================================
"""

import pandas as pd


def leer_excel(archivo, hoja=None):

    return pd.read_excel(

        archivo,

        sheet_name=hoja

    )


def guardar_excel(df, ruta):

    df.to_excel(

        ruta,

        index=False

    )