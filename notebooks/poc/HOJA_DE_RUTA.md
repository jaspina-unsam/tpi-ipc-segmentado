# Hoja de ruta — del POC a la entrega final

Este documento traduce los aprendizajes del POC en plan concreto para las próximas dos entregas.

**Fecha del documento**: 28 de abril de 2026
**Próximas fechas**: presentación 2 el 8 de mayo, entrega final fines de mayo.

---

## Resumen ejecutivo de lo que aprendimos en el POC

Tres aprendizajes que cambian o consolidan supuestos del proyecto:

1. **El pipeline corre y produce resultados defendibles**. LCA → matching → D-CPI → deflactación. Cada pieza por separado funciona; la integración funciona.

2. **La heterogeneidad por perfil existe pero es modesta en magnitud acumulada (~1 pp en 8 años)** y mucho más visible en los momentos de shock (5–6 pp de spread interanual entre clases en 2023–2024). La narrativa central del proyecto se reformula así: "la heterogeneidad no es un atributo permanente, es un atributo de los shocks".

3. **El POC replica dentro de su pipeline dos hallazgos clásicos**:
   - El efecto OUE-La Pampa (canasta nueva vs vieja, ~6 pp en 2024).
   - El sesgo "anti-rico" de Lódola para regímenes de inflación alta (las profesionales asalariadas enfrentaron más inflación que los obreros con primario en 2024).

Estos resultados son munición para la presentación 2 y consolidan el rumbo del proyecto. **No hace falta pivotar a LCA en ENGH ni reformular la pregunta de investigación**.

---

## Para entrega 3 (modelado, segunda mitad de mayo)

La entrega 3 es la implementación robusta del pipeline. La diferencia con el POC es que cada decisión que en el POC fue arbitraria, en la entrega 3 hay que justificarla o someterla a análisis de sensibilidad.

### Bloque A — Refinamientos del LCA en EPH

**A1. Probar k = 4, 5, 6, 7 con curva BIC completa** (n_init mayor, e.g. 10) y reportar la curva con confianza, no con un único corrida.

**A2. Considerar agregar el ingreso como variable indicadora**. Discretizarlo en quintiles (con `PONDERA`, no equal-frequency). Ventaja: clases más diferenciadas en perfil y, probablemente, en canastas. Costo: el matching tiene que incluir un equivalente de ingreso de la ENGH (`ingtoth`, que existe). Probarlo en una variante y comparar accuracy del RF.

**A3. Análisis de sensibilidad por subset de variables**. Correr LCA con (a) las 6 originales, (b) sin `REGION`, (c) sin `FORMAL`, (d) con un agrupamiento alternativo de `EDAD_GRP`. Mostrar tabla con tamaños de clase y BIC. Si las clases siguen siendo interpretables, robustez ✓.

**A4. Estabilidad temporal**. Reentrenar el LCA año por año (2017, 2019, 2021, 2023) y verificar que las clases tienen perfiles parecidos en el tiempo. Si la composición cambia mucho entre años, declararlo como limitación.

**A5. Caracterización rica de las clases** usando variables de la ENGH que **no entraron** al matching: `califica`, `jer_ocup`, `caracter_ocup`. Esto es post-hoc — sirve para validar que las clases imputadas en ENGH tienen perfiles laborales coherentes con su nombre.

### Bloque B — Refinamientos del matching

**B1. Sumar variables del hogar al matching**. `cantmiem`, `menor14`, `mayor65`, `regten`, `tipohog` están en ambas encuestas. Añadirlas al feature set del RF y reportar el cambio en accuracy.

**B2. Pseudo-validación de la CIA**. Entrenar el RF con tres combinaciones distintas de variables comunes (e.g., 5 originales, +ingreso, +variables hogar) y mostrar que las shares promedio por clase son **estables**. Si las shares cambian mucho según el set de variables comunes, la CIA está apoyada en una variable específica → frágil. Si son estables → el matching no depende de un solo predictor.

**B3. Comparar RF con baseline más simple**. Implementar también un matching por celda (hot-deck dentro de celda definida por sexo × edad × niveled × cat_ocup) y comparar shares resultantes. Ventaja: si los dos métodos coinciden en las shares, el RF no está alucinando.

**B4. Multinomial logistic regression** como alternativa interpretable. La librería `sklearn` lo soporta. Útil para mostrar coeficientes y para que la cita metodológica sea más amplia (no sólo Random Forest).

### Bloque C — Refinamientos del D-CPI

**C1. Mantener tres deflactores en paralelo**:
   - IPC oficial publicado (canasta 2004/05) — la referencia "del telediario".
   - IPC promedio reconstruido (canasta 2017/18 overall) — aísla el efecto OUE.
   - D-CPI por clase — el aporte original.

   Reportar siempre los tres en cualquier comparación. Esto es lo que el notebook 04 ya hace.

**C2. Variación de los D-CPI por sub-período**. Calcular tasas anualizadas para cada año (2017–2018, 2019, …, 2024–2025) y mostrar tabla. Permite ver claramente que la heterogeneidad es desigual en el tiempo.

**C3. Decomposición**. Para cada clase, calcular qué divisiones explicaron mayor parte de la diferencia con el oficial. Útil para narrar: "los profesionales asalariadas enfrentaron 9 pp más inflación en 2024 principalmente por su mayor exposición a vivienda y restaurantes/hoteles".

### Bloque D — Refinamientos del análisis de salarios

**D1. Múltiples definiciones de salario**. Probar también `inglabt` (ingresos laborales totales, ocupación principal + secundaria), no sólo `P21`. Comparar.

