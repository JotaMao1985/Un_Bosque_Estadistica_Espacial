# =====================================================================
# genera_cap7.R — el precálculo del capítulo 7 (T4.4)
#
#   «Autocorrelación espacial global y local»
#   semanas 12-13 · Material de Estadística Espacial 2026-II (20929).
#
# QUÉ PRODUCE
#   precalculo/salidas/cap7_datos.json   las cifras de los 12 módulos
#   precalculo/salidas/cap7_mapas.json   las fuentes de los .geomapa
#   precalculo/salidas/cap7_*.csv        lo que las pestañas de Python leen
#
# LA REGLA QUE MANDA (D10): ninguna cifra del capítulo se escribe a mano.
#
# LAS CUATRO DECISIONES DE JAVIER (2026-09-08), y las cuatro salen del
# cronómetro del A.28, no de la costumbre. La medición entera está allí.
#
#  1. LOS TABLEROS SON COLUMBUS, LOS MUNICIPIOS Y LA REJILLA DE GETIS-ORD.
#     Columbus es el laboratorio (12,9 KB con sus cinco capas), los
#     municipios el caso real (~150 KB, declarados en su módulo) y la
#     rejilla 16x16 del artículo original entra para el módulo 11 (1,2
#     KB). Auckland y `nc` quedan fuera de los mapas: 70 KB sin una cifra
#     anclada que aportar. `nc` sigue en los bloques de código.
#
#  2. LA W CANÓNICA DE COLUMBUS ES LA GAL DE ANSELIN (1988), `spdep::oldcol`.
#     Y hay una trampa que el cronómetro destapó: `oldcol` y el
#     `columbus.gpkg` traen los 49 barrios EN ÓRDENES DISTINTOS, y cada
#     lista de vecinos va con el suyo. Mezclarlos da I = 0,342 con la
#     misma variable y la misma W. Aquí los polígonos del .gpkg se
#     reordenan por POLYID —es una permutación exacta— y la GAL reproduce
#     las cifras de Anselin (1995): I = 0,511, z = 5,63. Las diez W del
#     capítulo 6 se reconstruyen sobre ese mismo orden para el módulo 7.
#
#  3. EL p DEL CAPÍTULO ES EL DE RANGOS («Pr(folded) Sim»), CON 24 999
#     RÉPLICAS. Es el convenio de GeoDa y de `esda`, y son las réplicas
#     que hacen a Bonferroni alcanzable: con 999 el p no baja de 0,001 y
#     sobre 1 121 unidades el umbral es 4,5e-05. Los otros dos p que
#     `localmoran_perm` devuelve se publican en el módulo 10 como material.
#
#  4. LA CACHE DE LA SIMPLIFICACIÓN VIVE SOLO AQUÍ. `geo_simplifica` sobre
#     los municipios cuesta 125 s por llamada; se cachea con llave de
#     tamaño y fecha del .gpkg más el presupuesto (A.26.6). El 6 se deja.
#
# Ejecutar SIEMPRE con el envoltorio, nunca con `Rscript` a pelo:
#     precalculo/rscript.sh precalculo/genera_cap7.R
# desde la carpeta `Estadistica espacial/`. Ver utf8.R y rscript.sh.
# =====================================================================

suppressPackageStartupMessages({
  library(sf)
  library(spdep)
  library(spData)
  library(jsonlite)
  library(data.table)
})

AQUI <- "precalculo"
source(file.path(AQUI, "utf8.R"))     # PRIMERO: para si el proceso no es UTF-8
source(file.path(AQUI, "geo.R"))
source(file.path(AQUI, "fuentes.R"))

SALIDAS <- file.path(AQUI, "salidas")
CACHE   <- file.path(AQUI, "cache")
PROC    <- "datos/procesado"
dir.create(SALIDAS, showWarnings = FALSE, recursive = TRUE)
dir.create(CACHE,   showWarnings = FALSE, recursive = TRUE)

SEMILLA <- 2026L
set.seed(SEMILLA)
options(stringsAsFactors = FALSE)

# Las réplicas y el p, escritos UNA vez (decisión 3). Cambiarlos aquí
# cambia el capítulo entero, y así tiene que ser.
#
# Y TODA PERMUTACIÓN VA CON `no_repeat_in_row = TRUE`. Por defecto spdep
# muestrea los vecinos de cada unidad CON reemplazo, y GeoDa y esda
# permutan sin él: con el valor por defecto los p de spdep salían
# sistemáticamente mayores —17 de 49 en Columbus, fuera del error de
# Monte Carlo con 99 999 réplicas—, y el auditor lo llamaba defecto. Es
# el convenio de GeoDa el que el capítulo adopta (decisión 3), y los Ii
# no cambian: solo el p (A.29).
NSIM  <- 24999L
P_COL <- "Pr(folded) Sim"
ALFA  <- 0.05

r4  <- function(x) round(as.numeric(x), 4)
r5  <- function(x) round(as.numeric(x), 5)
r6  <- function(x) round(as.numeric(x), 6)
r10 <- function(x) round(as.numeric(x), 10)

N_ANCLAS <- 0L
ancla <- function(calculado, publicado, que, tol = 1e-6) {
  N_ANCLAS <<- N_ANCLAS + 1L
  d <- abs(as.numeric(calculado) - as.numeric(publicado))
  if (!is.finite(d) || d > tol)
    stop(sprintf("ANCLA ROTA · %s: calculado %.8f, la fuente publica %.8f (dif %.2e)",
                 que, as.numeric(calculado), as.numeric(publicado), d))
  invisible(TRUE)
}

cacheado <- function(nombre, expr) {
  f <- file.path(CACHE, paste0("cap7_", nombre, ".rds"))
  if (file.exists(f)) { message(sprintf("    %s: de la cache", nombre)); return(readRDS(f)) }
  v <- force(expr)
  saveRDS(v, f)
  v
}

# ---------------------------------------------------------------------
# cacheado_gpkg() — una cache con llave, para lo que depende de un dato
#
# La simplificación de los 1 122 municipios cuesta 125 s y depende de DOS
# cosas: el archivo y el presupuesto. La llave es el tamaño y la fecha
# del .gpkg más el presupuesto, como manda A.26.6: si el dato cambia, la
# cache se descarta sola. Una cache que sobrevive a su fuente es un
# generador que publica lo que ya no está mirando.
# ---------------------------------------------------------------------
cacheado_gpkg <- function(nombre, ruta, extra, expr) {
  st <- file.info(ruta)
  llave <- sprintf("%d·%d·%s", as.integer(st$size), as.integer(st$mtime), as.character(extra))
  f <- file.path(CACHE, paste0("cap7_", nombre, ".rds"))
  if (file.exists(f)) {
    v <- readRDS(f)
    if (identical(attr(v, "llave"), llave)) { message(sprintf("    %s: de la cache (llave %s)", nombre, llave)); return(v) }
    message(sprintf("    %s: la cache tiene otra llave, se rehace", nombre))
  }
  v <- force(expr)
  attr(v, "llave") <- llave
  saveRDS(v, f)
  v
}

pares_nb <- function(nb) {
  ij <- do.call(rbind, lapply(seq_along(nb), function(i) {
    j <- nb[[i]]; j <- j[j > 0]
    if (length(j) == 0) NULL else cbind(pmin(i, j), pmax(i, j))
  }))
  if (is.null(ij)) 0L else nrow(unique(ij))
}

# Lo que se publica de un test de Moran, en un solo sitio: la I, su
# esperanza, su varianza bajo el supuesto elegido, la z y el p.
resumen_moran <- function(x, lw, zp = FALSE, alternative = "greater") {
  ra <- moran.test(x, lw, zero.policy = zp, alternative = alternative)
  no <- moran.test(x, lw, zero.policy = zp, randomisation = FALSE, alternative = alternative)
  list(I = r6(ra$estimate[1]), EI = r6(ra$estimate[2]),
       var_aleat = r6(ra$estimate[3]), z_aleat = r4(ra$statistic), p_aleat = signif(ra$p.value, 4),
       var_norm = r6(no$estimate[3]), z_norm = r4(no$statistic), p_norm = signif(no$p.value, 4))
}

