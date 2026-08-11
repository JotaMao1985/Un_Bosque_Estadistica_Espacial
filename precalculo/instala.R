# =====================================================================
# T0.1 — Instalación del stack espacial de R
#
# Material de Estadística Espacial 2026-II (20929).
#
# OJO: hay dos R en esta máquina y solo una sirve. Este script tiene que
# correrse con
#   /Library/Frameworks/R.framework/Versions/4.4-arm64/Resources/bin/Rscript
# El Rscript del PATH es Homebrew 4.6.0 y no tiene ni sf.
#
# Todos los paquetes de la lista tienen binario arm64 verificado el
# 2026-08-03, así que ninguno debería compilar.
# =====================================================================

options(repos = c(CRAN = "https://cran.rstudio.com"))

# El orden importa poco (R resuelve dependencias), pero se agrupa por
# para-qué-sirve para que se lea como el plan.
PAQUETES <- c(
  # --- datos de área y econometría espacial (caps. 6, 7, 8) ---
  "spdep", "spatialreg", "sfdep",
  # --- geoestadística (cap. 9) ---
  "gstat",
  # --- patrones puntuales (caps. 4, 5). spatstat es meta-paquete y
  #     arrastra .geom, .random, .explore, .model, .data, .univar ---
  "spatstat",
  # --- cartografía y clasificación (cap. 3) ---
  "tmap", "classInt", "RColorBrewer",
  # --- datos ---
  "spData", "HistData",
  # --- rásteres y superficies (caps. 5, 9, 10) ---
  "stars",
  # --- ML espacial (cap. 10) ---
  "blockCV", "spatialsample",
  # --- regresión geográficamente ponderada (cap. 8) ---
  "GWmodel",
  # --- simplificación de geometría para el .geomapa (T0.3) ---
  "rmapshaper"
)

faltan <- PAQUETES[!vapply(PAQUETES, requireNamespace, logical(1), quietly = TRUE)]

if (length(faltan) == 0L) {
  cat("Nada que instalar: los", length(PAQUETES), "paquetes ya están.\n")
} else {
  cat("Instalando", length(faltan), "paquetes:", paste(faltan, collapse = ", "), "\n\n")
  install.packages(faltan, type = "binary", quiet = FALSE)
}

# ---------------------------------------------------------------------
# Informe: qué quedó instalado y qué no
# ---------------------------------------------------------------------
cat("\n=== RESULTADO ===\n")
ok <- vapply(PAQUETES, requireNamespace, logical(1), quietly = TRUE)
for (p in PAQUETES) {
  cat(sprintf("%-16s %s\n", p,
              if (ok[[p]]) paste("OK", as.character(packageVersion(p))) else "FALLO"))
}
cat(sprintf("\n%d de %d instalados.\n", sum(ok), length(PAQUETES)))
if (any(!ok)) {
  cat("FALTAN:", paste(PAQUETES[!ok], collapse = ", "), "\n")
  quit(status = 1L)
}
