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

## Licencia

Código MIT (`LICENSE`). Contenido CC BY 4.0.
