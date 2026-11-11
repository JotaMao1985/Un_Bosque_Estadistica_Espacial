# =====================================================================
# genera_taller3.R — las variantes del Taller 3 y la clave del lado de R
#
#   Estadística Espacial 2026-II (20929) · Corte III
#   Ver PLAN_Taller_3_SIG.md
#
# QUÉ PRODUCE
#   precalculo/salidas/taller3_datos.json   LO QUE SE PUBLICA: las 1000
#       variantes, las localidades elegibles con su n, su área y su
#       lambda, y los valores que puede traer una variante. Ninguna
#       respuesta.
#   precalculo/cache/taller3_claves_r.json  LO QUE NO SE PUBLICA: las
#       cifras de T5 (lo que el estudiante corre en R) por localidad y
#       por radio. `cache/` está fuera del repositorio.
#
# POR QUÉ ESTE GUION SÍ SE VERSIONA, a diferencia de los generadores de
# los Talleres 1 y 2. Aquellos construían los patrones SABIENDO de qué
# familia era cada uno, y leerlos era leer la respuesta. Este no sabe
# nada que el enunciado no diga: reparte una localidad y cuatro números,
# y las respuestas salen de hacer el taller. Lo que no viaja es el JSON
# de claves.
#
# LA REGLA DE PERTENENCIA ES GEOMÉTRICA, como en el Taller 2: las sedes
# de una localidad son las que caen dentro de su polígono, que es lo que
# el estudiante obtiene en QGIS con «Extraer por localización».
#
# Ejecutar SIEMPRE con el envoltorio:
#     precalculo/rscript.sh precalculo/genera_taller3.R
# =====================================================================

suppressPackageStartupMessages({
  library(sf)
  library(spatstat)
  library(jsonlite)
})

AQUI <- "precalculo"
source(file.path(AQUI, "utf8.R"))

SEMILLA   <- 2026L
N_MIN     <- 35L                     # sedes para que una localidad entre al sorteo
NX        <- c(3L, 4L, 5L)           # T3 · lado de la rejilla de cuadrantes
R_GF      <- c(100L, 150L, 200L)     # T3 · radio de lectura de G y F, en metros
R_KL      <- c(200L, 300L, 400L)     # T3 · radio de lectura de L, en metros
RADIOS    <- c(600L, 800L, 1000L)    # T4 · radio del mapa de calor, en metros
N_VARIANTES <- 1000L

DATOS <- file.path("entrega", "datos")
loc   <- st_read(file.path(DATOS, "taller3.gpkg"), layer = "localidades", quiet = TRUE)
sedes <- st_read(file.path(DATOS, "taller3_sedes_3857.geojson"), quiet = TRUE)
stopifnot(nrow(loc) == 20, nrow(sedes) == 2209,
          st_crs(loc)$epsg == 9377, st_crs(sedes)$epsg == 3857)
sedes <- st_transform(sedes, 9377)

DENTRO <- st_intersects(st_geometry(sedes), st_geometry(loc), sparse = FALSE)
stopifnot(all(rowSums(DENTRO) <= 1))
loc$n_sedes  <- as.integer(colSums(DENTRO))
loc$area_km2 <- as.numeric(st_area(loc)) / 1e6
loc$lambda   <- loc$n_sedes / loc$area_km2
elegibles <- loc[loc$n_sedes >= N_MIN, ]
elegibles <- elegibles[order(elegibles$localidad), ]
stopifnot(nrow(elegibles) == 16)
message(sprintf("%d localidades elegibles (n >= %d): de %d a %d sedes",
                nrow(elegibles), N_MIN, min(elegibles$n_sedes), max(elegibles$n_sedes)))

# ---------------------------------------------------------------------
# A. Las 1000 variantes
#
# Cada columna se reparte por separado y en bloques iguales, barajada con
# su propia corriente de la semilla: así cada localidad y cada valor salen
# casi el mismo número de veces, y saber la localidad de un compañero no
# dice nada de sus otros cuatro números.
# ---------------------------------------------------------------------
set.seed(SEMILLA)
reparte <- function(valores) sample(rep(valores, length.out = N_VARIANTES))
variantes <- data.frame(
  clave     = sprintf("%03d", 0:(N_VARIANTES - 1L)),
  localidad = reparte(elegibles$localidad),
  nx        = reparte(NX),
  r_gf      = reparte(R_GF),
  r_kl      = reparte(R_KL),
  radio     = reparte(RADIOS),
  stringsAsFactors = FALSE
)
stopifnot(!anyDuplicated(variantes$clave),
          all(table(variantes$localidad) >= floor(N_VARIANTES / 16)),
          nrow(unique(variantes[, -1])) > 500)

