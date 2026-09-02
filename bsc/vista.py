"""
=========================================================
bsc/vista.py  —  MÓDULO BSC con PESTAÑAS
=========================================================
Un solo módulo (/bsc) con pestañas:
  - Mensual    (lectura, todos)
  - Anual      (lectura, todos)
  - Objetivos  (todos la VEN; solo admin la edita/guarda)
  - Captura    (solo admin)

Patrón igual a Inventario: los paneles están SIEMPRE montados y
solo se muestran/ocultan; así ningún callback queda huérfano. El
rol se lee de dcc.Store(id="store-sesion").

registrar_callbacks_bsc(app) engancha este contenedor, crea el
esquema y registra los callbacks de cada panel (mensual, anual,
objetivos y captura).
"""

from dash import Input, Output, State, html, dcc, no_update, ALL, ctx
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

_FMT_VALOR = {"function": (
    "params.value == null ? '' : "
    "(params.data.unidad === '$' ? '$' + d3.format(',.0f')(params.value) : "
    " params.data.unidad === 'Días' ? d3.format(',.0f')(params.value) + ' d' : "
    " d3.format(',.0f')(params.value)))"
)}
_FMT_PCT = {"function":
    "params.value == null ? '' : d3.format(',.1f')(params.value*100) + '%'"}

_CELL_SEMAFORO = {"function": (
    "({'verde':{color:'#2ecc71',fontSize:'18px',textAlign:'center'},"
    "  'amarillo':{color:'#f1c40f',fontSize:'18px',textAlign:'center'},"
    "  'rojo':{color:'#e74c3c',fontSize:'18px',textAlign:'center'},"
    "  'gris':{color:'#cfd6df',fontSize:'18px',textAlign:'center'}}"
    ")[params.data.color] || {textAlign:'center'}"
)}
_CELL_INDICADOR = {"function":
    "params.data.nivel === 1 ? "
    "{color:'#5A6472', paddingLeft:'26px'} : "
    "{fontWeight:'700', color:'#173C73'}"}

# % / $ sin color de semáforo (número simple, negrita azul)
_CELL_PCT_SEMAFORO = {"fontWeight": "700", "color": "#173C73"}


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


# =========================================================
# LAYOUT PRINCIPAL DEL MÓDULO (contenedor de pestañas)
# =========================================================

def crear_layout_bsc():
    """Contenedor con pestañas. Importa (perezoso) los paneles de
    cada pestaña para evitar ciclos de import."""
    from bsc.captura import crear_panel_captura_bsc
    from bsc.acumulado import crear_panel_acumulado_bsc

    return html.Div(
        [
            html.H1("BSC — Tablero de control", className="titulo"),

            # pestaña activa (fuente de verdad del cambio de panel)
            dcc.Store(id="bsc-tab-activa", data="mensual"),

            # barra de pestañas (se rellena por callback según el rol)
            html.Div(id="bsc-tabs-cont", style={"marginBottom": "18px"}),

            html.Div(id="bsc-panel-mensual", children=_panel_mensual()),

            html.Div(id="bsc-panel-anual",
                     children=crear_panel_acumulado_bsc(),
                     style={"display": "none"}),

            html.Div(id="bsc-panel-captura",
                     children=crear_panel_captura_bsc(),
                     style={"display": "none"}),
        ]
    )


def _tab_btn(texto, valor, activo):
    base = {
        "padding": "10px 22px", "border": "none", "cursor": "pointer",
        "fontWeight": "600", "fontSize": "15px", "borderRadius": "10px",
        "marginRight": "8px",
    }
    if activo:
        base.update({"background": AZUL, "color": "#FFFFFF"})
    else:
        base.update({"background": "#EEF2F7", "color": "#5A6472"})
    return html.Button(texto, id={"type": "bsc-tab", "tab": valor},
                       n_clicks=0, style=base)


def _panel_mensual():
    anios = datos.anios_con_bsc()
    anio_val = anios[0] if anios else None
    return html.Div([
        html.P("Objetivo vs. real por semana, con semáforo de avance.",
               className="subtitulo"),
        html.Div(
            [
                html.Div([
                    html.Label("Año", style={"fontWeight": "600", "color": AZUL,
                                             "display": "block",
                                             "marginBottom": "4px"}),
                    dcc.Dropdown(id="bsc-anio",
                                 options=[{"label": str(a), "value": a}
                                          for a in anios],
                                 value=anio_val, clearable=False,
                                 style={"width": "140px"}),
                ]),
                html.Div([
                    html.Label("Mes", style={"fontWeight": "600", "color": AZUL,
                                             "display": "block",
                                             "marginBottom": "4px"}),
                    dcc.Dropdown(id="bsc-mes", options=[], value=None,
                                 clearable=False, style={"width": "180px"}),
                ]),
            ],
            style={"display": "flex", "gap": "20px", "marginBottom": "18px",
                   "alignItems": "flex-end", "flexWrap": "wrap"},
        ),
        html.Div(id="bsc-info",
                 style={"marginBottom": "14px", "fontSize": "13px",
                        "color": "#6C757D", "fontStyle": "italic"}),
        html.Div(id="bsc-tabla-cont"),
    ])


