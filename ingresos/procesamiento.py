"""
=========================================================
PROCESAMIENTO DEL MÓDULO INGRESOS  (BD Cobranza)
=========================================================
Ahora la BD que se sube es la hoja "BD Cobranza" del reporte,
YA FORMULADA. Este procesamiento la lee tal cual y deja un
DataFrame limpio con las columnas que necesita la matriz.

Columnas de la BD Cobranza (los nombres pueden traer espacios):
  Fecha de factura | Número | Cliente | Importe | IVA | Total |
  Fecha de vencimiento | Estado de pago | Fecha último pago |
  Vendedor | Términos de pago | Estatus | Mes | Semana

Se toma:
  • Importe  -> valor que suma la matriz (SIN IVA, columna D).
  • Vendedor -> filas nivel 1.
  • Cliente  -> filas nivel 2.
  • Términos de pago (Contado / Crédito)  -> tal cual.
  • Estatus (Vigente / Vencido)           -> tal cual (de la BD).

Se RECALCULAN (por seguridad, por si las fórmulas no vinieran
recalculadas):
  • MES    = MONTH(Fecha último pago)
  • SEMANA = WEEKNUM(Fecha último pago)  (estilo Excel, no ISO)
  • AÑO    = YEAR(Fecha último pago)

Nombres de salida (los que usan arbol_ingresos / tabla):
  IMPORTE, Vendedor, Cliente, TERMINOS DE PAGO, ESTATUS,
  MES, SEMANA, AÑO
"""

import base64
import io
from datetime import date
import pandas as pd


def _buscar_col(df, *candidatos):
    """Devuelve el nombre real de la primera columna que coincida
    (ignorando espacios y mayúsculas). None si no está."""
    norm = {str(c).strip().lower(): c for c in df.columns}
    for cand in candidatos:
        k = cand.strip().lower()
        if k in norm:
            return norm[k]
    return None


def _weeknum_excel(d):
    """WEEKNUM(fecha) como Excel (sistema 1): la semana 1 es la que
    contiene el 1 de enero y las semanas empiezan en DOMINGO.
    (No es isocalendar de Python.)"""
    if pd.isna(d):
        return None
    if isinstance(d, pd.Timestamp):
        d = d.date()
    jan1 = date(d.year, 1, 1)
    dias = (d - jan1).days
    dow_jan1 = (jan1.weekday() + 1) % 7
    return (dias + dow_jan1) // 7 + 1


def leer_excel(contents):
    """Convierte el contents de un dcc.Upload (base64) a DataFrame.
    Intenta la hoja 'BD Cobranza'; si no está, usa la primera."""
    if contents is None:
        return None
    contenido = contents.split(",")[1]
    archivo = base64.b64decode(contenido)
    xls = pd.ExcelFile(io.BytesIO(archivo))
    hoja = "BD Cobranza" if "BD Cobranza" in xls.sheet_names else xls.sheet_names[0]
    return pd.read_excel(xls, sheet_name=hoja)


def procesar_bd_ingresos(df, fecha_corte=None):
    """Limpia la BD Cobranza y deja las columnas que usa la matriz.
    fecha_corte se ignora (se deja por compatibilidad de firma)."""
    df = df.copy()
    df.columns = [str(c).strip() for c in df.columns]

    c_importe = _buscar_col(df, "Importe", "Importe ")
    c_vendedor = _buscar_col(df, "Vendedor")
    c_cliente = _buscar_col(df, "Cliente")
    c_terminos = _buscar_col(df, "Términos de pago", "Terminos de pago")
    c_estatus = _buscar_col(df, "Estatus")
    c_pago = _buscar_col(df, "Fecha último pago", "Fecha ultimo pago")

    faltan = [n for n, c in [("Importe", c_importe), ("Vendedor", c_vendedor),
                             ("Cliente", c_cliente), ("Términos de pago", c_terminos),
                             ("Estatus", c_estatus), ("Fecha último pago", c_pago)]
              if c is None]
    if faltan:
        raise Exception("A la BD Cobranza le faltan columnas: " + ", ".join(faltan))

    # quedarnos solo con filas reales (con vendedor)
    df = df[df[c_vendedor].notna()].copy()

    out = pd.DataFrame()
    out["Vendedor"] = df[c_vendedor].astype(str).str.strip()
    out["Cliente"] = df[c_cliente].astype(str).str.strip()
    out["IMPORTE"] = pd.to_numeric(df[c_importe], errors="coerce").fillna(0.0)
    out["TERMINOS DE PAGO"] = df[c_terminos].astype(str).str.strip()
    out["ESTATUS"] = df[c_estatus].astype(str).str.strip()

    # periodo recalculado desde la Fecha último pago
    pago = pd.to_datetime(df[c_pago], errors="coerce")
    out["MES"] = pago.dt.month.astype("Int64")
    out["AÑO"] = pago.dt.year.astype("Int64")
    out["SEMANA"] = pago.apply(_weeknum_excel).astype("Int64")

    return out.reset_index(drop=True)


def leer_archivo(contents, fecha_corte=None):
    df = leer_excel(contents)
    if df is None or df.empty:
        raise Exception("La BD de Ingresos (Cobranza) está vacía o no se pudo leer.")
    return procesar_bd_ingresos(df, fecha_corte=fecha_corte)