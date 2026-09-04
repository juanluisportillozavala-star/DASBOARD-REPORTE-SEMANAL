"""
=========================================================
bsc/catalogo.py  —  FUENTE DE VERDAD de los indicadores BSC
=========================================================
Todo el módulo BSC se arma leyendo esta lista. Para agregar,
quitar o reclasificar un indicador, se edita AQUÍ (un solo
lugar) y el resto (captura, tabla, semáforo) se ajusta solo.

Cada indicador es un dict con estos campos:

  id          Llave estable (no cambiar; se usa en la base).
  nombre      Texto que se muestra.
  nivel       0 = principal, 1 = sub-indicador (se indenta).
  grupo       Dueño/área: Comercial, Administración,
              Operaciones, Global.
  unidad      "$"  -> dinero
              "Días" -> días
              "%"  -> porcentaje
  tipo        "flujo" -> acumulado del mes = SUMA de semanas
                          (Venta, Utilidad, Ingreso…)
              "saldo" -> acumulado = ÚLTIMA semana capturada
                          (Cartera, Saldo proveedor, Días…)
  sentido     "mayor" -> más es mejor (Venta, Utilidad, Bancos)
              "menor" -> menos es mejor (Días, Vencido, Gastos)
  capturable  True  -> se teclea en la pantalla de captura.
              False -> se CALCULA (los padres que suman hijos).
  suma_hijos  True  -> su acumulado = suma del acumulado de sus
                       hijos (padre = total de sus sub-filas).
  padre       id del indicador padre (para los hijos), o None.
  fuente      "manual" en la Fase 1. En la Fase 2 se cambiará a
              "auto:ventas", "auto:cartera", etc. para que jale
              el dato del módulo correspondiente sin teclear.

NOTA: los nombres de vendedor deben coincidir con db.VENDEDORES
      (ILSE GARCÍA, FREDY SALAS, MATEO LÓPEZ). Si cambian allá,
      cambiarlos también aquí.
"""

VENDEDORES = ["Ilse García", "Fredy Salas", "Mateo López"]

# claves cortas y estables para los ids de vendedor
_VEND_ID = {"Ilse García": "ilse", "Fredy Salas": "fredy", "Mateo López": "mateo"}


def _hijos_vendedor(padre_id, grupo, fuente="manual"):
    """Genera las 3 sub-filas por vendedor de un indicador padre."""
    filas = []
    for v in VENDEDORES:
        filas.append({
            "id": f"{padre_id}_{_VEND_ID[v]}",
            "nombre": v, "nivel": 1, "grupo": grupo, "unidad": "$",
            "tipo": "flujo", "sentido": "mayor", "capturable": True,
            "suma_hijos": False, "padre": padre_id, "fuente": fuente,
        })
    return filas


# =========================================================
# LISTA DE INDICADORES (en el orden en que se muestran)
# =========================================================

