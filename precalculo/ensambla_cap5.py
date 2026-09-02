#!/usr/bin/env python3
"""
ensambla_cap5.py — construye el capítulo 5 del material (T3.5)

Material de Estadística Espacial 2026-II (20929).
«Intensidad por núcleos y modelamiento de procesos puntuales» · semanas 8-10

MISMO REPARTO QUE LOS CAPÍTULOS 1 A 4 (el capítulo 1 es el molde):
  · La **prosa** vive en f-strings y se interpola desde el JSON. Es lo que
    audita `audita_texto_cap5.py`, y `sin_aritmetica.py` vigila que
    ninguna de esas cifras se CALCULE aquí en vez de venir de R.
  · El **JavaScript** no se interpola: recibe el JSON entero como
    `DATOS_CAP5` y saca de ahí sus cifras.
  · Los **mapas** se registran con su JSON literal, salvo la familia del
    deslizador, que es una función — y ahí está la trampa de abajo.

LA DESVIACIÓN DEL MOLDE, DECLARADA (decisión 1 de Javier, 2026-08-28):
**12 preguntas y 5 ejercicios**, como el capítulo 4 y por el mismo motivo:
cubre más de una semana de clase. Aquí, tres.

LO QUE ESTE CAPÍTULO ESTRENA, y va declarado:

  · **Es el primero que publica SUPERFICIES.** Diez rásteres, 606 KB en la
    forma que `geo_rejilla()` escribe. Viajan EMPAQUETADOS —máscara en
    tiradas y valores en diferencias por fila, `rejilla_comprime.py`— y
    bajan a 297 KB, el 49 %. La plantilla estrena su decodificador, y la
    ida y vuelta se comprueba AQUÍ, en Python, antes de escribir nada.
  · **El deslizador busca su superficie POR SU SIGMA, nunca por su
    posición.** El capítulo 1 pagó esta lección dos veces (T1.2 y T1.3) y
    la dejó escrita en su propio código: `campoDePhi()` y
    `realizacionDeId()` existen porque emparejar dos listas por índice las
    descuadró en silencio. Y el capítulo 5 casi la paga una tercera: el
    mismo sigma salía con 8 dígitos en `cap5_mapas.json` y con 10 en
    `cap5_datos.json`, así que la clave no coincidía consigo misma. Se
    arregló redondeando sigma EN EL ORIGEN; aquí se comprueba que las dos
    listas siguen casando antes de escribir el documento.

Y LA REGLA DEL RITMO (§9.1 del plan): ningún módulo abre pidiendo trabajo
· todo componente interactivo va con dos párrafos, el que lo motiva y el
que lo cierra · el encabezado del módulo es un contrato.

Uso:  python3 precalculo/ensambla_cap5.py
      (desde la carpeta `Estadistica espacial/`)
"""
from __future__ import annotations

import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from rejilla_comprime import ida_y_vuelta

RAIZ = pathlib.Path(__file__).resolve().parent.parent
PLANTILLA = RAIZ / "plantilla" / "plantilla-capitulo.html"
SALIDAS = RAIZ / "precalculo" / "salidas"
DESTINO = RAIZ / "Htmls_Espacial" / "capitulo-5-intensidad-nucleos.html"

D = json.loads((SALIDAS / "cap5_datos.json").read_text(encoding="utf-8"))
M = json.loads((SALIDAS / "cap5_mapas.json").read_text(encoding="utf-8"))
S = json.loads((SALIDAS / "cap5_soluciones.json").read_text(encoding="utf-8"))

m1, m2, m3, m4 = D["m1"], D["m2"], D["m3"], D["m4"]
m5, m6, m7, m8 = D["m5"], D["m6"], D["m7"], D["m8"]
m9, m10, m11 = D["m9"], D["m10"], D["m11"]
FAM = m2["familia"]
SEL_K, SEL_U = m3["kennedy"]["sigmas_m"], m3["urbana"]["sigmas_m"]


# =====================================================================
# Formateadores. NO calculan: dan forma a lo que R ya calculó.
# =====================================================================
def n(x, d=5):
    return f"{float(x):.{d}f}"


def ent(x):
    """Entero con espacio fino U+202F. NO usar dentro de KaTeX."""
    return f"{int(round(float(x))):,}".replace(",", " ")


def ent_mate(x):
    return f"{int(round(float(x))):,}".replace(",", r"\,")


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


def sim(ident, titulo, pie="", alto=260):
    return f"""      <div class="simulador" data-simulador="{ident}">
        <h4><i class="fas fa-sliders" aria-hidden="true"></i> {titulo}</h4>
        {f'<p class="simulador-intro">{pie}</p>' if pie else ''}
        <div class="simulador-controles"></div>
        <div class="grafico-wrapper" style="height:{alto}px;">
          <canvas role="img" aria-label="{titulo}"></canvas>
        </div>
        <div class="simulador-lectura"></div>
      </div>
"""


def fila(*celdas):
    cab, resto = celdas[0], celdas[1:]
    return ('            <tr><th scope="row">' + str(cab) + '</th>'
            + ''.join('<td>' + str(c) + '</td>' for c in resto) + '</tr>\n')


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


def mapa_html(ident, titulo, controles=False):
    ctrl = (f'      <div class="geomapa-controles" id="ctrl-{ident}"></div>\n'
            if controles else "")
    return ctrl + f"""      <div class="geomapa" data-geomapa="{ident}">
        <p class="geomapa-titulo">{titulo}</p>
        <div class="geomapa-marco">
          <canvas class="geomapa-lienzo" role="img" aria-label="{titulo}"></canvas>
        </div>
        <div class="geomapa-pie-caja"></div>
      </div>
"""


TITULOS = (
    ("De contar a suavizar", "El estimador núcleo de la intensidad"),
    ("El ancho de banda lo es todo", "El núcleo importa poco"),
    ("Selectores de ancho de banda", "Qué optimiza cada uno"),
    ("Corrección de borde en la KDE", "Y la ventana otra vez"),
    ("La KDE como mapa de calor", "Oferta, cobertura y demanda"),
    ("Intensidad relativa", "Casos, controles y proporción de tipo"),
    ("Covariables", "La intensidad como función de otra cosa"),
    ("El Poisson inhomogéneo", "El modelo y su verosimilitud"),
    ("Ajustar con `ppm`", "Berman-Turner y la lectura de los coeficientes"),
    ("Diagnóstico del ajuste", "Residuos, K inhomogénea y envolventes"),
    ("Conglomerado y autoexcitación", "Thomas, Matérn, Cox y Hawkes"),
    ("Autoevaluación y ejercicios", "Doce preguntas y cinco ejercicios"),
)



# =====================================================================
# LOS BLOQUES DE CÓDIGO VAN APARTE DE LA PROSA, y no es estilo.
#
# Un literal de tres comillas dentro de una f-string de tres comillas la
# CIERRA a media expresión, y el `SyntaxError` sale a doscientas líneas de
# distancia señalando un paréntesis que no tiene nada que ver. Los bloques
# se construyen aquí, con comillas simples triples, y la prosa los recibe
# ya formados. Los `#>` los rellena `.format()` desde el JSON: ninguno se
# escribe a mano, y `verifica_bloques.py` los ejecuta para comprobarlo.
# =====================================================================
R1 = '''library(sf)
library(spatstat)

cole &lt;- st_read(&quot;datos/procesado/bogota_colegios.gpkg&quot;, quiet = TRUE)
loc  &lt;- st_read(&quot;datos/procesado/bogota_localidades.gpkg&quot;, quiet = TRUE)

W  &lt;- as.owin(st_union(st_geometry(loc[loc$localidad == &quot;Kennedy&quot;, ])))
xy &lt;- st_coordinates(cole)
p  &lt;- ppp(xy[, 1], xy[, 2], window = W)   # descarta lo que cae fuera

npoints(p)
#&gt; [1] {N}
round(area.owin(W) / 1e6, 4)              # km2
#&gt; [1] {A}

# El punto de partida del capitulo 4: contar en celdas que no se solapan
cuad &lt;- quadratcount(p, nx = {NX}, ny = {NX})
range(as.numeric(cuad))
#&gt; [1] {CMIN} {CMAX}'''

PY1 = '''import geopandas as gpd
import numpy as np

cole = gpd.read_file(&quot;datos/procesado/bogota_colegios.gpkg&quot;)
loc = gpd.read_file(&quot;datos/procesado/bogota_localidades.gpkg&quot;)

W = loc.loc[loc[&quot;localidad&quot;] == &quot;Kennedy&quot;, &quot;geometry&quot;].union_all()
dentro = cole.geometry.within(W).to_numpy()
px = cole.geometry.x.to_numpy()[dentro]
py = cole.geometry.y.to_numpy()[dentro]

print(len(px))
#&gt; {N}
print(round(W.area / 1e6, 4))
#&gt; {A}

# El mismo conteo con el convenio de cut(): abierto por la izquierda
x0, y0, x1, y1 = W.bounds
nx = {NX}
ix = np.clip(np.searchsorted(np.linspace(x0, x1, nx + 1), px, &quot;left&quot;) - 1, 0, nx - 1)
iy = np.clip(np.searchsorted(np.linspace(y0, y1, nx + 1), py, &quot;left&quot;) - 1, 0, nx - 1)
cnt = np.zeros((nx, nx), int)
np.add.at(cnt, (ix, iy), 1)
print(cnt.min(), cnt.max())
#&gt; {CMIN} {CMAX}'''

_SUB1 = dict(N=ent(m1["ventana"]["n"]).replace(" ", ""),
             A=n(m1["ventana"]["area_km2"], 4),
             NX=str(m1["cuadrantes"]["nx"]),
             CMIN=ent(m1["cuadrantes"]["conteo_min"]),
             CMAX=ent(m1["cuadrantes"]["conteo_max"]))

R2 = '''# El nucleo casi no importa: cuatro pesos distintos, el mismo mapa
sigmas &lt;- c(&quot;gaussian&quot;, &quot;epanechnikov&quot;, &quot;quartic&quot;, &quot;disc&quot;)
maximos &lt;- sapply(sigmas, function(k)
  max(density(p, sigma = {SIG}, kernel = k, dimyx = c({NY}, {NX}))) * 1e6)
round(maximos, 2)
#&gt;     gaussian epanechnikov      quartic         disc
#&gt;   {MAXS}

# El ancho SI importa: el mismo nucleo, siete anchuras
anchos &lt;- c({SIGMAS})
picos  &lt;- sapply(anchos, function(s)
  max(density(p, sigma = s, dimyx = c({NY}, {NX}))) * 1e6)
round(picos, 1)
#&gt; [1] {PICOS}'''

PY2 = '''from scipy.signal import fftconvolve

# Python NO traduce la llamada a spatstat: no hay equivalente. Reimplementa
# la matematica —binar los puntos en la rejilla, convolucionar con el nucleo
# y dividir por la masa que cae dentro de la ventana—, que es lo que
# density.ppp hace por dentro. La correccion de borde va incluida: sin ella
# el pico sale mas bajo y las dos columnas no se podrian comparar.
def kde_pico(px, py, sigma, nx, ny, W):
    x0, y0, x1, y1 = W.bounds
    dx, dy = (x1 - x0) / nx, (y1 - y0) / ny
    xc = x0 + (np.arange(nx) + 0.5) * dx
    yc = y0 + (np.arange(ny) + 0.5) * dy
    X, Y = np.meshgrid(xc, yc)
    mask = gpd.GeoSeries(gpd.points_from_xy(X.ravel(), Y.ravel())).within(W)
    mask = mask.to_numpy().reshape(ny, nx)

    rx, ry = int(np.ceil(4 * sigma / dx)), int(np.ceil(4 * sigma / dy))
    gx, gy = np.arange(-rx, rx + 1) * dx, np.arange(-ry, ry + 1) * dy
    k = np.exp(-(gx[None, :] ** 2 + gy[:, None] ** 2) / (2 * sigma ** 2))
    k /= 2 * np.pi * sigma ** 2

    conteo = np.zeros((ny, nx))
    ix = np.clip(((px - x0) / dx).astype(int), 0, nx - 1)
    iy = np.clip(((py - y0) / dy).astype(int), 0, ny - 1)
    np.add.at(conteo, (iy, ix), 1.0)
    cruda = fftconvolve(conteo, k, mode=&quot;same&quot;)
    e = fftconvolve(mask.astype(float), k, mode=&quot;same&quot;) * dx * dy
    return np.nanmax(np.where((e &gt; 0) &amp; mask, cruda / np.maximum(e, 1e-300), np.nan)) * 1e6

anchos = [{SIGMAS}]
print(round(kde_pico(px, py, anchos[0], {NX}, {NY}, W), 1))
#&gt; {P0}
print(round(kde_pico(px, py, anchos[-1], {NX}, {NY}, W), 1))
#&gt; {P1}'''

_SUB2 = dict(
    SIG=ent(m2["sigma_m"]),
    NX=str(FAM["nx"]), NY=str(FAM["ny"]),
    MAXS="  ".join(n(m2["nucleos"]["max_km2"][k], 2) for k in m2["nucleos"]["nombres"]),
    SIGMAS=", ".join(n(s, 4) for s in FAM["sigmas_m"]),
    PICOS=" ".join(n(v, 1) for v in FAM["max_km2"]),
    P0=n(FAM["max_km2"][0], 1), P1=n(FAM["max_km2"][-1], 1))


# =====================================================================
# MÓDULO 1 · De contar a suavizar
# =====================================================================
_f = m1["frontera"]
_disc = "; ".join(
    f'«{s["nombre"].title()}», que el atributo pone en {s["atributo"]} y la geometría deja '
    f'{"dentro" if s["dentro_geometria"] else "fuera"}, a {n(s["dist_borde_m"], 1)} m del borde'
    for s in _f["sedes"])

MOD1 = cabecera(
    1, "De contar a suavizar", "From counting to smoothing",
    "Entender el estimador núcleo de la intensidad como lo que es: contar, pero "
    "con una vecindad que se solapa y que no tiene bordes rectos.") + f"""
      <p>El capítulo 4 terminó con una intensidad y un veredicto: las sedes educativas de Bogotá
        no están repartidas al azar. Pero aquella intensidad era <em>una sola cifra</em> para
        toda la ciudad, y la pregunta que un mapa invita a hacer no es cuántas sedes hay por
        kilómetro cuadrado en promedio, sino <strong>dónde</strong> hay más y dónde menos.</p>

      <p>El test de cuadrantes ya daba una respuesta a eso: la rejilla parte la ventana y cuenta.
        Lo que hace este capítulo es quitarle a esa respuesta sus dos limitaciones —que las
        celdas no se solapan y que sus bordes son rectos y los puso alguien— sin cambiar la idea
        de fondo.</p>

      <h3>La ventana de trabajo: una localidad</h3>

      <p>Bajamos de la ciudad a <strong>{m1["ventana"]["nombre"]}</strong>. El motivo es técnico
        y el módulo 3 lo explica entero: sobre la ciudad completa, la celda más fina que el mapa
        puede pagar es más ancha que el núcleo más estrecho que querríamos dibujar, y un mapa así
        no dibuja el núcleo — dibuja su propia rejilla. Kennedy es una caja de
        {n(m1["ventana"]["caja_x_km"], 1)} × {n(m1["ventana"]["caja_y_km"], 1)} km con
        {firma(ent(m1["ventana"]["n"]), " sedes")} sobre
        {firma(n(m1["ventana"]["area_km2"], 2), " km²")}, o sea
        {firma(n(m1["ventana"]["lambda_km2"], 2), " sedes por km²")}.</p>

      <div class="nota-lateral">
        <h4>Dos formas de preguntar «¿está en Kennedy?», y no dan lo mismo</h4>
        <p>La capa de sedes trae una columna <code>localidad</code>; la de localidades trae la
          geometría. Por el atributo son {ent(_f["n_atributo"])} sedes, por la geometría
          {ent(_f["n_geometria"])}. Discrepan {ent(_f["n_discrepan"])}, y las tres están a menos
          de {n(_f["dist_max_m"], 0)} m del borde: {_disc}.</p>
        <p>Manda la geometría, porque es la que usa <code>ppp()</code>: la ventana de un patrón
          puntual es un objeto geométrico y no admite otra respuesta. Pero la discrepancia no se
          esconde, porque es la lección del capítulo 2 y del 3 vista desde un tercer sitio:
          <strong>un borde es una decisión, y cerca de él la respuesta depende de a quién se le
          pregunte</strong>.</p>
      </div>

{mapa_html("cap5-kennedy", "Kennedy: las 262 sedes educativas dentro de la ventana")}
      <p class="pie-figura">La ventana no es la caja: es el contorno de la localidad, con sus
        entrantes y su borde irregular. Todo lo que este capítulo estime —cada superficie, cada
        corrección de borde, cada integral— se hace contra esta forma y no contra el rectángulo
        que la contiene.</p>

      <p>Con la ventana puesta, el punto de partida es el del capítulo anterior. Sobre una
        rejilla de {m1["cuadrantes"]["nx"]} × {m1["cuadrantes"]["nx"]} celdas, la más vacía tiene
        {ent(m1["cuadrantes"]["conteo_min"])} sedes y la más llena
        {ent(m1["cuadrantes"]["conteo_max"])}: entre
        {n(m1["cuadrantes"]["intensidad_min_km2"], 1)} y
        {n(m1["cuadrantes"]["intensidad_max_km2"], 1)} sedes por km².</p>

{tabs("La ventana de Kennedy y su conteo por cuadrantes", R1.format(**_SUB1), PY1.format(**_SUB1))}
      <p>Ese cuadro tiene dos cosas que molestan y una que no. La que no: es una estimación
        honesta de la intensidad local. Las que molestan: la rejilla la puso alguien —moverla
        media celda cambia los conteos, que es el MAUP del capítulo 3 otra vez— y una sede al
        otro lado de una línea no aporta nada a la celda vecina, aunque esté a diez metros.</p>

      <p>El estimador por núcleos arregla las dos con una sola idea: en vez de contar cuántos
        puntos caen dentro de una caja, <strong>sumar cuánto pesa cada punto</strong> según lo
        lejos que esté del sitio donde miramos. El peso lo pone una función que decae con la
        distancia —el núcleo— y su anchura, σ, ocupa el lugar del tamaño de celda.</p>

      <div class="formula-destacada">
        $$\\hat\\lambda(u) \;=\; \\frac{{1}}{{e(u)}} \\sum_{{i=1}}^{{n}} k_\\sigma\\!\\left(u - x_i\\right)$$
      </div>

      <p>El término $e(u)$ es la corrección de borde, y tiene el módulo 4 para él solo. Por ahora
        basta con saber por qué existe: la ventana corta el núcleo de los puntos cercanos al
        perímetro, y sin corregir esa masa se pierde por el borde.</p>
""" + CIERRE


# =====================================================================
# MÓDULO 2 · El ancho de banda lo es todo
# =====================================================================
_nuc = m2["nucleos"]
_cor_min = min(_nuc["cor_con_gaussiano"].values())

MOD2 = cabecera(
    2, "El ancho de banda lo es todo", "The kernel matters little",
    "Medir cuánto cambia el mapa al cambiar de núcleo y cuánto al cambiar de "
    "ancho, y comprobar que no juegan en la misma liga.") + f"""
      <p>Elegir un estimador por núcleos son dos decisiones: qué función de peso usar y con qué
        anchura. Suenan igual de importantes y no lo son, ni de lejos. Este módulo mide las dos
        sobre el mismo patrón, para que la diferencia se vea en una cifra en vez de creerse.</p>

      <h3>Primero el núcleo, que es la decisión que no importa</h3>

      <p>Con σ = {ent(m2["sigma_m"])} m fijo, cambiar entre los cuatro núcleos habituales mueve
        la intensidad máxima del mapa un {firma(pct(_nuc["max_dif_pct"]))}. Las superficies
        correlacionan por encima de {n(_cor_min, 3)} con la gaussiana: son, a efectos de lo que
        un lector ve, el mismo mapa.</p>

      <table class="tabla-datos">
        <caption>Los cuatro núcleos al mismo σ = {ent(m2["sigma_m"])} m sobre Kennedy</caption>
        <thead><tr><th scope="col">Núcleo</th><th scope="col">Intensidad máxima (por km²)</th>
          <th scope="col">Correlación con el gaussiano</th></tr></thead>
        <tbody>
""" + "".join(
    fila(k, n(_nuc["max_km2"][k], 2),
         "—" if k == "gaussian" else n(_nuc["cor_con_gaussiano"][k], 4))
    for k in _nuc["nombres"]) + f"""        </tbody>
      </table>

      <p><strong>Una advertencia que es la que hace justa la comparación:</strong> «al mismo σ»
        quiere decir a la misma <em>desviación típica</em>, no al mismo soporte. Cada núcleo se
        escala para que su σ sea la pedida; sin esa escala estaríamos comparando anchuras
        distintas, y la tabla demostraría lo contrario de lo que demuestra.</p>

      <h3>Y ahora el ancho, que es la decisión que lo decide todo</h3>

      <p>El mismo patrón, el mismo núcleo, {ent(FAM["n"])} anchuras. La intensidad máxima cae de
        {firma(n(FAM["max_km2"][0], 1), " por km²")} a
        {firma(n(FAM["max_km2"][-1], 1), " por km²")}: un {firma(pct(FAM["caida_pct"]))}, que es
        trece veces lo que movía cambiar de núcleo.</p>

{tabs("El núcleo contra el ancho de banda", R2.format(**_SUB2), PY2.format(**_SUB2))}
      <p>Mueve el deslizador y mira la ciudad, no la cifra: con σ pequeño aparecen focos que son
        colegios concretos; con σ grande queda una sola mancha que no distingue barrios. Ninguno
        de los dos extremos es un error de cálculo — los dos son la misma estimación con otra
        anchura, y por eso el módulo siguiente trata de cómo se elige.</p>

{sim("cap5-anchos", "El pico contra el ancho de banda",
      "El deslizador mueve σ. La curva no se mueve —el ancho ya es su eje—: "
      "lo que se mueve es el punto que marca dónde estás, y el mapa de abajo.")}
{mapa_html("cap5-familia", "Intensidad por núcleos sobre Kennedy, con σ regulable")}
      <p class="pie-figura">Las {ent(FAM["n"])} superficies comparten <strong>una sola escala de
        color</strong>, y eso no es presentación: normalizada cada una contra su propio máximo,
        las siete saldrían igual de intensas y el mapa afirmaría justo lo contrario que la tabla
        de arriba. La celda mide {n(FAM["celda_m"], 0)} m y el σ más estrecho del abanico es
        {n(min(FAM["sigmas_m"]), 0)} m: tres celdas, que es el mínimo para que lo que se vea sea
        el núcleo y no la rejilla.</p>

      <p>Recapitulando lo que este módulo ha medido: cambiar de núcleo mueve el mapa un
        {pct(_nuc["max_dif_pct"])} y cambiar de ancho lo mueve un {pct(FAM["caida_pct"])}. La
        primera decisión se puede tomar por costumbre sin consecuencias; la segunda decide qué
        dice el mapa, y no hay ninguna forma de tomarla sin tomarla.</p>

      <p>Queda entonces la pregunta que este módulo ha estado aplazando: <strong>quién elige
        σ</strong>. R trae cuatro selectores automáticos que contestan por uno, y el módulo
        siguiente enseña que los cuatro contestan cosas distintas —y que uno de ellos, a veces,
        no contesta nada—.</p>
""" + CIERRE


