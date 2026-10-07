# =====================================================================
# genera_preparcial2.R — el precálculo del preparcial del Corte II (P1.1)
#
#   Estadística Espacial 2026-II (20929) · Parcial 2: jueves 15 de octubre
#   Capítulos 4 y 5, módulos 1 a 11 de cada uno. PLAN_Preparcial_Corte_2.md.
#
# QUÉ PRODUCE
#   precalculo/salidas/preparcial2_datos.json
#   precalculo/salidas/preparcial2_murchison_oro.csv       (para el auditor)
#   precalculo/salidas/preparcial2_murchison_fallas.csv    (para el auditor)
#   precalculo/salidas/preparcial2_murchison_greenstone.csv
#
# LAS REGLAS QUE MANDAN AQUÍ, heredadas del Corte I (genera_preparcial1.R)
#
# 1. Ninguna cifra del preparcial se escribe a mano (D10).
# 2. Una cifra de un capítulo no se copia: se REFERENCIA. Cada entrada de
#    `reutilizado` guarda archivo y ruta, y `audita_preparcial2.py` vuelve a
#    resolverla contra el capítulo. Si se regenera el capítulo 4 o el 5, hay
#    que volver a correr esto y el ensamblador.
# 3. El `que` de cada cifra se PUBLICA: el catálogo de errores lo imprime
#    detrás del valor. No es una nota para quien redacta.
#
# Y UNA PROPIA, QUE COSTÓ ANTES DE ESCRIBIR UNA LÍNEA
#
# 4. El nombre de una ruta no dice lo que mide; el generador del capítulo
#    sí. `m2.urbana_hist.teorico` parece la referencia «con las celdas
#    recortadas» y es UNA Poisson de media común (genera_cap4.R, junto a
#    `urbana_hist`). La pregunta A2 se escribió sobre lo que es, no sobre lo
#    que su nombre sugiere. Antes de añadir aquí una ruta, abrir el `.R`.
#
# LOS EJERCICIOS VAN SOBRE `murchison` (D5 del plan)
#
# Los 255 yacimientos de oro de Australia Occidental, con las fallas y el
# afloramiento de greenstone. Ningún documento del curso lo usa, y sobre
# él reaparecen casi todas las trampas de los dos capítulos —varias con el
# veredicto al revés que en Bogotá—, que es lo que obliga a razonar en vez
# de recordar. Las respuestas se anclan a un trozo LITERAL de su enunciado
# (`responde()`, como en genera_soluciones.R tras M5 de la revisión 2 del
# capítulo 5) y `sin_contestar()` exige que toda demanda tenga respuesta.
#
# Ejecutar SIEMPRE con el envoltorio:
#     precalculo/rscript.sh precalculo/genera_preparcial2.R
# =====================================================================

source("precalculo/utf8.R")

suppressPackageStartupMessages({
  library(jsonlite)
  library(sf)
  library(spatstat)
})
# La F por muestra reducida y la G con el mismo criterio, las del capítulo 4:
# la pregunta del 4.7 lee los pinos suecos con las MISMAS medianas que el
# módulo enseña sobre células, pinos japoneses y secuoyas.
source("precalculo/puntual.R")

SALIDAS <- "precalculo/salidas"
PROC <- "datos/procesado"
SEMILLA <- 2026
set.seed(SEMILLA)

FECHA_PARCIAL <- "2026-10-15"

para <- function(...) stop("PARADO · genera_preparcial2: ", ..., call. = FALSE)
r10 <- function(x) round(x, 10)

CAPS <- list(
  cap4 = fromJSON(file.path(SALIDAS, "cap4_datos.json"), simplifyVector = FALSE),
  cap5 = fromJSON(file.path(SALIDAS, "cap5_datos.json"), simplifyVector = FALSE)
)
ARCHIVO <- c(cap4 = "cap4_datos.json", cap5 = "cap5_datos.json")

# ---------------------------------------------------------------------
# El resolutor de rutas: nombres separados por punto e índices de lista
# entre corchetes, en base 1. El mismo de genera_preparcial1.R.
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
# LO REUTILIZADO. Una fila por cifra: de qué módulo del temario habla,
# dónde vive y qué dice. El `que` se publica.
# ---------------------------------------------------------------------
r <- function(clave, doc, modulo, ruta, que, vector = FALSE)
  list(clave = clave, doc = doc, modulo = modulo, ruta = ruta,
       que = que, vector = vector)

REUSA <- list(
  # ---- capítulo 4 -------------------------------------------------
  r("c4m1_n_urb",        "cap4", 1, "m1.urbana.n",            "Sedes dentro del perímetro urbano"),
  r("c4m1_n_dc",         "cap4", 1, "m1.dc.n",                "Sedes dentro del Distrito Capital completo"),
  r("c4m1_area_urb",     "cap4", 1, "m1.urbana.area_km2",     "Área del perímetro urbano, en km²"),
  r("c4m1_area_dc",      "cap4", 1, "m1.dc.area_km2",         "Área del Distrito Capital, en km²"),
  r("c4m1_lambda_urb",   "cap4", 1, "m1.urbana.lambda_km2",   "Intensidad de sedes en el perímetro urbano"),
  r("c4m1_lambda_dc",    "cap4", 1, "m1.dc.lambda_km2",       "Intensidad de sedes en el Distrito Capital"),
  r("c4m1_factor",       "cap4", 1, "m1.factor_lambda",       "Veces que la intensidad urbana supera a la del D.C.: la misma ciudad con otra ventana"),
  r("c4m1_total",        "cap4", 1, "m1.sedes_total",         "Filas del archivo de sedes: las de dentro del perímetro urbano más las que ppp() descarta"),
  r("c4m1_fuera_urb",    "cap4", 1, "m1.urbana.fuera",        "Sedes que ppp() descarta con la ventana del perímetro urbano"),
  r("c4m1_fuera_dc",     "cap4", 1, "m1.dc.fuera",            "Sedes que caen fuera también del Distrito Capital"),

  r("c4m2_celdas",       "cap4", 2, "m2.urbana.celdas",       "Celdas vivas de la rejilla 10 × 10 sobre el perímetro urbano"),
  r("c4m2_media",        "cap4", 2, "m2.urbana.media",        "Sedes por celda viva, de media, con la rejilla 10 × 10"),
  r("c4m2_dispersion",   "cap4", 2, "m2.urbana.dispersion",   "Índice de dispersión observado de las sedes: varianza entre media de los conteos"),
  r("c4m2_disp_nula",    "cap4", 2, "m2.urbana.dispersion_nula", "Índice de dispersión que daría, aproximadamente y de media, un Poisson homogéneo con la rejilla 10 × 10 recortada contra el perímetro urbano"),
  r("c4m2_vacios",       "cap4", 2, "m2.urbana.vacios",       "Celdas vivas sin ninguna sede, con la rejilla 10 × 10"),
  r("c4m2_maximo",       "cap4", 2, "m2.urbana.maximo",       "Sedes en la celda más poblada de la rejilla 10 × 10"),
  r("c4m2_esp_baja",     "cap4", 2, "m2.urbana.celdas_esperanza_baja", "Celdas vivas que esperan menos de 5 sedes con la rejilla 10 × 10"),
  r("c4m2_chi2",         "cap4", 2, "m2.urbana.chi2",         "χ² de cuadrantes de las sedes con la rejilla 10 × 10 sobre el perímetro urbano"),
  r("c4m2_gl",           "cap4", 2, "m2.urbana.gl",           "Grados de libertad de ese χ²: celdas vivas menos una"),
  r("c4m2_esp_min",      "cap4", 2, "m2.urbana.esperanza_min", "Sedes que espera la celda viva más pequeña de la rejilla 10 × 10 si λ fuera constante"),
  r("c4m2_esp_max",      "cap4", 2, "m2.urbana.esperanza_max", "Sedes que espera la celda viva más grande de la rejilla 10 × 10 si λ fuera constante"),

  r("c4m3_ce_bog",       "cap4", 3, "m3.bogota.clark_evans",  "Índice de Clark-Evans sin corregir de las sedes, ventana urbana"),
  r("c4m3_nn_bog",       "cap4", 3, "m3.bogota.nn_media",     "Distancia media de cada sede a su vecina más próxima, en metros, ventana urbana"),
  r("c4m3_nn_esp_bog",   "cap4", 3, "m3.bogota.nn_esperada",  "Distancia al vecino más próximo que daría el azar con la intensidad urbana, en metros"),

  r("c4m4_n_real",       "cap4", 4, "m4.n_realizaciones",     "Realizaciones de CSR simuladas en el módulo 4"),
  r("c4m4_lambda",       "cap4", 4, "m4.lambda",              "Intensidad de esas realizaciones en el cuadrado unidad"),
  r("c4m4_media",        "cap4", 4, "m4.conteo_media",        "Media del número de puntos de las realizaciones de CSR"),
  r("c4m4_var",          "cap4", 4, "m4.conteo_var",          "Varianza del número de puntos de las realizaciones de CSR"),
  r("c4m4_R_media",      "cap4", 4, "m4.R_csr.media",         "Media del índice de Clark-Evans sin corregir sobre las realizaciones de CSR"),
  r("c4m4_R_sd",        "cap4", 4, "m4.R_csr.sd",            "Desviación típica del índice de Clark-Evans sin corregir sobre las realizaciones de CSR"),
  r("c4m4_R_bajo1",      "cap4", 4, "m4.R_csr.bajo_1",        "Realizaciones de CSR con un índice de Clark-Evans por debajo de 1"),

  r("c4m5_chi2",         "cap4", 5, "m5.original.chi2",       "χ² de cuadrantes 5 × 5 de las plántulas de secuoya, idéntico en el patrón rebarajado"),
  r("c4m5_gl",           "cap4", 5, "m5.original.gl",         "Grados de libertad del χ² de cuadrantes 5 × 5"),
  r("c4m5_ce_orig",      "cap4", 5, "m5.ce_original",         "Índice de Clark-Evans sin corregir de las plántulas de secuoya originales"),
  r("c4m5_ce_reb",       "cap4", 5, "m5.ce_rebarajado",       "Índice de Clark-Evans sin corregir de las plántulas rebarajadas dentro de cada celda 5 × 5"),

  r("c4m6_red_rechazos", "cap4", 6, "m6.redwood_rechazos",    "Rejillas, de las diez del barrido, en que el test de cuadrantes rechaza sobre las secuoyas"),
  r("c4m6_red_emin10",   "cap4", 6, "m6.redwood.esperanza_min[7]", "Plántulas que espera cada celda de la rejilla 10 × 10 sobre las secuoyas"),

  r("c4m7_umbral_f",     "cap4", 7, "m7.j_umbral_f",          "Valor de F hasta el que se dibuja J, el tramo que spatstat recomienda leer"),
  r("c4m7_f_sitios",     "cap4", 7, "m7.bogota.f_sitios",     "Sitios de la rejilla de F que caen dentro de la ventana urbana"),
  r("c4m7_f_rejilla",    "cap4", 7, "m7.bogota.f_rejilla",    "Sitios de la rejilla de F sobre el rectángulo que encierra la ventana"),

  r("c4m8_vecino_max",   "cap4", 8, "m8.bogota.vecino_max",   "Distancia de la sede más aislada a su vecina más próxima, en metros: pasada esa distancia, G vale 1"),
  r("c4m8_rmax",         "cap4", 8, "m8.abanico.bogota.r_b",  "Distancia máxima a la que Kest mira por defecto sobre la ventana urbana, en metros"),
  r("c4m8_peso_1km",     "cap4", 8, "m8.piezas.peso_medio",   "Peso medio de traslación de las parejas de sedes a 1 km o menos, ventana urbana"),
  r("c4m8_peso_rmax",    "cap4", 8, "m8.pesos_borde.hasta_rmax.peso_medio", "Peso medio de traslación de las parejas de sedes en la última décima antes del alcance por defecto de Kest"),
  r("c4m8_peso_doble",   "cap4", 8, "m8.pesos_borde.al_doble.peso_medio",   "Peso medio de traslación de las parejas de sedes en la última décima antes del doble de ese alcance"),
  r("c4m8_peso_doble_max", "cap4", 8, "m8.pesos_borde.al_doble.peso_max",   "Mayor peso de traslación de una pareja de sedes en la última décima antes del doble del alcance"),
  r("c4m8_max_desvio",   "cap4", 8, "m8.bogota.max_desvio",   "Mayor valor de L(r) − r de las sedes"),
  r("c4m8_parejas",      "cap4", 8, "m8.piezas.parejas_r",    "Parejas ordenadas de sedes a 1 km o menos, en la ventana urbana"),
  r("c4m8_vecinas",      "cap4", 8, "m8.piezas.vecinas",      "Vecinas por sede a 1 km o menos, con los pesos de traslación"),
  r("c4m8_vecinas_csr",  "cap4", 8, "m8.piezas.vecinas_csr",  "Vecinas por sede a 1 km o menos que daría el azar con la misma intensidad"),

  r("c4m9_g_max",        "cap4", 9, "m9.bogota.g_max",        "Máximo de la correlación de pares de las sedes, en el primer radio del barrido"),
  r("c4m9_g_final",      "cap4", 9, "m9.bogota.g_obs[101]",   "Correlación de pares de las sedes en el radio más largo que se miró, el último del barrido"),
  r("c4m9_r_final",      "cap4", 9, "m9.bogota.r[101]",       "Radio más largo en que se miró la correlación de pares de las sedes, en metros"),

  r("c4m10_veces_iso",   "cap4", 10, "m10.coste.veces_isotropica_sobre_traslacion", "Veces que tarda más la corrección isotrópica que la de traslación al calcular K sobre la ventana urbana (medido en una máquina: vale el orden de magnitud)"),
  r("c4m10_vertices",    "cap4", 10, "m10.ventana.vertices",  "Vértices del contorno de la ventana urbana de Bogotá"),
  r("c4m10_r_sesgo",     "cap4", 10, "m10.r_sesgo_max",       "Distancia a la que la K sin corregir de las sedes queda más por debajo de la corregida, en metros"),
  r("c4m10_sesgo",       "cap4", 10, "m10.sesgo_max_pct",     "Porcentaje máximo en que la K sin corregir de las sedes queda por debajo de la corregida por traslación, ventana urbana"),
  r("c4m10_horas_iso",   "cap4", 10, "m10.coste.horas_envolvente_isotropica", "Horas que costaría una envolvente de 999 con la corrección isotrópica"),
  r("c4m10_min_trans",   "cap4", 10, "m10.coste.minutos_envolvente_traslacion", "Minutos que cuesta esa misma envolvente con la corrección de traslación"),

  r("c4m11_tasa_bog",    "cap4", 11, "m11.bogota.tasa_salida.pct", "Porcentaje de las 999 simulaciones de CSR de las sedes que se salen en algún r de la banda de sus cuantiles centrales al 95 % (no de la del mínimo y el máximo, que es la que dibuja el capítulo)"),
  r("c4m11_nivel",       "cap4", 11, "m11.bogota.tasa_salida.nivel", "Cobertura en cada r de la banda de cuantiles con que se mide esa tasa: un contraste puntual al 5 %"),
  r("c4m11_nsim",        "cap4", 11, "m11.nsim",              "Simulaciones de las envolventes del capítulo 4"),
  r("c4m11_p_min",       "cap4", 11, "m11.p_minimo",          "p-valor más pequeño posible con 999 simulaciones"),

  # ---- capítulo 5 -------------------------------------------------
  r("c5m1_n_ken",        "cap5", 1, "m1.ventana.n",            "Sedes de Kennedy, contadas con la geometría de la localidad"),
  r("c5m1_area_ken",     "cap5", 1, "m1.ventana.area_km2",     "Área de la localidad de Kennedy, en km²"),
  r("c5m1_lambda_ken",   "cap5", 1, "m1.ventana.lambda_km2",   "Intensidad media de sedes en Kennedy, n/|W|, por km²"),

  r("c5m2_sigmas",       "cap5", 2, "m2.familia.sigmas_m",     "Anchos de banda del abanico del módulo 2, en metros", vector = TRUE),
  r("c5m2_maximos",      "cap5", 2, "m2.familia.max_km2",      "Intensidad máxima de cada superficie del abanico, por km²", vector = TRUE),
  r("c5m2_caida",        "cap5", 2, "m2.familia.caida_pct",    "Porcentaje en que cae el pico al pasar del ancho más estrecho al más ancho"),
  r("c5m2_nucleo_dif",   "cap5", 2, "m2.nucleos.max_dif_pct",  "Porcentaje máximo en que se mueve el pico al cambiar de núcleo con el mismo σ"),

  r("c5m3_tope_jp",      "cap5", 3, "m3.topes[1].sigma",       "Lo que devuelve bw.ppl sobre los pinos japoneses: el tope de su intervalo de búsqueda"),
  r("c5m3_razon_urb",    "cap5", 3, "m3.urbana.razon",         "Veces que el mayor de los cuatro selectores de ancho supera al menor sobre la ciudad"),

  r("c5m4_n",            "cap5", 4, "m4.n",                    "Sedes de Kennedy con las que se mide la masa de la KDE"),
  r("c5m4_sigma_800",    "cap5", 4, "m4.tabla[3].sigma_m",     "El σ más ancho de la tabla de masas del módulo 4, en metros"),
  r("c5m4_masa_def",     "cap5", 4, "m4.tabla[3].masa_defecto", "Integral de la KDE con la corrección por defecto a σ = 800 m"),
  r("c5m4_masa_sin",     "cap5", 4, "m4.tabla[3].masa_sin_corregir", "Integral de la KDE sin corregir el borde a σ = 800 m"),
  r("c5m4_masa_dig",     "cap5", 4, "m4.tabla[3].masa_diggle", "Integral de la KDE con diggle = TRUE a σ = 800 m"),
  r("c5m4_exceso",       "cap5", 4, "m4.tabla[3].exceso_defecto_pct", "Porcentaje en que la integral con la corrección por defecto supera a n en Kennedy, a σ = 800 m"),

  r("c5m5_n_of",         "cap5", 5, "m5.capas.oferta.n",       "Sedes de la capa de oferta: todas las de la ventana urbana"),
  r("c5m5_n_11",         "cap5", 5, "m5.capas.grado_11.n",     "Sedes con grado 11, las que entran en la capa de bachillerato"),
  r("c5m5_pct_11",       "cap5", 5, "m5.capas.grado_11.pct_de_las_sedes", "Porcentaje de las sedes que tiene grado 11"),
  r("c5m5_total_est",    "cap5", 5, "m5.capas.estudiantes.total", "Evaluados de Saber 11 con que se pesa la tercera capa"),
  r("c5m5_cor_of_11",    "cap5", 5, "m5.cor_oferta_grado11",   "Correlación entre las superficies de oferta y de bachillerato"),
  r("c5m5_cor_of_es",    "cap5", 5, "m5.cor_oferta_estudiantes", "Correlación entre las superficies de oferta y de evaluados"),
  r("c5m5_cor_11_es",    "cap5", 5, "m5.cor_grado11_estudiantes", "Correlación entre las superficies de bachillerato y de evaluados"),

  r("c5m6_ch_pmax",      "cap5", 6, "m6.chorley.p_max",        "Probabilidad máxima de que un cáncer registrado sea de laringe, en el mapa de chorley"),
  r("c5m6_ch_global",    "cap5", 6, "m6.chorley.prop_global",  "Proporción de casos de laringe sobre todos los cánceres de chorley"),
  r("c5m6_ch_casos",     "cap5", 6, "m6.chorley.casos",        "Casos de cáncer de laringe en chorley"),
  r("c5m6_ch_controles", "cap5", 6, "m6.chorley.controles",    "Controles de cáncer de pulmón en chorley"),
  r("c5m6_orient_ch",    "cap5", 6, "m6.chorley.orientacion_verificada", "Fracción de casos de laringe entre los cincuenta vecinos del máximo del mapa de chorley hecho al derecho (los niveles reordenados para que pinte laringe): por encima de la proporción global, como debe"),
  r("c5m6_bog_global",   "cap5", 6, "m6.bogota.prop_global",   "Proporción de sedes oficiales sobre todas las sedes de la ventana urbana"),
  r("c5m6_orient_bog",   "cap5", 6, "m6.bogota.orientacion_verificada", "Fracción de sedes oficiales entre los cincuenta vecinos del máximo del mapa de Bogotá: por encima de la proporción global de oficiales"),

  r("c5m7_bei_n",        "cap5", 7, "m7.bei.n",                "Árboles de Beilschmiedia en la parcela de Barro Colorado"),
  r("c5m7_razon_bog",    "cap5", 7, "m7.bogota.curva.razon",   "Razón entre el ρ máximo y el mínimo de la curva rhohat de las sedes contra la distancia al centro, en todo su rango"),
  r("c5m7_bulto_bog",    "cap5", 7, "m7.bogota.curva.razon_bulto", "Razón entre el ρ máximo y el mínimo de la curva rhohat de las sedes, solo entre los percentiles 5 y 95 de la distancia al centro"),

  r("c5m8_suma_pesos",   "cap5", 8, "m8.forzado.suma_pesos_km2", "Suma de los pesos de la cuadratura por defecto sobre la ciudad, en km²"),
  r("c5m8_area",         "cap5", 8, "m8.forzado.area_km2",     "Área de la ventana urbana, en km²"),
  r("c5m8_sin_contar",   "cap5", 8, "m8.cuadratura.tabla[2].sin_contar_km2", "Área de ciudad que la cuadratura por defecto deja sin contar"),
  r("c5m8_esperadas",    "cap5", 8, "m8.cuadratura.tabla[2].integral_exacta", "Sedes que el modelo de la distancia pone sobre la ciudad con la integral bien hecha"),
  r("c5m8_gana_ppm",     "cap5", 8, "m8.comparacion.gana_distancia_ppm", "Puntos de AIC con que gana el modelo de la distancia según los AIC que devuelve ppm"),
  r("c5m8_gana_const",   "cap5", 8, "m8.comparacion.gana_constante_exacta", "Puntos de AIC con que gana el modelo constante con la integral bien hecha en los dos"),

  r("c5m9_xc",           "cap5", 9, "m9.centrado.coef[2]",     "Coeficiente de xc en ppm(~ xc + yc), por kilómetro hacia el este"),
  r("c5m9_yc",           "cap5", 9, "m9.centrado.coef[3]",     "Coeficiente de yc en ppm(~ xc + yc), por kilómetro hacia el norte"),
  r("c5m9_z_xc",         "cap5", 9, "m9.centrado.z[2]",        "z del coeficiente de xc bajo el Poisson"),
  r("c5m9_z_yc",         "cap5", 9, "m9.centrado.z[3]",        "z del coeficiente de yc bajo el Poisson"),
  r("c5m9_cond",         "cap5", 9, "m9.crudo.cond_reciproco", "Número de condición recíproco de la matriz de diseño de la cuadratura de ppm (sedes y puntos ficticios) con las coordenadas crudas en EPSG:9377"),
  r("c5m9_mejora",       "cap5", 9, "m9.mejora_condicion",     "Factor en que mejora ese número de condición al centrar y pasar a kilómetros"),

  r("c5m10_pct_fuera",   "cap5", 10, "m10.pct_r_fuera_de_banda", "Porcentaje de radios en que la K inhomogénea de las sedes —con la λ̂ por núcleo que Kinhom estima por defecto— se sale de la banda de 999 simulaciones del modelo ajustado"),
  r("c5m10_primer",      "cap5", 10, "m10.primer_r_fuera_m",   "Primer radio en que la K inhomogénea se sale de la banda del modelo, en metros"),
  r("c5m10_ultimo",      "cap5", 10, "m10.ultimo_r_fuera_m",   "Último radio en que la K inhomogénea se sale de la banda del modelo, en metros"),
  r("c5m10_rmax",        "cap5", 10, "m10.r_max_m",            "Radio máximo del barrido de la K inhomogénea, en metros"),
  r("c5m10_nodos_dentro","cap5", 10, "m10.nodos_dentro_tras_el_tramo", "Radios del barrido en que la K inhomogénea, de vuelta en la banda, se queda dentro hasta el final"),
  r("c5m10_tasa",        "cap5", 10, "m10.tasa_salida.pct",    "Porcentaje de las 999 curvas del modelo ajustado del capítulo 5 que cruzan en algún radio la banda del mínimo y el máximo de las demás, cuyo nivel puntual es del 0.2 %"),
  r("c5m10_nivel",       "cap5", 10, "m10.nivel_puntual_pct",  "Nivel puntual, en porcentaje, de la banda del mínimo y el máximo de 999 simulaciones"),
  r("c5m10_veces_nivel", "cap5", 10, "m10.tasa_salida.veces_el_nivel", "Veces que esa tasa de salida supera el nivel puntual de su banda"),
  r("c5m10_dclf",        "cap5", 10, "m10.test_global.dclf_p", "p del test DCLF de la K inhomogénea contra el modelo ajustado"),
  r("c5m10_nsim",        "cap5", 10, "m10.tasa_salida.nsim",   "Simulaciones del modelo ajustado con que se construye la banda de la K inhomogénea"),
  r("c5m10_fuera",       "cap5", 10, "m10.tasa_salida.fuera",  "Curvas del modelo, de 999, que cruzan en algún radio la banda de las demás"),
  r("c5m10_mmean_pct",   "cap5", 10, "m10.mmean_vs_teorica_pct", "Porcentaje máximo en que la media de las K inhomogéneas del modelo se separa de πr² en el barrido"),

  r("c5m11_th_iso_esc",  "cap5", 11, "m11.ajustes[1].parametros.scale", "Escala del Thomas ajustado a las sedes con la K isotrópica, en metros"),
  r("c5m11_th_tr_esc",   "cap5", 11, "m11.ajustes[2].parametros.scale", "Escala del Thomas ajustado a las sedes con la K de traslación, en metros"),
  r("c5m11_th_iso_mu",   "cap5", 11, "m11.ajustes[1].mu",      "Sedes por conglomerado del Thomas ajustado con la K isotrópica"),
  r("c5m11_th_tr_mu",    "cap5", 11, "m11.ajustes[2].mu",      "Sedes por conglomerado del Thomas ajustado con la K de traslación"),
  r("c5m11_mat_iso_esc", "cap5", 11, "m11.ajustes[3].parametros.scale", "Escala del Matérn ajustado a las sedes con la K isotrópica: el radio del disco, en metros"),
  r("c5m11_mat_iso_mu",  "cap5", 11, "m11.ajustes[3].mu",      "Sedes por conglomerado del Matérn ajustado con la K isotrópica: casi las mismas que el Thomas con la misma K"),
  r("c5m11_th_iso_seg",  "cap5", 11, "m11.ajustes[1].segundos", "Segundos que tarda kppm con la K isotrópica sobre la ventana urbana"),
  r("c5m11_th_tr_seg",   "cap5", 11, "m11.ajustes[2].segundos", "Segundos que tarda kppm con la K de traslación sobre la ventana urbana"),
  r("c5m11_mu_pct",      "cap5", 11, "m11.divergencia[1].mu_pct", "Porcentaje en que cambian las sedes por conglomerado del Thomas al cambiar de corrección"),
  r("c5m11_deff",        "cap5", 11, "m11.tendencia.efecto_diseno", "Veces que se multiplica la varianza del coeficiente de xc con Thomas y la K de traslación, frente a la del Poisson"),
  r("c5m11_n",           "cap5", 11, "m11.tendencia.n",        "Sedes de la ventana urbana con que se ajusta la tendencia"),
  r("c5m11_neff",        "cap5", 11, "m11.tendencia.n_efectivo", "Sedes independientes a las que equivalen las de la ventana urbana para estimar el gradiente"),
  r("c5m11_mat_iso_inf", "cap5", 11, "m11.tendencia.ajustes[3].inflacion[1]", "Veces que crece el error estándar de xc con Matérn y la K isotrópica, frente al del Poisson"),
  r("c5m11_th_iso_inf",  "cap5", 11, "m11.tendencia.ajustes[1].inflacion[1]", "Veces que crece el error estándar de xc con Thomas y la K isotrópica, frente al del Poisson"),
  r("c5m11_th_tr_inf",   "cap5", 11, "m11.tendencia.ajustes[2].inflacion[1]", "Veces que crece el error estándar de xc con Thomas y la K de traslación, frente al del Poisson"),
  r("c5m11_z_pois",      "cap5", 11, "m11.tendencia.poisson.z[1]", "z del coeficiente de xc bajo el Poisson"),
  r("c5m11_z_th_tr",     "cap5", 11, "m11.tendencia.ajustes[2].z[1]", "z del coeficiente de xc con Thomas y la K de traslación"),
  r("c5m11_z_abs_max",   "cap5", 11, "m11.tendencia.z_xc_abs_max", "Mayor |z| del coeficiente de xc entre los seis ajustes de conglomerado"),
  r("c5m11_zc",          "cap5", 11, "m11.tendencia.z_critico", "Valor crítico de una z al 5 % bilateral"),
  r("c5m11_dup_cambio",  "cap5", 11, "m11.duplicados.cambio_maximo_pct", "Mayor cambio porcentual de un parámetro de conglomerado al quitar las sedes duplicadas"),
  r("c5m11_repetidas",   "cap5", 11, "m11.duplicados.repetidos", "Sedes de la ventana urbana que repiten las coordenadas de otra")
)

