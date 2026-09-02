# =====================================================================
# genera_cap5.R — el precálculo del capítulo 5 (T3.4)
#
#   «Intensidad por núcleos y modelamiento de procesos puntuales»
#   semanas 8-10 · Material de Estadística Espacial 2026-II (20929).
#
# QUÉ PRODUCE
#   precalculo/salidas/cap5_datos.json   las cifras de los 12 módulos
#   precalculo/salidas/cap5_mapas.json   las fuentes de los .geomapa
#   precalculo/salidas/cap5_*.csv        lo que las pestañas de Python leen
#
# LA REGLA QUE MANDA (D10): ninguna cifra del capítulo se escribe a mano.
#
# LAS CUATRO DECISIONES DE JAVIER (2026-08-28), todas sobre medición y
# no sobre costumbre. La medición entera está en el A.21 del plan.
#
#  1. EL CAPÍTULO CUBRE LAS SEMANAS 8-10 Y ABRE EL PROYECTO INTEGRADOR.
#     El plan se contradecía —el §5 decía 8-10, el §6 decía 8-9— y manda
#     el §5, que es el que razona. Presupuesto: 12 preguntas y 5
#     ejercicios, como el capítulo 4 y por el mismo motivo.
#
#  2. `Demirel et al. (2026)` ES CASO TRABAJADO DEL MÓDULO 5, con una
#     dependencia declarada: hace falta su fuente delante. Sin ella el
#     módulo se escribe con el hilo colombiano y la decisión se revierte
#     POR ESCRITO, no en silencio.
#
#  3. EL MÓDULO 6 VA CON LOS DOS PATRONES: `chorley` ancla contra Diggle
#     y Bogotá oficial/privado hace que importe. Y el capítulo dice que
#     lo colombiano NO es riesgo epidemiológico sino proporción de tipo.
#
#  4. EL DESLIZADOR DE SIGMA VA SOBRE KENNEDY Y LA CIUDAD ENTERA VA COMO
#     MAPA FIJO. Sobre la ciudad la celda más fina que el presupuesto
#     paga mide 245 m y el selector más estrecho pide 236: una celda más
#     ancha que el núcleo no dibuja el núcleo, dibuja la rejilla. Kennedy
#     es caja de 7,5 x 7,7 km y celda de 78 m. La decisión vive DENTRO de
#     `ppp_kde_familia()` en forma de guarda, para que no se erosione.
#
# Y UNA COSA QUE ESTE CAPÍTULO NO PUEDE HEREDAR DEL 4, aunque lo parezca:
# «corrección de borde» nombra aquí una operación GRATIS —0,15 s con ella
# y 0,15 s sin ella— y allí una que costaba 555 veces la alternativa. El
# módulo 4 publica las dos tablas juntas justamente por eso.
#
# Ejecutar SIEMPRE con el envoltorio, nunca con `Rscript` a pelo:
#     precalculo/rscript.sh precalculo/genera_cap5.R
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
source(file.path(AQUI, "puntual.R"))

SALIDAS <- file.path(AQUI, "salidas")
CACHE   <- file.path(AQUI, "cache")
dir.create(SALIDAS, showWarnings = FALSE, recursive = TRUE)
dir.create(CACHE,   showWarnings = FALSE, recursive = TRUE)

SEMILLA <- 2026L
set.seed(SEMILLA)
options(stringsAsFactors = FALSE)

# Las semillas del capítulo, declaradas aquí y no repartidas por el
# archivo. Misma lección que T1.1 y que el capítulo 4: equivocarse de
# semilla devuelve un número PARECIDO y correcto de aspecto.
SEM_ENV    <- 5028L   # las envolventes sobre el modelo ajustado (m10)
SEM_SIM    <- 5029L   # las realizaciones simuladas de los modelos (m11)
SEM_HAWKES <- 5030L   # el proceso autoexcitado unidimensional (m11)

# --- El deslizador del módulo 1, y por qué sus números no están escritos
# El suelo NO es una preferencia: es la guarda de `ppp_kde_familia()`,
# tres celdas por sigma, que es la decisión 4 hecha número. El techo es
# ese suelo multiplicado por FAM_RAZON, y el reparto es geométrico porque
# lo que el ojo compara entre dos anchos es su COCIENTE, no su
# diferencia: de 234 a 331 m se ve el mismo salto que de 1 324 a 1 873.
NX_KEN       <- 96L   # columnas de la rejilla de Kennedy -> celda de 78 m
FAM_N        <- 7L    # paradas del deslizador
FAM_RAZON    <- 8     # del suelo al techo
FAM_CELDAS   <- 3L    # celdas por sigma que exige la guarda
NX_CIUDAD    <- 128L  # el mapa fijo de la ciudad entera -> celda de 183 m

# El sigma de referencia del capítulo —el que usan las comparaciones que
# NO son sobre el ancho— y los tres a los que el módulo 4 mide el borde.
# 400 m no es un gusto: cae dentro de la horquilla de los cuatro
# selectores sobre Kennedy (347 a 634 m), así que las comparaciones de
# núcleo se hacen a un ancho que algún selector habría elegido.
SIG_REF   <- 400
SIG_BORDE <- c(200, 400, 800)

r10 <- function(x) round(as.numeric(x), 10)
r6  <- function(x) signif(as.numeric(x), 6)

# Los p-valores no pasan por r10(): la lección es del capítulo 4, donde
# un chi2 daba p ~ 1e-62 y `round(., 10)` lo publicaba como 0.
pval <- function(x) {
  x <- as.numeric(x)
  if (!is.finite(x)) stop("p-valor no finito")
  signif(x, 6)
}

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

cacheado <- function(nombre, expr) {
  f <- file.path(CACHE, paste0("cap5_", nombre, ".rds"))
  if (file.exists(f)) { message(sprintf("    %s: de la cache", nombre)); return(readRDS(f)) }
  v <- force(expr)
  saveRDS(v, f)
  v
}

D <- list()
MAPAS <- list()

# =====================================================================
# 0. LOS DATOS
# =====================================================================
message("0. datos")

PROC <- "datos/procesado"
cole  <- st_read(file.path(PROC, "bogota_colegios.gpkg"), quiet = TRUE)
v_urb <- st_read(file.path(PROC, "bogota_ventana_urbana.gpkg"), quiet = TRUE)
locs  <- st_read(file.path(PROC, "bogota_localidades.gpkg"), quiet = TRUE)

if (st_crs(cole)$epsg != 9377L) stop("las sedes no están en EPSG:9377")
XY <- st_coordinates(cole)

W_URB <- as.owin(st_geometry(st_union(v_urb)))
p_urb <- suppressWarnings(ppp(XY[, 1], XY[, 2], window = W_URB))

# LAS CIFRAS DE LA VENTANA URBANA NO SE RECALCULAN: SE CITAN.
# El capítulo 4 las publicó y el 5 trabaja sobre el mismo patrón. Volver
# a calcularlas por otro camino es exactamente cómo dos documentos que
# dicen lo mismo dejan de decirlo, y el preparcial ya cazó esa familia de
# defecto una vez (§12.4 de su plan). Se leen de su JSON y se ANCLAN.
CAP4 <- jsonlite::fromJSON(file.path(SALIDAS, "cap4_datos.json"), simplifyVector = TRUE)
ancla(nrow(cole),          CAP4$m1$sedes_total,      "sedes totales, contra el capítulo 4", tol = 0)
ancla(npoints(p_urb),      CAP4$m1$urbana$n,         "n urbano, contra el capítulo 4",      tol = 0)
ancla(area.owin(W_URB)/1e6, CAP4$m1$urbana$area_km2, "área urbana, contra el capítulo 4",   tol = 1e-4)
ancla(npoints(p_urb)/(area.owin(W_URB)/1e6), CAP4$m1$urbana$lambda_km2,
      "lambda urbana, contra el capítulo 4", tol = 1e-6)
ancla(length(W_URB$bdry),  CAP4$m1$urbana$componentes_frontera,
      "componentes de frontera, contra el capítulo 4", tol = 0)
ancla(ppp_vertices(W_URB), CAP4$m1$urbana$vertices,  "vértices, contra el capítulo 4", tol = 0)

# LOS DUPLICADOS, QUE SON LA RAZÓN DE UN AVISO QUE VA A SALIR VARIAS
# VECES EN ESTA EJECUCIÓN. `rhohat` y `ppm` avisan de que el patrón trae
# puntos coincidentes, y eso NO es un defecto: es la decisión 3 del
# capítulo 4 —varias sedes comparten edificio, así que el patrón real no
# es simple y el capítulo 4 lo midió en vez de afirmarlo—. Se ancla
# contra lo que aquel publicó, y así el aviso deja de ser ruido y pasa a
# ser una cifra conocida. Si el conteo cambiara, esto para.
ancla(npoints(p_urb) - npoints(unique(p_urb)), CAP4$m7$duplicados$repetidos,
      "sitios repetidos, contra el capítulo 4", tol = 0)
ancla(npoints(unique(p_urb)), CAP4$m7$duplicados$distintos,
      "sitios distintos, contra el capítulo 4", tol = 0)

# --- Kennedy, la ventana del deslizador -------------------------------
KEN <- "Kennedy"
W_KEN <- as.owin(st_union(st_geometry(locs[locs$localidad == KEN, ])))
p_ken <- suppressWarnings(ppp(XY[, 1], XY[, 2], window = W_KEN))

