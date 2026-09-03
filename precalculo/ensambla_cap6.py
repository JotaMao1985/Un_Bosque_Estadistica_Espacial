#!/usr/bin/env python3
"""
ensambla_cap6.py — el capítulo 6 escrito sobre la plantilla (T4.2)

  «Datos de área y la matriz de pesos espaciales»
  semanas 10-11 · Material de Estadística Espacial 2026-II (20929).

QUÉ HACE. Estampa `plantilla/plantilla-capitulo.html` con los doce módulos
del capítulo, sus simuladores, sus dos mapas, su autoevaluación y sus
ejercicios, y escribe `Htmls_Espacial/capitulo-6-pesos-espaciales.html`.

LA REGLA QUE MANDA (D10): ninguna cifra se escribe aquí. Todas salen de
`cap6_datos.json`, por un formateador. Lo vigila `sin_aritmetica.py`, que
mira el CÓDIGO y no el resultado: si un número se calcula dentro de un
formateador, para.

LOS DOS TABLEROS, que son la decisión de la que cuelga todo el capítulo:

  · COLUMBUS (49 barrios) es el LABORATORIO. Diez definiciones de vecindad
    sobre los mismos polígonos, 18,9 KB, y sus cifras son las que publica
    Anselin —118 parejas y grado 4,8163 la reina—, así que el tablero se
    valida solo.
  · LOS 1 122 MUNICIPIOS son el CASO REAL, con UNA sola vecindad. Diez
    sobre ellos pesaban 465 KB contra un presupuesto de 120. Lo que traen
    y no se puede mudar de tablero: 2 islas, 3 subgrafos y una variable
    con la que el rezago significa algo.

El porqué entero está en el A.25 del plan, y las cifras que lo deciden en
`cap6_datos.json`.

Uso:  python3 precalculo/ensambla_cap6.py
Devuelve 1 mientras el capítulo esté a medias, y lo dice.
"""
from __future__ import annotations

import json
import pathlib
import sys

from baraja_opciones import baraja_documento

RAIZ = pathlib.Path(__file__).resolve().parent.parent
PLANTILLA = RAIZ / "plantilla" / "plantilla-capitulo.html"
SALIDAS = RAIZ / "precalculo" / "salidas"
DESTINO = RAIZ / "Htmls_Espacial" / "capitulo-6-pesos-espaciales.html"

D = json.loads((SALIDAS / "cap6_datos.json").read_text(encoding="utf-8"))
M = json.loads((SALIDAS / "cap6_mapas.json").read_text(encoding="utf-8"))
SOL = json.loads((SALIDAS / "cap6_soluciones.json").read_text(encoding="utf-8"))

m1, m2, m3, m4 = D["m1"], D["m2"], D["m3"], D["m4"]
m5, m6, m7, m8 = D["m5"], D["m6"], D["m7"], D["m8"]
m9, m10, m11 = D["m9"], D["m10"], D["m11"]

# Los diez criterios del módulo 2, por su identificador, para no repetir
# el `next(... if c["id"] == ...)` treinta veces.
CRIT = {c["id"]: c for c in m2["criterios"]}
GEOM = {g["id"]: g for g in m6["columbus"]}
EST = {e["id"]: e for e in m7["estilos"]}

MODULOS_OBJETIVO = 12


def n(x, d=5):
    return f"{float(x):.{d}f}"


def ent(x):
    """Entero con espacio fino U+202F. NO usar dentro de KaTeX."""
    return f"{int(round(float(x))):,}".replace(",", " ")


def firma(valor, unidad=""):
    return f"<strong>{valor}</strong>{unidad}"


def pct(x, d=1):
    return f"{float(x):.{d}f} %".replace(".", ",")


def cabecera(num, titulo, ingles, objetivo):
    return f"""
  <!-- ============================================================ -->
  <!-- MÓDULO {num} · {titulo[:52]:<52} -->
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


def sim(ident, titulo, pie="", alto=260, mandos=True):
    icono = "fa-sliders" if mandos else "fa-chart-column"
    return f"""      <div class="simulador" data-simulador="{ident}">
        <h4><i class="fas {icono}" aria-hidden="true"></i> {titulo}</h4>
        {f'<p class="simulador-intro">{pie}</p>' if pie else ''}
{'        <div class="simulador-controles"></div>' + chr(10) if mandos else ''}        <div class="grafico-wrapper" style="height:{alto}px;">
          <canvas role="img" aria-label="{titulo}"></canvas>
        </div>
        <div class="simulador-lectura"></div>
      </div>
