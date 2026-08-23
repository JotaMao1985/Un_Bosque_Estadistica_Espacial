# =====================================================================
# genera_cap4.R — el precálculo del capítulo 4 (T3.1)
#
#   «Patrones puntuales: descripción, CSR y funciones de resumen»
#   semanas 6-7 · Material de Estadística Espacial 2026-II (20929).
#
# QUÉ PRODUCE
#   precalculo/salidas/cap4_datos.json   las cifras de los 12 módulos
#   precalculo/salidas/cap4_mapas.json   las fuentes de los .geomapa
#   precalculo/salidas/cap4_*.csv        lo que las pestañas de Python leen
#
# LA REGLA QUE MANDA (D10): ninguna cifra del capítulo se escribe a mano.
#
# LAS TRES DECISIONES DE JAVIER (2026-08-21), y por qué gobiernan este
# archivo entero. Las tres salieron de medir, no de suponer:
#
#  1. LAS ENVOLVENTES VAN CON CORRECCIÓN DE TRASLACIÓN, sobre la ventana
#     ÍNTEGRA. El plan declaraba que «las envolventes son caras» y
#     atribuía el coste al número de puntos. Es falso: `lansing` tiene
#     2 251 puntos —más que el patrón colombiano— y su envolvente tarda
#     0,11 s, porque su ventana es un RECTÁNGULO. Lo que se paga es el
#     perímetro contra el que hay que corregir, y la isotrópica de
#     Ripley lo recorre por pareja de puntos: 127 s por estimación
#     contra 0,42 s de la traslación, sobre las 22 piezas, 5 agujeros y
#     13 767 vértices del perímetro urbano de Bogotá. Con la isotrópica,
#     una
#     envolvente de 999 son 35 horas. La isotrópica se calcula UNA vez
#     por patrón —no 999— y el módulo 10 publica la diferencia en la
#     ESTIMACIÓN y el coste. Ver A.17 del plan.
#
#  2. DOCE PREGUNTAS Y CINCO EJERCICIOS, como el capítulo 2 y por el
#     mismo motivo: el capítulo cubre dos semanas de clase.
#
#  3. LOS PUNTOS DUPLICADOS SE QUEDAN Y SON MATERIAL. Varias sedes
#     comparten edificio, así que el patrón real NO es simple, y se le
#     nota en G(0) > 0. El módulo 7 lo mide en vez de afirmarlo.
#     Colapsarlos habría cambiado n y con él la λ que el capítulo 1 ya
#     publicó; `rjitter` habría inventado coordenadas que no están.
#
# Ejecutar SIEMPRE con el envoltorio, nunca con `Rscript` a pelo:
#     precalculo/rscript.sh precalculo/genera_cap4.R
# desde la carpeta `Estadistica espacial/`. Ver utf8.R y rscript.sh.
# =====================================================================

suppressPackageStartupMessages({
  library(sf)
  library(spatstat)
  library(spatstat.data)
  library(jsonlite)
  library(data.table)
})

AQUI <- "precalculo"
source(file.path(AQUI, "utf8.R"))     # PRIMERO: para si el proceso no es UTF-8
source(file.path(AQUI, "geo.R"))
source(file.path(AQUI, "puntual.R"))  # lo puntual, compartido con genera_soluciones.R

SALIDAS <- file.path(AQUI, "salidas")
CACHE   <- file.path(AQUI, "cache")
dir.create(SALIDAS, showWarnings = FALSE, recursive = TRUE)
dir.create(CACHE,   showWarnings = FALSE, recursive = TRUE)

SEMILLA <- 2026L
set.seed(SEMILLA)
options(stringsAsFactors = FALSE)

# Las semillas del capítulo, declaradas aquí y no repartidas por el
# archivo: equivocarse de semilla devuelve un número PARECIDO y correcto
# de aspecto, que es el peor tipo de error (lección de T1.1).
SEM_CSR    <- 4026L   # las realizaciones de CSR del módulo 4
SEM_CIEGO  <- 4027L   # la búsqueda de los dos patrones con el mismo chi2 (m5)
SEM_ENV    <- 4028L   # las envolventes de los módulos 8, 9 y 11
SEM_THOMAS <- 4029L   # el proceso de conglomerado del módulo 3

# El presupuesto de simulaciones, declarado en un solo sitio porque el
# Checkpoint 3 exige que cada envolvente publique el suyo.
NSIM_ENV    <- 999L   # las envolventes que el capítulo publica
NSIM_ESCALA <- c(19L, 39L, 99L, 999L)  # el simulador de nsim del módulo 11
N_R         <- 101L   # nodos de la rejilla de r: el JSON se lee, no se integra

r10 <- function(x) round(as.numeric(x), 10)

# LOS P-VALORES NO PASAN POR r10(), y esto lo destapó la primera pasada
# del módulo 2: el chi2 de la ventana urbana da p ~ 1e-62 y `round(.,10)`
# lo publica como **0**. Un p-valor de cero no existe, y el capítulo que
# más habla de qué significa un p-valor no puede imprimir uno imposible.
# Se conservan cifras significativas, y aparte el log10, que es lo que se
# lee en voz alta («del orden de 10^-62»).
pval <- function(x) {
  x <- as.numeric(x)
  if (!is.finite(x)) stop("p-valor no finito")
  signif(x, 6)
}
plog <- function(x) if (as.numeric(x) <= 0) NA_real_ else r10(log10(as.numeric(x)))

# ---------------------------------------------------------------------
# ancla() — la transcripción contra la literatura, que PARA si falla
# ---------------------------------------------------------------------
N_ANCLAS <- 0L
ancla <- function(calculado, publicado, que, tol = 1e-6) {
  N_ANCLAS <<- N_ANCLAS + 1L
  d <- abs(as.numeric(calculado) - as.numeric(publicado))
  if (!is.finite(d) || d > tol)
    stop(sprintf("ANCLA ROTA · %s: calculado %.8f, la fuente publica %.8f (dif %.2e)",
                 que, as.numeric(calculado), as.numeric(publicado), d))
  invisible(TRUE)
}

D <- list()
MAPAS <- list()

# =====================================================================
# 0. LOS DATOS
# =====================================================================
message("0. datos")

PROC <- "datos/procesado"
cole <- st_read(file.path(PROC, "bogota_colegios.gpkg"), quiet = TRUE)
v_urb <- st_read(file.path(PROC, "bogota_ventana_urbana.gpkg"), quiet = TRUE)
v_dc  <- st_read(file.path(PROC, "bogota_ventana_dc.gpkg"), quiet = TRUE)

ancla(nrow(cole), 2209, "sedes educativas de la SED (T0.4)", tol = 0)
ancla(st_crs(cole)$epsg, 9377, "CRS de trabajo: MAGNA-SIRGAS origen nacional", tol = 0)
for (v in list(v_urb, v_dc))
  if (st_crs(v)$epsg != 9377L) stop("una ventana no está en EPSG:9377")

XY <- st_coordinates(cole)

# LA VENTANA NO ES DECORACIÓN, y este capítulo empieza justo ahí. `ppp()`
# DESCARTA los puntos que caen fuera y lo dice en un aviso, que es el
# lugar donde este proyecto no quiere que vivan las cifras: un aviso no
# lo lee nadie. Se capturan y se publican, porque «102 sedes caen fuera
# del perímetro urbano» es el módulo 1 entero.
ppp_en <- function(ventana) {
  w <- as.owin(st_geometry(st_union(ventana)))
  fuera <- 0L
  p <- withCallingHandlers(
    ppp(XY[, 1], XY[, 2], window = w),
    warning = function(w2) {
      m <- regmatches(conditionMessage(w2),
                      regexpr("^[0-9]+(?= point)", conditionMessage(w2), perl = TRUE))
      if (length(m)) fuera <<- as.integer(m)
      invokeRestart("muffleWarning")
    })
  list(p = p, fuera = fuera)
}
u <- ppp_en(v_urb); p_urb <- u$p; fuera_urb <- u$fuera
d <- ppp_en(v_dc);  p_dc  <- d$p; fuera_dc  <- d$fuera

# `ppp()` dice «1 point was rejected», en singular, y el regex de arriba
# solo captura el número si la frase empieza por él. Que el conteo cuadre
# con la resta es la comprobación de que no se perdió por el camino.
if (fuera_urb != nrow(cole) - npoints(p_urb))
  stop("el aviso de puntos rechazados y el conteo real no cuadran (urbana)")
if (fuera_dc != nrow(cole) - npoints(p_dc))
  stop("el aviso de puntos rechazados y el conteo real no cuadran (D.C.)")

A_URB <- area.owin(p_urb$window); A_DC <- area.owin(p_dc$window)
LAM_URB <- npoints(p_urb) / (A_URB / 1e6)     # por km2
LAM_DC  <- npoints(p_dc)  / (A_DC  / 1e6)

