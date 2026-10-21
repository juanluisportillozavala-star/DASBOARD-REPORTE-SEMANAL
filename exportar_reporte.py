"""
=========================================================
exportar_reporte.py  —  Descargar el REPORTE en Excel con las
tablas dinámicas VIVAS
=========================================================
Toma la plantilla (plantillas/REPORTE_SEMANAL_FINAL.xlsx), que
ya trae las 7 tablas dinámicas y los segmentadores, y reemplaza
SOLO los datos de las hojas BD (BD Ventas, BD Cobranza, BD
Cartera, BD CxP) con la BD CRUDA guardada en Supabase.

Técnica: cirugía de ZIP/XML (openpyxl NO soporta pivots/slicers
y los rompería). Se reescribe únicamente el sheetN.xml de cada
hoja BD; todo lo demás (pivots, caches, slicers) se copia intacto.

CORRECCIÓN AGING CxP: la plantilla calcula el aging de Saldo
Proveedor usando el "Total pendiente" (que NO resta los abonos),
por eso los saldos salían inflados. Aquí, SOLO para la hoja
BD CxP, se RECALCULAN las 4 columnas de aging usando el
"Importe adeudado" (saldo real, con abonos ya descontados) y
los "Dias vencido". El resto de hojas no se toca.

Además:
  • Se preserva el estilo (formato) de cada columna.
  • Se ajusta el rango de origen de cada pivotCache.
  • Se activa refreshOnLoad=1.
"""

import io
import re
import zipfile
import xml.etree.ElementTree as ET
from datetime import datetime, date
import pandas as pd
from openpyxl.utils import get_column_letter

import db

# módulo interno -> nombre de la hoja BD en la plantilla
MODULO_HOJA = {
    "ventas": "BD Ventas",
    "ingresos": "BD Cobranza",
    "cartera": "BD Cartera",
    "saldo_proveedor": "BD CxP",
}

# módulo interno -> nombre de la hoja de la TABLA DINÁMICA
MODULO_PIVOTE = {
    "ventas": "Ventas",
    "ingresos": "Ingreso",
    "cartera": "Cartera",
    "saldo_proveedor": "Saldo Prov",
}

_NS_MAIN = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
_NS_R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"


# =========================================================
# CORRECCIÓN DEL AGING DE CxP (usar Importe adeudado)
# =========================================================

_AGING_CXP = ["Vencido 0-30 días", "Vencido 31-60 días",
              "Vencido >60 días", "Vigente"]


def _rango_aging(dias_vencido):
    """En qué columna de aging cae, según los días de vencido."""
    try:
        dv = float(dias_vencido)
    except (ValueError, TypeError):
        dv = 0
    if dv <= 0:
        return "Vigente"
    if dv <= 30:
        return "Vencido 0-30 días"
    if dv <= 60:
        return "Vencido 31-60 días"
    return "Vencido >60 días"


def _buscar(cols, *cand):
    norm = {str(c).strip().lower(): c for c in cols}
    for c in cand:
        k = c.strip().lower()
        if k in norm:
            return norm[k]
    return None


