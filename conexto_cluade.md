Buena idea. Acá va:

---

**PROMPT DE CONTINUIDAD — Proyecto EPH / Poder Adquisitivo Argentina**

Estoy desarrollando mi trabajo final de la materia Ciencia de Datos (carrera LCD, UNSAM). El proyecto estudia **la evolución del poder adquisitivo en Argentina ajustado por inflación distribucionalmente segmentada**, inspirado en la literatura de *distributional inflation* (Jaravel 2024, Lodola et al. años 90).

**La idea central:** construir un IPC personalizado por perfil de trabajador cruzando EPH + ENGH + IPC desagregado por rubro, y estudiar quién realmente pierde poder adquisitivo ante shocks macroeconómicos.

**Decisiones metodológicas tomadas:**

- Unidad de análisis: **pseudo-panel por cohorte** (no individuos) — grupos definidos por características sociodemográficas estables observados en cada trimestre
- Variables de **cohorte:** sexo (`CH04`), edad (`CH06`), nivel educativo (`NIVEL_ED`), región (`REGION`)
- Variables de **resultado:** sueldo (`P21`, `P47T`), formalidad (`EMPLEO`), situación de actividad (`ESTADO`), categoría ocupacional (`CAT_OCUP`, `CAT_INAC`), rama de actividad (`PP04B_COD` CAES, `PP04D_COD` CNO)
- Ponderadores de ingreso: `PONDIIO` para `P21`, `PONDII` para `P47T`, `PONDERA` para el resto
- Identificación de persona: `CODUSU` + `NRO_HOGAR` + `COMPONENTE`
- El **clustering ML** va a descubrir agrupamientos que emergen de los datos, complementando las cohortes teóricas
- Pipeline: **R** (`eph` package) para descarga y ETL inicial → exportar a **Parquet** → **Python/pandas** para análisis y ML

**Estado actual del código en R:**

```r
library(eph)
library(tidyverse)

vars_select = c(
  "CODUSU", "NRO_HOGAR", "COMPONENTE",
  "ANO4", "TRIMESTRE", "REGION",
  "PONDERA", "PONDII", "PONDIIO",
  "CH04", "CH06", "NIVEL_ED",
  "ESTADO", "CAT_OCUP", "CAT_INAC", "EMPLEO",
  "P21", "P47T",
  "PP04B_COD", "PP04D_COD"
)

base_ind_2024 <- get_microdata(
  year = 2024,
  trimester = 1:4,
  vars = vars_select
)

base_ind_2024 <- base_ind_2024 %>% 
  organize_labels() %>% 
  organize_caes() %>% 
  organize_cno()
```

Funciona correctamente. Warning benigno en `PP04B_COD` (conversión a character por `organize_caes()`).

**Próximos pasos pendientes:**

1. EDA del dataset de 2024 en R o Python
2. Exportar a Parquet para continuar en Python
3. Ampliar la serie histórica (desde 2003, con consideración del cambio de CAES en 2010 y el IPC intervenido 2007-2015)
4. Incorporar ENGH e IPC desagregado por rubro
5. Construir el IPC personalizado por cohorte
6. Clustering ML en Python

**Fuentes de datos adicionales a incorporar:** IPC desagregado por rubro (INDEC), tipo de cambio, tarifas, ENGH 2017/18 (descarga manual desde INDEC).

**Repo:** público en GitHub, licencia MIT para código y CC BY 4.0 para contenido. Pipeline mixto R + Python justificado metodológicamente.

---

Guardalo y en la próxima sesión pegalo al inicio. Cualquier Claude va a poder retomar desde acá sin perder contexto.