# =====================================================================
# T0.3 — Datos de demostración del componente .geomapa
#
# Genera un JSON con los CINCO modos, para el capítulo de prueba que
# valida el componente antes de escribir el capítulo 1.
#
# Correr desde la carpeta del curso:
#   .../4.4-arm64/Resources/bin/Rscript precalculo/genera_demo_geomapa.R
# =====================================================================

source("precalculo/entorno.R")
source("precalculo/geo.R")

suppressPackageStartupMessages({
  library(spdep); library(spData); library(spatstat.data); library(spatstat.explore)
})

set.seed(SEMILLA)
demo <- list(meta = list(generado = as.character(Sys.Date()), semilla = SEMILLA,
                         script = "precalculo/genera_demo_geomapa.R"))

# ---------------------------------------------------------------------
# 1. POLÍGONOS — coropleto de la tasa de SIDS en Carolina del Norte
#
# Se mapea la TASA (casos por mil nacimientos), no el conteo: el mapa de
# conteos sería el mapa de la población. Es la lección del módulo 2 del
# capítulo 3, y conviene que el propio dato de demostración la respete.
# ---------------------------------------------------------------------
message("1. poligonos (nc, tasa de SIDS)")
nc <- sf::st_read(system.file("shape/nc.shp", package = "sf"), quiet = TRUE)
nc <- sf::st_transform(nc, 32119)          # NAD83 / North Carolina, en metros
nc$tasa <- 1000 * nc$SID74 / nc$BIR74

demo$poligonos <- geo_poligonos(
  nc, valor = nc$tasa, n_clases = 5, estilo = "quantile",
  etiquetas = nc$NAME, titulo = "Tasa de SIDS 1974-78, Carolina del Norte",
  leyenda = "casos por 1000 nacimientos", presupuesto = 6000L)

# ---------------------------------------------------------------------
# 2. PUNTOS — los tres regímenes de patrón puntual
# ---------------------------------------------------------------------
message("2. puntos (japanesepines, cells, redwood)")
demo$puntos <- lapply(
  list(list(d = spatstat.data::japanesepines, t = "Pinos japoneses (aleatorio)"),
       list(d = spatstat.data::cells,         t = "Celulas (regular)"),
       list(d = spatstat.data::redwood,       t = "Secuoyas (agregado)")),
  function(e) {
    p <- e$d; w <- p$window
    geo_puntos(cbind(p$x, p$y),
               ventana = c(w$xrange[1], w$yrange[1], w$xrange[2], w$yrange[2]),
               titulo = e$t, leyenda = sprintf("n = %d", p$n))
  })

# ---------------------------------------------------------------------
# 3. GRAFO — vecindad de contigüidad reina sobre Columbus
#
# Columbus (49 barrios) es el dato canónico de Anselin: las cifras del
# capítulo 8 se podrán contrastar contra su libro.
# ---------------------------------------------------------------------
message("3. grafo (columbus, reina y k=4)")
col <- sf::st_read(system.file("shapes/columbus.gpkg", package = "spData")[1], quiet = TRUE)
nb_reina <- spdep::poly2nb(col, queen = TRUE)
nb_torre <- spdep::poly2nb(col, queen = FALSE)
nb_knn4  <- spdep::knn2nb(spdep::knearneigh(sf::st_point_on_surface(sf::st_geometry(col)), k = 4))

# Las tres variantes comparten la geometria: repetirla triplicaria el
# peso sin anadir nada. En el capitulo 6 seran ~10 definiciones de W.
demo$grafo <- geo_grafo_multi(
  col,
  list(reina = nb_reina, torre = nb_torre, knn4 = nb_knn4),
  titulo = "Vecindad sobre Columbus", leyenda = "Columbus, 49 barrios")

# ---------------------------------------------------------------------
# 4. REJILLA — intensidad por núcleos sobre bei, con tres anchos de banda
#
# El ancho de banda es lo que importa (módulo 2 del capítulo 5), así que
# la demostración trae tres para que el simulador pueda conmutarlos.
# ---------------------------------------------------------------------
message("4. rejilla (KDE de bei con 3 anchos de banda)")
bei <- spatstat.data::bei
w   <- bei$window
caja <- c(w$xrange[1], w$yrange[1], w$xrange[2], w$yrange[2])
anchos <- c(10, 30, 80)
demo$rejilla <- lapply(anchos, function(sg) {
  d <- spatstat.explore::density.ppp(bei, sigma = sg, dimyx = c(48, 96))
  # density.ppp devuelve la fila 1 abajo; el navegador pinta de arriba
  # abajo, asi que se invierte aqui y no en JS.
  z <- d$v[nrow(d$v):1, ]
  geo_rejilla(z, caja, titulo = sprintf("Intensidad por nucleos, sigma = %d m", sg),
              leyenda = "arboles por m2", n_clases = 7, estilo = "equal")
})
names(demo$rejilla) <- paste0("sigma", anchos)

