"""
=========================================================
PROCESAMIENTO DEL MÓDULO SALDO PROVEEDOR  (BD CxP)
=========================================================
La BD que se sube es la hoja "BD CxP" del reporte, YA FORMULADA
(trae el aging, Estatus, Mes y Semana calculados). Se lee tal
cual y se deja un DataFrame limpio para la matriz.

NO se pide fecha de corte (la BD ya trae su columna Fecha).

Se toma:
  • Proveedor  -> filas de la matriz.
  • Las 4 columnas de AGING ya calculadas (se suman tal cual):
      Vencido 0-30 días, Vencido 31-60 días, Vencido >60 días, Vigente
Se RECALCULAN desde la columna Fecha (por seguridad):
  • MES = MONTH(Fecha), SEMANA = WEEKNUM(Fecha), AÑO = YEAR(Fecha)

Nombres de salida:
  Proveedor, Vencido 0-30 días, Vencido 31-60 días,
  Vencido >60 días, Vigente, MES, SEMANA, AÑO
"""

import base64
import io
from datetime import date
import pandas as pd

AGING = ["Vencido 0-30 días", "Vencido 31-60 días", "Vencido >60 días", "Vigente"]


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
    hoja = "BD CxP" if "BD CxP" in xls.sheet_names else xls.sheet_names[0]
    return pd.read_excel(xls, sheet_name=hoja)


def procesar_bd_saldo_proveedor(df, fecha_referencia=None):
    """Limpia la BD CxP formulada. fecha_referencia se ignora
    (se deja por compatibilidad de firma)."""
    df = df.copy()
    df.columns = [str(c).strip() for c in df.columns]

    c_prov = _buscar_col(df, "Proveedor")
    c_fecha = _buscar_col(df, "Fecha")

    faltan = [n for n, c in [("Proveedor", c_prov), ("Fecha", c_fecha)] if c is None]
    if faltan:
        raise Exception("A la BD CxP le faltan columnas: " + ", ".join(faltan))

    aging_cols = {a: _buscar_col(df, a) for a in AGING}
    faltan_aging = [a for a, c in aging_cols.items() if c is None]
    if faltan_aging:
        raise Exception("A la BD CxP le faltan columnas de aging: "
                        + ", ".join(faltan_aging))

    df = df[df[c_prov].notna()].copy()

    out = pd.DataFrame()
    out["Proveedor"] = df[c_prov].astype(str).str.strip()
    for a in AGING:
        out[a] = pd.to_numeric(df[aging_cols[a]], errors="coerce").fillna(0.0)

    fecha = pd.to_datetime(df[c_fecha], errors="coerce")
    out["MES"] = fecha.dt.month.astype("Int64")
    out["AÑO"] = fecha.dt.year.astype("Int64")
    out["SEMANA"] = fecha.apply(_weeknum_excel).astype("Int64")

    return out.reset_index(drop=True)


def leer_archivo(contents, fecha_referencia=None):
    df = leer_excel(contents)
    if df is None or df.empty:
        raise Exception("La BD de Saldo Proveedor (CxP) está vacía o no se pudo leer.")
    return procesar_bd_saldo_proveedor(df, fecha_referencia=fecha_referencia)