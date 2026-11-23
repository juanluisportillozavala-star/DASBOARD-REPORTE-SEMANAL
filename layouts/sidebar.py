"""
SIDEBAR
=========================================================
NOTA: el ítem "Dashboard" está OCULTO por ahora (módulo aún no
desarrollado). Para reactivarlo, descomentar su línea abajo.
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


def crear_sidebar(rol=None, vendedor=None):

    # Ítems que TODOS ven (admin y consulta)
    items = [

        html.Div(
            "MENÚ PRINCIPAL",
            className="menu-titulo"
        ),

        # Dashboard OCULTO por ahora (módulo en desarrollo):
        # item("Dashboard", "fas fa-gauge-high", "/dashboard"),

        item("Ventas", "fas fa-chart-line", "/ventas"),

        item("Proyección", "fas fa-bullseye", "/proyeccion"),

        item("Ingresos", "fas fa-wallet", "/ingresos"),

        item("Cartera", "fas fa-users", "/cartera"),

        item("Inventario", "fas fa-box", "/inventario"),

        item("Saldo Proveedor", "fas fa-truck", "/saldo-proveedor"),

        item("BSC", "fas fa-table-columns", "/bsc"),

        item("Reportes", "fas fa-file-lines", "/reportes"),

    ]

    # Captura de proyecciones: solo la ven el ADMIN o un usuario con
    # VENDEDOR asignado (los que de verdad pueden editar algo). A un
    # usuario de consulta sin vendedor se le oculta el ítem.
    # Se inserta después de "Proyección". Como Dashboard ya no está,
    # Proyección es el índice 2 y Captura va en el índice 3.
    if rol == "admin" or vendedor:

        items.insert(
            3,
            item("Captura de proyecciones", "fas fa-pen-to-square",
                 "/captura-proyeccion"),
        )

    # Ítems SOLO para admin: carga de datos y configuración.
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