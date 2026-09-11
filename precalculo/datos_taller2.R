# =====================================================================
# datos_taller2.R — el dato que se descarga el estudiante · C2b
#
#   Estadística Espacial 2026-II (20929) · Corte II
#   Ver PLAN_Taller_2_Cap_4.md, C2b
#
# QUÉ PRODUCE
#   entrega/datos/taller2_sedes.gpkg        2 209 sedes educativas
#   entrega/datos/taller2_localidades.gpkg  las 20 localidades
#   entrega/datos/taller2_patrones.csv      los patrones, COPIADOS del
#                                           precálculo (ver la sección B)
#
# EL CRITERIO QUE MANDA AQUÍ NACE DE UN FALLO REAL. El Taller 1 se
# repartió el 2026-08-13 con un enunciado que mandaba ejecutar código
# sobre una carpeta que **da 404 fuera del equipo de Javier**, y hubo
# que publicar el dato en un segundo commit el 18 de agosto (`22f4fcc`,
# «el 45 % del escrito ya lo puede ejecutar alguien más»). Por eso este
# guion existe separado del precálculo y por eso sus archivos entran en
# la lista blanca del `.gitignore`: lo que el enunciado manda ejecutar
# tiene que poder ejecutarse desde fuera.
#
# LO QUE ESTOS ARCHIVOS NO PUEDEN LLEVAR. Igual que el JSON: ninguna
# columna que revele la familia de un patrón de T2. Los patrones viajan
# con un identificador opaco —`p01`…`p24` los propios, `t01a`…`t12c` los
# de los tríos— y sin más atributo que las coordenadas. La letra del
# trío es POSICIÓN, no familia: el orden se barajó en el precálculo.
#
# Ejecutar SIEMPRE con el envoltorio:
#     precalculo/rscript.sh precalculo/datos_taller2.R
# =====================================================================

suppressPackageStartupMessages({
  library(sf)
  library(spatstat.geom)
  library(spatstat.random)
  library(jsonlite)
})

AQUI <- "precalculo"
source(file.path(AQUI, "utf8.R"))
source(file.path(AQUI, "puntual.R"))   # ppp_F_borde(): ver `curvas()` abajo

DESTINO <- file.path("entrega", "datos")
dir.create(DESTINO, showWarnings = FALSE, recursive = TRUE)
SALIDAS <- file.path(AQUI, "salidas")

message("A · Las capas de Bogotá")
PROC <- "datos/procesado"
col <- st_read(file.path(PROC, "bogota_colegios.gpkg"),    quiet = TRUE)
loc <- st_read(file.path(PROC, "bogota_localidades.gpkg"), quiet = TRUE)
stopifnot(nrow(col) == 2209, nrow(loc) == 20, st_crs(col)$epsg == 9377)

# Se entrega la capa COMPLETA, las 20 localidades y las 2 209 sedes, y no
# solo las 16 usables: recortarla le diría al estudiante cuáles entraron
# en el sorteo, que es información que no le toca, y además la regla de
# pertenencia de su localidad es suya de calcular.
#
# Se conservan los atributos de marca —sector, calendario, carácter…—
# porque no revelan nada del taller y sí abren la puerta a que alguien
# mire más allá de lo que se le pide.
st_write(col, file.path(DESTINO, "taller2_sedes.gpkg"),
         delete_dsn = TRUE, quiet = TRUE)
st_write(loc, file.path(DESTINO, "taller2_localidades.gpkg"),
         delete_dsn = TRUE, quiet = TRUE)
message(sprintf("    sedes %d · localidades %d · EPSG:%d",
                nrow(col), nrow(loc), st_crs(col)$epsg))

