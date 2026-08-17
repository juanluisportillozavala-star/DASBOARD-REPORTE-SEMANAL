"""
=========================================================
proyeccion_captura.py  —  CAPTURA DE PROYECCIONES (admin)
=========================================================
VERSIÓN 2 — edición en pantalla (store temporal).

La lista de productos y sus cantidades se editan EN PANTALLA
(en un store temporal del navegador). Agregar/quitar NO tocan
la base: solo cambian lo que se ve. El botón GUARDAR es el
único que escribe en la base de datos.

Flujo:
  • Al elegir año/mes: se carga en el store la proyección
    guardada de ese mes; si el mes está vacío, se cargan los
    16 productos predeterminados (con cantidad 0).
  • Agregar producto  -> se añade al store (no a la base).
  • Quitar producto   -> se saca del store (no de la base).
  • Escribir cantidad -> se guarda en el store al vuelo.
  • GUARDAR           -> escribe el store completo en la base.

La lista POR MES: guardar deja el mes EXACTAMENTE con lo que
haya en el store en ese momento.
"""

from datetime import date

from dash import Input, Output, State, html, dcc, no_update, ALL, ctx
import dash_bootstrap_components as dbc

import db

AZUL = "#173C73"
DORADO = "#D4AF37"

VARIOS = "VARIOS"   # grupo especial: meta editable, siempre al final

ANIOS = list(range(2025, 2036))   # 2025 .. 2035

MESES = [
    (1, "Enero"), (2, "Febrero"), (3, "Marzo"), (4, "Abril"),
    (5, "Mayo"), (6, "Junio"), (7, "Julio"), (8, "Agosto"),
    (9, "Septiembre"), (10, "Octubre"), (11, "Noviembre"), (12, "Diciembre"),
]


def _fila_producto(nombre, valor, fija=False):
    """Una fila: nombre + input de cantidad + botón quitar.
    Si fija=True (caso VARIOS), NO lleva botón de quitar y el
    nombre va en cursiva/gris."""
    elementos = [
        html.Span(nombre,
                  style={"flex": "1",
                         "color": "#6C757D" if fija else AZUL,
                         "fontWeight": "500",
                         "fontStyle": "italic" if fija else "normal"}),
        dcc.Input(
            id={"type": "proy-cant", "producto": nombre},
            type="number", min=0, step="any",
            value=valor if valor not in (None, 0) else None,
            placeholder="0",
            style={"width": "140px", "padding": "6px 8px",
                   "borderRadius": "6px", "border": "1px solid #CBD5E1"},
        ),
    ]
    if not fija:
        elementos.append(
            html.Button(
                html.I(className="fas fa-trash"),
                id={"type": "proy-quitar", "producto": nombre},
                n_clicks=0, title="Quitar de este mes",
                style={"backgroundColor": "transparent", "border": "none",
                       "color": "#C0392B", "cursor": "pointer",
                       "marginLeft": "10px"},
            )
        )
    else:
        # espacio para alinear con las filas que sí tienen botón
        elementos.append(html.Span(style={"width": "34px",
                                           "marginLeft": "10px"}))
    return html.Div(
        elementos,
        style={"display": "flex", "alignItems": "center",
               "justifyContent": "space-between", "padding": "6px 0",
               "borderBottom": "1px solid #EEF2F7",
               "backgroundColor": "#FAFAF5" if fija else "transparent"},
    )


def _render_tabla(lista):
    """lista: [{'producto': nombre, 'cantidad': valor}, ...]
    VARIOS se muestra SIEMPRE al final como fila fija (su meta es
    editable pero no se puede quitar)."""
    # separar VARIOS (si viene en la lista) del resto
    normales = [x for x in (lista or []) if x["producto"].strip().upper() != VARIOS]
    varios = next((x for x in (lista or [])
                   if x["producto"].strip().upper() == VARIOS), None)
    varios_val = varios.get("cantidad") if varios else None

    filas = [_fila_producto(x["producto"], x.get("cantidad")) for x in normales]
    # VARIOS siempre al final, fijo
    filas.append(_fila_producto(VARIOS, varios_val, fija=True))
    return html.Div(filas)