# =====================================================================
# MÓDULO 3 · Selectores de ancho de banda
# =====================================================================
R3 = '''# Los cuatro selectores sobre la MISMA ventana. Cada uno optimiza una
# cosa distinta, asi que discrepar no es un defecto: es lo que son.
sel &lt;- c(diggle = as.numeric(bw.diggle(p)),
         ppl    = as.numeric(bw.ppl(p)),
         CvL    = as.numeric(bw.CvL(p)),
         scott  = as.numeric(bw.scott(p))[1])
round(sel, 4)
#&gt;   diggle      ppl      CvL    scott
#&gt; {SEL}

round(max(sel) / min(sel), 4)          # cuanto discrepan entre si
#&gt; [1] {RAZON}

# EL SELECTOR QUE NO SELECCIONO. R avisa por consola; el valor devuelto
# no delata nada, y 0.7071 es el extremo DERECHO de su propio intervalo.
round(as.numeric(bw.ppl(japanesepines)), 4)
#&gt; [1] {TOPE}'''

PY3 = '''import pandas as pd

# De los cuatro, bw.scott es el unico con forma cerrada: es la regla de
# referencia normal, sd(x) * n^(-1/6) en dos dimensiones. Reimplementarla
# explica de paso por que casi siempre sale la mas ancha —supone que la
# intensidad es una normal, y una ciudad no lo es—.
def scott(v, n):
    return v.std(ddof=1) * n ** (-1 / 6)

ken = pd.read_csv(&quot;precalculo/salidas/cap5_kennedy.csv&quot;)
urb = pd.read_csv(&quot;precalculo/salidas/cap5_bogota_urbana.csv&quot;)

print(round(scott(ken.x, len(ken)), 4))
#&gt; {SCOTT_KEN}
print(round(scott(urb.x, len(urb)), 4))
#&gt; {SCOTT_URB}'''

_SUB3 = dict(
    SEL=" ".join(n(m3["kennedy"]["sigmas_m"][k], 4)
                 for k in ("diggle", "ppl", "CvL", "scott")),
    RAZON=n(m3["kennedy"]["razon"], 4),
    TOPE=n(m3["topes"][0]["sigma"], 4),
    SCOTT_KEN=n(m3["kennedy"]["sigmas_m"]["scott"], 4),
    SCOTT_URB=n(m3["urbana"]["sigmas_m"]["scott"], 4))

_QUE_OPTIMIZA = {
    "diggle": ("<code>bw.diggle</code>",
               "el error cuadrático medio de la intensidad, por validación cruzada "
               "(Berman y Diggle). Mira la superficie."),
    "ppl": ("<code>bw.ppl</code>",
            "la verosimilitud del proceso puntual, dejando fuera un punto cada vez "
            "(Loader). Mira los puntos."),
    "CvL": ("<code>bw.CvL</code>",
            "el criterio de Cronie y van Lieshout: que la suma de "
            "1/λ̂ sobre los puntos devuelva el área de la ventana."),
    "scott": ("<code>bw.scott</code>",
              "nada: es la regla de referencia normal de Scott, "
              "sd·n<sup>−1/6</sup>, en forma cerrada y sin buscar."),
}

_TOPES = "; ".join(
    f'<code>{t["nombre"].split(" sobre ")[0]}</code> sobre <code>{t["nombre"].split(" sobre ")[1]}</code> '
    f'devuelve {n(t["sigma"], 4)}'
    for t in m3["topes"])

MOD3 = cabecera(
    3, "Selectores de ancho de banda", "Bandwidth selectors",
    "Saber qué optimiza cada uno de los cuatro selectores, por qué discrepan y "
    "cómo se reconoce el que no ha seleccionado nada.") + f"""
      <p>Si el ancho de banda lo decide todo, la pregunta siguiente se cae de madura: quién lo
        decide. R trae cuatro selectores automáticos, se llaman parecido y devuelven un número
        cada uno. Lo que este módulo defiende es que <strong>ese número no es «el ancho
        óptimo»</strong>, porque los cuatro optimizan cosas distintas y ninguno optimiza «que el
        mapa se entienda».</p>

      <h3>Qué optimiza cada uno</h3>

      <table class="tabla-datos">
        <caption>Los cuatro selectores sobre las dos ventanas del capítulo, en metros</caption>
        <thead><tr><th scope="col">Selector</th><th scope="col">Qué minimiza o maximiza</th>
          <th scope="col">σ en {m1["ventana"]["nombre"]}</th>
          <th scope="col">σ en la ciudad</th></tr></thead>
        <tbody>
""" + "".join(
    fila(_QUE_OPTIMIZA[k][0], _QUE_OPTIMIZA[k][1],
         n(m3["kennedy"]["sigmas_m"][k], 1), n(m3["urbana"]["sigmas_m"][k], 1))
    for k in ("diggle", "ppl", "CvL", "scott")) + f"""        </tbody>
      </table>

      <p>Sobre {m1["ventana"]["nombre"]} el mayor es {firma(n(m3["kennedy"]["razon"]), " veces")}
        el menor; sobre la ciudad entera, {firma(n(m3["urbana"]["razon"]), " veces")}. Y el
        orden ni siquiera se conserva: en {m1["ventana"]["nombre"]} <code>bw.ppl</code> pide más
        que <code>bw.diggle</code> y en la ciudad pide bastante menos —
        {n(m3["urbana"]["sigmas_m"]["ppl"], 0)} m contra
        {n(m3["urbana"]["sigmas_m"]["diggle"], 0)}—. El mismo dato, el mismo método y cuatro
        respuestas que no convergen al crecer la ventana: <strong>divergen</strong>.</p>

{sim("cap5-selectores", "Los cuatro selectores sobre las dos ventanas",
      "Cambia de ventana y mira dos cosas: cuánto se abre el abanico y si el orden "
      "de los cuatro se conserva. La línea marca el σ mínimo que la rejilla de la "
      "ciudad puede dibujar sin mentir, que es lo que descarta dos de ellos en el módulo 5.")}
      <p>Lo que el abanico enseña no es que alguno esté mal calculado. Es que
        <strong>«el ancho óptimo» no es una propiedad del patrón</strong>: es la respuesta a una
        pregunta que hay que hacer antes, y cada selector hace una distinta. Elegir sin decir
        cuál se eligió es publicar una superficie sin decir qué se le pidió.</p>

      <h3>El selector que no seleccionó</h3>

      <p>Hay un caso peor que discrepar, y es el que este módulo quiere que se sepa reconocer.
        Los tres selectores que buscan lo hacen dentro de un intervalo, y cuando el óptimo cae
        fuera de él <strong>devuelven el extremo</strong>: un número finito, con el aspecto de
        cualquier otro, que no es un óptimo sino una pared. Medidos —el segundo sobre
        <code>bw.relrisk</code>, que no es de los cuatro pero es el selector del módulo 6 y falla
        igual—: {_TOPES}.</p>

      <div class="nota-lateral">
        <h4>Por qué el valor de retorno no delata nada</h4>
        <p>R sí avisa —«criterion was maximised at right-hand end of interval»— pero el aviso va
          a la consola y el número va a la variable. En un guion que calcula veinte cosas, el
          aviso se pierde entre los demás y el número sigue su camino hasta el mapa. Lo que sí
          lo delata es <strong>compararlo con el borde del intervalo de búsqueda</strong>:
          <code>bw.ppl</code> sobre <code>japanesepines</code> devuelve exactamente
          {n(m3["topes"][0]["sigma"], 4)}, que es la mitad del lado de su ventana unitaria y el
          tope por defecto del rango. Un óptimo que coincide con el borde al último decimal no
          es un óptimo.</p>
        <p style="margin-bottom:0;">El ejercicio 1 del módulo 12 pide encontrar el caso entre
          doce, y es exactamente esta comprobación.</p>
      </div>

{tabs("Los cuatro selectores, y el que choca con su intervalo", R3.format(**_SUB3), PY3.format(**_SUB3))}
      <p>La consecuencia práctica llega en el módulo 5, y no es teórica: sobre la ciudad entera
        el mapa se dibuja en una rejilla que solo puede representar núcleos de al menos
        {n(m5["rejilla"]["sigma_minimo_dibujable_m"], 0)} m, así que
        <strong>{" y ".join("<code>bw." + s + "</code>" for s in m5["rejilla"]["selectores_descartados"])}
        quedan fuera</strong> — no por gusto, sino porque a esa resolución su superficie
        dibujaría la rejilla en vez del núcleo. La decisión de qué selector usar acaba tomándola,
        en parte, el presupuesto del ráster; y eso también se dice en voz alta.</p>
""" + CIERRE


# =====================================================================
# MÓDULO 4 · Corrección de borde en la KDE
# =====================================================================
R4 = '''# La comprobacion que decide: integrar la intensidad estimada sobre la
# ventana tiene que devolver n. Si no, el estimador esta perdiendo o
# inventando puntos, y el mapa no lo dice.
integra &lt;- function(im) {{
  v &lt;- as.numeric(im$v); v &lt;- v[is.finite(v)]
  sum(v) * im$xstep * im$ystep
}}

s &lt;- {SIG}
con &lt;- density(p, sigma = s, dimyx = c({NY}, {NX}))                 # por defecto
sin &lt;- density(p, sigma = s, dimyx = c({NY}, {NX}), edge = FALSE)   # sin corregir
dig &lt;- density(p, sigma = s, dimyx = c({NY}, {NX}), diggle = TRUE)  # Diggle

round(c(defecto = integra(con), diggle = integra(dig),
        sin_corregir = integra(sin), n = npoints(p)), 4)
#&gt;      defecto       diggle sin_corregir            n
#&gt; {MASAS}

# Y lo mismo en porcentaje sobre n, que es como se lee
round(100 * (c(integra(con), integra(dig), integra(sin)) / npoints(p) - 1), 4)
#&gt; [1] {PCTS}'''

PY4 = '''# Sin correccion de borde, la integral de la KDE sobre la ventana es
# exactamente la suma de e_i: la fraccion del nucleo de cada punto que
# cae DENTRO. Calcularla punto por punto explica la fuga en vez de
# medirla: los puntos del centro aportan 1, los del borde bastante menos.
def masa_dentro(px, py, sigma, W, paso):
    x0, y0, x1, y1 = W.bounds
    gx, gy = np.meshgrid(np.arange(x0, x1 + paso, paso), np.arange(y0, y1 + paso, paso))
    dentro = gpd.GeoSeries(gpd.points_from_xy(gx.ravel(), gy.ravel())).within(W).to_numpy()
    gx, gy = gx.ravel()[dentro], gy.ravel()[dentro]
    e = np.empty(len(px))
    for i in range(len(px)):
        d2 = (gx - px[i]) ** 2 + (gy - py[i]) ** 2
        e[i] = np.exp(-d2 / (2 * sigma ** 2)).sum() * paso * paso / (2 * np.pi * sigma ** 2)
    return e

e = masa_dentro(px, py, 800.0, W, 200.0)
print(round(float(e.sum()), 2), round(float(e.min()), 4))
#&gt; 224.07 0.2319'''

_SUB4 = dict(
    SIG=ent(m4["sigmas_m"][-1]),
    NX=str(FAM["nx"]), NY=str(FAM["ny"]),
    MASAS=" ".join(n(v, 4) for v in (m4["tabla"][-1]["masa_defecto"],
                                     m4["tabla"][-1]["masa_diggle"],
                                     m4["tabla"][-1]["masa_sin_corregir"],
                                     m4["n"])),
    PCTS=" ".join(n(v, 4) for v in (m4["tabla"][-1]["exceso_defecto_pct"],
                                    m4["tabla"][-1]["error_diggle_pct"],
                                    m4["tabla"][-1]["fuga_sin_corregir_pct"])))

_c = m4["coste_segundos"]

MOD4 = cabecera(
    4, "Corrección de borde en la KDE", "Edge correction for kernel intensity",
    "Ver qué hace la corrección de borde —no cuánto cuesta— y descubrir que hay "
    "tres comportamientos donde parecía haber dos.") + f"""
      <p>El módulo 1 dejó el divisor $e(u)$ apuntado y sin explicar. Toca ahora, y conviene
        empezar por qué problema resuelve: el núcleo de un punto pegado al borde
        <strong>se sale de la ventana</strong>, y la masa que se sale no la recoge nadie. Sin
        hacer nada, el estimador se queda corto justo en el perímetro, que suele ser donde más
        se mira.</p>

      <p>La comprobación que lo decide no es visual. Si $\\hat\\lambda$ estima la intensidad,
        su integral sobre la ventana tiene que devolver el número de puntos:</p>

      <div class="formula-destacada">
        $$\\int_W \\hat\\lambda(u)\\,du \;=\; n$$
      </div>

      <p>Es una identidad, no una aproximación, y por eso sirve de prueba. Medida sobre
        {m1["ventana"]["nombre"]} a tres anchos, aparecieron <strong>tres</strong>
        comportamientos donde el manual sugiere dos.</p>

      <table class="tabla-datos">
        <caption>La integral de la intensidad estimada sobre la ventana, contra
          n = {ent(m4["n"])} sedes</caption>
        <thead><tr><th scope="col">σ</th>
          <th scope="col">Sin corregir</th><th scope="col">Por defecto</th>
          <th scope="col">Con <code>diggle = TRUE</code></th></tr></thead>
        <tbody>
""" + "".join(
    fila(f'{ent(f["sigma_m"])} m',
         f'{n(f["masa_sin_corregir"], 2)} ({n(f["fuga_sin_corregir_pct"], 2)} %)',
         f'{n(f["masa_defecto"], 2)} (+{n(f["exceso_defecto_pct"], 2)} %)',
         f'{n(f["masa_diggle"], 2)} ({n(f["error_diggle_pct"], 4)} %)')
    for f in m4["tabla"]) + f"""        </tbody>
      </table>

      <p>Sin corregir, <strong>la masa se escapa</strong>, y cada vez más al abrir el núcleo:
        de {n(m4["tabla"][0]["fuga_sin_corregir_pct"], 2)} % a
        {firma(n(m4["tabla"][-1]["fuga_sin_corregir_pct"], 2), " %")}. Con la corrección que
        <code>density.ppp</code> aplica sin pedírsela, <strong>la masa se pasa</strong>, y
        también crece con σ. Y con <code>diggle = TRUE</code> la integral devuelve n clavado a
        cualquier ancho.</p>

      <div class="nota-lateral">
        <h4>Por qué solo una de las tres conserva el conteo</h4>
        <p>Las dos correcciones dividen por la misma cosa —la fracción del núcleo que cae dentro
          de la ventana— pero <strong>la evalúan en sitios distintos</strong>. La de por defecto
          divide en el punto <em>donde se estima</em>, $u$; la de Diggle, en el punto
          <em>donde está el dato</em>, $x_i$. Con la segunda cada punto aporta exactamente 1 a
          la integral, así que el total es n por construcción. Las dos están publicadas y las
          dos son legítimas; solo una conserva el conteo, y no es la que sale sin pedirla.</p>
        <p style="margin-bottom:0;">Ninguna de las tres se distingue mirando el mapa de calor:
          los tres salen plausibles. Es el modo de fallo de siempre — la operación que devuelve
          algo creíble en vez de fallar.</p>
      </div>

{sim("cap5-borde", "Las tres correcciones, y lo que le hacen a la masa",
      "Cambia el ancho y mira la barra de n. Lo que interesa no es cuál está más "
      "alta, sino que las dos desviaciones crecen con σ: el problema del borde no "
      "es un detalle fijo, escala con el núcleo.")}
      <p>Entre no corregir y corregir por defecto hay
        {firma(n(m4["horquilla_pct"]), " puntos porcentuales")} a σ =
        {ent(m4["sigmas_m"][-1])} m. Y la horquilla también se ve en el pico del mapa: sin
        corregir, la intensidad máxima baja de {n(m4["tabla"][-1]["max_km2_defecto"], 2)} a
        {n(m4["tabla"][-1]["max_km2_sin_corregir"], 2)} sedes por km².</p>

{tabs("La integral que tiene que dar n", R4.format(**_SUB4), PY4.format(**_SUB4))}
      <p>La columna de Python no traduce la llamada: calcula punto por punto qué fracción de su
        núcleo cae dentro de la ventana y las suma, que es exactamente lo que vale la integral
        sin corregir. Los dos caminos coinciden en sus tres primeras cifras —son dos
        discretizaciones de la misma integral, y el bloque publica las dos—, y el de Python enseña
        de paso lo que la cifra global esconde: hay sedes cuyo núcleo pierde más de las tres
        cuartas partes de su masa por el borde.</p>

      <h3>Y una palabra que aquí significa otra cosa</h3>

      <p>El capítulo 4 dedicó un módulo entero a la corrección de borde de K, y allí la decisión
        fue cara: la isotrópica costaba <strong>555 veces</strong> la de traslación sobre esta
        misma ciudad, y hubo que elegir declarándolo. Aquí las tres cuestan lo mismo —
        {n(_c["defecto"], 2)} s por defecto, {n(_c["sin_corregir"], 2)} s sin corregir y
        {n(_c["diggle"], 2)} s con Diggle— porque <strong>la KDE se paga por píxel y no por
        perímetro</strong>.</p>

      <p>La misma expresión, «corrección de borde», nombra una operación gratis y una carísima
        según qué se esté estimando. No hay aquí nada que elegir por precio: solo por lo que
        cada una conserva. Y el módulo 11 traerá el caso opuesto —una llamada que
        <em>elige la corrección por ti</em>, la más cara, sin mencionarla.</p>
""" + CIERRE

# =====================================================================
# MÓDULO 5 · La KDE como mapa de calor
#
# LA DECISIÓN 2 DE LA FASE 3 SE REVIERTE AQUÍ, Y POR ESCRITO.
# El caso trabajado de `Demirel et al. (2026)` entraba en este módulo con
# una dependencia declarada: hacía falta su fuente delante. No llegó —el
# precálculo la publica como `caso_demirel: null`— así que el módulo se
# escribe con el hilo colombiano, que es lo que la propia decisión
# preveía. D10 no admite cifras que no se puedan leer en su origen, y un
# caso trabajado citado de memoria es exactamente eso.
# =====================================================================
R5 = '''library(spatstat)

v_urb &lt;- st_read(&quot;datos/procesado/bogota_ventana_urbana.gpkg&quot;, quiet = TRUE)
s11   &lt;- st_read(&quot;datos/procesado/bogota_colegios_saber11.gpkg&quot;, quiet = TRUE)

WU &lt;- as.owin(st_geometry(st_union(v_urb)))
pu &lt;- ppp(xy[, 1], xy[, 2], window = WU)
en &lt;- inside.owin(xy[, 1], xy[, 2], WU)
c11 &lt;- en &amp; !is.na(s11$s11_n)
p11 &lt;- ppp(st_coordinates(s11)[c11, 1], st_coordinates(s11)[c11, 2], window = WU)

# TRES MAPAS QUE NO SON EL MISMO MAPA. El tercero pesa cada sede por sus
# evaluados: `weights` cambia lo que la superficie cuenta, no como se ve.
# El sigma NO se escribe: lo elige bw.CvL, que es el mas estrecho de los
# cuatro selectores que esta rejilla puede dibujar sin mentir.
sg &lt;- as.numeric(bw.CvL(pu))
round(sg, 4)
#&gt; [1] {SIG}

d &lt;- c({NY}, {NX})
k_of &lt;- density(pu,  sigma = sg, dimyx = d, diggle = TRUE)
k_11 &lt;- density(p11, sigma = sg, dimyx = d, diggle = TRUE)
k_es &lt;- density(p11, sigma = sg, dimyx = d, diggle = TRUE,
                weights = s11$s11_n[c11])

round(c(oferta = max(k_of), grado11 = max(k_11), evaluados = max(k_es)) * 1e6, 4)
#&gt;    oferta   grado11 evaluados
#&gt; {MAXS}

# Y cuanto se parecen entre si, que es lo que dice si la distincion
# es pedante o es el modulo
dentro &lt;- is.finite(as.numeric(k_of$v))
vu &lt;- function(im) as.numeric(im$v)[dentro]
round(c(of_11 = cor(vu(k_of), vu(k_11)), of_ev = cor(vu(k_of), vu(k_es)),
        c11_ev = cor(vu(k_11), vu(k_es))), 4)
#&gt;  of_11  of_ev c11_ev
#&gt; {CORS}'''

