# =====================================================================
# genera_apendicea.R — el precálculo del apéndice A
#
#   «La densidad en una dimensión»
#   Material de Estadística Espacial 2026-II (20929).
#
# QUÉ PRODUCE
#   precalculo/salidas/apendicea_datos.json       las cifras de los 13 módulos
#   precalculo/salidas/apendicea_soluciones.json  los diez ejercicios guiados
#   precalculo/salidas/apendicea_mc.csv           el Monte Carlo del módulo 11,
#                                                 réplica a réplica
#   precalculo/salidas/apendicea_mc_muestras.csv  las muestras de 20 réplicas,
#                                                 para que el auditor las rehaga
#
# DE DÓNDE SALE. El apéndice adapta un documento del profesor
# (`JMS_Densidades.Rmd`, «Estadística no paramétrica · Densidades»), que
# vive fuera de este repositorio. De él se conservan los ejemplos de
# cálculo a mano y los nueve ejercicios; TODAS sus cifras se recalculan
# aquí, y las que dependían de otra semilla cambian (la casa usa 2026).
#
# POR QUÉ UN APÉNDICE Y NO UN CAPÍTULO. El capítulo 5 estima intensidades
# por núcleos en el plano, y usa σ, cuatro núcleos, cuatro selectores y la
# corrección de borde sin la teoría de la que salen: en una dimensión todo
# eso se puede dibujar y calcular a mano. Cada módulo cierra con su gemelo
# espacial, así que el apéndice también calcula cosas sobre las sedes de
# Bogotá (módulos 4, 9 y 12, y el ejercicio 10).
#
# LA REGLA QUE MANDA (D10): ninguna cifra del apéndice se escribe a mano.
#
# LOS DATOS. `faithful` (datasets), simulados con la semilla de la casa,
# los ejemplos de juguete del documento original, las 2 107 sedes de
# `cap5_bogota_urbana.csv` y las 262 de `cap5_kennedy.csv` (las dos
# versionadas) y el perímetro urbano de `datos/procesado/`, del que solo
# se lee el área.
#
# Ejecutar SIEMPRE con el envoltorio:
#     precalculo/rscript.sh precalculo/genera_apendicea.R
# desde la carpeta `Estadistica espacial/`. Ver utf8.R y rscript.sh.
# =====================================================================

suppressPackageStartupMessages({
  library(jsonlite)
  library(spatstat)
  library(sf)
  library(KernSmooth)
})

AQUI <- "precalculo"
source(file.path(AQUI, "utf8.R"))     # PRIMERO: para si el proceso no es UTF-8
source(file.path(AQUI, "geo.R"))      # geo_escribe()

SALIDAS <- file.path(AQUI, "salidas")
PROC    <- "datos/procesado"
dir.create(SALIDAS, showWarnings = FALSE, recursive = TRUE)

SEMILLA <- 2026L
options(stringsAsFactors = FALSE)

r4  <- function(x) round(as.numeric(x), 4)
r5  <- function(x) round(as.numeric(x), 5)
r6  <- function(x) round(as.numeric(x), 6)
r10 <- function(x) round(as.numeric(x), 10)

N_ANCLAS <- 0L
N_GUARDAS <- 0L

# ---------------------------------------------------------------------
# ancla() — la transcripción contra la literatura, que PARA si falla.
# Misma función que los capítulos 4 a 6: una cifra que no cuadra con su
# fuente tiene que romper el precálculo, no salir publicada.
# ---------------------------------------------------------------------
ancla <- function(calculado, publicado, que, tol = 1e-6) {
  N_ANCLAS <<- N_ANCLAS + 1L
  d <- abs(as.numeric(calculado) - as.numeric(publicado))
  if (!is.finite(d) || d > tol)
    stop(sprintf("ANCLA ROTA · %s: calculado %.8f, la fuente publica %.8f (dif %.2e)",
                 que, as.numeric(calculado), as.numeric(publicado), d))
  invisible(TRUE)
}

# guarda() — una afirmación de FORMA que la prosa hace sobre una cifra.
# «La UCV ve tres modas y las demás dos», «el ASH se acerca al triangular
# a medida que m crece»: si el dato deja de decirlo, el texto mentiría con
# aspecto de correcto. Es la lección del umbral (2026-09-17): las frases de
# forma se vigilan en R, no se confían al ojo.
guarda <- function(ok, que) {
  N_GUARDAS <<- N_GUARDAS + 1L
  if (!isTRUE(ok)) stop("GUARDA ROTA · ", que)
  invisible(TRUE)
}

trapecio <- function(x, y) sum(diff(x) * (head(y, -1) + tail(y, -1)) / 2)

# ---------------------------------------------------------------------
# Contar modas. DOS definiciones, porque son dos objetos distintos, y el
# JavaScript de los simuladores usa exactamente las mismas (lo comprueba
# `prueba_densidad1d.py`).
#
#  · modas_escalon: alturas de las barras de un histograma. Las barras
#    iguales y contiguas son UNA meseta; una meseta es moda si es más alta
#    que lo que tiene a los dos lados (fuera del histograma la altura es 0).
#  · modas_curva: una curva evaluada en una rejilla. Mismo criterio sobre
#    la secuencia comprimida, que es lo que hace que un máximo plano de dos
#    nodos cuente una vez y no cero ni dos.
# ---------------------------------------------------------------------
modas_secuencia <- function(y) {
  r <- rle(as.numeric(y))$values
  if (length(r) == 0) return(0L)
  izq <- c(0, head(r, -1)); der <- c(tail(r, -1), 0)
  sum(r > izq & r > der & r > 0)
}
donde_modas <- function(x, y) {
  # Las posiciones de las modas de una curva (para la prosa del módulo 10).
  rl <- rle(as.numeric(y)); fin <- cumsum(rl$lengths); ini <- fin - rl$lengths + 1
  r <- rl$values; izq <- c(0, head(r, -1)); der <- c(tail(r, -1), 0)
  k <- which(r > izq & r > der & r > 0)
  x[floor((ini[k] + fin[k]) / 2)]
}

# Los núcleos en la escala de SOPORTE [-1, 1] (la de la tabla 3.1 del texto
# guía), y aparte el factor que pasa a la convención de `density()`, donde
# `bw` es la DESVIACIÓN TÍPICA del núcleo.
NUC <- list(
  gaussiano   = function(u) dnorm(u),
  epanechnikov = function(u) ifelse(abs(u) <= 1, 0.75 * (1 - u^2), 0),
  uniforme    = function(u) ifelse(abs(u) <= 1, 0.5, 0),
  triangular  = function(u) ifelse(abs(u) <= 1, 1 - abs(u), 0),
  biweight    = function(u) ifelse(abs(u) <= 1, (15 / 16) * (1 - u^2)^2, 0),
  triweight   = function(u) ifelse(abs(u) <= 1, (35 / 32) * (1 - u^2)^3, 0))

D <- list()

# =====================================================================
# 0. LOS DATOS QUE SE REPITEN
# =====================================================================
message("0. los datos")
data(faithful)
ERU <- faithful$eruptions
N_ERU <- length(ERU)
# `faithful` es el conjunto canónico de R y sus resúmenes están en todos
# los textos; si un día cambiara, el apéndice entero hablaría de otro dato.
ancla(N_ERU, 272, "observaciones de faithful", tol = 0)
ancla(sd(ERU), 1.141371, "sd de faithful$eruptions", tol = 1e-6)
ancla(IQR(ERU), 2.2915, "IQR de faithful$eruptions", tol = 1e-9)

sedes <- read.csv(file.path(SALIDAS, "cap5_bogota_urbana.csv"))
N_SEDES <- nrow(sedes)
ancla(N_SEDES, 2107, "sedes urbanas de Bogotá (las del capítulo 5)", tol = 0)
ken <- read.csv(file.path(SALIDAS, "cap5_kennedy.csv"))
ancla(nrow(ken), 262, "sedes de Kennedy (las del capítulo 5)", tol = 0)

ventana <- st_read(file.path(PROC, "bogota_ventana_urbana.gpkg"), quiet = TRUE)
AREA_KM2 <- as.numeric(sum(st_area(ventana))) / 1e6
# El capítulo 5 publica la misma área (módulo 8, la cuadratura forzada).
ancla(AREA_KM2, 370.0898165101, "área del perímetro urbano (km²)", tol = 1e-6)

# =====================================================================
# A. MÓDULO 1 — Densidad e intensidad: el área es la probabilidad
#
# La cafetería del documento original: dos tipos de pedido, y la media cae
# en el valle. Se simula con la semilla de la casa.
# =====================================================================
message("A. modulo 1 - la cafeteria")
set.seed(SEMILLA)
CAF <- list(n1 = 60L, mu1 = 3.5, sd1 = 0.7, n2 = 40L, mu2 = 9.5, sd2 = 1.4)
bebidas <- rnorm(CAF$n1, CAF$mu1, CAF$sd1)
comidas <- rnorm(CAF$n2, CAF$mu2, CAF$sd2)
tiempos <- c(bebidas, comidas)
n_caf <- length(tiempos)
cortes1 <- seq(floor(min(tiempos)), ceiling(max(tiempos)), by = 1)
h1 <- hist(tiempos, breaks = cortes1, plot = FALSE, right = FALSE)
guarda(sum(h1$counts) == n_caf, "m1: el histograma cuenta los 100 tiempos")
guarda(abs(sum(h1$density * diff(h1$breaks)) - 1) < 1e-12, "m1: el área del histograma es 1")
i_max <- which.max(h1$counts)
media_caf <- mean(tiempos)
i_media <- findInterval(media_caf, cortes1)
en_valle <- sum(tiempos >= 5 & tiempos < 7)
# La media tiene que caer donde casi no hay datos: es la tesis del módulo.
guarda(h1$counts[i_media] <= 3, "m1: la media cae en una barra casi vacía")
guarda(modas_secuencia(h1$density) == 2, "m1: el histograma de la cafetería tiene dos modas")
# La prosa dice que la mediana «describe a los clientes de bebida»: tiene que
# caer antes del valle, del lado de los rápidos.
guarda(median(tiempos) < 5, "m1: la mediana cae del lado de los clientes de bebida")

D$m1 <- list(
  diseno = CAF,
  n = n_caf,
  media = r10(media_caf),
  mediana = r10(median(tiempos)),
  min = r10(min(tiempos)), max = r10(max(tiempos)),
  cortes = cortes1,
  conteos = h1$counts,
  densidades = r10(h1$density),
  ancho = 1,
  barra_max = list(desde = cortes1[i_max], hasta = cortes1[i_max + 1],
                   conteo = h1$counts[i_max], densidad = r10(h1$density[i_max]),
                   densidad_por_hora = r10(60 * h1$density[i_max]),
                   intensidad = h1$counts[i_max]),
  barra_media = list(desde = cortes1[i_media], hasta = cortes1[i_media + 1],
                     conteo = h1$counts[i_media], densidad = r10(h1$density[i_media])),
  valle = list(desde = 5, hasta = 7, conteo = en_valle, proporcion = r10(en_valle / n_caf)),
  modas = modas_secuencia(h1$density),
  minutos_por_hora = 60L,
  tiempos = r6(tiempos))

# El puente: la intensidad de las sedes, n entre el área.
D$m1$sedes <- list(n = N_SEDES, area_km2 = r10(AREA_KM2),
                   lambda_km2 = r10(N_SEDES / AREA_KM2))

# =====================================================================
# B. MÓDULO 2 — El histograma: dos perillas
# =====================================================================
message("B. modulo 2 - el histograma")
# Un histograma con convención [a, b): ancho h y origen o (la fracción de
# h en que se corre la rejilla). Misma función que `densidad1d.js`.
histograma <- function(x, h, frac) {
  o <- frac * h
  a <- floor((min(x) - o) / h) * h + o
  br <- a + h * (0:(floor((max(x) - a) / h) + 1))
  cnt <- hist(x, breaks = br, plot = FALSE, right = FALSE)$counts
  list(cortes = br, conteos = cnt, densidad = cnt / (length(x) * h))
}
h_def <- hist(ERU, plot = FALSE)          # lo que hace R sin que se le pida nada
anchos2 <- seq(0.10, 1.00, by = 0.05)
fracs2 <- seq(0, 0.95, by = 0.05)
tab_modas <- t(sapply(anchos2, function(h) sapply(fracs2, function(f)
  modas_secuencia(histograma(ERU, h, f)$densidad))))
rango <- data.frame(h = anchos2, min = apply(tab_modas, 1, min),
                    max = apply(tab_modas, 1, max))
# El ancho que se enseña: el mayor en el que mover SOLO el origen cambia el
# número de modas. Se elige aquí, no a ojo, y se dice por qué.
cambia <- rango$h[rango$max > rango$min]
guarda(length(cambia) > 0, "m2: hay algún ancho en el que el origen cambia las modas")
H_ORIGEN <- max(cambia[cambia <= 0.5])
fila_o <- tab_modas[which(abs(anchos2 - H_ORIGEN) < 1e-9), ]
f_pocas <- fracs2[which.min(fila_o)]; f_muchas <- fracs2[which.max(fila_o)]
guarda(min(fila_o) == 2 && max(fila_o) >= 3,
       "m2: en el ancho elegido el origen lleva de dos modas a tres o más")
# Y el efecto de escala, con el origen quieto (frac = 0).
modas_escala <- tab_modas[, 1]
h_fd <- 2 * IQR(ERU) * N_ERU^(-1 / 3)
h_scott_hist <- 3.5 * sd(ERU) * N_ERU^(-1 / 3)
# La prosa: con 272 erupciones Sturges todavía da barras MÁS ESTRECHAS que
# Scott y FD. La primera versión decía lo contrario («con muchos datos produce
# muy pocas barras») y su propio ejemplo la desmentía (revisión 2).
guarda(diff(h_def$breaks)[1] < h_scott_hist && diff(h_def$breaks)[1] < h_fd,
       "m2: con estas erupciones Sturges da barras más estrechas que Scott y FD")
D$m2 <- list(
  n = N_ERU,
  sturges_clases = nclass.Sturges(ERU),
  def_cortes = h_def$breaks, def_clases = length(h_def$breaks) - 1L,
  def_ancho = r10(diff(h_def$breaks)[1]),
  fd = list(h = r10(h_fd), clases = nclass.FD(ERU)),
  scott = list(h = r10(h_scott_hist), constante = 3.5,
               # el óptimo exacto para una normal: (6 · 4√π)^(1/3) σ n^(-1/3)
               constante_exacta = r10((24 * sqrt(pi))^(1 / 3))),
  anchos = anchos2, fracs = fracs2,
  modas_min = rango$min, modas_max = rango$max,
  h_origen = H_ORIGEN,
  origen = list(frac_pocas = f_pocas, frac_muchas = f_muchas,
                desplaza_pocas = r10(f_pocas * H_ORIGEN),
                desplaza_muchas = r10(f_muchas * H_ORIGEN),
                modas_pocas = min(fila_o), modas_muchas = max(fila_o),
                n_origenes = length(fila_o),
                origenes_pocas = sum(fila_o == min(fila_o)),
                origenes_muchas = sum(fila_o == max(fila_o))),
  escala_modas_origen0 = modas_escala,
  eruptions = r6(ERU))
# La tasa: sesgo O(h), varianza O(1/(nh)) → h ∝ n^(-1/3), MISE ∝ n^(-2/3).
D$m2$tasas <- list(h = "-1/3", mise = "-2/3",
                   datos_para_mitad = r10(2^(3 / 2)))

# =====================================================================
# C. MÓDULO 3 — El ASH: promediar los orígenes
# =====================================================================
message("C. modulo 3 - el ASH")
ash <- function(x, h, m, g) {
  n <- length(x); d <- h / m
  mal <- seq(min(x) - h, max(x) + h + d, by = h)       # malla EXTENDIDA
  e <- numeric(length(g))
  for (j in 0:(m - 1)) {
    b <- mal + j * d
    cn <- hist(x, breaks = b, plot = FALSE, right = FALSE, include.lowest = TRUE)$counts
    i <- findInterval(g, b)
    ok <- i >= 1 & i <= length(b) - 1
    e <- e + ifelse(ok, cn[pmax(pmin(i, length(cn)), 1)], 0)
  }
  e / (m * n * h)
}
kde_tri <- function(x, h, g) sapply(g, function(t) mean(pmax(0, 1 - abs((t - x) / h))) / h)

# El ejemplo a mano: {2, 3, 3, 5, 7, 8, 9, 10}, h = 2, m = 3.
xa <- c(2, 3, 3, 5, 7, 8, 9, 10); ha <- 2; ma <- 3; da <- ha / ma
base <- seq(min(xa), max(xa), by = ha)                 # 2, 4, 6, 8, 10
cnt_base <- hist(xa, breaks = base, plot = FALSE, right = FALSE,
                 include.lowest = TRUE)$counts
# La trampa: la malla base desplazada pierde datos por el borde.
pierde <- sapply(0:(ma - 1), function(j) {
  b <- base + j * da
  sum(xa >= b[1] & xa < b[length(b)]) + sum(xa == b[length(b)])
})
ext <- seq(0, 12, by = ha)
tabla_desp <- lapply(0:(ma - 1), function(j) {
  b <- ext + j * da
  cn <- hist(xa, breaks = b, plot = FALSE, right = FALSE, include.lowest = TRUE)$counts
  list(j = j, desplazamiento = r10(j * da), cortes = r10(b), conteos = cn, suma = sum(cn))
})
guarda(all(sapply(tabla_desp, `[[`, "suma") == length(xa)),
       "m3: con la malla extendida los tres histogramas cuentan los 8 datos")
guarda(pierde[1] == length(xa) && all(diff(pierde) < 0),
       "m3: con la malla base cada desplazamiento pierde más datos")
