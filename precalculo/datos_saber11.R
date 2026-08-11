# =====================================================================
# T0.4 — Microdatos de Saber 11: la falacia ecológica con dato real
#
# Material de Estadística Espacial 2026-II (20929).
#
# El módulo 10 del capítulo 3 («la falacia ecológica») es de los que más
# fácil salen mal: es tentador afirmar que «la correlación entre agregados
# no es la correlación entre individuos» y quedarse ahí. Con los
# microdatos de Saber 11 se puede MEDIR, que es lo que Robinson (1950)
# hizo y lo que el capítulo tiene que hacer.
#
# Y de paso resuelve el módulo 8 (MAUP, efecto escala): la MISMA pareja de
# variables a tres niveles —estudiante, municipio, departamento— da tres
# correlaciones distintas. Un solo dato, dos módulos, cero fabricación.
#
# Salidas:
#   municipios_saber11.csv            — atributos de área nacional (caps. 3, 6, 7, 8).
#                                       La geometría NO se duplica: vive en
#                                       colombia_adm2.gpkg y se une con
#                                       carga_municipios() de fuentes.R
#   bogota_colegios_saber11.gpkg      — el patrón puntual MARCADO (caps. 4, 5)
#   saber11_20224_submuestra.csv      — individuos para el simulador de la nube
#   saber11_20224_cifras.json         — las cifras exactas, calculadas sobre TODOS
#   casos_territoriales.json          — Belén de Bajirá y Mapiripana, enriquecido aquí
#
# Correr desde la carpeta del curso:
#   .../4.4-arm64/Resources/bin/Rscript precalculo/datos_saber11.R
# =====================================================================

# La guarda de codificacion va PRIMERO: sin ella jsonlite escribe las
# tildes como <c3><b3> sin fallar, y el emparejamiento por categoria
# con tilde deja de emparejar en silencio. Ver precalculo/utf8.R.
source("precalculo/utf8.R")
source("precalculo/entorno.R")
source("precalculo/fuentes.R")
suppressPackageStartupMessages({
  library(sf); library(jsonlite); library(data.table)
})

CRUDO <- "datos/crudo"; PROC <- "datos/procesado"
RECURSO <- "kgxf-xxbe"
PERIODO <- "20224"            # Saber 11 calendario A de 2022, la cohorte más reciente publicada
N_SUBMUESTRA <- 4000

# TRAMPA MEDIDA, y cuesta 10 minutos aprenderla:
#   * el endpoint de exportación (`/api/views/ID/rows.csv?accessType=DOWNLOAD`)
#     IGNORA $select y $where: devuelve los 7 109 704 registros y las 51
#     columnas, 2,8 GB, en 11 minutos.
#   * el endpoint SoQL (`/resource/ID.csv`) SÍ filtra, pero con $order
#     obliga a ordenar el millón de filas y expira.
# Lo que funciona: /resource/ID.csv, con $where y $select, sin $order y con
# un $limit por encima del total, en UNA sola petición.
COLUMNAS <- c("cole_cod_mcpio_ubicacion", "cole_cod_dane_sede", "cole_naturaleza",
              "cole_area_ubicacion", "cole_calendario", "fami_estratovivienda",
              "fami_educacionmadre", "fami_tieneinternet", "fami_tienecomputador",
              "estu_genero", "estu_estadoinvestigacion",
              "punt_global", "punt_matematicas", "punt_lectura_critica")

URL <- sprintf("https://www.datos.gov.co/resource/%s.csv?$select=%s&$where=%s&$limit=1100000",
               RECURSO,
               utils::URLencode(paste(COLUMNAS, collapse = ","), reserved = TRUE),
               utils::URLencode(sprintf("periodo='%s'", PERIODO), reserved = TRUE))

# Escala ordinal de la educación de la madre. Es una DECISIÓN de
# codificación, no un dato: se declara aquí para que se pueda discutir.
# «No sabe» y «No Aplica» son NA, no 0: no saber no es no tener estudios.
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

# ---------------------------------------------------------------------
# 1. Descarga y limpieza
# ---------------------------------------------------------------------
message("1. microdatos Saber 11, periodo ", PERIODO)
f <- descarga(URL, file.path(CRUDO, sprintf("saber11_%s.csv", PERIODO)))
d <- data.table::fread(f, encoding = "UTF-8", showProgress = FALSE)
message(sprintf("  %s registros leidos", format(nrow(d), big.mark = " ")))