# ---------------------------------------------------------------------
# 5. PROYECCIÓN — Colombia y el mundo bajo varios CRS
#
# La distorsión se mide comparando el área proyectada contra el área
# geodésica sobre el elipsoide. Se incluyen los dos CRS oficiales de
# Colombia (3116 y 9377), que es el hilo colombiano del curso.
# ---------------------------------------------------------------------
message("5. proyeccion (mundo y Colombia)")
mundo <- spData::world[, c("name_long", "continent")]
mundo <- sf::st_make_valid(mundo)
demo$proyeccion_mundo <- geo_proyeccion(
  mundo,
  list(list(nombre = "WGS84 sin proyectar (4326)", crs = 4326, familia = "geografica"),
       list(nombre = "Web Mercator (3857)",        crs = 3857, familia = "conforme"),
       list(nombre = "Mollweide",                  crs = "+proj=moll", familia = "equivalente"),
       list(nombre = "Equal Earth (8857)",         crs = 8857, familia = "equivalente"),
       list(nombre = "Robinson",                   crs = "+proj=robin", familia = "compromiso")),
  titulo = "El mismo mundo bajo cinco sistemas de referencia", presupuesto = 1400L,
  # Las indicatrices de Tissot, que estrena T2.1a. El banco de pruebas
  # tiene que EJERCITAR el componente nuevo, o la regla del §9 se cumple
  # a medias: retropropagar el motor sin darle un caso que lo use deja el
  # código nuevo sin una sola comprobación en el navegador.
  tissot = list(lon = rep(seq(-150, 150, by = 60), times = 5),
                lat = rep(seq(-60, 60, by = 30), each = 6)),
  radio_km = 500)

col_pais <- mundo[mundo$name_long == "Colombia", ]
demo$proyeccion_colombia <- geo_proyeccion(
  col_pais,
  list(list(nombre = "WGS84 (4326)",                    crs = 4326, familia = "geografica"),
       list(nombre = "Web Mercator (3857)",             crs = 3857, familia = "conforme"),
       list(nombre = "MAGNA-SIRGAS / Bogota (3116)",    crs = 3116, familia = "conforme"),
       list(nombre = "MAGNA-SIRGAS / Origen Nal (9377)", crs = 9377, familia = "conforme")),
  titulo = "Colombia y sus sistemas de referencia oficiales", presupuesto = 2500L,
  tissot = list(lon = rep(c(-77, -74, -71, -68), each = 4),
                lat = rep(c(-3, 2, 7, 11), times = 4)),
  radio_km = 120)

# ---------------------------------------------------------------------
# 6. PUNTOS CON CAPAS — lo que el modo `puntos` aprendió en T1.2
#
# El modo `puntos` de T0.3 pintaba una sola nube, de un solo color, sobre
# nada. El mapa de Snow del capítulo 1 pedía cuatro cosas más —calles de
# fondo, una segunda capa de otro tipo de objeto, una de ellas resaltada y
# color por marca categórica— y T1.2 las añadió. Entran aquí, al banco de
# pruebas permanente del componente, porque un componente que solo se
# ejercita dentro del capítulo que lo estrenó se rompe en el siguiente sin
# que nadie se entere. Es la regla del §9 del plan.
#
# Se usan los datos reales de Snow y no un juguete: el caso difícil es
# justamente el real —528 polilíneas y 13 categorías, que es MÁS de lo que
# una paleta cualitativa aguanta—, y un juguete de tres calles habría dado
# verde sin probar nada.
message("6. puntos con capas (Snow: calles, bombas y marca categorica)")
suppressPackageStartupMessages(library(HistData))
data(Snow.deaths); data(Snow.pumps); data(Snow.streets)

mu_xy <- as.matrix(Snow.deaths[, c("x", "y")])
bo_xy <- as.matrix(Snow.pumps[,  c("x", "y")])
i_bs  <- which(Snow.pumps$label == "Broad St")
stopifnot(length(i_bs) == 1L)

dm  <- as.matrix(dist(rbind(mu_xy, bo_xy)))[seq_len(nrow(mu_xy)),
                                            nrow(mu_xy) + seq_len(nrow(bo_xy))]
cer <- max.col(-dm, ties.method = "first")

demo$puntos_capas <- geo_puntos(
  mu_xy,
  marcas = factor(as.character(Snow.pumps$label)[cer],
                  levels = as.character(Snow.pumps$label)),
  lineas = unname(lapply(split(Snow.streets, Snow.streets$street),
                         function(s) as.matrix(s[, c("x", "y")]))),
  puntos2 = bo_xy, etiquetas2 = as.character(Snow.pumps$label),
  resaltado2 = i_bs,
  titulo = "Puntos con capas: muertes, calles y bombas",
  leyenda = "marca categorica = bomba mas proxima")

