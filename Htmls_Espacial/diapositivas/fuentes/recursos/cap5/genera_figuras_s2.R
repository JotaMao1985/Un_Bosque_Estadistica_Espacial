# =====================================================================
# genera_figuras_s2.R — figuras de la sesión 2 (módulos 7 a 11) del cap. 5
# Desde la raíz del repo:
#   precalculo/rscript.sh Htmls_Espacial/diapositivas/fuentes/recursos/cap5/genera_figuras_s2.R          # todas
#   precalculo/rscript.sh …/genera_figuras_s2.R bei rhohat                                               # algunas
# Mismo código y mismos parámetros que los bloques del capítulo: cada cifra
# que aparece en una figura sale de la misma llamada (semilla 2026, orden de
# las llamadas a `rhohat`, nd por defecto…) y cada una se compara con lo que
# publica el capítulo antes de dibujar (`stopifnot`).
# =====================================================================
source("Htmls_Espacial/diapositivas/fuentes/recursos/cap5/figuras_comunes.R")
options(scipen = 999, warn = 1); set.seed(2026)
SAL <- "Htmls_Espacial/diapositivas/fuentes/recursos/cap5/"
ARGS <- commandArgs(trailingOnly = TRUE)
quiero <- function(f) length(ARGS) == 0 || f %in% ARGS
FUEN <- "Htmls_Espacial/diapositivas/fuentes/"
leej <- function(f) jsonlite::fromJSON(paste0(FUEN, f), simplifyVector = TRUE)

cole  <- st_read("datos/procesado/bogota_colegios.gpkg", quiet = TRUE)
v_urb <- st_read("datos/procesado/bogota_ventana_urbana.gpkg", quiet = TRUE)
xy <- st_coordinates(cole)
sf_urb <- st_union(st_geometry(v_urb))
WU <- as.owin(sf_urb)
pu <- suppressWarnings(ppp(xy[, 1], xy[, 2], window = WU))
stopifnot(npoints(pu) == 2107)
bb <- st_bbox(sf_urb)

# Las figuras se proyectan a 600-1000 px de ancho: con res = 250 en vez de 200 la letra (en puntos) ocupa
# un 25 % más de la figura y se lee desde el fondo del aula.
RES <- 250
abre <- function(archivo, ancho_px, alto_px) abre_png(archivo, ancho_px, alto_px, res = RES)

PAL_TERRENO <- c("#eef5f2", "#c3dfd3", "#8cc8b0", "#3f9a7a", "#1a7358", "#0b4a38")
COL_AZUL <- "#56B4E9"

# Ejes de línea con el estilo de las figuras de la sesión 1
ejes <- function(x_at = NULL, y_at = NULL, x_lab = NULL, y_lab = NULL, cex = 1.06) {
  if (!is.null(x_at)) axis(1, at = x_at, labels = if (is.null(x_lab)) TRUE else x_lab, col = COL_GRIS, col.axis = COL_TEXTO, cex.axis = cex, lwd = 0, lwd.ticks = 1)
  if (!is.null(y_at)) axis(2, at = y_at, labels = if (is.null(y_lab)) TRUE else y_lab, las = 1, col = COL_GRIS, col.axis = COL_TEXTO, cex.axis = cex, lwd = 0, lwd.ticks = 1)
}

# ---------------------------------------------------------------------
# S2-A · bei: los 3 604 árboles sobre la elevación (el norte, arriba)
# ---------------------------------------------------------------------
data(bei)
E <- bei.extra$elev
stopifnot(npoints(bei) == 3604)
if (quiero("bei")) {
  mc <- mapa_color(PAL_TERRENO, range(E))
  abre(paste0(SAL, "s2-bei-mapa.png"), 2200, 1520)
  layout(matrix(1:2, 2), heights = c(1, 0.27)); par(mar = c(0.3, 0.3, 4.2, 0.3))
  plot(NA, xlim = c(-12, 1062), ylim = c(-62, 512), asp = 1, axes = FALSE, xlab = "", ylab = "")
  plot(E, col = mc$cmap, main = "", ribbon = FALSE, axes = FALSE, box = FALSE, add = TRUE)
  plot(Window(bei), add = TRUE, border = COL_TEXTO, lwd = 1.6)
  points(bei$x, bei$y, pch = 16, cex = 0.47, col = adjustcolor(COL_NARANJA, 0.85))
  titulo_panel("3 604 árboles sobre la elevación del terreno", NULL, cex1 = 1.5)
  barra_escala(10, -52, 100, "100 m", cex = 1.3)
  points(330, -52, pch = 16, cex = 1.7, col = COL_NARANJA); text(352, -52, "un árbol", adj = 0, cex = 1.3, col = COL_TEXTO)
  norte(1040, 250, 120)
  barra_color(mc, "elevación (m sobre el nivel del mar)", c(120, 130, 140, 150, 159.48), c("120", "130", "140", "150", "159"), cex = 1.3, mar = c(3.4, 5, 2.4, 5))
  dev.off()
  cat("S2-A bei: elevación", round(range(E), 2), "\n")
}

