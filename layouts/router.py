"""
=========================================================
ROUTER
=========================================================
Controla las páginas del sistema.
"""

from dash import html

from layouts.dashboard import crear_dashboard


# =========================================================
# PÁGINAS TEMPORALES
# =========================================================

def pagina_construccion(nombre):

    return html.Div(

        className="card-premium",

        children=[

            html.H2(

                nombre,

                className="titulo"

            ),

            html.Hr(),

            html.H4(

                "🚧 Módulo en construcción",

                style={

                    "color":"#173C73"

                }

            ),

            html.Br(),

            html.P(

                f"El módulo '{nombre}' estará disponible en una próxima versión.",

                style={

                    "fontSize":"18px",

                    "color":"#666"

                }

            )

        ]

    )


# =========================================================
# ROUTER
# =========================================================

def crear_router(pathname="/dashboard"):

    if pathname in ["/", "/dashboard"]:

        return crear_dashboard()

    elif pathname == "/ventas":

        return pagina_construccion("Ventas")

    elif pathname == "/ingresos":

        return pagina_construccion("Ingresos")

    elif pathname == "/cartera":

        return pagina_construccion("Cartera")

    elif pathname == "/inventario":

        return pagina_construccion("Inventario")

    elif pathname == "/saldo-proveedor":

        return pagina_construccion("Saldo Proveedor")

    elif pathname == "/reportes":

        return pagina_construccion("Reportes")

    elif pathname == "/configuracion":

        return pagina_construccion("Configuración")

    return pagina_construccion("Página no encontrada")