n_bruto <- nrow(d)
d <- d[estu_estadoinvestigacion == "PUBLICAR"]
message(sprintf("  con estado PUBLICAR: %s (se descartan %d de otro estado)",
                format(nrow(d), big.mark = " "), n_bruto - nrow(d)))

d[, estrato := suppressWarnings(as.integer(sub("^Estrato ", "", fami_estratovivienda)))]
d[!fami_estratovivienda %chin% paste("Estrato", 1:6), estrato := NA_integer_]
d[, edu_madre := unname(EDU_MADRE[fami_educacionmadre])]
# `sprintf("%05d", NA_integer_)` devuelve la CADENA "000NA", que no falla
# y viaja como si fuera un codigo de municipio. Hay 2 registros sin codigo
# de colegio en la cohorte; se marcan como NA de verdad y se cuentan.
cod_mcpio <- suppressWarnings(as.integer(d$cole_cod_mcpio_ubicacion))
d[, divipola := ifelse(is.na(cod_mcpio), NA_character_, sprintf("%05d", cod_mcpio))]
n_sin_codigo <- sum(is.na(d$divipola))
if (n_sin_codigo > 0)
  message(sprintf("  %d registro(s) sin codigo de municipio del colegio -> divipola NA, fuera de todo agregado",
                  n_sin_codigo))
d[, dane_sede := as.character(cole_cod_dane_sede)]
d[, punt_global := as.numeric(punt_global)]

# Dos decimales, no uno: con %.1f el 10,45 % se imprimia como «10.5 %» y
# esa cifra redondeada acababa copiada a la documentacion. La cifra que se
# imprime tiene que ser la que se publica.
sin_estrato <- sum(is.na(d$estrato))
sin_madre   <- sum(is.na(d$edu_madre))
message(sprintf("  sin estrato utilizable: %s (%.2f%%) -- «Sin Estrato» y vacio; van con NA, nunca con 0",
                format(sin_estrato, big.mark = " "), 100 * sin_estrato / nrow(d)))
message(sprintf("  sin educacion de la madre utilizable: %s (%.2f%%) -- «No sabe» y «No Aplica» incluidos",
                format(sin_madre, big.mark = " "), 100 * sin_madre / nrow(d)))
message(sprintf("  punt_global: media %.2f, sd %.2f, rango %d a %d",
                mean(d$punt_global), sd(d$punt_global), min(d$punt_global), max(d$punt_global)))

# ---------------------------------------------------------------------
# 2. LA FALACIA ECOLÓGICA, MEDIDA A TRES NIVELES
#
# La misma pareja de variables (estrato de vivienda, puntaje global) en
# tres unidades de análisis. Si las tres cifras coincidieran, el módulo 10
# no tendría nada que enseñar; el que no coincidan ES la lección.
# ---------------------------------------------------------------------
message("2. la falacia ecologica, medida")

# La escalera completa para una variable individual: individuo -> municipio
# -> departamento, con la correlación municipal SIN ponderar, PONDERADA por
# el número de estudiantes, y barrida por umbral de tamaño.
#
# El barrido no es un adorno. La primera versión de este script publicaba
# solo la correlación municipal sin ponderar y sin umbral, que sale
# NEGATIVA con el estrato, y eso parecía la inversión de signo de Robinson.
# No lo es: son municipios diminutos. Hay uno con DOS estudiantes y estrato
# medio 6,00 que tira él solo del extremo alto. Con umbral 300 la
# correlación es +0,39 y ponderada por n es +0,56. Publicar el −0,06 a
# secas habría sido enseñar un artefacto como si fuera un fenómeno.
UMBRALES <- c(0, 10, 30, 100, 300, 1000)
UMBRAL   <- 30

