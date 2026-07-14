"""
SIDEBAR
"""

from dash import html, dcc


def item(nombre, icono, ruta):

    return dcc.Link(

        href=ruta,

        className="menu-link",

        children=[

            html.Div(

                className="menu-item",

                children=[

                    html.I(className=icono),

                    html.Span(nombre)

                ]

            )

        ]

    )


def crear_sidebar():

    return html.Div(

        className="sidebar",

        children=[

            html.Div(

                "MENÚ PRINCIPAL",

                className="menu-titulo"

            ),

            item("Dashboard", "fas fa-gauge-high", "/dashboard"),

            item("Ventas", "fas fa-chart-line", "/ventas"),

            item("Ingresos", "fas fa-wallet", "/ingresos"),

            item("Cartera", "fas fa-users", "/cartera"),

            item("Inventario", "fas fa-box", "/inventario"),

            item("Saldo Proveedor", "fas fa-truck", "/saldo-proveedor"),

            item("Reportes", "fas fa-file-lines", "/reportes"),

            item("Configuración", "fas fa-gear", "/configuracion")

        ]

    )