message("B · Los patrones, COPIADOS del precálculo y no regenerados")
# ESTE GUION YA NO GENERA NADA, Y ESA ES LA CORRECCIÓN DE LA FUGA.
#
# Hasta el 2026-09-10 esta sección volvía a sortear los sesenta patrones
# con `set.seed(20262)` y las mismas tres funciones que el precálculo:
# `rThomas` para uno, `rpoispp` para otro y `rSSI` para el tercero, con
# los tres metidos en una lista cuyos NOMBRES eran los tres regímenes.
# Este archivo sí se versiona —tiene que hacerlo: es lo que permite que
# el dato del enunciado se pueda reconstruir desde fuera—, así que
# cualquiera que clonase el repositorio tenía delante:
#
#   · que hay exactamente TRES regímenes y cómo se llaman,
#   · que cada trío trae uno de cada —lo que convierte la clasificación
#     de T2 en un emparejamiento, que es mucho más fácil—,
#   · y, corriéndolo, la respuesta literal de cada trío.
#
# El `.gitignore` sacaba `genera_taller2.R` del repositorio exactamente
# por eso, y este archivo hacía lo mismo sin que nadie lo mirase. Ver el
# §0 del plan, «FUGA».
#
# Ahora las coordenadas las escribe el precálculo —que no se versiona— y
# aquí solo se COPIAN y se COMPRUEBAN. Lo que se pierde es la capacidad
# de reconstruir los patrones sin el precálculo; lo que se gana es que
# ese archivo ya no sea un solucionario. La comprobación de la sección C
# es más fuerte que antes: en vez de «regenero y me da lo mismo» dice
# «lo que se entrega reproduce las curvas publicadas», que es la
# propiedad que de verdad importa y no necesita saber la semilla.
R_MAX <- 0.25; R_NODOS <- 51L; RG <- seq(0, R_MAX, length.out = R_NODOS)
N_PROPIOS <- 24L; N_TRIOS <- 12L

CSV <- file.path(DESTINO, "taller2_patrones.csv")
if (!file.exists(CSV))
  stop(sprintf(paste0("PARADO: no está %s. Lo escribe `genera_taller2.R`, que no se versiona ",
                      "mientras el taller esté vivo. Sin él este guion no puede fabricar los ",
                      "patrones, y no debe: fabricarlos era la fuga."), CSV))
filas <- read.csv(CSV, stringsAsFactors = FALSE)
ids <- unique(filas$patron)
esperados <- c(sprintf("p%02d", seq_len(N_PROPIOS)),
               unlist(lapply(seq_len(N_TRIOS), function(i)
                 sprintf("t%02d%s", i, letters[1:3]))))
if (!setequal(ids, esperados))
  stop(sprintf("PARADO: el CSV trae %d identificadores y se esperaban %d",
               length(ids), length(esperados)))
message(sprintf("    %d patrones · %d puntos en total", length(ids), nrow(filas)))

# El identificador no puede llevar la familia dentro. La letra del trío
# es POSICIÓN, y el orden se barajó en el precálculo.
for (prohibida in c("agregado", "aleatorio", "regular", "thomas", "familia"))
  if (any(grepl(prohibida, filas$patron, ignore.case = TRUE)))
    stop(sprintf("PARADO: el identificador de patrón contiene «%s»", prohibida))

# Y la guarda que faltaba: que este archivo no vuelva a saber generar.
# Se mira a sí mismo, porque la fuga no estaba en lo que producía sino
# en lo que su propio texto enseñaba a quien lo abriera.
yo <- paste(readLines(file.path(AQUI, "datos_taller2.R"), warn = FALSE), collapse = "\n")
cuerpo <- paste(grep("^\\s*#", strsplit(yo, "\n")[[1]], value = TRUE, invert = TRUE),
                collapse = "\n")
# Los nombres van PARTIDOS a propósito. La guarda se lee a sí misma, así
# que un literal entero en esta línea la haría fallar siempre — y una
# guarda que siempre falla se acaba borrando, que es peor que no tenerla.
for (prohibida in c(paste0("rTho", "mas("), paste0("rpoi", "spp("),
                    paste0("rS", "SI("), paste0("set.", "seed(")))
  if (grepl(prohibida, cuerpo, fixed = TRUE))
    stop(sprintf(paste0("PARADO: este guion volvió a llevar «%s» fuera de un comentario. ",
                        "Se versiona, así que eso es publicar cómo se construyeron los ",
                        "patrones — la fuga del §0. Las coordenadas se copian del CSV que ",
                        "escribe el precálculo; no se fabrican aquí."), prohibida))

