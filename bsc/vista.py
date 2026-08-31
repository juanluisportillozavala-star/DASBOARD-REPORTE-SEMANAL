"""
=========================================================
bsc/vista.py  —  VISTA del BSC (tabla con semáforo)
=========================================================
Pantalla de solo lectura (/bsc): selector de año/mes y una tabla
AG Grid agrupada por área (dueño), con columnas dinámicas por
semana, acumulado, %, deber ser y semáforo de color.

Estilo alineado a los demás módulos: encabezado azul, fila total
crema/azul, clase hdr-bsc para encabezados blancos.

registrar_callbacks_bsc(app) engancha ESTA vista y también la
captura (bsc/captura.py) y crea el esquema si falta.
"""

from dash import Input, Output, html, dcc, no_update
import dash_ag_grid as dag

from bsc import catalogo, logica, datos
from bsc import semanas as S

AZUL = "#173C73"
DORADO = "#D4AF37"

MESES = [(1, "Enero"), (2, "Febrero"), (3, "Marzo"), (4, "Abril"),
         (5, "Mayo"), (6, "Junio"), (7, "Julio"), (8, "Agosto"),
         (9, "Septiembre"), (10, "Octubre"), (11, "Noviembre"),
         (12, "Diciembre")]
_MES_NOMBRE = dict(MESES)

# formateadores JS (según la unidad de cada fila)
_FMT_VALOR = {"function": (
    "params.value == null ? '' : "
    "(params.data.unidad === '$' ? '$' + d3.format(',.0f')(params.value) : "
    " params.data.unidad === 'Días' ? d3.format(',.0f')(params.value) + ' d' : "
    " d3.format(',.0f')(params.value)))"
)}
_FMT_PCT = {"function":
    "params.value == null ? '' : d3.format(',.1f')(params.value*100) + '%'"}

# color del punto de semáforo según params.data.color
_CELL_SEMAFORO = {"function": (
    "({'verde':{color:'#2ecc71',fontSize:'18px',textAlign:'center'},"
    "  'amarillo':{color:'#f1c40f',fontSize:'18px',textAlign:'center'},"
    "  'rojo':{color:'#e74c3c',fontSize:'18px',textAlign:'center'},"
    "  'gris':{color:'#cfd6df',fontSize:'18px',textAlign:'center'}}"
    ")[params.data.color] || {textAlign:'center'}"
)}

# indicadores principales en negrita azul; hijos indentados en gris
_CELL_INDICADOR = {"function":
    "params.data.nivel === 1 ? "
    "{color:'#5A6472', paddingLeft:'26px'} : "
    "{fontWeight:'700', color:'#173C73'}"}


def _estilo_grid(alto):
    return {
        "width": "100%", "height": alto,
        "--ag-font-size": "14px",
        "--ag-header-background-color": AZUL,
        "--ag-header-foreground-color": "#FFFFFF",
        "--ag-background-color": "#FFFFFF",
        "--ag-border-color": "#E7DBB0",
        "--ag-row-hover-color": "#E5DECB",
        "--ag-icon-color": "#FFFFFF",
    }


def crear_layout_bsc():
    anios = datos.anios_con_bsc()
    anio_val = anios[0] if anios else None
    return html.Div(
        [
            html.H1("BSC — Tablero de control", className="titulo"),
            html.P("Objetivo vs. real por semana, con semáforo de avance.",
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
                                id="bsc-anio",
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
                            dcc.Dropdown(id="bsc-mes", options=[], value=None,
                                         clearable=False,
                                         style={"width": "180px"}),
                        ],
                    ),
                ],
                style={"display": "flex", "gap": "20px", "marginBottom": "18px",
                       "alignItems": "flex-end", "flexWrap": "wrap"},
            ),

            html.Div(id="bsc-info",
                     style={"marginBottom": "14px", "fontSize": "13px",
                            "color": "#6C757D", "fontStyle": "italic"}),

            html.Div(id="bsc-tabla-cont"),
        ]
    )


