# =====================================================================
# genera_soluciones.R — los ejercicios guiados, con solución calculada
#
# Material de Estadística Espacial 2026-II (20929). T1.1 (capítulo 1).
#
# CÓMO ESTÁ ORGANIZADO, Y POR QUÉ NO ES UN SOLO ARCHIVO GIGANTE.
#
# En Diseño de Experimentos este guion acabó con 5 468 líneas y los diez
# capítulos dentro. Aquí cada capítulo aporta una SECCIÓN y escribe su
# propio JSON (`capN_soluciones.json`), de modo que regenerar el capítulo
# 1 no obliga a recalcular los otros nueve ni a leerlos para encontrar el
# suyo. La sección que toca se elige con el argumento de la línea de
# órdenes; sin argumento se hacen todas las que existan.
#
#     precalculo/rscript.sh precalculo/genera_soluciones.R 1
#
# LA REGLA: ninguna solución se escribe a mano. El enunciado sí es texto,
# pero todas las cifras de la solución —incluidos los pasos intermedios—
# salen de ejecutar R aquí. Un ejercicio cuya solución esté escrita de
# memoria es una errata esperando a que un estudiante la encuentre.
# =====================================================================

suppressPackageStartupMessages({
  library(sf)
  library(sp)
  library(spdep)
  library(HistData)
  library(jsonlite)
})

AQUI <- "precalculo"
source(file.path(AQUI, "utf8.R"))
source(file.path(AQUI, "fuentes.R"))

SALIDAS <- file.path(AQUI, "salidas")
dir.create(SALIDAS, showWarnings = FALSE, recursive = TRUE)

SEMILLA <- 2026L
r10 <- function(x) round(as.numeric(x), 10)

args <- commandArgs(trailingOnly = TRUE)
CAPS <- if (length(args)) as.integer(args) else 1L

