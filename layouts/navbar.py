"""
=========================================================
NAVBAR
=========================================================
"""

from dash import html
import dash_bootstrap_components as dbc


def crear_navbar():

    return dbc.Nav(

        [

            dbc.NavLink("🏠 Dashboard", href="#"),

            dbc.NavLink("📊 Ventas", href="#"),

            dbc.NavLink("💰 Ingresos", href="#"),

            dbc.NavLink("💳 Cartera", href="#"),

            dbc.NavLink("📦 Inventario", href="#"),

            dbc.NavLink("🚚 Saldo Proveedor", href="#")

        ],

        pills=True,

        justified=True,

        className="menu-superior"

    )