"""
=========================================================
PROCESAMIENTO DEL MÓDULO INVENTARIO
=========================================================
Toma la BD cruda de inventario y:
  - limpia filas sin Producto y los subtotales "Existencias"
  - calcula DIAS EN ALMACEN = (fecha_corte - Fecha de entrada)
    NOTA: fecha_corte = DÍA DE LA CARGA (se congela; no cambia
    hasta la próxima carga), igual criterio que Ingresos.
  - clasifica CATEGORIA: 1-30 / 31-60 / 61+ días
"""

import base64
import io
import pandas as pd

COL_PRODUCTO = "Producto"
COL_UBICACION = "Ubicación"
COL_UNIDAD = "Unidad de medida"
COL_CANTIDAD = "Cantidad en inventario"
COL_FECHA_ENTRADA = "Fecha de entrada"
COL_VALOR = "Valor"

CAT_1 = "1-30 días"
CAT_2 = "31-60 días"
CAT_3 = "61+ días"


def leer_excel(contents):
    if contents is None:
        return None
    contenido = contents.split(",")[1]
    archivo = base64.b64decode(contenido)
    return pd.read_excel(io.BytesIO(archivo))


def procesar_bd_inventario(df, fecha_corte=None):
    """
    df: BD cruda de inventario.
    fecha_corte: día con el que se congelan los DIAS EN ALMACEN.
                 Por defecto hoy; en la carga = día de la carga.
    """
    df = df.copy()
    df.columns = df.columns.str.strip()

    if fecha_corte is None:
        fecha_corte = pd.Timestamp.today().normalize()
    else:
        fecha_corte = pd.Timestamp(fecha_corte).normalize()

    # limpieza: sin producto y sin subtotales "Existencias"
    df = df.dropna(subset=[COL_PRODUCTO])
    df = df[~df[COL_PRODUCTO].str.contains("Existencias", case=False, na=False)]

    # días en almacén (congelados a la fecha de corte)
    df[COL_FECHA_ENTRADA] = pd.to_datetime(df[COL_FECHA_ENTRADA], errors="coerce")
    df["DIAS EN ALMACEN"] = (fecha_corte - df[COL_FECHA_ENTRADA]).dt.days

    # categoría por antigüedad
    df["CATEGORIA"] = pd.cut(
        df["DIAS EN ALMACEN"],
        bins=[0, 30, 60, 999999],
        labels=[CAT_1, CAT_2, CAT_3],
    ).astype(str)  # texto plano (JSON no admite Categorical)

    return df.reset_index(drop=True)


def leer_archivo(contents, fecha_corte=None):
    df = leer_excel(contents)
    if df is None or df.empty:
        raise Exception("La BD de Inventario está vacía o no se pudo leer.")
    return procesar_bd_inventario(df, fecha_corte=fecha_corte)