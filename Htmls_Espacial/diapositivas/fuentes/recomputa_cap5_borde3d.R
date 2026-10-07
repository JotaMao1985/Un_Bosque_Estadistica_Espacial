# =====================================================================
# recomputa_cap5_borde3d.R — recómputos de la lámina «En 3D: lo que se escapa por el borde»
# (sesión 1, módulo 4).
#
# La animación (`precalculo/nucleo3d/nucleo3d.js`, escena «borde») calcula en el navegador lo que las
# notas de la lámina dicen: cuánto queda dentro de la ventana de la loma de una sede (e) y el volumen
# de las tres superficies. Aquí se vuelve a calcular con `density()` de spatstat sobre los MISMOS
# diecinueve puntos, que se LEEN del motor (no se copian): si el patrón o σ cambian en el motor, este
# archivo lo sigue y el verificador de cifras lo nota.
#
# Escribe `recomputo_cap5_borde3d.json` (`verifica_cifras_cap5.py` junta todos los `recomputo_cap5*.json`).
#
# Desde la raíz del repo:
#   precalculo/rscript.sh Htmls_Espacial/diapositivas/fuentes/recomputa_cap5_borde3d.R
# =====================================================================
suppressPackageStartupMessages({ library(spatstat); library(jsonlite) })
options(scipen = 999, digits = 10, warn = 1)
MOTOR  <- "precalculo/nucleo3d/nucleo3d.js"
SALIDA <- "Htmls_Espacial/diapositivas/fuentes/recomputo_cap5_borde3d.json"
NPIX   <- as.integer(Sys.getenv("NPIX_PRUEBA", "1000"))     # píxeles por lado: 1000 → 0.01 de lado
quieto <- function(expr) suppressMessages(suppressWarnings(expr))

# ---------------------------------------------------------------------
# 1 · Lo que el motor fija: la ventana, los puntos, σ, el guion y el margen (leídos de `nucleo3d.js`)
# ---------------------------------------------------------------------
src <- paste(readLines(MOTOR, encoding = "UTF-8", warn = FALSE), collapse = "\n")
saca <- function(rx) {
  m <- regmatches(src, regexec(rx, src, perl = TRUE))[[1]]
  if (length(m) < 2) stop("no encuentro en el motor: ", rx)
  m[2]
}
numeros <- function(txt) as.numeric(regmatches(txt, gregexpr("-?[0-9]+(?:\\.[0-9]+)?", txt, perl = TRUE))[[1]])

V <- as.numeric(saca("const V = ([0-9.]+);"))
patron <- matrix(numeros(saca("(?s)const PATRON = \\[(.*?)\\];")), ncol = 2, byrow = TRUE)
colnames(patron) <- c("x", "y")
n <- nrow(patron)
# σ de la escena «borde»: { min, max, ini, tope }, y hasta dónde se puede llevar una sede hacia el borde
sg_txt <- regmatches(src, regexec("(?s)id: 'borde',.*?sigma: \\{ min: ([0-9.]+), max: ([0-9.]+), ini: ([0-9.]+), tope: ([0-9.]+) \\}", src, perl = TRUE))[[1]]
SG <- setNames(as.numeric(sg_txt[2:5]), c("min", "max", "ini", "tope"))
margen <- as.numeric(saca("(?s)id: 'borde',.*?margen: ([0-9.]+)"))
# el guion de «Reproducir» de la escena «borde»: las duraciones (s) de sus cuatro pasos
guion_txt <- saca("(?s)const GUION_BORDE = \\[(.*?)\\n    \\];")
guion <- as.numeric(regmatches(guion_txt, gregexpr("(?<=dur: )[0-9]+", guion_txt, perl = TRUE))[[1]])
stopifnot(n == 19, length(guion) == 4, V == 5)

W <- owin(c(-V, V), c(-V, V))
P <- ppp(patron[, "x"], patron[, "y"], window = W)
s <- SG[["ini"]]                                           # el σ con el que abre la escena

OUT <- list()
OUT$motor <- list(n = n, V = V, sigma = as.list(SG), margen = margen, guion_por_paso_s = guion, guion_s = sum(guion),
                  foco0 = list(i = 1, x = patron[1, "x"], y = patron[1, "y"],
                               dist_borde = V - abs(patron[1, "x"])))

# ---------------------------------------------------------------------
# 2 · e(x): la fracción de un núcleo gaussiano centrado en x que cae dentro de la ventana (forma cerrada)
# ---------------------------------------------------------------------
e_gauss <- function(x, y, s) (pnorm((V - x) / s) - pnorm((-V - x) / s)) * (pnorm((V - y) / s) - pnorm((-V - y) / s))
e_i <- e_gauss(patron[, "x"], patron[, "y"], s)

