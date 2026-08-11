# =====================================================================
# genera_cap3.R — el precálculo del capítulo 3 (T2.4)
#
#   «Cartografía estadística y el MAUP» · semana 4
#   Material de Estadística Espacial 2026-II (20929).
#
# QUÉ PRODUCE
#   precalculo/salidas/cap3_datos.json   todas las cifras de los 12 módulos
#   precalculo/salidas/cap3_mapas.json   las fuentes de los .geomapa
#   precalculo/salidas/cap3_*.csv        lo que las pestañas de Python leen
#
# LA REGLA QUE MANDA (D10): ninguna cifra del capítulo se escribe a mano.
# El JSON se guarda con 10 decimales y la prosa publica 5, para que no
# haya doble redondeo entre el texto y el bloque de código.
#
# EL RIESGO PROPIO DE ESTE CAPÍTULO, que el §6 del plan declara: el
# módulo 11 tiene que ser análisis y no editorial. Aquí eso se traduce en
# una regla dura: **el módulo 11 no publica ni una cifra que no salga de
# este script**, y los dos casos históricos que no se pueden medir desde
# aquí —el redlining y la vigilancia predictiva— entran como CITA con
# fuente, marcados como tales, nunca como medida.
#
# LA DECISIÓN DE JAVIER QUE ORDENA LOS MÓDULOS 8, 9 Y 10 (2026-08-05):
# los tres van sobre UN SOLO dato, los microdatos de Saber 11, con sus
# tres niveles reales (estudiante -> municipio -> departamento). Es el
# único conjunto del proyecto que tiene nivel individual, y sin nivel
# individual la falacia ecológica no se puede medir: se afirma. Que los
# tres módulos compartan dato es lo que permite comparar el efecto de
# escala, el de zonificación y la falacia sobre el MISMO número.
#
# POR QUÉ SE RECALCULA LA ESCALERA EN VEZ DE LEER municipios_saber11.csv:
# ese CSV trae `s11_edu_madre_media` calculada con na.rm sobre un
# denominador DISTINTO de `s11_n`. Promediar medias con el peso
# equivocado es el error nº 4 de T0.4 —la columna que miente por su
# nombre— y aquí haría falta justamente el peso correcto para agregar a
# zonas arbitrarias. Se vuelve al microdato y cada media lleva su n.
#
# Ejecutar SIEMPRE con el envoltorio, nunca con `Rscript` a pelo:
#     precalculo/rscript.sh precalculo/genera_cap3.R
# desde la carpeta `Estadistica espacial/`. Ver utf8.R y rscript.sh.
# =====================================================================

suppressPackageStartupMessages({
  library(sf)
  library(spData)
  library(jsonlite)
  library(classInt)
  library(spdep)
  library(cartogram)
  library(RColorBrewer)
  library(data.table)
})

AQUI <- "precalculo"
source(file.path(AQUI, "utf8.R"))     # PRIMERO: para si el proceso no es UTF-8
source(file.path(AQUI, "fuentes.R"))
source(file.path(AQUI, "geo.R"))

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
SEM_PART_CONT <- 3026L   # las 1 000 particiones CONTIGUAS del módulo 9
SEM_PART_ARB  <- 3027L   # las 1 000 particiones ARBITRARIAS del módulo 9
SEM_PUNTOS    <- 3028L   # el dot density del módulo 7
SEM_ESCALA    <- 3029L   # las particiones de la curva de escala del módulo 8

N_PARTICIONES <- 1000L
N_ZONAS       <- 33L     # el número real de departamentos: la comparación
                         # solo es honesta a igual número de zonas

r10 <- function(x) round(as.numeric(x), 10)

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
# 0. LOS DATOS, cargados una sola vez
# =====================================================================
message("0. datos")

PROC <- "datos/procesado"
mun <- carga_municipios(proc = PROC)
ancla(nrow(mun), 1122, "municipios de la capa nacional", tol = 0)

# LOS DEPARTAMENTOS SE DERIVAN DISOLVIENDO LOS MUNICIPIOS, no se leen de
# colombia_adm1.gpkg. Dos motivos, y el segundo es del propio capítulo:
#
#  1. La capa adm1 y la municipal NO comparten los nombres —«Bogota
#     Capital District» contra «Bogotá, D.C.», «Quindío» contra
#     «Quindio»— y unir dos fuentes por el nombre es exactamente lo que
#     rompió T0.4a. El código DIVIPOLA de dos dígitos sí determina el
#     departamento uno a uno (33 parejas para 33 departamentos,
#     comprobado abajo), así que la llave es el código.
#
#  2. El capítulo trata de la agregación. Que los 33 departamentos SEAN
#     la agregación de los 1 122 municipios no es un atajo técnico: es
#     la jerarquía que los módulos 8 y 9 recorren, y construirla aquí
#     garantiza que el nivel departamental y el municipal son el mismo
#     territorio y no dos capas que se parecen.
#
# Se contrasta contra la capa oficial por área, que es una comprobación
# que puede fallar.
mun$cod_dep <- substr(mun$divipola, 1, 2)
llave_dep <- unique(data.table(cod_dep = mun$cod_dep, nombre = mun$departamento))
if (nrow(llave_dep) != 33L)
  stop(sprintf("el codigo de departamento no determina el nombre: %d parejas para 33 codigos",
               nrow(llave_dep)))

f_dep <- file.path(CACHE, sprintf("dep_disuelto_%d.rds", nrow(mun)))
if (file.exists(f_dep)) {
  dep <- readRDS(f_dep)
  message("  departamentos disueltos: de la cache")
} else {
  message("  disolviendo municipios en departamentos (~5 s)...")
  dep <- aggregate(mun[, "cod_dep"], by = list(cod_dep = mun$cod_dep), FUN = function(z) z[1])
  dep <- dep[, "cod_dep"]
  saveRDS(dep, f_dep)
}
ancla(nrow(dep), 33, "departamentos derivados de los municipios", tol = 0)
if (any(!st_is_valid(dep))) stop("la disolucion dejo geometrias invalidas")
dep$nombre <- llave_dep$nombre[match(dep$cod_dep, llave_dep$cod_dep)]
if (any(is.na(dep$nombre))) stop("departamento disuelto sin nombre")

# El contraste externo: la capa oficial adm1 tiene que dar la misma área
# nacional salvo astillas de digitalización.
a_oficial <- sum(as.numeric(st_area(st_read(file.path(PROC, "colombia_adm1.gpkg"), quiet = TRUE))))
a_disuelta <- sum(as.numeric(st_area(dep)))
dif_area <- abs(a_disuelta / a_oficial - 1)
if (dif_area > 0.002)
  stop(sprintf("la disolucion se aparta de la capa oficial un %.4f %%", 100 * dif_area))
message(sprintf("  departamentos disueltos: 33, area a %.6f %% de la capa oficial",
                100 * dif_area))

nc <- st_read(system.file("shape/nc.shp", package = "sf"), quiet = TRUE)
ancla(nrow(nc), 100, "condados de sf::nc", tol = 0)

# El grafo de contigüidad tarda ~44 s sobre 1 122 municipios y hace falta
# en dos módulos. Se cachea; la caché lleva el número de rasgos en el
# nombre para que no pueda servirse una caché de otra capa.
f_nb <- file.path(CACHE, sprintf("nb_reina_%d.rds", nrow(mun)))
if (file.exists(f_nb)) {
  nb <- readRDS(f_nb)
  message("  grafo de contiguidad: de la cache")
} else {
  message("  grafo de contiguidad (poly2nb, ~45 s)...")
  nb <- suppressWarnings(poly2nb(mun, queen = TRUE))
  saveRDS(nb, f_nb)
}
if (length(nb) != nrow(mun)) stop("la cache del grafo no corresponde a esta capa")
N_ISLAS <- sum(card(nb) == 0)
ancla(N_ISLAS, 2, "islas del grafo de contiguidad (T0.4a)", tol = 0)

# ---------------------------------------------------------------------
# Los microdatos de Saber 11. Se lee solo lo que hace falta: el archivo
# son 130 MB y leerlo entero cuesta minutos sin necesidad.
# ---------------------------------------------------------------------
message("  microdatos de Saber 11 (130 MB, solo 5 columnas)...")
EDU_MADRE <- c(
  "Ninguno"                              = 0,
  "Primaria incompleta"                  = 1,
  "Primaria completa"                    = 2,
  "Secundaria (Bachillerato) incompleta" = 3,
  "Secundaria (Bachillerato) completa"   = 4,
  "Técnica o tecnológica incompleta"     = 5,
  "Técnica o tecnológica completa"       = 6,
  "Educación profesional incompleta"     = 7,
  "Educación profesional completa"       = 8,
  "Postgrado"                            = 9)

s11 <- data.table::fread(
  "datos/crudo/saber11_20224.csv", encoding = "UTF-8", showProgress = FALSE,
  select = c("estu_estadoinvestigacion", "cole_cod_mcpio_ubicacion",
             "fami_educacionmadre", "fami_estratovivienda", "punt_global"))
s11 <- s11[estu_estadoinvestigacion == "PUBLICAR"]
ancla(nrow(s11), 1065436, "registros publicables de Saber 11 20224 (T0.4)", tol = 0)

# La guarda de codificación de T0.5: si el locale volviera a romperse, las
# cuatro categorías CON TILDE dejarían de emparejar y el 27,7 % de la
# cohorte saldría del cálculo EN SILENCIO. Aquí para.
s11[, edu_madre := unname(EDU_MADRE[fami_educacionmadre])]
cat_con_tilde <- c("Técnica o tecnológica incompleta", "Técnica o tecnológica completa",
                   "Educación profesional incompleta", "Educación profesional completa")
n_tilde <- sum(s11$fami_educacionmadre %chin% cat_con_tilde)
if (n_tilde < 100000L)
  stop(sprintf(paste("CODIFICACION ROTA: solo %d registros emparejan las categorias acentuadas.",
                     "Es el defecto de T0.5 otra vez: el proceso no esta en UTF-8."), n_tilde))
