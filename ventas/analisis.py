"""
=========================================================
ANÁLISIS DEL DASHBOARD DE VENTAS
=========================================================

Todas las funciones de este módulo reciben un DataFrame
ya filtrado por Mes y Semana.

Regresan DataFrames listos para mostrarse en las tablas.
"""

import pandas as pd


# =========================================================
# COLUMNAS DEL REPORTE
# =========================================================
#
# NOTA (fix): "Usuario/Vendedor" no existe en ningún punto
# de procesamiento.py — la columna real del vendedor, tal
# como la deja procesar_bd_ventas(), es la cruda de Odoo:
# "Líneas de la orden de venta/Vendedor". Si se dejaba
# "Usuario/Vendedor", top_vendedores() tronaba con KeyError.

COL_VENDEDOR = "Líneas de la orden de venta/Vendedor"

COL_CLIENTE = "Asiento contable/Nombre del partner para mostrar en la factura."

COL_PRODUCTO = "Producto 2"

COL_CANTIDAD = "Líneas de la orden de venta/Cantidad facturada"

COL_VENTA = "Crédito"

COL_UTILIDAD = "Ut Bruta MN"


# =========================================================
# FORMATO GENERAL DE TABLAS
# =========================================================

def preparar_tabla(df):

    df = df.copy()

    df["Margen %"] = 0

    mascara = df["Venta"] != 0

    df.loc[mascara, "Margen %"] = (

        df.loc[mascara, "Utilidad Bruta"]

        /

        df.loc[mascara, "Venta"]

        * 100

    )

    df["Utilidad Unitaria"] = 0

    mascara = df["Cantidad"] != 0

    df.loc[mascara, "Utilidad Unitaria"] = (

        df.loc[mascara, "Utilidad Bruta"]

        /

        df.loc[mascara, "Cantidad"]

    )

    df = df.round(

        {

            "Cantidad":2,

            "Venta":2,

            "Utilidad Bruta":2,

            "Utilidad Unitaria":2,

            "Margen %":2

        }

    )

    return df


# =========================================================
# TOP VENDEDORES
# =========================================================

def top_vendedores(df):

    tabla = (

        df

        .groupby(

            COL_VENDEDOR,

            as_index=False

        )

        .agg(

            {

                COL_CANTIDAD:"sum",

                COL_VENTA:"sum",

                COL_UTILIDAD:"sum"

            }

        )

    )

    tabla.columns = [

        "Vendedor",

        "Cantidad",

        "Venta",

        "Utilidad Bruta"

    ]

    tabla = preparar_tabla(tabla)

    tabla = tabla.sort_values(

        "Venta",

        ascending=False

    )

    return tabla


# =========================================================
# TOP CLIENTES
# =========================================================

def top_clientes(df):

    tabla = (

        df

        .groupby(

            COL_CLIENTE,

            as_index=False

        )

        .agg(

            {

                COL_CANTIDAD:"sum",

                COL_VENTA:"sum",

                COL_UTILIDAD:"sum"

            }

        )

    )

    tabla.columns = [

        "Cliente",

        "Cantidad",

        "Venta",

        "Utilidad Bruta"

    ]

    tabla = preparar_tabla(tabla)

    tabla = tabla.sort_values(

        "Venta",

        ascending=False

    )

    return tabla


# =========================================================
# TOP PRODUCTOS
# =========================================================

def top_productos(df):

    tabla = (

        df

        .groupby(

            COL_PRODUCTO,

            as_index=False

        )

        .agg(

            {

                COL_CANTIDAD:"sum",

                COL_VENTA:"sum",

                COL_UTILIDAD:"sum"

            }

        )

    )

    tabla.columns = [

        "Producto",

        "Cantidad",

        "Venta",

        "Utilidad Bruta"

    ]

    tabla = preparar_tabla(tabla)

    tabla = tabla.sort_values(

        "Venta",

        ascending=False

    )

    return tabla


# =========================================================
# TOP FAMILIAS
# (Preparado para cuando exista la columna)
# =========================================================

