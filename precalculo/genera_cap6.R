# =====================================================================
# genera_cap6.R — el precálculo del capítulo 6 (T4.1)
#
#   «Datos de área y la matriz de pesos espaciales»
#   semanas 10-11 · Material de Estadística Espacial 2026-II (20929).
#
# QUÉ PRODUCE
#   precalculo/salidas/cap6_datos.json   las cifras de los 12 módulos
#   precalculo/salidas/cap6_mapas.json   las fuentes de los .geomapa
#   precalculo/salidas/cap6_*.csv        lo que las pestañas de Python leen
#
# LA REGLA QUE MANDA (D10): ninguna cifra del capítulo se escribe a mano.
#
# LAS TRES DECISIONES DE JAVIER (2026-09-03), y las tres salen del
# cronómetro del A.25, no de la costumbre. La medición entera está allí.
#
#  1. EL CONSTRUCTOR DE W CORRE SOBRE `columbus`. Diez definiciones de
#     vecindad sobre los 1 122 municipios pesan 465 KB contra un
#     presupuesto de 120; sobre los 49 polígonos de Columbus, 18,9. Y no
#     es solo el precio: 49 unidades se ven UNA A UNA, que es lo que un
#     constructor necesita para que se entienda qué cambió. De regalo, el
#     tablero se valida solo — sus cifras son las que publica Anselin.
#
#  2. EL HILO COLOMBIANO ENTRA COMO COROPLETA MUNICIPAL CON UNA SOLA
#     VECINDAD, la contigüidad reina. Es lo que conserva lo que no se
#     puede mudar de tablero: las 2 islas y los 3 subgrafos de los que
#     sale el `zero.policy` del módulo 9, y el rezago del módulo 10 sobre
#     la deserción. El peso se declara en el propio módulo.
#
#  3. `dbscan` SE INSTALA, y con él entra la esfera de influencia del
#     módulo 6. `soi.graph` no avisa cuando falta: muere con «dbscan
#     required». Queda declarado en `instala.R` y en `versiones.json`.
#
# LO QUE ESTE CAPÍTULO NO PUEDE HEREDAR DE LOS ANTERIORES: aquí lo caro
# no es el cálculo. Todo `spdep` es instantáneo salvo `poly2nb` sobre los
# municipios —42 s—, y eso se paga una vez y se cachea. Lo caro es
# PUBLICAR: cada arista pesa, y el capítulo 5 aprendió con el ráster que
# el presupuesto se declara, no se descubre al final.
#
# Ejecutar SIEMPRE con el envoltorio, nunca con `Rscript` a pelo:
#     precalculo/rscript.sh precalculo/genera_cap6.R
# desde la carpeta `Estadistica espacial/`. Ver utf8.R y rscript.sh.
# =====================================================================

suppressPackageStartupMessages({
  library(sf)
  library(spdep)
  library(jsonlite)
  library(data.table)
})

AQUI <- "precalculo"
source(file.path(AQUI, "utf8.R"))     # PRIMERO: para si el proceso no es UTF-8
source(file.path(AQUI, "geo.R"))
source(file.path(AQUI, "fuentes.R"))

SALIDAS <- file.path(AQUI, "salidas")
CACHE   <- file.path(AQUI, "cache")
PROC    <- "datos/procesado"
dir.create(SALIDAS, showWarnings = FALSE, recursive = TRUE)
dir.create(CACHE,   showWarnings = FALSE, recursive = TRUE)

SEMILLA <- 2026L
set.seed(SEMILLA)
options(stringsAsFactors = FALSE)

r4  <- function(x) round(as.numeric(x), 4)
r5  <- function(x) round(as.numeric(x), 5)
r10 <- function(x) round(as.numeric(x), 10)

N_ANCLAS <- 0L

# ---------------------------------------------------------------------
# ancla() — la transcripción contra la literatura, que PARA si falla.
# Misma función que los capítulos 4 y 5, y por el mismo motivo: una cifra
# que no cuadra con su fuente tiene que romper el precálculo, no salir
# publicada con aspecto de correcta.
# ---------------------------------------------------------------------
ancla <- function(calculado, publicado, que, tol = 1e-6) {
  N_ANCLAS <<- N_ANCLAS + 1L
  d <- abs(as.numeric(calculado) - as.numeric(publicado))
  if (!is.finite(d) || d > tol)
    stop(sprintf("ANCLA ROTA · %s: calculado %.8f, la fuente publica %.8f (dif %.2e)",
                 que, as.numeric(calculado), as.numeric(publicado), d))
  invisible(TRUE)
}

cacheado <- function(nombre, expr) {
  f <- file.path(CACHE, paste0("cap6_", nombre, ".rds"))
  if (file.exists(f)) { message(sprintf("    %s: de la cache", nombre)); return(readRDS(f)) }
  v <- force(expr)
  saveRDS(v, f)
  v
}

# ---------------------------------------------------------------------
# resumen_nb() — lo que se publica de CADA vecindad, en un solo sitio.
#
# Se calcula aquí y no en cada módulo porque son nueve módulos mirando lo
# mismo desde ángulos distintos, y dos definiciones del «grado medio»
# —una que divide por n y otra que divide por los que tienen vecinos—
# darían dos cifras plausibles para la misma palabra.
# ---------------------------------------------------------------------
resumen_nb <- function(nb, n = length(nb)) {
  g <- card(nb)
  comp <- n.comp.nb(nb)
  # ENLACES Y PARES NO SON LO MISMO, y aquí es donde se nota: `k3` dirige
  # 147 enlaces pero solo une 73 o 74 PAREJAS distintas, porque «ser de
  # los tres más próximos» no es recíproco. La primera versión de esto
  # publicaba `sum(g)/2` para todas y devolvía **73,5 aristas**, que no
  # es que sea inexacto: es que no existe. Media arista no significa nada
  # y habría llegado al documento con aspecto de cifra.
  pares <- {
    ij <- do.call(rbind, lapply(seq_along(nb), function(i) {
      j <- nb[[i]]; j <- j[j > 0]
      if (length(j) == 0) NULL else cbind(pmin(i, j), pmax(i, j))
    }))
    if (is.null(ij)) 0L else nrow(unique(ij))
  }
  list(enlaces   = sum(g),          # dirigidos: i -> j
       pares     = pares,           # distintos: {i, j}
       simetrica = is.symmetric.nb(nb, verbose = FALSE),
       grado     = r4(mean(g)),
       grado_min = min(g),
       grado_max = max(g),
       islas     = sum(g == 0L),
       subgrafos = comp$nc,
       # La densidad de la matriz: qué fracción de las n(n-1) casillas
       # posibles está ocupada. Es la cifra que hace ver que W es DISPERSA
       # y la que sostiene el módulo 11.
       densidad_pct = r4(100 * sum(g) / (n * (n - 1))))
}

