# Pendientes para entrega 2 — presentación 2 (8 de mayo)

Esta entrega NO requiere código. Es revisión de fuentes + discusión metodológica + diapositivas. Lo que sí podés (y conviene) hacer es **incorporar los hallazgos del POC al bloque metodológico** como prueba de viabilidad del pipeline.

Dos referencias al lado mientras armás la entrega:
- `Guía de lectura.pdf` (la consigna, en `tpi-ipc-segmentado/sota_candidates/` o donde la tengas).
- El presente documento.

---

## Etapa 1 — Ficha de lectura profunda (Suzuki 2020)

**Tiempo estimado**: 3 sesiones de 2 horas cada una (lun-mar-mié de la semana 1).

**Producto**: una ficha estructurada con seis bloques (info general, problema, método, resultados, limitaciones, ideas clave).

### Checklist de la ficha

- [ ] **Bloque 1 — Información general**: cita completa, journal, contexto del paper, cuál es el "lugar" del paper en su literatura.
- [ ] **Bloque 2 — Problema**: qué pregunta responde Suzuki, cuál es el debate previo, qué hueco identifica.
- [ ] **Bloque 3 — Método**: variables que usa Suzuki para LCA, criterios de selección de k, cómo valida el modelo. **Subrayá lo que vos vas a usar igual y lo que vas a hacer distinto** — sirve para la presentación.
- [ ] **Bloque 4 — Resultados**: qué clases encuentra, qué dice de cada una. Tomá notas comparativas con tus propias clases del POC (obreros formales, informales jóvenes, mayores con primario, profesionales asalariadas, cuentapropistas).
- [ ] **Bloque 5 — Limitaciones**: las que el autor declara y las que vos detectás como lector crítico.
- [ ] **Bloque 6 — Ideas clave**: tres a cinco bullets de qué te llevás para tu propio trabajo.

### Tip de lectura

Suzuki usa LCA en Japón. Vos en Argentina. Mientras leés, anotá:
- Variables indicadoras suyas vs tuyas (probablemente parecidas: educación, categoría ocupacional, formalidad, etc.).
- Qué hace **igual** que vos: identificar tipos de trabajadores con LCA.
- Qué hace **distinto**: él estudia salarios *como output* de las clases; vos estudiás *inflación enfrentada* (vía D-CPI). Esa diferencia es tu aporte original sobre Suzuki, y conviene subrayarla.

---

## Etapa 2 — Contraste con LLM

**Tiempo estimado**: 1 sesión de 2 horas (viernes de la semana 1).

**Producto**: prompts y respuestas guardados, más una reflexión escrita sobre los puntos en que el LLM coincidió/disintió con tu lectura.

### Sugerencias prácticas

- Prepará 3-4 prompts específicos antes de la sesión:
  1. Pedile al LLM un resumen ciego del paper (sin tu interpretación previa).
  2. Pedile que critique el método LCA aplicado al mercado laboral.
  3. Pedile que sugiera cómo extender Suzuki al caso argentino con la ENGH como ponderación de canasta.
- Comparalo con tu propia ficha. Anotá divergencias.
- Documentá ambos: *"el LLM enfatizó X que yo había subestimado"*; *"el LLM omitió Y que es central en la lectura humana"*.

Esto es trabajo de prosa, no de código. Es una hora bien invertida porque la consigna lo pide explícitamente.

---

## Etapa 3 — Discusión metodológica (los 5 bloques)

**Tiempo estimado**: 1-2 sesiones (miércoles de la semana 2).

**Producto**: respuestas a los cinco bloques de la guía de lectura, cada uno con 2-4 párrafos.

### Bloque A — Diseño

Comentar el diseño del estudio de Suzuki: ¿es transversal o longitudinal? ¿Qué unidad de análisis? ¿Qué supuestos hace? Conexión con tu trabajo: vos también es transversal con extensión al panel rotativo, unidad individuo ocupado, supuesto de estabilidad estructural de las clases.

### Bloque B — Datos

¿Qué datos usa Suzuki, cómo los caracteriza? ¿Hay limitaciones de los datos que afectan los resultados? Conexión con tu trabajo: la EPH y la ENGH como fuentes; las limitaciones de cada una (sub-reporte de ingresos, una sola ola de la ENGH, asimetría de variables comunes).

### Bloque C — Reproducibilidad

¿Qué tan reproducible es el trabajo de Suzuki? ¿Publica código, datos, decisiones? Conexión con tu trabajo: tu pipeline está documentado en notebooks (00, 01, 02, 03, 04), tu código está en GitHub, tus decisiones de filtrado y mapeo están explícitas en cada notebook. **Acá podés citar tu propio POC como ejemplo de reproducibilidad**.

### Bloque D — Transferibilidad

**Este es el bloque clave**: "¿cómo realizarías este estudio en Argentina?". La respuesta es literalmente tu proyecto. Estructura sugerida:

1. **Insumo de canasta**: ENGH 2017/18, una sola ola, 21.547 hogares. Limitación: no permite ver evolución temporal de la canasta.
2. **Insumo de perfil de trabajador**: EPH continua 2017+ (~80k personas por trimestre). Permite armar variables ricas para LCA.
3. **Puente**: como no existe el mismo hogar en ambas encuestas, statistical matching con Random Forest. Variables comunes pobres, supuesto crítico CIA.
4. **Resultado intermedio del POC**: 5 clases interpretables, accuracy del matching ≈ 0.83, D-CPI por clase con dinámica visible en 2024 (~5 pp de spread).
5. **Limitaciones declaradas**: las del POC.

