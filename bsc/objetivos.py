"""
=========================================================
bsc/objetivos.py  —  CAPTURA de OBJETIVOS anuales (/bsc-objetivos)
=========================================================
Pantalla de admin para planear el año: una tabla editable con
una fila por indicador y columnas [Objetivo anual | Ene..Dic].
Los objetivos mensuales alimentan la vista mensual (BSC); el
objetivo anual (mes=0) alimenta la vista Acumulado.

Los padres (Venta, Utilidad…) van como filas-título; sus
objetivos se calculan sumando a los hijos, no se teclean aquí.
"""

from dash import Input, Output, State, html, dcc, no_update
import dash_ag_grid as dag

from bsc import catalogo, datos

AZUL = "#173C73"

MESES_COL = [(1, "Ene"), (2, "Feb"), (3, "Mar"), (4, "Abr"),
             (5, "May"), (6, "Jun"), (7, "Jul"), (8, "Ago"),
             (9, "Sep"), (10, "Oct"), (11, "Nov"), (12, "Dic")]

_CELL_INDICADOR = {"function": (
    "params.data.es_titulo ? "
    "{fontWeight:'700', color:'#173C73', backgroundColor:'#F4F1E4'} : "
    "(params.data.nivel === 1 ? "
    "  {color:'#5A6472', paddingLeft:'26px'} : "
    "  {fontWeight:'700', color:'#173C73'})"
)}
_EDITABLE = {"function": "!params.data.es_titulo"}
_CELL_EDIT = {"function": (
    "params.data.es_titulo ? "
    "{backgroundColor:'#EFF2F7', fontWeight:'700', color:'#173C73'} : "
    "{backgroundColor:'#FFFDF5'}"
)}
# Objetivo anual: SIEMPRE calculado -> fondo gris claro, en azul,
# para que se note que no se teclea.
_CELL_ANUAL_CALC = {"function": (
    "{backgroundColor:'#EFF2F7', fontWeight:'700', color:'#173C73'}"
)}


def _estilo_grid(alto):
    return {
        "width": "100%", "height": alto,
        "--ag-font-size": "13px",
        "--ag-header-background-color": AZUL,
        "--ag-header-foreground-color": "#FFFFFF",
        "--ag-background-color": "#FFFFFF",
        "--ag-border-color": "#E7DBB0",
        "--ag-row-hover-color": "#EEF3FA",
    }


def crear_panel_objetivos_bsc():
    anios_g = datos.anios_con_bsc()
    anios = sorted(set(list(range(2025, 2036)) + anios_g), reverse=True)
    anio_val = anios_g[0] if anios_g else 2026
    return html.Div(
        [
            html.P("Planea el año: objetivo anual y su desglose por mes. "
                   "(Solo el administrador puede editar y guardar.)",
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
                                id="bsc-obj-anio",
                                options=[{"label": str(a), "value": a}
                                         for a in anios],
                                value=anio_val, clearable=False,
                                style={"width": "140px"}),
                        ],
                    ),
                    # el botón Guardar se muestra/oculta por rol (callback)
                    html.Div(id="bsc-obj-guardar-cont"),
                ],
                style={"display": "flex", "gap": "20px", "marginBottom": "18px",
                       "alignItems": "flex-end", "flexWrap": "wrap"},
            ),
            html.Div(id="bsc-obj-msg",
                     style={"marginBottom": "12px", "fontWeight": "600"}),
            html.Div(id="bsc-obj-tabla-cont"),
        ]
    )


def _column_defs(editable):
    edit = _EDITABLE if editable else False
    cols = [
        {"field": "indicador", "headerName": "Indicador", "minWidth": 240,
         "pinned": "left", "editable": False, "headerClass": "hdr-bsc",
         "cellStyle": _CELL_INDICADOR},
        # Objetivo anual: SIEMPRE calculado (nunca se teclea)
        {"field": "anual", "headerName": "Objetivo anual", "editable": False,
         "type": "numericColumn", "minWidth": 140, "pinned": "left",
         "headerClass": "hdr-bsc", "cellStyle": _CELL_ANUAL_CALC},
    ]
    for m, nombre in MESES_COL:
        cols.append({
            "field": f"m_{m}", "headerName": nombre, "editable": edit,
            "type": "numericColumn", "minWidth": 90, "headerClass": "hdr-bsc",
            "cellStyle": _CELL_EDIT})
    return cols


