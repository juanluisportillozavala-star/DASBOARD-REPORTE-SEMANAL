"""
=========================================================
carga.py  —  CARGA CENTRAL DE BASES DE DATOS (solo admin)
=========================================================
Una sola pantalla donde el admin sube las BD de TODOS los
módulos. Diseñada para escalar: agregar un módulo nuevo =
agregar una entrada a MODULOS_CARGA.

Cada módulo declara:
  clave:      id corto del módulo (= clave en la tabla datasets)
  titulo:     nombre visible
  archivos:   lista de archivos que necesita, cada uno con
              su id y etiqueta
  procesar:   función que recibe los contenidos (en el orden
              de 'archivos') y devuelve el DataFrame final a
              guardar en Supabase. Si el módulo pide fecha, la
              recibe como segundo argumento.
  pide_fecha: (opcional) True si el módulo necesita una fecha
              de referencia que el admin captura al cargar
              (caso Cartera: la columna N / fecha de corte).
"""

from datetime import date

from dash import Input, Output, State, html, dcc, no_update, ALL, ctx
import dash_bootstrap_components as dbc

import db
from inventario_historico_captura import (
    crear_seccion_historico_inventario,
    registrar_callbacks_historico_captura,
)
from ventas.procesamiento import leer_archivos
from ingresos.procesamiento import leer_archivo as leer_ingresos
from inventario.procesamiento import leer_archivo as leer_inventario
from cartera.procesamiento import leer_archivo as leer_cartera

AZUL = "#173C73"
DORADO = "#D4AF37"


# --- adaptadores de procesado por módulo ---
# Reciben la lista de 'contents' (en el orden de 'archivos').
# Los módulos con pide_fecha reciben además 'fecha' (str ISO).

def _procesar_ventas(contents_list, fecha=None):
    catalogo, ventas = contents_list  # orden segun 'archivos' abajo
    _, df_ventas = leer_archivos(catalogo, ventas)
    return df_ventas


def _procesar_ingresos(contents_list, fecha=None):
    # Un solo archivo (la BD de ingresos).
    (bd,) = contents_list
    return leer_ingresos(bd)


def _procesar_inventario(contents_list, fecha=None):
    # DOS archivos que se cruzan por código de producto:
    #   valuation (fechas de entrada) + quants (ubicaciones).
    # La fecha de corte (manual) alimenta los DIAS EN ALMACEN.
    valuation, quants = contents_list  # orden segun 'archivos'
    return leer_inventario(valuation, quants, fecha_corte=fecha)


def _procesar_cartera(contents_list, fecha=None):
    # Un solo archivo + la FECHA de referencia (columna N) que el
    # admin captura al cargar. Base de todo el aging de cartera.
    (bd,) = contents_list
    return leer_cartera(bd, fecha_referencia=fecha)


# --- CATÁLOGO DE MÓDULOS ---
MODULOS_CARGA = {
    "ventas": {
        "titulo": "Ventas",
        "archivos": [
            {"id": "catalogo", "label": "Catálogo"},
            {"id": "bd", "label": "BD Ventas"},
        ],
        "procesar": _procesar_ventas,
    },
    "ingresos": {
        "titulo": "Ingresos",
        "archivos": [
            {"id": "bd", "label": "BD Ingresos"},
        ],
        "procesar": _procesar_ingresos,
    },
    "inventario": {
        "titulo": "Inventario",
        "archivos": [
            {"id": "valuation", "label": "BD Valuación (fechas)"},
            {"id": "quants", "label": "BD Quants (ubicaciones)"},
        ],
        "procesar": _procesar_inventario,
        "pide_fecha": True,
    },
    "cartera": {
        "titulo": "Cartera",
        "archivos": [
            {"id": "bd", "label": "BD Cartera"},
        ],
        "procesar": _procesar_cartera,
        "pide_fecha": True,
    },
}


def _tarjeta_modulo(clave, cfg):
    """Una tarjeta por módulo, con sus zonas de subida y botón.
    Si el módulo pide_fecha, inserta un selector de fecha entre
    los archivos y el botón de procesar."""
    uploads = []
    for arch in cfg["archivos"]:
        uploads.append(
            html.Div(
                [
                    html.H6(arch["label"],
                            style={"color": AZUL, "marginBottom": "6px"}),
                    dcc.Upload(
                        id={"type": "carga-upload", "modulo": clave,
                            "archivo": arch["id"]},
                        multiple=False,
                        children=html.Button(
                            [html.I(className="fas fa-folder-open me-2"),
                             f"Seleccionar {arch['label']}"],
                            style={"width": "100%", "padding": "10px",
                                   "borderRadius": "8px",
                                   "border": f"1px solid {AZUL}",
                                   "backgroundColor": "white", "color": AZUL,
                                   "cursor": "pointer"},
                        ),
                    ),
                    html.Div(
                        id={"type": "carga-nombre", "modulo": clave,
                            "archivo": arch["id"]},
                        style={"fontSize": "13px", "color": "#6C757D",
                               "marginTop": "4px", "marginBottom": "12px"},
                        children="Ningún archivo seleccionado.",
                    ),
                ]
            )
        )

    # selector de fecha (solo si el módulo lo pide) — entre archivos y botón
    bloque_fecha = []
    if cfg.get("pide_fecha"):
        bloque_fecha = [
            html.Div(
                [
                    html.H6("Fecha de corte",
                            style={"color": AZUL, "marginBottom": "6px"}),
                    html.P("Fecha base para calcular la antigüedad "
                           "(días en almacén / vencimiento de cartera).",
                           style={"fontSize": "12px", "color": "#6C757D",
                                  "marginBottom": "8px"}),
                    dcc.DatePickerSingle(
                        id={"type": "carga-fecha", "modulo": clave},
                        display_format="DD/MM/YYYY",
                        placeholder="Selecciona la fecha",
                        date=date.today().isoformat(),
                        style={"marginBottom": "14px"},
                    ),
                ]
            )
        ]

    return html.Div(
        [
            html.H4(cfg["titulo"],
                    style={"color": AZUL, "fontWeight": "700",
                           "marginBottom": "16px"}),
            *uploads,
            *bloque_fecha,
            html.Button(
                [html.I(className="fas fa-gears me-2"), "Procesar y guardar"],
                id={"type": "carga-btn", "modulo": clave},
                n_clicks=0,
                style={"backgroundColor": AZUL, "color": "white",
                       "border": "none", "padding": "12px 20px",
                       "borderRadius": "8px", "fontWeight": "600",
                       "cursor": "pointer", "width": "100%"},
            ),
            html.Div(
                id={"type": "carga-estado", "modulo": clave},
                style={"marginTop": "14px", "minHeight": "24px"},
            ),
        ],
        style={"backgroundColor": "white", "padding": "28px",
               "borderRadius": "14px", "borderTop": f"4px solid {DORADO}",
               "boxShadow": "0 6px 24px rgba(23,60,115,0.10)",
               "width": "420px", "maxWidth": "92vw"},
    )


