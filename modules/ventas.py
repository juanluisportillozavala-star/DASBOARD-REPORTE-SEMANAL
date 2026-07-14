"""
=========================================================
MODULO VENTAS
=========================================================
Motor del reporte de ventas.
"""

import pandas as pd


class MotorVentas:

    def __init__(self):

        self.catalogo = None
        self.bd = None
        self.ventas = None

    # -----------------------------------------------------

    def cargar_catalogo(self, archivo):

        self.catalogo = pd.read_excel(
            archivo,
            sheet_name="Catalogo"
        )

        return self.catalogo

    # -----------------------------------------------------

    def cargar_bd(self, archivo):

        self.bd = pd.read_excel(archivo)

        self.bd["Fecha factura"] = pd.to_datetime(
            self.bd["Fecha factura"]
        )

        return self.bd

    # -----------------------------------------------------

    def generar_columnas():

        pass

    # -----------------------------------------------------

    def unir_catalogo():

        pass

    # -----------------------------------------------------

    def generar_reporte():

        pass