PY5 = '''# Lo primero no necesita ningun estimador: cuantas sedes hay, cuantas
# tienen grado 11 y cuantos estudiantes presentaron. Media capa se cae
# entre la primera cifra y la segunda, y esa mitad es la que convierte
# un mapa de oferta en uno de bachillerato sin cambiar el titulo.
print(len(urb), int(urb.s11_n.notna().sum()), int(urb.s11_n.sum()))
#&gt; {N} {N11} {TOT}
print(round(100 * urb.s11_n.notna().mean(), 4))
#&gt; {PCT}

# La maquinaria de la ciudad, una vez: rejilla, mascara y el divisor de
# borde e(u). Es el mismo binado y la misma convolucion del modulo 2, con
# la ventana urbana en vez de la de Kennedy.
WU = gpd.read_file(&quot;datos/procesado/bogota_ventana_urbana.gpkg&quot;).geometry.union_all()
NX, NY, SIG = {NX}, {NY}, {SIG_LARGO}
X0, Y0, X1, Y1 = WU.bounds
DX, DY = (X1 - X0) / NX, (Y1 - Y0) / NY
GX, GY = np.meshgrid(X0 + (np.arange(NX) + 0.5) * DX, Y0 + (np.arange(NY) + 0.5) * DY)
MASK = gpd.GeoSeries(gpd.points_from_xy(GX.ravel(), GY.ravel())).within(WU).to_numpy().reshape(NY, NX)
_rx, _ry = int(np.ceil(4 * SIG / DX)), int(np.ceil(4 * SIG / DY))
_kx, _ky = np.arange(-_rx, _rx + 1) * DX, np.arange(-_ry, _ry + 1) * DY
NUC = np.exp(-(_kx[None, :] ** 2 + _ky[:, None] ** 2) / (2 * SIG ** 2)) / (2 * np.pi * SIG ** 2)
BORDE = fftconvolve(MASK.astype(float), NUC, mode=&quot;same&quot;) * DX * DY

def kde_ciudad(px, py, w=None):
    c = np.zeros((NY, NX))
    ix = np.clip(((px - X0) / DX).astype(int), 0, NX - 1)
    iy = np.clip(((py - Y0) / DY).astype(int), 0, NY - 1)
    np.add.at(c, (iy, ix), 1.0 if w is None else w)
    z = fftconvolve(c, NUC, mode=&quot;same&quot;) / np.maximum(BORDE, 1e-300)
    return np.where(MASK, z, np.nan)

# Las tres superficies y cuanto se parecen. No sale identica a la de R
# —otra discretizacion— pero contesta lo mismo: se parecen mucho y no
# son iguales, y la pareja que menos se parece es edificios contra gente.
ok11 = urb.s11_n.notna().to_numpy()
UX, UY = urb.x.to_numpy(), urb.y.to_numpy()
z_of = kde_ciudad(UX, UY)
z_11 = kde_ciudad(UX[ok11], UY[ok11])
z_es = kde_ciudad(UX[ok11], UY[ok11], urb.s11_n.to_numpy()[ok11])
print([round(float(np.corrcoef(a[MASK], b[MASK])[0, 1]), 4)
       for a, b in ((z_of, z_11), (z_of, z_es), (z_11, z_es))])
#&gt; [0.9391, 0.8555, 0.9155]'''

_SUB5 = dict(
    SIG=n(m5["sigma_m"], 4), SIG_LARGO=n(m5["sigma_m"], 10),
    NX=str(m5["rejilla"]["nx"]), NY=str(m5["rejilla"]["ny"]),
    MAXS=" ".join(n(m5["capas"][k]["max_km2"], 4)
                  for k in ("oferta", "grado_11", "estudiantes")),
    CORS=" ".join(n(m5[k], 4) for k in ("cor_oferta_grado11", "cor_oferta_estudiantes",
                                        "cor_grado11_estudiantes")),
    N=ent(m5["capas"]["oferta"]["n"]).replace(" ", ""),
    N11=ent(m5["capas"]["grado_11"]["n"]).replace(" ", ""),
    TOT=ent(m5["capas"]["estudiantes"]["total"]).replace(" ", ""),
    PCT=n(m5["capas"]["grado_11"]["pct_de_las_sedes"], 4))

_desc = " y ".join(f'<code>bw.{s}</code>' for s in m5["rejilla"]["selectores_descartados"])

MOD5 = cabecera(
    5, "La KDE como mapa de calor", "Kernel intensity as a heat map",
    "Distinguir tres mapas que se parecen mucho y no dicen lo mismo, y no dejar "
    "que ninguno se llame «la demanda» sin haberlo decidido.") + f"""
      <p>Hasta aquí la superficie ha sido un objeto técnico. En cuanto sale de la pantalla y
        entra en un informe pasa a ser <strong>un mapa de calor</strong>, y con eso se le
        atribuye un significado que el estimador no tiene: la gente lee «aquí hay más» y
        entiende «aquí hace falta más», o al revés, según el mapa.</p>

      <p>Este módulo trabaja el paso de una cosa a la otra con el hilo colombiano, y su ejercicio
        central es que <strong>tres mapas casi idénticos responden a tres preguntas
        distintas</strong>.</p>

      <div class="tip-box">
        <h4>Una decisión revertida, y se dice</h4>
        <p style="margin-bottom:0;">Este módulo iba a llevar un caso trabajado de la literatura
          reciente sobre localización de servicios educativos. La decisión se tomó
          <strong>con una dependencia declarada</strong>: hacía falta la fuente delante para
          poder leer sus cifras en su origen. La fuente no llegó, así que el caso no se escribe
          — y la decisión se revierte aquí, por escrito, en vez de quedarse el título y
          rellenarlo de memoria. Es la misma regla que sostiene todo el material: ninguna cifra
          que no se pueda comprobar en su origen.</p>
      </div>

      <h3>Tres mapas que no son el mismo mapa</h3>

      <table class="tabla-datos">
        <caption>Las tres capas sobre la ciudad, con σ = {n(m5["sigma_m"], 0)} m</caption>
        <thead><tr><th scope="col">Mapa</th><th scope="col">Qué cuenta</th>
          <th scope="col">Unidades</th><th scope="col">Máximo por km²</th></tr></thead>
        <tbody>
{fila("Oferta", "todas las sedes educativas", f'{ent(m5["capas"]["oferta"]["n"])} sedes', n(m5["capas"]["oferta"]["max_km2"], 2))}{fila("Bachillerato", "solo las sedes con grado 11", f'{ent(m5["capas"]["grado_11"]["n"])} sedes ({n(m5["capas"]["grado_11"]["pct_de_las_sedes"], 1)} %)', n(m5["capas"]["grado_11"]["max_km2"], 2))}{fila("Estudiantes", "las mismas sedes, pesadas por sus evaluados", f'{ent(m5["capas"]["estudiantes"]["total"])} evaluados', n(m5["capas"]["estudiantes"]["max_km2"], 2))}        </tbody>
      </table>

      <p>Entre el primero y el segundo se cae <strong>media capa</strong>: una sede de primaria
        no tiene undécimo, así que solo entra el
        {n(m5["capas"]["grado_11"]["pct_de_las_sedes"], 1)} % de las sedes. Pesar por Saber 11 sin decir esto convertiría un mapa de oferta en uno
        de bachillerato <em>sin que el título cambiara</em>. Y el tercero cuenta personas y no
        edificios: su unidad ya no es «sedes por km²».</p>

      <p>Los tres se parecen —correlacionan
        {n(m5["cor_oferta_grado11"], 3)}, {n(m5["cor_oferta_estudiantes"], 3)} y
        {n(m5["cor_grado11_estudiantes"], 3)} entre sí— y por eso la distinción no es pedante:
        <strong>si correlacionaran 1 daría igual cuál se publica, y no correlacionan 1</strong>.
        La menor de las tres es justo la que enfrenta edificios contra estudiantes.</p>

{mapa_html("cap5-oferta", "Oferta: intensidad de sedes educativas en la ciudad")}
      <p class="pie-figura">La rejilla es de {m5["rejilla"]["nx"]} × {m5["rejilla"]["ny"]} celdas
        y cada celda mide {n(m5["rejilla"]["celda_m"], 0)} m, así que el σ más estrecho que este
        mapa puede dibujar honestamente es {n(m5["rejilla"]["sigma_minimo_dibujable_m"], 0)} m
        —tres celdas—. Eso <strong>descarta {_desc}</strong>, que piden menos, y deja el mapa con
        <code>bw.{m5["sigma_selector"]}</code>: {n(m5["sigma_m"], 0)} m. La resolución no es un
        detalle de presentación; aquí ha elegido selector.</p>

{mapa_html("cap5-estudiantes", "Demanda: evaluados en Saber 11, con las sedes pesadas por sus estudiantes")}
      <p class="pie-figura">El mismo σ, la misma rejilla y las mismas
        {ent(m5["capas"]["grado_11"]["n"])} sedes: lo único que cambia es que cada punto pesa por
        sus evaluados en vez de por uno. Compárense los dos mapas en el norte y en el suroccidente
        —donde las manchas no coinciden es donde el edificio y el estudiante dejan de ser la
        misma cosa—.</p>

{sim("cap5-capas", "Las tres capas, y cuánto se parecen",
      "Las barras son el máximo de cada superficie —en su propia unidad, que por eso "
      "van en escala logarítmica— y la lectura trae las tres correlaciones. Cambia de "
      "capa y mira cuál es la pareja que menos se parece.")}
      <p>Ninguno de los tres es «el mapa de la demanda». El primero dice dónde hay colegio, el
        segundo dónde hay bachillerato y el tercero dónde están los estudiantes que ya lo cursan
        —que no es lo mismo que dónde <em>haría falta</em> que lo hubiera, porque un estudiante
        cuenta donde estudia, no donde vive—. <strong>Llamar «demanda» a cualquiera de los tres
        es una decisión, no una descripción</strong>, y este material la escribe en vez de
        dejarla en el título de la figura.</p>

{tabs("Las tres capas, y qué cambia entre ellas", R5.format(**_SUB5), PY5.format(**_SUB5))}
      <p>La comprobación que hace honesto el tercero está en el precálculo y no en el mapa: la
        KDE pesada integra <strong>la suma de los pesos</strong>, no el número de puntos, así que
        su integral sobre la ciudad tiene que dar los
        {ent(m5["capas"]["estudiantes"]["total"])} evaluados. Es la identidad del módulo 4 con
        pesos, y es lo que dice que la superficie cuenta estudiantes.</p>
""" + CIERRE


# =====================================================================
# MÓDULO 6 · Intensidad relativa y riesgo relativo
# =====================================================================
R6 = '''# EL CANONICO PRIMERO, PORQUE ES EL QUE SE PUEDE CONTRASTAR CON EL LIBRO.
# `chorley`: casos de laringe contra CONTROLES DE PULMON —no poblacion
# sana—, elegidos asi para que la geografia del tabaco no se cuele en el
# cociente. Esa eleccion es la mitad del metodo.
data(chorley)
table(marks(chorley))
#&gt; larynx   lung
#&gt;     {CASOS}    {CTRL}

# `relrisk` DEVUELVE LA PROBABILIDAD DEL SEGUNDO NIVEL DEL FACTOR, y los
# niveles se ordenan alfabeticamente: sin tocar nada, el mapa es
# P(pulmon) —los controles— y no P(laringe). Se fija el orden.
ch &lt;- chorley
marks(ch) &lt;- factor(as.character(marks(chorley)), levels = c(&quot;lung&quot;, &quot;larynx&quot;))
rr &lt;- relrisk(ch, sigma = {SIG_CH})
v &lt;- as.numeric(rr$v); v &lt;- v[is.finite(v)]

round(c(mediana = median(v), global = mean(marks(ch) == &quot;larynx&quot;),
        maxima = max(v)), 4)
#&gt; mediana  global  maxima
#&gt;  {CH}'''

PY6 = '''# El riesgo relativo es un COCIENTE DE DOS INTENSIDADES sobre la misma
# ventana, y por eso se puede reconstruir con la KDE que ya esta escrita:
# nada nuevo salvo dividir. Aqui, sobre Bogota, P(oficial).
of = (urb.sector == &quot;Oficial&quot;).to_numpy()
z_ofi = kde_ciudad(UX[of], UY[of])
z_pri = kde_ciudad(UX[~of], UY[~of])
p_of = z_ofi / (z_ofi + z_pri)

print(round(float(np.nanmedian(p_of)), 4), round(float(of.mean()), 4))
#&gt; 0.309 {PROP}

# La correccion de borde SE VA en el cociente: numerador y denominador la
# llevan igual, asi que se cancela. Es la razon de que un mapa de
# proporcion sea mas robusto que los dos mapas de los que sale.
print(round(float(np.nanmax(p_of)), 4), int(of.sum()), int((~of).sum()))
#&gt; 0.9999 {OFI} {PRI}'''

_SUB6 = dict(
    SIG_CH=ent(m6["chorley"]["sigma"]),
    CASOS=ent(m6["chorley"]["casos"]),
    CTRL=ent(m6["chorley"]["controles"]),
    CH=" ".join(n(v, 4) for v in (m6["chorley"]["p_mediana"],
                                  m6["chorley"]["prop_global"],
                                  m6["chorley"]["p_max"])),
    PROP=n(m6["bogota"]["prop_global"], 4),
    OFI=ent(m6["bogota"]["oficiales"]).replace(" ", ""),
    PRI=ent(m6["bogota"]["privadas"]).replace(" ", ""))

_ch, _bg = m6["chorley"], m6["bogota"]

MOD6 = cabecera(
    6, "Intensidad relativa", "Relative risk and relative intensity",
    "Estimar un cociente de intensidades, leerlo con la palabra correcta y montar "
    "la guarda que impide publicarlo del revés.") + f"""
      <p>Todo lo anterior estima <em>una</em> intensidad. Muchas preguntas reales no van de
        cuántos hay, sino de <strong>qué proporción</strong>: dónde pesan más los casos que los
        controles, dónde pesa más lo público que lo privado. Y eso es un
        <strong>cociente de dos intensidades</strong> estimadas sobre la misma ventana.</p>

      <div class="formula-destacada">
        $$\\hat p(u) \;=\; \\frac{{\\hat\\lambda_1(u)}}{{\\hat\\lambda_1(u) + \\hat\\lambda_0(u)}}$$
      </div>

      <p>La forma tiene una ventaja que no es evidente: <strong>la corrección de borde del módulo
        4 se cancela</strong>. Numerador y denominador la llevan igual, así que un mapa de
        proporción es más robusto que cualquiera de los dos mapas de los que sale.</p>

      <h3>El caso canónico, con los controles bien nombrados</h3>

      <p>El casos-controles de Diggle son {firma(ent(_ch["casos"]), " casos de laringe")} contra
        {firma(ent(_ch["controles"]), " controles")}, y lo que hace que el ejemplo enseñe es qué
        son los controles: <strong>{_ch["que_son_los_controles"]}</strong>.
        Se eligieron así para que la geografía del tabaco esté en los dos grupos y se vaya en el
        cociente. Cambiar los controles cambia lo que el mapa significa, y esa decisión es la
        mitad del método.</p>

      <p>La proporción global de casos es {n(_ch["prop_global"], 4)}. La mediana de la superficie
        es {n(_ch["p_mediana"], 4)} y su máximo llega a {n(_ch["p_max"], 4)}: hay sitios donde
        uno de cada tres cánceres registrados es de laringe, seis veces la proporción de la
        comarca.</p>

      <div class="nota-lateral">
        <h4>La trampa que casi publica este módulo al revés</h4>
        <p><code>relrisk</code> devuelve la probabilidad del <strong>segundo nivel</strong> del
          factor de marcas, y los niveles se ordenan alfabéticamente. Con
          <code>larynx, lung</code>, el mapa que sale sin tocar nada es
          <strong>P(pulmón)</strong> —los controles—; con <code>oficial, privado</code>, es
          P(privado). La primera versión de este módulo tituló su mapa «proporción de sedes
          oficiales», comparó su mediana contra la proporción de oficiales y sacó una conclusión
          sobre dónde está lo público. Todo corría, ninguna comprobación fallaba y la afirmación
          era la contraria de la cierta.</p>
        <p style="margin-bottom:0;">Se arregla de dos formas <em>a la vez</em>, porque una sola
          no basta: se fija el orden de niveles, y se <strong>comprueba la orientación contra el
          dato</strong> —donde el mapa dice que la proporción es máxima, los vecinos tienen que
          ser mayoritariamente de ese tipo—. Medido: en el máximo de <code>chorley</code> el
          {pct(100 * _ch["orientacion_verificada"], 0)} de los cincuenta vecinos son casos, sobre
          una proporción global de {pct(100 * _ch["prop_global"], 1)}; en el de Bogotá, el
          {pct(100 * _bg["orientacion_verificada"], 0)} son oficiales. Esa segunda guarda es la
          que habría cazado el defecto, y sobrevive a que alguien reordene los niveles.</p>
      </div>

      <h3>Y el caso colombiano, que no es riesgo</h3>

      <p>La misma matemática sobre {firma(ent(_bg["oficiales"]), " sedes oficiales")} y
        {firma(ent(_bg["privadas"]), " privadas")}, y aquí el capítulo dice en voz alta que
        <strong>esto no es riesgo epidemiológico sino proporción de tipo</strong>. Nadie
        «contrae» ser oficial: no hay casos ni controles, hay dos poblaciones completas. Publicar
        el mapa llamándolo riesgo importaría una palabra que aquí no significa nada.</p>

{mapa_html("cap5-proporcion", "P(oficial): proporción de sedes oficiales sobre el total")}
      <p class="pie-figura">La escala va fija de 0 a 1 y no se normaliza contra el máximo del
        mapa: una proporción tiene una escala propia, y normalizarla haría que el mapa dijera
        «aquí es donde más» en vez de «aquí vale tanto». El blanco del centro no es ausencia de
        colegios — es ausencia de colegios <em>oficiales</em>.</p>

{mapa_html("cap5-sector", "Las mismas sedes, por sector, sin suavizar")}
      <p class="pie-figura">El mapa de puntos es el control de la superficie: enseña de dónde
        sale cada mancha y recuerda que lo privado está apiñado en el centro y lo oficial ocupa
        la periferia.</p>

      <p>Y aquí aparece la cifra que es el módulo. La proporción de oficiales <em>contando
        puntos</em> es {firma(n(_bg["prop_global"], 4))}; la mediana de la
        <em>superficie</em> es {firma(n(_bg["p_mediana"], 4))}. No tienen por qué coincidir, y su
        diferencia dice algo geográfico: como la mediana del área queda
        <strong>por debajo</strong> de la proporción de los puntos, lo oficial está
        <strong>concentrado</strong> —es mayoría en poca superficie—, mientras lo privado se
        reparte por más ciudad.</p>

{sim("cap5-riesgo", "Contar puntos y mirar el mapa dan respuestas distintas",
      "Cada patrón trae dos referencias: la proporción global —contando puntos— y la "
      "mediana de la superficie. Que la segunda quede por debajo de la primera es lo "
      "que significa «concentrado».")}
      <p>Las dos cifras son ciertas y contestan preguntas distintas: «¿qué fracción de las sedes
        es oficial?» y «¿en qué fracción de la ciudad son mayoría?». Un informe que solo publique
        una de las dos no está mintiendo, pero tampoco está diciendo lo que el lector va a
        entender.</p>

{tabs("El cociente de dos intensidades, y quién es el segundo nivel", R6.format(**_SUB6), PY6.format(**_SUB6))}
      <p>Con esto se cierra la mitad descriptiva del capítulo: ya se sabe estimar una superficie,
        elegir su ancho, corregirle el borde y dividir dos. Antes de pasar a modelar —que es
        poner una covariable donde hasta ahora había un mapa— van cuatro preguntas sobre lo que
        llevamos.</p>

{quiz_html('cap5-trampas', 'Cuatro trampas de la intensidad por núcleos',
           'Sin nota. Cada opción trae su explicación, así que equivocarse aquí vale tanto '
           'como acertar.')}
      <p>Las cuatro comparten forma: una operación que devuelve algo plausible y una decisión
        que nadie escribió. A partir del módulo siguiente la intensidad deja de ser una
        superficie que se dibuja y pasa a ser <strong>una función de algo</strong> —de una
        covariable, y luego de un modelo con coeficientes que se leen—.</p>
""" + CIERRE

# =====================================================================
# MÓDULO 7 · Covariables: la intensidad como función de otra cosa
# =====================================================================
R7 = '''# `rhohat` ES ALEATORIO. Usa una cuadratura muestreada, asi que dos
# ejecuciones seguidas dan curvas parecidas y no iguales —la razon de
# esta misma curva se mueve entre 21.12 y 21.14 sin tocar el dato—. Sin
# semilla, la cifra que se publique no la puede reproducir nadie.
set.seed({SEMILLA})

rango &lt;- function(p, cov) {{
  rh &lt;- rhohat(p, cov)
  ok &lt;- is.finite(rh$rho)
  x &lt;- rh[[1]][ok]; y &lt;- rh$rho[ok]
  vp &lt;- if (is.function(cov)) cov(p$x, p$y) else cov[p]
  q &lt;- quantile(vp, c(0.05, 0.95))          # el BULTO: donde hay dato
  b &lt;- x &gt;= q[1] &amp; x &lt;= q[2]
  c(total = max(y) / min(y), bulto = max(y[b]) / min(y[b]))
}}

signif(rango(bei, bei.extra$elev), 6)
#&gt;   total   bulto
#&gt; {ELEV}
signif(rango(bei, bei.extra$grad), 6)
#&gt;   total   bulto
#&gt; {GRAD}

# Y el caso colombiano: la distancia al centro de masa de las sedes
centro &lt;- ppp(mean(pu$x), mean(pu$y), window = WU)
signif(rango(pu, distfun(centro)), 6)
#&gt;   total   bulto
#&gt; {DCEN}'''

PY7 = '''# `rhohat` es un suavizado de Nadaraya-Watson: en el numerador el nucleo
# evaluado en la covariable DE LOS PUNTOS, en el denominador el mismo
# nucleo sobre toda la ventana. Reimplementarlo enseña por que la cola
# infla: alli el denominador se queda con un punado de celdas.
Z_PTS = np.hypot(UX - UX.mean(), UY - UY.mean())
Z_WIN = np.hypot(GX[MASK] - UX.mean(), GY[MASK] - UY.mean())
H = 1.06 * Z_PTS.std(ddof=1) * len(Z_PTS) ** (-1 / 5)
ZZ = np.linspace(Z_PTS.min(), Z_PTS.max(), 512)

def rho(z0):
    num = np.exp(-((Z_PTS - z0) / H) ** 2 / 2).sum()
    den = np.exp(-((Z_WIN - z0) / H) ** 2 / 2).sum() * DX * DY
    return num / den if den &gt; 0 else np.nan

R = np.array([rho(z) for z in ZZ])
ok = np.isfinite(R) &amp; (R &gt; 0)
q1, q2 = np.quantile(Z_PTS, [0.05, 0.95])
bulto = ok &amp; (ZZ &gt;= q1) &amp; (ZZ &lt;= q2)
print(round(float(R[ok].max() / R[ok].min()), 4),
      round(float(R[bulto].max() / R[bulto].min()), 4))
#&gt; 24.8535 1.5274'''

_SUB7 = dict(
    SEMILLA=str(D["meta"]["semilla"]),
    ELEV=" ".join(f'{m7["bei"]["elevacion"][k]:g}' for k in ("razon", "razon_bulto")),
    GRAD=" ".join(f'{m7["bei"]["pendiente"][k]:g}' for k in ("razon", "razon_bulto")),
    DCEN=" ".join(f'{m7["bogota"]["curva"][k]:g}' for k in ("razon", "razon_bulto")))

_curvas7 = (("<code>bei</code> · elevación", m7["bei"]["elevacion"], "m"),
            ("<code>bei</code> · pendiente", m7["bei"]["pendiente"], ""),
            ("Bogotá · distancia al centro", m7["bogota"]["curva"], "m"))

