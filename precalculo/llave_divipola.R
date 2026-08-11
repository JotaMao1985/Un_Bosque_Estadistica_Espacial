# =====================================================================
# T0.4 — La llave DIVIPOLA
#
# Material de Estadística Espacial 2026-II (20929).
#
# El problema: geoBoundaries da la GEOMETRÍA de los 1 122 municipios con
# linaje del DANE y licencia clara, pero NO trae el código DIVIPOLA. El
# MEN da los INDICADORES con el código, pero no la geometría. Sin llave
# no hay coropleto, ni Moran, ni SAR sobre Colombia.
#
# La unión tiene que pasar por los nombres, y los nombres no coinciden:
# hay paréntesis aclaratorios («Puracé (Coconuco)»), espacios que bailan
# («Labranza Grande» / «Labranzagrande») y nombres oficiales largos
# («Buga» / «Guadalajara de Buga»).
#
# Este script empareja POR ETAPAS, de la más estricta a la más laxa, y
# después VALIDA el resultado con una comprobación independiente: los dos
# primeros dígitos del código DIVIPOLA son el departamento, así que tienen
# que coincidir con el departamento que da la unión espacial. Esa
# comprobación no usa nombres, o sea que no puede fallar del mismo modo
# que el emparejamiento.
#
# TRAMPA, verificada: en macOS `iconv(x, to = "ASCII//TRANSLIT")` devuelve
# NA para toda cadena acentuada. Destruía en silencio cada municipio con
# tilde y hundía el emparejamiento al 87,5 %. Se usa stringi.
# =====================================================================

# La guarda de codificacion va PRIMERO: sin ella jsonlite escribe las
# tildes como <c3><b3> sin fallar, y el emparejamiento por categoria
# con tilde deja de emparejar en silencio. Ver precalculo/utf8.R.
source("precalculo/utf8.R")
source("precalculo/entorno.R")
source("precalculo/fuentes.R")
suppressPackageStartupMessages({
  library(sf); library(jsonlite); library(stringi)
})

# El DIVIPOLA OFICIAL del DANE. Es la lista autoritativa de qué entidades
# territoriales existen y con qué código, y sirve para dos cosas que la
# comprobación por prefijo de departamento no puede hacer:
#   1. validar los 1 122 códigos contra la fuente que los define, en vez
#      de contra una regla derivada de ellos mismos;
#   2. traer el TIPO —Municipio / Área no municipalizada / Isla—, que es
#      una particularidad del ordenamiento territorial colombiano y no un
#      detalle administrativo: 18 de las 1 122 unidades no son municipios.
URL_DIVIPOLA <- "https://www.datos.gov.co/resource/gdxc-w37w.json?$limit=2000"

# ---------------------------------------------------------------------
# Normalización
# ---------------------------------------------------------------------
norm_base <- function(s) {
  s <- stringi::stri_trans_general(s, "Latin-ASCII")
  s <- toupper(s)
  s <- gsub("[^A-Z0-9 ]", " ", s)
  gsub("\\s+", " ", trimws(s))
}
sin_parentesis <- function(s) gsub("\\s*\\(.*?\\)\\s*", " ", s)
sin_espacios   <- function(s) gsub(" ", "", s)