# LISA: de los cuadrantes de spdep a los cinco códigos del capítulo.
#   1 no significativo · 2 alto-alto · 3 bajo-bajo · 4 alto-bajo · 5 bajo-alto
# NA donde el p es NA: las islas. Un rezago que vale cero porque no hay
# vecinos no es un cuadrante, es una ausencia, y el mapa lo pinta así.
LISA_NIVELES <- c("No significativo", "Alto-alto", "Bajo-bajo", "Alto-bajo", "Bajo-alto")
LISA_COLORES <- c("#e5e5e5", "#c1272d", "#2166ac", "#f4a582", "#92c5de")
lisa_codigo <- function(lmp, p, corte = ALFA) {
  q <- as.character(attr(lmp, "quadr")$mean)
  cod <- c("High-High" = 2L, "Low-Low" = 3L, "High-Low" = 4L, "Low-High" = 5L)[q]
  cod[!is.na(p) & p >= corte] <- 1L
  cod[is.na(p)] <- NA_integer_
  unname(cod)
}
lisa_conteo <- function(cod) as.integer(table(factor(cod, levels = 1:5)))

# Gi*: siete niveles por el signo de la z y el p por rangos.
G_NIVELES <- c("Frío al 99 %", "Frío al 95 %", "Frío al 90 %", "No significativo",
               "Caliente al 90 %", "Caliente al 95 %", "Caliente al 99 %")
G_COLORES <- c("#2166ac", "#67a9cf", "#d1e5f0", "#e5e5e5", "#fddbc7", "#ef8a62", "#b2182b")
gistar_codigo <- function(z, p) {
  cod <- rep(4L, length(z))
  cod[!is.na(p) & p < 0.10] <- ifelse(z[!is.na(p) & p < 0.10] > 0, 5L, 3L)
  cod[!is.na(p) & p < 0.05] <- ifelse(z[!is.na(p) & p < 0.05] > 0, 6L, 2L)
  cod[!is.na(p) & p < 0.01] <- ifelse(z[!is.na(p) & p < 0.01] > 0, 7L, 1L)
  cod[is.na(p) | is.na(z)] <- NA_integer_
  cod
}
gistar_conteo <- function(cod) as.integer(table(factor(cod, levels = 1:7)))

D <- list()
MAPAS <- list()

# =====================================================================
# 0. LOS DATOS
# =====================================================================
message("0. los datos")

# --- El laboratorio: Columbus EN EL ORDEN DE ANSELIN ------------------
col0 <- st_read(system.file("shapes/columbus.gpkg", package = "spData"), quiet = TRUE)
data(oldcol, package = "spdep")                    # COL.OLD, COL.nb
ord <- match(COL.OLD$POLYID, col0$POLYID)
if (anyNA(ord) || length(unique(ord)) != nrow(col0))
  stop("POLYID no es una permutación entre oldcol y columbus.gpkg")
col <- col0[ord, ]
ancla(nrow(col), 49, "barrios de Columbus", tol = 0)
ancla(max(abs(col$CRIME - COL.OLD$CRIME)), 0, "CRIME idéntico tras reordenar por POLYID", tol = 0)
ancla(max(abs(col$X - COL.OLD$X), abs(col$Y - COL.OLD$Y)), 0, "centroides idénticos tras reordenar", tol = 0)
GAL    <- COL.nb
lw_gal <- nb2listw(GAL, style = "W")
col_cent <- suppressWarnings(st_centroid(st_geometry(col)))
col_xy   <- st_coordinates(col_cent)

# --- El caso real: los municipios de Colombia -------------------------
mun <- carga_municipios(proc = PROC)
ancla(nrow(mun), 1122, "municipios de la capa nacional", tol = 0)
des <- mun$desercion
ok_des <- is.finite(des)
sub <- which(ok_des)
message("  poly2nb sobre los municipios (42 s la primera vez, luego cache)")
f6 <- file.path(CACHE, "cap6_mun_reina.rds")
mun_reina <- if (file.exists(f6)) { message("    mun_reina: de la cache del capítulo 6"); readRDS(f6) } else
  cacheado("mun_reina", poly2nb(mun, queen = TRUE))
nb_sub <- subset.nb(mun_reina, ok_des)
lw_sub <- nb2listw(nb_sub, style = "W", zero.policy = TRUE)
tiene_vecino <- card(nb_sub) > 0
islas_sub <- which(!tiene_vecino)
y_mun <- des[sub]

# --- La rejilla de Getis y Ord (1992) ---------------------------------
data(getisord, package = "spData")                 # go_x, go_y, go_xyz
go_xy <- cbind(go_xyz$x, go_xyz$y)
nb30  <- dnearneigh(go_xy, 0, 30)
lw30B <- nb2listw(nb30, style = "B")
lw30S <- nb2listw(include.self(nb30), style = "B")

# =====================================================================
# A. MÓDULO 1 — La pregunta: ¿lo cercano se parece más de lo esperable?
# =====================================================================
message("A. modulo 1 - la pregunta")

wy_mun <- lag.listw(lw_sub, y_mun, zero.policy = TRUE)
wcrime <- lag.listw(lw_gal, col$CRIME)

# El retículo del simulador 1: la banda de referencia bajo H0 solo
# depende de W, así que se publica y el navegador no la inventa.
ret10 <- cell2nb(10, 10, type = "rook")
lw_ret <- nb2listw(ret10, style = "W")
m_ret <- moran.test(rnorm(100), lw_ret, randomisation = FALSE)
W_ret <- nb2mat(ret10, style = "W")
ev_ret <- eigen((W_ret + t(W_ret)) / 2, symmetric = TRUE, only.values = TRUE)$values

D$m1 <- list(
  columbus = list(n = nrow(col), variable = "CRIME",
                  media = r4(mean(col$CRIME)), sd = r4(sd(col$CRIME)),
                  cor_con_rezago = r4(cor(col$CRIME, wcrime)),
                  EI = r6(-1 / (nrow(col) - 1))),
  municipios = list(n = nrow(mun), con_dato = length(sub), sin_dato = sum(!ok_des),
                    islas = length(islas_sub),
                    media = r4(mean(y_mun)), sd = r4(sd(y_mun)),
                    cor_con_rezago = r4(cor(y_mun[tiene_vecino], wy_mun[tiene_vecino])),
                    EI = r6(-1 / (length(sub) - 1))),
  reticulo = list(lado = 10L, n = 100L, EI = r6(m_ret$estimate[2]),
                  sd_norm = r6(sqrt(m_ret$estimate[3])),
                  rango = r4(range(ev_ret))))

# =====================================================================
# B. MÓDULO 2 — El índice de Moran: fórmula, E[I] y su rango real
# =====================================================================
message("B. modulo 2 - el indice de Moran")

z_col  <- as.numeric(scale(col$CRIME))
wz_col <- lag.listw(lw_gal, z_col)
rm_col <- resumen_moran(col$CRIME, lw_gal)
# Las anclas se comprueban sobre el valor CRUDO, no sobre el redondeado
# que se publica: un r6 contra una tolerancia de 1e-9 rompe solo.
mt_col_raw <- moran.test(col$CRIME, lw_gal)
I_col_raw  <- unname(mt_col_raw$estimate[1])

