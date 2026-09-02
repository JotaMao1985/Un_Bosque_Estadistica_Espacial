# =====================================================================
# T0.3 — geo.R · el lado de R del componente .geomapa
#
# Material de Estadística Espacial 2026-II (20929).
#
# La cadena es siempre la misma:
#     proyectar -> simplificar -> cuantizar -> serializar
#
# Decisiones que conviene entender antes de tocar nada:
#
# 1. La geometría se serializa en COORDENADAS PROYECTADAS cuantizadas a
#    enteros 0..Q, no en píxeles. El ajuste al lienzo lo hace el
#    navegador, que es quien conoce su tamaño; así el mismo JSON sirve
#    para un canvas de 300 px y para uno de 900 sin volver a generarlo.
#
# 2. Los ARRAYS SON PLANOS: [x0,y0,x1,y1,...] en vez de [[x0,y0],...].
#    En JSON eso ahorra ~40 % de bytes, y el presupuesto del capítulo es
#    de 120 KB de geometría.
#
# 3. Los CORTES DE CLASE LOS CALCULA R, no JS. Es la regla del plan
#    (D10) y además evita reimplementar Fisher-Jenks en el navegador.
#    Ojo con el hallazgo A.2: classInt usa [a,b) y mapclassify (a,b].
#    Aquí manda la convención de classInt, y el JS la respeta.
#
# 4. Nada de esto pinta: pintar es del .geomapa en el HTML.
# =====================================================================

suppressPackageStartupMessages({
  library(sf)
  library(jsonlite)
  library(classInt)
  library(methods)      # `as()` de CIELAB; Rscript no siempre lo adjunta
  library(colorspace)   # T2.4: referencia externa de la simulación de daltonismo
})

# Cuantización: 0..QMAX. Con 4096 el error máximo de posición es de
# 1/4096 del ancho del mapa; sobre un canvas de 900 px son 0,22 px, o
# sea invisible. Subirlo engorda el JSON sin que se note nada.
QMAX <- 4096L

# ---------------------------------------------------------------------
# geo_simplifica — baja la geometría hasta un presupuesto de vértices
#
# Busca por bisección el `keep` de rmapshaper que deja el objeto justo
# por debajo del presupuesto. `keep_shapes = TRUE` es obligatorio: sin
# él, ms_simplify BORRA los polígonos pequeños y un mapa de municipios
# pierde municipios en silencio.
# ---------------------------------------------------------------------
geo_n_vertices <- function(x) {
  sum(vapply(sf::st_geometry(x), function(g) nrow(sf::st_coordinates(g)), integer(1)))
}

geo_simplifica <- function(x, presupuesto = 8000L, verbose = TRUE) {
  n0 <- geo_n_vertices(x)
  if (n0 <= presupuesto) {
    if (verbose) message(sprintf("  sin simplificar: %d vertices <= %d", n0, presupuesto))
    return(x)
  }
  lo <- 0.001; hi <- 1.0; mejor <- NULL; keep_mejor <- NA_real_
  for (i in 1:14) {
    mid <- (lo + hi) / 2
    cand <- try(rmapshaper::ms_simplify(x, keep = mid, keep_shapes = TRUE), silent = TRUE)
    # Un fallo de ms_simplify NO dice que haga falta MENOS detalle; hay
    # que estrechar por arriba, no por abajo.
    if (inherits(cand, "try-error")) { hi <- mid; next }
    n <- geo_n_vertices(cand)
    if (n <= presupuesto) { mejor <- cand; keep_mejor <- mid; lo <- mid } else { hi <- mid }
    # OJO: el corte por cercanía solo vale si YA hay un candidato
    # admisible. Sin esta guarda, un n de 1403 frente a un presupuesto de
    # 1400 rompe el bucle dejando `mejor` en NULL, y la función muere
    # diciendo que el presupuesto es inalcanzable cuando no lo es.
    if (!is.null(mejor) && abs(n - presupuesto) < presupuesto * 0.03) break
  }

  if (is.null(mejor)) {
    # El suelo de ms_simplify con keep_shapes = TRUE es estructural: cada
    # polígono conserva un anillo mínimo, así que un objeto con muchos
    # rasgos no baja de ~4 vértices por parte por mucho que se insista.
    # Eso no es un error del que llama: se avisa con la cifra real y se
    # devuelve el suelo, para que decida si reduce rasgos o sube el
    # presupuesto.
    suelo <- rmapshaper::ms_simplify(x, keep = 0.001, keep_shapes = TRUE)
    n_suelo <- geo_n_vertices(suelo)
    if (n_suelo > presupuesto)
      warning(sprintf(paste("presupuesto de %d vertices inalcanzable: el suelo de %d rasgos es %d.",
                            "Reduce rasgos (p. ej. disolviendo) o sube el presupuesto."),
                      presupuesto, nrow(x), n_suelo))
    mejor <- suelo; keep_mejor <- 0.001
  }
  if (verbose) message(sprintf("  simplificado: %d -> %d vertices (keep = %.4f)",
                               n0, geo_n_vertices(mejor), keep_mejor))
  # Simplificar puede romper la validez topologica; se repara y se avisa.
  malos <- !sf::st_is_valid(mejor)
  if (any(malos, na.rm = TRUE)) {
    if (verbose) message(sprintf("  %d geometria(s) invalida(s) tras simplificar -> st_make_valid",
                                 sum(malos, na.rm = TRUE)))
    mejor <- sf::st_make_valid(mejor)
  }
  mejor
}

# ---------------------------------------------------------------------
# geo_cuantiza — de coordenadas proyectadas a enteros 0..QMAX
#
# Devuelve la caja original para que el navegador pueda rotular ejes o
# calcular escalas reales si hiciera falta.
# ---------------------------------------------------------------------
geo_caja <- function(x) as.numeric(sf::st_bbox(x))   # xmin, ymin, xmax, ymax

geo_q <- function(v, lo, rango) as.integer(round((v - lo) / rango * QMAX))

# ---------------------------------------------------------------------
# Codificación por DIFERENCIAS (T2.4)
#
# Los vértices consecutivos de un anillo están pegados: guardar
# [x0, y0, dx1, dy1, ...] en vez de las coordenadas absolutas convierte
# números de tres o cuatro cifras en números de una o dos. Sobre los
# 1 122 municipios de Colombia son un 33 % menos de bytes, medido, con
# round-trip exacto (son enteros: no hay pérdida posible).
#
# Va como OPCIÓN y no por defecto, y eso es deliberado: los capítulos 1
# y 2 ya están publicados y verificados con la codificación absoluta, y
# cambiarles el JSON por debajo obligaría a regenerarlos y volver a
# auditarlos para ahorrar unos kilobytes que no les hacen falta. El
# navegador lee `codificacion` del propio mapa, así que los dos formatos
# conviven sin que nadie tenga que acordarse de nada.
# ---------------------------------------------------------------------
geo_delta <- function(p) {
  n <- length(p)
  if (n <= 2L) return(p)
  x <- p[seq(1, n, by = 2)]; y <- p[seq(2, n, by = 2)]
  as.integer(rbind(c(x[1], diff(x)), c(y[1], diff(y))))
}

# Aplana un sfg a lista de partes, cada una un vector plano cuantizado.
geo_partes <- function(g, caja, q = QMAX) {
  rx <- caja[3] - caja[1]; ry <- caja[4] - caja[2]
  r  <- max(rx, ry)               # MISMA escala en x e y: no deformar
  cx <- caja[1] + rx / 2; cy <- caja[2] + ry / 2
  qx <- function(v) as.integer(round((v - (cx - r/2)) / r * q))
  qy <- function(v) as.integer(round((v - (cy - r/2)) / r * q))

  m <- sf::st_coordinates(g)
  # L1/L2 identifican anillo y polígono según el tipo
  cols <- intersect(c("L1", "L2", "L3"), colnames(m))
  if (length(cols) == 0) {
    return(list(as.integer(rbind(qx(m[, 1]), qy(m[, 2])))))
  }
  clave <- do.call(paste, c(as.data.frame(m[, cols, drop = FALSE]), sep = "-"))
  lapply(split(seq_len(nrow(m)), factor(clave, levels = unique(clave))), function(idx) {
    as.integer(rbind(qx(m[idx, 1]), qy(m[idx, 2])))
  })
}