puntos3 <- c(3, 5, 7, 9)
f_j <- sapply(0:(ma - 1), function(j) {
  b <- ext + j * da
  cn <- hist(xa, breaks = b, plot = FALSE, right = FALSE, include.lowest = TRUE)$counts
  cn[findInterval(puntos3, b)] / (length(xa) * ha)
})
f_ash3 <- rowMeans(f_j)
guarda(max(abs(f_ash3 - ash(xa, ha, ma, puntos3))) < 1e-12,
       "m3: la tabla a mano coincide con la función ash()")

# La varianza: (2m² + 1) / (3m²) veces la del histograma.
ms_var <- c(1, 2, 3, 4, 8, 16)
# El ASH tiende al núcleo triangular de semiancho h, con error ~ 1/m.
H_TRI <- 0.6
g3 <- seq(min(ERU) - 1, max(ERU) + 1, by = 0.005)
tri <- kde_tri(ERU, H_TRI, g3)
pico_tri <- max(tri)
ms_tri <- c(1, 2, 4, 8, 16, 32, 64, 256)
dist_tri <- sapply(ms_tri, function(m) max(abs(ash(ERU, H_TRI, m, g3) - tri)))
guarda(all(diff(dist_tri) < 0), "m3: la distancia al triangular baja con cada m")
guarda(all(abs(ms_tri[-1] * dist_tri[-1] / (ms_tri[2] * dist_tri[2]) - 1) < 0.35),
       "m3: la distancia baja como 1/m (m · distancia casi constante)")
areas_ash <- sapply(c(1, 4, 16), function(m) trapecio(g3, ash(ERU, H_TRI, m, g3)))

# La trampa de las ventanas solapadas: tres centros, ancho 3.
xs <- c(1, 2, 2.5, 3, 4, 4.5, 5, 6, 7, 7.5, 8); cs <- c(3, 5, 7); ws <- 3
cnt_s <- sapply(cs, function(c0) sum(xs >= c0 - ws / 2 & xs <= c0 + ws / 2))
fuera_s <- sum(sapply(xs, function(v) all(abs(v - cs) > ws / 2)))
veces_s <- sapply(xs, function(v) sum(abs(v - cs) <= ws / 2))
guarda(sum(veces_s) == sum(cnt_s) && all(veces_s <= 2), "m3: ningún dato cae en tres ventanas")
D$m3 <- list(
  ejemplo = list(datos = xa, n = length(xa), h = ha, m = ma, delta = r10(da),
                 base_cortes = base, base_conteos = cnt_base,
                 base_desplazada_cuenta = pierde,
                 extendida = list(desde = min(ext), hasta = max(ext)),
                 desplazados = tabla_desp,
                 puntos = puntos3, f_j = lapply(seq_along(puntos3), function(i) r10(f_j[i, ])),
                 f_ash = r10(f_ash3)),
  varianza = list(m = ms_var, factor = r10((2 * ms_var^2 + 1) / (3 * ms_var^2)),
                  limite = r10(2 / 3)),
  triangular = list(h = H_TRI, m = ms_tri, distancia = r10(dist_tri),
                    m_por_distancia = r10(ms_tri * dist_tri),
                    pico = r10(pico_tri), pct_pico = r10(100 * dist_tri / pico_tri),
                    paso_rejilla = 0.005),
  areas = list(m = c(1, 4, 16), area = r10(areas_ash)),
  solapadas = list(datos = xs, n = length(xs), centros = cs, ancho = ws,
                   desde = cs - ws / 2, hasta = cs + ws / 2,
                   dobles = xs[veces_s == 2], sin_datos = xs[veces_s == 0],
                   conteos = cnt_s, contribuciones = sum(cnt_s),
                   area = r10(sum(cnt_s) / length(xs)),
                   densidades = r10(cnt_s / (length(xs) * ws)),
                   sin_ventana = fuera_s))

# =====================================================================
# D. MÓDULO 4 — Contar en una ventana: k / (nV)
#
# La distribución EXACTA del estimador ingenuo en x0 = 0 bajo N(0, 1): el
# número de datos en la ventana es binomial, así que no hace falta simular.
# Es la ecuación (2.7) del texto guía, dibujada.
# =====================================================================
message("D. modulo 4 - k/(nV)")
f0 <- dnorm(0)
# La rejilla logarítmica del simulador, con los tres anchos que cita la prosa
# (0.05, 0.2 y 2) dentro EXACTOS: antes el deslizador no podía llegar a 0.2 y
# su lectura daba 0.1353 donde la tabla daba 0.1354 (revisión 2).
Vs <- sort(unique(c(r10(exp(seq(log(0.05), log(4), length.out = 61))), 0.2, 2)))
ns4 <- c(25L, 100L, 400L, 1600L)
ecm_v <- function(V, nn) {
  p <- pnorm(V / 2) - pnorm(-V / 2)
  (p / V - f0)^2 + p * (1 - p) / (nn * V^2)
}
por_n <- lapply(ns4, function(nn) {
  p <- pnorm(Vs / 2) - pnorm(-Vs / 2)
  media <- p / Vs; sdv <- sqrt(p * (1 - p) / nn) / Vs
  ecm <- (media - f0)^2 + sdv^2
  # El mejor V EXACTO, no el nodo más cercano de la rejilla.
  o <- optimize(ecm_v, c(0.05, 4), nn = nn, tol = 1e-10)
  list(n = nn, media = r10(media), sd = r10(sdv), ecm = r10(ecm),
       vacia = r10((1 - p)^nn),
       v_opt = r10(o$minimum), ecm_min = r10(o$objective))
})
v_opts <- sapply(por_n, `[[`, "v_opt")
razones_v <- head(v_opts, -1) / tail(v_opts, -1)
# La ventana está centrada en x: su sesgo es O(V²) y el mejor V baja como
# n^(-1/5). Cada vez que n se cuadruplica, V se divide por casi 4^(1/5).
guarda(all(abs(razones_v / 4^(1 / 5) - 1) < 0.02),
       "m4: el mejor V se divide por casi 4^(1/5) cada vez que n se cuadruplica")
names(por_n) <- paste0("n", ns4)
# Las dos ventanas que la prosa contrasta, a n = 100.
V_PEQ <- 0.2; V_GRA <- 2
una <- function(V, nn) {
  p <- pnorm(V / 2) - pnorm(-V / 2)
  list(V = V, p = r10(p), media = r10(p / V), sesgo = r10(p / V - f0),
       sd = r10(sqrt(p * (1 - p) / nn) / V), vacia = r10((1 - p)^nn),
       esperados = r10(nn * p))
}
v_peq <- una(V_PEQ, 100); v_gra <- una(V_GRA, 100); v_min <- una(0.05, 100)
guarda(abs(v_peq$sesgo) < v_peq$sd && abs(v_gra$sesgo) > v_gra$sd,
       "m4: con V pequeña manda la varianza y con V grande el sesgo")
guarda(all(diff(sapply(por_n, `[[`, "v_opt")) < 0),
       "m4: la ventana óptima se encoge al crecer n")
# La maldición de la dimensión: datos para bajar el MISE a la mitad.
ds <- c(1, 2, 3, 10, 20)
D$m4 <- list(x0 = 0, f0 = r10(f0), V = Vs, por_n = unname(por_n), ns = ns4,
             v_peq = v_peq, v_gra = v_gra, v_min = v_min, n_contraste = 100L,
             razon_v = r10(mean(razones_v)), cuatro_quinta = r10(4^(1 / 5)),
             # su desviación típica (una caja de ancho V la tiene V/√12): el
             # módulo 8 la compara con el mejor h del gaussiano en el mismo x.
             v_opt_sd_n100 = r10(v_opts[ns4 == 100] / sqrt(12)),
             dimension = list(d = ds, exponente = r10(4 / (4 + ds)),
                              datos_para_mitad = r10(2^((4 + ds) / 4)),
                              lado_10pct = r10(0.1^(1 / ds))))
guarda(isTRUE(all.equal(2^(6 / 4), 2^(3 / 2))), "m4: el plano pide lo mismo que el histograma en la recta")
# EN x = 0 NO SE VE QUE CENTRAR IMPORTE: la pendiente es nula, y hasta una
# casilla [0, V) baja como n^(-1/5). Se ve en un punto con pendiente: en
# x = 0.5 la ventana centrada sigue con 4^(1/5) y la casilla [x, x + V) va
# hacia el 4^(1/3) del histograma (segunda pasada de la revisión 2).
X_PEND <- 0.5
ecm_cv <- function(V, nn, centrada) {
  p <- if (centrada) pnorm(X_PEND + V / 2) - pnorm(X_PEND - V / 2) else pnorm(X_PEND + V) - pnorm(X_PEND)
  (p / V - dnorm(X_PEND))^2 + p * (1 - p) / (nn * V^2)
}
vo_c <- sapply(ns4, function(nn) optimize(ecm_cv, c(0.01, 4), nn = nn, centrada = TRUE, tol = 1e-10)$minimum)
vo_k <- sapply(ns4, function(nn) optimize(ecm_cv, c(0.01, 4), nn = nn, centrada = FALSE, tol = 1e-10)$minimum)
raz_c <- mean(head(vo_c, -1) / tail(vo_c, -1)); raz_k <- mean(head(vo_k, -1) / tail(vo_k, -1))
guarda(abs(raz_c / 4^(1 / 5) - 1) < 0.03 && raz_k > raz_c + 0.1 && raz_k < 4^(1 / 3),
       "m4: en x = 0.5 la ventana centrada baja como n^(-1/5) y la casilla, hacia n^(-1/3)")
D$m4$pendiente <- list(x = X_PEND, centrada = r10(vo_c), casilla = r10(vo_k),
                       razon_centrada = r10(raz_c), razon_casilla = r10(raz_k),
                       cuatro_tercio = r10(4^(1 / 3)))

# --- La figura del plano: Parzen (radio fijo) contra k-NN (k fijo) ------
# Una esquina de Kennedy con sus sedes, en kilómetros desde la esquina de la
# caja. Las distancias se miden contra TODAS las sedes de la localidad, no
# solo las de la caja: si no, los sitios del borde verían menos vecinas de
# las que tienen (el problema de borde del capítulo 5, otra vez).
kx <- ken$x / 1000; ky <- ken$y / 1000
vec600 <- sapply(seq_along(kx), function(i) sum(sqrt((kx - kx[i])^2 + (ky - ky[i])^2) < 0.6))
c0 <- which.max(vec600)
LADO <- 2.0
x0c <- kx[c0] - LADO / 2; y0c <- ky[c0] - LADO / 2
ax <- kx - x0c; ay <- ky - y0c
MARGEN <- 0.5
vis <- ax >= -MARGEN & ax <= LADO + MARGEN & ay >= -MARGEN & ay <= LADO + MARGEN
cand <- expand.grid(x = seq(0.5, LADO - 0.5, by = 0.05), y = seq(0.5, LADO - 0.5, by = 0.05))
R_PARZEN <- 0.3; K_KNN <- 4L
cuenta_r <- apply(cand, 1, function(s) sum(sqrt((ax - s[1])^2 + (ay - s[2])^2) <= R_PARZEN))
dk <- apply(cand, 1, function(s) sort(sqrt((ax - s[1])^2 + (ay - s[2])^2))[K_KNN])
s_denso <- order(-cuenta_r, dk)[1]
s_ralo <- which.max(dk)
s_medio <- which.min(abs(dk - stats::median(dk)))
# Qué sedes cuenta cada círculo, como índices (desde 0) en la lista visible:
# la figura las rellena con el color del círculo para que se puedan contar.
iv <- which(vis)
sitios <- lapply(c(s_denso, s_medio, s_ralo), function(i) {
  d <- sqrt((ax[iv] - cand$x[i])^2 + (ay[iv] - cand$y[i])^2)
  list(x = r4(cand$x[i]), y = r4(cand$y[i]),
       parzen_conteo = cuenta_r[i],
       parzen_intensidad = r4(cuenta_r[i] / (pi * R_PARZEN^2)),
       knn_radio = r4(dk[i]),
       knn_intensidad = r4(K_KNN / (pi * dk[i]^2)),
       parzen_dentro = which(d <= R_PARZEN) - 1L,
       knn_dentro = order(d)[seq_len(K_KNN)] - 1L)
})
guarda(all(sapply(sitios, function(s) length(s$parzen_dentro) == s$parzen_conteo)),
       "m4: todas las sedes que cuenta el círculo fijo están en la figura")
guarda(length(unique(c(s_denso, s_medio, s_ralo))) == 3, "m4: los tres sitios son distintos")
guarda(sitios[[1]]$knn_radio < sitios[[2]]$knn_radio && sitios[[2]]$knn_radio < sitios[[3]]$knn_radio,
       "m4: el radio del k-NN crece del sitio denso al ralo")
guarda(sitios[[1]]$parzen_conteo > sitios[[3]]$parzen_conteo,
       "m4: la ventana fija cuenta más sedes en el sitio denso")
D$m4$plano <- list(lado_km = LADO, margen_km = MARGEN, n = sum(vis),
                   n_dentro = sum(vis & ax >= 0 & ax <= LADO & ay >= 0 & ay <= LADO),
                   n_margen = sum(vis) - sum(vis & ax >= 0 & ax <= LADO & ay >= 0 & ay <= LADO),
                   x = r4(ax[vis]), y = r4(ay[vis]),
                   radio_km = R_PARZEN, k = K_KNN, sitios = sitios)

# =====================================================================
# E. MÓDULO 5 — El estimador de núcleo: una loma por punto
# =====================================================================
message("E. modulo 5 - el estimador de nucleo")
x15 <- 1:5
f_par <- function(x, datos, h, K) sapply(x, function(t) mean(K((t - datos) / h)) / h)
unif_le <- function(u) ifelse(abs(u) <= 1, 0.5, 0)
unif_lt <- function(u) ifelse(abs(u) < 1, 0.5, 0)
f15 <- f_par(x15, x15, 1, unif_le)
terminos3 <- unif_le((3 - x15) / 1)
guarda(f15[1] < f15[3], "m5: en el borde la ventana recoge menos")

x5 <- c(2, 3, 4, 5, 7)
terminos_g <- dnorm(4 - x5)
hs5 <- c(0.5, 1, 2)
tabla5 <- lapply(hs5, function(h) list(h = h, uniforme = r10(f_par(4, x5, h, unif_le)),
                                       gaussiano = r10(f_par(4, x5, h, dnorm))))
g5 <- seq(-1, 11, length.out = 500)
hs_modas <- c(0.3, 0.5, 1, 2)
modas5 <- sapply(hs_modas, function(h) modas_secuencia(f_par(g5, x5, h, dnorm)))
guarda(identical(as.integer(modas5), c(5L, 3L, 1L, 1L)),
       "m5: las modas con h = 0.3, 0.5, 1 y 2 son 5, 3, 1 y 1")
# Los TRAMOS del simulador: sus mismos anchos (0.20 a 2.50 de 0.05 en 0.05) y
# su misma rejilla. La primera versión saltaba de 3 modas a 1 y no veía la
# etapa de 2 (de 0.65 a 0.85): el grupo de 2 a 5 y el 7 aislado (revisión 2).
H5 <- round(seq(0.2, 2.5, by = 0.05), 2)
md5 <- sapply(H5, function(h) modas_secuencia(f_par(g5, x5, h, dnorm)))
rl5 <- rle(md5); fin5 <- cumsum(rl5$lengths); ini5 <- fin5 - rl5$lengths + 1
tramos5 <- lapply(seq_along(rl5$values), function(i) list(
  modas = rl5$values[i], desde = H5[ini5[i]], hasta = H5[fin5[i]],
  donde = r4(donde_modas(g5, f_par(g5, x5, H5[ini5[i]], dnorm)))))
guarda(identical(as.integer(rl5$values), c(5L, 3L, 2L, 1L)),
       "m5: al crecer h las modas pasan por 5, 3, 2 y 1, sin volver atrás")
d2 <- tramos5[[3]]$donde
guarda(length(d2) == 2 && d2[1] > 2 && d2[1] < 5 && abs(d2[2] - 7) < 0.5,
       "m5: con dos modas, una es el grupo de 2 a 5 y la otra el 7 aislado")
unif_sd1 <- function(u) unif_le(u)          # la caja estirada a semiancho √3 tiene sd 1
caja_sd1 <- f_par(4, x5, sqrt(3), unif_sd1)
D$m5 <- list(
  uniforme = list(datos = x15, h = 1, f = r10(f15), terminos_x3 = terminos3,
                  suma_x3 = sum(terminos3)),
  frontera = list(datos = x5, x = 4, h = 1,
                  le = r10(f_par(4, x5, 1, unif_le)), lt = r10(f_par(4, x5, 1, unif_lt))),
  gaussiano = list(datos = x5, x = 4, h = 1, terminos = r10(terminos_g),
                   suma = r10(sum(terminos_g)), f = r10(mean(terminos_g))),
  tabla = tabla5,
  modas = list(h = hs_modas, modas = as.integer(modas5)),
  tramos = tramos5, h_inicial = 0.3,
  # La caja con h = 1 tiene desviación típica 1/√3; con semiancho √3, la
  # misma que el gaussiano con h = 1: la comparación justa en x = 4.
  caja = list(sd_h1 = r10(1 / sqrt(3)), semiancho_sd1 = r10(sqrt(3)), f_sd1 = r10(caja_sd1)),
  rejilla = list(desde = -1, hasta = 11, puntos = 500L))