D <- list()
MAPAS <- list()

# =====================================================================
# 0. LOS DATOS
# =====================================================================
message("0. los datos")

# --- El laboratorio: Columbus, el tablero de Anselin ------------------
col <- st_read(system.file("shapes/columbus.gpkg", package = "spData"), quiet = TRUE)
ancla(nrow(col), 49, "barrios de Columbus", tol = 0)
col_cent <- suppressWarnings(st_centroid(st_geometry(col)))
col_xy   <- st_coordinates(col_cent)

# --- El caso real: los municipios de Colombia -------------------------
mun <- carga_municipios(proc = PROC)
ancla(nrow(mun), 1122, "municipios de la capa nacional", tol = 0)
des <- mun$desercion
ok_des <- is.finite(des)
mun_cent <- suppressWarnings(st_centroid(st_geometry(mun)))

message("  poly2nb sobre los municipios (42 s la primera vez, luego cache)")
mun_reina <- cacheado("mun_reina", poly2nb(mun, queen = TRUE))
mun_torre <- cacheado("mun_torre", poly2nb(mun, queen = FALSE))

# =====================================================================
# A. MÓDULO 1 — El dato de área
#
# La idea: en un retículo lo aleatorio es EL VALOR, no la posición. El
# capítulo 4 pasó doce módulos preguntándose si un patrón de puntos era
# azar; aquí las unidades están donde están y lo que varía es lo que
# llevan dentro.
# =====================================================================
message("A. modulo 1 - el dato de area")

D$m1 <- list(
  columbus = list(
    n = nrow(col),
    variables = list(
      crime = list(media = r4(mean(col$CRIME)), sd = r4(sd(col$CRIME)),
                   min = r4(min(col$CRIME)), max = r4(max(col$CRIME))),
      hoval = list(media = r4(mean(col$HOVAL)), sd = r4(sd(col$HOVAL))),
      inc   = list(media = r4(mean(col$INC)),   sd = r4(sd(col$INC))))),
  # SIN ÁREA, Y A PROPÓSITO. El `columbus.gpkg` de spData no trae CRS: sus
  # coordenadas están en unidades arbitrarias, así que `st_area` devolvía
  # un número que al redondear daba CERO y que no habría significado nada
  # aunque no lo diera. Un tablero de laboratorio no necesita escala; lo
  # que necesita es que nadie publique una que no tiene.
  municipios = list(
    n = nrow(mun),
    con_dato = sum(ok_des),
    sin_dato = sum(!ok_des),
    desercion = list(media = r4(mean(des[ok_des])), sd = r4(sd(des[ok_des])),
                     min = r4(min(des[ok_des])), max = r4(max(des[ok_des])),
                     ceros = sum(des[ok_des] == 0)),
    departamentos = length(unique(substr(mun$divipola, 1, 2)))))

# =====================================================================
# B. MÓDULO 2 — Vecindad: las diez definiciones sobre el mismo tablero
#
# El constructor. Diez criterios sobre los mismos 49 polígonos, para que
# la única cosa que cambia sea la definición de «vecino».
# =====================================================================
message("B. modulo 2 - las diez W sobre Columbus")

d1_col <- max(unlist(nbdists(knn2nb(knearneigh(col_cent, k = 1)), col_cent)))

W_COL <- list(
  reina    = poly2nb(col, queen = TRUE),
  torre    = poly2nb(col, queen = FALSE),
  k1       = knn2nb(knearneigh(col_cent, k = 1)),
  k3       = knn2nb(knearneigh(col_cent, k = 3)),
  k6       = knn2nb(knearneigh(col_cent, k = 6)),
  d_mitad  = dnearneigh(col_cent, 0, d1_col * 0.5),
  d_conexo = dnearneigh(col_cent, 0, d1_col),
  delaunay = tri2nb(col_cent),
  gabriel  = graph2nb(gabrielneigh(col_xy), sym = TRUE),
  esfera   = graph2nb(soi.graph(tri2nb(col_cent), col_cent), sym = TRUE))

# LAS DOS ANCLAS QUE VALIDAN EL TABLERO ENTERO: la reina y la torre de los
# polígonos, tal como las dan `poly2nb` aquí y `libpysal` en el auditor (y
# como las documenta libpysal, cuyo `columbus.gal` es esta reina). NO son
# «las de Anselin», como decían estas etiquetas hasta el 2026-11-03: la W que
# Anselin publicó con los datos (1988), el `COL.nb` de spdep, tiene 116
# parejas, y el capítulo la mide más abajo (`m3$gal`). Si alguna se moviera
# —otra versión de spdep, otro archivo, otro convenio de contigüidad— el
# capítulo entero estaría midiendo otra cosa sin avisar.
ancla(resumen_nb(W_COL$reina)$pares, 118, "Columbus reina: parejas de poly2nb y libpysal", tol = 0)
ancla(resumen_nb(W_COL$reina)$grado, 4.8163, "Columbus reina: grado medio de poly2nb y libpysal", tol = 1e-4)
ancla(resumen_nb(W_COL$torre)$pares, 100, "Columbus torre: parejas de poly2nb y libpysal", tol = 0)
ancla(resumen_nb(W_COL$torre)$grado, 4.0816, "Columbus torre: grado medio de poly2nb y libpysal", tol = 1e-4)

