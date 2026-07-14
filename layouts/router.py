"""
=========================================================
ROUTER
=========================================================
Controla las páginas del sistema.
"""

from dash import html

from layouts.dashboard import crear_dashboard


# =========================================================
# PLANTILLA TEMPORAL PARA MÓDULOS
# =========================================================

def pagina_temporal(titulo):

    return html.Div(

        className="card-premium",

        children=[

            html.H1(
                titulo,
                className="titulo"
            ),

            html.P(
                "Módulo en desarrollo.",
                className="subtitulo"
            ),

            html.Hr(),

            html.Br(),

            html.H3(
                "🚧 Próximamente",
                style={
                    "color": "#173C73"
                }
            ),

            html.Br(),

            html.P(

                "Este módulo será desarrollado en las siguientes etapas del proyecto.",

                style={

                    "fontSize": "18px",

                    "color": "#666"

                }

            )

        ]

    )


# =========================================================
# ROUTER
# =========================================================

def crear_router(pathname):

    if pathname in ["/", "/dashboard", None]:

        return crear_dashboard()

    elif pathname == "/ventas":

        return pagina_temporal("Ventas")

    elif pathname == "/ingresos":

        return pagina_temporal("Ingresos")

    elif pathname == "/cartera":

        return pagina_temporal("Cartera")

    elif pathname == "/inventario":

        return pagina_temporal("Inventario")

    elif pathname == "/saldo-proveedor":

        return pagina_temporal("Saldo Proveedor")

    elif pathname == "/reportes":

        return pagina_temporal("Reportes")

    elif pathname == "/configuracion":

        return pagina_temporal("Configuración")

    else:

        return html.Div(

            className="card-premium",

            children=[

                html.H1(
                    "404",
                    className="titulo"
                ),

                html.P(
                    "Página no encontrada.",
                    className="subtitulo"
                )

            ]

        )