# ---------------------------------------------------------------------
# Resolución y guardas: una cifra que no existe, un vector que se ha
# hecho enorme o una cadena con la codificación rota paran el guion.
# ---------------------------------------------------------------------
REUTILIZADO <- list()
for (e in REUSA) {
  if (!is.null(REUTILIZADO[[e$clave]]))
    para("la clave ", e$clave, " está declarada dos veces")
  v <- en_ruta(CAPS[[e$doc]], e$ruta)
  if (is.null(v))
    para("no existe ", e$doc, ":", e$ruta, " (clave ", e$clave, ")")
  if (is.list(v)) {
    if (all(vapply(v, function(x) is.atomic(x) && length(x) == 1, logical(1)))) {
      v <- unlist(v)
    } else {
      para(e$clave, " (", e$doc, ":", e$ruta, ") no es una cifra ni un vector")
    }
  }
  if (!e$vector && length(v) != 1)
    para(e$clave, " trae ", length(v), " valores y no está declarada como vector")
  if (length(v) > 40)
    para(e$clave, " trae ", length(v), " valores: demasiado para incrustarlo")
  if (is.character(v) && any(grepl("<U\\+", v)))
    para("CODIFICACIÓN ROTA en ", e$doc, ":", e$ruta)
  if (is.numeric(v) && any(!is.finite(v)))
    para(e$clave, " tiene valores no finitos")
  REUTILIZADO[[e$clave]] <- list(
    origen = unname(ARCHIVO[e$doc]), ruta = e$ruta,
    doc = e$doc, modulo = e$modulo, que = e$que, valor = unname(v))
}
val <- function(clave) {
  if (is.null(REUTILIZADO[[clave]])) para("la clave ", clave, " no está en REUSA")
  REUTILIZADO[[clave]]$valor
}

esperados <- c(paste0("cap4.m", 1:11), paste0("cap5.m", 1:11))
cubiertos <- unique(vapply(REUTILIZADO, function(x) paste0(x$doc, ".m", x$modulo), ""))
if (length(setdiff(esperados, cubiertos)))
  para("módulos del alcance sin ninguna cifra: ",
       paste(setdiff(esperados, cubiertos), collapse = ", "))
if (length(setdiff(cubiertos, esperados)))
  para("cifras de módulos FUERA del alcance: ",
       paste(setdiff(cubiertos, esperados), collapse = ", "))

# Ningún pie puede ser relativo ni empezar por la unidad: el catálogo los
# imprime sueltos y detrás del valor (§12.7 del plan del Corte I).
RELATIVOS <- c("^Lo mismo", "^La misma", "^El mismo", "^Los mismos", "^Ídem", "^Igual ")
for (nm in names(REUTILIZADO)) {
  q <- REUTILIZADO[[nm]]$que
  if (any(vapply(RELATIVOS, grepl, logical(1), x = q)))
    para("PIE RELATIVO · ", nm, ": «", q, "»")
  if (grepl("^%", q)) para("PIE QUE EMPIEZA POR LA UNIDAD · ", nm)
}

message(sprintf("  %d cifras reutilizadas sobre %d módulos", length(REUTILIZADO), length(cubiertos)))

# =====================================================================
# LOS CÁLCULOS NUEVOS DE LAS PREGUNTAS
#
# Cada uno existe porque una pregunta pide algo que ningún capítulo
# calculó: una transferencia (la misma idea sobre otra ventana, otro nsim,
# otro rectángulo) o el error concreto que una retroalimentación nombra.
# Los errores van como `distractores` con su `error` dicho en palabras, y
# una guarda exige que se distingan de la respuesta a la precisión con que
# se publican (la lección del (n-1) contra el n del Corte I).
# =====================================================================
cole <- st_read(file.path(PROC, "bogota_colegios.gpkg"), quiet = TRUE)
XY <- st_coordinates(cole)
ppp_en <- function(archivo) {
  v <- st_read(file.path(PROC, archivo), quiet = TRUE)
  if (st_crs(v)$epsg != 9377L) para(archivo, " no está en EPSG:9377")
  w <- as.owin(st_geometry(st_union(v)))
  suppressWarnings(ppp(XY[, 1], XY[, 2], window = w))
}
p_urb <- ppp_en("bogota_ventana_urbana.gpkg")
p_dc  <- ppp_en("bogota_ventana_dc.gpkg")

# ---------------------------------------------------------------------
# A3 · Las mismas sedes, otra ventana, otra R (cap. 4, módulo 3)
#
# R divide la distancia media al vecino por la que daría el azar CON LA λ
# DE LA VENTANA. Con el D.C. entra suelo sin colegios, λ cae y la
# referencia del azar se alarga: la R baja sin que ninguna sede se haya
# movido. Es la lección del módulo 1 —la ventana es parte del estimador—
# leída desde el módulo 3.
# ---------------------------------------------------------------------
N_CE <- list(
  modulo = "cap4.m3",
  n_urb = npoints(p_urb), n_dc = npoints(p_dc),
  ce_urb = r10(clarkevans(p_urb)[["naive"]]),
  ce_dc = r10(clarkevans(p_dc)[["naive"]]),
  nn_dc = r10(mean(nndist(p_dc))),
  nn_esp_dc = r10(1 / (2 * sqrt(intensity(p_dc)))),
  lambda_dc_km2 = r10(intensity(p_dc) * 1e6)
)

# ---------------------------------------------------------------------
# A1 · La intensidad del resto del Distrito (cap. 4, módulo 1)
#
# El simulacro 5 del capítulo ya pide el cociente de intensidades entre dos
# ventanas; lo que nadie pide es la ventana que queda al RESTAR una de otra.
# Con ella se ve que la λ del D.C. es la media de dos regímenes que no se
# parecen, y que una ventana nueva trae su n y su |W| a la vez. Se cuenta
# con la geometría, no restando conteos: si alguna sede urbana quedara
# fuera del polígono del D.C., la resta mentiría.
# ---------------------------------------------------------------------
W_RESTO <- setminus.owin(Window(p_dc), Window(p_urb))
en_urb <- inside.owin(XY[, 1], XY[, 2], Window(p_urb))
en_dc  <- inside.owin(XY[, 1], XY[, 2], Window(p_dc))
if (any(en_urb & !en_dc)) para("A1: hay sedes urbanas fuera del D.C. y el resto ya no es una resta")
n_resto <- sum(inside.owin(XY[, 1], XY[, 2], W_RESTO))
if (n_resto != sum(en_dc & !en_urb)) para("A1: la ventana del resto no cuenta lo mismo que la resta de conteos")
a_resto <- area.owin(W_RESTO) / 1e6
lam_resto <- n_resto / a_resto
N_RESTO <- list(
  modulo = "cap4.m1", n_resto = n_resto, area_resto_km2 = r10(a_resto),
  lambda_resto_km2 = r10(lam_resto), decimales = 1,
  correcto = val("c4m1_lambda_urb") / lam_resto,
  distractores = list(
    list(id = "el_del_dc", valor = val("c4m1_factor"),
         error = "comparar con la λ del Distrito entero, que incluye la propia ciudad: es el factor del módulo 1"),
    list(id = "area_entera", valor = val("c4m1_lambda_urb") / (n_resto / val("c4m1_area_dc")),
         error = "dividir las sedes del resto por el área del Distrito entero en vez de por la del resto"),
    list(id = "al_reves", valor = lam_resto / val("c4m1_lambda_urb"),
         error = "invertir el cociente")
  )
)

# ---------------------------------------------------------------------
# A4 · Diez veces más puntos en el mismo cuadrado (cap. 4, módulo 4)
#
# El banco de la defensa ya pregunta por qué la media de R no cae en 1 y por
# qué n cambia de una realización a otra. Lo que nadie pregunta es qué le
# pasa a ese sesgo con la densidad: se encoge —el vecino está más cerca y
# a menos puntos se les escapa fuera—, pero el azar de R se encoge casi al
# mismo ritmo, y la proporción de realizaciones bajo 1 apenas se mueve.
# ---------------------------------------------------------------------
LAM_DENSO <- 10 * val("c4m4_lambda")
set.seed(SEMILLA)
sim_denso <- replicate(val("c4m4_n_real"), {
  X <- rpoispp(LAM_DENSO)
  c(R = as.numeric(clarkevans(X, correction = "none")), n = npoints(X))
})
set.seed(SEMILLA)
N_DENSO <- list(
  modulo = "cap4.m4", lambda = LAM_DENSO, n_real = ncol(sim_denso),
  R_media = r10(mean(sim_denso["R", ])), R_sd = r10(sd(sim_denso["R", ])),
  R_bajo1 = as.integer(sum(sim_denso["R", ] < 1)),
  pct_bajo1 = r10(100 * mean(sim_denso["R", ] < 1)),
  pct_bajo1_capitulo = r10(100 * val("c4m4_R_bajo1") / val("c4m4_n_real")),
  sesgo = r10(mean(sim_denso["R", ]) - 1), sesgo_capitulo = r10(val("c4m4_R_media") - 1),
  n_media = r10(mean(sim_denso["n", ])), n_var = r10(var(sim_denso["n", ]))
)
# Lo que la pregunta afirma, comprobado: el sesgo baja sin desaparecer, la
# proporción bajo 1 se queda a menos de tres puntos de la del capítulo, y la
# varianza del conteo crece con λ (es Poisson).
if (!(N_DENSO$R_media > 1 && N_DENSO$R_media < val("c4m4_R_media") - 0.02))
  para("A4: con diez veces más puntos la media de R ya no se acerca a 1 sin llegar")
if (abs(N_DENSO$pct_bajo1 - N_DENSO$pct_bajo1_capitulo) > 3)
  para("A4: la proporción de realizaciones bajo 1 ya no se parece a la del capítulo")
if (!(N_DENSO$n_var > 5 * val("c4m4_var"))) para("A4: la varianza del conteo ya no crece con λ")

# ---------------------------------------------------------------------
# A10 · El peso de traslación sobre la ventana urbana (cap. 4, módulo 10)
#
# La afirmación falsa n.º 8 del Taller 2 y el banco ya cubren qué cuesta
# cada corrección y que no coinciden. Aquí se pregunta por el mecanismo de
# la de traslación con números: |W| / |W ∩ (W + v)| depende del vector v
# —longitud Y dirección— y no de dónde esté la pareja, y no vale 1 para
# ninguna pareja. El solape se mide con el polígono exacto (intersect.owin),
# que es la definición; spatstat lo aproxima con píxeles al calcular K.
# ---------------------------------------------------------------------
W_URB <- Window(p_urb)
solape <- function(dx, dy) area.owin(intersect.owin(W_URB, shift(W_URB, c(dx, dy)))) / area.owin(W_URB)
N_TRASL <- list(
  modulo = "cap4.m10", d_corta_m = 100, d_larga_m = 1000,
  frac_este_100 = r10(100 * solape(100, 0)), frac_norte_100 = r10(100 * solape(0, 100)),
  frac_este_1000 = r10(100 * solape(1000, 0))
)
N_TRASL$peso_este_100 <- r10(100 / N_TRASL$frac_este_100)
N_TRASL$peso_norte_100 <- r10(100 / N_TRASL$frac_norte_100)
N_TRASL$peso_este_1000 <- r10(100 / N_TRASL$frac_este_1000)
# La fracción como proporción: un distractor la toma por el peso (el error de
# invertir |W| / |W ∩ (W + v)|).
N_TRASL$prop_este_1000 <- r10(N_TRASL$frac_este_1000 / 100)
if (!(N_TRASL$peso_este_100 > 1.001 && abs(N_TRASL$peso_este_100 - N_TRASL$peso_norte_100) > 1e-4 &&
      N_TRASL$peso_este_1000 > N_TRASL$peso_este_100))
  para("A10: el peso de traslación ya no es mayor que 1, distinto por dirección y creciente con la distancia")
# Lo que hace falsa la opción c de A10: la pareja norte-sur pesa menos que la
# este-oeste, y la ciudad es más larga de norte a sur.
if (!(N_TRASL$peso_norte_100 < N_TRASL$peso_este_100 && diff(W_URB$yrange) > diff(W_URB$xrange)))
  para("A10: la pareja norte-sur ya no pesa menos, o la ciudad ya no es más larga de norte a sur")