# `d_conexo` es el umbral SIN ISLAS, no el conexo: con él el grafo sigue en
# dos pedazos, que es la lección del módulo 5. El identificador se queda
# porque lo usan el mapa y la caché; la etiqueta, que es lo que se lee, ya no
# lo llama conexo (hasta el 2026-11-03 decía «la mitad del mínimo conexo»).
ETQ_W <- c(reina = "Contigüidad reina", torre = "Contigüidad torre",
           k1 = "1 vecino más próximo", k3 = "3 vecinos más próximos",
           k6 = "6 vecinos más próximos",
           d_mitad = "Umbral: la mitad del mínimo sin islas",
           d_conexo = "Umbral mínimo sin islas",
           delaunay = "Delaunay", gabriel = "Gabriel", esfera = "Esfera de influencia")

D$m2 <- list(
  tablero = "columbus", n = nrow(col),
  umbral_sin_islas = r4(d1_col),
  criterios = lapply(names(W_COL), function(k) {
    c(list(id = k, etiqueta = unname(ETQ_W[k])), resumen_nb(W_COL[[k]], nrow(col)))
  }),
  # El histograma de grados de la reina, que es lo que el simulador dibuja
  # al lado del mapa: un grafo con el mismo grado medio puede repartirlo
  # de formas muy distintas.
  histograma = {
    tope <- max(vapply(W_COL, function(nb) max(card(nb)), numeric(1)))
    lapply(names(W_COL), function(k)
      list(id = k, conteo = as.integer(tabulate(card(W_COL[[k]]) + 1L, nbins = tope + 1L))))
  })

# =====================================================================
# C. MÓDULO 3 — Contigüidad: reina, torre y los órdenes superiores
# =====================================================================
message("C. modulo 3 - contiguidad")

# Las aristas que la reina tiene y la torre no: el contacto de esquina.
ar_de <- function(nb) {
  ar <- do.call(rbind, lapply(seq_along(nb), function(i) {
    j <- nb[[i]]; j <- j[j > i]
    if (length(j) == 0) NULL else cbind(i, j)
  }))
  if (is.null(ar)) character(0) else paste(ar[, 1], ar[, 2], sep = "-")
}
solo_reina <- setdiff(ar_de(W_COL$reina), ar_de(W_COL$torre))
solo_reina_mun <- setdiff(ar_de(mun_reina), ar_de(mun_torre))

# Contigüidad de orden superior: `nblag` NO acumula. El orden 2 son los
# vecinos de los vecinos que no eran ya vecinos, y esa exclusión es la
# mitad de la idea.
#
# HASTA EL DIÁMETRO, NO HASTA 3. Con tres órdenes la prosa leyó «al tercer
# orden el mapa se está quedando sin sitios», y la serie entera dice otra
# cosa: hace cima en el 3 (243 parejas) con menos de la mitad de las parejas
# alcanzadas, y el 4 todavía añade 234 (auditoría del 2026-11-03, R5). El
# diámetro es el primer orden que ya no encuentra a nadie, menos uno.
lags <- suppressWarnings(nblag(W_COL$reina, maxlag = 20L))
p_orden <- vapply(lags, function(nb) resumen_nb(nb, nrow(col))$pares, numeric(1))
diametro <- max(which(p_orden > 0))
if (diametro >= 20L) stop("PARADO: el diámetro de la reina de Columbus no cabe en maxlag = 20")
lags <- lags[seq_len(diametro)]
parejas_posibles <- nrow(col) * (nrow(col) - 1) / 2
acum <- cumsum(p_orden[seq_len(diametro)])
ancla(acum[diametro], parejas_posibles, "nblag hasta el diámetro recorre todas las parejas", tol = 0)

# LA GAL DE ANSELIN (1988), el `COL.nb` de spdep, alineada por POLYID con la
# reina de los polígonos: su orden es el de `COL.OLD`, no el del gpkg. Es la
# W que usa el capítulo 7, y el módulo 3 decía que la reina era «la de
# Anselin». Se publica en qué se diferencian, y cuántas de las parejas que
# solo tiene la reina son contactos de esquina.
data(oldcol, package = "spdep")
ancla(isTRUE(all.equal(COL.OLD$CRIME[order(COL.OLD$POLYID)], col$CRIME[order(col$POLYID)])), 1,
      "COL.OLD y el gpkg son los mismos barrios por POLYID", tol = 0)
pares_lab <- function(nb, lab) {
  ij <- do.call(rbind, lapply(seq_along(nb), function(i) {
    j <- nb[[i]]; j <- j[j > 0]
    if (length(j) == 0) NULL else cbind(lab[i], lab[j]) }))
  unique(paste(pmin(ij[, 1], ij[, 2]), pmax(ij[, 1], ij[, 2]), sep = "-"))
}
p_reina_pol <- pares_lab(W_COL$reina, col$POLYID)
p_gal <- pares_lab(COL.nb, COL.OLD$POLYID)
p_esquina_pol <- {
  ij <- do.call(rbind, strsplit(solo_reina, "-"))
  paste(pmin(col$POLYID[as.integer(ij[, 1])], col$POLYID[as.integer(ij[, 2])]),
        pmax(col$POLYID[as.integer(ij[, 1])], col$POLYID[as.integer(ij[, 2])]), sep = "-")
}
gal_solo_reina <- setdiff(p_reina_pol, p_gal)
gal_solo_gal <- setdiff(p_gal, p_reina_pol)
# La copia `columbus.gal` que trae spData, por si alguien la toma por la de
# Anselin: no coincide con ninguna de las dos.
gal_spdata <- read.gal(system.file("weights/columbus.gal", package = "spData"))

D$m3 <- list(
  reina = resumen_nb(W_COL$reina, nrow(col)),
  torre = resumen_nb(W_COL$torre, nrow(col)),
  solo_reina = length(solo_reina),
  # Qué parte de la reina son esquinas, en los tres mapas del capítulo
  # (el de `nc` lo publican las soluciones): «el criterio importa lo que la
  # geometría le deje importar», con la cifra al lado.
  pct_esquina = r4(100 * length(solo_reina) / resumen_nb(W_COL$reina, nrow(col))$pares),
  diametro = diametro,
  parejas_posibles = parejas_posibles,
  ordenes = lapply(seq_along(lags), function(i)
    c(list(orden = i, acumuladas = acum[i], pct_acumulado = r4(100 * acum[i] / parejas_posibles)),
      resumen_nb(lags[[i]], nrow(col)))),
  gal = list(pares = length(p_gal),
             enlaces = sum(card(COL.nb)),
             grado = r4(mean(card(COL.nb))),
             solo_reina = length(gal_solo_reina),
             solo_reina_esquinas = sum(gal_solo_reina %in% p_esquina_pol),
             solo_gal = length(gal_solo_gal),
             pares_spdata = sum(card(gal_spdata)) / 2),
  # Y sobre el caso real, para que la comparación exista
  municipios = list(reina = resumen_nb(mun_reina, nrow(mun)),
                    torre = resumen_nb(mun_torre, nrow(mun)),
                    solo_reina = length(solo_reina_mun),
                    pct_esquina = r4(100 * length(solo_reina_mun) /
                                     resumen_nb(mun_reina, nrow(mun))$pares)))