# =====================================================================
# F. MÓDULO 6 — La forma del núcleo importa poco; la escala, mucho
# =====================================================================
message("F. modulo 6 - los nucleos")
mom <- function(K, lim) {
  mu2 <- integrate(function(u) u^2 * K(u), -lim, lim, subdivisions = 2000L)$value
  RK  <- integrate(function(u) K(u)^2, -lim, lim, subdivisions = 2000L)$value
  ar  <- integrate(K, -lim, lim, subdivisions = 2000L)$value
  c(mu2 = mu2, RK = RK, area = ar)
}
tab_k <- lapply(names(NUC), function(nm) {
  lim <- if (nm == "gaussiano") Inf else 1
  m <- mom(NUC[[nm]], lim)
  list(nombre = nm, mu2 = r10(m[["mu2"]]), RK = r10(m[["RK"]]), area = r10(m[["area"]]))
})
names(tab_k) <- names(NUC)
ref <- tab_k$epanechnikov$RK * sqrt(tab_k$epanechnikov$mu2)
for (nm in names(tab_k)) {
  tab_k[[nm]]$eficiencia <- r10(ref / (tab_k[[nm]]$RK * sqrt(tab_k[[nm]]$mu2)))
  # Cuántas veces más datos pide el núcleo para el mismo AMISE que el óptimo.
  tab_k[[nm]]$datos_para_igualar <- r10(1 / tab_k[[nm]]$eficiencia)
  # semiancho del soporte cuando la desviación típica vale 1: 1/sqrt(mu2)
  tab_k[[nm]]$soporte_por_sigma <- if (nm == "gaussiano") NA else r10(1 / sqrt(tab_k[[nm]]$mu2))
  # Con los mismos datos, el AMISE mínimo va como (R(K)·√μ₂)^(4/5): el error
  # del núcleo es (1/eficiencia)^(4/5) veces el del Epanechnikov.
  tab_k[[nm]]$error_relativo <- r10((1 / tab_k[[nm]]$eficiencia)^(4 / 5))
  # R(K) del núcleo estirado a desviación típica 1, que es R(K)·√μ₂: la
  # escala de soporte [-1, 1] hace que las dos columnas de la tabla engañen.
  tab_k[[nm]]$RK_sd1 <- r10(tab_k[[nm]]$RK * sqrt(tab_k[[nm]]$mu2))
  tab_k[[nm]]$h2_sobre_sigma2 <- if (nm == "gaussiano") NA else r10(1 / tab_k[[nm]]$mu2)
}
ancla(tab_k$epanechnikov$mu2, 1 / 5, "mu2 del Epanechnikov")
ancla(tab_k$epanechnikov$RK, 3 / 5, "R(K) del Epanechnikov")
ancla(tab_k$uniforme$mu2, 1 / 3, "mu2 del uniforme")
ancla(tab_k$gaussiano$RK, 1 / (2 * sqrt(pi)), "R(K) del gaussiano")
ancla(tab_k$gaussiano$eficiencia, 0.9512, "eficiencia del gaussiano (Wand y Jones)", tol = 1e-4)
guarda(which.max(sapply(tab_k, `[[`, "eficiencia")) == which(names(NUC) == "epanechnikov"),
       "m6: el Epanechnikov es el más eficiente")
# Los mismos cocientes en el PLANO, para los núcleos radiales de spatstat:
# la varianza por coordenada es la mitad de E[r²].
radial <- function(k) {
  num <- integrate(function(r) r^3 * k(r), 0, 1)$value
  den <- integrate(function(r) r * k(r), 0, 1)$value
  1 / (num / den / 2)
}
plano_k <- list(epanechnikov = r10(radial(function(r) 1 - r^2)),
                cuartico = r10(radial(function(r) (1 - r^2)^2)),
                disco = r10(radial(function(r) rep(1, length(r)))))
ancla(plano_k$epanechnikov, 6, "h²/σ² del Epanechnikov en el plano")
ancla(plano_k$cuartico, 8, "h²/σ² del cuártico en el plano")
ancla(plano_k$disco, 4, "h²/σ² del disco en el plano")

set.seed(SEMILLA)
uni <- rnorm(100, mean = 5, sd = 2)
set.seed(SEMILLA)
tri_m <- c(rnorm(500, 3, 0.5), rnorm(200, 6, 0.7), rnorm(50, 9, 0.6))
# El KDE EXACTO en la convención de `density()` (bw = desviación típica del
# núcleo), por suma directa. No se usa `density()` para contar máximos: su
# FFT deja un rizado numérico de 1e-17 en las zonas planas, y cada rizo
# contaría como una moda de la caja.
kde_r <- function(x, g, bw, nucleo) {
  a <- switch(nucleo, gaussian = 1, rectangular = sqrt(3), epanechnikov = sqrt(5),
              triangular = sqrt(6), biweight = sqrt(7))
  K <- switch(nucleo, gaussian = NUC$gaussiano, rectangular = NUC$uniforme,
              epanechnikov = NUC$epanechnikov, triangular = NUC$triangular,
              biweight = NUC$biweight)
  colMeans(K(outer(x, g, function(xi, t) (t - xi) / (a * bw)))) / (a * bw)
}
compara_nucleos <- function(x) {
  bw <- bw.nrd0(x)
  rg <- range(x) + c(-3, 3) * bw
  gx <- seq(rg[1], rg[2], length.out = 2048)
  dd <- lapply(c("gaussian", "rectangular", "epanechnikov"), function(k) kde_r(x, gx, bw, k))
  # La comprobación de que la suma directa es la misma curva que density().
  dr <- density(x, bw = bw, kernel = "gaussian", n = 2048, from = rg[1], to = rg[2])$y
  ancla(max(abs(dr - dd[[1]])), 0, "el KDE directo coincide con density()", tol = 1e-3 * max(dr))
  list(n = length(x), bw = r10(bw),
       max_gauss = r10(max(dd[[1]])),
       dif_rect = r10(max(abs(dd[[1]] - dd[[2]]))),
       dif_epan = r10(max(abs(dd[[1]] - dd[[3]]))),
       modas_gauss = modas_secuencia(dd[[1]]),
       modas_rect = modas_secuencia(dd[[2]]),
       modas_epan = modas_secuencia(dd[[3]]),
       caja_semiancho = r10(sqrt(3) * bw),
       caja_altura_sobre_n = r10(1 / (2 * sqrt(3) * bw)))
}
cmp_uni <- compara_nucleos(uni); cmp_tri <- compara_nucleos(tri_m)
# Los dos modos del simulador, sobre la trimodal: la misma desviación típica
# (b = bw) o el mismo soporte que el Epanechnikov de R (b = √5·bw / escala).
# La primera versión del «Cómo se lee» decía que con el mismo soporte «el
# uniforme y el triangular dejan de parecerse»; el triangular apenas cambia,
# y quien se aleja es la caja, con el biweight detrás (revisión 2).
ESC <- c(rectangular = sqrt(3), triangular = sqrt(6), biweight = sqrt(7), epanechnikov = sqrt(5))
rg_t <- range(tri_m) + c(-3, 3) * cmp_tri$bw
gx_t <- seq(rg_t[1], rg_t[2], length.out = 2048)
ref_t <- kde_r(tri_m, gx_t, cmp_tri$bw, "gaussian")
modos6 <- lapply(c("rectangular", "triangular", "biweight"), function(k) {
  b_sop <- sqrt(5) * cmp_tri$bw / ESC[[k]]
  list(nucleo = k,
       dif_misma_sd = r10(max(abs(kde_r(tri_m, gx_t, cmp_tri$bw, k) - ref_t))),
       sd_mismo_soporte = r10(b_sop),
       dif_mismo_soporte = r10(max(abs(kde_r(tri_m, gx_t, b_sop, k) - ref_t))))
})
names(modos6) <- c("caja", "triangular", "biweight")
guarda(modos6$caja$dif_mismo_soporte > 2 * modos6$caja$dif_misma_sd &&
       modos6$biweight$dif_mismo_soporte > 2 * modos6$biweight$dif_misma_sd &&
       modos6$triangular$dif_mismo_soporte < 2 * modos6$triangular$dif_misma_sd,
       "m6: con el mismo soporte se alejan la caja y el biweight; el triangular casi no")
# «La forma no mueve las modas grandes; sí decide cuántos dientes las
# acompañan»: sobre la unimodal, el Epanechnikov y la caja tienen máximos
# locales de sobra y el gaussiano uno.
guarda(cmp_uni$modas_gauss == 1 && cmp_uni$modas_epan > 1 && cmp_uni$modas_rect > cmp_uni$modas_epan,
       "m6: sobre la unimodal, los núcleos de soporte acotado añaden máximos locales")
guarda(cmp_tri$modas_gauss == 3, "m6: el KDE gaussiano de la trimodal tiene tres modas")
guarda(cmp_uni$dif_rect < 0.2 * cmp_uni$max_gauss && cmp_tri$dif_rect < 0.2 * cmp_tri$max_gauss,
       "m6: con el mismo bw los núcleos cambian poco la curva")
guarda(cmp_tri$modas_rect > cmp_tri$modas_gauss,
       "m6: el rectangular deja más rugosidad (más máximos) que el gaussiano")
# La convención de `density()`, comprobada sobre un solo dato.
d1 <- density(0, bw = 1, kernel = "epanechnikov", n = 8192, from = -3, to = 3)
sop_epa <- max(abs(d1$x[d1$y > 1e-9]))
ancla(sop_epa, sqrt(5), "density(): el Epanechnikov con bw = 1 llega a ±√5", tol = 3e-3)
d2 <- density(0, bw = 1, kernel = "rectangular", n = 8192, from = -3, to = 3)
ancla(max(abs(d2$x[d2$y > 1e-9])), sqrt(3), "density(): la caja con bw = 1 llega a ±√3", tol = 3e-3)
# El valor que enseñan las dos pestañas del bloque: el Epanechnikov de R con
# bw = 1 todavía pesa en x = 2, porque su soporte llega a √5.
epa_en_2 <- approx(d1$x, d1$y, xout = 2)$y
ancla(epa_en_2, 0.75 * (1 - 4 / 5) / sqrt(5), "Epanechnikov de R con bw = 1 en x = 2", tol = 2e-4)
D$m6 <- list(nucleos = unname(tab_k), plano = plano_k,
             epa_bw1_en_2 = r10(epa_en_2),
             pregunta_caja = list(bw = 0.6, semiancho = r10(sqrt(3) * 0.6)), epa_bw1_en_2_exacto = r10(0.75 * (1 - 4 / 5) / sqrt(5)),
             mismo_soporte = modos6,
             unimodal = c(cmp_uni, list(mu = 5, sd = 2)),
             trimodal = c(cmp_tri, list(n1 = 500L, n2 = 200L, n3 = 50L,
                                        mu = c(3, 6, 9), sd = c(0.5, 0.7, 0.6))),
             density_soporte = list(epanechnikov = r10(sqrt(5)), rectangular = r10(sqrt(3)),
                                    triangular = r10(sqrt(6)), biweight = r10(sqrt(7))),
             muestra_trimodal = r10(tri_m))

# =====================================================================
# G. MÓDULO 7 — k vecinos: el radio se adapta
# =====================================================================
message("G. modulo 7 - k vecinos")
knn1 <- function(x0, datos, k) { d <- sort(abs(datos - x0)); k / (2 * length(datos) * d[k]) }
xe <- c(20, 23, 25, 29, 31, 35, 40); x0e <- 30; ke <- 3L
de <- sort(abs(xe - x0e))
dentro_e <- sum(abs(xe - x0e) <= de[ke])
guarda(dentro_e > ke, "m7: el ejemplo de x = 30 tiene un empate en el tercer vecino")
D$m7 <- list(
  edades = list(datos = xe, x = x0e, k = ke, distancias = de, d_k = de[ke],
                V = 2 * de[ke], f = r10(knn1(x0e, xe, ke)),
                dentro = dentro_e,
                balloon = r10(dentro_e / (length(xe) * 2 * de[ke]))))

ing <- c(35, 42, 47, 53, 57, 61, 64, 68, 73, 75, 78, 82, 85, 90, 94, 100, 103, 107, 110, 115)
n_ing <- length(ing)
h_ing <- 1.06 * min(sd(ing), IQR(ing) / 1.34) * n_ing^(-1 / 5)
epa_sop <- function(t, h) mean(NUC$epanechnikov((t - ing) / h)) / h
r_ing <- sort(abs(ing - 80))[3]
# La convención de R: `bw` es la desviación típica, así que el soporte es ±√5·bw.
a_r <- sqrt(5) * h_ing
d_r <- mean(NUC$epanechnikov((80 - ing) / a_r)) / a_r
d_rr <- density(ing, bw = h_ing, kernel = "epanechnikov", n = 4096, from = 0, to = 160)
ancla(approx(d_rr$x, d_rr$y, xout = 80)$y, d_r, "density() del Epanechnikov en 80", tol = 1e-4)
knn_ing <- function(t) 3 / (2 * n_ing * sort(abs(ing - t))[3])
areas_knn <- lapply(list(c(30, 120), c(-200, 350), c(-5000, 5000)), function(rg) {
  g <- seq(rg[1], rg[2], length.out = 20001)
  list(desde = rg[1], hasta = rg[2], area = r10(trapecio(g, sapply(g, knn_ing))))
})
guarda(all(diff(sapply(areas_knn, `[[`, "area")) > 0),
       "m7: el área del k-NN sigue creciendo al ensanchar la ventana")
D$m7$ingresos <- list(
  datos = ing, n = n_ing, x = 80, k = 3L, radio = r_ing,
  knn = r10(knn_ing(80)),
  # Las cuatro distancias más cortas a 80 y cuántos datos encierra la
  # ventana: el 75 y el 85 empatan con la tercera, y la ventana cuenta 4.
  distancias_4 = sort(abs(ing - 80))[1:4], dentro = sum(abs(ing - 80) <= r_ing),
  sd = r10(sd(ing)), iqr_134 = r10(IQR(ing) / 1.34), h = r10(h_ing),
  h_nrd0 = r10(bw.nrd0(ing)),
  epa_soporte = r10(epa_sop(80, h_ing)),
  gauss = r10(mean(dnorm((80 - ing) / h_ing)) / h_ing),
  epa_density = r10(d_r),
  epa_density_semiancho = r10(sqrt(5) * h_ing),
  areas = areas_knn)
guarda(abs(D$m7$ingresos$epa_density - D$m7$ingresos$epa_soporte) > 1e-4,
       "m7: el mismo número como bw o como soporte da densidades distintas")
guarda(D$m7$ingresos$dentro == 4L && D$m7$ingresos$dentro > D$m7$ingresos$k,
       "m7: en 80 la ventana del k-NN encierra cuatro ingresos y cobra tres")

# La mezcla bimodal, con k variable.
set.seed(SEMILLA)
mez <- c(rnorm(100, 5, 1), rnorm(100, 10, 1.5))
g7 <- seq(min(mez), max(mez), length.out = 1000)
f_mez <- function(x) 0.5 * dnorm(x, 5, 1) + 0.5 * dnorm(x, 10, 1.5)
ks7 <- c(3L, 5L, 10L, 20L, 40L, 80L)
knn_curva <- function(k) sapply(g7, function(t) k / (2 * length(mez) * sort(abs(mez - t))[k]))
# El valle se evalúa EN 7.5, no en el nodo de la rejilla más cercano: con los
# dientes del k-NN, correrse tres milésimas cambiaba la cifra un 2 %, y el
# módulo y el ejercicio 3 daban cifras distintas de la misma muestra
# (revisión 2).
res7 <- lapply(ks7, function(k) {
  y <- knn_curva(k)
  list(k = k, modas = modas_secuencia(y), area = r10(trapecio(g7, y)),
       f_valle = r10(k / (2 * length(mez) * sort(abs(mez - 7.5))[k])), maximo = r10(max(y)))
})
guarda(all(diff(sapply(res7, `[[`, "modas")) <= 0), "m7: más vecinos, menos modas")
# LOS DIENTES SON DE LA FÓRMULA, NO DEL RUIDO. d_k(x) es lineal a trozos y
# tiene un mínimo cada vez que el k-ésimo vecino cambia de lado, así que la
# curva tiene un pico en cada cambio por grande que sea k. La primera versión
# de esta guarda esperaba «pocas modas con k = 80» y quedaban 72: la prosa
# tiene que decir que el k-NN es continuo pero no derivable, no que se alisa.
guarda(res7[[length(res7)]]$modas > 10, "m7: aun con k = 80 la curva conserva decenas de dientes")
h7 <- hist(mez, breaks = 30, plot = FALSE)
D$m7$mezcla <- list(n = length(mez), medias = c(5, 10), sd = c(1, 1.5),
                    rejilla = list(desde = r10(min(mez)), hasta = r10(max(mez)), puntos = 1000L),
                    por_k = res7, area_verdad = r10(trapecio(g7, f_mez(g7))),
                    f_valle_verdad = r10(f_mez(7.5)),
                    hist_pide = 30L, valle_x = 7.5,
                    hist_clases = length(h7$breaks) - 1L,
                    hist_modas = modas_secuencia(h7$density),
                    muestra = r10(mez))

# =====================================================================
# H. MÓDULO 8 — Sesgo, varianza y error integrado
#
# f = N(0, 1) y núcleo gaussiano: todo tiene forma cerrada, así que el ECM
# es EXACTO, no simulado. La nube de 30 muestras es para verlo.
# =====================================================================
message("H. modulo 8 - sesgo y varianza")
n8 <- 100L
Ef <- function(x, h) dnorm(x, 0, sqrt(1 + h^2))
EK2 <- function(x, h) dnorm(x, 0, sqrt(1 + h^2 / 2)) / (2 * sqrt(pi) * h)
Vf <- function(x, h) (EK2(x, h) - Ef(x, h)^2) / n8
hs8 <- seq(0.05, 1.50, by = 0.01)
sesgo2_0 <- (Ef(0, hs8) - dnorm(0))^2
var_0 <- Vf(0, hs8)
ecm_0 <- sesgo2_0 + var_0
h_ecm <- hs8[which.min(ecm_0)]
h_amise <- (4 / (3 * n8))^(1 / 5)
mise <- function(h) (1 / (2 * sqrt(pi))) * (1 / (n8 * h) + (1 - 1 / n8) / sqrt(1 + h^2) -
                                              2^(3 / 2) / sqrt(2 + h^2) + 1)
