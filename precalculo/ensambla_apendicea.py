#!/usr/bin/env python3
"""
ensambla_apendicea.py — el apéndice A escrito sobre la plantilla

  «La densidad en una dimensión»
  Material de Estadística Espacial 2026-II (20929).

QUÉ HACE. Estampa `plantilla/plantilla-capitulo.html` con los trece módulos
del apéndice, sus catorce simuladores, su figura del plano, su
autoevaluación y sus diez ejercicios, y escribe
`Htmls_Espacial/apendice-a-densidad.html`.

POR QUÉ UN APÉNDICE. El capítulo 5 estima intensidades por núcleos en el
plano y usa σ, cuatro núcleos, cuatro selectores y la corrección de borde
sin la teoría de la que salen. En una dimensión todo eso se puede dibujar y
calcular a mano. El apéndice adapta un documento del profesor
(`JMS_Densidades.Rmd`, «Estadística no paramétrica · Densidades») y le
añade lo que un curso de estadística ESPACIAL necesita de él: cada módulo
cierra con un recuadro «En el plano» que dice dónde reaparece la idea en el
material.

LA REGLA QUE MANDA (D10): ninguna cifra se escribe aquí. Todas salen de
`apendicea_datos.json` o `apendicea_soluciones.json`, por un formateador. Lo
vigila `sin_aritmetica.py`, que mira el CÓDIGO: si un número se calcula
dentro de un formateador, para.

LO QUE SE CALCULA EN EL NAVEGADOR. Los simuladores con deslizador continuo
—el ancho de un histograma, el ancho de banda, k— dibujan con
`precalculo/densidad1d.js`, que se inyecta en línea y tiene su prueba contra
R (`prueba_densidad1d.py`). Las cifras de la PROSA nunca salen de ahí.

Uso:  python3 precalculo/ensambla_apendicea.py
Devuelve 1 si algo no cuadra, y lo dice.
"""
from __future__ import annotations

import json
import pathlib
import re as _re
import sys

from baraja_opciones import baraja_documento

RAIZ = pathlib.Path(__file__).resolve().parent.parent
PLANTILLA = RAIZ / "plantilla" / "plantilla-capitulo.html"
SALIDAS = RAIZ / "precalculo" / "salidas"
MOTOR = RAIZ / "precalculo" / "densidad1d.js"
DESTINO = RAIZ / "Htmls_Espacial" / "apendice-a-densidad.html"

D = json.loads((SALIDAS / "apendicea_datos.json").read_text(encoding="utf-8"))
S = json.loads((SALIDAS / "apendicea_soluciones.json").read_text(encoding="utf-8"))

m1, m2, m3, m4, m5, m6 = (D[f"m{i}"] for i in range(1, 7))
m7, m8, m9, m10, m11, m12 = (D[f"m{i}"] for i in range(7, 13))
NUC = {k["nombre"]: k for k in m6["nucleos"]}
REALES = {r["selector"]: r for r in m11["reales"]}
MC = {r["selector"]: r for r in m11["por_selector"]}
AIM = {a["selector"]: a for a in m10["aimse"]}
SEL12 = m12["selectores"]
BORDE = m12["borde"]
SIT = m4["plano"]["sitios"]
CON = m9["constantes"]


# =====================================================================
# Formateadores. NO calculan: dan forma a lo que R ya calculó.
# =====================================================================
def n(x, d=5):
    return f"{float(x):.{d}f}"


def lista(v):
    """jsonlite publica un vector de longitud 1 como escalar: aquí vuelve a ser lista."""
    return v if isinstance(v, list) else [v]


def ent(x):
    """Entero con espacio fino U+202F (no partible). NO usar dentro de KaTeX."""
    return f"{int(round(float(x))):,}".replace(",", " ")


def ent_codigo(x):
    """Entero sin separador de millares, para dentro de un bloque de código."""
    return str(int(round(float(x))))


def firma(valor, unidad=""):
    return f"<strong>{valor}</strong>{unidad}"


# El porcentaje lleva PUNTO decimal, como `n()` y como el resto del curso
# (la regla M6 del capítulo 5, que `audita_texto_apendicea.py` vigila).
def pct(x, d=1):
    return f"{float(x):.{d}f} %"


def cabecera(num, titulo, ingles, objetivo):
    plano = titulo.replace("<code>", "").replace("</code>", "")
    return f"""
  <!-- ============================================================ -->
  <!-- MÓDULO {num} · {plano[:52]:<52} -->
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


# Lo que dibuja cada lienzo, para quien no lo ve. El `aria-label` era el
# título, que no describe ejes ni series (revisión 2). Sin cifras: las cifras
# cambian con los mandos y las anuncia la lectura, que es `aria-live`.
DESCRIPCIONES = {
    "apa-area": "Histograma de densidad de los tiempos de espera de los clientes, con dos grupos de "
                "barras; las del intervalo elegido van en verde y una raya naranja marca la espera media, "
                "que cae en el hueco entre los dos grupos.",
    "apa-histograma": "Histograma de densidad de las duraciones de erupción del géiser, con el ancho y el "
                      "origen que fijan los deslizadores.",
    "apa-ash": "Dos curvas sobre las duraciones de erupción: el histograma desplazado promediado, en "
               "escalera naranja, y el estimador de núcleo triangular, discontinuo verde; al subir m se "
               "superponen.",
    "apa-ventana": "Valor esperado del estimador ingenuo en el centro de una normal, en función del ancho "
                   "de la ventana en escala logarítmica, con una banda de dos desviaciones típicas y la "
                   "densidad verdadera como línea horizontal discontinua.",
    "apa-lomas": "Cinco lomas gaussianas finas, una sobre cada dato, y su suma gruesa en verde, que es la "
                 "densidad estimada; los datos son puntos sobre el eje.",
    "apa-nucleos": "Estimación de la muestra trimodal con el núcleo elegido, en verde, sobre la estimación "
                   "gaussiana de referencia, en gris.",
    "apa-knn": "Estimación con k vecinos de una mezcla de dos normales, en verde y llena de picos, junto a "
               "la densidad verdadera discontinua.",
    "apa-nube": "Treinta estimaciones gaussianas finas en gris, una por muestra, con el valor esperado "
                "exacto en verde y la densidad verdadera discontinua.",
    "apa-ecm": "Sesgo al cuadrado, varianza y su suma, el error cuadrático medio en el centro, en función "
               "del ancho, junto al error integrado de toda la curva, discontinuo.",
    "apa-selectores": "Estimación gaussiana de las duraciones de erupción con el ancho del selector elegido.",
    "apa-cv": "Los criterios de validación cruzada UCV, en azul, y LCV, en naranja, en función del ancho, "
              "con su óptimo marcado; un botón los recalcula sin la erupción más aislada.",
    "apa-mc": "Nube de puntos, uno por muestra simulada: el error integrado de bw.SJ en el eje horizontal "
              "contra el del selector elegido en el vertical, con la diagonal y la línea del doble.",
    "apa-borde": "Estimaciones de la densidad de las distancias de cada sede a la más cercana, sin corregir "
                 "y con tres correcciones de borde, junto a la densidad bajo CSR, que arranca en cero.",
    "apa-empates": "Estimación gaussiana de las distancias al vecino con el ancho elegido: con el más pequeño, "
                   "un peine de picos; con el otro, una curva lisa.",
}


def sim(ident, titulo, pie="", alto=280, mandos=True):
    """Un componente con su lienzo, su lectura y —si los tiene— sus mandos."""
    if ident not in DESCRIPCIONES:
        sys.exit(f"PARADO: el simulador {ident} no tiene descripción para su lienzo")
    icono = "fa-sliders" if mandos else "fa-chart-column"
    return f"""      <div class="simulador" data-simulador="{ident}">
        <h4><i class="fas {icono}" aria-hidden="true"></i> {titulo}</h4>
        {f'<p class="simulador-intro">{pie}</p>' if pie else ''}
{'        <div class="simulador-controles"></div>' + chr(10) if mandos else ''}        <div class="grafico-wrapper" style="height:{alto}px;">
          <canvas role="img" aria-label="{DESCRIPCIONES[ident]}"></canvas>
        </div>
        <div class="simulador-lectura" aria-live="polite"></div>
      </div>
"""


def fila(*celdas):
    cab, resto = celdas[0], celdas[1:]
    return ('            <tr><th scope="row">' + str(cab) + '</th>'
            + ''.join('<td>' + str(c) + '</td>' for c in resto) + '</tr>\n')


def tabla(cabeceras, filas, pie=""):
    th = "".join(f'<th scope="col">{c}</th>' for c in cabeceras)
    cap = f"\n          <caption>{pie}</caption>" if pie else ""
    return (f'      <table>{cap}\n'
            f'          <thead><tr>{th}</tr></thead>\n'
            '          <tbody>\n' + filas +
            '          </tbody>\n      </table>\n')


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


def en_el_plano(cuerpo):
    """El recuadro que cierra cada módulo: dónde reaparece la idea en el plano."""
    return f"""      <div class="tip-box">
        <h4><i class="fas fa-map-location-dot mr-2" aria-hidden="true"></i>En el plano</h4>
{cuerpo}
      </div>
"""


def como_se_lee(cuerpo):
    return f"""      <div class="definition">
        <h4><i class="fas fa-glasses mr-2" aria-hidden="true"></i>Cómo se lee</h4>
{cuerpo}
      </div>
"""


def trampa(titulo, cuerpo):
    return f"""      <div class="warning">
        <p><strong>Trampa: {titulo}.</strong> {cuerpo}</p>
      </div>
"""


def derivacion(ident, rotulo, pasos, resultado):
    lis = "".join(f"            <li>\n{p}\n            </li>\n" for p in pasos)
    return f"""      <div class="derivacion">
        <button type="button" class="derivacion-boton" aria-expanded="false" aria-controls="{ident}">
          <i class="fas fa-square-root-variable" aria-hidden="true"></i>
          <span class="derivacion-texto">{rotulo}</span>
          <i class="fas fa-chevron-down" aria-hidden="true"></i>
        </button>
        <div class="derivacion-panel" id="{ident}" hidden>
          <ol class="derivacion-pasos">
{lis}          </ol>
          <p class="derivacion-resultado">{resultado}</p>
        </div>
      </div>
"""


# LOS TÍTULOS SE ESCRIBEN EN HTML, NO EN MARKDOWN (la lección del módulo 9
# del capítulo 5): el índice lateral los pinta con `innerHTML`.
TITULOS = (
    ("Densidad e intensidad", "El área es la probabilidad"),
    ("El histograma", "Un estimador con dos perillas"),
    ("Promediar los orígenes", "El histograma desplazado promediado"),
    ("Contar en una ventana", "La idea que une a todos: k / (nV)"),
    ("El estimador de núcleo", "Una loma por cada dato"),
    ("La forma y la escala del núcleo", "Cuál importa y cuál no"),
    ("<em>k</em> vecinos", "El radio que se adapta"),
    ("Sesgo, varianza y error integrado", "Lo que el ancho de banda negocia"),
    ("Reglas de referencia", "Silverman, Scott y la que es de otro"),
    ("Validación cruzada", "Elegir h con los datos"),
    ("Una verdad conocida", "Qué selector acierta, y cuántas veces"),
    ("Del renglón al plano", "Las distancias entre las sedes de Bogotá"),
    ("Autoevaluación y ejercicios", "Diecisiete preguntas y diez ejercicios"),
)
INGLES = (
    "Density and intensity", "The histogram", "Averaged shifted histograms",
    "Counting in a window", "The kernel estimator", "Kernel shape and scale",
    "k nearest neighbours", "Bias, variance and integrated error",
    "Reference rules", "Cross-validation", "A known truth",
    "From the line to the plane", "Self-assessment and guided exercises",
)


# =====================================================================
# LOS BLOQUES DE CÓDIGO VAN APARTE DE LA PROSA, y se escriben en claro: el
# escapado HTML lo hace `esc()` al publicarlos. Los `#>` se rellenan con
# `.format()` desde el JSON; ninguno se escribe a mano, y
# `verifica_bloques.py` los ejecuta para comprobarlo.
#
# CADA BLOQUE ES AUTÓNOMO y fija su propia semilla. No es estilo:
# `verifica_bloques.py --todos` encadena UNA sesión de R para todos los
# documentos, y `apendice-…` va antes que `capitulo-1`. Un objeto que este
# apéndice dejara vivo llegaría a los bloques de los capítulos.
# =====================================================================
import html as _html


def esc(codigo):
    return _html.escape(codigo, quote=False)


def nz(x, d=4):
    """Una cifra de una línea `#>`: redondeada y SIN los ceros finales.

    R y numpy no escriben los ceros finales de un número suelto (5.809, no
    5.8090) y R sí los escribe cuando alinea un vector (0.1250). La cifra sin
    ceros está contenida en las dos formas, y `verifica_bloques.py` acepta la
    subcadena: así una misma `#>` vale para las dos pestañas.
    """
    t = n(x, d)
    if "." in t:
        t = t.rstrip("0").rstrip(".")
    return "0" if t in ("-0", "") else t


def vec(xs, d):
    """Una lista de cifras como la imprime R (separadas por espacio)."""
    return " ".join(nz(x, d) for x in xs)


def vec_py(xs, d):
    return ", ".join(nz(x, d) for x in xs)


R1 = '''# La cafetería: dos tipos de pedido en la hora pico
set.seed({SEMILLA})
bebidas <- rnorm({N1}, mean = {MU1}, sd = {SD1})   # solo bebida: rápidos
comidas <- rnorm({N2}, mean = {MU2}, sd = {SD2})   # con comida: lentos
tiempos <- c(bebidas, comidas)

round(mean(tiempos), 4)
#> [1] {MEDIA}

# Histograma de DENSIDAD: altura = conteo / (n · ancho). El área total es 1.
barras <- hist(tiempos, breaks = seq({DESDE}, {HASTA}, by = 1), right = FALSE, plot = FALSE)
barras$counts
#> [1] {CONTEOS}
sum(barras$density * diff(barras$breaks))
#> [1] 1

# La media cae en una barra vacía: el resumen vive donde no hay datos
barras$counts[findInterval(mean(tiempos), barras$breaks)]
#> [1] {EN_MEDIA}'''

PY1 = '''import numpy as np
import pandas as pd

# R y numpy no comparten generador aleatorio: Python lee la MISMA muestra
t = pd.read_csv("precalculo/salidas/apendicea_cafeteria.csv")["tiempo"].to_numpy()
print(round(t.mean(), 4))
#> {MEDIA}

cortes = np.arange({DESDE}, {HASTA} + 1)          # intervalos [a, a + 1)
conteos, _ = np.histogram(t, bins=cortes)
print(conteos.tolist())
#> [{CONTEOS_PY}]
densidad = conteos / (len(t) * 1)                   # alto = conteo / (n · ancho)
print(round(float((densidad * 1).sum()), 4))
#> 1.0

print(conteos[np.searchsorted(cortes, t.mean(), side="right") - 1])
#> {EN_MEDIA}'''

R2 = '''x <- faithful$eruptions                 # 272 erupciones del géiser, en minutos

# Lo que R hace sin que se le pida nada: Sturges propone, pretty() decide
nclass.Sturges(x)
#> [1] {STURGES}
length(hist(x, plot = FALSE)$counts)
#> [1] {DEF}

# Un histograma con ancho h y el origen corrido `desplaza` minutos
histo <- function(x, h, desplaza) {{
  a <- floor((min(x) - desplaza) / h) * h + desplaza
  cortes <- a + h * 0:(floor((max(x) - a) / h) + 1)
  hist(x, breaks = cortes, right = FALSE, plot = FALSE)$density
}}
# Una moda: una meseta más alta que sus dos vecinas
modas <- function(y) {{
  r <- rle(y)$values
  sum(r > c(0, head(r, -1)) & r > c(tail(r, -1), 0))
}}

# Mismo ancho, dos orígenes: el dato no cambió y las modas sí
modas(histo(x, {H}, {D_MUCHAS}))
#> [1] {MODAS_MUCHAS}
modas(histo(x, {H}, {D_POCAS}))
#> [1] {MODAS_POCAS}

# Las dos reglas de ancho pensadas para el histograma (tasa n^(-1/3))
round(c(FD = 2 * IQR(x), Scott = 3.5 * sd(x)) * length(x)^(-1/3), 4)
#> FD {FD} Scott {SCOTT}'''

PY2 = '''import numpy as np
import pandas as pd

x = pd.read_csv("precalculo/salidas/apendicea_faithful.csv")["eruptions"].to_numpy()

# numpy aplica Sturges tal cual; R lo redondea con pretty()
print(len(np.histogram_bin_edges(x, bins="sturges")) - 1)
#> {STURGES}

def histo(x, h, desplaza):
    a = np.floor((min(x) - desplaza) / h) * h + desplaza
    k = int(np.floor((max(x) - a) / h)) + 1
    # R corre los cortes 1e-7·h hacia abajo antes de contar. Sin esa
    # tolerancia, un dato que cae justo en un corte (1.75 con h = 0.25)
    # se va a veces a la casilla de abajo por el redondeo binario.
    i = np.floor((x - a) / h + 1e-7).astype(int)
    return np.bincount(i, minlength=k) / (len(x) * h)

def modas(y):
    r = [v for j, v in enumerate(y) if j == 0 or v != y[j - 1]]
    izq, der = [0] + r[:-1], r[1:] + [0]
    return sum(a > b and a > c for a, b, c in zip(r, izq, der))

print(modas(histo(x, {H}, {D_MUCHAS})), modas(histo(x, {H}, {D_POCAS})))
#> {MODAS_MUCHAS} {MODAS_POCAS}

q75, q25 = np.percentile(x, [75, 25])
print(round(2 * (q75 - q25) * len(x) ** (-1 / 3), 4), round(3.5 * x.std(ddof=1) * len(x) ** (-1 / 3), 4))
#> {FD} {SCOTT}'''

R3 = '''# El ASH: m histogramas de ancho h, desplazados h/m, promediados en
# los MISMOS puntos g. La malla se EXTIENDE un h por cada lado: si no,
# los histogramas desplazados pierden los datos de los extremos.
ash <- function(x, h, m, g) {{
  d <- h / m
  malla <- seq(min(x) - h, max(x) + h + d, by = h)
  f <- numeric(length(g))
  for (j in 0:(m - 1)) {{
    b <- malla + j * d
    cnt <- hist(x, breaks = b, right = FALSE, include.lowest = TRUE, plot = FALSE)$counts
    i <- findInterval(g, b)
    dentro <- i >= 1 & i <= length(cnt)
    f[dentro] <- f[dentro] + cnt[i[dentro]]
  }}
  f / (m * length(x) * h)
}}

# El ejemplo a mano: ocho datos, h = 2, m = 3
round(ash(c(2, 3, 3, 5, 7, 8, 9, 10), h = 2, m = 3, g = c(3, 5, 7, 9)), 4)
#> [1] {F_ASH}

# Con m grande el ASH ES un núcleo triangular de semiancho h
e <- faithful$eruptions
g <- seq(min(e) - 1, max(e) + 1, by = 0.005)
tri <- sapply(g, function(t) mean(pmax(0, 1 - abs((t - e) / {HT}))) / {HT})
round(sapply(c({MS}), function(m) max(abs(ash(e, {HT}, m, g) - tri))), 4)
#> [1] {DIST}'''

PY3 = '''import numpy as np
import pandas as pd

def ash(x, h, m, g):
    x, g = np.asarray(x, float), np.asarray(g, float)
    d = h / m
    malla = np.arange(x.min() - h, x.max() + h + d + 1e-12, h)
    f = np.zeros_like(g)
    for j in range(m):
        b = malla + j * d
        cnt = np.bincount(np.floor((x - b[0]) / h + 1e-7).astype(int), minlength=len(b) - 1)
        i = np.searchsorted(b, g, side="right")        # findInterval() de R
        dentro = (i >= 1) & (i <= len(b) - 1)
        f[dentro] += cnt[i[dentro] - 1]
    return f / (m * len(x) * h)

print(np.round(ash([2, 3, 3, 5, 7, 8, 9, 10], 2, 3, [3, 5, 7, 9]), 4))
#> [{F_ASH}]

e = pd.read_csv("precalculo/salidas/apendicea_faithful.csv")["eruptions"].to_numpy()
g = np.arange(e.min() - 1, e.max() + 1 + 1e-9, 0.005)
tri = np.array([np.maximum(0, 1 - np.abs((t - e) / {HT})).mean() / {HT} for t in g])
print([round(float(np.abs(ash(e, {HT}, m, g) - tri).max()), 4) for m in ({MS})])
#> [{DIST_PY}]'''

R4 = '''# El estimador ingenuo k/(nV) en x = 0, con datos N(0, 1) y n = 100.
# El número de datos en la ventana es binomial: no hace falta simular.
n <- {N}
V <- c({VS})                              # anchos de la ventana
p <- pnorm(V / 2) - pnorm(-V / 2)          # P(un dato cae dentro)
round(p / V, 4)                            # E[k/(nV)]: el centro de la nube
#> [1] {MEDIAS}
round(sqrt(p * (1 - p) / n) / V, 4)        # su desviación típica
#> [1] {SDS}
round((1 - p)^n, 4)                        # P(la ventana no encierra a nadie)
#> [1] {VACIAS}
round(dnorm(0), 4)                         # la verdad
#> [1] {F0}'''

PY4 = '''import numpy as np
from scipy.stats import norm

n = {N}
V = np.array([{VS_PY}])
p = norm.cdf(V / 2) - norm.cdf(-V / 2)
print(np.round(p / V, 4))
#> [{MEDIAS}]
print(np.round(np.sqrt(p * (1 - p) / n) / V, 4))
#> [{SDS}]
print(np.round((1 - p) ** n, 4))
#> [{VACIAS}]
print(round(norm.pdf(0), 4))
#> {F0}'''

R5 = '''# Ventanas de Parzen: una función K centrada en cada dato, de ancho h
f_hat <- function(x, datos, h, K) sapply(x, function(t) mean(K((t - datos) / h)) / h)
K_caja <- function(u) ifelse(abs(u) <= 1, 0.5, 0)

f_hat(1:5, datos = 1:5, h = 1, K_caja)    # en el borde la ventana recoge menos
#> [1] {UNIF}

Y <- c(2, 3, 4, 5, 7)
round(dnorm(4 - Y), 4)                     # los cinco sumandos en x = 4, con h = 1
#> [1] {TERM}
round(f_hat(4, Y, h = 1, dnorm), 4)        # su promedio
#> [1] {F4}

modas <- function(y) {{ r <- rle(y)$values; sum(r > c(0, head(r, -1)) & r > c(tail(r, -1), 0)) }}
g <- seq(-1, 11, length.out = 500)
sapply(c({HM}), function(h) modas(f_hat(g, Y, h, dnorm)))
#> [1] {MODAS}'''

PY5 = '''import numpy as np
from scipy.stats import norm

def f_hat(x, datos, h, K):
    x, datos = np.atleast_1d(x)[:, None], np.asarray(datos, float)[None, :]
    return K((x - datos) / h).mean(axis=1) / h

caja = lambda u: np.where(np.abs(u) <= 1, 0.5, 0.0)
print(f_hat(np.arange(1, 6), np.arange(1, 6), 1, caja))
#> [{UNIF_PY}]

Y = [2, 3, 4, 5, 7]
print(np.round(norm.pdf(4 - np.array(Y)), 4))
#> [{TERM}]
print(round(float(f_hat(4, Y, 1, norm.pdf)[0]), 4))
#> {F4}

def modas(y):
    r = [v for j, v in enumerate(y) if j == 0 or v != y[j - 1]]
    return sum(a > b and a > c for a, b, c in zip(r, [0] + r[:-1], r[1:] + [0]))

g = np.linspace(-1, 11, 500)
print([int(modas(list(f_hat(g, Y, h, norm.pdf)))) for h in ({HM})])
#> [{MODAS_PY}]'''

R6 = '''# Las constantes de cada núcleo, integrando (soporte [-1, 1])
K <- list(epanechnikov = function(u) ifelse(abs(u) <= 1, 0.75 * (1 - u^2), 0),
          uniforme     = function(u) ifelse(abs(u) <= 1, 0.5, 0),
          gaussiano    = dnorm)
lim <- c(1, 1, Inf)
mu2 <- mapply(function(k, l) integrate(function(u) u^2 * k(u), -l, l)$value, K, lim)
RK  <- mapply(function(k, l) integrate(function(u) k(u)^2, -l, l)$value, K, lim)
round(RK[1] * sqrt(mu2[1]) / (RK * sqrt(mu2)), 4)   # eficiencia contra el Epanechnikov
#> epanechnikov     uniforme    gaussiano
#> {EF_E} {EF_U} {EF_G}

# density() mide el ancho como DESVIACIÓN TÍPICA del núcleo: con bw = 1 el
# Epanechnikov no acaba en 1 sino en √5, y en x = 2 todavía pesa
d <- density(0, bw = 1, kernel = "epanechnikov", n = 8192, from = -3, to = 3)
round(approx(d$x, d$y, xout = 2)$y, 4)
#> [1] {EPA2}'''

PY6 = '''import numpy as np
from scipy.integrate import quad
from scipy.stats import norm
from sklearn.neighbors import KernelDensity

K = {{"epanechnikov": (lambda u: 0.75 * (1 - u**2), 1),
      "uniforme": (lambda u: 0.5, 1),
      "gaussiano": (norm.pdf, np.inf)}}
mu2 = {{k: quad(lambda u: u**2 * f(u), -l, l)[0] for k, (f, l) in K.items()}}
RK = {{k: quad(lambda u: f(u)**2, -l, l)[0] for k, (f, l) in K.items()}}
ref = RK["epanechnikov"] * np.sqrt(mu2["epanechnikov"])
print({{k: round(float(ref / (RK[k] * np.sqrt(mu2[k]))), 4) for k in K}})
#> {{'epanechnikov': {EF_E}, 'uniforme': {EF_U}, 'gaussiano': {EF_G}}}

# En sklearn `bandwidth` es el RADIO del soporte, no la desviación típica:
# con bandwidth = 1 el Epanechnikov ya no pesa nada en x = 2...
kd = KernelDensity(kernel="epanechnikov", bandwidth=1).fit([[0]])
print(round(float(np.exp(kd.score_samples([[2]]))[0]), 4))
#> 0.0
# ...y para tener el núcleo de R hay que pasarle √5 · bw
kd = KernelDensity(kernel="epanechnikov", bandwidth=np.sqrt(5)).fit([[0]])
print(round(float(np.exp(kd.score_samples([[2]]))[0]), 4))
#> {EPA2}'''

R7 = '''# k vecinos: fijar k y dejar que la ventana crezca hasta encerrarlos
X <- c(20, 23, 25, 29, 31, 35, 40); x0 <- 30; k <- 3
d <- sort(abs(X - x0)); d
#> [1] {DIST}
k / (2 * length(X) * d[k])                 # f = k / (n · 2 d_k)
#> [1] {FK}
sum(abs(X - x0) <= d[k])                   # hay un empate: la ventana encierra más
#> [1] {DENTRO}

# El área del k-NN no es 1, y crece sin tope al ensanchar la ventana:
# sus colas decaen como 1/|x| y esa integral no converge.
# (La función se llama area_knn y no area: spatstat ya tiene una area(),
# y taparla rompería cualquier código que la use después.)
ing <- c({ING})
knn <- function(t) 3 / (2 * length(ing) * sort(abs(ing - t))[3])
area_knn <- function(a, b) {{
  g <- seq(a, b, length.out = 20001); y <- sapply(g, knn)
  sum(diff(g) * (head(y, -1) + tail(y, -1)) / 2)
}}
round(c(area_knn({A1}), area_knn({A2}), area_knn({A3})), 4)
#> [1] {AREAS}'''

PY7 = '''import numpy as np

X = np.array([20, 23, 25, 29, 31, 35, 40]); x0, k = 30, 3
d = np.sort(np.abs(X - x0)); print(d.tolist())
#> [{DIST_PY}]
print(k / (2 * len(X) * d[k - 1]))
#> {FK}
print(int((np.abs(X - x0) <= d[k - 1]).sum()))
#> {DENTRO}

ing = np.array([{ING_PY}])
def knn(t):
    return 3 / (2 * len(ing) * np.sort(np.abs(ing - t))[2])
def area(a, b):
    g = np.linspace(a, b, 20001); y = np.array([knn(t) for t in g])
    return float(np.sum(np.diff(g) * (y[:-1] + y[1:]) / 2))
print([round(area({A1}), 4), round(area({A2}), 4), round(area({A3}), 4)])
#> [{AREAS_PY}]'''

R8 = '''# Datos N(0, 1), n = 100 y núcleo gaussiano: el ECM tiene forma cerrada
n <- {N}
h <- seq(0.05, 1.5, by = 0.01)
media <- dnorm(0, 0, sqrt(1 + h^2))                       # E f̂(0)
varianza <- (dnorm(0, 0, sqrt(1 + h^2 / 2)) / (2 * sqrt(pi) * h) - media^2) / n
ecm <- (media - dnorm(0))^2 + varianza
h[which.min(ecm)]                          # el mejor h para el punto x = 0
#> [1] {H_ECM}
round((4 / (3 * n))^(1 / 5), 4)            # el que minimiza el error INTEGRADO aproximado
#> [1] {H_AMISE}
mise <- function(h) (1 / (2 * sqrt(pi))) *
  (1 / (n * h) + (1 - 1 / n) / sqrt(1 + h^2) - 2^(3 / 2) / sqrt(2 + h^2) + 1)
round(optimize(mise, c(0.05, 1.5), tol = 1e-10)$minimum, 4)   # el del exacto
#> [1] {H_MISE}'''

PY8 = '''import numpy as np
from scipy.optimize import minimize_scalar
from scipy.stats import norm

n = {N}
h = np.round(np.arange(0.05, 1.5 + 1e-9, 0.01), 2)
media = norm.pdf(0, 0, np.sqrt(1 + h**2))
varianza = (norm.pdf(0, 0, np.sqrt(1 + h**2 / 2)) / (2 * np.sqrt(np.pi) * h) - media**2) / n
ecm = (media - norm.pdf(0))**2 + varianza
print(h[np.argmin(ecm)])
#> {H_ECM}
print(round((4 / (3 * n)) ** (1 / 5), 4))
#> {H_AMISE}
mise = lambda h: (1 / (n * h) + (1 - 1 / n) / np.sqrt(1 + h**2)
                  - 2**1.5 / np.sqrt(2 + h**2) + 1) / (2 * np.sqrt(np.pi))
print(round(minimize_scalar(mise, bounds=(0.05, 1.5), method="bounded",
                            options={{"xatol": 1e-10}}).x, 4))
#> {H_MISE}'''

R9 = '''x <- faithful$eruptions; n <- length(x)
round(c(sd = sd(x), IQR_1.34 = IQR(x) / 1.34), 4)   # manda el menor
#> {SD} {IQR134}
round(c(nrd0 = bw.nrd0(x), nrd = bw.nrd(x), histograma = 3.5 * sd(x) * n^(-1/3)), 4)
#> nrd0 {NRD0} nrd {NRD} histograma {HIST}

# El σ del plano: bw.scott de spatstat ES la regla de referencia normal en
# d = 2 —el factor (4/(d+2))^(1/(d+4)) vale 1— con la tasa n^(-1/6)
library(spatstat)
s <- read.csv("precalculo/salidas/cap5_bogota_urbana.csv")
X <- suppressWarnings(ppp(s$x, s$y, window = owin(range(s$x), range(s$y))))  # hay sedes repetidas
round(bw.scott(X), 2)
#>  sigma.x  sigma.y
#> {SCX} {SCY}
round(sd(s$x) * nrow(s)^(-1/6), 2)
#> [1] {SCX}'''

PY9 = '''import numpy as np
import pandas as pd
from scipy.spatial import cKDTree
from scipy.stats import gaussian_kde

x = pd.read_csv("precalculo/salidas/apendicea_faithful.csv")["eruptions"].to_numpy()
n, sd = len(x), x.std(ddof=1)
iqr = np.subtract(*np.percentile(x, [75, 25]))
print(round(0.9 * min(sd, iqr / 1.34) * n ** -0.2, 4), round(1.06 * min(sd, iqr / 1.34) * n ** -0.2, 4))
#> {NRD0} {NRD}

# El «silverman» de scipy NO es bw.nrd0: usa la sd y nunca el IQR.
# En las distancias al vecino de las sedes —cola larga— se nota.
s = pd.read_csv("precalculo/salidas/cap5_bogota_urbana.csv")
xy = s[["x", "y"]].to_numpy()
nn = cKDTree(xy).query(xy, k=2)[0][:, 1]            # k=2: el primero es la propia sede
kde = gaussian_kde(nn, bw_method="silverman")
q = np.subtract(*np.percentile(nn, [75, 25]))
print(round(kde.factor * nn.std(ddof=1), 2), round(0.9 * min(nn.std(ddof=1), q / 1.34) * len(nn) ** -0.2, 2))
#> {SCIPY} {NN_NRD0}'''

R10 = '''x <- faithful$eruptions; n <- length(x)
dif <- outer(x, x, "-")   # no D: es la derivada simbólica de R
# El estimador DEJANDO UNO FUERA, evaluado en cada dato
loo <- function(h) {{ W <- dnorm(dif / h); diag(W) <- 0; rowSums(W) / ((n - 1) * h) }}
# UCV: ∫ f̂² − (2/n) Σ f̂₋ᵢ(xᵢ), que se MINIMIZA
ucv <- function(h) sum(dnorm(dif / (sqrt(2) * h))) / (n^2 * h * sqrt(2)) - 2 * mean(loo(h))
# LCV: la log-verosimilitud dejando uno fuera, que se MAXIMIZA
lcv <- function(h) mean(log(loo(h)))
hh <- seq(0.02, 0.60, by = 0.002)
c(UCV = hh[which.min(sapply(hh, ucv))], LCV = hh[which.max(sapply(hh, lcv))])
#>   UCV   LCV
#> {HU} {HL}

# Lo que hace R por dentro, con las distancias agrupadas en 1000 casillas
round(c(ucv = bw.ucv(x), bcv = bw.bcv(x), SJ = bw.SJ(x)), 4)
#>    ucv    bcv     SJ
#> {UCV} {BCV} {SJ}'''

PY10 = '''import numpy as np
import pandas as pd
from scipy.stats import norm

x = pd.read_csv("precalculo/salidas/apendicea_faithful.csv")["eruptions"].to_numpy()
n = len(x)
D = x[:, None] - x[None, :]

def loo(h):
    W = norm.pdf(D / h); np.fill_diagonal(W, 0)
    return W.sum(axis=1) / ((n - 1) * h)

def ucv(h):
    return norm.pdf(D / (np.sqrt(2) * h)).sum() / (n**2 * h * np.sqrt(2)) - 2 * loo(h).mean()

def lcv(h):
    return np.log(loo(h)).mean()

hh = np.round(np.arange(0.02, 0.60 + 1e-9, 0.002), 3)
print(hh[np.argmin([ucv(h) for h in hh])], hh[np.argmax([lcv(h) for h in hh])])
#> {HU} {HL}
# Ni scipy ni statsmodels traen el selector de Sheather y Jones: el ISJ de
# KDEpy es otro método. La comparación con bw.SJ se hace en R.'''

R11 = '''# La «verdad»: una mezcla de dos normales ajustada a faithful por EM
x <- faithful$eruptions; n <- length(x)
em <- function(y, mu, s, p) {{
  ll0 <- -Inf
  repeat {{
    w <- p * dnorm(y, mu[1], s[1]); w <- w / (w + (1 - p) * dnorm(y, mu[2], s[2]))
    p <- mean(w); mu <- c(sum(w * y) / sum(w), sum((1 - w) * y) / sum(1 - w))
    s <- sqrt(c(sum(w * (y - mu[1])^2) / sum(w), sum((1 - w) * (y - mu[2])^2) / sum(1 - w)))
    ll <- sum(log(p * dnorm(y, mu[1], s[1]) + (1 - p) * dnorm(y, mu[2], s[2])))
    if (ll - ll0 < 1e-12) break       # se para cuando la verosimilitud deja de subir
    ll0 <- ll
  }}
  list(p = p, mu = mu, s = s)
}}
a <- em(x, mu = c(2, 4.3), s = c(0.25, 0.35), p = 0.5)
round(c(a$p, a$mu, a$s), 4)
#> [1] {EM}

# 1000 muestras de esa mezcla; en cada una, el ISE de cada selector
verdad <- function(z) a$p * dnorm(z, a$mu[1], a$s[1]) + (1 - a$p) * dnorm(z, a$mu[2], a$s[2])
gz <- seq(-1, 8, by = 0.01); gv <- verdad(gz)
sel <- list(nrd0 = bw.nrd0, nrd = bw.nrd, ucv = bw.ucv, bcv = bw.bcv, SJ = bw.SJ)
set.seed({SEMILLA})
ISE <- t(replicate(1000, {{
  y <- ifelse(runif(n) < a$p, rnorm(n, a$mu[1], a$s[1]), rnorm(n, a$mu[2], a$s[2]))
  sapply(sel, function(f) {{
    h <- suppressWarnings(f(y))
    sum((density(y, bw = h, n = length(gz), from = -1, to = 8)$y - gv)^2) * diff(gz)[1]
  }})
}}))
round(100 * table(factor(names(sel)[apply(ISE, 1, which.min)], names(sel))) / 1000, 1)
#> nrd0  nrd  ucv  bcv   SJ
#> {GANA}
round(100 * colMeans(ISE > 2 * ISE[, "SJ"]), 1)     # perder por mucho: el doble que SJ
#> nrd0  nrd  ucv  bcv   SJ
#> {COLA}'''

PY11 = '''import numpy as np
import pandas as pd

# Las 1000 réplicas viajan en un CSV: numpy no puede repetir el azar de R
mc = pd.read_csv("precalculo/salidas/apendicea_mc.csv")
sel = ["nrd0", "nrd", "ucv", "bcv", "SJ"]
ise = mc[[f"ise_{{s}}" for s in sel]].to_numpy()
gana = np.bincount(ise.argmin(axis=1), minlength=5) / len(ise) * 100
print(dict(zip(sel, np.round(gana, 1).tolist())))
#> {{{GANA_PY}}}
cola = (ise > 2 * ise[:, [4]]).mean(axis=0) * 100
print(dict(zip(sel, np.round(cola, 1).tolist())))
#> {{{COLA_PY}}}
print(np.round(ise.mean(axis=0), 5).tolist())      # el MISE de cada selector
#> [{MISE_PY}]'''

R12 = '''library(spatstat)
s <- read.csv("precalculo/salidas/cap5_bogota_urbana.csv")
nn <- nndist(s$x, s$y)              # la distancia de cada sede a la más cercana
quien <- nnwhich(s$x, s$y)          # y quién es esa vecina
sum(nn == 0)                        # sedes que comparten dirección
#> [1] {CEROS}
round(100 * mean(quien[quien] == seq_along(quien)), 1)   # vecinas recíprocas, en %
#> [1] {RECIP}

# Con todas las distancias la UCV se hunde, y R avisa: el mínimo está en el borde.
# El aviso es el único que lo delata, así que no se silencia.
round(c(ucv = bw.ucv(nn), SJ = bw.SJ(nn)), 2)
#>   ucv    SJ
#> {UCV_T} {SJ_T}
#> Warning message:
#> In bw.ucv(nn) : minimum occurred at one end of the range
# Una distancia por pareja recíproca y sin los ceros: los empates se van
par0 <- nn[!(quien[quien] == seq_along(quien)) | seq_along(quien) < quien]
par0 <- par0[par0 > 0]
round(c(ucv = bw.ucv(par0), SJ = bw.SJ(par0)), 2)
#>   ucv    SJ
#> {UCV_P} {SJ_P}

# El borde en r = 0: la masa que el núcleo deja en distancias negativas
h <- bw.SJ(par0)
round(100 * mean(pnorm(-nn / h)), 2)
#> [1] {MASA_NEG}'''

PY12 = '''import numpy as np
import pandas as pd
from scipy.spatial import cKDTree
from scipy.stats import norm

s = pd.read_csv("precalculo/salidas/cap5_bogota_urbana.csv")
xy = s[["x", "y"]].to_numpy()
d, j = cKDTree(xy).query(xy, k=4)
# Entre sedes que comparten dirección hay que elegir vecina, y spatstat elige
# la de índice MAYOR. Con otro desempate el porcentaje de recíprocas cambia
# (con el de cKDTree sale 59.5): es una convención, y hay que escribirla.
nn, q = np.empty(len(xy)), np.empty(len(xy), int)
for i in range(len(xy)):
    otras = [(dd, jj) for dd, jj in zip(d[i], j[i]) if jj != i]
    nn[i] = min(dd for dd, _ in otras)
    q[i] = max(jj for dd, jj in otras if dd == nn[i])
print(int((nn == 0).sum()), round(100 * float((q[q] == np.arange(len(q))).mean()), 1))
#> {CEROS} {RECIP}

# Parejas empatadas: el criterio UCV se va a −∞ cuando superan el umbral
def empates(v):
    _, c = np.unique(np.round(v, 6), return_counts=True)
    return int((c * (c - 1) // 2).sum())
umbral = (1 / (2 * np.sqrt(np.pi))) / (4 * norm.pdf(0) - 2 / (2 * np.sqrt(np.pi)))
print(round(empates(nn) / len(nn), 4), round(umbral, 4))
#> {E_T} {UMBRAL}

def ucv_exacta(v, h):                     # el criterio sin agrupar, con h minúsculo
    n = len(v); D = v[:, None] - v[None, :]
    W = norm.pdf(D / h); np.fill_diagonal(W, 0)
    return norm.pdf(D / (np.sqrt(2) * h)).sum() / (n**2 * h * np.sqrt(2)) - 2 * (W.sum(1) / ((n - 1) * h)).mean()
print(round(ucv_exacta(nn, 0.001), 4))
#> {UCVX_T}'''


SUB1 = dict(SEMILLA=ent_codigo(D["meta"]["semilla"]),
            N1=ent_codigo(m1["diseno"]["n1"]), MU1=m1["diseno"]["mu1"], SD1=m1["diseno"]["sd1"],
            N2=ent_codigo(m1["diseno"]["n2"]), MU2=m1["diseno"]["mu2"], SD2=m1["diseno"]["sd2"],
            MEDIA=nz(m1["media"], 4), DESDE=ent_codigo(m1["cortes"][0]),
            HASTA=ent_codigo(m1["cortes"][-1]),
            CONTEOS=" ".join(ent_codigo(c) for c in m1["conteos"]),
            CONTEOS_PY=", ".join(ent_codigo(c) for c in m1["conteos"]),
            EN_MEDIA=ent_codigo(m1["barra_media"]["conteo"]))
SUB2 = dict(STURGES=ent_codigo(m2["sturges_clases"]), DEF=ent_codigo(m2["def_clases"]),
            H=m2["h_origen"], D_MUCHAS=m2["origen"]["desplaza_muchas"],
            D_POCAS=m2["origen"]["desplaza_pocas"],
            MODAS_MUCHAS=m2["origen"]["modas_muchas"], MODAS_POCAS=m2["origen"]["modas_pocas"],
            FD=nz(m2["fd"]["h"], 4), SCOTT=nz(m2["scott"]["h"], 4))
_MS3 = [1, 4, 16, 64, 256]
_DIST3 = [m3["triangular"]["distancia"][m3["triangular"]["m"].index(m)] for m in _MS3]
SUB3 = dict(F_ASH=vec(m3["ejemplo"]["f_ash"], 4), HT=m3["triangular"]["h"],
            MS=", ".join(str(m) for m in _MS3), DIST=vec(_DIST3, 4), DIST_PY=vec_py(_DIST3, 4))
_V4 = [m4["v_min"], m4["v_peq"], m4["v_gra"]]
SUB4 = dict(N=ent_codigo(m4["n_contraste"]), VS=", ".join(str(v["V"]) for v in _V4),
            VS_PY=", ".join(str(v["V"]) for v in _V4),
            MEDIAS=vec([v["media"] for v in _V4], 4), SDS=vec([v["sd"] for v in _V4], 4),
            VACIAS=vec([v["vacia"] for v in _V4], 4), F0=nz(m4["f0"], 4))
SUB5 = dict(UNIF=" ".join(f"{v:g}" for v in m5["uniforme"]["f"]),
            UNIF_PY=" ".join(f"{v:g}" for v in m5["uniforme"]["f"]),
            TERM=vec(m5["gaussiano"]["terminos"], 4), F4=nz(m5["gaussiano"]["f"], 4),
            HM=", ".join(f"{h:g}" for h in m5["modas"]["h"]),
            MODAS=" ".join(str(v) for v in m5["modas"]["modas"]),
            MODAS_PY=", ".join(str(v) for v in m5["modas"]["modas"]))
SUB6 = dict(EF_E=nz(NUC["epanechnikov"]["eficiencia"], 4), EF_U=nz(NUC["uniforme"]["eficiencia"], 4),
            EF_G=nz(NUC["gaussiano"]["eficiencia"], 4), EPA2=nz(m6["epa_bw1_en_2"], 4))
_E7, _I7 = m7["edades"], m7["ingresos"]
SUB7 = dict(DIST=" ".join(f"{v:g}" for v in _E7["distancias"]),
            DIST_PY=", ".join(f"{v:g}" for v in _E7["distancias"]),
            FK=nz(_E7["f"], 8), DENTRO=ent_codigo(_E7["dentro"]),
            ING=", ".join(f"{v:g}" for v in _I7["datos"]), ING_PY=", ".join(f"{v:g}" for v in _I7["datos"]),
            A1=", ".join(f"{v:g}" for v in (_I7["areas"][0]["desde"], _I7["areas"][0]["hasta"])),
            A2=", ".join(f"{v:g}" for v in (_I7["areas"][1]["desde"], _I7["areas"][1]["hasta"])),
            A3=", ".join(f"{v:g}" for v in (_I7["areas"][2]["desde"], _I7["areas"][2]["hasta"])),
            AREAS=vec([a["area"] for a in _I7["areas"]], 4),
            AREAS_PY=vec_py([a["area"] for a in _I7["areas"]], 4))
SUB8 = dict(N=ent_codigo(m8["n"]), H_ECM=f"{m8['h_ecm']:g}", H_AMISE=nz(m8["h_amise"], 4),
            H_MISE=nz(m8["h_mise"], 4))
_F9 = m9["faithful"]
SUB9 = dict(SD=nz(_F9["sd"], 4), IQR134=nz(_F9["iqr_134"], 4), NRD0=nz(_F9["nrd0"], 4),
            NRD=nz(_F9["nrd"], 4), HIST=nz(_F9["hist_rule"], 4),
            SCX=nz(m9["plano"]["scott_x"], 2), SCY=nz(m9["plano"]["scott_y"], 2),
            SCIPY=nz(m9["distancias"]["scipy"], 2), NN_NRD0=nz(m9["distancias"]["nrd0"], 2))
SUB10 = dict(HU=f"{m10['h_ucv_mano']:g}", HL=f"{m10['h_lcv_mano']:g}",
             UCV=nz(m10["selectores"]["ucv"], 4), BCV=nz(m10["selectores"]["bcv"], 4),
             SJ=nz(m10["selectores"]["SJ"], 4))
_SEL = ["nrd0", "nrd", "ucv", "bcv", "SJ"]
SUB11 = dict(SEMILLA=ent_codigo(m11["semilla"]),
             EM=vec([m11["em"]["p"]] + m11["em"]["mu"] + m11["em"]["s"], 4),
             GANA=" ".join(nz(MC[s]["gana_pct"], 1) for s in _SEL),
             COLA=" ".join(nz(MC[s]["cola_pct"], 1) for s in _SEL),
             GANA_PY=", ".join(f"'{s}': {nz(MC[s]['gana_pct'], 1)}" for s in _SEL),
             COLA_PY=", ".join(f"'{s}': {nz(MC[s]['cola_pct'], 1)}" for s in _SEL),
             MISE_PY=vec_py([MC[s]["mise"] for s in _SEL], 5))
SUB12 = dict(CEROS=ent_codigo(m12["ceros"]), RECIP=nz(m12["recipro"]["pct"], 1),
             UCV_T=nz(SEL12["todas"]["ucv"], 2), SJ_T=nz(SEL12["todas"]["sj"], 2),
             UCV_P=nz(SEL12["una_por_pareja_sin_ceros"]["ucv"], 2),
             SJ_P=nz(SEL12["una_por_pareja_sin_ceros"]["sj"], 2),
             MASA_NEG=nz(BORDE["masa_negativa_pct"], 2),
             E_T=nz(SEL12["todas"]["empates_por_n"], 4), UMBRAL=nz(m12["umbral_empates"], 4),
             UCVX_T=nz(SEL12["todas"]["ucv_h_minusculo"], 4))


# =====================================================================
# LOS MÓDULOS
#
# Cada pieza con LaTeX —recuadros, tablas, derivaciones— se construye
# ANTES, en su propia variable, y el módulo solo la interpola. No es
# estilo: el Python de la casa es el 3.10, que no admite una barra
# invertida dentro de la expresión de un f-string, y casi toda pieza de
# este apéndice lleva fórmulas. Las cadenas son rf"…": crudas para que
# `\frac` no sea un salto de página, y f para interpolar. Las llaves de
# LaTeX van dobladas.
# =====================================================================
_BM, _BV = m1["barra_max"], m1["barra_media"]
_D1 = m1["diseno"]

_M1_SIM = sim(
    "apa-area", "El área bajo el histograma es la proporción de clientes",
    "Mueve los dos extremos del intervalo: la lectura suma las áreas de las barras que quedan "
    "dentro y cuenta los clientes que de verdad esperaron ese tiempo. Los botones cambian la "
    "unidad del eje (minutos u horas) y lo que miden las alturas (densidad, o intensidad: la "
    "densidad multiplicada por n). La raya naranja es la espera media. Antes de pasar el eje a "
    "horas: ¿cuánto medirá la barra más alta, y qué fracción de los clientes seguirá cayendo en ella?")

_M1_LEE = como_se_lee(rf"""        <p>La altura de una barra <strong>no es una probabilidad</strong>: es probabilidad por
          minuto. La barra más alta, de {ent(_BM["desde"])} a {ent(_BM["hasta"])} minutos, mide
          {firma(n(_BM["densidad"], 2), " por minuto")} porque contiene a {ent(_BM["conteo"])} de los
          {ent(m1["n"])} clientes y mide un minuto de ancho. Si los mismos tiempos se midieran en
          horas, esa barra pasaría a medir {firma(n(_BM["densidad_por_hora"], 1), " por hora")}: los
          datos son los mismos, el área es la misma, y la altura se multiplica por
          {ent(m1["minutos_por_hora"])} porque cada barra se estrecha en esa proporción. La
          fracción de clientes que cae en ella sigue siendo {n(_BM["densidad"], 2)}.</p>
        <p>Por eso una densidad puede valer más de 1 sin que nada esté mal, y por eso dos densidades
          solo se comparan si están en las mismas unidades. Lo que nunca pasa de 1 es un área.</p>
        <p style="margin-bottom:0;">Con las alturas como intensidad la forma no cambia: cada barra se
          multiplica por {ent(m1["n"])}, la más alta pasa a medir {ent(_BM["intensidad"])} clientes por
          minuto de espera y el área total deja de ser 1 para ser {ent(m1["n"])}, los clientes.</p>""")

_M1_PLANO = en_el_plano(rf"""        <p>En el plano la intensidad se mide en sedes por kilómetro cuadrado. Las
          {ent(m1["sedes"]["n"])} sedes del perímetro urbano de Bogotá, sobre
          {n(m1["sedes"]["area_km2"], 2)} km², dan una intensidad media de
          {firma(n(m1["sedes"]["lambda_km2"], 2), " sedes por km²")}. Cuando el capítulo 4 cuenta
          sedes por cuadrante y divide por el área, construye un histograma de intensidad en dos
          dimensiones. El capítulo 5 pone sobre cada sede una loma \(k_\sigma\) de anchura σ —el
          <em>núcleo</em> del módulo 5 de este apéndice— y las suma, \(\sum_i k_\sigma(u - x_i)\).
          Sobre todo el plano esa suma integra el número de sedes, y no 1, por la misma razón que aquí
          el área pasa a valer \(n\). Dentro de la ciudad integra algo menos, porque las lomas de las
          sedes cercanas al borde se salen de la ciudad; por eso el capítulo la divide por una corrección,
          \(e(u)\), que este apéndice ve en el módulo 12.</p>
        <p style="margin-bottom:0;">Lo que sigue en el apéndice es cómo estimar esa forma sin los
          defectos del histograma, que el módulo 2 pone a la vista.</p>""")

_M1_COD = tabs("La cafetería, en R y en Python", esc(R1.format(**SUB1)), esc(PY1.format(**SUB1)))

MOD1 = cabecera(
    1, TITULOS[0][0], INGLES[0],
    "Distinguir una densidad de una probabilidad y de una intensidad, y leer un "
    "histograma de densidad por sus áreas, no por sus alturas.") + rf"""
      <p>El capítulo 5 estima la <strong>intensidad</strong> de las sedes educativas de Bogotá con
        núcleos: pone una loma sobre cada sede, las suma y lee el resultado como un mapa. Para hacerlo
        decide un ancho de banda σ, una forma de núcleo, un selector que elige σ por él y una corrección
        para el borde de la ciudad. Cada una de esas decisiones tiene una versión en <strong>una sola
        dimensión</strong>, donde todo se puede dibujar sobre un renglón y calcular a mano. (En la recta
        el ancho de banda se llama \(h\), como en casi todos los libros; la letra σ queda para el ancho
        del capítulo 5, y la desviación típica de los datos se escribe \(s\) en la muestra y
        \(\sigma_f\) en la distribución que los generó.)</p>

      <p>Este apéndice recorre esa versión en este orden: el histograma (módulo 2) y el histograma
        promediado (3); la fórmula \(k/(nV)\), que une a todos los estimadores que siguen (4); el
        estimador de núcleo, que nace de las ventanas de Parzen (5), y la forma de su loma (6); los
        <em>k</em> vecinos (7); el error que comete el estimador (8); las reglas (9) y la validación
        cruzada (10) que eligen su ancho; un experimento con una verdad conocida para ver qué selector
        acierta (11), y, al final, las distancias entre las sedes de Bogotá, donde aparece lo que la
        recta daba por hecho: que no hay borde y que los datos son independientes (12); para cerrar,
        una autoevaluación con ejercicios (13). Los módulos 1 a 12 terminan en un recuadro
        <strong>En el plano</strong> que dice dónde reaparece la idea en el material.</p>

      <h3>Una cafetería con dos tipos de cliente</h3>

      <p>En la hora pico de una cafetería hay dos tipos de pedido. Los que piden solo una bebida se
        despachan rápido; los que piden comida tardan. Se simulan {firma(ent(_D1["n1"]), " clientes")}
        de bebida, con un tiempo de espera medio de {_D1["mu1"]} minutos y desviación {_D1["sd1"]}, y
        {firma(ent(_D1["n2"]), " de comida")}, con media {_D1["mu2"]} y desviación {_D1["sd2"]}. La
        muestra junta los {ent(m1["n"])} tiempos y no dice de qué tipo era cada cliente, que es lo
        habitual: quien mide el tiempo de espera no anota qué se pidió.</p>

      <p>La espera media es de {firma(n(m1["media"], 4), " minutos")}. Es una cifra correcta y no
        describe a nadie, como enseña el histograma de abajo: la barra que la contiene, la de
        {ent(_BV["desde"])} a {ent(_BV["hasta"])} minutos, tiene <strong>{ent(_BV["conteo"])}
        clientes</strong>. Entre {ent(m1["valle"]["desde"])} y {ent(m1["valle"]["hasta"])} minutos solo
        esperaron {ent(m1["valle"]["conteo"])} de los {ent(m1["n"])}. La media cae en el valle entre
        dos grupos, y ella sola no tiene manera de avisarlo. La mediana, {n(m1["mediana"], 2)} minutos,
        tampoco salva el resumen: describe a los clientes de bebida y deja fuera a los
        {ent(_D1["n2"])} de comida. Esa es la razón de estimar una
        <strong>densidad</strong> en vez de un parámetro: ver la forma entera de la distribución antes
        de decidir cómo resumirla.</p>

      <p>El histograma de densidad divide el eje en intervalos de ancho \(h\). Si el intervalo
          \(j\) tiene \(\nu_j\) de las \(n\) observaciones, su barra mide</p>

      <div class="formula">
        $$\hat f(x) = \frac{{\nu_j}}{{n\,h}} \quad \text{{para }}x\text{{ en el intervalo }}j,
          \qquad\qquad \int \hat f(x)\,dx = \sum_j \frac{{\nu_j}}{{n\,h}}\,h = 1.$$
      </div>

      <p>El área de cada barra es la <strong>proporción</strong> de
          datos que caen en ella, y la suma de todas las áreas vale 1.</p>

      <h3>De la densidad a la intensidad</h3>

      <p>Si cada barra se multiplica por \(n\), deja de ser una proporción por minuto y pasa a ser un
        <strong>conteo por minuto</strong>, y el área total ya no es 1 sino {ent(m1["n"])}, el número de
        clientes. Esa función, \(\lambda(x) = n\,f(x)\), es una <strong>intensidad</strong>. Es la misma
        curva que la densidad, en otra escala, y responde otra pregunta: no «qué fracción» sino
        «cuántos». Ojo con el «por minuto»: es por cada minuto <em>del eje de espera</em>, no por minuto
        de reloj. No dice cuántos clientes llegan por minuto, sino cuántos esperaron un tiempo que cae
        en ese tramo de un minuto.</p>