MOD7 = cabecera(
    7, "Covariables", "Covariates and rhohat",
    "Estimar la intensidad como función de otra variable sin modelo, y aprender a "
    "no leer el titular de esa curva, que casi siempre es su cola.") + f"""
      <p>Un mapa de calor dice <em>dónde</em>. La pregunta siguiente es <em>por qué ahí</em>, y
        la forma más honesta de empezar a contestarla es <strong>sin modelo</strong>: en vez de
        suponer una forma funcional, mirar cómo cambia la intensidad a lo largo de una variable
        que está definida en toda la ventana.</p>

      <p>Eso hace <code>rhohat</code>: estima $\\rho(z)$, la intensidad por unidad de área
        <em>condicionada</em> a que la covariable valga z. No supone que la relación sea lineal,
        ni monótona, ni nada — la dibuja.</p>

      <h3>El caso canónico, y por qué es el caso canónico</h3>

      <p>{firma(ent(m7["bei"]["n"]), " árboles")} de <em>Beilschmiedia</em> en Barro Colorado, con
        la elevación y la pendiente del terreno <strong>medidas aparte</strong>, no derivadas de
        los propios árboles. Esa independencia es lo que hace honesta la pregunta: si la
        covariable saliera del patrón, la curva estaría contestándose sola.</p>

      <table class="tabla-datos">
        <caption>Razón entre el ρ máximo y el mínimo de cada curva, entera y restringida al
          bulto (percentiles 5 a 95 de la covariable observada en los puntos)</caption>
        <thead><tr><th scope="col">Curva</th><th scope="col">Razón en todo el rango</th>
          <th scope="col">Razón en el bulto</th><th scope="col">Cuánto infla la cola</th></tr></thead>
        <tbody>
""" + "".join(
    fila(nom, f'{n(c["razon"], 1)} ×', f'{n(c["razon_bulto"], 2)} ×',
         f'{n(c["cola_infla"], 1)} ×')
    for nom, c, _ in _curvas7) + f"""        </tbody>
      </table>

      <p>Aquí está la lección del módulo, y salió midiendo. Si uno lee el titular —«la intensidad
        varía {n(m7["bogota"]["curva"]["razon"], 0)} veces con la distancia al centro»— concluye
        que la distancia manda muchísimo. Restringida al tramo donde de verdad hay datos, la
        misma curva varía {firma(n(m7["bogota"]["curva"]["razon_bulto"]), " veces")}.
        <strong>El titular era toda cola.</strong></p>

      <div class="nota-lateral">
        <h4>Y no es una rareza del dato colombiano</h4>
        <p style="margin-bottom:0;">Se comprobó sobre el canónico antes de escribir la
          comparación, porque enfrentar un número inflado contra otro habría sido tramposo:
          <code>bei</code> con la elevación pasa de {n(m7["bei"]["elevacion"]["razon"], 1)} a
          {n(m7["bei"]["elevacion"]["razon_bulto"], 2)}, y con la pendiente de
          {n(m7["bei"]["pendiente"]["razon"], 1)} a
          {n(m7["bei"]["pendiente"]["razon_bulto"], 2)}. Las tres curvas se comportan igual:
          <strong>el máximo y el mínimo de una <code>rhohat</code> viven casi siempre en los
          extremos, donde apenas hay puntos con los que estimarla</strong>. Por eso este material
          publica las dos razones y compara covariables por la del bulto.</p>
      </div>

{sim("cap5-rhohat", "El titular de una curva rhohat, y lo que queda al quitarle la cola",
      "Las dos barras de cada covariable son la misma curva medida en todo su rango "
      "y en el tramo donde hay datos. Lo que hay que mirar es cuánto encoge la "
      "primera al pasar a la segunda.")}
      <p>Ordenadas por la razón del bulto, las tres covariables quedan al revés que por el
        titular: la pendiente de <code>bei</code> es la que más manda
        ({n(m7["bei"]["pendiente"]["razon_bulto"], 2)} ×) y la distancia al centro de Bogotá la
        que menos ({n(m7["bogota"]["curva"]["razon_bulto"], 2)} ×), justo la que el titular
        ponía primera. <strong>Publicar covariables que no funcionan es la mitad de la
        lección</strong>: un material que solo enseña las que sí entrena a encontrarlas
        siempre.</p>

{tabs("rhohat, su semilla y su cola", R7.format(**_SUB7), PY7.format(**_SUB7))}
      <p>Las dos columnas dan razones distintas sobre todo el rango —el bloque publica las dos—
        porque son dos suavizadores distintos con dos anchos distintos, y eso también es contenido:
        <strong>la razón de una curva <code>rhohat</code> depende del suavizado que la
        produjo</strong>. Lo que no depende del suavizado es la conclusión: al quitar las colas,
        las dos caen a algo muy cerca de {n(m7["bogota"]["curva"]["razon_bulto"], 2)}.</p>

      <p>El módulo 9 volverá sobre esta misma covariable con un modelo, y le dará un coeficiente
        que no se distingue de cero. Convendrá acordarse de esta curva para no leer aquello como
        «la distancia no tiene nada que ver».</p>
""" + CIERRE


# =====================================================================
# MÓDULO 8 · El proceso de Poisson inhomogéneo
# =====================================================================
R8 = '''# LA IDENTIDAD QUE CIERRA EL CIRCULO CON EL CAPITULO 1: la estimacion de
# maxima verosimilitud de un Poisson HOMOGENEO es n/|W|. Que `ppm` la
# recupere dice que la maquinaria de Berman-Turner resuelve el problema
# que dice resolver.
f0 &lt;- ppm(pu ~ 1)
print(c(mle = exp(coef(f0)[[1]]), ingenua = npoints(pu) / area.owin(WU)),
      digits = 6)
#&gt;         mle     ingenua
#&gt; {LAM} {LAM}

round(exp(coef(f0)[[1]]) * 1e6, 4)      # por km2: la lambda del capitulo 1
#&gt; [1] {LAMKM}

# LA CUADRATURA NO ES INOCENTE. Berman-Turner convierte la verosimilitud
# en una regresion de Poisson sobre los puntos MAS una malla de puntos
# ficticios, y `nd` decide cuantos. El defecto no se lee en la ayuda: se
# pregunta.
X0 &lt;- mean(pu$x); Y0 &lt;- mean(pu$y)
centro &lt;- ppp(X0, Y0, window = WU)
COVS &lt;- list(dcen = distfun(centro),
             xc = function(x, y) (x - X0) / 1000,
             yc = function(x, y) (y - Y0) / 1000)

f1 &lt;- ppm(pu ~ dcen, covariates = COVS)
f3 &lt;- ppm(pu ~ dcen, covariates = COVS, nd = 300)
c(nd100 = npoints(quad.ppm(f1)$dummy), nd300 = npoints(quad.ppm(f3)$dummy))
#&gt; nd100 nd300
#&gt;  {FIC} {FIC3}

# El AIC se mueve nueve puntos sin que el modelo cambie una coma. Con los
# siete digitos de siempre no se ve: hay que pedirle a `print` que los de.
print(c(nd100 = AIC(f1), nd300 = AIC(f3)), digits = 10)
#&gt;       nd100       nd300
#&gt; {AIC1} {AIC3}'''

PY8 = '''# La EMV de un Poisson homogeneo no necesita optimizador ninguno: es
# n dividido por el area de la ventana, y sale igual a la decima cifra.
print(float(f&quot;{{len(urb) / WU.area:.6g}}&quot;))
#&gt; {LAM}
print(round(len(urb) / WU.area * 1e6, 4))
#&gt; {LAMKM}'''

_cu = m8["cuadratura"]
_SUB8 = dict(
    LAM=f'{m8["homogeneo"]["lambda_mle_m2"]:g}',
    LAMKM=n(m8["homogeneo"]["lambda_km2"], 4),
    FIC=ent(_cu["defecto_ficticios"]).replace(" ", ""),
    AIC1=n(_cu["tabla"][1]["aic"], 5),
    FIC3=ent(_cu["tabla"][-1]["ficticios"]).replace(" ", ""),
    AIC3=n(_cu["tabla"][-1]["aic"], 5))

MOD8 = cabecera(
    8, "El Poisson inhomogéneo", "The inhomogeneous Poisson process",
    "Pasar de dibujar la intensidad a modelarla, y ver de qué está hecha por dentro "
    "la verosimilitud que lo permite.") + f"""
      <p>Hasta aquí la intensidad ha sido una superficie <em>estimada</em>. Modelarla es otra
        cosa: escribir de qué depende, ajustar los coeficientes de esa dependencia y poder
        contrastarlos. El modelo mínimo que admite intensidad variable es el
        <strong>proceso de Poisson inhomogéneo</strong>, y son dos supuestos, no uno:</p>

      <div class="formula-destacada">
        $$N(B) \\sim \\text{{Poisson}}\\!\\left(\\int_B \\lambda(u)\\,du\\right), \\qquad
          \\lambda(u) \;=\; \\exp\\!\\big(\\beta_0 + \\beta_1 z_1(u) + \\dots\\big)$$
      </div>

      <p>El primero es el mismo del capítulo 4: dadas las regiones, los conteos son Poisson e
        independientes. El segundo es la novedad: λ ya no es constante, sino
        <strong>una función log-lineal de covariables</strong>. La exponencial no es un adorno —
        garantiza que λ sea positiva pase lo que pase con los coeficientes.</p>

      <h3>La comprobación que cierra el círculo</h3>

      <p>Si el modelo se ajusta sin covariables, tiene que devolver la intensidad ingenua del
        capítulo 1: la EMV de un Poisson homogéneo <strong>es</strong> n/|W|. Medido sobre la
        ciudad, las dos coinciden con una diferencia relativa de
        {firma(f'{m8["homogeneo"]["dif_relativa"]:g}')} —el ruido de coma flotante— y la cifra a
        la que llegan es {firma(n(m8["homogeneo"]["lambda_km2"], 4), " sedes por km²")}, la misma
        que el capítulo 1 publicó y el 4 ancló.</p>

      <p>No es un detalle de implementación: es la prueba de que el aparato que viene ahora
        resuelve el problema que dice resolver.</p>

      <h3>Berman-Turner, y la malla que nadie escribe</h3>

      <p>La verosimilitud de un proceso puntual lleva una integral sobre la ventana, y esa
        integral no tiene forma cerrada. El truco de Berman y Turner es aproximarla por
        cuadratura y convertir todo el problema en una <strong>regresión de Poisson ponderada</strong>
        sobre los puntos del dato <em>más</em> una malla de puntos ficticios. Cuántos ficticios lo
        decide el argumento <code>nd</code>, y su valor por defecto —{_cu["defecto_nd"]}— pone
        {firma(ent(_cu["defecto_ficticios"]), " puntos ficticios")} sobre esta ventana.</p>

      <table class="tabla-datos">
        <caption>El mismo modelo con cuatro cuadraturas</caption>
        <thead><tr><th scope="col"><code>nd</code></th><th scope="col">Ficticios</th>
          <th scope="col">Pendiente</th><th scope="col">Error estándar</th>
          <th scope="col">AIC</th></tr></thead>
        <tbody>
""" + "".join(
    fila(ent(z["nd"]), ent(z["ficticios"]), f'{z["pendiente"]:g}',
         f'{z["ee_pendiente"]:g}', n(z["aic"], 2))
    for z in _cu["tabla"]) + f"""        </tbody>
      </table>

      <p>Dos lecturas, y la segunda es la que muerde. La primera: el coeficiente <strong>se mueve
        poco en unidades de su propio error</strong> —de un extremo a otro de la tabla cambia
        {firma(n(_cu["rango_pendiente_en_ee"]), " errores estándar")}—, así que la inferencia
        aguanta. La segunda: <strong>el AIC se mueve {n(_cu["rango_aic"], 1)} puntos</strong>.</p>

      <div class="nota-lateral">
        <h4>Por qué esos {n(_cu["rango_aic"], 1)} puntos importan tanto</h4>
        <p style="margin-bottom:0;">El AIC de <code>ppm</code> sale de la verosimilitud
          <em>aproximada por la cuadratura</em>. Dos modelos ajustados con cuadraturas distintas
          tienen AIC que <strong>no son comparables</strong> — y comparar modelos es exactamente
          para lo que se usa el AIC. Nueve puntos de AIC deciden entre dos modelos con soltura;
          aquí no vienen de ningún modelo, vienen de un argumento que no se escribió.</p>
      </div>

{sim("cap5-cuadratura", "La cuadratura, y lo que le hace a lo que se lee",
      "Cambia nd y mira las dos cosas a la vez: la banda del coeficiente —que apenas "
      "se mueve— y el AIC, que se mueve lo que decide un modelo.")}
      <p>La regla que sale de aquí es corta: <strong>la cuadratura viaja con el modelo</strong>.
        Comparar dos <code>ppm</code> por AIC solo vale si los dos se ajustaron con la misma, y
        eso hay que escribirlo, porque el defecto no aparece en ninguna de las dos llamadas.</p>

{tabs("La EMV homogénea y la cuadratura por defecto", R8.format(**_SUB8), PY8.format(**_SUB8))}
      <p>Con el modelo montado, el módulo siguiente hace lo único que queda por hacer con él:
        leer los coeficientes. Y ahí espera un defecto que no avisa.</p>
""" + CIERRE


# =====================================================================
# MÓDULO 9 · Ajustar con `ppm`
# =====================================================================
R9 = '''# EL AJUSTE QUE SALE BIEN Y NO SE PUEDE LEER. Con x e y en EPSG:9377 las
# coordenadas de Bogota son numeros de siete cifras, y la informacion de
# Fisher queda tan mal condicionada que su inversa no existe en doble
# precision. `ppm` NO falla: devuelve tres coeficientes plausibles.
f_crudo &lt;- ppm(pu ~ x + y)
round(coef(f_crudo), 8)
#&gt;  (Intercept)            x            y
#&gt; {CRUDO}

# Y aqui esta el defecto: `vcov()` avisa y devuelve NULL, y
# `sqrt(diag(NULL))` devuelve una matriz 0 x 0 SIN QUEJARSE. Un try() no
# ve nada. Lo que decide es que haya UN error estandar POR COEFICIENTE.
ee &lt;- suppressWarnings(sqrt(diag(vcov(f_crudo))))
length(ee) == length(coef(f_crudo))
#&gt; [1] FALSE

# El arreglo es una linea: centrar y escalar. El AIC no se mueve —es el
# mismo modelo— pero ahora se puede leer.
f_centr &lt;- ppm(pu ~ xc + yc, covariates = COVS)
round(coef(f_centr), 6)
#&gt; (Intercept)          xc          yc
#&gt; {CENTR}
round(coef(f_centr) / sqrt(diag(vcov(f_centr))), 4)
#&gt; (Intercept)          xc          yc
#&gt; {ZS}'''

PY9 = '''# El numero de condicion explica el NA sin necesidad de ajustar nada:
# es una propiedad de la MATRIZ DE DISENO, no del modelo.
def cond_rec(x, y):
    M = np.column_stack([np.ones(len(x)), x, y])
    s = np.linalg.svd(M, compute_uv=False)
    return s.min() / s.max()

print(f&quot;{{cond_rec(UX, UY):.3g}}&quot;)
#&gt; 1.7e-10
print(f&quot;{{cond_rec((UX - UX.mean()) / 1000, (UY - UY.mean()) / 1000):.4g}}&quot;)
#&gt; 0.1224'''

_cr, _ce, _cd = m9["crudo"], m9["centrado"], m9["distancia"]
_SUB9 = dict(
    CRUDO=" ".join(n(v, 8) for v in _cr["coef"]),
    CENTR=" ".join(n(v, 6) for v in _ce["coef"]),
    ZS=" ".join(n(v, 4) for v in _ce["z"]))

MOD9 = cabecera(
    9, "Ajustar con `ppm`", "Fitting with ppm",
    "Leer los coeficientes de un proceso puntual ajustado, y reconocer los dos casos "
    "en que no se pueden leer aunque el ajuste haya salido.") + f"""
      <p>Ajustar es una línea. Leer lo ajustado tiene dos trampas, y las dos devuelven algo
        plausible en vez de fallar. Este módulo las trabaja sobre el patrón colombiano y el mismo
        modelo de siempre: la intensidad como función log-lineal de dónde está uno.</p>

      <h3>Trampa 1: el sistema de referencia dentro de la verosimilitud</h3>

      <p><code>ppm(pu ~ x + y)</code> ajusta, mejora el AIC frente al modelo constante y devuelve
        tres coeficientes con toda la pinta de serlo —uno de ellos un intercepto de
        {firma(n(_cr["coef"][0], 3))}—. Y sus errores estándar son <code>NA</code>: la información
        de Fisher es singular. En EPSG:9377 las coordenadas de Bogotá son números de siete cifras,
        y la matriz de diseño queda con número de condición recíproco
        {firma(f'{_cr["cond_reciproco"]:g}')}.</p>

      <p>Esto es el capítulo 2 llegando hasta aquí. Allí el sistema de referencia era una decisión
        sobre distancias y áreas; aquí <strong>la misma decisión se mete dentro de una
        verosimilitud y le rompe la inversa</strong>, sin que nada en la llamada hable de sistemas
        de referencia.</p>

      <p>El arreglo es una línea —centrar y pasar a kilómetros— y sube el condicionamiento a
        {firma(f'{_ce["cond_reciproco"]:g}')}, o sea
        {firma(f'{m9["mejora_condicion"]:g}', " veces mejor")}. El AIC no se mueve
        (los dos dan {n(_ce["aic"], 1)}): <strong>es el mismo modelo</strong>. Lo que cambia es
        que ahora se puede leer.</p>

      <table class="tabla-datos">
        <caption>El mismo modelo con dos parametrizaciones, y un tercero con otra covariable</caption>
        <thead><tr><th scope="col">Ajuste</th><th scope="col">Coeficiente</th>
          <th scope="col">Estimación</th><th scope="col">Error estándar</th>
          <th scope="col">z</th></tr></thead>
        <tbody>
""" + "".join(
    fila(f'<code>~ x + y</code> crudo' if i == 0 else "", _cr["nombres"][i],
         f'{_cr["coef"][i]:g}', "—", "—")
    for i in range(len(_cr["coef"]))) + "".join(
    fila(f'<code>~ xc + yc</code> centrado' if i == 0 else "", _ce["nombres"][i],
         f'{_ce["coef"][i]:g}', f'{_ce["ee"][i]:g}', n(_ce["z"][i], 2))
    for i in range(len(_ce["coef"]))) + "".join(
    fila(f'<code>~ dcen</code>' if i == 0 else "", _cd["nombres"][i],
         f'{_cd["coef"][i]:g}', f'{_cd["ee"][i]:g}', n(_cd["z"][i], 2))
    for i in range(len(_cd["coef"]))) + f"""        </tbody>
      </table>

      <p>Con el modelo legible, la lectura es directa: el coeficiente de <code>xc</code> vale
        {n(_ce["coef"][1], 4)} por kilómetro hacia el este —negativo, así que la intensidad baja
        yendo al este— y su z es {n(_ce["z"][1], 2)}; el de <code>yc</code> es cuatro veces menor
        en valor absoluto y su z, {n(_ce["z"][2], 2)}, no llega a separarse de cero.
        <strong>La ciudad tiene gradiente este-oeste y no norte-sur</strong>, y eso es una
        afirmación contrastable, no una impresión de mirar el mapa.</p>

      <div class="nota-lateral">
        <h4>Trampa 2: el <code>try()</code> que no atrapa nada</h4>
        <p style="margin-bottom:0;"><code>vcov()</code> ante una información singular
          <strong>no falla</strong>: avisa y devuelve <code>NULL</code>. Y
          <code>sqrt(diag(NULL))</code> devuelve una matriz 0 × 0 sin quejarse, así que un
          <code>try()</code> no ve nada y un <code>any(!is.finite(.))</code> sobre cero elementos
          vale <code>FALSE</code> — la comprobación ingenua declara «no singular» justo en el caso
          singular. Lo que sí decide es <strong>que haya un error estándar por coeficiente</strong>.
          El ejercicio 4 del módulo 12 lo reproduce sobre un patrón de libro desplazado 4 900 000
          unidades, para que se vea que no es cosa de Bogotá sino del número.</p>
      </div>

{sim("cap5-ppm", "Tres ajustes del mismo patrón, y cuál se puede leer",
      "Las barras son |z| por coeficiente: el ajuste crudo no tiene ninguna, y esa "
      "ausencia es todo el módulo. La lectura trae el número de condición.")}
      <p>Pásese por los tres y mírese la barra que falta. El primero no tiene ninguna, y sin
        embargo su AIC es el mismo que el del segundo: <strong>el modelo está bien ajustado y solo
        es ilegible</strong>. Es una distinción que conviene tener clara antes de la siguiente
        trampa, porque la que viene es justo la contraria — un ajuste perfectamente legible cuya
        lectura obvia es falsa.</p>

      <h3>Y una z que no significa lo que parece</h3>

      <p>El tercer ajuste usa la covariable del módulo 7 —la distancia al centro de masa— y le
        sale z = {firma(n(_cd["z"][1], 2))}. La tentación es concluir que la distancia al centro
        no tiene nada que ver con dónde hay colegios, y es falso: <strong>lo que ese número dice
        es que no hay relación <em>log-lineal</em></strong>. La curva <code>rhohat</code> del
        módulo 7 ya enseñó que en el bulto la intensidad varía
        {n(m7["bogota"]["curva"]["razon_bulto"], 2)} veces, y que su forma no es una recta en la
        escala del logaritmo.</p>

      <p>Un modelo no ve lo que no puede escribir. Por eso los dos módulos van seguidos y en este
        orden: la curva sin modelo primero, el coeficiente después.</p>

{tabs("El ajuste que no se puede leer, y el que sí", R9.format(**_SUB9), PY9.format(**_SUB9))}
      <p>Las dos columnas dan condicionamientos parecidos y no iguales —el bloque publica los
        dos— porque R lo mide sobre la matriz de diseño de la cuadratura, con sus
        {ent(_cu["defecto_ficticios"])} ficticios dentro, y Python sobre las coordenadas del dato,
        sin modelo ninguno. Los dos caen en el orden de {f'{_cr["cond_reciproco"]:g}'}, que es lo
        que el módulo afirma: <strong>el problema estaba en los números antes de que hubiera
        modelo</strong>.</p>
""" + CIERRE

