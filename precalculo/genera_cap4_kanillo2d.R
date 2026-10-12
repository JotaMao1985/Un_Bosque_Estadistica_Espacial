# =====================================================================
# genera_cap4_kanillo2d.R — las cifras de referencia de la animación «K es un disco, g un anillo»
#
#   Capítulo 4, módulos 8 y 9 · Material de Estadística Espacial 2026-II (20929).
#
# QUÉ PRODUCE
#   precalculo/salidas/cap4_kanillo2d.json           coordenadas crudas y referencias, para las pruebas
#   precalculo/salidas/cap4_kanillo2d_resumen.json   las cifras que cita la prosa de los módulos 8 y 9
#
# POR QUÉ ES UN SCRIPT APARTE Y NO UN BLOQUE DE `genera_cap4.R`
#   La animación (`anim2d/kanillo2d.js`) cuenta en el navegador los vecinos de cada punto
#   dentro de un disco o de un anillo, con o sin el peso de traslación, y calcula K̂ con
#   esas cuentas. Es aritmética que ningún auditor de prosa ve, y se prueba contra ESTAS
#   cifras. Regenerar `genera_cap4.R` entero movería cada cifra del capítulo —y las del
#   Taller 2, que se reparte con ellas—; este archivo no usa azar y no toca nada más.
#
# LAS COORDENADAS SON LAS CRUDAS de spatstat.data. El capítulo trae las de los mapas
#   cuantizadas (q = 4096, error ≈ 1e-4), y con ellas muchas parejas que están EXACTAMENTE
#   a una distancia de la rejilla de r (los pinos y las secuoyas vienen en una rejilla de
#   0.01) caerían a un lado o a otro por azar del redondeo. Pesan ~3 KB.
#
# LOS EMPATES SE CUENTAN DENTRO. Una pareja a distancia r está en el disco de radio r
#   (d ≤ r, como dice la definición), con una tolerancia de 1e-9 para que la raíz en coma
#   flotante no decida. `Kest` no siempre lo hace así en un nodo con empates (bina sobre
#   su propia rejilla): fuera de esos nodos coincide con la cuenta de aquí a 1e-12 y se
#   comprueba; en ellos se publica cuántos hay y en qué r, para que la prueba los lea.
#
# LA CURVA DEL CAPÍTULO NO ES LA DE AQUÍ EN ESOS NODOS. `D4.m8[...].k_obs` interpola la
#   rejilla de 513 nodos de `Kest` en la de 101 del capítulo, y en un nodo con empates eso
#   cuenta la pareja a medias (pinos, r = 0.01: K/πr² publicada 0.74, exacta 1.55). Y fuera
#   de los empates también puede diferir, en lo que mide un escalón de K entre dos nodos de
#   la rejilla de Kest (≤ 0.002 en estos tres patrones; en K/πr², hasta 0.15 en las
#   secuoyas a r = 0.02, donde πr² es pequeño). La animación calcula la suya, exacta, y su
#   pie lo dice.
#
# EL ANILLO ES GEOMETRÍA, NO EL ESTIMADOR. La g que se traza es la publicada (`pcf`, que
#   en spatstat.explore 3.8.0 suaviza en la escala del área, πd², con un núcleo de
#   Epanechnikov): su ventana no es un anillo de ancho fijo en r. La animación dibuja un
#   anillo de ancho 2 × H_ANILLO solo para que se vea qué parejas están «a esa distancia»,
#   y cuenta las de un punto; aquí se publican esas cuentas para probarlas.
#
# Ejecutar con el envoltorio, desde la carpeta `Estadistica espacial/`:
#     sh precalculo/rscript.sh precalculo/genera_cap4_kanillo2d.R
# =====================================================================

suppressPackageStartupMessages({
  library(spatstat.explore)
  library(spatstat.data)
  library(jsonlite)
})

AQUI <- "precalculo"
source(file.path(AQUI, "utf8.R"))

SALIDAS <- file.path(AQUI, "salidas")
PATRONES <- c("cells", "japanesepines", "redwood")
NOMBRES <- c(cells = "Células", japanesepines = "Pinos japoneses", redwood = "Secuoyas")
R_NODOS <- seq(0, 0.25, length.out = 101L)   # la rejilla de las curvas del capítulo (D4.m8 / D4.m9)
EPS <- 1e-9                                   # una pareja a distancia r está DENTRO del disco de radio r
H_ANILLO <- 0.01                              # medio ancho del anillo que se dibuja
R_CUENTAS <- c(0.02, 0.04, 0.06, 0.1, 0.145, 0.15, 0.2, 0.25)   # r en que se publica la cuenta de cada punto

