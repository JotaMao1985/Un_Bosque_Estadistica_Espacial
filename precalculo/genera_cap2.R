# =====================================================================
# genera_cap2.R — el precálculo del capítulo 2 (T2.1b)
#
#   «SIG, sistemas de referencia y georreferenciación con sf» · semanas 2-3
#   Material de Estadística Espacial 2026-II (20929).
#
# QUÉ PRODUCE
#   precalculo/salidas/cap2_datos.json   todas las cifras de los 12 módulos
#   precalculo/salidas/cap2_mapas.json   las fuentes de los .geomapa
#   precalculo/salidas/cap2_*.csv        lo que las pestañas de Python leen
#
# LA REGLA QUE MANDA (D10): ninguna cifra del capítulo se escribe a mano.
# El JSON se guarda con 10 decimales y la prosa publica 5, para que no
# haya doble redondeo entre el texto y el bloque de código.
#
# EL RIESGO PROPIO DE ESTE CAPÍTULO, que el §6 del plan declara: es el
# más propenso a afirmaciones plausibles y falsas —«el error es
# pequeño»—. Aquí no se afirma ninguna: cada comparación de áreas, de
# distancias y de ángulos se calcula, y las que tienen valor teórico
# conocido se anclan contra él.
#
# LA REFERENCIA ES EL ELIPSOIDE, Y ESO NO ES UN DETALLE.
# `st_area()` con s2 encendido mide sobre una ESFERA, y sobre Colombia
# esa esfera infla el área un 0,44 % de mediana. Ese 0,44 % se cuela
# entero dentro de cualquier razón que lo use de referencia: con él,
# EPSG:3116 —que tiene k = 1 y por tanto NO PUEDE encoger nada— parecía
# encoger las áreas un 0,4 %. Todas las áreas «verdaderas» de este
# capítulo se miden con `area_elip()`, que apaga s2 y deja medir a
# lwgeom sobre el elipsoide. La discrepancia esfera/elipsoide no se
# esconde: es el módulo 6.
#
# Ejecutar SIEMPRE con el envoltorio, nunca con `Rscript` a pelo:
#     precalculo/rscript.sh precalculo/genera_cap2.R
# desde la carpeta `Estadistica espacial/`. Ver utf8.R y rscript.sh.
# =====================================================================

