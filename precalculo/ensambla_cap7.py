#!/usr/bin/env python3
"""
ensambla_cap7.py — el capítulo 7 escrito sobre la plantilla (T4.5)

  «Autocorrelación espacial global y local»
  semanas 12-13 · Material de Estadística Espacial 2026-II (20929).

QUÉ HACE. Estampa `plantilla/plantilla-capitulo.html` con los doce módulos
del capítulo, sus simuladores, sus mapas, su autoevaluación y sus
ejercicios, y escribe `Htmls_Espacial/capitulo-7-autocorrelacion.html`.

LA REGLA QUE MANDA (D10): ninguna cifra se escribe aquí. Todas salen de
`cap7_datos.json` (o de `cap7_soluciones.json`), por un formateador. Lo
vigila `sin_aritmetica.py`, que mira el CÓDIGO y no el resultado.

LOS TRES TABLEROS, decididos por Javier el 2026-09-08 sobre el cronómetro
del A.28 del plan:

  · COLUMBUS (49 barrios) es el LABORATORIO, y EN EL ORDEN DE ANSELIN:
    `spdep::oldcol` trae la GAL de 1988 y el `columbus.gpkg` los polígonos,
    y los dos no vienen en el mismo orden. Reordenados por POLYID, la GAL
    reproduce las cifras de Anselin (1995) —I = 0.511, z = 5.63—, que son
    las anclas del capítulo.
  · LOS 1 121 MUNICIPIOS con deserción son el CASO REAL: 2 islas, un
    mapa de 179 KB que el módulo 9 declara, y un LISA donde Bonferroni
    solo es alcanzable con 44 760 réplicas o más (el capítulo usa 49 999).
  · LA REJILLA DE GETIS Y ORD (16 × 16) es la del artículo original, para
    el módulo 11.

EL p DEL CAPÍTULO es el BILATERAL por rangos con 49 999 réplicas y
`no_repeat_in_row = TRUE`, y Gi* con la unidad dentro de la permutación
(`fix_i_in_Gstar_permutations = FALSE`). Hasta la auditoría de contenido
del 2026-10-20 era el plegado de GeoDa y `esda` con 24 999: el plegado es
de una cola, y bajo la nula marca el 10 % al 5 % (medido en el módulo 10).
Javier decidió pasar los mapas al bilateral y medir el plegado en vez de
callarlo. Los otros p que `localmoran_perm` devuelve son material del
módulo 10, no un descuido.

EL MOTOR DE MAPAS gana aquí la CAPA CATEGÓRICA (lado del navegador; el lado
R lo escribió T4.4 en `geo.R`): un mapa LISA son cinco categorías con su
color, uno de Gi* siete, y «sin dato o sin vecinos» se pinta rayado. Vive
en la plantilla, así que todos los capítulos la heredan al reensamblarse.

Uso:  python3 precalculo/ensambla_cap7.py
Devuelve 1 mientras el capítulo esté a medias, y lo dice.
"""
from __future__ import annotations

import html as _html
import json
import pathlib
import re
import sys

from baraja_opciones import baraja_documento

RAIZ = pathlib.Path(__file__).resolve().parent.parent
from pon_boton_indice import aplica as aplica_boton
PLANTILLA = RAIZ / "plantilla" / "plantilla-capitulo.html"
SALIDAS = RAIZ / "precalculo" / "salidas"
DESTINO = RAIZ / "Htmls_Espacial" / "capitulo-7-autocorrelacion.html"

D = json.loads((SALIDAS / "cap7_datos.json").read_text(encoding="utf-8"))
M = json.loads((SALIDAS / "cap7_mapas.json").read_text(encoding="utf-8"))
SOL = json.loads((SALIDAS / "cap7_soluciones.json").read_text(encoding="utf-8"))

m1, m2, m3, m4 = D["m1"], D["m2"], D["m3"], D["m4"]
m5, m6, m7, m8 = D["m5"], D["m6"], D["m7"], D["m8"]
m9, m10, m11 = D["m9"], D["m10"], D["m11"]

# Los atajos que la prosa usa sin parar: el tablero de laboratorio y el real
# de cada módulo, y las W por su identificador.
C1, M1 = m1["columbus"], m1["municipios"]
C2 = m2["columbus"]
C3, M3 = m3["columbus"], m3["municipios"]
C4, M4 = m4["columbus"], m4["municipios"]
C5 = m5["columbus"]
EST = {e["id"]: e for e in m2["estilos"]}
CG = m6["correlograma"]
JC = m6["join_count"]
W7 = {e["id"]: e for e in m7["columbus"]}
W7M = {e["id"]: e for e in m7["municipios"]}
C8, M8 = m8["columbus"], m8["municipios"]
T10C, T10M = m10["columbus"]["tabla"], m10["municipios"]["tabla"]
GO = m11["getisord"]
DISC = {d["id"]: d for d in D["discrepancias"]}
POT = {c["n"]: c for c in m3["potencia"]["curvas"]}
_RHO = m1["reticulo"]["I_por_rho"]   # la pendiente frente a ρ (0.2, 0.5, 0.8)
# El error típico de una proporción del 5 % con las réplicas de la potencia, y
# la guarda de lo que la prosa afirma: las cuatro curvas, en ρ = 0, a menos de
# dos errores del alfa.
_SE_POT = (m3["potencia"]["alfa"] * (1 - m3["potencia"]["alfa"]) / m3["potencia"]["replicas"]) ** 0.5
if any(abs(c["potencia"][0] - m3["potencia"]["alfa"]) >= 2 * _SE_POT for c in m3["potencia"]["curvas"]):
    sys.exit("PARADO: alguna curva de potencia se aparta del 5 % en más de dos errores típicos")
if max(m3["potencia"]["curvas"], key=lambda c: abs(c["potencia"][0] - m3["potencia"]["alfa"]))["n"] != 25:
    sys.exit("PARADO: la curva que más se aparta del 5 % ya no es la de 25 celdas")

MODULOS_OBJETIVO = 12


def n(x, d=5):
    return f"{float(x):.{d}f}"


def ent(x):
    """Entero con espacio fino U+202F. NO usar dentro de KaTeX ni de código."""
    return f"{int(round(float(x))):,}".replace(",", " ")


def ent_codigo(x):
    """Entero SIN separador de millares, para dentro de un bloque de código:
    `#> [1] 1121` es lo que R imprime, y un fino ahí no casaría nunca."""
    return str(int(round(float(x))))


def pct(x, d=1):
    """Porcentaje con PUNTO decimal, como el resto del curso (A.32 del plan)
    y con el espacio duro delante del signo, para que no se parta."""
    return f"{float(x):.{d}f} %"


_SUPER = str.maketrans("-0123456789", "⁻⁰¹²³⁴⁵⁶⁷⁸⁹")


def cient(x, cifras=4):
    """Un p diminuto en notación científica legible: 6.008·10⁻¹⁰¹.

    La mantisa sale del JSON tal cual (R la guardó con `signif(·, 4)`), así
    que el auditor de prosa la reconoce; el exponente va en superíndice."""
    mant, exp = f"{float(x):.{cifras - 1}e}".split("e")
    mant = mant.rstrip("0").rstrip(".")
    return f"{mant}·10{str(int(exp)).translate(_SUPER)}"


def firma(valor, unidad=""):
    return f"<strong>{valor}</strong>{unidad}"


def cabecera(num, titulo, ingles, objetivo):
    limpio = re.sub(r"<[^>]+>", "", titulo)
    return f"""
  <!-- ============================================================ -->
  <!-- MÓDULO {num} · {limpio[:52]:<52} -->
  <!-- ============================================================ -->
  <template id="module-{num}">
    <div class="animate-fade-in">
      <div class="border-b border-gray-100 pb-6 mb-6">
        <div class="flex items-center space-x-2 text-sm text-secondary font-semibold mb-2 uppercase tracking-wide">
          <span>Módulo {num}</span>
        </div>
        <h2 class="text-3xl font-bold text-gray-900 mb-4" style="border:none; padding:0;">{titulo}
          <span class="text-gray-400 font-normal text-2xl">/ {ingles}</span></h2>
        <div class="bg-gray-50 rounded-lg p-4 border border-gray-200 flex items-start gap-3">
          <span class="text-xl">🎯</span>
          <div>
            <h3 class="font-bold text-gray-800 text-sm" style="margin:0;">Objetivo</h3>
            <p class="text-gray-600 text-sm" style="margin:0;">{objetivo}</p>
          </div>
        </div>
      </div>
"""


CIERRE = """    </div>
  </template>
"""


def tabs(etiqueta, r_code, py_code):
    return f"""      <div class="code-tabs">
        <div class="code-tabs-nav" role="tablist" aria-label="{etiqueta}">
          <button class="code-tab-btn active" data-lang="r" role="tab" aria-selected="true">R</button>
          <button class="code-tab-btn" data-lang="python" role="tab" aria-selected="false">Python</button>
        </div>
        <div class="code-tab-panel" data-lang="r">
          <pre><code class="language-r">{r_code}</code></pre>
        </div>
        <div class="code-tab-panel" data-lang="python" hidden>
          <pre><code class="language-python">{py_code}</code></pre>
        </div>
      </div>
"""


def sim(ident, titulo, pie="", alto=260, mandos=True, aria=None):
    icono = "fa-sliders" if mandos else "fa-chart-column"
    return f"""      <div class="simulador" data-simulador="{ident}">
        <h4><i class="fas {icono}" aria-hidden="true"></i> {titulo}</h4>
        {f'<p class="simulador-intro">{pie}</p>' if pie else ''}
{'        <div class="simulador-controles"></div>' + chr(10) if mandos else ''}        <div class="grafico-wrapper" style="height:{alto}px;">
          <canvas role="img" aria-label="{aria or titulo}"></canvas>
        </div>
        <div class="simulador-lectura"></div>
      </div>
"""


def sim_doble(ident, titulo, pie, aria_a, aria_b, alto=280):
    """Un simulador con DOS lienzos lado a lado (el retículo y su diagrama).

    Los dos van en el marcado con su `aria-label`, que es lo que cuenta el
    auditor de accesibilidad; el primero lo pinta el simulador a mano y el
    segundo es un Chart.js. En el teléfono se apilan (`.cap7-par`)."""
    return f"""      <div class="simulador" data-simulador="{ident}">
        <h4><i class="fas fa-sliders" aria-hidden="true"></i> {titulo}</h4>
        <p class="simulador-intro">{pie}</p>
        <div class="simulador-controles"></div>
        <div class="cap7-par">
          <div class="cap7-reticulo"><canvas class="cap7-lienzo-a" role="img" aria-label="{aria_a}"></canvas></div>
          <div class="grafico-wrapper" style="height:{alto}px;"><canvas class="cap7-lienzo-b" role="img" aria-label="{aria_b}"></canvas></div>
        </div>
        <div class="simulador-lectura"></div>
      </div>
"""


def mandos_html(ident, titulo, pie):
    """Un simulador SIN lienzo propio: solo botones y lectura, que mueven un
    `.geomapa` del módulo. El mapa es el lienzo."""
    return f"""      <div class="simulador" data-simulador="{ident}">
        <h4><i class="fas fa-sliders" aria-hidden="true"></i> {titulo}</h4>
        <p class="simulador-intro">{pie}</p>
        <div class="simulador-controles"></div>
        <div class="simulador-lectura"></div>
      </div>
"""


def fila(*celdas):
    cab, resto = celdas[0], celdas[1:]
    return ('            <tr><th scope="row">' + str(cab) + '</th>'
            + ''.join('<td>' + str(c) + '</td>' for c in resto) + '</tr>\n')


def tabla(cabeceras, filas, titulo=""):
    th = "".join(f'<th scope="col">{c}</th>' for c in cabeceras)
    cap = f'        <p class="tabla-titulo">{titulo}</p>\n' if titulo else ""
    return (cap + '        <div class="tabla-envoltorio">\n'
            '          <table class="tabla-datos">\n'
            f'            <thead><tr>{th}</tr></thead>\n'
            '            <tbody>\n' + filas +
            '            </tbody>\n          </table>\n        </div>\n')


def quiz_html(ident, titulo, bajada):
    return f"""      <div class="quiz" data-quiz="{ident}">
        <h4><i class="fas fa-circle-question" aria-hidden="true"></i> {titulo}</h4>
        <p class="text-sm" style="margin-bottom:0;">{bajada}</p>
        <div class="quiz-progreso" role="presentation"><div class="quiz-progreso-barra"></div></div>
        <div class="quiz-preguntas"></div>
        <div class="quiz-resumen" role="status" hidden></div>
        <div class="quiz-marcador">
          <span class="quiz-conteo"></span>
          <button type="button" class="quiz-reiniciar">Reiniciar</button>
        </div>
      </div>
"""


def mapa_html(ident, titulo):
    return f"""      <div class="geomapa" data-geomapa="{ident}">
        <p class="geomapa-titulo">{titulo}</p>
        <div class="geomapa-marco">
          <canvas class="geomapa-lienzo" role="img" aria-label="{titulo}"></canvas>
        </div>
        <div class="geomapa-pie-caja"></div>
      </div>
"""


def par_mapas(a, ta, b, tb):
    """Dos mapas lado a lado (LISA frente a Gi*); en el teléfono, apilados."""
    return ('      <div class="cap7-par cap7-par-mapas">\n'
            + mapa_html(a, ta).replace("      ", "        ", 1)
            + mapa_html(b, tb).replace("      ", "        ", 1)
            + '      </div>\n')


# EL SUBTÍTULO ES EL DE LA BARRA LATERAL Y VA EN ESPAÑOL; el inglés es la
# glosa del `<h2>`. Y los títulos van en HTML, nunca en Markdown: el índice
# lateral los pinta con `innerHTML` y un acento grave saldría a la vista
# (lo que le pasó al módulo 9 del capítulo 5).
TITULOS = (
    ("La pregunta", "¿Lo cercano se parece más que por azar?"),
    ("El índice de Moran", "La fórmula, E[I] y su rango real"),
    ("Inferencia", "Normalidad, aleatorización y permutación"),
    ("El diagrama de Moran", "La pendiente es I"),
    ("La c de Geary", "Diferencias en vez de productos"),
    ("Correlograma y join count", "Por órdenes, y con una variable binaria"),
    ("Moran es sensible a W", "Once vecindades para el mismo dato"),
    ("Del global al local", "La descomposición de Anselin"),
    ("El mapa LISA", "Conglomerados, atípicos e islas"),
    ("La trampa de la multiplicidad", "Bonferroni, FDR y el suelo del p"),
    ("Getis-Ord G<sub>i</sub> y G<sub>i</sub>*", "Intensidad, no similitud"),
    ("Autoevaluación y ejercicios", "Trece preguntas y cinco ejercicios"),
)

INGLES = (
    "The question", "Moran's I", "Inference", "The Moran scatterplot",
    "Geary's c", "Correlogram and join counts", "Moran depends on W",
    "From global to local", "The LISA cluster map", "The multiple-testing trap",
    "Getis-Ord Gi and Gi*", "Self-assessment and guided exercises",
)


# =====================================================================
# LOS BLOQUES DE CÓDIGO VAN APARTE DE LA PROSA (trampa 4 del §0.6: un literal
# de tres comillas dentro de una f-string la cierra a media expresión).
#
# Se escriben LIMPIOS —R y Python tal como los teclea el estudiante— y
# `bloque()` los escapa para HTML y rellena los `#>`. Los huecos van con
# comillas latinas y en MAYÚSCULAS, «ASÍ», y no con llaves: el código de R
# está lleno de llaves y `$`, y `.format()` o `Template` obligarían a
# escaparlas todas. Las «palabras» en minúscula de los comentarios no son
# huecos. Ningún `#>` se escribe a mano: o sale del JSON o es un lógico.
# `verifica_bloques.py` los ejecuta y comprueba cada uno.
# =====================================================================
_HUECO = re.compile(r"«([A-Z][A-Z0-9_]*)»")


def bloque(texto, **subs):
    faltan = sorted(set(_HUECO.findall(texto)) - set(subs))
    if faltan:
        sys.exit(f"PARADO: huecos sin valor en un bloque de código: {faltan}")
    sobran = sorted(set(subs) - set(_HUECO.findall(texto)))
    if sobran:
        sys.exit(f"PARADO: valores que ningún hueco usa: {sobran}")
    lleno = _HUECO.sub(lambda m: str(subs[m.group(1)]), texto)
    return _html.escape(lleno, quote=True)


R1 = r'''library(sf)
library(spdep)

# Columbus EN EL ORDEN DE ANSELIN. `oldcol` trae su lista de vecinos (la GAL
# de 1988) y el .gpkg los polígonos, y NO vienen en el mismo orden:
data(oldcol, package = "spdep")
col0 <- st_read(system.file("shapes/columbus.gpkg", package = "spData"), quiet = TRUE)
identical(col0$POLYID, COL.OLD$POLYID)
#> [1] FALSE

# Se reordenan los polígonos por POLYID, y ya casan con la GAL
col <- col0[match(COL.OLD$POLYID, col0$POLYID), ]
gal <- nb2listw(COL.nb, style = "W")
nrow(col)
#> [1] «N»
round(mean(col$CRIME), 4)
#> [1] «MEDIA»
round(sd(col$CRIME), 4)
#> [1] «SD»

# El dato y la media de sus vecinos se parecen. ¿Más que por azar?
round(cor(col$CRIME, lag.listw(gal, col$CRIME)), 4)
#> [1] «COR»

# El caso real: los municipios, con la deserción escolar del MEN (2024).
# La unión va por shapeID, nunca por la posición de la fila.
mun   <- st_read("datos/procesado/colombia_adm2.gpkg", quiet = TRUE)
llave <- read.csv("datos/procesado/municipios_llave.csv")
mun$desercion <- llave$desercion[match(mun$shapeID, llave$shapeID)]
con_dato <- is.finite(mun$desercion)
sum(con_dato)
#> [1] «NMUN»

nb_m <- poly2nb(mun[con_dato, ], queen = TRUE)    # ~40 s: 1 121 polígonos
y_m  <- mun$desercion[con_dato]
lw_m <- nb2listw(nb_m, style = "W", zero.policy = TRUE)
sum(card(nb_m) == 0)                              # las islas del capítulo 6
#> [1] «ISLAS»'''

PY1 = r'''import numpy as np
import pandas as pd
import geopandas as gpd
from libpysal import weights

# Los mismos 49 barrios y LA MISMA GAL, en el mismo orden, desde los CSV del
# capítulo. Ojo: el `columbus.gal` que trae libpysal no es la GAL de Anselin,
# es la reina —118 parejas, no 116—.
col = pd.read_csv("precalculo/salidas/cap7_columbus.csv")
gal = pd.read_csv("precalculo/salidas/cap7_columbus_gal.csv")
vecinos = {i: [] for i in range(len(col))}
for i, j in zip(gal.i0, gal.j0):
    vecinos[i].append(j)
    vecinos[j].append(i)
w = weights.W(vecinos, silence_warnings=True)
w.transform = "r"                       # el estilo W de spdep
print(len(col), len(gal))
#> «N» «PARES»
print(round(col.CRIME.mean(), 4), round(col.CRIME.std(), 4))
#> «MEDIA» «SD»

wy = weights.lag_spatial(w, col.CRIME.to_numpy())
print(round(np.corrcoef(col.CRIME, wy)[0, 1], 4))
#> «COR»

# Los municipios: la misma unión por shapeID
mun = gpd.read_file("datos/procesado/colombia_adm2.gpkg")
llave = pd.read_csv("datos/procesado/municipios_llave.csv")
mun = mun.merge(llave[["shapeID", "desercion"]], on="shapeID", how="left")
sub = mun[mun.desercion.notna()].reset_index(drop=True)
wm = weights.Queen.from_dataframe(sub, use_index=True, silence_warnings=True)
wm.transform = "r"
print(len(sub), len(wm.islands))
#> «NMUN» «ISLAS»'''

R2 = r'''# I pieza a pieza. z centrada —aquí, tipificada— y su rezago Wz
z  <- as.numeric(scale(col$CRIME))
wz <- lag.listw(gal, z)

print(sum(z * wz), digits = 8)     # el numerador: productos de vecinos
#> [1] «ZWZ»
sum(z^2)                           # el denominador: con z tipificada, n - 1
#> [1] «ZZ»
round(sum(z * wz) / sum(z^2), 6)   # con W por filas S0 = n, y n / S0 = 1
#> [1] «I»

# El mismo número, con la función, y su esperanza bajo la nula
mt <- moran.test(col$CRIME, gal)
round(mt$estimate[["Moran I statistic"]], 6)
#> [1] «I»
round(mt$estimate[["Expectation"]], 6)          # -1 / (n - 1)
#> [1] «EI»

# Su rango REAL no es [-1, 1]. Como z suma cero, los extremos son los valores
# propios de M (W + W')/2 M, con M = I - 11'/n, que deja fuera la dirección
# de las constantes (de Jong, Sprenger y van Veen, 1984)
W  <- listw2mat(gal)
nW <- nrow(W)
M  <- diag(nW) - 1 / nW
round(range(eigen(M %*% ((W + t(W)) / 2) %*% M, symmetric = TRUE,
                  only.values = TRUE)$values), 4)
#> [1] «RMIN»  «RMAX»

# Sin centrar salen COTAS: valores que ningún mapa alcanza
round(range(eigen((W + t(W)) / 2, symmetric = TRUE, only.values = TRUE)$values), 4)
#> [1] «SMIN»  «SMAX»'''

PY2 = r'''y = col.CRIME.to_numpy()
z = (y - y.mean()) / y.std(ddof=1)
wz = weights.lag_spatial(w, z)

print(round(z @ wz, 6), round(z @ z, 6))
#> «ZWZ» «ZZ»
print(round((z @ wz) / (z @ z), 6))
#> «I»
print(round(-1 / (len(y) - 1), 6))
#> «EI»

# El rango real: los valores propios de la parte simétrica de W, CENTRADA
W = w.full()[0]
M = np.eye(len(W)) - 1 / len(W)
ev = np.linalg.eigvalsh(M @ ((W + W.T) / 2) @ M)
print(round(ev.min(), 4), round(ev.max(), 4))
#> «RMIN» «RMAX»'''

R3 = r'''# Las dos varianzas analíticas: bajo normalidad y bajo aleatorización
mn <- moran.test(col$CRIME, gal, randomisation = FALSE)
ma <- moran.test(col$CRIME, gal)            # aleatorización: la de por defecto
round(mn$statistic[[1]], 4)
#> [1] «ZN»
round(ma$statistic[[1]], 4)
#> [1] «ZA»

# Y la permutación: 999 repartos al azar de los MISMOS 49 valores
set.seed(2026)
mc <- moran.mc(col$CRIME, gal, nsim = 999)
sum(mc$res[1:999] >= mc$statistic)     # réplicas que igualan o superan a I
#> [1] «RANGO»
mc$p.value                             # (0 + 1) / (999 + 1)
#> [1] «P999»
round(max(mc$res[1:999]), 6)           # la mayor I que dio el azar
#> [1] «MAXSIM»

# El suelo: con los municipios, el analítico da un p minúsculo...
signif(moran.test(y_m, lw_m, zero.policy = TRUE)$p.value, 4)
#> [1] «PMUN»
# ...y la permutación no baja de 1 / (999 + 1), diga lo que diga el dato
set.seed(2026)
moran.mc(y_m, lw_m, nsim = 999, zero.policy = TRUE)$p.value
#> [1] «PM999»'''

PY3 = r'''from esda.moran import Moran

np.random.seed(2026)
m = Moran(col.CRIME, w, permutations=999)
print(round(m.z_norm, 4), round(m.z_rand, 4))
#> «ZN» «ZA»

# esda permuta con su propio generador: las réplicas no son las de R, pero
# ninguna llega a I, así que el p es el mismo suelo
print(m.p_sim)
#> «P999»'''

R4 = r'''# La recta de Wz sobre z: su pendiente ES el I de Moran
round(coef(lm(wz ~ z))[[2]], 6)
#> [1] «I»

# Los cuatro cuadrantes: alto-alto, bajo-bajo, alto-bajo, bajo-alto
cuad <- ifelse(z >= 0, ifelse(wz >= 0, "AA", "AB"), ifelse(wz >= 0, "BA", "BB"))
table(factor(cuad, levels = c("AA", "BB", "AB", "BA")))
#> AA BB AB BA
#> «AA» «BB»  «AB»  «BA»

# Los «influyentes» de moran.plot: los que fallan CUALQUIERA de los
# diagnósticos de influence.measures, no solo los que mueven la recta
mp <- moran.plot(col$CRIME, gal, plot = FALSE, return_df = TRUE)
col$POLYID[mp$is_inf]
#> [1] «INF»
# La pendiente sin cada uno de ellos: dos la mueven, dos casi nada
sapply(which(mp$is_inf), function(k) round(coef(lm(wx ~ x, data = mp[-k, ]))[[2]], 4))
#> [1] «PSIN»

# Con el dato CRUDO, sin centrar ni tipificar, la pendiente también es I:
# sin islas, centrar no hace falta
round(coef(lm(mp$wx ~ mp$x))[[2]], 6)
#> [1] «I»

# Con islas, la identidad vale sobre TODAS las unidades, no sobre las
# que tienen vecinos, y solo con el dato centrado
z_m  <- as.numeric(scale(y_m))
wz_m <- lag.listw(lw_m, z_m, zero.policy = TRUE)
con  <- card(nb_m) > 0
round(coef(lm(wz_m ~ z_m))[[2]], 6)
#> [1] «PTODAS»
round(coef(lm(wz_m[con] ~ z_m[con]))[[2]], 6)
#> [1] «PCON»
round(coef(lm(lag.listw(lw_m, y_m, zero.policy = TRUE) ~ y_m))[[2]], 6)   # crudo
#> [1] «PCRUDA»'''

PY4 = r'''pendiente = np.polyfit(z, wz, 1)[0]
print(round(pendiente, 6))
#> «I»

cuad = np.where(z >= 0, np.where(wz >= 0, "AA", "AB"),
                np.where(wz >= 0, "BA", "BB"))
print({c: int((cuad == c).sum()) for c in ["AA", "BB", "AB", "BA"]})
#> {'AA': «AA», 'BB': «BB», 'AB': «AB», 'BA': «BA»}'''

R5 = r'''# La c de Geary: diferencias al cuadrado entre vecinos, no productos
gt <- geary.test(col$CRIME, gal)
round(gt$estimate[["Geary C statistic"]], 5)
#> [1] «C»
round(gt$statistic[[1]], 4)       # spdep: z = (E[c] - c) / sd, positiva si se parecen
#> [1] «ZC»

# El barrio de mayor CRIME, multiplicado por ocho
x <- col$CRIME
x[which.max(x)] <- 8 * x[which.max(x)]
round(moran.test(x, gal)$estimate[[1]], 4)
#> [1] «I8»
round(geary.test(x, gal)$estimate[[1]], 4)
#> [1] «C8»'''

PY5 = r'''from esda.geary import Geary

g = Geary(col.CRIME, w, permutations=0)
print(round(g.C, 5))
#> «C»
# la MISMA z con el signo al revés: esda la escribe (c - E[c]) / sd
print(round(g.z_rand, 4))
#> -«ZC»'''

R6 = r'''# El correlograma: I por orden de contigüidad. `nblag` NO acumula: el orden 2
# son los vecinos de los vecinos que no eran ya vecinos (capítulo 6)
cg <- sp.correlogram(COL.nb, col$CRIME, order = 6, method = "I",
                     style = "W", zero.policy = TRUE)
round(cg$res[, 1], 4)
#>       1       2       3       4       5       6
#> «O1» «O2» «O3» «O4» «O5» «O6»

# El caso binario: centro (CP = 1) y periferia (CP = 0)
cp <- factor(col$CP, levels = c(0, 1), labels = c("periferia", "centro"))
jc <- joincount.multi(cp, gal)
round(jc[, c("Joincount", "Expected", "z-value")], 4)
#>                     Joincount Expected z-value
#> periferia:periferia   «JPPO»     «JPPE»  «JPPZ»
#> centro:centro          «JCCO»     «JCCE»  «JCCZ»
#> centro:periferia       «JCPO»    «JCPE» «JCPZ»

# Con la W BINARIA las uniones se cuentan, no se pesan, y no cambia solo la
# escala: la z de periferia-periferia es otra
round(joincount.multi(cp, nb2listw(COL.nb, style = "B"))["periferia:periferia", "z-value"], 4)
#> [1] «JBPPZ»'''

PY6 = r'''# El mismo correlograma con libpysal: `higher_order` da los vecinos a
# EXACTAMENTE k pasos, como `nblag`. Hasta el orden 5; el 6 deja barrios
# sin vecinos, y ahí esda y spdep cuentan n distinto (módulo 9)
for k in range(1, 6):
    wk = w if k == 1 else weights.higher_order(
        weights.W(vecinos, silence_warnings=True), k, silence_warnings=True)
    wk.transform = "r"
    print(k, round(Moran(col.CRIME, wk, permutations=0).I, 4))
#> 1 «O1»
#> 2 «O2»
#> 3 «O3»
#> 4 «O4»
#> 5 «O5»'''

R7 = r'''# El mismo CRIME bajo cinco W: el I cambia y el veredicto no
cent <- st_centroid(st_geometry(col))
ws <- list(gal      = COL.nb,
           reina    = poly2nb(col, queen = TRUE),
           k1       = knn2nb(knearneigh(cent, k = 1)),
           k6       = knn2nb(knearneigh(cent, k = 6)),
           delaunay = tri2nb(cent))
round(sapply(ws, function(nb)
  moran.test(col$CRIME, nb2listw(nb, style = "W"))$estimate[[1]]), 4)
#>      gal    reina       k1       k6 delaunay
#>   «IGAL»   «IREI»   «IK1»   «IK6»   «IDEL»'''

PY7 = r'''import libpysal

# Los polígonos de libpysal, puestos en el orden de Anselin
shp = gpd.read_file(libpysal.examples.get_path("columbus.shp"))
shp = shp.set_index("POLYID").loc[col.polyid].reset_index()

def moran_con(wx):
    wx.transform = "r"
    return round(Moran(col.CRIME, wx, permutations=0).I, 4)

print(moran_con(weights.Queen.from_dataframe(shp, use_index=False, silence_warnings=True)))
#> «IREI»
print(moran_con(weights.KNN.from_dataframe(shp, k=1)),
      moran_con(weights.KNN.from_dataframe(shp, k=6)))
#> «IK1» «IK6»'''