# ---------------------------------------------------------------------
# A5 · El rebarajado empata a 5 × 5 y deja de empatar a 10 × 10 (4.5)
#
# Las coordenadas son las que publicó el capítulo 4 (m5.x1…y2), así que no
# se vuelve a rebarajar nada: se lee el patrón que el estudiante vio.
# ---------------------------------------------------------------------
m5 <- CAPS$cap4$m5
W5 <- owin(c(0, 1), c(-1, 0))
p_orig <- ppp(unlist(m5$x1), unlist(m5$y1), window = W5)
p_reb  <- ppp(unlist(m5$x2), unlist(m5$y2), window = W5)
chi <- function(p, k) as.numeric(suppressWarnings(quadrat.test(p, nx = k, ny = k))$statistic)
N_REB <- list(
  modulo = "cap4.m5",
  chi2_5_orig = r10(chi(p_orig, 5)), chi2_5_reb = r10(chi(p_reb, 5)),
  chi2_10_orig = r10(chi(p_orig, 10)), chi2_10_reb = r10(chi(p_reb, 10)),
  gl_10 = 99L
)

# ---------------------------------------------------------------------
# A11 · El nrank que da un contraste al 5 % con nsim = 199 (4.11)
#
# 199 no aparece en ningún documento del curso, y por eso sirve: la regla
# 2k/(nsim+1) se aplica, no se recuerda.
# ---------------------------------------------------------------------
NS <- 199L; NIVEL <- 0.05
N_NRANK <- list(
  modulo = "cap4.m11", nsim = NS, nivel = NIVEL, nivel_pct = 100 * NIVEL, decimales = 0,
  correcto = (NS + 1) * NIVEL / 2,
  nivel_defecto = 2 / (NS + 1),
  nivel_defecto_pct = 100 * 2 / (NS + 1),
  p_minimo = 1 / (NS + 1),
  distractores = list(
    list(id = "una_cola", valor = (NS + 1) * NIVEL,
         error = "olvidar que la banda tiene dos lados: el nivel puntual cuenta la k-ésima más baja Y la k-ésima más alta"),
    list(id = "defecto", valor = 1,
         error = "quedarse con el rango por defecto, que con 199 simulaciones da un contraste al 1 %, no al 5 %")
  )
)

# ---------------------------------------------------------------------
# B3 · La pared de bw.ppl en un rectángulo de 3 × 4 km (5.3)
#
# El tope es la mitad del diámetro de la ventana, y el diámetro de un
# rectángulo es su diagonal. Además se comprueba que chocar NO es una
# rareza: sobre patrones de CSR en ese rectángulo, bw.ppl choca a menudo,
# porque para un patrón sin estructura la mejor intensidad es una
# constante y el criterio sigue mejorando al abrir el núcleo.
# ---------------------------------------------------------------------
W_RECT <- owin(c(0, 3000), c(0, 4000))
LAM_TOPE_KM2 <- 20
choques <- vapply(1:20, function(s) {
  set.seed(SEMILLA + s)
  X <- rpoispp(LAM_TOPE_KM2 / 1e6, win = W_RECT)
  aviso <- NA_character_
  v <- withCallingHandlers(as.numeric(bw.ppl(X)),
    warning = function(w) { aviso <<- conditionMessage(w); invokeRestart("muffleWarning") })
  c(v, !is.na(aviso) && grepl("end of interval", aviso, fixed = TRUE), npoints(X))
}, numeric(3))
set.seed(SEMILLA)
# Los que NO chocan también se publican: «el selector se va al mayor σ que le
# dejan» era cierto en 11 de 20 y falso en los otros 9, que devuelven un
# ancho finito (la auditoría de verdad de la ronda 4 lo midió).
en_tope <- abs(choques[1, ] - diameter(W_RECT) / 2) < 1e-6 & choques[2, ] == 1
N_TOPE <- list(
  modulo = "cap5.m3", lado_x_m = 3000, lado_y_m = 4000, decimales = 0,
  correcto = diameter(W_RECT) / 2,
  csr_lambda_km2 = LAM_TOPE_KM2,
  csr_puntos_esperados = LAM_TOPE_KM2 * area.owin(W_RECT) / 1e6,
  csr_puntos_media = r10(mean(choques[3, ])),
  csr_realizaciones = ncol(choques),
  csr_chocan = as.integer(sum(choques[2, ])),
  csr_chocan_en_el_tope = as.integer(sum(en_tope)),
  csr_no_chocan = as.integer(sum(!en_tope)),
  csr_sigma_min_m = r10(min(choques[1, !en_tope])),
  csr_sigma_max_m = r10(max(choques[1, !en_tope])),
  distractores = list(
    list(id = "mitad_lado_mayor", valor = 4000 / 2,
         error = "tomar la mitad del lado mayor: el diámetro de una ventana es la mayor distancia entre dos de sus puntos, y en un rectángulo es la diagonal"),
    list(id = "mitad_lado_menor", valor = 3000 / 2,
         error = "tomar la mitad del lado menor, que es el tope de otra cosa: el cuarto del lado corto es lo que limita a Kest"),
    list(id = "diagonal_entera", valor = diameter(W_RECT),
         error = "tomar la diagonal entera en vez de su mitad")
  )
)

# ---------------------------------------------------------------------
# B6 · De la probabilidad de caso al riesgo relativo (5.6)
# ---------------------------------------------------------------------
pmax_ch <- val("c5m6_ch_pmax")
N_RR <- list(
  modulo = "cap5.m6", p = pmax_ch, decimales = 2,
  correcto = pmax_ch / (1 - pmax_ch),
  distractores = list(
    list(id = "contra_global", valor = pmax_ch / val("c5m6_ch_global"),
         error = "dividir por la proporción global: eso dice cuántas veces la proporción local supera a la de la comarca, que es otra pregunta"),
    list(id = "al_reves", valor = (1 - pmax_ch) / pmax_ch,
         error = "invertir el cociente: es el riesgo relativo de los controles contra los casos"),
    list(id = "la_misma", valor = pmax_ch,
         error = "creer que la probabilidad de caso y el riesgo relativo son la misma escala")
  )
)

# ---------------------------------------------------------------------
# B1 y B8 · Kennedy, la ventana del capítulo 5
#
# Se rehace el patrón de Kennedy con la geometría de la localidad, como
# genera_cap5.R, y se ancla contra lo que publicó el capítulo.
# ---------------------------------------------------------------------
locs <- st_read(file.path(PROC, "bogota_localidades.gpkg"), quiet = TRUE)
W_KEN <- as.owin(st_union(st_geometry(locs[locs$localidad == "Kennedy", ])))
p_ken <- suppressWarnings(ppp(XY[, 1], XY[, 2], window = W_KEN))
if (npoints(p_ken) != val("c5m1_n_ken")) para("Kennedy ya no tiene las sedes que publica el capítulo 5")
if (abs(area.owin(W_KEN) / 1e6 - val("c5m1_area_ken")) > 1e-6) para("Kennedy ya no mide lo que publica el capítulo 5")

# B1 · Con σ enorme, la KDE corregida tiende a n/|W|. Es la pregunta del
# 5.1 —contar con una vecindad que crece hasta abarcarlo todo es contar
# todo y dividir por toda el área— y se comprueba, no se afirma: con
# σ = 1 000 km la superficie corregida es plana en n/|W| (a la precisión de
# la rejilla de 256 × 256). La de sin corregir NO se cita: en spatstat no
# tiende a cero, sino a n entre el área del marco con su relleno de la FFT
# (1.14 sedes por km² en Kennedy), que es un artefacto de la
# discretización y no la lección.
SIG_GRANDE <- 1e6
d_corr <- density(p_ken, sigma = SIG_GRANDE, dimyx = 256)
N_LIMITE <- list(
  modulo = "cap5.m1", sigma_m = SIG_GRANDE,
  corregida_min_km2 = r10(min(d_corr) * 1e6), corregida_max_km2 = r10(max(d_corr) * 1e6)
)
if (abs(N_LIMITE$corregida_min_km2 / val("c5m1_lambda_ken") - 1) > 1e-3 ||
    abs(N_LIMITE$corregida_max_km2 / val("c5m1_lambda_ken") - 1) > 1e-3)
  para("B1: con σ enorme la KDE corregida ya no es plana en n/|W|")

# B8 · La identidad del intercepto, con la cuadratura dentro. Sin
# covariables, `ppm` usa la fórmula cerrada n/|W| y no pasa por Berman y
# Turner (lo destapó M3 de la segunda revisión del capítulo 5); con
# `forcefit = TRUE` sí, y entonces lo que iguala n es la SUMA de la
# cuadratura: λ̂·Σw = n, así que λ̂ = n/Σw. Es el cálculo del módulo 8
# sobre la ciudad (5.71211 con 368.86563 km²) llevado a otra ventana. La
# versión anterior preguntaba ∫λ̂ con n en el enunciado, y la respuesta era
# ese mismo número: se acertaba sin derivar nada (ronda 4 de la auditoría).
f_forz <- ppm(p_ken ~ 1, forcefit = TRUE)
suma_w_ken <- sum(w.quad(quad.ppm(f_forz)))
lam_forz <- exp(coef(f_forz))[[1]]
lam_cerr <- exp(coef(ppm(p_ken ~ 1)))[[1]]
if (abs(lam_forz * suma_w_ken - npoints(p_ken)) > 1e-6)
  para("B8: con forcefit, λ̂·Σw ya no es n")
if (abs(lam_cerr * area.owin(W_KEN) - npoints(p_ken)) > 1e-6)
  para("B8: sin forcefit, ppm(~1) ya no da n/|W|")
N_FORZADO <- list(
  modulo = "cap5.m8", n = npoints(p_ken), decimales = 3,
  area_km2 = r10(area.owin(W_KEN) / 1e6), suma_pesos_km2 = r10(suma_w_ken / 1e6),
  sin_contar_km2 = r10((area.owin(W_KEN) - suma_w_ken) / 1e6),
  correcto = r10(lam_forz * 1e6),
  distractores = list(
    list(id = "formula_cerrada", valor = r10(lam_cerr * 1e6),
         error = "dividir por el área de la ventana: es la fórmula cerrada, la que ppm usa sin forcefit, pero la cuadratura no reparte el área entera")
  )
)

# ---------------------------------------------------------------------
# C5 · El efecto de diseño de otro ajuste (5.11, con el cap. 1 detrás)
#
# El capítulo publica el tamaño efectivo para Thomas con la K de
# traslación. Aquí se pide para Matérn con la isotrópica: hay que saber
# que el efecto de diseño es el cuadrado del cociente de errores.
# ---------------------------------------------------------------------
infl_m <- val("c5m11_mat_iso_inf"); n_bog <- val("c5m11_n")
N_NEFF <- list(
  modulo = "cap5.m11", inflacion = infl_m, n = n_bog, decimales = 1,
  efecto_diseno = r10(infl_m^2),
  correcto = n_bog / infl_m^2,
  distractores = list(
    list(id = "sin_cuadrado", valor = n_bog / infl_m,
         error = "dividir por el cociente de errores estándar sin elevarlo al cuadrado: el efecto de diseño compara varianzas"),
    list(id = "el_de_thomas", valor = val("c5m11_neff"),
         error = "copiar el tamaño efectivo que el capítulo publica para Thomas con la K de traslación, que es otro ajuste")
  )
)

# C3 · los niveles puntuales de las dos bandas, en porcentaje. La del
# capítulo 4 es un intervalo central de probabilidad `nivel` en cada r, así
# que contrasta al 1 − nivel; la del 5 es el mínimo y el máximo, al
# 2/(nsim+1). La pregunta los compara en la misma unidad.
# La del 5 ya viene en porcentaje en el capítulo (`c5m10_nivel`) y se cita
# de ahí: copiarla aquí dejaba el original sin leer.
N_NIVELES <- list(
  modulo = "cap5.m10",
  cap4_pct = r10(100 * (1 - val("c4m11_nivel"))),
  cap4_cobertura_pct = r10(100 * val("c4m11_nivel"))
)

# B11 · Las escalas de Thomas y de Matérn no son la misma magnitud. La de
# Thomas es la desviación típica de una gaussiana por eje y la de Matérn el
# radio de un disco: pasadas a la distancia media de un punto hijo a su
# centro —σ·√(π/2) y 2R/3— salen casi iguales, aunque la tabla del capítulo
# ponga 932 m contra 1 782 m. Es el distractor que la auditoría del experto
# encontró defendible cuando hablaba de «los parámetros» sin más.
th_esc <- val("c5m11_th_iso_esc"); mat_esc <- val("c5m11_mat_iso_esc")
N_ESCALAS <- list(
  modulo = "cap5.m11",
  thomas_media_m = r10(th_esc * sqrt(pi / 2)), matern_media_m = r10(2 * mat_esc / 3),
  razon_escalas = r10(mat_esc / th_esc),
  dif_media_pct = r10(100 * abs(2 * mat_esc / 3 - th_esc * sqrt(pi / 2)) / (th_esc * sqrt(pi / 2))),
  dif_mu_pct = r10(100 * abs(val("c5m11_mat_iso_mu") - val("c5m11_th_iso_mu")) / val("c5m11_th_iso_mu"))
)
if (!(N_ESCALAS$razon_escalas > 1.5 && N_ESCALAS$dif_media_pct < 5 && N_ESCALAS$dif_mu_pct < 1))
  para("B11: las escalas de Thomas y Matérn ya no dicen «casi el doble en la tabla, casi lo mismo en distancia»")

# El catálogo (E4): de los rechazos de las secuoyas en el barrido, cuántos
# salen de rejillas en que alguna celda espera menos de 5. La cifra cruda,
# «9 de 10 rechazan», leída sola sugería un rechazo robusto.
rw <- CAPS$cap4$m6$redwood
rw_rech <- unlist(rw$rechaza); rw_emin <- unlist(rw$esperanza_min); rw_nx <- unlist(rw$nx)
if (sum(rw_rech) != val("c4m6_red_rechazos")) para("los rechazos de las secuoyas no cuadran con el capítulo")
N_SUPUESTO_RW <- list(
  modulo = "cap4.m6",
  rechazos_sin_supuesto = as.integer(sum(rw_rech & rw_emin < 5)),
  rechazos_con_supuesto = as.integer(sum(rw_rech & rw_emin >= 5)),
  nx_con_supuesto = as.list(rw_nx[rw_rech & rw_emin >= 5]),
  nx_no_rechaza_con_supuesto = as.list(rw_nx[!rw_rech & rw_emin >= 5])
)
if (length(N_SUPUESTO_RW$nx_con_supuesto) < 1 || length(N_SUPUESTO_RW$nx_no_rechaza_con_supuesto) < 1)
  para("C4: entre las rejillas de las secuoyas que respetan el supuesto ya no hay una que rechace y otra que no")

# A7 · G y F sobre los pinos suecos (4.7). El módulo lee G frente a F con
# tres medianas —la de G, la de F y la que tendrían las dos bajo CSR— sobre
# células, pinos japoneses y secuoyas; aquí la misma lectura sobre un patrón
# que el módulo 7 no usa. Las mismas funciones del capítulo (puntual.R): la
# mediana de G es la de las distancias al vecino, la de F se interpola en
# la F por muestra reducida, y la J va por muestra reducida en las dos y
# solo donde F <= 0.9, como en el capítulo.
X_SW <- rescale(swedishpines, 10, "m")
f_sw <- Fest(X_SW, correction = "km")
rg_sw <- ppp_rejilla_r(f_sw, 101L)
fb_sw <- ppp_F_borde(X_SW, rg_sw)
i5 <- which(fb_sw$f >= 0.5)[1]
f_med_sw <- rg_sw[i5 - 1] + (0.5 - fb_sw$f[i5 - 1]) * (rg_sw[i5] - rg_sw[i5 - 1]) / (fb_sw$f[i5] - fb_sw$f[i5 - 1])
hasta_sw <- max(which(fb_sw$f <= val("c4m7_umbral_f")))
j_sw <- (1 - ppp_G_borde(X_SW, rg_sw)[seq_len(hasta_sw)]) / (1 - fb_sw$f[seq_len(hasta_sw)])
k_sw <- 2:hasta_sw
N_GF <- list(
  modulo = "cap4.m7", n = npoints(X_SW),
  lado_x_m = diff(Window(X_SW)$xrange), lado_y_m = diff(Window(X_SW)$yrange),
  g_mediana_m = r10(unname(quantile(nndist(X_SW), 0.5))),
  f_mediana_m = r10(f_med_sw),
  csr_mediana_m = r10(sqrt(log(2) / (intensity(X_SW) * pi))),
  j_sobre_1 = as.integer(sum(j_sw[k_sw] > 1)), j_nodos = length(k_sw)
)
if (!(N_GF$g_mediana_m > N_GF$csr_mediana_m && N_GF$csr_mediana_m > N_GF$f_mediana_m))
  para("A7: los pinos suecos ya no tienen G tarde y F pronto")
if (N_GF$j_sobre_1 < 0.8 * N_GF$j_nodos) para("A7: la J de los pinos suecos ya no queda casi toda sobre 1")

# B9 · El coeficiente de xc leído en su escala: cada kilómetro hacia el este
# multiplica λ por e^β. Ninguna pregunta pedía la lectura multiplicativa
# (auditoría de pertinencia, ronda 4).
N_EBETA <- list(
  modulo = "cap5.m9",
  factor_por_km = r10(exp(val("c5m9_xc"))),
  pct_por_km = r10(100 * (1 - exp(val("c5m9_xc"))))
)

# B10 y C1 · Qué intensidad divide la K inhomogénea del capítulo 5. Su
# `envelope(f_centr, Kinhom)` no pasa `lambda`, y entonces Kinhom estima λ̂
# en cada patrón —el dato y cada simulación— por núcleo, sin el punto y con
# el σ por defecto de density.ppp: un octavo del lado corto del rectángulo
# que encierra la ventana. Lo destapó la auditoría de verdad de la ronda 4;
# aquí se comprueba contra la curva publicada, y el σ se exporta para que
# las retros lo digan en vez de atribuirle al gradiente lo que hace el
# núcleo. Es un defecto del capítulo, anotado para Javier.
SIG_KINH <- min(sidelengths(Frame(W_URB))) / 8
lam_nuc <- density(p_urb, sigma = SIG_KINH, at = "points", leaveoneout = TRUE)
k_def <- Kinhom(p_urb, correction = "translate")
k_nuc <- Kinhom(p_urb, lambda = lam_nuc, correction = "translate")
rg_c5 <- unlist(CAPS$cap5$m10$curva$r)
obs_c5 <- unlist(CAPS$cap5$m10$curva$obs)
ok_r <- rg_c5 > 0
# Interpolada como la publica el capítulo (ppp_curva, de puntual.R).
obs_def <- ppp_curva(k_def, PPP_CORR_COL, rg_c5)
obs_nuc <- ppp_curva(k_nuc, PPP_CORR_COL, rg_c5)
dif_def <- max(abs(obs_def[ok_r] / obs_c5[ok_r] - 1))
dif_nuc <- max(abs(obs_nuc[ok_r] / obs_c5[ok_r] - 1))
if (dif_def > 1e-6) para("B10/C1: la curva del capítulo 5 ya no es la Kinhom por defecto")
if (dif_nuc > 1e-6) para("B10/C1: el σ por defecto de Kinhom ya no es el que se publica")
N_KINH <- list(modulo = "cap5.m10", sigma_nucleo_m = r10(SIG_KINH))

# C2 · la isotrópica y la de traslación no dan la misma K: la mayor
# diferencia entre las dos curvas del módulo 10 del capítulo 4, en
# porcentaje, y el radio donde cae. Sin el r = 0, donde la de traslación vale
# 0. La retro de C02 la necesita para refutar «todas dan la misma curva» con
# dos correcciones y no con la K sin corregir (verdad, ronda 5).
corr_m10 <- CAPS$cap4$m10$correcciones
k_m10 <- function(nm) unlist(Filter(function(x) x$correccion == nm, corr_m10)[[1]]$k)
k_iso_m10 <- k_m10("isotropic"); k_tr_m10 <- k_m10("translate"); r_m10 <- unlist(CAPS$cap4$m10$r)
ok_m10 <- k_tr_m10 > 0
dif_m10 <- abs(k_iso_m10[ok_m10] / k_tr_m10[ok_m10] - 1)
N_ISO_TR <- list(modulo = "cap4.m10", max_dif_pct = r10(100 * max(dif_m10)),
                 r_max_dif_m = r10(r_m10[ok_m10][which.max(dif_m10)]))
if (!(N_ISO_TR$max_dif_pct > 1 && N_ISO_TR$max_dif_pct < val("c4m10_sesgo")))
  para("C2: la diferencia entre isotrópica y traslación ya no es pequeña frente al sesgo sin corregir")

NUEVO <- list(resto_dc = N_RESTO, limite = N_LIMITE, ce_ventana = N_CE, denso = N_DENSO, rebarajado = N_REB,
              traslacion = N_TRASL, nrank = N_NRANK, tope_ppl = N_TOPE, niveles = N_NIVELES,
              riesgo_relativo = N_RR, forzado = N_FORZADO, escalas = N_ESCALAS,
              n_efectivo = N_NEFF, supuesto_rw = N_SUPUESTO_RW, gf_suecos = N_GF,
              ebeta = N_EBETA, kinhom_nucleo = N_KINH, iso_tras = N_ISO_TR)