# =====================================================================
# CAPÍTULO 1 — «Datos espaciales y la primera ley de la geografía»
# =====================================================================
solucion_cap1 <- function() {
  message("Capítulo 1 · los cuatro ejercicios guiados")
  set.seed(SEMILLA)
  E <- list()

  # -------------------------------------------------------------------
  # E1 · Snow sin la bomba de Broad Street
  #
  # El ejercicio no repite el módulo 1: lo lleva un paso más allá. Si el
  # argumento de Snow es que las muertes se apiñan alrededor de UNA bomba,
  # entonces quitar esa bomba del mapa tiene que dejar a sus muertes
  # notablemente más lejos de la siguiente. Y eso se mide.
  # -------------------------------------------------------------------
  message("  E1 · Snow")
  data(Snow.deaths); data(Snow.pumps)
  muertes <- as.matrix(Snow.deaths[, c("x", "y")])
  bombas  <- as.matrix(Snow.pumps[,  c("x", "y")])
  i_broad <- which(Snow.pumps$label == "Broad St")

  dmat <- as.matrix(dist(rbind(muertes, bombas)))[
    seq_len(nrow(muertes)), nrow(muertes) + seq_len(nrow(bombas))]
  cerca <- max.col(-dmat, ties.method = "first")
  d_min <- dmat[cbind(seq_len(nrow(dmat)), cerca)]

  # El mismo cálculo sin la columna de Broad Street
  dsin <- dmat[, -i_broad, drop = FALSE]
  cerca_sin <- max.col(-dsin, ties.method = "first")
  d_min_sin <- dsin[cbind(seq_len(nrow(dsin)), cerca_sin)]

  suyas <- cerca == i_broad      # las 359 muertes de la celda de Broad St
  otras <- !suyas

  E$e1 <- list(
    titulo = "Quitarle a Snow su bomba",
    enunciado = paste(
      "Con `HistData::Snow.deaths` y `Snow.pumps`, calcula para cada",
      "muerte la bomba más próxima. Después repite el cálculo ELIMINANDO",
      "la bomba de Broad Street de la lista. ¿Cuánto se alejan de su",
      "bomba las muertes que la tenían como más próxima? ¿Y las demás?",
      "¿Qué te dice la comparación entre los dos grupos?"),
    pasos = list(
      list(paso = "Muertes y bombas leídas",
           valor = sprintf("%d muertes, %d bombas", nrow(muertes), nrow(bombas))),
      list(paso = "Muertes cuya bomba más próxima es Broad Street",
           valor = as.integer(sum(suyas))),
      list(paso = "Distancia media a su bomba, con Broad Street",
           valor = r10(mean(d_min[suyas]))),
      list(paso = "Distancia media a su bomba, sin Broad Street",
           valor = r10(mean(d_min_sin[suyas]))),
      list(paso = "Cuánto se alejan esas muertes (factor)",
           valor = r10(mean(d_min_sin[suyas]) / mean(d_min[suyas]))),
      list(paso = "Y las demás muertes, cuánto se alejan (factor)",
           valor = r10(mean(d_min_sin[otras]) / mean(d_min[otras])))
    ),
    solucion = list(
      n_suyas = as.integer(sum(suyas)),
      n_otras = as.integer(sum(otras)),
      d_con_broad_suyas = r10(mean(d_min[suyas])),
      d_sin_broad_suyas = r10(mean(d_min_sin[suyas])),
      factor_suyas = r10(mean(d_min_sin[suyas]) / mean(d_min[suyas])),
      d_con_broad_otras = r10(mean(d_min[otras])),
      d_sin_broad_otras = r10(mean(d_min_sin[otras])),
      factor_otras = r10(mean(d_min_sin[otras]) / mean(d_min[otras])),
      # La cifra que cierra el ejercicio
      exceso_pct = r10(100 * (mean(d_min_sin[suyas]) / mean(d_min[suyas]) - 1))
    ),
    lectura = paste(
      "Las muertes de la celda de Broad Street se alejan de forma",
      "sustancial cuando se retira esa bomba, mientras que las demás no",
      "se mueven: por construcción, quitar una bomba solo afecta a quien",
      "la tenía como más próxima. El ejercicio deja ver que el argumento",
      "de Snow es GEOMÉTRICO —una concentración alrededor de un punto—",
      "y no epidemiológico: el dato por sí solo no distingue el agua de",
      "cualquier otra cosa que estuviera en esa esquina. Lo que convierte",
      "el mapa en evidencia es el mecanismo que Snow ya sospechaba, no el",
      "mapa solo. Esa distinción vuelve en el capítulo 3 (falacia",
      "ecológica) y en el 8 (los tres orígenes de la dependencia).")
  )

  # -------------------------------------------------------------------
  # E2 · El error estándar de la cobertura neta
  #
  # Es el experimento del módulo 4 sobre OTRA variable, para que el
  # estudiante no pueda copiar el resultado. Y con una pregunta añadida
  # que obliga a interpretar: ¿el intervalo ingenuo y el correcto llevan
  # a la misma conclusión sustantiva?
  # -------------------------------------------------------------------
  message("  E2 · El e.e. de la cobertura neta")
  muni <- carga_municipios()
  muni$dpto <- substr(muni$divipola, 1, 2)
  cob <- muni[!is.na(muni$cobertura), ]
  bloques <- split(cob$cobertura, cob$dpto)
  n <- nrow(cob)
  NB <- 4000L

  set.seed(SEMILLA + 900L)
  b_iid <- replicate(NB, mean(sample(cob$cobertura, n, replace = TRUE)))
  set.seed(SEMILLA + 901L)
  b_blq <- replicate(NB, {
    e <- sample(seq_along(bloques), length(bloques), replace = TRUE)
    mean(unlist(bloques[e], use.names = FALSE))
  })
  ee_i <- sd(b_iid); ee_b <- sd(b_blq)
  media <- mean(cob$cobertura)
  z <- 1.959964

  E$e2 <- list(
    titulo = "El intervalo de confianza que miente",
    enunciado = paste(
      "Con `carga_municipios()`, toma la cobertura neta municipal.",
      "Calcula (a) el error estándar de la media suponiendo",
      "independencia, por remuestreo de municipios uno a uno, y (b) el",
      "mismo error estándar remuestreando DEPARTAMENTOS enteros. Con",
      "cada uno construye el intervalo al 95 %. Después identifica el",
      "conjunto de valores de referencia que el intervalo ingenuo",
      "descartaría y el honesto no: ¿sobre qué coberturas objetivo",
      "llevarían los dos métodos a conclusiones OPUESTAS?"),
    pasos = list(
      list(paso = "Municipios con dato de cobertura", valor = as.integer(n)),
      list(paso = "Departamentos (bloques del remuestreo)",
           valor = as.integer(length(bloques))),
      list(paso = "Media de la cobertura neta (%)", valor = r10(media)),
      list(paso = "e.e. remuestreando municipios", valor = r10(ee_i)),
      list(paso = "e.e. remuestreando departamentos", valor = r10(ee_b)),
      list(paso = "Factor de subestimación", valor = r10(ee_b / ee_i))
    ),
    solucion = list(
      n = as.integer(n), n_bloques = as.integer(length(bloques)), nboot = NB,
      media = r10(media),
      ee_iid = r10(ee_i), ee_bloques = r10(ee_b),
      factor = r10(ee_b / ee_i),
      n_eff = r10(n * (ee_i / ee_b)^2),
      ic_iid = r10(media + c(-1, 1) * z * ee_i),
      ic_bloques = r10(media + c(-1, 1) * z * ee_b),
      ancho_iid = r10(2 * z * ee_i),
      ancho_bloques = r10(2 * z * ee_b),
      # La respuesta al enunciado: los dos tramos sobre los que los dos
      # métodos dicen cosas opuestas. Salen del propio cálculo, así que
      # no hay ningún valor de referencia elegido a conveniencia — que es
      # justo lo que haría falsa esta clase de ejercicio.
      zona_desacuerdo_inferior = r10(c(media - z * ee_b, media - z * ee_i)),
      zona_desacuerdo_superior = r10(c(media + z * ee_i, media + z * ee_b)),
      ancho_zona_desacuerdo = r10(2 * z * (ee_b - ee_i)),
      # Y la comprobación interna que hace que el ejercicio no pueda
      # salir mal sin avisar: el intervalo honesto contiene al ingenuo.
      contiene = (media - z * ee_b) <= (media - z * ee_i) &&
                 (media + z * ee_i) <= (media + z * ee_b)
    ),
    lectura = paste(
      "Los dos intervalos están centrados en el mismo sitio: la media no",
      "cambia. Lo que cambia es la anchura, y con ella lo que se puede",
      "afirmar. Sobre los dos tramos de desacuerdo el método ingenuo",
      "declara una diferencia significativa donde el honesto no la ve.",
      "Ése es el daño exacto de ignorar la dependencia espacial: no",
      "sesga la estimación, sesga la CONFIANZA. Y fíjate en el orden de",
      "magnitud del n efectivo: 1 121 municipios informan como unos",
      "pocos cientos, no como 1 121.")
  )

  # -------------------------------------------------------------------
  # E3 · Cuántas estaciones hacen falta de verdad
  #
  # Invierte el n efectivo: en vez de preguntar cuánta información hay,
  # pregunta cuántas observaciones habría que tomar. Es la pregunta que
  # un estudiante se va a encontrar cuando diseñe un muestreo.
  # -------------------------------------------------------------------
  message("  E3 · n efectivo, al revés")
  est <- st_read("datos/procesado/colombia_estaciones_clima.gpkg", quiet = TRUE)
  xy <- st_coordinates(est)
  n_est <- nrow(est)

  # La correlación media entre pares se estima con un correlograma por
  # bandas, no suponiéndola constante. Aquí basta con la primera banda
  # para tener una cota, y con la media sobre todas las bandas para tener
  # el rho medio que pide la fórmula de equicorrelación.
  bandas <- c(0, 25, 50, 100, 175, 300, 500, 800) * 1000
  Is <- vapply(seq_len(length(bandas) - 1L), function(i) {
    nb <- suppressWarnings(dnearneigh(xy, bandas[i], bandas[i + 1]))
    if (all(card(nb) == 0)) return(NA_real_)
    lw <- nb2listw(nb, style = "W", zero.policy = TRUE)
    suppressWarnings(moran.test(est$t_media_anual, lw,
                                zero.policy = TRUE))$estimate[["Moran I statistic"]]
  }, numeric(1))

  # rho medio sobre TODOS los pares: la media de las I por banda,
  # ponderada por el número de pares de cada banda.
  npares <- vapply(seq_len(length(bandas) - 1L), function(i) {
    nb <- suppressWarnings(dnearneigh(xy, bandas[i], bandas[i + 1]))
    sum(card(nb)) / 2
  }, numeric(1))
  rho_medio <- sum(Is * npares, na.rm = TRUE) / sum(npares[!is.na(Is)])

  n_eff_equi <- function(n, rho) n / (1 + (n - 1) * rho)
  # Y al revés: para tener la precisión de `objetivo` observaciones
  # independientes, ¿cuántas correlacionadas hacen falta?
  #   n_eff = n/(1+(n-1)rho)  =>  n = n_eff (1-rho) / (1 - n_eff rho)
  n_para <- function(objetivo, rho) {
    if (rho <= 0) return(objetivo)
    if (objetivo * rho >= 1) return(Inf)   # el techo: 1/rho, se alcance o no
    objetivo * (1 - rho) / (1 - objetivo * rho)
  }

  E$e3 <- list(
    titulo = "Cuántas estaciones hacen falta de verdad",
    enunciado = paste(
      "Con las 361 estaciones del IDEAM, estima la correlación media",
      "entre pares mediante un correlograma por bandas de distancia.",
      "Con esa correlación y la fórmula del tamaño de muestra efectivo,",
      "responde: (a) ¿a cuántas estaciones independientes equivale la",
      "red actual? (b) Si quisieras la precisión de 25 estaciones",
      "independientes, ¿cuántas correlacionadas necesitarías? (c) ¿Y la",
      "de 50? ¿Hay algún número de estaciones que baste?"),
    pasos = list(
      list(paso = "Estaciones", valor = as.integer(n_est)),
      list(paso = "I de Moran de la primera banda (0-25 km)",
           valor = r10(Is[1])),
      list(paso = "Correlación media entre pares, ponderada por pares",
           valor = r10(rho_medio)),
      list(paso = "n efectivo de la red actual",
           valor = r10(n_eff_equi(n_est, rho_medio))),
      list(paso = "Techo de información: 1/rho",
           valor = r10(1 / rho_medio))
    ),
    solucion = list(
      n = as.integer(n_est),
      bandas_km = r10(bandas / 1000),
      moran_por_banda = r10(Is),
      pares_por_banda = as.integer(npares),
      rho_medio = r10(rho_medio),
      n_eff = r10(n_eff_equi(n_est, rho_medio)),
      pct_informacion = r10(100 * n_eff_equi(n_est, rho_medio) / n_est),
      # El techo: por mucho que se añadan estaciones, n_eff no pasa de
      # 1/rho. Es la respuesta al apartado (c) y la que suele sorprender.
      techo = r10(1 / rho_medio),
      # 25 está por debajo del techo, así que tiene respuesta finita.
      n_para_25 = r10(n_para(25, rho_medio)),
      objetivo_25_alcanzable = is.finite(n_para(25, rho_medio)),
      # 50 está por encima: no existe ninguna red, por grande que sea,
      # que dé esa precisión con esta correlación. `Inf` no viaja a JSON,
      # así que la respuesta se publica como el booleano y no como null.
      objetivo_50_alcanzable = is.finite(n_para(50, rho_medio)),
      objetivo_100_alcanzable = is.finite(n_para(100, rho_medio))
    ),
    lectura = paste(
      "El apartado (c) es el que enseña. Con correlación positiva",
      "constante el tamaño efectivo tiene un TECHO en 1/rho: añadir",
      "estaciones deja de aportar información mucho antes de lo que",
      "cualquiera esperaría. Ojo con el modelo, eso sí: la fórmula de",
      "equicorrelación supone que todas las parejas se parecen lo mismo,",
      "y el correlograma dice justo lo contrario —la correlación decae",
      "con la distancia—. Por eso el resultado es una COTA orientativa y",
      "no una cifra de diseño; el cálculo exacto necesita la matriz de",
      "correlación entera, que es lo que llega en el capítulo 9.")
  )

  # -------------------------------------------------------------------
  # E4 · ¿Cuál es «la» correlación?
  #
  # Tres escalas del mismo par de variables, y una pregunta que no tiene
  # respuesta única. Es la pincelada del MAUP con la que cierra el
  # capítulo, y remite al capítulo 3.
  # -------------------------------------------------------------------
  message("  E4 · Tres escalas, tres correlaciones")
  d <- st_drop_geometry(muni)
  d$dpto <- substr(d$divipola, 1, 2)
  ok <- !is.na(d$s11_punt_medio) & !is.na(d$s11_pct_internet)
  dd <- d[ok, ]

  # La escala intermedia se construye agrupando municipios por CERCANÍA,
  # no por división administrativa: así el ejercicio separa lo que es
  # efecto de la escala de lo que es efecto de la frontera concreta.
  cen <- suppressWarnings(st_coordinates(
    st_point_on_surface(st_geometry(muni[ok, ]))))
  set.seed(SEMILLA + 950L)
  K_INTERMEDIA <- 150L
  grupos <- kmeans(cen, centers = K_INTERMEDIA, nstart = 25,
                   iter.max = 100)$cluster

  agr_por <- function(clave) {
    a <- tapply(dd$s11_punt_medio, clave, mean, na.rm = TRUE)
    b <- tapply(dd$s11_pct_internet, clave, mean, na.rm = TRUE)
    list(n = length(a), r = r10(cor(a, b, use = "complete.obs")))
  }
  esc_mun <- list(n = nrow(dd),
                  r = r10(cor(dd$s11_punt_medio, dd$s11_pct_internet)))
  esc_int <- agr_por(grupos)
  esc_dep <- agr_por(dd$dpto)

  E$e4 <- list(
    titulo = "¿Cuál es «la» correlación?",
    enunciado = paste(
      "Toma el puntaje medio de Saber 11 y el porcentaje de hogares con",
      "internet, por municipio. Calcula su correlación (a) por",
      "municipio, (b) agrupando los municipios en 150 conglomerados",
      "espaciales con k-medias sobre sus centroides, y (c) por",
      "departamento. Escribe cuál de las tres es la correlación entre",
      "puntaje e internet en Colombia."),
    pasos = list(
      list(paso = "Municipios con las dos variables", valor = as.integer(esc_mun$n)),
      list(paso = "r por municipio", valor = esc_mun$r),
      list(paso = sprintf("r por conglomerado (%d grupos)", esc_int$n),
           valor = esc_int$r),
      list(paso = sprintf("r por departamento (%d unidades)", esc_dep$n),
           valor = esc_dep$r)
    ),
    solucion = list(
      k_intermedia = K_INTERMEDIA,
      municipal = esc_mun, conglomerado = esc_int, departamental = esc_dep,
      subida_mun_dep_pct = r10(100 * (esc_dep$r / esc_mun$r - 1)),
      # La correlación crece de forma monótona con el tamaño de la unidad
      monotona = esc_mun$r <= esc_int$r && esc_int$r <= esc_dep$r,
      respuesta = paste(
        "Ninguna de las tres, y las tres. La pregunta está mal planteada:",
        "«la correlación entre puntaje e internet en Colombia» no existe",
        "hasta que se dice sobre qué unidades se calcula. Las tres cifras",
        "son correctas y responden a tres preguntas distintas.")
    ),
    lectura = paste(
      "Éste es el problema de la unidad de área modificable (MAUP) en su",
      "forma más simple, el efecto ESCALA. El capítulo 3 añade el efecto",
      "ZONIFICACIÓN —misma escala, distinta partición— y la falacia",
      "ecológica, que es lo que pasa cuando la correlación entre",
      "agregados se lee como si fuera la correlación entre personas.",
      "Fíjate en que el enunciado agrupa por cercanía y no por",
      "departamento: así queda claro que el efecto es de la escala y no",
      "de dónde estén las fronteras.")
  )

  E$meta <- list(capitulo = 1L, semilla = SEMILLA, n_ejercicios = 4L,
                 generado = format(Sys.Date()), r = R.version.string)

  write_json(E, file.path(SALIDAS, "cap1_soluciones.json"),
             auto_unbox = TRUE, digits = 10, pretty = TRUE, na = "null")
  kb <- file.size(file.path(SALIDAS, "cap1_soluciones.json")) / 1024
  message(sprintf("\ncap1_soluciones.json  %.1f KB", kb))
  message(sprintf("  E1 · las muertes de Broad St se alejan un %.2f %% al quitar la bomba",
                  E$e1$solucion$exceso_pct))
  message(sprintf("  E2 · e.e. %.5f -> %.5f (factor %.4f); zona de desacuerdo de %.4f puntos",
                  E$e2$solucion$ee_iid, E$e2$solucion$ee_bloques,
                  E$e2$solucion$factor, E$e2$solucion$ancho_zona_desacuerdo))
  message(sprintf("  E3 · rho medio %.5f -> n_eff %.2f de %d, techo %.2f (25 alcanzable: %s; 50: %s)",
                  E$e3$solucion$rho_medio, E$e3$solucion$n_eff,
                  E$e3$solucion$n, E$e3$solucion$techo,
                  E$e3$solucion$objetivo_25_alcanzable,
                  E$e3$solucion$objetivo_50_alcanzable))
  message(sprintf("  E4 · r: %.5f (%d muni) -> %.5f (%d congl.) -> %.5f (%d dptos)",
                  esc_mun$r, esc_mun$n, esc_int$r, esc_int$n, esc_dep$r, esc_dep$n))
  invisible(E)
}