# Las anclas contra T0.4, que es la fuente de estas cifras y las publicó
# el capítulo 1. Si la capa cambiara bajo los pies, esto para aquí y no
# en el navegador.
ancla(A_URB / 1e6,  370.1, "área de la ventana urbana (T0.4)", tol = 0.05)
ancla(A_DC  / 1e6, 1633.1, "área de la ventana D.C. (T0.4)",   tol = 0.05)
ancla(LAM_URB, 5.6932, "lambda urbana por km2 (T0.4)", tol = 1e-4)
ancla(LAM_DC,  1.3520, "lambda D.C. por km2 (T0.4)",   tol = 1e-4)

message(sprintf("  urbana: n=%d (fuera %d)  %.1f km2  lambda=%.4f",
                npoints(p_urb), fuera_urb, A_URB/1e6, LAM_URB))
message(sprintf("  D.C.  : n=%d (fuera %d)  %.1f km2  lambda=%.4f",
                npoints(p_dc), fuera_dc, A_DC/1e6, LAM_DC))

# --- Los patrones canónicos, anclados contra la literatura ------------
data(japanesepines); data(redwood); data(cells)
data(swedishpines); data(bei); data(lansing); data(chorley)
ancla(npoints(japanesepines), 65, "japanesepines (Numata)", tol = 0)
ancla(npoints(redwood),       62, "redwood (Strauss/Ripley)", tol = 0)
ancla(npoints(cells),         42, "cells (Crick-Ripley)", tol = 0)
ancla(npoints(swedishpines),  71, "swedishpines (Strand)", tol = 0)
ancla(npoints(bei),         3604, "bei (Condit, Barro Colorado)", tol = 0)
ancla(npoints(lansing),     2251, "lansing (Gerrard)", tol = 0)
ancla(npoints(chorley),     1036, "chorley (Diggle)", tol = 0)

# `n_anclas` se rellena al final, cuando ya están todas contadas: aquí
# valdría 14 y el auditor comprobaría un número que no significa nada.
D$meta <- list(
  capitulo = 4L, generado = format(Sys.Date()), semilla = SEMILLA,
  semillas = list(csr = SEM_CSR, ciego = SEM_CIEGO, envolventes = SEM_ENV,
                  thomas = SEM_THOMAS),
  nsim_envolventes = NSIM_ENV, nsim_escala = NSIM_ESCALA,
  # La corrección de borde de las envolventes viaja EN EL DATO, no en la
  # prosa del ensamblador: el Checkpoint 3 exige que el material la diga
  # al lado de la envolvente, y así no puede quedarse desincronizada.
  correccion_envolventes = "translate",
  paquetes = list(
    spatstat = as.character(packageVersion("spatstat")),
    spatstat.explore = as.character(packageVersion("spatstat.explore")),
    spatstat.geom = as.character(packageVersion("spatstat.geom")),
    sf = as.character(packageVersion("sf"))))

# =====================================================================
# MÓDULO 1 · Qué es un proceso puntual: el objeto ppp y la VENTANA
# =====================================================================
message("1. el objeto ppp y la ventana")

# La ventana como objeto medible: partes y vértices. No es una curiosidad
# geométrica —es la variable que decide el coste de todo el capítulo, y
# el módulo 10 vuelve sobre ella con el cronómetro en la mano.
# `length(owin$bdry)` NO CUENTA PIEZAS: cuenta COMPONENTES DE FRONTERA, y
# un polígono con un agujero aporta dos —su contorno exterior y el del
# agujero—. La ventana urbana son 22 piezas disjuntas y 5 agujeros, que
# suman 27; llamar «27 partes» a eso publica una cifra que no significa
# lo que su nombre dice, y así se escribió hasta que el auditor en
# Python, que cuenta las piezas con shapely, no coincidió. Se publican
# las tres, porque las tres se usan: las piezas describen la ciudad, los
# agujeros explican parte del perímetro, y las componentes son lo que
# recorre la corrección isotrópica.
#
# CONTAR PIEZAS Y AGUJEROS NO ES CONTAR COMPONENTES DE FRONTERA.
# `length(owin$bdry)` da 27 para la ventana urbana, y eso NO son 27
# piezas: son 22 piezas disjuntas más 5 agujeros. Publicarlo como
# «27 partes» —que es como se escribió primero, hasta en el plan— es
# publicar una cifra que no significa lo que su nombre dice, y lo cazó el
# auditor en Python al contar las piezas con shapely.
#
# El segundo intento fue clasificar cada componente por el signo de su
# área, porque spatstat recorre los agujeros al revés. TAMPOCO: sale
# 23 + 3 = 26, uno menos que las componentes, porque hay anillos
# degenerados de área prácticamente nula donde el signo no decide nada.
# Clasificar por el signo era adivinar con aspecto de medir.
#
# Se cuentan donde la estructura está EXPLÍCITA: en el polígono de sf, un
# MULTIPOLYGON es una lista de piezas y cada pieza una lista de anillos,
# el primero exterior y los demás agujeros. Y se comprueba que la suma
# cuadre con las componentes de spatstat, que es una comprobación que
# puede fallar.
piezas_y_agujeros <- function(ventana_sf) {
  g <- sf::st_geometry(sf::st_union(ventana_sf))[[1]]
  if (inherits(g, "MULTIPOLYGON")) {
    list(piezas = length(g),
         agujeros = sum(vapply(g, function(pieza) length(pieza) - 1L, 0L)))
  } else {
    list(piezas = 1L, agujeros = length(g) - 1L)
  }
}

resumen_ventana <- function(p, ventana_sf, fuera, nombre, descripcion) {
  a <- area.owin(p$window)
  pa <- piezas_y_agujeros(ventana_sf)
  if (pa$piezas + pa$agujeros != length(p$window$bdry))
    stop(sprintf("%s: %d piezas y %d agujeros no suman las %d componentes de frontera de spatstat",
                 nombre, pa$piezas, pa$agujeros, length(p$window$bdry)))
  list(nombre = nombre, descripcion = descripcion,
       n = npoints(p), fuera = fuera,
       area_km2 = r10(a / 1e6), perimetro_km = r10(perimeter(p$window) / 1000),
       lambda_km2 = r10(npoints(p) / (a / 1e6)),
       piezas = pa$piezas, agujeros = pa$agujeros,
       componentes_frontera = length(p$window$bdry),
       vertices = ppp_vertices(p$window))
}
D$m1 <- list(
  sedes_total = nrow(cole),
  urbana = resumen_ventana(p_urb, v_urb, fuera_urb, "Perímetro urbano",
                           "El suelo urbano de Bogotá, sin los cerros ni la ruralidad del D.C."),
  dc = resumen_ventana(p_dc, v_dc, fuera_dc, "Distrito Capital",
                       "El D.C. completo, incluida Sumapaz y los cerros orientales"),
  # El cociente es LA cifra del módulo: el mismo dato, la misma ciudad y
  # dos intensidades que se llevan un factor de más de cuatro. La ventana
  # no acompaña al estimador: forma parte de él.
  factor_lambda = r10(LAM_URB / LAM_DC),
  # Y el reverso, que es el que sorprende: la ventana grande no tiene
  # cuatro veces más sedes, tiene cuatro veces más SUELO. Al pasar del
  # perímetro urbano al D.C. entero, el numerador sube un 4,8 % y el
  # denominador se multiplica por 4,41. Toda la diferencia de lambda la
  # pone la ventana, y ninguna, el dato.
  diferencia_n = npoints(p_dc) - npoints(p_urb),
  aumento_n_pct = r10(100 * (npoints(p_dc) - npoints(p_urb)) / npoints(p_urb)),
  cociente_area = r10(A_DC / A_URB))
ancla(D$m1$factor_lambda, 4.2110, "el factor de lambda entre las dos ventanas", tol = 1e-3)

message(sprintf("  factor lambda = %.4f  ·  n difiere en %d  ·  el area, x%.2f",
                D$m1$factor_lambda, D$m1$diferencia_n, D$m1$cociente_area))
# =====================================================================
# MÓDULO 2 · La intensidad lambda: homogénea contra inhomogénea
# =====================================================================
message("2. intensidad por conteo")