"""


def fila(*celdas):
    cab, resto = celdas[0], celdas[1:]
    return ('            <tr><th scope="row">' + str(cab) + '</th>'
            + ''.join('<td>' + str(c) + '</td>' for c in resto) + '</tr>\n')


def tabla(cabeceras, filas, titulo=""):
    th = "".join(f"<th>{c}</th>" for c in cabeceras)
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


# EL SUBTÍTULO ES EL DE LA BARRA LATERAL Y VA EN ESPAÑOL; el inglés es la
# glosa del `<h2>`. Son dos cosas distintas y la primera versión las
# confundió: `courseData` acabó con «Areal data» de subtítulo, que es lo
# único que un estudiante ve en el índice del capítulo.
TITULOS = (
    ("El dato de área", "Qué se observa y qué es aleatorio"),
    ("Vecindad", "La decisión que condiciona todo lo demás"),
    ("Contigüidad", "Torre, reina y órdenes superiores"),
    ("k vecinos más próximos", "Siempre k, y la simetría rota"),
    ("Umbral de distancia", "Islas y densidad desigual"),
    ("Vecindades geométricas", "Delaunay, Gabriel y esfera de influencia"),
    ("De vecinos a pesos", "Los estilos B, W, S, C y U"),
    ("El flujo de `spdep`", "Y `sfdep` como interfaz tidy"),
    ("Islas y `zero.policy`", "Qué hace R con quien no tiene vecinos"),
    ("El rezago espacial Wy", "La media de los vecinos"),
    ("W es un grafo", "Adyacencia, paso de mensajes y GNN"),
    ("Autoevaluación y ejercicios", "Trece preguntas y cinco ejercicios"),
)

INGLES = (
    "Areal data", "The decision that conditions everything",
    "Rook, queen and higher orders", "Always k, and symmetry broken",
    "Distance thresholds and islands", "Geometric neighbourhoods",
    "From neighbours to weights", "The spdep workflow",
    "Islands and zero.policy", "The spatial lag", "W is a graph",
    "Self-assessment and guided exercises",
)

# =====================================================================
# LOS BLOQUES DE CÓDIGO VAN APARTE DE LA PROSA, y no es estilo: un literal
# de tres comillas dentro de una f-string de tres comillas la cierra a
# media expresión, y el SyntaxError sale doscientas líneas más allá.
# Los `#>` se rellenan con `.format()` desde el JSON; ninguno se escribe a
# mano, y `verifica_bloques.py` los ejecuta para comprobarlo.
# =====================================================================
R1 = '''library(sf)
library(spdep)

# El laboratorio: 49 barrios de Columbus, el tablero de Anselin
col &lt;- st_read(system.file(&quot;shapes/columbus.gpkg&quot;, package = &quot;spData&quot;), quiet = TRUE)
nrow(col)
#&gt; [1] {NCOL}

# El caso real: los municipios de Colombia, con su deserción escolar
mun &lt;- st_read(&quot;datos/procesado/colombia_adm2.gpkg&quot;, quiet = TRUE)
nrow(mun)
#&gt; [1] {NMUN}

round(mean(col$CRIME), 4)
#&gt; [1] {CRIME}'''

PY1 = '''import geopandas as gpd
import numpy as np
import libpysal
from libpysal import weights

# El mismo tablero, leído por el otro lado
col = gpd.read_file(libpysal.examples.get_path(&quot;columbus.shp&quot;))
print(len(col))
#&gt; {NCOL}

mun = gpd.read_file(&quot;datos/procesado/colombia_adm2.gpkg&quot;)
print(len(mun))
#&gt; {NMUN}

print(round(col[&quot;CRIME&quot;].mean(), 4))
#&gt; {CRIME}'''

R2 = '''# Diez definiciones de vecino sobre los MISMOS 49 polígonos
cent &lt;- st_centroid(st_geometry(col))

reina &lt;- poly2nb(col, queen = TRUE)
torre &lt;- poly2nb(col, queen = FALSE)
k3    &lt;- knn2nb(knearneigh(cent, k = 3))
del   &lt;- tri2nb(cent)

# Lo que hay que mirar de cada una: cuántas parejas une y con qué reparto
sum(card(reina)) / 2
#&gt; [1] {PR}
sum(card(torre)) / 2
#&gt; [1] {PT}

round(mean(card(reina)), 4)
#&gt; [1] {GR}
round(mean(card(torre)), 4)
#&gt; [1] {GT}'''

PY2 = '''# Y las mismas, con libpysal: dos bibliotecas para la misma pregunta
reina = weights.Queen.from_dataframe(col, use_index=True)
torre = weights.Rook.from_dataframe(col, use_index=True)

# `pares` cuenta {{i, j}}; `enlaces` cuenta i -&gt; j. En una vecindad
# simétrica uno es el doble del otro, y en una de k vecinos NO.
def pares(w):
    return len({{tuple(sorted((i, j))) for i in w.neighbors
                for j in w.neighbors[i]}})

print(pares(reina), pares(torre))
#&gt; {PR} {PT}

print(round(reina.mean_neighbors, 4), round(torre.mean_neighbors, 4))
#&gt; {GR} {GT}'''

R3 = '''# Reina y torre se diferencian SOLO en el contacto de esquina
sum(card(reina)) / 2 - sum(card(torre)) / 2
#&gt; [1] {SOLO}

# Y la contigüidad de ORDEN SUPERIOR no acumula: el orden 2 son los
# vecinos de los vecinos que no eran ya vecinos.
ordenes &lt;- nblag(reina, maxlag = 3)
sapply(ordenes, function(nb) sum(card(nb)) / 2)
#&gt; [1] {O1} {O2} {O3}'''

PY3 = '''# El mismo cálculo, por conjuntos de parejas
p_reina = {{tuple(sorted((i, j))) for i in reina.neighbors for j in reina.neighbors[i]}}
p_torre = {{tuple(sorted((i, j))) for i in torre.neighbors for j in torre.neighbors[i]}}

print(len(p_reina - p_torre))
#&gt; {SOLO}

# La torre está CONTENIDA en la reina: no son dos criterios distintos,
# es uno más exigente que el otro.
print(p_torre &lt;= p_reina)
#&gt; True'''

R4 = '''# `knearneigh` da SIEMPRE k vecinos, haya quien haya cerca
k3 &lt;- knn2nb(knearneigh(cent, k = 3))

# ...y la relación no es recíproca
is.symmetric.nb(k3)
#&gt; [1] FALSE

# Los enlaces DIRIGIDOS son 3n, y son impares: ya eso lo delata
sum(card(k3))
#&gt; [1] {EK3}

# Forzar la simetría añade aristas, así que el grado deja de valer k
sim &lt;- make.sym.nb(k3)
round(mean(card(sim)), 4)
#&gt; [1] {GSIM}'''

PY4 = '''k3 = weights.KNN.from_dataframe(col, k=3, use_index=True)

# La asimetría, contada: pares (i, j) con j vecino de i pero no al revés
asim = sum(1 for i in k3.neighbors for j in k3.neighbors[i]
           if i not in k3.neighbors[j])
print(asim)
#&gt; {ASIM}

# Y por eso enlaces y parejas no son el doble uno del otro
print(sum(len(v) for v in k3.neighbors.values()), pares(k3))
#&gt; {EK3} {PK3}'''

R5 = '''# El umbral no mira fronteras ni vecinos: mira una distancia
d1 &lt;- max(unlist(nbdists(knn2nb(knearneigh(cent, k = 1)), cent)))
round(d1, 4)          # el umbral MÁS CORTO que no deja a nadie solo
#&gt; [1] {U}

corto &lt;- dnearneigh(cent, 0, d1 / 2)
justo &lt;- dnearneigh(cent, 0, d1)

# Con la mitad, buena parte del mapa se queda sin vecinos
sum(card(corto) == 0)
#&gt; [1] {I1}

# Y en el umbral justo NO hay islas... pero el grafo sigue partido
sum(card(justo) == 0)
#&gt; [1] {I2}
n.comp.nb(justo)$nc
#&gt; [1] {S2}'''

PY5 = '''xy = np.c_[col.geometry.centroid.x, col.geometry.centroid.y]
d = np.sqrt(((xy[:, None, :] - xy[None, :, :]) ** 2).sum(-1))
np.fill_diagonal(d, np.inf)
umbral = d.min(axis=1).max()
print(round(umbral, 4))
#&gt; {U}

justo = weights.DistanceBand.from_array(xy, threshold=umbral,
                                        silence_warnings=True)
print(justo.n_components)
#&gt; {S2}'''

R6 = '''# Tres grafos geométricos, y uno contiene al siguiente
del &lt;- tri2nb(cent)                                   # Delaunay
gab &lt;- graph2nb(gabrielneigh(st_coordinates(cent)), sym = TRUE)
rel &lt;- graph2nb(relativeneigh(st_coordinates(cent)), sym = TRUE)
soi &lt;- graph2nb(soi.graph(tri2nb(cent), cent), sym = TRUE)

sapply(list(del, gab, rel, soi), function(nb) sum(card(nb)) / 2)
#&gt; [1] {PD} {PG} {PR} {PS}'''

PY6 = '''delaunay = weights.Delaunay(xy)
gabriel  = weights.Gabriel(xy)
relativa = weights.Relative_Neighborhood(xy)

# El anidamiento se COMPRUEBA, no se cita
def pset(w):
    return {{tuple(sorted((i, j))) for i in w.neighbors for j in w.neighbors[i]}}

print(pset(relativa) &lt;= pset(gabriel) &lt;= pset(delaunay))
#&gt; True

print(len(pset(delaunay)), len(pset(gabriel)), len(pset(relativa)))
#&gt; {PD} {PG} {PR}'''

R7 = '''# El mismo grafo, cinco matrices distintas
for (e in c(&quot;B&quot;, &quot;W&quot;, &quot;S&quot;, &quot;C&quot;, &quot;U&quot;)) {{
  lw &lt;- nb2listw(reina, style = e)
  cat(e, round(sum(unlist(lw$weights)), 4), &quot;\\n&quot;)
}}
#&gt; B {SBi}
#&gt; W {SWi}
#&gt; S {SSi}
#&gt; C {SCi}
#&gt; U {SUi}

# Y lo que eso le hace al rezago de la misma variable
lw &lt;- nb2listw(reina, style = &quot;W&quot;)
round(cor(col$CRIME, lag.listw(lw, col$CRIME)), 4)
#&gt; [1] {CW}'''

PY7 = '''A = reina.full()[0]                      # la adyacencia binaria

def estilo(A, e):
    n = len(A)
    if e == &quot;B&quot;: return A
    if e == &quot;W&quot;: return A / A.sum(1, keepdims=True)
    if e == &quot;C&quot;: return A * (n / A.sum())
    if e == &quot;U&quot;: return A / A.sum()
    q = np.sqrt((A ** 2).sum(1, keepdims=True))     # S, estabilización
    S = A / q
    return S * (n / S.sum())

print([round(float(estilo(A, e).sum()), 4) for e in &quot;BWSCU&quot;])
#&gt; [{SBf}, {SWf}, {SSf}, {SCf}, {SUf}]'''

R8 = '''# El flujo de spdep son tres llamadas, y siempre en este orden
nb &lt;- poly2nb(col, queen = TRUE)     # 1. quiénes son vecinos
lw &lt;- nb2listw(nb, style = &quot;W&quot;)      # 2. cuánto pesa cada uno
wy &lt;- lag.listw(lw, col$CRIME)       # 3. la media de los vecinos

round(head(wy, 3), 4)
#&gt; [1] {WY}

# sfdep es la MISMA maquinaria con nombres tidy
library(sfdep)
nb2 &lt;- st_contiguity(st_geometry(col))
wt2 &lt;- st_weights(nb2)
max(abs(wy - st_lag(col$CRIME, nb2, wt2)))
#&gt; [1] {DIFi}'''

PY8 = '''# En Python el mismo camino son dos pasos, porque los pesos van dentro
w = weights.Queen.from_dataframe(col, use_index=True)
w.transform = &quot;r&quot;                     # estandarizada por filas
wy = weights.lag_spatial(w, col[&quot;CRIME&quot;].values)

print([round(float(v), 4) for v in wy[:3]])
#&gt; [{WY_PY}]

# Las dos bibliotecas cuentan las mismas parejas
print(pares(w))
#&gt; {NP}'''

R9 = '''nb &lt;- poly2nb(mun, queen = TRUE)

# Dos municipios no tocan a nadie, y son islas de verdad
which(card(nb) == 0)
#&gt; [1] {I1} {I2}

# Sin `zero.policy`, construir los pesos FALLA. Y es lo correcto:
# una fila vacía no tiene media.
class(try(nb2listw(nb, style = &quot;W&quot;), silent = TRUE))
#&gt; [1] &quot;try-error&quot;

# Con él, la fila se queda a cero y el rezago de la isla vale CERO,
# que no es lo mismo que «no tiene rezago».
lw &lt;- nb2listw(nb, style = &quot;W&quot;, zero.policy = TRUE)
n.comp.nb(nb)$nc
#&gt; [1] {NC}'''

PY9 = '''wm = weights.Queen.from_dataframe(mun, use_index=True)

# libpysal no falla: avisa. Es el mismo problema con otra política.
islas = [i for i, v in wm.neighbors.items() if len(v) == 0]
print(sorted(islas))
#&gt; {ISLAS_PY}

print(wm.n_components)
#&gt; {NC}'''

R10 = '''# El rezago es la media de los vecinos, y punto
des &lt;- read.csv(&quot;datos/procesado/municipios_llave.csv&quot;)$desercion
ok  &lt;- is.finite(des)
sub &lt;- subset.nb(nb, ok)
lw  &lt;- nb2listw(sub, style = &quot;W&quot;, zero.policy = TRUE)
y   &lt;- des[ok]
wy  &lt;- lag.listw(lw, y, zero.policy = TRUE)
con &lt;- card(sub) &gt; 0

# Se parecen, y esa es toda la autocorrelación espacial del capítulo 7
round(cor(y[con], wy[con]), 4)
#&gt; [1] {COR}

# Pero el rezago es MÁS SUAVE que el dato: promediar contrae
round(sd(y), 4)
#&gt; [1] {SDY}
round(sd(wy[con]), 4)
#&gt; [1] {SDWY}'''

PY10 = '''import pandas as pd

llave = pd.read_csv(&quot;datos/procesado/municipios_llave.csv&quot;)
des = llave[&quot;desercion&quot;].to_numpy(dtype=float)
ok = np.isfinite(des)

# El subconjunto con dato, con su propia W
sub = mun[ok].reset_index(drop=True)
ws = weights.Queen.from_dataframe(sub, use_index=True)
ws.transform = &quot;r&quot;
y = des[ok]
wy = weights.lag_spatial(ws, y)
con = np.array([len(ws.neighbors[i]) for i in ws.id_order]) &gt; 0

print(round(float(np.corrcoef(y[con], wy[con])[0, 1]), 4))
#&gt; {COR}

print(round(float(100 * (1 - wy[con].std(ddof=1) / y.std(ddof=1))), 4))
#&gt; {CONTRA}'''

R11 = '''# W es la matriz de adyacencia de un grafo, y es DISPERSA
A &lt;- nb2mat(reina, style = &quot;B&quot;)
length(A)
#&gt; [1] {CAS}
sum(A &gt; 0)
#&gt; [1] {OCU}

# Estandarizar por filas ES normalizar por el grado: D^-1 A
W &lt;- nb2mat(reina, style = &quot;W&quot;)
max(abs(W - A / rowSums(A)))
#&gt; [1] {DINV}

# Y el rezago ES el producto W y: una capa de paso de mensajes
max(abs(as.numeric(W %*% col$CRIME) - lag.listw(nb2listw(reina, style = &quot;W&quot;), col$CRIME)))
#&gt; [1] {PROD}'''

PY11 = '''grados = A.sum(1)

# Lo mismo, con la notación de las redes neuronales sobre grafos
D_inv = np.diag(1 / grados)
print(np.abs(D_inv @ A - estilo(A, &quot;W&quot;)).max())
#&gt; {DINV}

# La densidad: qué fracción de la matriz está ocupada
print(round(100 * (A &gt; 0).sum() / A.size, 4))
#&gt; {DENS}'''

_SUB1 = dict(NCOL=ent(m1["columbus"]["n"]).replace(" ", ""),
             NMUN=ent(m1["municipios"]["n"]).replace(" ", ""),
             CRIME=n(m1["columbus"]["variables"]["crime"]["media"], 4))
_SUB2 = dict(PR=ent(CRIT["reina"]["pares"]), PT=ent(CRIT["torre"]["pares"]),
             GR=n(CRIT["reina"]["grado"], 4), GT=n(CRIT["torre"]["grado"], 4))
_SUB3 = dict(SOLO=ent(m3["solo_reina"]),
             O1=ent(m3["ordenes"][0]["pares"]), O2=ent(m3["ordenes"][1]["pares"]),
             O3=ent(m3["ordenes"][2]["pares"]))
_K3 = m4["columbus"][2]
_SUB4 = dict(EK3=ent(_K3["enlaces"]), PK3=ent(_K3["pares"]),
             NPARES=ent(_K3["pares"]), ASIM=ent(_K3["asimetricos"]),
             GSIM=n(m4["simetrizada_k3"]["grado"], 4))



# El bloque usa `d1 / 2`, que NO es ninguno de los puntos de la curva
# publicada: la curva va de 0,4·d1 a 1,6·d1. Las islas de la mitad se
# publican aparte para que el `#>` salga del JSON y no de una regla de tres.
_SUB5 = dict(U=n(m5["columbus"]["umbral_sin_islas"], 4),
             I1=ent(m5["columbus"]["islas_en_la_mitad"]),
             I2=ent(m5["columbus"]["curva"][3]["islas"]),
             S2=ent(m5["columbus"]["curva"][3]["subgrafos"]))
_SUB6 = dict(PS=ent(GEOM["esfera"]["pares"]), PD=ent(GEOM["delaunay"]["pares"]), PG=ent(GEOM["gabriel"]["pares"]),
             PR=ent(GEOM["relativa"]["pares"]))
# R imprime `236` y Python `236.0`: dos formatos para la misma cifra, y
# los dos salen del JSON. Escribir uno de ellos a mano es lo que
# `verifica_bloques.py` existe para cazar.
_SUB7 = dict(SBi=ent(EST["B"]["suma_total"]), SWi=ent(EST["W"]["suma_total"]),
             SSi=ent(EST["S"]["suma_total"]), SCi=ent(EST["C"]["suma_total"]),
             SUi=ent(EST["U"]["suma_total"]),
             SBf=n(EST["B"]["suma_total"], 1), SWf=n(EST["W"]["suma_total"], 1),
             SSf=n(EST["S"]["suma_total"], 1), SCf=n(EST["C"]["suma_total"], 1),
             SUf=n(EST["U"]["suma_total"], 1),
             CW=n(EST["W"]["cor_con_crime"], 4))
_SUB8 = dict(DIFi=ent(m8["dif_max"]), NP=ent(m8["n_pares_spdep"]),
             WY=" ".join(n(v, 4) for v in m8["wy_primeros"]),
             WY_PY=", ".join(n(v, 4) for v in m8["wy_primeros"]))


_SUB9 = dict(I1=ent(m9["islas_i"][0]), I2=ent(m9["islas_i"][1]),
             ERR=m9["error_sin_zero_policy"], NC=ent(m9["subgrafos"]),
             ISLAS_PY="[" + ", ".join(ent(i) for i in m9["islas_i0"]) + "]")
_SUB10 = dict(COR=n(m10["correlacion"], 4), SDY=n(m10["y"]["sd"], 4),
              SDWY=n(m10["wy"]["sd"], 4), CONTRA=n(m10["contraccion_pct"], 4))
_C11 = m11["columbus"]
_SUB11 = dict(CAS=ent(_C11["casillas"]), OCU=ent(_C11["no_ceros"]),
              DINV=n(_C11["d_inv_a_igual_w"], 0), PROD=n(_C11["lag_es_producto"], 0),
              DENS=n(_C11["densidad_pct"], 4))


import re as _re


def _codigo(texto):
    return _re.sub(r"`([^`]+)`", r"<code>\1</code>", texto)


def ejercicio(k, e):
    """El marcado de la CASA, no uno inventado.

    `cuenta_sitio.py` cuenta los ejercicios por `.ejercicio-guiado` y el
    desplegable se cablea por `.ejercicio-boton`; inventarse selectores deja
    un capítulo que se ve perfecto, con cero ejercicios contados y los
    botones muertos, sin un solo error en consola (A.13).
    """
    pasos = "".join(
        f'                <tr><th scope="row">{p["paso"]}</th>'
        f'<td>{p["valor"]:g}</td></tr>\n'
        for p in e["pasos"])
    return f"""
        <div class="ejercicio-guiado">
          <p class="ejercicio-enunciado"><span class="ejercicio-numero">{k}.</span><strong>{e['titulo']}.</strong>
            {_codigo(e['enunciado'])}</p>
          <div class="ejercicio-acciones">
            <button type="button" class="ejercicio-boton" aria-expanded="false" aria-controls="cap6-e{k}-sol">
              <i class="fas fa-key" aria-hidden="true"></i> Solución <i class="fas fa-chevron-down" aria-hidden="true"></i>
            </button>
          </div>
          <div class="ejercicio-panel solucion" id="cap6-e{k}-sol" hidden>
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
# LOS MÓDULOS
# =====================================================================
MOD1 = cabecera(
    1, TITULOS[0][0], INGLES[0],
    "Entender qué es lo aleatorio cuando el dato viene por unidades ya "
    "dibujadas, y por qué eso cambia la pregunta.") + f"""
      <p>Los dos capítulos anteriores preguntaban <em>dónde</em>. Un patrón puntual es una lista de
        posiciones y lo aleatorio es justamente esa lista: otra realización del mismo proceso pone
        los puntos en otro sitio, y hasta en otro número. El capítulo 4 dedicó doce módulos a
        decidir si esa lista era azar, y el 5 a estimar dónde se concentraba.</p>

      <p>El dato de área no funciona así. <strong>Las unidades están donde están</strong> —un
        municipio no se mueve, un barrio tampoco— y lo que varía es <em>lo que llevan dentro</em>.
        La pregunta deja de ser «¿por qué aquí?» y pasa a ser «¿por qué este valor aquí, y no el
        que tienen al lado?». Y para poder decir «al lado» hay que decir qué es estar al lado, que
        es de lo que va este capítulo entero.</p>

      <h3>Los dos tableros, y cada uno hace lo suyo</h3>

      <p>El capítulo trabaja con dos, y la diferencia no es de tamaño: es de papel.
        <strong>Columbus</strong> son {firma(ent(m1["columbus"]["n"]), " barrios")} de Ohio, el
        tablero con el que Anselin escribió los ejemplos que todo el mundo cita. Es pequeño a
        propósito: con 49 unidades se ve <em>una a una</em> qué cambia al cambiar la definición de
        vecino, y eso es lo que hace falta para entenderla. Su variable es la tasa de delitos, con
        media {firma(n(m1["columbus"]["variables"]["crime"]["media"], 4))} y desviación
        {firma(n(m1["columbus"]["variables"]["crime"]["sd"], 4))}.</p>

      <p>El otro son los {firma(ent(m1["municipios"]["n"]), " municipios")} de Colombia con su
        deserción escolar —{ent(m1["municipios"]["con_dato"])} con dato, media
        {firma(pct(m1["municipios"]["desercion"]["media"], 4))}, desviación
        {n(m1["municipios"]["desercion"]["sd"], 4)} y
        {ent(m1["municipios"]["desercion"]["ceros"])} ceros exactos—, el mismo hilo que viene
        desde el capítulo 1. Ahí no se ve nada unidad por unidad: lo que se ve es lo que un dato
        real trae y un tablero de laboratorio no tiene.</p>

{mapa_html("cap6-municipios", "Los 1 122 municipios y su contigüidad reina")}
      <p class="pie-figura">Cada punto es un municipio y cada línea, una pareja de vecinos por
        contigüidad reina. Los dos puntos rojos del Caribe son islas en el sentido literal
        <em>y</em> en el del grafo: no tocan a nadie, y el módulo 9 va sobre lo que R hace con
        ellos.</p>

{tabs("Los dos tableros", R1.format(**_SUB1), PY1.format(**_SUB1))}
      <p>Las dos columnas leen las mismas dos capas con dos bibliotecas distintas, y esa costumbre
        no es decorativa en este capítulo: <strong>todo lo que viene se puede calcular con
        <code>spdep</code> en R y con <code>libpysal</code> en Python</strong>, y las dos tienen
        que dar lo mismo. Cuando no lo dan, una de las dos está usando un convenio que no ha
        escrito.</p>
""" + CIERRE

