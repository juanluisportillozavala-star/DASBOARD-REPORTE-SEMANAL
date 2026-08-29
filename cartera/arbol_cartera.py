"""
=========================================================
cartera/arbol_cartera.py
=========================================================
Árbol jerárquico de Cartera: Vendedor -> Cliente, expandible,
con los 7 rangos de aging como columnas:
  Vencido >90, Vencido 61-90, Vencido 31-60, Vencido 0-30,
  Por vencer, Vigente, Total Cartera.

El aging YA viene calculado por el procesamiento (columnas de
aging por fila). Aquí solo se SUMAN por vendedor y por cliente.
El cliente viene en la columna "Clientes" (BD Cartera).
"""

import pandas as pd

COL_VENDEDOR = "Vendedor"
COL_CLIENTE = "Clientes"

# columnas de aging (campo interno -> etiqueta visible)
RANGOS = [
    ("v90",   "Vencido >90 días"),
    ("v6190", "Vencido 61-90 días"),
    ("v3160", "Vencido 31-60 días"),
    ("v030",  "Vencido 0-30 días"),
    ("porv",  "Por vencer"),
    ("vig",   "Vigente"),
]

# mapa campo interno -> columna del DataFrame procesado
_COL_DE = {
    "v90":   "Vencido >90 días",
    "v6190": "Vencido 61-90 días",
    "v3160": "Vencido 31-60 días",
    "v030":  "Vencido 0-30 días",
    "porv":  "Por vencer",
    "vig":   "Vigente",
}

CAMPOS = [c for c, _ in RANGOS]


def _sumas(sub):
    """Dict {campo: suma} + total, para un subconjunto de filas."""
    d = {}
    total = 0.0
    for campo in CAMPOS:
        col = _COL_DE[campo]
        val = float(sub[col].sum()) if col in sub.columns else 0.0
        d[campo] = val if val != 0 else None
        total += val
    d["total"] = total if total != 0 else None
    return d


def construir_arbol_cartera(df):
    """DataFrame plano con filas de Vendedor (nivel 1) y Cliente
    (nivel 2), ordenadas por total descendente."""
    filas = []

    vendedores = df[COL_VENDEDOR].dropna().unique().tolist()
    tot_vend = []
    for v in vendedores:
        sub_v = df[df[COL_VENDEDOR] == v]
        s = _sumas(sub_v)
        tot_vend.append((v, s.get("total") or 0, s, sub_v))
    tot_vend.sort(key=lambda x: x[1], reverse=True)

    for v, _t, s_v, sub_v in tot_vend:
        id_v = f"n0::{v}"
        fila_v = {"id": id_v, "parentId": "", "nivel": 1,
                  "concepto": str(v), "tieneHijos": True, "expandido": False}
        fila_v.update(s_v)
        filas.append(fila_v)

        clientes = sub_v[COL_CLIENTE].dropna().unique().tolist()
        tot_cli = []
        for c in clientes:
            sub_c = sub_v[sub_v[COL_CLIENTE] == c]
            s_c = _sumas(sub_c)
            tot_cli.append((c, s_c.get("total") or 0, s_c))
        tot_cli.sort(key=lambda x: x[1], reverse=True)

        for c, _tc, s_c in tot_cli:
            id_c = f"{id_v}||n1::{c}"
            fila_c = {"id": id_c, "parentId": id_v, "nivel": 2,
                      "concepto": str(c), "tieneHijos": False, "expandido": False}
            fila_c.update(s_c)
            filas.append(fila_c)

    cols = ["id", "parentId", "nivel", "concepto", "tieneHijos", "expandido"] + CAMPOS + ["total"]
    return pd.DataFrame(filas, columns=cols)


def total_general_cartera(df):
    s = _sumas(df)
    fila = {"id": "total", "parentId": "", "nivel": 0,
            "concepto": "TOTAL CARTERA", "tieneHijos": False, "expandido": False}
    fila.update(s)
    return fila


def filas_visibles_cartera(df_arbol, ids_expandidos):
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