# LAS ANCLAS DE ANSELIN (1995). Son las cifras que validan el tablero
# entero: si alguna se moviera —otro orden, otra GAL, otro estilo—, el
# capítulo estaría midiendo otra cosa sin avisar.
ancla(I_col_raw, 0.511, "Columbus CRIME: I de Moran (Anselin 1995)", tol = 5e-4)
ancla(mt_col_raw$statistic, 5.63, "Columbus CRIME: z por aleatorización (Anselin 1995)", tol = 5e-3)
ancla(mt_col_raw$estimate[2], -1 / 48, "E[I] = -1/(n-1)", tol = 1e-9)

W_gal <- nb2mat(GAL, style = "W")
ev_gal <- eigen((W_gal + t(W_gal)) / 2, symmetric = TRUE, only.values = TRUE)$values
W_msub <- nb2mat(nb_sub, style = "W", zero.policy = TRUE)
ev_mun <- eigen((W_msub + t(W_msub)) / 2, symmetric = TRUE, only.values = TRUE)$values

D$m2 <- list(
  columbus = c(list(tablero = "Columbus, GAL de Anselin (1988)", n = nrow(col),
                    pares_gal = pares_nb(GAL), S0 = r6(Szero(lw_gal)),
                    # Las piezas de la fórmula, para que el bloque de código
                    # las imprima y no las recite: I = (n/S0) · z'Wz / z'z.
                    z_Wz = r6(sum(z_col * wz_col)), z_z = r6(sum(z_col^2))),
               rm_col),
  # El mismo I bajo los cinco estilos: B, C y U dan lo mismo porque
  # escalar todos los pesos por igual no mueve el cociente; W y S no.
  estilos = lapply(c("B", "W", "C", "U", "S"), function(e) {
    lw <- nb2listw(GAL, style = e)
    list(id = e, I = r6(moran.test(col$CRIME, lw)$estimate[1]), S0 = r6(Szero(lw)))
  }),
  # EL RANGO REAL: los valores propios extremos de (W + W')/2 escalados por
  # n/S0 (de Jong, Sprenger & van Veen, 1984). Con W estandarizada por
  # filas n/S0 = 1 y el rango es el de los valores propios.
  rango = list(columbus_gal = r4(range(ev_gal)),
               municipios = r4(range(ev_mun)),
               reticulo_10 = r4(range(ev_ret))))

# =====================================================================
# C. MÓDULO 3 — Inferencia: normalidad, aleatorización y permutación
# =====================================================================
message("C. modulo 3 - inferencia")

set.seed(SEMILLA)
mc_col_999 <- moran.mc(col$CRIME, lw_gal, nsim = 999)
set.seed(SEMILLA)
mc_col_99k <- moran.mc(col$CRIME, lw_gal, nsim = 99999)
rm_mun <- resumen_moran(y_mun, lw_sub, zp = TRUE)
mt_mun_raw <- moran.test(y_mun, lw_sub, zero.policy = TRUE)
ancla(mt_mun_raw$estimate[1], 0.3809079, "I municipal de la deserción (T0.4a, A.11)", tol = 1e-6)
set.seed(SEMILLA)
mc_mun_999 <- moran.mc(y_mun, lw_sub, nsim = 999, zero.policy = TRUE)
set.seed(SEMILLA)
mc_mun_9999 <- moran.mc(y_mun, lw_sub, nsim = 9999, zero.policy = TRUE)

# La curtosis es lo que separa la varianza por aleatorización de la de
# normalidad: se publica para que la diferencia tenga causa.
b2 <- function(x) { n <- length(x); (sum((x - mean(x))^4) / n) / (sum((x - mean(x))^2) / n)^2 }

# LA POTENCIA frente a rho y n, con campos SAR sobre retículos torre.
# Vectorizada: 1 000 réplicas por celda son 40 000 campos en ~3 s.
potencia_celda <- function(k, rho, reps = 1000L) {
  set.seed(SEMILLA + 1000L * k + as.integer(round(rho * 10)))
  nb <- cell2nb(k, k, type = "rook"); n <- k * k
  W <- nb2mat(nb, style = "W"); A <- solve(diag(n) - rho * W)
  E <- matrix(rnorm(n * reps), n); Y <- A %*% E
  Z <- scale(Y); WZ <- W %*% Z
  I <- colSums(Z * WZ) / colSums(Z^2)
  m0 <- moran.test(Y[, 1], nb2listw(nb, style = "W"), randomisation = FALSE)
  r4(mean((I - m0$estimate[2]) / sqrt(m0$estimate[3]) > qnorm(1 - ALFA)))
}
LADOS <- c(5L, 7L, 10L, 20L); RHOS <- seq(0, 0.9, by = 0.1)
potencia <- lapply(LADOS, function(k) list(lado = k, n = k * k,
  potencia = vapply(RHOS, function(r) potencia_celda(k, r), numeric(1))))

D$m3 <- list(
  columbus = list(
    normalidad = list(var = rm_col$var_norm, z = rm_col$z_norm, p = rm_col$p_norm),
    aleatorizacion = list(var = rm_col$var_aleat, z = rm_col$z_aleat, p = rm_col$p_aleat,
                          curtosis = r4(b2(col$CRIME))),
    permutacion = list(
      nsim = 999L, I = r6(mc_col_999$statistic), p = r6(mc_col_999$p.value),
      rango_observado = as.integer(sum(mc_col_999$res[-1000] >= mc_col_999$statistic)),
      media_sim = r6(mean(mc_col_999$res[-1000])), sd_sim = r6(sd(mc_col_999$res[-1000])),
      max_sim = r6(max(mc_col_999$res[-1000])),
      # Las 999 réplicas, para el histograma del módulo: el simulador las
      # rehace en el navegador, pero la figura del texto sale de aquí.
      replicas = r4(mc_col_999$res[-1000])),
    permutacion_99999 = list(nsim = 99999L, p = signif(mc_col_99k$p.value, 3),
                             suelo = signif(1 / (99999 + 1), 3))),
  municipios = list(
    aleatorizacion = list(I = rm_mun$I, EI = rm_mun$EI, var = rm_mun$var_aleat,
                          z = rm_mun$z_aleat, p = rm_mun$p_aleat,
                          n_con_vecinos = sum(tiene_vecino), n = length(sub)),
    # EL SUELO DEL p DE PERMUTACIÓN: con 999 réplicas no baja de 0,001 aunque
    # el analítico diga 1e-101. No es que el efecto sea menor: es que el
    # método no puede decir más.
    permutacion = lapply(list(mc_mun_999, mc_mun_9999), function(m)
      list(nsim = length(m$res) - 1L, p = r6(m$p.value), suelo = r6(1 / length(m$res))))),
  potencia = list(alfa = ALFA, replicas = 1000L, rhos = RHOS, curvas = potencia))

# =====================================================================
# D. MÓDULO 4 — El diagrama de Moran: la pendiente ES I
# =====================================================================
message("D. modulo 4 - el diagrama de Moran")

pend <- unname(coef(lm(wz_col ~ z_col))[2])
ancla(pend, I_col_raw, "pendiente de Wz sobre z = I (Anselin 1996)", tol = 1e-9)
mp <- moran.plot(col$CRIME, lw_gal, plot = FALSE, return_df = TRUE)
cuad_col <- ifelse(z_col >= 0, ifelse(wz_col >= 0, "AA", "AB"), ifelse(wz_col >= 0, "BA", "BB"))

z_mun  <- as.numeric(scale(y_mun))
wz_mun <- lag.listw(lw_sub, z_mun, zero.policy = TRUE)
pend_mun_con <- unname(coef(lm(wz_mun[tiene_vecino] ~ z_mun[tiene_vecino]))[2])