message(sprintf("  categorias acentuadas: %s registros emparejan (la guarda de T0.5)",
                format(n_tilde, big.mark = " ")))

s11[, estrato := suppressWarnings(as.integer(sub("^Estrato ", "", fami_estratovivienda)))]
s11[!fami_estratovivienda %chin% paste("Estrato", 1:6), estrato := NA_integer_]
cod <- suppressWarnings(as.integer(s11$cole_cod_mcpio_ubicacion))
s11[, divipola := ifelse(is.na(cod), NA_character_, sprintf("%05d", cod))]
s11[, punt_global := as.numeric(punt_global)]

D$fuente <- list(
  n_publicable   = nrow(s11),
  n_municipios   = nrow(mun),
  n_departamentos = nrow(dep),
  n_islas_grafo  = N_ISLAS,
  n_acentuados   = n_tilde)

# =====================================================================
# A. MÓDULO 1 — Del dato al mapa
#
# La idea: un coropleto no es una foto del dato, es el resultado de una
# cadena de decisiones. La pregunta que se contesta con números es
# ¿cuántos mapas DISTINTOS admite el mismo dato?
# =====================================================================
message("A. modulo 1 - del dato al mapa")

ESQUEMAS <- c("equal", "quantile", "fisher", "sd", "headtails")
ESQ_ES <- c(equal = "Intervalos iguales", quantile = "Cuantiles",
            fisher = "Fisher-Jenks", sd = "Desviación estándar",
            headtails = "Head/tails")

des <- mun$desercion
ok_des <- is.finite(des)
message(sprintf("  desercion: %d municipios con dato de %d", sum(ok_des), length(des)))

# ¿Cuántas particiones DISTINTAS produce el mismo dato? Se cuenta la
# firma de la asignación de clase, no los cortes: dos esquemas que
# imprimen cortes distintos pero clasifican igual dan EL MISMO mapa
# (es exactamente el falso negativo del anexo A.2 con Fisher-Jenks).
KS <- 3:9
firmas <- list(); rejilla <- list()
for (e in ESQUEMAS) for (k in KS) {
  cl <- try(geo_cortes(des[ok_des], n = k, estilo = e), silent = TRUE)
  if (inherits(cl, "try-error")) next
  fir <- paste(cl$clase, collapse = ",")
  firmas[[length(firmas) + 1L]] <- fir
  rejilla[[length(rejilla) + 1L]] <- list(
    esquema = e, k = k, n_clases_usadas = length(unique(cl$clase)),
    tam = as.integer(cl$tam))
}
n_config  <- length(firmas)
n_mapas_distintos <- length(unique(unlist(firmas)))

# Las clases VACÍAS son un fallo silencioso del esquema, no un detalle de
# estética: la leyenda anuncia k clases y el mapa pinta menos.
vacias <- Filter(function(r) r$n_clases_usadas < r$k, rejilla)

D$m1 <- list(
  n_con_dato = sum(ok_des),
  n_configuraciones = n_config,
  n_mapas_distintos = n_mapas_distintos,
  pct_distintos = r10(100 * n_mapas_distintos / n_config),
  ks = as.integer(range(KS)),
  n_esquemas = length(ESQUEMAS),
  n_con_clase_vacia = length(vacias),
  clases_vacias = lapply(vacias, function(r)
    list(esquema = r$esquema, k = r$k, usadas = r$n_clases_usadas)),
  desercion = list(
    media = r10(mean(des[ok_des])), sd = r10(sd(des[ok_des])),
    min = r10(min(des[ok_des])), max = r10(max(des[ok_des])),
    mediana = r10(median(des[ok_des]))))
message(sprintf("  %d configuraciones -> %d mapas distintos (%.2f %%); %d con clase vacia",
                n_config, n_mapas_distintos, D$m1$pct_distintos, length(vacias)))

# =====================================================================
# B. MÓDULO 2 — Normalizar o mentir
#
# El mapa de conteos es el mapa de la población. Se demuestra con el
# número de estudiantes de Saber 11 por municipio (conteo) frente al
# puntaje medio (tasa): dos mapas del mismo dato que ordenan el país de
# formas que casi no se solapan.
# =====================================================================
message("B. modulo 2 - normalizar o mentir")

agr <- s11[!is.na(divipola) & !is.na(punt_global),
           .(n = .N, punt = mean(punt_global)), by = divipola]
mm <- merge(data.table(divipola = mun$divipola, municipio = mun$municipio,
                       depto = mun$departamento),
            agr, by = "divipola", all.x = TRUE)
mm <- mm[!is.na(n)]

r_pearson  <- cor(mm$n, mm$punt)
r_spearman <- cor(mm$n, mm$punt, method = "spearman")

top_n    <- mm[order(-n)][1:20]
top_punt <- mm[order(-punt)][1:20]
solape20 <- length(intersect(top_n$divipola, top_punt$divipola))

D$m2 <- list(
  n_municipios = nrow(mm),
  n_estudiantes = sum(mm$n),
  r_conteo_tasa = r10(r_pearson),
  rho_conteo_tasa = r10(r_spearman),
  solape_top20 = solape20,
  top10_conteo = lapply(seq_len(10), function(i)
    list(municipio = top_n$municipio[i], depto = top_n$depto[i],
         n = top_n$n[i], punt = r10(top_n$punt[i]),
         rango_por_punt = which(order(-mm$punt) == which(mm$divipola == top_n$divipola[i])))),
  top10_tasa = lapply(seq_len(10), function(i)
    list(municipio = top_punt$municipio[i], depto = top_punt$depto[i],
         n = top_punt$n[i], punt = r10(top_punt$punt[i]))),
  # La cifra que cierra el módulo: qué fracción de los estudiantes vive
  # en los 10 municipios que el mapa de conteos pinta más oscuros.
  pct_estudiantes_top10 = r10(100 * sum(top_n$n[1:10]) / sum(mm$n)),
  pct_municipios_top10  = r10(100 * 10 / nrow(mm)))
message(sprintf("  r(conteo, tasa) = %+.5f  rho = %+.5f  ·  solape del top-20: %d de 20",
                r_pearson, r_spearman, solape20))
message(sprintf("  los 10 municipios mas oscuros del mapa de conteos son el %.5f %% de los municipios y el %.5f %% de los estudiantes",
                D$m2$pct_municipios_top10, D$m2$pct_estudiantes_top10))

# =====================================================================
# C. MÓDULO 3 — Esquemas de clasificación
#
# Las definiciones, sobre el dato canónico donde vive el hallazgo A.2:
# `nc` y su SID74. Aquí se calcula el lado de R; el auditor recalcula el
# de Python con mapclassify y la discrepancia queda DECLARADA.
# =====================================================================
message("C. modulo 3 - esquemas de clasificacion")

sid <- nc$SID74
cl_nc <- lapply(ESQUEMAS, function(e) {
  cl <- geo_cortes(sid, n = 5, estilo = e)
  list(esquema = e, etiqueta = unname(ESQ_ES[e]),
       cortes = r10(cl$cortes), tam = as.integer(cl$tam),
       n_usadas = length(unique(cl$clase)))
})
names(cl_nc) <- ESQUEMAS

# El corazón de A.2: los EMPATES justo en los cortes de cuantiles. Es la
# causa de que R y Python clasifiquen distinto, y se cuenta, no se deduce.
cortes_q <- geo_cortes(sid, n = 5, estilo = "quantile")$cortes
empates <- lapply(cortes_q[-c(1, length(cortes_q))], function(c0)
  list(corte = r10(c0), n_iguales = sum(sid == c0)))
n_empatados <- sum(vapply(empates, function(e) e$n_iguales, integer(1)))

D$m3 <- list(
  dato = "sf::nc, SID74 (muertes subitas de lactantes, 1974-78)",
  n = nrow(nc), k = 5L,
  esquemas = unname(cl_nc),
  cortes_cuantiles = r10(cortes_q),
  empates_en_cortes = empates,
  n_empatados = n_empatados,
  # La convención, dicha en voz alta: classInt cierra por la izquierda.
  convenio_r = "[a, b)", convenio_python = "(a, b]",
  sid_resumen = list(min = min(sid), max = max(sid), media = r10(mean(sid)),
                     n_ceros = sum(sid == 0)))
message(sprintf("  SID74: %d condados empatados justo en los cortes de cuantiles", n_empatados))
for (e in ESQUEMAS)
  message(sprintf("    %-20s tam = %s", ESQ_ES[e], paste(cl_nc[[e]]$tam, collapse = "/")))

# =====================================================================
# D. MÓDULO 4 — El mismo dato, cinco mapas
#
# El simulador estrella. Sobre la deserción municipal, con k = 5: cuántos
# municipios cambian de clase al cambiar de esquema, para las diez
# parejas. Y cuál es el municipio que más baila.
# =====================================================================
message("D. modulo 4 - el mismo dato, cinco mapas")

clases5 <- sapply(ESQUEMAS, function(e) geo_cortes(des[ok_des], 5, e)$clase)
colnames(clases5) <- ESQUEMAS

pares <- list()
for (i in 1:(length(ESQUEMAS) - 1)) for (j in (i + 1):length(ESQUEMAS)) {
  a <- ESQUEMAS[i]; b <- ESQUEMAS[j]
  dif <- mean(clases5[, a] != clases5[, b])
  pares[[length(pares) + 1L]] <- list(
    a = a, b = b, etiqueta_a = unname(ESQ_ES[a]), etiqueta_b = unname(ESQ_ES[b]),
    pct_cambian = r10(100 * dif))
}
pct <- vapply(pares, function(p) p$pct_cambian, numeric(1))
par_max <- pares[[which.max(pct)]]; par_min <- pares[[which.min(pct)]]