# Diccionario de los casos que ninguna regla resuelve: nombres realmente
# distintos entre las dos fuentes. Cada entrada es una decisión explícita
# y revisable, no una heurística.
#
# La clave lleva el DEPARTAMENTO, y no es un adorno: «Santuario» existe en
# Antioquia (donde el MEN lo llama «El Santuario») y en Risaralda (donde
# lo llama «Santuario», igual que geoBoundaries). Un diccionario que solo
# mirase el municipio arreglaba Antioquia y ROMPÍA Risaralda, que ya
# estaba bien. Cada nombre repetido del país es una trampa de este tipo.
#
#   clave = "DEPARTAMENTO|MUNICIPIO" normalizados, tal como los da geoBoundaries
#   valor = municipio normalizado tal como lo da el MEN
DICCIONARIO <- c(
  "ANTIOQUIA|SANTUARIO"                                        = "EL SANTUARIO",
  # geoBoundaries trae el nombre TRUNCADO en la propia fuente, con
  # asterisco incluido: "Distrito Especial, Industrial Y Portuario De Barr*".
  "ATLANTICO|DISTRITO ESPECIAL INDUSTRIAL Y PORTUARIO DE BARR" = "BARRANQUILLA",
  "CUNDINAMARCA|UBATE"                                         = "VILLA DE SAN DIEGO DE UBATE",
  "VALLE DEL CAUCA|BUGA"                                       = "GUADALAJARA DE BUGA",
  "VALLE DEL CAUCA|CALIMA"                                     = "CALIMA EL DARIEN",
  "CORDOBA|SAN ANDRES DE SOTAVENTO"                            = "SAN ANDRES SOTAVENTO",
  "SUCRE|SAN LUIS DE SINCE"                                    = "SINCE",
  "SUCRE|RICAURTE COLOSO"                                      = "COLOSO",
  "TOLIMA|SAN SEBASTIAN DE MARIQUITA"                          = "MARIQUITA",
  "MAGDALENA|CERRO DE SAN ANTONIO"                             = "CERRO SAN ANTONIO",
  "MAGDALENA|CHIVOLO"                                          = "CHIBOLO",
  "BOLIVAR|TIQUISO"                                            = "TIQUISIO",
  "BOLIVAR|CARTAGENA DE INDIAS"                                = "CARTAGENA",
  "SANTANDER|JORDAN SUBE"                                      = "JORDAN",
  "CHOCO|EL CARMEN"                                            = "EL CARMEN DE ATRATO",
  "AMAZONAS|SANTANDER ARARACUARA"                              = "PUERTO SANTANDER",
  "PUTUMAYO|PUERTO LEGUIZAMO"                                  = "LEGUIZAMO",
  "NARINO|TUMACO"                                              = "SAN ANDRES DE TUMACO",
  "CESAR|MANAURE BALCON DEL CESAR"                             = "MANAURE",
  "CESAR|BECERRILL"                                            = "BECERRIL",
  "GUAINIA|BARRANCO MINA"                                      = "BARRANCO MINAS",
  "BOGOTA CAPITAL DISTRICT|BOGOTA D C"                         = "BOGOTA D C"
)

# El departamento de Bogotá se llama distinto en cada fuente. Se declara
# aquí en vez de meterlo en el diccionario de municipios.
DPTO_ALIAS <- c("BOGOTA CAPITAL DISTRICT" = "BOGOTA D C")

# Municipios que geoBoundaries tiene y el MEN NO reporta en 2024. No es un
# fallo de emparejamiento: es un vacío de la fuente, y se declara para que
# nadie lo confunda con un error. Quedan con NA en las VARIABLES.
#
# El CÓDIGO, en cambio, sí se puede recuperar de otra fuente. Los
# microdatos de Saber 11 del ICFES (kgxf-xxbe, periodo 20224) reportan
# 32 estudiantes en `cole_cod_mcpio_ubicacion = 94663`, con
# `cole_mcpio_ubicacion = MAPIRIPANA` y `cole_depto_ubicacion = GUAINIA`.
# Rellenar la llave desde ahí deja la capa con los 1 122 códigos completos
# y permite unir Saber 11; las variables del MEN siguen en NA, que es lo
# honesto. Un código verificado y unas variables ausentes no son lo mismo.
SIN_DATO_MEN <- c("GUAINIA|MAPIRIPANA" = "94663")

# ---------------------------------------------------------------------
# Datos
# ---------------------------------------------------------------------
message("cargando capas y MEN 2024")
gb2 <- sf::st_read("datos/procesado/colombia_adm2.gpkg", quiet = TRUE)
gb1 <- sf::st_read("datos/procesado/colombia_adm1.gpkg", quiet = TRUE)
men <- jsonlite::fromJSON("datos/crudo/men_2024.json")

# departamento de cada municipio POR GEOMETRÍA, no por nombre
cen <- suppressWarnings(sf::st_point_on_surface(sf::st_geometry(gb2)))
dentro <- sf::st_within(cen, sf::st_geometry(gb1))
stopifnot(all(lengths(dentro) == 1))
gb2$dpto <- gb1$shapeName[unlist(dentro)]