# ---------------------------------------------------------------------
# geo_cortes — clases con classInt, calculadas en R
#
# Devuelve los cortes Y la asignación de clase, para que el navegador no
# tenga que reimplementar la regla del intervalo (ver hallazgo A.2).
# ---------------------------------------------------------------------
geo_cortes <- function(v, n = 5, estilo = "quantile") {
  v <- as.numeric(v)
  fin <- is.finite(v)
  ci <- classInt::classIntervals(v[fin], n = n, style = estilo)
  # `findCols` devuelve una clase por valor FINITO, no por elemento de `v`.
  # Devolverla tal cual dejaba `clase` más corto que `valor` en cuanto
  # había un solo NA, y el navegador coloreaba desplazado a partir de ahí
  # sin que nada fallara. Se realinea contra el vector completo y los
  # ausentes salen como NA declarado, que el .geomapa pinta sin color.
  clase <- rep(NA_integer_, length(v))
  clase[fin] <- as.integer(classInt::findCols(ci))
  list(estilo = estilo, n = n,
       cortes = as.numeric(ci$brks),
       clase  = clase,
       n_sin_dato = sum(!fin),
       tam    = as.integer(table(factor(clase, levels = seq_len(n)))))
}

# ---------------------------------------------------------------------
# Constructores por modo. Todos devuelven una lista lista para toJSON.
# ---------------------------------------------------------------------

