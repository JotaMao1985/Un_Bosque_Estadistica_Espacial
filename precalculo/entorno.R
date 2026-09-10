# =====================================================================
# T0.1 — Entorno del precálculo + prueba de humo
#
# Material de Estadística Espacial 2026-II (20929).
#
# Dos funciones:
#   1. source()-ado desde cualquier genera_capN.R, fija semilla y opciones
#      y deja el entorno en un estado reproducible.
#   2. Ejecutado directamente, corre la prueba de humo: no comprueba que
#      los paquetes CARGUEN, sino que CALCULEN. Cargar y calcular no son
#      lo mismo: sf carga sin GDAL utilizable.
#
# Correr SIEMPRE con la ruta absoluta:
#   /Library/Frameworks/R.framework/Versions/4.4-arm64/Resources/bin/Rscript
# El Rscript del PATH es Homebrew 4.6.0 y no tiene ni sf.
# =====================================================================

SEMILLA <- 2026

# Lo que afecte al formato de la salida va aquí Y, cuando el bloque se
# publique en el material, DENTRO del bloque: el verificador ejecuta los
# bloques con su propia cabecera y si no, marca discrepancias falsas.
options(
  scipen        = 999,      # nada de notación científica en las salidas
  digits        = 7,
  stringsAsFactors = FALSE,
  warn          = 1         # los avisos salen cuando ocurren, no al final
)

set.seed(SEMILLA)

# sf usa s2 para geometría esférica sobre lon/lat. Se deja ENCENDIDO
# (es el defecto y es lo correcto), pero el capítulo 2 lo apaga a
# propósito en un módulo para enseñar la diferencia con GEOS plano.
# Aquí se declara para que el estado de partida sea explícito.
if (requireNamespace("sf", quietly = TRUE)) sf::sf_use_s2(TRUE)

# ---------------------------------------------------------------------
# Registro de versiones: se congela en versiones.json
# ---------------------------------------------------------------------
PAQUETES <- c(
  "sf", "terra", "sp", "units", "jsonlite",
  "spdep", "spatialreg", "sfdep", "dbscan", "gstat", "spatstat",
  "spatstat.geom", "spatstat.explore", "spatstat.model", "spatstat.data",
  "tmap", "classInt", "RColorBrewer", "spData", "HistData",
  "stars", "blockCV", "spatialsample", "GWmodel", "rmapshaper"
)

# `forzar` existe porque re-congelar el acta es legítimo —el día que se
# suba de R, o que se publique desde otra máquina— pero nunca es un efecto
# secundario de haber corrido la prueba de humo. Ver la guarda de abajo.
registra_versiones <- function(destino = "precalculo/versiones.json",
                               forzar = FALSE) {
  vers <- vapply(PAQUETES, function(p) {
    if (requireNamespace(p, quietly = TRUE)) as.character(packageVersion(p)) else NA_character_
  }, character(1))

  ext <- sf::sf_extSoftVersion()

  info <- list(
    generado  = as.character(Sys.Date()),
    r         = R.version.string,
    plataforma = R.version$platform,
    rscript   = file.path(R.home("bin"), "Rscript"),
    semilla   = SEMILLA,
    sistema   = list(GDAL = unname(ext["GDAL"]),
                     GEOS = unname(ext["GEOS"]),
                     PROJ = unname(ext["PROJ"]),
                     s2   = unname(ext["s2"])),
    # Rutas a los datos que el lado de Python necesita leer para la
    # verificación cruzada. Se escriben desde aquí en vez de codificarlas
    # en el .py porque la biblioteca de R vive en el directorio del
    # USUARIO (~/Library/R/arm64/4.4/library), no dentro del framework.
    rutas     = list(nc_shp = system.file("shape/nc.shp", package = "sf"),
                     biblioteca = .libPaths()[1]),
    paquetes  = as.list(vers)
  )
  # ---------------------------------------------------------------------
  # GUARDA DE PROCEDENCIA
  #
  # Este archivo NO es un informe de la máquina que lo corre: es el ACTA
  # de la máquina que publicó el material. La diferencia no se ve mientras
  # haya una sola máquina, y por eso el fallo estuvo aquí desde el
  # principio sin morder.
  #
  # Muerde en cuanto hay una segunda. `registra_versiones()` se llama sola
  # al final de la prueba de humo de este mismo archivo —el paso natural
  # de «compruebo que mi entorno funciona»—, así que en un Windows recién
  # montado, comprobar el entorno REESCRIBÍA el acta: `plataforma` pasaba
  # a x86_64-w64-mingw32, `rutas` a rutas C:\..., y el capítulo 1 publica
  # esa tabla de versiones en su módulo de reproducibilidad.
  #
  # Y no se puede resolver separando las rutas de las cifras, que sería lo
  # limpio: la forma de este archivo ESTÁ PUBLICADA. El capítulo 1 lo cita
  # cuatro veces y el preparcial dos, en bloques de código que leen
  # `["rutas"]["nc_shp"]` y que `verifica_bloques.py` ejecuta. Partir el
  # archivo obligaría a regenerar capítulo y preparcial, que es justo lo
  # que no se hace con material ya repartido.
  #
  # Así que el acta no se parte: se defiende. Escribir sobre un acta ajena
  # tiene que ser un acto deliberado, no la consecuencia de haber mirado.
  # ---------------------------------------------------------------------
  if (!forzar && file.exists(destino)) {
    previo <- tryCatch(jsonlite::fromJSON(destino), error = function(e) NULL)
    if (!is.null(previo)) {
      difiere <- c(
        if (!identical(previo$plataforma, info$plataforma))
          paste0("  plataforma:  acta = ", previo$plataforma, "\n",
                 "               esta = ", info$plataforma),
        if (!identical(previo$r, info$r))
          paste0("  R:           acta = ", previo$r, "\n",
                 "               esta = ", info$r))
      if (length(difiere)) {
        stop("PARADO: ", destino, " lo escribió otra máquina.\n\n",
             paste(difiere, collapse = "\n"), "\n\n",
             "  Ese archivo es el acta de la máquina que PUBLICÓ el material, no\n",
             "  un informe de la que lo corre. El capítulo 1 publica su tabla de\n",
             "  versiones, y ensambla_cap1.py, ensambla_preparcial1.py,\n",
             "  ensambla_demo_auditoria.py y audita_cap1.py leen sus `rutas` para\n",
             "  cargar nc.shp y columbus.gpkg de la biblioteca de R de ESA máquina.\n",
             "  Sobrescribirlo desde aquí dejaría el material diciendo que se\n",
             "  generó donde no se generó, y las rutas apuntando a un disco ajeno.\n\n",
             "  Generar y calcular NO necesitan tocarlo: solo lo escribe esta\n",
             "  función, y solo la llama la prueba de humo de entorno.R.\n\n",
             "  Si de verdad toca re-congelar el acta —se sube de R, o se pasa a\n",
             "  publicar desde aquí— es un acto deliberado y se pide así:\n\n",
             "      registra_versiones(forzar = TRUE)\n\n",
             "  ...y entonces hay que regenerar el material, porque las cifras\n",
             "  publicadas salieron de la máquina que el acta acaba de dejar de\n",
             "  describir.",
             call. = FALSE)
      }
    }
  }

  jsonlite::write_json(info, destino, auto_unbox = TRUE, pretty = TRUE)
  invisible(info)
}