op <- optimize(mise, c(0.05, 1.5), tol = 1e-10)
guarda(h_ecm < h_amise && h_amise < op$minimum,
       "m8: el h del ECM en x = 0 < el del AMISE < el del MISE exacto")
# La aproximación asintótica, comprobada en un punto con h pequeño.
x_as <- 0.5; h_as <- 0.05
fpp <- function(x) (x^2 - 1) * dnorm(x)
asin <- list(x = x_as, h = h_as,
             sesgo_exacto = r10(Ef(x_as, h_as) - dnorm(x_as)),
             sesgo_formula = r10(h_as^2 / 2 * fpp(x_as)),
             var_exacta = r10(Vf(x_as, h_as)),
             var_formula = r10((1 / (2 * sqrt(pi))) * dnorm(x_as) / (n8 * h_as)))
# El mejor ancho de UN punto, en tres puntos: en x = 1 la curvatura f'' se
# anula y el sesgo asintótico con ella, y el mejor ancho se dispara. Es el
# ejemplo que muestra «el mejor ancho para un punto no es el de la curva»;
# 0.39 frente a 0.4455 apenas lo mostraba (revisión 2).
ecm_x <- function(x, h) (Ef(x, h) - dnorm(x))^2 + Vf(x, h)
xs_ecm <- c(0, 0.5, 1)
h_ecm_x <- sapply(xs_ecm, function(x) optimize(function(h) ecm_x(x, h), c(0.05, 3), tol = 1e-10)$minimum)
guarda(all(diff(h_ecm_x) > 0) && h_ecm_x[3] > 1.5 * h_ecm_x[1],
       "m8: el mejor ancho puntual crece de x = 0 a x = 1, donde f'' se anula")
# Donde se cortan sesgo² y varianza NO es donde está el mínimo del ECM: allí
# las dos PENDIENTES se compensan, no los dos valores.
cruce8 <- uniroot(function(h) (Ef(0, h) - dnorm(0))^2 - Vf(0, h), c(0.1, 1.4), tol = 1e-10)$root
i_opt8 <- which.min(ecm_0)
guarda(cruce8 > hs8[i_opt8] && sesgo2_0[i_opt8] < var_0[i_opt8],
       "m8: sesgo² y varianza se cortan a la derecha del mejor h, donde el sesgo² es menor")
# El promedio de 30 curvas tiene su propio error de Monte Carlo: en x = 0 y
# con h = 0.4, dos desviaciones típicas de un promedio de 30.
H_NUBE <- 0.4
mc_nube <- 2 * sqrt(Vf(0, H_NUBE) / 30)
sesgo_nube <- Ef(0, H_NUBE) - dnorm(0)
set.seed(SEMILLA)
nube <- lapply(1:30, function(i) r6(rnorm(n8)))
D$m8 <- list(n = n8, x0 = 0, h = hs8, sesgo2 = r10(sesgo2_0), var = r10(var_0),
             ecm = r10(ecm_0), h_ecm = h_ecm, ecm_min = r10(min(ecm_0)),
             h_amise = r10(h_amise), constante_amise = r10((4 / 3)^(1 / 5)),
             h_mise = r10(op$minimum), mise_min = r10(op$objective),
             mise_en_amise = r10(mise(h_amise)),
             mise_pct_amise = r10(100 * (mise(h_amise) / op$objective - 1)),
             mise_h = r10(mise(hs8)),
             h_ecm_x = list(x = xs_ecm, h = r10(h_ecm_x)),
             cruce = r10(cruce8),
             en_optimo = list(sesgo2 = r10(sesgo2_0[i_opt8]), var = r10(var_0[i_opt8])),
             nube_h = H_NUBE, nube_sesgo = r10(sesgo_nube), nube_error_mc = r10(mc_nube),
             asintotica = asin,
             tasas = list(hist_datos_para_mitad = r10(2^(3 / 2)),
                          kde_datos_para_mitad = r10(2^(5 / 4))),
             nube = nube)

# =====================================================================
# I. MÓDULO 9 — Reglas de referencia
# =====================================================================
message("I. modulo 9 - reglas de referencia")
s_e <- sd(ERU); iqr_e <- IQR(ERU)
nrd0_e <- bw.nrd0(ERU); nrd_e <- bw.nrd(ERU)
ancla(nrd0_e, 0.9 * min(s_e, iqr_e / 1.34) * N_ERU^(-1 / 5), "bw.nrd0 = 0.9·min·n^(-1/5)", tol = 1e-12)
ancla(nrd_e, 1.06 * min(s_e, iqr_e / 1.34) * N_ERU^(-1 / 5), "bw.nrd = 1.06·min·n^(-1/5)", tol = 1e-12)
hist_rule <- 3.5 * s_e * N_ERU^(-1 / 3)
fac <- function(d) (4 / (d + 2))^(1 / (d + 4))
# El σ del plano: `bw.scott` de spatstat sobre las sedes, contra la fórmula.
X_sedes <- suppressWarnings(ppp(sedes$x, sedes$y, window = owin(range(sedes$x), range(sedes$y))))
bs <- bw.scott(X_sedes)
ancla(bs[1], sd(sedes$x) * N_SEDES^(-1 / 6), "bw.scott x = sd·n^(-1/6)", tol = 1e-9)
ancla(bs[2], sd(sedes$y) * N_SEDES^(-1 / 6), "bw.scott y = sd·n^(-1/6)", tol = 1e-9)
# Las distancias al vecino: aquí el IQR manda, y scipy no lo usa.
nn <- nndist(sedes$x, sedes$y)
s_nn <- sd(nn); iqr_nn <- IQR(nn)
guarda(iqr_nn / 1.34 < s_nn, "m9: en las distancias al vecino IQR/1.34 < sd")
D$m9 <- list(
  faithful = list(n = N_ERU, sd = r10(s_e), iqr = r10(iqr_e), iqr_134 = r10(iqr_e / 1.34),
                  minimo = r10(min(s_e, iqr_e / 1.34)), n_quinta = r10(N_ERU^(-1 / 5)),
                  nrd0 = r10(nrd0_e), nrd = r10(nrd_e), hist_rule = r10(hist_rule),
                  # el distractor de la autoevaluación: tomar la escala MAYOR
                  nrd0_con_iqr = r10(0.9 * iqr_e / 1.34 * N_ERU^(-1 / 5)),
                  hist_sobre_nrd = r10(hist_rule / nrd_e),
                  factor_constante = r10(3.5 / 1.06),
                  factor_exponente = r10(N_ERU^(-1 / 3) / N_ERU^(-1 / 5)),
                  # La constante del histograma mide un ancho ENTERO; en
                  # desviación típica (una barra de ancho h la tiene h/√12)
                  # es casi el 1.06 del núcleo: lo que separa las reglas es
                  # el exponente. Y como n^(-2/15) → 0, desde unos miles de
                  # datos la regla del histograma da MENOS que bw.nrd.
                  hist_constante_sd = r10((24 * sqrt(pi))^(1 / 3) / sqrt(12)),
                  n_cruce = r10((3.5 / 1.06)^(15 / 2)), n_cruce_redondo = round((3.5 / 1.06)^(15 / 2), -2),
                  sd_doble = r10(2 * s_e * N_ERU^(-1 / 5))),
  constantes = list(silverman = 0.9, scott = 1.06, iqr = 1.34, hist = 3.5,
                    iqr_normal = r10(qnorm(0.75) - qnorm(0.25))),
  factor_d = list(d = 1:3, factor = r10(fac(1:3)), exponente = r10(-1 / (1:3 + 4))),
  plano = list(n = N_SEDES, sd_x = r10(sd(sedes$x)), sd_y = r10(sd(sedes$y)),
               scott_x = r10(bs[1]), scott_y = r10(bs[2]), n_sexta = r10(N_SEDES^(-1 / 6))),
  distancias = list(n = N_SEDES, sd = r10(s_nn), iqr_134 = r10(iqr_nn / 1.34),
                    maximo = r10(max(nn)), mediana = r10(median(nn)),
                    nrd0 = r10(bw.nrd0(nn)), nrd = r10(bw.nrd(nn)),
                    scipy = r10(fac(1) * s_nn * N_SEDES^(-1 / 5))))
guarda(D$m9$distancias$scipy > 1.3 * D$m9$distancias$nrd,
       "m9: el «silverman» de scipy se aleja de bw.nrd cuando manda el IQR")
guarda(abs(D$m9$faithful$hist_constante_sd / 1.06 - 1) < 0.06 && D$m9$faithful$n_cruce > N_ERU,
       "m9: en desviación típica las dos constantes casi coinciden, y el cruce queda lejos de 272")

# =====================================================================
# J. MÓDULO 10 — Validación cruzada
# =====================================================================
message("J. modulo 10 - validacion cruzada")
Dm <- outer(ERU, ERU, "-")
loo <- function(h) { W <- dnorm(Dm / h); diag(W) <- 0; rowSums(W) / ((N_ERU - 1) * h) }
Rf2 <- function(h) sum(dnorm(Dm / (sqrt(2) * h))) / (N_ERU^2 * h * sqrt(2))
ucv <- function(h) Rf2(h) - 2 * mean(loo(h))
lcv <- function(h) mean(log(loo(h)))
sel <- c(ucv = bw.ucv(ERU), bcv = bw.bcv(ERU), SJ = bw.SJ(ERU), dpik = dpik(ERU))
hh <- seq(0.02, 0.60, by = 0.002)
U <- sapply(hh, ucv); L <- sapply(hh, lcv)
h_ucv_mano <- hh[which.min(U)]; h_lcv_mano <- hh[which.max(L)]
guarda(abs(h_ucv_mano - sel[["ucv"]]) < 0.003, "m10: la UCV a mano reproduce bw.ucv")
gK <- seq(min(ERU) - 1, max(ERU) + 1, length.out = 2048)
kde_g <- function(h) sapply(gK, function(t) mean(dnorm((t - ERU) / h)) / h)
todos_h <- c(nrd0 = nrd0_e, nrd = nrd_e, sel, hist_rule = hist_rule)
modas_sel <- sapply(todos_h, function(h) modas_secuencia(kde_g(h)))
guarda(modas_sel[["ucv"]] == 3 && all(modas_sel[names(modas_sel) != "ucv"] == 2),
       "m10: con bw.ucv salen tres modas y con los demás selectores dos")
donde3 <- donde_modas(gK, kde_g(sel[["ucv"]]))
# LAS ERUPCIONES TAMBIÉN TIENEN EMPATES. 126 valores distintos entre 272: las
# parejas empatadas por dato superan el umbral del módulo 12, así que la UCV
# exacta baja sin tope cuando h → 0 y el 0.102 es un mínimo LOCAL. La primera
# versión lo llamaba «el mínimo», y cinco módulos después el ejercicio 10
# enseñaba que un número sin aviso no garantiza un mínimo (revisión 2).
umbral_g <- (1 / (2 * sqrt(pi))) / (4 * dnorm(0) - 2 / (2 * sqrt(pi)))
t_eru <- table(round(ERU, 6)); empates_eru <- sum(t_eru * (t_eru - 1) / 2)
ucv_001 <- ucv(0.001)
hmax_eru <- 1.144 * sqrt(var(ERU)) * N_ERU^(-1 / 5)
# ¿Es estable ese mínimo local? Se rompen los empates con medio segundo de
# ruido (las duraciones vienen en minutos con tres decimales) y se repite.
jit <- sapply(1:6, function(s) { set.seed(SEMILLA + s)
  bw.ucv(ERU + runif(N_ERU, -0.5 / 60, 0.5 / 60)) })
guarda(empates_eru / N_ERU > umbral_g && ucv_001 < ucv(h_ucv_mano),
       "m10: las erupciones superan el umbral de empates y la UCV baja sin tope cerca de 0")
guarda(all(abs(jit / sel[["ucv"]] - 1) < 0.1),
       "m10: rompiendo los empates, bw.ucv sigue cerca del mínimo local")
# La rugosidad y la descomposición del AIMSE (lo que estima la BCV).
G <- 2048; gr <- seq(min(ERU) - 3, max(ERU) + 3, length.out = G); dx <- diff(gr)[1]
dens_h <- function(b) density(ERU, bw = b, n = G, from = min(gr), to = max(gr))$y
rug_f <- function(v) trapecio(gr[-c(1, 2)], (diff(v, differences = 2) / dx^2)^2)
RK_g <- 1 / (2 * sqrt(pi))
# LA RUGOSIDAD DE UNA CURVA ESTIMADA NO ES LA DE LA VERDAD. R(f̂''_h) lleva
# dentro un término R(K'')/(n h⁵) que crece al achicar h: con el ancho de la
# UCV es la mitad de toda su rugosidad. La primera versión metía R(f̂'') en el
# AMISE como si fuera R(f'') y leía «menos sesgo, más varianza»; esa lectura
# era circular (la varianza solo depende de h) y su orden contradecía al MISE
# exacto del módulo 11 (revisión 2). Restar ese término es lo que hace bw.bcv.
RKpp_g <- 3 / (8 * sqrt(pi))
aimse <- lapply(names(todos_h), function(nm) {
  b <- todos_h[[nm]]; r <- rug_f(dens_h(b))
  list(selector = nm, h = r10(b), rugosidad = r10(r), ruido = r10(RKpp_g / (N_ERU * b^5)))
})
names(aimse) <- names(todos_h)
parte_ruido <- sapply(aimse[c("ucv", "SJ", "bcv", "nrd0")], function(a) a$ruido / a$rugosidad)
guarda(parte_ruido[["ucv"]] > 0.4 && all(diff(parte_ruido) < 0),
       "m10: casi la mitad de la rugosidad de la UCV es ruido del ancho, y la parte baja al crecer h")
# El peso de la observación más aislada en la LCV. La primera versión decía
# que la LCV es «tan plana que la posición casi no está determinada»; medida
# en su propio recorrido, la UCV es igual de plana. Lo que sí es de la LCV:
# entre 0.05 y 0.14 casi toda su subida la pone UNA erupción (revisión 2).
aislada <- lapply(c(0.05, 0.14), function(b) {
  l <- log(loo(b)); list(h = b, min_log = r10(min(l)), aporte = r10(min(l) / N_ERU),
                         x = r10(ERU[which.min(l)]), min_loo = r10(min(loo(b))))
})
i_ais <- which.min(log(loo(0.05)))
lcv_sube <- lcv(0.14) - lcv(0.05)
guarda((aislada[[2]]$aporte - aislada[[1]]$aporte) > 0.8 * lcv_sube,
       "m10: la erupción aislada pone más del 80 % de la subida de la LCV entre 0.05 y 0.14")
# Los dos criterios SIN esa erupción, en la rejilla del simulador.
E_sin <- ERU[-i_ais]; n_sin <- length(E_sin); Dm_sin <- outer(E_sin, E_sin, "-")
loo_sin <- function(h) { W <- dnorm(Dm_sin / h); diag(W) <- 0; rowSums(W) / ((n_sin - 1) * h) }
ucv_sin <- function(h) sum(dnorm(Dm_sin / (sqrt(2) * h))) / (n_sin^2 * h * sqrt(2)) - 2 * mean(loo_sin(h))
lcv_sin <- function(h) mean(log(loo_sin(h)))
L_sin <- sapply(hh, lcv_sin); U_sin <- sapply(hh, ucv_sin)
h_lcv_sin <- hh[which.max(L_sin)]; h_ucv_sin <- hh[which.min(U_sin)]
guarda(h_lcv_sin < h_lcv_mano - 0.01 && abs(h_ucv_sin - h_ucv_mano) < 0.01,
       "m10: sin esa erupción la LCV mueve su máximo y la UCV casi no")
# Dejar uno fuera, a mano, con los cinco datos del módulo 5 y h = 1.
loo5 <- dnorm(4 - c(2, 3, 5, 7))
# Para el simulador: UCV, LCV y número de modas en cada h de la rejilla.
hh_sim <- seq(0.04, 0.60, by = 0.01)
D$m10 <- list(
  n = N_ERU, distintos = length(unique(ERU)), repetidos = N_ERU - length(unique(ERU)),
  selectores = lapply(sel, r10), h_ucv_mano = h_ucv_mano, h_lcv_mano = h_lcv_mano,
  modas = as.list(modas_sel), donde_modas_ucv = r10(donde3),
  aimse = unname(aimse),
  empates = list(parejas = empates_eru, por_dato = r10(empates_eru / N_ERU), umbral = r10(umbral_g),
                 ucv_001 = r10(ucv_001), ucv_min_local = r10(ucv(h_ucv_mano)),
                 busqueda_desde = r10(0.1 * hmax_eru), rejilla_desde = min(hh),
                 jitter_min = r10(min(jit)), jitter_max = r10(max(jit)), jitter_n = length(jit)),
  aislada = aislada,
  aislada_cambio = r10(aislada[[2]]$aporte - aislada[[1]]$aporte),
  lcv_sube = r10(lcv_sube), h_lcv_sin = h_lcv_sin, h_ucv_sin = h_ucv_sin,
  loo_mano = list(datos = c(2, 3, 4, 5, 7), x = 4, terminos = r10(loo5), f = r10(mean(loo5))),
  curvas = list(h = hh_sim, ucv = r10(sapply(hh_sim, ucv)), lcv = r10(sapply(hh_sim, lcv)),
                ucv_sin = r10(sapply(hh_sim, ucv_sin)), lcv_sin = r10(sapply(hh_sim, lcv_sin)),
                modas = sapply(hh_sim, function(h) modas_secuencia(kde_g(h)))))
md_sim <- D$m10$curvas$modas
D$m10$h_max_tres <- max(hh_sim[md_sim >= 3])
guarda(all(md_sim[hh_sim > D$m10$h_max_tres] <= 2), "m10: por encima de ese ancho nunca vuelve la tercera moda")
D$m10$rug_ucv_sobre_sj <- r10(aimse$ucv$rugosidad / aimse$SJ$rugosidad)

