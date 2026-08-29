Sistema Gerencial Liderza

Dashboard de Indicadores Empresariales

Módulos

✔ Ventas
✔ Ingresos
✔ Cartera
✔ Inventario
✔ Saldo Proveedor

Tecnologías

Python
Streamlit
Pandas
Plotly
OpenPyXL

Estado

🚧 En desarrollo


# Plan de Arquitectura — Dashboard Gerencial Liderza

> Hoja de ruta del proyecto de automatización. Documento vivo: se actualiza
> conforme avanzamos. Sirve también como memoria entre sesiones de trabajo.

---

## 1. Visión

Reemplazar el proceso manual actual (descargar BD de Odoo → pegarlas en el
Excel maestro → arrastrar fórmulas → refrescar tablas dinámicas) por un flujo
automático:

1. El usuario descarga las BD crudas de Odoo.
2. Las sube a la web **una sola vez**.
3. La web muestra todo automático (tablas, gráficos, calendario) en los 5 módulos.
4. La web puede **regenerar el Excel maestro** (con BD ocultas, hojas de reporte,
   tablas dinámicas y calendarios) para compartir con usuarios que no usan la web.

---

## 2. Estado actual (lo que YA está hecho)

- **Módulo Ventas funcional**: carga de archivos, procesamiento, filtro
  Mes/Semana, 4 tablas jerárquicas y 5 gráficos de análisis.
- **Núcleo reutilizable (`core/`)**:
  - `columnas.py` — fuente única de nombres de columna.
  - `metricas.py` — margen / utilidad unitaria (una sola definición).
  - `arbol.py` — motor jerárquico parametrizable (N niveles) + orden
    (métrica/alfabético, asc/desc).
- **Fábrica de tablas** (`ventas/tabla_arbol.py`, `tablas_ventas.py`): una
  configuración por tabla; los callbacks son pattern-matching (un juego sirve
  a todas).
- **Módulo de gráficos** (`ventas/graficos.py`): Top 10 productos/clientes,
  Venta vs Margen %, Participación (donas). Optimizados para no recalcular con
  el accordion cerrado.
- **Despliegue en Render** funcionando (gunicorn con threads).

**Verificado con datos reales**: los totales cuadran al centavo con el Excel
maestro (Venta 21,903,281.90 / Ut Bruta 4,361,352.48).

---

## 3. Lo que falta (el proyecto a futuro)

Cuatro piezas. **El orden importa**: cada una habilita la siguiente.

### Pieza 1 — Estado global (CIMIENTO)
**Problema que resuelve**: hoy los datos viven en un `dcc.Store` dentro del
layout de Ventas; al cambiar de pestaña, ese layout se destruye y los datos se
pierden.
**Solución**: mover el estado a un nivel por encima de las pestañas (layout
principal), de modo que persista al navegar entre módulos.
**Es el cimiento**: sin esto, ni la carga central ni la exportación tienen
dónde apoyarse.

> **DECISIÓN TOMADA** — ¿dónde viven los datos? **COMPARTIDO con base de datos.**
>
> Flujo confirmado: **una persona actualiza el reporte semanalmente y el equipo
> lo consulta** ("uno actualiza, muchos consultan"). Por eso:
> - Los datos se guardan en una **base de datos PostgreSQL en Render** (gestionada).
> - Una persona sube las BD de Odoo una vez por semana; el equipo entra y ve el
>   reporte actualizado sin subir nada.
> - **Beneficio extra**: al vivir los datos en la base y no en la memoria de un
>   worker, se resuelve de raíz la limitación actual de "1 solo worker" — se
>   podrían usar varios workers para aguantar más consultas simultáneas.

### Pieza 2 — Carga central de BD
**Qué es**: una pantalla única donde se suben las BD de todos los módulos
(Ventas, Ingresos, Cartera, Saldo Prov, Inventario) de una sola vez.
**Depende de**: la Pieza 1 (guarda lo cargado en el estado global).

### Pieza 3 — Los 5 módulos con el mismo patrón
**Qué es**: replicar el patrón de Ventas (tablas + gráficos + calendario) a los
otros 4 módulos, mediante una **fábrica de módulos** (cada módulo se define con
su configuración: qué BD usa, qué niveles de árbol, qué gráficos).
**Depende de**: Piezas 1 y 2.
**Ventaja**: evita copiar el módulo Ventas 5 veces; una sola base que se
configura.

