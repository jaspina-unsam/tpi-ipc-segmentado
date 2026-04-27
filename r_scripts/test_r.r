library(tidyverse)
install.packages("eph")

library(eph)

# Cargar los datos de la EPH
eph_96o1_data <- get_microdata(year = 1996, period = 1) %>%
  organize_labels() %>%
  organize_caes() %>%
  organize_cno()

names(eph_96o1_data)