#' Modo `poligonos` — coropleto
#'
#' Argumentos añadidos en T2.4, todos RETROCOMPATIBLES (quien no los pasa
#' obtiene exactamente el JSON de T0.3):
#'
#'   `caja`     caja de cuantización EXPLÍCITA, en las unidades del CRS.
#'              Existe por el módulo 7: un cartograma y su coropleto tienen
#'              que cuantizarse contra la MISMA caja o el navegador reescala
#'              cada uno para llenar su lienzo y **desaparece justo lo que el
#'              cartograma quiere enseñar**, que es que unas áreas crecen y
#'              otras encogen. Con caja compartida el mapa se lee; sin ella,
#'              los dos mapas salen del mismo tamaño y la deformación se ve
#'              como un cambio de forma, no de área.
#'
#'   `vistas`   lista con nombre de especificaciones de clasificación, cada
#'              una `list(estilo=, n=)`. El capítulo 3 pinta el MISMO mapa
#'              bajo cinco esquemas; guardar cinco mapas costaría cinco
#'              copias de la geometría —el presupuesto es de 120 KB para el
#'              capítulo entero— y aquí la geometría se paga UNA vez y cada
#'              esquema añade solo su vector de clases y sus cortes.
#'
#'   `puntos_*` capa de puntos superpuesta al coropleto, para los símbolos
#'              proporcionales y el dot density del módulo 7. `puntos_modo`
#'              declara cuál de los dos es —igual que `marcas_tipo` en
#'              `geo_puntos()`: el navegador NO lo adivina—, porque un mismo
#'              vector de coordenadas se dibuja con radio proporcional en un
#'              caso y con radio constante en el otro.
#'   `capas`    varias VARIABLES sobre la misma geometría, cada una con
#'              sus propias vistas de clasificación. Es el escalón por
#'              encima de `vistas`: aquélla reclasifica un mismo valor,
#'              ésta cambia de valor. El capítulo 3 pinta los 1 122
#'              municipios cuatro veces —deserción, conteo, tasa y
#'              presencia en la cohorte— y la geometría de esa capa cuesta
#'              150 KB: pagarla cuatro veces son 600 KB, y el presupuesto
#'              del capítulo entero es de 120.
#'
#'   `q`        cuantización de ESTE mapa. Por defecto QMAX (4096). Un
#'              mapa de 1 122 municipios sobre un lienzo de 900 px no
#'              necesita 4096 pasos —el error de 1/1024 son 0,88 px, o sea
#'              menos que un píxel— y bajarlo acorta cada coordenada un
#'              carácter. No se toca a la ligera: sobre un mapa de pocos
#'              rasgos grandes se notaría.
#'
#' Argumentos añadidos en T2.7 DEL CAPÍTULO 1 (su módulo 7 los pedía), todos
#' RETROCOMPATIBLES igual que los de arriba:
#'
#'   `lineas`   lista de matrices de 2 columnas — polilíneas SOBRE el
#'              coropleto. Es la misma capacidad que `geo_puntos()` tiene
#'              desde T1.1 para las calles de Soho, traída aquí porque hay
#'              una segunda geometría que no es ni una variable más sobre
#'              los mismos polígonos (eso es `capas`) ni una nube de puntos
#'              (eso es `superpuestos`): la rejilla de 100 rectángulos que
#'              el módulo 7 le pone encima a Carolina del Norte.
#'
#'              SE CUANTIZAN CONTRA LA MISMA CAJA Y LA MISMA `q` DE ESTE
#'              MAPA, y ahí está todo el asunto. `geo_puntos()` usa QMAX
#'              porque no tiene otra; aquí `q` es del mapa, y cuantizar la
#'              rejilla contra QMAX mientras los condados van a otra `q`
#'              dibujaría las dos capas a escalas distintas — el mapa
#'              saldría, con su leyenda y sus colores, y la rejilla caería
#'              desplazada sobre unos condados que no son los suyos. Es el
#'              mismo modo de fallo que `geo_qxy` existe para evitar en las
#'              indicatrices de Tissot.
#'
#'              Ojo con la CAJA cuando además se simplifica: `geo_simplifica`
#'              mueve vértices y puede encoger el bbox de los polígonos unos
#'              metros. Si la caja se deduce de ellos, la rejilla —que no se
#'              simplifica— se sale del encuadre y el navegador le recorta el
#'              borde. Por eso el módulo 7 pasa `caja` explícita: la del dato
#'              SIN simplificar, que es la que `st_make_grid` usó.
#'
#'   `lineas_resaltadas`  índices 1-basados de las polilíneas que hay que
#'              destacar. Existe porque un mapa de rejilla sobre condados no
#'              enseña nada por sí solo: lo que convierte la cifra en
#'              evidencia es ver UN condado y LAS CELDAS QUE TOCA. Sin el
#'              resalte el lector ve dos capas superpuestas y sigue sin ver
#'              el doble conteo.
#'
#'   `resaltado`  índice 1-basado del rasgo del coropleto que se destaca (el
#'              condado del caso). 1-basado como `resaltado2` de
#'              `geo_puntos()`, y no 0-basado como la opción `resaltado` que
#'              el navegador ya admitía: los índices que vienen de R son
#'              1-basados en todo este archivo —`aristas`, `resaltado2`,
#'              `lineas_resaltadas`— y estrenar aquí el otro convenio sería
#'              sembrar un desplazamiento de uno que da un mapa plausible.
geo_poligonos <- function(x, valor = NULL, n_clases = 5, estilo = "quantile",
                          etiquetas = NULL, titulo = "", presupuesto = 8000L,
                          leyenda = "", verbose = TRUE, caja = NULL,
                          vistas = NULL, puntos_xy = NULL, puntos_valor = NULL,
                          puntos_modo = NULL, capas = NULL, q = QMAX,
                          superpuestos = list(), delta = FALSE,
                          lineas = NULL, lineas_resaltadas = NULL,
                          resaltado = NULL) {
  stopifnot(inherits(x, "sf"))
  if (is.na(sf::st_crs(x))) stop("el objeto no tiene CRS: proyectalo antes")
  if (sf::st_is_longlat(x)) warning("geometria en lon/lat: proyecta antes o el mapa saldra deformado")
  x <- geo_simplifica(x, presupuesto, verbose)
  if (is.null(caja)) caja <- geo_caja(x)
  caja <- as.numeric(caja)
  q <- as.integer(q)
  # La cuantización de ESTE mapa, escrita una sola vez. La usaban ya las
  # capas de puntos superpuestas y ahora también las polilíneas, y son la
  # misma aritmética que `geo_partes` aplica a la geometría: tenerla en tres
  # copias es tener tres sitios donde una se puede quedar atrás sin que nada
  # falle — las capas saldrían dibujadas, solo que desplazadas.
  .rx <- caja[3] - caja[1]; .ry <- caja[4] - caja[2]; .r <- max(.rx, .ry)
  .cx <- caja[1] + .rx / 2; .cy <- caja[2] + .ry / 2
  qx <- function(v) as.integer(round((v - (.cx - .r / 2)) / .r * q))
  qy <- function(v) as.integer(round((v - (.cy - .r / 2)) / .r * q))
  geom <- lapply(sf::st_geometry(x), geo_partes, caja = caja, q = q)
  if (delta) {
    # Round-trip comprobado AQUÍ y no en el navegador: son enteros, así
    # que la reconstrucción tiene que ser idéntica bit a bit. Si algún
    # día dejara de serlo, para el generador y no sale un mapa torcido.
    geom_d <- lapply(geom, function(f) lapply(f, geo_delta))
    recon <- lapply(geom_d, function(f) lapply(f, function(p) {
      n <- length(p); if (n <= 2L) return(p)
      as.integer(rbind(cumsum(p[seq(1, n, by = 2)]), cumsum(p[seq(2, n, by = 2)])))
    }))
    if (!identical(recon, geom))
      stop("la codificacion por diferencias no reconstruye la geometria original")
    geom <- geom_d
  }

  out <- list(
    modo = "poligonos", titulo = titulo, leyenda = leyenda,
    crs = sf::st_crs(x)$epsg %||% NA, caja = caja, q = as.integer(q),
    codificacion = if (delta) "delta" else "absoluta",
    n = nrow(x),
    geom = unname(lapply(geom, unname))
  )
  if (!is.null(capas)) {
    out$capas <- lapply(capas, function(cp) {
      v <- as.numeric(cp$valor)
      if (length(v) != nrow(x))
        stop(sprintf("la capa '%s' trae %d valores y la geometria tiene %d rasgos",
                     cp$id %||% "?", length(v), nrow(x)))
      cl <- geo_cortes(v, cp$n_clases %||% n_clases, cp$estilo %||% estilo)
      base <- list(id = cp$id, etiqueta = cp$etiqueta %||% cp$id,
                   leyenda = cp$leyenda %||% "",
                   valor = v, cortes = cl$cortes, clase = cl$clase,
                   estilo = cl$estilo, tam = cl$tam, n_sin_dato = cl$n_sin_dato)
      if (!is.null(cp$vistas)) base$vistas <- lapply(cp$vistas, function(vi) {
        c2 <- geo_cortes(v, vi$n %||% cp$n_clases %||% n_clases, vi$estilo)
        list(estilo = c2$estilo, n = c2$n, etiqueta = vi$etiqueta %||% c2$estilo,
             cortes = c2$cortes, clase = c2$clase, tam = c2$tam,
             n_sin_dato = c2$n_sin_dato)
      })
      base
    })
  }
  if (!is.null(valor)) {
    cl <- geo_cortes(valor, n_clases, estilo)
    out$valor  <- as.numeric(valor)
    out$cortes <- cl$cortes
    out$clase  <- cl$clase
    out$estilo <- cl$estilo
    out$tam    <- cl$tam
  }
  if (!is.null(vistas)) {
    if (is.null(valor)) stop("`vistas` necesita `valor`: son clasificaciones del mismo dato")
    out$vistas <- lapply(vistas, function(v) {
      cl <- geo_cortes(valor, v$n %||% n_clases, v$estilo)
      list(estilo = cl$estilo, n = cl$n, etiqueta = v$etiqueta %||% cl$estilo,
           cortes = cl$cortes, clase = cl$clase, tam = cl$tam)
    })
  }
  if (!is.null(etiquetas)) out$etiquetas <- as.character(etiquetas)
  # Capas de puntos superpuestas. Se admite la forma corta de un solo
  # conjunto (`puntos_xy` + `puntos_modo`) y la forma larga en lista
  # (`superpuestos`), que es la que usa el módulo 7: los símbolos
  # proporcionales y el dot density van sobre EL MISMO mapa de fondo, y
  # separarlos en dos objetos pagaría la geometría departamental dos
  # veces.
  if (!is.null(puntos_xy)) {
    superpuestos <- c(superpuestos, list(list(
      id = "puntos", modo = puntos_modo, xy = puntos_xy, valor = puntos_valor)))
  }
  if (length(superpuestos)) {
    out$superpuestos <- lapply(superpuestos, function(sp) {
      if (is.null(sp$modo))
        stop("una capa superpuesta sin `modo` ('simbolo' o 'densidad'): el navegador no lo adivina")
      if (!sp$modo %in% c("simbolo", "densidad"))
        stop("`modo` de la capa superpuesta tiene que ser 'simbolo' o 'densidad': ", sp$modo)
      p <- as.matrix(sp$xy)
      # La MISMA cuantización que la geometría de este mapa, no QMAX: si
      # difirieran, los puntos aterrizarían desplazados sobre sus polígonos.
      z <- list(id = sp$id %||% sp$modo, modo = sp$modo, n = nrow(p),
                etiqueta = sp$etiqueta %||% "",
                pts = as.integer(rbind(qx(p[, 1]), qy(p[, 2]))))
      if (!is.null(sp$valor)) z$valor <- as.numeric(sp$valor)
      z
    })
  }
  # --- Polilíneas sobre el coropleto (T2.7 del capítulo 1) ------------
  # Misma caja y misma `q` que todo lo demás: ver la documentación de
  # arriba. Cada polilínea sale como un vector plano [x0,y0,x1,y1,...],
  # igual que las calles de Soho en `geo_puntos()`, para que el navegador
  # tenga UN solo formato de línea que aprender.
  if (!is.null(lineas)) {
    out$lineas <- unname(lapply(lineas, function(m) {
      m <- as.matrix(m)
      if (ncol(m) < 2) stop("cada polilinea tiene que ser una matriz de 2 columnas")
      as.integer(rbind(qx(m[, 1]), qy(m[, 2])))
    }))
    out$n_lineas <- length(out$lineas)
  }
  # Los dos resaltes. Se validan CONTRA su capa y se para, en vez de
  # dejar pasar un índice fuera de rango: en el navegador un índice que no
  # existe no falla, simplemente no resalta nada, y un mapa que enseña el
  # doble conteo sin señalar dónde está es un mapa bonito que no demuestra
  # nada. Es el modo de fallo de siempre —salir plausible— aplicado a un
  # resalte.
  if (!is.null(lineas_resaltadas)) {
    if (is.null(lineas)) stop("`lineas_resaltadas` sin `lineas`: no hay nada que resaltar")
    ir <- as.integer(lineas_resaltadas)
    if (any(is.na(ir)) || any(ir < 1L) || any(ir > length(lineas)))
      stop(sprintf("`lineas_resaltadas` sale del rango 1..%d: %s",
                   length(lineas), paste(ir, collapse = ", ")))
    out$lineas_resaltadas <- ir
  }
  if (!is.null(resaltado)) {
    ir <- as.integer(resaltado)
    if (length(ir) != 1L || is.na(ir) || ir < 1L || ir > nrow(x))
      stop(sprintf("`resaltado` tiene que ser UN indice 1-basado en 1..%d y es %s",
                   nrow(x), paste(resaltado, collapse = ", ")))
    out$resaltado <- ir
  }
  out
}