# =====================================================================
# K. MÓDULO 11 — Una verdad conocida: ¿qué selector acierta?
# =====================================================================
message("K. modulo 11 - verdad conocida y Monte Carlo (unos segundos)")
em2 <- function(y, mu, s, p, tol = 1e-12, maxit = 5000) {
  ll_old <- -Inf
  for (it in 1:maxit) {
    w <- p * dnorm(y, mu[1], s[1]); w <- w / (w + (1 - p) * dnorm(y, mu[2], s[2]))
    p <- mean(w)
    mu <- c(sum(w * y) / sum(w), sum((1 - w) * y) / sum(1 - w))
    s <- sqrt(c(sum(w * (y - mu[1])^2) / sum(w), sum((1 - w) * (y - mu[2])^2) / sum(1 - w)))
    ll <- sum(log(p * dnorm(y, mu[1], s[1]) + (1 - p) * dnorm(y, mu[2], s[2])))
    if (ll - ll_old < tol) break
    ll_old <- ll
  }
  list(p = p, mu = mu, s = s, loglik = ll, iter = it)
}
aj <- em2(ERU, mu = c(2, 4.3), s = c(0.25, 0.35), p = 0.5)
PI <- c(aj$p, 1 - aj$p); MU <- aj$mu; SG <- aj$s
Aprod <- function(a, b) {
  S <- 0
  for (i in 1:2) for (j in 1:2)
    S <- S + PI[i] * PI[j] * dnorm(MU[i] - MU[j], 0, sqrt(a[i]^2 + b[j]^2))
  S
}
mise_mez <- function(h, n = N_ERU) {
  s <- sqrt(SG^2 + h^2)
  Aprod(s, s) - 2 * Aprod(s, SG) + Aprod(SG, SG) + (1 / (2 * h * sqrt(pi)) - Aprod(s, s)) / n
}
opm <- optimize(mise_mez, c(0.02, 0.8), tol = 1e-10)
h_star <- opm$minimum
sel_real <- c(nrd0 = nrd0_e, nrd = nrd_e, sel, hist_rule = hist_rule)
tabla11 <- lapply(names(sel_real), function(nm) list(
  selector = nm, h = r10(sel_real[[nm]]), mise = r10(mise_mez(sel_real[[nm]])),
  sobre_pct = r10(100 * (mise_mez(sel_real[[nm]]) / opm$objective - 1))))
names(tabla11) <- names(sel_real)
guarda(tabla11$SJ$sobre_pct < tabla11$bcv$sobre_pct && tabla11$bcv$sobre_pct < tabla11$ucv$sobre_pct,
       "m11: sobre los datos reales SJ < BCV < UCV en MISE")
guarda(tabla11$nrd0$sobre_pct > 100 && tabla11$hist_rule$sobre_pct > tabla11$nrd$sobre_pct,
       "m11: las reglas de referencia normal cuestan más del doble del óptimo")

g_ver <- function(z) PI[1] * dnorm(z, MU[1], SG[1]) + PI[2] * dnorm(z, MU[2], SG[2])
gz <- seq(-1, 8, by = 0.01); gvv <- g_ver(gz); dgz <- diff(gz)[1]
SEL <- c("nrd0", "nrd", "ucv", "bcv", "SJ")
bwf <- list(nrd0 = bw.nrd0, nrd = bw.nrd, ucv = bw.ucv, bcv = bw.bcv, SJ = bw.SJ)
B <- 1000L
set.seed(SEMILLA)
ISE <- matrix(NA_real_, B, length(SEL), dimnames = list(NULL, SEL)); HS <- ISE
avisos <- matrix(0L, B, length(SEL), dimnames = list(NULL, SEL))
N_GUARDA_MUESTRAS <- 20L
muestras <- vector("list", N_GUARDA_MUESTRAS)
for (b in seq_len(B)) {
  y <- ifelse(runif(N_ERU) < PI[1], rnorm(N_ERU, MU[1], SG[1]), rnorm(N_ERU, MU[2], SG[2]))
  if (b <= N_GUARDA_MUESTRAS) muestras[[b]] <- y
  for (s in SEL) {
    hb <- withCallingHandlers(bwf[[s]](y), warning = function(w) {
      avisos[b, s] <<- avisos[b, s] + 1L; invokeRestart("muffleWarning") })
    HS[b, s] <- hb
    ISE[b, s] <- sum((density(y, bw = hb, n = length(gz), from = min(gz), to = max(gz))$y - gvv)^2) * dgz
  }
}
gana <- apply(ISE, 1, function(v) SEL[which.min(v)])
pct_gana <- 100 * as.numeric(table(factor(gana, levels = SEL))) / B
cola <- colMeans(ISE > 2 * ISE[, "SJ"])
emparejada <- function(a, b) {
  d <- ISE[, a] - ISE[, b]
  list(a = a, b = b, media = r10(mean(d)), ee = r10(sd(d) / sqrt(B)),
       t = r10(mean(d) / (sd(d) / sqrt(B))),
       pct = r10(100 * (mean(ISE[, a]) / mean(ISE[, b]) - 1)))
}
ee_pct <- function(p) 100 * sqrt(p * (1 - p) / B)
ic_cola <- function(p) 100 * (p + c(-1, 1) * 1.96 * sqrt(p * (1 - p) / B))
por_sel <- lapply(SEL, function(s) list(
  selector = s, h_media = r10(mean(HS[, s])), h_mediana = r10(median(HS[, s])),
  # La prueba de que la UCV es «de alta varianza» está en la dispersión de
  # sus ANCHOS, no en la del ISE (revisión 2).
  h_sd = r10(sd(HS[, s])), pct_sobre_hstar = r10(100 * mean(HS[, s] > h_star)),
  mise = r10(mean(ISE[, s])), ee_mc = r10(sd(ISE[, s]) / sqrt(B)),
  sd_ise = r10(sd(ISE[, s])), ise_mediano = r10(median(ISE[, s])),
  gana_pct = r10(pct_gana[SEL == s]), gana_ee = r10(ee_pct(pct_gana[SEL == s] / 100)),
  cola_pct = r10(100 * cola[[s]]), avisos = sum(avisos[, s] > 0)))
names(por_sel) <- SEL
guarda(which.max(pct_gana) == which(SEL == "ucv"), "m11: la UCV es la que más veces gana")
guarda(por_sel$ucv$mise > por_sel$SJ$mise, "m11: pero su MISE medio es peor que el de SJ")
guarda(por_sel$ucv$cola_pct > 2 && por_sel$bcv$cola_pct == 0,
       "m11: la UCV tiene cola (ISE > 2×SJ) y la BCV no")
# La UCV no se equivoca de centro sino de dispersión, y hacia un solo lado:
# sus fallos grandes eligieron todos un ancho menor que el de SJ. Eso es lo
# que «tiende a infrasuavizar» quiere decir; la primera versión del módulo 10
# lo afirmaba de su ancho medio, que está junto al óptimo (revisión 2).
en_cola <- ISE[, "ucv"] > 2 * ISE[, "SJ"]
guarda(por_sel$ucv$h_sd > 2 * por_sel$SJ$h_sd && all(HS[en_cola, "ucv"] < HS[en_cola, "SJ"]) &&
       max(HS[en_cola, "ucv"]) < 0.1,
       "m11: los fallos grandes de la UCV eligieron todos menos ancho que SJ, y menos de 0.10")
guarda(por_sel$SJ$pct_sobre_hstar > 90 && por_sel$bcv$pct_sobre_hstar > 90,
       "m11: SJ y la BCV se pasan de ancho casi siempre")
# El error que importa al comparar dos porcentajes de victoria es el de su
# DIFERENCIA: salen de las mismas muestras (revisión 2).
dif_gana <- function(a, b) {
  pa <- mean(gana == a); pb <- mean(gana == b)
  ee <- sqrt((pa + pb - (pa - pb)^2) / B)
  list(a = a, b = b, dif = r10(100 * (pa - pb)), ee = r10(100 * ee), z = r10((pa - pb) / ee))
}
dg_ub <- dif_gana("ucv", "bcv"); dg_bs <- dif_gana("bcv", "SJ")
guarda(dg_ub$z > 2 && abs(dg_bs$z) < 2, "m11: UCV-BCV se distingue del ruido y BCV-SJ no")
cara_bcv_sj <- 100 * mean(ISE[, "bcv"] < ISE[, "SJ"])
guarda(cara_bcv_sj < 50 && pct_gana[SEL == "bcv"] > pct_gana[SEL == "SJ"],
       "m11: SJ le gana a la BCV cara a cara aunque en la carrera de cinco quede detrás")
D$m11 <- list(
  em = list(p = r10(aj$p), mu = r10(MU), s = r10(SG), loglik = r10(aj$loglik), iter = aj$iter),
  h_estrella = r10(h_star), mise_min = r10(opm$objective),
  reales = unname(tabla11), B = B, n = N_ERU, semilla = SEMILLA,
  por_selector = unname(por_sel),
  emparejadas = list(ucv_sj = emparejada("ucv", "SJ"), bcv_sj = emparejada("bcv", "SJ")),
  cola_ucv_ic = r10(ic_cola(cola[["ucv"]])),
  cola_cero_cota = r10(100 * 3 / B),
  cola_ucv = list(n = sum(en_cola), h_max = r10(max(HS[en_cola, "ucv"])),
                  pct_h_bajo = r10(100 * mean(HS[, "ucv"] < 0.1)), corte = 0.1),
  dif_gana = list(ucv_bcv = dg_ub, bcv_sj = dg_bs),
  cara_bcv_sj = r10(cara_bcv_sj), cara_ucv_sj = r10(100 * mean(ISE[, "ucv"] < ISE[, "SJ"])),
  rejilla_ise = list(desde = -1, hasta = 8, paso = 0.01),
  # Diez decimales y no seis: con seis, algunas réplicas empataban al
  # redondear y el simulador daba 40.5 % donde el CSV da 40.9 % (revisión 2).
  ise = lapply(SEL, function(s) r10(ISE[, s])))
names(D$m11$ise) <- SEL

# El CSV réplica a réplica y las muestras de las primeras 20, para el auditor.
mc <- data.frame(replica = seq_len(B))
for (s in SEL) { mc[[paste0("h_", s)]] <- r10(HS[, s]); mc[[paste0("ise_", s)]] <- r10(ISE[, s]) }
for (s in SEL) mc[[paste0("aviso_", s)]] <- avisos[, s]
write.csv(mc, file.path(SALIDAS, "apendicea_mc.csv"), row.names = FALSE)
write.csv(data.frame(replica = rep(seq_len(N_GUARDA_MUESTRAS), each = N_ERU),
                     y = r10(unlist(muestras))),
          file.path(SALIDAS, "apendicea_mc_muestras.csv"), row.names = FALSE)

# =====================================================================
# L. MÓDULO 12 — Del renglón al plano: las sedes de Bogotá
# =====================================================================
message("L. modulo 12 - las sedes de Bogota")
quien <- nnwhich(sedes$x, sedes$y)
recip <- quien[quien] == seq_along(quien)
ceros <- sum(nn == 0)
# Una distancia por PAREJA recíproca: la otra mitad es la misma cifra.
uno_por_pareja <- nn[!recip | seq_along(quien) < quien]
guarda(length(uno_por_pareja) == N_SEDES - sum(recip) / 2,
       "m12: una por pareja deja n menos la mitad de las recíprocas")
# La constante de CSR: la fracción de vecinos recíprocos en un Poisson del
# plano, 6π / (8π + 3√3). Se comprueba simulando, no se copia.
c_recip <- 6 * pi / (8 * pi + 3 * sqrt(3))
set.seed(SEMILLA)
Xc <- runifpoint(20000, win = square(1))
wq <- nnwhich(Xc); bd <- bdist.points(Xc)
# Un margen FIJO al borde, no uno proporcional a la distancia de cada punto a
# su vecino. La primera versión exigía «borde > 3 × distancia al vecino», y eso
# selecciona los puntos con vecinos cercanos: sesgaba la fracción hacia arriba
# (0.628 sobre 20 semillas contra 0.6215 de la fórmula). Lo midió el auditor
# independiente (2026-10-02). Con 20 000 puntos en el cuadrado unidad la
# distancia típica al vecino es 0.0035, así que 0.03 son unas ocho.
lejos <- bd > 0.03
c_sim <- mean((wq[wq] == seq_along(wq))[lejos])
ancla(c_sim, c_recip, "fracción recíproca bajo CSR: simulación contra fórmula", tol = 0.012)  # unos 3 errores estándar con ~17 600 puntos lejos del borde
lambda_km2 <- N_SEDES / AREA_KM2
lambda_m2 <- lambda_km2 / 1e6
media_csr <- 0.5 / sqrt(lambda_m2)
mediana_csr <- sqrt(log(2) / (lambda_m2 * pi))
sel12 <- function(v) {
  av <- NA_character_
  u <- withCallingHandlers(bw.ucv(v), warning = function(w) {
    av <<- conditionMessage(w); invokeRestart("muffleWarning") })
  list(ucv = r10(u), aviso = !is.na(av), sj = r10(bw.SJ(v)), nrd0 = r10(bw.nrd0(v)), n = length(v))
}
# POR QUÉ COLAPSA LA UCV, CON NÚMEROS Y NO CON ADJETIVOS.
#
# Con empates EXACTOS, cuando h -> 0 el criterio se comporta como
#   UCV(h) ≈ (1/h) [ R(K)(n + 2E)/n² − 4 E K(0) / (n(n−1)) ],
# con E el número de parejas {i, j} con X_i = X_j. El corchete se hace
# negativo —y la UCV se va a −∞, sin mínimo— cuando E/n supera
#   R(K) / (4K(0) − 2R(K)) ≈ 0.2735 con el núcleo gaussiano.
# Y una lista de distancias al vecino trae empates POR CONSTRUCCIÓN: cada
# pareja recíproca aporta la misma cifra dos veces, y bajo CSR son el 62 %
# de los puntos, o sea E/n ≈ 0.31 > 0.2735. Los ceros (sedes que comparten
# dirección) empatan además TODOS entre sí.
#
# Medido el 2026-10-02: la primera versión culpaba solo a las parejas, y la
# guarda la desmintió (con una por pareja y los ceros dentro también
# colapsa); la segunda esperaba que Kennedy colapsara, y `bw.ucv` devolvió
# 30 m sin aviso: es un mínimo LOCAL dentro de su intervalo de búsqueda, y
# el criterio exacto con h minúsculo sigue siendo negativo. Eso es el
# ejercicio 10.
ucv_exacta <- function(v, h) {
  n <- length(v); Dd <- outer(v, v, "-"); W <- dnorm(Dd / h); diag(W) <- 0
  sum(dnorm(Dd / (sqrt(2) * h))) / (n^2 * h * sqrt(2)) - 2 * mean(rowSums(W) / ((n - 1) * h))
}
empates <- function(v) { t <- table(round(v, 6)); sum(t * (t - 1) / 2) }
UMBRAL <- (1 / (2 * sqrt(pi))) / (4 * dnorm(0) - 2 / (2 * sqrt(pi)))
H_MINUSCULO <- 0.001
H_RAZONABLE <- 20
sel12 <- function(v) {
  av <- NA_character_
  u <- withCallingHandlers(bw.ucv(v), warning = function(w) {
    av <<- conditionMessage(w); invokeRestart("muffleWarning") })
  # La referencia del «negativo»: la UCV estima MISE − ∫f², que es negativo
  # también en un buen ancho. Lo que delata el colapso no es el signo sino
  # caer POR DEBAJO del valor en un ancho razonable, 20 m (revisión 2).
  list(ucv = r10(u), aviso = !is.na(av), sj = r10(bw.SJ(v)), nrd0 = r10(bw.nrd0(v)),
       n = length(v), empates = empates(v), empates_por_n = r10(empates(v) / length(v)),
       ucv_h_minusculo = r10(ucv_exacta(v, H_MINUSCULO)), ucv_h20 = r10(ucv_exacta(v, H_RAZONABLE)),
       busqueda_desde = r10(0.1 * 1.144 * sqrt(var(v)) * length(v)^(-1 / 5)))
}
par0 <- uno_por_pareja[uno_por_pareja > 0]
s_todas <- sel12(nn); s_sin0 <- sel12(nn[nn > 0]); s_par <- sel12(uno_por_pareja)
s_par0 <- sel12(par0)
for (z in list(s_todas, s_sin0, s_par)) {
  guarda(z$empates_por_n > UMBRAL && z$ucv_h_minusculo < z$ucv_h20,
         "m12: con empates por encima del umbral el criterio con h minúsculo cae bajo el de 20 m")
  guarda(z$aviso && z$ucv < 0.4 * z$sj, "m12: con empates bw.ucv colapsa y avisa")
}
guarda(s_par0$empates_por_n < UMBRAL && s_par0$ucv_h_minusculo > s_par0$ucv_h20,
       "m12: sin parejas ni ceros el criterio con h minúsculo queda por encima del de 20 m")
# bw.ucv no iguala al decimal el extremo de su búsqueda: se queda a una
# tolerancia. Solo el aviso lo delata (revisión 2).
guarda(s_todas$ucv > s_todas$busqueda_desde && s_todas$ucv < 1.1 * s_todas$busqueda_desde,
       "m12: bw.ucv se queda junto al extremo inferior, sin igualarlo")
guarda(!s_par0$aviso && abs(s_par0$ucv / s_par0$sj - 1) < 0.1,
       "m12: sin parejas ni ceros, la UCV vuelve junto a SJ")
