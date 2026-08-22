# =====================================================================
# puntual.R — la librería de patrones puntuales de los capítulos 4 y 5
#
# Material de Estadística Espacial 2026-II (20929). T3.1.
#
# POR QUÉ NO VIVE EN geo.R. `geo.R` lo cargan los capítulos 1, 2 y 3, y
# ninguno de los tres necesita spatstat, que tarda lo suyo en adjuntarse.
# Lo puntual va aparte por la misma razón por la que `fuentes.R` y
# `utf8.R` van aparte: cada guion carga lo que usa.
#
# POR QUÉ EXISTE, que es lo importante. Estas funciones las necesitan DOS
# guiones —`genera_cap4.R` y la sección del capítulo 4 de
# `genera_soluciones.R`— y una de ellas encierra una convención que ya se
# equivocó dos veces. Copiada en dos archivos, se desincroniza y el
# ejercicio deja de comprobar lo que el módulo enseña, sin que nada falle.
# =====================================================================

suppressPackageStartupMessages({
  library(spatstat)
})

# El nombre del argumento y el de la columna NO coinciden, y pedir la
# columna por el nombre del argumento devuelve NULL: `approx()` muere
# después con un mensaje que no menciona ninguno de los dos. Los dos
# nombres, en un solo sitio.
PPP_CORR     <- "translate"   # lo que se le pide a spatstat
PPP_CORR_COL <- "trans"       # como se llama la columna que devuelve

#' Vértices de una ventana, sumando todas sus partes
ppp_vertices <- function(w) sum(vapply(w$bdry, function(b) length(b$x), integer(1)))

#' Rejilla de publicación para una curva de spatstat
#'
#' Las curvas se CALCULAN en la rejilla fina que elija spatstat y se
#' PUBLICAN en una de `n` nodos. No al revés: pasarle una r gruesa a
#' `Kest` cambia la estimación —el estimador de bordes trabaja sobre los
#' intervalos que se le den— y `pcf` necesita rejilla fina para suavizar.
ppp_rejilla_r <- function(fv, n = 101L) seq(0, max(fv$r), length.out = n)

#' Una columna de un objeto `fv`, interpolada a la rejilla de publicación
ppp_curva <- function(fv, col, rg) {
  y <- as.numeric(fv[[col]])
  if (is.null(y) || !length(y))
    stop(sprintf("la columna `%s` no existe en el objeto fv (¿es `%s` y no `%s`?)",
                 col, PPP_CORR_COL, PPP_CORR))
  ok <- is.finite(y)
  if (sum(ok) < 2L) stop(sprintf("la columna `%s` no tiene dos valores finitos", col))
  approx(fv$r[ok], y[ok], xout = rg, rule = 2)$y
}

#' Rebarajar un patrón conservando EXACTAMENTE el conteo de cada celda
#'
#' Devuelve un patrón con los mismos conteos por celda que `p` en una
#' rejilla nx x ny, pero con los puntos repartidos uniformemente dentro
#' de la suya. El chi2 del test de cuadrantes sale idéntico hasta el
#' último decimal; la estructura a escala menor que la celda desaparece.
#' Es la demostración del módulo 5 y el ejercicio E2 del capítulo 4.
#'
#' UNA SOLA CONVENCIÓN DE CELDA, y costó dos intentos llegar a ella.
#'
#'  1. Binar con `findInterval` discrepa con `quadratcount` en los puntos
#'     que caen EXACTAMENTE sobre el borde de una celda. Con `redwood`
#'     —coordenadas a dos decimales, bordes en 0,2, 0,4, 0,6 y 0,8— hay
#'     varios, y los conteos salían casi iguales, que es la forma más
#'     cara de estar mal.
#'
#'  2. Usar la teselación de spatstat, `cut(X, quadrats(X, nx, ny))`,
#'     TAMPOCO coincide con `quadratcount`: son dos funciones del mismo
#'     paquete y no reparten igual los puntos del borde. Comprobado, no
#'     supuesto: con `redwood` y nx = 5 los dos repartos dan
#'     multiconjuntos de conteos distintos —uno tiene una celda con 9
#'     puntos y el otro ninguna—.
#'
#' `quadratcount()` bina con `cut()`: intervalos abiertos por la
#' izquierda y cerrados por la derecha, con el más bajo cerrado por los
#' dos lados. Se reprodujo su tabla entera con `cut()` a mano para
#' confirmarlo. Como el chi2 sale de `quadrat.test()`, que cuenta con
#' `quadratcount()`, ESA es la convención que manda. Los puntos nuevos
#' salen de `runif` y no caen nunca sobre un borde, así que del lado
#' rebarajado no hay ambigüedad.
ppp_rebaraja <- function(p, nx, ny = nx, semilla) {
  set.seed(semilla)
  w <- p$window
  bx <- seq(w$xrange[1], w$xrange[2], length.out = nx + 1)
  by <- seq(w$yrange[1], w$yrange[2], length.out = ny + 1)
  ix <- cut(p$x, bx, include.lowest = TRUE)
  iy <- cut(p$y, by, include.lowest = TRUE)
  if (anyNA(ix) || anyNA(iy)) stop("un punto quedó fuera de la rejilla de celdas")
  xs <- numeric(0); ys <- numeric(0)
  for (i in seq_len(nx)) for (j in seq_len(ny)) {
    k <- sum(as.integer(ix) == i & as.integer(iy) == j)
    if (k == 0) next
    xs <- c(xs, runif(k, bx[i], bx[i + 1]))
    ys <- c(ys, runif(k, by[j], by[j + 1]))
  }
  q <- ppp(xs, ys, window = w)
  # La comprobación viaja CON la función, no con quien la llama: si el
  # reparto dejara de conservar los conteos, lo que se cae es la
  # demostración del módulo 5 y el ejercicio E2 a la vez.
  if (!identical(as.vector(quadratcount(p, nx = nx, ny = ny)),
                 as.vector(quadratcount(q, nx = nx, ny = ny))))
    stop("ppp_rebaraja: los conteos por celda no se conservaron")
  q
}