#' Modo `puntos` — patrón puntual sobre su ventana
#'
#' Argumentos opcionales añadidos en T1.1 (el mapa de Snow los pedía), todos
#' RETROCOMPATIBLES: quien no los pasa obtiene exactamente el JSON de T0.3.
#'
#'   `lineas`   lista de matrices de 2 columnas — polilíneas de fondo (las
#'              calles de Soho). Se cuantizan contra la MISMA caja que los
#'              puntos, que es lo que garantiza que se superpongan bien.
#'   `puntos2`  segundo conjunto de puntos, con semántica distinta de los
#'              primeros (las 13 bombas frente a las 578 muertes). Va aparte
#'              y no dentro de `pts` con una marca porque son dos capas, no
#'              dos categorías: se dibujan con símbolo y tamaño distintos.
#'   `etiquetas2`  su rótulo, para la tabla de respaldo accesible.
#'   `resaltado2`  índice 1-basado del punto de la segunda capa que hay que
#'              destacar (la bomba de Broad Street).
#'
#' EL TIPO DE LA MARCA LO DECLARA R, no lo adivina el navegador (T1.2).
#' Las 578 muertes de Snow llevan como marca la bomba más próxima —trece
#' CATEGORÍAS—, y las 361 estaciones del IDEAM llevan su temperatura —un
#' NÚMERO—. Sobre el JSON las dos llegaban como un vector de números, así
#' que el navegador tenía que distinguirlas por su aspecto: trece enteros
#' pequeños *parecen* categorías y una escala de 12 a 29 °C *parece*
#' continua, hasta el día en que una marca categórica tenga cien niveles o
#' una numérica tome tres valores enteros. Entonces el mapa saldría bien
#' dibujado y mal coloreado, sin avisar — el modo de fallo de siempre.
#' Ahora un `factor` (o un vector de texto) sale como códigos 1..k más sus
#' `niveles`, y el campo `marcas_tipo` lo dice en voz alta.
#' Retrocompatible: `demo_geomapa.json` no usa marcas, así que T0.3 no se
#' mueve.
geo_puntos <- function(xy, ventana = NULL, marcas = NULL, titulo = "",
                       leyenda = "", caja = NULL, lineas = NULL,
                       puntos2 = NULL, etiquetas2 = NULL, resaltado2 = NULL) {
  xy <- as.matrix(xy)
  stopifnot(ncol(xy) == 2)
  if (is.null(caja)) {
    caja <- c(min(xy[, 1]), min(xy[, 2]), max(xy[, 1]), max(xy[, 2]))
    if (!is.null(ventana)) caja <- c(min(caja[1], ventana[1]), min(caja[2], ventana[2]),
                                     max(caja[3], ventana[3]), max(caja[4], ventana[4]))
    # Las capas de fondo tienen que caber también, o las calles saldrían
    # cortadas por el borde del lienzo.
    if (!is.null(lineas)) {
      todo <- do.call(rbind, lapply(lineas, as.matrix))
      caja <- c(min(caja[1], min(todo[, 1])), min(caja[2], min(todo[, 2])),
                max(caja[3], max(todo[, 1])), max(caja[4], max(todo[, 2])))
    }
    if (!is.null(puntos2)) {
      p2 <- as.matrix(puntos2)
      caja <- c(min(caja[1], min(p2[, 1])), min(caja[2], min(p2[, 2])),
                max(caja[3], max(p2[, 1])), max(caja[4], max(p2[, 2])))
    }
  }
  rx <- caja[3] - caja[1]; ry <- caja[4] - caja[2]; r <- max(rx, ry)
  cx <- caja[1] + rx/2; cy <- caja[2] + ry/2
  qx <- function(v) as.integer(round((v - (cx - r/2)) / r * QMAX))
  qy <- function(v) as.integer(round((v - (cy - r/2)) / r * QMAX))

  out <- list(modo = "puntos", titulo = titulo, leyenda = leyenda,
              caja = as.numeric(caja), q = QMAX, n = nrow(xy),
              pts = as.integer(rbind(qx(xy[, 1]), qy(xy[, 2]))))
  if (!is.null(ventana)) out$ventana <- as.integer(
    c(qx(ventana[1]), qy(ventana[2]), qx(ventana[3]), qy(ventana[4])))
  if (!is.null(marcas)) {
    if (is.factor(marcas) || is.character(marcas)) {
      f <- if (is.factor(marcas)) marcas else factor(marcas)
      out$marcas      <- as.integer(f)          # códigos 1..k
      out$niveles     <- levels(f)              # y qué significa cada código
      out$marcas_tipo <- "categoria"
    } else {
      out$marcas      <- as.numeric(marcas)
      out$marcas_tipo <- "numero"
    }
  }
  if (!is.null(lineas)) out$lineas <- unname(lapply(lineas, function(m) {
    m <- as.matrix(m); as.integer(rbind(qx(m[, 1]), qy(m[, 2])))
  }))
  if (!is.null(puntos2)) {
    p2 <- as.matrix(puntos2)
    out$puntos2 <- as.integer(rbind(qx(p2[, 1]), qy(p2[, 2])))
    out$n2 <- nrow(p2)
  }
  if (!is.null(etiquetas2)) out$etiquetas2 <- as.character(etiquetas2)
  if (!is.null(resaltado2)) out$resaltado2 <- as.integer(resaltado2)
  out
}

#' Modo `grafo` — grafo de vecindad sobre los centroides
geo_grafo <- function(x, nb, titulo = "", leyenda = "", presupuesto = 6000L,
                      verbose = TRUE) {
  stopifnot(inherits(x, "sf"))
  base <- geo_poligonos(x, titulo = titulo, leyenda = leyenda,
                        presupuesto = presupuesto, verbose = verbose)
  cen  <- sf::st_coordinates(sf::st_point_on_surface(sf::st_geometry(x)))
  caja <- base$caja
  rx <- caja[3] - caja[1]; ry <- caja[4] - caja[2]; r <- max(rx, ry)
  cx <- caja[1] + rx/2; cy <- caja[2] + ry/2
  qx <- function(v) as.integer(round((v - (cx - r/2)) / r * QMAX))
  qy <- function(v) as.integer(round((v - (cy - r/2)) / r * QMAX))

  # aristas i<j para no dibujar cada una dos veces
  ar <- do.call(rbind, lapply(seq_along(nb), function(i) {
    j <- nb[[i]]; j <- j[j > i]
    if (length(j) == 0) NULL else cbind(i, j)
  }))
  base$modo    <- "grafo"
  base$nodos   <- as.integer(rbind(qx(cen[, 1]), qy(cen[, 2])))
  base$aristas <- if (is.null(ar)) integer(0) else as.integer(t(ar))  # pares 1-indexados
  base$grados  <- as.integer(vapply(nb, function(v) if (identical(v, 0L)) 0L else length(v), integer(1)))
  base
}

#' Varias vecindades sobre UN MISMO mapa, con la geometría compartida
#'
#' `geo_grafo` repite los polígonos en cada llamada. Con las tres
#' variantes de Columbus eso ya son 47 KB de los que 31 son copias; en el
#' capítulo 6, con ~10 definiciones de W sobre el mismo territorio,
#' serían cientos de KB de pura duplicación y el capítulo no cabría en el
#' presupuesto. Aquí la geometría va una vez y cada variante aporta solo
#' sus aristas y sus grados.
#'
#' `nbs` es una lista con nombre: list(reina = nb1, torre = nb2, ...)
geo_grafo_multi <- function(x, nbs, titulo = "", leyenda = "",
                            presupuesto = 6000L, verbose = TRUE) {
  stopifnot(inherits(x, "sf"), is.list(nbs), !is.null(names(nbs)))
  base <- geo_grafo(x, nbs[[1]], titulo = titulo, leyenda = leyenda,
                    presupuesto = presupuesto, verbose = verbose)
  caja <- base$caja
  rx <- caja[3] - caja[1]; ry <- caja[4] - caja[2]; r <- max(rx, ry)

  variantes <- lapply(nbs, function(nb) {
    ar <- do.call(rbind, lapply(seq_along(nb), function(i) {
      j <- nb[[i]]; j <- j[j > i]
      if (length(j) == 0) NULL else cbind(i, j)
    }))
    grados <- as.integer(vapply(nb, function(v) if (identical(v, 0L)) 0L else length(v), integer(1)))
    list(aristas = if (is.null(ar)) integer(0) else as.integer(t(ar)),
         grados  = grados,
         n_aristas = if (is.null(ar)) 0L else nrow(ar),
         grado_medio = round(mean(grados), 4),
         islas = sum(grados == 0L))
  })

  base$modo <- "grafo"
  base$aristas <- NULL; base$grados <- NULL   # viven ahora en las variantes
  base$variantes <- variantes
  base
}

