# =============================================================================
# ingest_continua.R
# Ingesta de microdatos EPH continua (2003T3 en adelante)
#
# Fuente: paquete {eph} — get_microdata()
# Esquema de salida: común con ingest_puntual.R
#
# Decisiones documentadas:
#   - Se descarga un parquet por año (todos los trimestres concatenados)
#   - Idempotencia: si el parquet del año ya existe, se omite la descarga
#   - organize_labels(), organize_caes(), organize_cno() aplicados fuera del
#     pipe principal con fallback explícito — evita que warnings de INDEC
#     (período 2007-2015) o ausencia de PP04B/D_COD se propaguen como errores
#   - PONDII, PONDIIO, EMPLEO, PP04B_COD, PP04D_COD NO declarados en vars_select:
#     get_microdata() los rechaza con df vacío en años pre-incorporación
#   - PONDII / PONDIIO: disponibles desde 2016; NA en años anteriores
#   - RAMA: NA (clasificación propia de la puntual, no existe en continua)
#   - FUENTE_BASE = "continua" en todos los registros
#   - 2003: solo T3 y T4 (T1 y T2 corresponden a la puntual)
#
# Nota sobre 2007-2015: INDEC advierte reservas sobre estas series.
#   El paquete {eph} emite un warning; lo capturamos y registramos pero
#   no interrumpimos la ingesta. El usuario debe tener en cuenta esta
#   advertencia al analizar ese período.
# =============================================================================

library(eph)
library(arrow)
library(dplyr)
library(purrr)

OUTPUT_DIR <- "data"

ANIO_INICIO     <- 2003
ANIO_FIN        <- as.integer(format(Sys.Date(), "%Y"))
TRIMESTRES_2003 <- 3:4

vars_select <- c(
  "CODUSU", "NRO_HOGAR", "COMPONENTE",
  "ANO4", "TRIMESTRE",
  "REGION", "AGLOMERADO",
  "PONDERA",
  "CH04", "CH06", "NIVEL_ED",
  "ESTADO", "CAT_OCUP", "CAT_INAC",
  "CH08", "PP07H",
  "P21", "P47T"
)

# -----------------------------------------------------------------------------
# Helpers — todos aplicados fuera del pipe, con fallback a df original
# -----------------------------------------------------------------------------

garantizar_col <- function(df, col, tipo_na) {
  if (!col %in% names(df)) df[[col]] <- tipo_na
  df
}

aplicar_labels <- function(df, anio) {
  # withCallingHandlers permite capturar warnings sin interrumpir la ejecución
  withCallingHandlers(
    tryCatch(
      organize_labels(df),
      error = function(e) {
        cat(sprintf("    ⚠ organize_labels() falló en %d: %s\n", anio, conditionMessage(e)))
        df
      }
    ),
    warning = function(w) {
      cat(sprintf("    ℹ organize_labels() advertencia en %d: %s\n", anio, conditionMessage(w)))
      invokeRestart("muffleWarning")
    }
  )
}

aplicar_caes <- function(df, anio) {
  if (!("PP04B_COD" %in% names(df)) || all(is.na(df$PP04B_COD))) {
    cat(sprintf("    ⚠ organize_caes() omitido en %d: PP04B_COD ausente\n", anio))
    return(df)
  }
  resultado <- tryCatch(organize_caes(df), error = function(e) {
    cat(sprintf("    ⚠ organize_caes() omitido en %d: %s\n", anio, conditionMessage(e)))
    NULL
  })
  if (is.null(resultado)) df else resultado
}

aplicar_cno <- function(df, anio) {
  if (!("PP04D_COD" %in% names(df)) || all(is.na(df$PP04D_COD))) {
    cat(sprintf("    ⚠ organize_cno() omitido en %d: PP04D_COD ausente\n", anio))
    return(df)
  }
  resultado <- tryCatch(organize_cno(df), error = function(e) {
    cat(sprintf("    ⚠ organize_cno() omitido en %d: %s\n", anio, conditionMessage(e)))
    NULL
  })
  if (is.null(resultado)) df else resultado
}

# -----------------------------------------------------------------------------
# Procesamiento de un año completo
# -----------------------------------------------------------------------------

procesar_anio <- function(anio) {
  nombre_archivo <- sprintf("base_ind_%d", anio)
  ruta_parquet   <- file.path(OUTPUT_DIR, paste0(nombre_archivo, ".parquet"))
  
  if (file.exists(ruta_parquet)) {
    cat(sprintf("✓ Ya existe: %s — omitido\n", nombre_archivo))
    return(invisible(NULL))
  }
  
  trimestres <- if (anio == ANIO_INICIO) TRIMESTRES_2003 else 1:4
  cat(sprintf("→ Descargando: %d (trimestres %s)\n", anio,
              paste(trimestres, collapse = ", ")))
  
  tryCatch({
    # Paso 1: descarga — warnings de INDEC capturados aquí también
    raw <- withCallingHandlers(
      get_microdata(year = anio, trimester = trimestres, vars = vars_select),
      warning = function(w) {
        cat(sprintf("    ℹ get_microdata() advertencia en %d: %s\n", anio, conditionMessage(w)))
        invokeRestart("muffleWarning")
      }
    )
    
    if (nrow(raw) == 0 || !"TRIMESTRE" %in% names(raw)) {
      cat(sprintf("  ✗ Sin datos en %d — omitido\n", anio))
      return(invisible(NULL))
    }
    
    # Paso 2: clasificadores — secuenciales con fallback individual
    raw <- aplicar_labels(raw, anio)
    raw <- aplicar_caes(raw, anio)
    raw <- aplicar_cno(raw, anio)
    
    # Paso 3: esquema común
    out <- raw |>
      garantizar_col("PONDII",    NA_real_)    |>
      garantizar_col("PONDIIO",   NA_real_)    |>
      garantizar_col("EMPLEO",    NA_real_)    |>
      garantizar_col("PP07H",     NA_real_)    |>
      garantizar_col("NRO_HOGAR", NA_integer_) |>
      mutate(
        PERIODO      = as.integer(TRIMESTRE),
        TIPO_PERIODO = "trimestre",
        RAMA         = NA_integer_,
        FUENTE_BASE  = "continua",
        PONDII       = as.numeric(PONDII),
        PONDIIO      = as.numeric(PONDIIO),
        NRO_HOGAR    = as.integer(NRO_HOGAR)
      )
    
    write_parquet(out, ruta_parquet)
    cat(sprintf("  ✓ Exportado: %s (%d filas, %d trimestres)\n",
                ruta_parquet, nrow(out), length(trimestres)))
    
  }, error = function(e) {
    cat(sprintf("  ✗ Error en %d: %s\n", anio, conditionMessage(e)))
  })
  
  invisible(NULL)
}

# -----------------------------------------------------------------------------
# Ejecutar sobre todos los años
# -----------------------------------------------------------------------------
cat("=== Ingesta EPH continua ===\n")
walk(ANIO_INICIO:ANIO_FIN, procesar_anio)
cat("=== Completado ===\n")