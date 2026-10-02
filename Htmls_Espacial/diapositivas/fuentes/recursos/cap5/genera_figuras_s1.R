# =====================================================================
# genera_figuras_s1.R — figuras de la sesión 1 (módulos 1 a 6) del cap. 5
# Desde la raíz del repo:
#   precalculo/rscript.sh Htmls_Espacial/diapositivas/fuentes/recursos/cap5/genera_figuras_s1.R
# Mismo código y mismos parámetros que los bloques del capítulo: cada cifra
# que aparece en una figura sale de la misma llamada (σ, dimyx, diggle…).
# =====================================================================
source("Htmls_Espacial/diapositivas/fuentes/recursos/cap5/figuras_comunes.R")
options(scipen = 999, warn = 1); set.seed(2026)
SAL <- "Htmls_Espacial/diapositivas/fuentes/recursos/cap5/"
# Legibilidad proyectada: las figuras se ven a 240-440 px de alto en una diapositiva de 720, o sea a una escala de
# 0.25-0.4 de su lienzo. Con la letra a cex ~1.3 y res = 200, la letra de la diapositiva mide ~9-11 px (y menos aún con
# `layout()`, que baja el cex base a 0.83 con 2 x 2 y a 0.66 con tres columnas). Achicar el lienzo Z veces deja la letra
# Z veces mayor respecto de la figura, y la figura se muestra con el mismo `alto`: el objetivo es ~15-16 px de letra.
ZOOM <- c("s1-kennedy" = 1.35, "s1-sigma-tres" = 1.3, "s1-borde-tres" = 1.4, "s1-bwppl-criterio" = 1.2, "s1-oferta-estudiantes" = 1.25,
          "s1-chorley" = 1.25, "s1-oficial-mapa-puntos" = 1.3, "s1-nucleos-cuatro" = 1.15, "s1-tres-capas" = 1.25)
abre_z <- function(nombre, ancho_px, alto_px) {
  z <- if (nombre %in% names(ZOOM)) ZOOM[[nombre]] else 1
  abre_png(paste0(SAL, nombre, ".png"), round(ancho_px / z), round(alto_px / z))
}
integra <- function(im) { v <- as.numeric(im$v); v <- v[is.finite(v)]; sum(v) * im$xstep * im$ystep }

cole <- st_read("datos/procesado/bogota_colegios.gpkg", quiet = TRUE)
loc  <- st_read("datos/procesado/bogota_localidades.gpkg", quiet = TRUE)
v_urb <- st_read("datos/procesado/bogota_ventana_urbana.gpkg", quiet = TRUE)
s11   <- st_read("datos/procesado/bogota_colegios_saber11.gpkg", quiet = TRUE)
xy <- st_coordinates(cole)
sf_ken <- st_union(st_geometry(loc[loc$localidad == "Kennedy", ]))
W  <- as.owin(sf_ken)
p  <- suppressWarnings(ppp(xy[, 1], xy[, 2], window = W))
sf_urb <- st_union(st_geometry(v_urb))
WU <- as.owin(sf_urb)
pu <- suppressWarnings(ppp(xy[, 1], xy[, 2], window = WU))
en <- inside.owin(xy[, 1], xy[, 2], WU)
c11 <- en & !is.na(s11$s11_n)
p11 <- suppressWarnings(ppp(st_coordinates(s11)[c11, 1], st_coordinates(s11)[c11, 2], window = WU))
stopifnot(npoints(p) == 262, npoints(pu) == 2107, npoints(p11) == 1062)
bb <- st_bbox(sf_urb); bk <- st_bbox(sf_ken)

# Localidades recortadas al perímetro urbano, para rotular
loc_u <- suppressWarnings(st_intersection(loc, sf_urb))
et_loc <- function(nombre) st_coordinates(st_point_on_surface(st_union(st_geometry(loc_u[loc_u$localidad == nombre, ]))))

# ---------------------------------------------------------------------
# F0 · ilustración de juguete: cada punto pone una loma; la suma es λ̂
# ---------------------------------------------------------------------
x_j <- c(1.2, 1.9, 2.3, 6.5, 7.9, 8.4)
xs <- seq(0, 10, length.out = 800)
loma <- function(x0, s) dnorm(xs, x0, s)
ymax_j <- 1.3 * max(sapply(c(0.35, 1.2), function(s) max(Reduce(`+`, lapply(x_j, loma, s = s)))))   # la MISMA escala vertical en los dos paneles
abre_z("s1-nucleo-juguete", 2100, 700)
layout(matrix(1:2, 1)); par(mar = c(3.6, 2.2, 3.6, 0.8))
for (s in c(0.35, 1.2)) {
  tot <- Reduce(`+`, lapply(x_j, loma, s = s))
  plot(NA, xlim = c(0, 10), ylim = c(0, ymax_j), axes = FALSE, xlab = "", ylab = "")
  for (x0 in x_j) lines(xs, loma(x0, s), col = "#FFAB5C", lwd = 2.4)
  lines(xs, tot, col = COL_VERDE, lwd = 4.5)
  points(x_j, rep(0, length(x_j)), pch = 16, col = COL_NARANJA, cex = 2.2)
  axis(1, at = 0:10, col = COL_GRIS, col.axis = COL_TEXTO, cex.axis = 1.3, lwd = 0, lwd.ticks = 1)
  mtext("posición u (una sola dimensión)", side = 1, line = 2.4, cex = 1.2, col = COL_TEXTO)
  mtext(if (s < 1) "σ = 0.35: casi cada punto hace su loma" else "σ = 1.2: las lomas se funden en dos",
        side = 3, line = 0.8, cex = 1.45, font = 2, col = COL_TEXTO)
  if (s < 1) legend(x = 3.1, y = ymax_j, bty = "n", cex = 1.05, text.col = COL_TEXTO, lwd = c(4.5, 2.4), col = c(COL_VERDE, "#FFAB5C"),
                    legend = c(expression(hat(lambda)(u) * ": la suma"), "un peso por punto"))
}
dev.off()