# 7. PUNTOS CON MARCA NUMÉRICA — la otra rama de `marcas_tipo`
#
# Sin este caso el banco probaría una sola de las dos ramas, y la que no
# se ejercita es la que se rompe. `meuse` es además el canónico del
# capítulo 9, así que la rampa se ve sobre el dato que la va a usar.
message("7. puntos con marca numerica (meuse, zinc)")
suppressPackageStartupMessages(library(sp))
data(meuse, package = "sp")
demo$puntos_numericos <- geo_puntos(
  as.matrix(meuse[, c("x", "y")]), marcas = as.numeric(meuse$zinc),
  titulo = "Puntos con marca numerica: zinc en la vega del Mosa",
  leyenda = "marca numerica = ppm de zinc")

stopifnot(identical(demo$puntos_capas$marcas_tipo, "categoria"),
          identical(demo$puntos_numericos$marcas_tipo, "numero"),
          length(demo$puntos_capas$niveles) == 13L,
          is.null(demo$puntos_numericos$niveles))

# 8. LO QUE ESTRENA EL CAPÍTULO 3 (T2.4)
#
# Tres cosas nuevas del motor, y las tres entran aquí como caso
# PERMANENTE: capas —varias variables sobre una misma geometría—,
# codificación por diferencias, y capas de puntos superpuestas al
# coropleto. La regla del §9 dice que un componente no está terminado
# hasta que está en la plantilla Y en el banco de pruebas.
#
# El sujeto es `nc`, que es barato y ya está en el banco: 100 condados
# con dos variables reales (SID74 y BIR74) que además NO se clasifican
# igual, así que conmutar de capa cambia el mapa de verdad y no
# repintaría lo mismo con otro rótulo.
message("8. capas, diferencias y superpuestos (nc)")
# Semilla PROPIA y declarada: el dot density de juguete usa `runif`, y sin
# sembrarla `demo_geomapa.json` dejaría de salir idéntico byte a byte
# entre ejecuciones, que es el criterio con el que se verifica el banco.
set.seed(3038L)
nc8 <- st_transform(st_read(system.file("shape/nc.shp", package = "sf"), quiet = TRUE), 32119)
ctr8 <- st_coordinates(st_centroid(st_geometry(nc8), of_largest_polygon = TRUE))[, 1:2]
demo$capas_delta <- geo_poligonos(
  nc8, presupuesto = 1500L, delta = TRUE, verbose = FALSE,
  etiquetas = nc8$NAME,
  titulo = "Capas + diferencias + superpuestos (Carolina del Norte)",
  leyenda = "conmuta la capa y la vista",
  capas = list(
    list(id = "sid74", etiqueta = "Muertes súbitas 1974-78", leyenda = "SID74",
         valor = nc8$SID74, n_clases = 5, estilo = "quantile",
         vistas = lapply(c("equal", "quantile", "fisher"), function(e)
           list(estilo = e, n = 5, etiqueta = e))),
    list(id = "bir74", etiqueta = "Nacimientos 1974-78", leyenda = "BIR74",
         valor = nc8$BIR74, n_clases = 5, estilo = "quantile")),
  superpuestos = list(
    list(id = "simbolos", modo = "simbolo", xy = ctr8, valor = nc8$BIR74,
         etiqueta = "Símbolos proporcionales a los nacimientos"),
    list(id = "densidad", modo = "densidad",
         xy = ctr8[rep(seq_len(nrow(ctr8)), 3), ] +
              matrix(stats::runif(3 * nrow(ctr8) * 2, -8000, 8000), ncol = 2),
         etiqueta = "Dot density de juguete")))

# Las tres propiedades que el navegador va a suponer, comprobadas aquí:
# la codificación va declarada, las capas son una LISTA (no un objeto) y
# cada capa reparte los 100 condados.
stopifnot(identical(demo$capas_delta$codificacion, "delta"),
          length(demo$capas_delta$capas) == 2L,
          is.null(names(demo$capas_delta$capas)),
          all(vapply(demo$capas_delta$capas, function(c) sum(c$tam) == 100L, logical(1))),
          length(demo$capas_delta$superpuestos) == 2L,
          identical(demo$capas_delta$superpuestos[[1]]$modo, "simbolo"),
          identical(demo$capas_delta$superpuestos[[2]]$modo, "densidad"))

# Y la comprobación que de verdad importa de las diferencias: que
# reconstruyan la geometría absoluta. `geo_poligonos` ya para si no lo
# hacen, pero aquí se vuelve a comprobar contra el mapa SIN delta, que
# es un camino distinto.
abs8 <- geo_poligonos(nc8, presupuesto = 1500L, verbose = FALSE)
recon8 <- lapply(demo$capas_delta$geom, function(f) lapply(f, function(p) {
  n <- length(p); if (n <= 2L) return(p)
  as.integer(rbind(cumsum(p[seq(1, n, by = 2)]), cumsum(p[seq(2, n, by = 2)])))
}))
if (!identical(recon8, abs8$geom))
  stop("las diferencias del caso 8 no reconstruyen la geometria absoluta")
message("   diferencias verificadas contra la geometria absoluta")

# ---------------------------------------------------------------------
geo_escribe(demo, "precalculo/demo_geomapa.json", presupuesto_kb = 260)
message("\nlisto.")
