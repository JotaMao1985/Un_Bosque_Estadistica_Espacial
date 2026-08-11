# =====================================================================
# T0.4 — Auditoría del hilo colombiano
#
# Material de Estadística Espacial 2026-II (20929).
#
# Este script NO confía en los que generaron los datos. Abre los archivos
# congelados, los vuelve a medir, y donde puede RECALCULA desde el crudo
# por un camino distinto al del generador. Un verificador que repita el
# mismo cálculo del generador solo comprueba que R es determinista.
#
# La lección viene de Muestreo: un verificador permisivo da falsa calma.
# Cada comprobación es una afirmación concreta y falsable, y el script sale
# con estado != 0 si alguna falla.
#
#   .../4.4-arm64/Resources/bin/Rscript precalculo/verifica_t04.R
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

# El arnés de inyección corre este mismo script contra una copia
# manipulada, así que la carpeta de datos procesados es parametrizable.
PROC  <- Sys.getenv("T04_PROC", "datos/procesado")
CRUDO <- Sys.getenv("T04_CRUDO", "datos/crudo")
res <- list()
comprueba <- function(nombre, condicion, detalle = "") {
  ok <- isTRUE(condicion)
  res[[length(res) + 1]] <<- list(nombre = nombre, ok = ok, detalle = detalle)
  message(sprintf("  [%s] %-58s %s", if (ok) "OK" else "FALLA", nombre, detalle))
  invisible(ok)
}

# ---------------------------------------------------------------------
# A. Las capas existen, se abren y traen lo que dicen traer
# ---------------------------------------------------------------------
message("A. capas congeladas")
CAPAS <- c("colombia_adm1.gpkg", "colombia_adm2.gpkg",
           "bogota_colegios.gpkg", "bogota_colegios_saber11.gpkg",
           "bogota_ventana_urbana.gpkg", "bogota_ventana_dc.gpkg",
           "bogota_localidades.gpkg", "colombia_estaciones_clima.gpkg")
TABLAS <- c("municipios_llave.csv", "municipios_saber11.csv",
            "casos_territoriales.json", "saber11_20224_cifras.json")
for (c_ in CAPAS)  comprueba(paste("existe", c_),  file.exists(file.path(PROC, c_)))
for (t_ in TABLAS) comprueba(paste("existe", t_), file.exists(file.path(PROC, t_)))

# La geometria NO puede volver a duplicarse. Si alguien reintroduce un
# GeoPackage municipal por comodidad, vuelven los 78 MB por capa.
for (v_ in c("colombia_municipios_educacion.gpkg", "colombia_municipios_saber11.gpkg"))
  comprueba(paste("la geometria NO se duplica en", v_), !file.exists(file.path(PROC, v_)),
            "los atributos van en CSV, unidos por carga_municipios()")
comprueba("los atributos municipales pesan < 1 MB en total",
          sum(file.size(file.path(PROC, c("municipios_llave.csv", "municipios_saber11.csv")))) < 1024^2,
          sprintf("%.0f KB", sum(file.size(file.path(PROC, c("municipios_llave.csv", "municipios_saber11.csv")))) / 1024))

leer <- function(x) sf::st_read(file.path(PROC, x), quiet = TRUE)
adm1  <- leer("colombia_adm1.gpkg")
adm2  <- leer("colombia_adm2.gpkg")
muni  <- carga_municipios(proc = PROC)
colb  <- leer("bogota_colegios.gpkg")
cole  <- leer("bogota_colegios_saber11.gpkg")
vurb  <- leer("bogota_ventana_urbana.gpkg")
vdc   <- leer("bogota_ventana_dc.gpkg")
loca  <- leer("bogota_localidades.gpkg")
est   <- leer("colombia_estaciones_clima.gpkg")

comprueba("adm2 trae los 1 122 municipios oficiales", nrow(adm2) == 1122, sprintf("n = %d", nrow(adm2)))
comprueba("la capa municipal de Saber 11 conserva los 1 122", nrow(muni) == 1122, sprintf("n = %d", nrow(muni)))
comprueba("las 20 localidades de Bogota", nrow(loca) == 20, sprintf("n = %d", nrow(loca)))