R8 = r'''# Los I locales: uno por barrio, y su media ES el I global
li <- localmoran(col$CRIME, gal)
round(mean(li[, "Ii"]), 6)
#> [1] «I»
round(sum(li[, "Ii"]), 5)          # = S0 · I, y aquí S0 = n
#> [1] «SUMA»

# El p de cada uno, por permutación CONDICIONAL: el barrio se queda quieto y
# se barajan los demás a su alrededor. 49 999 réplicas, sin repetir valores
# dentro de una vecindad (el convenio de GeoDa y de esda), y el p BILATERAL
lp <- localmoran_perm(col$CRIME, gal, nsim = 49999, iseed = 2026,
                      no_repeat_in_row = TRUE)
p  <- lp[, "Pr(z != E(Ii)) Sim"]
min(p)                             # el suelo es 2 / (49 999 + 1)
#> [1] «PMIN»
sum(p < 0.05)
#> [1] «SIG»
# El plegado de GeoDa y esda mira solo la cola donde cayó el dato: la mitad
sum(lp[, "Pr(folded) Sim"] < 0.05)
#> [1] «SIGPLEG»'''

PY8 = r'''from esda.moran import Moran_Local

ml = Moran_Local(col.CRIME, w, permutations=0)
# esda divide cada I_i por la varianza MUESTRAL (n - 1) y spdep por la
# poblacional (n): las sumas difieren en n / (n - 1), exactamente
print(round(ml.Is.sum(), 6))
#> «ZWZ»
print(round(ml.Is.sum() / (len(col) - 1), 6))
#> «I»'''

R9 = r'''# Del p y el cuadrante al mapa: cinco categorías
q     <- attr(lp, "quadr")$mean
clase <- ifelse(p < 0.05, as.character(q), "No significativo")
as.vector(table(factor(clase, levels = c("No significativo", "High-High",
                                         "Low-Low", "High-Low", "Low-High"))))
#> [1] «K1» «K2»  «K3»  «K4»  «K5»

# Los municipios: las islas salen sin p, y el capítulo las pinta así
lp_m <- localmoran_perm(y_m, lw_m, nsim = 49999, zero.policy = TRUE,
                        iseed = 2026, no_repeat_in_row = TRUE)   # ~1 min
p_m <- lp_m[, "Pr(z != E(Ii)) Sim"]
sum(is.na(p_m))
#> [1] «ISLAS»
sum(p_m < 0.05, na.rm = TRUE)
#> [1] «SIGM»'''

PY9 = r'''# La discrepancia declarada: el MISMO grafo y la MISMA fórmula dan dos I.
# spdep toma n = las unidades con vecinos (1 119); esda, n = todas (1 121)
mg = Moran(sub.desercion.to_numpy(), wm, permutations=0)
print(round(mg.I, 6))
#> «IESDA»'''

R10 = r'''# Bonferroni pide p < 0.05 / n, ESTRICTO, y el p bilateral no baja de
# 2 / (nsim + 1): hace falta nsim + 1 > 2n / 0.05
signif(0.05 / nrow(col), 4)
#> [1] «UMB»
2 * nrow(col) / 0.05                   # réplicas mínimas: con una menos, el suelo IGUALA al umbral
#> [1] «NSIMMIN»

# Las tres lecturas del MISMO vector de p
c(sin = sum(p < 0.05),
  bonferroni = sum(p.adjust(p, "bonferroni") < 0.05),
  fdr = sum(p.adjust(p, "fdr") < 0.05))
#>        sin bonferroni        fdr
#>         «S»          «B»         «F»

# Los municipios con 999 réplicas, las habituales de GeoDa y esda: Bonferroni
# no deja nada, porque el suelo (0.002) está por encima del umbral
lp_m999 <- localmoran_perm(y_m, lw_m, nsim = 999, zero.policy = TRUE,
                           iseed = 2026, no_repeat_in_row = TRUE)
p999 <- lp_m999[, "Pr(z != E(Ii)) Sim"]
sum(p.adjust(p999[!is.na(p999)], "bonferroni") < 0.05)
#> [1] «BM999»
sum(p.adjust(p_m[!is.na(p_m)], "bonferroni") < 0.05)      # con 49 999
#> [1] «BMN»

# ¿Cuántos «significativos» marca cada p cuando NO hay nada? 200 mapas con
# CRIME repartido al azar, 999 réplicas cada uno (~20 s)
set.seed(2026)
tasas <- sapply(1:200, function(r) {
  lp0 <- localmoran_perm(sample(col$CRIME), gal, nsim = 999, no_repeat_in_row = TRUE)
  c(plegado = mean(lp0[, "Pr(folded) Sim"] < 0.05),
    bilateral = mean(lp0[, "Pr(z != E(Ii)) Sim"] < 0.05))
})
round(mean(tasas["plegado", ]), 4)     # el p de GeoDa: el doble de lo prometido
#> [1] «TPL»
round(mean(tasas["bilateral", ]), 4)
#> [1] «TBI»'''

PY10 = r'''# Benjamini-Hochberg a mano, sobre los p de spdep que guarda el CSV: se
# ordenan y se busca el mayor k con p_(k) <= k * alfa / n
p = col.p_rangos.to_numpy()
orden = np.sort(p)
k = np.arange(1, len(p) + 1)
print(np.nonzero(orden <= k * 0.05 / len(p))[0].max() + 1)
#> «KBH»
print((p < 0.05 / len(p)).sum())       # Bonferroni
#> «B»'''

R11 = r'''# La rejilla del artículo de Getis y Ord: 256 celdas y un umbral de 30
data(getisord, package = "spData")
xy   <- cbind(go_xyz$x, go_xyz$y)
nb30 <- dnearneigh(xy, 0, 30)
G  <- localG(go_xyz$val, nb2listw(nb30, style = "B"))                 # Gi
Gs <- localG(go_xyz$val, nb2listw(include.self(nb30), style = "B"))   # Gi*
go_xyz$val[«CELDA»]
#> [1] «VALOR»
round(as.numeric(G)[«CELDA»], 4)
#> [1] «G»
round(as.numeric(Gs)[«CELDA»], 4)
#> [1] «GS»

# Gi* sobre Columbus, con el barrio dentro de su propia vecindad
# y DENTRO de la permutación: por defecto spdep lo deja fijo, y entonces
# el p de Gi* es, en la práctica, el de Gi
gs <- localG_perm(col$CRIME, nb2listw(include.self(COL.nb), style = "W"),
                  nsim = 49999, iseed = 2026, no_repeat_in_row = TRUE,
                  fix_i_in_Gstar_permutations = FALSE)
round(max(gs), 4)
#> [1] «ZMAX»
col$POLYID[which.max(gs)]
#> [1] «PZMAX»
# El barrio de menor CRIME, bajo entre altos: su p con él dentro
round(attr(gs, "internals")[col$POLYID == «PBA», "Pr(z != E(Gi)) Sim"], 4)
#> [1] «PLIB»'''

PY11 = r'''from esda.getisord import G_Local

go = pd.read_csv("precalculo/salidas/cap7_getisord.csv")
wb = weights.DistanceBand(go[["x", "y"]].to_numpy(), threshold=30,
                          binary=True, silence_warnings=True)
# Con pesos BINARIOS, esda y spdep dan la misma z. Con pesos por filas la
# z de Gi* de esda 2.9 sale mal (su varianza es ocho veces la debida en el
# barrio 9 de Columbus): para Gi*, binarios
g_est = G_Local(go.val.to_numpy(), wb, transform="B", star=True, permutations=0)
g_sin = G_Local(go.val.to_numpy(), wb, transform="B", star=False, permutations=0)
print(round(g_sin.Zs[«CELDA» - 1], 4), round(g_est.Zs[«CELDA» - 1], 4))
#> «G» «GS»'''


# ---------------------------------------------------------------------
# Lo que llena los `#>`. R y Python NO imprimen igual el mismo número —R
# rellena con ceros la columna de un vector («0.5230»), Python escribe el
# redondeo tal cual («0.523»)—, así que donde difieren hay dos valores: el
# de R con `n()` y el de Python con `py()`. Ninguno lleva aritmética.
# ---------------------------------------------------------------------
def py(x, d):
    """Lo que imprime `print(round(x, d))` en Python."""
    return repr(round(float(x), d))


def gx(x):
    """Lo que imprime R para un número que no necesita más cifras: 0.001, 8e-05."""
    return f"{float(x):g}"


def pfmt(x):
    """Un p en la prosa: tal cual si es legible (0.00052), y con potencia de diez
    donde R ya lo escribiría en notación científica (4·10⁻⁵ y no «4e-05»)."""
    return cient(x) if float(x) < 1e-4 else gx(x)


_JCP = {f["par"]: f for f in JC["columbus_cp"]["tabla"]}
_JCB = {f["par"]: f for f in JC["columbus_cp_binaria"]["tabla"]}
if any(x["p"] != JC["columbus_cp"]["p_permutacion"][0]["p"]
       for v in ("columbus_cp", "municipios_desercion", "municipios_tipo") for x in JC[v]["p_permutacion"]):
    sys.exit("PARADO: no todas las categorías del join count están en el suelo del p, y el módulo 6 lo dice")
if not JC["columbus_cp_binaria"]["p_permutacion"][0]["p"] > JC["columbus_cp"]["p_permutacion"][0]["p"]:
    sys.exit("PARADO: con la W binaria el p de periferia-periferia ya no sube")
_CGC = CG["columbus"]
_T10 = T10C["bilateral_nsim"]

S1R = dict(N=ent_codigo(C1["n"]), MEDIA=n(C1["media"], 4), SD=n(C1["sd"], 4),
           COR=n(C1["cor_con_rezago"], 4), NMUN=ent_codigo(M1["con_dato"]),
           ISLAS=ent_codigo(M1["islas"]))
S1P = dict(S1R, PARES=ent_codigo(C2["pares_gal"]))
S2 = dict(ZWZ=n(C2["z_Wz"], 6), ZZ=ent_codigo(C2["z_z"]), I=n(C2["I"], 6),
          EI=n(C2["EI"], 6), RMIN=n(m2["rango"]["columbus_gal"][0], 4),
          RMAX=n(m2["rango"]["columbus_gal"][1], 4),
          SMIN=n(m2["rango"]["sin_centrar"]["columbus_gal"][0], 4),
          SMAX=n(m2["rango"]["sin_centrar"]["columbus_gal"][1], 4))
# Python no rellena con ceros: −0.698 y no −0.6980.
S2P = dict(ZWZ=S2["ZWZ"], ZZ=S2["ZZ"], I=S2["I"], EI=S2["EI"],
           RMIN=py(m2["rango"]["columbus_gal"][0], 4), RMAX=py(m2["rango"]["columbus_gal"][1], 4))
S3R = dict(ZN=n(C3["normalidad"]["z"], 4), ZA=n(C3["aleatorizacion"]["z"], 4),
           RANGO=ent_codigo(C3["permutacion"]["rango_observado"]),
           P999=gx(C3["permutacion"]["p"]), MAXSIM=n(C3["permutacion"]["max_sim"], 6),
           PMUN=f'{M3["aleatorizacion"]["p"]:.4g}', PM999=gx(M3["permutacion"][0]["p"]))
S3P = dict(ZN=S3R["ZN"], ZA=S3R["ZA"], P999=S3R["P999"])
S4R = dict(I=n(C4["pendiente"], 6), AA=ent_codigo(C4["cuadrantes"]["AA"]),
           BB=ent_codigo(C4["cuadrantes"]["BB"]), AB=ent_codigo(C4["cuadrantes"]["AB"]),
           BA=ent_codigo(C4["cuadrantes"]["BA"]),
           INF=" ".join(ent_codigo(x) for x in C4["influyentes_polyid"]),
           PSIN=" ".join(n(x["pendiente_sin"], 4) for x in C4["influyentes_detalle"]),
           PTODAS=n(M4["pendiente_todas"], 6), PCON=n(M4["pendiente_con_vecinos"], 6),
           PCRUDA=n(M4["pendiente_cruda_todas"], 6))
S4P = dict(I=S4R["I"], AA=S4R["AA"], BB=S4R["BB"], AB=S4R["AB"], BA=S4R["BA"])
S5R = dict(C=n(C5["c"], 5), ZC=n(C5["z"], 4),
           I8=n(m5["pico_en_alto"]["curva"][-1]["I"], 4),
           C8=n(m5["pico_en_alto"]["curva"][-1]["c"], 4))
S5P = dict(C=S5R["C"], ZC=S5R["ZC"])
S6R = dict({f"O{k + 1}": n(_CGC[k]["I"], 4) for k in range(6)},
           JPPO=n(_JCP["periferia:periferia"]["observado"], 4),
           JPPE=n(_JCP["periferia:periferia"]["esperado"], 2),
           JPPZ=n(_JCP["periferia:periferia"]["z"], 4),
           JCCO=n(_JCP["centro:centro"]["observado"], 4),
           JCCE=n(_JCP["centro:centro"]["esperado"], 2),
           JCCZ=n(_JCP["centro:centro"]["z"], 4),
           JCPO=n(_JCP["centro:periferia"]["observado"], 4),
           JCPE=n(_JCP["centro:periferia"]["esperado"], 2),
           JCPZ=n(_JCP["centro:periferia"]["z"], 4),
           JBPPZ=n({f["par"]: f for f in JC["columbus_cp_binaria"]["tabla"]}["periferia:periferia"]["z"], 4))
S6P = {f"O{k + 1}": py(_CGC[k]["I"], 4) for k in range(5)}
S7R = dict(IGAL=n(W7["gal"]["I"], 4), IREI=n(W7["reina"]["I"], 4),
           IK1=n(W7["k1"]["I"], 4), IK6=n(W7["k6"]["I"], 4),
           IDEL=n(W7["delaunay"]["I"], 4))
S7P = dict(IREI=py(W7["reina"]["I"], 4), IK1=py(W7["k1"]["I"], 4),
           IK6=py(W7["k6"]["I"], 4))
S8R = dict(I=n(C8["media_Ii"], 6), SUMA=n(C8["suma_Ii"], 5),
           PMIN=gx(C8["p_min"]), SIG=ent_codigo(C8["significativos"]),
           SIGPLEG=ent_codigo(T10C["plegado_nsim"]["sin_corregir"]))
S8P = dict(ZWZ=n(C2["z_Wz"], 6), I=n(C2["I"], 6))
S9R = dict({f"K{k + 1}": ent_codigo(m9["columbus"]["conteo"][k]) for k in range(5)},
           ISLAS=ent_codigo(m9["municipios"]["sin_vecinos"]),
           SIGM=ent_codigo(M8["significativos"]))
S9P = dict(IESDA=n(M8["I_esda_equivalente"], 6))
S10R = dict(UMB=gx(m10["suelo"]["columbus"]["umbral_bonferroni"]),
            NSIMMIN=ent_codigo(m10["suelo"]["columbus"]["nsim_minimo"]),
            S=ent_codigo(_T10["sin_corregir"]), B=ent_codigo(_T10["bonferroni"]),
            F=ent_codigo(_T10["fdr"]),
            BM999=ent_codigo(T10M["bilateral_999"]["bonferroni"]),
            BMN=ent_codigo(T10M["bilateral_nsim"]["bonferroni"]),
            TPL=gx(m10["tasa_nula"]["plegado"]), TBI=gx(m10["tasa_nula"]["bilateral"]))
S10P = dict(KBH=ent_codigo(m10["columbus"]["bh"]["k"]), B=S10R["B"])
S11R = dict(CELDA=ent_codigo(GO["celda"]), VALOR=ent_codigo(GO["valor"]),
            G=gx(GO["G"]), GS=gx(GO["G_estrella"]),
            ZMAX=n(m11["columbus"]["z_max"], 4),
            PZMAX=ent_codigo(m11["columbus"]["polyid_z_max"]),
            PBA=ent_codigo(m11["columbus"]["autoinclusion"]["polyid"]),
            PLIB=gx(round(m11["columbus"]["autoinclusion"]["p_libre"], 4)))
S11P = dict(CELDA=S11R["CELDA"], G=S11R["G"], GS=S11R["GS"])


def _codigo(texto):
    return re.sub(r"`([^`]+)`", r"<code>\1</code>", texto)


def ejercicio(k, e):
    """El marcado de la CASA: `cuenta_sitio.py` cuenta `.ejercicio-guiado` y el
    desplegable se cablea por `.ejercicio-boton` (A.13)."""
    pasos = "".join(
        f'                <tr><th scope="row">{p["paso"]}</th>'
        f'<td>{p["valor"]:g}</td></tr>\n'
        for p in e["pasos"])
    return f"""
        <div class="ejercicio-guiado">
          <p class="ejercicio-enunciado"><span class="ejercicio-numero">{k}.</span><strong>{e['titulo']}.</strong>
            {_codigo(e['enunciado'])}</p>
          <div class="ejercicio-acciones">
            <button type="button" class="ejercicio-boton" aria-expanded="false" aria-controls="cap7-e{k}-sol">
              <i class="fas fa-key" aria-hidden="true"></i> Solución <i class="fas fa-chevron-down" aria-hidden="true"></i>
            </button>
          </div>
          <div class="ejercicio-panel solucion" id="cap7-e{k}-sol" hidden>
            <table>
              <caption>Los pasos de la solución, calculados en R por <code>precalculo/genera_soluciones.R</code>.</caption>
              <thead><tr><th scope="col">Paso</th><th scope="col">Valor</th></tr></thead>
              <tbody>
{pasos}
              </tbody>
            </table>
            <p class="ejercicio-lectura">{_codigo(e['solucion']['lectura'])}</p>
          </div>
        </div>
"""


EJERCICIOS = [SOL[f"e{i}"] for i in range(1, SOL["meta"]["n_ejercicios"] + 1)]
EJ = "".join(ejercicio(i + 1, e) for i, e in enumerate(EJERCICIOS))


# =====================================================================
# LAS FÓRMULAS, aparte y en cadenas crudas: dentro de una f-string cada
# llave de KaTeX habría que doblarla, y una que se olvida no da error —da
# otra fórmula—. Medidas en un teléfono de 375 px, donde la caja deja
# entre 265 y 273 px útiles (punto 6 del §0.5 del plan): Moran con z cabe
# en un renglón; Geary, Gi* y el Moran local van partidos.
# =====================================================================
F_MORAN = r'''      <div class="formula">
        $$I \;=\; \frac{n}{S_0}\,\frac{\sum_i \sum_j w_{ij}\, z_i z_j}{\sum_i z_i^2}$$
      </div>
'''

F_EI = r'''      <div class="formula">
        $$\begin{aligned}
          \sum_{i \neq j} z_i z_j &amp;= \Big(\sum_i z_i\Big)^2 - \sum_i z_i^2 = -\sum_i z_i^2 \\[6pt]
          E[I] &amp;= -\frac{1}{n-1}
        \end{aligned}$$
      </div>
'''

F_PENDIENTE = r'''      <div class="formula">
        $$\begin{aligned}
          b &amp;= \frac{\sum_i z_i\,(Wz)_i}{\sum_i z_i^2} \\[6pt]
          I &amp;= \frac{n}{S_0}\; b
        \end{aligned}$$
      </div>
'''

F_GEARY = r'''      <div class="formula">
        $$\begin{aligned}
          c &amp;= \frac{n-1}{2\,S_0}\;\frac{\sum_i \sum_j w_{ij}\,(x_i - x_j)^2}{\sum_i (x_i - \bar{x})^2} \\[6pt]
          E[c] &amp;= 1
        \end{aligned}$$
      </div>
'''

F_LOCAL = r'''      <div class="formula">
        $$\begin{gathered}
          I_i = \frac{z_i}{m_2} \sum_j w_{ij}\, z_j, \qquad m_2 = \frac{1}{n}\sum_k z_k^2 \\[6pt]
          \sum_i I_i = S_0 \, I
        \end{gathered}$$
      </div>
'''

F_BH = r'''      <div class="formula">
        $$\begin{aligned}
          \text{Bonferroni:}&amp;\quad p_i &lt; \frac{\alpha}{n} \\[6pt]
          \text{FDR:}&amp;\quad p_{(i)} \le \frac{i}{n}\,\alpha \;\text{ para } i \le k
        \end{aligned}$$
      </div>
'''

F_GI = r'''      <div class="formula">
        $$\begin{aligned}
          G_i^{*} &amp;= \frac{\sum_{j} w_{ij}\, x_j}{\sum_{j} x_j} \quad (j \text{ incluye a } i) \\[6pt]
          G_i &amp;= \frac{\sum_{j \neq i} w_{ij}\, x_j}{\sum_{j \neq i} x_j}
        \end{aligned}$$
      </div>
'''


# =====================================================================
# LOS MÓDULOS
#
# Se escriben con f-strings CRUDAS (rf"""…"""), para que las barras de KaTeX
# lleguen enteras: `\frac` dentro de una f-string normal es un salto de
# página (`\f`) seguido de «rac». Las llaves de KaTeX en línea van dobladas.
# =====================================================================
MOD1 = cabecera(
    1, TITULOS[0][0], INGLES[0],
    "Convertir la primera ley de Tobler en una pregunta que se puede contestar: un número "
    "que mida el parecido entre vecinos y un azar contra el que compararlo.") + rf"""
      <p>El capítulo 6 terminó con una pieza en la mano: el <strong>rezago</strong> \(Wy\), la media
        de los vecinos de cada unidad. Y con una advertencia: cuánto se parece un dato a su rezago
        depende de la W que se haya elegido. Este capítulo usa esa pieza para hacer la pregunta que
        el curso trae desde el capítulo 1, cuando el correlograma de las estaciones del IDEAM midió
        la primera ley de Tobler: <em>¿lo cercano se parece más de lo que cabría esperar por
        azar?</em></p>

      <p>La frase tiene dos mitades, y cada una pide una cosa distinta. «Se parece» pide una
        <strong>medida</strong>: un número que resuma, sobre todas las parejas de vecinos a la vez,
        si sus valores van juntos. «Por azar» pide una <strong>referencia</strong>: cuánto se
        parecerían esos mismos vecinos si la posición no importara. La segunda es la que se olvida,
        y sin ella la primera no dice nada, porque en cualquier mapa hay vecinos que se parecen.</p>

      <h3>Qué es «por azar» cuando las unidades no se mueven</h3>

      <p>En un patrón puntual el azar de referencia era la aleatoriedad espacial completa: puntos
        que caen uniformemente en la ventana (capítulo 4). Aquí no sirve, porque las unidades están
        donde están —el capítulo 6 lo dejó dicho: en un dato de área lo aleatorio es el valor, no la
        posición—. La referencia es otra: <strong>los mismos valores, repartidos al azar entre las
        mismas unidades</strong>. El mapa se queda, W se queda y la lista de valores se queda; lo
        único que cambia es qué valor le toca a qué unidad. Si la posición no importa, cualquiera de
        esos repartos era igual de probable que el que se observó.</p>

      <p>Esa es la hipótesis nula de todo el capítulo, y se llama <em>ausencia de autocorrelación
        espacial</em>. Lo que el capítulo mide es cuánto se aleja el mapa observado de lo que
        darían esos repartos: hacia el parecido entre vecinos (autocorrelación
        <strong>positiva</strong>) o hacia el contraste (autocorrelación <strong>negativa</strong>,
        un tablero de ajedrez).</p>

{sim_doble("cap7-reticulo", "Autocorrelación que tú controlas",
           "Un retículo de 10 × 10 celdas, vecindad torre y W por filas. Cada celda recibe un "
           "valor de un proceso con un parámetro ρ que mueves tú: con ρ = 0 los valores son "
           "independientes; con ρ positivo cada celda tiende a parecerse a sus vecinas, y con ρ "
           "negativo, a llevarles la contraria. A la izquierda, el mapa. A la derecha, cada celda "
           "es un punto: su valor tipificado en horizontal y la media de sus vecinas en vertical. "
           "La recta es la de mínimos cuadrados. Empieza con ρ = 0 y pulsa «Otra realización» "
           "varias veces.",
           "Retículo de 10 por 10 celdas coloreado por el valor de cada celda en la realización "
           "actual del proceso",
           "Diagrama de dispersión de las 100 celdas: el valor tipificado de cada una frente a la "
           "media de sus vecinas, con su recta de mínimos cuadrados")}
      <p>Con ρ = 0 la recta no es horizontal: oscila de una realización a otra, unas veces sube y
        otras baja, alrededor de un valor un poco menor que cero. Ese vaivén <em>es</em> el azar del
        que habla la pregunta, y la lectura del simulador marca hasta dónde suele llegar. Con
        ρ = 0.5 casi todas las realizaciones lo rebasan; con ρ = 0.2, unas sí y otras no. Y fíjate
        en que la pendiente se queda <em>por debajo</em> de ρ: con ρ = {n(_RHO[1]["rho"], 1)} ronda
        {n(_RHO[1]["I_medio"], 2)} y solo la alcanza el {pct(_RHO[1]["llega_pct"], 2)} de las
        realizaciones; con ρ = {n(_RHO[0]["rho"], 1)}, ronda {n(_RHO[0]["I_medio"], 2)} y la alcanza el
        {pct(_RHO[0]["llega_pct"], 1)}. Medidas en {ent(_RHO[0]["reps"])} realizaciones por valor de ρ. No son
        la misma cifra: ρ es el parámetro del proceso que generó el mapa y la pendiente es lo que
        se mide sobre <em>una</em> realización de él. El capítulo 8 vuelve sobre ese proceso —un
        modelo autorregresivo simultáneo, SAR— para estimar ρ en vez de medir el parecido.</p>

      <h3>Los tableros del capítulo</h3>

      <p><strong>Columbus</strong> es el laboratorio, como en el capítulo 6:
        {firma(ent(C1["n"]), " barrios")} de Columbus (Ohio) con su tasa de delitos, CRIME, de media
        {firma(n(C1["media"], 4))} y desviación típica {firma(n(C1["sd"], 4))}. Con un cambio que
        no es menor: la W ya no es la reina que construía <code>poly2nb</code>, sino la
        <strong>GAL</strong> que Luc Anselin publicó con los datos en 1988. Las dos casi coinciden
        —{ent(m7["gal_vs_reina"]["pares_gal"])} parejas frente a
        {ent(m7["gal_vs_reina"]["pares_reina"])}— y el módulo 7 cuenta en qué se diferencian. Se usa
        la GAL porque es la W con la que se calcularon las cifras que todo el mundo cita, y
        reproducirlas es la forma de saber que el tablero está bien montado.</p>

{mapa_html("cap7-columbus-m1", "Columbus: la tasa de delitos de los 49 barrios")}
      <p class="pie-figura">CRIME en quintiles —cinco clases con el mismo número de barrios,
        calculadas en R con <code>classInt</code>—. A simple vista los valores altos no están
        repartidos al azar: se juntan. Pero «a simple vista» es justo lo que este capítulo existe
        para no hacer, porque el ojo encuentra grupos también en los repartos al azar.</p>

      <p>El caso real son los <strong>municipios de Colombia</strong> con su deserción escolar de
        2024: {firma(ent(M1["con_dato"]), " municipios")} con dato de los {ent(M1["n"])}, de media
        {firma(pct(M1["media"], 4))} y desviación típica de {n(M1["sd"], 4)} puntos porcentuales, con la contigüidad reina
        del capítulo 6 y sus {ent(M1["islas"])} islas, San Andrés y Providencia. Y un tercer
        tablero entra en el módulo 11: la rejilla con la que Getis y Ord presentaron su estadístico
        en 1992.</p>

{tabs("Los dos tableros, en R y en Python", bloque(R1, **S1R), bloque(PY1, **S1P))}
      <p>El bloque hace las dos cosas que el resto del capítulo da por hechas. La primera es poner
        los polígonos de Columbus en el orden de la GAL: <code>oldcol</code> trae la lista de
        vecinos en un orden y el <code>.gpkg</code> los barrios en otro —el <code>FALSE</code> de la
        primera comprobación—, y juntarlos sin reordenar no da ningún error, da <em>otra</em> I.
        La segunda es la W municipal con <code>zero.policy</code>, igual que en el capítulo 6. La
        correlación entre el dato y su rezago es alta: {n(C1["cor_con_rezago"], 4)} en Columbus, la
        que imprime el bloque, y {n(M1["cor_con_rezago"], 4)} en los municipios, calculada sin las
        dos islas, que no tienen rezago. Lo que ninguna dice es si es más de lo que daría el azar.
        Para eso hace falta el índice que construye el módulo 2.</p>
""" + CIERRE