# El estimador por conteo de toda la vida: n / |W|. Lo que el módulo
# enseña es que ese número solo describe el patrón si lambda es
# CONSTANTE, y que basta partir la ventana para verlo.
#
# `quadratcount` reparte una rejilla nx x ny sobre el rectángulo
# envolvente y recorta cada celda contra la ventana. En una ventana de 27
# partes eso deja celdas con área minúscula, y ahí el chi2 deja de valer:
# se publica cuántas celdas tienen esperanza < 5, que es el supuesto que
# el módulo 5 va a poner en duda. No se esconde en un aviso.
cuadrantes <- function(p, nx, ny = nx) {
  qc <- quadratcount(p, nx = nx, ny = ny)
  te <- quadrat.test(p, nx = nx, ny = ny)   # avisa si alguna esperanza < 5
  obs <- as.vector(qc); esp <- as.vector(te$expected)
  list(nx = nx, ny = ny, celdas = length(obs),
       n_obs = sum(obs), media = r10(mean(obs)), var = r10(var(obs)),
       # El índice de dispersión: var/media. Bajo Poisson vale 1, y es la
       # cifra que el chi2 escala. Se publica aparte porque el módulo 6 lo
       # hace variar con el tamaño de celda y necesita la serie.
       dispersion = r10(var(obs) / mean(obs)),
       vacios = sum(obs == 0), maximo = max(obs),
       chi2 = r10(te$statistic), gl = as.integer(te$parameter["df"]),
       p_valor = pval(te$p.value), p_log10 = plog(te$p.value),
       esperanza_min = r10(min(esp)), celdas_esperanza_baja = sum(esp < 5))
}
q_urb <- suppressWarnings(cuadrantes(p_urb, 10))
q_jap <- cuadrantes(japanesepines, 5)
q_bei <- cuadrantes(bei, 10, 5)

D$m2 <- list(
  lambda_urbana_km2 = r10(LAM_URB),
  lambda_urbana_m2  = r10(npoints(p_urb) / A_URB),
  # La misma intensidad en tres unidades. No es relleno: el estudiante
  # que la calcule en m2 va a leer 5,7e-06 y tiene que reconocerla.
  lambda_urbana_ha  = r10(npoints(p_urb) / (A_URB / 1e4)),
  urbana = q_urb, japanesepines = q_jap, bei = q_bei,
  # bei es el contraste canónico: 3 604 árboles cuya intensidad varía
  # con la elevación del terreno, y por eso su chi2 es enorme. El
  # capítulo 5 lo modela; aquí solo se constata que lambda no es una
  # constante y que un solo número la describía mal.
  bei_veces_chi2 = r10(q_bei$chi2 / q_jap$chi2))

# El ancla de este módulo es una identidad, no una cita: el chi2 del test
# de cuadrantes ES el índice de dispersión multiplicado por los grados de
# libertad, cuando las celdas tienen la misma área. `japanesepines` vive
# en el cuadrado unidad, así que ahí tiene que cuadrar exacto.
ancla(q_jap$chi2, q_jap$dispersion * q_jap$gl,
      "chi2 = indice de dispersion x gl, en celdas de igual area", tol = 1e-6)

message(sprintf("  urbana 10x10: chi2=%.1f (gl=%d, p=10^%.1f) · %d celdas con esperanza < 5",
                q_urb$chi2, q_urb$gl, q_urb$p_log10, q_urb$celdas_esperanza_baja))

# =====================================================================
# MÓDULO 3 · Los tres regímenes
# =====================================================================
message("3. los tres regimenes")

# Las mismas cifras que el capítulo 1 publica para los tres canónicos,
# recalculadas aquí a propósito: si el capítulo 4 leyera las del 1,
# una divergencia entre los dos pasaría inadvertida. El auditor las
# contrasta entre capítulos.
regimen <- function(p, nombre, fuente, regimen) {
  a <- area.owin(p$window); n <- npoints(p); nn <- nndist(p)
  esperada <- 0.5 / sqrt(n / a)
  list(nombre = nombre, fuente = fuente, regimen = regimen,
       n = n, area = r10(a), lambda = r10(n / a),
       # La ventana viaja CON el patrón. Sin ella, el auditor en Python
       # tendría que transcribir a mano que `redwood` vive en
       # [0,1]x[-1,0] y `swedishpines` en [0,96]x[0,100], y una
       # transcripción a mano en el control es exactamente lo que el
       # control existe para no tener que creerse.
       ventana = r10(c(p$window$xrange[1], p$window$yrange[1],
                       p$window$xrange[2], p$window$yrange[2])),
       ventana_rectangular = as.integer(is.rectangle(p$window)),
       perimetro = r10(perimeter(p$window)),
       nn_media = r10(mean(nn)), nn_sd = r10(sd(nn)),
       nn_min = r10(min(nn)), nn_max = r10(max(nn)),
       nn_esperada = r10(esperada),
       clark_evans = r10(mean(nn) / esperada),
       # Donnelly corrige el borde subiendo el denominador con el
       # perímetro. La fórmula se escribe en vez de heredarla, y se ancla
       # contra `clarkevans()` más abajo: el convenio queda a la vista Y
       # verificado. El 0.0412 es el de spatstat, no el 0.041 que se cita.
       clark_evans_donnelly = r10(
         mean(nn) / (0.5 * sqrt(a / n) +
                     (0.0514 + 0.0412 / sqrt(n)) * perimeter(p$window) / n)))
}
D$m3 <- list(
  cells = regimen(cells, "Células biológicas", "Crick y Ripley, vía spatstat.data", "regular"),
  japanesepines = regimen(japanesepines, "Pinos japoneses", "Numata (1961)", "aleatorio"),
  redwood = regimen(redwood, "Plántulas de secuoya", "Strauss (1975) / Ripley (1977)", "agregado"),
  swedishpines = regimen(swedishpines, "Pinos suecos", "Strand (1972)", "regular"),
  bogota = regimen(p_urb, "Sedes educativas de Bogotá",
                   "SED Bogotá 12.25, ventana urbana", "por decidir"))

# Las anclas contra la implementación de referencia. `clarkevans()`
# devuelve el ingenuo y el de Donnelly; si spatstat cambiara de convenio,
# esto para el precálculo en vez de publicar otra cifra.
for (nm in c("cells", "japanesepines", "redwood", "swedishpines")) {
  pp <- get(nm)
  ce <- clarkevans(pp)
  ancla(D$m3[[nm]]$clark_evans, ce[["naive"]],
        sprintf("R ingenuo de %s contra clarkevans()", nm), tol = 1e-8)
  if ("Donnelly" %in% names(ce))
    ancla(D$m3[[nm]]$clark_evans_donnelly, ce[["Donnelly"]],
          sprintf("R de Donnelly de %s contra clarkevans()", nm), tol = 1e-8)
}
# Y el orden de los tres regímenes, que es la afirmación del módulo: si
# alguna vez dejara de cumplirse, el módulo estaría enseñando algo falso.
if (!(D$m3$cells$clark_evans > 1 &&
      D$m3$redwood$clark_evans < 1 &&
      abs(D$m3$japanesepines$clark_evans - 1) < 0.15))
  stop("los tres regímenes ya no se ordenan como el módulo 3 afirma")

message(sprintf("  R: cells=%.4f  japanesepines=%.4f  redwood=%.4f  bogota=%.4f",
                D$m3$cells$clark_evans, D$m3$japanesepines$clark_evans,
                D$m3$redwood$clark_evans, D$m3$bogota$clark_evans))

# =====================================================================
# MÓDULO 4 · CSR: el proceso de Poisson homogéneo y sus dos propiedades
# =====================================================================
message("4. CSR y sus dos propiedades")

# CSR se define por DOS cosas, y el módulo las separa porque el estudiante
# suele quedarse con la segunda:
#   (1) el NÚMERO de puntos en una región A es Poisson de media lambda|A|
#   (2) DADO ese número, las posiciones son uniformes e independientes
# La primera es la que se olvida, y es la que explica por qué dos
# realizaciones del mismo proceso no tienen el mismo n.
set.seed(SEM_CSR)
N_REAL <- 2000L
LAM_DEMO <- 65                       # la lambda de japanesepines, por comparar
conteos <- replicate(N_REAL, npoints(rpoispp(LAM_DEMO, win = owin())))

# La comprobación de la propiedad (1): media y varianza del conteo tienen
# que valer lambda|W| las dos. Que coincidan ENTRE SÍ es la firma de
# Poisson, y es lo que el simulador enseña.
D$m4 <- list(
  n_realizaciones = N_REAL, lambda = LAM_DEMO,
  conteo_media = r10(mean(conteos)), conteo_var = r10(var(conteos)),
  conteo_min = min(conteos), conteo_max = max(conteos),
  conteo_esperado = LAM_DEMO,
  # El histograma que el simulador pinta, contra la Poisson teórica. Se
  # publican los dos: la ley y la muestra, para que se vea que el ajuste
  # es bueno y no perfecto, que es justamente el punto.
  hist_k = seq(min(conteos), max(conteos)),
  hist_obs = as.integer(table(factor(conteos, levels = seq(min(conteos), max(conteos))))),
  hist_teorico = r10(dpois(seq(min(conteos), max(conteos)), LAM_DEMO) * N_REAL))

ancla(D$m4$conteo_media, LAM_DEMO, "media del conteo bajo CSR = lambda|W|", tol = 0.6)
ancla(D$m4$conteo_var,   LAM_DEMO, "varianza del conteo bajo CSR = lambda|W|", tol = 3.5)