D$m4 <- list(
  columbus = list(
    pendiente = r6(pend), I = rm_col$I,
    pendiente_sin_tipificar = r6(unname(coef(lm(mp$wx ~ mp$x))[2])),
    cuadrantes = as.list(table(factor(cuad_col, levels = c("AA", "BB", "AB", "BA")))),
    influyentes = as.integer(sum(mp$is_inf)),
    influyentes_polyid = as.integer(col$POLYID[mp$is_inf]),
    # Los 49 puntos, con su POLYID: es lo que el diagrama clicable
    # necesita para resaltar el barrio en el mapa.
    puntos = list(polyid = as.integer(col$POLYID), z = r5(z_col), wz = r5(wz_col))),
  municipios = list(
    I = rm_mun$I,
    # CON ISLAS LA IDENTIDAD SE CUMPLE SOBRE TODAS LAS UNIDADES, no sobre las
    # que tienen vecinos —al revés de lo que uno espera—: spdep divide por
    # n_con_vecinos y S0 también vale n_con_vecinos, así que I = z'Wz / z'z
    # sobre las 1 121, con las dos islas aportando Wz = 0. Sobre las 1 119
    # la recta se desvía, porque ese subconjunto ya no está centrado.
    pendiente_con_vecinos = r6(pend_mun_con),
    pendiente_todas = r6(unname(coef(lm(wz_mun ~ z_mun))[2])),
    cuadrantes = as.list(table(factor(
      ifelse(z_mun >= 0, ifelse(wz_mun >= 0, "AA", "AB"), ifelse(wz_mun >= 0, "BA", "BB"))[tiene_vecino],
      levels = c("AA", "BB", "AB", "BA")))),
    puntos = list(z = r5(z_mun), wz = r5(wz_mun))))

# =====================================================================
# E. MÓDULO 5 — La c de Geary, y cuándo discrepa de I
# =====================================================================
message("E. modulo 5 - la c de Geary")

gt_col <- geary.test(col$CRIME, lw_gal)
set.seed(SEMILLA)
gmc_col <- geary.mc(col$CRIME, lw_gal, nsim = 9999)
gt_mun <- geary.test(y_mun, lw_sub, zero.policy = TRUE)

# El caso en que discrepan: UN barrio disparado. Se dispara el de MAYOR
# CRIME —un valor alto entre altos— y el de vecindad más baja —uno que se
# vuelve extremo entre bajos—, y se publican las DOS curvas. Lo que dicen,
# medido y no supuesto: caiga donde caiga, el extremo arrastra a I hacia
# CERO y a c hacia UNO, sus dos valores nulos. I pierde el 90 % con el
# factor 8; c recorre el 80 % del camino hasta 1. Ninguno es robusto, y
# 1 - c y I se separan justo cuando hay un atípico: la discrepancia es la
# señal. (La primera versión disparaba «el más conectado», que resultó ser
# el de MENOR CRIME: multiplicar 0,22 por ocho no es un pico.)
FACTORES <- c(1, 1.5, 2, 3, 5, 8)
curva_pico <- function(i) lapply(FACTORES, function(f) {
  x <- col$CRIME; x[i] <- x[i] * f
  list(factor = f, I = r4(moran.test(x, lw_gal)$estimate[1]),
       c = r4(geary.test(x, lw_gal)$estimate[1]))
})
i_pico_alto <- which.max(col$CRIME)          # el de mayor CRIME: alto entre altos
i_pico_bajo <- which.min(wz_col)             # el de vecindad más baja
ficha_pico <- function(i) list(unidad = as.integer(i), polyid = as.integer(col$POLYID[i]),
                               grado = as.integer(card(GAL)[i]), crime = r4(col$CRIME[i]),
                               z = r4(z_col[i]), wz = r4(wz_col[i]), curva = curva_pico(i))
tres <- lapply(c("CRIME", "HOVAL", "INC"), function(v)
  list(variable = v, I = r4(moran.test(col[[v]], lw_gal)$estimate[1]),
       c = r4(geary.test(col[[v]], lw_gal)$estimate[1]),
       uno_menos_c = r4(1 - geary.test(col[[v]], lw_gal)$estimate[1])))

D$m5 <- list(
  columbus = list(c = r6(gt_col$estimate[1]), Ec = 1, var = r6(gt_col$estimate[3]),
                  z = r4(gt_col$statistic), p = signif(gt_col$p.value, 4),
                  uno_menos_c = r6(1 - gt_col$estimate[1]), I = rm_col$I,
                  p_permutacion_9999 = r6(gmc_col$p.value)),
  tres_variables = tres,
  pico_en_alto = ficha_pico(i_pico_alto),
  pico_en_bajo = ficha_pico(i_pico_bajo),
  municipios = list(c = r6(gt_mun$estimate[1]), z = r4(gt_mun$statistic),
                    p = signif(gt_mun$p.value, 4), I = rm_mun$I))

# =====================================================================
# F. MÓDULO 6 — Correlograma y join count
# =====================================================================
message("F. modulo 6 - correlograma y join count")

correlograma <- function(nb, x, orden, zp = TRUE) {
  lags <- nblag(nb, maxlag = orden)
  sc <- sp.correlogram(nb, x, order = orden, method = "I", zero.policy = zp)
  lapply(seq_len(orden), function(k) list(
    orden = k, I = r6(sc$res[k, 1]), EI = r6(sc$res[k, 2]), var = r6(sc$res[k, 3]),
    z = r4((sc$res[k, 1] - sc$res[k, 2]) / sqrt(sc$res[k, 3])),
    pares = pares_nb(lags[[k]]), sin_vecinos = as.integer(sum(card(lags[[k]]) == 0)),
    subgrafos = as.integer(n.comp.nb(lags[[k]])$nc)))
}
cg_col <- suppressWarnings(correlograma(GAL, col$CRIME, 6L))
cg_mun <- suppressWarnings(correlograma(nb_sub, y_mun, 8L))

# Join count: la variable binaria. En Columbus, CP (centro / periferia),
# que ya viene binaria; en los municipios, deserción sobre la mediana y
# el tipo de entidad (18 áreas no municipalizadas).
jc <- function(f, lw, zp = FALSE, nsim = 9999L) {
  m <- joincount.multi(f, lw, zero.policy = zp)
  set.seed(SEMILLA)
  mc <- joincount.mc(f, lw, nsim = nsim, zero.policy = zp)
  filas <- lapply(rownames(m), function(r) list(
    par = r, observado = r6(m[r, "Joincount"]), esperado = r6(m[r, "Expected"]),
    var = r6(m[r, "Variance"]), z = r4(m[r, "z-value"])))
  list(tabla = filas, niveles = levels(f), n_por_nivel = as.integer(table(f)),
       p_permutacion = lapply(seq_along(mc), function(i)
         list(nivel = levels(f)[i], p = r6(mc[[i]]$p.value))))
}
f_cp <- factor(col$CP, levels = c(0, 1), labels = c("periferia", "centro"))
f_des <- factor(y_mun > median(y_mun), levels = c(FALSE, TRUE), labels = c("bajo la mediana", "sobre la mediana"))
f_tipo <- factor(mun$tipo[sub] == "Municipio", levels = c(FALSE, TRUE), labels = c("no municipalizada o isla", "municipio"))

D$m6 <- list(
  correlograma = list(columbus = cg_col, municipios = cg_mun),
  join_count = list(columbus_cp = jc(f_cp, lw_gal),
                    municipios_desercion = jc(f_des, lw_sub, zp = TRUE),
                    municipios_tipo = jc(f_tipo, lw_sub, zp = TRUE)))

# =====================================================================
# G. MÓDULO 7 — Moran es sensible a W: las once de Columbus, seis municipales
# =====================================================================
message("G. modulo 7 - sensible a W")