escalera <- function(datos, xcol, etiqueta) {
  v <- datos[!is.na(get(xcol)) & !is.na(punt_global) & !is.na(divipola)]
  r_ind <- cor(v[[xcol]], v$punt_global)
  am <- v[, .(n = .N, x = mean(get(xcol)), p = mean(punt_global)), by = divipola]
  ad <- v[, .(n = .N, x = mean(get(xcol)), p = mean(punt_global)),
          by = .(dpto = substr(divipola, 1, 2))]
  barrido <- lapply(UMBRALES, function(u) {
    s <- am[n >= u]; list(umbral = u, n_municipios = nrow(s), r = round(cor(s$x, s$p), 4))
  })
  r_pond <- stats::cov.wt(cbind(am$x, am$p), wt = am$n, cor = TRUE)$cor[1, 2]
  r_dpto <- cor(ad$x, ad$p)

  # ¿Es la ausencia del dato inocente? Si los municipios donde MÁS gente
  # responde la variable son también los de mejor puntaje, quitarlos no es
  # quitar ruido: es sesgar. Se mide, no se supone.
  cob <- datos[!is.na(punt_global), .(cob = mean(!is.na(get(xcol)))), by = divipola]
  mm  <- merge(am, cob, by = "divipola")
  r_cob_p <- cor(mm$cob, mm$p); r_cob_x <- cor(mm$cob, mm$x)

  message(sprintf("  --- %s (n = %s estudiantes) ---", etiqueta, format(nrow(v), big.mark = " ")))
  message(sprintf("      individuo                      r = %+.4f", r_ind))
  for (b in barrido)
    message(sprintf("      municipio  n>=%-4d (%4d unid.)  r = %+.4f", b$umbral, b$n_municipios, b$r))
  message(sprintf("      municipio  ponderado por n       r = %+.4f", r_pond))
  message(sprintf("      departamento    (%2d unid.)      r = %+.4f", nrow(ad), r_dpto))
  message(sprintf("      ausencia del dato: corr(cobertura, puntaje medio) = %+.4f | corr(cobertura, x medio) = %+.4f",
                  r_cob_p, r_cob_x))

  list(n = nrow(v), r_individuo = round(r_ind, 4),
       r_municipio_barrido = barrido,
       r_municipio_umbral_30 = round(cor(am[n >= UMBRAL]$x, am[n >= UMBRAL]$p), 4),
       r_municipio_ponderado = round(r_pond, 4),
       r_departamento = round(r_dpto, 4), n_departamentos = nrow(ad),
       corr_cobertura_puntaje = round(r_cob_p, 4),
       corr_cobertura_variable = round(r_cob_x, 4))
}

val <- d[!is.na(estrato) & !is.na(punt_global)]
esc_estrato <- escalera(d, "estrato",   "estrato de vivienda (1-6)")
esc_madre   <- escalera(d, "edu_madre", "educacion de la madre (0-9)")

# Por qué pasa: al agregar se tira la variación DENTRO de cada unidad y
# solo sobrevive la de ENTRE unidades. Es una cifra, no una metáfora.
ss_tot <- sum((val$punt_global - mean(val$punt_global))^2)
medias <- val[, .(m = mean(punt_global), n = .N), by = divipola]
ss_entre <- sum(medias$n * (medias$m - mean(val$punt_global))^2)
icc <- ss_entre / ss_tot
message(sprintf("  varianza del puntaje que vive ENTRE municipios: %.1f%% (dentro: %.1f%%)",
                100 * icc, 100 * (1 - icc)))
message("  LECTURA: la educacion de la madre da la escalera limpia (+0,31 -> +0,29 -> +0,57):")
message("  estable frente al umbral y creciente al agregar. El estrato da el caso de aviso:")
message("  su correlacion municipal depende del umbral y del ponderador, que es material del")
message("  modulo 2 del capitulo 3 («normalizar o mentir») antes que del modulo 10.")

# ---------------------------------------------------------------------
# 3. Capa de área nacional
# ---------------------------------------------------------------------
message("3. agregados municipales")
muni <- carga_municipios(saber11 = FALSE)

# OJO CON EL NOMBRE. La primera version llamaba `s11_n` al conteo hecho
# sobre `val`, que ya esta filtrado a quien tiene estrato. Un capitulo que
# lea «s11_n» va a entender «estudiantes del municipio», y en Belen de
# Bajira eso eran 216 en vez de 290. El conteo y el puntaje salen de TODOS
# los que tienen puntaje; lo que depende del estrato se nombra aparte.
agr_full <- d[!is.na(punt_global) & !is.na(divipola),
              .(s11_n         = .N,
                s11_punt_medio = round(mean(punt_global), 3),
                s11_punt_sd    = round(sd(punt_global), 3)), by = divipola]
agr_estr <- val[, .(s11_n_estrato     = .N,
                    s11_estrato_medio = round(mean(estrato), 4)), by = divipola]
