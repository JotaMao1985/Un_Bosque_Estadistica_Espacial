# =====================================================================
# T0.4 — El hilo colombiano de datos abiertos
#
# Material de Estadística Espacial 2026-II (20929).
#
# Descarga, verifica y congela las capas colombianas que recorren el
# curso. Reglas que se cumplen aquí y hay que seguir cumpliendo:
#
#   * De cada fuente se documentan URL, licencia, fecha de corte y fecha
#     de descarga, y eso viaja al material. Nada sin verificar.
#   * Las URL van FIJADAS POR COMMIT donde se pueda: una URL "current"
#     cambia bajo los pies y el material deja de reproducirse.
#   * La geometría se guarda en GeoPackage, no en shapefile: el
#     shapefile trunca los nombres de campo a 10 caracteres y no lleva
#     el CRS de forma fiable. Es además lo que enseña el capítulo 2.
#
# Correr desde la carpeta del curso:
#   .../4.4-arm64/Resources/bin/Rscript precalculo/datos_colombia.R
# =====================================================================

# La guarda de codificacion va PRIMERO: sin ella jsonlite escribe las
# tildes como <c3><b3> sin fallar, y el emparejamiento por categoria
# con tilde deja de emparejar en silencio. Ver precalculo/utf8.R.
source("precalculo/utf8.R")
source("precalculo/entorno.R")
suppressPackageStartupMessages(library(sf))

CRUDO <- "datos/crudo"
PROC  <- "datos/procesado"
dir.create(CRUDO, recursive = TRUE, showWarnings = FALSE)
dir.create(PROC,  recursive = TRUE, showWarnings = FALSE)

# El commit de geoBoundaries se fija a mano: es lo que hace que esto se
# pueda volver a ejecutar dentro de un año y dé lo mismo.
GB_COMMIT <- "9469f09"
gb_url <- function(nivel)
  sprintf("https://github.com/wmgeolab/geoBoundaries/raw/%s/releaseData/gbOpen/COL/%s/geoBoundaries-COL-%s.geojson",
          GB_COMMIT, nivel, nivel)

procedencia <- list()

descarga <- function(url, destino) {
  if (!file.exists(destino)) {
    message("  descargando ", basename(destino))
    utils::download.file(url, destino, quiet = TRUE, mode = "wb")
  } else message("  ya estaba: ", basename(destino))
  destino
}

# ---------------------------------------------------------------------
# 1. Límites administrativos — DANE MGN vía geoBoundaries (CC BY 4.0)
# ---------------------------------------------------------------------
message("1. limites administrativos")

for (nivel in c("ADM1", "ADM2")) {
  f <- descarga(gb_url(nivel), file.path(CRUDO, paste0("COL_", nivel, ".geojson")))
  x <- sf::st_read(f, quiet = TRUE)

  # Verificación de geometría ANTES de usar nada
  malos <- !sf::st_is_valid(x)
  n_malos <- sum(malos, na.rm = TRUE)
  if (n_malos > 0) {
    message(sprintf("  %s: %d geometria(s) invalida(s) -> st_make_valid", nivel, n_malos))
    x <- sf::st_make_valid(x)
  }
  stopifnot(all(sf::st_is_valid(x)))

  # Se proyecta a MAGNA-SIRGAS / Origen Nacional (EPSG:9377), que es el
  # CRS oficial de Colombia para cartografía nacional. Guardar en 4326
  # obligaria a reproyectar en cada capitulo.
  xp <- sf::st_transform(x, 9377)

  destino <- file.path(PROC, paste0("colombia_", tolower(nivel), ".gpkg"))
  sf::st_write(xp, destino, delete_dsn = TRUE, quiet = TRUE)

  message(sprintf("  %s: %d rasgos, CRS 9377, %s", nivel, nrow(xp), basename(destino)))
  procedencia[[nivel]] <- list(
    nivel = nivel, n = nrow(xp), url = gb_url(nivel),
    fuente = "Departamento Administrativo Nacional de Estadistica (DANE), Marco Geoestadistico Nacional",
    redistribuidor = "geoBoundaries (gbOpen), College of William & Mary",
    licencia = "CC BY 4.0",
    fuente_url = "https://geoportal.dane.gov.co/servicios/descarga-y-metadatos/descarga-mgn-marco-geoestadistico-nacional/",
    commit = GB_COMMIT,
    geometrias_reparadas = n_malos,
    descargado = as.character(Sys.Date()))
}

# ---------------------------------------------------------------------
# Informe
# ---------------------------------------------------------------------
jsonlite::write_json(procedencia, file.path(PROC, "procedencia.json"),
                     auto_unbox = TRUE, pretty = TRUE)
message("\nprocedencia.json escrito.")

for (nivel in names(procedencia)) {
  p <- procedencia[[nivel]]
  message(sprintf("  %s: n = %d, licencia %s, reparadas %d",
                  p$nivel, p$n, p$licencia, p$geometrias_reparadas))
}
