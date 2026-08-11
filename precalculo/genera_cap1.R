# =====================================================================
# genera_cap1.R — el precálculo del capítulo 1 (T1.1)
#
#   «Datos espaciales y la primera ley de la geografía» · semana 1
#   Material de Estadística Espacial 2026-II (20929).
#
# QUÉ PRODUCE
#   precalculo/salidas/cap1_datos.json   todas las cifras de los 12 módulos
#   precalculo/salidas/cap1_mapas.json   las fuentes de los .geomapa
#   precalculo/salidas/cap1_dep.csv      un CSV que R y Python leen igual
#
# LA REGLA QUE MANDA (D10): ninguna cifra del capítulo se escribe a mano.
# Si el texto la argumenta, sale de aquí. Y la regla de publicación de
# T0.5: toda cifra de la que el texto argumenta se publica con >= 5
# decimales, así que el JSON se guarda con 10 — holgura por debajo, para
# que no haya doble redondeo entre la prosa y el bloque de código.
#
# LO QUE ESTE CAPÍTULO TIENE QUE **MEDIR** Y NO AFIRMAR
#   · módulo 1  el argumento de Snow: proporción de muertes cuya bomba más
#               próxima es Broad Street, y la historia del mango de la
#               bomba contrastada con las fechas (es apócrifa, y se ve).
#   · módulo 4  cuánto se subestima el e.e. bajo autocorrelación. Dos
#               frentes: Monte Carlo sobre campo gaussiano CON su error de
#               Monte Carlo, y réplica por remuestreo sobre dato real.
#   · módulo 7  el efecto escala del MAUP con la deserción colombiana.
#   · módulo 10 la inflación del desempeño con validación cruzada
#               aleatoria. Frontera declarada: aquí se mide UN caso; el
#               desarrollo (blockCV, área de aplicabilidad, tamaño de
#               bloque) es del capítulo 10.
#
# Ejecutar SIEMPRE con el envoltorio, nunca con `Rscript` a pelo:
#     precalculo/rscript.sh precalculo/genera_cap1.R
# desde la carpeta `Estadistica espacial/`. Ver utf8.R y rscript.sh.
# =====================================================================

suppressPackageStartupMessages({
  library(sf)
  library(sp)
  library(spdep)
  library(spData)
  library(spatstat.data)
  library(spatstat.geom)
  library(HistData)
  library(jsonlite)
  library(classInt)
})

AQUI <- "precalculo"
source(file.path(AQUI, "utf8.R"))     # PRIMERO: para si el proceso no es UTF-8
source(file.path(AQUI, "fuentes.R"))
source(file.path(AQUI, "geo.R"))

SALIDAS <- file.path(AQUI, "salidas")
dir.create(SALIDAS, showWarnings = FALSE, recursive = TRUE)

SEMILLA <- 2026L
set.seed(SEMILLA)
options(stringsAsFactors = FALSE)

# 10 decimales: la regla de T0.5. Publicar 5 con el JSON guardado a 6
# provocaba que la prosa dijera 3.95446 y el bloque de código del propio
# capítulo imprimiera 3.95447.
r10 <- function(x) round(as.numeric(x), 10)

# ---------------------------------------------------------------------
# ancla() — la transcripción contra la literatura, que PARA si falla
#
# Heredado de `verifica_contra_texto` de Diseño de Experimentos. No es
# decorativo: es la única defensa contra un dato canónico mal cargado.
# Un `japanesepines` con 64 puntos en vez de 65 no da error en ninguna
# parte, y el capítulo entero quedaría desalineado con Baddeley.
# ---------------------------------------------------------------------
N_ANCLAS <- 0L
ancla <- function(calculado, publicado, que, tol = 1e-6) {
  N_ANCLAS <<- N_ANCLAS + 1L
  d <- abs(as.numeric(calculado) - as.numeric(publicado))
  if (!is.finite(d) || d > tol)
    stop(sprintf("ANCLA ROTA · %s: calculado %.8f, la fuente publica %.8f (dif %.2e)",
                 que, as.numeric(calculado), as.numeric(publicado), d))
  invisible(TRUE)
}

D <- list()

# =====================================================================
# A. MÓDULO 1 — El mapa que cambió la epidemiología
# =====================================================================
message("A · Snow, Broad Street 1854")

data(Snow.deaths);   data(Snow.pumps)
data(Snow.streets);  data(Snow.polygons);  data(Snow.dates)

# Anclas contra lo que documenta HistData y contra Snow (1855).
ancla(nrow(Snow.deaths),  578, "muertes digitalizadas por Dodson-Tobler")
ancla(nrow(Snow.pumps),    13, "bombas del mapa")
ancla(length(unique(Snow.streets$street)), 528, "segmentos de calle")
ancla(length(Snow.polygons), 13, "polígonos de Thiessen, uno por bomba")
ancla(sum(Snow.dates$deaths), 616, "muertes de la tabla de Snow (1855)")

muertes <- as.matrix(Snow.deaths[, c("x", "y")])
bombas  <- as.matrix(Snow.pumps[,  c("x", "y")])
i_broad <- which(Snow.pumps$label == "Broad St")
stopifnot(length(i_broad) == 1L)

# Matriz de distancias muerte x bomba, en unidades del mapa.
#
# LAS UNIDADES. Las coordenadas son las de la digitalización de Rusty
# Dodson (NCGIA, 1992) sobre el mapa de Snow: un sistema LOCAL, sin datum
# y sin escala publicada. Así que aquí no se convierte a metros —eso
# sería inventarse un factor— y todo lo que el capítulo argumenta son
# PROPORCIONES y RAZONES, que son invariantes a la escala. El sistema sin
# datum es además el primer gancho hacia el capítulo 2.
dmat <- as.matrix(dist(rbind(muertes, bombas)))[seq_len(nrow(muertes)),
                                                nrow(muertes) + seq_len(nrow(bombas))]
mas_cerca  <- max.col(-dmat, ties.method = "first")
d_su_bomba <- dmat[cbind(seq_len(nrow(dmat)), mas_cerca)]
d_broad    <- dmat[, i_broad]

# La segunda bomba más próxima: es lo que convierte «están cerca de Broad
# Street» en un argumento. Si la más próxima fuera cualquiera, la razón
# entre la primera y la segunda rondaría 1.
d_orden  <- t(apply(dmat, 1, sort))
d_segunda <- d_orden[, 2]

# CAMINO INDEPENDIENTE, y no es un adorno: la asignación por distancia
# euclídea se contrasta contra los polígonos de Thiessen que Tobler
# distribuye con el dato. Son dos construcciones distintas de la misma
# idea; si discreparan, una de las dos está mal y publicar cualquiera de
# ellas sería publicar un resultado sin verificar.
celda_tobler <- rep(NA_integer_, nrow(muertes))
for (k in seq_along(Snow.polygons)) {
  pol <- Snow.polygons[[k]]
  dentro <- sp::point.in.polygon(muertes[, 1], muertes[, 2], pol$x, pol$y) > 0
  celda_tobler[dentro] <- k
}
n_asignadas  <- sum(!is.na(celda_tobler))
n_coinciden  <- sum(celda_tobler == mas_cerca, na.rm = TRUE)
if (n_asignadas > 0 && n_coinciden / n_asignadas < 0.98)
  stop(sprintf("los dos caminos discrepan en %d de %d muertes",
               n_asignadas - n_coinciden, n_asignadas))

# --- La historia del mango de la bomba, contrastada con las fechas -----
# La versión popular dice que la epidemia acabó cuando Snow hizo quitar
# el mango, el 8 de septiembre. Los datos de la propia tabla de Snow
# dicen otra cosa, y el capítulo lo mide en vez de repetirlo.
fecha_mango <- as.Date("1854-09-08")
sd_dat <- Snow.dates[!is.na(Snow.dates$date), ]
i_pico <- which.max(sd_dat$attacks)
ataques_antes <- sum(sd_dat$attacks[sd_dat$date < fecha_mango])
ataques_desde <- sum(sd_dat$attacks[sd_dat$date >= fecha_mango])

D$snow <- list(
  n_muertes   = nrow(muertes),
  n_bombas    = nrow(bombas),
  n_segmentos = length(unique(Snow.streets$street)),
  n_vertices_calle = nrow(Snow.streets),
  bomba_broad = i_broad,
  # El argumento espacial, medido
  n_mas_cerca_broad  = sum(mas_cerca == i_broad),
  pct_mas_cerca_broad = r10(100 * mean(mas_cerca == i_broad)),
  # Si las muertes se repartieran por igual entre las 13 bombas
  pct_esperado_uniforme = r10(100 / nrow(bombas)),
  razon_sobre_uniforme  = r10(mean(mas_cerca == i_broad) * nrow(bombas)),
  dist_media_broad   = r10(mean(d_broad)),
  dist_mediana_broad = r10(median(d_broad)),
  dist_media_su_bomba = r10(mean(d_su_bomba)),
  # La razón entre la bomba más próxima y la segunda. Adimensional, así
  # que no depende de la escala desconocida del mapa.
  razon_primera_segunda = r10(mean(d_su_bomba / d_segunda)),
  # Verificación cruzada contra los polígonos de Thiessen de Tobler
  n_en_poligono = n_asignadas,
  n_coinciden_tobler = n_coinciden,
  pct_coinciden_tobler = r10(100 * n_coinciden / n_asignadas),
  # La cronología
  fecha_pico   = format(sd_dat$date[i_pico]),
  ataques_pico = as.integer(sd_dat$attacks[i_pico]),
  fecha_mango  = format(fecha_mango),
  ataques_dia_mango = as.integer(sd_dat$attacks[sd_dat$date == fecha_mango]),
  ataques_antes_mango = as.integer(ataques_antes),
  ataques_desde_mango = as.integer(ataques_desde),
  pct_ataques_antes_mango = r10(100 * ataques_antes / (ataques_antes + ataques_desde)),
  # Cuánto había caído ya el brote el día del mango, respecto del pico
  caida_hasta_mango_pct = r10(100 * (1 - sd_dat$attacks[sd_dat$date == fecha_mango] /
                                       sd_dat$attacks[i_pico])),
  muertes_tabla = as.integer(sum(sd_dat$deaths)),
  # La tabla de Snow trae 44 filas y una de ellas no lleva fecha (recoge
  # las muertes anteriores al brote). La serie que se publica son las 43
  # con fecha, y se dice cuántas se quedaron fuera en vez de dejar que la
  # resta la haga quien lea.
  n_dias_tabla = as.integer(nrow(Snow.dates)),
  n_dias_con_fecha = as.integer(nrow(sd_dat)),
  n_dias_sin_fecha = as.integer(nrow(Snow.dates) - nrow(sd_dat)),
  serie_fecha   = format(sd_dat$date),
  serie_ataques = as.integer(sd_dat$attacks),
  serie_muertes = as.integer(sd_dat$deaths)
)

# =====================================================================
# B. MÓDULO 2 — Los tres tipos de dato espacial
#
# Cada tipo, dos veces: el canónico de la literatura (que el estudiante
# puede contrastar contra Baddeley, Bivand y Pebesma) y su gemelo
# colombiano (decisión de Javier, 2026-08-03). Lo que cambia entre los
# tres tipos es QUÉ ES ALEATORIO, y por eso se publica de cada uno el
# mismo puñado de cifras.
# =====================================================================
message("B · Los tres tipos de dato, canónico y colombiano")

# --- B.1 Patrón puntual: lo aleatorio es la LOCALIZACIÓN --------------
data(japanesepines); data(redwood); data(cells); data(bei)
ancla(npoints(japanesepines), 65, "japanesepines (Numata)")
ancla(npoints(redwood),       62, "redwood (Strauss/Ripley)")
ancla(npoints(cells),         42, "cells (Crick-Ripley)")
ancla(npoints(bei),         3604, "bei (Condit, Barro Colorado)")
ancla(area.owin(bei$window), 5e5, "ventana de bei: 1000 x 500 m", tol = 1)

resumen_ppp <- function(p, nombre, fuente) {
  a <- area.owin(p$window)
  list(nombre = nombre, fuente = fuente, n = npoints(p),
       area = r10(a), lambda = r10(npoints(p) / a),
       # La distancia media al vecino más próximo separa los tres
       # regímenes sin necesidad de ninguna función de resumen todavía.
       nn_media = r10(mean(nndist(p))),
       nn_sd    = r10(sd(nndist(p))),
       # Bajo CSR, E[d_nn] = 1/(2 sqrt(lambda)). El cociente contra ese
       # valor es el índice de Clark-Evans, y es lo que ordena los tres
       # regímenes: < 1 agregado, = 1 aleatorio, > 1 regular.
       #
       # `nn_esperada` es ese denominador publicado aparte, y no es
       # redundancia: el módulo 3 enseña el índice poniendo las dos
       # distancias una al lado de la otra —la observada y la que daría
       # el azar—, y sin la segunda el cociente habría que creérselo. No
       # se puede calcular en el ensamblador: D10 y `sin_aritmetica.py`
       # exigen que toda cifra de la prosa nazca aquí. (2026-08-10)
       nn_esperada = r10(0.5 / sqrt(npoints(p) / a)),
       clark_evans = r10(mean(nndist(p)) / (0.5 / sqrt(npoints(p) / a))),
       # --- La misma R, corrigiendo el EFECTO DE BORDE -----------------
       # 1/(2 sqrt(lambda)) vale para una ventana infinita. En una finita,
       # un punto pegado al borde puede tener su vecino de verdad FUERA, y
       # `nndist` devuelve entonces el de dentro, que está más lejos: el
       # numerador sale inflado y R con él. Donnelly (1978) lo compensa
       # subiendo el denominador con un término que depende del perímetro.
       #
       # Se escribe la fórmula en vez de llamar a spatstat.explore, por la
       # misma razón que el módulo 3 escribe la I de Moran en la pestaña de
       # Python: heredar la función esconde el convenio. Pero se ANCLA
       # contra ella más abajo, así que el convenio queda a la vista Y
       # verificado contra la implementación de referencia.
       #
       # El 0.0412 es el que usa spatstat (`clarkevansCalc`), no el 0.041
       # que suele citarse: con 0.041 la fórmula se separa de la función en
       # 2e-5, por encima de la tolerancia del ancla. Se descubrió porque el
       # ancla lo paró, que es exactamente para lo que está.
       clark_evans_donnelly = r10(
         mean(nndist(p)) /
           (0.5 * sqrt(a / npoints(p)) +
              (0.0514 + 0.0412 / sqrt(npoints(p))) *
              perimeter(p$window) / npoints(p))))
}

D$puntual_canonico <- list(
  japanesepines = resumen_ppp(japanesepines, "Pinos japoneses",
                              "Numata (1961), vía spatstat.data"),
  redwood       = resumen_ppp(redwood, "Plántulas de secuoya",
                              "Strauss (1975) / Ripley (1977), vía spatstat.data"),
  cells         = resumen_ppp(cells, "Células biológicas",
                              "Crick y Ripley, vía spatstat.data")
)