agr_full <- merge(agr_full, agr_estr, by = "divipola", all.x = TRUE)
# TRAMPA, y costó 4,3 puntos porcentuales: en R `"" == "Si"` es FALSE, no
# NA, así que `mean(x == "Si", na.rm = TRUE)` cuenta cada respuesta VACÍA
# como un «no tiene». El na.rm no protege de nada porque no hay ningún NA
# que quitar. Con los 63 326 vacíos de `fami_tieneinternet` la cobertura
# nacional pasaba del 72,60 % real al 68,29 %, y el sesgo se concentra
# donde más ausencia hay — que son justo los municipios rurales. El vacío
# se convierte en NA de forma explícita ANTES de comparar.
vacio_a_na <- function(x) { x[x == ""] <- NA_character_; x }
extra <- d[!is.na(punt_global),
           .(s11_pct_oficial  = round(100 * mean(vacio_a_na(cole_naturaleza) == "OFICIAL", na.rm = TRUE), 2),
             s11_pct_internet = round(100 * mean(vacio_a_na(fami_tieneinternet) == "Si", na.rm = TRUE), 2),
             s11_cob_internet = round(100 * mean(!is.na(vacio_a_na(fami_tieneinternet))), 2),
             s11_edu_madre_media = round(mean(edu_madre, na.rm = TRUE), 4)),
           by = divipola]
agr_full <- merge(agr_full, extra, by = "divipola", all.x = TRUE)

i <- match(muni$divipola, agr_full$divipola)
for (cl in setdiff(names(agr_full), "divipola")) muni[[cl]] <- agr_full[[cl]][i]

con <- sum(!is.na(muni$s11_n))
message(sprintf("  municipios de la capa con datos de Saber 11: %d de %d", con, nrow(muni)))
sin <- which(is.na(muni$s11_n) & !is.na(muni$divipola))
if (length(sin)) {
  message(sprintf("  sin datos (%d), van con NA y declarados:", length(sin)))
  for (i in sin)
    message(sprintf("     %s  %-18s %-12s [%s]", muni$divipola[i], muni$municipio[i],
                    muni$departamento[i], muni$tipo[i]))
  # Qué TIPO de entidad se queda sin dato no es un detalle: si son
  # sistemáticamente áreas no municipalizadas, el vacío tiene geografía.
  message(sprintf("     por tipo: %s",
                  paste(sprintf("%s %d", names(table(muni$tipo[sin])), table(muni$tipo[sin])),
                        collapse = " | ")))
}
# Los códigos de Saber 11 sin polígono no se tiran a la basura: se cuentan
# y se devuelven a `casos_territoriales.json`, que es donde el capítulo 3
# los va a buscar. Un estudiante que no cabe en ningún mapa es exactamente
# el tipo de cosa que este material tiene que saber decir en voz alta.
huerfanos <- setdiff(agr_full$divipola, muni$divipola)
casos <- jsonlite::fromJSON(file.path(PROC, "casos_territoriales.json"), simplifyVector = FALSE)
if (length(huerfanos)) {
  message(sprintf("  codigos de Saber 11 SIN poligono (%d):", length(huerfanos)))
  for (h in huerfanos) {
    n_total <- agr_full$s11_n[agr_full$divipola == h]
    n_agreg <- agr_full$s11_n_estrato[agr_full$divipola == h]
    message(sprintf("     %s -> %d estudiantes que no caen en ningun poligono (%d con estrato)",
                    h, n_total, n_agreg))
    for (ci in seq_along(casos))
      if (identical(casos[[ci]]$codigo_usado_por_icfes, h)) {
        casos[[ci]]$estudiantes_saber11_20224 <- n_total
        casos[[ci]]$estudiantes_con_estrato   <- n_agreg
      }
  }
  jsonlite::write_json(casos, file.path(PROC, "casos_territoriales.json"),
                       auto_unbox = TRUE, pretty = TRUE, na = "null")
}

# La geometria NO se vuelve a escribir: ya vive en colombia_adm2.gpkg.
# Aqui sale solo la tabla de atributos, unida por divipola.
utils::write.csv(sf::st_drop_geometry(muni)[, c("divipola", names(agr_full)[-1])],
                 file.path(PROC, "municipios_saber11.csv"),
                 row.names = FALSE, fileEncoding = "UTF-8")
message(sprintf("  municipios_saber11.csv escrito: %.0f KB (antes: un GeoPackage de 78 MB)",
                file.size(file.path(PROC, "municipios_saber11.csv")) / 1024))