MOD2 = cabecera(
    2, TITULOS[1][0], INGLES[1],
    "Ver que «vecino» no es un hecho del mapa sino una decisión, y que la "
    "decisión cambia el grafo entero.") + f"""
      <p>Todo lo que viene después —el rezago, el índice de Moran del capítulo 7, los modelos del
        8— se apoya en una matriz <strong>W</strong> que dice quién es vecino de quién. Y esa
        matriz no viene con el dato: <strong>la elige quien analiza</strong>. Es la decisión más
        consecuente del análisis de datos de área y, con diferencia, la menos justificada.</p>

      <p>La forma de verlo es no discutirla: fijar los polígonos y cambiar solo el criterio. Estos
        son los diez que el capítulo recorre, sobre los mismos {ent(m1["columbus"]["n"])} barrios.</p>

{sim("cap6-constructor",
     "Diez definiciones de vecino sobre los mismos 49 barrios",
     "Elige el criterio y mira dos cosas a la vez: el grafo, que se dibuja sobre el mapa, "
     "y el reparto de grados, que es lo que dos criterios con el mismo grado medio pueden "
     "tener distinto.")}
{mapa_html("cap6-w", "Columbus: el grafo del criterio elegido")}
      <p class="pie-figura">El mapa y el histograma se mueven juntos. Un punto rojo es una unidad
        sin vecinos: solo aparece con el umbral corto, y esa es la mitad de la lección del
        módulo 5.</p>

      <p>La tabla dice lo mismo en frío. Conviene mirar dos columnas que suelen confundirse:
        <strong>enlaces</strong> cuenta <em>i → j</em> y <strong>parejas</strong> cuenta
        {{<em>i, j</em>}}. En una vecindad simétrica el primero es el doble del segundo; en una de
        k vecinos, no — y por eso están las dos.</p>

{tabla(("Criterio", "Enlaces", "Parejas", "Grado medio", "Islas", "Subgrafos"),
       "".join(fila(c["etiqueta"], ent(c["enlaces"]), ent(c["pares"]),
                    n(c["grado"], 4), ent(c["islas"]), ent(c["subgrafos"]))
               for c in m2["criterios"]),
       "Los diez criterios sobre los 49 barrios de Columbus")}
      <p>Ninguno está mal calculado. Van de {firma(ent(CRIT["d_mitad"]["pares"]), " parejas")} a
        {firma(ent(CRIT["k6"]["pares"]))} sobre el mismo mapa, y cada uno contesta una pregunta
        distinta sobre qué significa estar cerca. Lo que no se puede hacer es publicar una
        superficie, un índice o un modelo <em>sin decir cuál se usó</em>.</p>

{tabs("Construir las vecindades", R2.format(**_SUB2), PY2.format(**_SUB2))}
      <p>Los módulos que siguen van uno por familia: contigüidad, k vecinos, umbral de distancia y
        vecindades geométricas. Y el 7 recoge lo que falta, que es cómo se pasa de «quiénes son
        vecinos» a «cuánto pesa cada uno».</p>
""" + CIERRE

MOD3 = cabecera(
    3, TITULOS[2][0], INGLES[2],
    "Distinguir torre de reina, ver dónde difieren y entender que la "
    "contigüidad de orden superior no acumula.") + f"""
      <p>La contigüidad es el criterio más antiguo y el más usado: son vecinos los que
        <em>se tocan</em>. La única duda es qué cuenta como tocarse, y hay dos respuestas con
        nombre de ajedrez. La <strong>torre</strong> exige compartir un tramo de frontera; la
        <strong>reina</strong> se conforma con un punto, así que añade los contactos de esquina.</p>

      <p>Sobre Columbus la diferencia es de {firma(ent(m3["solo_reina"]), " parejas")}: la reina
        une {ent(m3["reina"]["pares"])} y la torre {ent(m3["torre"]["pares"])}, con grados medios de
        {firma(n(m3["reina"]["grado"], 4))} y {firma(n(m3["torre"]["grado"], 4))}. Son las dos
        cifras que Anselin publica, y el precálculo <em>para</em> si alguna deja de salir: un
        tablero canónico sirve justamente para eso.</p>

      <p>Y una relación que conviene tener clara antes de elegir: <strong>la torre está contenida
        en la reina</strong>. No son dos criterios rivales, es uno más exigente que el otro, y por
        eso la reina nunca puede tener menos vecinos.</p>

{sim("cap6-ordenes",
     "La reina, la torre y los tres primeros órdenes",
     "Los dos primeros botones comparan los dos criterios de contacto. Los otros tres suben "
     "de orden sobre la reina, y lo que hay que mirar es que la barra no se acumula: cada "
     "orden son los que están a ESA distancia, no a esa o menos.")}
      <p>La contigüidad de orden superior es la respuesta a «¿y los vecinos de mis vecinos?».
        <code>nblag</code> la calcula, y trae una trampa de lectura: <strong>el orden 2 son los
        vecinos de los vecinos que no eran ya vecinos</strong>, no todos los que están a dos pasos.
        De ahí que la serie sea {ent(m3["ordenes"][0]["pares"])},
        {ent(m3["ordenes"][1]["pares"])} y {ent(m3["ordenes"][2]["pares"])} parejas y no una suma
        que crece sin parar: al tercer orden el mapa se está quedando sin sitios nuevos adonde
        llegar.</p>

{tabs("Reina, torre y órdenes", R3.format(**_SUB3), PY3.format(**_SUB3))}
      <p>Sobre el dato real la elección pesa menos de lo que parece: los municipios dan
        {ent(m3["municipios"]["reina"]["pares"])} parejas por reina y
        {ent(m3["municipios"]["torre"]["pares"])} por torre, un grado medio de
        {n(m3["municipios"]["reina"]["grado"], 4)} contra
        {n(m3["municipios"]["torre"]["grado"], 4)}. Con fronteras irregulares los contactos de
        esquina son pocos; con una retícula regular —un ráster, un tablero— son la mitad del
        grafo. <strong>El criterio importa lo que la geometría le deje importar.</strong></p>
""" + CIERRE

MOD4 = cabecera(
    4, TITULOS[3][0], INGLES[3],
    "Ver que k vecinos garantiza el grado y rompe la simetría, y qué "
    "consecuencias tiene cada una de las dos cosas.") + f"""
      <p>El criterio siguiente no mira las fronteras: mira las distancias entre centros y se queda
        con los <strong>k más próximos</strong>. Tiene una virtud que la contigüidad no tiene
        —<em>nadie se queda sin vecinos</em>— y un precio que casi nadie declara.</p>

      <p>La virtud primero. Con <code>knearneigh</code> el grado vale exactamente k para todas las
        unidades, siempre: sobre Columbus, k = 3 da {ent(_K3["enlaces"])} enlaces dirigidos y grado
        {n(_K3["grado"], 0)} en las {ent(m1["columbus"]["n"])}. Eso hace comparables las filas de W,
        y es la razón de que se use tanto en econometría espacial.</p>

      <p>Y ahora el precio: <strong>«ser de los k más próximos» no es recíproco</strong>. Que B sea
        de los tres más cercanos a A no obliga a que A lo sea de B —basta con que B esté en una
        zona más densa—. Con k = 3 sobre Columbus hay {firma(ent(_K3["asimetricos"]), " pares")} en
        esa situación, y por eso los {ent(_K3["enlaces"])} enlaces dirigidos solo unen
        {firma(ent(_K3["pares"]), " parejas distintas")}.</p>

      <p>Hay una forma de verlo sin contar nada: <strong>{ent(_K3["enlaces"])} es impar</strong>. Si
        la relación fuera recíproca, cada pareja aportaría dos enlaces y el total sería par por
        construcción. Un número impar de enlaces dirigidos es, por sí solo, la prueba de que la
        vecindad no es simétrica.</p>

{sim("cap6-knn",
     "k, de 1 a 8: lo que garantiza y lo que rompe",
     "El deslizador mueve k. La barra verde son las parejas distintas que el criterio une "
     "y la naranja, los pares en los que la relación NO es recíproca. Las dos crecen, pero "
     "no al mismo ritmo.")}
      <p>La asimetría no es un defecto que haya que corregir: es información sobre la densidad del
        patrón. Pero <em>hay que saber que está</em>, porque casi todo lo que viene después —el
        índice de Moran, los modelos autorregresivos— supone una W simétrica o la simetriza por su
        cuenta sin decirlo.</p>

      <p>Simetrizar tiene un coste que se ve en una cifra. <code>make.sym.nb</code> añade las
        aristas que faltan, así que el grado <strong>deja de valer k</strong>: la k = 3 de Columbus
        pasa a {firma(n(m4["simetrizada_k3"]["grado"], 4))} de media, con unidades de hasta
        {ent(m4["simetrizada_k3"]["grado_max"])} vecinos. Se gana la simetría y se pierde
        exactamente lo que hacía atractivo al criterio.</p>

{tabs("k vecinos y la simetría", R4.format(**_SUB4), PY4.format(**_SUB4))}
      <p>Sobre los municipios pasa lo mismo y más marcado: k = 4 deja
        {firma(ent(m4["municipios_k4"]["asimetricos"]), " pares asimétricos")} sobre
        {ent(m4["municipios_k4"]["enlaces"])} enlaces. Y aquí aparece la otra cara del criterio:
        con k vecinos <strong>no hay islas nunca</strong> —el archipiélago de San Andrés queda
        unido al continente por 700 km de mar—, lo cual resuelve un problema del módulo 9 creando
        uno peor: una vecindad que no significa nada.</p>
""" + CIERRE