# =====================================================================
# MÓDULO 10 · Diagnóstico del ajuste
# =====================================================================
R10 = '''# LA ENVOLVENTE NO SE SIMULA CONTRA CSR: SE SIMULA CONTRA EL MODELO
# AJUSTADO. Es la diferencia con el capitulo 4, y es toda la pregunta de
# este modulo: si la agregacion era intensidad variable disfrazada, la K
# inhomogenea del patron tiene que caer DENTRO de la banda de su propio
# modelo.
#
# Con nsim = 39 esto tarda unos segundos; el capitulo publica una de 999,
# precalculada, cuyo nivel puntual es {NIVEL} % en vez del 5 %.
set.seed({SEM})
e39 &lt;- envelope(f_centr, Kinhom, nsim = 39, correction = &quot;translate&quot;,
                verbose = FALSE)

dentro_r &lt;- e39$r &gt; 0
fuera &lt;- e39$obs &gt; e39$hi | e39$obs &lt; e39$lo
round(c(nivel_puntual = 2 / (39 + 1),
        pct_fuera = 100 * mean(fuera[dentro_r]),
        r_max = max(e39$r)), 4)
#&gt; nivel_puntual     pct_fuera         r_max
#&gt;        0.0500       78.5156     5868.1157'''

PY10 = '''# La envolvente de 999 que el capitulo publica viaja en un CSV, con sus
# cinco columnas: r, la K observada, el suelo y el techo de la banda, y
# la media de las simulaciones. Leerla es lo que hace un diagnostico.
env = pd.read_csv(&quot;precalculo/salidas/cap5_envolvente.csv&quot;)
ok = env.r &gt; 0
fuera = (env.obs &gt; env.hi) | (env.obs &lt; env.lo)

print(round(100 * fuera[ok].mean(), 1), round(env.r[ok][fuera[ok]].min(), 4))
#&gt; {PCT} {PRIMER}
print(round(env.r.max(), 4))
#&gt; {RMAX}

# La observada por encima del techo en TODO el rango util no es &quot;un poco
# fuera&quot;: es el modelo entero contestando que no.
print(int((env.obs[ok] &gt; env.hi[ok]).sum()), int(ok.sum()))
#&gt; 62 100'''

_SUB10 = dict(
    SEM=str(D["meta"]["semillas"]["envolventes"]),
    NIVEL=n(m10["nivel_puntual_pct"], 1),
    PCT=n(m10["pct_r_fuera_de_banda"], 1),
    PRIMER=n(m10["primer_r_fuera_m"], 4),
    RMAX=n(m10["r_max_m"], 4))

MOD10 = cabecera(
    10, "Diagnóstico del ajuste", "Model diagnostics",
    "Contestar con una medición si la intensidad variable explica la agregación "
    "del patrón, y montar la envolvente contra el modelo y no contra el azar.") + f"""
      <p>El capítulo 4 cerró con un veredicto: las sedes de Bogotá no están repartidas al azar, y
        su K se sale de la banda de CSR por muchísimo. Pero aquella banda comparaba contra un
        proceso de <em>intensidad constante</em>, y ahora hay un modelo que admite intensidad
        variable. La pregunta de este módulo es la bisagra del capítulo:</p>

      <div class="tip-box">
        <h4>La pregunta, y tiene respuesta</h4>
        <p style="margin-bottom:0;">¿Basta con que la intensidad varíe para explicar la
          agregación? Si la K inhomogénea del patrón cae <strong>dentro</strong> de la banda de
          su propio modelo ajustado, entonces sí: lo que parecía atracción entre puntos era
          intensidad variable disfrazada. Si se sale igual, hace falta otra cosa — y esa otra cosa
          es el módulo 11.</p>
      </div>

      <h3>Tres cambios respecto a la envolvente del capítulo 4</h3>

      <p><strong>Uno:</strong> se simula desde el <em>modelo ajustado</em>, no desde CSR. Cada una
        de las {ent(m10["nsim"])} simulaciones es una realización del modelo que se ajustó en el
        módulo 9 —{m10["modelo"]}—.
        <strong>Dos:</strong> se resume con la K <em>inhomogénea</em>, que divide cada pareja por
        la intensidad estimada en sus dos puntos — sin eso, el gradiente este-oeste del propio
        modelo aparecería como agregación. <strong>Tres:</strong> la referencia ya no es la
        teórica de CSR sino la <strong>media de las simulaciones</strong>, porque un objeto
        <code>envelope</code> sobre un modelo ajustado no trae columna teórica y no tendría
        sentido que la trajera.</p>

{sim("cap5-envolvente", "K inhomogénea contra la banda del modelo ajustado",
      "La banda gris son las {NSIM} simulaciones del modelo; la línea verde, el patrón "
      "real. Mira dónde se separa y desde qué radio.".replace("{NSIM}", ent(m10["nsim"])))}
      <p>La respuesta es que <strong>no basta</strong>. La K observada se sale de la banda en el
        {firma(pct(m10["pct_r_fuera_de_banda"], 0))} de los radios, desde
        {firma(n(m10["primer_r_fuera_m"]), " m")} —el primer nodo distinto de cero— y por
        arriba: hay muchas más parejas cercanas de las que un Poisson inhomogéneo con este
        gradiente produciría. Con {ent(m10["nsim"])} simulaciones y la banda por defecto, el nivel
        puntual es {pct(m10["nivel_puntual_pct"], 1)}, así que no es un margen que el azar
        recorra con soltura.</p>

      <p>El veredicto que el precálculo deja escrito es <strong>«{m10["veredicto"]}»</strong>.
        Modelar la intensidad
        explica <em>dónde</em> hay más colegios, pero no explica que los colegios estén cerca unos
        de otros más de lo que ese «dónde» implica. Los colegios se agrupan por razones que no
        son la geografía de la ciudad: comparten manzana, comparten predio, comparten edificio.</p>

      <h3>Y los residuos, que aquí no son lo que uno espera</h3>

      <p>El diagnóstico habitual de un modelo ajustado son sus residuos, y con un proceso puntual
        esa palabra significa otra cosa. <strong>No hay un residuo por observación</strong>: no
        existe un valor observado al que restarle un ajustado, porque lo observado no son números
        sino <em>posiciones</em>. El residuo de un <code>ppm</code> es la diferencia entre dos
        medidas —el patrón, que suma uno en cada punto, y la intensidad ajustada integrada sobre la
        región— y lo que <code>diagnose.ppm</code> dibuja es esa diferencia suavizada en una
        superficie.</p>

      <p>Sirve, y sirve sobre todo para <strong>la tendencia</strong>: si el modelo pone demasiada
        intensidad en el norte, el residuo suavizado se ve negativo ahí. Pero tiene un límite que
        conviene saber antes de fiarse de él, y es la razón de que este módulo diagnostique con la
        K inhomogénea: <strong>un Poisson ajustado por máxima verosimilitud reproduce por
        construcción la tendencia que se le dio</strong>, así que su residuo suavizado tiende a
        salir plano sobre las covariables del propio modelo — y queda ciego justo a lo que aquí
        sobra, que no es tendencia sino <em>interacción entre puntos</em>. Un residuo plano y una K
        que se sale de la banda son perfectamente compatibles, y las dos cosas serían ciertas.</p>

      <div class="nota-lateral">
        <h4>Una corrección de borde que se hereda, y por qué</h4>
        <p style="margin-bottom:0;">La envolvente va con corrección de <strong>traslación</strong>,
          la misma del capítulo 4 y por el mismo motivo medido: sobre esta ventana la isotrópica
          cuesta 555 veces más y hay que estimarla {ent(m10["nsim"])} veces. Esa decisión viaja
          <em>en el dato</em> —el JSON dice <code>{m10["correccion"]}</code>— y no en la prosa,
          para que no se pueda desincronizar. El módulo siguiente enseña el caso en que esa misma
          elección la toma la llamada sin decirlo.</p>
      </div>

{tabs("Una envolvente contra el modelo, no contra el azar", R10.format(**_SUB10), PY10.format(**_SUB10))}
      <p>El bloque de R corre una envolvente pequeña —{ent(39)} simulaciones, unos segundos— para
        que se pueda ejecutar leyendo; el de Python lee la de {ent(m10["nsim"])} que el precálculo
        dejó escrita. Y la comparación entre las dos es material: con 39 la banda es más estrecha
        en nivel ({pct(5, 0)} puntual contra {pct(m10["nivel_puntual_pct"], 1)}) y la observada se
        sale <em>más</em>. Subir <code>nsim</code> no afina la banda por defecto: le cambia el
        contraste. Es exactamente lo que el módulo 11 del capítulo 4 midió.</p>
""" + CIERRE


# =====================================================================
# MÓDULO 11 · Conglomerado y autoexcitación
# =====================================================================
R11 = '''# `kppm` PIDE K POR DENTRO, Y LA PIDE CON EL `correction` POR DEFECTO.
# Sobre una ventana no rectangular eso es la ISOTROPICA —la del capitulo
# 4, la que costaba 555 veces la otra— sin que la llamada la mencione.
# Sobre `redwood`, que vive en un cuadrado, las dos son instantaneas: asi
# que lo que se ve aqui NO es velocidad, es la respuesta cambiando.
data(redwood)
k_iso   &lt;- kppm(redwood ~ 1, &quot;Thomas&quot;)
k_trans &lt;- kppm(redwood ~ 1, &quot;Thomas&quot;,
                statargs = list(correction = &quot;translate&quot;))

round(c(k_iso$clustpar, mu = k_iso$mu), 6)
#&gt;     kappa     scale        mu
#&gt; {ISO}
round(c(k_trans$clustpar, mu = k_trans$mu), 6)
#&gt;     kappa     scale        mu
#&gt; {TRANS}'''

PY11 = '''# La K de un proceso de Thomas tiene forma cerrada, y con ella se ve por
# que dos ajustes tan distintos pueden salir del mismo dato: sus curvas
# de K casi coinciden. El contraste minimo esta buscando el minimo de un
# valle plano, y ahi cualquier cambio en la estimacion de K lo mueve.
def k_thomas(r, kappa, escala):
    return np.pi * r ** 2 + (1 - np.exp(-r ** 2 / (4 * escala ** 2))) / kappa

for r in (500.0, 1000.0, 2000.0):
    a = k_thomas(r, {KI}, {SI})
    b = k_thomas(r, {KT}, {ST})
    print(int(round(r)), round(100 * abs(b - a) / a, 1))
#&gt; 500 0.6
#&gt; 1000 0.9
#&gt; 2000 4.8'''

R11B = '''# HAWKES: el conglomerado en el TIEMPO, y la conexion con fraude y
# sismologia. No es un Poisson con intensidad variable —donde la
# variacion la pone una covariable de fuera— sino uno donde CADA EVENTO
# SUBE la intensidad de los siguientes.
hawkes &lt;- function(mu, alpha, beta, Tmax, semilla) {{
  set.seed(semilla); t &lt;- 0; ev &lt;- numeric(0)
  repeat {{
    # La intensidad DECRECE entre eventos, asi que su valor en t acota el
    # intervalo [t, siguiente): es la cota de Ogata para el adelgazamiento.
    cota &lt;- mu + sum(alpha * exp(-beta * (t - ev)))
    t &lt;- t - log(runif(1)) / cota
    if (t &gt; Tmax) break
    if (runif(1) &lt;= (mu + sum(alpha * exp(-beta * (t - ev)))) / cota) ev &lt;- c(ev, t)
  }}
  ev
}}

ev &lt;- hawkes({MU}, {ALPHA}, {BETA}, {TMAX}, {SEM})
c(eventos = length(ev), tasa = length(ev) / {TMAX},
  teorica = {MU} / (1 - {ALPHA} / {BETA}))
#&gt;    eventos       tasa    teorica
#&gt; {HAW}'''

PY11B = '''# Los tiempos simulados viajan en un CSV, con un Poisson de la MISMA
# tasa media al lado para que la comparacion sea sobre la estructura y no
# sobre el numero de eventos. El indice de dispersion —varianza sobre
# media de los conteos por intervalo— vale 1 bajo Poisson.
h = pd.read_csv(&quot;precalculo/salidas/cap5_hawkes.csv&quot;)

def dispersion(t, tmax={TMAX}.0, k=200):
    c, _ = np.histogram(t, bins=np.linspace(0, tmax, k + 1))
    return c.var(ddof=1) / c.mean()

d_h = dispersion(h.t[h.proceso == &quot;hawkes&quot;].to_numpy())
d_p = dispersion(h.t[h.proceso == &quot;poisson&quot;].to_numpy())
print(round(d_h, 10), round(d_p, 10), round(d_h / d_p, 10))
#&gt; {DISP}'''

_aj = {(a["modelo"], a["correccion"]): a for a in m11["ajustes"]}
_hw = m11["hawkes"]
_e5 = S["e5"]["solucion"]

_SUB11 = dict(
    ISO=" ".join(n(v, 6) for v in (_e5["isotropica"]["kappa"], _e5["isotropica"]["escala"],
                                   _e5["isotropica"]["mu"])),
    TRANS=" ".join(n(v, 6) for v in (_e5["traslacion"]["kappa"], _e5["traslacion"]["escala"],
                                     _e5["traslacion"]["mu"])),
    KI=f'{_aj[("Thomas", "iso")]["parametros"]["kappa"]:g}',
    SI=n(_aj[("Thomas", "iso")]["parametros"]["scale"], 10),
    KT=f'{_aj[("Thomas", "translate")]["parametros"]["kappa"]:g}',
    ST=n(_aj[("Thomas", "translate")]["parametros"]["scale"], 10))

_SUB11B = dict(
    MU=f'{_hw["mu"]:g}', ALPHA=f'{_hw["alpha"]:g}', BETA=f'{_hw["beta"]:g}',
    TMAX=ent(_hw["T"]).replace(" ", ""), SEM=str(D["meta"]["semillas"]["hawkes"]),
    HAW=" ".join((ent(_hw["n_eventos"]).replace(" ", ""),
                  n(_hw["tasa_simulada"], 5), n(_hw["tasa_teorica"], 6))),
    DISP=" ".join(n(v, 10) for v in (_hw["dispersion_hawkes"], _hw["dispersion_poisson"],
                                     _hw["veces_mas_agregado"])))

_dv = {d["modelo"]: d for d in m11["divergencia"]}

MOD11 = cabecera(
    11, "Conglomerado y autoexcitación", "Cluster and self-exciting processes",
    "Ajustar modelos que explican la agregación, descubrir que el ajuste depende "
    "de un argumento que nadie escribe, y llevar la idea al tiempo.") + f"""
      <p>El módulo anterior dejó una pregunta sin cerrar: la intensidad variable no explica que
        los colegios estén cerca unos de otros. Hace falta un modelo donde <strong>los puntos
        vengan en grupos</strong>, y hay tres familias clásicas, todas con la misma forma —unos
        centros invisibles, y alrededor de cada uno una nube de puntos—:</p>

      <table class="tabla-datos">
        <caption>Los tres modelos ajustados al patrón urbano, cada uno por las dos
          correcciones con que se le puede estimar la K</caption>
        <thead><tr><th scope="col">Modelo</th><th scope="col">Qué supone</th>
          <th scope="col">Escala (isotrópica)</th><th scope="col">Escala (traslación)</th>
          <th scope="col">Segundos</th></tr></thead>
        <tbody>
{fila("Thomas", "hijos gaussianos alrededor de cada centro", n(_aj[("Thomas", "iso")]["parametros"]["scale"], 0) + " m", n(_aj[("Thomas", "translate")]["parametros"]["scale"], 0) + " m", n(_dv["Thomas"]["segundos_iso"], 1) + " / " + n(_dv["Thomas"]["segundos_trans"], 2))}{fila("Matérn", "hijos uniformes en un disco", n(_aj[("MatClust", "iso")]["parametros"]["scale"], 0) + " m", n(_aj[("MatClust", "translate")]["parametros"]["scale"], 0) + " m", n(_dv["MatClust"]["segundos_iso"], 1) + " / " + n(_dv["MatClust"]["segundos_trans"], 2))}{fila("Cox log-gaussiano", "la intensidad misma es un campo aleatorio", n(_aj[("LGCP", "iso")]["parametros"]["scale"], 0) + " m", n(_aj[("LGCP", "translate")]["parametros"]["scale"], 0) + " m", n(_dv["LGCP"]["segundos_iso"], 1) + " / " + n(_dv["LGCP"]["segundos_trans"], 2))}        </tbody>
      </table>

      <h3>El argumento que no aparece en la llamada</h3>

      <p>Mírese la columna de los segundos antes que la de las escalas. Los tres modelos tienen
        tres verosimilitudes distintas y tardan <strong>lo mismo</strong>: unos
        {n(_dv["Thomas"]["segundos_iso"], 0)} s cada uno. Cuando tres cosas distintas cuestan lo
        mismo, no se está pagando lo que uno cree estar pagando.</p>

      <p>Lo que se paga es <strong>K</strong>. <code>kppm</code> ajusta por contraste mínimo:
        estima la K empírica del patrón y busca los parámetros cuya K teórica más se le parezca.
        Y pide esa K con el <code>correction</code> por defecto, que sobre una ventana no
        rectangular incluye la <strong>isotrópica</strong> — la del capítulo 4, la que allí costaba
        555 veces la alternativa—. Un <code>statargs = list(correction = "translate")</code> baja
        el ajuste de {n(_dv["Thomas"]["segundos_iso"], 0)} s a
        {n(_dv["Thomas"]["segundos_trans"], 2)} s,
        {firma(n(_dv["Thomas"]["veces_mas_rapido"]), " veces más rápido")}.</p>

      <div class="nota-lateral">
        <h4>Y no es un acelerón: es otra respuesta</h4>
        <p>Se comprobó antes de consagrarlo, y menos mal. Los mismos datos, el mismo modelo, el
          mismo <code>kppm</code>: con la isotrópica, la ciudad son conglomerados de
          <strong>{n(_aj[("Thomas", "iso")]["mu"], 1)}</strong> sedes con escala
          <strong>{n(_aj[("Thomas", "iso")]["parametros"]["scale"], 0)} m</strong>; con la de
          traslación, conglomerados de
          <strong>{n(_aj[("Thomas", "translate")]["mu"], 1)}</strong> con escala
          <strong>{n(_aj[("Thomas", "translate")]["parametros"]["scale"], 0)} m</strong> y la mitad
          de centros. Un {n(_dv["Thomas"]["parametros"]["kappa"], 1)} % en κ, un
          {n(_dv["Thomas"]["parametros"]["scale"], 1)} % en la escala y un
          {n(_dv["Thomas"]["mu_pct"], 1)} % en μ.</p>
        <p style="margin-bottom:0;">Tampoco es una rareza de esta ventana de 22 piezas: sobre
          <code>redwood</code> —62 puntos en un cuadrado, donde la isotrópica es instantánea y no
          hay ninguna tentación de cambiarla— las dos siguen dando μ =
          {n(_e5["isotropica"]["mu"], 2)} contra {n(_e5["traslacion"]["mu"], 2)}, un
          {n(_e5["diferencias_pct"]["mu"], 1)} %. <strong>El contraste mínimo no ajusta el modelo
          al patrón: lo ajusta a una <em>estimación</em> de K</strong>, y cambiar de estimador
          mueve los parámetros más que cambiar de modelo.</p>
      </div>

{sim("cap5-conglomerado", "Los tres modelos por las dos correcciones",
      "Cada par de barras es el mismo modelo estimado dos veces. Lo que hay que "
      "mirar no es cuál barra es más alta, sino cuánto se separan las dos del "
      "mismo par — y que el orden entre modelos apenas cambia.")}
      <p>La consecuencia es una regla y no una preferencia: <strong>un ajuste de conglomerado sin
        decir con qué estimación de K se hizo está incompleto</strong>. En este material la
        corrección viaja dentro del dato, junto al ajuste, para que no se pueda desincronizar de
        la prosa que la comenta.</p>

{tabs("El mismo kppm con dos correcciones", R11.format(**_SUB11), PY11.format(**_SUB11))}
      <p>La columna de Python explica <em>por qué</em> pasa esto, y es lo que lo hace tolerable:
        evaluada la K teórica de Thomas con los dos juegos de parámetros, las dos curvas se
        diferencian menos de un 1 % a 500 y 1 000 m. <strong>El valle que el contraste mínimo
        está minimizando es casi plano</strong>, así que un cambio pequeño en la K empírica mueve
        mucho el punto donde cae el mínimo. Dos descripciones muy distintas del mismo dato, y las
        dos ajustan casi igual de bien.</p>

      <h3>El cabo que el capítulo 4 dejó abierto</h3>

      <p>La decisión 3 de aquel capítulo conservó los {ent(m11["duplicados"]["repetidos"])} sitios
        con sedes repetidas —varias sedes en un mismo edificio— y los midió en G y en K. Pero
        aquel capítulo <em>describía</em> y este <em>ajusta</em>, y un modelo de conglomerado que
        ve puntos coincidentes tiene que explicarlos con lo único que tiene: una escala diminuta.
        La hipótesis era que los duplicados descuadrarían el ajuste.</p>

      <p><strong>Se midió y la hipótesis es falsa</strong>, y por eso vale publicarla: quitando
        los {ent(m11["duplicados"]["repetidos"])} repetidos, la escala de Thomas pasa de
        {n(m11["duplicados"]["efecto"][0]["con_duplicados"]["scale"], 0)} m a
        {n(m11["duplicados"]["efecto"][0]["sin_duplicados"]["scale"], 0)} m —un
        {n(m11["duplicados"]["efecto"][0]["cambio_pct"]["scale"], 1)} %— y el mayor cambio entre
        los tres modelos y todos sus parámetros es de
        {firma(n(m11["duplicados"]["cambio_maximo_pct"], 1), " %")}. El capítulo cierra el cabo
        con una cifra en vez de dejar al lector suponiendo en cualquiera de los dos sentidos.</p>

      <h3>Y la misma idea en el tiempo: procesos autoexcitados</h3>

      <p>Un proceso de conglomerado espacial supone centros invisibles. En el tiempo hay una
        variante donde los centros son <em>los propios eventos</em>: cada uno sube la intensidad
        de los siguientes, que es lo que se llama un <strong>proceso de Hawkes</strong>.</p>

      <div class="formula-destacada">
        $$\\lambda(t) \;=\; \\mu \;+\; \\sum_{{t_i &lt; t}} \\alpha\\, e^{{-\\beta (t - t_i)}}$$
      </div>

      <p>Es el modelo de la réplica sísmica —cada terremoto dispara sus propias réplicas, y de ahí
        viene: Ogata lo llevó a la sismología y de paso dio el algoritmo con que se simula, el
        adelgazamiento— y el de la ráfaga de fraude —una tarjeta comprometida se usa varias veces
        seguidas—. Su parámetro
        que manda es la <strong>razón de ramificación</strong> α/β, el número esperado de hijos
        por evento: con {n(_hw["razon_ramificacion"], 4)} el proceso no explota, y su tasa media
        vale μ/(1 − α/β) = {n(_hw["tasa_teorica"], 4)} eventos por unidad de tiempo. La simulación
        da {n(_hw["tasa_simulada"], 4)}, así que la fórmula no se cita: se comprueba.</p>

{sim("cap5-hawkes", "Un Hawkes contra un Poisson de su misma tasa",
      "Los dos procesos tienen el mismo número de eventos y la misma tasa media. "
      "Lo único distinto es cómo se reparten, y el índice de dispersión lo mide: "
      "vale 1 bajo Poisson.")}
      <p>Con {ent(_hw["n_eventos"])} eventos cada uno, el índice de dispersión del Hawkes vale
        {firma(n(_hw["dispersion_hawkes"]))} y el del Poisson
        {firma(n(_hw["dispersion_poisson"]))}: {n(_hw["veces_mas_agregado"], 1)} veces más
        agregado con <em>la misma tasa media</em>. Es la lección del capítulo 4 en una dimensión
        —la intensidad no describe el patrón— y la razón por la que un detector de fraude que
        modele las transacciones como Poisson va a subestimar sistemáticamente las ráfagas.</p>

{tabs("Un Hawkes por adelgazamiento de Ogata", R11B.format(**_SUB11B), PY11B.format(**_SUB11B))}
      <p>Y con esto el capítulo tiene todas las piezas: estimar la intensidad, elegirle el ancho,
        corregirle el borde, dividir dos, modelarla con covariables, leer los coeficientes,
        diagnosticar el ajuste y, cuando el diagnóstico dice que no basta, cambiar de familia de
        modelo. El módulo siguiente lo comprueba y abre el proyecto integrador.</p>
""" + CIERRE

