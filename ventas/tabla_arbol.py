"""
=========================================================
ventas/tabla_arbol.py
=========================================================
FÁBRICA DE TABLAS JERÁRQUICAS.

Una sola función, crear_modulo_tabla(...), genera el layout
Y registra los callbacks de CUALQUIER tabla jerárquica del
dashboard de ventas. En vez de un archivo por tabla (con el
mismo cuerpo copiado), cada tabla es solo unas líneas de
configuración (ver ventas/tablas_ventas.py).

Reutiliza:
  • core.arbol   -> construir_arbol / total_general / filas_visibles
  • ventas.aggrid -> dibujo del grid (mismo look que la tabla original)
  • ventas.filtros -> filtro Mes/Semana compartido

ORDEN: se controla desde Python con un dropdown "Ordenar por"
(no con el sort del encabezado de AG Grid). El motor recibe
columna_orden y devuelve las filas ya ordenadas jerárquicamente,
así AG Grid no reordena nada y la jerarquía nunca se rompe.

IDs: todos llevan un sufijo por-tabla (clave) para que varias
tablas convivan sin chocar. Se usan IDs de diccionario
(pattern-matching) con {"type": ..., "index": clave}.
"""

from dash import Input, Output, State, html, dcc, no_update, MATCH
import pandas as pd

from ventas.filtros import filtrar_dataframe
from core import columnas as C
from ventas.aggrid import (
    crear_aggrid, crear_encabezado_periodo,
    configuracion_tamano, estilo_grid, opciones_grid,
)
from core.arbol import (
    construir_arbol, total_general, filas_visibles,
    COLUMNAS_ORDEN_VALIDAS, ORDEN_ALFABETICO,
)


# Dropdown único "Ordenar por": cada opción codifica métrica y
# dirección en un solo value "columna|asc" o "columna|desc".
# ORDEN_ALFABETICO ordena por el nombre de la primera columna.
OPCIONES_ORDEN = [
    {"label": "Ut Bruta MN ↓", "value": "Utilidad Bruta|desc"},
    {"label": "Ut Bruta MN ↑", "value": "Utilidad Bruta|asc"},
    {"label": "Venta MN ↓", "value": "Venta|desc"},
    {"label": "Venta MN ↑", "value": "Venta|asc"},
    {"label": "Cantidad ↓", "value": "Cantidad|desc"},
    {"label": "Cantidad ↑", "value": "Cantidad|asc"},
    {"label": "Margen % ↓", "value": "Margen %|desc"},
    {"label": "Margen % ↑", "value": "Margen %|asc"},
    {"label": "Ut. Unitaria ↓", "value": "Utilidad Unitaria|desc"},
    {"label": "Ut. Unitaria ↑", "value": "Utilidad Unitaria|asc"},
    {"label": "Nombre A-Z", "value": f"{ORDEN_ALFABETICO}|asc"},
    {"label": "Nombre Z-A", "value": f"{ORDEN_ALFABETICO}|desc"},
]
ORDEN_POR_DEFECTO = "Utilidad Bruta|desc"


def _parse_orden(value):
    """Convierte 'columna|asc' -> (columna, ascendente_bool)."""
    if not value or "|" not in value:
        return C.UTILIDAD_BRUTA, False
    col, dirn = value.rsplit("|", 1)
    return col, (dirn == "asc")


# ---- Tipos de id (pattern-matching) ----
def _id(tipo, clave):
    return {"type": tipo, "index": clave}


def crear_layout_tabla(clave, niveles, titulo=None):
    """
    Layout de una tabla: título + dropdown de orden + stores +
    contenedor del grid. 'clave' es un identificador corto y
    único (p.ej. 'prod_cli'); 'niveles' la lista de dimensiones;
    'titulo' el encabezado visible (por defecto, los niveles
    unidos por ' / ').
    """
    if titulo is None:
        titulo = " / ".join(niveles)

    return html.Div(
        [
            dcc.Store(id=_id("tabla-niveles", clave), data=niveles),
            dcc.Store(id=_id("tabla-clave", clave), data=clave),
            dcc.Store(id=_id("tabla-arbol", clave), data=None),
            dcc.Store(id=_id("tabla-total", clave), data=None),
            dcc.Store(id=_id("tabla-exp", clave), data=[]),

            html.Div(
                [
                    html.H4(
                        titulo,
                        style={"color": "#173C73", "fontWeight": "700",
                               "margin": "0"},
                    ),
                    html.Div(
                        [
                            html.Span("Ordenar por: ",
                                      style={"fontWeight": "600",
                                             "color": "#173C73",
                                             "marginRight": "8px"}),
                            dcc.Dropdown(
                                id=_id("tabla-orden", clave),
                                options=OPCIONES_ORDEN,
                                value=ORDEN_POR_DEFECTO,
                                clearable=False,
                                style={"width": "230px"},
                            ),
                        ],
                        style={"display": "flex", "alignItems": "center"},
                    ),
                ],
                style={"display": "flex", "justifyContent": "space-between",
                       "alignItems": "center", "marginTop": "10px",
                       "marginBottom": "12px"},
            ),

            html.Div(id=_id("tabla-cont", clave)),
        ]
    )


