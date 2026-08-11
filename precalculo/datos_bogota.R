# =====================================================================
# T0.4 — El patrón puntual: colegios de Bogotá y sus dos ventanas
#
# Material de Estadística Espacial 2026-II (20929).
#
# Es el conjunto de PATRÓN PUNTUAL del hilo colombiano (capítulos 4 y 5).
# Tres capas, de la misma casa (Secretaría Distrital de Planeación y
# Secretaría de Educación del Distrito, publicadas por IDECA):
#
#   colegios          — 2 211 sedes educativas, EPSG:3857 en origen
#   perímetro urbano  — la ventana A
#   localidades       — las 20 localidades; su unión es la ventana B
#
# LA VENTANA NO ES UN DETALLE. Bogotá D.C. incluye Sumapaz: la mitad del
# área del distrito, rural, casi sin colegios. La intensidad λ = n/|W| y
# las funciones K, G y F dependen de |W|, así que elegir ventana CAMBIA
# los números. Se congelan las DOS y el capítulo 4 mide bajo cada una en
# vez de afirmar que la ventana importa.
#
# Correr desde la carpeta del curso:
#   .../4.4-arm64/Resources/bin/Rscript precalculo/datos_bogota.R
# =====================================================================

# La guarda de codificacion va PRIMERO: sin ella jsonlite escribe las
# tildes como <c3><b3> sin fallar, y el emparejamiento por categoria
# con tilde deja de emparejar en silencio. Ver precalculo/utf8.R.
source("precalculo/utf8.R")
source("precalculo/entorno.R")
source("precalculo/fuentes.R")
suppressPackageStartupMessages({ library(sf); library(jsonlite) })

CRUDO <- "datos/crudo"; PROC <- "datos/procesado"
dir.create(CRUDO, recursive = TRUE, showWarnings = FALSE)
dir.create(PROC,  recursive = TRUE, showWarnings = FALSE)

# Las URL del portal de Bogotá se fijan por UUID DE RECURSO, y el UUID es
# por versión: «12.25» es una versión concreta y congelada, no un
# «current» que rota. Es el equivalente del commit de geoBoundaries.
BASE <- "https://datosabiertos.bogota.gov.co/dataset"
URL_COLEGIOS  <- file.path(BASE, "d451b52f-e30c-43b3-9066-3a7816638fea",
                           "resource/157d4822-d1d5-4d71-8c3e-1ac27e7421cb/download/cole")
URL_PERIMETRO <- file.path(BASE, "12a704ee-e5bb-4c5d-bad6-a5069d12f90a",
                           "resource/2b5ed242-8e16-4afb-9f85-13790170f874/download/perimetrourbano.json")
URL_LOCALIDAD <- file.path(BASE, "856cb657-8ca3-4ee8-857f-37211173b1f8",
                           "resource/497b8756-0927-4aee-8da9-ca4e32ca3a8a/download/loca.json")

VERSION_COLEGIOS <- "12.25"   # diciembre de 2025
CRS_TRABAJO      <- 9377      # MAGNA-SIRGAS / Origen Nacional, igual que las capas nacionales

# ---------------------------------------------------------------------
# Diccionarios de dominio.
#
# El GeoJSON publica los campos CODIFICADOS: SECTOR vale 1 o 2, no
# «Oficial». Los códigos se leen del servicio ArcGIS de origen
# (educacion/infraestructuraeducativa/MapServer/0), no se adivinan.
#
# TRAMPA: SECTOR 1 = No Oficial y 2 = Oficial, al revés de lo que sugiere
# la intuición. Invertirlo daría un mapa de colegios privados rotulado
# «oficiales» y ninguna comprobación numérica lo cazaría.
# ---------------------------------------------------------------------
DOM_SECTOR <- c("1" = "No oficial", "2" = "Oficial")
DOM_ZONA   <- c("1" = "Urbana", "2" = "Rural", "3" = "Rural (expansion urbana)",
                "4" = "Rural (reserva forestal)",
                "5" = "20% urbano / 80% expansion", "6" = "30% urbano / 70% expansion")
DOM_CALEND <- c("1" = "A", "2" = "A - B", "3" = "B", "4" = "B - Otro", "5" = "Otro")
DOM_GENERO <- c("1" = "Femenino", "2" = "Femenino-Mixto", "3" = "Masculino",
                "4" = "Masculino-Mixto", "5" = "Mixto", "6" = "Mixto-Masculino")
DOM_CLASE  <- c("1" = "Distrital", "2" = "Distrital - administracion contratada",
                "3" = "Oficial - regimen especial", "4" = "Privado",
                "5" = "Privado - matricula contratada", "6" = "Privado - regimen especial")