{_M1_SIM}
{_M1_LEE}
{_M1_COD}
      <p>Dos detalles del código que vuelven en todo el apéndice. El argumento
        <code>right = FALSE</code> hace que los intervalos sean \([a, b)\): un cliente que esperó
        exactamente {ent(_BM["hasta"])} minutos cuenta en la barra que empieza ahí, no en la que
        termina ahí; <code>np.histogram</code> usa la misma convención. Y la pestaña de Python
        <em>lee</em> la muestra en vez de simularla, porque R y numpy no comparten generador
        aleatorio: con la misma semilla producen números distintos.</p>

{_M1_PLANO}""" + CIERRE

_O2 = m2["origen"]
_M2_DER = derivacion("der-hist", r"Ver de dónde sale \(h \propto n^{-1/3}\)", [
    rf"""              <p>La barra que contiene a \(x\) cuenta los datos de un intervalo cuya
                probabilidad es \(p \approx f(x)\,h\). El conteo es binomial, así que la altura
                \(\nu/(nh)\) tiene varianza</p>
              $$\operatorname{{Var}} \hat f(x) = \frac{{p(1-p)}}{{n h^2}} \approx \frac{{f(x)}}{{n h}}.$$""",
    rf"""              <p>El sesgo sale de aproximar \(f\) por una constante en un intervalo de ancho
                \(h\): es del orden de \(f'(x)\,h\). Integrado sobre la recta, el sesgo al cuadrado
                vale \(\tfrac{{h^2}}{{12}} R(f')\), con \(R(f') = \int f'(x)^2\,dx\).</p>""",
    rf"""              <p>Integrada sobre la recta, la varianza da \(1/(nh)\), porque \(f\) integra 1. El
                error cuadrático medio integrado para \(n\) grande —en inglés <em>AMISE</em>, que el
                módulo 8 define con calma— es la suma de los dos, y se minimiza derivando respecto a
                \(h\):</p>
              $$\text{{AMISE}}(h) = \frac{{1}}{{n h}} + \frac{{h^2}}{{12}} R(f') \quad\Longrightarrow\quad
                h^\ast = \left(\frac{{6}}{{n\,R(f')}}\right)^{{1/3}}.$$""",
    rf"""              <p>Si \(f\) fuera normal con desviación típica \(\sigma_f\) —la de la distribución
                que generó los datos; la de la muestra es \(s\), y ninguna de las dos es un ancho de
                banda—, \(R(f') = 1/(4\sqrt\pi\,\sigma_f^3)\) y el óptimo queda
                \(h^\ast = (6 \cdot 4\sqrt\pi)^{{1/3}}\,\sigma_f\,n^{{-1/3}}
                \approx {n(m2["scott"]["constante_exacta"], 2)}\,\sigma_f\,n^{{-1/3}}\).</p>"""],
    rf"""Es la <strong>regla de Scott</strong> para el histograma, que suele redondearse a
    \({m2['scott']['constante']}\,s\,n^{{-1/3}}\), con la desviación típica \(s\) de la muestra en el
    lugar de \(\sigma_f\). El error decae como \(n^{{-2/3}}\): para bajarlo a la mitad hacen falta
    {n(m2['tasas']['datos_para_mitad'], 2)} veces más datos.""")

_M2_SIM = sim(
    "apa-histograma", "Ancho y origen de un histograma de las erupciones",
    "Dos deslizadores: el ancho de los intervalos y cuánto se corre su origen, como fracción del "
    "ancho. La lectura cuenta las barras y las modas —una meseta más alta que sus dos vecinas, es "
    "decir, un máximo local del histograma—. "
    "Antes de tocar el ancho, deja el que viene, mueve solo el origen y cuenta cuántos números de "
    "modas distintos consigues.")

_M2_LEE = como_se_lee(rf"""        <p>Con {ent(_O2["origenes_muchas"])} de los {ent(_O2["n_origenes"])} orígenes el
          histograma tiene {firma(ent(_O2["modas_muchas"]), " modas")}, y con los otros
          {ent(_O2["origenes_pocas"])}, {firma(ent(_O2["modas_pocas"]))}. Con el origen sin correr hay
          {ent(_O2["modas_muchas"])}; corriéndolo un cuarto del ancho, {n(_O2["desplaza_pocas"], 4)}
          minutos, quedan {ent(_O2["modas_pocas"])}.</p>
        <p>Una moda que aparece o desaparece al mover el origen no es una propiedad del dato:
          es de la rejilla. Con el origen quieto, el ancho hace lo mismo a otra escala: a
          {n(m2["anchos"][0], 2)} minutos el histograma tiene {ent(m2["escala_modas_origen0"][0])}
          modas, a {n(m2["anchos"][1], 2)} tiene {ent(m2["escala_modas_origen0"][1])}, a
          {n(m2["anchos"][2], 2)} tiene {ent(m2["escala_modas_origen0"][2])}, y desde
          {n(m2["anchos"][4], 2)} se queda en {ent(m2["escala_modas_origen0"][4])}: las erupciones
          cortas y las largas, los dos grupos que cualquier gráfico del géiser deja ver. «Moda» quiere
          decir aquí lo que cuenta la lectura, un máximo local de la curva estimada; si ese bulto está
          también en la distribución de verdad es otra pregunta, y es la de los módulos 5, 10 y 11.</p>
        <p style="margin-bottom:0;">Una afirmación sobre la forma de una distribución que solo se
          sostiene con un ancho y un origen concretos no se sostiene.</p>""")

_M2_COD = tabs("Ancho, origen y modas, en R y en Python", esc(R2.format(**SUB2)), esc(PY2.format(**SUB2)))

_M2_PLANO = en_el_plano(r"""        <p>Las dos perillas del histograma son los dos efectos del <strong>problema de la unidad
          de área modificable</strong> (MAUP) del capítulo 3. Mover el origen sin cambiar el
          ancho es el <strong>efecto de zonificación</strong>: unidades del mismo tamaño, con las
          fronteras en otro sitio. Cambiar el ancho es el <strong>efecto de escala</strong>: cuántas
          unidades hay. Cuando el capítulo 4 cuenta sedes por cuadrante, su prueba χ² hereda las dos:
          su módulo 6 muestra que el veredicto cambia con el tamaño de la celda (escala), y el módulo 1
          del capítulo 5 advierte, con la rejilla de Kennedy, que moverla media celda cambia los
          conteos (zonificación), y con ellos lo que lee el χ².</p>
        <p style="margin-bottom:0;">Si el origen es arbitrario, la salida natural es no elegir
          uno: promediar sobre todos. Es la idea del módulo 3.</p>""")

MOD2 = cabecera(
    2, TITULOS[1][0], INGLES[1],
    "Ver que un histograma depende de dos decisiones —el ancho y el origen de los "
    "intervalos— y reconocer en cada una un efecto del MAUP.") + rf"""
      <p>Un histograma exige dos decisiones antes de contar nada: el <strong>ancho</strong> \(h\) de
        los intervalos y su <strong>origen</strong>, el punto donde empieza el primero. Los datos no las
        dictan: hay reglas que proponen un ancho a partir de ellos —vienen enseguida—, pero ninguna
        dice dónde empezar. Para verlo se usan las {ent(m2["n"])} erupciones del géiser Old
        Faithful (<code>faithful$eruptions</code>, en R base): la duración de cada erupción, en
        minutos. Es el conjunto con que todos los textos de estimación de densidad enseñan, y eso
        permite contrastar cada cifra de este apéndice con la literatura.</p>

      <p>Si no se le pide nada, R aplica la regla de <strong>Sturges</strong>, que propone
        \(\lceil \log_2 n + 1\rceil\) = {ent(m2["sturges_clases"])} intervalos, y luego los redondea
        con <code>pretty()</code> a cortes «bonitos»: el histograma por defecto tiene
        {firma(ent(m2["def_clases"]), " barras")} de {n(m2["def_ancho"], 1)} minutos. Sturges se pensó
        para muestras pequeñas: su número de barras crece como \(\log_2 n\), mucho más despacio que el
        \(n^{{1/3}}\) de las dos reglas que vienen abajo. Con {ent(m2["n"])} erupciones todavía no se
        nota —aquí da barras más estrechas que ellas—, pero con decenas de miles de datos se queda con
        muy pocas.</p>

      <h3>El ancho: sesgo contra varianza</h3>

      <p>Dentro de un intervalo el histograma supone que la densidad es constante. Si el intervalo es
        ancho, esa suposición es falsa —la densidad sube o baja dentro de él— y el histograma se
        equivoca de forma <strong>sistemática</strong>: es el <strong>sesgo</strong>, y crece con
        \(h\). Si el intervalo es estrecho, cae en él un puñado de datos, y la altura de la barra
        depende de cuáles cayeron por azar: es la <strong>varianza</strong>, y crece cuando \(h\)
        baja. El ancho óptimo equilibra las dos, y la cuenta dice que debe encogerse como
        \(n^{{-1/3}}\) al crecer la muestra.</p>

{_M2_DER}
      <p>Sobre las erupciones, la regla de Scott da \(h\) = {firma(n(m2["scott"]["h"], 4))} minutos y
        la de Freedman y Diaconis, que cambia la desviación por el rango intercuartílico
        (\(2\,\mathrm{{IQR}}\,n^{{-1/3}}\)), da {firma(n(m2["fd"]["h"], 4))}. Las dos están pensadas
        para el histograma, y el módulo 9 vuelve sobre la primera, porque se la confunde a menudo con
        una regla para el estimador de núcleo.</p>

      <h3>El origen: el mismo ancho, otra historia</h3>

      <p>Ahora se fija el ancho en {firma(n(m2["h_origen"], 2), " minutos")} y se mueve solo el
        origen, en {ent(_O2["n_origenes"])} pasos iguales de un vigésimo de \(h\). El dato es el
        mismo y el ancho es el mismo; lo único que cambia es dónde caen los cortes.</p>

{_M2_SIM}
{_M2_LEE}
{_M2_COD}
      <p>La función <code>histo()</code> construye los cortes a partir del origen en vez de dejar que
        <code>hist()</code> los elija, y <code>modas()</code> comprime primero las barras iguales
        contiguas con <code>rle()</code>: una meseta de dos barras iguales es <em>una</em> moda, no dos
        ni ninguna. La pestaña de Python tiene una línea que la de R no necesita, y vale la pena
        leerla: R corre los cortes una diezmillonésima del ancho antes de contar, para que un dato que
        cae justo en un corte no se pierda por el redondeo binario de la coma flotante. Sin esa
        tolerancia, numpy y R discrepan en el conteo de algunas barras y las modas no coinciden.</p>

{_M2_PLANO}""" + CIERRE

_E3 = m3["ejemplo"]
_T3 = m3["triangular"]
_V3 = m3["varianza"]
_S3 = m3["solapadas"]


def _fila_desp(t):
    return fila(rf"\(j = {t['j']}\)", n(t["desplazamiento"], 2),
                ", ".join(n(c, 2) for c in t["cortes"][:3]) + ", …",
                ", ".join(ent(c) for c in t["conteos"]), ent(t["suma"]))


def _fila_ash(i):
    return fila(rf"\(x = {ent(_E3['puntos'][i])}\)", *[n(v, 4) for v in _E3["f_j"][i]],
                f"<strong>{n(_E3['f_ash'][i], 4)}</strong>")


_M3_TAB1 = tabla(["Histograma", "Desplazamiento", "Primeros cortes", "Conteos", "Suma"],
                 "".join(_fila_desp(t) for t in _E3["desplazados"]),
                 "Los tres histogramas desplazados sobre la malla extendida.")
_M3_TAB2 = tabla(["Punto", r"\(j = 0\)", r"\(j = 1\)", r"\(j = 2\)", r"\(\hat f_{\text{ASH}}(x)\)"],
                 "".join(_fila_ash(i) for i in range(len(_E3["puntos"]))),
                 "Las alturas de cada histograma en cuatro puntos, y su promedio.")
_S3_VENT = ", ".join(f"[{v[0]:g}, {v[1]:g}]" for v in zip(_S3["desde"], _S3["hasta"]))
_M3_SOLAP = trampa("ventanas solapadas no es un ASH", rf"""Algunos textos presentan como
        «suavizado» un esquema que se le parece: ventanas fijas que se solapan, cada una dibujada como
        una barra de altura conteo/(\(n\) · ancho). Con los {ent(_S3["n"])} datos
        {{{", ".join(f"{v:g}" for v in _S3["datos"])}}} y tres ventanas de ancho {ent(_S3["ancho"])}
        —{_S3_VENT}— se cuentan {", ".join(ent(c) for c in _S3["conteos"])} datos:
        {", ".join(f"{v:g}" for v in lista(_S3["dobles"]))} caen en dos ventanas y cuentan dos veces,
        y {", ".join(f"{v:g}" for v in lista(_S3["sin_datos"]))} no cae en ninguna. Son
        {ent(_S3["contribuciones"])} contribuciones para {ent(_S3["n"])} datos, y las áreas de las tres
        barras suman {ent(_S3["contribuciones"])}/{ent(_S3["n"])} = {n(_S3["area"], 4)}, no 1. El ASH
        no tiene ese problema porque cada uno de sus histogramas reparte exactamente los \(n\) datos, y
        el promedio de cosas que integran 1 integra 1.""")
_M3_SIM = sim(
    "apa-ash", "El ASH de las erupciones se acerca al núcleo triangular",
    f"La escalera naranja es el ASH, con un ancho fijo de {n(_T3['h'], 1)} minutos; la línea discontinua verde es "
    "el estimador de núcleo triangular del mismo semiancho. El deslizador cambia el número m de "
    "histogramas que se promedian, y la lectura da la mayor distancia vertical entre las dos curvas. "
    "Antes de moverlo: ¿con qué m dejarías de distinguirlas a simple vista?")
_I8 = _T3["m"].index(8)
_I16 = _T3["m"].index(16)
_M3_LEE = como_se_lee(rf"""        <p>Hacia \(m\) = {ent(_T3["m"][_I8])} o {ent(_T3["m"][_I16])} las dos curvas dejan de
          distinguirse: la distancia máxima baja a {n(_T3["distancia"][_I8], 4)} y
          {n(_T3["distancia"][_I16], 4)}, entre el {pct(_T3["pct_pico"][_I8], 0)} y el
          {pct(_T3["pct_pico"][_I16], 0)} de la altura del pico, que es de {n(_T3["pico"], 2)}. Desde ahí,
          más histogramas solo pulen escalones que ya no se ven.</p>
        <p style="margin-bottom:0;">Fíjate en lo que <em>no</em> cambia al mover el deslizador: la
          anchura de la curva. Las dos modas tienen la misma forma con \(m\) = 2 que con \(m\) = 64,
          porque cuánto se suaviza lo decide \(h\), y \(h\) está fijo.</p>""")
_M3_COD = tabs("El ASH, en R y en Python", esc(R3.format(**SUB3)), esc(PY3.format(**SUB3)))
_M3_TRUE = trampa("<code>MASS::truehist</code> no promedia nada", """En CRAN el ASH tiene su propio
        paquete, <code>ash</code>, del mismo Scott (<code>bin1()</code> y <code>ash1()</code>); este
        apéndice no lo usa porque construirlo a mano deja ver cada paso. Lo que no hay que hacer es
        buscarlo en una función de nombre prometedor: <code>truehist()</code>, del paquete
        <code>MASS</code>, dibuja <em>un</em> histograma, y su argumento <code>nbins</code> cambia el
        ancho. Subirlo no suaviza, hace el histograma más rugoso.""")
