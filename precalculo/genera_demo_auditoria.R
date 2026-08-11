# =====================================================================
# genera_demo_auditoria.R — las cifras del capítulo-banco de pruebas (T0.5)
#
# Material de Estadística Espacial 2026-II (20929).
#
# POR QUÉ EXISTE ESTE ARCHIVO.
#
# T0.5 pide cuatro auditores y exige que el arnés de inyección cace el
# 100 % de las cifras falsas. Pero la plantilla del curso tiene CINCO
# bloques de código y CERO líneas `#>`: `verifica_bloques.py` sobre ella
# informaría «0 de 0 cifras» en verde sin haber comprobado nada. Y sin
# prosa con cifras respaldadas por un precálculo, el auditor de texto no
# tiene dónde morder y el arnés de inyección no prueba nada.
#
# Un auditor que sale limpio sobre un documento vacío es exactamente la
# falsa calma que T0.5 existe para impedir. Así que antes que los
# auditores hay que fabricarles un sujeto: un capítulo de mentira con
# cifras de verdad.
#
# «De verdad» quiere decir que salen de aquí, calculadas sobre los datos
# de T0.4 y sobre los canónicos de la literatura. Ninguna está escrita a
# mano (D10). Si una cambia, cambia en el JSON y el capítulo se vuelve a
# ensamblar; el auditor compara contra el JSON, no contra la memoria.
#
# El fixture se queda como prueba de regresión permanente: cuando el
# núcleo `audita_texto_base.py` cambie por el capítulo 7, esto dice si el
# cambio rompió algo.
#
# Ejecutar SIEMPRE con el R 4.4-arm64, no con el del PATH:
#   /Library/Frameworks/R.framework/Versions/4.4-arm64/Resources/bin/Rscript \
#     precalculo/genera_demo_auditoria.R
# desde la carpeta `Estadistica espacial/`.
# =====================================================================

suppressMessages({
  library(sf)
  library(sp)
  library(spdep)
  library(spData)
  library(jsonlite)
  library(classInt)
})

set.seed(2026)
options(stringsAsFactors = FALSE)

AQUI <- "precalculo"
# PRIMERO la guarda de codificación: sin ella `jsonlite` escribe las
# tildes como `<c3><b3>` y no falla. Ver la cabecera de utf8.R.
source(file.path(AQUI, "utf8.R"))
source(file.path(AQUI, "fuentes.R"))
source(file.path(AQUI, "geo.R"))

SALIDAS <- file.path(AQUI, "salidas")
dir.create(SALIDAS, showWarnings = FALSE, recursive = TRUE)

# `round` a 10 decimales en todo lo que se publica. El redondeo existe para
# que dos ejecuciones del mismo script den JSON idénticos byte a byte —lo
# que la verificación de T1.1 comprueba— y diez decimales bastan de sobra:
# por debajo de eso solo hay ruido de coma flotante.
#
# POR QUÉ 10 Y NO 6, que es lo que decía la primera versión. La regla de
# publicación de T0.5 es de **5 decimales**, y con el JSON redondeado a 6
# el capítulo hacía un **doble redondeo**: R guardaba 3.954465 y el
# ensamblador lo formateaba a 3.95446, mientras el bloque de código del
# propio capítulo —que calcula `round(x, 5)` sobre el valor sin redondear—
# imprimía 3.95447. Una diezmilésima de diferencia entre la prosa y su
# propio código, que `verifica_bloques.py` cazó al primer intento.
#
# Con la regla en 4 decimales no se notaba porque sobraban dos de margen.
# La regla exige que el JSON conserve holgura por debajo de lo que se
# publica: si se publican 5, no se guardan 6.
r6 <- function(x) round(as.numeric(x), 10)

D <- list()

# ---------------------------------------------------------------------
message("1/6 · Columbus — la contigüidad canónica de Anselin")
# ---------------------------------------------------------------------
# Instantáneo y contrastable contra el libro: es el dato con el que el
# capítulo 6 va a enseñar la matriz W.
data(oldcol, package = "spdep")   # COL.nb: la lista GAL que publicó Anselin
col_sf <- st_read(system.file("shapes/columbus.gpkg", package = "spData"),
                  quiet = TRUE)
nb_reina <- poly2nb(col_sf, queen = TRUE)
nb_torre <- poly2nb(col_sf, queen = FALSE)