integra <- function(p, s, kernel = "gaussian", N = NPIX) {
  c(sin     = integral(quieto(density(p, sigma = s, kernel = kernel, edge = FALSE, dimyx = c(N, N)))),
    defecto = integral(quieto(density(p, sigma = s, kernel = kernel, dimyx = c(N, N)))),
    diggle  = integral(quieto(density(p, sigma = s, kernel = kernel, diggle = TRUE, dimyx = c(N, N)))))
}

# ---------------------------------------------------------------------
# 3 · Lo que dice la pantalla al abrir (paso 1: sede n.º 1 en foco, σ = 1.2, núcleo gaussiano)
# ---------------------------------------------------------------------
OUT$apertura <- list(
  sigma = s,
  e_foco = e_i[1], dentro_pct = round(100 * e_i[1]), fuera_pct = 100 - round(100 * e_i[1]))

# ---------------------------------------------------------------------
# 4 · Los tres volúmenes con las diecinueve sedes (pasos 2 a 4) y lo que aporta la sede en foco
# ---------------------------------------------------------------------
v <- integra(P, s)
OUT$volumen <- list(sin_analitico = sum(e_i), sin = v[["sin"]], defecto = v[["defecto"]], diggle = v[["diggle"]],
                    exceso_defecto_pct = 100 * (v[["defecto"]] - n) / n, fuga_sin_pct = 100 * (v[["sin"]] - n) / n)
a1 <- integra(ppp(patron[1, "x"], patron[1, "y"], window = W), s)
OUT$foco_aporta <- list(sin = a1[["sin"]], defecto = a1[["defecto"]], diggle = a1[["diggle"]])

# ---------------------------------------------------------------------
# 4b · «Con Diggle el volumen vuelve a ser n, con cualquier σ y cualquier núcleo»: los cuatro núcleos × σ del deslizador
#      (los dos extremos y el de partida). Con el disco la rejilla de píxeles da algo de error: de ahí la tolerancia del verificador.
# ---------------------------------------------------------------------
sigmas <- c(SG[["min"]], SG[["ini"]], SG[["max"]])
dig <- sapply(c("gaussian", "epanechnikov", "quartic", "disc"), function(k) sapply(sigmas, function(sg_) {
  integral(quieto(density(P, sigma = sg_, kernel = k, diggle = TRUE, dimyx = c(max(400, NPIX %/% 2), max(400, NPIX %/% 2)))))
}))
rownames(dig) <- paste0("sigma_", sigmas)
OUT$diggle_todos <- list(sigmas = sigmas, volumen = as.data.frame(t(dig)), min = min(dig), max = max(dig))

# ---------------------------------------------------------------------
# 5 · «Una sede pegada al borde aporta menos de 1; una a uno y medio o dos σ de él, más de 1»
#     Una sede sola, en medio del lado izquierdo, a distancia d del borde; con la corrección por defecto.
#     Distancias: el margen mínimo que deja el visor (0.25), la que separa del borde a la sede n.º 1 (0.7: aquí la sede
#     va en medio del lado, no donde está la n.º 1), 1.5σ y 2σ.
# ---------------------------------------------------------------------
dist <- c(margen, V - abs(patron[1, "x"]), 1.5 * s, 2 * s)
nucleos <- c("gaussian", "epanechnikov", "quartic", "disc")
sola <- lapply(nucleos, function(k) {
  r <- lapply(dist, function(d) { a <- integra(ppp(-V + d, 0, window = W), s, kernel = k, N = max(400, NPIX %/% 2)); a[["defecto"]] })
  setNames(as.list(unlist(r)), c("margen", "d_sede1", "uno_y_medio_sigma", "dos_sigma"))
})
names(sola) <- nucleos
OUT$sola <- list(sigma = s, distancias = dist, por_nucleo = sola,
                 menor_a_uno_pegada = all(sapply(sola, function(z) z$margen < 1 && z$d_sede1 < 1)),
                 mayor_a_uno_lejos = all(sapply(sola, function(z) z$uno_y_medio_sigma > 1 && z$dos_sigma > 1)),
                 min_lejos = min(sapply(sola, function(z) min(z$uno_y_medio_sigma, z$dos_sigma))),
                 max_pegada = max(sapply(sola, function(z) max(z$margen, z$d_sede1))))

# ---------------------------------------------------------------------
OUT$meta <- list(spatstat = as.character(packageVersion("spatstat")), R = R.version.string, npix = NPIX,
                 fecha = format(Sys.time(), "%Y-%m-%d"),
                 nota = "n, ventana, σ, guion y margen leídos de precalculo/nucleo3d/nucleo3d.js; density() de spatstat sobre una rejilla de npix × npix")
write_json(list(borde3d = OUT, meta = OUT$meta), SALIDA, auto_unbox = TRUE, digits = 12, pretty = TRUE)
cat("escrito", SALIDA, "\n")
print(unlist(OUT[c("volumen", "foco_aporta", "apertura")]))
cat("sola (por defecto):\n"); print(do.call(rbind, lapply(sola, unlist)))