# ---------------------------------------------------------------------
# S2-B · rhohat: dónde está el máximo y el mínimo de la curva, y dónde hay datos
#   Mismo orden de llamadas y misma semilla que el bloque del módulo 7.
# ---------------------------------------------------------------------
if (quiero("rhohat")) {
  set.seed(2026)
  rango <- function(p, cov) {
    rh <- rhohat(p, cov)
    ok <- is.finite(rh$rho)
    x <- rh[[1]][ok]; y <- rh$rho[ok]
    vp <- if (is.function(cov)) cov(p$x, p$y) else cov[p]
    q <- quantile(vp, c(0.05, 0.95))
    b <- x >= q[1] & x <= q[2]
    list(rh = rh, ok = ok, x = x, y = y, vp = vp, q = q, b = b,
         total = max(y) / min(y), bulto = max(y[b]) / min(y[b]))
  }
  r_e <- rango(bei, bei.extra$elev)
  r_g <- rango(bei, bei.extra$grad)
  centro <- ppp(mean(pu$x), mean(pu$y), window = WU)
  r_b <- rango(pu, distfun(centro))
  chk <- c(signif(r_e$total, 6), signif(r_e$bulto, 6), signif(r_g$total, 6), signif(r_g$bulto, 6), signif(r_b$total, 6), signif(r_b$bulto, 6))
  stopifnot(all(abs(chk - c(21.1346, 2.35639, 8.37795, 3.34267, 36.0759, 1.58183)) < 1e-9))
  cat("S2-B rhohat:", chk, "\n")

  panel <- function(r, esc_x, esc_y, xlab, ylab, titulo, ejes_x, fmt_x) {
    x <- r$x * esc_x; y <- r$y * esc_y
    hi <- r$rh$hi[r$ok] * esc_y; lo <- pmax(r$rh$lo[r$ok] * esc_y, 0)
    ymax <- max(y) * 1.25
    plot(NA, xlim = range(x), ylim = c(0, ymax), axes = FALSE, xlab = "", ylab = "")
    # el bulto: entre los percentiles 5 y 95 de la covariable en los puntos
    rect(r$q[1] * esc_x, 0, r$q[2] * esc_x, ymax, col = adjustcolor(COL_VERDE, 0.09), border = NA)
    polygon(c(x, rev(x)), c(pmin(hi, ymax), rev(lo)), col = adjustcolor(COL_GRIS, 0.35), border = NA)
    lines(x, y, lwd = 7, col = "#1a7358")
    i_max <- which.max(y); i_min <- which.min(y)
    points(x[c(i_max, i_min)], y[c(i_max, i_min)], pch = 21, bg = COL_NARANJA, col = "white", cex = 2.1, lwd = 3)
    # máximo y mínimo del bulto
    xb <- x[r$b]; yb <- y[r$b]
    points(xb[c(which.max(yb), which.min(yb))], yb[c(which.max(yb), which.min(yb))], pch = 21, bg = COL_VERDE, col = "white", cex = 1.8, lwd = 3)
    rug(r$vp * esc_x, side = 1, col = adjustcolor(COL_NARANJA, 0.35), ticksize = 0.05, lwd = 1.5)
    ejes(x_at = ejes_x, x_lab = fmt_x(ejes_x), cex = 1.45)
    axis(2, las = 1, col = COL_GRIS, col.axis = COL_TEXTO, cex.axis = 1.45, lwd = 0, lwd.ticks = 1.5)
    mtext(xlab, side = 1, line = 3.3, cex = 1.45, col = COL_TEXTO)
    mtext(ylab, side = 2, line = 3.5, cex = 1.4, col = COL_TEXTO)
    mtext(titulo, side = 3, line = 3.3, cex = 1.55, font = 2, col = COL_TEXTO)
    mtext(sprintf("razón total: %.1f", r$total), side = 3, line = 1.9, cex = 1.35, col = "#8A3D00", font = 2)
    mtext(sprintf("razón del bulto: %.2f", r$bulto), side = 3, line = 0.4, cex = 1.35, col = "#8A3D00", font = 2)
  }
  abre(paste0(SAL, "s2-rhohat-tres.png"), 3300, 1250)
  layout(matrix(1:3, 1)); par(cex = 1, mar = c(4.4, 5.0, 5.0, 0.5))
  panel(r_e, 1, 1e4, "elevación (m)", "árboles por hectárea",
        "bei · elevación", c(120, 130, 140, 150, 160), as.character)
  panel(r_g, 1, 1e4, "pendiente (gradiente)", "árboles por hectárea",
        "bei · pendiente", c(0, 0.1, 0.2, 0.3), as.character)
  panel(r_b, 1 / 1000, 1e6, "distancia al centro (km)", "sedes por km²",
        "Bogotá · distancia", c(0, 5, 10, 15, 20), as.character)
  dev.off()
  # lo que se dice en la diapositiva
  cat(sprintf("   bei elev: bulto [%.2f, %.2f] m · rho máx %.2f / mín %.2f árboles/ha\n", r_e$q[1], r_e$q[2], max(r_e$y) * 1e4, min(r_e$y) * 1e4))
  cat(sprintf("   Bogotá: bulto [%.1f, %.1f] m · rho máx %.2f / mín %.2f sedes/km2 · rango curva [%.0f, %.0f] m\n", r_b$q[1], r_b$q[2], max(r_b$y) * 1e6, min(r_b$y) * 1e6, min(r_b$x), max(r_b$x)))
  cat(sprintf("   Bogotá: puntos fuera del bulto: %.1f %% (esperado 10 %%)\n", 100 * mean(r_b$vp < r_b$q[1] | r_b$vp > r_b$q[2])))
}