### Pieza 4 — Exportar a Excel
**Qué es**: generar el Excel maestro descargable.
**Enfoque acordado** (importante): NO crear las tablas dinámicas desde cero
(openpyxl no lo soporta de forma fiable — verificado: `TableDefinition` tiene
97 atributos sin API de creación). En su lugar:
- Usar **tu Excel maestro actual como plantilla** (ya tiene las PivotTables y
  calendarios funcionando).
- **Inyectar** las BD nuevas en las hojas ocultas.
- Marcar las PivotTables para que **se refresquen al abrir**.
**Trade-off aceptado**: en algunas versiones de Excel el usuario podría tener
que dar "Actualizar todo" una vez. Confirmado que no es problema.
**Depende de**: Piezas 1 y 2 (necesita los datos cargados).

### Pieza 5 — Control de acceso (login)
**Qué es**: pantalla de inicio de sesión para el equipo, porque el reporte
contiene datos financieros sensibles y estará accesible por internet.
**Decidido**: la app **sí** llevará login.
**Depende de**: la base de datos (Pieza 1) — los usuarios/contraseñas se
guardan ahí. Conviene hacerlo junto con o justo después de la Pieza 1.
**Nota**: manejar contraseñas requiere cuidado (guardarlas cifradas con hash,
nunca en texto plano). A definir: ¿usuarios fijos creados por un admin, o
registro abierto? Para un equipo interno, lo normal es que un admin cree las
cuentas.

---

## 4. Orden de construcción recomendado

```
Pieza 1 (Estado global)  ──►  Pieza 2 (Carga central)  ──►  Pieza 3 (5 módulos)
                          └─►  Pieza 4 (Exportar Excel)
```

1. **Estado global** — primero, es el cimiento.
2. **Carga central** — se apoya en el estado global.
3. **Módulos 2-5** y **Exportar Excel** pueden ir en paralelo o en el orden que
   convenga, una vez que 1 y 2 estén.

---

## 5. Riesgos y notas honestas

- **Multi-worker en Render**: la app actual solo funciona con 1 worker porque el
  estado no se comparte entre procesos. Si se elige "compartido con base de
  datos" (Pieza 1), esto se resuelve de raíz y se podrían usar más workers.
- **Tamaño de datos en el navegador**: si se elige "privado por usuario", ojo con
  el límite de almacenamiento del navegador para BD grandes.
- **Exportación Excel**: el refresco automático de PivotTables no es 100% fiable
  entre versiones de Excel (aceptado).
- **Rendimiento**: con 5 módulos × (tablas + gráficos), habrá que cuidar que no
  se recalcule todo a la vez. El patrón de "no calcular lo que no se ve"
  (accordion cerrado) ya lo tenemos y se debe extender.

---

## 6. Decisiones — estado

**Ya tomadas:**
1. ✅ **Datos compartidos** con base de datos **PostgreSQL en Render**.
2. ✅ **La app llevará login** (datos financieros sensibles).

**Pendientes de decidir (para retomar):**
1. ¿Los 5 módulos usan exactamente el mismo patrón, o alguno difiere?
   (Dijiste "patrón similar de tablas y algunos gráficos + calendario" — hay que
   precisar los niveles de árbol y gráficos de cada módulo cuando lleguemos ahí.)
2. Login: ¿usuarios fijos creados por un admin, o registro abierto? (Para equipo
   interno, lo normal es que un admin cree las cuentas.)
3. ¿Cada semana se reemplazan las BD anteriores, o se guarda histórico para poder
   comparar semanas/meses? (Relevante para el comparador de meses que quedó
   pendiente y para el diseño de la base de datos.)

---

## 7. Higiene pendiente (deuda técnica menor, no urgente)

- Eliminar código muerto: `ventas/tabla_producto_cliente.py` (prototipo ya
  reemplazado por la fábrica), callbacks de la tabla original en reposo,
  `debug-store-bd-ventas`.
- Variables sin uso en `aggrid.py` (`UMBRAL_SCROLL`, `ALTO_VIEWPORT` tras el
  cambio a altura calculada).
- `requirements.txt`: fijar las mismas versiones que corren en local/Render.
- README: dice "Streamlit", corregir a "Dash".
- Unificar colores de marca en una sola fuente (hoy repartidos entre
  `config.py`, `estilos.css` y los módulos).