# Las anclas de la R corregida contra la implementación de referencia.
# `clarkevans()` vive en spatstat.explore y devuelve TRES valores —naive,
# Donnelly y cdf—; aquí se contrasta el segundo contra la fórmula escrita
# arriba, y de paso el primero contra la R sin corregir, que es lo que
# publica la tabla del módulo 3. Si spatstat cambiara de convenio, esto
# para el precálculo en vez de dejar pasar una cifra distinta.
local({
  ce <- spatstat.explore::clarkevans(japanesepines)
  ancla(ce[["naive"]],    D$puntual_canonico$japanesepines$clark_evans,
        "japanesepines: R sin corregir contra spatstat")
  ancla(ce[["Donnelly"]], D$puntual_canonico$japanesepines$clark_evans_donnelly,
        "japanesepines: R de Donnelly contra spatstat")
  for (nm in c("redwood", "cells")) {
    ce <- spatstat.explore::clarkevans(get(nm))
    ancla(ce[["naive"]],    D$puntual_canonico[[nm]]$clark_evans,
          paste0(nm, ": R sin corregir contra spatstat"))
    ancla(ce[["Donnelly"]], D$puntual_canonico[[nm]]$clark_evans_donnelly,
          paste0(nm, ": R de Donnelly contra spatstat"))
  }
})

# --- B.2 Dato de área: lo aleatorio es el VALOR en unidades fijas ------
# Dos lecturas del mismo archivo a propósito: `nc0` es el objeto tal como
# lo recibe el estudiante y es el que describe el módulo 9; `nc` es el que
# este script manipula (le añade la tasa). Describir la anatomía del
# objeto ya tocado sería describir otra cosa.
nc0 <- st_read(system.file("shape/nc.shp", package = "sf"), quiet = TRUE)
nc  <- st_read(system.file("shape/nc.shp", package = "sf"), quiet = TRUE)
ancla(nrow(nc), 100, "condados de Carolina del Norte")
ancla(ncol(nc0), 15, "columnas del shapefile nc (14 atributos + geometría)")
ancla(sum(nc$SID74), 667, "muertes súbitas infantiles 1974-78 (nc)")
ancla(sum(nc$BIR74), 329962, "nacimientos 1974-78 (nc)")

nc$tasa_sids <- 1000 * nc$SID74 / nc$BIR74
# El área proyectada, en la misma zona UTM 17N con la que se dibuja el
# mapa (`nc_proj`, más abajo). Medir áreas sobre las coordenadas
# geográficas de NAD27 las deformaría, y aquí el área ENTRA en una
# correlación que se publica: no es un adorno del mapa.
nc_area_km2 <- as.numeric(st_area(st_transform(nc, 32617))) / 1e6

D$area_canonico <- list(
  nombre = "SIDS de Carolina del Norte, 1974-78",
  fuente = "Cressie (1993) / Bivand, Pebesma y Gómez-Rubio (2013), vía sf",
  n = nrow(nc),
  sid74_total = as.integer(sum(nc$SID74)),
  bir74_total = as.integer(sum(nc$BIR74)),
  tasa_media  = r10(mean(nc$tasa_sids)),
  tasa_sd     = r10(sd(nc$tasa_sids)),
  tasa_min    = r10(min(nc$tasa_sids)),
  tasa_max    = r10(max(nc$tasa_sids)),
  # La tasa global NO es la media de las tasas. Es la primera pincelada
  # del módulo 2 del capítulo 3 («normalizar o mentir») y aquí ya se ve.
  tasa_global = r10(1000 * sum(nc$SID74) / sum(nc$BIR74)),
  # Cuánto se separan, que es lo que el módulo argumenta. Sin publicarla,
  # el texto tendría que decir «difieren» sin decir cuánto.
  diferencia_media_global = r10(mean(nc$tasa_sids) -
                                  1000 * sum(nc$SID74) / sum(nc$BIR74)),
  diferencia_media_global_pct = r10(
    100 * (mean(nc$tasa_sids) / (1000 * sum(nc$SID74) / sum(nc$BIR74)) - 1)),
  # --- El SOPORTE (Pebesma y Bivand, cap. 5 y §10.2) ------------------
  # Extensiva frente a intensiva, MEDIDO en vez de afirmado. El libro
  # avisa de que pintar una variable extensiva en un coropleta arriesga
  # pintar el tamaño de la unidad; aquí se le pone cifra, y la cifra
  # corrige al aviso genérico: en un dato de salud el conteo crudo no
  # sigue tanto al ÁREA como al DENOMINADOR —los nacimientos—, que es
  # justo por lo que se divide por población y no por superficie. Se
  # publican las dos correlaciones del conteo, y no solo la del área,
  # porque la comparación entre ellas ES el argumento.
  soporte = list(
    cor_conteo_nacimientos = r10(cor(nc$SID74, nc$BIR74)),
    cor_conteo_area        = r10(cor(nc$SID74, nc_area_km2)),
    cor_tasa_nacimientos   = r10(cor(nc$tasa_sids, nc$BIR74)),
    # Cuánto varía el denominador entre condados: si fuera 1 el conteo y
    # la tasa ordenarían igual y nada de esto importaría.
    razon_nacimientos      = r10(max(nc$BIR74) / min(nc$BIR74))
  ),
  crs_epsg    = if (is.na(st_crs(nc)$epsg)) NA_integer_ else st_crs(nc)$epsg,
  crs_nombre  = "NAD27 (EPSG:4267)"
)

# --- B.3 Dato geoestadístico: el valor existe en TODO punto -----------
data(meuse, package = "sp")
ancla(nrow(meuse), 155, "observaciones de meuse")
ancla(min(meuse$zinc), 113, "zinc mínimo en meuse")
ancla(max(meuse$zinc), 1839, "zinc máximo en meuse")

D$geo_canonico <- list(
  nombre = "Metales pesados en la vega del Mosa (meuse)",
  fuente = "Burrough y McDonnell (1998) / Pebesma, vía sp",
  n = nrow(meuse),
  zinc_media  = r10(mean(meuse$zinc)),
  zinc_sd     = r10(sd(meuse$zinc)),
  zinc_min    = as.integer(min(meuse$zinc)),
  zinc_max    = as.integer(max(meuse$zinc)),
  # log porque el zinc es fuertemente asimétrico: es lo que hace todo el
  # mundo con este dato y conviene que el capítulo lo diga.
  log_zinc_media = r10(mean(log(meuse$zinc))),
  log_zinc_sd    = r10(sd(log(meuse$zinc))),
  asimetria_zinc = r10(mean(((meuse$zinc - mean(meuse$zinc)) / sd(meuse$zinc))^3)),
  # La correlación con la distancia al río: la razón por la que el
  # capítulo 9 acabará hablando de deriva externa.
  corr_dist_rio  = r10(cor(log(meuse$zinc), meuse$dist)),
  crs_epsg = 28992L
)

# --- B.4 Los tres, en Colombia ----------------------------------------
muni <- carga_municipios()
est  <- st_read("datos/procesado/colombia_estaciones_clima.gpkg", quiet = TRUE)
cole <- st_read("datos/procesado/bogota_colegios.gpkg", quiet = TRUE)
v_urb <- st_read("datos/procesado/bogota_ventana_urbana.gpkg", quiet = TRUE)
v_dc  <- st_read("datos/procesado/bogota_ventana_dc.gpkg", quiet = TRUE)

ancla(nrow(muni), 1122, "municipios del MGN (T0.4)")
ancla(nrow(est),   361, "estaciones del IDEAM (T0.4)")
ancla(nrow(cole), 2209, "sedes educativas de Bogotá (T0.4)")

area_km2 <- function(x) as.numeric(sum(st_area(x))) / 1e6
a_urb <- area_km2(v_urb)
n_urb <- sum(cole$en_urbana)

muni_ok <- muni[!is.na(muni$desercion), ]

D$colombia <- list(
  puntual = list(
    nombre = "Sedes educativas de Bogotá",
    fuente = "Secretaría de Educación del Distrito, v. 12.25 (CC BY-SA 4.0)",
    n = nrow(cole),
    n_urbana = as.integer(n_urb),
    area_urbana_km2 = r10(a_urb),
    lambda_urbana = r10(n_urb / a_urb),
    # La ventana entera de Bogotá D.C. incluye Sumapaz: rural y casi sin
    # colegios. El capítulo 4 lo desarrolla; aquí solo se enseña que el
    # mismo dato da dos intensidades.
    area_dc_km2 = r10(area_km2(v_dc)),
    n_dc = as.integer(sum(cole$en_ventana_dc)),
    lambda_dc = r10(sum(cole$en_ventana_dc) / area_km2(v_dc)),
    factor_lambda = r10((n_urb / a_urb) /
                        (sum(cole$en_ventana_dc) / area_km2(v_dc)))
  ),
  area = list(
    nombre = "Deserción escolar municipal",
    fuente = "Ministerio de Educación Nacional, 2024",
    n = nrow(muni), n_con_dato = nrow(muni_ok),
    media = r10(mean(muni_ok$desercion)),
    sd    = r10(sd(muni_ok$desercion)),
    minimo = r10(min(muni_ok$desercion)),
    maximo = r10(max(muni_ok$desercion))
  ),
  geo = list(
    nombre = "Temperatura media anual, estaciones del IDEAM 1991-2020",
    fuente = "IDEAM, vía datos.gov.co",
    n = nrow(est),
    t_media = r10(mean(est$t_media_anual)),
    t_sd    = r10(sd(est$t_media_anual)),
    t_min   = r10(min(est$t_media_anual)),
    t_max   = r10(max(est$t_media_anual)),
    alt_media = r10(mean(est$altitud_m)),
    alt_max   = r10(max(est$altitud_m)),
    corr_alt  = r10(cor(est$altitud_m, est$t_media_anual)),
    gradiente = r10(coef(lm(t_media_anual ~ altitud_m, data = est))[["altitud_m"]] * 1000)
  )
)

# =====================================================================
# C. MÓDULO 3 — La primera ley de Tobler
#
# «Todo está relacionado con todo lo demás, pero las cosas próximas están
# más relacionadas que las distantes» (Tobler 1970, p. 236). Aquí se
# CONTRASTA: correlograma por bandas de distancia sobre tres datos, más
# dos contraejemplos que no son retóricos sino medidos.
# =====================================================================
message("C · Tobler: el correlograma por bandas, y sus contraejemplos")

# I de Moran para una banda de distancia [d1, d2). Devuelve NA si la
# banda se queda sin pares: eso es información, no un fallo que ocultar.
moran_banda <- function(coords, z, d1, d2) {
  nb <- suppressWarnings(dnearneigh(coords, d1, d2))
  card_nb <- card(nb)
  if (all(card_nb == 0)) return(list(I = NA_real_, p = NA_real_,
                                     n_pares = 0L, grado = 0))
  lw <- nb2listw(nb, style = "W", zero.policy = TRUE)
  mt <- suppressWarnings(moran.test(z, lw, zero.policy = TRUE))
  list(I = r10(mt$estimate[["Moran I statistic"]]),
       p = r10(mt$p.value),
       n_pares = as.integer(sum(card_nb) / 2),
       grado = r10(mean(card_nb)))
}

correlograma <- function(coords, z, cortes, escala = 1) {
  out <- lapply(seq_len(length(cortes) - 1L), function(i) {
    r <- moran_banda(coords, z, cortes[i], cortes[i + 1])
    c(list(d1 = r10(cortes[i] / escala), d2 = r10(cortes[i + 1] / escala),
           centro = r10((cortes[i] + cortes[i + 1]) / 2 / escala)), r)
  })
  list(bandas = out,
       esperado = r10(-1 / (length(z) - 1)))
}

# --- C.1 meuse, en metros ---------------------------------------------
xy_meuse <- as.matrix(meuse[, c("x", "y")])
cor_meuse <- correlograma(xy_meuse, log(meuse$zinc),
                          c(0, 150, 300, 500, 750, 1100, 1600, 2400), escala = 1)

# --- C.2 IDEAM, en kilómetros -----------------------------------------
xy_est <- st_coordinates(est)
cor_ideam <- correlograma(xy_est, est$t_media_anual,
                          c(0, 25, 50, 100, 175, 300, 500, 800) * 1000, escala = 1000)

# --- C.3 CONTRAEJEMPLO 1: el mismo dato, permutado --------------------
# Destruir la posición y conservar los valores deja el correlograma plano
# alrededor de E[I] = -1/(n-1). Es la referencia contra la que se lee
# todo lo demás: sin ella, un I de 0,2 no significa nada.
set.seed(SEMILLA + 1L)
z_perm <- sample(est$t_media_anual)
cor_perm <- correlograma(xy_est, z_perm,
                         c(0, 25, 50, 100, 175, 300, 500, 800) * 1000, escala = 1000)

# --- C.4 CONTRAEJEMPLO 2: la autocorrelación que era una covariable ---
# La temperatura del IDEAM está fortísimamente autocorrelacionada. Pero
# quitarle la altitud —una variable que también es espacial— se lleva casi
# toda la estructura. Lo cercano se parecía porque estaba a la misma
# altura. Es la lección que el capítulo 8 (variable omitida espacial) y el
# 9 (deriva externa) desarrollan, y se ve ya con dos líneas de R.
res_alt <- residuals(lm(t_media_anual ~ altitud_m, data = est))
cor_resid <- correlograma(xy_est, res_alt,
                          c(0, 25, 50, 100, 175, 300, 500, 800) * 1000, escala = 1000)

# --- C.5 CONTRAEJEMPLO 3: un patrón regular ---------------------------
# En `cells` lo cercano NO se parece más: los puntos se repelen. Tobler
# describe una tendencia empírica dominante, no una ley física.
D$tobler <- list(
  meuse  = cor_meuse,
  ideam  = cor_ideam,
  permutado = cor_perm,
  residuos_altitud = cor_resid,
  # Los tres regímenes ordenados por Clark-Evans: el contraejemplo
  # puntual de la primera ley.
  clark_evans = list(
    redwood       = r10(D$puntual_canonico$redwood$clark_evans),
    japanesepines = r10(D$puntual_canonico$japanesepines$clark_evans),
    cells         = r10(D$puntual_canonico$cells$clark_evans)
  ),
  # Cuánta autocorrelación se lleva la altitud, en la banda más corta
  caida_por_altitud_pct = r10(
    100 * (1 - cor_resid$bandas[[1]]$I / cor_ideam$bandas[[1]]$I))
)

# =====================================================================
# D. MÓDULO 4 — Por qué se rompe la inferencia clásica
#
# El riesgo propio que el plan le asigna al capítulo: hay que MEDIR la
# subestimación del error estándar, no afirmarla. Dos frentes.
# =====================================================================
message("D · La subestimación del error estándar, medida")