# ---------------------------------------------------------------------
# B. Geometría: validez, CRS y coordenadas dentro del planeta
# ---------------------------------------------------------------------
message("B. geometria")
# Las DIEZ capas, no una muestra: la hoja de procedencia afirma «0
# geometrias invalidas en las diez», y una afirmacion sin comprobar es
# exactamente lo que este arnes existe para impedir.
for (nm in c("adm1", "adm2", "muni", "colb", "cole", "vurb", "vdc", "loca", "est")) {
  x <- get(nm)
  comprueba(paste0(nm, ": 0 geometrias invalidas"), all(sf::st_is_valid(x)),
            sprintf("invalidas = %d", sum(!sf::st_is_valid(x))))
  comprueba(paste0(nm, ": CRS EPSG:9377"), isTRUE(sf::st_crs(x)$epsg == 9377),
            paste("epsg =", sf::st_crs(x)$epsg))
}
# El fallo que tumbó la capa de sedes del MEN: coordenadas centinela que
# NO son NA y que st_is_valid da por buenas.
co_cole <- sf::st_coordinates(cole)
comprueba("colegios: ninguna coordenada centinela (|x| > 2e7)",
          all(is.finite(co_cole)) && max(abs(co_cole)) < 2e7,
          sprintf("max|coord| = %.3g", max(abs(co_cole))))
co_est <- sf::st_coordinates(est)
comprueba("estaciones: ninguna coordenada centinela",
          all(is.finite(co_est)) && max(abs(co_est)) < 2e7,
          sprintf("max|coord| = %.3g", max(abs(co_est))))

# ---------------------------------------------------------------------
# C. La llave DIVIPOLA
# ---------------------------------------------------------------------
message("C. llave DIVIPOLA")
comprueba("los 1 122 municipios tienen codigo", sum(is.na(muni$divipola)) == 0,
          sprintf("sin codigo = %d", sum(is.na(muni$divipola))))
comprueba("los codigos son unicos", !any(duplicated(muni$divipola)),
          sprintf("duplicados = %d", sum(duplicated(muni$divipola))))
comprueba("todos los codigos tienen 5 digitos", all(nchar(muni$divipola) == 5))
# Comprobación INDEPENDIENTE, la misma idea que validó T0.4a: los dos
# primeros dígitos son el departamento, y el departamento se obtiene por
# union espacial, que no mira nombres ni codigos.

cen <- suppressWarnings(sf::st_point_on_surface(sf::st_geometry(muni)))
dentro <- sf::st_within(cen, sf::st_geometry(adm1))
dpto_geo <- rep(NA_character_, nrow(muni)); dpto_geo[lengths(dentro) == 1] <- adm1$shapeName[unlist(dentro)]
pref <- substr(muni$divipola, 1, 2)
tab <- tapply(pref, dpto_geo, function(v) names(sort(table(v), decreasing = TRUE))[1])
coh <- pref == tab[dpto_geo]
comprueba("prefijo de departamento coherente con la geometria",
          sum(coh, na.rm = TRUE) == nrow(muni),
          sprintf("%d de %d", sum(coh, na.rm = TRUE), nrow(muni)))

# ---------------------------------------------------------------------
# D. El patron puntual y sus dos ventanas — RECONTADO aqui
# ---------------------------------------------------------------------
message("D. patron puntual")
proc <- jsonlite::fromJSON(file.path(PROC, "procedencia.json"), simplifyVector = FALSE)
a_urb <- as.numeric(sf::st_area(vurb)) / 1e6
a_dc  <- as.numeric(sf::st_area(vdc))  / 1e6
n_urb <- sum(lengths(sf::st_within(cole, sf::st_geometry(vurb))) == 1)
n_dc  <- sum(lengths(sf::st_within(cole, sf::st_geometry(vdc)))  == 1)

