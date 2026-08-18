"""
=========================================================
PROCESAMIENTO DEL MÓDULO CARTERA
=========================================================
Toma la BD cruda (hoja DESCARGA) y agrega las columnas de
aging de cartera, replicando las fórmulas del Excel (hoja
EDITADA, columnas N a Y).

CLAVE: la columna N ("FECHA") es una fecha de REFERENCIA que
se PIDE al cargar el archivo (no se deduce de los datos). Todo
el cálculo de vigente/vencido/por-vencer y la antigüedad se
basa en esa fecha.

Fórmulas replicadas:
  O Importe pendiente = IF(Impuesto>0, TotalPendiente/1.16, TotalPendiente)
  P Estatus = IF(Venc<=FECHA,"Vencido",
                 IF(FECHA-Venc>=-7,"Por vencer","Vigente"))
  Q Mes    = MONTH(FECHA)
  R Semana = WEEKNUM(FECHA)
  S Dias vencido = IF(Vencido, FECHA-Venc+1, 0)
  T..W rangos de vencido por días (0-30,31-60,61-90,>90)
  X Por vencer = importe si Estatus="Por vencer"
  Y Vigente   = importe si Estatus="Vigente"
"""

import base64
import io
from datetime import date
import pandas as pd
import numpy as np

COL_FACTURA = "Fecha de factura"
COL_NUMERO = "Número"
COL_CONTACTO = "Contacto"
COL_IMPORTE = "Importe sin impuestos firmado"
COL_IMPUESTO = "Impuesto firmado"
COL_TOTAL = "Total firmado"
COL_TOTAL_PENDIENTE = "Importe pendiente firmado"
COL_VENCIMIENTO = "Fecha de vencimiento"
COL_ULTIMO_PAGO = "Fecha último pago"
COL_VENDEDOR = "Vendedor"
COL_DESC = "Términos de pago/Descripción de la factura"

TEXTO_CONTADO = "<p>Términos de pago: pago inmediato</p>"

# nombres de las columnas de aging (para la tabla)
RANGOS = ["Vencido >90 días", "Vencido 61-90 días", "Vencido 31-60 días",
          "Vencido 0-30 días", "Por vencer", "Vigente"]


def _weeknum_excel(d):
    """WEEKNUM(fecha) como Excel (sistema 1, el de por defecto):
    la semana 1 es la que CONTIENE el 1 de enero y las semanas
    empiezan en DOMINGO.

    OJO: NO es lo mismo que isocalendar().week de Python (ese
    empieza en lunes y numera distinto), por eso la semana salía
    diferente a la tabla dinámica. Validado contra la BD Cartera
    real: coincide 100% con =WEEKNUM del Excel.
    """
    if isinstance(d, pd.Timestamp):
        d = d.date()
    jan1 = date(d.year, 1, 1)
    dias = (d - jan1).days
    # weekday(): lunes=0 .. domingo=6  ->  domingo=0 .. sábado=6
    dow_jan1 = (jan1.weekday() + 1) % 7
    return (dias + dow_jan1) // 7 + 1


def leer_excel(contents, sheet_name="DESCARGA"):
    if contents is None:
        return None
    contenido = contents.split(",")[1]
    archivo = base64.b64decode(contenido)
    # intenta la hoja DESCARGA; si no existe, la primera
    xls = pd.ExcelFile(io.BytesIO(archivo))
    hoja = sheet_name if sheet_name in xls.sheet_names else xls.sheet_names[0]
    return pd.read_excel(xls, sheet_name=hoja)


def procesar_bd_cartera(df, fecha_referencia):
    """
    df: BD cruda de cartera (hoja DESCARGA).
    fecha_referencia: la FECHA que se pide al cargar (columna N).
                      Base de todo el cálculo de aging.
    """
    if fecha_referencia is None:
        raise ValueError("Cartera requiere una fecha de referencia.")

    df = df.copy()
    df.columns = [str(c).strip() for c in df.columns]
    FECHA = pd.Timestamp(fecha_referencia).normalize()

    # localizar la columna de total pendiente (el nombre varía un poco)
    col_pend = COL_TOTAL_PENDIENTE
    if col_pend not in df.columns:
        cand = [c for c in df.columns if "pendiente" in c.lower() and "firmado" in c.lower()]
        if cand:
            col_pend = cand[0]

    df[COL_VENCIMIENTO] = pd.to_datetime(df[COL_VENCIMIENTO], errors="coerce")

    # N: FECHA (constante de referencia)
    df["FECHA"] = FECHA

    # O: Importe pendiente = IF(Impuesto>0, Pendiente/1.16, Pendiente)
    df["Importe pendiente"] = np.where(
        df[COL_IMPUESTO] > 0, df[col_pend] / 1.16, df[col_pend]
    )

    # P: Estatus
    def _estatus(h):
        if pd.isna(h):
            return None
        if h <= FECHA:
            return "Vencido"
        if (FECHA - h).days >= -7:
            return "Por vencer"
        return "Vigente"
    df["Estatus"] = df[COL_VENCIMIENTO].apply(_estatus)

    # Q, R: Mes y Semana de la FECHA de referencia (iguales para todas).
    # Semana = WEEKNUM(FECHA) estilo Excel (NO isocalendar), para que
    # coincida con la tabla dinámica.
    df["Mes"] = FECHA.month
    df["Semana"] = _weeknum_excel(FECHA)

    # S: Dias vencido
    df["Dias vencido"] = np.where(
        df["Estatus"] == "Vencido",
        (FECHA - df[COL_VENCIMIENTO]).dt.days + 1,
        0,
    )

    # T..W: rangos de vencido
    O = df["Importe pendiente"]
    S = df["Dias vencido"]
    df["Vencido 0-30 días"] = np.where((S > 0) & (S < 31), O, 0)
    df["Vencido 31-60 días"] = np.where((S > 30) & (S < 61), O, 0)
    df["Vencido 61-90 días"] = np.where((S > 60) & (S < 91), O, 0)
    df["Vencido >90 días"] = np.where(S > 90, O, 0)

    # X, Y
    df["Por vencer"] = np.where(df["Estatus"] == "Por vencer", O, 0)
    df["Vigente"] = np.where(df["Estatus"] == "Vigente", O, 0)

    # TERMINOS DE PAGO (Contado/Crédito), por si se filtra
    df["TERMINOS DE PAGO"] = np.where(
        df[COL_DESC].astype(str) == TEXTO_CONTADO, "Contado", "Crédito"
    )

    return df


def leer_archivo(contents, fecha_referencia=None):
    df = leer_excel(contents)
    if df is None or df.empty:
        raise Exception("La BD de Cartera está vacía o no se pudo leer.")
    return procesar_bd_cartera(df, fecha_referencia)