_M3_PLANO = en_el_plano(r"""        <p>La rejilla de Kennedy del capítulo 5 (módulo 1) es la del módulo 2 de este apéndice
          en dos dimensiones: la puso alguien, y moverla media celda cambia los conteos. Promediar los
          conteos de todas las rejillas desplazadas, en horizontal y en vertical, da por el mismo
          argumento de este módulo un núcleo: el producto de dos triangulares, uno por eje, con soporte
          cuadrado. Con él deja de importar <em>dónde</em> se puso la rejilla, pero no hacia dónde mira:
          un cuadrado tiene direcciones privilegiadas, y una sede a 300 m en diagonal pesa distinto que
          una a 300 m hacia el norte. El núcleo gaussiano del capítulo 5 da el paso que falta: pesa por
          distancia, igual en todas las direcciones.</p>
        <p style="margin-bottom:0;">Antes de escribir el núcleo en general hay una formulación que
          contiene a la vez al histograma, a las ventanas de Parzen y a los <em>k</em> vecinos: el
          módulo 4.</p>""")

MOD3 = cabecera(
    3, TITULOS[2][0], INGLES[2],
    "Construir el histograma desplazado promediado a mano, ver por qué su malla tiene que "
    "extenderse y descubrir que, con muchos desplazamientos, es un estimador de núcleo.") + rf"""
      <p>Si el origen de un histograma es arbitrario, se pueden dibujar <em>todos</em> los orígenes y
        promediarlos. El <strong>histograma desplazado promediado</strong> (<em>averaged shifted
        histogram</em>, ASH; Scott, 1985) construye \(m\) histogramas con el mismo ancho \(h\), cada
        uno corrido \(\delta = h/m\) respecto del anterior, y promedia sus alturas <strong>en los
        mismos puntos</strong> \(x\):</p>

      <div class="formula">
        $$\hat f_{{\text{{ASH}}}}(x) = \frac{{1}}{{m}} \sum_{{j=0}}^{{m-1}} \frac{{c_j(x)}}{{n\,h}},$$
      </div>

      <p>donde \(c_j(x)\) es el número de datos en el intervalo del
          histograma \(j\) que contiene a \(x\). Con \(m = 1\) es el histograma de siempre.</p>

      <h3>El ejemplo a mano, y la trampa de la malla</h3>

      <p>Los datos son {{{", ".join(ent(v) for v in _E3["datos"])}}}, con \(h\) = {ent(_E3["h"])} y
        \(m\) = {ent(_E3["m"])}, de modo que cada histograma se corre \(\delta\) =
        {n(_E3["delta"], 2)} respecto del anterior. El histograma de base usa los cortes
        {", ".join(ent(c) for c in _E3["base_cortes"])} y cuenta
        {", ".join(ent(c) for c in _E3["base_conteos"])}.</p>

      <p>Si se corre esa misma malla, los datos de los extremos se quedan fuera: el histograma
        desplazado \(\delta\) cuenta {ent(_E3["base_desplazada_cuenta"][1])} datos y el desplazado
        \(2\delta\), solo {ent(_E3["base_desplazada_cuenta"][2])} de los {ent(_E3["n"])}. El promedio
        perdería masa y dejaría de integrar 1. Por eso la malla se <strong>extiende</strong> un ancho
        por cada lado, de {ent(_E3["extendida"]["desde"])} a {ent(_E3["extendida"]["hasta"])}, y con
        ella los tres histogramas cuentan los {ent(_E3["n"])}:</p>

{_M3_TAB1}
      <p>El paso que define el método es promediar <strong>en el mismo \(x\)</strong>. La casilla que
        contiene a \(x = 3\) es la segunda en el primer histograma y la primera en el tercero:
        promediar las casillas que ocupan la misma posición en los tres vectores de conteos sería
        promediar intervalos distintos del eje.</p>

{_M3_TAB2}
{_M3_SOLAP}
      <h3>Lo que se gana, y su límite</h3>

      <p>Promediar baja la varianza, pero no indefinidamente: para el mismo \(h\), la varianza del
        ASH es aproximadamente \((2m^2+1)/(3m^2)\) veces la del histograma, que vale
        {n(_V3["factor"][1], 4)} con \(m\) = {ent(_V3["m"][1])}, {n(_V3["factor"][3], 4)} con
        \(m\) = {ent(_V3["m"][3])} y tiende a {n(_V3["limite"], 4)}: por muchos histogramas que se
        promedien, la varianza no baja de dos tercios de la del histograma. Lo que más se gana está en
        el otro término del error. El sesgo al cuadrado integrado del histograma,
        \(\tfrac{{h^2}}{{12}}R(f')\) en el módulo 2, se divide por \(m^2\) (Scott, 1985), y en el
        límite queda solo el del núcleo triangular, que es de orden \(h^4\) (módulo 8). Por eso, con
        \(m\) grande, el ASH alcanza la tasa del núcleo, \(n^{{-4/5}}\), mejor que el \(n^{{-2/3}}\) del
        histograma. Gana además una curva <strong>sin escalones grandes</strong> y
        <strong>sin un origen arbitrario</strong>. Para suavizar más —promediar sobre una ventana más
        ancha— hay que subir \(h\).</p>

      <h3>El ASH es un núcleo disfrazado</h3>

      <p>Con \(h\) fijo y \(m\) creciendo, el ASH converge a una curva concreta. Sobre las erupciones,
        con \(h\) = {n(_T3["h"], 1)}, su distancia máxima a la curva
        \(\hat f(x) = \frac{{1}}{{n h}}\sum_i \max\left(0,\,1 - |x - x_i|/h\right)\) vale
        {n(_T3["distancia"][0], 4)} con \(m\) = 1, {n(_T3["distancia"][2], 4)} con
        \(m\) = {ent(_T3["m"][2])}, {n(_T3["distancia"][4], 4)} con \(m\) = {ent(_T3["m"][4])} y
        {n(_T3["distancia"][7], 5)} con \(m\) = {ent(_T3["m"][7])}. El producto de \(m\) por la
        distancia se queda cerca de {n(_T3["m_por_distancia"][2], 2)}: el error baja como \(1/m\).</p>

      <p>Esa curva es un <strong>estimador de núcleo</strong> con núcleo triangular de semiancho
        \(h\), el objeto de los módulos 5 y 6. La razón es directa: promediado sobre todos los
        orígenes, lo que un dato \(x_i\) aporta a la altura en \(x\) es la probabilidad de que los dos
        caigan en el mismo intervalo, y esa probabilidad es \(1 - |x - x_i|/h\) si están a menos de
        \(h\) y cero si no. El histograma promediado no es una técnica distinta del núcleo: es su
        versión discreta.</p>

{_M3_SIM}
{_M3_LEE}
{_M3_COD}
      <p>La función <code>ash()</code> hace en pocas líneas lo que la tabla hizo a mano: construye la
        malla extendida, corre los cortes \(j\delta\) en cada vuelta y, para cada punto de
        <code>g</code>, busca con <code>findInterval()</code> la casilla que lo contiene en
        <em>ese</em> histograma. La última línea de cada pestaña mide la distancia al núcleo
        triangular con cinco valores de \(m\): desde \(m\) = {ent(_T3["m"][2])}, cada vez que
        \(m\) se multiplica por {ent(_T3["m"][2])}, la distancia se divide casi exactamente por lo
        mismo.</p>

{_M3_TRUE}
{_M3_PLANO}""" + CIERRE

_VM, _VP, _VG = m4["v_min"], m4["v_peq"], m4["v_gra"]
_PN = {p["n"]: p for p in m4["por_n"]}
_DIM = m4["dimension"]
_P4 = m4["plano"]


def svg_plano():
    """Las dos maneras de elegir la ventana, sobre sedes reales de Kennedy.

    Dos paneles con las mismas sedes y los mismos tres sitios. A la izquierda,
    un círculo de radio fijo alrededor de cada sitio (Parzen); a la derecha, el
    círculo que llega a la k-ésima sede (k-NN). Son DOS `<svg>` y no uno: en el
    teléfono se apilan y cada panel ocupa el ancho entero; lado a lado en uno
    solo, los rótulos quedaban a cinco píxeles. Las coordenadas salen del JSON
    en kilómetros; los rótulos numéricos también, y `audita_texto_apendicea.py`
    los lee panel por panel.
    """
    # El lienzo enseña también el MARGEN, más tenue: antes un `<svg>` interior
    # lo recortaba, y el pie hablaba de 58 sedes donde se veían 39; los
    # círculos grandes, además, se cortaban (segunda pasada de la revisión 2).
    lado, margen = _P4["lado_km"], _P4["margen_km"]
    total = lado + 2 * margen
    px = 300 / total
    def X(v): return f"{(v + margen) * px:.1f}"
    def Y(v): return f"{(lado + margen - v) * px:.1f}"
    colores = ["#1a7358", "#D55E00", "#0072B2"]
    nombres = ["denso", "intermedio", "ralo"]

    # Los rótulos van DEBAJO del cuadro, no dentro: dentro tapaban justo las
    # sedes que contaban, y quien contaba veía menos de las que decía el
    # rótulo (revisión 2). Las sedes que cuenta cada círculo van rellenas con
    # su color; la lista de cuáles son la calcula R (`parzen_dentro`,
    # `knn_dentro`), no esta función.
    def panel(clase, radios, rotulos, clave, titulo, alt):
        # Una sede que cuentan DOS círculos lleva el relleno del primero y un
        # anillo del segundo: con un solo color, el naranja enseñaba 6 rellenas
        # bajo un rótulo de 7 (segunda pasada de la revisión 2).
        colores_de = {}
        for s, c in zip(SIT, colores):
            for i in lista(s[clave]):
                colores_de.setdefault(i, []).append(c)

        def sede(i, x, y):
            cs = colores_de.get(i, [])
            dentro = 0 <= x <= lado and 0 <= y <= lado
            if not cs:
                return (f'<circle cx="{X(x)}" cy="{Y(y)}" r="3.2" fill="#6b7280" '
                        f'fill-opacity="{0.6 if dentro else 0.25}"/>')
            anillo = f' stroke="{cs[1]}" stroke-width="2.2"' if len(cs) > 1 else ""
            return f'<circle cx="{X(x)}" cy="{Y(y)}" r="4.2" fill="{cs[0]}" fill-opacity="0.95"{anillo}/>'
        puntos = "".join(sede(i, x, y) for i, (x, y) in enumerate(zip(_P4["x"], _P4["y"])))
        circ = "".join(
            f'<circle cx="{X(s["x"])}" cy="{Y(s["y"])}" r="{r * px:.1f}" fill="none" '
            f'stroke="{c}" stroke-width="2.5"/>'
            f'<path d="M{X(s["x"])} {Y(s["y"])} m-5 0 h10 m-5 -5 v10" stroke="{c}" stroke-width="2.5"/>'
            for s, r, c in zip(SIT, radios, colores))
        etiquetas = "".join(
            f'<text x="4" y="{324 + 20 * k}" fill="{c}" font-size="15" font-weight="700">'
            f'✚ {nm}: {t}</text>'
            for k, (c, nm, t) in enumerate(zip(colores, nombres, rotulos)))
        return (f'<svg class="{clase}" viewBox="-6 -30 312 396" role="img" aria-label="{alt}" '
                f'style="width:100%;max-width:330px;height:auto;color:#374151;">'
                f'<text x="150" y="-11" text-anchor="middle" font-size="15" font-weight="700" '
                f'fill="currentColor">{titulo}</text>'
                f'<rect x="0" y="0" width="300" height="300" fill="none" stroke="currentColor" '
                f'stroke-opacity="0.12"/>'
                f'<rect x="{margen * px:.1f}" y="{margen * px:.1f}" width="{lado * px:.1f}" '
                f'height="{lado * px:.1f}" fill="none" stroke="currentColor" stroke-opacity="0.45"/>'
                f'{puntos}{circ}{etiquetas}</svg>')
    izq = panel("apa-panel-fijo", [_P4["radio_km"]] * 3,
                [f'{ent(s["parzen_conteo"])} sede' + ("" if s["parzen_conteo"] == 1 else "s") + " dentro"
                 for s in SIT], "parzen_dentro",
                f"Radio fijo: {n(_P4['radio_km'], 1)} km",
                "Las sedes de una esquina de Kennedy con tres círculos del mismo radio, que "
                "encierran distinto número de sedes; las que cuenta cada círculo van rellenas con su color.")
    der = panel("apa-panel-k", [s["knn_radio"] for s in SIT],
                [f'radio {n(s["knn_radio"], 2)} km' for s in SIT], "knn_dentro",
                f"k fijo: la {ent(_P4['k'])}.ª sede más cercana",
                "Las mismas sedes con tres círculos que llegan a la cuarta sede más cercana: "
                "pequeños donde hay muchas y grandes donde hay pocas; las cuatro vecinas de cada "
                "sitio van rellenas con su color.")
    return (f'      <figure style="margin:1.5rem 0;">\n'
            f'        <div style="display:flex;flex-wrap:wrap;justify-content:center;gap:1rem 1.5rem;">'
            f'{izq}{der}</div>\n'
            f'        <figcaption class="text-sm text-gray-600" style="text-align:center;'
            f'margin-top:0.5rem;">Una esquina de Kennedy de {n(lado, 1)} km de lado —el cuadro—, con '
            f'{ent(_P4["n_dentro"])} sedes dentro; alrededor, más tenues, las {ent(_P4["n_margen"])} de '
            f'un margen de {n(margen, 1)} km, que también cuentan, para que ningún círculo pierda '
            f'sedes por el borde del cuadro. Cada cruz es un sitio donde se estima: el más denso, uno '
            f'intermedio y el más ralo del cuadro. Las sedes rellenas son las que cuenta el círculo de '
            f'su color, y un anillo marca la que cuentan dos.</figcaption>\n      </figure>\n')


def _fila_plano(etq, s):
    return fila(etq, ent(s["parzen_conteo"]), n(s["parzen_intensidad"], 2),
                n(s["knn_radio"], 3), n(s["knn_intensidad"], 2))


_M4_TAB1 = tabla([r"Ancho \(V\)", "Valor esperado", "Sesgo", "Desviación típica", "P(ventana vacía)"],
                 "".join(fila(n(v["V"], 2), n(v["media"], 4), n(v["sesgo"], 5), n(v["sd"], 4),
                              n(v["vacia"], 4)) for v in (_VM, _VP, _VG)),
                 f"El estimador k/(nV) en x = 0 con n = {ent(m4['n_contraste'])} datos normales, "
                 "en forma cerrada.")
_M4_SIM = sim(
    "apa-ventana", "El estimador ingenuo en x = 0: centro, nube y verdad",
    "El eje horizontal es el ancho V de la ventana, en escala logarítmica. La línea verde es el valor "
    "esperado de k/(nV); la banda, dos desviaciones típicas a cada lado; la línea discontinua, la "
    "verdad. Los botones cambian el tamaño n de la muestra y el deslizador marca un ancho. Antes de "
    "tocar los botones: ¿qué crees que le pasa a la banda al cuadruplicar n?", alto=300)
_M4_LEE = como_se_lee(r"""        <p>La distancia entre la línea verde y la discontinua es el <strong>sesgo</strong>; la
          banda mide la <strong>desviación típica</strong>: se abre dos desviaciones típicas a cada
          lado de la línea verde, y el cuadrado de una de ellas es la varianza. Achicar la ventana
          acerca la línea a la verdad y abre la banda; agrandarla hace lo contrario.</p>
        <p style="margin-bottom:0;">Cuadruplicar \(n\) deja la banda a la mitad en todos los anchos,
          porque la desviación típica va como \(1/\sqrt n\), y la línea verde no se mueve: el sesgo no
          depende de \(n\), solo de la ventana. Por eso el mejor ancho se puede achicar cuando \(n\)
          crece. El módulo 8 convierte esta figura en una fórmula.</p>""")
_M4_TAB2 = tabla(["Sitio", "Sedes a 300 m", "Intensidad (Parzen)", "Radio de la 4.ª (km)",
                  "Intensidad (k-NN)"],
                 _fila_plano("Denso", SIT[0]) + _fila_plano("Intermedio", SIT[1])
                 + _fila_plano("Ralo", SIT[2]),
                 "Las dos intensidades, en sedes por km²: el conteo entre el área del círculo fijo, "
                 "y k entre el área del círculo que llega a la k-ésima sede.")
_M4_COD = tabs("El estimador ingenuo en forma cerrada, en R y en Python", esc(R4.format(**SUB4)),
               esc(PY4.format(**SUB4)))
_M4_PLANO = en_el_plano(r"""        <p>En el plano \(V\) es un área, y \(k/V\) —sin dividir por \(n\)— es una intensidad: es
          lo que hace el capítulo 4 cuando divide el conteo de un cuadrante por su área. Las dos ramas
          de la figura tienen su función en spatstat: <code>density.ppp</code> fija el tamaño de la
          región (el núcleo y su σ) y <code>nndensity</code> fija \(k\) y estima
          \(\hat\lambda(u) = k/(\pi\,d_k(u)^2)\), con \(d_k(u)\) la distancia de \(u\) a la
          \(k\)-ésima sede. Allí aparece la otra «ventana», la de observación de los capítulos 4 y 5
          —el perímetro urbano—: el círculo que se sale de ella se recorta.</p>
        <p style="margin-bottom:0;">El módulo 5 toma la primera rama y cambia la ventana rígida
          por un peso que decae con la distancia.</p>""")

MOD4 = cabecera(
    4, TITULOS[3][0], INGLES[3],
    "Derivar el estimador ingenuo k/(nV), ver su sesgo y su varianza en su distribución exacta, y "
    "reconocer las dos maneras de elegir la ventana: fijar su tamaño o fijar cuántos datos "
    "encierra.") + rf"""
      <p>El histograma, el ASH y todo lo que viene después son casos de una misma idea. Para estimar la
        densidad en un punto \(x\) se toma una región \(R\) a su alrededor, de tamaño \(V\) —una
        longitud en la recta, un área en el plano—, y se cuenta cuántos datos caen dentro. En este
        módulo esa región se llama <strong>ventana</strong>; no hay que confundirla con la ventana de
        observación de los capítulos 4 y 5, el recinto donde se miró el patrón.</p>

      <p>La probabilidad de que un dato caiga en \(R\) es \(P = \int_R f(u)\,du\). Si \(R\) es tan
          pequeña que \(f\) casi no cambia dentro de ella, \(P \approx f(x)\,V\). Si además los datos
          son <strong>independientes</strong> —cada uno cae en \(R\) sin mirar dónde cayeron los
          demás—, el número \(k\) de datos que caen en \(R\) es binomial, con \(E(k/n) = P\) y
          \(\operatorname{{Var}}(k/n) = P(1-P)/n\). Como esa varianza se va a cero al crecer \(n\),
          \(k/n\) se acerca a \(P\); y como \(P \approx f(x)\,V\), despejando:</p>

      <div class="formula">
        $$\hat f(x) = \frac{{k}}{{n\,V}}.$$
      </div>

      <p>Es el <strong>estimador ingenuo</strong>. En una dimensión, con \(V = h\) y regiones fijas y
        contiguas —que no se centran en el \(x\) que estiman—, es el histograma; con la región centrada
        en cada \(x\), es el núcleo uniforme del módulo 5. La fórmula enseña la tensión entera de la estimación de
        densidad: con \(V\) grande la aproximación \(P \approx f(x)V\) es mala, porque \(f\) cambia
        dentro de la ventana; con \(V\) pequeña la ventana encierra pocos datos, o ninguno, y \(k\)
        depende del azar. Para que el estimador converja hace falta que \(V\) se encoja y que, a la
        vez, \(k\) crezca: \(V \to 0\), \(k \to \infty\) y \(k/n \to 0\).</p>

      <h3>La distribución exacta, sin simular</h3>

      <p>Como \(k\) es binomial, el comportamiento del estimador se puede calcular entero. Con
        {ent(m4["n_contraste"])} datos de una normal estándar, en \(x = 0\), donde la verdad vale
        {n(m4["f0"], 4)}:</p>

{_M4_TAB1}
      <p>En la ventana más estrecha caben en promedio {n(_VM["esperados"], 2)} de los
        {ent(m4["n_contraste"])} datos. Su valor esperado casi coincide con la verdad, pero la desviación
        típica es {n(_VM["sd"], 4)} —del orden de la propia densidad— y la probabilidad de que la
        ventana quede vacía, y el estimador dé exactamente cero, es {n(_VM["vacia"], 4)}. En la más
        ancha caben {n(_VG["esperados"], 2)}: la nube se estrecha a {n(_VG["sd"], 4)}, pero su centro se
        ha ido a {n(_VG["media"], 4)}, un sesgo de {n(_VG["sesgo"], 4)} que ningún tamaño de muestra
        corrige, porque no viene del azar sino de la ventana. El ancho que minimiza el error total —el
        sesgo al cuadrado más la varianza, el <strong>error cuadrático medio</strong> (ECM) que el
        módulo 8 estudia— se encoge al crecer la muestra, pero despacio: {n(_PN[25]["v_opt"], 2)} con
        {ent(m4["ns"][0])} datos, {n(_PN[100]["v_opt"], 2)} con {ent(m4["ns"][1])},
        {n(_PN[400]["v_opt"], 2)} con {ent(m4["ns"][2])} y {n(_PN[1600]["v_opt"], 2)} con
        {ent(m4["ns"][3])}.</p>

      <p>Cada vez que \(n\) se multiplica por 4, el mejor ancho se divide por {n(m4["razon_v"], 2)},
        muy cerca de \(4^{{1/5}}\) = {n(m4["cuatro_quinta"], 2)}: el mejor ancho baja como
        \(n^{{-1/5}}\), no como el \(n^{{-1/3}}\) del histograma del módulo 2. La diferencia está en que
        esta ventana está <strong>centrada</strong> en el punto que estima. Lo que la pendiente de
        \(f\) añade por un lado de \(x\) lo quita por el otro, y el sesgo que queda es de orden
        \(V^2\), no \(V\); la casilla de un histograma casi nunca está centrada en el \(x\) que estima.
        En \(x\) = 0 esa diferencia no se ve, porque allí la pendiente es nula y hasta una casilla
        \([0, V)\) baja casi igual. Se ve en un punto con pendiente: en \(x\) =
        {n(m4["pendiente"]["x"], 1)}, cada vez que \(n\) se cuadruplica, el mejor ancho de la ventana
        centrada se divide por {n(m4["pendiente"]["razon_centrada"], 2)} y el de la casilla
        \([x, x + V)\), por {n(m4["pendiente"]["razon_casilla"], 2)}, camino del \(4^{{1/3}}\) =
        {n(m4["pendiente"]["cuatro_tercio"], 2)} del histograma. El módulo 8 hace la cuenta.</p>

{_M4_SIM}
{_M4_LEE}
      <h3>Dos maneras de elegir la ventana</h3>

      <p>La fórmula \(k/(nV)\) tiene dos cantidades que se pueden fijar. Si se fija el
        <strong>tamaño</strong> \(V\) y se cuenta cuántos datos caen dentro, se obtienen las
        <strong>ventanas de Parzen</strong> (módulo 5). Si se fija el <strong>número</strong> \(k\)
        y se deja que la ventana crezca hasta encerrarlos, se obtienen los <strong><em>k</em> vecinos
        más cercanos</strong> (módulo 7). La figura lo hace en el plano, sobre una esquina de Kennedy:
        en el panel «Radio fijo», los tres círculos tienen {n(_P4["radio_km"], 1)} km de radio y
        encierran cantidades muy distintas de sedes; en el panel «k fijo», cada círculo llega a la
        {ent(_P4["k"])}.ª sede más cercana y su tamaño se adapta a lo concurrido del sitio.</p>

{svg_plano()}
{_M4_TAB2}
      <p>Los dos estimadores casi coinciden en el sitio intermedio y se separan en los extremos. En el
        denso, el círculo fijo promedia {ent(SIT[0]["parzen_conteo"])} sedes sobre un área grande y el
        de <em>k</em> vecinos se encoge a {n(SIT[0]["knn_radio"], 3)} km y lee un pico más local. En el
        ralo, el círculo fijo encierra {ent(SIT[2]["parzen_conteo"])} sede y su estimación depende de
        esa única sede, mientras que el de <em>k</em> vecinos se agranda hasta
        {n(SIT[2]["knn_radio"], 2)} km para tener siempre {ent(_P4["k"])}.</p>

      <h3>Por qué el plano es más difícil que la recta</h3>

      <p>En \(d\) dimensiones la ventana es un volumen \(V = h^d\). Para encerrar el 10 % de unos datos
        repartidos por igual en un cubo de lado 1, su lado tiene que medir
        {n(_DIM["lado_10pct"][0], 2)} en la recta, {n(_DIM["lado_10pct"][1], 2)} en el plano y
        {n(_DIM["lado_10pct"][3], 2)} en diez dimensiones: la ventana deja de ser local. El error del
        estimador de núcleo con su mejor ancho —el de los módulos 5 a 8— decae como
        \(n^{{-4/(4+d)}}\); en la recta, \(n^{{-4/5}}\), más deprisa que el \(n^{{-2/3}}\) del histograma.
        Para bajarlo a la mitad hacen falta {n(_DIM["datos_para_mitad"][0], 2)} veces más datos en la
        recta, {n(_DIM["datos_para_mitad"][1], 2)} en el plano —lo mismo que el histograma pedía en la
        recta—, {n(_DIM["datos_para_mitad"][2], 2)} en tres dimensiones y
        {n(_DIM["datos_para_mitad"][3], 1)} en diez. Es la <strong>maldición de la dimensión</strong>,
        y el plano todavía la sufre poco.</p>

{_M4_COD}
      <p>El bloque no simula ninguna muestra: <code>pnorm(V / 2) - pnorm(-V / 2)</code> es la
        probabilidad \(P\) de que un dato normal caiga en la ventana, y de ella salen el centro y la
        dispersión de \(k/(nV)\) por las fórmulas de la binomial. La penúltima línea de cada pestaña
        es la probabilidad de que la ventana quede vacía, \((1-P)^n\), que es el caso en que el
        estimador da exactamente cero.</p>

{_M4_PLANO}""" + CIERRE

_U5, _G5, _FR5 = m5["uniforme"], m5["gaussiano"], m5["frontera"]
_M5_TRAMPA = trampa(r"\(|u| \le 1\) o \(|u| \lt 1\)", rf"""El núcleo uniforme se escribe con las dos
        desigualdades, y al integrar dan lo mismo, porque solo difieren en los dos puntos
        \(u = \pm 1\). Pero el cálculo en un punto sí cambia. Con los datos
        {{{", ".join(ent(v) for v in _FR5["datos"])}}}, \(h\) = 1 y \(x\) = {ent(_FR5["x"])}, los datos
        3 y 5 están exactamente en el borde de la ventana: con \(\le\) cuentan y
        \(\hat f\) = {n(_FR5["le"], 1)}; con \(\lt\) no cuentan y \(\hat f\) = {n(_FR5["lt"], 1)}. Cuando
        dos fuentes dan cifras distintas en un ejemplo así, conviene mirar primero qué desigualdad
        usó cada una.""")
_M5_TAB = tabla([r"\(h\)", "Uniforme", "Gaussiano"],
                "".join(fila(n(t["h"], 1), n(t["uniforme"], 4), n(t["gaussiano"], 4))
                        for t in m5["tabla"]),
                f"La densidad estimada en x = {ent(_G5['x'])} con los datos "
                f"{{{', '.join(ent(v) for v in _G5['datos'])}}}, dos núcleos y tres anchos.")
_M5_SIM = sim(
    "apa-lomas", "Una loma por dato: el estimador gaussiano de cinco datos",
    "Las cinco líneas finas son las lomas, una por dato, cada una con área 1/5; la línea gruesa es su "
    "suma, la densidad estimada. Las marcas del eje son los datos. El deslizador cambia el ancho h, "
    f"que arranca en {n(m5['h_inicial'], 2)}. Antes de moverlo: ¿con qué h crees que las cinco lomas "
    "se funden en una sola montaña?")
_TR5 = m5["tramos"]
_M5_LEE = como_se_lee(rf"""        <p>Con \(h\) pequeño cada dato levanta su propia loma y la curva tiene tantas modas
          como datos: {ent(_TR5[0]["modas"])} hasta \(h\) = {n(_TR5[0]["hasta"], 2)}. Al crecer \(h\)
          las lomas se solapan y las modas se funden por pasos: {ent(_TR5[1]["modas"])} entre
          {n(_TR5[1]["desde"], 2)} y {n(_TR5[1]["hasta"], 2)}; {ent(_TR5[2]["modas"])} entre
          {n(_TR5[2]["desde"], 2)} y {n(_TR5[2]["hasta"], 2)}, una para el grupo de 2 a 5 y otra para el
          7, que está aislado; y {firma(ent(_TR5[3]["modas"]))} desde \(h\) = {n(_TR5[3]["desde"], 2)}.</p>
        <p style="margin-bottom:0;">Ninguno de esos números es «el» número de modas de los datos; es el
          número de modas <em>a esa escala</em>. Con cinco datos no hay manera de saber si el 7 es un
          grupo aparte o un dato suelto del mismo grupo: esa pregunta la contestan los módulos 10 y 11,
          con más datos y un criterio para elegir \(h\).</p>""")
_M5_COD = tabs("Ventanas de Parzen a mano, en R y en Python", esc(R5.format(**SUB5)), esc(PY5.format(**SUB5)))
_M5_PLANO = en_el_plano(r"""        <p><code>density.ppp</code> de spatstat calcula esta suma en el plano,
          \(\sum_i k_\sigma(u - x_i)\), una loma bidimensional sobre cada sede: exactamente así con
          <code>edge = FALSE</code>, y por defecto dividida además por una corrección de borde que el
          módulo 12 de este apéndice explica en una dimensión. No divide por \(n\), así que el
          resultado es una intensidad y no una densidad. El módulo 1 del capítulo 5 lo dice con las
          mismas palabras: el peso lo pone una función que decae con la distancia —el núcleo— y su
          anchura, σ, ocupa el lugar del tamaño de celda.</p>
        <p style="margin-bottom:0;">El módulo 6 pregunta qué importa más de la loma: su forma o su
          anchura.</p>""")

MOD5 = cabecera(
    5, TITULOS[4][0], INGLES[4],
    "Escribir el estimador de Parzen-Rosenblatt, calcularlo a mano y ver cómo el ancho h decide "
    "cuántas modas aparecen.") + rf"""
      <p>El estimador ingenuo cuenta los datos de una ventana rígida: un dato dentro pesa lo mismo esté
        en el centro o en el borde, y un dato justo fuera no pesa nada. Las <strong>ventanas de
        Parzen</strong> (Rosenblatt, 1956; Parzen, 1962) cambian ese corte por un peso \(K\) que
        decide cuánto aporta cada dato según su distancia a \(x\):</p>

      <div class="formula">
        $$\hat f(x) = \frac{{1}}{{n\,h}} \sum_{{i=1}}^{{n}} K\!\left(\frac{{x - x_i}}{{h}}\right),
          \qquad K(u) \ge 0, \quad \int K(u)\,du = 1, \quad K(-u) = K(u).$$
      </div>

      <p>\(K\) es el <strong>núcleo</strong> y \(h\) el <strong>ancho de
          banda</strong>. Con el núcleo uniforme, \(K(u) = \tfrac12\) si \(|u| \le 1\), es
          exactamente \(k/(nV)\) con una ventana de ancho \(V = 2h\) centrada en \(x\).</p>

      <h3>A mano, con una caja</h3>

      <p>Con los datos {{{", ".join(ent(v) for v in _U5["datos"])}}}, núcleo uniforme y \(h\) = 1, en
        \(x = 3\) la ventana \([2, 4]\) recoge los datos 2, 3 y 4, cada uno con peso
        \(K = \tfrac12\): los cinco sumandos son {", ".join(f"{v:g}" for v in _U5["terminos_x3"])},
        suman {_U5["suma_x3"]:g} y \(\hat f(3)\) = {n(_U5["f"][2], 1)}. En los cinco datos la
        estimación vale {", ".join(n(v, 1) for v in _U5["f"])}: baja en los extremos porque allí la
        ventana solo encuentra vecinos de un lado. Si los datos no pudieran pasar de 1 ni de 5, esa
        caída sería un error: es la primera aparición de un problema que el módulo 12 resuelve, el
        <strong>borde</strong>.</p>

{_M5_TRAMPA}
      <h3>Con una campana</h3>

      <p>El núcleo gaussiano, \(K(u) = \phi(u)\) —la densidad normal estándar—, no tiene borde: todo dato pesa algo, menos cuanto
        más lejos. Con los datos {{{", ".join(ent(v) for v in _G5["datos"])}}} y \(h\) = 1, en \(x = 4\)
        los cinco pesos \(\phi(4 - x_i)\) son {", ".join(n(v, 4) for v in _G5["terminos"])}; suman
        {n(_G5["suma"], 4)} y \(\hat f(4)\) = {firma(n(_G5["f"], 4))}. El uniforme da
        {n(m5["tabla"][1]["uniforme"], 1)} en el mismo punto, pero la comparación no es justa, por dos
        motivos. Con \(h\) = 1 la caja tiene desviación típica {n(m5["caja"]["sd_h1"], 3)} y la campana
        1: la caja mira más cerca de \(x\). Y ese {n(m5["tabla"][1]["uniforme"], 1)} es el caso de borde
        de la trampa de arriba, con los datos 3 y 5 justo en \(\pm h\). Si la caja se estira hasta tener
        la misma desviación típica que la campana —semiancho \(\sqrt3\) = {n(m5["caja"]["semiancho_sd1"], 3)}—
        da {firma(n(m5["caja"]["f_sd1"], 4))}, junto al {n(_G5["f"], 4)} de la campana. El módulo 6
        convierte esta observación en una regla.</p>

{_M5_TAB}
      <p>La columna del uniforme sube y baja porque cuenta datos enteros: un dato que entra en la ventana
        suma de golpe, y con \(h\) = 1 y con \(h\) = 2 hay datos que caen justo en su borde. La del
        gaussiano cambia suavemente, porque ningún dato entra ni sale: solo pesa más o menos.</p>
      <h3>Una loma por cada dato</h3>

      <p>La fórmula se lee mejor al revés. Con \(K_h(u) = K(u/h)/h\) —el núcleo estirado al ancho
        \(h\), que sigue teniendo área 1—, en vez de «para cada \(x\), sumar los pesos de los
        datos», «sobre cada dato, poner una loma \(K_h(x - x_i)/n\) de área \(1/n\), y sumar las
        lomas». La
        densidad estimada es una suma de \(n\) montoncitos de arena, y el ancho de banda es lo ancho
        de cada montón. El capítulo 5 escribe \(k_\sigma\) para lo mismo en el plano: el núcleo ya
        estirado a su ancho σ.</p>

      <p>Un aviso sobre la letra \(h\), que ha ido cambiando de papel sin decirlo. En el histograma era
        el ancho <em>entero</em> de la barra. En un núcleo con soporte \([-1, 1]\), como la caja de
        arriba, es el <em>semiancho</em>: la caja de \(h\) = 1 va de \(x - 1\) a \(x + 1\). Y en el
        gaussiano, cuyo soporte es toda la recta, es la <em>desviación típica</em> de la loma. El módulo 6 pone
        orden: para comparar núcleos, lo que hay que igualar es la desviación típica.</p>

{_M5_SIM}
{_M5_LEE}
{_M5_COD}
      <p>El bloque escribe el estimador en una línea, <code>mean(K((t - datos) / h)) / h</code>, y
        se lo pasa a dos núcleos distintos: la caja, como función propia, y <code>dnorm</code>, que
        ya es un núcleo gaussiano. La última línea cuenta las modas sobre una rejilla de 500 puntos
        para cuatro anchos, con la misma función de modas del módulo 2: es la prueba numérica de lo
        que el simulador deja ver.</p>

{_M5_PLANO}""" + CIERRE

_NK = [NUC[k] for k in ("gaussiano", "epanechnikov", "uniforme", "triangular", "biweight", "triweight")]
_FORMULAS6 = {
    "gaussiano": r"\(\phi(u)\)",
    "epanechnikov": r"\(\tfrac34(1-u^2)\)",
    "uniforme": r"\(\tfrac12\)",
    "triangular": r"\(1-|u|\)",
    "biweight": r"\(\tfrac{15}{16}(1-u^2)^2\)",
    "triweight": r"\(\tfrac{35}{32}(1-u^2)^3\)",
}
_UNI6, _TRI6 = m6["unimodal"], m6["trimodal"]


