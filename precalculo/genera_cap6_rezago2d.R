# =====================================================================
# genera_cap6_rezago2d.R — las cifras de referencia de la animación del rezago
#
#   Capítulo 6, módulo 10 · Material de Estadística Espacial 2026-II (20929).
#
# QUÉ PRODUCE
#   precalculo/salidas/cap6_rezago2d.json           la serie entera, para las pruebas
#   precalculo/salidas/cap6_rezago2d_resumen.json   los 8 números que cita la prosa del módulo 10
#
# POR QUÉ ES UN SCRIPT APARTE Y NO UN BLOQUE DE `genera_cap6.R`
#   La animación (`anim2d/rezago2d.js`) calcula W^k y en el navegador, y esa
#   aritmética es de las que no ve ningún auditor de prosa. Se prueba contra
#   ESTAS cifras, que salen de `spdep` (poly2nb, nb2listw, lag.listw), y no
#   de la misma aritmética en otro lenguaje. Regenerar `genera_cap6.R` entero
#   para añadirlas movería la marca de tiempo y cada cifra del capítulo sin
#   necesidad: este archivo es determinista, no usa azar y no toca nada más.
#
# QUÉ SE PUBLICA, y para qué
#   · `y`            CRIME de los 49 barrios de Columbus, con todos sus decimales:
#                    es lo único que la página necesita traer; el resto lo calcula.
#   · `vecinos`      los vecinos de cada barrio (base 1) que ve `spdep`, para
#                    comprobar que las aristas del mapa del capítulo son esas.
#   · `serie`        media, desviación típica (ddof = 1), correlación con y y
#                    pendiente de W^k y sobre y, para k = 0…70: el deslizador llega a las
#                    66 aplicaciones que la prosa dice que hacen falta con la reina
#                    para dejar la desviación en el 5 % de la de y (56 con la torre).
#   · `vectores`     W^k y entero en unos pocos k, para comparar barrio a barrio.
#   · `limite`       a dónde va W^k y: NO a la media de y, sino a la media
#                    ponderada por el grado, Σ dᵢ yᵢ / Σ dᵢ (la W por filas es
#                    una cadena de Markov cuya distribución estacionaria es
#                    proporcional al grado).
#   · `lambda2`      el segundo valor propio en módulo, que manda la velocidad
#                    del aplanado, y `k_5pct`, las aplicaciones que hacen falta
#                    para dejar la desviación en el 5 % de la de y.
#   · `moran`        el I de Moran del capítulo 7, que con W por filas es la
#                    PENDIENTE de Wy sobre y = cor · sd(Wy)/sd(y), no la cor.
#
# Ejecutar con el envoltorio, desde la carpeta `Estadistica espacial/`:
#     sh precalculo/rscript.sh precalculo/genera_cap6_rezago2d.R
# =====================================================================

suppressPackageStartupMessages({
  library(sf)
  library(spdep)
  library(jsonlite)
})

AQUI <- "precalculo"
source(file.path(AQUI, "utf8.R"))

SALIDAS <- file.path(AQUI, "salidas")
K_MAX <- 70L                          # lo que el deslizador de la animación recorre (pasa del k_5pct de las dos vecindades)
K_VECTORES <- c(1L, 2L, 5L, 10L, 30L, 70L)  # los k de los que se publica el vector entero
K_LARGO <- 2000L                      # para medir el límite: 0.971^2000 ≈ 1e-26

ancla <- function(calculado, esperado, que, tol = 1e-9) {
  d <- max(abs(as.numeric(calculado) - as.numeric(esperado)))
  if (!is.finite(d) || d > tol)
    stop(sprintf("ANCLA ROTA · %s: diferencia %.3e (tolerancia %.1e)", que, d, tol))
  invisible(TRUE)
}

col <- st_read(system.file("shapes/columbus.gpkg", package = "spData"), quiet = TRUE)
y <- as.numeric(col$CRIME)
stopifnot(length(y) == 49L)
# Lo que el capítulo ya publica de CRIME (módulo 1): si no cuadra, este no es
# el mismo dato.
ancla(round(mean(y), 4), 35.1288, "media de CRIME", tol = 1e-9)
ancla(round(sd(y), 4), 16.7321, "desviación de CRIME", tol = 1e-9)

