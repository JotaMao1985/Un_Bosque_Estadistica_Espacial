# =====================================================================
# genera_preparcial1.R — el precálculo del preparcial del Corte I (P1.1)
#
#   Estadística Espacial 2026-II (20929) · parcial del 1 de septiembre
#   Capítulos 1 y 2 completos + capítulo 3 hasta el módulo 8.
#
# QUÉ PRODUCE
#   precalculo/salidas/preparcial1_datos.json
#
# LAS DOS REGLAS QUE MANDAN AQUÍ
#
# 1. La de siempre (D10): ninguna cifra del preparcial se escribe a mano.
#
# 2. Una propia, y es la razón de que este archivo exista en vez de copiar
#    cifras: **una cifra reutilizada no se copia, se REFERENCIA**. El
#    preparcial cita cosas que ya calcularon genera_cap1.R, genera_cap2.R y
#    genera_cap3.R. Si aquí se copiaran los números, el día que un capítulo
#    se regenere y una cifra cambie, la pregunta del preparcial quedaría
#    mintiendo con su propio JSON perfectamente coherente: nada podría
#    verlo. Por eso cada entrada de `reutilizado` guarda de dónde viene
#    —archivo y ruta— además del valor, y `audita_preparcial1.py` vuelve a
#    resolver esa ruta contra el capítulo en el momento de auditar.
#
#    Es la única familia de comprobación que ni los capítulos ni el taller
#    tienen, porque son los únicos documentos del sitio que no dependen de
#    las cifras de otro.
#
# LO QUE ESTE ARCHIVO SE NIEGA A PROPAGAR
#
# Los capítulos 2 y 3 publican hoy nombres de lugar con la codificación
# rota —«Bogot<U+00E1>, D.C.», «Guain<U+00ED>a»—: entra en los CSV del
# precálculo y llega al HTML. Está reportado aparte y se arregla en su
# sitio, no aquí. Lo que sí se hace aquí es **rechazar** cualquier cadena
# reutilizada que traiga esa marca, para que el defecto no se multiplique
# por un documento nuevo mientras se corrige en los viejos.
#
# LOS DISTRACTORES SE CALCULAN, NO SE INVENTAN
#
# Cada opción incorrecta de las preguntas numéricas es el resultado de un
# error CONCRETO Y NOMBRADO: meter en la fórmula del tamaño efectivo el
# Moran de la primera banda en vez del rho medio, dejar que s2 mida sobre
# la esfera creyendo que mide sobre el elipsoide, olvidar el coseno de la
# latitud, clasificar con el intervalo cerrado por el otro lado. Así la
# retroalimentación puede decir «llegaste a 3,5 porque usaste la
# correlación de los vecinos inmediatos como si fuera la media» en vez de
# «incorrecto». Es más caro de construir y es lo único que enseña.
#
# Y un error nombrado no basta: el distractor tiene que SEPARARSE de la
# respuesta. Dos candidatos se cayeron por eso —el (n-1) contra el n, que
# con n = 1121 difieren en centésimas, y el arco de paralelo contra la
# geodésica, nueve milímetros en ciento once kilómetros—. Los dos nombran
# un error real y ninguno lo evalúa: preguntan por el redondeo. Se quedan
# como cifras de la prosa, en `nota_n_menos_1` y `nota_arco`, que es donde
# sí enseñan. La guarda de más abajo lo comprueba y no lo deja a criterio.
#
# Ejecutar SIEMPRE con el envoltorio:
#     precalculo/rscript.sh precalculo/genera_preparcial1.R
# =====================================================================

source("precalculo/utf8.R")

suppressPackageStartupMessages({
  library(jsonlite)
  library(sf)
})

SALIDAS <- "precalculo/salidas"
SEMILLA <- 2026
set.seed(SEMILLA)

FECHA_PARCIAL <- "2026-09-01"

para <- function(...) stop("PARADO · genera_preparcial1: ", ..., call. = FALSE)

CAPS <- list(
  cap1 = fromJSON(file.path(SALIDAS, "cap1_datos.json"), simplifyVector = FALSE),
  cap2 = fromJSON(file.path(SALIDAS, "cap2_datos.json"), simplifyVector = FALSE),
  cap3 = fromJSON(file.path(SALIDAS, "cap3_datos.json"), simplifyVector = FALSE)
)
ARCHIVO <- c(cap1 = "cap1_datos.json", cap2 = "cap2_datos.json",
             cap3 = "cap3_datos.json")

# ---------------------------------------------------------------------
# El resolutor de rutas. `tobler.ideam.bandas[1].I` y poco más: nombres
# separados por punto e índices de lista entre corchetes, en base 1 como
# todo lo demás en R.
# ---------------------------------------------------------------------
en_ruta <- function(obj, ruta) {
  cur <- obj
  for (p in strsplit(ruta, ".", fixed = TRUE)[[1]]) {
    m <- regmatches(p, regexec("^([^\\[]*)(\\[([0-9]+)\\])?$", p))[[1]]
    if (!length(m)) return(NULL)
    nombre <- m[2]; idx <- m[4]
    if (nzchar(nombre)) {
      if (is.null(cur) || !nombre %in% names(cur)) return(NULL)
      cur <- cur[[nombre]]
    }
    if (nzchar(idx)) {
      i <- as.integer(idx)
      if (is.null(cur) || length(cur) < i) return(NULL)
      cur <- cur[[i]]
    }
  }
  cur
}

# ---------------------------------------------------------------------
# La tabla de lo reutilizado. Una fila por cifra: de qué módulo del
# temario habla, dónde vive y qué dice. La columna `que` no es adorno:
# es lo que el redactor de la pregunta lee para no tener que volver al
# capítulo, y lo que el auditor imprime cuando algo se desincroniza.
# ---------------------------------------------------------------------
r <- function(clave, doc, modulo, ruta, que, vector = FALSE)
  list(clave = clave, doc = doc, modulo = modulo, ruta = ruta,
       que = que, vector = vector)