def _column_defs(sems):
    # Orden como el Excel: Indicador | Objetivo | Acumulado | %/$ |
    # Deber ser | [semanas...]
    cols = [
        {"field": "indicador", "headerName": "Indicador", "minWidth": 240,
         "pinned": "left", "sortable": False, "filter": False,
         "headerClass": "hdr-bsc", "cellStyle": _CELL_INDICADOR},
        {"field": "objetivo", "headerName": "Objetivo", "type": "numericColumn",
         "valueFormatter": _FMT_VALOR, "minWidth": 115, "pinned": "left",
         "sortable": False, "filter": False, "headerClass": "hdr-bsc"},
        {"field": "acumulado", "headerName": "Acumulado",
         "type": "numericColumn", "valueFormatter": _FMT_VALOR,
         "minWidth": 120, "pinned": "left", "sortable": False, "filter": False,
         "headerClass": "hdr-bsc",
         "cellStyle": {"fontWeight": "700", "color": AZUL}},
        # % / $ con la CELDA coloreada según cumplimiento (semáforo)
        {"field": "pct", "headerName": "% / $", "type": "numericColumn",
         "valueFormatter": _FMT_PCT, "minWidth": 95, "pinned": "left",
         "sortable": False, "filter": False, "headerClass": "hdr-bsc",
         "cellStyle": _CELL_PCT_SEMAFORO},
        {"field": "deber_ser", "headerName": "Deber ser",
         "type": "numericColumn", "valueFormatter": _FMT_PCT, "minWidth": 95,
         "pinned": "left", "sortable": False, "filter": False,
         "headerClass": "hdr-bsc", "cellStyle": {"color": "#8A94A6"}},
    ]
    # semanas: el real suelto de cada semana
    for s in sems:
        cols.append({
            "field": f"sem_{s['num']}", "headerName": s["label"],
            "type": "numericColumn", "valueFormatter": _FMT_VALOR,
            "minWidth": 100, "sortable": False, "filter": False,
            "headerClass": "hdr-bsc",
            "cellStyle": {"color": "#3B4658", "backgroundColor": "#F5F8FC"}})
    return cols


def registrar_callbacks_bsc(app):
    try:
        datos.inicializar_esquema_bsc()
    except Exception as e:
        print("[BSC] No se pudo inicializar esquema:", e)

    # 1) al picar un botón de pestaña -> actualizar la pestaña activa
    @app.callback(
        Output("bsc-tab-activa", "data"),
        Input({"type": "bsc-tab", "tab": ALL}, "n_clicks"),
        prevent_initial_call=True,
    )
    def _cambiar_tab(_clicks):
        tid = ctx.triggered_id
        if isinstance(tid, dict) and tid.get("tab"):
            return tid["tab"]
        return no_update

    # 2) pintar la barra de pestañas según rol y pestaña activa
    @app.callback(
        Output("bsc-tabs-cont", "children"),
        Input("bsc-tab-activa", "data"),
        Input("store-sesion", "data"),
    )
    def _barra(activa, sesion):
        es_admin = bool(sesion and sesion.get("rol") == "admin")
        activa = activa or "mensual"
        tabs = [("Mensual", "mensual"), ("Anual", "anual")]
        if es_admin:
            tabs.append(("Captura", "captura"))
        return html.Div([_tab_btn(t, v, v == activa) for t, v in tabs])

    # 3) mostrar/ocultar paneles según la pestaña activa
    @app.callback(
        Output("bsc-panel-mensual", "style"),
        Output("bsc-panel-anual", "style"),
        Output("bsc-panel-captura", "style"),
        Input("bsc-tab-activa", "data"),
    )
    def _mostrar(activa):
        activa = activa or "mensual"
        ocul = {"display": "none"}
        vis = {"display": "block"}
        return (vis if activa == "mensual" else ocul,
                vis if activa == "anual" else ocul,
                vis if activa == "captura" else ocul)

    # meses disponibles (panel mensual)
    @app.callback(
        Output("bsc-mes", "options"),
        Output("bsc-mes", "value"),
        Input("bsc-anio", "value"),
    )
    def _meses(anio):
        if not anio:
            return [{"label": n, "value": m} for m, n in MESES], 1
        meses = datos.meses_con_bsc(anio)
        if not meses:
            return [{"label": n, "value": m} for m, n in MESES], 1
        return ([{"label": _MES_NOMBRE.get(m, str(m)), "value": m}
                 for m in meses], meses[-1])

    # construir tabla mensual
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
        for f in filas:
            f["semaforo"] = "●"
        grid = dag.AgGrid(
            id="bsc-grid", rowData=filas, columnDefs=_column_defs(sems),
            defaultColDef={"resizable": True, "sortable": False,
                           "filter": False, "flex": 1, "minWidth": 90},
            dashGridOptions={"animateRows": False, "rowHeight": 32,
                             "headerHeight": 40, "suppressCellFocus": True},
            className="ag-theme-alpine", style=_estilo_grid("640px"),
        )
        info = (f"{_MES_NOMBRE.get(int(mes), mes)} {anio} · "
                f"deber ser a hoy: {ds*100:.0f}%")
        return grid, info

    # registrar callbacks de los otros paneles
    from bsc.captura import registrar_callbacks_bsc_captura
    registrar_callbacks_bsc_captura(app)
    from bsc.acumulado import registrar_callbacks_bsc_acumulado
    registrar_callbacks_bsc_acumulado(app)