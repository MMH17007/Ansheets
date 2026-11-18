"""Verificación del motor de Ansheets.

Uso:
  python3 verificar.py                  # ejemplos de referencia + casos que el validador debe rechazar
  python3 verificar.py respuestas DIR   # evalúa respuestas reales del modelo (DIR/c01.json, ...) contra pruebas/casos.json

Los ejemplos se exportan a .xlsx y se RECALCULAN con LibreOffice para comprobar
que las fórmulas funcionan de verdad, no solo que "parecen" correctas.
"""
from __future__ import annotations

import json
import pathlib
import shutil
import subprocess
import sys
import tempfile

from openpyxl import load_workbook

from ansheets_motor import a_excel, validar

AQUI = pathlib.Path(__file__).parent
PRUEBAS = AQUI / "pruebas"
SALIDAS = AQUI / "salidas"
ERRORES_EXCEL = ("#NAME?", "#REF!", "#VALUE!", "#DIV/0!", "#N/A", "Err:", "#NULL!", "#NUM!")


def recalcular(xlsx: pathlib.Path) -> pathlib.Path:
    """LibreOffice abre el archivo, recalcula todas las fórmulas y lo guarda con los valores."""
    destino = xlsx.parent / "recalculado"
    destino.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory() as perfil:
        subprocess.run(
            ["soffice", f"-env:UserInstallation=file://{perfil}", "--headless", "--calc",
             "--convert-to", "xlsx", "--outdir", str(destino), str(xlsx)],
            check=True, capture_output=True, timeout=120,
        )
    return destino / xlsx.name


def comprobar_ejemplos() -> int:
    fallos = 0
    if SALIDAS.exists():
        shutil.rmtree(SALIDAS)
    SALIDAS.mkdir()
    for ruta in sorted((PRUEBAS / "ejemplos").glob("*.json")):
        ej = json.loads(ruta.read_text(encoding="utf-8"))
        resp = ej["respuesta"]
        errores = validar(resp)
        if errores:
            print(f"✗ {ruta.stem}: no pasa la validación → {errores}")
            fallos += 1
            continue
        if resp["tipo"] != "hoja":
            print(f"✓ {ruta.stem}: respuesta '{resp['tipo']}' válida ({len(resp['mensaje'].split())} palabras)")
            continue
        xlsx = SALIDAS / f"{ruta.stem}.xlsx"
        a_excel(resp, str(xlsx))
        ws = load_workbook(recalcular(xlsx), data_only=True).active

        problemas = []
        for fila in ws.iter_rows():
            for c in fila:
                if isinstance(c.value, str) and c.value.startswith(ERRORES_EXCEL):
                    problemas.append(f"{c.coordinate}={c.value}")
        for celda, esperado in ej["comprobaciones"].items():
            real = ws[celda].value
            if isinstance(esperado, (int, float)) and not isinstance(esperado, bool):
                ok = isinstance(real, (int, float)) and abs(real - esperado) < 0.005
            else:
                ok = (real or "") == esperado
            if not ok:
                problemas.append(f"{celda}: esperado {esperado!r}, obtenido {real!r}")
        if problemas:
            print(f"✗ {ruta.stem}: {problemas}")
            fallos += 1
        else:
            print(f"✓ {ruta.stem}: fórmulas recalculadas en LibreOffice, {len(ej['comprobaciones'])} valores correctos")
    return fallos


def comprobar_negativos() -> int:
    fallos = 0
    casos = json.loads((PRUEBAS / "validador_negativos.json").read_text(encoding="utf-8"))
    for nombre, resp in casos.items():
        errores = validar(resp)
        if errores:
            print(f"✓ rechaza «{nombre}»: {errores[0]}")
        else:
            print(f"✗ NO rechaza «{nombre}»")
            fallos += 1
    return fallos


def _texto(resp: dict) -> str:
    return json.dumps(resp, ensure_ascii=False)


def errores_al_recalcular(resp: dict, ruta: pathlib.Path) -> list[str]:
    """Exporta la hoja a Excel, la recalcula con LibreOffice y busca celdas con error."""
    a_excel(resp, str(ruta))
    ws = load_workbook(recalcular(ruta), data_only=True).active
    return [f"{c.coordinate}={c.value}" for fila in ws.iter_rows() for c in fila
            if isinstance(c.value, str) and c.value.startswith(ERRORES_EXCEL)]