def crear_seccion_proyeccion():
    anio_actual = date.today().year if date.today().year in ANIOS else ANIOS[0]

    return html.Div(
        [
            # store con la lista EN EDICIÓN (no tocada la base hasta Guardar)
            dcc.Store(id="proy-lista-edit", data=[]),
            # marca para saber qué año/mes tiene cargado el store
            dcc.Store(id="proy-cargado", data=None),

            html.Hr(style={"margin": "40px 0 24px"}),
            html.H2("Proyección de ventas",
                    style={"color": AZUL, "fontWeight": "700"}),
            html.P("Captura la proyección mensual de cantidad por producto. "
                   "Agrega o quita productos libremente; nada se guarda hasta "
                   "que pulses «Guardar proyección». La lista es por mes.",
                   style={"color": "#6C757D", "marginBottom": "20px"}),

            html.Div(
                [
                    html.Div(
                        [
                            html.Label("Año", style={"fontWeight": "600",
                                                     "color": AZUL,
                                                     "display": "block",
                                                     "marginBottom": "4px"}),
                            dcc.Dropdown(
                                id="proy-anio",
                                options=[{"label": str(a), "value": a} for a in ANIOS],
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
                                id="proy-mes",
                                options=[{"label": n, "value": m} for m, n in MESES],
                                value=date.today().month, clearable=False,
                                style={"width": "180px"},
                            ),
                        ],
                    ),
                ],
                style={"display": "flex", "gap": "20px", "marginBottom": "24px",
                       "alignItems": "flex-end", "flexWrap": "wrap"},
            ),

            dbc.Card(
                dbc.CardBody(
                    [
                        html.H5("Cantidad proyectada por producto",
                                style={"color": AZUL, "fontWeight": "700",
                                       "marginBottom": "16px"}),
                        html.Div(id="proy-tabla-captura"),
                        html.Br(),
                        html.Button(
                            [html.I(className="fas fa-floppy-disk me-2"),
                             "Guardar proyección"],
                            id="proy-btn-guardar", n_clicks=0,
                            style={"backgroundColor": AZUL, "color": "white",
                                   "border": "none", "padding": "12px 22px",
                                   "borderRadius": "8px", "fontWeight": "600",
                                   "cursor": "pointer"},
                        ),
                        html.Div(id="proy-msg-guardar",
                                 style={"marginTop": "12px", "minHeight": "22px"}),
                    ]
                ),
                className="card-premium",
                style={"marginBottom": "24px", "maxWidth": "620px"},
            ),

            dbc.Card(
                dbc.CardBody(
                    [
                        html.H5("Agregar producto a este mes",
                                style={"color": AZUL, "fontWeight": "700",
                                       "marginBottom": "14px"}),
                        html.Div(
                            [
                                dcc.Input(
                                    id="proy-nuevo-producto",
                                    type="text",
                                    placeholder="Nombre exacto del producto",
                                    style={"width": "320px", "padding": "8px 10px",
                                           "borderRadius": "6px",
                                           "border": "1px solid #CBD5E1",
                                           "marginRight": "10px"},
                                ),
                                html.Button(
                                    [html.I(className="fas fa-plus me-2"), "Agregar"],
                                    id="proy-btn-agregar", n_clicks=0,
                                    style={"backgroundColor": DORADO,
                                           "color": AZUL, "border": "none",
                                           "padding": "8px 16px",
                                           "borderRadius": "6px",
                                           "fontWeight": "600", "cursor": "pointer"},
                                ),
                            ],
                            style={"marginBottom": "8px"},
                        ),
                        html.P("Se agrega solo en pantalla; recuerda pulsar "
                               "«Guardar proyección» para grabar. Escribe el "
                               "nombre EXACTO como aparece en Ventas (Producto).",
                               style={"fontSize": "12px", "color": "#6C757D"}),
                        html.Div(id="proy-msg-lista", style={"minHeight": "20px"}),
                    ]
                ),
                className="card-premium",
                style={"maxWidth": "620px"},
            ),
        ]
    )


def _leer_cantidades_actuales(valores, ids):
    """Recoge lo escrito en los inputs (para no perder cantidades
    al agregar/quitar)."""
    actuales = {}
    for val, cid in zip(valores, ids):
        actuales[cid["producto"]] = val if val is not None else 0
    return actuales