def _fila_nucleo(k):
    soporte = "toda la recta" if k["nombre"] == "gaussiano" else n(k["soporte_por_sigma"], 3)
    return fila(k["nombre"].capitalize(), _FORMULAS6[k["nombre"]], n(k["mu2"], 4), n(k["RK"], 4),
                n(k["eficiencia"], 4), soporte)


_M6_TAB = tabla(["Núcleo", r"\(K(u)\) en \(|u| \le 1\)", r"\(\mu_2(K)\)", r"\(R(K)\)",
                 "Eficiencia", "Soporte por σ"],
                "".join(_fila_nucleo(k) for k in _NK),
                "Seis núcleos: cinco escritos sobre el soporte [−1, 1] y el gaussiano, cuyo soporte es "
                "toda la recta. Sus dos constantes, su eficiencia respecto del Epanechnikov y el semiancho "
                "del soporte cuando la desviación típica vale 1.")
_MS6 = m6["mismo_soporte"]
_M6_SIM = sim(
    "apa-nucleos", "Cinco núcleos sobre la misma muestra trimodal",
    "Los botones de «núcleo» eligen la forma; los de «igualar por», cómo se iguala el ancho: con la misma "
    "desviación típica (lo que hace density() de R) o con el mismo soporte, el del Epanechnikov de R, "
    "que llega a √5 veces el ancho. La curva gris es la estimación hecha con el núcleo gaussiano, de "
    "referencia. La lectura cuenta los máximos locales y mide la mayor "
    "diferencia con la referencia. Antes de pulsar: ¿cuál de los dos modos de igualar crees que "
    "separa más las curvas?", alto=300)
_M6_LEE = como_se_lee(rf"""        <p>Con la misma desviación típica las curvas casi se superponen —la mayor diferencia con
          el gaussiano es {n(_MS6["caja"]["dif_misma_sd"], 4)} para la caja,
          {n(_MS6["biweight"]["dif_misma_sd"], 4)} para el biweight y
          {n(_MS6["triangular"]["dif_misma_sd"], 4)} para el triangular, sobre un pico de
          {n(_TRI6["max_gauss"], 4)}— pero no son igual de lisas: la caja tiene
          {ent(_TRI6["modas_rect"])} máximos locales contra {ent(_TRI6["modas_gauss"])} del gaussiano.
          Su curva es una escalera, y cada peldaño que sube y vuelve a bajar cuenta como un máximo.</p>
        <p style="margin-bottom:0;">Con el mismo soporte, en cambio, la caja se aleja: su desviación
          típica sube a {n(_MS6["caja"]["sd_mismo_soporte"], 3)} y su mayor diferencia con el gaussiano
          pasa a {n(_MS6["caja"]["dif_mismo_soporte"], 4)}. El biweight, que se estrecha a
          {n(_MS6["biweight"]["sd_mismo_soporte"], 3)}, pasa a {n(_MS6["biweight"]["dif_mismo_soporte"], 4)}.
          El triangular casi no cambia ({n(_MS6["triangular"]["dif_mismo_soporte"], 4)}), porque su soporte
          por desviación típica, \(\sqrt6\), está muy cerca del \(\sqrt5\) del Epanechnikov. El mismo
          número ya no es el mismo suavizado.</p>""")
_M6_TRAMPA = trampa("el mismo número no es el mismo ancho", rf"""En R, <code>bw</code> es la
        desviación típica del núcleo, y <code>density(kernel = "epanechnikov", bw = 1)</code> llega a
        \(\pm\sqrt5\) = \(\pm\){n(m6["density_soporte"]["epanechnikov"], 3)}. En
        <code>KernelDensity</code> de sklearn, <code>bandwidth</code> es el radio del soporte en los
        núcleos que lo tienen —con 1 el Epanechnikov acaba en 1— y solo en el gaussiano es la
        desviación típica. En <code>scipy.stats.gaussian_kde</code> hay una tercera: un
        <code>bw_method</code> numérico no es un ancho sino un <em>factor</em> que multiplica la
        desviación típica de los datos. Con una muestra de {ent(m7["ingresos"]["n"])} ingresos anuales,
        en miles de dólares, que vuelve en el módulo 7, y el ancho de la regla <code>bw.nrd</code>
        (módulo 9), {n(m7["ingresos"]["h"], 2)}, el Epanechnikov da en \(x\) = {ent(m7["ingresos"]["x"])}
        {n(m7["ingresos"]["epa_density"], 5)} con la convención de R y {n(m7["ingresos"]["epa_soporte"], 5)}
        con la de sklearn. El gaussiano, con el mismo número en la convención de R, da
        {n(m7["ingresos"]["gauss"], 5)}: igualar la desviación típica es igualar el suavizado, y los dos
        núcleos casi coinciden. El <code>sigma</code> de spatstat sigue la convención de R.""")
_M6_COD = tabs("Las constantes y la convención de cada lenguaje, en R y en Python",
               esc(R6.format(**SUB6)), esc(PY6.format(**SUB6)))
_PL6 = m6["plano"]
_M6_PLANO = en_el_plano(rf"""        <p>El módulo 2 del capítulo 5 compara cuatro núcleos «al mismo σ» y encuentra que el
          núcleo mueve el pico de la intensidad unos pocos por ciento, y el ancho mucho más: es este
          mismo módulo en el plano. La advertencia de allí —«al mismo σ» es a la misma desviación
          típica, no al mismo soporte— tiene aquí sus cifras. En el plano los soportes son otros,
          porque la desviación típica se mide por coordenada: el cuadrado del radio del soporte es
          {ent(_PL6["epanechnikov"])} veces \(\sigma^2\) para el Epanechnikov, {ent(_PL6["cuartico"])}
          para el cuártico (<em>quartic</em> en spatstat: el biweight de la tabla) y
          {ent(_PL6["disco"])} para el disco (<em>disc</em>: la caja en el plano), contra {n(NUC["epanechnikov"]["h2_sobre_sigma2"], 0)},
          {n(NUC["biweight"]["h2_sobre_sigma2"], 0)} y {n(NUC["uniforme"]["h2_sobre_sigma2"], 0)} en la recta.</p>
        <p style="margin-bottom:0;">Fijado el ancho, falta la otra rama del módulo 4: fijar cuántos
          datos encierra la ventana. Es el módulo 7.</p>""")

MOD6 = cabecera(
    6, TITULOS[5][0], INGLES[5],
    "Comparar núcleos con la misma escala, saber qué significa «el mismo ancho» en R, en Python y "
    "en spatstat, y medir cuánto importa la forma del núcleo frente a su anchura.") + rf"""
      <p>Un núcleo tiene una <strong>forma</strong> y una <strong>escala</strong>. La forma es la
        función \(K\); la escala es \(h\). La tabla reúne los seis núcleos habituales con las dos
        constantes que gobiernan su comportamiento: \(\mu_2(K) = \int u^2 K(u)\,du\), la varianza del
        núcleo, que fija el sesgo; y \(R(K) = \int K(u)^2\,du\), que fija la varianza del estimador
        (módulo 8). La literatura llama a \(R(K)\) la <em>rugosidad</em> (<em>roughness</em>) del
        núcleo, pero no mide lo dentada que sale la curva estimada: eso depende de lo suave que sea
        \(K\).</p>

{_M6_TAB}
      <p>Las dos columnas de constantes hay que leerlas con cuidado, porque dependen de la escala en
        que se escribió el núcleo. Escritos así, el gaussiano parece tener mucho más
        \(\mu_2\) que los demás, y eso es un artefacto. Si se estiran todos hasta tener desviación
        típica 1, \(\mu_2\) vale 1 en todos y \(R(K)\) va de {n(NUC["epanechnikov"]["RK_sd1"], 3)} en el
        Epanechnikov a {n(NUC["uniforme"]["RK_sd1"], 3)} en la caja. Ese \(R(K)\) igualado es
        \(R(K)\sqrt{{\mu_2(K)}}\), la combinación con que se calcula la eficiencia. Y ni igualado
        ordena la suavidad de la curva: el gaussiano tiene más \(R(K)\) que el Epanechnikov
        ({n(NUC["gaussiano"]["RK_sd1"], 3)} contra {n(NUC["epanechnikov"]["RK_sd1"], 3)}) y, sin
        embargo, deja una sola moda en la muestra unimodal de abajo, donde el Epanechnikov deja
        {ent(_UNI6["modas_epan"])}.</p>

      <p>La columna de <strong>eficiencia</strong> compara cada núcleo con el Epanechnikov, que es el
        óptimo (Epanechnikov, 1969): el gaussiano llega a {n(NUC["gaussiano"]["eficiencia"], 4)} y la
        caja, el peor de los habituales, a {n(NUC["uniforme"]["eficiencia"], 4)}. Es un cociente de
        tamaños de muestra: con la caja hacen falta {n(NUC["uniforme"]["datos_para_igualar"], 3)} veces
        más observaciones para igualar el error del Epanechnikov. Con los mismos datos, su error es
        {n(NUC["uniforme"]["error_relativo"], 3)} veces mayor. Es una diferencia real y pequeña, y el
        resto del módulo la pone en su sitio.</p>

      <h3>La misma escala, otra forma</h3>

      <p>Las dos muestras de esta comparación son simuladas: una unimodal de {ent(_UNI6["n"])} datos,
        normal de media {ent(_UNI6["mu"])} y desviación {ent(_UNI6["sd"])}, y otra trimodal de
        {ent(_TRI6["n"])}, con {ent(_TRI6["n1"])}, {ent(_TRI6["n2"])} y {ent(_TRI6["n3"])} datos alrededor
        de {ent(_TRI6["mu"][0])}, {ent(_TRI6["mu"][1])} y {ent(_TRI6["mu"][2])}. Con el ancho fijo que R
        usa por defecto, el de <code>bw.nrd0</code> (módulo 9), y tres núcleos, la mayor diferencia entre
        la curva gaussiana y la de la caja es {n(_UNI6["dif_rect"], 4)} sobre un pico de
        {n(_UNI6["max_gauss"], 4)} en la primera y {n(_TRI6["dif_rect"], 4)} sobre
        {n(_TRI6["max_gauss"], 4)} en la segunda.</p>

      <p>Las tres modas grandes de la trimodal aparecen con los tres núcleos. Lo que cambia es el resto.
        Sobre la unimodal, la caja tiene {ent(_UNI6["modas_rect"])} máximos locales y el Epanechnikov
        {ent(_UNI6["modas_epan"])}, contra {ent(_UNI6["modas_gauss"])} del gaussiano. Cada loma de un
        núcleo con soporte acaba en seco —la caja con un salto, el Epanechnikov con un quiebre de la
        pendiente—, y en las colas, donde se solapan pocas lomas, esos bordes dejan dientes. La forma no
        mueve las modas grandes; sí decide cuántos dientes las acompañan.</p>

{_M6_TRAMPA}
{_M6_SIM}
{_M6_LEE}
{_M6_COD}
      <p>El bloque integra las dos constantes de tres núcleos con <code>integrate()</code> (en Python,
        <code>quad</code>) y calcula la eficiencia como el cociente de \(R(K)\sqrt{{\mu_2(K)}}\)
        contra el del Epanechnikov, que es la combinación que aparece en el error del módulo 8. La
        segunda mitad pone las dos convenciones lado a lado en el mismo punto, \(x = 2\): el núcleo
        de R con <code>bw = 1</code> todavía pesa allí, y el de sklearn con
        <code>bandwidth = 1</code> ya no; para obtener el de R hay que pasarle \(\sqrt5\) veces el
        ancho.</p>

{_M6_PLANO}""" + CIERRE

_E7, _I7, _MZ = m7["edades"], m7["ingresos"], m7["mezcla"]
_K7 = {p["k"]: p for p in _MZ["por_k"]}
_M7_SIM = sim(
    "apa-knn", "k vecinos sobre una mezcla de dos normales",
    "La curva verde es la estimación con k vecinos; la discontinua, la densidad verdadera de la "
    "mezcla. El deslizador cambia k, y el botón de la lupa amplía el tramo de 4.5 a 5.5, cerca de la "
    "primera moda, con una rejilla mucho más fina. La lectura cuenta los picos de la curva en la "
    "rejilla del simulador y en la de la lupa, mide su área dentro del rango de los datos y compara "
    f"la estimación en el valle, x = {n(_MZ['valle_x'], 1)}, con la verdad. Antes de moverlo: ¿crees "
    "que con k grande la curva queda lisa?", alto=300)
_M7_LEE = como_se_lee(rf"""        <p>La curva del <em>k</em>-NN tiene dientes por construcción, no por azar. La distancia
          \(d_k(x)\) al \(k\)-ésimo vecino es una función lineal a trozos de \(x\): baja mientras \(x\) se
          acerca al centro de un grupo de \(k\) datos consecutivos y sube cuando se aleja, así que tiene
          un mínimo en el punto medio de muchos de esos grupos, y en cada mínimo \(k/(2n\,d_k)\) hace
          un pico agudo. Con \(k\) = {ent(_MZ["por_k"][0]["k"])} la rejilla del simulador cuenta
          {ent(_MZ["por_k"][0]["modas"])} picos; con \(k\) = {ent(_MZ["por_k"][2]["k"])},
          {ent(_MZ["por_k"][2]["modas"])}; con \(k\) = {ent(_MZ["por_k"][5]["k"])} todavía
          {ent(_MZ["por_k"][5]["modas"])}. A escala completa la curva de \(k\) =
          {ent(_MZ["por_k"][5]["k"])} parece lisa; la lupa enseña que no lo es. Y cuántos picos se
          cuentan depende también de lo fino que se mire, porque muchos dientes son más estrechos que la
          distancia entre dos puntos de la rejilla. Subir \(k\) redondea la forma general, pero la curva
          sigue siendo continua y no derivable.</p>
        <p style="margin-bottom:0;">Y en el valle es inestable: en \(x\) = {n(_MZ["valle_x"], 1)}
          la estimación vale {n(_MZ["por_k"][1]["f_valle"], 4)} con \(k\) = {ent(_MZ["por_k"][1]["k"])},
          {n(_MZ["por_k"][2]["f_valle"], 4)} con \(k\) = {ent(_MZ["por_k"][2]["k"])} y
          {n(_MZ["por_k"][5]["f_valle"], 4)} con \(k\) = {ent(_MZ["por_k"][5]["k"])}, contra
          {n(_MZ["f_valle_verdad"], 4)} de la verdad. Con pocos vecinos manda el azar de la muestra
          —la varianza—; con muchos, la ventana se abre hasta los grupos vecinos y se trae su densidad
          —el sesgo—. Que \(k\) = {ent(_MZ["por_k"][2]["k"])} acierte aquí no lo hace mejor en otro
          punto.</p>""")
_M7_COD = tabs("k vecinos a mano, en R y en Python", esc(R7.format(**SUB7)), esc(PY7.format(**SUB7)))
_M7_PLANO = en_el_plano(r"""        <p>La distancia al vecino más cercano, \(d_1\), es la protagonista del capítulo 4: el
          índice de Clark-Evans la promedia y la función \(G\) la acumula. Su generalización,
          \(d_k\), da el estimador de intensidad <code>nndensity</code> de spatstat, que el módulo 4
          ya presentó: es este módulo en el plano. <code>adaptive.density</code> reúne los estimadores
          de ancho variable; su método de núcleo, <code>densityAdaptiveKernel</code>, pone el ancho en
          cada sede y no en cada punto del mapa —es un estimador de punto muestral—, y por eso, sobre
          todo el plano, sí integra el número de sedes; dentro de una ventana depende de la corrección
          de borde (módulo 12). El capítulo 6 usa la
          misma idea para otra cosa —<code>knearneigh</code> declara vecinas a las \(k\) unidades más
          cercanas— y el 8, todavía en preparación, la usará para el ancho <em>adaptativo</em> de
          la regresión geográficamente ponderada, que se fija en número de vecinos y no en
          metros.</p>
        <p style="margin-bottom:0;">Ya están los dos estimadores. El módulo 8 mide su error.</p>""")

MOD7 = cabecera(
    7, TITULOS[6][0], INGLES[6],
    "Estimar con k vecinos, entender por qué esa curva no integra 1 y tiene dientes, y reconocerla "
    "como un estimador de núcleo de ancho variable.") + rf"""
      <p>La otra rama del módulo 4 fija el número de datos y deja que la ventana crezca hasta
        encerrarlos. Si \(d_k(x)\) es la distancia de \(x\) a su \(k\)-ésimo vecino más cercano, la
        ventana es el intervalo \([x - d_k, x + d_k]\), de longitud \(2\,d_k\), y</p>

      <div class="formula">
        $$\hat f(x) = \frac{{k}}{{n \cdot 2\,d_k(x)}}.$$
      </div>

      <p>Donde los datos se apiñan, \(d_k\) es pequeña y la estimación
          sube; donde escasean, \(d_k\) crece y la estimación baja. El ancho se adapta solo.</p>

      <h3>A mano, y el problema de los empates</h3>

      <p>Con las edades {{{", ".join(ent(v) for v in _E7["datos"])}}} y \(k\) = {ent(_E7["k"])}, en
        \(x\) = {ent(_E7["x"])} las distancias ordenadas son {", ".join(ent(v) for v in _E7["distancias"])}.
        El tercer vecino está a \(d_3\) = {ent(_E7["d_k"])}, la ventana mide {ent(_E7["V"])} y
        \(\hat f\) = {ent(_E7["k"])}/({ent(len(_E7["datos"]))} × {ent(_E7["V"])}) =
        {firma(n(_E7["f"], 4))}. Pero el 35 está a la misma distancia que el 25, así que la ventana
        encierra {ent(_E7["dentro"])} datos y no {ent(_E7["k"])}: el estimador «cobra» \(k\) aunque
        cuente más. Si se usaran los {ent(_E7["dentro"])}, saldría {n(_E7["balloon"], 4)}. Con datos
        redondeados los empates son la norma, y cuando hay \(k\) o más datos <em>iguales</em> a \(x\),
        \(d_k = 0\) y el estimador vale infinito: el ejercicio 8 lo encuentra en los tiempos de espera
        de la caja de una tienda.</p>

      <p>Los {ent(_I7["n"])} ingresos anuales del módulo 6, en miles de dólares, vuelven aquí con el
        mismo problema. En \(x\) = {ent(_I7["x"])} y con \(k\) = {ent(_I7["k"])}, las distancias más
        cortas son {", ".join(ent(v) for v in _I7["distancias_4"])}: el tercer vecino está a
        {ent(_I7["radio"])} y empata con el cuarto. El <em>k</em>-NN da {firma(n(_I7["knn"], 4))}, del
        orden del {n(_I7["epa_density"], 4)} que el Epanechnikov daba en el módulo 6, pero su ventana
        vuelve a encerrar {ent(_I7["dentro"])} datos y cobrar {ent(_I7["k"])}.</p>

      <h3>No es una densidad</h3>

      <p>Lejos de los datos, \(d_k(x)\) crece como la distancia a ellos, y la estimación decae como
        \(1/|x|\): demasiado despacio para que su integral converja. Con {ent(_I7["n"])} ingresos y
        \(k\) = {ent(_I7["k"])}, el área bajo la curva vale {n(_I7["areas"][0]["area"], 4)} entre
        {ent(_I7["areas"][0]["desde"])} y {ent(_I7["areas"][0]["hasta"])},
        {n(_I7["areas"][1]["area"], 4)} si la ventana se abre a [{ent(_I7["areas"][1]["desde"])},
        {ent(_I7["areas"][1]["hasta"])}] y {n(_I7["areas"][2]["area"], 4)} si se abre a
        [{ent(_I7["areas"][2]["desde"])}, {ent(_I7["areas"][2]["hasta"])}]: sigue creciendo sin
        tope. El <em>k</em>-NN sirve para leer la concentración local de los datos, no para calcular
        probabilidades con su área.</p>

      <h3>Con muchos datos: una mezcla</h3>

      <p>Una muestra de {ent(_MZ["n"])} datos, mitad de una normal de media {ent(_MZ["medias"][0])} y
        desviación {ent(_MZ["sd"][0])}, mitad de una de media {ent(_MZ["medias"][1])} y desviación
        {n(_MZ["sd"][1], 1)}, tiene dos modas y un valle hacia \(x\) = {n(_MZ["valle_x"], 1)}, donde
        la verdad vale {n(_MZ["f_valle_verdad"], 4)}. Es una <strong>mezcla</strong> de dos normales,
        como la cafetería del módulo 1 y como la verdad que fabrica el módulo 11, y tiene una ventaja
        sobre los datos reales: su densidad verdadera se conoce, así que el error se puede ver. Es
        también la muestra del ejercicio 3.</p>

{_M7_SIM}
{_M7_LEE}
      <h3>El <em>k</em>-NN es un núcleo de ancho variable</h3>

      <p>Comparado con la fórmula del módulo 5, el <em>k</em>-NN es un estimador de núcleo uniforme
        cuyo ancho cambia con el punto: \(h(x) = d_k(x)\). Salvo con empates: en las edades, una caja
        de semiancho \(d_3\) cuenta los {ent(_E7["dentro"])} datos y da {n(_E7["balloon"], 4)}, mientras
        el <em>k</em>-NN cobra {ent(_E7["k"])} y da {n(_E7["f"], 4)}. Los estimadores que dejan variar el
        ancho con el punto de evaluación se llaman <em>balloon</em> (globo), porque el ancho se infla
        y desinfla al recorrer la recta; la diferencia con el <em>k</em>-NN es cómo se elige \(h(x)\),
        que en el <em>k</em>-NN lo decide el número de vecinos y en otros <em>balloon</em> una
        estimación piloto de \(f\).</p>

      <p>Ninguno integra 1 en general, y la razón no es la de las colas del <em>k</em>-NN: como el
        ancho depende del punto donde se mira, cada dato deja de tener una loma propia de área
        \(1/n\). Hay otra familia que deja variar el ancho <em>por dato</em>, no por punto: cada dato
        lleva su loma, más ancha si su entorno está vacío y más estrecha si está concurrido, y cada
        loma conserva su área \(1/n\). Esos estimadores de <em>punto muestral</em> sí integran 1. La
        versión más usada pone en cada dato un ancho inversamente proporcional a la raíz de una
        estimación piloto en ese dato. Dejar que el ancho cambie solo compensa cuando la escala de
        los datos cambia mucho de una zona a otra; si no, el ancho fijo es más estable, y el módulo 8
        dice por qué.</p>

{_M7_COD}
      <p>El bloque hace a mano el ejemplo de las edades —<code>sort(abs(X - x0))</code> son las
        distancias ordenadas y su elemento \(k\) es \(d_k\)— y cuenta con
        <code>sum(abs(X - x0) &lt;= d[k])</code> cuántos datos caen de verdad en la ventana. La
        segunda mitad integra la curva de los ingresos por trapecios sobre tres intervalos cada vez
        más anchos: el área crece en cada uno, que es lo que «no integra 1» significa en la
        práctica.</p>

{_M7_PLANO}""" + CIERRE

_A8 = m8["asintotica"]
_M8_DER = derivacion("der-ecm", r"Ver por qué el ECM es sesgo al cuadrado más varianza", [
    r"""              <p>Se suma y se resta el valor esperado del estimador, \(E\hat f(x)\), dentro del
                cuadrado:</p>
              $$E\big[(\hat f(x) - f(x))^2\big] = E\big[(\hat f(x) - E\hat f(x) + E\hat f(x) - f(x))^2\big].$$""",
    r"""              <p>Al desarrollar el cuadrado aparecen tres términos. El cruzado se anula, porque
                \(E\hat f(x) - f(x)\) es una constante y \(E[\hat f(x) - E\hat f(x)] = 0\):</p>
              $$\text{ECM}(x) = \underbrace{E\big[(\hat f(x) - E\hat f(x))^2\big]}_{\operatorname{Var}\hat f(x)}
                + \underbrace{\big(E\hat f(x) - f(x)\big)^2}_{\text{sesgo}^2}.$$"""],
    r"""La varianza mide cuánto cambiaría la estimación con otra muestra; el sesgo, cuánto se
    equivoca en promedio. Integrada sobre \(x\), la misma descomposición vale para el error de toda
    la curva, que se define más abajo.""")
_M8_SIM_NUBE = sim(
    "apa-nube", "Treinta muestras, treinta curvas: el sesgo y la varianza a la vista",
    f"Cada línea gris es la estimación de núcleo gaussiano de una muestra de {ent(m8['n'])} datos normales. "
    "La verde es el valor esperado del estimador, lo que daría el promedio de infinitas muestras, "
    "calculado exacto; la discontinua, la densidad verdadera. El deslizador cambia el ancho h, el "
    "mismo para las treinta. Antes de moverlo: ¿dónde se separa primero la verde de la discontinua "
    "cuando h crece, en el centro o en las colas?", alto=300)
_M8_SIM_ECM = sim(
    "apa-ecm", "El error en x = 0, separado en sus dos partes",
    "Las curvas son exactas, no simuladas: el sesgo al cuadrado (naranja), la varianza (azul) y su "
    "suma, el error cuadrático medio (verde), en x = 0 y en función de h; la discontinua gris es el "
    "error de toda la curva, el MISE. El deslizador marca un ancho y la lectura da las cifras en él. "
    "Antes de moverlo: ¿crees que el mejor h está donde se cortan la naranja y la azul?")
_HX8 = m8["h_ecm_x"]["h"]
_M8_LEE = como_se_lee(rf"""        <p>En la nube, el ancho de la franja gris es la varianza y la distancia de la curva verde
          a la discontinua es el sesgo. Con \(h\) pequeño las treinta curvas se pelean entre sí, pero
          su valor esperado está casi encima de la verdad; con \(h\) grande las treinta casi coinciden
          y todas se equivocan igual, aplastando el pico. El sesgo se ve primero en el pico porque es
          ahí donde la curvatura \(f''\) es mayor. Su signo es el de \(f''\): negativo en el pico, que
          baja, y positivo más allá de \(x = \pm 1\), en las colas, que se llenan.</p>
        <p style="margin-bottom:0;">La lectura da además el promedio de las treinta curvas en \(x\) = 0,
          y no coincide con el valor esperado: es un promedio de solo treinta muestras y tiene su propio
          error de Monte Carlo. Con \(h\) = {n(m8["nube_h"], 1)}, dos desviaciones típicas de ese promedio
          son {n(m8["nube_error_mc"], 4)}, casi la mitad del tamaño del sesgo en ese punto,
          {n(m8["nube_sesgo"], 4)}; con \(h\) más
          pequeño el sesgo se encoge y el ruido del promedio lo tapa. Por eso la curva verde es la
          exacta.</p>""")
_M8_LEE_ECM = como_se_lee(rf"""        <p>No. La naranja y la azul se cortan en \(h\) = {n(m8["cruce"], 2)}, y el mínimo del
          ECM está antes, en {n(m8["h_ecm"], 2)}, donde el sesgo al cuadrado, {n(m8["en_optimo"]["sesgo2"], 5)},
          es bastante menor que la varianza, {n(m8["en_optimo"]["var"], 5)}. En el mínimo no se igualan
          los dos errores, sino lo deprisa que cambian: ensanchar un poco más subiría el sesgo al
          cuadrado más de lo que bajaría la varianza.</p>
        <p style="margin-bottom:0;">La discontinua gris tiene su mínimo más a la derecha, en
          {n(m8["h_mise"], 4)}: el mejor ancho para \(x\) = 0 no es el mejor para la curva entera, que es
          lo que discute el texto de arriba.</p>""")
_M8_AMISE = derivacion("der-amise", r"Ver de dónde salen \(h_{\text{AMISE}}\) y la tasa \(n^{-4/5}\)", [
    r"""              <p>Se integran sobre la recta las dos fórmulas de arriba. El sesgo al cuadrado
                da \(\tfrac{h^4}{4}\mu_2(K)^2 R(f'')\), y la varianza, \(R(K)/(nh)\), porque \(f\)
                integra 1:</p>
              $$\text{AMISE}(h) = \frac{h^4}{4}\,\mu_2(K)^2\,R(f'') + \frac{R(K)}{n\,h}.$$""",
    r"""              <p>Se deriva respecto a \(h\) y se iguala a cero:
                \(h^3\mu_2(K)^2R(f'') = R(K)/(nh^2)\), es decir,</p>
              $$h_{\text{AMISE}} = \left(\frac{R(K)}{\mu_2(K)^2\,R(f'')\,n}\right)^{1/5}.$$""",
    r"""              <p>Se sustituye ese ancho en el AMISE. Después de simplificar:</p>
              $$\text{AMISE}^\ast = \frac{5}{4}\,\Big(R(K)\sqrt{\mu_2(K)}\Big)^{4/5}\,R(f'')^{1/5}\,n^{-4/5}.$$"""],
    r"""Ahí están las dos cosas que el módulo promete. La tasa, \(n^{-4/5}\). Y la combinación
    \(R(K)\sqrt{\mu_2(K)}\) con que el módulo 6 calculó la eficiencia: el núcleo solo entra en el
    error por ella, y la forma que la minimiza es el Epanechnikov.""")
_M8_CUADRO = tabla(["Estimador", "Qué se fija", "¿Integra 1?", "¿Curva suave?", "Sesgo", "Error integrado"],
    fila("Histograma (módulo 2)", "ancho \\(h\\) y origen", "sí", "no: escalones", "de orden \\(h\\)",
         "\\(n^{-2/3}\\)")
    + fila("ASH (módulo 3)", "ancho \\(h\\) y \\(m\\)", "sí", "casi", "baja con \\(m\\)",
           "\\(n^{-4/5}\\) con \\(m\\) grande")
    + fila("Núcleo (módulos 5 y 6)", "ancho \\(h\\) y forma \\(K\\)", "sí", "tanto como \\(K\\)",
           "de orden \\(h^2\\)", "\\(n^{-4/5}\\)")
    + fila("<em>k</em>-NN (módulo 7)", "número \\(k\\)", "no", "no: dientes",
           "el de una caja de semiancho \\(d_k\\)",
           "\\(n^{-4/5}\\) en cada punto, con \\(k \\propto n^{4/5}\\); el integrado lo lastran las colas"),
    "Los cuatro estimadores de la recta, lado a lado. Las tasas son las del error integrado con el "
    "mejor ancho.")
_M8_COD = tabs("El ECM exacto, en R y en Python", esc(R8.format(**SUB8)), esc(PY8.format(**SUB8)))
_M8_PLANO = en_el_plano(r"""        <p>El módulo 2 del capítulo 5 describe con palabras lo que este módulo mide: con σ
          pequeño «aparecen focos que son colegios concretos» —eso es varianza: la superficie
          depende de qué sedes tocaron— y con σ grande «queda una sola mancha» —eso es sesgo: la
          superficie se aplana aunque no hubiera azar—. En el plano la tasa del mejor ancho es
          \(n^{-1/6}\) y la del error, \(n^{-2/3}\), por la maldición de la dimensión del
          módulo 4: el núcleo en el plano converge tan despacio como el histograma en la recta.</p>
        <p style="margin-bottom:0;">Las fórmulas de este módulo dependen de \(f''\), que no se
          conoce. Hay tres salidas: suponerla, con una densidad de referencia (módulo 9); estimarla
          con los mismos datos y meterla en la fórmula, que es el <em>plug-in</em>; o estimar el
          error directamente, sin pasar por \(f''\), con validación cruzada. El módulo 10 trae las
          dos últimas.</p>""")

MOD8 = cabecera(
    8, TITULOS[7][0], INGLES[7],
    "Separar el error de un estimador de densidad en sesgo y varianza, ver cuál gobierna cada "
    "extremo de h y de dónde sale que el error decaiga como n elevado a −4/5.") + rf"""
      <p>Los módulos anteriores han dicho «sesgo» y «varianza» al describir figuras. El módulo 2 los
        derivó para el histograma y el 4 los calculó exactos para la ventana rígida; aquí se miden
        para el núcleo y se vuelven las fórmulas que usan los selectores de ancho. El
        <strong>error cuadrático medio</strong> en un punto,
        \(\text{{ECM}}(x) = E\big[(\hat f(x) - f(x))^2\big]\), se parte en dos piezas que el ancho de
        banda mueve en direcciones opuestas.</p>

{_M8_DER}
      <h3>Las dos piezas, en fórmula</h3>

      <p>Cuando \(h\) es pequeño y \(n\,h\) grande, las dos piezas tienen una forma aproximada que no
        depende del núcleo más que por sus dos constantes del módulo 6:</p>

      <div class="formula">
        $$\operatorname{{sesgo}}\hat f(x) \approx \frac{{h^2}}{{2}}\,\mu_2(K)\,f''(x),
          \qquad \operatorname{{Var}}\hat f(x) \approx \frac{{R(K)\,f(x)}}{{n\,h}}.$$
      </div>

      <p>El sesgo crece con \(h^2\) y es mayor donde la curva se dobla (\(f''\) grande: los picos y los
          valles). Su signo es el de \(f''\): negativo en los picos, que la estimación aplana, y
          positivo en los valles y en las colas, que rellena. La varianza decrece con \(n\,h\), que es
          proporcional al número de datos que caen dentro de la loma.</p>

      <p>Compárese con el módulo 2, donde el sesgo del histograma era del orden de \(f'(x)\,h\): la
          pendiente, no la curvatura. La loma está <strong>centrada</strong> en el punto que estima, y
          lo que la pendiente de \(f\) añade por un lado de \(x\) lo quita por el otro; solo queda la
          curvatura, y con ella el \(h^2\). Una barra de histograma casi nunca está centrada en el
          punto que estima. Toda la ventaja del núcleo —\(n^{{-4/5}}\) frente a \(n^{{-2/3}}\)— sale de
          ahí, y es la misma que el módulo 4 encontró en la ventana centrada.</p>

      <p>Son aproximaciones, y conviene comprobarlas. Con datos normales, \(n\) = {ent(m8["n"])},
        núcleo gaussiano, \(x\) = {n(_A8["x"], 1)} y \(h\) = {n(_A8["h"], 2)}, el sesgo exacto es
        {n(_A8["sesgo_exacto"], 8)} y la fórmula da {n(_A8["sesgo_formula"], 8)}; la varianza exacta
        es {n(_A8["var_exacta"], 5)} y la fórmula da {n(_A8["var_formula"], 5)}. La del sesgo es casi
        perfecta. La de la varianza se pasa porque se queda con el término principal y descarta
        otro, \(-\big(E\hat f(x)\big)^2/n\), que es del orden de \(h\) veces el principal: con
        \(h\) = {n(_A8["h"], 2)} todavía se nota, y la diferencia desaparece cuando \(h\) se
        achica.</p>

      <h3>El mejor ancho para un punto y para toda la curva</h3>

      <p>Como \(f\) es normal, el error tiene forma cerrada y no hace falta simular. En \(x = 0\), el
        ancho que minimiza el ECM es {firma(f"{m8['h_ecm']:g}")}. Pero un ancho no se elige para un
        punto: se elige para la curva entera. Para una muestra concreta, el error de toda la curva es
        \(\int(\hat f - f)^2\), el <strong>error cuadrático integrado</strong>, ECI (en inglés,
        <em>ISE</em>): cambia de una muestra a otra. Su promedio sobre todas las muestras es el
        <strong>error cuadrático integrado promedio</strong>, \(\text{{ECIP}} = E\int(\hat f - f)^2\)
        (en inglés, <em>MISE</em>), y es él el que se parte en sesgo al cuadrado y varianza
        integrados. Para el error integrado, desde aquí el apéndice usa las siglas inglesas, ISE y
        MISE, que son las de R y de la literatura. El mínimo exacto del MISE está en {firma(n(m8["h_mise"], 4))}; su aproximación para
        \(h\) pequeño, el AMISE, que sale de integrar las dos fórmulas de arriba, tiene el mínimo en la
        fórmula de abajo, donde \(R(f'') = \int f''(x)^2\,dx\) mide cuánto se dobla la densidad
        verdadera:</p>

      <div class="formula">
        $$h_{{\text{{AMISE}}}} = \left(\frac{{R(K)}}{{\mu_2(K)^2\,R(f'')\,n}}\right)^{{1/5}}
          = \left(\frac{{4}}{{3n}}\right)^{{1/5}} = {n(m8["h_amise"], 4)},$$
      </div>

      <p>donde la segunda igualdad es la de un núcleo gaussiano con
          datos normales de desviación 1. El error del ancho asintótico es
          {n(m8["mise_en_amise"], 6)}, contra {n(m8["mise_min"], 6)} del óptimo exacto.</p>

{_M8_AMISE}
      <p>Los tres anchos no coinciden, y cada diferencia enseña algo. La del punto con la curva: el mejor
        ancho en \(x\) = {n(m8["h_ecm_x"]["x"][0], 1)} es {n(_HX8[0], 2)}, en
        \(x\) = {n(m8["h_ecm_x"]["x"][1], 1)} es {n(_HX8[1], 2)} y en \(x\) = {n(m8["h_ecm_x"]["x"][2], 1)},
        donde la curva cambia de curvatura y \(f''\) se anula, sube a {n(_HX8[2], 2)}. El mejor ancho
        para un punto depende de cuánto se dobla la densidad allí, y un ancho para toda la curva es un
        compromiso entre todos ellos. La del ancho exacto con el asintótico enseña lo contrario: el
        error con {n(m8["h_amise"], 4)} es solo un {pct(m8["mise_pct_amise"], 1)} mayor que con
        {n(m8["h_mise"], 4)}, porque el MISE es muy plano cerca de su mínimo, y equivocarse un poco
        de ancho cuesta poco. Las dos diferencias juntas dicen cuándo compensa dejar que el ancho
        cambie de un punto a otro, como los estimadores adaptativos del módulo 7. Lo que se gana es
        poco, porque un solo ancho bien elegido ya está cerca del mejor error posible; y lo que se
        paga es otra estimación —la piloto que decide el ancho de cada zona—, con su propia varianza,
        que el ancho fijo no tiene. Solo sale a cuenta cuando la escala de los datos cambia mucho de
        una zona a otra, como en una ciudad con un centro denso y una periferia rala.</p>

      <p>De la fórmula sale también la tasa: el mejor error integrado decae como \(n^{{-4/5}}\), más
        deprisa que el \(n^{{-2/3}}\) del histograma. Para bajarlo a la mitad, el núcleo necesita
        {n(m8["tasas"]["kde_datos_para_mitad"], 2)} veces más datos y el histograma
        {n(m8["tasas"]["hist_datos_para_mitad"], 2)}.</p>

      <p>Y una cuenta que une este módulo con el 4. La mejor ventana rígida en el mismo \(x\) = 0, con
        los mismos {ent(m4["n_contraste"])} datos normales, medía {n(_PN[100]["v_opt"], 2)}; una caja
        de ese ancho tiene desviación típica \(V/\sqrt{{12}}\) = {n(m4["v_opt_sd_n100"], 2)}, casi los
        {n(_HX8[0], 2)} del gaussiano. Medidos por su desviación típica, la caja y la campana piden el
        mismo ancho: es la regla del módulo 6, con cifras.</p>

{_M8_SIM_NUBE}
{_M8_LEE}
{_M8_SIM_ECM}
{_M8_LEE_ECM}
{_M8_CUADRO}
{_M8_COD}
      <p>Las dos fórmulas del bloque son exactas porque la convolución de dos normales es otra
        normal: \(E\hat f(0)\) es la densidad en 0 de una normal de varianza \(1 + h^2\), y el segundo
        momento sale de otra de varianza \(1 + h^2/2\). La función <code>mise()</code> es la integral
        de esas expresiones sobre toda la recta, también cerrada, y <code>optimize()</code> busca su
        mínimo con una tolerancia fina para que la cuarta cifra no dependa de dónde se detiene.</p>

{_M8_PLANO}""" + CIERRE