def evaluar_respuestas(directorio: pathlib.Path, detalle: dict | None = None) -> int:
    casos = json.loads((PRUEBAS / "casos.json").read_text(encoding="utf-8"))
    fallos = 0
    excel_dir = directorio / "excel"
    excel_dir.mkdir(exist_ok=True)
    for caso in casos:
        archivo = directorio / f"{caso['id']}.json"
        if not archivo.exists():
            print(f"· {caso['id']}: sin respuesta")
            continue
        try:
            resp = json.loads(archivo.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            print(f"✗ {caso['id']}: no es JSON válido ({e})")
            if detalle is not None:
                detalle[caso["id"]] = [f"no es JSON válido ({e})"]
            fallos += 1
            continue
        exp = caso["esperado"]
        p = validar(resp)
        tipos = exp["tipo"] if isinstance(exp["tipo"], list) else [exp["tipo"]]
        if resp.get("tipo") not in tipos:
            p.append(f"tipo {resp.get('tipo')!r}, esperado {tipos}")
        if "idioma" in exp and resp.get("idioma") != exp["idioma"]:
            p.append(f"idioma {resp.get('idioma')!r}, esperado {exp['idioma']!r}")
        hoja = resp.get("hoja") or {}
        cols = hoja.get("columnas") or []
        nombres = " ".join([hoja.get("titulo", "")] + [c.get("nombre", "") for c in cols]).lower()
        if exp.get("requiere_formula") and hoja and not any(c.get("formula") for c in cols):
            p.append("no tiene ninguna fórmula")
        for palabra in exp.get("columnas_contienen", []):
            if hoja and palabra not in nombres:
                p.append(f"ni el título ni las columnas contienen «{palabra}»")
        if "moneda" in exp and hoja and hoja.get("moneda") != exp["moneda"]:
            p.append(f"moneda {hoja.get('moneda')!r}, esperada {exp['moneda']!r}")
        if exp.get("sin_datos_inventados") and hoja and hoja.get("filas"):
            p.append(f"inventó {len(hoja['filas'])} filas de datos")
        if "max_filas" in exp and len(hoja.get("filas") or []) > exp["max_filas"]:
            p.append("supera el máximo de filas")
        for t in exp.get("texto_corregido", []):
            if t not in _texto(resp):
                p.append(f"no aparece «{t}» corregido")
        for t in exp.get("no_contiene", []):
            if t in _texto(resp):
                p.append(f"filtra texto interno «{t}»")
        if "tipos_columna" in exp and hoja:
            for t in exp["tipos_columna"]:
                if t not in {c.get("tipo") for c in cols}:
                    p.append(f"falta una columna de tipo {t}")
        if exp.get("sin_fechas_inventadas") and hoja:
            for i, c in enumerate(cols):
                if c.get("tipo") == "fecha" and any(len(f) > i and f[i] for f in hoja.get("filas") or []):
                    p.append(f"inventó fechas en «{c.get('nombre')}»")
        if resp.get("tipo") == "hoja" and not validar(resp):
            try:
                p += [f"fórmula con error al recalcular: {e}" for e in
                      errores_al_recalcular(resp, excel_dir / f"{caso['id']}.xlsx")]
            except Exception as e:
                p.append(f"no se pudo exportar a Excel: {e}")
        if "celda_texto_literal" in exp and exp["celda_texto_literal"] not in _texto(hoja.get("filas")):
            p.append("no conservó el texto literal")
        if detalle is not None:
            detalle[caso["id"]] = p
        if p:
            print(f"✗ {caso['id']}: {p}")
            fallos += 1
        else:
            print(f"✓ {caso['id']}")
    return fallos


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "respuestas":
        sys.exit(1 if evaluar_respuestas(pathlib.Path(sys.argv[2])) else 0)
    print("== Ejemplos de referencia (exportar + recalcular) ==")
    f = comprobar_ejemplos()
    print("\n== El validador debe rechazar estas respuestas ==")
    f += comprobar_negativos()
    print(f"\n{'TODO CORRECTO' if not f else f'{f} FALLOS'}")
    sys.exit(1 if f else 0)
