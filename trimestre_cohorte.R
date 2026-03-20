library(eph)
library(tidyverse)
library(arrow)

vars_select = c(
  "CODUSU",
  "NRO_HOGAR",
  "COMPONENTE",
  "ANO4",
  "TRIMESTRE",
  "REGION",
  "AGLOMERADO",
  "PONDERA",
  # "PONDII",
  # "PONDIIO",
  "CH04",
  "CH06",
  "NIVEL_ED",
  "ESTADO",
  "CAT_OCUP",
  "CAT_INAC",
  # "EMPLEO",
  "PP07H",
  "CH08",
  "P21",
  "P47T",
  "PP04B_COD",
  "PP04D_COD"
)

base_ind <- get_microdata(
  year = 2003,
  trimester = 1:4,
  vars = vars_select
)

base_ind <- base_ind %>% organize_labels() %>% organize_caes() %>% organize_cno()

write_parquet(base_ind, "data/base_ind_2003.parquet")
