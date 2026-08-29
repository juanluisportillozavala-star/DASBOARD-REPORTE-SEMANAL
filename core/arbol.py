"""
=========================================================
core/arbol.py
=========================================================
MOTOR JERÁRQUICO GENERALIZADO (N niveles).

Generaliza lo que ventas/analisis.arbol_ventas hacía con
3 niveles FIJOS (Vendedor>Cliente>Producto) a una lista
de niveles ARBITRARIA:

    construir_arbol(df, niveles=["Producto", "Cliente"])
    construir_arbol(df, niveles=["Vendedor", "Producto"])
    ...

Una sola función alimenta las 4 tablas de la hoja Ventas.
Reutiliza core.metricas (margen / utilidad unitaria) y
core.columnas (nombres). No sabe nada de Dash ni de AG
Grid: solo produce un DataFrame plano listo para pintar,
con el MISMO esquema de columnas que el árbol original,
para que aggrid.py lo dibuje sin cambios.

Contrato de salida (idéntico al árbol viejo):
  id, parentId, nivel, concepto, Cantidad, Venta,
  Utilidad Bruta, Margen %, Utilidad Unitaria,
  tieneHijos, expandido, _ruta_<metrica> por cada métrica.
"""

import pandas as pd

from core import columnas as C
from core.metricas import agregar_metricas_df, margen, utilidad_unitaria


COLUMNAS_ORDEN_VALIDAS = [
    C.VENTA, C.UTILIDAD_BRUTA, C.CANTIDAD, C.MARGEN, C.UTILIDAD_UNITARIA,
]

_BASE = ["id", "parentId", "nivel", "concepto",
         C.CANTIDAD, C.VENTA, C.UTILIDAD_BRUTA, C.MARGEN, C.UTILIDAD_UNITARIA,
         "tieneHijos", "expandido"]

COLUMNAS_ARBOL = _BASE + [f"_ruta_{m}" for m in COLUMNAS_ORDEN_VALIDAS]


def _rangos(df, grupo=None):
    df = df.copy()
    for m in COLUMNAS_ORDEN_VALIDAS:
        col = f"rango_{m}"
        if grupo:
            df[col] = df.groupby(grupo)[m].rank(method="first", ascending=True)
        else:
            df[col] = df[m].rank(method="first", ascending=True)
        df[col] = df[col].astype(int) - 1
    return df


# Valor especial de columna_orden para ordenar por el nombre
# (texto del nivel) en vez de por una métrica numérica.
ORDEN_ALFABETICO = "__alfabetico__"


def construir_arbol(df_crudo, niveles, columna_orden=C.UTILIDAD_BRUTA,
                    ascendente=False):
    """
    df_crudo: DataFrame de ventas enriquecido (columnas crudas
              de Odoo + Producto 2). El mismo insumo que usa el
              árbol viejo.
    niveles:  lista de dimensiones amigables, p.ej.
              ["Producto", "Cliente"]. Cada una debe estar en
              C.DIMENSION_A_RAW.
    columna_orden: métrica de ordenamiento (default Ut Bruta MN),
              o ORDEN_ALFABETICO para ordenar por el nombre del
              nivel (A-Z / Z-A).
    ascendente: False = mayor a menor (o Z-A si alfabético);
              True = menor a mayor (o A-Z si alfabético).
    """
    alfabetico = (columna_orden == ORDEN_ALFABETICO)
    if not alfabetico and columna_orden not in COLUMNAS_ORDEN_VALIDAS:
        columna_orden = C.UTILIDAD_BRUTA

    if df_crudo is None or len(df_crudo) == 0 or not niveles:
        return pd.DataFrame(columns=COLUMNAS_ARBOL)

    # ---- renombrar solo las columnas necesarias ----
    # Se construye el mapa validando ANTES contra las columnas
    # crudas reales. Nota: una dimensión (p.ej. Producto) puede
    # mapear a una columna cruda cuyo nombre YA es el destino
    # (Producto 2 -> Producto); se filtran esos casos y los
    # renombrados identidad para no pedir columnas inexistentes.
    mapa = {}
    for dim in niveles:
        cruda = C.DIMENSION_A_RAW[dim]
        if cruda != dim:
            mapa[cruda] = dim
    if C.RAW_CANTIDAD != C.CANTIDAD:
        mapa[C.RAW_CANTIDAD] = C.CANTIDAD
    if C.RAW_CREDITO != C.VENTA:
        mapa[C.RAW_CREDITO] = C.VENTA
    if C.UT_BRUTA != C.UTILIDAD_BRUTA:
        mapa[C.UT_BRUTA] = C.UTILIDAD_BRUTA

    faltantes = [c for c in mapa if c not in df_crudo.columns]
    if faltantes:
        raise KeyError("construir_arbol: faltan columnas: " + ", ".join(faltantes))

    df = df_crudo.rename(columns=mapa)[niveles + [C.CANTIDAD, C.VENTA, C.UTILIDAD_BRUTA]].copy()
    for dim in niveles:
        df[dim] = df[dim].fillna(f"Sin {dim.lower()}")

    num = [C.CANTIDAD, C.VENTA, C.UTILIDAD_BRUTA]

    # ---- agregados por nivel (de más fino a más grueso) ----
    # niveles_acumulados[k] = groupby de los primeros k+1 niveles
    agregados = []
    for k in range(len(niveles)):
        grupo = niveles[: k + 1]
        g = df.groupby(grupo, as_index=False)[num].sum()
        g[num] = g[num].astype(float)
        g = agregar_metricas_df(g)
        padre = niveles[:k] if k > 0 else None
        g = _rangos(g, grupo=padre)
        agregados.append(g)

    # nivel más grueso (0): por nombre (alfabético) o por métrica
    col0 = niveles[0] if alfabetico else columna_orden
    agregados[0] = agregados[0].sort_values(col0, ascending=ascendente)

    # ---- índices hijos-por-padre, para recorrido en profundidad ----
    # clave = tupla de valores de niveles[:k+1]
    hijos = []
    for k in range(len(niveles)):
        # alfabético -> ordenar por el nombre del nivel k; si no, por métrica
        col_k = niveles[k] if alfabetico else columna_orden
        g = agregados[k].sort_values(col_k, ascending=ascendente)
        d = {}
        for reg in g.to_dict("records"):
            if k == 0:
                clave = ()
            else:
                clave = tuple(reg[niveles[j]] for j in range(k))
            d.setdefault(clave, []).append(reg)
        hijos.append(d)

    # ---- armar filas planas en profundidad ----
    cols = {c: [] for c in _BASE}
    rutas = {m: [] for m in COLUMNAS_ORDEN_VALIDAS}

    def emit(id_, parent, nivel, concepto, reg, ruta, tiene_hijos):
        cols["id"].append(id_)
        cols["parentId"].append(parent)
        cols["nivel"].append(nivel + 1)  # 1-based como el árbol viejo
        cols["concepto"].append(str(concepto))
        cols[C.CANTIDAD].append(reg[C.CANTIDAD])
        cols[C.VENTA].append(reg[C.VENTA])
        cols[C.UTILIDAD_BRUTA].append(reg[C.UTILIDAD_BRUTA])
        cols[C.MARGEN].append(reg[C.MARGEN])
        cols[C.UTILIDAD_UNITARIA].append(reg[C.UTILIDAD_UNITARIA])
        cols["tieneHijos"].append(tiene_hijos)
        cols["expandido"].append(False)
        for m in COLUMNAS_ORDEN_VALIDAS:
            rutas[m].append(ruta[m])

    ultimo = len(niveles) - 1

    def recorrer(k, clave_padre, id_padre, ruta_padre):
        for reg in hijos[k].get(clave_padre, []):
            val = reg[niveles[k]]
            id_ = f"{id_padre}||n{k}::{val}" if id_padre else f"n{k}::{val}"
            ruta = {m: ruta_padre[m] + [int(reg[f"rango_{m}"])] for m in COLUMNAS_ORDEN_VALIDAS}
            tiene = k < ultimo
            emit(id_, id_padre, k, val, reg, ruta, tiene)
            if tiene:
                clave_hijo = (clave_padre + (val,)) if clave_padre != () else (val,)
                recorrer(k + 1, clave_hijo, id_, ruta)

    ruta0 = {m: [] for m in COLUMNAS_ORDEN_VALIDAS}
    recorrer(0, (), "", ruta0)

    datos = {c: cols[c] for c in _BASE}
    for m in COLUMNAS_ORDEN_VALIDAS:
        datos[f"_ruta_{m}"] = rutas[m]
    return pd.DataFrame(datos, columns=COLUMNAS_ARBOL)