#' Modo `rejilla` — superficie continua (KDE, kriging, varianza)
#'
#' `z` se guarda CUANTIZADO a enteros 0..ZQ, no como flotantes. Una
#' rejilla de 128x64 en flotantes de 6 decimales pesa 78 KB; cuantizada,
#' 20 KB. Y no se pierde nada: el destino es una rampa de color, que a lo
#' sumo distingue un par de cientos de niveles. El rango real y los
#' cortes viajan aparte, así que el navegador puede recuperar el valor
#' original para la leyenda y para el texto alternativo.
ZQ <- 1000L

#' @param escala  rango COMÚN para una familia de superficies, `c(lo, hi)`.
#'   Por defecto `NULL`: cada superficie se normaliza contra su propio
#'   mínimo y máximo, que es lo que quiere un mapa suelto y lo que
#'   publican los diez rásteres del capítulo 1.
#'
#'   PARA UNA FAMILIA NO SIRVE, y el capítulo 5 es la primera que hay.
#'   Las siete superficies del deslizador de sigma son el MISMO patrón
#'   suavizado con anchos distintos, y lo que el módulo enseña es que al
#'   abrir el núcleo la superficie se APLANA: la intensidad máxima cae de
#'   63,8 por km2 con sigma = 100 m a 9,4 con sigma = 1600 m. Normalizada
#'   cada una contra su propio máximo, las siete salen igual de picudas y
#'   el mapa afirma lo contrario que el texto —con la tinta más
#'   convincente de las dos—. Con `escala` las siete comparten regla y la
#'   caída se ve.
geo_rejilla <- function(z, caja, titulo = "", leyenda = "", n_clases = 7,
                        estilo = "equal", escala = NULL) {
  z <- as.matrix(z)
  fin <- z[is.finite(z)]
  if (is.null(escala)) {
    lo <- min(fin); hi <- max(fin)
  } else {
    if (length(escala) != 2L || !all(is.finite(escala)) || escala[1] >= escala[2])
      stop("geo_rejilla: `escala` tiene que ser c(lo, hi) finito y creciente")
    lo <- escala[1]; hi <- escala[2]
    # Una superficie que se sale de la escala común se publicaría
    # recortada SIN avisar: la celda saturada se ve igual que la que
    # justo llega. Se para aquí, que es donde se puede arreglar.
    if (min(fin) < lo - 1e-12 || max(fin) > hi + 1e-12)
      stop(sprintf("geo_rejilla: la superficie [%.6g, %.6g] se sale de la escala común [%.6g, %.6g]",
                   min(fin), max(fin), lo, hi))
  }
  rango <- hi - lo
  ci <- classInt::classIntervals(as.numeric(fin), n = n_clases, style = estilo)

  # por filas, de arriba a abajo, como lo espera el navegador
  plano <- as.numeric(t(z))
  zq <- ifelse(is.finite(plano),
               as.integer(round((plano - lo) / rango * ZQ)),
               -1L)                      # -1 = celda sin dato (fuera de ventana)

  list(modo = "rejilla", titulo = titulo, leyenda = leyenda,
       caja = as.numeric(caja), nx = ncol(z), ny = nrow(z),
       zq = as.integer(zq), zqmax = ZQ,
       rango = c(lo, hi),
       cortes = as.numeric(ci$brks))
}

# ---------------------------------------------------------------------
# geo_qxy — la MISMA cuantización que geo_partes, para puntos sueltos
#
# Existe porque las indicatrices de Tissot tienen que caer exactamente
# donde cae la geometría: si el centro de la elipse se cuantizara con
# otra convención, el mapa saldría bien y la elipse desplazada, que es
# el tipo de defecto que nadie ve porque el resultado es plausible.
# ---------------------------------------------------------------------
geo_qxy <- function(px, py, caja) {
  rx <- caja[3] - caja[1]; ry <- caja[4] - caja[2]
  r  <- max(rx, ry)
  cx <- caja[1] + rx / 2; cy <- caja[2] + ry / 2
  list(x = as.integer(round((px - (cx - r / 2)) / r * QMAX)),
       y = as.integer(round((py - (cy - r / 2)) / r * QMAX)))
}