def top_familias(df):

    columna = "Familia"

    if columna not in df.columns:

        return pd.DataFrame(

            columns=[

                "Familia",

                "Cantidad",

                "Venta",

                "Utilidad Bruta",

                "Utilidad Unitaria",

                "Margen %"

            ]

        )

    tabla = (

        df

        .groupby(

            columna,

            as_index=False

        )

        .agg(

            {

                COL_CANTIDAD:"sum",

                COL_VENTA:"sum",

                COL_UTILIDAD:"sum"

            }

        )

    )

    tabla.columns = [

        "Familia",

        "Cantidad",

        "Venta",

        "Utilidad Bruta"

    ]

    tabla = preparar_tabla(tabla)

    tabla = tabla.sort_values(

        "Venta",

        ascending=False

    )

    return tabla


# =========================================================
# DASHBOARD COMPLETO (tarjetas planas)
# =========================================================

def obtener_tablas_dashboard(df):

    return {

        "vendedores":top_vendedores(df),

        "productos":top_productos(df),

        "clientes":top_clientes(df),

        "familias":top_familias(df)

    }


# =========================================================
# ÁRBOL DE VENTAS: Vendedor > Cliente > Producto
#
# Para la tabla dinámica estilo Excel en AG Grid COMMUNITY
# (aggrid.py). Como rowGroup/treeData son funciones
# Enterprise, la jerarquía se arma manualmente aquí: cada
# fila del DataFrame de salida ES una fila del grid (de
# Vendedor, de Cliente o de Producto), ya con su subtotal
# calculado, su nivel, y su relación padre-hijo por id.
#
# Se asume que "df" ya llega con las columnas limpias:
# Vendedor, Cliente, Producto, Cantidad, Venta, Utilidad Bruta
# =========================================================

COLUMNAS_ORDEN_VALIDAS = [

    "Venta",

    "Utilidad Bruta",

    "Cantidad",

    "Margen %",

    "Utilidad Unitaria"

]

COLUMNAS_ARBOL = [

    "id",
    "parentId",
    "nivel",
    "concepto",
    "Cantidad",
    "Venta",
    "Utilidad Bruta",
    "Margen %",
    "Utilidad Unitaria",
    "tieneHijos",
    "expandido"

] + [

    f"_ruta_{metrica}" for metrica in COLUMNAS_ORDEN_VALIDAS

]


def _calcular_metricas(cantidad, venta, utilidad):

    """
    Margen % y Utilidad Unitaria NO se pueden sumar entre
    niveles (no son aditivos): se recalculan en cada nivel
    a partir de sus propios totales agregados.
    """

    margen = 0.0

    if venta != 0:

        margen = (utilidad / venta) * 100

    utilidad_unitaria = 0.0

    if cantidad != 0:

        utilidad_unitaria = utilidad / cantidad

    return margen, utilidad_unitaria


def _agregar_metricas_df(df):

    """
    Igual que _calcular_metricas, pero vectorizado sobre un
    DataFrame completo (Cantidad, Venta, Utilidad Bruta ya
    agregadas). Se necesita ANTES de ordenar, porque ahora
    se puede ordenar por Margen % o Utilidad Unitaria, no
    solo por Venta/Cantidad/Utilidad Bruta.
    """

    df = df.copy()

    df["Margen %"] = 0.0

    mascara = df["Venta"] != 0

    df.loc[mascara, "Margen %"] = (

        df.loc[mascara, "Utilidad Bruta"]

        /

        df.loc[mascara, "Venta"]

        * 100

    )

    df["Utilidad Unitaria"] = 0.0

    mascara = df["Cantidad"] != 0

    df.loc[mascara, "Utilidad Unitaria"] = (

        df.loc[mascara, "Utilidad Bruta"]

        /

        df.loc[mascara, "Cantidad"]

    )

    return df


def _agregar_rangos(df, columnas_grupo=None):

    """
    Para cada métrica ordenable, calcula el RANGO ascendente
    (0 = valor más chico) de cada fila dentro de su grupo de
    hermanos (columnas_grupo=None => rango global, entre TODOS
    los vendedores; columnas_grupo=["Vendedor"] => rango entre
    los clientes DE ESE vendedor; etc.)

    Este rango es la pieza base de la "ruta jerárquica" que
    arma cada fila (ver arbol_ventas): permite que un clic en
    el encabezado de la columna ordene de mayor a menor SIN
    romper la jerarquía, porque el orden entre hermanos nunca
    mezcla niveles distintos.
    """

    df = df.copy()

    for metrica in COLUMNAS_ORDEN_VALIDAS:

        columna_rango = f"rango_{metrica}"

        if columnas_grupo:

            df[columna_rango] = (

                df

                .groupby(columnas_grupo)[metrica]

                .rank(method="first", ascending=True)

            )

        else:

            df[columna_rango] = df[metrica].rank(

                method="first",

                ascending=True

            )

        df[columna_rango] = (

            df[columna_rango].astype(int) - 1

        )

    return df


