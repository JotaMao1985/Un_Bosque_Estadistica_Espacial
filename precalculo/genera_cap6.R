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
      inc   = list(media = r4(mean(col$INC)),   sd = r4(sd(col$INC)))),
    area_km2 = r4(sum(as.numeric(st_area(col))) / 1e6)),
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

# LAS DOS ANCLAS QUE VALIDAN EL TABLERO ENTERO. Son las cifras que
# Anselin publica para Columbus, y si alguna se moviera —otra versión de
# spdep, otro archivo, otro convenio de contigüidad— el capítulo entero
# estaría midiendo otra cosa sin avisar.
ancla(resumen_nb(W_COL$reina)$pares, 118, "Columbus reina: aristas (Anselin)", tol = 0)
ancla(resumen_nb(W_COL$reina)$grado, 4.8163, "Columbus reina: grado medio (Anselin)", tol = 1e-4)
ancla(resumen_nb(W_COL$torre)$pares, 100, "Columbus torre: aristas (Anselin)", tol = 0)
ancla(resumen_nb(W_COL$torre)$grado, 4.0816, "Columbus torre: grado medio (Anselin)", tol = 1e-4)

ETQ_W <- c(reina = "Contigüidad reina", torre = "Contigüidad torre",
           k1 = "1 vecino más próximo", k3 = "3 vecinos más próximos",
           k6 = "6 vecinos más próximos",
           d_mitad = "Umbral: la mitad del mínimo conexo",
           d_conexo = "Umbral mínimo sin islas",
           delaunay = "Delaunay", gabriel = "Gabriel", esfera = "Esfera de influencia")

D$m2 <- list(
  tablero = "columbus", n = nrow(col),
  umbral_sin_islas_m = r4(d1_col),
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

# Contigüidad de orden superior: `nblag` NO acumula. El orden 2 son los
# vecinos de los vecinos que no eran ya vecinos, y esa exclusión es la
# mitad de la idea.
lags <- nblag(W_COL$reina, maxlag = 3L)
D$m3 <- list(
  reina = resumen_nb(W_COL$reina, nrow(col)),
  torre = resumen_nb(W_COL$torre, nrow(col)),
  solo_reina = length(solo_reina),
  ordenes = lapply(seq_along(lags), function(i)
    c(list(orden = i), resumen_nb(lags[[i]], nrow(col)))),
  # Y sobre el caso real, para que la comparación exista
  municipios = list(reina = resumen_nb(mun_reina, nrow(mun)),
                    torre = resumen_nb(mun_torre, nrow(mun))))

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
    c(list(k = k, simetrica = is.symmetric.nb(nb), asimetricos = asimetria(nb)),
      resumen_nb(nb, nrow(col)))
  }),
  municipios_k4 = {
    nb <- knn2nb(knearneigh(mun_cent, k = 4))
    c(list(k = 4L, simetrica = is.symmetric.nb(nb), asimetricos = asimetria(nb)),
      resumen_nb(nb, nrow(mun)))
  },
  # `make.sym.nb` fuerza la simetría añadiendo las aristas que faltan: el
  # grado deja de valer k, que es justo lo que había que entender.
  simetrizada_k3 = {
    nb <- make.sym.nb(knn2nb(knearneigh(col_cent, k = 3)))
    c(list(k = 3L), resumen_nb(nb, nrow(col)))
  })

# =====================================================================
# E. MÓDULO 5 — Umbral de distancia: islas, densidad desigual y el
#     umbral mínimo conexo
# =====================================================================
message("E. modulo 5 - umbral de distancia")

curva_umbral <- function(cent, umbrales, n) {
  lapply(umbrales, function(u) {
    nb <- suppressWarnings(dnearneigh(cent, 0, u))
    c(list(umbral = r4(u)), resumen_nb(nb, n))
  })
}
u_col <- seq(d1_col * 0.4, d1_col * 1.6, length.out = 7)
d1_mun <- max(unlist(nbdists(knn2nb(knearneigh(mun_cent, k = 1)), mun_cent)))

D$m5 <- list(
  columbus = list(umbral_sin_islas = r4(d1_col),
                  curva = curva_umbral(col_cent, u_col, nrow(col))),
  municipios = list(
    umbral_sin_islas_m = r4(d1_mun),
    umbral_sin_islas_km = r4(d1_mun / 1000),
    # LA CIFRA QUE ES EL MÓDULO: el umbral que no deja a nadie solo
    # convierte la vecindad en un sinsentido, y encima es impublicable
    # como dibujo. Esa W se mira como número.
    en_el_umbral = resumen_nb(suppressWarnings(dnearneigh(mun_cent, 0, d1_mun)), nrow(mun)),
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
D$m6 <- list(
  columbus = lapply(names(geo_nb_col), function(k)
    c(list(id = k), resumen_nb(geo_nb_col[[k]], nrow(col)))),
  anidamiento = list(
    relativa_en_gabriel = contenida_en(geo_nb_col$relativa, geo_nb_col$gabriel),
    gabriel_en_delaunay = contenida_en(geo_nb_col$gabriel, geo_nb_col$delaunay)),
  municipios = {
    g <- list(delaunay = tri2nb(mun_cent),
              gabriel  = graph2nb(gabrielneigh(st_coordinates(mun_cent)), sym = TRUE),
              relativa = graph2nb(relativeneigh(st_coordinates(mun_cent)), sym = TRUE),
              esfera   = graph2nb(soi.graph(tri2nb(mun_cent), mun_cent), sym = TRUE))
    lapply(names(g), function(k) c(list(id = k), resumen_nb(g[[k]], nrow(mun))))
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
  islas_nombre = as.character(mun$municipio[islas_i]),
  islas_departamento = as.character(mun$departamento[islas_i]),
  subgrafos = comp_mun$nc,
  tamanos_subgrafo = tam_comp,
  error_sin_zero_policy = err_sin,
  # Lo que el `zero.policy` hace de verdad: la fila de la isla se queda a
  # cero, así que su rezago es 0 — que NO es «no tiene rezago», es «su
  # rezago vale cero», y esa diferencia se cuela en cualquier media.
  lag_isla = r4(lag.listw(lw_mun, ifelse(ok_des, des, 0), zero.policy = TRUE)[islas_i[1]]))

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

D$m10 <- list(
  n = length(sub),
  islas_en_el_subconjunto = sum(!tiene_vecino),
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