MOD2 = cabecera(
    2, TITULOS[1][0], INGLES[1],
    "Leer la fórmula del I de Moran término a término, saber por qué su valor esperado no es "
    "cero y por qué su rango no es [−1, 1].") + rf"""
      <p>El capítulo 1 presentó la fórmula y dejó una promesa: que el I de Moran no vale cero
        cuando no hay autocorrelación, y que el capítulo 7 explicaría por qué. Aquí está, empezando
        por la fórmula entera:</p>

{F_MORAN}
      <div class="definition">
        <h3>Lo que hay en cada pieza</h3>
        <ul>
          <li>\(z_i = x_i - \bar{{x}}\) es el valor de la unidad \(i\) <strong>centrado</strong> en la
            media: positivo si está por encima, negativo si está por debajo.</li>
          <li>\(z_i z_j\) es positivo cuando dos unidades caen del mismo lado de la media —las dos
            altas o las dos bajas— y negativo cuando caen en lados opuestos.</li>
          <li>\(w_{{ij}}\) vale cero si \(j\) no es vecina de \(i\), así que la doble suma solo
            cuenta las parejas que W declara vecinas. El numerador es, entonces, <em>cuánto van
            juntos los valores de los vecinos</em>.</li>
          <li>\(\sum_i z_i^2\), abajo, es la variabilidad total del dato: hace que I no dependa de
            las unidades en que se mida.</li>
          <li>\(S_0 = \sum_i \sum_j w_{{ij}}\) es el peso total de W, y \(n/S_0\) corrige por él. Con W
            estandarizada por filas cada fila suma 1, así que \(S_0 = n\) y el factor vale 1. Con
            islas no: una isla aporta una fila de ceros, y en los municipios \(S_0\) vale
            {ent(M3["aleatorizacion"]["n_con_vecinos"])} y no {ent(M1["con_dato"])}. <code>spdep</code> lo
            arregla contando como \(n\) solo las unidades con vecinos, y el módulo 4 enseña qué
            cuesta ese convenio.</li>
        </ul>
      </div>

      <p>Sobre Columbus, con la GAL por filas y CRIME tipificada, el numerador vale
        {firma(n(C2["z_Wz"], 6))} y el denominador {firma(ent(C2["z_z"]))} —con un dato tipificado,
        la suma de cuadrados es siempre \(n - 1\)—, así que
        {firma("I = " + n(C2["I"], 6))}. Anselin (1995) publica 0.511 para estos datos: es la
        primera ancla del capítulo, y el precálculo se para si deja de salir.</p>

      <h3>Por qué E[I] no es cero</h3>

      <p>Bajo la hipótesis nula cada valor puede caer en cualquier unidad. Y hay una restricción
        que no depende del azar: los \(z_i\) suman cero, porque están centrados. Si una unidad tiene
        un \(z\) alto, las demás, en conjunto, tienen que compensarlo. Por eso el producto de
        \(z_i\) con el \(z\) de <em>otra</em> unidad cualquiera vale, en promedio, un poco menos que
        cero. La cuenta es corta:</p>

{F_EI}
      <p>La suma de todos los productos \(z_i z_j\) <em>incluida</em> la diagonal es \((\sum z_i)^2\),
        que vale cero. W no tiene diagonal —nadie es vecino de sí mismo—, así que de esa suma se
        quitan los \(n\) productos \(z_i^2\), todos positivos, y lo que queda es negativo. Repartido
        entre las \(n(n-1)\) parejas posibles, cada pareja de unidades distintas vale en promedio
        \(-\sum_k z_k^2 / [n(n-1)]\). El numerador de I suma \(S_0\) veces esa cantidad —una por
        cada peso de W—, y al multiplicar por \(n/S_0\) y dividir por \(\sum_k z_k^2\) se cancela
        todo menos \(E[I] = -1/(n-1)\). Ese es «el artefacto de comparar cada unidad consigo misma excluida» del
        capítulo 1. Con los {ent(C1["n"])} barrios de Columbus, {firma(n(C1["EI"], 6))}; con las
        100 celdas del retículo del módulo 1, {n(m1["reticulo"]["EI"], 6)}. Se desvanece al crecer
        \(n\), pero nunca es cero, y por eso un I se compara con \(E[I]\) y no con 0.</p>

      <h3>El rango real no es [−1, 1]</h3>

      <p>La correlación de Pearson vive entre −1 y 1. El I de Moran, no. Sus extremos los fijan los
        valores propios mayor y menor de la parte simétrica de W, \((W + W^\top)/2\),
        <strong>centrada</strong>, multiplicados por \(n/S_0\) (de Jong, Sprenger y van Veen, 1984).
        Centrada porque los \(z_i\) suman cero: ningún mapa puede tomar la dirección de las
        constantes, y la matriz que cuenta es \(M\,(W + W^\top)/2\,M\), con
        \(M = I - \mathbf{{1}}\mathbf{{1}}^\top/n\), la que resta la media. Sin centrar salen cotas, valores
        que ningún mapa alcanza. Medidos sobre los tres tableros del capítulo:</p>

{tabla(["Tablero", "Mínimo posible", "Máximo posible"],
       fila("Columbus, GAL por filas", n(m2["rango"]["columbus_gal"][0], 4), n(m2["rango"]["columbus_gal"][1], 4))
       + fila("Municipios, reina por filas", n(m2["rango"]["municipios"][0], 4), n(m2["rango"]["municipios"][1], 4))
       + fila("Retículo de 10 × 10, torre por filas", n(m2["rango"]["reticulo_10"][0], 4), n(m2["rango"]["reticulo_10"][1], 4)),
       "El rango real del I de Moran: los valores propios extremos de (W + Wᵀ)/2, centrada")}
      <p>Tres consecuencias. El máximo <em>puede</em> pasar de 1: en Columbus llega a
        {n(m2["rango"]["columbus_gal"][1], 4)}, y hay un mapa que lo alcanza —el que sigue al vector
        propio del máximo—. Pero no siempre pasa: en el retículo del módulo 1 se queda en
        {n(m2["rango"]["reticulo_10"][1], 4)}. El mínimo puede quedar lejos de −1: en Columbus, la
        autocorrelación negativa más extrema posible da {n(m2["rango"]["columbus_gal"][0], 4)}, así
        que un −0.5 ahí sería mucho más extremo de lo que parece. Y comparar el I de dos mapas con W
        distintas es comparar números en escalas distintas: una razón más para la regla del módulo
        7, que pide enseñar el I de todas las W en vez de quedarse con una.</p>

      <h3>Y el estilo de W también lo mueve</h3>

      <p>El capítulo 6 enseñó cinco formas de convertir vecinos en pesos. Sobre el mismo CRIME y la
        misma GAL, los estilos B, C y U dan {firma(n(EST["B"]["I"], 6))}; el estilo W,
        {firma(n(EST["W"]["I"], 6))}, y el S, {firma(n(EST["S"]["I"], 6))}. B, C y U son la misma
        matriz multiplicada por una constante, y el factor \(n/S_0\) la cancela: dan el mismo I.
        W y S cambian cuánto pesa cada vecino respecto a los demás —con W, el vecino de una unidad
        con pocos vecinos pesa más—, y eso sí mueve el índice. El capítulo usa W por filas, que es
        el convenio de Anselin y el que hace del rezago una media.</p>

{tabs("El I de Moran pieza a pieza", bloque(R2, **S2), bloque(PY2, **S2P))}
      <p>El bloque calcula I dos veces: a mano, como el cociente de dos productos escalares —con W
        por filas no hace falta nada más—, y con <code>moran.test</code>, que da además la esperanza.
        La pestaña de Python escribe lo mismo con álgebra de vectores. El rango sale de
        <code>eigen()</code> sobre la parte simétrica de W, y hay que simetrizar porque la W por
        filas no es simétrica aunque la vecindad lo sea: el peso que \(i\) le da a \(j\) es uno entre
        los vecinos de \(i\), y el que \(j\) le da a \(i\), uno entre los de \(j\). La segunda
        llamada, sin centrar, da las cotas que publican algunos textos: su máximo,
        {n(m2["rango"]["sin_centrar"]["columbus_gal"][1], 4)}, no lo alcanza ningún reparto de
        valores sobre Columbus.</p>

      <p>Queda la pregunta del módulo 1 sin contestar. Un I de {n(C2["I"], 3)} sobre un rango que
        llega a {n(m2["rango"]["columbus_gal"][1], 4)} parece mucho; si es más de lo que daría el
        azar lo dice el módulo 3.</p>
""" + CIERRE

MOD3 = cabecera(
    3, TITULOS[2][0], INGLES[2],
    "Distinguir las tres formas de obtener la distribución de I bajo la hipótesis nula, saber "
    "qué supone cada una, por qué el p de permutación tiene un suelo y cuánto ve el test según "
    "el número de unidades.") + rf"""
      <p>Un I de {n(C2["I"], 3)} no significa nada hasta que se sabe qué valores da el azar. Hay tres
        formas de averiguarlo. Las tres comparan con el mismo azar —que la posición no importe— y
        se diferencian en lo que suponen además, y conviene separar dos niveles: lo que suponen del
        <em>dato</em> y lo que suponen de la distribución de <em>I</em>.</p>

      <ol>
        <li><strong>Normalidad.</strong> Supone que los valores son extracciones independientes de
          una normal. Bajo ese supuesto I es aproximadamente normal, con una varianza que tiene
          fórmula cerrada: en Columbus, {firma(n(C3["normalidad"]["var"], 5))}, y una
          {firma("z = " + n(C3["normalidad"]["z"], 4))}.</li>
        <li><strong>Aleatorización.</strong> No supone ninguna distribución para el dato: toma los
          valores observados como dados y considera igual de probables todas sus asignaciones a las
          unidades. De ahí saca la media y la varianza exactas de I, y su varianza depende de la
          <em>curtosis</em> del dato —cuánto pesan sus extremos—, que en CRIME vale
          {firma(n(C3["aleatorizacion"]["curtosis"], 4))} (una normal tiene 3). Da una varianza de
          {n(C3["aleatorizacion"]["var"], 6)} y {firma("z = " + n(C3["aleatorizacion"]["z"], 4))}, la
          que publica Anselin (1995). Para el p, en cambio, sí supone algo: que I se reparte como una
          normal con esa media y esa varianza. Es la que <code>moran.test</code> usa por defecto.</li>
        <li><strong>Permutación.</strong> No usa ninguna fórmula ni supone nada sobre la forma de I:
          reparte los valores al azar entre
          los barrios muchas veces y calcula I en cada reparto. El p es la fracción de repartos que
          igualan o superan el I observado, contando el propio observado como uno más:
          \(p = (r + 1)/(\text{{nsim}} + 1)\), donde \(r\) es el número de réplicas que llegan.</li>
      </ol>

      <p>Las dos primeras z se parecen, pero no porque la curtosis de CRIME se parezca a la de una
        normal: con {ent(C1["n"])} unidades el término de la curtosis pesa poco en la varianza, y
        las dos solo se separan con pocas unidades o con un dato de colas muy pesadas. La
        permutación es la que usan GeoDa y <code>esda</code>, y la que el capítulo va a usar para
        todo lo local. Su histograma se puede mirar:</p>

{sim("cap7-permutacion", "El I de 999 repartos al azar",
     "Las réplicas que dio <code>moran.mc</code> sobre Columbus con la semilla 2026, en un "
     "histograma. La línea naranja es el I observado; la gris, E[I]; la curva, la normal que supone "
     "la aleatorización. El deslizador elige cuántas réplicas usar —siempre las primeras de la "
     "misma lista—, y la lectura recalcula el p con ellas.",
     alto=280, aria="Histograma de los I de Moran de las réplicas por permutación de CRIME en "
     "Columbus, con el I observado y la normal de la aleatorización")}
      <p>Ninguna de las {ent(C3["permutacion"]["nsim"])} réplicas llega al I observado: la mayor da
        {firma(n(C3["permutacion"]["max_sim"], 6))}, menos de dos tercios del observado. Su media,
        {n(C3["permutacion"]["media_sim"], 6)}, cae junto a \(E[I]\), y su desviación típica,
        {n(C3["permutacion"]["sd_sim"], 6)}, junto a la raíz de la varianza por aleatorización, que
        es lo que debe pasar: la permutación y la aleatorización hacen la misma hipótesis, una
        contando y la otra con una fórmula. Y fíjate en lo que hace el p al mover el deslizador:
        nunca baja de uno entre el número de réplicas más uno.</p>

      <h3>El suelo del p</h3>

      <p>Ese es el detalle que más se olvida de la permutación: <strong>su p no puede bajar de
        \(1/(\text{{nsim}}+1)\)</strong>, porque el dato observado siempre cuenta. Con 999 réplicas,
        {firma(gx(C3["permutacion"]["p"]))}; con {ent(C3["permutacion_99999"]["nsim"])},
        {cient(C3["permutacion_99999"]["p"])}, que es justo el suelo otra vez. En los municipios se ve
        mejor: la aleatorización da un p de {firma(cient(M3["aleatorizacion"]["p"]))}, con cien
        ceros detrás de la coma. Esa cifra es la cola de una normal a
        z = {n(M3["aleatorizacion"]["z"], 2)}, tan lejos del centro que nadie ha comprobado que I se
        reparta así allí: léase «muchísimo», no la cifra. La permutación da {gx(M3["permutacion"][0]["p"])} con 999 réplicas
        y {gx(M3["permutacion"][1]["p"])} con {ent(M3["permutacion"][1]["nsim"])}. No es que el
        efecto sea menor con la permutación: es que el método no puede decir más con esas réplicas.
        Para un I global da igual —cualquiera de esos p rechaza—, pero en el módulo 10 este suelo
        decide si una corrección de multiplicidad puede funcionar o no.</p>

      <h3>Cuál usar, y lo que las tres suponen</h3>

      <p>La normalidad casi nunca es defendible con datos de área: las tasas, los conteos y las
        proporciones no son normales. La aleatorización es la opción analítica sensata, y la
        permutación la que no necesita fórmula, a cambio de una precisión que depende de las
        réplicas y de un resultado que depende de la semilla. Pero las tres comparten un supuesto
        que no se ve: que <strong>cualquier valor podría haber caído en cualquier unidad</strong>.
        Con una tasa eso falla cuando las unidades tienen poblaciones muy distintas: la deserción de
        un municipio con cuarenta estudiantes es mucho más variable que la de uno con cuarenta mil,
        y permutarlas como si fueran intercambiables trata el ruido de los pequeños como
        estructura. Es el problema de los números pequeños del capítulo 3, y el módulo 11 vuelve a
        él.</p>

      <h3>Cuánto ve el test: la potencia</h3>

      <p>Todo lo anterior responde a «¿es esto más que azar?». La pregunta inversa importa tanto:
        si hay autocorrelación, ¿la ve el test? Depende de cuánta haya y de cuántas unidades se
        tengan, y se puede medir simulando mapas con un ρ conocido —el proceso del retículo del
        módulo 1— y contando cuántas veces rechaza.</p>

{sim("cap7-potencia", "La potencia del test frente a ρ y al número de unidades",
     "Retículos de 25, 49, 100 y 400 celdas, con un proceso SAR de ρ conocido y 1 000 "
     "realizaciones por punto. Cada curva es la fracción de realizaciones en que el test de Moran "
     "bajo normalidad (unilateral, al 5 %) rechaza: aquí ese supuesto sí se cumple, porque los "
     "campos simulados son normales. Elige un ρ para leer las cuatro a la vez.",
     alto=280, aria="La potencia del test de Moran frente a rho para retículos de 25, 49, 100 y "
     "400 celdas")}
      <p>En ρ = 0 las cuatro curvas valen {n(POT[25]["potencia"][0], 3)},
        {n(POT[49]["potencia"][0], 3)}, {n(POT[100]["potencia"][0], 3)} y
        {n(POT[400]["potencia"][0], 3)}: alrededor del 5 % que se fijó, que es lo que debe dar un
        test honesto cuando no hay nada. Con {ent(m3["potencia"]["replicas"])} realizaciones el error
        típico de cada punto ronda {n(_SE_POT, 3)}, y los cuatro quedan a menos de dos errores del
        5 %: el que más se aparta, el de 25 celdas, es azar de la simulación y no un test que
        rechace de más. A partir de ahí manda el tamaño. Con ρ = 0.3 el test rechaza
        {n(POT[25]["potencia"][3], 3)} de las veces con 25 celdas y {n(POT[400]["potencia"][3], 3)}
        con 400; con 49 —el tamaño de Columbus— pasa de {n(POT[49]["potencia"][3], 3)} en ρ = 0.3 a
        {n(POT[49]["potencia"][5], 3)} en ρ = 0.5. <strong>Un test que no rechaza sobre pocas
        unidades no dice que no haya autocorrelación</strong>: puede estar diciendo que no había
        datos para verla.</p>

{tabs("Las tres inferencias y el suelo del p", bloque(R3, **S3R), bloque(PY3, **S3P))}
      <p>El bloque calcula las tres. Las dos z analíticas salen de <code>moran.test</code> con y sin
        <code>randomisation</code>; la permutación, de <code>moran.mc</code>. La línea que cuenta
        réplicas es la definición del p: ninguna alcanzó el I observado, y aun así el p es
        {gx(C3["permutacion"]["p"])} y no cero. En Python, <code>esda</code> baraja con su propio
        generador y sus réplicas no son las de R, pero el p coincide porque las dos se quedan en el
        suelo. Las dos últimas órdenes de R son el suelo con los municipios: un p analítico
        minúsculo y uno de permutación que no baja de {gx(M3["permutacion"][0]["p"])}.</p>

      <p>Hasta aquí, I es un número y un p. Anselin propuso convertirlo en una figura, y la figura
        resulta ser más que una ilustración: es otra forma de calcularlo.</p>
""" + CIERRE

# Los «influyentes» de moran.plot, partidos por lo que de verdad hacen. La
# prosa afirma: dos mueven la recta (cambio > 0.03), dos solo fallan la
# razón de covarianzas, y un barrio SIN marcar la mueve más que esos dos.
_DET = C4["influyentes_detalle"]
_MUEVE = [d for d in _DET if abs(d["cambio"]) > 0.03]
_PREC = [d for d in _DET if d["criterios"] == ["razón de covarianzas"]]
_NOMARC = next(d for d in C4["mueven_mas"] if not d["marcado"])
if len(_MUEVE) != 2 or len(_PREC) != 2 or len(_DET) != 4:
    sys.exit("PARADO: los influyentes ya no se parten en dos que mueven la recta y dos de precisión")
if abs(_NOMARC["cambio"]) <= max(abs(d["cambio"]) for d in _PREC):
    sys.exit("PARADO: ningún barrio sin marcar mueve la recta más que los de precisión")

MOD4 = cabecera(
    4, TITULOS[3][0], INGLES[3],
    "Leer el diagrama de dispersión de Moran: sus cuatro cuadrantes, la recta cuya pendiente es "
    "I, y cuáles de los puntos que <code>moran.plot</code> llama «influyentes» la mueven de verdad.") + rf"""
      <p>El diagrama de Moran (Anselin, 1996) dibuja cada unidad como un punto: en horizontal, su
        valor tipificado \(z_i\); en vertical, la media de los valores tipificados de sus vecinos,
        \((Wz)_i\). Los dos ejes se cortan en cero —la media—, y eso divide la figura en cuatro
        cuadrantes:</p>

      <ul>
        <li><strong>Alto-alto</strong>, arriba a la derecha: una unidad por encima de la media
          rodeada de vecinos por encima de la media.</li>
        <li><strong>Bajo-bajo</strong>, abajo a la izquierda: por debajo, entre vecinos por
          debajo.</li>
        <li><strong>Alto-bajo</strong>, abajo a la derecha: por encima de la media entre vecinos por
          debajo.</li>
        <li><strong>Bajo-alto</strong>, arriba a la izquierda: por debajo, entre vecinos por
          encima.</li>
      </ul>

      <p>Los dos primeros son <em>parecido</em> entre vecinos y los dos últimos, <em>contraste</em>.
        Un mapa con autocorrelación positiva amontona sus puntos en los dos primeros, y la nube se
        inclina.</p>

      <h3>La pendiente es I</h3>

      <p>La recta de mínimos cuadrados de \(Wz\) sobre \(z\) tiene una pendiente \(b\). Como \(z\)
        está centrada, esa pendiente es la misma con término independiente o sin él, y se puede
        escribir sin él. Comparándola con la fórmula del módulo 2 sale una identidad:</p>

{F_PENDIENTE}
      <p>Con W por filas, \(n/S_0 = 1\) y <strong>la pendiente <em>es</em> el I de Moran</strong>, no
        una aproximación. En Columbus, {firma(n(C4["pendiente"], 6))}, el mismo I del módulo 2. La
        condición que importa es esa, \(n/S_0 = 1\): W por filas y sin islas. Centrar o tipificar el
        dato no hace falta. La recta con término independiente sobre el CRIME crudo da la misma
        pendiente, {n(C4["pendiente_sin_tipificar"], 6)}, porque con W por filas el rezago de un
        dato trasladado se traslada lo mismo, y escalar los dos ejes por igual no la mueve. Con
        islas la cosa cambia, como se ve abajo con los municipios. Y con la W binaria la pendiente se
        separa de I por el factor \(n/S_0\); el ejercicio 2 lo comprueba sobre otro mapa.</p>

      <p>Sobre los {ent(C1["n"])} barrios, los cuadrantes se reparten así:
        {firma(ent(C4["cuadrantes"]["AA"]))} alto-alto y {firma(ent(C4["cuadrantes"]["BB"]))}
        bajo-bajo, frente a {firma(ent(C4["cuadrantes"]["AB"]))} alto-bajo y
        {firma(ent(C4["cuadrantes"]["BA"]))} bajo-alto.</p>

      <p>Y <code>moran.plot</code> marca {ent(C4["influyentes"])} barrios como
        <strong>influyentes</strong>: los POLYID {", ".join(ent(x) for x in C4["influyentes_polyid"][:-1])}
        y {ent(C4["influyentes_polyid"][-1])}. La palabra engaña. La columna <code>is_inf</code> marca a
        quien falle <em>cualquiera</em> de los diagnósticos de influencia de una regresión
        (<code>influence.measures</code>): cuánto cambiarían los coeficientes sin el punto (DFBETAS),
        cuánto su propio ajuste (DFFIT), la precisión de la pendiente (razón de covarianzas), la
        distancia de Cook y la palanca. No todos mueven la recta. Sin el POLYID
        {ent(_MUEVE[0]["polyid"])} la pendiente pasa de {n(C4["pendiente"], 4)} a
        {firma(n(_MUEVE[0]["pendiente_sin"], 4))}, y sin el {ent(_MUEVE[1]["polyid"])} a
        {n(_MUEVE[1]["pendiente_sin"], 4)}: esos dos sí la mueven. El {ent(_PREC[0]["polyid"])} y el
        {ent(_PREC[1]["polyid"])} solo fallan la razón de covarianzas —están lejos en horizontal y
        caen cerca de la recta—: cambian lo precisa que es la pendiente, no cuánto vale, y sin ellos
        queda en {n(_PREC[0]["pendiente_sin"], 4)} y {n(_PREC[1]["pendiente_sin"], 4)}. Y hay
        barrios sin marcar que la mueven más que esos dos: sin el POLYID {ent(_NOMARC["polyid"])},
        {n(_NOMARC["pendiente_sin"], 4)}.</p>

{sim("cap7-diagrama", "El diagrama de Moran, clicable",
     "Cada punto es una unidad, coloreada por su <em>cuadrante</em> —rojo alto-alto, azul "
     "bajo-bajo, rosa alto-bajo, celeste bajo-alto—, no por su significación, que llega en el "
     "módulo 9. En Columbus, los cuatro «influyentes» llevan un anillo negro. Pulsa un punto —o "
     "recórrelos con las flechas de los botones— y el mapa de abajo la pinta de naranja sobre el "
     "verde del dato; en Columbus, la figura rodea además a sus vecinos con un aro naranja. La "
     "lectura dice dónde cae y en qué cuadrante. La recta es la de mínimos cuadrados y su "
     "pendiente, el I de Moran. Cambia de tablero para ver los municipios: las dos islas salen "
     "huecas, porque no tienen cuadrante.",
     alto=320, aria="Diagrama de dispersión de Moran: cada unidad con su valor tipificado frente a "
     "la media de sus vecinos, la recta de mínimos cuadrados y la unidad seleccionada")}
{mapa_html("cap7-diagrama-mapa", "La unidad seleccionada en el diagrama")}
      <p>Prueba con los cuatro del anillo negro. El POLYID {ent(m5["pico_en_alto"]["polyid"])} es el barrio
        de mayor CRIME, y su punto queda lejos a la derecha: es el que el módulo 5 va a disparar
        para ver qué le hace un extremo a cada índice. Y busca un punto pegado al eje vertical pero
        bastante arriba: un barrio de valor casi medio rodeado de vecinos altos. En el diagrama apenas
        llama la atención; en el módulo 8 resulta ser el de p más pequeño de todo el mapa.</p>

      <p>Con los municipios aparece algo que no se ve en Columbus. La recta que reproduce el I de
        <code>spdep</code> —{firma(n(M4["pendiente_todas"], 6))}— es la de las
        {ent(M1["con_dato"])} unidades <em>con</em> las dos islas, que se quedan sobre el eje
        horizontal porque su rezago vale cero. Sobre las {ent(M3["aleatorizacion"]["n_con_vecinos"])}
        que tienen vecinos, la pendiente es {n(M4["pendiente_con_vecinos"], 6)}. Es al revés de lo
        que uno esperaría, y tiene explicación: con islas, <code>spdep</code> toma \(n\) como las
        unidades con vecinos y \(S_0\) también vale eso, así que el factor sigue siendo 1 y la
        identidad se cumple sobre todas. Y aquí centrar sí importa: con el dato crudo la recta da
        {n(M4["pendiente_cruda_todas"], 6)}, porque el rezago de una isla vale cero y no la media,
        así que trasladar el dato ya no traslada su rezago lo mismo. Las dos islas no tienen
        cuadrante —su rezago no mide nada— y el diagrama las deja huecas. Los cuadrantes municipales, contando solo las unidades con
        vecinos: {ent(M4["cuadrantes"]["AA"])} alto-alto, {ent(M4["cuadrantes"]["BB"])} bajo-bajo,
        {ent(M4["cuadrantes"]["AB"])} alto-bajo y {ent(M4["cuadrantes"]["BA"])} bajo-alto.</p>

{tabs("El diagrama de Moran", bloque(R4, **S4R), bloque(PY4, **S4P))}
      <p>Tres comprobaciones en el bloque. La pendiente de <code>lm()</code> coincide con el I del
        módulo 2 hasta el sexto decimal. Los cuadrantes salen de dos signos, el del valor y el de
        su rezago. Y <code>moran.plot</code> con <code>return_df = TRUE</code> devuelve, sin dibujar
        nada, la columna <code>is_inf</code> que marca los influyentes; la línea siguiente rehace la
        recta sin cada uno y enseña cuáles la mueven. La recta sobre el dato crudo confirma que
        centrar no hacía falta. Las tres últimas órdenes son la sorpresa de las islas: la recta que
        reproduce I es la de todas las unidades, y solo con el dato centrado.</p>

      <p>I mira productos: si dos vecinos caen del mismo lado de la media. Hay otra forma de medir
        el parecido —mirar directamente cuánto se diferencian— y no siempre dice lo mismo.</p>
""" + CIERRE

_PA, _PB = m5["pico_en_alto"], m5["pico_en_bajo"]
_TV = {t["variable"]: t for t in m5["tres_variables"]}
# Lo que la prosa del módulo 5 afirma del mecanismo y de las tres variables.
if not (_PA["cocientes_8"]["numerador_c"] > _PA["cocientes_8"]["denominador"] > _PA["cocientes_8"]["numerador_I"]
        and _PB["cocientes_8"]["numerador_I"] < 1):
    sys.exit("PARADO: el mecanismo del barrio disparado ya no es el que cuenta el módulo 5")
_DISC5 = {v: abs(_TV[v]["I"] - _TV[v]["uno_menos_c"]) for v in _TV}
if not (max(_TV, key=lambda v: _TV[v]["z_max_abs"]) == "HOVAL" == min(_DISC5, key=_DISC5.get)
        and max(_DISC5, key=_DISC5.get) == "INC"):
    sys.exit("PARADO: HOVAL ya no es la de dato más extremo y menor discrepancia, o INC la de mayor")

MOD5 = cabecera(
    5, TITULOS[4][0], INGLES[4],
    "Entender qué mide la c de Geary, por qué va al revés que I y qué enseña un valor extremo "
    "a los dos índices.") + rf"""
      <p>El I de Moran compara cada valor con la <em>media global</em>: \(z_i z_j\) es grande cuando
        dos vecinos están, los dos, lejos de la media y del mismo lado. Geary (1954) propuso mirar
        otra cosa: comparar a los vecinos <em>entre sí</em>, sin pasar por la media, con la
        diferencia al cuadrado de sus valores.</p>

{F_GEARY}
      <p>El numerador suma \((x_i - x_j)^2\) sobre las parejas de vecinos: es pequeño cuando los
        vecinos se parecen y grande cuando no. El denominador vuelve a ser la variabilidad total, y
        las constantes están elegidas para que, bajo la hipótesis nula, \(E[c] = 1\). De ahí sale su
        sentido, que es el contrario del de I: <strong>c por debajo de 1 es autocorrelación
        positiva</strong> —vecinos más parecidos de lo que daría el azar— y por encima de 1,
        negativa. Para ponerlos en la misma dirección se compara I con \(1 - c\).</p>

      <p>En Columbus, {firma("c = " + n(C5["c"], 5))}, con una z de {n(C5["z"], 4)} y un p analítico de
        {cient(C5["p"])}; por permutación, con {ent(C5["nsim_permutacion"])}
        réplicas, el p se queda en el suelo, {gx(C5["p_permutacion_9999"])}. Así que
        \(1 - c = \) {n(C5["uno_menos_c"], 5)}, frente a un I de {n(C5["I"], 6)}. Y con las otras dos
        variables del tablero —el valor de la vivienda y el ingreso— pasa lo mismo: se parecen sin
        ser iguales.</p>

{tabla(["Variable", "I de Moran", "c de Geary", "1 − c"],
       fila("CRIME (delitos)", n(_TV["CRIME"]["I"], 4), n(_TV["CRIME"]["c"], 4), n(_TV["CRIME"]["uno_menos_c"], 4))
       + fila("HOVAL (valor de la vivienda)", n(_TV["HOVAL"]["I"], 4), n(_TV["HOVAL"]["c"], 4), n(_TV["HOVAL"]["uno_menos_c"], 4))
       + fila("INC (ingreso)", n(_TV["INC"]["I"], 4), n(_TV["INC"]["c"], 4), n(_TV["INC"]["uno_menos_c"], 4)),
       "Los dos índices sobre las tres variables de Columbus, con la GAL por filas")}
      <p>Que no coincidan tiene causa, y es la diferencia de definición. Piensa en una zona de
        barrios muy parecidos entre sí pero con valores cerca de la media. Para Moran casi no
        cuenta: sus \(z_i z_j\) son productos de números pequeños. Para Geary es parecido puro: sus
        diferencias al cuadrado son mínimas. Moran premia los grupos que se apartan de la media;
        Geary, los vecinos que se parecen, estén donde estén.</p>

      <h3>Un barrio disparado</h3>

      <p>Esa diferencia se ve forzándola. El experimento es multiplicar el CRIME de un solo barrio
        por un factor y recalcular los dos índices sin tocar nada más.</p>

{sim("cap7-geary", "Un barrio disparado: qué le hace un extremo a cada índice",
     f"Elige el barrio que se dispara: el de mayor CRIME (el POLYID {ent(_PA['polyid'])}, alto entre "
     f"altos, con {ent(_PA['grado'])} vecinos) o el de vecindad más baja (el POLYID "
     f"{ent(_PB['polyid'])}, de CRIME {n(_PB['crime'], 4)}, el barrio cuyos vecinos tienen la media "
     "más baja del mapa). En horizontal, el factor por el que se multiplica su valor; las líneas "
     "discontinuas marcan el valor de cada índice bajo la hipótesis nula: E[I] para I y 1 para c.",
     alto=280, aria="El I de Moran y la c de Geary de Columbus al multiplicar el CRIME de un solo "
     "barrio por un factor de 1 a 8")}
      <p>En los dos casos el extremo empuja a I hacia su valor nulo, \(E[I]\), y a c hacia arriba.
        Con el factor ocho sobre el POLYID {ent(_PA['polyid'])}, I baja de
        {n(_PA["curva"][0]["I"], 3)} a {firma(n(_PA["curva"][-1]["I"], 4))} y c sube de
        {n(_PA["curva"][0]["c"], 4)} a {firma(n(_PA["curva"][-1]["c"], 4))}; sobre el
        {ent(_PB['polyid'])}, I acaba en {n(_PB["curva"][-1]["I"], 4)} y c en
        {n(_PB["curva"][-1]["c"], 2)}. Un solo barrio hace desaparecer casi toda la autocorrelación
        de un mapa que la tiene. Pero la razón no es la misma en los dos índices, y se ve
        separando el numerador del denominador.</p>

      <p>Con el factor ocho sobre el POLYID {ent(_PA['polyid'])}, el denominador —la variabilidad
        total— se multiplica por {n(_PA["cocientes_8"]["denominador"], 2)}, y el numerador de Moran
        solo por {n(_PA["cocientes_8"]["numerador_I"], 2)}: el extremo entra en el denominador al
        cuadrado y en el numerador una sola vez, multiplicado por sus vecinos, así que I se hunde.
        Sobre el {ent(_PB['polyid'])} lo que se hunde es el numerador, que queda en
        {n(_PB["cocientes_8"]["numerador_I"], 2)} veces el original: el barrio deja de sumar como bajo
        entre bajos y pasa a restar como alto entre bajos. En Geary pasa lo contrario: su numerador
        crece <em>más</em> que el denominador —{n(_PA["cocientes_8"]["numerador_c"], 2)} veces
        frente a {n(_PA["cocientes_8"]["denominador"], 2)} sobre el {ent(_PA['polyid'])}—, porque las
        diferencias con los vecinos crecen al cuadrado igual que la varianza, y por eso c sube. Si
        el factor siguiera creciendo, el extremo acabaría dominando numerador y denominador a la vez,
        y cada índice tendería a un límite que solo depende de la vecindad de ese barrio: I a
        {n(_PA["limite"]["I"], 4)}, casi \(E[I]\), y c a \((1 + \textstyle\sum_j w_{{jk}})/2\), la
        mitad de uno más la suma de la columna de ese barrio en W: {n(_PA["limite"]["c"], 4)} para el
        {ent(_PA['polyid'])}. Ese límite no es 1 en general: en Columbus va de
        {n(m5["limite_c_rango"][0], 4)} a {n(m5["limite_c_rango"][1], 4)} según el barrio.</p>

      <p>Ninguno es robusto, entonces. Pero no se mueven igual: cuánto se desplaza cada uno depende
        de dónde caiga el extremo y de cuántos vecinos tenga. Aquí los dos se hunden casi al mismo
        ritmo; en el ejercicio 3, sobre otro mapa, I cae casi a la mitad y c apenas se mueve. Por
        eso, <strong>cuando I y \(1 - c\) cuentan historias distintas sobre el mismo dato, hay dos
        sospechosos</strong>: la diferencia de definición, como en el ingreso de la tabla, y un valor
        extremo, como en el ejercicio 3. No hay que darlo por hecho en ninguna dirección: el valor de
        la vivienda tiene el dato más extremo de los tres —{n(_TV["HOVAL"]["z_max_abs"], 2)}
        desviaciones típicas— y es donde I y \(1 - c\) más se parecen. El diagrama de Moran del
        módulo 4 es donde se distinguen los dos casos: un extremo aparece como un punto aislado,
        lejos de la nube.</p>

      <p>En los municipios la c de la deserción vale {n(m5["municipios"]["c"], 6)}, con una z de
        {n(m5["municipios"]["z"], 4)}: la misma conclusión que I, {n(m5["municipios"]["I"], 6)}, con
        un número distinto.</p>

{tabs("La c de Geary y el barrio disparado", bloque(R5, **S5R), bloque(PY5, **S5P))}
      <p>El bloque calcula c con <code>geary.test</code> y repite el experimento del simulador en su
        punto final. La pestaña de Python enseña un convenio que conviene conocer antes de comparar
        bibliotecas: <code>spdep</code> escribe la z de Geary como \((E[c] - c)/\text{{sd}}\), positiva
        cuando hay parecido, para que se lea como la de Moran; <code>esda</code> la escribe al
        revés, \((c - E[c])/\text{{sd}}\). Es la misma cifra con el signo cambiado, y quien no lo sepa
        creerá que una biblioteca contradice a la otra.</p>

      <p>I y c resumen el mapa en un número calculado con una sola vecindad, la de primer orden. El
        módulo 6 pregunta qué pasa más lejos, y qué hacer cuando la variable no es un número sino
        una categoría.</p>
""" + CIERRE