d1_col <- max(unlist(nbdists(knn2nb(knearneigh(col_cent, k = 1)), col_cent)))
W_COL <- list(
  gal      = GAL,
  reina    = poly2nb(col, queen = TRUE),
  torre    = poly2nb(col, queen = FALSE),
  k1       = knn2nb(knearneigh(col_cent, k = 1)),
  k3       = knn2nb(knearneigh(col_cent, k = 3)),
  k6       = knn2nb(knearneigh(col_cent, k = 6)),
  d_mitad  = suppressWarnings(dnearneigh(col_cent, 0, d1_col * 0.5)),
  d_conexo = suppressWarnings(dnearneigh(col_cent, 0, d1_col)),
  delaunay = tri2nb(col_cent),
  gabriel  = graph2nb(gabrielneigh(col_xy), sym = TRUE),
  esfera   = graph2nb(soi.graph(tri2nb(col_cent), col_cent), sym = TRUE))
ancla(pares_nb(W_COL$reina), 118, "Columbus reina: aristas (Anselin, cap. 6)", tol = 0)
ancla(pares_nb(W_COL$torre), 100, "Columbus torre: aristas (Anselin, cap. 6)", tol = 0)
ETQ_W <- c(gal = "GAL de Anselin (1988)", reina = "Contigüidad reina", torre = "Contigüidad torre",
           k1 = "1 vecino más próximo", k3 = "3 vecinos más próximos",
           k6 = "6 vecinos más próximos",
           d_mitad = "Umbral: la mitad del mínimo conexo",
           d_conexo = "Umbral mínimo sin islas",
           delaunay = "Delaunay", gabriel = "Gabriel", esfera = "Esfera de influencia")

moran_bajo <- function(x, nb, zp) {
  lw <- nb2listw(nb, style = "W", zero.policy = zp)
  m <- moran.test(x, lw, zero.policy = zp)
  list(pares = pares_nb(nb), grado = r4(mean(card(nb))), islas = as.integer(sum(card(nb) == 0)),
       simetrica = is.symmetric.nb(nb, verbose = FALSE),
       I = r6(m$estimate[1]), EI = r6(m$estimate[2]), z = r4(m$statistic), p = signif(m$p.value, 4))
}
# La GAL frente a la reina: las tres esquinas que mueven la segunda cifra.
solo_en <- function(a, b) sum(vapply(seq_along(a), function(i) length(setdiff(a[[i]], b[[i]])), integer(1))) / 2
mun_cent_sub <- suppressWarnings(st_centroid(st_geometry(mun)))[sub]
f_torre <- file.path(CACHE, "cap6_mun_torre.rds")
mun_torre <- if (file.exists(f_torre)) readRDS(f_torre) else cacheado("mun_torre", poly2nb(mun, queen = FALSE))
W_MUN <- list(reina = nb_sub, torre = subset.nb(mun_torre, ok_des),
              k4 = knn2nb(knearneigh(mun_cent_sub, k = 4)), k8 = knn2nb(knearneigh(mun_cent_sub, k = 8)),
              d50 = suppressWarnings(dnearneigh(mun_cent_sub, 0, 50e3)), delaunay = tri2nb(mun_cent_sub))
ETQ_M <- c(reina = "Contigüidad reina", torre = "Contigüidad torre", k4 = "4 vecinos más próximos",
           k8 = "8 vecinos más próximos", d50 = "Umbral de 50 km", delaunay = "Delaunay")

D$m7 <- list(
  columbus = lapply(names(W_COL), function(k)
    c(list(id = k, etiqueta = unname(ETQ_W[k])), moran_bajo(col$CRIME, W_COL[[k]], zp = TRUE))),
  gal_vs_reina = list(pares_gal = pares_nb(GAL), pares_reina = pares_nb(W_COL$reina),
                      solo_gal = as.integer(solo_en(GAL, W_COL$reina)),
                      solo_reina = as.integer(solo_en(W_COL$reina, GAL)),
                      I_gal = rm_col$I, I_reina = r6(moran.test(col$CRIME, nb2listw(W_COL$reina))$estimate[1])),
  municipios = lapply(names(W_MUN), function(k)
    c(list(id = k, etiqueta = unname(ETQ_M[k])), moran_bajo(y_mun, W_MUN[[k]], zp = TRUE))))
rango_I <- function(l) { v <- vapply(l, function(e) e$I, numeric(1)); r4(range(v)) }
D$m7$resumen <- list(columbus_I = rango_I(D$m7$columbus), municipios_I = rango_I(D$m7$municipios),
                     columbus_p_max = max(vapply(D$m7$columbus, function(e) e$p, numeric(1))),
                     municipios_p_max = max(vapply(D$m7$municipios, function(e) e$p, numeric(1))))

# =====================================================================
# H. MÓDULO 8 — Del global al local: la descomposición de Anselin
# =====================================================================
message("H. modulo 8 - del global al local (", NSIM, " permutaciones)")

lm_col  <- localmoran(col$CRIME, lw_gal)
lmp_col <- localmoran_perm(col$CRIME, lw_gal, nsim = NSIM, iseed = SEMILLA, no_repeat_in_row = TRUE)
ancla(mean(lm_col[, "Ii"]), I_col_raw, "suma de Ii / S0 = I (Anselin 1995)", tol = 1e-9)
p_col <- lmp_col[, P_COL]

message("   localmoran_perm sobre los municipios (~9 s)")
lm_mun  <- localmoran(y_mun, lw_sub, zero.policy = TRUE)
lmp_mun <- localmoran_perm(y_mun, lw_sub, nsim = NSIM, zero.policy = TRUE, iseed = SEMILLA, no_repeat_in_row = TRUE)
p_mun <- lmp_mun[, P_COL]
# CON ISLAS, LA SUMA DE LOS Ii ENTRE S0 NO DA EL I DE spdep: DA EL DE esda.
# Los Ii se calculan con n = todas las unidades (1 121) y el I global de
# spdep con n = las que tienen vecinos (1 119); el cociente entre los dos
# es exactamente 1 121/1 119, el convenio de A.11. Es la misma
# discrepancia vista desde lo local, y se publica con ese nombre.
ident_mun <- sum(lm_mun[, "Ii"], na.rm = TRUE) / Szero(lw_sub)
I_esda_equiv <- unname(mt_mun_raw$estimate[1]) * length(sub) / sum(tiene_vecino)

top <- order(-abs(lmp_mun[, "Ii"]))[1:5]
D$m8 <- list(
  nsim = NSIM, p = P_COL,
  columbus = list(
    I = rm_col$I, media_Ii = r6(mean(lm_col[, "Ii"])), S0 = r6(Szero(lw_gal)),
    suma_Ii = r6(sum(lm_col[, "Ii"])),
    Ii = r5(lmp_col[, "Ii"]), E_Ii = r5(lmp_col[, "E.Ii"]), z = r4(lmp_col[, "Z.Ii"]),
    p_analitico = signif(lm_col[, "Pr(z != E(Ii))"], 4),
    p_bilateral = signif(lmp_col[, "Pr(z != E(Ii)) Sim"], 4),
    p_normal_permutado = signif(lmp_col[, "Pr(z != E(Ii))"], 4),
    p_rangos = r5(p_col),
    cuadrante = as.character(attr(lmp_col, "quadr")$mean),
    polyid = as.integer(col$POLYID),
    p_min = r5(min(p_col)), suelo = r5(1 / (NSIM + 1)),
    significativos = as.integer(sum(p_col < ALFA))),
  municipios = list(
    I = rm_mun$I, suma_Ii_sobre_S0 = r6(ident_mun), I_esda_equivalente = r6(I_esda_equiv),
    factor_islas = r6(length(sub) / sum(tiene_vecino)),
    p_min = r5(min(p_mun, na.rm = TRUE)), significativos = as.integer(sum(p_mun < ALFA, na.rm = TRUE)),
    Ii_max = r5(max(lmp_mun[, "Ii"])), Ii_min = r5(min(lmp_mun[, "Ii"])),
    top5 = lapply(top, function(i) list(
      municipio = mun$municipio[sub][i], departamento = mun$departamento[sub][i],
      desercion = r4(y_mun[i]), Ii = r5(lmp_mun[i, "Ii"]), p = r5(p_mun[i]),
      cuadrante = as.character(attr(lmp_mun, "quadr")$mean[i])))))

