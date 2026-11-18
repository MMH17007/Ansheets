# Motor de IA de Ansheets (Tarea 3)

Explicado sin tecnicismos: así convierte Ansheets una frase en una hoja de cálculo.

```
Usuario escribe            Modelo de IA                 Nuestro código                  Usuario descarga
"balance de enero:   →   devuelve una ESTRUCTURA   →   la revisa (validador) y    →   Excel con fórmulas vivas
 nómina 1800..."          (columnas, filas, fórmulas)   la convierte en .xlsx / CSV     o CSV con los valores
```

**Idea clave:** la IA no escribe el archivo Excel. Describe la tabla y nuestro código la construye. Así:
- **Las fórmulas no se rompen.** La IA escribe `=[Saldo@anterior]+[Ingreso]-[Gasto]` (con nombres de columna) y el código lo traduce a `=F2+D3-E3`. La IA nunca tiene que adivinar letras de columna.
- **Se ahorran tokens.** Exportar a CSV, Excel o PDF no vuelve a llamar a la IA.
- **Es más seguro.** El validador rechaza funciones peligrosas (`HYPERLINK`, `INDIRECT`, `WEBSERVICE`…) y guarda como texto cualquier dato del usuario que empiece por `=`, para evitar la inyección de fórmulas.

## Archivos

| Archivo | Qué es |
|---|---|
| `prompt_sistema.md` | Las instrucciones ocultas que lee la IA. **Es el archivo que tienes que revisar tú.** |
| `esquema_salida.json` | La "plantilla" exacta que debe rellenar la IA |
| `ansheets_motor.py` | Valida la respuesta y genera el Excel |
| `verificar.py` | Ejecuta todas las pruebas |
| `pruebas/ejemplos/` | 7 respuestas de referencia con los valores que deben salir |
| `pruebas/casos.json` | 20 peticiones para probar el modelo real (normales, con faltas, en inglés, fuera de tema, maliciosas…) |
| `pruebas/validador_negativos.json` | 12 respuestas incorrectas que el validador debe rechazar |
| `salidas/*.xlsx` | Los Excel generados a partir de los ejemplos. **Ábrelos para ver el resultado.** |

## Estado de las pruebas

- ✅ Los 6 ejemplos de hoja se exportan a Excel, LibreOffice recalcula las fórmulas y los 29 valores comprobados son correctos (saldos, IVA, totales, alertas de stock, estado de facturas, presupuesto en inglés).
- ✅ El ejemplo fuera de tema es válido (19 palabras).
- ✅ El validador rechaza las 12 respuestas incorrectas.
- ⏳ **Falta probar el modelo real con los 20 casos.** No ha sido posible porque la clave de Gemini conectada al entorno devuelve "permiso denegado".

Para ejecutar las pruebas: `python3 verificar.py`.
Para evaluar respuestas reales del modelo: `python3 verificar.py respuestas carpeta/`.