# LA SEGUNDA MITAD DEL MÓDULO, y la que engancha con el 11: el azar NO se
# ve uniforme. Se miden 2 000 realizaciones de CSR y se publica el
# recorrido de su R de Clark-Evans. Que el azar puro llegue a R = 0,87 y
# a R = 1,13 es lo que hace inútil comparar una R contra 1 a ojo, y es el
# argumento de las envolventes tres módulos más adelante.
set.seed(SEM_CSR + 1L)
Rs <- replicate(N_REAL, {
  z <- rpoispp(LAM_DEMO, win = owin())
  if (npoints(z) < 3) return(NA_real_)
  mean(nndist(z)) / (0.5 / sqrt(npoints(z) / area.owin(z$window)))
})
Rs <- Rs[is.finite(Rs)]
D$m4$R_csr <- list(
  n = length(Rs), media = r10(mean(Rs)), sd = r10(sd(Rs)),
  min = r10(min(Rs)), max = r10(max(Rs)),
  q025 = r10(unname(quantile(Rs, 0.025))), q975 = r10(unname(quantile(Rs, 0.975))),
  # Cuántas de las 2 000 realizaciones de azar puro darían, leídas a ojo,
  # un veredicto equivocado si el umbral fuera «R < 1 es agregado».
  bajo_1 = sum(Rs < 1), sobre_1 = sum(Rs > 1))
message(sprintf("  R bajo CSR: media=%.4f  recorrido [%.4f, %.4f]  IC95 [%.4f, %.4f]",
                D$m4$R_csr$media, D$m4$R_csr$min, D$m4$R_csr$max,
                D$m4$R_csr$q025, D$m4$R_csr$q975))

# Tres realizaciones para el simulador, con su n distinto a la vista.
set.seed(SEM_CSR + 2L)
D$m4$realizaciones <- lapply(1:3, function(i) {
  z <- rpoispp(LAM_DEMO, win = owin())
  list(n = npoints(z), x = r10(z$x), y = r10(z$y),
       clark_evans = r10(mean(nndist(z)) /
                         (0.5 / sqrt(npoints(z) / area.owin(z$window)))))
})

# =====================================================================
# MÓDULO 5 · El test de cuadrantes y SU CEGUERA
# =====================================================================
message("5. la ceguera del test de cuadrantes")

# La demostración no es «dos patrones con un chi2 PARECIDO»: es dos
# patrones con el chi2 IDÉNTICO, por construcción, y estructuras
# opuestas. Se toma `redwood` —agregado— y se rehace punto por punto
# conservando EXACTAMENTE cuántos caen en cada celda, pero repartiéndolos
# uniformemente dentro de la suya. Los conteos son los mismos, luego el
# chi2 es el mismo hasta el último decimal; y sin embargo uno tiene
# grumos de dos metros y el otro no tiene ninguno.
#
# Que sea EXACTO y no aproximado importa: un chi2 «parecido» invita a
# discutir si la diferencia es del azar. Con el mismo número no hay
# discusión posible, y lo que queda es la pregunta del módulo: entonces,
# ¿qué es lo que el chi2 no mira?
NX5 <- 5L

# `ppp_rebaraja()` vive en puntual.R, con la convención de celda que
# costó dos intentos y la comprobación de conteos dentro. La comparte con
# el ejercicio E2 del capítulo, en genera_soluciones.R: copiarla aquí es
# como las dos dejarían de comprobar lo mismo.
red_reb <- ppp_rebaraja(redwood, NX5, NX5, SEM_CIEGO)

q_red <- cuadrantes(redwood, NX5)
q_reb <- cuadrantes(red_reb, NX5)
# La comprobación de que los conteos se conservan vive DENTRO de
# `ppp_rebaraja()`: es de la función, no de quien la llama. Aquí queda el
# ancla sobre lo que el módulo publica, que es el chi2 idéntico.
ancla(q_reb$chi2, q_red$chi2, "el chi2 de los dos patrones del módulo 5 es el mismo", tol = 1e-9)

# Y lo que SÍ los separa, adelantado aquí y desarrollado en los módulos
# 7 a 9: la distancia media al vecino más próximo, que cae un tercio.
D$m5 <- list(
  nx = NX5, n = npoints(redwood),
  original = c(q_red, list(nombre = "redwood original", regimen = "agregado")),
  rebarajado = c(q_reb, list(nombre = "redwood rebarajado por celda",
                             regimen = "uniforme dentro de cada celda")),
  nn_original = r10(mean(nndist(redwood))),
  nn_rebarajado = r10(mean(nndist(red_reb))),
  nn_cociente = r10(mean(nndist(red_reb)) / mean(nndist(redwood))),
  ce_original = r10(clarkevans(redwood)[["naive"]]),
  ce_rebarajado = r10(clarkevans(red_reb)[["naive"]]),
  # Las coordenadas de los dos, para pintarlos lado a lado. 62 puntos por
  # patrón: 0,5 KB del presupuesto y son el módulo entero.
  x1 = r10(redwood$x), y1 = r10(redwood$y),
  x2 = r10(red_reb$x), y2 = r10(red_reb$y))
message(sprintf("  chi2 identico = %.6f  ·  d_nn media: %.4f -> %.4f (x%.2f)",
                q_red$chi2, D$m5$nn_original, D$m5$nn_rebarajado, D$m5$nn_cociente))

# =====================================================================
# MÓDULO 6 · El tamaño del cuadrante: esto es el MAUP otra vez
# =====================================================================
message("6. el tamano del cuadrante")

# El mismo patrón, la misma pregunta, y el veredicto cambia con el tamaño
# de la celda. Es literalmente el efecto de escala del capítulo 3, ahora
# sobre un patrón puntual, y por eso el módulo se llama así.
barrido <- function(p, nombre, nxs) {
  filas <- lapply(nxs, function(k) {
    q <- suppressWarnings(cuadrantes(p, k))
    data.table(patron = nombre, nx = k, celdas = q$celdas,
               media = q$media, dispersion = q$dispersion,
               chi2 = q$chi2, gl = q$gl, p_valor = q$p_valor,
               esperanza_min = q$esperanza_min,
               celdas_esperanza_baja = q$celdas_esperanza_baja,
               rechaza = as.integer(q$p_valor < 0.05))
  })
  rbindlist(filas)
}
NXS <- c(2L, 3L, 4L, 5L, 6L, 8L, 10L, 12L, 15L, 20L)
b_red <- barrido(redwood, "redwood", NXS)
b_jap <- barrido(japanesepines, "japanesepines", NXS)
b_urb <- barrido(p_urb, "bogota_urbana", NXS)

D$m6 <- list(
  nxs = NXS,
  redwood = as.list(b_red), japanesepines = as.list(b_jap), bogota = as.list(b_urb),
  # LA CIFRA DEL MÓDULO: con qué tamaño de celda el veredicto cambia de
  # signo sobre el MISMO patrón. Si algún día dejara de haber cambio, el
  # módulo tendría que decir otra cosa, así que se comprueba abajo.
  japanesepines_rechazos = sum(b_jap$rechaza),
  japanesepines_celdas_rechazo = b_jap$nx[b_jap$rechaza == 1],
  redwood_rechazos = sum(b_red$rechaza),
  # Y el aviso que el módulo tiene que dar: a partir de cierto nx, la
  # esperanza por celda baja de 5 y el chi2 deja de valer. La escala que
  # más resuelve es la que rompe el supuesto.
  redwood_nx_esperanza_baja = b_red$nx[b_red$celdas_esperanza_baja > 0][1])
if (D$m6$japanesepines_rechazos == 0L && D$m6$redwood_rechazos == length(NXS))
  message("  (sin cambio de veredicto en japanesepines: el módulo 6 lo dice así)")
message(sprintf("  redwood rechaza en %d de %d tamaños · esperanza < 5 desde nx=%s",
                D$m6$redwood_rechazos, length(NXS),
                as.character(D$m6$redwood_nx_esperanza_baja)))

# =====================================================================
# Las funciones de resumen: la maquinaria común de los módulos 7 a 11
# =====================================================================

# LAS CURVAS SE CALCULAN EN LA REJILLA FINA DE SPATSTAT Y SE PUBLICAN EN
# UNA DE 101 NODOS. No al revés, y la diferencia no es de peso sino de
# corrección: pasarle a `Kest` una r gruesa cambia la estimación —el
# estimador de bordes trabaja sobre los intervalos que se le den— y `pcf`
# directamente necesita rejilla fina para el suavizado. Se calcula con lo
# que spatstat elija y se INTERPOLA para publicar.
r6 <- function(x) signif(as.numeric(x), 6)
rejilla_r <- function(fv, n = N_R) ppp_rejilla_r(fv, n)
curva <- function(fv, col, rg) r6(ppp_curva(fv, col, rg))

