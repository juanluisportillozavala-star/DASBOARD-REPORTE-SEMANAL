"""
=========================================================
CONFIGURACIÓN GENERAL
=========================================================
"""

import base64
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

LOGO = os.path.join(BASE_DIR, "assets", "logo.png")


def convertir_logo():

    try:

        with open(LOGO, "rb") as f:

            return base64.b64encode(f.read()).decode()

    except:

        return ""


LOGO_BASE64 = convertir_logo()


COLOR_AZUL = "#0B2D5B"

COLOR_DORADO = "#C9A227"

COLOR_FONDO = "#F5F7FA"

COLOR_TARJETA = "#FFFFFF"

TITULO = "SISTEMA GERENCIAL LIDERZA"

SUBTITULO = "Dashboard Comercial"