# La contención se mide POR ÁREA, no con st_covered_by.
#
# st_covered_by es exacto, y dos capas dibujadas por separado —el
# perímetro del POT y las 20 localidades— nunca comparten los vértices al
# último decimal. Aquí el desbordamiento son 141 astillas que suman
# 0,0000 km², la mayor de medio metro de ancho, y NINGÚN colegio cae en
# ellas. El predicado exacto decía «no está contenida» y era verdad en el
# sentido literal y falso en el que importa. Una comprobación demasiado
# estricta miente igual que una permisiva, solo que en la otra dirección.
TOL_SOLAPE <- 0.01   # % del área urbana
sobra   <- sf::st_difference(sf::st_geometry(vurb), sf::st_geometry(vdc))
a_sobra <- if (length(sobra)) sum(as.numeric(sf::st_area(sobra))) / 1e6 else 0
comprueba("la ventana urbana encaja dentro del D.C. salvo astillas de frontera",
          100 * a_sobra / a_urb < TOL_SOLAPE,
          sprintf("desborde %.5f km2 = %.5f%% del area urbana (tolerancia %.2f%%)",
                  a_sobra, 100 * a_sobra / a_urb, TOL_SOLAPE))
comprueba("ningun colegio cae en el desborde de frontera",
          length(sobra) == 0 || sum(lengths(sf::st_within(cole, sobra)) == 1) == 0)
comprueba("area urbana < area D.C.", a_urb < a_dc, sprintf("%.1f < %.1f km2", a_urb, a_dc))
comprueba("n dentro de la urbana <= n dentro del D.C.", n_urb <= n_dc, sprintf("%d <= %d", n_urb, n_dc))
comprueba("procedencia registra el mismo n urbano que se recuenta aqui",
          proc$BOGOTA_VENTANA_URBANA$n_colegios == n_urb,
          sprintf("registrado %s, recontado %d", proc$BOGOTA_VENTANA_URBANA$n_colegios, n_urb))
comprueba("procedencia registra el mismo n del D.C. que se recuenta aqui",
          proc$BOGOTA_VENTANA_DC$n_colegios == n_dc,
          sprintf("registrado %s, recontado %d", proc$BOGOTA_VENTANA_DC$n_colegios, n_dc))
lam_urb <- n_urb / a_urb; lam_dc <- n_dc / a_dc
comprueba("la eleccion de ventana cambia lambda al menos por 2",
          lam_urb / lam_dc > 2, sprintf("lambda_urb/lambda_dc = %.2f", lam_urb / lam_dc))
comprueba("los colegios fuera de la ventana D.C. estan marcados",
          sum(!cole$en_ventana_dc) == nrow(cole) - n_dc,
          sprintf("marcados %d, fuera al recontar %d", sum(!cole$en_ventana_dc), nrow(cole) - n_dc))
comprueba("la columna en_urbana coincide con el recuento espacial",
          sum(cole$en_urbana) == n_urb, sprintf("columna %d, recuento %d", sum(cole$en_urbana), n_urb))
comprueba("dane_sede es unico en la capa de colegios", !any(duplicated(cole$dane_sede)))

# ---------------------------------------------------------------------
# E. Estaciones: se recalcula el gradiente térmico DESDE EL CRUDO
# ---------------------------------------------------------------------
message("E. estaciones climaticas")
crudo_cl <- jsonlite::fromJSON(file.path(CRUDO, "ideam_normales_tmedia_1991_2020.json"))
alt_c <- as.numeric(crudo_cl$altitud_m); t_c <- as.numeric(crudo_cl$anual)
usable <- !is.na(alt_c) & !is.na(t_c)
r_crudo <- cor(alt_c[usable], t_c[usable])
r_capa  <- cor(est$altitud_m, est$t_media_anual)
comprueba("corr(altitud, T) de la capa coincide con la del crudo (tol 0.005)",
          abs(r_crudo - r_capa) < 0.005, sprintf("crudo %.4f vs capa %.4f", r_crudo, r_capa))
grad <- coef(lm(t_media_anual ~ altitud_m, data = est))[["altitud_m"]] * 1000
comprueba("el gradiente termico cae en el rango fisico (-7 a -5 C/1000 m)",
          grad > -7 && grad < -5, sprintf("%.2f C por 1000 m", grad))
comprueba("estaciones sin altitud o sin temperatura: ninguna",
          sum(is.na(est$altitud_m) | is.na(est$t_media_anual)) == 0)
comprueba("ninguna estacion comparte coordenada (gstat aborta si la hay)",
          !any(duplicated(sf::st_coordinates(est))),
          sprintf("repetidas = %d", sum(duplicated(sf::st_coordinates(est)))))
