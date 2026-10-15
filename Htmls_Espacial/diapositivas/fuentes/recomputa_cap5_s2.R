# =====================================================================
# recomputa_cap5_s2.R — recómputo en R de las cifras de la sesión 2 (módulos 7 a 11)
# del capítulo 5. Hermano de `recomputa_cap5.R` (sesión 1).
#
# Cada módulo escribe su propio JSON (`recomputo_cap5_<módulo>.json`) para poder correr
# en paralelo: los ajustes con la corrección isotrópica de `kppm` tardan ~127 s cada uno.
# `verifica_cifras_cap5.py` junta todos los `recomputo_cap5*.json`.
#
# A diferencia del precálculo del capítulo, aquí NO se lee ninguna caché: todo se vuelve a
# ajustar, con el mismo código del generador (`ppp_kppm()` de `precalculo/puntual.R`) y las
# mismas semillas (5028 las envolventes, 5030 el Hawkes, 2026 `rhohat`).
#
# Desde la raíz del repo:
#   for m in m7 m8 m9 m10 m11_Thomas m11_MatClust m11_LGCP m11_redwood_hawkes; do
#     precalculo/rscript.sh Htmls_Espacial/diapositivas/fuentes/recomputa_cap5_s2.R $m & done; wait
# =====================================================================
suppressPackageStartupMessages({ library(sf); library(spatstat); library(jsonlite) })
options(scipen = 999, digits = 7, warn = 1)
args <- commandArgs(trailingOnly = TRUE)
modulo <- if (length(args)) args[1] else stop("hay que nombrar el módulo: m7, m8, m9, m10, m11_<modelo>, m11_redwood_hawkes")
SALIDA <- sprintf("Htmls_Espacial/diapositivas/fuentes/recomputo_cap5_%s.json", modulo)
OUT <- list()
guarda <- function(nombre, valor) OUT[[nombre]] <<- valor
suppressWarnings(source("precalculo/puntual.R"))     # ppp_kppm(), ppp_rejilla_r(), ppp_curva(), PPP_CORR

cole  <- st_read("datos/procesado/bogota_colegios.gpkg", quiet = TRUE)
v_urb <- st_read("datos/procesado/bogota_ventana_urbana.gpkg", quiet = TRUE)
xy <- st_coordinates(cole)
WU <- as.owin(st_geometry(st_union(v_urb)))
pu <- suppressWarnings(ppp(xy[, 1], xy[, 2], window = WU))
X0 <- mean(pu$x); Y0 <- mean(pu$y)
centro <- ppp(X0, Y0, window = WU)
COVS <- list(dcen = distfun(centro), xc = function(x, y) (x - X0) / 1000, yc = function(x, y) (y - Y0) / 1000)
N_URB <- npoints(pu); A_URB <- area.owin(WU)
ayuda_txt <- function(tema) {
  h <- utils:::.getHelpFile(help(tema, package = "spatstat.data"))
  paste(capture.output(tools::Rd2txt(h, options = list(underline_titles = FALSE))), collapse = "\n")
}
meta_t0 <- Sys.time()

# =====================================================================
if (modulo == "m7") {
  # ---- el bloque del módulo 7, tal cual: rhohat es aleatorio, hay semilla ----
  rango <- function(p, cov) {
    rh <- rhohat(p, cov)
    ok <- is.finite(rh$rho)
    x <- rh[[1]][ok]; y <- rh$rho[ok]
    vp <- if (is.function(cov)) cov(p$x, p$y) else cov[p]
    q <- quantile(vp, c(0.05, 0.95))
    b <- x >= q[1] & x <= q[2]
    c(total = max(y) / min(y), bulto = max(y[b]) / min(y[b]), q05 = q[[1]], q95 = q[[2]])
  }
  set.seed(2026)
  re <- rango(bei, bei.extra$elev)
  rg <- rango(bei, bei.extra$grad)
  rd <- rango(pu, distfun(centro))
  guarda("m7", list(
    bei = list(n = npoints(bei), ventana_x_m = diff(bei$window$xrange), ventana_y_m = diff(bei$window$yrange),
               elevacion_min_m = min(bei.extra$elev), elevacion_max_m = max(bei.extra$elev),
               pendiente_min = min(bei.extra$grad), pendiente_max = max(bei.extra$grad),
               ayuda = ayuda_txt("bei")),
    elevacion = list(total = re[["total"]], bulto = re[["bulto"]], infla = re[["total"]] / re[["bulto"]]),
    pendiente = list(total = rg[["total"]], bulto = rg[["bulto"]], infla = rg[["total"]] / rg[["bulto"]]),
    bogota = list(total = rd[["total"]], bulto = rd[["bulto"]], infla = rd[["total"]] / rd[["bulto"]], n = N_URB)))
  # cuánto se mueve la razón de la elevación entre semillas (el capítulo dice «entre 21.12 y 21.14»)
  tot <- sapply(1:20, function(s) { set.seed(s); rango(bei, bei.extra$elev)[["total"]] })
  guarda("m7_semillas", list(n_semillas = 20, min = min(tot), max = max(tot), valores = tot))
}