# --- D.1 Monte Carlo sobre campo gaussiano ----------------------------
#
# Retícula k x k con correlación exponencial rho(h) = exp(-h/phi) sobre la
# distancia en pasos de retícula. Para cada phi se simulan NREP campos y
# se comparan tres cosas:
#   ee_ingenuo  s / sqrt(n)          — lo que devuelve cualquier software
#   ee_real     sd de las medias     — lo que de verdad varía la media
#   ee_exacto   sqrt(1'R1)/n         — la verdad teórica, para controlar
#                                       que la simulación no miente
# y la cobertura real de un IC nominal al 95 %.
K4 <- 16L; N4 <- K4^2; NREP <- 3000L
rej <- expand.grid(x = seq_len(K4), y = seq_len(K4))
DIST4 <- as.matrix(dist(rej))
PHIS <- c(0, 0.5, 1, 2, 4, 8, 16)

# El jitter de la diagonal existe solo para que la factorización de
# Cholesky no falle por redondeo con phi grande. 1e-9 sobre una varianza
# de 1 es invisible, y se declara aquí en vez de esconderse.
JITTER <- 1e-9
t_crit <- qt(0.975, N4 - 1)

mc <- lapply(PHIS, function(phi) {
  R <- if (phi <= 0) diag(N4) else exp(-DIST4 / phi)
  L <- t(chol(R + diag(JITTER, N4)))
  set.seed(SEMILLA + 100L + round(phi * 10))
  Z <- L %*% matrix(rnorm(N4 * NREP), N4, NREP)
  medias <- colMeans(Z)
  ees    <- apply(Z, 2, sd) / sqrt(N4)
  s2     <- (ees * sqrt(N4))^2          # la s^2 que ve el software
  cubre  <- abs(medias) <= t_crit * ees
  cob    <- mean(cubre)
  n_ef   <- N4^2 / sum(R)               # sin redondear: entra en s2_esperada
  list(phi = r10(phi),
       # Correlación entre vecinos inmediatos, que es como se lee phi
       rho_vecino = r10(if (phi <= 0) 0 else exp(-1 / phi)),
       # Y la de los vecinos en diagonal, a h = sqrt(2). Se publica porque
       # es lo que distingue «h en pasos de retícula» de «h = son vecinos o
       # no»: sin ella el lector no puede saber cuál de las dos se usó.
       rho_diagonal = r10(if (phi <= 0) 0 else exp(-sqrt(2) / phi)),
       ee_ingenuo = r10(mean(ees)),
       ee_real    = r10(sd(medias)),
       ee_exacto  = r10(sqrt(sum(R)) / N4),
       factor     = r10(sd(medias) / mean(ees)),
       cobertura  = r10(cob),
       # El error de Monte Carlo de la cobertura. Sin él, «94,7 %» y
       # «95,0 %» parecen distintos y no lo son.
       emc_cobertura = r10(sqrt(cob * (1 - cob) / NREP)),
       # n efectivo exacto: Var(Zbar) = sigma^2 * 1'R1 / n^2 = sigma^2/n_eff
       n_eff = r10(n_ef),
       # --- T2.2 · el puente de phi al factor, en sus dos tramos ---------
       # El módulo publicaba «la información se divide por unas 61.7»
       # calculando factor^2 en el ensamblador. Son DOS cocientes distintos
       # y el capítulo los llamaba igual, con 24 % de diferencia entre
       # ellos. Se publican los dos, con nombre propio:
       #
       #   efecto_diseno      Var(Zbar) real frente a sigma^2/n. Es n/n_eff,
       #                      y es el puente al módulo 5.
       #   inflacion_varianza cuánto se queda corta la varianza QUE EL
       #                      SOFTWARE DECLARA. Es factor^2, y es mayor
       #                      porque la propia s^2 se encoge con correlación.
       efecto_diseno      = r10(sum(R) / N4),
       inflacion_varianza = r10((sd(medias) / mean(ees))^2),
       # La identidad que explica la diferencia entre los dos de arriba, y
       # su medida, para no afirmarla: E[s^2] = sigma^2 (n/(n-1))(1-1/n_eff).
       s2_esperada = r10((N4 / (N4 - 1)) * (1 - 1 / n_ef)),
       s2_medida   = r10(mean(s2)))
})

# CONTROL DE LA SIMULACIÓN. Si el e.e. empírico no reprodujera el exacto,
# el Monte Carlo estaría mal montado y todo lo que sigue sería ruido bien
# presentado. Se comprueba antes de publicar nada.
for (m in mc) {
  err <- abs(m$ee_real - m$ee_exacto) / m$ee_exacto
  if (err > 0.06)
    stop(sprintf("el Monte Carlo no reproduce el e.e. exacto en phi = %.1f: %.5f vs %.5f",
                 m$phi, m$ee_real, m$ee_exacto))
}

# CONTROL de la identidad que T2.2 publica. El módulo 4 explica la brecha
# entre sus dos cocientes diciendo que s^2 se encoge, y eso es una
# afirmación con fórmula: hay que medirla antes de imprimirla. La
# tolerancia está MEDIDA, no elegida: el peor caso de los siete alcances es
# 2,03 % en phi = 8, así que 0,06 —la misma del control de arriba— deja
# holgura de tres veces sin volverse decorativa.
for (m in mc) {
  err <- abs(m$s2_medida - m$s2_esperada) / m$s2_esperada
  if (err > 0.06)
    stop(sprintf("E[s^2] no cuadra con (n/(n-1))(1-1/n_eff) en phi = %.1f: %.5f vs %.5f",
                 m$phi, m$s2_medida, m$s2_esperada))
}

D$inferencia <- list(
  n = N4, k = K4, nrep = NREP, jitter = JITTER,
  # La escala de h y la varianza marginal, declaradas para que el capítulo
  # pueda publicarlas. Sin ellas el módulo enseñaba rho(h) = e^(-h/phi) sin
  # decir en qué se mide h, y nadie podía llegar a e^(-1/4) por su cuenta.
  escala_h = "distancia euclídea entre centros de celda, medida en pasos de retícula",
  sigma = 1,
  t_critico = r10(t_crit),
  rejilla = mc,
  # Las dos cifras con las que cierra el módulo
  cobertura_independiente = r10(mc[[1]]$cobertura),
  cobertura_phi4 = r10(mc[[which(PHIS == 4)]]$cobertura),
  factor_phi4    = r10(mc[[which(PHIS == 4)]]$factor),
  n_eff_phi4     = r10(mc[[which(PHIS == 4)]]$n_eff),
  # T2.2 · los dos tramos del puente, para el phi que el módulo destaca
  efecto_diseno_phi4      = r10(mc[[which(PHIS == 4)]]$efecto_diseno),
  inflacion_varianza_phi4 = r10(mc[[which(PHIS == 4)]]$inflacion_varianza),
  s2_esperada_phi4        = r10(mc[[which(PHIS == 4)]]$s2_esperada)
)

# --- D.2 La réplica sobre dato real -----------------------------------
#
# El escéptico legítimo dice: «eso pasa porque tú lo simulaste así». Así
# que el mismo experimento sobre la deserción municipal real, donde la
# autocorrelación es la que es (I = 0,38 según T0.4) y nadie la eligió.
#
# Dos remuestreos que solo se diferencian en si respetan el espacio:
#   · i.i.d.       — se remuestrean municipios, uno a uno
#   · por bloques  — se remuestrean DEPARTAMENTOS enteros, con todos sus
#                    municipios dentro
# Los dos son bootstrap, así que la diferencia entre sus errores estándar
# no la puede explicar el método: la explica la dependencia espacial.
NBOOT <- 4000L
muni_ok$dpto <- substr(muni_ok$divipola, 1, 2)
bloques <- split(muni_ok$desercion, muni_ok$dpto)
n_muni <- nrow(muni_ok)

set.seed(SEMILLA + 200L)
boot_iid <- replicate(NBOOT, mean(sample(muni_ok$desercion, n_muni, replace = TRUE)))
set.seed(SEMILLA + 201L)
boot_blq <- replicate(NBOOT, {
  elegidos <- sample(seq_along(bloques), length(bloques), replace = TRUE)
  mean(unlist(bloques[elegidos], use.names = FALSE))
})

ee_iid <- sd(boot_iid)
ee_blq <- sd(boot_blq)

D$inferencia_real <- list(
  n_municipios = n_muni,
  n_departamentos = length(bloques),
  nboot = NBOOT,
  media = r10(mean(muni_ok$desercion)),
  ee_analitico = r10(sd(muni_ok$desercion) / sqrt(n_muni)),
  ee_bootstrap_iid = r10(ee_iid),
  ee_bootstrap_bloques = r10(ee_blq),
  factor = r10(ee_blq / ee_iid),
  # Leído al revés, el mismo número dice cuántos municipios independientes
  # hay de verdad. Es el puente al módulo 5.
  n_eff = r10(n_muni * (ee_iid / ee_blq)^2),
  pct_informacion = r10(100 * (ee_iid / ee_blq)^2),
  # El IC ingenuo y el que respeta el espacio, para poder enseñar los dos
  ic_iid = r10(mean(muni_ok$desercion) + c(-1, 1) * 1.959964 * ee_iid),
  ic_bloques = r10(mean(muni_ok$desercion) + c(-1, 1) * 1.959964 * ee_blq),
  ancho_iid = r10(2 * 1.959964 * ee_iid),
  ancho_bloques = r10(2 * 1.959964 * ee_blq)
)

# =====================================================================
# E. MÓDULO 5 — Tamaño de muestra efectivo
# =====================================================================
message("E · n efectivo")

# La fórmula cerrada bajo equicorrelación, que es la que se demuestra en
# el módulo: n_eff = n / (1 + (n-1) rho).
n_eff_equi <- function(n, rho) n / (1 + (n - 1) * rho)
RHOS <- c(0, 0.01, 0.02, 0.05, 0.1, 0.2, 0.3, 0.5, 0.8)
NN   <- c(25L, 50L, 100L, 250L, 500L, 1000L)

D$n_efectivo <- list(
  formula = "n_eff = n / (1 + (n-1) rho)",
  rhos = r10(RHOS), enes = NN,
  # Una rejilla n x rho: es el simulador del módulo
  rejilla = lapply(NN, function(n) list(
    n = n,
    n_eff = r10(vapply(RHOS, function(r) n_eff_equi(n, r), numeric(1))),
    pct   = r10(vapply(RHOS, function(r) 100 * n_eff_equi(n, r) / n, numeric(1))))),
  # El caso que más impresiona y que conviene tener publicado: con una
  # correlación pequeñísima, la mitad de la muestra se evapora.
  caso_n1000_rho001 = r10(n_eff_equi(1000, 0.01)),
  # El n_eff EXACTO del campo simulado, que no supone equicorrelación
  exacto_campo = lapply(mc, function(m) list(phi = m$phi, n_eff = m$n_eff,
                                             pct = r10(100 * m$n_eff / N4))),
  # Y los dos datos reales
  desercion_municipal = r10(D$inferencia_real$n_eff),
  desercion_n = n_muni,
  desercion_pct = r10(D$inferencia_real$pct_informacion)
)

# --- E.1 El rho del titular: el implícito y el estimado (T2.1) --------
#
# EL DEFECTO QUE CIERRA. El titular del módulo dice que 1 121 municipios
# informan como 64.52155, y no dice con qué rho. T1.1.b encontró por qué:
# NO HAY RHO. Ese 64.52155 es `n * (ee_iid/ee_blq)^2`, un cociente de dos
# remuestreos del módulo 4, y no pasa por la equicorrelación en ningún
# momento. Así que la pregunta no era «¿cuál es el rho escondido?» sino
# «¿cuál publicamos?», y se publican LOS DOS, porque decir en qué se
# separan es el contenido del módulo y no una nota al pie:
#
#   IMPLÍCITO   el rho que la equicorrelación NECESITARÍA para explicar la
#               inflación medida. Se despeja de n_eff = n/(1+(n-1)rho), así
#               que reproduce 64.52155 por construcción. No es una
#               estimación de nada: es una retro-transformación, y el
#               capítulo lo dice con esas palabras.
#   ESTIMADO    el rho medio entre pares, medido sobre el mapa con el MISMO
#               método del ejercicio 3 —correlograma por bandas, I de Moran
#               por banda, promediada con el número de pares de cada una—.
#               Éste sí es una estimación.
#
# Y no coinciden ni de lejos. Eso NO es un fallo del montaje: es la
# demostración de la advertencia que el capítulo ya hacía sin medirla —que
# la equicorrelación es falsa en el espacio—. La equicorrelación supone UN
# rho para todos los pares; en el mapa el rho decae con la distancia y
# llega a ponerse negativo, y como la inmensa mayoría de los pares son
# lejanos, el promedio se hunde hacia cero. El rho que haría falta para
# explicar la pérdida de información resulta ser varias veces el que se
# mide. La advertencia pasa de afirmación a cociente.
message("E.1 · el rho implícito y el rho estimado del módulo 5")

RHO_N     <- n_muni
RHO_N_EFF <- D$inferencia_real$n_eff
rho_implicito <- (RHO_N / RHO_N_EFF - 1) / (RHO_N - 1)

# Las MISMAS bandas del ejercicio 3, y a propósito: el estudiante que haga
# el ejercicio tiene que poder repetir aquí el gesto sin cambiar de método.
BANDAS_RHO <- c(0, 25, 50, 100, 175, 300, 500, 800) * 1000
xy_muni <- st_coordinates(suppressWarnings(st_point_on_surface(st_geometry(muni_ok))))
banda_rho <- lapply(seq_len(length(BANDAS_RHO) - 1L), function(i) {
  nb <- suppressWarnings(dnearneigh(xy_muni, BANDAS_RHO[i], BANDAS_RHO[i + 1]))
  pares <- sum(card(nb)) / 2
  I <- if (all(card(nb) == 0)) NA_real_ else
    suppressWarnings(moran.test(muni_ok$desercion,
                                nb2listw(nb, style = "W", zero.policy = TRUE),
                                zero.policy = TRUE))$estimate[["Moran I statistic"]]
  # Las islas DE ESTA BANDA, y no como curiosidad: son la única forma de que
  # el auditor en Python reproduzca esta I. `spdep::moran.test` con
  # `zero.policy = TRUE` toma n = unidades CON vecinos y `esda.Moran` toma
  # n = todas (la discrepancia `moran_islas` que el módulo 7 ya declara), así
  # que las dos convenciones se convierten exactamente una en otra:
  #     I_esda = I_spdep * n / (n - islas)
  # En la banda de 0 a 25 km casi la mitad de los municipios no tiene un solo
  # vecino, así que aquí eso no es un detalle de la cuarta cifra.
  list(d1 = as.integer(BANDAS_RHO[i] / 1000), d2 = as.integer(BANDAS_RHO[i + 1] / 1000),
       I = r10(I), pares = as.integer(pares),
       islas = as.integer(sum(card(nb) == 0)))
})
Is_rho <- vapply(banda_rho, function(b) b$I, numeric(1))
np_rho <- vapply(banda_rho, function(b) b$pares, numeric(1))
rho_estimado <- sum(Is_rho * np_rho, na.rm = TRUE) / sum(np_rho[!is.na(Is_rho)])