# =====================================================================
# D. MÓDULO 4 — k vecinos más próximos, y la simetría rota
#
# `knearneigh` da SIEMPRE k vecinos, incluso donde no hay nadie cerca. Y
# la relación «ser de los k más próximos» no es simétrica: A puede tener
# a B entre sus tres más cercanos sin que B tenga a A.
# =====================================================================
message("D. modulo 4 - k vecinos")

asimetria <- function(nb) {
  # Pares (i, j) con j vecino de i pero i no vecino de j.
  n <- 0L
  for (i in seq_along(nb)) {
    for (j in nb[[i]]) if (j > 0 && !(i %in% nb[[j]])) n <- n + 1L
  }
  n
}
KS <- 1:8
D$m4 <- list(
  columbus = lapply(KS, function(k) {
    nb <- knn2nb(knearneigh(col_cent, k = k))
    # `simetrica` la trae ya `resumen_nb`: repetirla aquí escribía la MISMA
    # clave dos veces en el JSON, y jsonlite las escribe las dos sin
    # quejarse. Quien lea el archivo se queda con una de ellas según la
    # biblioteca, que es la peor forma de tener razón.
    c(list(k = k, asimetricos = asimetria(nb)), resumen_nb(nb, nrow(col)))
  }),
  municipios_k4 = {
    nb <- knn2nb(knearneigh(mun_cent, k = 4))
    c(list(k = 4L, asimetricos = asimetria(nb)), resumen_nb(nb, nrow(mun)))
  },
  # `make.sym.nb` fuerza la simetría añadiendo las aristas que faltan: el
  # grado deja de valer k, que es justo lo que había que entender.
  simetrizada_k3 = {
    nb <- make.sym.nb(knn2nb(knearneigh(col_cent, k = 3)))
    c(list(k = 3L), resumen_nb(nb, nrow(col)))
  },
  # QUÉ CAMBIA SIMETRIZAR, medido en el índice que viene después. La prosa
  # decía que «el índice de Moran supone una W simétrica o la simetriza sin
  # decirlo», y no: `moran.test` usa la W de k vecinos tal como viene, y la
  # cifra cambia si se simetriza antes (auditoría del 2026-11-03, R4). La
  # comprobación a mano asegura que spdep no simetriza por debajo.
  moran_k3 = {
    lw3 <- nb2listw(knn2nb(knearneigh(col_cent, k = 3)), style = "W")
    lw3s <- nb2listw(make.sym.nb(knn2nb(knearneigh(col_cent, k = 3))), style = "W")
    z <- col$CRIME - mean(col$CRIME); W3 <- listw2mat(lw3)
    a_mano <- (nrow(col) / sum(W3)) * sum(z * (W3 %*% z)) / sum(z^2)
    I3 <- unname(moran.test(col$CRIME, lw3)$estimate[1])
    ancla(I3, a_mano, "moran.test con k = 3 es la fórmula sin simetrizar", tol = 1e-10)
    list(asimetrica = r4(I3),
         simetrizada = r4(unname(moran.test(col$CRIME, lw3s)$estimate[1])),
         # La W por filas de la REINA tampoco es simétrica, aunque la vecindad
         # lo sea: w_ij = 1/d_i. Lo dice el capítulo 7 y lo comprueba esto.
         reina_por_filas_simetrica = isSymmetric(unname(nb2mat(W_COL$reina, style = "W"))))
  },
  # San Andrés con k = 4: a qué distancia lo une el criterio con la costa.
  # La prosa decía «700 km de mar», escrito a mano.
  san_andres_k4 = {
    sa <- which(card(mun_reina) == 0L)[1]
    v <- knn2nb(knearneigh(mun_cent, k = 4))[[sa]]
    dv <- as.numeric(st_distance(mun_cent[sa], mun_cent[v])) / 1000
    cont <- mun$departamento[v] != mun$departamento[sa]   # fuera, la del propio archipiélago
    list(municipio = as.character(mun$municipio[sa]),
         costa_min_km = r4(min(dv[cont])), costa_max_km = r4(max(dv[cont])),
         vecinos_costa = sum(cont))
  })

# =====================================================================
# E. MÓDULO 5 — Umbral de distancia: islas, densidad desigual y el
#     umbral mínimo conexo
# =====================================================================
message("E. modulo 5 - umbral de distancia")

curva_umbral <- function(cent, umbrales, n, km = TRUE) {
  lapply(umbrales, function(u) {
    nb <- suppressWarnings(dnearneigh(cent, 0, u))
    # `umbral_km` va aquí y no se calcula en la prosa: dividir entre mil en
    # el ensamblador es aritmética en el texto, que es lo que D10 prohíbe.
    # Columbus no la lleva: no tiene CRS, y sus «0.0006 km» no los leía nadie.
    c(list(umbral = r4(u)), if (km) list(umbral_km = r4(u / 1000)), resumen_nb(nb, n))
  })
}
u_col <- seq(d1_col * 0.4, d1_col * 1.6, length.out = 7)
k1_mun <- knn2nb(knearneigh(mun_cent, k = 1))
dnn_mun <- unlist(nbdists(k1_mun, mun_cent))
d1_mun <- max(dnn_mun)

