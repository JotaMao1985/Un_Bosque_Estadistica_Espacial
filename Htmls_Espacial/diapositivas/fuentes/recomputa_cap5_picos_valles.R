# =====================================================================
# recomputa_cap5_picos_valles.R — recómputos de «al subir σ, los picos bajan y los valles se llenan»
# (sesión 1: la ilustración de juguete de la lámina 8 y la animación en 3D de la lámina 9).
#
# La lámina 9 decía, en sus notas, que al subir σ «baja el mapa entero»: es media verdad. La superficie baja donde
# estaba alta y SUBE donde estaba baja (cada punto reparte la misma masa en más terreno), y con el disco el máximo
# hasta puede subir, a saltos. Aquí se mide con los MISMOS datos que las diapositivas, que se LEEN, no se copian:
#   · la ilustración: las seis posiciones, los dos σ y la rejilla de u salen de `genera_figuras_s1.R`;
#   · la animación: los diecinueve puntos, el rango de σ y su paso salen de `precalculo/nucleo3d/nucleo3d.js`
#     (sin corrección de borde, como la escena de conteo), con los cuatro núcleos de spatstat.
#
# Escribe `recomputo_cap5_picos_valles.json` (`verifica_cifras_cap5.py` junta todos los `recomputo_cap5*.json`).
#
# Desde la raíz del repo:
#   precalculo/rscript.sh Htmls_Espacial/diapositivas/fuentes/recomputa_cap5_picos_valles.R
# =====================================================================
suppressPackageStartupMessages({ library(spatstat); library(jsonlite) })
options(scipen = 999, digits = 10, warn = 1)
MOTOR   <- "precalculo/nucleo3d/nucleo3d.js"
FIGURAS <- "Htmls_Espacial/diapositivas/fuentes/recursos/cap5/genera_figuras_s1.R"
SALIDA  <- "Htmls_Espacial/diapositivas/fuentes/recomputo_cap5_picos_valles.json"
NPIX    <- as.integer(Sys.getenv("NPIX_PRUEBA", "1000"))     # píxeles por lado en la escena de conteo
quieto  <- function(expr) suppressMessages(suppressWarnings(expr))
lee     <- function(f) paste(readLines(f, encoding = "UTF-8", warn = FALSE), collapse = "\n")
saca    <- function(src, rx) {
  m <- regmatches(src, regexec(rx, src, perl = TRUE))[[1]]
  if (length(m) < 2) stop("no encuentro: ", rx)
  m[2:length(m)]
}
numeros <- function(txt) as.numeric(regmatches(txt, gregexpr("-?[0-9]+(?:\\.[0-9]+)?", txt, perl = TRUE))[[1]])
# «el 10 % más alto» y «la mitad más baja» por rango (con empates, como los ceros del disco, no se vacían)
alto_decil <- function(v) rank(-v, ties.method = "first") <= 0.1 * length(v)
mitad_baja <- function(v) rank(v, ties.method = "first") <= 0.5 * length(v)

OUT <- list()

# ---------------------------------------------------------------------
# 1 · La ilustración de juguete (lámina 8): seis posiciones en una dimensión, núcleo gaussiano, dos σ
# ---------------------------------------------------------------------
fig  <- lee(FIGURAS)
x_j  <- numeros(saca(fig, "x_j <- c\\(([^)]*)\\)"))
sg_j <- numeros(saca(fig, "(?s)abre_z\\(\"s1-nucleo-juguete\".*?for \\(s in c\\(([^)]*)\\)\\) \\{"))
xs_args <- numeros(saca(fig, "xs <- seq\\(([^)]*)\\)"))                  # `seq(0, 10, length.out = 800)`: desde, hasta, longitud
xs   <- seq(xs_args[1], xs_args[2], length.out = xs_args[3])
stopifnot(length(x_j) == 6, length(sg_j) == 2, sg_j[1] < sg_j[2], length(xs) == 800)
suma  <- function(u, s) Reduce(`+`, lapply(x_j, function(x0) dnorm(u, x0, s)))     # la suma de lomas, en un punto o en un vector
est   <- suma(xs, sg_j[1]); anc <- suma(xs, sg_j[2])
o     <- sort(x_j); hueco <- which.max(diff(o)); u_valle <- (o[hueco] + o[hueco + 1]) / 2   # punto medio del hueco más ancho
OUT$juguete <- list(
  x_j = x_j, sigmas = sg_j, u_valle = u_valle,
  max_estrecho = max(est), max_ancho = max(anc),
  valle_estrecho = suma(u_valle, sg_j[1]), valle_ancho = suma(u_valle, sg_j[2]),
  alta_baja = mean(anc[alto_decil(est)] < est[alto_decil(est)]),         # el 10 % más alto con σ estrecho: ¿baja con σ ancho?
  baja_sube = mean(anc[mitad_baja(est)] > est[mitad_baja(est)]))         # la mitad más baja con σ estrecho: ¿sube con σ ancho?