# El generador SE DETIENE si el implícito dejara de reproducir el titular:
# es una identidad algebraica, así que un fallo aquí significa que alguien
# cambió la fórmula y no el despeje.
if (abs(n_eff_equi(RHO_N, rho_implicito) - RHO_N_EFF) > 1e-6)
  stop(sprintf("el rho implícito no reproduce el n_eff del titular: %.5f vs %.5f",
               n_eff_equi(RHO_N, rho_implicito), RHO_N_EFF))

D$n_efectivo$rho_del_titular <- list(
  n = RHO_N,
  n_eff_publicado = r10(RHO_N_EFF),
  implicito = r10(rho_implicito),
  estimado  = r10(rho_estimado),
  # Qué n_eff daría el rho estimado si la equicorrelación valiera. La
  # distancia entre este número y el 64.52155 es lo que mide el error del
  # supuesto sobre este dato concreto.
  n_eff_con_estimado = r10(n_eff_equi(RHO_N, rho_estimado)),
  razon_rho   = r10(rho_implicito / rho_estimado),
  razon_n_eff = r10(n_eff_equi(RHO_N, rho_estimado) / RHO_N_EFF),
  # La primera banda es la cifra que un lector desprevenido citaría como
  # «la» correlación —vecinos contra vecinos—, y es dos órdenes de magnitud
  # mayor que el promedio sobre todos los pares. Publicarla evita la
  # objeción y de paso enseña de dónde sale la diferencia.
  I_primera_banda = r10(Is_rho[1]),
  n_bandas = length(banda_rho),
  pares_totales = as.integer(sum(np_rho)),
  pares_lejanos = as.integer(sum(np_rho[Is_rho < 0 & !is.na(Is_rho)])),
  bandas = banda_rho,
  metodo = paste("correlograma por bandas sobre los puntos interiores de los",
                 "municipios, I de Moran por banda y promedio ponderado por el",
                 "número de pares de cada una — el método del ejercicio 3")
)
message(sprintf("  · rho implícito %.7f (reproduce %.5f) · rho estimado %.7f (daría %.5f)",
                rho_implicito, RHO_N_EFF, rho_estimado,
                n_eff_equi(RHO_N, rho_estimado)))

# =====================================================================
# F. MÓDULO 6 — Estacionariedad, isotropía y una sola realización
#
# El problema fundamental: del proceso se observa UNA realización, y la
# estadística clásica supone muchas. Aquí se simulan las muchas para
# poder enseñar lo que nunca se ve.
# =====================================================================
message("F · Una realización frente a muchas")

K6 <- 16L; N6 <- K6^2; PHI6 <- 4; NREAL <- 1000L
R6 <- exp(-DIST4 / PHI6)
L6 <- t(chol(R6 + diag(JITTER, N6)))
set.seed(SEMILLA + 300L)
CAMPOS <- L6 %*% matrix(rnorm(N6 * NREAL), N6, NREAL)

medias_real <- colMeans(CAMPOS)
sds_real    <- apply(CAMPOS, 2, sd)

# El variograma empírico de CADA realización, sobre lags enteros de la
# retícula. La media del proceso es 0 y su varianza 1, así que el
# variograma teórico es gamma(h) = 1 - exp(-h/phi).
LAGS <- 1:8
pares_lag <- lapply(LAGS, function(h) which(abs(DIST4 - h) < 0.5 & upper.tri(DIST4),
                                            arr.ind = TRUE))
vario_de <- function(z) vapply(pares_lag, function(p)
  mean(0.5 * (z[p[, 1]] - z[p[, 2]])^2), numeric(1))
V <- vapply(seq_len(NREAL), function(i) vario_de(CAMPOS[, i]), numeric(length(LAGS)))

# CONTROL ENTRE MÓDULOS. El módulo 4 mide la cobertura de un IC al 95 %
# con phi = 4 sobre 3 000 réplicas; el módulo 6 mide, sobre otras 1 000
# realizaciones y con otra semilla, cuántas rechazarían la media
# verdadera. Son el mismo número visto del derecho y del revés, así que
# tienen que coincidir dentro del error de Monte Carlo conjunto. Si no
# coincidieran, uno de los dos montajes estaría mal y el capítulo
# publicaría dos cifras contradictorias del mismo fenómeno.
p_rech <- mean(abs(medias_real) > t_crit * (sds_real / sqrt(N6)))
p_mod4 <- 1 - mc[[which(PHIS == PHI6)]]$cobertura
emc_conjunto <- sqrt(p_rech * (1 - p_rech) / NREAL +
                     p_mod4 * (1 - p_mod4) / NREP)
if (abs(p_rech - p_mod4) > 3 * emc_conjunto)
  stop(sprintf(paste("los módulos 4 y 6 no cuadran: rechazo %.4f (n=%d) frente a",
                     "%.4f (n=%d); %.1f errores de Monte Carlo"),
               p_rech, NREAL, p_mod4, NREP, abs(p_rech - p_mod4) / emc_conjunto))

D$una_realizacion <- list(
  n = N6, k = K6, phi = PHI6, n_realizaciones = NREAL,
  # La media del proceso es 0 por construcción. Lo que se mide es cuánto
  # se aleja de 0 la media espacial de UNA realización.
  media_del_proceso = 0,
  media_de_las_medias = r10(mean(medias_real)),
  sd_de_las_medias    = r10(sd(medias_real)),
  media_min = r10(min(medias_real)), media_max = r10(max(medias_real)),
  # Cuántas de las 200 realizaciones darían, leídas SOLAS y con el e.e.
  # ingenuo, un contraste significativo contra la media verdadera —que es
  # 0 y la conozco porque generé el proceso—. El umbral no es arbitrario:
  # es el mismo IC al 95 % del módulo 4, y por eso este número cierra el
  # círculo entre los dos módulos.
  pct_rechaza_ingenuo = r10(100 * p_rech),
  emc_rechaza = r10(100 * sqrt(p_rech * (1 - p_rech) / NREAL)),
  pct_esperado_si_valiera = 5,
  # El mismo número que el módulo 4 mide como cobertura, visto del
  # derecho. Se publican los dos y se declara que tienen que cuadrar.
  pct_rechaza_modulo4 = r10(100 * (1 - mc[[which(PHIS == PHI6)]]$cobertura)),
  discrepancia_con_modulo4 = r10(abs(100 * p_rech -
    100 * (1 - mc[[which(PHIS == PHI6)]]$cobertura))),
  sd_espacial_media = r10(mean(sds_real)),
  sd_espacial_min = r10(min(sds_real)), sd_espacial_max = r10(max(sds_real)),
  # Las 12 primeras medias, para el simulador
  medias_muestra = r10(medias_real[1:12]),
  variograma = list(
    lags = LAGS,
    teorico = r10(1 - exp(-LAGS / PHI6)),
    media   = r10(rowMeans(V)),
    q05     = r10(apply(V, 1, quantile, 0.05)),
    q95     = r10(apply(V, 1, quantile, 0.95))),
  # El ancho relativo de la banda al lag 4: cuánto puede desviarse el
  # variograma de UNA realización del del proceso que lo generó.
  banda_rel_lag4 = r10((quantile(V[4, ], 0.95) - quantile(V[4, ], 0.05)) /
                         (1 - exp(-4 / PHI6)))
)

# --- F.1 Las tres realizaciones que el capítulo ENSEÑA -----------------
#
# T1.3. Aquí y no en la sección M, que es donde vivían, porque el defecto
# que esta tarea cierra nacía justo de esa separación: los tres mapas
# salían de una simulación APARTE —28 x 28, semilla +700— mientras la
# curva, la banda y todas las cifras del módulo salían de este lote de
# 16 x 16. El variograma dibujado no era el de ninguno de los tres mapas,
# y la intro decía «16 x 16» sobre un mapa de 28 x 28.
#
# Ahora son las TRES PRIMERAS de las NREAL, sin elegir, y el capítulo lo
# declara: la tesis del módulo —tres tiradas del mismo proceso no se
# parecen— pierde toda su fuerza si las tres están escogidas.
#
# `media` y `sd` salen de `medias_real`/`sds_real`, calculadas arriba
# sobre la matriz entera; el mapa recalculará las suyas con mean(z)/sd(z)
# sobre su propio vector. Dos rutas para la misma cifra, a propósito: es
# lo único que puede delatar un emparejamiento torcido entre las dos
# listas, y comparar una lista consigo misma no delata nada (T1.2.d).
N_VISTAS <- 3L
stopifnot(N_VISTAS <= NREAL, N_VISTAS <= length(D$una_realizacion$medias_muestra))

# Cuánto se aparta del proceso el variograma de cada una, en el peor lag
# y en el lag 4 —el que el texto usa para el ancho de banda—. Convierte
# la tesis del módulo en una medida en vez de una afirmación.
TEO6 <- 1 - exp(-LAGS / PHI6)
D$realizaciones_vistas <- lapply(seq_len(N_VISTAS), function(i) list(
  id = i,
  media = r10(medias_real[i]),
  sd    = r10(sds_real[i]),
  variograma = r10(V[, i]),
  desvio_rel_max  = r10(max(abs(V[, i] - TEO6) / TEO6)),
  lag_desvio_max  = LAGS[which.max(abs(V[, i] - TEO6) / TEO6)],
  desvio_rel_lag4 = r10(abs(V[4, i] - TEO6[4]) / TEO6[4]),
  # Cuántos de los 8 lags se salen de la banda del 5-95 %. Puede ser 0 y
  # no es un fallo: una realización dentro de la banda en los ocho lags
  # sigue apartándose del teórico, que es lo que el módulo enseña. Se
  # publica el número, no una promesa sobre él.
  lags_fuera_banda = sum(V[, i] < apply(V, 1, quantile, 0.05) |
                         V[, i] > apply(V, 1, quantile, 0.95))
))
message(sprintf("  · las %d realizaciones vistas: medias %s · desvío rel. máx. %s",
                N_VISTAS,
                paste(sprintf("%.5f", medias_real[seq_len(N_VISTAS)]), collapse = ", "),
                paste(sprintf("%.5f", vapply(D$realizaciones_vistas,
                                             function(r) r$desvio_rel_max, numeric(1))),
                      collapse = ", ")))

# =====================================================================
# G. MÓDULO 7 — Escala, soporte y agregación (la pincelada del MAUP)
# =====================================================================
message("G · El efecto escala, con dato colombiano y con dato simulado")

# --- G.1 El dato real: municipio -> departamento ----------------------
nb_mun <- suppressWarnings(poly2nb(muni_ok, queen = TRUE))
lw_mun <- nb2listw(nb_mun, style = "W", zero.policy = TRUE)
mi_mun <- moran.test(muni_ok$desercion, lw_mun, zero.policy = TRUE)

dep <- st_read("datos/procesado/colombia_adm1.gpkg", quiet = TRUE)
agr <- aggregate(muni_ok[, c("desercion", "cobertura")],
                 by = list(dpto = muni_ok$dpto),
                 FUN = function(v) mean(v, na.rm = TRUE))
agr <- st_drop_geometry(agr)

# La unión departamento-polígono va por geometría, no por nombre: cada
# polígono se etiqueta con el prefijo DIVIPOLA mayoritario de los
# municipios cuyo punto interior cae dentro. Una llave, no una cadena
# parecida (la lección de A.7).
centro <- suppressWarnings(st_point_on_surface(st_geometry(muni_ok)))
i_dep  <- st_intersects(centro, dep)
muni_ok$dep_idx <- vapply(i_dep, function(z) if (length(z)) z[1] else NA_integer_, 1L)
tab <- table(muni_ok$dep_idx, muni_ok$dpto)
dep$dpto <- ifelse(rowSums(tab) > 0,
                   colnames(tab)[max.col(tab, ties.method = "first")], NA)
dep$desercion <- agr$desercion[match(dep$dpto, agr$dpto)]
dep$cobertura <- agr$cobertura[match(dep$dpto, agr$dpto)]
dep_ok <- dep[!is.na(dep$desercion), ]

nb_dep <- suppressWarnings(poly2nb(dep_ok, queen = TRUE))
lw_dep <- nb2listw(nb_dep, style = "W", zero.policy = TRUE)
mi_dep <- moran.test(dep_ok$desercion, lw_dep, zero.policy = TRUE)

# ---------------------------------------------------------------------
# LA I DE MORAN NO VALE LO MISMO EN R QUE EN PYTHON, Y LA CULPA ES DE LAS
# ISLAS. Encontrado al auditar T1.1 con geopandas + esda.
#
# Con `zero.policy = TRUE`, `spdep::moran.test` calcula
#     I = (n / S0) * sum(z Wz) / sum(z^2)
# tomando **n = número de unidades CON vecinos**, no el número de
# unidades. `esda.Moran` toma n = todas. Sobre los 1 121 municipios, con
# 2 islas, eso son 1 119 frente a 1 121 y la I cambia en la cuarta cifra.
#
# Ninguna de las dos está mal: son dos convenios sobre qué hacer con una
# unidad que no tiene vecinos. Pero comparar 0,3809 con 0,3816 sin saber
# esto parece un error de cálculo, y no lo es. Se publican LOS DOS y se
# declara la causa, igual que se hizo con los cuantiles de A.2. Es además
# el caso trabajado que el módulo 9 del capítulo 6 (`zero.policy`) tenía
# encargado, y sale del propio dato.
I_con_n_total <- function(x, lw) {
  z <- x - mean(x)
  n <- length(z)
  S0 <- sum(unlist(lw$weights))
  (n / S0) * sum(z * lag.listw(lw, z, zero.policy = TRUE)) / sum(z^2)
}

# ---------------------------------------------------------------------
# G.1b · AGREGAR: el predicado, la conservación y la alternativa
#
# El módulo 7 se titula «Escala, soporte y agregación» y hasta T2.3 medía
# solo la escala. Esto le pone cifra a la agregación, siguiendo el
# capítulo 5 de Pebesma y Bivand («Attributes and Support»).
#
# Van dos casos y no uno a propósito:
#
#   · `nc` reproduce el ejemplo del libro y es el que ENSEÑA el mecanismo,
#     porque el error se ve a simple vista: sumar un conteo sobre unas
#     áreas que no son unión de las originales, emparejando por
#     `intersects`, cuenta varias veces el mismo condado. El total deja de
#     conservarse y se infla casi por cuatro.
#
#   · Colombia lo aplica AL PROPIO CAPÍTULO, que es lo que le da filo: la
#     deserción departamental que este material publica es una media NO
#     ponderada de las tasas municipales. Es una elección legítima, pero
#     es una elección, y aquí se mide lo que cuesta — incluida la I de
#     Moran del titular del módulo, que cambia sin que se mueva ni una
#     frontera.
# ---------------------------------------------------------------------
nc_ag  <- st_transform(nc, 2264)          # NC State Plane, como el libro
rej_nc <- st_sf(geom = st_make_grid(nc_ag))
# El predicado por defecto de `aggregate.sf` es `st_intersects`: cada
# condado que TOQUE un rectángulo aporta su conteo entero a ese
# rectángulo, y los condados tocan varios.
sid_rect <- sum(aggregate(nc_ag["SID74"], rej_nc, sum)$SID74, na.rm = TRUE)
# La alternativa correcta: repartir por área. Con `extensive = TRUE` el
# total SE CONSERVA, y esa conservación es la comprobación, no un adorno.
sid_aw <- sum(suppressWarnings(
  st_interpolate_aw(nc_ag["SID74"], rej_nc, extensive = TRUE))$SID74,
  na.rm = TRUE)
