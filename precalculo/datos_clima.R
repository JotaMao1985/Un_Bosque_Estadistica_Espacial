# =====================================================================
# T0.4 — Los puntos con valor continuo: normales climatológicas del IDEAM
#
# Material de Estadística Espacial 2026-II (20929).
#
# Es el conjunto GEOESTADÍSTICO del hilo colombiano (capítulo 9). Un dato
# geoestadístico de verdad: Z(s) —la temperatura media anual— existe en
# TODO punto del país y se observa en n estaciones. No es un patrón
# puntual (las estaciones no son aleatorias) ni un dato de área.
#
# Por qué este y no el valor del suelo de Bogotá: el valor del suelo se
# publica por MANZANA, o sea que es dato de ÁREA. Krigearlo obliga a bajar
# a centroides y arrastra el problema de cambio de soporte, que es justo
# lo contrario de lo que el capítulo 9 quiere enseñar.
#
# Y trae de regalo el módulo 10 (kriging universal y con deriva externa):
# la ALTITUD viene en el mismo archivo y correlaciona con la temperatura
# a un nivel que no admite discusión. El capítulo puede mostrar, con dato
# real, por qué el kriging ordinario está mal planteado aquí.
#
# Correr desde la carpeta del curso:
#   .../4.4-arm64/Resources/bin/Rscript precalculo/datos_clima.R
# =====================================================================

# La guarda de codificacion va PRIMERO: sin ella jsonlite escribe las
# tildes como <c3><b3> sin fallar, y el emparejamiento por categoria
# con tilde deja de emparejar en silencio. Ver precalculo/utf8.R.
source("precalculo/utf8.R")
source("precalculo/entorno.R")
source("precalculo/fuentes.R")
suppressPackageStartupMessages({
  library(sf); library(jsonlite); library(sp); library(gstat)
})

CRUDO <- "datos/crudo"; PROC <- "datos/procesado"
dir.create(CRUDO, recursive = TRUE, showWarnings = FALSE)

# El conjunto se reemplaza en sitio (no hay commit que fijar), así que la
# reproducibilidad se apoya en la HUELLA del crudo: si el IDEAM lo cambia,
# la reejecución lo canta en vez de dejar cifras viejas en el material.
RECURSO   <- "nsz2-kzcq"
PERIODO   <- "1991-2020"     # la normal vigente de la OMM
PARAMETRO <- "TEMPERATURA MEDIA"
CRS_TRABAJO <- 9377

url_socrata <- function(recurso, periodo, parametro) {
  sprintf("https://www.datos.gov.co/resource/%s.json?%s",
          recurso,
          paste0("$limit=5000&$where=",
                 utils::URLencode(sprintf("periodo='%s' AND par_metro='%s'", periodo, parametro),
                                  reserved = TRUE)))
}

# ---------------------------------------------------------------------
# 1. Descarga
# ---------------------------------------------------------------------
message("1. normales climatologicas del IDEAM (", PERIODO, ", ", PARAMETRO, ")")
f <- descarga(url_socrata(RECURSO, PERIODO, PARAMETRO),
              file.path(CRUDO, "ideam_normales_tmedia_1991_2020.json"))
dat <- jsonlite::fromJSON(f)
message(sprintf("  %d estaciones", nrow(dat)))

num <- function(v) suppressWarnings(as.numeric(v))
dat$lat   <- num(dat$latitud)
dat$lon   <- num(dat$longitud)
dat$alt   <- num(dat$altitud_m)
dat$t_med <- num(dat$anual)

# ---------------------------------------------------------------------
# 2. Verificación ANTES de usar nada
# ---------------------------------------------------------------------
message("2. verificacion")
falta <- is.na(dat$lat) | is.na(dat$lon) | is.na(dat$alt) | is.na(dat$t_med)
if (any(falta)) {
  message(sprintf("  %d estacion(es) sin coordenada, altitud o valor -> se descartan", sum(falta)))
  dat <- dat[!falta, ]
}

est <- sf::st_as_sf(dat, coords = c("lon", "lat"), crs = 4326, remove = FALSE)

# ¿Caen DENTRO de Colombia? Se comprueba contra la capa nacional, que es
# otra fuente (DANE vía geoBoundaries). Es el mismo principio que tumbó a
# `finiterank/mapa-colombia-js`, cuyas coordenadas ponían el país en la
# latitud 33-52 N: una fuente cuyos puntos no caen en el país no se usa.
pais <- sf::st_read(file.path(PROC, "colombia_adm1.gpkg"), quiet = TRUE)
pais_u <- sf::st_union(sf::st_transform(sf::st_geometry(pais), 4326))
dentro <- lengths(sf::st_within(sf::st_geometry(est), pais_u)) == 1
message(sprintf("  dentro del territorio nacional: %d de %d", sum(dentro), nrow(est)))
if (any(!dentro)) {
  d <- as.numeric(sf::st_distance(est[!dentro, ], sf::st_boundary(pais_u)))
  for (k in seq_len(sum(!dentro)))
    message(sprintf("     FUERA: %-34s (%s) a %.1f km del borde",
                    est$estaci_n[!dentro][k], est$departamento[!dentro][k], d[k] / 1000))
  message("  nota: las coordenadas de la fuente vienen a 2 decimales (~1,1 km);")
  message("        a esa resolucion una estacion costera puede caer al otro lado de la linea.")
}
est$en_territorio <- dentro

est <- sf::st_transform(est, CRS_TRABAJO)