D$columbus <- list(
  n            = length(nb_reina),
  aristas_reina = sum(card(nb_reina)) / 2,
  grado_reina   = r6(mean(card(nb_reina))),
  aristas_torre = sum(card(nb_torre)) / 2,
  grado_torre   = r6(mean(card(nb_torre))),
  # Cuánto se pierde al pasar de reina a torre. El capítulo argumenta con
  # esta cifra, así que se publica: si el texto la cita, el auditor la
  # tiene que poder encontrar.
  perdida_pct   = r6(100 * (1 - mean(card(nb_torre)) / mean(card(nb_reina)))),
  # Y la discrepancia que el fixture declara: la lista GAL que Anselin
  # distribuye con `oldcol` NO es la contigüidad reina recalculada sobre
  # el polígono. Difiere, y el material tiene que decirlo en vez de
  # presentar una de las dos como «la» vecindad de Columbus.
  aristas_gal   = sum(card(COL.nb)) / 2,
  grado_gal     = r6(mean(card(COL.nb)))
)

# ---------------------------------------------------------------------
message("2/6 · nc (SIDS) — la clasificación que no coincide entre R y Python")
# ---------------------------------------------------------------------
nc <- st_read(system.file("shape/nc.shp", package = "sf"), quiet = TRUE)
ci_q <- classIntervals(nc$SID74, n = 5, style = "quantile")
ci_f <- classIntervals(nc$SID74, n = 5, style = "fisher")

# OJO, y es la trampa A.2 vista desde dentro: `findCols()` da la partición
# que `classInt` usa de verdad, con intervalos **[a, b)**. Escribir
# `cut(v, brks)` parece equivalente y NO lo es — `cut` cierra por la
# derecha, **(a, b]**, que es el convenio de `mapclassify`. Con `SID74`,
# que tiene 39 empates justo en los cortes, las dos particiones difieren
# en 11 condados solo en la primera clase. Un `cut` ingenuo dentro de un
# script de R devuelve la respuesta de PYTHON sin avisar de nada.
tam_q <- as.integer(table(findCols(ci_q)))
tam_f <- as.integer(table(findCols(ci_f)))
# Y la otra partición, la de (a, b], que es lo que el material contrasta.
tam_q_py <- as.integer(table(cut(nc$SID74, ci_q$brks,
                                 include.lowest = TRUE, right = TRUE)))

# Los empates justo en los cortes son la CAUSA de la discrepancia A.2, y
# el capítulo lo afirma. Se cuenta, no se recuerda.
empates <- sum(nc$SID74 %in% ci_q$brks[-c(1, length(ci_q$brks))])

D$nc <- list(
  n_condados     = nrow(nc),
  cortes_quantile = r6(as.numeric(ci_q$brks)),
  tam_quantile    = tam_q,        # [a, b) — classInt
  tam_quantile_py = tam_q_py,     # (a, b] — mapclassify
  movidos         = sum(abs(tam_q - tam_q_py)) / 2,
  cortes_fisher   = r6(as.numeric(ci_f$brks)),
  tam_fisher      = tam_f,
  empates_en_cortes = empates,
  sid74_total     = sum(nc$SID74),
  sid74_media     = r6(mean(nc$SID74))
)

# ---------------------------------------------------------------------
message("3/6 · IDEAM — el gradiente térmico, que es la prueba de salud del dato")
# ---------------------------------------------------------------------
est <- st_read("datos/procesado/colombia_estaciones_clima.gpkg", quiet = TRUE)
aj <- lm(t_media_anual ~ altitud_m, data = est)

D$clima <- list(
  n_estaciones = nrow(est),
  corr         = r6(cor(est$altitud_m, est$t_media_anual)),
  r2           = r6(summary(aj)$r.squared),
  # °C por cada 1 000 m. El signo importa y el rango físico (−5 a −7)
  # es lo que convierte esto en evidencia y no en adorno.
  gradiente    = r6(coef(aj)[["altitud_m"]] * 1000),
  intercepto   = r6(coef(aj)[["(Intercept)"]]),
  temp_media   = r6(mean(est$t_media_anual)),
  alt_media    = r6(mean(est$altitud_m)),
  alt_max      = r6(max(est$altitud_m))
)

# ---------------------------------------------------------------------
message("4/6 · Bogotá — la ventana de observación cambia lambda")
# ---------------------------------------------------------------------
colegios <- st_read("datos/procesado/bogota_colegios.gpkg", quiet = TRUE)
v_urb <- st_read("datos/procesado/bogota_ventana_urbana.gpkg", quiet = TRUE)
v_dc  <- st_read("datos/procesado/bogota_ventana_dc.gpkg", quiet = TRUE)

area_km2 <- function(x) as.numeric(sum(st_area(x))) / 1e6
dentro <- function(pts, win) sum(lengths(st_intersects(pts, win)) > 0)

a_urb <- area_km2(v_urb); a_dc <- area_km2(v_dc)
n_urb <- dentro(colegios, v_urb); n_dc <- dentro(colegios, v_dc)