# ---------------------------------------------------------------------
# Emparejamiento por etapas
# ---------------------------------------------------------------------
gbD <- norm_base(gb2$dpto)
gbD <- ifelse(gbD %in% names(DPTO_ALIAS), DPTO_ALIAS[gbD], gbD)
gbM <- norm_base(gb2$shapeName)
mnD <- norm_base(men$departamento); mnM <- norm_base(men$municipio)

# El diccionario se aplica ANTES de las etapas laxas, y su clave lleva el
# departamento SIN alias (tal como lo escribe geoBoundaries).
clave_dic <- paste(norm_base(gb2$dpto), gbM, sep = "|")
gbM_dic <- ifelse(clave_dic %in% names(DICCIONARIO), DICCIONARIO[clave_dic], gbM)

# OJO con el orden: `sin_parentesis` tiene que actuar sobre el nombre
# CRUDO. norm_base ya convierte «(» y «)» en espacios, así que aplicarlo
# después no quita nada — la primera versión de esta etapa emparejaba 0
# municipios justamente por eso, y el fallo pasaba por «no hay más casos
# de paréntesis» en vez de por «esta etapa no hace nada».
gbM_sp <- norm_base(sin_parentesis(gb2$shapeName))
clave_sp <- paste(norm_base(gb2$dpto), gbM_sp, sep = "|")
gbM_sp <- ifelse(clave_sp %in% names(DICCIONARIO), DICCIONARIO[clave_sp], gbM_sp)
mnM_sp <- norm_base(sin_parentesis(men$municipio))

etapas <- list(
  exacta       = list(g = paste(gbD, gbM_dic),  m = paste(mnD, mnM)),
  sin_parent   = list(g = paste(gbD, gbM_sp),   m = paste(mnD, mnM_sp)),
  sin_espacios = list(g = paste(gbD, sin_espacios(gbM_sp)),
                      m = paste(mnD, sin_espacios(mnM_sp)))
)

idx <- rep(NA_integer_, nrow(gb2))
via <- rep(NA_character_, nrow(gb2))
for (nm in names(etapas)) {
  e <- etapas[[nm]]
  pend <- is.na(idx)
  hit <- match(e$g[pend], e$m)
  idx[pend] <- hit
  via[pend & !is.na(idx)] <- nm
  message(sprintf("  etapa %-13s -> %d emparejados (acumulado %d de %d)",
                  nm, sum(!is.na(hit)), sum(!is.na(idx)), nrow(gb2)))
}

# ---------------------------------------------------------------------
# VALIDACIÓN INDEPENDIENTE
#
# Los dos primeros dígitos del DIVIPOLA son el departamento. Se comprueba
# contra el departamento obtenido por unión ESPACIAL. Esta comprobación no
# mira nombres, así que no puede equivocarse igual que el emparejamiento.
# ---------------------------------------------------------------------
ok <- !is.na(idx)
gb2$divipola <- NA_character_
gb2$divipola[ok] <- men$c_digo_municipio[idx[ok]]
gb2$dpto_cod_men <- NA_character_
gb2$dpto_cod_men[ok] <- men$c_digo_departamento[idx[ok]]

# codigo de departamento segun la geometria: el mas frecuente entre los
# municipios que SI se emparejaron dentro de cada departamento
tabla_dpto <- tapply(gb2$dpto_cod_men[ok], gb2$dpto[ok],
                     function(v) names(sort(table(v), decreasing = TRUE))[1])
esperado <- tabla_dpto[gb2$dpto]
coherente <- ok & (gb2$dpto_cod_men == esperado)

message(sprintf("\nemparejados: %d de %d (%.1f%%)", sum(ok), nrow(gb2), 100 * mean(ok)))
message(sprintf("de esos, con departamento COHERENTE con la geometria: %d (%.1f%%)",
                sum(coherente, na.rm = TRUE), 100 * mean(coherente[ok], na.rm = TRUE)))

incoherentes <- which(ok & !coherente)
if (length(incoherentes)) {
  message("\nINCOHERENTES (el codigo dice un departamento y la geometria otro):")
  for (i in incoherentes)
    message(sprintf("  %-32s geometria=%-22s codigo=%s", gb2$shapeName[i], gb2$dpto[i], gb2$divipola[i]))
}