# ---------------------------------------------------------------------
# F1 · dónde está Kennedy (izquierda) y sus 262 sedes dentro de su contorno (derecha)
# ---------------------------------------------------------------------
abre_z("s1-kennedy", 2200, 1000)
layout(matrix(1:2, 1), widths = c(0.82, 1.18)); par(mar = c(0.4, 0.4, 3.2, 0.4))
plot(st_geometry(sf_urb), col = "#F1F5F9", border = COL_GRIS, lwd = 1.4)
plot(sf_ken, col = adjustcolor(COL_NARANJA, 0.38), border = COL_NARANJA, lwd = 2.6, add = TRUE)
ck <- st_coordinates(st_centroid(sf_ken))
text(ck[1], bk["ymin"] - 2300, "Kennedy", font = 2, cex = 1.8, col = "#8A3D00")
mtext("Perímetro urbano", side = 3, line = 0.5, cex = 1.45, font = 2, col = COL_TEXTO)
norte(bb["xmin"] + 1500, bb["ymax"] - 3200, 2800)
barra_escala(bb["xmin"] + 900, bb["ymin"] + 1800, 5000, "5 km")
plot(sf_ken, col = "#FFF7ED", border = COL_TEXTO, lwd = 2.4)
points(p$x, p$y, pch = 16, cex = 1, col = COL_NARANJA)
mtext("Las 262 sedes de Kennedy", side = 3, line = 0.5, cex = 1.45, font = 2, col = COL_TEXTO)
norte(bk["xmax"] - 350, bk["ymax"] - 800, 750)
barra_escala(bk["xmin"] + 120, bk["ymax"] - 500, 1000, "1 km")
dev.off()

# ---------------------------------------------------------------------
# F2 · el mismo patrón con tres anchos de banda, una sola escala de color
# ---------------------------------------------------------------------
sigs <- c(233.3949, 660.1404, 1867.1589)
dens <- lapply(sigs, function(s) density(p, sigma = s, dimyx = c(99, 96)) * 1e6)     # por km2
pico <- sapply(dens, max); cat("F2 picos:", round(pico, 4), "\n")
mc <- mapa_color(PAL_NARANJA, c(0, ceiling(max(pico) * 2) / 2 - 0.5 + 0.5))          # 0 a 29.5 -> 30 (borde del rango)
mc <- mapa_color(PAL_NARANJA, c(0, max(pico)))
abre_z("s1-sigma-tres", 2300, 1060)
layout(matrix(c(1, 2, 3, 4, 4, 4), 2, 3, byrow = TRUE), heights = c(1, 0.2)); par(mar = c(0.2, 0.2, 4.6, 0.2))
for (i in 1:3) { pinta_im(dens[[i]], mc, W); titulo_panel(sprintf("σ = %.0f m", sigs[i]), sprintf("máximo %.1f sedes por km²", pico[i])) }
barra_color(mc, "sedes por km² · la misma escala de color en los tres mapas", c(0, 5, 10, 15, 20, 25, 29.5), c("0", "5", "10", "15", "20", "25", "29.5"), cex = 1.3)
dev.off()