# EL UMBRAL QUE CONECTA, que no es el que quita las islas. Es la arista más
# larga del árbol generador mínimo de los centroides: por debajo de ella el
# grafo tiene al menos dos pedazos, y en ella, uno (Prim, sobre la matriz de
# distancias). La prosa decía «hace falta subir hasta 0.7426», que es solo el
# punto siguiente del barrido; el ejercicio 3 ya lo calculaba así para `nc`.
cuello_mst <- function(dm) {
  n <- nrow(dm); dentro <- c(TRUE, rep(FALSE, n - 1)); mejor <- dm[1, ]; mx <- 0
  for (s in 2:n) {
    mejor[dentro] <- Inf; j <- which.min(mejor)
    mx <- max(mx, mejor[j]); dentro[j] <- TRUE; mejor <- pmin(mejor, dm[j, ])
  }
  mx
}
u_conexo_col <- cuello_mst(as.matrix(dist(col_xy)))
nb_conexo_col <- dnearneigh(col_cent, 0, u_conexo_col)
ancla(n.comp.nb(nb_conexo_col)$nc, 1, "Columbus: en el umbral conexo el grafo es una pieza", tol = 0)
ancla(n.comp.nb(suppressWarnings(dnearneigh(col_cent, 0, u_conexo_col * (1 - 1e-9))))$nc > 1, 1,
      "Columbus: justo por debajo del umbral conexo, más de una pieza", tol = 0)

# QUIÉN FIJA EL UMBRAL MUNICIPAL. La prosa decía que 166.8 km era «la
# distancia que separa a San Andrés de su vecino más próximo», y es la de
# Puerto Carreño: San Andrés tiene a Providencia a 98 km. El archipiélago no
# lo une ningún umbral por debajo de su distancia a la costa.
mun_xy <- st_coordinates(mun_cent)
i_fija <- which.max(dnn_mun)
sa_i <- which(card(mun_reina) == 0L)
arch <- mun$departamento == mun$departamento[sa_i[1]]
d_arch <- as.matrix(dist(mun_xy))
costa <- which(!arch)
d_costa <- d_arch[sa_i, costa, drop = FALSE]
j_costa <- costa[arrayInd(which.min(d_costa), dim(d_costa))[2]]
u_todo_mun <- cuello_mst(d_arch)
u_continente <- cuello_mst(d_arch[!arch, !arch])
nb_umbral_mun <- suppressWarnings(dnearneigh(mun_cent, 0, d1_mun))
# Leticia y Manizales, que la prosa ponía de vecinas en esa W. No lo son: el
# contraste que sí da es el de sus grados.
i_let <- which(mun$municipio == "Leticia" & mun$departamento == "Amazonas")
i_man <- which(mun$municipio == "Manizales" & mun$departamento == "Caldas")
stopifnot(length(i_let) == 1L, length(i_man) == 1L)
i_mas <- which.max(card(nb_umbral_mun))

D$m5 <- list(
  columbus = list(umbral_sin_islas = r4(d1_col),
                  # El bloque de código del capítulo usa `d1 / 2`, que no es
                  # ninguno de los siete puntos de la curva. Su cifra se publica
                  # aquí para que el `#>` salga del JSON y no de una regla de tres.
                  # LA MITAD, entera: la prosa dice «con la mitad de lo que
                  # hace falta» y el bloque de código usa `d1 / 2`. Publicar
                  # solo las islas obligaba a la prosa a citar otro punto de
                  # la curva —el de 0,6·d1— para dar los subgrafos, así que
                  # el texto y el código hablaban de umbrales distintos con
                  # la misma palabra.
                  la_mitad = resumen_nb(suppressWarnings(
                    dnearneigh(col_cent, 0, d1_col / 2)), nrow(col)),
                  islas_en_la_mitad = sum(card(suppressWarnings(
                    dnearneigh(col_cent, 0, d1_col / 2))) == 0),
                  # EN VECES DEL UMBRAL MÍNIMO, porque es como la prosa lee la
                  # curva. Decía «con el doble» del punto más alto del barrido,
                  # y el barrido llega a 1,6 veces: el doble no está medido.
                  multiplos = r4(u_col / d1_col),
                  umbral_conexo = r4(u_conexo_col),
                  en_el_conexo = resumen_nb(nb_conexo_col, nrow(col)),
                  curva = curva_umbral(col_cent, u_col, nrow(col), km = FALSE)),
  municipios = list(
    umbral_sin_islas_m = r4(d1_mun),
    umbral_sin_islas_km = r4(d1_mun / 1000),
    # LA CIFRA QUE ES EL MÓDULO: el umbral que no deja a nadie solo
    # convierte la vecindad en un sinsentido, y encima es impublicable
    # como dibujo. Esa W se mira como número.
    en_el_umbral = resumen_nb(nb_umbral_mun, nrow(mun)),
    fija_el_umbral = list(municipio = as.character(mun$municipio[i_fija]),
                          departamento = as.character(mun$departamento[i_fija]),
                          vecino = as.character(mun$municipio[k1_mun[[i_fija]]]),
                          km = r4(dnn_mun[i_fija] / 1000)),
    san_andres = list(municipio = as.character(mun$municipio[sa_i[1]]),
                      vecino = as.character(mun$municipio[k1_mun[[sa_i[1]]]]),
                      vecino_km = r4(dnn_mun[sa_i[1]] / 1000),
                      vecinos_en_el_umbral = as.character(mun$municipio[nb_umbral_mun[[sa_i[1]]]]),
                      costa = as.character(mun$municipio[j_costa]),
                      costa_departamento = as.character(mun$departamento[j_costa]),
                      costa_km = r4(min(d_costa) / 1000)),
    # Las dos aristas más largas del árbol generador mínimo: la que une el
    # continente consigo mismo y la que le une el archipiélago.
    umbral_conecta_continente_km = r4(u_continente / 1000),
    umbral_conecta_todo_km = r4(u_todo_mun / 1000),
    leticia_manizales = list(km = r4(d_arch[i_let, i_man] / 1000),
                             vecinas = i_man %in% nb_umbral_mun[[i_let]],
                             grado_leticia = length(nb_umbral_mun[[i_let]]),
                             grado_manizales = length(nb_umbral_mun[[i_man]])),
    mas_conectado = list(municipio = as.character(mun$municipio[i_mas]),
                         departamento = as.character(mun$departamento[i_mas]),
                         grado = length(nb_umbral_mun[[i_mas]])),
    curva = curva_umbral(mun_cent, c(30e3, 50e3, 100e3, d1_mun), nrow(mun))))

