"""
=========================================================
SISTEMA GERENCIAL LIDERZA
=========================================================
Aplicación principal
"""

from dash import Dash
import dash_bootstrap_components as dbc

# =========================
# Layouts
# =========================

from layouts.principal import crear_principal, registrar_callbacks_principal

# =========================
# Callbacks
# =========================

from callbacks.router_callbacks import registrar_router_callbacks
from ventas.callbacks import registrar_callbacks_ventas
from ventas.tablas_ventas import registrar_callbacks_tablas_ventas
from ventas.graficos import registrar_callbacks_graficos
from ventas.comparativo import registrar_callbacks_comparativo
from carga import registrar_callbacks_carga

# Ingresos
from ingresos.callbacks import registrar_callbacks_ingresos
from ingresos.tabla_ingresos import registrar_callbacks_tabla_ingresos

# Inventario
from inventario.callbacks import registrar_callbacks_inventario_carga
from inventario.tabla_inventario import registrar_callbacks_inventario

# Configuración (admin de usuarios)
from configuracion import registrar_callbacks_configuracion

# Cartera
from cartera.callbacks import registrar_callbacks_cartera
from cartera.tabla_cartera import registrar_callbacks_tabla_cartera

# Proyección
from proyeccion.vista import registrar_callbacks_proyeccion

# Captura de proyecciones (por vendedor)
from captura_proyeccion import registrar_callbacks_captura_proyeccion

# Saldo Proveedor
from saldo_proveedor.callbacks import registrar_callbacks_sp_calendario
from saldo_proveedor.tabla_sp import registrar_callbacks_sp

# =========================
# Crear aplicación
# =========================

app = Dash(

    __name__,

    external_stylesheets=[

        dbc.themes.BOOTSTRAP,

        "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.2/css/all.min.css",

        "/assets/estilos.css"

    ],

    suppress_callback_exceptions=True,

    title="Sistema Gerencial Liderza"

)

server = app.server

# ==========================================================
# ENDPOINT /ping  —  mantiene DESPIERTA la base de datos
# ==========================================================
# Un servicio externo (cron-job.org) visita esta ruta cada
# pocos días. La consulta mínima "SELECT 1" toca Supabase y
# evita que el plan gratuito pause el proyecto por inactividad.
# No afecta el resto de la app.
import db as _db_ping
from flask import Response

@server.route("/ping")
def ping():
    # Respuesta MÍNIMA para el cron anti-pausa: cuerpo de 1 byte
    # ("o") y encabezados reducidos, para no superar el límite de
    # tamaño de cron-job.org ("salida demasiado grande"). Igual
    # toca Supabase (SELECT 1) para mantenerla despierta.
    try:
        with _db_ping._conn() as c, c.cursor() as cur:
            cur.execute("SELECT 1;")
            cur.fetchone()
        cuerpo = "o"
        codigo = 200
    except Exception:
        cuerpo = "e"
        codigo = 500
    resp = Response(cuerpo, status=codigo, mimetype="text/plain")
    # quitar encabezados que abultan la respuesta
    resp.headers["Content-Type"] = "text/plain"
    resp.headers.pop("Set-Cookie", None)
    return resp


# ==========================================================
# ENDPOINT /descargar-reporte  —  Excel con dinámicas VIVAS
# ==========================================================
# Genera el REPORTE tomando la plantilla del repo y reemplazando
# las 4 BD (Ventas/Cobranza/Cartera/CxP) con lo guardado en
# Supabase. Devuelve el archivo como descarga. Las dinámicas se
# refrescan solas al abrir el archivo en Excel.
import os as _os
from datetime import datetime as _dt
from flask import send_file as _send_file
import exportar_reporte as _export

_PLANTILLA = _os.path.join(_os.path.dirname(__file__),
                           "plantillas", "REPORTE_SEMANAL_FINAL.xlsx")

@server.route("/descargar-reporte")
def descargar_reporte():
    if not _os.path.exists(_PLANTILLA):
        return Response(
            "No se encontró la plantilla. Sube el archivo a "
            "plantillas/REPORTE_SEMANAL_FINAL.xlsx en el repositorio.",
            status=404, mimetype="text/plain")
    try:
        data = _export.generar_reporte(_PLANTILLA)
    except Exception as e:
        return Response(f"Error al generar el reporte: {e}",
                        status=500, mimetype="text/plain")
    nombre = f"Reporte_Liderza_{_dt.now():%Y-%m-%d}.xlsx"
    return _send_file(
        _io_bytes(data),
        as_attachment=True,
        download_name=nombre,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


def _io_bytes(data):
    import io
    b = io.BytesIO(data)
    b.seek(0)
    return b

# =========================
# Layout principal
# =========================

app.layout = crear_principal()

# ==========================================================
# INICIALIZACIÓN DE BASE DE DATOS (Supabase / PostgreSQL)
# ==========================================================
import db

try:
    db.inicializar_esquema()
    print(">>> [DB] Conexión a Supabase OK. Tablas listas.", flush=True)
except Exception as e:
    print(f">>> [DB] ERROR conectando a Supabase: {e}", flush=True)

# =========================
# Registrar callbacks
# =========================

registrar_callbacks_principal(app)

registrar_router_callbacks(app)

# Ventas
registrar_callbacks_ventas(app)
registrar_callbacks_tablas_ventas(app)
registrar_callbacks_graficos(app)
registrar_callbacks_comparativo(app)

# Carga central
registrar_callbacks_carga(app)

# Ingresos
registrar_callbacks_ingresos(app)
registrar_callbacks_tabla_ingresos(app)

# Inventario
registrar_callbacks_inventario_carga(app)
registrar_callbacks_inventario(app)

# Configuración
registrar_callbacks_configuracion(app)

# Cartera
registrar_callbacks_cartera(app)
registrar_callbacks_tabla_cartera(app)

# Proyección
registrar_callbacks_proyeccion(app)

# Captura de proyecciones (por vendedor)
registrar_callbacks_captura_proyeccion(app)

# Saldo Proveedor
registrar_callbacks_sp_calendario(app)
registrar_callbacks_sp(app)

# =========================
# Ejecutar
# =========================

if __name__ == "__main__":

    app.run(debug=True)
    