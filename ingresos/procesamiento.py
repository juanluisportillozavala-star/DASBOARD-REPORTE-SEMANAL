"""
=========================================================
PROCESAMIENTO DEL MÓDULO INGRESOS
=========================================================
Toma la BD cruda (tal como se sube) y agrega 4 columnas
calculadas, replicando las fórmulas del Excel:

  ESTATUS          Vigente si fin-de-mes(Fecha vencimiento) >=
                   fin-de-mes(fecha_corte); si no, Vencido.
                   fecha_corte = DÍA DE LA CARGA (se congela;
                   no cambia hasta la próxima carga).
  TERMINOS DE PAGO Contado si la descripción es "pago inmediato";
                   si no, Crédito.
  MES              mes de la Fecha último pago.
  SEMANA           semana ISO de la Fecha último pago.
"""

import base64
import io
import pandas as pd


# Nombres de columna de la BD cruda (tal como llegan del Excel)
COL_VENCIMIENTO = "Fecha de vencimiento"
COL_DESCRIPCION = "Términos de pago/Descripción de la factura"
COL_ULTIMO_PAGO = "Fecha último pago"
COL_IMPORTE = "Importe sin impuestos firmado"
COL_VENDEDOR = "Vendedor"

TEXTO_CONTADO = "<p>Términos de pago: pago inmediato</p>"


def leer_excel(contents):
    """Convierte el contents de un dcc.Upload (base64) a DataFrame."""
    if contents is None:
        return None
    contenido = contents.split(",")[1]
    archivo = base64.b64decode(contenido)
    return pd.read_excel(io.BytesIO(archivo))


def _fin_de_mes(fecha):
    """Último día del mes (equivalente a EOMONTH(x, 0))."""
    return fecha + pd.offsets.MonthEnd(0)


def procesar_bd_ingresos(df, fecha_corte=None):
    """
    df: BD cruda de ingresos.

    NOTA: ESTATUS (Vigente/Vencido) YA NO se calcula aquí. Se
    calcula dinámicamente en la tabla según el mes de corte del
    calendario (el mes más alto seleccionado). Aquí solo se
    preparan las columnas que NO dependen del filtro: TERMINOS,
    MES, SEMANA, y se conserva la Fecha de vencimiento (que la
    tabla usa para el cálculo dinámico del estatus).

    fecha_corte: se mantiene el parámetro por compatibilidad,
    pero ya no se usa para ESTATUS.
    """
    df = df.copy()

    df[COL_VENCIMIENTO] = pd.to_datetime(df[COL_VENCIMIENTO], errors="coerce")
    df[COL_ULTIMO_PAGO] = pd.to_datetime(df[COL_ULTIMO_PAGO], errors="coerce")

    # MES_VENCIMIENTO: mes de la fecha de vencimiento. Lo usa la tabla
    # para calcular ESTATUS dinámicamente (vigente/vencido según el
    # mes de corte del calendario). ESTATUS ya NO se congela aquí.
    df["MES_VENCIMIENTO"] = df[COL_VENCIMIENTO].dt.month

    # TERMINOS DE PAGO
    df["TERMINOS DE PAGO"] = df[COL_DESCRIPCION].apply(
        lambda x: "Contado" if str(x) == TEXTO_CONTADO else "Crédito"
    )

    # MES y SEMANA (de la Fecha último pago)
    df["MES"] = df[COL_ULTIMO_PAGO].dt.month
    df["SEMANA"] = df[COL_ULTIMO_PAGO].dt.isocalendar().week.astype("Int64")

    return df


def leer_archivo(contents, fecha_corte=None):
    """Lee el Excel subido y lo procesa. Devuelve el DataFrame
    con las 4 columnas calculadas."""
    df = leer_excel(contents)
    if df is None or df.empty:
        raise Exception("La BD de Ingresos está vacía o no se pudo leer.")
    return procesar_bd_ingresos(df, fecha_corte=fecha_corte)