REUSA <- list(
  # ---- capítulo 1 -------------------------------------------------
  r("snow_muertes",        "cap1",  1, "snow.n_muertes",                  "Muertes del brote de Broad Street, 1854"),
  r("snow_pct_broad",      "cap1",  1, "snow.pct_mas_cerca_broad",        "Porcentaje de muertes cuya bomba más cercana es la de Broad Street"),
  r("snow_razon_uniforme", "cap1",  1, "snow.razon_sobre_uniforme",       "Veces por encima de lo esperado si las 13 bombas fueran equivalentes"),
  r("snow_caida_mango",    "cap1",  1, "snow.caida_hasta_mango_pct",      "Porcentaje de caída de los ataques antes de quitar la manija de la bomba"),

  r("ce_redwood",          "cap1",  2, "puntual_canonico.redwood.clark_evans",       "Clark-Evans de las secuoyas (agregado, <1)"),
  r("ce_pinos",            "cap1",  2, "puntual_canonico.japanesepines.clark_evans", "Clark-Evans de los pinos japoneses: cerca de 1, compatible con aleatoriedad"),
  r("ce_celulas",          "cap1",  2, "puntual_canonico.cells.clark_evans",         "Clark-Evans de las células (regular, >1)"),
  r("nc_tasa_global",      "cap1",  2, "area_canonico.tasa_global",        "Tasa global de SIDS en Carolina del Norte, por mil"),
  r("meuse_corr_rio",      "cap1",  2, "geo_canonico.corr_dist_rio",       "Correlación entre log-zinc y distancia al río (meuse)"),

  r("tobler_ideam_b1",     "cap1",  3, "tobler.ideam.bandas[1].I",         "Moran I de la primera banda de distancia, estaciones del IDEAM"),
  r("tobler_perm_b1",      "cap1",  3, "tobler.permutado.bandas[1].I",     "Moran I de la primera banda tras permutar las estaciones al azar"),
  r("tobler_esperado",     "cap1",  3, "tobler.ideam.esperado",            "E[I] bajo independencia, -1/(n-1)"),
  r("tobler_caida_alt",    "cap1",  3, "tobler.caida_por_altitud_pct",     "Porcentaje en que cae la autocorrelación al descontar la altitud"),

  r("inf_cobertura_ind",   "cap1",  4, "inferencia.cobertura_independiente", "Cobertura real del IC al 95 % con datos independientes"),
  r("inf_cobertura_phi4",  "cap1",  4, "inferencia.cobertura_phi4",        "Cobertura real de un IC nominal al 95 % bajo dependencia (phi = 4)"),
  r("inf_factor_phi4",     "cap1",  4, "inferencia.factor_phi4",           "Veces que se subestima el error estándar ingenuo"),
  r("inf_inflacion",       "cap1",  4, "inferencia.inflacion_varianza_phi4", "Porcentaje en que la varianza real supera a la ingenua"),
  r("inf_real_factor",     "cap1",  4, "inferencia_real.factor",           "Veces que se subestima el error estándar sobre el dato real: bootstrap por bloques contra iid"),
  r("inf_cobertura_phi16", "cap1",  4, "inferencia.rejilla[7].cobertura",  "Cobertura real del IC al 95 % en el extremo derecho de la curva (phi = 16)"),

  r("neff_desercion",      "cap1",  5, "n_efectivo.desercion_municipal",   "Tamaño efectivo de los 1121 municipios con deserción"),
  r("neff_desercion_n",    "cap1",  5, "n_efectivo.desercion_n",           "Municipios con dato de deserción"),
  r("neff_pct",            "cap1",  5, "n_efectivo.desercion_pct",         "Porcentaje de la información nominal que queda tras la autocorrelación"),
  r("neff_rho_implicito",  "cap1",  5, "n_efectivo.rho_del_titular.implicito", "rho implícito en ese n efectivo"),
  r("neff_I_primera_banda","cap1",  5, "n_efectivo.rho_del_titular.I_primera_banda", "Moran I de la primera banda: la correlación de los vecinos inmediatos, que NO es el rho medio"),

  r("realiz_rechaza",      "cap1",  6, "una_realizacion.pct_rechaza_ingenuo", "Porcentaje de veces que la prueba ingenua rechaza siendo cierta H0"),
  r("realiz_esperado",     "cap1",  6, "una_realizacion.pct_esperado_si_valiera", "Porcentaje que debería rechazar si la prueba fuera válida"),
  r("realiz_sd_medias",    "cap1",  6, "una_realizacion.sd_de_las_medias", "Desviación de la media entre 1000 realizaciones del mismo proceso"),
  r("realiz_n",            "cap1",  6, "una_realizacion.n_realizaciones",  "Realizaciones simuladas del proceso"),
  r("realiz_emc",          "cap1",  6, "una_realizacion.emc_rechaza",      "Error de Monte Carlo del porcentaje de rechazo, en puntos porcentuales"),

  r("escala_moran_mun",    "cap1",  7, "escala.moran_municipal",           "Moran I de la deserción a nivel municipal"),
  r("escala_moran_dep",    "cap1",  7, "escala.moran_departamental",       "Moran I de la misma variable agregada a departamento"),
  r("escala_caida",        "cap1",  7, "escala.caida_pct",                 "Porcentaje en que cae el Moran I al agregar"),
  r("escala_n_dep",        "cap1",  7, "escala.n_departamental",           "Unidades del nivel departamental: el n con el que se calcula el Moran agregado"),
  r("soporte_inflacion",   "cap1",  7, "agregacion_soporte.nc.inflacion_pct", "Porcentaje en que se infla el total al repartir por rectángulos sin ponderar por área"),

  r("eco_gdal",            "cap1",  8, "ecosistema.sistema.GDAL",          "Versión de GDAL bajo sf"),
  r("eco_geos",            "cap1",  8, "ecosistema.sistema.GEOS",          "Versión de GEOS bajo sf"),
  r("eco_proj",            "cap1",  8, "ecosistema.sistema.PROJ",          "Versión de PROJ bajo sf"),

  r("anat_pct_geom",       "cap1",  9, "anatomia.nc.pct_geometria",        "Porcentaje de los bytes de un objeto sf que ocupa la geometría"),
  r("anat_filas",          "cap1",  9, "anatomia.nc.filas",                "Condados de nc: las filas del objeto sf"),
  r("anat_vertices",       "cap1",  9, "anatomia.nc.n_vertices",           "Vértices de los 100 condados de nc"),
  r("anat_multiples",      "cap1",  9, "anatomia.nc.n_partes_multiples",   "Condados con más de una parte (MULTIPOLYGON de verdad)"),
  r("anat_ppp_n",          "cap1",  9, "anatomia.ppp.n",                   "Puntos del ppp de los pinos japoneses"),

  r("cv_rmse_alea",        "cap1", 10, "cv_espacial.rmse_aleatoria",       "RMSE con validación cruzada aleatoria"),
  r("cv_rmse_bloques",     "cap1", 10, "cv_espacial.rmse_bloques",         "RMSE con validación cruzada por bloques espaciales"),
  r("cv_inflacion",        "cap1", 10, "cv_espacial.inflacion_pct",        "Porcentaje en que el error por bloques supera al que anuncia la validación aleatoria"),
  r("cv_r2_bloques",       "cap1", 10, "cv_espacial.r2_bloques",           "R2 por bloques: negativo, peor que predecir la media"),

  r("glos_n_filas",        "cap1", 11, "glosario.filas",                   "Entradas del glosario de notación del curso", vector = TRUE),

  # ---- capítulo 2 -------------------------------------------------
  r("elip_a",              "cap2",  1, "elipsoide.a",                      "Semieje mayor del WGS84, en metros"),
  r("elip_a_menos_b",      "cap2",  1, "elipsoide.a_menos_b",              "Diferencia entre semiejes: cuánto se aparta la Tierra de una esfera"),
  r("elip_f_inv",          "cap2",  1, "elipsoide.aplanamiento_inv",       "Aplanamiento inverso del WGS84"),
  r("elip_datum_desp",     "cap2",  1, "elipsoide.datum.desp_medio_m",     "Desplazamiento medio al cambiar de datum (WGS84 a Bogotá 1975)"),

  r("grad_lat",            "cap2",  2, "grados.lat",                       "Latitudes tabuladas", vector = TRUE),
  r("grad_lon_elip",       "cap2",  2, "grados.lon_m_elipsoide",           "Metros de un grado de longitud sobre el elipsoide", vector = TRUE),
  r("grad_lon_esfera",     "cap2",  2, "grados.lon_m_esfera",              "Metros de un grado de longitud sobre la esfera de s2", vector = TRUE),
  r("grad_bogota_oslo",    "cap2",  2, "grados.bogota_vs_oslo",            "Veces que un grado de longitud es más largo en Bogotá que en Oslo"),

  r("proy_omega_med",      "cap2",  3, "proyecciones.tabla.omega_med_grados", "Distorsión angular media por proyección", vector = TRUE),
  r("proy_razon_max",      "cap2",  3, "proyecciones.tabla.razon_max",      "Razón de área máxima por proyección", vector = TRUE),
  r("proy_nombres",        "cap2",  3, "proyecciones.tabla.nombre",         "Las seis proyecciones comparadas", vector = TRUE),
  r("proy_ninguna",        "cap2",  3, "proyecciones.ninguna_conforme_y_equivalente", "Ninguna proyección es conforme y equivalente a la vez"),

  r("epsg_3116_max",       "cap2",  4, "epsg.continente.max_3116_pct",     "Error de área máximo con EPSG:3116 en el continente, en %"),
  r("epsg_9377_max",       "cap2",  4, "epsg.continente.max_9377_pct",     "Error de área máximo con EPSG:9377 en el continente, en %"),
  r("epsg_3116_med",       "cap2",  4, "epsg.continente.med_3116_pct",     "Error de área mediano con EPSG:3116"),
  r("epsg_9377_med",       "cap2",  4, "epsg.continente.med_9377_pct",     "Error de área mediano con EPSG:9377"),

  r("etiq_transform",      "cap2",  5, "etiquetar.transform_max_delta",    "Desplazamiento máximo de los vértices al reproyectar de verdad, con st_transform"),
  r("etiq_set_crs",        "cap2",  5, "etiquetar.set_crs_max_delta",      "Desplazamiento de los vértices al reetiquetar con st_set_crs"),
  r("etiq_lon_absurda",    "cap2",  5, "etiquetar.lon_absurda",            "Longitud que queda tras reetiquetar mal: ninguna Tierra tiene esa coordenada"),
  r("etiq_silencioso",     "cap2",  5, "etiquetar.silencioso.desplazamiento_m", "Desplazamiento de un st_transform 4686->4326: cero, y tampoco avisa"),
  r("etiq_n_localidades",  "cap2",  5, "etiquetar.n_localidades",          "Localidades de Bogotá sobre las que se hace el ensayo de reetiquetado"),

  r("medir_dif_esfera",    "cap2",  6, "medir.colombia.dif_esfera_km2",    "km2 de diferencia al medir Colombia sobre esfera o elipsoide"),
  r("medir_dif_esfera_pct","cap2",  6, "medir.colombia.dif_esfera_pct",    "Diferencia relativa al medir el área de Colombia sobre la esfera en vez del elipsoide"),
  r("medir_dist_max",      "cap2",  6, "medir.distancias.dif_max_m",       "Diferencia máxima entre distancia esférica y geodésica, en metros"),
  r("medir_equiv_mun",     "cap2",  6, "medir.municipios.equivalente_a_municipios", "A cuántos municipios equivale el error acumulado"),

  r("form_campos_largos",  "cap2",  7, "formatos.shapefile.n_campos_largos", "Campos cuyo nombre trunca el shapefile a 10 caracteres"),
  r("form_n_rasgos",       "cap2",  7, "formatos.n_rasgos",                "Rasgos guardados en los tres formatos: NO son las localidades de m5"),
  r("form_n_campos",       "cap2",  7, "formatos.shapefile.n_campos",      "Columnas del conjunto que se guarda en los tres formatos"),
  r("form_gpkg_razon",     "cap2",  7, "formatos.gpkg.razon_sobre_shp",    "Tamaño del GeoPackage respecto del shapefile"),
  r("form_geojson_razon",  "cap2",  7, "formatos.geojson.razon_sobre_shp", "Tamaño del GeoJSON respecto del shapefile"),
  r("form_logico",         "cap2",  7, "formatos.shapefile.tipo_logico_despues", "En qué se convierte un logical al pasar por shapefile"),

  r("csv_desplaz_med",     "cap2",  8, "csv_sf.desplazamiento_km_med",     "Distancia a la que aterriza un punto con lon y lat invertidos"),
  r("csv_en_colombia",     "cap2",  8, "csv_sf.n_en_colombia",             "Estaciones que caen en Colombia con las coordenadas invertidas"),
  r("csv_hubo_aviso",      "cap2",  8, "csv_sf.hubo_aviso",                "¿Avisó sf del error?"),
  r("csv_coma_na",         "cap2",  8, "csv_sf.coma_decimal.n_na",         "NA que produce la coma decimal al leerse como texto"),

  r("pos_razon_max_min",   "cap2",  9, "posicional.sesgo.razon_max_min",   "Veces que la tasa de error posicional es peor en la localidad peor que en la mejor"),
  r("pos_corr",            "cap2",  9, "posicional.sesgo.corr_pearson",    "Correlación entre compacidad de la localidad y tasa de error"),
  r("pos_tasa_global",     "cap2",  9, "posicional.sesgo.tasa_global_pct", "Tasa global de error de asignación, en %"),
  r("pos_sedes_por_pos",   "cap2",  9, "posicional.sedes_por_posicion_2dec", "Sedes que comparten posición al redondear a 2 decimales"),

  r("topo_area_antes",     "cap2", 10, "topologia.lazo.area_antes",        "Área del polígono con autointersección antes de repararlo"),
  r("topo_area_despues",   "cap2", 10, "topologia.lazo.area_despues",      "Área tras st_make_valid"),
  r("topo_buffer_grados",  "cap2", 10, "topologia.buffer.grados_area_km2", "Área de un buffer de radio 1 000 construido sobre grados, leída como km²"),
  r("topo_buffer_3857",    "cap2", 10, "topologia.buffer.m3857_area_real_km2", "Área real de ese buffer hecho en Web Mercator"),

  r("ing_reduccion",       "cap2", 11, "ingenieria.join.reduccion",        "Veces que el índice espacial reduce los pares a comparar"),
  r("ing_pares_bruta",     "cap2", 11, "ingenieria.join.pares_fuerza_bruta", "Pares por fuerza bruta"),
  r("ing_pares_cajas",     "cap2", 11, "ingenieria.join.pares_tras_cajas", "Pares tras el filtro de cajas"),
  r("ing_vecino_mediana",  "cap2", 11, "ingenieria.geohash.d_vecino_mediana_m", "Distancia mediana al vecino más cercano, en metros"),

  # ---- capítulo 3, hasta el módulo 8 -------------------------------
  r("c3m1_config",         "cap3",  1, "m1.n_configuraciones",             "Configuraciones de esquema y k probadas sobre el mismo dato"),
  r("c3m1_distintos",      "cap3",  1, "m1.n_mapas_distintos",             "Mapas visualmente distintos que salen de ellas"),
  r("c3m1_pct",            "cap3",  1, "m1.pct_distintos",                 "Porcentaje de configuraciones que dan un mapa distinto"),
  r("c3m1_vacias",         "cap3",  1, "m1.n_con_clase_vacia",             "Configuraciones que dejan alguna clase vacía"),

  r("c3m2_r",              "cap3",  2, "m2.r_conteo_tasa",                 "Correlación de Pearson entre el conteo de estudiantes y el puntaje medio"),
  r("c3m2_rho",            "cap3",  2, "m2.rho_conteo_tasa",               "Correlación de Spearman entre los dos ordenamientos"),
  r("c3m2_solape",         "cap3",  2, "m2.solape_top20",                  "Municipios comunes a los 20 primeros por conteo y por puntaje medio"),
  r("c3m2_pct_est",        "cap3",  2, "m2.pct_estudiantes_top10",         "Porcentaje de estudiantes que vive en los 10 municipios con más conteo"),
  r("c3m2_pct_mun",        "cap3",  2, "m2.pct_municipios_top10",          "Porcentaje de municipios que son esos diez"),

  r("c3m3_cortes",         "cap3",  3, "m3.cortes_cuantiles",              "Cortes por cuantiles sobre SID74, k=5", vector = TRUE),
  r("c3m3_empatados",      "cap3",  3, "m3.n_empatados",                   "Condados empatados justo en un corte"),
  r("c3m3_convenio_r",     "cap3",  3, "m3.convenio_r",                    "Lado cerrado del intervalo en classInt"),
  r("c3m3_convenio_py",    "cap3",  3, "m3.convenio_python",               "Lado cerrado del intervalo en mapclassify"),

  r("c3m4_discordante",    "cap3",  4, "m4.par_mas_discordante.pct_cambian", "Porcentaje de municipios que cambian de clase entre los dos esquemas más discordantes"),
  r("c3m4_concordante",    "cap3",  4, "m4.par_mas_concordante.pct_cambian", "Porcentaje de municipios que cambian de clase entre los dos esquemas más concordantes"),
  r("c3m4_estables",       "cap3",  4, "m4.pct_estables",                  "Porcentaje de municipios que no cambian de clase con ningún esquema"),
  r("c3m4_rango_max",      "cap3",  4, "m4.rango_max",                     "Clases distintas que llega a tomar un mismo municipio"),

  r("c3m5_dE_normal",      "cap3",  5, "m5.rojo_verde.dE_normal",          "Distancia perceptual entre el rojo y el verde en visión típica"),
  r("c3m5_dE_deuter",      "cap3",  5, "m5.rojo_verde.dE_deuteranopia",    "Distancia perceptual entre el rojo y el verde bajo deuteranopia"),
  r("c3m5_caida",          "cap3",  5, "m5.rojo_verde.caida_pct",          "Porcentaje en que cae esa distancia perceptual"),
  r("c3m5_comparaciones",  "cap3",  5, "m5.n_comparaciones_cvd",           "Comparaciones de color simuladas"),

  r("c3m6_verbos",         "cap3",  6, "m6.n_verbos",                      "Verbos de tmap verificados ejecutando"),
  r("c3m6_version",        "cap3",  6, "m6.version_tmap",                  "Versión de tmap del material"),

  r("c3m7_por_punto",      "cap3",  7, "m7.dot_density.por_punto",         "Estudiantes que representa cada punto del dot density"),
  r("c3m7_n_puntos",       "cap3",  7, "m7.dot_density.n_puntos",          "Puntos dibujados"),
  r("c3m7_hexagonos",      "cap3",  7, "m7.hexbin.n_hexagonos",            "Hexágonos del hexbin"),
  r("c3m7_razon_simbolos", "cap3",  7, "m7.simbolos.razon_valor",          "Razón entre el valor mayor y el menor en símbolos proporcionales"),

  r("c3m8_r_ind",          "cap3",  8, "m8.r_individuo",                   "Correlación educación de la madre / puntaje, a nivel individual"),
  r("c3m8_r_mun",          "cap3",  8, "m8.r_municipio",                   "Correlación educación de la madre / puntaje, agregada a municipio"),
  r("c3m8_r_dep",          "cap3",  8, "m8.r_departamento",                "Correlación educación de la madre / puntaje, agregada a departamento"),
  r("c3m8_subida",         "cap3",  8, "m8.subida_ind_dep_pct",            "Porcentaje que sube la correlación al pasar del individuo al departamento"),
  r("c3m8_pct_var",        "cap3",  8, "m8.pct_var_entre",                 "Porcentaje de la varianza total que vive entre municipios")
)