# =====================================================================
# MÓDULO 7 · Distancias al vecino más próximo: G y F
# =====================================================================
message("7. las funciones G y F")

# G mira desde los PUNTOS: la distribución de la distancia de cada punto
# a su vecino más próximo. F mira desde el ESPACIO VACÍO: desde una
# rejilla de sitios cualesquiera, la distancia al punto más cercano. La
# pareja separa los regímenes en direcciones opuestas —un patrón agregado
# deja mucho hueco, así que su G sube pronto y su F tarde— y por eso el
# módulo las enseña juntas y no una detrás de otra.
# LA G VA CON DOS CURVAS Y NO CON UNA, y el motivo lo destapó la primera
# pasada. El estimador de Kaplan-Meier —el que corrige el borde— vale
# CERO en r = 0 por convenio, así que el atomo que los puntos duplicados
# ponen justo ahí no se ve: G(0) salía 0,0000 con 79 sedes coincidentes
# encima de la mesa. La G empírica (`raw`, sin corregir) sí lo enseña, y
# vale 0,037494, que es exactamente la fracción de sedes con un vecino a
# distancia cero. No es un error de spatstat ni un detalle: es que la
# corrección de borde y el atomo viven en el mismo punto de la curva, y
# el módulo lo enseña poniendo las dos una encima de otra.
gf <- function(p, nombre) {
  g <- Gest(p, correction = c("km", "none"))   # `none` da la columna `raw`
  f <- Fest(p, correction = "km")
  rg_g <- rejilla_r(g); rg_f <- rejilla_r(f)
  nn <- nndist(p)
  list(nombre = nombre, n = npoints(p),
       # G(0) > 0 SOLO puede pasar con puntos duplicados, y es la cifra
       # que la decisión 3 de Javier convierte en material.
       coincidentes = sum(nn == 0),
       coincidentes_pct = r10(100 * sum(nn == 0) / npoints(p)),
       r_g = r6(rg_g), g_obs = curva(g, "km", rg_g), g_teo = curva(g, "theo", rg_g),
       g_emp = curva(g, "raw", rg_g), g_emp_en_cero = r6(g[["raw"]][1]),
       r_f = r6(rg_f), f_obs = curva(f, "km", rg_f), f_teo = curva(f, "theo", rg_f),
       # La distancia a la que G alcanza la mitad de los puntos: una sola
       # cifra que resume la curva y se puede comparar entre patrones.
       g_mediana = r6(unname(quantile(nn, 0.5))))
}
D$m7 <- list(
  cells = gf(cells, "Células biológicas"),
  japanesepines = gf(japanesepines, "Pinos japoneses"),
  redwood = gf(redwood, "Plántulas de secuoya"),
  bogota = gf(p_urb, "Sedes educativas, ventana urbana"))

# LOS DUPLICADOS, MEDIDOS. Que el patrón real no sea simple no es un
# defecto del dato: son sedes distintas en el mismo edificio. Pero rompe
# el supuesto de todos los estimadores del capítulo, así que se publica
# cuántas son y qué le hace a G.
xy_urb <- cbind(p_urb$x, p_urb$y)
dup_urb <- sum(duplicated(xy_urb))
D$m7$duplicados <- list(
  n = npoints(p_urb), distintos = npoints(p_urb) - dup_urb, repetidos = dup_urb,
  # `duplicated` cuenta las repeticiones; los PUNTOS implicados son más,
  # porque el primero de cada coincidencia no está duplicado todavía.
  implicados = sum(nndist(p_urb) == 0),
  maximo_por_sitio = max(table(paste(xy_urb[, 1], xy_urb[, 2]))),
  # Las dos lecturas de G en r = 0, y la diferencia entre ellas es el
  # módulo: la empírica ve el atomo, la corregida lo pone a cero.
  g_empirica_en_cero = D$m7$bogota$g_emp_en_cero,
  g_km_en_cero = r6(D$m7$bogota$g_obs[1]))
# La identidad que hace exacta la afirmación: la G empírica en r = 0 ES
# la fracción de puntos con un vecino a distancia cero.
ancla(D$m7$duplicados$g_empirica_en_cero,
      D$m7$bogota$coincidentes / npoints(p_urb),
      "G empírica en r=0 = fracción de puntos coincidentes", tol = 1e-6)
if (D$m7$bogota$coincidentes == 0)
  stop("el patrón colombiano ya no tiene duplicados: el módulo 7 afirma que sí")
message(sprintf("  bogota: %d sedes coincidentes (%.2f %%) · G empírica(0)=%.6f, G km(0)=%.6f · máximo %d en un sitio",
                D$m7$bogota$coincidentes, D$m7$bogota$coincidentes_pct,
                D$m7$duplicados$g_empirica_en_cero, D$m7$duplicados$g_km_en_cero,
                D$m7$duplicados$maximo_por_sitio))

# =====================================================================
# MÓDULO 8 · La función K de Ripley, y su transformación L
# =====================================================================
message("8. K de Ripley y L")

# K(r) es el número esperado de vecinos a distancia <= r de un punto
# cualquiera, dividido por lambda. Bajo CSR vale pi r^2, que es una
# parábola: comparar una curva contra una parábola a ojo es incómodo, y
# de ahí L(r) = sqrt(K/pi), que bajo CSR es la recta L = r.
#
# LA CORRECCIÓN ES `translate` EN TODO EL CAPÍTULO SALVO EL MÓDULO 10,
# por la decisión 1 de Javier. No es un detalle de implementación: va
# escrito en el material al lado de cada curva.
#
# Los dos nombres —el del argumento y el de la columna— vienen de
# puntual.R, que explica por qué no coinciden.
CORR     <- PPP_CORR       # "translate", lo que se le pide a spatstat
CORR_COL <- PPP_CORR_COL   # "trans", como se llama la columna que devuelve
kl <- function(p, nombre) {
  k <- Kest(p, correction = CORR)
  rg <- rejilla_r(k)
  kobs <- curva(k, CORR_COL, rg); kteo <- curva(k, "theo", rg)
  list(nombre = nombre, n = npoints(p), correccion = CORR,
       r = r6(rg), k_obs = kobs, k_teo = kteo,
       # L se calcula aquí y no en el navegador: sqrt() de una cifra
       # publicada es aritmética en el ensamblador, que D10 prohíbe.
       l_obs = r6(sqrt(kobs / pi)), l_teo = r6(sqrt(kteo / pi)),
       l_menos_r = r6(sqrt(kobs / pi) - rg),
       # El máximo de |L(r) - r| resume la desviación en una cifra, y es
       # la que el test de desviación del módulo 11 formaliza.
       max_desvio = r6(max(abs(sqrt(kobs / pi) - rg))),
       r_max_desvio = r6(rg[which.max(abs(sqrt(kobs / pi) - rg))]))
}
D$m8 <- list(
  cells = kl(cells, "Células biológicas"),
  japanesepines = kl(japanesepines, "Pinos japoneses"),
  redwood = kl(redwood, "Plántulas de secuoya"),
  bogota = kl(p_urb, "Sedes educativas, ventana urbana"))

# El ancla del módulo: bajo CSR, K teórica ES pi r^2. Si spatstat cambiara
# de convenio en la columna `theo`, esto para el precálculo.
rg_j <- D$m8$japanesepines$r
ancla(max(abs(D$m8$japanesepines$k_teo - pi * rg_j^2)), 0,
      "K teórica = pi r^2", tol = 1e-6)
# Y el orden de los regímenes en L: regular por debajo de la recta,
# agregado por encima. Es la lectura que el módulo enseña.
if (!(D$m8$cells$l_menos_r[50] < 0 && D$m8$redwood$l_menos_r[50] > 0))
  stop("L - r ya no ordena los regímenes como el módulo 8 afirma")
message(sprintf("  max|L-r|: cells=%.4f  japanesepines=%.4f  redwood=%.4f  bogota=%.1f m",
                D$m8$cells$max_desvio, D$m8$japanesepines$max_desvio,
                D$m8$redwood$max_desvio, D$m8$bogota$max_desvio))

# =====================================================================
# MÓDULO 9 · La correlación de pares g(r)
# =====================================================================
message("9. la correlacion de pares")

