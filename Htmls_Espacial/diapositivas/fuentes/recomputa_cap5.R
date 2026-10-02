# =====================================================================
# recomputa_cap5.R — recómputo en R de las cifras de las presentaciones del
# capítulo 5 (sesiones 1 y 2). Escribe `recomputo_cap5.json`, que lee
# `verifica_cifras_cap5.py`.
#
# POR QUÉ EXISTE
#   `cap5_datos.json` trae lo que el capítulo publica. Esto vuelve a calcular,
#   con el mismo código y las mismas semillas, lo que las diapositivas dicen y el
#   JSON no trae (cuentas derivadas, el rango de la rejilla movida, dónde caen
#   los máximos de dos mapas, los tiempos…), y de paso re-ejecuta lo que sí trae,
#   para que cada cifra proyectada tenga una segunda fuente que no sea el propio
#   precálculo.
#
# Se ejecuta desde la raíz del repo, con el envoltorio del proyecto:
#   precalculo/rscript.sh Htmls_Espacial/diapositivas/fuentes/recomputa_cap5.R [s1|s2|todo]
# =====================================================================
suppressPackageStartupMessages({ library(sf); library(spatstat); library(jsonlite) })
options(scipen = 999, digits = 7, warn = 1)

SALIDA <- "Htmls_Espacial/diapositivas/fuentes/recomputo_cap5.json"
args <- commandArgs(trailingOnly = TRUE)
que <- if (length(args)) args[1] else "todo"

R_ <- if (file.exists(SALIDA)) fromJSON(SALIDA, simplifyVector = FALSE) else list()
guarda <- function(nombre, valor) { R_[[nombre]] <<- valor }
integra <- function(im) { v <- as.numeric(im$v); v <- v[is.finite(v)]; sum(v) * im$xstep * im$ystep }
ayuda_txt <- function(tema) {
  h <- utils:::.getHelpFile(help(tema, package = "spatstat.data"))
  paste(capture.output(tools::Rd2txt(h, options = list(underline_titles = FALSE))), collapse = "\n")
}

# ---------------------------------------------------------------------
# Datos de partida: las mismas líneas de preparación de los bloques del capítulo
# ---------------------------------------------------------------------
cole  <- st_read("datos/procesado/bogota_colegios.gpkg", quiet = TRUE)
loc   <- st_read("datos/procesado/bogota_localidades.gpkg", quiet = TRUE)
v_urb <- st_read("datos/procesado/bogota_ventana_urbana.gpkg", quiet = TRUE)
s11   <- st_read("datos/procesado/bogota_colegios_saber11.gpkg", quiet = TRUE)
xy <- st_coordinates(cole)
W  <- as.owin(st_union(st_geometry(loc[loc$localidad == "Kennedy", ])))
p  <- suppressWarnings(ppp(xy[, 1], xy[, 2], window = W))
WU <- as.owin(st_geometry(st_union(v_urb)))
pu <- suppressWarnings(ppp(xy[, 1], xy[, 2], window = WU))
en <- inside.owin(xy[, 1], xy[, 2], WU)
c11 <- en & !is.na(s11$s11_n)
p11 <- suppressWarnings(ppp(st_coordinates(s11)[c11, 1], st_coordinates(s11)[c11, 2], window = WU))

guarda("meta", list(
  fecha = format(Sys.Date()), R = R.version.string,
  paquetes = list(spatstat = as.character(packageVersion("spatstat")),
                  spatstat.explore = as.character(packageVersion("spatstat.explore")),
                  spatstat.model = as.character(packageVersion("spatstat.model")),
                  spatstat.geom = as.character(packageVersion("spatstat.geom")),
                  spatstat.data = as.character(packageVersion("spatstat.data")),
                  sf = as.character(packageVersion("sf"))),
  nota = "Cada bloque se calcula con el mismo código que el bloque de R del capítulo; las semillas viajan con el cálculo."))