_F9, _PL9, _DN9 = m9["faithful"], m9["plano"], m9["distancias"]
_M9_TRAMPA = trampa(r"\(3.5\,s\,n^{-1/3}\) no es para el núcleo", rf"""Esa fórmula aparece en
        muchos textos como «la regla de Scott», y lo es, pero para el <strong>ancho de las barras de un
        histograma</strong> (módulo 2). Aplicada al núcleo da {n(_F9["hist_rule"], 4)} en las
        erupciones, {n((_F9["hist_sobre_nrd"]), 2)} veces lo que da <code>bw.nrd</code>: la constante
        es {n(_F9["factor_constante"], 2)} veces mayor y el exponente \(n^{{-1/3}}\) frente a
        \(n^{{-1/5}}\) la reduce en un factor {n(_F9["factor_exponente"], 3)}. La constante mayor es,
        casi toda, un cambio de unidad: el \(h\) del histograma es el ancho <em>entero</em> de la barra,
        y una barra de ancho \(h\) tiene desviación típica \(h/\sqrt{{12}}\), así que la constante exacta
        del módulo 2, medida en desviaciones típicas, es {n(_F9["hist_constante_sd"], 3)}: casi el 1.06
        del núcleo. Lo que de verdad separa las dos reglas es el exponente, y su error no tiene una
        dirección fija. El cociente \(n^{{-1/3}}/n^{{-1/5}} = n^{{-2/15}}\) tiende a cero, así que con
        estas erupciones la regla del histograma sobresuaviza, pero desde unos
        {ent(_F9["n_cruce_redondo"])} datos daría menos que <code>bw.nrd</code>: aplicada al núcleo
        ni siquiera alcanza la tasa óptima.""")
_M9_SIM = sim(
    "apa-selectores", "Cada selector, su ancho y su curva sobre las erupciones",
    "Cada botón aplica el ancho que eligió un selector sobre los mismos datos y dibuja el estimador "
    "gaussiano con él. Los dos primeros son las reglas de este módulo; los tres siguientes, bw.ucv, "
    "bw.bcv y bw.SJ, son selectores que el módulo 10 explica —aquí basta saber que eligen h mirando "
    "los datos en vez de suponer una normal—; el último es la regla del histograma, aplicada por "
    "error. Antes de pulsar: ¿cuál crees que verá más modas?", alto=300)
_MO10 = m10["modas"]
_M9_LEE = como_se_lee(rf"""        <p>La que más modas ve es <code>bw.ucv</code>, con {ent(_MO10["ucv"])}; todas las demás ven
          {ent(_MO10["SJ"])}, las dos clases de erupción. Lo que cambia entre ellas es lo hondo del valle y
          lo alto de los picos: las dos reglas de referencia dan curvas más lisas que los selectores del
          módulo 10, y la regla del histograma, aplicada por error, aplana todavía más, aunque sigue
          viendo las dos modas.</p>
        <p style="margin-bottom:0;">Si la tercera moda de <code>bw.ucv</code> es real o un artefacto
          del ancho es la pregunta del módulo 10.</p>""")
_M9_COD = tabs("Reglas de referencia, en R y en Python", esc(R9.format(**SUB9)), esc(PY9.format(**SUB9)))
_M9_PLANO = en_el_plano(rf"""        <p>La regla general en \(d\) dimensiones es
          \(h = \left(\tfrac{{4}}{{d+2}}\right)^{{1/(d+4)}} \sigma_f\, n^{{-1/(d+4)}}\), con \(\sigma_f\)
          la desviación típica de los datos en cada coordenada. En la recta el
          factor vale {n(m9["factor_d"]["factor"][0], 4)} —el 1.06 de <code>bw.nrd</code>— y la tasa es
          \(n^{{-1/5}}\); en el plano el factor vale exactamente 1 y la tasa es \(n^{{-1/6}}\). Eso es
          <code>bw.scott</code> de spatstat, que el módulo 3 del capítulo 5 usa: sobre las
          {ent(_PL9["n"])} sedes, la desviación típica de la coordenada este,
          {n(_PL9["sd_x"], 2)} m, por \(n^{{-1/6}}\) = {n(_PL9["n_sexta"], 4)}, da
          {firma(n(_PL9["scott_x"], 2), " m")}, y la de la norte da {n(_PL9["scott_y"], 2)} m. Devuelve
          dos números, uno por coordenada, y en Bogotá difieren tanto porque la ciudad es más larga
          que ancha.</p>
        <p>Ojo con la letra. Aquí \(\sigma_f\) es cuánto se dispersan las sedes; el σ del capítulo 5 es
          lo ancho del núcleo. La regla de referencia es justo la fórmula que convierte la una en el
          otro: en el plano, \(\sigma = \sigma_f\,n^{{-1/6}}\).</p>
        <p style="margin-bottom:0;">Y el capítulo 5, en su módulo 7, suaviza la curva de
          <code>rhohat</code> en Python con \(1.06\,s\,n^{{-1/5}}\): es esta regla, la de la recta, sin el
          mínimo con el rango intercuartílico; la variante que scipy llama «silverman», como se vio
          arriba.</p>""")

MOD9 = cabecera(
    9, TITULOS[8][0], INGLES[8],
    "Aplicar las reglas de referencia normal, saber qué constante usa cada función de R y de "
    "Python, y ver por qué fallan cuando los datos no se parecen a una normal.") + rf"""
      <p>El ancho óptimo del módulo 8 depende de \(R(f'')\), la curvatura de una densidad que no se
        conoce. La salida más simple es <strong>suponer</strong> una: si \(f\) fuera normal con
        desviación típica \(\sigma_f\) —la de los datos—, \(R(f'') = 3/(8\sqrt\pi\,\sigma_f^5)\), y con
        núcleo gaussiano el óptimo queda</p>

      <div class="formula">
        $$h = \left(\tfrac{{4}}{{3}}\right)^{{1/5}} \sigma_f\, n^{{-1/5}} \approx
          {n(m8["constante_amise"], 3)}\,\sigma_f\,n^{{-1/5}}.$$
      </div>

      <p>Es una <strong>regla de referencia normal</strong>. En la práctica \(\sigma_f\) se estima con
          la muestra, y para que una cola larga o un dato extremo no la inflen se usa
          \(\min(s,\ \mathrm{{IQR}}/{CON["iqr"]})\), con \(s\) la desviación típica muestral: en una
          normal el rango intercuartílico vale {n(CON["iqr_normal"], 4)} desviaciones, así que
          \(\mathrm{{IQR}}/{CON["iqr"]}\) también estima \(\sigma_f\), pero no se deja arrastrar por los
          extremos.</p>

      <p>R trae dos versiones. <code>bw.nrd</code> usa la constante {CON["scott"]} y R se la atribuye
        a Scott; <code>bw.nrd0</code>, la que usa <code>density()</code> si no se le pide otra cosa,
        usa {CON["silverman"]} y se la atribuye a Silverman (1986), que la achicó a propósito para que
        no borrara las modas de una distribución que no fuera normal.</p>

      <p>Sobre las erupciones, \(s\) = {n(_F9["sd"], 4)} y \(\mathrm{{IQR}}/{CON["iqr"]}\) =
        {n(_F9["iqr_134"], 4)}, así que manda la desviación típica, y \(n^{{-1/5}}\) =
        {n(_F9["n_quinta"], 4)}. <code>bw.nrd0</code> da {firma(n(_F9["nrd0"], 4))} y
        <code>bw.nrd</code>, {firma(n(_F9["nrd"], 4))}. Los selectores del módulo 10, que miran los
        datos en vez de suponer una normal, eligen entre {n(m10["selectores"]["ucv"], 4)} y
        {n(m10["selectores"]["dpik"], 4)}: las reglas de referencia dan anchos entre dos y cuatro
        veces mayores —sobresuavizan—, porque el géiser tiene dos modas y la referencia solo una.</p>

{_M9_TRAMPA}
{_M9_SIM}
{_M9_LEE}
      <h3>El «silverman» de scipy no es el de R</h3>

      <p><code>gaussian_kde</code> de scipy acepta <code>bw_method="silverman"</code>, y el nombre
        engaña: usa \((4/3)^{{1/5}}\,s\,n^{{-1/5}} \approx {n(m8["constante_amise"], 3)}\,s\,n^{{-1/5}}\),
        la constante exacta de arriba, sin el mínimo con el rango intercuartílico. Su método por
        defecto, <code>"scott"</code>, ni siquiera lleva esa constante: en una dimensión es
        \(s\,n^{{-1/5}}\). Cuando manda la desviación típica, como en las erupciones, el «silverman» de
        scipy casi coincide con <code>bw.nrd</code>. Cuando hay una
        cola larga se separa. Las distancias de cada sede de Bogotá a la más cercana (módulo 12)
        tienen \(s\) = {n(_DN9["sd"], 2)} m pero \(\mathrm{{IQR}}/{CON["iqr"]}\) =
        {n(_DN9["iqr_134"], 2)} m, porque unas pocas sedes están muy aisladas —la más lejana, a
        {n(_DN9["maximo"], 0)} m de su vecina—; scipy da {firma(n(_DN9["scipy"], 2), " m")};
        <code>bw.nrd</code>, que sí toma el mínimo, {firma(n(_DN9["nrd"], 2), " m")}, y <code>bw.nrd0</code>,
        con además la constante 0.9, {firma(n(_DN9["nrd0"], 2), " m")}.</p>

{_M9_COD}
      <p>La pestaña de R llama a <code>bw.nrd0</code> y <code>bw.nrd</code>; la de Python las escribe
        con su fórmula —0.9 y 1.06 por el mínimo de las dos escalas, por \(n^{{-1/5}}\)— y da las mismas
        cifras, para que se vea que no hay nada más dentro. La segunda mitad de la pestaña de R
        comprueba que <code>bw.scott</code> de spatstat es la desviación típica de cada coordenada por
        \(n^{{-1/6}}\). La de Python cruza el cálculo de las distancias al vecino con
        <code>cKDTree</code>, que devuelve primero a la propia sede (distancia cero) y por eso se le
        piden dos vecinos y se toma el segundo; con <code>kde.factor</code> por la desviación típica se
        recupera el ancho que scipy usa de verdad.</p>

{_M9_PLANO}""" + CIERRE

_SEL10 = m10["selectores"]
_AIS = m10["aislada"]
_EMP10 = m10["empates"]
_LOO10 = m10["loo_mano"]


def _fila_aimse(nombre, a):
    return fila(nombre, n(a["h"], 4), n(a["rugosidad"], 2), n(a["ruido"], 2))


_M10_TAB = tabla(["Selector", r"\(h\)", r"\(R(\hat f'')\) de su curva", r"de ella, ruido \(R(K'')/(nh^5)\)"],
                 _fila_aimse("<code>bw.ucv</code>", AIM["ucv"]) + _fila_aimse("<code>bw.SJ</code>", AIM["SJ"])
                 + _fila_aimse("<code>bw.bcv</code>", AIM["bcv"]) + _fila_aimse("<code>bw.nrd0</code>", AIM["nrd0"]),
                 "La curvatura de cada curva estimada y la parte de ella que pone el propio ancho.")
_M10_DER = derivacion("der-cv", r"Ver por qué \(\int f^2\) no hace falta", [
    r"""              <p>El error integrado se desarrolla en tres términos:</p>
              $$\int (\hat f - f)^2 = \int \hat f^2 - 2\int \hat f\, f + \int f^2.$$""",
    r"""              <p>El último no depende de \(h\), así que no cambia dónde está el mínimo y se puede
                quitar. El primero solo depende de los datos. El del medio es \(E[\hat f(X)]\) para un
                \(X\) nuevo de \(f\): no se tiene un dato nuevo, pero se puede <em>fabricar</em> uno
                sacando \(x_i\) de la muestra y estimando con los demás,</p>
              $$\hat f_{-i}(x_i) = \frac{1}{(n-1)\,h}\sum_{j \ne i} K\!\left(\frac{x_i - x_j}{h}\right),$$""",
    r"""              <p>y promediando sobre todos los \(i\). Ese promedio estima \(\int \hat f\,f\) sin
                sesgo: de ahí la «validación cruzada».</p>"""],
    r"""\(\text{UCV}(h) = \int \hat f_h^2 - \frac{2}{n}\sum_i \hat f_{h,-i}(x_i)\) estima
    \(\text{MISE}(h) - \int f^2\) sin conocer \(f\), y se minimiza en \(h\).""")
_M10_SIM = sim(
    "apa-cv", "Los dos criterios de validación cruzada sobre las erupciones",
    "La curva azul es el criterio UCV, que se minimiza (eje de la izquierda); la naranja es la "
    "log-verosimilitud LCV, que se maximiza (eje de la derecha); un punto de su color marca el "
    "óptimo de cada una. El deslizador marca un ancho y la lectura da los dos criterios, cuántas "
    "modas tiene la estimación con ese ancho y dónde está cada óptimo. El botón quita de la muestra "
    f"la erupción de {n(_AIS[0]['x'], 3)} minutos, la más aislada, y redibuja los dos criterios sin "
    "ella. Antes de pulsarlo: ¿cuál de los dos crees que cambiará más?", alto=300)
_UCV_SIN = (f"el mínimo de la UCV no se mueve: sigue en {m10['h_ucv_mano']:g}"
            if m10["h_ucv_sin"] == m10["h_ucv_mano"] else
            f"el mínimo de la UCV apenas pasa de {m10['h_ucv_mano']:g} a {m10['h_ucv_sin']:g}")
_M10_LEE = como_se_lee(rf"""        <p>La LCV. Sin esa sola erupción su máximo se va de {f"{m10['h_lcv_mano']:g}"} a
          {f"{m10['h_lcv_sin']:g}"}; {_UCV_SIN}. La razón está en el logaritmo. La erupción de
          {n(_AIS[0]["x"], 3)} minutos, en el fondo del valle entre las dos modas, tiene con
          \(h\) = {n(_AIS[0]["h"], 2)} una densidad dejándola fuera de {n(_AIS[0]["min_loo"], 6)}; su
          logaritmo, {n(_AIS[0]["min_log"], 2)}, aporta {n(_AIS[0]["aporte"], 4)} al promedio, y con
          \(h\) = {n(_AIS[1]["h"], 2)} aporta {n(_AIS[1]["aporte"], 4)}. Entre esos dos anchos la LCV
          entera sube {n(m10["lcv_sube"], 4)}, y {n(m10["aislada_cambio"], 4)} de esa subida la pone esa
          erupción. Un promedio de logaritmos de cifras diminutas es rehén de sus cifras más
          diminutas.</p>
        <p style="margin-bottom:0;">Con un núcleo de soporte acotado sería peor: un dato sin vecinos a
          menos de \(h\) tendría densidad cero y logaritmo \(-\infty\), la ventana vacía del módulo 4. La
          UCV no tiene ese talón, pero tiene otro: es la resta de dos sumandos grandes que casi se
          cancelan, \(\int\hat f^2\) y el doble del promedio dejando uno fuera, y una diferencia pequeña
          entre cantidades grandes salta con poco. El módulo 11 mide cuánto.</p>""")
_M10_TRAMPA = trampa("<code>bw.bcv</code> no es la validación por verosimilitud", r"""Las dos
        siglas se cruzan: la B de BCV es de <em>biased</em>, sesgada, no de verosimilitud. En R,
        <code>bw.ucv</code> es la validación cruzada <em>insesgada</em> (<em>unbiased</em>: la UCV de
        este módulo) y <code>bw.bcv</code> la <em>sesgada</em> (Scott y Terrell, 1987): no deja uno
        fuera, sino que mete en el AMISE la rugosidad de la curva estimada menos su término de ruido,
        el de la tabla de arriba, y por eso es mucho más estable. La de verosimilitud (LCV) no está en
        <code>stats</code>: hay que programarla, como hace el bloque.""")
_M10_COD = tabs("Validación cruzada a mano, en R y en Python", esc(R10.format(**SUB10)),
                esc(PY10.format(**SUB10)))
_M10_PLANO = en_el_plano(r"""        <p>De los cuatro selectores que el módulo 3 del capítulo 5 aplica a las sedes, tres
          tienen pariente en la recta. <code>bw.ppl</code> maximiza la verosimilitud de un proceso
          puntual dejando una sede fuera cada vez (Loader): es la LCV. <code>bw.diggle</code>
          minimiza el error cuadrático medio de la intensidad, estimado por validación cruzada a
          través de la función \(K\) de Ripley del capítulo 4 —la de parejas de sedes, no el núcleo—
          (Diggle, 1985; Berman y Diggle, 1989): es la pariente de la UCV. <code>bw.scott</code> es la
          regla del módulo 9. El cuarto, <code>bw.CvL</code> (Cronie y van Lieshout, 2018), no tiene
          pariente en este apéndice: pide que la suma de los inversos de la intensidad estimada en las
          sedes iguale el área.</p>
        <p style="margin-bottom:0;">Allí <code>bw.ppl</code>, sobre <code>japanesepines</code>,
          devuelve el extremo superior de su intervalo de búsqueda; en el módulo 12 de este apéndice
          <code>bw.ucv</code> se queda junto al inferior, y solo un aviso lo delata. En los dos casos el
          número que vuelve no es una selección sino un efecto de dónde se buscó. Y si cada selector da
          otro ancho, falta saber cuál acierta: el módulo 11 lo mide contra una verdad conocida.</p>""")

MOD10 = cabecera(
    10, TITULOS[9][0], INGLES[9],
    "Construir los criterios UCV y LCV a mano, reconocer sus fallos —mínimos que no lo son, "
    "alta varianza, dependencia de unas pocas observaciones—, conocer el plug-in de Sheather y "
    "Jones y conectar cada criterio con su selector de spatstat.") + rf"""
      <p>Las reglas de referencia suponen una forma para \(f\). La <strong>validación
        cruzada</strong> no supone nada: busca el \(h\) que minimiza una estimación del error
        integrado hecha solo con los datos.</p>

{_M10_DER}
      <p>Para verlo a mano con los cinco datos del módulo 5 y \(h\) = 1: dejando fuera el
        {ent(_LOO10["x"])}, los otros cuatro le dan los pesos
        {", ".join(n(v, 4) for v in _LOO10["terminos"])}, y su promedio es
        \(\hat f_{{-i}}({ent(_LOO10["x"])})\) = {firma(n(_LOO10["f"], 4))}, menos que el
        {n(m5["gaussiano"]["f"], 4)} de la estimación que sí lo veía: el dato ya no se vota a sí
        mismo. Fabricar así un dato «nuevo» supone que \(x_i\) es <strong>independiente</strong> de los
        que quedan; si tuviera un gemelo dentro de la muestra, el dato nuevo ya estaría visto. El
        módulo 12 encuentra ese gemelo.</p>

      <p>La variante de <strong>verosimilitud</strong> (LCV) cambia el error por la probabilidad de
        los datos: maximiza \(\frac{{1}}{{n}}\sum_i \log \hat f_{{h,-i}}(x_i)\), la log-verosimilitud de
        cada dato bajo la estimación que no lo vio.</p>

      <h3>Sobre las erupciones</h3>

      <p>Calculado sobre una rejilla de anchos que empieza en {n(_EMP10["rejilla_desde"], 2)}, el
        mínimo de la UCV está en {firma(f"{m10['h_ucv_mano']:g}")}, y <code>bw.ucv</code> devuelve
        {n(_SEL10["ucv"], 4)}: el mismo criterio, con las distancias agrupadas para ir más rápido. Con ese
        ancho la estimación tiene <strong>{ent(m10["modas"]["ucv"])} modas</strong>, en
        {", ".join(n(v, 2) for v in m10["donde_modas_ucv"])} minutos; con los otros selectores
        —<code>bw.SJ</code> ({n(_SEL10["SJ"], 4)}), <code>bw.bcv</code> ({n(_SEL10["bcv"], 4)}) y
        <code>KernSmooth::dpik</code> ({n(_SEL10["dpik"], 4)}), que se presentan abajo— tiene
        {ent(m10["modas"]["SJ"])}. La moda del medio parece espuria: solo aparece con anchos de
        {n(m10["h_max_tres"], 2)} o menos, y ningún otro selector la ve.</p>

      <p>Pero ese mínimo de la UCV es <strong>local</strong>. Las erupciones vienen redondeadas —hay
        {ent(m10["distintos"])} valores distintos entre {ent(m10["n"])}—, y forman
        {ent(_EMP10["parejas"])} parejas de valores idénticos, {n(_EMP10["por_dato"], 2)} por dato. El
        módulo 12 demuestra que, por encima de {n(_EMP10["umbral"], 4)} parejas por dato, la UCV baja sin
        tope cuando \(h\) se acerca a cero: con \(h\) = 0.001 vale {n(_EMP10["ucv_001"], 2)}, muy por
        debajo de los {n(_EMP10["ucv_min_local"], 4)} del mínimo. Aquí el mínimo local es estable
        —rompiendo los empates con medio segundo de ruido, <code>bw.ucv</code> da entre
        {n(_EMP10["jitter_min"], 3)} y {n(_EMP10["jitter_max"], 3)} en {ent(_EMP10["jitter_n"])}
        intentos—, pero se encuentra porque la búsqueda empieza lejos de cero: la rejilla de esta página
        en {n(_EMP10["rejilla_desde"], 2)} y <code>bw.ucv</code> en {n(_EMP10["busqueda_desde"], 3)}. Con
        las sedes de Bogotá no habrá esa suerte.</p>

      <h3>La tercera salida: el <em>plug-in</em></h3>

      <p>Entre suponer \(f''\) (módulo 9) y no usarla (la validación cruzada) hay un camino intermedio:
        estimar \(R(f'')\) con los mismos datos y meterla en la fórmula de \(h_{{\text{{AMISE}}}}\) del
        módulo 8. Es el <em>plug-in</em>. Tiene una dificultad: medir la curvatura también exige
        suavizar, y con un ancho pequeño la curva estimada es más rugosa que la verdad. La tabla lo
        muestra con la curvatura \(R(\hat f'')\) de cada curva: la de la UCV es
        {n(m10["rug_ucv_sobre_sj"], 2)} veces la de SJ, pero buena parte de esa rugosidad no es del
        géiser. La pone el propio ancho, porque \(R(\hat f''_h)\) lleva dentro un término de ruido,
        \(R(K'')/(nh^5)\), que crece muy deprisa al achicar \(h\).</p>

{_M10_TAB}
      <p><code>bw.SJ</code> (Sheather y Jones, 1991) resuelve el problema con un ancho
        <em>piloto</em>, distinto del final y elegido para estimar bien la curvatura: busca el \(h\)
        que cumple \(h = \big[R(K)/(\mu_2(K)^2\,\hat R(f'')\,n)\big]^{{1/5}}\), donde \(\hat R(f'')\) se
        estima con ese piloto, que a su vez depende de \(h\). <code>KernSmooth::dpik</code> hace lo
        mismo en dos pasos directos, sin resolver la ecuación. Los dos estiman una sola cifra,
        \(R(f'')\), con un piloto más ancho que el \(h\) final, y no restan dos sumandos grandes que
        casi se cancelan, como la UCV: por eso varían mucho menos de una muestra a otra.</p>

{_M10_SIM}
{_M10_LEE}
{_M10_TRAMPA}
{_M10_COD}
      <p>La matriz <code>dif</code> guarda todas las diferencias \(x_i - x_j\), y con ella los dos
        criterios son dos líneas: <code>loo()</code> anula la diagonal para que cada dato no se vea a
        sí mismo, y la integral \(\int \hat f^2\) del núcleo gaussiano tiene forma cerrada —la
        convolución de dos gaussianas de ancho \(h\) es una gaussiana de ancho \(h\sqrt2\)—. La
        última línea de R compara con los selectores de R, que agrupan las distancias en mil casillas
        antes de calcular; <code>bw.ucv</code> da {n(_SEL10["ucv"], 4)} y la rejilla
        {f"{m10['h_ucv_mano']:g}"}, una diferencia que cabe en un paso de la rejilla.</p>

{_M10_PLANO}""" + CIERRE

_EM = m11["em"]


def _fila_real(etq, r):
    return fila(etq, n(r["h"], 4), n(r["mise"], 5), f"+{n(r['sobre_pct'], 1)} %")


def _fila_mc(etq, r):
    return fila(etq, n(r["h_media"], 4), n(r["h_sd"], 4), n(r["mise"], 5), n(r["sd_ise"], 5),
                pct(r["gana_pct"], 1), pct(r["cola_pct"], 1))


_M11_TAB1 = tabla(["Selector", r"\(h\) sobre los datos", "MISE exacto", "Sobre el óptimo"],
                  _fila_real("<code>bw.SJ</code>", REALES["SJ"]) + _fila_real("<code>bw.bcv</code>", REALES["bcv"])
                  + _fila_real("<code>bw.ucv</code>", REALES["ucv"])
                  + _fila_real("<code>KernSmooth::dpik</code>", REALES["dpik"])
                  + _fila_real("<code>bw.nrd0</code>", REALES["nrd0"]) + _fila_real("<code>bw.nrd</code>", REALES["nrd"])
                  + _fila_real("Regla del histograma", REALES["hist_rule"]),
                  "El error integrado exacto de cada ancho elegido sobre los datos reales, si la "
                  "verdad fuera la mezcla ajustada.")
_M11_TAB2 = tabla(["Selector", r"\(h\) medio", r"Desv. de \(h\)", "ISE medio", "Desv. del ISE", "Gana",
                   "ISE > 2 × SJ"],
                  "".join(_fila_mc(f"<code>{s}</code>", MC[s]) for s in ("SJ", "bcv", "ucv", "nrd0", "nrd")),
                  f"{ent(m11['B'])} muestras de {ent(m11['n'])} datos de la mezcla: el ancho medio y "
                  "su dispersión, el error medio —que estima el MISE— y su dispersión, en qué fracción "
                  "de muestras cada selector dio el menor error y en cuál perdió por mucho contra SJ.")
_CU11 = m11["cola_ucv"]
_DG11 = m11["dif_gana"]
_M11_SIM = sim(
    "apa-mc", "Mil muestras: cada punto compara dos selectores en la misma muestra",
    "Cada punto es una de las mil muestras. El eje horizontal es el error integrado (ISE) de bw.SJ y "
    "el vertical, el del selector del botón. Debajo de la diagonal gana ese selector; por encima de "
    "la línea discontinua pierde por más del doble. Antes de pulsar: ¿esperas que la nube de la UCV "
    "esté más o menos dispersa que la de la BCV?", alto=320)
_M11_LEE = como_se_lee(rf"""        <p>Más dispersa. La UCV es un selector de <strong>alta varianza</strong>: es la que más
          veces gana, en el {pct(MC["ucv"]["gana_pct"], 1)} de las muestras, pero en el
          {pct(MC["ucv"]["cola_pct"], 1)} su error supera el doble del de SJ, algo que a la BCV no le pasó
          ni una vez. Su error medio queda {pct(m11["emparejadas"]["ucv_sj"]["pct"], 1)} por encima del
          de SJ. Ganar algo más a menudo y a veces perder por mucho puede ser peor que ganar algo menos
          y no perder nunca por mucho, si lo que se necesita es un ancho en el que confiar.</p>
        <p style="margin-bottom:0;">La tabla dice de dónde viene esa dispersión. La UCV no se equivoca
          de centro: la mediana de sus anchos, {n(MC["ucv"]["h_mediana"], 4)}, está junto al óptimo,
          {n(m11["h_estrella"], 4)}. Se equivoca de dispersión —la desviación de sus anchos es
          {n(MC["ucv"]["h_sd"], 4)}, contra {n(MC["SJ"]["h_sd"], 4)} de SJ— y hacia un solo lado: las
          {ent(_CU11["n"])} muestras en que pierde por más del doble eligieron todas un ancho menor que el
          de SJ, y menor que {n(_CU11["corte"], 2)}. Eso es lo que la frase «la UCV tiende a
          infrasuavizar» quiere decir: no que se quede corta en promedio, sino que cuando falla, falla
          hacia ahí. SJ y la BCV hacen lo contrario: se pasan de ancho casi siempre —en el
          {pct(MC["SJ"]["pct_sobre_hstar"], 1)} y el {pct(MC["bcv"]["pct_sobre_hstar"], 1)} de las
          muestras—, pero por poco.</p>""")
_M11_COD = tabs("La verdad conocida y el Monte Carlo, en R y en Python", esc(R11.format(**SUB11)),
                esc(PY11.format(**SUB11)))
_M11_PLANO = en_el_plano(r"""        <p>El módulo 3 del capítulo 5 sostiene que «el ancho óptimo» no es una propiedad del
          patrón: cada selector optimiza otra cosa y dan anchos distintos sobre las mismas sedes. Este
          módulo enseña algo más modesto y que vale también allí. Aquí los tres selectores de datos
          apuntan al mismo blanco, el MISE, y aun así discrepan de una muestra a otra; en el plano,
          además, cada uno apunta a un blanco distinto. Cuál acierta más depende de la muestra, y elegir
          un selector es elegir un perfil de riesgo, no una respuesta.</p>
        <p>Con datos espaciales reales tampoco hay verdad conocida, pero la receta de este módulo se
          traslada: simular de un modelo conocido y ver quién lo recupera, como hacen las envolventes
          del capítulo 4, módulo 11. Y la costumbre que deja es la del capítulo 5: <strong>declarar el
          selector</strong> y mirar la superficie, no solo el número.</p>
        <p style="margin-bottom:0;">Falta lo que la teoría de la recta da por hecho y un dato
          espacial no cumple. Es el módulo 12.</p>""")

MOD11 = cabecera(
    11, TITULOS[10][0], INGLES[10],
    "Comparar selectores contra una densidad conocida, distinguir el error medio del riesgo de "
    "perder por mucho y leer un experimento de Monte Carlo con su propio error.") + rf"""
      <p>Sobre datos reales no se puede decir qué selector acierta, porque la densidad verdadera no
        se conoce. El recurso es fabricar una verdad parecida a los datos. Se ajusta a las erupciones
        una mezcla de dos normales, como la de la cafetería del módulo 1, por el algoritmo EM
        (<em>expectation-maximization</em>). El EM alterna dos pasos: da a cada erupción una
        probabilidad de pertenecer a cada grupo, y recalcula el peso, las medias y las desviaciones
        con esas probabilidades; repite hasta que la verosimilitud deja de subir. Aquí bastan
        {ent(_EM["iter"])} vueltas, y salen un peso de {n(_EM["p"], 4)} para el primer grupo, medias
        {n(_EM["mu"][0], 4)} y {n(_EM["mu"][1], 4)} y desviaciones {n(_EM["s"][0], 4)} y
        {n(_EM["s"][1], 4)}. Desde ahí la mezcla se trata como si fuera la densidad de la que salieron
        las erupciones. Con núcleo gaussiano, el error integrado exacto contra una
        mezcla de normales tiene forma cerrada: su mínimo está en \(h^\ast\) =
        {firma(n(m11["h_estrella"], 4))}, con un MISE de {n(m11["mise_min"], 5)}.</p>

{_M11_TAB1}
      <p>La columna se lee así: cada selector eligió su ancho sobre las erupciones reales, y el MISE es
        el error medio que daría ese ancho sobre muestras de la mezcla —no el error de la estimación
        hecha con la muestra real, que no se puede medir—. El MISE del ancho de SJ queda a menos de un
        uno por ciento del óptimo y las reglas de referencia normal multiplican el error por más de
        cuatro.
        Pero esa tabla mira <em>una</em> muestra. Para ver cómo se comporta cada selector hay que darle
        muchas: se sacan
        {ent(m11["B"])} muestras de {ent(m11["n"])} datos de la mezcla y en cada una se mide el error
        integrado (ISE) de los cinco selectores.</p>

{_M11_TAB2}
      <p>La tabla cuenta en qué fracción de las muestras cada selector fue <em>el mejor de los
        cinco</em>. El simulador compara de dos en dos —un selector contra SJ en la misma muestra— y
        por eso sus porcentajes de victoria son mayores: ganarle a SJ es más fácil que ganarles a
        todos.</p>

{_M11_SIM}
{_M11_LEE}
      <h3>El Monte Carlo también tiene error</h3>

      <p>Mil réplicas no dan cifras exactas. Un porcentaje de victorias suelto tiene un error estándar
        de unos {n(MC["ucv"]["gana_ee"], 1)} puntos, pero dos porcentajes que salen de las mismas
        muestras se comparan por el error de su <em>diferencia</em>. La UCV le saca a la BCV
        {n(_DG11["ucv_bcv"]["dif"], 1)} puntos ({pct(MC["ucv"]["gana_pct"], 1)} frente a
        {pct(MC["bcv"]["gana_pct"], 1)}), con un error de {n(_DG11["ucv_bcv"]["ee"], 1)}: \(z\) =
        {n(_DG11["ucv_bcv"]["z"], 1)}, una ventaja real. La BCV le saca a SJ {n(_DG11["bcv_sj"]["dif"], 1)}
        ({pct(MC["SJ"]["gana_pct"], 1)} para SJ), con un error de {n(_DG11["bcv_sj"]["ee"], 1)}: \(z\) =
        {n(_DG11["bcv_sj"]["z"], 1)}, que no se distingue del ruido. Y cara a cara, sin los otros tres,
        la BCV le gana a SJ solo en el {pct(m11["cara_bcv_sj"], 1)} de las muestras: quién gana una
        carrera depende de quién más corre. El riesgo de cola de
        la UCV tiene un intervalo del 95 % de {n(m11["cola_ucv_ic"][0], 1)} a
        {n(m11["cola_ucv_ic"][1], 1)} %; el cero de la BCV solo dice que su riesgo está por debajo
        del {n(m11["cola_cero_cota"], 1)} % —la regla de tres: con cero casos en mil, el límite
        superior del 95 % es tres entre mil—, y el de SJ es cero por construcción, porque SJ es la
        referencia. Comparadas réplica a réplica, la UCV tiene un
        error medio {n(m11["emparejadas"]["ucv_sj"]["media"], 5)} mayor que SJ, con
        \(t\) = {n(m11["emparejadas"]["ucv_sj"]["t"], 1)}; la BCV, {n(m11["emparejadas"]["bcv_sj"]["media"], 6)}
        mayor, también detectable (\(t\) = {n(m11["emparejadas"]["bcv_sj"]["t"], 1)}) pero de un
        {pct(m11["emparejadas"]["bcv_sj"]["pct"], 1)}, que en la práctica no importa. Y
        <code>bw.ucv</code> avisó de que su mínimo caía en el extremo del intervalo en
        {ent(MC["ucv"]["avisos"])} de las {ent(m11["B"])} muestras.</p>

{_M11_COD}
      <p>La pestaña de R es el experimento entero: el EM, la verdad, la semilla de la casa y un
        <code>replicate()</code> que en cada vuelta saca una muestra y mide el ISE de los cinco
        selectores como suma de cuadrados sobre una rejilla. La de Python no puede repetirlo —numpy
        no reproduce el azar de R—, así que lee las mil réplicas de un CSV que escribe el
        precálculo y recalcula los mismos resúmenes: si las dos pestañas dan lo mismo, el CSV dice la
        verdad.</p>

{_M11_PLANO}""" + CIERRE