# El municipio más volátil: cuántas clases DISTINTAS recibe según el
# esquema. Que un municipio pueda ser a la vez «clase 1» y «clase 5» es
# el argumento del capítulo en una sola unidad.
n_clases_por_mun <- apply(clases5, 1, function(v) length(unique(v)))
rango_por_mun <- apply(clases5, 1, function(v) max(v) - min(v))
i_volatil <- which.max(rango_por_mun)
mun_ok <- mun[ok_des, ]

D$m4 <- list(
  k = 5L, n = sum(ok_des),
  pares = pares,
  par_mas_discordante = par_max, par_mas_concordante = par_min,
  pct_max = r10(max(pct)), pct_min = r10(min(pct)),
  # Cuántos municipios reciben la MISMA clase en los cinco esquemas
  n_estables = sum(n_clases_por_mun == 1L),
  pct_estables = r10(100 * mean(n_clases_por_mun == 1L)),
  rango_max = as.integer(max(rango_por_mun)),
  n_con_rango_max = sum(rango_por_mun == max(rango_por_mun)),
  municipio_volatil = list(
    municipio = mun_ok$municipio[i_volatil],
    depto = mun_ok$departamento[i_volatil],
    desercion = r10(des[ok_des][i_volatil]),
    clases = as.integer(clases5[i_volatil, ]),
    esquemas = ESQUEMAS),
  # Tamaño de la clase más alta según el esquema: el mapa "de alarma"
  n_en_clase_alta = as.integer(apply(clases5, 2, function(v) sum(v == 5))))
message(sprintf("  cambian de clase: de %.5f %% (%s vs %s) a %.5f %% (%s vs %s)",
                min(pct), par_min$a, par_min$b, max(pct), par_max$a, par_max$b))
message(sprintf("  estables en los 5 esquemas: %d de %d (%.5f %%); rango maximo %d clases",
                D$m4$n_estables, sum(ok_des), D$m4$pct_estables, D$m4$rango_max))
message(sprintf("  en la clase mas alta: %s municipios segun el esquema",
                paste(D$m4$n_en_clase_alta, collapse = "/")))

# =====================================================================
# E. MÓDULO 5 — Color
#
# La medida: la distancia perceptual MÍNIMA entre clases contiguas, en
# CIELAB, con visión normal y bajo los tres tipos de daltonismo. Una
# paleta no se rompe cuando "se ve rara": se rompe cuando dos clases
# vecinas dejan de distinguirse.
# =====================================================================
message("E. modulo 5 - color")

# La autoprueba de geo_cvd contra colorspace PARA si discrepan.
PALETA_PRUEBA <- unique(c(brewer.pal(9, "Set1"), brewer.pal(9, "YlOrRd"),
                          brewer.pal(9, "RdYlGn"), brewer.pal(9, "Blues"),
                          brewer.pal(11, "Spectral"), brewer.pal(8, "Dark2")))
n_cvd_ok <- geo_cvd_autoprueba(PALETA_PRUEBA)

PALETAS <- list(
  list(id = "YlOrRd",   tipo = "secuencial",  k = 5),
  list(id = "Blues",    tipo = "secuencial",  k = 5),
  list(id = "RdYlGn",   tipo = "divergente",  k = 5),
  list(id = "Spectral", tipo = "divergente",  k = 5),
  list(id = "RdBu",     tipo = "divergente",  k = 5),
  list(id = "Set1",     tipo = "cualitativo", k = 5),
  list(id = "Dark2",    tipo = "cualitativo", k = 5))

TIPOS_CVD <- c("deuteranopia", "protanopia", "tritanopia")
pal_med <- lapply(PALETAS, function(p) {
  cc <- brewer.pal(p$k, p$id)
  base <- geo_paleta_dmin(cc)
  sim <- lapply(TIPOS_CVD, function(tp) {
    cs <- geo_cvd(cc, tp)
    list(tipo = tp, colores = cs, dmin = r10(geo_paleta_dmin(cs)),
         caida_pct = r10(100 * (1 - geo_paleta_dmin(cs) / base)))
  })
  names(sim) <- TIPOS_CVD
  list(id = p$id, tipo = p$tipo, k = p$k, colores = cc,
       dmin_normal = r10(base), simulaciones = unname(sim),
       # La luminosidad: la variable que decide si una paleta rojo-verde
       # sobrevive al daltonismo o no.
       luminosidad = r10(methods::as(colorspace::hex2RGB(cc), "LAB")@coords[, 1]),
       rango_luminosidad = r10(diff(range(methods::as(colorspace::hex2RGB(cc), "LAB")@coords[, 1]))))
})

# La pareja crítica: rojo y verde a IGUAL luminosidad, que es el caso que
# de verdad se rompe bajo daltonismo.
#
# NO se eligen a ojo. La primera versión usaba el rojo y el verde de la
# paleta de Tableau (#D62728 y #2CA02C) y los presentaba como «a igual
# luminosidad»: **no lo están** —L* 46,85 y 57,90, once puntos— y el
# capítulo habría afirmado algo falso que además le quitaba la fuerza al
# argumento, porque parte de la distancia que sobrevive es luminosidad.
# Lo cazó el auditor, que mide el L* en vez de creérselo.
#
# Se construyen en HCL, donde la luminosidad es un parámetro: mismo L,
# mismo C, dos matices opuestos. Así la igualdad es por CONSTRUCCIÓN, y
# la guarda de abajo comprueba que la construcción hizo lo que dice.
L_RV <- 55; C_RV <- 60
rojo_verde <- colorspace::hex(colorspace::polarLUV(
  L = c(L_RV, L_RV), C = c(C_RV, C_RV), H = c(25, 135)), fixup = TRUE)
lab_rv <- methods::as(colorspace::hex2RGB(rojo_verde), "LAB")@coords
if (abs(diff(lab_rv[, 1])) > 1.5)
  stop(sprintf("la pareja rojo/verde NO esta a igual luminosidad: L* %.2f y %.2f",
               lab_rv[1, 1], lab_rv[2, 1]))
dE <- function(a, b) sqrt(sum((a - b)^2))
d_rv_normal <- dE(lab_rv[1, ], lab_rv[2, ])
rv_deu <- geo_cvd(rojo_verde, "deuteranopia")
lab_rv_deu <- methods::as(colorspace::hex2RGB(rv_deu), "LAB")@coords
d_rv_deu <- dE(lab_rv_deu[1, ], lab_rv_deu[2, ])

D$m5 <- list(
  n_comparaciones_cvd = n_cvd_ok,
  n_colores_probados = length(PALETA_PRUEBA),
  paletas = pal_med,
  tipos = TIPOS_CVD,
  # Las anclas que el navegador tiene que reproducir. Sin esto, la
  # implementación en JS no tendría contra qué compararse y podría
  # divergir de la de R sin que nadie lo notara.
  anclas_cvd = lapply(TIPOS_CVD, function(tp)
    list(tipo = tp, entrada = PALETA_PRUEBA, salida = geo_cvd(PALETA_PRUEBA, tp))),
  matriz_deuteranopia = r10(as.numeric(t(geo_cvd_matriz("deuteranopia")))),
  matriz_protanopia   = r10(as.numeric(t(geo_cvd_matriz("protanopia")))),
  matriz_tritanopia   = r10(as.numeric(t(geo_cvd_matriz("tritanopia")))),
  rojo_verde = list(
    colores = rojo_verde, simulado = rv_deu,
    luminosidad = r10(lab_rv[, 1]),
    dE_normal = r10(d_rv_normal), dE_deuteranopia = r10(d_rv_deu),
    caida_pct = r10(100 * (1 - d_rv_deu / d_rv_normal))))
message(sprintf("  geo_cvd: %d comparaciones identicas a colorspace", n_cvd_ok))
for (p in pal_med)
  message(sprintf("    %-9s %-11s dmin %7.3f -> deuteranopia %7.3f (%+.2f %%)  rango L* %6.2f",
                  p$id, p$tipo, p$dmin_normal, p$simulaciones[[1]]$dmin,
                  -p$simulaciones[[1]]$caida_pct, p$rango_luminosidad))
message(sprintf("  rojo/verde a igual luminosidad: dE %.5f -> %.5f (%.5f %% menos)",
                d_rv_normal, d_rv_deu, D$m5$rojo_verde$caida_pct))

# =====================================================================
# F. MÓDULO 6 — tmap
#
# El módulo es de código, no de cifras: lo que hay que fijar aquí es la
# VERSIÓN y la sintaxis, porque tmap 4 rompió la de tmap 3 y casi todo lo
# que hay escrito por ahí es de la 3.
# =====================================================================
message("F. modulo 6 - tmap")

suppressPackageStartupMessages(library(tmap))
v_tmap <- as.character(packageVersion("tmap"))
if (as.integer(sub("\\..*", "", v_tmap)) < 4L)
  stop("este capitulo documenta la API de tmap 4; la instalada es ", v_tmap)
# Que los verbos que el capítulo va a escribir EXISTEN de verdad en esta
# versión. Escribir de memoria una función que no existe es el defecto
# nº 4 de A.13, y ahí costó un ReferenceError que tumbó el capítulo.
VERBOS <- c("tm_shape", "tm_polygons", "tm_fill", "tm_borders", "tm_bubbles",
            "tm_dots", "tm_facets", "tm_layout", "tm_scale_intervals",
            "tm_scale_continuous", "tm_scale_categorical", "tm_legend")
faltan <- VERBOS[!VERBOS %in% ls("package:tmap")]
if (length(faltan)) stop("verbos de tmap que el capitulo usa y no existen: ",
                         paste(faltan, collapse = ", "))
D$m6 <- list(version_tmap = v_tmap,
             verbos_verificados = VERBOS,
             n_verbos = length(VERBOS),
             version_ggplot2 = as.character(packageVersion("ggplot2")))
message(sprintf("  tmap %s: %d verbos verificados contra el paquete instalado",
                v_tmap, length(VERBOS)))

