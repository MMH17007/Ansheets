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