def arbol_ventas(df, columna_orden="Venta"):

    """
    Recibe el DataFrame CRUDO de ventas (el mismo que usan
    top_vendedores/top_clientes/top_productos, con las
    columnas de Odoo: COL_VENDEDOR, COL_CLIENTE, COL_PRODUCTO,
    COL_CANTIDAD, COL_VENTA, COL_UTILIDAD). NO hace falta
    renombrarlo antes de llamar esta función; el renombrado
    a Vendedor/Cliente/Producto/Cantidad/Venta/Utilidad Bruta
    se hace aquí adentro.

    columna_orden: por cuál métrica ordenar, de mayor a menor,
    en LOS TRES niveles (Vendedor, Cliente dentro de cada
    Vendedor, Producto dentro de cada Cliente). Debe ser una
    de COLUMNAS_ORDEN_VALIDAS ("Venta", "Utilidad Bruta",
    "Cantidad", "Margen %", "Utilidad Unitaria"); si llega
    cualquier otro valor, se usa "Venta" por default.

    Regresa un DataFrame PLANO, ordenado en profundidad
    (Vendedor -> sus Clientes -> los Productos de cada
    Cliente), listo para pintarse tal cual en un AG Grid
    Community. Cada fila trae:

        id            str   identificador único de la fila
        parentId      str   id de la fila padre ("" en Vendedor)
        nivel         int   1=Vendedor, 2=Cliente, 3=Producto
        concepto      str   texto a mostrar, ya indentado
        Cantidad      float subtotal del nivel
        Venta         float subtotal del nivel
        Utilidad Bruta float subtotal del nivel
        Margen %      float recalculado en este nivel
        Utilidad Unitaria float recalculado en este nivel
        tieneHijos    bool  si se puede expandir
        expandido     bool  estado inicial (siempre False)

    Esta función SOLO arma la estructura completa; expandir/
    contraer (qué filas se muestran) lo resuelve el callback
    que ya tienes. Si te sirve, más abajo hay dos funciones
    de apoyo opcionales: total_general_arbol() y
    filas_visibles().
    """

    if columna_orden not in COLUMNAS_ORDEN_VALIDAS:

        columna_orden = "Venta"

    if df is None or len(df) == 0:

        return pd.DataFrame(columns=COLUMNAS_ARBOL)

    df = df.copy()

    # -----------------------------------------------
    # Renombrar de columnas crudas (Odoo) a nombres
    # amigables. Mismas constantes que usa el resto
    # del archivo (top_vendedores, top_clientes, etc.)
    # -----------------------------------------------

    mapa_columnas = {

        COL_VENDEDOR: "Vendedor",

        COL_CLIENTE: "Cliente",

        COL_PRODUCTO: "Producto",

        COL_CANTIDAD: "Cantidad",

        COL_VENTA: "Venta",

        COL_UTILIDAD: "Utilidad Bruta"

    }

    faltantes = [

        columna for columna in mapa_columnas

        if columna not in df.columns

    ]

    if faltantes:

        raise KeyError(

            "arbol_ventas: al DataFrame le faltan estas columnas: "

            + ", ".join(faltantes)

        )

    df = df.rename(columns=mapa_columnas)

    df = df[

        [

            "Vendedor",

            "Cliente",

            "Producto",

            "Cantidad",

            "Venta",

            "Utilidad Bruta"

        ]

    ]

    df["Vendedor"] = df["Vendedor"].fillna("Sin vendedor")

    df["Cliente"] = df["Cliente"].fillna("Sin cliente")

    df["Producto"] = df["Producto"].fillna("Sin producto")

    # -----------------------------------------------
    # Subtotales por nivel (de más fino a más grueso)
    # -----------------------------------------------

    productos = (

        df

        .groupby(

            ["Vendedor", "Cliente", "Producto"],

            as_index=False

        )

        .agg(

            {

                "Cantidad": "sum",

                "Venta": "sum",

                "Utilidad Bruta": "sum"

            }

        )

    )

    columnas_numericas = ["Cantidad", "Venta", "Utilidad Bruta"]

    productos[columnas_numericas] = productos[columnas_numericas].astype(float)

    productos = _agregar_metricas_df(productos)

    productos = _agregar_rangos(

        productos,

        columnas_grupo=["Vendedor", "Cliente"]

    )

    clientes = (

        productos

        .groupby(

            ["Vendedor", "Cliente"],

            as_index=False

        )

        .agg(

            {

                "Cantidad": "sum",

                "Venta": "sum",

                "Utilidad Bruta": "sum"

            }

        )

    )

    clientes = _agregar_metricas_df(clientes)

    clientes = _agregar_rangos(

        clientes,

        columnas_grupo=["Vendedor"]

    )

    vendedores = (

        clientes

        .groupby(

            "Vendedor",

            as_index=False

        )

        .agg(

            {

                "Cantidad": "sum",

                "Venta": "sum",

                "Utilidad Bruta": "sum"

            }

        )

    )

    vendedores = _agregar_metricas_df(vendedores)

    vendedores = _agregar_rangos(vendedores)

    vendedores = vendedores.sort_values(

        columna_orden,

        ascending=False

    )

    # -----------------------------------------------
    # Armar filas planas, en profundidad
    #
    # OPTIMIZACIÓN: antes, por cada vendedor se filtraba y
    # ordenaba "clientes" desde cero, y por cada cliente se
    # filtraba y ordenaba "productos" desde cero (además de
    # usar .iterrows(), que es lento). Con muchos vendedores/
    # clientes eso se nota mucho al dar clic. Ahora:
    #
    #  1. Se ordena clientes/productos UNA sola vez (no una
    #     vez por cada padre).
    #  2. Se llama a .to_dict("records") UNA sola vez sobre
    #     TODO el DataFrame ya ordenado (no una vez por cada
    #     grupo chiquito: eso se probó y resultó MÁS lento,
    #     porque to_dict tiene un costo fijo por llamada que
    #     se multiplica por miles de grupos pequeños).
    #  3. Se agrupan esos registros en un dict de listas con
    #     un solo loop de Python puro (sin overhead de pandas).
    # -----------------------------------------------

    clientes_por_vendedor = {}

    for registro in (

        clientes

        .sort_values(columna_orden, ascending=False)

        .to_dict("records")

    ):

        clientes_por_vendedor.setdefault(

            registro["Vendedor"],

            []

        ).append(registro)

    productos_por_cliente = {}

    for registro in (

        productos

        .sort_values(columna_orden, ascending=False)

        .to_dict("records")

    ):

        productos_por_cliente.setdefault(

            (registro["Vendedor"], registro["Cliente"]),

            []

        ).append(registro)

    # -----------------------------------------------
    # OPTIMIZACIÓN (la que realmente pesaba con volumen
    # grande): antes se armaba un dict NUEVO por cada una de
    # las ~96,000 filas, con "**{...}" para meterle las 5
    # rutas — cada dict-comprehension + unpacking tiene su
    # propio costo, multiplicado por 96,000 se sentía mucho
    # (medido con cProfile: ~1.25s solo en Python puro, sin
    # contar pandas). Ahora se llenan LISTAS por columna con
    # .append() (mucho más barato que crear un dict por fila),
    # y el DataFrame se arma UNA sola vez al final.
    # -----------------------------------------------

    col_id = []
    col_parent_id = []
    col_nivel = []
    col_concepto = []
    col_cantidad = []
    col_venta = []
    col_utilidad = []
    col_margen = []
    col_ut_unitaria = []
    col_tiene_hijos = []
    col_expandido = []

    col_rutas = {

        metrica: []

        for metrica in COLUMNAS_ORDEN_VALIDAS

    }

    def _agregar_fila(

        id_fila,

        parent_id,

        nivel,

        concepto,

        cantidad,

        venta,

        utilidad,

        margen,

        ut_unitaria,

        tiene_hijos,

        ruta

    ):

        col_id.append(id_fila)

        col_parent_id.append(parent_id)

        col_nivel.append(nivel)

        col_concepto.append(concepto)

        col_cantidad.append(cantidad)

        col_venta.append(venta)

        col_utilidad.append(utilidad)

        col_margen.append(margen)

        col_ut_unitaria.append(ut_unitaria)

        col_tiene_hijos.append(tiene_hijos)

        col_expandido.append(False)

        for metrica in COLUMNAS_ORDEN_VALIDAS:

            col_rutas[metrica].append(ruta[metrica])

    for fila_v in vendedores.to_dict("records"):

        vendedor = fila_v["Vendedor"]

        id_vendedor = f"v::{vendedor}"

        rutas_v = {

            metrica: [int(fila_v[f"rango_{metrica}"])]

            for metrica in COLUMNAS_ORDEN_VALIDAS

        }

        _agregar_fila(

            id_vendedor,

            "",

            1,

            str(vendedor),

            fila_v["Cantidad"],

            fila_v["Venta"],

            fila_v["Utilidad Bruta"],

            fila_v["Margen %"],

            fila_v["Utilidad Unitaria"],

            True,

            rutas_v

        )

        for fila_c in clientes_por_vendedor.get(vendedor, []):

            cliente = fila_c["Cliente"]

            id_cliente = f"{id_vendedor}||c::{cliente}"

            rutas_c = {

                metrica: rutas_v[metrica] + [int(fila_c[f"rango_{metrica}"])]

                for metrica in COLUMNAS_ORDEN_VALIDAS

            }

            _agregar_fila(

                id_cliente,

                id_vendedor,

                2,

                str(cliente),

                fila_c["Cantidad"],

                fila_c["Venta"],

                fila_c["Utilidad Bruta"],

                fila_c["Margen %"],

                fila_c["Utilidad Unitaria"],

                True,

                rutas_c

            )

            for fila_p in productos_por_cliente.get((vendedor, cliente), []):

                producto = fila_p["Producto"]

                id_producto = f"{id_cliente}||p::{producto}"

                rutas_p = {

                    metrica: rutas_c[metrica] + [int(fila_p[f"rango_{metrica}"])]

                    for metrica in COLUMNAS_ORDEN_VALIDAS

                }

                _agregar_fila(

                    id_producto,

                    id_cliente,

                    3,

                    str(producto),

                    fila_p["Cantidad"],

                    fila_p["Venta"],

                    fila_p["Utilidad Bruta"],

                    fila_p["Margen %"],

                    fila_p["Utilidad Unitaria"],

                    False,

                    rutas_p

                )

    datos_columnas = {

        "id": col_id,

        "parentId": col_parent_id,

        "nivel": col_nivel,

        "concepto": col_concepto,

        "Cantidad": col_cantidad,

        "Venta": col_venta,

        "Utilidad Bruta": col_utilidad,

        "Margen %": col_margen,

        "Utilidad Unitaria": col_ut_unitaria,

        "tieneHijos": col_tiene_hijos,

        "expandido": col_expandido

    }

    for metrica in COLUMNAS_ORDEN_VALIDAS:

        datos_columnas[f"_ruta_{metrica}"] = col_rutas[metrica]

    return pd.DataFrame(datos_columnas, columns=COLUMNAS_ARBOL)


