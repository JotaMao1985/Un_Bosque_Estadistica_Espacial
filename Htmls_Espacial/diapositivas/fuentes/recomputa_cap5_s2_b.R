# =====================================================================
# recomputa_cap5_s2_b.R — recómputos de la revisión de la sesión 2 tras la auditoría independiente B
# (2026-10-01). Hermano de `recomputa_cap5_s2.R`: mismo patrón, mismas semillas del capítulo, y los
# números nuevos que pidieron las correcciones (ancho de `rhohat`, jitter, información de Fisher,
# otras semillas de la envolvente, g inhomogénea, tendencia flexible, K empírica, `vcov` exacto,
# réplicas de Hawkes, duplicados, kppm con tendencia).
#
# Cada módulo escribe su propio JSON (`recomputo_cap5_b_<módulo>.json`) para correr en paralelo;
# `verifica_cifras_cap5.py` junta todos los `recomputo_cap5*.json`.
#
# Desde la raíz del repo:
#   R=precalculo/rscript.sh; F=Htmls_Espacial/diapositivas/fuentes/recomputa_cap5_s2_b.R
#   for m in b_m7 b_m9 b_m10_pcf b_m10_flex b_m11_kemp b_m11_vcov b_m11_hawkes b_m11_dups b_m11_trend; do $R $F $m & done
#   for s in 1 2 3 4 5 6 7 8; do $R $F b_m10_sem $s & done; wait
# =====================================================================
suppressPackageStartupMessages({ library(sf); library(spatstat); library(jsonlite) })
options(scipen = 999, digits = 7, warn = 1)
args <- commandArgs(trailingOnly = TRUE)
modulo <- if (length(args)) args[1] else stop("hay que nombrar el módulo")
semilla <- if (length(args) > 1) as.integer(args[2]) else NA_integer_
sufijo <- if (modulo == "b_m10_sem") sprintf("b_m10_s%d", semilla) else modulo
SALIDA <- sprintf("Htmls_Espacial/diapositivas/fuentes/recomputo_cap5_%s.json", sufijo)
OUT <- list()
guarda <- function(nombre, valor) OUT[[nombre]] <<- valor

cole  <- st_read("datos/procesado/bogota_colegios.gpkg", quiet = TRUE)
v_urb <- st_read("datos/procesado/bogota_ventana_urbana.gpkg", quiet = TRUE)
xy <- st_coordinates(cole)
WU <- as.owin(st_geometry(st_union(v_urb)))
pu <- suppressWarnings(ppp(xy[, 1], xy[, 2], window = WU))
X0 <- mean(pu$x); Y0 <- mean(pu$y)
centro <- ppp(X0, Y0, window = WU)
COVS <- list(xc = function(x, y) (x - X0) / 1000, yc = function(x, y) (y - Y0) / 1000)
N_URB <- npoints(pu); A_URB <- area.owin(WU)
meta_t0 <- Sys.time()
quieto <- function(expr) suppressMessages(suppressWarnings(expr))
# NSIM_PRUEBA=19 corre el módulo entero en segundos, para probar que el JSON se arma bien
nsim_o <- function(por_defecto) { v <- Sys.getenv("NSIM_PRUEBA", ""); if (nzchar(v)) as.integer(v) else por_defecto }

# ---------------------------------------------------------------------
if (modulo == "b_m7") {
  # ¿Cuánto mueve el ancho del núcleo la razón de la curva de Bogotá? (jitter = FALSE: no depende de la semilla)
  dcen <- distfun(centro)
  vp <- dcen(pu$x, pu$y); q <- quantile(vp, c(0.05, 0.95))
  razon <- function(adj, jit = FALSE) {
    rh <- quieto(rhohat(pu, dcen, jitter = jit, adjust = adj))
    ok <- is.finite(rh$rho); x <- rh[[1]][ok]; y <- rh$rho[ok]
    b <- x >= q[[1]] & x <= q[[2]]
    c(total = max(y) / min(y), bulto = max(y[b]) / min(y[b]))
  }
  adj <- c(0.5, 1, 2, 4)
  res <- sapply(adj, razon)
  guarda("m7b_adjust", list(adjust = adj, total = unname(res["total", ]), bulto = unname(res["bulto", ]),
                            infla = unname(res["total", ] / res["bulto", ])))
  # de dónde viene lo aleatorio: el jitter de la covariable en los puntos
  r1 <- razon(1); r2 <- razon(1)
  a <- quieto(rhohat(pu, dcen)); b <- quieto(rhohat(pu, dcen))
  set.seed(7); u0 <- runif(1)
  set.seed(7); invisible(quieto(rhohat(pu, dcen, jitter = FALSE))); u1 <- runif(1)
  set.seed(7); invisible(quieto(rhohat(pu, dcen))); u2 <- runif(1)
  guarda("m7b_jitter", list(identico_con_FALSE = isTRUE(all.equal(r1, r2)),
                            distinto_con_TRUE = !isTRUE(all.equal(a$rho, b$rho)),
                            consume_rng_con_FALSE = !isTRUE(all.equal(u0, u1)),
                            consume_rng_con_TRUE = !isTRUE(all.equal(u0, u2)),
                            total_FALSE = r1[["total"]], bulto_FALSE = r1[["bulto"]]))
}

