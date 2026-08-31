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
    L = []

    # ---------- COMERCIAL ----------
    L.append({"id": "venta", "nombre": "Venta ($)", "nivel": 0,
              "grupo": "Comercial", "unidad": "$", "tipo": "flujo",
              "sentido": "mayor", "capturable": False, "suma_hijos": True,
              "padre": None, "fuente": "manual"})
    L += _hijos_vendedor("venta", "Comercial")

    L.append({"id": "utilidad", "nombre": "Utilidad bruta ($)", "nivel": 0,
              "grupo": "Comercial", "unidad": "$", "tipo": "flujo",
              "sentido": "mayor", "capturable": False, "suma_hijos": True,
              "padre": None, "fuente": "manual"})
    L += _hijos_vendedor("utilidad", "Comercial")

    # ---------- ADMINISTRACIÓN ----------
    L.append({"id": "cartera", "nombre": "Cartera clientes ($)", "nivel": 0,
              "grupo": "Administración", "unidad": "$", "tipo": "saldo",
              "sentido": "menor", "capturable": False, "suma_hijos": True,
              "padre": None, "fuente": "manual"})
    L.append({"id": "cartera_corr", "nombre": "Al corriente ($)", "nivel": 1,
              "grupo": "Administración", "unidad": "$", "tipo": "saldo",
              "sentido": "mayor", "capturable": True, "suma_hijos": False,
              "padre": "cartera", "fuente": "manual"})
    L.append({"id": "cartera_venc", "nombre": "Vencido ($)", "nivel": 1,
              "grupo": "Administración", "unidad": "$", "tipo": "saldo",
              "sentido": "menor", "capturable": True, "suma_hijos": False,
              "padre": "cartera", "fuente": "manual"})
    L.append({"id": "dias_cartera", "nombre": "Días cartera", "nivel": 0,
              "grupo": "Administración", "unidad": "Días", "tipo": "saldo",
              "sentido": "menor", "capturable": True, "suma_hijos": False,
              "padre": None, "fuente": "manual"})

    L.append({"id": "ingreso", "nombre": "Ingreso ($)", "nivel": 0,
              "grupo": "Administración", "unidad": "$", "tipo": "flujo",
              "sentido": "mayor", "capturable": False, "suma_hijos": True,
              "padre": None, "fuente": "manual"})
    L += _hijos_vendedor("ingreso", "Administración")

    L.append({"id": "saldo_prov", "nombre": "Saldo proveedores ($)", "nivel": 0,
              "grupo": "Administración", "unidad": "$", "tipo": "saldo",
              "sentido": "menor", "capturable": False, "suma_hijos": True,
              "padre": None, "fuente": "manual"})
    L.append({"id": "prov_corr", "nombre": "Al corriente ($)", "nivel": 1,
              "grupo": "Administración", "unidad": "$", "tipo": "saldo",
              "sentido": "mayor", "capturable": True, "suma_hijos": False,
              "padre": "saldo_prov", "fuente": "manual"})
    L.append({"id": "prov_venc", "nombre": "Vencido ($)", "nivel": 1,
              "grupo": "Administración", "unidad": "$", "tipo": "saldo",
              "sentido": "menor", "capturable": True, "suma_hijos": False,
              "padre": "saldo_prov", "fuente": "manual"})
    L.append({"id": "dias_proveedor", "nombre": "Días proveedor", "nivel": 0,
              "grupo": "Administración", "unidad": "Días", "tipo": "saldo",
              "sentido": "mayor", "capturable": True, "suma_hijos": False,
              "padre": None, "fuente": "manual"})
    L.append({"id": "ciclo_efectivo", "nombre": "Ciclo efectivo", "nivel": 0,
              "grupo": "Administración", "unidad": "Días", "tipo": "saldo",
              "sentido": "menor", "capturable": True, "suma_hijos": False,
              "padre": None, "fuente": "manual"})
    L.append({"id": "bancos", "nombre": "Bancos ($)", "nivel": 0,
              "grupo": "Administración", "unidad": "$", "tipo": "saldo",
              "sentido": "mayor", "capturable": True, "suma_hijos": False,
              "padre": None, "fuente": "manual"})
    L.append({"id": "capital_trabajo", "nombre": "Capital de trabajo ($)",
              "nivel": 0, "grupo": "Administración", "unidad": "$",
              "tipo": "saldo", "sentido": "mayor", "capturable": True,
              "suma_hijos": False, "padre": None, "fuente": "manual"})

    # ---------- OPERACIONES ----------
    L.append({"id": "costo_inv", "nombre": "Costo inventario ($)", "nivel": 0,
              "grupo": "Operaciones", "unidad": "$", "tipo": "saldo",
              "sentido": "menor", "capturable": False, "suma_hijos": True,
              "padre": None, "fuente": "manual"})
    L.append({"id": "inventario", "nombre": "Inventario ($)", "nivel": 1,
              "grupo": "Operaciones", "unidad": "$", "tipo": "saldo",
              "sentido": "menor", "capturable": True, "suma_hijos": False,
              "padre": "costo_inv", "fuente": "manual"})
    L.append({"id": "sobrestock", "nombre": "Sobrestock ($)", "nivel": 1,
              "grupo": "Operaciones", "unidad": "$", "tipo": "saldo",
              "sentido": "menor", "capturable": True, "suma_hijos": False,
              "padre": "costo_inv", "fuente": "manual"})
    L.append({"id": "dias_inventario", "nombre": "Días inventario", "nivel": 0,
              "grupo": "Operaciones", "unidad": "Días", "tipo": "saldo",
              "sentido": "menor", "capturable": True, "suma_hijos": False,
              "padre": None, "fuente": "manual"})

    # ---------- GLOBAL ----------
    L.append({"id": "gastos_op", "nombre": "Gastos de operación ($)", "nivel": 0,
              "grupo": "Global", "unidad": "$", "tipo": "flujo",
              "sentido": "menor", "capturable": True, "suma_hijos": False,
              "padre": None, "fuente": "manual"})
    L.append({"id": "ut_operativa", "nombre": "Utilidad operativa ($)", "nivel": 0,
              "grupo": "Global", "unidad": "$", "tipo": "flujo",
              "sentido": "mayor", "capturable": True, "suma_hijos": False,
              "padre": None, "fuente": "manual"})

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