# K es ACUMULATIVA y arrastra: si hay agregación a 20 m, K sigue por
# encima de la teórica a 500 m aunque a 500 m no pase nada, porque los
# vecinos de 20 m siguen contados dentro. g(r) es su derivada
# normalizada y mira solo la distancia r, así que dice DÓNDE está la
# estructura. El módulo pone las dos sobre el mismo patrón para que se
# vea el arrastre.
gr <- function(p, nombre) {
  g <- pcf(p, correction = CORR)
  rg <- rejilla_r(g)
  gobs <- curva(g, CORR_COL, rg)
  # g se dispara cerca de r = 0 (el suavizado no tiene datos ahí) y ese
  # tramo no se publica: se recorta al primer nodo con estimación finita
  # y estable, declarado en el propio dato para que el capítulo lo diga.
  list(nombre = nombre, n = npoints(p), correccion = CORR,
       r = r6(rg), g_obs = gobs, g_teo = rep(1, length(rg)),
       g_max = r6(max(gobs[-1])), r_g_max = r6(rg[which.max(replace(gobs, 1, -Inf))]),
       # La distancia a la que g cruza el 1 por última vez: el alcance de
       # la estructura, que K no sabe decir.
       r_ultimo_cruce = r6(rg[max(which(abs(gobs - 1) > 0.05))]))
}
D$m9 <- list(
  cells = gr(cells, "Células biológicas"),
  japanesepines = gr(japanesepines, "Pinos japoneses"),
  redwood = gr(redwood, "Plántulas de secuoya"),
  bogota = gr(p_urb, "Sedes educativas, ventana urbana"))
message(sprintf("  g maxima: redwood=%.2f en r=%.3f  ·  bogota=%.2f en r=%.0f m",
                D$m9$redwood$g_max, D$m9$redwood$r_g_max,
                D$m9$bogota$g_max, D$m9$bogota$r_g_max))

# =====================================================================
# La caché de lo caro, y el cronómetro
# =====================================================================

# Se cachea lo que tarda minutos, con los parámetros EN EL NOMBRE del
# archivo: una caché que no declara con qué se hizo es una caché que
# devuelve el resultado de otra pregunta. La lección es de T2.4, donde el
# grafo de contiguidad lleva el número de rasgos en el nombre.
cacheado <- function(nombre, expr) {
  f <- file.path(CACHE, paste0("cap4_", nombre, ".rds"))
  if (file.exists(f)) { message(sprintf("    %s: de la cache", nombre)); return(readRDS(f)) }
  v <- force(expr)
  saveRDS(v, f)
  v
}
# El cronómetro devuelve el valor Y el tiempo, porque el módulo 10
# publica los dos y separarlos invitaría a medir una cosa y publicar otra.
con_reloj <- function(expr) {
  t0 <- proc.time()[["elapsed"]]
  v <- force(expr)
  list(valor = v, segundos = as.numeric(proc.time()[["elapsed"]] - t0))
}

# =====================================================================
# MÓDULO 10 · Efectos de borde: las tres correcciones, y qué cuestan
# =====================================================================
message("10. efectos de borde (lo caro: la isotrópica va una vez)")

# UN PUNTO PEGADO AL BORDE TIENE VECINOS FUERA DE LA VENTANA, y nadie los
# ha observado. Sin corregir, K cuenta menos vecinos de los que hay y el
# patrón parece MÁS regular de lo que es. Las tres correcciones reparan
# eso de tres maneras, y este módulo hace algo que ningún libro hace:
# medir también lo que cuestan, sobre una ventana de verdad.
#
# Aquí, y solo aquí, se calcula la isotrópica: UNA vez, no 999. Es la
# decisión 1 de Javier, y la cifra que la justifica se publica en este
# mismo módulo.
CORRECCIONES <- c("none", "border", "translate", "isotropic")
COL_DE <- c(none = "un", border = "border", translate = "trans", isotropic = "iso")

bordes <- cacheado("bordes_urbana", {
  lapply(CORRECCIONES, function(cr) {
    message(sprintf("    Kest %s ...", cr))
    r <- con_reloj(Kest(p_urb, correction = cr))
    list(correccion = cr, segundos = r$segundos, fv = r$valor)
  })
})
names(bordes) <- CORRECCIONES

rg_b <- rejilla_r(bordes$translate$fv)
curvas_b <- lapply(CORRECCIONES, function(cr)
  curva(bordes[[cr]]$fv, COL_DE[[cr]], rg_b))
names(curvas_b) <- CORRECCIONES
k_teo_b <- curva(bordes$translate$fv, "theo", rg_b)

D$m10 <- list(
  ventana = list(piezas = D$m1$urbana$piezas, agujeros = D$m1$urbana$agujeros,
                 componentes_frontera = D$m1$urbana$componentes_frontera,
                 vertices = ppp_vertices(p_urb$window),
                 perimetro_km = r10(perimeter(p_urb$window) / 1000)),
  r = r6(rg_b), k_teo = k_teo_b,
  correcciones = lapply(CORRECCIONES, function(cr) list(
    correccion = cr, segundos = r6(bordes[[cr]]$segundos),
    k = curvas_b[[cr]],
    l_menos_r = r6(sqrt(curvas_b[[cr]] / pi) - rg_b))),
  # EL ÁTOMO DE LOS DUPLICADOS APARECE TAMBIÉN AQUÍ, y lo destapó el
  # auditor. En r = 0 la K SIN corregir no vale cero: vale lo que aportan
  # las parejas a distancia exactamente cero, que son las 79 sedes
  # coincidentes del módulo 7. Es el mismo átomo que allí se ve en G,
  # ahora en K, y por eso la afirmación «sin corregir siempre queda por
  # debajo» vale PARA r > 0 y no en el origen. Se publica en vez de
  # recortar la curva: los duplicados no son una anécdota del dato, se
  # cuelan en todos los estimadores, y eso enlaza los módulos 7 y 10.
  k_cero_sin_corregir = curvas_b$none[1],
  k_cero_traslacion = curvas_b$translate[1],
  # QUÉ PASA SI SE IGNORA, en una cifra: cuánto se pierde de K en el
  # tramo largo por no corregir. Es una subestimación, siempre, y por eso
  # el patrón parece más regular de lo que es.
  sesgo_max_pct = r6(100 * max((curvas_b$translate - curvas_b$none) /
                               pmax(curvas_b$translate, 1e-9))),
  r_sesgo_max = r6(rg_b[which.max((curvas_b$translate - curvas_b$none) /
                                  pmax(curvas_b$translate, 1e-9))]),
  # Y LO QUE CUESTA CADA UNA, que es la mitad del módulo. Estas cifras
  # son de ESTA máquina: el auditor no puede reproducirlas y las declara
  # saltadas. Lo que sí es reproducible —y es lo que el capítulo afirma—
  # es el ORDEN de magnitud entre ellas.
  coste = list(
    medido_en = sprintf("R %s.%s, %s",
                        R.version$major, R.version$minor, R.version$platform),
    nucleos = as.integer(parallel::detectCores()),
    veces_isotropica_sobre_traslacion =
      r6(bordes$isotropic$segundos / bordes$translate$segundos),
    horas_envolvente_isotropica = r6(bordes$isotropic$segundos * NSIM_ENV / 3600),
    minutos_envolvente_traslacion = r6(bordes$translate$segundos * NSIM_ENV / 60)))

# Las dos afirmaciones del módulo, comprobadas y no supuestas.
if (D$m10$sesgo_max_pct <= 0)
  stop("sin corregir, K ya no queda por debajo: el módulo 10 afirma que sí")
if (any(curvas_b$none[-1] > curvas_b$translate[-1] + 1e-9))
  stop("sin corregir, K supera a la corregida en algún r > 0: el módulo 10 afirma que no")
if (bordes$isotropic$segundos <= bordes$translate$segundos)
  stop("la isotrópica ya no es la cara: la decisión 1 se apoyaba en que lo fuera")
message(sprintf("  coste: iso=%.1fs  trans=%.2fs  border=%.2fs  none=%.2fs  (x%.0f)",
                bordes$isotropic$segundos, bordes$translate$segundos,
                bordes$border$segundos, bordes$none$segundos,
                D$m10$coste$veces_isotropica_sobre_traslacion))
message(sprintf("  sin corregir, K se queda hasta un %.1f %% por debajo (en r=%.0f m)",
                D$m10$sesgo_max_pct, D$m10$r_sesgo_max))

# =====================================================================
# MÓDULO 11 · Envolventes: qué NO es un p-valor de envolvente
# =====================================================================
message("11. envolventes (nsim=999, traslación)")

# La envolvente puntual se lee mal casi siempre. Es un intervalo al 95 %
# PARA CADA r POR SEPARADO; mirar la curva entera y decir «sale, luego
# p < 0,05» es hacer 101 contrastes y quedarse con el peor. Este módulo
# lo MIDE: con las 999 simulaciones ya guardadas se cuenta cuántas de
# ellas —todas de CSR puro, todas «nulas» por construcción— se salen de
# la banda en algún r. Ese número es el error simultáneo real, y no se
# parece al 5 % que la banda promete punto a punto.
envolvente <- function(p, nombre, fun, nsim, semilla) {
  cacheado(sprintf("env_%s_%s_%d_%s", nombre, deparse(substitute(fun)), nsim, CORR), {
    message(sprintf("    envolvente %s · %s · nsim=%d ...", nombre, "K", nsim))
    set.seed(semilla)
    envelope(p, Kest, nsim = nsim, correction = CORR,
             savefuns = TRUE, verbose = FALSE)
  })
}
env_bog <- envolvente(p_urb, "bogota", Kest, NSIM_ENV, SEM_ENV)
env_red <- envolvente(redwood, "redwood", Kest, NSIM_ENV, SEM_ENV + 1L)
env_jap <- envolvente(japanesepines, "japanesepines", Kest, NSIM_ENV, SEM_ENV + 2L)