_PAR0 = SEL12["una_por_pareja_sin_ceros"]
_AP = BORDE["aporte"]
_RV12, _RM12 = BORDE["reflejada_valle"], BORDE["reflejada_moda"]
_M12_SIM_BORDE = sim(
    "apa-borde", "La densidad de las distancias al vecino, en el borde r = 0",
    f"Las cuatro curvas estiman la densidad de las {ent(m12['n'])} distancias con el mismo ancho: sin "
    "corregir (gris), reflejando los datos en el cero (verde), dividiendo por e(r) como density.ppp "
    "(morada) y con la corrección de Diggle (azul). La línea discontinua es la densidad que tendrían "
    "las distancias si las sedes estuvieran repartidas al azar. Los botones encienden y apagan cada "
    "curva, y el último cambia el tramo del eje: de 0 a 200 m, donde está el borde, o hasta 600 m. "
    "Antes de encender la verde: reflejar devuelve el área que el núcleo dejaba en r < 0; ¿crees "
    "que también arregla la forma de la curva cerca del cero?", alto=300)
_RS12 = BORDE["reflejada_sin_ceros"]
_M12_LEE_BORDE = como_se_lee(rf"""        <p>No. Reflejar devuelve el área, pero duplica la altura en \(r\) = 0 y deja la curva con
          pendiente cero en el borde, y eso solo es lo correcto si la densidad verdadera llega al cero
          alta y plana. La de las distancias al vecino no: bajo CSR, la discontinua, arranca en 0 y con
          pendiente, porque es raro tener una vecina a un metro.</p>
        <p>Aquí, además, la reflejada arranca en {n(BORDE["f0_reflejada"], 5)}, baja hasta
          {n(_RV12["f"], 5)} en \(r\) = {ent(_RV12["r"])} m y vuelve a subir hasta su moda, en
          {n(_RM12["r"], 1)} m. Ese máximo en el borde lo ponen enteros los {ent(m12["ceros"])} ceros, y
          reflejar lo duplica: sin ellos, la reflejada arrancaría en {n(_RS12["f"][0], 5)} y subiría desde
          ahí, hasta {n(_RS12["f"][3], 5)} en \(r\) = {ent(_RS12["r"][3])} m.</p>
        <p style="margin-bottom:0;">La morada coincide con la reflejada en \(r\) = 0, porque divide
          por \(e(0)\) = 1/2, y se separa de ella hacia dentro. La azul, la de Diggle, reparte la
          corrección dato a dato; como la reflejada, conserva el área exactamente, pero no fuerza la
          pendiente cero en el borde.</p>""")
_M12_DER = derivacion("der-empates", r"Ver por qué la UCV se va a \(-\infty\) con empates", [
    r"""              <p>Sea \(E\) el número de parejas \(\{i, j\}\) con \(x_i = x_j\). Cuando \(h \to 0\),
                los núcleos de datos distintos dejan de tocarse y solo sobreviven los términos de
                los datos empatados. El primer término de la UCV queda</p>
              $$\int \hat f_h^2 \approx \frac{R(K)}{n^2 h}\,(n + 2E),$$""",
    r"""              <p>porque cada dato se solapa consigo mismo y cada pareja empatada, dos veces. En el
                segundo, cada dato empatado ve a su gemelo a distancia cero, con peso \(K(0)\):</p>
              $$\frac{2}{n}\sum_i \hat f_{h,-i}(x_i) \approx \frac{4\,E\,K(0)}{n\,(n-1)\,h}.$$""",
    r"""              <p>Los dos crecen como \(1/h\). Si el segundo gana, la UCV se hunde sin límite
                al achicar \(h\); para \(n\) grande eso pasa cuando</p>
              $$\frac{E}{n} > \frac{R(K)}{4K(0) - 2R(K)}.$$"""],
    rf"""Con el núcleo gaussiano el umbral vale {n(m12["umbral_empates"], 4)}: si hay más de
    {n(m12["umbral_empates"], 4)} parejas empatadas por dato, el criterio no tiene mínimo y su ínfimo
    está en \(h = 0\).""")
_M12_SIM_EMP = sim(
    "apa-empates", "Dos anchos de banda para las mismas distancias",
    f"La curva es la estimación de núcleo gaussiano de las {ent(m12['n'])} distancias al vecino, con el ancho que "
    "elige cada botón: el que devuelve bw.ucv con todas las distancias y el que devuelve con una por "
    f"pareja recíproca y sin los ceros. La lectura cuenta los picos visibles entre 0 y "
    f"{ent(m12['curvas_hasta'])} m: los que sobresalen de sus valles más de un 5 % de la altura máxima. "
    "El eje vertical es el mismo con los dos anchos, para que las alturas se puedan comparar. Antes "
    "de pulsar: ¿cómo crees que se ve una densidad estimada con un ancho de tres metros?", alto=300)


def _fila_emp(etq, z):
    return fila(etq, ent(z["n"]), n(z["empates_por_n"], 4), n(z["ucv_h_minusculo"], 4), n(z["ucv_h20"], 5),
                n(z["ucv"], 2) + (" (aviso)" if z["aviso"] else ""), n(z["sj"], 2))


_M12_TAB = tabla(["Distancias", r"\(n\)", r"\(E/n\)", r"UCV con \(h\) = 0.001 m", r"UCV con \(h\) = 20 m",
                  "<code>bw.ucv</code> (m)", "<code>bw.SJ</code> (m)"],
                 _fila_emp("Todas", SEL12["todas"]) + _fila_emp("Sin los ceros", SEL12["sin_ceros"])
                 + _fila_emp("Una por pareja", SEL12["una_por_pareja"])
                 + _fila_emp("Una por pareja, sin ceros", _PAR0),
                 f"Parejas empatadas por dato, el criterio UCV exacto con un ancho minúsculo y los "
                 f"anchos que eligen bw.ucv y bw.SJ. El umbral es {n(m12['umbral_empates'], 4)}.")
_DEP12 = m12["depurada"]
_M12_LEE = como_se_lee(rf"""        <p>Con tres metros la curva es un peine: cada pareja de sedes a la misma distancia levanta
          su propio pico. Con veinte se ve la forma.</p>
        <p>La teoría de los once módulos anteriores supone que los datos son
          <strong>independientes</strong>: que cada uno es una extracción nueva de \(f\); el módulo 4 lo
          usó para el conteo binomial y el 10 para dejar un dato fuera. Una lista de distancias al
          vecino más cercano no lo es nunca, porque la misma distancia la mide cada extremo de una
          pareja recíproca, y las sedes que comparten dirección la miden igual a cero. La validación
          cruzada, que se basa en sacar un dato y predecirlo con los demás, es la primera víctima: el
          dato que sale deja dentro a su gemelo.</p>
        <p style="margin-bottom:0;">Dos matices. Los empates no son solo espaciales: las erupciones del
          módulo 10 ya tenían {n(m10["empates"]["por_dato"], 2)} parejas por dato, por redondeo; la
          diferencia es que allí sobrevivía un mínimo local estable y aquí no. Y quitar los gemelos quita
          los empates, no la dependencia: las {ent(_DEP12["n"])} distancias de la lista depurada siguen
          sin ser extracciones independientes, y su mediana, {n(_DEP12["mediana"], 1)} m, ya no es la de
          la lista entera, {n(m12["distancias"]["mediana"], 1)} m, porque cada pareja cuenta una vez. Por
          eso aquí sirve para elegir el ancho, y el ancho se aplica luego a las {ent(m12["n"])}.</p>""")


def _fila_sintesis(a, b, c):
    return fila(a, b, c)


_M12_SINTESIS = tabla(["En la recta (este apéndice)", "En el plano", "Dónde"],
                      _fila_sintesis("Densidad \\(f\\), integra 1 (módulo 1)", "Intensidad \\(\\lambda = n f\\), integra el número de puntos", "Cap. 4, módulo 2")
                      + _fila_sintesis("Histograma (módulo 2)", "Conteo por cuadrantes", "Cap. 4, módulos 2, 5 y 6")
                      + _fila_sintesis("Origen y ancho del histograma (módulo 2)", "Zonificación y escala del MAUP", "Cap. 3")
                      + _fila_sintesis("ASH (módulo 3)", "La rejilla que cambia al moverla; promediarla da un núcleo", "Cap. 5, módulo 1 (el promedio es de este apéndice)")
                      + _fila_sintesis("Contar en una ventana, \\(k/(nV)\\) (módulo 4)", "Conteo entre área, \\(\\hat\\lambda = n/|W|\\); la maldición de la dimensión", "Cap. 4, módulo 2")
                      + _fila_sintesis("Núcleo y ancho \\(h\\) (módulos 5–6)", "<code>density.ppp</code> y su σ", "Cap. 5, módulos 1–2")
                      + _fila_sintesis("<em>k</em> vecinos (módulo 7)", "<code>nndensity</code>, \\(G\\), Clark-Evans", "\\(G\\) y Clark-Evans: cap. 4, módulos 3 y 7; <code>nndensity</code>: módulo 4 de este apéndice")
                      + _fila_sintesis("Sesgo y varianza (módulo 8)", "Focos sueltos frente a una sola mancha", "Cap. 5, módulo 2")
                      + _fila_sintesis("Reglas de referencia (módulo 9)", "<code>bw.scott</code>, con \\(n^{-1/6}\\)", "Cap. 5, módulo 3")
                      + _fila_sintesis("UCV y LCV (módulo 10)", "<code>bw.diggle</code> y <code>bw.ppl</code>", "Cap. 5, módulo 3")
                      + _fila_sintesis("Una verdad conocida (módulo 11)", "Simular de un modelo y ver quién lo recupera: las envolventes", "Cap. 4, módulo 11")
                      + _fila_sintesis("Borde en \\(r = 0\\) (módulo 12)", "Corrección de borde de la KDE", "Cap. 5, módulo 4")
                      + _fila_sintesis("Datos que no son independientes (módulo 12)", "Validación cruzada espacial", "Cap. 10 (en preparación)"),
                      "Lo que cada módulo del apéndice es en el resto del material.")
_M12_COD = tabs("Las distancias al vecino de las sedes, en R y en Python", esc(R12.format(**SUB12)),
                esc(PY12.format(**SUB12)))

MOD12 = cabecera(
    12, TITULOS[11][0], INGLES[11],
    "Llevar el apéndice a un dato espacial —las distancias al vecino más cercano de las sedes de "
    "Bogotá— y ver qué supuestos de la teoría en una dimensión rompe: el borde y la "
    "independencia.") + rf"""
      <p>Para cada una de las {ent(m12["n"])} sedes del perímetro urbano se mide la distancia a la sede
        más cercana. Es un dato en una dimensión —una lista de metros— que sale de un dato espacial. Su
        función de distribución acumulada es la función \(G\) del capítulo 4, en su versión sin corregir
        el borde, y su densidad es la derivada de \(G\) para \(r &gt; 0\); en \(r\) = 0, \(G\) da un salto,
        que son las sedes a distancia cero. La media es
        {n(m12["distancias"]["media"], 1)} m y la mediana {n(m12["distancias"]["mediana"], 1)} m; la
        más aislada está a {n(m12["distancias"]["maximo"], 0)} m de su vecina. Si las sedes estuvieran
        repartidas al azar con la misma intensidad, {n(m12["lambda_km2"], 2)} por km², la distancia
        media sería {n(m12["csr"]["media"], 1)} m y la mediana {n(m12["csr"]["mediana"], 1)} m: el
        índice de Clark-Evans vale {n(m12["csr"]["clark_evans"], 4)}, menos de 1, y las sedes están
        más cerca entre sí de lo que pondría un reparto homogéneo. Eso es un exceso respecto de CSR,
        no una causa: una intensidad que cambia por la ciudad, como la que estima el capítulo 5, da la
        misma huella que una atracción entre sedes. El índice tampoco corrige el borde de la ventana:
        una sede junto al perímetro urbano puede tener su vecina de verdad fuera de él (capítulo 4,
        módulos 4 y 10). Este módulo trata un borde distinto, el de \(r\) = 0.</p>

      <h3>El borde en cero</h3>

      <p>Una distancia no puede ser negativa, pero un núcleo gaussiano centrado en una distancia
        pequeña reparte masa a los dos lados del cero. Con un ancho de
        {n(BORDE["h"], 2)} m —el que elige <code>bw.SJ</code> sobre una lista depurada que se explica
        abajo, y que luego se aplica a las {ent(m12["n"])} distancias— la estimación deja
        {pct(BORDE["masa_negativa_pct"], 2)} de su masa en distancias negativas, y en \(r = 0\) vale
        {n(BORDE["f0_sin"], 5)} por metro.</p>

      <p>Esa altura en el borde hay que leerla con cuidado. Más de la mitad, {n(BORDE["f0_ceros"], 5)},
        la ponen las {ent(m12["ceros"])} distancias iguales a cero: sedes que comparten dirección con
        otra. Son un <em>átomo</em>, una masa concentrada en un solo punto —el salto de \(G\) en
        \(r\) = 0 del capítulo 4, módulo 7—, y no densidad. Por eso ninguna de las cuatro estimaciones
        de abajo arranca en cero, como sí la del azar: los ceros las sostienen en \(r\) = 0. El
        argumento de siempre —«en el borde el estimador da la mitad de lo debido, porque
        solo le llega masa de un lado»— vale cuando la densidad verdadera llega al borde con altura; la
        de las distancias al vecino, bajo CSR, llega a cero. Hay tres arreglos. Los dos últimos son los
        que compara el módulo 4 del capítulo 5; el primero es propio de la recta, donde el borde es un
        punto y reflejar es trivial:</p>

      <ul>
        <li><strong>Reflejar</strong> los datos en el cero y sumar las dos mitades: el área vuelve a
          ser 1.</li>
        <li><strong>Dividir en el punto de estimación</strong> por la fracción del núcleo que cae en
          \(r \ge 0\), \(e(r) = \Phi(r/h)\), con \(\Phi\) la función de distribución normal
          estándar. Es la corrección por defecto de
          <code>density.ppp</code>. Un dato en el mismo borde aporta exactamente
          \(\ln 2\) = {n(_AP["ln2"], 4)}; uno a {n(_AP["d_max"], 2)} anchos del borde aporta
          {n(_AP["max"], 4)}, más de 1. El total depende de dónde estén los datos: aquí, con un
          {pct(BORDE["cerca_del_borde_pct"], 1)} de las distancias a menos de un ancho del cero, se
          queda en {n(BORDE["masa_e"], 4)}: por debajo de 1, al revés que en Kennedy, donde el capítulo 5
          (módulo 4) encontró que esta corrección se pasaba, porque aquí {ent(m12["ceros"])} datos están
          exactamente en el borde y cada uno aporta solo \(\ln 2\).</li>
        <li><strong>Dividir cada núcleo por su propia masa</strong> dentro del soporte: es la de
          Diggle, <code>diggle = TRUE</code>, y el área vale exactamente {n(BORDE["masa_diggle"], 0)},
          porque cada dato aporta 1 por construcción.</li>
      </ul>

{_M12_SIM_BORDE}
{_M12_LEE_BORDE}
      <h3>Los empates, y por qué la validación cruzada se rompe</h3>

      <p>Las distancias al vecino traen empates de dos clases. {ent(m12["ceros"])} sedes comparten
        dirección con otra, y su distancia es exactamente cero: todos esos ceros empatan entre sí. Y
        el {pct(m12["recipro"]["pct"], 1)} de las sedes forman <strong>parejas recíprocas</strong> —la
        vecina más cercana de A es B y la de B es A—, así que la misma distancia aparece dos veces.
        Las parejas no son una rareza de Bogotá: en un patrón completamente al azar del plano la
        fracción de recíprocas es \(6\pi/(8\pi + 3\sqrt3)\) = {n(m12["recipro"]["csr"], 4)} (Cox,
        1981), y simulando {ent(m12["recipro"]["csr_n"])} puntos sale {n(m12["recipro"]["csr_simulada"], 4)}.
        Son geometría, no agrupamiento.</p>

{_M12_DER}
      <p>Las parejas recíprocas de un patrón al azar aportan \(E/n\) =
        {n(m12["csr_parejas_por_n"], 4)}, ya por encima del umbral: <strong>sobre las distancias al
        vecino más cercano de un patrón al azar, la UCV no tiene mínimo</strong>, ni en el de
        cualquier patrón con más de un {pct(m12["umbral_recipro_pct"], 1)} de vecinas recíprocas,
        como Bogotá ({pct(m12["recipro"]["pct"], 1)}). La intuición: cada gemelo, al quedarse fuera, encuentra
        a su pareja en la misma cifra, y el criterio premia sin tope a los anchos que la ven más alta.
        La tabla lo comprueba sobre las sedes, quitando cada fuente de empates por separado:</p>

{_M12_TAB}
      <p>El signo del criterio no dice nada por sí solo: la UCV estima el MISE menos \(\int f^2\), y es
        negativa también en un buen ancho, como se ve en la columna de 20 m. Lo que delata el colapso es
        compararla consigo misma. Mientras quede cualquiera de las dos fuentes de empates, con un ancho
        de un milímetro el criterio cae por debajo de su valor en 20 m, y sigue cayendo al achicar
        \(h\); <code>bw.ucv</code> se queda en {n(SEL12["todas"]["ucv"], 2)} m, junto al extremo inferior
        de su búsqueda, {n(SEL12["todas"]["busqueda_desde"], 2)} m, con un aviso. No lo iguala al
        decimal —se detiene a una tolerancia—, así que un número sin el aviso no lo delataría. Sin
        parejas ni ceros vuelve a {firma(n(_PAR0["ucv"], 2), " m")}, junto a los {n(_PAR0["sj"], 2)} m
        de SJ.</p>

{_M12_SIM_EMP}
{_M12_LEE}
{_M12_COD}
      <p>El bloque de R usa <code>nndist()</code> y <code>nnwhich()</code> de spatstat: la segunda
        dice quién es la vecina, y <code>quien[quien] == seq_along(quien)</code> es la pregunta «¿mi vecina me
        tiene a mí por vecina?». Para quedarse con una distancia por pareja se conserva la de la sede
        de índice menor. La pestaña de Python hace lo mismo con <code>cKDTree</code>, con una
        precaución que la de R no necesita y que conviene leer: entre sedes que comparten dirección
        hay que elegir vecina, y spatstat elige la de índice mayor; con otro desempate el porcentaje de
        recíprocas cambia.</p>

      <h3>El apéndice entero, en el plano</h3>

{_M12_SINTESIS}
{en_el_plano(r'''        <p>Las dos últimas filas de la tabla son de este módulo, y la última es la que más lejos
          llega. El capítulo 10, todavía en
          preparación, volverá sobre ella con la validación cruzada de modelos: separar al azar los datos de entrenamiento y de
          prueba supone que son independientes, y con datos espaciales un dato de prueba casi siempre
          tiene un vecino de entrenamiento al lado: un pariente del gemelo que aquí tumba a la UCV.</p>''')}""" + CIERRE


# =====================================================================
# MÓDULO 13 · Autoevaluación, ejercicios y lecturas
# =====================================================================
def _codigo(texto):
    """Los acentos graves del enunciado pasan a <code>, no se borran."""
    return _re.sub(r"`([^`]+)`", r"<code>\1</code>", texto)


def _pregunta(pide):
    i = 1 if pide.startswith("¿") else 0
    t = pide[:i] + pide[i].upper() + pide[i + 1:]
    if i and not t.endswith("?"):
        return t + "?"
    return t if t[-1] in ".?!" else t + "."


def _valor(v):
    return f"{v:g}" if isinstance(v, (int, float)) and float(v).is_integer() else n(v, 4)


def ejercicio(k, e):
    """El marcado de la casa (`.ejercicio-guiado`, `.ejercicio-boton`), con una
    respuesta por pregunta anclada a un trozo literal del enunciado."""
    pasos = "".join(
        f'                <tr><th scope="row">{_codigo(p["paso"])}</th>'
        f'<td>{_valor(p["valor"])}</td></tr>\n'
        for p in e["pasos"])
    resp = e["solucion"].get("respuestas") or []
    if not resp:
        sys.exit(f"PARADO: el ejercicio {k} llega sin respuestas; regenera con genera_apendicea.R")
    for r in resp:
        if r["pide"] not in e["enunciado"]:
            sys.exit(f"PARADO: una respuesta del ejercicio {k} contesta a «{r['pide']}», "
                     "que su enunciado no pregunta")
    respuestas = "".join(
        f'            <p class="ejercicio-respuesta"><strong>{_codigo(_pregunta(r["pide"]))}</strong>\n'
        f'              {_codigo(r["respuesta"])}</p>\n'
        for r in resp)
    # La pista: el PLAN la prometía y la plantilla trae su panel, pero la
    # primera versión solo ofrecía «Solución», y quien se atascaba no tenía
    # más salida que leer la respuesta entera (revisión 2).
    if not e.get("pista"):
        sys.exit(f"PARADO: el ejercicio {k} llega sin pista; regenera con genera_apendicea.R")
    plural = " y " in e["modulos"] or "," in e["modulos"]
    practica = ("módulos " if plural else "módulo ") + e["modulos"]
    return f"""
        <div class="ejercicio-guiado">
          <p class="ejercicio-enunciado"><span class="ejercicio-numero">{k}.</span><strong>{e['titulo']}</strong>
            <span class="text-gray-500">({practica})</span>.
            {_codigo(e['enunciado'])}</p>
          <div class="ejercicio-acciones">
            <button type="button" class="ejercicio-boton" aria-expanded="false" aria-controls="apa-e{k}-pista">
              <i class="fas fa-lightbulb" aria-hidden="true"></i> Pista <i class="fas fa-chevron-down" aria-hidden="true"></i>
            </button>
            <button type="button" class="ejercicio-boton" aria-expanded="false" aria-controls="apa-e{k}-sol">
              <i class="fas fa-key" aria-hidden="true"></i> Solución <i class="fas fa-chevron-down" aria-hidden="true"></i>
            </button>
          </div>
          <div class="ejercicio-panel pista" id="apa-e{k}-pista" hidden>
            <p style="margin:0;">{_codigo(e['pista'])}</p>
          </div>
          <div class="ejercicio-panel solucion" id="apa-e{k}-sol" hidden>
            <table>
              <caption>Los pasos de la solución, calculados en R por <code>precalculo/genera_apendicea.R</code>.</caption>
              <thead><tr><th scope="col">Paso</th><th scope="col">Valor</th></tr></thead>
              <tbody>
{pasos}
              </tbody>
            </table>
{respuestas}            <p class="ejercicio-lectura">{_codigo(e['solucion']['lectura'])}</p>
          </div>
        </div>
"""


N_EJERCICIOS = S["meta"]["n_ejercicios"]
EJERCICIOS = [S[f"e{i}"] for i in range(1, N_EJERCICIOS + 1)]
EJ = "".join(ejercicio(i + 1, e) for i, e in enumerate(EJERCICIOS))
N_PREGUNTAS = 17

_M13_QUIZ = quiz_html(
    "apa-quiz", "Autoevaluación del apéndice A",
    "Diecisiete preguntas, al menos una por módulo, sobre densidad e intensidad, el histograma y el MAUP, el ASH, la ventana, los núcleos y sus "
    "convenciones, los k vecinos, el sesgo y la varianza, los selectores del ancho de banda y lo que "
    "un dato espacial le hace a todo eso.")

_LECTURAS = """      <div class="references">
        <h3><i class="fas fa-book-open mr-2" aria-hidden="true"></i>Lecturas de este apéndice</h3>
        <ul style="margin-bottom:0;">
          <li>Silverman, B. W. (1986). <em>Density Estimation for Statistics and Data Analysis</em>.
            Chapman &amp; Hall. <strong>Capítulos 2 y 3</strong>: el histograma, el estimador ingenuo, el
            de núcleo y la regla que lleva su nombre. El texto de referencia más legible.</li>
          <li>Wand, M. P. y Jones, M. C. (1995). <em>Kernel Smoothing</em>. Chapman &amp; Hall.
            <strong>Capítulos 2 y 3</strong>: el MISE, el AMISE, la eficiencia de los núcleos y los
            selectores <em>plug-in</em>.</li>
          <li>Scott, D. W. (2015). <em>Multivariate Density Estimation</em> (2.ª ed.). Wiley.
            <strong>Capítulos 3 y 5</strong>: el histograma y el ASH, con la tasa en \\(d\\) dimensiones.</li>
          <li>Rosenblatt, M. (1956). Remarks on some nonparametric estimates of a density function.
            <em>The Annals of Mathematical Statistics</em>, 27(3), 832–837.
            <a href="https://doi.org/10.1214/aoms/1177728190">doi:10.1214/aoms/1177728190</a></li>
          <li>Parzen, E. (1962). On estimation of a probability density function and mode. <em>The
            Annals of Mathematical Statistics</em>, 33(3), 1065–1076.
            <a href="https://doi.org/10.1214/aoms/1177704472">doi:10.1214/aoms/1177704472</a></li>
          <li>Epanechnikov, V. A. (1969). Non-parametric estimation of a multivariate probability
            density. <em>Theory of Probability &amp; Its Applications</em>, 14(1), 153–158.
            <a href="https://doi.org/10.1137/1114019">doi:10.1137/1114019</a></li>
          <li>Scott, D. W. (1979). On optimal and data-based histograms. <em>Biometrika</em>, 66(3),
            605–610. <a href="https://doi.org/10.1093/biomet/66.3.605">doi:10.1093/biomet/66.3.605</a></li>
          <li>Scott, D. W. (1985). Averaged shifted histograms: effective nonparametric density
            estimators in several dimensions. <em>The Annals of Statistics</em>, 13(3), 1024–1040.
            <a href="https://doi.org/10.1214/aos/1176349654">doi:10.1214/aos/1176349654</a></li>
          <li>Scott, D. W. y Terrell, G. R. (1987). Biased and unbiased cross-validation in density
            estimation. <em>Journal of the American Statistical Association</em>, 82(400), 1131–1146.
            <a href="https://doi.org/10.1080/01621459.1987.10478550">doi:10.1080/01621459.1987.10478550</a></li>
          <li>Sheather, S. J. y Jones, M. C. (1991). A reliable data-based bandwidth selection method
            for kernel density estimation. <em>Journal of the Royal Statistical Society, Series B</em>,
            53(3), 683–690. <a href="https://doi.org/10.1111/j.2517-6161.1991.tb01857.x">doi:10.1111/j.2517-6161.1991.tb01857.x</a></li>
          <li>Diggle, P. (1985). A kernel method for smoothing point process data. <em>Applied
            Statistics</em>, 34(2), 138–147. <a href="https://doi.org/10.2307/2347366">doi:10.2307/2347366</a>
            — el estimador de intensidad del capítulo 5 y su corrección de borde.</li>
          <li>Berman, M. y Diggle, P. (1989). Estimating weighted integrals of the second-order
            intensity of a spatial point process. <em>Journal of the Royal Statistical Society, Series
            B</em>, 51(1), 81–92. <a href="https://doi.org/10.1111/j.2517-6161.1989.tb01750.x">doi:10.1111/j.2517-6161.1989.tb01750.x</a>
            — el criterio de <code>bw.diggle</code>.</li>
          <li>Cronie, O. y van Lieshout, M. N. M. (2018). A non-model-based approach to bandwidth
            selection for kernel estimators of spatial intensity functions. <em>Biometrika</em>,
            105(2), 455–462. <a href="https://doi.org/10.1093/biomet/asy001">doi:10.1093/biomet/asy001</a></li>
          <li>Clark, P. J. y Evans, F. C. (1954). Distance to nearest neighbor as a measure of spatial
            relationships in populations. <em>Ecology</em>, 35(4), 445–453.
            <a href="https://doi.org/10.2307/1931034">doi:10.2307/1931034</a></li>
          <li>Cox, T. F. (1981). Reflexive nearest neighbours. <em>Biometrics</em>, 37(2), 367–369.
            <a href="https://doi.org/10.2307/2530424">doi:10.2307/2530424</a> — la fracción de
            vecinos recíprocos del módulo 12.</li>
        </ul>
      </div>
"""

MOD13 = cabecera(
    13, TITULOS[12][0], INGLES[12],
    "Comprobar lo aprendido y practicar, sobre datos pequeños y sobre las sedes de Kennedy, las "
    "decisiones que el apéndice obliga a declarar.") + rf"""
      <p>El apéndice ha defendido una idea desde el módulo 2: <strong>una densidad estimada no es
        una descripción del dato, es una respuesta que depende de decisiones</strong> —el ancho, el
        origen, el núcleo, el número de vecinos, el selector, la corrección de borde— y de supuestos
        que el dato puede no cumplir. Las preguntas no llevan nota y cada opción trae su
        explicación, así que equivocarse aquí vale tanto como acertar.</p>

{_M13_QUIZ}
      <p>Y diez ejercicios guiados con su solución calculada. Los nueve primeros vienen del
        documento del que nace el apéndice y se hacen a mano o con pocas líneas de código; el décimo
        lleva el módulo 12 a otra localidad, y pide reconocer un número que sale sin aviso y no se
        puede creer.</p>

{EJ}
{_LECTURAS}
      <div class="tip-box">
        <h4>Dónde sigue esto</h4>
        <p style="margin-bottom:0;">El destino natural del apéndice es el capítulo 5,
          <a href="capitulo-5-intensidad-nucleos.html">Intensidad por núcleos y procesos
          puntuales</a>: sus módulos 1 a 4 son los módulos 4 a 6 y 8 a 12 de este apéndice en el
          plano. El capítulo 4, <a href="capitulo-4-patrones-puntuales.html">Patrones puntuales</a>,
          trae las distancias al vecino del módulo 7 y del 12, y el capítulo 3,
          <a href="capitulo-3-cartografia-maup.html">Cartografía estadística y el MAUP</a>, las dos
          perillas del histograma del módulo 2.</p>
      </div>
""" + CIERRE

MODULOS = (MOD1 + MOD2 + MOD3 + MOD4 + MOD5 + MOD6 + MOD7 + MOD8 + MOD9 + MOD10 + MOD11
           + MOD12 + MOD13)

COURSE_DATA = (
    "    const courseData = {\n      modules: [\n"
    + "".join(f"        {{ id: {i + 1}, title: {json.dumps(t, ensure_ascii=False)}, "
              f"subtitle: {json.dumps(s, ensure_ascii=False)} }},\n"
              for i, (t, s) in enumerate(TITULOS))
    + "      ]\n    };\n\n"
    + "    // Todas las cifras del apéndice, tal como salieron del precálculo.\n"
    + "    // El JavaScript no lleva ninguna escrita: las saca de aquí.\n"
    + "    const DATOS_APA = " + json.dumps(D, ensure_ascii=False) + ";\n"
    + "    const SOL_APA = " + json.dumps(S, ensure_ascii=False) + ";\n"
    + "    const DA = DATOS_APA;\n"
)


# =====================================================================
# LOS SIMULADORES
#
# Los ayudantes son los del capítulo 5 (lectura, botonera, deslizador,
# gráfico), con el sufijo A. El motor `densidad1d.js` va delante, en línea,
# y deja `D1` en el ámbito global. Toda cifra que un simulador ENSEÑA sale
# de `DA` (el JSON) o la calcula `D1`, que tiene su prueba contra R.
# =====================================================================
JS_PREAMBULO = r"""
    const nA = (x, d) => Number(x).toFixed(d == null ? 4 : d);
    const milA = x => Math.round(Number(x)).toLocaleString('es-ES').replace(/\./g, ' ');
    const CA = { verde: '#1a7358', naranja: '#FF6600', gris: '#8a8a8a', azul: '#0072B2',
                 rojo: '#D55E00', morado: '#7B3FA0', grisClaro: 'rgba(138,138,138,0.25)',
                 verdeSuave: 'rgba(26,115,88,0.18)', naranjaSuave: 'rgba(255,102,0,0.15)',
                 azulSuave: 'rgba(0,114,178,0.15)' };

    function lecturaA(raiz, pares) {
      const caja = raiz.querySelector('.simulador-lectura');
      if (!caja) return;
      caja.innerHTML = pares.map(p =>
        `<span class="lectura-item"><span class="lectura-etiqueta">${p[0]}</span> ` +
        `<span class="lectura-valor">${p[1]}</span></span>`).join('');
    }

    // Una fila de botones sobre `.geomapa-boton`, la clase de la casa.
    // La fila ocupa SIEMPRE un renglón entero: con un botón dentro, la
    // plantilla convierte `.simulador-controles` en una fila flexible
    // (`:has(.geomapa-boton)`) y entonces `gridColumn` deja de valer; sin
    // `flexBasis` los botones de dos grupos salían en una sola fila y un
    // deslizador vecino se encogía a 125 px (revisión 2, 2026-10-02).
    // `rotulo`, si viene, nombra el grupo delante de sus botones.
    function filaA(raiz, rotulo) {
      const cont = raiz.querySelector('.simulador-controles');
      const fila = document.createElement('div');
      fila.style.gridColumn = '1 / -1'; fila.style.flexBasis = '100%';
      fila.style.display = 'flex'; fila.style.flexWrap = 'wrap'; fila.style.gap = '6px';
      fila.style.alignItems = 'center';
      cont.appendChild(fila);
      if (rotulo) {
        const r = document.createElement('span');
        r.className = 'lectura-etiqueta'; r.textContent = rotulo;
        fila.appendChild(r);
      }
      return fila;
    }
    function botoneraA(raiz, ops, alPulsar, activo, rotulo) {
      const fila = filaA(raiz, rotulo);
      const ini = Math.max(0, activo || 0);
      fila.insertAdjacentHTML('beforeend', ops.map((o, i) =>
        `<button type="button" class="geomapa-boton${i === ini ? ' activo' : ''}" ` +
        `aria-pressed="${i === ini}" data-i="${i}">${o}</button>`).join(''));
      fila.addEventListener('click', e => {
        const b = e.target.closest('.geomapa-boton');
        if (!b) return;
        fila.querySelectorAll('.geomapa-boton').forEach(x => {
          x.classList.remove('activo'); x.setAttribute('aria-pressed', 'false'); });
        b.classList.add('activo'); b.setAttribute('aria-pressed', 'true');
        alPulsar(+b.dataset.i);
      });
    }

    // Interruptores: botones que se encienden y apagan cada uno por su cuenta.
    function interruptoresA(raiz, ops, encendidos, alCambiar, rotulo) {
      const fila = filaA(raiz, rotulo);
      fila.insertAdjacentHTML('beforeend', ops.map((o, i) =>
        `<button type="button" class="geomapa-boton${encendidos[i] ? ' activo' : ''}" ` +
        `aria-pressed="${!!encendidos[i]}" data-i="${i}">${o}</button>`).join(''));
      fila.addEventListener('click', e => {
        const b = e.target.closest('.geomapa-boton');
        if (!b) return;
        const i = +b.dataset.i;
        encendidos[i] = !encendidos[i];
        b.classList.toggle('activo', encendidos[i]);
        b.setAttribute('aria-pressed', String(encendidos[i]));
        alCambiar(encendidos);
      });
    }

    // Deslizador sobre una lista DISCRETA de posiciones: `opciones` es
    // [[valor, rótulo]] y `aria-valuetext` anuncia la magnitud, no la posición.
    function deslizadorA(raiz, opciones, etiqueta, iniPos, alCambiar) {
      const cont = raiz.querySelector('.simulador-controles');
      const id = 'ctl-' + Math.random().toString(36).slice(2, 10);
      const caja = document.createElement('div');
      caja.className = 'control-slider';
      // Si el contenedor es una fila flexible (hay botones), cada deslizador
      // pide al menos 16rem: dos caben lado a lado en el escritorio y en el
      // teléfono bajan a su propio renglón.
      caja.style.flex = '1 1 16rem';
      const rotulo = document.createElement('label');
      rotulo.setAttribute('for', id);
      rotulo.append(etiqueta + ' ');
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
      input.addEventListener('input', () => { pinta(); alCambiar(opciones[+input.value][0]); });
      pinta();
      caja.appendChild(rotulo); caja.appendChild(input); cont.appendChild(caja);
    }

    // CONTRATO DEL MOTOR: un simulador DEVUELVE sus gráficos, para que
    // `destruirSimuladores()` pueda matarlos.
    function graficoA(raiz, tipo, data, opciones) {
      return new Chart(raiz.querySelector('canvas').getContext('2d'), {
        type: tipo, data: data,
        options: Object.assign({ responsive: true, maintainAspectRatio: false, animation: false,
                                 parsing: false, normalized: true }, opciones || {})
      });
    }

    const curvaA = (xs, ys) => xs.map((x, i) => ({ x: x, y: ys[i] }))
      .filter(p => Number.isFinite(p.x) && Number.isFinite(p.y));

    // Un histograma como polígono explícito: DOS puntos por barra, (corte_i,
    // altura_i) y (corte_i+1, altura_i), y una línea recta entre ellos. Sin
    // `stepped`. La primera versión usaba `stepped: 'after'` con un punto por
    // corte, y en Chart.js 4 ese modo pinta el tramo [x_i, x_i+1] con la altura
    // del punto SIGUIENTE: cada barra salía un intervalo a la izquierda, la
    // primera no se veía y la última quedaba en cero. Ningún auditor lo veía;
    // lo midió un revisor leyendo píxeles (revisión 2, 2026-10-02).
    function escaleraA(cortes, alturas) {
      const p = [{ x: cortes[0], y: 0 }];
      alturas.forEach((h, i) => { p.push({ x: cortes[i], y: h }); p.push({ x: cortes[i + 1], y: h }); });
      p.push({ x: cortes[alturas.length], y: 0 });
      return p;
    }

    const ejesA = (tx, ty, extra) => Object.assign({
      x: { type: 'linear', title: { display: true, text: tx } },
      y: { title: { display: true, text: ty }, beginAtZero: true }
    }, extra || {});
"""

