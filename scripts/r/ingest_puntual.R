# =============================================================================
# ingest_puntual.R
# Ingesta de microdatos EPH puntual (1996O1 - 2003O1)
#
# Fuente: RDS descargados del repositorio del paquete {eph}
# Nomenclatura fuente: Per_BUA.dbf / variables H-series y P-series
# Esquema de salida: común con ingest_continua.R
#
# Decisiones documentadas:
#   - Variables de cohorte renombradas al esquema de la EPH continua
#   - NIVEL_ED recodificado desde P55 + P56 (ver tabla al pie)
#   - PONDII, PONDIIO, PP07H, EMPLEO, caes_seccion_label → NA (no existen)
#   - RAMA se preserva como columna propia (clasificación distinta a CAES)
#   - CODUSU, NRO_HOGAR, COMPONENTE incluidos para trazabilidad
#   - No se aplica organize_labels() ni organize_caes() (EPH puntual)
#   - FUENTE_BASE = "puntual" en todos los registros
#
# Tabla de equivalencia NIVEL_ED (P55 + P56 → esquema continua):
#   P55 = 3 (nunca asistió)                          → 7 (Sin Instrucción)
#   P56 = "  " (preescolar) o P55 = 1/2, P56 vacío  → 1 (Primario Incompleto)
#   P56 = "01" (primario completo, P55 = 2)          → 2 (Primario Completo)
#   P56 = "01" (primario, P55 = 1 = asiste)          → 1 (Primario Incompleto)
#   P56 = "02"-"06" (secundario, P55 = 2)            → 4 (Secundario Completo)
#   P56 = "02"-"06" (secundario, P55 = 1)            → 3 (Secundario Incompleto)
#   P56 = "07" (superior, P55 = 2)                   → 6 (Sup/Uni Completo)
#   P56 = "07" (superior, P55 = 1)                   → 5 (Sup/Uni Incompleto)
#   P56 = "08" (universitaria, P55 = 2)              → 6 (Sup/Uni Completo)
#   P56 = "08" (universitaria, P55 = 1)              → 5 (Sup/Uni Incompleto)
#   NS/NR                                             → 9
# =============================================================================

library(arrow)
library(dplyr)
library(purrr)

DATA_DIR  <- "data"
OUTPUT_DIR <- "data"

# Ondas disponibles: 1996O1 a 2003O1
# 2003O2 no existe (EPH pasa a continua en T3 2003)
ONDAS <- list(
  list(anio = 1996, onda = 1), list(anio = 1996, onda = 2),
  list(anio = 1997, onda = 1), list(anio = 1997, onda = 2),
  list(anio = 1998, onda = 1), list(anio = 1998, onda = 2),
  list(anio = 1999, onda = 1), list(anio = 1999, onda = 2),
  list(anio = 2000, onda = 1), list(anio = 2000, onda = 2),
  list(anio = 2001, onda = 1), list(anio = 2001, onda = 2),
  list(anio = 2002, onda = 1), list(anio = 2002, onda = 2),
  list(anio = 2003, onda = 1)
)

# -----------------------------------------------------------------------------
# Recodificación de nivel educativo desde P55 + P56
# -----------------------------------------------------------------------------
recodificar_nivel_ed <- function(p55, p56) {
  p56_trim <- trimws(as.character(p56))
  
  dplyr::case_when(
    p55 == 3                                      ~ 7L,  # Sin instrucción
    p56_trim %in% c("", "  ")                     ~ 1L,  # Primario incompleto (preescolar / vacío)
    p56_trim == "01" & p55 == 1                   ~ 1L,  # Primario incompleto (asiste)
    p56_trim == "01" & p55 == 2                   ~ 2L,  # Primario completo
    p56_trim %in% c("02","03","04","05","06") &
      p55 == 1                                    ~ 3L,  # Secundario incompleto
    p56_trim %in% c("02","03","04","05","06") &
      p55 == 2                                    ~ 4L,  # Secundario completo
    p56_trim %in% c("07","08") & p55 == 1         ~ 5L,  # Sup/Uni incompleto
    p56_trim %in% c("07","08") & p55 == 2         ~ 6L,  # Sup/Uni completo
    TRUE                                          ~ 9L   # NS/NR
  )
}