# =====================================================================
if (modulo == "m8") {
  # igual que el capítulo: media de λ̂ sobre una máscara de 4096 px de lado (con 2048 la cifra se mueve ±0.015 sedes)
  integral_fina <- function(f) A_URB * mean(suppressMessages(suppressWarnings(predict(f, dimyx = 4096))))
  f_hom <- ppm(pu ~ 1)
  lam_mle <- exp(unname(coef(f_hom))); lam_ing <- N_URB / A_URB
  f_bt <- ppm(pu ~ 1, forcefit = TRUE)
  q_bt <- quad.ppm(f_bt); sw <- sum(w.quad(q_bt))
  # teselas de la cuadratura por defecto que se quedan sin ningún punto (el área que nadie cuenta)
  teselas_vacias <- function(Q) {
    pw <- Q$param$weight; nt <- pw$ntile; ar <- pw$areas
    U <- union.quad(Q)
    id <- gridindex(U$x, U$y, WU$xrange, WU$yrange, nt[1], nt[2])$index
    vac <- setdiff(which(ar > 0), unique(id))
    list(tocan = sum(ar > 0), vacias = length(vac), area = sum(ar[vac]))
  }
  tv_bt <- teselas_vacias(q_bt)
  guarda("m8_homogeneo", list(
    fitter = f_hom$fitter, lambda_km2 = lam_mle * 1e6, ingenua_km2 = lam_ing * 1e6,
    dif_relativa = abs(lam_mle - lam_ing) / lam_ing, n = N_URB, area_km2 = A_URB / 1e6,
    forzado = list(fitter = f_bt$fitter, lambda_km2 = exp(unname(coef(f_bt))) * 1e6,
                   exceso_pct = 100 * (exp(unname(coef(f_bt))) / lam_mle - 1),
                   suma_pesos_km2 = sw / 1e6, faltan_km2 = (A_URB - sw) / 1e6,
                   teselas_tocan = tv_bt$tocan, teselas_vacias = tv_bt$vacias),
    aic = AIC(f_hom), aic_forzado = AIC(f_bt),
    ntile = as.integer(q_bt$param$weight$ntile), npix = as.integer(q_bt$param$weight$npix),
    tesela_m = c(diff(WU$xrange), diff(WU$yrange)) / as.integer(q_bt$param$weight$ntile)))
  # `nd` no interviene cuando el ajuste es exacto: el constante con nd = 300 es el mismo
  f_hom300 <- ppm(pu ~ 1, nd = 300)
  guarda("m8_constante_nd300", list(fitter = f_hom300$fitter, aic = AIC(f_hom300), aic_defecto = AIC(f_hom),
                                    mismo = isTRUE(all.equal(AIC(f_hom300), AIC(f_hom)))))
  filas <- lapply(c(50L, 100L, 200L, 300L), function(nd) {
    f <- ppm(pu ~ dcen, covariates = COVS, nd = nd)
    Q <- quad.ppm(f); lam <- fitted(f)
    suma_log <- sum(log(lam[is.data(Q)])); ll <- as.numeric(logLik(f))
    ix <- integral_fina(f)
    tv <- teselas_vacias(Q)
    list(nd = nd, ficticios = npoints(Q$dummy), pendiente = unname(coef(f)[2]), ee = unname(sqrt(diag(vcov(f)))[2]),
         aic = AIC(f), sin_contar_km2 = tv$area / 1e6, sedes_esperadas = ix, logver_ppm = ll, logver_exacta = suma_log - ix,
         suma_log = suma_log, integral_por_cuadratura = sum(w.quad(Q) * lam))
  })
  pend <- sapply(filas, `[[`, "pendiente"); aics <- sapply(filas, `[[`, "aic")
  llp <- sapply(filas, `[[`, "logver_ppm"); llx <- sapply(filas, `[[`, "logver_exacta")
  f_def <- ppm(pu ~ dcen, covariates = COVS)
  aic_exacto <- -2 * filas[[2]]$logver_exacta + 4
  guarda("m8_nd", list(
    filas = filas,
    rango_pendiente_en_ee = (max(pend) - min(pend)) / filas[[2]]$ee, rango_aic = max(aics) - min(aics),
    rango_logver_ppm = diff(range(llp)), rango_logver_exacta = diff(range(llx)),
    gana_distancia_ppm = AIC(f_hom) - AIC(f_def),
    gana_constante_exacta = aic_exacto - AIC(f_hom),
    gana_constante_misma = AIC(f_def) - AIC(f_bt),
    ficticios_por_defecto = npoints(quad.ppm(f_def)$dummy)))
  # la intensidad media de la cuadratura frente a la integral bien hecha (módulo 8, bloque de R)
  q1 <- quad.ppm(f_def); lam1 <- fitted(f_def)
  guarda("m8_bloque", list(suma_log = sum(log(lam1[is.data(q1)])), integral = sum(w.quad(q1) * lam1), logLik = as.numeric(logLik(f_def)),
                           integral_fina_4096 = integral_fina(f_def), pesos_km2 = sum(w.quad(q1)) / 1e6))
}