SIMULADORES_JS = JS_PREAMBULO + r"""
    // --- Módulo 1 · el área es la proporción ---------------------------
    // Dos botoneras además del intervalo: la UNIDAD del eje (minutos u horas)
    // y la ESCALA (densidad o intensidad, × n). Las dos cambian las alturas y
    // ninguna cambia lo que el área cuenta; esa es la lección del módulo, y
    // con barras de un minuto no se veía, porque altura y área coincidían.
    SIMULADORES['apa-area'] = function (raiz) {
      const m = DA.m1, c = m.cortes, k = m.densidades.length, MIN_H = m.minutos_por_hora;
      let a = c.indexOf(m.barra_max.desde), b = a + 1, enHoras = 0, intens = 0;
      const g = graficoA(raiz, 'line', { datasets: [
        { label: 'barras dentro del intervalo', data: [], borderColor: CA.verde, order: 0,
          backgroundColor: 'rgba(26,115,88,0.45)', fill: 'origin', pointRadius: 0, borderWidth: 2 },
        { label: 'histograma', data: [], borderColor: CA.gris, order: 1,
          backgroundColor: CA.grisClaro, fill: 'origin', pointRadius: 0, borderWidth: 1.5 },
        { label: 'espera media', data: [], borderColor: CA.naranja, borderDash: [6, 4], order: 0,
          pointRadius: 0, borderWidth: 2 }
      ] }, { scales: ejesA('', '') });
      const fmt = v => v >= 100 ? milA(v) : nA(v, 2);
      const pinta = () => {
        const fx = enHoras ? 1 / MIN_H : 1, fy = (enHoras ? MIN_H : 1) * (intens ? m.n : 1);
        const unidad = enHoras ? 'hora' : 'minuto', cs = c.map(v => v * fx);
        const alt = m.densidades.map((d, i) => (i >= a && i < b) ? d * fy : 0);
        const tope = Math.max(...m.densidades) * fy * 1.08;
        g.data.datasets[0].data = escaleraA(cs, alt);
        g.data.datasets[1].data = escaleraA(cs, m.densidades.map(d => d * fy));
        g.data.datasets[2].data = [{ x: m.media * fx, y: 0 }, { x: m.media * fx, y: tope }];
        g.options.scales.x.title.text = 'tiempo de espera (' + (enHoras ? 'horas' : 'minutos') + ')';
        g.options.scales.y.title.text = (intens ? 'clientes' : 'densidad') + ' por ' + unidad + ' de espera';
        g.options.scales.y.max = tope;
        g.update('none');
        let area = 0, clientes = 0, alto = 0;
        for (let i = a; i < b; i++) { area += m.densidades[i] * (c[i + 1] - c[i]); clientes += m.conteos[i];
                                       alto = Math.max(alto, m.densidades[i]); }
        lecturaA(raiz, [
          ['intervalo', '[' + c[a] + ', ' + c[b] + ') min'],
          [intens ? 'área de las barras (clientes)' : 'área de las barras (proporción)',
           intens ? fmt(area * m.n) : nA(area, 2)],
          ['clientes en el intervalo', clientes + ' de ' + m.n],
          ['barra más alta dentro', fmt(alto * fy) + (intens ? ' clientes' : '') + ' por ' + unidad + ' de espera']]);
      };
      deslizadorA(raiz, c.slice(0, k).map((v, i) => [i, v + ' min']), 'desde', a, v => {
        a = v; if (b <= a) b = a + 1; pinta(); });
      deslizadorA(raiz, c.slice(1).map((v, i) => [i + 1, v + ' min']), 'hasta', b - 1, v => {
        b = v; if (a >= b) a = b - 1; pinta(); });
      botoneraA(raiz, ['minutos', 'horas'], i => { enHoras = i; pinta(); }, 0, 'eje en');
      botoneraA(raiz, ['densidad', 'intensidad (× n)'], i => { intens = i; pinta(); }, 0, 'alturas como');
      pinta();
      return [g];
    };

    // --- Módulo 2 · ancho y origen ----------------------------------------
    SIMULADORES['apa-histograma'] = function (raiz) {
      const x = DA.m2.eruptions;
      let h = DA.m2.h_origen, f = 0;
      const g = graficoA(raiz, 'line', { datasets: [
        { label: 'histograma', data: [], borderColor: CA.verde,
          backgroundColor: CA.verdeSuave, fill: 'origin', pointRadius: 0, borderWidth: 2 }
      ] }, { plugins: { legend: { display: false } },
             scales: ejesA('duración de la erupción (minutos)', 'densidad', { x: { type: 'linear', min: 1, max: 6,
               title: { display: true, text: 'duración de la erupción (minutos)' } } }) });
      const pinta = () => {
        const r = D1.histograma(x, h, f);
        g.data.datasets[0].data = escaleraA(r.cortes, r.densidad);
        g.update('none');
        lecturaA(raiz, [['ancho', nA(h, 2) + ' min'], ['origen corrido', nA(f * h, 4) + ' min'],
                        ['barras', r.conteos.length], ['modas', D1.modas(r.densidad)],
                        ['altura máxima', nA(Math.max(...r.densidad), 3)]]);
      };
      const ini = DA.m2.anchos.findIndex(v => Math.abs(v - DA.m2.h_origen) < 1e-9);
      deslizadorA(raiz, DA.m2.anchos.map(v => [v, nA(v, 2) + ' min']), 'ancho', ini, v => { h = v; pinta(); });
      deslizadorA(raiz, DA.m2.fracs.map(v => [v, nA(v, 2) + ' del ancho']), 'origen', 0, v => { f = v; pinta(); });
      pinta();
      return [g];
    };

    // --- Módulo 3 · el ASH y el triangular -----------------------------
    SIMULADORES['apa-ash'] = function (raiz) {
      const x = DA.m2.eruptions, h = DA.m3.triangular.h;
      const gr = D1.secuencia(D1.minimo(x) - 1, D1.maximo(x) + 1, DA.m3.triangular.paso_rejilla);
      const tri = D1.kdeTriangular(x, h, gr);
      const MS = [1, 2, 4, 8, 16, 32, 64];
      const g = graficoA(raiz, 'line', { datasets: [
        { label: 'ASH', data: [], borderColor: CA.naranja, pointRadius: 0, borderWidth: 2 },
        { label: 'núcleo triangular', data: curvaA(gr, tri), borderColor: CA.verde, borderDash: [6, 4],
          pointRadius: 0, borderWidth: 2 }
      ] }, { scales: ejesA('duración de la erupción (minutos)', 'densidad') });
      const pinta = m => {
        const a = D1.ash(x, h, m, gr);
        g.data.datasets[0].data = curvaA(gr, a);
        g.update('none');
        const d = D1.distanciaMaxima(a, tri);
        lecturaA(raiz, [['histogramas promediados m', m], ['ancho h', nA(h, 1) + ' min'],
                        ['distancia máxima al triangular', nA(d, 5)], ['m × distancia', nA(m * d, 3)]]);
      };
      deslizadorA(raiz, MS.map(m => [m, String(m)]), 'm', 0, pinta);
      pinta(1);
      return [g];
    };

    // --- Módulo 4 · centro, nube y verdad ----------------------------------
    SIMULADORES['apa-ventana'] = function (raiz) {
      const m = DA.m4, V = m.V;
      let iN = 1, iV = V.findIndex(v => v >= m.v_peq.V);
      // Eje y fijo y lo bastante alto para la banda más ancha (n = 25, V = 0.05
      // llega a 1.52): con 1.2 se recortaba justo el caso que más enseña.
      const g = graficoA(raiz, 'line', { datasets: [
        { label: 'media + 2 desviaciones', data: [], borderColor: 'transparent', pointRadius: 0, fill: false, order: 3 },
        { label: 'banda de dos desviaciones', data: [], borderColor: 'transparent', backgroundColor: CA.verdeSuave,
          pointRadius: 0, fill: '-1', order: 3 },
        { label: 'valor esperado de k/(nV)', data: [], borderColor: CA.verde, pointRadius: 0, borderWidth: 2.5, order: 1 },
        { label: 'verdad', data: [], borderColor: CA.gris, borderDash: [6, 4], pointRadius: 0, borderWidth: 1.5, order: 2 },
        { label: 'ancho marcado', data: [], type: 'scatter', backgroundColor: CA.naranja, pointRadius: 7, order: 0 }
      ] }, { plugins: { legend: { labels: { filter: it => it.datasetIndex >= 1 } } },
             scales: { x: { type: 'logarithmic', title: { display: true, text: 'ancho de la ventana V (escala log)' } },
                       y: { min: 0, max: 1.6, title: { display: true, text: 'k / (nV)' } } } });
      const pinta = () => {
        const p = m.por_n[iN];
        g.data.datasets[0].data = curvaA(V, p.media.map((u, i) => u + 2 * p.sd[i]));
        g.data.datasets[1].data = curvaA(V, p.media.map((u, i) => Math.max(0, u - 2 * p.sd[i])));
        g.data.datasets[2].data = curvaA(V, p.media);
        g.data.datasets[3].data = curvaA(V, V.map(() => m.f0));
        g.data.datasets[4].data = [{ x: V[iV], y: p.media[iV] }];
        g.update('none');
        lecturaA(raiz, [['n', p.n], ['V', nA(V[iV], 3)], ['valor esperado', nA(p.media[iV])],
                        ['sesgo', nA(p.media[iV] - m.f0, 5)], ['desviación típica', nA(p.sd[iV])],
                        ['ECM', nA(p.ecm[iV], 5)], ['P(ventana vacía)', nA(p.vacia[iV])],
                        ['mejor V para este n', nA(p.v_opt, 2)]]);
      };
      botoneraA(raiz, m.ns.map(v => 'n = ' + milA(v)), i => { iN = i; pinta(); }, iN);
      deslizadorA(raiz, V.map((v, i) => [i, nA(v, 3)]), 'V', iV, i => { iV = i; pinta(); });
      pinta();
      return [g];
    };

    // --- Módulo 5 · una loma por dato ----------------------------------
    SIMULADORES['apa-lomas'] = function (raiz) {
      const x = DA.m5.gaussiano.datos, gr = D1.rejilla(-2, 12, 301);
      const r5 = DA.m5.rejilla, gm = D1.rejilla(r5.desde, r5.hasta, r5.puntos);
      const H = []; for (let v = 0.2; v <= 2.501; v += 0.05) H.push(Math.round(v * 100) / 100);
      const sets = x.map((xi, i) => ({ label: i === 0 ? 'una loma por dato' : '', data: [],
        borderColor: CA.naranja, borderWidth: 1, pointRadius: 0 }));
      sets.push({ label: 'su suma: la densidad estimada', data: [], borderColor: CA.verde, borderWidth: 3, pointRadius: 0 });
      sets.push({ label: 'datos', data: x.map(v => ({ x: v, y: 0 })), type: 'scatter',
                  backgroundColor: CA.gris, pointRadius: 5 });
      const g = graficoA(raiz, 'line', { datasets: sets }, {
        plugins: { legend: { labels: { filter: it => it.text !== '' } } },
        scales: ejesA('x', 'densidad') });
      const pinta = h => {
        x.forEach((xi, i) => { g.data.datasets[i].data = curvaA(gr, D1.kde([xi], gr, h, 'gaussian').map(v => v / x.length)); });
        g.data.datasets[x.length].data = curvaA(gr, D1.kde(x, gr, h, 'gaussian'));
        g.update('none');
        lecturaA(raiz, [['ancho h', nA(h, 2)], ['f̂(4)', nA(D1.kde(x, [4], h, 'gaussian')[0])],
                        ['modas', D1.modas(D1.kde(x, gm, h, 'gaussian'))]]);
      };
      // Arranca con las cinco lomas separadas, no con la respuesta a la vista.
      const h0 = DA.m5.h_inicial, ini = H.indexOf(h0);
      deslizadorA(raiz, H.map(v => [v, nA(v, 2)]), 'h', ini, pinta);
      pinta(h0);
      return [g];
    };

    // --- Módulo 6 · cinco núcleos ----------------------------------------
    SIMULADORES['apa-nucleos'] = function (raiz) {
      const x = DA.m6.muestra_trimodal, bw = DA.m6.trimodal.bw;
      const gr = D1.rejilla(D1.minimo(x) - 3 * bw, D1.maximo(x) + 3 * bw, 2048);
      const ref = D1.kde(x, gr, bw, 'gaussian');
      const NOM = ['rectangular', 'triangular', 'epanechnikov', 'biweight', 'gaussian'];
      const ETQ = ['caja', 'triangular', 'Epanechnikov', 'biweight', 'gaussiano'];
      let k = 0, modo = 0;
      // El núcleo elegido se dibuja ENCIMA (`order` menor): antes la gris de
      // referencia lo tapaba justo en los picos.
      const g = graficoA(raiz, 'line', { datasets: [
        { label: 'gaussiano de referencia', data: curvaA(gr, ref), borderColor: CA.gris, borderWidth: 2,
          pointRadius: 0, order: 1 },
        { label: 'núcleo elegido', data: [], borderColor: CA.verde, borderWidth: 1.75, pointRadius: 0, order: 0 }
      ] }, { scales: ejesA('x', 'densidad') });
      const pinta = () => {
        const nombre = NOM[k];
        // «Mismo soporte»: todos acaban donde acaba el Epanechnikov de R, en ±√5·bw.
        const b = (modo === 0 || nombre === 'gaussian') ? bw : D1.ESCALA.epanechnikov * bw / D1.ESCALA[nombre];
        const y = D1.kde(x, gr, b, nombre);
        g.data.datasets[1].data = curvaA(gr, y);
        g.update('none');
        lecturaA(raiz, [['núcleo', ETQ[k]], ['desviación típica del núcleo', nA(b, 3)],
                        ['semiancho del soporte', nombre === 'gaussian' ? 'sin soporte' : nA(D1.ESCALA[nombre] * b, 3)],
                        ['máximos locales', D1.modas(y)],
                        ['mayor diferencia con el gaussiano', nA(D1.distanciaMaxima(y, ref))]]);
      };
      botoneraA(raiz, ETQ, i => { k = i; pinta(); }, 0, 'núcleo');
      botoneraA(raiz, ['misma desviación típica', 'mismo soporte'], i => { modo = i; pinta(); }, 0, 'igualar por');
      pinta();
      return [g];
    };

    // --- Módulo 7 · k vecinos ----------------------------------------------
    SIMULADORES['apa-knn'] = function (raiz) {
      const z = DA.m7.mezcla, x = z.muestra;
      const gr = D1.rejilla(z.rejilla.desde, z.rejilla.hasta, z.rejilla.puntos);
      const norm = (t, mu, s) => Math.exp(-0.5 * ((t - mu) / s) ** 2) / (s * Math.sqrt(2 * Math.PI));
      const verdad = gr.map(t => 0.5 * norm(t, z.medias[0], z.sd[0]) + 0.5 * norm(t, z.medias[1], z.sd[1]));
      let iv = 0; gr.forEach((t, i) => { if (Math.abs(t - z.valle_x) < Math.abs(gr[iv] - z.valle_x)) iv = i; });
      // La lupa: el tramo de 4.5 a 5.5 con una rejilla mucho más fina, donde
      // se ve que la curva de k = 80, lisa a escala completa, sigue dentada.
      const LUPA = [4.5, 5.5], gl = D1.rejilla(LUPA[0], LUPA[1], 2001);
      const verdadL = gl.map(t => 0.5 * norm(t, z.medias[0], z.sd[0]) + 0.5 * norm(t, z.medias[1], z.sd[1]));
      let kk = 10, lupa = 0;
      // Sin `Math.min`: aplanar los picos a 0.5 fabricaba mesetas que no
      // existen; el eje recorta, que es honesto (revisión 2).
      const g = graficoA(raiz, 'line', { datasets: [
        { label: 'k vecinos', data: [], borderColor: CA.verde, borderWidth: 1.5, pointRadius: 0, order: 0 },
        { label: 'verdad', data: curvaA(gr, verdad), borderColor: CA.gris, borderDash: [6, 4], borderWidth: 2,
          pointRadius: 0, order: 1 }
      ] }, { scales: ejesA('x', 'densidad', { x: { type: 'linear', title: { display: true, text: 'x' } },
                                               y: { min: 0, max: 0.5, title: { display: true, text: 'densidad' } } }) });
      const pinta = () => {
        const y = D1.knn(x, gr, kk), yl = D1.knn(x, gl, kk);
        g.data.datasets[0].data = lupa ? curvaA(gl, yl) : curvaA(gr, y);
        g.data.datasets[1].data = lupa ? curvaA(gl, verdadL) : curvaA(gr, verdad);
        g.options.scales.x.min = lupa ? LUPA[0] : undefined;
        g.options.scales.x.max = lupa ? LUPA[1] : undefined;
        g.options.scales.y.max = lupa ? 0.35 : 0.5;
        g.update('none');
        const area = D1.trapecio(gr, y);
        lecturaA(raiz, [['k', kk], ['picos (rejilla del simulador)', D1.modas(y)],
                        ['picos en la lupa', D1.modas(yl)],
                        ['área en el rango de los datos',
                         Number.isFinite(area) ? nA(area, 3) : '∞ (con k = 1 la curva sube sin tope en cada dato)'],
                        ['estimación en el valle', nA(D1.knn(x, [z.valle_x], kk)[0])],
                        ['verdad en el valle', nA(z.f_valle_verdad)]]);
      };
      const K = []; for (let k = 1; k <= 80; k++) K.push([k, String(k)]);
      deslizadorA(raiz, K, 'k', 9, v => { kk = v; pinta(); });
      botoneraA(raiz, ['curva entera', 'lupa: de 4.5 a 5.5'], i => { lupa = i; pinta(); }, 0, 'ver');
      pinta();
      return [g];
    };

    // --- Módulo 8 · la nube de treinta curvas -------------------------
    SIMULADORES['apa-nube'] = function (raiz) {
      const m = DA.m8, gr = D1.rejilla(-4, 4, 161);
      const fi = t => Math.exp(-0.5 * t * t) / Math.sqrt(2 * Math.PI);
      // La verde es E f̂ EXACTO: con núcleo gaussiano y datos N(0, 1), una normal
      // de varianza 1 + h². La primera versión pintaba el promedio de las 30, y
      // su error de Monte Carlo (≈ 0.013 en x = 0) era mayor que el sesgo que
      // quería enseñar: con h = 0.2 quedaba POR ENCIMA de la verdad (revisión 2).
      const esperado = (t, h) => fi(t / Math.sqrt(1 + h * h)) / Math.sqrt(1 + h * h);
      const sets = m.nube.map((s, i) => ({ label: i === 0 ? 'una curva por muestra' : '', data: [],
        borderColor: 'rgba(138,138,138,0.35)', borderWidth: 1, pointRadius: 0, order: 2 }));
      sets.push({ label: 'valor esperado (exacto)', data: [], borderColor: CA.verde, borderWidth: 3,
                  pointRadius: 0, order: 0 });
      sets.push({ label: 'verdad', data: curvaA(gr, gr.map(fi)), borderColor: '#111827', borderDash: [6, 4],
                  borderWidth: 2, pointRadius: 0, order: 1 });
      const g = graficoA(raiz, 'line', { datasets: sets }, {
        plugins: { legend: { labels: { filter: it => it.text !== '' } } },
        scales: ejesA('x', 'densidad', { y: { min: 0, max: 0.8, title: { display: true, text: 'densidad' } } }) });
      const pinta = i => {
        const h = m.h[i], en0 = [];
        m.nube.forEach((s, j) => {
          const y = D1.kde(s, gr, h, 'gaussian');
          en0.push(y[80]);
          g.data.datasets[j].data = curvaA(gr, y);
        });
        g.data.datasets[m.nube.length].data = curvaA(gr, gr.map(t => esperado(t, h)));
        g.update('none');
        const med = en0.reduce((a, b) => a + b, 0) / en0.length;
        lecturaA(raiz, [['ancho h', nA(h, 2)], ['valor esperado en x = 0', nA(esperado(0, h))],
                        ['verdad en x = 0', nA(fi(0))], ['promedio de las 30 en x = 0', nA(med)],
                        ['sesgo² exacto', nA(m.sesgo2[i], 5)], ['varianza exacta', nA(m.var[i], 5)]]);
      };
      const ini = m.h.findIndex(v => Math.abs(v - 0.4) < 1e-9);
      deslizadorA(raiz, m.h.map((v, i) => [i, nA(v, 2)]), 'h', ini, pinta);
      pinta(ini);
      return [g];
    };

    // --- Módulo 8 · el ECM en sus dos partes -------------------------------
    SIMULADORES['apa-ecm'] = function (raiz) {
      const m = DA.m8;
      const g = graficoA(raiz, 'line', { datasets: [
        { label: 'sesgo²', data: curvaA(m.h, m.sesgo2), borderColor: CA.naranja, borderWidth: 2, pointRadius: 0, order: 2 },
        { label: 'varianza', data: curvaA(m.h, m.var), borderColor: CA.azul, borderWidth: 2, pointRadius: 0, order: 2 },
        { label: 'ECM en x = 0', data: curvaA(m.h, m.ecm), borderColor: CA.verde, borderWidth: 3, pointRadius: 0, order: 1 },
        { label: 'MISE de la curva entera', data: curvaA(m.h, m.mise_h), borderColor: CA.gris, borderDash: [6, 4],
          borderWidth: 2, pointRadius: 0, order: 1 },
        { label: 'h marcado', data: [], type: 'scatter', backgroundColor: '#111827', pointRadius: 6, order: 0 }
      ] }, { scales: ejesA('ancho h', 'error', { y: { min: 0, max: 0.02, title: { display: true, text: 'error' } } }) });
      const pinta = i => {
        g.data.datasets[4].data = [{ x: m.h[i], y: m.ecm[i] }];
        g.update('none');
        lecturaA(raiz, [['ancho h', nA(m.h[i], 2)], ['sesgo²', nA(m.sesgo2[i], 5)], ['varianza', nA(m.var[i], 5)],
                        ['ECM', nA(m.ecm[i], 5)], ['MISE', nA(m.mise_h[i], 5)],
                        ['mejor h en x = 0', nA(m.h_ecm, 2)], ['mejor h para la curva', nA(m.h_mise, 4)]]);
      };
      const ini = m.h.findIndex(v => Math.abs(v - m.h_ecm) < 1e-9);
      deslizadorA(raiz, m.h.map((v, i) => [i, nA(v, 2)]), 'h', ini, pinta);
      pinta(ini);
      return [g];
    };

    // --- Módulo 9 · cada selector, su curva --------------------------------
    SIMULADORES['apa-selectores'] = function (raiz) {
      const x = DA.m2.eruptions, s = DA.m10.selectores, f = DA.m9.faithful;
      const gr = D1.rejilla(D1.minimo(x) - 1, D1.maximo(x) + 1, 2048);
      const OPS = [['bw.nrd0', f.nrd0], ['bw.nrd', f.nrd], ['bw.ucv', s.ucv], ['bw.bcv', s.bcv],
                   ['bw.SJ', s.SJ], ['regla del histograma', f.hist_rule]];
      const g = graficoA(raiz, 'line', { datasets: [
        { label: 'estimación gaussiana', data: [], borderColor: CA.verde, borderWidth: 2.5, pointRadius: 0,
          backgroundColor: CA.verdeSuave, fill: 'origin' }
      ] }, { plugins: { legend: { display: false } },
             scales: ejesA('duración de la erupción (minutos)', 'densidad', { y: { min: 0, max: 1,
               title: { display: true, text: 'densidad' } } }) });
      const pinta = i => {
        const y = D1.kde(x, gr, OPS[i][1], 'gaussian');
        g.data.datasets[0].data = curvaA(gr, y);
        g.update('none');
        lecturaA(raiz, [['selector', OPS[i][0]], ['ancho h', nA(OPS[i][1])], ['modas', D1.modas(y)],
                        ['altura máxima', nA(Math.max(...y), 3)]]);
      };
      botoneraA(raiz, OPS.map(o => o[0]), pinta, 0);
      pinta(0);
      return [g];
    };

    // --- Módulo 10 · UCV y LCV ---------------------------------------------
    SIMULADORES['apa-cv'] = function (raiz) {
      // El botón quita la erupción más aislada: la pregunta del módulo es cuál
      // de los dos criterios depende de ella. Con dos ejes que se ajustan solos,
      // la versión anterior preguntaba qué curva era «más plana», y eso el
      // dibujo no lo podía contestar (revisión 2). Los óptimos que se leen son
      // los del JSON, calculados en una rejilla de 0.002.
      const c = DA.m10.curvas, m = DA.m10;
      let i = c.h.findIndex(v => Math.abs(v - 0.1) < 1e-9), sin = 0;
      const arg = (v, mejor) => v.reduce((b, y, k) => (mejor(y, v[b]) ? k : b), 0);
      const g = graficoA(raiz, 'line', { datasets: [
        { label: 'UCV (se minimiza)', data: [], borderColor: CA.azul, borderWidth: 2.5, pointRadius: 0, yAxisID: 'y', order: 1 },
        { label: 'LCV (se maximiza)', data: [], borderColor: CA.naranja, borderWidth: 2.5, pointRadius: 0, yAxisID: 'y2', order: 1 },
        { label: 'mínimo de la UCV', data: [], type: 'scatter', backgroundColor: CA.azul, pointRadius: 6,
          pointStyle: 'rectRot', yAxisID: 'y', order: 0 },
        { label: 'máximo de la LCV', data: [], type: 'scatter', backgroundColor: CA.naranja, pointRadius: 6,
          pointStyle: 'rectRot', yAxisID: 'y2', order: 0 },
        { label: 'h marcado', data: [], type: 'scatter', backgroundColor: '#111827', pointRadius: 5, yAxisID: 'y', order: 0 }
      ] }, { scales: {
          x: { type: 'linear', title: { display: true, text: 'ancho h' } },
          y: { position: 'left', title: { display: true, text: 'UCV' } },
          y2: { position: 'right', title: { display: true, text: 'LCV' }, grid: { drawOnChartArea: false } } } });
      const pinta = () => {
        const u = sin ? c.ucv_sin : c.ucv, l = sin ? c.lcv_sin : c.lcv;
        const iu = arg(u, (a, b) => a < b), il = arg(l, (a, b) => a > b);
        g.data.datasets[0].data = curvaA(c.h, u);
        g.data.datasets[1].data = curvaA(c.h, l);
        g.data.datasets[2].data = [{ x: c.h[iu], y: u[iu] }];
        g.data.datasets[3].data = [{ x: c.h[il], y: l[il] }];
        g.data.datasets[4].data = [{ x: c.h[i], y: u[i] }];
        g.update('none');
        lecturaA(raiz, [['muestra', sin ? 'sin la erupción aislada' : 'las ' + m.n + ' erupciones'],
                        ['ancho h', nA(c.h[i], 2)], ['UCV', nA(u[i], 5)], ['LCV', nA(l[i], 5)],
                        ['modas de la estimación', c.modas[i]],
                        ['mínimo de la UCV en', nA(sin ? m.h_ucv_sin : m.h_ucv_mano, 3)],
                        ['máximo de la LCV en', nA(sin ? m.h_lcv_sin : m.h_lcv_mano, 3)]]);
      };
      deslizadorA(raiz, c.h.map((v, k) => [k, nA(v, 2)]), 'h', i, k => { i = k; pinta(); });
      botoneraA(raiz, ['todas las erupciones', 'sin la erupción de ' + nA(m.aislada[0].x, 3)],
                k => { sin = k; pinta(); }, 0, 'muestra');
      pinta();
      return [g];
    };

    // --- Módulo 11 · mil muestras ------------------------------------------
    SIMULADORES['apa-mc'] = function (raiz) {
      const ise = DA.m11.ise, SEL = ['ucv', 'bcv', 'nrd0'];
      // Máximos redondos: con el máximo de los datos, el último rótulo quedaba
      // en 0.029 y en el teléfono se saltaba el 0.02 (revisión 2).
      const redondoA = v => Math.ceil(v * 100) / 100;
      const max = redondoA(Math.max(...ise.SJ));
      const g = graficoA(raiz, 'scatter', { datasets: [
        { label: 'una muestra', data: [], backgroundColor: 'rgba(26,115,88,0.45)', pointRadius: 2.5 },
        { label: 'empate (y = x)', data: [{ x: 0, y: 0 }, { x: max, y: max }], type: 'line',
          borderColor: CA.gris, borderWidth: 1.5, pointRadius: 0 },
        { label: 'el doble de SJ (y = 2x)', data: [{ x: 0, y: 0 }, { x: max, y: 2 * max }], type: 'line',
          borderColor: CA.rojo, borderDash: [6, 4], borderWidth: 1.5, pointRadius: 0 }
      ] }, { scales: { x: { type: 'linear', min: 0, max: max, title: { display: true, text: 'ISE de bw.SJ' } },
                       y: { type: 'linear', min: 0, title: { display: true, text: 'ISE del selector' } } } });
      const pinta = i => {
        const s = SEL[i], y = ise[s];
        g.data.datasets[0].data = ise.SJ.map((v, j) => ({ x: v, y: y[j] }));
        g.options.scales.y.max = s === 'nrd0' ? redondoA(Math.max(...y)) : redondoA(2.5 * max);
        g.update('none');
        let gana = 0, cola = 0;
        y.forEach((v, j) => { if (v < ise.SJ[j]) gana++; if (v > 2 * ise.SJ[j]) cola++; });
        const fila = DA.m11.por_selector.find(r => r.selector === s);
        lecturaA(raiz, [['selector', 'bw.' + s], ['muestras en que gana a SJ', nA(100 * gana / y.length, 1) + ' %'],
                        ['muestras en que pierde por más del doble', nA(100 * cola / y.length, 1) + ' %'],
                        ['su ISE medio', nA(fila.mise, 5)], ['el de SJ', nA(DA.m11.por_selector.find(r => r.selector === 'SJ').mise, 5)]]);
      };
      botoneraA(raiz, SEL.map(s => 'bw.' + s), pinta, 0);
      pinta(0);
      return [g];
    };

    // --- Módulo 12 · el borde en r = 0 -------------------------------------
    SIMULADORES['apa-borde'] = function (raiz) {
      // El tramo de 0 a 200 m va primero: en el teléfono, con el eje hasta
      // 600 m, el borde —el tema del simulador— cabía en 12 píxeles.
      const c = DA.m12.curvas, b = DA.m12.borde;
      const enc = [true, false, false, false, true];
      let cerca = 1;
      const g = graficoA(raiz, 'line', { datasets: [
        { label: 'sin corregir', data: curvaA(c.r, c.sin), borderColor: CA.gris, borderWidth: 2, pointRadius: 0, order: 2 },
        { label: 'reflejada', data: curvaA(c.r, c.reflejada), borderColor: CA.verde, borderWidth: 2.5, pointRadius: 0, order: 1 },
        { label: 'dividida por e(r)', data: curvaA(c.r, c.e), borderColor: CA.morado, borderWidth: 2, pointRadius: 0, order: 1 },
        { label: 'Diggle', data: curvaA(c.r, c.diggle), borderColor: CA.azul, borderWidth: 2, pointRadius: 0, order: 1 },
        { label: 'si las sedes estuvieran al azar', data: curvaA(c.r, c.csr), borderColor: '#111827',
          borderDash: [6, 4], borderWidth: 1.5, pointRadius: 0, order: 3 }
      ] }, { scales: ejesA('distancia a la sede más cercana (m)', 'densidad (por metro)',
                            { x: { type: 'linear', min: 0, title: { display: true, text: 'distancia a la sede más cercana (m)' } } }) });
      const pinta = () => {
        g.data.datasets.forEach((d, i) => { d.hidden = !enc[i]; });
        g.options.scales.x.max = cerca ? 200 : DA.m12.curvas_hasta;
        g.update('none');
        lecturaA(raiz, [['ancho h', nA(b.h, 2) + ' m'], ['en r = 0 sin corregir', nA(b.f0_sin, 5)],
                        ['de ello, los ceros', nA(b.f0_ceros, 5)],
                        ['reflejada', nA(b.f0_reflejada, 5)], ['dividida por e(r)', nA(b.f0_e, 5)],
                        ['Diggle', nA(b.f0_diggle, 5)],
                        ['área sin corregir', nA(b.masa_sin)], ['área reflejada', nA(b.masa_reflejada)],
                        ['área con e(r)', nA(b.masa_e)],
                        ['área con Diggle', nA(b.masa_diggle)]]);
      };
      interruptoresA(raiz, ['sin corregir', 'reflejada', 'dividida por e(r)', 'Diggle', 'al azar'], enc, pinta, 'curvas');
      botoneraA(raiz, ['de 0 a 200 m', 'hasta ' + DA.m12.curvas_hasta + ' m'], k => { cerca = 1 - k; pinta(); }, 0, 'tramo');
      pinta();
      return [g];
    };

    // --- Módulo 12 · dos anchos para las mismas distancias ----------------
    SIMULADORES['apa-empates'] = function (raiz) {
      const nn = DA.m12.nn, s = DA.m12.selectores, hasta = DA.m12.curvas_hasta;
      const gr = D1.rejilla(0, hasta, hasta + 1);
      const OPS = [['bw.ucv con todas las distancias', s.todas.ucv],
                   ['bw.ucv sin parejas ni ceros', s.una_por_pareja_sin_ceros.ucv]];
      // Eje vertical FIJO para los dos anchos (antes saltaba de 0.006 a 0.0045
      // y alturas distintas parecían iguales), y picos con prominencia: con
      // 20.42 m la lectura contaba como pico una ondulación de 7e-5 a 597 m
      // que el ojo no ve (revisión 2).
      const Y = OPS.map(o => D1.kde(nn, gr, o[1], 'gaussian'));
      const tope = Math.ceil(Math.max(...Y.map(y => Math.max(...y))) * 1e4) / 1e4;
      const picosVisibles = (y, frac) => {
        const umbral = frac * Math.max(...y), mx = [], mn = [];
        for (let k = 1; k < y.length - 1; k++) {
          if (y[k] > y[k - 1] && y[k] >= y[k + 1]) mx.push(k);
          if (y[k] < y[k - 1] && y[k] <= y[k + 1]) mn.push(k);
        }
        return mx.filter(k => {
          const izq = mn.filter(j => j < k), der = mn.filter(j => j > k);
          const vi = izq.length ? y[izq[izq.length - 1]] : 0, vd = der.length ? y[der[0]] : 0;
          return y[k] - Math.max(vi, vd) > umbral;
        }).length + (y[0] > y[1] && y[0] - (mn.length ? y[mn[0]] : 0) > umbral ? 1 : 0);
      };
      const g = graficoA(raiz, 'line', { datasets: [
        { label: 'estimación', data: [], borderColor: CA.verde, borderWidth: 1.5, pointRadius: 0 }
      ] }, { plugins: { legend: { display: false } },
             scales: ejesA('distancia a la sede más cercana (m)', 'densidad (por metro)',
                           { y: { min: 0, max: tope, title: { display: true, text: 'densidad (por metro)' } } }) });
      const pinta = i => {
        g.data.datasets[0].data = curvaA(gr, Y[i]);
        g.update('none');
        lecturaA(raiz, [['ancho', nA(OPS[i][1], 2) + ' m'], ['picos visibles entre 0 y ' + hasta + ' m', picosVisibles(Y[i], 0.05)]]);
      };
      botoneraA(raiz, OPS.map(o => o[0]), pinta, 0);
      pinta(0);
      return [g];
    };
"""