# ---------------------------------------------------------------------
# S2-C · la cuadratura por defecto de ppm: teselas que tocan la ciudad y se quedan sin ningún punto
#   Mismo cálculo que el módulo 8 (`ppm(pu ~ 1, forcefit = TRUE)`, nd = 100 por defecto).
# ---------------------------------------------------------------------
if (quiero("teselas")) {
  f0q <- ppm(pu ~ 1, forcefit = TRUE)
  Q <- quad.ppm(f0q)
  pw <- Q$param$weight; nt <- pw$ntile; ar <- pw$areas
  U <- union.quad(Q)
  id <- gridindex(U$x, U$y, WU$xrange, WU$yrange, nt[1], nt[2])$index
  vac <- setdiff(which(ar > 0), unique(id))
  dx <- diff(WU$xrange) / nt[1]; dy <- diff(WU$yrange) / nt[2]
  stopifnot(sum(ar > 0) == 4345, length(vac) == 201, abs(sum(ar[vac]) / 1e6 - 1.22418) < 5e-6, npoints(Q$dummy) == 4140)
  x0 <- WU$xrange[1]; y0 <- WU$yrange[1]
  teselas_vac <- lapply(vac, function(k) {
    ix <- (k - 1) %% nt[1] + 1; iy <- (k - 1) %/% nt[1] + 1
    suppressWarnings(intersect.owin(WU, owin(x0 + c(ix - 1, ix) * dx, y0 + c(iy - 1, iy) * dy)))
  })
  ROJO <- "#C2410C"
  # el tramo ampliado: 8 teselas de ancho y 4 de alto, con la tesela vacía (93, 84) en un borde recto
  cx <- 93; cy <- 84
  stopifnot(((cy - 1) * nt[1] + cx) %in% vac)
  zx <- x0 + c(cx - 4, cx + 4) * dx; zy <- y0 + c(cy - 3, cy + 1) * dy
  abre(paste0(SAL, "s2-teselas.png"), 2500, 1500)
  layout(matrix(c(1, 2, 3, 3), 2, byrow = TRUE), widths = c(0.78, 1.22), heights = c(1, 0.13)); par(cex = 1, mar = c(0.4, 0.4, 4.6, 0.4))
  plot(WU, main = "", col = "#F1F5F9", border = COL_TEXTO, lwd = 1.2)
  for (w in teselas_vac) plot(w, add = TRUE, col = ROJO, border = ROJO, lwd = 2.6)
  rect(zx[1], zy[1], zx[2], zy[2], border = COL_VERDE, lwd = 3.6)
  ndc <- c(grconvertX(zx[2], "user", "ndc"), grconvertY(zy[2], "user", "ndc"), grconvertY(zy[1], "user", "ndc"))
  mtext("201 teselas vacías", side = 3, line = 2.4, cex = 1.65, font = 2, col = COL_TEXTO)
  mtext("de 4 345 que tocan la ciudad", side = 3, line = 0.5, cex = 1.45, col = COL_TEXTO)
  norte(bb["xmin"] + 1500, bb["ymax"] - 5200, 2600); barra_escala(bb["xmin"] + 900, bb["ymin"] + 1700, 5000, "5 km", cex = 1.5)
  par(mar = c(0.4, 0.4, 4.6, 0.4))
  plot(NA, xlim = zx, ylim = zy, asp = 1, axes = FALSE, xlab = "", ylab = "", xaxs = "i", yaxs = "i")
  plot(WU, add = TRUE, col = "#F8FAFC", border = NA)
  for (w in teselas_vac) plot(w, add = TRUE, col = adjustcolor(ROJO, 0.9), border = NA)
  segments(x0 + ((cx - 4):(cx + 4)) * dx, zy[1], x0 + ((cx - 4):(cx + 4)) * dx, zy[2], col = COL_GRIS, lwd = 1.4)
  segments(zx[1], y0 + ((cy - 3):(cy + 1)) * dy, zx[2], y0 + ((cy - 3):(cy + 1)) * dy, col = COL_GRIS, lwd = 1.4)
  plot(WU, add = TRUE, border = COL_TEXTO, lwd = 3.2)
  en_z <- function(P) P$x >= zx[1] & P$x <= zx[2] & P$y >= zy[1] & P$y <= zy[2]
  d <- Q$dummy; s <- Q$data
  points(d$x[en_z(d)], d$y[en_z(d)], pch = 16, cex = 1.3, col = COL_AZUL)
  points(s$x[en_z(s)], s$y[en_z(s)], pch = 21, cex = 1.8, bg = COL_NARANJA, col = "white", lwd = 1.6)
  rect(zx[1], zy[1], zx[2], zy[2], border = COL_VERDE, lwd = 4)
  mtext("Un tramo del borde, ampliado", side = 3, line = 2.4, cex = 1.65, font = 2, col = COL_TEXTO)
  mtext("cada tesela mide 235 × 400 m", side = 3, line = 0.5, cex = 1.45, col = COL_TEXTO)
  rojo_tes <- teselas_vac[[match((cy - 1) * nt[1] + cx, vac)]]
  cr <- c(mean(rojo_tes$xrange), mean(rojo_tes$yrange))
  arrows(cr[1] + 180, cr[2] + 480, cr[1] + 20, cr[2] + 60, length = 0.12, lwd = 3.2, col = ROJO)
  text(cr[1] + 200, cr[2] + 560, "tesela vacía:\nsin ningún punto", adj = c(0, 0.5), cex = 1.5, font = 2, col = ROJO)
  barra_escala(zx[1] + 100, zy[2] - 230, 500, "500 m", cex = 1.4)
  # las dos rectas que unen el recuadro de la ciudad con su ampliación
  par(xpd = NA)
  segments(grconvertX(ndc[1], "ndc", "user"), grconvertY(ndc[2], "ndc", "user"), zx[1], zy[2], col = COL_VERDE, lwd = 2.6, lty = 3)
  segments(grconvertX(ndc[1], "ndc", "user"), grconvertY(ndc[3], "ndc", "user"), zx[1], zy[1], col = COL_VERDE, lwd = 2.6, lty = 3)
  par(xpd = FALSE, mar = c(0.2, 0.5, 0.2, 0.5)); plot.new()
  legend("center", ncol = 3, bty = "n", cex = 1.5, text.col = COL_TEXTO, x.intersp = 0.8,
         pch = c(21, 16, 15), pt.cex = c(2.0, 1.6, 2.4), col = c("white", COL_AZUL, ROJO), pt.bg = c(COL_NARANJA, NA, NA),
         legend = c("sede", "punto ficticio", "tesela sin punto"))
  dev.off()
  i <- which.max(sapply(teselas_vac, area.owin))
  cat(sprintf("S2-C teselas: %d vacías de %d · área sin contar %.5f km2 · mayor tesela vacía %.0f m2 (de %.0f)\n",
              length(vac), sum(ar > 0), sum(ar[vac]) / 1e6, area.owin(teselas_vac[[i]]), dx * dy))
}