MOD5 = cabecera(
    5, TITULOS[4][0], INGLES[4],
    "Entender que un umbral de distancia reparte vecinos de forma desigual "
    "cuando la densidad lo es, y que quitar islas no conecta el grafo.") + f"""
      <p>El tercer criterio es el más directo de explicar: son vecinos los que están a menos de
        cierta distancia. Y es el que peor se porta, por un motivo que no tiene que ver con la
        matemática sino con el mundo: <strong>las unidades no están repartidas de forma
        uniforme</strong>. Un umbral que en una ciudad da tres vecinos, en el campo da cero.</p>

      <p>Sobre Columbus se ve entero moviendo el umbral. Con la mitad de lo que hace falta,
        {firma(ent(m5["columbus"]["la_mitad"]["islas"]), " de los 49 barrios")} se quedan sin
        vecinos y el mapa se parte en {ent(m5["columbus"]["la_mitad"]["subgrafos"])} pedazos. Con
        el doble, el grado medio sube a {n(m5["columbus"]["curva"][6]["grado"], 4)} y la vecindad
        deja de distinguir nada: casi todo el mundo es vecino de casi todo el mundo.</p>

{sim("cap6-umbral",
     "El umbral, de corto a largo",
     "El deslizador mueve la distancia. La barra verde son las parejas que el criterio une; "
     "la naranja, las unidades que se quedan sin ninguna. Lo que hay que buscar es el punto "
     "donde la naranja llega a cero, y luego mirar los subgrafos.")}
      <h3>El umbral mínimo sin islas, y por qué no basta</h3>

      <p>Hay un umbral que se puede calcular en vez de tantear: <strong>la mayor de las distancias
        al vecino más próximo</strong>. Por debajo de él alguien se queda solo por construcción;
        justo en él, nadie. Sobre Columbus vale {firma(n(m5["columbus"]["umbral_sin_islas"], 4))}.</p>

      <p>Y aquí está lo que casi nunca se dice. En ese umbral hay
        {firma(ent(m5["columbus"]["curva"][3]["islas"]), " islas")}… y el grafo sigue teniendo
        {firma(ent(m5["columbus"]["curva"][3]["subgrafos"]), " subgrafos")}. <strong>Quitar las
        islas no conecta el grafo</strong>: son dos propiedades distintas, y la que suele importar
        —que la información pueda viajar de cualquier unidad a cualquier otra— es la segunda. Hace
        falta subir hasta {n(m5["columbus"]["curva"][4]["umbral"], 4)} para que el mapa sea una
        sola pieza.</p>

{tabs("El umbral y sus islas", R5.format(**_SUB5), PY5.format(**_SUB5))}
      <h3>Y sobre el dato real, la cifra que cierra el módulo</h3>

      <p>En los municipios de Colombia el umbral mínimo sin islas es de
        {firma(n(m5["municipios"]["umbral_sin_islas_km"], 1), " km")} —la distancia que separa a
        San Andrés de su vecino más próximo—. A esa distancia el grafo tiene
        {firma(ent(m5["municipios"]["en_el_umbral"]["pares"]), " parejas")} y un grado medio de
        {firma(n(m5["municipios"]["en_el_umbral"]["grado"], 1))}: cada municipio sería vecino de
        ciento setenta y nueve, y el más conectado de
        {ent(m5["municipios"]["en_el_umbral"]["grado_max"])}.</p>

      <p>Esa W es correcta y es inútil. No hay ninguna pregunta razonable cuya respuesta dependa
        de que Leticia y Manizales sean vecinas. <strong>Y sigue teniendo
        {ent(m5["municipios"]["en_el_umbral"]["subgrafos"])} subgrafos</strong>, así que ni
        siquiera compra lo que se pagó por ella. La lección del módulo cabe en una frase: el umbral
        que arregla las islas rompe la vecindad, y cuando eso pasa el problema no es el umbral
        — es que la escala del dato no es uniforme.</p>

      <p>Es también la única de las diez definiciones de este capítulo que <strong>no se puede
        dibujar</strong>: cien mil aristas sobre mil polígonos son una mancha. Se mira como
        número, y eso también es parte de saber elegir una W.</p>
""" + CIERRE

MOD6 = cabecera(
    6, TITULOS[5][0], INGLES[5],
    "Conocer las vecindades que salen de la geometría del propio patrón, y "
    "ver que están anidadas unas dentro de otras.") + f"""
      <p>Las tres familias anteriores necesitan una decisión humana: qué cuenta como tocarse,
        cuánto vale k, dónde está el umbral. Hay una cuarta que no: <strong>vecindades que salen de
        la geometría de los propios puntos</strong>, sin parámetro que ajustar.</p>

      <p>La más conocida es la <strong>triangulación de Delaunay</strong>: son vecinos los puntos
        unidos por un lado de la triangulación, que es la que evita los triángulos alargados. Sobre
        Columbus da {firma(ent(GEOM["delaunay"]["pares"]), " parejas")} y grado medio
        {n(GEOM["delaunay"]["grado"], 4)}, muy cerca de la contigüidad reina — y no es casualidad:
        las dos están diciendo «los que rodean».</p>

      <p>Las otras tres son subconjuntos suyos, cada una con una regla más exigente:</p>

{tabla(("Criterio", "Parejas", "Grado medio", "Grado mínimo", "Grado máximo"),
       "".join(fila({"delaunay": "Delaunay", "gabriel": "Gabriel",
                     "relativa": "Vecindad relativa", "esfera": "Esfera de influencia"}[g["id"]],
                    ent(g["pares"]), n(g["grado"], 4), ent(g["grado_min"]), ent(g["grado_max"]))
               for g in m6["columbus"]),
       "Las cuatro vecindades geométricas sobre Columbus")}
      <p>El <strong>grafo de Gabriel</strong> se queda con las parejas cuyo círculo de diámetro
        <em>ij</em> no contiene a nadie más. La <strong>vecindad relativa</strong> aprieta más: no
        puede haber nadie más cerca de los dos que ellos entre sí. Y la <strong>esfera de
        influencia</strong> une a los que se solapan con el círculo centrado en cada punto y radio
        su distancia al más próximo.</p>

      <p>Lo que hace que esto sea una familia y no una lista es que <strong>están anidadas</strong>:
        {firma("relativa ⊆ Gabriel ⊆ Delaunay")}. El precálculo no lo cita: lo comprueba, y el
        auditor lo vuelve a comprobar con la otra biblioteca. Por eso los grados caen de
        {n(GEOM["delaunay"]["grado"], 4)} a {n(GEOM["gabriel"]["grado"], 4)} y a
        {n(GEOM["relativa"]["grado"], 4)} sin que ninguna añada nada que la anterior no tuviera.</p>

{tabs("Las vecindades geométricas", R6.format(**_SUB6), PY6.format(**_SUB6))}
      <p>Sobre los municipios el orden se conserva —{ent(m6["municipios"][0]["pares"])},
        {ent(m6["municipios"][1]["pares"])} y {ent(m6["municipios"][2]["pares"])} parejas— y la
        esfera de influencia queda en medio con {ent(m6["municipios"][3]["pares"])}. Ninguna deja
        islas, ni siquiera con San Andrés: al no mirar fronteras, el archipiélago acaba unido a la
        costa. <strong>Es la misma solución tramposa que los k vecinos</strong>, con otro nombre.</p>
""" + CIERRE

MOD7 = cabecera(
    7, TITULOS[6][0], INGLES[6],
    "Pasar de «quiénes son vecinos» a «cuánto pesa cada uno», y ver que el "
    "estilo cambia lo que la fila significa.") + f"""
      <p>Hasta aquí W ha sido un grafo: hay arista o no la hay. Para calcular algo hace falta el
        otro paso, que es poner un número en cada arista. <code>nb2listw</code> lo hace, y trae
        cinco convenios con nombre de letra. <strong>El mismo grafo, cinco matrices.</strong></p>

      <p>Y no es un detalle de escala. Lo que cambia entre ellos es <em>qué significa una fila</em>,
        y con eso, qué significa el rezago que se calcule después.</p>

{tabla(("Estilo", "Suma de W", "Peso del vecino de la unidad de grado 10",
        "Peso del vecino de la de grado 2", "Correlación del rezago con CRIME"),
       "".join(fila({"B": "B · binaria", "W": "W · por filas", "S": "S · estabilizada",
                     "C": "C · global", "U": "U · unitaria"}[e["id"]],
                    n(e["suma_total"], 4), n(e["peso_max"], 4), n(e["peso_min"], 4),
                    n(e["cor_con_crime"], 4))
               for e in m7["estilos"]),
       "Los cinco estilos sobre la contigüidad reina de Columbus")}
      <p><strong>B</strong> deja todos los pesos en 1, así que la fila de una unidad con
        {ent(m7["unidad_max"]["grado"])} vecinos suma {ent(m7["unidad_max"]["grado"])} y la de una
        con {ent(m7["unidad_min"]["grado"])} suma {ent(m7["unidad_min"]["grado"])}: el rezago deja
        de ser una media y pasa a ser una suma, y las unidades del centro pesan más solo por estar
        rodeadas. Su total es {firma(ent(EST["B"]["suma_total"]))}, que son los enlaces dirigidos
        del grafo.</p>

      <p><strong>W</strong> divide cada fila por su grado, así que todas suman 1 y el rezago es
        <em>la media de los vecinos</em>. Es el más usado y el que casi siempre se quiere. Su
        precio se ve en la tabla: el vecino de la unidad de grado {ent(m7["unidad_min"]["grado"])}
        pesa {firma(n(EST["W"]["peso_min"], 4))} y el de la de grado
        {ent(m7["unidad_max"]["grado"])} pesa {firma(n(EST["W"]["peso_max"], 4))}. <strong>El mismo
        vecino vale cinco veces más según a quién esté al lado</strong>, y eso es exactamente lo
        que la estandarización por filas hace: no reparte influencia, la concentra en las unidades
        con pocos vecinos.</p>

      <p><strong>S</strong> es el intento de tener las dos cosas —Tiefelsdorf lo propuso para
        estabilizar la varianza—: divide por la raíz de la suma de cuadrados de la fila y luego
        reescala todo para que el total sea n. <strong>C</strong> reparte un peso igual a todas las
        aristas del mapa, y <strong>U</strong> hace que la matriz entera sume 1.</p>

{sim("cap6-estilos",
     "Los cinco estilos sobre el mismo grafo",
     "Cada botón cambia el estilo. Lo que hay que mirar no es la altura de las barras —van en "
     "escalas distintas a propósito— sino la lectura: la suma total y qué le pasa al rezago de "
     "la misma variable.")}
      <p>La última columna de la tabla es la que cierra el módulo. La correlación entre CRIME y su
        rezago va de {n(EST["B"]["cor_con_crime"], 4)} a {n(EST["W"]["cor_con_crime"], 4)} según el
        estilo: no es un cambio dramático, y por eso es peligroso. <strong>Un estilo mal elegido no
        rompe nada</strong> — mueve la conclusión un poco, en la dirección de lo que uno esperaba, y
        nadie se entera.</p>

{tabs("Los cinco estilos", R7.format(**_SUB7), PY7.format(**_SUB7))}
      <p>Y una asimetría que conviene saber: B, C y U dan <em>exactamente</em> la misma correlación
        —{n(EST["C"]["cor_con_crime"], 4)}— porque los tres son la misma matriz multiplicada por una
        constante, y una constante no mueve una correlación. Los que cambian algo son W y S, que
        son los que tratan a las filas de forma distinta según su grado.</p>
""" + CIERRE