# ---------------------------------------------------------------------
# 3b. LA LECTURA POR TIPO DE ENTIDAD TERRITORIAL
#
# Colombia no está hecha solo de municipios: de las 1 122 unidades del
# DIVIPOLA, 18 son **áreas no municipalizadas** y 1 es isla. Son
# territorios de Amazonas, Guainía y Vaupés, y separarlos no es un
# tecnicismo administrativo: el tipo de entidad predice tanto si HAY dato
# como cuál es el dato.
#
# Se mide a nivel de ESTUDIANTE, no promediando medias municipales. Con
# unidades de 2 a 24 estudiantes, la media de medias es justo la trampa
# que ya casi se cuela con el estrato: la aritmética la domina el ruido de
# las unidades diminutas. A nivel de individuo el tamaño de la unidad no
# entra en la cuenta.
# ---------------------------------------------------------------------
message("3b. lectura por tipo de entidad territorial")
tipo_de <- setNames(muni$tipo, muni$divipola)
d[, tipo := unname(tipo_de[divipola])]
por_tipo <- d[!is.na(punt_global) & !is.na(tipo),
              .(estudiantes = .N,
                punt_medio  = round(mean(punt_global), 2),
                punt_sd     = round(sd(punt_global), 2)), by = tipo][order(-estudiantes)]
cob_tipo <- data.table::as.data.table(sf::st_drop_geometry(muni))[
  , .(unidades = .N, con_dato = sum(!is.na(s11_n))), by = tipo]
rep_tipo <- merge(por_tipo, cob_tipo, by = "tipo", all = TRUE)
for (i in seq_len(nrow(rep_tipo)))
  message(sprintf("  %-36s unidades %4d | con dato %4d (%5.1f%%) | estudiantes %s | puntaje %s",
                  rep_tipo$tipo[i], rep_tipo$unidades[i], rep_tipo$con_dato[i],
                  100 * rep_tipo$con_dato[i] / rep_tipo$unidades[i],
                  format(rep_tipo$estudiantes[i], big.mark = " "),
                  ifelse(is.na(rep_tipo$punt_medio[i]), "-", format(rep_tipo$punt_medio[i]))))

# Comparar contra el literal "Área no municipalizada" depende de que la
# tilde del script y la del dato coincidan byte a byte; bajo Rscript no
# siempre pasa, y la comparacion devolvia numeric(0) SIN FALLAR: el
# mensaje de la brecha simplemente no se imprimia. Se busca por subcadena.
mun_p <- por_tipo[tipo == "Municipio", punt_medio]
anm_p <- por_tipo[grepl("no municipalizada", tipo), punt_medio]
stopifnot(length(mun_p) == 1, length(anm_p) == 1)
brecha <- mun_p - anm_p
message(sprintf("  => brecha municipio vs area no municipalizada: %.2f puntos, %.2f desviaciones tipicas",
                brecha, brecha / sd(d$punt_global, na.rm = TRUE)))

# ---------------------------------------------------------------------
# 4. El patrón puntual MARCADO: colegios de Bogotá con su puntaje
# ---------------------------------------------------------------------
message("4. patron puntual marcado (Bogota)")
cole <- sf::st_read(file.path(PROC, "bogota_colegios.gpkg"), quiet = TRUE)
bog <- val[divipola == "11001"]
por_sede <- d[divipola == "11001" & !is.na(punt_global),
              .(s11_n = .N,
                s11_punt_medio = round(mean(punt_global), 3),
                s11_punt_sd    = round(sd(punt_global), 3),
                s11_estrato_medio = round(mean(estrato, na.rm = TRUE), 4)), by = dane_sede]

j <- match(cole$dane_sede, por_sede$dane_sede)
for (cl in setdiff(names(por_sede), "dane_sede")) cole[[cl]] <- por_sede[[cl]][j]

con_marca <- sum(!is.na(cole$s11_n))
message(sprintf("  colegios con puntaje: %d de %d (%.1f%%)",
                con_marca, nrow(cole), 100 * con_marca / nrow(cole)))
message("  la mitad sin marca NO es un fallo de union: la capa trae sedes de preescolar y")
message("  primaria, que no presentan Saber 11 porque es una prueba de grado 11.")
sin_punto <- por_sede[!dane_sede %chin% cole$dane_sede]
message(sprintf("  sedes de Saber 11 SIN punto en la capa: %d, con %s estudiantes (%.1f%% de Bogota)",
                nrow(sin_punto), format(sum(sin_punto$s11_n), big.mark = " "),
                100 * sum(sin_punto$s11_n) / sum(por_sede$s11_n)))

sf::st_write(cole, file.path(PROC, "bogota_colegios_saber11.gpkg"),
             delete_dsn = TRUE, quiet = TRUE)