# ---------------------------------------------------------------------
if (modulo == "b_m9") {
  # 1.794e-10 es el condicionamiento de la matriz de DISEÑO; la información de Fisher es de otro orden
  f_crudo <- ppm(pu ~ x + y)
  f_centr <- ppm(pu ~ xc + yc, covariates = COVS)
  Fc <- vcov(f_crudo, what = "fisher"); Ft <- vcov(f_centr, what = "fisher")
  sv <- function(M) { s <- svd(M)$d; min(s) / max(s) }
  falla <- try(solve(Fc), silent = TRUE)
  guarda("m9b_info", list(
    rcond_info_crudo = rcond(Fc), rcond_info_centrado = rcond(Ft), tolerancia_solve = .Machine$double.eps,
    sv_info_crudo = sv(Fc), sv_info_centrado = sv(Ft),
    sv_diseno_crudo = sv(model.matrix(f_crudo)), sv_diseno_centrado = sv(model.matrix(f_centr)),
    solve_falla = inherits(falla, "try-error"),
    mensaje_solve = if (inherits(falla, "try-error")) trimws(conditionMessage(attr(falla, "condition"))) else NA_character_))
}

# ---------------------------------------------------------------------
if (modulo == "b_m9_dcen") {
  # «la z de dcen no encuentra una relación log-lineal, que no es lo mismo que ninguna relación»:
  # con la integral bien hecha (máscara de 2048 px), un dcen cuadrático mejora el AIC del constante
  dcen <- distfun(centro); cv <- list(dk = function(x, y) dcen(x, y) / 1000)
  ll_exacta <- function(f) { P <- quieto(predict(f, dimyx = 2048)); sum(log(fitted(f)[is.data(quad.ppm(f))])) - A_URB * mean(P) }
  f_c <- ppm(pu ~ 1)
  f_q <- quieto(ppm(pu ~ polynom(dk, 2), covariates = cv, nd = 200))
  ll0 <- as.numeric(logLik(f_c)); llq <- ll_exacta(f_q)
  aic0 <- -2 * ll0 + 2 * length(coef(f_c)); aicq <- -2 * llq + 2 * length(coef(f_q))
  guarda("m9b_dcen", list(aic_constante = aic0, aic_cuadratico = aicq, dif_aic = aic0 - aicq, lr = 2 * (llq - ll0),
                          k_cuadratico = length(coef(f_q)), p_chi2 = pchisq(2 * (llq - ll0), length(coef(f_q)) - 1, lower.tail = FALSE)))
}

