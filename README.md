# tpi-ipc-segmentado

## problemática

El IPC en Argentina no muestra el detalle de cómo afecta el incremento de precios en los diferentes segmentos de la sociedad. En el presente trabajo la propuesta es segmentar el IPC por grupo social y determinar si hoy en día hay actores más vulnerables que otros.

## motivación

El sentimiento social de que la inflación no representa eficientemente lo que sucede en la clase trabajadora.

## papers a estudiar

[Distributional Consumer Price Indices (Xavier Jaravel)](https://events.berkeley.edu/live/files/26-dcpipdf)

[Distributional Impacts of Inflation Accounting for Behavioral Effects and Real Assets (Cicek et al)](https://www.imf.org/-/media/files/publications/wp/2026/english/wpiea2026022-source-pdf.pdf)

[Sesgos en el Índice de Precios al Consumidor: El Sesgo Plutocrático en Argentina (Lódola, Busso, Cerimedo)](https://cdi.mecon.gob.ar/bases/doc/aaep/cong/00/lodola_busso_cerimedo.pdf)

## Pregunta central

> *¿Cuál es la tasa de inflación real que enfrenta cada perfil de trabajador argentino, y qué tan vulnerable es su situación laboral cuando se mide con ese índice personalizado en lugar del IPC oficial?*

## Datos

| Fuente | Uso |
|---|---|
| EPH (INDEC) — microdatos panel | Perfiles de trabajadores, salarios, situación laboral |
| ENGH (Encuesta Nac. de Gastos de Hogares) | Estructura de gasto por perfil → ponderadores del IPC |
| IPC por categoría (INDEC) | Precios desagregados por rubro |
| RIPTE, tipo de cambio, tarifas | Variables proxy del contexto macro |

### otros recursos:
- https://ropensci.github.io/eph/
- https://www.diariouno.com.ar/economia/el-metodo-medir-la-inflacion-es-unico-el-mundo-dijo-josefina-rim-quien-calculara-el-ipc-del-indec-n1468702
- https://www.cadena3.com/noticia/politica-y-economia/el-gobierno-posterga-la-nueva-metodologia-para-medir-la-inflacion-en-el-ipc_515160
- https://www.infobae.com/economia/2026/01/03/nueva-formula-para-medir-la-inflacion-que-cambios-implementara-el-indec-para-calcular-los-precios-a-partir-de-este-mes/

---
## con ayuda de claude:

### Arquitectura metodológica

**Paso 1 — Segmentación de perfiles laborales** (Clustering, EPH)
Identificar grupos de trabajadores según sector, formalidad, decil de ingreso, región. No categorías predefinidas — que los datos las encuentren.

**Paso 2 — IPC personalizado por cluster** (ENGH + IPC por rubro)
Cada cluster tiene su estructura de gasto → su propia canasta → su propia tasa de inflación. Esto es la contribución metodológica central.

**Paso 3 — Revaluación del salario real**
Deflactar el salario de cada trabajador con *su* IPC, no el oficial. Comparar la foto resultante con la que da el IPC agregado. Mostrar quién queda mejor y peor parado en cada lectura.

**Paso 4 — Índice de vulnerabilidad laboral**
Combinar la pérdida de salario real ajustada con variables de precariedad (informalidad, subempleo, rama de actividad) para construir un índice compuesto. ML para identificar qué factores predicen mayor vulnerabilidad.

---

### El aporte concreto

Tres cosas que este trabajo haría que no están hechas juntas para Argentina:

1. Construir IPCs segmentados con datos recientes usando clustering en lugar de categorías administrativas
2. Revaluar la pérdida salarial real con esos índices personalizados
3. Mostrar que el debate "la inflación subió/bajó" es incompleto sin especificar *para quién*


---

## brainstorming

Jaraval y Lodola et al hablan de IPC distribuido por decil de ingresos. Ambos encuentran como resultado que el IPC distribuido muestra de manera desagregada los índices de inflacion para cada segmento de la población. De nuevo, esto si consideramos sólo a la población según decil de ingresos.

La idea es obtener de la EPH y de la ENGH grupos más complejos con ayuda de ML y a estos grupos darle su propio IPC, según su canasta de gastos.

Con la serie de tiempo de cada IPC de cada grupo el siguiente paso sería deflactar el ingreso y analizar la variación del poder adquisitivo.

Surgen muchas preguntas...

1. Del EPH, uso los microdatos individuales o de hogar?
2. Cómo me ayuda o complementa la EPH con la ENGHo?
3. Cómo conecto los grupos/clusters que encontramos con ML con las categorías que tengo de la canasta del IPC?

Y muchas otras más que iran surgiendo...