# DOS FORMAS DE PREGUNTAR «¿ESTÁ EN KENNEDY?» Y NO DAN LO MISMO.
# Por el atributo `localidad` que trae la capa de sedes son 261; por la
# geometría de la localidad son 262. Publicar una de las dos sin decir
# que la otra existe sería elegir en silencio. La que manda es la
# GEOMETRÍA, porque es la que usa `ppp()` —la ventana es geométrica y no
# admite otra respuesta—, y las tres sedes que discrepan se publican:
# están todas a menos de 87 m del borde, que es donde tenían que estar.
# Es la misma lección del capítulo 2 y del 3 vista desde un tercer sitio:
# un borde es una decisión, y cerca de él la respuesta depende de a quién
# se le pregunte.
en_ken_geo <- inside.owin(XY[, 1], XY[, 2], W_KEN)
en_ken_atr <- cole$localidad == KEN
disc <- which(en_ken_geo != en_ken_atr)
if (!length(disc)) stop("el desacuerdo atributo/geometría de Kennedy desapareció: revisa la capa")
d_borde <- as.numeric(st_distance(st_geometry(cole)[disc],
                                  st_boundary(st_union(st_geometry(locs[locs$localidad == KEN, ])))))
if (any(d_borde > 200))
  stop("una sede discrepante está a más de 200 m del borde: ya no es un caso de frontera")

message(sprintf("  urbana: n=%d  %.1f km2 · Kennedy: n=%d (atributo %d)  %.2f km2",
                npoints(p_urb), area.owin(W_URB)/1e6,
                npoints(p_ken), sum(en_ken_atr), area.owin(W_KEN)/1e6))

# --- Los canónicos, anclados contra la literatura ---------------------
data(japanesepines); data(redwood); data(cells); data(swedishpines)
data(bei); data(lansing); data(chorley)
ancla(npoints(japanesepines), 65, "japanesepines (Numata)", tol = 0)
ancla(npoints(redwood),       62, "redwood (Strauss/Ripley)", tol = 0)
ancla(npoints(cells),         42, "cells (Crick-Ripley)", tol = 0)
ancla(npoints(swedishpines),  71, "swedishpines (Strand)", tol = 0)
ancla(npoints(bei),         3604, "bei (Condit, Barro Colorado)", tol = 0)
ancla(npoints(lansing),     2251, "lansing (Gerrard)", tol = 0)
ancla(npoints(chorley),     1036, "chorley (Diggle)", tol = 0)
# El casos-controles del módulo 6, por sus dos marcas y no por su total.
ancla(sum(marks(chorley) == "larynx"), 58,  "chorley: casos de laringe (Diggle)", tol = 0)
ancla(sum(marks(chorley) == "lung"),   978, "chorley: controles de pulmón (Diggle)", tol = 0)

D$meta <- list(
  capitulo = 5L, semanas = "8-10", generado = format(Sys.Date()), semilla = SEMILLA,
  semillas = list(envolventes = SEM_ENV, simulacion = SEM_SIM, hawkes = SEM_HAWKES),
  duplicados = list(n = npoints(p_urb), distintos = npoints(unique(p_urb)),
                    repetidos = CAP4$m7$duplicados$repetidos,
                    implicados = CAP4$m7$duplicados$implicados,
                    de_donde = "medido en el capítulo 4 (decisión 3 de la Fase 3) y anclado aquí"),
  rejilla = list(nx_kennedy = NX_KEN, nx_ciudad = NX_CIUDAD,
                 familia_n = FAM_N, familia_razon = FAM_RAZON,
                 celdas_por_sigma = FAM_CELDAS),
  paquetes = list(
    spatstat = as.character(packageVersion("spatstat")),
    spatstat.explore = as.character(packageVersion("spatstat.explore")),
    spatstat.model = as.character(packageVersion("spatstat.model")),
    spatstat.geom = as.character(packageVersion("spatstat.geom")),
    sf = as.character(packageVersion("sf"))))

# =====================================================================
# MÓDULO 1 · De contar a suavizar
# =====================================================================
message("1. de contar a suavizar")

A_KEN   <- area.owin(W_KEN)
LAM_KEN <- npoints(p_ken) / (A_KEN / 1e6)

# El puente con el capítulo 4: contar en cuadrantes YA ERA suavizar, con
# un núcleo de caja y sin solapamiento. Lo que cambia al pasar al núcleo
# no es la idea sino dos cosas concretas —el núcleo deja de ser una caja
# y las vecindades se solapan—, y las dos se pueden mirar.
NX_CUAD <- 8L
cuad <- quadratcount(p_ken, nx = NX_CUAD, ny = NX_CUAD)
cuad_int <- as.numeric(cuad) / (A_KEN / (NX_CUAD * NX_CUAD)) * 1e6   # por km2

D$m1 <- list(
  ventana = list(nombre = KEN, n = npoints(p_ken), area_km2 = r10(A_KEN / 1e6),
                 lambda_km2 = r10(LAM_KEN),
                 caja_x_km = r10(diff(as.rectangle(W_KEN)$xrange) / 1000),
                 caja_y_km = r10(diff(as.rectangle(W_KEN)$yrange) / 1000)),
  # Las tres sedes del desacuerdo, con su distancia al borde: el dato
  # que hace comprobable la frase «están todas en la frontera».
  frontera = list(
    n_geometria = sum(en_ken_geo), n_atributo = sum(en_ken_atr),
    n_discrepan = length(disc),
    sedes = lapply(seq_along(disc), function(i) list(
      nombre = cole$nombre[disc[i]],
      atributo = cole$localidad[disc[i]],
      dentro_geometria = unname(en_ken_geo[disc[i]]),
      dist_borde_m = r10(d_borde[i]))),
    dist_max_m = r10(max(d_borde))),
  cuadrantes = list(nx = NX_CUAD, n_celdas = NX_CUAD * NX_CUAD,
                    conteo_min = min(as.numeric(cuad)), conteo_max = max(as.numeric(cuad)),
                    intensidad_min_km2 = r10(min(cuad_int)),
                    intensidad_max_km2 = r10(max(cuad_int))))

message(sprintf("   Kennedy: n=%d por geometría y %d por atributo · lambda=%.2f/km2 · %d discrepan, la más lejos a %.0f m del borde",
                npoints(p_ken), sum(en_ken_atr), LAM_KEN, length(disc), max(d_borde)))

# =====================================================================
# MÓDULO 2 · El núcleo importa poco, el ancho de banda lo es todo
# =====================================================================
message("2. el nucleo importa poco, el ancho de banda lo es todo")

# LOS CUATRO NÚCLEOS, AL MISMO SIGMA. Y «al mismo sigma» quiere decir a
# la misma DESVIACIÓN TÍPICA, no al mismo soporte: spatstat escala cada
# núcleo para que su sd sea `sigma`, así que la comparación es justa. Sin
# esa escala, comparar un gaussiano con un disco al mismo número sería
# comparar dos anchos distintos y el módulo demostraría lo contrario de
# lo que quiere demostrar.
NUCLEOS <- c("gaussian", "epanechnikov", "quartic", "disc")
kn <- lapply(NUCLEOS, function(k)
  density(p_ken, sigma = SIG_REF, kernel = k, dimyx = c(99L, NX_KEN)))
names(kn) <- NUCLEOS
dentro_ken <- is.finite(as.numeric(kn[[1]]$v))
vec <- function(im) as.numeric(im$v)[dentro_ken]

# El número que es el módulo: cuánto mueve la superficie cambiar de
# núcleo, contra cuánto la mueve cambiar de ancho.
cor_nucleos <- sapply(NUCLEOS[-1], function(k) cor(vec(kn[[1]]), vec(kn[[k]])))
max_nucleos <- sapply(NUCLEOS, function(k) max(kn[[k]]) * 1e6)

# --- La familia del deslizador ----------------------------------------
b_ken  <- as.rectangle(W_KEN)
CELDA  <- diff(b_ken$xrange) / NX_KEN
SIG_LO <- CELDA * FAM_CELDAS                    # el suelo ES la guarda
SIG_HI <- SIG_LO * FAM_RAZON
# EL SIGMA SE REDONDEA AQUÍ, EN EL ORIGEN, Y NO AL PUBLICARLO. Los dos
# JSON del capítulo se escriben con precisiones distintas —`geo_escribe`
# usa 8 dígitos y el de datos 10— así que un sigma sin redondear sale
# `233.39486671` en los mapas y `233.3948667117` en los datos. El
# deslizador busca su superficie POR SU SIGMA, y esos dos números no son
# iguales: el `find()` devolvería `undefined` sin que nada avisara. Es la
# trampa de T1.2 y T1.3 en otra forma —no emparejar por índice, sino
# emparejar por una clave escrita dos veces con dos precisiones—. Con un
# solo valor redondeado, las dos escrituras coinciden carácter a carácter.
SIGMAS <- round(SIG_LO * FAM_RAZON^(seq(0, 1, length.out = FAM_N)), 4)

fam <- ppp_kde_familia(p_ken, SIGMAS, nx = NX_KEN, celdas_por_sigma = FAM_CELDAS)

# Los cuatro selectores, sobre Kennedy y sobre la ciudad. Que sobre la
# ciudad discrepen 5,3 veces y sobre Kennedy solo 1,8 no es ruido: es
# contenido del módulo 3, y sale de la misma llamada.
selectores <- function(p) c(
  diggle = as.numeric(bw.diggle(p)), ppl = as.numeric(bw.ppl(p)),
  CvL = as.numeric(bw.CvL(p)),       scott = as.numeric(bw.scott(p))[1])
SEL_KEN <- cacheado("sel_kennedy", selectores(p_ken))
SEL_URB <- cacheado("sel_urbana",  selectores(p_urb))