# ---------------------------------------------------------------------
if (modulo == "b_m10_sem") {
  # la envolvente de 999 del módulo 10 con OTRA semilla: ¿cuánto de lo que dice el capítulo es de la semilla?
  f_centr <- ppm(pu ~ xc + yc, covariates = COVS)
  set.seed(semilla)
  t0 <- proc.time()[["elapsed"]]
  nS <- nsim_o(999)
  e <- quieto(envelope(f_centr, Kinhom, nsim = nS, correction = "translate", verbose = FALSE, savefuns = TRUE))
  seg <- proc.time()[["elapsed"]] - t0
  rr <- e$r
  M <- as.matrix(as.data.frame(attr(e, "simfuns"))[, -1])
  # banda de la envolvente en la rejilla nativa (512 radios) y en 101 nodos, como el simulador del capítulo
  fuera_nat <- (e$obs > e$hi | e$obs < e$lo)[rr > 0]
  g101 <- seq(0, max(rr), length.out = 101)
  ap <- function(y) approx(rr, y, xout = g101)$y
  obs101 <- ap(e$obs); lo101 <- ap(e$lo); hi101 <- ap(e$hi); mm101 <- ap(e$mmean)
  f101 <- (obs101 > hi101 | obs101 < lo101)[g101 > 0]
  idx <- which(g101 > 0)[f101]
  # cuántas de las 999 curvas cruzan la banda de las otras (salida estricta, dejando fuera la propia)
  sale_loo <- function(M) {
    out <- rep(FALSE, ncol(M))
    for (i in seq_len(nrow(M))) {
      fila <- M[i, ]; ord <- sort(fila, decreasing = TRUE)
      if (ord[1] > ord[2]) out[which(fila == ord[1])[1]] <- TRUE
      ord2 <- sort(fila)
      if (ord2[1] < ord2[2]) out[which(fila == ord2[1])[1]] <- TRUE
    }
    out
  }
  ok <- rr > 0 & apply(M, 1, function(z) all(is.finite(z)))
  s_nat <- sale_loo(M[ok, , drop = FALSE])
  M101 <- apply(M, 2, function(col) approx(rr, col, xout = g101)$y)
  s_101 <- sale_loo(M101[g101 > 0, , drop = FALSE])
  rel101 <- (mm101 / (pi * g101^2) - 1)[g101 > 0]; relnat <- (e$mmean / (pi * rr^2) - 1)[rr > 0]
  d <- dclf.test(e); m <- mad.test(e)
  nivel <- 100 * 2 / (nS + 1)
  guarda(sprintf("m10b_sem_%d", semilla), list(
    semilla = semilla, segundos = seg,
    fuera_101 = sum(f101), pct_101 = 100 * mean(f101), arriba_101 = sum((obs101 > hi101)[g101 > 0]), abajo_101 = sum((obs101 < lo101)[g101 > 0]),
    primer_r_101 = min(g101[idx]), ultimo_r_101 = max(g101[idx]), contiguos_101 = all(diff(idx) == 1),
    nodos_dentro_tras_tramo_101 = sum(g101 > max(g101[idx])),
    fuera_nativa = sum(fuera_nat), pct_nativa = 100 * mean(fuera_nat),
    tasa_fuera_nativa = sum(s_nat), tasa_pct_nativa = 100 * mean(s_nat), veces_el_nivel_nativa = 100 * mean(s_nat) / nivel,
    tasa_fuera_101 = sum(s_101), tasa_pct_101 = 100 * mean(s_101),
    max_rel_mmean_101_pct = 100 * max(abs(rel101)), max_rel_mmean_nativa_pct = 100 * max(abs(relnat)),
    dclf_p = unname(d$p.value), mad_p = unname(m$p.value)))
}

# ---------------------------------------------------------------------
if (modulo == "b_m10_pcf") {
  # la K acumula; la g inhomogénea mira cada escala por separado
  f_centr <- ppm(pu ~ xc + yc, covariates = COVS)
  rr <- seq(0, 6000, length.out = 241)
  set.seed(4242)
  e <- quieto(envelope(f_centr, pcfinhom, nsim = nsim_o(199), correction = "translate", r = rr, verbose = FALSE, savefuns = TRUE))
  ok <- e$r > 0 & is.finite(e$obs)
  fuera <- (e$obs > e$hi)[ok]; rok <- e$r[ok]
  runs <- rle(fuera)
  en <- function(rv) { j <- which.min(abs(e$r - rv)); list(g_obs = e$obs[j], mmean = e$mmean[j], hi = e$hi[j], lo = e$lo[j], g_sobre_mmean = e$obs[j] / e$mmean[j]) }
  guarda("m10b_pcf", list(
    semilla = 4242, nsim = 199, radios = sum(ok), fuera_arriba = sum(fuera), pct_fuera_arriba = 100 * mean(fuera),
    primer_r_fuera = min(rok[fuera]), ultimo_r_fuera = max(rok[fuera]),
    primera_racha_largo = runs$lengths[1], primera_racha_hasta_r = rok[runs$lengths[1]],
    g_500 = en(500), g_1000 = en(1000), g_2000 = en(2000), g_3000 = en(3000)))
}

