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
              guardar en Supabase.

Hoy solo Ventas (catálogo + BD). Para añadir Ingresos, etc.,
se agrega su entrada con su propia función de procesado.
"""

from dash import Input, Output, State, html, dcc, no_update, ALL, ctx
import dash_bootstrap_components as dbc

import db
from ventas.procesamiento import leer_archivos

AZUL = "#173C73"
DORADO = "#D4AF37"


# --- adaptadores de procesado por módulo ---
# Reciben la lista de 'contents' (en el orden de 'archivos')
# y devuelven el DataFrame a guardar.

def _procesar_ventas(contents_list):
    catalogo, ventas = contents_list  # orden segun 'archivos' abajo
    _, df_ventas = leer_archivos(catalogo, ventas)
    return df_ventas


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
    # Para añadir un módulo nuevo, descomentar y adaptar:
    # "ingresos": {
    #     "titulo": "Ingresos",
    #     "archivos": [{"id": "bd", "label": "BD Ingresos"}],
    #     "procesar": _procesar_ingresos,
    # },
}


def _tarjeta_modulo(clave, cfg):
    """Una tarjeta por módulo, con sus zonas de subida y botón."""
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

    return html.Div(
        [
            html.H4(cfg["titulo"],
                    style={"color": AZUL, "fontWeight": "700",
                           "marginBottom": "16px"}),
            *uploads,
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
    """Página de carga central: una tarjeta por módulo."""
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
        ]
    )


def registrar_callbacks_carga(app):

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
        State("store-sesion", "data"),
        prevent_initial_call=True,
    )
    def procesar_y_guardar(n_clicks_list, contents_all, ids_all, sesion):
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

        try:
            df = cfg["procesar"](contents_ordenados)
            admin = sesion.get("usuario", "admin")
            db.guardar_dataset(modulo, df, admin)
            salida[idx] = html.Div(
                [html.I(className="fas fa-circle-check me-2"),
                 f"Guardado correctamente: {len(df):,} registros."],
                style={"color": "#198754", "fontWeight": "600"})
        except Exception as e:
            salida[idx] = html.Div(
                ["Error al procesar: ", html.Pre(str(e))],
                style={"color": "#DC3545"})
        return salida