# =====================================================================
# I. MÓDULO 9 — El mapa de conglomerados LISA
# =====================================================================
message("I. modulo 9 - el mapa LISA")

lisa_col <- lisa_codigo(lmp_col, p_col)
lisa_mun <- lisa_codigo(lmp_mun, p_mun)

# LAS ISLAS: spdep les da Ii = 0, p = NA y un cuadrante. Se publica lo que
# spdep dice y lo que el capítulo hace con ello, que no es lo mismo.
D$m9 <- list(
  niveles = LISA_NIVELES, colores = LISA_COLORES, alfa = ALFA, nsim = NSIM,
  columbus = list(conteo = lisa_conteo(lisa_col),
                  alto_alto_polyid = as.integer(col$POLYID[!is.na(lisa_col) & lisa_col == 2L]),
                  bajo_bajo_polyid = as.integer(col$POLYID[!is.na(lisa_col) & lisa_col == 3L]),
                  atipicos_polyid = as.integer(col$POLYID[!is.na(lisa_col) & lisa_col >= 4L])),
  municipios = list(
    conteo = lisa_conteo(lisa_mun), sin_vecinos = as.integer(sum(is.na(lisa_mun))),
    islas = list(municipio = mun$municipio[sub][islas_sub], departamento = mun$departamento[sub][islas_sub],
                 Ii = r5(lmp_mun[islas_sub, "Ii"]),
                 cuadrante_spdep = as.character(attr(lmp_mun, "quadr")$mean[islas_sub])),
    # Los conglomerados alto-alto por departamento: dónde están.
    alto_alto_por_departamento = {
      t <- sort(table(mun$departamento[sub][!is.na(lisa_mun) & lisa_mun == 2L]), decreasing = TRUE)
      lapply(seq_len(min(6, length(t))), function(i) list(departamento = names(t)[i], n = as.integer(t[i])))
    },
    bajo_bajo_por_departamento = {
      t <- sort(table(mun$departamento[sub][!is.na(lisa_mun) & lisa_mun == 3L]), decreasing = TRUE)
      lapply(seq_len(min(6, length(t))), function(i) list(departamento = names(t)[i], n = as.integer(t[i])))
    }))

# =====================================================================
# J. MÓDULO 10 — La trampa de la multiplicidad
# =====================================================================
message("J. modulo 10 - multiplicidad")

conteos <- function(p) {
  p <- p[!is.na(p)]
  list(sin_corregir = as.integer(sum(p < ALFA)),
       bonferroni = as.integer(sum(p.adjust(p, "bonferroni") < ALFA)),
       holm = as.integer(sum(p.adjust(p, "holm") < ALFA)),
       fdr = as.integer(sum(p.adjust(p, "fdr") < ALFA)))
}
# Y con 999 réplicas, que es lo que sale por defecto y lo que enseña la
# trampa: la MISMA semilla, otro nsim.
lmp_col_999 <- localmoran_perm(col$CRIME, lw_gal, nsim = 999L, iseed = SEMILLA, no_repeat_in_row = TRUE)
lmp_mun_999 <- localmoran_perm(y_mun, lw_sub, nsim = 999L, zero.policy = TRUE, iseed = SEMILLA, no_repeat_in_row = TRUE)

# El procedimiento de Benjamini-Hochberg, paso a paso sobre Columbus: los
# p ordenados y el umbral i·alfa/n de cada uno, que es lo que el ejercicio
# repite a mano sobre diez valores.
p_ord <- sort(p_col); n_c <- length(p_ord)
umbral_bh <- seq_len(n_c) * ALFA / n_c
k_bh <- suppressWarnings(max(which(p_ord <= umbral_bh)))
if (!is.finite(k_bh)) k_bh <- 0L

# LOS CUATRO p, con el nombre que la ayuda de spdep les da y no el que
# parece: en `localmoran_perm` la columna «Pr(z != E(Ii))» NO es la
# analítica —usa la media y la desviación de las permutaciones—, la
# analítica de verdad es la de `localmoran()`. «Pr(z != E(Ii)) Sim» es el
# rango bilateral y «Pr(folded) Sim» el rango plegado, el de esda y GeoDa.
tabla_p <- function(lmp, lmp999, lm0) list(
  plegado_999 = c(list(p = "Pr(folded) Sim", que = "rangos, plegado (GeoDa/esda)", nsim = 999L),
                  conteos(lmp999[, "Pr(folded) Sim"])),
  plegado_nsim = c(list(p = "Pr(folded) Sim", que = "rangos, plegado (GeoDa/esda)", nsim = NSIM),
                   conteos(lmp[, "Pr(folded) Sim"])),
  bilateral_999 = c(list(p = "Pr(z != E(Ii)) Sim", que = "rangos, bilateral", nsim = 999L),
                    conteos(lmp999[, "Pr(z != E(Ii)) Sim"])),
  bilateral_nsim = c(list(p = "Pr(z != E(Ii)) Sim", que = "rangos, bilateral", nsim = NSIM),
                     conteos(lmp[, "Pr(z != E(Ii)) Sim"])),
  normal_permutado_999 = c(list(p = "Pr(z != E(Ii))", que = "normal con momentos permutados", nsim = 999L),
                           conteos(lmp999[, "Pr(z != E(Ii))"])),
  normal_permutado_nsim = c(list(p = "Pr(z != E(Ii))", que = "normal con momentos permutados", nsim = NSIM),
                            conteos(lmp[, "Pr(z != E(Ii))"])),
  analitico = c(list(p = "localmoran: Pr(z != E(Ii))", que = "analítico", nsim = 0L),
                conteos(lm0[, "Pr(z != E(Ii))"])))

lisa_col_bonf <- lisa_codigo(lmp_col, p.adjust(p_col, "bonferroni"))
lisa_col_fdr  <- lisa_codigo(lmp_col, p.adjust(p_col, "fdr"))
p_mun_bonf <- p_mun; p_mun_bonf[!is.na(p_mun)] <- p.adjust(p_mun[!is.na(p_mun)], "bonferroni")
p_mun_fdr  <- p_mun; p_mun_fdr[!is.na(p_mun)]  <- p.adjust(p_mun[!is.na(p_mun)], "fdr")
lisa_mun_bonf <- lisa_codigo(lmp_mun, p_mun_bonf)
lisa_mun_fdr  <- lisa_codigo(lmp_mun, p_mun_fdr)

sig999 <- lmp_mun_999[, P_COL] < ALFA; sigN <- p_mun < ALFA
D$m10 <- list(
  alfa = ALFA, nsim = NSIM,
  # El suelo: con nsim réplicas el p por rangos no baja de 1/(nsim+1), y
  # Bonferroni exige alfa/n. nsim_min = ceiling(n/alfa) - 1.
  suelo = list(columbus = list(n = nrow(col), umbral_bonferroni = signif(ALFA / nrow(col), 4),
                               nsim_minimo = as.integer(ceiling(nrow(col) / ALFA) - 1)),
               municipios = list(n = length(sub), umbral_bonferroni = signif(ALFA / length(sub), 4),
                                 nsim_minimo = as.integer(ceiling(length(sub) / ALFA) - 1)),
               p_min_999 = r6(1 / 1000), p_min_nsim = r6(1 / (NSIM + 1))),
  columbus = list(tabla = tabla_p(lmp_col, lmp_col_999, lm_col),
                  conteo_sin = lisa_conteo(lisa_col), conteo_bonferroni = lisa_conteo(lisa_col_bonf),
                  conteo_fdr = lisa_conteo(lisa_col_fdr),
                  bh = list(p_ordenados = r5(p_ord), umbrales = r5(umbral_bh), k = as.integer(k_bh),
                            umbral_bonferroni = r6(ALFA / n_c))),
  municipios = list(tabla = tabla_p(lmp_mun, lmp_mun_999, lm_mun),
                    conteo_sin = lisa_conteo(lisa_mun), conteo_bonferroni = lisa_conteo(lisa_mun_bonf),
                    conteo_fdr = lisa_conteo(lisa_mun_fdr),
                    # Entre 999 y NSIM réplicas: los cuadrantes no se mueven, el
                    # conjunto significativo sí.
                    cuadrantes_cambian = as.integer(sum(attr(lmp_mun_999, "quadr")$mean != attr(lmp_mun, "quadr")$mean)),
                    significativos_cambian = as.integer(sum(xor(sig999, sigN), na.rm = TRUE))))