for (nm in names(NUEVO)) {
  item <- NUEVO[[nm]]
  if (is.null(item$distractores)) next
  etiquetas <- c("correcto", vapply(item$distractores, function(x) x$id, ""))
  valores <- c(item$correcto, vapply(item$distractores, function(x) x$valor, numeric(1)))
  red <- round(valores, item$decimales)
  if (any(duplicated(red))) {
    i <- which(duplicated(red))[1]; j <- which(red == red[i])[1]
    para("DISTRACTOR INDISTINGUIBLE · ", nm, ": «", etiquetas[j], "» y «", etiquetas[i],
         "» valen los dos ", red[i], " con ", item$decimales, " decimal(es)")
  }
}
message(sprintf("  %d cálculos nuevos para las preguntas", length(NUEVO)))

# =====================================================================
# LOS CINCO EJERCICIOS: EL ORO DE MURCHISON
#
# Cada respuesta se ancla a un trozo LITERAL de su enunciado (`pide`), y la
# página lo pinta como encabezado. Si alguien reescribe el enunciado, la
# respuesta se queda sin ancla y esto se para. `sin_contestar()` mira el
# otro lado: que toda demanda —«di», «explica», «contesta», «compara»,
# «decide» y cada «¿»— caiga dentro de alguna respuesta. Es la maquinaria
# de genera_soluciones.R tras M5 de la segunda revisión del capítulo 5,
# con «decide» añadido porque estos ejercicios terminan en una decisión.
#
# Y las cifras de las respuestas se escriben AQUÍ, en R, con `f()` y
# `fe()`: el auditor exige que todo número de una respuesta esté entre los
# valores del JSON, así que una cifra a mano en la prosa de un ejercicio
# no llega a publicarse.
# =====================================================================
responde <- function(enunciado, pide, respuesta) {
  if (!grepl(pide, enunciado, fixed = TRUE))
    para("una respuesta no encuentra su pregunta en el enunciado: «", pide, "»")
  list(pide = pide, respuesta = respuesta)
}
DEMANDA <- "(*UCP)(?<!\\p{L})(?:[Dd]i|[Ee]xplica|[Cc]ontesta|[Cc]ompara|[Dd]ecide)(?!\\p{L})|¿"
sin_contestar <- function(e) {
  en <- e$enunciado
  ini <- vapply(e$solucion$respuestas, function(r)
    as.integer(regexpr(r$pide, en, fixed = TRUE)), integer(1))
  fin <- ini + vapply(e$solucion$respuestas, function(r) nchar(r$pide), integer(1)) - 1L
  m <- gregexpr(DEMANDA, en, perl = TRUE)[[1]]
  largo <- attr(m, "match.length")
  fuera <- character(0)
  for (i in seq_along(m)) {
    if (m[i] < 0) break
    dentro <- any(ini <= m[i] & m[i] <= fin)
    # «contesta: ¿…?» — la demanda que presenta a otra queda contestada si
    # una respuesta empieza detrás de ella en la misma frase (la regla de
    # genera_soluciones.R, que la primera versión de este archivo perdió).
    tras <- substr(en, m[i] + largo[i], m[i] + largo[i])
    if (!dentro && tras == ":") {
      resto <- ini[ini > m[i]]
      dentro <- length(resto) > 0 &&
        !grepl(".", substr(en, m[i], min(resto)), fixed = TRUE)
    }
    if (!dentro) fuera <- c(fuera, substr(en, m[i], m[i] + largo[i] + 30L))
  }
  fuera
}
# El signo menos tipográfico y los miles con espacio fino, como en el resto
# del material: la prosa de los ejercicios decía «de -4.82 a -0.94» y
# «7045.91» (redacción, ronda 5).
f  <- function(x, d) sub("^-", "−", formatC(x, format = "f", digits = d, big.mark = " "))
fe <- function(x) formatC(round(x), format = "d", big.mark = " ")

data(murchison)
ORO    <- rescale(murchison$gold, 1000, "km")
FALLAS <- rescale(murchison$faults, 1000, "km")
GS     <- rescale(murchison$greenstone, 1000, "km")
W_ORO  <- Window(ORO)
if (!is.rectangle(W_ORO)) para("la ventana de murchison ya no es un rectángulo y el E1 lo dice")
N_ORO <- npoints(ORO)
D_FALLA <- distfun(FALLAS)
G_IND <- function(x, y) as.numeric(inside.owin(x, y, GS))

# Exportar lo que el auditor necesita para rehacer en Python lo que se
# pueda: los puntos, los segmentos y el polígono, en kilómetros.
write.csv(data.frame(x = ORO$x, y = ORO$y),
          file.path(SALIDAS, "preparcial2_murchison_oro.csv"), row.names = FALSE)
write.csv(as.data.frame(FALLAS)[, c("x0", "y0", "x1", "y1")],
          file.path(SALIDAS, "preparcial2_murchison_fallas.csv"), row.names = FALSE)
write.csv(data.frame(xmin = W_ORO$xrange[1], xmax = W_ORO$xrange[2],
                     ymin = W_ORO$yrange[1], ymax = W_ORO$yrange[2]),
          file.path(SALIDAS, "preparcial2_murchison_ventana.csv"), row.names = FALSE)
# El greenstone viaja como anillos sueltos —pieza, si es agujero, orden y
# coordenadas— y no como GeoJSON: escribirlo con sf obliga a inventarle un
# CRS que no tiene, y el auditor lo reconstruye igual con shapely (la unión
# de las piezas menos la de los agujeros, que es lo que spatstat entiende
# por una ventana poligonal).
anillos <- do.call(rbind, lapply(seq_along(GS$bdry), function(i) {
  b <- GS$bdry[[i]]
  data.frame(anillo = i, agujero = spatstat.utils::is.hole.xypolygon(b),
             orden = seq_along(b$x), x = b$x, y = b$y)
}))
write.csv(anillos, file.path(SALIDAS, "preparcial2_murchison_greenstone.csv"), row.names = FALSE)

EJ <- list()

# ---------------------------------------------------------------------
# E1 · Dónde se buscó el oro (4.1, 4.2, 4.5, 4.6)
# ---------------------------------------------------------------------
A_RECT <- area.owin(W_ORO); A_GS <- area.owin(GS)
n_gs <- sum(inside.owin(ORO$x, ORO$y, GS))
lam_rect <- N_ORO / A_RECT; lam_gs <- n_gs / A_GS
lam_fuera <- (N_ORO - n_gs) / (A_RECT - A_GS)
cociente_gs <- lam_gs / lam_fuera
KS <- 2:10
qt <- lapply(KS, function(k) {
  t <- suppressWarnings(quadrat.test(ORO, nx = k, ny = k))
  list(k = k, chi2 = r10(as.numeric(t$statistic)), gl = as.integer(t$parameter),
       p = signif(t$p.value, 6), log10_p = r10(log10(t$p.value)),
       esperanza_min = r10(min(t$expected)), celdas_baja = sum(t$expected < 5))
})
emin <- vapply(qt, function(z) z$esperanza_min, numeric(1))
pvals <- vapply(qt, function(z) z$p, numeric(1))
respetan <- KS[emin >= 5]
if (!all(pvals < 0.05)) para("E1: alguna rejilla ya no rechaza y la respuesta dice que todas")
# La respuesta dice que sobre un rectángulo el supuesto se rompe DE UNA VEZ:
# que las que lo respetan son las primeras, sin huecos.
if (!length(respetan) || !identical(respetan, KS[seq_along(respetan)]))
  para("E1: las rejillas que respetan el supuesto ya no son un tramo inicial: ",
       paste(respetan, collapse = ", "))
k_rompe <- KS[length(respetan) + 1L]
emin_rompe <- emin[length(respetan) + 1L]
# «Fuera del greenstone» por la resta de ventanas pierde un yacimiento: el
# que está justo sobre el borde derecho del rectángulo, y que el polígono de
# setminus.owin deja fuera. El enunciado fija el convenio (255 menos los de
# dentro) y la respuesta enseña la trampa, con el yacimiento identificado.
W_FUERA <- setminus.owin(W_ORO, GS)
dentro_gs <- inside.owin(ORO$x, ORO$y, GS)
en_fuera <- inside.owin(ORO$x, ORO$y, W_FUERA)
perdidos <- which(!dentro_gs & !en_fuera)
n_resta <- sum(en_fuera)
if (length(perdidos) != 1L || n_resta != N_ORO - n_gs - 1L)
  para("E1: setminus.owin ya no pierde exactamente un yacimiento, y la respuesta lo cuenta")
if (abs(ORO$x[perdidos] - W_ORO$xrange[2]) > 1e-9)
  para("E1: el yacimiento perdido ya no está sobre el borde derecho del rectángulo")
cociente_resta <- lam_gs / (n_resta / area.owin(W_FUERA))

# La respuesta dice que el greenstone basta para rechazar aunque el oro no se
# atrajera nada. Se comprueba en vez de afirmarlo: un Poisson que SOLO sabe
# del greenstone —su λ dentro y la de fuera fuera, sin ninguna atracción—
# también hace rechazar al test de cuadrantes con cada rejilla defendible. Y
# el χ² del oro de verdad supera al de todas las simulaciones: algo queda que
# el greenstone no explica, que es lo que mide el ejercicio 5 (auditoría de
# los ejercicios, ronda 4).
NSIM_E1 <- 99L
set.seed(SEMILLA)
lam_pieza <- function(x, y) ifelse(inside.owin(x, y, GS), lam_gs, lam_fuera)
sim_e1 <- replicate(NSIM_E1, {
  X <- rpoispp(lam_pieza, lmax = lam_gs, win = W_ORO)
  vapply(respetan, function(k) {
    tq <- suppressWarnings(quadrat.test(X, nx = k, ny = k))
    c(as.numeric(tq$statistic), tq$p.value)
  }, numeric(2))
}, simplify = "array")
chi_sim <- matrix(sim_e1[1, , ], nrow = length(respetan))
p_sim <- matrix(sim_e1[2, , ], nrow = length(respetan))
rech_e1 <- rowSums(p_sim < 0.05)
chi_med_e1 <- apply(chi_sim, 1, median)
chi_obs_e1 <- vapply(respetan, function(k) qt[[which(KS == k)]]$chi2, numeric(1))
if (any(rech_e1 < NSIM_E1)) para("E1: el Poisson del greenstone ya no hace rechazar en todas las simulaciones")
if (!all(chi_obs_e1 > apply(chi_sim, 1, max))) para("E1: el χ² del oro ya no supera a todas las simulaciones")
K_EJ_E1 <- 5L
if (!K_EJ_E1 %in% respetan) para("E1: la rejilla de ejemplo ya no respeta el supuesto")
set.seed(SEMILLA)

en1 <- paste(
  "Los 255 yacimientos de oro de `murchison$gold` vienen en metros. Pásalos a",
  "kilómetros, y lo mismo las fallas y el greenstone, con los nombres que usan los",
  "cinco ejercicios: `oro <- rescale(murchison$gold, 1000, \"km\")`,",
  "`fallas <- rescale(murchison$faults, 1000, \"km\")` y",
  "`greenstone <- rescale(murchison$greenstone, 1000, \"km\")`. Estima la",
  "intensidad del oro con dos ventanas —el rectángulo de la prospección,",
  "`Window(oro)`, y el afloramiento de greenstone— y di cuántos yacimientos caen",
  "en cada una. Calcula también el cociente entre la intensidad dentro y fuera",
  "del greenstone; la de fuera se calcula con los 255 menos los de dentro, sobre el",
  "área del rectángulo menos la del greenstone. Aplica después el test de cuadrantes sobre el rectángulo con",
  "rejillas de 2 × 2 a 10 × 10 y anota el χ², el p-valor y la esperanza mínima",
  "de sus celdas. ¿Qué rejillas sostienen un rechazo que se pueda defender? Y",
  "contesta: ¿dice ese rechazo que el oro se agrupa?")
if (!grepl(as.character(N_ORO), en1, fixed = TRUE)) para("E1: el enunciado ya no dice cuántos yacimientos hay")
EJ$e1 <- list(
  titulo = "Dónde se buscó el oro",
  modulos = list("cap4.m1", "cap4.m2", "cap4.m4", "cap4.m5", "cap4.m6"),
  enunciado = en1,
  # Las nueve rejillas no van en `pasos` sino en `cuadrantes`: la página las
  # pinta como una tabla propia, con una columna por magnitud, porque meter
  # χ², p y esperanza mínima en una sola celda las hacía ilegibles.
  pasos = list(
    list(paso = "Yacimientos en el rectángulo", valor = N_ORO),
    list(paso = "Área del rectángulo (km²)", valor = r10(A_RECT)),
    list(paso = "λ en el rectángulo (por km²)", valor = r10(lam_rect)),
    list(paso = "Yacimientos dentro del greenstone", valor = n_gs),
    list(paso = "Área del greenstone (km²)", valor = r10(A_GS)),
    list(paso = "λ en el greenstone (por km²)", valor = r10(lam_gs)),
    list(paso = "λ fuera del greenstone (por km²)", valor = r10(lam_fuera)),
    list(paso = "Cociente dentro / fuera", valor = r10(cociente_gs))),
  solucion = list(
    n = N_ORO, n_gs = n_gs, area_rect = r10(A_RECT), area_gs = r10(A_GS),
    pct_area_gs = r10(100 * A_GS / A_RECT), pct_oro_gs = r10(100 * n_gs / N_ORO),
    lambda_rect = r10(lam_rect), lambda_gs = r10(lam_gs), lambda_fuera = r10(lam_fuera),
    cociente = r10(cociente_gs), cuadrantes = qt, respetan = respetan,
    n_fuera_resta = n_resta, yacimiento_perdido = perdidos, x_perdido_km = r10(ORO$x[perdidos]),
    x_max_km = r10(W_ORO$xrange[2]), cociente_resta = r10(cociente_resta),
    k_rompe = k_rompe, esperanza_min_rompe = emin_rompe,
    nsim_greenstone = NSIM_E1, rechazos_greenstone = as.list(rech_e1),
    chi2_mediana_greenstone = as.list(r10(chi_med_e1)), rejilla_ejemplo = K_EJ_E1,
    respuestas = list(
      responde(en1, "di cuántos yacimientos caen en cada una",
        sprintf(paste(
          "En el rectángulo caen los %d, que es lo que lo define: la prospección se hizo ahí.",
          "En el greenstone caen %d —el %s %%— sobre el %s %% del área. Las dos λ, %s y %s",
          "yacimientos por km², son correctas y no son la misma cifra: cada una vale solo con",
          "su ventana. Y una trampa al contar los de fuera: si los cuentas sobre",
          "`setminus.owin(Window(oro), greenstone)` te salen %d y no %d, y el cociente sube a",
          "%s. El yacimiento %d está justo sobre el borde derecho del rectángulo, en x = %s km, y",
          "el polígono de la resta lo deja fuera. Un punto sobre el borde de una ventana es una",
          "decisión, como las sedes de Kennedy del capítulo 5: por eso el enunciado fija el",
          "convenio."),
          N_ORO, n_gs, f(100 * n_gs / N_ORO, 1), f(100 * A_GS / A_RECT, 1),
          f(lam_rect, 5), f(lam_gs, 5), n_resta, N_ORO - n_gs, f(cociente_resta, 2),
          perdidos, f(ORO$x[perdidos], 4))),
      responde(en1, "¿Qué rejillas sostienen un rechazo que se pueda defender?",
        sprintf(paste(
          "Las nueve rechazan, pero solo se defienden las de %d × %d a %d × %d: son las únicas",
          "en que ninguna celda espera menos de 5 yacimientos. Con la de %d × %d la celda más",
          "pobre ya espera %s, y desde ahí el p-valor sale de una aproximación que no vale,",
          "por pequeño que sea. Sobre un rectángulo todas las celdas miden lo mismo, así que",
          "afinar baja a la vez la esperanza de todas y el supuesto se rompe de una vez: aquí",
          "sí se puede decir «desde la rejilla %d × %d, el supuesto no se cumple». Sobre la",
          "ventana urbana de Bogotá, que recorta las celdas del borde, no se podía."),
          min(respetan), min(respetan), max(respetan), max(respetan),
          k_rompe, k_rompe, f(emin_rompe, 2), k_rompe, k_rompe)),
      responde(en1, "¿dice ese rechazo que el oro se agrupa?",
        sprintf(paste(
          "No. La nula del test es el Poisson homogéneo entero —λ constante y puntos",
          "independientes—, y aquí la primera mitad falla a la vista: el greenstone, con el",
          "%s %% del área, tiene el %s %% de los yacimientos, y su intensidad es %s veces la",
          "de fuera. Eso basta para rechazar aunque los yacimientos no se atrajeran nada, y",
          "no hace falta creerlo: en %d simulaciones de un Poisson que solo sabe del",
          "greenstone —su λ dentro, la de fuera fuera, ninguna atracción—, el test rechaza",
          "las %d veces con cada una de las rejillas defendibles. Fíjate además en otra",
          "cosa: el χ² del oro de verdad supera al de las %d simulaciones en todas ellas (con",
          "la de %d × %d, %s frente a una mediana de %s). Algo queda que el greenstone no",
          "explica; medirlo es el trabajo del ejercicio 5, y este test no lo puede hacer."),
          f(100 * A_GS / A_RECT, 1), f(100 * n_gs / N_ORO, 1), f(cociente_gs, 2),
          NSIM_E1, NSIM_E1, NSIM_E1, K_EJ_E1, K_EJ_E1,
          f(chi_obs_e1[respetan == K_EJ_E1], 1), f(chi_med_e1[respetan == K_EJ_E1], 1)))
    ),
    lectura = paste(
      "Una λ sin su ventana no es una cifra completa, y un rechazo del test de cuadrantes no dice cuál",
      "de las dos propiedades de CSR falla. Las dos cosas se ven aquí antes de mirar una sola",
      "distancia.")
  )
)

# ---------------------------------------------------------------------
# E2 · El borde que da la vuelta al veredicto (4.3, 4.4, 4.8, 4.10)
# ---------------------------------------------------------------------
ORO_GS <- ORO[GS]
ce_gs <- clarkevans(ORO_GS)
ce_rect_todo <- clarkevans(ORO)
ce_rect <- ce_rect_todo[["naive"]]; ce_rect_cdf <- ce_rect_todo[["cdf"]]
# Por qué aquí el borde cambia el RÉGIMEN y en Bogotá solo el grado: la
# fracción de puntos que están más cerca del borde que de su vecino más
# próximo. A esos el estimador sin corregir puede medirles un vecino falso.
# El capítulo 4 ya publicó por qué el sesgo va siempre hacia «más regular»
# (su ejercicio guiado 5); lo nuevo es medir cuánto borde hay.
cerca_borde <- function(X) 100 * mean(bdist.points(X) < nndist(X))
pct_borde_gs <- cerca_borde(ORO_GS); pct_borde_bog <- cerca_borde(p_urb)
med_borde_gs <- median(bdist.points(ORO_GS)); med_nn_gs <- median(nndist(ORO_GS))
if (!(pct_borde_gs > 2 * pct_borde_bog)) para("E2: el greenstone ya no tiene mucho más borde que Bogotá")
RR <- (0:240) / 20
i10 <- which(abs(RR - 10) < 1e-12)
if (length(i10) != 1L) para("E2: la rejilla de r no pasa por 10 km")
K_none <- Kest(ORO_GS, r = RR, correction = "none")$un[i10]
K_tr   <- Kest(ORO_GS, r = RR, correction = "translate")$trans[i10]
PIR2 <- pi * 10^2
bd <- GS$bdry
n_piezas <- sum(!vapply(bd, spatstat.utils::is.hole.xypolygon, logical(1)))
n_aguj   <- sum(vapply(bd, spatstat.utils::is.hole.xypolygon, logical(1)))
n_vert   <- sum(vapply(bd, function(b) length(b$x), integer(1)))
perim_gs <- perimeter(GS)
if (!(K_none < PIR2 && PIR2 < K_tr))
  para("E2: K sin corregir ya no queda por debajo de πr² y la corregida por encima")
if (!(ce_gs[["naive"]] > 0.9 && ce_gs[["cdf"]] < 0.8))
  para("E2: la R sin corregir ya no parece aleatoria o la corregida ya no parece agregada")