# ---------------------------------------------------------------------
# F3 · el abanico de los cuatro selectores en las dos ventanas (escala log)
# ---------------------------------------------------------------------
sel_k <- c(diggle = as.numeric(bw.diggle(p)), ppl = as.numeric(bw.ppl(p)), CvL = as.numeric(bw.CvL(p)), scott = as.numeric(bw.scott(p))[1])
sel_u <- c(diggle = as.numeric(bw.diggle(pu)), ppl = as.numeric(bw.ppl(pu)), CvL = as.numeric(bw.CvL(pu)), scott = as.numeric(bw.scott(pu))[1])
cat("F3 Kennedy:", round(sel_k, 1), " ciudad:", round(sel_u, 1), "\n")
nomb <- c(diggle = "bw.diggle", ppl = "bw.ppl", CvL = "bw.CvL", scott = "bw.scott")
col_sel <- c(diggle = "#1a7358", ppl = "#D55E00", CvL = "#0072B2", scott = "#8A3D00")
abre_z("s1-selectores", 2200, 800)
par(mar = c(4.2, 11.5, 2.4, 1.4))
plot(NA, xlim = c(200, 1500), ylim = c(0.35, 2.85), log = "x", axes = FALSE, xlab = "", ylab = "")
mtext("valores por defecto de cada selector · bw.scott: el ancho del eje x", side = 3, line = 0.4, cex = 1.3, col = COL_TEXTO)
axis(1, at = c(200, 300, 500, 700, 1000, 1500), col = COL_GRIS, col.axis = COL_TEXTO, cex.axis = 1.35, lwd = 0, lwd.ticks = 1)
mtext("ancho de banda σ elegido (metros, escala logarítmica)", side = 1, line = 2.9, cex = 1.35, col = COL_TEXTO)
mtext(c("Ciudad\n2 107 sedes", "Kennedy\n262 sedes"), side = 2, at = c(1, 2.3), las = 1, line = 0.8, cex = 1.4, col = COL_TEXTO, font = 2)
abline(h = c(1, 2.3), col = "#E2E8F0", lwd = 3)
for (k in 1:2) {
  v <- if (k == 1) sel_u else sel_k
  y0 <- c(1, 2.3)[k]
  segments(min(v), y0, max(v), y0, lwd = 7, col = "#CBD5E1")
  points(v, rep(y0, 4), pch = 21, bg = col_sel[names(v)], col = "white", cex = 3.6, lwd = 2)
  rk <- rank(v)                                    # etiquetas alternadas arriba / abajo
  arr <- rk %% 2 == 1
  text(v, y0 + ifelse(arr, 0.4, -0.4), sprintf("%s\n%.0f", nomb[names(v)], v), col = col_sel[names(v)], font = 2, cex = 1.2)
}
dev.off()

# ---------------------------------------------------------------------
# F4 · pico contra ancho de banda: el ancho decide cuánto vale el máximo
# ---------------------------------------------------------------------
anchos <- c(233.3949, 330.0702, 466.7897, 660.1404, 933.5795, 1320.2807, 1867.1589)
picos  <- sapply(anchos, function(s) max(density(p, sigma = s, dimyx = c(99, 96))) * 1e6)
cat("F4 picos:", round(picos, 4), " caida:", round(100 * (picos[1] - picos[7]) / picos[1], 4), "\n")
abre_z("s1-pico-sigma", 2000, 800)
par(mar = c(4.6, 5.2, 1, 1.4))
plot(NA, xlim = c(1, 7.25), ylim = c(0, 33), axes = FALSE, xlab = "", ylab = "")
axis(1, at = 1:7, labels = sprintf("%.0f m", anchos), col = COL_GRIS, col.axis = COL_TEXTO, cex.axis = 1.25, lwd = 0, lwd.ticks = 1)
axis(2, at = seq(0, 30, 10), las = 1, col = COL_GRIS, col.axis = COL_TEXTO, cex.axis = 1.3, lwd = 0, lwd.ticks = 1)
abline(h = seq(0, 30, 10), col = "#E2E8F0", lwd = 1.5)
mtext("ancho de banda σ", side = 1, line = 3.2, cex = 1.35, col = COL_TEXTO)
mtext("máximo (sedes por km²)", side = 2, line = 3.3, cex = 1.35, col = COL_TEXTO)
polygon(c(1:7, 7, 1), c(picos, 0, 0), col = adjustcolor(COL_VERDE, 0.10), border = NA)
lines(1:7, picos, lwd = 5, col = "#1a7358")
points(1:7, picos, pch = 21, bg = "white", col = "#1a7358", cex = 2.4, lwd = 3)
text(1:7, picos + 2.4, sprintf("%.1f", picos), cex = 1.35, font = 2, col = COL_TEXTO)
arrows(1, 30, 7, 30, length = 0.12, lwd = 2.4, col = COL_NARANJA, code = 3)
text(4.1, 32.2, "cada paso multiplica σ por √2; de 233 a 1867 m son ×8", cex = 1.25, col = "#8A3D00", font = 2)
dev.off()

# ---------------------------------------------------------------------
# F5 · las tres correcciones de borde a σ = 800 m: los mapas se ven casi igual
# ---------------------------------------------------------------------
s <- 800; d <- c(99, 96)
con <- density(p, sigma = s, dimyx = d) * 1e6
sin <- density(p, sigma = s, dimyx = d, edge = FALSE) * 1e6
dig <- density(p, sigma = s, dimyx = d, diggle = TRUE) * 1e6
m3 <- c(sin = integra(sin), def = integra(con), dig = integra(dig)) / 1e6
cat("F5 masas:", round(m3, 4), " % =", round(100 * (m3 / 262 - 1), 4), "\n")
zl <- c(0, max(max(con), max(sin), max(dig)))
mc <- mapa_color(PAL_NARANJA, zl)
abre_z("s1-borde-tres", 2300, 1060)
layout(matrix(c(1, 2, 3, 4, 4, 4), 2, 3, byrow = TRUE), heights = c(1, 0.2)); par(mar = c(0.2, 0.2, 4.6, 0.2))
# A = por defecto, B = sin corregir, C = diggle = TRUE (el orden no es el de la tabla a propósito: la clave va en la respuesta)
pinta_im(con, mc, W); titulo_panel("A", cex1 = 2.4)
pinta_im(sin, mc, W); titulo_panel("B", cex1 = 2.4)
pinta_im(dig, mc, W); titulo_panel("C", cex1 = 2.4)
barra_color(mc, "sedes por km² · σ = 800 m · misma escala en los tres mapas", c(0, 3, 6, 9, 12), cex = 1.3)
dev.off()