DOM_CARACT <- c("1" = "Academico", "2" = "Academico - tecnico", "3" = "Tecnico",
                "4" = "Sin informacion")
DOM_ESTRATO <- c("0" = "No indica estrato", "1" = "Estrato 1", "2" = "Estrato 2",
                 "3" = "Estrato 3", "4" = "Estrato 4", "5" = "Estrato 5",
                 "6" = "Estrato 6", "7" = "Sin estrato")
DOM_LOCA <- c("01"="Usaquen","02"="Chapinero","03"="Santa Fe","04"="San Cristobal",
              "05"="Usme","06"="Tunjuelito","07"="Bosa","08"="Kennedy","09"="Fontibon",
              "10"="Engativa","11"="Suba","12"="Barrios Unidos","13"="Teusaquillo",
              "14"="Los Martires","15"="Antonio Narino","16"="Puente Aranda",
              "17"="La Candelaria","18"="Rafael Uribe Uribe","19"="Ciudad Bolivar",
              "20"="Sumapaz")

decodifica <- function(v, dom) unname(dom[as.character(v)])

procedencia <- list()

# ---------------------------------------------------------------------
# 1. Colegios — el patrón puntual
# ---------------------------------------------------------------------
message("1. colegios de Bogota (SED, version ", VERSION_COLEGIOS, ")")
f_cole <- descarga(URL_COLEGIOS, file.path(CRUDO, "bogota_colegios_1225.geojson"))
cole <- sf::st_read(f_cole, quiet = TRUE)
n_bruto <- nrow(cole)
message(sprintf("  leidos %d rasgos, CRS de origen EPSG:%s", n_bruto, sf::st_crs(cole)$epsg))

# GEOMETRÍAS CENTINELA. La fuente codifica «sin ubicación» como
# ±DBL_MAX (-1.797e308), que NO es un NA: st_is_valid las da por buenas y
# viajan al análisis empujando el bounding box al infinito. Se detectan
# por magnitud, se cuentan y se declaran; nunca se corrigen a mano.
xy <- sf::st_coordinates(cole)
centinela <- !is.finite(xy[, 1]) | !is.finite(xy[, 2]) |
             abs(xy[, 1]) > 2e7 | abs(xy[, 2]) > 2e7
n_centinela <- sum(centinela)
if (n_centinela > 0) {
  message(sprintf("  %d geometria(s) centinela (+/-DBL_MAX) -> se descartan y se declaran:", n_centinela))
  for (i in which(centinela)) message("     ", cole$NOMBRE_SED[i])
  cole <- cole[!centinela, ]
}

v <- valida_geometria(cole, "colegios"); cole <- v$x
cole <- sf::st_transform(cole, CRS_TRABAJO)

cole$dane_sede    <- as.character(cole$DANE12_SED)
cole$dane_est     <- as.character(cole$DANE12_EST)
cole$nombre       <- cole$NOMBRE_SED
cole$establecim   <- cole$NOMBRE_EST
cole$sector       <- decodifica(cole$SECTOR,    DOM_SECTOR)
cole$clase        <- decodifica(cole$CLASE_TIPO, DOM_CLASE)
cole$caracter     <- decodifica(cole$CARACTER_P, DOM_CARACT)
cole$calendario   <- decodifica(cole$CALENDARIO, DOM_CALEND)
cole$genero       <- decodifica(cole$GENERO,     DOM_GENERO)
cole$zona         <- decodifica(cole$ZONA,       DOM_ZONA)
cole$estrato_txt  <- decodifica(cole$ESTRATO,    DOM_ESTRATO)
cole$estrato      <- suppressWarnings(as.integer(cole$ESTRATO))
cole$estrato[!cole$estrato %in% 1:6] <- NA_integer_   # 0 y 7 no son estratos
cole$cod_loca     <- sprintf("%02d", as.integer(cole$COD_LOCA))
cole$localidad    <- decodifica(cole$cod_loca, DOM_LOCA)

# Ninguna decodificación puede quedar en NA por un código que no está en
# el diccionario: eso significaría que el dominio cambió en la fuente.
for (campo in c("sector", "clase", "caracter", "calendario", "genero", "zona",
                "estrato_txt", "localidad")) {
  faltan <- sum(is.na(cole[[campo]]))
  if (faltan > 0) stop(sprintf("%d valor(es) de '%s' sin entrada en el diccionario de dominio", faltan, campo))
}
message("  dominios decodificados sin huecos: sector, clase, caracter, calendario, genero, zona, estrato, localidad")

# ---------------------------------------------------------------------
# 2. Las dos ventanas
# ---------------------------------------------------------------------
message("2. ventanas de observacion")
f_per <- descarga(URL_PERIMETRO, file.path(CRUDO, "bogota_perimetro_urbano.geojson"))
f_loc <- descarga(URL_LOCALIDAD, file.path(CRUDO, "bogota_localidades.geojson"))

