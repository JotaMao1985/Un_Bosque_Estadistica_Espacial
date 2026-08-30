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
""" + CIERRE


MODULOS = MOD1 + MOD2


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

GEOMAPAS_JS = (
    FAMILIA_JS
    + "    GEOMAPAS['cap5-familia'] = {\n"
      "      fuente: () => superficieDeSigma(D5.m2.familia.sigmas_m[famIdx]),\n"
      "      paleta: 'naranja',\n"
      "      etiqueta: 'Intensidad de sedes educativas en Kennedy estimada por núcleos, "
      "sobre una rejilla de " + str(FAM["nx"]) + " por " + str(FAM["ny"]) + " celdas; "
      "el ancho de banda se controla con el deslizador.'\n"
      "    };\n"
)


SIMULADORES_JS = """    // --- El pico contra el ancho de banda ----------------------------
    // La curva NO se mueve: el ancho ya es su eje horizontal. Lo que se
    // mueve es el marcador y el mapa de al lado. Es el patrón del
    // simulador de campos del capítulo 1, y por el mismo motivo.
    SIMULADORES['cap5-anchos'] = function (raiz) {
      const f = D5.m2.familia;
      const g = grafico(raiz, 'line', {
        labels: f.sigmas_m.map(s => n5(s, 0) + ' m'),
        datasets: [{ label: 'intensidad máxima (por km²)', data: f.max_km2,
                     borderColor: COLOR.verde, backgroundColor: COLOR.verdeSuave,
                     fill: true, tension: 0.3, pointRadius: 3 }]
      }, { scales: { y: { title: { display: true, text: 'sedes por km²' } },
                     x: { title: { display: true, text: 'ancho de banda σ' } } } });

      const lee = () => actualizarLectura(raiz.querySelector('.simulador-lectura'), [
        ['ancho de banda σ', n5(f.sigmas_m[famIdx], 0) + ' m'],
        ['celdas por σ', n5(f.sigmas_m[famIdx] / f.celda_m, 1)],
        ['intensidad máxima', n5(f.max_km2[famIdx], 1) + ' por km²']]);

      const pinta = () => {
        g.data.datasets[0].pointRadius = f.sigmas_m.map((_, i) => i === famIdx ? 7 : 3);
        g.update('none');
      };
      // Las posiciones se DERIVAN de las superficies que existen de verdad:
      // si alguna faltara, el control no ofrecería su posición.
      const hay = f.sigmas_m.map((s, i) => [i, n5(s, 0) + ' m'])
                            .filter(par => superficieDeSigma(f.sigmas_m[par[0]]));
      famIdx = hay[0][0];
      deslizador(raiz, hay, 'ancho de banda σ', 0, v => {
        famIdx = v;
        const m = document.querySelector('[data-geomapa="cap5-familia"]');
        if (m && m.__geomapa) m.__geomapa.dibuja();
        lee(); pinta();
      });
      lee(); pinta();
      return [g];
    };
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
MODULOS_ESCRITOS = 2
MODULOS_OBJETIVO = 12


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
                           "    AUTOEVALUACIONES['cap5'] = [\n    ];\n",
                           "AUTOEVALUACIONES", max_lineas=90)

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
    kb = DESTINO.stat().st_size / 1024

    crudo = sum(len(json.dumps(m, ensure_ascii=False)) for m in
                ([M[k] for k in M if isinstance(M[k], dict) and M[k].get("modo") == "rejilla"]
                 + list(M["kennedy_familia"]))) / 1024

    print(f"{DESTINO.relative_to(RAIZ)}  {kb:.0f} KB")
    print(f"  {mods} módulos · {sims} simuladores · {mapas} mapas · "
          f"{bl_r} bloques de R y {bl_py} de Python · {cifras} cifras anunciadas")
    print(f"  {lienzos} lienzos, {con_alt} con aria-label")
    print(f"  ráster: {crudo:.0f} KB sin empaquetar, ida y vuelta comprobada en los "
          f"{len(M['kennedy_familia']) + 3} rásteres")

    problemas = []
    if mods != MODULOS_ESCRITOS:
        problemas.append(f"módulos: {mods} y hay {MODULOS_ESCRITOS} escritos")
    if bl_r != bl_py:
        problemas.append(f"R y Python descuadrados: {bl_r} y {bl_py}")
    if lienzos != con_alt:
        problemas.append(f"lienzos sin aria-label: {lienzos - con_alt}")
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
