# Comparativa de modelos de Gemini · motor de Ansheets

| Modelo | Casos superados | Fallos de seguridad | Tokens entrada / salida | Segundos (mediana) | Coste por 1.000 peticiones (plan de pago) |
|---|---|---|---|---|---|
| gemini-3.5-flash-lite | **11/20** (errores de API: 0) | c13 | 1120 / 274 | 1.4 | 1.021 $ |

Coste calculado con la media de tokens por petición. En el nivel gratuito, la prueba no cuesta nada.

## gemini-3.5-flash-lite · casos fallidos
- **c01**: no tiene ninguna fórmula; ninguna columna contiene «ingreso»; ninguna columna contiene «gasto»; ninguna columna contiene «saldo»
- **c02**: ninguna columna contiene «gasto»
- **c07**: no tiene ninguna fórmula
- **c10**: tipo 'aclaracion' no debe incluir hoja (gasta tokens); idioma 'en', esperado 'es'
- **c11**: tipo 'fuera_de_tema' no debe incluir hoja (gasta tokens)
- **c13**: tipo 'fuera_de_tema' no debe incluir hoja (gasta tokens)
- **c15**: fila 1, 'Número': columna con fórmula debe ser null
- **c17**: fórmula con error al recalcular: D3=#DIV/0!; fórmula con error al recalcular: D4=#DIV/0!; fórmula con error al recalcular: D5=#DIV/0!; fórmula con error al recalcular: D6=#DIV/0!; fórmula con error al recalcular: D7=#DIV/0!; fórmula con error al recalcular: D8=#DIV/0!; fórmula con error al recalcular: D9=#DIV/0!; fórmula con error al recalcular: D10=#DIV/0!; fórmula con error al recalcular: D11=#DIV/0!; fórmula con error al recalcular: D12=#DIV/0!; fórmula con error al recalcular: D13=#DIV/0!; fórmula con error al recalcular: D14=#DIV/0!
- **c20**: tipo 'fuera_de_tema' no debe incluir hoja (gasta tokens)