# ---------------------------------------------------------------------
# S2-D · la K inhomogénea del patrón contra la banda de su propio modelo (999 simulaciones)
#   Datos: precalculo/salidas/cap5_envolvente.csv, el mismo archivo que lee el bloque de Python del capítulo.
# ---------------------------------------------------------------------
if (quiero("envolvente")) {
  env <- read.csv("precalculo/salidas/cap5_envolvente.csv")
  ok <- env$r > 0
  fuera <- env$obs > env$hi | env$obs < env$lo
  stopifnot(nrow(env) == 101, sum(ok) == 100, round(100 * mean(fuera[ok])) == 62, all(env$obs[ok][fuera[ok]] > env$hi[ok][fuera[ok]]))
  r_ini <- min(env$r[ok][fuera[ok]]); r_fin <- max(env$r[ok][fuera[ok]])
  stopifnot(abs(r_ini - 58.68116) < 1e-4, abs(r_fin - 3638.23175) < 1e-4)
  x <- env$r[ok]; o <- env$obs[ok] / env$mmean[ok]; lo <- env$lo[ok] / env$mmean[ok]; hi <- env$hi[ok] / env$mmean[ok]
  fu <- fuera[ok]
  abre(paste0(SAL, "s2-envolvente.png"), 2000, 1050)
  par(mar = c(5.2, 5.6, 4.4, 1.0))
  plot(NA, xlim = c(0, 5868.1157), ylim = c(0.4, 2.9), axes = FALSE, xlab = "", ylab = "", xaxs = "i")
  rect(r_ini, 0.4, r_fin, 2.9, col = adjustcolor(COL_NARANJA, 0.09), border = NA)
  polygon(c(x, rev(x)), c(hi, rev(lo)), col = adjustcolor(COL_GRIS, 0.55), border = NA)
  abline(h = 1, lty = 2, lwd = 3, col = COL_TEXTO)
  lines(x, o, lwd = 5, col = "#1a7358")
  points(x[fu], o[fu], pch = 21, bg = COL_NARANJA, col = "white", cex = 1.4, lwd = 1.2)
  ejes(x_at = seq(0, 6000, 1000), x_lab = c("0", "1", "2", "3", "4", "5", "6"), y_at = c(0.5, 1, 1.5, 2, 2.5), cex = 1.35)
  mtext("distancia r (km)", side = 1, line = 3.4, cex = 1.4, col = COL_TEXTO)
  mtext("K inhomogénea ÷ media del modelo", side = 2, line = 3.6, cex = 1.15, col = COL_TEXTO)
  mtext("Patrón de Bogotá contra su modelo (999 simulaciones)", side = 3, line = 2.3, cex = 1.5, font = 2, col = COL_TEXTO)
  mtext("62 de los 100 radios quedan sobre la banda; ninguno bajo ella", side = 3, line = 0.6, cex = 1.25, col = "#8A3D00", font = 2)
  text(1000, 0.62, "el modelo: la media\nde sus simulaciones = 1", adj = 0, cex = 1.25, col = COL_TEXTO)
  text(r_ini, 2.76, sprintf("empieza en %.1f m", r_ini), adj = c(0, 0.5), cex = 1.3, font = 2, col = "#8A3D00")
  text(r_fin, 2.76, sprintf("termina en %.0f m", r_fin), adj = c(1, 0.5), cex = 1.3, font = 2, col = "#8A3D00")
  legend("topright", bty = "n", cex = 1.2, text.col = COL_TEXTO, pch = c(NA, 15, 21), lty = c(1, NA, NA), lwd = c(5, NA, NA), pt.cex = c(NA, 2.6, 1.7),
         col = c("#1a7358", adjustcolor(COL_GRIS, 0.8), "white"), pt.bg = c(NA, NA, COL_NARANJA),
         legend = c("patrón observado", "banda de las 999 simulaciones", "radio fuera de la banda"), inset = c(0, 0.12))
  dev.off()
  cat(sprintf("S2-D envolvente: fuera %d/%d · inicio %.5f · fin %.5f · razón máxima obs/modelo %.2f en r = %.1f m\n", sum(fu), sum(ok), r_ini, r_fin, max(o), x[which.max(o)]))
}