# =====================================================================
if (modulo == "m9") {
  coefs_de <- function(f) {
    co <- coef(f); vc <- suppressWarnings(try(vcov(f), silent = TRUE))
    ee <- if (is.null(vc) || inherits(vc, "try-error")) numeric(0) else suppressWarnings(as.numeric(sqrt(diag(vc))))
    list(nombres = names(co), coef = unname(co), n_ee = length(ee), ee = ee, z = if (length(ee) == length(co)) unname(co / ee) else NULL,
         vcov_es_null = is.null(vc), aic = AIC(f))
  }
  cond_de <- function(f) { s <- svd(model.matrix(f))$d; min(s) / max(s) }
  f_crudo <- suppressWarnings(ppm(pu ~ x + y)); f_centr <- ppm(pu ~ xc + yc, covariates = COVS)
  f_dcen <- ppm(pu ~ dcen, covariates = COVS)
  ee0 <- suppressWarnings(sqrt(diag(vcov(f_crudo))))
  guarda("m9", list(
    crudo = c(coefs_de(f_crudo), list(cond = cond_de(f_crudo), length_ee_igual_a_coef = length(ee0) == length(coef(f_crudo)),
                                      dim_sqrt_diag_null = if (is.null(vcov(f_crudo))) dim(suppressWarnings(sqrt(diag(NULL)))) else NULL)),
    centrado = c(coefs_de(f_centr), list(cond = cond_de(f_centr))),
    distancia = coefs_de(f_dcen),
    mejora_condicion = cond_de(f_centr) / cond_de(f_crudo)))
}

