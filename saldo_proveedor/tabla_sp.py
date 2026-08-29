"""
=========================================================
saldo_proveedor/tabla_sp.py
=========================================================
Matriz de Saldo Proveedor (un solo nivel: Proveedor), réplica
de la tabla dinámica "Saldo Prov" del Excel:
  Proveedor | Vencido >60 | Vencido 31-60 | Vencido 0-30 |
            | Vigente | Total Saldo prov
+ fila TOTAL GENERAL. Ordenada por total descendente.

Filtros: Año (maestro) + calendario Mes/Semana.
Lee de la caché del servidor (db.obtener_df).
"""

from dash import Input, Output, html, dcc
import dash_ag_grid as dag

import db

MODULO = "saldo_proveedor"
COL_PROV = "Proveedor"
COL_MES = "MES"
COL_SEMANA = "SEMANA"
COL_ANIO = "AÑO"

AZUL = "#173C73"
DORADO = "#D4AF37"

ALTO_FILA = 34
ALTO_ENCABEZADO = 38
ALTO_MAXIMO = 600

# columnas de aging (columna del df -> etiqueta), en el orden de la dinámica
AGING = [
    ("Vencido >60 días", "Vencido >60 días"),
    ("Vencido 31-60 días", "Vencido 31-60 días"),
    ("Vencido 0-30 días", "Vencido 0-30 días"),
    ("Vigente", "Vigente"),
]

FMT_MONEDA = {"function": "params.value == null ? '' : '$' + d3.format(',.2f')(params.value)"}


def _column_defs():
    defs = [
        {"field": "proveedor", "headerName": "Proveedor",
         "minWidth": 300, "pinned": "left", "filter": False, "sortable": True,
         "headerClass": "hdr-sp",
         "cellStyle": {"fontWeight": "600", "color": AZUL}},
    ]
    for campo, etiqueta in AGING:
        defs.append({
            "field": campo, "headerName": etiqueta,
            "type": "numericColumn", "valueFormatter": FMT_MONEDA,
            "minWidth": 140, "filter": False, "sortable": True,
            "headerClass": "hdr-sp",
        })
    defs.append({
        "field": "total", "headerName": "Total Saldo prov",
        "type": "numericColumn", "valueFormatter": FMT_MONEDA,
        "minWidth": 160, "pinned": "right", "filter": False, "sortable": True,
        "headerClass": "hdr-sp",
        "cellStyle": {"fontWeight": "700", "color": AZUL}},
    )
    return defs


def _estilo_grid(alto):
    return {
        "width": "100%", "height": alto,
        "--ag-font-size": "15px",
        "--ag-header-background-color": AZUL,
        "--ag-header-foreground-color": "#FFFFFF",
        "--ag-background-color": "#FFFFFF",
        "--ag-border-color": "#E7DBB0",
        "--ag-row-hover-color": "#E5DECB",
        "--ag-icon-color": "#FFFFFF",
    }


def _altura_dinamica(n):
    alto = ALTO_ENCABEZADO + (n * ALTO_FILA) + ALTO_FILA + 16
    return f"{min(alto, ALTO_MAXIMO)}px"


def crear_encabezado_periodo(anio_txt, semanas_texto):
    return html.Div(
        [
            html.Span("Año:  ",
                      style={"color": DORADO, "fontWeight": "bold", "marginLeft": "24px"}),
            html.Span(anio_txt,
                      style={"color": "#FFFFFF", "fontWeight": "bold", "marginRight": "32px"}),
            html.Span("Semana:  ", style={"color": DORADO, "fontWeight": "bold"}),
            html.Span(semanas_texto, style={"color": "#FFFFFF", "fontWeight": "bold"}),
        ],
        style={"backgroundColor": AZUL, "padding": "12px 16px",
               "borderRadius": "10px 10px 0 0", "display": "flex",
               "justifyContent": "flex-end", "flexWrap": "wrap", "fontSize": "15px"},
    )


def crear_layout_tabla_sp():
    return html.Div(
        [
            html.Div(
                dcc.Markdown(
                    """<style>
                    .hdr-sp, .hdr-sp .ag-header-cell-text { color:#FFFFFF !important; }
                    </style>""",
                    dangerously_allow_html=True,
                ),
                style={"display": "none"},
            ),
            html.Div(id="tabla-sp-cont"),
        ]
    )


def _filtrar(df, anio, semanas):
    if df is None:
        return df
    if anio:
        df = df[df[COL_ANIO] == int(anio)]
    # el MES ya no filtra; solo la SEMANA (única)
    if semanas:
        df = df[df[COL_SEMANA].isin(semanas)]
    return df


def _filas(df):
    """Una fila por proveedor (suma de aging), ordenada por total
    desc, + fila total general (para pinnedBottom)."""
    campos = [c for c, _ in AGING]
    filas = []
    for prov in df[COL_PROV].dropna().unique().tolist():
        sub = df[df[COL_PROV] == prov]
        fila = {"proveedor": str(prov)}
        total = 0.0
        for c in campos:
            val = float(sub[c].sum()) if c in sub.columns else 0.0
            fila[c] = val if val != 0 else None
            total += val
        fila["total"] = total if total != 0 else None
        filas.append(fila)
    filas.sort(key=lambda f: f.get("total") or 0, reverse=True)

    # total general
    tot = {"proveedor": "TOTAL GENERAL"}
    gran = 0.0
    for c in campos:
        val = float(df[c].sum()) if c in df.columns else 0.0
        tot[c] = val if val != 0 else None
        gran += val
    tot["total"] = gran if gran != 0 else None
    return filas, tot


def registrar_callbacks_sp(app):

    @app.callback(
        Output("tabla-sp-cont", "children"),
        Input("store-bd-sp", "data"),
        Input("dropdown-anio-sp", "value"),
        Input("store-semana-sp", "data"),
    )
    def construir(marca, anio, semanas):
        df = db.obtener_df(MODULO)
        if df is None:
            return html.Div("Aún no hay datos de Saldo Proveedor cargados.",
                            style={"color": "#6C757D"})
        try:
            df_f = _filtrar(df, anio, semanas)
            if df_f is None or len(df_f) == 0:
                return html.Div("Selecciona una semana para ver el saldo.",
                                style={"color": "#6C757D"})

            filas, total = _filas(df_f)
            semana_txt = str(sorted(semanas)[0]) if semanas else "—"
            anio_txt = str(anio) if anio else "—"

            grid = dag.AgGrid(
                id="tabla-sp-grid",
                rowData=filas,
                columnDefs=_column_defs(),
                getRowStyle={"function":
                    "params.node.rowPinned ? "
                    "{fontWeight:'700', color:'#173C73', backgroundColor:'#F4F1E4'} : {}"},
                defaultColDef={"flex": 1, "minWidth": 140, "sortable": True,
                               "filter": False, "resizable": True},
                dashGridOptions={"animateRows": False, "rowHeight": ALTO_FILA,
                                 "headerHeight": ALTO_ENCABEZADO,
                                 "pinnedBottomRowData": [total],
                                 "suppressCellFocus": True},
                className="ag-theme-alpine",
                style=_estilo_grid(_altura_dinamica(len(filas))),
            )
            return html.Div([
                crear_encabezado_periodo(anio_txt, semana_txt),
                grid,
            ])
        except Exception as e:
            return html.Div([html.H3("ERROR"), html.Pre(str(e))],
                            style={"color": "red"})