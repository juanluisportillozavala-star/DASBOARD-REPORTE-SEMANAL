"""
=========================================================
ventas/tabla_producto_cliente.py
=========================================================
Tabla dinámica jerárquica Producto > Cliente.

Módulo AUTOCONTENIDO: trae su layout y sus callbacks, y se
enchufa sin tocar la tabla actual (Vendedor>Cliente>Producto),
que sigue intacta. Reutiliza:
  • core.arbol    -> motor jerárquico + filas_visibles
  • ventas.aggrid -> mismo dibujo AG Grid que la tabla actual
  • ventas.filtros -> mismo filtro Mes/Semana

IDs propios (sufijo -pc) para no chocar con la tabla actual.
"""

from dash import Input, Output, State, html, dcc, no_update
import pandas as pd

from ventas.filtros import filtrar_dataframe
from ventas.aggrid import (
    crear_aggrid, crear_encabezado_periodo,
    configuracion_tamano, estilo_grid, opciones_grid,
)
from core.arbol import construir_arbol, total_general, filas_visibles


# Niveles de ESTA tabla. Para las otras dos tablas, este es
# literalmente el único valor que cambia.
NIVELES = ["Producto", "Cliente"]

# IDs propios de esta tabla
ID_GRID = "tabla-ventas-pc"
ID_CONTENEDOR = "contenedor-tabla-pc"
ID_STORE_ARBOL = "store-arbol-pc"
ID_STORE_TOTAL = "store-total-pc"
ID_STORE_EXPANDIDO = "store-expandido-pc"


def crear_layout_tabla_pc():
    """Contenedor + stores propios de la tabla Producto/Cliente."""
    return html.Div(
        [
            dcc.Store(id=ID_STORE_ARBOL, data=None),
            dcc.Store(id=ID_STORE_TOTAL, data=None),
            dcc.Store(id=ID_STORE_EXPANDIDO, data=[]),
            html.H4(
                "Producto / Cliente",
                style={"color": "#173C73", "fontWeight": "700",
                       "marginTop": "10px", "marginBottom": "12px"},
            ),
            html.Div(id=ID_CONTENEDOR),
        ]
    )


def registrar_callbacks_tabla_pc(app):

    # 1) Construir la tabla cuando cambian datos o filtro
    @app.callback(
        Output(ID_CONTENEDOR, "children"),
        Output(ID_STORE_ARBOL, "data"),
        Output(ID_STORE_TOTAL, "data"),
        Input("store-bd-ventas", "data"),
        Input("store-mes", "data"),
        Input("store-semana", "data"),
        State(ID_STORE_EXPANDIDO, "data"),
    )
    def construir(data, meses, semanas, ids_expandidos):
        if data is None:
            return (
                html.Div("Procesa un archivo para ver la tabla.",
                         style={"color": "#6C757D"}),
                None, None,
            )
        try:
            df = pd.DataFrame(data)
            df_f = filtrar_dataframe(df, meses=meses, semanas=semanas)

            arbol = construir_arbol(df_f, niveles=NIVELES)
            total = total_general(df_f)

            col_fecha = "Asiento contable/Fecha de factura"
            fecha_corte = "N/D"
            if col_fecha in df_f.columns and len(df_f) > 0:
                fmax = pd.to_datetime(df_f[col_fecha], errors="coerce").max()
                if pd.notna(fmax):
                    fecha_corte = fmax.strftime("%d/%m/%Y")
            semanas_txt = (
                ", ".join(str(s) for s in sorted(semanas)) if semanas else "Todas"
            )

            visibles = filas_visibles(arbol, ids_expandidos or [])
            contenido = html.Div([
                crear_encabezado_periodo(fecha_corte, semanas_txt),
                crear_aggrid(visibles, fila_total=total, id_grid=ID_GRID),
            ])
            return contenido, arbol.to_dict("records"), total
        except Exception as e:
            return (
                html.Div([html.H3("ERROR"), html.Pre(str(e))],
                         style={"color": "red"}),
                None, None,
            )

    # 2) Refresco ligero al expandir/contraer
    @app.callback(
        Output(ID_GRID, "rowData"),
        Output(ID_GRID, "style"),
        Output(ID_GRID, "dashGridOptions"),
        Input(ID_STORE_EXPANDIDO, "data"),
        State(ID_STORE_ARBOL, "data"),
        State(ID_STORE_TOTAL, "data"),
        prevent_initial_call=True,
    )
    def refrescar(ids_expandidos, arbol_data, total):
        if arbol_data is None:
            return no_update, no_update, no_update
        arbol = pd.DataFrame(arbol_data)
        visibles = filas_visibles(arbol, ids_expandidos or [])
        extra, alto = configuracion_tamano(len(visibles), hay_total=bool(total))
        pinned = [total] if total else None
        return (
            visibles.to_dict("records"),
            estilo_grid(alto),
            opciones_grid(pinned, extra),
        )

    # 3) Expandir/contraer al hacer clic
    @app.callback(
        Output(ID_STORE_EXPANDIDO, "data"),
        Input(ID_GRID, "cellClicked"),
        State(ID_STORE_EXPANDIDO, "data"),
        prevent_initial_call=True,
    )
    def alternar(celda, ids_expandidos):
        if celda is None:
            return no_update
        fila_id = celda.get("rowId")
        if fila_id is None:
            return no_update
        # hoja (último nivel) no se expande: con N niveles, el
        # último tiene (N-1) separadores "||".
        if fila_id.count("||") >= len(NIVELES) - 1:
            return no_update
        ids = set(ids_expandidos or [])
        if fila_id in ids:
            ids.discard(fila_id)
        else:
            ids.add(fila_id)
        return sorted(ids)