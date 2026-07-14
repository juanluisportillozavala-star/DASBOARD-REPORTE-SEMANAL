"""
GRÁFICAS DEL DASHBOARD
"""

import plotly.graph_objects as go


def grafica_vacia():

    fig = go.Figure()

    fig.update_layout(

        template="plotly_white",

        height=400

    )

    return fig