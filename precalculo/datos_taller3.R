# =====================================================================
# datos_taller3.R — el dato que se descarga el estudiante del Taller 3
#
#   Estadística Espacial 2026-II (20929) · Corte III
#   Ver PLAN_Taller_3_SIG.md
#
# QUÉ PRODUCE
#   entrega/datos/taller3.gpkg               dos capas en EPSG:9377:
#                                            `localidades` (20) y
#                                            `perimetro_urbano` (1)
#   entrega/datos/taller3_sedes_3857.geojson las 2 209 sedes educativas,
#                                            A PROPÓSITO en EPSG:3857
#
# POR QUÉ LAS SEDES VAN EN OTRO SISTEMA DE REFERENCIA. La primera tarea
# del taller es reproyectarlas, y todo lo demás depende de haberlo hecho
# bien: quien las reetiquete en vez de reproyectarlas no tendrá ni una
# sede dentro de su localidad. El capítulo 2 lo dice (módulo 5); aquí se
# comprueba con las manos.
#
# Igual que en el Taller 2, se entregan las capas ENTERAS: recortarlas
# diría qué localidades entraron en el sorteo. Y no llevan ninguna
# columna calculada: ni conteos, ni áreas, ni densidades.
#
# Ejecutar SIEMPRE con el envoltorio:
#     precalculo/rscript.sh precalculo/datos_taller3.R
# =====================================================================

suppressPackageStartupMessages(library(sf))

AQUI <- "precalculo"
source(file.path(AQUI, "utf8.R"))

DESTINO <- file.path("entrega", "datos")
dir.create(DESTINO, showWarnings = FALSE, recursive = TRUE)
PROC <- "datos/procesado"

col <- st_read(file.path(PROC, "bogota_colegios.gpkg"),       quiet = TRUE)
loc <- st_read(file.path(PROC, "bogota_localidades.gpkg"),    quiet = TRUE)
urb <- st_read(file.path(PROC, "bogota_ventana_urbana.gpkg"), quiet = TRUE)
stopifnot(nrow(col) == 2209, nrow(loc) == 20, nrow(urb) == 1,
          st_crs(col)$epsg == 9377, st_crs(loc)$epsg == 9377, st_crs(urb)$epsg == 9377)

gpkg <- file.path(DESTINO, "taller3.gpkg")
if (file.exists(gpkg)) file.remove(gpkg)
st_write(loc[, c("cod_loca", "localidad")], gpkg, layer = "localidades", quiet = TRUE)
urb$nombre <- "Perímetro urbano de Bogotá"
st_write(urb[, "nombre"], gpkg, layer = "perimetro_urbano", quiet = TRUE)

# Las sedes, con los atributos que no revelan nada del taller, y SIN las
# columnas que ya traen la localidad: la pertenencia es geométrica y la
# calcula quien resuelve.
sedes <- col[, c("dane_sede", "nombre", "sector", "clase", "zona", "estrato")]
sedes <- st_transform(sedes, 3857)
geo <- file.path(DESTINO, "taller3_sedes_3857.geojson")
if (file.exists(geo)) file.remove(geo)
st_write(sedes, geo, driver = "GeoJSON", quiet = TRUE,
         layer_options = c("COORDINATE_PRECISION=3", "RFC7946=NO"))

# Lo que se acaba de escribir, leído de vuelta desde el disco.
v_loc <- st_read(gpkg, layer = "localidades", quiet = TRUE)
v_urb <- st_read(gpkg, layer = "perimetro_urbano", quiet = TRUE)
v_sed <- st_read(geo, quiet = TRUE)
stopifnot(nrow(v_loc) == 20, nrow(v_urb) == 1, nrow(v_sed) == 2209,
          st_crs(v_loc)$epsg == 9377, st_crs(v_sed)$epsg == 3857,
          !any(c("cod_loca", "localidad") %in% names(v_sed)))
# La vuelta a 9377 no se aleja de la capa original más de un milímetro.
d <- st_distance(st_transform(v_sed, 9377), col, by_element = TRUE)
stopifnot(max(as.numeric(d)) < 0.001)

message(sprintf("taller3.gpkg: %d localidades y el perímetro, EPSG:%d · %.0f KB",
                nrow(v_loc), st_crs(v_loc)$epsg, file.size(gpkg) / 1024))
message(sprintf("taller3_sedes_3857.geojson: %d sedes, EPSG:%d · %.0f KB",
                nrow(v_sed), st_crs(v_sed)$epsg, file.size(geo) / 1024))