# ---------------------------------------------------------------------
# Resolución y guardas. Una cifra que no existe, un vector que se ha
# hecho enorme o una cadena con la codificación rota paran el guion: son
# las tres formas de que este JSON salga plausible y equivocado.
# ---------------------------------------------------------------------
REUTILIZADO <- list()
for (e in REUSA) {
  v <- en_ruta(CAPS[[e$doc]], e$ruta)
  if (is.null(v))
    para("no existe ", e$doc, ":", e$ruta, " (clave ", e$clave, ")")
  if (is.list(v)) {
    if (all(vapply(v, function(x) is.atomic(x) && length(x) == 1, logical(1)))) {
      v <- unlist(v)
    } else if (e$vector) {
      v <- length(v)   # listas de objetos: solo interesa cuántas son
    } else {
      para(e$clave, " (", e$doc, ":", e$ruta, ") no es una cifra ni un vector")
    }
  }
  if (!e$vector && length(v) != 1)
    para(e$clave, " trae ", length(v), " valores y no está declarada como vector")
  if (length(v) > 40)
    para(e$clave, " trae ", length(v), " valores: demasiado para incrustarlo")
  if (is.character(v) && any(grepl("<U\\+", v)))
    para("CODIFICACIÓN ROTA en ", e$doc, ":", e$ruta, " -> ", paste(v, collapse = " | "),
         "\n  El preparcial no propaga tildes rotas. Arréglese en el capítulo.")
  if (is.numeric(v) && any(!is.finite(v)))
    para(e$clave, " tiene valores no finitos")

  REUTILIZADO[[e$clave]] <- list(
    origen = unname(ARCHIVO[e$doc]), ruta = e$ruta,
    doc = e$doc, modulo = e$modulo, que = e$que,
    valor = if (length(v) == 1) unname(v) else unname(v)
  )
}