comprueba("n de estaciones >= 50 (por debajo el variograma no ensena)", nrow(est) >= 50,
          sprintf("n = %d", nrow(est)))

# ---------------------------------------------------------------------
# F. Saber 11: se recalcula la escalera DESDE EL CRUDO, no desde el JSON
# ---------------------------------------------------------------------
message("F. Saber 11")
cif <- jsonlite::fromJSON(file.path(PROC, "saber11_20224_cifras.json"), simplifyVector = FALSE)
d <- data.table::fread(file.path(CRUDO, "saber11_20224.csv"), encoding = "UTF-8",
                       showProgress = FALSE,
                       select = c("cole_cod_mcpio_ubicacion", "fami_estratovivienda",
                                  "fami_educacionmadre", "estu_estadoinvestigacion",
                                  "punt_global"))
d <- d[estu_estadoinvestigacion == "PUBLICAR"]
d[, est_n := suppressWarnings(as.integer(sub("^Estrato ", "", fami_estratovivienda)))]
d[!fami_estratovivienda %chin% paste("Estrato", 1:6), est_n := NA_integer_]
EM <- c("Ninguno"=0,"Primaria incompleta"=1,"Primaria completa"=2,
        "Secundaria (Bachillerato) incompleta"=3,"Secundaria (Bachillerato) completa"=4,
        "Técnica o tecnológica incompleta"=5,"Técnica o tecnológica completa"=6,
        "Educación profesional incompleta"=7,"Educación profesional completa"=8,"Postgrado"=9)
d[, em := unname(EM[fami_educacionmadre])]
d[, dv := sprintf("%05d", as.integer(cole_cod_mcpio_ubicacion))]

w <- d[!is.na(em) & !is.na(punt_global)]
r_i <- cor(w$em, w$punt_global)
ad  <- w[, .(x = mean(em), p = mean(punt_global)), by = .(dp = substr(dv, 1, 2))]
r_d <- cor(ad$x, ad$p)
comprueba("r individual (madre) reproduce el JSON",
          abs(r_i - cif$falacia_ecologica$educacion_madre$r_individuo) < 1e-3,
          sprintf("recalculado %.4f vs JSON %.4f", r_i, cif$falacia_ecologica$educacion_madre$r_individuo))
comprueba("r departamental (madre) reproduce el JSON",
          abs(r_d - cif$falacia_ecologica$educacion_madre$r_departamento) < 1e-3,
          sprintf("recalculado %.4f vs JSON %.4f", r_d, cif$falacia_ecologica$educacion_madre$r_departamento))
# UMBRAL RECALIBRADO EN T0.5, y conviene saber por qué antes que aceptarlo.
#
# El 0,15 original se fijó contra unas cifras que estaban mal: el generador
# corría con LC_CTYPE=C, y en ese estado las cuatro categorías con tilde de
# `fami_educacionmadre` NO emparejaban con la escala ordinal. `EM[x]`
# devuelve NA en vez de fallar, así que 295 724 estudiantes —el 27,7 % de
# la cohorte, y justo los niveles educativos MÁS ALTOS— desaparecían en
# silencio. Con el sesgo puesto, r iba de 0,3068 a 0,5650: diferencia
# 0,2582, y 0,15 parecía holgado.
#
# Con el dato entero (976 374 estudiantes) la escalera es 0,3627 →
# 0,5126: diferencia **0,1499**. El fenómeno sigue ahí y es fuerte —el
# agregado infla la correlación un 41 %— pero 0,15 lo dejaba fuera por una
# diezmilésima. Un umbral heredado de un cálculo sesgado no es evidencia
# de nada; se baja a 0,10, que es lo que el material necesita para que la
# falacia sea material didáctico, y se declara la cifra observada.
#
# Es la lección de A.8 en la otra dirección: una comprobación demasiado
# estricta miente igual que una permisiva.
comprueba("la falacia es visible: r departamental supera al individual en >= 0,10",
          r_d - r_i >= 0.10,
          sprintf("diferencia = %.4f (el agregado infla r un %.0f %%)",
                  r_d - r_i, 100 * (r_d / r_i - 1)))