suppressPackageStartupMessages({
  library(sf)
  library(spData)
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

# Las semillas del capítulo, declaradas aquí y no repartidas por el
# archivo: equivocarse de semilla devuelve un número PARECIDO y correcto
# de aspecto, que es el peor tipo de error (lección de T1.1).
SEM_RUIDO <- 2226L      # el ruido posicional del módulo 9

r10 <- function(x) round(as.numeric(x), 10)

# ---------------------------------------------------------------------
# ancla() — la transcripción contra la literatura, que PARA si falla
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

# ---------------------------------------------------------------------
# Medir sobre el elipsoide y sobre la esfera, a propósito y por separado
#
# No es un envoltorio por comodidad: es la pieza que impide que el
# capítulo compare peras con manzanas sin enterarse. `area_elip` apaga
# s2 y deja que lwgeom integre sobre el elipsoide; `area_esf` es lo que
# hace sf por defecto. La diferencia entre las dos ES el módulo 6.
# ---------------------------------------------------------------------
con_s2 <- function(usar, expr) {
  antes <- suppressMessages(sf_use_s2(usar))
  on.exit(suppressMessages(sf_use_s2(antes)))
  suppressMessages(force(expr))
}
area_elip <- function(x) con_s2(FALSE, as.numeric(st_area(x)))
area_esf  <- function(x) con_s2(TRUE,  as.numeric(st_area(x)))
dist_elip <- function(a, b) con_s2(FALSE, as.numeric(st_distance(a, b, by_element = TRUE)))
dist_esf  <- function(a, b) con_s2(TRUE,  as.numeric(st_distance(a, b, by_element = TRUE)))
pto <- function(lon, lat, crs = 4326) st_sfc(st_point(c(lon, lat)), crs = crs)

D <- list()
MAPAS <- list()

# =====================================================================
# A. MÓDULO 1 — La Tierra no es plana ni una esfera
# =====================================================================
message("A · elipsoide, geoide y datum")

cr <- st_crs(4326)
ea <- as.numeric(cr$SemiMajor); eb <- as.numeric(cr$SemiMinor)
apl_inv <- ea / (ea - eb)
e2 <- (ea^2 - eb^2) / ea^2

# Las dos cifras que DEFINEN el WGS84 (NIMA TR8350.2). No son medidas:
# son la definición, así que la tolerancia es de redondeo puro.
ancla(ea, 6378137, "semieje mayor del WGS84", tol = 1e-6)
ancla(apl_inv, 298.257223563, "aplanamiento inverso del WGS84", tol = 1e-6)

# Radios de curvatura a varias latitudes. M (meridiano) y N (primer
# vertical) son lo que hace que «un grado» no mida lo mismo en todas
# partes, y son la base local de la indicatriz de Tissot del módulo 3.
LATS <- c(0, 4.7110, 40, 59.9139, 80)
w_lat <- sqrt(1 - e2 * sin(LATS * pi / 180)^2)
M_lat <- ea * (1 - e2) / w_lat^3
N_lat <- ea / w_lat

# La esfera contra el elipsoide, sobre una distancia larga de verdad.
BOG <- c(-74.0721, 4.7110); OSL <- c(10.7522, 59.9139)
p_bog <- pto(BOG[1], BOG[2]); p_osl <- pto(OSL[1], OSL[2])
d_esf <- dist_esf(p_bog, p_osl); d_eli <- dist_elip(p_bog, p_osl)

# El datum: Bogotá 1975 (EPSG:4218) contra WGS84. Las mismas cifras de
# latitud y longitud, leídas en dos datums, señalan puntos distintos del
# terreno — y ningún programa avisa.
CIUDADES <- data.frame(
  ciudad = c("Bogotá", "Medellín", "Cúcuta", "Leticia", "Quibdó"),
  lon = c(-74.0721, -75.5636, -72.5078, -69.9406, -76.6612),
  lat = c(  4.7110,   6.2518,   7.8891,  -4.2150,   5.6947))
p_wgs <- st_sfc(lapply(seq_len(nrow(CIUDADES)),
                       function(i) st_point(c(CIUDADES$lon[i], CIUDADES$lat[i]))), crs = 4326)
p_bta <- st_transform(p_wgs, 4218)
xy_bta <- st_coordinates(p_bta)
# Se reinterpretan las coordenadas de Bogotá 1975 COMO SI fueran WGS84:
# eso es exactamente lo que hace un programa al que no se le dice el
# datum, y el desplazamiento resultante es el error que comete.
p_como_wgs <- st_sfc(lapply(seq_len(nrow(xy_bta)),
                            function(i) st_point(xy_bta[i, ])), crs = 4326)
desp_datum <- dist_elip(p_wgs, p_como_wgs)

D$elipsoide <- list(
  a = r10(ea), b = r10(eb), a_menos_b = r10(ea - eb),
  aplanamiento_inv = r10(apl_inv), e2 = r10(e2),
  radios = list(lat = LATS, M = r10(M_lat), N = r10(N_lat),
                razon_N_M = r10(N_lat / M_lat)),
  esfera_vs_elipsoide = list(
    origen = "Bogotá", destino = "Oslo",
    d_esfera_m = r10(d_esf), d_elipsoide_m = r10(d_eli),
    dif_m = r10(d_eli - d_esf), dif_pct = r10(100 * (d_eli - d_esf) / d_eli)),
  datum = list(
    origen_epsg = 4326L, destino_epsg = 4218L,
    destino_nombre = "Bogota 1975",
    towgs84 = c(307, 304, -318),
    ciudad = CIUDADES$ciudad,
    desplazamiento_m = r10(desp_datum),
    desp_medio_m = r10(mean(desp_datum)),
    desp_min_m = r10(min(desp_datum)), desp_max_m = r10(max(desp_datum))))

# =====================================================================
# B. MÓDULO 2 — Latitud y longitud no son coordenadas cartesianas
# =====================================================================
message("B · un grado, según dónde")

grado <- function(la) {
  a1 <- st_sfc(st_point(c(0, la)), crs = 4326)
  a2 <- st_sfc(st_point(c(1, la)), crs = 4326)
  b2 <- st_sfc(st_point(c(0, la + 1)), crs = 4326)
  c(lon_elip = dist_elip(a1, a2), lat_elip = dist_elip(a1, b2),
    lon_esf = dist_esf(a1, a2), lat_esf = dist_esf(a1, b2))
}
LATS_G <- c(0, 4.7110, 10, 20, 30, 40, 45, 50, 59.9139, 70, 80)
G <- as.data.frame(t(vapply(LATS_G, grado, numeric(4))))
G$lat <- LATS_G

# Las dos cifras publicadas de la geodesia elemental: un grado de latitud
# mide 110,574 km en el ecuador y 111,694 km en el polo. Con tolerancia
# de un metro, porque la fuente publica al metro.
ancla(G$lat_elip[G$lat == 0], 110574.3, "un grado de latitud en el ecuador (m)", tol = 1.0)
ancla(dist_elip(st_sfc(st_point(c(0, 89)), crs = 4326),
                st_sfc(st_point(c(0, 90)), crs = 4326)),
      111694.0, "un grado de latitud junto al polo (m)", tol = 1.5)
ancla(G$lon_elip[G$lat == 0], 111319.5, "un grado de longitud en el ecuador (m)", tol = 1.0)

# Y la consecuencia, medida sobre dato real: la distancia euclídea en
# GRADOS no es una distancia. Se compara contra la geodésica sobre las
# 361 estaciones del IDEAM.
est <- st_transform(st_read("datos/procesado/colombia_estaciones_clima.gpkg", quiet = TRUE), 4326)
xy_est <- st_coordinates(est)
n_est <- nrow(est)
set.seed(SEMILLA)
pares <- cbind(sample(n_est, 2000, replace = TRUE), sample(n_est, 2000, replace = TRUE))
pares <- pares[pares[, 1] != pares[, 2], ]
d_grados <- sqrt((xy_est[pares[, 1], 1] - xy_est[pares[, 2], 1])^2 +
                 (xy_est[pares[, 1], 2] - xy_est[pares[, 2], 2])^2)
d_real <- dist_elip(st_geometry(est)[pares[, 1]], st_geometry(est)[pares[, 2]])
# Si un grado midiera lo mismo en las dos direcciones, la razón
# metros/grado sería constante. Se mide cuánto varía.
razon_km_grado <- (d_real / 1000) / d_grados

D$grados <- list(
  lat = G$lat,
  lon_m_elipsoide = r10(G$lon_elip), lat_m_elipsoide = r10(G$lat_elip),
  lon_m_esfera = r10(G$lon_esf), lat_m_esfera = r10(G$lat_esf),
  # cuánto encoge el grado de longitud desde el ecuador
  lon_pct_del_ecuador = r10(100 * G$lon_elip / G$lon_elip[1]),
  bogota_vs_oslo = r10(G$lon_elip[G$lat == 4.7110] / G$lon_elip[G$lat == 59.9139]),
  # el grado de LATITUD sobre la esfera es constante y sobre el
  # elipsoide no: la esfera esconde el achatamiento
  lat_esfera_constante = r10(diff(range(G$lat_esf))),
  lat_elipsoide_recorrido_m = r10(diff(range(G$lat_elip))),
  euclidea = list(
    n_pares = nrow(pares), n_estaciones = n_est,
    km_por_grado_med = r10(median(razon_km_grado)),
    km_por_grado_min = r10(min(razon_km_grado)),
    km_por_grado_max = r10(max(razon_km_grado)),
    recorrido_pct = r10(100 * (max(razon_km_grado) / min(razon_km_grado) - 1)),
    corr = r10(cor(d_grados, d_real))))

# =====================================================================
# C. MÓDULO 3 — Proyectar es elegir qué destruir (Tissot)
# =====================================================================
message("C · las seis proyecciones, con la distorsión medida")

geo_tissot_autoprueba()      # las tres anclas matemáticas del medidor
N_ANCLAS <- N_ANCLAS + 3L    # Mercator conforme · Mollweide equivalente · eqc

PROY_MUNDO <- list(
  list(nombre = "Mercator", crs = "+proj=merc +ellps=WGS84 +units=m +no_defs",
       familia = "conforme"),
  list(nombre = "Web Mercator (3857)", crs = 3857,
       familia = "ni conforme ni equivalente"),
  list(nombre = "Mollweide", crs = "+proj=moll +ellps=WGS84 +units=m +no_defs",
       familia = "equivalente sobre la esfera"),
  list(nombre = "Equal Earth", crs = "+proj=eqearth +ellps=WGS84 +units=m +no_defs",
       familia = "equivalente"),
  list(nombre = "Robinson", crs = "+proj=robin +ellps=WGS84 +units=m +no_defs",
       familia = "compromiso"),
  list(nombre = "Azimutal equidistante (Bogotá)",
       crs = "+proj=aeqd +lat_0=4.711 +lon_0=-74.0721 +ellps=WGS84 +units=m +no_defs",
       familia = "equidistante desde el centro"))

REJ <- expand.grid(lon = seq(-150, 150, by = 60), lat = seq(-60, 60, by = 30))

mundo <- world[, c("name_long", "continent")]
# Mercator manda la latitud 90 al infinito, así que TODO atlas recorta.
# Se recorta una vez, para las seis vistas, y se declara: es parte de la
# lección, no una trampa para que el mapa salga bonito.
LAT_CORTE <- 84
s2_antes <- suppressMessages(sf_use_s2(FALSE))
mundo <- suppressWarnings(suppressMessages(
  st_crop(st_make_valid(mundo),
          st_bbox(c(xmin = -180, ymin = -LAT_CORTE, xmax = 180, ymax = LAT_CORTE)))))
# LO QUE SE MIDE Y LO QUE SE DIBUJA NO SON LO MISMO, y conviene decirlo.
# La razón de área se mide sobre los 177 PAÍSES —es la cifra que el
# capítulo cita, y sobre países reales significa algo—; lo que viaja
# dentro del HTML es el mundo DISUELTO POR CONTINENTE, porque 177
# polígonos bajo seis proyecciones son 95 KB de los 120 del capítulo
# entero. La forma del planeta, que es lo que el mapa tiene que enseñar,
# sobrevive intacta a la disolución.
continentes <- suppressWarnings(suppressMessages(
  st_make_valid(aggregate(mundo["continent"], by = list(cont = mundo$continent),
                          FUN = function(z) z[1]))))
suppressMessages(sf_use_s2(s2_antes))
ancla(nrow(world), 177, "países de spData::world", tol = 0)

# La razón de área, país a país, sobre la geometría SIN disolver.
razon_pais <- function(crs) {
  ap <- suppressMessages(as.numeric(st_area(st_transform(mundo, crs))))
  ap / area_elip(mundo)
}
rz_mundo <- lapply(PROY_MUNDO, function(p) razon_pais(p$crs))

MAPAS$proyecciones_mundo <- geo_proyeccion(
  continentes, PROY_MUNDO, titulo = "El mundo bajo seis proyecciones",
  presupuesto = 450L, verbose = FALSE,
  tissot = list(lon = REJ$lon, lat = REJ$lat), radio_km = 500)

vis <- MAPAS$proyecciones_mundo$vistas
tab <- data.frame(
  nombre = vapply(vis, `[[`, character(1), "nombre"),
  familia = vapply(vis, `[[`, character(1), "familia"),
  omega_med = vapply(vis, `[[`, numeric(1), "omega_med"),
  omega_max = vapply(vis, `[[`, numeric(1), "omega_max"),
  s_med = vapply(vis, `[[`, numeric(1), "s_med"),
  s_min = vapply(vis, `[[`, numeric(1), "s_min"),
  s_max = vapply(vis, `[[`, numeric(1), "s_max"),
  razon_med = vapply(rz_mundo, median, numeric(1)),
  razon_min = vapply(rz_mundo, min, numeric(1)),
  razon_max = vapply(rz_mundo, max, numeric(1)),
  estiramiento = vapply(rz_mundo, function(r) max(r) / min(r), numeric(1)),
  conforme = vapply(vis, `[[`, logical(1), "es_conforme"),
  equivalente = vapply(vis, `[[`, logical(1), "es_equivalente"))

# EL TEOREMA DE TISSOT, comprobado y no citado: ninguna proyección del
# plano puede ser conforme y equivalente a la vez. Si alguna vista
# saliera con las dos banderas, o el medidor está mal o la geometría
# diferencial ha cambiado; las dos merecen que el guion pare.
if (any(tab$conforme & tab$equivalente))
  stop("ANCLA ROTA · una proyección sale conforme Y equivalente: eso es imposible")
N_ANCLAS <- N_ANCLAS + 1L
# Y la contraria: que haya al menos una de cada, o el capítulo no tiene
# los dos ejemplos que promete.
if (!any(tab$conforme) || !any(tab$equivalente))
  stop("las seis proyecciones no incluyen una conforme y una equivalente")

# Mercator: el factor de escala tiene que ser sec(phi). Se comprueba
# contra la fórmula, no contra la fe.
t_merc <- geo_tissot(PROY_MUNDO[[1]]$crs, rep(0, 4), c(0, 30, 45, 60))
ancla(t_merc$a[1], 1, "Mercator: escala 1 en el ecuador", tol = 1e-6)
ancla(t_merc$s[3] / t_merc$a[3]^2, 1, "Mercator: s = k^2 (es conforme)", tol = 1e-6)

D$proyecciones <- list(
  n_paises = nrow(mundo),
  n_dibujados = as.integer(MAPAS$proyecciones_mundo$n),
  dibujado = "continentes disueltos; la razón de área se mide sobre los países sin disolver",
  lat_corte = LAT_CORTE,
  n_indicatrices = nrow(REJ),
  radio_km = 500,
  tabla = list(
    nombre = tab$nombre, familia = tab$familia,
    omega_med_grados = r10(tab$omega_med * 180 / pi),
    omega_max_grados = r10(tab$omega_max * 180 / pi),
    s_med = r10(tab$s_med), s_min = r10(tab$s_min), s_max = r10(tab$s_max),
    razon_med = r10(tab$razon_med), razon_min = r10(tab$razon_min),
    razon_max = r10(tab$razon_max),
    estiramiento = r10(tab$estiramiento),
    conforme = tab$conforme, equivalente = tab$equivalente),
  mercator = list(
    lat = t_merc$lat, escala = r10(t_merc$a), area = r10(t_merc$s),
    sec_phi = r10(1 / cos(t_merc$lat * pi / 180))),
  # Se recalcula desde la tabla, no se hereda de ninguna bandera:
  # una lista que dijera de sí misma «ninguna cumple las dos» no es
  # evidencia de nada (regla 4 de la auditoría).
  ninguna_conforme_y_equivalente = !any(tab$conforme & tab$equivalente))

# =====================================================================
# D. MÓDULO 4 — EPSG en la práctica: 4326, 3857, 3116, 9377
# =====================================================================
message("D · los cuatro códigos EPSG que este curso usa")

mun <- carga_municipios()
ancla(nrow(mun), 1122, "municipios de la capa nacional", tol = 0)
mun_ll <- st_transform(mun, 4326)
area_verdad <- area_elip(mun_ll)          # el elipsoide, no la esfera

EPSG_LISTA <- list(
  list(codigo = 3857L, nombre = "Web Mercator", tipo = "Mercator esférico"),
  list(codigo = 3116L, nombre = "MAGNA-SIRGAS / Colombia Bogotá zone",
       tipo = "transversa de Mercator, k = 1"),
  list(codigo = 9377L, nombre = "MAGNA-SIRGAS 2018 / Origen-Nacional",
       tipo = "transversa de Mercator, k = 0,9992"))

epsg_fila <- function(e) {
  ap <- as.numeric(st_area(st_transform(mun_ll, e$codigo)))
  rz <- ap / area_verdad
  peor <- which.max(abs(rz - 1))
  list(codigo = e$codigo, nombre = e$nombre, tipo = e$tipo,
       razon_med = r10(median(rz)), razon_min = r10(min(rz)), razon_max = r10(max(rz)),
       estiramiento = r10(max(rz) / min(rz)),
       peor_municipio = mun$municipio[peor], peor_dpto = mun$departamento[peor],
       peor_razon = r10(rz[peor]),
       # cuántos municipios se salen del 1 % de error
       n_sobre_1pct = sum(abs(rz - 1) > 0.01))
}
filas <- lapply(EPSG_LISTA, epsg_fila)
names(filas) <- vapply(EPSG_LISTA, function(e) paste0("e", e$codigo), character(1))

# LAS DOS ANCLAS TEÓRICAS DE ESTE MÓDULO, y son exactas:
# una transversa de Mercator es conforme, así que su razón de ÁREA es
# k^2 en el meridiano central y crece hacia los lados. Por tanto el
# MÍNIMO de la razón sobre todo el país tiene que ser exactamente k^2.
ancla(filas$e9377$razon_min, 0.9992^2, "EPSG:9377 · razón de área mínima = k^2", tol = 5e-5)
ancla(filas$e3116$razon_min, 1.0, "EPSG:3116 · razón de área mínima = k^2 = 1", tol = 5e-5)

# 3116 fuera de su zona: se mide el error a lo largo de la longitud,
# porque el argumento del módulo es que 3116 sirve en Bogotá y no en
# Leticia, y eso hay que verlo en una tabla.
cen <- st_coordinates(st_centroid(st_geometry(mun_ll)))
dist_mc_3116 <- abs(cen[, 1] - (-74.0775079166667))
rz_3116 <- as.numeric(st_area(st_transform(mun_ll, 3116))) / area_verdad
rz_9377 <- as.numeric(st_area(st_transform(mun_ll, 9377))) / area_verdad
bandas <- cut(dist_mc_3116, breaks = c(-Inf, 1, 2, 3, 4, 5, Inf),
              labels = c("<1°", "1-2°", "2-3°", "3-4°", "4-5°", ">5°"))
por_banda <- data.frame(
  banda = levels(bandas),
  n = as.integer(table(bandas)),
  err_3116_pct = r10(as.numeric(tapply(100 * abs(rz_3116 - 1), bandas, median))),
  err_9377_pct = r10(as.numeric(tapply(100 * abs(rz_9377 - 1), bandas, median))))

# EL ARCHIPIÉLAGO MANDA, Y CASI PUBLICO LO CONTRARIO.
#
# Iba a escribir que 9377 minimiza el peor caso nacional, que es para lo
# que el IGAC le puso k = 0,9992. Sobre el PAÍS ENTERO el dato dice lo
# contrario: gana 3116, porque el peor caso de los dos es San Andrés y el
# archipiélago está 700 km mar adentro, más cerca del meridiano de 3116
# (-74,08) que del de 9377 (-73). Separando continente e islas se ve lo
# que de verdad pasa, y es mejor material que la frase que yo tenía
# preparada: 9377 gana el PEOR CASO continental, que es su promesa, y
# pierde la MEDIANA, que es lo que cuesta bajar el factor de escala.
insular <- substr(mun$divipola, 1, 2) == "88"
err3116 <- 100 * abs(rz_3116 - 1); err9377 <- 100 * abs(rz_9377 - 1)
tierra_firme <- list(
  n = sum(!insular),
  max_3116_pct = r10(max(err3116[!insular])), max_9377_pct = r10(max(err9377[!insular])),
  med_3116_pct = r10(median(err3116[!insular])), med_9377_pct = r10(median(err9377[!insular])),
  peor_municipio = mun$municipio[!insular][which.max(err9377[!insular])],
  peor_dpto = mun$departamento[!insular][which.max(err9377[!insular])])
archipielago <- list(
  n = sum(insular), municipios = mun$municipio[insular],
  max_3116_pct = r10(max(err3116[insular])), max_9377_pct = r10(max(err9377[insular])))

D$epsg <- list(
  n_municipios = nrow(mun),
  continente = tierra_firme,
  archipielago = archipielago,
  # Las dos lecturas, RECALCULADAS desde las cifras. Escribir «gana 9377»
  # a mano habría dejado en el capítulo una afirmación que su propia
  # tabla desmiente.
  gana_9377_peor_caso_continental =
    as.logical(tierra_firme$max_9377_pct < tierra_firme$max_3116_pct),
  gana_3116_mediana_continental =
    as.logical(tierra_firme$med_3116_pct < tierra_firme$med_9377_pct),
  gana_3116_pais_entero =
    as.logical(max(err3116) < max(err9377)),
  referencia = "área geodésica sobre el elipsoide GRS80 (lwgeom), no sobre la esfera de s2",
  filas = unname(lapply(filas, identity)),
  # el gemelo de 4326: tratar grados como si fueran metros
  bandas = list(banda = por_banda$banda, n = por_banda$n,
                err_3116_pct = por_banda$err_3116_pct,
                err_9377_pct = por_banda$err_9377_pct),
  # cuál gana, RECALCULADO
  gana_9377_lejos = as.logical(por_banda$err_9377_pct[6] < por_banda$err_3116_pct[6]),
  gana_3116_cerca = as.logical(por_banda$err_3116_pct[1] < por_banda$err_9377_pct[1]))

# El mapa: los departamentos coloreados por el error de área de 3116.
dep <- st_read("datos/procesado/colombia_adm1.gpkg", quiet = TRUE)
ancla(nrow(dep), 33, "departamentos de la capa nacional", tol = 0)
dep_ll <- st_transform(dep, 4326)
dep_verdad <- area_elip(dep_ll)
dep_err <- 100 * (as.numeric(st_area(st_transform(dep_ll, 3116))) / dep_verdad - 1)
MAPAS$error_3116 <- geo_poligonos(
  st_transform(dep_ll, 9377), valor = dep_err, n_clases = 5, estilo = "quantile",
  titulo = "Error de área de EPSG:3116 por departamento",
  leyenda = "% de exceso sobre el área geodésica", presupuesto = 900L, verbose = FALSE)

# El CONTORNO del país, no los 33 departamentos: bajo tres proyecciones,
# los departamentos multiplican por tres una geometría cuyo detalle
# interno no aporta nada a la comparación. Lo que hay que ver es cómo
# cambia la SILUETA.
contorno_co <- st_sf(pais = "Colombia", geom = st_union(st_geometry(dep_ll)))
MAPAS$proyecciones_colombia <- geo_proyeccion(
  contorno_co,
  list(list(nombre = "Web Mercator (3857)", crs = 3857, familia = "conforme sobre la esfera"),
       list(nombre = "MAGNA-SIRGAS / Bogotá (3116)", crs = 3116, familia = "conforme"),
       list(nombre = "MAGNA-SIRGAS / Origen Nacional (9377)", crs = 9377, familia = "conforme")),
  titulo = "Colombia bajo tres sistemas", presupuesto = 500L, verbose = FALSE,
  tissot = list(lon = rep(c(-77, -74, -71, -68), each = 4),
                lat = rep(c(-3, 2, 7, 11), times = 4)), radio_km = 120)

# =====================================================================
# E. MÓDULO 5 — st_transform vs. st_set_crs
# =====================================================================
message("E · reproyectar no es reetiquetar")

loc <- st_read("datos/procesado/bogota_localidades.gpkg", quiet = TRUE)
ancla(nrow(loc), 20, "localidades de Bogotá", tol = 0)
loc_bien <- st_transform(loc, 4326)                       # BIEN
loc_mal  <- suppressWarnings(st_set_crs(loc, 4326))       # MAL: reetiquetar

xy_bien <- st_coordinates(loc_bien)[, 1:2]
xy_mal  <- st_coordinates(loc_mal)[, 1:2]
xy_orig <- st_coordinates(loc)[, 1:2]

D$etiquetar <- list(
  n_localidades = nrow(loc),
  crs_original = as.character(st_crs(loc)$input),
  # LO QUE DEFINE LA DIFERENCIA, medido: st_set_crs no mueve NI UNA
  # coordenada, y st_transform las mueve todas.
  set_crs_max_delta = r10(max(abs(xy_mal - xy_orig))),
  transform_max_delta = r10(max(abs(xy_bien - xy_orig))),
  transform_n_movidas = sum(rowSums(abs(xy_bien - xy_orig)) > 0),
  n_vertices = nrow(xy_orig),
  bbox_bien = r10(as.numeric(st_bbox(loc_bien))),
  bbox_mal = r10(as.numeric(st_bbox(loc_mal))),
  # el delator: una «longitud» de casi cinco millones de grados
  lon_absurda = r10(max(abs(as.numeric(st_bbox(loc_mal))[c(1, 3)]))),
  area_bien_km2 = r10(sum(area_elip(loc_bien)) / 1e6),
  area_original_km2 = r10(sum(as.numeric(st_area(loc))) / 1e6))

# El caso que SÍ es silencioso, y hay que decir cuál es: reetiquetar
# 4686 como 4326 no rompe nada, porque MAGNA-SIRGAS y WGS84 coinciden
# a nivel de centímetros. El que rompe es el datum viejo. Que no toda
# etiqueta equivocada haga daño es un resultado, no una excusa.
p_4686 <- pto(BOG[1], BOG[2], 4686)
p_4686_como4326 <- suppressWarnings(st_set_crs(p_4686, 4326))
D$etiquetar$silencioso <- list(
  desde = 4686L, hasta = 4326L,
  desplazamiento_m = r10(dist_elip(st_transform(p_4686, 4326), p_4686_como4326)),
  contraste_desde = 4218L,
  contraste_desplazamiento_m = r10(desp_datum[1]))

# =====================================================================
# F. MÓDULO 6 — Medir sobre la Tierra: s2 contra el elipsoide
# =====================================================================
message("F · medir: la esfera y el elipsoide no dan lo mismo")

col_union <- st_union(st_geometry(mun_ll))
a_esf <- area_esf(col_union); a_eli <- area_elip(col_union)
a_9377 <- as.numeric(st_area(st_transform(col_union, 9377)))
rz_area <- area_esf(mun_ll) / area_elip(mun_ll)

# distancias: 300 pares de estaciones, esfera contra elipsoide
d_e_esf <- dist_esf(st_geometry(est)[pares[, 1]], st_geometry(est)[pares[, 2]])
dif_d <- d_real - d_e_esf

D$medir <- list(
  colombia = list(
    area_esfera_km2 = r10(a_esf / 1e6),
    area_elipsoide_km2 = r10(a_eli / 1e6),
    area_9377_km2 = r10(a_9377 / 1e6),
    dif_esfera_km2 = r10((a_esf - a_eli) / 1e6),
    dif_esfera_pct = r10(100 * (a_esf - a_eli) / a_eli),
    dif_9377_pct = r10(100 * (a_9377 - a_eli) / a_eli)),
  municipios = list(
    n = nrow(mun),
    razon_med = r10(median(rz_area)), razon_min = r10(min(rz_area)),
    razon_max = r10(max(rz_area)),
    # cuántos municipios «caben» dentro del error de la esfera
    equivalente_a_municipios = sum(sort(area_elip(mun_ll)) <= (a_esf - a_eli)) ),
  distancias = list(
    n_pares = nrow(pares),
    dif_med_m = r10(median(dif_d)), dif_max_m = r10(max(abs(dif_d))),
    dif_pct_med = r10(median(100 * dif_d / d_real)),
    bogota_oslo_dif_m = r10(d_eli - d_esf)))

# LA DISCREPANCIA DECLARADA. El auditor lee esta lista: una discrepancia
# declarada es material didáctico, una sin declarar es un fallo.
D$discrepancias <- list(
  list(que = "st_area con s2 y sin s2 no dan el mismo número",
       motivo = paste("s2 integra sobre una ESFERA y lwgeom sobre el ELIPSOIDE.",
                      "Sobre Colombia la esfera infla el área un",
                      sprintf("%.5f %%", 100 * (a_esf - a_eli) / a_eli),
                      "—", sprintf("%.0f km2", (a_esf - a_eli) / 1e6),
                      "—, más que la suma de los municipios más pequeños."),
       r = r10(a_eli / 1e6), python = r10(a_esf / 1e6),
       donde = "capítulo 2, módulo 6",
       como_recuperar = "sf_use_s2(FALSE) mide sobre el elipsoide; GeoPandas .to_crs(9377).area proyecta"),
  list(que = "Mollweide sale con s distinto de 1 aunque es equivalente",
       motivo = paste("PROJ implementa Mollweide sobre la ESFERA. Medida contra el",
                      "elipsoide, su escala de área se desvía hasta",
                      sprintf("%.5f", max(abs(tab$s_max[3] - 1), abs(tab$s_min[3] - 1))),
                      "· es la misma brecha esfera/elipsoide del módulo 6, no un",
                      "defecto de la proyección. Equal Earth, que PROJ sí resuelve",
                      "sobre el elipsoide, da s = 1 exacto."),
       r = r10(tab$s_med[3]), python = r10(tab$s_med[4]),
       donde = "capítulo 2, módulo 3",
       como_recuperar = "comparar contra la esfera autálica en vez de contra el elipsoide"))

# =====================================================================
# G. MÓDULO 7 — Formatos vectoriales, medidos y no citados
# =====================================================================
message("G · el shapefile y sus limitaciones, medidas de verdad")

tmp <- file.path(tempdir(), "fmt"); dir.create(tmp, showWarnings = FALSE)
unlink(list.files(tmp, full.names = TRUE))
# Una muestra con acentos DE VERDAD: el .dbf no declara su codificación
# si no se le fuerza un .cpg, y los acentos son el canario.
con_tilde <- grep("[áéíóúñ]", mun$municipio)
sel <- sort(unique(c(head(con_tilde, 40), setdiff(seq_len(nrow(mun)), con_tilde)[1:20])))
mu_s <- mun[sel, c("divipola", "municipio", "departamento", "tipo", "desercion")]
mu_s$desercion_escolar_2024 <- r10(mu_s$desercion)
mu_s$nombre_del_municipio_largo <- mu_s$municipio
mu_s$es_area_no_municipalizada <- mu_s$tipo != "Municipio"
mu_s$fecha_de_corte <- as.Date("2024-06-30")
nombres_antes <- setdiff(names(mu_s), attr(mu_s, "sf_column"))

suppressWarnings(st_write(mu_s, file.path(tmp, "prueba.shp"), quiet = TRUE, delete_dsn = TRUE))
st_write(mu_s, file.path(tmp, "prueba.gpkg"), quiet = TRUE, delete_dsn = TRUE)
st_write(mu_s, file.path(tmp, "prueba.geojson"), quiet = TRUE, delete_dsn = TRUE)
re_shp <- st_read(file.path(tmp, "prueba.shp"), quiet = TRUE)
re_gpkg <- st_read(file.path(tmp, "prueba.gpkg"), quiet = TRUE)

nombres_despues <- setdiff(names(re_shp), attr(re_shp, "sf_column"))
largos <- nombres_antes[nchar(nombres_antes) > 10]
arch_shp <- list.files(tmp, pattern = "^prueba\\.(shp|shx|dbf|prj|cpg)$")
tam_shp <- sum(file.size(file.path(tmp, arch_shp)))

# Los tipos: qué sobrevive al viaje y qué no.
tipo_de <- function(x, nm) if (nm %in% names(x)) class(x[[nm]])[1] else NA_character_
nm_fecha_shp <- nombres_despues[grepl("^f", nombres_despues)][1]
nm_logi_shp <- nombres_despues[grepl("^es_", nombres_despues)][1]

D$formatos <- list(
  n_rasgos = nrow(mu_s),
  shapefile = list(
    n_archivos = length(arch_shp), archivos = arch_shp,
    tiene_cpg = "prueba.cpg" %in% arch_shp,
    bytes = as.numeric(tam_shp),
    n_campos = length(nombres_antes),
    n_campos_largos = length(largos),
    ejemplos_antes = head(largos, 5),
    ejemplos_despues = head(nombres_despues[match(head(largos, 5), nombres_antes)], 5),
    # el nombre no se TRUNCA: GDAL le quita vocales para desambiguar, que
    # es peor, porque el resultado ya no se reconoce a ojo
    truncado_simple = as.logical(all(head(nombres_despues[match(head(largos, 5), nombres_antes)], 5) ==
                                     substr(head(largos, 5), 1, 10))),
    tipo_fecha_antes = "Date",
    tipo_fecha_despues = tipo_de(re_shp, nm_fecha_shp),
    tipo_logico_antes = "logical",
    tipo_logico_despues = tipo_de(re_shp, nm_logi_shp),
    n_con_tilde = length(intersect(sel, con_tilde)),
    tildes_sobreviven = sum(mu_s$municipio == re_shp[[nombres_despues[match("municipio", nombres_antes)]]])),
  gpkg = list(
    bytes = as.numeric(file.size(file.path(tmp, "prueba.gpkg"))),
    n_campos = length(setdiff(names(re_gpkg), attr(re_gpkg, "sf_column"))),
    nombres_intactos = as.logical(all(nombres_antes %in% names(re_gpkg))),
    tipo_fecha_despues = tipo_de(re_gpkg, "fecha_de_corte"),
    tipo_logico_despues = tipo_de(re_gpkg, "es_area_no_municipalizada")),
  geojson = list(
    bytes = as.numeric(file.size(file.path(tmp, "prueba.geojson")))),
  # el país entero, para que la comparación no dependa de una muestra
  pais = list(
    gpkg_mb = r10(file.size("datos/procesado/colombia_adm2.gpkg") / 1024^2),
    geojson_mb = r10(file.size("datos/crudo/COL_ADM2.geojson") / 1024^2),
    razon = r10(file.size("datos/crudo/COL_ADM2.geojson") /
                file.size("datos/procesado/colombia_adm2.gpkg"))))
D$formatos$geojson$razon_sobre_shp <-
  r10(D$formatos$geojson$bytes / D$formatos$shapefile$bytes)
# La del GeoPackage faltaba, y el ensamblador la dividía a mano en la prosa
# —la única cifra del capítulo que no salía de aquí—. Encontrada en T2.2,
# al triar las cifras de pocos decimales de los tres capítulos.
D$formatos$gpkg$razon_sobre_shp <-
  r10(D$formatos$gpkg$bytes / D$formatos$shapefile$bytes)

# El shapefile TIENE que perder algo, o la comprobación no comprueba nada.
if (D$formatos$shapefile$n_campos_largos == 0)
  stop("el caso de prueba del shapefile no tiene ningún campo de más de 10 caracteres")

# =====================================================================
# H. MÓDULO 8 — De un CSV a un objeto sf, y la trampa del orden
# =====================================================================
message("H · lon/lat invertidos: dónde aterrizan las 361 estaciones")

ancla(n_est, 361, "estaciones del IDEAM", tol = 0)
inv <- st_as_sf(data.frame(lon = xy_est[, 2], lat = xy_est[, 1]),
                coords = c("lon", "lat"), crs = 4326)
d_inv <- dist_elip(st_geometry(est), st_geometry(inv))

s2_antes <- suppressMessages(sf_use_s2(FALSE))
donde <- suppressWarnings(suppressMessages(
  st_join(inv, world[, c("name_long", "continent")], join = st_within)))
suppressMessages(sf_use_s2(s2_antes))
tb_donde <- table(ifelse(is.na(donde$name_long), "(mar abierto)", donde$name_long))

D$csv_sf <- list(
  n = n_est,
  centroide_bien = r10(colMeans(xy_est)),
  centroide_mal = r10(rev(colMeans(xy_est))),
  desplazamiento_km_med = r10(mean(d_inv) / 1000),
  desplazamiento_km_min = r10(min(d_inv) / 1000),
  desplazamiento_km_max = r10(max(d_inv) / 1000),
  caja_bien = r10(as.numeric(st_bbox(est))),
  caja_mal = r10(as.numeric(st_bbox(inv))),
  destino = list(nombre = names(tb_donde), n = as.integer(tb_donde)),
  n_en_tierra = sum(!is.na(donde$name_long)),
  n_en_mar = sum(is.na(donde$name_long)),
  # La cifra que hace el argumento: NINGUNA cae en Colombia, y aun así
  # `st_as_sf` no dio ni un aviso.
  n_en_colombia = sum(donde$name_long == "Colombia", na.rm = TRUE),
  hubo_aviso = FALSE)

# La otra trampa del CSV, y esta es de aquí: el separador decimal. Un
# CSV exportado en configuración regional española trae la coma, y
# `read.csv` lo lee como TEXTO sin quejarse.
csv_coma <- data.frame(estacion = seq_len(5),
                       lon = sub("\\.", ",", sprintf("%.5f", xy_est[1:5, 1])),
                       lat = sub("\\.", ",", sprintf("%.5f", xy_est[1:5, 2])))
D$csv_sf$coma_decimal <- list(
  ejemplo_lon = csv_coma$lon[1],
  clase_leida = class(csv_coma$lon),
  as_numeric_da = as.character(suppressWarnings(as.numeric(csv_coma$lon[1]))),
  n_na = sum(is.na(suppressWarnings(as.numeric(csv_coma$lon)))))

# Mapa: el mundo de fondo y los dos enjambres.
#
# Todo el trabajo de geometría de la costa va con s2 APAGADO. Simplificar
# rompe la topología esférica —«Loop 86: Edge 0 is degenerate»— y s2 se
# niega, con razón; para dibujar una costa de fondo la topología esférica
# no aporta nada y el plano de GEOS sí.
s2_antes <- suppressMessages(sf_use_s2(FALSE))
costa <- st_make_valid(st_union(st_geometry(world)))
# dTolerance en GRADOS: sf avisa de que no es lo correcto para lon/lat, y
# tiene razón en general. Aquí sí lo es: esto no mide nada, es la costa
# de fondo de un mapamundi, y el grado es justo la unidad del lienzo.
costa <- st_make_valid(suppressWarnings(
  st_simplify(costa, dTolerance = 1.5, preserveTopology = TRUE)))
anillos <- suppressWarnings(st_cast(st_cast(costa, "POLYGON"), "LINESTRING"))
suppressMessages(sf_use_s2(s2_antes))
# `lineas` de geo_puntos espera una LISTA de matrices, no un sfc.
lineas_costa <- lapply(anillos, function(g) unclass(st_coordinates(g)[, 1:2, drop = FALSE]))
lineas_costa <- Filter(function(m) nrow(m) >= 4, lineas_costa)

MAPAS$invertidos <- geo_puntos(
  st_coordinates(inv),
  ventana = c(-180, -90, 180, 90),
  lineas = lineas_costa,
  puntos2 = xy_est,
  titulo = "Las 361 estaciones del IDEAM, con la longitud y la latitud cambiadas de sitio",
  leyenda = "rombo = posición correcta · punto = con lon/lat invertidos")

# =====================================================================
# I. MÓDULO 9 — Error posicional, y quién lo paga
# =====================================================================
message("I · degradar la posición a propósito, y medir el sesgo")

cole <- st_read("datos/procesado/bogota_colegios.gpkg", quiet = TRUE)
ancla(nrow(cole), 2209, "sedes educativas de Bogotá", tol = 0)
cole_ll <- st_transform(cole, 4326)
xy_col <- st_coordinates(cole_ll)
xy_col_m <- st_coordinates(cole)
verdad_loc <- st_join(cole["dane_sede"], loc["cod_loca"], join = st_within)$cod_loca

reasigna <- function(g) {
  nuevo <- st_join(g, loc["cod_loca"], join = st_within)$cod_loca
  (is.na(verdad_loc) != is.na(nuevo)) |
    (!is.na(verdad_loc) & !is.na(nuevo) & verdad_loc != nuevo)
}

# (a) redondeo de las coordenadas geográficas
redondeos <- lapply(c(4L, 3L, 2L), function(dg) {
  p <- st_transform(st_as_sf(data.frame(x = round(xy_col[, 1], dg),
                                        y = round(xy_col[, 2], dg)),
                             coords = c("x", "y"), crs = 4326), st_crs(cole))
  d <- dist_elip(st_geometry(cole_ll), st_transform(st_geometry(p), 4326))
  cam <- reasigna(p)
  list(decimales = dg,
       n_posiciones = length(unique(paste(round(xy_col[, 1], dg), round(xy_col[, 2], dg)))),
       desplaz_med_m = r10(mean(d)), desplaz_max_m = r10(max(d)),
       n_cambian = sum(cam), pct_cambian = r10(100 * mean(cam)))
})

# (b) ruido gaussiano en METROS, que es como se comporta de verdad un
# geocodificador: no redondea, se equivoca.
set.seed(SEM_RUIDO)
ruidos <- lapply(c(50, 150, 500), function(s) {
  p <- st_as_sf(data.frame(x = xy_col_m[, 1] + rnorm(nrow(xy_col_m), 0, s),
                           y = xy_col_m[, 2] + rnorm(nrow(xy_col_m), 0, s)),
                coords = c("x", "y"), crs = st_crs(cole))
  d <- as.numeric(st_distance(st_geometry(cole), st_geometry(p), by_element = TRUE))
  cam <- reasigna(p)
  list(sigma_m = s, desplaz_med_m = r10(mean(d)), desplaz_max_m = r10(max(d)),
       n_cambian = sum(cam), pct_cambian = r10(100 * mean(cam)), cambia = cam)
})

# EL SESGO: el mismo error no cuesta lo mismo en toda la ciudad, y lo
# que lo explica NO es la riqueza sino la GEOMETRÍA de la unidad. Se
# mide contra perímetro/área, que es lo que la teoría predice: la
# probabilidad de que un punto cruce el borde escala con perímetro × σ
# repartido sobre el área.
#
# CON RÉPLICAS, Y NO CON UNA. Una sola realización del ruido daba
# correlaciones de 0,38 y de 0,72 según la semilla, y localidades con
# «20,00 %» que eran cuatro sedes de veinte. Eso no es una medida, es
# una anécdota. Con N_REP realizaciones la tasa de cada localidad es un
# promedio con su error de Monte Carlo publicado, igual que la cobertura
# del módulo 4 del capítulo 1.
N_REP <- 200L
loc$perim_km <- as.numeric(st_length(st_cast(st_geometry(loc), "MULTILINESTRING"))) / 1000
loc$area_km2 <- as.numeric(st_area(loc)) / 1e6
loc$compacidad <- loc$perim_km / loc$area_km2

set.seed(SEM_RUIDO + 1L)
reps <- vapply(seq_len(N_REP), function(k) {
  pk <- st_as_sf(data.frame(x = xy_col_m[, 1] + rnorm(nrow(xy_col_m), 0, 150),
                            y = xy_col_m[, 2] + rnorm(nrow(xy_col_m), 0, 150)),
                 coords = c("x", "y"), crs = st_crs(cole))
  as.numeric(reasigna(pk))
}, numeric(nrow(cole)))                     # sedes x réplicas

tasa_sede <- rowMeans(reps)                 # P(cambiar) de cada sede
agg <- aggregate(tasa_sede, list(cod = verdad_loc), function(z) c(n = length(z), p = mean(z)))
agg <- data.frame(cod = agg$cod, n = as.integer(agg$x[, 1]), tasa = agg$x[, 2])
agg <- merge(agg, st_drop_geometry(loc[, c("cod_loca", "localidad", "perim_km",
                                           "area_km2", "compacidad")]),
             by.x = "cod", by.y = "cod_loca")
# El error de Monte Carlo de la tasa GLOBAL, publicado y no escondido.
tasa_global_rep <- colMeans(reps)
emc_global <- sd(tasa_global_rep) / sqrt(N_REP)
agg_f <- agg[agg$n >= 30, ]
agg_f <- agg_f[order(-agg_f$tasa), ]

# Por estrato, que es la lectura que un lector espera y que el dato NO
# sostiene. Se publica igualmente: decir que el patrón esperado no está
# es un resultado.
est_col <- suppressWarnings(as.integer(cole$estrato))
agg_e <- aggregate(tasa_sede, list(e = est_col), function(z) c(n = length(z), p = 100 * mean(z)))
agg_e <- data.frame(estrato = agg_e$e, n = as.integer(agg_e$x[, 1]),
                    pct = r10(agg_e$x[, 2]))

D$posicional <- list(
  n_sedes = nrow(cole), n_localidades = nrow(loc),
  semilla_ruido = SEM_RUIDO,
  redondeos = lapply(redondeos, function(r) r[names(r) != "cambia"]),
  ruidos = lapply(ruidos, function(r) r[names(r) != "cambia"]),
  # El ancla externa: la fuente del MEN que T0.4 descartó traía las
  # coordenadas con DOS decimales, y allí 2 403 sedes de Bogotá
  # colapsaban en 398 posiciones. Degradar nuestro dato bueno a dos
  # decimales tiene que reproducir esa densidad.
  men_descartada = list(
    fuente = "x5ay-984n (MEN, sedes nacionales) — descartada en T0.4",
    n_sedes = 2403L, n_posiciones = 398L,
    sedes_por_posicion = r10(2403 / 398)),
  sesgo = list(
    sigma_m = 150, n_replicas = N_REP,
    tasa_global_pct = r10(100 * mean(tasa_sede)),
    emc_global_pct = r10(100 * emc_global),
    n_localidades_con_30 = nrow(agg_f),
    localidad = agg_f$localidad, n = agg_f$n,
    tasa_pct = r10(100 * agg_f$tasa),
    area_km2 = r10(agg_f$area_km2), compacidad = r10(agg_f$compacidad),
    corr_pearson = r10(cor(agg_f$tasa, agg_f$compacidad)),
    corr_spearman = r10(cor(agg_f$tasa, agg_f$compacidad, method = "spearman")),
    tasa_min_pct = r10(100 * min(agg_f$tasa)), tasa_max_pct = r10(100 * max(agg_f$tasa)),
    razon_max_min = r10(max(agg_f$tasa) / min(agg_f$tasa)),
    peor = agg_f$localidad[1], mejor = agg_f$localidad[nrow(agg_f)]),
  por_estrato = list(estrato = agg_e$estrato, n = agg_e$n, pct = agg_e$pct,
                     monotono_en_estrato = as.logical(
                       all(diff(agg_e$pct) >= 0) || all(diff(agg_e$pct) <= 0))))
D$posicional$sedes_por_posicion_2dec <-
  r10(nrow(cole) / redondeos[[3]]$n_posiciones)

# Mapas del módulo 9
# Las posiciones redondeadas se guardan SIN REPETIR: son 360 distintas
# para 2 209 sedes, y ese colapso es justo lo que el mapa enseña. Guardar
# 2 209 copias de 360 posiciones costaría 15 KB para no dibujar ni un
# píxel más.
xy_red <- unique(cbind(round(xy_col[, 1], 2), round(xy_col[, 2], 2)))
# Y de las posiciones REALES viaja una muestra declarada, no las 2 209: a
# la escala de la ciudad 2 209 rombos son una mancha, y costaban 15 KB de
# los 120 del capítulo. La muestra es reproducible y el JSON dice cuántas
# son, para que nadie tenga que deducirlo del dibujo.
N_MUESTRA_MAPA <- 700L
set.seed(SEMILLA)
i_muestra <- sort(sample(nrow(xy_col), N_MUESTRA_MAPA))
MAPAS$degradado <- geo_puntos(
  xy_red,
  ventana = st_bbox(cole_ll),
  puntos2 = xy_col[i_muestra, ],
  titulo = "Las 2 209 sedes con la coordenada redondeada a dos decimales",
  leyenda = paste0("punto = una de las ", nrow(xy_red),
                   " posiciones que quedan · rombo = ", N_MUESTRA_MAPA,
                   " posiciones reales (muestra)"))
D$posicional$n_muestra_mapa <- N_MUESTRA_MAPA
D$posicional$n_posiciones_2dec <- nrow(xy_red)
loc_tasa <- merge(loc, data.frame(cod_loca = agg$cod, tasa = 100 * agg$tasa),
                  by = "cod_loca", all.x = TRUE)
MAPAS$sesgo_localidades <- geo_poligonos(
  loc_tasa, valor = ifelse(is.na(loc_tasa$tasa), 0, loc_tasa$tasa),
  n_clases = 5, estilo = "quantile",
  titulo = "Sedes que cambian de localidad con 150 m de error (200 réplicas)",
  leyenda = "% de las sedes de la localidad", presupuesto = 1000L, verbose = FALSE)

# =====================================================================
# J. MÓDULO 10 — Validación topológica y DE-9IM
# =====================================================================
message("J · topología: lo que st_is_valid caza y lo que st_area calla")

# El lazo. Es el ejemplo canónico y aquí importa por una razón concreta:
# `st_area` sobre él devuelve CERO sin quejarse. Es el modo de fallo
# dominante de este proyecto —la operación que devuelve un valor
# plausible en vez de fallar— en tres líneas de código.
lazo <- st_sfc(st_polygon(list(rbind(c(0, 0), c(2, 2), c(2, 0), c(0, 2), c(0, 0)))))
lazo_ok <- st_make_valid(lazo)
ancla(as.numeric(st_area(lazo)), 0, "el área del lazo inválido es 0", tol = 1e-12)
ancla(sum(as.numeric(st_area(lazo_ok))), 2, "el área tras st_make_valid es 2", tol = 1e-9)

valid_mun <- st_is_valid(mun)
crudo_dep <- st_read("datos/crudo/COL_ADM1.geojson", quiet = TRUE)
valid_crudo <- st_is_valid(crudo_dep)

# DE-9IM: las cinco relaciones canónicas, con su matriz calculada.
A <- st_sfc(st_polygon(list(rbind(c(0, 0), c(4, 0), c(4, 4), c(0, 4), c(0, 0)))))
CASOS <- list(
  disjuntos = rbind(c(6, 6), c(8, 6), c(8, 8), c(6, 8), c(6, 6)),
  tocan     = rbind(c(4, 0), c(6, 0), c(6, 4), c(4, 4), c(4, 0)),
  solapan   = rbind(c(2, 2), c(6, 2), c(6, 6), c(2, 6), c(2, 2)),
  contiene  = rbind(c(1, 1), c(3, 1), c(3, 3), c(1, 3), c(1, 1)),
  iguales   = rbind(c(0, 0), c(4, 0), c(4, 4), c(0, 4), c(0, 0)))
de9im <- vapply(CASOS, function(m)
  st_relate(A, st_sfc(st_polygon(list(m))))[1], character(1))
# Las cinco matrices están publicadas en la especificación OGC Simple
# Features. Se anclan como CADENAS, que es lo que son.
ESPERADO <- c(disjuntos = "FF2FF1212", tocan = "FF2F11212", solapan = "212101212",
              contiene = "212FF1FF2", iguales = "2FFF1FFF2")
for (nm in names(ESPERADO)) {
  N_ANCLAS <- N_ANCLAS + 1L
  if (de9im[[nm]] != ESPERADO[[nm]])
    stop(sprintf("ANCLA ROTA · DE-9IM de «%s»: sale %s y la OGC publica %s",
                 nm, de9im[[nm]], ESPERADO[[nm]]))
}

# El buffer que cambia de tamaño según el CRS: mismo radio nominal,
# distinta superficie real.
b_ll <- st_buffer(st_transform(pto(BOG[1], BOG[2]), 4326), 0.01)   # 0,01 grados
b_9377 <- st_buffer(st_transform(pto(BOG[1], BOG[2]), 9377), 1000) # 1 000 m
b_3857 <- st_buffer(st_transform(pto(BOG[1], BOG[2]), 3857), 1000)

D$topologia <- list(
  lazo = list(area_antes = 0, area_despues = r10(sum(as.numeric(st_area(lazo_ok)))),
              valido_antes = FALSE,
              razon = as.character(st_is_valid(lazo, reason = TRUE)),
              tipo_despues = as.character(st_geometry_type(lazo_ok))[1],
              n_partes_despues = length(st_geometry(st_cast(lazo_ok, "POLYGON")))),
  municipios = list(n = nrow(mun), n_invalidos = sum(!valid_mun, na.rm = TRUE)),
  crudo = list(n = nrow(crudo_dep), n_invalidos = sum(!valid_crudo, na.rm = TRUE)),
  de9im = list(caso = names(de9im), matriz = unname(de9im),
               predicado = c("st_disjoint", "st_touches", "st_overlaps",
                             "st_contains", "st_equals")),
  buffer = list(
    grados_area_km2 = r10(area_elip(b_ll) / 1e6),
    m9377_area_km2 = r10(as.numeric(st_area(b_9377)) / 1e6),
    m3857_area_km2 = r10(as.numeric(st_area(b_3857)) / 1e6),
    m3857_area_real_km2 = r10(area_elip(st_transform(b_3857, 4326)) / 1e6),
    # el buffer de 1 000 m en 3857 NO mide 1 000 m sobre el terreno
    m3857_radio_real_m = r10(sqrt(area_elip(st_transform(b_3857, 4326)) / pi))))

# =====================================================================
# K. MÓDULO 11 — Ingeniería de datos geoespaciales
# =====================================================================
message("K · índices espaciales y geohash")

# --- El índice: cuántos pares deja de mirar ---------------------------
cajas <- t(vapply(st_geometry(loc), function(g) as.numeric(st_bbox(g)), numeric(4)))
cand <- sum(vapply(seq_len(nrow(xy_col_m)), function(i)
  sum(xy_col_m[i, 1] >= cajas[, 1] & xy_col_m[i, 1] <= cajas[, 3] &
      xy_col_m[i, 2] >= cajas[, 2] & xy_col_m[i, 2] <= cajas[, 4]), integer(1)))
exactos <- sum(lengths(st_within(cole, loc)))

# --- Geohash, implementado aquí y verificado por decodificación -------
#
# NO se instala `h3jsr` (decisión de Javier, 2026-08-04): el geohash es
# un algoritmo público de cuarenta líneas y así el capítulo puede
# ENSEÑARLO en vez de invocarlo. Lo que no se puede es creerse una
# cadena escrita de memoria: la implementación se verifica contra los
# dos vectores canónicos publicados Y, sobre todo, DECODIFICANDO — cada
# punto tiene que caer dentro de la caja de su propia celda. La primera
# versión de esto traía seis «vectores canónicos» y tres eran inventados.
B32 <- strsplit("0123456789bcdefghjkmnpqrstuvwxyz", "")[[1]]
geohash <- function(lon, lat, n = 8L) {
  n <- as.integer(n)
  vapply(seq_along(lon), function(i) {
    la <- c(-90, 90); lo <- c(-180, 180); bits <- integer(n * 5L); par <- TRUE
    for (k in seq_len(n * 5L)) {
      if (par) { mid <- (lo[1] + lo[2]) / 2
        if (lon[i] >= mid) { bits[k] <- 1L; lo[1] <- mid } else lo[2] <- mid
      } else { mid <- (la[1] + la[2]) / 2
        if (lat[i] >= mid) { bits[k] <- 1L; la[1] <- mid } else la[2] <- mid }
      par <- !par
    }
    paste(B32[vapply(seq_len(n), function(j)
      as.integer(sum(bits[((j - 1L) * 5L + 1L):(j * 5L)] * c(16L, 8L, 4L, 2L, 1L))) + 1L,
      integer(1))], collapse = "")
  }, character(1))
}
geohash_caja <- function(g) {
  idx <- match(strsplit(g, "")[[1]], B32) - 1L
  bits <- unlist(lapply(idx, function(v) as.integer(intToBits(v))[5:1]))
  la <- c(-90, 90); lo <- c(-180, 180); par <- TRUE
  for (b in bits) {
    if (par) { mid <- (lo[1] + lo[2]) / 2; if (b == 1L) lo[1] <- mid else lo[2] <- mid }
    else     { mid <- (la[1] + la[2]) / 2; if (b == 1L) la[1] <- mid else la[2] <- mid }
    par <- !par
  }
  c(lo[1], lo[2], la[1], la[2])
}
# Los DOS vectores que sí están publicados y se pueden citar.
N_ANCLAS <- N_ANCLAS + 2L
if (geohash(-5.6, 42.6, 5) != "ezs42")
  stop("ANCLA ROTA · geohash de (-5,6 · 42,6) debería ser ezs42")
if (geohash(-122.4194, 37.7749, 8) != "9q8yyk8y")
  stop("ANCLA ROTA · geohash de San Francisco debería ser 9q8yyk8y")

gh <- lapply(4:8, function(L) {
  g <- geohash(xy_col[, 1], xy_col[, 2], L)
  cajas_g <- lapply(unique(g), geohash_caja)
  names(cajas_g) <- unique(g)
  dentro <- vapply(seq_along(g), function(i) {
    b <- cajas_g[[g[i]]]
    xy_col[i, 1] >= b[1] && xy_col[i, 1] <= b[2] &&
      xy_col[i, 2] >= b[3] && xy_col[i, 2] <= b[4] }, logical(1))
  anchos <- vapply(cajas_g, function(b) (b[2] - b[1]) * 111.320 * cos(4.65 * pi / 180), numeric(1))
  altos <- vapply(cajas_g, function(b) (b[4] - b[3]) * 110.574, numeric(1))
  list(longitud = L, n_celdas = length(unique(g)), n_dentro = sum(dentro),
       celda_ancho_km = r10(mean(anchos)), celda_alto_km = r10(mean(altos)), g = g)
})
# La verificación que de verdad prueba la implementación.
n_dentro_total <- sum(vapply(gh, `[[`, integer(1), "n_dentro"))
N_ANCLAS <- N_ANCLAS + 1L
if (n_dentro_total != 5L * nrow(cole))
  stop(sprintf("ANCLA ROTA · round-trip del geohash: %d de %d puntos dentro de su celda",
               n_dentro_total, 5L * nrow(cole)))

# El defecto que importa: proximidad en geohash != proximidad en el espacio
Dm <- as.matrix(st_distance(cole)); diag(Dm) <- Inf
vecino <- apply(Dm, 1, which.min)
d_vecino <- Dm[cbind(seq_len(nrow(Dm)), vecino)]
frontera <- lapply(gh, function(x)
  list(longitud = x$longitud,
       n_distinto = sum(x$g != x$g[vecino]),
       pct_distinto = r10(100 * mean(x$g != x$g[vecino]))))

D$ingenieria <- list(
  join = list(n_puntos = nrow(cole), n_poligonos = nrow(loc),
              pares_fuerza_bruta = nrow(cole) * nrow(loc),
              pares_tras_cajas = cand,
              reduccion = r10(nrow(cole) * nrow(loc) / cand),
              aciertos_exactos = exactos,
              sin_poligono = nrow(cole) - exactos),
  geohash = list(
    alfabeto = "0123456789bcdefghjkmnpqrstuvwxyz",
    base = 32L,
    vectores_canonicos = list(
      list(lon = -5.6, lat = 42.6, esperado = "ezs42", obtenido = geohash(-5.6, 42.6, 5)),
      list(lon = -122.4194, lat = 37.7749, esperado = "9q8yyk8y",
           obtenido = geohash(-122.4194, 37.7749, 8))),
    round_trip = list(n_puntos = 5L * nrow(cole), n_dentro = n_dentro_total,
                      completo = n_dentro_total == 5L * nrow(cole)),
    niveles = lapply(gh, function(x) x[names(x) != "g"]),
    frontera = frontera,
    d_vecino_mediana_m = r10(median(d_vecino)),
    d_vecino_media_m = r10(mean(d_vecino))))

# Mapa: las celdas de geohash de longitud 6 sobre Bogotá, con su conteo.
g6 <- gh[[2]]$g   # longitud 5: 50 celdas en vez de 503
cel_unicas <- unique(g6)
cel_poly <- st_sfc(lapply(cel_unicas, function(s) {
  b <- geohash_caja(s)
  st_polygon(list(rbind(c(b[1], b[3]), c(b[2], b[3]), c(b[2], b[4]),
                        c(b[1], b[4]), c(b[1], b[3]))))
}), crs = 4326)
cel_sf <- st_sf(celda = cel_unicas, n = as.integer(table(g6)[cel_unicas]),
                geom = st_transform(cel_poly, 9377))
MAPAS$geohash <- geo_poligonos(
  cel_sf, valor = cel_sf$n, n_clases = 5, estilo = "quantile",
  titulo = "Celdas de geohash de longitud 5 sobre las sedes de Bogotá",
  leyenda = "sedes por celda", presupuesto = 1500L, verbose = FALSE)

# =====================================================================
# L. Coherencia entre módulos, antes de escribir nada
# =====================================================================
message("L · coherencia entre módulos")

# El módulo 3 y el módulo 6 tienen que contar la MISMA historia sobre la
# esfera: la desviación de Mollweide respecto de 1 y el exceso de área de
# s2 sobre Colombia son el mismo fenómeno, y si difirieran en un orden de
# magnitud es que uno de los dos está mal.
desv_moll <- max(abs(tab$s_max[3] - 1), abs(tab$s_min[3] - 1))
exceso_s2 <- abs(D$medir$colombia$dif_esfera_pct) / 100
if (desv_moll / exceso_s2 > 5 || exceso_s2 / desv_moll > 5)
  stop(sprintf(paste("INCOHERENCIA · la brecha esfera/elipsoide sale %.5f en el modulo 3",
                     "y %.5f en el 6: son el mismo fenomeno y no pueden diferir tanto"),
               desv_moll, exceso_s2))

# El módulo 9 tiene que reproducir la densidad de la fuente descartada.
razon_men <- D$posicional$men_descartada$sedes_por_posicion
razon_nuestra <- D$posicional$sedes_por_posicion_2dec
if (abs(razon_nuestra / razon_men - 1) > 0.25)
  stop(sprintf(paste("INCOHERENCIA · degradar a 2 decimales da %.4f sedes por posicion",
                     "y la fuente del MEN daba %.4f"), razon_nuestra, razon_men))

# =====================================================================
# M. Escritura
# =====================================================================
message("M · escritura")

D$meta <- list(
  capitulo = 2L,
  titulo = "SIG, sistemas de referencia y georreferenciación con sf",
  semana = "2-3",
  generado = format(Sys.Date()),
  semilla = SEMILLA,
  r = R.version.string,
  gdal = as.character(sf_extSoftVersion()[["GDAL"]]),
  geos = as.character(sf_extSoftVersion()[["GEOS"]]),
  proj = as.character(sf_extSoftVersion()[["PROJ"]]),
  anclas_verificadas = N_ANCLAS)

# Los CSV que las pestañas de Python necesitan para partir del MISMO
# dato. Sin ellos el bloque de Python del capítulo no podría reproducir
# ninguna cifra de la prosa, y las pestañas serían decorativas.
write.csv(data.frame(
  estacion = seq_len(n_est), lon = r10(xy_est[, 1]), lat = r10(xy_est[, 2])),
  file.path(SALIDAS, "cap2_estaciones.csv"), row.names = FALSE, fileEncoding = "UTF-8")

write.csv(data.frame(
  dane_sede = cole$dane_sede, localidad = cole$localidad,
  estrato = cole$estrato,
  lon = r10(xy_col[, 1]), lat = r10(xy_col[, 2]),
  x_9377 = r10(xy_col_m[, 1]), y_9377 = r10(xy_col_m[, 2])),
  file.path(SALIDAS, "cap2_sedes.csv"), row.names = FALSE, fileEncoding = "UTF-8")

write.csv(data.frame(
  divipola = mun$divipola, municipio = mun$municipio,
  departamento = mun$departamento,
  area_elipsoide_km2 = r10(area_verdad / 1e6),
  area_3116_km2 = r10(as.numeric(st_area(st_transform(mun_ll, 3116))) / 1e6),
  area_9377_km2 = r10(as.numeric(st_area(st_transform(mun_ll, 9377))) / 1e6),
  area_3857_km2 = r10(as.numeric(st_area(st_transform(mun_ll, 3857))) / 1e6),
  lon_centroide = r10(cen[, 1]), lat_centroide = r10(cen[, 2])),
  file.path(SALIDAS, "cap2_areas.csv"), row.names = FALSE, fileEncoding = "UTF-8")

write_json(D, file.path(SALIDAS, "cap2_datos.json"),
           auto_unbox = TRUE, digits = 10, pretty = TRUE, na = "null")
write_json(MAPAS, file.path(SALIDAS, "cap2_mapas.json"),
           auto_unbox = TRUE, digits = 8, na = "null")

kb_d <- file.size(file.path(SALIDAS, "cap2_datos.json")) / 1024
kb_m <- file.size(file.path(SALIDAS, "cap2_mapas.json")) / 1024
message(sprintf("\ncap2_datos.json  %.1f KB", kb_d))
message(sprintf("cap2_mapas.json  %.1f KB   (presupuesto de geometría: 120 KB)", kb_m))
for (nm in names(MAPAS))
  message(sprintf("    %-22s %6.1f KB", nm,
                  nchar(toJSON(MAPAS[[nm]], auto_unbox = TRUE, digits = 8),
                        type = "bytes") / 1024))
if (kb_m > 120) stop(sprintf(
  "el conjunto de mapas pesa %.1f KB y el listón del capítulo es 120 KB", kb_m))

message("\nCifras que el capítulo va a citar:")
message(sprintf("  datum:   reetiquetar Bogotá 1975 como WGS84 mueve %.2f m de media",
                D$elipsoide$datum$desp_medio_m))
message(sprintf("  grado:   1° de longitud pasa de %.1f m en el ecuador a %.1f m a 80°",
                D$grados$lon_m_elipsoide[1], tail(D$grados$lon_m_elipsoide, 1)))
message(sprintf("  Tissot:  %d proyecciones; conformes %d, equivalentes %d, las dos %d",
                nrow(tab), sum(tab$conforme), sum(tab$equivalente),
                sum(tab$conforme & tab$equivalente)))
message(sprintf("  3857:    omega máx %.5f° y área ×%.5f de mediana sobre el mundo",
                D$proyecciones$tabla$omega_max_grados[2], D$proyecciones$tabla$s_med[2]))
message(sprintf("  EPSG:    9377 razón mín %.6f (= k²) · 3116 razón mín %.6f",
                filas$e9377$razon_min, filas$e3116$razon_min))
message(sprintf("           continente: peor caso 9377 %.5f %% < 3116 %.5f %% · mediana 3116 %.5f %% < 9377 %.5f %%",
                D$epsg$continente$max_9377_pct, D$epsg$continente$max_3116_pct,
                D$epsg$continente$med_3116_pct, D$epsg$continente$med_9377_pct))
message(sprintf("           pero con San Andrés y Providencia gana 3116 en el país entero: %s",
                D$epsg$gana_3116_pais_entero))
message(sprintf("  s2:      la esfera infla Colombia %.5f %% = %.0f km²",
                D$medir$colombia$dif_esfera_pct, D$medir$colombia$dif_esfera_km2))
message(sprintf("  shp:     %d de %d campos con nombre de más de 10 caracteres; ¿truncado simple? %s",
                D$formatos$shapefile$n_campos_largos, D$formatos$shapefile$n_campos,
                D$formatos$shapefile$truncado_simple))
message(sprintf("  lon/lat: invertir manda %d de %d estaciones a %s",
                D$csv_sf$destino$n[which.max(D$csv_sf$destino$n)], n_est,
                D$csv_sf$destino$nombre[which.max(D$csv_sf$destino$n)]))
message(sprintf("  posición: 2 decimales dejan %d posiciones de %d sedes (%.4f por posición)",
                redondeos[[3]]$n_posiciones, nrow(cole), D$posicional$sedes_por_posicion_2dec))
message(sprintf("  sesgo:   global %.4f %% (+- %.4f) · de %.4f %% a %.4f %% según la localidad",
                D$posicional$sesgo$tasa_global_pct, D$posicional$sesgo$emc_global_pct,
                D$posicional$sesgo$tasa_min_pct, D$posicional$sesgo$tasa_max_pct))
message(sprintf("           corr con perímetro/área: Pearson %.5f · Spearman %.5f",
                D$posicional$sesgo$corr_pearson, D$posicional$sesgo$corr_spearman))
message(sprintf("  geohash: %d de %d puntos dentro de su celda (round-trip)",
                n_dentro_total, 5L * nrow(cole)))
message(sprintf("  índice:  %d pares posibles -> %d tras el filtro de cajas (%.2f×)",
                D$ingenieria$join$pares_fuerza_bruta, D$ingenieria$join$pares_tras_cajas,
                D$ingenieria$join$reduccion))
message(sprintf("\n  %d anclas contra la literatura, todas verificadas", N_ANCLAS))
