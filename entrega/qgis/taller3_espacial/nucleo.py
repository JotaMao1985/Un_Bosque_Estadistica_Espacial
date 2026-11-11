# -*- coding: utf-8 -*-
"""
nucleo.py — las cuentas del Taller 3, sin nada de QGIS

Estadística Espacial 2026-II (20929) · Universidad El Bosque

Aquí está TODO lo que las herramientas del taller calculan. No importa
nada de QGIS a propósito: solo numpy, que QGIS ya trae. Así se puede leer
de corrido, y así el curso lo contrasta contra `spatstat` fuera de QGIS.

Las cuatro cuentas son las de los capítulos 4 y 5, con las mismas
convenciones que el material:

  * la VENTANA es el polígono, no su caja envolvente;
  * el borde se corrige por MUESTRA REDUCIDA: para un radio r solo
    cuentan los puntos (o los sitios) que están a más de r del borde,
    que son los únicos cuyo disco de radio r se observó entero;
  * G y F se cuentan por umbral, «¿hay algo a distancia r o menos?»,
    igual que `ppp_G_borde` y `ppp_F_borde` del curso.

Una ventana llega como una lista de anillos; cada anillo es un arreglo
de N x 2 con sus vértices (el primero repetido al final o no, da igual).
Huecos e islas se tratan con la regla par-impar.
"""

import math

import numpy as np

TROZO = 2_000_000          # tope de celdas por operación vectorizada


# ---------------------------------------------------------------------
# Geometría de la ventana
# ---------------------------------------------------------------------
def segmentos(anillos):
    """Todos los lados de la ventana: (x1, y1, x2, y2), uno por fila."""
    partes = []
    for a in anillos:
        a = np.asarray(a, dtype=float)
        if len(a) < 3:
            continue
        if not np.array_equal(a[0], a[-1]):
            a = np.vstack([a, a[:1]])
        partes.append(np.hstack([a[:-1], a[1:]]))
    s = np.vstack(partes)
    return s[(s[:, 0] != s[:, 2]) | (s[:, 1] != s[:, 3])]   # sin lados nulos


def area(anillos):
    """Área con la regla par-impar: los anillos de fuera suman, los huecos restan."""
    total = 0.0
    for i, a in enumerate(anillos):
        a = np.asarray(a, dtype=float)
        x, y = a[:, 0], a[:, 1]
        s = abs(0.5 * float(np.sum(x * np.roll(y, -1) - np.roll(x, -1) * y)))
        # ¿cuántos de los OTROS anillos contienen a este? Par: suma. Impar: resta.
        otros = [b for j, b in enumerate(anillos) if j != i]
        nivel = 0
        if otros:
            nivel = int(_cruces(a[:1, 0], a[:1, 1], segmentos(otros))[0])
        total += s if nivel % 2 == 0 else -s
    return total