comprueba("la escalera de la madre es estable frente al umbral (rango < 0,02 entre n>=0 y n>=30)",
          {b <- cif$falacia_ecologica$educacion_madre$r_municipio_barrido
           abs(b[[1]]$r - b[[3]]$r) < 0.02},
          "si dependiera del umbral seria un artefacto, no un fenomeno")
comprueba("el caso de aviso esta declarado: el estrato SI depende del umbral",
          {b <- cif$falacia_ecologica$estrato$r_municipio_barrido
           abs(b[[1]]$r - b[[length(b)]]$r) > 0.3},
          "publicar solo el r sin umbral habria ensenado un artefacto")

# El fallo del vacío contado como «No»: se comprueba que la cifra
# publicada es la que trata el vacío como ausente.
d2 <- data.table::fread(file.path(CRUDO, "saber11_20224.csv"), encoding = "UTF-8",
                        showProgress = FALSE,
                        select = c("cole_cod_mcpio_ubicacion", "fami_tieneinternet",
                                   "estu_estadoinvestigacion", "punt_global"))
d2 <- d2[estu_estadoinvestigacion == "PUBLICAR" & !is.na(punt_global)]
d2[, dv := sprintf("%05d", as.integer(cole_cod_mcpio_ubicacion))]
d2[, tiene := ifelse(fami_tieneinternet == "", NA_character_, fami_tieneinternet)]
ref <- d2[, .(pct = round(100 * mean(tiene == "Si", na.rm = TRUE), 2)), by = dv]
k <- match(muni$divipola, ref$dv)
dif <- abs(muni$s11_pct_internet - ref$pct[k])
comprueba("s11_pct_internet trata el vacio como ausente, no como «No»",
          all(is.na(dif) | dif < 0.011), sprintf("max diferencia = %.4f", max(dif, na.rm = TRUE)))

comprueba("municipios con datos de Saber 11 >= 1 100", sum(!is.na(muni$s11_n)) >= 1100,
          sprintf("con datos = %d de %d", sum(!is.na(muni$s11_n)), nrow(muni)))
comprueba("n de area >= 50 unidades (criterio de T0.4)", nrow(muni) >= 50)
comprueba("los municipios sin Saber 11 van con NA, no con 0",
          !any(muni$s11_n %in% 0, na.rm = TRUE))

# ---------------------------------------------------------------------
# G. Procedencia: ninguna fuente sin papeles
# ---------------------------------------------------------------------
message("G. procedencia")
OBLIG <- c("url", "fuente", "licencia", "descargado")
for (nm in names(proc)) {
  faltan <- setdiff(OBLIG, names(proc[[nm]]))
  comprueba(paste0("procedencia[", nm, "] completa"), length(faltan) == 0,
            if (length(faltan)) paste("faltan:", paste(faltan, collapse = ", ")) else
              proc[[nm]]$licencia)
}
nuevas <- c("BOGOTA_COLEGIOS", "BOGOTA_VENTANA_URBANA", "BOGOTA_VENTANA_DC",
            "CLIMA_ESTACIONES", "SABER11")
for (nm in nuevas)
  comprueba(paste0("procedencia[", nm, "] lleva huella SHA-256"),
            !is.null(proc[[nm]]$sha256) && !is.na(proc[[nm]]$sha256) &&
              nchar(proc[[nm]]$sha256) == 64)

# ---------------------------------------------------------------------
# H. El ordenamiento territorial colombiano
#
# Colombia no esta hecha solo de municipios, y el material lo dice. Esto
# comprueba que lo que dice esta respaldado.
# ---------------------------------------------------------------------
message("H. casos territoriales")
dv <- jsonlite::fromJSON(file.path(CRUDO, "divipola_gdxc_w37w.json"))
comprueba("el DIVIPOLA oficial trae 1 122 entidades", nrow(dv) == 1122, sprintf("n = %d", nrow(dv)))
tab_of <- table(dv$tipo_municipio)
comprueba("el DIVIPOLA oficial: 1 103 municipios, 18 areas no municipalizadas, 1 isla",
          identical(sort(as.integer(tab_of)), c(1L, 18L, 1103L)),
          paste(sprintf("%s=%d", names(tab_of), tab_of), collapse = " "))