# =====================================================================
# CAPÍTULO 2 — «SIG, sistemas de referencia y georreferenciación con sf»
# =====================================================================
#
# CINCO ejercicios y no cuatro. Es una desviación del molde del capítulo
# 1 y va declarada: Javier la decidió el 2026-08-04 porque este capítulo
# cubre DOS semanas de clase (2 y 3) y porque sus errores —el CRS mal
# puesto, el orden lon/lat, el buffer en grados— son los que de verdad se
# cometen en la práctica. Un ejercicio más es barato; un estudiante que
# reproyecta mal en el proyecto integrador, no.
solucion_cap2 <- function() {
  message("Capítulo 2 · los cinco ejercicios guiados")
  set.seed(SEMILLA)
  E <- list()

  # Medir sobre el elipsoide y sobre la esfera, a propósito. Es la misma
  # separación que hace genera_cap2.R y por el mismo motivo: la esfera de
  # s2 infla las áreas un 0,44 % sobre Colombia, y ese 0,44 % se cuela
  # dentro de cualquier razón que la use de referencia.
  con_s2 <- function(usar, expr) {
    antes <- suppressMessages(sf_use_s2(usar))
    on.exit(suppressMessages(sf_use_s2(antes)))
    suppressMessages(force(expr))
  }
  area_elip <- function(x) con_s2(FALSE, as.numeric(st_area(x)))
  dist_elip <- function(a, b) con_s2(FALSE, as.numeric(st_distance(a, b, by_element = TRUE)))

  # -------------------------------------------------------------------
  # E1 · ¿Con qué CRS se mide un área, y cuánto cuesta equivocarse?
  #
  # No repite el módulo 4: allí se ve el error de cada sistema sobre todo
  # el país, y aquí el estudiante tiene que ELEGIR uno para tres
  # municipios concretos y poner una cifra al coste de la elección.
  # -------------------------------------------------------------------
  message("  E1 · elegir el CRS para medir un área")
  muni <- carga_municipios()
  muni_ll <- st_transform(muni, 4326)
  cen <- st_coordinates(st_centroid(st_geometry(muni_ll)))
  d_mc <- abs(cen[, 1] - (-74.0775079166667))     # al meridiano central de 3116
  # Los tres del CONTINENTE: sobre el meridiano, a la distancia mediana y
  # el más lejano. El archipiélago se deja fuera A PROPÓSITO y entra
  # después: es la vuelta de tuerca del ejercicio.
  insular <- substr(muni$divipola, 1, 2) == "88"
  cand <- which(!insular)
  i_cerca <- cand[which.min(d_mc[cand])]
  i_lejos <- cand[which.max(d_mc[cand])]
  i_medio <- cand[which.min(abs(d_mc[cand] - stats::median(d_mc[cand])))]
  i_isla <- which(insular)[which.max(d_mc[insular])]
  sel <- c(i_cerca, i_medio, i_lejos)

  areas <- function(idx) {
    ver <- area_elip(muni_ll[idx, ]) / 1e6
    list(ver = ver,
         a3116 = as.numeric(st_area(st_transform(muni_ll[idx, ], 3116))) / 1e6,
         a9377 = as.numeric(st_area(st_transform(muni_ll[idx, ], 9377))) / 1e6,
         a3857 = as.numeric(st_area(st_transform(muni_ll[idx, ], 3857))) / 1e6)
  }
  A <- areas(sel); Ai <- areas(i_isla)
  err <- function(a, v) 100 * (a / v - 1)
  e3 <- err(A$a3116, A$ver); e9 <- err(A$a9377, A$ver); e8 <- err(A$a3857, A$ver)
  # y los mismos cuatro, añadiendo la isla
  e3i <- c(e3, err(Ai$a3116, Ai$ver)); e9i <- c(e9, err(Ai$a9377, Ai$ver))
  elige <- function(x3, x9) if (max(abs(x3)) < max(abs(x9))) "EPSG:3116" else "EPSG:9377"

  E$e1 <- list(
    titulo = "Tres municipios, cuatro sistemas y una decisión que cambia",
    enunciado = paste(
      "Carga la capa municipal con `carga_municipios()` y quédate con los",
      "municipios CONTINENTALES cuyos centroides estén: (a) sobre el",
      "meridiano central de EPSG:3116, (b) a la distancia mediana de él y",
      "(c) lo más lejos posible. Calcula el área de los tres en EPSG:3116,",
      "EPSG:9377 y EPSG:3857, y compárala con el área geodésica sobre el",
      "elipsoide (`sf_use_s2(FALSE)` y `st_area` sobre lon/lat). ¿Qué",
      "sistema elegirías para un informe nacional si el criterio es el",
      "PEOR error? Ahora añade San Andrés a los tres. ¿Cambia tu",
      "respuesta? ¿Y si el criterio fuera el error MEDIANO en lugar del",
      "peor?"),
    pasos = list(
      list(paso = "Municipio sobre el meridiano central",
           valor = sprintf("%s (%s), a %.4f°", muni$municipio[i_cerca],
                           muni$departamento[i_cerca], d_mc[i_cerca])),
      list(paso = "Municipio a la distancia mediana",
           valor = sprintf("%s (%s), a %.4f°", muni$municipio[i_medio],
                           muni$departamento[i_medio], d_mc[i_medio])),
      list(paso = "Municipio continental más lejano",
           valor = sprintf("%s (%s), a %.4f°", muni$municipio[i_lejos],
                           muni$departamento[i_lejos], d_mc[i_lejos])),
      list(paso = "Área geodésica de los tres (km²)", valor = r10(A$ver)),
      list(paso = "Error de EPSG:3116 en los tres (%)", valor = r10(e3)),
      list(paso = "Error de EPSG:9377 en los tres (%)", valor = r10(e9)),
      list(paso = "Error de EPSG:3857 en los tres (%)", valor = r10(e8)),
      list(paso = "Peor error de cada uno, sin la isla (%)",
           valor = r10(c(max(abs(e3)), max(abs(e9)), max(abs(e8))))),
      list(paso = "Peor error de 3116 y 9377 añadiendo San Andrés (%)",
           valor = r10(c(max(abs(e3i)), max(abs(e9i)))))
    ),
    solucion = list(
      municipios = muni$municipio[sel], departamentos = muni$departamento[sel],
      grados_al_meridiano = r10(d_mc[sel]),
      area_elipsoide_km2 = r10(A$ver),
      area_3116_km2 = r10(A$a3116), area_9377_km2 = r10(A$a9377),
      area_3857_km2 = r10(A$a3857),
      err_3116_pct = r10(e3), err_9377_pct = r10(e9), err_3857_pct = r10(e8),
      peor_3116_pct = r10(max(abs(e3))), peor_9377_pct = r10(max(abs(e9))),
      peor_3857_pct = r10(max(abs(e8))),
      mediano_3116_pct = r10(stats::median(abs(e3))),
      mediano_9377_pct = r10(stats::median(abs(e9))),
      elegido_continente = elige(e3, e9),
      isla = muni$municipio[i_isla],
      isla_grados_al_meridiano = r10(d_mc[i_isla]),
      err_3116_isla_pct = r10(err(Ai$a3116, Ai$ver)),
      err_9377_isla_pct = r10(err(Ai$a9377, Ai$ver)),
      peor_3116_con_isla_pct = r10(max(abs(e3i))),
      peor_9377_con_isla_pct = r10(max(abs(e9i))),
      elegido_con_isla = elige(e3i, e9i),
      # LA CIFRA QUE HACE EL EJERCICIO: ¿cambia la respuesta al añadir un
      # solo municipio? Se recalcula, no se afirma.
      la_isla_cambia_la_respuesta = as.logical(elige(e3, e9) != elige(e3i, e9i))
    ),
    lectura = paste(
      "EPSG:3116 es exacto donde se definió —sobre su meridiano central el",
      "error de área es cero por construcción, porque k = 1— y se degrada",
      "al alejarse. EPSG:9377 renuncia a ese cero, con k = 0,9992, a",
      "cambio de que el peor caso del país sea más pequeño: por eso el",
      "IGAC lo adoptó como origen único nacional, y por eso gana cuando el",
      "criterio es el peor error continental. Pero pierde cuando el",
      "criterio es el error MEDIANO, porque paga el factor de escala en",
      "todas partes; y pierde también, del revés, en cuanto entra San",
      "Andrés: el archipiélago está 700 km mar adentro y le queda más",
      "cerca el meridiano de 3116 que el de 9377. Un solo municipio de",
      "1 122 puede dar la vuelta a la recomendación. Ese es el resultado",
      "que hay que llevarse: «¿qué CRS uso?» no tiene respuesta sin decir",
      "PARA QUÉ, SOBRE QUÉ EXTENSIÓN y CON QUÉ CRITERIO. Y fíjate en que",
      "3857 pierde con cualquiera de los tres criterios: es un sistema",
      "para teselas de mapa web, no para medir.")
  )

  # -------------------------------------------------------------------
  # E2 · El buffer que no mide lo que dice
  #
  # La primera versión de este ejercicio usaba las 361 estaciones del
  # IDEAM y un radio de 5 km, y la respuesta era CERO: Colombia está casi
  # sobre el ecuador, así que 5/111,32 grados mide 4,98 km y no cambia
  # ninguna cuenta. Cierto y didácticamente inútil. Se cambia a las 2 209
  # sedes de Bogotá, que están mil veces más juntas, y ahí el mismo error
  # sí mueve un número que alguien usaría. El caso ecuatorial no se tira:
  # se convierte en la última pregunta del enunciado.
  # -------------------------------------------------------------------
  message("  E2 · el buffer que no mide lo que dice")
  cole2 <- st_read("datos/procesado/bogota_colegios.gpkg", quiet = TRUE)
  cole2_ll <- st_transform(cole2, 4326)
  cole2_m <- st_transform(cole2, 9377)
  lat2 <- st_coordinates(cole2_ll)[, 2]
  RADIOS <- c(200, 500, 1000)
  buf <- lapply(RADIOS, function(m) {
    nb <- lengths(st_intersects(st_buffer(st_geometry(cole2_m), m),
                                st_geometry(cole2_m))) - 1L
    bm <- con_s2(FALSE, suppressWarnings(
      st_buffer(st_geometry(cole2_ll), (m / 1000) / 111.32)))
    nm <- con_s2(FALSE, lengths(st_intersects(bm, st_geometry(cole2_ll)))) - 1L
    list(radio_m = m, total_bien = as.integer(sum(nb)), total_grados = as.integer(sum(nm)),
         n_cambian = as.integer(sum(nb != nm)), pct_cambian = r10(100 * mean(nb != nm)),
         sesgo_total = as.integer(sum(nm) - sum(nb)))
  })
  # Cuánto mide DE VERDAD un buffer de d grados, según la latitud
  radio_ns_km <- function(d) 111.132 * d
  radio_eo_km <- function(d, la) 111.320 * cos(la * pi / 180) * d
  d500 <- 0.5 / 111.32

  E$e2 <- list(
    titulo = "Un buffer de 500 metros que no mide 500 metros",
    enunciado = paste(
      "Con las 2 209 sedes educativas de Bogotá, cuenta para cada una",
      "cuántas otras caen dentro de un radio de 200, 500 y 1 000 m.",
      "Hazlo dos veces: (a) proyectando a EPSG:9377 y usando",
      "`st_buffer(x, r)` en metros, y (b) dejando el objeto en EPSG:4326",
      "y usando `st_buffer(x, (r/1000)/111.32)`, que es la conversión de",
      "kilómetros a grados en el ecuador. ¿A cuántas sedes les cambia la",
      "cuenta con cada radio? ¿La cuenta equivocada sale de más o de",
      "menos, y por qué? Y para terminar: calcula cuánto mediría ese",
      "mismo buffer en grados, en la dirección este-oeste, a la latitud",
      "de Bogotá y a la de Oslo (59,9139°)."),
    pasos = list(
      list(paso = "Sedes", valor = nrow(cole2)),
      list(paso = "Radio 200 m · sedes con la cuenta cambiada",
           valor = as.integer(buf[[1]]$n_cambian)),
      list(paso = "Radio 500 m · sedes con la cuenta cambiada",
           valor = as.integer(buf[[2]]$n_cambian)),
      list(paso = "Radio 1 000 m · sedes con la cuenta cambiada",
           valor = as.integer(buf[[3]]$n_cambian)),
      list(paso = "Radio real este-oeste a la latitud de Bogotá (m), con 500 m nominales",
           valor = r10(1000 * radio_eo_km(d500, mean(lat2)))),
      list(paso = "El mismo, a la latitud de Oslo (m)",
           valor = r10(1000 * radio_eo_km(d500, 59.9139)))
    ),
    solucion = list(
      n_sedes = nrow(cole2),
      radios = buf,
      lat_media_bogota = r10(mean(lat2)),
      radio_ns_m = r10(1000 * radio_ns_km(d500)),
      radio_eo_bogota_m = r10(1000 * radio_eo_km(d500, mean(lat2))),
      radio_eo_oslo_m = r10(1000 * radio_eo_km(d500, 59.9139)),
      achatamiento_bogota = r10(radio_eo_km(d500, mean(lat2)) / radio_ns_km(d500)),
      achatamiento_oslo = r10(radio_eo_km(d500, 59.9139) / radio_ns_km(d500)),
      # el sesgo tiene SIGNO, y se recalcula en vez de afirmarse
      cuenta_de_menos = as.logical(all(vapply(buf, function(b) b$sesgo_total < 0, logical(1))))
    ),
    lectura = paste(
      "Un buffer en grados no es un círculo sobre el terreno: es una",
      "elipse, más achatada cuanto más lejos del ecuador, porque un grado",
      "de longitud encoge con el coseno de la latitud y uno de latitud",
      "casi no (módulo 2). En Bogotá el achatamiento es de menos de medio",
      "punto porcentual, y aun así basta para mover la cuenta de cientos",
      "de sedes: el buffer queda un poco corto por los dos lados y se",
      "deja fuera a los vecinos que estaban justo en el borde. Fíjate en",
      "que el efecto CRECE con el radio, porque cuantos más vecinos hay",
      "cerca del borde, más se cae alguno. Y en que el error es",
      "sistemático, no aleatorio: siempre cuenta de menos. La versión",
      "peligrosa de este error no es la de Bogotá sino la de Oslo, donde",
      "el mismo código produce un buffer que en la dirección este-oeste",
      "mide la mitad de lo que dice — y ese código se escribe una vez",
      "cerca del ecuador y se reutiliza en otra parte.")
  )

  # -------------------------------------------------------------------
  # E3 · Cazar coordenadas invertidas sin saber cuáles son
  #
  # Es la versión útil del módulo 8: no «mira qué pasa si inviertes»,
  # sino «te dan un archivo sucio, encuentra los sucios y di con qué
  # seguridad». Y obliga a distinguir precisión de exhaustividad.
  # -------------------------------------------------------------------
  message("  E3 · cazar las coordenadas invertidas")
  # Las estaciones del IDEAM las usan E3 y E4; se cargan una vez aquí.
  est <- st_transform(st_read("datos/procesado/colombia_estaciones_clima.gpkg",
                              quiet = TRUE), 4326)
  xy <- st_coordinates(est)
  n <- nrow(xy)
  set.seed(SEMILLA)
  malas <- sort(sample(n, round(0.12 * n)))       # el 12 % viene invertido
  sucio <- xy
  sucio[malas, ] <- xy[malas, c(2, 1)]
  # La regla: Colombia cabe entera en esta caja, y es pública.
  CAJA <- c(lon_min = -82.0, lon_max = -66.5, lat_min = -4.5, lat_max = 13.5)
  sospecha <- !(sucio[, 1] >= CAJA["lon_min"] & sucio[, 1] <= CAJA["lon_max"] &
                sucio[, 2] >= CAJA["lat_min"] & sucio[, 2] <= CAJA["lat_max"])
  verdad <- seq_len(n) %in% malas
  vp <- sum(sospecha & verdad); fp <- sum(sospecha & !verdad)
  fn <- sum(!sospecha & verdad); vn <- sum(!sospecha & !verdad)
  # Y la comprobación que cierra el ciclo: invertir las sospechosas, ¿las
  # devuelve a su sitio?
  arreglado <- sucio
  arreglado[sospecha, ] <- sucio[sospecha, c(2, 1)]
  bien_arreglados <- sum(abs(arreglado - xy) < 1e-9) / 2

  E$e3 <- list(
    titulo = "Un archivo con el 12 % de las filas invertidas",
    enunciado = paste(
      "Toma las 361 estaciones del IDEAM e invierte la longitud y la",
      "latitud del 12 % de las filas, elegidas al azar con `set.seed(2026)`.",
      "Ahora olvida cuáles invertiste. Escribe una regla que las señale",
      "usando solo la caja envolvente de Colombia (lon de -82,0 a -66,5;",
      "lat de -4,5 a 13,5) y calcula sus verdaderos positivos, falsos",
      "positivos, falsos negativos, precisión y exhaustividad. Después",
      "invierte las señaladas y comprueba cuántas filas quedan bien.",
      "¿Por qué funciona tan bien AQUÍ, y en qué país fallaría?"),
    pasos = list(
      list(paso = "Filas totales", valor = as.integer(n)),
      list(paso = "Filas invertidas a propósito", valor = as.integer(length(malas))),
      list(paso = "Filas señaladas por la regla", valor = as.integer(sum(sospecha))),
      list(paso = "Verdaderos positivos", valor = as.integer(vp)),
      list(paso = "Falsos positivos", valor = as.integer(fp)),
      list(paso = "Falsos negativos", valor = as.integer(fn)),
      list(paso = "Filas correctas tras invertir las señaladas",
           valor = as.integer(bien_arreglados))
    ),
    solucion = list(
      n = as.integer(n), n_invertidas = as.integer(length(malas)),
      pct_invertidas = r10(100 * length(malas) / n),
      caja = as.numeric(CAJA),
      vp = as.integer(vp), fp = as.integer(fp), fn = as.integer(fn), vn = as.integer(vn),
      precision = r10(if (vp + fp > 0) vp / (vp + fp) else NA_real_),
      exhaustividad = r10(vp / (vp + fn)),
      n_arregladas_bien = as.integer(bien_arreglados),
      pct_arregladas_bien = r10(100 * bien_arreglados / n),
      # el porqué: invertir saca a Colombia de su caja SIEMPRE, porque la
      # caja de longitudes y la de latitudes NO SE SOLAPAN
      solapan_las_cajas = as.logical(
        !(CAJA["lon_max"] < CAJA["lat_min"] || CAJA["lat_max"] < CAJA["lon_min"]))
    ),
    lectura = paste(
      "La regla acierta de pleno, y conviene entender por qué: el",
      "intervalo de longitudes de Colombia y el de latitudes NO SE",
      "SOLAPAN —uno vive en los negativos de dos cifras y el otro entre",
      "-4,5 y 13,5—, así que invertir saca al punto de la caja sin",
      "excepción. Donde esa condición no se cumple, la regla se calla:",
      "en un país que ocupe longitudes y latitudes del mismo rango (Chad,",
      "por ejemplo, o cualquier punto cerca del meridiano de Greenwich y",
      "del ecuador a la vez) hay filas invertidas que caen dentro del",
      "país y no hay forma geométrica de distinguirlas. Ahí la única",
      "defensa es la de la fuente: que el CSV declare el orden y que",
      "alguien lo lea.")
  )

  # -------------------------------------------------------------------
  # E4 · El vecino más próximo aguanta; el umbral, no
  #
  # También hubo que rehacerlo: preguntado solo por el vecino más
  # próximo, el resultado sobre Colombia era CERO —cerca del ecuador un
  # grado de longitud mide el 99,67 % de uno de latitud y el orden no se
  # altera—. El cero no se esconde: se convierte en la mitad del
  # ejercicio, porque el contraste con el umbral, que sí falla, es la
  # lección. Y el umbral no es un ejemplo de laboratorio: es exactamente
  # `dnearneigh()`, con el que el capítulo 6 construye W.
  # -------------------------------------------------------------------
  message("  E4 · el vecino aguanta, el umbral no")
  D_grad <- as.matrix(dist(xy))                       # euclídea SOBRE GRADOS
  # OJO: st_distance devuelve una matriz CON UNIDADES, y comparar eso con
  # un número pelado aborta. Se le quitan a propósito y no por descuido.
  D_real <- matrix(as.numeric(con_s2(FALSE, st_distance(est))), nrow = n)
  diag(D_grad) <- Inf; diag(D_real) <- Inf
  v_grad <- apply(D_grad, 1, which.min)
  v_real <- apply(D_real, 1, which.min)
  cambian <- v_grad != v_real

  UMBRALES <- c(25, 50, 100, 200)
  arriba <- upper.tri(D_real)
  umb <- lapply(UMBRALES, function(km) {
    ug <- D_grad[arriba] <= km / 111.32
    ur <- D_real[arriba] <= km * 1000
    list(umbral_km = km,
         pares_grados = as.integer(sum(ug)), pares_geodesica = as.integer(sum(ur)),
         discrepan = as.integer(sum(ug != ur)),
         pct_discrepan = r10(100 * mean(ug != ur)),
         pct_sobre_los_vecinos = r10(100 * sum(ug != ur) / sum(ur)))
  })

  E$e4 <- list(
    titulo = "El vecino más próximo aguanta; el umbral de vecindad, no",
    enunciado = paste(
      "Para las 361 estaciones del IDEAM calcula dos matrices de",
      "distancias: la euclídea sobre las columnas de longitud y latitud,",
      "y la geodésica con `st_distance`. Primero: ¿a cuántas estaciones",
      "les cambia el vecino MÁS PRÓXIMO? Segundo: define vecindad por",
      "umbral —como hace `spdep::dnearneigh`— a 25, 50, 100 y 200 km,",
      "usando `km/111.32` grados en un caso y metros en el otro, y cuenta",
      "en cuántos PARES discrepan las dos definiciones. Explica por qué",
      "los dos resultados son tan distintos."),
    pasos = list(
      list(paso = "Estaciones y pares",
           valor = sprintf("%d estaciones, %d pares", n, sum(arriba))),
      list(paso = "Estaciones a las que les cambia el vecino más próximo",
           valor = as.integer(sum(cambian))),
      list(paso = "Correlación entre las dos matrices de distancia",
           valor = r10(cor(D_grad[arriba], D_real[arriba]))),
      list(paso = "Pares que discrepan con umbral de 25 km",
           valor = as.integer(umb[[1]]$discrepan)),
      list(paso = "Pares que discrepan con umbral de 200 km",
           valor = as.integer(umb[[4]]$discrepan)),
      list(paso = "Y eso, sobre los pares que SÍ son vecinos a 200 km (%)",
           valor = r10(umb[[4]]$pct_sobre_los_vecinos))
    ),
    solucion = list(
      n = as.integer(n), n_pares = as.integer(sum(arriba)),
      n_cambia_vecino = as.integer(sum(cambian)),
      pct_cambia_vecino = r10(100 * mean(cambian)),
      corr_grados_metros = r10(cor(D_grad[arriba], D_real[arriba])),
      umbrales = umb,
      # el porqué, medido y no afirmado: el grado de longitud a la
      # latitud media del dato, en fracción del de latitud
      anisotropia = r10(cos(mean(xy[, 2]) * pi / 180)),
      lat_media = r10(mean(xy[, 2])),
      # y la lectura, recalculada
      vecino_intacto = as.logical(sum(cambian) == 0),
      umbral_falla = as.logical(any(vapply(umb, function(u) u$discrepan > 0, logical(1))))
    ),
    lectura = paste(
      "El vecino más próximo no cambia para ninguna estación, y el umbral",
      "discrepa en cientos de pares. Las dos cosas salen del mismo dato y",
      "no se contradicen. El vecino más próximo es una pregunta de ORDEN:",
      "sobrevive a cualquier deformación que no altere el ranking, y en",
      "Colombia un grado de longitud mide el 99,67 % de uno de latitud, así",
      "que la deformación es demasiado leve para invertir un orden. El",
      "umbral es una pregunta de MAGNITUD: hay un corte, y todo par que",
      "caiga cerca de él cambia de lado con que la distancia se mueva un",
      "0,3 %. Por eso el número de discrepancias crece con el umbral —hay",
      "más pares cerca del corte— y por eso una definición de vecindad por",
      "distancia es más frágil que una por k vecinos. Es la decisión que",
      "abre el capítulo 6: `dnearneigh` contra `knearneigh` no es cuestión",
      "de gusto.")
  )

  # -------------------------------------------------------------------
  # E5 · ¿Cuánto error posicional se puede tolerar?
  #
  # Es el módulo 9 puesto del revés: en vez de «mira lo que pasa con
  # 150 m», el estudiante fija el requisito y tiene que despejar la
  # tolerancia. Es la forma en que la pregunta aparece en el trabajo real.
  # -------------------------------------------------------------------
  message("  E5 · la tolerancia posicional")
  cole <- st_read("datos/procesado/bogota_colegios.gpkg", quiet = TRUE)
  loc <- st_read("datos/procesado/bogota_localidades.gpkg", quiet = TRUE)
  xyc <- st_coordinates(cole)
  verdad_loc <- st_join(cole["dane_sede"], loc["cod_loca"], join = st_within)$cod_loca
  tasa_para <- function(sigma, nrep = 40L) {
    mean(vapply(seq_len(nrep), function(k) {
      p <- st_as_sf(data.frame(x = xyc[, 1] + rnorm(nrow(xyc), 0, sigma),
                               y = xyc[, 2] + rnorm(nrow(xyc), 0, sigma)),
                    coords = c("x", "y"), crs = st_crs(cole))
      nv <- st_join(p, loc["cod_loca"], join = st_within)$cod_loca
      mean((is.na(verdad_loc) != is.na(nv)) |
             (!is.na(verdad_loc) & !is.na(nv) & verdad_loc != nv))
    }, numeric(1)))
  }
  set.seed(SEMILLA)
  OBJETIVO <- 0.01                       # como mucho el 1 % mal asignado
  rejilla <- c(10, 25, 50, 75, 100, 150, 250)
  tasas <- vapply(rejilla, tasa_para, numeric(1))
  # bisección entre el último que cumple y el primero que no
  lo <- max(rejilla[tasas <= OBJETIVO]); hi <- min(rejilla[tasas > OBJETIVO])
  for (i in 1:8) {
    mid <- (lo + hi) / 2
    if (tasa_para(mid) <= OBJETIVO) lo <- mid else hi <- mid
  }
  sigma_max <- lo

  E$e5 <- list(
    titulo = "Un requisito, y la tolerancia que implica",
    enunciado = paste(
      "El requisito del proyecto es: «como mucho el 1 % de las sedes",
      "puede quedar asignado a una localidad que no es la suya». Con las",
      "2 209 sedes de Bogotá y las 20 localidades, añade a las",
      "coordenadas un ruido gaussiano isótropo de desviación sigma metros",
      "y estima, promediando 40 realizaciones, la proporción de sedes que",
      "cambian de localidad. Barre sigma y despeja el mayor valor que",
      "cumple el requisito. ¿Qué precisión de geocodificación estás",
      "exigiendo, entonces?"),
    pasos = list(
      list(paso = "Sedes y localidades",
           valor = sprintf("%d sedes, %d localidades", nrow(cole), nrow(loc))),
      list(paso = "Sigma barridos (m)", valor = rejilla),
      list(paso = "Tasa de reasignación en cada uno (%)", valor = r10(100 * tasas)),
      list(paso = "Objetivo", valor = "1 % de reasignación"),
      list(paso = "Sigma máximo admisible (m)", valor = r10(sigma_max))
    ),
    solucion = list(
      n_sedes = nrow(cole), n_localidades = nrow(loc),
      objetivo_pct = 1,
      sigma_barrido_m = rejilla, tasa_pct = r10(100 * tasas),
      sigma_max_m = r10(sigma_max),
      tasa_en_sigma_max_pct = r10(100 * tasa_para(sigma_max, nrep = 100L)),
      # traducido a decimales de coordenada geográfica, que es como lo
      # entrega un geocodificador
      decimales_equivalentes = r10(log10(111320 / sigma_max)),
      n_replicas = 40L
    ),
    lectura = paste(
      "El requisito «1 % mal asignado» se traduce en una tolerancia de",
      "unas pocas decenas de metros, que es MÁS EXIGENTE de lo que",
      "suena y más de lo que muchos geocodificadores por dirección",
      "garantizan. Ese es el valor del ejercicio: los requisitos se",
      "escriben en unidades de resultado («1 % mal asignado») y las",
      "fuentes se compran en unidades de posición («precisión de nivel de",
      "calle»), y traducir de unas a otras es trabajo, no intuición. La",
      "traducción además no es universal: depende de la GEOMETRÍA de las",
      "unidades, así que el mismo requisito sobre municipios grandes",
      "toleraría un error mucho mayor. Es la contracara del sesgo del",
      "módulo 9.")
  )

  E$meta <- list(capitulo = 2L, semilla = SEMILLA, n_ejercicios = 5L,
                 generado = format(Sys.Date()), r = R.version.string)

  write_json(E, file.path(SALIDAS, "cap2_soluciones.json"),
             auto_unbox = TRUE, digits = 10, pretty = TRUE, na = "null")
  kb <- file.size(file.path(SALIDAS, "cap2_soluciones.json")) / 1024
  message(sprintf("\ncap2_soluciones.json  %.1f KB", kb))
  message(sprintf("  E1 · peor error continental: 3116 %.5f %% · 9377 %.5f %% · 3857 %.5f %% -> %s",
                  E$e1$solucion$peor_3116_pct, E$e1$solucion$peor_9377_pct,
                  E$e1$solucion$peor_3857_pct, E$e1$solucion$elegido_continente))
  message(sprintf("       añadiendo %s la respuesta pasa a %s (¿cambia? %s)",
                  E$e1$solucion$isla, E$e1$solucion$elegido_con_isla,
                  E$e1$solucion$la_isla_cambia_la_respuesta))
  message(sprintf("  E2 · el buffer en grados cambia la cuenta de %d sedes a 500 m (%.4f %%) y %d a 1 km",
                  E$e2$solucion$radios[[2]]$n_cambian, E$e2$solucion$radios[[2]]$pct_cambian,
                  E$e2$solucion$radios[[3]]$n_cambian))
  message(sprintf("  E3 · precisión %.5f, exhaustividad %.5f; %d de %d filas quedan bien",
                  E$e3$solucion$precision, E$e3$solucion$exhaustividad,
                  E$e3$solucion$n_arregladas_bien, E$e3$solucion$n))
  message(sprintf("  E4 · vecino más próximo: %d cambian · umbral de 200 km: %d pares discrepan (%.4f %% de los vecinos)",
                  E$e4$solucion$n_cambia_vecino, E$e4$solucion$umbrales[[4]]$discrepan,
                  E$e4$solucion$umbrales[[4]]$pct_sobre_los_vecinos))
  message(sprintf("  E5 · sigma máximo para el 1 %%: %.4f m (%.4f decimales de coordenada)",
                  E$e5$solucion$sigma_max_m, E$e5$solucion$decimales_equivalentes))
  invisible(E)
}