# =====================================================================
# SESIÓN 1 · módulos 1 a 6
# =====================================================================
if (que %in% c("s1", "todo")) {
  # ---- ciudad y Kennedy (módulo 1) ----
  guarda("urbana", list(
    n_capa = nrow(cole), n_urbana = npoints(pu), area_km2 = area.owin(WU) / 1e6,
    lambda_km2 = npoints(pu) / area.owin(WU) * 1e6))
  guarda("kennedy", list(
    n = npoints(p), area_km2 = area.owin(W) / 1e6, lambda_km2 = npoints(p) / area.owin(W) * 1e6,
    caja_x_km = diff(W$xrange) / 1000, caja_y_km = diff(W$yrange) / 1000,
    n_atributo = sum(cole$localidad == "Kennedy", na.rm = TRUE),
    # Kennedy no está contenida en la ventana urbana: parte de su contorno y 3 de sus sedes caen fuera del perímetro
    sedes_fuera_de_la_urbana = sum(!inside.owin(p$x, p$y, WU)),
    area_fuera_de_la_urbana_pct = 100 * (area.owin(W) - area.owin(intersect.owin(W, WU))) / area.owin(W)))

  # ---- cuadrantes, y la rejilla movida (módulo 1) ----
  cuad <- quadratcount(p, nx = 8, ny = 8)
  caja <- as.rectangle(W); dx <- diff(caja$xrange) / 8; dy <- diff(caja$yrange) / 8
  mx <- c()
  for (sx in c(0, .25, .5, .75)) for (sy in c(0, .25, .5, .75)) {
    xb <- caja$xrange[1] - sx * dx + (0:9) * dx; yb <- caja$yrange[1] - sy * dy + (0:9) * dy
    mx <- c(mx, max(as.numeric(quadratcount(p, xbreaks = xb, ybreaks = yb))))
  }
  guarda("cuadrantes", list(
    nx = 8, celdas_rejilla = 64, celdas_con_ventana = length(as.numeric(cuad)),
    conteo_min = min(as.numeric(cuad)), conteo_max = max(as.numeric(cuad)),
    celdas_con_el_maximo = sum(as.numeric(cuad) == max(as.numeric(cuad))),
    desplazamientos = 16, maximos_desplazados = mx, rango_desplazados = range(mx)))

  # ---- núcleos y anchos (módulo 2) ----
  ker <- c("gaussian", "epanechnikov", "quartic", "disc")
  dg <- density(p, sigma = 400, dimyx = c(99, 96)); okg <- is.finite(as.numeric(dg$v))
  nuc_max <- sapply(ker, function(k) max(density(p, sigma = 400, kernel = k, dimyx = c(99, 96))) * 1e6)
  nuc_cor <- sapply(ker[-1], function(k) cor(as.numeric(dg$v)[okg], as.numeric(density(p, sigma = 400, kernel = k, dimyx = c(99, 96))$v)[okg]))
  dif_nuc <- (max(nuc_max) - min(nuc_max)) / nuc_max[["gaussian"]] * 100
  anchos <- c(233.3949, 330.0702, 466.7897, 660.1404, 933.5795, 1320.2807, 1867.1589)
  picos <- sapply(anchos, function(s) max(density(p, sigma = s, dimyx = c(99, 96))) * 1e6)
  caida <- (picos[1] - picos[7]) / picos[1] * 100
  guarda("nucleos", list(sigma_m = 400, max_km2 = as.list(nuc_max), cor_gauss = as.list(nuc_cor), dif_pct = dif_nuc))
  guarda("anchos", list(sigmas_m = anchos, picos_km2 = picos, caida_pct = caida,
                        razon_pasos = anchos[-1] / anchos[-7], razon_total = anchos[7] / anchos[1],
                        veces_el_nucleo = caida / dif_nuc,
                        caida_con_redondeo_1dec = (round(picos[1], 1) - round(picos[7], 1)) / round(picos[1], 1) * 100,
                        celda_x_m = diff(W$xrange) / 96, celda_y_m = diff(W$yrange) / 99,
                        celdas_en_233 = anchos[1] / (diff(W$xrange) / 96), nx = 96, ny = 99))

  # ---- selectores (módulo 3) ----
  selk <- c(diggle = as.numeric(bw.diggle(p)), ppl = as.numeric(bw.ppl(p)), CvL = as.numeric(bw.CvL(p)), scott = as.numeric(bw.scott(p))[1])
  selu <- c(diggle = as.numeric(bw.diggle(pu)), ppl = as.numeric(bw.ppl(pu)), CvL = as.numeric(bw.CvL(pu)), scott = as.numeric(bw.scott(pu))[1])
  guarda("selectores", list(
    kennedy = list(sigmas_m = as.list(selk), razon = max(selk) / min(selk), scott_x_m = as.numeric(bw.scott(p))[1], scott_y_m = as.numeric(bw.scott(p))[2]),
    ciudad  = list(sigmas_m = as.list(selu), razon = max(selu) / min(selu), scott_x_m = as.numeric(bw.scott(pu))[1], scott_y_m = as.numeric(bw.scott(pu))[2]),
    # bw.ppl y bw.CvL no optimizan sobre un continuo: evalúan su criterio en `ns` anchos de una rejilla y devuelven el mejor
    ns_ppl = eval(formals(bw.ppl)$ns), ns_cvl = eval(formals(bw.CvL)$ns), shortcut_ppl = eval(formals(bw.ppl)$shortcut)))

  # ---- los mismos selectores con una rejilla fina de anchos (módulo 3): `bw.ppl` y `bw.CvL` evalúan su criterio en `ns` anchos ----
  fin_k <- c(ppl = as.numeric(bw.ppl(p, ns = 256)), CvL = as.numeric(bw.CvL(p, ns = 256)))
  fin_u <- c(ppl = as.numeric(bw.ppl(pu, ns = 256)), CvL = as.numeric(bw.CvL(pu, ns = 256)))
  guarda("selectores_fino", list(ns = 256, kennedy = as.list(fin_k), ciudad = as.list(fin_u)))

  # ---- japanesepines y bw.ppl (módulo 3) ----
  jp <- japanesepines
  avisos <- NULL
  r <- withCallingHandlers(as.numeric(bw.ppl(jp)), warning = function(w) { avisos <<- c(avisos, conditionMessage(w)); invokeRestart("muffleWarning") })
  bj <- bw.ppl(jp, srange = c(0.01, 2), warn = FALSE)
  guarda("japanesepines", list(
    n = npoints(jp), lado_m = 5.7, bw_ppl = r, tope_intervalo = diameter(Window(jp)) / 2,
    aviso = avisos, optimo_con_srange_2 = as.numeric(bj),
    criterio_h = attr(bj, "h"), criterio_cv = attr(bj, "cv"),
    ayuda = ayuda_txt("japanesepines")))

  # ---- bordes (módulo 4): masas, porcentajes, picos ----
  b <- list()
  for (s in c(200, 400, 800)) {
    con <- density(p, sigma = s, dimyx = c(99, 96))
    sin <- density(p, sigma = s, dimyx = c(99, 96), edge = FALSE)
    dig <- density(p, sigma = s, dimyx = c(99, 96), diggle = TRUE)
    m <- c(sin = integra(sin), defecto = integra(con), diggle = integra(dig))
    b[[as.character(s)]] <- list(masa_sin = m[["sin"]], masa_defecto = m[["defecto"]], masa_diggle = m[["diggle"]],
                                 pct_sin = 100 * (m[["sin"]] / 262 - 1), pct_defecto = 100 * (m[["defecto"]] / 262 - 1), pct_diggle = 100 * (m[["diggle"]] / 262 - 1),
                                 max_sin = max(sin) * 1e6, max_defecto = max(con) * 1e6, max_diggle = max(dig) * 1e6)
  }
  guarda("bordes", c(b, list(horquilla_pp_800 = b[["800"]]$pct_defecto - b[["800"]]$pct_sin)))

  # ---- 300 patrones CSR con n = 262 en la ventana de Kennedy: desviación media de la masa integrada (módulo 4) ----
  set.seed(7)
  csr <- t(sapply(1:300, function(i) {
    X <- rpoint(262, win = W)
    unlist(lapply(c(400, 800), function(s) c(sin = integra(density(X, sigma = s, dimyx = c(99, 96), edge = FALSE)),
                                             defecto = integra(density(X, sigma = s, dimyx = c(99, 96))),
                                             diggle = integra(density(X, sigma = s, dimyx = c(99, 96), diggle = TRUE)))))
  }))
  colnames(csr) <- paste0(rep(c("sin", "defecto", "diggle"), 2), "_", rep(c(400, 800), each = 3))
  desv <- 100 * (csr / 262 - 1)
  guarda("bordes_csr", list(patrones = 300, n = 262,
                            media_pct = as.list(colMeans(desv)), sd_pct = as.list(apply(desv, 2, sd)),
                            ee_media_pct = as.list(apply(desv, 2, sd) / sqrt(300))))

  # ---- tiempos (módulo 4): mediana de 15, sobre la ventana urbana a 128 x 128 (varían con la máquina) ----
  t_of <- function(f) median(replicate(15, system.time(f())[["elapsed"]]))
  guarda("tiempos", list(
    ciudad_128 = list(defecto = t_of(function() density(pu, sigma = 720.3691, dimyx = c(128, 128))),
                      sin_corregir = t_of(function() density(pu, sigma = 720.3691, dimyx = c(128, 128), edge = FALSE)),
                      diggle = t_of(function() density(pu, sigma = 720.3691, dimyx = c(128, 128), diggle = TRUE))),
    nota = "Medianas de 15 ejecuciones; dependen de la máquina. Se aceptan con tolerancia."))

  # ---- identidad de Diggle (módulo 4): la fórmula a mano contra spatstat, en puntos del borde ----
  set.seed(1)
  s <- 800
  Wm <- as.mask(W, dimyx = c(700, 700)); xs <- Wm$xcol; ys <- Wm$yrow; inside <- Wm$m; dA <- Wm$xstep * Wm$ystep
  Xg <- matrix(rep(xs, each = length(ys)), nrow = length(ys)); Yg <- matrix(rep(ys, times = length(xs)), nrow = length(ys))
  Xi <- Xg[inside]; Yi <- Yg[inside]
  kg <- function(dx, dy) exp(-(dx^2 + dy^2) / (2 * s^2)) / (2 * pi * s^2)
  e_en <- function(x0, y0) sum(kg(Xi - x0, Yi - y0)) * dA
  ei <- mapply(e_en, p$x, p$y)
  digs <- density(p, sigma = s, dimyx = c(99, 96), diggle = TRUE); cons <- density(p, sigma = s, dimyx = c(99, 96))
  gx <- rep(digs$xcol, each = length(digs$yrow)); gy <- rep(digs$yrow, times = length(digs$xcol))
  fin <- which(is.finite(as.numeric(digs$v)))
  eu <- sapply(fin, function(k) e_en(gx[k], gy[k]))
  borde <- fin[eu < 0.55]; pick <- sample(borde, 8)
  tab <- t(sapply(pick, function(k) {
    u0 <- gx[k]; v0 <- gy[k]; sk <- sum(kg(p$x - u0, p$y - v0))
    c(D_mano = sum(kg(p$x - u0, p$y - v0) / ei) * 1e6, D_spatstat = as.numeric(digs$v)[k] * 1e6,
      def_mano = sk / e_en(u0, v0) * 1e6, def_spatstat = as.numeric(cons$v)[k] * 1e6)
  }))
  guarda("diggle_identidad", list(
    puntos = nrow(tab), sigma_m = s,
    error_pct_diggle = max(abs(tab[, 1] - tab[, 2]) / tab[, 2]) * 100,
    error_pct_defecto = max(abs(tab[, 3] - tab[, 4]) / tab[, 4]) * 100,
    cruce_pct = max(abs(tab[, 3] - tab[, 2]) / tab[, 2]) * 100,
    nota = "D_mano = suma de k(u - x_i) / e(x_i); def_mano = suma de k(u - x_i) / e(u); e por malla de 700 x 700 píxeles."))

  # ---- las tres capas de la ciudad (módulo 5) ----
  sg <- as.numeric(bw.CvL(pu)); dd <- c(218, 128)
  k_of <- density(pu,  sigma = sg, dimyx = dd, diggle = TRUE)
  k_11 <- density(p11, sigma = sg, dimyx = dd, diggle = TRUE)
  k_es <- density(p11, sigma = sg, dimyx = dd, diggle = TRUE, weights = s11$s11_n[c11])
  dentro <- is.finite(as.numeric(k_of$v)); vu <- function(im) as.numeric(im$v)[dentro]
  # lo mismo con la corrección de borde POR DEFECTO (sin `diggle = TRUE`): son las cifras de la versión de Python del módulo 5
  d_of <- density(pu,  sigma = sg, dimyx = dd)
  d_11 <- density(p11, sigma = sg, dimyx = dd)
  d_es <- density(p11, sigma = sg, dimyx = dd, weights = s11$s11_n[c11])
  guarda("capas_defecto", list(
    cor_of_11 = cor(vu(d_of), vu(d_11)), cor_of_es = cor(vu(d_of), vu(d_es)), cor_11_es = cor(vu(d_11), vu(d_es)),
    max_oferta = max(d_of) * 1e6, max_grado11 = max(d_11) * 1e6, max_estudiantes = max(d_es) * 1e6))
  guarda("capas", list(
    sigma_m = sg, n_oferta = npoints(pu), n_grado11 = npoints(p11), pct_grado11 = 100 * npoints(p11) / npoints(pu),
    evaluados = sum(s11$s11_n[c11]), max_oferta = max(k_of) * 1e6, max_grado11 = max(k_11) * 1e6, max_estudiantes = max(k_es) * 1e6,
    cor_of_11 = cor(vu(k_of), vu(k_11)), cor_of_es = cor(vu(k_of), vu(k_es)), cor_11_es = cor(vu(k_11), vu(k_es)),
    celda_x_m = diff(WU$xrange) / 128, celda_y_m = diff(WU$yrange) / 218, sigma_minimo_m = 3 * diff(WU$xrange) / 128,
    integral_estudiantes = integra(k_es)))
  loc_de <- function(x, y) { pt <- st_sfc(st_point(c(x, y)), crs = st_crs(loc)); i <- st_intersects(pt, loc)[[1]]; if (length(i)) as.character(loc$localidad[i[1]]) else NA }
  im_max <- function(im) { ij <- which(as.matrix(im$v) == max(im$v, na.rm = TRUE), arr.ind = TRUE)[1, ]; c(x = im$xcol[ij[2]], y = im$yrow[ij[1]]) }
  mo <- im_max(k_of); me <- im_max(k_es)
  guarda("capas_maximos", list(localidad_max_oferta = loc_de(mo[["x"]], mo[["y"]]), localidad_max_estudiantes = loc_de(me[["x"]], me[["y"]])))

  # ---- chorley (módulo 6) ----
  data(chorley)
  ch <- chorley; marks(ch) <- factor(as.character(marks(chorley)), levels = c("lung", "larynx"))
  rr <- relrisk(ch, sigma = 1); v <- as.numeric(rr$v); v <- v[is.finite(v)]
  rr0 <- relrisk(chorley, sigma = 1); v0 <- as.numeric(rr0$v); v0 <- v0[is.finite(v0)]
  orienta <- function(im, pp, nivel, k = 50L) {
    ij <- which(as.matrix(im$v) == max(as.numeric(im$v), na.rm = TRUE), arr.ind = TRUE)[1, ]
    x0 <- im$xcol[ij[2]]; y0 <- im$yrow[ij[1]]
    d <- (pp$x - x0)^2 + (pp$y - y0)^2
    vec <- marks(pp)[order(d)[seq_len(min(k, npoints(pp)))]]
    c(prop = mean(vec == nivel), n = sum(vec == nivel))
  }
  o_ch <- orienta(rr, ch, "larynx")
  ij_ch <- which(as.matrix(rr$v) == max(as.numeric(rr$v), na.rm = TRUE), arr.ind = TRUE)[1, ]
  d_ch <- sqrt((ch$x - rr$xcol[ij_ch[2]])^2 + (ch$y - rr$yrow[ij_ch[1]])^2)
  guarda("chorley", list(
    n_laringe = sum(marks(ch) == "larynx"), n_pulmon = sum(marks(ch) == "lung"), n = npoints(ch),
    area_km2 = area.owin(Window(ch)), global = mean(marks(ch) == "larynx"), mediana = median(v), maximo = max(v),
    maximo_sobre_global = max(v) / mean(marks(ch) == "larynx"),
    mediana_sin_fijar_niveles = median(v0), vecinos_k = 50, vecinos_casos = o_ch[["n"]], vecinos_prop = o_ch[["prop"]],
    max_dist_punto_mas_cercano_km = min(d_ch), max_dist_vecino_50_km = sort(d_ch)[50],
    ayuda = ayuda_txt("chorley")))

  # ---- Bogotá oficial / privado (módulo 6) ----
  marca <- factor(ifelse(cole$sector[en] == "Oficial", "oficial", "privado"), levels = c("privado", "oficial"))
  p_sec <- suppressWarnings(ppp(xy[en, 1], xy[en, 2], window = WU, marks = marca))
  rb <- relrisk(p_sec, sigma = sg); vb <- as.numeric(rb$v); vb <- vb[is.finite(vb)]
  m0 <- factor(ifelse(cole$sector[en] == "Oficial", "oficial", "privado"))
  p0 <- suppressWarnings(ppp(xy[en, 1], xy[en, 2], window = WU, marks = m0))
  r0 <- relrisk(p0, sigma = sg); v00 <- as.numeric(r0$v); v00 <- v00[is.finite(v00)]
  o_b <- orienta(rb, p_sec, "oficial")
  guarda("oficial", list(
    n_oficiales = sum(marks(p_sec) == "oficial"), n_privadas = sum(marks(p_sec) == "privado"), n = npoints(p_sec),
    global = mean(marks(p_sec) == "oficial"), mediana = median(vb), maximo = max(vb),
    brecha = mean(marks(p_sec) == "oficial") - median(vb),
    mediana_sin_fijar_niveles = median(v00), complemento_de_la_mediana = 1 - median(vb),
    area_mayoria_oficial_pct = 100 * mean(vb > 0.5),     # la respuesta directa a «¿en qué fracción de la ciudad son mayoría?»
    vecinos_k = 50, vecinos_oficiales = o_b[["n"]], vecinos_prop = o_b[["prop"]]))
}

write(toJSON(R_, auto_unbox = TRUE, digits = NA, pretty = TRUE, null = "null"), SALIDA)
cat("escrito", SALIDA, "\n")