# LA REFERENCIA QUE LA CIFRA SIN CORREGIR NO TIENE: el azar dentro de estas
# mismas franjas. La versión anterior explicaba el vuelco con «el vecino de
# verdad puede estar al otro lado del borde, donde nadie miró», y fuera del
# greenstone sí se miró —es el rectángulo del E1— y casi ningún yacimiento
# tiene su vecino más próximo fuera (auditoría de los ejercicios, ronda 4).
# Lo que falla es la comparación: πr² y R = 1 son el azar en un plano sin
# bordes. Repartiendo los mismos yacimientos al azar DENTRO del greenstone,
# la K̂ y la R sin corregir que tocarían son otras, y contra ellas el oro
# sin corregir también se agrupa.
NSIM_E2 <- 199L
set.seed(SEMILLA)
ref_gs <- replicate(NSIM_E2, {
  Y <- runifpoint(npoints(ORO_GS), win = GS)
  c(K = Kest(Y, r = RR, correction = "none")$un[i10],
    R = as.numeric(clarkevans(Y, correction = "none")))
})
set.seed(SEMILLA)
q_K <- unname(quantile(ref_gs["K", ], c(0.025, 0.5, 0.975)))
q_R <- unname(quantile(ref_gs["R", ], c(0.025, 0.5, 0.975)))
if (!(K_none > q_K[3] && ce_gs[["naive"]] < q_R[1]))
  para("E2: contra el azar dentro del greenstone, el oro sin corregir ya no sale agregado")
# De los yacimientos del greenstone, cuántos tienen su vecino más próximo
# —entre los 255— fuera de él.
dentro_gs_e2 <- inside.owin(ORO$x, ORO$y, GS)
vecino_fuera <- sum(!dentro_gs_e2[nnwhich(ORO)[which(dentro_gs_e2)]])
if (vecino_fuera > 0.1 * npoints(ORO_GS)) para("E2: ya no son pocos los que tienen su vecino fuera del greenstone")
# Lo medido apenas cambia entre ventanas; cambia la referencia.
nn_med_gs <- mean(nndist(ORO_GS)); nn_med_rect <- mean(nndist(ORO))
nn_esp_gs <- 0.5 / sqrt(lam_gs); nn_esp_rect <- 0.5 / sqrt(lam_rect)
# El vuelco de K es a la escala que pide el enunciado: la K̂ sin corregir
# supera πr² desde 2 km hasta cerca de 10, y solo ahí la cruza.
kn_todo <- Kest(ORO_GS, r = RR, correction = "none")$un
coc_kn <- kn_todo / (pi * RR^2)
# Desde 2 km: por debajo apenas hay parejas, y K̂/πr² arranca en cero.
i_cruce <- which(RR >= 2 & coc_kn < 1)[1]
r_cruce <- RR[i_cruce]
i2 <- which(abs(RR - 2) < 1e-12)
if (!(length(i2) == 1L && all(coc_kn[RR >= 2 & RR < r_cruce] > 1) && r_cruce > 5 && r_cruce < 10))
  para("E2: la K sin corregir ya no supera πr² entre 2 km y un cruce antes de 10")
# Qué parte del greenstone está a más de 10 km de su borde: dónde cabe un
# disco de 10 km entero. Se publica con un decimal: spatstat (erosion) y
# shapely (buffer negativo) aproximan distinto los arcos y difieren un 5 %.
pct_nucleo_10 <- 100 * area.owin(erosion(GS, 10)) / A_GS

en2 <- paste(
  "Restringe el oro al greenstone (`oro[greenstone]`, en km) y calcula el índice de",
  "Clark-Evans, R, sin corregir y con la corrección `cdf`. Calcula también K̂ a 10 km",
  "sin corregir y con la corrección de traslación —pide `r = (0:240) / 20`, que pasa",
  "justo por 10— y compáralas con πr². Di qué régimen leería cada versión, la sin",
  "corregir y la corregida, y di cuál publicarías. En las sedes de Bogotá el borde movía",
  "el grado de agregación sin cambiar el régimen: cuenta qué fracción de los yacimientos",
  "está más cerca del borde del greenstone que de su vecino más próximo (`bdist.points`",
  sprintf("contra `nndist`), compárala con la de las sedes en la ventana urbana, el %s %%,", f(pct_borde_bog, 1)),
  "y explica por qué aquí el borde cambia el veredicto. Compara por último la R sin",
  "corregir de dentro del greenstone con la del rectángulo entero, y explica por qué el",
  "mismo oro parece tan distinto.")
EJ$e2 <- list(
  titulo = "El borde que da la vuelta al veredicto",
  modulos = list("cap4.m3", "cap4.m4", "cap4.m8", "cap4.m10"),
  enunciado = en2,
  pasos = list(
    list(paso = "Yacimientos dentro del greenstone", valor = npoints(ORO_GS)),
    list(paso = "Piezas del greenstone", valor = n_piezas),
    list(paso = "Agujeros del greenstone", valor = n_aguj),
    list(paso = "Vértices del contorno", valor = n_vert),
    list(paso = "Perímetro del greenstone (km)", valor = r10(perim_gs)),
    list(paso = "R de Clark-Evans sin corregir, greenstone", valor = r10(ce_gs[["naive"]])),
    list(paso = "R de Clark-Evans corregida (cdf), greenstone", valor = r10(ce_gs[["cdf"]])),
    list(paso = "K̂(10 km) sin corregir (km²)", valor = r10(K_none)),
    list(paso = "K̂(10 km) con traslación (km²)", valor = r10(K_tr)),
    list(paso = "π · 10² (km²)", valor = r10(PIR2)),
    list(paso = "Yacimientos más cerca del borde que de su vecino (%)", valor = r10(pct_borde_gs)),
    list(paso = "Sedes de Bogotá más cerca del borde que de su vecina (%)", valor = r10(pct_borde_bog)),
    list(paso = "R de Clark-Evans sin corregir, rectángulo", valor = r10(ce_rect)),
    list(paso = "R de Clark-Evans corregida (cdf), rectángulo", valor = r10(ce_rect_cdf)),
    list(paso = "Yacimientos del greenstone con su vecino más próximo fuera de él", valor = vecino_fuera),
    list(paso = "K̂(10 km) sin corregir, mediana de 199 repartos al azar en el greenstone (km²)", valor = r10(q_K[2])),
    list(paso = "R sin corregir, mediana de esos repartos", valor = r10(q_R[2]))
  ),
  solucion = list(
    n_gs = npoints(ORO_GS), piezas = n_piezas, agujeros = n_aguj, vertices = n_vert,
    perimetro_km = r10(perim_gs), area_km2 = r10(A_GS),
    ce_naive = r10(ce_gs[["naive"]]), ce_cdf = r10(ce_gs[["cdf"]]), ce_rect = r10(ce_rect),
    ce_rect_cdf = r10(ce_rect_cdf), pct_borde_gs = r10(pct_borde_gs), pct_borde_bogota = r10(pct_borde_bog),
    mediana_borde_km = r10(med_borde_gs), mediana_vecino_km = r10(med_nn_gs),
    K_none = r10(K_none), K_trans = r10(K_tr), pir2 = r10(PIR2),
    veces_trans = r10(K_tr / PIR2), veces_none = r10(K_none / PIR2),
    pct_area_fuera_gs = r10(100 - 100 * A_GS / A_RECT), lambda_gs_sobre_rect = r10(lam_gs / lam_rect),
    cociente_gs = r10(cociente_gs),
    nsim_referencia = NSIM_E2, cobertura_pct = 95,
    ref_K_cuantiles = as.list(r10(q_K)), ref_R_cuantiles = as.list(r10(q_R)),
    vecino_fuera = vecino_fuera, nn_media_gs_km = r10(nn_med_gs), nn_media_rect_km = r10(nn_med_rect),
    nn_esperada_gs_km = r10(nn_esp_gs), nn_esperada_rect_km = r10(nn_esp_rect),
    r_cruce_km = r10(r_cruce), K_none_sobre_pir2_2km = r10(coc_kn[i2]),
    pct_area_a_mas_de_10km = r10(pct_nucleo_10),
    respuestas = list(
      responde(en2, "Di qué régimen leería cada versión, la sin corregir y la corregida",
        sprintf(paste(
          "Sin corregir, casi aleatorio tirando a regular: R = %s, y K̂(10 km) = %s km², por",
          "debajo de πr² = %s. Corregidas, agregado y con holgura: R = %s, y K̂ = %s km², %s",
          "veces πr². Sin envolvente es una lectura, no un veredicto; lo que no depende del azar",
          "es que, con la misma nube de puntos y la misma ventana, las dos versiones leen",
          "regímenes distintos. Y eso es a 10 km: entre 2 y %s km la K̂ sin corregir también",
          "supera πr² —a 2 km es %s veces—. El sesgo del borde crece con r, porque a r grande",
          "casi ningún disco cabe en las franjas del greenstone, y desde %s km es lo bastante",
          "grande para cruzar πr². El vuelco de K es a la escala que pide el enunciado; el de",
          "Clark-Evans no depende de ninguna."),
          f(ce_gs[["naive"]], 3), f(K_none, 1), f(PIR2, 1), f(ce_gs[["cdf"]], 3),
          f(K_tr, 1), f(K_tr / PIR2, 2), f(r_cruce, 2), f(coc_kn[i2], 2), f(r_cruce, 2))),
      responde(en2, "explica por qué aquí el borde cambia el veredicto",
        sprintf(paste(
          "El %s %% de los yacimientos está más cerca del borde que de su vecino más",
          "próximo, frente al %s %% de las sedes de Bogotá: la mediana de la distancia al borde",
          "es %s km, y la del vecino, %s. El greenstone tiene %d piezas con %d agujeros y %s km",
          "de contorno para %s km², y solo el %s %% de su área está a más de 10 km del borde: es",
          "una ventana hecha de franjas. Ojo con la explicación fácil, que aquí es falsa: no es",
          "que el vecino de verdad esté al otro lado del borde, donde nadie miró. Fuera del",
          "greenstone también se buscó —es el rectángulo del ejercicio 1—, y solo %d de los %d",
          "tienen su vecino más próximo fuera. La cifra sin corregir está bien medida y mal",
          "comparada: πr² y R = 1 son lo que daría el azar en un plano sin bordes, y en una",
          "ventana hecha de franjas el azar da otra cosa. Repartiendo %d puntos al azar dentro",
          "de este mismo greenstone, %d veces, la K̂(10 km) sin corregir sale en torno a %s km²",
          "—entre %s y %s en el %d %% central de los repartos—, no %s, y la R en torno a %s, no 1.",
          "El oro da %s y %s: frente a la referencia de su propia ventana, está agregado. En",
          "Bogotá el borde tocaba a una minoría de sedes y solo movía el grado; aquí toca a la",
          "mayoría de los yacimientos, y la referencia de libro le da la vuelta al régimen."),
          f(pct_borde_gs, 1), f(pct_borde_bog, 1), f(med_borde_gs, 2), f(med_nn_gs, 2),
          n_piezas, n_aguj, fe(perim_gs), fe(A_GS), f(pct_nucleo_10, 1),
          vecino_fuera, npoints(ORO_GS), npoints(ORO_GS), NSIM_E2, f(q_K[2], 1),
          f(q_K[1], 1), f(q_K[3], 1), 95L, f(PIR2, 1), f(q_R[2], 2),
          f(K_none, 1), f(ce_gs[["naive"]], 3))),
      responde(en2, "di cuál publicarías",
        sprintf(paste(
          "Las corregidas, diciendo qué corrección se usó. Como contraste de CSR valen tal",
          "cual: bajo la nula los puntos son un Poisson recortado a la ventana, y para eso",
          "están hechas. Si además quieres leer la K corregida como la escala de los grupos,",
          "ten presente lo que supone: que el oro sigue igual más allá del borde, y aquí la",
          "frontera es geológica —fuera hay %s veces menos oro por km²—. La comprobación que",
          "no supone nada es la de los %d repartos al azar dentro del mismo greenstone: contra",
          "ella, el oro sin corregir queda agregado igual."),
          f(cociente_gs, 2), NSIM_E2)),
      responde(en2, "Compara por último la R sin corregir de dentro del greenstone con la del rectángulo entero, y explica por qué el mismo oro parece tan distinto",
        sprintf(paste(
          "Porque R divide por la distancia que daría el azar con la λ de la ventana, y lo",
          "que se mide apenas se mueve: la distancia media al vecino es %s km dentro del",
          "greenstone y %s en el rectángulo. Lo que cambia es contra qué se mide: el azar",
          "esperaría %s km con la λ del greenstone y %s con la del rectángulo. En el",
          "rectángulo, R = %s: la λ está diluida en un %s %% de terreno cuya intensidad es %s",
          "veces menor que la del greenstone, y el oro, apiñado en las franjas del greenstone,",
          "parece muy agregado. Dentro del greenstone la λ es %s veces la del rectángulo y la",
          "referencia se acorta. Y la R sin corregir del greenstone, %s, se compara con una",
          "referencia que esa ventana no tiene: el azar, dentro de estas franjas, daría en",
          "torno a %s y no 1; corregida es %s. En el rectángulo el borde apenas pesa (%s",
          "corregida, %s sin corregir). Las dos R contestan preguntas distintas: la del",
          "rectángulo mezcla la geología con el agrupamiento; la del greenstone, comparada con",
          "su propia referencia, pregunta si los yacimientos se agrupan dentro de la roca que",
          "los admite."),
          f(nn_med_gs, 2), f(nn_med_rect, 2), f(nn_esp_gs, 2), f(nn_esp_rect, 2),
          f(ce_rect, 3), f(100 - 100 * A_GS / A_RECT, 1), f(cociente_gs, 2), f(lam_gs / lam_rect, 2),
          f(ce_gs[["naive"]], 3), f(q_R[2], 2), f(ce_gs[["cdf"]], 3), f(ce_rect_cdf, 3), f(ce_rect, 3)))
    ),
    lectura = paste(
      "Antes de leer el régimen, el borde; y antes de corregir, la pregunta de qué hay al otro",
      "lado. Aquí se miró, y lo que cambia la corrección no es lo medido: es la referencia con",
      "que se compara.")
  )
)
message("  E1 y E2 · ventana, cuadrantes y borde")

# ---------------------------------------------------------------------
# E3 · Cuatro anchos para el mismo oro (5.1 a 5.4)
# ---------------------------------------------------------------------
selector <- function(nombre, fun) {
  aviso <- NA_character_
  s <- withCallingHandlers(fun(ORO),
    warning = function(w) { aviso <<- conditionMessage(w); invokeRestart("muffleWarning") })
  h <- attr(s, "h")
  v <- as.numeric(s)[1]
  list(selector = nombre, sigma = r10(v),
       choco = !is.na(aviso) && grepl("end of interval", aviso, fixed = TRUE),
       h_min = if (is.null(h)) NA else r10(min(h)),
       h_max = if (is.null(h)) NA else r10(max(h)),
       en_extremo = if (is.null(h)) FALSE else (abs(v - min(h)) < 1e-9 || abs(v - max(h)) < 1e-9))
}
SEL <- list(diggle = selector("diggle", bw.diggle), ppl = selector("ppl", bw.ppl),
            CvL = selector("CvL", bw.CvL), scott = selector("scott", bw.scott))
scott_y <- as.numeric(bw.scott(ORO))[2]
sig <- vapply(SEL, function(z) z$sigma, numeric(1))
raz_sel <- max(sig) / min(sig)
if (any(vapply(SEL, function(z) z$choco || z$en_extremo, logical(1))))
  para("E3: algún selector choca con su intervalo y la respuesta dice que ninguno")
integra <- function(im) { v <- as.numeric(im$v); v <- v[is.finite(v)]; sum(v) * im$xstep * im$ystep }
# La rejilla por defecto, 128 × 128 sobre 330 × 400 km, deja celdas de unos
# 3 km: menos de tres celdas para el σ de bw.diggle y el de bw.ppl, que es lo
# que el capítulo 5 (módulo 5) pide para dibujar un σ honestamente. Con la
# rejilla por defecto el pico del σ más estrecho cambiaba un 13 % al afinar.
DIMYX <- 1024L
im_def <- density(ORO, sigma = SEL$diggle$sigma)
celda_def <- c(im_def$xstep, im_def$ystep)
if (!(3 * max(celda_def) > SEL$ppl$sigma)) para("E3: con la rejilla por defecto el σ de bw.ppl ya cubre tres celdas")
S_DIG <- SEL$diggle$sigma; S_PPL <- SEL$ppl$sigma; S_CVL <- SEL$CvL$sigma
kd <- function(s, ...) density(ORO, sigma = s, dimyx = DIMYX, ...)
celda_fina <- with(kd(S_DIG), c(xstep, ystep))
if (!(3 * max(celda_fina) < S_DIG)) para("E3: con la rejilla fina el σ de bw.diggle sigue sin cubrir tres celdas")
masas <- lapply(c(diggle = S_DIG, CvL = S_CVL), function(s)
  c(sin = integra(kd(s, edge = FALSE)), def = integra(kd(s)), dig = integra(kd(s, diggle = TRUE))))
# Lo que las respuestas afirman: sin corregir pierde poco con el σ estrecho y
# casi un tercio con el ancho; la corrección por defecto se queda corta con
# uno y se pasa con el otro —por eso «no es una ley»—, y la de Diggle clava n.
if (!(masas$diggle[["sin"]] > 0.99 * N_ORO && masas$CvL[["sin"]] < 0.8 * N_ORO))
  para("E3: la fuga sin corregir ya no es pequeña con bw.diggle y grande con bw.CvL")
if (!(masas$diggle[["def"]] < N_ORO && masas$CvL[["def"]] > N_ORO))
  para("E3: la corrección por defecto ya no se queda corta con un σ y se pasa con el otro")
if (any(abs(c(masas$diggle[["dig"]], masas$CvL[["dig"]]) - N_ORO) > 0.01))
  para("E3: la corrección de Diggle ya no integra el número de yacimientos")
picos <- vapply(c(diggle = S_DIG, ppl = S_PPL, CvL = S_CVL), function(s) max(kd(s, diggle = TRUE)), numeric(1))
if (!(picos[["CvL"]] < lam_gs && picos[["ppl"]] > lam_gs))
  para("E3: el pico de bw.CvL ya no queda bajo la intensidad del greenstone o el de bw.ppl ya no la supera")

en3 <- paste(
  "Sobre el oro en km y su ventana rectangular, calcula el σ que devuelve cada uno de",
  "los cuatro selectores de ancho de banda —`bw.diggle`, `bw.ppl`, `bw.CvL` y",
  "`bw.scott`, que da un σ por eje— y el cociente entre el mayor y el menor, y",
  "comprueba si alguno chocó con el extremo de su intervalo de búsqueda. Estima después",
  "la intensidad con el σ de `bw.diggle` y con el de `bw.CvL`, cada uno sin corregir",
  "(`edge = FALSE`) y con la corrección por defecto, las cuatro superficies con",
  "`dimyx = 1024`, e intégralas sobre la",
  "ventana. Di qué parte de los yacimientos pierde la superficie sin corregir con",
  "cada σ y explica la diferencia; di también si la corrección por defecto se pasa",
  "de los 255 o se queda corta, y compárala con la de Diggle (`diggle = TRUE`). Por",
  "último, estima la superficie con el σ de cada uno de los tres selectores que buscan,",
  "con `diggle = TRUE`, mira su máximo junto a la intensidad media del greenstone del",
  "ejercicio 1, decide qué σ publicarías en un mapa de «dónde hay oro» y di cómo lo",
  "declararías.")