_CGM = CG["municipios"]
_JCD = {f["par"]: f for f in JC["municipios_desercion"]["tabla"]}
_JCT = {f["par"]: f for f in JC["municipios_tipo"]["tabla"]}

MOD6 = cabecera(
    6, TITULOS[5][0], INGLES[5],
    "Medir la autocorrelación a distancias crecientes con el correlograma, y contrastarla con "
    "una variable binaria con el join count.") + rf"""
      <p>El correlograma del capítulo 1 agrupaba las parejas de estaciones por bandas de kilómetros.
        Con datos de área la distancia natural no se mide en kilómetros sino en <strong>órdenes de
        contigüidad</strong>: el orden 1 son los vecinos; el orden 2, los vecinos de los vecinos
        que no eran ya vecinos —<code>nblag</code> no acumula, como enseñó el capítulo 6—, y así
        sucesivamente. Calcular I en cada orden dice hasta dónde llega el parecido.</p>

{sim("cap7-correlograma", "El correlograma por órdenes de contigüidad",
     "Una barra por orden con su I de Moran: verde si es positivo, morada si es negativo. Las "
     "líneas marcan E[I] y la banda de dos desviaciones típicas a cada lado, la que el azar casi "
     "nunca rebasa. Pulsa una barra —o recórrelas con los botones— y la lectura da su I, su "
     "esperanza, su z y cuántas parejas tiene; la elegida se pinta de naranja. Cambia de tablero y "
     "mira hasta qué orden llega el parecido en cada uno.",
     alto=280, aria="El I de Moran por orden de contigüidad, con E[I] y su banda de dos "
     "desviaciones típicas")}
      <p>En Columbus el I pasa de {n(_CGC[0]["I"], 4)} en el orden 1 a {n(_CGC[1]["I"], 4)} en el 2 y se
        vuelve <strong>negativo</strong> desde el 3: {n(_CGC[2]["I"], 4)}, {n(_CGC[3]["I"], 4)} y
        {n(_CGC[4]["I"], 4)} en los órdenes 3, 4 y 5, este último con una z de {n(_CGC[4]["z"], 4)}.
        Una autocorrelación negativa a larga distancia no significa que los barrios lejanos «se
        repelan». Es la huella típica de un <strong>gradiente</strong>: valores altos en una parte
        de la ciudad y bajos en la otra, de modo que dos barrios a cinco pasos suelen caer en lados
        opuestos. En Columbus los barrios del centro tienen más delitos que los de la
        periferia, y el capítulo 8 trata una tendencia así como lo que es, una variable que falta
        en el modelo. El orden 6 ya es el borde: deja {ent(_CGC[5]["sin_vecinos"])} barrios sin
        vecinos y el grafo partido en {ent(_CGC[5]["subgrafos"])} trozos, y hace falta
        <code>zero.policy</code> para calcularlo.</p>

      <p>En los municipios el parecido se apaga despacio: {n(_CGM[0]["I"], 4)} en el orden 1,
        {n(_CGM[3]["I"], 4)} en el 4, {n(_CGM[5]["I"], 4)} en el 6 y {n(_CGM[6]["I"], 4)} en el 7, ya
        indistinguible de \(E[I]\) (z = {n(_CGM[6]["z"], 4)}). En el 8 sale de la banda por abajo
        (z = {n(_CGM[7]["z"], 4)}): a esa distancia, como en Columbus, los municipios tienden a caer
        en lados opuestos de la media. Y hay un detalle que conviene mirar en
        la lectura: la z del orden 2, {n(_CGM[1]["z"], 4)}, es <em>mayor</em> que la del orden 1,
        {n(_CGM[0]["z"], 4)}, aunque su I sea menor. El orden 2 tiene muchas más parejas
        —{ent(_CGM[1]["pares"])} frente a {ent(_CGM[0]["pares"])}— y con más parejas la varianza de
        I baja. <strong>Significación no es magnitud</strong>, y esto se va a repetir con los I
        locales del módulo 8.</p>

      <h3>Cuando la variable es binaria: el join count</h3>

      <p>Si la variable solo tiene dos valores —centro o periferia, por encima o por debajo de la
        mediana—, el parecido entre vecinos se puede contar directamente: cuántas parejas de vecinos
        son de la misma categoría y cuántas mezclan las dos, frente a las que habría si las
        categorías estuvieran repartidas al azar. Es el <strong>join count</strong> (uniones), el
        estadístico más antiguo de los de este capítulo.</p>

      <p>Un detalle de <code>spdep</code> antes de leer las cifras: con la W por filas, las uniones
        no se cuentan, se <em>pesan</em>. Cada barrio reparte un peso total de 1 entre sus vecinos,
        así que las uniones suman la mitad de \(S_0\) y no el número de parejas, y salen con
        decimales. Y no es solo una cuestión de escala: con la W binaria, que sí cuenta parejas, la z
        de las uniones periferia–periferia de Columbus baja de {n(_JCP["periferia:periferia"]["z"], 2)}
        a {n(_JCB["periferia:periferia"]["z"], 2)}, y su p por permutación pasa del suelo,
        {gx(JC["columbus_cp"]["p_permutacion"][0]["p"])}, a
        {gx(JC["columbus_cp_binaria"]["p_permutacion"][0]["p"])}. El mismo dato con la misma vecindad
        y otros pesos da otra evidencia: es la lección del módulo 7 en miniatura. El capítulo sigue
        con la W por filas, la de todo lo demás.</p>

{sim("cap7-joincount", "Uniones observadas frente a las esperadas",
     "Tres variables binarias. CP es la de Columbus: centro o periferia. Las dos municipales: la "
     "deserción por encima o por debajo de la mediana, y el tipo de entidad —las áreas no "
     "municipalizadas y San Andrés frente a los municipios—. Para cada tipo de pareja de vecinos, "
     "las uniones observadas y las que daría un reparto al azar.",
     alto=260, aria="Uniones observadas y esperadas por tipo de pareja de vecinos para la "
     "variable binaria elegida")}
      <p>Las tres dicen lo mismo con distinto grado de obviedad. CP es la ubicación misma, así que su
        resultado es casi una comprobación del método: las parejas centro–centro pesan
        {n(_JCP["centro:centro"]["observado"], 4)} frente a una esperanza de
        {n(_JCP["centro:centro"]["esperado"], 2)}, y las mixtas {n(_JCP["centro:periferia"]["observado"], 4)}
        frente a {n(_JCP["centro:periferia"]["esperado"], 1)} (z = {n(_JCP["centro:periferia"]["z"], 4)}).
        La deserción sobre la mediana repite en binario lo que dijo el I de Moran: las parejas de
        dos municipios por encima pesan {n(_JCD["sobre la mediana:sobre la mediana"]["observado"], 4)}
        frente a {n(_JCD["sobre la mediana:sobre la mediana"]["esperado"], 0)}, con una z de
        {n(_JCD["sobre la mediana:sobre la mediana"]["z"], 4)}. Y el tipo de entidad da la z más alta
        de las tres, {n(_JCT["no municipalizada o isla:no municipalizada o isla"]["z"], 4)}: las
        dieciocho áreas no municipalizadas, todas en Amazonas, Guainía y Vaupés, están pegadas unas a
        otras. La categoría suma {ent(JC["municipios_tipo"]["n_por_nivel"][0])} unidades porque incluye
        además a San Andrés, que es una de las dos islas del grafo y no se une con nadie. Esa z no
        hay que leerla como la más fuerte de las tres: con una categoría tan rara la esperanza de
        esas uniones es diminuta, y la aproximación normal infla la z. Significación no es magnitud,
        otra vez. Lo que sí comparten las tres es el p por permutación, que en todas las categorías
        es el suelo de sus réplicas, {gx(JC["columbus_cp"]["p_permutacion"][0]["p"])}.</p>

{tabs("Correlograma y join count", bloque(R6, **S6R), bloque(PY6, **S6P))}
      <p><code>sp.correlogram</code> hace en una llamada lo que el simulador enseña: <code>nblag</code>
        para cada orden y un test de Moran sobre cada uno. En Python, <code>higher_order</code> da
        los vecinos a exactamente k pasos y coincide con <code>nblag</code> hasta el orden 5; en el
        6, con barrios sin vecinos, cada biblioteca cuenta \(n\) a su manera, que es la discrepancia
        que el módulo 9 declara. El join count sale de <code>joincount.multi</code>: una fila por
        tipo de pareja con las uniones, su esperanza y su z.</p>

      <p>Hasta aquí todo se ha calculado con una sola W por tablero. El módulo 7 hace el experimento
        contrario: deja quieto el dato y cambia la W.</p>
""" + CIERRE

_GVR = m7["gal_vs_reina"]
_RES7 = m7["resumen"]
_NGVR = _GVR["solo_gal"] + _GVR["solo_reina"]
# Lo que el módulo 7 afirma: por permutación todas en el suelo, y la del
# umbral a medias es la única que el analítico deja por encima de 0.001.
_SUELO7 = W7["gal"]["p_permutacion"]
if _RES7["columbus_p_perm_max"] != _SUELO7 or _RES7["municipios_p_perm_max"] != _SUELO7:
    sys.exit("PARADO: alguna W ya no rechaza en el suelo de la permutación")
if [e["id"] for e in m7["columbus"] if e["p"] >= 0.001] != ["d_mitad"] or not 0.01 < W7["d_mitad"]["p"] < 0.05:
    sys.exit("PARADO: la excepción analítica del módulo 7 ya no es solo el umbral a medias, al borde")

MOD7 = cabecera(
    7, TITULOS[6][0], INGLES[6],
    "Medir cuánto cambia el I de Moran al cambiar W, y saber qué hay que publicar para que esa "
    "dependencia no se esconda.") + rf"""
      <p>El capítulo 6 construyó diez definiciones de vecino sobre los mismos 49 polígonos de
        Columbus y avisó de que todo lo que viniera después dependería de cuál se eligiera. Aquí se
        cobra el aviso: el mismo CRIME, las mismas diez vecindades y la GAL de Anselin como
        undécima, y un I de Moran para cada una.</p>

{sim("cap7-w", "El mismo dato bajo once W",
     "Elige una vecindad: el mapa dibuja su grafo y la barra resaltada es su I. La lectura da lo "
     "que hay que mirar de cada una —parejas, grado medio, unidades sin vecinos y si es "
     "simétrica— junto al I, su esperanza, su z, su p analítico y su p por permutación. "
     "«Simétrica» dice si cada vecino reconoce al otro: con k vecinos más próximos no siempre, "
     "porque que tú seas el más próximo de alguien no lo hace el tuyo, y por eso las parejas no "
     "son n por k entre dos.",
     alto=260, aria="El I de Moran de CRIME en Columbus bajo once definiciones de vecindad, con la "
     "elegida resaltada")}
{mapa_html("cap7-w-mapa", "Columbus: el grafo de la vecindad elegida")}
      <p>El I va de {firma(n(_RES7["columbus_I"][0], 4))}, con el umbral de distancia a la mitad del
        mínimo conexo, a {firma(n(_RES7["columbus_I"][1], 4))}, con un solo vecino más próximo. Las
        once rechazan la hipótesis nula al 5 %. Por permutación, las once lo hacen en el suelo de sus
        {ent(W7["gal"]["nsim_permutacion"])} réplicas, p = {gx(_RES7["columbus_p_perm_max"])}. Con
        el test analítico, diez quedan por debajo de una milésima, y la excepción es la del umbral a
        medias, que deja {ent(W7["d_mitad"]["islas"])} barrios sin vecinos y da
        {firma("p = " + n(_RES7["columbus_p_max"], 5))}. Esa diferencia no la pone el dato: la pone
        el convenio de islas. Con islas, <code>spdep</code> calcula la esperanza y la varianza de I
        contando solo las unidades que tienen vecinos —el mismo convenio que en el módulo 4—, pero
        los valores que reparte son todos. Por eso la esperanza no es {n(W7["gal"]["EI"], 6)} sino
        {n(W7["d_mitad"]["EI"], 2)}. Y el I mismo depende del convenio: con el de <code>esda</code>,
        que cuenta como \(n\) todas las unidades, esa W da {n(W7["d_mitad"]["I_esda"], 4)} y no
        {n(W7["d_mitad"]["I"], 4)}. Una W que deja la mitad del mapa sin vecinos no mide mal el
        parecido: mide algo que depende de cómo se cuente a los que no tienen con quién
        parecerse.</p>

      <p>La GAL y la reina, que parecen la misma vecindad, se diferencian en {ent(_NGVR)} parejas:
        {ent(_GVR["solo_gal"])} está solo en la GAL y {ent(_GVR["solo_reina"])} solo en la reina,
        contactos en los que la lista de Anselin y los polígonos del <code>.gpkg</code> no
        coinciden. Basta para mover la segunda cifra: {n(_GVR["I_gal"], 6)} con la GAL y
        {n(_GVR["I_reina"], 6)} con la reina, que es el 0.5002 que el capítulo 6 calculó para este
        mismo dato. Ninguna de las dos está mal: son dos decisiones distintas sobre qué cuenta como
        tocarse.</p>

      <p>Con los municipios pasa lo mismo a otra escala. Seis definiciones, la deserción, y estos
        resultados:</p>

{tabla(["Vecindad", "Parejas", "Grado medio", "Sin vecinos", "I", "z"],
       "".join(fila(e["etiqueta"], ent(e["pares"]), n(e["grado"], 4), ent(e["islas"]),
                    n(e["I"], 4), n(e["z"], 4)) for e in m7["municipios"]),
       "La deserción municipal bajo seis definiciones de vecindad")}
      <p>De {n(_RES7["municipios_I"][0], 4)} con el umbral de 50 km —que deja
        {ent(W7M["d50"]["islas"])} municipios sin vecinos— a {n(_RES7["municipios_I"][1], 4)} con
        cuatro vecinos más próximos. El mayor de los seis p analíticos es
        {cient(_RES7["municipios_p_max"])}, y por permutación los seis están en el suelo,
        {gx(_RES7["municipios_p_perm_max"])}.
        En los dos tableros la lección es la misma: <strong>la sensibilidad a W es de magnitud, no
        siempre de veredicto</strong>. El I cambia bastante; la conclusión de que hay
        autocorrelación no cambia en ninguna de las diecisiete vecindades. La del umbral a medias,
        que el test analítico dejaba al borde, la permutación la deja en el suelo: el borde era del
        convenio de islas, no del dato. Y por eso la sensibilidad es fácil de esconder: quien publica un solo I no
        está mintiendo, pero está callando que con otra W, igual de defendible, el número sería
        otro.</p>

      <div class="warning">
        <h4>Lo honesto, en tres reglas</h4>
        <ol style="margin-bottom:0;">
          <li><strong>Elegir W antes de ver el I</strong>, con una razón sustantiva —quién influye en
            quién, como pedía el capítulo 6—, no por el resultado que da.</li>
          <li><strong>Publicar la sensibilidad</strong>: el I bajo dos o tres W razonables, como en
            la tabla de arriba. Si el veredicto aguanta, el resultado es más sólido; si no aguanta,
            eso es lo que hay que contar.</li>
          <li><strong>No elegir la W que da el resultado más llamativo.</strong> Probar diez
            vecindades y quedarse con la del p más pequeño es elegir la conclusión, y el p ya no
            significa lo que dice. Es la multiplicidad del módulo 10, aplicada a W.</li>
        </ol>
      </div>

{tabs("El mismo CRIME bajo distintas W", bloque(R7, **S7R), bloque(PY7, **S7P))}
      <p>El bloque recorre cinco vecindades con un <code>sapply</code>: la función es la misma y solo
        cambia el <code>nb</code>. En Python, los polígonos de <code>libpysal</code> se reordenan por
        POLYID antes de construir nada, y la reina y los k vecinos más próximos dan los mismos I que
        en R. Para la GAL, la pestaña de Python del módulo 1 ya construyó la W desde el CSV.</p>

      <p>Todos los números de este módulo, y de los seis anteriores, son <em>globales</em>: un I para
        el mapa entero. Un I de {n(C2["I"], 3)} dice que hay parecido entre vecinos, pero no dónde. El
        módulo 8 parte ese número en un trozo por unidad.</p>
""" + CIERRE

_TOP = M8["top5"]
# Los barrios que la prosa nombra se BUSCAN, no se apuntan por posición: si el
# precálculo cambia, una posición fija nombraría a otro barrio sin avisar.
_ORD = sorted(range(len(C8["Ii"])), key=lambda i: -C8["Ii"][i])
_IDX24 = C8["p_rangos"].index(C8["p_min"])
_CRIME = M["cap7-columbus"]["capas"][0]["valor"]
if M["cap7-columbus"]["polyid"] != C8["polyid"] or C4["puntos"]["polyid"] != C8["polyid"]:
    sys.exit("PARADO: el mapa, el diagrama y los LISA de Columbus no vienen en el mismo orden")
if _CRIME.index(min(_CRIME)) != _ORD[-1]:
    sys.exit("PARADO: el I local más negativo ya no es el barrio de menos delitos; reescribe el módulo 8")
if not (C8["cuadrante"][_ORD[0]] == C8["cuadrante"][_ORD[1]] == "High-High"):
    sys.exit("PARADO: los dos mayores I locales ya no son alto-alto; reescribe el módulo 8")
if not (abs(C4["puntos"]["z"][_IDX24]) < 0.3 and C4["puntos"]["wz"][_IDX24] > 1):
    sys.exit("PARADO: el barrio de menor p ya no es «casi en la media entre vecinos altos»")
_RANK24 = _ORD.index(_IDX24) + 1
if not C8["Ii"][_IDX24] < C8["media_Ii"]:
    sys.exit("PARADO: el barrio de menor p ya no está por debajo de la línea de la media")
if m9["columbus"]["conteo"][3] or m9["columbus"]["conteo"][4]:
    sys.exit("PARADO: algún atípico de Columbus es significativo y el pie de cap7-local dice que ninguno")

MOD8 = cabecera(
    8, TITULOS[7][0], INGLES[7],
    "Descomponer el I global en un I por unidad, entender su prueba por permutación condicional y "
    "por qué su p no es el de un test aislado.") + rf"""
      <p>Anselin (1995) observó que el numerador del I de Moran es una suma de términos, uno por
        unidad, y que cada término se puede mirar por separado. El de la unidad \(i\) es su valor
        centrado multiplicado por el rezago de los centrados de sus vecinos:</p>

{F_LOCAL}
      <p>Es un <strong>indicador local de asociación espacial</strong> —LISA, por sus siglas en
        inglés—, y lo que lo hace local y no solo «otro número» es la segunda línea: sumados,
        reconstruyen el global (sin islas; con ellas falla, y abajo se ve por qué). Con W por filas \(S_0 = n\), así que <em>la media</em> de los
        \(I_i\) es el I de Moran. En Columbus, {firma(n(C8["media_Ii"], 6))}, el mismo I de siempre,
        y la suma, {n(C8["suma_Ii"], 5)}, es {ent(C8["S0"])} veces eso. Un \(I_i\) positivo es una
        unidad del mismo lado de la media que sus vecinos (alto-alto o bajo-bajo); uno negativo, una
        unidad del lado contrario.</p>

      <p>Los mayores de Columbus son alto-alto: el POLYID {ent(C8["polyid"][_ORD[0]])} da
        {n(C8["Ii"][_ORD[0]], 5)} y el {ent(C8["polyid"][_ORD[1]])}, {n(C8["Ii"][_ORD[1]], 5)}. El más
        negativo es el POLYID {ent(C8["polyid"][_ORD[-1]])}, con {n(C8["Ii"][_ORD[-1]], 5)}: el barrio
        de menos delitos de todo el mapa, rodeado de vecinos por encima de la media.</p>

      <h3>Cada \(I_i\) necesita su propio azar</h3>

      <p>Para saber si un \(I_i\) es más de lo esperable hace falta su distribución bajo la nula, y
        aquí la permutación cambia de forma: es <strong>condicional</strong>. El valor de la unidad
        \(i\) se queda quieto, y lo que se baraja son los demás valores, que se reparten al azar
        entre sus vecinos. Se repite muchas veces y el p es, como en el módulo 3, la fracción de
        repartos tan extremos como el observado. El capítulo usa {ent(m8["nsim"])} réplicas, una
        decisión que el módulo 10 justifica, y el p <strong>bilateral</strong> por rangos: la
        fracción de repartos que se alejan del centro tanto como el observado, por cualquiera de los
        dos lados. GeoDa y <code>esda</code> usan por defecto otro, el p <em>plegado</em>, que solo
        mira la cola del lado en que cayó el dato y por eso vale la mitad. Es un test de una cola en
        la dirección que eligió el propio dato, y el módulo 10 mide lo que eso cuesta.</p>

      <div class="note">
        <p style="margin-bottom:0;"><strong>Un argumento que nadie mira.</strong>
          <code>localmoran_perm</code> tiene <code>no_repeat_in_row = FALSE</code> por defecto: al
          sacar los vecinos al azar de cada unidad, <em>puede repetir valores</em>. GeoDa y
          <code>esda</code> no repiten. La diferencia no toca a los \(I_i\) —no cambian ni en un
          bit— pero sí al p: con el valor por defecto, los p de <code>spdep</code> salían
          sistemáticamente mayores que los de <code>esda</code>, y no por azar. El capítulo fija
          <code>no_repeat_in_row = TRUE</code> en todas sus llamadas. Quien reproduzca estas cifras
          con el valor por defecto verá p algo mayores, y ya sabe por qué.</p>
      </div>

      <p>El simulador pone los {ent(C1["n"])} \(I_i\) uno junto a otro, de mayor a menor. Mira qué
        color tienen las barras más altas y dónde caen las de color, y busca la que el módulo 4
        dejó pendiente: el barrio casi medio rodeado de vecinos altos. La lectura da, para el barrio
        elegido, su \(I_i\), su p bilateral por permutación, su z —la distancia de \(I_i\) a la
        media de sus repartos, en desviaciones típicas— y el p analítico, el que saldría de suponer
        que \(I_i\) se reparte como una normal.</p>

{sim("cap7-local", "Los 49 I locales de Columbus",
     "Una barra por barrio, ordenadas de mayor a menor, y una línea en su media, que es el I de "
     "Moran. El color es el del mapa LISA del módulo 9: rojo (alto-alto) o azul (bajo-bajo) si el "
     "barrio es significativo al 5 % —en Columbus ningún atípico llega—, gris si no. Pulsa una "
     "barra —o recórrelas con los botones— para ver el barrio en el mapa.",
     alto=300, aria="Los 49 I locales de Moran de Columbus ordenados de mayor a menor, coloreados "
     "por su categoría LISA, con su media")}
{mapa_html("cap7-local-mapa", "El barrio elegido, sobre su categoría LISA")}
      <p>Baja por las barras hasta la {ent(_RANK24)}.ª, ya por debajo de la línea de la media: el
        POLYID {ent(C8["polyid"][_IDX24])}, con un \(I_i\) de solo {n(C8["Ii"][_IDX24], 5)}, tiene el p
        más pequeño de todo el mapa, {pfmt(C8["p_min"])}. Es el barrio del módulo 4: un valor casi en
        la media rodeado de vecinos altos. Su \(I_i\) es pequeño porque su propio \(z_i\) lo es, pero
        con la permutación condicional ese mismo \(z_i\) pequeño multiplica a todos los repartos, y
        la distribución de referencia es igual de estrecha: lo que el p mide es lo rara que es su
        vecindad, no el tamaño de su \(I_i\). <strong>Un \(I_i\) grande no es un \(I_i\)
        significativo</strong>, y al revés.</p>

      <p>Al 5 %, {firma(ent(C8["significativos"]))} de los {ent(C1["n"])} barrios son significativos,
        y el p más pequeño posible con estas réplicas es {cient(C8["suelo"])}, dos entre el número
        de réplicas más uno, porque el bilateral cuenta las dos colas. Cada uno de esos p parece el
        de un test aislado, y no lo es: son {ent(C1["n"])} tests a la vez, así que alguno saldrá
        significativo por azar aunque no haya nada, y los \(I_i\) de dos vecinos comparten valores,
        así que sus tests no son independientes. El módulo 10 lo trata como el problema que es. En
        los municipios son
        {firma(ent(M8["significativos"]))}, y los cinco mayores \(I_i\) salen todos de la Amazonía y
        la Orinoquía:</p>

{tabla(["Municipio", "Departamento", "Deserción (%)", "I local", "p"],
       "".join(fila(t["municipio"], t["departamento"], n(t["desercion"], 2), n(t["Ii"], 5),
                    pfmt(t["p"])) for t in _TOP),
       "Los cinco mayores I locales de la deserción municipal, todos alto-alto")}
      <p>Y con los municipios reaparece la discrepancia de las islas desde el otro lado. La suma de
        los \(I_i\) entre \(S_0\) no da el I de <code>spdep</code>, {n(M8["I"], 6)}: da
        {firma(n(M8["suma_Ii_sobre_S0"], 6))}, que es exactamente el I que calcula
        <code>esda</code>. Los \(I_i\) se calculan con \(n\) igual a todas las unidades y el I global
        de <code>spdep</code> con \(n\) igual a las que tienen vecinos, y el cociente entre los dos
        es {n(M8["factor_islas"], 6)}, la razón entre {ent(M3["aleatorizacion"]["n"])} y
        {ent(M3["aleatorizacion"]["n_con_vecinos"])}. El módulo 9 la declara con su nombre.</p>

{tabs("Los I locales y su permutación condicional", bloque(R8, **S8R), bloque(PY8, **S8P))}
      <p><code>localmoran</code> da los \(I_i\) con su p analítico; <code>localmoran_perm</code>, los
        mismos \(I_i\) con los p de la permutación condicional, y la semilla va en
        <code>iseed</code> porque la función reparte el trabajo y una semilla global no alcanzaría a
        todas las réplicas. En Python aparece otro convenio: <code>esda</code> divide cada \(I_i\) por
        la varianza <em>muestral</em> y <code>spdep</code> por la poblacional, así que las sumas
        difieren en el factor \(n/(n-1)\). La de <code>esda</code> es exactamente el numerador que
        el bloque del módulo 2 calcula con el CRIME tipificado, {n(C2["z_Wz"], 6)}. La última línea de
        R cuenta los significativos con el p plegado: {ent(T10C["plegado_nsim"]["sin_corregir"])}
        frente a {ent(C8["significativos"])}.</p>

      <p>Queda una pregunta que la barra de colores ya ha contestado sin decirlo: qué significa
        pintar un barrio de rojo. El módulo 9 la hace en voz alta.</p>
""" + CIERRE

