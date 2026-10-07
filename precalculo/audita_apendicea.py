#!/usr/bin/env python3
"""
audita_apendicea.py — auditoría independiente del precálculo del apéndice A

  «La densidad en una dimensión»
  Material de Estadística Espacial 2026-II (20929).

NO comprueba que los archivos existan: comprueba que sus NÚMEROS sean
ciertos, por caminos que no pasan por R.

QUÉ SE REIMPLEMENTA AQUÍ, que es lo que hace que esto sea un control:

  · EL HISTOGRAMA DE R, con su convenio [a, b) o (a, b] y con la holgura
    (`fuzz`) que `hist()` le pone a los cortes. Sin ella, un dato que cae
    justo en un corte —y `faithful` tiene muchos: sus 272 valores son 126
    cifras de tres decimales— se iría a la barra de al lado, y el número de
    modas del módulo 2 saldría distinto sin que nadie hubiera mentido.
  · `pretty()`, porque «el histograma que R hace por defecto» depende de él.
  · CONTAR MODAS con la misma definición del generador —comprimir las
    rachas iguales y contar las que superan a sus dos vecinas, con 0 fuera—
    pero escrita aquí. Una moda es una frase de la prosa: si el dato deja de
    decirla, el texto miente con aspecto de correcto.
  · EL ASH con su malla extendida, el núcleo triangular, el k-NN, todas las
    KDE por SUMA DIRECTA, y las formas cerradas de los módulos 4, 8 y 11.
  · EL EM de la mezcla, con los mismos valores iniciales, y la MISE exacta
    de la KDE gaussiana contra esa mezcla, por convolución de normales.
    Además, la misma MISE por integración numérica del error punto a punto,
    que es otro camino a la misma cifra.
  · Las DISTANCIAS AL VECINO con `cKDTree`, y la reciprocidad.
  · Los RESÚMENES DEL MONTE CARLO, uno a uno, desde el CSV réplica a réplica.

LA SEMILLA COMPARTIDA, O CÓMO SE AUDITA UNA MUESTRA QUE NO SE PUBLICA
La muestra unimodal del módulo 6 no viaja en el JSON. Pero el generador
la saca con `set.seed(2026); rnorm(100, 5, 2)`, y la cafetería, la
trimodal, la mezcla y la nube del módulo 8 arrancan TODAS con la misma
semilla. `rnorm(n, mu, sd)` es `mu + sd·z` con la misma sucesión de z, así
que las cuatro muestras publicadas tienen que contar las mismas z —se
comprueba— y la unimodal se reconstruye como `5 + 2·z`, con un error de
1e-6 que viene del redondeo a seis decimales. Con ella sus tres conteos de
modas (1, 27 y 9) salen idénticos.

LOS SELECTORES DE R, POR DOS CAMINOS
`bw.ucv`, `bw.bcv` y `bw.SJ` no minimizan el criterio exacto: AGRUPAN las
diferencias por parejas en 1 000 casillas (y, con más de 500 datos, agrupan
antes los propios datos) y luego buscan con el Brent de `optimize()` o el
`uniroot()` de R. Se auditan dos veces:

  1. PORTADOS: el agrupado de `bw_pair_cnts`, las sumas de `bandwidths.c`,
     el `Brent_fmin` de `optimize` y el `zeroin2` de `uniroot`, escritos
     aquí desde su definición. Es independencia PARCIAL —el mismo algoritmo,
     otra implementación—, y es lo que permite exigir 1e-8: coinciden con R
     a 1e-11 en `faithful`, en las 20 réplicas guardadas y en las sedes.
  2. EXACTOS: los criterios sin agrupar (UCV dejando uno fuera, BCV,
     la ecuación de Sheather y Jones), minimizados o resueltos con scipy.
     Es independencia TOTAL, y el precio es una tolerancia del 3 %, que es
     lo que mueve el agrupado. Solo se aplica donde el criterio tiene
     mínimo: con empates la UCV exacta no lo tiene, y eso es el módulo 12.

`KernSmooth::dpik` va solo por el camino 2: su agrupado lineal en 401
puntos no se porta, se recalcula el plug-in de dos etapas sin agrupar.

`density()` TAMBIÉN SE PORTA (agrupado lineal, FFT, interpolación final),
porque las ISE del Monte Carlo y la rugosidad del módulo 10 se calcularon
con ella. Y al lado va la KDE exacta por suma directa, que es el camino
independiente: las ISE se separan de las de `density()` en menos del 1 %.

HASTA DÓNDE LLEGA LA INDEPENDENCIA, DECLARADO Y NO INSINUADO
  · TOTAL para los histogramas, las modas, el ASH, las KDE, el k-NN, las
    formas cerradas, los núcleos (por cuadratura), el EM, la MISE de la
    mezcla, las distancias al vecino, los empates, el umbral, la UCV exacta,
    la corrección de borde y todos los resúmenes del Monte Carlo.
  · PARCIAL para los selectores agrupados y para `density()`: mismo
    algoritmo, otra implementación. Cada uno lleva al lado su versión exacta.
  · NULA para los DATOS: `faithful` es el conjunto de R. Se ancla a las
    cifras que publica la literatura (n, media, sd, IQR). Y nula para la
    constante de CSR «simulada»: sale del generador de R. Se comprueba que
    está a menos de 0.012 de la fórmula, y se repite la simulación aquí,
    con el generador de numpy.

LA RUGOSIDAD DEL MÓDULO 10, MEDIDA Y DECLARADA. El generador estima ∫f̂''²
con segundas diferencias sobre la salida de `density()`, que INTERPOLA
linealmente desde su propia rejilla. La forma cerrada, ψ₄(√2·h), se separa
de lo publicado un 0.2 % con los selectores de validación cruzada y hasta
un 6.5 % con la regla del histograma (h = 0.62). Se audita lo publicado
con `density()` portada, a 1e-6, y la forma cerrada con su tolerancia: no
cambia ninguna frase, pero la cifra es una aproximación y aquí se dice.

Ejecutar con el Python de geo_env:
    "$(python3 -c 'import json;print(json.load(open("precalculo/versiones_py.json"))["ejecutable"])')" \\
        precalculo/audita_apendicea.py

Las rutas de los siete archivos se pueden cambiar con APA_DATOS,
APA_SOLUCIONES, APA_MC, APA_MUESTRAS, APA_CAFETERIA, APA_FAITHFUL y
APA_MEZCLA (los tres últimos son los CSV que leen las pestañas de
Python, porque numpy no puede simular la muestra de R): es lo que usa el
arnés de inyección
(`prueba_auditor_apendicea.py`) para auditar copias envenenadas sin tocar
nunca las publicadas.

LOS RÓTULOS TIENEN PRESUPUESTO: 57 CARACTERES, PREFIJO INCLUIDO. Uno de
58 o más queda pegado a su detalle y el arnés deja de contar esa
comprobación como cubierta, en silencio. Ver `audita_cap4.py`.
"""
from __future__ import annotations

import math
import os
import pathlib
import re
import sys
import warnings

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from audita_base import Auditoria, carga as _carga, decimales, sin_nan  # noqa: E402

import numpy as np                                   # noqa: E402
import pandas as pd                                  # noqa: E402
from scipy import integrate, optimize                # noqa: E402
from scipy.spatial import cKDTree                    # noqa: E402
from scipy.stats import gaussian_kde, norm           # noqa: E402

warnings.filterwarnings("ignore")

RAIZ = pathlib.Path(__file__).resolve().parent.parent
PRECALCULO = RAIZ / "precalculo"
SALIDAS = PRECALCULO / "salidas"
PROCESADO = RAIZ / "datos" / "procesado"

EPS = float(np.finfo(float).eps)
RAIZ2PI = math.sqrt(2 * math.pi)
RK_GAUSS = 1 / (2 * math.sqrt(math.pi))

# El JSON de datos sale de `geo_escribe()` con `digits = 8`: OCHO decimales,
# aunque el generador redondee a diez. Una cifra recalculada aquí por el
# mismo camino no puede exigir más que eso.
T8 = 1.1e-8
# Las muestras van con seis decimales (r6): lo que se rehace desde ellas
# arrastra hasta 5e-7 por dato.
T6 = 2e-6
# Los criterios exactos frente a los agrupados de R (ver la cabecera).
# Medido: SJ, BCV y dpik se separan menos del 0.8 %. La UCV es más plana y
# su mínimo se mueve más con el agrupado —hasta un 2.4 % en las réplicas del
# Monte Carlo y en las sedes, donde R agrupa además los propios datos—, así
# que lleva su propia tolerancia.
TOL_AGRUPADO = 0.03
TOL_UCV = 0.05


def carga(var: str, nombre: str):
    return _carga(var, nombre, SALIDAS)


def ruta_csv(var: str, nombre: str) -> pathlib.Path:
    p = pathlib.Path(os.environ.get(var) or (SALIDAS / nombre))
    if not p.exists():
        sys.exit(f"PARADO: falta {p}")
    return p


# =====================================================================
# LAS PIEZAS DE R QUE HACEN FALTA, ESCRITAS AQUÍ
# =====================================================================
def r_seq_by(a: float, b: float, by: float) -> np.ndarray:
    """`seq(a, b, by = by)`: a + (0:n)·by, recortado a b (seq.default)."""
    n = int((b - a) / by + 1e-10)
    return np.minimum(a + np.arange(n + 1) * by, b)


def r_seq_len(a: float, b: float, n: int) -> np.ndarray:
    """`seq(a, b, length.out = n)`: el último es b exacto."""
    if n == 1:
        return np.array([a], float)
    out = a + np.arange(n) * ((b - a) / (n - 1))
    out[-1] = b
    return out


def r_pretty(lo: float, up: float, ndiv: int, min_n: int,
             shrink: float = 0.75, hb: float = 1.5) -> np.ndarray:
    """`pretty()` de R (R_pretty, con bounds = TRUE), para los cortes de hist()."""
    h5 = .5 + 1.5 * hb
    dx = up - lo
    if dx == 0 and up == 0:
        cell, i_small = 1.0, True
    else:
        cell = max(abs(lo), abs(up))
        U = 1 + (1 / (1 + hb) if h5 >= 1.5 * hb + .5 else 1.5 / (1 + h5))
        U *= max(1, ndiv) * EPS
        i_small = dx < cell * U * 3
    if i_small:
        if cell > 10:
            cell = 9 + cell / 10
        cell *= shrink
        if min_n > 1:
            cell /= min_n
    else:
        cell = dx
        if ndiv > 1:
            cell /= ndiv
    base = 10.0 ** math.floor(math.log10(cell))
    unit = base
    if 2 * base - cell < hb * (cell - unit):
        unit = 2 * base
        if 5 * base - cell < h5 * (cell - unit):
            unit = 5 * base
            if 10 * base - cell < hb * (cell - unit):
                unit = 10 * base
    reps = 1e-10
    ns = math.floor(lo / unit + reps)
    nu = math.ceil(up / unit - reps)
    while ns * unit > lo + reps * unit:
        ns -= 1
    while nu * unit < up - reps * unit:
        nu += 1
    k = int(0.5 + nu - ns)
    if k < min_n:
        k = min_n - k
        if ns >= 0:
            nu += k // 2
            ns -= k // 2 + k % 2
        else:
            ns -= k // 2
            nu += k // 2 + k % 2
        ndiv = min_n
    else:
        ndiv = k
    l = ns * unit if ns * unit < lo else lo
    u = nu * unit if nu * unit > up else up
    s = r_seq_len(l, u, ndiv + 1)
    delta = (u - l) / ndiv
    s[np.abs(s) < 1e-14 * delta] = 0.0
    return s


def r_conteos(x, br, right: bool = True, include_lowest: bool = True) -> np.ndarray:
    """Los conteos de `hist()` con su holgura: 1e-7 de la mediana del ancho.

    Con `right = FALSE` las barras son [a, b) y la holgura mueve los cortes
    a la izquierda; con `right = TRUE` son (a, b] y los mueve a la derecha
    (salvo el primero, si include.lowest). Es lo que hace que un dato que
    cae justo en el corte vaya siempre a la misma barra, haya error de
    representación o no.
    """
    x = np.asarray(x, float)
    br = np.asarray(br, float)
    nB = len(br)
    h = np.diff(br)
    if nB > 5:
        diddle = 1e-7 * float(np.median(h))
    elif nB <= 3:
        diddle = 1e-7 * float(x.max() - x.min())
    else:
        diddle = 1e-7 * float(h[h > 0].min())
    if right:
        fz = np.r_[-diddle if include_lowest else diddle, np.full(nB - 1, diddle)]
        fb = br + fz
        k = np.searchsorted(fb, x, side="left") - 1
    else:
        fz = np.r_[np.full(nB - 1, -diddle), diddle if include_lowest else -diddle]
        fb = br + fz
        k = np.searchsorted(fb, x, side="right") - 1
        k = np.where(x == fb[-1], nB - 2, k)
    ok = (k >= 0) & (k < nB - 1)
    return np.bincount(k[ok], minlength=nB - 1)[:nB - 1]


def find_interval(v, b) -> np.ndarray:
    """`findInterval()`: cuántos cortes hay <= v (índice 1-based de R)."""
    return np.searchsorted(np.asarray(b, float), np.asarray(v, float), side="right")


def modas_secuencia(y) -> int:
    """Rachas iguales comprimidas; moda = racha mayor que sus dos vecinas (0 fuera)."""
    y = np.asarray(y, float)
    if y.size == 0:
        return 0
    r = y[np.r_[True, y[1:] != y[:-1]]]
    izq = np.r_[0.0, r[:-1]]
    der = np.r_[r[1:], 0.0]
    return int(np.sum((r > izq) & (r > der) & (r > 0)))


def donde_modas(x, y) -> np.ndarray:
    y = np.asarray(y, float)
    corte = np.r_[True, y[1:] != y[:-1]]
    ini = np.flatnonzero(corte)                       # 0-based
    fin = np.r_[ini[1:] - 1, len(y) - 1]
    r = y[ini]
    izq = np.r_[0.0, r[:-1]]
    der = np.r_[r[1:], 0.0]
    k = np.flatnonzero((r > izq) & (r > der) & (r > 0))
    # R: x[floor((ini + fin) / 2)] con índices 1-based
    pos = np.floor(((ini[k] + 1) + (fin[k] + 1)) / 2).astype(int) - 1
    return np.asarray(x)[pos]


def trapecio(x, y) -> float:
    x = np.asarray(x, float)
    y = np.asarray(y, float)
    return float(np.sum(np.diff(x) * (y[:-1] + y[1:]) / 2))


def sd(x) -> float:
    return float(np.std(np.asarray(x, float), ddof=1))


def iqr(x) -> float:
    x = np.asarray(x, float)
    return float(np.quantile(x, .75) - np.quantile(x, .25))      # tipo 7


def bw_nrd0(x) -> float:
    hi = sd(x)
    lo = min(hi, iqr(x) / 1.34)
    if not lo:
        lo = hi or abs(float(np.asarray(x)[0])) or 1.0
    return 0.9 * lo * len(x) ** (-0.2)


def bw_nrd(x) -> float:
    return 1.06 * min(sd(x), iqr(x) / 1.34) * len(x) ** (-1 / 5)


def phi(u):
    return np.exp(-0.5 * np.asarray(u, float) ** 2) / RAIZ2PI