def _corregir_aging_cxp(df):
    """Recalcula las 4 columnas de aging de BD CxP con el saldo
    PENDIENTE real (Importe adeudado, que resta abonos), convertido
    a pesos y sin IVA, para que cuadre EXACTO con la página:

      USD:  saldo = Importe_adeudado * (Importe / Total_en_divisa)
            (Importe/Total_en_divisa = tipo de cambio, ya sin IVA)
      MXN:  saldo = Importe_adeudado / 1.16   (quita IVA)

    El resultado se coloca en la columna de aging según el Estatus
    (Vigente) o los Días vencido. Si faltan columnas, no toca el df.
    Verificado contra la página (p.ej. RITA = 27,348.34).
    """
    c_div = _buscar(df.columns, "Divisa", "Moneda")
    c_imp = _buscar(df.columns, "Importe")              # importe en MN
    c_divtot = _buscar(df.columns, "Total en divisa", "Total en divisa ")
    c_adeudado = _buscar(df.columns, "Importe adeudado", "Importe Adeudado")
    c_estatus = _buscar(df.columns, "Estatus", "Estado")
    c_dias = _buscar(df.columns, "Dias vencido", "Días vencido",
                     "Dias vencidos", "Días vencidos")
    cols_aging = {a: _buscar(df.columns, a) for a in _AGING_CXP}

    if c_adeudado is None or any(v is None for v in cols_aging.values()):
        return df

    df = df.copy()

    def _num(serie, i):
        try:
            v = serie.iloc[i]
            return float(v) if v not in (None, "") and not (isinstance(v, float) and pd.isna(v)) else 0.0
        except Exception:
            return 0.0

    def _saldo(i):
        L = abs(_num(df[c_adeudado], i))
        if L == 0:
            return 0.0
        divisa = str(df[c_div].iloc[i]).strip().upper() if c_div else "MXN"
        if divisa == "USD" and c_imp is not None and c_divtot is not None:
            H = abs(_num(df[c_imp], i))
            K = abs(_num(df[c_divtot], i))
            return L * (H / K) if K else L     # USD: adeudado × TC
        return L / 1.16                        # MXN: quitar IVA

    def _rango(i):
        est = str(df[c_estatus].iloc[i]).strip().lower() if c_estatus else ""
        if est == "vigente":
            return "Vigente"
        dv = 0
        if c_dias is not None:
            try:
                dv = float(df[c_dias].iloc[i])
            except (ValueError, TypeError):
                dv = 0
        if dv <= 0:
            return "Vigente"
        if dv <= 30:
            return "Vencido 0-30 días"
        if dv <= 60:
            return "Vencido 31-60 días"
        return "Vencido >60 días"

    nuevas = {a: [0.0] * len(df) for a in _AGING_CXP}
    for i in range(len(df)):
        nuevas[_rango(i)][i] = _saldo(i)
    for a in _AGING_CXP:
        df[cols_aging[a]] = nuevas[a]
    return df


# ---------------------------------------------------------
# helpers de celda
# ---------------------------------------------------------

def _es_fecha(v):
    return isinstance(v, (datetime, date, pd.Timestamp))


def _excel_serial(v):
    if isinstance(v, pd.Timestamp):
        v = v.to_pydatetime()
    if isinstance(v, date) and not isinstance(v, datetime):
        v = datetime(v.year, v.month, v.day)
    base = datetime(1899, 12, 30)
    delta = v - base
    return delta.days + delta.seconds / 86400.0


def _celda_xml(ref, valor, estilo):
    s_attr = f' s="{estilo}"' if estilo else ""
    if valor is None or (isinstance(valor, float) and pd.isna(valor)):
        return f'<c r="{ref}"{s_attr}/>'
    if _es_fecha(valor):
        return f'<c r="{ref}"{s_attr}><v>{_excel_serial(valor)}</v></c>'
    if isinstance(valor, bool):
        return f'<c r="{ref}" t="b"{s_attr}><v>{1 if valor else 0}</v></c>'
    if isinstance(valor, (int, float)):
        return f'<c r="{ref}"{s_attr}><v>{valor}</v></c>'
    txt = (str(valor).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))
    return (f'<c r="{ref}" t="inlineStr"{s_attr}>'
            f'<is><t xml:space="preserve">{txt}</t></is></c>')


# ---------------------------------------------------------
# mapeo hoja -> sheetN.xml
# ---------------------------------------------------------

def _mapa_hojas(zf):
    wb = zf.read("xl/workbook.xml").decode("utf-8")
    rels = zf.read("xl/_rels/workbook.xml.rels").decode("utf-8")
    root = ET.fromstring(wb)
    sheets = []
    for s in root.find(f"{{{_NS_MAIN}}}sheets"):
        rid = s.get(f"{{{_NS_R}}}id")
        sheets.append((s.get("name"), rid))
    rroot = ET.fromstring(rels)
    rmap = {rel.get("Id"): rel.get("Target") for rel in rroot}
    out = {}
    for nombre, rid in sheets:
        target = rmap.get(rid, "")
        if not target.startswith("xl/"):
            target = "xl/" + target
        out[nombre] = target
    return out


# ---------------------------------------------------------
# estilos por columna
# ---------------------------------------------------------

def _estilos_por_columna(sheet_xml):
    fila2 = re.search(r'<row r="2"[^>]*>(.*?)</row>', sheet_xml, re.DOTALL)
    estilos = {}
    if fila2:
        for col, s in re.findall(r'<c r="([A-Z]+)2"(?:\s+s="(\d+)")?', fila2.group(1)):
            estilos[col] = s or ""
    return estilos


def _cargar_shared_strings(zf):
    try:
        x = zf.read("xl/sharedStrings.xml").decode("utf-8")
    except KeyError:
        return []
    textos = []
    for si in re.findall(r"<si>(.*?)</si>", x, re.DOTALL):
        partes = re.findall(r"<t[^>]*>(.*?)</t>", si, re.DOTALL)
        txt = "".join(partes)
        txt = (txt.replace("&amp;", "&").replace("&lt;", "<")
               .replace("&gt;", ">"))
        textos.append(txt)
    return textos


