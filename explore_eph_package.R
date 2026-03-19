library(eph)
library(tidyverse)

eph_ind_2025_3 <- get_microdata(
  year = 1996,
  trimester = 1,
  type = "individual"
)

vars_select <- c(
  "ANO4",
  "TRIMESTRE",
  "CODUSU",
  "NRO_HOGAR",
  "COMPONENTE",
  "AGLOMERADO",
  "REGION",
  "ESTADO",
  "CAT_OCUP",
  "CH04",
  "CH06",
  "NIVEL_ED",
  "PP04B_COD",
  "PP04D_COD",
  "P21",
  "ITF",
  "PONDERA",
  "PONDIIO",
  "PONDIH"
)

eph_ind_2025_3_select <- get_microdata(
  year = 2025,
  trimester = 1,
  vars = vars_select,
  type = "individual"
)

# etiqueta de variables

df <- eph_ind_2025_3_select %>%
  organize_labels()

# organización de ramas de actividad de ocupados

df <- df %>%
  organize_cno()

df <- df %>% 
  organize_caes()

# algunas tablas rápidas con calculate_tabulates

calculate_tabulates(
  base = df,
  x = "JERARQUIA",
  y = "CH04",
  weights = "PONDERA",
  add.totals = "both"
)

calculate_tabulates(
  base = df,
  x = "caes_seccion_label",
  y = "NIVEL_ED",
  weights = "PONDERA",
  add.percentage = "row"
)


# mapas

tasas <- df %>% 
  group_by(AGLOMERADO) %>% 
  summarize(tasa_actividad = sum(PONDERA[ESTADO==1])/sum(PONDERA))

map_agglomerates(.data = tasas,
                 agglomerates = "AGLOMERADO",
                 indicator = "tasa_actividad")


# pobreza

valoriz_canastas_trimestral <- get_poverty_lines(regional = TRUE)

calculate_poverty(
  base = df,
  basket = valoriz_canastas_trimestral
)


## Múltiples bases

all_eph <- get_microdata(
  year = 2018:2019,
  trimester = 1:4
)

# paneles
pool <- organize_panels(
  bases = all_eph,
  variables = vars_select,
  window = "trimestral"
)