val <- function(clave) REUTILIZADO[[clave]]$valor

# Cobertura: los 30 módulos del alcance, tocados por al menos una cifra.
cubiertos <- unique(vapply(REUTILIZADO, function(x) paste0(x$doc, ".m", x$modulo), ""))
esperados <- c(paste0("cap1.m", 1:11), paste0("cap2.m", 1:11), paste0("cap3.m", 1:8))
faltan <- setdiff(esperados, cubiertos)
if (length(faltan))
  para("módulos del alcance sin ninguna cifra: ", paste(faltan, collapse = ", "))
if (length(setdiff(cubiertos, esperados)))
  para("cifras de módulos FUERA del alcance: ",
       paste(setdiff(cubiertos, esperados), collapse = ", "))

# ---------------------------------------------------------------------
# N1 · Tamaño de muestra efectivo (cap. 1, módulo 5)
# ---------------------------------------------------------------------
n1  <- val("neff_desercion_n")
rho <- val("neff_rho_implicito")
I1  <- val("neff_I_primera_banda")
neff <- function(n, r) n / (1 + (n - 1) * r)
N1 <- list(
  modulo = "cap1.m5", n = n1, rho = rho, decimales = 2,
  correcto = neff(n1, rho),
  distractores = list(
    list(id = "resta_lineal", valor = n1 * (1 - rho),
         error = "descontar la correlación linealmente, como si quitara una fracción de las observaciones en vez de dividir por el efecto de diseño"),
    list(id = "rho_primera_banda", valor = neff(n1, I1),
         error = "meter en la fórmula el Moran I de la primera banda de distancia en vez del rho medio: la correlación de los vecinos inmediatos no es la correlación media"),
    list(id = "multiplica", valor = n1 * (1 + (n1 - 1) * rho),
         error = "multiplicar por el efecto de diseño en vez de dividir")
  ),
  # El (n-1) contra el n NO entra como opción, y por qué no entra es la
  # mitad de lo que hay que enseñar: con n = 1121 los dos dan 64,5 y la
  # diferencia es de centésimas. Preguntar por eso sería preguntar por el
  # redondeo. La diferencia vive en el n pequeño, y así se dice.
  nota_n_menos_1 = list(
    n_grande = n1, con_n_menos_1 = neff(n1, rho), con_n = n1 / (1 + n1 * rho),
    n_pequeno = 25,
    con_n_menos_1_25 = neff(25, rho), con_n_25 = 25 / (1 + 25 * rho),
    dice = "con n grande el (n-1) es indiferente; el término manda cuando n es pequeño"
  )
)