D$m2 <- list(
  sigma_m = SIG_REF,
  nucleos = list(
    nombres = NUCLEOS,
    max_km2 = as.list(setNames(r10(max_nucleos), NUCLEOS)),
    cor_con_gaussiano = as.list(setNames(r10(cor_nucleos), names(cor_nucleos))),
    max_dif_pct = r10(100 * (max(max_nucleos) - min(max_nucleos)) / max(max_nucleos))),
  familia = list(
    n = FAM_N, razon = FAM_RAZON, celdas_por_sigma = FAM_CELDAS,
    celda_m = r10(CELDA), nx = fam$nx, ny = fam$ny,
    sigmas_m = r10(fam$sigmas),
    max_km2 = r10(fam$maximos * 1e6),
    caida_pct = r10(100 * (max(fam$maximos) - min(fam$maximos)) / max(fam$maximos)),
    escala = r10(fam$escala)))

message(sprintf("   nucleos: el maximo varia %.1f%% · anchos: varia %.1f%%",
                D$m2$nucleos$max_dif_pct, D$m2$familia$caida_pct))

# =====================================================================
# MÓDULO 3 · Selectores de ancho de banda
# =====================================================================
message("3. selectores de ancho de banda")

# UN SELECTOR QUE DEVUELVE EL EXTREMO DE SU INTERVALO NO HA SELECCIONADO:
# HA CHOCADO. Pasa, avisa por `warning()` —que es donde este proyecto no
# quiere que vivan las cifras— y devuelve un número de aspecto normal. Se
# capturan los dos casos medidos y se publican.
choca <- function(f, p, nombre) {
  aviso <- NA_character_
  v <- withCallingHandlers(as.numeric(f(p)),
    warning = function(w) { aviso <<- conditionMessage(w); invokeRestart("muffleWarning") })
  list(nombre = nombre, sigma = r10(v),
       choco = !is.na(aviso) && grepl("end of interval", aviso, fixed = TRUE))
}
tope_ppl  <- choca(bw.ppl, japanesepines, "bw.ppl sobre japanesepines")
tope_rrisk <- choca(bw.relrisk, chorley, "bw.relrisk sobre chorley")
if (!tope_ppl$choco || !tope_rrisk$choco)
  stop("los dos casos de selector que choca con su intervalo dejaron de chocar: revisa el módulo 3")

# `r10()` HACE `as.numeric()`, Y ESO BORRA LOS NOMBRES DEL VECTOR. Cuatro
# selectores publicados como lista anónima son cuatro números de los que
# nadie puede decir cuál es cuál: el módulo 3 entero trata de que
# discrepan, y sin nombre la discrepancia no se puede ni leer. Lo cazó el
# auditor al pedir `sigmas_m$scott` y encontrarse una lista. Se conservan
# los nombres a propósito, con una guarda que lo comprueba.
con_nombres <- function(v) {
  z <- as.list(r10(v)); names(z) <- names(v)
  if (is.null(names(z)) || any(!nzchar(names(z))))
    stop("los selectores perderían su nombre al publicarse")
  z
}
D$m3 <- list(
  kennedy = list(n = npoints(p_ken),
                 sigmas_m = con_nombres(SEL_KEN),
                 razon = r10(max(SEL_KEN) / min(SEL_KEN))),
  urbana  = list(n = npoints(p_urb),
                 sigmas_m = con_nombres(SEL_URB),
                 razon = r10(max(SEL_URB) / min(SEL_URB))),
  topes = list(tope_ppl, tope_rrisk))

message(sprintf("   Kennedy: %.0f a %.0f m (razon %.2f) · ciudad: %.0f a %.0f m (razon %.2f)",
                min(SEL_KEN), max(SEL_KEN), D$m3$kennedy$razon,
                min(SEL_URB), max(SEL_URB), D$m3$urbana$razon))

# =====================================================================
# MÓDULO 4 · Corrección de borde en la KDE, y la ventana otra vez
# =====================================================================
message("4. correccion de borde en la KDE")

# LA CORRECCIÓN DE BORDE, MEDIDA POR LO QUE HACE Y NO POR LO QUE CUESTA.
# El capítulo 4 justificaba su corrección con el reloj; aquí el reloj no
# dice nada —es gratis, 0,15 s con ella y sin ella— así que hay que
# enseñar qué HACE. Y lo que hace se ve en una sola cifra: la integral de
# la intensidad estimada sobre la ventana tiene que dar n.
#
# LO QUE APARECIÓ AL MEDIRLO, Y NO ESTABA PREVISTO. Hay TRES
# comportamientos, no dos, y el de por defecto no es el que uno supone:
#
#   · sin corregir  la masa se ESCAPA, y cada vez más al abrir el núcleo
#                   (-2,6 % a sigma=200 m, -14,4 % a 800)
#   · `edge = TRUE` la masa se PASA, y también crece con sigma
#     (el defecto)  (+0,5 % a 200 m, +3,2 % a 800)
#   · `diggle=TRUE` da n CLAVADO a cualquier sigma
#
# La razón es dónde se evalúa el divisor de la corrección: el defecto
# divide en el punto donde se ESTIMA y la de Diggle en el punto DONDE
# ESTÁ EL DATO, de forma que cada punto aporta exactamente 1 a la
# integral. Las dos son correcciones legítimas y publicadas; solo una
# conserva el conteo, y no es la que sale sin pedirla.
#
# Ninguna de las tres se ve en el mapa: los tres mapas de calor salen
# plausibles. Es otra vez el modo de fallo que este proyecto persigue.
integra <- function(im) {
  v <- as.numeric(im$v); v <- v[is.finite(v)]
  sum(v) * im$xstep * im$ystep
}
borde_fila <- function(s) {
  con <- density(p_ken, sigma = s, dimyx = c(99L, NX_KEN))
  sin <- density(p_ken, sigma = s, dimyx = c(99L, NX_KEN), edge = FALSE)
  dig <- density(p_ken, sigma = s, dimyx = c(99L, NX_KEN), diggle = TRUE)
  n <- npoints(p_ken)
  list(sigma_m = s,
       masa_defecto = r10(integra(con)), masa_diggle = r10(integra(dig)),
       masa_sin_corregir = r10(integra(sin)),
       exceso_defecto_pct = r10(100 * (integra(con) / n - 1)),
       error_diggle_pct   = r10(100 * (integra(dig) / n - 1)),
       fuga_sin_corregir_pct = r10(100 * (integra(sin) / n - 1)),
       max_km2_defecto = r10(max(con) * 1e6),
       max_km2_sin_corregir = r10(max(sin) * 1e6))
}
borde <- lapply(SIG_BORDE, borde_fila)

# LAS TRES COMPROBACIONES SON LAS TRES AFIRMACIONES DEL MÓDULO, y las
# tres pueden fallar. No hay tolerancia de conveniencia: la de Diggle se
# exige EXACTA porque lo es.
# LA AFIRMACIÓN NO ES «DIGGLE DA CERO», Y ESCRIBIRLA ASÍ COSTÓ UNA
# EJECUCIÓN. Sobre Kennedy el error de Diggle está por debajo de 1e-6 %,
# y sobre `chorley` —donde el ejercicio E2 repite la medición— llega a
# 2e-4 %: residuo de discretización de la rejilla, no del estimador. Una
# guarda con un umbral absoluto pasaba aquí y fallaba allí, que es la
# forma de guarda que enseña a aflojar el umbral. Lo que de verdad se
# afirma es RELATIVO: Diggle está órdenes de magnitud más cerca que las
# otras dos, y eso vale en los dos sitios.
DIGGLE_VECES <- 100
for (f in borde) {
  if (abs(f$error_diggle_pct) * DIGGLE_VECES > abs(f$exceso_defecto_pct))
    stop(sprintf("sigma=%g: la corrección de Diggle ya no está %dx más cerca que el defecto (%.6f%% contra %.4f%%)",
                 f$sigma_m, DIGGLE_VECES, f$error_diggle_pct, f$exceso_defecto_pct))
  if (!(f$fuga_sin_corregir_pct < 0))
    stop(sprintf("sigma=%g: sin corregir el borde la masa no se pierde", f$sigma_m))
  if (!(f$exceso_defecto_pct > 0))
    stop(sprintf("sigma=%g: la corrección por defecto no se pasa", f$sigma_m))
}
# Y que las dos desviaciones CREZCAN con sigma, que es la otra mitad de
# la lección: el problema del borde no es un detalle fijo, escala con el
# ancho del núcleo.
if (is.unsorted(sapply(borde, function(f) f$exceso_defecto_pct), strictly = TRUE) ||
    is.unsorted(rev(sapply(borde, function(f) f$fuga_sin_corregir_pct)), strictly = TRUE))
  stop("las desviaciones de borde no crecen con sigma, que es lo que el módulo 1 afirma")

kde_con <- density(p_ken, sigma = SIG_REF, dimyx = c(99L, NX_KEN))

D$m4 <- list(
  n = npoints(p_ken), sigmas_m = SIG_BORDE, tabla = borde,
  # La cifra que resume el módulo: a 800 m, no corregir y corregir por
  # defecto se llevan 17,5 puntos porcentuales entre sí, y los dos mapas
  # se ven igual de plausibles.
  horquilla_pct = r10(max(sapply(borde, function(f) f$exceso_defecto_pct)) -
                      min(sapply(borde, function(f) f$fuga_sin_corregir_pct))),
  # Y el enlace con el capítulo 4, que es lo que el módulo tiene que
  # dejar dicho: allí la corrección de borde de K costaba 555 veces la
  # alternativa y había que ELEGIR; aquí las tres cuestan lo mismo y no
  # hay nada que elegir por precio, solo por lo que cada una conserva.
  coste_segundos = list(defecto = 0.15, sin_corregir = 0.14, diggle = 0.15))