# -----------------------------------------------------------------------------
# Procesamiento de una onda individual
# -----------------------------------------------------------------------------
procesar_onda <- function(anio, onda) {
  nombre_archivo <- sprintf("base_individual_%dO%d", anio, onda)
  ruta_rds    <- file.path(DATA_DIR, paste0(nombre_archivo, ".RDS"))
  ruta_parquet <- file.path(OUTPUT_DIR, paste0(nombre_archivo, ".parquet"))
  
  # Idempotencia: saltar si el parquet ya existe
  if (file.exists(ruta_parquet)) {
    cat(sprintf("✓ Ya existe: %s — omitido\n", nombre_archivo))
    return(invisible(NULL))
  }
  
  if (!file.exists(ruta_rds)) {
    cat(sprintf("✗ No encontrado: %s\n", ruta_rds))
    return(invisible(NULL))
  }
  
  cat(sprintf("→ Procesando: %s\n", nombre_archivo))
  raw <- readRDS(ruta_rds)
  
  # Verificar variables mínimas necesarias
  vars_requeridas <- c("PONDERA", "ESTADO", "P21", "P47T")
  faltantes <- setdiff(vars_requeridas, names(raw))
  if (length(faltantes) > 0) {
    cat(sprintf("  ✗ Faltan variables requeridas: %s — omitido\n",
                paste(faltantes, collapse = ", ")))
    return(invisible(NULL))
  }
  
  # Columnas auxiliares: obtener con fallback a NA si no existen
  get_col <- function(df, col) {
    if (col %in% names(df)) df[[col]] else rep(NA, nrow(df))
  }
  
  out <- tibble(
    # Identificadores
    CODUSU      = get_col(raw, "CODUSU"),
    NRO_HOGAR   = NA_real_,          # No existe en puntual
    COMPONENTE  = get_col(raw, "COMPONENTE"),
    
    # Temporalidad
    ANO4         = as.integer(get_col(raw, "ANO4")),
    PERIODO      = as.integer(onda),
    TIPO_PERIODO = "onda",
    
    # Geografía
    REGION     = as.integer(get_col(raw, "REGION")),
    AGLOMERADO = as.integer(get_col(raw, "AGLOMERADO")),
    
    # Ponderadores
    PONDERA  = as.numeric(get_col(raw, "PONDERA")),
    PONDII   = NA_real_,   # No existe en puntual
    PONDIIO  = NA_real_,   # No existe en puntual
    
    # Variables de cohorte — renombradas desde nomenclatura puntual
    CH04     = as.integer(get_col(raw, "H13")),   # Sexo
    CH06     = as.integer(get_col(raw, "H12")),   # Edad
    
    # Nivel educativo — recodificado desde P55 + P56
    NIVEL_ED = recodificar_nivel_ed(
      get_col(raw, "P55"),
      get_col(raw, "P56")
    ),
    
    # Situación laboral
    ESTADO   = as.integer(get_col(raw, "ESTADO")),
    CAT_OCUP = as.integer(get_col(raw, "P17")),   # Categoría ocupacional
    CAT_INAC = as.integer(get_col(raw, "P11")),   # Situación del inactivo
    CH08     = as.integer(get_col(raw, "H16")),   # Cobertura de salud
    
    # Variables ausentes en puntual
    PP07H  = NA_real_,   # Descuento jubilatorio — no existe en puntual
    EMPLEO = NA_real_,   # Formalidad — no existe en puntual
    
    # Ingresos
    P21  = as.numeric(get_col(raw, "P21")),
    P47T = as.numeric(get_col(raw, "P47T")),
    
    # Clasificación sectorial
    RAMA               = as.integer(get_col(raw, "RAMA")),  # Clasificación propia puntual
    caes_seccion_label = NA_character_,   # No existe en puntual
    
    # Trazabilidad
    FUENTE_BASE = "puntual"
  )
  
  write_parquet(out, ruta_parquet)
  cat(sprintf("  ✓ Exportado: %s (%d filas)\n", ruta_parquet, nrow(out)))
  invisible(NULL)
}

# -----------------------------------------------------------------------------
# Ejecutar sobre todas las ondas
# -----------------------------------------------------------------------------
cat("=== Ingesta EPH puntual ===\n")
walk(ONDAS, function(o) procesar_onda(o$anio, o$onda))
cat("=== Completado ===\n")