ancla(sid_rect, 2621, "SIDS sumados sobre los rectángulos (Pebesma y Bivand, §5.2)")
ancla(sid_aw, sum(nc$SID74), "y el reparto por área devuelve el total exacto")

# --- El caso que el mapa del módulo 7 enseña (T2.4) -------------------
#
# Hasta aquí el módulo DECÍA el mecanismo —«un condado toca varios
# rectángulos y aporta su conteo entero a todos»— y no lo MOSTRABA. Eso se
# entiende de golpe con una imagen y a medias con un párrafo, así que el
# módulo estrena un mapa: la rejilla encima de los condados, con uno
# resaltado y las celdas que toca. De aquí salen sus cifras.
#
# EL CONDADO NO SE ELIGE A OJO NI «PORQUE SE VE BIEN». El exceso que aporta
# cada condado es (k_i - 1) · SID74_i —las veces que se le cuenta de más,
# por su conteo—, y el mapa señala al que MÁS infla el total. Es un criterio
# que se puede escribir, recalcular y desmentir; «el que se veía bien» no.
#
# Y trae de regalo la identidad que ata el caso al titular:
#
#     sum_i (k_i - 1) · SID74_i  =  2 621 - 667
#
# o sea, la inflación entera es la suma de los excesos condado a condado.
# Si eso fallara, el predicado no estaría haciendo lo que el módulo dice que
# hace, y el mapa estaría ilustrando otra cosa. Se comprueba, no se supone.
toca_nc  <- st_intersects(nc_ag, rej_nc)
celdas_x_condado <- lengths(toca_nc)
exceso_x_condado <- (celdas_x_condado - 1L) * nc_ag$SID74
stopifnot(sum(exceso_x_condado) == sid_rect - sum(nc$SID74))
i_caso <- which.max(exceso_x_condado)
# Un empate dejaría el mapa a merced del orden del shapefile: el criterio
# tiene que señalar a UNO, o no es un criterio.
stopifnot(sum(exceso_x_condado == exceso_x_condado[i_caso]) == 1L)

# El reparto por área DEL MISMO condado, celda a celda: es el segundo
# estado del mapa y el contraste que convierte la cifra en lección. Con
# «se tocan» las cinco celdas reciben las 44 muertes enteras; repartiendo,
# cada una recibe su fracción y las cinco suman 44.
g_caso   <- st_geometry(nc_ag)[i_caso]
a_caso   <- as.numeric(st_area(g_caso))
cel_caso <- toca_nc[[i_caso]]
frac_caso <- vapply(cel_caso, function(j) {
  z <- suppressWarnings(st_intersection(g_caso, st_geometry(rej_nc)[j]))
  if (length(z) == 0) 0 else sum(as.numeric(st_area(z)))
}, numeric(1)) / a_caso
# Las fracciones tienen que sumar 1: el condado está entero dentro de las
# celdas que toca, por definición de tocar. Si no sumaran, el segundo
# estado del mapa estaría repartiendo un condado que no es éste.
stopifnot(abs(sum(frac_caso) - 1) < 1e-9)

# Fila y columna de cada celda, contadas desde el SUROESTE de la caja. Se
# derivan de la posición del centroide y no del índice de `st_make_grid`,
# para no depender de un orden de recorrido que es un detalle de sf: el
# auditor las rehace en Python con esta misma definición.
bb_rej  <- as.numeric(st_bbox(rej_nc))
paso_x  <- (bb_rej[3] - bb_rej[1]) / 10
paso_y  <- (bb_rej[4] - bb_rej[2]) / 10
ctr_cel <- st_coordinates(st_centroid(st_geometry(rej_nc)[cel_caso]))
col_cel <- as.integer(pmin(10, floor((ctr_cel[, 1] - bb_rej[1]) / paso_x) + 1))
fil_cel <- as.integer(pmin(10, floor((ctr_cel[, 2] - bb_rej[2]) / paso_y) + 1))

# La misma variable departamental por la OTRA regla: media ponderada por
# área. `extensive = FALSE` porque la deserción es una tasa, no un conteo.
dep_aw <- suppressWarnings(
  st_interpolate_aw(muni_ok["desercion"], dep, extensive = FALSE))
dep$desercion_area <- dep_aw$desercion
dep_dos <- dep[!is.na(dep$desercion) & !is.na(dep$desercion_area), ]
nb_dos  <- suppressWarnings(poly2nb(dep_dos, queen = TRUE))
lw_dos  <- nb2listw(nb_dos, style = "W", zero.policy = TRUE)
mi_area <- moran.test(dep_dos$desercion_area, lw_dos, zero.policy = TRUE)

D$agregacion_soporte <- list(
  nc = list(
    total_condados    = as.integer(sum(nc$SID74)),
    n_celdas          = as.integer(nrow(rej_nc)),
    total_rectangulos = as.integer(sid_rect),
    inflacion_pct     = r10(100 * (sid_rect / sum(nc$SID74) - 1)),
    total_por_area    = r10(sid_aw),
    # El caso que el mapa señala. `indice` es 1-basado porque es el que
    # `geo_poligonos(resaltado = )` va a recibir, y `celdas_tocadas` son los
    # índices 1-basados dentro de las 100 celdas de la rejilla: el mapa los
    # usa como `lineas_resaltadas`, y el ensamblador comprueba que las dos
    # listas sean la misma. Sin esa comprobación, el mapa podría resaltar
    # unas celdas y la tabla hablar de otras, y saldría bien dibujado.
    condado_caso = list(
      nombre           = as.character(nc$NAME[i_caso]),
      indice           = as.integer(i_caso),
      sids             = as.integer(nc_ag$SID74[i_caso]),
      n_celdas_toca    = as.integer(celdas_x_condado[i_caso]),
      celdas_tocadas   = as.integer(cel_caso),
      aporte_predicado = as.integer(celdas_x_condado[i_caso] * nc_ag$SID74[i_caso]),
      exceso           = as.integer(exceso_x_condado[i_caso]),
      exceso_total     = as.integer(sum(exceso_x_condado)),
      pct_del_exceso   = r10(100 * exceso_x_condado[i_caso] / sum(exceso_x_condado)),
      # La celda del ROCE: la que menos área del condado recibe. Es la que
      # más enseña, porque «intersecta» es cierto ahí igual que en las
      # otras cuatro y le entrega el conteo entero.
      roce_pct         = r10(100 * min(frac_caso)),
      roce_aporte_area = r10(nc_ag$SID74[i_caso] * min(frac_caso)),
      # El 100 del pie de la tabla de respaldo. Sale de aquí y no escrito a
      # mano en el navegador porque es la afirmación central del segundo
      # estado del mapa —que el reparto cubre el condado y nada más— y una
      # afirmación central no se cablea: se calcula y se audita (D10).
      fraccion_total_pct = r10(100 * sum(frac_caso)),
      reparto = lapply(seq_along(cel_caso), function(m) list(
        celda        = as.integer(cel_caso[m]),
        fila         = fil_cel[m],
        columna      = col_cel[m],
        fraccion_pct = r10(100 * frac_caso[m]),
        aporte_area  = r10(nc_ag$SID74[i_caso] * frac_caso[m])))
    )
  ),
  colombia = list(
    n_departamentos    = nrow(dep_dos),
    dif_media_abs      = r10(mean(abs(dep_dos$desercion - dep_dos$desercion_area))),
    dif_max            = r10(max(abs(dep_dos$desercion - dep_dos$desercion_area))),
    cor_reglas         = r10(cor(dep_dos$desercion, dep_dos$desercion_area)),
    # La I sin ponderar TIENE que coincidir con `escala$moran_departamental`:
    # si no coincide, es que este bloque no está reproduciendo la misma
    # agregación que publica el capítulo, y entonces la comparación no
    # compara nada. El auditor lo exige.
    moran_sin_ponderar = r10(moran.test(dep_dos$desercion, lw_dos,
                                        zero.policy = TRUE)$estimate[[1]]),
    moran_por_area     = r10(mi_area$estimate[[1]]),
    p_por_area         = r10(mi_area$p.value)
  )
)

D$escala <- list(
  n_municipal = nrow(muni_ok),
  moran_municipal = r10(mi_mun$estimate[["Moran I statistic"]]),
  p_municipal = r10(mi_mun$p.value),
  islas_municipal = as.integer(sum(card(nb_mun) == 0)),
  subgrafos_municipal = as.integer(n.comp.nb(nb_mun)$nc),
  grado_municipal = r10(mean(card(nb_mun))),
  n_departamental = nrow(dep_ok),
  moran_departamental = r10(mi_dep$estimate[["Moran I statistic"]]),
  p_departamental = r10(mi_dep$p.value),
  grado_departamental = r10(mean(card(nb_dep))),
  islas_departamental = as.integer(sum(card(nb_dep) == 0)),
  caida_pct = r10(100 * (1 - mi_dep$estimate[["Moran I statistic"]] /
                           mi_mun$estimate[["Moran I statistic"]])),
  # El otro convenio, el que usa esda. Ver D$discrepancias.
  moran_municipal_n_total = r10(I_con_n_total(muni_ok$desercion, lw_mun)),
  moran_departamental_n_total = r10(I_con_n_total(dep_ok$desercion, lw_dep))
)

# ---------------------------------------------------------------------
# Las discrepancias DECLARADAS entre R y Python.
#
# Que exista esta lista es la mitad del asunto. La otra mitad es que
# `audita_cap1.py` la lee: si el auditor encuentra una diferencia que
# está aquí, con su causa y sus dos valores, la da por material
# didáctico; si encuentra una que no está, falla. Una discrepancia sin
# explicar y una explicada se parecen mucho sobre un informe, y
# confundirlas es lo que convierte un auditor en un adorno (A.2).
# ---------------------------------------------------------------------
D$discrepancias <- list(
  list(
    id = "moran_islas",
    que = "El I de Moran de la deserción municipal",
    valor_r = r10(mi_mun$estimate[["Moran I statistic"]]),
    valor_python = r10(I_con_n_total(muni_ok$desercion, lw_mun)),
    diferencia = r10(abs(I_con_n_total(muni_ok$desercion, lw_mun) -
                         mi_mun$estimate[["Moran I statistic"]])),
    causa = paste(
      "Con zero.policy = TRUE, spdep::moran.test toma n = unidades CON",
      "vecinos (1 119 de 1 121, porque hay 2 islas) mientras esda.Moran",
      "toma n = todas las unidades. Mismo grafo, misma fórmula, dos",
      "convenios sobre qué es una unidad sin vecinos."),
    va_a = "capítulo 6, módulo 9 (islas y zero.policy)"
  ),
  list(
    id = "moran_islas_dep",
    que = "El I de Moran de la deserción departamental",
    valor_r = r10(mi_dep$estimate[["Moran I statistic"]]),
    valor_python = r10(I_con_n_total(dep_ok$desercion, lw_dep)),
    diferencia = r10(abs(I_con_n_total(dep_ok$desercion, lw_dep) -
                         mi_dep$estimate[["Moran I statistic"]])),
    causa = paste(
      "El mismo convenio, a escala departamental: San Andrés queda como",
      "isla de la contigüidad y los dos programas la cuentan distinto.",
      "Con 33 unidades la diferencia relativa es mayor que con 1 121."),
    va_a = "capítulo 6, módulo 9 (islas y zero.policy)"
  ),
  list(
    id = "tipo_geometria_nc",
    que = "El tipo de geometría de los 100 condados de nc.shp",
    valor_r = 100,
    valor_python = as.integer(sum(vapply(st_geometry(nc0), length, integer(1)) > 1)),
    diferencia = r10(100 - sum(vapply(st_geometry(nc0), length, integer(1)) > 1)),
    causa = paste(
      "sf informa MULTIPOLYGON para los 100 porque ése es el tipo",
      "declarado de la CAPA; shapely mira cada geometría y solo 6",
      "condados tienen más de una parte, así que geopandas informa",
      "Polygon para los otros 94. La geometría es idéntica: lo que",
      "difiere es qué se considera el tipo de un rasgo."),
    va_a = "capítulo 1, módulo 9 (anatomía de un objeto sf)"
  )
)

# --- G.1b El otro efecto escala: la correlación entre DOS variables ---
#
# Gehlke y Biehl (1934) observaron que la correlación entre dos variables
# cambia al agregar las unidades. La primera versión de esto publicaba UN
# par —deserción y cobertura— y decía «sube un 345 %». Era falso de una
# forma peligrosa: r municipal = 0.0211 y r departamental = -0.0940, o
# sea dos valores de ruido de signos opuestos, y el «345 %» era el
# cociente entre ellos. Exactamente el fallo de A.8, donde el estrato
# municipal dio -0.0577 y parecía Robinson (1950).
#
# Se corrige del modo que aquel anexo dejó escrito: en vez de una cifra
# sola, **el barrido entero**. Ocho variables, todos los pares con una
# correlación municipal apreciable, a las dos escalas. Y el resultado es
# mejor material que el que buscaba: agregar cambia la correlación, pero
# NO siempre en la misma dirección. Unos pares suben, otros bajan y uno
# invierte el signo.
VARS_ESCALA <- c("desercion", "cobertura", "s11_punt_medio",
                 "s11_pct_internet", "s11_cob_internet",
                 "s11_edu_madre_media", "s11_pct_oficial", "s11_estrato_medio")
ETIQ_ESCALA <- c(desercion = "Deserción escolar (%)",
                 cobertura = "Cobertura neta (%)",
                 s11_punt_medio = "Puntaje medio Saber 11",
                 s11_pct_internet = "Hogares con internet (%)",
                 s11_cob_internet = "Cobertura del dato de internet (%)",
                 s11_edu_madre_media = "Educación de la madre (escala ordinal)",
                 s11_pct_oficial = "Colegios oficiales (%)",
                 s11_estrato_medio = "Estrato medio")

d_mun <- st_drop_geometry(muni)
d_mun$dpto <- substr(d_mun$divipola, 1, 2)
d_dep <- aggregate(d_mun[, VARS_ESCALA], by = list(dpto = d_mun$dpto),
                   FUN = function(v) mean(v, na.rm = TRUE))