def _headers_originales(sheet_xml, shared):
    fila1 = re.search(r'<row r="1"[^>]*>(.*?)</row>', sheet_xml, re.DOTALL)
    if not fila1:
        return []
    headers = []
    for m in re.finditer(r'<c r="([A-Z]+)1"([^>]*)>(.*?)</c>', fila1.group(1), re.DOTALL):
        attrs, contenido = m.group(2), m.group(3)
        if 't="s"' in attrs:
            vi = re.search(r"<v>(\d+)</v>", contenido)
            headers.append(shared[int(vi.group(1))] if vi else "")
        else:
            t = re.search(r"<t[^>]*>(.*?)</t>", contenido, re.DOTALL)
            if t:
                headers.append(t.group(1).replace("&amp;", "&")
                               .replace("&lt;", "<").replace("&gt;", ">"))
            else:
                headers.append("")
    return headers


# ---------------------------------------------------------
# construir el sheetData nuevo
# ---------------------------------------------------------

def _sheet_data_xml(headers, df, estilos):
    filas = []
    celdas = []
    for j, h in enumerate(headers):
        col = get_column_letter(j + 1)
        celdas.append(_celda_xml(f"{col}1", h, estilos.get(col, "")))
    filas.append(f'<row r="1">{"".join(celdas)}</row>')
    for i in range(len(df)):
        r = df.iloc[i]
        celdas = []
        for j, h in enumerate(headers):
            col = get_column_letter(j + 1)
            celdas.append(_celda_xml(f"{col}{i + 2}", r[h], estilos.get(col, "")))
        filas.append(f'<row r="{i + 2}">{"".join(celdas)}</row>')
    return "<sheetData>" + "".join(filas) + "</sheetData>"


def _alinear(df_crudo, headers):
    norm = {str(c).strip().lower(): c for c in df_crudo.columns}
    salida = pd.DataFrame()
    for h in headers:
        real = norm.get(str(h).strip().lower())
        salida[h] = df_crudo[real] if real is not None else None
    return salida


def _actualizar_sheet(sheet_xml, headers, df, estilos):
    sd = _sheet_data_xml(headers, df, estilos)
    n_filas = len(df) + 1
    ultima = f"{get_column_letter(len(headers))}{n_filas}"
    sheet_xml = re.sub(r'<dimension ref="[^"]*"/>',
                       f'<dimension ref="A1:{ultima}"/>', sheet_xml, count=1)
    if "<sheetData>" in sheet_xml:
        ini = sheet_xml.index("<sheetData>")
        fin = sheet_xml.index("</sheetData>") + len("</sheetData>")
        sheet_xml = sheet_xml[:ini] + sd + sheet_xml[fin:]
    elif "<sheetData/>" in sheet_xml:
        sheet_xml = sheet_xml.replace("<sheetData/>", sd, 1)
    return sheet_xml, n_filas


def _solo_visible(workbook_xml, hoja_visible):
    sheets = list(re.finditer(r'<sheet\b[^>]*/>', workbook_xml))
    viejos = [m.group(0) for m in sheets]
    nuevas = []
    idx_visible = 0
    for i, tag in enumerate(viejos):
        nm = re.search(r'name="([^"]+)"', tag)
        nombre = nm.group(1) if nm else ""
        tag_sin = re.sub(r'\s+state="[^"]*"', "", tag)
        if nombre == hoja_visible:
            idx_visible = i
            nuevas.append(tag_sin)
        else:
            nuevas.append(tag_sin[:-2] + ' state="hidden"/>')
    for viejo, nuevo in zip(viejos, nuevas):
        workbook_xml = workbook_xml.replace(viejo, nuevo, 1)

    def _fix(m):
        wv = m.group(0)
        wv = re.sub(r'\s+activeTab="[^"]*"', "", wv)
        if wv.endswith("/>"):
            return wv[:-2] + f' activeTab="{idx_visible}"/>'
        return wv[:-1] + f' activeTab="{idx_visible}">'
    workbook_xml = re.sub(r'<workbookView\b[^>]*/?>', _fix,
                          workbook_xml, count=1)
    return workbook_xml, hoja_visible