# =====================================================================
if (modulo == "m10") {
  f_centr <- ppm(pu ~ xc + yc, covariates = COVS)
  # --- el bloque de R del módulo: 39 simulaciones ---
  set.seed(5028)
  e39 <- envelope(f_centr, Kinhom, nsim = 39, correction = "translate", verbose = FALSE, savefuns = TRUE)
  dr <- e39$r > 0; fu <- e39$obs > e39$hi | e39$obs < e39$lo
  guarda("m10_e39", list(nivel_puntual = 2 / (39 + 1), pct_fuera = 100 * mean(fu[dr]), r_max = max(e39$r),
                         dclf = dclf.test(e39)$p.value, mad = mad.test(e39)$p.value))
  # --- la envolvente de 999, como en el generador (misma semilla) ---
  t0 <- proc.time()[["elapsed"]]
  set.seed(5028)
  env <- envelope(f_centr, Kinhom, nsim = 999L, correction = "translate", verbose = FALSE, savefuns = TRUE)
  seg <- proc.time()[["elapsed"]] - t0
  rg <- ppp_rejilla_r(env, 101L)
  obs <- ppp_curva(env, "obs", rg); lo <- ppp_curva(env, "lo", rg); hi <- ppp_curva(env, "hi", rg); mme <- ppp_curva(env, "mmean", rg)
  fuera <- obs > hi | obs < lo; dentro_r <- rg > 0
  i_fuera <- which(fuera[dentro_r])
  sale_loo <- function(M) {
    sale <- logical(ncol(M))
    for (i in seq_len(nrow(M))) {
      o <- order(M[i, ]); k <- length(o)
      if (M[i, o[k]] > M[i, o[k - 1L]]) sale[o[k]] <- TRUE
      if (M[i, o[1L]] < M[i, o[2L]]) sale[o[1L]] <- TRUE
    }
    sale
  }
  simf <- as.data.frame(attr(env, "simfuns")); M_sim <- as.matrix(simf[, -1L])
  ok_sim <- simf$r > 0 & apply(M_sim, 1, function(z) all(is.finite(z)))
  sale_nat <- sale_loo(M_sim[ok_sim, , drop = FALSE])
  M_101 <- vapply(seq_len(999L), function(j) approx(simf$r, M_sim[, j], xout = rg, rule = 2)$y, numeric(length(rg)))
  sale_101 <- sale_loo(M_101[dentro_r, , drop = FALSE])
  t_dclf <- dclf.test(env); t_mad <- mad.test(env)
  mm_nat <- env$mmean; r_mad_obs <- simf$r[which.max(abs(env$obs - mm_nat))]
  dev_loo <- vapply(seq_len(999L), function(j) {
    ref <- (mm_nat * 999 - M_sim[, j]) / 998; d <- abs(M_sim[, j] - ref); d[!is.finite(d)] <- 0
    c(max(d), simf$r[which.max(d)])
  }, numeric(2))
  mad_obs <- max(abs(env$obs - mm_nat), na.rm = TRUE); superan <- dev_loo[1, ] >= mad_obs
  guarda("m10", list(
    nsim = 999, segundos = seg, nivel_puntual_pct = 100 * 2 / 1000, r_max_m = max(rg), n_nodos = 101,
    pct_fuera = 100 * mean(fuera[dentro_r]), primer_r_fuera_m = min(rg[dentro_r][fuera[dentro_r]]),
    ultimo_r_fuera_m = max(rg[dentro_r][fuera[dentro_r]]), nodos_dentro_tras_el_tramo = sum(dentro_r) - max(i_fuera),
    mmean_vs_teorica_pct = 100 * max(abs(mme[dentro_r] / (pi * rg[dentro_r]^2) - 1)),
    nativa = list(nodos = sum(ok_sim), fuera = sum(sale_nat), pct = 100 * mean(sale_nat)),
    simulador = list(nodos = sum(dentro_r), fuera = sum(sale_101), pct = 100 * mean(sale_101)),
    veces_el_nivel = 100 * mean(sale_nat) / (100 * 2 / 1000),
    dclf_p = t_dclf$p.value, mad_p = t_mad$p.value, r_mad_observada_m = r_mad_obs,
    mad_superan = sum(superan), r_min_mad_superan_m = min(dev_loo[2, superan])))
}