_L9C, _L9M = m9["columbus"], m9["municipios"]
_ISL = _L9M["islas"]
_POL = C8["polyid"]
# Con el p bilateral, Columbus se queda sin atípicos significativos. El
# módulo 9 usa el alto-bajo de menor p —el POLYID 17— para enseñar que «alto»
# es un signo: su valor es casi medio, no llega al 5 %, y un signo lo pone en
# su cuadrante. Se busca; no se apunta por posición.
_AB = [i for i in range(len(_POL)) if C8["cuadrante"][i] == "High-Low"]
_I17 = min(_AB, key=lambda i: C8["p_rangos"][i])
if not (abs(C4["puntos"]["z"][_I17]) < 0.3 and C8["p_rangos"][_I17] >= m9["alfa"]):
    sys.exit("PARADO: el alto-bajo de menor p de Columbus ya no es casi medio y no significativo")
if _L9C["atipicos_polyid"]:
    sys.exit("PARADO: Columbus vuelve a tener atípicos significativos; reescribe el módulo 9")
_DM = DISC["moran_islas"]


def _dep(lista):
    return ", ".join(f"{d['departamento']} ({ent(d['n'])})" for d in lista[:-1]) + \
        f" y {lista[-1]['departamento']} ({ent(lista[-1]['n'])})"


MOD9 = cabecera(
    9, TITULOS[8][0], INGLES[8],
    "Leer un mapa de conglomerados LISA: qué dice cada color, qué no dice, y qué hacer con las "
    "unidades que no tienen vecinos.") + rf"""
      <p>El mapa de conglomerados junta las dos cosas que el módulo 8 calculó para cada unidad: si
        su \(I_i\) es significativo y en qué cuadrante del diagrama de Moran cae. Salen cinco
        categorías, siempre con los mismos colores —los de GeoDa y de toda la literatura, y por eso
        viajan desde R con el dato y no los elige el navegador—: <strong>no significativo</strong>
        en gris, <strong>alto-alto</strong> en rojo, <strong>bajo-bajo</strong> en azul,
        <strong>alto-bajo</strong> en rosa y <strong>bajo-alto</strong> en celeste.</p>

{mapa_html("cap7-columbus-lisa", "Columbus: los conglomerados LISA de CRIME, sin corregir")}
      <p class="pie-figura">El p bilateral por rangos con {ent(m9["nsim"])} réplicas, al 5 %, sin
        corrección por multiplicidad. {ent(_L9C["conteo"][1])} barrios alto-alto,
        {ent(_L9C["conteo"][2])} bajo-bajo, ningún atípico y {ent(_L9C["conteo"][0])} no
        significativos. El mapa que GeoDa dibuja por defecto usa el p plegado y pintaría
        {ent(T10C["plegado_nsim"]["sin_corregir"])} barrios en vez de {ent(C8["significativos"])}: el
        módulo 10 explica de dónde salen los de más.</p>

      <h3>Lo que dice un color, y lo que no</h3>

      <p>Un barrio rojo dice: <em>este barrio y sus vecinos forman, juntos, una configuración
        alto-alto que el azar rara vez produce</em>. Tres lecturas habituales van más allá de eso, y
        las tres son falsas.</p>

      <ol>
        <li><strong>«La zona roja es un conglomerado».</strong> El color marca el
          <em>centro</em> de una vecindad significativa, no la vecindad. Sus vecinos forman parte del
          conglomerado y pueden estar en gris, porque su propia vecindad —que es otra— no lo es. Un
          mapa LISA señala centros; no dibuja fronteras.</li>
        <li><strong>«Alto-alto quiere decir valor alto».</strong> Alto y bajo se refieren solo al
          <em>signo</em>: por encima o por debajo de la media. El POLYID {ent(_POL[_IDX24])} está en
          rojo con un valor tipificado de {n(C4["puntos"]["z"][_IDX24], 4)}, casi en la media: lo que
          es extremo es su vecindad. Y lo mismo vale al revés: el POLYID {ent(_POL[_I17])} cae en el
          cuadrante alto-bajo con un valor tipificado de {n(C4["puntos"]["z"][_I17], 4)}, un barrio
          corriente. Aquí no llega al 5 % (p = {gx(C8["p_rangos"][_I17])}), pero si llegara el mapa
          lo pintaría de rosa, «alto entre bajos», y poco más de una décima menos lo habría dejado en bajo-bajo.
          Con un valor casi medio, el cuadrante lo decide un signo.</li>
        <li><strong>«Cada color es un test independiente».</strong> Dos barrios vecinos comparten
          vecinos, así que sus tests miran casi los mismos datos. Son {ent(C1["n"])} tests, cada uno
          al 5 %, y no independientes: el módulo 10 va de lo que eso hace con el mapa.</li>
      </ol>

      <h3>El mapa de los municipios</h3>

      <p>Con más de mil unidades el mapa LISA se lee de otra manera: lo que importa no es un color
        suelto sino dónde se juntan. Y aquí sí aparecen atípicos. Mira primero la deserción, y luego
        qué zonas de deserción alta acaban en rojo, cuáles no, y dónde salen los rosas y los
        celestes.</p>

{mandos_html("cap7-lisa-mapa", "La deserción y sus conglomerados",
             f"Los {ent(M1['n'])} municipios. Conmuta entre la tasa de deserción y su mapa LISA para ver "
             "qué zonas de la primera acaban en rojo o en azul en el segundo.")}
{mapa_html("cap7-municipios-m9", "Los municipios: deserción escolar o conglomerados LISA")}
      <p>Con la deserción salen {ent(_L9M["conteo"][1])} municipios alto-alto,
        {ent(_L9M["conteo"][2])} bajo-bajo, {ent(_L9M["conteo"][3])} alto-bajo y
        {ent(_L9M["conteo"][4])} bajo-alto: los atípicos que Columbus no tenía. Los alto-alto se concentran en {_dep(_L9M["alto_alto_por_departamento"])};
        los bajo-bajo, en {_dep(_L9M["bajo_bajo_por_departamento"])}. Son conteos de centros, con la
        advertencia de la primera lectura: los vecinos de esos centros no están contados.</p>

      <p>El mapa municipal es el objeto más pesado del capítulo: la geometría de los municipios no
        se puede simplificar más sin romper su topología, como midió el capítulo 6. Se carga una sola
        vez y la comparten los mapas de los módulos 4, 9, 10 y 11.</p>

      <h3>Las islas no son bajo-bajo</h3>

      <p>{_ISL["municipio"][0]} y {_ISL["municipio"][1]} no tienen vecinos. <code>spdep</code> les
        devuelve un \(I_i\) de {n(_ISL["Ii"][0], 0)}, un p que no existe y un cuadrante,
        «{_ISL["cuadrante_spdep"][0]}». Ese cuadrante es mitad medición y mitad artefacto. El primer
        «Low» es cierto: las dos tienen deserción por debajo de la media. El segundo no mide nada:
        sale de comparar un rezago que vale cero <em>porque no hay vecinos</em> con la media de los
        rezagos. Pintarlas de azul
        diría que son el centro de un conglomerado de baja deserción, y no son el centro de nada. El
        capítulo las pinta rayadas, como «sin dato o sin vecinos», junto al único municipio sin dato.
        <strong>Un rezago que vale cero porque no hay vecinos no es un cuadrante: es una
        ausencia</strong>, y es la misma decisión que el capítulo 6 pedía tomar en voz alta.</p>

      <div class="warning">
        <h3 style="margin-top:0;">Discrepancia declarada · {_DM["que"].lower()}</h3>
        <p>La misma variable, el mismo grafo y la misma fórmula, y dos números:
          <code>spdep</code> da <strong>{n(_DM["valor_r"], 6)}</strong> y <code>esda</code>
          <strong>{n(M8["I_esda_equivalente"], 6)}</strong>. {_DM["causa"]}</p>
        <p style="margin-bottom:0;">Es la discrepancia D2 del capítulo 1, que el capítulo 6 recogió al
          hablar de <code>zero.policy</code>, y la que el módulo 8 vio desde lo local. No es un
          error de ninguna de las dos bibliotecas: es una decisión sobre qué hacer con quien no tiene
          vecinos, y por eso se declara en vez de esconderse.</p>
      </div>

{tabs("Del p y el cuadrante al mapa", bloque(R9, **S9R), bloque(PY9, **S9P))}
      <p>El bloque construye las cinco categorías con dos ingredientes: el p bilateral y el cuadrante
        que <code>localmoran_perm</code> guarda en el atributo <code>quadr</code> (con tres
        versiones: por la media, por la mediana y por el pivote; el capítulo usa la media). Con los
        municipios, las islas salen con el p a <code>NA</code>, que es la señal que el mapa
        aprovecha. En Python, el I global de <code>esda</code> reproduce la discrepancia de la
        caja.</p>

      <p>El mapa de este módulo es el que sale sin corregir:
        {ent(C8["significativos"])} barrios y {ent(M8["significativos"])} municipios en color. El
        módulo 10 pregunta cuántos de ellos lo merecen.</p>
""" + CIERRE

_SUC, _SUM = m10["suelo"]["columbus"], m10["suelo"]["municipios"]
_BH = m10["columbus"]["bh"]
# La tasa nula en porcentaje, y los extremos de la tabla municipal: la prosa
# los cita, y se calculan aquí para no fijar a mano qué fila los da.
_TN = m10["tasa_nula"]
_TN_PLEG, _TN_BIL, _TN_ET = _TN["plegado"] * 100, _TN["bilateral"] * 100, _TN["error_tipico"] * 100
_RANGO_SIN = (min(r["sin_corregir"] for r in T10M.values()), max(r["sin_corregir"] for r in T10M.values()))
_RANGO_BON = (min(r["bonferroni"] for r in T10M.values()), max(r["bonferroni"] for r in T10M.values()))
if not (_TN["plegado"] > 1.6 * m10["alfa"] and abs(_TN["bilateral"] - m10["alfa"]) < 3 * _TN["error_tipico"]):
    sys.exit("PARADO: la tasa nula ya no dice «el plegado marca el doble, el bilateral el 5 %»")
if not (T10M["bilateral_999"]["bonferroni"] == T10M["plegado_999"]["bonferroni"] == 0
        and T10M["analitico"]["bonferroni"] > 0 and T10M["normal_permutado_999"]["bonferroni"] > 0):
    sys.exit("PARADO: las filas de 999 réplicas ya no enseñan el suelo como dice el módulo 10")
_po, _um = _BH["p_ordenados"], _BH["umbrales"]
if not (all(_po[i] <= _um[i] for i in range(_BH["k"])) and all(_po[i] > _um[i] for i in range(_BH["k"], len(_po)))):
    sys.exit("PARADO: los k primeros p ya no son exactamente los que quedan bajo la línea de FDR")
if m10["columbus"]["conteo_bonferroni"][2] or any(m10[t]["conteo_bonferroni"][k] for t in ("columbus", "municipios") for k in (3, 4)):
    sys.exit("PARADO: Bonferroni deja bajo-bajo en Columbus o algún atípico, y el módulo 10 dice que no")
if m10["suelo"]["bonferroni_mun_en_suelo"] != m10["suelo"]["bonferroni_mun"]:
    sys.exit("PARADO: no todos los municipios que pasan Bonferroni están en el suelo")
_FILAS_P = (("analitico", "Analítico", "<code>localmoran</code>"),
            ("normal_permutado_999", "Normal con los momentos de la permutación", "999"),
            ("normal_permutado_nsim", "Normal con los momentos de la permutación", ent(m10["nsim"])),
            ("bilateral_999", "Rangos, bilateral", "999"),
            ("bilateral_nsim", "Rangos, bilateral", ent(m10["nsim"])),
            ("plegado_999", "Rangos, plegado (GeoDa y <code>esda</code>)", "999"),
            ("plegado_nsim", "Rangos, plegado (GeoDa y <code>esda</code>)", ent(m10["nsim"])))


def _tabla_p(t, titulo):
    return tabla(["p usado", "Réplicas", "Sin corregir", "Bonferroni", "Holm", "FDR"],
                 "".join(fila(nombre, rep, ent(t[k]["sin_corregir"]), ent(t[k]["bonferroni"]),
                              ent(t[k]["holm"]), ent(t[k]["fdr"]))
                         for k, nombre, rep in _FILAS_P),
                 titulo)


_DP = DISC["p_permutacion"]

MOD10 = cabecera(
    10, TITULOS[9][0], INGLES[9],
    "Ver por qué el mapa LISA por defecto exagera, corregirlo con Bonferroni y con FDR, y saber "
    "qué p se está corrigiendo y con cuántas réplicas se calculó.") + rf"""
      <p>Cada unidad en color del módulo 9 es el resultado de un test al 5 %. En Columbus son
        {ent(_SUC["n"])} tests y en los municipios {ent(_SUM["n"])}, porque las dos islas no tienen
        test. Un test al 5 % declara significativas, cuando no hay nada, cinco de cada cien
        unidades: un mapa sin ninguna autocorrelación seguiría saliendo con una de cada veinte
        pintada de color. Eso con el p bilateral del capítulo; con el plegado que GeoDa usa por
        defecto es peor, y la última sección lo mide. El mapa LISA de GeoDa pinta esos falsos
        positivos con el mismo color que los reales. <code>spdep</code>, en cambio, corrige por
        defecto cuando construye las categorías con <code>hotspot()</code>, con FDR y un corte de
        0.005. Esa es la trampa de la multiplicidad, y es la parte del análisis local que más fácil
        sale mal.</p>

      <h3>Dos formas de corregir</h3>

{F_BH}
      <ul>
        <li><strong>Bonferroni</strong> compara cada p con \(\alpha/n\): en Columbus,
          {firma(gx(_SUC["umbral_bonferroni"]))}; en los municipios,
          {firma(cient(_SUM["umbral_bonferroni"], 3))}. Controla la probabilidad de declarar
          <em>algún</em> falso positivo en todo el mapa. Es muy exigente, y aquí más todavía, porque
          supone el peor caso y los tests de LISA no son independientes.</li>
        <li><strong>FDR</strong>, la tasa de falsos descubrimientos (Benjamini y Hochberg, 1995),
          ordena los p de menor a mayor, busca el mayor \(k\) con \(p_{{(k)}} \le k\,\alpha/n\) y
          declara significativos los \(k\) primeros, aunque alguno de ellos quede por encima de su
          propio umbral: se busca desde arriba, no desde abajo. No controla la probabilidad de
          equivocarse alguna vez, sino la <em>proporción</em> esperada de falsos entre los que
          declara.</li>
        <li><strong>Holm</strong>, que aparece en las tablas de más abajo, es Bonferroni por pasos:
          compara el menor p con \(\alpha/n\), el siguiente con \(\alpha/(n-1)\), y así hasta el
          primero que no pasa. Controla lo mismo que Bonferroni y nunca declara menos.</li>
      </ul>

{sim("cap7-bh", "Benjamini-Hochberg, paso a paso",
     f"Los {ent(_SUC['n'])} p bilaterales de Columbus, con {ent(m10['nsim'])} réplicas, ordenados "
     "de menor a mayor (eje vertical en escala logarítmica). La línea creciente es el umbral de "
     "FDR, k·α/n —una recta, que la escala logarítmica dobla—; la horizontal, el de Bonferroni, "
     "α/n. En naranja, los p que entran con FDR; en gris, los que no. Pulsa un punto para ver su "
     "comparación.",
     alto=300, aria="Los p de los 49 I locales de Columbus ordenados, con el umbral de "
     "Benjamini-Hochberg y el de Bonferroni")}
      <p>Los {ent(_BH["k"])} primeros p quedan bajo la línea de FDR y el siguiente,
        {n(_BH["p_ordenados"][_BH["k"]], 5)}, ya no: su umbral es {n(_BH["umbrales"][_BH["k"]], 5)}.
        Bonferroni, la horizontal, solo deja pasar {ent(T10C["bilateral_nsim"]["bonferroni"])}.
        Así que de los {ent(T10C["bilateral_nsim"]["sin_corregir"])} barrios significativos sin
        corregir quedan {ent(T10C["bilateral_nsim"]["fdr"])} con FDR y
        {ent(T10C["bilateral_nsim"]["bonferroni"])} con Bonferroni.</p>

      <h3>El mapa, corregido</h3>

{mandos_html("cap7-multiplicidad", "El mapa LISA con y sin corrección",
             "Elige el tablero y la corrección. El mapa se repinta con las mismas cinco categorías "
             "y la lectura cuenta cuántas unidades quedan en cada una.")}
{mapa_html("cap7-multiplicidad-mapa", "Los conglomerados LISA con la corrección elegida")}
      <p>En Columbus, Bonferroni deja {ent(m10["columbus"]["conteo_bonferroni"][1])} alto-alto y
        ningún bajo-bajo; FDR, {ent(m10["columbus"]["conteo_fdr"][1])} alto-alto y
        {ent(m10["columbus"]["conteo_fdr"][2])} bajo-bajo. En los municipios, de
        {ent(T10M["bilateral_nsim"]["sin_corregir"])} quedan {ent(T10M["bilateral_nsim"]["fdr"])} con FDR
        y {ent(T10M["bilateral_nsim"]["bonferroni"])} con Bonferroni
        ({ent(m10["municipios"]["conteo_bonferroni"][1])} alto-alto y
        {ent(m10["municipios"]["conteo_bonferroni"][2])} bajo-bajo). Con Bonferroni no queda ningún
        atípico en ninguno de los dos tableros. Y esos {ent(m10["suelo"]["bonferroni_mun"])}
        municipios están todos en el suelo: ninguna de sus {ent(m10["nsim"])} réplicas fue tan
        extrema como el dato. Ese número es en parte un sorteo de Monte Carlo: un municipio cuyo p
        verdadero ronde el suelo puede sacar, con otra semilla, una réplica tan extrema y caerse del
        mapa, o entrar otro. Cuál de los tres mapas publicar es una decisión, no
        un cálculo: el de Bonferroni casi no se equivoca y casi no ve; el de FDR acepta algunos
        falsos a cambio de ver más; el que no corrige no dice cuántos de sus colores son
        ruido.</p>

      <h3>El suelo del p, otra vez, y por qué el capítulo usa {ent(m10["nsim"])} réplicas</h3>

      <p>El módulo 3 avisó de que un p por permutación tiene un suelo. El bilateral cuenta las dos
        colas, así que el suyo es \(2/(\text{{nsim}}+1)\). Con las 999 réplicas que usan GeoDa y
        <code>esda</code> —<code>spdep</code> trae 499—, el mínimo es {gx(m10["suelo"]["p_min_999"])},
        y Bonferroni pide p por debajo de {gx(_SUC["umbral_bonferroni"])} en Columbus y de
        {cient(_SUM["umbral_bonferroni"], 4)} en los municipios: <strong>ningún barrio ni municipio
        puede pasar</strong>. No porque no haya conglomerados, sino porque el procedimiento no puede
        verlos. Como Bonferroni pide «menor que», hace falta \(\text{{nsim}} + 1 > 2n/\alpha\): al
        menos {ent(_SUC["nsim_minimo"])} réplicas en Columbus y {firma(ent(_SUM["nsim_minimo"]))} en
        los municipios. Con una menos, el suelo <em>iguala</em> al umbral, y no basta. Por eso el
        capítulo usa {ent(m10["nsim"])}, cuyo suelo es {cient(m10["suelo"]["p_min_nsim"])}.</p>

      <h3>Qué p se está corrigiendo</h3>

      <p>Falta una pregunta previa a toda corrección. <code>localmoran_perm</code> devuelve
        <em>tres</em> p por unidad, y ninguno es el analítico: <code>Pr(z != E(Ii))</code> es una
        aproximación normal con la media y la desviación de las permutaciones;
        <code>Pr(z != E(Ii)) Sim</code>, el rango bilateral, el que usa este capítulo, y
        <code>Pr(folded) Sim</code>, el rango plegado, el de GeoDa y <code>esda</code>: la mitad del
        bilateral, porque solo mira la cola del lado en que cayó el dato. El analítico de verdad es
        el de <code>localmoran</code>.</p>

      <p>Esa mitad tiene un precio, y se puede medir. El último trozo del bloque de abajo reparte el
        CRIME al azar sobre Columbus {ent(m10["tasa_nula"]["mapas"])} veces —la hipótesis nula hecha
        realidad— y cuenta qué fracción de barrios sale «significativa» al 5 %. Con el p bilateral,
        {firma(pct(_TN_BIL, 2))}; con el plegado, {firma(pct(_TN_PLEG, 2))}, con un error típico de
        {n(_TN_ET, 2)} puntos. <strong>El plegado al 5 % es un test al 10 %</strong>: marca el doble
        de falsos positivos de los que promete, y Bonferroni o FDR aplicados sobre él controlan el
        doble de lo que dicen. Por eso este capítulo pinta sus mapas con el bilateral. Sobre el
        mismo dato, los distintos p dan mapas distintos:</p>

{_tabla_p(T10M, "Los municipios: unidades significativas al 5 % según el p y la corrección")}
      <p>Sin corregir, de {ent(_RANGO_SIN[0])} a {ent(_RANGO_SIN[1])} municipios; con Bonferroni, de
        {ent(_RANGO_BON[0])} a {ent(_RANGO_BON[1])}. Las filas de 999 réplicas enseñan el suelo: ni
        el bilateral ni el plegado dejan pasar a nadie con Bonferroni, y los dos p normales sí,
        porque no tienen suelo, a cambio de suponer que \(I_i\) se reparte como una normal justo en
        la cola, donde nadie lo ha comprobado. Entre 999 y {ent(m10["nsim"])} réplicas el cuadrante
        de cada unidad es el mismo —no depende de las réplicas—, pero el conjunto de significativos
        al 5 % cambia en {ent(m10["municipios"]["significativos_cambian"])}: la resolución del p
        también es parte del método. Sobre Columbus:</p>

{_tabla_p(T10C, "Columbus: barrios significativos al 5 % según el p y la corrección")}
      <p><strong>La corrección de multiplicidad empieza por saber qué p se está corrigiendo y con
        cuántas réplicas se calculó.</strong> Un mapa LISA publicado sin decir las dos cosas no se
        puede reproducir, y con otra elección razonable podría tener el doble o la mitad de
        colores.</p>

      <div class="note">
        <h4 style="margin-top:0;">Discrepancia declarada · {_DP["que"].lower()}</h4>
        <p style="margin-bottom:0;">{_DP["causa"]}</p>
      </div>

{tabs("Bonferroni, FDR y el suelo", bloque(R10, **S10R), bloque(PY10, **S10P))}
      <p>En R la corrección es una línea: <code>p.adjust</code> con <code>"bonferroni"</code>,
        <code>"holm"</code> o <code>"fdr"</code>, aplicada al vector de p que se haya elegido —y
        <code>hotspot()</code> de <code>spdep</code> la hace al construir las categorías—. Ojo: la
        función no tiene un argumento para corregir dentro de <code>localmoran_perm</code>; se corrige
        después. El final del bloque es la medición de la tasa nula: doscientos mapas al azar, y en
        cada uno la fracción de barrios que cada p declara significativos. La pestaña de Python
        escribe Benjamini-Hochberg a mano sobre los p bilaterales de <code>spdep</code> que guarda el
        CSV del capítulo, y da el mismo {ent(_BH["k"])}.</p>

      <p>Todo lo anterior mide <em>parecido</em>: si una unidad se parece a sus vecinos. Hay otra
        pregunta, que suena igual y no lo es: si una zona tiene, en conjunto, valores altos.</p>
""" + CIERRE

_G11C, _G11M = m11["columbus"], m11["municipios"]
_CRC = {f["lisa"]: f for f in _G11C["cruce"]}
_CRM = {f["lisa"]: f for f in _G11M["cruce"]}
_AUT = _G11C["autoinclusion"]
# Lo que el módulo 11 afirma, comprobado: con la unidad fija Gi* copia a Gi;
# con ella dentro, el bajo-alto más extremo deja de ser caliente.
if not (_AUT["cor_fijo_Gi"] > 0.99 and _AUT["p_Gi"] < 0.10 and _AUT["p_libre"] > 0.30
        and abs(_AUT["p_fijo"] - _AUT["p_Gi"]) < 0.01 and _AUT["polyid"] == _POL[_ORD[-1]]):
    sys.exit("PARADO: la autoinclusión de Gi* ya no enseña lo que cuenta el módulo 11")
if not (_CRC["Alto-alto"]["caliente"] == _L9C["conteo"][1] and _CRC["Bajo-bajo"]["frio"] == _L9C["conteo"][2]
        and _CRM["Alto-alto"]["caliente"] == _L9M["conteo"][1] and _CRM["Bajo-bajo"]["frio"] == _L9M["conteo"][2]
        and _CRM["Alto-bajo"]["caliente"] == 0 and _CRM["Bajo-alto"]["frio"] == 0):
    sys.exit("PARADO: el cruce LISA × Gi* ya no es el que describe el módulo 11")
if _TOP[0]["municipio"] != _G11M["municipio_z_max"]:
    sys.exit("PARADO: el municipio de mayor z de Gi* ya no es el de mayor I local")