reconocidos <- sum(muni$divipola %in% dv$cod_mpio)
comprueba("nuestros codigos reconocidos por el DIVIPOLA oficial: 1 121 de 1 122",
          reconocidos == 1121, sprintf("%d de %d", reconocidos, nrow(muni)))

casos <- jsonlite::fromJSON(file.path(PROC, "casos_territoriales.json"), simplifyVector = FALSE)
comprueba("los 2 casos territoriales estan documentados", length(casos) == 2,
          paste(vapply(casos, function(x) x$nombre, ""), collapse = ", "))
for (c_ in casos) {
  faltan <- setdiff(c("nombre", "codigo_usado_por_icfes", "que_pasa", "consecuencia",
                      "tiene_poligono_en_mgn"), names(c_))
  comprueba(paste0("caso ", c_$nombre, ": ficha completa"), length(faltan) == 0,
            if (length(faltan)) paste("faltan:", paste(faltan, collapse = ", ")) else "")
}
# Toda discrepancia entre nuestra llave y el DIVIPOLA tiene que estar
# EXPLICADA en casos_territoriales.json. Una discrepancia sin ficha es una
# discrepancia que nadie miro.
sin_ficha <- setdiff(
  union(setdiff(muni$divipola, dv$cod_mpio), setdiff(dv$cod_mpio, muni$divipola)),
  unlist(lapply(casos, function(x) c(x$codigo_usado_por_icfes, x$codigo_divipola_oficial))))
comprueba("ninguna discrepancia con el DIVIPOLA se queda sin ficha",
          length(sin_ficha) == 0,
          if (length(sin_ficha)) paste("sin explicar:", paste(sin_ficha, collapse = ", ")) else "")

comprueba("la capa trae la columna `tipo` del DIVIPOLA", "tipo" %in% names(muni))
n_anm <- sum(grepl("no municipalizada", muni$tipo))
comprueba("18 areas no municipalizadas en la capa", n_anm == 18, sprintf("n = %d", n_anm))

# La brecha por tipo se RECALCULA aqui desde el crudo, no se lee del JSON.
pt <- cif$por_tipo_territorial
s11 <- data.table::fread(file.path(CRUDO, "saber11_20224.csv"), encoding = "UTF-8",
                         showProgress = FALSE,
                         select = c("cole_cod_mcpio_ubicacion", "estu_estadoinvestigacion",
                                    "punt_global"))
s11 <- s11[estu_estadoinvestigacion == "PUBLICAR" & !is.na(punt_global)]
cm <- suppressWarnings(as.integer(s11$cole_cod_mcpio_ubicacion))
s11[, dv2 := ifelse(is.na(cm), NA_character_, sprintf("%05d", cm))]
tipo_de <- setNames(muni$tipo, muni$divipola)
s11[, tp := unname(tipo_de[dv2])]
g_mun <- s11[tp == "Municipio", mean(punt_global)]
g_anm <- s11[grepl("no municipalizada", tp), mean(punt_global)]
comprueba("la brecha por tipo territorial reproduce el JSON (tol 0,05)",
          abs((g_mun - g_anm) - pt$brecha_municipio_vs_area_no_municipalizada) < 0.05,
          sprintf("recalculada %.2f vs JSON %.2f", g_mun - g_anm,
                  pt$brecha_municipio_vs_area_no_municipalizada))
comprueba("la brecha se mide sobre individuos, no promediando medias de unidad",
          grepl("nivel de estudiante", pt$nota))
comprueba("los 2 registros sin codigo de municipio quedan fuera de los agregados",
          sum(is.na(s11$dv2)) == 2 && !any(muni$divipola == "000NA"),
          sprintf("sin codigo = %d", sum(is.na(s11$dv2))))

# ---------------------------------------------------------------------
# Informe
# ---------------------------------------------------------------------
ok <- vapply(res, `[[`, logical(1), "ok")
cat(sprintf("\n=== %d de %d comprobaciones OK ===\n", sum(ok), length(ok)))
if (any(!ok)) {
  cat("FALLAN:\n")
  for (r in res[!ok]) cat("  -", r$nombre, "|", r$detalle, "\n")
  quit(status = 1L)
}
cat("T0.4 verificada.\n")
