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

# =====================================================================
# LO QUE AÑADE EL CAPÍTULO 5 (T3.4)
#
# Tres convenciones que se midieron el 2026-08-28 (anexo A.21 del plan) y
# que, sueltas, se vuelven a equivocar. Van aquí por el mismo motivo por
# el que `ppp_rebaraja()` vino en T3.1: las necesita más de un guion y
# cada una encierra algo que ya salió mal o que sale mal solo.
# =====================================================================

#' Una familia de superficies KDE del MISMO patrón, con UNA sola regla
#'
#' Es el deslizador de sigma del módulo 1, y la decisión 4 de la Fase 3
#' vive dentro de esta función en forma de tres guardas.
#'
#' POR QUÉ NO BASTA CON LLAMAR A `density()` SIETE VECES.
#'
#'  1. LA ESCALA. `geo_rejilla()` normaliza cada superficie contra su
#'     propio máximo, que es lo correcto para un mapa suelto y es lo que
#'     publican los diez rásteres del capítulo 1. Para una FAMILIA es
#'     justo lo contrario de lo que hay que hacer: lo que el módulo 2
#'     enseña es que al abrir el núcleo la superficie se APLANA —la
#'     intensidad máxima cae de 63,8 por km2 con sigma = 100 m a 9,4 con
#'     sigma = 1600 m— y con siete escalas distintas las siete salen
#'     igual de picudas. El mapa contradiría al texto con la tinta más
#'     convincente de las dos. Por eso se devuelve `escala`, y por eso
#'     `geo_rejilla()` estrenó el argumento del mismo nombre.
#'
#'  2. LA REJILLA. Las siete superficies tienen que ir sobre la MISMA
#'     rejilla o el deslizador da saltos que no son del dato. Se calcula
#'     una vez y se impone a todas.
#'
#'  3. LA CELDA CONTRA EL SIGMA MÁS ESTRECHO, que es la decisión 4
#'     entera. Una celda más ancha que el núcleo no dibuja el núcleo:
#'     dibuja la rejilla. Sobre la ciudad completa la celda más fina que
#'     el presupuesto pagaba medía 245 m y el selector más estrecho pide
#'     236 m, y de ahí salió bajar el deslizador a Kennedy —caja de
#'     7,5 x 7,7 km, celda de 78 m—. Si alguien mueve `nx` o alarga
#'     `sigmas` por abajo, esto para. Sin la guarda, la decisión se
#'     erosiona en silencio y el mapa vuelve a mentir sin que nadie
#'     cambie una línea de prosa.
ppp_kde_familia <- function(p, sigmas, nx, celdas_por_sigma = 3) {
  if (length(sigmas) < 2L) stop("ppp_kde_familia: una familia son dos o más sigmas")
  if (is.unsorted(sigmas, strictly = TRUE))
    stop("ppp_kde_familia: los sigmas tienen que ir de menor a mayor y sin repetir")

  b  <- as.rectangle(p$window)
  ny <- max(1L, as.integer(round(nx * diff(b$yrange) / diff(b$xrange))))
  celda <- diff(b$xrange) / nx

  if (celda * celdas_por_sigma > min(sigmas))
    stop(sprintf(paste0("ppp_kde_familia: la celda mide %.0f m y el sigma más estrecho es %.0f m.\n",
                        "  Hacen falta %d celdas por sigma y hay %.1f. Ver la decisión 4 de la Fase 3:\n",
                        "  una celda más ancha que el núcleo no dibuja el núcleo, dibuja la rejilla."),
                 celda, min(sigmas), celdas_por_sigma, min(sigmas) / celda))

  ims <- lapply(sigmas, function(s) density(p, sigma = s, dimyx = c(ny, nx)))

  maximos <- vapply(ims, function(im) max(im), numeric(1))
  # La caída de la punta al abrir el núcleo NO es una suposición del
  # texto: es la afirmación del módulo 2, y aquí se comprueba. Si alguna
  # vez no cayera, lo que está mal es la frase, no el dato.
  if (is.unsorted(rev(maximos), strictly = TRUE))
    stop("ppp_kde_familia: la intensidad máxima no cae al abrir el núcleo, que es lo que el módulo 2 afirma")

  fin <- unlist(lapply(ims, function(im) as.numeric(im$v)[is.finite(as.numeric(im$v))]))
  list(sigmas = as.numeric(sigmas), imagenes = ims,
       nx = as.integer(nx), ny = ny, celda = celda,
       caja = c(b$xrange[1], b$yrange[1], b$xrange[2], b$yrange[2]),
       escala = c(min(fin), max(fin)),
       maximos = maximos)
}