# =====================================================================
# F. MÓDULO 6 — Vecindades geométricas, y su anidamiento
#
# Vecindad relativa ⊆ Gabriel ⊆ Delaunay. No es una curiosidad: es lo que
# explica por qué dan grados tan distintos sobre el mismo dato.
# =====================================================================
message("F. modulo 6 - vecindades geometricas")

geo_nb_col <- list(
  delaunay = tri2nb(col_cent),
  gabriel  = graph2nb(gabrielneigh(col_xy), sym = TRUE),
  relativa = graph2nb(relativeneigh(col_xy), sym = TRUE),
  esfera   = graph2nb(soi.graph(tri2nb(col_cent), col_cent), sym = TRUE))

contenida_en <- function(a, b) {
  # ¿toda arista de `a` está en `b`?
  all(ar_de(a) %in% ar_de(b))
}
# LA ESFERA DE INFLUENCIA POR SU DEFINICIÓN: i y j son vecinos si sus
# círculos se solapan, d_ij <= r_i + r_j, con r el radio al vecino más
# próximo. `soi.graph` no la calcula así: parte de la triangulación y se
# queda con las aristas de Delaunay que la cumplen. La prosa la daba por
# «subconjunto de Delaunay, con una regla más exigente», y por definición no
# lo es (auditoría del 2026-11-03, 4.3). Se publican las dos cuentas y se
# comprueba que la de spdep es exactamente la intersección.
dm_col <- as.matrix(dist(col_xy)); diag(dm_col) <- Inf
r_col <- apply(dm_col, 1, min)
soi_def <- which(dm_col <= outer(r_col, r_col, "+") & upper.tri(dm_col), arr.ind = TRUE)
p_soi_def <- paste(soi_def[, 1], soi_def[, 2], sep = "-")
p_del <- ar_de(geo_nb_col$delaunay)
ancla(setequal(intersect(p_soi_def, p_del), ar_de(geo_nb_col$esfera)), 1,
      "la esfera de spdep es la de la definición restringida a Delaunay", tol = 0)
p_rei <- ar_de(W_COL$reina)

D$m6 <- list(
  columbus = lapply(names(geo_nb_col), function(k)
    c(list(id = k), resumen_nb(geo_nb_col[[k]], nrow(col)))),
  anidamiento = list(
    relativa_en_gabriel = contenida_en(geo_nb_col$relativa, geo_nb_col$gabriel),
    gabriel_en_delaunay = contenida_en(geo_nb_col$gabriel, geo_nb_col$delaunay),
    # La esfera de spdep NO es una cadena con Gabriel: tiene más parejas y
    # ninguna de las dos contiene a la otra.
    gabriel_en_esfera = contenida_en(geo_nb_col$gabriel, geo_nb_col$esfera),
    esfera_en_gabriel = contenida_en(geo_nb_col$esfera, geo_nb_col$gabriel)),
  esfera_definicion = list(pares = length(p_soi_def),
                           fuera_de_delaunay = sum(!p_soi_def %in% p_del),
                           pares_spdep = length(ar_de(geo_nb_col$esfera))),
  # «Muy cerca de la contigüidad reina, y no es casualidad»: cuánto, pareja
  # a pareja.
  delaunay_y_reina = list(comunes = length(intersect(p_del, p_rei)),
                          solo_delaunay = length(setdiff(p_del, p_rei)),
                          solo_reina = length(setdiff(p_rei, p_del))),
  municipios = {
    g <- list(delaunay = tri2nb(mun_cent),
              gabriel  = graph2nb(gabrielneigh(st_coordinates(mun_cent)), sym = TRUE),
              relativa = graph2nb(relativeneigh(st_coordinates(mun_cent)), sym = TRUE),
              esfera   = graph2nb(soi.graph(tri2nb(mun_cent), mun_cent), sym = TRUE))
    # NO TENER ISLAS NO ES ESTAR CONECTADO, y con estos cuatro criterios se
    # ve: los cuatro dejan islas = 0 y la esfera de influencia se parte en
    # dos igualmente. La prosa lo contaba al revés —«el archipiélago acaba
    # unido a la costa»— porque solo tenía `islas` para mirar. Así que se
    # publica el reparto en subgrafos y, cuando el pequeño es diminuto,
    # QUIÉN se queda en él: sin eso la prosa tendría que suponerlo.
    lapply(names(g), function(k) {
      comp <- n.comp.nb(g[[k]])
      tam <- sort(as.integer(table(comp$comp.id)), decreasing = TRUE)
      menor <- as.integer(names(which.min(table(comp$comp.id))))
      c(list(id = k), resumen_nb(g[[k]], nrow(mun)),
        # I(): con `auto_unbox`, el grafo de una pieza publicaría su tamaño
        # como un número suelto y no como la lista de tamaños que es.
        list(tamanos_subgrafo = I(tam),
             subgrafo_menor_n = min(tam),
             subgrafo_menor_municipios = I(if (comp$nc > 1L && min(tam) <= 5L)
               as.character(mun$municipio[comp$comp.id == menor]) else character(0))))
    })
  })

# =====================================================================
# G. MÓDULO 7 — De vecinos a pesos: los cinco estilos
#
# El mismo grafo, cinco matrices. Lo que cambia no es «el número»: es qué
# significa una fila.
# =====================================================================
message("G. modulo 7 - los estilos")

ESTILOS <- c("B", "W", "S", "C", "U")
i_max <- which.max(card(W_COL$reina))     # el barrio con más vecinos
i_min <- which.min(card(W_COL$reina))     # el que menos

