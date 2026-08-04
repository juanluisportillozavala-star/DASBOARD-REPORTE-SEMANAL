"""
=========================================================
ingresos/arbol_ingresos.py
=========================================================
Árbol jerárquico de Ingresos: Vendedor -> Cliente (contacto),
expandible, con columnas cruzadas Contado/Crédito x
Vencido/Vigente + Total general.

Produce filas PLANAS con el MISMO esquema base que el motor de
Ventas (id, parentId, nivel, concepto, tieneHijos, expandido)
para poder reutilizar el diseño premium (getRowStyle por nivel)
y la expansión por clic. Las columnas de datos son las 4 cruces
y el total, en vez de Cantidad/Venta/Margen.

ESTATUS (Vigente/Vencido) es DINÁMICO: se calcula aquí según el
mes de corte que se pase (el más alto seleccionado en el
calendario), comparando el mes de vencimiento de cada factura.
"""

import pandas as pd

COL_IMPORTE = "Importe sin impuestos firmado"
COL_VENDEDOR = "Vendedor"
COL_CONTACTO = "Contacto"
COL_TERMINOS = "TERMINOS DE PAGO"     # Contado / Crédito
COL_MES_VENC = "MES_VENCIMIENTO"
COL_VENCIMIENTO = "Fecha de vencimiento"
COL_ULTIMO_PAGO = "Fecha último pago"

TERMINOS = ["Contado", "Crédito"]
ESTATUS = ["Vigente", "Vencido"]

# nombres de campo para las 4 columnas cruzadas + total
def _campo(t, e):
    return f"{t}|{e}"

CAMPOS_CRUCE = [_campo(t, e) for t in TERMINOS for e in ESTATUS]


def _anio_reporte(df):
    """Año del reporte = año MÁS COMÚN de la fecha de último pago.
    (Se conserva por compatibilidad; ya no se usa para el estatus.)"""
    fechas = pd.to_datetime(df[COL_ULTIMO_PAGO], errors="coerce").dropna()
    if len(fechas) == 0:
        return pd.Timestamp.today().year
    return int(fechas.dt.year.mode().iloc[0])


def fecha_corte(df, meses):
    """(Compatibilidad) Devuelve una fecha de referencia. Ya NO se
    usa para clasificar vigente/vencido — el estatus ahora se calcula
    por factura (vencimiento vs último pago). Se mantiene por si algún
    texto de la UI la usa."""
    anio = _anio_reporte(df)
    if meses:
        mes = max(meses)
    else:
        fp = pd.to_datetime(df[COL_ULTIMO_PAGO], errors="coerce").dropna()
        mes = int(fp.dt.month.max()) if len(fp) else 12
    return pd.Timestamp(year=anio, month=mes, day=1) + pd.offsets.MonthEnd(0)


def mes_corte(df, meses):
    return fecha_corte(df, meses)


def _con_estatus(df, corte=None):
    """Clasifica cada factura por su PROPIO par de fechas:
      Vigente  si fin_de_mes(Fecha de vencimiento) >= fin_de_mes(Fecha último pago)
               (es decir, se pagó dentro del mes de vencimiento o antes)
      Vencido  si venció en un mes anterior al del pago (pago tardío).

    El estatus es FIJO por factura: NO depende del mes de corte ni del
    calendario. El parámetro 'corte' se ignora (se deja por
    compatibilidad con las llamadas existentes).
    """
    df = df.copy()
    venc = pd.to_datetime(df[COL_VENCIMIENTO], errors="coerce")
    pago = pd.to_datetime(df[COL_ULTIMO_PAGO], errors="coerce")

    fin_venc = venc + pd.offsets.MonthEnd(0)
    fin_pago = pago + pd.offsets.MonthEnd(0)

    def clasificar(fv, fp):
        if pd.isna(fv) or pd.isna(fp):
            return None
        return "Vigente" if fv >= fp else "Vencido"

    df["_ESTATUS"] = [clasificar(fv, fp) for fv, fp in zip(fin_venc, fin_pago)]
    return df


