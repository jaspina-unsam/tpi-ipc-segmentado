library(eph)
library(tidyverse)
library(readr)


process_year <- function(output_path, year, period) {
  fancy_name <- sprintf("base_ind_%d_%d", year, period)
  path_to_parquet <- file.path(output_path, paste0(fancy_name, ".csv"))

  if (file.exists(path_to_parquet)) {
    cat(sprintf("[INFO] %s exists. Consider deleting that file.\n", fancy_name))
    return(invisible(NULL))
  }

  tryCatch(
    {
      current_raw <- withCallingHandlers(
        get_microdata(
          year = year,
          period = period
        ),
        warning = function(w) {
          cat(sprintf(
            "[WARN] From get_microdata() year:%d, period:%d\n%s\n",
            year,
            period,
            conditionMessage(w)
          ))
          invokeRestart("muffleWarning")
        }
      )

      if (nrow(current_raw) == 0) {
        cat(sprintf("[INFO] %s has 0 rows.\n", fancy_name))
        return(invisible(NULL))
      }

      
      #current_raw <- current_raw %>%
      #  organize_labels() %>%
      #  organize_caes() %>%
      #  organize_cno()
      write_csv(current_raw, path_to_parquet)
      cat(sprintf("[INFO] Successfully exported: %s\n", fancy_name))
    },
    error = function(e) {
      cat(sprintf(
        "[ERR] Retry year %d, period %d: %s\n",
        year,
        period,
        conditionMessage(e)
      ))
    }
  )

  invisible(NULL)
}

output_dir <- "raw_eph_db"

for (yr in 1996:2002) {
  for (prd in c(1, 2)) {
    process_year(output_dir, yr, prd)
  }
}

process_year(output_dir, 2003, 1)
process_year(output_dir, 2003, 3)
process_year(output_dir, 2003, 4)

for (yr in 2004:2024) {
  for (prd in (1:4)) {
    process_year(output_dir, yr, prd)
  }
}

process_year(output_dir, 2025, 1)
process_year(output_dir, 2025, 2)
process_year(output_dir, 2025, 3)

# process_year(output_dir, 2011, 3)

# ?get_microdata