# =====================================================================
# K. MÓDULO 11 — Getis-Ord Gi y Gi*: intensidad, no similitud
# =====================================================================
message("K. modulo 11 - Getis-Ord")

G30  <- localG(go_xyz$val, lw30B)
G30s <- localG(go_xyz$val, lw30S)
i120 <- length(go_xyz$val) - 136L                  # la celda del ejemplo de spdep
G30s_n1 <- as.numeric(G30s)[i120] *
  (sqrt(sum(scale(go_xyz$val, scale = FALSE)^2) / length(go_xyz$val)) / sqrt(var(go_xyz$val)))
# LA ANCLA DE GETIS Y ORD (1996, p. 267), con la procedencia en dos pasos:
# es la cifra que la ayuda de spdep dice reproducir con n-1 en la varianza.
ancla(G30s_n1, 1.448, "Getis-Ord celda 120: Gi* con n-1 (G&O 1996 p. 267, vía spdep)", tol = 1e-3)
barrido <- lapply(c(30, 60, 90, 120, 150), function(d) {
  nb <- dnearneigh(go_xy, 0, d)
  list(d = d, vecinos_medio = r4(mean(card(nb))),
       G = r4(as.numeric(localG(go_xyz$val, nb2listw(nb, style = "B")))[i120]),
       G_estrella = r4(as.numeric(localG(go_xyz$val, nb2listw(include.self(nb), style = "B")))[i120]))
})
set.seed(SEMILLA)
G30s_p <- localG_perm(go_xyz$val, lw30S, nsim = NSIM, iseed = SEMILLA, no_repeat_in_row = TRUE)

# Gi* sobre Columbus y los municipios, con el mismo NSIM y el mismo p.
gs_col <- localG_perm(col$CRIME, nb2listw(include.self(GAL), style = "W"), nsim = NSIM, iseed = SEMILLA, no_repeat_in_row = TRUE)
gs_col_p <- attr(gs_col, "internals")[, P_COL]
message("   localG_perm sobre los municipios (~10 s)")
gs_mun <- localG_perm(y_mun, nb2listw(include.self(nb_sub), style = "W", zero.policy = TRUE),
                      nsim = NSIM, zero.policy = TRUE, iseed = SEMILLA, no_repeat_in_row = TRUE)
gs_mun_p <- attr(gs_mun, "internals")[, P_COL]
gcod_col <- gistar_codigo(as.numeric(gs_col), gs_col_p)
gcod_mun <- gistar_codigo(as.numeric(gs_mun), gs_mun_p)
gcod_mun[is.na(lisa_mun)] <- NA_integer_         # las islas tampoco tienen Gi*

# LISA frente a Gi*, lado a lado: la tabla cruzada es el módulo entero.
# Un alto-bajo es «significativo» para LISA y nada para Gi*, porque Gi*
# mide intensidad y no similitud.
cruce <- function(lisa, g) {
  caliente <- !is.na(g) & g >= 5L; frio <- !is.na(g) & g <= 3L; nada <- !is.na(g) & g == 4L
  lapply(1:5, function(k) list(lisa = LISA_NIVELES[k],
    caliente = as.integer(sum(lisa == k & caliente, na.rm = TRUE)),
    frio = as.integer(sum(lisa == k & frio, na.rm = TRUE)),
    ninguno = as.integer(sum(lisa == k & nada, na.rm = TRUE))))
}

D$m11 <- list(
  niveles = G_NIVELES, colores = G_COLORES, nsim = NSIM,
  getisord = list(n = length(go_xyz$val), lado = 16L, umbral = 30,
                  vecinos_medio = r4(mean(card(nb30))),
                  celda = i120, x = go_xyz$x[i120], y = go_xyz$y[i120], valor = go_xyz$val[i120],
                  G = r4(as.numeric(G30)[i120]), G_estrella = r4(as.numeric(G30s)[i120]),
                  G_estrella_n1 = r4(G30s_n1),
                  G_estrella_p = r5(attr(G30s_p, "internals")[i120, P_COL]),
                  dif_max_G_Gestrella = r4(max(abs(as.numeric(G30) - as.numeric(G30s)))),
                  barrido = barrido,
                  calientes_95 = as.integer(sum(attr(G30s_p, "internals")[, P_COL] < ALFA & as.numeric(G30s_p) > 0)),
                  frios_95 = as.integer(sum(attr(G30s_p, "internals")[, P_COL] < ALFA & as.numeric(G30s_p) < 0))),
  columbus = list(conteo = gistar_conteo(gcod_col), cruce = cruce(lisa_col, gcod_col),
                  z_max = r4(max(as.numeric(gs_col))), z_min = r4(min(as.numeric(gs_col))),
                  polyid_z_max = as.integer(col$POLYID[which.max(as.numeric(gs_col))])),
  municipios = list(conteo = gistar_conteo(gcod_mun), cruce = cruce(lisa_mun, gcod_mun),
                    z_max = r4(max(as.numeric(gs_mun))), z_min = r4(min(as.numeric(gs_mun))),
                    municipio_z_max = mun$municipio[sub][which.max(as.numeric(gs_mun))],
                    departamento_z_max = mun$departamento[sub][which.max(as.numeric(gs_mun))]))

# =====================================================================
# LAS DISCREPANCIAS DECLARADAS, que el auditor lee
# =====================================================================
D$discrepancias <- list(
  list(id = "moran_islas",
       que = "El I de Moran de la deserción municipal",
       valor_r = r10(rm_mun$I), valor_python = r10(rm_mun$I * length(sub) / sum(tiene_vecino)),
       diferencia = r10(rm_mun$I * length(sub) / sum(tiene_vecino) - rm_mun$I),
       causa = paste("Con zero.policy = TRUE, spdep::moran.test toma n = unidades CON vecinos (1 119 de 1 121)",
                     "mientras esda.Moran toma n = todas. Mismo grafo, misma fórmula, dos convenios:",
                     "el paso de uno a otro es exactamente el factor 1 121/1 119."),
       va_a = "capítulo 7, módulo 9 (las islas en el mapa LISA)"),
  list(id = "p_permutacion",
       que = "Los p por permutación de LISA y Gi*",
       valor_r = NA, valor_python = NA, diferencia = NA,
       causa = paste("spdep y esda permutan con generadores distintos: los Ii coinciden al bit y los p",
                     "solo hasta el error de Monte Carlo, del orden de sqrt(p(1-p)/nsim). El auditor",
                     "compara Ii exactos y p con esa tolerancia, y cuenta las categorías que cambian."),
       va_a = "capítulo 7, módulo 10 (qué p se está corrigiendo)"))

# =====================================================================
# LOS MAPAS
# =====================================================================
message("L. los mapas")

capa_cat <- function(id, etiqueta, valor, niveles, colores, leyenda = "")
  list(id = id, etiqueta = etiqueta, tipo = "categoria", valor = valor,
       niveles = niveles, colores = colores, leyenda = leyenda)