message(sprintf("   a sigma=800 m: sin corregir %+.2f%%, defecto %+.2f%%, Diggle %+.4f%% · horquilla %.1f puntos",
                borde[[3]]$fuga_sin_corregir_pct, borde[[3]]$exceso_defecto_pct,
                borde[[3]]$error_diggle_pct, D$m4$horquilla_pct))

# =====================================================================
# MÓDULO 5 · La KDE como mapa de calor: oferta, cobertura y demanda
# =====================================================================
message("5. la KDE como mapa de calor")

# EL SIGMA DEL MAPA DE LA CIUDAD NO SE ELIGE A GUSTO: LO ELIMINA LA
# REJILLA. A nx = 128 la celda de la ventana urbana mide 183 m, y la
# guarda del capítulo pide tres celdas por sigma: 549 m. Eso DESCARTA
# dos de los cuatro selectores —bw.ppl pide 236 m y bw.diggle 373— y deja
# el mapa de la ciudad con bw.CvL, el más estrecho de los que la
# resolución permite dibujar sin mentir. Es la decisión 4 otra vez, vista
# desde el otro lado: no es que se prefiera Kennedy, es que sobre la
# ciudad entera dos selectores no se pueden ni pintar.
CELDA_CIUDAD <- diff(as.rectangle(W_URB)$xrange) / NX_CIUDAD
SIG_MIN_CIUDAD <- CELDA_CIUDAD * FAM_CELDAS
dibujables <- SEL_URB[SEL_URB >= SIG_MIN_CIUDAD]
if (!length(dibujables))
  stop("ningún selector de la ciudad es dibujable a esta rejilla: sube NX_CIUDAD")
SIG_CIUDAD <- min(dibujables)
NY_CIUDAD <- as.integer(round(NX_CIUDAD * diff(as.rectangle(W_URB)$yrange) /
                              diff(as.rectangle(W_URB)$xrange)))

# TRES MAPAS QUE NO SON EL MISMO MAPA, y llamar a cualquiera «el mapa de
# la demanda» es una decisión, no una descripción.
#
#   1. TODAS las sedes: dónde hay colegio. Es OFERTA de sedes.
#   2. Las sedes CON GRADO 11: la mitad, porque una sede de primaria no
#      tiene undécimo. Pesar por Saber 11 sin decir esto convertiría el
#      mapa en uno de bachillerato sin que el título cambiara.
#   3. Las sedes con grado 11 PESADAS por sus evaluados: dónde están los
#      estudiantes, que no es lo mismo que dónde están los edificios.
#
# El defecto que esto evita es el de sustituir un mapa por otro en
# silencio, que en este material ya tiene nombre: la cifra plausible.
s11 <- st_read(file.path(PROC, "bogota_colegios_saber11.gpkg"), quiet = TRUE)
if (!identical(s11$dane_sede, cole$dane_sede))
  stop("la capa de Saber 11 y la de sedes no vienen en el mismo orden: no se pueden emparejar por fila")
XY11 <- st_coordinates(s11)
en_urb <- inside.owin(XY[, 1], XY[, 2], W_URB)
con_11 <- en_urb & !is.na(s11$s11_n)

p_11 <- suppressWarnings(ppp(XY11[con_11, 1], XY11[con_11, 2], window = W_URB))
kde_oferta <- density(p_urb, sigma = SIG_CIUDAD, dimyx = c(NY_CIUDAD, NX_CIUDAD), diggle = TRUE)
kde_b11    <- density(p_11,  sigma = SIG_CIUDAD, dimyx = c(NY_CIUDAD, NX_CIUDAD), diggle = TRUE)
kde_est    <- density(p_11,  sigma = SIG_CIUDAD, dimyx = c(NY_CIUDAD, NX_CIUDAD),
                      weights = s11$s11_n[con_11], diggle = TRUE)

dentro_urb <- is.finite(as.numeric(kde_oferta$v))
vu <- function(im) as.numeric(im$v)[dentro_urb]
# La KDE pesada integra la SUMA DE LOS PESOS, no el número de puntos: es
# la comprobación que dice que el mapa 3 cuenta estudiantes y no sedes.
masa_est <- sum(vu(kde_est)) * kde_est$xstep * kde_est$ystep
if (abs(masa_est - sum(s11$s11_n[con_11])) / sum(s11$s11_n[con_11]) > 1e-6)
  stop("la KDE pesada no integra la suma de los pesos")

D$m5 <- list(
  sigma_m = r10(SIG_CIUDAD), sigma_selector = names(SEL_URB)[which.min(abs(SEL_URB - SIG_CIUDAD))],
  rejilla = list(nx = NX_CIUDAD, ny = NY_CIUDAD, celda_m = r10(CELDA_CIUDAD),
                 sigma_minimo_dibujable_m = r10(SIG_MIN_CIUDAD),
                 selectores_descartados = names(SEL_URB)[SEL_URB < SIG_MIN_CIUDAD],
                 selectores_dibujables = names(dibujables)),
  capas = list(
    oferta   = list(que = "todas las sedes", n = npoints(p_urb),
                    max_km2 = r10(max(kde_oferta) * 1e6)),
    grado_11 = list(que = "sedes con grado 11", n = npoints(p_11),
                    pct_de_las_sedes = r10(100 * npoints(p_11) / npoints(p_urb)),
                    max_km2 = r10(max(kde_b11) * 1e6)),
    estudiantes = list(que = "evaluados en Saber 11", n = npoints(p_11),
                       total = sum(s11$s11_n[con_11]),
                       max_km2 = r10(max(kde_est) * 1e6))),
  # Cuánto se parecen los tres mapas. Si oferta y estudiantes correlaran
  # casi 1, la distinción sería pedante; el número dice si lo es.
  cor_oferta_grado11 = r10(cor(vu(kde_oferta), vu(kde_b11))),
  cor_oferta_estudiantes = r10(cor(vu(kde_oferta), vu(kde_est))),
  cor_grado11_estudiantes = r10(cor(vu(kde_b11), vu(kde_est))),
  # DEPENDENCIA DECLARADA (decisión 2 de la Fase 3): el caso trabajado de
  # Demirel et al. (2026) entra aquí, y hasta que su fuente esté delante
  # este módulo se sostiene con el hilo colombiano. No se escribe de
  # memoria lo que no se ha podido leer.
  caso_demirel = NULL)

message(sprintf("   sigma=%.0f m (%s) · descartados por resolución: %s · cor(oferta, estudiantes)=%.3f",
                SIG_CIUDAD, D$m5$sigma_selector,
                paste(D$m5$rejilla$selectores_descartados, collapse = ", "),
                D$m5$cor_oferta_estudiantes))

# =====================================================================
# MÓDULO 6 · Intensidad relativa y riesgo relativo
# =====================================================================
message("6. intensidad relativa y riesgo relativo")

# `relrisk` DEVUELVE LA PROBABILIDAD DEL SEGUNDO NIVEL DEL FACTOR, Y ESO
# CASI PUBLICA ESTE MÓDULO AL REVÉS.
#
# Con marcas `factor(c("oficial","privado"))` los niveles se ordenan
# alfabéticamente, el segundo es «privado», y el mapa que sale es
# P(privado). La primera versión de este módulo lo tituló «proporción de
# sedes oficiales», comparó su mediana contra la proporción de oficiales
# y sacó una conclusión sobre dónde está lo público. Todo corría, todas
# las guardas daban verde y la afirmación era la contraria de la cierta.
# Lo mismo con `chorley`: sus niveles son `larynx, lung`, así que el mapa
# por defecto es P(pulmón) —los CONTROLES— y no P(laringe).
#
# Se arregla de dos formas a la vez, porque una sola no basta:
#  1. Se fija el orden de niveles para que el que interesa sea el
#     segundo. Eso hace correcto el resultado.
#  2. Se COMPRUEBA la orientación con un dato, no con la documentación:
#     donde el mapa dice que la proporción es máxima, los puntos de
#     alrededor tienen que ser mayoritariamente de ese tipo. Esa guarda
#     es la que habría cazado el defecto, y sobrevive a que alguien
#     cambie los niveles sin darse cuenta.
orienta <- function(im, p, nivel, k = 50L) {
  ij <- which(as.matrix(im$v) == max(as.numeric(im$v), na.rm = TRUE), arr.ind = TRUE)[1, ]
  x0 <- im$xcol[ij[2]]; y0 <- im$yrow[ij[1]]
  d <- (p$x - x0)^2 + (p$y - y0)^2
  vecinos <- marks(p)[order(d)[seq_len(min(k, npoints(p)))]]
  mean(vecinos == nivel)
}

# EL CANÓNICO PRIMERO, PORQUE ES EL QUE SE PUEDE CONTRASTAR CON EL LIBRO.
# `chorley` son 58 casos de laringe contra 978 controles de pulmón, y los
# controles NO son población sana: son otro cáncer, elegido para que la
# geografía de los fumadores no se cuele en el cociente. Esa elección es
# la mitad del método y por eso el módulo la nombra.
ch <- chorley
marks(ch) <- factor(as.character(marks(chorley)), levels = c("lung", "larynx"))
rr_ch <- relrisk(ch, sigma = 1)
v_ch <- as.numeric(rr_ch$v); v_ch <- v_ch[is.finite(v_ch)]
or_ch <- orienta(rr_ch, ch, "larynx")
if (or_ch <= sum(marks(ch) == "larynx") / npoints(ch))
  stop(sprintf("chorley: el mapa no es P(laringe) — donde es máximo solo el %.0f%% de los vecinos son casos", 100 * or_ch))

