# =====================================================================
# datos_taller2.R — el dato que se descarga el estudiante · C2b
#
#   Estadística Espacial 2026-II (20929) · Corte II
#   Ver PLAN_Taller_2_Cap_4.md, C2b
#
# QUÉ PRODUCE
#   entrega/datos/taller2_sedes.gpkg        2 209 sedes educativas
#   entrega/datos/taller2_localidades.gpkg  las 20 localidades
#   entrega/datos/taller2_patrones.csv      los patrones generados
#
# EL CRITERIO QUE MANDA AQUÍ NACE DE UN FALLO REAL. El Taller 1 se
# repartió el 2026-08-13 con un enunciado que mandaba ejecutar código
# sobre una carpeta que **da 404 fuera del equipo de Javier**, y hubo
# que publicar el dato en un segundo commit el 18 de agosto (`22f4fcc`,
# «el 45 % del escrito ya lo puede ejecutar alguien más»). Por eso este
# guion existe separado del precálculo y por eso sus archivos entran en
# la lista blanca del `.gitignore`: lo que el enunciado manda ejecutar
# tiene que poder ejecutarse desde fuera.
#
# LO QUE ESTOS ARCHIVOS NO PUEDEN LLEVAR. Igual que el JSON: ninguna
# columna que revele la familia de un patrón de T2. Los patrones viajan
# con un identificador opaco —`p01`…`p24` los propios, `t01a`…`t12c` los
# de los tríos— y sin más atributo que las coordenadas. La letra del
# trío es POSICIÓN, no familia: el orden se barajó en el precálculo.
#
# Ejecutar SIEMPRE con el envoltorio:
#     precalculo/rscript.sh precalculo/datos_taller2.R
# =====================================================================

suppressPackageStartupMessages({
  library(sf)
  library(spatstat.geom)
  library(spatstat.random)
  library(jsonlite)
})

AQUI <- "precalculo"
source(file.path(AQUI, "utf8.R"))
source(file.path(AQUI, "puntual.R"))   # ppp_F_borde(): ver `curvas()` abajo

DESTINO <- file.path("entrega", "datos")
dir.create(DESTINO, showWarnings = FALSE, recursive = TRUE)
SALIDAS <- file.path(AQUI, "salidas")

message("A · Las capas de Bogotá")
PROC <- "datos/procesado"
col <- st_read(file.path(PROC, "bogota_colegios.gpkg"),    quiet = TRUE)
loc <- st_read(file.path(PROC, "bogota_localidades.gpkg"), quiet = TRUE)
stopifnot(nrow(col) == 2209, nrow(loc) == 20, st_crs(col)$epsg == 9377)

# Se entrega la capa COMPLETA, las 20 localidades y las 2 209 sedes, y no
# solo las 16 usables: recortarla le diría al estudiante cuáles entraron
# en el sorteo, que es información que no le toca, y además la regla de
# pertenencia de su localidad es suya de calcular.
#
# Se conservan los atributos de marca —sector, calendario, carácter…—
# porque no revelan nada del taller y sí abren la puerta a que alguien
# mire más allá de lo que se le pide.
st_write(col, file.path(DESTINO, "taller2_sedes.gpkg"),
         delete_dsn = TRUE, quiet = TRUE)
st_write(loc, file.path(DESTINO, "taller2_localidades.gpkg"),
         delete_dsn = TRUE, quiet = TRUE)
message(sprintf("    sedes %d · localidades %d · EPSG:%d",
                nrow(col), nrow(loc), st_crs(col)$epsg))

message("B · Los patrones generados")
# Se regeneran con la MISMA semilla que el precálculo, en el mismo orden,
# para que las coordenadas que se entregan sean exactamente las que el
# JSON describe. Si esto se desincroniza, el estudiante calcula sus
# curvas sobre otros puntos que los que el enunciado le enseña, y nada
# falla: las curvas simplemente no cuadran. Se comprueba abajo contra el
# JSON, que es la única forma de verlo.
SEMILLA <- 20262L
set.seed(SEMILLA)
VENTANA <- owin(c(0, 1), c(0, 1))
R_MAX <- 0.25; R_NODOS <- 51L; RG <- seq(0, R_MAX, length.out = R_NODOS)

a_rejilla <- function(fv, colu) {
  x <- as.numeric(fv$r); y <- as.numeric(fv[[colu]])
  ok <- is.finite(x) & is.finite(y)
  as.numeric(approx(x[ok], y[ok], xout = RG, rule = 2)$y)
}
suppressPackageStartupMessages(library(spatstat.explore))
# La F NO sale de `Fest`, y tiene que ser la MISMA decisión que toma
# `genera_taller2.R`: en esta instalación `distmap.ppp()` devuelve
# distancias al cuadrado y `Fest()` las lee como distancias (M-14 del
# plan). `ppp_F_borde()` la calcula sobre una rejilla de sondas con
# `nncross` y `bdist.points`, que sí son exactas, y ya en la rejilla de
# publicación. Si las dos mitades usaran caminos distintos, la
# comprobación C de abajo lo diría — que es exactamente para lo que está.
curvas <- function(p) {
  G <- Gest(p)
  K <- Kest(p, correction = "translate"); g <- pcf(p, correction = "translate")
  Kv <- a_rejilla(K, "trans")
  list(r = round(RG, 10), G = round(a_rejilla(G, "km"), 10),
       F = round(ppp_F_borde(p, RG)$f, 10), K = round(Kv, 10),
       L = round(sqrt(pmax(Kv, 0) / pi) - RG, 10),
       g = round(a_rejilla(g, "trans"), 10))
}
lee_contraste <- function(cv) {
  g <- cv$g; L <- cv$L; r <- cv$r
  i_pico <- which.max(g[-1]) + 1L
  vuelve <- which(seq_along(g) > i_pico & g <= 1.10)
  r_vuelve <- if (length(vuelve)) r[vuelve[1]] else NA_real_
  i_ult <- max(which(L > 0))
  list(g_max = g[i_pico], arrastre = if (is.na(r_vuelve)) NA_real_ else r[i_ult] - r_vuelve)
}
genera_agregado <- function() {
  kappa <- sample(12:30, 1); escala <- runif(1, 0.015, 0.045); mu <- sample(5:12, 1)
  rThomas(kappa = kappa, scale = escala, mu = mu, win = VENTANA)
}
genera_aleatorio <- function() rpoispp(lambda = sample(120:260, 1), win = VENTANA)
genera_regular   <- function() rSSI(r = runif(1, 0.045, 0.065), n = sample(90:150, 1), win = VENTANA)

