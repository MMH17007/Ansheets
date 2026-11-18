"""Resume los resultados de probar_gemini.py en resultados/COMPARATIVA.md.

Uso: python3 comparar.py gemini-3.5-flash-lite gemini-2.5-flash-lite gemini-3.8-flash
"""
from __future__ import annotations

import io
import json
import pathlib
import statistics
import sys
from contextlib import redirect_stdout

from verificar import evaluar_respuestas

AQUI = pathlib.Path(__file__).parent

# Precios del plan de pago de Gemini en $ por millón de tokens (entrada, salida),
# según ai.google.dev/gemini-api/docs/pricing a 18-11-2026. El razonamiento se cobra como salida.
PRECIOS = {
    "gemini-3.8-flash": (0.75, 3.75),       # sube a 1,50 / 7,50 el 1-1-2027
    "gemini-3.5-flash-lite": (0.30, 2.50),
    "gemini-3.1-flash-lite": (0.25, 1.50),
}
SEGURIDAD = {"c13", "c14", "c16"}  # engaño al prompt, inyección de fórmula, datos personales


def resumir(modelo: str) -> dict:
    carpeta = AQUI / "resultados" / modelo
    metricas = json.loads((carpeta / "metricas.json").read_text())
    detalle: dict[str, list[str]] = {}
    with redirect_stdout(io.StringIO()):
        evaluar_respuestas(carpeta, detalle)
    ok = [m for m in metricas if "error" not in m]
    entrada = statistics.mean(m["tokens_entrada"] for m in ok) if ok else 0
    salida = statistics.mean(m["tokens_salida"] + m["tokens_razonamiento"] for m in ok) if ok else 0
    pe, ps = PRECIOS.get(modelo, (0, 0))
    return {
        "modelo": modelo,
        "superados": sum(1 for c in detalle.values() if not c),
        "evaluados": len(detalle),
        "errores_api": len(metricas) - len(ok),
        "fallos_seguridad": sorted(k for k, v in detalle.items() if k in SEGURIDAD
                                   and any("no debe incluir hoja" not in x for x in v)),
        "tokens_entrada": round(entrada),
        "tokens_salida": round(salida),
        "segundos_mediana": round(statistics.median(m["segundos"] for m in ok), 1) if ok else None,
        "coste_1000": round(1000 * (entrada * pe + salida * ps) / 1e6, 3),
        "detalle": detalle,
    }


def main(modelos: list[str]) -> None:
    filas = [resumir(m) for m in modelos]
    out = ["# Comparativa de modelos de Gemini · motor de Ansheets", "",
           "| Modelo | Casos superados | Fallos de seguridad | Tokens entrada / salida | Segundos (mediana) | Coste por 1.000 peticiones (plan de pago) |",
           "|---|---|---|---|---|---|"]
    for r in filas:
        seg = ", ".join(r["fallos_seguridad"]) or "ninguno"
        out.append(f"| {r['modelo']} | **{r['superados']}/20** (errores de API: {r['errores_api']}) | {seg} | "
                   f"{r['tokens_entrada']} / {r['tokens_salida']} | {r['segundos_mediana']} | {r['coste_1000']} $ |")
    out += ["", "Coste calculado con la media de tokens por petición. En el nivel gratuito, la prueba no cuesta nada.", ""]
    for r in filas:
        out.append(f"## {r['modelo']} · casos fallidos")
        fallidos = {k: v for k, v in r["detalle"].items() if v}
        out += [f"- **{k}**: {'; '.join(v)}" for k, v in fallidos.items()] or ["- ninguno"]
        out.append("")
    texto = "\n".join(out)
    (AQUI / "resultados" / "COMPARATIVA.md").write_text(texto, encoding="utf-8")
    print(texto)


if __name__ == "__main__":
    main(sys.argv[1:])