D$m7 <- list(
  unidad_max = list(i = i_max, grado = card(W_COL$reina)[i_max]),
  unidad_min = list(i = i_min, grado = card(W_COL$reina)[i_min]),
  # Cuántas veces más pesa el vecino de la unidad de menos vecinos que el de
  # la de más, con W: la prosa lo escribía en letras («cinco veces»).
  razon_w = r4(card(W_COL$reina)[i_max] / card(W_COL$reina)[i_min]),
  estilos = lapply(ESTILOS, function(e) {
    lw <- nb2listw(W_COL$reina, style = e)
    pesos <- unlist(lw$weights)
    list(id = e,
         suma_total = r4(sum(pesos)),
         peso_max = r4(lw$weights[[i_max]][1]),
         peso_min = r4(lw$weights[[i_min]][1]),
         # El rezago de CRIME bajo este estilo: la cifra que enseña que el
         # estilo no es cosmética.
         lag_medio = r4(mean(lag.listw(lw, col$CRIME))),
         lag_sd = r4(sd(lag.listw(lw, col$CRIME))),
         cor_con_crime = r4(cor(col$CRIME, lag.listw(lw, col$CRIME))))
  }))

# =====================================================================
# H. MÓDULO 8 — El flujo de spdep, y sfdep como interfaz
#
# Las dos vías tienen que dar EXACTAMENTE lo mismo. Si no, una de las dos
# está haciendo algo que no dice.
# =====================================================================
message("H. modulo 8 - spdep y sfdep")

lw_spdep <- nb2listw(W_COL$reina, style = "W")
lag_spdep <- lag.listw(lw_spdep, col$CRIME)
lag_sfdep <- if (requireNamespace("sfdep", quietly = TRUE)) {
  nb_s <- sfdep::st_contiguity(st_geometry(col))
  wt_s <- sfdep::st_weights(nb_s)
  sfdep::st_lag(col$CRIME, nb_s, wt_s)
} else NULL

D$m8 <- list(
  pasos = c("poly2nb", "nb2listw", "lag.listw"),
  # Los tres primeros rezagos, que el bloque de código imprime. Sin ellos
  # el bloque tendría que escribirlos a mano, y `verifica_bloques.py` los
  # ejecuta: una cifra escrita a mano ahí no es un descuido, es un fallo.
  wy_primeros = r5(head(lag_spdep, 3)),
  sfdep_disponible = !is.null(lag_sfdep),
  # La diferencia máxima entre las dos vías: se publica el número, no la
  # promesa de que coinciden.
  dif_max = if (is.null(lag_sfdep)) NA_real_ else signif(max(abs(lag_spdep - lag_sfdep)), 3),
  n_pares_spdep = resumen_nb(W_COL$reina, nrow(col))$pares,
  n_pares_sfdep = if (is.null(lag_sfdep)) NA_integer_
                    else as.integer(sum(lengths(sfdep::st_contiguity(st_geometry(col)))) / 2))

# =====================================================================
# I. MÓDULO 9 — Islas y `zero.policy`
#
# El caso NO se fabrica: los 1 122 municipios traen 2 islas y 3 subgrafos.
# =====================================================================
message("I. modulo 9 - islas y zero.policy")

islas_i <- which(card(mun_reina) == 0L)
comp_mun <- n.comp.nb(mun_reina)
tam_comp <- sort(as.integer(table(comp_mun$comp.id)), decreasing = TRUE)

# Sin `zero.policy` la construcción FALLA. Se captura el mensaje para
# publicarlo: el estudiante tiene que reconocerlo cuando le salga.
err_sin <- tryCatch({ nb2listw(mun_reina, style = "W"); NA_character_ },
                    error = function(e) conditionMessage(e))
lw_mun <- nb2listw(mun_reina, style = "W", zero.policy = TRUE)

D$m9 <- list(
  islas = length(islas_i),
  # Los índices, en las DOS bases. R cuenta desde 1 y Python desde 0, y el
  # capítulo publica un bloque en cada lenguaje: restar uno en el
  # ensamblador sería aritmética en la prosa, que es justo lo que D10
  # prohíbe y `sin_aritmetica.py` caza.
  islas_i = as.integer(islas_i),
  islas_i0 = as.integer(islas_i - 1L),
  islas_nombre = as.character(mun$municipio[islas_i]),
  islas_departamento = as.character(mun$departamento[islas_i]),
  subgrafos = comp_mun$nc,
  tamanos_subgrafo = tam_comp,
  error_sin_zero_policy = err_sin,
  # Lo que el `zero.policy` hace de verdad: la fila de la isla se queda a
  # cero, así que su rezago es 0 — que NO es «no tiene rezago», es «su
  # rezago vale cero», y esa diferencia se cuela en cualquier media.
  lag_isla = r4(lag.listw(lw_mun, ifelse(ok_des, des, 0), zero.policy = TRUE)[islas_i[1]]),
  # Y QUÉ LE HACE ESE CERO A LOS RESÚMENES, medido. La prosa decía que tira
  # «de cualquier resumen hacia abajo», también de la correlación, y con este
  # dato la correlación SUBE: las dos islas tienen la deserción por debajo de
  # la media, y «dato bajo, rezago cero» encaja con la tendencia. Moran centra,
  # así que para él el cero vale «la media», y su cifra depende del convenio
  # de spdep para el n (auditoría del 2026-11-03, 4.4).
  efecto_cero = local({
    nbs <- subset.nb(mun_reina, ok_des); yy <- des[ok_des]; cv <- card(nbs) > 0
    lw0 <- nb2listw(nbs, style = "W", zero.policy = TRUE)
    w0 <- lag.listw(lw0, yy, zero.policy = TRUE)
    lws <- nb2listw(subset.nb(nbs, cv), style = "W")
    list(desercion_islas = r4(des[islas_i]),
         media_y = r4(mean(yy)),
         media_wy_con_ceros = r4(mean(w0)), media_wy_sin_islas = r4(mean(w0[cv])),
         cor_con_ceros = r4(cor(yy, w0)), cor_sin_islas = r4(cor(yy[cv], w0[cv])),
         moran_con_islas = r5(moran.test(yy, lw0, zero.policy = TRUE)$estimate[[1]]),
         moran_con_islas_sin_ajuste = r5(moran.test(yy, lw0, zero.policy = TRUE,
                                                    adjust.n = FALSE)$estimate[[1]]),
         moran_sin_islas = r5(moran.test(yy[cv], lws)$estimate[[1]]))
  }),
  # `nb2listw` también se niega con el estilo B, que no divide por nada: es
  # una política de spdep, no una división por cero.
  falla_tambien_con_B = inherits(try(nb2listw(mun_reina, style = "B"), silent = TRUE), "try-error"))