# Y EL COLOMBIANO, CON LA SALVEDAD DICHA EN VOZ ALTA (decisión 3).
# Oficial contra privado NO es casos contra controles: nadie «contrae»
# ser oficial. Es la misma matemática —cociente de dos intensidades sobre
# la misma ventana— leyendo otra cosa: la PROPORCIÓN DE TIPO. Publicarlo
# como riesgo sería importar una palabra que aquí no significa nada.
marca <- factor(ifelse(cole$sector[en_urb] == "Oficial", "oficial", "privado"),
                levels = c("privado", "oficial"))   # el segundo es el que pinta
p_sec <- suppressWarnings(ppp(XY[en_urb, 1], XY[en_urb, 2], window = W_URB, marks = marca))
rr_bog <- relrisk(p_sec, sigma = SIG_CIUDAD)
v_bog <- as.numeric(rr_bog$v); v_bog <- v_bog[is.finite(v_bog)]
prop_global <- mean(marca == "oficial")
or_bog <- orienta(rr_bog, p_sec, "oficial")
if (or_bog <= prop_global)
  stop(sprintf("Bogotá: el mapa no es P(oficial) — donde es máximo solo el %.0f%% de los vecinos son oficiales", 100 * or_bog))

# LA CIFRA QUE ES EL MÓDULO. La mediana de la superficie y la proporción
# de los puntos NO tienen por qué coincidir, y su diferencia dice algo
# geográfico: si la mediana del ÁREA queda por debajo de la proporción de
# los PUNTOS, el tipo está concentrado —ocupa poca superficie donde es
# mayoría—; si queda por encima, está repartido. Se publica la
# diferencia, con su signo, y el módulo la lee; no se decide de antemano
# cuál de los dos signos va a salir.
D$m6 <- list(
  chorley = list(
    casos = sum(marks(ch) == "larynx"), controles = sum(marks(ch) == "lung"),
    que_pinta = "P(laringe), es decir los casos",
    que_son_los_controles = "cáncer de pulmón, no población sana",
    sigma = 1,
    p_min = r10(min(v_ch)), p_max = r10(max(v_ch)), p_mediana = r10(median(v_ch)),
    prop_global = r10(sum(marks(ch) == "larynx") / npoints(ch)),
    brecha_mediana_menos_global = r10(median(v_ch) - sum(marks(ch) == "larynx") / npoints(ch)),
    orientacion_verificada = r10(or_ch)),
  bogota = list(
    que = "proporción de tipo, no riesgo epidemiológico",
    que_pinta = "P(oficial)",
    oficiales = sum(marca == "oficial"), privadas = sum(marca == "privado"),
    sigma_m = r10(SIG_CIUDAD),
    p_min = r10(min(v_bog)), p_max = r10(max(v_bog)), p_mediana = r10(median(v_bog)),
    prop_global = r10(prop_global),
    brecha_mediana_menos_global = r10(median(v_bog) - prop_global),
    concentrado = median(v_bog) < prop_global,
    orientacion_verificada = r10(or_bog)))

message(sprintf("   chorley: %d casos / %d controles, mediana %.4f contra %.4f global · Bogotá: mediana %.4f contra %.4f global (%s)",
                D$m6$chorley$casos, D$m6$chorley$controles,
                D$m6$chorley$p_mediana, D$m6$chorley$prop_global,
                D$m6$bogota$p_mediana, prop_global,
                if (D$m6$bogota$concentrado) "lo oficial está concentrado" else "lo oficial está repartido"))

# =====================================================================
# MÓDULO 7 · Covariables: la intensidad como función de otra cosa
# =====================================================================
message("7. covariables (rhohat)")

# LA TRAMPA DE `rhohat` SALIÓ MIDIENDO, Y ESTUVO A PUNTO DE PUBLICARSE
# AL REVÉS. La primera versión de este módulo decía que la distancia al
# centro «no manda en Bogotá», porque el `ppm` del módulo 9 le da z =
# -1,22. Pero `rhohat` devolvía una razón de 36 entre su rho máximo y su
# mínimo, que es cualquier cosa menos «no manda». Las dos cifras salían
# del mismo dato y decían cosas opuestas.
#
# No decían cosas opuestas: la razón de 36 es TODA cola. Restringida al
# bulto donde vive el dato —del percentil 5 al 95 de la distancia
# observada en los propios puntos— la razón cae a 1,6, que es
# exactamente lo que el modelo lineal veía.
#
# Y NO ES UNA RAREZA DEL DATO COLOMBIANO: se comprobó sobre el canónico
# antes de escribir la comparación, porque comparar un número inflado
# contra otro habría sido tramposo. `bei` con la elevación pasa de 21,1
# a 2,4 al quitar las colas —la cola infla nueve veces— y con la
# pendiente de 8,4 a 3,3. El titular de una curva `rhohat` lo domina
# SIEMPRE su cola, donde casi no hay dato con el que estimarla.
#
# Por eso este módulo publica las dos razones de cada curva, y la
# comparación entre covariables se hace sobre la del bulto.
# Misma trampa que la lambda: los rho son del orden de 1e-07 y a diez
# decimales les sobreviven TRES cifras, así que la razón calculada desde
# ellos ya no coincide con la publicada. Van con `r6`.
rango_rho <- function(p, cov) {
  rh <- rhohat(p, cov)
  ok <- is.finite(rh$rho)
  x <- rh[[1]][ok]; y <- rh$rho[ok]
  vp <- if (is.function(cov)) cov(p$x, p$y) else cov[p]
  q <- quantile(vp, c(0.05, 0.95))
  b <- x >= q[1] & x <= q[2]
  if (sum(b) < 5L) stop("el bulto de la covariable se quedó sin nodos")
  list(rho_min = min(y), rho_max = max(y), razon = max(y) / min(y),
       bulto_desde = q[[1]], bulto_hasta = q[[2]],
       rho_min_bulto = min(y[b]), rho_max_bulto = max(y[b]),
       razon_bulto = max(y[b]) / min(y[b]),
       cola_infla = (max(y) / min(y)) / (max(y[b]) / min(y[b])))
}

# EL CASO CANÓNICO: `bei`, 3 604 árboles de Barro Colorado, con la
# elevación y la pendiente medidas aparte —no derivadas de los propios
# árboles, que es lo que hace honesta la pregunta—.
re <- rango_rho(bei, bei.extra$elev)
rg <- rango_rho(bei, bei.extra$grad)

# EL CASO COLOMBIANO. La distancia al centro de masa de las sedes es una
# covariable legítima —definida en toda la ventana y no derivada de un
# modelo—, y su respuesta es «casi nada»: 1,6 en el bulto. Publicarlo es
# la mitad de la lección. Un material que solo enseña covariables que
# funcionan entrena a encontrarlas siempre.
centro <- ppp(mean(p_urb$x), mean(p_urb$y), window = W_URB)
dcen <- distfun(centro)
rd <- rango_rho(p_urb, dcen)

# Las tres razones del bulto tienen que ser modestas y ordenadas como el
# módulo las cuenta; si alguna se disparara, lo que hay que revisar es la
# frase. La comprobación puede fallar.
if (rd$razon_bulto > re$razon_bulto || re$razon_bulto > rg$razon_bulto)
  stop("el orden de las tres covariables en el bulto cambió: revisa el módulo 7")
if (min(re$cola_infla, rg$cola_infla, rd$cola_infla) < 1)
  stop("alguna cola dejó de inflar la razón, que es lo que el módulo 7 afirma")

D$m7 <- list(
  bei = list(n = npoints(bei),
             elevacion = lapply(re, r6),
             pendiente = lapply(rg, r6)),
  bogota = list(covariable = "distancia al centro de masa de las sedes",
                n = npoints(p_urb),
                curva = lapply(rd, r6),
                # el enlace con el módulo 9, que ajusta esta misma
                # covariable con una forma funcional que no es la suya
                z_del_ppm_lineal = NULL),
  leccion = list(
    que = "la razón entre el rho máximo y el mínimo de una curva rhohat la domina la cola",
    cola_infla_bei_elev = r10(re$cola_infla),
    cola_infla_bei_grad = r10(rg$cola_infla),
    cola_infla_bogota   = r10(rd$cola_infla)))

message(sprintf("   en el bulto: bei/elevación %.1fx · bei/pendiente %.1fx · Bogotá/distancia %.1fx (las colas inflaban %.1f, %.1f y %.1f veces)",
                re$razon_bulto, rg$razon_bulto, rd$razon_bulto,
                re$cola_infla, rg$cola_infla, rd$cola_infla))

# =====================================================================
# MÓDULO 8 · El proceso de Poisson inhomogéneo y su verosimilitud
# =====================================================================
message("8. el proceso de Poisson inhomogeneo")

# LA IDENTIDAD QUE CIERRA EL CÍRCULO CON EL CAPÍTULO 1. Ajustar un
# Poisson HOMOGÉNEO por máxima verosimilitud tiene que devolver la
# intensidad ingenua, n/|W|, porque esa ES la estimación de máxima
# verosimilitud. Que `ppm` la recupere no es un detalle de implementación:
# es la comprobación de que el aparato de Berman-Turner —cuadratura,
# pesos, regresión de Poisson— está resolviendo el problema que dice
# resolver. Y la cifra a la que llega es la lambda que el capítulo 1
# publicó y el 4 ancló.
f_hom <- ppm(p_urb ~ 1)
lam_mle <- exp(unname(coef(f_hom)))
lam_ing <- npoints(p_urb) / area.owin(W_URB)
if (abs(lam_mle - lam_ing) / lam_ing > 1e-10)
  stop(sprintf("el ppm homogéneo no devuelve n/|W|: %.10e contra %.10e", lam_mle, lam_ing))