# =====================================================================
# LA AUTOEVALUACIÓN: diecisiete preguntas, al menos una por módulo. Cinco del documento original
# (adaptadas) y siete de interpretación. Cada opción trae su `retro`, la
# clave que el motor lee; las cifras salen de `DA`.
# =====================================================================
QUIZ_JS = r"""
    // Cada pregunta declara `modulo`: el resumen final manda a repasar ese
    // módulo. La primera versión no lo declaraba, y quien fallaba recibía un
    // «revisa la retroalimentación» sin enlace (revisión 2). Las opciones
    // tienen longitudes parejas: en seis de ocho preguntas la correcta era la
    // más larga, y elegir siempre la más larga acertaba casi todo.
    const NUC_A = nombre => DA.m6.nucleos.find(k => k.nombre === nombre);
    const MC_A = s => DA.m11.por_selector.find(r => r.selector === s);
    AUTOEVALUACIONES['apa-quiz'] = [
      {
        tipo: 'numerica', modulo: 1,
        pista: 'La altura cambia con la unidad del eje; el área de la barra, no.',
        pregunta: 'Con el eje en horas, la barra del histograma de la cafetería que va de ' + DA.m1.barra_max.desde + ' a ' + DA.m1.barra_max.hasta + ' minutos mide ' + nA(DA.m1.barra_max.densidad_por_hora, 1) + ' por hora. ¿Qué fracción de los clientes esperó entre ' + DA.m1.barra_max.desde + ' y ' + DA.m1.barra_max.hasta + ' minutos? Responde con una proporción entre 0 y 1.',
        respuesta: DA.m1.barra_max.densidad, tolerancia: 0.005,
        retroAcierto: 'Eso es: el área no depende de la unidad. ' + nA(DA.m1.barra_max.densidad_por_hora, 1) + ' por hora durante un minuto, que es 1/' + DA.m1.minutos_por_hora + ' de hora, da ' + nA(DA.m1.barra_max.densidad, 2) + ': ' + DA.m1.barra_max.conteo + ' de los ' + DA.m1.n + ' clientes.',
        retroFallo: 'La fracción es el área de la barra, no su altura: ' + nA(DA.m1.barra_max.densidad_por_hora, 1) + ' por hora por un ancho de 1/' + DA.m1.minutos_por_hora + ' de hora da ' + nA(DA.m1.barra_max.densidad, 2) + '. Cambiar de minutos a horas multiplica la altura y estrecha la barra en la misma proporción.'
      },
      {
        tipo: 'opcion', modulo: 2,
        pista: 'Piensa en qué cambió y qué no: los datos y el ancho son los mismos.',
        pregunta: 'Con el mismo ancho de ' + nA(DA.m2.h_origen, 2) + ' minutos, correr el origen de los intervalos hace que el histograma de las erupciones pase de ' + DA.m2.origen.modas_muchas + ' a ' + DA.m2.origen.modas_pocas + ' modas. ¿Qué efecto del MAUP es ese?',
        opciones: [
          { texto: 'El de zonificación: intervalos del mismo tamaño, otra partición', correcta: true,
            retro: 'Exacto. Mover el origen sin tocar el ancho es repartir el eje de otra manera, como redibujar los límites de las zonas sin cambiar su tamaño.' },
          { texto: 'El de escala: los intervalos cambiaron de tamaño al moverse', correcta: false,
            retro: 'El tamaño no cambió: el ancho sigue siendo ' + nA(DA.m2.h_origen, 2) + ' minutos. La escala es la otra perilla, el ancho.' },
          { texto: 'Ninguno: es la variabilidad de una muestra a otra', correcta: false,
            retro: 'No hay otra muestra: son las mismas ' + DA.m2.n + ' erupciones. Lo único que cambió es dónde caen los cortes.' },
          { texto: 'Un error de redondeo de la máquina en los cortes', correcta: false,
            retro: 'El redondeo sí puede cambiar en qué barra cae un dato que está justo en un corte, y por eso R los corre una fracción minúscula antes de contar. Pero aquí ya está corregido: lo que mueve las modas es que los cortes caen en otro sitio.' }
        ] },
      {
        tipo: 'opcion', modulo: 3,
        pista: 'Piensa en qué probabilidad tienen dos puntos de caer en la misma casilla cuando el origen se mueve al azar.',
        pregunta: 'Con el ancho h fijo y cada vez más histogramas desplazados promediados (m creciente), ¿a qué se acerca el ASH?',
        opciones: [
          { texto: 'Al estimador de núcleo triangular de semiancho h', correcta: true,
            retro: 'Eso es: promediado sobre todos los orígenes, un dato aporta en x la probabilidad de caer en la misma casilla que x, que baja en línea recta con la distancia. Sobre las erupciones la distancia al triangular baja como 1/m.' },
          { texto: 'A un histograma con barras de ancho h dividido por m', correcta: false,
            retro: 'h/m es el paso entre un origen y el siguiente, no el ancho de las barras: todas miden h. Por eso subir m no afina nada; solo quita la dependencia del origen.' },
          { texto: 'A la densidad verdadera, si m es bastante grande', correcta: false,
            retro: 'Con h fijo el ASH conserva el sesgo de suavizar a la escala h: se acerca a una curva concreta que depende de h, no a la verdad. Para acercarse a la verdad hacen falta más datos y un h más pequeño.' },
          { texto: 'Al estimador de núcleo gaussiano de desviación h', correcta: false,
            retro: 'La forma límite sale de contar en cuántos histogramas caen juntos dos puntos, y esa fracción baja en línea recta con la distancia: un triángulo, no una campana.' }
        ] },
      {
        tipo: 'opcion', modulo: 4,
        pista: 'Escribe la media y la varianza de k/n del módulo 4 y mira en cuál de las dos aparece n.',
        pregunta: 'En el estimador ingenuo del módulo 4, con la ventana fija en V = ' + nA(DA.m4.v_peq.V, 1) + ', la muestra pasa de ' + DA.m4.ns[1] + ' a ' + DA.m4.ns[2] + ' datos. ¿Qué les pasa a la banda de dos desviaciones típicas y a la línea del valor esperado?',
        opciones: [
          { texto: 'La banda se estrecha a la mitad y la línea no se mueve', correcta: true,
            retro: 'Eso es. La desviación típica va como 1/√n: cuatro veces más datos la dividen por dos. Y el valor esperado, P/V, depende de la ventana, no de n: el sesgo es el mismo.' },
          { texto: 'La banda se estrecha a la cuarta parte y la línea no se mueve', correcta: false,
            retro: 'Lo que se divide por cuatro es la varianza. La banda mide desviaciones típicas, que van como 1/√n: se divide por dos.' },
          { texto: 'La banda se estrecha y la línea se acerca a la verdad', correcta: false,
            retro: 'Con la misma ventana el valor esperado es el mismo con cualquier n: el sesgo no viene del azar sino de la ventana. Para acercar la línea hay que achicar V.' },
          { texto: 'La banda no cambia, porque la ventana es la misma', correcta: false,
            retro: 'La ventana es la misma, pero ahora caen en ella cuatro veces más datos en promedio, y su proporción fluctúa menos: la banda se estrecha a la mitad.' }
        ] },
      {
        tipo: 'opcion', modulo: 5,
        pista: 'Piensa en qué mide h y en si los datos solos deciden a qué escala mirarlos.',
        pregunta: 'Con los cinco datos {' + DA.m5.gaussiano.datos.join(', ') + '} y núcleo gaussiano, al subir h de ' + nA(DA.m5.tramos[0].desde, 2) + ' a ' + nA(DA.m5.tramos[DA.m5.tramos.length - 1].hasta, 2) + ' el número de modas pasa por ' + DA.m5.tramos.map(t => t.modas).join(', ') + '. ¿Qué se concluye sobre el número de modas de los datos?',
        opciones: [
          { texto: 'Que no tiene un valor propio: depende de la escala h', correcta: true,
            retro: 'Eso es. Cada cuenta es el número de modas a una escala. Elegir la escala es elegir h, y para eso hace falta un criterio: el de los módulos 9 a 11.' },
          { texto: 'Que son cinco, lo que se ve con el h más pequeño', correcta: false,
            retro: 'Con h pequeño cada dato levanta su propia loma: eso cuenta datos, no grupos.' },
          { texto: 'Que es una, el valor que más se repite al mover h', correcta: false,
            retro: 'Que una cuenta dure más en el deslizador no la hace verdadera: con h grande todo se funde, y el recorrido de h lo eligió quien hizo el simulador.' },
          { texto: 'Que son dos, porque el 7 está lejos de los demás', correcta: false,
            retro: 'Puede ser, pero con cinco datos no hay manera de saber si el 7 es un grupo aparte o un dato suelto del mismo grupo: es una lectura a una escala, no un hecho de los datos.' }
        ] },
      {
        tipo: 'opcion', modulo: 5,
        pista: 'Repasa las tres propiedades que el módulo 5 le pide a un núcleo, y piensa en el gaussiano.',
        pregunta: '¿Cuál de estas afirmaciones sobre un núcleo univariado de los que usa el apéndice es verdadera?',
        opciones: [
          { texto: 'Es una función par: K(u) = K(−u)', correcta: true,
            retro: 'Sí. Los núcleos habituales son simétricos, no negativos e integran 1, y por eso la estimación no se inclina hacia ningún lado del dato.' },
          { texto: 'Se anula fuera del intervalo [−1, 1]', correcta: false,
            retro: 'Los de soporte acotado sí, pero el gaussiano no se anula nunca, y es un núcleo.' },
          { texto: 'En el centro, u = 0, vale exactamente 1', correcta: false,
            retro: 'El Epanechnikov vale 3/4 en el centro y el gaussiano ' + nA(DA.m4.f0, 4) + ': lo que fija la definición es el área, no la altura.' },
          { texto: 'Su integral sobre la recta vale 1/h', correcta: false,
            retro: 'Integra 1. Lo que lleva el 1/h es el núcleo estirado, K<sub>h</sub>(u) = K(u/h)/h, y también integra 1.' }
        ] },
      {
        tipo: 'opcion', modulo: 6,
        pista: 'La eficiencia compara cada núcleo con el Epanechnikov, cada uno con su mejor ancho.',
        pregunta: 'La caja tiene una eficiencia de ' + nA(NUC_A('uniforme').eficiencia) + ' respecto del Epanechnikov. ¿Qué quiere decir?',
        opciones: [
          { texto: 'Que necesita ' + nA(NUC_A('uniforme').datos_para_igualar, 3) + ' veces más datos para el mismo error', correcta: true,
            retro: 'Eso es: la eficiencia es un cociente de tamaños de muestra. Con los mismos datos, su error es ' + nA(NUC_A('uniforme').error_relativo, 3) + ' veces el del Epanechnikov.' },
          { texto: 'Que su curva difiere de la del Epanechnikov en esa proporción', correcta: false,
            retro: 'La eficiencia no compara curvas sino errores, con el mejor ancho para cada núcleo. Con la misma desviación típica las curvas casi coinciden (módulo 6).' },
          { texto: 'Que con el mismo h su error es mayor en esa proporción', correcta: false,
            retro: 'Cada núcleo se compara con su propio mejor ancho, no con el mismo h. Y la eficiencia es una proporción de datos: con los mismos datos, el error de la caja es ' + nA(NUC_A('uniforme').error_relativo, 3) + ' veces el del Epanechnikov.' },
          { texto: 'Que acierta en esa fracción de las muestras simuladas', correcta: false,
            retro: 'No es una frecuencia de aciertos: es un cociente de tamaños de muestra con el mismo error asintótico. Las frecuencias de acierto son las del módulo 11.' }
        ] },
      {
        tipo: 'numerica', modulo: 6,
        pista: '¿Qué desviación típica tiene una caja que va de −a a a? En density(), bw es esa desviación.',
        pregunta: 'Con <code>density(x, bw = ' + DA.m6.pregunta_caja.bw + ', kernel = "rectangular")</code>, ¿hasta qué distancia de cada dato llega la caja?',
        respuesta: DA.m6.pregunta_caja.semiancho, tolerancia: 0.01,
        retroAcierto: 'Eso es: una caja de semiancho a tiene desviación típica a/√3, así que llega a √3 × ' + DA.m6.pregunta_caja.bw + ' = ' + nA(DA.m6.pregunta_caja.semiancho, 3) + '. En R el ancho no es el radio del soporte.',
        retroFallo: 'R mide el ancho como desviación típica: la caja llega a √3 × ' + DA.m6.pregunta_caja.bw + ' = ' + nA(DA.m6.pregunta_caja.semiancho, 3) + ', no a ' + DA.m6.pregunta_caja.bw + '.'
      },
      {
        tipo: 'opcion', modulo: 7,
        pista: 'Piensa en cómo decae la curva del k-NN lejos de los datos.',
        pregunta: 'Con k = ' + DA.m7.ingresos.k + ' y ' + DA.m7.ingresos.n + ' ingresos, el área bajo la curva del k-NN vale ' + nA(DA.m7.ingresos.areas[0].area) + ' entre ' + DA.m7.ingresos.areas[0].desde + ' y ' + DA.m7.ingresos.areas[0].hasta + ', ' + nA(DA.m7.ingresos.areas[1].area) + ' entre ' + DA.m7.ingresos.areas[1].desde + ' y ' + DA.m7.ingresos.areas[1].hasta + ' y ' + nA(DA.m7.ingresos.areas[2].area) + ' entre ' + DA.m7.ingresos.areas[2].desde + ' y ' + DA.m7.ingresos.areas[2].hasta + '. ¿Qué se concluye?',
        opciones: [
          { texto: 'Que no es una densidad: sus colas decaen como 1/|x|', correcta: true,
            retro: 'Eso es: una cola en 1/|x| tiene integral infinita, y el área crece sin tope al abrir el intervalo. El k-NN sirve para leer la concentración local de los datos, no para calcular probabilidades con su área.' },
          { texto: 'Que hay que dividirla por el área en el rango de los datos', correcta: false,
            retro: 'Dividir por un área que depende de dónde se corta no arregla nada: con otro intervalo el divisor sería otro.' },
          { texto: 'Que k es demasiado pequeño para veinte datos', correcta: false,
            retro: 'Con k más grande el área en el rango baja, pero las colas siguen decayendo como 1/|x| y la integral sigue sin converger.' },
          { texto: 'Que la integración por trapecios falla lejos de los datos', correcta: false,
            retro: 'La integral por trapecios es correcta: crece porque la curva no baja lo bastante deprisa lejos de los datos.' }
        ] },
      {
        tipo: 'numerica', modulo: 8,
        pista: '¿Con qué potencia de n decae el error integrado del núcleo? Despeja por cuánto hay que multiplicar n para que ese error se divida por 2.',
        pregunta: 'Para bajar a la mitad el error integrado del estimador de núcleo en la recta, con su mejor ancho, ¿cuántas veces más datos hacen falta?',
        respuesta: DA.m8.tasas.kde_datos_para_mitad, tolerancia: 0.03,
        retroAcierto: 'Eso es: el error decae como n elevado a −4/5, así que hace falta 2 elevado a 5/4 = ' + nA(DA.m8.tasas.kde_datos_para_mitad, 2) + ' veces más datos.',
        retroFallo: 'El error del núcleo decae como n elevado a −4/5: hacen falta ' + nA(DA.m8.tasas.kde_datos_para_mitad, 2) + ' veces más datos. ' + nA(DA.m8.tasas.hist_datos_para_mitad, 2) + ' es lo que pide el histograma en la recta, o el núcleo en el plano.'
      },
      {
        tipo: 'opcion', modulo: 9,
        pista: 'density() tiene un ancho por defecto; mira en el módulo 9 qué constante usa cada función de R.',
        pregunta: 'Para las erupciones, n = ' + DA.m9.faithful.n + ', s = ' + nA(DA.m9.faithful.sd) + ' e IQR = ' + nA(DA.m9.faithful.iqr) + '. ¿Qué ancho usa <code>density(faithful$eruptions)</code> si no se le da <code>bw</code>?',
        opciones: [
          { texto: nA(DA.m9.faithful.nrd0), correcta: true,
            retro: 'Eso es: <code>bw.nrd0</code>, 0.9 por el mínimo de s e IQR/1.34 —aquí manda s— por n<sup>−1/5</sup>. Es el que density() usa si no se le pide otro.' },
          { texto: nA(DA.m9.faithful.nrd), correcta: false,
            retro: 'Ese es <code>bw.nrd</code>, con la constante 1.06, la que R atribuye a Scott. density() no lo usa salvo que se le pida.' },
          { texto: nA(DA.m9.faithful.hist_rule), correcta: false,
            retro: 'Esa es la regla de Scott para el ancho de las barras de un histograma, 3.5 · s · n<sup>−1/3</sup>. Aplicada al núcleo sobresuaviza.' },
          { texto: nA(DA.m9.faithful.nrd0_con_iqr), correcta: false,
            retro: 'Sale de tomar la escala mayor, IQR/1.34, en vez del mínimo de las dos. La regla usa el mínimo para que una cola larga no infle el ancho.' }
        ] },
      {
        tipo: 'opcion', modulo: 9,
        pista: 'Para una normal, IQR/1.34 y s estiman lo mismo. ¿Qué pasa si hay colas largas?',
        pregunta: '¿Por qué la regla de referencia usa min(s, IQR/1.34) y no solo la desviación típica s?',
        opciones: [
          { texto: 'IQR/1.34 también estima σ<sub>f</sub> y no lo arrastran los extremos', correcta: true,
            retro: 'Eso es. En las distancias al vecino de las sedes, s = ' + nA(DA.m9.distancias.sd, 2) + ' m e IQR/1.34 = ' + nA(DA.m9.distancias.iqr_134, 2) + ' m: unas pocas sedes aisladas inflan la desviación.' },
          { texto: 'La desviación típica muestral no es un estimador consistente', correcta: false,
            retro: 'Sí lo es. El problema no es la consistencia sino la sensibilidad a unos pocos valores extremos.' },
          { texto: 'El rango intercuartílico siempre es menor que s', correcta: false,
            retro: 'No: en una normal el IQR vale ' + nA(DA.m9.constantes.iqr_normal, 2) + ' desviaciones, más que una. En las erupciones IQR = ' + nA(DA.m9.faithful.iqr, 2) + ' y s = ' + nA(DA.m9.faithful.sd, 2) + '. Por eso se divide por 1.34 antes de comparar.' },
          { texto: 'Para que el ancho no dependa del tamaño de la muestra', correcta: false,
            retro: 'El ancho depende de n por el factor n<sup>−1/5</sup>, que no cambia. El mínimo solo elige la escala.' }
        ] },
      {
        tipo: 'opcion', modulo: 9,
        pista: '¿De qué depende el exponente de n en el error del módulo 4? ¿Cuántas coordenadas tiene una sede?',
        pregunta: '<code>bw.scott</code> de spatstat multiplica la desviación típica de cada coordenada por n<sup>−1/6</sup>. ¿Por qué −1/6 y no −1/5?',
        opciones: [
          { texto: 'Porque el plano tiene d = 2 y la tasa es n<sup>−1/(d+4)</sup>', correcta: true,
            retro: 'Eso es. En la recta, d = 1 da −1/5; en el plano, −1/6, y además el factor (4/(d+2))<sup>1/(d+4)</sup> vale exactamente 1.' },
          { texto: 'Porque spatstat usa la regla del histograma', correcta: false,
            retro: 'La del histograma tiene n<sup>−1/3</sup>. −1/6 sale de la misma cuenta del núcleo, en dos dimensiones.' },
          { texto: 'Porque las sedes no son datos independientes', correcta: false,
            retro: 'La regla de referencia no corrige por dependencia: supone una normal y datos independientes en cualquier dimensión.' },
          { texto: 'Para suavizar a propósito más que en la recta', correcta: false,
            retro: 'Que n<sup>−1/6</sup> decrezca más despacio es consecuencia de la dimensión, no una decisión de suavizar más.' }
        ] },
      {
        tipo: 'opcion', modulo: 10,
        pista: 'Piensa en dónde busca R el mínimo y qué devuelve cuando no lo encuentra dentro.',
        pregunta: '<code>bw.ucv(x)</code> devuelve un número y avisa «minimum occurred at one end of the range». ¿Qué quiere decir?',
        opciones: [
          { texto: 'Que el número está junto al borde de la búsqueda, no en un mínimo', correcta: true,
            retro: 'Eso es. Con las distancias de las sedes devuelve ' + nA(DA.m12.selectores.todas.ucv, 2) + ' m, a una tolerancia del extremo inferior, ' + nA(DA.m12.selectores.todas.busqueda_desde, 2) + ' m, porque el criterio sigue bajando al achicar h. Y sin aviso tampoco hay garantía: es el ejercicio 10.' },
          { texto: 'Que el mínimo cayó en el dato más pequeño o en el más grande', correcta: false,
            retro: 'El «range» del aviso es el intervalo de anchos h en que busca R, no el rango de los datos.' },
          { texto: 'Que el ancho elegido es el menor posible y por eso el mejor', correcta: false,
            retro: 'El extremo no es un óptimo: es donde la búsqueda se paró. Publicarlo como «el ancho óptimo» sería falso.' },
          { texto: 'Que algunos de los datos tienen valores negativos', correcta: false,
            retro: 'El aviso no habla de los datos sino del criterio: su mínimo cayó en el borde del intervalo de búsqueda.' }
        ] },
      {
        tipo: 'opcion', modulo: 11,
        pista: 'Compara cuántas veces gana con cuánto pierde cuando pierde.',
        pregunta: 'En el Monte Carlo del módulo 11, la UCV es el selector que más veces da el menor error (' + nA(MC_A('ucv').gana_pct, 1) + ' % de las muestras), pero su error medio queda ' + nA(DA.m11.emparejadas.ucv_sj.pct, 1) + ' % por encima del de SJ. ¿Cómo se concilian las dos cosas?',
        opciones: [
          { texto: 'Es de alta varianza: a menudo la mejor y a veces muy mala', correcta: true,
            retro: 'Eso es. En el ' + nA(MC_A('ucv').cola_pct, 1) + ' % de las muestras su error pasa del doble del de SJ, y esas muestras pesan en el promedio. Sus anchos tienen una desviación de ' + nA(MC_A('ucv').h_sd, 4) + ', contra ' + nA(MC_A('SJ').h_sd, 4) + ' de SJ.' },
          { texto: 'Es un error del Monte Carlo que más réplicas borrarían', correcta: false,
            retro: 'Con mil réplicas el error estándar de la diferencia media es pequeño (t = ' + nA(DA.m11.emparejadas.ucv_sj.t, 1) + '): la diferencia es real.' },
          { texto: 'La UCV es mejor y el error medio no importa', correcta: false,
            retro: 'Si se necesita un ancho en el que confiar, perder a veces por mucho importa más que ganar a menudo por poco. Y cara a cara, frente a SJ sola, la UCV gana solo en el ' + nA(DA.m11.cara_ucv_sj, 1) + ' % de las muestras.' },
          { texto: 'SJ hace trampa porque conoce la densidad verdadera', correcta: false,
            retro: 'Ninguno conoce la verdad: todos ven la misma muestra. La verdad solo la usa el experimento para medir el error.' }
        ] },
      {
        tipo: 'multiple', modulo: 12,
        pista: 'Busca lo que hace que una misma cifra entre más de una vez en la lista.',
        pregunta: 'Marca <strong>todo</strong> lo que hace que las distancias de cada sede a la más cercana no sean datos independientes.',
        retroAcierto: 'Las dos: las parejas recíprocas repiten la misma cifra y las sedes que comparten dirección dan ceros que empatan entre sí.',
        retroFallo: 'Las dos ciertas son las parejas recíprocas y los ceros de las sedes que comparten dirección.',
        opciones: [
          { texto: 'Si la vecina más cercana de A es B y la de B es A, esa distancia aparece dos veces', correcta: true,
            retro: 'Sí: pasa con el ' + nA(DA.m12.recipro.pct, 1) + ' % de las sedes, y en un patrón al azar con el ' + nA(DA.m12.recipro.csr_pct, 1) + ' %.' },
          { texto: 'Dos sedes en la misma dirección se tienen una a otra a distancia cero', correcta: true,
            retro: 'Sí: cada una mide el mismo cero que la otra, así que los ' + DA.m12.ceros + ' ceros entran por grupos y no uno a uno, y todos empatan entre sí. Que valgan cero es además un átomo en r = 0, otro supuesto roto.' },
          { texto: 'Junto al perímetro urbano, la vecina de verdad puede quedar fuera de la ventana', correcta: false,
            retro: 'Eso es un sesgo de borde, el de la ventana, no una dependencia entre las distancias: las hace más largas de la cuenta, no repetidas.' },
          { texto: 'Las distancias al vecino no siguen una distribución normal', correcta: false,
            retro: 'No ser normal no es depender. Los estimadores de los módulos 5 a 11 no suponen que los datos sean normales.' }
        ] },
      {
        tipo: 'grafico', modulo: 12, alto: 220,
        descripcionGrafico: 'La densidad estimada sin corregir de las distancias de cada sede a la más cercana, de 0 a 200 metros: en r = 0 no vale cero, sube sin bajar hasta su máximo hacia los 120 metros y después desciende.',
        pregunta: 'La curva es la estimación de núcleo, sin corregir el borde, de las ' + DA.m12.n + ' distancias de cada sede de Bogotá a la más cercana. En r = 0 vale ' + nA(DA.m12.borde.f0_sin, 5) + ' por metro. ¿Qué pone más de la mitad de esa altura?',
        pista: 'Mira el módulo 12: ¿cuántas distancias valen exactamente cero, y qué aporta cada una en r = 0?',
        dibujar: canvas => {
          const c = DA.m12.curvas, hasta = 200;
          const puntos = c.r.map((r, i) => ({ x: r, y: c.sin[i] })).filter(p => p.x <= hasta);
          return new Chart(canvas.getContext('2d'), {
            type: 'line',
            data: { datasets: [{ label: 'sin corregir', data: puntos, borderColor: '#8a8a8a', borderWidth: 2, pointRadius: 0 }] },
            options: { responsive: true, maintainAspectRatio: false, animation: false, parsing: false,
                       plugins: { legend: { display: false } },
                       scales: { x: { type: 'linear', min: 0, max: hasta, title: { display: true, text: 'distancia (m)' } },
                                 y: { min: 0, title: { display: true, text: 'densidad (por metro)' } } } }
          });
        },
        opciones: [
          { texto: 'Las ' + DA.m12.ceros + ' sedes que comparten dirección: un átomo en cero', correcta: true,
            retro: 'Eso es: aportan ' + nA(DA.m12.borde.f0_ceros, 5) + ' de los ' + nA(DA.m12.borde.f0_sin, 5) + '. Son una masa concentrada en un punto —el salto de G en r = 0 del capítulo 4—, no densidad.' },
          { texto: 'La masa que el núcleo pierde por el lado negativo del cero', correcta: false,
            retro: 'La masa que se va a r &lt; 0 baja la curva en el borde, no la sube; reflejar la devuelve.' },
          { texto: 'Las sedes junto al perímetro, cuya vecina queda fuera', correcta: false,
            retro: 'Ese borde, el de la ventana, alarga las distancias, no las acorta: pone masa lejos del cero, no en él.' },
          { texto: 'Que las sedes se atraen a distancias muy cortas', correcta: false,
            retro: 'Clark-Evans dice que están más cerca que bajo CSR, pero no por qué: una intensidad que cambia por la ciudad deja la misma huella. Y lo que sube la curva en r = 0 son direcciones repetidas, distancias exactamente cero.' }
        ] }
    ];
"""


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


MODULOS_OBJETIVO = 13
N_SIMULADORES = 14


def main() -> int:
    doc = PLANTILLA.read_text(encoding="utf-8")
    print(f"\n=== ensambla_apendicea.py ===\nplantilla: {len(doc)/1024:.0f} KB\n")

    motor = MOTOR.read_text(encoding="utf-8")
    if "</script" in motor.lower():
        sys.exit("PARADO: el motor densidad1d.js contiene «</script» y rompería el documento")

    doc = sustituye(doc, "<title>Plantilla de capítulo — Estadística Espacial</title>",
                    "<title>Apéndice A · La densidad en una dimensión — Estadística Espacial</title>",
                    "título")
    doc = sustituye(doc, "PLANTILLA BASE •\n              5 MÓDULOS DE DEMOSTRACIÓN • UNBOSQUE 2026-II",
                    "APÉNDICE A • LA DENSIDAD EN UNA DIMENSIÓN •\n"
                    "              EL REPASO DEL CAPÍTULO 5 • UNBOSQUE 2026-II",
                    "subtítulo de la cabecera")
    doc = sustituye(doc, "Estadística Espacial (20929) • Plantilla de\n          capítulo • UnBosque 2026-II",
                    "Estadística Espacial (20929) • Apéndice A •\n"
                    "          La densidad en una dimensión • UnBosque 2026-II", "pie")

    doc = reemplaza_region(doc, "    const courseData = {", "\n    };\n", COURSE_DATA,
                           "courseData + DATOS_APA", max_lineas=20)

    doc = reemplaza_region(
        doc,
        "  <!-- ============================================================ -->\n"
        "  <!-- MÓDULO 1 · Cajas y tipografía",
        "\n  <script>", MODULOS.lstrip("\n") + "\n  <script>",
        "los módulos escritos", max_lineas=600)

    vieja = [l for l in doc.splitlines() if l.startswith("    GEOMAPAS['demo-mapa'] =")]
    if len(vieja) != 1:
        sys.exit(f"PARADO: {len(vieja)} registros de GEOMAPAS['demo-mapa'], se esperaba 1")
    doc = sustituye(doc, vieja[0], "    // El apéndice A no tiene mapas: su figura del plano es un SVG fijo.",
                    "los .geomapa")

    doc = reemplaza_region(doc, "    GLOSARIOS['demo-notacion'] = {", "\n    };\n",
                           "    // El glosario de notación del curso vive en el capítulo 1.\n",
                           "GLOSARIOS", max_lineas=40)

    doc = reemplaza_region(
        doc,
        "    // --- Deslizadores sobre un gráfico de línea ----------------------\n"
        "    SIMULADORES['demo-deslizadores'] = function (raiz) {",
        "    // ================================================================\n"
        "    // Autoevaluación de demostración: una pregunta de cada tipo\n",
        "    // --- El motor de los simuladores (precalculo/densidad1d.js) ---\n"
        + motor + "\n" + SIMULADORES_JS
        + "\n    // ================================================================\n"
          "    // Autoevaluación de demostración: una pregunta de cada tipo\n",
        "los simuladores de demostración", max_lineas=140, min_lineas=100)

    doc = reemplaza_region(doc, "    AUTOEVALUACIONES['demo'] = [", "\n    ];\n",
                           QUIZ_JS.lstrip("\n"), "AUTOEVALUACIONES", max_lineas=90)
    doc = reemplaza_region(doc, "    SIMULACROS['demo'] = {", "\n    };\n", "",
                           "el simulacro de demostración", max_lineas=40)
    doc = reemplaza_region(doc, "    TABLAS_RANKING['demo'] = function () {", "\n    };\n", "",
                           "la tabla de ranking de demostración", max_lineas=40)

    DESTINO.parent.mkdir(parents=True, exist_ok=True)
    # La SAL del barajado. Con «apendicea» la correcta caía 7 de 15 veces en la
    # segunda posición: marcar siempre la (b) acertaba casi la mitad. El
    # barajador es determinista y compartido, así que no se toca; se probaron
    # 28 sales y esta es la que reparte más parejo (3, 4, 4 y 4). Añadir una
    # pregunta solo rebaraja esa pregunta (revisión 2, 2026-10-02).
    doc = baraja_documento(doc, "apendicea-r4")
    DESTINO.write_text(doc, encoding="utf-8")

    marcado = doc[:doc.rindex("\n  <script>")]
    mods = doc.count('<template id="module-')
    sims = marcado.count('data-simulador="')
    registrados = len(_re.findall(r"SIMULADORES\['apa-[a-z]+'\] = function", doc))
    bl_r = doc.count('class="language-r"')
    bl_py = doc.count('class="language-python"')
    cifras = doc.count("#&gt;")
    lienzos = marcado.count("<canvas")
    con_alt = sum(1 for c in marcado.split("<canvas")[1:] if "aria-label" in c.split(">")[0])
    ejercicios = marcado.count('class="ejercicio-guiado"')
    preguntas = QUIZ_JS.count("tipo: '")
    opciones_quiz = QUIZ_JS.count("{ texto: ")
    retros = QUIZ_JS.count("retro: '")
    kb = DESTINO.stat().st_size / 1024

    print(f"{DESTINO.relative_to(RAIZ)}  {kb:.0f} KB")
    print(f"  {mods} módulos · {sims} simuladores ({registrados} registrados) · "
          f"{bl_r} bloques de R y {bl_py} de Python · {cifras} cifras anunciadas")
    print(f"  {lienzos} lienzos, {con_alt} con aria-label · {preguntas} preguntas "
          f"({opciones_quiz} opciones, {retros} con su retroalimentación) · {ejercicios} ejercicios")
    problemas = []
    if mods != MODULOS_OBJETIVO:
        problemas.append(f"módulos: {mods} y son {MODULOS_OBJETIVO}")
    if sims != N_SIMULADORES or registrados != N_SIMULADORES:
        problemas.append(f"simuladores: {sims} en el marcado y {registrados} registrados; son {N_SIMULADORES}")
    ids = set(_re.findall(r'data-simulador="([^"]+)"', marcado))
    regs = set(_re.findall(r"SIMULADORES\['([^']+)'\] = function", doc))
    if ids - regs or {r for r in regs if r.startswith("apa-")} - ids:
        problemas.append(f"simuladores sin pareja: marcado sin registro {sorted(ids - regs)}, "
                         f"registro sin marcado {sorted({r for r in regs if r.startswith('apa-')} - ids)}")
    if bl_r != bl_py:
        problemas.append(f"R y Python descuadrados: {bl_r} y {bl_py}")
    if lienzos != con_alt:
        problemas.append(f"lienzos sin aria-label: {lienzos - con_alt}")
    if ejercicios != N_EJERCICIOS:
        problemas.append(f"ejercicios: {ejercicios} y son {N_EJERCICIOS}")
    if preguntas != N_PREGUNTAS:
        problemas.append(f"preguntas: {preguntas} y son {N_PREGUNTAS}")
    if "respuesta: '" in doc or "explicacion: '" in doc:
        problemas.append("hay opciones con la clave `respuesta`/`explicacion`: el motor lee `retro`")
    if retros != opciones_quiz:
        problemas.append(f"opciones sin `retro`: {opciones_quiz - retros} de {opciones_quiz}")
    if "demo-" in marcado:
        problemas.append("quedan restos de los módulos de demostración en el marcado")
    if problemas:
        print("\n  PROBLEMAS:")
        for p in problemas:
            print(f"   - {p}")
        return 1
    print("\n  Apéndice A ensamblado.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
