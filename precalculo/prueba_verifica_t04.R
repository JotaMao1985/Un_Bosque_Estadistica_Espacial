# =====================================================================
# T0.4 — Arnés de inyección para el auditor
#
# Material de Estadística Espacial 2026-II (20929).
#
# `verifica_t04.R` da 90 de 90. Eso, por sí solo, no dice nada: un
# verificador que nunca falla y un verificador que no comprueba nada
# producen la misma salida. Aquí se le rompe el dato A PROPÓSITO, defecto
# a defecto, y se exige que lo cace. Un defecto inyectado que pasa
# desapercibido es un agujero real del auditor.
#
# Cada inyección imita un fallo que PODRÍA ocurrir de verdad — no un
# disparate. Están tomadas de lo que ya salió mal en este proyecto: la
# coordenada centinela de la capa de sedes del MEN, el hueco de la llave
# DIVIPOLA, el cero que se cuela donde debía haber NA, el vacío contado
# como «No», y la geometría duplicándose otra vez en 78 MB por capa.
#
#   .../4.4-arm64/Resources/bin/Rscript precalculo/prueba_verifica_t04.R
# =====================================================================

suppressPackageStartupMessages({ library(sf); library(jsonlite) })

RSCRIPT <- file.path(R.home("bin"), "Rscript")
ORIG    <- normalizePath("datos/procesado")
BANCO   <- file.path(tempdir(), "t04_inyeccion")

prepara <- function() {
  unlink(BANCO, recursive = TRUE); dir.create(BANCO, recursive = TRUE)
  file.copy(list.files(ORIG, full.names = TRUE), BANCO, overwrite = TRUE)
  BANCO
}

# Cada inyección recibe la carpeta manipulable y devuelve una descripción.
INYECCIONES <- list(

  "llave DIVIPOLA con un hueco" = function(p) {
    f <- file.path(p, "municipios_llave.csv")
    x <- utils::read.csv(f, colClasses = "character"); x$divipola[7] <- NA
    utils::write.csv(x, f, row.names = FALSE, fileEncoding = "UTF-8")
    "un municipio se queda sin codigo"
  },

  "llave DIVIPOLA con un duplicado" = function(p) {
    f <- file.path(p, "municipios_llave.csv")
    x <- utils::read.csv(f, colClasses = "character"); x$divipola[7] <- x$divipola[8]
    utils::write.csv(x, f, row.names = FALSE, fileEncoding = "UTF-8")
    "dos municipios comparten codigo"
  },

  "codigo de departamento incoherente" = function(p) {
    f <- file.path(p, "municipios_llave.csv")
    x <- utils::read.csv(f, colClasses = "character")
    x$divipola[3] <- paste0("99", substr(x$divipola[3], 3, 5))
    utils::write.csv(x, f, row.names = FALSE, fileEncoding = "UTF-8")
    "el prefijo deja de cuadrar con la geometria"
  },

  "discrepancia con el DIVIPOLA sin ficha" = function(p) {
    f <- file.path(p, "municipios_llave.csv")
    x <- utils::read.csv(f, colClasses = "character"); x$divipola[500] <- "99999"
    utils::write.csv(x, f, row.names = FALSE, fileEncoding = "UTF-8")
    "un codigo que el DIVIPOLA no reconoce y que nadie explico"
  },

  "caso territorial sin documentar" = function(p) {
    f <- file.path(p, "casos_territoriales.json")
    j <- jsonlite::fromJSON(f, simplifyVector = FALSE)
    jsonlite::write_json(j[1], f, auto_unbox = TRUE, pretty = TRUE, na = "null")
    "se borra la ficha de Mapiripana"
  },

  "columna `tipo` mutilada" = function(p) {
    f <- file.path(p, "municipios_llave.csv")
    x <- utils::read.csv(f, colClasses = "character")
    x$tipo[grepl("no municipalizada", x$tipo)][1:5] <- "Municipio"
    utils::write.csv(x, f, row.names = FALSE, fileEncoding = "UTF-8")
    "5 areas no municipalizadas disfrazadas de municipio"
  },

  "brecha territorial que no reproduce el crudo" = function(p) {
    f <- file.path(p, "saber11_20224_cifras.json")
    j <- jsonlite::fromJSON(f, simplifyVector = FALSE)
    j$por_tipo_territorial$brecha_municipio_vs_area_no_municipalizada <- 12.34
    jsonlite::write_json(j, f, auto_unbox = TRUE, pretty = TRUE)
    "una cifra publicada que el crudo desmiente"
  },

  "la geometria vuelve a duplicarse" = function(p) {
    file.copy(file.path(p, "colombia_adm2.gpkg"),
              file.path(p, "colombia_municipios_saber11.gpkg"))
    "reaparecen los 78 MB por capa que se acaban de eliminar"
  },

  "coordenada centinela en los colegios" = function(p) {
    f <- file.path(p, "bogota_colegios_saber11.gpkg")
    x <- sf::st_read(f, quiet = TRUE)
    g <- sf::st_geometry(x); g[[5]] <- sf::st_point(c(-1.7976931348623157e308, 0))
    sf::st_geometry(x) <- sf::st_sfc(g, crs = sf::st_crs(x))
    sf::st_write(x, f, delete_dsn = TRUE, quiet = TRUE)
    "el fallo que tumbo la capa de sedes del MEN"
  },

  "columna en_urbana que miente" = function(p) {
    f <- file.path(p, "bogota_colegios_saber11.gpkg")
    x <- sf::st_read(f, quiet = TRUE); x$en_urbana[1:20] <- !x$en_urbana[1:20]
    sf::st_write(x, f, delete_dsn = TRUE, quiet = TRUE)
    "la columna deja de coincidir con el recuento espacial"
  },

  "estacion con altitud alterada" = function(p) {
    f <- file.path(p, "colombia_estaciones_clima.gpkg")
    x <- sf::st_read(f, quiet = TRUE); x$altitud_m <- x$altitud_m * 0.35
    sf::st_write(x, f, delete_dsn = TRUE, quiet = TRUE)
    "el gradiente termico se sale del rango fisico"
  },

  "dos estaciones en la misma coordenada" = function(p) {
    f <- file.path(p, "colombia_estaciones_clima.gpkg")
    x <- sf::st_read(f, quiet = TRUE)
    g <- sf::st_geometry(x); g[[2]] <- g[[1]]
    sf::st_geometry(x) <- sf::st_sfc(g, crs = sf::st_crs(x))
    sf::st_write(x, f, delete_dsn = TRUE, quiet = TRUE)
    "gstat abortaria al calcular el variograma"
  },

  "un cero donde debia ir NA" = function(p) {
    f <- file.path(p, "municipios_saber11.csv")
    x <- utils::read.csv(f, colClasses = c(divipola = "character"))
    x$s11_n[is.na(x$s11_n)][1] <- 0
    utils::write.csv(x, f, row.names = FALSE, fileEncoding = "UTF-8")
    "el dato inventado que T0.4a prohibio explicitamente"
  },

  "vacio contado como «No» en internet" = function(p) {
    f <- file.path(p, "municipios_saber11.csv")
    x <- utils::read.csv(f, colClasses = c(divipola = "character"))
    x$s11_pct_internet <- round(x$s11_pct_internet * 0.94, 2)   # el sesgo que tenia el script
    utils::write.csv(x, f, row.names = FALSE, fileEncoding = "UTF-8")
    "el fallo real que se encontro y corrigio en esta tarea"
  },

  "cifra del JSON que no reproduce el crudo" = function(p) {
    f <- file.path(p, "saber11_20224_cifras.json")
    j <- jsonlite::fromJSON(f, simplifyVector = FALSE)
    j$falacia_ecologica$educacion_madre$r_departamento <- 0.9123
    jsonlite::write_json(j, f, auto_unbox = TRUE, pretty = TRUE)
    "una cifra publicada que el crudo no respalda"
  },

  "procedencia sin huella" = function(p) {
    f <- file.path(p, "procedencia.json")
    j <- jsonlite::fromJSON(f, simplifyVector = FALSE)
    j$SABER11$sha256 <- NULL
    jsonlite::write_json(j, f, auto_unbox = TRUE, pretty = TRUE)
    "una fuente sin manera de detectar que cambio"
  },

  "procedencia sin licencia" = function(p) {
    f <- file.path(p, "procedencia.json")
    j <- jsonlite::fromJSON(f, simplifyVector = FALSE)
    j$CLIMA_ESTACIONES$licencia <- NULL
    jsonlite::write_json(j, f, auto_unbox = TRUE, pretty = TRUE)
    "material docente con una fuente sin licencia declarada"
  }
)

