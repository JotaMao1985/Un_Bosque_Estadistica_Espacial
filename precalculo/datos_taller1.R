# =====================================================================
# datos_taller1.R — el dato del Taller 1, alcanzable desde fuera
#
#   Estadística Espacial 2026-II (20929) · corte I
#   Ver PLAN_Datos_Taller_1.md (el relevo) y PLAN_Taller_1_Caps_1_2.md.
#
# PARA QUÉ EXISTE
#
# T2, T4 y T5 —el 45 % del escrito— mandan ejecutar código sobre
# `datos/procesado/*.gpkg`. Son 86 MB —dentro de los 431 de `datos/`—,
# están en `.gitignore` a propósito y NO viajan a GitHub Pages:
# comprobado, 404. O sea que el taller pedía correr código sobre un
# archivo que solo existe en el equipo donde se construyó, y eso no lo
# mide ningún auditor que compare números contra números: las cifras
# publicadas eran correctas.
#
# Esto extrae de `datos/procesado/` los TRES archivos que el estudiante
# necesita y los deja en `entrega/datos/`, que sí se publica:
#
#   taller1_estaciones.gpkg     las 361 del IDEAM          ~152 KB
#   taller1_municipios.gpkg     SOLO los 60 asignados      ~5,5 MB
#   taller1_departamentos.gpkg  los 33                     ~5,2 MB
#
# Se hace en R y con guion versionado, y no a mano en una consola,
# porque en este proyecto el dato publicado tiene que poder
# reconstruirse. Es la misma disciplina de los `datos_*.R` de al lado.
#
# LA RESTRICCIÓN QUE MANDA SOBRE TODO LO DEMÁS
#
# **No se puede simplificar la geometría para achicar los archivos.** T4
# mide áreas, y —más grave— el punto interior de un polígono simplificado
# desplaza cuáles son las 40 estaciones más próximas: cambiaría el DÍGITO
# DE VERIFICACIÓN de las 60 variantes y rompería un taller ya repartido.
# Aquí se FILTRAN filas y no se toca un solo vértice; la guarda 5 lo
# comprueba rehaciendo los 60 dígitos desde los archivos ya escritos.
#
# LO QUE ESTE GUION **NO** HACE
#
#   · NO ejecuta `genera_taller1.R` ni lo necesita. Reejecutarlo
#     reasignaría las 1000 variantes y dejaría sin sentido lo repartido
#     (§9 del plan del taller).
#   · NO toca ningún JSON de `salidas/`. Los LEE, para saber qué 60
#     municipios hay que publicar y contra qué comprobar.
#   · NO reproyecta: las tres capas ya están en EPSG:9377 y reproyectar
#     movería las coordenadas.
#
# Y UNA COSA QUE NO SE REPRODUCE, PARA QUE NO ASUSTE
#
# Reejecutar esto NO da los mismos bytes. El GeoPackage guarda un
# `last_change` en su tabla `gpkg_contents`, así que dos pasadas seguidas
# dejan tres archivos con MD5 distinto y una geometría idéntica —los 60
# dígitos de verificación se rehacen abajo y lo prueban—. Eso significa
# que reejecutarlo por costumbre antes de un commit mete 10,4 MB de diff
# que no cambian nada: NO se reejecuta salvo que cambie la fuente o el
# catálogo del JSON.
#
# LICENCIAS — esto redistribuye un derivado, así que la atribución viaja
# con él (README, y el módulo 1 del taller junto a los enlaces):
#   · estaciones: IDEAM, normales climatológicas 1991-2020, CC BY-SA 4.0
#   · municipios y departamentos: DANE (MGN) vía geoBoundaries, CC BY 4.0
#
# Correr desde la carpeta del curso:
#   precalculo/rscript.sh precalculo/datos_taller1.R
# =====================================================================

# La guarda de codificación va PRIMERO: los nombres de municipio llevan
# tilde y aquí se comparan contra el JSON publicado. Ver precalculo/utf8.R.
source("precalculo/utf8.R")
source("precalculo/entorno.R")
suppressPackageStartupMessages({
  library(sf); library(jsonlite)
})

PROC    <- "datos/procesado"
SALIDAS <- "precalculo/salidas"
DESTINO <- "entrega/datos"

N_ESTACIONES <- 40L
CRS_TRABAJO  <- 9377L

dir.create(DESTINO, recursive = TRUE, showWarnings = FALSE)