### Bloque E — Propuestas

¿Qué propondrías para profundizar el trabajo? Acá entra la lista del HOJA_DE_RUTA.md: análisis de sensibilidad, comparación con deciles, supervised LCA, BRR para errores estándar, etc.

### Diapositiva sugerida — el "money slide"

En la presentación, una sola diapositiva debería resumir el bloque D. Sugerencia de contenido:

```
¿Cómo realizarías este estudio en Argentina?

Datos:    EPH continua 2017+  +  ENGH 2017/18  +  IPC INDEC mensual
                  |                   |                  |
Unidad:    Trabajador            Hogar              Mes × división
                  |                   |                  |
              [LCA] ─────────► [Matching RF] ──────► [D-CPI/clase]

Hallazgo del POC:
- 5 clases latentes interpretables
- Matching con accuracy ≈ 0.83
- Heterogeneidad acumulada: ~1 pp en 8 años
- Heterogeneidad en 2024 (post-shock): 5 pp de spread entre clases
- Reproduce el sesgo "anti-rico" de Lódola para regímenes de inflación alta

Limitación crítica: CIA no testeable
```

---

## Diapositivas — armado final (jueves 7 mayo)

**Tiempo estimado**: media jornada.

### Estructura sugerida (10–12 diapositivas)

1. **Título**.
2. **Contexto**: el problema del IPC promedio. Una línea sobre el OUE para mostrar que la actualización de canasta es un debate vivo.
3. **Pregunta de investigación**: la versión actual (no reformulada).
4. **Aporte distintivo**: clustering no supervisado en lugar de deciles. Citar Schneider & Scharfenaker.
5. **Pipeline conceptual**: diagrama LCA → matching → D-CPI → deflactación.
6. **Ficha de Suzuki — 2 diapositivas**: qué hace, cómo se conecta.
7. **Etapa 3 — bloque D ("money slide")**: el resumen del POC y su transferibilidad al caso argentino.
8. **Resultados preliminares del POC** (1-2 diapositivas): figura `02_shares_by_class.png`, figura `07_three_way_comparison.png` y un par de números clave.
9. **Limitaciones**: la lista del POC.
10. **Trabajo futuro**: la sección de tesina del HOJA_DE_RUTA.md.

### Checklist de las diapositivas

- [ ] Cada gráfico se entiende sin necesidad de explicación oral (título descriptivo, ejes legibles, leyenda visible).
- [ ] No hay diapositivas con 5+ bullets de texto. Una idea por diapositiva.
- [ ] Hay al menos un slide con un número impactante en grande (e.g., "5 pp de spread interanual entre profesionales y mayores con primario en dic 2024").
- [ ] La cita de Suzuki, Donatiello, Schneider & Scharfenaker, Lódola, Jaravel y Rosati está pegada en algún lado (slide de fuentes o pie de página).

---

## Lecturas paralelas (en orden de prioridad)

| Paper | Cuándo | Tiempo | Por qué |
|---|---|---|---|
| **Suzuki (2020)** | Lun-Mié sem. 1 | 6 h | El paper de la ficha. Profundo. |
| **Donatiello et al. (2014)** | Mar sem. 2 | 1.5 h | Espejo del statistical matching. Para Bloque D. |
| **Weller, Bowen & Faubert (2020)** | Si te quedás trabado en LCA | 1 h | Glosario práctico de criterios LCA. |
| **Nylund, Asparouhov & Muthén (2007)** | En diagonal | 0.5 h | Una cita para BIC > AIC + BLRT. |
| **Schneider & Scharfenaker (2020)** | Lun sem. 2 | 2 h | Munición contra "¿por qué no usaste deciles?". |
| **Webber & Tonkin / Eurostat (2013)** | Optativo | 0.5 h | Para mencionar como comparativa de métodos. |

---

## Lo que NO entra en entrega 2

Para que no te disperses:

- **Implementación de los refinamientos del HOJA_DE_RUTA.md** — eso es entrega 3.
- **Sub-item de LCA en ENGH como extensión** — entrega 3 si llegás, sino tesina.
- **Errores estándar formales, BRR, supervised LCA, multiple imputation** — todo eso es tesina.
- **Reformulación de la pregunta de investigación** — la pregunta original sigue válida.
- **Lectura de bibliografía secundaria** que no esté en la lista de arriba — guardala para más adelante.

---

## Cronograma minimalista

| Día | Tarea |
|---|---|
| Lun 28 abr | Empezar Suzuki — sesión 1 (introducción, problema, datos) |
| Mar 29 abr | Suzuki — sesión 2 (método, resultados) |
| Mié 30 abr | Suzuki — sesión 3 (limitaciones, ideas clave) → ficha terminada |
| Jue 1 may | (feriado — descanso o repaso ligero) |
| Vie 2 may | Etapa 2 — sesión LLM contrastando la ficha |
| Sáb 3 may | Lectura ligera: Weller (glosario LCA si hace falta) |
| Dom 4 may | Descanso |
| Lun 5 may | Schneider & Scharfenaker + leer Donatiello en diagonal |
| Mar 6 may | Etapa 3 — escribir los 5 bloques |
| Mié 7 may | Armado de diapositivas |
| Jue 8 may | **Entrega 2** |

Si el lunes 5 termina con Suzuki bien leído y Donatiello mapeado, llegás holgado.