N_PROPIOS <- 24L; N_TRIOS <- 12L
propios <- vector("list", N_PROPIOS)
for (i in seq_len(N_PROPIOS)) {
  repeat {
    p <- genera_agregado()
    if (npoints(p) < 80 || npoints(p) > 320) next
    cv <- curvas(p); ct <- lee_contraste(cv)
    if (is.na(ct$arrastre) || ct$arrastre < 0.05 || ct$g_max < 2) next
    propios[[i]] <- p; break
  }
}
trios <- vector("list", N_TRIOS)
for (i in seq_len(N_TRIOS)) {
  repeat {
    ps <- list(agregado = genera_agregado(), aleatorio = genera_aleatorio(),
               regular = genera_regular())
    ns <- vapply(ps, npoints, integer(1))
    if (any(ns < 80 | ns > 320)) next
    cvs <- lapply(ps, curvas)
    Gs <- do.call(cbind, lapply(cvs, function(c) c$G))
    sep <- min(c(max(abs(Gs[,1]-Gs[,2])), max(abs(Gs[,1]-Gs[,3])), max(abs(Gs[,2]-Gs[,3]))))
    if (sep < 0.25) next
    o <- sample(3L)
    trios[[i]] <- ps[o]; break
  }
}

filas <- do.call(rbind, c(
  lapply(seq_len(N_PROPIOS), function(i)
    data.frame(patron = sprintf("p%02d", i), x = propios[[i]]$x, y = propios[[i]]$y)),
  unlist(lapply(seq_len(N_TRIOS), function(i)
    lapply(1:3, function(j)
      data.frame(patron = sprintf("t%02d%s", i, letters[j]),
                 x = trios[[i]][[j]]$x, y = trios[[i]][[j]]$y))), recursive = FALSE)))
write.csv(filas, file.path(DESTINO, "taller2_patrones.csv"), row.names = FALSE)
message(sprintf("    %d patrones · %d puntos en total",
                length(unique(filas$patron)), nrow(filas)))

# El identificador no puede llevar la familia dentro.
for (prohibida in c("agregado", "aleatorio", "regular", "thomas", "familia"))
  if (any(grepl(prohibida, filas$patron, ignore.case = TRUE)))
    stop(sprintf("PARADO: el identificador de patrón contiene «%s»", prohibida))

message("C · La comprobación que importa: ¿cuadra con el JSON publicado?")
# Sin esto, una desincronización entre este guion y el precálculo sería
# invisible: los dos correrían en verde y el estudiante calcularía sobre
# otros puntos.
#
# SE COMPARAN LAS CINCO CURVAS, no solo la G. Comparar solo G fue el
# agujero que dejó pasar M-14 durante toda la construcción: la F llevaba
# meses sin ser la función de espacio vacío y ni esta comprobación ni el
# auditor la miraban. Una comprobación que mira una de cinco columnas da
# la misma sensación de verde que una que las mira todas.
jd <- jsonlite::fromJSON(file.path(SALIDAS, "taller2_datos.json"), simplifyVector = FALSE)
cmp <- function(a, b, que, tol = 1e-8) {
  d <- max(abs(as.numeric(a) - as.numeric(b)))
  if (!is.finite(d) || d > tol)
    stop(sprintf("PARADO: %s no cuadra con el JSON (dif %.2e). El dato entregado y el enunciado describen patrones DISTINTOS", que, d))
  invisible(TRUE)
}
COLUMNAS <- c("G", "F", "K", "L", "g")
n_cmp <- 0L
for (i in seq_len(N_PROPIOS)) {
  cv <- curvas(propios[[i]])
  for (co in COLUMNAS) {
    cmp(cv[[co]], unlist(jd$patrones[[i]][[co]]), sprintf("la %s del propio %d", co, i))
    n_cmp <- n_cmp + 1L
  }
}
for (i in seq_len(N_TRIOS)) for (j in 1:3) {
  cv <- curvas(trios[[i]][[j]])
  for (co in COLUMNAS) {
    cmp(cv[[co]], unlist(jd$trios[[i]][[j]][[co]]),
        sprintf("la %s del trío %d posición %s", co, i, letters[j]))
    n_cmp <- n_cmp + 1L
  }
}
message(sprintf("    %d curvas comparadas contra el JSON (%d patrones x %d columnas), todas cuadran",
                n_cmp, N_PROPIOS + N_TRIOS * 3L, length(COLUMNAS)))

for (f in list.files(DESTINO, pattern = "^taller2_", full.names = TRUE))
  message(sprintf("    %-42s %6.1f KB", f, file.size(f) / 1024))
message("\nHECHO")