corre_auditor <- function(carpeta) {
  system2(RSCRIPT, "precalculo/verifica_t04.R",
          stdout = NULL, stderr = NULL,
          env = c(paste0("T04_PROC=", carpeta)))
}

message("control: el auditor sobre los datos BUENOS tiene que pasar")
base_ok <- corre_auditor(prepara()) == 0
message(sprintf("  [%s] copia intacta -> el auditor %s\n",
                if (base_ok) "OK" else "FALLA", if (base_ok) "pasa" else "FALLA SIN INYECTAR"))
if (!base_ok) { message("el control falla: el arnes no puede probar nada. Se aborta."); quit(status = 1L) }

message(sprintf("inyectando %d defectos, uno por uno", length(INYECCIONES)))
cazados <- 0L; escapados <- character()
for (nm in names(INYECCIONES)) {
  p <- prepara()
  detalle <- INYECCIONES[[nm]](p)
  cazado <- corre_auditor(p) != 0
  if (cazado) cazados <- cazados + 1L else escapados <- c(escapados, nm)
  message(sprintf("  [%s] %-42s %s", if (cazado) "CAZADO" else "ESCAPA", nm, detalle))
}
unlink(BANCO, recursive = TRUE)

cat(sprintf("\n=== %d de %d defectos inyectados cazados (%.0f%%) ===\n",
            cazados, length(INYECCIONES), 100 * cazados / length(INYECCIONES)))
if (length(escapados)) {
  cat("ESCAPARON — son agujeros reales del auditor:\n")
  for (e in escapados) cat("  -", e, "\n")
  quit(status = 1L)
}
cat("El auditor caza el 100% de los defectos inyectados.\n")