def _column_defs(sems):
    """Columnas: Área | Indicador | Objetivo | [semanas…] |
    Acumulado | % | Deber ser | Semáforo."""
    cols = [
        {"field": "indicador", "headerName": "Indicador", "minWidth": 260,
         "pinned": "left", "sortable": False, "filter": False,
         "headerClass": "hdr-bsc", "cellStyle": _CELL_INDICADOR},
        {"field": "objetivo", "headerName": "Objetivo", "type": "numericColumn",
         "valueFormatter": _FMT_VALOR, "minWidth": 120, "sortable": False,
         "filter": False, "headerClass": "hdr-bsc"},
    ]
    for s in sems:
        cols.append({
            "field": f"sem_{s['num']}", "headerName": s["label"],
            "type": "numericColumn", "valueFormatter": _FMT_VALOR,
            "minWidth": 95, "sortable": False, "filter": False,
            "headerClass": "hdr-bsc",
            "cellStyle": {"color": "#5A6472"}})
    cols += [
        {"field": "acumulado", "headerName": "Acumulado",
         "type": "numericColumn", "valueFormatter": _FMT_VALOR,
         "minWidth": 130, "sortable": False, "filter": False,
         "headerClass": "hdr-bsc",
         "cellStyle": {"fontWeight": "700", "color": AZUL}},
        {"field": "pct", "headerName": "% avance", "type": "numericColumn",
         "valueFormatter": _FMT_PCT, "minWidth": 100, "sortable": False,
         "filter": False, "headerClass": "hdr-bsc"},
        {"field": "deber_ser", "headerName": "Deber ser",
         "type": "numericColumn", "valueFormatter": _FMT_PCT, "minWidth": 100,
         "sortable": False, "filter": False, "headerClass": "hdr-bsc",
         "cellStyle": {"color": "#8A94A6"}},
        {"field": "semaforo", "headerName": "", "minWidth": 60,
         "maxWidth": 70, "pinned": "right", "sortable": False,
         "filter": False, "headerClass": "hdr-bsc",
         "cellStyle": _CELL_SEMAFORO},
    ]
    return cols


def registrar_callbacks_bsc(app):
    # crea el esquema una vez al arrancar (idempotente)
    try:
        datos.inicializar_esquema_bsc()
    except Exception as e:
        print("[BSC] No se pudo inicializar esquema:", e)

    # meses disponibles al cambiar el año (o al cargar)
    @app.callback(
        Output("bsc-mes", "options"),
        Output("bsc-mes", "value"),
        Input("bsc-anio", "value"),
    )
    def _meses(anio):
        if not anio:
            # sin datos aún: ofrecer los 12 meses para no dejar vacío
            return [{"label": n, "value": m} for m, n in MESES], 1
        meses = datos.meses_con_bsc(anio)
        if not meses:
            return [{"label": n, "value": m} for m, n in MESES], 1
        opciones = [{"label": _MES_NOMBRE.get(m, str(m)), "value": m}
                    for m in meses]
        return opciones, meses[-1]

    # construir tabla al cambiar año/mes
    @app.callback(
        Output("bsc-tabla-cont", "children"),
        Output("bsc-info", "children"),
        Input("bsc-anio", "value"),
        Input("bsc-mes", "value"),
    )
    def _tabla(anio, mes):
        if not anio or not mes:
            return html.Div("Selecciona un año y un mes.",
                            style={"color": "#6C757D"}), ""

        objetivos = datos.leer_objetivos(anio, mes)
        captura = datos.leer_captura(anio, mes)
        filas, sems, ds = logica.construir_bsc(anio, mes, objetivos, captura)

        # símbolo de semáforo por fila
        for f in filas:
            f["semaforo"] = "●"

        grid = dag.AgGrid(
            id="bsc-grid",
            rowData=filas,
            columnDefs=_column_defs(sems),
            defaultColDef={"resizable": True, "sortable": False,
                           "filter": False, "flex": 1, "minWidth": 90},
            dashGridOptions={"animateRows": False, "rowHeight": 32,
                             "headerHeight": 40, "suppressCellFocus": True},
            className="ag-theme-alpine",
            style=_estilo_grid("640px"),
        )
        info = (f"{_MES_NOMBRE.get(int(mes), mes)} {anio} · "
                f"deber ser a hoy: {ds*100:.0f}%")
        return grid, info

    # enganchar los callbacks de captura
    from bsc.captura import registrar_callbacks_bsc_captura
    registrar_callbacks_bsc_captura(app)