def kde_gauss(x, g, h) -> np.ndarray:
    """KDE gaussiana por suma directa, por bloques para no inflar la memoria."""
    x = np.asarray(x, float)
    g = np.asarray(g, float)
    out = np.empty(len(g))
    paso = max(1, 4_000_000 // max(1, len(x)))
    for i in range(0, len(g), paso):
        u = (g[i:i + paso, None] - x[None, :]) / h
        out[i:i + paso] = np.exp(-0.5 * u * u).sum(axis=1)
    return out / (len(x) * h * RAIZ2PI)


def kde_r(x, g, bw, nucleo) -> np.ndarray:
    """La KDE en la convención de `density()`: bw es la desviación típica."""
    a = {"gaussian": 1.0, "rectangular": math.sqrt(3), "epanechnikov": math.sqrt(5),
         "triangular": math.sqrt(6), "biweight": math.sqrt(7)}[nucleo]
    x = np.asarray(x, float)
    out = np.zeros(len(g))
    for xi in x:
        u = (g - xi) / (a * bw)
        if nucleo == "gaussian":
            out += np.exp(-0.5 * u * u) / RAIZ2PI
        elif nucleo == "rectangular":
            out += np.where(np.abs(u) <= 1, 0.5, 0.0)
        elif nucleo == "triangular":
            out += np.where(np.abs(u) <= 1, 1 - np.abs(u), 0.0)
        elif nucleo == "biweight":
            out += np.where(np.abs(u) <= 1, (15 / 16) * (1 - u * u) ** 2, 0.0)
        else:
            out += np.where(np.abs(u) <= 1, 0.75 * (1 - u * u), 0.0)
    return out / len(x) / (a * bw)


def knn_curva(datos, g, k) -> np.ndarray:
    """k / (2 n d_k(t)) en cada punto de la rejilla."""
    datos = np.asarray(datos, float)
    g = np.asarray(g, float)
    out = np.empty(len(g))
    paso = max(1, 2_000_000 // max(1, len(datos)))
    for i in range(0, len(g), paso):
        d = np.abs(g[i:i + paso, None] - datos[None, :])
        dk = np.partition(d, k - 1, axis=1)[:, k - 1]
        out[i:i + paso] = k / (2 * len(datos) * dk)
    return out


def ash(x, h, m, g) -> np.ndarray:
    """El ASH con la malla EXTENDIDA, [a, b) e include.lowest, como el generador."""
    x = np.asarray(x, float)
    g = np.asarray(g, float)
    n = len(x)
    d = h / m
    mal = r_seq_by(x.min() - h, x.max() + h + d, h)
    e = np.zeros(len(g))
    for j in range(m):
        b = mal + j * d
        cn = r_conteos(x, b, right=False, include_lowest=True)
        i = find_interval(g, b)
        ok = (i >= 1) & (i <= len(b) - 1)
        e += np.where(ok, cn[np.clip(i, 1, len(cn)) - 1], 0)
    return e / (m * n * h)


# =====================================================================
# density() DE R, PORTADA (R ≥ 4.4: coordenadas nuevas del núcleo)
# =====================================================================
def r_density(x, bw, n_user, frm, to, ext=4, nucleo="gaussian", xout=None) -> np.ndarray:
    """Agrupado lineal (BinDist), convolución por FFT e interpolación lineal."""
    x = np.asarray(x, float)
    n = max(n_user, 512)
    if n > 512:
        n = int(2 ** math.ceil(math.log2(n)))
    lo = frm - ext * bw
    up = to + ext * bw
    y = np.zeros(2 * n)
    w = 1.0 / len(x)
    xpos = (x - lo) / ((up - lo) / (n - 1))
    ix = np.floor(xpos).astype(np.int64)
    fx = xpos - ix
    m = (ix >= 0) & (ix <= n - 2)
    np.add.at(y, ix[m], w * (1 - fx[m]))
    np.add.at(y, ix[m] + 1, w * fx[m])
    m = ix == -1
    np.add.at(y, np.zeros(int(m.sum()), int), w * fx[m])
    m = ix == n - 1
    np.add.at(y, ix[m], w * (1 - fx[m]))
    kords = r_seq_len(0.0, (2 * n - 1) / (n - 1) * (up - lo), 2 * n)
    kords[n + 1:] = -kords[n - 1:0:-1]
    if nucleo == "gaussian":
        kords = np.exp(-0.5 * (kords / bw) ** 2) / (RAIZ2PI * bw)
    else:                                            # epanechnikov
        ae = bw * math.sqrt(5)
        ax_ = np.abs(kords)
        kords = np.where(ax_ < ae, 0.75 * (1 - (ax_ / ae) ** 2) / ae, 0.0)
    conv = np.fft.ifft(np.fft.fft(y) * np.conj(np.fft.fft(kords)))
    kk = np.maximum(0.0, conv.real[:n])
    xords = r_seq_len(lo, up, n)
    xs = r_seq_len(frm, to, n_user)
    ys = np.interp(xs, xords, kk)
    return ys if xout is None else np.interp(xout, xs, ys)


# =====================================================================
# LOS SELECTORES DE R, PORTADOS (camino 1 de la cabecera)
# =====================================================================
def brent_fmin(ax, bx, f, tol) -> float:
    """El `Brent_fmin` de `optimize()`, paso a paso."""
    c = (3. - math.sqrt(5.)) * .5
    eps = math.sqrt(EPS)
    a, b = ax, bx
    v = a + c * (b - a)
    w = x = v
    d = e = 0.
    fx = f(x)
    fv = fw = fx
    tol3 = tol / 3.
    while True:
        xm = (a + b) * .5
        tol1 = eps * abs(x) + tol3
        t2 = tol1 * 2.
        if abs(x - xm) <= t2 - (b - a) * .5:
            break
        p = q = r = 0.
        if abs(e) > tol1:
            r = (x - w) * (fx - fv)
            q = (x - v) * (fx - fw)
            p = (x - v) * q - (x - w) * r
            q = (q - r) * 2.
            if q > 0.:
                p = -p
            else:
                q = -q
            r = e
            e = d
        if abs(p) >= abs(q * .5 * r) or p <= q * (a - x) or p >= q * (b - x):
            e = (b - x) if x < xm else (a - x)
            d = c * e
        else:
            d = p / q
            u = x + d
            if u - a < t2 or b - u < t2:
                d = tol1 if x < xm else -tol1
        if abs(d) >= tol1:
            u = x + d
        elif d > 0.:
            u = x + tol1
        else:
            u = x - tol1
        fu = f(u)
        if fu <= fx:
            if u < x:
                b = x
            else:
                a = x
            v, w, x = w, x, u
            fv, fw, fx = fw, fx, fu
        else:
            if u < x:
                a = u
            else:
                b = u
            if fu <= fw or w == x:
                v, fv, w, fw = w, fw, u, fu
            elif fu <= fv or v == x or v == w:
                v, fv = u, fu
    return x


def zeroin2(ax, bx, fa, fb, f, tol, maxit=1000) -> float:
    """El `zeroin2` de `uniroot()` (Brent), paso a paso."""
    a, b = ax, bx
    c, fc = a, fa
    if fa == 0.0:
        return a
    if fb == 0.0:
        return b
    maxit += 1
    while maxit:
        maxit -= 1
        prev_step = b - a
        if abs(fc) < abs(fb):
            a, b, c = b, c, b
            fa, fb, fc = fb, fc, fb
        tol_act = 2 * EPS * abs(b) + tol / 2
        new_step = (c - b) / 2
        if abs(new_step) <= tol_act or fb == 0.0:
            return b
        if abs(prev_step) >= tol_act and abs(fa) > abs(fb):
            cb = c - b
            if a == c:
                t1 = fb / fa
                p = cb * t1
                q = 1.0 - t1
            else:
                q = fa / fc
                t1 = fb / fc
                t2 = fb / fa
                p = t2 * (cb * q * (q - t1) - (b - a) * (t1 - 1.0))
                q = (q - 1.0) * (t1 - 1.0) * (t2 - 1.0)
            if p > 0:
                q = -q
            else:
                p = -p
            if p < (0.75 * cb * q - abs(tol_act * q) / 2) and p < abs(prev_step * q / 2):
                new_step = p / q
        if abs(new_step) < tol_act:
            new_step = tol_act if new_step > 0 else -tol_act
        a, fa = b, fb
        b += new_step
        fb = f(b)
        if (fb > 0 and fc > 0) or (fb < 0 and fc < 0):
            c, fc = a, fa
    return b


def pares_agrupados(x, nb=1000):
    """`bw_pair_cnts`: las diferencias por parejas en nb casillas."""
    x = np.asarray(x, float)
    n = len(x)
    if n > nb / 2:
        # Con muchos datos R agrupa ANTES los datos y cuenta casilla contra casilla.
        d = (x.max() - x.min()) * 1.01 / nb
        xx = np.trunc(np.abs(x) / d) * np.sign(x)
        xx = (xx - xx.min() + 1).astype(np.int64)
        w = np.bincount(xx, minlength=nb + 1)[1:nb + 1].astype(float)
        cnt = np.zeros(nb)
        cnt[0] = 0.5 * float(np.sum(w * (w - 1.)))
        cnt[1:] = np.correlate(w, w, mode="full")[nb:]
        return d, cnt
    dd = (x.max() - x.min()) * 1.01 / nb
    idx = (x / dd).astype(np.int64)                  # (int)(x/dd): trunca
    iu = np.triu_indices(n, 1)
    dif = np.abs(idx[iu[1]] - idx[iu[0]])
    return dd, np.bincount(dif, minlength=nb)[:nb].astype(float)


def _suma(cnt, d, h, termino) -> float:
    i = np.arange(len(cnt))
    delta = (i * d / h) ** 2
    corte = np.flatnonzero(delta >= 1000.)            # DELMAX
    k = corte[0] if corte.size else len(cnt)
    t = termino(delta[:k])
    s = 0.0
    for ti, ci in zip(t, cnt[:k]):                     # el orden de suma de C
        s += ti * ci
    return s


def r_ucv(n, d, cnt, h):
    s = _suma(cnt, d, h, lambda dl: np.exp(-dl / 4.) - math.sqrt(8.0) * np.exp(-dl / 2.))
    return (0.5 + s / n) / (n * h * math.sqrt(math.pi))


def r_bcv(n, d, cnt, h):
    s = _suma(cnt, d, h, lambda dl: np.exp(-dl / 4) * (dl * dl - 12 * dl + 12))
    return (1 + s / (32.0 * n)) / (2.0 * n * h * math.sqrt(math.pi))


def r_phi4(n, d, cnt, h):
    s = _suma(cnt, d, h, lambda dl: np.exp(-dl / 2.) * (dl * dl - 6. * dl + 3.))
    return (2. * s + n * 3.) / (float(n) * (n - 1) * h ** 5.0 * RAIZ2PI)


def r_phi6(n, d, cnt, h):
    s = _suma(cnt, d, h, lambda dl: np.exp(-dl / 2) * (dl ** 3 - 15 * dl * dl + 45 * dl - 15))
    return (2. * s - 15. * n) / (float(n) * (n - 1) * h ** 7.0 * RAIZ2PI)


def bw_cv_r(x, criterio):
    """bw.ucv / bw.bcv de R: (h, avisa)."""
    x = np.asarray(x, float)
    n = len(x)
    hmax = 1.144 * sd(x) * n ** (-1 / 5)
    lower, upper = 0.1 * hmax, hmax
    tol = 0.1 * lower
    d, cnt = pares_agrupados(x)
    f = r_ucv if criterio == "ucv" else r_bcv
    h = brent_fmin(lower, upper, lambda hh: f(n, d, cnt, hh), tol)
    return h, bool(h < lower + tol or h > upper - tol)


def bw_sj_r(x) -> float:
    """bw.SJ(method = "ste") de R."""
    x = np.asarray(x, float)
    n = len(x)
    d, cnt = pares_agrupados(x)
    escala = min(sd(x), iqr(x) / 1.349)
    a = 1.24 * escala * n ** (-1 / 7)
    b = 1.23 * escala * n ** (-1 / 9)
    c1 = 1 / (2 * math.sqrt(math.pi) * n)
    TD = -r_phi6(n, d, cnt, b)
    hmax = 1.144 * escala * n ** (-1 / 5)
    lower, upper = 0.1 * hmax, hmax
    alph2 = 1.357 * (r_phi4(n, d, cnt, a) / TD) ** (1 / 7)

    def fSD(h):
        return (c1 / r_phi4(n, d, cnt, alph2 * h ** (5 / 7))) ** (1 / 5) - h
    itry = 1
    while fSD(lower) * fSD(upper) > 0 and itry < 100:
        if itry % 2:
            upper *= 1.2
        else:
            lower /= 1.2
        itry += 1
    return zeroin2(lower, upper, fSD(lower), fSD(upper), fSD, 0.1 * lower)


# =====================================================================
# LOS CRITERIOS EXACTOS, SIN AGRUPAR (camino 2 de la cabecera)
# =====================================================================
def _difs(v):
    v = np.asarray(v, float)
    iu = np.triu_indices(len(v), 1)
    return v[iu[1]] - v[iu[0]]


def ucv_exacta(v, h) -> float:
    """∫f̂² − (2/n) Σ f̂₋ᵢ(Xᵢ), la UCV que deja uno fuera (la del generador)."""
    v = np.asarray(v, float)
    n = len(v)
    dd = _difs(v)
    rf2 = (n * phi(0.0) + 2 * phi(dd / (math.sqrt(2) * h)).sum()) / (n * n * h * math.sqrt(2))
    loo = 2 * 2 * phi(dd / h).sum() / (n * (n - 1) * h)
    return float(rf2 - loo)


def _minimo_en_rejilla(f, lo, hi, puntos=40) -> float:
    """El mínimo GLOBAL en [lo, hi]: rejilla y luego Brent alrededor."""
    g = np.exp(np.linspace(math.log(lo), math.log(hi), puntos))
    val = np.array([f(h) for h in g])
    i = int(np.argmin(val))
    a = g[max(i - 1, 0)]
    b = g[min(i + 1, len(g) - 1)]
    r = optimize.minimize_scalar(f, bounds=(a, b), method="bounded",
                                 options={"xatol": 1e-10 * hi})
    return float(r.x)


def ucv_exacta_min(v) -> float:
    v = np.asarray(v, float)
    hmax = 1.144 * sd(v) * len(v) ** (-1 / 5)
    return _minimo_en_rejilla(lambda h: ucv_exacta(v, h), 0.1 * hmax, hmax)


def bcv_exacta_min(v) -> float:
    v = np.asarray(v, float)
    n = len(v)
    dd = _difs(v)
    hmax = 1.144 * sd(v) * n ** (-1 / 5)

    def f(h):
        dl = (dd / h) ** 2
        s = float(np.sum(np.exp(-dl / 4) * (dl * dl - 12 * dl + 12)))
        return (1 + s / (32.0 * n)) / (2.0 * n * h * math.sqrt(math.pi))
    return _minimo_en_rejilla(f, 0.1 * hmax, hmax)


def sj_exacto(v) -> float:
    """La ecuación de Sheather y Jones (1991), con las parejas exactas."""
    v = np.asarray(v, float)
    n = len(v)
    dd = _difs(v)

    def psi(h, orden):
        dl = (dd / h) ** 2
        if orden == 4:
            s = 2 * float(np.sum(np.exp(-dl / 2) * (dl * dl - 6 * dl + 3))) + 3 * n
            return s / (n * (n - 1) * h ** 5 * RAIZ2PI)
        s = 2 * float(np.sum(np.exp(-dl / 2) * (dl ** 3 - 15 * dl * dl + 45 * dl - 15))) - 15 * n
        return s / (n * (n - 1) * h ** 7 * RAIZ2PI)
    escala = min(sd(v), iqr(v) / 1.349)
    a = 0.920 * 1.349 * escala * n ** (-1 / 7)
    b = 0.912 * 1.349 * escala * n ** (-1 / 9)
    TD = -psi(b, 6)
    alfa = 1.357 * (psi(a, 4) / TD) ** (1 / 7)

    def ecuacion(h):
        return (RK_GAUSS / (n * psi(alfa * h ** (5 / 7), 4))) ** (1 / 5) - h
    lo, hi = 0.05 * escala * n ** (-1 / 5), 3 * escala * n ** (-1 / 5)
    return float(optimize.brentq(ecuacion, lo, hi, xtol=1e-12))


def dpik_exacto(v) -> float:
    """El plug-in de dos etapas de Wand y Jones (dpik, level = 2), sin agrupar."""
    v = np.asarray(v, float)
    n = len(v)
    esc = min(sd(v), iqr(v) / (norm.ppf(.75) - norm.ppf(.25)))
    z = (v - v.mean()) / esc
    dz = np.subtract.outer(z, z).ravel()

    def psi(g, r):
        u = dz / g
        if r == 6:
            k = (u ** 6 - 15 * u ** 4 + 45 * u ** 2 - 15) * phi(u)
        else:
            k = (u ** 4 - 6 * u ** 2 + 3) * phi(u)
        return float(k.sum()) / (n * n * g ** (r + 1))
    alfa = (2 * math.sqrt(2) ** 9 / (7 * n)) ** (1 / 9)
    psi6 = psi(alfa, 6)
    alfa = (-3 * math.sqrt(2 / math.pi) / (psi6 * n)) ** (1 / 7)
    psi4 = psi(alfa, 4)
    return esc * (4 * math.pi) ** (-1 / 10) * (1 / (psi4 * n)) ** (1 / 5)


# =====================================================================
# Comparadores
# =====================================================================
def vec(a, calc, pub, que, tol):
    """Dos vectores, por su mayor diferencia absoluta."""
    try:
        c = np.asarray(calc, float)
        p = np.asarray(pub, float)
    except (TypeError, ValueError):
        return a.cierto(False, que, "no son números")
    if c.shape != p.shape:
        return a.cierto(False, que, f"longitudes {c.shape} y {p.shape}")
    dmax = float(np.max(np.abs(c - p))) if c.size else 0.0
    return a.cierto(dmax <= tol, que, f"dif máx {dmax:.2e} (tol {tol:.0e})")


def enteros(a, calc, pub, que):
    c = [int(v) for v in calc]
    ok = isinstance(pub, list) and len(pub) == len(c) and all(
        isinstance(p, (int, float)) and p == q for p, q in zip(pub, c))
    det = "" if ok else f"calc {c[:8]} · publ {list(pub)[:8] if isinstance(pub, list) else pub}"
    return a.cierto(ok, que, det)


def por(lista, clave, valor):
    return next((x for x in lista if isinstance(x, dict) and x.get(clave) == valor), {})


# =====================================================================
# Los módulos
# =====================================================================
def datos_de_partida(a, D, ctx):
    a.titulo("0 · Los datos de partida")
    E = np.asarray(D["m2"]["eruptions"], float)
    ctx["E"] = E
    # `faithful` es el conjunto canónico de R; sus resúmenes están en todos
    # los textos. Si el JSON trajera otro vector, todo lo demás cuadraría
    # consigo mismo y el apéndice hablaría de otro dato.
    a.igual(len(E), 272, "faithful: 272 erupciones")
    a.igual(E.mean(), 3.487783, "faithful: media 3.487783 (literatura)", tol=6e-7)
    a.igual(sd(E), 1.141371, "faithful: sd 1.141371 (literatura)", tol=6e-7)
    a.igual(iqr(E), 2.2915, "faithful: IQR 2.2915 (literatura)", tol=1e-9)
    a.cierto(E.min() == 1.6 and E.max() == 5.1, "faithful: rango [1.6, 5.1]",
             f"[{E.min()}, {E.max()}]")
    tres = np.all(np.abs(E * 1000 - np.round(E * 1000)) < 1e-6)
    a.cierto(bool(tres), "faithful: ningún dato pasa de tres decimales")

    sed = pd.read_csv(SALIDAS / "cap5_bogota_urbana.csv")
    ken = pd.read_csv(SALIDAS / "cap5_kennedy.csv")
    ctx["sed"] = sed[["x", "y"]].to_numpy(float)
    ctx["ken"] = ken[["x", "y"]].to_numpy(float)
    a.igual(len(sed), 2107, "sedes: 2 107 urbanas (las del capítulo 5)")
    a.igual(len(ken), 262, "sedes: 262 de Kennedy (las del capítulo 5)")

    area = None
    gpkg = PROCESADO / "bogota_ventana_urbana.gpkg"
    if gpkg.exists():
        import geopandas as gpd
        v = gpd.read_file(gpkg)
        area = float(v.geometry.area.sum()) / 1e6
        a.igual(area, 370.0898165101, "área urbana: el gpkg, releído (km²)", tol=1e-6)
    else:
        a.salta("área urbana: el gpkg, releído", f"no está {gpkg} (worktree sin datos/)")
    cap5 = SALIDAS / "cap5_datos.json"
    if cap5.exists():
        import json
        c5 = json.loads(cap5.read_text(encoding="utf-8"))
        a5 = (c5.get("m8", {}).get("forzado", {}) or {}).get("area_km2")
        if a5 is not None:
            a.igual(a5, 370.0898165101, "área urbana: la del capítulo 5", tol=1e-6)
            area = area if area is not None else float(a5)
    if area is None:
        area = 370.0898165101
        a.salta("área urbana: contra una fuente", "ni el gpkg ni cap5_datos.json")
    ctx["area"] = area
    a.igual(D["m1"]["sedes"]["area_km2"], area, "m1: el área publicada", tol=T8)
    a.igual(D["m12"]["area_km2"], area, "m12: el área publicada", tol=T8)


def semilla(a, D, ctx):
    a.titulo("0b · La semilla compartida: las mismas z en todas")
    z = np.asarray(D["m8"]["nube"], float).ravel()
    t = np.asarray(D["m1"]["tiempos"], float)
    tri = np.asarray(D["m6"]["muestra_trimodal"], float)
    mez = np.asarray(D["m7"]["mezcla"]["muestra"], float)
    a.igual(len(z), 3000, "nube: 30 muestras de 100")
    # rnorm(n, mu, sd) = mu + sd·z con la misma sucesión de z: tras
    # set.seed(2026), las cinco muestras tienen que contar las mismas z.
    # Con los DISEÑOS PUBLICADOS (μ y σ de cada muestra), no con constantes
    # de aquí: un diseño declarado que no es el que generó la muestra rompe
    # estas igualdades.
    ca = D["m1"]["diseno"]
    n1 = int(ca["n1"])
    vec(a, (t[:n1] - ca["mu1"]) / ca["sd1"], z[:n1], "semilla: bebidas = μ₁ + σ₁·z", 2e-6)
    vec(a, (t[n1:] - ca["mu2"]) / ca["sd2"], z[n1:len(t)], "semilla: comidas = μ₂ + σ₂·z", 2e-6)
    tr = D["m6"]["trimodal"]
    cortes = np.cumsum([0, tr["n1"], tr["n2"], tr["n3"]])
    for i in range(3):
        a_, b_ = int(cortes[i]), int(cortes[i + 1])
        vec(a, (tri[a_:b_] - tr["mu"][i]) / tr["sd"][i], z[a_:b_],
            f"semilla: trimodal {i + 1} = μ + σ·z", 2e-6)
    mz = D["m7"]["mezcla"]
    h_ = len(mez) // 2
    vec(a, (mez[:h_] - mz["medias"][0]) / mz["sd"][0], z[:h_], "semilla: mezcla 1 = μ + σ·z", 2e-6)
    vec(a, (mez[h_:] - mz["medias"][1]) / mz["sd"][1], z[h_:2 * h_], "semilla: mezcla 2 = μ + σ·z", 2e-6)
    a.cierto((ca["mu1"], ca["sd1"], ca["mu2"], ca["sd2"]) == (3.5, 0.7, 9.5, 1.4),
             "semilla: el diseño de la cafetería es el del texto")
    # La unimodal NO se publica: se reconstruye con su diseño publicado.
    un = D["m6"]["unimodal"]
    a.cierto((un["mu"], un["sd"]) == (5, 2), "semilla: la unimodal es N(5, 2)")
    ctx["uni"] = un["mu"] + un["sd"] * z[:100]


def modulo1(a, D, ctx):
    a.titulo("1 · La cafetería: densidad e intensidad")
    m = D["m1"]
    t = np.asarray(m["tiempos"], float)
    n = len(t)
    a.igual(n, m["n"], "m1: el número de tiempos")
    a.igual(m["diseno"]["n1"] + m["diseno"]["n2"], n, "m1: bebidas + comidas = n")
    a.igual(t.mean(), m["media"], "m1: la media", tol=T6)
    a.igual(float(np.median(t)), m["mediana"], "m1: la mediana", tol=T6)
    a.igual(t.min(), m["min"], "m1: el mínimo", tol=T6)
    a.igual(t.max(), m["max"], "m1: el máximo", tol=T6)
    cortes = r_seq_by(math.floor(t.min()), math.ceil(t.max()), 1.0)
    vec(a, cortes, m["cortes"], "m1: los cortes de ancho 1", 0)
    cnt = r_conteos(t, cortes, right=False)
    dens = cnt / (n * 1.0)
    enteros(a, cnt, m["conteos"], "m1: los conteos [a, b)")
    vec(a, dens, m["densidades"], "m1: las densidades", T8)
    a.igual(float(np.sum(dens * np.diff(cortes))), 1.0, "m1: el área del histograma es 1", tol=1e-12)
    i = int(np.argmax(cnt))
    bm = m["barra_max"]
    a.igual(cortes[i], bm["desde"], "m1: la barra más alta empieza")
    a.igual(cnt[i], bm["conteo"], "m1: la barra más alta cuenta")
    a.igual(dens[i], bm["densidad"], "m1: su densidad", tol=T8)
    a.igual(60 * dens[i], bm["densidad_por_hora"], "m1: su densidad por hora", tol=T8)
    a.igual(cnt[i], bm["intensidad"], "m1: su intensidad (pedidos por hora)")
    j = int(find_interval([t.mean()], cortes)[0]) - 1
    bme = m["barra_media"]
    a.igual(cortes[j], bme["desde"], "m1: la barra de la media empieza")
    a.igual(cnt[j], bme["conteo"], "m1: la barra de la media cuenta")
    a.cierto(cnt[j] <= 3, "m1: la media cae en una barra casi vacía", f"{cnt[j]} tiempos")
    valle = int(np.sum((t >= 5) & (t < 7)))
    a.igual(valle, m["valle"]["conteo"], "m1: los tiempos del valle [5, 7)")
    a.igual(valle / n, m["valle"]["proporcion"], "m1: su proporción", tol=T8)
    a.igual(modas_secuencia(dens), m["modas"], "m1: las modas del histograma")
    a.igual(m["modas"], 2, "m1: y son dos, como dice la prosa")
    a.igual(m["ancho"], 1, "m1: el ancho de barra declarado")
    a.igual(m["minutos_por_hora"], 60, "m1: sesenta minutos por hora")
    a.igual(m["sedes"]["n"], len(ctx["sed"]), "m1: las sedes del puente")
    a.igual(len(ctx["sed"]) / ctx["area"], m["sedes"]["lambda_km2"],
            "m1: λ = n / área (sedes por km²)", tol=T8)


def modulo2(a, D, ctx):
    a.titulo("2 · El histograma: ancho y origen")
    m = D["m2"]
    E = ctx["E"]
    n = len(E)
    a.igual(m["n"], n, "m2: n")
    stur = math.ceil(math.log2(n) + 1)
    a.igual(stur, m["sturges_clases"], "m2: Sturges = ⌈log₂ n + 1⌉")
    br = r_pretty(E.min(), E.max(), stur, 1)
    vec(a, br, m["def_cortes"], "m2: los cortes de hist() (pretty)", 1e-12)
    a.igual(len(br) - 1, m["def_clases"], "m2: las clases de hist() por defecto")
    a.igual(br[1] - br[0], m["def_ancho"], "m2: su ancho", tol=T8)
    hfd = 2 * iqr(E) * n ** (-1 / 3)
    a.igual(hfd, m["fd"]["h"], "m2: el ancho de Freedman-Diaconis", tol=T8)
    a.igual(math.ceil((E.max() - E.min()) / (2 * iqr(E)) * n ** (1 / 3)),
            m["fd"]["clases"], "m2: las clases de nclass.FD")
    a.igual(3.5 * sd(E) * n ** (-1 / 3), m["scott"]["h"], "m2: el ancho de Scott", tol=T8)
    a.igual(m["scott"]["constante"], 3.5, "m2: la constante de Scott, 3.5")
    a.igual((24 * math.sqrt(math.pi)) ** (1 / 3), m["scott"]["constante_exacta"],
            "m2: y la exacta, (24√π)^(1/3)", tol=T8)

    anchos = r_seq_by(0.10, 1.00, 0.05)
    fracs = r_seq_by(0.0, 0.95, 0.05)
    vec(a, anchos, m["anchos"], "m2: la rejilla de anchos", 1e-12)
    vec(a, fracs, m["fracs"], "m2: la rejilla de orígenes", 1e-12)

    def histo(h, f):
        o = f * h
        a0 = math.floor((E.min() - o) / h) * h + o
        b = a0 + h * np.arange(math.floor((E.max() - a0) / h) + 2)
        return r_conteos(E, b, right=False) / (n * h)
    tab = np.array([[modas_secuencia(histo(h, f)) for f in fracs] for h in anchos])
    enteros(a, tab.min(axis=1), m["modas_min"], "m2: las modas mínimas por ancho")
    enteros(a, tab.max(axis=1), m["modas_max"], "m2: las modas máximas por ancho")
    enteros(a, tab[:, 0], m["escala_modas_origen0"], "m2: las modas con el origen quieto")
    cambia = anchos[tab.max(axis=1) > tab.min(axis=1)]
    h_o = float(cambia[cambia <= 0.5].max())
    a.igual(h_o, m["h_origen"], "m2: el ancho en que el origen manda", tol=1e-12)
    fila = tab[np.argmin(np.abs(anchos - h_o))]
    o = m["origen"]
    a.igual(fracs[int(np.argmin(fila))], o["frac_pocas"], "m2: el origen de pocas modas", tol=1e-12)
    a.igual(fracs[int(np.argmax(fila))], o["frac_muchas"], "m2: el origen de muchas", tol=1e-12)
    a.igual(fracs[int(np.argmin(fila))] * h_o, o["desplaza_pocas"], "m2: su desplazamiento", tol=T8)
    a.igual(fracs[int(np.argmax(fila))] * h_o, o["desplaza_muchas"],
            "m2: el desplazamiento de muchas", tol=T8)
    a.igual(fila.min(), o["modas_pocas"], "m2: las modas con el origen bueno")
    a.igual(fila.max(), o["modas_muchas"], "m2: las modas con el origen malo")
    a.cierto(fila.min() == 2 and fila.max() >= 3,
             "m2: mover solo el origen lleva de 2 modas a 3 o más",
             f"{fila.min()} → {fila.max()}")
    a.igual(len(fila), o["n_origenes"], "m2: los orígenes probados")
    a.igual(int(np.sum(fila == fila.min())), o["origenes_pocas"], "m2: orígenes con pocas modas")
    a.igual(int(np.sum(fila == fila.max())), o["origenes_muchas"], "m2: orígenes con muchas")
    a.igual(2 ** 1.5, m["tasas"]["datos_para_mitad"], "m2: datos para la mitad: 2^(3/2)", tol=T8)
    a.cierto(m["tasas"]["h"] == "-1/3" and m["tasas"]["mise"] == "-2/3",
             "m2: las tasas h ∝ n^(-1/3), MISE ∝ n^(-2/3)")


def modulo3(a, D, ctx):
    a.titulo("3 · El ASH: promediar los orígenes")
    m = D["m3"]
    ej = m["ejemplo"]
    xa = np.array([2, 3, 3, 5, 7, 8, 9, 10], float)
    ha, ma = 2.0, 3
    da = ha / ma
    vec(a, xa, ej["datos"], "m3: los datos del ejemplo a mano", 0)
    a.igual(da, ej["delta"], "m3: δ = h/m", tol=T8)
    base = r_seq_by(xa.min(), xa.max(), ha)
    vec(a, base, ej["base_cortes"], "m3: la malla base", 0)
    enteros(a, r_conteos(xa, base, right=False), ej["base_conteos"], "m3: los conteos de la malla base")
    pierde = [int(np.sum((xa >= b[0]) & (xa < b[-1])) + np.sum(xa == b[-1]))
              for b in (base + j * da for j in range(ma))]
    enteros(a, pierde, ej["base_desplazada_cuenta"], "m3: lo que ve la malla base corrida")
    a.cierto(pierde[0] == len(xa) and all(np.diff(pierde) < 0),
             "m3: cada corrimiento de la base pierde más datos", str(pierde))
    ext = r_seq_by(0, 12, ha)
    a.cierto(ej["extendida"]["desde"] == ext[0] and ej["extendida"]["hasta"] == ext[-1],
             "m3: la malla extendida va de 0 a 12")
    pts = np.array([3, 5, 7, 9], float)
    fj = np.zeros((4, ma))
    for j in range(ma):
        b = ext + j * da
        cn = r_conteos(xa, b, right=False)
        dsp = ej["desplazados"][j]
        vec(a, b, dsp["cortes"], f"m3: cortes del corrimiento {j}", T8)
        enteros(a, cn, dsp["conteos"], f"m3: conteos del corrimiento {j}")
        a.igual(cn.sum(), dsp["suma"], f"m3: el corrimiento {j} cuenta los 8")
        a.cierto(dsp["j"] == j and abs(dsp["desplazamiento"] - j * da) <= T8,
                 f"m3: el corrimiento {j} se desplaza j·δ")
        fj[:, j] = cn[find_interval(pts, b) - 1] / (len(xa) * ha)
    vec(a, fj, ej["f_j"], "m3: las f_j de la tabla a mano", T8)
    vec(a, fj.mean(axis=1), ej["f_ash"], "m3: el ASH a mano en 3, 5, 7 y 9", T8)
    vec(a, ash(xa, ha, ma, pts), fj.mean(axis=1), "m3: y la función ash() da lo mismo", 1e-12)

    ms = np.asarray(m["varianza"]["m"], float)
    vec(a, (2 * ms ** 2 + 1) / (3 * ms ** 2), m["varianza"]["factor"],
        "m3: factor de varianza (2m²+1)/(3m²)", T8)
    a.igual(2 / 3, m["varianza"]["limite"], "m3: su límite, 2/3", tol=T8)

    E = ctx["E"]
    tr = m["triangular"]
    h = tr["h"]
    a.igual(h, 0.6, "m3: el ancho del triangular")
    g = r_seq_by(E.min() - 1, E.max() + 1, 0.005)
    a.igual(tr["paso_rejilla"], 0.005, "m3: el paso de la rejilla")
    tri = np.array([np.mean(np.maximum(0, 1 - np.abs((t - E) / h))) / h for t in g])
    dist = np.array([np.max(np.abs(ash(E, h, int(mm), g) - tri)) for mm in tr["m"]])
    for mm, dc, dp in zip(tr["m"], dist, tr["distancia"]):
        a.igual(dc, dp, f"m3: distancia al triangular, m={int(mm)}", tol=T8)
    vec(a, np.asarray(tr["m"]) * dist, tr["m_por_distancia"], "m3: m · distancia", T8)
    pub = np.asarray(tr["distancia"], float)
    a.cierto(bool(np.all(np.diff(pub) < 0)), "m3: la distancia baja con cada m (publicada)",
             " ".join(f"{v:.4f}" for v in pub))
    mpd = np.asarray(tr["m"], float) * pub
    a.cierto(bool(np.all(np.abs(mpd[1:] / mpd[1] - 1) < 0.35)),
             "m3: y baja como 1/m (m·distancia casi fija)",
             " ".join(f"{v:.3f}" for v in mpd))
    for mm, ap in zip(m["areas"]["m"], m["areas"]["area"]):
        a.igual(trapecio(g, ash(E, h, int(mm), g)), ap, f"m3: área del ASH, m={int(mm)}", tol=T8)

    s = m["solapadas"]
    xs = np.array([1, 2, 2.5, 3, 4, 4.5, 5, 6, 7, 7.5, 8])
    cs = np.array([3, 5, 7.0])
    ws = 3.0
    vec(a, xs, s["datos"], "m3: los datos de las ventanas solapadas", 0)
    vec(a, cs, s["centros"], "m3: los centros de las ventanas", 0)
    a.igual(ws, s["ancho"], "m3: el ancho de las ventanas")
    cnt = np.array([np.sum((xs >= c - ws / 2) & (xs <= c + ws / 2)) for c in cs])
    enteros(a, cnt, s["conteos"], "m3: los conteos de las tres ventanas")
    a.igual(cnt.sum(), s["contribuciones"], "m3: las contribuciones suman 13")
    a.igual(cnt.sum() / len(xs), s["area"], "m3: el área de la trampa, 13/11", tol=T8)
    a.cierto(s["area"] > 1, "m3: la trampa da área mayor que 1", f"{s['area']}")
    vec(a, cnt / (len(xs) * ws), s["densidades"], "m3: las densidades de las ventanas", T8)
    fuera = int(sum(all(abs(v - c) > ws / 2 for c in cs) for v in xs))
    a.igual(fuera, s["sin_ventana"], "m3: los datos sin ventana")


def kennedy_caja(ken):
    """Reconstruye la caja de 2 km del módulo 4 desde las 262 sedes."""
    kx = ken[:, 0] / 1000
    ky = ken[:, 1] / 1000
    d = np.sqrt((kx[:, None] - kx[None, :]) ** 2 + (ky[:, None] - ky[None, :]) ** 2)
    vec600 = (d < 0.6).sum(axis=1)
    c0 = int(np.argmax(vec600))
    lado = 2.0
    ax = kx - (kx[c0] - lado / 2)
    ay = ky - (ky[c0] - lado / 2)
    return ax, ay


def modulo4(a, D, ctx):
    a.titulo("4 · Contar en una ventana: k / (nV)")
    m = D["m4"]
    f0 = float(norm.pdf(0))
    a.igual(f0, m["f0"], "m4: f(0) de la N(0, 1)", tol=T8)
    # La rejilla del simulador lleva dentro, exactos, los tres anchos que
    # cita la prosa (revisión 2).
    V = np.unique(np.concatenate([np.round(np.exp(r_seq_len(math.log(0.05), math.log(4), 61)), 10),
                                  [0.2, 2.0]]))
    vec(a, V, m["V"], "m4: la rejilla de ventanas", T8)
    ns = [25, 100, 400, 1600]
    enteros(a, ns, m["ns"], "m4: los cuatro tamaños de muestra")
    p = norm.cdf(V / 2) - norm.cdf(-V / 2)
    vopt = []
    for nn, bloque in zip(ns, m["por_n"]):
        media = p / V
        sdv = np.sqrt(p * (1 - p) / nn) / V
        ecm = (media - f0) ** 2 + sdv ** 2
        a.igual(nn, bloque["n"], f"m4: n = {nn}, el bloque")
        vec(a, media, bloque["media"], f"m4: n = {nn}, E f̂ exacta", T8)
        vec(a, sdv, bloque["sd"], f"m4: n = {nn}, sd de f̂ (binomial)", T8)
        vec(a, ecm, bloque["ecm"], f"m4: n = {nn}, el ECM", T8)
        vec(a, (1 - p) ** nn, bloque["vacia"], f"m4: n = {nn}, P(ventana vacía)", T8)
        # El mejor V EXACTO, por un minimizador propio (Brent, sin R).
        def ecm_v(Vv, nn=nn):
            pp = norm.cdf(Vv / 2) - norm.cdf(-Vv / 2)
            return (pp / Vv - f0) ** 2 + pp * (1 - pp) / (nn * Vv * Vv)
        vo = brent_fmin(0.05, 4.0, ecm_v, 1e-10)
        a.igual(vo, bloque["v_opt"], f"m4: n = {nn}, la ventana óptima exacta", tol=1e-6)
        a.igual(ecm_v(vo), bloque["ecm_min"], f"m4: n = {nn}, el ECM mínimo", tol=T8)
        a.cierto(ecm_v(vo) <= ecm.min() + 1e-12, f"m4: n = {nn}, no lo mejora ningún nodo de la rejilla")
        vopt.append(bloque["v_opt"])
    a.cierto(all(np.diff(vopt) < 0), "m4: la ventana óptima se encoge al crecer n",
             " ".join(f"{v:.3f}" for v in vopt))
    raz = np.asarray(vopt[:-1]) / np.asarray(vopt[1:])
    a.igual(raz.mean(), m["razon_v"], "m4: el cociente medio entre óptimos", tol=T8)
    a.igual(4 ** 0.2, m["cuatro_quinta"], "m4: 4^(1/5)", tol=T8)
    a.cierto(bool(np.all(np.abs(raz / 4 ** 0.2 - 1) < 0.02)), "m4: el mejor V baja como n^(-1/5)",
             " ".join(f"{v:.3f}" for v in raz))
    a.igual(vopt[1] / math.sqrt(12), m["v_opt_sd_n100"], "m4: la desviación de la mejor caja, n=100", tol=T8)
    # En x = 0.5, con pendiente: centrada contra casilla (segunda pasada).
    pe = m["pendiente"]
    xp = pe["x"]

    def ecm_cv(Vv, nn, centrada):
        pp = (norm.cdf(xp + Vv / 2) - norm.cdf(xp - Vv / 2)) if centrada else (norm.cdf(xp + Vv) - norm.cdf(xp))
        return (pp / Vv - norm.pdf(xp)) ** 2 + pp * (1 - pp) / (nn * Vv * Vv)
    for clave, cen in (("centrada", True), ("casilla", False)):
        vo = [brent_fmin(0.01, 4.0, lambda Vv, nn=nn: ecm_cv(Vv, nn, cen), 1e-10) for nn in ns]
        vec(a, vo, pe[clave], f"m4: en x = 0.5, el mejor ancho ({clave})", 1e-6)
        rz = float(np.mean(np.asarray(vo[:-1]) / np.asarray(vo[1:])))
        a.igual(rz, pe["razon_" + clave], f"m4: en x = 0.5, su razón ({clave})", tol=1e-6)
    a.igual(4 ** (1 / 3), pe["cuatro_tercio"], "m4: 4^(1/3)", tol=T8)
    a.cierto(abs(pe["razon_centrada"] / 4 ** 0.2 - 1) < 0.03 and pe["razon_casilla"] > pe["razon_centrada"] + 0.1,
             "m4: con pendiente, centrar cambia la tasa")

    def una(Vv, nn):
        pp = norm.cdf(Vv / 2) - norm.cdf(-Vv / 2)
        return dict(p=pp, media=pp / Vv, sesgo=pp / Vv - f0,
                    sd=math.sqrt(pp * (1 - pp) / nn) / Vv, vacia=(1 - pp) ** nn,
                    esperados=nn * pp)
    for clave, Vv in (("v_peq", 0.2), ("v_gra", 2.0), ("v_min", 0.05)):
        c = una(Vv, 100)
        b = m[clave]
        a.igual(b["V"], Vv, f"m4: {clave}, la ventana")
        for k in ("p", "media", "sesgo", "sd", "vacia", "esperados"):
            a.igual(c[k], b[k], f"m4: {clave}, {k}", tol=T8)
    a.cierto(abs(m["v_peq"]["sesgo"]) < m["v_peq"]["sd"] and
             abs(m["v_gra"]["sesgo"]) > m["v_gra"]["sd"],
             "m4: V pequeña: manda la varianza; grande: el sesgo")
    dd = np.asarray(m["dimension"]["d"], float)
    vec(a, 4 / (4 + dd), m["dimension"]["exponente"], "m4: el exponente 4/(4+d)", T8)
    vec(a, 2 ** ((4 + dd) / 4), m["dimension"]["datos_para_mitad"],
        "m4: datos para la mitad, 2^((4+d)/4)", T8)
    vec(a, 0.1 ** (1 / dd), m["dimension"]["lado_10pct"], "m4: el lado que encierra el 10 %", T8)

    # --- La figura del plano, contra TODAS las sedes de Kennedy ---------
    pl = m["plano"]
    ax, ay = kennedy_caja(ctx["ken"])
    vis = (ax >= -0.5) & (ax <= 2.5) & (ay >= -0.5) & (ay <= 2.5)
    a.igual(int(vis.sum()), pl["n"], "m4: las sedes que se ven en la caja")
    dentro = vis & (ax >= 0) & (ax <= 2) & (ay >= 0) & (ay <= 2)
    a.igual(int(dentro.sum()), pl["n_dentro"], "m4: las sedes dentro del cuadro")
    a.igual(int(vis.sum() - dentro.sum()), pl["n_margen"], "m4: las sedes del margen")
    vec(a, np.round(ax[vis], 4), pl["x"], "m4: sus x (km desde la esquina)", 6e-5)
    vec(a, np.round(ay[vis], 4), pl["y"], "m4: sus y (km desde la esquina)", 6e-5)
    gx = r_seq_by(0.5, 1.5, 0.05)
    cx = np.tile(gx, len(gx))                        # expand.grid: x corre primero
    cy = np.repeat(gx, len(gx))
    dist = np.sqrt((ax[None, :] - cx[:, None]) ** 2 + (ay[None, :] - cy[:, None]) ** 2)
    cuenta = (dist <= 0.3).sum(axis=1)
    dk = np.sort(dist, axis=1)[:, 3]
    s_denso = int(np.lexsort((np.arange(len(dk)), dk, -cuenta))[0])
    s_ralo = int(np.argmax(dk))
    s_medio = int(np.argmin(np.abs(dk - np.median(dk))))
    a.cierto(len({s_denso, s_medio, s_ralo}) == 3, "m4: los tres sitios son distintos")
    for nombre, i, sp in zip(("denso", "medio", "ralo"), (s_denso, s_medio, s_ralo), pl["sitios"]):
        a.igual(cx[i], sp["x"], f"m4: sitio {nombre}, x", tol=6e-5)
        a.igual(cy[i], sp["y"], f"m4: sitio {nombre}, y", tol=6e-5)
        a.igual(cuenta[i], sp["parzen_conteo"], f"m4: sitio {nombre}, sedes a ≤ 0.3 km")
        a.igual(cuenta[i] / (math.pi * 0.09), sp["parzen_intensidad"],
                f"m4: sitio {nombre}, intensidad de Parzen", tol=6e-5)
        a.igual(dk[i], sp["knn_radio"], f"m4: sitio {nombre}, radio del 4.º vecino", tol=6e-5)
        a.igual(4 / (math.pi * dk[i] ** 2), sp["knn_intensidad"],
                f"m4: sitio {nombre}, intensidad k-NN", tol=6e-5)
        # Qué sedes rellena la figura: índices en la lista visible.
        dv = np.sqrt((ax[vis] - cx[i]) ** 2 + (ay[vis] - cy[i]) ** 2)
        lista = lambda v: v if isinstance(v, list) else [v]  # noqa: E731
        a.cierto(sorted(np.flatnonzero(dv <= 0.3).tolist()) == sorted(lista(sp["parzen_dentro"])),
                 f"m4: sitio {nombre}, las sedes que cuenta el círculo fijo")
        a.cierto(sorted(np.argsort(dv, kind="stable")[:4].tolist()) == sorted(lista(sp["knn_dentro"])),
                 f"m4: sitio {nombre}, sus cuatro vecinas")
    r = [s["knn_radio"] for s in pl["sitios"]]
    a.cierto(r[0] < r[1] < r[2], "m4: el radio k-NN crece de denso a ralo", str(r))
    a.cierto(pl["sitios"][0]["parzen_conteo"] > pl["sitios"][2]["parzen_conteo"],
             "m4: la ventana fija cuenta más en el sitio denso")
    a.cierto(pl["radio_km"] == 0.3 and pl["k"] == 4 and pl["lado_km"] == 2 and pl["margen_km"] == 0.5,
             "m4: radio 0.3, k = 4, caja de 2 y margen 0.5 km")
    a.cierto(m["x0"] == 0 and m["n_contraste"] == 100, "m4: x₀ = 0 y el contraste con n = 100")


def modulo5(a, D, ctx):
    a.titulo("5 · El estimador de núcleo: una loma por punto")
    m = D["m5"]

    def fpar(x, datos, h, K):
        return np.array([np.mean(K((t - datos) / h)) / h for t in np.atleast_1d(x)])
    ule = lambda u: np.where(np.abs(u) <= 1, 0.5, 0.0)        # noqa: E731
    ult = lambda u: np.where(np.abs(u) < 1, 0.5, 0.0)         # noqa: E731
    x15 = np.arange(1, 6, dtype=float)
    u = m["uniforme"]
    vec(a, fpar(x15, x15, 1, ule), u["f"], "m5: el uniforme sobre 1..5", T8)
    vec(a, ule(3 - x15), u["terminos_x3"], "m5: los términos en x = 3", 0)
    a.igual(ule(3 - x15).sum(), u["suma_x3"], "m5: la suma de los términos en x = 3")
    a.cierto(u["f"][0] < u["f"][2], "m5: en el borde la ventana recoge menos")
    x5 = np.array([2, 3, 4, 5, 7], float)
    fr = m["frontera"]
    a.igual(fpar(4, x5, 1, ule)[0], fr["le"], "m5: con |u| ≤ 1", tol=T8)
    a.igual(fpar(4, x5, 1, ult)[0], fr["lt"], "m5: con |u| < 1", tol=T8)
    a.cierto(fr["le"] != fr["lt"], "m5: la frontera cambia la cifra")
    gs = m["gaussiano"]
    tg = phi(4 - x5)
    vec(a, tg, gs["terminos"], "m5: los términos gaussianos en x = 4", T8)
    a.igual(tg.sum(), gs["suma"], "m5: la suma de los términos gaussianos", tol=T8)
    a.igual(tg.mean(), gs["f"], "m5: f̂(4) gaussiano", tol=T8)
    for fila in m["tabla"]:
        h = fila["h"]
        a.igual(fpar(4, x5, h, ule)[0], fila["uniforme"], f"m5: tabla, uniforme con h={h:g}", tol=T8)
        a.igual(fpar(4, x5, h, phi)[0], fila["gaussiano"], f"m5: tabla, gaussiano con h={h:g}", tol=T8)
    rj = m["rejilla"]
    g = r_seq_len(rj["desde"], rj["hasta"], rj["puntos"])
    md = [modas_secuencia(kde_gauss(x5, g, h)) for h in m["modas"]["h"]]
    enteros(a, md, m["modas"]["modas"], "m5: las modas con h = 0.3, 0.5, 1 y 2")
    enteros(a, [5, 3, 1, 1], m["modas"]["modas"], "m5: y son 5, 3, 1 y 1, como dice la prosa")
    # Los tramos del simulador: mismos anchos (0.20 a 2.50) y misma rejilla.
    H5 = np.round(r_seq_by(0.2, 2.5, 0.05), 2)
    md5 = [modas_secuencia(kde_gauss(x5, g, h)) for h in H5]
    tramos, i = [], 0
    while i < len(md5):
        j = i
        while j + 1 < len(md5) and md5[j + 1] == md5[i]:
            j += 1
        tramos.append((md5[i], H5[i], H5[j]))
        i = j + 1
    pub = [(t["modas"], t["desde"], t["hasta"]) for t in m["tramos"]]
    a.cierto(len(pub) == len(tramos) and all(p[0] == c[0] and abs(p[1] - c[1]) < 1e-9 and abs(p[2] - c[2]) < 1e-9
                                             for p, c in zip(pub, tramos)),
             "m5: los tramos de modas según h", str(tramos))
    enteros(a, [5, 3, 2, 1], [t[0] for t in tramos], "m5: pasan por 5, 3, 2 y 1")
    d2 = donde_modas(g, kde_gauss(x5, g, tramos[2][1]))
    a.cierto(len(d2) == 2 and 2 < d2[0] < 5 and abs(d2[1] - 7) < 0.5,
             "m5: con dos modas, el grupo de 2 a 5 y el 7 aislado", str(d2))
    cj = m["caja"]
    a.igual(1 / math.sqrt(3), cj["sd_h1"], "m5: la caja de h = 1 tiene sd 1/√3", tol=T8)
    a.igual(math.sqrt(3), cj["semiancho_sd1"], "m5: semiancho √3 para sd 1", tol=T8)
    a.igual(fpar(4, x5, math.sqrt(3), ule)[0], cj["f_sd1"], "m5: la caja a la misma sd en x = 4", tol=T8)
    a.igual(0.3, m["h_inicial"], "m5: el simulador arranca en h = 0.3")


def modulo6(a, D, ctx):
    a.titulo("6 · Los núcleos, y la escala de density()")
    m = D["m6"]
    nucs = {
        "gaussiano": (lambda u: phi(u), np.inf),
        "epanechnikov": (lambda u: 0.75 * (1 - u * u), 1.0),
        "uniforme": (lambda u: 0.5 + 0 * u, 1.0),
        "triangular": (lambda u: 1 - abs(u), 1.0),
        "biweight": (lambda u: (15 / 16) * (1 - u * u) ** 2, 1.0),
        "triweight": (lambda u: (35 / 32) * (1 - u * u) ** 3, 1.0),
    }
    calc = {}
    for nm, (K, lim) in nucs.items():
        mu2 = integrate.quad(lambda u: u * u * K(u), -lim, lim, limit=200)[0]
        RK = integrate.quad(lambda u: K(u) ** 2, -lim, lim, limit=200)[0]
        ar = integrate.quad(K, -lim, lim, limit=200)[0]
        calc[nm] = (mu2, RK, ar)
    ref = calc["epanechnikov"][1] * math.sqrt(calc["epanechnikov"][0])
    # Las formas cerradas de la tabla de núcleos (Wand y Jones, tabla 2.1).
    literatura = {"gaussiano": (1, RK_GAUSS), "epanechnikov": (1 / 5, 3 / 5),
                  "uniforme": (1 / 3, 1 / 2), "triangular": (1 / 6, 2 / 3),
                  "biweight": (1 / 7, 5 / 7), "triweight": (1 / 9, 350 / 429)}
    for nm, (mu2, RK, ar) in calc.items():
        p = por(m["nucleos"], "nombre", nm)
        a.igual(mu2, p.get("mu2"), f"m6: {nm}, μ₂(K)", tol=T8)
        a.igual(RK, p.get("RK"), f"m6: {nm}, R(K)", tol=T8)
        a.igual(ar, p.get("area"), f"m6: {nm}, área 1", tol=T8)
        a.igual(literatura[nm][0], p.get("mu2"), f"m6: {nm}, μ₂ de la literatura", tol=T8)
        a.igual(literatura[nm][1], p.get("RK"), f"m6: {nm}, R(K) de la literatura", tol=T8)
        a.igual(ref / (RK * math.sqrt(mu2)), p.get("eficiencia"), f"m6: {nm}, eficiencia", tol=T8)
        if nm == "gaussiano":
            a.cierto(p.get("soporte_por_sigma") is None, "m6: el gaussiano no tiene soporte")
        else:
            a.igual(1 / math.sqrt(mu2), p.get("soporte_por_sigma"), f"m6: {nm}, soporte/σ", tol=T8)
            a.igual(1 / mu2, p.get("h2_sobre_sigma2"), f"m6: {nm}, h²/σ²", tol=T8)
        a.igual((RK * math.sqrt(mu2)) / ref, p.get("datos_para_igualar"),
                f"m6: {nm}, datos para igualar al Epanechnikov", tol=T8)
        a.igual(((RK * math.sqrt(mu2)) / ref) ** 0.8, p.get("error_relativo"),
                f"m6: {nm}, error con los mismos datos", tol=T8)
        a.igual(RK * math.sqrt(mu2), p.get("RK_sd1"), f"m6: {nm}, R(K) a sd 1", tol=T8)
    a.igual(0.9512, por(m["nucleos"], "nombre", "gaussiano").get("eficiencia"),
            "m6: eficiencia gaussiana 0.9512 (Wand y Jones)", tol=1e-4)
    efs = {x["nombre"]: x["eficiencia"] for x in m["nucleos"]}
    a.cierto(max(efs, key=efs.get) == "epanechnikov", "m6: el Epanechnikov es el más eficiente")
    for nm, nd in (("epanechnikov", "epanechnikov"), ("uniforme", "rectangular"),
                   ("triangular", "triangular"), ("biweight", "biweight")):
        a.igual(por(m["nucleos"], "nombre", nm).get("soporte_por_sigma"),
                m["density_soporte"][nd], f"m6: density() y 1/√μ₂: {nd}", tol=T8)

    # El Epanechnikov de R con bw = 1 todavía pesa en x = 2: su soporte llega
    # a √5. Por la forma cerrada y por density() portada (n = 8192).
    exacto = 0.75 * (1 - 4 / 5) / math.sqrt(5)
    a.igual(exacto, m["epa_bw1_en_2_exacto"], "m6: Epanechnikov de R en x = 2, exacto", tol=T8)
    a.igual(float(r_density([0.0], 1.0, 8192, -3.0, 3.0, nucleo="epanechnikov", xout=2.0)),
            m["epa_bw1_en_2"], "m6: y lo que da density() en x = 2", tol=T8)
    a.cierto(abs(m["epa_bw1_en_2"] - exacto) < 2e-4, "m6: density() y la forma cerrada casi coinciden")
    pc = m["pregunta_caja"]
    a.igual(math.sqrt(3) * pc["bw"], pc["semiancho"], "m6: la caja de la pregunta, √3·bw", tol=T8)

    def radial(k):
        num = integrate.quad(lambda r: r ** 3 * k(r), 0, 1)[0]
        den = integrate.quad(lambda r: r * k(r), 0, 1)[0]
        return 1 / (num / den / 2)
    for nm, k, v in (("epanechnikov", lambda r: 1 - r * r, 6), ("cuartico", lambda r: (1 - r * r) ** 2, 8),
                     ("disco", lambda r: 1.0, 4)):
        a.igual(radial(k), m["plano"][nm], f"m6: en el plano, h²/σ² del {nm}", tol=T8)
        a.igual(v, m["plano"][nm], f"m6: y vale {v} ({nm})", tol=T8)

    def compara(x, pub, et, tol):
        bw = bw_nrd0(x)
        g = r_seq_len(x.min() - 3 * bw, x.max() + 3 * bw, 2048)
        dg, dr, de = (kde_r(x, g, bw, k) for k in ("gaussian", "rectangular", "epanechnikov"))
        a.igual(len(x), pub["n"], f"m6: {et}, n")
        a.igual(bw, pub["bw"], f"m6: {et}, bw.nrd0", tol=tol)
        a.igual(dg.max(), pub["max_gauss"], f"m6: {et}, máximo gaussiano", tol=tol)
        a.igual(np.abs(dg - dr).max(), pub["dif_rect"], f"m6: {et}, dif. con la caja", tol=tol)
        a.igual(np.abs(dg - de).max(), pub["dif_epan"], f"m6: {et}, dif. con Epanechnikov", tol=tol)
        a.igual(modas_secuencia(dg), pub["modas_gauss"], f"m6: {et}, modas gaussianas")
        a.igual(modas_secuencia(dr), pub["modas_rect"], f"m6: {et}, modas de la caja")
        a.igual(modas_secuencia(de), pub["modas_epan"], f"m6: {et}, modas Epanechnikov")
        a.igual(math.sqrt(3) * bw, pub["caja_semiancho"], f"m6: {et}, semiancho de la caja", tol=tol)
        a.igual(1 / (2 * math.sqrt(3) * bw), pub["caja_altura_sobre_n"],
                f"m6: {et}, altura de la caja", tol=tol)
    tri = np.asarray(m["muestra_trimodal"], float)
    t = m["trimodal"]
    a.igual(t["n1"] + t["n2"] + t["n3"], len(tri), "m6: trimodal, 500 + 200 + 50")
    compara(tri, t, "trimodal", T6)
    compara(ctx["uni"], m["unimodal"], "unimodal", 1e-6)
    a.cierto(t["modas_gauss"] == 3, "m6: la trimodal gaussiana tiene tres modas")
    a.cierto(t["modas_rect"] > t["modas_gauss"], "m6: la caja deja más máximos que la gaussiana",
             f"{t['modas_rect']} contra {t['modas_gauss']}")
    for et, pub in (("unimodal", m["unimodal"]), ("trimodal", t)):
        a.cierto(pub["dif_rect"] < 0.2 * pub["max_gauss"],
                 f"m6: {et}, con el mismo bw la caja cambia poco")
    u = m["unimodal"]
    a.cierto(u["modas_gauss"] == 1 and u["modas_epan"] > 1 and u["modas_rect"] > u["modas_epan"],
             "m6: unimodal, los núcleos con soporte añaden máximos",
             f"{u['modas_gauss']}, {u['modas_epan']}, {u['modas_rect']}")
    # Los dos modos del simulador: misma sd o el soporte del Epanechnikov de R.
    bw = t["bw"]
    g = r_seq_len(tri.min() - 3 * bw, tri.max() + 3 * bw, 2048)
    ref_t = kde_r(tri, g, bw, "gaussian")
    esc = {"rectangular": math.sqrt(3), "triangular": math.sqrt(6), "biweight": math.sqrt(7)}
    ms = m["mismo_soporte"]
    for clave, nd in (("caja", "rectangular"), ("triangular", "triangular"), ("biweight", "biweight")):
        bs = math.sqrt(5) * bw / esc[nd]
        a.igual(np.abs(kde_r(tri, g, bw, nd) - ref_t).max(), ms[clave]["dif_misma_sd"],
                f"m6: {clave}, dif. a la misma sd", tol=T6)
        a.igual(bs, ms[clave]["sd_mismo_soporte"], f"m6: {clave}, sd al mismo soporte", tol=T6)
        a.igual(np.abs(kde_r(tri, g, bs, nd) - ref_t).max(), ms[clave]["dif_mismo_soporte"],
                f"m6: {clave}, dif. al mismo soporte", tol=T6)
    a.cierto(ms["caja"]["dif_mismo_soporte"] > 2 * ms["caja"]["dif_misma_sd"]
             and ms["biweight"]["dif_mismo_soporte"] > 2 * ms["biweight"]["dif_misma_sd"]
             and ms["triangular"]["dif_mismo_soporte"] < 2 * ms["triangular"]["dif_misma_sd"],
             "m6: al mismo soporte se alejan la caja y el biweight, no el triangular")


def modulo7(a, D, ctx):
    a.titulo("7 · k vecinos: el radio se adapta")
    m = D["m7"]
    ed = m["edades"]
    xe = np.array([20, 23, 25, 29, 31, 35, 40], float)
    de = np.sort(np.abs(xe - 30))
    vec(a, de, ed["distancias"], "m7: edades, las distancias a 30", 0)
    a.igual(de[2], ed["d_k"], "m7: edades, d₃")
    a.igual(2 * de[2], ed["V"], "m7: edades, V = 2d₃")
    a.igual(3 / (2 * 7 * de[2]), ed["f"], "m7: edades, f̂ = k/(2nd₃)", tol=T8)
    dentro = int(np.sum(np.abs(xe - 30) <= de[2]))
    a.igual(dentro, ed["dentro"], "m7: edades, los datos dentro del radio")
    a.cierto(dentro > 3, "m7: edades, hay un empate en el 3.er vecino", f"{dentro} > 3")
    a.igual(dentro / (7 * 2 * de[2]), ed["balloon"], "m7: edades, el «globo»", tol=T8)

    ig = m["ingresos"]
    ing = np.array([35, 42, 47, 53, 57, 61, 64, 68, 73, 75, 78, 82, 85, 90, 94, 100, 103,
                    107, 110, 115], float)
    vec(a, ing, ig["datos"], "m7: los ingresos", 0)
    r3 = np.sort(np.abs(ing - 80))[2]
    a.igual(r3, ig["radio"], "m7: ingresos, radio del 3.er vecino")
    a.igual(3 / (2 * 20 * r3), ig["knn"], "m7: ingresos, k-NN en 80", tol=T8)
    a.igual(sd(ing), ig["sd"], "m7: ingresos, sd", tol=T8)
    a.igual(iqr(ing) / 1.34, ig["iqr_134"], "m7: ingresos, IQR/1.34", tol=T8)
    h = bw_nrd(ing)
    a.igual(h, ig["h"], "m7: ingresos, h de bw.nrd", tol=T8)
    a.igual(bw_nrd0(ing), ig["h_nrd0"], "m7: ingresos, bw.nrd0", tol=T8)
    epa = lambda u: np.where(np.abs(u) <= 1, 0.75 * (1 - u * u), 0.0)   # noqa: E731
    a.igual(np.mean(epa((80 - ing) / h)) / h, ig["epa_soporte"], "m7: Epanechnikov, h de soporte", tol=T8)
    a.igual(np.mean(phi((80 - ing) / h)) / h, ig["gauss"], "m7: gaussiano en 80", tol=T8)
    ar = math.sqrt(5) * h
    a.igual(np.mean(epa((80 - ing) / ar)) / ar, ig["epa_density"],
            "m7: Epanechnikov, convención de R", tol=T8)
    a.igual(ar, ig["epa_density_semiancho"], "m7: su semiancho √5·bw", tol=T8)
    a.cierto(abs(ig["epa_density"] - ig["epa_soporte"]) > 1e-4,
             "m7: bw o soporte: dos densidades distintas")
    vec(a, np.sort(np.abs(ing - 80))[:4], ig["distancias_4"], "m7: ingresos, las cuatro distancias", 0)
    a.igual(int(np.sum(np.abs(ing - 80) <= r3)), ig["dentro"], "m7: ingresos, los datos en la ventana")
    a.cierto(ig["dentro"] > ig["k"], "m7: ingresos, la ventana encierra más que k")
    areas = []
    for w in ig["areas"]:
        g = r_seq_len(w["desde"], w["hasta"], 20001)
        ac = trapecio(g, knn_curva(ing, g, 3))
        a.igual(ac, w["area"], f"m7: área del k-NN en [{w['desde']}, {w['hasta']}]", tol=T8)
        areas.append(w["area"])
    a.cierto(all(np.diff(areas) > 0), "m7: el área del k-NN crece sin parar",
             " ".join(f"{v:.3f}" for v in areas))

    mz = m["mezcla"]
    mez = np.asarray(mz["muestra"], float)
    a.igual(len(mez), mz["n"], "m7: mezcla, n")
    a.igual(mez.min(), mz["rejilla"]["desde"], "m7: mezcla, la rejilla empieza", tol=T6)
    a.igual(mez.max(), mz["rejilla"]["hasta"], "m7: mezcla, la rejilla acaba", tol=T6)
    g = r_seq_len(mez.min(), mez.max(), 1000)
    fv = lambda x: 0.5 * norm.pdf(x, 5, 1) + 0.5 * norm.pdf(x, 10, 1.5)     # noqa: E731
    a.cierto(mz["valle_x"] == 7.5 and mz["hist_pide"] == 30, "m7: el valle en 7.5 y hist(breaks = 30)")
    modas = []
    for blq in mz["por_k"]:
        k = int(blq["k"])
        y = knn_curva(mez, g, k)
        a.igual(modas_secuencia(y), blq["modas"], f"m7: mezcla, modas con k={k}")
        a.igual(trapecio(g, y), blq["area"], f"m7: mezcla, área con k={k}", tol=1e-5)
        # k/(2n·d_k): con la muestra a seis decimales d_k se mueve hasta 1e-6,
        # y eso es un error RELATIVO de 1e-6/d_k = 2n·f/k · 1e-6. Donde el
        # vecino está muy cerca (k = 3, en el pico) llega a 3e-4. El valle se
        # evalúa EN 7.5, no en el nodo más cercano (revisión 2).
        en_valle = float(knn_curva(mez, np.array([mz["valle_x"]]), k)[0])
        for clave, v, et in (("f_valle", en_valle, "el valle"), ("maximo", y.max(), "el máximo")):
            a.cerca(v, blq[clave], f"m7: mezcla, {et} con k={k}",
                    rel=1e-6 * 2 * len(mez) * v / k + 1e-8)
        modas.append(blq["modas"])
    a.cierto(all(np.diff(modas) <= 0), "m7: más vecinos, menos modas", str(modas))
    a.cierto(modas[-1] > 10, "m7: aun con k = 80 quedan decenas de dientes", str(modas[-1]))
    a.igual(trapecio(g, fv(g)), mz["area_verdad"], "m7: el área de la verdad", tol=1e-6)
    a.igual(fv(mz["valle_x"]), mz["f_valle_verdad"], "m7: la verdad en el valle", tol=T8)
    br = r_pretty(mez.min(), mez.max(), int(mz["hist_pide"]), 1)
    cnt = r_conteos(mez, br, right=True)
    a.igual(len(br) - 1, mz["hist_clases"], "m7: hist(breaks = 30): sus clases")
    a.igual(modas_secuencia(cnt / (len(mez) * np.diff(br))), mz["hist_modas"],
            "m7: hist(breaks = 30): sus modas")


def modulo8(a, D, ctx):
    a.titulo("8 · Sesgo, varianza y MISE, en forma cerrada")
    m = D["m8"]
    n = 100
    a.igual(m["n"], n, "m8: n")
    a.igual(m["x0"], 0, "m8: el punto x₀ = 0")

    def Ef(x, h):
        return norm.pdf(x, 0, np.sqrt(1 + h * h))

    def Vf(x, h):
        ek2 = norm.pdf(x, 0, np.sqrt(1 + h * h / 2)) / (2 * math.sqrt(math.pi) * h)
        return (ek2 - Ef(x, h) ** 2) / n
    hs = r_seq_by(0.05, 1.50, 0.01)
    vec(a, hs, m["h"], "m8: la rejilla de h", 1e-12)
    s2 = (Ef(0, hs) - norm.pdf(0)) ** 2
    va = Vf(0, hs)
    vec(a, s2, m["sesgo2"], "m8: el sesgo² en x = 0", T8)
    vec(a, va, m["var"], "m8: la varianza en x = 0", T8)
    vec(a, s2 + va, m["ecm"], "m8: el ECM en x = 0", T8)
    a.igual(hs[int(np.argmin(s2 + va))], m["h_ecm"], "m8: el h del ECM mínimo", tol=1e-12)
    a.igual((s2 + va).min(), m["ecm_min"], "m8: el ECM mínimo", tol=T8)
    ha = (4 / (3 * n)) ** (1 / 5)
    a.igual(ha, m["h_amise"], "m8: h_AMISE = (4/(3n))^(1/5)", tol=T8)
    a.igual((4 / 3) ** (1 / 5), m["constante_amise"], "m8: la constante (4/3)^(1/5)", tol=T8)

    def mise(h):
        return RK_GAUSS * (1 / (n * h) + (1 - 1 / n) / math.sqrt(1 + h * h)
                           - 2 ** 1.5 / math.sqrt(2 + h * h) + 1)
    r = optimize.minimize_scalar(mise, bounds=(0.05, 1.5), method="bounded",
                                 options={"xatol": 1e-11})
    a.igual(r.x, m["h_mise"], "m8: el h del MISE exacto", tol=1e-7)
    a.igual(mise(r.x), m["mise_min"], "m8: el MISE mínimo", tol=T8)
    a.igual(mise(ha), m["mise_en_amise"], "m8: el MISE en h_AMISE", tol=T8)
    # La forma cerrada, por OTRO camino: integrar sesgo² + varianza punto a punto.
    num = integrate.quad(lambda x: (Ef(x, r.x) - norm.pdf(x)) ** 2 + Vf(x, r.x),
                         -np.inf, np.inf, epsabs=1e-13)[0]
    a.igual(num, m["mise_min"], "m8: el MISE mínimo, integrado punto a punto", tol=T8)
    a.cierto(m["h_ecm"] < m["h_amise"] < m["h_mise"], "m8: h del ECM < h_AMISE < h del MISE",
             f"{m['h_ecm']} < {m['h_amise']:.4f} < {m['h_mise']:.4f}")
    asn = m["asintotica"]
    x, h = asn["x"], asn["h"]
    a.igual(Ef(x, h) - norm.pdf(x), asn["sesgo_exacto"], "m8: el sesgo exacto en x = 0.5", tol=T8)
    a.igual(h * h / 2 * (x * x - 1) * norm.pdf(x), asn["sesgo_formula"],
            "m8: el sesgo asintótico h²f''/2", tol=T8)
    a.igual(Vf(x, h), asn["var_exacta"], "m8: la varianza exacta en x = 0.5", tol=T8)
    a.igual(RK_GAUSS * norm.pdf(x) / (n * h), asn["var_formula"],
            "m8: la varianza asintótica R(K)f/(nh)", tol=T8)
    a.igual(2 ** 1.5, m["tasas"]["hist_datos_para_mitad"], "m8: histograma: 2^(3/2)", tol=T8)
    a.igual(2 ** 1.25, m["tasas"]["kde_datos_para_mitad"], "m8: núcleo: 2^(5/4)", tol=T8)
    a.cierto(len(m["nube"]) == 30 and all(len(v) == n for v in m["nube"]),
             "m8: la nube son 30 muestras de 100")
    # Lo que añadió la revisión 2: el mejor ancho en tres puntos, el cruce
    # de sesgo² y varianza, la planitud del MISE y el error del promedio de 30.
    for xx, hp in zip(m["h_ecm_x"]["x"], m["h_ecm_x"]["h"]):
        ho = brent_fmin(0.05, 3.0, lambda hh, xx=xx: (Ef(xx, hh) - norm.pdf(xx)) ** 2 + Vf(xx, hh), 1e-10)
        a.igual(ho, hp, f"m8: el mejor h puntual en x = {xx:g}", tol=1e-6)
    a.cierto(all(np.diff(m["h_ecm_x"]["h"]) > 0), "m8: el mejor h puntual crece hacia x = 1")
    cr = optimize.brentq(lambda hh: (Ef(0, hh) - norm.pdf(0)) ** 2 - Vf(0, hh), 0.1, 1.4, xtol=1e-12)
    a.igual(cr, m["cruce"], "m8: donde se cortan sesgo² y varianza", tol=1e-7)
    io = int(np.argmin(s2 + va))
    a.igual(s2[io], m["en_optimo"]["sesgo2"], "m8: el sesgo² en el óptimo", tol=T8)
    a.igual(va[io], m["en_optimo"]["var"], "m8: la varianza en el óptimo", tol=T8)
    a.cierto(m["cruce"] > m["h_ecm"] and m["en_optimo"]["sesgo2"] < m["en_optimo"]["var"],
             "m8: el óptimo no está en el cruce")
    a.igual(100 * (mise(ha) / mise(r.x) - 1), m["mise_pct_amise"], "m8: cuánto cuesta h_AMISE (%)", tol=1e-6)
    vec(a, np.array([mise(hh) for hh in hs]), m["mise_h"], "m8: el MISE en la rejilla de h", T8)
    a.igual(0.4, m["nube_h"], "m8: el h de la nota del promedio")
    a.igual(Ef(0, 0.4) - norm.pdf(0), m["nube_sesgo"], "m8: el sesgo en x = 0 con h = 0.4", tol=T8)
    a.igual(2 * math.sqrt(Vf(0, 0.4) / 30), m["nube_error_mc"], "m8: dos errores del promedio de 30", tol=T8)


def modulo9(a, D, ctx):
    a.titulo("9 · Reglas de referencia normal")
    m = D["m9"]
    E = ctx["E"]
    n = len(E)
    f = m["faithful"]
    s, q = sd(E), iqr(E)
    a.igual(s, f["sd"], "m9: faithful, sd", tol=T8)
    a.igual(q, f["iqr"], "m9: faithful, IQR", tol=T8)
    a.igual(q / 1.34, f["iqr_134"], "m9: faithful, IQR/1.34", tol=T8)
    a.igual(min(s, q / 1.34), f["minimo"], "m9: faithful, el mínimo de los dos", tol=T8)
    a.igual(n ** (-1 / 5), f["n_quinta"], "m9: faithful, n^(-1/5)", tol=T8)
    a.igual(bw_nrd0(E), f["nrd0"], "m9: faithful, bw.nrd0", tol=T8)
    a.igual(bw_nrd(E), f["nrd"], "m9: faithful, bw.nrd", tol=T8)
    hr = 3.5 * s * n ** (-1 / 3)
    a.igual(hr, f["hist_rule"], "m9: faithful, 3.5·sd·n^(-1/3)", tol=T8)
    a.igual(hr / bw_nrd(E), f["hist_sobre_nrd"], "m9: faithful, histograma / bw.nrd", tol=T8)
    a.igual(3.5 / 1.06, f["factor_constante"], "m9: el factor de las constantes", tol=T8)
    a.igual(n ** (-1 / 3) / n ** (-1 / 5), f["factor_exponente"], "m9: el factor de los exponentes", tol=T8)
    a.igual(2 * s * n ** (-1 / 5), f["sd_doble"], "m9: 2·sd·n^(-1/5)", tol=T8)
    a.igual((24 * math.sqrt(math.pi)) ** (1 / 3) / math.sqrt(12), f["hist_constante_sd"],
            "m9: la constante del histograma en desviaciones", tol=T8)
    a.igual((3.5 / 1.06) ** 7.5, f["n_cruce"], "m9: el n en que las dos reglas se cruzan", tol=1e-4)
    a.igual(round((3.5 / 1.06) ** 7.5, -2), f["n_cruce_redondo"], "m9: ese n, redondeado")
    a.igual(0.9 * q / 1.34 * n ** (-1 / 5), f["nrd0_con_iqr"], "m9: el distractor, con la escala mayor", tol=T8)
    c = m["constantes"]
    a.igual(norm.ppf(.75) - norm.ppf(.25), c["iqr_normal"], "m9: el IQR de la N(0, 1)", tol=T8)
    a.cierto((c["silverman"], c["scott"], c["iqr"], c["hist"]) == (0.9, 1.06, 1.34, 3.5),
             "m9: las cuatro constantes de las reglas")
    d = np.asarray(m["factor_d"]["d"], float)
    vec(a, (4 / (d + 2)) ** (1 / (d + 4)), m["factor_d"]["factor"], "m9: el factor (4/(d+2))^(1/(d+4))", T8)
    vec(a, -1 / (d + 4), m["factor_d"]["exponente"], "m9: el exponente -1/(d+4)", T8)

    xy = ctx["sed"]
    N = len(xy)
    p = m["plano"]
    a.igual(N, p["n"], "m9: las sedes del plano")
    a.cerca(sd(xy[:, 0]), p["sd_x"], "m9: sd de x de las sedes", rel=1e-9)
    a.cerca(sd(xy[:, 1]), p["sd_y"], "m9: sd de y de las sedes", rel=1e-9)
    a.cerca(sd(xy[:, 0]) * N ** (-1 / 6), p["scott_x"], "m9: bw.scott en x = sd·n^(-1/6)", rel=1e-9)
    a.cerca(sd(xy[:, 1]) * N ** (-1 / 6), p["scott_y"], "m9: bw.scott en y = sd·n^(-1/6)", rel=1e-9)
    a.igual(N ** (-1 / 6), p["n_sexta"], "m9: n^(-1/6)", tol=T8)

    nn = ctx["nn"]
    di = m["distancias"]
    a.igual(len(nn), di["n"], "m9: las distancias al vecino")
    a.cerca(sd(nn), di["sd"], "m9: su sd", rel=1e-9)
    a.cerca(iqr(nn) / 1.34, di["iqr_134"], "m9: su IQR/1.34", rel=1e-9)
    a.cerca(nn.max(), di["maximo"], "m9: su máximo", rel=1e-9)
    a.cerca(float(np.median(nn)), di["mediana"], "m9: su mediana", rel=1e-9)
    a.cerca(bw_nrd0(nn), di["nrd0"], "m9: su bw.nrd0", rel=1e-9)
    a.cerca(bw_nrd(nn), di["nrd"], "m9: su bw.nrd", rel=1e-9)
    sil = (4 / 3) ** (1 / 5) * sd(nn) * N ** (-1 / 5)
    a.cerca(sil, di["scipy"], "m9: el «silverman» de scipy, por fórmula", rel=1e-9)
    kde = gaussian_kde(nn, bw_method="silverman")
    a.cerca(kde.factor * math.sqrt(float(kde.covariance[0, 0]) / kde.factor ** 2),
            di["scipy"], "m9: y el de gaussian_kde, de verdad", rel=1e-9)
    a.cierto(di["iqr_134"] < di["sd"], "m9: en las distancias IQR/1.34 < sd")
    a.cierto(di["scipy"] > 1.3 * di["nrd"], "m9: el de scipy se aleja de bw.nrd",
             f"{di['scipy']:.2f} contra {di['nrd']:.2f}")


def modulo10(a, D, ctx):  # noqa: C901
    a.titulo("10 · Validación cruzada")
    m = D["m10"]
    E = ctx["E"]
    n = len(E)
    a.igual(n, m["n"], "m10: n")
    a.igual(len(np.unique(E)), m["distintos"], "m10: los valores distintos")
    a.igual(n - len(np.unique(E)), m["repetidos"], "m10: los repetidos")
    sel = m["selectores"]
    u, au = bw_cv_r(E, "ucv")
    b, ab = bw_cv_r(E, "bcv")
    sj = bw_sj_r(E)
    ctx["sel_r"] = dict(ucv=u, bcv=b, SJ=sj)
    a.igual(u, sel["ucv"], "m10: bw.ucv (portado)", tol=T8)
    a.igual(b, sel["bcv"], "m10: bw.bcv (portado)", tol=T8)
    a.igual(sj, sel["SJ"], "m10: bw.SJ (portado)", tol=T8)
    a.cierto(not au and not ab, "m10: ni bw.ucv ni bw.bcv avisan")
    a.cerca(ucv_exacta_min(E), sel["ucv"], "m10: la UCV exacta, sin agrupar", rel=TOL_UCV)
    a.cerca(bcv_exacta_min(E), sel["bcv"], "m10: la BCV exacta, sin agrupar", rel=TOL_AGRUPADO)
    a.cerca(sj_exacto(E), sel["SJ"], "m10: Sheather-Jones exacto, sin agrupar", rel=TOL_AGRUPADO)
    a.cerca(dpik_exacto(E), sel["dpik"], "m10: dpik, plug-in sin agrupar", rel=TOL_AGRUPADO)

    Dm = np.subtract.outer(E, E)

    def loo(h):
        W = phi(Dm / h)
        np.fill_diagonal(W, 0)
        return W.sum(axis=1) / ((n - 1) * h)

    def ucv(h):
        return phi(Dm / (math.sqrt(2) * h)).sum() / (n * n * h * math.sqrt(2)) - 2 * loo(h).mean()

    def lcv(h):
        return float(np.mean(np.log(loo(h))))
    hh = r_seq_by(0.02, 0.60, 0.002)
    U = np.array([ucv(h) for h in hh])
    L = np.array([lcv(h) for h in hh])
    a.igual(hh[int(np.argmin(U))], m["h_ucv_mano"], "m10: el mínimo de la UCV a mano", tol=1e-12)
    a.igual(hh[int(np.argmax(L))], m["h_lcv_mano"], "m10: el máximo de la LCV a mano", tol=1e-12)
    a.cierto(abs(m["h_ucv_mano"] - sel["ucv"]) < 0.003, "m10: la UCV a mano reproduce bw.ucv")

    gK = r_seq_len(E.min() - 1, E.max() + 1, 2048)
    todos = {"nrd0": bw_nrd0(E), "nrd": bw_nrd(E), "ucv": u, "bcv": b, "SJ": sj,
             "dpik": sel["dpik"], "hist_rule": 3.5 * sd(E) * n ** (-1 / 3)}
    for nm, h in todos.items():
        a.igual(modas_secuencia(kde_gauss(E, gK, h)), m["modas"].get(nm), f"m10: modas con {nm}")
    a.cierto(m["modas"].get("ucv") == 3 and all(v == 2 for k, v in m["modas"].items() if k != "ucv"),
             "m10: con bw.ucv tres modas; con los demás, dos")
    vec(a, donde_modas(gK, kde_gauss(E, gK, u)), m["donde_modas_ucv"],
        "m10: dónde caen las tres modas de la UCV", T8)

    gr = r_seq_len(E.min() - 3, E.max() + 3, 2048)
    dx = gr[1] - gr[0]

    def rug(h):
        v = r_density(E, h, 2048, gr[0], gr[-1])
        return trapecio(gr[2:], (np.diff(v, 2) / dx ** 2) ** 2)

    def rug_exacta(h):
        g = math.sqrt(2) * h
        uu = Dm / g
        return float(np.sum((uu ** 4 - 6 * uu ** 2 + 3) * phi(uu))) / (n * n * g ** 5)
    # La rugosidad de cada curva y su término de RUIDO, R(K'')/(nh⁵): la
    # revisión 2 quitó la «descomposición del AMISE» con R(f̂''), que no
    # estimaba R(f''), y publica en su lugar qué parte es del ancho.
    RKpp = 3 / (8 * math.sqrt(math.pi))
    a.igual(RKpp, integrate.quad(lambda x: ((x * x - 1) * phi(x)) ** 2, -np.inf, np.inf)[0],
            "m10: R(K'') del gaussiano, integrado", tol=1e-10)
    parte = {}
    for fila in m["aimse"]:
        nm = fila["selector"]
        h = todos[nm]
        a.igual(h, fila["h"], f"m10: el h de {nm}", tol=T8)
        r = rug(h)
        a.cerca(r, fila["rugosidad"], f"m10: rugosidad de {nm} (density)", rel=1e-6)
        # La forma cerrada: ver la cabecera. Medido: 0.2 % con los selectores
        # de validación cruzada, 1.2 % con nrd0, 2 % con nrd, 6.5 % con hist_rule.
        a.cerca(rug_exacta(h), fila["rugosidad"], f"m10: rugosidad de {nm} (exacta)",
                rel=0.01 if h < 0.2 else 0.07)
        # h⁵ multiplica por cinco el error relativo del h redondeado del JSON.
        a.cerca(RKpp / (n * h ** 5), fila["ruido"], f"m10: el ruido R(K'')/(nh⁵) de {nm}", rel=1e-6)
        parte[nm] = fila["ruido"] / fila["rugosidad"]
    orden = [parte[k] for k in ("ucv", "SJ", "bcv", "nrd0")]
    a.cierto(orden[0] > 0.4 and all(np.diff(orden) < 0),
             "m10: casi la mitad de la rugosidad de la UCV es ruido", " ".join(f"{v:.2f}" for v in orden))
    pa = {f["selector"]: f for f in m["aimse"]}
    a.igual(pa["ucv"]["rugosidad"] / pa["SJ"]["rugosidad"], m["rug_ucv_sobre_sj"],
            "m10: rugosidad UCV / SJ", tol=1e-7)

    # Los empates de las erupciones: la UCV exacta baja sin tope cerca de 0.
    em = m["empates"]
    _, cuenta = np.unique(np.round(E, 6), return_counts=True)
    pares = int(np.sum(cuenta * (cuenta - 1) // 2))
    umbral = RK_GAUSS / (4 * float(norm.pdf(0)) - 2 * RK_GAUSS)
    a.igual(pares, em["parejas"], "m10: las parejas de erupciones idénticas")
    a.igual(pares / n, em["por_dato"], "m10: parejas por dato", tol=T8)
    a.igual(umbral, em["umbral"], "m10: el umbral del módulo 12", tol=T8)
    a.igual(ucv(0.001), em["ucv_001"], "m10: la UCV exacta con h = 0.001", tol=1e-7)
    a.igual(ucv(m["h_ucv_mano"]), em["ucv_min_local"], "m10: la UCV en su mínimo local", tol=T8)
    a.cierto(em["por_dato"] > umbral and em["ucv_001"] < em["ucv_min_local"],
             "m10: las erupciones superan el umbral y la UCV baja sin tope")
    a.igual(0.1 * 1.144 * sd(E) * n ** (-1 / 5), em["busqueda_desde"], "m10: dónde empieza bw.ucv", tol=T8)
    a.igual(float(hh[0]), em["rejilla_desde"], "m10: dónde empieza la rejilla")
    # El jitter: R lo hizo con su generador; aquí se repite con OTRO azar, y
    # la conclusión —el mínimo local sobrevive— tiene que sostenerse igual.
    rng = np.random.default_rng(2026)
    otro = [bw_cv_r(E + rng.uniform(-0.5 / 60, 0.5 / 60, n), "ucv")[0] for _ in range(6)]
    a.cierto(all(abs(v / u - 1) < 0.1 for v in otro), "m10: con otro azar el mínimo local sobrevive",
             " ".join(f"{v:.3f}" for v in otro))
    a.cierto(em["jitter_n"] == 6 and abs(em["jitter_min"] / u - 1) < 0.1 and abs(em["jitter_max"] / u - 1) < 0.1,
             "m10: el rango publicado del jitter, junto a bw.ucv")

    # La LCV sin la erupción aislada, y dejar uno fuera a mano.
    i_ais = int(np.argmin(np.log(loo(0.05))))
    Es = np.delete(E, i_ais)
    ns_ = len(Es)
    Ds = np.subtract.outer(Es, Es)

    def loo_s(h):
        W = phi(Ds / h)
        np.fill_diagonal(W, 0)
        return W.sum(axis=1) / ((ns_ - 1) * h)
    Ls = np.array([np.mean(np.log(loo_s(h))) for h in hh])
    Us = np.array([phi(Ds / (math.sqrt(2) * h)).sum() / (ns_ * ns_ * h * math.sqrt(2)) - 2 * loo_s(h).mean()
                   for h in hh])
    a.igual(hh[int(np.argmax(Ls))], m["h_lcv_sin"], "m10: el máximo de la LCV sin la aislada", tol=1e-12)
    a.igual(hh[int(np.argmin(Us))], m["h_ucv_sin"], "m10: el mínimo de la UCV sin la aislada", tol=1e-12)
    a.igual(lcv(0.14) - lcv(0.05), m["lcv_sube"], "m10: cuánto sube la LCV de 0.05 a 0.14", tol=T8)
    a.cierto(m["aislada_cambio"] > 0.8 * m["lcv_sube"], "m10: la aislada pone casi toda la subida")
    lm = m["loo_mano"]
    t5 = phi(4 - np.array([2, 3, 5, 7], float))
    vec(a, t5, lm["terminos"], "m10: dejar uno fuera, los pesos", T8)
    a.igual(t5.mean(), lm["f"], "m10: dejar uno fuera, f̂₋ᵢ(4)", tol=T8)
    for z in m["aislada"]:
        l = np.log(loo(z["h"]))
        i = int(np.argmin(l))
        a.igual(l[i], z["min_log"], f"m10: aislada, h={z['h']}: log f̂₋ᵢ mínimo", tol=T8)
        a.igual(l[i] / n, z["aporte"], f"m10: aislada, h={z['h']}: su aporte", tol=T8)
        a.igual(E[i], z["x"], f"m10: aislada, h={z['h']}: el dato", tol=T8)
        a.igual(np.exp(l[i]), z["min_loo"], f"m10: aislada, h={z['h']}: f̂₋ᵢ mínima", tol=T8)
    cv = m["curvas"]
    hs = r_seq_by(0.04, 0.60, 0.01)
    vec(a, hs, cv["h"], "m10: la rejilla del simulador", 1e-12)
    vec(a, [ucv(h) for h in hs], cv["ucv"], "m10: la curva UCV del simulador", T8)
    vec(a, [lcv(h) for h in hs], cv["lcv"], "m10: la curva LCV del simulador", T8)
    vec(a, [float(np.mean(np.log(loo_s(h)))) for h in hs], cv["lcv_sin"], "m10: la LCV sin la aislada", T8)
    vec(a, [phi(Ds / (math.sqrt(2) * h)).sum() / (ns_ * ns_ * h * math.sqrt(2)) - 2 * loo_s(h).mean()
            for h in hs], cv["ucv_sin"], "m10: la UCV sin la aislada", T8)
    mds = [modas_secuencia(kde_gauss(E, gK, h)) for h in hs]
    enteros(a, mds, cv["modas"], "m10: las modas del simulador, h a h")
    tres = max(h for h, md in zip(hs, mds) if md >= 3)
    a.igual(tres, m["h_max_tres"], "m10: el mayor h con tercera moda", tol=1e-12)


def em2(y, mu, s, p, tol=1e-12, maxit=5000):
    ll_old = -np.inf
    mu = np.array(mu, float)
    s = np.array(s, float)
    for it in range(1, maxit + 1):
        w = p * norm.pdf(y, mu[0], s[0])
        w = w / (w + (1 - p) * norm.pdf(y, mu[1], s[1]))
        p = float(np.mean(w))
        mu = np.array([np.sum(w * y) / np.sum(w), np.sum((1 - w) * y) / np.sum(1 - w)])
        s = np.sqrt([np.sum(w * (y - mu[0]) ** 2) / np.sum(w),
                     np.sum((1 - w) * (y - mu[1]) ** 2) / np.sum(1 - w)])
        ll = float(np.sum(np.log(p * norm.pdf(y, mu[0], s[0]) + (1 - p) * norm.pdf(y, mu[1], s[1]))))
        if ll - ll_old < tol:
            break
        ll_old = ll
    return p, mu, s, ll, it


def modulo11(a, D, ctx, mc, ms):  # noqa: C901
    a.titulo("11 · La mezcla verdadera, la MISE y el Monte Carlo")
    m = D["m11"]
    E = ctx["E"]
    n = len(E)
    p, mu, s, ll, it = em2(E, [2, 4.3], [0.25, 0.35], 0.5)
    em = m["em"]
    a.igual(p, em["p"], "m11: EM, el peso de la primera normal", tol=T8)
    vec(a, mu, em["mu"], "m11: EM, las medias", T8)
    vec(a, s, em["s"], "m11: EM, las desviaciones", T8)
    a.igual(ll, em["loglik"], "m11: EM, la log-verosimilitud", tol=T8)
    # EL CORTE DEL EM ESTÁ EN EL RUIDO, y por eso se admite una iteración de
    # diferencia. Para cuando la log-verosimilitud (≈ −276) sube menos de
    # 1e-12, cada incremento es del orden de 6e-13: R suma en doble largo y
    # numpy no, y la iteración en que se cruza el umbral puede caer una antes
    # o una después. Los parámetros no se mueven a 8 decimales entre una y
    # otra; lo que sí se mueve se mide más abajo, en el sobrecoste.
    a.igual(it, em["iter"], "m11: EM, las iteraciones (±1: el corte es ruido)", tol=1)
    try:
        from sklearn.mixture import GaussianMixture
        gm = GaussianMixture(2, tol=1e-12, max_iter=5000, means_init=[[2.0], [4.3]],
                             precisions_init=[[[1 / 0.25 ** 2]], [[1 / 0.35 ** 2]]],
                             weights_init=[0.5, 0.5], reg_covar=0).fit(E[:, None])
        o = np.argsort(gm.means_.ravel())
        a.igual(gm.weights_[o][0], em["p"], "m11: EM de sklearn, el peso", tol=1e-5)
        vec(a, gm.means_.ravel()[o], em["mu"], "m11: EM de sklearn, las medias", 1e-5)
        vec(a, np.sqrt(gm.covariances_.ravel()[o]), em["s"], "m11: EM de sklearn, las sd", 1e-5)
    except ImportError:
        a.salta("m11: EM de sklearn", "sklearn no está en este entorno")
    PI = np.array([p, 1 - p])
    MU, SG = mu, s

    def Aprod(av, bv):
        return sum(PI[i] * PI[j] * norm.pdf(MU[i] - MU[j], 0, math.sqrt(av[i] ** 2 + bv[j] ** 2))
                   for i in range(2) for j in range(2))

    def mise(h):
        ss = np.sqrt(SG ** 2 + h * h)
        return Aprod(ss, ss) - 2 * Aprod(ss, SG) + Aprod(SG, SG) + (1 / (2 * h * math.sqrt(math.pi))
                                                                    - Aprod(ss, ss)) / n
    r = optimize.minimize_scalar(mise, bounds=(0.02, 0.8), method="bounded", options={"xatol": 1e-11})
    a.igual(r.x, m["h_estrella"], "m11: h* que minimiza la MISE", tol=1e-7)
    a.igual(mise(r.x), m["mise_min"], "m11: la MISE mínima", tol=T8)

    def gv(x):
        return PI[0] * norm.pdf(x, MU[0], SG[0]) + PI[1] * norm.pdf(x, MU[1], SG[1])

    def mise_num(h):
        def err(x):
            ef = sum(PI[i] * norm.pdf(x, MU[i], math.sqrt(SG[i] ** 2 + h * h)) for i in range(2))
            ek2 = sum(PI[i] * norm.pdf(x, MU[i], math.sqrt(SG[i] ** 2 + h * h / 2))
                      for i in range(2)) / (2 * math.sqrt(math.pi) * h)
            return (ef - gv(x)) ** 2 + (ek2 - ef * ef) / n
        return integrate.quad(err, -np.inf, np.inf, epsabs=1e-13, limit=200)[0]
    a.igual(mise_num(r.x), m["mise_min"], "m11: la MISE mínima, integrada punto a punto", tol=T8)
    hs = {"nrd0": bw_nrd0(E), "nrd": bw_nrd(E), **ctx["sel_r"],
          "dpik": D["m10"]["selectores"]["dpik"], "hist_rule": 3.5 * sd(E) * n ** (-1 / 3)}
    for fila in m["reales"]:
        nm = fila["selector"]
        h = hs[nm]
        a.igual(h, fila["h"], f"m11: real, el h de {nm}", tol=T8)
        a.igual(mise(h), fila["mise"], f"m11: real, la MISE de {nm}", tol=T8)
        # El sobrecoste es 100·(cociente − 1), y el cociente de dos MISE
        # arrastra ~1.5e-8 relativo del corte del EM (medido: entre parar en
        # la iteración 29, en la 30 o en la 200, se mueve eso). Así que el
        # error ABSOLUTO del porcentaje es 100·cociente·1.5e-8 —hasta 2e-5
        # con la regla del histograma, que cuesta ×12,7— y no los 8
        # decimales del JSON. La tolerancia lleva un factor 2 de holgura.
        a.igual(100 * (mise(h) / mise(r.x) - 1), fila["sobre_pct"],
                f"m11: real, el sobrecoste de {nm}", tol=(100 + abs(fila["sobre_pct"])) * 3e-8)
    sp = {f["selector"]: f["sobre_pct"] for f in m["reales"]}
    a.cierto(sp["SJ"] < sp["bcv"] < sp["ucv"], "m11: sobre faithful, SJ < BCV < UCV",
             f"{sp['SJ']:.2f} < {sp['bcv']:.2f} < {sp['ucv']:.2f}")
    a.cierto(sp["nrd0"] > 100 and sp["hist_rule"] > sp["nrd"],
             "m11: las reglas normales cuestan más del doble")

    # --- El Monte Carlo, desde el CSV réplica a réplica -----------------
    SEL = ["nrd0", "nrd", "ucv", "bcv", "SJ"]
    B = len(mc)
    a.igual(B, m["B"], "mc: las réplicas del CSV")
    a.cierto(list(mc["replica"]) == list(range(1, B + 1)), "mc: las réplicas van de 1 a B")
    a.igual(m["n"], n, "mc: n de cada réplica")
    a.igual(m["semilla"], 2026, "mc: la semilla de la casa")
    ISE = mc[[f"ise_{s}" for s in SEL]].to_numpy(float)
    HS = mc[[f"h_{s}" for s in SEL]].to_numpy(float)
    AV = mc[[f"aviso_{s}" for s in SEL]].to_numpy(float)
    gana = np.argmin(ISE, axis=1)
    cola = (ISE > 2 * ISE[:, [SEL.index("SJ")]]).mean(axis=0)
    for j, s in enumerate(SEL):
        f = por(m["por_selector"], "selector", s)
        a.igual(HS[:, j].mean(), f.get("h_media"), f"mc: {s}, h medio", tol=T8)
        a.igual(float(np.median(HS[:, j])), f.get("h_mediana"), f"mc: {s}, h mediano", tol=T8)
        a.igual(ISE[:, j].mean(), f.get("mise"), f"mc: {s}, la MISE (ISE medio)", tol=T8)
        a.igual(sd(ISE[:, j]) / math.sqrt(B), f.get("ee_mc"), f"mc: {s}, su error de Monte Carlo",
                tol=T8)
        a.igual(sd(ISE[:, j]), f.get("sd_ise"), f"mc: {s}, la sd del ISE", tol=T8)
        a.igual(float(np.median(ISE[:, j])), f.get("ise_mediano"), f"mc: {s}, el ISE mediano", tol=T8)
        pg = 100 * float(np.mean(gana == j))
        a.igual(pg, f.get("gana_pct"), f"mc: {s}, % de victorias", tol=T8)
        a.igual(100 * math.sqrt(pg / 100 * (1 - pg / 100) / B), f.get("gana_ee"),
                f"mc: {s}, el error de ese %", tol=T8)
        a.igual(100 * cola[j], f.get("cola_pct"), f"mc: {s}, % con ISE > 2×SJ", tol=T8)
        a.igual(int((AV[:, j] > 0).sum()), f.get("avisos"), f"mc: {s}, réplicas con aviso")
        # El JSON lleva ahora el ISE con todos los decimales que escribe (8),
        # no seis: con seis, algunas réplicas empataban al redondear y el
        # simulador daba 40.5 % donde el CSV da 40.9 % (revisión 2).
        ise_j = (m.get("ise") or {}).get(s)
        vec(a, ISE[:, j], ise_j, f"mc: {s}, el ISE del JSON es el del CSV", 5.0e-9 + 5.1e-11)
        a.igual(sd(HS[:, j]), f.get("h_sd"), f"mc: {s}, la sd de sus anchos", tol=T8)
        a.igual(100 * float(np.mean(HS[:, j] > m["h_estrella"])), f.get("pct_sobre_hstar"),
                f"mc: {s}, % de anchos por encima de h*", tol=T8)
    ps = {f["selector"]: f for f in m["por_selector"]}
    a.cierto(max(ps, key=lambda k: ps[k]["gana_pct"]) == "ucv", "mc: la UCV es la que más gana")
    a.cierto(abs(sum(f["gana_pct"] for f in m["por_selector"]) - 100) < 1e-6,
             "mc: las victorias suman 100 %")
    a.cierto(ps["ucv"]["mise"] > ps["SJ"]["mise"], "mc: pero su MISE es peor que la de SJ")
    a.cierto(ps["ucv"]["cola_pct"] > 2 and ps["bcv"]["cola_pct"] == 0,
             "mc: la UCV tiene cola y la BCV no")
    # La UCV se equivoca de dispersión y hacia un lado (revisión 2).
    iu, isj, ib = SEL.index("ucv"), SEL.index("SJ"), SEL.index("bcv")
    en_cola = ISE[:, iu] > 2 * ISE[:, isj]
    cu = m["cola_ucv"]
    a.igual(int(en_cola.sum()), cu["n"], "mc: las réplicas en que la UCV pierde por más del doble")
    a.igual(float(HS[en_cola, iu].max()), cu["h_max"], "mc: el mayor ancho de la UCV en esas", tol=T8)
    a.igual(100 * float(np.mean(HS[:, iu] < 0.1)), cu["pct_h_bajo"], "mc: % de anchos de la UCV bajo 0.10", tol=T8)
    a.cierto(bool(np.all(HS[en_cola, iu] < HS[en_cola, isj])) and cu["h_max"] < cu["corte"],
             "mc: en sus fallos grandes la UCV eligió menos ancho que SJ")
    a.cierto(ps["ucv"]["h_sd"] > 2 * ps["SJ"]["h_sd"], "mc: la UCV dispersa sus anchos más del doble que SJ")
    a.cierto(ps["SJ"]["pct_sobre_hstar"] > 90 and ps["bcv"]["pct_sobre_hstar"] > 90,
             "mc: SJ y la BCV se pasan de ancho casi siempre")
    # El error de la DIFERENCIA de dos porcentajes de victoria.
    for clave, (x_, y_) in (("ucv_bcv", ("ucv", "bcv")), ("bcv_sj", ("bcv", "SJ"))):
        pa_, pb_ = float(np.mean(gana == SEL.index(x_))), float(np.mean(gana == SEL.index(y_)))
        ee = math.sqrt((pa_ + pb_ - (pa_ - pb_) ** 2) / B)
        g_ = m["dif_gana"][clave]
        a.igual(100 * (pa_ - pb_), g_["dif"], f"mc: {clave}, la diferencia de victorias", tol=T8)
        a.igual(100 * ee, g_["ee"], f"mc: {clave}, su error estándar", tol=T8)
        a.igual((pa_ - pb_) / ee, g_["z"], f"mc: {clave}, su z", tol=1e-6)
    a.cierto(m["dif_gana"]["ucv_bcv"]["z"] > 2 and abs(m["dif_gana"]["bcv_sj"]["z"]) < 2,
             "mc: UCV-BCV es real y BCV-SJ no se distingue")
    a.igual(100 * float(np.mean(ISE[:, ib] < ISE[:, isj])), m["cara_bcv_sj"], "mc: BCV contra SJ, cara a cara", tol=T8)
    a.igual(100 * float(np.mean(ISE[:, iu] < ISE[:, isj])), m["cara_ucv_sj"], "mc: UCV contra SJ, cara a cara", tol=T8)
    for clave, (x_, y_) in (("ucv_sj", ("ucv", "SJ")), ("bcv_sj", ("bcv", "SJ"))):
        dd = ISE[:, SEL.index(x_)] - ISE[:, SEL.index(y_)]
        e = m["emparejadas"][clave]
        a.cierto(e["a"] == x_ and e["b"] == y_, f"mc: {clave}, la pareja es la que dice")
        a.igual(dd.mean(), e["media"], f"mc: {clave}, la diferencia media", tol=T8)
        a.igual(sd(dd) / math.sqrt(B), e["ee"], f"mc: {clave}, su error estándar", tol=T8)
        a.igual(dd.mean() / (sd(dd) / math.sqrt(B)), e["t"], f"mc: {clave}, la t emparejada", tol=1e-6)
        a.igual(100 * (ISE[:, SEL.index(x_)].mean() / ISE[:, SEL.index(y_)].mean() - 1), e["pct"],
                f"mc: {clave}, la diferencia en %", tol=1e-6)
    pc = cola[SEL.index("ucv")]
    ic = 100 * (pc + np.array([-1, 1]) * 1.96 * math.sqrt(pc * (1 - pc) / B))
    vec(a, ic, m["cola_ucv_ic"], "mc: el IC 95 % de la cola de la UCV", T8)
    a.igual(100 * 3 / B, m["cola_cero_cota"], "mc: la cota de la regla del tres", tol=T8)
    rj = m["rejilla_ise"]
    a.cierto((rj["desde"], rj["hasta"], rj["paso"]) == (-1, 8, 0.01), "mc: la rejilla del ISE")

    # --- Las 20 réplicas guardadas: se rehacen enteras ------------------
    gz = r_seq_by(-1, 8, 0.01)
    gvv = gv(gz)
    dgz = gz[1] - gz[0]
    reps = sorted(ms["replica"].unique())
    a.cierto(reps == list(range(1, 21)) and all((ms["replica"] == r).sum() == n for r in reps),
             "mc: el CSV de muestras trae 20 réplicas de 272")
    d_h, d_r, d_x, d_av, d_u = 0.0, 0.0, 0.0, 0, 0.0
    for r_ in reps:
        y = ms.loc[ms["replica"] == r_, "y"].to_numpy(float)
        fila = mc.loc[mc["replica"] == r_].iloc[0]
        hh = {"nrd0": bw_nrd0(y), "nrd": bw_nrd(y)}
        hu, avu = bw_cv_r(y, "ucv")
        hb_, avb = bw_cv_r(y, "bcv")
        hh.update(ucv=hu, bcv=hb_, SJ=bw_sj_r(y))
        av = {"nrd0": False, "nrd": False, "ucv": avu, "bcv": avb, "SJ": False}
        for s in SEL:
            d_h = max(d_h, abs(hh[s] - fila[f"h_{s}"]))
            d_av += int(bool(av[s]) != bool(fila[f"aviso_{s}"] > 0))
            ise_r = float(np.sum((r_density(y, fila[f"h_{s}"], len(gz), -1.0, 8.0) - gvv) ** 2) * dgz)
            ise_x = float(np.sum((kde_gauss(y, gz, fila[f"h_{s}"]) - gvv) ** 2) * dgz)
            d_r = max(d_r, abs(ise_r - fila[f"ise_{s}"]))
            d_x = max(d_x, abs(ise_x / fila[f"ise_{s}"] - 1))
        d_u = max(d_u, abs(ucv_exacta_min(y) / fila["h_ucv"] - 1))
    a.cierto(d_h <= 2e-9, "mc: 20 réplicas, los cinco h rehechos", f"dif máx {d_h:.1e}")
    a.cierto(d_av == 0, "mc: 20 réplicas, los avisos rehechos", f"{d_av} discrepan")
    a.cierto(d_r <= 2e-9, "mc: 20 réplicas, el ISE con density() portada", f"dif máx {d_r:.1e}")
    a.cierto(d_x <= 0.01, "mc: 20 réplicas, el ISE con la KDE exacta (1 %)", f"dif rel máx {d_x:.2%}")
    a.cierto(d_u <= TOL_UCV, "mc: 20 réplicas, la UCV exacta (5 %)", f"dif rel máx {d_u:.2%}")
    allv = ms["y"].to_numpy(float)
    media_v = PI @ MU
    var_v = PI @ (SG ** 2 + MU ** 2) - media_v ** 2
    zsc = (allv.mean() - media_v) / math.sqrt(var_v / len(allv))
    a.cierto(abs(zsc) < 4, "mc: las muestras salen de la mezcla (media)", f"z = {zsc:.2f}")


def nn_spatstat(xy):
    """Distancia y vecino más próximo con el desempate de spatstat.

    `nnwhich` ordena por y (orden estable) y busca HACIA DELANTE primero,
    quedándose con el primer mínimo estricto; luego hacia atrás, solo si
    mejora. Con sedes que comparten dirección hay empates exactos, y el
    desempate decide quién es la pareja recíproca: en el trío de Bogotá
    no es lo mismo «1036↔1053» que «1053↔1091», y la lista «una por
    pareja» cambia de orden.
    """
    n = len(xy)
    o = np.argsort(xy[:, 1], kind="stable")
    pos = np.empty(n, int)
    pos[o] = np.arange(n)
    t = cKDTree(xy)
    dd, _ = t.query(xy, k=2)
    nn = dd[:, 1]
    quien = np.empty(n, int)
    for i in range(n):
        cand = np.array(t.query_ball_point(xy[i], nn[i] * (1 + 1e-12) + 1e-12))
        cand = cand[cand != i]
        d2 = (xy[cand, 0] - xy[i, 0]) ** 2 + (xy[cand, 1] - xy[i, 1]) ** 2
        cand = cand[d2 == d2.min()]
        delante = cand[pos[cand] > pos[i]]
        if delante.size:
            quien[i] = delante[np.argmin(pos[delante])]
        else:
            quien[i] = cand[np.argmax(pos[cand])]
    return nn, quien


def empates(v) -> int:
    _, c = np.unique(np.round(np.asarray(v, float), 6), return_counts=True)
    return int(np.sum(c * (c - 1) // 2))


def _gauss_legendre(a, b, paneles, nodos=12):
    t, w = np.polynomial.legendre.leggauss(nodos)
    bordes = np.linspace(a, b, paneles + 1)
    centro = (bordes[:-1] + bordes[1:]) / 2
    medio = (bordes[1:] - bordes[:-1]) / 2
    return ((centro[:, None] + medio[:, None] * t).ravel(),
            (medio[:, None] * w).ravel())


# (1 − Φ(x))/Φ(x) se anula —en doble precisión— antes de x = 40.
_X_AP, _W_AP = _gauss_legendre(0.0, 40.0, 400)
_R_AP = norm.sf(_X_AP) / norm.cdf(_X_AP)


def aporte_e(d):
    """∫₀^∞ φ(x − d)/Φ(x) dx: lo que aporta un dato a d anchos del borde con e(x).

    Se parte en Φ(d) + ∫₀^∞ φ(x − d)·(1 − Φ(x))/Φ(x) dx. El primer término
    es exacto; el segundo solo vive cerca del borde —(1 − Φ)/Φ cae como
    φ(x)/x—, así que una cuadratura de Gauss-Legendre fija en [0, 40] lo
    resuelve para CUALQUIER d. Y eso no es un detalle: la integral directa
    sobre [0, ∞) pierde el pico cuando el dato está lejos del borde (las
    sedes llegan a d ≈ 120), que es justo lo que le pasa a `integrate()`.
    """
    d = np.atleast_1d(np.asarray(d, float))
    out = np.empty(len(d))
    for i in range(0, len(d), 256):
        dd = d[i:i + 256]
        out[i:i + 256] = norm.cdf(dd) + (phi(_X_AP[None, :] - dd[:, None]) * _R_AP) @ _W_AP
    return out


def modulo12(a, D, ctx):  # noqa: C901
    a.titulo("12 · Del renglón al plano: las sedes de Bogotá")
    m = D["m12"]
    nn, quien = ctx["nn"], ctx["quien"]
    N = len(nn)
    a.igual(N, m["n"], "m12: las sedes")
    a.igual(int((nn == 0).sum()), m["ceros"], "m12: las distancias cero (direcciones repetidas)")
    lam = N / ctx["area"]
    a.igual(lam, m["lambda_km2"], "m12: λ (sedes por km²)", tol=T8)
    idx = np.arange(N)
    rec = quien[quien] == idx
    rp = m["recipro"]
    a.igual(int(rec.sum()), rp["n"], "m12: las sedes con vecino recíproco")
    a.igual(100 * rec.mean(), rp["pct"], "m12: el % recíproco", tol=T8)
    a.igual(int(rec.sum()) // 2, rp["parejas"], "m12: las parejas recíprocas")
    c = 6 * math.pi / (8 * math.pi + 3 * math.sqrt(3))
    a.igual(c, rp["csr"], "m12: la constante de CSR 6π/(8π+3√3)", tol=T8)
    a.igual(100 * c, rp["csr_pct"], "m12: esa constante, en %", tol=T8)
    a.cierto(abs(rp["csr_simulada"] - c) < 0.012, "m12: la simulada de R, a menos de 0.012",
             f"{rp['csr_simulada']} contra {c:.5f}")
    # LA SIMULACIÓN DE AQUÍ NO COPIA EL FILTRO DEL GENERADOR, y a propósito.
    # Quedarse con los puntos cuyo borde está a más de 3 veces SU distancia
    # al vecino favorece, cerca del borde, a los que tienen el vecino muy
    # cerca, que son justo los que más se emparejan: medido con numpy sobre
    # 20 semillas, ese filtro da 0.6281 ± 0.0008, no 0.6215. Un margen FIJO
    # (0.03, unas ocho distancias medias) no mira la distancia de cada punto
    # y no sesga: 0.6225 ± 0.0006 sobre 40 semillas.
    rng = np.random.default_rng(2026)
    P = rng.random((rp["csr_n"], 2))
    dq, wq = cKDTree(P).query(P, k=2)
    bd = np.minimum.reduce([P[:, 0], P[:, 1], 1 - P[:, 0], 1 - P[:, 1]])
    w = wq[:, 1]
    c_sim = float((w[w] == np.arange(len(P)))[bd > 0.03].mean())
    a.igual(c_sim, c, "m12: y la simulada aquí, con numpy", tol=0.012)
    a.igual(c / 2, m["csr_parejas_por_n"], "m12: parejas por dato bajo CSR", tol=T8)
    di = m["distancias"]
    a.cerca(nn.mean(), di["media"], "m12: la distancia media", rel=1e-9)
    a.cerca(float(np.median(nn)), di["mediana"], "m12: la distancia mediana", rel=1e-9)
    a.cerca(nn.max(), di["maximo"], "m12: la distancia máxima", rel=1e-9)
    a.igual(len(np.unique(np.round(nn, 6))), di["distintas"], "m12: las distancias distintas")
    lm2 = lam / 1e6
    mc_ = 0.5 / math.sqrt(lm2)
    a.cerca(mc_, m["csr"]["media"], "m12: la media bajo CSR, 1/(2√λ)", rel=1e-9)
    a.cerca(math.sqrt(math.log(2) / (lm2 * math.pi)), m["csr"]["mediana"],
            "m12: la mediana bajo CSR, √(ln2/(λπ))", rel=1e-9)
    a.cerca(nn.mean() / mc_, m["csr"]["clark_evans"], "m12: Clark-Evans", rel=1e-8)
    a.cierto(m["csr"]["clark_evans"] < 1, "m12: las sedes, más cerca que bajo CSR")

    RK, K0 = RK_GAUSS, float(norm.pdf(0))
    umbral = RK / (4 * K0 - 2 * RK)
    a.igual(umbral, m["umbral_empates"], "m12: el umbral R(K)/(4K(0)−2R(K))", tol=T8)
    a.igual(0.001, m["h_minusculo"], "m12: el h minúsculo, 1 mm")
    una = nn[(~rec) | (idx < quien)]
    a.igual(len(una), N - int(rec.sum()) // 2, "m12: una por pareja: n − parejas")
    a.igual(int((una == 0).sum()), m["ceros_una_por_pareja"], "m12: los ceros de una por pareja")
    subs = {"todas": nn, "sin_ceros": nn[nn > 0], "una_por_pareja": una,
            "una_por_pareja_sin_ceros": una[una > 0]}
    for k, v in subs.items():
        p = m["selectores"][k]
        et = {"todas": "todas", "sin_ceros": "sin ceros", "una_por_pareja": "una/pareja",
              "una_por_pareja_sin_ceros": "una/pareja sin 0"}[k]
        a.igual(len(v), p["n"], f"m12: {et}, n")
        a.cerca(bw_nrd0(v), p["nrd0"], f"m12: {et}, bw.nrd0", rel=1e-9)
        E_ = empates(v)
        a.igual(E_, p["empates"], f"m12: {et}, parejas empatadas")
        a.igual(E_ / len(v), p["empates_por_n"], f"m12: {et}, empates por dato", tol=T8)
        ux = ucv_exacta(v, 0.001)
        a.igual(ux, p["ucv_h_minusculo"], f"m12: {et}, UCV exacta con h = 1 mm", tol=T8)
        a.igual(ucv_exacta(v, 20.0), p["ucv_h20"], f"m12: {et}, UCV exacta con h = 20 m", tol=T8)
        a.igual(0.1 * 1.144 * sd(v) * len(v) ** (-1 / 5), p["busqueda_desde"],
                f"m12: {et}, dónde empieza bw.ucv", tol=T8)
        # La teoría del colapso: con h → 0 manda el corchete
        # R(K)(n+2E)/n² − 4E·K(0)/(n(n−1)); su signo es el del criterio.
        nn_ = len(v)
        corchete = RK * (nn_ + 2 * E_) / nn_ ** 2 - 4 * E_ * K0 / (nn_ * (nn_ - 1))
        a.cierto(np.sign(corchete) == np.sign(p["ucv_h_minusculo"]),
                 f"m12: {et}, signo por la teoría de empates",
                 f"corchete {corchete:+.4f}, UCV·h {p['ucv_h_minusculo'] * 0.001:+.6f}")
        hu, av = bw_cv_r(v, "ucv")
        a.cerca(hu, p["ucv"], f"m12: {et}, bw.ucv (portado)", rel=1e-8)
        a.cierto(av == p["aviso"], f"m12: {et}, el aviso de bw.ucv", f"{av} / {p['aviso']}")
        a.cerca(bw_sj_r(v), p["sj"], f"m12: {et}, bw.SJ (portado)", rel=1e-8)
    S_ = m["selectores"]
    for k in ("todas", "sin_ceros", "una_por_pareja"):
        z = S_[k]
        # El colapso no se lee en el signo —la UCV es negativa también en un
        # buen ancho— sino en caer por debajo de su valor en 20 m (revisión 2).
        a.cierto(z["empates_por_n"] > m["umbral_empates"] and z["ucv_h_minusculo"] < z["ucv_h20"],
                 f"m12: {k}: sobre el umbral, la UCV se hunde"[:57])
        a.cierto(z["aviso"] and z["ucv"] < 0.4 * z["sj"], f"m12: {k}: bw.ucv colapsa y avisa"[:57])
    z = S_["una_por_pareja_sin_ceros"]
    a.cierto(z["empates_por_n"] < m["umbral_empates"] and z["ucv_h_minusculo"] > z["ucv_h20"],
             "m12: sin parejas ni ceros, con 1 mm no cae bajo 20 m")
    t_ = S_["todas"]
    a.cierto(t_["busqueda_desde"] < t_["ucv"] < 1.1 * t_["busqueda_desde"],
             "m12: bw.ucv junto al extremo, sin igualarlo")
    a.cierto(not z["aviso"] and abs(z["ucv"] / z["sj"] - 1) < 0.1,
             "m12: sin parejas ni ceros, la UCV vuelve junto a SJ")
    v0 = subs["una_por_pareja_sin_ceros"]
    a.cerca(ucv_exacta_min(v0), z["ucv"], "m12: una/pareja sin 0, UCV exacta", rel=TOL_UCV)
    a.cerca(sj_exacto(v0), z["sj"], "m12: una/pareja sin 0, SJ exacto", rel=TOL_AGRUPADO)

    # --- El borde en r = 0 ----------------------------------------------
    bo = m["borde"]
    h = float(z["sj"])
    a.igual(h, bo["h"], "m12: borde, el h es el SJ sin parejas ni ceros", tol=T8)
    hx = bw_sj_r(v0)
    masa_neg = float(np.mean(norm.cdf(-nn / hx)))
    a.igual(100 * masa_neg, bo["masa_negativa_pct"], "m12: borde, % de masa en r < 0", tol=1e-7)
    a.igual(1 - masa_neg, bo["masa_sin"], "m12: borde, la masa sin corregir", tol=T8)
    a.igual(1, bo["masa_reflejada"], "m12: borde, reflejar conserva la masa")
    ap = bo["aporte"]
    ds = np.asarray(ap["d_sobre_h"], float)
    a.igual(float(aporte_e(0.0)[0]), math.log(2), "m12: la cuadratura da ln 2 en el borde", tol=1e-12)
    vec(a, aporte_e(ds), ap["aporte"], "m12: borde, el aporte de un dato con e(x)", T8)
    a.igual(math.log(2), ap["ln2"], "m12: borde, ln 2", tol=T8)
    a.igual(ap["aporte"][0], math.log(2), "m12: un dato en el borde aporta ln 2", tol=T8)
    rmax = optimize.minimize_scalar(lambda d: -float(aporte_e(d)[0]), bounds=(0, 4),
                                    method="bounded", options={"xatol": 1e-9})
    # `optimize()` de R se para con tol = eps^0.25 ≈ 1.2e-4: el punto del
    # máximo no tiene más cifras que esas; el valor sí, porque ahí es plano.
    a.igual(rmax.x, ap["d_max"], "m12: borde, dónde aporta más un dato", tol=2.5e-4)
    a.igual(-rmax.fun, ap["max"], "m12: borde, cuánto aporta como máximo", tol=T8)
    a.cierto(ap["max"] > 1, "m12: a 1.6 anchos del borde un dato aporta > 1")
    # LA PRIMERA PASADA DE ESTE AUDITOR CAZÓ AQUÍ UN DEFECTO REAL (2026-10-02):
    # el generador integraba con `integrate()` sobre [0, ∞), que pierde el
    # pico de las sedes lejanas (d ≳ 20) y las hace aportar 0 en vez de 1.
    # Publicaba 0.94916; la masa es 0.99140. Se comprueba contra el valor
    # de aquí, sin más: la cuadratura de `aporte_e` no depende de d.
    ue = aporte_e(nn / hx)
    a.igual(ue.mean(), bo["masa_e"], "m12: borde, la masa con e(x)", tol=T8)
    a.cierto(bo["masa_e"] < 1, "m12: en las sedes e(x) se queda corta")
    a.igual(100 * float(np.mean(nn < hx)), bo["cerca_del_borde_pct"], "m12: borde, % a menos de h", tol=T8)
    pesos = 1 / norm.cdf(nn / hx)
    a.igual(float(np.mean(pesos * (1 - norm.cdf(-nn / hx)))), bo["masa_diggle"],
            "m12: borde, la masa con Diggle", tol=T8)
    a.igual(bo["masa_diggle"], 1, "m12: Diggle conserva la masa: vale 1", tol=1e-12)
    f0s = float(np.mean(phi(nn / hx)) / hx)
    a.igual(f0s, bo["f0_sin"], "m12: borde, f̂(0) sin corregir", tol=T8)
    a.igual(2 * f0s, bo["f0_reflejada"], "m12: borde, f̂(0) reflejada", tol=T8)
    a.igual(f0s / norm.cdf(0), bo["f0_e"], "m12: borde, f̂(0) con e(x)", tol=T8)
    a.igual(float(np.mean(pesos * phi(nn / hx)) / hx), bo["f0_diggle"], "m12: borde, f̂(0) con Diggle",
            tol=T8)
    a.igual(bo["f0_reflejada"], 2 * bo["f0_sin"], "m12: reflejar duplica f̂(0)", tol=2.1e-8)
    # En r = 0 mandan los ceros: un átomo, no densidad (revisión 2).
    fc = float((nn == 0).sum()) * float(norm.pdf(0)) / (N * hx)
    a.igual(fc, bo["f0_ceros"], "m12: borde, lo que ponen los ceros en r = 0", tol=T8)
    a.cierto(bo["f0_ceros"] > 0.5 * bo["f0_sin"], "m12: los ceros ponen más de la mitad")
    cv = m["curvas"]
    r = r_seq_by(0, 600, 0.5)[::4]
    vec(a, r, cv["r"], "m12: la rejilla de las curvas", 1e-12)
    a.igual(m["curvas_hasta"], r[-1], "m12: las curvas llegan a 600 m")
    U = (r[:, None] - nn[None, :]) / hx
    Ur = (r[:, None] + nn[None, :]) / hx
    vec(a, phi(U).mean(axis=1) / hx, cv["sin"], "m12: la curva sin corregir", T8)
    vec(a, (phi(U) + phi(Ur)).mean(axis=1) / hx, cv["reflejada"], "m12: la curva reflejada", T8)
    vec(a, (pesos[None, :] * phi(U)).mean(axis=1) / hx, cv["diggle"], "m12: la curva de Diggle", T8)
    vec(a, phi(U).mean(axis=1) / hx / norm.cdf(r / hx), cv["e"], "m12: la curva dividida por e(r)", T8)
    # El valle y la moda de la reflejada, en la rejilla de 0.5 m del generador.
    rf = r_seq_by(0, 600, 0.5)
    yref = (phi((rf[:, None] - nn[None, :]) / hx) + phi((rf[:, None] + nn[None, :]) / hx)).mean(axis=1) / hx
    iv = int(np.flatnonzero(np.diff(np.sign(np.diff(yref))) > 0)[0]) + 1
    im = int(np.argmax(np.where(rf > rf[iv], yref, -np.inf)))
    a.igual(rf[iv], bo["reflejada_valle"]["r"], "m12: el valle de la reflejada", tol=1e-9)
    a.igual(yref[iv], bo["reflejada_valle"]["f"], "m12: su altura", tol=T8)
    a.igual(rf[im], bo["reflejada_moda"]["r"], "m12: la moda de la reflejada", tol=1e-9)
    a.cierto(yref[0] > yref[iv] and rf[im] > rf[iv], "m12: la reflejada tiene un máximo en r = 0")
    # Ese máximo es de los ceros: sin ellos la reflejada sube desde r = 0.
    rs = m["borde"]["reflejada_sin_ceros"]
    pos = nn[nn > 0]
    rr = np.asarray(rs["r"], float)
    ys = (phi((rr[:, None] - pos[None, :]) / hx) + phi((rr[:, None] + pos[None, :]) / hx)).mean(axis=1) / hx
    vec(a, ys, rs["f"], "m12: la reflejada sin los ceros", T8)
    a.cierto(bool(np.all(np.diff(ys) > 0)) and ys[0] < yref[iv], "m12: sin los ceros sube desde r = 0")
    dep = m["depurada"]
    a.igual(len(v0), dep["n"], "m12: la lista depurada, n")
    a.cerca(float(np.median(v0)), dep["mediana"], "m12: la lista depurada, mediana", rel=1e-9)
    vec(a, 2 * math.pi * lm2 * r * np.exp(-lm2 * math.pi * r * r), cv["csr"],
        "m12: la densidad de CSR, 2πλr·e^(−λπr²)", T8)
    vec(a, np.round(nn, 1), m["nn"], "m12: las distancias publicadas (0.1 m)", 0.0501)
    vec(a, np.sort(np.round(una, 1)), np.sort(np.asarray(m["una_por_pareja"], float)),
        "m12: una por pareja: las mismas cifras", 0.0501)
    vec(a, np.round(una, 1), m["una_por_pareja"], "m12: una por pareja: y en el mismo orden", 0.0501)


# =====================================================================
# Los ejercicios
# =====================================================================
DEMANDA = re.compile(r"(?<!\w)(?:[Dd]i|[Ee]xplica|[Ee]ncuéntralo|[Ee]ncuentra|[Cc]ontesta|"
                     r"[Cc]ompara|[Dd]iscute)(?!\w)|¿")


def sin_contestar(e) -> list[str]:
    """La guarda `sin_contestar()` del generador, reescrita sin mirarla."""
    en = e.get("enunciado", "")
    ini, fin = [], []
    for r in e.get("solucion", {}).get("respuestas") or []:
        p = r.get("pide") or ""
        i = en.find(p) if p else -1
        if i >= 0:
            ini.append(i)
            fin.append(i + len(p) - 1)
    fuera = []
    for mt in DEMANDA.finditer(en):
        q = mt.start()
        dentro = any(a_ <= q <= b_ for a_, b_ in zip(ini, fin))
        if not dentro:
            resto = [i for i in ini if i > q]
            if resto:
                tramo = en[q:min(resto) + 1]
                dentro = ":" in tramo and "." not in tramo
        if not dentro:
            fuera.append(en[q:q + 30])
    return fuera


def ejercicios(a, S, D, ctx):  # noqa: C901
    a.titulo("13 · Los diez ejercicios")
    a.igual(S["meta"]["n_ejercicios"], 10, "ej: son diez")
    a.igual(S["meta"]["semilla"], 2026, "ej: con la semilla de la casa")
    claves = [f"e{i}" for i in range(1, 11)]
    for k in claves:
        a.cierto(k in S, f"ej: está {k}")
    if any(k not in S for k in claves):
        return
    for k in claves:
        e = S[k]
        resp = e["solucion"]["respuestas"]
        a.cierto(len(resp) > 0 and all(str(r.get("respuesta", "")).strip() for r in resp),
                 f"{k}: trae respuestas, y ninguna vacía", str(len(resp)))
        sueltas = [r.get("pide") for r in resp if not r.get("pide") or r.get("pide") not in e["enunciado"]]
        a.cierto(not sueltas, f"{k}: cada «pide» está literal en su enunciado", "; ".join(map(str, sueltas)))
        fuera = sin_contestar(e)
        a.cierto(not fuera, f"{k}: ninguna demanda se queda sin respuesta", " | ".join(fuera))
        a.cierto(bool(str(e["solucion"].get("lectura", "")).strip()), f"{k}: trae su lectura")
        # La pista y el módulo que practica: la revisión 2 los añadió.
        a.cierto(len(str(e.get("pista", "")).strip()) > 20, f"{k}: trae su pista")
        a.cierto(bool(re.fullmatch(r"\d+( y \d+|(, \d+)+ y \d+)?", str(e.get("modulos", "")))),
                 f"{k}: dice qué módulos practica", str(e.get("modulos")))

    def paso(k, empieza):
        for p in S[k]["pasos"]:
            if p["paso"].startswith(empieza):
                return p["valor"]
        return None

    def mismo(k, empieza, valor, que, tol=1e-9):
        v = paso(k, empieza)
        if v is None:
            return a.cierto(False, que, f"falta el paso «{empieza}»")
        return a.igual(valor, v, que, tol=tol)

    def dice(k, texto, que):
        todo = " ".join(r["respuesta"] for r in S[k]["solucion"]["respuestas"])
        return a.cierto(texto in todo, que, texto)

    def silv(x):
        return bw_nrd(x)

    def fg(x, datos, h):
        return float(np.mean(phi((x - datos) / h)) / h)

    # E1
    X1 = np.array([2.5, 3.5, 5, 5.5, 7, 8.5, 10, 11, 11.5, 14])
    br = r_pretty(X1.min(), X1.max(), math.ceil(math.log2(len(X1)) + 1), 1)
    h1 = silv(X1)
    mismo("e1", "Intervalos del histograma", len(br) - 1, "e1: las clases de hist() por defecto")
    mismo("e1", "Ancho de cada intervalo", br[1] - br[0], "e1: su ancho")
    mismo("e1", "Modas del histograma por defecto", modas_secuencia(r_conteos(X1, br)),
          "e1: las modas del histograma por defecto")
    mismo("e1", "Ancho de banda de bw.nrd", h1, "e1: el ancho de bw.nrd")
    mismo("e1", "Suma de φ", float(phi(7 - X1).sum()), "e1: la suma de φ((7 − xᵢ)/1)")
    mismo("e1", "f̂(7) con h = 1", fg(7, X1, 1), "e1: f̂(7) con h = 1")
    g1 = r_seq_len(X1.min() - 3, X1.max() + 3, 400)
    m1 = modas_secuencia(kde_gauss(X1, g1, h1))
    mu1 = modas_secuencia(kde_gauss(X1, g1, 1.0))
    mismo("e1", "Modas con el ancho de bw.nrd", m1, "e1: modas con bw.nrd")
    mismo("e1", "Modas con h = 1", mu1, "e1: modas con h = 1")
    y1 = kde_gauss(X1, g1, 1.0)
    mx = np.flatnonzero(np.diff(np.sign(np.diff(y1))) == -2) + 1
    mn = np.flatnonzero(np.diff(np.sign(np.diff(y1))) == 2) + 1
    ib = int(mx[np.argmin(y1[mx])])
    lados = [y1[mn[mn < ib].max()]] if np.any(mn < ib) else []
    lados += [y1[mn[mn > ib].min()]] if np.any(mn > ib) else []
    valle = max(lados + [0.0])
    mismo("e1", "Altura de la moda menor", float(y1[ib]), "e1: la moda menor con h = 1", 1e-8)
    mismo("e1", "Altura del valle", float(valle), "e1: el valle que la separa", 1e-8)
    a.cierto(g1[ib] > X1.max() - 1 and y1[ib] - valle < 0.002, "e1: la moda del 14 apenas sobresale")
    ga = r_seq_len(X1.min() - 8 * h1, X1.max() + 8 * h1, 2001)
    mismo("e1", "Área de la curva", trapecio(ga, kde_gauss(X1, ga, h1)), "e1: el área de la curva", 1e-8)
    dice("e1", f"queda f̂(7) = {fg(7, X1, 1):.4f}", "e1: la respuesta da f̂(7)")
    dice("e1", f"la curva tiene {m1} moda; con h = 1, {mu1}", "e1: la respuesta da las modas")

    # E2
    X2 = np.array([1, 2, 3, 5, 6, 7, 9, 10], float)
    d2 = np.sort(np.abs(X2 - 4))
    mismo("e2", "Distancia al tercer vecino", d2[2], "e2: d₃")
    mismo("e2", "Longitud de la ventana", 2 * d2[2], "e2: la ventana 2d₃")
    mismo("e2", "f̂(4)", 3 / (2 * 8 * d2[2]), "e2: f̂(4) = k/(2nd₃)")
    den2 = int(np.sum(np.abs(X2 - 4) <= d2[2]))
    mismo("e2", "Observaciones dentro", den2, "e2: las observaciones dentro")
    dice("e2", f"aunque la ventana encierre {den2}", "e2: la respuesta da cuántas hay")

    # E3: la misma muestra que la mezcla del módulo 7
    X3 = np.asarray(D["m7"]["mezcla"]["muestra"], float)
    a.cierto("set.seed(2026)" in S["e3"]["enunciado"], "e3: el enunciado da la semilla 2026")
    g3 = r_seq_len(X3.min() - 1, X3.max() + 1, 300)
    f5, f10 = knn_curva(X3, g3, 5), knn_curva(X3, g3, 10)
    i75 = int(np.argmin(np.abs(g3 - 7.5)))
    # EN 7.5, no en el nodo más cercano (revisión 2).
    e5_, e10_ = (float(knn_curva(X3, np.array([7.5]), k)[0]) for k in (5, 10))
    ft = 0.5 * norm.pdf(7.5, 5, 1) + 0.5 * norm.pdf(7.5, 10, 1.5)
    mismo("e3", "f̂(7.5) con k = 5", e5_, "e3: f̂(7.5) con k = 5", 1e-5)
    mismo("e3", "f̂(7.5) con k = 10", e10_, "e3: f̂(7.5) con k = 10", 1e-5)
    mismo("e3", "Densidad verdadera", ft, "e3: la verdad en 7.5")
    mismo("e3", "Con k = 5, en el nodo", f5[i75], "e3: k = 5 en el nodo más cercano", 1e-5)
    mismo("e3", "Área de la curva con k = 5", trapecio(g3, f5), "e3: el área con k = 5", 1e-5)
    mismo("e3", "Área de la curva con k = 10", trapecio(g3, f10), "e3: el área con k = 10", 1e-5)
    dice("e3", f"casi el doble de la verdad, {ft:.4f}", "e3: la respuesta da la verdad")
    a.cierto("módulo 7" in S["e3"]["enunciado"], "e3: el enunciado dice que es la muestra del módulo 7")
    # Lo que la respuesta afirma de forma: con k = 5 se pasa, con k = 10 casi acierta.
    a.cierto(e5_ > 1.5 * ft and abs(e10_ / ft - 1) < 0.05,
             "e3: con k = 5 el valle se pasa y con k = 10 casi acierta")
    a.cerca(e5_, D["m7"]["mezcla"]["por_k"][1]["f_valle"], "e3: la misma cifra que el módulo 7", rel=1e-5)

    # E4
    X4 = np.array([2, 4, 4.5, 6, 6.5, 7, 9], float)
    # m impares: con pares el 3.5 ya da el valor del triangular (revisión 2).
    ms4 = (1, 3, 5, 9)
    v4 = [float(ash(X4, 1.0, mm, [3.5])[0]) for mm in ms4]
    for mm, v in zip(ms4, v4):
        mismo("e4", f"ASH en x = 3.5 con m = {mm}", v, f"e4: el ASH en 3.5 con m = {mm}")
    tri4 = float(np.mean(np.maximum(0, 1 - np.abs(3.5 - X4))))
    mismo("e4", "Núcleo triangular", tri4, "e4: el triangular de semiancho 1 en 3.5")
    g4 = r_seq_by(0, 11, 0.001)
    mismo("e4", "Área con m = 1", trapecio(g4, ash(X4, 1.0, 1, g4)), "e4: el área con m = 1", 1e-8)
    mismo("e4", "Área con m = 9", trapecio(g4, ash(X4, 1.0, 9, g4)), "e4: el área con m = 9", 1e-8)
    a.cierto(v4[0] == 0 and all(np.diff(v4) > 0) and all(v < tri4 for v in v4),
             "e4: el hueco de 3.5 sube hacia el triangular")
    a.cierto(abs(float(ash(X4, 1.0, 2, [3.5])[0]) - tri4) < 1e-12, "e4: con m par ya sale el triangular")
    a.cierto("[a, a + 1)" in S["e4"]["enunciado"], "e4: el enunciado fija la convención de los cortes")
    dice("e4", f"pasa de {v4[0]:.4f} a {v4[1]:.4f}, {v4[2]:.4f} y {v4[3]:.4f}", "e4: la respuesta da el hueco")

    # E5
    X5 = np.array([1, 2, 3, 3.5, 5, 5.5, 6, 8])
    u5 = 4 - X5
    uni_ = lambda u: np.where(np.abs(u) <= 1, 0.5, 0.0)            # noqa: E731
    tri_ = lambda u: np.where(np.abs(u) <= 1, 1 - np.abs(u), 0.0)  # noqa: E731
    h5 = silv(X5)
    mismo("e5", "Uniforme, h = 1", uni_(u5).mean(), "e5: uniforme con h = 1")
    mismo("e5", "Triangular, h = 1", tri_(u5).mean(), "e5: triangular con h = 1")
    mismo("e5", "Gaussiano, h = 1", float(phi(u5).mean()), "e5: gaussiano con h = 1")
    mismo("e5", "Ancho de bw.nrd", h5, "e5: el ancho de bw.nrd")
    sop = [uni_(u5 / h5).mean() / h5, tri_(u5 / h5).mean() / h5, float(phi(u5 / h5).mean()) / h5]
    # La convención de density(): bw es la desviación típica, así que la caja
    # llega a √3·bw y el triangular a √6·bw.
    a3, a6 = np.sqrt(3) * h5, np.sqrt(6) * h5
    sd_ = [uni_(u5 / a3).mean() / a3, tri_(u5 / a6).mean() / a6, sop[2]]
    mismo("e5", "Uniforme, bw.nrd como semiancho", sop[0], "e5: uniforme, bw.nrd como semiancho")
    mismo("e5", "Triangular, bw.nrd como semiancho", sop[1], "e5: triangular, bw.nrd como semiancho")
    mismo("e5", "Gaussiano, bw.nrd como desviación", sop[2], "e5: gaussiano con bw.nrd")
    mismo("e5", "Uniforme, bw.nrd como desviación", sd_[0], "e5: uniforme, bw.nrd como desviación")
    mismo("e5", "Triangular, bw.nrd como desviación", sd_[1], "e5: triangular, bw.nrd como desviación")
    a.cierto(np.ptp(sd_) < 0.5 * np.ptp(sop),
             "e5: con la misma desviación típica los núcleos se parecen más")
    dice("e5", f"como desviación típica, {sd_[0]:.4f}, {sd_[1]:.4f} y {sd_[2]:.4f}",
         "e5: la respuesta da las dos escalas")
    dice("e5", f"La suma es {tri_(u5).sum():.1f} contra {uni_(u5).sum():.1f}", "e5: la respuesta da las sumas")

    # E6
    X6 = np.array([10, 12, 13, 15, 15.5, 17, 19, 20])
    d6 = np.sort(np.abs(X6 - 14))
    f6 = np.arange(1, 9) / (2 * 8 * d6)
    for k in range(1, 9):
        mismo("e6", f"f̂(14) con k = {k} (d = {d6[k - 1]:g})", f6[k - 1], f"e6: f̂(14) con k = {k}")
    a.cierto(not np.all(np.diff(f6) >= 0) and not np.all(np.diff(f6) <= 0),
             "e6: la curva contra k no es monótona")
    dice("e6", f"de {f6[0]:.4f} a {f6[1]:.4f}", "e6: la respuesta da el salto de k = 1 a 2")

    # E7
    X7 = np.array([2, 3, 4, 6, 7, 8, 10, 11], float)
    h7 = silv(X7)
    d7 = np.sort(np.abs(X7 - 5))
    p7, k7 = fg(5, X7, h7), 3 / (2 * 8 * d7[2])
    mismo("e7", "Ancho de bw.nrd", h7, "e7: el ancho de bw.nrd")
    mismo("e7", "Parzen gaussiano en 5", p7, "e7: Parzen en 5")
    mismo("e7", "Distancia al tercer vecino", d7[2], "e7: d₃")
    mismo("e7", "k-NN en 5", k7, "e7: k-NN en 5")
    mismo("e7", "Cociente", k7 / p7, "e7: el cociente k-NN / Parzen")
    dice("e7", f"El cociente, {k7 / p7:.4f}", "e7: la respuesta da el cociente")
    knn7 = np.arange(1, 9) / (2 * 8 * d7)
    mismo("e7", "k-NN en 5 con k = 1", knn7[0], "e7: k-NN con k = 1")
    mismo("e7", "k-NN en 5 con k = 2, 4 o 6", knn7[1], "e7: k-NN con k = 2, 4 o 6")
    a.cierto(knn7[1] == knn7[3] == knn7[5] and abs(knn7[1] / p7 - 1) > 0.3,
             "e7: con k = 2, 4 y 6 da lo mismo, lejos de Parzen")
    dice("e7", f"en buena parte por casualidad: con k = 2, 4 o 6 el k-NN da {knn7[1]:.4f}",
         "e7: la respuesta dice que es en parte casual")

    # E8
    X8 = np.array([3, 5, 2, 4, 3, 6, 5, 7, 4, 5, 8, 2, 3, 4, 6, 5, 4, 5, 7], float)
    d8 = np.sort(np.abs(X8 - 5))
    k8 = int(np.flatnonzero(d8 > 0)[0]) + 1
    mismo("e8", "Clientes que esperaron", int(np.sum(X8 == 5)), "e8: los empatados en 5")
    mismo("e8", "Altura de la barra", np.sum(X8 == 5) / 19, "e8: la altura de la barra de 5")
    mismo("e8", "Ancho de bw.nrd", silv(X8), "e8: el ancho de bw.nrd")
    mismo("e8", "Parzen en 5", fg(5, X8, silv(X8)), "e8: Parzen en 5")
    mismo("e8", "Menor k", k8, "e8: el menor k que se puede usar")
    mismo("e8", "k-NN en 5", k8 / (2 * 19 * d8[k8 - 1]), "e8: k-NN en 5 con ese k")
    dice("e8", f"k = {k8}.", "e8: la respuesta da el k")
    den8 = int(np.sum(np.abs(X8 - 5) <= d8[k8 - 1]))
    mismo("e8", "Observaciones dentro de su ventana", den8, "e8: lo que encierra la ventana del k-NN")
    mismo("e8", "Clientes que esperaron 4 minutos o menos", int(np.sum(X8 <= 4)), "e8: los de 4 min o menos")
    mismo("e8", "Clientes que esperaron 6 minutos o más", int(np.sum(X8 >= 6)), "e8: los de 6 min o más")
    a.cierto(den8 > k8 and k8 / (2 * 19 * d8[k8 - 1]) < fg(5, X8, silv(X8)) < np.sum(X8 == 5) / 19,
             "e8: el k-NN da la cifra más baja de las tres")

    # E9
    X9 = np.array([165, 170, 172, 168, 174, 175, 169, 171, 173, 175, 167, 168, 174, 176, 170, 172.])
    w9 = tri_((170 - X9) / 2)
    d9 = np.sort(np.abs(X9 - 170))
    w9b = tri_((174 - X9) / 2)
    mismo("e9", "Suma de los pesos triangulares en 170", w9.sum(), "e9: la suma de pesos en 170")
    mismo("e9", "Parzen triangular en 170", w9.sum() / (16 * 2), "e9: Parzen triangular en 170")
    mismo("e9", "Distancia al cuarto vecino", d9[3], "e9: d₄")
    mismo("e9", "k-NN en 170", 4 / (2 * 16 * d9[3]), "e9: k-NN en 170")
    mismo("e9", "Suma de los pesos triangulares en 174", w9b.sum(), "e9: la suma de pesos en 174")
    mismo("e9", "Parzen triangular en 174", w9b.sum() / (16 * 2), "e9: Parzen triangular en 174")
    # La meseta: los centímetros donde la curva no baja de su valor en 170.
    cm = np.arange(165, 178)
    p_cm = np.array([tri_((c - X9) / 2).sum() / 32 for c in cm])
    alta = cm[p_cm >= w9.sum() / 32 - 1e-12]
    a.cierto(alta.min() == 168 and alta.max() == 175 and bool(np.all(np.diff(alta) == 1)),
             "e9: la meseta va de 168 a 175 cm", str(alta))
    meseta = int(np.sum((X9 >= alta.min()) & (X9 <= alta.max())))
    mismo("e9", f"Estudiantes entre {alta.min()} y {alta.max()}", meseta, "e9: los que están en la meseta")
    dice("e9", f"ahí están {meseta} de los 16", "e9: la respuesta da la meseta")
    a.cierto(w9b.sum() > w9.sum() and w9b.sum() - w9.sum() < 1, "e9: de 170 a 174 sube menos de un dato")

    # E10: Kennedy
    nnk, wk = nn_spatstat(ctx["ken"])
    idx = np.arange(len(nnk))
    rk = wk[wk] == idx
    par = nnk[(~rk) | (idx < wk)]
    par0 = par[par > 0]
    RK, K0 = RK_GAUSS, float(norm.pdf(0))
    umbral = RK / (4 * K0 - 2 * RK)
    ek = empates(nnk) / len(nnk)
    hk, avk = bw_cv_r(nnk, "ucv")
    hk0, _ = bw_cv_r(par0, "ucv")
    sk0 = bw_sj_r(par0)
    ux, ux0 = ucv_exacta(nnk, 0.001), ucv_exacta(par0, 0.001)
    ux20, ux020 = ucv_exacta(nnk, 20.0), ucv_exacta(par0, 20.0)
    mismo("e10", "Sedes", len(nnk), "e10: las sedes de Kennedy")
    mismo("e10", "Distancias iguales a cero", int((nnk == 0).sum()), "e10: las distancias cero")
    mismo("e10", "Fracción recíproca", 100 * rk.mean(), "e10: el % recíproco")
    mismo("e10", "Parejas empatadas por dato", ek, "e10: las parejas empatadas por dato")
    mismo("e10", "Umbral del núcleo", umbral, "e10: el umbral gaussiano")
    mismo("e10", "bw.ucv con todas", hk, "e10: bw.ucv con todas (portado)", 1e-7)
    mismo("e10", "UCV exacta con h = 0.001 m, todas", ux, "e10: UCV exacta, todas", 1e-8)
    mismo("e10", "UCV exacta con h = 0.001 m, una", ux0, "e10: UCV exacta, una/pareja sin 0", 1e-8)
    mismo("e10", "UCV exacta con h = 20 m, todas", ux20, "e10: UCV exacta con 20 m, todas", 1e-8)
    mismo("e10", "UCV exacta con h = 20 m, una", ux020, "e10: UCV exacta con 20 m, una/pareja", 1e-8)
    # Dentro del intervalo de bw.ucv: dos mínimos locales, y el más bajo no
    # es el suyo (revisión 2).
    hmax_k = 1.144 * sd(nnk) * len(nnk) ** (-1 / 5)
    mismo("e10", "Intervalo en que busca bw.ucv, desde", 0.1 * hmax_k, "e10: el intervalo, desde", 1e-8)
    mismo("e10", "Intervalo en que busca bw.ucv, hasta", hmax_k, "e10: el intervalo, hasta", 1e-8)
    hh_k = r_seq_len(0.1 * hmax_k, hmax_k, 400)
    uu_k = np.array([ucv_exacta(nnk, h) for h in hh_k])
    loc = np.flatnonzero(np.diff(np.sign(np.diff(uu_k))) > 0) + 1
    a.cierto(len(loc) >= 2, "e10: el criterio exacto tiene dos mínimos locales", str(hh_k[loc]))
    if len(loc) >= 2:
        # Refinados con un Brent propio alrededor de cada nodo (revisión 2).
        fk = lambda h: ucv_exacta(nnk, h)  # noqa: E731
        ref = [brent_fmin(hh_k[max(i - 2, 0)], hh_k[min(i + 2, len(hh_k) - 1)], fk, 1e-7) for i in loc]
        val = [fk(h) for h in ref]
        bajo = float(ref[int(np.argmin(val))])
        otro = float(ref[int(np.argmin(np.abs(np.array(ref) - hk)))])
        mismo("e10", "Mínimo local más bajo", bajo, "e10: el mínimo local más bajo", 1e-4)
        mismo("e10", "Mínimo local junto al de bw.ucv", otro, "e10: el mínimo junto al de bw.ucv", 1e-4)
        a.cierto(bajo < 10 and abs(otro - hk) < 2, "e10: el más bajo no es el de bw.ucv")
        # La búsqueda de bw.ucv, sobre el criterio EXACTO: cae en el mismo valle.
        ok_ = brent_fmin(0.1 * hmax_k, hmax_k, fk, 0.1 * 0.1 * hmax_k)
        mismo("e10", "optimize sobre el criterio exacto", ok_, "e10: optimize sobre el criterio exacto", 1e-3)
        a.cierto(abs(ok_ - otro) < 0.5, "e10: y cae en el valle de bw.ucv, no en el más bajo")
    mismo("e10", "bw.ucv con una por pareja", hk0, "e10: bw.ucv una/pareja sin 0 (portado)", 1e-7)
    mismo("e10", "bw.SJ con una por pareja", sk0, "e10: bw.SJ una/pareja sin 0 (portado)", 1e-7)
    v_sj = paso("e10", "bw.SJ con una por pareja")
    v_uc = paso("e10", "bw.ucv con una por pareja")
    a.cerca(sj_exacto(par0), v_sj if v_sj is not None else float("nan"),
            "e10: SJ exacto, sin agrupar", rel=TOL_AGRUPADO)
    a.cerca(ucv_exacta_min(par0), v_uc if v_uc is not None else float("nan"),
            "e10: UCV exacta minimizada, sin agrupar", rel=TOL_UCV)
    a.cierto(not avk and ek > umbral and ux < ux20 and ux0 > ux020 and abs(hk0 / sk0 - 1) < 0.25,
             "e10: sin aviso, sin mínimo; sin empates, junto a SJ")
    c = 6 * math.pi / (8 * math.pi + 3 * math.sqrt(3))
    dice("e10", f"El {100 * rk.mean():.1f} %, del orden del {100 * c:.1f} %", "e10: la respuesta da el %")
    dice("e10", f"devuelve {hk:.2f} m sin ningún aviso", "e10: la respuesta da bw.ucv")
    dice("e10", f"son {ek:.3f} por dato, por encima del umbral {umbral:.4f}",
         "e10: la respuesta da empates y umbral")


def csv_python(a, D, caf, fai, mzc):
    a.titulo("13b · Los CSV que leen las pestañas de Python")
    t = np.asarray(D["m1"]["tiempos"], float)
    tc = caf["tiempo"].to_numpy(float) if "tiempo" in caf else np.array([])
    a.igual(len(tc), len(t), "csv: la cafetería trae los 100 tiempos")
    if len(tc) == len(t):
        vec(a, tc, t, "csv: la cafetería es la del JSON (r10 contra r6)", 5.0e-7 + 5.1e-11)
        a.igual(tc.mean(), D["m1"]["media"], "csv: su media, a 8 decimales", tol=T8)
        a.igual(float(np.median(tc)), D["m1"]["mediana"], "csv: su mediana, a 8 decimales", tol=T8)
    E = np.asarray(D["m2"]["eruptions"], float)
    ok = list(fai.columns) == ["eruptions", "waiting"] and len(fai) == len(E)
    a.cierto(ok, "csv: faithful trae sus 272 filas y dos columnas", str(list(fai.columns)))
    if ok:
        vec(a, fai["eruptions"].to_numpy(float), E, "csv: faithful, las erupciones del JSON", 0)
        w = fai["waiting"].to_numpy(float)
        a.igual(w.mean(), 70.897059, "csv: faithful, espera media 70.897059 (lit.)", tol=6e-7)
        a.igual(sd(w), 13.594974, "csv: faithful, sd de la espera 13.594974 (lit.)", tol=6e-7)
    mez = np.asarray(D["m7"]["mezcla"]["muestra"], float)
    mv = mzc["valor"].to_numpy(float) if "valor" in mzc else np.array([])
    a.igual(len(mv), len(mez), "csv: la mezcla trae los 200 datos")
    if len(mv) == len(mez):
        vec(a, mv, mez, "csv: la mezcla es la del JSON (r10 contra r6)", 5.0e-7 + 5.1e-11)
        a.igual(mv.min(), D["m7"]["mezcla"]["rejilla"]["desde"], "csv: la mezcla empieza donde la rejilla", tol=T8)
        a.igual(mv.max(), D["m7"]["mezcla"]["rejilla"]["hasta"], "csv: y acaba donde la rejilla", tol=T8)


def formato(a, D, S, p_datos, p_sols, mc, ms):
    a.titulo("14 · Formato")
    for nombre, obj in (("datos", D), ("soluciones", S)):
        nans = list(sin_nan(obj))
        a.cierto(not nans, f"fmt: {nombre}, sin NaN ni infinitos", str(nans[:3]))
    for nombre, p in (("datos", p_datos), ("soluciones", p_sols)):
        txt = p.read_text(encoding="utf-8")
        a.cierto('"NA"' not in txt, f"fmt: {nombre}, ningún NA escrito como texto")
        a.cierto("Ã" not in txt and "�" not in txt and "<c3>" not in txt.lower()
                 and "<U+" not in txt, f"fmt: {nombre}, las tildes están intactas")
        a.cierto("ó" in txt or "í" in txt, f"fmt: {nombre}, y hay tildes que comprobar")
    exc = [(r, k) for r, k in decimales(D) if k > 8]
    a.cierto(not exc, "fmt: datos, ningún flotante pasa de 8 decimales", str(exc[:3]))
    exc = [(r, k) for r, k in decimales(S) if k > 10]
    a.cierto(not exc, "fmt: soluciones, ninguno pasa de 10 decimales", str(exc[:3]))
    kb = p_datos.stat().st_size / 1024
    a.cierto(kb <= 400, "fmt: datos, cabe en su presupuesto", f"{kb:.1f} KB de 400")
    col = ["replica"] + [f"{p}_{s}" for s in ("nrd0", "nrd", "ucv", "bcv", "SJ") for p in ("h", "ise")] \
        + [f"aviso_{s}" for s in ("nrd0", "nrd", "ucv", "bcv", "SJ")]
    a.cierto(list(mc.columns) == col, "fmt: el CSV del Monte Carlo trae sus 16 columnas")
    a.cierto(list(ms.columns) == ["replica", "y"], "fmt: el CSV de muestras trae replica e y")
    a.cierto(not mc.isna().any().any() and not ms.isna().any().any(), "fmt: los CSV no traen huecos")
    me = D["meta"]
    a.cierto(me.get("apendice") == "A", "fmt: la metainformación dice apéndice A")
    a.igual(me.get("semilla"), 2026, "fmt: y la semilla de la casa")
    a.cierto("JMS_Densidades.Rmd" in str(me.get("fuente", "")), "fmt: la fuente es el documento del profesor")
    a.cierto(me.get("anclas", 0) >= 20 and me.get("guardas", 0) >= 50,
             "fmt: el generador comprobó anclas y guardas",
             f"{me.get('anclas')} anclas, {me.get('guardas')} guardas")


def main() -> int:
    a = Auditoria("Precálculo del apéndice A verificado")
    D, p_datos = carga("APA_DATOS", "apendicea_datos.json")
    S, p_sols = carga("APA_SOLUCIONES", "apendicea_soluciones.json")
    mc = pd.read_csv(ruta_csv("APA_MC", "apendicea_mc.csv"))
    ms = pd.read_csv(ruta_csv("APA_MUESTRAS", "apendicea_mc_muestras.csv"))
    caf = pd.read_csv(ruta_csv("APA_CAFETERIA", "apendicea_cafeteria.csv"))
    fai = pd.read_csv(ruta_csv("APA_FAITHFUL", "apendicea_faithful.csv"))
    mzc = pd.read_csv(ruta_csv("APA_MEZCLA", "apendicea_mezcla.csv"))
    ctx: dict = {}
    datos_de_partida(a, D, ctx)
    nn, quien = nn_spatstat(ctx["sed"])
    ctx["nn"], ctx["quien"] = nn, quien
    semilla(a, D, ctx)
    modulo1(a, D, ctx)
    modulo2(a, D, ctx)
    modulo3(a, D, ctx)
    modulo4(a, D, ctx)
    modulo5(a, D, ctx)
    modulo6(a, D, ctx)
    modulo7(a, D, ctx)
    modulo8(a, D, ctx)
    modulo9(a, D, ctx)
    modulo10(a, D, ctx)
    modulo11(a, D, ctx, mc, ms)
    modulo12(a, D, ctx)
    ejercicios(a, S, D, ctx)
    csv_python(a, D, caf, fai, mzc)
    formato(a, D, S, p_datos, p_sols, mc, ms)
    return a.cierre()


if __name__ == "__main__":
    sys.exit(main())