# LA TASA DE SALIDA, calculada sobre las simulaciones ya guardadas: no
# cuesta ni una simulación más, y es la cifra que da sentido al módulo.
tasa_salida <- function(env, nivel = 0.95) {
  simf <- attr(env, "simfuns")
  M <- as.matrix(as.data.frame(simf)[, -1])       # filas = r, columnas = sims
  ok <- apply(M, 1, function(z) all(is.finite(z)))
  M <- M[ok, , drop = FALSE]
  a <- (1 - nivel) / 2
  lo <- apply(M, 1, quantile, probs = a)
  hi <- apply(M, 1, quantile, probs = 1 - a)
  fuera <- apply(M, 2, function(col) any(col < lo | col > hi))
  list(nsim = ncol(M), nodos_r = nrow(M),
       fuera = sum(fuera), pct = r6(100 * mean(fuera)), nivel = nivel)
}
ts_bog <- tasa_salida(env_bog); ts_red <- tasa_salida(env_red)

rg_e <- rejilla_r(env_bog)
serie_env <- function(env, nombre) {
  rg <- rejilla_r(env)
  list(nombre = nombre, nsim = NSIM_ENV, correccion = CORR,
       r = r6(rg), obs = curva(env, "obs", rg), teo = curva(env, "theo", rg),
       lo = curva(env, "lo", rg), hi = curva(env, "hi", rg),
       # Si la observada se sale, y dónde. La primera r en que se sale es
       # la escala de la estructura, y es lo que se interpreta.
       sale = as.integer(any(curva(env, "obs", rg) > curva(env, "hi", rg) |
                             curva(env, "obs", rg) < curva(env, "lo", rg))))
}
D$m11 <- list(
  nsim = NSIM_ENV, correccion = CORR, nivel_puntual = 0.95,
  bogota = serie_env(env_bog, "Sedes educativas, ventana urbana"),
  redwood = serie_env(env_red, "Plántulas de secuoya"),
  japanesepines = serie_env(env_jap, "Pinos japoneses"),
  # EL NÚMERO DEL MÓDULO. Bajo CSR, la banda puntual al 95 % la cruza en
  # algún r una fracción muchísimo mayor que el 5 %.
  tasa_salida_bogota = ts_bog, tasa_salida_redwood = ts_red,
  # El p-valor puntual mínimo alcanzable con nsim simulaciones: 1/(nsim+1).
  # No es una convención: con 999 simulaciones no existe un p menor que
  # 0,001, por bien que se separe la curva.
  p_minimo = r6(1 / (NSIM_ENV + 1)))

# Y los tests que SÍ contrastan la curva entera, reutilizando las mismas
# simulaciones: no hacen falta 999 más.
D$m11$test_global <- list(
  dclf_bogota_p = pval(dclf.test(env_bog)$p.value),
  mad_bogota_p  = pval(mad.test(env_bog)$p.value),
  dclf_japanesepines_p = pval(dclf.test(env_jap)$p.value),
  mad_japanesepines_p  = pval(mad.test(env_jap)$p.value))

if (ts_bog$pct < 5)
  stop("la tasa de salida bajo CSR salió por debajo del 5 %: el módulo 11 afirma lo contrario")
message(sprintf("  bajo CSR, %d de %d simulaciones (%.1f %%) se salen de la banda puntual al 95 %%",
                ts_bog$fuera, ts_bog$nsim, ts_bog$pct))
message(sprintf("  p mínimo con nsim=%d: %.4f · dclf(bogota) p=%.4g",
                NSIM_ENV, D$m11$p_minimo, D$m11$test_global$dclf_bogota_p))

# LA ESCALA DE nsim, Y LA TRAMPA QUE ESCONDE. La primera versión de este
# bloque decía «la banda se estrecha y se estabiliza al subir nsim». Es
# FALSO, y la propia ejecución lo enseñó: el ancho medio subió de 0,0227
# con 19 simulaciones a 0,0422 con 999.
#
# El motivo no es el ruido: es que `envelope()` construye la banda por
# defecto con el MÍNIMO Y EL MÁXIMO de las simulaciones (nrank = 1), y
# esa banda tiene nivel puntual 2·nrank/(nsim+1). Con 19 simulaciones es
# un contraste al 10 %; con 999, al 0,2 %. Subir nsim sin tocar nrank no
# afina la misma banda: cambia de contraste, y por eso se ensancha.
#
# El módulo publica las dos lecturas, y van en direcciones OPUESTAS. A
# nrank = 1 el nivel se mueve con nsim y la banda se ensancha un 85 %. A
# nivel fijo del 5 % —que exige subir nrank con nsim— la banda se
# ESTRECHA un 23 % de 39 a 999 simulaciones, porque el cuantil deja de
# estimarse con dos observaciones extremas y empieza a estimarse bien.
# Que las dos series se lean al revés es todo el módulo: la pregunta
# «¿cuántas simulaciones hacen falta?» no tiene respuesta hasta que se
# dice a qué nivel.
#
# Y una cifra cierra el asunto: con 19 simulaciones la banda puntual al
# 5 % NO EXISTE —el nrank que haría falta es 0,5—, así que esa fila queda
# fuera de la comparación a nivel fijo y marcada como inalcanzable. La
# elección de nsim no es de precisión: es de qué contrastes hay.
NIVEL_PUNTUAL <- 0.05
banda <- function(M, nrank) {
  lo <- apply(M, 1, function(z) sort(z)[nrank])
  hi <- apply(M, 1, function(z) sort(z, decreasing = TRUE)[nrank])
  mean(hi - lo)
}
D$m11$escala_nsim <- lapply(NSIM_ESCALA, function(ns) {
  e <- cacheado(sprintf("env_escala_%d_%s_sf", ns, CORR), {
    message(sprintf("    envolvente japanesepines · nsim=%d ...", ns))
    set.seed(SEM_ENV + 10L)
    envelope(japanesepines, Kest, nsim = ns, correction = CORR,
             savefuns = TRUE, verbose = FALSE)
  })
  simf <- attr(e, "simfuns")
  M <- as.matrix(as.data.frame(simf)[, -1])
  M <- M[apply(M, 1, function(z) all(is.finite(z))), , drop = FALSE]
  nr5 <- (ns + 1) * NIVEL_PUNTUAL / 2          # el nrank que daría el 5 %
  nr5_ent <- max(1L, as.integer(round(nr5)))
  rg <- rejilla_r(e)
  list(nsim = ns,
       # A nrank = 1: la banda del mínimo-máximo, y el nivel que implica.
       nrank_defecto = 1L,
       nivel_defecto = r6(2 / (ns + 1)),
       ancho_defecto = r6(banda(M, 1L)),
       # A nivel fijo del 5 %: el nrank que hace falta, y si es alcanzable.
       nrank_para_5pct = r6(nr5),
       nrank_usado = nr5_ent,
       nivel_real = r6(2 * nr5_ent / (ns + 1)),
       alcanza_5pct = as.integer(abs(2 * nr5_ent / (ns + 1) - NIVEL_PUNTUAL) < 0.005),
       ancho_5pct = r6(banda(M, nr5_ent)),
       p_minimo = r6(1 / (ns + 1)),
       r = r6(rg), lo = curva(e, "lo", rg), hi = curva(e, "hi", rg))
})
anchos_def <- vapply(D$m11$escala_nsim, function(z) z$ancho_defecto, 0)
anchos_5   <- vapply(D$m11$escala_nsim, function(z) z$ancho_5pct, 0)
alcanzan   <- vapply(D$m11$escala_nsim, function(z) z$alcanza_5pct, 0L) == 1L
# Las dos afirmaciones del módulo, comprobadas y en direcciones opuestas.
# La segunda solo se mira donde el 5 % es alcanzable: incluir la fila de
# nsim = 19, que en realidad es un contraste al 10 %, compararía dos
# niveles distintos y es justo el error que el módulo enseña a no cometer.
if (!all(diff(anchos_def) > 0))
  stop("la banda por defecto ya no se ensancha con nsim: el módulo 11 afirma que sí")
if (sum(alcanzan) < 2L)
  stop("ningún nsim del barrido alcanza el 5 %: el módulo 11 se queda sin comparación")
if (!all(diff(anchos_5[alcanzan]) <= 0))
  stop("a nivel fijo la banda ya no se estrecha con nsim: el módulo 11 afirma que sí")