# Localizaciones repetidas: gstat aborta al calcular el variograma si dos
# observaciones comparten coordenada. Se detectan y se declaran; no se
# desplazan a ojo.
co <- sf::st_coordinates(est)
dup <- duplicated(co)
if (any(dup)) {
  message(sprintf("  %d estacion(es) con coordenada repetida -> se conserva la primera:", sum(dup)))
  for (i in which(dup)) message("     ", est$estaci_n[i], " (", est$municipio[i], ")")
  est <- est[!dup, ]
}
message(sprintf("  quedan %d estaciones en localizaciones distintas", nrow(est)))

message(sprintf("  altitud: %.0f a %.0f m  |  temperatura media anual: %.1f a %.1f C",
                min(est$alt), max(est$alt), min(est$t_med), max(est$t_med)))

# ---------------------------------------------------------------------
# 3. ¿ENSEÑA? Un dato que cuadra no basta: tiene que dar clase.
#
# Tres comprobaciones, y las tres son material del capítulo 9:
#   a) la tendencia con la altitud  -> por qué el kriging ORDINARIO está
#      mal planteado aquí (módulos 9 y 10)
#   b) el variograma del dato crudo -> sin meseta clara, la firma de una
#      tendencia no modelada
#   c) el variograma de los RESIDUOS tras quitar la altitud -> pepita,
#      meseta y rango legibles (módulo 5)
# ---------------------------------------------------------------------
message("3. validacion como material didactico")

r_alt <- cor(est$alt, est$t_med)
aj <- lm(t_med ~ alt, data = est)
gradiente <- coef(aj)[["alt"]] * 1000     # C por cada 1 000 m
message(sprintf("  a) corr(altitud, T) = %.4f  |  R2 = %.4f  |  gradiente = %.2f C por 1000 m",
                r_alt, summary(aj)$r.squared, gradiente))
message(sprintf("     (el gradiente adiabatico de referencia esta entre -5 y -7 C por 1000 m)"))

sp_est <- as(est, "Spatial")
sp_est$resid <- residuals(aj)

vg_crudo <- gstat::variogram(t_med ~ 1,   sp_est)
vg_resid <- gstat::variogram(resid ~ 1,   sp_est)

ajusta <- function(vg, etiqueta) {
  ini <- gstat::vgm(psill = max(vg$gamma) * 0.7, model = "Sph",
                    range = max(vg$dist) / 3, nugget = min(vg$gamma))
  m <- tryCatch(gstat::fit.variogram(vg, ini), warning = function(w) NULL, error = function(e) NULL)
  if (is.null(m)) { message(sprintf("     %s: el ajuste no converge", etiqueta)); return(NULL) }
  pep <- if (m$model[1] == "Nug") m$psill[1] else 0
  mes <- sum(m$psill); ran <- m$range[nrow(m)]
  message(sprintf("     %s: pepita %.3f | meseta %.3f | rango %.1f km | pepita/meseta %.1f%%",
                  etiqueta, pep, mes, ran / 1000, 100 * pep / mes))
  list(pepita = pep, meseta = mes, rango_km = ran / 1000, razon_pepita = pep / mes)
}
message("  b) variograma del dato crudo (con la tendencia dentro):")
m_crudo <- ajusta(vg_crudo, "crudo  ")
message("  c) variograma de los residuos (quitada la altitud):")
m_resid <- ajusta(vg_resid, "residuo")

# OJO: st_distance devuelve una matriz CON UNIDADES; as.numeric() le quita
# las dimensiones y la deja en vector. Hay que rearmarla.
nn <- matrix(as.numeric(sf::st_distance(est)), nrow = nrow(est))
diag(nn) <- Inf
d_vecino <- apply(nn, 1, min)
message(sprintf("  distancia al vecino mas proximo: mediana %.1f km, minima %.1f, maxima %.1f",
                median(d_vecino) / 1000, min(d_vecino) / 1000, max(d_vecino) / 1000))

# ---------------------------------------------------------------------
# 4. Salida
# ---------------------------------------------------------------------
est$codigo    <- as.character(est$c_digo)
est$estacion  <- est$estaci_n
salida <- est[, c("codigo", "estacion", "municipio", "departamento",
                  "alt", "t_med", "en_territorio", "categoria")]
names(salida)[names(salida) == "alt"]   <- "altitud_m"
names(salida)[names(salida) == "t_med"] <- "t_media_anual"

destino <- file.path(PROC, "colombia_estaciones_clima.gpkg")
sf::st_write(salida, destino, delete_dsn = TRUE, quiet = TRUE)
message("\n", destino, " escrito: ", nrow(salida), " estaciones.")

registra_procedencia(list(CLIMA_ESTACIONES = list(
  capa = "colombia_estaciones_clima.gpkg", n = nrow(salida),
  variable = "temperatura media anual (C), normal 1991-2020",
  covariable = "altitud (m), en el mismo archivo",
  url = url_socrata(RECURSO, PERIODO, PARAMETRO),
  recurso = RECURSO, periodo = PERIODO, parametro = PARAMETRO,
  fuente = "Instituto de Hidrologia, Meteorologia y Estudios Ambientales (IDEAM)",
  redistribuidor = "datos.gov.co (Socrata)",
  licencia = "CC BY-SA 4.0",
  fuente_url = "https://www.datos.gov.co/d/nsz2-kzcq",
  crs = CRS_TRABAJO,
  precision_coordenadas = "2 decimales de grado (~1,1 km); despreciable frente a la mediana de distancia entre estaciones",
  corr_altitud_temperatura = round(r_alt, 4),
  gradiente_c_por_1000m = round(gradiente, 2),
  rango_km_variograma_residuos = if (!is.null(m_resid)) round(m_resid$rango_km, 1) else NA,
  sha256 = huella(f), descargado = as.character(Sys.Date()),
  uso = "datos geoestadisticos, capitulo 9 (variograma y kriging)")))