MOD11 = cabecera(
    11, TITULOS[10][0], INGLES[10],
    "Distinguir lo que mide Gi* —intensidad— de lo que mide LISA —similitud—, y leer un mapa de "
    "puntos calientes sabiendo qué no puede ver.") + rf"""
      <p>LISA pregunta si una unidad se parece a sus vecinos. Getis y Ord (1992) hicieron otra
        pregunta: si la <em>zona</em> alrededor de una unidad tiene, en conjunto, valores altos o
        bajos. Su estadístico suma los valores de la vecindad y los compara con el total:</p>

{F_GI}
      <p>\(G_i^*\) incluye a la propia unidad en su vecindad; \(G_i\), no. Lo que devuelve
        <code>localG</code> de <code>spdep</code> no es el cociente sino su versión tipificada, una z:
        muy positiva es un <strong>punto caliente</strong> —una zona de valores altos—, y muy
        negativa, un <strong>punto frío</strong>. Los mapas de este módulo lo pintan en siete
        categorías: frío o caliente al 99, al 95 y al 90 %, y no significativo.</p>

      <p>El nivel sale de una permutación, como en LISA, y aquí hay una decisión que tomar.
        \(G_i^*\) incluye a la unidad, así que la unidad tiene que entrar en el reparto. Por defecto
        <code>localG_perm</code> la deja fija (<code>fix_i_in_Gstar_permutations = TRUE</code>), y
        entonces el test de \(G_i^*\) es, en la práctica, el de \(G_i\): en Columbus, los p de los
        dos se parecen con una correlación de {n(_AUT["cor_fijo_Gi"], 4)}. Este capítulo la mete en
        la permutación, que es además lo que supone la z de Getis y Ord. Con el p bilateral, como en
        todo el capítulo, y el signo de la z para decir si es caliente o frío.</p>

      <h3>La rejilla del artículo</h3>

      <p>Getis y Ord presentaron el estadístico sobre una rejilla de {ent(GO["lado"])} × {ent(GO["lado"])}
        celdas, {ent(GO["n"])} en total, con un umbral de distancia de {ent(GO["umbral"])}: cada celda
        tiene de media {n(GO["vecinos_medio"], 2)} vecinas.</p>

{par_mapas("cap7-getisord-valor", "La rejilla de Getis y Ord (1992): el dato",
           "cap7-getisord-g", "La misma rejilla: Gi* con umbral 30")}
      <p class="pie-figura">El primer mapa es el dato, en siete clases con el mismo número de
        celdas. El segundo es la z de \(G_i^*\), cortada en ±1.645, ±1.96 y ±2.576: sus siete clases
        son los siete niveles de arriba, de frío al 99 % en azul a caliente al 99 % en rojo, leídos
        en la z analítica. Es más suave que el primero, porque cada celda resume su vecindad. Por
        permutación, al 5 %, la rejilla tiene {ent(GO["calientes_95"])} celdas calientes y
        {ent(GO["frios_95"])} frías.</p>

      <p>La celda {ent(GO["celda"])}, en ({ent(GO["x"])}, {ent(GO["y"])}) y con valor {ent(GO["valor"])},
        es el ejemplo de la ayuda de <code>spdep</code>: su \(G_i\) da {firma(gx(GO["G"]))} y su
        \(G_i^*\), {firma(n(GO["G_estrella"], 4))}. Con \(n - 1\) en lugar de \(n\) en la varianza sale
        {n(GO["G_estrella_n1"], 4)}, que es la cifra que Getis y Ord (1996, p. 267) publican según esa
        misma ayuda: el ancla del módulo, con su procedencia en dos pasos. Su p bilateral por
        permutación es {n(GO["G_estrella_p"], 5)}: la celda está en una zona algo alta, pero no lo bastante para que
        el azar no la explique.</p>

      <p>Y la respuesta depende de qué se llame zona. Con el umbral de distancia creciendo, la misma
        celda da:</p>

{tabla(["Umbral", "Vecinas de media", "G (z)", "G* (z)"],
       "".join(fila(ent(b["d"]), n(b["vecinos_medio"], 2), n(b["G"], 4), n(b["G_estrella"], 4))
               for b in GO["barrido"]),
       "La celda 120 de la rejilla con cinco umbrales de distancia")}
      <p>La z sube hasta el umbral de 90 y vuelve a bajar: con vecindades pequeñas la zona es apenas
        la celda y sus contiguas; con vecindades enormes la zona es media rejilla y se parece al
        total. <strong>Un punto caliente lo es a una escala</strong>, y la escala la elige quien fija
        el umbral, exactamente como W en el módulo 7. Y las dos versiones, \(G_i\) y \(G_i^*\), no se
        separan en esta rejilla más de {n(GO["dif_max_G_Gestrella"], 4)} en ninguna celda: con un
        umbral de 30 cada celda tiene muchas vecinas, y su propio valor pesa poco en la suma. Donde
        una unidad tiene pocos vecinos y un valor muy distinto del de ellos, la diferencia es justo
        la lección, como se ve abajo.</p>

      <h3>Intensidad frente a similitud</h3>

      <p>La diferencia de fondo con LISA está en la definición. LISA multiplica la desviación de la
        unidad por la de sus vecinos: mide <strong>similitud</strong>, si la unidad se parece a lo que
        la rodea. \(G_i^*\) suma la vecindad entera: mide <strong>intensidad</strong>, si la zona es
        alta o baja en conjunto. Casi siempre coinciden, y donde no coinciden está la lección.</p>

{mandos_html("cap7-gistar", "LISA y Gi*, lado a lado",
             "El mismo tablero dos veces: el primer mapa, los conglomerados LISA; el segundo, los "
             "puntos calientes y fríos de Gi*. Cambia de tablero; la lectura cruza las dos "
             "clasificaciones.")}
{par_mapas("cap7-lado-lisa", "Conglomerados LISA",
           "cap7-lado-gi", "Puntos calientes y fríos de Gi*")}
      <p>En Columbus los {ent(_CRC["Alto-alto"]["caliente"])} alto-alto son calientes y los
        {ent(_CRC["Bajo-bajo"]["frio"])} bajo-bajo, fríos: ahí las dos medidas dicen lo mismo. Columbus
        no tiene atípicos significativos, pero el bajo-alto más extremo, el POLYID
        {ent(_AUT["polyid"])} —el barrio de menos delitos, rodeado de vecinos por encima de la
        media—, enseña la diferencia entre las dos versiones. Con \(G_i\), que no lo incluye, su
        vecindad es caliente: p = {gx(_AUT["p_Gi"])}. Con \(G_i^*\) y el barrio dentro de la
        permutación, su propio valor bajo cuenta, y el p sube a {firma(gx(_AUT["p_libre"]))}: ya no
        es una zona caliente. Con la opción por defecto, que lo deja fijo, saldría
        {gx(_AUT["p_fijo"])}, el de \(G_i\). La decisión sobre la permutación decide qué pregunta
        contesta \(G_i^*\). La mayor z de Columbus es {n(_G11C["z_max"], 4)}, en el POLYID
        {ent(_G11C["polyid_z_max"])}.</p>

      <p>En los municipios sí hay atípicos, y el cruce enseña lo que \(G_i^*\) hace con ellos. Los
        {ent(_CRM["Alto-alto"]["caliente"])} alto-alto salen calientes y los
        {ent(_CRM["Bajo-bajo"]["frio"])} bajo-bajo, fríos. De los {ent(_L9M["conteo"][3])} alto-bajo,
        {ent(_CRM["Alto-bajo"]["frio"])} salen <strong>fríos</strong>, y de los
        {ent(_L9M["conteo"][4])} bajo-alto, {ent(_CRM["Bajo-alto"]["caliente"])} salen
        <strong>calientes</strong>, contando hasta el 90 %; el resto no llega. Salen pintados del
        color de su vecindad, el contrario al suyo: incluso con su propio valor dentro de la suma,
        pesan más los vecinos. Y \(G_i^*\) marca además, alrededor de municipios que LISA no marca,
        {ent(_CRM["No significativo"]["caliente_95"])} zonas calientes y
        {ent(_CRM["No significativo"]["frio_95"])} frías al 5 %, el mismo nivel que LISA: unidades que
        no se parecen lo bastante a sus vecinos para LISA pero viven en una zona alta o baja. (Con
        el 90 % serían {ent(_CRM["No significativo"]["caliente"])} y
        {ent(_CRM["No significativo"]["frio"])}, pero ese nivel es más laxo que el de LISA y no se
        compara con él.) La z más alta del país es {n(_G11M["z_max"], 4)}, en
        {_G11M["municipio_z_max"]} ({_G11M["departamento_z_max"]}). Quien lea solo el mapa de puntos
        calientes verá una zona caliente donde hay un municipio de baja deserción, porque ese mapa
        no tiene una categoría para «distinto de lo que le rodea».</p>

      <div class="warning">
        <h4 style="margin-top:0;">Un punto caliente de pocos estudiantes</h4>
        <p>El capítulo 3 prometió que este capítulo separaría un punto caliente real de un municipio
          con pocos datos. Con el dato que tiene el curso, no puede cumplirlo, y conviene decir por
          qué. {_G11M["municipio_z_max"]} es el punto más caliente de Gi* y el mayor \(I_i\) del
          módulo 8, y los cinco mayores I locales son municipios de la Amazonía y la Orinoquía. Si
          tienen pocos estudiantes —y el dato no lo dice—, son justo el perfil en que una tasa es más
          ruidosa. LISA y Gi* tratan la deserción
          de un municipio con pocos estudiantes exactamente igual que la de una ciudad: no saben de
          cuántos estudiantes sale cada tasa.</p>
        <p style="margin-bottom:0;">Los remedios son los del capítulo 3: un umbral de matrícula
          declarado, un intervalo por municipio o un suavizado bayesiano empírico —en
          <code>spdep</code>, <code>EBlocal</code> suaviza las tasas y <code>EBImoran.mc</code> hace
          el I de Moran de una tasa teniendo en cuenta su población (Assunção y Reis, 1999)—. Los
          tres necesitan el <strong>denominador</strong>, los estudiantes matriculados, y el dato que
          el curso descargó del MEN trae la tasa sin él. Así que este capítulo
          <strong>no puede separar aquí</strong> un punto caliente real de uno de pocos datos, y lo
          dice en vez de fingirlo. Es lo que un informe serio tiene que declarar al pie de su
          mapa.</p>
      </div>

{tabs("Gi y Gi*", bloque(R11, **S11R), bloque(PY11, **S11P))}
      <p>En R, \(G_i^*\) no tiene función propia: es <code>localG</code> con la unidad dentro de su
        vecindad, <code>include.self()</code>, y en <code>localG_perm</code> la unidad entra también en
        la permutación con <code>fix_i_in_Gstar_permutations = FALSE</code>; la última línea da el p
        del POLYID {ent(_AUT["polyid"])} así calculado. Y la pestaña de Python enseña el otro hallazgo de la
        auditoría del precálculo: con pesos estandarizados por filas, la z de \(G_i^*\) de
        <code>esda</code> 2.9 sale mal —su varianza es ocho veces la que dan las ecuaciones de Ord y
        Getis (1995) escritas a mano—. Con pesos binarios coincide con <code>spdep</code> al bit, y
        como la z de \(G_i^*\) no cambia al reescalar cada fila, calcularla con binarios no pierde
        nada.</p>

      <p>Con esto el capítulo tiene sus dos familias completas: la global, que dice si hay
        autocorrelación, y la local, que dice dónde, con sus dos preguntas distintas y sus
        trampas.</p>
""" + CIERRE

MOD12 = cabecera(
    12, TITULOS[11][0], INGLES[11],
    "Comprobar lo aprendido y practicar sobre un mapa que el capítulo no ha usado, que es donde se "
    "ve si el método viaja.") + rf"""
      <p>El capítulo ha hecho una sola pregunta —<em>¿lo cercano se parece más de lo que cabría
        esperar por azar?</em>— y ha ido aprendiendo a contestarla con cuidado: que la respuesta es
        un número y una referencia, que el número depende de la W y del estilo, que el p tiene un
        suelo, que lo local multiplica los tests, y que «parecido» e «intensidad» son dos preguntas.
        Trece preguntas para comprobarlo, sin nota: cada opción trae su explicación, así que
        equivocarse aquí vale tanto como acertar.</p>

{quiz_html("cap7-quiz", "Autoevaluación del capítulo 7",
           "Trece preguntas sobre Moran, Geary, LISA, la multiplicidad y Gi*.")}
      <p>Y cinco ejercicios guiados con su solución calculada en R. <strong>Ninguno usa Columbus ni
        los municipios</strong>: los cinco trabajan sobre los 100 condados de <code>nc</code>, el
        mapa de Carolina del Norte, con la tasa de muerte súbita del lactante de 1979. Un hallazgo
        que solo aparece donde te lo enseñaron es una anécdota; encontrarlo en otro mapa es lo que lo
        convierte en método.</p>
{EJ}
      <p>Los cinco repiten el capítulo en orden: el índice pieza a pieza, la recta del diagrama, un
        extremo contra los dos índices, el mapa que sale por defecto y la diferencia entre parecido e
        intensidad. Y los cinco tienen una pregunta final sin cifra, que es la que de verdad
        comprueba que se entendió.</p>

      <div class="tip-box">
        <h4>Dónde sigue esto</h4>
        <p style="margin-bottom:0;">El <strong>capítulo 8</strong> da la vuelta a la pregunta. Aquí se
          ha medido la autocorrelación de una variable; allí aparece en los <em>residuos</em> de una
          regresión —el test de Moran sobre los residuos es su primer diagnóstico— y se modela con el
          proceso del módulo 1, el SAR, y con sus parientes. El ρ del retículo deja de ser un deslizador
          y pasa a estimarse. Los anteriores son
          <a href="capitulo-1-datos-espaciales.html">Datos espaciales y la primera ley de la
          geografía</a>, <a href="capitulo-2-crs-georreferenciacion.html">SIG, sistemas de referencia y
          georreferenciación</a>, <a href="capitulo-3-cartografia-maup.html">Cartografía estadística y
          el MAUP</a> —de donde viene el problema de las tasas de pocos datos—,
          <a href="capitulo-4-patrones-puntuales.html">Patrones puntuales</a>,
          <a href="capitulo-5-intensidad-nucleos.html">Intensidad por núcleos</a> y
          <a href="capitulo-6-pesos-espaciales.html">Datos de área y la matriz de pesos
          espaciales</a>, que construyó la W de la que depende todo lo de este capítulo.</p>
      </div>
""" + CIERRE

MODULOS_ESCRITOS = 12
MODULOS = (MOD1 + MOD2 + MOD3 + MOD4 + MOD5 + MOD6 + MOD7
           + MOD8 + MOD9 + MOD10 + MOD11 + MOD12)


# =====================================================================
# LOS DATOS QUE VIAJAN AL NAVEGADOR
# =====================================================================
COURSE_DATA = (
    "    const courseData = {\n      modules: [\n"
    + "".join(f"        {{ id: {i + 1}, title: {json.dumps(t, ensure_ascii=False)}, "
              f"subtitle: {json.dumps(s, ensure_ascii=False)} }},\n"
              for i, (t, s) in enumerate(TITULOS))
    + "      ]\n    };\n\n"
    + "    // Todas las cifras del capítulo, tal como salieron del precálculo.\n"
    + "    // El JavaScript no lleva ninguna escrita: las saca de aquí.\n"
    + "    const DATOS_CAP7 = " + json.dumps(D, ensure_ascii=False) + ";\n"
    + "    const SOL_CAP7 = " + json.dumps(SOL, ensure_ascii=False) + ";\n"
    + "    const D7 = DATOS_CAP7;\n"
)

# Los nombres de los 1 121 municipios con dato, EN EL ORDEN del precálculo (el
# de `cap7_municipios_lisa.csv`, que es el de los puntos del módulo 4). Sin
# ellos, pulsar un punto del diagrama municipal daría «el municipio 731».
import csv as _csv
with (SALIDAS / "cap7_municipios_lisa.csv").open(encoding="utf-8") as _f:
    _NOMBRES = [[r["municipio"], r["departamento"]] for r in _csv.DictReader(_f)]
if len(_NOMBRES) != len(M4["puntos"]["z"]):
    sys.exit(f"PARADO: {len(_NOMBRES)} nombres de municipio para {len(M4['puntos']['z'])} puntos del diagrama")

CSS_CAP7 = """
    /* ================================================================
       Capítulo 7: dos lienzos o dos mapas lado a lado (el retículo y su
       diagrama; LISA frente a Gi*). Con `auto-fit` se apilan solos cuando
       la columna no da para dos de 260 px —en el teléfono y también con el
       índice lateral abierto en una ventana estrecha, donde un media query
       por el ancho de la VENTANA se equivocaría—.
       ================================================================ */
    .cap7-par {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
      gap: 0.9rem;
      align-items: start;
    }
    .cap7-par > * { min-width: 0; }
    .cap7-par-mapas > .geomapa { margin: 0.75rem 0; }
    .cap7-reticulo { display: flex; justify-content: center; }
    .cap7-reticulo canvas { width: 100%; max-width: 300px; aspect-ratio: 1 / 1; display: block; }
    .cap7-grupo { display: flex; flex-wrap: wrap; gap: 0.35rem; align-items: center; grid-column: 1 / -1; }
    .cap7-grupo-rotulo { font-size: 0.8rem; color: #4b5563; margin-right: 0.25rem; }
"""


def _etq(texto):
    return ",\n      etiqueta: " + json.dumps(texto, ensure_ascii=False)


GEOMAPAS_JS = (
    "    // Los mapas del capítulo, UNA sola vez: la geometría municipal es lo que\n"
    "    // pesa, y la comparten los mapas de los módulos 4, 9, 10 y 11.\n"
    "    const MAPAS_CAP7 = " + json.dumps(M, ensure_ascii=False) + ";\n"
    "    const COL7 = MAPAS_CAP7['cap7-columbus'], MUN7 = MAPAS_CAP7['cap7-municipios'];\n"
    "    const NOMBRES_MUN7 = " + json.dumps(_NOMBRES, ensure_ascii=False) + ";\n"
    + r"""
    // Los índices de la GEOMETRÍA de los municipios con dato, en el orden de los
    // puntos del diagrama (el municipio sin dato no tiene punto, y sí polígono).
    const MUN7_IDX = [];
    MUN7.capas[0].valor.forEach((v, i) => { if (v != null) MUN7_IDX.push(i); });

    // El estado de los mapas que cambian. Los registros lo leen con GETTERS y no
    // reciben opciones al repintarse: así el ResizeObserver y el conmutador de
    // daltonismo, que llaman a dibuja() sin argumentos, no devuelven el mapa a
    // su capa por defecto (en el capítulo 6, girar el teléfono lo hacía).
    const E7 = { diagTab: 'col', diagSel: null, w: 'gal', localSel: null,
                 m9capa: 'desercion', multTab: 'col', multCapa: 'lisa', ladoTab: 'col' };
    const SIN_DATO7 = 'sin dato o sin vecinos';

    // La tabla de respaldo: lo que el mapa dice con color, dicho con números.
    function tablaCapa7(d, capaId) {
      const cp = d.capas.find(c => c.id === capaId) || d.capas[0];
      let filas;
      if (cp.tipo === 'categoria') {
        filas = cp.niveles.map((nv, k) => `<tr><th scope="row">${nv}</th><td>${cp.tam[k]}</td></tr>`).join('');
      } else {
        filas = cp.tam.map((t, k) => `<tr><th scope="row">${n7(cp.cortes[k], 2)} – ${n7(cp.cortes[k + 1], 2)}</th><td>${t}</td></tr>`).join('');
      }
      if (cp.n_sin_dato) filas += `<tr><th scope="row">${SIN_DATO7}</th><td>${cp.n_sin_dato}</td></tr>`;
      return `<table><caption>${cp.etiqueta}: unidades en cada clase</caption>`
        + `<thead><tr><th scope="col">Clase</th><th scope="col">Unidades</th></tr></thead>`
        + `<tbody>${filas}</tbody></table>`;
    }

    // Columbus barrio a barrio: el dato y sus dos clasificaciones locales.
    function tablaColumbus7() {
      const cr = COL7.capas[0], li = COL7.capas[1], gi = COL7.capas[4];
      const filas = COL7.polyid.map((p, i) =>
        `<tr><th scope="row">${p}</th><td>${n7(cr.valor[i], 2)}</td>`
        + `<td>${li.niveles[li.valor[i] - 1]}</td><td>${gi.niveles[gi.valor[i] - 1]}</td></tr>`).join('');
      return `<table><caption>Los 49 barrios de Columbus: CRIME, su categoría LISA sin corregir y su categoría de Gi*</caption>`
        + `<thead><tr><th scope="col">POLYID</th><th scope="col">CRIME</th><th scope="col">LISA</th>`
        + `<th scope="col">Gi*</th></tr></thead><tbody>${filas}</tbody></table>`;
    }

    GEOMAPAS['cap7-columbus-m1'] = { fuente: COL7, capa: 'crime', paleta: 'naranja',
      titulo: 'Columbus: la tasa de delitos (CRIME) de los 49 barrios',
      etiqueta: 'Los 49 barrios de Columbus coloreados por su tasa de delitos, CRIME, en cinco clases de igual número de barrios: los valores altos se agrupan.',
      tabla: () => tablaColumbus7() };
    GEOMAPAS['cap7-diagrama-mapa'] = {
      fuente: () => E7.diagTab === 'mun' ? MUN7 : COL7,
      get capa() { return E7.diagTab === 'mun' ? 'desercion' : 'crime'; },
      get resaltado() { return E7.diagSel == null ? null : (E7.diagTab === 'mun' ? MUN7_IDX[E7.diagSel] : E7.diagSel); },
      get titulo() { return E7.diagTab === 'mun' ? 'Los municipios: la unidad elegida, sobre la deserción'
                                               : 'Columbus: la unidad elegida, sobre CRIME'; },
      // VERDE y no naranja: el motor resalta la unidad en naranja, y sobre la
      // paleta naranja el resalte de la clase 4 de CRIME no se distinguía
      // (rgb 227,104,8 frente a 255,102,0; auditoría del 2026-10-20).
      paleta: 'verde', nombreSinDato: SIN_DATO7,
      tabla: d => tablaCapa7(d, E7.diagTab === 'mun' ? 'desercion' : 'crime') };
    GEOMAPAS['cap7-w-mapa'] = { fuente: MAPAS_CAP7['cap7-w'], get variante() { return E7.w; },
      etiqueta: 'Los 49 barrios de Columbus con el grafo de la vecindad elegida: cada línea une dos barrios que esa definición considera vecinos, y un punto rojo es un barrio que se queda sin ninguno.' };
    GEOMAPAS['cap7-local-mapa'] = { fuente: COL7, capa: 'lisa', get resaltado() { return E7.localSel; },
      titulo: 'Columbus: el barrio elegido, sobre su categoría LISA',
      tabla: () => tablaColumbus7() };
    GEOMAPAS['cap7-columbus-lisa'] = { fuente: COL7, capa: 'lisa', tabla: () => tablaColumbus7(),
      titulo: 'Columbus: los conglomerados LISA de CRIME, sin corregir' };
    GEOMAPAS['cap7-municipios-m9'] = { fuente: MUN7, get capa() { return E7.m9capa; }, paleta: 'naranja',
      get titulo() { return E7.m9capa === 'lisa' ? 'Los municipios: los conglomerados LISA de la deserción, sin corregir'
                                                 : 'Los municipios: la deserción escolar (MEN, 2024)'; },
      nombreSinDato: SIN_DATO7, tabla: d => tablaCapa7(d, E7.m9capa) };
    GEOMAPAS['cap7-multiplicidad-mapa'] = { fuente: () => E7.multTab === 'mun' ? MUN7 : COL7,
      get capa() { return E7.multCapa; }, nombreSinDato: SIN_DATO7, tabla: d => tablaCapa7(d, E7.multCapa),
      get titulo() { return (E7.multTab === 'mun' ? 'Los municipios' : 'Columbus') + ': conglomerados LISA '
        + ({ lisa: 'sin corregir', lisa_bonferroni: 'con Bonferroni', lisa_fdr: 'con FDR' })[E7.multCapa]; } };
    GEOMAPAS['cap7-getisord-valor'] = { fuente: MAPAS_CAP7['cap7-getisord-valor'], paleta: 'verde',
      etiqueta: 'La rejilla de 16 por 16 celdas de Getis y Ord, coloreada por el valor de cada celda en siete clases.' };
    GEOMAPAS['cap7-getisord-g'] = { fuente: MAPAS_CAP7['cap7-getisord-g'], paleta: 'frio_caliente',
      etiqueta: 'La misma rejilla coloreada por la z de Gi* con un umbral de distancia de 30, cortada en ±1.645, ±1.96 y ±2.576: siete niveles, de frío al 99 % en azul a caliente al 99 % en rojo.' };
    GEOMAPAS['cap7-lado-lisa'] = { fuente: () => E7.ladoTab === 'mun' ? MUN7 : COL7, capa: 'lisa',
      get titulo() { return (E7.ladoTab === 'mun' ? 'Los municipios' : 'Columbus') + ': conglomerados LISA, sin corregir'; },
      nombreSinDato: SIN_DATO7, tabla: d => tablaCapa7(d, 'lisa') };
    GEOMAPAS['cap7-lado-gi'] = { fuente: () => E7.ladoTab === 'mun' ? MUN7 : COL7, capa: 'gistar',
      get titulo() { return (E7.ladoTab === 'mun' ? 'Los municipios' : 'Columbus') + ': puntos calientes y fríos de Gi*'; },
      nombreSinDato: SIN_DATO7, tabla: d => tablaCapa7(d, 'gistar') };
""")


# =====================================================================
# EL PREÁMBULO DE JAVASCRIPT DEL CAPÍTULO
#
# `n7`, la paleta y las fábricas de control NO las trae la plantilla: las
# define cada capítulo (trampa 8 del §0.6: un `ReferenceError` en un
# simulador se lleva por delante a TODOS los del módulo).
# =====================================================================
JS_PREAMBULO = r"""
    const n7 = (x, d) => Number(x).toFixed(d == null ? 4 : d);
    const mil7 = x => Math.round(Number(x)).toLocaleString('es-ES').replace(/\./g, ' ');
    // Un p en la lectura: tal cual si es legible, con potencia de diez si no.
    const p7 = x => {
      const v = Number(x);
      if (!(v > 0) || v >= 1e-4) return String(+v.toPrecision(4));
      const [m, e] = v.toExponential(3).split('e');
      return `${+m}·10<sup>${+e}</sup>`;
    };

    const C7 = { rojo: '#c1272d', azul: '#2166ac', rosa: '#f4a582', celeste: '#92c5de',
                 gris: '#9ca3af', grisClaro: '#e5e5e5', naranja: '#FF6600', verde: '#1a7358',
                 tinta: '#012820', morado: '#7B3FA0', suave: 'rgba(26,115,88,0.18)' };
    const CUAD7 = { AA: C7.rojo, BB: C7.azul, AB: C7.rosa, BA: C7.celeste };
    const CUAD7_NOMBRE = { AA: 'alto-alto', BB: 'bajo-bajo', AB: 'alto-bajo', BA: 'bajo-alto' };
    const SPDEP7 = { 'High-High': 'alto-alto', 'Low-Low': 'bajo-bajo', 'High-Low': 'alto-bajo', 'Low-High': 'bajo-alto' };
    const cuad7 = (z, wz) => z >= 0 ? (wz >= 0 ? 'AA' : 'AB') : (wz >= 0 ? 'BA' : 'BB');

    function lectura7(raiz, pares) {
      const caja = raiz.querySelector('.simulador-lectura');
      if (!caja) return;
      caja.innerHTML = pares.map(p =>
        `<span class="lectura-item"><span class="lectura-etiqueta">${p[0]}</span> ` +
        `<span class="lectura-valor">${p[1]}</span></span>`).join('');
    }

    // Un GRUPO de botones, que se AÑADE a los mandos en vez de sustituirlos:
    // varios simuladores de este capítulo tienen dos botoneras (tablero y
    // corrección). Devuelve una función para marcar uno desde fuera.
    function grupo7(raiz, rotulo, ops, alPulsar, activo) {
      const cont = raiz.querySelector('.simulador-controles');
      if (!cont) return () => {};
      const g = document.createElement('div');
      g.className = 'cap7-grupo';
      g.setAttribute('role', 'group');
      g.setAttribute('aria-label', rotulo);
      const ini = Math.max(0, activo || 0);
      g.innerHTML = `<span class="cap7-grupo-rotulo">${rotulo}:</span>` + ops.map((o, i) =>
        `<button type="button" class="geomapa-boton${i === ini ? ' activo' : ''}" ` +
        `aria-pressed="${i === ini}" data-i="${i}">${o}</button>`).join('');
      const marca = i => g.querySelectorAll('.geomapa-boton').forEach(x => {
        const si = +x.dataset.i === i;
        x.classList.toggle('activo', si);
        x.setAttribute('aria-pressed', String(si));
      });
      g.addEventListener('click', e => {
        const b = e.target.closest('.geomapa-boton');
        if (!b) return;
        marca(+b.dataset.i);
        alPulsar(+b.dataset.i);
      });
      cont.appendChild(g);
      return marca;
    }

    // Botones sueltos (anterior / siguiente, otra realización), sin estado.
    function accion7(raiz, rotulo, ops, alPulsar) {
      const cont = raiz.querySelector('.simulador-controles');
      if (!cont) return;
      const g = document.createElement('div');
      g.className = 'cap7-grupo';
      g.setAttribute('role', 'group');
      g.setAttribute('aria-label', rotulo);
      g.innerHTML = ops.map((o, i) =>
        `<button type="button" class="geomapa-boton" data-i="${i}">${o}</button>`).join('');
      g.addEventListener('click', e => {
        const b = e.target.closest('.geomapa-boton');
        if (b) alPulsar(+b.dataset.i);
      });
      cont.appendChild(g);
    }

    function deslizador7(raiz, opciones, etiqueta, iniPos, alCambiar) {
      const cont = raiz.querySelector('.simulador-controles');
      if (!cont) return;
      const id = 'ctl-' + Math.random().toString(36).slice(2, 10);
      const caja = document.createElement('div');
      caja.className = 'control-slider';
      caja.style.gridColumn = '1 / -1';
      const rotulo = document.createElement('label');
      rotulo.setAttribute('for', id);
      rotulo.append(etiqueta);
      const salida = document.createElement('output');
      rotulo.appendChild(salida);
      const input = document.createElement('input');
      input.type = 'range'; input.id = id;
      input.min = 0; input.max = opciones.length - 1; input.step = 1; input.value = iniPos;
      const pinta = () => {
        const o = opciones[+input.value];
        salida.textContent = o[1];
        input.setAttribute('aria-valuetext', etiqueta + ': ' + o[1]);
      };
      input.addEventListener('input', () => { pinta(); alCambiar(+input.value); });
      caja.append(rotulo, input);
      cont.appendChild(caja);
      pinta();
    }

    // El gráfico de la casa. `animation: false` NO es estilo: con la animación,
    // Chart.js aplaza el primer trazo a un fotograma que en este montaje no
    // llega nunca, y el lienzo se queda con cero píxeles (trampa 12 del §0.6).
    function grafico7(cv, tipo, data, opciones) {
      if (!cv || typeof Chart === 'undefined') return null;
      return new Chart(cv.getContext('2d'), {
        type: tipo, data,
        options: Object.assign({
          responsive: true, maintainAspectRatio: false, animation: false,
          plugins: { legend: { labels: { filter: it => it.text !== '' } } }
        }, opciones || {})
      });
    }

    // El mapa de un módulo se repinta SIN opciones: lo que cambia lo leen sus
    // getters del estado E7 (ver los registros de GEOMAPAS).
    function repinta7(ident) {
      const g = document.querySelector(`[data-geomapa="${ident}"]`);
      if (g && g.__geomapa) g.__geomapa.dibuja();
    }

    // El punto de un gráfico más cercano a un clic, de un conjunto de datos dado.
    function pulsado7(chart, evt, ds) {
      const els = chart.getElementsAtEventForMode(evt, 'nearest', { intersect: false, axis: 'xy' }, true);
      const e = els.find(x => x.datasetIndex === ds);
      return e ? e.index : null;
    }
"""