def _cruces(x, y, seg):
    """Cuántos lados cruza la semirrecta horizontal que sale de cada punto."""
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    n = np.zeros(len(x), dtype=np.int64)
    paso = max(1, TROZO // max(1, len(seg)))
    x1, y1, x2, y2 = seg[:, 0], seg[:, 1], seg[:, 2], seg[:, 3]
    for i in range(0, len(x), paso):
        px = x[i:i + paso, None]
        py = y[i:i + paso, None]
        sube = (y1 > py) != (y2 > py)
        with np.errstate(divide="ignore", invalid="ignore"):
            xc = x1 + (py - y1) * (x2 - x1) / (y2 - y1)
        n[i:i + paso] = np.sum(sube & (px < xc), axis=1)
    return n


def dentro(x, y, anillos):
    """¿Está cada punto dentro de la ventana? Regla par-impar."""
    return _cruces(x, y, segmentos(anillos)) % 2 == 1


def dist_borde(x, y, anillos):
    """Distancia de cada punto al borde de la ventana (al lado más cercano)."""
    seg = segmentos(anillos)
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    x1, y1 = seg[:, 0], seg[:, 1]
    dx, dy = seg[:, 2] - x1, seg[:, 3] - y1
    l2 = dx * dx + dy * dy
    d = np.empty(len(x))
    paso = max(1, TROZO // max(1, len(seg)))
    for i in range(0, len(x), paso):
        px = x[i:i + paso, None]
        py = y[i:i + paso, None]
        t = np.clip(((px - x1) * dx + (py - y1) * dy) / l2, 0.0, 1.0)
        ex = px - (x1 + t * dx)
        ey = py - (y1 + t * dy)
        d[i:i + paso] = np.sqrt(np.min(ex * ex + ey * ey, axis=1))
    return d


def caja(anillos):
    """(xmin, xmax, ymin, ymax) de la ventana."""
    v = np.vstack([np.asarray(a, dtype=float) for a in anillos])
    return float(v[:, 0].min()), float(v[:, 0].max()), float(v[:, 1].min()), float(v[:, 1].max())


# ---------------------------------------------------------------------
# Distancias
# ---------------------------------------------------------------------
def dist_vecino(x, y):
    """Distancia de cada punto a su vecino más próximo (0 si hay un duplicado)."""
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    n = len(x)
    d = np.empty(n)
    paso = max(1, TROZO // max(1, n))
    for i in range(0, n, paso):
        dx = x[i:i + paso, None] - x[None, :]
        dy = y[i:i + paso, None] - y[None, :]
        d2 = dx * dx + dy * dy
        f = np.arange(d2.shape[0])
        d2[f, i + f] = np.inf            # un punto no es vecino de sí mismo
        d[i:i + paso] = np.sqrt(d2.min(axis=1))
    return d


def dist_al_patron(sx, sy, x, y):
    """Distancia de cada sitio (sx, sy) al punto del patrón más cercano."""
    sx = np.asarray(sx, dtype=float)
    sy = np.asarray(sy, dtype=float)
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    d = np.empty(len(sx))
    paso = max(1, TROZO // max(1, len(x)))
    for i in range(0, len(sx), paso):
        dx = sx[i:i + paso, None] - x[None, :]
        dy = sy[i:i + paso, None] - y[None, :]
        d[i:i + paso] = np.sqrt((dx * dx + dy * dy).min(axis=1))
    return d


# ---------------------------------------------------------------------
# G, F y J (capítulo 4, módulo 7)
# ---------------------------------------------------------------------
def g_borde(x, y, anillos, rg):
    """G(r): de los puntos a más de r del borde, la fracción con vecino a r o menos."""
    d = dist_vecino(x, y)
    b = dist_borde(x, y, anillos)
    g = np.full(len(rg), np.nan)
    for k, r in enumerate(rg):
        usa = b > r
        if usa.any():
            g[k] = float(np.mean(d[usa] <= r))
    return g


def f_borde(x, y, anillos, rg, lado=200):
    """F(r): de los SITIOS a más de r del borde, la fracción con un punto a r o menos.

    Los sitios son los nodos de una rejilla de lado x lado sobre la caja de
    la ventana que caen DENTRO de la ventana. Devuelve (F, número de sitios).
    """
    x0, x1, y0, y1 = caja(anillos)
    gx = np.linspace(x0, x1, lado)
    gy = np.linspace(y0, y1, lado)
    sx, sy = np.meshgrid(gx, gy)
    sx, sy = sx.ravel(), sy.ravel()
    ok = dentro(sx, sy, anillos)
    sx, sy = sx[ok], sy[ok]
    d = dist_al_patron(sx, sy, x, y)
    b = dist_borde(sx, sy, anillos)
    f = np.full(len(rg), np.nan)
    for k, r in enumerate(rg):
        usa = b > r
        if usa.any():
            f[k] = float(np.mean(d[usa] <= r))
    return f, int(len(sx))


def gf_teorica(lam, rg):
    """G y F bajo CSR, que son la misma curva: 1 - exp(-lambda pi r^2)."""
    return 1.0 - np.exp(-lam * math.pi * np.asarray(rg, dtype=float) ** 2)


def j_de(g, f):
    """J(r) = (1 - G) / (1 - F); sin valor donde F llega a 1."""
    with np.errstate(divide="ignore", invalid="ignore"):
        j = (1.0 - g) / (1.0 - f)
    j[~np.isfinite(j)] = np.nan
    return j


# ---------------------------------------------------------------------
# K y L de Ripley (capítulo 4, módulos 8 y 10)
# ---------------------------------------------------------------------
def k_borde(x, y, b, a, rg):
    """K(r) con corrección de borde por muestra reducida.

    K(r) = [ suma, sobre los puntos i a más de r del borde, del número de
             OTROS puntos a distancia r o menos de i ]
           / ( lambda * número de puntos a más de r del borde ),
    con lambda = n / área. `b` es la distancia de cada punto al borde.
    """
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    rg = np.asarray(rg, dtype=float)
    n = len(x)
    lam = n / a
    cuenta = np.zeros((n, len(rg)))            # vecinos de i a distancia <= r
    paso = max(1, TROZO // max(1, n))
    for i in range(0, n, paso):
        dx = x[i:i + paso, None] - x[None, :]
        dy = y[i:i + paso, None] - y[None, :]
        d = np.sqrt(dx * dx + dy * dy)
        f = np.arange(d.shape[0])
        d[f, i + f] = np.inf
        d.sort(axis=1)
        for j in range(d.shape[0]):
            cuenta[i + j] = np.searchsorted(d[j], rg, side="right")
    k = np.full(len(rg), np.nan)
    for q, r in enumerate(rg):
        usa = b > r
        m = int(usa.sum())
        if m:
            k[q] = float(cuenta[usa, q].sum()) / (lam * m)
    return k


def l_de(k):
    """L(r) = raíz de K(r) / pi. Bajo CSR, L(r) = r."""
    return np.sqrt(np.asarray(k, dtype=float) / math.pi)


def csr(n, anillos, rng):
    """n puntos uniformes dentro de la ventana, por rechazo sobre su caja."""
    x0, x1, y0, y1 = caja(anillos)
    xs = np.empty(0)
    ys = np.empty(0)
    while len(xs) < n:
        m = 2 * n + 64
        cx = x0 + (x1 - x0) * rng.random(m)
        cy = y0 + (y1 - y0) * rng.random(m)
        ok = dentro(cx, cy, anillos)
        xs = np.concatenate([xs, cx[ok]])
        ys = np.concatenate([ys, cy[ok]])
    return xs[:n], ys[:n]


def envolvente_l(n, anillos, a, rg, nsim, semilla):
    """Banda puntual de L(r) bajo CSR: mínimo y máximo de nsim simulaciones.

    Cada simulación reparte n puntos al azar en la ventana (n fijo, el del
    patrón) y calcula su L con la MISMA corrección de borde. Con nsim = 99
    y mínimo-máximo, salirse de la banda en UN r fijado de antemano es un
    contraste al 2 %; mirar toda la curva y buscar dónde se sale no lo es
    (capítulo 4, módulo 11).
    """
    rng = np.random.default_rng(int(semilla))
    sims = np.empty((nsim, len(rg)))
    for s in range(nsim):
        sx, sy = csr(n, anillos, rng)
        sims[s] = l_de(k_borde(sx, sy, dist_borde(sx, sy, anillos), a, rg))
    return np.nanmin(sims, axis=0), np.nanmax(sims, axis=0)


# ---------------------------------------------------------------------
# Test de cuadrantes (capítulo 4, módulos 5 y 6)
# ---------------------------------------------------------------------
def celda_de(x, y, cj, nx, ny):
    """Celda (columna, fila) de cada punto en una rejilla nx x ny sobre la caja.

    Intervalos abiertos por la izquierda y cerrados por la derecha, con el
    primero cerrado por los dos lados: la convención de `quadratcount`.
    """
    x0, x1, y0, y1 = cj
    ix = np.ceil((np.asarray(x, dtype=float) - x0) / (x1 - x0) * nx).astype(int) - 1
    iy = np.ceil((np.asarray(y, dtype=float) - y0) / (y1 - y0) * ny).astype(int) - 1
    return np.clip(ix, 0, nx - 1), np.clip(iy, 0, ny - 1)


def chi2_cuadrantes(obs, areas):
    """chi2 de cuadrantes con celdas de área DESIGUAL (ventana no rectangular).

    El esperado de cada celda es n por su fracción del área de la ventana.
    Devuelve (chi2, grados de libertad, esperados). Las celdas de área
    cero no existen: no entran ni en la suma ni en los grados de libertad.
    """
    obs = np.asarray(obs, dtype=float)
    areas = np.asarray(areas, dtype=float)
    ok = areas > 0
    esp = np.zeros_like(areas)
    esp[ok] = obs[ok].sum() * areas[ok] / areas[ok].sum()
    x2 = float(np.sum((obs[ok] - esp[ok]) ** 2 / esp[ok]))
    return x2, int(ok.sum()) - 1, esp


def chi2_cola(x, gl):
    """P(chi2 con gl grados de libertad > x), sin scipy.

    Es la gamma incompleta regularizada Q(gl/2, x/2): serie para x
    pequeño, fracción continua para x grande (Numerical Recipes, 6.2).
    """
    a, z = gl / 2.0, x / 2.0
    if z <= 0:
        return 1.0
    lg = math.lgamma(a)
    if z < a + 1.0:
        ap, suma, d = a, 1.0 / a, 1.0 / a
        for _ in range(10_000):
            ap += 1.0
            d *= z / ap
            suma += d
            if abs(d) < abs(suma) * 1e-15:
                break
        return 1.0 - suma * math.exp(-z + a * math.log(z) - lg)
    chico = 1e-300
    b = z + 1.0 - a
    c = 1.0 / chico
    d = 1.0 / b
    h = d
    for i in range(1, 10_000):
        an = -i * (i - a)
        b += 2.0
        d = an * d + b
        d = chico if abs(d) < chico else d
        c = b + an / c
        c = chico if abs(c) < chico else c
        d = 1.0 / d
        delta = d * c
        h *= delta
        if abs(delta - 1.0) < 1e-15:
            break
    return math.exp(-z + a * math.log(z) - lg) * h


# ---------------------------------------------------------------------
# Una gráfica de líneas en SVG, sin matplotlib
# ---------------------------------------------------------------------
def svg_lineas(x, series, titulo, eje_x, eje_y, banda=None, marca=None, ancho=720, alto=420):
    """Devuelve un <svg> con las series dadas.

    series: lista de (nombre, valores, color, discontinua).
    banda:  (inferior, superior) para sombrear, o None.
    marca:  abscisa donde trazar una vertical, o None.
    """
    x = np.asarray(x, dtype=float)
    ml, mr, mt, mb = 64, 16, 34, 46
    todo = [np.asarray(v, dtype=float) for _, v, _, _ in series]
    if banda is not None:
        todo += [np.asarray(banda[0], dtype=float), np.asarray(banda[1], dtype=float)]
    junto = np.concatenate(todo)
    junto = junto[np.isfinite(junto)]
    y0, y1 = (float(junto.min()), float(junto.max())) if len(junto) else (0.0, 1.0)
    if y1 == y0:
        y1 = y0 + 1.0
    hol = 0.04 * (y1 - y0)
    y0, y1 = y0 - hol, y1 + hol
    x0, x1 = float(x.min()), float(x.max())

    def px(v):
        return ml + (v - x0) / (x1 - x0) * (ancho - ml - mr)

    def py(v):
        return alto - mb - (v - y0) / (y1 - y0) * (alto - mt - mb)

    def camino(v):
        v = np.asarray(v, dtype=float)
        trozos, abierto = [], False
        for xi, vi in zip(x, v):
            if not np.isfinite(vi):
                abierto = False
                continue
            trozos.append("%s%.1f,%.1f" % ("L" if abierto else "M", px(xi), py(vi)))
            abierto = True
        return " ".join(trozos)

    def num(v):
        return ("%.4g" % v).replace("e+0", "e").replace("e-0", "e-")

    o = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d" '
         'style="font-family:sans-serif;font-size:12px;background:#fff">' % (ancho, alto, ancho, alto),
         '<text x="%d" y="20" font-size="14" font-weight="bold">%s</text>' % (ml, titulo)]
    for i in range(6):
        vy = y0 + (y1 - y0) * i / 5
        vx = x0 + (x1 - x0) * i / 5
        o.append('<line x1="%d" y1="%.1f" x2="%d" y2="%.1f" stroke="#e3e3e3"/>'
                 % (ml, py(vy), ancho - mr, py(vy)))
        o.append('<text x="%d" y="%.1f" text-anchor="end">%s</text>' % (ml - 6, py(vy) + 4, num(vy)))
        o.append('<text x="%.1f" y="%d" text-anchor="middle">%s</text>' % (px(vx), alto - mb + 16, num(vx)))
    o.append('<rect x="%d" y="%d" width="%d" height="%d" fill="none" stroke="#888"/>'
             % (ml, mt, ancho - ml - mr, alto - mt - mb))
    if banda is not None:
        lo = np.asarray(banda[0], dtype=float)
        hi = np.asarray(banda[1], dtype=float)
        ok = np.isfinite(lo) & np.isfinite(hi)
        if ok.sum() > 1:
            arriba = " ".join("%.1f,%.1f" % (px(a), py(b)) for a, b in zip(x[ok], hi[ok]))
            abajo = " ".join("%.1f,%.1f" % (px(a), py(b)) for a, b in zip(x[ok][::-1], lo[ok][::-1]))
            o.append('<polygon points="%s %s" fill="#bbbbbb" fill-opacity="0.5"/>' % (arriba, abajo))
    if marca is not None and x0 <= marca <= x1:
        o.append('<line x1="%.1f" y1="%d" x2="%.1f" y2="%d" stroke="#FF6600" stroke-dasharray="2 3"/>'
                 % (px(marca), mt, px(marca), alto - mb))
    for i, (nombre, v, color, disc) in enumerate(series):
        o.append('<path d="%s" fill="none" stroke="%s" stroke-width="2"%s/>'
                 % (camino(v), color, ' stroke-dasharray="6 4"' if disc else ""))
        lx = ml + 10 + 150 * i
        o.append('<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="%s" stroke-width="2"%s/>'
                 % (lx, mt + 12, lx + 22, mt + 12, color, ' stroke-dasharray="6 4"' if disc else ""))
        o.append('<text x="%d" y="%d">%s</text>' % (lx + 27, mt + 16, nombre))
    o.append('<text x="%.1f" y="%d" text-anchor="middle">%s</text>'
             % ((ml + ancho - mr) / 2, alto - 8, eje_x))
    o.append('<text x="14" y="%.1f" text-anchor="middle" transform="rotate(-90 14 %.1f)">%s</text>'
             % ((mt + alto - mb) / 2, (mt + alto - mb) / 2, eje_y))
    o.append("</svg>")
    return "\n".join(o)