# ---------------------------------------------------------------------
if (modulo == "b_m10_flex") {
  # la misma envolvente (Kinhom, traslación, simulada desde el ajuste) con una tendencia más flexible
  filas <- list()
  for (gr in c(1, 10, 12)) {
    f <- eval(bquote(ppm(pu ~ polynom(xc, yc, .(gr)), covariates = COVS)))
    P <- quieto(predict(f, dimyx = 1024))
    ll <- sum(log(fitted(f)[is.data(quad.ppm(f))])) - A_URB * mean(P)
    fila <- list(grado = gr, k = length(coef(f)), aic_ppm = AIC(f), aic_integral_fina = -2 * ll + 2 * length(coef(f)),
                 int_min_km2 = min(P) * 1e6, int_max_km2 = max(P) * 1e6, int_media_km2 = mean(P) * 1e6, semillas = list())
    for (sd in c(101, 202)) {
      set.seed(sd)
      e <- quieto(envelope(f, Kinhom, nsim = nsim_o(199), correction = "translate", verbose = FALSE, savefuns = TRUE))
      ok <- e$r > 0; fuera <- (e$obs > e$hi | e$obs < e$lo)[ok]
      fila$semillas[[as.character(sd)]] <- list(pct_fuera = 100 * mean(fuera), dclf_p = unname(dclf.test(e)$p.value), mad_p = unname(mad.test(e)$p.value))
    }
    filas[[as.character(gr)]] <- fila
  }
  guarda("m10b_flex", filas)
}

# ---------------------------------------------------------------------
if (modulo == "b_m11_kemp") {
  # las dos K empíricas: la isotrópica cuesta ~2 min y la de traslación, una fracción de segundo
  t_tr <- system.time(Ktr <- Kest(pu, correction = "translate"))[["elapsed"]]
  t_iso <- system.time(Kiso <- Kest(pu, correction = "isotropic"))[["elapsed"]]
  r <- Ktr$r
  ki <- approx(Kiso$r, Kiso$iso, xout = r)$y; kt <- Ktr$trans
  ok <- r > 250 & is.finite(ki) & is.finite(kt)
  dif <- 100 * (kt / ki - 1)
  en <- function(rv) { a <- approx(r, ki, rv)$y; b <- approx(r, kt, rv)$y
    list(dif_pct = 100 * (b / a - 1), exceso_iso = a - pi * rv^2, exceso_trans = b - pi * rv^2, cociente_exceso = (b - pi * rv^2) / (a - pi * rv^2)) }
  guarda("m11b_kemp", list(t_iso_s = t_iso, t_trans_s = t_tr, cociente_tiempos = t_iso / t_tr,
                           dif_max_pct = max(dif[ok]), r_dif_max_m = r[ok][which.max(dif[ok])],
                           dif_min_pct = min(dif[ok]), en_250 = en(250), en_1000 = en(1000), en_2000 = en(2000), en_5800 = en(5800)))
}

# ---------------------------------------------------------------------
if (modulo == "b_m11_vcov") {
  # vcov(kppm) usa por defecto una aproximación rápida cuando la matriz de la cuadratura es muy grande
  f_ppm <- ppm(pu ~ xc + yc, covariates = COVS); ee_p <- sqrt(diag(vcov(f_ppm)))
  k <- kppm(pu ~ xc + yc, clusters = "Thomas", covariates = COVS, statargs = list(correction = "translate"))
  q <- quad.ppm(k$po); nU <- npoints(q$data) + npoints(q$dummy)
  v_def <- vcov(k, verbose = FALSE); v_exa <- vcov(k, fast = FALSE, verbose = FALSE); v_fast <- vcov(k, fast = TRUE, verbose = FALSE)
  e_def <- sqrt(diag(v_def)); e_exa <- sqrt(diag(v_exa))
  guarda("m11b_vcov", list(nU = nU, maxmatrix = spatstat.options("maxmatrix"), fast_por_defecto = nU^2 > spatstat.options("maxmatrix"), defecto_igual_fast_TRUE = isTRUE(all.equal(v_def, v_fast)),
                           efecto_defecto = (e_def[2] / ee_p[2])^2, n_efectivo_defecto = N_URB / (e_def[2] / ee_p[2])^2,
                           efecto_exacto = (e_exa[2] / ee_p[2])^2, n_efectivo_exacto = N_URB / (e_exa[2] / ee_p[2])^2,
                           cociente_ee_exacto_defecto = e_exa[2] / e_def[2]))
}