pares <- list()
for (i in seq_along(VARS_ESCALA)) for (j in seq_along(VARS_ESCALA)) if (i < j) {
  a_ <- VARS_ESCALA[i]; b_ <- VARS_ESCALA[j]
  rm_ <- cor(d_mun[[a_]], d_mun[[b_]], use = "complete.obs")
  rd_ <- cor(d_dep[[a_]], d_dep[[b_]], use = "complete.obs")
  # Solo los pares con señal municipal apreciable. Comparar dos ruidos
  # es lo que produjo el 345 % y no se vuelve a hacer.
  if (abs(rm_) <= 0.20) next
  pares[[length(pares) + 1L]] <- list(
    a = a_, b = b_, a_etiqueta = unname(ETIQ_ESCALA[a_]),
    b_etiqueta = unname(ETIQ_ESCALA[b_]),
    r_municipal = r10(rm_), r_departamental = r10(rd_),
    razon = r10(rd_ / rm_),
    cambio_pct = r10(100 * (rd_ / rm_ - 1)),
    invierte_signo = sign(rm_) != sign(rd_))
}

# El par principal, y su BARRIDO POR UMBRAL. Es la comprobación que salvó
# T0.4: una correlación municipal calculada sobre unidades de dos
# estudiantes no es una correlación, es ruido con nombre. Si la cifra no
# sobrevive al barrido, no se publica.
UMBRALES <- c(1L, 10L, 30L, 100L, 300L)
barrido <- lapply(UMBRALES, function(u) {
  sub <- d_mun[!is.na(d_mun$s11_n) & d_mun$s11_n >= u, ]
  list(umbral = u, n = nrow(sub),
       r = r10(cor(sub$s11_punt_medio, sub$s11_pct_internet,
                   use = "complete.obs")))
})

D$escala_correlacion <- list(
  n_variables = length(VARS_ESCALA),
  n_pares = length(pares),
  n_suben = sum(vapply(pares, function(p) abs(p$r_departamental) >
                         abs(p$r_municipal), logical(1))),
  n_bajan = sum(vapply(pares, function(p) abs(p$r_departamental) <=
                         abs(p$r_municipal), logical(1))),
  n_invierten = sum(vapply(pares, function(p) p$invierte_signo, logical(1))),
  pares = pares,
  principal = list(
    a = "s11_punt_medio", b = "s11_pct_internet",
    r_municipal = r10(cor(d_mun$s11_punt_medio, d_mun$s11_pct_internet,
                          use = "complete.obs")),
    r_departamental = r10(cor(d_dep$s11_punt_medio, d_dep$s11_pct_internet,
                              use = "complete.obs")),
    barrido = barrido,
    # DOS LECTURAS DEL BARRIDO, y conviene no confundirlas.
    #
    # 1) ¿La cifra municipal la ponen los municipios diminutos? NO: entre
    #    todos (n = 1 113) y los de al menos 30 estudiantes (n = 1 097) la
    #    correlación se mueve una centésima. Ésta sí es la comprobación de
    #    estabilidad que A.8 dejó como obligatoria, y la pasa.
    diferencia_umbral_30 = r10(abs(barrido[[3]]$r - barrido[[1]]$r)),
    estable_ante_unidades_pequenas = abs(barrido[[3]]$r - barrido[[1]]$r) < 0.05,
    # 2) Por encima de n >= 100 el barrido deja de ser un control y pasa a
    #    ser OTRA MEDIDA DEL MISMO EFECTO: quedarse solo con los
    #    municipios grandes es una forma de agregar, y la correlación sube
    #    igual que al pasar a departamentos. Sube de forma monótona, que
    #    es lo que se espera si el mecanismo es el que el módulo dice.
    monotono = all(diff(vapply(barrido, function(b) b$r, numeric(1))) >= 0),
    recorrido_barrido = r10(diff(range(vapply(barrido, function(b) b$r, numeric(1)))))
  ),
  # El caso de aviso, declarado y no escondido: el ESTRATO invierte el
  # signo al agregar. T0.4 ya lo había congelado como caso de aviso
  # porque su ausencia no es inocente —corr(cobertura del estrato,
  # puntaje) = +0,5952—, así que aquí se enseña como advertencia
  # metodológica y no como fenómeno.
  caso_aviso = list(
    a = "s11_pct_internet", b = "s11_estrato_medio",
    r_municipal = r10(cor(d_mun$s11_pct_internet, d_mun$s11_estrato_medio,
                          use = "complete.obs")),
    r_departamental = r10(cor(d_dep$s11_pct_internet, d_dep$s11_estrato_medio,
                              use = "complete.obs")),
    nota = paste("El estrato quedó congelado en T0.4 como caso de aviso:",
                 "su ausencia no es aleatoria. Se muestra como advertencia,",
                 "no como resultado.")
  )
)

# --- G.2 El dato simulado: agregación controlada ----------------------
#
# Aquí no hay nada que discutir sobre el dato: lo genero yo y sé de dónde
# sale cada pieza. Dos variables sobre una retícula 64 x 64:
#
#     a = s * u + sqrt(1-s^2) * e_a
#     b = s * u + sqrt(1-s^2) * e_b
#
# donde `u` es un campo SUAVE (rango 6 pasos de retícula), compartido por
# las dos, y `e_a`, `e_b` son RUIDO BLANCO independiente. La correlación
# de partida vale s^2.
#
# EL MECANISMO, que es lo que el módulo tiene que explicar: al promediar
# celdas vecinas, el ruido blanco se cancela —su media sobre b^2 celdas
# tiene varianza 1/b^2— mientras que la señal suave sobrevive casi
# entera, porque las celdas vecinas comparten su valor. Agregar no añade
# información: **retira ruido de forma selectiva**, y por eso la
# correlación sube.
#
# La primera versión de esto construía `e_a` y `e_b` también como campos
# suaves, y entonces no pasaba nada (0.3802 -> 0.3595): el promediado se
# llevaba señal y ruido por igual. Que el ruido NO tenga estructura
# espacial no es un detalle del montaje, es la condición del fenómeno.
K7 <- 64L; N7 <- K7^2
rej7 <- expand.grid(x = seq_len(K7), y = seq_len(K7))
D7 <- as.matrix(dist(rej7))
RANGO7 <- 6
L7 <- t(chol(exp(-D7 / RANGO7) + diag(1e-8, N7)))
set.seed(SEMILLA + 400L)
u <- as.numeric(L7 %*% rnorm(N7))
u <- (u - mean(u)) / sd(u)
S7 <- 0.6                       # corr de partida = S7^2 = 0.36
a <- S7 * u + sqrt(1 - S7^2) * rnorm(N7)
b <- S7 * u + sqrt(1 - S7^2) * rnorm(N7)

agrega <- function(v, k, b_) {
  m <- matrix(v, k, k)
  kk <- k %/% b_
  as.numeric(vapply(seq_len(kk), function(j)
    vapply(seq_len(kk), function(i)
      mean(m[((i - 1) * b_ + 1):(i * b_), ((j - 1) * b_ + 1):(j * b_)]),
      numeric(1)), numeric(kk)))
}
BLOQUES <- c(1L, 2L, 4L, 8L, 16L)
niveles <- lapply(BLOQUES, function(b_) {
  aa <- agrega(a, K7, b_); bb <- agrega(b, K7, b_)
  list(bloque = b_, n_unidades = length(aa),
       celdas_por_unidad = as.integer(b_^2),
       corr = r10(cor(aa, bb)))
})
# CONTROL: si el efecto no aparece, el montaje está mal y publicarlo
# sería enseñar como fenómeno lo que es un error de construcción. La
# comprobación va aquí, no en la cabeza de nadie.
if (niveles[[length(niveles)]]$corr <= niveles[[1]]$corr + 0.1)
  stop(sprintf("la agregación no produce el efecto escala: %.4f -> %.4f",
               niveles[[1]]$corr, niveles[[length(niveles)]]$corr))

D$agregacion <- list(
  k = K7, s = S7, rango_correlacion = RANGO7,
  corr_teorica_base = r10(S7^2),
  mecanismo = paste("El componente independiente es ruido blanco y el",
                    "compartido es un campo suave: promediar cancela el",
                    "primero y conserva el segundo."),
  niveles = niveles,
  corr_base = r10(niveles[[1]]$corr),
  corr_max  = r10(niveles[[length(niveles)]]$corr),
  subida_pct = r10(100 * (niveles[[length(niveles)]]$corr /
                            niveles[[1]]$corr - 1))
)

# =====================================================================
# H. MÓDULO 8 — El ecosistema de R espacial
# =====================================================================
message("H · El ecosistema, con las versiones que de verdad hay instaladas")

# Las versiones NO se escriben a mano: se preguntan. Un capítulo que diga
# «sf 1.0.19» cuando la máquina tiene la 1.0.22 enseña algo falso.
paquetes <- list(
  list(nombre = "sf",        papel = "Geometría vectorial: leer, escribir, proyectar, medir, unir"),
  list(nombre = "spatstat",  papel = "Patrones puntuales: ppp, K, G, F, ppm"),
  list(nombre = "spdep",     papel = "Vecindad y pesos espaciales: nb, listw, Moran, LISA"),
  list(nombre = "gstat",     papel = "Geoestadística: variograma y kriging"),
  list(nombre = "tmap",      papel = "Mapas temáticos con gramática de capas"),
  list(nombre = "spatialreg",papel = "Econometría espacial: SAR, SEM, SDM, impactos"),
  list(nombre = "terra",     papel = "Datos ráster: leer, recortar, remuestrear y hacer álgebra de mapas"),
  list(nombre = "stars",     papel = "Cubos espacio-temporales y ráster con dimensiones con nombre"),
  list(nombre = "classInt",  papel = "Cortes de clase para coropletos: cuantiles, Jenks, Fisher"),
  list(nombre = "sfdep",     papel = "Interfaz tidy sobre spdep, para encadenar con dplyr")
)
D$ecosistema <- list(
  r_version = R.version.string,
  paquetes = lapply(paquetes, function(p) {
    v <- tryCatch(as.character(packageVersion(p$nombre)), error = function(e) NA_character_)
    c(p, list(version = v))
  }),
  sistema = list(GDAL = sf_extSoftVersion()[["GDAL"]],
                 GEOS = sf_extSoftVersion()[["GEOS"]],
                 PROJ = sf_extSoftVersion()[["PROJ"]])
)

# =====================================================================
# I. MÓDULO 9 — Anatomía de un objeto sf (y del ppp)
# =====================================================================
message("I · Anatomía de sf y de ppp")

un_punto  <- st_point(c(1, 2))                       # sfg
unos_pts  <- st_sfc(st_point(c(1, 2)), st_point(c(3, 4)), crs = 4326)  # sfc
peq       <- st_sf(id = 1:2, geom = unos_pts)        # sf

D$anatomia <- list(
  nc = list(
    filas = nrow(nc0), columnas = ncol(nc0),
    columnas_atributo = ncol(nc0) - 1L,
    tipo_geom = as.character(unique(st_geometry_type(nc0))[1]),
    n_multipolygon = as.integer(sum(st_geometry_type(nc0) == "MULTIPOLYGON")),
    # Los condados que de verdad tienen más de una parte. Es la cifra
    # sustantiva —hay islas en la costa— y además la única en la que R y
    # Python coinciden: ver la discrepancia `tipo_geometria_nc`.
    n_partes_multiples = as.integer(sum(vapply(st_geometry(nc0), length,
                                               integer(1)) > 1)),
    n_vertices = as.integer(nrow(st_coordinates(nc0))),
    bbox = r10(as.numeric(st_bbox(nc0))),
    # El peso del objeto entero frente al de solo sus atributos: la
    # geometría es la mayor parte, y por eso T0.4 la guarda una sola vez.
    bytes_sf = as.numeric(object.size(nc0)),
    bytes_atributos = as.numeric(object.size(st_drop_geometry(nc0))),
    bytes_geometria = as.numeric(object.size(st_geometry(nc0))),
    pct_geometria = r10(100 * as.numeric(object.size(st_geometry(nc0))) /
                          as.numeric(object.size(nc0)))
  ),
  clases = list(
    sfg = paste(class(un_punto), collapse = ", "),
    sfc = paste(class(unos_pts), collapse = ", "),
    sf  = paste(class(peq), collapse = ", "),
    sfg_bytes = as.numeric(object.size(un_punto)),
    sfc_bytes = as.numeric(object.size(unos_pts)),
    sf_bytes  = as.numeric(object.size(peq))
  ),
  ppp = list(
    clase = paste(class(japanesepines), collapse = ", "),
    n = npoints(japanesepines),
    ventana_tipo = japanesepines$window$type,
    ventana_area = r10(area.owin(japanesepines$window)),
    marcado = !is.null(japanesepines$marks),
    # La diferencia que sostiene el capítulo 4: un ppp lleva su ventana
    # DENTRO. Un data.frame de coordenadas, no.
    bytes = as.numeric(object.size(japanesepines))
  )
)

# =====================================================================
# J. MÓDULO 10 — Dependencia espacial en ciencia de datos
#
# FRONTERA DECLARADA CON EL CAPÍTULO 10 (decisión de Javier, 2026-08-03):
# aquí se mide UN caso pequeño y reproducible para que la afirmación no
# quede sin respaldo. El desarrollo —las tres estrategias de CV espacial,
# el tamaño de bloque guiado por el rango del variograma y el área de
# aplicabilidad— es del capítulo 10, y el texto lo remite explícitamente.
# =====================================================================
message("J · La validación cruzada aleatoria, y cuánto infla")

xy_cv <- st_coordinates(est)
z_cv  <- est$t_media_anual
n_cv  <- nrow(xy_cv)
K_VECINOS <- 5L
NPLIEGUES <- 10L

# Predictor deliberadamente simple y sin paquetes: la media de los K
# vecinos más próximos del conjunto de entrenamiento. Que sea simple es
# parte del argumento — el efecto no depende del modelo.
predice_knn <- function(idx_tr, idx_te) {
  d <- as.matrix(dist(xy_cv))[idx_te, idx_tr, drop = FALSE]
  vapply(seq_len(nrow(d)), function(i) {
    o <- order(d[i, ])[seq_len(min(K_VECINOS, length(idx_tr)))]
    mean(z_cv[idx_tr[o]])
  }, numeric(1))
}
rmse_cv <- function(pliegue) {
  err <- unlist(lapply(sort(unique(pliegue)), function(f) {
    te <- which(pliegue == f); tr <- which(pliegue != f)
    z_cv[te] - predice_knn(tr, te)
  }))
  sqrt(mean(err^2))
}

set.seed(SEMILLA + 500L)
pl_aleatorio <- sample(rep_len(seq_len(NPLIEGUES), n_cv))
set.seed(SEMILLA + 501L)
km <- kmeans(xy_cv, centers = NPLIEGUES, nstart = 25, iter.max = 100)
pl_espacial <- km$cluster

rmse_al <- rmse_cv(pl_aleatorio)
rmse_es <- rmse_cv(pl_espacial)