D$m11$escala_resumen <- list(
  ancho_defecto = r6(anchos_def), ancho_5pct = r6(anchos_5),
  alcanzan_5pct = as.integer(alcanzan),
  veces_defecto = r6(max(anchos_def) / min(anchos_def)),
  # El estrechamiento a nivel fijo, medido SOLO donde el nivel es el
  # mismo: de nsim=39 a nsim=999.
  veces_5pct_alcanzable = r6(max(anchos_5[alcanzan]) / min(anchos_5[alcanzan])))
message(sprintf("  ancho a nrank=1 : %s  (x%.2f)",
                paste(sprintf("%d->%.5f", NSIM_ESCALA, anchos_def), collapse = "  "),
                D$m11$escala_resumen$veces_defecto))
message(sprintf("  ancho al 5 %%    : %s  (x%.2f donde el 5 %% existe)",
                paste(sprintf("%d->%.5f%s", NSIM_ESCALA, anchos_5,
                              ifelse(alcanzan, "", "*")), collapse = "  "),
                D$m11$escala_resumen$veces_5pct_alcanzable))

# =====================================================================
# LOS MAPAS · modo `puntos` del componente .geomapa
# =====================================================================
message("mapas")

# LA VENTANA QUE SE DIBUJA NO ES LA QUE SE ANALIZA, y el capítulo lo
# dice. Analizar con 13 767 vértices es lo correcto —la decisión 1 de
# Javier es no simplificar nada del análisis— pero dibujarlos sería
# meter 110 KB de contorno en un lienzo de 350 px donde no se distingue
# ni uno. Para PINTAR se simplifica; para MEDIR, nunca. Son dos usos del
# mismo objeto y conviene que el material los separe en voz alta.
# Cada parte del contorno viaja como una polilínea. El identificador de
# parte es L2 en un POLYGON y L3 en un MULTIPOLYGON, y la ventana urbana
# es de las segundas: sin mirar las dos columnas, las piezas salen
# empalmadas en una sola línea que cruza la ciudad.
partes_de <- function(ventana, presupuesto) {
  s <- geo_simplifica(ventana, presupuesto = presupuesto, verbose = FALSE)
  cs <- sf::st_coordinates(sf::st_geometry(sf::st_union(s)))
  idx <- if ("L3" %in% colnames(cs)) paste(cs[, "L3"], cs[, "L2"]) else cs[, "L2"]
  lapply(split(seq_len(nrow(cs)), idx), function(i) cs[i, 1:2, drop = FALSE])
}

lineas_urb <- partes_de(v_urb, 900L)
lineas_dc  <- partes_de(v_dc,  600L)
message(sprintf("  contorno urbano: %d partes, %d vértices (el análisis usa %d)",
                length(lineas_urb), sum(vapply(lineas_urb, nrow, 0L)),
                ppp_vertices(p_urb$window)))

MAPAS$patron_urbano <- geo_puntos(
  cbind(p_urb$x, p_urb$y), lineas = lineas_urb,
  titulo = sprintf("%d sedes educativas en el perímetro urbano (%.1f km²)",
                   npoints(p_urb), A_URB / 1e6),
  leyenda = "sede educativa")
MAPAS$patron_dc <- geo_puntos(
  cbind(p_dc$x, p_dc$y), lineas = lineas_dc,
  titulo = sprintf("Las mismas sedes en el D.C. completo (%.1f km²)", A_DC / 1e6),
  leyenda = "sede educativa")

# Los tres regímenes, en su ventana unidad. Son 169 puntos entre los
# tres: el módulo 3 los pone uno al lado del otro y es la imagen que el
# estudiante recuerda del capítulo.
MAPAS$cells <- geo_puntos(cbind(cells$x, cells$y),
  titulo = "Regular: células biológicas (n = 42)", leyenda = "célula")
MAPAS$japanesepines <- geo_puntos(cbind(japanesepines$x, japanesepines$y),
  titulo = "Aleatorio: pinos japoneses (n = 65)", leyenda = "pino")
MAPAS$redwood <- geo_puntos(cbind(redwood$x, redwood$y),
  titulo = "Agregado: plántulas de secuoya (n = 62)", leyenda = "plántula")

# Los dos patrones del módulo 5, con la rejilla de celdas dibujada
# encima: sin ver la rejilla, «el mismo chi2» es una afirmación.
rejilla_lineas <- function(w, nx) {
  bx <- seq(w$xrange[1], w$xrange[2], length.out = nx + 1)
  by <- seq(w$yrange[1], w$yrange[2], length.out = nx + 1)
  c(lapply(bx, function(x) cbind(c(x, x), w$yrange)),
    lapply(by, function(y) cbind(w$xrange, c(y, y))))
}
lin5 <- rejilla_lineas(redwood$window, NX5)
MAPAS$ceguera_original <- geo_puntos(cbind(redwood$x, redwood$y), lineas = lin5,
  titulo = sprintf("Original · chi² = %.4f", D$m5$original$chi2),
  leyenda = "plántula")
MAPAS$ceguera_rebarajado <- geo_puntos(cbind(D$m5$x2, D$m5$y2), lineas = lin5,
  titulo = sprintf("Rebarajado dentro de cada celda · chi² = %.4f", D$m5$rebarajado$chi2),
  leyenda = "punto")

MAPAS$meta <- list(capitulo = 4L, generado = D$meta$generado)

# =====================================================================
# SALIDAS
# =====================================================================
message("salidas")

# El conteo de anclas se sella AQUÍ, con todas ya comprobadas.
D$meta$n_anclas <- N_ANCLAS

txt_datos <- jsonlite::toJSON(D, auto_unbox = TRUE, digits = 10,
                              null = "null", na = "null")
if (grepl('"NA"', txt_datos, fixed = TRUE))
  stop("cap4_datos.json: hay NA escritos como la cadena \"NA\"")
writeLines(txt_datos, file.path(SALIDAS, "cap4_datos.json"), useBytes = TRUE)
message(sprintf("  cap4_datos.json: %.1f KB",
                file.size(file.path(SALIDAS, "cap4_datos.json")) / 1024))

# EL PRESUPUESTO DE ESTE CAPÍTULO ES 150 KB, y la desviación sobre los
# ~120 del §4 está medida, no supuesta: 2 107 + 2 208 puntos son 8 630
# enteros solo de coordenadas, y son EL DATO del capítulo —no geometría
# de fondo que se pueda simplificar—. Los contornos sí se simplificaron,
# a 900 y 600 vértices.
geo_escribe(MAPAS, file.path(SALIDAS, "cap4_mapas.json"), presupuesto_kb = 150)

# Los CSV que leen las pestañas de Python. El de las sedes lleva las
# marcas que el capítulo 5 va a necesitar (sector, zona, jornada) aunque
# el 4 no las use: leer dos veces el GeoPackage para escribir dos CSV
# distintos del mismo dato es cómo se desincronizan.
en_urb <- inside.owin(XY[, 1], XY[, 2], p_urb$window)
data.table::fwrite(data.table(
  x = XY[en_urb, 1], y = XY[en_urb, 2],
  dane_sede = cole$dane_sede[en_urb], sector = cole$sector[en_urb],
  clase = cole$clase[en_urb], zona = cole$zona[en_urb],
  estrato = cole$estrato[en_urb]),
  file.path(SALIDAS, "cap4_bogota_urbana.csv"))
# LOS CUATRO, no los tres que se dibujan. `swedishpines` no tiene mapa
# —el módulo 3 enseña tres regímenes y con cuatro imágenes se pierde la
# terna— pero SÍ tiene cifras publicadas en el módulo 3 y es el patrón
# sobre el que trabaja el ejercicio E2. Sin sus coordenadas aquí, el
# auditor no puede recalcular ninguna de las dos cosas, y de hecho no
# podía: el arnés de inyección le cambió la R de Donnelly y no se enteró
# nadie. Un dato publicado sin fuente auditable es un dato en el que hay
# que creer.
data.table::fwrite(rbindlist(lapply(
  list(cells = cells, japanesepines = japanesepines, redwood = redwood,
       swedishpines = swedishpines),
  function(z) data.table(x = z$x, y = z$y)), idcol = "patron"),
  file.path(SALIDAS, "cap4_regimenes.csv"))
data.table::fwrite(data.table(
  r = D$m8$bogota$r, K = D$m8$bogota$k_obs, K_teorica = D$m8$bogota$k_teo,
  L_menos_r = D$m8$bogota$l_menos_r),
  file.path(SALIDAS, "cap4_bogota_K.csv"))
data.table::fwrite(as.data.table(D$m6$bogota), file.path(SALIDAS, "cap4_cuadrantes.csv"))

message(sprintf("\nLISTO. %d anclas comprobadas, ninguna rota.", N_ANCLAS))
