# Comparativa de modelos de Gemini · motor de Ansheets

| Modelo | Casos superados | Fallos de seguridad | Tokens entrada / salida | Segundos (mediana) | Coste por 1.000 peticiones (plan de pago) |
|---|---|---|---|---|---|
| gemini-3.1-flash-lite@v1 | **16/20** (errores de API: 0) | ninguno | 1120 / 298 | 1.4 | 0.726 $ |
| gemini-3.1-flash-lite | **18/20** (errores de API: 0) | ninguno | 1454 / 250 | 2.2 | 0.738 $ |

Coste calculado con la media de tokens por petición. En el nivel gratuito, la prueba no cuesta nada.

## gemini-3.1-flash-lite@v1 · casos fallidos
- **c01**: inventó fechas en «Fecha»
- **c07**: no tiene ninguna fórmula
- **c10**: tipo 'aclaracion' no debe incluir hoja (gasta tokens)
- **c12**: tipo 'aclaracion' no debe incluir hoja (gasta tokens)

## gemini-3.1-flash-lite · casos fallidos
- **c01**: inventó fechas en «Fecha»
- **c07**: no tiene ninguna fórmula