# =====================================================================
# G. MÓDULO 7 — Más allá del coropleto
#
# Cuatro alternativas al coropleto, sobre los 33 departamentos y con el
# número de estudiantes de Saber 11 como valor. Cada una con la medida
# que la juzga, no con un adjetivo.
# =====================================================================
message("G. modulo 7 - mas alla del coropleto")

# Valor por departamento: número de estudiantes (un conteo, que es
# justo lo que el coropleto no debe pintar y el cartograma sí).
s11_dep <- s11[!is.na(divipola) & !is.na(punt_global),
               .(n = .N, punt = mean(punt_global)), by = .(cod_dep = substr(divipola, 1, 2))]
# La unión es por CÓDIGO, nunca por nombre (ver el bloque 0). Y se
# comprueba que no queda ningún departamento sin dato: un NA aquí
# viajaría hasta el cartograma y saldría como un polígono de área cero.
i_dep <- match(dep$cod_dep, s11_dep$cod_dep)
if (any(is.na(i_dep)))
  stop(sprintf("departamentos sin dato de Saber 11: %s",
               paste(dep$nombre[is.na(i_dep)], collapse = ", ")))
dep$n_est <- s11_dep$n[i_dep]
dep$punt  <- s11_dep$punt[i_dep]
ancla(sum(dep$n_est), sum(s11_dep$n), "estudiantes repartidos en los 33 departamentos", tol = 0)

area_dep <- as.numeric(st_area(dep))

# --- Los tres cartogramas -------------------------------------------
carto_n <- geo_carto_ncont(dep, dep$n_est)
carto_d <- geo_carto_dorling(dep, dep$n_est, k = 20)
# El contiguo es iterativo y NO alcanza la proporcionalidad exacta: tiene
# que conservar la topología, y esa restricción compite con el área. En
# vez de publicar una sola cifra y dejarla parecer un defecto de
# implementación, se barre el número de iteraciones para enseñar que
# converge... a algo que no es 1.
message("  cartograma contiguo (Dougenik, iterativo, barrido)...")
ITERS <- c(1L, 5L, 20L, 60L)
ITER_CONT <- 60L
f_cc <- file.path(CACHE, "carto_cont.rds")
if (file.exists(f_cc)) {
  cc_cache <- readRDS(f_cc); barrido_cont <- cc_cache$barrido; carto_c <- cc_cache$carto
  message("    del cache")
} else {
  barrido_cont <- lapply(ITERS, function(it) {
    cc <- suppressWarnings(cartogram_cont(dep, "n_est", itermax = it, verbose = FALSE))
    a <- as.numeric(st_area(cc))
    list(itermax = it, corr = r10(cor(a, dep$n_est)),
         max_error_rel = r10(max(abs(a / dep$n_est / mean(a / dep$n_est) - 1))))
  })
  carto_c <- suppressWarnings(cartogram_cont(dep, "n_est", itermax = ITER_CONT, verbose = FALSE))
  saveRDS(list(barrido = barrido_cont, carto = carto_c), f_cc)
}

prop_exacta <- function(g, v) {
  a <- as.numeric(st_area(g))
  list(corr = r10(cor(a, v)),
       max_error_rel = r10(max(abs(a / v / mean(a / v) - 1))))
}
p_ncont <- prop_exacta(carto_n, dep$n_est)
p_dorl  <- prop_exacta(carto_d, dep$n_est)
p_cont  <- prop_exacta(carto_c, dep$n_est)

# El contraste externo: el paquete implementa el mismo Olson con otra
# normalización, así que las áreas solo pueden diferir en un FACTOR
# GLOBAL. Si la razón no fuera constante, una de las dos estaría mal.
carto_n_pkg <- cartogram_ncont(dep, "n_est")
rz <- as.numeric(st_area(carto_n)) / as.numeric(st_area(carto_n_pkg))
cv_rz <- sd(rz) / mean(rz)
if (cv_rz > 1e-8)
  stop(sprintf("el Olson propio y el del paquete no difieren en un factor global: cv = %.3e", cv_rz))
ancla(p_ncont$corr, 1, "Olson: corr(area, valor) exacta", tol = 1e-9)
ancla(p_dorl$corr,  1, "Dorling: corr(area, valor) exacta", tol = 1e-9)

# --- Dot density: el mismo mapa con dos semillas ---------------------
# Un punto por cada N estudiantes, colocado al azar dentro del polígono.
# La medida que importa: el mapa CAMBIA con la semilla, y eso es una
# propiedad del método, no un descuido.
POR_PUNTO <- 2000L
n_pts <- pmax(1L, round(dep$n_est / POR_PUNTO))
muestrea <- function(semilla) {
  set.seed(semilla)
  pts <- lapply(seq_len(nrow(dep)), function(i)
    st_coordinates(st_sample(dep[i, ], n_pts[i], type = "random", exact = TRUE)))
  do.call(rbind, pts)
}
dd1 <- muestrea(SEM_PUNTOS)
dd2 <- muestrea(SEM_PUNTOS + 1L)
# Distancia media al punto más próximo del OTRO sorteo: cuánto se mueve
# el mapa cuando solo cambia la semilla.
d12 <- as.numeric(st_distance(st_as_sf(as.data.frame(dd1), coords = c("X", "Y"), crs = st_crs(dep)),
                              st_as_sf(as.data.frame(dd2), coords = c("X", "Y"), crs = st_crs(dep))))
d12 <- matrix(d12, nrow = nrow(dd1))
dmin12 <- apply(d12, 1, min)

# --- Hexbin ----------------------------------------------------------
hexes <- st_make_grid(dep, cellsize = 120000, square = FALSE)
hexes <- st_sf(id_hex = seq_along(hexes), geometry = hexes)
hexes <- hexes[lengths(st_intersects(hexes, dep)) > 0, ]
hexes$id_hex <- seq_len(nrow(hexes))

# Se reparte el conteo departamental proporcionalmente al ÁREA de la
# intersección: es una reagregación, o sea el MAUP otra vez, y el
# capítulo lo dice en voz alta en vez de presentar el hexbin como una
# vista neutra del dato.
#
# El reparto se agrupa por IDENTIFICADOR, nunca por el valor. La primera
# versión hacía `by = n_est` y funcionaba solo porque los 33 conteos
# resultan ser distintos entre sí: el día que dos departamentos
# empataran, sus áreas se sumarían juntas y el reparto saldría mal sin
# avisar. Es el mismo patrón que el error nº 4 de T0.4.
dep_r <- dep
dep_r$id_dep <- seq_len(nrow(dep_r))
inter <- suppressWarnings(st_intersection(st_make_valid(hexes),
                                          st_make_valid(dep_r[, c("id_dep", "n_est")])))
inter_dt <- as.data.table(st_drop_geometry(inter))
inter_dt[, a := as.numeric(st_area(inter))]
inter_dt[, a_dep := sum(a), by = id_dep]
hex_val <- inter_dt[, .(v = sum(n_est * a / a_dep)), by = id_hex]
hexes$v <- 0
hexes$v[match(hex_val$id_hex, hexes$id_hex)] <- hex_val$v

# La comprobación que puede fallar: el reparto conserva el total. Si un
# trozo de departamento cayera fuera de todo hexágono, aquí se vería.
err_hex <- abs(sum(hexes$v) - sum(dep$n_est)) / sum(dep$n_est)
if (err_hex > 1e-9)
  stop(sprintf("el reparto al hexbin pierde el %.3e del total: hay area sin hexagono", err_hex))

D$m7 <- list(
  n_departamentos = nrow(dep),
  valor = "estudiantes de Saber 11 por departamento",
  total_estudiantes = sum(dep$n_est),
  cartogramas = list(
    list(id = "ncont", nombre = "No contiguo (Olson 1976)", origen = "implementacion propia",
         corr = p_ncont$corr, max_error_rel = p_ncont$max_error_rel),
    list(id = "dorling", nombre = "Dorling (1996)", origen = "implementacion propia",
         corr = p_dorl$corr, max_error_rel = p_dorl$max_error_rel,
         iteraciones = as.integer(carto_d$.carto_iter[1])),
    list(id = "cont", nombre = "Contiguo (Dougenik et al. 1985)", origen = "paquete cartogram",
         corr = p_cont$corr, max_error_rel = p_cont$max_error_rel, itermax = ITER_CONT)),
  barrido_contiguo = barrido_cont,
  contraste_olson = list(cv_razon = r10(cv_rz), factor = r10(mean(rz))),
  dot_density = list(
    por_punto = POR_PUNTO, n_puntos = nrow(dd1),
    dmin_media_km = r10(mean(dmin12) / 1000),
    dmin_mediana_km = r10(median(dmin12) / 1000),
    dmin_max_km = r10(max(dmin12) / 1000)),
  hexbin = list(n_hexagonos = nrow(hexes), lado_km = 120,
                error_reparto_rel = r10(err_hex),
                n_con_valor = sum(hexes$v > 0)),
  simbolos = list(
    radio_max_rel = r10(sqrt(max(dep$n_est) / min(dep$n_est))),
    razon_valor = r10(max(dep$n_est) / min(dep$n_est))))
message(sprintf("  Olson propio corr = %.10f · Dorling propio corr = %.10f · Dougenik corr = %.10f",
                p_ncont$corr, p_dorl$corr, p_cont$corr))
for (b in barrido_cont)
  message(sprintf("    Dougenik itermax=%-3d corr = %.10f  (error max rel %.5f)",
                  b$itermax, b$corr, b$max_error_rel))
message(sprintf("  contraste con el paquete: la razon de areas es constante (cv = %.2e)", cv_rz))
message(sprintf("  dot density: %d puntos; al cambiar la semilla se mueven %.5f km de media",
                nrow(dd1), D$m7$dot_density$dmin_media_km))
message(sprintf("  hexbin: %d hexagonos, error de reparto %.3e", nrow(hexes), err_hex))