# El borde en r = 0, con el ancho de SJ sobre una por pareja.
h12 <- s_par0$sj
masa_neg <- mean(pnorm(-nn / h12))                         # masa que cae en r < 0
g12 <- seq(0, 600, by = 0.5)
f_sin <- sapply(g12, function(r) mean(dnorm((r - nn) / h12)) / h12)
f_ref <- sapply(g12, function(r) mean(dnorm((r - nn) / h12) + dnorm((r + nn) / h12)) / h12)
e_x <- pnorm(g12 / h12)                                    # e(r): lo que queda a la derecha
f_e <- f_sin / e_x
pesos <- 1 / pnorm(nn / h12)                               # Diggle: cada dato, su propia masa
f_dig <- sapply(g12, function(r) mean(pesos * dnorm((r - nn) / h12)) / h12)
m_sin <- 1 - masa_neg
m_ref <- 1
m_dig <- mean(pesos * (1 - pnorm(-nn / h12)))              # = 1 exacto
# LO QUE APORTA CADA DATO con la corrección en el punto de estimación, e(x).
# Es la de `density.ppp` por defecto, y el capítulo 5 (módulo 4) encontró que
# en el plano «la masa se pasa» o se queda corta según dónde estén las sedes.
# En una dimensión tiene forma cerrada en el borde: un dato en r = 0 aporta
# ∫ φ(u)/Φ(u) du sobre [0, ∞) = ln 2. Y un dato a 1.6 anchos del borde aporta
# más de 1. El total depende del patrón, no del método.
# LA INTEGRAL VA SOBRE EL TRAMO DONDE VIVE LA LOMA, [d − 12, d + 12], y no
# sobre [0, ∞). Con [0, ∞) `integrate()` no encuentra la loma de una sede
# lejana —las hay a más de cien anchos del borde— y devuelve 0 en vez de 1: la
# primera versión publicaba una masa total de 0.949 con 89 sedes aportando
# nada, y la cazó `audita_apendicea.py` (2026-10-02). Fuera de ese tramo el
# integrando es menor que 2·φ(12), del orden de 1e-32.
aporte <- function(d) integrate(function(x) dnorm(x - d) / pnorm(x),
                                max(0, d - 12), d + 12, rel.tol = 1e-10)$value
ds12 <- c(0, 0.5, 1, 1.5, 2, 3, 4)
ap12 <- sapply(ds12, aporte)
ap_max <- optimize(function(d) -aporte(d), c(0, 4))
ancla(ap12[1], log(2), "un dato en el borde aporta ln 2 con la corrección e(x)", tol = 1e-6)
m_e <- mean(sapply(nn / h12, aporte))
guarda(-ap_max$objective > 1, "m12: a cierta distancia del borde un dato aporta más de 1")
guarda(m_e < 1, "m12: en las sedes de Bogotá la corrección e(x) se queda corta")
guarda(abs(m_dig - 1) < 1e-12, "m12: la corrección de Diggle conserva la masa exactamente")
g_csr <- function(r) 2 * pi * lambda_m2 * r * exp(-lambda_m2 * pi * r^2)
# EN r = 0 MANDAN LOS CEROS. Las 79 distancias cero son un átomo —el salto de
# G en r = 0 del capítulo 4, módulo 7—, no densidad, y ponen más de la mitad
# de la altura de la curva sin corregir en el borde. La primera versión leía
# esa altura como «la mitad de lo que debería» (revisión 2).
aporte_ceros <- ceros * dnorm(0) / (N_SEDES * h12)
guarda(aporte_ceros > 0.5 * f_sin[1], "m12: los ceros ponen más de la mitad de la altura en r = 0")
# La reflejada baja desde r = 0 hasta un valle antes de subir a la moda. ESE
# MÁXIMO EN EL BORDE LO PONEN ENTEROS LOS CEROS: sin ellos, la reflejada
# arranca abajo y sube. La primera versión de la revisión 2 decía que
# reflejar lo «fabricaba»; lo midió la segunda pasada (2026-10-02).
i_val <- which(diff(sign(diff(f_ref))) > 0)[1] + 1
i_moda <- which.max(f_ref[g12 > g12[i_val]]) + sum(g12 <= g12[i_val])
guarda(!is.na(i_val) && f_ref[1] > f_ref[i_val] && g12[i_moda] > g12[i_val],
       "m12: la reflejada baja desde r = 0 hasta un valle antes de subir a la moda")
nn_pos <- nn[nn > 0]
r_sin0 <- c(0, 5, 10, 20)
f_ref_sin0 <- sapply(r_sin0, function(r) mean(dnorm((r - nn_pos) / h12) + dnorm((r + nn_pos) / h12)) / h12)
guarda(all(diff(f_ref_sin0) > 0) && f_ref_sin0[1] < f_ref[i_val],
       "m12: sin los ceros la reflejada sube desde r = 0: el máximo del borde es de los ceros")
# La lista depurada es otra distribución: una pareja cuenta una vez.
D$m12 <- list(
  n = N_SEDES, ceros = ceros, area_km2 = r10(AREA_KM2), lambda_km2 = r10(lambda_km2),
  recipro = list(n = sum(recip), pct = r10(100 * mean(recip)), parejas = sum(recip) / 2,
                 csr = r10(c_recip), csr_pct = r10(100 * c_recip), csr_simulada = r10(c_sim), csr_n = 20000L),
  distancias = list(media = r10(mean(nn)), mediana = r10(median(nn)), maximo = r10(max(nn)),
                    distintas = length(unique(round(nn, 6)))),
  csr = list(media = r10(media_csr), mediana = r10(mediana_csr),
             clark_evans = r10(mean(nn) / media_csr)),
  umbral_empates = r10(UMBRAL), h_minusculo = H_MINUSCULO,
  csr_parejas_por_n = r10(c_recip / 2),
  umbral_recipro_pct = r10(100 * 2 * UMBRAL),
  selectores = list(todas = s_todas, sin_ceros = s_sin0, una_por_pareja = s_par,
                    una_por_pareja_sin_ceros = s_par0),
  ceros_una_por_pareja = sum(uno_por_pareja == 0),
  borde = list(h = r10(h12), masa_negativa_pct = r10(100 * masa_neg),
               masa_sin = r10(m_sin), masa_reflejada = m_ref, masa_e = r10(m_e),
               aporte = list(d_sobre_h = ds12, aporte = r10(ap12), ln2 = r10(log(2)),
                             d_max = r10(ap_max$minimum), max = r10(-ap_max$objective)),
               cerca_del_borde_pct = r10(100 * mean(nn < h12)),
               masa_diggle = r10(m_dig),
               f0_sin = r10(f_sin[1]), f0_reflejada = r10(f_ref[1]),
               f0_e = r10(f_e[1]), f0_diggle = r10(f_dig[1]),
               f0_ceros = r10(aporte_ceros),
               reflejada_valle = list(r = g12[i_val], f = r10(f_ref[i_val])),
               reflejada_sin_ceros = list(r = r_sin0, f = r10(f_ref_sin0)),
               reflejada_moda = list(r = g12[i_moda], f = r10(f_ref[i_moda]))),
  depurada = list(n = length(par0), mediana = r10(median(par0))),
  curvas = list(r = g12[seq(1, length(g12), by = 4)],
                sin = r10(f_sin[seq(1, length(g12), by = 4)]),
                reflejada = r10(f_ref[seq(1, length(g12), by = 4)]),
                e = r10(f_e[seq(1, length(g12), by = 4)]),
                diggle = r10(f_dig[seq(1, length(g12), by = 4)]),
                csr = r10(g_csr(g12[seq(1, length(g12), by = 4)]))),
  curvas_hasta = max(g12),
  nn = round(nn, 1), una_por_pareja = round(uno_por_pareja, 1))
guarda(D$m12$borde$f0_reflejada > 1.8 * D$m12$borde$f0_sin,
       "m12: reflejar casi duplica la densidad en r = 0")
guarda(D$m12$csr$clark_evans < 1, "m12: las sedes están más cerca que bajo CSR")

# =====================================================================
# M. LOS EJERCICIOS (apendicea_soluciones.json)
#
# Viven aquí y no en `genera_soluciones.R` porque ese guion elige la sección
# por número de capítulo (`as.integer(args)`), y el apéndice no lo tiene. La
# maquinaria es la misma del capítulo 5: cada respuesta se ancla a un trozo
# LITERAL de su enunciado, y `sin_contestar()` vigila que toda demanda del
# enunciado caiga en alguna respuesta.
# =====================================================================
message("M. los ejercicios")
responde <- function(enunciado, pide, respuesta) {
  if (!grepl(pide, enunciado, fixed = TRUE))
    stop("una respuesta no encuentra su pregunta en el enunciado: «", pide, "»")
  list(pide = pide, respuesta = respuesta)
}
DEMANDA <- "(*UCP)(?<!\\p{L})(?:[Dd]i|[Ee]xplica|[Ee]ncuéntralo|[Ee]ncuentra|[Cc]ontesta|[Cc]ompara|[Dd]iscute)(?!\\p{L})|¿"
sin_contestar <- function(e) {
  en <- e$enunciado
  ini <- vapply(e$solucion$respuestas, function(r)
    as.integer(regexpr(r$pide, en, fixed = TRUE)), integer(1))
  fin <- ini + vapply(e$solucion$respuestas, function(r) nchar(r$pide), integer(1)) - 1L
  m <- gregexpr(DEMANDA, en, perl = TRUE)[[1]]
  largo <- attr(m, "match.length")
  fuera <- character(0)
  for (i in seq_along(m)) {
    if (m[i] < 0) break
    dentro <- any(ini <= m[i] & m[i] <= fin)
    # «Compara las dos cifras: ¿…?» — la demanda que presenta a otra queda
    # contestada si una respuesta empieza detrás de ella en la misma frase
    # (la misma regla que el capítulo 5).
    if (!dentro) {
      resto <- ini[ini > m[i]]
      dentro <- length(resto) > 0 && grepl(":", substr(en, m[i], min(resto)), fixed = TRUE) &&
        !grepl(".", substr(en, m[i], min(resto)), fixed = TRUE)
    }
    if (!dentro) fuera <- c(fuera, substr(en, m[i], m[i] + largo[i] + 30L))
  }
  fuera
}
f_g <- function(x, datos, h) mean(dnorm((x - datos) / h)) / h
silv <- function(X) 1.06 * min(sd(X), IQR(X) / 1.34) * length(X)^(-1 / 5)
E <- list()

# --- E1 · Histograma y Parzen gaussiano --------------------------------
X1 <- c(2.5, 3.5, 5, 5.5, 7, 8.5, 10, 11, 11.5, 14)
hh1 <- hist(X1, plot = FALSE)
h1s <- silv(X1)
gr1 <- seq(min(X1) - 3, max(X1) + 3, length.out = 400)
fs1 <- sapply(gr1, f_g, datos = X1, h = h1s)
fu1 <- sapply(gr1, f_g, datos = X1, h = 1)
# La moda menor de h = 1 y el valle que la separa: la revisión de la
# autoevaluación (2026-10-02) midió que la tercera moda, la del dato aislado,
# sobresale menos de una milésima — a la vista son dos bultos y un hombro.
ext1 <- function(y, signo) which(diff(sign(diff(y))) == signo) + 1
mx1 <- ext1(fu1, -2); mn1 <- ext1(fu1, 2)
i_baja1 <- mx1[which.min(fu1[mx1])]
valle1 <- max(c(if (any(mn1 < i_baja1)) fu1[max(mn1[mn1 < i_baja1])],
                if (any(mn1 > i_baja1)) fu1[min(mn1[mn1 > i_baja1])], 0))
modas_hist1 <- modas_secuencia(hh1$counts)
guarda(modas_hist1 == 2L && modas_secuencia(fs1) == 1L && modas_secuencia(fu1) == 3L &&
       gr1[i_baja1] > max(X1) - 1 && fu1[i_baja1] - valle1 < 0.002,
       "e1: el histograma da dos grupos, bw.nrd uno y h = 1 tres, con la del 14 casi plana")
en1 <- paste(
  "Con X = {2.5, 3.5, 5, 5.5, 7, 8.5, 10, 11, 11.5, 14}, construye el histograma que R",
  "hace por defecto (`hist(X, probability = TRUE)`) y después suavízalo con ventanas de",
  "Parzen y núcleo gaussiano, con el ancho de `bw.nrd` y con h = 1. Calcula a mano",
  "f̂(7) con h = 1. ¿Cuántas modas deja cada ancho?")
E$e1 <- list(
  titulo = "Del histograma a la curva", enunciado = en1, modulos = "2 y 5",
  pista = paste("Para f̂(7) con h = 1, calcula 7 − xᵢ para cada dato, pásalo por φ y promedia. Para",
                "las modas, piensa que un dato aislado solo levanta bulto propio si h es pequeño frente",
                "a la distancia a sus vecinos, y mira cuánto sobresale cada bulto de su valle."),
  pasos = list(
    list(paso = sprintf("Intervalos del histograma por defecto (Sturges propone %d y pretty() redondea los cortes)",
                        nclass.Sturges(X1)), valor = length(hh1$counts)),
    list(paso = "Ancho de cada intervalo", valor = diff(hh1$breaks)[1]),
    list(paso = "Modas del histograma por defecto", valor = modas_hist1),
    list(paso = "Ancho de banda de bw.nrd", valor = r10(h1s)),
    list(paso = "Suma de φ((7 − xᵢ)/1)", valor = r10(sum(dnorm(7 - X1)))),
    list(paso = "f̂(7) con h = 1", valor = r10(f_g(7, X1, 1))),
    list(paso = "Modas con el ancho de bw.nrd", valor = modas_secuencia(fs1)),
    list(paso = "Modas con h = 1", valor = modas_secuencia(fu1)),
    list(paso = "Altura de la moda menor con h = 1", valor = r10(fu1[i_baja1])),
    list(paso = "Altura del valle que la separa", valor = r10(valle1)),
    list(paso = "Área de la curva de bw.nrd (trapecios)", valor = r10(trapecio(
      seq(min(X1) - 8 * h1s, max(X1) + 8 * h1s, length.out = 2001),
      sapply(seq(min(X1) - 8 * h1s, max(X1) + 8 * h1s, length.out = 2001), f_g, datos = X1, h = h1s))))),
  solucion = list(
    respuestas = list(responde(en1, "Calcula a mano",
      sprintf(paste("Las desviaciones 7 − xᵢ van de 4.5 a −7; sus φ suman %.4f, y entre n = 10",
                    "queda f̂(7) = %.4f."), sum(dnorm(7 - X1)), f_g(7, X1, 1))),
      responde(en1, "¿Cuántas modas deja cada ancho?",
      sprintf(paste("El histograma por defecto, con conteos %s, tiene %d modas. Con el ancho de",
                    "bw.nrd (%.4f) la curva tiene %d moda; con h = 1, %d, pero la menor —la del dato",
                    "aislado %g— sobresale apenas %.4f de su valle (%.4f contra %.4f): a simple vista",
                    "se ven dos bultos y un hombro."),
              paste(hh1$counts, collapse = ", "), modas_hist1, h1s,
              modas_secuencia(fs1), modas_secuencia(fu1), max(X1),
              fu1[i_baja1] - valle1, fu1[i_baja1], valle1))),
    lectura = paste("El histograma por defecto sugiere dos grupos, la curva de bw.nrd los funde en",
                    "uno y la de h = 1 los separa: los datos no deciden cuál de las tres lecturas es la",
                    "buena; lo decide el ancho.")))

# --- E2 · k-NN a mano ------------------------------------------------
X2 <- c(1, 2, 3, 5, 6, 7, 9, 10)
d2s <- sort(abs(X2 - 4))
en2 <- paste(
  "Con X = {1, 2, 3, 5, 6, 7, 9, 10}, estima la densidad en x = 4 con k-NN y k = 3.",
  "¿Cuántas observaciones hay de verdad dentro del intervalo de radio d₃?")
E$e2 <- list(
  titulo = "k vecinos a mano", enunciado = en2, modulos = "4 y 7",
  pista = paste("Ordena las distancias |4 − xᵢ| de menor a mayor: d₃ es la tercera. Después cuenta",
                "cuántas son menores o iguales que ella; fíjate en las que se repiten."),
  pasos = list(list(paso = "Distancia al tercer vecino d₃", valor = d2s[3]),
               list(paso = "Longitud de la ventana 2d₃", valor = 2 * d2s[3]),
               list(paso = "f̂(4) = k / (2 n d₃)", valor = r10(3 / (2 * 8 * d2s[3]))),
               list(paso = "Observaciones dentro de [4 − d₃, 4 + d₃]",
                    valor = sum(abs(X2 - 4) <= d2s[3]))),
  solucion = list(
    respuestas = list(responde(en2, "¿Cuántas observaciones hay de verdad dentro",
      sprintf(paste("%d: el 2, el 3, el 5 y el 6. Hay empates a distancia 1 y a distancia 2, y",
                    "el estimador cobra k = 3 aunque la ventana encierre %d."),
              sum(abs(X2 - 4) <= d2s[3]), sum(abs(X2 - 4) <= d2s[3])))),
    lectura = "El k-NN fija k y deja que la ventana crezca; cuando hay distancias empatadas, la ventana encierra más de k."))

# --- E3 · La mezcla con k-NN -----------------------------------------
set.seed(SEMILLA)
X3 <- c(rnorm(100, 5, 1), rnorm(100, 10, 1.5))
g3e <- seq(min(X3) - 1, max(X3) + 1, length.out = 300)
fk <- function(k) sapply(g3e, function(t) k / (2 * 200 * sort(abs(X3 - t))[k]))
f5 <- fk(5); f10 <- fk(10)
f_teo3 <- function(x) 0.5 * dnorm(x, 5, 1) + 0.5 * dnorm(x, 10, 1.5)
# EN 7.5, NO EN EL NODO MÁS CERCANO de la rejilla (7.5055): con los dientes
# del k-NN el nodo daba 0.0808 donde 7.5 da 0.0780, y el módulo 7, con otra
# rejilla, daba una tercera cifra de la misma muestra (revisión 2).
knn3_en <- function(k, t) k / (2 * 200 * sort(abs(X3 - t))[k])
f5_75 <- knn3_en(5, 7.5); f10_75 <- knn3_en(10, 7.5)
en3 <- paste(
  "Con `set.seed(2026)`, genera 100 datos de N(5, 1) y 100 de N(10, 1.5): es la muestra del",
  "módulo 7. Estima la densidad con k-NN y k = 5 y k = 10 sobre una rejilla de 300 puntos que",
  "desborde los datos en una unidad por cada lado, evalúa las dos estimaciones en x = 7.5 y",
  "compáralas con la densidad verdadera allí. ¿Integra 1 la curva del k-NN?")