# ---------------------------------------------------------------------
if (modulo == "b_m11_hawkes") {
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
  disp <- function(x, k, Tm = 4000) { cnt <- tabulate(findInterval(x, seq(0, Tm, length.out = k + 1), rightmost.closed = TRUE), nbins = k); var(cnt) / mean(cnt) }
  ev <- hawkes(0.5, 0.8, 1.4, 4000, 5030)
  set.seed(5031); evp <- sort(runif(length(ev), 0, 4000))
  ks <- c(20, 50, 100, 200, 400, 800, 2000)
  por_k <- lapply(ks, function(k) list(k = k, ancho = 4000 / k, hawkes = disp(ev, k), poisson = disp(evp, k)))
  res <- sapply(seq_len(nsim_o(200)), function(s) { e <- hawkes(0.5, 0.8, 1.4, 4000, 6000 + s); c(n = length(e), d = disp(e, 200)) })
  tasa_teo <- 0.5 / (1 - 0.8 / 1.4)
  guarda("m11b_hawkes", list(por_intervalos = por_k, replicas = ncol(res),
                             disp_media = mean(res["d", ]), disp_sd = sd(res["d", ]), disp_min = min(res["d", ]), disp_max = max(res["d", ]),
                             tasa_media = mean(res["n", ]) / 4000, tasa_sd_una = sd(res["n", ]) / 4000,
                             z_tasa_simulada = (length(ev) / 4000 - tasa_teo) / (sd(res["n", ]) / 4000)))
}

# ---------------------------------------------------------------------
if (modulo == "b_m11_dups") {
  key <- paste(pu$x, pu$y); t <- table(key); nn <- nndist(pu); lam <- N_URB / A_URB
  f_centr <- ppm(pu ~ xc + yc, covariates = COVS)
  set.seed(8128)
  sims <- quieto(simulate(f_centr, nsim = nsim_o(99), progress = FALSE))
  pct_mod <- sapply(sims, function(s) 100 * mean(nndist(s) < 100))
  guarda("m11b_dups", list(n = N_URB, sitios_distintos = length(t), sedes_sobrantes = N_URB - length(t),
                           simulaciones_modelo = length(pct_mod), semilla_modelo = 8128,
                           pct_vecino_menos_100m_modelo = mean(pct_mod), pct_vecino_menos_100m_modelo_sd = sd(pct_mod),
                           sitios_con_repetidas = sum(t >= 2), sedes_en_esos_sitios = sum(t[t >= 2]),
                           sitios_de_2 = sum(t == 2), sitios_de_3 = sum(t == 3),
                           pct_vecino_menos_100m = 100 * mean(nn < 100), pct_vecino_menos_100m_csr = 100 * (1 - exp(-lam * pi * 100^2))))
}

# ---------------------------------------------------------------------
if (modulo == "b_m11_trend") {
  # los kppm de la diapositiva 37 llevan tendencia (~ xc + yc): sus parámetros de grupo no son los de ~ 1
  res <- list()
  for (cor in c("translate", "iso")) {
    k <- kppm(pu ~ xc + yc, clusters = "Thomas", covariates = COVS, statargs = list(correction = cor))
    res[[cor]] <- list(kappa = unname(k$clustpar[["kappa"]]), scale = unname(k$clustpar[["scale"]]))
  }
  guarda("m11b_trend", res)
}