D$cv_espacial <- list(
  n = n_cv, k_vecinos = K_VECINOS, n_pliegues = NPLIEGUES,
  variable = "temperatura media anual (°C)",
  sd_variable = r10(sd(z_cv)),
  rmse_aleatoria = r10(rmse_al),
  rmse_bloques   = r10(rmse_es),
  # El número del módulo: cuánto se infla el desempeño al ignorar el
  # espacio. Es la misma idea que el e.e. del módulo 4, en versión
  # predictiva.
  inflacion_pct = r10(100 * (rmse_es / rmse_al - 1)),
  razon = r10(rmse_es / rmse_al),
  # Cuánto de la variabilidad explica cada una, para poder decirlo en
  # términos que un curso de ciencia de datos reconoce
  r2_aleatoria = r10(1 - rmse_al^2 / var(z_cv)),
  r2_bloques   = r10(1 - rmse_es^2 / var(z_cv)),
  # Los pliegues espaciales salen DESIGUALES, y eso no es un defecto del
  # montaje: es la geografía de las estaciones del IDEAM, que se
  # concentran en la región andina. Se publica el reparto entero en vez
  # de un mínimo y un máximo, porque el RMSE se calcula agrupando los
  # errores de los diez pliegues —no promediando diez RMSE—, y así se ve
  # que un pliegue pequeño no puede desestabilizar la cifra.
  tam_pliegues = as.integer(sort(as.vector(table(pl_espacial)))),
  tam_pliegue_min = as.integer(min(table(pl_espacial))),
  tam_pliegue_max = as.integer(max(table(pl_espacial))),
  frontera = paste("El desarrollo (blockCV, spatialsample, tamaño de bloque",
                   "guiado por el rango del variograma y área de",
                   "aplicabilidad) es del capítulo 10.")
)

# ---------------------------------------------------------------------
# J.2 · ¿DISEÑO O MODELO? La red del IDEAM no es una muestra probabilística
#
# Pebesma y Bivand, §10.4: la inferencia basada en el DISEÑO exige que el
# dato venga de un muestreo probabilístico, con probabilidades de
# inclusión conocidas y positivas. Si no lo hay, la única vía es la
# basada en MODELO. El módulo 10 mide la consecuencia predictiva de
# ignorar el espacio (la CV de arriba); esto mide la consecuencia
# INFERENCIAL, que es la otra mitad del asunto y no estaba.
#
# La red del IDEAM no se muestreó: se ubicó, donde había cómo llegar y a
# quién servir. Para ponerle cifra se construyen los polígonos de Thiessen
# de las 361 estaciones, recortados al país: el área de cada celda es el
# territorio que esa estación «representa». Bajo un muestreo de igual
# probabilidad esas áreas serían parecidas. No lo son.
#
# El emparejamiento celda -> estación va por CONTENCIÓN y no por el orden
# que devuelve st_voronoi, que no es el de entrada. Y el recorte lleva un
# id explícito porque st_intersection puede reordenar: sin él, las
# temperaturas se pegarían a las áreas equivocadas y la cifra saldría
# plausible y falsa.
# ---------------------------------------------------------------------
pais_geo <- st_union(dep)
vor <- st_collection_extract(
  st_voronoi(st_union(st_geometry(est)), st_as_sfc(st_bbox(pais_geo))), "POLYGON")
vor <- st_sf(geom = vor)
dentro <- st_within(st_geometry(est), st_geometry(vor))
stopifnot(all(lengths(dentro) == 1L))
vor <- vor[unlist(dentro), ]          # fila i de `vor` = estación i
vor$id <- seq_len(nrow(vor))
vor_rec <- suppressWarnings(st_intersection(vor, pais_geo))
area_vor <- rep(NA_real_, nrow(est))
area_vor[vor_rec$id] <- as.numeric(st_area(vor_rec)) / 1e6
stopifnot(!anyNA(area_vor))

t_ideam <- est$t_media_anual
media_area <- sum(t_ideam * area_vor) / sum(area_vor)
ancla(round(sum(area_vor), -4), 1140000,
      "área continental de Colombia reconstruida por Thiessen (km²)", tol = 1e4)

D$diseno_modelo <- list(
  n = nrow(est),
  area_total_km2 = r10(sum(area_vor)),
  area_min_km2   = r10(min(area_vor)),
  area_max_km2   = r10(max(area_vor)),
  razon_areas    = r10(max(area_vor) / min(area_vor)),
  t_media_simple = r10(mean(t_ideam)),
  t_media_area   = r10(media_area),
  # La brecha ES el argumento: si fuera cero, la red estaría equilibrada
  # y la media muestral serviría como estimador del país.
  brecha_c       = r10(media_area - mean(t_ideam)),
  # Y la CAUSA, que sin ella la brecha parece un accidente: las
  # estaciones están mucho más arriba que el territorio que representan.
  alt_media_simple = r10(mean(est$altitud_m)),
  alt_media_area   = r10(sum(est$altitud_m * area_vor) / sum(area_vor))
)

# =====================================================================
# K. MÓDULO 11 — El glosario de notación del curso
#
# Se publica aquí, no en el HTML, para que los diez capítulos citen la
# MISMA notación y para que el auditor pueda comprobarla. Las columnas
# van declaradas: A.4 dejó `iniciarGlosarios` parametrizable justo para
# esto (la versión de Muestreo traía «Lohr» y «Gutiérrez» cableados).
# =====================================================================
message("K · El glosario de notación")

D$glosario <- list(
  titulo = "Notación de Estadística Espacial",
  nota = paste("La notación unificada de los diez capítulos. La columna",
               "«Texto guía» remite a Bivand, Pebesma y Gómez-Rubio (2013)",
               "para datos de área y geoestadística, y a Baddeley, Rubak y",
               "Turner (2015) para patrones puntuales."),
  columnas = list(
    list(clave = "simbolo", titulo = "Símbolo", tipo = "mate"),
    list(clave = "nombre",  titulo = "Qué es",  tipo = "texto"),
    list(clave = "guia",    titulo = "Texto guía", tipo = "texto"),
    list(clave = "en_r",    titulo = "En R",    tipo = "codigo")
  ),
  filas = list(
    list(simbolo = "s", nombre = "Una localización del dominio", guia = "Bivand §1.2", en_r = "st_coordinates()"),
    list(simbolo = "D", nombre = "El dominio de estudio", guia = "Bivand §1.2", en_r = "st_bbox()"),
    list(simbolo = "Z(s)", nombre = "El valor del proceso en la localización s", guia = "Bivand §8.1", en_r = "x$variable"),
    list(simbolo = "h", nombre = "Vector (o distancia) de separación entre dos localizaciones", guia = "Bivand §8.4", en_r = "st_distance()"),
    list(simbolo = "C(h)", nombre = "Covarianza entre dos puntos separados h", guia = "Bivand §8.4", en_r = "gstat::variogram()"),
    list(simbolo = "\\gamma(h)", nombre = "Semivariograma", guia = "Bivand §8.4", en_r = "gstat::variogram()"),
    # §6.2 «Estimating homogeneous intensity», no §5.3. La referencia vieja
    # mandaba al estudiante a §5.3, que es «Complete spatial randomness»:
    # una sección real y del tema, pero no la de este símbolo. Corregido
    # contra el índice que los autores publican en book.spatstat.org, donde
    # 6 es Intensity, 7 Correlation y 8 Spacing. (2026-08-10)
    list(simbolo = "\\lambda", nombre = "Intensidad de un patrón puntual", guia = "Baddeley §6.2", en_r = "spatstat.geom::intensity()"),
    # Los dos que estrena el módulo 3 de este capítulo. Van juntos porque
    # el segundo es el primero dividido por su valor esperado bajo CSR.
    list(simbolo = "\\bar{d}_{\\min}", nombre = "Distancia media al vecino más próximo", guia = "Baddeley §8.2", en_r = "mean(spatstat.geom::nndist())"),
    # El ['naive'] NO es un detalle de estilo: clarkevans() devuelve TRES
    # valores —naive, Donnelly y cdf— y solo el primero es el que publica
    # la tabla del módulo 3. Sin el índice, quien ejecute la celda ve tres
    # números y dos no cuadran con el material.
    list(simbolo = "R", nombre = "Índice de Clark-Evans: lo observado frente a lo que daría el azar", guia = "Baddeley §8.2", en_r = "spatstat.explore::clarkevans()['naive']"),
    list(simbolo = "W", nombre = "Matriz de pesos espaciales", guia = "Bivand §9.2", en_r = "spdep::nb2listw()"),
    list(simbolo = "Wy", nombre = "Rezago espacial: la media de los vecinos", guia = "Bivand §9.3", en_r = "spdep::lag.listw()"),
    list(simbolo = "I", nombre = "Índice de Moran (autocorrelación global)", guia = "Bivand §9.3", en_r = "spdep::moran.test()"),
    list(simbolo = "n_{\\text{eff}}", nombre = "Tamaño de muestra efectivo", guia = "Cressie §1.3", en_r = "—"),
    list(simbolo = "\\rho", nombre = "Coeficiente de retardo espacial (SAR)", guia = "Bivand §9.4", en_r = "spatialreg::lagsarlm()"),
    list(simbolo = "G_i^*", nombre = "Estadístico de Getis-Ord local", guia = "Bivand §9.3", en_r = "spdep::localG()")
  )
)

# =====================================================================
# L. El árbol de decisión del curso (simulador 8)
# =====================================================================
D$arbol <- list(
  titulo = "¿Qué método necesito?",
  raiz = "tipo",
  nodos = list(
    list(id = "tipo", pregunta = "¿Qué es aleatorio en tu dato?",
         opciones = list(
           list(texto = "La LOCALIZACIÓN de los eventos", destino = "puntual"),
           list(texto = "El VALOR sobre unidades territoriales fijas", destino = "area"),
           list(texto = "El VALOR de algo que existe en todo punto", destino = "geo"))),
    list(id = "puntual", pregunta = "Patrón puntual. ¿Qué preguntas?",
         opciones = list(
           list(texto = "¿Hay agregación o regularidad?", destino = "hoja_k",
                metodo = "K de Ripley, g(r), envolventes", capitulo = 4),
           list(texto = "¿Dónde es más intenso?", destino = "hoja_kde",
                metodo = "Estimación por núcleos de la intensidad", capitulo = 5),
           list(texto = "¿Qué covariables lo explican?", destino = "hoja_ppm",
                metodo = "ppm, proceso de Poisson inhomogéneo", capitulo = 5))),
    list(id = "area", pregunta = "Dato de área. ¿Qué preguntas?",
         opciones = list(
           list(texto = "¿Lo cercano se parece?", destino = "hoja_moran",
                metodo = "I de Moran, c de Geary, LISA, G*", capitulo = 7),
           list(texto = "¿Cómo defino quién es vecino?", destino = "hoja_w",
                metodo = "poly2nb, knn2nb, dnearneigh, nb2listw", capitulo = 6),
           list(texto = "¿Qué explica la variable?", destino = "hoja_sar",
                metodo = "SAR, SEM, SDM, GWR", capitulo = 8))),
    list(id = "geo", pregunta = "Dato geoestadístico. ¿Qué preguntas?",
         opciones = list(
           list(texto = "¿Cómo decae la dependencia?", destino = "hoja_vario",
                metodo = "Variograma empírico y modelo teórico", capitulo = 9),
           list(texto = "¿Cuánto vale donde no medí?", destino = "hoja_krig",
                metodo = "Kriging ordinario, universal o con deriva", capitulo = 9),
           list(texto = "¿Cuánto me fío de mi modelo predictivo?", destino = "hoja_cv",
                metodo = "Validación cruzada espacial por bloques", capitulo = 10)))
  )
)

# =====================================================================
# M. Los .geomapa del capítulo
# =====================================================================
message("M · Los mapas")

MAPAS <- list()

# --- M.1 Snow: puntos + calles + bombas -------------------------------
lineas_calle <- lapply(split(Snow.streets, Snow.streets$street),
                       function(s) as.matrix(s[, c("x", "y")]))
# La marca es la bomba más próxima, y eso es una CATEGORÍA, no un número:
# la bomba 10 no está «más arriba» que la 3. Se pasa como factor con los
# trece rótulos por niveles, así que los códigos salen idénticos a los de
# `mas_cerca` —el JSON no cambia por este lado— y el mapa gana la lista de
# niveles con la que el navegador colorea y rotula. Ver geo_puntos().
bomba_de <- factor(as.character(Snow.pumps$label)[mas_cerca],
                   levels = as.character(Snow.pumps$label))
stopifnot(identical(as.integer(bomba_de), as.integer(mas_cerca)))
MAPAS$snow <- geo_puntos(
  muertes, marcas = bomba_de,
  lineas = unname(lineas_calle),
  puntos2 = bombas, etiquetas2 = as.character(Snow.pumps$label),
  resaltado2 = i_broad,
  titulo = "Muertes por cólera y bombas de agua, Soho, 1854",
  leyenda = "bomba más próxima")

# --- M.2 Los tres tipos de dato, canónicos ----------------------------
# La ventana se LEE del objeto, no se escribe. Escrita a mano estuvo mal
# desde T1.2 y en silencio: los tres se declaraban `c(0, 0, 1, 1)`, pero
# la ventana de `redwood` en spatstat es [0,1] x [-1,0]. `geo_puntos()`
# une la caja de los puntos con la ventana declarada, así que el mapa de
# las secuoyas salía con una razón de 1.96 —los 62 puntos apretados en la
# mitad de abajo y la mitad de arriba en blanco—, y con él la comparación
# «los tres son el mismo dibujo» habría sido falsa justo en el módulo que
# la usa como argumento. No se vio en dos meses porque el mapa se
# exportaba y no se dibujaba en ninguna parte. (2026-08-10)
ventana_de <- function(p) c(p$window$xrange[1], p$window$yrange[1],
                            p$window$xrange[2], p$window$yrange[2])
# Y que los tres cuadrados sean del mismo tamaño no es decorativo: es lo
# que permite decir «sobre una ventana unitaria» y comparar las tres
# distancias al vecino sin más correcciones.
for (p in list(japanesepines, redwood, cells)) {
  v <- ventana_de(p)
  stopifnot(abs((v[3] - v[1]) - 1) < 1e-9, abs((v[4] - v[2]) - 1) < 1e-9)
}
MAPAS$japanesepines <- geo_puntos(
  cbind(japanesepines$x, japanesepines$y),
  ventana = ventana_de(japanesepines),
  titulo = "Pinos japoneses: patrón puntual", leyenda = "árbol")
MAPAS$redwood <- geo_puntos(
  cbind(redwood$x, redwood$y), ventana = ventana_de(redwood),
  titulo = "Plántulas de secuoya: agregación", leyenda = "plántula")
MAPAS$cells <- geo_puntos(
  cbind(cells$x, cells$y), ventana = ventana_de(cells),
  titulo = "Células: regularidad", leyenda = "célula")

nc_proj <- st_transform(nc, 32617)     # UTM 17N, para no deformar el mapa
MAPAS$nc <- geo_poligonos(
  nc_proj, valor = nc_proj$tasa_sids, n_clases = 5, estilo = "quantile",
  etiquetas = nc_proj$NAME, presupuesto = 900L,
  titulo = "Tasa de muerte súbita infantil, Carolina del Norte 1974-78",
  leyenda = "por 1 000 nacimientos", verbose = FALSE)

