# =====================================================================
# figuras_comunes.R — utilidades de las figuras de las diapositivas del
# capítulo 5 (sesiones 1 y 2). Se cargan con source() desde
# genera_figuras_s1.R / genera_figuras_s2.R, desde la raíz del repo.
#
# POR QUÉ HAY FIGURAS PROPIAS Y NO LAS FOTOS DEL CAPÍTULO
#   Las fotos de los mapas ráster del capítulo (Kennedy por σ, oferta,
#   estudiantes, P(oficial)) salen invertidas verticalmente —el sur arriba—:
#   el exportador guarda la fila 0 en el sur y el visor la pinta arriba. Se
#   comprobó midiendo píxeles en la página servida y contra las coordenadas
#   de las sedes. Estas figuras se dibujan con el norte arriba.
# =====================================================================
suppressPackageStartupMessages({ library(sf); library(spatstat) })

PAL_NARANJA <- c("#fff0e0", "#ffd2a3", "#ffab5c", "#ff8420", "#d95f00", "#8a3d00")
PAL_DIVERG  <- c("#8a3d00", "#d95f00", "#ffab5c", "#f2f2f2", "#7cc0aa", "#1a7358", "#012820")
COL_OFICIAL <- "#E69F00"; COL_PRIVADO <- "#56B4E9"      # Okabe-Ito, como el visor del capítulo
COL_TEXTO <- "#1E293B"; COL_VERDE <- "#012820"; COL_NARANJA <- "#FF6600"; COL_GRIS <- "#94A3B8"

# ragg y no png(type = "cairo"): el R del framework 4.4 no trae las bibliotecas
# X11 que cairo necesita (`failed to load cairo DLL`), y ragg escribe UTF-8 (σ).
abre_png <- function(archivo, ancho_px, alto_px, res = 200, ...) {
  ragg::agg_png(archivo, width = ancho_px, height = alto_px, units = "px", res = res,
                background = "transparent", ...)
}

# Un ráster de spatstat (im): plot.im pinta la fila i en y creciente, o sea con
# el norte arriba, que es lo correcto.
pinta_im <- function(im, mc, W = NULL) {
  plot(im, col = mc$cmap, main = "", ribbon = FALSE, axes = FALSE, box = FALSE, add = FALSE)
  if (!is.null(W)) plot(W, add = TRUE, border = COL_TEXTO, lwd = 1.3)
}
# Un mapa de color = colores + cortes (se guardan juntos para pintar el mapa Y su barra)
mapa_color <- function(pal, zlim, n = 200, clases = FALSE) {
  cols <- if (clases) pal else colorRampPalette(pal)(n)
  br <- seq(zlim[1], zlim[2], length.out = length(cols) + 1)
  list(cols = cols, br = br, cmap = colourmap(cols, breaks = br), zlim = zlim, clases = clases)
}

# Título de panel en una o dos líneas, dentro del área de la figura
titulo_panel <- function(l1, l2 = NULL, cex1 = 1.5, cex2 = 1.25) {
  mtext(l1, side = 3, line = if (is.null(l2)) 0.4 else 2.1, cex = cex1, font = 2, col = COL_TEXTO)
  if (!is.null(l2)) mtext(l2, side = 3, line = 0.15, cex = cex2, col = COL_TEXTO)
}

norte <- function(x, y, largo, cex = 1.3) {
  arrows(x, y - largo / 2, x, y + largo / 2, length = 0.09, lwd = 2.2, col = COL_TEXTO)
  text(x, y + largo / 2, "N", font = 2, cex = cex, col = COL_TEXTO, pos = 3, offset = 0.3)
}
barra_escala <- function(x, y, metros, etiqueta, cex = 1.15) {
  segments(x, y, x + metros, y, lwd = 3, col = COL_TEXTO)
  segments(c(x, x + metros), y - metros * 0.03, c(x, x + metros), y + metros * 0.03, lwd = 2, col = COL_TEXTO)
  text(x + metros / 2, y, etiqueta, cex = cex, col = COL_TEXTO, pos = 3, offset = 0.5)
}
# Barra de color horizontal con la escala visible
barra_color <- function(mc, titulo, ticks, etiquetas = format(ticks, trim = TRUE), cex = 1.25, mar = c(2.6, 5, 1.8, 5)) {
  par(mar = mar)
  plot(NA, xlim = mc$zlim, ylim = c(0, 1), axes = FALSE, xlab = "", ylab = "", xaxs = "i", yaxs = "i")
  br <- mc$br
  rect(br[-length(br)], 0, br[-1], 1, col = mc$cols, border = if (mc$clases) "white" else NA, lwd = 1)
  rect(mc$zlim[1], 0, mc$zlim[2], 1, border = COL_GRIS, lwd = 1)
  axis(1, at = ticks, labels = etiquetas, col = COL_GRIS, col.axis = COL_TEXTO, cex.axis = cex, lwd = 0, lwd.ticks = 1, line = -0.3)
  mtext(titulo, side = 3, line = 0.2, cex = cex, col = COL_TEXTO)
}
