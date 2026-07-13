"""
=========================================================
HEADER
=========================================================
"""

from dash import html

from config.config import (
    LOGO_BASE64,
    TITULO,
    SUBTITULO
)


def crear_header():

    return html.Div(

        style={

            "backgroundColor": "#0B2D5B",

            "padding": "25px",

            "borderBottom": "5px solid #C9A227",

            "boxShadow": "0px 3px 10px rgba(0,0,0,.25)"

        },

        children=[

            html.Div(

                style={

                    "display":"flex",

                    "alignItems":"center",

                    "maxWidth":"1700px",

                    "margin":"auto"

                },

                children=[

                    html.Img(

                        src=f"data:image/png;base64,{LOGO_BASE64}",

                        style={

                            "width":"320px",

                            "background":"white",

                            "padding":"10px",

                            "borderRadius":"10px",

                            "marginRight":"30px"

                        }

                    ),

                    html.Div(

                        [

                            html.H1(

                                TITULO,

                                style={

                                    "color":"white",

                                    "margin":"0",

                                    "fontSize":"52px"

                                }

                            ),

                            html.H4(

                                SUBTITULO,

                                style={

                                    "color":"#D4AF37"

                                }

                            )

                        ]

                    )

                ]

            )

        ]

    )