def _ajustar_tabselected(sheet_xml, seleccionar):
    m = re.search(r'<sheetView\b[^>]*?>', sheet_xml)
    if not m:
        return sheet_xml
    tag = m.group(0)
    tag_limpio = re.sub(r'\s+tabSelected="[^"]*"', "", tag)
    if seleccionar:
        if tag_limpio.endswith("/>"):
            nuevo = tag_limpio[:-2] + ' tabSelected="1"/>'
        else:
            nuevo = tag_limpio[:-1] + ' tabSelected="1">'
    else:
        nuevo = tag_limpio
    return sheet_xml.replace(tag, nuevo, 1)


def _actualizar_pivotcache(cache_xml, hoja, n_filas):
    def _rep(m):
        attrs = m.group(0)
        if f'sheet="{hoja}"' not in attrs:
            return attrs
        return re.sub(r'ref="([A-Z]+1:[A-Z]+)\d+"',
                      lambda mm: f'ref="{mm.group(1)}{n_filas}"', attrs)
    cache_xml = re.sub(r'<worksheetSource[^>]*/>', _rep, cache_xml)
    if "refreshOnLoad" in cache_xml:
        cache_xml = re.sub(r'refreshOnLoad="[01]"', 'refreshOnLoad="1"', cache_xml)
    else:
        cache_xml = cache_xml.replace("<pivotCacheDefinition ",
                                      '<pivotCacheDefinition refreshOnLoad="1" ', 1)
    return cache_xml


# ---------------------------------------------------------
# función principal
# ---------------------------------------------------------

def generar_reporte(plantilla_path, solo_modulo=None):
    """Devuelve los BYTES del xlsx con las BD reemplazadas por lo
    guardado en Supabase (BD cruda). Las dinámicas quedan vivas."""
    with zipfile.ZipFile(plantilla_path) as z:
        nombres = z.namelist()
        contenido = {n: z.read(n) for n in nombres}
        shared = _cargar_shared_strings(z)

    mapa = _mapa_hojas(zipfile.ZipFile(plantilla_path))

    filas_por_hoja = {}

    for modulo, hoja in MODULO_HOJA.items():
        parte = mapa.get(hoja)
        if not parte or parte not in contenido:
            continue
        try:
            df_crudo = db.leer_crudo(modulo)
        except Exception:
            df_crudo = None
        if df_crudo is None or len(df_crudo) == 0:
            continue

        # CORRECCIÓN: para Saldo Proveedor, recalcular el aging con
        # el "Importe adeudado" (saldo real) antes de escribir.
        if modulo == "saldo_proveedor":
            try:
                df_crudo = _corregir_aging_cxp(df_crudo)
            except Exception as e:
                print(f">>> [CxP] No se pudo corregir aging: {e}", flush=True)

        sheet_xml = contenido[parte].decode("utf-8")
        headers = _headers_originales(sheet_xml, shared)
        if not headers:
            continue
        estilos = _estilos_por_columna(sheet_xml)
        df_align = _alinear(df_crudo, headers)
        nuevo_xml, n_filas = _actualizar_sheet(sheet_xml, headers, df_align, estilos)
        contenido[parte] = nuevo_xml.encode("utf-8")
        filas_por_hoja[hoja] = n_filas

    for n in list(contenido.keys()):
        if re.search(r"xl/pivotCache/pivotCacheDefinition\d+\.xml$", n):
            x = contenido[n].decode("utf-8")
            for hoja, nf in filas_por_hoja.items():
                x = _actualizar_pivotcache(x, hoja, nf)
            if "refreshOnLoad" in x:
                x = re.sub(r'refreshOnLoad="[01]"', 'refreshOnLoad="1"', x)
            else:
                x = x.replace("<pivotCacheDefinition ",
                              '<pivotCacheDefinition refreshOnLoad="1" ', 1)
            contenido[n] = x.encode("utf-8")

    if solo_modulo and solo_modulo in MODULO_PIVOTE:
        hoja_vis = MODULO_PIVOTE[solo_modulo]
        wbxml = contenido["xl/workbook.xml"].decode("utf-8")
        wbxml, _ = _solo_visible(wbxml, hoja_vis)
        contenido["xl/workbook.xml"] = wbxml.encode("utf-8")

        parte_visible = mapa.get(hoja_vis)
        for nombre_hoja, parte in mapa.items():
            if parte not in contenido:
                continue
            xml = contenido[parte].decode("utf-8")
            xml = _ajustar_tabselected(xml, seleccionar=(parte == parte_visible))
            contenido[parte] = xml.encode("utf-8")

    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as z:
        for n in nombres:
            z.writestr(n, contenido[n])
    buffer.seek(0)
    return buffer.getvalue()