def _construir():
    """Orden EXACTO de la hoja '2026 Objetivos' del Excel, fila por
    fila, sin saltar ni reordenar nada."""
    L = []

    def add(iid, nombre, nivel, grupo, unidad, tipo, sentido,
            capturable, suma_hijos, padre, fuente="manual", **extra):
        d = {"id": iid, "nombre": nombre, "nivel": nivel, "grupo": grupo,
             "unidad": unidad, "tipo": tipo, "sentido": sentido,
             "capturable": capturable, "suma_hijos": suma_hijos,
             "padre": padre, "fuente": fuente}
        d.update(extra)
        L.append(d)

    # 3  Venta ($)
    add("venta", "Venta ($)", 0, "Comercial", "$", "flujo", "mayor",
        False, True, None)
    # 4-6  vendedores (auto:ventas)
    for v in VENDEDORES:
        add(f"venta_{_VEND_ID[v]}", v, 1, "Comercial", "$", "flujo",
            "mayor", True, False, "venta", fuente="auto:ventas")

    # 7  Utilidad bruta ($)
    add("utilidad", "Utilidad bruta ($)", 0, "Comercial", "$", "flujo",
        "mayor", False, True, None)
    for v in VENDEDORES:
        add(f"utilidad_{_VEND_ID[v]}", v, 1, "Comercial", "$", "flujo",
            "mayor", True, False, "utilidad", fuente="auto:ventas")

    # 11  Gastos de operación
    add("gastos_op", "Gastos de operación ($)", 0, "Administración", "$",
        "flujo", "menor", True, False, None)
    # 12  Ut. Operativa ($)
    add("ut_operativa", "Ut. Operativa ($)", 0, "Comercial", "$", "flujo",
        "mayor", True, False, None)

    # 13  Cartera clientes ($)
    add("cartera", "Cartera clientes ($)", 0, "Administración", "$",
        "saldo", "menor", False, True, None)
    add("cartera_corr", "Al corriente ($)", 1, "Administración", "$",
        "saldo", "mayor", True, False, "cartera")
    add("cartera_venc", "Vencido ($)", 1, "Administración", "$",
        "saldo", "menor", True, False, "cartera")
    # 16  Días cartera
    add("dias_cartera", "Días cartera", 0, "Administración", "Días",
        "saldo", "menor", True, False, None)

    # 17  Ingreso ($)  -> vendedor -> corriente/vencida/contado
    add("ingreso", "Ingreso ($)", 0, "Administración", "$", "flujo",
        "mayor", False, True, None)
    _sub = [("corr", "Cobranza al corriente"),
            ("venc", "Cobranza vencida"),
            ("cont", "Contado")]
    for v in VENDEDORES:
        vid = f"ingreso_{_VEND_ID[v]}"
        add(vid, v, 1, "Administración", "$", "flujo", "mayor",
            False, True, "ingreso")
        for suf, nom in _sub:
            add(f"{vid}_{suf}", nom, 2, "Administración", "$", "flujo",
                "mayor", True, False, vid)

    # 30  Costo Inventario $
    add("costo_inv", "Costo Inventario $", 0, "Operaciones", "$",
        "saldo", "menor", False, True, None)
    add("inventario", "Inventario", 1, "Operaciones", "$", "saldo",
        "menor", True, False, "costo_inv")
    add("sobrestock", "Sobrestock", 1, "Operaciones", "$", "saldo",
        "menor", True, False, "costo_inv")
    # 33  Días inventario (acumulado)
    add("dias_inventario", "Días inventario (acumulado)", 0, "Operaciones",
        "Días", "saldo", "menor", True, False, None)

    # 34  Saldo proveedores ($)
    add("saldo_prov", "Saldo proveedores ($)", 0, "Administración", "$",
        "saldo", "menor", False, True, None)
    add("prov_corr", "Al corriente ($)", 1, "Administración", "$",
        "saldo", "mayor", True, False, "saldo_prov")
    add("prov_venc", "Vencido ($)", 1, "Administración", "$",
        "saldo", "menor", True, False, "saldo_prov")
    # 37  Días proveedor
    add("dias_proveedor", "Días proveedor", 0, "Administración", "Días",
        "saldo", "mayor", True, False, None)
    # 38  Ciclo efectivo (fórmula: dias_inv - dias_prov + dias_cartera)
    add("ciclo_efectivo", "Ciclo efectivo", 0, "Administración", "Días",
        "saldo", "menor", False, False, None, fuente="formula:ciclo")
    # 39  Bancos (objetivo anual tecleado)
    add("bancos", "Bancos", 0, "Administración", "$", "saldo", "mayor",
        True, False, None, anual_manual=True)
    # 40  Capital de trabajo ($) (objetivo anual tecleado)
    add("capital_trabajo", "Capital de trabajo  ($)", 0, "Administración",
        "$", "saldo", "mayor", True, False, None, anual_manual=True)

    return L


_INDICADORES = _construir()

# orden fijo de los grupos (para mostrar la tabla por dueño)
GRUPOS = ["Comercial", "Administración", "Operaciones", "Global"]


def indicadores():
    """Lista completa de indicadores (copia, en orden de despliegue)."""
    return [dict(i) for i in _INDICADORES]


def capturables():
    """Solo los indicadores que se teclean en la pantalla de
    captura (excluye los padres que se calculan por suma)."""
    return [dict(i) for i in _INDICADORES if i["capturable"]]


def por_id(iid):
    for i in _INDICADORES:
        if i["id"] == iid:
            return dict(i)
    return None


def hijos_de(padre_id):
    return [dict(i) for i in _INDICADORES if i["padre"] == padre_id]