sin <- which(!ok)
if (length(sin)) {
  message(sprintf("\nSIN PAREJA (%d):", length(sin)))
  for (i in sin) message(sprintf("  %-46s | %s", gb2$shapeName[i], gb2$dpto[i]))
}

# ---------------------------------------------------------------------
# Salida
# ---------------------------------------------------------------------
clave_gb <- paste(norm_base(gb2$dpto), norm_base(gb2$shapeName), sep = "|")
declarado_sin_dato <- clave_gb %in% names(SIN_DATO_MEN)
pendientes <- which(!ok & !declarado_sin_dato)

# Se inyecta el código recuperado de la fuente independiente y se valida
# con la MISMA comprobación que el resto: los dos primeros dígitos tienen
# que ser el departamento que da la unión espacial. Un código regalado sin
# comprobar no vale más que ninguno.
for (i in which(declarado_sin_dato & !ok)) {
  cod <- unname(SIN_DATO_MEN[clave_gb[i]])
  dpto_esperado <- unname(tabla_dpto[gb2$dpto[i]])
  if (!is.na(dpto_esperado) && substr(cod, 1, 2) != dpto_esperado)
    stop(sprintf("el codigo recuperado %s para %s no cuadra con el departamento %s de la geometria",
                 cod, gb2$shapeName[i], dpto_esperado))
  gb2$divipola[i] <- cod
  message(sprintf("  codigo recuperado de fuente independiente: %s = %s (departamento %s, coherente)",
                  gb2$shapeName[i], cod, substr(cod, 1, 2)))
}
message(sprintf("\nsin pareja NO declarados: %d  |  vacios declarados de la fuente: %d",
                length(pendientes), sum(declarado_sin_dato)))

if (length(pendientes) > 0 || !all(coherente[ok], na.rm = TRUE)) {
  message("\nNO se escribe nada: hay municipios sin pareja o incoherentes.")
  message("Anade las entradas que falten al DICCIONARIO y vuelve a correr.")
  quit(status = 1L)
}

# idx es NA en los vacios declarados: las variables quedan en NA, que es
# lo correcto. Un 0 ahi seria un dato inventado.
gb2$desercion    <- as.numeric(men$deserci_n[idx])
gb2$cobertura    <- as.numeric(men$cobertura_neta[idx])
gb2$municipio    <- ifelse(is.na(idx), gb2$shapeName, men$municipio[idx])
gb2$departamento <- ifelse(is.na(idx), gb2$dpto, men$departamento[idx])

# ---------------------------------------------------------------------
# VALIDACIÓN CONTRA LA FUENTE AUTORITATIVA
#
# La comprobación por prefijo de departamento es buena pero es interna:
# valida los códigos contra la geometría, no contra quien los define. El
# DIVIPOLA del DANE es la lista oficial, y contrastar contra ella es lo
# que convierte «los códigos son coherentes» en «los códigos son los que
# son». También es lo que destapó los dos casos territoriales de abajo.
# ---------------------------------------------------------------------
message("\nvalidacion contra el DIVIPOLA oficial del DANE")
f_dv <- descarga(URL_DIVIPOLA, "datos/crudo/divipola_gdxc_w37w.json")
dv <- jsonlite::fromJSON(f_dv)
message(sprintf("  DIVIPOLA oficial: %d entidades (%s)", nrow(dv),
                paste(sprintf("%s %d", names(table(dv$tipo_municipio)), table(dv$tipo_municipio)),
                      collapse = ", ")))

k <- match(gb2$divipola, dv$cod_mpio)
gb2$tipo <- dv$tipo_municipio[k]
reconocidos <- sum(!is.na(k))
message(sprintf("  codigos nuestros reconocidos por el DIVIPOLA: %d de %d (%.1f%%)",
                reconocidos, nrow(gb2), 100 * reconocidos / nrow(gb2)))

nuestros_no_oficiales <- gb2$divipola[is.na(k)]
oficiales_sin_poligono <- setdiff(dv$cod_mpio, gb2$divipola)