MAPAS[["cap7-columbus"]] <- geo_poligonos(
  col, titulo = "Columbus: CRIME, sus conglomerados LISA y sus puntos calientes",
  presupuesto = 6000L, verbose = FALSE,
  capas = list(
    list(id = "crime", etiqueta = "Tasa de delitos (CRIME)", valor = col$CRIME, estilo = "quantile",
         n_clases = 5, leyenda = "delitos por mil hogares"),
    capa_cat("lisa", "LISA sin corregir (p por rangos < 0,05)", lisa_col, LISA_NIVELES, LISA_COLORES),
    capa_cat("lisa_bonferroni", "LISA con Bonferroni", lisa_col_bonf, LISA_NIVELES, LISA_COLORES),
    capa_cat("lisa_fdr", "LISA con FDR", lisa_col_fdr, LISA_NIVELES, LISA_COLORES),
    capa_cat("gistar", "Gi* de Getis-Ord", gcod_col, G_NIVELES, G_COLORES)))
MAPAS[["cap7-columbus"]]$polyid <- as.integer(col$POLYID)

MAPAS[["cap7-w"]] <- geo_grafo_multi(
  col, W_COL, titulo = "Columbus: once definiciones de vecindad sobre los mismos 49 barrios",
  leyenda = "vecinos", presupuesto = 6000L, verbose = FALSE)

# Las capas municipales viven sobre los 1 122: NA donde no hay dato y en
# las islas. La geometría simplificada viene de la cache con llave.
a1122 <- function(v) { out <- rep(NA, nrow(mun)); out[sub] <- v; out }
gpkg <- file.path(PROC, "colombia_adm2.gpkg")
message("   simplificando los municipios (125 s la primera vez, luego cache con llave)")
mun_simp <- cacheado_gpkg("mun_simplificado", gpkg, "13000",
                          geo_simplifica(mun, presupuesto = 13000L, verbose = FALSE))
MAPAS[["cap7-municipios"]] <- geo_poligonos(
  mun_simp, titulo = "Los 1 122 municipios: deserción, conglomerados LISA y puntos calientes",
  presupuesto = 13000L, verbose = FALSE,
  capas = list(
    list(id = "desercion", etiqueta = "Deserción escolar (%)", valor = a1122(y_mun),
         estilo = "quantile", n_clases = 5, leyenda = "% de deserción"),
    capa_cat("lisa", "LISA sin corregir (p por rangos < 0,05)", as.integer(a1122(lisa_mun)), LISA_NIVELES, LISA_COLORES),
    capa_cat("lisa_bonferroni", "LISA con Bonferroni", as.integer(a1122(lisa_mun_bonf)), LISA_NIVELES, LISA_COLORES),
    capa_cat("lisa_fdr", "LISA con FDR", as.integer(a1122(lisa_mun_fdr)), LISA_NIVELES, LISA_COLORES),
    capa_cat("gistar", "Gi* de Getis-Ord", as.integer(a1122(gcod_mun)), G_NIVELES, G_COLORES)))

# La rejilla de Getis-Ord: el dato y la Gi*, por filas de arriba abajo.
xs <- sort(unique(go_xyz$x)); ys <- sort(unique(go_xyz$y))
fila <- length(ys) + 1L - match(go_xyz$y, ys); colu <- match(go_xyz$x, xs)
M_val <- matrix(NA_real_, length(ys), length(xs)); M_val[cbind(fila, colu)] <- go_xyz$val
M_g   <- matrix(NA_real_, length(ys), length(xs)); M_g[cbind(fila, colu)] <- as.numeric(G30s)
dx <- diff(xs)[1]; dy <- diff(ys)[1]
caja_go <- c(min(xs) - dx / 2, min(ys) - dy / 2, max(xs) + dx / 2, max(ys) + dy / 2)
MAPAS[["cap7-getisord-valor"]] <- geo_rejilla(M_val, caja_go, titulo = "La rejilla de Getis y Ord (1992): el dato",
                                              leyenda = "valor", n_clases = 7, estilo = "quantile")
MAPAS[["cap7-getisord-g"]] <- geo_rejilla(M_g, caja_go, titulo = "La misma rejilla: Gi* con umbral 30",
                                          leyenda = "Gi* (z)", n_clases = 7, estilo = "equal")

# =====================================================================
# LO QUE SE ESCRIBE
# =====================================================================
message("M. escribiendo")

D$meta <- list(
  capitulo = 7L,
  semanas = "12-13",
  semilla = SEMILLA,
  generado = as.character(Sys.Date()),
  tableros = list(laboratorio = "columbus (GAL de Anselin 1988, orden de oldcol)",
                  caso = "municipios de Colombia", rejilla = "getisord (Getis y Ord 1992)"),
  nsim = NSIM, p = P_COL, alfa = ALFA,
  anclas = NA_integer_)
D$meta$anclas <- N_ANCLAS

geo_escribe(D, file.path(SALIDAS, "cap7_datos.json"), presupuesto_kb = 200)
geo_escribe(MAPAS, file.path(SALIDAS, "cap7_mapas.json"), presupuesto_kb = 220)

# Los CSV que leen las pestañas de Python y el auditor.
fwrite(data.table(
  orden = seq_len(nrow(col)), polyid = as.integer(col$POLYID),
  CRIME = col$CRIME, HOVAL = col$HOVAL, INC = col$INC, CP = as.integer(col$CP),
  X = col$X, Y = col$Y,
  z = r10(z_col), wz = r10(wz_col),
  Ii = r10(lmp_col[, "Ii"]), p_rangos = r10(p_col),
  cuadrante = as.character(attr(lmp_col, "quadr")$mean),
  lisa = lisa_col, lisa_bonferroni = lisa_col_bonf, lisa_fdr = lisa_col_fdr,
  gistar_z = r10(as.numeric(gs_col)), gistar_p = r10(gs_col_p), gistar = gcod_col),
  file.path(SALIDAS, "cap7_columbus.csv"))

ar_gal <- aristas_no_dirigidas(GAL)               # parejas {i, j} únicas, i < j
fwrite(data.table(i = ar_gal[, 1], j = ar_gal[, 2], i0 = ar_gal[, 1] - 1L, j0 = ar_gal[, 2] - 1L,
                  polyid_i = as.integer(col$POLYID[ar_gal[, 1]]), polyid_j = as.integer(col$POLYID[ar_gal[, 2]])),
       file.path(SALIDAS, "cap7_columbus_gal.csv"))

fwrite(data.table(celda = seq_along(go_xyz$val), x = go_xyz$x, y = go_xyz$y, val = go_xyz$val,
                  G30 = r10(as.numeric(G30)), G30_estrella = r10(as.numeric(G30s))),
       file.path(SALIDAS, "cap7_getisord.csv"))

fwrite(data.table(
  divipola = mun$divipola[sub], municipio = mun$municipio[sub], departamento = mun$departamento[sub],
  desercion = y_mun, vecinos = card(nb_sub), z = r10(z_mun), wz = r10(wz_mun),
  Ii = r10(lmp_mun[, "Ii"]), p_rangos = r10(p_mun),
  cuadrante = as.character(attr(lmp_mun, "quadr")$mean),
  lisa = lisa_mun, lisa_bonferroni = lisa_mun_bonf, lisa_fdr = lisa_mun_fdr,
  gistar_z = r10(as.numeric(gs_mun)), gistar_p = r10(gs_mun_p), gistar = gcod_mun),
  file.path(SALIDAS, "cap7_municipios_lisa.csv"))

fwrite(rbindlist(lapply(potencia, function(pc) data.table(lado = pc$lado, n = pc$n, rho = RHOS, potencia = pc$potencia))),
       file.path(SALIDAS, "cap7_potencia.csv"))

message(sprintf("\nLISTO. %d anclas comprobadas, ninguna rota.", N_ANCLAS))
