"""
=========================================================
inventario_historico_captura.py  —  CARGA DEL HISTÓRICO
MENSUAL DE INVENTARIO (solo admin)
=========================================================
Sección que se coloca dentro de la página "Carga de datos"
(abajo, aparte, igual que la captura de Proyección).

El admin elige AÑO y MES, sube los MISMOS 2 archivos del
inventario actual (valuación + quants) y una fecha de corte;
se procesa con la MISMA lógica del inventario (leer_archivo) y
se guarda como foto de ese mes en la tabla inventario_historico.
Si el año/mes ya existía, se REEMPLAZA.

IDs con prefijo "invh-cap-" para no chocar con los callbacks de
patrón de carga.py ni con la pestaña de consulta (invh-*).
"""

from datetime import date

from dash import Input, Output, State, html, dcc
import dash_bootstrap_components as dbc

import db
from inventario.procesamiento import leer_archivo as leer_inventario

AZUL = "#173C73"
DORADO = "#D4AF37"

ANIOS = list(range(2025, 2036))   # 2025 .. 2035

MESES = [
    (1, "Enero"), (2, "Febrero"), (3, "Marzo"), (4, "Abril"),
    (5, "Mayo"), (6, "Junio"), (7, "Julio"), (8, "Agosto"),
    (9, "Septiembre"), (10, "Octubre"), (11, "Noviembre"), (12, "Diciembre"),
]


def _bloque_upload(id_upload, id_nombre, label):
    """Una zona de subida (botón + nombre del archivo elegido),
    con el mismo look de las tarjetas de carga."""
    return html.Div(
        [
            html.H6(label, style={"color": AZUL, "marginBottom": "6px"}),
            dcc.Upload(
                id=id_upload,
                multiple=False,
                children=html.Button(
                    [html.I(className="fas fa-folder-open me-2"),
                     f"Seleccionar {label}"],
                    style={"width": "100%", "padding": "10px",
                           "borderRadius": "8px",
                           "border": f"1px solid {AZUL}",
                           "backgroundColor": "white", "color": AZUL,
                           "cursor": "pointer"},
                ),
            ),
            html.Div(
                id=id_nombre,
                children="Ningún archivo seleccionado.",
                style={"fontSize": "13px", "color": "#6C757D",
                       "marginTop": "4px", "marginBottom": "12px"},
            ),
        ]
    )


def crear_seccion_historico_inventario():
    anio_actual = date.today().year if date.today().year in ANIOS else ANIOS[0]

    return html.Div(
        [
            html.Hr(style={"margin": "40px 0 24px"}),
            html.H2("Histórico de inventario (mensual)",
                    style={"color": AZUL, "fontWeight": "700"}),
            html.P("Sube una foto mensual del inventario para dejar registro "
                   "de cómo va cambiando. Usa los mismos 2 archivos del "
                   "inventario semanal. Si el año/mes ya existe, se reemplaza. "
                   "Esto NO afecta al inventario actual.",
                   style={"color": "#6C757D", "marginBottom": "20px"}),

            # Año / Mes
            html.Div(
                [
                    html.Div(
                        [
                            html.Label("Año", style={"fontWeight": "600",
                                                     "color": AZUL,
                                                     "display": "block",
                                                     "marginBottom": "4px"}),
                            dcc.Dropdown(
                                id="invh-cap-anio",
                                options=[{"label": str(a), "value": a}
                                         for a in ANIOS],
                                value=anio_actual, clearable=False,
                                style={"width": "140px"},
                            ),
                        ],
                    ),
                    html.Div(
                        [
                            html.Label("Mes", style={"fontWeight": "600",
                                                     "color": AZUL,
                                                     "display": "block",
                                                     "marginBottom": "4px"}),
                            dcc.Dropdown(
                                id="invh-cap-mes",
                                options=[{"label": n, "value": m}
                                         for m, n in MESES],
                                value=date.today().month, clearable=False,
                                style={"width": "180px"},
                            ),
                        ],
                    ),
                ],
                style={"display": "flex", "gap": "20px", "marginBottom": "20px",
                       "alignItems": "flex-end", "flexWrap": "wrap"},
            ),

            dbc.Card(
                dbc.CardBody(
                    [
                        _bloque_upload("invh-cap-up-val", "invh-cap-nom-val",
                                       "BD Valuación (fechas)"),
                        _bloque_upload("invh-cap-up-quants", "invh-cap-nom-quants",
                                       "BD Quants (ubicaciones)"),

                        html.Div(
                            [
                                html.H6("Fecha de corte",
                                        style={"color": AZUL,
                                               "marginBottom": "6px"}),
                                html.P("Fecha base para calcular los días en "
                                       "almacén de esta foto.",
                                       style={"fontSize": "12px",
                                              "color": "#6C757D",
                                              "marginBottom": "8px"}),
                                dcc.DatePickerSingle(
                                    id="invh-cap-fecha",
                                    display_format="DD/MM/YYYY",
                                    placeholder="Selecciona la fecha",
                                    date=date.today().isoformat(),
                                    style={"marginBottom": "14px"},
                                ),
                            ]
                        ),

                        html.Button(
                            [html.I(className="fas fa-floppy-disk me-2"),
                             "Guardar histórico"],
                            id="invh-cap-btn", n_clicks=0,
                            style={"backgroundColor": AZUL, "color": "white",
                                   "border": "none", "padding": "12px 22px",
                                   "borderRadius": "8px", "fontWeight": "600",
                                   "cursor": "pointer", "width": "100%"},
                        ),
                        html.Div(id="invh-cap-estado",
                                 style={"marginTop": "14px",
                                        "minHeight": "24px"}),
                    ]
                ),
                className="card-premium",
                style={"maxWidth": "620px", "borderTop": f"4px solid {DORADO}"},
            ),
        ]
    )


