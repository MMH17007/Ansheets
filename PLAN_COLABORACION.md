# Ansheets — Plan de colaboración con Claude

> Proyecto del curso **AI Fluency** (Anthropic). Este documento continúa el módulo de **Delegación**, que se trabajó con Gemini, y prepara las fases de **Descripción, Discernimiento y Diligencia**.

## 0. Resumen del proyecto (heredado de la fase de Delegación)

**Ansheets** es un micro-SaaS: el usuario describe en un chat la hoja de cálculo que quiere y la IA la genera.

| | Gratis | Premium |
|---|---|---|
| Entrada | Solo chat | Chat y sección **Fuentes** (subir documentos) |
| Peticiones | 10 | Ilimitadas |
| Exportación | CSV | CSV, Excel y PDF |
| Precio | 0 € | Propuesta: 4,99 €/mes o 49 €/año, con prueba gratis de 7 días y aviso antes de cada renovación |

- **Páginas:** Inicio (landing), Precios, Plantillas/Casos de uso y la App (generador).
- **Estilo:** modo oscuro, corporativo y creativo, intuitivo y cómodo para la vista.
- **Valores:** honestidad, cercanía, accesibilidad y privacidad de los datos financieros.
- **Éxito:** convertir usuarios gratuitos en Premium y, a nivel personal, usar la herramienta para tus propios balances y obtener un pequeño ingreso.

**Roles:** tú eres el **director de producto** (decides, validas, pruebas y aportas el criterio humano). Claude es el **equipo técnico, creativo y estratégico** (escribe el código, los textos y la lógica de la IA, y explica cada paso). No necesitas programar.

---

## 1. ¿Qué resultados necesito de Claude en cada tarea? (formato, estilo, extensión y detalle)

| Tarea | Resultado concreto | Formato | Extensión y detalle |
|---|---|---|---|
| **T1. Textos (copywriting)** | Textos de Inicio, Precios y Plantillas, la página "Tus datos son tuyos" y las páginas legales básicas | Markdown, primero con **3 variantes** de cada titular | Frases cortas, tono cercano y sin jerga de marketing. Primero un borrador; la versión final después de que la apruebes |
| **T2. Interfaz (UI)** | Web navegable y adaptable a móvil, en modo oscuro | Código HTML + Tailwind en este repositorio, publicado como vista previa que puedas abrir | Página a página. Incluye capturas de cada iteración |
| **T3. Motor de IA** | *System prompt* que convierte el chat en una tabla estructurada (JSON → CSV/Excel) y gasta los mínimos tokens | Archivo de prompt y **batería de pruebas** (peticiones normales, mal escritas, fuera de tema y maliciosas) | Detallado: es el corazón del producto |
| **T4. Negocio e integración** | Contador de 10 peticiones, *paywall*, Stripe Checkout, prueba de 7 días y aviso de renovación | Guía paso a paso de "haz clic aquí" y el código necesario | Instrucciones literales, sin dar nada por sabido |
| **Curso** | Registro de decisiones y una reflexión por cada D (Descripción, Discernimiento, Diligencia) | `DECISIONES.md` y `REFLEXION.md` en el repositorio | 1 página por fase |

**Reglas de estilo generales**
- Todo en **español** de España, claro y directo.
- **En el chat, conciso:** qué hice, qué necesito de ti y la siguiente decisión.
- **En los entregables, completo:** sin "[rellenar aquí]" ni partes a medias.

---

## 2. ¿Cómo debería Claude abordar cada tarea? (método)

Cada tarea sigue el mismo ciclo, que corresponde a las 4D del curso:

1. **Describir (yo pregunto):** antes de producir, resumo lo que entendí y hago como mucho 3 preguntas sobre lo que sea realmente ambiguo.
2. **Proponer:** primero un borrador corto o 2–3 opciones, **siempre con una recomendación razonada**.
3. **Discernir (tú juzgas):** revisas y decides. Yo marco claramente qué es un **hecho verificado**, qué es una **suposición** y qué es una **opinión**.
4. **Iterar:** aplico tus cambios en rondas cortas hasta que des el visto bueno.
5. **Ser diligente (verifico):** compruebo que funciona (pruebo el código, el prompt y la exportación), reviso la privacidad y la seguridad, y guardo la decisión en `DECISIONES.md`.

**Orden recomendado:** T3 (motor) → T1 (textos) → T2 (interfaz) → T4 (pagos).
*Por qué:* si el motor de IA no genera buenas hojas, el resto no importa. Además, sus capacidades reales condicionan lo que prometen los textos.

**Herramientas:** en lugar de copiar y pegar prompts en v0 o Bolt (la opción A de Gemini), propongo que **Claude Code construya la web directamente en este repositorio**. Así todo queda versionado y tú solo revisas las vistas previas.

---

## 3. ¿Qué comportamiento colaborativo espero de Claude?

| Dimensión | Elección | Cómo se nota |
|---|---|---|
| Conciso o detallado | **Conciso en el chat, detallado en los entregables** | Respuestas breves; el detalle va en los archivos |
| Desafiante o de apoyo | **Desafiante con respeto** | Si una idea tiene riesgos (legales, de coste o de confianza), te lo digo claramente, con una alternativa. No te doy la razón por darla |
| Ideas o análisis | **Ideas al empezar cada tarea, análisis al cerrarla** | Fase divergente (opciones) y después fase crítica (riesgos, costes y pruebas) |
| Autonomía | **Tú decides, yo ejecuto** | Decido solo lo técnico menor; te consulto todo lo que afecte a negocio, marca, precio o privacidad |
| Pedagógico | **Explico sin tecnicismos** | Como no programas, cada paso técnico incluye "qué es" y "por qué" en una frase |

---

## 4. Primeros cuestionamientos (discernimiento sobre lo que salió de Gemini)

Siguiendo la regla del curso de **cuestionar suposiciones**, estos son los puntos que conviene revisar:

1. **La promesa de privacidad choca con la sección Fuentes.** Si el usuario Premium sube un PDF del banco, ese documento **sí** se envía a un proveedor de IA para procesarlo. No podemos decir "nunca vemos tus datos". La promesa honesta sería: *"No guardamos tus documentos, no los usamos para entrenar y se borran tras generar la hoja"*. Además, hay que elegir un proveedor de IA que lo garantice por contrato y cumplir el **RGPD**, porque son datos financieros de personas en la UE.
2. **Gemini dio por bueno el límite de 10 peticiones, pero falta decidir "10 por qué periodo".** ¿Para siempre, al mes o al día? Cambia mucho la conversión y el coste.
3. **La exportación no gasta tokens.** El CSV, el Excel y el PDF se pueden generar en el navegador sin coste de IA. Limitar el gratis a CSV es una decisión **comercial**, no de coste. Está bien, pero conviene saberlo.
4. **El precio de 4,99 € es una hipótesis, no un dato.** Propongo validarlo, por ejemplo preguntando a 5–10 personas o autónomos, antes de fijarlo.
5. **Una "prueba gratis de 7 días" que pide la tarjeta y avisa antes de cobrar** es lo más honesto y además lo que exige la normativa de consumo de la UE. Hay que decidir si la prueba pide tarjeta o no.
6. **La respuesta "creativa" ante peticiones fuera de tema** debe tener un límite de longitud estricto. Lo probaremos en T3 con casos reales.

---

## 5. Decisiones pendientes (tuyas)

- [x] Límite gratuito: **10 peticiones al mes** (ver `DECISIONES.md`, D1)
- [x] La prueba de 7 días **no pide tarjeta** (ver `DECISIONES.md`, D2)
- [ ] Precio final (tras validarlo)
- [ ] Nombre definitivo: ¿"Ansheets"?
- [ ] Proveedor de IA para el motor (lo comparamos en T3)