E$e3 <- list(
  titulo = "Una mezcla vista con k vecinos", enunciado = en3, modulos = "7",
  pista = paste("Para f̂(7.5), d_k es la k-ésima distancia ordenada a 7.5, no al nodo de la rejilla más",
                "cercano. Para el área, integra por trapecios sobre la rejilla y piensa en cómo decaen",
                "sus colas lejos de los datos."),
  pasos = list(
    list(paso = "f̂(7.5) con k = 5", valor = r10(f5_75)),
    list(paso = "f̂(7.5) con k = 10", valor = r10(f10_75)),
    list(paso = "Densidad verdadera en 7.5", valor = r10(f_teo3(7.5))),
    list(paso = "Con k = 5, en el nodo de la rejilla más cercano a 7.5", valor = r10(f5[which.min(abs(g3e - 7.5))])),
    list(paso = "Área de la curva con k = 5", valor = r10(trapecio(g3e, f5))),
    list(paso = "Área de la curva con k = 10", valor = r10(trapecio(g3e, f10)))),
  solucion = list(
    respuestas = list(responde(en3, "compáralas con la densidad verdadera",
      sprintf(paste("Con k = 5 la estimación en el valle es %.4f, casi el doble de la verdad, %.4f;",
                    "con k = 10 es %.4f, casi exacta. En un punto suelto la cifra depende mucho de k,",
                    "de la muestra y hasta del punto exacto: en el nodo de la rejilla más cercano a 7.5,",
                    "con k = 5, sale %.4f. El k-NN se lee en la forma de la curva, no en un valor."),
              f5_75, f_teo3(7.5), f10_75, f5[which.min(abs(g3e - 7.5))])),
      responde(en3, "¿Integra 1 la curva del k-NN?",
      sprintf(paste("No: %.4f con k = 5 y %.4f con k = 10, solo dentro de la rejilla. Sus colas",
                    "decaen como 1/|x|, y esa integral no converge."),
              trapecio(g3e, f5), trapecio(g3e, f10)))),
    lectura = paste("Con k = 10 la curva sigue llena de dientes: subir k un poco no los quita, porque",
                    "son de la fórmula —cada vez que cambia el grupo de vecinos, el radio cambia de",
                    "ritmo— y no de la muestra (módulo 7). Cuántos se cuentan depende además de lo fina",
                    "que sea la rejilla.")))
# Lo que la respuesta afirma, vigilado: con k = 5 se pasa, con k = 10 casi acierta.
guarda(f5_75 > 1.5 * f_teo3(7.5) && abs(f10_75 / f_teo3(7.5) - 1) < 0.05,
       "e3: con k = 5 el valle se pasa y con k = 10 casi acierta")
guarda(abs(f5_75 - D$m7$mezcla$por_k[[which(ks7 == 5)]]$f_valle) < 1e-9,
       "e3: f̂(7.5) con k = 5 es la misma cifra que el módulo 7")

# --- E4 · ASH ----------------------------------------------------------
X4 <- c(2, 4, 4.5, 6, 6.5, 7, 9)
f4 <- function(m, x) ash(X4, 1, m, x)
# m IMPARES: con m = 2, 4 y 8 el valor en 3.5 quedaba clavado en el del
# triangular desde m = 2 (el 3.5 y el 4 caen alineados con la rejilla fina) y
# no se veía que el ASH SE ACERCA a algo. Con 1, 3, 5 y 9 sube hacia él
# (revisión 2). Y la convención de los cortes va en el enunciado: con la de
# hist() por defecto, (a, b], el intervalo de 3 a 4 contiene al 4.
en4 <- paste(
  "Con X = {2, 4, 4.5, 6, 6.5, 7, 9}, construye el ASH con h = 1 fijo y m = 1, 3, 5 y 9,",
  "con la primera rejilla cortada en los enteros e intervalos [a, a + 1) (`right = FALSE`).",
  "Evalúalo en x = 3.5, el centro de un intervalo vacío del histograma, y compáralo con el",
  "núcleo triangular de semiancho 1 en ese punto. Explica qué cambia al aumentar m y qué no",
  "cambia.")
ms4 <- c(1, 3, 5, 9)
v4 <- sapply(ms4, function(m) f4(m, 3.5))
tri4 <- mean(pmax(0, 1 - abs(3.5 - X4)))
g4 <- seq(0, 11, by = 0.001)
area4 <- sapply(ms4, function(m) trapecio(g4, f4(m, g4)))
guarda(v4[1] == 0 && all(diff(v4) > 0) && all(v4 < tri4), "e4: el hueco de 3.5 sube hacia el triangular")
guarda(abs(f4(2, 3.5) - tri4) < 1e-12, "e4: con m par el ASH ya da el valor del triangular en 3.5")
guarda(all(abs(area4 - 1) < 2e-3), "e4: el área sigue valiendo 1 con todos los m")
E$e4 <- list(
  titulo = "El ASH rellena los huecos", enunciado = en4, modulos = "3",
  pista = paste("Para cada m, cuenta en cuántos de los m histogramas desplazados el 3.5 comparte",
                "casilla con algún dato y divide entre m: es la fracción de histogramas que le dan la",
                "altura de una barra con un dato, 1/(n·h). El módulo 3 dice a qué se acerca el ASH",
                "cuando m crece."),
  pasos = c(lapply(seq_along(ms4), function(i) list(
              paso = sprintf("ASH en x = 3.5 con m = %d", ms4[i]), valor = r10(v4[i]))),
            list(list(paso = "Núcleo triangular de semiancho 1 en x = 3.5", valor = r10(tri4)),
                 list(paso = "Área con m = 1 (trapecios)", valor = r10(area4[1])),
                 list(paso = "Área con m = 9 (trapecios)", valor = r10(area4[4])))),
  solucion = list(
    respuestas = list(responde(en4, "Explica qué cambia al aumentar m y qué no cambia",
      sprintf(paste("Cambia la forma: el hueco de x = 3.5 pasa de %.4f a %.4f, %.4f y %.4f con",
                    "m = 3, 5 y 9, y se acerca a %.4f, lo que da allí el núcleo triangular (módulo 3):",
                    "cada histograma desplazado que pone el 3.5 en la misma casilla que el dato 4 le",
                    "suma un poco. Con m par ya sale ese valor, porque el 3.5 y el 4 quedan alineados",
                    "con la rejilla fina. No cambia el ancho h, que sigue fijando cuánto se suaviza, ni",
                    "el área, que sigue valiendo 1."), v4[1], v4[2], v4[3], v4[4], tri4))),
    lectura = "Subir m no suaviza más: quita la dependencia del origen. Suavizar más es subir h."))

# --- E5 · Parzen con tres núcleos ---------------------------------------
X5 <- c(1, 2, 3, 3.5, 5, 5.5, 6, 8)
u5 <- 4 - X5
sumas5 <- c(uniforme = sum(NUC$uniforme(u5)), triangular = sum(NUC$triangular(u5)),
            gaussiano = sum(dnorm(u5)))
h5s <- silv(X5)
# El ancho de bw.nrd usado de las DOS maneras: como semiancho del soporte y
# como desviación típica del núcleo, que es como lo usa density(). La primera
# versión del ejercicio solo hacía la primera y su lectura afirmaba lo de la
# segunda («R fija la escala y entonces los núcleos casi coinciden») sin que
# ninguna cifra lo mostrara; la revisión independiente lo cazó (2026-10-02).
r5_sop <- c(uniforme = mean(NUC$uniforme(u5 / h5s)) / h5s,
            triangular = mean(NUC$triangular(u5 / h5s)) / h5s,
            gaussiano = mean(dnorm(u5 / h5s)) / h5s)
r5_sd <- c(uniforme = mean(NUC$uniforme(u5 / (sqrt(3) * h5s))) / (sqrt(3) * h5s),
           triangular = mean(NUC$triangular(u5 / (sqrt(6) * h5s))) / (sqrt(6) * h5s),
           gaussiano = mean(dnorm(u5 / h5s)) / h5s)
guarda(diff(range(r5_sd)) < 0.5 * diff(range(r5_sop)),
       "e5: con la misma desviación típica los tres núcleos se parecen más que con el mismo soporte")
en5 <- paste(
  "Con X = {1, 2, 3, 3.5, 5, 5.5, 6, 8}, estima la densidad en x = 4 con ventanas de",
  "Parzen de núcleo uniforme, triangular y gaussiano, primero con h = 1 en la escala de",
  "soporte [−1, 1] y después con el ancho de `bw.nrd` usado de dos maneras: como semiancho",
  "del soporte y como desviación típica del núcleo, que es como lo usa `density()`. ¿Por qué",
  "el triangular da tan poco con h = 1? ¿En cuál de las dos maneras se parecen más los tres?")
E$e5 <- list(
  titulo = "Tres núcleos, un punto", enunciado = en5, modulos = "5 y 6",
  pista = paste("¿Qué desviación típica tiene una caja de semiancho a? ¿Y un triángulo? La columna",
                "«Soporte por σ» del módulo 6 lo dice. Con h = 1 en la escala de soporte, mira qué",
                "datos caen justo en el borde de la ventana."),
  pasos = list(
    list(paso = "Uniforme, h = 1", valor = r10(sumas5[["uniforme"]] / 8)),
    list(paso = "Triangular, h = 1", valor = r10(sumas5[["triangular"]] / 8)),
    list(paso = "Gaussiano, h = 1", valor = r10(sumas5[["gaussiano"]] / 8)),
    list(paso = "Ancho de bw.nrd", valor = r10(h5s)),
    list(paso = "Uniforme, bw.nrd como semiancho", valor = r10(r5_sop[["uniforme"]])),
    list(paso = "Triangular, bw.nrd como semiancho", valor = r10(r5_sop[["triangular"]])),
    list(paso = "Gaussiano, bw.nrd como desviación típica", valor = r10(r5_sop[["gaussiano"]])),
    list(paso = "Uniforme, bw.nrd como desviación típica", valor = r10(r5_sd[["uniforme"]])),
    list(paso = "Triangular, bw.nrd como desviación típica", valor = r10(r5_sd[["triangular"]]))),
  solucion = list(
    respuestas = list(
      responde(en5, "¿Por qué el triangular da tan poco con h = 1?",
        sprintf(paste("Porque en |u| = 1 vale cero: de los datos a distancia 1 o menos (3, 3.5 y",
                      "5) solo el 3.5 pesa, y pesa 0.5. La suma es %.1f contra %.1f del uniforme.",
                      "Con el mismo soporte el triangular es más estrecho: su desviación típica",
                      "es menor."), sumas5[["triangular"]], sumas5[["uniforme"]])),
      responde(en5, "¿En cuál de las dos maneras se parecen más los tres?",
        sprintf(paste("En la de R. Con el ancho como semiancho del soporte dan %.4f, %.4f y %.4f;",
                      "como desviación típica, %.4f, %.4f y %.4f. El gaussiano, cuyo soporte es toda la",
                      "recta, da lo mismo en las dos. Igualar la desviación típica es igualar cuánto suaviza",
                      "cada núcleo, e igualar el soporte no."),
                r5_sop[["uniforme"]], r5_sop[["triangular"]], r5_sop[["gaussiano"]],
                r5_sd[["uniforme"]], r5_sd[["triangular"]], r5_sd[["gaussiano"]]))),
    lectura = "Fijar el soporte no es fijar la escala. R fija la escala —bw es la desviación típica del núcleo— y por eso, al mismo bw, sus núcleos casi coinciden."))

# --- E6 · Sensibilidad a k ------------------------------------------------
X6 <- c(10, 12, 13, 15, 15.5, 17, 19, 20)
d6 <- sort(abs(X6 - 14))
f6 <- (1:8) / (2 * 8 * d6)
en6 <- paste(
  "Con X = {10, 12, 13, 15, 15.5, 17, 19, 20}, estima la densidad k-NN en x = 14 para",
  "k = 1, …, 8. Discute por qué la curva de f̂(14) contra k no es monótona.")
E$e6 <- list(
  titulo = "Qué pasa al mover k", enunciado = en6, modulos = "7 y 8",
  pista = paste("Para cada k, d es la k-ésima distancia ordenada a 14. Fíjate en los k en que esa",
                "distancia no cambia y en los que salta."),
  pasos = lapply(1:8, function(k) list(paso = sprintf("f̂(14) con k = %d (d = %s)", k,
                                                      format(d6[k])), valor = r10(f6[k]))),
  solucion = list(
    respuestas = list(responde(en6, "Discute por qué la curva de f̂(14) contra k no es monótona",
      sprintf(paste("Porque el numerador sube de uno en uno y el radio sube a saltos: de k = 1 a",
                    "k = 2 el radio no cambia (13 y 15 están a la misma distancia) y la",
                    "estimación se duplica, de %.4f a %.4f; desde k = 5 el radio crece más",
                    "rápido que k y la curva baja hasta %.4f con k = 8, que es 1/%g: los ocho datos",
                    "repartidos por igual en una ventana de largo %g."), f6[1], f6[2], f6[8],
              2 * d6[8], 2 * d6[8]))),
    lectura = "Un k pequeño lee pocos datos (varianza); uno grande lee el rango entero (sesgo)."))

# --- E7 · Parzen contra k-NN --------------------------------------------
X7 <- c(2, 3, 4, 6, 7, 8, 10, 11)
h7s <- silv(X7)
d7 <- sort(abs(X7 - 5))
p7 <- f_g(5, X7, h7s); k7 <- 3 / (2 * 8 * d7[3])
en7 <- paste(
  "Con X = {2, 3, 4, 6, 7, 8, 10, 11}, estima la densidad en x = 5 con Parzen gaussiano",
  "(ancho de `bw.nrd`) y con k-NN y k = 3. Compara las dos cifras: ¿coinciden por la",
  "misma razón?")
# La coincidencia de k = 3 es en parte casual: con k = 2, 4 y 6 el k-NN da
# 0.125 en el mismo punto. La primera versión la atribuía a un reparto
# simétrico de los datos alrededor de 5, que no existe (revisión 2).
knn7 <- (1:8) / (2 * 8 * d7)
guarda(knn7[2] == knn7[4] && knn7[4] == knn7[6] && abs(knn7[2] / p7 - 1) > 0.3,
       "e7: con k = 2, 4 y 6 el k-NN da lo mismo, y lejos de Parzen")
E$e7 <- list(
  titulo = "Dos estimadores, un punto", enunciado = en7, modulos = "5 y 7",
  pista = paste("Antes de concluir, calcula el k-NN en el mismo punto con k = 2 y con k = 4, y",
                "compara."),
  pasos = list(list(paso = "Ancho de bw.nrd", valor = r10(h7s)),
               list(paso = "Parzen gaussiano en 5", valor = r10(p7)),
               list(paso = "Distancia al tercer vecino", valor = d7[3]),
               list(paso = "k-NN en 5 (k = 3)", valor = r10(k7)),
               list(paso = "Cociente k-NN / Parzen", valor = r10(k7 / p7)),
               list(paso = "k-NN en 5 con k = 1", valor = r10(knn7[1])),
               list(paso = "k-NN en 5 con k = 2, 4 o 6", valor = r10(knn7[2]))),
  solucion = list(
    respuestas = list(responde(en7, "¿coinciden por la misma razón?",
      sprintf(paste("No. Parzen da %.4f promediando las ocho observaciones con pesos que decaen;",
                    "k-NN da %.4f mirando solo hasta el tercer vecino. El cociente, %.4f, es casi 1",
                    "en buena parte por casualidad: con k = 2, 4 o 6 el k-NN da %.4f en el mismo punto",
                    "(cociente %.4f), y con k = 1, %.4f. Parzen promedia todos los datos; el k-NN",
                    "salta cada vez que entra un vecino."),
              p7, k7, k7 / p7, knn7[2], knn7[2] / p7, knn7[1]))),
    lectura = "Que dos estimadores coincidan en un punto no dice que estimen lo mismo en el resto."))

# --- E8 · Los empates del tiempo de espera ----------------------------
X8 <- c(3, 5, 2, 4, 3, 6, 5, 7, 4, 5, 8, 2, 3, 4, 6, 5, 4, 5, 7)
h8s <- silv(X8)
d8 <- sort(abs(X8 - 5))
en8 <- paste(
  "Los tiempos de espera en la caja de una tienda son X = {3, 5, 2, 4, 3, 6, 5, 7, 4, 5,",
  "8, 2, 3, 4, 6, 5, 4, 5, 7} minutos. Haz el histograma con intervalos de un minuto",
  "centrados en los enteros, suavízalo con Parzen gaussiano (ancho de `bw.nrd`) y estima",
  "la densidad en 5 minutos con k-NN. ¿Qué k es el menor que se puede usar, y por qué?",
  "¿Qué dicen las tres estimaciones sobre la espera de los clientes?")
k8 <- which(d8 > 0)[1]
dentro8 <- sum(abs(X8 - 5) <= d8[k8])
guarda(dentro8 > k8 && k8 / (2 * 19 * d8[k8]) < f_g(5, X8, h8s) && f_g(5, X8, h8s) < sum(X8 == 5) / 19,
       "e8: el k-NN da la cifra más baja de las tres, con una ventana que encierra más que k")