def registrar_callbacks_proyeccion_captura(app):

    # 1) Al cambiar año/mes: cargar la lista del mes en el store
    #    (de la base si existe; si no, los predeterminados).
    @app.callback(
        Output("proy-lista-edit", "data"),
        Output("proy-cargado", "data"),
        Input("proy-anio", "value"),
        Input("proy-mes", "value"),
    )
    def cargar_mes(anio, mes):
        if not anio or not mes:
            return [], None
        guardado = db.leer_proyeccion(anio, mes)   # {} si vacío
        if guardado:
            productos = db.listar_productos_mes(anio, mes)
            # VARIOS no va en la lista normal; se muestra fijo al final.
            # Su meta (si existe) se conserva y el render la coloca.
            lista = [{"producto": p, "cantidad": guardado.get(p, 0)}
                     for p in productos
                     if p.strip().upper() != VARIOS]
            if VARIOS in guardado:
                lista.append({"producto": VARIOS,
                              "cantidad": guardado.get(VARIOS, 0)})
        else:
            # mes nuevo: los predeterminados con cantidad 0
            lista = [{"producto": p, "cantidad": 0}
                     for p in db.productos_semilla()
                     if p.strip().upper() != VARIOS]
        return lista, {"anio": anio, "mes": mes}

    # 2) Render de la tabla según el store
    @app.callback(
        Output("proy-tabla-captura", "children"),
        Input("proy-lista-edit", "data"),
    )
    def render_tabla(lista):
        lista = lista or []
        if not lista:
            return _render_tabla(lista)
        encabezado = html.Div(
            f"{len(lista)} producto(s) en la lista de este mes",
            style={"fontSize": "12px", "color": "#6C757D",
                   "marginBottom": "10px", "fontStyle": "italic"},
        )
        return html.Div([encabezado, _render_tabla(lista)])

    # 3) Agregar producto -> SOLO al store (no a la base)
    @app.callback(
        Output("proy-lista-edit", "data", allow_duplicate=True),
        Output("proy-msg-lista", "children"),
        Output("proy-nuevo-producto", "value"),
        Input("proy-btn-agregar", "n_clicks"),
        State("proy-nuevo-producto", "value"),
        State("proy-lista-edit", "data"),
        State({"type": "proy-cant", "producto": ALL}, "value"),
        State({"type": "proy-cant", "producto": ALL}, "id"),
        prevent_initial_call=True,
    )
    def agregar(n, nombre, lista, valores, ids):
        nombre = (nombre or "").strip()
        if not nombre:
            return no_update, html.Span("Escribe un nombre.",
                                        style={"color": "#C0392B"}), no_update
        lista = lista or []
        # conservar lo que el usuario ya escribió en los inputs
        actuales = _leer_cantidades_actuales(valores, ids)
        for x in lista:
            if x["producto"] in actuales:
                x["cantidad"] = actuales[x["producto"]]
        # evitar duplicados (ignorando may/min y espacios)
        existentes = {x["producto"].strip().upper() for x in lista}
        if nombre.upper() == VARIOS:
            return no_update, html.Span(
                "«VARIOS» ya está fijo al final, no hace falta agregarlo.",
                style={"color": "#C0392B"}), ""
        if nombre.upper() in existentes:
            return no_update, html.Span(f"'{nombre}' ya está en la lista.",
                                        style={"color": "#C0392B"}), ""
        lista.append({"producto": nombre, "cantidad": 0})
        return lista, html.Span(f"'{nombre}' agregado (recuerda guardar).",
                                style={"color": "#198754"}), ""

    # 4) Quitar producto -> SOLO del store (no de la base)
    @app.callback(
        Output("proy-lista-edit", "data", allow_duplicate=True),
        Input({"type": "proy-quitar", "producto": ALL}, "n_clicks"),
        State("proy-lista-edit", "data"),
        State({"type": "proy-cant", "producto": ALL}, "value"),
        State({"type": "proy-cant", "producto": ALL}, "id"),
        prevent_initial_call=True,
    )
    def quitar(clicks, lista, valores, ids):
        if not ctx.triggered_id or not any(clicks):
            return no_update
        objetivo = ctx.triggered_id["producto"]
        lista = lista or []
        # conservar cantidades escritas
        actuales = _leer_cantidades_actuales(valores, ids)
        nueva = []
        for x in lista:
            if x["producto"] == objetivo:
                continue
            if x["producto"] in actuales:
                x["cantidad"] = actuales[x["producto"]]
            nueva.append(x)
        return nueva

    # 5) GUARDAR -> escribe el store completo en la base
    @app.callback(
        Output("proy-msg-guardar", "children"),
        Input("proy-btn-guardar", "n_clicks"),
        State("proy-anio", "value"),
        State("proy-mes", "value"),
        State("proy-lista-edit", "data"),
        State({"type": "proy-cant", "producto": ALL}, "value"),
        State({"type": "proy-cant", "producto": ALL}, "id"),
        State("store-sesion", "data"),
        prevent_initial_call=True,
    )
    def guardar(n, anio, mes, lista, valores, ids, sesion):
        if not sesion or sesion.get("rol") != "admin":
            return html.Span("Solo un administrador puede guardar.",
                             style={"color": "#C0392B"})
        if not anio or not mes:
            return html.Span("Selecciona año y mes.",
                             style={"color": "#C0392B"})
        # combinar: productos del store + cantidades de los inputs
        actuales = _leer_cantidades_actuales(valores, ids)
        proy = {}
        for x in (lista or []):
            p = x["producto"]
            if p.strip().upper() == VARIOS:
                continue  # VARIOS se maneja aparte, desde los inputs
            proy[p] = actuales.get(p, x.get("cantidad", 0))
        # VARIOS: su meta viene del input fijo (aunque no esté en el store).
        # Solo se guarda si tiene meta > 0, para no ensuciar meses sin uso.
        varios_meta = actuales.get(VARIOS, 0) or 0
        if varios_meta and float(varios_meta) > 0:
            proy[VARIOS] = varios_meta
        try:
            db.guardar_proyeccion(anio, mes, proy)
            return html.Span(f"Proyección guardada para {mes:02d}/{anio}: "
                             f"{len(proy)} línea(s).",
                             style={"color": "#198754", "fontWeight": "600"})
        except Exception as e:
            return html.Span(f"Error: {e}", style={"color": "#C0392B"})