# =====================================================================
# H. MÓDULO 8 — MAUP I, el efecto escala
#
# La escalera de Saber 11, recalculada desde el microdato, y la curva de
# la correlación frente al NÚMERO de zonas. Las zonas intermedias son
# particiones contiguas aleatorias de los municipios: la única forma de
# tener escalas que no existen administrativamente.
# =====================================================================
message("H. modulo 8 - MAUP, efecto escala")

v <- s11[!is.na(edu_madre) & !is.na(punt_global) & !is.na(divipola),
         .(divipola, edu_madre, punt_global)]
r_ind <- cor(v$edu_madre, v$punt_global)
por_mun <- v[, .(n = .N, x = mean(edu_madre), p = mean(punt_global)), by = divipola]
por_dep <- v[, .(n = .N, x = mean(edu_madre), p = mean(punt_global)),
             by = .(dpto = substr(divipola, 1, 2))]
r_mun <- cor(por_mun$x, por_mun$p)
r_dep <- cor(por_dep$x, por_dep$p)

# Las cifras de T0.4, que están publicadas: tienen que salir otra vez.
ancla(round(r_ind, 4), 0.3627, "escalera de T0.4: r individual", tol = 1e-4)
ancla(round(r_dep, 4), 0.5126, "escalera de T0.4: r departamental", tol = 1e-4)
message(sprintf("  escalera: individuo %+.5f -> municipio %+.5f -> departamento %+.5f",
                r_ind, r_mun, r_dep))

# --- La partición contigua aleatoria ---------------------------------
# Crecimiento de regiones desde k semillas sobre el grafo de contigüidad.
# Los municipios que quedan sin alcanzar (las 2 islas y lo que cuelgue de
# ellas) se declaran, no se rellenan a la fuerza.
particion_contigua <- function(nb, k) {
  n <- length(nb)
  z <- rep(NA_integer_, n)
  semillas <- sample(n, k)
  z[semillas] <- seq_len(k)
  frontera <- lapply(seq_len(k), function(j) {
    v <- nb[[semillas[j]]]; v[v > 0 & is.na(z[v])]
  })
  repeat {
    vivos <- which(vapply(frontera, length, integer(1)) > 0)
    if (!length(vivos)) break
    for (j in sample(vivos)) {
      cand <- frontera[[j]][is.na(z[frontera[[j]]])]
      if (!length(cand)) { frontera[[j]] <- integer(0); next }
      i <- cand[sample.int(length(cand), 1)]
      z[i] <- j
      nuevos <- nb[[i]]; nuevos <- nuevos[nuevos > 0]
      frontera[[j]] <- unique(c(setdiff(frontera[[j]], i), nuevos[is.na(z[nuevos])]))
    }
  }
  z
}

# Índice de los municipios que tienen dato, en el orden de la capa
idx_mun <- match(por_mun$divipola, mun$divipola)
tiene <- !is.na(idx_mun)
por_mun_ok <- por_mun[tiene]; idx_ok <- idx_mun[tiene]

# ---------------------------------------------------------------------
# DOS ESCALERAS, Y LA DIFERENCIA ENTRE ELLAS ES MATERIAL DEL MÓDULO 11.
#
# `r_dep` de arriba agrega TODOS los estudiantes con código de municipio.
# Pero una parte de ellos vive en municipios que el mapa no tiene —los
# huérfanos de T0.4: Belén de Bajirá y compañía—, así que en cuanto el
# análisis pasa por la geometría esos estudiantes desaparecen.
#
# Los módulos 8 y 9 tienen que usar la escalera CARTOGRÁFICA (solo lo
# que existe en el mapa), o compararían una partición real calculada
# sobre 1 065 436 estudiantes con particiones aleatorias calculadas sobre
# menos. Lo detectó el ancla de coherencia de abajo, que es justo para
# lo que estaba puesta.
#
# Y la diferencia entre las dos no se esconde: se publica. Es la cifra
# que sostiene el módulo 11 —quien no tiene polígono no sale en el mapa,
# y no salir en el mapa mueve el resultado— y se mide, no se afirma.
# ---------------------------------------------------------------------
v_mapa <- v[divipola %chin% mun$divipola]
por_dep_mapa <- v_mapa[, .(n = .N, x = mean(edu_madre), p = mean(punt_global)),
                       by = .(cod_dep = substr(divipola, 1, 2))]
r_dep_mapa <- cor(por_dep_mapa$x, por_dep_mapa$p)
r_ind_mapa <- cor(v_mapa$edu_madre, v_mapa$punt_global)
n_fuera <- nrow(v) - nrow(v_mapa)
message(sprintf("  estudiantes fuera del mapa: %s (%.5f %%); r departamental %+.5f -> %+.5f",
                format(n_fuera, big.mark = " "), 100 * n_fuera / nrow(v), r_dep, r_dep_mapa))

# La correlación de una partición: medias de zona PONDERADAS por el
# número de estudiantes. Promediar medias municipales sin peso mezclaría
# un municipio de 2 estudiantes con uno de 30 000.
r_de_zona <- function(z_mun, ponderar = TRUE) {
  dt <- data.table(z = z_mun, n = por_mun_ok$n, x = por_mun_ok$x, p = por_mun_ok$p)
  dt <- dt[!is.na(z)]
  ag <- if (ponderar)
    dt[, .(x = sum(n * x) / sum(n), p = sum(n * p) / sum(n)), by = z]
  else
    dt[, .(x = mean(x), p = mean(p)), by = z]
  if (nrow(ag) < 3) return(NA_real_)
  cor(ag$x, ag$p)
}
# Ancla de coherencia: con la partición departamental REAL, esta función
# tiene que devolver exactamente la correlación departamental CARTOGRÁFICA.
# Si no, o el ponderador está mal o los dos lados no cubren la misma
# población. La primera versión la comparaba contra `r_dep` —el de todos
# los estudiantes— y el ancla paró: la diferencia eran los huérfanos.
z_real <- as.integer(factor(substr(por_mun_ok$divipola, 1, 2)))
ancla(r_de_zona(z_real), r_dep_mapa,
      "r_de_zona() reproduce la particion departamental real", tol = 1e-9)

ESCALAS <- c(5L, 10L, 20L, 33L, 50L, 100L, 200L, 400L, 700L)
N_REP_ESCALA <- 30L
set.seed(SEM_ESCALA)
curva <- lapply(ESCALAS, function(k) {
  rs <- vapply(seq_len(N_REP_ESCALA), function(i) {
    z <- particion_contigua(nb, k)
    r_de_zona(z[idx_ok])
  }, numeric(1))
  rs <- rs[is.finite(rs)]
  list(zonas = k, n_rep = length(rs), media = r10(mean(rs)), sd = r10(sd(rs)),
       min = r10(min(rs)), max = r10(max(rs)))
})

D$m8 <- list(
  variable = "educacion de la madre (0-9) vs. puntaje global",
  n_estudiantes = nrow(v),
  n_municipios = nrow(por_mun), n_departamentos = nrow(por_dep),
  r_individuo = r10(r_ind), r_municipio = r10(r_mun), r_departamento = r10(r_dep),
  subida_ind_dep_pct = r10(100 * (r_dep / r_ind - 1)),
  # La escalera CARTOGRÁFICA: la que usan los módulos 8 y 9, porque es la
  # única que cubre la misma población que las particiones aleatorias.
  cartografica = list(
    n_estudiantes = nrow(v_mapa),
    n_fuera_del_mapa = n_fuera,
    pct_fuera = r10(100 * n_fuera / nrow(v)),
    r_individuo = r10(r_ind_mapa),
    r_departamento = r10(r_dep_mapa),
    desvio_departamental = r10(r_dep - r_dep_mapa)),
  curva = curva, n_rep = N_REP_ESCALA, escalas = as.integer(ESCALAS),
  # La descomposición que EXPLICA el efecto: al agregar se tira la
  # varianza de dentro y solo sobrevive la de entre.
  var_total = r10(var(v$punt_global)),
  var_entre_municipios = r10(sum(por_mun$n * (por_mun$p - mean(v$punt_global))^2) / (nrow(v) - 1)),
  pct_var_entre = r10(100 * sum(por_mun$n * (por_mun$p - mean(v$punt_global))^2) /
                        ((nrow(v) - 1) * var(v$punt_global))))
message(sprintf("  varianza entre municipios: %.5f %% del total", D$m8$pct_var_entre))
for (c0 in curva)
  message(sprintf("    %4d zonas  r = %+.5f  (sd %.5f, %d rep.)", c0$zonas, c0$media, c0$sd, c0$n_rep))

# =====================================================================
# I. MÓDULO 9 — MAUP II, el efecto zonificación
#
# MISMA escala —33 zonas—, distinta partición. Dos distribuciones: una de
# particiones CONTIGUAS y otra de particiones ARBITRARIAS, porque la
# diferencia entre las dos es media lección: lo que sostiene la
# correlación agregada es la ESTRUCTURA ESPACIAL, no el hecho de agregar.
# =====================================================================
message("I. modulo 9 - MAUP, efecto zonificacion")

# Cada partición se mide DOS veces: con las medias de zona ponderadas por
# el número de estudiantes y sin ponderar. No es un adorno — es la que
# explica el resultado. Una zona arbitraria reúne municipios de todo el
# país, así que su media ponderada la fija el municipio grande que le
# tocó; una zona contigua reúne vecinos, que se parecen entre sí. Si el
# mecanismo es ese, al quitar el ponderador las dos distribuciones tienen
# que moverse en direcciones distintas. Publicar el resultado sin esta
# comprobación sería vender un artefacto como fenómeno, que es el error
# que T1.1 cometió tres veces.
message(sprintf("  %d particiones contiguas de %d zonas...", N_PARTICIONES, N_ZONAS))
set.seed(SEM_PART_CONT)
mc <- vapply(seq_len(N_PARTICIONES), function(i) {
  z <- particion_contigua(nb, N_ZONAS)[idx_ok]
  c(r_de_zona(z, TRUE), r_de_zona(z, FALSE))
}, numeric(2))
r_cont <- mc[1, ]; r_cont_sp <- mc[2, ]
n_no_asignados <- {
  set.seed(SEM_PART_CONT)
  z1 <- particion_contigua(nb, N_ZONAS)
  sum(is.na(z1))
}