# ---------------------------------------------------------------------
# 2 · La animación (lámina 9): diecinueve puntos, σ de `min` a `max` en pasos del deslizador, sin corregir el borde
# ---------------------------------------------------------------------
mot    <- lee(MOTOR)
V      <- as.numeric(saca(mot, "const V = ([0-9.]+);"))
patron <- matrix(numeros(saca(mot, "(?s)const PATRON = \\[(.*?)\\];")), ncol = 2, byrow = TRUE)
SG     <- setNames(as.numeric(saca(mot, "const SIGMA = \\{ min: ([0-9.]+), max: ([0-9.]+), ini: ([0-9.]+) \\};")), c("min", "max", "ini"))
# el deslizador de σ: el motor del PR #8 lo escribe con `${SIGMA.min}` y el del #9 (varias escenas), con `${E.sigma.min}`
paso   <- as.numeric(saca(mot, "type=\"range\" min=\"\\$\\{(?:E\\.sigma|SIGMA)\\.min\\}\" max=\"\\$\\{(?:E\\.sigma|SIGMA)\\.max\\}\" step=\"([0-9.]+)\""))
stopifnot(V == 5, nrow(patron) == 19)
W   <- owin(c(-V, V), c(-V, V)); P <- ppp(patron[, 1], patron[, 2], window = W)
sig <- round(seq(SG[["min"]], SG[["max"]], by = paso), 4)

nucleos <- c("gaussian", "epanechnikov", "quartic", "disc")
por_nucleo <- lapply(setNames(nucleos, nucleos), function(k) {
  mx <- numeric(length(sig)); sube_paso <- numeric(length(sig) - 1); v1 <- NULL; prev <- NULL
  for (j in seq_along(sig)) {
    v <- as.vector(quieto(density(P, sigma = sig[j], kernel = k, edge = FALSE, dimyx = c(NPIX, NPIX)))$v)
    mx[j] <- max(v)
    if (!is.null(prev)) sube_paso[j - 1] <- mean(v > prev + 1e-12)       # fracción de la ventana que sube en este paso
    if (j == 1) v1 <- v
    prev <- v
  }
  salto <- which(diff(mx) > 1e-9)                                         # pasos en que el máximo SUBE
  out <- list(max_sigma_min = mx[1], max_sigma_max = mx[length(mx)], pasos_sube = length(salto),
              frac_sube_total = mean(prev > v1 + 1e-12),                  # de σ mínimo a σ máximo
              alta_baja = mean(prev[alto_decil(v1)] < v1[alto_decil(v1)]),
              baja_sube = mean(prev[mitad_baja(v1)] > v1[mitad_baja(v1)]),
              frac_sube_paso_min = min(sube_paso), frac_sube_paso_mediana = median(sube_paso))
  if (length(salto)) out$primer_salto <- list(de = sig[salto[1]], a = sig[salto[1] + 1], antes = mx[salto[1]], despues = mx[salto[1] + 1])
  if (k == "disc") {
    # la densidad del disco es (puntos dentro del círculo) / (π h²), con h = 2σ: el máximo es un conteo entre un área
    out$cuenta_max <- round(mx * pi * (2 * sig)^2)
    out$salto_con_mas_puntos <- length(salto) > 0 && all(out$cuenta_max[salto + 1] > out$cuenta_max[salto])
  }
  out
})
OUT$conteo <- list(n = nrow(patron), V = V, sigma = as.list(SG), paso = paso, n_valores = length(sig), n_pasos = length(sig) - 1,
                   por_nucleo = por_nucleo)

OUT$meta <- list(spatstat = as.character(packageVersion("spatstat")), R = R.version.string, npix = NPIX, fecha = format(Sys.time(), "%Y-%m-%d"),
                 nota = "x_j y σ de la ilustración leídos de genera_figuras_s1.R; PATRON, σ y su paso leídos de precalculo/nucleo3d/nucleo3d.js; density() de spatstat sobre npix × npix, sin corrección de borde")
write_json(list(picos_valles = OUT, meta = OUT$meta), SALIDA, auto_unbox = TRUE, digits = 12, pretty = TRUE)
cat("escrito", SALIDA, "\n")
str(OUT$juguete)
for (k in nucleos) {
  z <- por_nucleo[[k]]
  cat(sprintf("[%s] máx %.4f → %.4f; pasos en que sube: %d de %d; sube de σmín a σmáx en %.3f de la ventana; décil alto baja %.3f, mitad baja sube %.3f\n",
              k, z$max_sigma_min, z$max_sigma_max, z$pasos_sube, length(sig) - 1, z$frac_sube_total, z$alta_baja, z$baja_sube))
}
cat("disco: conteo máximo por σ =", paste(por_nucleo$disc$cuenta_max, collapse = " "), "\n")
cat("disco: cada salto trae un punto más al círculo:", por_nucleo$disc$salto_con_mas_puntos, "\n")
