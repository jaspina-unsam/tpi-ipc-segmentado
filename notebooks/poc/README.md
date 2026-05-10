# POC — IPC distribuido por perfil de trabajador

Prototipo end-to-end del pipeline LCA → statistical matching → D-CPI → salarios reales por clase.

**Esto es un POC**: alcance acotado, decisiones simplificadoras documentadas, IPC sintético. La intención es demostrar que el pipeline corre de punta a punta y produce resultados interpretables. La versión rigurosa (errores estándar, IPC real del INDEC, validación CIA, etc.) queda como tech debt para la tesina.

## Estructura

```
poc/
├── 00_data_prep.ipynb           preparación de EPH ocupados y ENGH
├── 01_lca_eph.ipynb             LCA en EPH 2017-18, k=5, BIC + perfiles
├── 02_match_eph_engh.ipynb      Random Forest sobre 5 vars comunes, accuracy ~0.83
├── 03_dcpi_and_wages.ipynb      shares por clase, D-CPI, salarios reales, gráfico final
├── _build_notebooks.py          regenera los notebooks desde texto plano
├── data/                        outputs intermedios (parquet, csv, pkl)
├── figures/                     PNGs generados por los notebooks
└── README.md                    este archivo
```

## Cómo correrlo

Desde la carpeta `poc/`, ejecutar los notebooks **en orden**:

```bash
jupyter nbconvert --to notebook --execute 00_data_prep.ipynb --inplace
jupyter nbconvert --to notebook --execute 01_lca_eph.ipynb --inplace
jupyter nbconvert --to notebook --execute 02_match_eph_engh.ipynb --inplace
jupyter nbconvert --to notebook --execute 03_dcpi_and_wages.ipynb --inplace
```

Dependencias:

```
pandas  numpy  pyarrow  scikit-learn  stepmix  matplotlib  nbformat
```

(Todas instalables vía `pip install --break-system-packages` si trabajás en el sandbox del proyecto.)

## El pipeline en una imagen

```
EPH 2017-25 ocupados ──┐
                       ├─→ [01] LCA (k=5)  ──→  clase por individuo (EPH)
6 variables indicadoras┘                              │
                                                      │ entrena RF sobre 5 vars comunes
                                                      ▼
ENGH 2017/18 ocupados ──→ [02] RF predict ──→ clase imputada (ENGH)
                                                      │
ENGH 2017/18 hogares    ──────────┬───────────────────┘
   gc_01..gc_12 / gastot          │
                                  ▼
                       [03] shares promedio por clase (5×12)
                                  │
                                  │  × IPC trimestral por división
                                  ▼
                          D-CPI por clase
                                  │
                                  │  ÷ salarios EPH por clase
                                  ▼
              Comparación: IPC oficial vs D-CPI propio
              Gráfico final: ¿quién perdió cuánto?
```

## Resultados del POC

### Las 5 clases latentes

| Clase | Etiqueta | % |
|---|---|---|
| 0 | Obreros formales con secundario | 17 % |
| 1 | Asalariados informales jóvenes | 18 % |
| 2 | Trabajadores mayores con primario | 10 % |
| 3 | Profesionales asalariadas (mujeres mayoría) | 28 % |
| 4 | Cuentapropistas y patrones | 27 % |

### Calidad del matching

Random Forest sobre 5 variables comunes (sexo, edad agrupada, nivel educativo, categoría ocupacional, región): **accuracy ≈ 0.83** en test. La clase 4 (cuentapropistas/patrones) se identifica perfectamente porque `CAT_OCUP` es decisiva. La distinción más débil es 0 vs 1 (formal vs informal), porque `PP07H` no entra al matching.

### Pérdida de salario real 2017Q1 → 2025Q3 (IPC INDEC real)

| Perfil | Con IPC oficial | Con D-CPI propio |
|---|---|---|
| Obreros formales | -15.0 % | -13.9 % |
| Informales jóvenes | -6.1 % | -5.3 % |
| Mayores c/ primario | -19.7 % | -19.0 % |
| Profesionales | -13.7 % | -12.4 % |
| Cuentapropistas | +1.1 % | +1.9 % |

La diferencia entre IPC oficial y D-CPI propio queda chica (~1 punto). El sentido es coherente: las clases con mayor share de alimentos (mayores con primario, informales jóvenes) terminan menos peor con su D-CPI propio que con el oficial, porque alimentos subió un pelo menos que el promedio del IPC en el período. El resultado puede cambiar bastante con otra discretización de variables o con k distinto — lo cual hay que explorar en la entrega final.

## Decisiones simplificadoras (documentadas, defendibles)

1. **k=5** elegido por BIC + interpretabilidad. La curva BIC sigue bajando hasta k=7 pero con caídas marginales y un rebote en k=6, indicio de inestabilidad.
2. **LCA entrenado en 2017-2018** (ventana coincidente con ENGH) y aplicado al panel completo 2017-2025. Asume estabilidad estructural de las clases en el tiempo.
3. **5 variables comunes EPH↔ENGH**, no 6. La variable `FORMAL` (proxy formalidad vía PP07H) queda fuera porque la ENGH no tiene equivalente directo. Costo: la clase 0 vs 1 se distingue peor.
4. **Asignación de clase al hogar ENGH** = clase del ocupado con mayor `ingtotp`. Aproxima al "jefe económico" del hogar. Si el hogar no tiene ocupados, queda fuera del análisis (~20% de los hogares de la ENGH).
5. **IPC**: serie INDEC con apertura por las 12 divisiones COICOP, base diciembre 2016=100, mensual, agregada a trimestres por promedio simple y rebaseada a 2017Q1=100. Cobertura 2017Q1–2026Q1.
6. **Salarios** = `P21` (ingreso de la ocupación principal). No incluye otros ingresos no laborales.

## Tech debt explícito (para la tesina)

- Usar los 200 pesos replicados de la ENGH para errores estándar de los D-CPI (BRR).
- Validación de CIA con análisis de sensibilidad (matching variando el set de variables comunes).
- Probar otros motores de matching (regresión multinomial, hot-deck, distancia mínima) y comparar.
- Multiple imputation para incertidumbre en la asignación de clase.
- Considerar variables del hogar (jefatura, composición, tenencia) además de las del ocupado.
- Análisis de robustez con k=4 y k=6.
- Tratamiento de imputación previa de la ENGH (`r_imputado`, `m_*`).
- Sub-declaración de ingresos en cuentapropistas y patrones (afecta la clase 4).
- Estabilidad temporal de las clases: ¿son las mismas en 2017 que en 2024?

## Para entrega 2 (presentación 2)

Este POC es **input opcional para la presentación 2**. La consigna pide ficha de Suzuki + contraste LLM + discusión metodológica, no implementación. Pero los gráficos `figures/04_money_chart.png` y `figures/02_shares_by_class.png` pueden ir como prueba de viabilidad del pipeline en el bloque D ("¿cómo realizarías este estudio en Argentina?").