def comparador_jerarquico(campo_ruta, profundidad=0, profundidad_max=3):

    """
    Genera, como texto, una expresión JS (sin sentencias: solo
    ternarios anidados, para que dash-ag-grid la acepte como
    función válida) que compara dos filas del árbol usando su
    "ruta jerárquica" (campo_ruta, p.ej. "_ruta_Venta") en vez
    del valor crudo de la columna.

    Por qué: el comparator nativo de AG Grid recibe
    (valueA, valueB, nodeA, nodeB, isDescending). Si comparamos
    valueA/valueB directamente, se mezclan vendedor/cliente/
    producto por valor y se rompe la jerarquía visual. Al
    comparar la ruta [rango_vendedor, rango_cliente, rango_
    producto] en vez del valor, un ancestro SIEMPRE queda antes
    que sus descendientes (sin importar el sentido del clic), y
    entre hermanos del mismo nivel sí respeta isDescending.
    """

    ref_a = f"nodeA.data['{campo_ruta}']"

    ref_b = f"nodeB.data['{campo_ruta}']"

    if profundidad >= profundidad_max:

        return "0"

    a_i = f"{ref_a}[{profundidad}]"

    b_i = f"{ref_b}[{profundidad}]"

    diferencia = f"(isDescending ? ({b_i} - {a_i}) : ({a_i} - {b_i}))"

    siguiente_nivel = comparador_jerarquico(

        campo_ruta,

        profundidad + 1,

        profundidad_max

    )

    return (

        f"({ref_a}.length <= {profundidad} || {ref_b}.length <= {profundidad}) "

        f"? ({ref_a}.length - {ref_b}.length) "

        f": ({a_i} !== {b_i} ? {diferencia} : {siguiente_nivel})"

    )


