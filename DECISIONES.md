# Registro de decisiones — Ansheets

Cada decisión indica quién la tomó, por qué y qué consecuencias tiene. Sirve como evidencia de **Discernimiento** y **Diligencia** para el curso AI Fluency.

---

## D1 · El plan gratuito tiene 10 peticiones al mes
- **Fecha:** 2026-11-18 · **Decide:** el director de producto
- **Alternativas:** 10 en total o 10 al día.
- **Por qué:** permite volver cada mes y ver el valor sin resolver todo el trabajo gratis.
- **Consecuencias:**
  - Hace falta **registro de usuario** (cuenta con email) para contar las peticiones de cada persona. Un contador solo en el navegador se salta borrando las cookies.
  - El contador se reinicia el día 1 de cada mes (más fácil de explicar que "30 días desde el registro").
  - Coste máximo por usuario gratuito: 10 llamadas a la IA al mes, y además acotadas por el *system prompt* (T3).

## D2 · La prueba Premium de 7 días no pide tarjeta
- **Fecha:** 2026-11-18 · **Decide:** el director de producto
- **Por qué:** coherente con los valores de honestidad y accesibilidad, y quita la fricción para probar.
- **Consecuencias:**
  - Al acabar la prueba **no se cobra nada**: la cuenta vuelve al plan gratuito y el usuario decide si paga. Desaparece el riesgo de "cobro sorpresa".
  - El aviso **antes de cada renovación** sigue siendo necesario para los que ya pagan.
  - **Riesgo:** alguien puede crear varias cuentas para encadenar pruebas. Mitigación: verificación de email y una sola prueba por email. No lo bloqueamos más, porque el coste por abuso es bajo.
  - **A medir:** la conversión de prueba a pago suele ser más baja sin tarjeta, así que los avisos de los días 5 y 7 ("tu prueba acaba en 2 días") importan.

## D3 · Casos de uso prioritarios
- **Fecha:** 2026-11-18 · **Decide:** el director de producto (aprueba la propuesta de Claude)
- Balance mensual personal, gastos de autónomo (con IVA), inventario/stock y seguimiento de facturas.
- Son los ejemplos de referencia del motor (`motor/pruebas/ejemplos/`).

## D4 · Las hojas incluyen fórmulas que funcionan
- **Fecha:** 2026-11-18 · **Decide:** el director de producto
- **Por qué:** es lo que da valor a la exportación a Excel del plan Premium.
- **Cómo (decisión técnica de Claude):** la IA describe las fórmulas con nombres de columna (`[Ingreso]`) y el código las traduce a referencias reales (`D3`). Solo se permiten funciones de una lista cerrada (IF, AND, OR, ROUND, ABS, MIN, MAX, TODAY y los totales SUM, AVERAGE, MIN, MAX, COUNT).
- **Consecuencia:** el **CSV** del plan gratuito llevará los **valores ya calculados**, no fórmulas. Un CSV no guarda fórmulas de forma fiable y, si las llevara, sería un riesgo de seguridad. El Excel lleva las fórmulas vivas.

## D5 · Idiomas: español e inglés
- **Fecha:** 2026-11-18 · **Decide:** el director de producto
- Se responde en el idioma del usuario. Si escribe en otro idioma, se responde en inglés y se avisa de que por ahora solo hay español e inglés.
- Moneda por defecto: EUR en español y USD en inglés, salvo que el usuario indique otra (EUR, USD o GBP).

## D6 · Prueba de modelos de Gemini (nivel gratuito)
- **Fecha:** 2026-11-18 · **Decide:** el director de producto (empezar por Gemini, que es gratis)
- **Resultados con el prompt v1:** 3.1 Flash-Lite superó 16 de 20 casos (0,73 $ cada 1.000 peticiones en el plan de pago); 3.5 Flash-Lite, 12 de 20 (1,02 $).
- **Descartados:** 2.5 Flash-Lite (Google ya no lo ofrece a usuarios nuevos) y 3.8 Flash (servidores saturados: solo respondió 2 de 12 peticiones en una hora).
- **Corrección de Claude:** la prueba del caso c02 era demasiado estricta (exigía "gasto" en una columna aunque el título fuera "Gastos de Enero"). Se corrigió.

## D7 · Prompt v2 y elección del modelo más barato
- **Fecha:** 2026-11-18 · **Decide:** el director de producto ("mejora el prompt y repite con el más barato")
- **Cambios en el prompt:**
  - Sin campo `hoja` cuando la respuesta no es una hoja.
  - El idioma lo decide el usuario.
  - No inventar fechas ni otros datos.
  - Ingreso/Gasto/Saldo en los balances y Presupuestado/Real/Diferencia en los presupuestos.
  - Divisiones protegidas.
  - Columnas con fórmula siempre a null.
- **Resultado con Gemini 3.1 Flash-Lite:** de **16/20 a 18/20**, sin fallos de seguridad.
- **Coste:** igual (0,74 $ cada 1.000 peticiones): el prompt es más largo (+30 % de tokens de entrada), pero las respuestas son más cortas.
- **Velocidad:** pasa de 1,4 a 2,2 s de mediana.