# La capa ya trae congeladas las dos pertenencias de T0.4. Recontarlas por
# intersección es un camino independiente, y que los dos caminos coincidan
# es lo que dice que el recuento no se ha torcido. Si discrepan, se para:
# publicar la cifra de uno de los dos sin mirar el otro sería justo el
# modo de fallo dominante de este proyecto — un valor plausible en vez de
# un error ruidoso.
stopifnot(n_urb == sum(colegios$en_urbana), n_dc == sum(colegios$en_ventana_dc))

D$ventanas <- list(
  n_sedes    = nrow(colegios),
  area_urbana = r6(a_urb), n_urbana = n_urb, lambda_urbana = r6(n_urb / a_urb),
  area_dc     = r6(a_dc),  n_dc = n_dc,      lambda_dc     = r6(n_dc / a_dc),
  # El factor es EL argumento del módulo: la ventana no es un detalle de
  # presentación, es parte del estimador.
  factor_lambda = r6((n_urb / a_urb) / (n_dc / a_dc)),
  razon_area    = r6(a_dc / a_urb),
  # Derivadas de las que el texto ARGUMENTA. Se publican en vez de
  # dejarlas al cálculo del auditor: el índice de comparaciones ya es
  # bastante ancho, y ensancharlo para que absorba cualquier derivación
  # de segundo orden es precisamente lo que le quita filo. Si el texto
  # razona con una cifra, la cifra se calcula aquí.
  razon_sedes   = r6(n_dc / n_urb),
  area_extra    = r6(a_dc - a_urb),
  sedes_extra   = n_dc - n_urb,
  lambda_extra  = r6((n_dc - n_urb) / (a_dc - a_urb))
)

# ---------------------------------------------------------------------
message("5/6 · Deserción por departamento — Moran, y el mapa del fixture")
# ---------------------------------------------------------------------
# A escala departamental, no municipal: 33 polígonos dan un mapa que cabe
# de sobra en el presupuesto de 120 KB y el argumento se ve igual. Los
# 1 122 municipios son del capítulo 3 en adelante.
muni <- carga_municipios(saber11 = FALSE)
dep  <- st_read("datos/procesado/colombia_adm1.gpkg", quiet = TRUE)

muni$dpto <- substr(muni$divipola, 1, 2)
# Media ponderada NO: la deserción del MEN ya es una tasa por municipio y
# el fixture necesita una cifra simple y reproducible. Se declara que es
# la media sin ponderar, que es lo que el texto va a decir.
agr <- aggregate(muni$desercion, by = list(dpto = muni$dpto),
                 FUN = function(v) mean(v, na.rm = TRUE))
names(agr)[2] <- "desercion"

# La unión va por geometría, no por nombre: el departamento de cada
# polígono se obtiene por el prefijo DIVIPOLA de sus municipios, que es
# una llave y no una cadena parecida.
centro <- suppressWarnings(st_point_on_surface(st_geometry(muni)))
i_dep <- st_intersects(centro, dep)
muni$dep_idx <- vapply(i_dep, function(z) if (length(z)) z[1] else NA_integer_, 1L)
tab <- table(muni$dep_idx, muni$dpto)
dep$dpto <- ifelse(rowSums(tab) > 0,
                   colnames(tab)[max.col(tab, ties.method = "first")], NA)
dep$desercion <- agr$desercion[match(dep$dpto, agr$dpto)]

ok <- !is.na(dep$desercion)
dep_ok <- dep[ok, ]
nb_dep <- suppressWarnings(poly2nb(dep_ok, queen = TRUE))
lw_dep <- nb2listw(nb_dep, style = "W", zero.policy = TRUE)
mi <- moran.test(dep_ok$desercion, lw_dep, zero.policy = TRUE)

D$desercion <- list(
  n_departamentos = nrow(dep_ok),
  n_municipios    = sum(!is.na(muni$desercion)),
  media           = r6(mean(dep_ok$desercion)),
  sd              = r6(sd(dep_ok$desercion)),
  minimo          = r6(min(dep_ok$desercion)),
  maximo          = r6(max(dep_ok$desercion)),
  recorrido       = r6(diff(range(dep_ok$desercion))),
  recorrido_en_sd = r6(diff(range(dep_ok$desercion)) / sd(dep_ok$desercion)),
  moran_I         = r6(mi$estimate[["Moran I statistic"]]),
  moran_esperado  = r6(mi$estimate[["Expectation"]]),
  moran_z         = r6(unname(mi$statistic)),
  moran_p         = r6(mi$p.value),
  # Las islas y los subgrafos NO son un estorbo del dato: son el caso de
  # `zero.policy` del capítulo 6, y salen solos a esta escala igual que
  # salían a escala municipal.
  islas           = sum(card(nb_dep) == 0),
  subgrafos       = n.comp.nb(nb_dep)$nc,
  grado_medio     = r6(mean(card(nb_dep)))
)