# =========================================================
# TOTAL GENERAL (opcional)
#
# Para usarse como pinnedBottomRowData en AG Grid: los
# renglones "fijos" (pinned) SÍ son una función de AG Grid
# Community, no requieren Enterprise.
# =========================================================

def total_general_arbol(df):

    """
    Recibe el mismo DataFrame CRUDO que arbol_ventas() (con
    las columnas COL_VENTA / COL_UTILIDAD / COL_CANTIDAD de
    Odoo), no uno ya renombrado.
    """

    if df is None or len(df) == 0:

        cantidad = venta = utilidad = 0.0

    else:

        cantidad = float(df[COL_CANTIDAD].sum())

        venta = float(df[COL_VENTA].sum())

        utilidad = float(df[COL_UTILIDAD].sum())

    margen, ut_unit = _calcular_metricas(cantidad, venta, utilidad)

    return {

        "id": "total",

        "parentId": "",

        "nivel": 0,

        "concepto": "TOTAL GENERAL",

        "Cantidad": cantidad,

        "Venta": venta,

        "Utilidad Bruta": utilidad,

        "Margen %": margen,

        "Utilidad Unitaria": ut_unit,

        "tieneHijos": False,

        "expandido": False

    }


# =========================================================
# FILAS VISIBLES SEGÚN EXPANSIÓN (opcional)
#
# Ayudante por si tu callback de expandir/contraer quiere
# resolverlo así: recibe el árbol completo de arbol_ventas()
# y el conjunto de ids actualmente expandidos, y regresa
# solo las filas que deben pintarse en el grid. Si tu
# callback ya lo resuelve distinto, esta función se ignora
# sin problema: arbol_ventas() no depende de ella.
# =========================================================