MOD8 = cabecera(
    8, TITULOS[7][0], INGLES[7],
    "Recorrer el flujo completo de `spdep` y ver que `sfdep` es la misma "
    "maquinaria con otra sintaxis.") + f"""
      <p>Todo lo que este capítulo ha explicado se escribe en R con tres llamadas, y siempre en el
        mismo orden. Vale la pena verlas juntas, porque cada una responde a una de las tres
        decisiones del capítulo:</p>

      <ol>
        <li><code>poly2nb</code>, <code>knearneigh</code>, <code>dnearneigh</code>, <code>tri2nb</code>…
          — <strong>quiénes son vecinos</strong>. Todas devuelven un objeto <code>nb</code>, que es
          una lista de listas: para cada unidad, los índices de sus vecinos.</li>
        <li><code>nb2listw</code> — <strong>cuánto pesa cada uno</strong>. Convierte el
          <code>nb</code> en un <code>listw</code> añadiéndole los pesos del estilo elegido.</li>
        <li><code>lag.listw</code> — <strong>qué se hace con eso</strong>. El rezago, que es el
          módulo siguiente.</li>
      </ol>

      <p>La separación entre los dos primeros pasos no es burocracia: es la que permite comparar
        estilos sobre la misma vecindad, y vecindades bajo el mismo estilo, sin recalcular lo que
        no cambia.</p>

{tabs("El flujo completo", R8.format(**_SUB8), PY8.format(**_SUB8))}
      <p><strong><code>sfdep</code> es la misma maquinaria con nombres tidy.</strong>
        <code>st_contiguity</code>, <code>st_weights</code> y <code>st_lag</code> hacen exactamente
        lo mismo que las tres de arriba, encajan en un <code>mutate</code> y devuelven columnas en
        vez de objetos sueltos. Medido: las dos vías cuentan las mismas
        {firma(ent(m8["n_pares_spdep"]), " parejas")} y sus rezagos difieren en
        {firma(n(m8["dif_max"], 4))}.</p>

      <p>Que la diferencia sea cero exacto no es una casualidad afortunada: <code>sfdep</code>
        llama a <code>spdep</code> por debajo. Es una interfaz, no una segunda implementación, y por
        eso <strong>no sirve como comprobación</strong>. La comprobación de verdad de este capítulo
        es la columna de Python: <code>libpysal</code> sí es otra implementación, escrita por otra
        gente, y cuando las dos coinciden la cifra significa algo.</p>
""" + CIERRE


MOD9 = cabecera(
    9, TITULOS[8][0], INGLES[8],
    "Saber qué hace R con una unidad sin vecinos, y por qué la salida "
    "cómoda es la que engaña.") + f"""
      <p>Los criterios de contigüidad tienen un caso que los de k vecinos no: <strong>alguien
        puede quedarse sin ninguno</strong>. No es una patología rara ni hay que fabricarla — el
        dato colombiano la trae puesta.</p>

      <p>Con contigüidad reina, {firma(ent(m9["islas"]), " de los 1 122 municipios")} no tocan a
        nadie: {firma(", ".join(m9["islas_nombre"]))}, las dos del archipiélago de San Andrés. Y el
        mapa se parte en {firma(ent(m9["subgrafos"]), " subgrafos")}, de tamaños
        {" · ".join(ent(t) for t in m9["tamanos_subgrafo"])}: el continente, y cada isla por su
        cuenta.</p>

      <h3>Lo primero que hace R es lo correcto: fallar</h3>

      <p><code>nb2listw</code> sobre una vecindad con islas <strong>se niega</strong>, con el
        mensaje <code>{m9["error_sin_zero_policy"]}</code>. Y tiene razón: la fila de una unidad sin
        vecinos no tiene media, así que un peso estandarizado por filas no existe para ella. Dividir
        por cero es la operación, y R prefiere parar.</p>

      <p>La salida es <code>zero.policy = TRUE</code>, y ahí empieza lo que este módulo quiere que
        se sepa. <strong>No arregla el problema: lo convierte en un cero.</strong> La fila se queda
        vacía, así que el rezago de San Andrés vale {firma(n(m9["lag_isla"], 4))} — que
        <em>no es lo mismo</em> que «San Andrés no tiene rezago».</p>

{tabs("Las islas y su política", R9.format(**_SUB9), PY9.format(**_SUB9))}
      <h3>Por qué ese cero engaña</h3>

      <p>Un cero es un número, y los números entran en las medias. Si el rezago de las islas vale
        cero y la variable no está centrada, esas unidades <strong>tiran de cualquier resumen hacia
        abajo</strong> sin que nada lo avise: la media del rezago baja, la correlación entre el
        dato y su rezago baja, y el índice de Moran del capítulo 7 —que es esa correlación con otro
        nombre— baja también.</p>

      <p>Las tres salidas honestas, y las tres hay que escribirlas:</p>

      <ul>
        <li><strong>Quitar las islas del análisis</strong> y decir cuántas eran. Es lo que hace el
          módulo siguiente: el rezago se calcula sobre el subconjunto con dato y con vecinos.</li>
        <li><strong>Cambiar de criterio</strong>, a k vecinos o a un umbral largo. Resuelve la
          aritmética y crea otro problema: San Andrés acaba siendo vecino de la costa a
          {n(m5["municipios"]["umbral_sin_islas_km"], 0)} km de mar. Una vecindad que no significa
          nada da un número que tampoco.</li>
        <li><strong>Analizar cada componente por separado</strong>, que es lo correcto cuando los
          subgrafos son grandes y no dos puntos en el Caribe.</li>
      </ul>

      <p>Lo que no es una salida es <code>zero.policy = TRUE</code> a secas, sin decirlo. Es la
        familia de defectos de todo este material: <strong>la operación que devuelve algo plausible
        en vez de fallar</strong>.</p>
""" + CIERRE

MOD10 = cabecera(
    10, TITULOS[9][0], INGLES[9],
    "Calcular el rezago espacial, leerlo como lo que es —una media de "
    "vecinos— y ver que suaviza.") + f"""
      <p>Con la vecindad elegida y los pesos puestos, la operación que da sentido a todo es una
        multiplicación: <strong>Wy</strong>. Para cada unidad, la media de sus vecinos.</p>

      <p>Es la pieza sobre la que se construye el resto del curso. El índice de Moran del capítulo 7
        es la correlación entre <em>y</em> y <em>Wy</em>; los modelos del capítulo 8 meten
        <em>Wy</em> como una variable más. Vale la pena entenderlo aquí, donde todavía es solo una
        media.</p>

      <p>Sobre la deserción municipal, calculado sobre los
        {firma(ent(m10["n"]), " municipios con dato")} —quitando las
        {ent(m10["islas_en_el_subconjunto"])} islas, que es la primera de las tres salidas del
        módulo anterior— la correlación entre la deserción de un municipio y la media de sus
        vecinos es {firma(n(m10["correlacion"], 4))}. <strong>Lo cercano se parece</strong>, y esa
        frase acaba de dejar de ser una intuición para ser una cifra.</p>

{sim("cap6-rezago",
     "El dato y su rezago, lado a lado",
     "Las dos barras son la misma variable: la deserción tal cual y la media de los vecinos "
     "de cada municipio. Lo que hay que mirar no es la media —que apenas se mueve— sino la "
     "desviación típica.")}
      <h3>El rezago contrae, y hay que saberlo antes de dibujarlo</h3>

      <p>La media de la deserción es {n(m10["y"]["media"], 4)} y la de su rezago
        {n(m10["wy"]["media"], 4)}: prácticamente la misma, y tiene que serlo. Pero las
        desviaciones típicas son {firma(n(m10["y"]["sd"], 4))} y {firma(n(m10["wy"]["sd"], 4))}:
        el rezago es un {firma(pct(m10["contraccion_pct"], 2), " más estrecho")}.</p>

      <p>No es un artefacto: <strong>promediar contrae</strong>. La media de varios números está
        más cerca del centro que los números que la forman, y el rezago es exactamente eso hecho
        {ent(m10["n"])} veces. La consecuencia práctica es de mapa: si se dibujan
        <em>y</em> y <em>Wy</em> con la misma escala de color, el segundo <strong>siempre</strong>
        se ve más plano, y eso no dice nada sobre el territorio — dice que uno es un promedio del
        otro.</p>

{tabs("El rezago espacial", R10.format(**_SUB10), PY10.format(**_SUB10))}
      <p>Y una advertencia que el capítulo 7 va a cobrar: esa correlación de
        {n(m10["correlacion"], 4)} <strong>depende de la W que se eligió</strong>. Con la torre, con
        k = 4 o con un umbral de {ent(m5["municipios"]["curva"][0]["umbral_km"])} km sale otra, y
        ninguna es la verdadera. El índice de Moran hereda entera esa dependencia, y por eso este
        capítulo va antes que aquel.</p>
""" + CIERRE

MOD11 = cabecera(
    11, TITULOS[10][0], INGLES[10],
    "Ver W como la matriz de adyacencia de un grafo, y reconocer el rezago "
    "como el paso de mensajes de una red neuronal sobre grafos.") + f"""
      <p>Todo lo que este capítulo ha construido tiene otro nombre en otra disciplina, y merece la
        pena decirlo porque es literalmente lo mismo. <strong>W es la matriz de adyacencia de un
        grafo</strong>: los nodos son las unidades, las aristas son las vecindades y los pesos son
        lo que en teoría de grafos se llama, sin más, pesos.</p>

      <p>Lo primero que eso explica es la forma de la matriz. Columbus tiene
        {firma(ent(_C11["casillas"]), " casillas")} y solo
        {firma(ent(_C11["no_ceros"]))} están ocupadas: un
        {firma(pct(_C11["densidad_pct"], 2))}. En los municipios la densidad baja a
        {firma(pct(m11["municipios"]["densidad_pct"], 4))}. <strong>W es dispersa siempre</strong>,
        y por eso <code>spdep</code> no guarda una matriz sino listas de vecinos: una matriz densa
        de 1 122 × 1 122 son {ent(m11["municipios"]["casillas"])} números para guardar
        {ent(m11["municipios"]["no_ceros"])}.</p>

      <h3>Estandarizar por filas es normalizar por el grado</h3>

      <p>La segunda cosa que el lenguaje de grafos hace evidente es qué era el estilo W del módulo
        7. Si <strong>A</strong> es la adyacencia binaria y <strong>D</strong> la diagonal de los
        grados, la matriz estandarizada por filas es exactamente
        <strong>D<sup>−1</sup>A</strong>. No se parece: <em>es</em>. El precálculo lo comprueba y la
        diferencia máxima entre las dos matrices vale {firma(n(_C11["d_inv_a_igual_w"], 0))}.</p>

      <p>Y el rezago del módulo 10 es el producto <strong>W y</strong>, con la misma diferencia
        máxima de {firma(n(_C11["lag_es_producto"], 0))} entre calcularlo con
        <code>lag.listw</code> y multiplicar las matrices a mano.</p>

{tabs("W como matriz", R11.format(**_SUB11), PY11.format(**_SUB11))}
      <h3>Y eso es una capa de una red neuronal sobre grafos</h3>

      <p>Quien haya visto redes neuronales sobre grafos acaba de reconocer la fórmula. Una capa de
        <em>paso de mensajes</em> hace, en su versión más simple, esto: cada nodo recibe la media de
        lo que tienen sus vecinos, y con eso actualiza su propio valor. En notación de GNN,
        <strong>H′ = σ(D<sup>−1</sup>A H W)</strong>, donde lo de dentro es <em>exactamente</em> el
        rezago espacial de este capítulo.</p>

      <p>La correspondencia no es una analogía bonita, y tiene dos consecuencias concretas:</p>

      <ul>
        <li><strong>Apilar capas es subir de orden.</strong> Dos capas de paso de mensajes miran a
          los vecinos de los vecinos, que es la contigüidad de orden 2 del módulo 3 — con la misma
          trampa: no acumula sola, hay que decidir si se acumula.</li>
        <li><strong>La elección de W es la elección de la arquitectura.</strong> Lo que en este
          capítulo es «reina o k = 4» allí es qué aristas tiene el grafo, y allí también se elige y
          casi nunca se justifica.</li>
      </ul>

      <p>Con esto el capítulo tiene sus piezas: qué es un vecino, cuánto pesa, qué se hace con eso y
        qué pasa cuando alguien no tiene ninguno. El capítulo siguiente hace la única pregunta que
        faltaba — <em>¿lo cercano se parece más de lo que cabría esperar por azar?</em>— y va a
        descubrir que la respuesta depende de la W que se eligió aquí.</p>
""" + CIERRE