# ---------------------------------------------------------------------
# F6 · japanesepines: el patrón (65 pinos) y el criterio de bw.ppl que sigue subiendo
# ---------------------------------------------------------------------
jp <- japanesepines
bj <- bw.ppl(jp, srange = c(0.01, 2), warn = FALSE)
hh <- attr(bj, "h"); cv <- attr(bj, "cv")
cat("F6 japanesepines n =", npoints(jp), " optimo con srange a 2:", as.numeric(bj), " tope por defecto:", diameter(Window(jp)) / 2, "\n")
sel <- hh >= 0.08                                   # el tramo donde el criterio ya no se desploma
cat("F6 criterio: ", paste(sprintf("%.3f->%.2f", hh[sel], cv[sel]), collapse = "  "), "\n")
abre_z("s1-bwppl-criterio", 1500, 1000)
par(mar = c(4.8, 5.6, 5.0, 1.0))
yl <- range(cv[sel]) + c(-0.8, 1.9)
plot(NA, xlim = c(0.08, 2.1), ylim = yl, log = "x", axes = FALSE, xlab = "", ylab = "")
axis(1, at = c(0.1, 0.2, 0.5, 0.7071, 1, 2), labels = c("0.1", "0.2", "0.5", "0.7071", "1", "2"), col = COL_GRIS, col.axis = COL_TEXTO, cex.axis = 1.4, lwd = 0, lwd.ticks = 1)
axis(2, las = 1, col = COL_GRIS, col.axis = COL_TEXTO, cex.axis = 1.4, lwd = 0, lwd.ticks = 1)
mtext("ancho de banda σ (unidad = 5.7 m)", side = 1, line = 3.5, cex = 1.4, col = COL_TEXTO)
mtext("criterio de bw.ppl", side = 2, line = 3.6, cex = 1.4, col = COL_TEXTO)
lines(hh[sel], cv[sel], lwd = 5, col = "#1a7358"); points(hh[sel], cv[sel], pch = 21, bg = "white", col = "#1a7358", cex = 1.9, lwd = 2.8)
abline(v = diameter(Window(jp)) / 2, lty = 2, lwd = 3.6, col = COL_NARANJA)
text(diameter(Window(jp)) / 2 * 0.93, yl[1] + 1.6, "tope por\ndefecto: 0.7071", col = "#8A3D00", font = 2, cex = 1.3, adj = c(1, 0.5))
text(0.78, yl[1] + 4.4, "sigue\nsubiendo", col = "#1a7358", font = 2, cex = 1.3, adj = c(0, 0.5))
mtext("bw.ppl sobre japanesepines", side = 3, line = 2.4, cex = 1.5, font = 2, col = COL_TEXTO)
mtext("intervalo ampliado a 2 · más alto = mejor", side = 3, line = 0.9, cex = 1.25, col = COL_TEXTO)
dev.off()

# ---------------------------------------------------------------------
# F7 · Bogotá: oferta (todas las sedes) frente a estudiantes (evaluados), σ = bw.CvL
# ---------------------------------------------------------------------
sg <- as.numeric(bw.CvL(pu)); dd <- c(218, 128)
k_of <- density(pu,  sigma = sg, dimyx = dd, diggle = TRUE) * 1e6
k_es <- density(p11, sigma = sg, dimyx = dd, diggle = TRUE, weights = s11$s11_n[c11]) * 1e6
cat("F7 sigma:", round(sg, 4), " maximos:", round(c(max(k_of), max(k_es)), 4), "\n")
mc1 <- mapa_color(PAL_NARANJA, c(0, max(k_of))); mc2 <- mapa_color(PAL_NARANJA, c(0, max(k_es)))
abre_z("s1-oferta-estudiantes", 2000, 1300)
layout(matrix(c(1, 2, 3, 4), 2, 2, byrow = TRUE), heights = c(1, 0.2)); par(mar = c(0.2, 0.2, 3.6, 0.2))
et <- list(Suba = et_loc("Suba"), Bosa = et_loc("Bosa"), Kennedy = et_loc("Kennedy"))
pos_et <- c(Suba = 1, Bosa = 2, Kennedy = 4)
for (k in 1:2) {
  pinta_im(if (k == 1) k_of else k_es, if (k == 1) mc1 else mc2, WU)
  titulo_panel(if (k == 1) "Oferta: 2 107 sedes" else "Estudiantes: 145 362",
               if (k == 1) sprintf("máximo %.1f sedes por km²", max(k_of)) else sprintf("máximo %.0f evaluados por km²", max(k_es)))
  for (n in names(et)) { points(et[[n]][1], et[[n]][2], pch = 16, cex = 0.9, col = COL_VERDE); text(et[[n]][1], et[[n]][2], n, cex = 1.2, font = 2, col = COL_VERDE, pos = pos_et[[n]], offset = 0.5) }
  norte(bb["xmin"] + 1500, bb["ymax"] - 5200, 2600)
  if (k == 1) barra_escala(bb["xmin"] + 800, bb["ymin"] + 1800, 5000, "5 km")
}
barra_color(mc1, "sedes por km²", c(0, 5, 10, 14.5), c("0", "5", "10", "14.5"), cex = 1.2)
barra_color(mc2, "evaluados por km²", c(0, 500, 1000, 1500), c("0", "500", "1000", "1500"), cex = 1.2)
dev.off()