# ---------------------------------------------------------------------
# N2 · Un grado de longitud (cap. 2, módulo 2)
# ---------------------------------------------------------------------
a  <- val("elip_a")
# La excentricidad se DERIVA del aplanamiento en vez de leerse de
# `elipsoide.e2`: ese campo viaja redondeado a los 10 decimales con que se
# escribe el JSON. Da igual para el resultado —son micras— y no da igual
# para el ancla: una que tolere el redondeo deja de distinguir una fórmula
# equivocada de una cifra corta.
f  <- 1 / val("elip_f_inv")
e2 <- 2 * f - f^2
lat_bog <- val("grad_lat")[2]           # 4,711°: la latitud de Bogotá tabulada
phi <- lat_bog * pi / 180
Nrad <- a / sqrt(1 - e2 * sin(phi)^2)                 # radio de curvatura primo vertical
Mrad <- a * (1 - e2) / (1 - e2 * sin(phi)^2)^(3 / 2)  # radio meridional

# QUÉ MIDE EL CAPÍTULO, medido y no supuesto. La columna `lon_m_elipsoide`
# NO es el arco de paralelo (pi/180)·N·cos(phi): es la GEODÉSICA sobre el
# elipsoide entre (0, phi) y (1, phi), que va un pelo más corta porque se
# comba hacia el polo. Las dos coinciden en el ecuador y se separan
# 0,0095 m en Bogotá y 0,53 m en Oslo, exactamente el (Δλ)²sen²φ/24 que
# predice la teoría. Se descubrió porque el ancla de N2 no cuadraba por 9 mm.
#
# Y la columna `lon_m_esfera` es lo que devuelve `st_distance` sobre
# EPSG:4326 TAL CUAL: en este entorno sf usa s2, que mide sobre una esfera
# de 6 371 008,8 m. No es un detalle de implementación, es el contenido del
# módulo 6 del capítulo 2 —s2 contra GEOS— y por eso el primer distractor
# de esta pregunta no es un error de fórmula inventado: **es la respuesta
# que da la orden que el estudiante va a escribir**.
geodesica <- function(lat, elipsoidal) {
  p <- st_sfc(st_point(c(0, lat)), st_point(c(1, lat)), crs = 4326)
  if (elipsoidal) return(as.numeric(lwgeom::st_geod_distance(p[1], p[2])))
  as.numeric(st_distance(p[1], p[2]))
}
g_elip  <- geodesica(lat_bog, TRUE)
g_esf   <- geodesica(lat_bog, FALSE)
arco    <- (pi / 180) * Nrad * cos(phi)
N2 <- list(
  modulo = "cap2.m2", lat = lat_bog, decimales = 1,
  correcto = g_elip,
  dif_s2_m = g_esf - g_elip,
  distractores = list(
    list(id = "s2_esfera", valor = g_esf,
         error = "dejar que st_distance mida con s2, que trabaja sobre una esfera, creyendo que mide sobre el elipsoide"),
    list(id = "olvida_coseno", valor = (pi / 180) * Nrad,
         error = "olvidar el coseno de la latitud: da el grado del ecuador en cualquier paralelo"),
    list(id = "radio_meridional", valor = (pi / 180) * Mrad * cos(phi),
         error = "usar el radio meridional M en vez del primo vertical N")
  ),
  # El arco de paralelo tampoco entra como opción: se separa de la geodésica
  # 9 mm en Bogotá, y una opción que se distingue en la cuarta cifra no
  # pregunta por geodesia, pregunta por decimales. Se queda como cifra de la
  # prosa —donde sí dice algo, porque en Oslo ya son 53 cm—.
  nota_arco = list(valor = arco, dif_m = arco - g_elip,
                   dice = "el arco de paralelo va por encima de la geodésica, y la separación crece con la latitud")
)

