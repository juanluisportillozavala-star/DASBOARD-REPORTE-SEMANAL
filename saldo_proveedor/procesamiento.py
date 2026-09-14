"""
=========================================================
PROCESAMIENTO DEL MÓDULO SALDO PROVEEDOR  (BD CxP)
=========================================================
La BD que se sube es la hoja "BD CxP" del reporte.

IMPORTANTE (corrección): el aging de la BD (columnas
"Vencido 0-30", etc.) estaba mal porque usaba el "Importe"
COMPLETO de la factura, SIN restar lo ya pagado. Aquí el
sistema RECALCULA el aging usando el saldo REAL pendiente
("Importe adeudado") y los "Dias vencido", clasificando:
    dias_vencido = 0  -> Vigente
    1  a 30           -> Vencido 0-30 días
    31 a 60           -> Vencido 31-60 días
    > 60              -> Vencido >60 días

Así el saldo por proveedor refleja lo que realmente se debe.

Se toma:
  • Proveedor  -> filas de la matriz.
  • Importe adeudado (saldo real) -> se reparte en el rango que
    corresponda según los días de vencido.
Se RECALCULAN desde la columna Fecha (por seguridad):
  • MES = MONTH(Fecha), SEMANA = WEEKNUM(Fecha), AÑO = YEAR(Fecha)

Nombres de salida (iguales que antes, para no tocar la tabla):
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


def _rango_aging(dias_vencido):
    """Devuelve en qué columna de aging cae, según días de vencido."""
    try:
        dv = float(dias_vencido)
    except (ValueError, TypeError):
        dv = 0
    if dv <= 0:
        return "Vigente"
    if dv <= 30:
        return "Vencido 0-30 días"
    if dv <= 60:
        return "Vencido 31-60 días"
    return "Vencido >60 días"


def leer_excel(contents):
    if contents is None:
        return None
    contenido = contents.split(",")[1]
    archivo = base64.b64decode(contenido)
    xls = pd.ExcelFile(io.BytesIO(archivo))
    hoja = "BD CxP" if "BD CxP" in xls.sheet_names else xls.sheet_names[0]
    return pd.read_excel(xls, sheet_name=hoja)


def procesar_bd_saldo_proveedor(df, fecha_referencia=None):
    """Limpia la BD CxP y RECALCULA el aging con el saldo real
    (Importe adeudado). fecha_referencia se ignora."""
    df = df.copy()
    df.columns = [str(c).strip() for c in df.columns]

    c_prov = _buscar_col(df, "Proveedor")
    c_fecha = _buscar_col(df, "Fecha")
    c_adeudado = _buscar_col(df, "Importe adeudado", "Importe Adeudado",
                             "Saldo", "Total pendiente")
    c_dias = _buscar_col(df, "Dias vencido", "Días vencido", "Dias vencidos",
                         "Días vencidos")
    c_estatus = _buscar_col(df, "Estatus", "Estado")

    faltan = [n for n, c in [("Proveedor", c_prov), ("Fecha", c_fecha),
                             ("Importe adeudado", c_adeudado),
                             ("Dias vencido", c_dias)] if c is None]
    if faltan:
        raise Exception("A la BD CxP le faltan columnas: " + ", ".join(faltan))

    df = df[df[c_prov].notna()].copy()

    # datos base
    proveedor = df[c_prov].astype(str).str.strip()
    adeudado = pd.to_numeric(df[c_adeudado], errors="coerce").fillna(0.0)
    dias = df[c_dias]
    fecha = pd.to_datetime(df[c_fecha], errors="coerce")

    out = pd.DataFrame()
    out["Proveedor"] = proveedor.values

    # aging RECALCULADO: cada factura pone su "Importe adeudado" (en
    # valor absoluto, por si viene negativo) en el rango que le toca.
    for a in AGING:
        out[a] = 0.0
    for i in range(len(df)):
        rango = _rango_aging(dias.iloc[i])
        # usar el saldo real; abs por si el signo viene invertido
        out.iat[i, out.columns.get_loc(rango)] = abs(float(adeudado.iloc[i]))

    out["MES"] = fecha.dt.month.astype("Int64").values
    out["AÑO"] = fecha.dt.year.astype("Int64").values
    out["SEMANA"] = fecha.apply(_weeknum_excel).astype("Int64").values

    return out.reset_index(drop=True)


def leer_archivo(contents, fecha_referencia=None):
    df = leer_excel(contents)
    if df is None or df.empty:
        raise Exception("La BD de Saldo Proveedor (CxP) está vacía o no se pudo leer.")
    return procesar_bd_saldo_proveedor(df, fecha_referencia=fecha_referencia)