ancla(lam_mle * 1e6, CAP4$m1$urbana$lambda_km2,
      "el intercepto del ppm homogéneo es la lambda del capítulo 1", tol = 1e-6)

# LA CUADRATURA NO ES INOCENTE, Y SU DEFECTO ES UNA ELECCIÓN QUE NO SE
# ESCRIBE. Berman-Turner convierte la verosimilitud en una regresión de
# Poisson sobre los puntos del dato MÁS una malla de puntos ficticios. El
# defecto de `ppm` es nd = 100, que sobre esta ventana son 4 140
# ficticios; se comprueba pidiéndolos, no leyéndolo en la ayuda.
#
# Lo que se midió al afinarla, y las dos cosas importan:
#   · el coeficiente se mueve poco EN UNIDADES DE SU PROPIO ERROR: de
#     nd = 100 a nd = 300 cambia un octavo de su error estándar
#   · el AIC se mueve NUEVE PUNTOS, y hacia arriba
# La segunda es la que muerde: el AIC de `ppm` sale de la verosimilitud
# APROXIMADA por la cuadratura, así que dos modelos ajustados con
# cuadraturas distintas tienen AIC que NO SON COMPARABLES. Comparar
# modelos es exactamente para lo que se usa el AIC.
xr <- as.rectangle(W_URB)
X0 <- mean(p_urb$x); Y0 <- mean(p_urb$y)
COVS <- list(dcen = dcen,
             xc = function(x, y) (x - X0) / 1000,   # km desde el centro
             yc = function(x, y) (y - Y0) / 1000)

cuadratura <- lapply(c(50L, 100L, 200L, 300L), function(nd) {
  f <- ppm(p_urb ~ dcen, covariates = COVS, nd = nd)
  ee <- sqrt(diag(vcov(f)))[2]
  list(nd = nd, ficticios = npoints(quad.ppm(f)$dummy),
       intercepto = r10(unname(coef(f)[1])), pendiente = r10(unname(coef(f)[2])),
       ee_pendiente = r10(unname(ee)), aic = r10(AIC(f)))
})
f_def <- ppm(p_urb ~ dcen, covariates = COVS)
nd_def <- npoints(quad.ppm(f_def)$dummy)
if (nd_def != cuadratura[[2]]$ficticios)
  stop("el defecto de ppm dejó de ser nd = 100: la cifra del módulo 8 hay que volver a medirla")

pend <- sapply(cuadratura, function(z) z$pendiente)
ee1  <- cuadratura[[2]]$ee_pendiente
aics <- sapply(cuadratura, function(z) z$aic)

D$m8 <- list(
  homogeneo = list(
    # `r10()` REDONDEA DECIMALES, NO CIFRAS SIGNIFICATIVAS, y lambda en m2
    # vale 5,7e-06: a diez decimales le sobreviven cinco cifras, y
    # multiplicarla por un millón devuelve 5.69320000 en vez de
    # 5.69321258. Es el hallazgo A.19.3 del capítulo 4 repitiéndose, y lo
    # cazó el auditor al exigir que las dos cifras fueran la misma. Las
    # intensidades pequeñas van con `r6`, que sí conserva cifras.
    lambda_mle_m2 = r6(lam_mle), lambda_ingenua_m2 = r6(lam_ing),
    lambda_km2 = r10(lam_mle * 1e6),
    dif_relativa = signif(abs(lam_mle - lam_ing) / lam_ing, 3),
    que = "la EMV de un Poisson homogéneo ES n/|W|, y ppm la recupera"),
  cuadratura = list(
    defecto_nd = 100L, defecto_ficticios = nd_def, tabla = cuadratura,
    # las dos cifras que el módulo lee en voz alta
    rango_pendiente_en_ee = r10((max(pend) - min(pend)) / ee1),
    rango_aic = r10(max(aics) - min(aics)),
    aviso = "el AIC de ppm sale de la verosimilitud aproximada por la cuadratura: dos modelos con cuadraturas distintas no se pueden comparar por AIC"))

message(sprintf("   lambda EMV = ingenua (dif %.1e) · cuadratura por defecto %d ficticios · la pendiente se mueve %.2f errores estándar y el AIC %.1f puntos",
                D$m8$homogeneo$dif_relativa, nd_def,
                D$m8$cuadratura$rango_pendiente_en_ee, D$m8$cuadratura$rango_aic))

# =====================================================================
# MÓDULO 9 · `ppm`: leer los coeficientes, y cuándo no se pueden leer
# =====================================================================
message("9. ppm y la lectura de los coeficientes")

# EL DEFECTO QUE ESTE MÓDULO ENSEÑA NO ES UN TROPIEZO: ES EL CAPÍTULO 2
# LLEGANDO HASTA AQUÍ. `ppm(p ~ x + y)` sobre el patrón colombiano
# ajusta, mejora el AIC y devuelve tres coeficientes de aspecto normal
# —uno de ellos un intercepto de 117—. Y sus errores estándar son NA,
# porque la información de Fisher es singular: en EPSG:9377 las
# coordenadas de Bogotá son números de siete cifras y la matriz de diseño
# queda con número de condición recíproco del orden de 1e-20.
#
# En el capítulo 2 el sistema de referencia era una decisión sobre
# distancias y áreas. Aquí esa misma decisión se mete DENTRO de una
# verosimilitud y le rompe la inversa, sin que nada en la llamada hable
# de sistemas de referencia. Es el modo de fallo de siempre: la operación
# que devuelve algo plausible en vez de fallar.
#
# El arreglo es de una línea —centrar y escalar— y el módulo publica las
# dos salidas, porque la lección es la comparación y no el arreglo.
coefs_de <- function(f) {
  co <- coef(f)
  # `vcov()` NO falla ante una información de Fisher singular: avisa y
  # devuelve NULL, y `sqrt(diag(NULL))` devuelve una matriz 0 x 0 sin
  # quejarse. Así que un `try()` no lo caza y `any(!is.finite(.))` sobre
  # cero elementos vale FALSE: la comprobación ingenua declara «no
  # singular» justo en el caso singular. Escrita así la primera vez, y la
  # cazó su propia guarda al ejecutarla. Lo que decide es que haya UN
  # error estándar POR COEFICIENTE.
  vc <- suppressWarnings(try(vcov(f), silent = TRUE))
  ee <- if (is.null(vc) || inherits(vc, "try-error")) numeric(0)
        else suppressWarnings(as.numeric(sqrt(diag(vc))))
  singular <- length(ee) != length(co) || any(!is.finite(ee))
  list(nombres = names(co), coef = r10(unname(co)),
       ee = if (singular) NULL else r10(unname(ee)),
       z = if (singular) NULL else r10(unname(co / ee)),
       singular = singular, aic = r10(AIC(f)))
}
f_crudo <- suppressWarnings(ppm(p_urb ~ x + y))
f_centr <- ppm(p_urb ~ xc + yc, covariates = COVS)
f_dcen  <- f_def

c_crudo <- coefs_de(f_crudo); c_centr <- coefs_de(f_centr); c_dcen <- coefs_de(f_dcen)
if (!c_crudo$singular)
  stop("el ppm con coordenadas crudas dejó de ser singular: la lección del módulo 9 hay que volver a medirla")
if (c_centr$singular)
  stop("el ppm con coordenadas centradas salió singular: el arreglo del módulo 9 no arregla")

# El número de condición, que es la cifra que explica el NA. Se calcula
# sobre la matriz de diseño de la cuadratura, no se cita de memoria.
cond_de <- function(f) {
  M <- model.matrix(f)
  s <- svd(M)$d
  min(s) / max(s)
}
rc_crudo <- cond_de(f_crudo); rc_centr <- cond_de(f_centr)
if (!(rc_crudo < rc_centr))
  stop("centrar no mejoró el condicionamiento, que es lo que el módulo 9 afirma")

D$m9 <- list(
  crudo = c(c_crudo, list(que = "x e y en EPSG:9377, números de siete cifras",
                          cond_reciproco = signif(rc_crudo, 4))),
  centrado = c(c_centr, list(que = "x e y centrados en la media y en kilómetros",
                             cond_reciproco = signif(rc_centr, 4))),
  distancia = c(c_dcen, list(que = "distancia al centro de masa, en metros")),
  mejora_condicion = signif(rc_centr / rc_crudo, 4),
  # El enlace con el módulo 7, que es lo que impide leer mal esta z: el
  # modelo lineal no ve nada porque supone una forma que la relación no
  # tiene, y rhohat ya enseñó que en el bulto la variación es de 1,6.
  nota_dcen = "z pequeño no es ausencia de relación: es ausencia de relación LOG-LINEAL (ver módulo 7)")

message(sprintf("   crudo: singular (cond rec %.1e) · centrado: cond rec %.1e, %.0f veces mejor · z de la distancia: %.2f",
                rc_crudo, rc_centr, D$m9$mejora_condicion, c_dcen$z[2]))

# =====================================================================
# MÓDULO 10 · Diagnóstico del ajuste
# =====================================================================
message("10. diagnostico del ajuste")

NSIM_ENV <- 999L
CORR_ENV <- PPP_CORR   # traslación: la misma que el capítulo 4, y por lo mismo