message(sprintf("  %d particiones arbitrarias de %d zonas...", N_PARTICIONES, N_ZONAS))
set.seed(SEM_PART_ARB)
tam_real <- as.integer(table(z_real))
ma <- vapply(seq_len(N_PARTICIONES), function(i) {
  # Se conservan los TAMAÑOS de los departamentos reales, para que la
  # única diferencia con la partición real sea cuáles municipios van
  # juntos, no cuántos.
  z <- rep(seq_along(tam_real), tam_real)[sample(nrow(por_mun_ok))]
  c(r_de_zona(z, TRUE), r_de_zona(z, FALSE))
}, numeric(2))
r_arb <- ma[1, ]; r_arb_sp <- ma[2, ]

pctl <- function(x, v) 100 * mean(x <= v)
D$m9 <- list(
  n_particiones = N_PARTICIONES, n_zonas = N_ZONAS,
  # La referencia es la departamental CARTOGRÁFICA: es la única que cubre
  # la misma población que las 2 000 particiones aleatorias.
  r_real = r10(r_dep_mapa),
  r_real_todos = r10(r_dep),
  no_asignados_por_islas = n_no_asignados,
  contiguas = list(
    media = r10(mean(r_cont)), sd = r10(sd(r_cont)),
    min = r10(min(r_cont)), max = r10(max(r_cont)),
    q05 = r10(quantile(r_cont, 0.05)), q50 = r10(median(r_cont)),
    q95 = r10(quantile(r_cont, 0.95)),
    percentil_real = r10(pctl(r_cont, r_dep_mapa)),
    n_por_encima = sum(r_cont > r_dep_mapa)),
  arbitrarias = list(
    media = r10(mean(r_arb)), sd = r10(sd(r_arb)),
    min = r10(min(r_arb)), max = r10(max(r_arb)),
    q05 = r10(quantile(r_arb, 0.05)), q50 = r10(median(r_arb)),
    q95 = r10(quantile(r_arb, 0.95)),
    percentil_real = r10(pctl(r_arb, r_dep_mapa)),
    n_por_encima = sum(r_arb > r_dep_mapa)),
  # El histograma que dibuja el navegador, precalculado
  hist_contiguas = local({
    h <- hist(r_cont, breaks = 30, plot = FALSE)
    list(cortes = r10(h$breaks), conteo = as.integer(h$counts))
  }),
  hist_arbitrarias = local({
    h <- hist(r_arb, breaks = 30, plot = FALSE)
    list(cortes = r10(h$breaks), conteo = as.integer(h$counts))
  }),
  # El recorrido total: el mismo dato, la misma escala, y la correlación
  # va de aquí a aquí solo cambiando dónde se trazan las fronteras.
  recorrido_contiguas = r10(max(r_cont) - min(r_cont)),
  tam_zonas_reales = list(min = min(tam_real), max = max(tam_real),
                          mediana = r10(median(tam_real))),
  # El diagnóstico del mecanismo: las mismas particiones, sin ponderar.
  sin_ponderar = list(
    contiguas_media = r10(mean(r_cont_sp)), contiguas_sd = r10(sd(r_cont_sp)),
    arbitrarias_media = r10(mean(r_arb_sp)), arbitrarias_sd = r10(sd(r_arb_sp)),
    real = r10(r_de_zona(z_real, FALSE)),
    # La brecha entre contiguas y arbitrarias, con y sin ponderador
    brecha_ponderada = r10(mean(r_arb) - mean(r_cont)),
    brecha_sin_ponderar = r10(mean(r_arb_sp) - mean(r_cont_sp))))
message(sprintf("  contiguas : media %+.5f  sd %.5f  [%+.5f, %+.5f]  · la real esta en el percentil %.5f",
                mean(r_cont), sd(r_cont), min(r_cont), max(r_cont), D$m9$contiguas$percentil_real))
message(sprintf("  arbitrarias: media %+.5f  sd %.5f  [%+.5f, %+.5f]  · la real esta en el percentil %.5f",
                mean(r_arb), sd(r_arb), min(r_arb), max(r_arb), D$m9$arbitrarias$percentil_real))

# --- Gerrymandering: la rejilla sintética -----------------------------
# 5x5 electores, 60 % del partido A, en 5 distritos de 5 casillas. El
# clásico: la misma población da 5-0, 3-2 o 2-3 según cómo se corte.
# No lleva dato real a propósito: es una demostración de aritmética, y
# mezclarla con geografía colombiana la volvería una acusación.
LADO <- 5L; N_DIST <- 5L; POR_DIST <- 5L
rej <- matrix(c(
  1,1,0,0,0,
  1,1,0,0,0,
  1,1,1,0,0,
  1,1,1,1,0,
  1,1,1,1,1), nrow = LADO, byrow = TRUE)
voto <- as.integer(t(rej))                 # orden por filas, 1-basado
pct_A <- mean(voto)

# Vecindad de torre sobre la rejilla
vec_rej <- lapply(seq_len(LADO * LADO), function(i) {
  f <- (i - 1) %/% LADO + 1; c0 <- (i - 1) %% LADO + 1
  v <- c(if (f > 1) i - LADO, if (f < LADO) i + LADO,
         if (c0 > 1) i - 1, if (c0 < LADO) i + 1)
  as.integer(v)
})

# Una partición contigua en distritos de EXACTAMENTE 5 casillas. Se
# construye creciendo un distrito cada vez y se rechaza si se atasca.
# No se dibuja a mano: la primera versión de este bloque llevaba tres
# particiones escritas a ojo y una tenía distritos de 6, 5, 4, 5 y 5
# casillas. La guarda de tamaño la cazó, pero la lección es que un
# ejemplo dibujado a mano no es una medida.
particion_rejilla <- function() {
  z <- rep(NA_integer_, LADO * LADO)
  for (d in seq_len(N_DIST)) {
    libres <- which(is.na(z))
    if (!length(libres)) return(NULL)
    sem <- libres[sample.int(length(libres), 1)]
    z[sem] <- d
    for (paso in seq_len(POR_DIST - 1L)) {
      cand <- unique(unlist(vec_rej[which(z == d)]))
      cand <- cand[is.na(z[cand])]
      if (!length(cand)) return(NULL)         # atascado: se descarta
      z[cand[sample.int(length(cand), 1)]] <- d
    }
  }
  if (any(is.na(z))) return(NULL)
  z
}

set.seed(SEM_PART_ARB)
escanos <- integer(0); ejemplos <- list()
INTENTOS <- 200000L
for (i in seq_len(INTENTOS)) {
  z <- particion_rejilla()
  if (is.null(z)) next
  tam <- as.integer(table(z))
  if (length(tam) != N_DIST || !all(tam == POR_DIST))
    stop("particion de gerrymandering con distritos de tamano desigual: ",
         paste(tam, collapse = "/"))
  e <- sum(vapply(seq_len(N_DIST), function(d) mean(voto[z == d]) > 0.5, logical(1)))
  escanos <- c(escanos, e)
  k <- as.character(e)
  if (is.null(ejemplos[[k]])) ejemplos[[k]] <- as.integer(z)
}
if (!length(escanos)) stop("la busqueda de particiones de la rejilla no encontro ninguna valida")

tabla_e <- table(factor(escanos, levels = 0:N_DIST))
D$m9$gerrymandering <- list(
  lado = LADO, n_distritos = N_DIST, casillas_por_distrito = POR_DIST,
  pct_A = r10(100 * pct_A), n_A = sum(voto), n_B = sum(voto == 0),
  rejilla = voto,
  n_particiones_probadas = INTENTOS,
  n_particiones_validas = length(escanos),
  escanos_min = min(escanos), escanos_max = max(escanos),
  escanos_proporcionales = r10(N_DIST * pct_A),
  distribucion = lapply(0:N_DIST, function(e)
    list(escanos = e, n = as.integer(tabla_e[as.character(e)]),
         pct = r10(100 * as.integer(tabla_e[as.character(e)]) / length(escanos)))),
  # Un trazado real por cada resultado alcanzable, para que el simulador
  # pueda pintarlos. Salen de la búsqueda, no de mi mano.
  ejemplos = lapply(sort(as.integer(names(ejemplos))), function(e)
    list(escanos_A = e, escanos_B = N_DIST - e, particion = ejemplos[[as.character(e)]])))
message(sprintf("  gerrymandering: A tiene el %.5f %% de los votos; de %d particiones contiguas validas",
                100 * pct_A, length(escanos)))
message(sprintf("    saca entre %d y %d escanos de %d (proporcional serian %.5f)",
                min(escanos), max(escanos), N_DIST, N_DIST * pct_A))

# =====================================================================
# J. MÓDULO 10 — La falacia ecológica
#
# Robinson (1950). Aquí se mide sobre el propio dato: el barrido de
# umbral que T0.4 dejó, más la nube individual contra la agregada.
#
# LO QUE NO SE HACE: publicar las cifras del artículo de Robinson de
# memoria. El capítulo cita el trabajo como origen del concepto —eso es
# una referencia— y todas las MAGNITUDES que publica salen de aquí.
# =====================================================================
message("J. modulo 10 - la falacia ecologica")

UMBRALES <- c(0L, 10L, 30L, 100L, 300L, 1000L)
barrido <- lapply(UMBRALES, function(u) {
  s <- por_mun[n >= u]
  list(umbral = u, n_municipios = nrow(s), r = r10(cor(s$x, s$p)))
})
r_pond <- stats::cov.wt(cbind(por_mun$x, por_mun$p), wt = por_mun$n, cor = TRUE)$cor[1, 2]

# La nube individual es demasiado grande para el navegador: se resume en
# la media del puntaje por cada nivel de educación de la madre, con su
# n y su desviación. Es el dato individual, no una muestra de él.
nube_ind <- v[, .(n = .N, media = r10(mean(punt_global)), sd = r10(sd(punt_global))),
              by = edu_madre][order(edu_madre)]