def _filas(anio):
    from bsc.logica import formular_objetivos
    porm = datos.leer_objetivos_anio(anio)      # {mes: {ind: val}}
    porm = formular_objetivos(porm)             # rellena anual + padres
    filas = []
    for ind in catalogo.indicadores():
        iid = ind["id"]
        es_titulo = not ind["capturable"]
        fila = {"id": iid, "indicador": ind["nombre"],
                "es_titulo": es_titulo, "nivel": ind["nivel"],
                "anual": porm.get(0, {}).get(iid)}
        for m, _ in MESES_COL:
            fila[f"m_{m}"] = porm.get(m, {}).get(iid)
        filas.append(fila)
    return filas


def registrar_callbacks_bsc_objetivos(app):

    # botón Guardar: solo para admin
    @app.callback(
        Output("bsc-obj-guardar-cont", "children"),
        Input("store-sesion", "data"),
    )
    def _boton(sesion):
        if sesion and sesion.get("rol") == "admin":
            return html.Button("Guardar", id="bsc-obj-guardar", n_clicks=0,
                               className="btn btn-primary",
                               style={"height": "40px", "padding": "0 26px"})
        # placeholder oculto: el botón debe EXISTIR para que su callback
        # quede conectado, aunque no se vea para consulta.
        return html.Button("Guardar", id="bsc-obj-guardar", n_clicks=0,
                           style={"display": "none"})

    # construir la tabla (editable solo si admin)
    @app.callback(
        Output("bsc-obj-tabla-cont", "children"),
        Input("bsc-obj-anio", "value"),
        Input("store-sesion", "data"),
    )
    def _construir(anio, sesion):
        if not anio:
            return html.Div("Selecciona un año.", style={"color": "#6C757D"})
        editable = bool(sesion and sesion.get("rol") == "admin")
        grid = dag.AgGrid(
            id="bsc-obj-grid",
            rowData=_filas(anio),
            columnDefs=_column_defs(editable),
            defaultColDef={"resizable": True, "sortable": False,
                           "filter": False, "flex": 1, "minWidth": 85},
            dashGridOptions={"animateRows": False, "rowHeight": 30,
                             "headerHeight": 40, "singleClickEdit": True,
                             "stopEditingWhenCellsLoseFocus": True},
            className="ag-theme-alpine",
            style=_estilo_grid("640px"),
        )
        return grid

    @app.callback(
        Output("bsc-obj-msg", "children"),
        Input("bsc-obj-guardar", "n_clicks"),
        State("bsc-obj-grid", "rowData"),
        State("bsc-obj-anio", "value"),
        State("store-sesion", "data"),
        prevent_initial_call=True,
    )
    def _guardar(n, rowdata, anio, sesion):
        if not n or not rowdata or not anio:
            return no_update
        # candado de servidor: aunque alguien fuerce el clic, solo
        # admin puede escribir.
        if not (sesion and sesion.get("rol") == "admin"):
            return html.Span("No tienes permiso para guardar objetivos.",
                             style={"color": "#C0392B"})
        # 1) recoger SOLO lo tecleado (meses de hijos y principales)
        from bsc.logica import formular_objetivos
        tecleado = {}   # {mes: {id: val}}
        for fila in rowdata:
            iid = fila.get("id")
            if not iid or fila.get("es_titulo"):
                continue
            for m, _ in MESES_COL:
                v = fila.get(f"m_{m}")
                if v not in (None, ""):
                    tecleado.setdefault(m, {})[iid] = v

        # 2) formular: rellena anuales (mes 0) y padres calculados
        completo = formular_objetivos(tecleado)

        # 3) aplanar a lista (mes, id, valor) para guardar TODO
        valores = []
        for m in range(0, 13):
            for iid, v in completo.get(m, {}).items():
                valores.append((m, iid, v))
        try:
            datos.guardar_objetivos_anio(anio, valores, reemplazar_anio=True)
        except Exception as e:
            return html.Span(f"Error al guardar: {e}",
                             style={"color": "#C0392B"})
        return html.Span(f"✓ Objetivos {anio} guardados.",
                         style={"color": "#1E8449"})