# =====================================================================
# Utilidades de procedencia — T0.4
#
# Material de Estadística Espacial 2026-II (20929).
#
# Tres cosas que todos los descargadores del hilo colombiano necesitan y
# que no conviene copiar y pegar en cada uno:
#
#   descarga()             — baja una vez y no vuelve a bajar
#   huella()               — SHA-256 del crudo
#   registra_procedencia() — añade una entrada a datos/procesado/procedencia.json
#                            SIN pisar las que ya estaban
#
# Por qué la huella. geoBoundaries se puede fijar por commit, pero
# datos.gov.co no: sus conjuntos se reemplazan en sitio y la URL sigue
# siendo la misma. Sin huella, una fuente que cambia bajo los pies pasa
# desapercibida y el material deja de cuadrar en silencio. Con huella, la
# reejecución grita.
# =====================================================================

descarga <- function(url, destino, forzar = FALSE) {
  if (forzar || !file.exists(destino)) {
    message("  descargando ", basename(destino))
    old <- getOption("timeout"); options(timeout = 1800)
    on.exit(options(timeout = old), add = TRUE)
    utils::download.file(url, destino, quiet = TRUE, mode = "wb")
  } else {
    message("  ya estaba: ", basename(destino),
            sprintf(" (%.1f MB)", file.size(destino) / 1024^2))
  }
  destino
}

huella <- function(ruta) {
  if (requireNamespace("digest", quietly = TRUE))
    return(digest::digest(file = ruta, algo = "sha256"))
  # Sin `digest` se cae a shasum, que en macOS viene de serie. Si tampoco
  # está, se declara NA en vez de fingir una huella.
  out <- suppressWarnings(tryCatch(
    system2("shasum", c("-a", "256", shQuote(ruta)), stdout = TRUE, stderr = FALSE),
    error = function(e) NA_character_))
  if (length(out) == 1 && !is.na(out)) sub(" .*$", "", out) else NA_character_
}

RUTA_PROCEDENCIA <- "datos/procesado/procedencia.json"

registra_procedencia <- function(entradas, ruta = RUTA_PROCEDENCIA) {
  previo <- if (file.exists(ruta))
    jsonlite::fromJSON(ruta, simplifyVector = FALSE) else list()
  for (nm in names(entradas)) previo[[nm]] <- entradas[[nm]]
  jsonlite::write_json(previo, ruta, auto_unbox = TRUE, pretty = TRUE)
  message("procedencia.json actualizado: ", length(previo), " fuentes registradas.")
  invisible(previo)
}

# ---------------------------------------------------------------------
# carga_municipios() — geometría una vez, atributos aparte
#
# Las tres capas municipales pesaban 78 MB CADA UNA porque cada una
# arrastraba su propia copia de la geometría sin simplificar de los 1 122
# municipios: 156 MB de duplicación pura. Ahora la geometría vive solo en
# `colombia_adm2.gpkg` y los atributos en CSV, que pesan kilobytes.
#
# La unión va por `shapeID`, que es la identidad que trae geoBoundaries y
# es estable dentro del commit fijado — NO por posición de fila, que se
# rompe en cuanto alguien reordena, ni por nombre, que ya sabemos lo que
# da. `divipola` sirve igual y es la llave hacia fuera.
#
#   muni <- carga_municipios()                    # todo
#   muni <- carga_municipios(saber11 = FALSE)     # solo llave + MEN
# ---------------------------------------------------------------------
carga_municipios <- function(saber11 = TRUE, proc = "datos/procesado") {
  g <- sf::st_read(file.path(proc, "colombia_adm2.gpkg"), quiet = TRUE)
  llave <- utils::read.csv(file.path(proc, "municipios_llave.csv"),
                           colClasses = "character", encoding = "UTF-8")
  i <- match(g$shapeID, llave$shapeID)
  if (anyNA(i)) stop(sprintf("%d poligono(s) sin fila en municipios_llave.csv", sum(is.na(i))))
  for (cl in setdiff(names(llave), "shapeID")) g[[cl]] <- llave[[cl]][i]
  for (cl in c("desercion", "cobertura")) g[[cl]] <- as.numeric(g[[cl]])

  if (saber11) {
    f <- file.path(proc, "municipios_saber11.csv")
    if (file.exists(f)) {
      s <- utils::read.csv(f, colClasses = c(divipola = "character"), encoding = "UTF-8")
      j <- match(g$divipola, s$divipola)
      for (cl in setdiff(names(s), "divipola")) g[[cl]] <- s[[cl]][j]
    } else warning("municipios_saber11.csv no existe todavia; se devuelve sin esas columnas")
  }
  g
}

# Comprobación de geometría que NO se salta nadie. Devuelve la capa ya
# reparada y el número de arreglos, para que la cifra viaje a procedencia.
valida_geometria <- function(x, etiqueta) {
  malas <- !sf::st_is_valid(x)
  n <- sum(malas, na.rm = TRUE)
  if (n > 0) {
    message(sprintf("  %s: %d geometria(s) invalida(s) -> st_make_valid", etiqueta, n))
    x <- sf::st_make_valid(x)
  }
  stopifnot(all(sf::st_is_valid(x)))
  list(x = x, reparadas = n)
}