D$m10 <- list(
  r_individuo = r10(r_ind),
  r_municipio = r10(r_mun),
  r_municipio_ponderado = r10(r_pond),
  r_departamento = r10(r_dep),
  barrido = barrido,
  nube_individual = lapply(seq_len(nrow(nube_ind)), function(i)
    list(nivel = nube_ind$edu_madre[i], n = nube_ind$n[i],
         media = nube_ind$media[i], sd = nube_ind$sd[i])),
  niveles_edu = names(EDU_MADRE),
  # Lo que la agregación destruye, en una cifra
  pct_var_dentro = r10(100 - D$m8$pct_var_entre))
message(sprintf("  barrido: %s", paste(vapply(barrido, function(b)
  sprintf("n>=%d:%+.4f", b$umbral, b$r), character(1)), collapse = "  ")))

# =====================================================================
# K. MÓDULO 11 — Cartografía y ética
#
# La regla del §6 del plan: análisis, no editorial. Aquí eso significa
# que la lección técnica —el sesgo entra por la unidad geográfica— va
# MEDIDA y por delante, y los dos casos históricos que no se pueden
# medir desde aquí entran declarados como cita.
# =====================================================================
message("K. modulo 11 - cartografia y etica")

# --- El caso de aviso: el estrato -----------------------------------
# T0.4 lo congeló como caso de aviso porque su correlación municipal
# cambia de SIGNO según el umbral. Es el mismo mapa, la misma variable,
# y una decisión de filtrado que nadie declara.
ve <- s11[!is.na(estrato) & !is.na(punt_global) & !is.na(divipola),
          .(divipola, estrato, punt_global)]
est_mun <- ve[, .(n = .N, x = mean(estrato), p = mean(punt_global)), by = divipola]
barrido_est <- lapply(UMBRALES, function(u) {
  s <- est_mun[n >= u]
  list(umbral = u, n_municipios = nrow(s), r = r10(cor(s$x, s$p)))
})
r_est_sin <- cor(est_mun$x, est_mun$p)
r_est_1000 <- cor(est_mun[n >= 1000]$x, est_mun[n >= 1000]$p)
if (sign(r_est_sin) == sign(r_est_1000))
  stop("el caso de aviso del estrato ya no invierte el signo: revisar antes de publicarlo")

# --- Quien no tiene polígono no sale en el mapa ----------------------
casos <- jsonlite::fromJSON(file.path(PROC, "casos_territoriales.json"),
                            simplifyVector = FALSE)
# Estudiantes cuyo código de municipio no empareja con ningún polígono
cod_mapa <- mun$divipola
huerfanos <- s11[!is.na(divipola) & !divipola %chin% cod_mapa,
                 .(n = .N), by = divipola][order(-n)]
n_huerfanos <- sum(huerfanos$n)

# --- El tipo de entidad territorial ---------------------------------
# La brecha que T0.4 midió: municipio contra área no municipalizada.
tipo_dt <- data.table(divipola = mun$divipola, tipo = mun$tipo)
por_tipo <- merge(v[, .(divipola, punt_global)], tipo_dt, by = "divipola")[
  , .(n = .N, media = r10(mean(punt_global)), sd = r10(sd(punt_global))), by = tipo]
sin_estudiantes <- tipo_dt[!divipola %chin% unique(v$divipola), .N, by = tipo]

D$m11 <- list(
  estrato = list(
    n_estudiantes = nrow(ve), n_municipios = nrow(est_mun),
    barrido = barrido_est,
    r_sin_umbral = r10(r_est_sin), r_umbral_1000 = r10(r_est_1000),
    invierte_signo = TRUE,
    n_municipios_umbral_1000 = nrow(est_mun[n >= 1000])),
  sin_poligono = list(
    n_estudiantes = n_huerfanos,
    # Lo que cuesta no estar en el mapa, medido sobre el resultado y no
    # sobre el censo: la correlación departamental se mueve esto al pasar
    # de "todos los estudiantes" a "los que caen en algún polígono".
    r_departamental_todos = r10(r_dep),
    r_departamental_mapa = r10(r_dep_mapa),
    desvio_departamental = r10(r_dep - r_dep_mapa),
    n_estudiantes_perdidos_escalera = n_fuera,
    pct_cohorte = r10(100 * n_huerfanos / nrow(s11)),
    n_codigos = nrow(huerfanos),
    codigos = lapply(seq_len(min(5, nrow(huerfanos))), function(i)
      list(divipola = huerfanos$divipola[i], n = huerfanos$n[i])),
    casos_documentados = casos),
  por_tipo = lapply(seq_len(nrow(por_tipo)), function(i)
    list(tipo = por_tipo$tipo[i], n = por_tipo$n[i],
         media = por_tipo$media[i], sd = por_tipo$sd[i])),
  sin_estudiantes = lapply(seq_len(nrow(sin_estudiantes)), function(i)
    list(tipo = sin_estudiantes$tipo[i], n = sin_estudiantes$N[i])),
  # Los dos casos históricos: CITA, no medida. El capítulo los presenta
  # como tales y el auditor comprueba que llevan fuente.
  casos_citados = list(
    list(id = "redlining",
         titulo = "Los mapas del HOLC y el redlining",
         anos = "1935-1940",
         fuente = "Home Owners' Loan Corporation; mapas digitalizados en Mapping Inequality, Digital Scholarship Lab, University of Richmond",
         url = "https://dsl.richmond.edu/panorama/redlining/",
         leccion = "una clasificacion por zonas convertida en criterio de credito"),
    list(id = "predictiva",
         titulo = "Vigilancia predictiva por zonas",
         anos = "2011-2020",
         fuente = "Lum & Isaac (2016), 'To predict and serve?', Significance 13(5)",
         url = "https://doi.org/10.1111/j.1740-9713.2016.00960.x",
         leccion = "el modelo aprende donde se ha patrullado, no donde hay delito")))
message(sprintf("  estrato: r sin umbral %+.5f, con n>=1000 %+.5f (INVIERTE el signo)",
                r_est_sin, r_est_1000))
message(sprintf("  sin poligono: %s estudiantes (%.5f %% de la cohorte) en %d codigos",
                format(n_huerfanos, big.mark = " "), D$m11$sin_poligono$pct_cohorte, nrow(huerfanos)))
for (i in seq_len(nrow(por_tipo)))
  message(sprintf("    %-28s n = %7d  media %.5f", por_tipo$tipo[i], por_tipo$n[i], por_tipo$media[i]))

# =====================================================================
# L. LOS MAPAS
# =====================================================================
message("L. mapas")

# --- nc con los cinco esquemas (modulo 3) ---------------------------
nc_p <- st_transform(nc, 32119)   # NC State Plane, metros
MAPAS$nc_esquemas <- geo_poligonos(
  nc_p, valor = sid, n_clases = 5, estilo = "quantile",
  etiquetas = nc$NAME, titulo = "Carolina del Norte · SID74",
  leyenda = "muertes subitas de lactantes, 1974-78", presupuesto = 1500L, delta = TRUE,
  # SIN nombres: `setNames` haría que jsonlite escribiera un OBJETO donde
  # las capas del mapa municipal escriben un ARRAY, y el navegador
  # tendría que distinguir los dos casos para recorrer lo mismo. Una sola
  # forma para una sola cosa.
  vistas = lapply(ESQUEMAS, function(e)
    list(estilo = e, n = 5, etiqueta = unname(ESQ_ES[e]))))

# --- LOS 1 122 MUNICIPIOS, UNA SOLA VEZ ------------------------------
#
# El capítulo pinta el mapa municipal cuatro veces: deserción con sus
# cinco esquemas (módulos 1 y 4), conteo de estudiantes y puntaje medio
# (módulo 2) y presencia en la cohorte (módulo 11). Cada copia de esa
# geometría cuesta 150 KB, y el presupuesto del capítulo entero es 120.
#
# Así que la geometría se paga UNA vez y las cuatro variables entran como
# CAPAS. Los valores van alineados a los 1 122 rasgos, con NA donde no
# hay dato: eso permite que capas con distinta cobertura —la deserción
# cubre 1 121 municipios y Saber 11 cubre 1 113— compartan la misma
# geometría sin recortarla, y de paso el mapa ENSEÑA dónde falta el dato
# en vez de esconderlo borrando el polígono.
#
# Y va a q = 1024 en vez de 4096. Sobre un lienzo de 900 px el error de
# cuantización pasa de 0,22 a 0,88 px —menos de un píxel— y cada
# coordenada pierde un carácter. En un mapa de pocos rasgos grandes no se
# haría; en uno de 1 122 municipios diminutos es invisible y son 40 KB.
# La simplificación de 1 122 polígonos es lo más caro del guion: la
# bisección de `geo_simplifica` gasta catorce llamadas a ms_simplify para
# terminar en el suelo estructural (cada polígono conserva su anillo
# mínimo, así que 1 122 rasgos no bajan de ~12 500 vértices por mucho que
# se insista). Es determinista, así que se cachea y el mapa se construye
# ya simplificado.
f_simp <- file.path(CACHE, sprintf("mun_simplificado_%d.rds", nrow(mun)))
if (file.exists(f_simp)) {
  mun_s <- readRDS(f_simp)
  message("  municipios simplificados: de la cache")
} else {
  message("  simplificando 1 122 municipios (lento, se cachea)...")
  mun_s <- geo_simplifica(mun, 3200L, verbose = TRUE)
  saveRDS(mun_s, f_simp)
}
if (nrow(mun_s) != nrow(mun)) stop("la simplificacion perdio municipios")
N_VERT_MUN <- geo_n_vertices(mun_s)