# ---------------------------------------------------------------------
# N3 · El lado cerrado del intervalo (cap. 3, módulo 3) — el hallazgo A.2
# ---------------------------------------------------------------------
nc <- read.csv(file.path(SALIDAS, "cap3_nc.csv"), stringsAsFactors = FALSE)
sid <- nc$sid74
cortes <- val("c3m3_cortes")
k <- length(cortes) - 1
# classInt: [a, b), con la última clase cerrada por arriba.
tam_r <- vapply(seq_len(k), function(i)
  sum(if (i < k) sid >= cortes[i] & sid < cortes[i + 1]
      else sid >= cortes[i] & sid <= cortes[i + 1]), integer(1))
# mapclassify: (a, b], con la primera clase abierta por abajo.
tam_py <- vapply(seq_len(k), function(i)
  sum(if (i == 1) sid <= cortes[i + 1]
      else sid > cortes[i] & sid <= cortes[i + 1]), integer(1))
N3 <- list(
  modulo = "cap3.m3", n = length(sid), cortes = cortes,
  tam_r = tam_r, tam_python = tam_py,
  primera_clase_r = tam_r[1], primera_clase_python = tam_py[1],
  movidos_primera = tam_py[1] - tam_r[1],
  error = "clasificar por cuantiles con el intervalo cerrado por el otro lado"
)

# ---------------------------------------------------------------------
# N4 · Euclídea sobre grados contra geodésica (cap. 2, módulo 6)
# ---------------------------------------------------------------------
est <- read.csv(file.path(SALIDAS, "cap2_estaciones.csv"), stringsAsFactors = FALSE)
pts <- st_as_sf(est, coords = c("lon", "lat"), crs = 4326)
# La referencia es la geodésica ELIPSOIDAL, que es la que mide el capítulo.
# Con s2 encendido —el estado por defecto— esto daría la esférica y el error
# del método ingenuo saldría medido contra la vara equivocada.
sf_use_s2(FALSE)
D_geo <- suppressMessages(as.numeric(st_distance(pts)))
sf_use_s2(TRUE)
dl <- outer(est$lon, est$lon, "-"); db <- outer(est$lat, est$lat, "-")
km_grado <- val("grad_lon_elip")[1] / 1000                  # 111,32 km, del propio capítulo
D_ing <- as.numeric(sqrt(dl^2 + db^2)) * km_grado * 1000    # metros, "un grado son 111 km"
sup <- upper.tri(matrix(0, nrow(est), nrow(est)))
g <- D_geo[sup]; i2 <- D_ing[sup]
rel <- (i2 - g) / g * 100
peor <- which.max(abs(rel))
idx <- which(sup, arr.ind = TRUE)[peor, ]
N4 <- list(
  modulo = "cap2.m6", n_estaciones = nrow(est), n_pares = length(g),
  km_por_grado = km_grado, referencia = "geodésica sobre el elipsoide WGS84 (lwgeom)",
  error_med_pct = mean(rel), error_max_pct = rel[peor],
  error_min_pct = min(rel), pct_sobreestima = mean(rel > 0) * 100,
  peor_par = list(
    a = est$estacion[idx[1]], b = est$estacion[idx[2]],
    d_geodesica_km = g[peor] / 1000, d_ingenua_km = i2[peor] / 1000
  ),
  error = "medir distancias euclídeas sobre grados y convertirlas con un factor fijo"
)

NUEVO <- list(n_efectivo = N1, grado_longitud = N2,
              convenio_intervalo = N3, euclidea_grados = N4)

# ---------------------------------------------------------------------
# LA GUARDA DE LOS DISTRACTORES, y existe por dos defectos propios.
#
# La primera versión ofrecía como opciones 64,52 y 64,47 —el (n-1) contra
# el n, que con n = 1121 no se distinguen— y 110945,9086 contra 110945,9181
# —la geodésica contra el arco de paralelo, nueve milímetros en ciento once
# kilómetros—. Las dos parecían distractores razonables al escribirlas:
# nombran un error real. Pero una opción que no se distingue de la
# respuesta no evalúa el error que nombra, evalúa el redondeo, y castiga
# al que entendió.
#
# La regla, mecanizada: **redondeados a la precisión con que la pregunta
# los va a mostrar, todos los valores tienen que ser distintos.** Se
# comprueba también entre distractores, porque dos opciones iguales dejan
# la pregunta con una alternativa menos sin que se note.
# ---------------------------------------------------------------------
for (nm in names(NUEVO)) {
  item <- NUEVO[[nm]]
  if (is.null(item$distractores)) next
  if (is.null(item$decimales))
    para(nm, " no declara con cuántos decimales se presenta")
  etiquetas <- c("correcto", vapply(item$distractores, function(x) x$id, ""))
  valores <- c(item$correcto, vapply(item$distractores, function(x) x$valor, numeric(1)))
  redondeados <- round(valores, item$decimales)
  d <- duplicated(redondeados)
  if (any(d)) {
    i <- which(d)[1]
    j <- which(redondeados == redondeados[i])[1]
    para("DISTRACTOR INDISTINGUIBLE · ", nm, ": «", etiquetas[j], "» y «",
         etiquetas[i], "» valen los dos ", format(redondeados[i], nsmall = item$decimales),
         " con ", item$decimales, " decimal(es).\n",
         "  Una opción que no se distingue de otra no evalúa el error que nombra.")
  }
}

# ---------------------------------------------------------------------
# Las series que dibujan las preguntas de lectura de gráfico. Todas
# salen de cifras ya reutilizadas: aquí solo se les da forma de serie.
# ---------------------------------------------------------------------
rejilla_inf <- en_ruta(CAPS$cap1, "inferencia.rejilla")
vario <- en_ruta(CAPS$cap1, "una_realizacion.variograma")
curva8 <- en_ruta(CAPS$cap3, "m8.curva")
pares4 <- en_ruta(CAPS$cap3, "m4.pares")