# =====================================================================
# Prueba de humo — solo si se ejecuta este archivo directamente
# =====================================================================
if (sys.nframe() == 0L) {

  resultados <- list()
  prueba <- function(nombre, expr) {
    val <- tryCatch(force(expr), error = function(e) structure(conditionMessage(e), class = "fallo"))
    ok  <- !inherits(val, "fallo")
    resultados[[nombre]] <<- list(ok = ok, valor = val)
    cat(sprintf("%-22s %s  %s\n", nombre,
                if (ok) "OK  " else "FALLO",
                if (ok) paste(format(val), collapse = " ") else val))
  }

  cat("=== PRUEBA DE HUMO DEL ENTORNO ESPACIAL ===\n")
  cat(R.version.string, "|", R.version$platform, "\n\n")

  # sp hace falta explícitamente: `coordinates<-` es suyo, y gstat no lo
  # adjunta al buscar. Cargar gstat sin sp y usar meuse falla.
  suppressPackageStartupMessages({
    library(sf); library(sp); library(spdep); library(spatialreg); library(gstat)
    library(spatstat); library(classInt); library(spData)
  })

  # --- 1. sf: leer un shapefile y reproyectar -------------------------
  nc <- st_read(system.file("shape/nc.shp", package = "sf"), quiet = TRUE)
  prueba("sf::st_read",      nrow(nc))
  prueba("sf::st_transform", as.integer(st_crs(st_transform(nc, 3857))$epsg))
  prueba("sf::st_area",      round(as.numeric(sum(st_area(st_transform(nc, 32617)))) / 1e9, 1))

  # --- 2. spdep: vecindad y Moran ------------------------------------
  nb <- poly2nb(nc, queen = TRUE)
  lw <- nb2listw(nb, style = "W")
  prueba("spdep::poly2nb",   length(nb))
  prueba("spdep::card",      round(mean(card(nb)), 4))
  mi <- moran.test(nc$SID74, lw)
  prueba("spdep::moran.test", round(unname(mi$estimate[1]), 6))
  lm_ <- localmoran_perm(nc$SID74, lw, nsim = 199)
  prueba("spdep::localmoran_perm", nrow(lm_))

  # --- 3. spatialreg: SAR y sus efectos ------------------------------
  m <- errorsarlm(SID74 ~ BIR74, data = nc, listw = lw, quiet = TRUE)
  prueba("spatialreg::errorsarlm", round(unname(m$lambda), 6))
  ml <- lagsarlm(SID74 ~ BIR74, data = nc, listw = lw, quiet = TRUE)
  prueba("spatialreg::lagsarlm",   round(unname(ml$rho), 6))
  prueba("spatialreg::impacts",
         round(impacts(ml, listw = lw)$direct[1], 6))

  # --- 4. gstat: variograma y kriging --------------------------------
  data(meuse, package = "sp")
  coordinates(meuse) <- ~x + y
  vg  <- variogram(log(zinc) ~ 1, meuse)
  fit <- fit.variogram(vg, vgm(1, "Sph", 900, 1))
  prueba("gstat::variogram",     nrow(vg))
  prueba("gstat::fit.variogram", round(fit$range[2], 3))

  # --- 5. spatstat: patrones puntuales -------------------------------
  data(japanesepines, package = "spatstat.data")
  k <- spatstat.explore::Kest(japanesepines)
  prueba("spatstat::Kest",       length(k$r))
  q <- spatstat.explore::quadrat.test(japanesepines, 3, 3)
  prueba("spatstat::quadrat.test", round(unname(q$statistic), 6))
  bw <- spatstat.explore::bw.diggle(japanesepines)
  prueba("spatstat::bw.diggle",  round(as.numeric(bw), 6))
  ppmod <- spatstat.model::ppm(japanesepines ~ x + y)
  prueba("spatstat::ppm",        round(unname(coef(ppmod)[1]), 6))

  # --- 6. classInt: cortes de clase (cap. 3) -------------------------
  ci <- classIntervals(nc$SID74, n = 5, style = "fisher")
  prueba("classInt::fisher",     round(ci$brks, 3))
  prueba("classInt::quantile",   round(classIntervals(nc$SID74, 5, style = "quantile")$brks, 3))

  # --- 7. GWmodel: regresión geográficamente ponderada ---------------
  ncsp <- as(st_transform(nc, 32617), "Spatial")
  bwg  <- GWmodel::bw.gwr(SID74 ~ BIR74, data = ncsp, approach = "AICc",
                          kernel = "bisquare", adaptive = TRUE)
  prueba("GWmodel::bw.gwr",      bwg)
  g <- GWmodel::gwr.basic(SID74 ~ BIR74, data = ncsp, bw = bwg,
                          kernel = "bisquare", adaptive = TRUE)
  prueba("GWmodel::gwr.basic",   round(mean(g$SDF$BIR74), 8))

  # --- 8. blockCV: validación cruzada espacial (cap. 10) -------------
  set.seed(SEMILLA)
  pts <- st_transform(st_centroid(nc), 32617)
  bcv <- blockCV::cv_spatial(x = pts, k = 5, size = 150000,
                             selection = "random", iteration = 10,
                             progress = FALSE, report = FALSE, plot = FALSE)
  prueba("blockCV::cv_spatial",  length(bcv$folds_list))

  # --- 9. stars / terra / rmapshaper ---------------------------------
  prueba("stars::st_as_stars",   dim(stars::st_as_stars(matrix(1:12, 3, 4)))[["X1"]])
  prueba("terra::rast",          terra::ncell(terra::rast(nrows = 4, ncols = 5)))
  simp <- rmapshaper::ms_simplify(nc, keep = 0.05, keep_shapes = TRUE)
  prueba("rmapshaper::ms_simplify", nrow(simp))

  # --- 10. datos que el plan promete ---------------------------------
  # getisord NO es un sf: es la rejilla 16x16 del artículo original de
  # Getis & Ord (1992), en go_xyz (256 celdas) más go_x y go_y.
  prueba("spData::getisord",  { data(getisord, package = "spData"); nrow(get("go_xyz")) })
  prueba("spData::auckland",  { data(auckland, package = "spData"); nrow(get("auckland")) })
  prueba("spdep::oldcol",     { data(oldcol, package = "spdep"); nrow(get("COL.OLD")) })
  prueba("HistData::Snow",    { data(Snow.deaths, package = "HistData"); nrow(get("Snow.deaths")) })
  prueba("gstat::jura",       { data(jura, package = "gstat"); nrow(get("jura.pred")) })

  # --- informe -------------------------------------------------------
  ok <- vapply(resultados, `[[`, logical(1), "ok")
  cat(sprintf("\n=== %d de %d comprobaciones OK ===\n", sum(ok), length(ok)))
  if (any(!ok)) {
    cat("FALLAN:", paste(names(ok)[!ok], collapse = ", "), "\n")
  }

  # La guarda de procedencia puede parar aquí, y no debe llevarse por
  # delante el informe: lo que esta prueba mide es si el entorno CALCULA,
  # y eso ya está medido tres líneas más arriba. Que el acta no se toque
  # es una noticia, no un fallo del entorno.
  cat(tryCatch({ registra_versiones(); "versiones.json escrito." },
               error = function(e) paste0("versiones.json NO se tocó.\n",
                                          conditionMessage(e))), "\n")
  if (any(!ok)) quit(status = 1L)
}