ancla <- function(calculado, esperado, que, tol = 1e-9) {
  d <- max(abs(as.numeric(calculado) - as.numeric(esperado)))
  if (!is.finite(d) || d > tol)
    stop(sprintf("ANCLA ROTA · %s: diferencia %.3e (tolerancia %.1e)", que, d, tol))
  invisible(TRUE)
}

# La versión de spatstat de la que salen las curvas del capítulo: si cambia, `Kest` y `pcf` pueden cambiar.
if (as.character(packageVersion("spatstat.explore")) != "3.8.0")
  stop("spatstat.explore no es la 3.8.0 con que se calculó el capítulo 4")

D4 <- fromJSON(file.path(SALIDAS, "cap4_datos.json"), simplifyVector = TRUE)
CSV <- read.csv(file.path(SALIDAS, "cap4_regimenes.csv"))

un_patron <- function(nm) {
  p <- get(nm)
  n <- npoints(p); A <- area(Window(p))
  a <- diff(p$window$xrange); b <- diff(p$window$yrange)
  if (!is.rectangle(Window(p))) stop(nm, ": la ventana no es un rectángulo")
  # Las coordenadas son las del CSV del capítulo, dato a dato (las dos salen de spatstat.data).
  cs <- CSV[CSV$patron == nm, ]
  ancla(c(cs$x, cs$y), c(p$x, p$y), sprintf("%s: las coordenadas son las del CSV del capítulo", nm), tol = 0)

  dx <- outer(p$x, p$x, "-"); dy <- outer(p$y, p$y, "-")
  d <- sqrt(dx^2 + dy^2)
  fuera <- row(d) != col(d)
  w <- A / ((a - abs(dx)) * (b - abs(dy)))          # peso de traslación: |W| / |W ∩ (W + xᵢ − xⱼ)|
  K <- function(r, peso) {
    dentro <- fuera & d <= r + EPS
    A / (n * (n - 1)) * (if (peso) sum(w[dentro]) else sum(dentro))
  }
  k_tr <- vapply(R_NODOS, K, 0, peso = TRUE)
  k_sin <- vapply(R_NODOS, K, 0, peso = FALSE)

  # Contra `Kest` en la misma rejilla: igual fuera de los nodos con empates.
  ke <- Kest(p, r = R_NODOS, correction = c("none", "translate"))
  empates <- vapply(R_NODOS, function(r) sum(abs(d[fuera] - r) < EPS) / 2L, 0)
  limpio <- empates == 0
  ancla(k_tr[limpio], ke$trans[limpio], sprintf("%s: K de traslación = Kest fuera de los empates", nm), tol = 1e-12)
  ancla(k_sin[limpio], ke$un[limpio], sprintf("%s: K sin corregir = Kest fuera de los empates", nm), tol = 1e-12)
  if (!all(k_sin <= k_tr + 1e-15)) stop(nm, ": la K sin corregir pasa a la corregida en algún r")

  # Las cuentas de cada punto: en el disco (crudas y con peso) y en el anillo [r − H, r + H] (crudas).
  cuentas <- lapply(R_CUENTAS, function(r) {
    disco <- fuera & d <= r + EPS
    anillo <- fuera & d >= max(0, r - H_ANILLO) - EPS & d <= r + H_ANILLO + EPS
    list(r = r,
         disco = I(as.integer(rowSums(disco))),
         disco_peso = I(rowSums(ifelse(disco, w, 0))),
         anillo = I(as.integer(rowSums(anillo))))
  })
  # La K del capítulo, en los nodos sin empates, es la de aquí a la precisión de su interpolación.
  pub <- D4$m8[[nm]]$k_obs
  list(nombre = unname(NOMBRES[nm]), n = n, area = A,
       ventana = I(c(p$window$xrange[1], p$window$yrange[1], p$window$xrange[2], p$window$yrange[2])),
       x = I(p$x), y = I(p$y),
       k_traslacion = I(k_tr), k_sin = I(k_sin),
       kest_traslacion = I(ke$trans), kest_sin = I(ke$un),
       empates = I(as.integer(empates)),
       dif_publicada_sin_empates = max(abs(k_tr - pub)[limpio]),
       peso_max = max(w[fuera & d <= max(R_NODOS) + EPS]),
       cuentas = cuentas)
}