# ---------------------------------------------------------------------
if (modulo == "b_m11_valle") {
  # ¿Es casi plano el valle del contraste mínimo de Thomas? Se evalúa el objetivo de `kppm` (p = 2, q = 0.25)
  # en los parámetros de cada ajuste y se calcula su perfil en sigma.
  lam <- N_URB / A_URB
  Ktr <- Kest(pu, correction = "translate"); Kiso <- Kest(pu, correction = "isotropic")
  kt <- kppm(pu ~ 1, "Thomas", statargs = list(correction = "translate"))
  mc <- kt$Fit$mcfit
  r <- Ktr$r; q <- mc$ctrl$q; p <- mc$ctrl$p
  rmin <- if (is.null(mc$ctrl$rmin)) 0 else mc$ctrl$rmin; rmax <- if (is.null(mc$ctrl$rmax)) max(r) else mc$ctrl$rmax
  sel <- r >= rmin & r <= rmax
  ki <- approx(Kiso$r, Kiso$iso, xout = r)$y; kt_emp <- Ktr$trans
  Kth <- function(par, r) pi * r^2 + (1 - exp(-r^2 / (4 * par[2]^2))) / par[1]
  obj <- function(par, Kemp) { a <- Kemp[sel]; b <- Kth(par, r[sel]); sum(abs(a^q - b^q)^p) }
  par_tr <- c(kappa = kt$clustpar[["kappa"]], sigma = kt$clustpar[["scale"]])
  opt_para <- function(Kemp, ini) optim(log(ini), function(th) obj(exp(th), Kemp), method = "Nelder-Mead", control = list(reltol = 1e-12, maxit = 5000))
  ti <- thomas.estK(Kiso, lambda = lam); par_iso0 <- c(kappa = ti$clustpar[["kappa"]], sigma = ti$clustpar[["scale"]])
  o_tr <- opt_para(kt_emp, par_tr); o_iso <- opt_para(ki, par_iso0)
  p_tr <- exp(o_tr$par); p_iso <- exp(o_iso$par)
  perfil <- function(Kemp, sg) optimize(function(lk) obj(c(exp(lk), sg), Kemp), c(log(1e-9), log(1e-4)), tol = 1e-12)$objective
  guarda("m11b_valle", list(
    q = q, p = p, rmax = rmax,
    objetivo_propio_sobre_spatstat = obj(par_tr, kt_emp) / mc$opt$value,
    traslacion = list(kappa = p_tr[[1]], sigma = p_tr[[2]], Q = o_tr$value),
    isotropica = list(kappa = p_iso[[1]], sigma = p_iso[[2]], Q = o_iso$value),
    kappa_sigma2_traslacion = p_tr[[1]] * p_tr[[2]]^2, kappa_sigma2_isotropica = p_iso[[1]] * p_iso[[2]]^2,
    cociente_kappa = p_iso[[1]] / p_tr[[1]],
    cruzada_traslacion_en_par_iso_pct = 100 * (obj(p_iso, kt_emp) / o_tr$value - 1),
    cruzada_isotropica_en_par_trasl_pct = 100 * (obj(p_tr, ki) / o_iso$value - 1),
    perfil_traslacion_sigma_isotropico_pct = 100 * (perfil(kt_emp, p_iso[[2]]) / o_tr$value - 1),
    perfil_isotropica_sigma_traslacion_pct = 100 * (perfil(ki, p_tr[[2]]) / o_iso$value - 1)))
}

# ---------------------------------------------------------------------
if (modulo == "b_ayuda") {
  # fichas de ayuda de las que cuelgan afirmaciones de las notas (se citan con `E(...)` en el registro)
  ayuda_txt <- function(tema, paquete) {
    h <- utils:::.getHelpFile(eval(bquote(help(.(tema), package = .(paquete)))))
    paste(capture.output(tools::Rd2txt(h, options = list(underline_titles = FALSE))), collapse = "\n")
  }
  guarda("ayuda_b", list(redwood = ayuda_txt("redwood", "spatstat.data"), kppm = ayuda_txt("kppm", "spatstat.model"),
                         rhohat = ayuda_txt("rhohat.ppp", "spatstat.explore"), vcov_kppm = ayuda_txt("vcov.kppm", "spatstat.model")))
}

OUT$meta <- list(modulo = sufijo, fecha = format(Sys.Date()), R = R.version.string,
                 segundos_totales = as.numeric(difftime(Sys.time(), meta_t0, units = "secs")),
                 spatstat = as.character(packageVersion("spatstat")), spatstat.explore = as.character(packageVersion("spatstat.explore")),
                 spatstat.model = as.character(packageVersion("spatstat.model")))
write(toJSON(OUT, auto_unbox = TRUE, digits = NA, pretty = TRUE, null = "null", na = "null"), SALIDA)
cat("escrito", SALIDA, sprintf("(%.0f s)\n", OUT$meta$segundos_totales))
