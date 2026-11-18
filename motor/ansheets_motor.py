"""Motor de Ansheets: valida la respuesta del modelo y la convierte en Excel (.xlsx) con fórmulas reales.

El modelo NUNCA escribe referencias tipo A1: usa nombres de columna entre corchetes
([Ingreso], [Saldo@anterior]) y este módulo las traduce. Así evitamos que una fórmula
apunte a la celda equivocada.
"""
from __future__ import annotations

import datetime as dt
import re

from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill
from openpyxl.utils import get_column_letter

FUNCIONES_PERMITIDAS = {"IF", "AND", "OR", "ROUND", "ABS", "MIN", "MAX", "TODAY"}
FUNCIONES_TOTAL = {"SUM", "AVERAGE", "MIN", "MAX", "COUNT"}
TIPOS_NUMERICOS = {"numero", "moneda", "porcentaje"}
MAX_PALABRAS_MENSAJE = 25
MAX_FILAS = 200
MAX_COLUMNAS = 15

RE_REF = re.compile(r"\[([^\[\]@]+?)(@anterior)?\]")
RE_CADENA = re.compile(r'"[^"]*"')
RE_FUNCION = re.compile(r"\b([A-Za-z_][A-Za-z0-9_.]*)\s*\(")
RE_A1 = re.compile(r"\$?\b[A-Z]{1,3}\$?[0-9]+\b")
RE_FECHA = re.compile(r"^\d{4}-\d{2}-\d{2}$")

FORMATO_MONEDA = {
    "EUR": '#,##0.00 "€"',
    "USD": '"$"#,##0.00',
    "GBP": '"£"#,##0.00',
}
FORMATO_FECHA = {"es": "dd/mm/yyyy", "en": "yyyy-mm-dd"}
ETIQUETA_TOTAL = {"es": "TOTAL", "en": "TOTAL"}
NOMBRE_FUNCION_TOTAL = {
    "es": {"SUM": "Total", "AVERAGE": "Media", "MIN": "Mínimo", "MAX": "Máximo", "COUNT": "Recuento"},
    "en": {"SUM": "Total", "AVERAGE": "Average", "MIN": "Min", "MAX": "Max", "COUNT": "Count"},
}


def _sin_cadenas(formula: str) -> str:
    return RE_CADENA.sub('""', formula)


def validar(resp: dict) -> list[str]:
    """Devuelve una lista de errores (vacía = respuesta válida)."""
    errores: list[str] = []
    tipo = resp.get("tipo")
    if tipo not in {"hoja", "aclaracion", "fuera_de_tema"}:
        errores.append(f"tipo inválido: {tipo!r}")
    if resp.get("idioma") not in {"es", "en"}:
        errores.append(f"idioma inválido: {resp.get('idioma')!r}")
    mensaje = resp.get("mensaje", "")
    if not isinstance(mensaje, str) or not mensaje.strip():
        errores.append("falta el mensaje")
    elif len(mensaje.split()) > MAX_PALABRAS_MENSAJE:
        errores.append(f"mensaje demasiado largo ({len(mensaje.split())} palabras > {MAX_PALABRAS_MENSAJE})")

    hoja = resp.get("hoja")
    if tipo != "hoja":
        if hoja:
            errores.append(f"tipo '{tipo}' no debe incluir hoja (gasta tokens)")
        return errores
    if not isinstance(hoja, dict):
        return errores + ["tipo 'hoja' sin objeto hoja"]

    columnas = hoja.get("columnas") or []
    filas = hoja.get("filas") or []
    if not columnas:
        errores.append("la hoja no tiene columnas")
    if len(columnas) > MAX_COLUMNAS:
        errores.append(f"demasiadas columnas ({len(columnas)})")
    if len(filas) > MAX_FILAS:
        errores.append(f"demasiadas filas ({len(filas)})")
    if hoja.get("moneda") not in FORMATO_MONEDA:
        errores.append(f"moneda no soportada: {hoja.get('moneda')!r}")
    vacias = hoja.get("filas_vacias", 0)
    if not isinstance(vacias, int) or not 0 <= vacias <= 50:
        errores.append(f"filas_vacias fuera de rango: {vacias!r}")
    if not filas and not vacias:
        errores.append("hoja sin datos y sin filas vacías de plantilla")

    nombres = [c.get("nombre", "") for c in columnas]
    if len(set(nombres)) != len(nombres):
        errores.append("hay nombres de columna repetidos")
    por_nombre = {c.get("nombre"): c for c in columnas}

    for c in columnas:
        if c.get("tipo") not in {"texto", "numero", "moneda", "fecha", "porcentaje"}:
            errores.append(f"columna {c.get('nombre')!r}: tipo inválido {c.get('tipo')!r}")
        f = c.get("formula")
        if not f:
            continue
        if not f.startswith("="):
            errores.append(f"columna {c['nombre']!r}: la fórmula debe empezar por '='")
        for nombre, anterior in RE_REF.findall(f):
            if nombre not in por_nombre:
                errores.append(f"columna {c['nombre']!r}: referencia a columna inexistente [{nombre}]")
            elif nombre == c["nombre"] and not anterior:
                errores.append(f"columna {c['nombre']!r}: se refiere a sí misma sin @anterior")
        limpia = RE_REF.sub("0", _sin_cadenas(f))
        for fn in RE_FUNCION.findall(limpia):
            if fn.upper() not in FUNCIONES_PERMITIDAS:
                errores.append(f"columna {c['nombre']!r}: función no permitida {fn}()")
        if RE_A1.search(limpia):
            errores.append(f"columna {c['nombre']!r}: usa referencias A1 ({RE_A1.search(limpia).group()})")
        if limpia.count("(") != limpia.count(")"):
            errores.append(f"columna {c['nombre']!r}: paréntesis desequilibrados")

    for i, fila in enumerate(filas, start=1):
        if len(fila) != len(columnas):
            errores.append(f"fila {i}: tiene {len(fila)} valores y hay {len(columnas)} columnas")
            continue
        for c, v in zip(columnas, fila):
            if c.get("formula"):
                if v is not None:
                    errores.append(f"fila {i}, {c['nombre']!r}: columna con fórmula debe ser null")
                continue
            if v is None or v == "":
                continue
            t = c.get("tipo")
            if t in TIPOS_NUMERICOS and not isinstance(v, (int, float)):
                errores.append(f"fila {i}, {c['nombre']!r}: se esperaba número y llegó {v!r}")
            if t == "fecha" and not (isinstance(v, str) and RE_FECHA.match(v)):
                errores.append(f"fila {i}, {c['nombre']!r}: fecha no está en AAAA-MM-DD: {v!r}")
            if t == "porcentaje" and isinstance(v, (int, float)) and abs(v) > 10:
                errores.append(f"fila {i}, {c['nombre']!r}: porcentaje {v} parece no estar en fracción (0.21)")

    for t in hoja.get("totales") or []:
        col = por_nombre.get(t.get("columna"))
        if not col:
            errores.append(f"total sobre columna inexistente {t.get('columna')!r}")
        elif col.get("tipo") not in TIPOS_NUMERICOS:
            errores.append(f"total sobre columna no numérica {t.get('columna')!r}")
        if t.get("funcion") not in FUNCIONES_TOTAL:
            errores.append(f"función de total no permitida {t.get('funcion')!r}")
    return errores