per <- sf::st_read(f_per, quiet = TRUE)
v <- valida_geometria(per, "perimetro"); per <- sf::st_transform(v$x, CRS_TRABAJO)
rep_per <- v$reparadas

loc <- sf::st_read(f_loc, quiet = TRUE)
v <- valida_geometria(loc, "localidades"); loc <- sf::st_transform(v$x, CRS_TRABAJO)
rep_loc <- v$reparadas
message(sprintf("  localidades: %d rasgos", nrow(loc)))

ventana_urbana <- sf::st_union(sf::st_geometry(per))
ventana_dc     <- sf::st_union(sf::st_geometry(loc))

area_urb <- as.numeric(sf::st_area(ventana_urbana)) / 1e6   # km²
area_dc  <- as.numeric(sf::st_area(ventana_dc))     / 1e6

# ---------------------------------------------------------------------
# 3. Coherencia con la capa nacional: los colegios tienen que caer dentro
#    de Bogotá D.C. según geoBoundaries, que es OTRA fuente. Es la misma
#    idea que validó la llave DIVIPOLA: una comprobación que no comparte
#    el modo de fallar con lo que comprueba.
# ---------------------------------------------------------------------
message("3. coherencia contra la capa nacional (geoBoundaries)")
nac <- carga_municipios(saber11 = FALSE)
bog_nac <- nac[which(nac$divipola == "11001"), ]
stopifnot(nrow(bog_nac) == 1)
dentro_nac <- lengths(sf::st_within(cole, sf::st_geometry(bog_nac))) == 1
message(sprintf("  colegios dentro del poligono 11001 de geoBoundaries: %d de %d (fuera: %d)",
                sum(dentro_nac), nrow(cole), sum(!dentro_nac)))

dentro_urb <- lengths(sf::st_within(cole, ventana_urbana)) == 1
dentro_dc  <- lengths(sf::st_within(cole, ventana_dc))     == 1
cole$en_urbana    <- dentro_urb
cole$en_ventana_dc <- dentro_dc

# Los que caen fuera de la ventana se DECLARAN en el dato, con su columna,
# porque spatstat los rechaza al construir el ppp y hay que saber cuáles
# son y por qué. Aquí las DOS delineaciones —IDECA y geoBoundaries, que
# son fuentes distintas— coinciden en dejar fuera al mismo colegio, así
# que no es el fallo de una capa: es la coordenada o el límite real.
fuera <- which(!dentro_dc)
if (length(fuera)) {
  d_borde <- as.numeric(sf::st_distance(cole[fuera, ], sf::st_boundary(ventana_dc)))
  message(sprintf("  FUERA de la ventana D.C.: %d colegio(s), se marcan con en_ventana_dc = FALSE", length(fuera)))
  for (k in seq_along(fuera))
    message(sprintf("     %-22s | %-10s | a %.0f m del borde | dentro de geoBoundaries: %s",
                    cole$nombre[fuera[k]], cole$localidad[fuera[k]], d_borde[k],
                    dentro_nac[fuera[k]]))
}

# Cuánto se parecen las dos delineaciones del distrito. No es un adorno:
# un solape del 98 % es la diferencia entre una capa generalizada y la
# oficial del POT, y es exactamente lo que el capítulo 2 discute.
inter_dc <- as.numeric(sf::st_area(sf::st_intersection(ventana_dc, sf::st_geometry(bog_nac)))) / 1e6

# ---------------------------------------------------------------------
# 4. Lo que hace falta saber ANTES de meter esto en spatstat
# ---------------------------------------------------------------------
message("4. diagnostico de patron puntual")
co <- sf::st_coordinates(cole)
dup <- duplicated(co)
n_coincidentes <- sum(dup)
message(sprintf("  puntos coincidentes (duplicados exactos): %d -> %d localizaciones distintas de %d sedes",
                n_coincidentes, nrow(cole) - n_coincidentes, nrow(cole)))

lambda_urb <- sum(dentro_urb) / area_urb
lambda_dc  <- sum(dentro_dc)  / area_dc
message(sprintf("  ventana urbana: %.1f km2, n = %d, lambda = %.4f colegios/km2",
                area_urb, sum(dentro_urb), lambda_urb))
message(sprintf("  ventana D.C.  : %.1f km2, n = %d, lambda = %.4f colegios/km2",
                area_dc, sum(dentro_dc), lambda_dc))
message(sprintf("  => la ventana D.C. es %.1f veces mayor y da una lambda %.1f veces menor",
                area_dc / area_urb, lambda_urb / lambda_dc))

