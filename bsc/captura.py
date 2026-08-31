"""
=========================================================
bsc/captura.py  —  CAPTURA del BSC (tabla editable)
=========================================================
Pantalla de admin (/bsc-captura): seleccionas año y mes y
capturas, en UNA tabla editable tipo Excel:
  - la columna Objetivo de cada indicador, y
  - una columna por semana del mes (valores reales).

Solo se editan las filas CAPTURABLES (los padres que se calculan
por suma no aparecen aquí). Al picar "Guardar", se lee el rowData
del grid y se persiste con bsc/datos.py.

NOTA técnica: se lee el estado editado vía State("bsc-cap-grid",
"rowData"), soportado por dash_ag_grid 35.x.
"""

from dash import Input, Output, State, html, dcc, no_update, ctx
import dash_ag_grid as dag

from bsc import catalogo, datos
from bsc import semanas as S

AZUL = "#173C73"
DORADO = "#D4AF37"

MESES = [(1, "Enero"), (2, "Febrero"), (3, "Marzo"), (4, "Abril"),
         (5, "Mayo"), (6, "Junio"), (7, "Julio"), (8, "Agosto"),
         (9, "Septiembre"), (10, "Octubre"), (11, "Noviembre"),
         (12, "Diciembre")]
_MES_NOMBRE = dict(MESES)


def _estilo_grid(alto):
    return {
        "width": "100%", "height": alto,
        "--ag-font-size": "14px",
        "--ag-header-background-color": AZUL,
        "--ag-header-foreground-color": "#FFFFFF",
        "--ag-background-color": "#FFFFFF",
        "--ag-border-color": "#E7DBB0",
        "--ag-row-hover-color": "#EEF3FA",
    }


def crear_layout_captura_bsc():
    anios_guardados = datos.anios_con_bsc()
    # ofrecer del 2025 al 2035 (como proyección) + los que ya existan
    anios = sorted(set(list(range(2025, 2036)) + anios_guardados), reverse=True)
    anio_val = (anios_guardados[0] if anios_guardados else 2026)

    return html.Div(
        [
            html.H1("Captura BSC", className="titulo"),
            html.P("Teclea los objetivos y los valores reales de cada "
                   "semana. Escribe directo en las celdas y pica «Guardar».",
                   className="subtitulo"),

            html.Div(
                [
                    html.Div(
                        [
                            html.Label("Año", style={"fontWeight": "600",
                                                     "color": AZUL,
                                                     "display": "block",
                                                     "marginBottom": "4px"}),
                            dcc.Dropdown(
                                id="bsc-cap-anio",
                                options=[{"label": str(a), "value": a}
                                         for a in anios],
                                value=anio_val, clearable=False,
                                style={"width": "140px"}),
                        ],
                    ),
                    html.Div(
                        [
                            html.Label("Mes", style={"fontWeight": "600",
                                                     "color": AZUL,
                                                     "display": "block",
                                                     "marginBottom": "4px"}),
                            dcc.Dropdown(
                                id="bsc-cap-mes",
                                options=[{"label": n, "value": m}
                                         for m, n in MESES],
                                value=1, clearable=False,
                                style={"width": "180px"}),
                        ],
                    ),
                    html.Button("Guardar", id="bsc-cap-guardar", n_clicks=0,
                                className="btn btn-primary",
                                style={"height": "40px", "padding": "0 26px"}),
                ],
                style={"display": "flex", "gap": "20px", "marginBottom": "18px",
                       "alignItems": "flex-end", "flexWrap": "wrap"},
            ),

            html.Div(id="bsc-cap-msg",
                     style={"marginBottom": "12px", "fontWeight": "600"}),

            html.Div(id="bsc-cap-tabla-cont"),
        ]
    )


# Estilo de la celda Indicador según el tipo de fila:
#  - título (padre con hijos): azul negrita sobre crema
#  - principal suelto (nivel 0 capturable): azul negrita, sin sangría
#  - hijo (nivel 1): gris, indentado
_CELL_INDICADOR = {"function": (
    "params.data.es_titulo ? "
    "{fontWeight:'700', color:'#173C73', backgroundColor:'#F4F1E4'} : "
    "(params.data.nivel === 1 ? "
    "  {color:'#5A6472', paddingLeft:'26px'} : "
    "  {fontWeight:'700', color:'#173C73'})"
)}

# Las celdas editables (objetivo/semanas) se DESHABILITAN en las
# filas-título: no tienen dato propio, solo rotulan.
_EDITABLE = {"function": "!params.data.es_titulo"}