# ---------------------------------------------------------------------
# geo_tissot — los parámetros de la indicatriz, MEDIDOS sobre la propia
# proyección (T2.1a)
#
# El capítulo 2 no puede AFIRMAR que Mercator conserva los ángulos: tiene
# que medirlo, igual que el capítulo 1 mide la subestimación del error
# estándar en vez de anunciarla. Esto es lo que lo mide.
#
# CÓMO. Por diferencias finitas centradas: se transforma cada punto y sus
# cuatro vecinos a ±d grados, se arma la jacobiana en la base LOCAL
# este-norte del elipsoide —que es la base en la que un círculo unitario
# sobre el terreno es de verdad un círculo— y se descompone en valores
# singulares.
#
#     J = [ dx/dE  dx/dN ]      E = este local, en metros de terreno
#         [ dy/dE  dy/dN ]      N = norte local, en metros de terreno
#
# Los DOS VALORES SINGULARES DE J SON LOS SEMIEJES DE LA INDICATRIZ. Eso
# es todo: no hace falta la trigonometría de Snyder (1987, pp. 20-24) con
# su sin(theta'), que da exactamente lo mismo y tiene tres sitios más
# donde equivocarse de signo. Y el primer vector singular izquierdo da la
# orientación del semieje mayor YA EN EL PLANO PROYECTADO, que es lo que
# el navegador necesita para dibujar la elipse.
#
#   a, b    semiejes, a >= b. Escala máxima y mínima en el punto.
#   s       escala de área = a*b = |det J|.  EQUIVALENTE  <=>  s = 1.
#   omega   deformación angular máxima = 2*asin((a-b)/(a+b)).
#           CONFORME  <=>  omega = 0.
#   orient  ángulo del semieje mayor en el plano proyectado, en radianes.
#   h, k    escala a lo largo del meridiano y del paralelo. NO son los
#           semiejes salvo que la proyección sea ortogonal en ese punto:
#           publicarlos como si lo fueran es un error clásico.
#
# La base local usa los dos radios de curvatura del elipsoide, sacados
# del CRS de origen y no cableados:
#     M = a(1-e^2) / (1 - e^2 sin^2 phi)^{3/2}   (meridiano)
#     N = a        / (1 - e^2 sin^2 phi)^{1/2}   (primer vertical)
# ---------------------------------------------------------------------
geo_tissot <- function(crs_destino, lon, lat, crs_origen = 4326, d = 0.02) {
  stopifnot(length(lon) == length(lat), d > 0)
  cro <- sf::st_crs(crs_origen)
  ea <- as.numeric(cro$SemiMajor)
  eb <- as.numeric(cro$SemiMinor)
  if (!is.finite(ea) || !is.finite(eb))
    stop("geo_tissot: el CRS de origen no declara su elipsoide")
  e2 <- (ea^2 - eb^2) / ea^2

  n <- length(lon)
  # Los 4n vecinos en UNA sola transformación: PROJ por punto suelto
  # cuesta más que todo lo demás junto, y aquí se llama seis veces por
  # mapa.
  ln <- c(lon - d, lon + d, lon,     lon)
  lt <- c(lat,     lat,     lat - d, lat + d)
  pts <- sf::st_sfc(lapply(seq_along(ln), function(i) sf::st_point(c(ln[i], lt[i]))),
                    crs = cro)
  xy <- try(sf::st_coordinates(sf::st_transform(pts, crs_destino)), silent = TRUE)
  if (inherits(xy, "try-error")) return(NULL)

  # SI EL DESTINO ES GEOGRÁFICO, HAY QUE DECIR EN QUÉ SE LE ESTÁ
  # CONVIRTIENDO — y esto lo cazó el banco de pruebas, no yo.
  #
  # Con crs_destino = 4326 la «proyección» es la identidad y las
  # coordenadas de salida son GRADOS. La jacobiana sale entonces en
  # grados por metro, del orden de 1e-7: la escala de área daba 0,000 y
  # las elipses se dibujaban con un radio de cero píxeles. Los ángulos
  # sí estaban bien —omega no depende del factor global—, así que el
  # informe parecía casi correcto, que es lo peor.
  #
  # Lo honesto no es negarse a medir: dibujar lon/lat en un plano ES una
  # proyección, la plate carrée, y decirlo es justo la lección del módulo
  # 4. Se convierten los grados a metros con R·pi/180 y la vista queda
  # medida como lo que de verdad es. La conversión se DECLARA arriba, en
  # `interpretado_como`, en vez de aplicarse en silencio.
  geografico <- isTRUE(sf::st_is_longlat(sf::st_crs(crs_destino)))
  # `factor` son las unidades de la caja por metro de plano. Vale 1 en
  # una proyección métrica y R·pi/180 cuando el destino es geográfico.
  # Se DEVUELVE, porque quien dibuja necesita deshacerlo: la caja del
  # mapa sigue estando en grados, y cuantizar unas coordenadas en metros
  # contra una caja en grados pone las elipses a millones de unidades de
  # su sitio. Eso es lo que pasó, y el mapa seguía saliendo «bien»
  # porque las elipses caían tan lejos que no se veía ninguna.
  factor <- 1
  if (geografico) {
    R <- (2 * ea + eb) / 3          # radio medio del elipsoide
    factor <- R * pi / 180
    xy_pos <- xy                    # para el CENTRO: unidades de la caja
    xy <- xy * factor               # para las DERIVADAS: metros
  } else {
    xy_pos <- xy
  }

  i_ol <- seq_len(n); i_or <- n + i_ol; i_as <- 2 * n + i_ol; i_ar <- 3 * n + i_ol
  drad <- d * pi / 180

  # d/dlambda y d/dphi en RADIANES, por diferencia centrada
  dxdl <- (xy[i_or, 1] - xy[i_ol, 1]) / (2 * drad)
  dydl <- (xy[i_or, 2] - xy[i_ol, 2]) / (2 * drad)
  dxdp <- (xy[i_ar, 1] - xy[i_as, 1]) / (2 * drad)
  dydp <- (xy[i_ar, 2] - xy[i_as, 2]) / (2 * drad)

  phi <- lat * pi / 180
  w <- sqrt(1 - e2 * sin(phi)^2)
  M <- ea * (1 - e2) / w^3
  N <- ea / w
  Ncos <- N * cos(phi)

  res <- data.frame(lon = lon, lat = lat,
                    a = NA_real_, b = NA_real_, s = NA_real_, omega = NA_real_,
                    orient = NA_real_, h = NA_real_, k = NA_real_,
                    x = NA_real_, y = NA_real_)
  for (i in seq_len(n)) {
    # dx/dE, dy/dE, dx/dN, dy/dN — la base local, en metros de terreno
    J <- matrix(c(dxdl[i] / Ncos[i], dxdp[i] / M[i],
                  dydl[i] / Ncos[i], dydp[i] / M[i]), nrow = 2, byrow = TRUE)
    if (!all(is.finite(J))) next
    sv <- svd(J)
    a <- sv$d[1]; b <- sv$d[2]
    if (!is.finite(a) || !is.finite(b) || a <= 0) next
    res$a[i] <- a
    res$b[i] <- b
    res$s[i] <- abs(det(J))                       # = a*b salvo redondeo
    res$omega[i] <- 2 * asin(min(1, (a - b) / (a + b)))
    res$orient[i] <- atan2(sv$u[2, 1], sv$u[1, 1])
    res$k[i] <- sqrt(J[1, 1]^2 + J[2, 1]^2)       # a lo largo del paralelo
    res$h[i] <- sqrt(J[1, 2]^2 + J[2, 2]^2)       # a lo largo del meridiano
  }
  # La posición del centro: el punto mismo, proyectado. Se saca del
  # promedio de los cuatro vecinos y no de una quinta transformación,
  # para que el centro no pueda quedar en un sitio y sus derivadas en
  # otro si PROJ decide algo raro en un borde.
  res$x <- (xy_pos[i_ol, 1] + xy_pos[i_or, 1] + xy_pos[i_as, 1] + xy_pos[i_ar, 1]) / 4
  res$y <- (xy_pos[i_ol, 2] + xy_pos[i_or, 2] + xy_pos[i_as, 2] + xy_pos[i_ar, 2]) / 4
  out <- res[is.finite(res$a) & is.finite(res$x) & is.finite(res$y), , drop = FALSE]
  attr(out, "geografico") <- geografico
  attr(out, "factor") <- factor
  out
}

# ---------------------------------------------------------------------
# geo_tissot_autoprueba — las anclas que PARAN si la medida está mal
#
# Un medidor de distorsión que devuelve números plausibles y equivocados
# es exactamente el modo de fallo dominante de este proyecto. Estas tres
# anclas son propiedades MATEMÁTICAS de tres proyecciones conocidas, no
# umbrales elegidos a ojo:
#
#   1. Mercator es conforme  ->  omega = 0 en todo punto.
#   2. Mollweide es equivalente sobre la esfera  ->  s = 1 en todo punto.
#   3. La equirrectangular sobre la esfera no deforma el meridiano -> h = 1,
#      y su escala del paralelo es 1/cos(phi), que se comprueba punto a punto.
#
# Se llama explícitamente desde el generador. No se ejecuta al cargar
# geo.R: un source() no puede costar segundos.
# ---------------------------------------------------------------------
geo_tissot_autoprueba <- function(verbose = TRUE) {
  lon <- rep(seq(-150, 150, by = 30), times = 5)
  lat <- rep(seq(-60, 60, by = 30), each = 11)
  esf <- "+proj=longlat +R=6371007 +no_defs"

  t1 <- geo_tissot("+proj=merc +ellps=WGS84 +units=m +no_defs", lon, lat)
  om <- max(abs(t1$omega))
  if (om > 1e-6)
    stop(sprintf("geo_tissot: Mercator deberia dar omega = 0 y da hasta %.3e rad", om))

  t2 <- geo_tissot("+proj=moll +R=6371007 +units=m +no_defs", lon, lat, crs_origen = esf)
  ds <- max(abs(t2$s - 1))
  if (ds > 1e-4)
    stop(sprintf("geo_tissot: Mollweide deberia dar s = 1 y se desvia hasta %.3e", ds))

  t3 <- geo_tissot("+proj=eqc +R=6371007 +units=m +no_defs", lon, lat, crs_origen = esf)
  dh <- max(abs(t3$h - 1))
  dk <- max(abs(t3$k - 1 / cos(t3$lat * pi / 180)))
  if (dh > 1e-4 || dk > 1e-4)
    stop(sprintf("geo_tissot: equirrectangular deberia dar h = 1 y k = sec(phi); %.3e / %.3e",
                 dh, dk))

  if (verbose)
    message(sprintf(paste("  geo_tissot OK: Mercator omega_max = %.2e rad ·",
                          "Mollweide |s-1| = %.2e · eqc |h-1| = %.2e"), om, ds, dh))
  invisible(list(merc_omega = om, moll_s = ds, eqc_h = dh))
}