por_loca <- sort(table(cole$localidad), decreasing = TRUE)
message("  colegios por localidad (extremos): ",
        sprintf("%s = %d ... %s = %d",
                names(por_loca)[1], por_loca[1],
                names(por_loca)[length(por_loca)], por_loca[length(por_loca)]))
message("  sector: ", paste(sprintf("%s = %d", names(table(cole$sector)), table(cole$sector)), collapse = " | "))

# ---------------------------------------------------------------------
# 5. Salida
# ---------------------------------------------------------------------
campos <- c("dane_sede", "dane_est", "nombre", "establecim", "sector", "clase",
            "caracter", "calendario", "genero", "zona", "estrato", "estrato_txt",
            "cod_loca", "localidad", "en_urbana", "en_ventana_dc", "geometry")
campos <- intersect(campos, c(names(cole), attr(cole, "sf_column")))
salida <- cole[, setdiff(campos, "geometry")]

sf::st_write(salida, file.path(PROC, "bogota_colegios.gpkg"), delete_dsn = TRUE, quiet = TRUE)
sf::st_write(sf::st_sf(ventana = "perimetro urbano", geom = ventana_urbana),
             file.path(PROC, "bogota_ventana_urbana.gpkg"), delete_dsn = TRUE, quiet = TRUE)
sf::st_write(sf::st_sf(ventana = "Bogota D.C. (union de localidades)", geom = ventana_dc),
             file.path(PROC, "bogota_ventana_dc.gpkg"), delete_dsn = TRUE, quiet = TRUE)

loc$cod_loca  <- sprintf("%02d", as.integer(loc$LocCodigo))
loc$localidad <- decodifica(loc$cod_loca, DOM_LOCA)
sf::st_write(loc[, c("cod_loca", "localidad")], file.path(PROC, "bogota_localidades.gpkg"),
             delete_dsn = TRUE, quiet = TRUE)

lic_bog <- "CC BY 4.0"
procedencia$BOGOTA_COLEGIOS <- list(
  capa = "bogota_colegios.gpkg", n = nrow(salida), n_bruto = n_bruto,
  descartados_centinela = n_centinela, puntos_coincidentes = n_coincidentes,
  url = URL_COLEGIOS, version = VERSION_COLEGIOS,
  fuente = "Secretaria de Educacion del Distrito (SED), Bogota D.C.",
  redistribuidor = "Datos Abiertos Bogota / IDECA",
  licencia = "CC BY-SA 4.0",
  fuente_url = "https://datosabiertos.bogota.gov.co/dataset/colegios-bogota-d-c",
  crs = CRS_TRABAJO, geometrias_reparadas = 0,
  sha256 = huella(f_cole), descargado = as.character(Sys.Date()),
  uso = "patron puntual, capitulos 4 y 5")
procedencia$BOGOTA_VENTANA_URBANA <- list(
  capa = "bogota_ventana_urbana.gpkg", area_km2 = round(area_urb, 2),
  n_colegios = sum(dentro_urb), lambda_por_km2 = round(lambda_urb, 4),
  url = URL_PERIMETRO, fuente = "Secretaria Distrital de Planeacion, POT Bogota D.C.",
  redistribuidor = "Datos Abiertos Bogota", licencia = lic_bog,
  crs = CRS_TRABAJO, geometrias_reparadas = rep_per,
  sha256 = huella(f_per), descargado = as.character(Sys.Date()),
  uso = "ventana de observacion A (urbana)")
procedencia$BOGOTA_VENTANA_DC <- list(
  capa = "bogota_ventana_dc.gpkg", area_km2 = round(area_dc, 2),
  n_colegios = sum(dentro_dc), lambda_por_km2 = round(lambda_dc, 4),
  n_localidades = nrow(loc),
  colegios_fuera_de_ventana = sum(!dentro_dc),
  area_km2_geoboundaries_11001 = round(as.numeric(sf::st_area(bog_nac)) / 1e6, 2),
  solape_con_geoboundaries_pct = round(100 * inter_dc / area_dc, 2),
  url = URL_LOCALIDAD, fuente = "Secretaria Distrital de Planeacion, POT Bogota D.C.",
  redistribuidor = "Datos Abiertos Bogota", licencia = lic_bog,
  crs = CRS_TRABAJO, geometrias_reparadas = rep_loc,
  sha256 = huella(f_loc), descargado = as.character(Sys.Date()),
  uso = "ventana de observacion B (D.C. completo) + agregacion por localidad")

registra_procedencia(procedencia)
message("\nlisto: bogota_colegios.gpkg, bogota_ventana_urbana.gpkg, bogota_ventana_dc.gpkg, bogota_localidades.gpkg")
