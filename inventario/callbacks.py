"""
=========================================================
CALLBACKS DEL MÓDULO INVENTARIO
=========================================================
Solo el callback de "cargar señal al entrar": pone la marca
ligera {cargado, version} en store-bd-inventario leyendo de la
caché. Los KPIs, gráficos, filtro y tabla están en
inventario/tabla_inventario.py.
"""

from dash import Input, Output, no_update
import db

MODULO = "inventario"


def registrar_callbacks_inventario_carga(app):
    @app.callback(
        Output("store-bd-inventario", "data"),
        Input("store-bd-inventario", "data"),
    )
    def cargar_desde_bd_inventario(marca):
        try:
            df = db.obtener_df(MODULO)
        except Exception as e:
            print(f">>> [DB] No se pudo leer inventario: {e}", flush=True)
            return no_update
        if df is None or len(df) == 0:
            return no_update
        version = db.version_actual(MODULO)
        if marca and isinstance(marca, dict) and marca.get("version") == version:
            return no_update
        return {"cargado": True, "version": version}