# El MISMO indicador a escala municipal. No es un extra: es el argumento
# del fixture. Agregar de 1 122 municipios a 33 departamentos no suaviza
# el mapa, le arranca la autocorrelación — que es el efecto escala del
# MAUP con dato colombiano, y se mide en vez de afirmarse.
muni_ok <- muni[!is.na(muni$desercion), ]
nb_mun <- suppressWarnings(poly2nb(muni_ok, queen = TRUE))
lw_mun <- nb2listw(nb_mun, style = "W", zero.policy = TRUE)
mi_mun <- moran.test(muni_ok$desercion, lw_mun, zero.policy = TRUE)

D$escala <- list(
  n_municipal      = nrow(muni_ok),
  moran_municipal  = r6(mi_mun$estimate[["Moran I statistic"]]),
  p_municipal      = mi_mun$p.value,
  n_departamental  = nrow(dep_ok),
  moran_departamental = r6(mi$estimate[["Moran I statistic"]]),
  p_departamental  = r6(mi$p.value),
  # Cuánto se pierde. Es la cifra con la que el módulo 1 cierra.
  caida_pct        = r6(100 * (1 - mi$estimate[["Moran I statistic"]] /
                                 mi_mun$estimate[["Moran I statistic"]])),
  islas_municipal  = sum(card(nb_mun) == 0),
  subgrafos_municipal = n.comp.nb(nb_mun)$nc,
  grado_municipal  = r6(mean(card(nb_mun)))
)

# --- El mapa del fixture: coropleto de 33 departamentos ----------------
mapa <- geo_poligonos(
  dep_ok, valor = dep_ok$desercion, n_clases = 5, estilo = "quantile",
  titulo = "Deserción escolar por departamento (%)",
  leyenda = "deserción (%)", presupuesto = 3000L)
mapa$etiquetas <- as.character(dep_ok$shapeName)

D$mapa_cortes <- r6(mapa$cortes)
D$mapa_n <- mapa$n

# ---------------------------------------------------------------------
message("6/6 · Escritura")
# ---------------------------------------------------------------------
D$meta <- list(
  generado = format(Sys.Date()),
  semilla  = 2026,
  r        = R.version.string
)

# Un CSV pequeño que R y Python leen IGUAL. Es lo que permite que el
# contraste de clasificación del módulo 2 sea un contraste de verdad: los
# dos lenguajes parten del mismo archivo, así que cualquier diferencia en
# la partición es del algoritmo y no del dato.
write.csv(data.frame(dpto = dep_ok$dpto,
                     nombre = dep_ok$shapeName,
                     desercion = r6(dep_ok$desercion)),
          file.path(SALIDAS, "demo_departamentos.csv"),
          row.names = FALSE, fileEncoding = "UTF-8")

write_json(D, file.path(SALIDAS, "demo_auditoria.json"),
           auto_unbox = TRUE, digits = 10, pretty = TRUE, na = "null")
write_json(mapa, file.path(SALIDAS, "demo_auditoria_mapa.json"),
           auto_unbox = TRUE, digits = 10, na = "null")

kb <- file.size(file.path(SALIDAS, "demo_auditoria_mapa.json")) / 1024
message(sprintf("\ndemo_auditoria.json      %.1f KB",
                file.size(file.path(SALIDAS, "demo_auditoria.json")) / 1024))
message(sprintf("demo_auditoria_mapa.json %.1f KB  (presupuesto 120 KB)", kb))
if (kb > 120) stop("el mapa del fixture se sale del presupuesto de 120 KB")

message("\nCifras que el capítulo-fixture va a citar:")
message(sprintf("  Columbus reina        %d aristas, grado %.4f",
                D$columbus$aristas_reina, D$columbus$grado_reina))
message(sprintf("  Moran I (deserción)   %.4f   p = %.6f",
                D$desercion$moran_I, D$desercion$moran_p))
message(sprintf("  lambda urbana / D.C.  %.4f / %.4f  -> factor %.4f",
                D$ventanas$lambda_urbana, D$ventanas$lambda_dc,
                D$ventanas$factor_lambda))
message(sprintf("  gradiente termico     %.4f C/1000 m  (corr %.4f)",
                D$clima$gradiente, D$clima$corr))
message(sprintf("  empates en los cortes %d de %d condados",
                D$nc$empates_en_cortes, D$nc$n_condados))
message(sprintf("  MAUP, efecto escala   I = %.4f (%d municipios) -> %.4f (%d dptos), cae %.2f %%",
                D$escala$moran_municipal, D$escala$n_municipal,
                D$escala$moran_departamental, D$escala$n_departamental,
                D$escala$caida_pct))