# =====================================================================
# MÓDULO 12 · Autoevaluación y ejercicios guiados
# =====================================================================
import re as _re


def _codigo(texto):
    """Los backticks del enunciado pasan a <code>, no se borran.

    El capítulo 4 los quitaba, y con ellos se iba la única marca de que
    `bw.ppl` es una función y no una palabra. Aquí se convierten.
    """
    return _re.sub(r"`([^`]+)`", r"<code>\1</code>", texto)


def ejercicio(k, e):
    """El marcado de la CASA, no uno inventado.

    `cuenta_sitio.py` cuenta los ejercicios por `.ejercicio-guiado` y el
    desplegable se cablea por `.ejercicio-boton`; inventarse selectores
    deja un capítulo que se ve perfecto, con cero ejercicios contados y
    los botones muertos, sin un solo error en consola (A.13).
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
            <button type="button" class="ejercicio-boton" aria-expanded="false" aria-controls="cap5-e{k}-sol">
              <i class="fas fa-key" aria-hidden="true"></i> Solución <i class="fas fa-chevron-down" aria-hidden="true"></i>
            </button>
          </div>
          <div class="ejercicio-panel solucion" id="cap5-e{k}-sol" hidden>
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


# Las soluciones viajan como e1…e5 y no como una lista: cada ejercicio es
# una clave, para que el auditor pueda nombrarlos.
EJERCICIOS = [S[f"e{i}"] for i in range(1, S["meta"]["n_ejercicios"] + 1)]
EJ = "".join(ejercicio(i + 1, e) for i, e in enumerate(EJERCICIOS))

MOD12 = cabecera(
    12, "Autoevaluación y ejercicios", "Self-assessment and guided exercises",
    "Comprobar lo aprendido, practicar sobre datos reales las decisiones que este "
    "capítulo obliga a declarar, y formular el proyecto integrador."
) + f"""      <p>El capítulo ha defendido una idea desde el módulo 1, y conviene decirla entera antes
        de comprobarla: <strong>una superficie de intensidad no es una descripción del dato, es
        una respuesta a una pregunta que alguien formuló</strong> —con qué ancho, con qué
        corrección, sobre qué ventana, contra qué referencia—. Los doce módulos han ido
        enseñando dónde vive cada una de esas decisiones y qué pasa cuando no se escribe.</p>

      <p>Ocho preguntas, sin nota, que se suman a las cuatro del módulo 6. Cada opción trae su
        explicación, así que equivocarse aquí vale tanto como acertar.</p>

{quiz_html('cap5-quiz', 'Autoevaluación del capítulo 5',
           'Ocho preguntas sobre ancho de banda, corrección de borde, riesgo relativo, '
           'covariables, ppm y modelos de conglomerado.')}

      <p>Y cinco ejercicios guiados con su solución calculada —uno más que el molde, porque el
        capítulo cubre tres semanas—. Los cinco terminan en una decisión que hay que defender, y
        cuatro de los cinco piden reconocer <em>un resultado que sale bien y no se puede
        creer</em>, que es lo que este capítulo entrena de verdad.</p>

{EJ}
      <div class="tip-box">
        <h4>El proyecto integrador, formulado</h4>
        <p>Con este capítulo se cierra el módulo de patrones puntuales y se abre el trabajo que
          se entrega al final del curso. El enunciado completo y su rúbrica viven en el capítulo
          10; lo que toca aquí es <strong>elegir el patrón y declarar sus decisiones</strong>,
          que es la parte que no se puede improvisar en la última semana.</p>
        <p style="margin-bottom:0;">Un proyecto de este bloque tiene que traer, por escrito y
          antes de la primera figura: la <strong>ventana</strong> y por qué esa; el
          <strong>ancho de banda</strong> y qué selector lo eligió —o por qué ninguno—; la
          <strong>corrección de borde</strong> y qué conserva; y, si hay modelo, la
          <strong>cuadratura</strong> y la <strong>estimación de K</strong> con que se ajustó.
          Cinco líneas. Son exactamente las cinco que este capítulo ha demostrado que cambian el
          resultado sin cambiar la llamada.</p>
      </div>

      <div class="tip-box">
        <h4>Dónde sigue esto</h4>
        <p style="margin-bottom:0;">El capítulo 6 cambia de tipo de dato: de puntos sueltos a
          <strong>datos de área</strong> —conteos y tasas por unidad administrativa— y a la
          matriz de pesos espaciales, que es la que decide quién es vecino de quién. La pregunta
          que abre aquel capítulo es prima de la que abrió éste: si aquí el ancho de banda lo
          decidía todo, allí lo decidirá la matriz. Los anteriores son
          <a href="capitulo-1-datos-espaciales.html">Datos espaciales y la primera ley de la
          geografía</a>, <a href="capitulo-2-crs-georreferenciacion.html">SIG, sistemas de
          referencia y georreferenciación</a>,
          <a href="capitulo-3-cartografia-maup.html">Cartografía estadística y el MAUP</a> —cuyo
          efecto de escala reaparece aquí cada vez que se cambia de rejilla— y
          <a href="capitulo-4-patrones-puntuales.html">Patrones puntuales: descripción, CSR y
          funciones de resumen</a>, que este capítulo continúa módulo a módulo.</p>
      </div>