MAPAS$meuse <- geo_puntos(
  as.matrix(meuse[, c("x", "y")]), marcas = as.numeric(meuse$zinc),
  titulo = "Zinc en la vega del Mosa", leyenda = "ppm")

# --- M.2b El mapa del módulo 7: la rejilla encima de los condados -----
#
# El error de agregación más caro del capítulo estaba DICHO y no MOSTRADO.
# Éste es el mapa que lo enseña: los 100 condados coloreados por el conteo
# que se está sumando, la rejilla de 100 rectángulos encima, el condado que
# más infla el total resaltado y las celdas que toca marcadas.
#
# TRES DECISIONES QUE NO SON DE ESTILO:
#
# 1. EPSG:2264 y no 32617. El otro mapa de nc del capítulo va en UTM 17N,
#    pero la rejilla del módulo 7 la construyó `st_make_grid` sobre el
#    State Plane —como el libro—, así que el mapa tiene que ir en el CRS
#    en el que se hizo la cuenta. Dibujar la rejilla del 2264 sobre unos
#    condados proyectados a 32617 daría un mapa plausible y falso.
#
# 2. `caja` explícita, la de la rejilla SIN simplificar. `geo_simplifica`
#    mueve vértices y encoge el bbox de los condados unos metros; si la
#    caja saliera de ahí, la rejilla —que no se simplifica— asomaría por
#    fuera del encuadre y el navegador le recortaría el borde exterior.
#
# 3. El mismo presupuesto de vértices que `MAPAS$nc` (900). Son dos mapas
#    del mismo territorio en el mismo capítulo: si uno saliera más
#    detallado que el otro, el lector leería la diferencia como si dijera
#    algo, y no dice nada.
lineas_rejilla <- lapply(st_geometry(rej_nc),
                         function(g) st_coordinates(g)[, 1:2, drop = FALSE])
MAPAS$agregacion <- geo_poligonos(
  nc_ag, valor = nc_ag$SID74, n_clases = 5, estilo = "quantile",
  presupuesto = 900L, verbose = FALSE,
  caja = geo_caja(rej_nc),
  lineas = lineas_rejilla,
  lineas_resaltadas = cel_caso,
  resaltado = i_caso,
  titulo = sprintf("Los %d condados y la rejilla de %d rectángulos",
                   nrow(nc_ag), nrow(rej_nc)),
  leyenda = "muertes súbitas, 1974-78")

# --- M.3 Los tres tipos, colombianos ----------------------------------
# Sin marcas: el capítulo 1 solo enseña que esto es un patrón puntual.
# La marca (urbana/rural, sector, jornada) es del capítulo 4, y aquí
# costaría 4,4 KB del presupuesto sin decir nada todavía.
MAPAS$bogota <- geo_puntos(
  st_coordinates(cole),
  titulo = "Sedes educativas de Bogotá", leyenda = "sede")
MAPAS$desercion <- geo_poligonos(
  dep_ok, valor = dep_ok$desercion, n_clases = 5, estilo = "quantile",
  etiquetas = dep_ok$shapeName, presupuesto = 1200L,
  titulo = "Deserción escolar por departamento (%)",
  leyenda = "deserción (%)", verbose = FALSE)
# 2 decimales en la marca: una temperatura en centésimas de grado es más
# precisión de la que tiene el dato y de la que distingue una rampa de
# color, y cada decimal de más son bytes del presupuesto.
MAPAS$ideam <- geo_puntos(
  st_coordinates(est), marcas = round(as.numeric(est$t_media_anual), 2),
  titulo = "Temperatura media anual, estaciones del IDEAM",
  leyenda = "°C")

# --- M.4 Los campos gaussianos de los simuladores ---------------------
# Una realización por valor de phi, en 28 x 28. Son la fuente del
# simulador «campo gaussiano con correlación regulable» del módulo 3-4.
#
# 28 y no 32: sobre un lienzo de ~350 px cada celda son 12 px, que se lee
# igual de bien, y las rejillas juntas bajan casi a la mitad. El
# presupuesto del capítulo manda sobre la resolución cuando la resolución
# de más no se ve.
#
# PHIS_VER cubre los SIETE alcances de `inferencia.rejilla` y no cinco
# (T1.2): el deslizador del módulo 4 recorre las cifras de esa rejilla, y
# dejar dos posiciones sin campo obligaba a acortar el control justo en
# los dos extremos que más enseñan — phi = 0 es la imagen de la
# independencia.
K8 <- 28L; N8 <- K8^2
rej8 <- expand.grid(x = seq_len(K8), y = seq_len(K8))
D8 <- as.matrix(dist(rej8))
PHIS_VER <- c(0, 0.5, 1, 2, 4, 8, 16)
set.seed(SEMILLA + 600L)
# El MISMO ruido blanco para todos los phi: así lo único que cambia entre
# un mapa y el siguiente es la correlación, no la realización. Sin esto
# el simulador parecería estar cambiando de dato al mover el control.
e8 <- rnorm(N8)
MAPAS$campos <- lapply(PHIS_VER, function(phi) {
  # phi = 0 es el caso LÍMITE, no un valor más: rho(h) = 0 para todo
  # h > 0, o sea R = I y el campo ES el ruido blanco de arriba. La
  # fórmula no sirve ahí —D8/0 da NaN en la diagonal—, así que se
  # despacha aparte. Y como el ruido es común a todos los phi, el mapa
  # de phi = 0 enseña literalmente el punto de partida de los otros seis.
  z <- if (phi == 0) e8 else
    as.numeric(t(chol(exp(-D8 / phi) + diag(1e-8, N8))) %*% e8)
  g <- geo_rejilla(matrix(z, K8, K8), caja = c(0, 0, K8, K8),
                   titulo = sprintf("Campo gaussiano, rango = %g", phi),
                   leyenda = "z", n_clases = 7, estilo = "equal")
  g$phi <- r10(phi)
  g$rho_vecino <- r10(if (phi == 0) 0 else exp(-1 / phi))
  g$moran <- r10(local({
    nb <- cell2nb(K8, K8, type = "queen")
    moran.test(z, nb2listw(nb, style = "W"))$estimate[["Moran I statistic"]]
  }))
  g
})

# --- M.5 Los mapas de las tres realizaciones que se enseñan -----------
# Las tres primeras del lote de la sección F, en su MISMA rejilla de
# K6 x K6. Aquí no se simula nada: `CAMPOS` ya está en memoria, y esa es
# justo la corrección de T1.3 —había una segunda simulación de 28 x 28
# con semilla propia cuyo variograma nadie dibujaba y cuyas cifras el
# texto atribuía a la de 16 x 16—.
#
# `mean(z)`/`sd(z)` sobre el vector del mapa, y no una copia de
# `medias_real[i]`: las dos rutas tienen que coincidir y el ensamblador
# lo exige. Copiarlas de la sección F volvería tautológica esa guarda.
MAPAS$realizaciones <- lapply(seq_len(N_VISTAS), function(i) {
  z <- CAMPOS[, i]
  g <- geo_rejilla(matrix(z, K6, K6), caja = c(0, 0, K6, K6),
                   titulo = sprintf("Realización %d del mismo proceso", i),
                   leyenda = "z", n_clases = 7, estilo = "equal")
  g$id             <- i
  g$media_espacial <- r10(mean(z))
  g$sd_espacial    <- r10(sd(z))
  g
})

# =====================================================================
# N. Escritura
# =====================================================================
message("N · Escritura")

D$meta <- list(
  capitulo = 1L,
  titulo = "Datos espaciales y la primera ley de la geografía",
  semana = 1L,
  generado = format(Sys.Date()),
  semilla = SEMILLA,
  r = R.version.string,
  anclas_verificadas = N_ANCLAS
)

# --- Los crudos que salen a CSV, y por qué ----------------------------
#
# Dos motivos, los dos importantes:
#
# 1. `audita_cap1.py` tiene que poder recalcular por su cuenta. Los datos
#    colombianos y `nc.shp` los lee geopandas directamente, así que ahí
#    la independencia es total. Pero `HistData`, `spatstat.data` y
#    `sp::meuse` NO existen en Python, y sin exportarlos el auditor no
#    tendría forma de contrastar la mitad del capítulo. Se exportan, y el
#    auditor DECLARA lo que eso limita: sobre estos cuatro conjuntos
#    verifica el análisis, no la lectura del paquete —esa la ancla R
#    contra las cifras que publican las fuentes—.
#
# 2. Las pestañas R/Python de T1.2 necesitan que el bloque de Python
#    parta del mismo dato. Sin esto, el bloque de Python del capítulo no
#    podría reproducir ninguna cifra de la prosa.
write.csv(data.frame(dpto = dep_ok$dpto, nombre = dep_ok$shapeName,
                     desercion = r10(dep_ok$desercion),
                     cobertura = r10(dep_ok$cobertura)),
          file.path(SALIDAS, "cap1_dep.csv"), row.names = FALSE,
          fileEncoding = "UTF-8")

write.csv(rbind(
  data.frame(tipo = "muerte", etiqueta = as.character(Snow.deaths$case),
             x = r10(Snow.deaths$x), y = r10(Snow.deaths$y)),
  data.frame(tipo = "bomba", etiqueta = as.character(Snow.pumps$label),
             x = r10(Snow.pumps$x), y = r10(Snow.pumps$y))),
  file.path(SALIDAS, "cap1_snow.csv"), row.names = FALSE, fileEncoding = "UTF-8")

write.csv(data.frame(fecha = format(sd_dat$date),
                     ataques = as.integer(sd_dat$attacks),
                     muertes = as.integer(sd_dat$deaths)),
          file.path(SALIDAS, "cap1_snow_fechas.csv"), row.names = FALSE,
          fileEncoding = "UTF-8")

write.csv(do.call(rbind, Map(function(p, nm)
  data.frame(patron = nm, x = r10(p$x), y = r10(p$y)),
  list(japanesepines, redwood, cells),
  c("japanesepines", "redwood", "cells"))),
  file.path(SALIDAS, "cap1_ppp.csv"), row.names = FALSE, fileEncoding = "UTF-8")

write.csv(data.frame(x = meuse$x, y = meuse$y, zinc = meuse$zinc,
                     dist = r10(meuse$dist), elev = r10(meuse$elev)),
          file.path(SALIDAS, "cap1_meuse.csv"), row.names = FALSE,
          fileEncoding = "UTF-8")

write_json(D, file.path(SALIDAS, "cap1_datos.json"),
           auto_unbox = TRUE, digits = 10, pretty = TRUE, na = "null")
write_json(MAPAS, file.path(SALIDAS, "cap1_mapas.json"),
           auto_unbox = TRUE, digits = 8, na = "null")

kb_d <- file.size(file.path(SALIDAS, "cap1_datos.json")) / 1024
kb_m <- file.size(file.path(SALIDAS, "cap1_mapas.json")) / 1024
message(sprintf("\ncap1_datos.json  %.1f KB", kb_d))
message(sprintf("cap1_mapas.json  %.1f KB   (presupuesto de geometría: 120 KB)", kb_m))

# El presupuesto del §4 del plan es de geometría. Los campos gaussianos
# son rejillas simuladas, no territorio, así que se cuentan aparte y se
# declara la separación en vez de esconderla dentro de un solo total.
kb_geo <- sum(vapply(
  MAPAS[c("snow", "japanesepines", "redwood", "cells", "nc", "agregacion",
          "meuse", "bogota", "desercion", "ideam")],
  function(g) nchar(toJSON(g, auto_unbox = TRUE, digits = 8), type = "bytes") / 1024,
  numeric(1)))
kb_sim <- kb_m - kb_geo
message(sprintf("  geografía: %.1f KB · rejillas simuladas: %.1f KB", kb_geo, kb_sim))
# El §4 del plan presupuesta 120 KB de GEOMETRÍA por capítulo. Las
# rejillas simuladas no son territorio, pero también viajan dentro del
# HTML, así que se comprueban las dos cosas: la geometría contra su
# presupuesto y el total contra un listón propio, para no ir gastando por
# la puerta de atrás lo que se ahorra por la de delante.
#
# EL LISTÓN DEL TOTAL SE SUBE A 160 EN T2.4, Y SE DICE POR QUÉ. Estaba en
# 120, el mismo número que el presupuesto de geometría, y eso lo convertía
# en el que mandaba: con 89,7 KB de geografía y 27,6 de rejillas, cada una
# a menos del 75 % de SU presupuesto, el capítulo iba al 97,7 % del total.
# O sea que el mapa siguiente lo habría decidido esta línea y no el §4 —es
# exactamente lo que T1.1 encontró con el tope de 560 KB del HTML, que
# llegó a querer recortar comentarios del código para ganar 1,3 KB—. El
# total no es un presupuesto de contenido: es una alarma contra un
# ensamblado desbocado, y 160 la deja alarmando (los dos presupuestos
# juntos suman 240, así que sigue muy por debajo de lo vacuo) sin que
# vuelva a ser ella quien decide qué se enseña. Ver
# `Vault/Estandar/Criterio de contenido.md`.
if (kb_geo > 120) stop("la geometría del capítulo 1 se sale del presupuesto de 120 KB")
if (kb_m > 160) stop(sprintf(
  "el conjunto de mapas pesa %.1f KB y la alarma del capítulo está en 160 KB", kb_m))

message("\nCifras que el capítulo va a citar:")
message(sprintf("  Snow: %.2f %% de las muertes tienen Broad St como bomba más próxima (%d de %d)",
                D$snow$pct_mas_cerca_broad, D$snow$n_mas_cerca_broad, D$snow$n_muertes))
message(sprintf("        y el %.2f %% de los ataques ocurrió ANTES del 8 de septiembre",
                D$snow$pct_ataques_antes_mango))
message(sprintf("  e.e.: cobertura del IC 95 %% con phi=4: %.4f (+- %.4f), factor %.4f",
                D$inferencia$cobertura_phi4, mc[[which(PHIS == 4)]]$emc_cobertura,
                D$inferencia$factor_phi4))
message(sprintf("  real: e.e. bootstrap i.i.d. %.5f vs. por bloques %.5f -> factor %.4f",
                D$inferencia_real$ee_bootstrap_iid, D$inferencia_real$ee_bootstrap_bloques,
                D$inferencia_real$factor))
message(sprintf("  n_eff de %d municipios: %.2f (%.2f %% de la información)",
                D$inferencia_real$n_municipios, D$inferencia_real$n_eff,
                D$inferencia_real$pct_informacion))
message(sprintf("  MAUP: I = %.4f (%d municipios) -> %.4f (%d dptos), cae %.2f %%",
                D$escala$moran_municipal, D$escala$n_municipal,
                D$escala$moran_departamental, D$escala$n_departamental,
                D$escala$caida_pct))
message(sprintf("  CV:   RMSE aleatoria %.4f vs. por bloques %.4f -> infla %.2f %%",
                D$cv_espacial$rmse_aleatoria, D$cv_espacial$rmse_bloques,
                D$cv_espacial$inflacion_pct))
message(sprintf("\n  %d anclas contra la literatura, todas verificadas", N_ANCLAS))
