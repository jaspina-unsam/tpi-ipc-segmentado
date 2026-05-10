library(eph)
library(tidyverse)

años_puntual <- 1996:2003

bases <- map(años_puntual, function(anio) {
  map(1:2, function(onda) {
    tryCatch({
      df <- get_microdata(year = anio, wave = onda, type = "individual")
      cat("✓ Descargado:", anio, "onda", onda,
          "| vars:", ncol(df),
          "| n:", nrow(df), "\n")
      df$ONDA <- onda  # asegurar que esté la variable
      df
    }, error = function(e) {
      cat("✗ Falló:", anio, "onda", onda, "-", conditionMessage(e), "\n")
      NULL
    })
  })
})

# Ver qué variables tiene cada base descargada exitosamente
bases_ok <- keep(flatten(bases), ~!is.null(.))
map(bases_ok, ~tibble(año = unique(.x$ANO4), vars = list(names(.x)))) %>%
  bind_rows()

# Ver las variables de una base representativa
vars_1996 <- names(bases_ok[[1]])

# Cuáles de tus variables de interés están disponibles
vars_objetivo <- c(
  "CODUSU", "NRO_HOGAR", "COMPONENTE", "ANO4", "ONDA",
  "REGION", "AGLOMERADO", "PONDERA",
  "CH04", "CH06", "NIVEL_ED", "ESTADO",
  "CAT_OCUP", "CAT_INAC", "PP07H", "CH08",
  "P21", "P47T", "PP04B_COD", "PP04D_COD"
)

cat("✓ Disponibles:\n")
print(intersect(vars_objetivo, vars_1996))

cat("\n✗ No disponibles en 1996:\n")
print(setdiff(vars_objetivo, vars_1996))

# Y ver si cambia en años posteriores (2001 en adelante tienen más vars)
vars_2001 <- names(bases_ok[[which(map_int(bases_ok, ~unique(.x$ANO4)[1]) == 2001)[1]]])
cat("\n✗ No disponibles en 2001:\n")
print(setdiff(vars_objetivo, vars_2001))

names(base1996)
