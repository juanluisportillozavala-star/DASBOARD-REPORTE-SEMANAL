"""
=========================================================
ingresos/arbol_ingresos.py
=========================================================
Árbol jerárquico de Ingresos: Vendedor -> Cliente, expandible,
con columnas cruzadas (Términos de pago × Estatus) + Total.

Cambios vs versión anterior:
  • El ESTATUS ya NO se calcula: se usa el que trae la BD Cobranza
    (columna "Estatus": Vigente / Vencido).
  • Nombres de columna de la BD Cobranza: Importe -> "IMPORTE",
    cliente -> "Cliente", términos -> "TERMINOS DE PAGO".
  • Columnas DINÁMICAS: la matriz solo muestra las combinaciones
    (Términos × Estatus) que existan en los datos filtrados,
    ordenadas Contado→Crédito y Vigente→Vencido (ver
    combos_presentes()).

Produce filas PLANAS con el mismo esquema base (id, parentId,
nivel, concepto, tieneHijos, expandido) para reutilizar el
diseño premium y la expansión por clic.
"""

import pandas as pd

COL_IMPORTE = "IMPORTE"
COL_VENDEDOR = "Vendedor"
COL_CLIENTE = "Cliente"
COL_TERMINOS = "TERMINOS DE PAGO"     # Contado / Crédito
COL_ESTATUS = "ESTATUS"               # Vigente / Vencido (de la BD)

# orden deseado: Contado antes que Crédito; Vigente antes que Vencido
TERMINOS = ["Contado", "Crédito"]
ESTATUS = ["Vigente", "Vencido"]


def _campo(t, e):
    return f"{t}|{e}"


# todas las combinaciones posibles (por si algo las necesita)
CAMPOS_CRUCE = [_campo(t, e) for t in TERMINOS for e in ESTATUS]


def combos_presentes(df):
    """Lista de (termino, estatus) que TIENEN datos en df, en el
    orden Contado→Crédito, Vigente→Vencido. Sirve para armar las
    columnas dinámicas (como la tabla dinámica de Excel: solo salen
    las combinaciones que existen)."""
    if df is None or len(df) == 0:
        return []
    presentes = []
    for t in TERMINOS:
        for e in ESTATUS:
            hay = df[(df[COL_TERMINOS] == t) & (df[COL_ESTATUS] == e)]
            if len(hay) and float(hay[COL_IMPORTE].sum()) != 0:
                presentes.append((t, e))
    return presentes


def _sumas_cruce(sub, combos):
    """Dict {campo_cruce: suma} para un subconjunto, solo de los
    combos indicados, + total."""
    d = {}
    total = 0.0
    for t, e in combos:
        monto = sub[(sub[COL_TERMINOS] == t) & (sub[COL_ESTATUS] == e)][COL_IMPORTE].sum()
        monto = float(monto) if monto and not pd.isna(monto) else 0.0
        d[_campo(t, e)] = monto if monto != 0 else None
        total += monto
    d["total"] = total if total != 0 else None
    return d


def construir_arbol_ingresos(df, meses=None):
    """DataFrame plano (Vendedor y Cliente) con columnas: id,
    parentId, nivel, concepto, tieneHijos, expandido, los cruces
    presentes y total. Ordenado por total desc dentro de cada nivel.
    El filtro de año/mes/semana ya se aplicó antes."""
    combos = combos_presentes(df)
    campos = [_campo(t, e) for t, e in combos]

    filas = []

    vendedores = df[COL_VENDEDOR].dropna().unique().tolist()
    tot_por_vend = []
    for v in vendedores:
        sub_v = df[df[COL_VENDEDOR] == v]
        sumas_v = _sumas_cruce(sub_v, combos)
        tot_por_vend.append((v, sumas_v.get("total") or 0, sumas_v, sub_v))
    tot_por_vend.sort(key=lambda x: x[1], reverse=True)

    for v, _tot, sumas_v, sub_v in tot_por_vend:
        id_v = f"n0::{v}"
        fila_v = {"id": id_v, "parentId": "", "nivel": 1,
                  "concepto": str(v), "tieneHijos": True, "expandido": False}
        fila_v.update(sumas_v)
        filas.append(fila_v)

        clientes = sub_v[COL_CLIENTE].dropna().unique().tolist()
        tot_por_cli = []
        for c in clientes:
            sub_c = sub_v[sub_v[COL_CLIENTE] == c]
            sumas_c = _sumas_cruce(sub_c, combos)
            tot_por_cli.append((c, sumas_c.get("total") or 0, sumas_c))
        tot_por_cli.sort(key=lambda x: x[1], reverse=True)

        for c, _tc, sumas_c in tot_por_cli:
            id_c = f"{id_v}||n1::{c}"
            fila_c = {"id": id_c, "parentId": id_v, "nivel": 2,
                      "concepto": str(c), "tieneHijos": False, "expandido": False}
            fila_c.update(sumas_c)
            filas.append(fila_c)

    cols = (["id", "parentId", "nivel", "concepto", "tieneHijos", "expandido"]
            + campos + ["total"])
    return pd.DataFrame(filas, columns=cols)


def total_general_ingresos(df, meses=None):
    """Fila TOTAL GENERAL (nivel 0) con los cruces presentes."""
    combos = combos_presentes(df)
    sumas = _sumas_cruce(df, combos)
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