# =====================================================================
# CAPÍTULO 3 — «Cartografía estadística y el MAUP»
#
# Los cuatro ejercicios recorren la columna vertebral del capítulo: elegir
# el mapa (E1), normalizar (E2), trazar las zonas (E3) y decidir qué se
# publica cuando el dato admite dos lecturas (E4). Ninguno repite un
# módulo: cada uno lleva su idea un paso más allá y termina en una
# DECISIÓN, que es lo que el capítulo entrena.
# =====================================================================
solucion_cap3 <- function() {
  message("Capítulo 3 · los cuatro ejercicios guiados")
  suppressPackageStartupMessages({
    library(classInt); library(data.table)
  })
  set.seed(SEMILLA)
  E <- list()

  mun <- carga_municipios(proc = "datos/procesado")
  des <- mun$desercion
  ok  <- is.finite(des)
  ESQ <- c("equal", "quantile", "fisher", "sd", "headtails")
  ESQ_ES <- c(equal = "Intervalos iguales", quantile = "Cuantiles",
              fisher = "Fisher-Jenks", sd = "Desviación estándar",
              headtails = "Head/tails")

  # -------------------------------------------------------------------
  # E1 · El mapa que quieras
  #
  # El módulo 4 enseña que el esquema cambia el mapa. Este ejercicio da la
  # vuelta a la pregunta: dado un municipio, ¿existe un esquema que lo
  # pinte en la clase más alta y otro que lo pinte en la más baja? Y si
  # existe, ¿para cuántos municipios existe? Eso convierte «el mapa es una
  # decisión» en una cifra.
  # -------------------------------------------------------------------
  message("  E1 · el mapa que quieras")
  KS <- 3:9
  # Para cada municipio, la clase RELATIVA (0 = la más baja, 1 = la más
  # alta) bajo cada combinación de esquema y k. Relativa porque con k
  # distintos «clase 3» no significa lo mismo.
  rel <- matrix(NA_real_, nrow = sum(ok), ncol = 0)
  cfg <- character(0)
  for (e in ESQ) for (k in KS) {
    cl <- try(classInt::classIntervals(des[ok], n = k, style = e), silent = TRUE)
    if (inherits(cl, "try-error")) next
    cc <- classInt::findCols(cl)
    rel <- cbind(rel, (cc - 1) / (k - 1))
    cfg <- c(cfg, sprintf("%s/k=%d", e, k))
  }
  colnames(rel) <- cfg
  extremo_alto <- apply(rel, 1, max)
  extremo_bajo <- apply(rel, 1, min)
  # «Se puede pintar como quieras» = existe una configuración que lo deja
  # en la clase más alta Y otra que lo deja en la más baja.
  camaleon <- extremo_alto == 1 & extremo_bajo == 0
  recorrido <- extremo_alto - extremo_bajo

  mun_ok <- mun[ok, ]
  i_peor <- which.max(recorrido)
  E$e1 <- list(
    titulo = "El mapa que quieras",
    enunciado = paste(
      "Con la deserción escolar municipal, clasifica el mapa con los cinco",
      "esquemas del módulo 3 y con k de 3 a 9 clases. Para cada municipio",
      "anota la clase RELATIVA que le toca en cada configuración (0 = la",
      "clase más baja, 1 = la más alta). ¿Cuántos municipios pueden quedar",
      "a la vez en la clase más alta bajo una configuración y en la más",
      "baja bajo otra? Elige uno y explica qué le dirías a alguien que",
      "publica solo uno de los dos mapas."),
    pasos = list(
      list(paso = "Municipios con dato", valor = as.integer(sum(ok))),
      list(paso = "Configuraciones (esquema x k)", valor = length(cfg)),
      list(paso = "Municipios que alcanzan la clase más alta en alguna",
           valor = as.integer(sum(extremo_alto == 1))),
      list(paso = "Municipios que alcanzan la más baja en alguna",
           valor = as.integer(sum(extremo_bajo == 0))),
      list(paso = "Municipios que alcanzan LAS DOS",
           valor = as.integer(sum(camaleon))),
      list(paso = "Recorrido relativo máximo", valor = r10(max(recorrido)))),
    solucion = list(
      n = as.integer(sum(ok)), n_configuraciones = length(cfg),
      n_alcanza_alta = as.integer(sum(extremo_alto == 1)),
      n_alcanza_baja = as.integer(sum(extremo_bajo == 0)),
      n_camaleon = as.integer(sum(camaleon)),
      pct_camaleon = r10(100 * mean(camaleon)),
      recorrido_medio = r10(mean(recorrido)),
      recorrido_max = r10(max(recorrido)),
      ejemplo = list(
        municipio = mun_ok$municipio[i_peor],
        departamento = mun_ok$departamento[i_peor],
        desercion = r10(des[ok][i_peor]),
        config_alta = cfg[which.max(rel[i_peor, ])],
        config_baja = cfg[which.min(rel[i_peor, ])],
        clase_rel_alta = r10(max(rel[i_peor, ])),
        clase_rel_baja = r10(min(rel[i_peor, ])))),
    lectura = paste(
      "La cifra que importa no es cuántos municipios cambian de clase —eso",
      "ya estaba en el módulo 4— sino cuántos admiten LAS DOS lecturas",
      "extremas. Para esos municipios, publicar «está entre los peores del",
      "país» y publicar «está entre los mejores» son las dos defendibles",
      "con el mismo dato y sin mentir en ningún número: lo único que cambia",
      "es una decisión que casi nunca se declara en el pie del mapa. De ahí",
      "la regla del capítulo: el esquema y el k son parte del RESULTADO, y",
      "un mapa sin ellos en la leyenda está incompleto. La contrapartida",
      "honesta es enseñar el mapa junto a su sensibilidad, no elegir el que",
      "conviene.")
  )

  # -------------------------------------------------------------------
  # E2 · Conteo o tasa
  #
  # El módulo 2 dice que el mapa de conteos es el mapa de la población.
  # Aquí el estudiante lo mide y además tiene que DECIDIR qué publicar
  # ante una pregunta concreta.
  # -------------------------------------------------------------------
  message("  E2 · conteo o tasa")
  # `divipola` SE LEE COMO TEXTO, siempre. Dejar que fread lo infiera lo
  # convierte en entero y «05667» pasa a ser 5667: la unión con la capa
  # municipal falla entera o, peor, empareja de menos sin avisar. Es el
  # mismo agujero que el `sprintf("%05d")` de T0.4, ahora al revés.
  # El agregado del MÓDULO 2 —todos los estudiantes con puntaje—, no el
  # de los módulos 8-10, que está filtrado por educación de la madre.
  # Los dos existen y dan cifras parecidas pero distintas; leer el
  # equivocado publicaría un número que no cuadra con el módulo que el
  # ejercicio dice practicar.
  s11 <- data.table::fread("precalculo/salidas/cap3_municipios_conteo_tasa.csv",
                           encoding = "UTF-8", showProgress = FALSE,
                           colClasses = c(divipola = "character"))
  data.table::setnames(s11, "punt", "p")
  r_p <- cor(s11$n, s11$p)
  r_s <- cor(s11$n, s11$p, method = "spearman")
  top_n <- s11[order(-n)][1:20]
  top_p <- s11[order(-p)][1:20]
  sol20 <- length(intersect(top_n$divipola, top_p$divipola))
  # El municipio pequeño que encabeza el mapa de tasas
  peor_n <- s11[order(-p)][1]
  # Cuántos de los 20 mejores por puntaje tienen menos de 50 estudiantes
  chicos <- sum(top_p$n < 50)

  E$e2 <- list(
    titulo = "Conteo o tasa",
    enunciado = paste(
      "Con `cap3_municipios_conteo_tasa.csv` (número de estudiantes y puntaje",
      "medio por municipio), dibuja los dos coropletos: el del conteo y el",
      "de la media. Calcula la correlación de Pearson y la de Spearman",
      "entre las dos variables, y cuenta cuántos municipios comparten el",
      "top-20 de las dos listas. Un periódico te pide un mapa para el",
      "titular «dónde les va peor a los estudiantes». ¿Cuál de los dos",
      "entregas, y qué le añades antes de que se publique?"),
    pasos = list(
      list(paso = "Municipios con dato", valor = as.integer(nrow(s11))),
      list(paso = "Correlación de Pearson conteo-media", valor = r10(r_p)),
      list(paso = "Correlación de Spearman conteo-media", valor = r10(r_s)),
      list(paso = "Municipios en los dos top-20", valor = as.integer(sol20)),
      list(paso = "De los 20 mejores por puntaje, con menos de 50 estudiantes",
           valor = as.integer(chicos))),
    solucion = list(
      n = as.integer(nrow(s11)),
      r_pearson = r10(r_p), r_spearman = r10(r_s),
      solape_top20 = as.integer(sol20),
      n_top20_pequenos = as.integer(chicos),
      primero_por_puntaje = list(municipio = peor_n$municipio,
                                 departamento = peor_n$departamento,
                                 n = as.integer(peor_n$n), punt = r10(peor_n$p)),
      primero_por_conteo = list(municipio = top_n$municipio[1],
                                departamento = top_n$departamento[1],
                                n = as.integer(top_n$n[1]), punt = r10(top_n$p[1]))),
    lectura = paste(
      "El mapa de conteos contesta «dónde hay más estudiantes», que es casi",
      "«dónde vive más gente», y no contesta la pregunta del titular. El de",
      "la media sí la contesta, pero trae su propio problema: los extremos",
      "los ocupan municipios diminutos, donde la media de un puñado de",
      "estudiantes se mueve sola. Así que la respuesta no es «la tasa» a",
      "secas: es la tasa MÁS algo que controle el tamaño —un umbral de n",
      "declarado, un intervalo de confianza por municipio o un suavizado",
      "bayesiano—, y el pie del mapa tiene que decir cuál se usó. Es la",
      "misma decisión que en el capítulo 7 separa un punto caliente real",
      "de uno que solo es un municipio con pocos datos.")
  )

  # -------------------------------------------------------------------
  # E3 · Traza tú las zonas
  #
  # El módulo 9 enseña la distribución de la correlación sobre 1 000
  # particiones. Aquí el estudiante genera las suyas y tiene que EXPLICAR
  # por qué las contiguas y las arbitrarias no dan lo mismo — que es el
  # mecanismo, no el resultado.
  # -------------------------------------------------------------------
  message("  E3 · traza tú las zonas")
  suppressPackageStartupMessages(library(spdep))
  f_nb <- file.path("precalculo", "cache", sprintf("nb_reina_%d.rds", nrow(mun)))
  if (!file.exists(f_nb)) stop("falta la cache del grafo: ejecuta antes genera_cap3.R")
  nb <- readRDS(f_nb)

  s11b <- data.table::fread("precalculo/salidas/cap3_municipios_edu_madre.csv",
                            encoding = "UTF-8", showProgress = FALSE,
                            colClasses = c(divipola = "character"))
  idx <- match(s11b$divipola, mun$divipola)
  s11b <- s11b[!is.na(idx)]; idx <- idx[!is.na(idx)]

  r_zona <- function(z, ponderar = TRUE) {
    dt <- data.table(z = z, n = s11b$n, x = s11b$x, p = s11b$p)[!is.na(z)]
    ag <- if (ponderar) dt[, .(x = sum(n * x) / sum(n), p = sum(n * p) / sum(n)), by = z]
          else          dt[, .(x = mean(x), p = mean(p)), by = z]
    if (nrow(ag) < 3) return(NA_real_)
    cor(ag$x, ag$p)
  }
  crecer <- function(k) {
    n <- length(nb); z <- rep(NA_integer_, n)
    sem <- sample(n, k); z[sem] <- seq_len(k)
    fr <- lapply(seq_len(k), function(j) { v <- nb[[sem[j]]]; v[v > 0 & is.na(z[v])] })
    repeat {
      vivos <- which(vapply(fr, length, integer(1)) > 0)
      if (!length(vivos)) break
      for (j in sample(vivos)) {
        cand <- fr[[j]][is.na(z[fr[[j]]])]
        if (!length(cand)) { fr[[j]] <- integer(0); next }
        i <- cand[sample.int(length(cand), 1)]; z[i] <- j
        nv <- nb[[i]]; nv <- nv[nv > 0]
        fr[[j]] <- unique(c(setdiff(fr[[j]], i), nv[is.na(z[nv])]))
      }
    }
    z
  }
  z_real <- as.integer(factor(substr(s11b$divipola, 1, 2)))
  r_real <- r_zona(z_real)
  tam_real <- as.integer(table(z_real))

  set.seed(3126L)      # semilla PROPIA del ejercicio, distinta de la del capítulo
  N_EJ <- 200L
  rc <- vapply(seq_len(N_EJ), function(i) r_zona(crecer(33L)[idx]), numeric(1))
  ra <- vapply(seq_len(N_EJ), function(i)
    r_zona(rep(seq_along(tam_real), tam_real)[sample(nrow(s11b))]), numeric(1))
  rc_sp <- vapply(seq_len(N_EJ), function(i) r_zona(crecer(33L)[idx], FALSE), numeric(1))
  ra_sp <- vapply(seq_len(N_EJ), function(i)
    r_zona(rep(seq_along(tam_real), tam_real)[sample(nrow(s11b))], FALSE), numeric(1))

  E$e3 <- list(
    titulo = "Traza tú las zonas",
    enunciado = paste(
      "Agrupa los 1 122 municipios en 33 zonas de dos maneras: (a) haciendo",
      "crecer 33 regiones CONTIGUAS desde semillas al azar sobre el grafo de",
      "vecindad, y (b) repartiendo los municipios al azar sin mirar dónde",
      "están, conservando los tamaños de los departamentos reales. Repite",
      "200 veces cada una y calcula, para cada partición, la correlación",
      "entre la educación media de la madre y el puntaje medio de la zona,",
      "ponderando por el número de estudiantes. Compara las dos",
      "distribuciones con la del trazado departamental real. ¿Cuál da",
      "correlaciones más altas, y por qué? Repite sin ponderar y explica el",
      "cambio."),
    pasos = list(
      list(paso = "Correlación con el trazado departamental real", valor = r10(r_real)),
      list(paso = "Contiguas: media de 200", valor = r10(mean(rc))),
      list(paso = "Arbitrarias: media de 200", valor = r10(mean(ra))),
      list(paso = "Contiguas sin ponderar", valor = r10(mean(rc_sp))),
      list(paso = "Arbitrarias sin ponderar", valor = r10(mean(ra_sp)))),
    solucion = list(
      n_replicas = N_EJ, n_zonas = 33L,
      r_real = r10(r_real),
      contiguas = list(media = r10(mean(rc)), sd = r10(sd(rc)),
                       min = r10(min(rc)), max = r10(max(rc)),
                       percentil_real = r10(100 * mean(rc <= r_real))),
      arbitrarias = list(media = r10(mean(ra)), sd = r10(sd(ra)),
                         min = r10(min(ra)), max = r10(max(ra)),
                         percentil_real = r10(100 * mean(ra <= r_real))),
      sin_ponderar = list(contiguas = r10(mean(rc_sp)), arbitrarias = r10(mean(ra_sp)),
                          brecha = r10(mean(ra_sp) - mean(rc_sp))),
      brecha_ponderada = r10(mean(ra) - mean(rc))),
    lectura = paste(
      "Con el ponderador, las zonas arbitrarias dan correlaciones MÁS altas",
      "que las contiguas, que es lo contrario de lo que suele esperarse. El",
      "motivo es el ponderador y no la geografía: una zona arbitraria reúne",
      "municipios de todo el país, así que su media ponderada acaba fijada",
      "por el municipio grande que le tocó, y comparar 33 zonas así se",
      "parece a comparar 33 ciudades grandes —donde la relación es más",
      "fuerte—. Una zona contigua reúne vecinos, que ya se parecen entre sí,",
      "y promediarlos añade poco. Al quitar el ponderador la brecha se",
      "mueve, y ese cambio es la prueba del mecanismo. La moraleja del",
      "ejercicio es doble: el trazado importa, y el PONDERADOR es parte del",
      "trazado aunque no se dibuje.")
  )

  # -------------------------------------------------------------------
  # E4 · Qué publicarías
  #
  # El caso de aviso del estrato. La respuesta correcta NO es un número:
  # es reconocer que el signo depende de una decisión de filtrado y que
  # publicar cualquiera de los dos sin declararla es el error.
  # -------------------------------------------------------------------
  message("  E4 · qué publicarías")
  ve <- data.table::fread("datos/procesado/saber11_20224_submuestra.csv",
                          encoding = "UTF-8", showProgress = FALSE)
  ve <- ve[!is.na(estrato) & !is.na(punt_global)]
  ve[, divipola := sprintf("%05d", as.integer(divipola))]
  em <- ve[, .(n = .N, x = mean(estrato), p = mean(punt_global)), by = divipola]
  UM <- c(0L, 5L, 10L, 25L, 50L)
  barr <- lapply(UM, function(u) {
    s <- em[n >= u]
    list(umbral = u, n_municipios = nrow(s),
         r = if (nrow(s) >= 3) r10(cor(s$x, s$p)) else NA_real_)
  })
  r_ind <- cor(ve$estrato, ve$punt_global)
  r_pond <- stats::cov.wt(cbind(em$x, em$p), wt = em$n, cor = TRUE)$cor[1, 2]
  signos <- unique(sign(vapply(barr, function(b) b$r, numeric(1))))

  E$e4 <- list(
    titulo = "Qué publicarías",
    enunciado = paste(
      "Con la submuestra de Saber 11 (`saber11_20224_submuestra.csv`),",
      "calcula la correlación entre el estrato de vivienda y el puntaje",
      "global a nivel de ESTUDIANTE. Después agrega por municipio y repite",
      "la correlación filtrando por municipios con al menos 0, 5, 10, 25 y",
      "50 estudiantes, y una vez más ponderando por el número de",
      "estudiantes. Anota qué pasa con el signo y con la magnitud. Un",
      "informe oficial va a citar una sola de estas cifras. ¿Cuál dejarías",
      "que citara y qué exigirías que apareciera al lado?"),
    pasos = c(
      list(list(paso = "Estudiantes en la submuestra", valor = as.integer(nrow(ve))),
           list(paso = "Correlación a nivel de estudiante", valor = r10(r_ind))),
      lapply(barr, function(b) list(
        paso = sprintf("Municipal, n >= %d (%d municipios)", b$umbral, b$n_municipios),
        valor = b$r)),
      list(list(paso = "Municipal ponderada por n", valor = r10(r_pond)))),
    solucion = list(
      n_estudiantes = as.integer(nrow(ve)),
      n_municipios = as.integer(nrow(em)),
      r_individuo = r10(r_ind),
      barrido = barr,
      r_ponderada = r10(r_pond),
      cambia_de_signo = length(signos) > 1,
      recorrido = r10(max(vapply(barr, function(b) b$r, numeric(1)), na.rm = TRUE) -
                        min(vapply(barr, function(b) b$r, numeric(1)), na.rm = TRUE))),
    lectura = paste(
      "Ninguna de las cifras es «la» correlación, y esa es la respuesta.",
      "El nivel de análisis y el filtro de tamaño cambian la magnitud y",
      "pueden cambiar el signo, así que citar una sola sin decir cuál es",
      "convierte una decisión metodológica en un hecho. Lo que hay que",
      "exigir al lado es el nivel (individuo o municipio), el filtro y el",
      "ponderador, y —si el informe habla de personas— la advertencia de",
      "que una correlación entre municipios no es una correlación entre",
      "estudiantes: eso es exactamente la falacia ecológica de Robinson",
      "(1950). El caso del estrato está en el material precisamente porque",
      "es el que peor se porta: es el aviso, no el ejemplo.")
  )

  cap3 <- list(
    capitulo = 3,
    titulo = "Cartografía estadística y el MAUP",
    # `Sys.Date()` y no `Sys.time()`, igual que los capítulos 1 y 2. Con la
    # hora y los segundos dentro, este archivo cambiaba en CADA ejecución y
    # el capítulo 3 no podía ser reproducible byte a byte ni corriéndolo dos
    # veces el mismo minuto: `prueba_reproducible.sh` solo sabe perdonar el
    # campo `generado` cuando la diferencia es la fecha, que es la única
    # excepción declarada. Se alinea AHORA, antes de que el capítulo 4 nazca
    # copiando a éste — que es exactamente como el campo `codificacion` de
    # `geo.R` se quedó a medias entre capítulos y costó dos tareas (T0.1, T0.3).
    generado = format(Sys.Date()),
    semilla = SEMILLA, semilla_e3 = 3126L,
    ejercicios = list(E$e1, E$e2, E$e3, E$e4))
  txt3 <- jsonlite::toJSON(cap3, auto_unbox = TRUE, digits = 10,
                           null = "null", na = "null")
  if (grepl('"NA"', txt3, fixed = TRUE))
    stop("cap3_soluciones.json: hay NA escritos como la cadena \"NA\"")
  writeLines(txt3, file.path(SALIDAS, "cap3_soluciones.json"), useBytes = TRUE)
  message(sprintf("  cap3_soluciones.json: %.1f KB",
                  file.size(file.path(SALIDAS, "cap3_soluciones.json")) / 1024))

  message(sprintf("  E1 · %d municipios de %d (%.4f %%) admiten las dos lecturas extremas",
                  E$e1$solucion$n_camaleon, E$e1$solucion$n, E$e1$solucion$pct_camaleon))
  message(sprintf("  E2 · Pearson %+.5f, Spearman %+.5f, solape del top-20: %d",
                  E$e2$solucion$r_pearson, E$e2$solucion$r_spearman, E$e2$solucion$solape_top20))
  message(sprintf("  E3 · real %+.5f · contiguas %+.5f · arbitrarias %+.5f (brecha %+.5f)",
                  E$e3$solucion$r_real, E$e3$solucion$contiguas$media,
                  E$e3$solucion$arbitrarias$media, E$e3$solucion$brecha_ponderada))
  message(sprintf("  E4 · individuo %+.5f; el barrido recorre %.5f y %s de signo",
                  E$e4$solucion$r_individuo, E$e4$solucion$recorrido,
                  if (E$e4$solucion$cambia_de_signo) "CAMBIA" else "no cambia"))
  invisible(E)
}

# =====================================================================
for (cap in CAPS) {
  fn <- get0(paste0("solucion_cap", cap))
  if (is.null(fn)) stop(sprintf("no hay soluciones para el capítulo %d todavía", cap))
  fn()
}
