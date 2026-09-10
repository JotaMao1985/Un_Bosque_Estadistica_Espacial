# =====================================================================
# T0.1 — Instalación del stack espacial de R
#
# Material de Estadística Espacial 2026-II (20929).
#
# Se corre con el envoltorio de la plataforma, que ya resuelve cuál es el
# R bueno —en macOS hay dos y solo una tiene `sf`; en Windows `Rscript.exe`
# ni siquiera está en el PATH—:
#
#     precalculo/rscript.sh   precalculo/instala.R    (macOS)
#     .\precalculo\rscript.ps1 precalculo\instala.R    (Windows)
#
# Todos los paquetes de la lista tienen binario arm64 verificado el
# 2026-08-03, así que en macOS ninguno debería compilar. En Windows CRAN
# publica binario de todos, así que tampoco.
# =====================================================================

options(repos = c(CRAN = "https://cran.rstudio.com"))

# El orden importa poco (R resuelve dependencias), pero se agrupa por
# para-qué-sirve para que se lea como el plan.
PAQUETES <- c(
  # --- lo que usa TODO el precálculo, y que hasta ahora no estaba aquí ---
  # Los tres llegaban de rebote como dependencia de los de abajo, así que
  # en esta máquina «ya estaban» y nadie los echó de menos. Depender de
  # una dependencia transitiva es depender de que nadie cambie la suya.
  # `digest` es además el que calcula el SHA-256 de `huella()`: sin él, en
  # Windows no hay huella —`shasum` no existe allí— y `fuentes.R` para.
  "sf", "jsonlite", "digest",
  # --- lo que usan los `datos_*.R` para DESCARGAR y armar las fuentes ---
  # Mismo caso que los de arriba: llegaban de rebote y nadie los echó de
  # menos. `stringi` lo usa `llave_divipola.R` para normalizar los nombres
  # de municipio; `data.table` lo usan `datos_saber11.R` y `verifica_t04.R`
  # para los 130 MB del CSV del ICFES, que con `read.csv` no es viable; y
  # `sp` lo usa `datos_clima.R`. Sin ellos, reconstruir `datos/` desde cero
  # falla en el tercer guion de la cadena.
  "stringi", "data.table", "sp",
  # --- datos de área y econometría espacial (caps. 6, 7, 8) ---
  "spdep", "spatialreg", "sfdep",
  # `dbscan` no se usa para agrupar: lo EXIGE `spdep::soi.graph`, la
  # esfera de influencia del módulo 6 del capítulo 6, y sin él la llamada
  # muere con «dbscan required» — no con un aviso, con un error. Añadido
  # el 2026-09-03, por decisión de Javier tras el cronómetro del A.25.
  "dbscan",
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
