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
from saldo_proveedor.procesamiento import leer_archivo as leer_saldo_prov

# Lectores de la BD CRUDA (hoja tal cual) para el reporte descargable.
# Cada uno devuelve el DataFrame con TODAS las columnas originales.
from ingresos.procesamiento import leer_excel as crudo_ingresos
from cartera.procesamiento import leer_excel as crudo_cartera
from saldo_proveedor.procesamiento import leer_excel as crudo_saldo_prov

# Para ventas leemos la hoja "BD Ventas" del archivo bd directamente.
import base64 as _b64
import io as _io
import pandas as _pd


def _crudo_ventas(contents):
    if contents is None:
        return None
    data = _b64.b64decode(contents.split(",")[1])
    xls = _pd.ExcelFile(_io.BytesIO(data))
    hoja = "BD Ventas" if "BD Ventas" in xls.sheet_names else xls.sheet_names[0]
    return _pd.read_excel(xls, sheet_name=hoja)


def crudo_ventas(contents):
    """BD Ventas cruda (para procesar y para el reporte)."""
    return _crudo_ventas(contents)


def crudo_ventas_catalogo(contents):
    """Catálogo crudo (primera hoja del archivo de catálogo)."""
    if contents is None:
        return None
    data = _b64.b64decode(contents.split(",")[1])
    xls = _pd.ExcelFile(_io.BytesIO(data))
    hoja = "Catalogo" if "Catalogo" in xls.sheet_names else xls.sheet_names[0]
    return _pd.read_excel(xls, sheet_name=hoja)


# módulo -> (id del archivo que trae la BD, función lectora del crudo)
_CRUDO_LECTORES = {
    "ventas": ("bd", _crudo_ventas),
    "ingresos": ("bd", crudo_ingresos),
    "cartera": ("bd", crudo_cartera),
    "saldo_proveedor": ("bd", crudo_saldo_prov),
}

AZUL = "#173C73"
DORADO = "#D4AF37"


# --- adaptadores de procesado por módulo ---
# Reciben la lista de 'contents' (en el orden de 'archivos').
# Los módulos con pide_fecha reciben además 'fecha' (str ISO).

def _procesar_ventas(contents_list, fecha=None):
    # Orden de 'archivos': [catalogo (opcional), bd]
    catalogo, ventas = contents_list

    if catalogo is not None:
        # Se subió catálogo: se usa y se GUARDA para la próxima vez.
        df_cat = crudo_ventas_catalogo(catalogo)
        if df_cat is not None and len(df_cat):
            try:
                db.guardar_crudo("catalogo_ventas", df_cat)
            except Exception as ec:
                print(f">>> [CAT] No se pudo guardar el catálogo: {ec}", flush=True)
    else:
        # No se subió: usar el ÚLTIMO catálogo guardado en Supabase.
        try:
            df_cat = db.leer_crudo("catalogo_ventas")
        except Exception:
            df_cat = None
        if df_cat is None or len(df_cat) == 0:
            raise Exception(
                "No subiste el Catálogo y no hay uno guardado. "
                "Sube el Catálogo al menos la primera vez.")

    # procesar la BD de ventas con el catálogo (subido o recuperado)
    df_ventas_cruda = crudo_ventas(ventas)
    from ventas.procesamiento import procesar_bd_ventas
    return procesar_bd_ventas(df_cat, df_ventas_cruda)


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
    # Un solo archivo (BD Cartera ya formulada). Ya NO se pide
    # fecha de corte: la BD trae su columna Fecha y su aging.
    (bd,) = contents_list
    return leer_cartera(bd)


def _procesar_saldo_proveedor(contents_list, fecha=None):
    # Un solo archivo (BD CxP ya formulada). Sin fecha de corte.
    (bd,) = contents_list
    return leer_saldo_prov(bd)


# --- CATÁLOGO DE MÓDULOS ---
MODULOS_CARGA = {
    "ventas": {
        "titulo": "Ventas",
        "archivos": [
            {"id": "catalogo", "label": "Catálogo (opcional)", "opcional": True},
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
    },
    "saldo_proveedor": {
        "titulo": "Saldo Proveedor",
        "archivos": [
            {"id": "bd", "label": "BD CxP"},
        ],
        "procesar": _procesar_saldo_proveedor,
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

        # Validar que estén todos los OBLIGATORIOS (los marcados
        # como "opcional" pueden faltar; ej. el Catálogo de Ventas).
        obligatorios = [a["id"] for a in cfg["archivos"] if not a.get("opcional")]
        faltan = [a for a in obligatorios if not por_archivo.get(a)]
        if faltan:
            salida[idx] = html.Div(
                "Falta seleccionar: " + ", ".join(faltan),
                style={"color": "#DC3545"})
            return salida

        # contents en el orden de 'archivos' (los opcionales que no
        # se subieron van como None)
        contents_ordenados = [por_archivo.get(a) for a in orden]

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

            # Guardar además la BD CRUDA (todas las columnas) para
            # poder regenerar el reporte Excel con dinámicas vivas.
            if modulo in _CRUDO_LECTORES:
                try:
                    file_id, lector = _CRUDO_LECTORES[modulo]
                    contents_bd = por_archivo.get(file_id)
                    if contents_bd is not None:
                        df_crudo = lector(contents_bd)
                        if df_crudo is not None and len(df_crudo):
                            db.guardar_crudo(modulo, df_crudo)
                except Exception as ec:
                    print(f">>> [CRUDO] No se pudo guardar crudo de {modulo}: {ec}",
                          flush=True)

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