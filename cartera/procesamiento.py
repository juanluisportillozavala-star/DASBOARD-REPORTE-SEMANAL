"""
=========================================================
PROCESAMIENTO DEL MÓDULO CARTERA  (BD Cartera formulada)
=========================================================
Ahora la BD que se sube es la hoja "BD Cartera" del reporte,
YA FORMULADA. Trae calculadas las columnas de aging, el
Estatus, Mes y Semana. Este procesamiento la lee tal cual y
deja un DataFrame limpio para la matriz.

YA NO se pide fecha de corte al cargar (la BD ya viene con su
columna Fecha y su aging calculado).

Columnas de la BD Cartera (los nombres pueden traer espacios):
  Fecha de factura | Número | Clientes | Importe | IVA | Total |
  Total pendiente | Fecha de vencimiento | Estado de pago |
  Vendedor | Fecha | Términos de pago | Importe pendiente |
  Estatus | Mes | Semana | Dias vencido |
  Vencido 0-30 días | Vencido 31-60 días | Vencido 61-90 días |
  Vencido >90 días | Por vencer | Vigente

Se toma:
  • Vendedor, Clientes (cliente), Términos de pago, Estatus.
  • Las 6 columnas de AGING ya calculadas (se suman tal cual).
Se RECALCULAN desde la columna Fecha (por seguridad):
  • MES = MONTH(Fecha), SEMANA = WEEKNUM(Fecha), AÑO = YEAR(Fecha)

Nombres de salida (los que usan arbol_cartera / tabla):
  Vendedor, Clientes, TERMINOS DE PAGO, Estatus,
  Vencido 0-30 días, Vencido 31-60 días, Vencido 61-90 días,
  Vencido >90 días, Por vencer, Vigente, MES, SEMANA, AÑO
"""

import base64
import io
from datetime import date
import pandas as pd

AGING = ["Vencido 0-30 días", "Vencido 31-60 días", "Vencido 61-90 días",
         "Vencido >90 días", "Por vencer", "Vigente"]


def _buscar_col(df, *candidatos):
    norm = {str(c).strip().lower(): c for c in df.columns}
    for cand in candidatos:
        k = cand.strip().lower()
        if k in norm:
            return norm[k]
    return None


def _weeknum_excel(d):
    """WEEKNUM(fecha) estilo Excel (sistema 1): semana 1 = la que
    contiene el 1 de enero; semanas empiezan en domingo."""
    if pd.isna(d):
        return None
    if isinstance(d, pd.Timestamp):
        d = d.date()
    jan1 = date(d.year, 1, 1)
    dias = (d - jan1).days
    dow_jan1 = (jan1.weekday() + 1) % 7
    return (dias + dow_jan1) // 7 + 1


def leer_excel(contents):
    if contents is None:
        return None
    contenido = contents.split(",")[1]
    archivo = base64.b64decode(contenido)
    xls = pd.ExcelFile(io.BytesIO(archivo))
    hoja = "BD Cartera" if "BD Cartera" in xls.sheet_names else xls.sheet_names[0]
    return pd.read_excel(xls, sheet_name=hoja)


def procesar_bd_cartera(df, fecha_referencia=None):
    """Limpia la BD Cartera formulada. fecha_referencia se ignora
    (se deja por compatibilidad de firma; la BD ya trae su Fecha)."""
    df = df.copy()
    df.columns = [str(c).strip() for c in df.columns]

    c_vendedor = _buscar_col(df, "Vendedor")
    c_cliente = _buscar_col(df, "Clientes", "Cliente")
    c_terminos = _buscar_col(df, "Términos de pago", "Terminos de pago")
    c_estatus = _buscar_col(df, "Estatus")
    c_fecha = _buscar_col(df, "Fecha")

    faltan = [n for n, c in [("Vendedor", c_vendedor), ("Clientes", c_cliente),
                             ("Términos de pago", c_terminos), ("Estatus", c_estatus),
                             ("Fecha", c_fecha)] if c is None]
    if faltan:
        raise Exception("A la BD Cartera le faltan columnas: " + ", ".join(faltan))

    # columnas de aging: deben existir (ya vienen calculadas)
    aging_cols = {a: _buscar_col(df, a) for a in AGING}
    faltan_aging = [a for a, c in aging_cols.items() if c is None]
    if faltan_aging:
        raise Exception("A la BD Cartera le faltan columnas de aging: "
                        + ", ".join(faltan_aging))

    df = df[df[c_vendedor].notna()].copy()

    out = pd.DataFrame()
    out["Vendedor"] = df[c_vendedor].astype(str).str.strip()
    out["Clientes"] = df[c_cliente].astype(str).str.strip()
    out["TERMINOS DE PAGO"] = df[c_terminos].astype(str).str.strip()
    out["Estatus"] = df[c_estatus].astype(str).str.strip()

    # aging ya calculado -> numérico
    for a in AGING:
        out[a] = pd.to_numeric(df[aging_cols[a]], errors="coerce").fillna(0.0)

    # periodo recalculado desde la Fecha (corte de esa carga)
    fecha = pd.to_datetime(df[c_fecha], errors="coerce")
    out["MES"] = fecha.dt.month.astype("Int64")
    out["AÑO"] = fecha.dt.year.astype("Int64")
    out["SEMANA"] = fecha.apply(_weeknum_excel).astype("Int64")

    return out.reset_index(drop=True)


def leer_archivo(contents, fecha_referencia=None):
    df = leer_excel(contents)
    if df is None or df.empty:
        raise Exception("La BD de Cartera está vacía o no se pudo leer.")
    return procesar_bd_cartera(df, fecha_referencia=fecha_referencia)