# ---------------------------------------------------------------------
# S2-E · la escala del conglomerado según la K con que se estimó (tres modelos)
# ---------------------------------------------------------------------
if (quiero("escalas")) {
  th <- leej("recomputo_cap5_m11_Thomas.json")$m11_Thomas
  mc_ <- leej("recomputo_cap5_m11_MatClust.json")$m11_MatClust
  lg <- leej("recomputo_cap5_m11_LGCP.json")$m11_LGCP
  iso <- c(th$iso$parametros$scale, mc_$iso$parametros$scale, lg$iso$parametros$scale)
  tra <- c(th$translate$parametros$scale, mc_$translate$parametros$scale, lg$translate$parametros$scale)
  stopifnot(all(round(iso) == c(932, 1782, 1296)), all(round(tra) == c(1320, 2522, 1927)))
  pct <- 100 * (tra / iso - 1)
  abre(paste0(SAL, "s2-escalas.png"), 2000, 1050)
  par(mar = c(4.2, 6.2, 4.6, 1.0))
  bp <- barplot(rbind(iso, tra), beside = TRUE, ylim = c(0, 4600), col = c(COL_AZUL, COL_NARANJA), border = NA, axes = FALSE, names.arg = rep("", 3), space = c(0, 0.6))
  ejes(y_at = seq(0, 3000, 1000), cex = 1.35)
  axis(1, at = colMeans(bp), labels = c("Thomas", "Matérn", "Cox log-gaussiano"), tick = FALSE, cex.axis = 1.45, col.axis = COL_TEXTO, font.axis = 2, line = 0.3)
  text(bp, rbind(iso, tra), labels = sprintf("%.0f m", rbind(iso, tra)), pos = 3, cex = 1.35, font = 2, col = COL_TEXTO, offset = 0.4)
  text(colMeans(bp), pmax(iso, tra) + 720, sprintf("+%.1f %%", pct), cex = 1.45, font = 2, col = "#8A3D00")
  mtext("escala (m)", side = 2, line = 4.3, cex = 1.4, col = COL_TEXTO)
  mtext("El mismo modelo, estimado dos veces", side = 3, line = 2.7, cex = 1.5, font = 2, col = COL_TEXTO)
  mtext("sobre las 2 107 sedes: solo cambia la estimación de K", side = 3, line = 1.0, cex = 1.25, col = COL_TEXTO)
  legend("top", ncol = 2, bty = "n", cex = 1.3, text.col = COL_TEXTO, pch = 15, pt.cex = 2.4, col = c(COL_AZUL, COL_NARANJA), legend = c("K isotrópica (defecto)", "K de traslación"))
  dev.off()
  cat("S2-E escalas:", round(iso, 1), "|", round(tra, 1), "| %:", round(pct, 2), "\n")
}

