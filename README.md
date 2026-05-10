# tpi-ipc-segmentado

**Inflación heterogénea y poder adquisitivo en Argentina — cuando los precios suben, ¿todos pierden por igual?**

Trabajo final, Ciencia de Datos (LCD, ECyT–UNSAM, 1.er cuatrimestre 2026). Autor: Javier Spina. Modalidad individual. Pieza embrionaria de la tesina.

## Pregunta

> ¿Cuál es la tasa de inflación real que enfrenta cada perfil de trabajador argentino, y qué tan vulnerable es su situación laboral cuando se mide con ese índice personalizado en lugar del IPC oficial?

## Aporte distintivo

La literatura existente (Jaravel 2024; Lódola, Busso & Cerimedo 2000) segmenta por decil de ingreso o por categorías sociodemográficas fijas. Este trabajo reemplaza esa segmentación a priori por **clustering no supervisado (LCA)** sobre microdatos de la EPH, dejando que los perfiles emerjan de los datos.

## Pipeline

```
LCA en EPH                         → grupos latentes de trabajadores
        ↓
Statistical matching EPH ↔ ENGH    → cada hogar de la ENGH recibe la clase
(Random Forest como motor)            LCA más probable según variables comunes
        ↓
Canasta de consumo por clase       → vector de shares por división CCIF
        ↓
D-CPI por clase                    → índice de precios específico del perfil
        ↓
Deflactación de salarios           → poder adquisitivo real por perfil
```

## Decisiones cerradas