EJ$e3 <- list(
  titulo = "Cuatro anchos para el mismo oro",
  modulos = list("cap5.m1", "cap5.m2", "cap5.m3", "cap5.m4", "cap5.m5"),
  enunciado = en3,
  pasos = list(
    list(paso = "σ de bw.diggle (km)", valor = S_DIG),
    list(paso = "σ de bw.ppl (km)", valor = S_PPL),
    list(paso = "σ de bw.CvL (km)", valor = S_CVL),
    list(paso = "σ de bw.scott a lo ancho (km)", valor = SEL$scott$sigma),
    list(paso = "σ de bw.scott a lo alto (km)", valor = r10(scott_y)),
    list(paso = "Cociente entre el mayor y el menor", valor = r10(raz_sel)),
    list(paso = "Selectores que chocaron con su intervalo", valor = 0L),
    list(paso = "Integral sin corregir, σ de bw.diggle", valor = r10(masas$diggle[["sin"]])),
    list(paso = "Integral con la corrección por defecto, σ de bw.diggle", valor = r10(masas$diggle[["def"]])),
    list(paso = "Integral sin corregir, σ de bw.CvL", valor = r10(masas$CvL[["sin"]])),
    list(paso = "Integral con la corrección por defecto, σ de bw.CvL", valor = r10(masas$CvL[["def"]])),
    list(paso = "Intensidad máxima con diggle = TRUE, σ de bw.diggle (por km²)", valor = r10(picos[["diggle"]])),
    list(paso = "Intensidad máxima con diggle = TRUE, σ de bw.ppl (por km²)", valor = r10(picos[["ppl"]])),
    list(paso = "Intensidad máxima con diggle = TRUE, σ de bw.CvL (por km²)", valor = r10(picos[["CvL"]])),
    list(paso = "Intensidad media del greenstone (por km², ejercicio 1)", valor = r10(lam_gs))
  ),
  solucion = list(
    selectores = unname(SEL), scott_y = r10(scott_y), razon = r10(raz_sel), dimyx = DIMYX,
    celda_defecto_km = r10(celda_def), celda_fina_km = r10(celda_fina), celdas_minimas = 3L,
    lado_corto_km = r10(min(diff(W_ORO$xrange), diff(W_ORO$yrange))), dimyx_defecto = 128L,
    masas_diggle = as.list(r10(masas$diggle)), masas_cvl = as.list(r10(masas$CvL)),
    fuga_pct_diggle = r10(100 * (1 - masas$diggle[["sin"]] / N_ORO)),
    fuga_pct_cvl = r10(100 * (1 - masas$CvL[["sin"]] / N_ORO)),
    exceso_pct_cvl = r10(100 * (masas$CvL[["def"]] / N_ORO - 1)),
    picos = as.list(r10(picos)), lambda_gs = r10(lam_gs),
    pico_ppl_sobre_gs = r10(picos[["ppl"]] / lam_gs), pico_cvl_sobre_gs = r10(picos[["CvL"]] / lam_gs),
    respuestas = list(
      responde(en3, "comprueba si alguno chocó con el extremo de su intervalo de búsqueda",
        sprintf(paste(
          "Ninguno: los tres que buscan devuelven un valor dentro de su intervalo y sin aviso,",
          "y bw.scott no busca: aplica una fórmula. El mayor es %s veces el menor —de %s km con",
          "bw.diggle a %s km con bw.CvL— sin que ninguno falle: el abanico no es un error de",
          "cálculo, es que cada selector contesta otra pregunta."),
          f(raz_sel, 1), f(S_DIG, 2), f(S_CVL, 1))),
      responde(en3, "Di qué parte de los yacimientos pierde la superficie sin corregir con cada σ y explica la diferencia",
        sprintf(paste(
          "Con el σ de bw.diggle pierde el %s %%: integra %s. Con el de bw.CvL pierde el %s %%:",
          "integra %s. Lo que se pierde es la parte de cada núcleo que cae fuera del",
          "rectángulo. Con %s km solo la pierden los yacimientos pegados al borde, y poca;",
          "con %s km, frente a un lado corto de %s km, casi todos los núcleos se salen de la",
          "ventana, y mucho.",
          "Cuanto más ancho el σ, más pesa el borde: elegir el ancho es también decidir",
          "cuánto importa la corrección."),
          f(100 * (1 - masas$diggle[["sin"]] / N_ORO), 2), f(masas$diggle[["sin"]], 2),
          f(100 * (1 - masas$CvL[["sin"]] / N_ORO), 1), f(masas$CvL[["sin"]], 1),
          f(S_DIG, 2), f(S_CVL, 1), f(min(diff(W_ORO$xrange), diff(W_ORO$yrange)), 1))),
      responde(en3, "di también si la corrección por defecto se pasa de los 255 o se queda corta, y compárala con la de Diggle (`diggle = TRUE`)",
        sprintf(paste(
          "Las dos cosas, según el σ. Con el de bw.CvL se pasa: %s, un %s %% por encima de",
          "%d. Con el de bw.diggle se queda corta, por poco: %s. No es una ley del método:",
          "esa corrección divide la estimación de cada sitio por la fracción del núcleo",
          "centrado en ese sitio que cae dentro, y el total sale por encima o por debajo de n",
          "según a qué distancia del borde estén los yacimientos, medida en anchos de banda.",
          "La de Diggle divide en otro sitio: el núcleo de cada yacimiento, por la fracción de",
          "ese mismo núcleo que cae dentro. Así cada uno aporta exactamente 1, y por eso",
          "integra n siempre: %s con los dos σ."),
          f(masas$CvL[["def"]], 1), f(100 * (masas$CvL[["def"]] / N_ORO - 1), 1), N_ORO,
          f(masas$diggle[["def"]], 2), f(masas$CvL[["dig"]], 2))),
      responde(en3, "mira su máximo junto a la intensidad media del greenstone del ejercicio 1, decide qué σ publicarías en un mapa de «dónde hay oro» y di cómo lo declararías",
        sprintf(paste(
          "El de bw.ppl, %s km, con diggle = TRUE. No porque sea el «correcto» —la teoría no",
          "entrega ninguno—, sino porque es el que contesta la pregunta del mapa. El de bw.diggle, %s km, pinta",
          "casi cada yacimiento por separado: su pico, %s por km², lo pone un puñado de",
          "puntos. El de bw.CvL, %s km, borra la geología: su pico, %s por km², queda por",
          "debajo de la intensidad media del propio greenstone, %s. El de bw.ppl resuelve las",
          "franjas sin deshacerlas en puntos —su pico, %s, es %s veces la intensidad del",
          "greenstone— y queda a la escala de los grupos que mide el ejercicio 5. En el pie va",
          "todo: núcleo gaussiano, σ = %s km elegido por bw.ppl, corrección de Diggle, la",
          "rejilla de %s × %s y los mapas de %s y %s km como sensibilidad. La rejilla también",
          "se declara: con la de 128 × 128 las celdas miden %s × %s km, y ni el σ de bw.diggle",
          "ni el de bw.ppl abarcarían las %d celdas que el capítulo 5 pide dentro de cada σ para",
          "que el mapa dibuje el núcleo y no su propia rejilla."),
          f(S_PPL, 2), f(S_DIG, 2), f(picos[["diggle"]], 4), f(S_CVL, 1), f(picos[["CvL"]], 4),
          f(lam_gs, 4), f(picos[["ppl"]], 4), f(picos[["ppl"]] / lam_gs, 1), f(S_PPL, 2),
          fe(DIMYX), fe(DIMYX), f(S_DIG, 2), f(S_CVL, 1), f(celda_def[1], 2), f(celda_def[2], 2), 3L))
    ),
    lectura = paste(
      "Un mapa de intensidad responde a una pregunta que alguien formuló, y lo hace con un",
      "ancho, una corrección y una rejilla concretos. Sin esas tres líneas en el pie, el mapa",
      "no dice lo que parece.")
  )
)

# ---------------------------------------------------------------------
# E4 · La falla, el greenstone y la cuadratura (5.7 a 5.9)
# ---------------------------------------------------------------------
dv <- D_FALLA(ORO$x, ORO$y)
q_bulto <- as.numeric(quantile(dv, c(0.05, 0.95)))
set.seed(2026)
rh <- rhohat(ORO, D_FALLA)
ok <- is.finite(rh$rho)
xr <- rh[[1]][ok]; yr <- rh$rho[ok]
b <- xr >= q_bulto[1] & xr <= q_bulto[2]
rho_max <- max(yr); rho_min <- min(yr)
# El mínimo vale CERO exacto: más allá del yacimiento más alejado de una
# falla no queda ninguno con que estimar ρ. La razón es infinita, y se dice
# con un indicador: `toJSON` escribía el Inf como null sin avisar.
if (rho_min != 0) para("E4: el ρ mínimo de rhohat ya no es cero y el ejercicio dice que la razón es infinita")
rho_max_b <- max(yr[b]); rho_min_b <- min(yr[b])
dist_max_oro <- max(dv); dist_max_ventana <- max(xr)
# Pasado el yacimiento más alejado ρ no es «cero en todo el tramo»: alterna
# ceros exactos con restos de redondeo (del orden de 1e-16). La respuesta
# dice cuántos ceros hay y desde dónde, no que el tramo entero valga cero.
primer_cero <- min(xr[yr == 0]); n_ceros <- sum(yr == 0)
if (!(primer_cero > dist_max_oro && max(yr[xr >= primer_cero]) < 1e-12))
  para("E4: el tramo sin yacimientos ya no es ceros y restos de redondeo")
set.seed(SEMILLA)

# spatstat atrapa la inversa singular con un try() que IMPRIME el error y
# sigue: ese «Error in solve.default» es justo lo que el ejercicio enseña a
# no confundir con un fallo, pero aquí solo ensucia la salida del guion.
f_m <- ppm(murchison$gold ~ x + y)
invisible(capture.output(
  v_m <- withCallingHandlers(tryCatch(vcov(f_m), error = function(e) NULL),
                             warning = function(w) invokeRestart("muffleWarning")),
  type = "message"))
f_km <- ppm(ORO ~ x + y)
se_km <- sqrt(diag(vcov(f_km)))
if (!is.null(v_m)) para("E4: el ajuste en metros ya devuelve errores estándar")
invisible(capture.output(aic_m <- AIC(f_m), type = "message"))
dif_aic <- aic_m - AIC(f_km)
# El intercepto en km es log λ en el origen de coordenadas, a miles de
# kilómetros del rectángulo: tampoco se lee sin centrar (cap. 5, módulo 9).
dist_origen <- sqrt(min(abs(W_ORO$xrange))^2 + min(abs(W_ORO$yrange))^2)
f_G <- ppm(ORO ~ G, covariates = list(G = G_IND))
f_G400 <- ppm(ORO ~ G, covariates = list(G = G_IND), nd = 400)
pesos_gs <- function(f) {
  q <- quad.ppm(f); U <- union.quad(q)
  sum(w.quad(q)[G_IND(U$x, U$y) == 1])
}
nd_def <- round(sqrt(npoints(quad.ppm(f_G)$dummy)))
eb <- exp(coef(f_G)[["G"]]); eb400 <- exp(coef(f_G400)[["G"]])
beta_def <- coef(f_G)[["G"]]; beta_400 <- coef(f_G400)[["G"]]
if (!(eb < eb400 && eb400 < cociente_gs))
  para("E4: la cuadratura fina ya no acerca e^β al cociente exacto")

en4 <- paste(
  "Construye la distancia de cada sitio de la ventana a la falla más cercana con",
  "`D <- distfun(fallas)` (en km). Calcula `rhohat(oro, D)` —pon `set.seed(2026)`",
  "justo antes, porque es aleatorio— y da la razón entre su ρ máximo y su mínimo en",
  "todo el rango (si no sale un número finito, di por qué), y la razón entre el máximo",
  "y el mínimo de ρ en el tramo que va del percentil 5 al 95 de la distancia observada",
  "en los yacimientos —el «bulto»—. Ajusta `ppm(oro ~ x + y)` dos veces, con el patrón",
  "en metros (`murchison$gold`) y en kilómetros (`oro`): di cuál de los dos trae errores estándar, y explica por qué",
  "sus AIC difieren en una cantidad que no dice nada de los modelos. Por último, ajusta",
  "`ppm(oro ~ G)`, con `G <- function(x, y) as.numeric(inside.owin(x, y, greenstone))`",
  "y el greenstone en km del ejercicio 1, y compara",
  "exp(β) con el cociente de intensidades del ejercicio 1; repite con `nd = 400` y",
  "explica de dónde sale la diferencia.")
EJ$e4 <- list(
  titulo = "La falla, el greenstone y la cuadratura",
  modulos = list("cap5.m7", "cap5.m8", "cap5.m9"),
  enunciado = en4,
  pasos = list(
    list(paso = "Distancia a la falla: percentil 5 en los yacimientos (km)", valor = r10(q_bulto[1])),
    list(paso = "Distancia a la falla: percentil 95 en los yacimientos (km)", valor = r10(q_bulto[2])),
    list(paso = "Distancia a la falla del yacimiento más alejado (km)", valor = r10(dist_max_oro)),
    list(paso = "ρ máximo en todo el rango", valor = signif(rho_max, 6)),
    list(paso = "ρ mínimo en todo el rango", valor = signif(rho_min, 6)),
    list(paso = "Razón en el bulto (percentiles 5 a 95)", valor = r10(rho_max_b / rho_min_b)),
    list(paso = "Coeficientes del ajuste en metros", valor = 3L),
    list(paso = "De ellos, con error estándar", valor = 0L),
    list(paso = "z del coeficiente de x, ajuste en km", valor = r10(coef(f_km)[["x"]] / se_km[["x"]])),
    list(paso = "z del coeficiente de y, ajuste en km", valor = r10(coef(f_km)[["y"]] / se_km[["y"]])),
    list(paso = "AIC en metros menos AIC en km", valor = r10(dif_aic)),
    list(paso = "β de G, cuadratura por defecto", valor = r10(beta_def)),
    list(paso = "β de G, nd = 400", valor = r10(beta_400)),
    list(paso = "exp(β) de G, cuadratura por defecto", valor = r10(eb)),
    list(paso = "exp(β) de G, nd = 400", valor = r10(eb400)),
    list(paso = "Cociente exacto de intensidades (ejercicio 1)", valor = r10(cociente_gs)),
    list(paso = "Área que los pesos dan al greenstone, por defecto (km²)", valor = r10(pesos_gs(f_G))),
    list(paso = "Área que los pesos dan al greenstone, nd = 400 (km²)", valor = r10(pesos_gs(f_G400)))
  ),
  solucion = list(
    percentiles = list(5L, 95L), bulto = r10(q_bulto), dist_max_oro = r10(dist_max_oro),
    dist_max_ventana = r10(dist_max_ventana),
    rho_max = signif(rho_max, 6), rho_min = signif(rho_min, 6),
    razon_total_infinita = TRUE, razon_bulto = r10(rho_max_b / rho_min_b),
    primer_cero_km = r10(primer_cero), ceros = n_ceros, valores_curva = length(yr),
    errores_metros = 0L, coeficientes = 3L, z_km = r10(unname(coef(f_km) / se_km)),
    intercepto_km = r10(coef(f_km)[["(Intercept)"]]), dist_origen_km = r10(dist_origen),
    beta_defecto = r10(beta_def), beta_400 = r10(beta_400),
    cambio_beta_pct = r10(100 * (beta_400 / beta_def - 1)), cambio_eb_pct = r10(100 * (eb400 / eb - 1)),
    dif_aic = r10(dif_aic), dos_n_log = r10(2 * N_ORO * log(1e6)),
    nd_defecto = nd_def, nd_fino = 400L, eb_defecto = r10(eb), eb_400 = r10(eb400), cociente_exacto = r10(cociente_gs),
    pesos_gs_defecto = r10(pesos_gs(f_G)), pesos_gs_400 = r10(pesos_gs(f_G400)), area_gs = r10(A_GS),
    respuestas = list(
      responde(en4, "da la razón entre su ρ máximo y su mínimo en todo el rango (si no sale un número finito, di por qué), y la razón entre el máximo y el mínimo de ρ en el tramo que va del percentil 5 al 95 de la distancia observada en los yacimientos",
        sprintf(paste(
          "En todo el rango no sale un número finito, y es lo que tenía que salir: el mínimo",
          "de ρ es cero. El yacimiento más alejado de una falla está a %s km y la curva llega",
          "hasta los %s km; pasado ese yacimiento ρ se apaga: %d de sus %d valores son cero exacto,",
          "todos a partir de %s km, y los demás de ese tramo no llegan a cero solo por",
          "redondeo. La razón entre el máximo y el mínimo la decide una cola, y en su forma",
          "extrema: un tramo sin datos. Entre los percentiles 5 y 95 —de %s a %s km— la razón",
          "es %s: aquí, al revés que con la distancia al centro de Bogotá, la covariable manda",
          "de verdad también donde hay datos. Aun así es una estimación puntual: el mínimo de",
          "ese tramo cae en su cola, donde quedan pocos yacimientos, y la cifra se lee como un",
          "orden de magnitud, no como un valor exacto."),
          f(dist_max_oro, 1), f(dist_max_ventana, 1), n_ceros, length(yr), f(primer_cero, 1),
          f(q_bulto[1], 2), f(q_bulto[2], 1), f(rho_max_b / rho_min_b, 1))),
      responde(en4, "di cuál de los dos trae errores estándar",
        sprintf(paste(
          "El de kilómetros. En metros las coordenadas son números de seis y siete cifras, la",
          "información de Fisher queda singular y `vcov()` avisa y devuelve `NULL`: hay %d",
          "coeficientes y ninguno con error estándar. Pasado a kilómetros, cada coeficiente",
          "trae el suyo, con z de %s para x y %s para y. Aun en kilómetros, el intercepto no se lee: es",
          "log λ en el origen de coordenadas, a %s km del rectángulo. Para leerlo hay que",
          "centrar, como hace el capítulo 5 con xc e yc."),
          3L, f(coef(f_km)[["x"]] / se_km[["x"]], 2), f(coef(f_km)[["y"]] / se_km[["y"]], 2),
          fe(dist_origen))),
      responde(en4, "explica por qué sus AIC difieren en una cantidad que no dice nada de los modelos",
        sprintf(paste(
          "El de metros es %s puntos más alto, y no por ajustar peor: los dos modelos son el",
          "mismo. Con el patrón en metros, la intensidad se mide por m², y sale un millón de",
          "veces menor que por km²; cada uno de los %d yacimientos aporta log λ a la",
          "log-verosimilitud, y la diferencia es exactamente 2n·ln(10⁶). Dos AIC solo se",
          "comparan con las mismas unidades, igual que solo se comparan con la misma cuadratura",
          "(capítulo 5, módulo 8)."),
          f(dif_aic, 2), N_ORO)),
      responde(en4, "compara exp(β) con el cociente de intensidades del ejercicio 1; repite con `nd = 400` y explica de dónde sale la diferencia",
        sprintf(paste(
          "Con una covariable que vale 0 o 1, la máxima verosimilitud tiene forma cerrada:",
          "exp(β) es el cociente de las dos intensidades empíricas, %s. La función `ppm` no la usa: aproxima la",
          "integral con una cuadratura cuyos pesos reparten el área entre los yacimientos y",
          "una malla de puntos ficticios, y con el greenstone partido en %d piezas los pesos",
          "por defecto le atribuyen %s km² cuando mide %s. Con área de más, la intensidad",
          "dentro sale baja: exp(β) = %s. Con nd = 400 los pesos casi aciertan (%s km²) y exp(β) =",
          "%s. La cuadratura es parte del modelo ajustado: cambia el coeficiente, y se",
          "declara. Medido en β el cambio es menor, de %s a %s, un %s %%; en exp(β) es un %s %%.",
          "El capítulo 5 enseña que en Bogotá el coeficiente apenas se mueve con la",
          "cuadratura; aquí se mueve más porque el greenstone en %d piezas es un caso extremo",
          "para una malla de puntos ficticios."),
          f(cociente_gs, 2), n_piezas, fe(pesos_gs(f_G)), fe(A_GS), f(eb, 2),
          fe(pesos_gs(f_G400)), f(eb400, 2), f(beta_def, 3), f(beta_400, 3),
          f(100 * (beta_400 / beta_def - 1), 1), f(100 * (eb400 / eb - 1), 1), n_piezas))
    ),
    lectura = paste(
      "Antes de leer una curva o un coeficiente, tres cosas que no salen en la llamada: dónde hay datos",
      "para estimar la curva, en qué unidades está el patrón y con qué cuadratura se ajustó.")
  )
)
message("  E3 y E4 · núcleos, covariable y cuadratura")

# ---------------------------------------------------------------------
# E5 · ¿Explican las covariables la agregación? (5.10, 5.11)
# ---------------------------------------------------------------------
# Todo con nd = 400: es la cuadratura que el ejercicio 4 deja buena, y con
# la de defecto la fracción de radios fuera de la banda pasaba del 1 % al 14 %
# solo por la malla. Por eso el ejercicio ya no pide esa fracción: es ruido
# de Monte Carlo y de cuadratura, no un contraste.
#
# Y el veredicto del DCLF depende del tramo de r. El rango por defecto llega
# a un cuarto del lado corto, 82 km; K crece como r², y las desviaciones a r
# grande ahogan las de unos pocos kilómetros, que es donde están los grupos
# (el ejercicio 4 del módulo 12 del capítulo 4 lo enseña sobre `cells`). El
# enunciado fija los dos tramos ANTES de mirar, y la respuesta dice lo que
# cada uno contesta. La auditoría de los ejercicios lo encontró: con un
# solo rango, la respuesta concluía «compatible» con un modelo que el tramo
# corto rechaza con todas las semillas probadas.
ND_E5 <- 400L; R_CORTO <- 20
f_D  <- ppm(ORO ~ D, covariates = list(D = D_FALLA), nd = ND_E5)
f_GD <- ppm(ORO ~ G + D, covariates = list(G = G_IND, D = D_FALLA), nd = ND_E5)
envuelve <- function(fit, semilla = 2026, ...) {
  set.seed(semilla)
  e <- envelope(fit, Kinhom, nsim = 99, correction = "translate", savefuns = TRUE, verbose = FALSE, ...)
  list(r_max_km = r10(max(e$r)),
       dclf_p = r10(dclf.test(e)$p.value),
       dclf_p_corto = r10(dclf.test(e, rinterval = c(0, R_CORTO))$p.value))
}
ENV_D <- envuelve(f_D); ENV_GD <- envuelve(f_GD)