# ---------------------------------------------------------------------
# ancla() — la comprobación que PARA
#
# Misma disciplina que en el resto del precálculo. Aquí para más que en
# otros sitios: publicar una geometría que no sea la que construyó el
# JSON le cambia las cifras a 60 variantes ya repartidas, y el estudiante
# no tendría cómo saberlo. Si algo no cuadra, esto se detiene y no
# escribe nada.
# ---------------------------------------------------------------------
N_ANCLAS <- 0L
ancla <- function(condicion, que) {
  N_ANCLAS <<- N_ANCLAS + 1L
  if (!isTRUE(condicion)) stop(sprintf("ANCLA ROTA · %s", que), call. = FALSE)
  invisible(TRUE)
}

# =====================================================================
# 1. Lo publicado manda: el JSON dice qué 60 municipios son
# =====================================================================
message("1. lo publicado")

D <- fromJSON(file.path(SALIDAS, "taller1_datos.json"), simplifyVector = TRUE)
llaves <- D$municipios$llave

ancla(length(llaves) == D$meta$n_municipios,
      sprintf("el JSON trae %d municipios y declara %d",
              length(llaves), D$meta$n_municipios))
ancla(!anyDuplicated(llaves), "hay llaves repetidas en el catálogo del JSON")
message(sprintf("   %d llaves, %d departamentos, %d estaciones declaradas",
                length(llaves), length(unique(D$municipios$departamento)),
                D$t7$n_estaciones))

# =====================================================================
# 2. Las fuentes
# =====================================================================
message("2. fuentes en datos/procesado")

est <- st_read(file.path(PROC, "colombia_estaciones_clima.gpkg"), quiet = TRUE)
mun <- st_read(file.path(PROC, "colombia_adm2.gpkg"),             quiet = TRUE)
dep <- st_read(file.path(PROC, "colombia_adm1.gpkg"),             quiet = TRUE)

for (par in list(list(est, "estaciones"), list(mun, "municipios"), list(dep, "departamentos")))
  ancla(st_crs(par[[1]])$epsg == CRS_TRABAJO,
        sprintf("%s no llegan en EPSG:%d", par[[2]], CRS_TRABAJO))

# GUARDA 1 · ninguna llave del JSON puede faltar en la MGN. Si geoBoundaries
# cambiara de commit, los shapeID se mueven y esto lo canta ANTES de
# publicar un archivo en el que el estudiante no encontraría su municipio.
faltan <- setdiff(llaves, mun$shapeID)
ancla(length(faltan) == 0,
      sprintf("%d llave(s) del JSON no están en la MGN: %s",
              length(faltan), paste(utils::head(faltan, 3), collapse = ", ")))

# GUARDA 2 · los departamentos del JSON tienen que existir con ESE nombre
# en ADM1. Es lo que hace comparable la tira de variante del estudiante
# con lo que le devuelve el join de T5(c).
sin_dep <- setdiff(unique(D$municipios$departamento), dep$shapeName)
ancla(length(sin_dep) == 0,
      sprintf("%d departamento(s) del JSON no están en ADM1: %s",
              length(sin_dep), paste(sin_dep, collapse = ", ")))

# =====================================================================
# 3. El filtrado — filas, no vértices
# =====================================================================
message("3. filtrando")

mun_t1 <- mun[match(llaves, mun$shapeID), ]   # en el ORDEN del JSON, no en el de la MGN

# GUARDA 3 · los conteos, que son la otra mitad de la decisión de §2 del
# relevo: 361 estaciones, 60 municipios, 33 departamentos.
ancla(nrow(est)    == D$t7$n_estaciones,
      sprintf("estaciones: %d, se esperaban %d", nrow(est), D$t7$n_estaciones))
ancla(nrow(mun_t1) == D$meta$n_municipios,
      sprintf("municipios filtrados: %d, se esperaban %d", nrow(mun_t1), D$meta$n_municipios))
ancla(nrow(dep)    == 33L,
      sprintf("departamentos: %d, se esperaban 33", nrow(dep)))

# GUARDA 4 · ni un vértice de menos. `st_write` no simplifica, pero esto
# lo deja comprobado en vez de supuesto: es LA restricción de este guion.
vert_antes <- sum(mapply(function(k) nrow(st_coordinates(mun[mun$shapeID == k, ])), llaves))

# =====================================================================
# 4. La escritura
# =====================================================================
message("4. escribiendo en ", DESTINO)

escribe <- function(x, nombre) {
  f <- file.path(DESTINO, paste0(nombre, ".gpkg"))
  st_write(x, f, layer = nombre, delete_dsn = TRUE, quiet = TRUE)
  message(sprintf("   %-28s %5.1f MB · %d rasgos",
                  basename(f), file.size(f) / 1024^2, nrow(x)))
  f
}

f_est <- escribe(est,    "taller1_estaciones")
f_mun <- escribe(mun_t1, "taller1_municipios")
f_dep <- escribe(dep,    "taller1_departamentos")

