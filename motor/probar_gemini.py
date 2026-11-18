"""Ejecuta las 20 peticiones de pruebas/casos.json contra modelos de Gemini.

Uso: python3 probar_gemini.py gemini-3.8-flash [otro-modelo ...]

Guarda cada respuesta en resultados/<modelo>/cNN.json y las métricas (tokens,
segundos, errores) en resultados/<modelo>/metricas.json. La clave la añade el
proxy del entorno en la cabecera x-goog-api-key: este script no la ve nunca.
"""
from __future__ import annotations

import datetime as dt
import json
import pathlib
import sys
import time
import urllib.error
import urllib.request

AQUI = pathlib.Path(__file__).parent
URL = "https://generativelanguage.googleapis.com/v1beta/models/{modelo}:generateContent"

PROMPT = (AQUI / "prompt_sistema.md").read_text(encoding="utf-8")
ESQUEMA = json.loads((AQUI / "esquema_salida.json").read_text(encoding="utf-8"))
for k in ("$schema", "title"):
    ESQUEMA.pop(k, None)


def _simplificar(nodo):
    """Gemini rechaza esquemas con muchos límites (maxItems, maxLength...).
    Los quitamos aquí: el validador de ansheets_motor.py ya los comprueba después."""
    if isinstance(nodo, dict):
        return {k: _simplificar(v) for k, v in nodo.items()
                if k not in {"maxItems", "minItems", "maxLength", "minimum", "maximum"}}
    if isinstance(nodo, list):
        return [_simplificar(v) for v in nodo]
    return nodo


ESQUEMA = _simplificar(ESQUEMA)
CASOS = json.loads((AQUI / "pruebas" / "casos.json").read_text(encoding="utf-8"))


def llamar(modelo: str, peticion: str) -> tuple[dict, float]:
    cuerpo = {
        "systemInstruction": {"parts": [{"text": PROMPT}]},
        "contents": [{"role": "user", "parts": [{"text": f"(Fecha de hoy: {dt.date.today().isoformat()})\n{peticion}"}]}],
        "generationConfig": {
            "responseMimeType": "application/json",
            "responseJsonSchema": ESQUEMA,
            "maxOutputTokens": 16000,
        },
    }
    req = urllib.request.Request(
        URL.format(modelo=modelo), data=json.dumps(cuerpo).encode(),
        headers={"Content-Type": "application/json"}, method="POST",
    )
    for intento in range(6):
        inicio = time.monotonic()
        try:
            with urllib.request.urlopen(req, timeout=180) as r:
                return json.load(r), time.monotonic() - inicio
        except urllib.error.HTTPError as e:
            detalle = e.read().decode(errors="replace")[:300]
            if e.code in (429, 500, 503) and intento < 5:
                espera = 20 * (intento + 1)
                print(f"   {e.code}, reintento en {espera}s", flush=True)
                time.sleep(espera)
                continue
            raise RuntimeError(f"HTTP {e.code}: {detalle}") from None
    raise RuntimeError("sin respuesta tras reintentos")


def probar(modelo: str) -> None:
    destino = AQUI / "resultados" / modelo
    destino.mkdir(parents=True, exist_ok=True)
    metricas = []
    for caso in CASOS:
        print(f"{modelo} · {caso['id']}", flush=True)
        fila = {"id": caso["id"]}
        try:
            datos, segundos = llamar(modelo, caso["peticion"])
            uso = datos.get("usageMetadata", {})
            fila |= {
                "segundos": round(segundos, 2),
                "tokens_entrada": uso.get("promptTokenCount", 0),
                "tokens_salida": uso.get("candidatesTokenCount", 0),
                "tokens_razonamiento": uso.get("thoughtsTokenCount", 0),
                "fin": (datos.get("candidates") or [{}])[0].get("finishReason"),
            }
            texto = "".join(p.get("text", "") for p in datos["candidates"][0]["content"]["parts"]
                            if not p.get("thought"))
            (destino / f"{caso['id']}.json").write_text(texto, encoding="utf-8")
        except Exception as e:  # se registra y se sigue con el siguiente caso
            fila["error"] = str(e)[:300]
            print(f"   ERROR {fila['error']}", flush=True)
        metricas.append(fila)
        time.sleep(4)  # respeta el límite de peticiones por minuto del nivel gratuito
    (destino / "metricas.json").write_text(json.dumps(metricas, indent=1), encoding="utf-8")


if __name__ == "__main__":
    for m in sys.argv[1:]:
        probar(m)