# ---------------------------------------------------------------------
# S2-F · la K de Thomas con los dos juegos de parámetros: casi la misma curva
#   Mismos parámetros que el bloque de Python del módulo 11.
# ---------------------------------------------------------------------
if (quiero("thomas")) {
  k_thomas <- function(r, kappa, escala) pi * r^2 + (1 - exp(-r^2 / (4 * escala^2))) / kappa
  pa <- c(2.108e-07, 932.1338909648); pb <- c(1.091e-07, 1319.7032545453)
  dif <- sapply(c(500, 1000, 2000), function(r) 100 * abs(k_thomas(r, pb[1], pb[2]) - k_thomas(r, pa[1], pa[2])) / k_thomas(r, pa[1], pa[2]))
  stopifnot(all(round(dif, 1) == c(0.6, 0.9, 4.8)))
  r <- seq(20, 3000, length.out = 600)
  ka <- k_thomas(r, pa[1], pa[2]) / (pi * r^2); kb <- k_thomas(r, pb[1], pb[2]) / (pi * r^2)
  abre(paste0(SAL, "s2-thomas-valle.png"), 2000, 1000)
  par(mar = c(4.2, 4.8, 3.2, 0.8))
  plot(NA, xlim = c(0, 3000), ylim = c(1, 1.5), axes = FALSE, xlab = "", ylab = "", xaxs = "i")
  abline(v = c(500, 1000, 2000), lty = 3, lwd = 2.4, col = COL_GRIS)
  abline(h = 1, lty = 2, lwd = 3, col = COL_TEXTO)
  lines(r, ka, lwd = 6, col = COL_AZUL); lines(r, kb, lwd = 6, col = COL_NARANJA, lty = 2)
  ejes(x_at = seq(0, 3000, 500), x_lab = c("0", "0.5", "1", "1.5", "2", "2.5", "3"), y_at = c(1, 1.1, 1.2, 1.3, 1.4, 1.5), cex = 1.4)
  mtext("distancia r (km)", side = 1, line = 3.0, cex = 1.4, col = COL_TEXTO)
  mtext("K(r) ÷ πr²", side = 2, line = 3.1, cex = 1.4, col = COL_TEXTO)
  mtext("K de Thomas con los parámetros de cada corrección", side = 3, line = 1.1, cex = 1.45, font = 2, col = COL_TEXTO)
  text(c(500, 1000, 2000) + 40, 1.475, sprintf("%.1f %%", dif), adj = c(0, 0.5), cex = 1.5, font = 2, col = "#8A3D00")
  text(3000, 1.0, "1 = sin conglomerado", adj = c(1, -0.7), cex = 1.3, col = COL_TEXTO)
  legend("bottomleft", bty = "n", cex = 1.3, text.col = COL_TEXTO, lwd = 6, lty = c(1, 2), col = c(COL_AZUL, COL_NARANJA), inset = c(0.01, 0.1),
         legend = c("isotrópica: κ = 2.108e-07, σ = 932 m", "traslación: κ = 1.091e-07, σ = 1320 m"))
  dev.off()
  cat("S2-F thomas:", round(dif, 2), "\n")
}