| Eje | Decisión |
|---|---|
| Unidad de análisis | Individuo ocupado (no hogar). El interés es la trayectoria de salarios reales del trabajador. |
| Período del TP | 2017 en adelante. Una sola ENGH (2017/18) → supuesto de estabilidad estructural acotado a ~7 años. |
| Período en reserva | 1996–2016 queda armado en el dataset, reservado para la tesina. |
| Clustering | LCA (eventualmente con `stepmix`). EPH es ~90% categórica; LCA captura la ambigüedad social mejor que k-means. |
| Fusión EPH↔ENGH | Statistical matching con Random Forest (versión accesible del menú de D'Orazio). |
| Pipeline ingesta | R (paquete `eph` de Kozlowski, Tiscornia, Weksler, Rosati & Shokida) → Parquet → Python. Idempotente, con `FUENTE_BASE` como bandera de trazabilidad. |
| Empleo formal/informal | Proxy `PP07H` (descuento jubilatorio) pre-2023, equivale a `EMPLEO` 1:1 desde 2023. |
| Variables de cohorte | `CH04` (sexo), `CH06` (edad), `NIVEL_ED`, `REGION`. ID persona: `CODUSU` + `NRO_HOGAR` + `COMPONENTE`. |

## Bloqueadores abiertos

1. **Crosswalk oficial CCIF↔IPC del INDEC** para ENGH 2017/18 — sin esto no hay D-CPI.
2. **Set inicial de 5–7 variables estructurales para LCA** — podar el draft de variables candidatas.
3. **CIA (independencia condicional) en el matching** — declararla explícitamente y validar indirectamente con accuracy del RF sobre variables comunes EPH↔ENGH.
4. **Decisión de _k_ en LCA** — correr BIC + BLRT, reportar curva.
5. **Supuesto individuo↔hogar** — el perfil del individuo entra al LCA, la canasta es la del hogar equivalente. Hay que escribirlo como supuesto explícito.

## Marco teórico (4 pilares)

- **Económico:** Jaravel (2024, _Distributional Consumer Price Indices_); Lódola, Busso & Cerimedo (2000, sesgo plutocrático en Argentina); Gasparini, Marchionni & Sosa Escudero (2002); Deaton (1985, pseudo-panel); Casanova (2008, aplicación local).
- **LCA y mezcla finita:** Weller, Bowen & Faubert (2020, guía operativa); Nylund, Asparouhov & Muthén (2007, BIC + BLRT); Suzuki (2020, espejo aplicado al mercado laboral japonés); Schneider & Scharfenaker (2020, defensa de mezcla finita vs deciles).
- **Statistical matching:** Donatiello et al. (2014, espejo SILC↔HBS); Webber/Eurostat (2013, comparación de métodos); D'Orazio, Di Zio & Scanu (2006, "la biblia") reservado para tesina.
- **Random Forest:** Stekhoven & Bühlmann (2012, missForest); Shah et al. (2014); Hong & Lynn (2020, sesgos en asimetría).
- **Antecedente local:** Germán Rosati (UNSAM) — co-autor del paquete `eph` y autor de Rosati (2017, ensemble learning para imputación en EPH); en agenda para entrevista.

## Datos

| Fuente | Uso |
|---|---|
| EPH (INDEC) — microdatos panel | perfiles de trabajadores, salarios, situación laboral |
| ENGH 2017/18 (INDEC) | estructura de gasto por perfil → ponderadores del IPC |
| IPC por división (INDEC) | precios desagregados por rubro |
| RIPTE, tipo de cambio, tarifas | proxies de contexto macro |

Series IPC INDEC: [GBA base abril 2008](https://www.indec.gob.ar/indec/web/Institucional-Indec-InformacionDeArchivo) · [Precios promedio por región](https://www.indec.gob.ar/indec/web/Nivel4-Tema-3-5-31).

## Calendario

- 27/3 ✅ Presentación 1 (introducción y contextualización)
- 8/5 — Presentación 2 (paper de la ficha: Suzuki 2020; Etapa 3 con cinco bloques)
- ~24/5 — entrevista a Rosati (incorporar feedback antes de la final)
- 2/6 — Presentación final
- 19/6 — Entrega del informe individual

Detalle semana a semana: ver `docs/notas/debrief_proyecto.md` (sección 7).

## Estructura del repositorio

```
notebooks/        exploracion/, ingest/, poc/ (pipeline 00→04: data_prep, lca, match, dcpi, monthly)
scripts/          python/ (build_panel) y r/ (ingesta EPH con paquete `eph`)
datos/            eph/{parquet, raw_db, docs}, engh/{raw, procesado, docs}, ipc/, outputs/
docs/             papers/, consignas/, entregas/, notas/, conversaciones_ia/, sota_candidates/, referencia/
presentaciones/   introduccion/ y revision_fuentes/ (LaTeX + PDF)
estado_del_arte.xlsx · tpi-ipc-segmentado.Rproj
```

`docs/notas/` contiene los debriefs originales y la tabla de lecturas con prioridades (must / should / tier-tesina) y modos (completa / parcial / diagonal / cita) — útil cuando hace falta el detalle.


## Keywords de búsqueda (Google Scholar / arXiv / SSRN)

| # | Keywords | Objetivo |
|---|---|---|
| 1 | `"latent class" "household expenditure"` OR `"mixture model" "consumption patterns"` | Encontrar el espejo aplicado correcto: LCA sobre canastas (no sobre mercado laboral). Reemplazo natural de Suzuki post-pivote. |
| 2 | `"Engel curves" heterogeneity "mixture"` OR `Lewbel "demand system" heterogeneous` | Fundamentar teóricamente que las elasticidades de gasto varían por perfil. Conecta con Schneider-Scharfenaker desde el lado de demanda. |
| 3 | `"household-level inflation"` OR `"distributional CPI" clustering` | D-CPIs construidos con clustering ML (no con deciles). Buscar Hobijn-Lagakos, Kaplan-Schulhofer-Wohl, Argente-Lee, Aguiar-Hurst. |
| 4 | `"ENGH" Argentina 2018..2026` OR `"encuesta nacional de gastos" hogares clustering` | Trabajos argentinos recientes que ya usaron la ENGH 2017/18 con métodos no paramétricos. Validar que no estás reinventando la rueda. |
| 5 | `CEDLAS Argentina consumo OR canasta 2023..2026` | Camada reciente del CEDLAS/UNLP sobre canastas y consumo (Marchionni, Tornaroli, Trujillo). |
| 6 | `"typology of consumption" machine learning survey` | Clustering ML aplicado a encuestas de gasto en otros países, para comparar enfoques metodológicos. |
| 7 | `"reweighting" OR "post-stratification" "income" INDEC` | Confirmar el cambio metodológico del INDEC que mencionó Rosati (abandono del hot-deck). Útil para nota técnica al margen, no para el cuerpo del TP. |

Empezaría por **#1 y #3** — son las que más probabilidad tienen de devolverte el espejo aplicado que te falta.

Sí, controlo Chrome. Antes de lanzar las búsquedas, una sola decisión para no desperdiciar el barrido:Chrome no está conectado. Voy con WebSearch + WebFetch que no requieren extensión:11 papers nuevos agregados (49 totales). Acá va la síntesis de lo que encontré y la trayectoria del campo:

## Hallazgo principal

**Existe un espejo argentino DIRECTO de tu proyecto, publicado hace un mes**, en tu propia universidad-de-origen (UNLP-CEDLAS):

> **Albina, Gasparini & Tornarolli (2026)**, _Medición de la pobreza en contextos de inflación cambiante: el caso de Argentina_, CEDLAS WP 370 (abril 2026). Período 2018-2025, usa la ENGH 2017/18 para reestimar el Coeficiente de Engel y mide el impacto sobre la línea de pobreza.

Esto valida tres cosas de un saque: (a) tu recorte temporal 2017+, (b) tu uso de la ENGH 2017/18, (c) la pregunta misma. Es la cita central de motivación post-pivote.

## Trayectoria 2017–2026 del campo

**Generación 1 (2017-2020) — fundación moderna del IPC distribuido:**
- **Kaplan & Schulhofer-Wohl (2017)** — IPC a nivel hogar con scanner data US, IQR 6.2-9.0pp.
- **Cravino & Levchenko (2017)** — devaluaciones grandes y desigualdad inflacionaria.
- **Cravino, Lan & Levchenko (2020)** — rigidez de precios por estrato de ingreso.
- **Argente & Lee (2021)** — Cost of Living Inequality durante la Gran Recesión, gap 2.4x.

**Generación 2 (2021-2024) — réplica internacional + crítica metodológica:**
- **Gouvêa (2022)** — replica Cravino-Levchenko en Brasil, valida en LATAM.
- **Del Canto, Grigsby, Qian & Walsh (2023)** — feasible set approach, cuestiona qué shocks son progresivos vs regresivos.
- **Kiss & Strasser (2024)** — replica europea (Francia + Alemania), confirma persistencia.
- **Klick & Stockburger (2024)** — BLS oficializa la metodología.
- **Jaravel (2024)** — base pública de D-CPIs en EE.UU.

**Generación 3 (2024-2026) — convergencia con datos administrativos y macro:**
- **Cicek et al. (2026 IMF)** — distributional inflation con activos reales y respuestas comportamentales.
- **CEDLAS 336 (2024)** y **CEDLAS 370 (2026)** — Argentina entra al campo combinando EPH con registros administrativos y reestimando Engel con ENGHo 2017/18.

## ⚠️ Hallazgo crítico que afecta tu proyecto

**Kaplan-Schulhofer-Wohl (2017) y Kiss-Strasser (2024)** convergen en un resultado que es una limitación estructural: **solo ~7% de la heterogeneidad de inflación entre hogares se explica por diferencias en canastas**. El resto viene de precios pagados por bienes idénticos (~⅔) y variedad dentro de categorías (~⅓).

Implicación: tu proyecto, que busca clusterizar canastas y deflactar con esos shares, captura por construcción solo una parte del fenómeno. Hay que declararlo como limitación explícita — pero no invalida el trabajo, porque (a) Argentina puede ser distinta (devaluaciones cambian precios relativos masivamente, no solo dispersión espacial), (b) el resultado de KSW es para EE.UU. donde la dispersión espacial es enorme, (c) Cravino-Levchenko muestra que en devaluaciones grandes el componente "canastas" sí domina.

## Lo que el campo todavía NO tiene (oportunidad de tesina)

1. **Aplicación argentina con clustering ML (no deciles)**: CEDLAS 370 sigue usando deciles. Tu pivote (LCA en ENGH) sería diferenciador.
2. **D-CPI con clustering en LATAM**: nadie lo hizo aún.
3. **Replicación de la descomposición KSW en Argentina**: para saber si el 7% se mantiene o si en contextos de alta volatilidad cambiaria sube. Esto sería un capítulo natural de la tesina.

## Sobre las búsquedas que hiciste antes

El error con keyword #1 era inevitable: `"latent class" "consumption patterns"` en Scholar está dominado por epidemiología nutricional ("dietary patterns"). Las keywords que funcionan en economics son: `"latent class" "household budget"`, `"latent class" "expenditure shares"`, `"finite mixture" income distribution`, o ir directo a autores (Lewbel, Banks-Blundell-Lewbel para sistemas de demanda; Schneider-Scharfenaker para mezcla finita en distribución del ingreso).


**Sources:**
- [CEDLAS WP 370 (Albina, Gasparini, Tornarolli 2026)](https://www.cedlas.econo.unlp.edu.ar/wp/en/no-370/)
- [CEDLAS WP 336 (Albina et al. 2024)](https://www.cedlas.econo.unlp.edu.ar/wp/en/no-336/)
- [Argente & Lee 2021 — JEEA](https://academic.oup.com/jeea/article-abstract/19/2/913/5863149)
- [Kaplan & Schulhofer-Wohl 2017 — JME](https://www.sciencedirect.com/science/article/abs/pii/S0304393217300879)
- [Cravino, Lan & Levchenko 2020 — JME](https://ideas.repec.org/a/eee/moneco/v110y2020icp19-32.html)
- [Cravino & Levchenko 2017 — AER](https://www.nber.org/papers/w23409)
- [Gouvêa 2022 — JAE](https://onlinelibrary.wiley.com/doi/abs/10.1002/jae.2880)
- [Del Canto, Grigsby, Qian & Walsh 2023 — NBER WP 31124](https://www.nber.org/papers/w31124)
- [Kiss & Strasser 2024 — ECB WP 2898](https://www.ecb.europa.eu/pub/pdf/scpwps/ecb.wp2898~29405f932f.en.pdf)
- [Klick & Stockburger 2024 — BLS MLR](https://www.bls.gov/opub/mlr/2024/article/examining-us-inflation-across-households-grouped-by-equivalized-income.htm)
- [Alzuabi et al. 2024 — Canadian J Economics](https://onlinelibrary.wiley.com/doi/10.1111/caje.12691)
- [INDEC IPC Calculator (junio 2025)](https://www.indec.gob.ar/indec/web/Institucional-Indec-mi_propio_IPC)
- [ECB Occasional Paper 325 — Inflation heterogeneity at household level](https://www.ecb.europa.eu/pub/pdf/scpops/ecb.op325~7422ebe3c1.en.pdf)
- [BIS WP 1152 — Heterogeneous impact of inflation on households' balance sheets](https://www.bis.org/publ/work1152.pdf)



## Sobre el "SQL join"

Tu intuición es **parcialmente correcta**: EPH y ENGHo comparten muchas variables sociodemográficas (sexo, edad, educación, región, jefe de hogar, tamaño del hogar, condición de actividad, categoría ocupacional). Pero **no es un join real** porque no hay individuos en común — son dos muestras independientes del mismo universo.

Lo que SÍ es cierto: si las distribuciones de las variables comunes coinciden razonablemente entre EPH y ENGHo (mismo INDEC, marco muestral similar), un esquema "clasificar en ENGHo → asignar a EPH por las mismas covariables" es muy parecido a un join. La diferencia con un join SQL exacto es:
- Dos individuos con el MISMO perfil sociodemográfico pueden tener canastas distintas (variación idiosincrática que no captura el modelo)
- El "matching" se vuelve **un problema de predicción**: dado el perfil, predecir el vector de shares

Así que el pilar Statistical Matching no se elimina — **se disuelve dentro del modelo de clustering/predicción**. Es la misma operación con otro nombre.

## Sobre LCA — mi respuesta filosófica honesta

**No, LCA dejó de ser "el" modelo obvio post-pivote.** LCA era natural cuando el clustering iba sobre EPH (variables ~90% categóricas: sexo, formalidad, categoría ocupacional). Ahora el clustering va sobre **ENGHo, donde el insumo natural son los shares de gasto — datos compositional/continuos** (suman 1, geometría simplex). LCA estándar no es la herramienta natural para eso.

Más importante: **tu pregunta sobre "shares como target" es exactamente la dirección que toma la literatura canónica del campo**. Argente-Lee, Cravino-Levchenko y la metodología BLS (Klick-Stockburger) NO clusterizan primero — directamente regresionan los shares contra demografía. Eso es lo que estás intuyendo.

## Tres caminos viables (ordenados de menos a más estructura)

**A — Supervisado puro (estilo Argente-Lee, BLS, Cravino-Levchenko)**
```
ENGHo: shares_ccif = f(sociodem)        # entrenar
EPH:   shares_predicted = f(sociodem_eph)  # aplicar
       D-CPI_individuo = shares_predicted · IPC_div
```
- Métodos: regresión multivariada, **Distributional Random Forests** (Biewen-Glaisner 2025, ya en tu xlsx) → es exactamente esto, **DRF predice la distribución completa de shares**
- Ventaja: directo, validable, alineado con la literatura canónica
- Desventaja: no hay "tipos" — cada individuo de la EPH tiene su propio vector. Rosati ya te advirtió que no querés 44M de inflaciones, pero esto es solucionable agrupando shares predichos en cuartiles o con un k-means simple después.

**B — Híbrido: predecir y después clusterizar (recomendado)**
```
1. ENGHo: shares ~ sociodem (DRF o regresión multivariada)
2. EPH: predecir vector de shares para cada individuo
3. Clusterizar los vectores predichos (k-means / GMM / LPA con log-ratio)
4. D-CPI por cluster
```
- Recuperás los "tipos" pero emergen de la estructura predictiva, no de un LCA artificial
- Es defendible metodológicamente y narrativamente
- Es lo que más cerca está del espíritu del nodo de CSC sin forzar LCA

**C — LCA/LPA respetando geometría compositional**
```
ENGHo: aplicar transformación log-ratio (ALR/ILR de Aitchison) a los shares
       → ahora viven en R^(k-1)
       → LPA o GMM sobre el espacio transformado
       → clases con perfil de gasto
       → caracterizar con sociodem
EPH: classify-analyze (lookup)
```
- "LCA en spirit" pero técnicamente correcto para compositional data
- Más complejo. La transformación log-ratio es estándar en literatura compositional pero no la trabajaste todavía.


## Variable selection — palabras clave para la próxima búsqueda

| # | Keywords | Objetivo |
|---|---|---|
| 1 | `compositional regression "variable selection" lasso OR sparse` | Selección de variables cuando el target es un vector de shares (geometría simplex). Aitchison + lasso. |
| 2 | `"distributional random forest" variable importance OR selection` | Cómo seleccionar variables para DRF, alineado con el camino B. |
| 3 | `Boruta OR "stability selection" household survey expenditure` | Métodos de selección estables para encuestas de hogares. |
| 4 | `"feature selection" OR "variable selection" "Engel curves" OR "demand system"` | Tradición econométrica: qué variables incluir/excluir en sistemas de demanda heterogéneos. |
| 5 | `"group lasso" demographic variables survey clustering` | Selección agrupada (variables vienen en bloques: demográficas / laborales / hogar) — útil si querés justificar bloques antes que variables individuales. |
| 6 | `"mutual information" OR "permutation importance" categorical mixed survey` | Importancia de variables no-paramétrica para datos mixtos (continuos + categóricos), alineado con la realidad de la ENGHo. |
| 7 | `StepMix OR "latent class" "covariate selection" 2022..2026` | Si querés mantener LCA en la mesa, cómo seleccionan covariables los papers más recientes. |


**Respuesta corta sobre las slides:** No, no se invalidan. La base conceptual — pregunta, motivación, aporte de ML para perfiles emergentes vs deciles — se mantiene 100%. Lo que pivota es solo el **orden** del pipeline (clusterizar en ENGHo en vez de EPH) y la elección puntual de método (LCA → DRF/híbrido). Las fuentes principales (Jaravel, Lódola, Donatiello, Weller) siguen vigentes; Suzuki pierde un poco como espejo aplicado pero conserva valor metodológico. La cita a Rosati en "riesgos" en la slide 9 envejeció bien — anticipaste el problema antes de saberlo.

Corro búsquedas ahora.Listo. 5 papers nuevos agregados en un nuevo eje **"Selección de variables"** (color lila). Total: 54 papers en el xlsx.

## Lo que sumé

**Para el camino B (DRF, recomendado):**
1. **Bénard, Näf & Josse (2024)** _"MMD-based Variable Importance for Distributional Random Forest"_ — AISTATS 2024 ⭐ La pieza técnica clave. Detecta variables que afectan cualquier aspecto de la distribución, no solo la media — exactamente lo que necesitás cuando el target es un vector de shares.
2. **Kursa & Rudnicki (2010)** _"Boruta"_ — JSS 36(11). Herramienta pragmática plug-and-play, primera vuelta de selección antes de MMD.

**Para selección compositional (camino A o si los shares son target en regresión):**
3. **Lu, Shi & Li (2024)** _"Variable selection and inference strategies for multiple compositional regression"_ — Chemometrics. Debiased lasso para predictores compositional con intervalos válidos.
4. **Susin, Wang, Cao & Calle (2020)** _"Variable selection in microbiome compositional data analysis"_ — review de selbal, clr-lasso, coda-lasso. Trasladable de microbioma a shares de gasto (mismo problema matemático).

**Para regresión penalizada con sociodem categóricas:**
5. **Park, Choi & Seo (2022)** _"Lasso and Group Lasso with Categorical Predictors"_ — JBDS. Group lasso es la respuesta natural para EPH (variables vienen en bloques: demográfico/laboral/hogar) con muchas categóricas.

## Lo que también encontré (no agregué para no inflar)

- **Bakk & Vermunt (2024)** _"Bias-Adjusted Three-Step Multilevel LCA with Covariates"_ — si terminás manteniendo LCA con covariables sociodemográficas
- **Variable Importance for Multivariate Random Forests** — JDS, soporte adicional al método de Bénard
- **Stability Selection** (Meinshausen & Bühlmann 2010) — clásico, complementa Boruta

Si querés que sume alguno de estos tres últimos, decime. Si no, con los 5 que están en el xlsx tenés cobertura completa para defender la decisión metodológica del TP.


**Sources:**
- [Bénard, Näf & Josse 2024 — MMD VI for DRF (PMLR)](https://proceedings.mlr.press/v238/benard24a.html)
- [Bénard, Näf & Josse — arXiv 2310.12115](https://arxiv.org/abs/2310.12115)
- [Lu, Shi & Li 2024 — Variable selection compositional regression](https://www.sciencedirect.com/science/article/abs/pii/S0169743924000613)
- [Susin et al. 2020 — Variable selection microbiome compositional](https://academic.oup.com/nargab/article/2/2/lqaa029/5836692)
- [Kursa & Rudnicki 2010 — Boruta (JSS 36/11)](https://www.jstatsoft.org/article/view/v036i11)
- [Park, Choi & Seo 2022 — Lasso/Group Lasso Categorical Predictors (JBDS)](https://jbds.isdsa.org/jbds/article/view/64)
- [Multi-Task Learning for Compositional Data via Sparse Network Lasso (MDPI)](https://www.mdpi.com/1099-4300/24/12/1839)
- [Log-ratio Lasso — Scalable Sparse Estimation](https://pmc.ncbi.nlm.nih.gov/articles/PMC9470385/)
- [Bias-Adjusted Three-Step Multilevel LCA with Covariates (Tandfonline)](https://www.tandfonline.com/doi/full/10.1080/10705511.2023.2300087)
- [Two-step estimator multilevel LCA with covariates (Psychometrika)](https://link.springer.com/article/10.1007/s11336-023-09929-2)

**Curva de Engel** — relación entre el ingreso (o gasto total) del hogar y la cantidad o el share gastado en un bien específico. Llamada así por Ernst Engel (estadístico alemán, 1857), que estableció la **ley de Engel**: a medida que sube el ingreso, el share gastado en alimentos cae. La forma de la curva (lineal, cuadrática, log-cuadrática) es el corazón técnico de los sistemas de demanda — Banks-Blundell-Lewbel 1997 popularizaron las cuadráticas (modelo QUAIDS). En tu proyecto, cuando regreses `shares ~ ingreso + sociodem`, **estás estimando curvas de Engel sin darte cuenta**. Es el lenguaje formal de "cómo cambia la canasta con el perfil del hogar".

**Variable selection — no, no quedás encerrado en shares.** El sociodem es lo que mantiene viva tu pregunta inicial. Tres lugares donde entra, según la arquitectura:

1. **Camino B (recomendado):** los shares son el **target**, sociodem (rama, sexo, edad, educación, formalidad) son los **predictores**. El DRF aprende `shares = f(sociodem)`, y después clusterizás los shares predichos. Los clusters quedan **definidos por consumo pero interpretados por demografía** — exactamente lo que pedís.
2. **LCA / LPA con covariables (StepMix three-step):** los shares definen las clases, pero el sociodem entra como **covariables externas** que predicen la pertenencia a clase. La narrativa queda: "perfil demográfico X tiene probabilidad alta de estar en la clase con canasta Y".
3. **Clustering mixto:** shares + sociodem juntos como input. Más cercano a tu LCA original, pero pierde la limpieza geométrica del shares-puro.

En las tres opciones la **rama de actividad, sexo y grupo etario son centrales**, no opcionales. La pregunta de la selección de variables no es "shares vs sociodem" sino **"cuáles de las ~30 variables sociodem candidatas dejo entrar"** — y ahí entran Boruta, MMD-VI, group lasso. Si querés, te armo un esquema gráfico de las 3 arquitecturas con qué variables entra dónde.


## Licencia

Código MIT (`LICENSE`). Contenido CC BY 4.0.
