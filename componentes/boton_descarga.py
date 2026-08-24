"""
Botón reutilizable para descargar el REPORTE en Excel (con las
tablas dinámicas vivas). Es un enlace a la ruta Flask
/descargar-reporte, así que no necesita callback.

Uso en cualquier layout:
    from componentes.boton_descarga import boton_descargar_reporte
    ...
    boton_descargar_reporte(),
"""

from dash import html

AZUL = "#173C73"
DORADO = "#D4AF37"


def boton_descargar_reporte(modulo=None, texto="Descargar Excel"):
    """Enlace-botón a /descargar-reporte. Si se pasa 'modulo'
    (ventas/ingresos/cartera/saldo_proveedor), el Excel se descarga
    con solo la pestaña de ese módulo visible."""
    href = "/descargar-reporte"
    if modulo:
        href += f"?modulo={modulo}"
    return html.A(
        [html.I(className="fas fa-file-excel me-2"), texto],
        href=href,
        download="Reporte_Liderza.xlsx",
        target="_blank",
        style={
            "display": "inline-flex",
            "alignItems": "center",
            "backgroundColor": AZUL,
            "color": "#FFFFFF",
            "textDecoration": "none",
            "padding": "10px 18px",
            "borderRadius": "8px",
            "fontWeight": "600",
            "border": f"2px solid {DORADO}",
            "boxShadow": "0 2px 6px rgba(0,0,0,0.12)",
        },
        title="Descarga el reporte en Excel con las tablas dinámicas actualizadas",
    )