# ---------------------------------------------------------------------
# CASOS TERRITORIALES
#
# Las dos discrepancias no son ruido: son el ordenamiento territorial
# colombiano moviéndose, y cada entidad del Estado moviéndose a su ritmo.
# Van al material como caso trabajado, no a una nota al pie.
# ---------------------------------------------------------------------
CASOS <- list(
  list(nombre = "Belen de Bajira",
       codigo_divipola_oficial = "27493", nombre_oficial = "NUEVO BELEN DE BAJIRA",
       codigo_usado_por_icfes = "27086", departamento = "Choco",
       tiene_poligono_en_mgn = FALSE,
       que_pasa = paste("Territorio en disputa entre Choco y Antioquia. El DIVIPOLA lo reconoce",
                        "como municipio con el codigo 27493; el ICFES codifica a sus estudiantes",
                        "bajo 27086, que el DIVIPOLA no lista; y el Marco Geoestadistico Nacional",
                        "no tiene poligono para el. Tres entidades del Estado, tres respuestas"),
       consecuencia = "sus estudiantes no entran en ningun poligono: quedan fuera del mapa"),
  list(nombre = "Mapiripana",
       codigo_divipola_oficial = NA, nombre_oficial = NA,
       codigo_usado_por_icfes = "94663", departamento = "Guainia",
       tiene_poligono_en_mgn = TRUE,
       que_pasa = paste("El caso espejo. La cartografia SI tiene su poligono, pero el DIVIPOLA",
                        "vigente ya retiro el codigo: el territorio quedo dentro de Barrancominas",
                        "(94343), que esta ademas como poligono aparte en la misma capa. El ICFES",
                        "de 2022 seguia usando el codigo antiguo"),
       consecuencia = "se conserva el codigo historico 94663, marcado como retirado"))

gb2$divipola_estado <- ifelse(is.na(k), "codigo historico o no vigente", "vigente en DIVIPOLA")
gb2$tipo[is.na(gb2$tipo)] <- "Sin clasificar en DIVIPOLA vigente"

for (c_ in nuestros_no_oficiales)
  message(sprintf("  nuestro codigo %s (%s) NO esta en el DIVIPOLA vigente",
                  c_, gb2$municipio[gb2$divipola == c_]))
for (c_ in oficiales_sin_poligono) {
  r <- dv[dv$cod_mpio == c_, ]
  message(sprintf("  el DIVIPOLA tiene %s (%s, %s) y NO hay poligono para el",
                  c_, r$nom_mpio, r$tipo_municipio))
}
message(sprintf("  tipos en la capa: %s",
                paste(sprintf("%s %d", names(table(gb2$tipo)), table(gb2$tipo)), collapse = " | ")))

jsonlite::write_json(CASOS, "datos/procesado/casos_territoriales.json",
                     auto_unbox = TRUE, pretty = TRUE, na = "null")

# ---------------------------------------------------------------------
# Salida: la geometria NO se duplica.
#
# `colombia_adm2.gpkg` ya tiene los 1 122 poligonos y no se toca. Aqui
# solo sale la tabla de atributos, unida por `shapeID`. Antes esto era un
# GeoPackage de 78 MB con la geometria repetida; ahora son unos cientos
# de KB. `carga_municipios()` de fuentes.R rehace la union.
# ---------------------------------------------------------------------
salida <- data.frame(
  shapeID        = gb2$shapeID,
  divipola       = gb2$divipola,
  municipio      = gb2$municipio,
  departamento   = gb2$departamento,
  tipo           = gb2$tipo,
  divipola_estado = gb2$divipola_estado,
  desercion      = gb2$desercion,
  cobertura      = gb2$cobertura,
  stringsAsFactors = FALSE)
utils::write.csv(salida, "datos/procesado/municipios_llave.csv",
                 row.names = FALSE, fileEncoding = "UTF-8")
message(sprintf("\nmunicipios_llave.csv escrito: %d filas, %.0f KB (antes: un GeoPackage de 78 MB)",
                nrow(salida), file.size("datos/procesado/municipios_llave.csv") / 1024))
message("casos_territoriales.json escrito: ", length(CASOS), " casos documentados.")