#' Ajustar un modelo de conglomerado NOMBRANDO la corrección, siempre
#'
#' `correccion` NO TIENE VALOR POR DEFECTO, y esa ausencia es la función.
#'
#' `kppm(p ~ 1, "Thomas")` no menciona ninguna corrección de borde. Por
#' dentro estima K y la pide con el `correction` por defecto, que sobre
#' una ventana no rectangular devuelve `border`, `trans` e `iso`, y de
#' las tres toma la ISOTRÓPICA —lo que spatstat marca como columna
#' recomendada; `fvnames(K, ".y")` devuelve `iso`—. Sobre las 22 piezas
#' del perímetro urbano eso son los 127 s del A.17, pagados sin haberlos
#' pedido: 126,3 s contra 0,4 s con traslación.
#'
#' Y AQUÍ VIENE LO QUE HACE FALTA SABER ANTES DE PONER EL ARGUMENTO
#' BARATO. Se midió qué le pasa al ajuste, no solo al reloj:
#'
#'                    kappa          escala      mu
#'   isotrópica     2,108e-07        932 m      27,10
#'   traslación     1,109e-07      1 320 m      52,35
#'   diferencia        48,2 %       41,6 %      93,2 %
#'
#' Un ajuste describe la ciudad como conglomerados de 27 sedes con escala
#' de 932 m; el otro, como conglomerados de 52 con escala de 1 320 m. No
#' es la misma respuesta redondeada distinto: **el contraste mínimo no
#' ajusta el modelo al patrón, lo ajusta a una ESTIMACIÓN de K**, y
#' cambiar de estimador mueve los parámetros más que cambiar de modelo.
#'
#' Por eso 263 veces de velocidad no se compran calladas. Quien llame
#' nombra la corrección, la corrección sale con el ajuste, y el módulo 11
#' publica los dos.
ppp_kppm <- function(p, modelo, correccion, tendencia = ~1) {
  if (missing(correccion))
    stop(paste0("ppp_kppm: hay que NOMBRAR la corrección. No hay defecto a propósito:\n",
                "  cambiarla mueve kappa un 48 %, la escala un 42 % y mu un 93 %.\n",
                "  Ver A.21.2 del plan. Las de esta ventana: \"iso\" o \"", PPP_CORR, "\"."))
  if (!correccion %in% c("iso", "isotropic", PPP_CORR, "border"))
    stop(sprintf("ppp_kppm: corrección desconocida: %s", correccion))

  t0  <- proc.time()[["elapsed"]]
  fit <- kppm(p, trend = tendencia, clusters = modelo,
              statargs = list(correction = correccion))
  segundos <- proc.time()[["elapsed"]] - t0

  pa <- fit$clustpar
  if (is.null(pa) || !length(pa))
    stop(sprintf("ppp_kppm: el ajuste de %s no devolvió parámetros de conglomerado", modelo))

  # `mu` NO significa lo mismo en los tres modelos, y publicarlo bajo un
  # solo nombre sería publicar tres cosas como si fueran una. En Thomas y
  # en Matérn es el número esperado de puntos por conglomerado —27, 52—;
  # en el LGCP es la media del campo gaussiano en escala logarítmica
  # —-12,33—, que no se cuenta en sedes. El nombre viaja con el número.
  mu_que <- if (modelo %in% c("Thomas", "MatClust")) "puntos por conglomerado"
            else if (modelo == "LGCP") "media del campo log-gaussiano"
            else NA_character_

  list(ajuste = fit, modelo = modelo, correccion = correccion,
       segundos = segundos,
       parametros = as.list(pa),
       mu = as.numeric(fit$mu), mu_que = mu_que)
}
