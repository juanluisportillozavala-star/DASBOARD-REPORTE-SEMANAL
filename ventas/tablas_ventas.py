"""
=========================================================
ventas/tablas_ventas.py
=========================================================
CATÁLOGO de las tablas jerárquicas de Ventas, mostradas en
PESTAÑAS (una visible a la vez).

VELOCIDAD: solo la tabla de la pestaña ACTIVA se monta en la
página, así que al filtrar (mes/semana) únicamente se
recalcula ESA tabla, no las cuatro. Cambiar de pestaña monta
la nueva (pequeño cálculo en ese momento).

Añadir una tabla = añadir una entrada a TABLAS. Nada más.
"""

from dash import html, dcc, Input, Output

from ventas.tabla_arbol import crear_layout_tabla, registrar_callbacks_tablas


TABLAS = [
    {"clave": "vend_cli_prod", "niveles": ["Vendedor", "Cliente", "Producto"]},
    {"clave": "prod_cli", "niveles": ["Producto", "Cliente"]},
    {"clave": "cli_prod", "niveles": ["Cliente", "Producto"]},
    {"clave": "vend_prod", "niveles": ["Vendedor", "Producto"]},
]


def _titulo(t):
    return t.get("titulo") or " / ".join(t["niveles"])


def crear_layout_tablas_ventas():
    """Pestañas: una por tabla. Solo se monta la tabla activa."""
    tabs = [
        dcc.Tab(
            label=_titulo(t),
            value=t["clave"],
            style={"padding": "10px 16px", "fontWeight": "600"},
            selected_style={"padding": "10px 16px", "fontWeight": "700",
                            "color": "#173C73",
                            "borderTop": "3px solid #D4AF37"},
        )
        for t in TABLAS
    ]

    return html.Div(
        [
            dcc.Tabs(
                id="tabs-tablas",
                value=TABLAS[0]["clave"],   # primera pestaña activa
                children=tabs,
            ),
            html.Div(style={"height": "12px"}),
            # aquí se monta SOLO la tabla de la pestaña activa
            html.Div(id="contenedor-tabla-activa"),
        ]
    )


def registrar_callbacks_tablas_ventas(app):
    # callbacks de la fábrica (pattern-matching, sirven a todas)
    registrar_callbacks_tablas(app)

    # monta la tabla de la pestaña activa (perezoso)
    @app.callback(
        Output("contenedor-tabla-activa", "children"),
        Input("tabs-tablas", "value"),
    )
    def montar_tabla_activa(clave):
        t = next((x for x in TABLAS if x["clave"] == clave), TABLAS[0])
        return crear_layout_tabla(t["clave"], t["niveles"], t.get("titulo"))