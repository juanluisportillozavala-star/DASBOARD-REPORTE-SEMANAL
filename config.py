"""
=========================================================
config.py
=========================================================
Configuración global del Sistema Gerencial Liderza.

Aquí se centralizan:

• Logo
• Colores
• Constantes
• Configuración general
"""

import os
import base64


# =========================================================
# CONFIGURACIÓN GENERAL
# =========================================================

NOMBRE_SISTEMA = "Sistema Gerencial Liderza"

VERSION = "1.0"

EMPRESA = "Liderza"


# =========================================================
# RUTAS
# =========================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

ASSETS_DIR = os.path.join(BASE_DIR, "assets")

LOGO = os.path.join(ASSETS_DIR, "logo.png")


# =========================================================
# CARGAR LOGO
# =========================================================

def cargar_logo():

    try:

        with open(LOGO, "rb") as archivo:

            return base64.b64encode(
                archivo.read()
            ).decode()

    except:

        return ""


LOGO_BASE64 = cargar_logo()


# =========================================================
# COLORES CORPORATIVOS
# =========================================================

COLOR_PRIMARIO = "#0B2D5B"

COLOR_SECUNDARIO = "#123E7A"

COLOR_DORADO = "#C9A227"

COLOR_BLANCO = "#FFFFFF"

COLOR_GRIS = "#F4F6F9"

COLOR_GRIS_OSCURO = "#6B7280"

COLOR_NEGRO = "#1F2937"

COLOR_VERDE = "#22C55E"

COLOR_ROJO = "#EF4444"


# =========================================================
# TAMAÑOS
# =========================================================

ANCHO_MENU = "240px"

ALTO_HEADER = "70px"

RADIO_BORDES = "14px"


# =========================================================
# SOMBRAS
# =========================================================

SOMBRA = "0px 4px 15px rgba(0,0,0,.08)"


# =========================================================
# ICONOS DEL MENÚ
# =========================================================

ICONOS = {

    "dashboard": "bi bi-speedometer2",

    "ventas": "bi bi-graph-up",

    "ingresos": "bi bi-cash-stack",

    "cartera": "bi bi-people",

    "inventario": "bi bi-box-seam",

    "proveedores": "bi bi-truck",

    "reportes": "bi bi-file-earmark-text",

    "configuracion": "bi bi-gear"

}


# =========================================================
# MÓDULOS
# =========================================================

MODULOS = [

    "Dashboard",

    "Ventas",

    "Ingresos",

    "Cartera",

    "Inventario",

    "Saldo Proveedor",

    "Reportes",

    "Configuración"

]