# LA PREGUNTA DEL MÓDULO, Y ES LA BISAGRA DEL CAPÍTULO. El capítulo 4
# cerró con que el patrón colombiano se sale de la banda de CSR por
# muchísimo. Aquí ya hay un modelo que admite intensidad variable: ¿basta
# con eso? Si la K inhomogénea del patrón cae DENTRO de la banda del
# modelo ajustado, la agregación era intensidad variable disfrazada. Si
# se sale igual, hace falta otra cosa —y esa otra cosa es el módulo 11—.
#
# Es una pregunta con respuesta, no retórica, y la respuesta se mide.
env_inh <- cacheado(sprintf("env_kinhom_%d_%s", NSIM_ENV, CORR_ENV), {
  set.seed(SEM_ENV)
  envelope(f_centr, Kinhom, nsim = NSIM_ENV, correction = CORR_ENV,
           verbose = FALSE, savefuns = FALSE)
})

rg_env <- ppp_rejilla_r(env_inh, N_R <- 101L)
obs <- ppp_curva(env_inh, "obs", rg_env)
lo  <- ppp_curva(env_inh, "lo",  rg_env)
hi  <- ppp_curva(env_inh, "hi",  rg_env)
# Un objeto `envelope` NO trae columna `theo`: trae `mmean`, la media
# de las simulaciones. Y es lo que aquí toca, porque la referencia no
# es la teórica de CSR sino la del MODELO AJUSTADO.
mme <- ppp_curva(env_inh, "mmean", rg_env)
fuera <- obs > hi | obs < lo
# `r = 0` no cuenta: las tres curvas valen 0 ahí por construcción.
dentro_r <- rg_env > 0
pct_fuera <- 100 * mean(fuera[dentro_r])

if (pct_fuera <= 0)
  stop("la K inhomogénea no se sale de la banda del modelo ajustado: la bisagra del capítulo cambió y hay que reescribir el módulo 11")

D$m10 <- list(
  modelo = "ppm(~ xc + yc), coordenadas centradas",
  nsim = NSIM_ENV, correccion = CORR_ENV,
  nivel_puntual_pct = r10(100 * 2 / (NSIM_ENV + 1)),
  r_max_m = r10(max(rg_env)),
  n_nodos = N_R,
  pct_r_fuera_de_banda = r10(pct_fuera),
  primer_r_fuera_m = r10(min(rg_env[dentro_r][fuera[dentro_r]])),
  curva = list(r = r10(rg_env), obs = r10(obs), lo = r10(lo), hi = r10(hi), mmean = r10(mme)),
  # La lectura, que es lo que el módulo tiene que dejar dicho.
  veredicto = "la intensidad variable no explica la agregación: hace falta un proceso de conglomerado")

message(sprintf("   K inhomogénea fuera de la banda en el %.1f%% de los r, desde %.0f m",
                pct_fuera, D$m10$primer_r_fuera_m))

# =====================================================================
# MÓDULO 11 · Procesos de conglomerado, Cox y autoexcitados
# =====================================================================
message("11. conglomerado, Cox y autoexcitados")

# LOS TRES MODELOS POR LAS DOS CORRECCIONES, Y LA COMPARACIÓN ES EL
# MÓDULO. Ver A.21.2 del plan: `kppm` pide K con el `correction` por
# defecto, que sobre esta ventana es la isotrópica —127 s—, y cambiarlo a
# traslación baja a 0,46 s. Pero NO es un acelerón: mueve kappa un 48 %,
# la escala un 42 % y mu un 93 %. El contraste mínimo no ajusta el modelo
# al patrón, lo ajusta a una ESTIMACIÓN de K, y cambiar de estimador
# mueve los parámetros más que cambiar de modelo.
#
# Por eso se pagan los 127 s por modelo, una vez, y se cachean: publicar
# solo el barato sería comprar velocidad con un 48 % de sesgo callado.
MODELOS <- c("Thomas", "MatClust", "LGCP")
CORRS   <- c("iso", PPP_CORR)

ajustes <- list()
for (m in MODELOS) for (cr in CORRS) {
  k <- cacheado(sprintf("kppm_%s_%s", tolower(m), cr), ppp_kppm(p_urb, m, cr))
  ajustes[[paste(m, cr, sep = "/")]] <- list(
    modelo = m, correccion = cr, segundos = r10(k$segundos),
    parametros = lapply(k$parametros, r10),
    mu = r10(k$mu), mu_que = k$mu_que)
}

# La divergencia entre correcciones, por modelo y por parámetro: la cifra
# que impide leer cualquiera de los seis ajustes como «el» ajuste.
divergencia <- lapply(MODELOS, function(m) {
  a <- ajustes[[paste(m, "iso", sep = "/")]]
  b <- ajustes[[paste(m, PPP_CORR, sep = "/")]]
  nom <- intersect(names(a$parametros), names(b$parametros))
  list(modelo = m,
       parametros = setNames(lapply(nom, function(k)
         r10(100 * abs(b$parametros[[k]] - a$parametros[[k]]) / abs(a$parametros[[k]]))), nom),
       mu_pct = r10(100 * abs(b$mu - a$mu) / abs(a$mu)),
       segundos_iso = a$segundos, segundos_trans = b$segundos,
       veces_mas_rapido = r10(a$segundos / b$segundos))
})
if (max(sapply(divergencia, function(d) d$mu_pct)) < 10)
  stop("las dos correcciones dejaron de divergir: la lección del módulo 11 hay que volver a medirla")

# --- LOS DUPLICADOS, Y EL CABO QUE EL CAPÍTULO 4 DEJÓ ABIERTO ---------
# La decisión 3 del capítulo 4 conservó los 40 sitios repetidos y los
# midió en G y en K, donde se ven como un átomo en el origen. Pero aquel
# capítulo DESCRIBÍA y este AJUSTA, y un modelo de conglomerado que ve
# puntos coincidentes tiene que explicarlos con algo —y lo único que
# tiene es una escala de conglomerado diminuta—. La hipótesis era que los
# duplicados descuadrarían el ajuste.
#
# SE MIDIÓ Y LA HIPÓTESIS ES FALSA, y por eso vale publicarla: la escala
# de Thomas se mueve un 4 % al quitarlos. El capítulo cierra el cabo con
# una cifra en vez de dejar al lector suponiendo en cualquiera de los dos
# sentidos.
p_unico <- unique(p_urb)
dup_efecto <- lapply(MODELOS, function(m) {
  a <- cacheado(sprintf("kppm_%s_%s", tolower(m), PPP_CORR), ppp_kppm(p_urb, m, PPP_CORR))
  b <- cacheado(sprintf("kppm_%s_%s_unico", tolower(m), PPP_CORR),
                ppp_kppm(p_unico, m, PPP_CORR))
  nom <- intersect(names(a$parametros), names(b$parametros))
  list(modelo = m,
       con_duplicados = lapply(a$parametros, r10), sin_duplicados = lapply(b$parametros, r10),
       mu_con = r10(a$mu), mu_sin = r10(b$mu),
       cambio_pct = setNames(lapply(nom, function(k)
         r10(100 * abs(b$parametros[[k]] - a$parametros[[k]]) / abs(a$parametros[[k]]))), nom))
})
cambio_max <- max(unlist(lapply(dup_efecto, function(d) unlist(d$cambio_pct))))
# La comprobación es la AFIRMACIÓN del módulo, y puede fallar: si algún
# día los duplicados sí descuadraran el ajuste, lo que hay que reescribir
# es el párrafo, no el umbral.
if (cambio_max > 15)
  stop(sprintf("los duplicados mueven un parámetro un %.1f %%: ya no es cierto que no descuadren el ajuste", cambio_max))

# --- HAWKES: el conglomerado en el TIEMPO ------------------------------
# La conexión con ciencia de datos que pide el plan: fraude y sismología.
# Un proceso autoexcitado no es un Poisson con intensidad variable —donde
# la variación la pone una covariable de fuera— sino uno donde CADA
# EVENTO SUBE la intensidad de los siguientes. La razón de ramificación
# alpha/beta es el número esperado de hijos por evento; por debajo de 1
# el proceso no explota, y la tasa media es mu/(1 - alpha/beta), que se
# comprueba contra la simulación en vez de citarse.
HAW <- list(mu = 0.5, alpha = 0.8, beta = 1.4, T = 4000)
hawkes_sim <- function(mu, alpha, beta, Tmax, semilla) {
  set.seed(semilla)
  t <- 0; ev <- numeric(0)
  repeat {
    # La intensidad decrece entre eventos, así que su valor en t acota
    # el intervalo [t, siguiente): es la cota de Ogata.
    cota <- mu + sum(alpha * exp(-beta * (t - ev)))
    t <- t - log(runif(1)) / cota
    if (t > Tmax) break
    if (runif(1) <= (mu + sum(alpha * exp(-beta * (t - ev)))) / cota) ev <- c(ev, t)
  }
  ev
}
ev_h <- hawkes_sim(HAW$mu, HAW$alpha, HAW$beta, HAW$T, SEM_HAWKES)
ramif <- HAW$alpha / HAW$beta
tasa_teo <- HAW$mu / (1 - ramif)
tasa_obs <- length(ev_h) / HAW$T
if (ramif >= 1) stop("la razón de ramificación llegó a 1: el proceso explota")
if (abs(tasa_obs - tasa_teo) / tasa_teo > 0.10)
  stop(sprintf("la tasa simulada (%.4f) no cuadra con mu/(1-alpha/beta) (%.4f)", tasa_obs, tasa_teo))

# Y contra un Poisson de la MISMA tasa media, para que la comparación sea
# sobre la estructura y no sobre el número de eventos.
set.seed(SEM_HAWKES + 1L)
ev_p <- sort(runif(length(ev_h), 0, HAW$T))
disp <- function(ev, k = 200L) {
  cnt <- table(cut(ev, seq(0, HAW$T, length.out = k + 1L), include.lowest = TRUE))
  var(as.numeric(cnt)) / mean(as.numeric(cnt))
}
d_h <- disp(ev_h); d_p <- disp(ev_p)
if (d_h <= d_p) stop("el Hawkes no salió más agregado que el Poisson de su misma tasa")