def filas_visibles(df_arbol, ids_expandidos):

    if df_arbol is None or len(df_arbol) == 0:

        return df_arbol

    ids_expandidos = set(ids_expandidos or [])

    padres = dict(

        zip(

            df_arbol["id"],

            df_arbol["parentId"]

        )

    )

    def es_visible(fila_id, nivel):

        if nivel == 1:

            return True

        padre = padres.get(fila_id, "")

        if padre == "" or padre not in ids_expandidos:

            return False

        return es_visible(padre, nivel - 1)

    mascara = df_arbol.apply(

        lambda fila: es_visible(

            fila["id"],

            fila["nivel"]

        ),

        axis=1

    )

    resultado = df_arbol[mascara].reset_index(drop=True)

    # -----------------------------------------------
    # BUG corregido: "expandido" siempre quedaba en False
    # en el árbol base (arbol_ventas no sabe qué está
    # expandido), así que el ícono nunca cambiaba a ▼. Se
    # actualiza aquí, que es donde sí se conoce el estado
    # real de expansión.
    # -----------------------------------------------

    resultado["expandido"] = resultado["id"].isin(ids_expandidos)

    # -----------------------------------------------
    # Indentación + ícono ▶/▼, HORNEADOS en el texto de
    # "concepto" (no vía cellRenderer en JS). Por qué: si el
    # ícono depende de leer OTRO campo aparte (como antes,
    # vía JS), AG Grid a veces no vuelve a dibujar la celda
    # cuando solo se actualiza "rowData" (porque el VALOR de
    # la celda "concepto" en sí no había cambiado). Horneando
    # el ícono directo en el texto, el valor de la celda SÍ
    # cambia cuando cambia "expandido", así que el refresco
    # ligero de rowData (sin reconstruir todo el grid) vuelve
    # a funcionar bien.
    # -----------------------------------------------

    def _texto_visual(fila):

        sangria = "\u00a0" * (fila["nivel"] * 6)

        if fila["tieneHijos"]:

            icono = "▼ " if fila["expandido"] else "▶ "

        elif fila["nivel"] > 0:

            icono = "\u00a0\u00a0\u00a0"

        else:

            icono = ""

        return sangria + icono + str(fila["concepto"])

    resultado["concepto"] = resultado.apply(_texto_visual, axis=1)

    return resultado