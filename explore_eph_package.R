install.packages("eph")
library(eph)
library(dplyr)

base_individual <- get_microdata(
  year = 2023,
  trimester = 3,
  type = "individual"
)

glimpse(base_individual)

install.packages("tidyverse")
library(tidyverse)

# Para calcular medianas ponderadas (weightedMedian) usamos el paquete matrixStats
install.packages("matrixStats")
library(matrixStats)

# Ingreso mediano por categoría ocupacional, ponderado
base_individual %>%
  filter(P21 > 0) %>%
  group_by(CAT_OCUP) %>%
  summarise(
    ingreso_mediano = matrixStats::weightedMedian(P21, w = PONDERA, na.rm = TRUE),
    n_ponderado = sum(PONDERA)
  )