# =====================================================================
if (grepl("^m11_(Thomas|MatClust|LGCP)$", modulo)) {
  m <- sub("^m11_", "", modulo)
  ajuste <- function(p, cr, tendencia = ~1, covs = NULL) {
    k <- ppp_kppm(p, m, cr, tendencia = tendencia, covariables = covs)
    list(segundos = k$segundos, parametros = k$parametros, mu = k$mu,
         coef = unname(coef(k$ajuste)), ee = unname(sqrt(diag(vcov(k$ajuste)))))
  }
  iso <- ajuste(pu, "iso"); tr <- ajuste(pu, "translate")
  sin_dup <- ajuste(unique(pu), "translate")
  f_centr <- ppm(pu ~ xc + yc, covariates = COVS)
  co_p <- unname(coef(f_centr)); ee_p <- unname(sqrt(diag(vcov(f_centr))))
  t_iso <- ajuste(pu, "iso", ~ xc + yc, COVS); t_tr <- ajuste(pu, "translate", ~ xc + yc, COVS)
  guarda(paste0("m11_", m), list(
    modelo = m, iso = iso[c("segundos", "parametros", "mu")], translate = tr[c("segundos", "parametros", "mu")],
    sin_duplicados = sin_dup[c("parametros", "mu")], n_unicos = npoints(unique(pu)),
    tendencia = list(poisson = list(coef = co_p, ee = ee_p),
                     iso = list(coef = t_iso$coef, ee = t_iso$ee, z = t_iso$coef / t_iso$ee, inflacion = t_iso$ee / ee_p),
                     translate = list(coef = t_tr$coef, ee = t_tr$ee, z = t_tr$coef / t_tr$ee, inflacion = t_tr$ee / ee_p))))
}

# =====================================================================
if (modulo == "m11_redwood_hawkes") {
  data(redwood)
  k_iso <- kppm(redwood ~ 1, "Thomas"); k_tr <- kppm(redwood ~ 1, "Thomas", statargs = list(correction = "translate"))
  set.seed(1); k_a <- kppm(redwood ~ 1, "Thomas"); set.seed(999); k_b <- kppm(redwood ~ 1, "Thomas")
  guarda("m11_kppm_determinista", list(mismo = isTRUE(all.equal(unlist(k_a$clustpar), unlist(k_b$clustpar))) && isTRUE(all.equal(k_a$mu, k_b$mu))))
  guarda("m11_ventana", list(piezas = length(st_cast(st_union(v_urb), "POLYGON"))))
  guarda("m11_redwood", list(n = npoints(redwood),
                             iso = c(as.list(k_iso$clustpar), mu = k_iso$mu), translate = c(as.list(k_tr$clustpar), mu = k_tr$mu),
                             ayuda = ayuda_txt("redwood")))
  hawkes <- function(mu, alpha, beta, Tmax, semilla) {
    set.seed(semilla); t <- 0; ev <- numeric(0)
    repeat {
      cota <- mu + sum(alpha * exp(-beta * (t - ev)))
      t <- t - log(runif(1)) / cota
      if (t > Tmax) break
      if (runif(1) <= (mu + sum(alpha * exp(-beta * (t - ev)))) / cota) ev <- c(ev, t)
    }
    ev
  }
  ev <- hawkes(0.5, 0.8, 1.4, 4000, 5030)
  set.seed(5031); ev_p <- sort(runif(length(ev), 0, 4000))
  disp <- function(e, k = 200L) { cnt <- table(cut(e, seq(0, 4000, length.out = k + 1L), include.lowest = TRUE)); var(as.numeric(cnt)) / mean(as.numeric(cnt)) }
  guarda("m11_hawkes", list(
    mu = 0.5, alpha = 0.8, beta = 1.4, T = 4000, razon_ramificacion = 0.8 / 1.4, tasa_teorica = 0.5 / (1 - 0.8 / 1.4),
    n_eventos = length(ev), tasa_simulada = length(ev) / 4000,
    dispersion_hawkes = disp(ev), dispersion_poisson = disp(ev_p), veces_mas_agregado = disp(ev) / disp(ev_p)))
}

OUT$meta <- list(modulo = modulo, fecha = format(Sys.Date()), R = R.version.string,
                 segundos_totales = as.numeric(difftime(Sys.time(), meta_t0, units = "secs")),
                 spatstat = as.character(packageVersion("spatstat")), spatstat.explore = as.character(packageVersion("spatstat.explore")),
                 spatstat.model = as.character(packageVersion("spatstat.model")))
write(toJSON(OUT, auto_unbox = TRUE, digits = NA, pretty = TRUE, null = "null", na = "null"), SALIDA)
cat("escrito", SALIDA, sprintf("(%.0f s)\n", OUT$meta$segundos_totales))