# ---------------------------------------------------------------------
# F8 · chorley: el patrón (casos y controles) y la superficie P(laringe)
# ---------------------------------------------------------------------
data(chorley)
ch <- chorley; marks(ch) <- factor(as.character(marks(chorley)), levels = c("lung", "larynx"))
rr <- relrisk(ch, sigma = 1)
vv <- as.numeric(rr$v); vv <- vv[is.finite(vv)]
cat("F8 chorley: mediana", round(median(vv), 4), " global", round(mean(marks(ch) == "larynx"), 4), " max", round(max(vv), 4), "\n")
inc <- chorley.extra$incin
mcc <- mapa_color(PAL_NARANJA, c(0, 1))                  # una probabilidad se pinta con escala fija de 0 a 1
xr <- Window(ch)$xrange; yr <- Window(ch)$yrange
abre_z("s1-chorley", 2300, 1200)
layout(matrix(c(1, 2, 3, 4), 2, 2, byrow = TRUE), heights = c(1, 0.3)); par(mar = c(0.4, 0.4, 3.8, 0.4))
plot(Window(ch), main = "", border = COL_TEXTO, lwd = 2, xlim = xr, ylim = yr - c(6.5, 0))
lung <- ch[marks(ch) == "lung"]; lar <- ch[marks(ch) == "larynx"]
points(lung$x, lung$y, pch = 16, cex = 0.55, col = adjustcolor(COL_PRIVADO, 0.75))
points(lar$x, lar$y, pch = 21, cex = 1.5, bg = COL_NARANJA, col = "white", lwd = 1.2)
points(inc$x, inc$y, pch = 4, cex = 2.4, lwd = 4, col = COL_VERDE)
mtext("978 de pulmón y 58 de laringe", side = 3, line = 0.6, cex = 1.4, font = 2, col = COL_TEXTO)
legend("bottomleft", bty = "n", cex = 1.4, pch = c(16, 21, 4), pt.cex = c(1.1, 1.6, 1.8), pt.bg = c(NA, COL_NARANJA, NA), col = c(COL_PRIVADO, "white", COL_VERDE),
       pt.lwd = c(1, 1, 4), legend = c("pulmón (controles)", "laringe (casos)", "incinerador en desuso"), text.col = COL_TEXTO)
barra_escala(xr[1] + 2.2, yr[2] - 2.3, 5, "5 km")
pinta_im(rr, mcc, Window(ch))
mtext("P(laringe) en cada punto", side = 3, line = 1.6, cex = 1.4, font = 2, col = COL_TEXTO)
mtext(sprintf("σ = 1 km · mediana %.4f · máximo %.4f", median(vv), max(vv)), side = 3, line = 0.2, cex = 1.2, col = COL_TEXTO)
points(inc$x, inc$y, pch = 4, cex = 2.4, lwd = 4, col = COL_VERDE)
plot.new()
par(mar = c(2.2, 5, 2.2, 5))
plot(NA, xlim = c(0, 1), ylim = c(0, 1), axes = FALSE, xlab = "", ylab = "", xaxs = "i", yaxs = "i")
n <- length(mcc$cols); rect(mcc$br[-(n + 1)], 0, mcc$br[-1], 1, col = mcc$cols, border = NA); rect(0, 0, 1, 1, border = COL_GRIS)
axis(1, at = c(0, 0.25, 0.5, 0.75, 1), labels = c("0", "0.25", "0.5", "0.75", "1"), col = COL_GRIS, col.axis = COL_TEXTO, cex.axis = 1.3, lwd = 0, lwd.ticks = 1, line = -0.3)
segments(mean(marks(ch) == "larynx"), 0, mean(marks(ch) == "larynx"), 1, lwd = 3, col = COL_VERDE)
mtext("línea verde: proporción global 58 / 1 036 = 0.056", side = 3, line = 0.2, cex = 1.25, col = COL_TEXTO)
dev.off()

