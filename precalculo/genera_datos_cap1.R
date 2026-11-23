# =====================================================================
# genera_datos_cap1.R — el extracto del capítulo 1, alcanzable desde fuera
#
#   Estadística Espacial 2026-II (20929) · R3 · T3.5 (decisión D9 del
#   PLAN_Mejora_Capitulo1_Fase1.md)
#
# PARA QUÉ EXISTE
#
# Los bloques de código del capítulo 1 leían `datos/procesado/…` y
# `precalculo/salidas/…`, y llamaban a `carga_municipios()`. Nada de eso
# viaja a GitHub Pages: `datos/` es privado (431 MB) y `precalculo/` no es
# lo que un estudiante tiene delante. Quien copiaba un bloque desde el
# sitio no lo podía ejecutar (H-07 de `diagnostico_cap1/lector_estudiante.md`).
# Esto escribe en `entrega/datos/`, que sí se publica, lo MÍNIMO que los
# bloques y los ejercicios necesitan, y nada más:
#
#   cap1_municipios.gpkg        1 122 municipios: un PUNTO interior cada uno
#                               (EPSG:9377) y cinco columnas
#   cap1_municipios_reina.gal   su vecindad de reina, calculada aquí con
#                               poly2nb() sobre los polígonos COMPLETOS
#   cap1_snow.csv               muertes y bombas de Snow (para Python)
#   cap1_japanesepines.csv      el patrón de los pinos (para Python)
#   cap1_meuse.csv              zinc del Mosa con sus coordenadas (Python)
#   cap1_nc.gpkg                los condados de Carolina del Norte (Python)
#
# Y DOS QUE NO ESCRIBE, PORQUE YA ESTÁN PUBLICADOS: las estaciones del IDEAM
# y los departamentos salen de `taller1_estaciones.gpkg` y
# `taller1_departamentos.gpkg`, que `datos_taller1.R` escribió copiando
# `colombia_estaciones_clima.gpkg` y `colombia_adm1.gpkg` sin tocarlos. El
# Taller 1 está repartido: esos archivos NO se reescriben. Aquí solo se
# LEEN y se comprueba (anclas 3 y 4) que siguen siendo, vértice a vértice,
# los de `datos/procesado/`, que es de donde salen las cifras del capítulo.
#
# POR QUÉ LOS MUNICIPIOS NO LLEVAN SU POLÍGONO
#
# La geometría municipal completa son 5 031 858 vértices: 81,7 MB el
# `colombia_adm2.gpkg`, y 61 MB comprimida en zip aun reescrita solo con
# las columnas del capítulo (medido el 2026-11-23). Simplificarla
# está prohibido: cambiaría los vecinos, y con ellos la I de Moran y cada
# `#>` publicado. Lo que los bloques hacen con el polígono es UNA cosa
# —calcular la vecindad de reina—, y eso se calcula aquí, sobre el
# polígono entero, y se publica en GAL, el formato de vecindad que leen
# `spdep::read.gal()` y `libpysal.io.open()`: 48 KB. El bloque del módulo 7
# enseña la línea de `poly2nb()` que la produjo. Y lo que el ejercicio 4
# hace con el polígono —k-medias sobre un punto de cada municipio— lo da el
# punto interior (`st_point_on_surface`, el mismo que usa la solución).
#
# EL ORDEN DE LAS FILAS IMPORTA. Es el de `colombia_adm2.gpkg`, que es el
# de `carga_municipios()`. Los remuestreos del módulo 4 y del ejercicio 2
# sortean POSICIONES: con otro orden, la misma semilla da otras cifras.
#
# LOS BYTES SON REPRODUCIBLES. El GeoPackage estampa la hora en
# `gpkg_contents.last_change` (lo que obliga a `datos_taller1.R` a no
# reejecutarse por costumbre). Aquí se fija con la opción de GDAL
# `OGR_CURRENT_DATE`, de modo que reejecutar con el mismo dato deja los
# mismos bytes y ningún diff.
#
# CÓMO SE REGENERA
#
# Lo llama `genera_cap1.R` al final, justo antes de escribir el JSON, y
# guarda lo que este guion mide (filas, columnas, bytes) en el campo
# `extracto` de `cap1_datos.json`: los tamaños y los conteos que el
# capítulo publica junto a los enlaces salen de ahí. Suelto,
#
#     precalculo/rscript.sh precalculo/genera_datos_cap1.R
#
# reescribe el extracto, rehace las anclas contra el `cap1_datos.json` ya
# publicado y PARA si lo que mide no es lo que el JSON dice: entonces hay
# que regenerar el capítulo entero. Las soluciones de los ejercicios 2 y 4
# (`genera_soluciones.R 1`) leen este extracto, así que se regeneran
# DESPUÉS.
#
# LICENCIAS — se redistribuye un derivado, y la atribución viaja con él
# (en el capítulo, junto a cada enlace; ver `procedencia.json`):
#   · municipios: geometría del DANE (MGN) vía geoBoundaries, CC BY 4.0;
#     deserción y cobertura del MEN, CC BY-SA 4.0; Saber 11 del ICFES,
#     CC BY-SA 4.0.
#   · Snow (HistData), japanesepines (spatstat.data), meuse (sp) y nc (sf):
#     los datos que esos paquetes de R distribuyen, con la procedencia que
#     el capítulo ya da en su tabla del módulo 12.
#
# Correr desde la carpeta del curso.
# =====================================================================