def _traducir(formula: str, letras: dict[str, str], fila: int, primera: int) -> str:
    """[Ingreso] -> D5 ; [Saldo@anterior] -> F4 (o 0 en la primera fila)."""
    partes = []
    pos = 0
    for m in RE_CADENA.finditer(formula):  # no tocar el texto entre comillas
        partes.append((formula[pos:m.start()], True))
        partes.append((m.group(), False))
        pos = m.end()
    partes.append((formula[pos:], True))

    def sustituir(m: re.Match) -> str:
        letra = letras[m.group(1)]
        if m.group(2):
            return "0" if fila == primera else f"{letra}{fila - 1}"
        return f"{letra}{fila}"

    return "".join(RE_REF.sub(sustituir, p) if traducir else p for p, traducir in partes)


def a_excel(resp: dict, ruta: str) -> dict:
    """Crea el .xlsx. Devuelve un mapa útil para pruebas: {'fila_total': n, 'letras': {...}}."""
    hoja = resp["hoja"]
    idioma = resp["idioma"]
    columnas = hoja["columnas"]
    letras = {c["nombre"]: get_column_letter(i) for i, c in enumerate(columnas, start=1)}

    wb = Workbook()
    ws = wb.active
    ws.title = hoja["titulo"][:31] or "Ansheets"
    negrita = Font(bold=True, color="FFFFFF")
    fondo = PatternFill("solid", fgColor="1E1B4B")

    for i, c in enumerate(columnas, start=1):
        celda = ws.cell(row=1, column=i, value=c["nombre"])
        celda.font, celda.fill = negrita, fondo
        ws.column_dimensions[get_column_letter(i)].width = max(12, len(c["nombre"]) + 4)
    ws.freeze_panes = "A2"

    datos = list(hoja["filas"]) + [[None] * len(columnas)] * hoja.get("filas_vacias", 0)
    primera = 2
    ultima = primera + len(datos) - 1

    def formatear(celda, tipo):
        if tipo == "moneda":
            celda.number_format = FORMATO_MONEDA[hoja["moneda"]]
        elif tipo == "porcentaje":
            celda.number_format = "0.0%"
        elif tipo == "fecha":
            celda.number_format = FORMATO_FECHA[idioma]
        elif tipo == "numero":
            celda.number_format = "#,##0.##"

    for r, fila in enumerate(datos, start=primera):
        for ci, (c, v) in enumerate(zip(columnas, fila), start=1):
            celda = ws.cell(row=r, column=ci)
            if c.get("formula"):
                celda.value = _traducir(c["formula"], letras, r, primera)
            elif v is None or v == "":
                pass
            elif c["tipo"] == "fecha":
                celda.value = dt.date.fromisoformat(v)
            else:
                celda.value = v
                if isinstance(v, str) and v[:1] in "=+-@":
                    celda.data_type = "s"  # texto literal: evita inyección de fórmulas
            formatear(celda, c["tipo"])

    fila_total = None
    if hoja.get("totales") and datos:
        fila_total = ultima + 1
        if columnas[0]["nombre"] not in {t["columna"] for t in hoja["totales"]}:
            ws.cell(row=fila_total, column=1, value=ETIQUETA_TOTAL[idioma]).font = Font(bold=True)
        for t in hoja["totales"]:
            ci = list(letras).index(t["columna"]) + 1
            letra = letras[t["columna"]]
            celda = ws.cell(row=fila_total, column=ci, value=f"={t['funcion']}({letra}{primera}:{letra}{ultima})")
            celda.font = Font(bold=True)
            tipo = next(c["tipo"] for c in columnas if c["nombre"] == t["columna"])
            formatear(celda, "numero" if t["funcion"] == "COUNT" else tipo)

    wb.save(ruta)
    return {"fila_total": fila_total, "letras": letras, "primera": primera, "ultima": ultima}