# ---------------------------------------------------------------------
# F9 · Bogotá: P(oficial) (clases como el visor del capítulo) y las sedes por sector
# ---------------------------------------------------------------------
marca <- factor(ifelse(cole$sector[en] == "Oficial", "oficial", "privado"), levels = c("privado", "oficial"))
p_sec <- suppressWarnings(ppp(xy[en, 1], xy[en, 2], window = WU, marks = marca))
rr_b <- relrisk(p_sec, sigma = sg)
vb <- as.numeric(rr_b$v); vb <- vb[is.finite(vb)]
cat("F9 Bogotá: mediana", round(median(vb), 4), " global", round(mean(marks(p_sec) == "oficial"), 4), " oficiales:", sum(marks(p_sec) == "oficial"), " privadas:", sum(marks(p_sec) == "privado"), "\n")
mcd <- mapa_color(PAL_DIVERG, c(0, 1), clases = TRUE)
abre_z("s1-oficial-mapa-puntos", 2200, 1350)
layout(matrix(c(1, 2, 3, 4), 2, 2, byrow = TRUE), heights = c(1, 0.27)); par(mar = c(0.2, 0.2, 3.6, 0.2))
pinta_im(rr_b, mcd, WU); titulo_panel("P(oficial) en cada punto", sprintf("σ = %.0f m · escala de 0 a 1", sg))
norte(bb["xmin"] + 1500, bb["ymax"] - 5200, 2600); barra_escala(bb["xmin"] + 800, bb["ymin"] + 1800, 5000, "5 km")
plot(WU, main = "", border = COL_GRIS, lwd = 1.3)
pr <- p_sec[marks(p_sec) == "privado"]; of <- p_sec[marks(p_sec) == "oficial"]
points(pr$x, pr$y, pch = 16, cex = 0.8, col = adjustcolor("#d95f00", 0.85)); points(of$x, of$y, pch = 16, cex = 0.8, col = adjustcolor("#1a7358", 0.95))
titulo_panel("Las sedes sin suavizar", "709 oficiales y 1 398 privadas")
legend("bottomright", bty = "n", cex = 1.6, pch = 16, pt.cex = 2.2, col = c("#1a7358", "#d95f00"), legend = c("oficial", "privada"), text.col = COL_TEXTO)
barra_color(mcd, "0: solo privadas · 1: solo oficiales", seq(0, 1, length.out = 8)[c(1, 4, 8)], c("0", "0.5", "1"), cex = 1.25)
plot.new()
dev.off()

# ---------------------------------------------------------------------
# F10 · Bogotá: contar puntos (0.3365) contra la mediana de la superficie (0.3086)
# ---------------------------------------------------------------------
glob <- mean(marks(p_sec) == "oficial"); med <- median(vb)
abre_z("s1-oficial-hist", 2000, 800)
par(mar = c(4.6, 5.2, 1.4, 1.4))
h <- hist(vb, breaks = seq(0, 1, by = 0.05), plot = FALSE)
plot(NA, xlim = c(0, 1), ylim = c(0, max(h$density) * 1.32), axes = FALSE, xlab = "", ylab = "")
rect(h$breaks[-length(h$breaks)], 0, h$breaks[-1], h$density, col = adjustcolor("#7cc0aa", 0.9), border = "white")
axis(1, at = seq(0, 1, 0.1), col = COL_GRIS, col.axis = COL_TEXTO, cex.axis = 1.3, lwd = 0, lwd.ticks = 1)
mtext("P(oficial) en cada punto de la ciudad (cada píxel pesa lo mismo: misma área)", side = 1, line = 3.2, cex = 1.3, col = COL_TEXTO)
mtext("densidad", side = 2, line = 1, cex = 1.3, col = COL_TEXTO)
rect(0.5, 0, 1, max(h$density) * 1.08, col = adjustcolor(COL_VERDE, 0.06), border = NA)
text(0.75, max(h$density) * 0.55, sprintf("P(oficial) > 0.5:\nel %.1f %% del área", 100 * mean(vb > 0.5)), cex = 1.3, font = 2, col = COL_VERDE)
segments(med, 0, med, max(h$density) * 1.08, lwd = 5, col = COL_NARANJA)
segments(glob, 0, glob, max(h$density) * 1.08, lwd = 5, col = COL_VERDE, lty = 2)
text(med - 0.014, max(h$density) * 1.13, sprintf("mediana de la\nsuperficie: %.4f", med), adj = c(1, 0.5), cex = 1.3, font = 2, col = "#C2410C")
text(glob + 0.014, max(h$density) * 1.13, sprintf("contando puntos:\n%.4f", glob), adj = c(0, 0.5), cex = 1.3, font = 2, col = COL_VERDE)
dev.off()