def crear_layout_carga():
    """Página de carga central: una tarjeta por módulo + la
    sección de captura de proyección (abajo)."""
    tarjetas = [_tarjeta_modulo(k, cfg) for k, cfg in MODULOS_CARGA.items()]
    return html.Div(
        [
            html.H1("Carga de datos", className="titulo"),
            html.P("Sube las bases de datos de cada módulo. Reemplazan la "
                   "versión anterior y quedan disponibles para todo el equipo.",
                   className="subtitulo"),
            html.Br(),
            html.Div(
                tarjetas,
                style={"display": "flex", "flexWrap": "wrap", "gap": "24px"},
            ),

            # sección de captura del histórico de inventario (abajo, aparte)
            crear_seccion_historico_inventario(),
        ]
    )


def registrar_callbacks_carga(app):

    # callbacks de la captura del histórico de inventario
    registrar_callbacks_historico_captura(app)

    # Mostrar el nombre del archivo seleccionado en cada zona
    @app.callback(
        Output({"type": "carga-nombre", "modulo": ALL, "archivo": ALL}, "children"),
        Input({"type": "carga-upload", "modulo": ALL, "archivo": ALL}, "filename"),
    )
    def mostrar_nombres(nombres):
        salida = []
        for n in nombres:
            if n:
                salida.append("✓ " + n)
            else:
                salida.append("Ningún archivo seleccionado.")
        return salida

    # Procesar y guardar en Supabase (un botón por módulo)
    @app.callback(
        Output({"type": "carga-estado", "modulo": ALL}, "children"),
        Input({"type": "carga-btn", "modulo": ALL}, "n_clicks"),
        State({"type": "carga-upload", "modulo": ALL, "archivo": ALL}, "contents"),
        State({"type": "carga-upload", "modulo": ALL, "archivo": ALL}, "id"),
        State({"type": "carga-fecha", "modulo": ALL}, "date"),
        State({"type": "carga-fecha", "modulo": ALL}, "id"),
        State("store-sesion", "data"),
        prevent_initial_call=True,
    )
    def procesar_y_guardar(n_clicks_list, contents_all, ids_all,
                           fechas_all, fechas_ids, sesion):
        # cuántos módulos hay (para armar la salida del tamaño correcto)
        claves = list(MODULOS_CARGA.keys())
        salida = [no_update] * len(claves)

        trigger = ctx.triggered_id
        if not trigger:
            return salida

        modulo = trigger["modulo"]
        idx = claves.index(modulo)

        # Verificar rol admin
        if not sesion or sesion.get("rol") != "admin":
            salida[idx] = html.Div("Solo un administrador puede cargar datos.",
                                   style={"color": "#DC3545"})
            return salida

        # Recolectar los contents de ESTE módulo, en el orden de 'archivos'
        cfg = MODULOS_CARGA[modulo]
        orden = [a["id"] for a in cfg["archivos"]]
        por_archivo = {}
        for cont, cid in zip(contents_all, ids_all):
            if cid["modulo"] == modulo:
                por_archivo[cid["archivo"]] = cont

        # Validar que estén todos
        faltan = [a for a in orden if not por_archivo.get(a)]
        if faltan:
            salida[idx] = html.Div(
                "Falta seleccionar: " + ", ".join(faltan),
                style={"color": "#DC3545"})
            return salida

        contents_ordenados = [por_archivo[a] for a in orden]

        # Si el módulo pide fecha, recuperarla y validarla
        fecha = None
        if cfg.get("pide_fecha"):
            for f, fid in zip(fechas_all, fechas_ids):
                if fid["modulo"] == modulo:
                    fecha = f
                    break
            if not fecha:
                salida[idx] = html.Div(
                    "Selecciona la fecha de corte antes de procesar.",
                    style={"color": "#DC3545"})
                return salida

        try:
            df = cfg["procesar"](contents_ordenados, fecha)
            admin = sesion.get("usuario", "admin")
            db.guardar_dataset(modulo, df, admin)
            extra = f" (fecha de corte: {fecha})" if fecha else ""
            salida[idx] = html.Div(
                [html.I(className="fas fa-circle-check me-2"),
                 f"Guardado correctamente: {len(df):,} registros.{extra}"],
                style={"color": "#198754", "fontWeight": "600"})
        except Exception as e:
            salida[idx] = html.Div(
                ["Error al procesar: ", html.Pre(str(e))],
                style={"color": "#DC3545"})
        return salida