# Fondo tenue de las celdas editables solo en filas capturables.
_CELL_EDIT = {"function": (
    "params.data.es_titulo ? "
    "{backgroundColor:'#F4F1E4'} : {backgroundColor:'#FFFDF5'}"
)}


def _column_defs(sems):
    cols = [
        {"field": "indicador", "headerName": "Indicador", "minWidth": 260,
         "pinned": "left", "editable": False, "headerClass": "hdr-bsc",
         "cellStyle": _CELL_INDICADOR},
        {"field": "objetivo", "headerName": "Objetivo", "editable": _EDITABLE,
         "type": "numericColumn", "minWidth": 130, "headerClass": "hdr-bsc",
         "cellStyle": _CELL_EDIT},
    ]
    for s in sems:
        cols.append({
            "field": f"sem_{s['num']}", "headerName": s["label"],
            "editable": _EDITABLE, "type": "numericColumn", "minWidth": 100,
            "headerClass": "hdr-bsc", "cellStyle": _CELL_EDIT})
    return cols


def _filas(anio, mes):
    """Arma el rowData de captura recorriendo TODO el catálogo en
    orden. Los indicadores que se calculan por suma (padres) se
    incluyen como FILAS-TÍTULO (es_titulo=True, no editables); los
    capturables van debajo, indentados, con objetivo y semanas."""
    sems = S.semanas_del_mes(anio, mes)
    objetivos = datos.leer_objetivos(anio, mes)
    captura = datos.leer_captura(anio, mes)

    filas = []
    for ind in catalogo.indicadores():
        iid = ind["id"]
        # ¿es una fila-título? -> los padres que suman hijos y
        # cualquier indicador NO capturable de nivel 0.
        es_titulo = (not ind["capturable"])
        fila = {
            "id": iid,
            "indicador": ind["nombre"],
            "es_titulo": es_titulo,
            "nivel": ind["nivel"],
            "objetivo": None if es_titulo else objetivos.get(iid),
        }
        semvals = captura.get(iid, {})
        for s in sems:
            fila[f"sem_{s['num']}"] = None if es_titulo else semvals.get(s["num"])
        filas.append(fila)
    return filas, sems


def registrar_callbacks_bsc_captura(app):

    @app.callback(
        Output("bsc-cap-tabla-cont", "children"),
        Input("bsc-cap-anio", "value"),
        Input("bsc-cap-mes", "value"),
    )
    def _construir(anio, mes):
        if not anio or not mes:
            return html.Div("Selecciona año y mes.", style={"color": "#6C757D"})
        filas, sems = _filas(anio, mes)
        grid = dag.AgGrid(
            id="bsc-cap-grid",
            rowData=filas,
            columnDefs=_column_defs(sems),
            defaultColDef={"resizable": True, "sortable": False,
                           "filter": False, "flex": 1, "minWidth": 95},
            dashGridOptions={"animateRows": False, "rowHeight": 32,
                             "headerHeight": 40, "stopEditingWhenCellsLoseFocus": True,
                             "singleClickEdit": True},
            className="ag-theme-alpine",
            style=_estilo_grid("620px"),
        )
        return grid

    @app.callback(
        Output("bsc-cap-msg", "children"),
        Input("bsc-cap-guardar", "n_clicks"),
        State("bsc-cap-grid", "rowData"),
        State("bsc-cap-anio", "value"),
        State("bsc-cap-mes", "value"),
        prevent_initial_call=True,
    )
    def _guardar(n, rowdata, anio, mes):
        if not n or not rowdata or not anio or not mes:
            return no_update
        sems = S.semanas_del_mes(anio, mes)
        objetivos = {}
        valores = []   # (indicador, semana, valor)
        for fila in rowdata:
            iid = fila.get("id")
            if not iid or fila.get("es_titulo"):
                continue   # las filas-título no guardan nada
            objetivos[iid] = fila.get("objetivo")
            for s in sems:
                valores.append((iid, s["num"], fila.get(f"sem_{s['num']}")))
        try:
            datos.guardar_objetivos(anio, mes, objetivos)
            datos.guardar_captura(anio, mes, valores)
        except Exception as e:
            return html.Span(f"Error al guardar: {e}",
                             style={"color": "#C0392B"})
        return html.Span(
            f"✓ Guardado {_MES_NOMBRE.get(int(mes), mes)} {anio}.",
            style={"color": "#1E8449"})