extracto_cap1 <- function(D, destino = "entrega/datos", proc = "datos/procesado") {
  suppressPackageStartupMessages({
    library(sf); library(spdep); library(HistData); library(sp)
    library(spatstat.data); library(spatstat.geom); library(jsonlite)
  })
  message("Extracto del capítulo 1 → ", destino)

  # El generador de números aleatorios de quien llama no se toca: las
  # anclas de abajo remuestrean con sus propias semillas.
  hay_semilla <- exists(".Random.seed", envir = globalenv())
  if (hay_semilla) estado <- get(".Random.seed", envir = globalenv())
  on.exit(if (hay_semilla) assign(".Random.seed", estado, envir = globalenv()), add = TRUE)

  antes <- Sys.getenv("OGR_CURRENT_DATE", unset = NA)
  Sys.setenv(OGR_CURRENT_DATE = "2026-11-23T00:00:00Z")
  on.exit(if (is.na(antes)) Sys.unsetenv("OGR_CURRENT_DATE")
          else Sys.setenv(OGR_CURRENT_DATE = antes), add = TRUE)

  n_anclas <- 0L
  ancla <- function(cond, que) {
    n_anclas <<- n_anclas + 1L
    if (!isTRUE(cond)) stop("ANCLA ROTA (extracto) · ", que, call. = FALSE)
  }
  cerca <- function(a, b, tol = 1e-9) isTRUE(abs(as.numeric(a) - as.numeric(b)) <= tol)
  dir.create(destino, recursive = TRUE, showWarnings = FALSE)
  ruta <- function(f) file.path(destino, f)

  # -------------------------------------------------------------------
  # 1. Municipios: punto interior + cinco columnas, en el orden de la MGN
  # -------------------------------------------------------------------
  g <- st_read(file.path(proc, "colombia_adm2.gpkg"), quiet = TRUE)
  llave <- utils::read.csv(file.path(proc, "municipios_llave.csv"),
                           colClasses = "character", encoding = "UTF-8")
  s11 <- utils::read.csv(file.path(proc, "municipios_saber11.csv"),
                         colClasses = c(divipola = "character"), encoding = "UTF-8")
  i <- match(g$shapeID, llave$shapeID)
  ancla(!anyNA(i), "hay polígonos de la MGN sin fila en municipios_llave.csv")
  divipola <- llave$divipola[i]
  ancla(!anyNA(divipola) && !anyDuplicated(divipola),
        "divipola tiene vacíos o repetidos: no sirve de identificador del GAL")
  j <- match(divipola, s11$divipola)
  mun <- st_sf(
    divipola         = divipola,
    desercion        = as.numeric(llave$desercion[i]),
    cobertura        = as.numeric(llave$cobertura[i]),
    s11_punt_medio   = as.numeric(s11$s11_punt_medio[j]),
    s11_pct_internet = as.numeric(s11$s11_pct_internet[j]),
    geom = suppressWarnings(st_point_on_surface(st_geometry(g))))

  # La vecindad, con el polígono entero y con divipola como identificador.
  message("  vecindad de reina sobre los polígonos completos (tarda ~1 min)")
  nb <- suppressWarnings(poly2nb(g, queen = TRUE, row.names = divipola))

  f_mun <- ruta("cap1_municipios.gpkg")
  st_write(mun, f_mun, layer = "cap1_municipios", delete_dsn = TRUE, quiet = TRUE)
  f_gal <- ruta("cap1_municipios_reina.gal")
  write.nb.gal(nb, f_gal, oldstyle = FALSE, shpfile = "cap1_municipios", ind = "divipola")

  # -------------------------------------------------------------------
  # 2. Lo que la pestaña de Python no tiene en un paquete
  # -------------------------------------------------------------------
  r10 <- function(x) round(as.numeric(x), 10)
  data(Snow.deaths, package = "HistData", envir = environment())
  data(Snow.pumps,  package = "HistData", envir = environment())
  f_snow <- ruta("cap1_snow.csv")
  utils::write.csv(rbind(
    data.frame(tipo = "muerte", etiqueta = as.character(Snow.deaths$case),
               x = r10(Snow.deaths$x), y = r10(Snow.deaths$y)),
    data.frame(tipo = "bomba", etiqueta = as.character(Snow.pumps$label),
               x = r10(Snow.pumps$x), y = r10(Snow.pumps$y))),
    f_snow, row.names = FALSE, fileEncoding = "UTF-8")

  data(japanesepines, package = "spatstat.data", envir = environment())
  f_pinos <- ruta("cap1_japanesepines.csv")
  utils::write.csv(data.frame(x = r10(japanesepines$x), y = r10(japanesepines$y)),
                   f_pinos, row.names = FALSE, fileEncoding = "UTF-8")

  data(meuse, package = "sp", envir = environment())
  f_meuse <- ruta("cap1_meuse.csv")
  utils::write.csv(data.frame(x = meuse$x, y = meuse$y, zinc = meuse$zinc),
                   f_meuse, row.names = FALSE, fileEncoding = "UTF-8")

  # nc, SIN promover a multipolígono: el shapefile no distingue polígono de
  # multipolígono, y el lector de GDAL que usa geopandas los separa rasgo a
  # rasgo (94 y 6). Promovidos, Python leería 100 MULTIPOLYGON y el bloque
  # del módulo 9 dejaría de enseñar lo que enseña. Las 14 columnas viajan
  # todas porque ese mismo bloque las cuenta.
  nc <- st_read(system.file("shape/nc.shp", package = "sf"), quiet = TRUE,
                promote_to_multi = FALSE)
  f_nc <- ruta("cap1_nc.gpkg")
  st_write(nc, f_nc, layer = "cap1_nc", delete_dsn = TRUE, quiet = TRUE)

  # -------------------------------------------------------------------
  # 3. Las anclas: se RELEE lo escrito y se rehacen las cifras publicadas
  # -------------------------------------------------------------------
  message("  anclas sobre lo escrito")
  m <- st_read(f_mun, quiet = TRUE)
  ancla(nrow(m) == 1122L && st_crs(m)$epsg == 9377L,
        sprintf("cap1_municipios: %d filas, EPSG %s", nrow(m), st_crs(m)$epsg))
  ancla(identical(m$divipola, divipola), "el orden o los códigos de los municipios cambiaron")
  ancla(identical(st_coordinates(m), st_coordinates(mun)),
        "los puntos interiores releídos no son los calculados")
  reina <- read.gal(f_gal, region.id = m$divipola)
  ok <- !is.na(m$desercion)
  vec <- subset(reina, ok)
  # la vecindad de las 1 121 con deserción es la que el capítulo calculó
  # con poly2nb() sobre esas 1 121: la reina es una relación entre pares
  lw <- nb2listw(vec, style = "W", zero.policy = TRUE)
  I <- moran.test(m$desercion[ok], lw, zero.policy = TRUE)$estimate[["Moran I statistic"]]
  es <- D$escala
  ancla(sum(ok) == es$n_municipal, "municipios con deserción")
  ancla(cerca(I, es$moran_municipal), sprintf("I municipal %.10f", I))
  ancla(sum(card(vec) == 0) == es$islas_municipal, "islas")
  ancla(n.comp.nb(vec)$nc == es$subgrafos_municipal, "subgrafos")
  ancla(cerca(mean(card(vec)), es$grado_municipal), "grado medio")

  ir <- D$inferencia_real
  dpto <- substr(m$divipola[ok], 1, 2)
  bl <- split(m$desercion[ok], dpto)
  set.seed(2026L + 200L)
  e_i <- sd(replicate(ir$nboot, mean(sample(m$desercion[ok], sum(ok), replace = TRUE))))
  set.seed(2026L + 201L)
  e_b <- sd(replicate(ir$nboot, {
    s <- sample(seq_along(bl), length(bl), replace = TRUE)
    mean(unlist(bl[s], use.names = FALSE))
  }))
  ancla(cerca(e_i, ir$ee_bootstrap_iid) && cerca(e_b, ir$ee_bootstrap_bloques),
        "el remuestreo del módulo 4 no reproduce sus errores estándar desde el extracto")

  sn <- utils::read.csv(f_snow)
  mu <- as.matrix(sn[sn$tipo == "muerte", c("x", "y")])
  bo <- as.matrix(sn[sn$tipo == "bomba", c("x", "y")])
  dd <- as.matrix(dist(rbind(mu, bo)))[seq_len(nrow(mu)), nrow(mu) + seq_len(nrow(bo))]
  ancla(sum(max.col(-dd, ties.method = "first") ==
              which(sn$etiqueta[sn$tipo == "bomba"] == "Broad St")) == D$snow$n_mas_cerca_broad,
        "Snow desde el CSV")
  ancla(nrow(utils::read.csv(f_pinos)) == D$anatomia$ppp$n, "japanesepines")
  me <- utils::read.csv(f_meuse)
  ancla(nrow(me) == D$geo_canonico$n && cerca(mean(me$zinc), D$geo_canonico$zinc_media),
        "meuse")
  # releído también sin promover: st_read() promueve por defecto
  nc2 <- st_read(f_nc, quiet = TRUE, promote_to_multi = FALSE)
  tipos <- as.character(st_geometry_type(nc2))
  ancla(ncol(nc2) == D$anatomia$nc$columnas && nrow(nc2) == D$anatomia$nc$filas &&
          sum(tipos == "MULTIPOLYGON") == D$anatomia$nc$n_partes_multiples &&
          sum(tipos == "POLYGON") == D$anatomia$nc$filas - D$anatomia$nc$n_partes_multiples,
        "nc: filas, columnas o tipos por rasgo")

  # Los dos archivos del Taller 1 que el capítulo reutiliza: los mismos
  # vértices y los mismos valores que datos/procesado.
  e_t1 <- st_read(ruta("taller1_estaciones.gpkg"), quiet = TRUE)
  e_pr <- st_read(file.path(proc, "colombia_estaciones_clima.gpkg"), quiet = TRUE)
  ancla(identical(st_coordinates(e_t1), st_coordinates(e_pr)) &&
          identical(e_t1$t_media_anual, e_pr$t_media_anual) &&
          nrow(e_t1) == D$colombia$geo$n,
        "taller1_estaciones.gpkg ya no es colombia_estaciones_clima.gpkg")
  d_t1 <- st_read(ruta("taller1_departamentos.gpkg"), quiet = TRUE)
  d_pr <- st_read(file.path(proc, "colombia_adm1.gpkg"), quiet = TRUE)
  ancla(identical(st_coordinates(d_t1), st_coordinates(d_pr)),
        "taller1_departamentos.gpkg ya no es colombia_adm1.gpkg")

  # -------------------------------------------------------------------
  # 4. Lo que el capítulo publica del extracto
  # -------------------------------------------------------------------
  ficha <- function(f, filas, columnas, que) {
    b <- file.size(f)
    list(archivo = basename(f), ruta = f, que = que, filas = as.integer(filas),
         columnas = as.list(columnas), bytes = b,
         kb = as.integer(round(b / 1e3)), mb = round(b / 1e6, 1))
  }
  sin_geom <- function(x) setdiff(names(x), attr(x, "sf_column"))
  E <- list(
    carpeta = destino,
    municipios = c(ficha(f_mun, nrow(m), sin_geom(m), "municipios"),
                   list(n_desercion = sum(ok), n_cobertura = sum(!is.na(m$cobertura)),
                        crs_epsg = 9377L)),
    reina = ficha(f_gal, length(reina), character(0), "vecindad de reina"),
    snow = ficha(f_snow, nrow(sn), names(sn), "Snow"),
    pinos = ficha(f_pinos, D$anatomia$ppp$n, c("x", "y"), "japanesepines"),
    meuse = ficha(f_meuse, nrow(me), names(me), "meuse"),
    nc = ficha(f_nc, nrow(nc2), sin_geom(nc2), "nc"),
    estaciones = ficha(ruta("taller1_estaciones.gpkg"), nrow(e_t1),
                       sin_geom(e_t1), "reutilizado del Taller 1"),
    departamentos = ficha(ruta("taller1_departamentos.gpkg"), nrow(d_t1),
                          sin_geom(d_t1), "reutilizado del Taller 1")
  )
  # Lo que NO viaja, medido: el polígono municipal completo. El capítulo
  # lo dice junto al GAL, para que se entienda por qué la vecindad viaja
  # ya calculada.
  f_adm2 <- file.path(proc, "colombia_adm2.gpkg")
  E$poligonos <- list(archivo = basename(f_adm2), bytes = file.size(f_adm2),
                      mb = round(file.size(f_adm2) / 1e6, 1),
                      vertices = nrow(st_coordinates(g)))
  nuevos <- c(f_mun, f_gal, f_snow, f_pinos, f_meuse, f_nc)
  E$bytes_nuevos <- sum(file.size(nuevos))
  E$mb_nuevos <- round(E$bytes_nuevos / 1e6, 1)
  for (k in c("municipios", "reina", "snow", "pinos", "meuse", "nc", "estaciones",
              "departamentos"))
    message(sprintf("   %-28s %9.0f B · %d filas", E[[k]]$archivo, E[[k]]$bytes, E[[k]]$filas))
  message(sprintf("   %d anclas, todas en pie · %.1f MB nuevos", n_anclas, E$mb_nuevos))
  E
}

# Suelto: reescribe y comprueba contra lo publicado, sin tocar el JSON.
if (sys.nframe() == 0L) {
  source("precalculo/utf8.R")
  D <- jsonlite::fromJSON("precalculo/salidas/cap1_datos.json", simplifyVector = FALSE)
  E <- extracto_cap1(D)
  viejo <- D$extracto
  if (is.null(viejo)) stop("cap1_datos.json no tiene el campo `extracto`: regenera con genera_cap1.R")
  clave <- function(x) vapply(c("municipios", "reina", "snow", "pinos", "meuse", "nc",
                                "estaciones", "departamentos"),
                              function(k) paste(x[[k]]$archivo, x[[k]]$filas, x[[k]]$bytes),
                              character(1))
  if (!identical(clave(E), clave(viejo)))
    stop("el extracto escrito no es el que cap1_datos.json publica: regenera con genera_cap1.R")
  message("El extracto coincide con lo que publica cap1_datos.json.")
}