def total_general(df_crudo):
    if df_crudo is None or len(df_crudo) == 0:
        c = v = u = 0.0
    else:
        c = float(df_crudo[C.RAW_CANTIDAD].sum())
        v = float(df_crudo[C.RAW_CREDITO].sum())
        u = float(df_crudo[C.UT_BRUTA].sum())
    return {
        "id": "total", "parentId": "", "nivel": 0, "concepto": "TOTAL GENERAL",
        C.CANTIDAD: c, C.VENTA: v, C.UTILIDAD_BRUTA: u,
        C.MARGEN: margen(u, v), C.UTILIDAD_UNITARIA: utilidad_unitaria(u, c),
        "tieneHijos": False, "expandido": False,
    }


def filas_visibles(df_arbol, ids_expandidos):
    """
    Filtra el árbol a las filas que deben verse según qué nodos
    están expandidos, y hornea indentación + ícono ▶/▼ en la
    columna 'concepto' (igual que el árbol original, para que el
    refresco ligero de rowData redibuje bien en AG Grid).

    Funciona con el formato de id del motor generalizado:
    "n0::Valor||n1::Valor||n2::Valor". El nivel de una fila se
    deduce de cuántos "||" tiene el id (0 sep = nivel 1, etc.).
    """
    if df_arbol is None or len(df_arbol) == 0:
        return df_arbol

    ids_expandidos = set(ids_expandidos or [])
    padres = dict(zip(df_arbol["id"], df_arbol["parentId"]))

    def es_visible(fila_id, nivel):
        if nivel == 1:
            return True
        padre = padres.get(fila_id, "")
        if padre == "" or padre not in ids_expandidos:
            return False
        return es_visible(padre, nivel - 1)

    mascara = df_arbol.apply(
        lambda fila: es_visible(fila["id"], fila["nivel"]),
        axis=1,
    )
    resultado = df_arbol[mascara].reset_index(drop=True)
    resultado["expandido"] = resultado["id"].isin(ids_expandidos)

    def _texto_visual(fila):
        sangria = "\u00a0" * (fila["nivel"] * 6)
        if fila["tieneHijos"]:
            icono = "▼ " if fila["expandido"] else "▶ "
        elif fila["nivel"] > 0:
            icono = "\u00a0\u00a0\u00a0"
        else:
            icono = ""
        return sangria + icono + str(fila["concepto"])

    resultado["concepto"] = resultado.apply(_texto_visual, axis=1)
    return resultado


def profundidad_maxima_id(fila_id):
    """Nº de niveles bajo un id (cuántos '||' tiene). Sirve al
    callback para decidir si una fila es hoja (no expandible)."""
    return fila_id.count("||")