val_por_divipola <- function(dt, col) {
  i <- match(mun$divipola, dt$divipola)
  ifelse(is.na(i), NA_real_, as.numeric(dt[[col]][i]))
}
presencia <- as.numeric(mun$divipola %chin% unique(v$divipola))
MAPAS$municipios <- geo_poligonos(
  mun_s, titulo = "Colombia · 1 122 municipios",
  leyenda = "", etiquetas = mun$municipio, presupuesto = N_VERT_MUN,
  verbose = FALSE, q = 1024L, delta = TRUE,
  capas = list(
    list(id = "desercion", etiqueta = "Deserción escolar (%)",
         leyenda = "% de deserción", valor = mun$desercion, n_clases = 5,
         estilo = "quantile",
         vistas = lapply(ESQUEMAS, function(e)
           list(estilo = e, n = 5, etiqueta = unname(ESQ_ES[e])))),
    list(id = "conteo", etiqueta = "Estudiantes de Saber 11 (conteo)",
         leyenda = "estudiantes", valor = val_por_divipola(mm, "n"),
         n_clases = 5, estilo = "quantile"),
    list(id = "tasa", etiqueta = "Puntaje global medio (tasa)",
         leyenda = "puntaje medio", valor = val_por_divipola(mm, "punt"),
         n_clases = 5, estilo = "quantile"),
    list(id = "presencia", etiqueta = "Presencia en la cohorte 20224",
         leyenda = "1 = con estudiantes, 0 = ninguno", valor = presencia,
         n_clases = 2, estilo = "equal")))

# --- Los cuatro mapas del modulo 7 ----------------------------------
# LA CAJA ES COMPARTIDA, y no es un detalle: sin ella el navegador
# reescala cada mapa para llenar su lienzo y desaparece justo lo que el
# cartograma enseña, que es que unas areas crecen y otras encogen.
# La caja tiene que cubrir TODO lo que se va a cuantizar contra ella,
# hexbin incluido. La primera versión la calculó solo sobre los cuatro
# mapas departamentales y la rejilla de hexágonos —que por construcción
# desborda el país— se salía del rango: vértices en -144 y en 4262 con
# q = 4096. Lo cazó la comprobación nueva de `audita_base`, que decodifica
# las diferencias y mira dónde caen de verdad los vértices.
caja7 <- as.numeric(st_bbox(Reduce(st_union, list(
  st_as_sfc(st_bbox(dep)), st_as_sfc(st_bbox(carto_n)),
  st_as_sfc(st_bbox(carto_d)), st_as_sfc(st_bbox(carto_c)),
  st_as_sfc(st_bbox(hexes))))))

# El coropleto departamental, los símbolos proporcionales y el dot
# density comparten EXACTAMENTE la misma geometría: van en un solo
# objeto con dos capas superpuestas, no en tres mapas. Tres copias de la
# geometría departamental son 70 KB por nada.
ctr_dep0 <- st_coordinates(st_centroid(st_geometry(dep), of_largest_polygon = TRUE))[, 1:2]
MAPAS$dep_coropleto <- geo_poligonos(
  dep, valor = dep$n_est, n_clases = 5, estilo = "quantile", caja = caja7,
  etiquetas = dep$nombre, titulo = "Coropleto", leyenda = "estudiantes",
  presupuesto = 1400L, delta = TRUE,
  superpuestos = list(
    list(id = "simbolos", modo = "simbolo", xy = ctr_dep0, valor = dep$n_est,
         etiqueta = "Símbolos proporcionales"),
    list(id = "densidad", modo = "densidad", xy = dd1,
         etiqueta = sprintf("Dot density · 1 punto = %d estudiantes", POR_PUNTO))))
MAPAS$dep_ncont <- geo_poligonos(
  carto_n, valor = dep$n_est, n_clases = 5, estilo = "quantile", caja = caja7,
  etiquetas = dep$nombre, titulo = "Cartograma no contiguo (Olson)",
  leyenda = "estudiantes", presupuesto = 1400L, delta = TRUE)
MAPAS$dep_dorling <- geo_poligonos(
  carto_d, valor = dep$n_est, n_clases = 5, estilo = "quantile", caja = caja7,
  etiquetas = dep$nombre, titulo = "Cartograma de Dorling",
  leyenda = "estudiantes", presupuesto = 1400L, delta = TRUE)
MAPAS$dep_cont <- geo_poligonos(
  carto_c, valor = dep$n_est, n_clases = 5, estilo = "quantile", caja = caja7,
  etiquetas = dep$nombre, titulo = "Cartograma contiguo (Dougenik)",
  leyenda = "estudiantes", presupuesto = 1400L, delta = TRUE)

MAPAS$dep_hexbin <- geo_poligonos(
  hexes, valor = hexes$v, n_clases = 5, estilo = "quantile", caja = caja7,
  titulo = "Hexbin", leyenda = "estudiantes (reparto por area)", presupuesto = 1600L, delta = TRUE)

# El mapa de la ética —quién no tiene polígono— es la capa `presencia`
# del objeto `municipios`: no necesita su propia geometría.

# =====================================================================
# M. SALIDA
# =====================================================================
message("M. escribiendo")

D$meta <- list(
  capitulo = 3,
  titulo = "Cartografia estadistica y el MAUP",
  semana = 4,
  generado = format(Sys.time(), "%Y-%m-%dT%H:%M:%S"),
  semillas = list(base = SEMILLA, particiones_contiguas = SEM_PART_CONT,
                  particiones_arbitrarias = SEM_PART_ARB, puntos = SEM_PUNTOS,
                  escala = SEM_ESCALA),
  n_anclas = N_ANCLAS,
  # El coste de la geometría municipal, que es lo que decide el peso del
  # capítulo y por qué se comparte entre las cuatro capas.
  geometria = list(n_municipios = nrow(mun_s), n_vertices = N_VERT_MUN,
                   q_municipal = 1024L, q_resto = QMAX),
  r_version = paste(R.version$major, R.version$minor, sep = "."),
  paquetes = list(
    sf = as.character(packageVersion("sf")),
    classInt = as.character(packageVersion("classInt")),
    cartogram = as.character(packageVersion("cartogram")),
    colorspace = as.character(packageVersion("colorspace")),
    spdep = as.character(packageVersion("spdep")),
    tmap = v_tmap))

MAPAS$meta <- list(capitulo = 3, generado = D$meta$generado)

# `na = "null"`: ver la nota de geo_escribe(). Misma guarda aquí.
txt_datos <- jsonlite::toJSON(D, auto_unbox = TRUE, digits = 10,
                              null = "null", na = "null")
if (grepl('"NA"', txt_datos, fixed = TRUE))
  stop("cap3_datos.json: hay NA escritos como la cadena \"NA\"")
writeLines(txt_datos, file.path(SALIDAS, "cap3_datos.json"), useBytes = TRUE)
message(sprintf("  cap3_datos.json: %.1f KB",
                file.size(file.path(SALIDAS, "cap3_datos.json")) / 1024))
# EL PRESUPUESTO DE ESTE CAPÍTULO ES 200 KB, NO 120, Y ESO ES UNA
# DESVIACIÓN DECLARADA (ver A.14 del plan). El §4 fija ~120 KB y afirma
# que los 1 122 municipios «simplificados a tolerancia visual» caben.
# No caben: el suelo de ms_simplify con keep_shapes = TRUE es
# ESTRUCTURAL —cada polígono conserva su anillo mínimo— y 1 122 rasgos
# no bajan de 12 547 vértices con ninguna tolerancia. Los capítulos 1 y
# 2 nunca lo tocaron porque usan la capa DEPARTAMENTAL (33 rasgos).
# Lo que sí se ha hecho es bajarlo de 653 KB a esto, por tres vías
# medidas: geometría compartida entre las cuatro capas municipales
# (-367 KB), cuantización a 1024 en el mapa municipal, y codificación
# por diferencias en todos los mapas del capítulo (-33 %).
geo_escribe(MAPAS, file.path(SALIDAS, "cap3_mapas.json"), presupuesto_kb = 200)

# Los CSV que las pestañas de Python del capítulo leen
data.table::fwrite(data.table(
  divipola = mun_ok$divipola, municipio = mun_ok$municipio,
  departamento = mun_ok$departamento, tipo = mun_ok$tipo,
  desercion = des[ok_des],
  clase_equal = clases5[, "equal"], clase_quantile = clases5[, "quantile"],
  clase_fisher = clases5[, "fisher"], clase_sd = clases5[, "sd"],
  clase_headtails = clases5[, "headtails"]),
  file.path(SALIDAS, "cap3_desercion.csv"))
data.table::fwrite(data.table(
  fips = nc$FIPS, condado = nc$NAME, sid74 = sid, bir74 = nc$BIR74),
  file.path(SALIDAS, "cap3_nc.csv"))
# DOS AGREGADOS MUNICIPALES, Y LOS NOMBRES DICEN CUÁL ES CUÁL.
# `por_mun` cubre a los estudiantes con educación de la madre Y puntaje
# —es la población de los módulos 8, 9 y 10— y `mm` cubre a todos los
# que tienen puntaje, que es la del módulo 2. Sobre la misma pareja de
# columnas dan cifras parecidas y DISTINTAS (r = 0,103 contra 0,100), y
# un ejercicio que leyera el archivo equivocado publicaría un número que
# no cuadra con el módulo que dice estar practicando. Se escriben los
# dos, con el sufijo que declara su cobertura.
data.table::fwrite(por_mun, file.path(SALIDAS, "cap3_municipios_edu_madre.csv"))
data.table::fwrite(mm[, .(divipola, municipio, departamento = depto, n, punt)],
                   file.path(SALIDAS, "cap3_municipios_conteo_tasa.csv"))
data.table::fwrite(data.table(
  departamento = dep$nombre, cod_dep = dep$cod_dep, n_est = dep$n_est,
  punt = dep$punt, area_km2 = area_dep / 1e6),
  file.path(SALIDAS, "cap3_departamentos.csv"))

message(sprintf("\nLISTO. %d anclas comprobadas, ninguna rota.", N_ANCLAS))
