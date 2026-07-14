"""
=========================================================
PROCESAMIENTO DE VENTAS
=========================================================
"""

import base64
import io

import pandas as pd


def leer_excel(contents):

    """
    Convierte el contenido recibido por dcc.Upload
    en un DataFrame de pandas.
    """

    if contents is None:
        return None

    contenido = contents.split(",")[1]

    archivo = base64.b64decode(contenido)

    return pd.read_excel(
        io.BytesIO(archivo)
    )


def leer_archivos(catalogo, ventas):

    df_catalogo = leer_excel(catalogo)
    df_ventas = leer_excel(ventas)

    return df_catalogo, df_ventas