""" + CIERRE

MODULOS = (MOD1 + MOD2 + MOD3 + MOD4 + MOD5 + MOD6
           + MOD7 + MOD8 + MOD9 + MOD10 + MOD11 + MOD12)


# =====================================================================
# El bloque de datos del capítulo
# =====================================================================
COURSE_DATA = (
    "    const courseData = {\n      modules: [\n"
    + "".join(f"        {{ id: {i + 1}, title: {json.dumps(t, ensure_ascii=False)}, "
              f"subtitle: {json.dumps(s, ensure_ascii=False)} }},\n"
              for i, (t, s) in enumerate(TITULOS))
    + "      ]\n    };\n\n"
    + "    // Todas las cifras del capítulo, tal como salieron del precálculo.\n"
    + "    // El JavaScript no lleva ninguna escrita: las saca de aquí.\n"
    + "    const DATOS_CAP5 = " + json.dumps(D, ensure_ascii=False) + ";\n"
    + "    const SOL_CAP5 = " + json.dumps(S, ensure_ascii=False) + ";\n"
    + "    const D5 = DATOS_CAP5;\n"
)


# =====================================================================
# Los mapas
#
# LOS RÁSTERES VIAJAN EMPAQUETADOS, y la ida y vuelta se comprueba AQUÍ.
# `ida_y_vuelta()` comprime y deshace en el acto: si el resultado no es el
# original byte a byte, el ensamblado para. Un ráster mal comprimido no
# revienta —se dibuja distinto—, y un mapa de calor mentido se ve igual de
# plausible que uno correcto.
# =====================================================================
def _empaqueta(mapa):
    return ida_y_vuelta(mapa) if mapa.get("modo") == "rejilla" else mapa


def geomapa(ident, clave, extra=""):
    fuente = json.dumps(_empaqueta(M[clave]), ensure_ascii=False)
    return f"    GEOMAPAS['{ident}'] = {{ fuente: {fuente}{extra} }};\n"


def _etq(texto):
    return ", etiqueta: " + json.dumps(texto, ensure_ascii=False)


# LA FAMILIA DEL DESLIZADOR ES UNA FUNCIÓN, Y BUSCA POR SIGMA.
# El capítulo 1 pagó esta lección dos veces (T1.2 y T1.3): emparejar dos
# listas por su posición las descuadra en silencio. Y este capítulo casi la
# paga una tercera, porque el mismo sigma salía con ocho dígitos en un JSON
# y con diez en el otro — así que la clave no coincidía ni consigo misma.
# Se arregló redondeando sigma en el origen; la comprobación de que las dos
# listas siguen casando está en `main()` y para el ensamblado.
FAMILIA_JS = (
    "    // Las siete superficies, con su sigma dentro de cada una.\n"
    "    const FAM5 = " + json.dumps([_empaqueta(g) for g in M["kennedy_familia"]],
                                     ensure_ascii=False) + ";\n"
    "    // POR SU SIGMA, NUNCA POR SU POSICIÓN. Ver T1.2 y T1.3 del plan.\n"
    "    function superficieDeSigma(s) { return FAM5.find(g => g.sigma_m === s); }\n"
    "    let famIdx = 0;\n"
)

# LA TABLA DE RESPALDO DEL DESLIZADOR, y es la lección del A.20.2 del
# capítulo 4 aplicada aquí: siete mapas y ninguna vía al dato para quien
# no ve el lienzo. El módulo 2 dice «mueve el deslizador y mira la ciudad,
# no la cifra», y su tesis —que el ancho lo decide todo— se sostiene sobre
# SIETE máximos de los que la prosa solo publica el primero y el último.
# Los cinco de en medio viven únicamente dentro del simulador. Para quien
# no ve el mapa, esta tabla ES el módulo.
#
# Aquí no se calcula nada: `celdas_por_sigma` sale de dividir dos cifras
# que R publica, y esa división la hace el navegador igual que la hace el
# simulador de al lado, sobre el mismo dato y a la vista.
TABLA_FAMILIA = """, tabla: function () {
        const f = D5.m2.familia;
        const filas = f.sigmas_m.map((s, i) =>
          `<tr><th scope="row">${n5(s, 0)} m</th>`
          + `<td>${n5(s / f.celda_m, 1)}</td>`
          + `<td>${n5(f.max_km2[i], 1)}</td></tr>`).join('');
        return `<table><caption>Las ${f.n} superficies del deslizador, `
          + `sobre la misma rejilla de ${f.nx}\u00d7${f.ny} celdas de `
          + `${n5(f.celda_m, 0)} m. La escala de color es común a las siete: `
          + `por eso la mancha se apaga al abrir el n\u00facleo.</caption>`
          + `<thead><tr><th scope="col">Ancho de banda \u03c3</th>`
          + `<th scope="col">Celdas por \u03c3</th>`
          + `<th scope="col">Intensidad m\u00e1xima (por km\u00b2)</th></tr></thead>`
          + `<tbody>${filas}</tbody></table>`;
      }"""


GEOMAPAS_JS = (
    FAMILIA_JS
    + geomapa('cap5-kennedy', 'kennedy_puntos',
              _etq('Las 262 sedes educativas que caen dentro de la ventana de Kennedy, '
                   'sobre el contorno de la localidad.'))
    + "    GEOMAPAS['cap5-familia'] = {\n"
      "      fuente: () => superficieDeSigma(D5.m2.familia.sigmas_m[famIdx]),\n"
      "      paleta: 'naranja',\n"
      "      etiqueta: 'Intensidad de sedes educativas en Kennedy estimada por núcleos, "
      "sobre una rejilla de " + str(FAM["nx"]) + " por " + str(FAM["ny"]) + " celdas; "
      "el ancho de banda se controla con el deslizador.'\n"
      + TABLA_FAMILIA + "\n    };\n"
    + geomapa('cap5-oferta', 'ciudad_oferta', ", paleta: 'naranja'" + _etq(
        'Intensidad de sedes educativas sobre la ventana urbana de Bogotá, estimada '
        'por núcleos gaussianos con sigma de 720 metros: la oferta de colegios.'))
    + geomapa('cap5-estudiantes', 'ciudad_estudiantes', ", paleta: 'naranja'" + _etq(
        'La misma estimación sobre las sedes con grado 11, pesada cada una por sus '
        'evaluados en Saber 11: dónde están los estudiantes, no los edificios.'))
    + geomapa('cap5-proporcion', 'proporcion_oficial', ", paleta: 'divergente'" + _etq(
        'Proporción de sedes oficiales sobre el total, estimada como cociente de dos '
        'intensidades; la escala va fija de cero a uno y el punto medio es la mitad.'))
    + geomapa('cap5-sector', 'sector_puntos', _etq(
        'Las mismas sedes sin suavizar, con un color por sector: 709 oficiales y '
        '1 398 privadas dentro del perímetro urbano.'))
)


# =====================================================================
# EL PREÁMBULO DE JAVASCRIPT DEL CAPÍTULO, Y NO ES DECORACIÓN.
#
# `n5`, la paleta y las tres fábricas de control NO las trae la
# plantilla: las define cada capítulo. Suponerlas costó un
# `ReferenceError` en el capítulo 2 que se llevó por delante
# `iniciarSimuladores()` ENTERO —no el simulador que fallaba: todos—
# porque el bucle no atrapa (A.13, nº 4). Y volvió a pasar aquí: los
# módulos 1 y 2 se escribieron llamando a `grafico()`, `deslizador()`,
# `n5()` y `COLOR`, cuatro nombres que no existían en ninguna parte, así
# que el único simulador del capítulo estaba muerto desde que se escribió
# y el ensamblador informaba «1 simulador» sin inmutarse. Un simulador
# que no arranca no deja hueco en la página: deja el lienzo en blanco.
#
# `.geomapa-boton` y `.control-slider` son las clases de la CASA —están
# en el CSS de la plantilla— y no unas inventadas aquí. Es la lección del
# A.13: un marcado propio se ve perfecto y no lo cuenta nadie.
# =====================================================================
JS_PREAMBULO = r"""
    const n5 = (x, d) => Number(x).toFixed(d == null ? 5 : d);
    const mil5 = x => Math.round(Number(x)).toLocaleString('es-ES').replace(/\./g, ' ');
    // Notación científica en español para las intensidades de orden 1e-07,
    // que en este capítulo son casi todas las de la ciudad.
    const exp5 = (x, d) => Number(x).toExponential(d == null ? 2 : d).replace('.', ',');

    // Fuera de COLORES_GRAFICO a propósito: cuatro colores no llegan para
    // seis series y la paleta de la casa no separa bien en daltonismo.
    const C5 = { verde: '#1a7358', naranja: '#FF6600', gris: '#8a8a8a',
                 azul: '#0072B2', rojo: '#D55E00', morado: '#7B3FA0',
                 verdeSuave: 'rgba(26,115,88,0.18)', grisSuave: 'rgba(138,138,138,0.18)' };

    function lectura5(raiz, pares) {
      const caja = raiz.querySelector('.simulador-lectura');
      if (!caja) return;
      caja.innerHTML = pares.map(p =>
        `<span class="lectura-item"><span class="lectura-etiqueta">${p[0]}</span>` +
        `<span class="lectura-valor">${p[1]}</span></span>`).join('');
    }

    // Botonera sobre `.geomapa-boton`, la clase de la casa. `activo` existe
    // porque hay estado que sobrevive a salir del módulo y volver: sin él,
    // los botones se redibujan con el primero marcado mientras el gráfico
    // sigue en el que el estudiante eligió (lección de T1.3).
    function botonera5(raiz, ops, alPulsar, activo) {
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

    // Deslizador sobre una lista DISCRETA de posiciones medidas, copiado
    // del capítulo 1: `opciones` es [[valor, rótulo]] y lo que se anuncia
    // por `aria-valuetext` es la MAGNITUD, no la posición.
    function deslizador5(raiz, opciones, etiqueta, iniPos, alCambiar) {
      const cont = raiz.querySelector('.simulador-controles');
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
      input.addEventListener('input', () => { pinta(); alCambiar(opciones[+input.value][0]); });
      pinta();
      caja.appendChild(rotulo); caja.appendChild(input); cont.appendChild(caja);
    }

    // CONTRATO DEL MOTOR: un simulador DEVUELVE sus gráficos, para que
    // `destruirSimuladores()` pueda matarlos. No existe `registrarGrafico`.
    function grafico5(raiz, tipo, data, opciones) {
      return new Chart(raiz.querySelector('canvas').getContext('2d'), {
        type: tipo, data: data,
        options: Object.assign({ responsive: true, maintainAspectRatio: false,
                                 animation: false }, opciones || {})
      });
    }

    const curva5 = (xs, ys) => xs.map((x, i) => ({ x: x, y: ys[i] }))
      .filter(p => Number.isFinite(p.x) && Number.isFinite(p.y));

    const ejesXY = (tx, ty) => ({
      x: { type: 'linear', title: { display: true, text: tx } },
      y: { title: { display: true, text: ty } }
    });
"""


SIMULADORES_JS = JS_PREAMBULO + r"""
    // --- Módulo 2 · el pico contra el ancho de banda -----------------
    // La curva NO se mueve: el ancho ya es su eje horizontal. Lo que se
    // mueve es el marcador y el mapa de al lado.
    SIMULADORES['cap5-anchos'] = function (raiz) {
      const f = D5.m2.familia;
      const g = grafico5(raiz, 'line', {
        labels: f.sigmas_m.map(s => n5(s, 0) + ' m'),
        datasets: [{ label: 'intensidad máxima (por km²)', data: f.max_km2,
                     borderColor: C5.verde, backgroundColor: C5.verdeSuave,
                     fill: true, tension: 0.3, pointRadius: 3 }]
      }, { scales: { y: { title: { display: true, text: 'sedes por km²' } },
                     x: { title: { display: true, text: 'ancho de banda σ' } } } });

      const lee = () => lectura5(raiz, [
        ['ancho de banda σ', n5(f.sigmas_m[famIdx], 0) + ' m'],
        ['celdas por σ', n5(f.sigmas_m[famIdx] / f.celda_m, 1)],
        ['intensidad máxima', n5(f.max_km2[famIdx], 1) + ' por km²'],
        ['contra el σ más estrecho', '×' + n5(f.max_km2[famIdx] / f.max_km2[0], 2)]]);

      const pinta = () => {
        g.data.datasets[0].pointRadius = f.sigmas_m.map((_, i) => i === famIdx ? 7 : 3);
        g.update('none');
      };
      // Las posiciones se DERIVAN de las superficies que existen de verdad:
      // si alguna faltara, el control no ofrecería su posición.
      const hay = f.sigmas_m.map((s, i) => [i, n5(s, 0) + ' m'])
                            .filter(par => superficieDeSigma(f.sigmas_m[par[0]]));
      famIdx = hay[0][0];
      deslizador5(raiz, hay, 'ancho de banda σ', 0, v => {
        famIdx = v;
        const m = document.querySelector('[data-geomapa="cap5-familia"]');
        if (m && m.__geomapa) m.__geomapa.dibuja();
        lee(); pinta();
      });
      lee(); pinta();
      return [g];
    };

    // --- Módulo 3 · los cuatro selectores ----------------------------
    SIMULADORES['cap5-selectores'] = function (raiz) {
      const VENT = ['kennedy', 'urbana'];
      const ETQ = ['Kennedy (262 sedes)', 'Ciudad entera (2 107 sedes)'];
      const NOM = ['diggle', 'ppl', 'CvL', 'scott'];
      let i = 0;
      const g = grafico5(raiz, 'bar', { labels: NOM.map(k => 'bw.' + k), datasets: [] }, {
        scales: { y: { beginAtZero: true, title: { display: true, text: 'σ (metros)' } } },
        plugins: { legend: { labels: { filter: it => it.text !== '' } } }
      });
      const pinta = () => {
        const s = D5.m3[VENT[i]], v = NOM.map(k => s.sigmas_m[k]);
        const suelo = D5.m5.rejilla.sigma_minimo_dibujable_m;
        g.data.datasets = [
          { type: 'bar', label: 'σ elegido', data: v,
            backgroundColor: v.map(x => x < suelo ? C5.rojo : C5.verde) },
          { type: 'line', label: 'σ mínimo dibujable sobre la ciudad',
            data: NOM.map(() => suelo), borderColor: C5.gris, borderDash: [5, 4],
            borderWidth: 1.5, pointRadius: 0 }
        ];
        g.update();
        const orden = NOM.slice().sort((a, b) => s.sigmas_m[a] - s.sigmas_m[b]);
        lectura5(raiz, [
          ['ventana', ETQ[i]],
          ['n', mil5(s.n)],
          ['el más estrecho', 'bw.' + orden[0] + ' · ' + n5(s.sigmas_m[orden[0]], 0) + ' m'],
          ['el más ancho', 'bw.' + orden[3] + ' · ' + n5(s.sigmas_m[orden[3]], 0) + ' m'],
          ['cuánto discrepan', '×' + n5(s.razon, 2)],
          ['de menor a mayor', orden.join(' < ')]]);
      };
      botonera5(raiz, ETQ, k => { i = k; pinta(); }, 0);
      pinta();
      return [g];
    };

    // --- Módulo 4 · las tres correcciones de borde -------------------
    SIMULADORES['cap5-borde'] = function (raiz) {
      const t = D5.m4.tabla, n = D5.m4.n;
      let vista = 0;   // 0 = masa integrada, 1 = desviación en %
      const g = grafico5(raiz, 'bar',
        { labels: t.map(f => 'σ = ' + n5(f.sigma_m, 0) + ' m'), datasets: [] }, {
          scales: { y: { title: { display: true, text: '' } } },
          plugins: { legend: { labels: { filter: it => it.text !== '' } } }
        });
      const pinta = () => {
        if (vista === 0) {
          g.data.datasets = [
            { type: 'bar', label: 'sin corregir', data: t.map(f => f.masa_sin_corregir),
              backgroundColor: C5.rojo },
            { type: 'bar', label: 'por defecto', data: t.map(f => f.masa_defecto),
              backgroundColor: C5.naranja },
            { type: 'bar', label: 'diggle = TRUE', data: t.map(f => f.masa_diggle),
              backgroundColor: C5.verde },
            { type: 'line', label: 'n = ' + n, data: t.map(() => n),
              borderColor: C5.gris, borderDash: [5, 4], borderWidth: 2, pointRadius: 0 }
          ];
          g.options.scales.y.title.text = 'integral de la intensidad sobre la ventana';
          g.options.scales.y.min = Math.min.apply(null, t.map(f => f.masa_sin_corregir)) * 0.97;
        } else {
          g.data.datasets = [
            { type: 'bar', label: 'sin corregir', data: t.map(f => f.fuga_sin_corregir_pct),
              backgroundColor: C5.rojo },
            { type: 'bar', label: 'por defecto', data: t.map(f => f.exceso_defecto_pct),
              backgroundColor: C5.naranja },
            { type: 'bar', label: 'diggle = TRUE', data: t.map(f => f.error_diggle_pct),
              backgroundColor: C5.verde }
          ];
          g.options.scales.y.title.text = 'desviación sobre n (%)';
          g.options.scales.y.min = undefined;
        }
        g.update();
        const u = t[t.length - 1];
        lectura5(raiz, [
          ['a σ = ' + n5(u.sigma_m, 0) + ' m, sin corregir', n5(u.fuga_sin_corregir_pct, 2) + ' %'],
          ['por defecto', '+' + n5(u.exceso_defecto_pct, 2) + ' %'],
          ['con diggle', n5(u.error_diggle_pct, 6) + ' %'],
          ['horquilla entre las dos primeras', n5(D5.m4.horquilla_pct, 1) + ' puntos'],
          ['lo que cuesta corregir', n5(D5.m4.coste_segundos.diggle, 2) + ' s contra ' +
                                     n5(D5.m4.coste_segundos.sin_corregir, 2) + ' s']]);
      };
      botonera5(raiz, ['La masa integrada', 'La desviación sobre n'],
                k => { vista = k; pinta(); }, 0);
      pinta();
      return [g];
    };

    // --- Módulo 5 · las tres capas de la ciudad ----------------------
    SIMULADORES['cap5-capas'] = function (raiz) {
      const c = D5.m5.capas;
      const CLAVES = ['oferta', 'grado_11', 'estudiantes'];
      const ETQ = ['Oferta: todas las sedes', 'Bachillerato: con grado 11',
                   'Demanda: evaluados en Saber 11'];
      let i = 0;
      const g = grafico5(raiz, 'bar', {
        labels: ETQ,
        datasets: [{ label: 'máximo de la superficie (por km², escala log)',
                     data: CLAVES.map(k => c[k].max_km2), backgroundColor: C5.verde }]
      }, { scales: { y: { type: 'logarithmic',
                          title: { display: true, text: 'máximo por km² (log)' } } } });
      const pinta = () => {
        g.data.datasets[0].backgroundColor = CLAVES.map((k, j) => j === i ? C5.naranja : C5.verde);
        g.update('none');
        const d = c[CLAVES[i]];
        lectura5(raiz, [
          ['capa', d.que],
          ['puntos que entran', mil5(d.n)],
          ['máximo', n5(d.max_km2, 2) + ' por km²'],
          ['unidad', CLAVES[i] === 'estudiantes' ? 'evaluados por km²' : 'sedes por km²'],
          ['cor(oferta, bachillerato)', n5(D5.m5.cor_oferta_grado11, 4)],
          ['cor(oferta, evaluados)', n5(D5.m5.cor_oferta_estudiantes, 4)],
          ['cor(bachillerato, evaluados)', n5(D5.m5.cor_grado11_estudiantes, 4)]]);
      };
      botonera5(raiz, ETQ, k => { i = k; pinta(); }, 0);
      pinta();
      return [g];
    };

    // --- Módulo 6 · contar puntos contra mirar el mapa ---------------
    SIMULADORES['cap5-riesgo'] = function (raiz) {
      const CLAVES = ['chorley', 'bogota'];
      const ETQ = ['chorley · P(laringe)', 'Bogotá · P(oficial)'];
      let i = 1;
      const g = grafico5(raiz, 'bar',
        { labels: ['mínimo', 'mediana de la superficie', 'máximo'], datasets: [] },
        { scales: { y: { beginAtZero: true, max: 1,
                         title: { display: true, text: 'probabilidad' } } },
          plugins: { legend: { labels: { filter: it => it.text !== '' } } } });
      const pinta = () => {
        const d = D5.m6[CLAVES[i]];
        g.data.datasets = [
          { type: 'bar', label: 'la superficie', data: [d.p_min, d.p_mediana, d.p_max],
            backgroundColor: [C5.gris, C5.naranja, C5.gris] },
          { type: 'line', label: 'proporción contando puntos',
            data: [d.prop_global, d.prop_global, d.prop_global],
            borderColor: C5.verde, borderDash: [5, 4], borderWidth: 2, pointRadius: 0 }
        ];
        g.update();
        const dosGrupos = CLAVES[i] === 'chorley'
          ? [['casos (laringe)', mil5(d.casos)], ['controles (pulmón)', mil5(d.controles)]]
          : [['oficiales', mil5(d.oficiales)], ['privadas', mil5(d.privadas)]];
        lectura5(raiz, dosGrupos.concat([
          ['proporción contando puntos', n5(d.prop_global, 4)],
          ['mediana de la superficie', n5(d.p_mediana, 4)],
          ['la mediana menos la global', n5(d.brecha_mediana_menos_global, 4)],
          ['lectura', d.brecha_mediana_menos_global < 0 ? 'concentrado: mayoría en poca superficie'
                                                        : 'repartido por la ventana'],
          ['orientación comprobada contra el dato', n5(100 * d.orientacion_verificada, 0) + ' %']]));
      };
      botonera5(raiz, ETQ, k => { i = k; pinta(); }, 1);
      pinta();
      return [g];
    };

    // --- Módulo 7 · el titular de una rhohat y su cola ---------------
    SIMULADORES['cap5-rhohat'] = function (raiz) {
      const CUR = [['bei · elevación', D5.m7.bei.elevacion],
                   ['bei · pendiente', D5.m7.bei.pendiente],
                   ['Bogotá · distancia al centro', D5.m7.bogota.curva]];
      let i = 2;
      const g = grafico5(raiz, 'bar', {
        labels: CUR.map(c => c[0]),
        datasets: [
          { label: 'razón en todo el rango', data: CUR.map(c => c[1].razon),
            backgroundColor: C5.rojo },
          { label: 'razón en el bulto (percentiles 5 a 95)',
            data: CUR.map(c => c[1].razon_bulto), backgroundColor: C5.verde }
        ]
      }, { scales: { y: { type: 'logarithmic',
                          title: { display: true, text: 'ρ máximo / ρ mínimo (log)' } } } });
      const pinta = () => {
        const d = CUR[i][1];
        lectura5(raiz, [
          ['curva', CUR[i][0]],
          ['razón en todo el rango', '×' + n5(d.razon, 2)],
          ['razón en el bulto', '×' + n5(d.razon_bulto, 2)],
          ['cuánto infla la cola', '×' + n5(d.cola_infla, 1)],
          ['el bulto va de', n5(d.bulto_desde, 3) + ' a ' + n5(d.bulto_hasta, 3)],
          ['ρ mínimo del bulto', exp5(d.rho_min_bulto, 3)],
          ['ρ máximo del bulto', exp5(d.rho_max_bulto, 3)]]);
      };
      botonera5(raiz, CUR.map(c => c[0]), k => { i = k; pinta(); }, 2);
      pinta();
      return [g];
    };

    // --- Módulo 8 · la cuadratura ------------------------------------
    SIMULADORES['cap5-cuadratura'] = function (raiz) {
      const t = D5.m8.cuadratura.tabla;
      let vista = 0;
      const g = grafico5(raiz, 'line',
        { labels: t.map(z => 'nd = ' + z.nd), datasets: [] },
        { scales: { y: { title: { display: true, text: '' } } },
          plugins: { legend: { labels: { filter: it => it.text !== '' } } } });
      const pinta = () => {
        if (vista === 0) {
          g.data.datasets = [
            { label: 'techo (± 1 error estándar)',
              data: t.map(z => z.pendiente + z.ee_pendiente),
              borderColor: C5.gris, pointRadius: 0, fill: '+1',
              backgroundColor: C5.grisSuave },
            { label: '', data: t.map(z => z.pendiente - z.ee_pendiente),
              borderColor: C5.gris, pointRadius: 0 },
            { label: 'coeficiente de la distancia', data: t.map(z => z.pendiente),
              borderColor: C5.verde, borderWidth: 3, pointRadius: 4 },
            { label: 'cero', data: t.map(() => 0), borderColor: C5.rojo,
              borderDash: [5, 4], borderWidth: 1.5, pointRadius: 0 }
          ];
          g.options.scales.y.title.text = 'coeficiente ± 1 e.e.';
        } else {
          g.data.datasets = [
            { label: 'AIC', data: t.map(z => z.aic), borderColor: C5.naranja,
              backgroundColor: 'rgba(255,102,0,0.15)', fill: true,
              borderWidth: 3, pointRadius: 4 }
          ];
          g.options.scales.y.title.text = 'AIC';
        }
        g.update();
        lectura5(raiz, [
          ['nd por defecto', D5.m8.cuadratura.defecto_nd],
          ['puntos ficticios que pone', mil5(D5.m8.cuadratura.defecto_ficticios)],
          ['con nd = ' + t[t.length - 1].nd, mil5(t[t.length - 1].ficticios) + ' ficticios'],
          ['el coeficiente se mueve', n5(D5.m8.cuadratura.rango_pendiente_en_ee, 2) +
                                      ' errores estándar'],
          ['el AIC se mueve', n5(D5.m8.cuadratura.rango_aic, 1) + ' puntos'],
          ['consecuencia', 'dos ppm con cuadraturas distintas no se comparan por AIC']]);
      };
      botonera5(raiz, ['El coeficiente y su error', 'El AIC'],
                k => { vista = k; pinta(); }, 0);
      pinta();
      return [g];
    };

    // --- Módulo 9 · tres ajustes, y cuál se puede leer ---------------
    SIMULADORES['cap5-ppm'] = function (raiz) {
      const CLAVES = ['crudo', 'centrado', 'distancia'];
      const ETQ = ['~ x + y (crudo)', '~ xc + yc (centrado)', '~ dcen'];
      let i = 0;
      const g = grafico5(raiz, 'bar', { labels: [], datasets: [] }, {
        scales: { y: { beginAtZero: true, title: { display: true, text: '|z|' } } },
        plugins: { legend: { labels: { filter: it => it.text !== '' } } }
      });
      const pinta = () => {
        const a = D5.m9[CLAVES[i]];
        g.data.labels = a.nombres;
        g.data.datasets = [
          { type: 'bar', label: a.singular ? 'sin errores estándar: no hay z' : '|z| por coeficiente',
            data: a.z ? a.z.map(Math.abs) : a.nombres.map(() => 0),
            backgroundColor: a.singular ? C5.rojo : C5.verde },
          { type: 'line', label: '|z| = 1.96', data: a.nombres.map(() => 1.96),
            borderColor: C5.naranja, borderDash: [5, 4], borderWidth: 1.5, pointRadius: 0 }
        ];
        g.update();
        lectura5(raiz, [
          ['parametrización', a.que],
          ['¿hay errores estándar?', a.singular ? 'NO: vcov() devuelve NULL' : 'sí, uno por coeficiente'],
          ['número de condición recíproco',
           a.cond_reciproco == null ? '—' : exp5(a.cond_reciproco, 3)],
          ['AIC', n5(a.aic, 1)],
          ['pendiente principal', a.nombres[1] + ' = ' + exp5(a.coef[1], 4)],
          ['su z', a.z ? n5(a.z[1], 2) : 'no calculable']]);
      };
      botonera5(raiz, ETQ, k => { i = k; pinta(); }, 0);
      pinta();
      return [g];
    };

    // --- Módulo 10 · la envolvente sobre el modelo ajustado ----------
    SIMULADORES['cap5-envolvente'] = function (raiz) {
      const c = D5.m10.curva;
      let escala = 0;
      const g = grafico5(raiz, 'line', { datasets: [] }, {
        parsing: false, scales: ejesXY('r (metros)', 'K inhomogénea'),
        plugins: { legend: { labels: { filter: it => it.text !== '' } } }
      });
      const pinta = () => {
        g.data.datasets = [
          { label: 'techo de la banda', data: curva5(c.r, c.hi), borderColor: C5.gris,
            pointRadius: 0, fill: '+1', backgroundColor: C5.grisSuave },
          { label: '', data: curva5(c.r, c.lo), borderColor: C5.gris, pointRadius: 0 },
          { label: 'media de las simulaciones', data: curva5(c.r, c.mmean),
            borderColor: C5.naranja, borderDash: [6, 4], pointRadius: 0 },
          { label: 'K inhomogénea observada', data: curva5(c.r, c.obs),
            borderColor: C5.verde, borderWidth: 3, pointRadius: 0 }
        ];
        g.options.scales.y.type = escala === 1 ? 'logarithmic' : 'linear';
        g.update();
        lectura5(raiz, [
          ['modelo simulado', D5.m10.modelo],
          ['simulaciones', mil5(D5.m10.nsim)],
          ['corrección de K', D5.m10.correccion],
          ['nivel puntual de la banda', n5(D5.m10.nivel_puntual_pct, 1) + ' %'],
          ['radios fuera de la banda', n5(D5.m10.pct_r_fuera_de_banda, 0) + ' %'],
          ['desde r =', n5(D5.m10.primer_r_fuera_m, 0) + ' m'],
          ['veredicto', D5.m10.veredicto]]);
      };
      botonera5(raiz, ['Escala lineal', 'Escala logarítmica'],
                k => { escala = k; pinta(); }, 0);
      pinta();
      return [g];
    };

    // --- Módulo 11 · los tres modelos por las dos correcciones -------
    SIMULADORES['cap5-conglomerado'] = function (raiz) {
      const A = D5.m11.ajustes, DIV = D5.m11.divergencia;
      const MOD = ['Thomas', 'MatClust', 'LGCP'];
      const de = (m, c) => A.find(a => a.modelo === m && a.correccion === c);
      let vista = 0;   // 0 = escala, 1 = mu, 2 = segundos
      const g = grafico5(raiz, 'bar', { labels: MOD, datasets: [] },
        { scales: { y: { beginAtZero: true, title: { display: true, text: '' } } } });
      const CAMPOS = [
        ['escala del conglomerado (m)', a => a.parametros.scale],
        ['μ (puntos por conglomerado, o media del campo)', a => a.mu],
        ['segundos que tarda el ajuste', a => a.segundos]
      ];
      const pinta = () => {
        const f = CAMPOS[vista][1];
        g.data.datasets = [
          { label: 'K isotrópica (el defecto, sin escribirlo)',
            data: MOD.map(m => f(de(m, 'iso'))), backgroundColor: C5.rojo },
          { label: 'K de traslación (statargs)',
            data: MOD.map(m => f(de(m, 'translate'))), backgroundColor: C5.verde }
        ];
        g.options.scales.y.title.text = CAMPOS[vista][0];
        g.options.scales.y.type = vista === 2 ? 'logarithmic' : 'linear';
        g.update();
        const d = DIV[0];
        lectura5(raiz, [
          ['Thomas · κ se mueve', n5(d.parametros.kappa, 1) + ' %'],
          ['la escala se mueve', n5(d.parametros.scale, 1) + ' %'],
          ['μ se mueve', n5(d.mu_pct, 1) + ' %'],
          ['isotrópica contra traslación', n5(d.segundos_iso, 1) + ' s contra ' +
                                           n5(d.segundos_trans, 2) + ' s'],
          ['veces más rápido', '×' + n5(d.veces_mas_rapido, 0)],
          ['quitar los duplicados mueve, como mucho',
           n5(D5.m11.duplicados.cambio_maximo_pct, 1) + ' %']]);
      };
      botonera5(raiz, CAMPOS.map(c => c[0].split(' (')[0]),
                k => { vista = k; pinta(); }, 0);
      pinta();
      return [g];
    };

    // --- Módulo 11 · Hawkes contra su propio Poisson -----------------
    SIMULADORES['cap5-hawkes'] = function (raiz) {
      const h = D5.m11.hawkes;
      const g = grafico5(raiz, 'bar', {
        labels: ['Hawkes autoexcitado', 'Poisson de la misma tasa'],
        datasets: [
          { type: 'bar', label: 'índice de dispersión (varianza / media)',
            data: [h.dispersion_hawkes, h.dispersion_poisson],
            backgroundColor: [C5.rojo, C5.verde] },
          { type: 'line', label: 'lo que vale bajo Poisson', data: [1, 1],
            borderColor: C5.gris, borderDash: [5, 4], borderWidth: 2, pointRadius: 0 }
        ]
      }, { scales: { y: { beginAtZero: true,
                          title: { display: true, text: 'varianza / media de los conteos' } } } });
      lectura5(raiz, [
        ['μ, α, β', h.mu + ', ' + h.alpha + ', ' + h.beta],
        ['razón de ramificación α/β', n5(h.razon_ramificacion, 4)],
        ['tasa teórica μ/(1 − α/β)', n5(h.tasa_teorica, 4)],
        ['tasa simulada', n5(h.tasa_simulada, 4)],
        ['eventos en ' + mil5(h.T) + ' unidades', mil5(h.n_eventos)],
        ['veces más agregado que su Poisson', '×' + n5(h.veces_mas_agregado, 1)]]);
      return [g];
    };
"""


# =====================================================================
# LAS DOCE PREGUNTAS: cuatro en el módulo 6 y ocho en el 12.
#
# LA CLAVE DE LA RETROALIMENTACIÓN POR OPCIÓN ES `retro`, Y NO ES UN
# DETALLE DE ESTILO. El motor de la plantilla lee `op.retro`; los
# capítulos 3 y 4 escribieron `respuesta`, así que sus 68 explicaciones
# por opción NUNCA se dibujan —`cerrar()` tiene una guarda `|| ''` que
# convierte la ausencia en cadena vacía, así que el estudiante ve
# «Correcto.» a secas y la consola queda limpia—. Lo mismo con las
# numéricas: el motor lee `retroAcierto`/`retroFallo` y aquellos
# capítulos escribieron `explicacion`. Aquí se usan los nombres del
# motor, y `main()` lo COMPRUEBA: una clave equivocada para el
# ensamblado en vez de publicarse en silencio.
#
# Ninguna respuesta lleva cifras escritas: todas salen de D5.
# =====================================================================
QUIZ_JS = r"""
    AUTOEVALUACIONES['cap5-trampas'] = [
      {
        tipo: 'opcion',
        pista: 'Piensa en qué le pide cada selector al ancho de banda.',
        pregunta: 'Dos personas estiman la intensidad del mismo patrón y publican dos mapas distintos. Una usó <code>bw.diggle</code> y la otra <code>bw.scott</code>. ¿Quién se equivocó?',
        opciones: [
          { texto: 'Ninguna de las dos: cada selector optimiza una cosa distinta', correcta: true,
            retro: 'Eso es. Sobre la ciudad los cuatro selectores se abren en un factor de ' + n5(D5.m3.urbana.razon, 2) + ', de ' + n5(D5.m3.urbana.sigmas_m.ppl, 0) + ' m a ' + n5(D5.m3.urbana.sigmas_m.scott, 0) + ' m. Lo que falta en los dos mapas no es corrección: es decir cuál se usó.' },
          { texto: 'La que usó bw.scott, porque es la regla más burda',
            retro: 'Es la más simple —forma cerrada, sd por n elevado a menos un sexto— pero eso no la hace incorrecta. Sobre Kennedy da ' + n5(D5.m3.kennedy.sigmas_m.scott, 0) + ' m, que está en el mismo orden que las otras tres.' },
          { texto: 'La que usó bw.diggle, porque la validación cruzada es inestable',
            retro: 'La validación cruzada puede ser inestable, pero aquí las dos dan valores razonables. El problema no es la estabilidad: es que optimizan criterios distintos.' },
          { texto: 'Las dos, porque el ancho hay que elegirlo a ojo',
            retro: 'A ojo es peor, no mejor: un ancho elegido a ojo tampoco se puede declarar ni reproducir. Lo que hay que hacer es elegir y decirlo.' }
        ] },
      {
        tipo: 'multiple',
        pista: 'Son dos. Una tiene que ver con lo que se conserva y la otra con lo que cuesta.',
        pregunta: 'Marca <strong>todo</strong> lo que es cierto de la corrección de borde en la KDE.',
        retroAcierto: 'Las dos: solo la de Diggle conserva el conteo, y ninguna de las tres cuesta nada apreciable.',
        retroFallo: 'Las correctas son la primera y la segunda.',
        opciones: [
          { texto: 'Solo <code>diggle = TRUE</code> hace que la integral devuelva n exactamente', correcta: true,
            retro: 'Divide en el punto donde ESTÁ el dato, así que cada punto aporta exactamente 1. Medido a σ = ' + n5(D5.m4.sigmas_m[2], 0) + ' m: ' + n5(D5.m4.tabla[2].masa_diggle, 2) + ' contra n = ' + D5.m4.n + '.' },
          { texto: 'Las tres opciones cuestan prácticamente lo mismo', correcta: true,
            retro: 'Cronometrado: ' + n5(D5.m4.coste_segundos.defecto, 2) + ' s por defecto, ' + n5(D5.m4.coste_segundos.sin_corregir, 2) + ' s sin corregir y ' + n5(D5.m4.coste_segundos.diggle, 2) + ' s con Diggle. La KDE se paga por píxel, no por perímetro.' },
          { texto: 'Sin corregir, la desviación no depende del ancho de banda',
            retro: 'Depende, y mucho: la fuga pasa de ' + n5(D5.m4.tabla[0].fuga_sin_corregir_pct, 2) + ' % a σ = ' + n5(D5.m4.sigmas_m[0], 0) + ' m a ' + n5(D5.m4.tabla[2].fuga_sin_corregir_pct, 2) + ' % a σ = ' + n5(D5.m4.sigmas_m[2], 0) + '.' },
          { texto: 'Un mapa sin corregir se distingue del corregido a simple vista',
            retro: 'No se distingue: los tres mapas de calor salen plausibles. Por eso la comprobación es la integral y no la mirada.' }
        ] },
      {
        tipo: 'numerica',
        pista: 'Tres celdas por sigma, y la celda de Kennedy mide 77.8 m.',
        pregunta: 'La rejilla de Kennedy tiene celdas de ' + n5(D5.m2.familia.celda_m, 1) + ' m y el capítulo exige al menos ' + D5.meta.rejilla.celdas_por_sigma + ' celdas por σ para que el mapa dibuje el núcleo y no la rejilla. ¿Cuál es el σ más estrecho que ese mapa puede dibujar, en metros?',
        respuesta: D5.m2.familia.sigmas_m[0], tolerancia: 1,
        unidad: 'm',
        retroAcierto: 'Son ' + n5(D5.m2.familia.celda_m, 1) + ' × ' + D5.meta.rejilla.celdas_por_sigma + ' = ' + n5(D5.m2.familia.sigmas_m[0], 1) + ' m, y ese suelo NO es una preferencia: es lo que decide bajar el deslizador de la ciudad entera a una localidad.',
        retroFallo: 'Es la celda por el número de celdas exigidas: ' + n5(D5.m2.familia.celda_m, 1) + ' × ' + D5.meta.rejilla.celdas_por_sigma + '. Una celda más ancha que el núcleo no dibuja el núcleo: dibuja la rejilla.'
      },
      {
        tipo: 'opcion',
        pista: 'Los niveles de un factor se ordenan alfabéticamente.',
        pregunta: 'Se marca un patrón con <code>factor(c("oficial", "privado"))</code> y se llama a <code>relrisk</code>. El mapa que sale, ¿qué probabilidad pinta?',
        opciones: [
          { texto: 'P(privado), porque devuelve el SEGUNDO nivel del factor', correcta: true,
            retro: 'Y es el defecto que casi publica el módulo 6 al revés: el mapa correcto con el título contrario, todo corriendo y sin un aviso. La guarda que lo caza no es leer la ayuda: es comprobar que donde el mapa es máximo los vecinos son de ese tipo. Medido aquí: ' + n5(100 * D5.m6.bogota.orientacion_verificada, 0) + ' % de oficiales en el máximo, contra ' + n5(100 * D5.m6.bogota.prop_global, 0) + ' % global.' },
          { texto: 'P(oficial), porque es el primer nivel',
            retro: 'Justo al revés. El primer nivel es la referencia; lo que se pinta es el segundo.' },
          { texto: 'Las dos, en dos capas',
            retro: 'Con dos niveles devuelve una sola superficie: la otra es su complemento a uno.' },
          { texto: 'Depende del sigma',
            retro: 'El sigma cambia lo suave que sale el mapa, no de qué nivel es la probabilidad.' }
        ] }
    ];

    AUTOEVALUACIONES['cap5-quiz'] = [
      {
        tipo: 'opcion',
        pista: 'El test de cuadrantes también estimaba intensidad local.',
        pregunta: 'Contar en cuadrantes ya estimaba la intensidad local. ¿Qué dos cosas le arregla el estimador por núcleos?',
        opciones: [
          { texto: 'Que las vecindades se solapen y que sus bordes no los ponga una rejilla', correcta: true,
            retro: 'Eso es. Contar en celdas ya era suavizar con un núcleo de caja y sin solapamiento; lo que cambia es el peso y la vecindad, no la idea. Sobre Kennedy los cuadrantes daban entre ' + n5(D5.m1.cuadrantes.intensidad_min_km2, 1) + ' y ' + n5(D5.m1.cuadrantes.intensidad_max_km2, 1) + ' sedes por km².' },
          { texto: 'Que la estimación sea insesgada y que no dependa de la ventana',
            retro: 'Ni una ni otra: la KDE sigue dependiendo de la ventana —el módulo 4 va justo de eso— y su corrección de borde por defecto ni siquiera conserva el conteo.' },
          { texto: 'Que no haga falta elegir ningún parámetro',
            retro: 'Al revés: el tamaño de celda se cambia por σ, que decide todavía más. El módulo 2 lo mide.' },
          { texto: 'Que funcione con patrones marcados',
            retro: 'Las marcas son otra cosa —el módulo 6— y el conteo por cuadrantes también admite separarlas.' }
        ] },
      {
        tipo: 'numerica',
        pista: 'La corrección de Diggle divide en el punto donde está el dato.',
        pregunta: 'Se estima la intensidad de las ' + D5.m4.n + ' sedes de Kennedy con <code>diggle = TRUE</code> y se integra la superficie sobre la ventana. ¿Qué valor da?',
        respuesta: D5.m4.n, tolerancia: 0.5,
        retroAcierto: 'Da n exactamente, a cualquier σ: es la única de las tres correcciones que conserva el conteo, y lo hace por construcción.',
        retroFallo: 'Da ' + D5.m4.n + ', el número de puntos. Es la identidad que define el estimador, y solo la corrección de Diggle la cumple: por defecto se pasa un ' + n5(D5.m4.tabla[2].exceso_defecto_pct, 2) + ' % y sin corregir se queda un ' + n5(-D5.m4.tabla[2].fuga_sin_corregir_pct, 2) + ' % corta.'
      },
      {
        tipo: 'opcion',
        pista: 'Compara las dos cifras que el módulo 2 mide.',
        pregunta: 'Entre elegir el núcleo y elegir el ancho de banda, ¿cuál mueve más el mapa, y cuánto?',
        opciones: [
          { texto: 'El ancho: cambiar de núcleo mueve el pico un ' + n5(D5.m2.nucleos.max_dif_pct, 1) + ' % y cambiar de ancho un ' + n5(D5.m2.familia.caida_pct, 0) + ' %', correcta: true,
            retro: 'Y las cuatro superficies de núcleo distinto correlacionan por encima de ' + n5(Math.min.apply(null, Object.values(D5.m2.nucleos.cor_con_gaussiano)), 3) + ' entre sí: a efectos de lo que un lector ve, son el mismo mapa.' },
          { texto: 'El núcleo, porque decide la forma del peso',
            retro: 'Decide la forma, pero al mismo σ las cuatro dan casi la misma superficie: el pico se mueve solo un ' + n5(D5.m2.nucleos.max_dif_pct, 1) + ' %.' },
          { texto: 'Los dos por igual',
            retro: 'No: hay un factor de trece entre lo que mueve uno y lo que mueve el otro, medido sobre el mismo patrón.' },
          { texto: 'Depende del número de puntos',
            retro: 'El número de puntos afecta a la varianza de la estimación, no a cuál de las dos decisiones domina.' }
        ] },
      {
        tipo: 'multiple',
        pista: 'Son dos. Piensa en qué delata a un selector que ha chocado con su intervalo.',
        pregunta: 'Un selector devuelve exactamente ' + n5(D5.m3.topes[0].sigma, 4) + ', que es el extremo derecho de su intervalo de búsqueda. Marca <strong>todo</strong> lo que es cierto.',
        retroAcierto: 'Las dos: no ha encontrado un óptimo dentro del intervalo, y el valor devuelto no lo delata por sí solo.',
        retroFallo: 'Las correctas son la primera y la tercera.',
        opciones: [
          { texto: 'No ha seleccionado nada: ha chocado con la pared del intervalo', correcta: true,
            retro: 'El criterio seguía subiendo cuando se acabó el rango. Publicar ese número como «el ancho óptimo» sería falso.' },
          { texto: 'El valor devuelto es NA o infinito',
            retro: 'No: es finito y tiene el aspecto de cualquier otro. Ese es exactamente el problema.' },
          { texto: 'R lo avisa por consola, pero el valor de retorno no', correcta: true,
            retro: 'El aviso va a la consola y el número va a la variable. En un guion que calcula veinte cosas, el aviso se pierde y el número llega hasta el mapa.' },
          { texto: 'Basta con ampliar el intervalo para que el problema desaparezca',
            retro: 'Amplía el rango, sí, pero el criterio puede seguir subiendo. Lo que hay que hacer es comprobar si el valor coincide con el borde, y decirlo.' }
        ] },
      {
        tipo: 'opcion',
        pista: 'Mira las unidades de cada uno de los tres mapas.',
        pregunta: 'De los tres mapas del módulo 5 —todas las sedes, las sedes con grado 11 y esas mismas pesadas por sus evaluados—, ¿cuál es «el mapa de la demanda educativa»?',
        opciones: [
          { texto: 'Ninguno por sí solo: llamarlo así es una decisión que hay que escribir', correcta: true,
            retro: 'Los tres se parecen —correlacionan ' + n5(D5.m5.cor_oferta_grado11, 3) + ', ' + n5(D5.m5.cor_oferta_estudiantes, 3) + ' y ' + n5(D5.m5.cor_grado11_estudiantes, 3) + '— y ninguno cuenta lo mismo. El tercero además cuenta a los estudiantes donde ESTUDIAN, no donde viven.' },
          { texto: 'El tercero, porque cuenta estudiantes',
            retro: 'Es el más cercano, pero cuenta estudiantes ya matriculados: es demanda ATENDIDA, que es casi lo contrario de demanda insatisfecha.' },
          { texto: 'El primero, porque incluye todas las sedes',
            retro: 'Ese es oferta, no demanda: dice dónde hay colegio. Y además incluye sedes de primaria, que no tienen grado 11.' },
          { texto: 'El segundo, porque restringe a bachillerato',
            retro: 'Sigue siendo oferta, solo que de bachillerato: son ' + n5(D5.m5.capas.grado_11.pct_de_las_sedes, 1) + ' % de las sedes, medidas en edificios.' }
        ] },
      {
        tipo: 'opcion',
        pista: 'Mira dónde caen el máximo y el mínimo de una curva rhohat.',
        pregunta: 'Una curva <code>rhohat</code> da una razón de ' + n5(D5.m7.bogota.curva.razon, 0) + ' entre su ρ máximo y su mínimo, pero el <code>ppm</code> lineal sobre la misma covariable da z = −1.22. ¿Se contradicen?',
        opciones: [
          { texto: 'No: la razón de ' + n5(D5.m7.bogota.curva.razon, 0) + ' es casi toda cola, y en el bulto vale ' + n5(D5.m7.bogota.curva.razon_bulto, 2), correcta: true,
            retro: 'Restringida al tramo entre los percentiles 5 y 95 de la covariable observada en los puntos, la curva varía ' + n5(D5.m7.bogota.curva.razon_bulto, 2) + ' veces: la cola infla el titular ' + n5(D5.m7.bogota.curva.cola_infla, 1) + ' veces. Y no es del dato colombiano: sobre bei la elevación pasa de ' + n5(D5.m7.bei.elevacion.razon, 1) + ' a ' + n5(D5.m7.bei.elevacion.razon_bulto, 2) + '.' },
          { texto: 'Sí: uno de los dos está mal calculado',
            retro: 'Los dos están bien calculados. Lo que pasa es que miden cosas distintas sobre tramos distintos de la covariable.' },
          { texto: 'No, porque el ppm es más fiable que rhohat',
            retro: 'El ppm supone una forma —log-lineal— que la relación puede no tener. Ni más ni menos fiable: menos flexible.' },
          { texto: 'Sí, y hay que quedarse con la razón porque no supone nada',
            retro: 'rhohat supone menos, pero su máximo y su mínimo viven donde casi no hay puntos con los que estimarlos. Por eso este material publica las dos razones.' }
        ] },
      {
        tipo: 'multiple',
        pista: 'Son dos, y las dos van de argumentos que no aparecen en la llamada.',
        pregunta: 'Sobre <code>ppm</code>, marca <strong>todo</strong> lo que es cierto.',
        retroAcierto: 'Las dos: el AIC depende de la cuadratura, y el ajuste con coordenadas crudas devuelve coeficientes sin errores estándar.',
        retroFallo: 'Las correctas son la primera y la tercera.',
        opciones: [
          { texto: 'Dos ppm ajustados con cuadraturas distintas no se pueden comparar por AIC', correcta: true,
            retro: 'El AIC sale de la verosimilitud APROXIMADA por la cuadratura. Entre nd = ' + D5.m8.cuadratura.tabla[0].nd + ' y nd = ' + D5.m8.cuadratura.tabla[3].nd + ' el AIC se mueve ' + n5(D5.m8.cuadratura.rango_aic, 1) + ' puntos sin que cambie el modelo.' },
          { texto: 'Si la información de Fisher es singular, ppm falla y hay que atraparlo con try()',
            retro: 'No falla: <code>vcov()</code> avisa y devuelve NULL, y <code>sqrt(diag(NULL))</code> devuelve una matriz 0 × 0 sin quejarse. Un try() no ve nada.' },
          { texto: 'Con coordenadas en EPSG:9377 el ajuste devuelve coeficientes pero ningún error estándar', correcta: true,
            retro: 'El número de condición recíproco de la matriz de diseño es ' + D5.m9.crudo.cond_reciproco + '. Centrar y pasar a kilómetros lo sube a ' + D5.m9.centrado.cond_reciproco + ' sin cambiar el modelo: el AIC es el mismo.' },
          { texto: 'El coeficiente estimado también se mueve mucho con la cuadratura',
            retro: 'Se mueve poco en unidades de su propio error: ' + n5(D5.m8.cuadratura.rango_pendiente_en_ee, 2) + ' errores estándar de un extremo a otro de la tabla. Lo que se mueve es el AIC.' }
        ] },
      {
        tipo: 'opcion',
        pista: 'La banda del módulo 10 no se simula contra CSR.',
        pregunta: 'La K inhomogénea del patrón urbano se sale de la banda de su modelo ajustado en el ' + n5(D5.m10.pct_r_fuera_de_banda, 0) + ' % de los radios. ¿Qué se concluye?',
        opciones: [
          { texto: 'Que la intensidad variable no explica la agregación: hace falta un proceso de conglomerado', correcta: true,
            retro: 'Esa es la bisagra del capítulo. Modelar la intensidad explica DÓNDE hay más colegios, no que estén cerca unos de otros más de lo que ese «dónde» implica. Y el módulo 11 enseña que el ajuste de conglomerado depende de con qué corrección se estimó K: sobre este patrón, μ pasa de ' + n5(D5.m11.ajustes[0].mu, 1) + ' a ' + n5(D5.m11.ajustes[1].mu, 1) + '.' },
          { texto: 'Que el modelo está mal ajustado y hay que añadir covariables',
            retro: 'Podría ayudar, pero la K inhomogénea ya descuenta la intensidad estimada: lo que sobra son parejas cercanas, y eso no lo arregla una covariable de gran escala.' },
          { texto: 'Que la banda es demasiado estrecha por usar ' + D5.m10.nsim + ' simulaciones',
            retro: 'Al revés: con ' + D5.m10.nsim + ' simulaciones y la banda por defecto el nivel puntual es ' + n5(D5.m10.nivel_puntual_pct, 1) + ' %, más exigente que el 5 % de una envolvente de 39.' },
          { texto: 'Que el patrón no es un proceso puntual simple por los duplicados',
            retro: 'Tiene duplicados —' + D5.m11.duplicados.repetidos + ' sitios repetidos— pero quitarlos mueve los parámetros del ajuste como mucho un ' + n5(D5.m11.duplicados.cambio_maximo_pct, 1) + ' %. No son la explicación.' }
        ] }
    ];
"""
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


# CUÁNTOS MÓDULOS HAY ESCRITOS, declarado y no supuesto. El capítulo son
# doce; mientras no lo sean, `main()` lo dice en voz alta y devuelve 1. Un
# ensamblador que informa «limpio» sobre un capítulo a medias es
# exactamente la falsa calma que este proyecto persigue.
MODULOS_ESCRITOS = 12
MODULOS_OBJETIVO = 12
# La desviación declarada del molde (decisión 1 de la Fase 3): el
# capítulo cubre tres semanas, así que van 12 preguntas y 5
# ejercicios en vez de 8 y 4. Escrito aquí para que se pueda
# comprobar en vez de contarse a mano.
N_PREGUNTAS = 12
N_EJERCICIOS = 5


def main() -> int:
    doc = PLANTILLA.read_text(encoding="utf-8")
    print(f"\n=== ensambla_cap5.py ===\nplantilla: {len(doc)/1024:.0f} KB\n")

    # LA CLAVE DEL DESLIZADOR, COMPROBADA ANTES DE ESCRIBIR NADA.
    # El mapa y el dato guardan el mismo sigma en dos archivos que se
    # escriben con precisiones distintas. Si dejaran de coincidir, el
    # `find()` del navegador devolvería `undefined` y el mapa saldría en
    # blanco con la consola limpia.
    sig_dato = D["m2"]["familia"]["sigmas_m"]
    sig_mapa = [g["sigma_m"] for g in M["kennedy_familia"]]
    if sig_dato != sig_mapa:
        sys.exit("PARADO: los sigmas del dato y los de los mapas no coinciden "
                 f"({sig_dato[:2]}… contra {sig_mapa[:2]}…): el deslizador buscaría por una "
                 "clave que no existe")

    doc = sustituye(doc, "<title>Plantilla de capítulo — Estadística Espacial</title>",
                    "<title>Capítulo 5 · Intensidad por núcleos — "
                    "Estadística Espacial</title>", "título")
    doc = sustituye(doc, "PLANTILLA BASE •\n              5 MÓDULOS DE DEMOSTRACIÓN • UNBOSQUE 2026-II",
                    "CAPÍTULO 5 • INTENSIDAD POR NÚCLEOS Y PROCESOS PUNTUALES •\n"
                    f"              SEMANAS {D['meta']['semanas']} • UNBOSQUE 2026-II",
                    "subtítulo de la cabecera")
    doc = sustituye(doc, "Estadística Espacial (20929) • Plantilla de\n          capítulo • UnBosque 2026-II",
                    "Estadística Espacial (20929) • Capítulo 5 de 10 •\n"
                    f"          Semanas {D['meta']['semanas']} • UnBosque 2026-II", "pie")

    doc = reemplaza_region(doc, "    const courseData = {", "\n    };\n", COURSE_DATA,
                           "courseData + DATOS_CAP5", max_lineas=20)

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
    DESTINO.write_text(doc, encoding="utf-8")

    marcado = doc[:doc.rindex("\n  <script>")]
    mods = doc.count('<template id="module-')
    sims = marcado.count('data-simulador="')
    mapas = marcado.count('data-geomapa="cap5-')
    bl_r = doc.count('class="language-r"')
    bl_py = doc.count('class="language-python"')
    cifras = doc.count("#&gt;")
    lienzos = marcado.count("<canvas")
    con_alt = sum(1 for c in marcado.split("<canvas")[1:] if "aria-label" in c.split(">")[0])
    ejercicios = marcado.count('class="ejercicio-guiado"')
    quices = marcado.count('data-quiz="cap5-')
    preguntas = QUIZ_JS.count("tipo: '")
    opciones_quiz = QUIZ_JS.count("{ texto: '")
    retros = QUIZ_JS.count("retro: '")
    kb = DESTINO.stat().st_size / 1024

    rasteres = ([M[k] for k in M if isinstance(M[k], dict) and M[k].get("modo") == "rejilla"]
                + list(M["kennedy_familia"]))
    crudo = sum(len(json.dumps(m, ensure_ascii=False)) for m in rasteres) / 1024
    # EL REPARTO DEL RÁSTER SE DECLARA, que es lo que pide la decisión 5:
    # el peso no recorta explicación, pero sí se dice de dónde sale.
    empacado = sum(len(json.dumps(_empaqueta(m), ensure_ascii=False))
                   for m in rasteres) / 1024
    puntos_kb = sum(len(json.dumps(M[k], ensure_ascii=False)) for k in M
                    if isinstance(M[k], dict) and M[k].get("modo") == "puntos") / 1024

    print(f"{DESTINO.relative_to(RAIZ)}  {kb:.0f} KB")
    print(f"  {mods} módulos · {sims} simuladores · {mapas} mapas · "
          f"{bl_r} bloques de R y {bl_py} de Python · {cifras} cifras anunciadas")
    print(f"  {lienzos} lienzos, {con_alt} con aria-label")
    print(f"  {preguntas} preguntas en {quices} autoevaluaciones "
          f"({opciones_quiz} opciones, {retros} con su retroalimentación) · "
          f"{ejercicios} ejercicios guiados")
    print(f"  ráster: {len(rasteres)} superficies · {crudo:.0f} KB sin empaquetar → "
          f"{empacado:.0f} KB con máscara aparte y deltas por fila "
          f"({100 * empacado / crudo:.0f} %), ida y vuelta comprobada en las "
          f"{len(rasteres)}")
    print(f"  reparto del documento: {empacado:.0f} KB de ráster + {puntos_kb:.0f} KB de "
          f"mapas de puntos + {kb - empacado - puntos_kb:.0f} KB de todo lo demás "
          f"= {kb:.0f} KB")

    problemas = []
    if mods != MODULOS_ESCRITOS:
        problemas.append(f"módulos: {mods} y hay {MODULOS_ESCRITOS} escritos")
    if bl_r != bl_py:
        problemas.append(f"R y Python descuadrados: {bl_r} y {bl_py}")
    if lienzos != con_alt:
        problemas.append(f"lienzos sin aria-label: {lienzos - con_alt}")
    if ejercicios != N_EJERCICIOS:
        problemas.append(f"ejercicios: {ejercicios} (la desviación declarada son "
                         f"{N_EJERCICIOS})")
    if preguntas != N_PREGUNTAS:
        problemas.append(f"preguntas: {preguntas} (la desviación declarada son "
                         f"{N_PREGUNTAS})")
    if quices != 2:
        problemas.append(f"autoevaluaciones: {quices} y son dos, la del módulo 6 y la del 12")
    # LA CLAVE DE LA RETROALIMENTACIÓN, COMPROBADA Y NO SUPUESTA.
    # El motor lee `op.retro`; los capítulos 3 y 4 escribieron `respuesta`
    # y sus 68 explicaciones por opción no se dibujan nunca, sin un solo
    # error en consola. Aquí para el ensamblado.
    if "respuesta: '" in doc or "explicacion: '" in doc:
        problemas.append("hay opciones con la clave `respuesta`/`explicacion`: "
                         "el motor lee `retro`, `retroAcierto` y `retroFallo`, "
                         "y lo que no lee no se dibuja")
    if retros != opciones_quiz:
        problemas.append(f"opciones de quiz sin `retro`: {opciones_quiz - retros} "
                         f"de {opciones_quiz}")
    if problemas:
        print("\n  PROBLEMAS:")
        for p in problemas:
            print(f"   - {p}")
        return 1

    if MODULOS_ESCRITOS < MODULOS_OBJETIVO:
        print(f"\n  EN CONSTRUCCIÓN: {MODULOS_ESCRITOS} de {MODULOS_OBJETIVO} módulos. "
              "No es publicable todavía.")
        return 1
    print("\n  Capítulo 5 ensamblado.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