def registrar_callbacks_tablas(app):
    """
    Registra UNA sola vez los callbacks pattern-matching que
    sirven a TODAS las tablas creadas con esta fábrica. Cada
    callback usa MATCH sobre 'index' (la clave), así que Dash
    lo aplica de forma independiente a cada tabla.
    """

    # 1) Construir tabla cuando cambian datos, filtro u orden
    @app.callback(
        Output(_id("tabla-cont", MATCH), "children"),
        Output(_id("tabla-arbol", MATCH), "data"),
        Output(_id("tabla-total", MATCH), "data"),
        Input("store-bd-ventas", "data"),
        Input("store-mes", "data"),
        Input("store-semana", "data"),
        Input(_id("tabla-orden", MATCH), "value"),
        State(_id("tabla-niveles", MATCH), "data"),
        State(_id("tabla-clave", MATCH), "data"),
        State(_id("tabla-exp", MATCH), "data"),
    )
    def construir(data, meses, semanas, orden, niveles, clave, ids_expandidos):
        if data is None:
            return (
                html.Div("Procesa un archivo para ver la tabla.",
                         style={"color": "#6C757D"}),
                None, None,
            )
        try:
            df = pd.DataFrame(data)
            df_f = filtrar_dataframe(df, meses=meses, semanas=semanas)

            columna, ascendente = _parse_orden(orden)
            if columna != ORDEN_ALFABETICO and columna not in COLUMNAS_ORDEN_VALIDAS:
                columna, ascendente = C.UTILIDAD_BRUTA, False

            arbol = construir_arbol(df_f, niveles=niveles,
                                    columna_orden=columna, ascendente=ascendente)
            total = total_general(df_f)

            col_fecha = "Asiento contable/Fecha de factura"
            fecha_corte = "N/D"
            if col_fecha in df_f.columns and len(df_f) > 0:
                fmax = pd.to_datetime(df_f[col_fecha], errors="coerce").max()
                if pd.notna(fmax):
                    fecha_corte = fmax.strftime("%d/%m/%Y")
            semanas_txt = (
                ", ".join(str(s) for s in sorted(semanas)) if semanas else "Todas"
            )

            visibles = filas_visibles(arbol, ids_expandidos or [])
            grid_id = _id("tabla-grid", clave)
            contenido = html.Div([
                crear_encabezado_periodo(fecha_corte, semanas_txt),
                crear_aggrid(visibles, fila_total=total,
                             id_grid=grid_id,
                             titulo_concepto=" / ".join(niveles)),
            ])
            return contenido, arbol.to_dict("records"), total
        except Exception as e:
            return (
                html.Div([html.H3("ERROR"), html.Pre(str(e))],
                         style={"color": "red"}),
                None, None,
            )

    # 2) Refresco ligero al expandir/contraer
    @app.callback(
        Output(_id("tabla-grid", MATCH), "rowData"),
        Output(_id("tabla-grid", MATCH), "style"),
        Output(_id("tabla-grid", MATCH), "dashGridOptions"),
        Input(_id("tabla-exp", MATCH), "data"),
        State(_id("tabla-arbol", MATCH), "data"),
        State(_id("tabla-total", MATCH), "data"),
        prevent_initial_call=True,
    )
    def refrescar(ids_expandidos, arbol_data, total):
        if arbol_data is None:
            return no_update, no_update, no_update
        arbol = pd.DataFrame(arbol_data)
        visibles = filas_visibles(arbol, ids_expandidos or [])
        extra, alto = configuracion_tamano(len(visibles), hay_total=bool(total))
        pinned = [total] if total else None
        return (visibles.to_dict("records"),
                estilo_grid(alto), opciones_grid(pinned, extra))

    # 3) Expandir/contraer al hacer clic
    @app.callback(
        Output(_id("tabla-exp", MATCH), "data"),
        Input(_id("tabla-grid", MATCH), "cellClicked"),
        State(_id("tabla-exp", MATCH), "data"),
        State(_id("tabla-niveles", MATCH), "data"),
        prevent_initial_call=True,
    )
    def alternar(celda, ids_expandidos, niveles):
        if celda is None:
            return no_update
        fila_id = celda.get("rowId")
        if fila_id is None:
            return no_update
        # hoja (último nivel) no se expande: con N niveles, el
        # último tiene (N-1) separadores "||".
        if fila_id.count("||") >= len(niveles) - 1:
            return no_update
        ids = set(ids_expandidos or [])
        if fila_id in ids:
            ids.discard(fila_id)
        else:
            ids.add(fila_id)
        return sorted(ids)