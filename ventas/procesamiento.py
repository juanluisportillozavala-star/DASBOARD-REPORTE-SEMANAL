"""
=========================================================
PROCESAMIENTO DEL MÓDULO DE VENTAS
=========================================================
"""

import base64
import io

import pandas as pd


# =========================================================
# LEER EXCEL
# =========================================================

def leer_excel(contents):

    """
    Convierte el archivo recibido desde dcc.Upload
    en un DataFrame de pandas.
    """

    if contents is None:
        return None

    contenido = contents.split(",")[1]

    archivo = base64.b64decode(contenido)

    return pd.read_excel(
        io.BytesIO(archivo)
    )


# =========================================================
# VALIDAR COLUMNAS
# =========================================================

def validar_archivo(df, nombre):

    if df is None:
        raise Exception(f"No fue posible leer {nombre}")

    if len(df.columns) == 0:
        raise Exception(f"{nombre} está vacío.")

    return True


# =========================================================
# LEER LOS DOS ARCHIVOS
# =========================================================

def leer_archivos(catalogo, ventas):

    df_catalogo = leer_excel(catalogo)

    df_ventas = leer_excel(ventas)

    validar_archivo(
        df_catalogo,
        "Catálogo"
    )

    validar_archivo(
        df_ventas,
        "BD Ventas"
    )

    return df_catalogo, df_ventas


# =========================================================
# INFORMACIÓN GENERAL
# =========================================================

def resumen(df_catalogo, df_ventas):

    return {

        "productos": len(df_catalogo),

        "ventas": len(df_ventas),

        "columnas_catalogo": len(df_catalogo.columns),

        "columnas_ventas": len(df_ventas.columns)

    }