out <- list(
  meta = list(capitulo = 4L, modulos = I(c(8L, 9L)), r = I(R_NODOS), eps = EPS, h_anillo = H_ANILLO,
              spatstat_explore = as.character(packageVersion("spatstat.explore")),
              fuente = "spatstat.data (cells, japanesepines, redwood); K a mano con el peso de traslación, contra Kest"),
  patrones = setNames(lapply(PATRONES, un_patron), PATRONES))

# Lo que la prosa del módulo 9 lee: dónde vuelve g a 1 en las secuoyas (del capítulo, no de aquí) y cuánto vale
# K/πr² allí y al final del barrido; y lo que lee la del módulo 8: cuánto se queda corta la K sin corregir.
rw <- out$patrones$redwood
r1 <- D4$m9$redwood$r_vuelve_a_1
j1 <- which(abs(R_NODOS - r1) < 1e-12)
if (length(j1) != 1L) stop("el r en que g vuelve a 1 no es un nodo de la rejilla")
if (rw$empates[j1] != 0) stop("hay empates justo en el r en que g vuelve a 1: la K de aquí y la del capítulo no coinciden ahí")
j_fin <- length(R_NODOS)
razon <- function(k, j) as.numeric(k[j]) / (pi * R_NODOS[j]^2)      # sin AsIs: si no, sale como [x]
ancla(razon(rw$k_traslacion, j1), razon(D4$m8$redwood$k_obs, j1),
      "K/πr² de las secuoyas donde g vuelve a 1: la de aquí es la del capítulo",
      tol = 2e-5)                                  # el capítulo publica K con seis decimales: ~7e-6 en el cociente
if (!(razon(rw$k_traslacion, j1) > 1.5 && abs(D4$m9$redwood$g_obs[j1] - 1) < 0.05))
  stop("en las secuoyas, donde g vuelve a 1, K ya no está claramente por encima: la prosa del módulo 9 lo afirma")
resumen <- list(
  secuoyas_r_g_vuelve = r1,
  secuoyas_k_razon_g_vuelve = razon(rw$k_traslacion, j1),
  secuoyas_k_razon_final = razon(rw$k_traslacion, j_fin),
  secuoyas_sin_sobre_con_final = as.numeric(rw$k_sin[j_fin]) / as.numeric(rw$k_traslacion[j_fin]),
  h_anillo = H_ANILLO)
# La prosa afirma que la K de las secuoyas no baja de πr² en todo el barrido a partir de su pareja más próxima.
desde <- R_NODOS >= D4$m3$redwood$nn_min - 1e-12
if (!all(rw$k_traslacion[desde] / (pi * R_NODOS[desde]^2) > 1))
  stop("la K de las secuoyas baja de πr² en algún r del barrido")

escribe <- function(obj, nombre) {
  txt <- toJSON(obj, auto_unbox = TRUE, digits = 15, null = "null", na = "null")
  if (grepl('"NA"', txt, fixed = TRUE)) stop("hay NA escritos como la cadena \"NA\"")
  destino <- file.path(SALIDAS, nombre)
  writeLines(txt, destino, useBytes = TRUE)
  message(sprintf("  %s: %.1f KB", nombre, file.size(destino) / 1024))
}
escribe(out, "cap4_kanillo2d.json")
# EL RESUMEN QUE CITA LA PROSA, aparte a propósito (la lección del capítulo 6): el auditor de cifras indexa TODO número
# de los JSON que se le dan, y las coordenadas y las cuentas traen cientos; con ellos, un entero corto inyectado como
# defecto cae en el índice por azar y el auditor deja de verlo.
escribe(resumen, "cap4_kanillo2d_resumen.json")
for (nm in PATRONES) {
  pz <- out$patrones[[nm]]
  message(sprintf("  %-14s n=%d · nodos con empates: %d · |K exacta − capítulo| sin empates ≤ %.1e · peso máx %.3f",
                  nm, pz$n, sum(pz$empates > 0), pz$dif_publicada_sin_empates, pz$peso_max))
}
message(sprintf("  secuoyas: g vuelve a 1 en r = %.4f, donde K/πr² = %.4f; en r = 0.25, %.4f; sin corregir/corregida = %.4f",
                resumen$secuoyas_r_g_vuelve, resumen$secuoyas_k_razon_g_vuelve,
                resumen$secuoyas_k_razon_final, resumen$secuoyas_sin_sobre_con_final))
