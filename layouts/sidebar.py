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


def crear_sidebar(rol=None):

    # Ítems que TODOS ven (admin y consulta)
    items = [

        html.Div(
            "MENÚ PRINCIPAL",
            className="menu-titulo"
        ),

        item("Dashboard", "fas fa-gauge-high", "/dashboard"),

        item("Ventas", "fas fa-chart-line", "/ventas"),

        item("Proyección", "fas fa-bullseye", "/proyeccion"),

        # Captura de proyecciones: la usan los vendedores (cada quien
        # edita la suya) y el admin. La edición se valida en el
        # servidor, así que es seguro mostrarla a todos.
        item("Captura de proyecciones", "fas fa-pen-to-square", "/captura-proyeccion"),

        item("Ingresos", "fas fa-wallet", "/ingresos"),

        item("Cartera", "fas fa-users", "/cartera"),

        item("Inventario", "fas fa-box", "/inventario"),

        item("Saldo Proveedor", "fas fa-truck", "/saldo-proveedor"),

        item("Reportes", "fas fa-file-lines", "/reportes"),

    ]

    # Ítems SOLO para admin: carga de datos y configuración
    if rol == "admin":

        items.append(

            item("Cargar datos", "fas fa-cloud-arrow-up", "/cargar")

        )

        items.append(

            item("Configuración", "fas fa-gear", "/configuracion")

        )

    return html.Div(

        className="sidebar",

        children=items

    )