# ---------------------------------------------------------------------
# S2-G · Hawkes contra Poisson de la misma tasa media (el CSV del capítulo)
# ---------------------------------------------------------------------
if (quiero("hawkes")) {
  h <- read.csv("precalculo/salidas/cap5_hawkes.csv")
  th_ <- h$t[h$proceso == "hawkes"]; tp_ <- h$t[h$proceso == "poisson"]
  cnt <- function(t, tmax = 4000, k = 200) as.numeric(table(cut(t, breaks = seq(0, tmax, length.out = k + 1), include.lowest = TRUE)))
  ch_ <- cnt(th_); cp_ <- cnt(tp_)
  dh <- var(ch_) / mean(ch_); dp <- var(cp_) / mean(cp_)
  stopifnot(length(th_) == 4577, length(tp_) == 4577, abs(dh - 5.1545371603) < 1e-8, abs(dp - 0.9578930264) < 1e-8)
  ymax <- max(c(ch_, cp_)) * 1.08
  abre(paste0(SAL, "s2-hawkes.png"), 1900, 950)
  layout(matrix(1:2, 1)); par(cex = 1, mar = c(4.6, 4.6, 3.0, 1.2))
  for (k in 1:2) {
    col <- if (k == 1) COL_NARANJA else COL_AZUL; cc <- if (k == 1) ch_ else cp_
    plot(NA, xlim = c(0, 4000), ylim = c(0, ymax), axes = FALSE, xlab = "", ylab = "", xaxs = "i")
    rect(seq(0, 3980, 20), 0, seq(20, 4000, 20), cc, col = col, border = NA)
    axis(1, at = seq(0, 4000, 2000), col = COL_GRIS, col.axis = COL_TEXTO, cex.axis = 1.4, lwd = 0, lwd.ticks = 1)
    axis(2, at = seq(0, 60, 20), las = 1, col = COL_GRIS, col.axis = COL_TEXTO, cex.axis = 1.4, lwd = 0, lwd.ticks = 1)
    abline(h = mean(cc), lty = 2, lwd = 3, col = COL_TEXTO)
    mtext(sprintf("%s: dispersión %.2f", if (k == 1) "Hawkes" else "Poisson", if (k == 1) dh else dp), side = 3, line = 0.7, cex = 1.4, font = 2, col = if (k == 1) "#8A3D00" else "#075985")
    mtext("tiempo (barras de 20 unidades)", side = 1, line = 3.1, cex = 1.15, col = COL_TEXTO)
    if (k == 1) mtext("eventos por intervalo", side = 2, line = 2.9, cex = 1.1, col = COL_TEXTO)
  }
  dev.off()
  cat(sprintf("S2-G hawkes: dispersión %.5f y %.5f · máximos por intervalo %d y %d · media %.2f\n", dh, dp, max(ch_), max(cp_), mean(ch_)))
}