# =====================================================================
# J. MÓDULO 10 — El rezago espacial Wy
# =====================================================================
message("J. modulo 10 - el rezago")

des0 <- ifelse(ok_des, des, NA_real_)
# El rezago se calcula sobre los municipios CON dato, con su propia W:
# meter ceros donde falta el dato inventaría vecinos con deserción cero.
sub <- which(ok_des)
nb_sub <- subset.nb(mun_reina, ok_des)
lw_sub <- nb2listw(nb_sub, style = "W", zero.policy = TRUE)
wy <- lag.listw(lw_sub, des[sub], zero.policy = TRUE)
tiene_vecino <- card(nb_sub) > 0

# LA MISMA CORRELACIÓN CON OTRAS W. La prosa decía «con la torre, con
# k = 4 o con un umbral de 30 km sale otra» sin enseñarla, y que la
# respuesta del capítulo 7 dependería «entera» de la W. Se mide.
cor_con <- function(nbx) {
  s <- subset.nb(nbx, ok_des); cv <- card(s) > 0
  w <- lag.listw(nb2listw(s, style = "W", zero.policy = TRUE), des[sub], zero.policy = TRUE)
  list(correlacion = r4(cor(des[sub][cv], w[cv])), sin_vecinos = sum(!cv))
}

D$m10 <- list(
  n = length(sub),
  islas_en_el_subconjunto = sum(!tiene_vecino),
  n_con_vecinos = sum(tiene_vecino),
  otras_w = list(torre = cor_con(mun_torre),
                 k4 = cor_con(knn2nb(knearneigh(mun_cent, k = 4))),
                 umbral_30km = c(list(km = 30), cor_con(suppressWarnings(dnearneigh(mun_cent, 0, 30e3))))),
  correlacion = r4(cor(des[sub][tiene_vecino], wy[tiene_vecino])),
  y = list(media = r4(mean(des[sub])), sd = r4(sd(des[sub]))),
  wy = list(media = r4(mean(wy[tiene_vecino])), sd = r4(sd(wy[tiene_vecino]))),
  # La contracción: el rezago es una media, así que su desviación típica
  # es menor que la del dato. Es la primera intuición de la suavización.
  contraccion_pct = r4(100 * (1 - sd(wy[tiene_vecino]) / sd(des[sub]))))

# =====================================================================
# K. MÓDULO 11 — W es la matriz de adyacencia de un grafo
# =====================================================================
message("K. modulo 11 - W como grafo")

W_B <- nb2mat(W_COL$reina, style = "B")
W_W <- nb2mat(W_COL$reina, style = "W")
grados <- rowSums(W_B)

D$m11 <- list(
  columbus = list(
    n = nrow(col),
    casillas = nrow(col)^2,
    no_ceros = sum(W_B > 0),
    densidad_pct = r4(100 * sum(W_B > 0) / nrow(col)^2),
    # Estandarizar por filas ES normalizar por el grado: D^-1 A. Se
    # comprueba, no se afirma.
    d_inv_a_igual_w = r4(max(abs(W_W - W_B / grados))),
    # Y el paso de mensajes: una capa de GNN es multiplicar por W.
    lag_es_producto = r4(max(abs(as.numeric(W_W %*% col$CRIME) -
                                 lag.listw(nb2listw(W_COL$reina, style = "W"), col$CRIME))))),
  municipios = list(
    n = nrow(mun),
    casillas = as.numeric(nrow(mun))^2,
    no_ceros = sum(card(mun_reina)),
    densidad_pct = r4(100 * sum(card(mun_reina)) / as.numeric(nrow(mun))^2)))

# =====================================================================
# LOS MAPAS
# =====================================================================
message("L. los mapas")

MAPAS[["cap6-w"]] <- geo_grafo_multi(
  col, W_COL,
  titulo = "Columbus: diez definiciones de vecindad sobre los mismos 49 barrios",
  leyenda = "vecinos", presupuesto = 6000L, verbose = FALSE)

MAPAS[["cap6-municipios"]] <- geo_grafo_multi(
  mun, list(reina = mun_reina),
  titulo = "Los 1 122 municipios y su contigüidad reina",
  leyenda = "vecinos", presupuesto = 12000L, verbose = FALSE)

# =====================================================================
# LO QUE SE ESCRIBE
# =====================================================================
message("M. escribiendo")

D$meta <- list(
  capitulo = 6L,
  semanas = "10-11",
  semilla = SEMILLA,
  generado = as.character(Sys.Date()),
  tableros = list(laboratorio = "columbus", caso = "municipios de Colombia"),
  anclas = NA_integer_)     # se rellena abajo
D$meta$anclas <- N_ANCLAS

geo_escribe(D, file.path(SALIDAS, "cap6_datos.json"), presupuesto_kb = 200)
geo_escribe(MAPAS, file.path(SALIDAS, "cap6_mapas.json"), presupuesto_kb = 400)

# Los CSV que leen las pestañas de Python: sin ellos, las cifras del
# capítulo solo se pueden comprobar contra sí mismas.
fwrite(data.table(
  id = names(W_COL),
  etiqueta = unname(ETQ_W[names(W_COL)]),
  enlaces = vapply(W_COL, function(nb) resumen_nb(nb, nrow(col))$enlaces, numeric(1)),
  pares = vapply(W_COL, function(nb) resumen_nb(nb, nrow(col))$pares, numeric(1)),
  grado = vapply(W_COL, function(nb) resumen_nb(nb, nrow(col))$grado, numeric(1)),
  islas = vapply(W_COL, function(nb) resumen_nb(nb, nrow(col))$islas, numeric(1)),
  subgrafos = vapply(W_COL, function(nb) resumen_nb(nb, nrow(col))$subgrafos, numeric(1))),
  file.path(SALIDAS, "cap6_columbus_w.csv"))

fwrite(data.table(
  divipola = mun$divipola[sub], municipio = mun$municipio[sub],
  departamento = mun$departamento[sub],
  desercion = des[sub], wy = r10(wy), vecinos = card(nb_sub)),
  file.path(SALIDAS, "cap6_municipios_rezago.csv"))

message(sprintf("\nLISTO. %d anclas comprobadas, ninguna rota.", N_ANCLAS))