#' Modo `proyeccion` — el mismo territorio bajo varios CRS, con distorsión
#'
#' La distorsión se MIDE por DOS caminos independientes, y eso es a
#' propósito: el área de cada unidad proyectada contra su área geodésica
#' (medida sobre los polígonos reales) y la indicatriz de Tissot (medida
#' punto a punto sobre la propia proyección). Que las dos coincidan en
#' magnitud es la comprobación cruzada; que una sola diga lo que se
#' quiere oír no lo es.
#'
#' @param tissot lista con `lon` y `lat` —la rejilla de indicatrices— o
#'   NULL para no medirlas. `radio_km` fija el radio del círculo de
#'   TERRENO que se dibuja: las elipses del mapa son ese círculo
#'   proyectado, no una decoración de tamaño arbitrario.
geo_proyeccion <- function(x_ll, crs_lista, titulo = "", presupuesto = 4000L,
                           verbose = TRUE, tissot = NULL, radio_km = 350) {
  stopifnot(inherits(x_ll, "sf"), sf::st_is_longlat(x_ll))
  x_ll <- geo_simplifica(x_ll, presupuesto, verbose)

  # LA REFERENCIA ES EL ELIPSOIDE, NO LA ESFERA — corregido en T2.1a.
  #
  # Hasta aquí esto llamaba a st_area() con s2 encendido, y s2 mide sobre
  # una ESFERA. Sobre los 1 122 municipios de Colombia esa esfera infla el
  # área un 0,44 % de mediana, y ese 0,44 % se colaba entero dentro de la
  # razón: EPSG:3116 tiene k = 1 y por tanto su razón de área NO PUEDE
  # bajar de 1, y con la referencia esférica salía 0,9962. Un número
  # plausible, con buena cara y falso — el modo de fallo de siempre.
  # El elipsoide (GRS80/WGS84) es el modelo que usan todos los CRS que
  # aquí se comparan, así que es la referencia correcta; la calcula
  # lwgeom, y de paso no revienta con la topología que deja simplificar.
  s2_antes <- sf::sf_use_s2(FALSE)
  area_geo <- suppressMessages(as.numeric(sf::st_area(x_ll)))
  sf::sf_use_s2(s2_antes)

  vistas <- lapply(crs_lista, function(cc) {
    xp <- try(sf::st_transform(x_ll, cc$crs), silent = TRUE)
    if (inherits(xp, "try-error")) return(NULL)
    ap <- as.numeric(sf::st_area(xp))
    razon <- ap / area_geo                        # 1 = área respetada
    caja <- geo_caja(xp)
    v <- list(nombre = cc$nombre, crs = cc$crs, familia = cc$familia %||% "",
              caja = caja, q = QMAX,
              geom = unname(lapply(lapply(sf::st_geometry(xp), geo_partes, caja = caja), unname)),
              # resumen de la distorsión de área, medido
              razon_med = stats::median(razon),
              razon_min = min(razon), razon_max = max(razon),
              # cuánto se estira el peor caso respecto del mejor
              estiramiento = max(razon) / min(razon))

    if (!is.null(tissot)) {
      tt <- geo_tissot(cc$crs, tissot$lon, tissot$lat, crs_origen = sf::st_crs(x_ll))
      if (!is.null(tt) && nrow(tt) > 0) {
        q <- geo_qxy(tt$x, tt$y, caja)
        r <- max(caja[3] - caja[1], caja[4] - caja[2])
        # El radio va a las UNIDADES DE LA CAJA antes de cuantizarse: en
        # una vista métrica el factor es 1 y esto no cambia nada; en una
        # geográfica pasa de metros a grados, que es lo que la caja mide.
        fac <- attr(tt, "factor")
        v$indicatrices <- list(
          # el radio del círculo de terreno, ya en unidades cuantizadas:
          # el navegador multiplica por a y por b y no calcula nada más
          rq = (radio_km * 1000 / fac) / r * QMAX,
          radio_km = radio_km,
          x = q$x, y = q$y,
          # CUATRO decimales y no diez: estos cinco vectores son para
          # DIBUJAR la elipse, y el navegador no puede resolver más de
          # un píxel. Los resúmenes de los que el texto argumenta
          # (omega_med, s_med...) se calculan abajo con la precisión
          # entera, así que la regla de los 5 decimales no se toca.
          a = round(tt$a, 4), b = round(tt$b, 4),
          s = round(tt$s, 4), omega = round(tt$omega, 4),
          orient = round(tt$orient, 4))
        v$omega_med <- stats::median(tt$omega)
        v$omega_max <- max(tt$omega)
        v$s_med <- stats::median(tt$s)
        v$s_min <- min(tt$s); v$s_max <- max(tt$s)
        # Las dos etiquetas, RECALCULADAS y no heredadas del nombre de la
        # proyección: una lista que dijera de sí misma «conforme» sería
        # una bandera, y las banderas no se auditan (regla de T1.1).
        v$es_conforme <- max(tt$omega) < 1e-6
        v$es_equivalente <- max(abs(tt$s - 1)) < 1e-3
        # Si el «destino» era geográfico, lo que se ha medido es la
        # plate carrée. Se dice, en el propio JSON, para que el capítulo
        # no pueda presentar 4326 como si no fuera una proyección.
        if (isTRUE(attr(tt, "geografico")))
          v$interpretado_como <- paste(
            "CRS geográfico: se mide como plate carrée, con los grados",
            "llevados a metros por el radio medio del elipsoide")
      }
    }
    v
  })
  vistas <- Filter(Negate(is.null), vistas)
  list(modo = "proyeccion", titulo = titulo, n = nrow(x_ll), vistas = vistas)
}

`%||%` <- function(a, b) if (is.null(a) || (length(a) == 1 && is.na(a))) b else a

# =====================================================================
# T2.4 · Cartogramas (capítulo 3, módulo 7)
#
# Dos de los tres se implementan AQUÍ y no se delegan en `cartogram`, y
# no es por ahorrarse la dependencia —está instalada—: es que los dos
# tienen una propiedad EXACTA que sirve de prueba, y una implementación
# propia es la única forma de que la prueba compare dos caminos.
#
#   Olson (1976), no contiguo: cada polígono se escala alrededor de su
#   centroide por sqrt( d_i / max(d) ), con d = valor/área. El más denso
#   conserva su tamaño y el resto encoge. El área resultante es
#   a_i · d_i/max(d) = v_i/max(d), o sea EXACTAMENTE proporcional al
#   valor. corr(área, valor) tiene que dar 1 a precisión de máquina; si
#   no, la implementación está mal, y eso es una prueba que puede fallar.
#
#   Dorling (1996): círculos de área proporcional al valor, centrados en
#   los centroides y separados por repulsión. Misma propiedad exacta, y
#   además una propiedad que la repulsión NO puede romper: mueve los
#   centros, nunca los radios.
#
# El contiguo (Dougenik et al. 1985) sí sale de `cartogram_cont`, porque
# es iterativo y reimplementarlo mal sería peor que no tenerlo. Y trae
# de regalo el material del módulo: **no alcanza la proporcionalidad
# exacta** —tiene que conservar la topología, y eso es una restricción
# que compite con el área—, así que su corr(área, valor) se mide y se
# publica en vez de esconderse.
# =====================================================================

#' Olson no contiguo, implementación propia
geo_carto_ncont <- function(x, valor) {
  v <- as.numeric(valor)
  if (any(!is.finite(v)) || any(v < 0)) stop("el valor del cartograma tiene que ser finito y no negativo")
  a <- as.numeric(sf::st_area(x))
  d <- v / a
  k <- sqrt(d / max(d))                       # factor de escala lineal
  g <- sf::st_geometry(x)
  ctr <- sf::st_centroid(g, of_largest_polygon = TRUE)
  g2 <- lapply(seq_along(g), function(i) {
    c0 <- sf::st_coordinates(ctr[i])[1, 1:2]
    (g[[i]] - c0) * k[i] + c0
  })
  sf::st_geometry(x) <- sf::st_sfc(g2, crs = sf::st_crs(x))
  x$.carto_k <- k
  x
}