GRAFICOS <- list(
  g_cobertura = list(
    modulo = "cap1.m4", titulo = "Cobertura real de un IC al 95 % según la dependencia",
    phi = vapply(rejilla_inf, function(x) x$phi, numeric(1)),
    cobertura = vapply(rejilla_inf, function(x) x$cobertura, numeric(1))
  ),
  g_variograma = list(
    modulo = "cap1.m6", titulo = "Variograma: el teórico y lo que da UNA realización",
    lags = unlist(vario$lags), teorico = unlist(vario$teorico),
    media = unlist(vario$media), q05 = unlist(vario$q05), q95 = unlist(vario$q95)
  ),
  g_grado = list(
    modulo = "cap2.m2", titulo = "Metros de un grado de longitud según la latitud",
    lat = val("grad_lat"), elipsoide = val("grad_lon_elip"), esfera = val("grad_lon_esfera")
  ),
  g_proyecciones = list(
    modulo = "cap2.m3", titulo = "Distorsión de área y de ángulo por proyección",
    nombre = val("proy_nombres"), razon_max = val("proy_razon_max"),
    omega_med = val("proy_omega_med")
  ),
  g_discordancia = list(
    modulo = "cap3.m4", titulo = "% de municipios que cambian de clase, por par de esquemas",
    etiqueta = vapply(pares4, function(x) paste0(x$etiqueta_a, " / ", x$etiqueta_b), ""),
    pct = vapply(pares4, function(x) x$pct_cambian, numeric(1))
  ),
  g_escala = list(
    modulo = "cap3.m8", titulo = "La correlación según el número de zonas",
    zonas = vapply(curva8, function(x) x$zonas, numeric(1)),
    media = vapply(curva8, function(x) x$media, numeric(1)),
    sd = vapply(curva8, function(x) x$sd, numeric(1))
  )
)

for (nm in names(GRAFICOS)) {
  serie <- GRAFICOS[[nm]]
  largos <- vapply(serie[!names(serie) %in% c("modulo", "titulo")], length, integer(1))
  if (length(unique(largos)) != 1)
    para("el gráfico ", nm, " tiene series de largos distintos: ",
         paste(largos, collapse = ", "))
  if (any(vapply(serie, function(x) is.character(x) && any(grepl("<U\\+", x)), logical(1))))
    para("CODIFICACIÓN ROTA en el gráfico ", nm)
}

# ---------------------------------------------------------------------
# El catálogo de errores del módulo 8. Cada uno con su cifra medida y el
# módulo al que hay que volver.
# ---------------------------------------------------------------------
err <- function(id, titulo, doc, modulo, claves, dice, nuevas = list())
  list(id = id, titulo = titulo, doc = doc, modulo = modulo,
       claves = claves, dice = dice, nuevas = nuevas)

# Una cifra de `nuevo` citada por un error: la ruta dentro de NUEVO y el pie
# con el que se lee suelta. Hace falta porque el error mejor medido del
# catálogo —la distancia euclídea sobre grados— NO lo mide ninguna cifra de
# los capítulos: lo mide N4, que se calculó justamente para eso. La primera
# versión lo cableó a `medir.distancias`, que compara esfera contra
# elipsoide. Otra cosa, y con el pie de otra cosa: en la página montada se
# leía «Diferencia máxima entre distancia esférica y geodésica» debajo del
# título «Medir distancias euclídeas sobre grados».
nueva <- function(ruta, que) list(ruta = ruta, que = que)

ERRORES <- list(
  err("set_crs", "Reetiquetar creyendo que se reproyecta", "cap2", 5,
      c("etiq_set_crs", "etiq_transform", "etiq_lon_absurda"),
      "st_set_crs no mueve ni un vértice y no da error; st_transform mueve todos"),
  err("lonlat", "Invertir el orden lon/lat", "cap2", 8,
      c("csv_desplaz_med", "csv_en_colombia", "csv_hubo_aviso"),
      "el punto aterriza a miles de kilómetros y sf no avisa"),
  err("conteo_tasa", "Leer un mapa de conteos como mapa de riesgo", "cap3", 2,
      c("c3m2_r", "c3m2_solape", "c3m2_pct_est"),
      "el mapa de conteos es el mapa de la población"),
  err("euclidea", "Medir distancias euclídeas sobre grados", "cap2", 6,
      character(0),
      "un grado no mide lo mismo en el ecuador que en Bogotá, y el error nunca se compensa",
      nuevas = list(
        nueva("euclidea_grados.error_med_pct",
              "Error medio del método ingenuo sobre los 64 980 pares de estaciones del IDEAM"),
        nueva("euclidea_grados.error_max_pct", "Error del peor par de los 64 980"),
        nueva("euclidea_grados.pct_sobreestima",
              "Porcentaje de pares en los que el método ingenuo se pasa: al ser siempre por exceso, el error no se cancela al promediar"))),
  err("ee_ingenuo", "Usar el error estándar clásico con datos autocorrelacionados", "cap1", 4,
      c("inf_cobertura_phi4", "inf_factor_phi4", "inf_inflacion"),
      "el IC al 95 % cubre mucho menos del 95 %"),
  err("cv_aleatoria", "Validar un modelo espacial con CV aleatoria", "cap1", 10,
      c("cv_rmse_alea", "cv_rmse_bloques", "cv_inflacion"),
      "el desempeño estimado está inflado porque el vecino está en el otro pliegue"),
  err("agregacion", "Comparar correlaciones entre niveles de agregación", "cap3", 8,
      c("c3m8_r_ind", "c3m8_r_dep", "c3m8_subida"),
      "la correlación sube al agregar y no es la misma cantidad"),
  err("paleta", "Codificar con rojo y verde", "cap3", 5,
      c("c3m5_dE_normal", "c3m5_dE_deuter", "c3m5_caida"),
      "bajo deuteranopia los dos colores casi coinciden"),
  err("intervalo", "Clasificar por cuantiles sin mirar el lado cerrado", "cap3", 3,
      c("c3m3_empatados", "c3m3_convenio_r", "c3m3_convenio_py"),
      "R y Python dan particiones distintas del mismo dato con el mismo nombre"),
  err("buffer_grados", "Hacer un buffer o medir un área en grados", "cap2", 10,
      c("topo_buffer_grados", "topo_buffer_3857"),
      "el resultado sale en grados cuadrados, que no son ninguna superficie")
)

for (e in ERRORES) {
  if (!paste0(e$doc, ".m", e$modulo) %in% esperados)
    para("el error ", e$id, " apunta fuera del alcance")
  faltantes <- setdiff(e$claves, names(REUTILIZADO))
  if (length(faltantes))
    para("el error ", e$id, " cita claves que no existen: ",
         paste(faltantes, collapse = ", "))
  for (nv in e$nuevas)
    if (is.null(en_ruta(NUEVO, nv$ruta)))
      para("el error ", e$id, " cita nuevo:", nv$ruta, ", que no existe")
  if (!length(e$claves) && !length(e$nuevas))
    para("el error ", e$id, " no cita ninguna cifra")
}