# =====================================================================
# 5. La comprobación que decide si esto salió bien
#
# Se releen los archivos ESCRITOS —no los de memoria— y se rehacen los 60
# dígitos de verificación con la misma regla que ejecuta el estudiante:
# las 40 estaciones más próximas al punto interior del municipio, medidas
# en 9377, y la suma de sus altitudes. Si uno solo no cuadra con el JSON
# publicado, la geometría que se iba a publicar no es la que construyó el
# taller.
# =====================================================================
message("5. rehaciendo los 60 dígitos desde lo escrito")

est_p <- st_read(f_est, quiet = TRUE)
mun_p <- st_read(f_mun, quiet = TRUE)
dep_p <- st_read(f_dep, quiet = TRUE)

ancla(st_crs(est_p)$epsg == CRS_TRABAJO && st_crs(mun_p)$epsg == CRS_TRABAJO &&
      st_crs(dep_p)$epsg == CRS_TRABAJO,
      "algo se escribió sin EPSG:9377")
ancla(nrow(est_p) == 361L && nrow(mun_p) == 60L && nrow(dep_p) == 33L,
      sprintf("releído: %d/%d/%d, se esperaba 361/60/33",
              nrow(est_p), nrow(mun_p), nrow(dep_p)))
ancla(all(c("altitud_m", "t_media_anual") %in% names(est_p)),
      "las estaciones publicadas no llevan altitud_m y t_media_anual")
ancla("shapeID" %in% names(mun_p) && "shapeName" %in% names(dep_p),
      "falta shapeID en los municipios o shapeName en los departamentos")

vert_despues <- nrow(st_coordinates(mun_p))
ancla(vert_despues == vert_antes,
      sprintf("la geometría perdió vértices: %d publicados contra %d de origen",
              vert_despues, vert_antes))

xy_est <- st_coordinates(st_geometry(est_p))
xy_mun <- st_coordinates(st_point_on_surface(st_geometry(mun_p)))

digitos <- vapply(seq_len(nrow(mun_p)), function(i) {
  d <- sqrt((xy_est[, 1] - xy_mun[i, 1])^2 + (xy_est[, 2] - xy_mun[i, 2])^2)
  sum(est_p$altitud_m[order(d)[seq_len(N_ESTACIONES)]])
}, numeric(1))

esperados <- D$municipios$suma_altitud[match(mun_p$shapeID, llaves)]
malos <- which(digitos != esperados)
ancla(length(malos) == 0,
      sprintf("%d dígito(s) de verificación cambiaron: %s",
              length(malos),
              paste(sprintf("%s %d != %d", mun_p$shapeName[malos],
                            digitos[malos], esperados[malos]), collapse = " · ")))

# El otro contraste que el estudiante hará, y que conviene saber antes
# que él: cuántas estaciones se quedan fuera de todo departamento incluso
# BIEN declaradas. No es un fallo —hay estaciones sobre la línea de costa
# o justo en un límite digitalizado—, pero es la respuesta correcta de
# T5(c) para quien la mida, y calificarla como cero sería corregirle una
# respuesta buena.
fuera <- sum(lengths(st_intersects(est_p, dep_p)) == 0)

# =====================================================================
# Informe
# =====================================================================
cat("\n")
cat(strrep("-", 70), "\n", sep = "")
cat(sprintf("  %d estaciones · %d municipios · %d departamentos, todos en EPSG:%d\n",
            nrow(est_p), nrow(mun_p), nrow(dep_p), CRS_TRABAJO))
cat(sprintf("  %s vértices de municipio, los mismos que en la MGN\n",
            formatC(vert_despues, format = "d", big.mark = " ")))
cat(sprintf("  los 60 dígitos de verificación rehechos desde lo publicado: intactos\n"))
cat(sprintf("  %d de las %d estaciones caen fuera de todo departamento aun bien declaradas\n",
            fuera, nrow(est_p)))
cat(sprintf("  %.1f MB en total en %s/\n",
            sum(file.size(c(f_est, f_mun, f_dep))) / 1024^2, DESTINO))
cat(sprintf("  %d anclas, todas en pie\n", N_ANCLAS))
cat(strrep("-", 70), "\n", sep = "")
cat("  Recordatorios:\n")
cat("  · `*.gpkg` está ignorado por extensión; sin la excepción estrecha del\n")
cat("    .gitignore estos tres archivos no viajan a Pages.\n")
cat("  · el GeoPackage estampa la hora en `gpkg_contents`, así que estos bytes\n")
cat("    NO son los de la pasada anterior aunque la geometría sí lo sea.\n")