# ---------------------------------------------------------------------
# F11 · cuadrantes: la rejilla de 8 × 8 y la misma rejilla movida un cuarto de celda
# ---------------------------------------------------------------------
caja <- as.rectangle(W); dxc <- diff(caja$xrange) / 8; dyc <- diff(caja$yrange) / 8
rejilla <- function(sx, sy) list(xb = caja$xrange[1] - sx * dxc + (0:9) * dxc, yb = caja$yrange[1] - sy * dyc + (0:9) * dyc)
cuenta <- function(g) { ix <- cut(p$x, g$xb, labels = FALSE, include.lowest = TRUE); iy <- cut(p$y, g$yb, labels = FALSE, include.lowest = TRUE); table(factor(ix, 1:9), factor(iy, 1:9)) }
mx_des <- c(); sh <- list()
for (sx in c(0, .25, .5, .75)) for (sy in c(0, .25, .5, .75)) {
  mx_des <- c(mx_des, max(as.numeric(quadratcount(p, xbreaks = rejilla(sx, sy)$xb, ybreaks = rejilla(sx, sy)$yb)))); sh[[length(sh) + 1]] <- c(sx, sy)
}
k_max <- which.max(mx_des)
cat("F11 cuadrantes: rejilla de 8 x 8 =", mx_des[1], " la mas llena de 16 desplazamientos =", max(mx_des), " con el desplazamiento", sh[[k_max]], "\n")
stopifnot(mx_des[1] == 15, max(mx_des) == 21, max(cuenta(rejilla(0, 0))) == 15, max(cuenta(rejilla(sh[[k_max]][1], sh[[k_max]][2]))) == 21)
panel_cuad <- function(sx, sy, l1, l2) {
  g <- rejilla(sx, sy); cn <- cuenta(g); m <- which(cn == max(cn), arr.ind = TRUE)[1, ]
  plot(sf_ken, col = "#FFF7ED", border = COL_TEXTO, lwd = 2.4)
  abline(v = g$xb, h = g$yb, col = adjustcolor(COL_GRIS, 0.95), lwd = 1.6)
  celda <- st_as_sfc(st_bbox(c(xmin = g$xb[m[1]], xmax = g$xb[m[1] + 1], ymin = g$yb[m[2]], ymax = g$yb[m[2] + 1]), crs = st_crs(sf_ken)))
  hl <- suppressWarnings(st_intersection(celda, sf_ken))
  plot(hl, col = adjustcolor(COL_NARANJA, 0.40), border = COL_NARANJA, lwd = 4, add = TRUE)
  plot(sf_ken, border = COL_TEXTO, lwd = 2.4, add = TRUE)
  points(p$x, p$y, pch = 16, cex = 0.9, col = COL_TEXTO)
  ctr <- st_coordinates(st_centroid(hl)); text(ctr[1], ctr[2], max(cn), cex = 3.4, font = 2, col = "#8A3D00")
  titulo_panel(l1, l2, cex1 = 1.7, cex2 = 1.45)
}
abre_z("s1-cuadrantes", 2200, 1100)
layout(matrix(1:2, 1)); par(mar = c(0.4, 0.4, 5.4, 0.4))
panel_cuad(0, 0, "Rejilla de 8 × 8", sprintf("la celda más llena: %d sedes", mx_des[1]))
panel_cuad(sh[[k_max]][1], sh[[k_max]][2], "La misma, movida media celda", sprintf("la celda más llena: %d sedes", max(mx_des)))
dev.off()

# ---------------------------------------------------------------------
# F12 · los cuatro núcleos al mismo σ = 400 m: el peso que una sede reparte según la distancia
# ---------------------------------------------------------------------
Wk <- owin(c(-3200, 3200), c(-3200, 3200)); X1 <- ppp(0, 0, window = Wk)
kers <- c("gaussian", "epanechnikov", "quartic", "disc")
perf <- lapply(kers, function(k) {
  im <- density(X1, sigma = 400, kernel = k, dimyx = c(641, 641), edge = FALSE)
  i0 <- which.min(abs(im$yrow)); d <- im$xcol; keep <- d >= 0
  list(d = d[keep], v = im$v[i0, keep] * 1e6, masa = sum(im$v) * im$xstep * im$ystep)
})
cat("F12 masa de cada núcleo (debe ser 1):", round(sapply(perf, `[[`, "masa"), 4), "\n")
col_k <- c(gaussian = "#1a7358", epanechnikov = "#D55E00", quartic = "#0072B2", disc = "#8A3D00")
abre_z("s1-nucleos-cuatro", 2000, 1000)
par(mar = c(5.4, 6.4, 4.8, 1.4))
ymx <- max(sapply(perf, function(z) max(z$v))) * 1.12
plot(NA, xlim = c(0, 1200), ylim = c(0, ymx), axes = FALSE, xlab = "", ylab = "")
axis(1, at = seq(0, 1200, 400), col = COL_GRIS, col.axis = COL_TEXTO, cex.axis = 1.5, lwd = 0, lwd.ticks = 1.5)
axis(2, at = c(0, 0.5, 1), las = 1, col = COL_GRIS, col.axis = COL_TEXTO, cex.axis = 1.5, lwd = 0, lwd.ticks = 1.5)
mtext("distancia a la sede (m)", side = 1, line = 3.6, cex = 1.55, col = COL_TEXTO)
mtext("peso por sede (por km²)", side = 2, line = 4.0, cex = 1.45, col = COL_TEXTO)
abline(v = 400, lty = 3, lwd = 3, col = COL_GRIS)
for (i in 1:4) lines(perf[[i]]$d, perf[[i]]$v, lwd = 7, col = col_k[kers[i]])
legend("topright", bty = "n", cex = 1.35, lwd = 7, col = col_k[kers], legend = kers, text.col = COL_TEXTO, seg.len = 1.6, y.intersp = 0.95)
mtext("Cuatro pesos, la misma desviación típica σ = 400 m", side = 3, line = 2.2, cex = 1.5, font = 2, col = COL_TEXTO)
mtext("cada uno integra 1; cambian la forma y el alcance", side = 3, line = 0.6, cex = 1.3, col = COL_TEXTO)
dev.off()

