"""
=========================================================
sidebar.py
=========================================================
Menú lateral del Sistema Gerencial Liderza.
"""

from dash import html, dcc
from config import *


def item_menu(icono, texto, ruta):

    return dcc.Link(

        href=ruta,

        className="menu-link",

        children=[

            html.Div(

                className="menu-item",

                children=[

                    html.I(

                        className=icono

                    ),

                    html.Span(

                        texto

                    )

                ]

            )

        ]

    )


def crear_sidebar():

    return html.Div(

        className="sidebar",

        children=[

            # ==========================================
            # TITULO
            # ==========================================

            html.Div(

                "MENÚ PRINCIPAL",

                className="menu-titulo"

            ),

            # ==========================================
            # OPCIONES
            # ==========================================

            item_menu(

                ICONOS["dashboard"],

                "Dashboard",

                "/dashboard"

            ),

            item_menu(

                ICONOS["ventas"],

                "Ventas",

                "/ventas"

            ),

            item_menu(

                ICONOS["ingresos"],

                "Ingresos",

                "/ingresos"

            ),

            item_menu(

                ICONOS["cartera"],

                "Cartera",

                "/cartera"

            ),

            item_menu(

                ICONOS["inventario"],

                "Inventario",

                "/inventario"

            ),

            item_menu(

                ICONOS["proveedores"],

                "Saldo Proveedor",

                "/proveedores"

            ),

            html.Hr(),

            item_menu(

                ICONOS["reportes"],

                "Reportes",

                "/reportes"

            ),

            item_menu(

                ICONOS["configuracion"],

                "Configuración",

                "/configuracion"

            )

        ]

    )