# NINGÚN PIE DE CIFRA PUEDE SER RELATIVO, y esto salió mirando la página
# montada, no el código. Los `que` se escribieron como nota para quien
# redacta, y ahí «Lo mismo en %» se entiende porque está debajo de su
# hermana. Pero en el catálogo de errores cada cifra se lee SUELTA, y «Lo
# mismo en %» acabó rotulando como porcentaje de una distancia lo que es una
# diferencia de área. Un pie que depende del orden miente en cuanto alguien
# reordena, y reordenar no rompe nada visible.
RELATIVOS <- c("^Lo mismo", "^La misma", "^El mismo", "^Los mismos", "^Ídem", "^Igual ")
relativo <- function(q) any(vapply(RELATIVOS, grepl, logical(1), x = q))
for (nm in names(REUTILIZADO))
  if (relativo(REUTILIZADO[[nm]]$que))
    para("PIE RELATIVO · la cifra ", nm, " se describe como «",
         REUTILIZADO[[nm]]$que, "», que solo se entiende al lado de otra.\n",
         "  En el catálogo cada cifra se lee suelta: el pie tiene que bastarse.")
for (e in ERRORES) for (nv in e$nuevas)
  if (relativo(nv$que))
    para("PIE RELATIVO en el error ", e$id, ": «", nv$que, "»")

# El pie se imprime DETRÁS del valor —«35.29626 % — % de estudiantes…»—, así
# que empezarlo por el símbolo de la unidad lo repite y se lee como un
# tartamudeo. Es cosmético y por eso se mecaniza: nadie vuelve a mirar 119
# pies a mano.
for (nm in names(REUTILIZADO))
  if (grepl("^%", REUTILIZADO[[nm]]$que))
    para("PIE QUE EMPIEZA POR LA UNIDAD · la cifra ", nm, ": «",
         REUTILIZADO[[nm]]$que, "». Se imprime detrás del valor, que ya lleva el %.")

# ---------------------------------------------------------------------
# ANCLAS. Paran el guion. No son pruebas de humo: cada una compara este
# precálculo contra algo calculado por otro —el capítulo, sf, o el anexo
# A.2 del plan— y si no cuadra, no hay JSON.
# ---------------------------------------------------------------------
ancla <- function(nombre, obtenido, esperado, tol) {
  if (!isTRUE(abs(obtenido - esperado) <= tol))
    para("ANCLA ROTA · ", nombre, ": ", format(obtenido, digits = 12),
         " contra ", format(esperado, digits = 12), " (tolerancia ", tol, ")")
  invisible(TRUE)
}

ancla_cierto <- function(nombre, condicion, detalle) {
  if (!isTRUE(condicion))
    para("ANCLA ROTA · ", nombre, " · ", detalle)
  invisible(TRUE)
}

ancla("N1 reproduce el n efectivo del capítulo 1",
      N1$correcto, val("neff_desercion"), 1e-6)
ancla("N1 el % de información cuadra",
      N1$correcto / n1 * 100, val("neff_pct"), 1e-6)
ancla("N2 reproduce el grado de longitud del capítulo 2 sobre el elipsoide",
      N2$correcto, val("grad_lon_elip")[2], 1e-4)
ancla("N2 el distractor de s2 reproduce la columna esférica del capítulo",
      N2$distractores[[1]]$valor, val("grad_lon_esfera")[2], 1e-4)
ancla("N2 el arco de paralelo se separa de la geodésica lo que predice (Δλ)²sen²φ/24",
      N2$nota_arco$dif_m,
      N2$correcto * (pi / 180)^2 * sin(phi)^2 / 24, 1e-4)
nn <- N1$nota_n_menos_1
rel_grande  <- abs(nn$con_n_menos_1 - nn$con_n) / nn$con_n_menos_1
rel_pequeno <- abs(nn$con_n_menos_1_25 - nn$con_n_25) / nn$con_n_menos_1_25
ancla_cierto("N1 el (n-1) pesa mucho más con n pequeño que con n grande",
             rel_pequeno > 10 * rel_grande,
             sprintf("n=25 -> %.3f %% · n=%d -> %.3f %%",
                     rel_pequeno * 100, nn$n_grande, rel_grande * 100))
ancla("N3 el reparto con [a,b) reproduce el del capítulo 3",
      sum(abs(N3$tam_r - unlist(en_ruta(CAPS$cap3, "m3.esquemas[2].tam")))), 0, 0)
ancla("N3 los 39 empates del anexo A.2 siguen ahí",
      N3$movidos_primera, 11, 0)
ancla("N3 la primera clase pasa de 13 a 24 condados (anexo A.2)",
      N3$primera_clase_python, 24, 0)
# Esta ancla afirma algo que hay que dejar dicho porque es contraintuitivo:
# `st_distance` sobre EPSG:4326, sin tocar nada, NO mide sobre el elipsoide.
# Mide con s2, sobre una esfera. La primera versión de este archivo la escribió
# al revés —comparándola contra la columna elipsoidal— y habría publicado un
# preparcial que enseña lo contrario de lo que hace la orden.
ancla("N4 st_distance con s2 mide un grado ecuatorial sobre la ESFERA",
      geodesica(0, FALSE), val("grad_lon_esfera")[1], 1e-4)
ancla("N4 lwgeom mide ese mismo grado sobre el ELIPSOIDE",
      geodesica(0, TRUE), val("grad_lon_elip")[1], 1e-4)
ancla("N4 todos los pares se han comparado",
      N4$n_pares, nrow(est) * (nrow(est) - 1) / 2, 0)
ancla("el alcance son 30 módulos", length(esperados), 30, 0)
N_ANCLAS <- 14

# ---------------------------------------------------------------------
D <- list(
  meta = list(
    documento = "preparcial-corte-1",
    corte = "I",
    fecha_parcial = FECHA_PARCIAL,
    generado = format(Sys.time(), "%Y-%m-%dT%H:%M:%S"),
    semilla = SEMILLA,
    n_modulos_alcance = length(esperados),
    n_reutilizadas = length(REUTILIZADO),
    n_nuevas = length(NUEVO),
    n_graficos = length(GRAFICOS),
    n_errores = length(ERRORES),
    n_anclas = N_ANCLAS,
    alcance = esperados,
    r_version = R.version.string,
    paquetes = list(jsonlite = as.character(packageVersion("jsonlite")),
                    sf = as.character(packageVersion("sf")))
  ),
  reutilizado = REUTILIZADO,
  nuevo = NUEVO,
  graficos = GRAFICOS,
  errores = ERRORES
)

txt <- toJSON(D, auto_unbox = TRUE, digits = 10, null = "null", na = "null")
if (grepl('"NA"', txt, fixed = TRUE))
  para("hay NA escritos como la cadena \"NA\"")
if (grepl("<U\\+", txt))
  para("el JSON lleva codificación rota")
destino <- file.path(SALIDAS, "preparcial1_datos.json")
writeLines(txt, destino, useBytes = TRUE)

message(sprintf("  preparcial1_datos.json: %.1f KB", file.size(destino) / 1024))
message(sprintf("  %d cifras reutilizadas sobre %d módulos · %d cálculos nuevos · %d gráficos · %d errores · %d anclas",
                length(REUTILIZADO), length(esperados), length(NUEVO),
                length(GRAFICOS), length(ERRORES), N_ANCLAS))
