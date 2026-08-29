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

    if contents is None:
        return None

    contenido = contents.split(",")[1]

    archivo = base64.b64decode(contenido)

    return pd.read_excel(io.BytesIO(archivo))


# =========================================================
# VALIDAR
# =========================================================

def validar_archivo(df, nombre):

    if df is None:
        raise Exception(f"No fue posible leer {nombre}")

    if df.empty:
        raise Exception(f"{nombre} está vacío.")

    return True


# =========================================================
# LEER AMBOS ARCHIVOS
# =========================================================

def leer_archivos(catalogo, ventas):

    df_catalogo = leer_excel(catalogo)

    df_ventas = leer_excel(ventas)

    validar_archivo(df_catalogo, "Catálogo")
    validar_archivo(df_ventas, "BD Ventas")

    return df_catalogo, procesar_bd_ventas(df_catalogo, df_ventas)


# =========================================================
# COLUMNAS QUE EL SISTEMA CALCULA
# =========================================================
# Si la BD que se sube YA trae estas columnas (por ejemplo,
# alguien subió el archivo con las fórmulas de la derecha ya
# puestas), se ELIMINAN al inicio para regenerarlas desde
# cero. Así el archivo puede subirse con o sin fórmulas: las
# columnas extra formuladas simplemente se ignoran y no
# rompen el merge del catálogo (antes chocaban y creaban
# 'Producto 2_x' / 'Producto 2_y').

COLUMNAS_CALCULADAS = [
    "Mes", "Semana", "Año", "Producto 2",
    "TC", "Ut Bruta MN", "Costo Venta MN",
]


# =========================================================
# PROCESAMIENTO
# =========================================================

def procesar_bd_ventas(df_catalogo, df):

    df = df.copy()

    # limpiar espacios en los nombres de columna
    df.columns = [str(c).strip() for c in df.columns]

    # -----------------------------------------------------
    # QUITAR columnas calculadas que ya vengan en el archivo
    # (permite subir la BD con o sin fórmulas)
    # -----------------------------------------------------

    a_quitar = [c for c in COLUMNAS_CALCULADAS if c in df.columns]
    if a_quitar:
        df = df.drop(columns=a_quitar)

    # también quitar columnas basura sin nombre (Unnamed) que
    # a veces se cuelan al final de un Excel formuleado
    basura = [c for c in df.columns if str(c).startswith("Unnamed")]
    if basura:
        df = df.drop(columns=basura)

    # -----------------------------------------------------
    # FECHA
    # -----------------------------------------------------

    fecha = "Asiento contable/Fecha de factura"

    df[fecha] = pd.to_datetime(
        df[fecha],
        errors="coerce"
    )

    # -----------------------------------------------------
    # MES
    # (Columna P)
    # -----------------------------------------------------

    df["Mes"] = df[fecha].dt.month

    # -----------------------------------------------------
    # AÑO
    # (para el segmentador de año)
    # -----------------------------------------------------

    df["Año"] = df[fecha].dt.year

    # -----------------------------------------------------
    # SEMANA
    # (Columna Q)
    # -----------------------------------------------------

    try:

        df["Semana"] = (
            df[fecha]
            .dt.isocalendar()
            .week
            .astype(int)
        )

    except Exception:

        df["Semana"] = df[fecha].dt.strftime("%U").astype(int)

    # -----------------------------------------------------
    # PRODUCTO 2
    # (Columna R)
    # -----------------------------------------------------

    codigo = "Líneas de la orden de venta/Producto"

    catalogo = df_catalogo.copy()

    catalogo.columns = catalogo.columns.str.strip()

    llave = catalogo.columns[0]

    descripcion = catalogo.columns[1]

    catalogo = catalogo.rename(

        columns={

            llave: codigo,

            descripcion: "Producto 2"

        }

    )

    # quedarnos solo con las 2 columnas del catálogo que usamos,
    # para que el merge no arrastre columnas extra del catálogo
    catalogo = catalogo[[codigo, "Producto 2"]]

    df = df.merge(

        catalogo,

        how="left",

        on=codigo

    )

    # -----------------------------------------------------
    # TC
    # (Columna U)
    # -----------------------------------------------------

    moneda = "Líneas de la orden de venta/Divisa"

    credito = "Crédito"

    cantidad = "Líneas de la orden de venta/Cantidad facturada"

    precio = "Líneas de la orden de venta/Precio unitario"

    df["TC"] = 1.0

    usd = df[moneda].astype(str).str.upper() == "USD"

    df.loc[usd, "TC"] = (

        df.loc[usd, credito]

        /

        df.loc[usd, cantidad]

        /

        df.loc[usd, precio]

    )

    # -----------------------------------------------------
    # UTILIDAD BRUTA MN
    # (Columna S)
    # -----------------------------------------------------

    costo = "Líneas de la orden de venta/Costo"

    df["Ut Bruta MN"] = (

        (df[precio] - df[costo])

        *

        df[cantidad]

        *

        df["TC"]

    )

    # -----------------------------------------------------
    # COSTO VENTA MN
    # (Columna T)
    # -----------------------------------------------------

    df["Costo Venta MN"] = (

        df[credito]

        -

        df["Ut Bruta MN"]

    )

    return df


# =========================================================
# RESUMEN
# =========================================================

def resumen(df_catalogo, df_ventas):

    return {

        "productos": len(df_catalogo),

        "ventas": len(df_ventas),

        "columnas_catalogo": len(df_catalogo.columns),

        "columnas_ventas": len(df_ventas.columns)

    }