**D2. Filtrar outliers**. `P21` con valores extremos (top y bottom 1% por trimestre) ensucia las medias. Documentar el filtro.

**D3. Ingreso real per cápita** del hogar (no sólo salario individual). Da una segunda lectura.

**D4. Decomposición por sub-período**. La pérdida acumulada 2017–2025 es la suma de pérdidas y ganancias por año. Reportar año por año para que se vea cuándo cada clase ganó o perdió.

### Bloque E — Extensión opcional (si sobra tiempo)

**E1. LCA en ENGH usando shares directamente**, como segunda mirada. Las clases definidas por consumo no son las mismas que las clases definidas por trabajo, pero deberían correlacionar. Cross-tab entre ambos clusterings es validación indirecta del matching.

**E2. Comparación con segmentación por deciles**. Construir el D-CPI por decil de ingreso (la versión "tradicional" tipo Lódola) y compararlo con el D-CPI por clase. Pregunta: ¿el LCA captura algo que los deciles no? Esa comparación es **el punto fuerte del proyecto** y la principal munición contra "¿por qué no usaste deciles?".

E1 y E2 son nice-to-have. E2 es altamente recomendable si llegás con tiempo — convierte la sección metodológica en una defensa explícita del aporte.

### Cronograma sugerido (semana 17–23 mayo)

- Lunes: A1, A2 (probar variantes LCA con BIC).
- Martes: A3, A4 (sensibilidad y estabilidad).
- Miércoles: B1, B2 (matching extendido + pseudo-validación CIA).
- Jueves: C1, C2, C3 (los tres deflactores y decomposición).
- Viernes: D1, D2, D3, D4 (salarios reales con detalles).
- Sábado: E2 (deciles vs LCA).
- Domingo: descanso o pulir notebooks.

---

## Para la entrega final (fin de mayo)

La entrega final es el cierre narrativo. La parte de modelado debería estar terminada al inicio de la última semana. Lo que queda es escribir.

### Estructura sugerida del documento final

1. **Introducción y motivación** (1 página). Pregunta de investigación, contexto argentino, la grieta entre IPC oficial y experiencia de los hogares.

2. **Marco teórico** (2-3 páginas). Lódola, Jaravel, Suzuki, Schneider & Scharfenaker. Posicionar el aporte: clustering no supervisado en lugar de deciles.

3. **Datos y método** (3-4 páginas). Descripción de EPH, ENGH, IPC INDEC. Pipeline en bloques. **Declaración honesta del supuesto CIA**. Variables que entran al LCA, variables comunes para matching, decisiones simplificadoras documentadas.

4. **Resultados** (4-5 páginas). En este orden:
   - Las clases del LCA: tabla de perfiles + figura de shares (figura 02 del POC).
   - Calidad del matching: accuracy del RF + sensibilidad a variables comunes.
   - D-CPI por clase: figuras 05, 06, 07 del POC.
   - Tabla de inflación interanual cada diciembre (la del notebook 04).
   - Salarios reales: figuras 03 y 04 del POC.
   - Comparación LCA vs deciles (si se hizo el bloque E2).

5. **Discusión** (2 páginas). Los tres niveles de comparación (oficial, promedio reconstruido, por clase). El sesgo Lódola en 2024. Por qué la magnitud acumulada es chica.

6. **Limitaciones** (1 página). CIA no testeable, asimetría rica/pobre, canasta estática, pesos replicados sin uso, sub-reporte cuentapropistas.

7. **Conclusiones y trabajo futuro** (1 página). Lo que va a tesina: pesos replicados con BRR, supervised LCA, multiple imputation, extensión 1996+.

8. **Bibliografía**.

### Tres figuras imprescindibles para la presentación final

1. **`02_shares_by_class.png`** — la heterogeneidad de canastas existe (Engel curve redescubierta).
2. **`07_three_way_comparison.png`** — los dos efectos superpuestos (canasta nueva vs vieja + heterogeneidad por perfil).
3. **`04_money_chart.png`** o variante — el "money chart" final, salarios reales por perfil.

---

## Tech debt explícito (para la tesina, no la entrega final)

Lo que **se nombra como limitación** pero **no se implementa**:

- Errores estándar formales con los 200 pesos replicados de la ENGH (BRR).
- Multiple imputation para incertidumbre en la asignación de clase a la ENGH.
- LCA supervisado / latent class regression con salario como variable estructural.
- Tratamiento sofisticado de la imputación previa de la ENGH (`r_imputado`, `m_*`).
- Extensión histórica a 1996–2016 (otra ENGH, pseudo-panel á la Casanova/Deaton).
- Validación cruzada con la ENGH 2012/13 si se consigue.
- Testeo formal de la CIA con análisis de sensibilidad bayesiano.
- Análisis decomposición tipo Oaxaca-Blinder de la diferencia entre clases.

---

## Criterios para evaluar la entrega final

Antes de entregar, validá que el documento responda **estas cinco preguntas**:

1. ¿Está claro qué pregunta se contesta? (no dejes que el lector la deduzca)
2. ¿Está claro qué método se usó y por qué? (cada decisión justificada o declarada simplificación)
3. ¿Los resultados están narrados con honestidad? (incluyendo magnitudes modestas y limitaciones)
4. ¿Hay diferencia explícita entre lo que el método logra y lo que **no** logra? (especialmente la CIA)
5. ¿Hay una propuesta concreta de continuidad? (la sección de tesina)

Si las cinco están bien resueltas, el TP está sólido.