publico <- list(
  semilla  = SEMILLA,
  n_min    = N_MIN,
  opciones = list(nx = NX, r_gf = R_GF, r_kl = R_KL, radio = RADIOS),
  ciudad   = list(sedes = nrow(sedes), localidades = nrow(loc),
                  sedes_en_alguna_localidad = sum(loc$n_sedes)),
  localidades = setNames(lapply(seq_len(nrow(elegibles)), function(i) list(
    n = elegibles$n_sedes[i],
    area_km2 = round(elegibles$area_km2[i], 5),
    lambda = round(elegibles$lambda[i], 5))), elegibles$localidad),
  variantes = variantes
)
dir.create(file.path(AQUI, "salidas"), showWarnings = FALSE)
write_json(publico, file.path(AQUI, "salidas", "taller3_datos.json"),
           auto_unbox = TRUE, digits = NA, pretty = FALSE)
message(sprintf("salidas/taller3_datos.json: %d variantes, %d combinaciones distintas",
                nrow(variantes), nrow(unique(variantes[, -1]))))

# ---------------------------------------------------------------------
# B. La clave de T5: lo que el estudiante corre en R, por localidad
#
# Es, línea por línea, el bloque de código del enunciado.
# ---------------------------------------------------------------------
xy <- st_coordinates(sedes)
claves <- list()
for (i in seq_len(nrow(elegibles))) {
  nom <- elegibles$localidad[i]
  w <- as.owin(st_geometry(elegibles[i, ]))
  d <- inside.owin(xy[, 1], xy[, 2], w)
  p <- ppp(xy[d, 1], xy[d, 2], window = w, check = FALSE)
  stopifnot(npoints(p) == elegibles$n_sedes[i])

  calor <- list()
  for (R in RADIOS) {
    sigma <- R / sqrt(8)
    sin <- density(p, sigma = sigma, kernel = "quartic", edge = FALSE, eps = 50)
    con <- density(p, sigma = sigma, kernel = "quartic", edge = TRUE, diggle = TRUE, eps = 50)
    calor[[as.character(R)]] <- list(sigma = sigma,
      pico_sin = max(sin), masa_sin = integral(sin),
      pico_con = max(con), masa_con = integral(con))
  }
  bd <- bw.diggle(p)
  bp <- bw.ppl(p)
  q <- rescale(shift(p, origin = "centroid"), 1000, "km")
  m <- ppm(q ~ x + y)
  cs <- coef(summary(m))
  claves[[nom]] <- list(
    n = npoints(p), area_km2 = area(w) / 1e6,
    calor = calor,
    bw_diggle = as.numeric(bd), bw_ppl = as.numeric(bp),
    ppl_en_el_limite = isTRUE(all.equal(as.numeric(bp), max(attr(bp, "h")))) ||
                       isTRUE(all.equal(as.numeric(bp), min(attr(bp, "h")))),
    radio_qgis_diggle = as.numeric(bd) * sqrt(8), radio_qgis_ppl = as.numeric(bp) * sqrt(8),
    ppm = list(x = unname(cs["x", "Estimate"]), z_x = unname(cs["x", "Zval"]),
               y = unname(cs["y", "Estimate"]), z_y = unname(cs["y", "Zval"])))
  message(sprintf("  %-20s n = %3d  diggle %6.1f m  ppl %6.1f m", nom, npoints(p), bd, bp))
}
dir.create(file.path(AQUI, "cache"), showWarnings = FALSE)
write_json(claves, file.path(AQUI, "cache", "taller3_claves_r.json"),
           auto_unbox = TRUE, digits = NA, pretty = TRUE)
message("cache/taller3_claves_r.json: la clave de T5 (fuera del repositorio)")
