# potencia.R — La tabla de potencia del Moran que publica el módulo 2 de la guía.
#
# Rejilla cuadrada con vecindad reina, W estandarizada por filas, y un SAR
# y = (I − ρW)⁻¹ ε con ε normal. Para cada (N, ρ), la fracción de las R réplicas
# en que moran.mc() con nsim permutaciones rechaza al 5 % (unilateral, «greater»).
# Con ρ = 0 es el tamaño de la prueba, y tiene que salir cerca de 0,05.
#
#   Rscript proyecto/potencia.R      → escribe proyecto/potencia.json (unos 3 min)
#
# proyecto/datos.py lee el JSON: la guía no lleva ninguna de estas cifras a mano.
suppressMessages(library(spdep))
library(jsonlite)

LADOS <- c(5, 6, 7, 8, 10)          # N = 25, 36, 49, 64, 100
RHOS  <- c(0, 0.3, 0.5)
R     <- 2000
NSIM  <- 499
ALFA  <- 0.05
SEMILLA <- 20929

set.seed(SEMILLA)
filas <- list()
for (lado in LADOS) {
  lw <- nb2listw(cell2nb(lado, lado, type = "queen"), style = "W")
  n  <- lado^2
  for (rho in RHOS) {
    A <- solve(diag(n) - rho * listw2mat(lw))
    rech <- replicate(R, moran.mc(as.vector(A %*% rnorm(n)), lw, NSIM,
                                  alternative = "greater")$p.value <= ALFA)
    filas[[length(filas) + 1]] <- list(N = n, rho = rho, potencia = round(mean(rech), 3))
    cat(sprintf("N = %3d  rho = %.1f  potencia = %.3f\n", n, rho, mean(rech)))
  }
}

salida <- list(
  que = "Potencia de moran.mc (unilateral, 5 %) frente a un SAR en rejilla reina con W por filas",
  replicas = R, nsim = NSIM, alfa = ALFA, semilla = SEMILLA,
  r = paste(R.version$major, R.version$minor, sep = "."),
  spdep = as.character(packageVersion("spdep")),
  filas = filas)
write_json(salida, "proyecto/potencia.json",
           auto_unbox = TRUE, pretty = TRUE, digits = NA)