SIMULADORES_JS = JS_PREAMBULO + r"""
    // --- Módulo 1 · el retículo con autocorrelación controlada ------------
    // El proceso es un SAR, y = ρWy + ε, sobre la rejilla torre con W por
    // filas: se resuelve iterando y ← ε + ρWy, que converge porque |ρ| < 1 y
    // las filas de W suman 1. Lo que el texto cita sale del JSON (E[I], su
    // desviación y el rango); el I de cada realización se calcula aquí porque
    // es justo lo que el simulador enseña a no tomar por una cifra fija.
    SIMULADORES['cap7-reticulo'] = function (raiz) {
      const R = D7.m1.reticulo, L = R.lado, N = L * L;
      const vec = [];
      for (let f = 0; f < L; f++) for (let c = 0; c < L; c++) {
        const v = [];
        if (f > 0) v.push((f - 1) * L + c);
        if (f < L - 1) v.push((f + 1) * L + c);
        if (c > 0) v.push(f * L + c - 1);
        if (c < L - 1) v.push(f * L + c + 1);
        vec.push(v);
      }
      const rezago = x => vec.map(v => v.reduce((s, j) => s + x[j], 0) / v.length);
      // mulberry32: un generador con semilla, para que «Otra realización» sea
      // reproducible y la misma semilla dé siempre el mismo mapa.
      const generador = s => () => {
        s = s + 0x6D2B79F5 | 0;
        let t = Math.imul(s ^ s >>> 15, 1 | s);
        t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t;
        return ((t ^ t >>> 14) >>> 0) / 4294967296;
      };
      const normales = u => {
        const out = [];
        while (out.length < N) {
          const a = u() || 1e-12, b = u(), r = Math.sqrt(-2 * Math.log(a));
          out.push(r * Math.cos(2 * Math.PI * b), r * Math.sin(2 * Math.PI * b));
        }
        return out.slice(0, N);
      };
      let rho = 0, semilla = D7.meta.semilla, ultimo = null;
      const cvA = raiz.querySelector('.cap7-lienzo-a');
      const cvB = raiz.querySelector('.cap7-lienzo-b');
      const g = grafico7(cvB, 'scatter', { datasets: [
          { label: 'celdas', data: [], backgroundColor: 'rgba(1,40,32,0.55)', pointRadius: 3 },
          { label: 'recta de mínimos cuadrados', data: [], showLine: true, borderColor: C7.naranja,
            borderWidth: 2, pointRadius: 0, fill: false }] },
        { scales: { x: { title: { display: true, text: 'valor de la celda (z)' } },
                    y: { title: { display: true, text: 'media de sus vecinas (Wz)' } } } });
      const color = t => {
        const a = [33, 102, 172], m = [247, 247, 247], b = [178, 24, 43];
        const u = Math.max(-1, Math.min(1, t / 2.5));
        const [p, q, f] = u < 0 ? [m, a, -u] : [m, b, u];
        return geomapaTinta(`rgb(${p.map((x, k) => Math.round(x + (q[k] - x) * f)).join(',')})`);
      };
      const pintaReticulo = z => {
        if (!cvA || !z) return;
        const ancho = Math.round(cvA.clientWidth || 260), dpr = window.devicePixelRatio || 1;
        cvA.width = Math.round(ancho * dpr); cvA.height = Math.round(ancho * dpr);
        const ctx = cvA.getContext('2d'), lado = cvA.width / L;
        ctx.clearRect(0, 0, cvA.width, cvA.height);
        z.forEach((v, i) => {
          ctx.fillStyle = color(v);
          ctx.fillRect((i % L) * lado, Math.floor(i / L) * lado, Math.ceil(lado), Math.ceil(lado));
        });
        ctx.strokeStyle = 'rgba(255,255,255,0.8)'; ctx.lineWidth = dpr;
        for (let k = 1; k < L; k++) {
          ctx.beginPath(); ctx.moveTo(k * lado, 0); ctx.lineTo(k * lado, cvA.height); ctx.stroke();
          ctx.beginPath(); ctx.moveTo(0, k * lado); ctx.lineTo(cvA.width, k * lado); ctx.stroke();
        }
      };
      const pinta = () => {
        const e = normales(generador(semilla));
        let y = e.slice();
        for (let it = 0; it < 400; it++) { const wy = rezago(y); y = e.map((ei, i) => ei + rho * wy[i]); }
        const m = y.reduce((s, v) => s + v, 0) / N;
        const sd = Math.sqrt(y.reduce((s, v) => s + (v - m) * (v - m), 0) / (N - 1));
        const z = y.map(v => (v - m) / sd), wz = rezago(z);
        const I = z.reduce((s, zi, i) => s + zi * wz[i], 0) / z.reduce((s, zi) => s + zi * zi, 0);
        ultimo = z;
        pintaReticulo(z);
        if (g) {
          g.data.datasets[0].data = z.map((zi, i) => ({ x: zi, y: wz[i] }));
          const xs = [Math.min(...z), Math.max(...z)];
          g.data.datasets[1].data = xs.map(x => ({ x, y: I * x }));
          g.update();
        }
        // Rótulos del módulo 1, que aún no ha definido I ni E[I]: se habla
        // de la pendiente y de hasta dónde llega el azar. Con ρ negativo el
        // azar se mira por abajo: el test es de una cola, y la cola es la
        // del signo de ρ (sin ella, ρ = −0.9 «no rebasaba» nunca).
        const abajo = rho < 0;
        const umbral = R.EI + (abajo ? -1.6449 : 1.6449) * R.sd_norm;
        lectura7(raiz, [
          ['ρ del proceso', n7(rho, 1)],
          ['pendiente de esta realización', n7(I, 4)],
          ['pendiente media sin autocorrelación', n7(R.EI, 6)],
          [abajo ? 'el azar baja hasta (95 % de las veces)' : 'el azar sube hasta (95 % de las veces)', n7(umbral, 4)],
          ['¿la rebasa?', (abajo ? I < umbral : I > umbral) ? 'sí' : 'no'],
          ['la pendiente puede ir de', n7(R.rango[0], 4) + ' a ' + n7(R.rango[1], 4)]]);
      };
      const rhos = [];
      for (let k = -9; k <= 9; k++) rhos.push([k / 10, (k / 10).toFixed(1)]);
      deslizador7(raiz, rhos, 'ρ ', 9, i => { rho = rhos[i][0]; pinta(); });
      accion7(raiz, 'Realizaciones', ['Otra realización'], () => { semilla += 1; pinta(); });
      pinta();
      let ro = null;
      if ('ResizeObserver' in window && cvA) {
        ro = new ResizeObserver(() => pintaReticulo(ultimo));
        ro.observe(cvA);
      }
      return [g, { destroy() { if (ro) ro.disconnect(); } }].filter(Boolean);
    };

    // --- Módulo 3 · el histograma de las réplicas ------------------------
    SIMULADORES['cap7-permutacion'] = function (raiz) {
      const P = D7.m3.columbus.permutacion, rep = P.replicas, I = P.I, EI = D7.m1.columbus.EI;
      const sdA = Math.sqrt(D7.m3.columbus.aleatorizacion.var);
      const KS = [19, 49, 99, 199, 499, P.nsim];
      const lo = -0.35, ancho = 0.025, nb = 40;
      let k = KS.length - 1;
      const g = grafico7(raiz.querySelector('canvas'), 'scatter', { datasets: [
          { label: 'réplicas por permutación', data: [], showLine: true, fill: 'origin',
            borderColor: C7.verde, backgroundColor: C7.suave, pointRadius: 0, borderWidth: 1.5 },
          { label: 'normal de la aleatorización', data: [], showLine: true, borderColor: C7.morado,
            borderDash: [5, 4], pointRadius: 0, borderWidth: 1.5 },
          { label: 'I observado', data: [], showLine: true, borderColor: C7.naranja, pointRadius: 0, borderWidth: 2.5 },
          { label: 'E[I]', data: [], showLine: true, borderColor: C7.gris, pointRadius: 0, borderWidth: 2 }] },
        { scales: { x: { type: 'linear', min: lo, max: lo + nb * ancho,
                         title: { display: true, text: 'I de Moran' } },
                    y: { beginAtZero: true, title: { display: true, text: 'réplicas' } } } });
      const pinta = () => {
        const K = KS[k], usadas = rep.slice(0, K);
        const cuenta = new Array(nb).fill(0);
        usadas.forEach(v => { const b = Math.floor((v - lo) / ancho); if (b >= 0 && b < nb) cuenta[b] += 1; });
        const esc = [];
        cuenta.forEach((c, b) => { esc.push({ x: lo + b * ancho, y: c }, { x: lo + (b + 1) * ancho, y: c }); });
        const curva = [];
        for (let x = lo; x <= lo + nb * ancho + 1e-9; x += ancho / 4) {
          const d = Math.exp(-0.5 * ((x - EI) / sdA) ** 2) / (sdA * Math.sqrt(2 * Math.PI));
          curva.push({ x, y: K * ancho * d });
        }
        const tope = Math.max(...cuenta, ...curva.map(p => p.y)) * 1.08;
        const r = usadas.filter(v => v >= I).length;
        const media = usadas.reduce((s, v) => s + v, 0) / K;
        const sd = Math.sqrt(usadas.reduce((s, v) => s + (v - media) ** 2, 0) / (K - 1));
        if (g) {
          g.data.datasets[0].data = esc;
          g.data.datasets[1].data = curva;
          g.data.datasets[2].data = [{ x: I, y: 0 }, { x: I, y: tope }];
          g.data.datasets[3].data = [{ x: EI, y: 0 }, { x: EI, y: tope }];
          g.options.scales.y.max = tope;
          g.update();
        }
        lectura7(raiz, [
          ['réplicas usadas', mil7(K)],
          ['I observado', n7(I, 6)],
          ['réplicas que lo igualan o superan', mil7(r)],
          ['p = (r + 1)/(réplicas + 1)', p7((r + 1) / (K + 1))],
          ['el p más pequeño posible', p7(1 / (K + 1))],
          ['media de esas réplicas', n7(media, 4)],
          ['desviación típica', n7(sd, 4)]]);
      };
      deslizador7(raiz, KS.map(v => [v, mil7(v)]), 'réplicas ', k, i => { k = i; pinta(); });
      pinta();
      return g ? [g] : [];
    };

    // --- Módulo 3 · la potencia -------------------------------------------
    SIMULADORES['cap7-potencia'] = function (raiz) {
      const PT = D7.m3.potencia, rhos = PT.rhos, curvas = PT.curvas;
      const tintas = [C7.rosa, C7.naranja, C7.verde, C7.tinta];
      let i = 3;
      const g = grafico7(raiz.querySelector('canvas'), 'scatter', { datasets: curvas.map((c, k) => ({
          label: c.n + ' celdas', data: rhos.map((r, j) => ({ x: r, y: c.potencia[j] })), showLine: true,
          borderColor: tintas[k], backgroundColor: tintas[k], pointRadius: 3, borderWidth: 2 }))
          .concat([{ label: '', data: [], showLine: true, borderColor: C7.gris, borderDash: [4, 4],
                     pointRadius: 0, borderWidth: 1.5 },
                   { label: 'nivel del test (5 %)', data: [{ x: rhos[0], y: PT.alfa }, { x: rhos[rhos.length - 1], y: PT.alfa }],
                     showLine: true, borderColor: C7.morado, borderDash: [2, 3], pointRadius: 0, borderWidth: 1 }]) },
        { scales: { x: { type: 'linear', min: 0, max: rhos[rhos.length - 1],
                         title: { display: true, text: 'ρ del proceso' } },
                    y: { min: 0, max: 1, title: { display: true, text: 'fracción de rechazos' } } } });
      const pinta = () => {
        if (g) { g.data.datasets[curvas.length].data = [{ x: rhos[i], y: 0 }, { x: rhos[i], y: 1 }]; g.update(); }
        lectura7(raiz, [['ρ', n7(rhos[i], 1)]].concat(curvas.map(c => [c.n + ' celdas', n7(c.potencia[i], 3)])));
      };
      deslizador7(raiz, rhos.map(r => [r, n7(r, 1)]), 'ρ ', i, j => { i = j; pinta(); });
      pinta();
      return g ? [g] : [];
    };

    // --- Módulo 4 · el diagrama de Moran clicable ---------------------------
    SIMULADORES['cap7-diagrama'] = function (raiz) {
      const PC = D7.m4.columbus.puntos, PM = D7.m4.municipios.puntos;
      const inf = new Set(D7.m4.columbus.influyentes_polyid);
      const sinEl = {};
      D7.m4.columbus.influyentes_detalle.forEach(d => { sinEl[d.polyid] = d.pendiente_sin; });
      // LAS ISLAS NO TIENEN CUADRANTE: su rezago vale 0 porque no hay vecinos,
      // y cuad7(z, 0) las ponía en «bajo-alto» (auditoría del 2026-10-20).
      // Se buscan por nombre y departamento, no por un Wz que valga cero.
      const IS7 = D7.m9.municipios.islas, islas7 = new Set();
      NOMBRES_MUN7.forEach((nm, k) => { IS7.municipio.forEach((m, j) => {
        if (nm[0] === m && nm[1] === IS7.departamento[j]) islas7.add(k); }); });
      // Los vecinos de cada barrio en la GAL, desde las aristas del mapa (1-based).
      const ar = MAPAS_CAP7['cap7-w'].variantes.gal.aristas, vec = PC.z.map(() => []);
      for (let a = 0; a < ar.length; a += 2) { vec[ar[a] - 1].push(ar[a + 1] - 1); vec[ar[a + 1] - 1].push(ar[a] - 1); }
      const g = grafico7(raiz.querySelector('canvas'), 'scatter', { datasets: [
          { label: 'unidades', data: [], pointRadius: [], pointBackgroundColor: [], pointBorderColor: [],
            pointBorderWidth: [] },
          { label: 'recta: su pendiente es I', data: [], showLine: true, borderColor: C7.tinta,
            borderWidth: 1.5, pointRadius: 0 }] },
        { scales: { x: { title: { display: true, text: 'valor tipificado (z)' } },
                    y: { title: { display: true, text: 'media de los vecinos (Wz)' } } },
          plugins: { legend: { display: false } },
          onClick: (evt, _e, chart) => { const k = pulsado7(chart, evt, 0); if (k != null) { E7.diagSel = k; pinta(); } } });
      const datos = () => E7.diagTab === 'mun' ? PM : PC;
      const pinta = () => {
        const P = datos(), n = P.z.length, s = E7.diagSel;
        const veci = E7.diagTab === 'col' && s != null ? new Set(vec[s]) : new Set();
        if (g) {
          const ds = g.data.datasets[0];
          ds.data = P.z.map((z, k) => ({ x: z, y: P.wz[k] }));
          const mun = E7.diagTab === 'mun';
          const isla = k => mun && islas7.has(k);
          const esInf = k => !mun && inf.has(P.polyid[k]);
          ds.pointBackgroundColor = P.z.map((z, k) => k === s ? C7.naranja
            : (isla(k) ? 'rgba(0,0,0,0)' : CUAD7[cuad7(z, P.wz[k])]));
          ds.pointRadius = P.z.map((_, k) => k === s ? 7 : (isla(k) ? 5 : (veci.has(k) || esInf(k) ? 5 : (n > 200 ? 2 : 4))));
          ds.pointBorderColor = P.z.map((_, k) => k === s ? C7.tinta : (veci.has(k) ? C7.naranja
            : (esInf(k) || isla(k) ? C7.tinta : 'rgba(255,255,255,0.7)')));
          ds.pointBorderWidth = P.z.map((_, k) => k === s ? 2 : (veci.has(k) || esInf(k) ? 2.5 : (isla(k) ? 1.5 : 0.5)));
          const I = E7.diagTab === 'mun' ? D7.m4.municipios.pendiente_todas : D7.m4.columbus.pendiente;
          const xs = [Math.min(...P.z), Math.max(...P.z)];
          g.data.datasets[1].data = xs.map(x => ({ x, y: I * x }));
          g.update();
        }
        repinta7('cap7-diagrama-mapa');
        const fila = [['tablero', E7.diagTab === 'mun' ? 'municipios' : 'Columbus'],
                      ['pendiente = I', n7(E7.diagTab === 'mun' ? D7.m4.municipios.pendiente_todas : D7.m4.columbus.pendiente, 6)]];
        if (s == null) { lectura7(raiz, fila.concat([['unidad', 'pulsa un punto']])); return; }
        const sinVecinos = E7.diagTab === 'mun' && islas7.has(s);
        const q = cuad7(P.z[s], P.wz[s]);
        if (E7.diagTab === 'mun') {
          fila.push(['municipio', NOMBRES_MUN7[s][0] + ' (' + NOMBRES_MUN7[s][1] + ')'],
                    ['deserción', n7(MUN7.capas[0].valor[MUN7_IDX[s]], 2) + ' %']);
        } else {
          fila.push(['barrio', 'POLYID ' + P.polyid[s]], ['CRIME', n7(COL7.capas[0].valor[s], 2)],
                    ['vecinos en la GAL', vec[s].length],
                    ['«influyente» para moran.plot', inf.has(P.polyid[s]) ? 'sí' : 'no']);
          if (inf.has(P.polyid[s])) fila.push(['la pendiente sin él', n7(sinEl[P.polyid[s]], 4)]);
        }
        fila.push(['z', n7(P.z[s], 4)], ['Wz', sinVecinos ? '0 (sin vecinos)' : n7(P.wz[s], 4)],
                  ['cuadrante', sinVecinos ? 'ninguno: no tiene vecinos' : CUAD7_NOMBRE[q]]);
        lectura7(raiz, fila);
      };
      grupo7(raiz, 'Tablero', ['Columbus', 'Municipios'], i => {
        E7.diagTab = i ? 'mun' : 'col'; E7.diagSel = null; pinta(); }, E7.diagTab === 'mun' ? 1 : 0);
      accion7(raiz, 'Recorrer las unidades', ['◀ anterior', 'siguiente ▶'], i => {
        const n = datos().z.length;
        E7.diagSel = E7.diagSel == null ? 0 : (E7.diagSel + (i ? 1 : n - 1)) % n;
        pinta();
      });
      pinta();
      return g ? [g] : [];
    };

    // --- Módulo 5 · un barrio disparado -------------------------------------
    SIMULADORES['cap7-geary'] = function (raiz) {
      const picos = [D7.m5.pico_en_alto, D7.m5.pico_en_bajo];
      const EI = D7.m1.columbus.EI;
      let i = 0;
      const xs = picos[0].curva.map(c => c.factor), x0 = xs[0], x1 = xs[xs.length - 1];
      const g = grafico7(raiz.querySelector('canvas'), 'scatter', { datasets: [
          { label: 'I de Moran', data: [], showLine: true, borderColor: C7.verde, backgroundColor: C7.verde, pointRadius: 4, borderWidth: 2 },
          { label: 'c de Geary', data: [], showLine: true, borderColor: C7.naranja, backgroundColor: C7.naranja, pointRadius: 4, borderWidth: 2 },
          { label: 'E[I], el nulo de I', data: [{ x: x0, y: EI }, { x: x1, y: EI }], showLine: true,
            borderColor: C7.verde, borderDash: [5, 4], pointRadius: 0, borderWidth: 1 },
          { label: 'E[c] = 1, el nulo de c', data: [{ x: x0, y: 1 }, { x: x1, y: 1 }], showLine: true,
            borderColor: C7.naranja, borderDash: [5, 4], pointRadius: 0, borderWidth: 1 }] },
        { scales: { x: { type: 'linear', min: x0, max: x1, title: { display: true, text: 'factor por el que se multiplica el barrio' } },
                    y: { min: -0.1, max: 1.1, title: { display: true, text: 'valor del índice' } } } });
      const pinta = () => {
        const p = picos[i], fin = p.curva[p.curva.length - 1];
        if (g) {
          g.data.datasets[0].data = p.curva.map(c => ({ x: c.factor, y: c.I }));
          g.data.datasets[1].data = p.curva.map(c => ({ x: c.factor, y: c.c }));
          g.update();
        }
        lectura7(raiz, [
          ['barrio', 'POLYID ' + p.polyid], ['CRIME', n7(p.crime, 4)], ['vecinos', p.grado],
          ['z', n7(p.z, 4)], ['Wz', n7(p.wz, 4)],
          ['I sin tocar', n7(p.curva[0].I, 4)], ['I con el factor ' + fin.factor, n7(fin.I, 4)],
          ['c sin tocar', n7(p.curva[0].c, 4)], ['c con el factor ' + fin.factor, n7(fin.c, 4)]]);
      };
      grupo7(raiz, 'Barrio disparado', picos.map((p, k) => (k ? 'el de vecindad más baja' : 'el de mayor CRIME')
        + ' (POLYID ' + p.polyid + ')'), k => { i = k; pinta(); }, 0);
      pinta();
      return g ? [g] : [];
    };

    // --- Módulo 6 · el correlograma -----------------------------------------
    SIMULADORES['cap7-correlograma'] = function (raiz) {
      let tab = 'columbus', sel = 0;
      const g = grafico7(raiz.querySelector('canvas'), 'bar', { labels: [], datasets: [
          { label: 'I de Moran', data: [], backgroundColor: [], order: 2 },
          { label: 'E[I] ± 2 desviaciones', data: [], type: 'line', borderColor: C7.gris, borderDash: [5, 4],
            pointRadius: 0, borderWidth: 1.5, fill: false, order: 1 },
          { label: '', data: [], type: 'line', borderColor: C7.gris, borderDash: [5, 4],
            pointRadius: 0, borderWidth: 1.5, fill: false, order: 1 },
          { label: 'E[I]', data: [], type: 'line', borderColor: C7.tinta, pointRadius: 0, borderWidth: 1, fill: false, order: 1 }] },
        // Sin leyenda: la muestra de «I de Moran» tomaba el color de la barra
        // 0 —naranja cuando está elegida—, y el pie ya dice qué es cada color.
        { scales: { x: { title: { display: true, text: 'orden de contigüidad' } },
                    y: { title: { display: true, text: 'I de Moran' } } },
          plugins: { legend: { display: false } },
          onClick: (evt, _e, chart) => { const k = pulsado7(chart, evt, 0); if (k != null) { sel = k; pinta(); } } });
      const pinta = () => {
        const cg = D7.m6.correlograma[tab];
        if (sel >= cg.length) sel = 0;
        if (g) {
          g.data.labels = cg.map(o => String(o.orden));
          g.data.datasets[0].data = cg.map(o => o.I);
          g.data.datasets[0].backgroundColor = cg.map((o, k) => k === sel ? C7.naranja : (o.I >= 0 ? C7.verde : C7.morado));
          g.data.datasets[1].data = cg.map(o => o.EI + 2 * Math.sqrt(o.var));
          g.data.datasets[2].data = cg.map(o => o.EI - 2 * Math.sqrt(o.var));
          g.data.datasets[3].data = cg.map(o => o.EI);
          g.update();
        }
        const o = cg[sel];
        lectura7(raiz, [['orden', o.orden], ['I', n7(o.I, 4)], ['E[I]', n7(o.EI, 6)], ['z', n7(o.z, 4)],
                        ['parejas a ese orden', mil7(o.pares)], ['unidades sin vecinos', mil7(o.sin_vecinos)],
                        ['trozos del grafo', mil7(o.subgrafos)]]);
      };
      grupo7(raiz, 'Tablero', ['Columbus', 'Municipios'], k => { tab = k ? 'municipios' : 'columbus'; sel = 0; pinta(); }, 0);
      // Las barras se pueden pulsar, y también recorrer con el teclado.
      accion7(raiz, 'Recorrer los órdenes', ['◀ anterior', 'siguiente ▶'], i => {
        const m = D7.m6.correlograma[tab].length;
        sel = (sel + (i ? 1 : m - 1)) % m; pinta();
      });
      pinta();
      return g ? [g] : [];
    };

    // --- Módulo 6 · el join count --------------------------------------------
    SIMULADORES['cap7-joincount'] = function (raiz) {
      const casos = [['columbus_cp', 'CP en Columbus'], ['municipios_desercion', 'deserción sobre la mediana'],
                     ['municipios_tipo', 'tipo de entidad']];
      const corto = { 'periferia': 'periferia', 'centro': 'centro', 'bajo la mediana': 'bajo',
                      'sobre la mediana': 'sobre', 'no municipalizada o isla': 'no municipio', 'municipio': 'municipio' };
      const nombre = par => par.split(':').map(x => corto[x] || x).join('–');
      let i = 0;
      const g = grafico7(raiz.querySelector('canvas'), 'bar', { labels: [], datasets: [
          { label: 'uniones observadas', data: [], backgroundColor: C7.verde },
          { label: 'esperadas al azar', data: [], backgroundColor: C7.gris }] },
        { scales: { y: { beginAtZero: true, title: { display: true, text: 'uniones (ponderadas por W)' } } } });
      const pinta = () => {
        const J = D7.m6.join_count[casos[i][0]], filas = J.tabla.filter(f => f.par !== 'Jtot');
        if (g) {
          g.data.labels = filas.map(f => nombre(f.par));
          g.data.datasets[0].data = filas.map(f => f.observado);
          g.data.datasets[1].data = filas.map(f => f.esperado);
          g.update();
        }
        lectura7(raiz, filas.map(f => ['z de ' + nombre(f.par), n7(f.z, 4)])
          .concat(J.niveles.map((nv, k) => [nv, mil7(J.n_por_nivel[k]) + ' unidades']))
          .concat(J.p_permutacion.map(x => ['p por permutación (' + x.nivel + '–' + x.nivel + ')', p7(x.p)])));
      };
      grupo7(raiz, 'Variable', casos.map(c => c[1]), k => { i = k; pinta(); }, 0);
      pinta();
      return g ? [g] : [];
    };

    // --- Módulo 7 · once W ---------------------------------------------------
    SIMULADORES['cap7-w'] = function (raiz) {
      const ws = D7.m7.columbus;
      const corto = { gal: 'GAL', reina: 'reina', torre: 'torre', k1: 'k = 1', k3: 'k = 3', k6: 'k = 6',
                      d_mitad: 'umbral ½', d_conexo: 'umbral mín.', delaunay: 'Delaunay', gabriel: 'Gabriel',
                      esfera: 'esfera' };
      const g = grafico7(raiz.querySelector('canvas'), 'bar', { labels: ws.map(w => corto[w.id] || w.id),
          datasets: [{ label: 'I de Moran de CRIME', data: ws.map(w => w.I), backgroundColor: [] }] },
        { scales: { y: { beginAtZero: true, title: { display: true, text: 'I de Moran' } } },
          plugins: { legend: { display: false } },
          onClick: (evt, _e, chart) => { const k = pulsado7(chart, evt, 0); if (k != null) { elige(k); } } });
      let marca = () => {};
      const pinta = () => {
        const k = ws.findIndex(w => w.id === E7.w), w = ws[k];
        if (g) { g.data.datasets[0].backgroundColor = ws.map((_, j) => j === k ? C7.naranja : C7.suave); g.update(); }
        repinta7('cap7-w-mapa');
        lectura7(raiz, [['vecindad', w.etiqueta], ['parejas', mil7(w.pares)], ['grado medio', n7(w.grado, 4)],
                        ['barrios sin vecinos', mil7(w.islas)], ['simétrica', w.simetrica ? 'sí' : 'no'],
                        ['I', n7(w.I, 6)], ['E[I]', n7(w.EI, 6)], ['z', n7(w.z, 4)], ['p analítico', p7(w.p)],
                        ['p por permutación (' + mil7(w.nsim_permutacion) + ' réplicas)', p7(w.p_permutacion)]]);
      };
      const elige = k => { E7.w = ws[k].id; marca(k); pinta(); };
      marca = grupo7(raiz, 'Vecindad', ws.map(w => w.etiqueta), k => { E7.w = ws[k].id; pinta(); },
                     ws.findIndex(w => w.id === E7.w));
      pinta();
      return g ? [g] : [];
    };

    // --- Módulo 8 · los I locales ---------------------------------------------
    SIMULADORES['cap7-local'] = function (raiz) {
      const L = D7.m8.columbus, lisa = COL7.capas[1];
      const orden = L.Ii.map((_, k) => k).sort((a, b) => L.Ii[b] - L.Ii[a]);
      const tinta = k => { const v = lisa.valor[k]; return v ? lisa.colores[v - 1] : C7.grisClaro; };
      let pos = null;
      const g = grafico7(raiz.querySelector('canvas'), 'bar', { labels: orden.map(k => String(L.polyid[k])),
          datasets: [{ label: 'I local', data: orden.map(k => L.Ii[k]), backgroundColor: [], borderColor: [], borderWidth: [], order: 2 },
                     { label: 'su media: el I de Moran', data: orden.map(() => L.media_Ii), type: 'line',
                       borderColor: C7.tinta, borderDash: [5, 4], pointRadius: 0, borderWidth: 1.5, order: 1 }] },
        { scales: { x: { title: { display: true, text: 'barrio (POLYID), de mayor a menor I local' }, ticks: { autoSkip: true, maxRotation: 0 } },
                    y: { title: { display: true, text: 'I local' } } },
          onClick: (evt, _e, chart) => { const k = pulsado7(chart, evt, 0); if (k != null) { pos = k; pinta(); } } });
      const pinta = () => {
        const s = pos == null ? null : orden[pos];
        E7.localSel = s;
        if (g) {
          const ds = g.data.datasets[0];
          ds.backgroundColor = orden.map(k => geomapaTinta(tinta(k)));
          ds.borderColor = orden.map(k => k === s ? C7.tinta : 'rgba(0,0,0,0)');
          ds.borderWidth = orden.map(k => k === s ? 3 : 0);
          g.update();
        }
        repinta7('cap7-local-mapa');
        if (s == null) { lectura7(raiz, [['I de Moran (la media)', n7(L.media_Ii, 6)], ['barrio', 'pulsa una barra']]); return; }
        const v = lisa.valor[s];
        lectura7(raiz, [['barrio', 'POLYID ' + L.polyid[s]], ['I local', n7(L.Ii[s], 5)],
                        ['z respecto de sus repartos', n7(L.z[s], 4)],
                        ['p bilateral (' + mil7(D7.m8.nsim) + ' réplicas)', p7(L.p_rangos[s])],
                        ['p plegado, el de GeoDa', p7(L.p_plegado[s])],
                        ['p analítico', p7(L.p_analitico[s])], ['cuadrante', SPDEP7[L.cuadrante[s]] || L.cuadrante[s]],
                        ['en el mapa LISA', v ? lisa.niveles[v - 1] : SIN_DATO7]]);
      };
      accion7(raiz, 'Recorrer los barrios', ['◀ anterior', 'siguiente ▶'], i => {
        pos = pos == null ? 0 : (pos + (i ? 1 : orden.length - 1)) % orden.length;
        pinta();
      });
      pinta();
      return g ? [g] : [];
    };

    // --- Módulo 9 · deserción o conglomerados ----------------------------------
    SIMULADORES['cap7-lisa-mapa'] = function (raiz) {
      const pinta = () => {
        repinta7('cap7-municipios-m9');
        const cp = MUN7.capas.find(c => c.id === E7.m9capa);
        const filas = cp.tipo === 'categoria'
          ? cp.niveles.map((nv, k) => [nv, mil7(cp.tam[k])])
          : cp.tam.map((t, k) => [n7(cp.cortes[k], 2) + ' – ' + n7(cp.cortes[k + 1], 2) + ' %', mil7(t)]);
        lectura7(raiz, [['capa', cp.etiqueta]].concat(filas).concat([[SIN_DATO7, mil7(cp.n_sin_dato)]]));
      };
      grupo7(raiz, 'Capa', ['Deserción', 'Conglomerados LISA'], k => { E7.m9capa = k ? 'lisa' : 'desercion'; pinta(); },
             E7.m9capa === 'lisa' ? 1 : 0);
      pinta();
      return [];
    };

    // --- Módulo 10 · Benjamini-Hochberg ------------------------------------------
    SIMULADORES['cap7-bh'] = function (raiz) {
      const B = D7.m10.columbus.bh, n = B.p_ordenados.length;
      const rangos = B.p_ordenados.map((_, k) => k + 1);
      let sel = B.k - 1;
      const g = grafico7(raiz.querySelector('canvas'), 'scatter', { datasets: [
          { label: 'p ordenados', data: B.p_ordenados.map((p, k) => ({ x: k + 1, y: p })),
            pointBackgroundColor: [], pointRadius: [], pointBorderColor: C7.tinta, pointBorderWidth: [] },
          { label: 'umbral FDR: k·α/n', data: rangos.map((k, j) => ({ x: k, y: B.umbrales[j] })), showLine: true,
            borderColor: C7.naranja, pointRadius: 0, borderWidth: 2 },
          { label: 'umbral Bonferroni: α/n', data: [{ x: 1, y: B.umbral_bonferroni }, { x: n, y: B.umbral_bonferroni }],
            showLine: true, borderColor: C7.morado, borderDash: [5, 4], pointRadius: 0, borderWidth: 2 }] },
        { scales: { x: { type: 'linear', min: 0, max: n + 1, title: { display: true, text: 'posición k del p, de menor a mayor' } },
                    y: { type: 'logarithmic', title: { display: true, text: 'p (escala logarítmica)' } } },
          onClick: (evt, _e, chart) => { const k = pulsado7(chart, evt, 0); if (k != null) { sel = k; pinta(); } } });
      const pinta = () => {
        if (g) {
          const ds = g.data.datasets[0];
          ds.pointBackgroundColor = B.p_ordenados.map((_, k) => k < B.k ? C7.naranja : C7.grisClaro);
          ds.pointRadius = B.p_ordenados.map((_, k) => k === sel ? 7 : 4);
          ds.pointBorderWidth = B.p_ordenados.map((_, k) => k === sel ? 2 : 0.5);
          g.update();
        }
        const p = B.p_ordenados[sel];
        lectura7(raiz, [['posición k', sel + 1], ['p', p7(p)], ['su umbral de FDR', p7(B.umbrales[sel])],
                        ['umbral de Bonferroni', p7(B.umbral_bonferroni)],
                        ['¿entra con FDR?', sel < B.k ? 'sí' : 'no'],
                        ['¿entra con Bonferroni?', p < B.umbral_bonferroni ? 'sí' : 'no'],
                        ['k de Benjamini-Hochberg', B.k]]);
      };
      pinta();
      return g ? [g] : [];
    };

    // --- Módulo 10 · el mapa con y sin corrección ----------------------------------
    SIMULADORES['cap7-multiplicidad'] = function (raiz) {
      const capas = ['lisa', 'lisa_bonferroni', 'lisa_fdr'];
      const nombres = ['sin corregir', 'Bonferroni', 'FDR'];
      const pinta = () => {
        repinta7('cap7-multiplicidad-mapa');
        const d = E7.multTab === 'mun' ? MUN7 : COL7;
        const cp = d.capas.find(c => c.id === E7.multCapa);
        const tab = E7.multTab === 'mun' ? D7.m10.municipios.tabla.bilateral_nsim : D7.m10.columbus.tabla.bilateral_nsim;
        const suelo = E7.multTab === 'mun' ? D7.m10.suelo.municipios : D7.m10.suelo.columbus;
        const k = capas.indexOf(E7.multCapa);
        lectura7(raiz, [['corrección', nombres[k]],
                        ['significativos', mil7([tab.sin_corregir, tab.bonferroni, tab.fdr][k])]]
          .concat(cp.niveles.slice(1).map((nv, j) => [nv, mil7(cp.tam[j + 1])]))
          .concat([['umbral de Bonferroni', p7(suelo.umbral_bonferroni)],
                   ['réplicas mínimas para Bonferroni', mil7(suelo.nsim_minimo)]]));
      };
      // El botón activo sale de E7, que sobrevive a cambiar de módulo: con un
      // 0 fijo, al volver los botones decían «Columbus · sin corregir» y el
      // mapa seguía en lo último elegido (auditoría del 2026-10-20).
      grupo7(raiz, 'Tablero', ['Columbus', 'Municipios'], k => { E7.multTab = k ? 'mun' : 'col'; pinta(); },
             E7.multTab === 'mun' ? 1 : 0);
      grupo7(raiz, 'Corrección', nombres, k => { E7.multCapa = capas[k]; pinta(); }, capas.indexOf(E7.multCapa));
      pinta();
      return [];
    };

    // --- Módulo 11 · LISA y Gi*, lado a lado ------------------------------------------
    SIMULADORES['cap7-gistar'] = function (raiz) {
      const pinta = () => {
        repinta7('cap7-lado-lisa');
        repinta7('cap7-lado-gi');
        const G = E7.ladoTab === 'mun' ? D7.m11.municipios : D7.m11.columbus;
        lectura7(raiz, G.cruce.map(f => [f.lisa + ' en LISA',
          `${mil7(f.caliente)} calientes · ${mil7(f.frio)} fríos · ${mil7(f.ninguno)} no significativos (al 90 %)`])
          .concat([['z máxima de Gi*', n7(G.z_max, 4)], ['z mínima', n7(G.z_min, 4)]]));
      };
      grupo7(raiz, 'Tablero', ['Columbus', 'Municipios'], k => { E7.ladoTab = k ? 'mun' : 'col'; pinta(); },
             E7.ladoTab === 'mun' ? 1 : 0);
      pinta();
      return [];
    };
"""

