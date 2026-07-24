"""
=========================================================
core/columnas.py
=========================================================
FUENTE ÚNICA DE VERDAD de los nombres de columna.

Antes, los mismos strings ("Crédito", "Ut Bruta MN",
"Asiento contable/Fecha de factura", "Mes", "Semana", ...)
estaban tecleados sueltos en procesamiento.py, kpis.py,
analisis.py, callbacks.py y filtros.py. Aquí viven en UN
solo lugar. El resto del proyecto los importa desde aquí.

NOTA: los valores son EXACTAMENTE los que el código ya
usaba. Este archivo no cambia ningún string; solo les da
un hogar único.
"""

# =========================================================
# COLUMNAS CRUDAS DE ODOO (tal como llegan en el Excel)
# =========================================================

RAW_FECHA_FACTURA = "Asiento contable/Fecha de factura"
RAW_VENDEDOR = "Líneas de la orden de venta/Vendedor"
RAW_CLIENTE = "Asiento contable/Nombre del partner para mostrar en la factura."
RAW_CANTIDAD = "Líneas de la orden de venta/Cantidad facturada"
RAW_PRODUCTO_COD = "Líneas de la orden de venta/Producto"
RAW_PRECIO = "Líneas de la orden de venta/Precio unitario"
RAW_COSTO = "Líneas de la orden de venta/Costo"
RAW_DIVISA = "Líneas de la orden de venta/Divisa"
RAW_CREDITO = "Crédito"

# =========================================================
# COLUMNAS DERIVADAS (las crea procesamiento.py)
# =========================================================

# Comunes a TODAS las hojas BD (Ventas, Cobranza, Cartera,
# CxP): por eso viven en core y no en ventas/.
MES = "Mes"
SEMANA = "Semana"

PRODUCTO_2 = "Producto 2"       # descripción de producto desde el catálogo
UT_BRUTA = "Ut Bruta MN"
COSTO_VENTA = "Costo Venta MN"
TC = "TC"

# =========================================================
# NOMBRES "AMIGABLES" DE LAS TABLAS / ÁRBOL
# =========================================================

VENDEDOR = "Vendedor"
CLIENTE = "Cliente"
PRODUCTO = "Producto"
CANTIDAD = "Cantidad"
VENTA = "Venta"
UTILIDAD_BRUTA = "Utilidad Bruta"
MARGEN = "Margen %"
UTILIDAD_UNITARIA = "Utilidad Unitaria"

# =========================================================
# MAPA: dimensión amigable -> columna cruda de Odoo
#
# Lo usa el motor del árbol para saber, dada una lista de
# niveles como ["Producto", "Cliente"], qué columna cruda
# leer de la BD para cada uno.
# =========================================================

DIMENSION_A_RAW = {
    VENDEDOR: RAW_VENDEDOR,
    CLIENTE: RAW_CLIENTE,
    PRODUCTO: PRODUCTO_2,   # el producto "amigable" es la descripción del catálogo
}