def _sumas_cruce(sub):
    """Dict {campo_cruce: suma} para un subconjunto de filas."""
    d = {}
    total = 0.0
    for t in TERMINOS:
        for e in ESTATUS:
            monto = sub[(sub[COL_TERMINOS] == t) & (sub["_ESTATUS"] == e)][COL_IMPORTE].sum()
            monto = float(monto) if monto and not pd.isna(monto) else 0.0
            d[_campo(t, e)] = monto if monto != 0 else None
            total += monto
    d["total"] = total if total != 0 else None
    return d


def construir_arbol_ingresos(df, meses):
    """
    Devuelve un DataFrame plano (filas de Vendedor y Cliente)
    con columnas: id, parentId, nivel, concepto, tieneHijos,
    expandido, los 4 cruces y total. Ordenado por total
    descendente dentro de cada nivel.
    """
    # ESTATUS fijo por factura (vencimiento vs último pago); no
    # depende del calendario. El filtro de meses ya se aplicó antes.
    df = _con_estatus(df)

    filas = []

    # nivel 1: vendedores, ordenados por total desc
    vendedores = df[COL_VENDEDOR].dropna().unique().tolist()
    tot_por_vend = []
    for v in vendedores:
        sub_v = df[df[COL_VENDEDOR] == v]
        sumas_v = _sumas_cruce(sub_v)
        tot_por_vend.append((v, sumas_v.get("total") or 0, sumas_v, sub_v))
    tot_por_vend.sort(key=lambda x: x[1], reverse=True)

    for v, _tot, sumas_v, sub_v in tot_por_vend:
        id_v = f"n0::{v}"
        fila_v = {"id": id_v, "parentId": "", "nivel": 1,
                  "concepto": str(v), "tieneHijos": True, "expandido": False}
        fila_v.update(sumas_v)
        filas.append(fila_v)

        # nivel 2: contactos de ese vendedor, ordenados por total desc
        contactos = sub_v[COL_CONTACTO].dropna().unique().tolist()
        tot_por_cont = []
        for c in contactos:
            sub_c = sub_v[sub_v[COL_CONTACTO] == c]
            sumas_c = _sumas_cruce(sub_c)
            tot_por_cont.append((c, sumas_c.get("total") or 0, sumas_c))
        tot_por_cont.sort(key=lambda x: x[1], reverse=True)

        for c, _tc, sumas_c in tot_por_cont:
            id_c = f"{id_v}||n1::{c}"
            fila_c = {"id": id_c, "parentId": id_v, "nivel": 2,
                      "concepto": str(c), "tieneHijos": False, "expandido": False}
            fila_c.update(sumas_c)
            filas.append(fila_c)

    cols = ["id", "parentId", "nivel", "concepto", "tieneHijos", "expandido"] + CAMPOS_CRUCE + ["total"]
    return pd.DataFrame(filas, columns=cols)


def total_general_ingresos(df, meses):
    """Fila TOTAL GENERAL (nivel 0) con los cruces globales."""
    d = _con_estatus(df)
    sumas = _sumas_cruce(d)
    fila = {"id": "total", "parentId": "", "nivel": 0,
            "concepto": "TOTAL GENERAL", "tieneHijos": False, "expandido": False}
    fila.update(sumas)
    return fila


def filas_visibles_ingresos(df_arbol, ids_expandidos):
    """Filtra a las filas visibles según expansión y hornea el
    ícono ▶/▼ + indentación en 'concepto'."""
    if df_arbol is None or len(df_arbol) == 0:
        return df_arbol

    ids_expandidos = set(ids_expandidos or [])
    padres = dict(zip(df_arbol["id"], df_arbol["parentId"]))

    def es_visible(fid, nivel):
        if nivel == 1:
            return True
        p = padres.get(fid, "")
        if p == "" or p not in ids_expandidos:
            return False
        return es_visible(p, nivel - 1)

    mask = df_arbol.apply(lambda f: es_visible(f["id"], f["nivel"]), axis=1)
    res = df_arbol[mask].reset_index(drop=True)
    res["expandido"] = res["id"].isin(ids_expandidos)

    def _texto(f):
        sangria = "\u00a0" * (f["nivel"] * 6)
        if f["tieneHijos"]:
            icono = "▼ " if f["expandido"] else "▶ "
        elif f["nivel"] > 1:
            icono = "\u00a0\u00a0\u00a0"
        else:
            icono = ""
        return sangria + icono + str(f["concepto"])

    res["concepto"] = res.apply(_texto, axis=1)
    return res