E$e8 <- list(
  titulo = "Cinco clientes empatados", enunciado = en8, modulos = "2, 5 y 7",
  pista = paste("Mira cuántos clientes esperaron exactamente 5 minutos: ¿a qué distancia de 5",
                "están? Para la última pregunta, cuenta cuántos esperaron menos, exactamente 5 y",
                "más."),
  pasos = list(list(paso = "Clientes que esperaron exactamente 5 minutos", valor = sum(X8 == 5)),
               list(paso = "Altura de la barra de 5 minutos", valor = r10(sum(X8 == 5) / 19)),
               list(paso = "Ancho de bw.nrd", valor = r10(h8s)),
               list(paso = "Parzen en 5", valor = r10(f_g(5, X8, h8s))),
               list(paso = "Menor k con distancia positiva", valor = k8),
               list(paso = "k-NN en 5 con ese k", valor = r10(k8 / (2 * 19 * d8[k8]))),
               list(paso = "Observaciones dentro de su ventana, [4, 6]", valor = dentro8),
               list(paso = "Clientes que esperaron 4 minutos o menos", valor = sum(X8 <= 4)),
               list(paso = "Clientes que esperaron 6 minutos o más", valor = sum(X8 >= 6))),
  solucion = list(
    respuestas = list(responde(en8, "¿Qué k es el menor que se puede usar, y por qué?",
      sprintf(paste("k = %d. Con cinco observaciones iguales a 5, la distancia a los cinco",
                    "primeros vecinos es cero y k/(2n·0) es infinito: el estimador no está",
                    "definido. El sexto vecino está a 1 minuto y da %.4f."),
              k8, k8 / (2 * 19 * d8[k8]))),
      responde(en8, "¿Qué dicen las tres estimaciones sobre la espera de los clientes?",
      sprintf(paste("La barra del histograma da %.4f, Parzen %.4f y el k-NN %.4f: el k-NN es el más",
                    "bajo porque cobra %d vecinos aunque su ventana encierre %d. Sobre el servicio, lo",
                    "que se sostiene es más simple: %d de los 19 clientes esperaron 4 minutos o menos;",
                    "%d, exactamente 5 minutos, y %d, 6 minutos o más: uno de cada cuatro. Con datos redondeados y",
                    "empatados, lo que se sostiene es la proporción, %d/19 —la altura de la barra de un",
                    "minuto—, no la forma de una curva."),
              sum(X8 == 5) / 19, f_g(5, X8, h8s), k8 / (2 * 19 * d8[k8]), k8, dentro8,
              sum(X8 <= 4), sum(X8 == 5), sum(X8 >= 6), sum(X8 == 5)))),
    lectura = "Los datos redondeados traen empates, y los empates rompen al k-NN antes que a cualquier otro estimador."))

# --- E9 · Alturas: ASH, triangular y k-NN ------------------------------
X9 <- c(165, 170, 172, 168, 174, 175, 169, 171, 173, 175, 167, 168, 174, 176, 170, 172)
u9 <- (170 - X9) / 2
d9 <- sort(abs(X9 - 170))
# La pregunta del «menor k» repetía la del ejercicio 8; vuelve la del texto
# original, la que obliga a interpretar: el rango de alturas más común
# (revisión 2).
u9b <- (174 - X9) / 2
p9_170 <- sum(NUC$triangular(u9)) / (16 * 2); p9_174 <- sum(NUC$triangular(u9b)) / (16 * 2)
en9 <- paste(
  "Con las alturas X = {165, 170, 172, 168, 174, 175, 169, 171, 173, 175, 167, 168, 174,",
  "176, 170, 172} cm, estima la densidad en 170 cm con Parzen triangular (h = 2 en la",
  "escala de soporte) y con k-NN, k = 4, y repite la de Parzen en 174 cm. ¿Qué rango de",
  "alturas es el más común, y cuánto te fías de esa lectura con 16 datos?")
# LA MESETA VA DE 168 A 175, no a 174: la curva vale lo mismo en 174 y en 175
# y solo cae en 175.5 (lo midió la segunda revisión, 2026-10-02).
p9_en <- sapply(165:177, function(x) sum(NUC$triangular((x - X9) / 2)) / (16 * 2))
meseta9 <- (165:177)[p9_en >= p9_170 - 1e-12]
guarda(identical(range(meseta9), c(168L, 175L)) && all(diff(meseta9) == 1) && p9_174 > p9_170,
       "e9: la curva se queda alta de 168 a 175 y sube un poco de 170 a 174")
E$e9 <- list(
  titulo = "Las alturas del curso", enunciado = en9, modulos = "5 y 7",
  pista = paste("Evalúa la estimación de Parzen en cada centímetro de 166 a 177 y mira dónde se queda",
                "alta y dónde cae. ¿Cuántos datos de diferencia hay detrás de la diferencia entre 170 y",
                "174?"),
  pasos = list(list(paso = "Suma de los pesos triangulares en 170", valor = sum(NUC$triangular(u9))),
               list(paso = "Parzen triangular en 170", valor = r10(p9_170)),
               list(paso = "Distancia al cuarto vecino", valor = d9[4]),
               list(paso = "k-NN en 170 (k = 4)", valor = r10(4 / (2 * 16 * d9[4]))),
               list(paso = "Suma de los pesos triangulares en 174", valor = sum(NUC$triangular(u9b))),
               list(paso = "Parzen triangular en 174", valor = r10(p9_174)),
               list(paso = sprintf("Estudiantes entre %d y %d cm", min(meseta9), max(meseta9)),
                    valor = sum(X9 >= min(meseta9) & X9 <= max(meseta9)))),
  solucion = list(
    respuestas = list(responde(en9, "¿Qué rango de alturas es el más común",
      sprintf(paste("Entre %d y %d cm: ahí están %d de los 16, y la curva de Parzen no baja de %.4f en",
                    "todo el tramo. Sube apenas de %.4f en 170 a %.4f en 174, una diferencia de %.1f en",
                    "la suma de los pesos, medio estudiante. Con 16 datos eso no basta para señalar un",
                    "pico: la lectura honesta es una meseta entre %d y %d cm."),
              min(meseta9), max(meseta9), sum(X9 >= min(meseta9) & X9 <= max(meseta9)), p9_170,
              p9_170, p9_174, sum(NUC$triangular(u9b)) - sum(NUC$triangular(u9)),
              min(meseta9), max(meseta9)))),
    lectura = "Con pocos datos una densidad se lee por sus mesetas, no por sus picos; y Parzen y k-NN dan cifras del mismo orden en el centro de los datos, por razones distintas."))

# --- E10 · Las sedes de Kennedy -------------------------------------
nnk <- nndist(ken$x, ken$y); wk <- nnwhich(ken$x, ken$y)
rk <- wk[wk] == seq_along(wk)
par_k <- nnk[!rk | seq_along(wk) < wk]
ak <- NA_character_
ucv_k <- withCallingHandlers(bw.ucv(nnk), warning = function(w) { ak <<- conditionMessage(w)
  invokeRestart("muffleWarning") })
par_k0 <- par_k[par_k > 0]
ucv_kp0 <- bw.ucv(par_k0); sj_kp0 <- bw.SJ(par_k0)
e_k <- empates(nnk) / length(nnk)
ucvx_k <- ucv_exacta(nnk, H_MINUSCULO); ucvx_k0 <- ucv_exacta(par_k0, H_MINUSCULO)
ucv20_k <- ucv_exacta(nnk, H_RAZONABLE); ucv20_k0 <- ucv_exacta(par_k0, H_RAZONABLE)
# DENTRO del intervalo en que busca bw.ucv el criterio exacto es casi plano y
# tiene dos mínimos locales; el más bajo NO es el de bw.ucv (lo encontró la
# revisión de la autoevaluación, 2026-10-02).
hmax_k <- 1.144 * sqrt(var(nnk)) * length(nnk)^(-1 / 5)
hh_k <- seq(0.1 * hmax_k, hmax_k, length.out = 400)
uu_k <- sapply(hh_k, function(h) ucv_exacta(nnk, h))
loc_k <- which(diff(sign(diff(uu_k))) > 0) + 1
guarda(length(loc_k) >= 2 && hh_k[which.min(uu_k)] < 10 && any(abs(hh_k[loc_k] - ucv_k) < 2),
       "e10: en el intervalo de bw.ucv hay dos mínimos locales, y el más bajo no es el suyo")
# Cada mínimo de la rejilla, REFINADO con optimize: la rejilla los ponía en
# 5.85 y 30.01, y un estudiante con su propio código encontraría 5.88 y 29.97.
ref_k <- lapply(loc_k, function(i) optimize(function(h) ucv_exacta(nnk, h),
                                            c(hh_k[max(i - 2, 1)], hh_k[min(i + 2, length(hh_k))]), tol = 1e-7))
hs_k <- sapply(ref_k, `[[`, "minimum"); vs_k <- sapply(ref_k, `[[`, "objective")
min_bajo <- hs_k[which.min(vs_k)]
i_otro <- which.min(abs(hs_k - ucv_k)); min_otro <- hs_k[i_otro]
dif_min <- abs(vs_k[i_otro] - min(vs_k))
# Lo que lleva a bw.ucv a los 30 m NO es agrupar las distancias: optimize sobre
# el criterio EXACTO, con su mismo intervalo y tolerancia, cae en el mismo valle
# (segunda revisión, 2026-10-02). Agrupar solo lo mueve unas décimas.
opt_k <- optimize(function(h) ucv_exacta(nnk, h), c(0.1 * hmax_k, hmax_k), tol = 0.1 * 0.1 * hmax_k)$minimum
guarda(abs(opt_k - min_otro) < 0.5 && abs(opt_k - min_bajo) > 10,
       "e10: optimize sobre el criterio exacto cae en el mismo valle que bw.ucv")
en10 <- paste(
  "Toma las 262 sedes de Kennedy (`precalculo/salidas/cap5_kennedy.csv`) y calcula, para",
  "cada una, la distancia a la sede más cercana. ¿Qué fracción de las sedes tiene por vecina",
  "más cercana a una sede que, a su vez, la tiene a ella por vecina más cercana? Calcula",
  "`bw.ucv` con todas las distancias: ¿avisa de algo? Evalúa con tu propio código el criterio",
  "UCV exacto con h = 0.001 m y con h = 20 m, con todas las distancias y con una sola por",
  "pareja sin los ceros, y compara el ancho que da `bw.ucv` en ese segundo caso con el de",
  "`bw.SJ`. Explica por qué un número sin aviso no garantiza que el criterio tenga mínimo.")
E$e10 <- list(
  titulo = "Las sedes de Kennedy", enunciado = en10, modulos = "10 y 12",
  pista = paste("Primero, el umbral del módulo 12: ¿cuántas parejas empatadas por dato hay? Después",
                "compara el criterio con un milímetro y con 20 m: lo que delata el colapso no es su",
                "signo sino que caiga por debajo de su valor en un ancho razonable."),
  pasos = list(list(paso = "Sedes", valor = length(nnk)),
               list(paso = "Distancias iguales a cero", valor = sum(nnk == 0)),
               list(paso = "Fracción recíproca (%)", valor = r10(100 * mean(rk))),
               list(paso = "Parejas empatadas por dato (todas)", valor = r10(e_k)),
               list(paso = "Umbral del núcleo gaussiano", valor = r10(UMBRAL)),
               list(paso = "bw.ucv con todas (m)", valor = r10(ucv_k)),
               list(paso = "UCV exacta con h = 0.001 m, todas", valor = r10(ucvx_k)),
               list(paso = "UCV exacta con h = 20 m, todas", valor = r10(ucv20_k)),
               list(paso = "UCV exacta con h = 0.001 m, una por pareja sin ceros", valor = r10(ucvx_k0)),
               list(paso = "UCV exacta con h = 20 m, una por pareja sin ceros", valor = r10(ucv20_k0)),
               list(paso = "bw.ucv con una por pareja y sin ceros (m)", valor = r10(ucv_kp0)),
               list(paso = "bw.SJ con una por pareja y sin ceros (m)", valor = r10(sj_kp0)),
               list(paso = "Intervalo en que busca bw.ucv, desde (m)", valor = r10(0.1 * hmax_k)),
               list(paso = "Intervalo en que busca bw.ucv, hasta (m)", valor = r10(hmax_k)),
               list(paso = "Mínimo local más bajo del criterio exacto en ese intervalo (m)", valor = r10(min_bajo)),
               list(paso = "Mínimo local junto al de bw.ucv (m)", valor = r10(min_otro)),
               list(paso = "optimize sobre el criterio exacto, como bw.ucv (m)", valor = r10(opt_k))),
  solucion = list(
    respuestas = list(),
    lectura = "La teoría de la densidad en una dimensión supone datos independientes; una lista de distancias al vecino no lo es nunca."))
E$e10$solucion$respuestas <- list(
  responde(en10, "¿Qué fracción de las sedes tiene por vecina",
    sprintf(paste("El %.1f %%, del orden del %.1f %% que da el azar en el plano: las parejas",
                  "son geometría, no agrupamiento."), 100 * mean(rk), 100 * c_recip)),
  responde(en10, "¿avisa de algo?",
    sprintf(paste("No: devuelve %.2f m sin ningún aviso, una cifra que parece razonable."),
            ucv_k)),
  responde(en10, "compara el ancho que da `bw.ucv` en ese segundo caso con el de `bw.SJ`",
    sprintf(paste("Con todas las distancias el criterio exacto vale %.4f con h = 0.001 m y %.5f con",
                  "h = 20 m: con un milímetro cae muy por debajo, y se hunde más cuanto más pequeño es",
                  "h. Sin parejas ni ceros vale %.4f con un milímetro, por encima de los %.5f de 20 m,",
                  "y bw.ucv da %.2f m, junto a los %.2f m de bw.SJ."),
            ucvx_k, ucv20_k, ucvx_k0, ucv20_k0, ucv_kp0, sj_kp0)),
  responde(en10, "Explica por qué un número sin aviso no garantiza que el criterio tenga mínimo",
    sprintf(paste("Porque bw.ucv no mira el criterio entero: lo busca en un intervalo acotado y",
                  "con las distancias agrupadas, y ahí encuentra un mínimo local. Las parejas",
                  "empatadas son %.3f por dato, por encima del umbral %.4f a partir del cual la",
                  "UCV se va a menos infinito cuando h tiende a cero: el ínfimo está en h = 0 y",
                  "cualquier número finito es un artefacto de la búsqueda. Y ni siquiera es el mínimo",
                  "del criterio exacto dentro del intervalo: entre %.2f y %.2f m el criterio es casi",
                  "plano, con dos mínimos locales, hacia %.1f y %.1f m, que difieren en %.6f; el más",
                  "bajo es el primero. bw.ucv busca con optimize, que estrecha el intervalo desde dentro",
                  "y se queda con el valle en que cae: aplicado al criterio exacto, con el mismo",
                  "intervalo y la misma tolerancia, también devuelve %.2f m. Agrupar las distancias solo",
                  "lo mueve a %.2f m."),
            e_k, UMBRAL, 0.1 * hmax_k, hmax_k, min_bajo, min_otro, dif_min, opt_k, ucv_k)))
guarda(is.na(ak) && e_k > UMBRAL && ucvx_k < ucv20_k && ucvx_k0 > ucv20_k0 && abs(ucv_kp0 / sj_kp0 - 1) < 0.25,
       "e10: Kennedy da un bw.ucv sin aviso con un criterio sin mínimo, y sin empates vuelve junto a SJ")

for (k in names(E)) {
  f <- sin_contestar(E[[k]])
  if (length(f)) stop("ejercicio ", k, " deja demandas sin contestar: ", paste(f, collapse = " | "))
  for (r in E[[k]]$solucion$respuestas)
    if (!nzchar(r$respuesta)) stop("ejercicio ", k, ": una respuesta quedó vacía")
}
E$meta <- list(apendice = "A", semilla = SEMILLA, n_ejercicios = 10L,
               generado = format(Sys.Date()))

# =====================================================================
# LO QUE SE ESCRIBE
# =====================================================================
message("N. escribiendo")
D$meta <- list(apendice = "A", semilla = SEMILLA, generado = as.character(Sys.Date()),
               anclas = N_ANCLAS, guardas = N_GUARDAS,
               fuente = "JMS_Densidades.Rmd (Estadística no paramétrica · Densidades)")
geo_escribe(D, file.path(SALIDAS, "apendicea_datos.json"), presupuesto_kb = 400)
txt <- jsonlite::toJSON(E, auto_unbox = TRUE, digits = 10, null = "null", na = "null")
if (grepl('"NA"', txt, fixed = TRUE)) stop("apendicea_soluciones.json: hay NA escritos como \"NA\"")
writeLines(txt, file.path(SALIDAS, "apendicea_soluciones.json"), useBytes = TRUE)

# Los CSV que leen las pestañas de Python. R y numpy no comparten generador
# aleatorio, así que Python no puede simular la misma muestra: la lee.
write.csv(data.frame(tiempo = r10(tiempos)), file.path(SALIDAS, "apendicea_cafeteria.csv"),
          row.names = FALSE)
write.csv(faithful, file.path(SALIDAS, "apendicea_faithful.csv"), row.names = FALSE)
write.csv(data.frame(valor = r10(mez)), file.path(SALIDAS, "apendicea_mezcla.csv"),
          row.names = FALSE)

message(sprintf("\nLISTO. %d anclas y %d guardas, ninguna rota.", N_ANCLAS, N_GUARDAS))
message(sprintf("  m2: h del origen %.2f (modas %d -> %d) · m10: ucv %.4f SJ %.4f bcv %.4f",
                H_ORIGEN, min(fila_o), max(fila_o), sel[["ucv"]], sel[["SJ"]], sel[["bcv"]]))
message(sprintf("  m11: h* %.4f · gana ucv %.1f %% · cola ucv %.1f %% · m12: ucv %.2f / %.2f, SJ %.2f",
                h_star, pct_gana[SEL == "ucv"], 100 * cola[["ucv"]], s_todas$ucv, s_par$ucv, s_par$sj))