MOD12 = cabecera(
    12, TITULOS[11][0], INGLES[11],
    "Comprobar lo aprendido y practicar sobre un mapa que el capítulo no "
    "ha usado, que es donde se ve si el método viaja.") + f"""
      <p>El capítulo ha defendido una sola idea desde el módulo 2, y conviene decirla entera antes
        de comprobarla: <strong>W no viene con el dato, la elige quien analiza</strong>, y cambiarla
        cambia todo lo que se calcule después. Los once módulos han ido enseñando cuántas formas hay
        de elegirla y qué se gana y se pierde con cada una.</p>

      <p>Trece preguntas, sin nota. Cada opción trae su explicación, así que equivocarse aquí vale
        tanto como acertar.</p>

{quiz_html("cap6-quiz", "Autoevaluación del capítulo 6",
           "Trece preguntas sobre vecindad, pesos, islas y rezago.")}
      <p>Y cinco ejercicios guiados con su solución calculada. <strong>Ninguno usa Columbus ni los
        municipios</strong>: los cinco trabajan sobre los 100 condados de <code>nc</code>, el mapa
        de Carolina del Norte que los capítulos 1 y 3 ya usaron para otra cosa. La razón es la de
        siempre en este material — un hallazgo que solo aparece donde te lo enseñaron es una
        anécdota; encontrarlo en otro mapa es lo que lo convierte en método.</p>
{EJ}
      <p>Con esto el capítulo cierra sus piezas: qué es un vecino, cuánto pesa cada uno, qué se hace
        con eso y qué pasa cuando alguien no tiene ninguno.</p>

      <div class="tip-box">
        <h4>Dónde sigue esto</h4>
        <p style="margin-bottom:0;">El <strong>capítulo 7</strong> hace la única pregunta que falta
          —<em>¿lo cercano se parece más de lo que cabría esperar por azar?</em>— y su respuesta va a
          depender, entera, de la W que se haya elegido aquí: el índice de Moran es la correlación
          entre <em>y</em> y <em>Wy</em>, así que hereda esta decisión completa. Los anteriores son
          <a href="capitulo-1-datos-espaciales.html">Datos espaciales y la primera ley de la
          geografía</a>, <a href="capitulo-2-crs-georreferenciacion.html">SIG, sistemas de
          referencia y georreferenciación</a>,
          <a href="capitulo-3-cartografia-maup.html">Cartografía estadística y el MAUP</a> —de donde
          viene el aviso de que la unidad de agregación es una decisión—,
          <a href="capitulo-4-patrones-puntuales.html">Patrones puntuales</a> y
          <a href="capitulo-5-intensidad-nucleos.html">Intensidad por núcleos</a>, que son los dos
          capítulos donde lo aleatorio era la posición y no el valor.</p>
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
    + "    const DATOS_CAP6 = " + json.dumps(D, ensure_ascii=False) + ";\n"
    + "    const SOL_CAP6 = " + json.dumps(SOL, ensure_ascii=False) + ";\n"
    + "    const D6 = DATOS_CAP6;\n"
)


def _etq(texto):
    return ",\n      etiqueta: " + json.dumps(texto, ensure_ascii=False)


def geomapa(ident, clave, extra=""):
    return (f"    GEOMAPAS['{ident}'] = {{\n      fuente: MAPAS_CAP6["
            + json.dumps(clave, ensure_ascii=False) + "]" + extra + "\n    };\n")


TABLA_W = """, tabla: function () {
        const cs = D6.m2.criterios;
        const filas = cs.map(c =>
          `<tr><th scope="row">${c.etiqueta}</th>`
          + `<td>${mil6(c.pares)}</td><td>${mil6(c.enlaces)}</td>`
          + `<td>${n6(c.grado)}</td><td>${mil6(c.islas)}</td>`
          + `<td>${mil6(c.subgrafos)}</td></tr>`).join('');
        return `<table><caption>Los diez criterios sobre los mismos `
          + `${mil6(D6.m2.n)} barrios de Columbus. «Parejas» cuenta {i, j} y `
          + `«enlaces» cuenta i \u2192 j: en una vecindad asim\u00e9trica no son `
          + `el doble uno del otro.</caption>`
          + `<thead><tr><th scope="col">Criterio</th><th scope="col">Parejas</th>`
          + `<th scope="col">Enlaces</th><th scope="col">Grado medio</th>`
          + `<th scope="col">Islas</th><th scope="col">Subgrafos</th></tr></thead>`
          + `<tbody>${filas}</tbody></table>`;
      }"""


GEOMAPAS_JS = (
    "    const MAPAS_CAP6 = " + json.dumps(M, ensure_ascii=False) + ";\n"
    + geomapa("cap6-w", "cap6-w", _etq(
        "Los 49 barrios de Columbus con el grafo del criterio de vecindad elegido: "
        "cada línea une dos unidades que ese criterio considera vecinas, y un punto rojo "
        "es una unidad que se ha quedado sin ninguna.") + TABLA_W)
    + geomapa("cap6-municipios", "cap6-municipios", _etq(
        "Los 1 122 municipios de Colombia unidos por contigüidad reina: 3 285 parejas, "
        "grado medio 5,86 y dos municipios sin vecinos, San Andrés y Providencia, "
        "dibujados en rojo."))
)


# =====================================================================
# EL PREÁMBULO DE JAVASCRIPT DEL CAPÍTULO
#
# `n6`, la paleta y las fábricas de control NO las trae la plantilla: las
# define cada capítulo. Darlas por hechas costó en el capítulo 2 un
# `ReferenceError` que se llevó por delante `iniciarSimuladores()` ENTERO
# —no el simulador que fallaba: todos, porque el bucle no atrapa— y en el
# 5 dejó su único simulador muerto desde que se escribió (A.13 nº 4 y
# A.23.1). Las clases son las de la CASA: `.geomapa-boton`, `.control-slider`.
# =====================================================================
JS_PREAMBULO = r"""
    const n6 = (x, d) => Number(x).toFixed(d == null ? 4 : d);
    const mil6 = x => Math.round(Number(x)).toLocaleString('es-ES').replace(/\./g, ' ');

    const C6 = { verde: '#1a7358', naranja: '#FF6600', gris: '#8a8a8a',
                 azul: '#0072B2', rojo: '#D55E00', morado: '#7B3FA0',
                 verdeSuave: 'rgba(26,115,88,0.18)' };

    function lectura6(raiz, pares) {
      const caja = raiz.querySelector('.simulador-lectura');
      if (!caja) return;
      caja.innerHTML = pares.map(p =>
        `<span class="lectura-item"><span class="lectura-etiqueta">${p[0]}</span>` +
        `<span class="lectura-valor">${p[1]}</span></span>`).join('');
    }

    function botonera6(raiz, ops, alPulsar, activo) {
      const cont = raiz.querySelector('.simulador-controles');
      if (!cont) return;
      const ini = Math.max(0, activo || 0);
      cont.innerHTML = ops.map((o, i) =>
        `<button type="button" class="geomapa-boton${i === ini ? ' activo' : ''}" ` +
        `data-i="${i}">${o}</button>`).join('');
      cont.addEventListener('click', e => {
        const b = e.target.closest('.geomapa-boton');
        if (!b) return;
        cont.querySelectorAll('.geomapa-boton').forEach(x => x.classList.remove('activo'));
        b.classList.add('activo');
        alPulsar(+b.dataset.i);
      });
    }

    function deslizador6(raiz, opciones, etiqueta, iniPos, alCambiar) {
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

    // El gráfico de la casa, con los ejes que este capítulo usa siempre.
    function grafico6(raiz, tipo, data, opciones) {
      const cv = raiz.querySelector('canvas');
      if (!cv || typeof Chart === 'undefined') return null;
      return new Chart(cv.getContext('2d'), {
        type: tipo, data,
        options: Object.assign({
          // `animation: false` NO es una preferencia de estilo: es la
          // diferencia entre que el gráfico se dibuje y que no. Con la
          // animación puesta, Chart.js aplaza el primer trazo a un
          // fotograma que en este montaje —el módulo se clona de una
          // plantilla y se inserta— no llega a pintar nunca: la
          // instancia existe, tiene sus datos y sus ejes, y el lienzo se
          // queda con CERO píxeles. Se vio midiendo la tinta, no mirando.
          responsive: true, maintainAspectRatio: false, animation: false,
          plugins: { legend: { labels: { filter: it => it.text !== '' } } }
        }, opciones || {})
      });
    }

    // El mapa de un módulo, para que un simulador pueda repintarlo sin
    // recrearlo: la plantilla expone `raiz.__geomapa.dibuja(opciones)`.
    function repintaGeomapa(ident, opciones) {
      const g = document.querySelector(`[data-geomapa="${ident}"]`);
      if (g && g.__geomapa) g.__geomapa.dibuja(opciones);
    }
"""

SIMULADORES_JS = JS_PREAMBULO + r"""
    // --- Módulo 2 · el constructor de W ------------------------------
    SIMULADORES['cap6-constructor'] = function (raiz) {
      const cs = D6.m2.criterios, hs = D6.m2.histograma;
      let i = 0;
      const g = grafico6(raiz, 'bar',
        { labels: hs[0].conteo.map((_, k) => String(k)),
          datasets: [{ label: 'unidades con ese número de vecinos',
                       data: hs[0].conteo, backgroundColor: C6.verde }] },
        { scales: { y: { beginAtZero: true, title: { display: true, text: 'unidades' } },
                    x: { title: { display: true, text: 'vecinos' } } } });
      const pinta = () => {
        const c = cs[i], h = hs[i];
        if (g) { g.data.datasets[0].data = h.conteo; g.update(); }
        repintaGeomapa('cap6-w', { variante: c.id });
        lectura6(raiz, [
          ['criterio', c.etiqueta],
          ['parejas', mil6(c.pares)],
          ['enlaces dirigidos', mil6(c.enlaces)],
          ['grado medio', n6(c.grado)],
          ['grados', c.grado_min + ' a ' + c.grado_max],
          ['simétrica', c.simetrica ? 'sí' : 'NO'],
          ['islas', mil6(c.islas)],
          ['subgrafos', mil6(c.subgrafos)]]);
      };
      botonera6(raiz, cs.map(c => c.etiqueta), k => { i = k; pinta(); }, 0);
      pinta();
      return g ? [g] : [];
    };

    // --- Módulo 3 · contigüidad y órdenes ----------------------------
    SIMULADORES['cap6-ordenes'] = function (raiz) {
      const m3 = D6.m3;
      const vistas = [
        { etq: 'Reina', d: m3.reina },
        { etq: 'Torre', d: m3.torre },
        { etq: 'Orden 1', d: m3.ordenes[0] },
        { etq: 'Orden 2', d: m3.ordenes[1] },
        { etq: 'Orden 3', d: m3.ordenes[2] }];
      let i = 0;
      const g = grafico6(raiz, 'bar',
        { labels: vistas.map(v => v.etq),
          datasets: [{ label: 'parejas distintas',
                       data: vistas.map(v => v.d.pares),
                       backgroundColor: vistas.map((_, k) => k === 0 ? C6.naranja : C6.verde) }] },
        { scales: { y: { beginAtZero: true, title: { display: true, text: 'parejas' } } } });
      const pinta = () => {
        if (g) {
          g.data.datasets[0].backgroundColor = vistas.map((_, k) =>
            k === i ? C6.naranja : C6.verdeSuave);
          g.update();
        }
        const d = vistas[i].d;
        lectura6(raiz, [
          ['vista', vistas[i].etq],
          ['parejas', mil6(d.pares)],
          ['grado medio', n6(d.grado)],
          ['grado máximo', mil6(d.grado_max)],
          ['densidad de W', n6(d.densidad_pct, 3) + ' %']]);
      };
      botonera6(raiz, vistas.map(v => v.etq), k => { i = k; pinta(); }, 0);
      pinta();
      return g ? [g] : [];
    };

    // --- Módulo 4 · k vecinos ----------------------------------------
    SIMULADORES['cap6-knn'] = function (raiz) {
      const ks = D6.m4.columbus;
      let i = 2;
      const g = grafico6(raiz, 'bar',
        { labels: ks.map(k => 'k = ' + k.k),
          datasets: [
            { label: 'parejas distintas', data: ks.map(k => k.pares),
              backgroundColor: C6.verde },
            { label: 'pares NO recíprocos', data: ks.map(k => k.asimetricos),
              backgroundColor: C6.naranja }] },
        { scales: { y: { beginAtZero: true, title: { display: true, text: 'pares' } } } });
      const pinta = () => {
        const k = ks[i];
        lectura6(raiz, [
          ['k', mil6(k.k)],
          ['enlaces dirigidos', mil6(k.enlaces)],
          ['parejas distintas', mil6(k.pares)],
          ['pares no recíprocos', mil6(k.asimetricos)],
          ['grado', n6(k.grado, 0)],
          ['simétrica', k.simetrica ? 'sí' : 'NO'],
          ['subgrafos', mil6(k.subgrafos)]]);
      };
      deslizador6(raiz, ks.map(k => [k.k, 'k = ' + k.k]),
                  'vecinos más próximos', i, k => { i = k; pinta(); });
      pinta();
      return g ? [g] : [];
    };

    // --- Módulo 5 · el umbral ----------------------------------------
    SIMULADORES['cap6-umbral'] = function (raiz) {
      const cu = D6.m5.columbus.curva;
      let i = 3;
      const g = grafico6(raiz, 'bar',
        { labels: cu.map(c => n6(c.umbral, 2)),
          datasets: [
            { label: 'parejas unidas', data: cu.map(c => c.pares),
              backgroundColor: C6.verde },
            { label: 'unidades sin vecinos', data: cu.map(c => c.islas),
              backgroundColor: C6.naranja }] },
        { scales: { y: { beginAtZero: true, title: { display: true, text: 'unidades' } },
                    x: { title: { display: true, text: 'umbral de distancia' } } } });
      const pinta = () => {
        const c = cu[i];
        lectura6(raiz, [
          ['umbral', n6(c.umbral, 4)],
          ['parejas', mil6(c.pares)],
          ['grado medio', n6(c.grado)],
          ['unidades sin vecinos', mil6(c.islas)],
          ['subgrafos', mil6(c.subgrafos)],
          ['¿una sola pieza?', c.subgrafos === 1 ? 'sí' : 'NO']]);
      };
      deslizador6(raiz, cu.map(c => [c.umbral, n6(c.umbral, 3)]),
                  'umbral de distancia', i, k => { i = k; pinta(); });
      pinta();
      return g ? [g] : [];
    };

    // --- Módulo 7 · los cinco estilos --------------------------------
    SIMULADORES['cap6-estilos'] = function (raiz) {
      const es = D6.m7.estilos;
      const nom = { B: 'B · binaria', W: 'W · por filas', S: 'S · estabilizada',
                    C: 'C · global', U: 'U · unitaria' };
      let i = 1;
      const g = grafico6(raiz, 'bar',
        { labels: es.map(e => nom[e.id]),
          datasets: [{ label: 'correlación del rezago con CRIME',
                       data: es.map(e => e.cor_con_crime),
                       backgroundColor: es.map((_, k) => k === i ? C6.naranja : C6.verdeSuave) }] },
        { scales: { y: { beginAtZero: true,
                         title: { display: true, text: 'correlación con CRIME' } } } });
      const pinta = () => {
        if (g) {
          g.data.datasets[0].backgroundColor = es.map((_, k) =>
            k === i ? C6.naranja : C6.verdeSuave);
          g.update();
        }
        const e = es[i];
        lectura6(raiz, [
          ['estilo', nom[e.id]],
          ['suma de toda W', n6(e.suma_total)],
          ['peso del vecino de la unidad de grado ' + D6.m7.unidad_max.grado, n6(e.peso_max)],
          ['peso del de la de grado ' + D6.m7.unidad_min.grado, n6(e.peso_min)],
          ['media del rezago', n6(e.lag_medio)],
          ['correlación con CRIME', n6(e.cor_con_crime)]]);
      };
      botonera6(raiz, es.map(e => nom[e.id]), k => { i = k; pinta(); }, i);
      pinta();
      return g ? [g] : [];
    };

    // --- Módulo 10 · el dato y su rezago -----------------------------
    SIMULADORES['cap6-rezago'] = function (raiz) {
      const m = D6.m10;
      const g = grafico6(raiz, 'bar',
        { labels: ['media', 'desviación típica'],
          datasets: [
            { label: 'la deserción', data: [m.y.media, m.y.sd], backgroundColor: C6.verde },
            { label: 'su rezago Wy', data: [m.wy.media, m.wy.sd], backgroundColor: C6.naranja }] },
        { scales: { y: { beginAtZero: true, title: { display: true, text: '% de deserción' } } } });
      lectura6(raiz, [
        ['municipios con dato', mil6(m.n)],
        ['media de y', n6(m.y.media)],
        ['media de Wy', n6(m.wy.media)],
        ['desviación de y', n6(m.y.sd)],
        ['desviación de Wy', n6(m.wy.sd)],
        ['contracción', n6(m.contraccion_pct, 2) + ' %'],
        ['correlación y con Wy', n6(m.correlacion)]]);
      return g ? [g] : [];
    };
"""

QUIZ_JS = r"""
    AUTOEVALUACIONES['cap6-quiz'] = [
      {
        tipo: 'opcion',
        pista: 'Piensa en qué cambiaría entre dos realizaciones del mismo proceso.',
        pregunta: 'En un dato de área —municipios, condados, barrios—, ¿qué es lo aleatorio?',
        opciones: [
          { texto: 'El valor que toma cada unidad, porque las unidades están fijas', correcta: true,
            retro: 'Eso es. Un municipio no se mueve entre dos realizaciones: lo que cambia es lo que lleva dentro. Por eso la pregunta deja de ser «¿por qué aquí?» y pasa a ser «¿por qué este valor aquí y no el de al lado?».' },
          { texto: 'La posición de las unidades, como en un patrón puntual',
            retro: 'Eso es un patrón puntual, que es el capítulo 4. Allí lo aleatorio es dónde caen los puntos; aquí las unidades vienen dibujadas de antemano por alguien.' },
          { texto: 'El número de unidades',
            retro: 'El número lo fija la división administrativa, no el azar. En un patrón puntual sí es aleatorio, y esa es una de las diferencias entre los dos tipos de dato.' },
          { texto: 'Nada: los datos de área son deterministas',
            retro: 'Si no hubiera nada aleatorio no habría nada que inferir. Lo aleatorio es el valor, y el modelo va sobre cómo se relacionan los valores de unidades vecinas.' }
        ] },
      {
        tipo: 'numerica',
        pista: 'Es la cifra canónica de Anselin, y el precálculo para si deja de salir.',
        pregunta: '¿Cuántas parejas de vecinos une la contigüidad REINA sobre los 49 barrios de Columbus?',
        respuesta: D6.m2.criterios[0].pares, tolerancia: 0,
        retroAcierto: 'Son ' + mil6(D6.m2.criterios[0].pares) + ' parejas y ' + mil6(D6.m2.criterios[0].enlaces) + ' enlaces dirigidos, con grado medio ' + n6(D6.m2.criterios[0].grado) + '. Es la cifra que publica Anselin, y por eso el tablero se valida solo.',
        retroFallo: 'Son ' + mil6(D6.m2.criterios[0].pares) + '. Cuidado con confundirlas con los enlaces dirigidos, que son ' + mil6(D6.m2.criterios[0].enlaces) + ': en una vecindad simétrica uno es el doble del otro.'
      },
      {
        tipo: 'opcion',
        pista: 'Fíjate en qué exige cada criterio para considerar que dos unidades se tocan.',
        pregunta: '¿Puede un polígono tener MÁS vecinos por contigüidad torre que por contigüidad reina?',
        opciones: [
          { texto: 'No: la torre está contenida en la reina, siempre', correcta: true,
            retro: 'Exacto. La torre exige compartir un tramo de frontera y la reina se conforma con un punto, así que toda pareja de la torre lo es también de la reina. Sobre Columbus la reina añade ' + mil6(D6.m3.solo_reina) + ' parejas de esquina.' },
          { texto: 'Sí, cuando los polígonos son muy irregulares',
            retro: 'La irregularidad cambia CUÁNTAS parejas de esquina hay, no quién contiene a quién. Un contacto de tramo también es un contacto de punto.' },
          { texto: 'Sí, si la capa tiene errores topológicos',
            retro: 'Con topología rota puede pasar cualquier cosa, pero entonces el problema no es el criterio: es que la capa no representa lo que dice representar.' },
          { texto: 'Depende del sistema de referencia',
            retro: 'El sistema de referencia cambia las coordenadas, no la relación de contacto entre polígonos vecinos.' }
        ] },
      {
        tipo: 'multiple',
        pista: 'Son dos. Piensa en qué significa exactamente «orden 2».',
        pregunta: 'Sobre la contigüidad de orden superior con <code>nblag</code>, marca <strong>todo</strong> lo que es cierto.',
        retroAcierto: 'Las dos: el orden 2 excluye a los que ya eran vecinos de orden 1, y por eso la serie no crece sin parar.',
        retroFallo: 'Las dos ciertas son que el orden 2 excluye a los vecinos de orden 1 y que la serie deja de crecer cuando el mapa se queda sin sitios nuevos.',
        opciones: [
          { texto: 'El orden 2 son los vecinos de los vecinos que NO eran ya vecinos', correcta: true,
            retro: 'Eso es, y es la trampa de lectura del módulo: `nblag` no acumula. Sobre Columbus da ' + mil6(D6.m3.ordenes[0].pares) + ', ' + mil6(D6.m3.ordenes[1].pares) + ' y ' + mil6(D6.m3.ordenes[2].pares) + ' parejas.' },
          { texto: 'La serie de parejas por orden acaba frenándose porque el mapa es finito', correcta: true,
            retro: 'Sí: al tercer orden ya casi no hay unidades nuevas a las que llegar, y por eso el salto de ' + mil6(D6.m3.ordenes[1].pares) + ' a ' + mil6(D6.m3.ordenes[2].pares) + ' es mucho menor que el anterior.' },
          { texto: 'El orden 2 incluye a los vecinos de orden 1',
            retro: 'No los incluye, y suponerlo hace que se cuenten dos veces las mismas parejas. Si se quiere la vecindad acumulada hay que unirlas a mano.' },
          { texto: 'El grado medio de orden 2 es el cuadrado del de orden 1',
            retro: 'No: eso valdría en un grafo infinito sin ciclos. En un mapa real los caminos se solapan y el crecimiento es mucho menor.' }
        ] },
      {
        tipo: 'opcion',
        pista: '¿Ser de los tres más próximos a alguien obliga a que ese alguien lo sea de ti?',
        pregunta: 'Una vecindad de k vecinos más próximos, ¿es simétrica?',
        opciones: [
          { texto: 'No, y por eso sus enlaces dirigidos no son el doble de sus parejas', correcta: true,
            retro: 'Eso es. Con k = 3 sobre Columbus hay ' + mil6(D6.m4.columbus[2].enlaces) + ' enlaces dirigidos pero solo ' + mil6(D6.m4.columbus[2].pares) + ' parejas distintas, porque ' + mil6(D6.m4.columbus[2].asimetricos) + ' pares no son recíprocos.' },
          { texto: 'Sí, siempre: la distancia es simétrica',
            retro: 'La distancia sí lo es; «estar entre los k más cercanos» no. B puede ser de los tres más cercanos a A sin que A lo sea de B, y basta con que B esté en una zona más densa.' },
          { texto: 'Solo si k es par',
            retro: 'La paridad de k no tiene nada que ver. Lo que decide la reciprocidad es cómo esté repartida la densidad de puntos.' },
          { texto: 'Sí, porque `knearneigh` la simetriza sola',
            retro: 'No la simetriza: hay que pedirlo con `make.sym.nb`, y al hacerlo el grado deja de valer k —sube a ' + n6(D6.m4.simetrizada_k3.grado) + ' de media—.' }
        ] },
      {
        tipo: 'numerica',
        pista: 'Cuenta los pares (i, j) en los que j es vecino de i pero i no lo es de j.',
        pregunta: 'Con k = 3 sobre Columbus, ¿cuántos pares NO son recíprocos?',
        respuesta: D6.m4.columbus[2].asimetricos, tolerancia: 0,
        retroAcierto: 'Son ' + mil6(D6.m4.columbus[2].asimetricos) + ' de ' + mil6(D6.m4.columbus[2].enlaces) + ' enlaces. Esa asimetría no es un defecto: es información sobre la densidad del patrón. Lo que hay que saber es que está.',
        retroFallo: 'Son ' + mil6(D6.m4.columbus[2].asimetricos) + '. Se cuentan recorriendo cada enlace i → j y comprobando si existe el j → i.'
      },
      {
        tipo: 'multiple',
        pista: 'Son dos, y la segunda es la que casi nadie declara.',
        pregunta: 'Sobre el umbral mínimo que no deja unidades sin vecinos, marca <strong>todo</strong> lo que es cierto.',
        retroAcierto: 'Las dos: se calcula sin tantear, y quitar las islas no basta para conectar el grafo.',
        retroFallo: 'Las dos ciertas son que se calcula como la mayor distancia al vecino más próximo y que en ese umbral el grafo puede seguir partido.',
        opciones: [
          { texto: 'Es la mayor de las distancias de cada unidad a su vecino más próximo', correcta: true,
            retro: 'Eso es, y por eso no hay que tantearlo: por debajo alguien se queda solo por construcción. Sobre Columbus vale ' + n6(D6.m2.umbral_sin_islas) + '.' },
          { texto: 'En ese umbral el grafo puede seguir teniendo varios subgrafos', correcta: true,
            retro: 'Y los tiene: ' + mil6(D6.m5.columbus.curva[3].subgrafos) + ' sobre Columbus y ' + mil6(D6.m5.municipios.en_el_umbral.subgrafos) + ' sobre los municipios. No tener islas y ser conexo son propiedades distintas.' },
          { texto: 'Garantiza que la información puede viajar entre dos unidades cualesquiera',
            retro: 'Eso es la conexidad, y es justo lo que NO garantiza. Hace falta subir más el umbral, y con él sube el grado medio.' },
          { texto: 'Es el umbral que maximiza la autocorrelación',
            retro: 'No optimiza nada de eso: es una condición sobre las islas, no sobre la variable. De hecho no mira la variable en ningún momento.' }
        ] },
      {
        tipo: 'opcion',
        pista: 'Piensa en cuál impone la condición más exigente para aceptar una pareja.',
        pregunta: 'Entre Delaunay, Gabriel y la vecindad relativa, ¿qué relación hay?',
        opciones: [
          { texto: 'Están anidadas: relativa ⊆ Gabriel ⊆ Delaunay', correcta: true,
            retro: 'Eso es, y el precálculo lo comprueba en vez de citarlo. Sobre Columbus: ' + mil6(D6.m6.columbus[0].pares) + ', ' + mil6(D6.m6.columbus[1].pares) + ' y ' + mil6(D6.m6.columbus[2].pares) + ' parejas.' },
          { texto: 'Son independientes: cada una encuentra parejas que las otras no',
            retro: 'No: cada una es un subconjunto de la anterior. Ninguna añade una pareja que Delaunay no tenga.' },
          { texto: 'Delaunay ⊆ Gabriel ⊆ relativa',
            retro: 'Es al revés. La relativa es la más exigente —no puede haber nadie más cerca de los dos que ellos entre sí— y por eso es la que menos parejas deja.' },
          { texto: 'Todas dan el mismo grafo con distinto nombre',
            retro: 'Dan grados medios de ' + n6(D6.m6.columbus[0].grado) + ', ' + n6(D6.m6.columbus[1].grado) + ' y ' + n6(D6.m6.columbus[2].grado) + ': no es el mismo grafo, es una cadena de subconjuntos.' }
        ] },
      {
        tipo: 'opcion',
        pista: '¿Cuál hace que cada fila de W sume 1?',
        pregunta: 'Quieres que el rezago espacial sea la MEDIA de los vecinos. ¿Qué estilo de <code>nb2listw</code> eliges?',
        opciones: [
          { texto: 'W, la estandarización por filas', correcta: true,
            retro: 'Eso es: divide cada fila por su grado, así que toda fila suma 1 y la matriz entera suma n = ' + mil6(D6.m7.estilos[1].suma_total) + '. Su precio es que el vecino de una unidad con pocos vecinos pesa mucho más.' },
          { texto: 'B, la binaria',
            retro: 'Con B el rezago es la SUMA de los vecinos, no la media, y las unidades del centro pesan más solo por estar rodeadas. La matriz suma ' + mil6(D6.m7.estilos[0].suma_total) + ', que son los enlaces dirigidos.' },
          { texto: 'C, la global',
            retro: 'C reparte un peso igual a todas las aristas del mapa, así que la matriz suma n pero las FILAS no suman 1: una unidad con más vecinos sigue sumando más.' },
          { texto: 'U, la unitaria',
            retro: 'U hace que toda la matriz sume 1, no cada fila. Es una escala global, no una media por unidad.' }
        ] },
      {
        tipo: 'multiple',
        pista: 'Son dos. Piensa en qué le hace una constante a una correlación.',
        pregunta: 'Sobre los estilos B, C y U, marca <strong>todo</strong> lo que es cierto.',
        retroAcierto: 'Las dos: son la misma matriz por una constante, y por eso la correlación del rezago no distingue entre ellos.',
        retroFallo: 'Las dos ciertas son que se diferencian en una constante y que dan la misma correlación del rezago.',
        opciones: [
          { texto: 'Los tres son la misma matriz multiplicada por una constante', correcta: true,
            retro: 'Eso es: B por 1, C por n entre el total y U por uno entre el total. Sus sumas son ' + mil6(D6.m7.estilos[0].suma_total) + ', ' + mil6(D6.m7.estilos[3].suma_total) + ' y ' + mil6(D6.m7.estilos[4].suma_total) + '.' },
          { texto: 'Los tres dan exactamente la misma correlación entre y y su rezago', correcta: true,
            retro: 'Sí: ' + n6(D6.m7.estilos[0].cor_con_crime) + ' los tres, porque una constante no mueve una correlación. Los que sí la cambian son W y S.' },
          { texto: 'Los tres hacen que cada fila sume 1',
            retro: 'Ninguno de los tres lo hace. El que estandariza por filas es W, y por eso es el único cuyo rezago es una media.' },
          { texto: 'Elegir entre ellos cambia la conclusión del análisis',
            retro: 'No la cambia si lo que se calcula es una correlación o un índice de Moran, precisamente porque solo se diferencian en una escala. Sí importa si se lee el valor absoluto del rezago.' }
        ] },
      {
        tipo: 'opcion',
        pista: 'Piensa en qué VALOR queda en la fila de una unidad sin vecinos.',
        pregunta: 'Una capa tiene dos unidades sin vecinos y usas <code>zero.policy = TRUE</code>. ¿Qué acabas de hacer?',
        opciones: [
          { texto: 'Convertir su rezago en un CERO, que entra en todas las medias', correcta: true,
            retro: 'Eso es, y es lo que hay que declarar. Sobre los municipios el rezago de San Andrés vale ' + n6(D6.m9.lag_isla) + ', y ese cero tira hacia abajo de cualquier resumen sin que nada avise.' },
          { texto: 'Excluir esas unidades del análisis',
            retro: 'No las excluye: las deja dentro con una fila vacía. Excluirlas es una decisión distinta —y más honesta— que hay que tomar explícitamente.' },
          { texto: 'Hacer que R estime sus vecinos por interpolación',
            retro: 'R no inventa vecinos en ningún caso. `zero.policy` solo decide si acepta filas vacías o se niega a construir los pesos.' },
          { texto: 'Nada: es una opción de presentación',
            retro: 'Cambia el resultado numérico de todo lo que venga después. Sin ella `nb2listw` falla con «' + D6.m9.error_sin_zero_policy + '», que es lo correcto.' }
        ] },
      {
        tipo: 'opcion',
        pista: 'Piensa en qué le pasa a la varianza cuando promedias.',
        pregunta: 'Dibujas la deserción municipal y su rezago Wy con la misma escala de color. El segundo mapa se ve más plano. ¿Qué significa?',
        opciones: [
          { texto: 'Nada sobre el territorio: promediar contrae, y el rezago es una media', correcta: true,
            retro: 'Eso es. La desviación pasa de ' + n6(D6.m10.y.sd) + ' a ' + n6(D6.m10.wy.sd) + ', un ' + n6(D6.m10.contraccion_pct, 2) + ' % menos, y eso pasaría con cualquier variable. Las medias, en cambio, casi coinciden.' },
          { texto: 'Que la deserción está espacialmente autocorrelacionada',
            retro: 'La autocorrelación se ve en la CORRELACIÓN entre y y Wy —aquí ' + n6(D6.m10.correlacion) + '—, no en que el mapa del rezago se vea plano. Eso último pasaría igual sin autocorrelación ninguna.' },
          { texto: 'Que la W elegida tiene demasiados vecinos',
            retro: 'Más vecinos contraen más, es cierto, pero la contracción existe con cualquier W: es una propiedad de promediar, no de esta vecindad.' },
          { texto: 'Que hay un error en el cálculo del rezago',
            retro: 'Es justo lo contrario: si el mapa del rezago NO se viera más plano habría que sospechar del cálculo.' }
        ] },
      {
        tipo: 'opcion',
        pista: 'Escribe la estandarización por filas con la matriz de grados.',
        pregunta: 'En lenguaje de grafos, la matriz W estandarizada por filas es…',
        opciones: [
          { texto: 'D⁻¹A: la adyacencia normalizada por el grado', correcta: true,
            retro: 'Exacto, y no se parece: ES. El precálculo lo comprueba y la diferencia máxima entre las dos matrices vale ' + n6(D6.m11.columbus.d_inv_a_igual_w, 0) + '. Es también la capa de paso de mensajes de una GNN.' },
          { texto: 'A⁻¹D: el grado normalizado por la adyacencia',
            retro: 'La adyacencia no es invertible en general —es dispersa y tiene filas enteras de ceros si hay islas—, así que esa expresión ni siquiera está definida.' },
          { texto: 'AᵀA: la matriz de coocurrencias',
            retro: 'Eso cuenta caminos de longitud 2 entre unidades, que es otra cosa: se parece más a la contigüidad de orden 2 del módulo 3.' },
          { texto: 'A/n: la adyacencia dividida por el número de unidades',
            retro: 'Eso es el estilo U —dividir por una constante—, no la estandarización por filas. La suma total sería 1 en vez de n.' }
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
                    "<title>Capítulo 6 · Pesos espaciales — Estadística Espacial</title>",
                    "el título")

    doc = reemplaza_region(doc, "    const courseData = {", "\n    };\n", COURSE_DATA,
                           "courseData + DATOS_CAP6", max_lineas=20)

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

    DESTINO.parent.mkdir(parents=True, exist_ok=True)
    # El orden de las opciones se decide en `baraja_opciones.py`: escritas
    # de una en una, las preguntas nacen con la correcta delante.
    doc = baraja_documento(doc, "cap6")

    DESTINO.write_text(doc, encoding="utf-8")

    # --- El recuento, contado y no recordado --------------------------
    marcado = doc[:doc.rindex("\n  <script>")]
    mods = doc.count('<template id="module-')
    sims = marcado.count('data-simulador="')
    mapas = marcado.count('data-geomapa="cap6-')
    bl_r = doc.count('class="language-r"')
    bl_py = doc.count('class="language-python"')
    cifras = doc.count("#&gt;")
    lienzos = marcado.count("<canvas")
    con_alt = sum(1 for c in marcado.split("<canvas")[1:] if "aria-label" in c.split(">")[0])
    kb = DESTINO.stat().st_size / 1024

    print(f"{DESTINO.relative_to(RAIZ)}  {kb:.0f} KB")
    print(f"  {mods} módulos · {sims} simuladores · {mapas} mapas · "
          f"{bl_r} bloques de R y {bl_py} de Python · {cifras} cifras anunciadas")
    print(f"  {lienzos} lienzos, {con_alt} con aria-label")

    problemas = []
    if con_alt != lienzos:
        problemas.append(f"lienzos sin aria-label: {lienzos - con_alt} de {lienzos}")
    if bl_r != bl_py:
        problemas.append(f"bloques descuadrados: {bl_r} de R y {bl_py} de Python")
    if problemas:
        print("\n  PROBLEMAS:")
        for p in problemas:
            print(f"   - {p}")
        return 1

    if MODULOS_ESCRITOS < MODULOS_OBJETIVO:
        print(f"\n  EN CONSTRUCCIÓN: {MODULOS_ESCRITOS} de {MODULOS_OBJETIVO} módulos. "
              "No es publicable todavía.")
        return 1

    print("\n  Capítulo 6 ensamblado.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