# ---------------------------------------------------------------------
# 5. Submuestra para el simulador
#
# El simulador de la nube individual no puede pintar 900 000 puntos en un
# canvas. Se incrusta una submuestra REPRODUCIBLE (semilla del entorno) y
# se publica su r junto al r exacto, para que se vea que la submuestra no
# cambia la conclusión.
# ---------------------------------------------------------------------
message("5. submuestra para el simulador")
set.seed(SEMILLA)
sub <- val[sample(.N, min(N_SUBMUESTRA, .N))]
r_sub <- cor(sub$estrato, sub$punt_global)
r_sub_madre <- cor(sub$edu_madre, sub$punt_global, use = "complete.obs")
message(sprintf("  estrato:   n = %d, r = %+.4f (exacto sobre todos: %+.4f, diferencia %.4f)",
                nrow(sub), r_sub, esc_estrato$r_individuo, abs(r_sub - esc_estrato$r_individuo)))
message(sprintf("  madre:     r = %+.4f (exacto: %+.4f, diferencia %.4f)",
                r_sub_madre, esc_madre$r_individuo, abs(r_sub_madre - esc_madre$r_individuo)))
data.table::fwrite(sub[, .(divipola, estrato, edu_madre, punt_global,
                           punt_matematicas, punt_lectura_critica, cole_naturaleza)],
                   file.path(PROC, sprintf("saber11_%s_submuestra.csv", PERIODO)))

# ---------------------------------------------------------------------
# 6. Cifras exactas
# ---------------------------------------------------------------------
cifras <- list(
  periodo = PERIODO, recurso = RECURSO,
  n_bruto = n_bruto, n_publicar = nrow(d), n_con_estrato_y_puntaje = nrow(val),
  sin_estrato_pct = round(100 * sin_estrato / nrow(d), 2),
  sin_educacion_madre_pct = round(100 * sin_madre / nrow(d), 2),
  punt_global = list(media = round(mean(d$punt_global), 3), sd = round(sd(d$punt_global), 3),
                     min = min(d$punt_global), max = max(d$punt_global)),
  falacia_ecologica = list(
    variable_principal = "educacion de la madre: escalera estable frente al umbral",
    variable_de_aviso  = "estrato: su correlacion municipal depende del umbral y del ponderador",
    educacion_madre = esc_madre,
    estrato = esc_estrato,
    varianza_entre_municipios_pct = round(100 * icc, 2)),
  submuestra = list(n = nrow(sub), r_estrato = round(r_sub, 4),
                    r_educacion_madre = round(r_sub_madre, 4)),
  por_tipo_territorial = list(
    nota = paste("medido a nivel de estudiante, no promediando medias de unidad:",
                 "las areas no municipalizadas tienen de 2 a 24 estudiantes y la media",
                 "de medias la dominaria el ruido de las unidades diminutas"),
    filas = lapply(seq_len(nrow(rep_tipo)), function(i) as.list(rep_tipo[i])),
    brecha_municipio_vs_area_no_municipalizada = round(brecha, 2),
    brecha_en_desviaciones_tipicas = round(brecha / sd(d$punt_global, na.rm = TRUE), 3)),
  bogota = list(colegios_con_marca = con_marca, colegios_totales = nrow(cole),
                sedes_sin_punto = nrow(sin_punto),
                estudiantes_sin_punto = sum(sin_punto$s11_n)),
  codificacion_edu_madre = as.list(EDU_MADRE))
jsonlite::write_json(cifras, file.path(PROC, sprintf("saber11_%s_cifras.json", PERIODO)),
                     auto_unbox = TRUE, pretty = TRUE)

registra_procedencia(list(SABER11 = list(
  capa = "municipios_saber11.csv + bogota_colegios_saber11.gpkg",
  n_registros = nrow(d), periodo = PERIODO,
  url = URL, recurso = RECURSO,
  fuente = "Instituto Colombiano para la Evaluacion de la Educacion (ICFES)",
  redistribuidor = "datos.gov.co (Socrata)",
  licencia = "CC BY-SA 4.0",
  fuente_url = "https://www.datos.gov.co/d/kgxf-xxbe",
  llave_municipal = "cole_cod_mcpio_ubicacion (DIVIPOLA de 5 digitos)",
  llave_sede = "cole_cod_dane_sede <-> DANE12_SED de la capa de colegios",
  sha256 = huella(f), descargado = as.character(Sys.Date()),
  uso = "falacia ecologica y MAUP (cap. 3); marcas del patron puntual (caps. 4-5); variable de area (caps. 6-8)")))

message("\nlisto. cifras en ", sprintf("saber11_%s_cifras.json", PERIODO))