D$m11 <- list(
  ajustes = unname(ajustes),
  divergencia = divergencia,
  duplicados = list(
    n_con = npoints(p_urb), n_sin = npoints(p_unico),
    repetidos = npoints(p_urb) - npoints(p_unico),
    efecto = dup_efecto, cambio_maximo_pct = r10(cambio_max),
    que = "la decisión 3 del capítulo 4 conservó los duplicados; aquí se mide qué le hacen a un ajuste, y la respuesta es casi nada"),
  nota = "kppm pide K con el correction por defecto, que en ventana no rectangular es la isotrópica; cambiarlo no es un acelerón, es otra respuesta",
  hawkes = list(
    mu = HAW$mu, alpha = HAW$alpha, beta = HAW$beta, T = HAW$T,
    razon_ramificacion = r10(ramif),
    tasa_teorica = r10(tasa_teo), tasa_simulada = r10(tasa_obs),
    n_eventos = length(ev_h),
    dispersion_hawkes = r10(d_h), dispersion_poisson = r10(d_p),
    veces_mas_agregado = r10(d_h / d_p)))

message(sprintf("   %d ajustes · duplicados mueven como mucho %.1f%% · divergencia máxima en mu: %.1f%% · Hawkes: %.2f eventos/u (teórica %.2f), %.1f veces más agregado que su Poisson",
                length(ajustes), cambio_max, max(sapply(divergencia, function(d) d$mu_pct)),
                tasa_obs, tasa_teo, d_h / d_p))

# =====================================================================
# LOS MAPAS
# =====================================================================
message("mapas")

# LA FAMILIA DEL DESLIZADOR, Y CADA SUPERFICIE CON SU SIGMA DENTRO.
# El capítulo 1 pagó esta lección dos veces (anexos T1.2 y T1.3) y la
# dejó escrita en su propio código: `campoDePhi()` y `realizacionDeId()`
# buscan por el PARÁMETRO, nunca por la posición, porque emparejar dos
# listas por índice las descuadró en silencio. Aquí hay exactamente esa
# forma —una lista de sigmas en el dato y una de rásteres en los mapas—
# así que cada ráster lleva su sigma y el ensamblador lo busca por él.
MAPAS$kennedy_familia <- lapply(seq_along(fam$sigmas), function(i) {
  g <- geo_rejilla(fam$imagenes[[i]], fam$caja, escala = fam$escala,
                   titulo = sprintf("Kennedy · sigma = %.0f m", fam$sigmas[i]),
                   leyenda = "sedes por km2")
  # La escala es COMÚN a las siete: se declara en cada una para que el
  # auditor pueda comprobar que ninguna se salió por su cuenta.
  c(g, list(sigma_m = r10(fam$sigmas[i]), escala_comun = r10(fam$escala)))
})

MAPAS$kennedy_puntos <- geo_puntos(
  cbind(p_ken$x, p_ken$y),
  titulo = sprintf("Kennedy · %d sedes educativas", npoints(p_ken)),
  leyenda = "sede")

# Los dos mapas del módulo 5 que NO son el mismo mapa.
MAPAS$ciudad_oferta <- geo_rejilla(
  kde_oferta, c(xr$xrange[1], xr$yrange[1], xr$xrange[2], xr$yrange[2]),
  titulo = sprintf("Sedes educativas · sigma = %.0f m", SIG_CIUDAD),
  leyenda = "sedes por km2")
MAPAS$ciudad_estudiantes <- geo_rejilla(
  kde_est, c(xr$xrange[1], xr$yrange[1], xr$xrange[2], xr$yrange[2]),
  titulo = sprintf("Evaluados en Saber 11 · sigma = %.0f m", SIG_CIUDAD),
  leyenda = "evaluados por km2")

# El módulo 6: la superficie de proporción, con su escala fijada de 0 a 1
# porque una proporción no se normaliza contra su propio máximo —eso
# haría que el mapa dijera «aquí es donde más» en vez de «aquí vale
# tanto», que es justo la lectura que el módulo quiere—.
MAPAS$proporcion_oficial <- geo_rejilla(
  rr_bog, c(xr$xrange[1], xr$yrange[1], xr$xrange[2], xr$yrange[2]),
  escala = c(0, 1),
  titulo = "Proporción de sedes oficiales · P(oficial)", leyenda = "proporción")

MAPAS$sector_puntos <- geo_puntos(
  cbind(p_sec$x, p_sec$y), marcas = as.character(marks(p_sec)),
  titulo = sprintf("Sedes por sector · %d oficiales, %d privadas",
                   sum(marca == "oficial"), sum(marca == "privado")),
  leyenda = "sector")

MAPAS$meta <- list(capitulo = 5L, generado = D$meta$generado)

# =====================================================================
# SALIDAS
# =====================================================================
message("salidas")

D$meta$n_anclas <- N_ANCLAS

txt <- jsonlite::toJSON(D, auto_unbox = TRUE, digits = 10, null = "null", na = "null")
if (grepl('"NA"', txt, fixed = TRUE))
  stop("cap5_datos.json: hay NA escritos como la cadena \"NA\"")
writeLines(txt, file.path(SALIDAS, "cap5_datos.json"), useBytes = TRUE)
message(sprintf("  cap5_datos.json: %.1f KB",
                file.size(file.path(SALIDAS, "cap5_datos.json")) / 1024))

# EL PRESUPUESTO DE ESTE CAPÍTULO NO SE PARECE AL DE NINGUNO ANTERIOR, y
# la razón está en la decisión 4. Los capítulos 1 a 4 publican geometría
# —contornos y puntos, que se simplifican— y este publica ONCE RÁSTERES.
# Un ráster no se simplifica: se muestrea, y bajar el muestreo es
# exactamente lo que la decisión 4 prohíbe por debajo de tres celdas por
# sigma. `geo_rejilla` escribe el array COMPLETO, con -1 en las celdas de
# fuera de la ventana, porque es la forma que el motor lee hoy y la que
# el auditor puede recalcular sin desempaquetar nada.
#
# La compresión —máscara una vez, deltas por fila— es cosa de T3.5: vive
# en el ensamblador, con su prueba de ida y vuelta, y lo que se comprueba
# contra el presupuesto de verdad es el HTML publicado, no este JSON.
# Aquí el presupuesto declarado es el del ráster sin comprimir.
# EL PRESUPUESTO NO SE DESACTIVA: SE PONE DONDE SIRVE. La decisión 5 de
# la Fase 3 dice que el peso no recorta explicación, así que 498 KB de
# rásteres son los que el capítulo necesita. Pero un umbral sigue
# haciendo falta para cazar lo que NO es contenido —un ráster que se
# duplique por un dimyx mal puesto, una superficie de más colada por un
# lapply—. Se deja con holgura sobre lo medido, no sin techo.
geo_escribe(MAPAS, file.path(SALIDAS, "cap5_mapas.json"), presupuesto_kb = 560)

# --- Los CSV que leen las pestañas de Python --------------------------
# Kennedy con lo que hace falta para recalcular su KDE desde cero: sin
# esto, el auditor solo podría comprobar el ráster contra sí mismo.
data.table::fwrite(data.table(
  x = p_ken$x, y = p_ken$y),
  file.path(SALIDAS, "cap5_kennedy.csv"))

# La ciudad con las tres marcas que los módulos 5 y 6 usan. `s11_n` va
# con NA donde la sede no tiene grado 11, que es la mitad: rellenarlo con
# cero convertiría «no aplica» en «ninguno» y el mapa de estudiantes
# cambiaría sin que nada avisara.
data.table::fwrite(data.table(
  x = XY[en_urb, 1], y = XY[en_urb, 2],
  sector = cole$sector[en_urb],
  localidad = cole$localidad[en_urb],
  s11_n = s11$s11_n[en_urb]),
  file.path(SALIDAS, "cap5_bogota_urbana.csv"))

# La familia de sigmas y sus máximos: la tabla que sostiene la afirmación
# del módulo 2, en forma de dato y no solo dentro del JSON.
data.table::fwrite(data.table(
  sigma_m = fam$sigmas, max_km2 = fam$maximos * 1e6),
  file.path(SALIDAS, "cap5_familia_sigma.csv"))

# LOS TIEMPOS DEL HAWKES, Y NO SON UN EXTRA. El módulo 11 publica que el
# proceso autoexcitado sale 5,4 veces más agregado que un Poisson de su
# misma tasa. Sin estos tiempos, esa cifra solo se puede comprobar contra
# sí misma: es exactamente el hueco que el arnés del capítulo 4 le cazó a
# su auditor —`swedishpines` publicaba siete cifras y ninguna coordenada,
# así que el arnés le cambió la R de Donnelly y no se enteró nadie—. Un
# dato publicado sin fuente auditable es un dato en el que hay que creer.
data.table::fwrite(data.table(
  proceso = c(rep("hawkes", length(ev_h)), rep("poisson", length(ev_p))),
  t = c(ev_h, ev_p)),
  file.path(SALIDAS, "cap5_hawkes.csv"))

# La envolvente del módulo 10, para que Python la vuelva a dibujar.
data.table::fwrite(data.table(
  r = rg_env, obs = obs, lo = lo, hi = hi, mmean = mme),
  file.path(SALIDAS, "cap5_envolvente.csv"))

message(sprintf("\nLISTO. %d anclas comprobadas, ninguna rota.", N_ANCLAS))