un_criterio <- function(nb) {
  lw <- nb2listw(nb, style = "W")
  W <- nb2mat(nb, style = "W")
  d <- as.integer(card(nb))
  stopifnot(all(d > 0L))                       # sin islas: la W por filas existe en toda fila

  v <- y
  serie <- vector("list", K_MAX + 1L)
  vectores <- list()
  for (k in 0:K_MAX) {
    if (k > 0L) {
      v_prev <- v
      v <- as.numeric(lag.listw(lw, v))
      # lag.listw y el producto matricial tienen que ser lo mismo.
      ancla(v, as.numeric(W %*% v_prev), sprintf("lag.listw contra W %%*%% v, k = %d", k), tol = 1e-10)
    }
    serie[[k + 1L]] <- list(
      k = k, media = mean(v), sd = sd(v),
      cor = cor(y, v), pendiente = cov(y, v) / var(y))
    if (k %in% K_VECTORES) vectores[[as.character(k)]] <- I(v)
  }

  # El límite se MIDE iterando mucho, y se compara con la fórmula cerrada.
  w_largo <- y
  for (k in seq_len(K_LARGO)) w_largo <- as.numeric(lag.listw(lw, w_largo))
  limite <- sum(d * y) / sum(d)
  ancla(w_largo, rep(limite, 49L), "W^k y converge a la media ponderada por grado", tol = 1e-9)

  # Segundo valor propio en módulo, y las aplicaciones que bajan la sd al 5 %.
  lam <- sort(Mod(eigen(W, only.values = TRUE)$values), decreasing = TRUE)
  ancla(lam[1], 1, "el mayor valor propio de W vale 1", tol = 1e-9)
  v <- y
  k5 <- NA_integer_
  for (k in 1:K_LARGO) {
    v <- as.numeric(lag.listw(lw, v))
    if (sd(v) <= 0.05 * sd(y)) { k5 <- k; break }
  }
  # La prosa cita k5, y el lector tiene que poder llevar el deslizador hasta ahí.
  if (is.na(k5) || k5 > K_MAX)
    stop(sprintf("el deslizador llega a k = %d y la desviación no baja al 5 %% hasta k = %s", K_MAX, k5))

  list(
    n_aristas = as.integer(sum(d) / 2L),
    grados = I(d),
    vecinos = lapply(seq_along(nb), function(i) I(as.integer(nb[[i]]))),
    limite = limite,
    media_simple = mean(y),
    lambda2 = lam[2],
    k_5pct = k5,
    serie = serie,
    vectores = vectores)
}

reina <- poly2nb(col, queen = TRUE)
torre <- poly2nb(col, queen = FALSE)
out <- list(
  meta = list(capitulo = 6L, modulo = 10L, k_max = K_MAX, k_vectores = I(K_VECTORES),
              fuente = "spData::columbus.gpkg, spdep poly2nb / nb2listw / lag.listw"),
  y = list(crime = I(y), media = mean(y), sd = sd(y), min = min(y), max = max(y)),
  vecindades = list(reina = un_criterio(reina), torre = un_criterio(torre)))

# El I de Moran del capítulo 7, con la W de la reina. Con W por filas es la
# pendiente de Wy sobre y (cor · sd(Wy)/sd(y)); se comprueba contra `moran()`.
lw1 <- nb2listw(reina, style = "W")
I_moran <- moran(y, lw1, n = 49L, S0 = Szero(lw1))$I
s1 <- out$vecindades$reina$serie[[2]]
ancla(I_moran, s1$pendiente, "I de Moran es la pendiente de Wy sobre y", tol = 1e-12)
wy1 <- as.numeric(lag.listw(lw1, y))
ancla(s1$cor * sd(wy1) / sd(y), I_moran, "I = cor · sd(Wy)/sd(y)", tol = 1e-12)
out$moran <- list(I = I_moran, cor = s1$cor, razon_sd = sd(wy1) / sd(y))

escribe <- function(obj, nombre) {
  txt <- toJSON(obj, auto_unbox = TRUE, digits = 15, null = "null", na = "null")
  if (grepl('"NA"', txt, fixed = TRUE)) stop("hay NA escritos como la cadena \"NA\"")
  destino <- file.path(SALIDAS, nombre)
  writeLines(txt, destino, useBytes = TRUE)
  message(sprintf("  %s: %.1f KB", nombre, file.size(destino) / 1024))
}
escribe(out, "cap6_rezago2d.json")

# EL RESUMEN QUE CITA LA PROSA, aparte a propósito. El auditor de cifras (`audita_texto_cap6.py`) indexa TODO número
# de los JSON que se le dan, y la serie de arriba trae miles: con ellos, un entero corto inyectado como defecto
# («8 931») cae dentro del índice por azar y el auditor deja de verlo. Se le da solo lo que el módulo 10 cita.
escribe(list(
  y_media = out$y$media,
  limite_reina = out$vecindades$reina$limite,
  limite_torre = out$vecindades$torre$limite,
  lambda2_reina = out$vecindades$reina$lambda2,
  k_5pct_reina = out$vecindades$reina$k_5pct,
  moran_I = out$moran$I,
  moran_cor = out$moran$cor,
  moran_razon_sd = out$moran$razon_sd), "cap6_rezago2d_resumen.json")