# CÓMO PESA CADA TRAMO EN EL DCLF. El estadístico suma el cuadrado de la
# desviación en cada r, y la varianza de K̂ entre simulaciones crece con r:
# se mide en la envolvente de ~ G + D cuánto más varía a 60 km que a 3, y
# qué parte de la varianza sumada pone el tramo corto. La respuesta decía
# «cientos de veces» y la cifra medida es otra (auditoría de los
# ejercicios, ronda 4).
set.seed(2026)
e_var <- envelope(f_GD, Kinhom, nsim = 99, correction = "translate", savefuns = TRUE, verbose = FALSE)
sf <- as.data.frame(attr(e_var, "simfuns"))
v_r <- apply(as.matrix(sf[, setdiff(names(sf), "r")]), 1, var)
i3 <- which.min(abs(sf$r - 3)); i60 <- which.min(abs(sf$r - 60))
VAR_E5 <- list(r_a_km = r10(sf$r[i3]), r_b_km = r10(sf$r[i60]),
               veces = r10(v_r[i60] / v_r[i3]),
               pct_tramo_corto = r10(100 * sum(v_r[sf$r <= R_CORTO], na.rm = TRUE) / sum(v_r, na.rm = TRUE)))
if (!(VAR_E5$veces > 10 && VAR_E5$pct_tramo_corto < 25))
  para("E5: la varianza de K̂ ya no crece mucho con r o el tramo corto ya no pesa poco")

# SIN `lambda`, KINHOM NO USA LA INTENSIDAD DEL MODELO: a cada patrón —el
# del oro y cada simulado— le estima la suya con un núcleo, sin el punto y
# con el σ por defecto de density.ppp (un octavo del lado corto). El modelo
# entra solo en las simulaciones, y eso basta para que la envolvente
# contraste el modelo; pero no es «la K inhomogénea con la intensidad de
# G + D», que es lo que un estudiante entiende. Es el mismo convenio que el
# capítulo 5 usa con las sedes (B10 y C1), y se dice. Con la intensidad del
# modelo, reajustado a cada simulación (`lambda = ajuste`), el veredicto no
# cambia; si cambiara, esto para.
SIG_KINH_ORO <- min(sidelengths(Frame(W_ORO))) / 8
k_def_oro <- Kinhom(ORO, correction = "translate")
k_nuc_oro <- Kinhom(ORO, correction = "translate",
                    lambda = density(ORO, sigma = SIG_KINH_ORO, at = "points", leaveoneout = TRUE))
if (max(abs(k_def_oro$trans - k_nuc_oro$trans), na.rm = TRUE) > 1e-6 * max(k_def_oro$trans, na.rm = TRUE))
  para("E5: el σ por defecto de Kinhom ya no es un octavo del lado corto")
ENV_GD_LAMBDA <- envuelve(f_GD, lambda = f_GD)
if (!(ENV_GD_LAMBDA$dclf_p_corto <= 0.05 && ENV_GD_LAMBDA$dclf_p > ENV_GD_LAMBDA$dclf_p_corto))
  para("E5: con la intensidad del modelo el tramo corto ya no rechaza ~ G + D")
if (!(ENV_D$dclf_p <= 0.05 && ENV_D$dclf_p_corto <= 0.05 &&
      ENV_GD$dclf_p > 0.05 && ENV_GD$dclf_p_corto <= 0.05))
  para("E5: el veredicto ya no es «D sola rechaza en los dos tramos; G + D solo en el corto»")
# El veredicto no puede ser una semilla afortunada: se repite con diez.
SEMILLAS_E5 <- 1:10
otras <- vapply(SEMILLAS_E5, function(s) unlist(envuelve(f_GD, s)[c("dclf_p", "dclf_p_corto")]), numeric(2))
if (!(all(otras[1, ] > 0.05) && all(otras[2, ] <= 0.05)))
  para("E5: con otras semillas el DCLF de G + D ya no deja de rechazar en el rango largo o de rechazar en el corto")
set.seed(SEMILLA)
z_ppm <- coef(f_GD) / sqrt(diag(vcov(f_GD)))
se_ppm <- sqrt(diag(vcov(f_GD)))
kp <- lapply(c(iso = "isotropic", trans = "translate"), function(cr) {
  k <- kppm(ORO ~ G + D, "Thomas", covariates = list(G = G_IND, D = D_FALLA),
            statargs = list(correction = cr), nd = ND_E5)
  se <- sqrt(diag(vcov(k)))
  list(correccion = cr, escala_km = r10(parameters(k)$scale), mu = r10(mean(k$mu)),
       se_G = r10(se[["G"]]), se_D = r10(se[["D"]]),
       z_G = r10(coef(k)[["G"]] / se[["G"]]), z_D = r10(coef(k)[["D"]] / se[["D"]]))
})
zc <- qnorm(0.975)
if (!(abs(z_ppm[["D"]]) > zc && all(vapply(kp, function(z) abs(z$z_D) < zc, logical(1))) &&
      all(vapply(kp, function(z) abs(z$z_G) > zc, logical(1)))))
  para("E5: ya no es cierto que la z de D cae bajo 1.96 con los conglomerados y la de G no")

en5 <- paste(
  "Con `G` y `D` del ejercicio 4, ajusta dos modelos de Poisson inhomogéneo con la",
  "cuadratura que el ejercicio 4 mostró suficiente, `ppm(oro ~ D, nd = 400)` y",
  "`ppm(oro ~ G + D, nd = 400)`. Para cada uno, construye la envolvente de la K",
  "inhomogénea con 99 simulaciones del modelo —`envelope(ajuste, Kinhom, nsim = 99,",
  "correction = \"translate\", savefuns = TRUE)`, con `set.seed(2026)` justo antes de",
  "cada `envelope`— y da el p del test DCLF dos veces: con el tramo de r por defecto y",
  "con `rinterval = c(0, 20)`. Los dos tramos se fijan antes de mirar la curva: la",
  "pregunta es si los yacimientos vienen en grupos, y un grupo de yacimientos se mide",
  "en kilómetros, no en decenas de kilómetros. Ajusta después `kppm(oro ~ G + D, \"Thomas\", nd = 400)`",
  "con `statargs = list(correction = \"isotropic\")` y con `\"translate\"`, y da el error",
  "estándar y la z de los coeficientes de G y de D frente a los del `ppm`. Contesta:",
  "¿explican las covariables la agregación del oro? ¿Qué autoriza a decir un test que",
  "no rechaza? Compara por último lo que les pasa a las z con lo que le pasó a la de",
  "`xc` en las sedes de Bogotá.")
EJ$e5 <- list(
  titulo = "¿Explican las covariables la agregación?",
  modulos = list("cap4.m11", "cap5.m8", "cap5.m10", "cap5.m11"),
  enunciado = en5,
  pasos = list(
    list(paso = "Tramo de r por defecto: hasta (km)", valor = ENV_GD$r_max_km),
    list(paso = "~ D: p del DCLF, tramo por defecto", valor = ENV_D$dclf_p),
    list(paso = "~ D: p del DCLF, r ≤ 20 km", valor = ENV_D$dclf_p_corto),
    list(paso = "~ G + D: p del DCLF, tramo por defecto", valor = ENV_GD$dclf_p),
    list(paso = "~ G + D: p del DCLF, r ≤ 20 km", valor = ENV_GD$dclf_p_corto),
    list(paso = "~ G + D con lambda = el ajuste: p del DCLF, tramo por defecto", valor = ENV_GD_LAMBDA$dclf_p),
    list(paso = "~ G + D con lambda = el ajuste: p del DCLF, r ≤ 20 km", valor = ENV_GD_LAMBDA$dclf_p_corto),
    list(paso = "Error estándar de G en el ppm", valor = r10(se_ppm[["G"]])),
    list(paso = "Error estándar de D en el ppm", valor = r10(se_ppm[["D"]])),
    list(paso = "z de G en el ppm", valor = r10(z_ppm[["G"]])),
    list(paso = "z de D en el ppm", valor = r10(z_ppm[["D"]])),
    list(paso = "Thomas, K isotrópica: escala (km)", valor = kp$iso$escala_km),
    list(paso = "Thomas, K isotrópica: error estándar de G", valor = kp$iso$se_G),
    list(paso = "Thomas, K isotrópica: error estándar de D", valor = kp$iso$se_D),
    list(paso = "Thomas, K isotrópica: z de G", valor = kp$iso$z_G),
    list(paso = "Thomas, K isotrópica: z de D", valor = kp$iso$z_D),
    list(paso = "Thomas, K de traslación: escala (km)", valor = kp$trans$escala_km),
    list(paso = "Thomas, K de traslación: error estándar de G", valor = kp$trans$se_G),
    list(paso = "Thomas, K de traslación: error estándar de D", valor = kp$trans$se_D),
    list(paso = "Thomas, K de traslación: z de G", valor = kp$trans$z_G),
    list(paso = "Thomas, K de traslación: z de D", valor = kp$trans$z_D)
  ),
  solucion = list(
    nsim = 99L, nd = ND_E5, n = N_ORO, r_corto_km = R_CORTO,
    envolvente_D = ENV_D, envolvente_GD = ENV_GD, envolvente_GD_lambda = ENV_GD_LAMBDA,
    sigma_kinhom_km = r10(SIG_KINH_ORO), varianza = VAR_E5,
    inflacion_xc_bogota_iso = val("c5m11_th_iso_inf"), inflacion_xc_bogota_trans = val("c5m11_th_tr_inf"),
    semillas = as.list(SEMILLAS_E5),
    dclf_GD_otras_semillas = r10(otras[1, ]), dclf_GD_corto_otras_semillas = r10(otras[2, ]),
    dclf_GD_rango = r10(range(otras[1, ])), dclf_GD_corto_rango = r10(range(otras[2, ])),
    ppm_coef = r10(unname(coef(f_GD))), ppm_se = r10(unname(se_ppm)), ppm_z = r10(unname(z_ppm)),
    kppm = unname(kp), z_critico = r10(zc),
    inflacion_D_iso = r10(kp$iso$se_D / se_ppm[["D"]]),
    inflacion_D_trans = r10(kp$trans$se_D / se_ppm[["D"]]),
    inflacion_G_trans = r10(kp$trans$se_G / se_ppm[["G"]]),
    z_xc_bogota_poisson = val("c5m11_z_pois"), z_xc_bogota_thomas = val("c5m11_z_th_tr"),
    respuestas = list(
      responde(en5, "¿explican las covariables la agregación del oro?",
        sprintf(paste(
          "Buena parte, no toda. La distancia a la falla sola, no: con ~ D el DCLF rechaza en",
          "los dos tramos (%s con el tramo por defecto, %s hasta %d km). Con el greenstone",
          "añadido, el DCLF sobre el tramo por defecto deja de rechazar (%s), pero el tramo",
          "corto sigue rechazando (%s). No es una semilla afortunada: con otras diez, el p",
          "del tramo largo va de %s a %s y el del corto, de %s a %s. El tramo por defecto",
          "llega a %s km, un cuarto del lado corto. El DCLF suma el cuadrado de la desviación",
          "en cada r, y la varianza de K̂ entre simulaciones crece con r: a %s km es %s veces",
          "la de %s km, y el tramo hasta %d km pone solo el %s %% de la varianza sumada. Las",
          "desviaciones a decenas de kilómetros ahogan justo lo que se pregunta. Las dos",
          "covariables explican la geografía del oro a gran escala; queda agrupamiento a pocos",
          "kilómetros, el que el Thomas ajusta con una escala de %s a %s km según la",
          "corrección. Una cosa que la llamada no dice: sin `lambda`, `Kinhom` no usa la",
          "intensidad del modelo. A cada patrón —el del oro y cada simulado— le estima la suya",
          "con un núcleo de σ = %s km, un octavo del lado corto, sin el propio punto. El modelo",
          "entra en las simulaciones, que es lo que hace de la envolvente un contraste de ese",
          "modelo. Si se lo pasas (`lambda = ajuste`, que lo reajusta a cada simulación), los p",
          "de ~ G + D quedan en %s y %s, y la conclusión es la misma."),
          f(ENV_D$dclf_p, 2), f(ENV_D$dclf_p_corto, 2), R_CORTO, f(ENV_GD$dclf_p, 2),
          f(ENV_GD$dclf_p_corto, 2), f(min(otras[1, ]), 2), f(max(otras[1, ]), 2),
          f(min(otras[2, ]), 2), f(max(otras[2, ]), 2), f(ENV_GD$r_max_km, 1),
          f(VAR_E5$r_b_km, 0), f(VAR_E5$veces, 0), f(VAR_E5$r_a_km, 0), R_CORTO,
          f(VAR_E5$pct_tramo_corto, 1),
          f(kp$iso$escala_km, 1), f(kp$trans$escala_km, 1), f(SIG_KINH_ORO, 1),
          f(ENV_GD_LAMBDA$dclf_p, 2), f(ENV_GD_LAMBDA$dclf_p_corto, 2))),
      responde(en5, "¿Qué autoriza a decir un test que no rechaza?",
        sprintf(paste(
          "Que con ese estadístico, ese tramo de r y 99 simulaciones no hay evidencia contra",
          "el modelo; no que el modelo sea correcto. Aquí se ve en el mismo ajuste: el DCLF",
          "sobre el tramo por defecto no rechaza el Poisson ~ G + D (%s) y sobre r ≤ %d km sí",
          "(%s). Es la asimetría de siempre —J = 1 no certifica CSR y pasar el test de",
          "cuadrantes tampoco— y una lección del capítulo 4: el tramo de r es una decisión del",
          "analista, se toma antes de mirar y se declara. Elegirlo después de ver dónde se",
          "sale la curva sería otra cosa: buscar el tramo que rechaza."),
          f(ENV_GD$dclf_p, 2), R_CORTO, f(ENV_GD$dclf_p_corto, 2))),
      responde(en5, "Compara por último lo que les pasa a las z con lo que le pasó a la de `xc` en las sedes de Bogotá",
        sprintf(paste(
          "En Bogotá la z de xc pasó de %s a %s con Thomas y la K de traslación: con los",
          "conglomerados dentro, el gradiente dejó de distinguirse de cero. Aquí el error",
          "estándar de D se multiplica por %s y su z cae de %s a %s: le pasa lo mismo. El de G",
          "se multiplica por %s y su z cae de %s a %s, y sobrevive. La regla no es «los",
          "conglomerados matan la z», sino que la z de un Poisson con datos agrupados no se lee",
          "sin rehacerla: unas sobreviven y otras no, y solo se sabe midiendo, coeficiente por",
          "coeficiente. Y una diferencia con Bogotá que no está en las z sino en la corrección:",
          "allí la isotrópica y la de traslación movían mucho el error de xc (×%s frente a ×%s)",
          "porque la ventana urbana es irregular; aquí, sobre un rectángulo, dan casi lo mismo",
          "(%s y %s de error estándar para G)."),
          f(val("c5m11_z_pois"), 2), f(val("c5m11_z_th_tr"), 2),
          f(kp$trans$se_D / se_ppm[["D"]], 1), f(z_ppm[["D"]], 2), f(kp$trans$z_D, 2),
          f(kp$trans$se_G / se_ppm[["G"]], 1), f(z_ppm[["G"]], 2), f(kp$trans$z_G, 2),
          f(val("c5m11_th_iso_inf"), 2), f(val("c5m11_th_tr_inf"), 2),
          f(kp$iso$se_G, 3), f(kp$trans$se_G, 3)))
    ),
    lectura = paste(
      "El diagnóstico contra el modelo dice si la intensidad variable basta para explicar las",
      "parejas, y su respuesta depende del tramo de r que se declaró. Lo que no dice es si los",
      "puntos son independientes, y de eso depende la inferencia sobre los coeficientes: sus",
      "errores estándar se escriben con un modelo que tenga en cuenta la dependencia, como el",
      "de Thomas. El ejercicio 2 vio que dentro del greenstone el oro se agrupa; este dice que",
      "la falla y la roca no bastan para explicarlo a pocos kilómetros.")
  )
)
message("  E5 · diagnóstico y conglomerados")

# Ningún ejercicio puede dejar una demanda sin contestar.
for (k in names(EJ)) {
  sc <- sin_contestar(EJ[[k]])
  if (length(sc)) para("el ejercicio ", k, " deja sin contestar: ", paste0("«", sc, "»", collapse = "; "))
}

# =====================================================================
# LAS SERIES DE LOS GRÁFICOS
#
# Todas salen de los capítulos, y cada serie guarda su ruta de origen para
# que el auditor la vuelva a resolver: un gráfico que dibuja una serie vieja
# miente igual que una cifra vieja, y nadie lo ve porque la curva sigue
# teniendo buena pinta. Lo que el texto alternativo afirma de la FORMA —dónde
# está el máximo, si baja de 1, qué rejillas respetan el supuesto— se resume
# aquí y se comprueba, no se decide en el ensamblador.
# =====================================================================
serie <- function(doc, ruta) {
  v <- en_ruta(CAPS[[doc]], ruta)
  if (is.null(v)) para("no existe la serie ", doc, ":", ruta)
  unlist(v)
}
desde <- function(doc, rutas) lapply(rutas, function(x) list(origen = unname(ARCHIVO[doc]), ruta = x))

# A2 · el histograma de los conteos y su referencia de media común
h_c <- serie("cap4", "m2.urbana_hist.centros"); h_o <- serie("cap4", "m2.urbana_hist.conteo")
h_t <- serie("cap4", "m2.urbana_hist.teorico"); h_b <- serie("cap4", "m2.urbana_hist.bordes")
if (sum(h_o) != val("c4m2_celdas")) para("el histograma no cuenta las celdas vivas")
der <- h_b[-1]; izq <- h_b[-length(h_b)]
G_HIST <- list(
  modulo = "cap4.m2", titulo = "Sedes por celda: lo observado y una Poisson de media común",
  centros = h_c, observado = h_o, referencia = h_t,
  forma = list(
    corte_bajo = 10L, corte_alto = 60L, ancho_tramo = h_b[2] - h_b[1],
    obs_hasta_10 = sum(h_o[der <= 10]), ref_hasta_10 = r10(sum(h_t[der <= 10])),
    obs_desde_60 = sum(h_o[izq >= 60]), ref_desde_60 = r10(sum(h_t[izq >= 60])),
    media = val("c4m2_media")),
  desde = desde("cap4", c(centros = "m2.urbana_hist.centros", observado = "m2.urbana_hist.conteo",
                          referencia = "m2.urbana_hist.teorico"))
)

# A6 · la esperanza mínima por rejilla sobre la ventana urbana
s_nx <- serie("cap4", "m6.bogota.nx"); s_em <- serie("cap4", "m6.bogota.esperanza_min")
s_cb <- serie("cap4", "m6.bogota.celdas_esperanza_baja"); s_ce <- serie("cap4", "m6.bogota.celdas")
respetan_bog <- s_nx[s_em >= 5]
# La pregunta existe porque NO es un tramo inicial: si algún día lo fuera,
# «se rompe a saltos» sería falso.
if (identical(respetan_bog, s_nx[seq_along(respetan_bog)]))
  para("las rejillas urbanas que respetan el supuesto ya son un tramo inicial: A6 dice lo contrario")
# La referencia nueva de A6: las mismas sedes en un rectángulo de la misma
# área, donde cada celda de una rejilla k × k espera n/k². Separa lo que pone
# la GEOMETRÍA (las celdas recortadas) de lo que no pone ni el número de
# sedes ni su patrón, porque la esperanza no mira dónde están.
rect_em <- val("c4m1_n_urb") / s_nx^2
if (any(rect_em < 5)) para("A6: en el rectángulo de la misma área alguna rejilla ya baja de 5, y la pregunta dice que no")
G_SUPUESTO <- list(
  modulo = "cap4.m6", titulo = "Esperanza mínima de una celda según la rejilla, ventana urbana",
  nx = s_nx, esperanza_min = s_em, celdas_baja = s_cb, celdas = s_ce,
  rectangulo = r10(rect_em),
  forma = list(respetan = as.list(respetan_bog), rect_min = r10(min(rect_em)),
               rect_nx_min = max(s_nx), n = val("c4m1_n_urb")),
  desde = desde("cap4", c(nx = "m6.bogota.nx", esperanza_min = "m6.bogota.esperanza_min",
                          celdas_baja = "m6.bogota.celdas_esperanza_baja", celdas = "m6.bogota.celdas"))
)

# A9 · la correlación de pares de las sedes
g_r <- serie("cap4", "m9.bogota.r"); g_g <- serie("cap4", "m9.bogota.g_obs")
vivo <- g_r > 0
if (abs(max(g_g[vivo]) - val("c4m9_g_max")) > 1e-9 || g_r[vivo][which.max(g_g[vivo])] != g_r[vivo][1])
  para("el máximo de g de las sedes ya no está en el primer nodo del barrido")