#' Dorling, implementación propia
#'
#' `k` es el mismo mando que el del paquete: escala global de los radios.
#' La repulsión es la clásica —empujar cada par solapado por la mitad de
#' su penetración— y se para cuando ya no hay solape o se agotan las
#' iteraciones. Que no converja del todo NO rompe la propiedad exacta.
geo_carto_dorling <- function(x, valor, k = 5, itermax = 1000, tol = 1e-9) {
  v <- as.numeric(valor)
  if (any(!is.finite(v)) || any(v < 0)) stop("el valor del cartograma tiene que ser finito y no negativo")
  a <- as.numeric(sf::st_area(x))
  n <- nrow(x)
  ctr <- sf::st_coordinates(sf::st_centroid(sf::st_geometry(x), of_largest_polygon = TRUE))[, 1:2, drop = FALSE]
  # Radio: área del círculo proporcional al valor, con la escala fijada
  # para que el área TOTAL de los círculos sea k/100 del área total real.
  r <- sqrt(v / sum(v) * sum(a) * (k / 100) / pi)
  p <- ctr
  for (it in seq_len(itermax)) {
    movido <- 0
    for (i in seq_len(n - 1)) {
      j <- (i + 1):n
      dx <- p[j, 1] - p[i, 1]; dy <- p[j, 2] - p[i, 2]
      dd <- sqrt(dx^2 + dy^2)
      solape <- r[i] + r[j] - dd
      hay <- which(solape > tol & dd > tol)
      if (!length(hay)) next
      for (m in hay) {
        jj <- j[m]
        ux <- dx[m] / dd[m]; uy <- dy[m] / dd[m]
        e <- solape[m] / 2
        p[i, ] <- p[i, ] - c(ux, uy) * e
        p[jj, ] <- p[jj, ] + c(ux, uy) * e
        movido <- movido + e
      }
    }
    if (movido < tol) break
  }
  circ <- lapply(seq_len(n), function(i) {
    th <- seq(0, 2 * pi, length.out = 33)[-33]
    sf::st_polygon(list(cbind(p[i, 1] + r[i] * cos(th), p[i, 2] + r[i] * sin(th))[c(1:32, 1), ]))
  })
  y <- x
  sf::st_geometry(y) <- sf::st_sfc(circ, crs = sf::st_crs(x))
  y$.carto_r <- r
  y$.carto_iter <- it
  y
}

# =====================================================================
# T2.4 · Simulación de daltonismo (capítulo 3, módulo 5)
#
# Machado, Oliveira & Fernandes (2009): linealizar sRGB, aplicar una 3x3
# publicada y volver a comprimir. Es el mismo modelo que implementa
# `colorspace::deutan()`, y por eso se escribe A MANO: el generador
# comprueba que los dos caminos dan el MISMO hexadecimal, y esa
# comparación puede fallar.
#
# Ojo con la lista de matrices del paquete: sus nombres van de "0" a
# "10" (severidad x10), así que la severidad 1,0 es el elemento 11
# POSICIONAL. `deutanomaly_cvd[["11"]]` devuelve NULL, no la matriz.
# =====================================================================

geo_cvd_lineal <- function(u) ifelse(u <= 0.04045, u / 12.92, ((u + 0.055) / 1.055)^2.4)
geo_cvd_gamma  <- function(u) ifelse(u <= 0.0031308, u * 12.92, 1.055 * u^(1/2.4) - 0.055)

geo_cvd_matriz <- function(tipo) {
  m <- switch(tipo,
    deuteranopia = colorspace::deutanomaly_cvd,
    protanopia   = colorspace::protanomaly_cvd,
    tritanopia   = colorspace::tritanomaly_cvd,
    stop("tipo de daltonismo desconocido: ", tipo))
  m[[11]]                                     # severidad 1,0
}

#' Simula un vector de colores hexadecimales bajo un tipo de daltonismo
geo_cvd <- function(hex, tipo) {
  M <- geo_cvd_matriz(tipo)
  rgb0 <- t(grDevices::col2rgb(hex)) / 255
  out  <- geo_cvd_lineal(rgb0) %*% t(M)
  out  <- geo_cvd_gamma(pmin(pmax(out, 0), 1))
  toupper(grDevices::rgb(pmin(pmax(out[, 1], 0), 1),
                         pmin(pmax(out[, 2], 0), 1),
                         pmin(pmax(out[, 3], 0), 1)))
}

#' Autoprueba: los dos caminos tienen que coincidir en TODOS los colores
geo_cvd_autoprueba <- function(paleta, verbose = TRUE) {
  res <- lapply(c("deuteranopia", "protanopia", "tritanopia"), function(tp) {
    f <- switch(tp, deuteranopia = colorspace::deutan,
                protanopia = colorspace::protan, tritanopia = colorspace::tritan)
    a <- geo_cvd(paleta, tp); b <- toupper(f(paleta, severity = 1))
    if (!identical(a, b)) {
      i <- which(a != b)[1]
      stop(sprintf("geo_cvd(%s) discrepa de colorspace en %s: %s vs %s",
                   tp, paleta[i], a[i], b[i]))
    }
    length(a)
  })
  if (verbose) message(sprintf("  geo_cvd: %d colores x 3 tipos identicos a colorspace",
                               length(paleta)))
  invisible(sum(unlist(res)))
}

#' Distancia perceptual mínima entre clases contiguas de una paleta, en CIELAB.
#' Es la medida del módulo 5: una paleta se rompe cuando dos clases vecinas
#' dejan de distinguirse, no cuando "se ve rara".
geo_paleta_dmin <- function(hex) {
  lab <- methods::as(colorspace::hex2RGB(hex), "LAB")@coords
  if (nrow(lab) < 2) return(NA_real_)
  min(sqrt(rowSums((lab[-1, , drop = FALSE] - lab[-nrow(lab), , drop = FALSE])^2)))
}

# ---------------------------------------------------------------------
# geo_escribe — serializa y avisa del peso
# ---------------------------------------------------------------------
geo_escribe <- function(obj, destino, presupuesto_kb = 120) {
  # `na = "null"` NO es opcional, y `null = "null"` no lo cubre: gobierna
  # los NULL, no los NA. Sin él **jsonlite escribe el NA como la CADENA
  # "NA"**, sin fallar y sin avisar, y al navegador le llega texto donde
  # espera un número. En JS eso no revienta: `"NA" >= 1` es `false` y
  # cualquier aritmética da NaN, así que el municipio saldría sin color
  # y con la consola limpia. Es el modo de fallo dominante de este
  # proyecto —la operación que devuelve algo plausible en vez de
  # fallar— y por eso debajo hay una guarda que PARA.
  #
  # Los capítulos 1 y 2 nunca lo pisaron porque filtraban los NA antes
  # de construir el mapa; el 3 conserva los 1 122 municipios con NA
  # donde no hay dato, a propósito, para que el mapa enseñe dónde falta.
  txt <- jsonlite::toJSON(obj, auto_unbox = TRUE, digits = 8,
                          null = "null", na = "null")
  if (grepl('"NA"', txt, fixed = TRUE))
    stop(sprintf("%s: hay NA escritos como la cadena \"NA\". Revisa el `na=` de toJSON",
                 basename(destino)))
  writeLines(txt, destino, useBytes = TRUE)
  kb <- file.size(destino) / 1024
  message(sprintf("  %s: %.1f KB", basename(destino), kb))
  if (kb > presupuesto_kb)
    warning(sprintf("%s pesa %.1f KB y el presupuesto es %d KB: sube la simplificacion",
                    basename(destino), kb, presupuesto_kb))
  invisible(kb)
}