# ---------------------------------------------------------------------
# F13 · el borde en una dimensión: el núcleo de una sede a 0.5σ del borde y la parte que se sale
# ---------------------------------------------------------------------
sg1 <- 1; x0 <- 0.5; xs1 <- seq(-3, 4.6, length.out = 1200); k1 <- dnorm(xs1, x0, sg1)
e1 <- 1 - pnorm(0, x0, sg1)
cat("F13 borde 1-D: e =", round(e1, 4), " se pierde:", round(100 * (1 - e1), 2), "%\n")
abre_z("s1-borde-1d", 2000, 1000)
par(mar = c(5.6, 2.4, 5.2, 1.4))
ym1 <- max(k1) * 1.5
plot(NA, xlim = c(-3, 4.6), ylim = c(0, ym1), axes = FALSE, xlab = "", ylab = "", xaxs = "i", yaxs = "i")
rect(-3, 0, 0, ym1, col = "#E8ECF1", border = NA)
polygon(c(xs1[xs1 <= 0], 0), c(k1[xs1 <= 0], 0), col = adjustcolor(COL_NARANJA, 0.55), border = NA)
polygon(c(0, xs1[xs1 >= 0], 4.6), c(0, k1[xs1 >= 0], 0), col = adjustcolor("#1a7358", 0.30), border = NA)
lines(xs1, k1, lwd = 6, col = COL_TEXTO)
segments(0, 0, 0, ym1, lwd = 7, col = COL_TEXTO)
points(x0, 0, pch = 21, bg = COL_NARANJA, col = "white", cex = 4.4, lwd = 3)
text(x0, -ym1 * 0.06, "una sede", cex = 1.25, font = 2, col = "#8A3D00", xpd = NA)
text(-1.5, ym1 * 0.92, "fuera de la ventana", cex = 1.5, font = 2, col = COL_GRIS)
text(2.4, ym1 * 0.92, "dentro de la ventana", cex = 1.5, font = 2, col = "#1a7358")
text(-1.75, max(k1) * 0.62, sprintf("se pierde\nel %.0f %%", 100 * (1 - e1)), cex = 1.7, font = 2, col = "#8A3D00")
arrows(-1.2, max(k1) * 0.42, -0.45, max(k1) * 0.14, length = 0.14, lwd = 3.5, col = "#8A3D00")
text(1.45, max(k1) * 0.17, sprintf("queda dentro\ne = %.2f", e1), cex = 1.5, font = 2, col = "#0F5E46")
axis(1, at = -2:4, col = COL_GRIS, col.axis = COL_TEXTO, cex.axis = 1.5, lwd = 0, lwd.ticks = 1.5)
mtext("distancia al borde, en unidades de σ (el borde está en 0)", side = 1, line = 3.9, cex = 1.45, col = COL_TEXTO)
mtext("El núcleo de una sede a media σ del borde", side = 3, line = 2.4, cex = 1.65, font = 2, col = COL_TEXTO)
mtext("la ventana solo recoge una parte de su masa: esa fracción es e(x)", side = 3, line = 0.8, cex = 1.4, col = COL_TEXTO)
dev.off()

# ---------------------------------------------------------------------
# F14 · las tres capas de Bogotá, cada una a su escala: oferta, bachillerato y estudiantes
# ---------------------------------------------------------------------
k_11 <- density(p11, sigma = sg, dimyx = dd, diggle = TRUE) * 1e6
mc3 <- mapa_color(PAL_NARANJA, c(0, max(k_11)))
cat("F14 máximos de las tres capas:", round(c(max(k_of), max(k_11), max(k_es)), 4), "\n")
abre_z("s1-tres-capas", 2600, 1250)
layout(matrix(1:6, 2, 3, byrow = TRUE), heights = c(1, 0.17)); par(mar = c(0.2, 0.2, 4.6, 0.2))
cap <- list(list(k_of, mc1, "Oferta: 2 107", sprintf("máximo %.1f por km²", max(k_of))),
            list(k_11, mc3, "Bachillerato: 1 062", sprintf("máximo %.1f por km²", max(k_11))),
            list(k_es, mc2, "Estudiantes: 145 362", sprintf("máximo %.0f por km²", max(k_es))))
for (i in 1:3) {
  cp <- cap[[i]]; pinta_im(cp[[1]], cp[[2]], WU); titulo_panel(cp[[3]], cp[[4]], cex1 = 1.4, cex2 = 1.3)
  if (i == 1) { norte(bb["xmin"] + 1500, bb["ymax"] - 5200, 2600, cex = 1.6); barra_escala(bb["xmin"] + 800, bb["ymin"] + 1800, 5000, "5 km", cex = 1.4) }
}
barra_color(mc1, "sedes por km²", c(0, 5, 10, 14.5), c("0", "5", "10", "14.5"), cex = 1.45)
barra_color(mc3, "sedes por km²", c(0, 3, 6, 9), c("0", "3", "6", "9"), cex = 1.45)
barra_color(mc2, "evaluados por km²", c(0, 500, 1000, 1500), c("0", "500", "1000", "1500"), cex = 1.45)
dev.off()

cat("figuras de la sesión 1 listas\n")