ppp_de <- function(id) {
  u <- filas[filas$patron == id, ]
  ppp(u$x, u$y, window = owin(c(0, 1), c(0, 1)), check = FALSE)
}

a_rejilla <- function(fv, colu) {
  x <- as.numeric(fv$r); y <- as.numeric(fv[[colu]])
  ok <- is.finite(x) & is.finite(y)
  as.numeric(approx(x[ok], y[ok], xout = RG, rule = 2)$y)
}
suppressPackageStartupMessages(library(spatstat.explore))
# La F NO sale de `Fest`, y tiene que ser la MISMA decisión que toma
# `genera_taller2.R`: en esta instalación `distmap.ppp()` devuelve
# distancias al cuadrado y `Fest()` las lee como distancias (M-14 del
# plan). `ppp_F_borde()` la calcula sobre una rejilla de sondas con
# `nncross` y `bdist.points`, que sí son exactas, y ya en la rejilla de
# publicación. Si las dos mitades usaran caminos distintos, la
# comprobación C de abajo lo diría — que es exactamente para lo que está.
curvas <- function(p) {
  G <- Gest(p)
  K <- Kest(p, correction = "translate"); g <- pcf(p, correction = "translate")
  Kv <- a_rejilla(K, "trans")
  list(r = round(RG, 10), G = round(a_rejilla(G, "km"), 10),
       F = round(ppp_F_borde(p, RG)$f, 10), K = round(Kv, 10),
       L = round(sqrt(pmax(Kv, 0) / pi) - RG, 10),
       g = round(a_rejilla(g, "trans"), 10))
}

message("C · La comprobación que importa: ¿cuadra con el JSON publicado?")
# Sin esto, una desincronización entre este guion y el precálculo sería
# invisible: los dos correrían en verde y el estudiante calcularía sobre
# otros puntos.
#
# SE COMPARAN LAS CINCO CURVAS, no solo la G. Comparar solo G fue el
# agujero que dejó pasar M-14 durante toda la construcción: la F llevaba
# meses sin ser la función de espacio vacío y ni esta comprobación ni el
# auditor la miraban. Una comprobación que mira una de cinco columnas da
# la misma sensación de verde que una que las mira todas.
jd <- jsonlite::fromJSON(file.path(SALIDAS, "taller2_datos.json"), simplifyVector = FALSE)
cmp <- function(a, b, que, tol = 1e-8) {
  d <- max(abs(as.numeric(a) - as.numeric(b)))
  if (!is.finite(d) || d > tol)
    stop(sprintf("PARADO: %s no cuadra con el JSON (dif %.2e). El dato entregado y el enunciado describen patrones DISTINTOS", que, d))
  invisible(TRUE)
}
COLUMNAS <- c("G", "F", "K", "L", "g")
n_cmp <- 0L
for (i in seq_len(N_PROPIOS)) {
  cv <- curvas(ppp_de(sprintf("p%02d", i)))
  for (co in COLUMNAS) {
    cmp(cv[[co]], unlist(jd$patrones[[i]][[co]]), sprintf("la %s del propio %d", co, i))
    n_cmp <- n_cmp + 1L
  }
}
for (i in seq_len(N_TRIOS)) for (j in 1:3) {
  cv <- curvas(ppp_de(sprintf("t%02d%s", i, letters[j])))
  for (co in COLUMNAS) {
    cmp(cv[[co]], unlist(jd$trios[[i]][[j]][[co]]),
        sprintf("la %s del trío %d posición %s", co, i, letters[j]))
    n_cmp <- n_cmp + 1L
  }
}
message(sprintf("    %d curvas comparadas contra el JSON (%d patrones x %d columnas), todas cuadran",
                n_cmp, N_PROPIOS + N_TRIOS * 3L, length(COLUMNAS)))

for (f in list.files(DESTINO, pattern = "^taller2_", full.names = TRUE))
  message(sprintf("    %-42s %6.1f KB", f, file.size(f) / 1024))
message("\nHECHO")