if (min(g_g[vivo]) < 1) para("la g de las sedes ya baja de 1 en el barrido, y A9 dice que no")
# A9 lee la curva en un nodo, el más cercano a 3 km: qué afirma ese valor
# (el anillo, no el disco). Para el distractor del disco se lee K/πr² en el
# mismo radio sobre la envolvente del capítulo 4, que comparte la rejilla.
i_lec <- which.min(abs(g_r - 3000))
c4_r <- serie("cap4", "m11.bogota.r"); c4_o <- serie("cap4", "m11.bogota.obs"); c4_t <- serie("cap4", "m11.bogota.teo")
j_lec <- which.min(abs(c4_r - g_r[i_lec]))
if (abs(c4_r[j_lec] - g_r[i_lec]) > 1) para("A9: la rejilla de g y la de K del capítulo 4 ya no comparten el nodo de 3 km")
lect <- list(r = g_r[i_lec], g = r10(g_g[i_lec]), pct = r10(100 * (g_g[i_lec] - 1)),
             disco = r10(c4_o[j_lec] / c4_t[j_lec]))
if (!(lect$g > 1 && lect$disco > lect$g)) para("A9: en el nodo de 3 km el disco ya no acumula más exceso que el anillo")
G_PCF <- list(
  modulo = "cap4.m9", titulo = "Correlación de pares de las sedes, ventana urbana",
  r = g_r, g = g_g,
  forma = list(g_min = r10(min(g_g[vivo])), r_g_min = g_r[vivo][which.min(g_g[vivo])],
               lectura = lect),
  desde = desde("cap4", c(r = "m9.bogota.r", g = "m9.bogota.g_obs"))
)

# B2 · el pico contra el ancho de banda
G_PICO <- list(
  modulo = "cap5.m2", titulo = "Intensidad máxima de la superficie según el ancho de banda, Kennedy",
  sigma = val("c5m2_sigmas"), maximo = val("c5m2_maximos"),
  desde = desde("cap5", c(sigma = "m2.familia.sigmas_m", maximo = "m2.familia.max_km2"))
)

# B10 · la K inhomogénea dividida por la media del modelo, que es la vista
# de entrada del simulador del módulo 10. El cociente se hace aquí, en R.
k_r <- serie("cap5", "m10.curva.r"); k_o <- serie("cap5", "m10.curva.obs")
k_lo <- serie("cap5", "m10.curva.lo"); k_hi <- serie("cap5", "m10.curva.hi")
k_mm <- serie("cap5", "m10.curva.mmean")
v2 <- k_r > 0
fuera_k <- k_r[v2][k_o[v2] > k_hi[v2] | k_o[v2] < k_lo[v2]]
if (abs(min(fuera_k) - val("c5m10_primer")) > 1e-6 || abs(max(fuera_k) - val("c5m10_ultimo")) > 1e-6)
  para("el tramo fuera de la banda ya no va de ", val("c5m10_primer"), " a ", val("c5m10_ultimo"))
if (any(k_o[v2] < k_lo[v2])) para("la K inhomogénea sale ahora también por debajo, y B10 dice que solo por arriba")
G_KINHOM <- list(
  modulo = "cap5.m10", titulo = "K inhomogénea de las sedes dividida por la media de las simulaciones del modelo",
  r = k_r[v2], observada = r10(k_o[v2] / k_mm[v2]), baja = r10(k_lo[v2] / k_mm[v2]), alta = r10(k_hi[v2] / k_mm[v2]),
  forma = list(max_cociente = r10(max(k_o[v2] / k_mm[v2])),
               r_max_cociente = k_r[v2][which.max(k_o[v2] / k_mm[v2])]),
  desde = desde("cap5", c(r = "m10.curva.r", obs = "m10.curva.obs", lo = "m10.curva.lo",
                          hi = "m10.curva.hi", mmean = "m10.curva.mmean"))
)
# C1 · las mismas sedes contra dos referencias: la K del capítulo 4 dividida
# por πr² con la banda de CSR, y la K inhomogénea del capítulo 5 dividida por
# la media de su modelo con la banda del modelo. Las dos rejillas de r son la
# misma (se comprueba) y las dos curvas quedan en la escala del 1.
c_r <- serie("cap4", "m11.bogota.r"); c_o <- serie("cap4", "m11.bogota.obs")
c_lo <- serie("cap4", "m11.bogota.lo"); c_hi <- serie("cap4", "m11.bogota.hi")
c_te <- serie("cap4", "m11.bogota.teo")
# El capítulo 4 guarda r con seis cifras significativas y el 5 con diez:
# se compara en relativo.
if (length(c_r) != length(k_r) || max(abs(c_r - k_r) / pmax(k_r, 1)) > 1e-5)
  para("las rejillas de r de la envolvente del capítulo 4 y la del 5 ya no son la misma")
v3 <- c_r > 0
if (!all(c_o[v3] > c_hi[v3]))
  para("la K de las sedes ya no queda por encima de la banda de CSR en todo el barrido, y C1 lo dice")
G_DOS <- list(
  modulo = "cap5.m10", titulo = "Las sedes contra CSR y contra su modelo ajustado",
  r = c_r[v3],
  csr_observada = r10(c_o[v3] / c_te[v3]), csr_baja = r10(c_lo[v3] / c_te[v3]), csr_alta = r10(c_hi[v3] / c_te[v3]),
  mod_observada = r10(k_o[v3] / k_mm[v3]), mod_baja = r10(k_lo[v3] / k_mm[v3]), mod_alta = r10(k_hi[v3] / k_mm[v3]),
  forma = list(csr_primera = r10(c_o[v3][1] / c_te[v3][1]), csr_ultima = r10(tail(c_o[v3] / c_te[v3], 1)),
               csr_alta_ultima = r10(tail(c_hi[v3] / c_te[v3], 1)),
               mod_primera = r10(k_o[v3][1] / k_mm[v3][1]), mod_ultima = r10(tail(k_o[v3] / k_mm[v3], 1)),
               mod_alta_ultima = r10(tail(k_hi[v3] / k_mm[v3], 1)),
               # Qué parte del exceso sobre 1 se llevó la intensidad variable, en
               # el primer nodo y en el último (C1).
               exceso_csr_primera = r10(c_o[v3][1] / c_te[v3][1] - 1),
               exceso_mod_primera = r10(k_o[v3][1] / k_mm[v3][1] - 1),
               llevado_primera_pct = r10(100 * (1 - (k_o[v3][1] / k_mm[v3][1] - 1) / (c_o[v3][1] / c_te[v3][1] - 1))),
               exceso_csr_ultima = r10(tail(c_o[v3] / c_te[v3], 1) - 1),
               exceso_mod_ultima = r10(tail(k_o[v3] / k_mm[v3], 1) - 1)),
  desde = c(desde("cap4", c(r = "m11.bogota.r", obs = "m11.bogota.obs", lo = "m11.bogota.lo",
                            hi = "m11.bogota.hi", teo = "m11.bogota.teo")),
            desde("cap5", c(obs5 = "m10.curva.obs", lo5 = "m10.curva.lo", hi5 = "m10.curva.hi",
                            mmean = "m10.curva.mmean")))
)
GRAFICOS <- list(g_hist = G_HIST, g_supuesto = G_SUPUESTO, g_pcf = G_PCF,
                 g_pico = G_PICO, g_kinhom = G_KINHOM, g_dos = G_DOS)
for (nm in names(GRAFICOS)) {
  g <- GRAFICOS[[nm]]
  largos <- vapply(g[!names(g) %in% c("modulo", "titulo", "forma", "desde")], length, integer(1))
  if (length(unique(largos)) != 1)
    para("el gráfico ", nm, " tiene series de largos distintos: ", paste(largos, collapse = ", "))
}

# =====================================================================
# EL CATÁLOGO DE ERRORES: los que no dan error
# =====================================================================
# `claves` viaja como LISTA aunque tenga una sola cifra: con `auto_unbox`,
# jsonlite escribe un vector de longitud 1 como una cadena suelta, y el
# ensamblador la recorría letra a letra (pasó con la tarjeta de la pared).
err <- function(id, titulo, doc, modulo, claves, dice, nuevas = list())
  list(id = id, titulo = titulo, doc = doc, modulo = modulo, claves = as.list(claves),
       dice = dice, nuevas = nuevas)
nueva <- function(ruta, que) list(ruta = ruta, que = que)
ERRORES <- list(
  err("ventana", "Publicar una intensidad sin su ventana", "cap4", 1,
      c("c4m1_lambda_urb", "c4m1_lambda_dc", "c4m1_factor"),
      "la cifra es correcta con una ventana e incompleta sin ella, y ppp() descarta los puntos de fuera con un aviso que se pierde en la consola"),
  err("dispersion", "Comparar el índice de dispersión con 1 cuando las celdas están recortadas", "cap4", 2,
      c("c4m2_dispersion", "c4m2_disp_nula"),
      "con celdas de áreas distintas, un Poisson homogéneo ya da un índice muy por encima de 1"),
  err("cuadrantes", "Tomar «no rechaza el test de cuadrantes» por aleatoriedad", "cap4", 5,
      c("c4m5_chi2", "c4m5_ce_orig", "c4m5_ce_reb"),
      paste("el χ² solo lee cuántos puntos hay en cada celda. Las plántulas de secuoya y su versión rebarajada dentro",
            "de cada celda —los mismos conteos, sin los grumos— dan el mismo χ²: el test no ve lo que pasa por debajo",
            "de su rejilla. Aquí los dos rechazan; si no rechazaran, tampoco dirían nada de lo que pasa dentro de las celdas")),
  err("supuesto", "Elegir la rejilla sin mirar el supuesto del χ²", "cap4", 6,
      c("c4m2_esp_baja", "c4m6_red_rechazos"),
      paste("afinar la rejilla da más detalle y puede dejar celdas que esperan menos de 5 puntos, que es lo que rompe",
            "la aproximación de la que sale el p-valor, y el p-valor sigue saliendo minúsculo"),
      nuevas = list(nueva("supuesto_rw.rechazos_sin_supuesto",
        "De esos rechazos de las secuoyas, los que se apoyan en rejillas con alguna celda que espera menos de 5 plántulas"))),
  err("borde", "Ignorar el efecto de borde", "cap4", 10,
      c("c4m10_sesgo", "c4m10_veces_iso"),
      paste("sin corregir, a los puntos cerca del borde les faltan vecinos —nunca les sobran—, y el patrón parece más",
            "regular de lo que es. Si tienta saltarse la corrección, es por lo que cuesta, no porque sirva poco")),
  err("banda", "Leer la banda puntual como un contraste de la curva entera", "cap4", 11,
      c("c4m11_tasa_bog", "c4m11_nivel", "c5m10_tasa", "c5m10_veces_nivel"),
      "mirar cientos de distancias a la vez y quedarse con la peor no es un contraste al nivel de la banda"),
  err("atraccion", "Leer un exceso de parejas como atracción", "cap5", 10,
      c("c4m8_max_desvio", "c4m8_vecinas", "c4m8_vecinas_csr", "c5m10_pct_fuera"),
      paste("contra CSR, una intensidad que cambia de un sitio a otro deja la misma huella que unos puntos que se",
            "atraen. Las sedes tienen un exceso claro contra CSR, y contra un modelo que ya lleva la intensidad",
            "variable su K inhomogénea todavía se sale de la banda en buena parte de los radios: parte del exceso era",
            "intensidad y parte no, y solo el segundo contraste empieza a separarlos")),
  err("pared", "Publicar la pared del intervalo como el ancho óptimo", "cap5", 3,
      c("c5m3_tope_jp"),
      "el selector devuelve un número finito, con el aspecto de cualquier otro, y el aviso se queda en la consola",
      nuevas = list(nueva("tope_ppl.csr_chocan_en_el_tope",
        "De las veinte realizaciones de CSR en el rectángulo de 3 × 4 km de la pregunta 3 del bloque B, en cuántas devuelve bw.ppl justo su tope"))),
  err("masa", "Creer que la corrección de borde por defecto conserva la masa", "cap5", 4,
      c("c5m4_n", "c5m4_masa_sin", "c5m4_masa_def", "c5m4_masa_dig"),
      paste("sin corregir, con la corrección por defecto y con la de Diggle, las tres superficies salen plausibles,",
            "y solo la de Diggle integra el número de puntos")),
  err("relrisk", "Publicar el relrisk del revés", "cap5", 6,
      c("c5m6_orient_ch", "c5m6_ch_global", "c5m6_orient_bog", "c5m6_bog_global"),
      paste("la función relrisk pinta la probabilidad del segundo nivel del factor, y los niveles van por orden",
            "alfabético: en chorley, larynx va antes que lung, así que sin reordenar pinta la probabilidad de pulmón,",
            "la de los controles")),
  err("rhohat", "Leer el titular de una curva rhohat, la razón entre su máximo y su mínimo", "cap5", 7,
      c("c5m7_razon_bog", "c5m7_bulto_bog"),
      paste("esa razón la fija una cola, donde casi no hay puntos con que estimar la curva: en las sedes, la cola",
            "que manda es la del mínimo, lejos del centro, donde apenas quedan sedes")),
  err("cuadratura", "Comparar por AIC dos ppm cuya integral se calculó distinto", "cap5", 8,
      c("c5m8_gana_ppm", "c5m8_gana_const", "c5m8_sin_contar"),
      "la cuadratura deja trozos de ventana sin contar, y esa área que falta entra en el AIC como si fuera del modelo"),
  err("coordenadas", "Ajustar un ppm con coordenadas de siete cifras", "cap5", 9,
      c("c5m9_cond", "c5m9_mejora"),
      "el ajuste devuelve coeficientes y ningún error estándar, y vcov() avisa y devuelve NULL en vez de fallar"),
  err("z_poisson", "Leer la z de un Poisson cuando los puntos vienen en grupos", "cap5", 11,
      c("c5m11_z_pois", "c5m11_z_th_tr", "c5m11_deff"),
      "los errores estándar del Poisson suponen puntos independientes y se quedan cortos sin avisar"),
  err("kppm", "Ajustar un modelo de conglomerado sin decir con qué K", "cap5", 11,
      c("c5m11_th_iso_mu", "c5m11_th_tr_mu", "c5m11_mu_pct", "c5m11_mat_iso_mu"),
      paste("la llamada a kppm elige la corrección de K por ti, y cambiarla mueve las sedes por conglomerado",
            "mucho más que cambiar de familia de modelo"))
)
for (e in ERRORES) {
  if (!paste0(e$doc, ".m", e$modulo) %in% esperados) para("el error ", e$id, " apunta fuera del alcance")
  falt <- setdiff(e$claves, names(REUTILIZADO))
  if (length(falt)) para("el error ", e$id, " cita claves que no existen: ", paste(falt, collapse = ", "))
  for (nv in e$nuevas) if (is.null(en_ruta(NUEVO, nv$ruta))) para("el error ", e$id, " cita nuevo:", nv$ruta)
}

# =====================================================================
# ANCLAS. Paran el guion; cada una compara contra algo calculado por otro.
# =====================================================================
ancla <- function(nombre, obtenido, esperado, tol) {
  if (!isTRUE(abs(obtenido - esperado) <= tol))
    para("ANCLA ROTA · ", nombre, ": ", format(obtenido, digits = 12),
         " contra ", format(esperado, digits = 12), " (tolerancia ", tol, ")")
  invisible(TRUE)
}
ancla_cierto <- function(nombre, condicion) if (!isTRUE(condicion)) para("ANCLA ROTA · ", nombre)

ancla("A3 la R urbana reproduce la del capítulo 4", N_CE$ce_urb, val("c4m3_ce_bog"), 1e-6)
ancla("A3 la ventana urbana tiene las sedes del capítulo 4", N_CE$n_urb, val("c4m1_n_urb"), 0)
ancla("A3 la ventana del D.C. tiene las sedes del capítulo 4", N_CE$n_dc, val("c4m1_n_dc"), 0)
ancla("A3 la λ del D.C. es la del capítulo 4", N_CE$lambda_dc_km2, val("c4m1_lambda_dc"), 1e-6)
ancla("A5 el original reproduce el χ² 5 × 5 del capítulo", N_REB$chi2_5_orig, val("c4m5_chi2"), 1e-6)
ancla("A5 el rebarajado reproduce el χ² 5 × 5 del capítulo", N_REB$chi2_5_reb, val("c4m5_chi2"), 1e-6)
ancla_cierto("A5 a 10 × 10 los dos χ² ya no coinciden", abs(N_REB$chi2_10_orig - N_REB$chi2_10_reb) > 1)
ancla("A11 el nrank da un contraste al 5 %", 2 * N_NRANK$correcto / (NS + 1), NIVEL, 1e-12)
ancla_cierto("A11 el nrank es entero", N_NRANK$correcto == round(N_NRANK$correcto))
ancla("B3 el tope es la mitad de la diagonal", N_TOPE$correcto, sqrt(3000^2 + 4000^2) / 2, 1e-9)
ancla_cierto("B3 chocar es lo normal en CSR", N_TOPE$csr_chocan_en_el_tope >= N_TOPE$csr_realizaciones / 2)
ancla("B6 el riesgo relativo devuelve la probabilidad", N_RR$correcto / (1 + N_RR$correcto), pmax_ch, 1e-12)
ancla("B8 la cuadratura por la intensidad forzada da n", N_FORZADO$correcto * N_FORZADO$suma_pesos_km2,
      N_FORZADO$n, 1e-6)
ancla_cierto("B8 la forzada se distingue de n/|W| a la precisión pedida",
             abs(N_FORZADO$correcto - N_FORZADO$distractores[[1]]$valor) > 0.005)
ancla("B1 Kennedy reproduce la λ del capítulo 5", N_FORZADO$distractores[[1]]$valor, val("c5m1_lambda_ken"), 1e-6)
ancla_cierto("B3 los que no chocan devuelven un ancho finito, por debajo del tope",
             N_TOPE$csr_sigma_max_m < N_TOPE$correcto)
ancla("C5 el tamaño efectivo por el efecto de diseño devuelve n", N_NEFF$correcto * N_NEFF$efecto_diseno, n_bog, 1e-6)
ancla("C5 el de Thomas reproduce el del capítulo", n_bog / val("c5m11_deff"), val("c5m11_neff"), 1e-6)
ancla("A1 el resto del D.C. tiene las sedes que le faltan a la ciudad", N_RESTO$n_resto,
      val("c4m1_n_dc") - val("c4m1_n_urb"), 0)
ancla("A1 el área del resto es la del D.C. menos la urbana", N_RESTO$area_resto_km2,
      val("c4m1_area_dc") - val("c4m1_area_urb"), 1e-4)
ancla("A4 el montaje denso es el del capítulo con diez veces λ", N_DENSO$n_real * N_DENSO$lambda,
      val("c4m4_n_real") * 10 * val("c4m4_lambda"), 0)
ancla("E1 los 255 yacimientos del enunciado", N_ORO, 255, 0)
ancla("E4 la diferencia de AIC es 2n·ln(10⁶)", dif_aic, 2 * N_ORO * log(1e6), 1e-6)
ancla("el alcance son 22 módulos", length(esperados), 22, 0)
N_ANCLAS <- 24L

# =====================================================================
D <- list(
  meta = list(
    documento = "preparcial-corte-2", corte = "II",
    fecha_parcial = FECHA_PARCIAL, generado = as.character(Sys.Date()),
    semilla = SEMILLA, n_modulos_alcance = length(esperados),
    n_reutilizadas = length(REUTILIZADO), n_nuevas = length(NUEVO),
    n_graficos = length(GRAFICOS), n_errores = length(ERRORES),
    n_ejercicios = length(EJ), n_anclas = N_ANCLAS, alcance = esperados,
    r_version = R.version.string,
    paquetes = list(spatstat = as.character(packageVersion("spatstat")),
                    spatstat.model = as.character(packageVersion("spatstat.model")),
                    sf = as.character(packageVersion("sf")))
  ),
  reutilizado = REUTILIZADO,
  nuevo = NUEVO,
  graficos = GRAFICOS,
  errores = ERRORES,
  ejercicios = EJ
)
txt <- toJSON(D, auto_unbox = TRUE, digits = I(10), null = "null", na = "null")
if (grepl('"NA"', txt, fixed = TRUE)) para("hay NA escritos como la cadena \"NA\"")
if (grepl("<U\\+", txt)) para("el JSON lleva codificación rota")
destino <- file.path(SALIDAS, "preparcial2_datos.json")
writeLines(txt, destino, useBytes = TRUE)
message(sprintf("  preparcial2_datos.json: %.1f KB", file.size(destino) / 1024))
message(sprintf("  %d cifras reutilizadas · %d cálculos nuevos · %d gráficos · %d errores · %d ejercicios · %d anclas",
                length(REUTILIZADO), length(NUEVO), length(GRAFICOS), length(ERRORES), length(EJ), N_ANCLAS))