# =====================================================================
# LA AUTOEVALUACIÓN
#
# Cada retro se escribe para que se entienda SOLA: `baraja_opciones.py`
# cambia el orden al ensamblar, y una retro que diga «como la anterior»
# acaba detrás de otra cualquiera (trampa 3 del capítulo 4). Los
# distractores se escriben con el mismo cuidado que la clave, y con una
# longitud parecida (A.30.6): el agente ciego acertaba por la más larga.
# =====================================================================
QUIZ_JS = r"""
    AUTOEVALUACIONES['cap7-quiz'] = [
      {
        tipo: 'opcion',
        pista: 'Piensa en qué se queda fijo y qué cambia entre dos realizaciones del azar.',
        pregunta: 'En este capítulo, ¿qué afirma la hipótesis nula de «ausencia de autocorrelación espacial»?',
        opciones: [
          { texto: 'Que cualquier reparto de los mismos valores entre las unidades era igual de probable', correcta: true,
            retro: 'Eso es. El mapa, W y la lista de valores se quedan; lo único que el azar mueve es qué valor le toca a qué unidad. Las tres inferencias del módulo 3 comparan con ese azar.' },
          { texto: 'Que el I de Moran del mapa observado vale exactamente cero, sin desviación',
            retro: 'Ni siquiera su esperanza es cero, como enseña el módulo 2. Y la nula habla de cómo se generó el mapa, no del valor de un índice.' },
          { texto: 'Que las unidades están colocadas al azar sobre el territorio, como puntos sueltos',
            retro: 'Eso es la aleatoriedad espacial completa de un patrón puntual, el capítulo 4. En un dato de área las unidades están fijas y lo aleatorio es el valor.' },
          { texto: 'Que los valores son extracciones independientes de una distribución normal',
            retro: 'Ese es un supuesto añadido de UNA de las tres inferencias, la de normalidad. La aleatorización y la permutación comparan con el mismo azar sin suponerlo.' }
        ] },
      {
        tipo: 'numerica',
        pista: 'Es −1/(n − 1), y Columbus tiene 49 barrios. Escríbela con tres decimales.',
        pregunta: '¿Cuánto vale E[I], la esperanza del I de Moran bajo la hipótesis nula, con los 49 barrios de Columbus?',
        respuesta: D7.m1.columbus.EI, tolerancia: 0.0002,
        retroAcierto: 'Es ' + n7(D7.m1.columbus.EI, 6) + '. Es negativa porque los valores centrados suman cero y W no tiene diagonal: de la suma de todos los productos z_i z_j, que vale cero, se quitan los n cuadrados, todos positivos.',
        retroFallo: 'Es −1/(n − 1) = ' + n7(D7.m1.columbus.EI, 6) + ', negativa y no cero: al quitar la diagonal —nadie es vecino de sí mismo— se quitan n productos positivos de una suma que valía cero. Si te salió −1/n, contaste también la pareja de cada unidad consigo misma.'
      },
      {
        tipo: 'opcion',
        pista: '¿Quién fija el máximo de I? No es la fórmula de la correlación.',
        pregunta: 'Calculas el I de Moran de un mapa con W por filas y te da 1.03. ¿Qué concluyes?',
        opciones: [
          { texto: 'Que puede ser, porque el máximo lo fijan los valores propios de (W + Wᵀ)/2 centrada', correcta: true,
            retro: 'Eso es. Con la reina municipal el rango alcanzable va de ' + n7(D7.m2.rango.municipios[0], 4) + ' a ' + n7(D7.m2.rango.municipios[1], 4) + ', y con la GAL de Columbus de ' + n7(D7.m2.rango.columbus_gal[0], 4) + ' a ' + n7(D7.m2.rango.columbus_gal[1], 4) + '. No siempre pasa de 1: en el retículo del módulo 1 se queda en ' + n7(D7.m2.rango.reticulo_10[1], 4) + '.' },
          { texto: 'Que hay un error de cálculo, porque I es una correlación y no puede pasar de 1',
            retro: 'I no es una correlación: su rango no es [−1, 1] sino el que dan los valores propios de (W + Wᵀ)/2 centrada, y su máximo puede pasar de 1 por poco.' },
          { texto: 'Que hay autocorrelación negativa: el valor se sale del rango habitual de I',
            retro: 'Un I por encima de E[I] es autocorrelación positiva, y uno cercano a su máximo, muy fuerte. La negativa estaría por debajo de E[I].' },
          { texto: 'Que W no está bien estandarizada por filas y hay que repetir el cálculo',
            retro: 'Con W por filas, n/S0 vale 1 y el rango es el de los valores propios, que puede superar 1. El valor no delata ningún problema de W.' }
        ] },
      {
        tipo: 'multiple',
        pista: 'Son dos. Piensa en qué supone cada método sobre el dato, y en qué pasa cuando ninguna réplica llega al observado.',
        pregunta: 'Sobre las tres formas de obtener la distribución de I bajo la nula, marca <strong>todo</strong> lo que es cierto.',
        retroAcierto: 'Las dos: la aleatorización no necesita que el dato sea normal, y el p de permutación tiene un suelo que no depende del dato.',
        retroFallo: 'Las dos ciertas son la de la curtosis y la del suelo 1/(nsim + 1). La permutación supone que todas las unidades son intercambiables, y un p que toca el suelo no dice que el efecto sea más débil.',
        opciones: [
          { texto: 'La aleatorización no supone que el dato sea normal: su varianza depende de su curtosis', correcta: true,
            retro: 'Sí: en Columbus la curtosis de CRIME es ' + n7(D7.m3.columbus.aleatorizacion.curtosis, 4) + ', y la varianza pasa de ' + n7(D7.m3.columbus.normalidad.var, 5) + ' bajo normalidad a ' + n7(D7.m3.columbus.aleatorizacion.var, 6) + '. Para el p sí supone algo: que I se reparte como una normal.' },
          { texto: 'El p por permutación no puede bajar de 1/(nsim + 1), porque el dato observado cuenta', correcta: true,
            retro: 'Sí: con 999 réplicas no baja de ' + p7(D7.m3.columbus.permutacion.p) + ', aunque el p analítico de los municipios sea ' + p7(D7.m3.municipios.aleatorizacion.p) + '.' },
          { texto: 'La permutación no supone nada, así que vale igual aunque las poblaciones sean muy distintas',
            retro: 'Supone que cualquier valor podría haber caído en cualquier unidad. Con tasas de poblaciones muy distintas eso falla: la tasa de un municipio pequeño es más ruidosa.' },
          { texto: 'Con 999 réplicas, un p de 0.001 indica un efecto más débil que un p analítico de 10⁻¹⁰¹',
            retro: 'El 0.001 es el suelo de 999 réplicas: el método no puede decir más. Y el 10⁻¹⁰¹ es la cola de una normal muy lejos del centro: dice «muchísimo», no la cifra.' }
        ] },
      {
        tipo: 'opcion',
        pista: 'Compara la fórmula de la pendiente con la de I: solo las separa un factor.',
        pregunta: 'En el diagrama de Moran de <code>spdep</code>, ¿cuándo es la pendiente de la recta de Wz sobre z exactamente el I de Moran?',
        opciones: [
          { texto: 'Cuando W está estandarizada por filas, porque entonces el factor n/S0 vale 1', correcta: true,
            retro: 'Eso es: I = (n/S0)·b, y con W por filas S0 = n. En Columbus las dos valen ' + n7(D7.m4.columbus.pendiente, 6) + '. Con la W binaria se separan, como enseña el ejercicio 2. Con islas spdep cuenta n como las unidades con vecinos, y el factor sigue valiendo 1.' },
          { texto: 'Siempre, con cualquier W: el diagrama es la definición misma del índice',
            retro: 'El diagrama es una lectura del índice, no su definición: con la W binaria la pendiente y el I difieren en el factor n/S0.' },
          { texto: 'Solo cuando el dato está tipificado, porque si no la escala de los ejes cambia',
            retro: 'Tipificar no hace falta, ni siquiera centrar: con la recta con término independiente, el CRIME crudo da también ' + n7(D7.m4.columbus.pendiente_sin_tipificar, 6) + '. Centrar solo importa con islas.' },
          { texto: 'Solo cuando no hay islas, porque una isla tiene un rezago que vale cero',
            retro: 'Con islas, en spdep, la identidad se sigue cumpliendo sobre todas las unidades, islas incluidas: ' + n7(D7.m4.municipios.pendiente_todas, 6) + ' en los municipios, con el dato centrado.' }
        ] },
      {
        tipo: 'opcion',
        pista: 'Mira qué eje del diagrama es la unidad y cuál son sus vecinos.',
        pregunta: 'Un barrio cae en el cuadrante bajo-alto del diagrama de Moran. ¿Qué dice eso de él?',
        opciones: [
          { texto: 'Que su valor está por debajo de la media y el de sus vecinos, por encima', correcta: true,
            retro: 'Eso es: es un contraste, no un parecido. En Columbus hay ' + D7.m4.columbus.cuadrantes.BA + ' en ese cuadrante, y el más extremo es el barrio de menos delitos del mapa.' },
          { texto: 'Que su valor es bajo y su I local es alto, por eso destaca en el mapa',
            retro: 'Un barrio bajo entre altos tiene un I local NEGATIVO: su desviación y la de sus vecinos tienen signos opuestos.' },
          { texto: 'Que es significativo y forma el centro de un conglomerado de valores altos',
            retro: 'El cuadrante no dice nada de significación: eso lo decide el p del módulo 8. Y un bajo-alto es un atípico, no un conglomerado.' },
          { texto: 'Que sus vecinos tienen valores más bajos que el suyo, aunque sean altos',
            retro: 'Es al revés: los vecinos están por encima de la media y él por debajo.' }
        ] },
      {
        tipo: 'opcion',
        pista: 'Recuerda cuál es el valor de c cuando no hay nada.',
        pregunta: 'La c de Geary de un mapa vale 0.53. ¿Qué indica?',
        opciones: [
          { texto: 'Autocorrelación positiva, porque por debajo de 1 los vecinos se parecen más que por azar', correcta: true,
            retro: 'Eso es: E[c] = 1, y c va al revés que I. Es justo la c de CRIME en Columbus, ' + n7(D7.m5.columbus.c, 5) + ', con una z de ' + n7(D7.m5.columbus.z, 4) + '.' },
          { texto: 'Ausencia de autocorrelación, porque está cerca de 0.5, su valor bajo la nula',
            retro: 'El valor nulo de c es 1, no 0.5. Un 0.53 está lejos de él, del lado del parecido.' },
          { texto: 'Autocorrelación negativa: c va en el mismo sentido que I, y aquí es pequeña',
            retro: 'c va al revés que I: por eso se compara I con 1 − c. Por debajo de 1 es parecido entre vecinos.' },
          { texto: 'Que el mapa tiene un valor extremo que arrastra el índice hacia abajo',
            retro: 'Un extremo no explica un 0.53. Al dispararse un valor, c tiende a un límite que depende de la vecindad de ese barrio —en Columbus, entre ' + n7(D7.m5.limite_c_rango[0], 3) + ' y ' + n7(D7.m5.limite_c_rango[1], 3) + '—; con el barrio de mayor CRIME, c sube. Un 0.53 se lee como parecido entre vecinos.' }
        ] },
      {
        tipo: 'multiple',
        pista: 'Son dos. Piensa en hacia dónde va cada índice cuando no hay nada.',
        pregunta: 'Multiplicas por ocho el CRIME del barrio de <strong>mayor</strong> CRIME de Columbus. Marca <strong>todo</strong> lo que es cierto.',
        retroAcierto: 'Las dos: I se hunde hacia su valor nulo y c sube, cada uno por su mecanismo. Ojo: con un barrio BAJO no pasa; multiplicar por ocho un valor casi cero no es un pico.',
        retroFallo: 'Las dos ciertas son que I se acerca a su valor nulo y que c sube. El extremo no hace más parecido al barrio, y Geary también se mueve.',
        opciones: [
          { texto: 'El I de Moran se acerca a su valor nulo, aunque el barrio sea alto entre altos', correcta: true,
            retro: 'Sí: I baja de ' + n7(D7.m5.pico_en_alto.curva[0].I, 3) + ' a ' + n7(D7.m5.pico_en_alto.curva[5].I, 4) + '. El extremo entra en el denominador al cuadrado y en el numerador una sola vez.' },
          { texto: 'La c de Geary sube, hacia un valor cercano a uno', correcta: true,
            retro: 'Sí: c pasa de ' + n7(D7.m5.pico_en_alto.curva[0].c, 4) + ' a ' + n7(D7.m5.pico_en_alto.curva[5].c, 4) + '. Su numerador crece más que el denominador (' + n7(D7.m5.pico_en_alto.cocientes_8.numerador_c, 2) + ' veces frente a ' + n7(D7.m5.pico_en_alto.cocientes_8.denominador, 2) + '), porque las diferencias con los vecinos crecen al cuadrado.' },
          { texto: 'El I de Moran sube, porque el barrio pasa a ser aún más alto que sus vecinos altos',
            retro: 'Baja: el producto del barrio con sus vecinos crece como su valor, pero el denominador crece como su cuadrado.' },
          { texto: 'Solo se mueve I: Geary compara vecinos entre sí y no usa la media',
            retro: 'Geary también se mueve, y mucho: las diferencias al cuadrado con ese barrio crecen más deprisa que la varianza.' }
        ] },
      {
        tipo: 'opcion',
        pista: 'Piensa en una ciudad con un centro y una periferia distintos.',
        pregunta: 'El correlograma de Columbus es positivo en los órdenes 1 y 2 y negativo desde el 3. ¿Cuál es la lectura más razonable?',
        opciones: [
          { texto: 'Un gradiente: valores altos en una parte de la ciudad y bajos en la otra', correcta: true,
            retro: 'Eso es: a varios pasos de distancia, dos barrios suelen caer en lados opuestos de la ciudad. En el orden 5 el I es ' + n7(D7.m6.correlograma.columbus[4].I, 4) + '.' },
          { texto: 'Que los barrios lejanos se repelen y tienden a tener valores opuestos a propósito',
            retro: 'No hay repulsión: es la geometría de un gradiente. Dos barrios lejanos caen en zonas distintas de la ciudad.' },
          { texto: 'Que hay un error, porque un correlograma no puede tener valores negativos',
            retro: 'I puede ser negativo en cualquier orden. Lo que no puede es bajar de su mínimo, que fijan los valores propios de (W + Wᵀ)/2 centrada.' },
          { texto: 'Que la W está mal elegida: a larga distancia I debería valer cero',
            retro: 'A larga distancia I no tiene por qué ser cero: con un gradiente es negativo. Eso es información sobre el dato, no un defecto de W.' }
        ] },
      {
        tipo: 'opcion',
        pista: 'Piensa en qué significa un p cuando se elige mirando el p.',
        pregunta: 'Calculas el I de Moran con once W distintas y publicas solo la que da el p más pequeño. ¿Qué has hecho?',
        opciones: [
          { texto: 'Elegir la conclusión: con esa selección, el p ya no significa lo que dice', correcta: true,
            retro: 'Eso es: es la multiplicidad del módulo 10 aplicada a W. Lo honesto es elegir W antes, por una razón sustantiva, y publicar la sensibilidad.' },
          { texto: 'Lo correcto: la W que da más evidencia es la que mejor describe el dato',
            retro: 'El p no mide qué W describe mejor el dato. Elegir por él convierte el análisis en una búsqueda del resultado.' },
          { texto: 'Nada grave, porque en Columbus todas las W rechazan la hipótesis nula de todos modos',
            retro: 'Que todas rechacen no arregla publicar una sola: el I va de ' + n7(D7.m7.resumen.columbus_I[0], 4) + ' a ' + n7(D7.m7.resumen.columbus_I[1], 4) + ', y quien lee no sabe cuál de ellos tiene delante.' },
          { texto: 'Corregir la multiplicidad: se ha mirado más de una W antes de decidir',
            retro: 'Es lo contrario: mirar muchas y quedarse con la mejor es justo lo que una corrección de multiplicidad existe para penalizar.' }
        ] },
      {
        tipo: 'opcion',
        pista: 'Mira el barrio de menor p del módulo 8 antes de contestar.',
        pregunta: 'Un barrio aparece en rojo (alto-alto) en el mapa LISA sin corregir. ¿Qué puedes afirmar?',
        opciones: [
          { texto: 'Que él y su vecindad forman una configuración alto-alto rara bajo el azar', correcta: true,
            retro: 'Eso es, con dos matices: «rara» según el p elegido y sin corregir la multiplicidad, y el rojo marca el centro de la vecindad, no la zona entera.' },
          { texto: 'Que su valor está entre los más altos de todo el mapa de Columbus',
            retro: 'Alto y bajo se refieren al signo. En Columbus hay un barrio en rojo casi en la media: lo extremo es su vecindad.' },
          { texto: 'Que todos sus vecinos son también significativos y forman un conglomerado',
            retro: 'Sus vecinos tienen su propia vecindad y su propio test, y pueden salir en gris. El rojo señala centros, no zonas.' },
          { texto: 'Que su I local está entre los más grandes de todo el mapa',
            retro: 'Un I local grande no es un I local significativo, ni al revés: el de menor p de Columbus tiene un I local pequeño.' }
        ] },
      {
        tipo: 'numerica',
        pista: 'Bonferroni pide p < α/n, estrictamente menor, y el p bilateral por rangos no baja de 2/(nsim + 1).',
        pregunta: 'Con los ' + mil7(D7.m10.suelo.municipios.n) + ' municipios que tienen test y α = 0.05, ¿cuántas réplicas hacen falta como mínimo para que Bonferroni pueda declarar significativa al menos una unidad con el p bilateral por rangos? Escribe el número sin separador de miles.',
        respuesta: D7.m10.suelo.municipios.nsim_minimo, tolerancia: 0,
        retroAcierto: 'Son ' + mil7(D7.m10.suelo.municipios.nsim_minimo) + ': hace falta 2/(nsim + 1) < 0.05/' + mil7(D7.m10.suelo.municipios.n) + ', es decir, nsim + 1 mayor que ' + mil7(D7.m10.suelo.municipios.nsim_minimo) + '. Con una réplica menos el suelo iguala al umbral, y no basta. Con las 999 de GeoDa ningún municipio puede pasar, y por eso el capítulo usa ' + mil7(D7.m10.nsim) + '.',
        retroFallo: 'Son ' + mil7(D7.m10.suelo.municipios.nsim_minimo) + ', el menor nsim con 2/(nsim + 1) < α/n. Si te salió uno menos, usaste ≤ en vez de <: ahí el suelo iguala al umbral. Si te salió la mitad, usaste el suelo del p plegado, 1/(nsim + 1). Con 999 réplicas el suelo bilateral es 0.002, muy por encima del umbral de Bonferroni, ' + p7(D7.m10.suelo.municipios.umbral_bonferroni) + '.'
      },
      {
        tipo: 'opcion',
        pista: 'Piensa en qué suma Gi* y qué parte de esa suma es la propia unidad.',
        pregunta: 'Un municipio de deserción baja, rodeado de municipios de deserción alta, sale bajo-alto y significativo en LISA. ¿Cómo tiende a pintarlo el mapa de Gi*?',
        opciones: [
          { texto: 'Caliente, del color de sus vecinos, porque la suma de su vecindad es alta', correcta: true,
            retro: 'Eso es: de los ' + mil7(D7.m9.municipios.conteo[4]) + ' bajo-alto municipales, ' + mil7(D7.m11.municipios.cruce[4].caliente) + ' salen calientes contando hasta el 90 %. Gi* incluye su valor bajo, pero pesa más la vecindad: mide intensidad, no similitud.' },
          { texto: 'Frío: su propio valor es bajo, y Gi* lo incluye en la suma',
            retro: 'Su valor bajo entra en la suma, pero pesa más la vecindad: de los bajo-alto municipales, ninguno sale frío.' },
          { texto: 'Como atípico, con un color propio para «distinto de lo que le rodea»',
            retro: 'Gi* no tiene una categoría de atípico: solo calientes, fríos y no significativos.' },
          { texto: 'De ningún color: Gi* solo marca conglomerados, no unidades sueltas',
            retro: 'Gi* pinta cada unidad según la suma de su vecindad, y la de este municipio es alta: tiende a salir caliente.' }
        ] }
    ];
"""


# =====================================================================
# EL ENSAMBLADO
# =====================================================================
def reemplaza_region(texto, abre, cierra, nuevo, que, max_lineas, min_lineas=0):
    if texto.count(abre) != 1:
        sys.exit(f"PARADO: el ancla de apertura de {que} aparece {texto.count(abre)} veces")
    i = texto.index(abre)
    j = texto.find(cierra, i + len(abre))
    if j < 0:
        sys.exit(f"PARADO: no aparece el ancla de cierre de {que}")
    nl = texto[i:j + len(cierra)].count("\n")
    if nl > max_lineas:
        sys.exit(f"PARADO: la región de {que} tiene {nl} líneas y el tope es {max_lineas}")
    if nl < min_lineas:
        sys.exit(f"PARADO: la región de {que} tiene {nl} líneas y el mínimo es {min_lineas}")
    return texto[:i] + nuevo + texto[j + len(cierra):]


def sustituye(texto, ancla, nuevo, que):
    if texto.count(ancla) != 1:
        sys.exit(f"PARADO: el ancla de {que} aparece {texto.count(ancla)} veces")
    return texto.replace(ancla, nuevo)


def main() -> int:
    doc = PLANTILLA.read_text(encoding="utf-8")

    doc = sustituye(doc, "<title>Plantilla de capítulo — Estadística Espacial</title>",
                    "<title>Capítulo 7 · Autocorrelación espacial — Estadística Espacial</title>",
                    "el título")
    doc = sustituye(doc, "PLANTILLA BASE •\n              5 MÓDULOS DE DEMOSTRACIÓN • UNBOSQUE 2026-II",
                    "CAPÍTULO 7 • AUTOCORRELACIÓN ESPACIAL GLOBAL Y LOCAL •\n"
                    f"              SEMANAS {D['meta']['semanas']} • UNBOSQUE 2026-II",
                    "el subtítulo de la cabecera")
    doc = sustituye(doc, "Estadística Espacial (20929) • Plantilla de\n          capítulo • UnBosque 2026-II",
                    "Estadística Espacial (20929) • Capítulo 7 de 10 •\n"
                    f"          Semanas {D['meta']['semanas']} • UnBosque 2026-II", "el pie")

    doc = sustituye(doc, "  </style>\n", CSS_CAP7 + "  </style>\n", "los estilos del capítulo")

    doc = reemplaza_region(doc, "    const courseData = {", "\n    };\n", COURSE_DATA,
                           "courseData + DATOS_CAP7", max_lineas=20)

    doc = reemplaza_region(
        doc,
        "  <!-- ============================================================ -->\n"
        "  <!-- MÓDULO 1 · Cajas y tipografía",
        "\n  <script>", MODULOS.lstrip("\n") + "\n  <script>",
        "los módulos escritos", max_lineas=600)

    vieja = [l for l in doc.splitlines() if l.startswith("    GEOMAPAS['demo-mapa'] =")]
    if len(vieja) != 1:
        sys.exit(f"PARADO: {len(vieja)} registros de GEOMAPAS['demo-mapa'], se esperaba 1")
    doc = sustituye(doc, vieja[0], GEOMAPAS_JS.rstrip("\n"), "los .geomapa del capítulo")

    doc = reemplaza_region(doc, "    GLOSARIOS['demo-notacion'] = {", "\n    };\n",
                           "    // El glosario de notación del curso vive en el capítulo 1.\n",
                           "GLOSARIOS", max_lineas=40)

    doc = reemplaza_region(
        doc,
        "    // --- Deslizadores sobre un gráfico de línea ----------------------\n"
        "    SIMULADORES['demo-deslizadores'] = function (raiz) {",
        "    // ================================================================\n"
        "    // Autoevaluación de demostración: una pregunta de cada tipo\n",
        SIMULADORES_JS
        + "\n    // ================================================================\n"
          "    // Autoevaluación de demostración: una pregunta de cada tipo\n",
        "los simuladores de demostración", max_lineas=140, min_lineas=100)

    doc = reemplaza_region(doc, "    AUTOEVALUACIONES['demo'] = [", "\n    ];\n",
                           QUIZ_JS.lstrip("\n"), "AUTOEVALUACIONES", max_lineas=90)

    # El simulacro y la tabla de ranking de demostración se borran en vez de
    # viajar muertos (ver ensambla_cap6.py).
    doc = reemplaza_region(doc, "    SIMULACROS['demo'] = {", "\n    };\n",
                           "", "el simulacro de demostración", max_lineas=40)
    doc = reemplaza_region(doc, "    TABLAS_RANKING['demo'] = function () {", "\n    };\n",
                           "", "la tabla de ranking de demostración", max_lineas=40)

    DESTINO.parent.mkdir(parents=True, exist_ok=True)
    doc = baraja_documento(doc, "cap7")
    doc = aplica_boton(doc, DESTINO, RAIZ, "franja")
    DESTINO.write_text(doc, encoding="utf-8")

    # --- El recuento, contado y no recordado --------------------------
    marcado = doc[:doc.rindex("\n  <script>")]
    mods = doc.count('<template id="module-')
    sims = marcado.count('data-simulador="')
    mapas = marcado.count('data-geomapa="cap7-')
    bl_r = doc.count('class="language-r"')
    bl_py = doc.count('class="language-python"')
    cifras = doc.count("#&gt;")
    lienzos = marcado.count("<canvas")
    con_alt = sum(1 for c in marcado.split("<canvas")[1:] if "aria-label" in c.split(">")[0])
    kb = DESTINO.stat().st_size / 1024

    print(f"{DESTINO.relative_to(RAIZ)}  {kb:.0f} KB")
    print(f"  {mods} módulos · {sims} simuladores · {mapas} mapas · "
          f"{bl_r} bloques de R y {bl_py} de Python · {cifras} líneas #> anunciadas")
    print(f"  {lienzos} lienzos, {con_alt} con aria-label")

    problemas = []
    if con_alt != lienzos:
        problemas.append(f"lienzos sin aria-label: {lienzos - con_alt} de {lienzos}")
    if bl_r != bl_py:
        problemas.append(f"bloques descuadrados: {bl_r} de R y {bl_py} de Python")
    usados = set(re.findall(r'data-geomapa="([^"]+)"', marcado))
    registrados = set(re.findall(r"GEOMAPAS\['([^']+)'\]\s*=", doc))
    if usados - registrados:
        problemas.append(f"mapas sin registrar: {sorted(usados - registrados)}")
    sim_usados = set(re.findall(r'data-simulador="([^"]+)"', marcado))
    sim_reg = set(re.findall(r"SIMULADORES\['([^']+)'\]\s*=", doc))
    if sim_usados - sim_reg:
        problemas.append(f"simuladores sin registrar: {sorted(sim_usados - sim_reg)}")
    if "«" in "".join(re.findall(r'<code class="language-[a-z]+">(.*?)</code>', doc, re.S)) and \
            _HUECO.search("".join(re.findall(r'<code class="language-[a-z]+">(.*?)</code>', doc, re.S))):
        problemas.append("un hueco «ASÍ» se quedó sin rellenar en un bloque de código")
    if problemas:
        print("\n  PROBLEMAS:")
        for p in problemas:
            print(f"   - {p}")
        return 1

    if MODULOS_ESCRITOS < MODULOS_OBJETIVO:
        print(f"\n  EN CONSTRUCCIÓN: {MODULOS_ESCRITOS} de {MODULOS_OBJETIVO} módulos. "
              "No es publicable todavía.")
        return 1

    print("\n  Capítulo 7 ensamblado.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
