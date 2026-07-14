"""
=========================================================
CALLBACKS VENTAS
=========================================================
"""

from dash import Input, Output, callback
from dash import html
import plotly.graph_objects as go


def registrar_callbacks(app):

    # =====================================================
    # GRAFICA VACÍA
    # =====================================================

    @app.callback(

        Output("grafica-ventas", "figure"),

        Input("grafica-ventas", "id")

    )
    def cargar_grafica(_):

        fig = go.Figure()

        fig.update_layout(

            title="Ventas por Mes",

            template="plotly_white",

            paper_bgcolor="white",

            plot_bgcolor="white",

            margin=dict(

                l=20,
                r=20,
                t=50,
                b=20

            ),

            xaxis_title="Mes",

            yaxis_title="Ventas"

        )

        return fig

    # =====================================================
    # TABLA VACÍA
    # =====================================================

    @app.callback(

        Output("tabla-ventas", "children"),

        Input("tabla-ventas", "id")

    )
    def cargar_tabla(_):

        return html.Div(

            [

                html.Br(),

                html.H5(

                    "No hay información cargada.",

                    style={

                        "textAlign":"center",

                        "color":"gray"

                    }

                )

            ]

        )