def registrar_callbacks_historico_captura(app):

    # nombre del archivo de valuación
    @app.callback(
        Output("invh-cap-nom-val", "children"),
        Input("invh-cap-up-val", "filename"),
    )
    def _nombre_val(nombre):
        return ("✓ " + nombre) if nombre else "Ningún archivo seleccionado."

    # nombre del archivo de quants
    @app.callback(
        Output("invh-cap-nom-quants", "children"),
        Input("invh-cap-up-quants", "filename"),
    )
    def _nombre_quants(nombre):
        return ("✓ " + nombre) if nombre else "Ningún archivo seleccionado."

    # procesar y guardar la foto del mes
    @app.callback(
        Output("invh-cap-estado", "children"),
        Input("invh-cap-btn", "n_clicks"),
        State("invh-cap-anio", "value"),
        State("invh-cap-mes", "value"),
        State("invh-cap-up-val", "contents"),
        State("invh-cap-up-quants", "contents"),
        State("invh-cap-fecha", "date"),
        State("store-sesion", "data"),
        prevent_initial_call=True,
    )
    def _guardar(n, anio, mes, cont_val, cont_quants, fecha, sesion):
        rojo = {"color": "#DC3545"}

        if not sesion or sesion.get("rol") != "admin":
            return html.Div("Solo un administrador puede cargar datos.",
                            style=rojo)
        if not anio or not mes:
            return html.Div("Selecciona año y mes.", style=rojo)

        faltan = []
        if not cont_val:
            faltan.append("BD Valuación")
        if not cont_quants:
            faltan.append("BD Quants")
        if faltan:
            return html.Div("Falta seleccionar: " + ", ".join(faltan),
                            style=rojo)
        if not fecha:
            return html.Div("Selecciona la fecha de corte antes de guardar.",
                            style=rojo)

        try:
            df = leer_inventario(cont_val, cont_quants, fecha_corte=fecha)
            admin = sesion.get("usuario", "admin")
            db.guardar_inventario_historico(anio, mes, df,
                                            admin=admin, fecha_corte=fecha)
            return html.Div(
                [html.I(className="fas fa-circle-check me-2"),
                 f"Histórico guardado para {int(mes):02d}/{anio}: "
                 f"{len(df):,} registros (fecha de corte: {fecha})."],
                style={"color": "#198754", "fontWeight": "600"})
        except Exception as e:
            return html.Div(["Error al procesar: ", html.Pre(str(e))],
                            style=rojo)