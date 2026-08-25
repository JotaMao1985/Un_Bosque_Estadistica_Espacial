#!/usr/bin/env python3
"""
ensambla_cap4.py — construye el capítulo 4 del material (T3.2)

Material de Estadística Espacial 2026-II (20929).
«Patrones puntuales: descripción, CSR y funciones de resumen» · semanas 6-7

MISMO REPARTO QUE LOS CAPÍTULOS 1, 2 Y 3 (Checkpoint 1: el capítulo 1 es
el molde):

  · La **prosa** vive en f-strings y se interpola aquí desde el JSON. Es
    lo que audita `audita_texto_cap4.py`, y `sin_aritmetica.py` vigila
    que ninguna de esas cifras se CALCULE aquí en vez de venir de R.
  · El **JavaScript** NO se interpola: recibe el JSON entero como
    `DATOS_CAP4` y saca de ahí sus cifras con `n5()`.
  · Los **mapas** se registran con su JSON LITERAL, no con una función.

LA DESVIACIÓN DEL MOLDE, DECLARADA (decisión 2 de Javier, 2026-08-21):
**12 preguntas y 5 ejercicios** en vez de 8 y 4. El capítulo cubre DOS
semanas de clase, igual que el 2, y por el mismo motivo. Las doce
preguntas se reparten en el quiz de 8 más un bloque intermedio de 4
«trampas de patrones puntuales» tras el módulo 6, que es donde el
capítulo ya ha dado suficiente cuerda para caer en ellas.

LO QUE ESTE CAPÍTULO ESTRENA, y va declarado:
  · Es el primero cuyos mapas son TODOS de modo `puntos`. Eso destapó un
    hueco en `audita_geomapa()`, que validaba la cuantización solo sobre
    `geom` (A.19).
  · La ventana que se DIBUJA está simplificada a 875 vértices y la que se
    ANALIZA tiene 13 767. Son dos usos distintos del mismo objeto y el
    capítulo lo dice en voz alta, en vez de dejar que el lector suponga
    que el contorno del mapa es el del cálculo.
  · Los bloques de Python NO traducen llamadas a spatstat, porque no
    existe equivalente: reimplementan la matemática con numpy y scipy.
    Es el mismo camino largo que recorre `audita_cap4.py`, y por eso se
    sabe que llega al mismo sitio.

Y LA REGLA DEL RITMO (§9.1 del plan): ningún módulo abre pidiendo trabajo
· todo componente interactivo va con dos párrafos, el que lo motiva y el
que lo cierra · el encabezado del módulo es un contrato.

Uso:  python3 precalculo/ensambla_cap4.py
      (desde la carpeta `Estadistica espacial/`)
"""
from __future__ import annotations

import json
import pathlib
import sys

RAIZ = pathlib.Path(__file__).resolve().parent.parent
PLANTILLA = RAIZ / "plantilla" / "plantilla-capitulo.html"
SALIDAS = RAIZ / "precalculo" / "salidas"
DESTINO = RAIZ / "Htmls_Espacial" / "capitulo-4-patrones-puntuales.html"

D = json.loads((SALIDAS / "cap4_datos.json").read_text(encoding="utf-8"))
M = json.loads((SALIDAS / "cap4_mapas.json").read_text(encoding="utf-8"))
S = json.loads((SALIDAS / "cap4_soluciones.json").read_text(encoding="utf-8"))

m1, m2, m3, m4 = D["m1"], D["m2"], D["m3"], D["m4"]
m5, m6, m7 = D["m5"], D["m6"], D["m7"]
m8, m9, m10, m11 = D["m8"], D["m9"], D["m10"], D["m11"]
CORR = {c["correccion"]: c for c in m10["correcciones"]}
ESC = {z["nsim"]: z for z in m11["escala_nsim"]}


# ---------------------------------------------------------------------
# Ayudantes de formato. Los mismos que los capítulos 2 y 3: la regla de
# publicación de T0.5 son CINCO decimales para toda cifra de la que el
# texto argumente.
# ---------------------------------------------------------------------
def n(x, d=5):
    return f"{float(x):.{d}f}"


def ent(x):
    """Entero con espacio fino U+202F. NO usar dentro de KaTeX."""
    return f"{int(round(float(x))):,}".replace(",", " ")


def ent_mate(x):
    """El mismo entero para DENTRO de una fórmula: KaTeX no entiende U+202F."""
    return f"{int(round(float(x))):,}".replace(",", r"\,")


def firma(valor, unidad=""):
    return f"<strong>{valor}</strong>{unidad}"


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
    """Un simulador con su lienzo de Chart.js.

    `.grafico-wrapper` CON ALTURA EXPLÍCITA es el contrato de la
    plantilla: inventarse una clase deja el canvas a cero de alto,
    Chart.js crea el gráfico sin quejarse y el simulador sale en blanco
    con la consola limpia (defecto nº 5 de A.13).
    """
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
    """El marcado ENTERO que `renderAutoevaluacion` espera (defecto nº 6 de A.13)."""
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
    """El div de un `.geomapa`, y sus controles FUERA de él.

    `iniciarGeomapas()` REESCRIBE el `innerHTML` del div del mapa. Un
    `<div class="geomapa-controles">` puesto dentro desaparece en ese
    momento: el capítulo se ve perfecto, la consola está limpia y los
    botones no existen.
    """
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
    ("Qué es un proceso puntual", "La ventana forma parte del estimador"),
    ("La intensidad λ", "Homogénea, inhomogénea y el estimador por conteo"),
    ("Los tres regímenes", "Aleatorio, regular, agregado"),
    ("CSR", "El proceso de Poisson homogéneo y sus dos propiedades"),
    ("El test de cuadrantes", "Y su ceguera: dos patrones con el mismo χ²"),
    ("El tamaño del cuadrante", "Esto es el MAUP otra vez"),
    ("Las funciones G y F", "Distancias al vecino y al espacio vacío"),
    ("La función K de Ripley", "Y su transformación L"),
    ("La correlación de pares g(r)", "Por qué g es más legible que K"),
    ("Efectos de borde", "Tres correcciones, y lo que cuestan"),
    ("Envolventes de simulación", "Qué NO es un p-valor de envolvente"),
    ("Autoevaluación y ejercicios", "Doce preguntas y cinco ejercicios guiados"),
)


# =====================================================================
# MÓDULO 1 · Qué es un proceso puntual
# =====================================================================
MOD1 = cabecera(
    1, "Qué es un proceso puntual", "What is a point process",
    "Entender que en un patrón puntual lo aleatorio es la LOCALIZACIÓN, y que "
    "la ventana de observación no acompaña al estimador: forma parte de él."
) + f"""      <p>En los tres capítulos anteriores el dato traía su sitio puesto: un municipio,
        una estación, un condado. Lo que variaba era el valor —la deserción, la
        temperatura— y el sitio estaba fijo. Aquí se invierte. Un <strong>patrón
        puntual</strong> es un conjunto de localizaciones, y lo aleatorio es
        <em>dónde</em> están. No hay valor que mapear: el dato es la posición.</p>

      <p>El objeto que lo representa en R es un <code>ppp</code>, y tiene dos partes que
        conviene no separar nunca: las coordenadas y la <strong>ventana de
        observación</strong>. La ventana es la región donde se buscó. No es el marco del
        dibujo ni un adorno del mapa: es la afirmación de que en ese recinto, y solo en
        ese, se habría visto un punto de haberlo.</p>

      <p>Tenemos {firma(ent(m1['sedes_total']))} sedes educativas de Bogotá georreferenciadas
        —las mismas del capítulo 1, ahora usadas como lo que son—. La pregunta que abre el
        capítulo no es sobre ellas sino sobre el recinto: ¿dónde se buscó? Hay dos
        respuestas defendibles, y las dos están dibujadas abajo.</p>

{mapa_html('cap4-urbano', 'Las sedes dentro del perímetro urbano')}
{mapa_html('cap4-dc', 'Las mismas sedes en el Distrito Capital completo')}

      <p>El perímetro urbano encierra {firma(n(m1['urbana']['area_km2'], 5), ' km²')} y deja
        {firma(ent(m1['urbana']['n']))} sedes dentro; el Distrito Capital,
        {firma(n(m1['dc']['area_km2'], 5), ' km²')} y {firma(ent(m1['dc']['n']))}. Fíjate en
        lo que pasa con esos dos pares de números. Al pasar de una ventana a otra el
        numerador sube un {n(m1['aumento_n_pct'], 5)} %, porque el suelo rural del D.C. casi
        no tiene colegios; el denominador se multiplica por {n(m1['cociente_area'], 5)}.</p>

      <div class="key-insight">
        <p style="margin:0;">La misma ciudad, el mismo dato y dos intensidades que se llevan
        un factor de {firma(n(m1['factor_lambda'], 5))}:
        {firma(n(m1['urbana']['lambda_km2'], 5), ' sedes/km²')} contra
        {firma(n(m1['dc']['lambda_km2'], 5))}. Ninguna de las dos es un error. Lo que sería
        un error es publicar una sin decir cuál es la ventana, porque entonces la cifra no
        es ni verdadera ni falsa: está incompleta.</p>
      </div>

      <p>Hay un detalle que el mapa esconde y el código no: al construir el <code>ppp</code>
        con el perímetro urbano, {firma(ent(m1['urbana']['fuera']))} sedes quedan
        <strong>fuera</strong> y se descartan. Con el D.C. solo se descarta
        {ent(m1['dc']['fuera'])}. Ese descarte lo hace <code>ppp()</code> con un aviso que
        nadie lee, y cambia n sin cambiar nada visible. Ahí empieza a decidirse el
        resultado.</p>

{tabs('El objeto ppp y sus dos ventanas',
      '''library(sf); library(spatstat)

cole  &lt;- st_read("datos/procesado/bogota_colegios.gpkg", quiet = TRUE)
v_urb &lt;- st_read("datos/procesado/bogota_ventana_urbana.gpkg", quiet = TRUE)
v_dc  &lt;- st_read("datos/procesado/bogota_ventana_dc.gpkg",     quiet = TRUE)

xy &lt;- st_coordinates(cole)
p_urb &lt;- ppp(xy[, 1], xy[, 2], window = as.owin(st_union(v_urb)))
p_dc  &lt;- ppp(xy[, 1], xy[, 2], window = as.owin(st_union(v_dc)))
# OJO al aviso: `ppp()` DESCARTA los puntos de fuera y sigue.

c(n_urb = npoints(p_urb), n_dc = npoints(p_dc))
#&gt; n_urb  n_dc
#&gt;  2107  2208

# La intensidad, en sedes por km2 (las coordenadas van en metros)
round(c(urbana = intensity(p_urb), dc = intensity(p_dc)) * 1e6, 4)
#&gt; urbana     dc
#&gt; 5.6932 1.3520''',
      '''import geopandas as gpd, numpy as np

cole  = gpd.read_file("datos/procesado/bogota_colegios.gpkg")
v_urb = gpd.read_file("datos/procesado/bogota_ventana_urbana.gpkg").union_all()
v_dc  = gpd.read_file("datos/procesado/bogota_ventana_dc.gpkg").union_all()

xy = np.c_[cole.geometry.x, cole.geometry.y]
# Python no tiene spatstat: aqui la "ventana" es el poligono, y
# pertenecer al patron es caer dentro de el.
dentro_urb = gpd.GeoSeries(cole.geometry).covered_by(v_urb).to_numpy()
dentro_dc  = gpd.GeoSeries(cole.geometry).covered_by(v_dc).to_numpy()

print([int(dentro_urb.sum()), int(dentro_dc.sum())])
#&gt; [2107, 2208]

print([round(float(dentro_urb.sum() / (v_urb.area / 1e6)), 4),
       round(float(dentro_dc.sum()  / (v_dc.area  / 1e6)), 4)])
#&gt; [5.6932, 1.352]''')}

      <p>Una última cosa sobre esa ventana urbana, porque va a costar dinero en el módulo
        10: no es un polígono cualquiera. Son {firma(ent(m1['urbana']['piezas']))} piezas
        disjuntas con {firma(ent(m1['urbana']['agujeros']))} agujeros y
        {firma(ent(m1['urbana']['vertices']))} vértices, y un perímetro de
        {firma(n(m1['urbana']['perimetro_km'], 5), ' km')} para
        {n(m1['urbana']['area_km2'], 5)} km² de superficie. Guarda ese número: la mitad de
        lo que este capítulo cuesta de calcular sale de ahí.</p>
""" + CIERRE


# =====================================================================
# MÓDULO 2 · La intensidad λ
# =====================================================================
MOD2 = cabecera(
    2, "La intensidad λ", "Intensity",
    "Estimar la intensidad por conteo, y ver que un solo número solo describe el "
    "patrón si λ es constante — cosa que casi nunca es."
) + f"""      <p>La intensidad λ es el número esperado de puntos por unidad de área. Su estimador
        más simple es una división: n entre el área de la ventana. Para el patrón urbano
        eso da {firma(n(m2['lambda_urbana_km2'], 5), ' sedes/km²')}, que en otras unidades
        es {n(m2['lambda_urbana_ha'], 5)} por hectárea o
        {n(m2['lambda_urbana_m2'], 10)} por metro cuadrado — la misma cifra, y conviene
        reconocerla en las tres, porque el código la devuelve en la unidad del CRS.</p>

      <div class="formula-box">
        <p>$$\\hat{{\\lambda}} = \\frac{{n}}{{|W|}} = \\frac{{{ent_mate(m1['urbana']['n'])}}}{{{n(m1['urbana']['area_km2'], 2)}\\ \\text{{km}}^2}}
          = {n(m2['lambda_urbana_km2'], 4)}\\ \\text{{sedes/km}}^2$$</p>
      </div>

      <p>Ese número describe el patrón <strong>solo si λ es constante</strong>. Y para
        comprobar si lo es basta partir la ventana en cuadrantes y contar: si la intensidad
        fuera la misma en todas partes, los conteos serían parecidos salvo el azar de
        Poisson. Con una rejilla de {m2['urbana']['nx']}×{m2['urbana']['ny']}, la celda más
        poblada tiene {firma(ent(m2['urbana']['maximo']))} sedes y hay
        {firma(ent(m2['urbana']['vacios']))} celdas con cero.</p>

      <p>El índice de dispersión —la varianza de los conteos dividida por su media— vale
        {firma(n(m2['urbana']['dispersion'], 5))}. Bajo Poisson valdría 1. El χ² del test de
        cuadrantes es {firma(n(m2['urbana']['chi2'], 2))} con
        {ent(m2['urbana']['gl'])} grados de libertad, y su p-valor es del orden de
        10<sup>{n(m2['urbana']['p_log10'], 1)}</sup>.</p>

      <p>Antes de celebrar ese rechazo, una advertencia que el módulo 5 va a cobrarse: el
        χ² supone que la esperanza de cada celda no es minúscula, y aquí
        {firma(ent(m2['urbana']['celdas_esperanza_baja']))} de las
        {ent(m2['urbana']['celdas'])} celdas vivas tienen esperanza menor que 5, porque la
        ventana las recorta. El número sigue siendo enorme, pero conviene saber sobre qué
        se apoya.</p>

      <p>El simulador reparte la rejilla que elijas y enseña el histograma de conteos junto
        a la Poisson que tocaría si λ fuera constante. Mira cómo se separan.</p>

{sim('cap4-cuadrantes', 'Contar en cuadrantes',
     'Elige el tamaño de la rejilla: la barra es el reparto observado y la línea, el que daría una intensidad constante.', 300)}

      <p>Lo que acabas de ver no es que Bogotá tenga «mucha» o «poca» intensidad, sino que
        <strong>no tiene una sola</strong>. A partir de aquí, un número deja de servir y hay
        que describir el patrón con funciones. Los módulos 7 a 9 se dedican a eso; antes
        hace falta saber contra qué compararlas.</p>

{tabs('Contar en cuadrantes y contrastar',
      '''qc &lt;- quadratcount(p_urb, nx = 10, ny = 10)
te &lt;- quadrat.test(p_urb, nx = 10, ny = 10)
# Avisa de que algunas esperanzas son pequenas: la ventana recorta celdas.

round(c(chi2 = unname(te$statistic), gl = unname(te$parameter["df"])), 2)
#&gt;   chi2     gl
#&gt; 456.12  64.00

# El indice de dispersion: bajo Poisson vale 1
round(var(as.vector(qc)) / mean(as.vector(qc)), 4)
#&gt; [1] 25.9097''',
      '''from shapely.geometry import box
XU = xy[dentro_urb]

# El binado de `quadratcount` es el de `cut()`: (a, b], con el mas
# bajo cerrado por los dos lados. Reproducirlo importa (ver modulo 5).
def celda(v, lo, hi, k):
    b = np.linspace(lo, hi, k + 1)
    return np.clip(np.searchsorted(b, v, side="left") - 1, 0, k - 1)

x0, y0, x1, y1 = v_urb.bounds
ix, iy = celda(XU[:, 0], x0, x1, 10), celda(XU[:, 1], y0, y1, 10)
obs = np.zeros((10, 10), int); np.add.at(obs, (ix, iy), 1)

# La esperanza de cada celda es su area RECORTADA contra la ventana
bx, by = np.linspace(x0, x1, 11), np.linspace(y0, y1, 11)
area = np.array([[v_urb.intersection(box(bx[i], by[j], bx[i+1], by[j+1])).area
                  for j in range(10)] for i in range(10)])
esp = area / v_urb.area * obs.sum()
vivas = esp &gt; 0
chi2 = float(((obs[vivas] - esp[vivas]) ** 2 / esp[vivas]).sum())

print([round(chi2, 2), int(vivas.sum()) - 1])
#&gt; [456.12, 64]
print(round(obs[vivas].var(ddof=1) / obs[vivas].mean(), 4))
#&gt; 25.9097''')}
""" + CIERRE


# =====================================================================
# MÓDULO 3 · Los tres regímenes
# =====================================================================
MOD3 = cabecera(
    3, "Los tres regímenes", "The three regimes",
    "Reconocer a ojo y con una cifra los tres comportamientos básicos —aleatorio, "
    "regular y agregado— sobre los patrones canónicos de la literatura."
) + f"""      <p>Antes de medir hace falta saber qué se está buscando. Un patrón puntual puede
        comportarse de tres maneras, y los tres conjuntos de abajo son los que la literatura
        usa para enseñarlas desde hace cincuenta años. Míralos antes de leer ninguna cifra:
        la diferencia se ve.</p>

{mapa_html('cap4-cells', 'Regular: células biológicas')}
{mapa_html('cap4-japanesepines', 'Aleatorio: pinos japoneses')}
{mapa_html('cap4-redwood', 'Agregado: plántulas de secuoya')}

      <p>En el primero los puntos se <strong>estorban</strong>: cada célula ocupa un sitio y
        empuja a las demás, así que quedan más separadas de lo que el azar daría. En el
        tercero se <strong>atraen</strong> —las plántulas brotan cerca del árbol madre— y
        aparecen grumos. El del medio no hace ni una cosa ni la otra.</p>

      <p>La cifra que los ordena es el índice de Clark-Evans: la distancia media al vecino
        más próximo, dividida por la que daría el azar. Bajo aleatoriedad esa distancia
        esperada vale 1/(2√λ), así que el cociente ronda 1; por debajo hay agregación y por
        encima, regularidad.</p>

      <div class="formula-box">
        <p>$$R = \\frac{{\\bar{{d}}_{{\\min}}}}{{1 / (2\\sqrt{{\\lambda}})}}
          \\qquad R &lt; 1 \\text{{ agregado}} \\qquad R \\approx 1 \\text{{ aleatorio}}
          \\qquad R &gt; 1 \\text{{ regular}}$$</p>
      </div>

      <table class="tabla-datos">
        <caption>Los tres canónicos y el patrón colombiano, con su distancia media al vecino
          más próximo, la que daría el azar y el cociente entre las dos.</caption>
        <thead><tr><th scope="col">Patrón</th><th scope="col">n</th>
          <th scope="col">d̄ observada</th><th scope="col">d̄ bajo azar</th>
          <th scope="col">R</th><th scope="col">Régimen</th></tr></thead>
        <tbody>
{fila('Células', ent(m3['cells']['n']), n(m3['cells']['nn_media'], 5),
      n(m3['cells']['nn_esperada'], 5), firma(n(m3['cells']['clark_evans'], 5)), 'regular')}{fila('Pinos suecos', ent(m3['swedishpines']['n']), n(m3['swedishpines']['nn_media'], 3),
      n(m3['swedishpines']['nn_esperada'], 3), firma(n(m3['swedishpines']['clark_evans'], 5)), 'regular')}{fila('Pinos japoneses', ent(m3['japanesepines']['n']), n(m3['japanesepines']['nn_media'], 5),
      n(m3['japanesepines']['nn_esperada'], 5), firma(n(m3['japanesepines']['clark_evans'], 5)), 'aleatorio')}{fila('Secuoyas', ent(m3['redwood']['n']), n(m3['redwood']['nn_media'], 5),
      n(m3['redwood']['nn_esperada'], 5), firma(n(m3['redwood']['clark_evans'], 5)), 'agregado')}{fila('Sedes de Bogotá', ent(m3['bogota']['n']), n(m3['bogota']['nn_media'], 2),
      n(m3['bogota']['nn_esperada'], 2), firma(n(m3['bogota']['clark_evans'], 5)), 'agregado')}        </tbody>
      </table>

      <p>La última fila es la que importa para el resto del capítulo: las sedes educativas
        de Bogotá tienen R = {firma(n(m3['bogota']['clark_evans'], 5))}, por debajo de 1.
        Están <strong>agregadas</strong>. Todavía no sabemos a qué escala ni cuánto, y esas
        dos preguntas son los módulos 7 a 9.</p>

      <p>El simulador de abajo genera patrones de los tres tipos con la intensidad que
        elijas y enseña su R junto a la distribución de distancias al vecino. Muévelo para
        ver algo que el módulo 4 va a convertir en el problema central: cuánto se mueve R
        cuando el patrón no cambia de naturaleza, solo de realización.</p>

{sim('cap4-regimenes', 'Los tres regímenes, y cuánto se mueve su R',
     'Elige el régimen y el número de puntos: la barra es la distribución de distancias al vecino más próximo.', 300)}

      <p>Si has movido el control unas cuantas veces habrás visto que la R del patrón
        aleatorio no se queda quieta en 1. Ese temblor no es ruido del simulador: es la
        propiedad que define el azar, y no tenerla en cuenta es el error más común al
        interpretar un patrón puntual. El módulo siguiente la mide.</p>

{tabs('El índice de Clark-Evans sobre los tres canónicos',
      '''data(cells); data(japanesepines); data(redwood)

round(sapply(list(cells = cells, japanesepines = japanesepines, redwood = redwood),
             function(p) clarkevans(p)[["naive"]]), 4)
#&gt;         cells japanesepines       redwood
#&gt;        1.6717        1.0640        0.6187''',
      '''import pandas as pd
from scipy.spatial import cKDTree

reg = pd.read_csv("precalculo/salidas/cap4_regimenes.csv")

def clark_evans(x, y, area):
    d, _ = cKDTree(np.c_[x, y]).query(np.c_[x, y], k=2)
    return float(d[:, 1].mean() / (0.5 / np.sqrt(len(x) / area)))

for nm in ("cells", "japanesepines", "redwood"):
    d = reg[reg.patron == nm]
    print(nm, round(clark_evans(d.x.values, d.y.values, 1.0), 4))
#&gt; cells 1.6717
#&gt; japanesepines 1.064
#&gt; redwood 0.6187''')}
""" + CIERRE


# =====================================================================
# MÓDULO 4 · CSR
# =====================================================================
MOD4 = cabecera(
    4, "CSR", "Complete Spatial Randomness",
    "Separar las DOS propiedades que definen la aleatoriedad completa, y medir "
    "cuánto se mueve un patrón aleatorio sin dejar de serlo."
) + f"""      <p>«Aleatorio» no es una impresión visual: es un modelo, y tiene nombre. El proceso
        de Poisson homogéneo —<em>Complete Spatial Randomness</em>, CSR— es la referencia
        contra la que se comparan todos los patrones, y se define por <strong>dos</strong>
        cosas. La segunda se recuerda siempre; la primera se olvida siempre.</p>

      <div class="key-insight">
        <p style="margin:0;"><strong>(1)</strong> El <em>número</em> de puntos en cualquier
        región A sigue una Poisson de media λ|A|. <strong>(2)</strong> <em>Dado</em> ese
        número, las posiciones son uniformes e independientes. La primera propiedad dice que
        dos realizaciones del mismo proceso <strong>no tienen el mismo n</strong>. Quien
        solo recuerda la segunda espera patrones que siempre tengan los mismos puntos, y se
        sorprende de lo que ve.</p>
      </div>

      <p>Se comprueba simulando. {firma(ent(m4['n_realizaciones']))} realizaciones de CSR con
        λ = {ent(m4['lambda'])} en el cuadrado unidad dan una media de
        {firma(n(m4['conteo_media'], 3))} puntos y una varianza de
        {firma(n(m4['conteo_var'], 3))}. Que las dos valgan aproximadamente lo mismo, y que
        ese algo sea λ|W|, es la firma de Poisson: ninguna otra distribución de conteos hace
        eso. El recorrido va de {ent(m4['conteo_min'])} a {ent(m4['conteo_max'])} puntos.</p>

      <p>La segunda mitad del módulo es la que engancha con el 11. Sobre esas mismas
        realizaciones —todas de azar puro, todas CSR por construcción— el índice de
        Clark-Evans recorre de {firma(n(m4['R_csr']['min'], 5))} a
        {firma(n(m4['R_csr']['max'], 5))}, con media
        {n(m4['R_csr']['media'], 5)} y un intervalo central del 95 % entre
        {n(m4['R_csr']['q025'], 5)} y {n(m4['R_csr']['q975'], 5)}.</p>

      <p>Léelo despacio, porque tiene consecuencias. Si el criterio fuera «R menor que 1
        significa agregación», {firma(ent(m4['R_csr']['bajo_1']))} de las
        {ent(m4['R_csr']['n'])} realizaciones de azar puro darían veredicto de agregado. Una
        R sola, sin saber cuánto se mueve el azar, no dice nada.</p>

{sim('cap4-poisson', 'Las dos propiedades de CSR',
     'Cambia λ y mira el reparto de conteos contra la Poisson teórica; el segundo control enseña cuánto se mueve la R del azar.', 300)}

      <p>Ese temblor es la razón de ser de las envolventes de simulación, que llegan en el
        módulo 11. Antes hay que ver qué herramientas describen un patrón, y empezar por la
        más antigua de todas, que también es la que peor ve.</p>

{tabs('Las dos propiedades, simuladas',
      '''set.seed(4026)
conteos &lt;- replicate(2000, npoints(rpoispp(65, win = owin())))

# Propiedad (1): media y varianza valen las dos lambda|W|
round(c(media = mean(conteos), varianza = var(conteos)), 3)
#&gt;    media varianza
#&gt;   64.979   67.673''',
      '''rng = np.random.default_rng(4026)
conteos = rng.poisson(65, size=2000)

print([round(float(conteos.mean()), 3), round(float(conteos.var(ddof=1)), 3)])
#&gt; [64.829, 67.47]

# OJO: R y Python NO comparten generador de numeros aleatorios, asi que
# las cifras simuladas difieren aunque la semilla sea la misma. Lo que
# coincide es la PROPIEDAD: media y varianza rondan las dos lambda|W|.''')}
""" + CIERRE


# ---------------------------------------------------------------------
# LOS BLOQUES DE CÓDIGO SE ARMAN ANTES DE LA PROSA, y no dentro del
# f-string de cada módulo. Motivo técnico y no de estilo: hasta Python
# 3.12 una expresión de f-string no puede llevar barras invertidas ni
# comillas triples, y los bloques de este capítulo llevan las dos —un
# `sprintf("...\n")` en R, una cadena de documentación en Python—. Con el
# `tabs(...)` dentro del f-string, el archivo no compila; con el bloque
# ya armado en una variable, el problema no existe. El intérprete del
# proyecto es 3.10 (ver versiones_py.json).
# ---------------------------------------------------------------------
TABS_M5 = tabs(
    'Dos patrones con el mismo χ²',
    '''set.seed(4027)
w  &lt;- redwood$window
bx &lt;- seq(w$xrange[1], w$xrange[2], length.out = 6)
by &lt;- seq(w$yrange[1], w$yrange[2], length.out = 6)
# `cut()` es el binado de quadratcount: (a, b], el mas bajo cerrado.
ix &lt;- cut(redwood$x, bx, include.lowest = TRUE)
iy &lt;- cut(redwood$y, by, include.lowest = TRUE)

xs &lt;- ys &lt;- numeric(0)
for (i in 1:5) for (j in 1:5) {
  k &lt;- sum(as.integer(ix) == i &amp; as.integer(iy) == j)
  if (k == 0) next
  xs &lt;- c(xs, runif(k, bx[i], bx[i + 1]))
  ys &lt;- c(ys, runif(k, by[j], by[j + 1]))
}
reb &lt;- ppp(xs, ys, window = w)

round(c(original   = unname(quadrat.test(redwood, nx = 5, ny = 5)$statistic),
        rebarajado = unname(quadrat.test(reb,     nx = 5, ny = 5)$statistic)), 6)
#&gt;   original rebarajado
#&gt;    64.6129    64.6129

round(c(nn_original = mean(nndist(redwood)), nn_rebarajado = mean(nndist(reb))), 4)
#&gt;   nn_original nn_rebarajado
#&gt;        0.0393        0.0575''',
    '''d = reg[reg.patron == "redwood"]
xr, yr = (0.0, 1.0), (-1.0, 0.0)   # la ventana de redwood
ix5, iy5 = celda(d.x.values, *xr, 5), celda(d.y.values, *yr, 5)
c1 = np.zeros((5, 5), int); np.add.at(c1, (ix5, iy5), 1)

rng = np.random.default_rng(4027)
b5x, b5y = np.linspace(*xr, 6), np.linspace(*yr, 6)
xs, ys = [], []
for i in range(5):
    for j in range(5):
        k = int(c1[i, j])
        if k:
            xs += list(rng.uniform(b5x[i], b5x[i+1], k))
            ys += list(rng.uniform(b5y[j], b5y[j+1], k))
xs, ys = np.array(xs), np.array(ys)

c2 = np.zeros((5, 5), int)
np.add.at(c2, (celda(xs, *xr, 5), celda(ys, *yr, 5)), 1)
print(np.array_equal(c1, c2))
#&gt; True

chi = lambda c: float((((c - c.mean()) ** 2) / c.mean()).sum())
print([round(chi(c1), 4), round(chi(c2), 4)])
#&gt; [64.6129, 64.6129]''')

TABS_M6 = tabs(
    'El mismo patrón, cuatro rejillas',
    '''for (k in c(2, 5, 10, 20)) {
  t &lt;- quadrat.test(redwood, nx = k, ny = k)
  cat(sprintf("nx=%2d  chi2=%8.2f  p=%.5f\\n", k, t$statistic, t$p.value))
}
#&gt; nx= 2  chi2=    6.52  p=0.17806
#&gt; nx= 5  chi2=   64.61  p=0.00003
#&gt; nx=10  chi2=  202.52  p=0.00000
#&gt; nx=20  chi2=  505.74  p=0.00045''',
    '''for k in (2, 5, 10, 20):
    cc = np.zeros((k, k), int)
    np.add.at(cc, (celda(d.x.values, *xr, k), celda(d.y.values, *yr, k)), 1)
    print(k, round(chi(cc), 2))
#&gt; 2 6.52
#&gt; 5 64.61
#&gt; 10 202.52
#&gt; 20 505.74''')

TABS_M7 = tabs(
    'G, F y el átomo de los duplicados',
    '''g &lt;- Gest(p_urb, correction = c("km", "none"))   # `none` da la columna `raw`

round(c(G_empirica_en_0 = g$raw[1], G_km_en_0 = g$km[1]), 6)
#&gt; G_empirica_en_0       G_km_en_0
#&gt;        0.037494        0.000000

# Y ese 0,037494 son exactamente las sedes con un vecino a distancia cero
sum(nndist(p_urb) == 0)
#&gt; [1] 79''',
    '''dd, _ = cKDTree(XU).query(XU, k=2)
nn = dd[:, 1]

print([int((nn == 0).sum()), round(float((nn == 0).mean()), 6)])
#&gt; [79, 0.037494]

# La G empirica es la funcion de distribucion de esas distancias, y su
# salto en r = 0 es la fraccion de puntos coincidentes. No hay nada que
# corregir: hay algo que declarar.''')

TABS_M8 = tabs(
    'K, L y el desvío máximo',
    '''k &lt;- Kest(p_urb, correction = "translate")
L &lt;- sqrt(k$trans / pi)
i &lt;- which.max(abs(L - k$r))

# OJO: esto sale sobre la rejilla nativa de spatstat (513 nodos). El
# capitulo publica sus curvas en una de 101, asi que el maximo cae en
# una r vecina y el valor difiere en la tercera cifra.
round(c(r = k$r[i], L_menos_r = (L - k$r)[i]), 2)
#&gt;         r L_menos_r
#&gt;   5088.76    331.98''',
    '''# El peso de la correccion de traslacion es el area de solape de la
# ventana consigo misma desplazada por el vector que une los dos puntos.
# Para un rectangulo a x b eso es exactamente (a-|dx|)(b-|dy|).
def K_traslacion(x, y, a, b, r):
    n = len(x); W = a * b
    dx = np.abs(x[:, None] - x[None, :]); dy = np.abs(y[:, None] - y[None, :])
    dist = np.hypot(dx, dy)
    sol = np.clip(a - dx, 0, None) * np.clip(b - dy, 0, None)
    m = ~np.eye(n, dtype=bool)
    return np.array([float((1 / sol[m])[dist[m] &lt;= rr].sum())
                     for rr in r]) / (n * (n - 1) / W ** 2)

dc_ = reg[reg.patron == "cells"]
r = np.linspace(0, 0.25, 101)
K = K_traslacion(dc_.x.values, dc_.y.values, 1.0, 1.0, r)
L = np.sqrt(K / np.pi)
print(round(float(np.max(np.abs(L - r))), 4))
#&gt; 0.0846''')


# =====================================================================
# MÓDULO 5 · El test de cuadrantes y su ceguera
# =====================================================================
MOD5 = cabecera(
    5, "El test de cuadrantes", "The quadrat test",
    "Usar el χ² de cuadrantes, y ver EXACTAMENTE qué es lo que no mira, con dos "
    "patrones que comparten su χ² hasta el último decimal."
) + f"""      <p>El test de cuadrantes es el más antiguo y el más fácil de explicar: se parte la
        ventana en celdas, se cuenta cuántos puntos caen en cada una y se compara ese reparto
        con el que daría una intensidad constante. El estadístico es el χ² de siempre.</p>

      <div class="formula-box">
        <p>$$\\chi^2 = \\sum_{{j=1}}^{{m}} \\frac{{(O_j - E_j)^2}}{{E_j}},
          \\qquad E_j = \\lambda\\,|A_j|$$</p>
      </div>

      <p>Funciona, y para el patrón de Bogotá rechaza con un margen enorme. Pero tiene una
        ceguera concreta, y la mejor manera de verla no es describirla: es construir dos
        patrones que el test <strong>no pueda distinguir</strong>, y comprobar que son
        distintos.</p>

      <p>Se toma <code>redwood</code>, que está agregado, y se rehace conservando
        exactamente cuántas plántulas caen en cada celda de una rejilla
        {m5['nx']}×{m5['nx']} pero repartiéndolas <em>al azar dentro de la suya</em>. Los
        conteos por celda son los mismos, uno a uno. Luego el χ² es el mismo. Míralos.</p>

{mapa_html('cap4-ceguera-original', 'El patrón original, con sus grumos')}
{mapa_html('cap4-ceguera-rebarajado', 'El mismo reparto por celda, sin grumos')}

      <div class="key-insight">
        <p style="margin:0;">Los dos dan χ² = {firma(n(m5['original']['chi2'], 6))} con
        {ent(m5['original']['gl'])} grados de libertad. No parecido: <strong>el mismo
        número</strong>, y por construcción, no por casualidad. Y sin embargo la distancia
        media al vecino más próximo pasa de {firma(n(m5['nn_original'], 5))} a
        {firma(n(m5['nn_rebarajado'], 5))} —se multiplica por
        {n(m5['nn_cociente'], 5)}— y el índice de Clark-Evans, de
        {n(m5['ce_original'], 5)} a {n(m5['ce_rebarajado'], 5)}.</p>
      </div>

      <p>Lo que el χ² no mira es <strong>dónde cae cada punto dentro de su celda</strong>.
        Dicho de otro modo: es ciego a toda estructura de escala menor que el cuadrante. Por
        eso pasar el test de cuadrantes no certifica aleatoriedad; certifica que los
        <em>conteos</em> son compatibles con ella, que es bastante menos.</p>

      <p>Queda una pregunta incómoda que el módulo siguiente recoge: si la ceguera depende
        del tamaño de la celda, ¿qué tamaño hay que elegir? Y si la respuesta cambia el
        veredicto, ¿de quién es el veredicto?</p>

{TABS_M5}""" + CIERRE


# =====================================================================
# MÓDULO 6 · El tamaño del cuadrante
# =====================================================================
_nx_baja = m6['redwood_nx_esperanza_baja']
_n_tam = len(m6['nxs'])
MOD6 = cabecera(
    6, "El tamaño del cuadrante", "Quadrat size",
    "Reconocer el MAUP del capítulo 3 dentro de un test de patrones puntuales: "
    "la misma pregunta, el mismo dato y un veredicto que depende de la celda."
) + f"""      <p>El módulo 5 dejó la pregunta abierta: si el χ² es ciego por debajo del tamaño de
        la celda, ¿qué tamaño se elige? No hay una respuesta técnica, y eso ya lo vimos en
        el capítulo 3 con otro nombre. Es el <strong>efecto de escala</strong> del MAUP,
        ahora sobre un patrón puntual.</p>

      <p>Se barre el mismo patrón con rejillas de 2×2 a 20×20 y se anota el χ² y su
        p-valor. Sobre <code>redwood</code>, {firma(ent(m6['redwood_rechazos']))} de los
        {ent(_n_tam)} tamaños rechazan la hipótesis de intensidad constante. El que no
        rechaza es el más grueso, y no porque el patrón sea distinto: porque con cuatro
        celdas no hay resolución para ver los grumos.</p>

      <p>Y en el otro extremo el problema se invierte. A partir de nx =
        {firma(ent(_nx_baja))} aparecen celdas con esperanza menor que 5, que es donde la
        aproximación χ² deja de valer. <strong>La escala que más resuelve es la que rompe el
        supuesto</strong>, y entre las dos no hay un tamaño «correcto» que la teoría
        entregue: hay una decisión del analista, que se declara.</p>

{sim('cap4-barrido', 'El veredicto en función de la celda',
     'Barre el tamaño de la rejilla sobre los tres patrones y mira dónde cambia el veredicto y dónde se rompe el supuesto.', 300)}

      <p>La lectura del capítulo 3 vale palabra por palabra: la escala no es un detalle de
        implementación, es parte del resultado, y un test de cuadrantes sin su tamaño de
        celda en el pie está incompleto. La diferencia es que aquí hay salida — las
        funciones de resumen de los módulos 7 a 9 no necesitan elegir ninguna celda.</p>

{TABS_M6}
      <p>Con seis módulos hechos ya hay cuerda suficiente para caer en las trampas
        habituales de este material. Las cuatro de abajo se responden con lo visto hasta
        aquí; ninguna requiere lo que viene después.</p>

{quiz_html('cap4-trampas', 'Cuatro trampas de patrones puntuales',
           'Un bloque intermedio, no el examen: si fallas una, vuelve al módulo que la cubre.')}

      <p>Las doce opciones traen su explicación, así que una fallada deja tanto como una
        acertada. Y con esto cierra la primera mitad del capítulo: hasta aquí se ha contado
        en cajas, y siempre ha habido que elegir la caja. Lo que viene deja de contar y
        empieza a medir distancias, que es lo que quita esa elección de en medio.</p>""" + CIERRE


# =====================================================================
# MÓDULO 7 · Las funciones G y F
# =====================================================================
MOD7 = cabecera(
    7, "Las funciones G y F", "Nearest-neighbour and empty-space functions",
    "Describir el patrón con distancias en vez de con conteos, y distinguir qué "
    "mira cada una de las dos funciones."
) + f"""      <p>Las funciones de resumen resuelven el problema del módulo 6 por la vía de no
        tener que elegir ninguna celda: en vez de contar en cajas, miden distancias. Las dos
        primeras son hermanas y se confunden constantemente, así que conviene fijar la
        diferencia antes de mirar ninguna curva.</p>

      <p><strong>G(r)</strong> mira desde los <em>puntos</em>: es la proporción de puntos
        cuyo vecino más próximo está a distancia r o menos. <strong>F(r)</strong> mira desde
        el <em>espacio vacío</em>: se toman sitios cualesquiera de la ventana —no puntos del
        patrón— y se mide la distancia al punto más cercano.</p>

      <p>Separan los regímenes en direcciones opuestas, y por eso se enseñan juntas. Un
        patrón agregado deja mucho hueco: sus puntos tienen vecinos muy cerca, así que G
        sube pronto, pero hay zonas grandes sin nada y F sube tarde. Un patrón regular hace
        lo contrario.</p>

{sim('cap4-gf', 'G y F sobre los tres regímenes',
     'Elige el patrón: se dibujan la G y la F observadas contra las que daría CSR.', 300)}

      <p>Sobre las sedes de Bogotá aparece algo que los patrones de libro no tienen, y que
        conviene mirar de frente en vez de barrer debajo de la alfombra.</p>

      <div class="key-insight">
        <p style="margin:0;">La G <em>empírica</em> de las sedes no arranca en cero: vale
        {firma(n(m7['duplicados']['g_empirica_en_cero'], 6))} justo en r = 0. Eso solo puede
        pasar si hay puntos <strong>coincidentes</strong>, y los hay:
        {firma(ent(m7['bogota']['coincidentes']))} sedes —el
        {n(m7['bogota']['coincidentes_pct'], 5)} %— comparten coordenada exacta con otra,
        hasta {ent(m7['duplicados']['maximo_por_sitio'])} en un mismo punto. Son sedes
        distintas en el mismo edificio.</p>
      </div>

      <p>Un patrón con puntos duplicados <strong>no es un proceso puntual simple</strong>, y
        eso rompe un supuesto de todos los estimadores de este capítulo. No se ha corregido
        —colapsarlos cambiaría n y con él la λ que el módulo 1 publicó— y por tanto se
        declara. El detalle fino: el estimador de Kaplan-Meier de G, que es el que corrige
        el borde, vale {n(m7['duplicados']['g_km_en_cero'], 6)} en r = 0 <em>por
        convenio</em>, así que la corrección y el átomo viven en el mismo punto de la curva
        y el segundo desaparece de la vista. Por eso el capítulo dibuja las dos.</p>

{TABS_M7}""" + CIERRE


# =====================================================================
# MÓDULO 8 · La función K de Ripley
# =====================================================================
MOD8 = cabecera(
    8, "La función K de Ripley", "Ripley's K function",
    "Medir la estructura a TODAS las escalas a la vez, y leerla con la "
    "transformación que la hace comparable contra una recta."
) + f"""      <p>G y F miran solo al vecino más próximo, que es una escala sola. La función K de
        Ripley mira todas: K(r) es el número esperado de puntos a distancia r o menos de un
        punto cualquiera del patrón, dividido por la intensidad.</p>

      <div class="formula-box">
        <p>$$\\hat{{K}}(r) = \\frac{{1}}{{\\hat{{\\lambda}}^2 |W|}}
          \\sum_{{i}} \\sum_{{j \\neq i}} w_{{ij}}\\, \\mathbf{{1}}(d_{{ij}} \\leq r)
          \\qquad \\text{{bajo CSR}} \\quad K(r) = \\pi r^2$$</p>
      </div>

      <p>Bajo aleatoriedad completa K vale exactamente πr², que es una parábola. Comparar
        una curva contra una parábola a ojo es incómodo —la vista juzga mal las curvaturas—
        y de ahí la transformación de Besag: L(r) = √(K(r)/π), que bajo CSR es la recta
        L = r. Se dibuja L(r) − r contra r, y entonces CSR es el eje horizontal: por encima
        hay agregación y por debajo, regularidad.</p>

{sim('cap4-kl', 'K y L sobre el mismo patrón',
     'Conmuta entre K y L − r: es la misma información, y solo una de las dos se lee de un vistazo.', 300)}

      <p>Sobre las sedes de Bogotá, L − r alcanza su máximo de
        {firma(n(m8['bogota']['max_desvio'], 2), ' m')} a una distancia de
        {firma(n(m8['bogota']['r_max_desvio'], 0), ' m')}, siempre por encima de cero: el
        patrón está agregado a todas las escalas medidas. Los tres canónicos ordenan sus
        desvíos como cabía esperar —{n(m8['cells']['max_desvio'], 5)} en las células,
        {n(m8['japanesepines']['max_desvio'], 5)} en los pinos y
        {n(m8['redwood']['max_desvio'], 5)} en las secuoyas— con el signo de cada uno
        marcando su régimen.</p>

      <p>Ese <em>a todas las escalas</em> es a la vez la fuerza de K y su problema, y el
        módulo siguiente lo desmonta: una función acumulativa arrastra lo que ya contó, así
        que no sirve para decir <em>dónde</em> está la estructura.</p>

{TABS_M8}""" + CIERRE


TABS_M9 = tabs(
    'La correlación de pares, y dónde está la estructura',
    '''gg &lt;- pcf(redwood, correction = "translate")

round(c(g_max = max(gg$trans[-1]),
        r_en_el_max = gg$r[which.max(replace(gg$trans, 1, -Inf))]), 4)
#&gt;       g_max r_en_el_max
#&gt;      3.2802      0.0220''',
    '''# spatstat suaviza g con un nucleo; aqui va la version cruda, que es
# la definicion: cuantas parejas caen en cada anillo, contra las que
# caerian bajo CSR. Sale MAS alta y mas ruidosa — y esa diferencia es
# justo lo que el suavizado compra.
dr = reg[reg.patron == "redwood"]
xx, yy = dr.x.values, dr.y.values
n = len(xx)
D2 = np.hypot(xx[:, None] - xx[None, :],
              yy[:, None] - yy[None, :])[~np.eye(n, dtype=bool)]

bordes = np.linspace(0, 0.25, 26)
cuenta, _ = np.histogram(D2, bins=bordes)
centros = (bordes[:-1] + bordes[1:]) / 2
anillo = np.pi * (bordes[1:] ** 2 - bordes[:-1] ** 2)
g = cuenta / (n * (n / 1.0) * anillo)

print([round(float(g.max()), 3), round(float(centros[g.argmax()]), 4)])
#&gt; [6.625, 0.025]''')

TABS_M10 = tabs(
    'Las tres correcciones, y lo que cuesta ignorarlas',
    '''# La K sin corregir, contra la corregida por traslacion
kn &lt;- Kest(p_urb, correction = "none")

round(100 * max((k$trans - kn$un) / pmax(k$trans, 1e-9)), 1)
#&gt; [1] 29.6

# El coste NO se anuncia aqui como salida esperada: depende de la
# maquina. Mideloo tu mismo y compara el orden de magnitud.
# system.time(Kest(p_urb, correction = "translate"))
# system.time(Kest(p_urb, correction = "isotropic"))''',
    '''# Sin correccion de borde, K es puro conteo de parejas: el arbol k-d
# las cuenta sin materializar la matriz de distancias, que para 2 107
# puntos ocuparia decenas de GB.
arbol = cKDTree(XU)
rr = np.linspace(0, 5868, 60)
pares = arbol.count_neighbors(arbol, rr) - len(XU)
K_sin = pares * v_urb.area / (len(XU) * (len(XU) - 1))

print([int(pares[-1]), round(float(K_sin[-1]) / 1e6, 2)])
#&gt; [1014516, 84.61]''')

TABS_M11 = tabs(
    'Una envolvente, y lo que su p-valor no dice',
    '''set.seed(4028)
e &lt;- envelope(japanesepines, Kest, nsim = 39, correction = "translate",
              savefuns = TRUE, verbose = FALSE)

# Con nsim = 39 y nrank = 1, la banda es un contraste PUNTUAL al 5 %
round(c(nivel_puntual = 2 / (39 + 1), p_minimo = 1 / (39 + 1)), 4)
#&gt; nivel_puntual      p_minimo
#&gt;         0.050         0.025

# El test global reutiliza las MISMAS simulaciones: no hacen falta 39 mas
round(dclf.test(e)$p.value, 4)
#&gt; [1] 0.225''',
    '''rng = np.random.default_rng(4028)
r2 = np.linspace(0, 0.25, 51)
sims = np.empty((999, len(r2)))
for s in range(999):
    m = rng.poisson(65)                    # propiedad (1) de CSR
    px, py = rng.random(m), rng.random(m)  # propiedad (2)
    sims[s] = K_traslacion(px, py, 1.0, 1.0, r2)

lo, hi = np.nanpercentile(sims, 2.5, axis=0), np.nanpercentile(sims, 97.5, axis=0)
fuera = ((sims &lt; lo) | (sims &gt; hi)).any(axis=1)

# Cuantas simulaciones de CSR PURO se salen de su propia banda al 95 %
print([int(fuera.sum()), round(100 * float(fuera.mean()), 1)])
#&gt; [366, 36.6]''')


# =====================================================================
# MÓDULO 9 · La correlación de pares g(r)
# =====================================================================
MOD9 = cabecera(
    9, "La correlación de pares g(r)", "Pair correlation function",
    "Leer dónde está la estructura, y entender por qué una función acumulativa "
    "no puede decirlo."
) + f"""      <p>K tiene un defecto que se ve en cuanto se busca: es <strong>acumulativa</strong>.
        K(r) cuenta todos los vecinos hasta r, así que si un patrón se agrupa a 20 metros,
        K sigue por encima de la teórica a 500 metros —aunque a 500 metros no pase
        absolutamente nada—, porque los vecinos de 20 metros siguen contados dentro.</p>

      <p>La correlación de pares g(r) es su derivada normalizada: mira solo el anillo de
        radio r, no el disco. Bajo CSR vale 1 en todo r, y por encima o por debajo indica
        más o menos parejas de las esperadas <em>a esa distancia concreta</em>.</p>

      <div class="formula-box">
        <p>$$g(r) = \\frac{{1}}{{2\\pi r}} \\frac{{dK(r)}}{{dr}}
          \\qquad \\text{{bajo CSR}} \\quad g(r) = 1$$</p>
      </div>

{sim('cap4-kg', 'K contra g sobre el mismo patrón',
     'Las dos curvas del mismo dato: mira hasta dónde sigue K separada de su teórica y dónde vuelve g a 1.', 300)}

      <p>Sobre las secuoyas, g alcanza {firma(n(m9['redwood']['g_max'], 5))} a una distancia
        de {firma(n(m9['redwood']['r_g_max'], 5))} y vuelve a rondar 1 mucho antes de que K
        se despegue de su teórica. Esa distancia es <strong>el tamaño de los grumos</strong>,
        y K no la sabe decir.</p>

      <p>Sobre las sedes de Bogotá, g llega a {firma(n(m9['bogota']['g_max'], 5))} en
        {firma(n(m9['bogota']['r_g_max'], 0), ' m')}. Es una agregación moderada y a escala
        de manzana, no de barrio: los colegios se agrupan a la distancia a la que se agrupan
        las manzanas construidas, que es una lectura urbana y no estadística.</p>

      <p>La contrapartida de g es que hay que estimarla suavizando, y ahí entra un ancho de
        banda que el capítulo 5 va a discutir en serio. La pestaña de Python de abajo enseña
        la versión cruda, sin suavizar, para que se vea qué compra el suavizado.</p>

{TABS_M9}""" + CIERRE


# =====================================================================
# MÓDULO 10 · Efectos de borde
# =====================================================================
MOD10 = cabecera(
    10, "Efectos de borde", "Edge effects",
    "Ver por qué ignorar el borde no añade ruido sino SESGO, y en qué dirección; "
    "y cuánto cuesta corregirlo sobre una ventana de verdad."
) + f"""      <p>Todo lo anterior tiene una grieta. Un punto pegado al borde de la ventana tiene
        vecinos <em>fuera</em>, y nadie los ha observado. El estimador cuenta menos vecinos
        de los que hay, y no de vez en cuando: siempre. Faltan vecinos, nunca sobran.</p>

      <div class="key-insight">
        <p style="margin:0;">Por eso ignorar el efecto de borde no añade ruido, <strong>añade
        dirección</strong>: empuja siempre hacia «más regular de lo que es». Sobre las sedes
        de Bogotá, la K sin corregir se queda hasta un
        {firma(n(m10['sesgo_max_pct'], 5), ' %')} por debajo de la corregida, y el máximo se
        alcanza en r = {firma(n(m10['r_sesgo_max'], 0), ' m')}, porque a r grande casi todos
        los discos tocan el borde.</p>
      </div>

      <p>Hay tres correcciones clásicas. La de <strong>borde</strong> descarta los puntos
        cuyo disco no cabe entero; la de <strong>traslación</strong> pesa cada pareja por el
        área de solape de la ventana consigo misma desplazada; la <strong>isotrópica</strong>
        de Ripley pesa por la fracción del círculo que queda dentro. Las tres corrigen; no
        las tres cuestan lo mismo.</p>

{sim('cap4-bordes', 'Las tres correcciones, y la que no corrige',
     'Activa y desactiva cada corrección sobre el patrón colombiano y mira cuánto se mueve la curva.', 300)}

      <p>Y aquí está la medición que ningún libro trae, porque los libros trabajan en
        rectángulos. La ventana urbana de Bogotá tiene
        {firma(ent(m10['ventana']['piezas']))} piezas,
        {ent(m10['ventana']['agujeros'])} agujeros y
        {firma(ent(m10['ventana']['vertices']))} vértices. Sobre ella, una sola estimación de
        K cuesta esto:</p>

      <table class="tabla-datos">
        <caption>Segundos por estimación de K sobre el patrón colombiano, en la máquina del
          precálculo ({m10['coste']['medido_en']}). Los tiempos absolutos dependen de la
          máquina; lo que no depende es el orden de magnitud entre ellos.</caption>
        <thead><tr><th scope="col">Corrección</th><th scope="col">Segundos</th>
          <th scope="col">Una envolvente de {ent(m11['nsim'])} simulaciones</th></tr></thead>
        <tbody>
{fila('Sin corregir', n(CORR['none']['segundos'], 2), '—')}{fila('De borde', n(CORR['border']['segundos'], 2), '—')}{fila('De traslación', firma(n(CORR['translate']['segundos'], 2)),
      firma(n(m10['coste']['minutos_envolvente_traslacion'], 1), ' minutos'))}{fila('Isotrópica', firma(n(CORR['isotropic']['segundos'], 2)),
      firma(n(m10['coste']['horas_envolvente_isotropica'], 1), ' horas'))}        </tbody>
      </table>

      <p>La isotrópica cuesta {firma(n(m10['coste']['veces_isotropica_sobre_traslacion'], 0))}
        veces lo que la de traslación, y no por el número de puntos: por el perímetro contra
        el que hay que corregir, que la de Ripley recorre pareja a pareja. El mismo cálculo
        sobre un patrón canónico con <em>más</em> puntos que éste pero ventana rectangular
        se hace en una fracción de segundo. Lo que se paga es el borde, no n.</p>

      <p>Por eso este capítulo <strong>precalcula sus envolventes con la corrección de
        traslación</strong> y calcula la isotrópica una sola vez por patrón, para poder
        publicar la diferencia. No es un atajo silencioso: es una decisión declarada, y la
        tabla de arriba es su justificación.</p>

      <p>Un último aviso que enlaza con el módulo 7: en r = 0 la K sin corregir
        <em>no</em> vale cero, vale {firma(n(m10['k_cero_sin_corregir'], 2))}. Son las
        parejas a distancia exactamente cero, es decir las sedes coincidentes. El átomo de
        los duplicados asoma en todos los estimadores, no solo en G.</p>

{TABS_M10}""" + CIERRE


# =====================================================================
# MÓDULO 11 · Envolventes de simulación
# =====================================================================
_e39, _e999 = ESC[39], ESC[999]
MOD11 = cabecera(
    11, "Envolventes de simulación", "Simulation envelopes",
    "Construir la banda de referencia que hace interpretable una curva, y saber "
    "exactamente qué NO dice el p-valor que se lee de ella."
) + f"""      <p>El módulo 4 dejó el problema planteado: una curva observada no se puede juzgar sin
        saber cuánto se mueve el azar. La solución es simular. Se generan
        {firma(ent(m11['nsim']))} patrones de CSR con la misma intensidad y la misma
        ventana, se calcula K para cada uno y se dibuja la banda que forman. Si la observada
        se sale, hay algo que CSR no explica.</p>

      <p>Funciona, y es la herramienta estándar. Pero el número que se lee de ella se
        malinterpreta casi siempre, y este módulo existe sobre todo para eso.</p>

{sim('cap4-envolvente', 'La envolvente y la curva observada',
     'Elige el patrón: la banda son las simulaciones de CSR y la línea gruesa, el dato.', 300)}

      <div class="key-insight">
        <p style="margin:0;">La banda puntual es un intervalo al 95 % <strong>para cada r por
        separado</strong>. Mirar la curva entera y decir «se sale en algún sitio, luego
        p &lt; 0,05» es hacer un centenar de contrastes y quedarse con el peor. ¿Cuánto
        importa? Se mide: de las {ent(m11['tasa_salida_bogota']['nsim'])} simulaciones de CSR
        <em>puro</em> usadas para construir la banda del patrón colombiano,
        {firma(ent(m11['tasa_salida_bogota']['fuera']))} —el
        {firma(n(m11['tasa_salida_bogota']['pct'], 5), ' %')}— se salen de ella en algún r.
        Todas eran nulas por construcción.</p>
      </div>

      <p>La salida correcta es un <strong>test de desviación global</strong>, que resume la
        curva entera en un número antes de compararla: el de Diggle-Cressie-Loosmore-Ford
        integra el cuadrado de la separación, y el MAD toma su máximo. Sobre el patrón
        colombiano, el dclf da p = {firma(n(m11['test_global']['dclf_bogota_p'], 5))} y el
        MAD, {n(m11['test_global']['mad_bogota_p'], 5)}; sobre los pinos japoneses,
        {n(m11['test_global']['dclf_japanesepines_p'], 5)} y
        {n(m11['test_global']['mad_japanesepines_p'], 5)}.</p>

      <p>Queda el otro malentendido, el de cuántas simulaciones hacen falta. La respuesta
        empieza por una cifra que sorprende: con {ent(m11['nsim'])} simulaciones el p-valor
        más pequeño que existe es {firma(n(m11['p_minimo'], 5))}, y no hay separación de la
        curva que lo baje. El p-valor mínimo es 1/(nsim+1) y no es una convención: es
        aritmética.</p>

{sim('cap4-nsim', 'Cuántas simulaciones, y a qué nivel',
     'Sube nsim con la banda por defecto y con el nivel fijo al 5 %: las dos series se leen al revés.', 300)}

      <p>Y aquí está la trampa que casi todo el mundo pisa. La banda que <code>envelope()</code>
        dibuja por defecto es el <em>mínimo y el máximo</em> de las simulaciones, cuyo nivel
        puntual vale 2/(nsim+1). Con {ent(_e39['nsim'])} simulaciones eso es un contraste al
        {n(_e39['nivel_defecto'], 5)}; con {ent(_e999['nsim'])}, al
        {n(_e999['nivel_defecto'], 5)}. <strong>Subir nsim sin tocar nada más no afina la
        misma banda: cambia de contraste</strong>, y por eso la banda se ENSANCHA
        —{n(m11['escala_resumen']['veces_defecto'], 5)} veces a lo largo del barrido— en vez
        de estrecharse.</p>

      <p>Manteniendo el nivel fijo al 5 %, que exige subir el rango con nsim, la banda sí se
        estrecha: {n(m11['escala_resumen']['veces_5pct_alcanzable'], 5)} veces entre los dos
        extremos donde ese nivel es alcanzable. Y con {ent(ESC[19]['nsim'])} simulaciones
        <strong>no lo es</strong>: el rango que haría falta es
        {n(ESC[19]['nrank_para_5pct'], 5)}, y los rangos son enteros. Elegir nsim no es
        elegir precisión, es elegir qué contrastes existen.</p>

{TABS_M11}""" + CIERRE


# =====================================================================
# MÓDULO 12 · Autoevaluación y ejercicios guiados
# =====================================================================
def ejercicio(k, e):
    """El marcado de la CASA, no uno inventado.

    `cuenta_sitio.py` cuenta los ejercicios por `.ejercicio-guiado` y el
    desplegable se cablea por `.ejercicio-boton`; inventarse selectores
    deja un capítulo que se ve perfecto, con cero ejercicios contados y
    los botones muertos, sin un solo error en consola (A.13).
    """
    pasos = "".join(
        f"                <tr><th scope=\"row\">{p['paso']}</th><td>{p['valor']}</td></tr>\n"
        for p in e["pasos"])
    return f"""
        <div class="ejercicio-guiado">
          <p class="ejercicio-enunciado"><span class="ejercicio-numero">{k}.</span><strong>{e['titulo']}.</strong>
            {e['enunciado'].replace('`', '')}</p>
          <div class="ejercicio-acciones">
            <button type="button" class="ejercicio-boton" aria-expanded="false" aria-controls="cap4-e{k}-sol">
              <i class="fas fa-key" aria-hidden="true"></i> Solución <i class="fas fa-chevron-down" aria-hidden="true"></i>
            </button>
          </div>
          <div class="ejercicio-panel solucion" id="cap4-e{k}-sol" hidden>
            <table>
              <caption>Los pasos de la solución, calculados en R por <code>precalculo/genera_soluciones.R</code>.</caption>
              <thead><tr><th scope="col">Paso</th><th scope="col">Valor</th></tr></thead>
              <tbody>
{pasos}
              </tbody>
            </table>
            <p class="ejercicio-lectura">{e['lectura']}</p>
          </div>
        </div>
"""


# Las soluciones del capítulo 4 viajan como e1…e5 y no como una lista:
# cada ejercicio es una clave, para que el auditor pueda nombrarlos.
EJERCICIOS = [S[f"e{i}"] for i in range(1, S["meta"]["n_ejercicios"] + 1)]
EJ = "".join(ejercicio(i + 1, e) for i, e in enumerate(EJERCICIOS))

MOD12 = cabecera(
    12, "Autoevaluación y ejercicios guiados", "Self-assessment and guided exercises",
    "Comprobar lo aprendido y practicar sobre datos reales las decisiones que este "
    "capítulo obliga a tomar y a declarar."
) + f"""      <p>El capítulo ha defendido una sola idea desde el módulo 1: en un patrón puntual, la
        pregunta «¿está agrupado?» no tiene respuesta hasta que se fijan la ventana, la
        escala y la referencia contra la que se compara. Todo lo demás —cuadrantes, G, F, K,
        g, envolventes— son maneras de fijar esas tres cosas y de declararlas.</p>

      <p>Ocho preguntas, sin nota, que se suman a las cuatro del módulo 6. Cada opción trae
        su explicación, así que equivocarse aquí vale tanto como acertar.</p>

{quiz_html('cap4-quiz', 'Autoevaluación del capítulo 4',
           'Ocho preguntas sobre ventana, intensidad, funciones de resumen, borde y envolventes.')}

      <p>Y cinco ejercicios guiados con su solución calculada —uno más que el molde, porque
        el capítulo cubre dos semanas—. Los cinco terminan en una decisión que hay que
        defender, que es lo que este capítulo entrena de verdad.</p>

{EJ}
      <div class="tip-box">
        <h4>Dónde sigue esto</h4>
        <p style="margin-bottom:0;">El capítulo 5 recoge el hilo donde éste lo deja: en vez
        de resumir el patrón con funciones, estima la <strong>intensidad como superficie</strong>
        —el suavizado por núcleos— y luego la modela con covariables. La pregunta que abre
        aquel capítulo es la que aquí se ha esquivado: si λ no es constante, ¿cómo es?
        Los anteriores son
        <a href="capitulo-1-datos-espaciales.html">Datos espaciales y la primera ley de la
        geografía</a>, <a href="capitulo-2-crs-georreferenciacion.html">SIG, sistemas de
        referencia y georreferenciación</a> y
        <a href="capitulo-3-cartografia-maup.html">Cartografía estadística y el MAUP</a>,
        cuyo efecto de escala reaparece en el módulo 6 de éste.</p>
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
    + "    const DATOS_CAP4 = " + json.dumps(D, ensure_ascii=False) + ";\n"
    + "    const SOL_CAP4 = " + json.dumps(S, ensure_ascii=False) + ";\n"
    + "    const D4 = DATOS_CAP4;\n"
)


# =====================================================================
# Los mapas, con su JSON LITERAL (no una función): `geomapas()` del
# auditor de prosa solo puede comprobar el n y el peso de un mapa cuya
# fuente sea un objeto.
# =====================================================================
def geomapa(ident, clave, extra=""):
    fuente = json.dumps(M[clave], ensure_ascii=False)
    return f"    GEOMAPAS['{ident}'] = {{ fuente: {fuente}{extra} }};\n"


def _etq(texto):
    return ", etiqueta: " + json.dumps(texto, ensure_ascii=False)


# ---------------------------------------------------------------------
# LA TABLA DE RESPALDO DE LOS DOS MAPAS DEL MÓDULO 5 (T3.3)
#
# Por qué solo estos dos, y por qué estos dos SÍ. El resto de los mapas
# del capítulo son patrones puntuales cuya tabla serían sus coordenadas,
# y una lista de 2 107 pares de metros no es la vía al dato de nadie: lo
# que esos mapas dicen —n, área, lambda, la R de cada régimen— ya está en
# la prosa y en sus tablas.
#
# El módulo 5 es el caso contrario. Afirma que la rebaraja conserva el
# conteo de cada celda «uno a uno» y remata con «Míralos». Quien no ve los
# dos lienzos no tiene dónde mirarlo: el chi² idéntico que la prosa
# publica es la CONSECUENCIA de esa igualdad, no la igualdad. Para ese
# lector, esta tabla es el módulo.
#
# La forma la fija el precedente de `TABLA_AGREGACION` del capítulo 1: las
# dos cantidades que hay que comparar van en COLUMNAS de la misma fila.
# Con una tabla por patrón habría que recordar 25 cifras de memoria para
# comprobar la afirmación, que es pedirle al lector justo lo que la tabla
# existe para ahorrarle.
#
# Las 25 cifras salen de `D4.m5.celdas`, que las calcula `quadratcount()`
# en R y recuenta `audita_cap4.py` con su propio binado. Aquí no se cuenta
# nada: se transcribe.
TABLA_CEGUERA = """, tabla: function () {
        const c = D4.m5.celdas;
        let filas = '';
        for (let k = 0; k < c.ny; k++) {
          for (let i = 0; i < c.nx; i++) {
            filas += `<tr><th scope="row">fila ${k + 1} (y en ${c.filas_y[k]}), `
              + `columna ${i + 1} (x en ${c.columnas_x[i]})</th>`
              + `<td>${c.original[k][i]}</td><td>${c.rebarajado[k][i]}</td></tr>`;
          }
        }
        return `<table><caption>Los cuadrantes de la rejilla ${c.nx}\u00d7${c.ny}: `
          + `cuántas plántulas caen en cada uno antes y después de rebarajar. `
          + `Las filas van de arriba abajo, como en el mapa.</caption>`
          + `<thead><tr><th scope="col">Celda</th><th scope="col">Original</th>`
          + `<th scope="col">Rebarajado</th></tr></thead><tbody>${filas}</tbody>`
          + `<tfoot><tr><th scope="row">Total</th><td>${D4.m5.n}</td>`
          + `<td>${D4.m5.n}</td></tr></tfoot></table>`;
      }"""


GEOMAPAS_JS = (
    geomapa('cap4-urbano', 'patron_urbano',
            _etq('Las 2 107 sedes educativas que caen dentro del perímetro urbano de '
                 'Bogotá, sobre el contorno del propio perímetro.'))
    + geomapa('cap4-dc', 'patron_dc',
              _etq('Las mismas sedes sobre el Distrito Capital completo, cuya superficie '
                   'es más de cuatro veces mayor.'))
    + geomapa('cap4-cells', 'cells',
              _etq('Patrón regular: 42 células biológicas, más separadas entre sí de lo '
                   'que daría el azar.'))
    + geomapa('cap4-japanesepines', 'japanesepines',
              _etq('Patrón aleatorio: 65 pinos japoneses, sin atracción ni repulsión '
                   'aparentes.'))
    + geomapa('cap4-redwood', 'redwood',
              _etq('Patrón agregado: 62 plántulas de secuoya, en grumos alrededor de los '
                   'árboles madre.'))
    + geomapa('cap4-ceguera-original', 'ceguera_original',
              _etq('Las plántulas de secuoya con la rejilla de cuadrantes encima: los '
                   'grumos se ven dentro de las celdas.') + TABLA_CEGUERA)
    + geomapa('cap4-ceguera-rebarajado', 'ceguera_rebarajado',
              _etq('El mismo número de puntos en cada celda, repartidos al azar dentro '
                   'de la suya: mismo chi cuadrado, sin grumos.') + TABLA_CEGUERA)
)


# =====================================================================
# Los simuladores
#
# NO se interpola nada aquí: el JS lee `D4` en tiempo de ejecución. Es la
# regla de los capítulos 1 a 3 y tiene un motivo concreto — una cifra
# interpolada en el JS se queda vieja en cuanto el precálculo cambia, sin
# que nada falle.
# =====================================================================
SIMULADORES_JS = r"""
    // `n5` NO lo trae la plantilla: lo define cada capítulo. Suponerlo
    // costó un ReferenceError que se llevó por delante
    // `iniciarSimuladores()` entero (A.13, nº 4).
    const n5 = (x, d) => Number(x).toFixed(d == null ? 5 : d);
    const miles4 = x => Math.round(Number(x)).toLocaleString('es-ES').replace(/\./g, ' ');

    // CONTRATO DEL MOTOR: un simulador DEVUELVE sus gráficos. No existe
    // `registrarGrafico`.
    const C4 = { verde: '#1a7358', naranja: '#FF6600', gris: '#8a8a8a',
                 azul: '#0072B2', rojo: '#D55E00', morado: '#7B3FA0' };

    function lectura4(raiz, pares) {
      const c = raiz.querySelector('.simulador-lectura');
      if (!c) return;
      c.innerHTML = pares.map(([k, v]) =>
        `<span class="lectura-item"><span class="lectura-etiqueta">${k}</span>` +
        `<span class="lectura-valor">${v}</span></span>`).join('');
    }

    function botones4(raiz, ops, alPulsar, activo) {
      const cont = raiz.querySelector('.simulador-controles');
      if (!cont) return;
      cont.innerHTML = '';
      ops.forEach((op, i) => {
        const b = document.createElement('button');
        b.className = 'sim-btn' + (i === (activo || 0) ? ' active' : '');
        b.textContent = op.etiqueta;
        b.onclick = () => {
          cont.querySelectorAll('.sim-btn').forEach(x => x.classList.remove('active'));
          b.classList.add('active');
          alPulsar(op.valor);
        };
        cont.appendChild(b);
      });
    }

    // Una curva (r, y) para Chart.js, saltando lo que no sea finito.
    const curva4 = (rs, ys) => rs.map((r, i) => ({ x: r, y: ys[i] }))
      .filter(p => Number.isFinite(p.x) && Number.isFinite(p.y));

    const ejesXY = (tx, ty) => ({
      x: { type: 'linear', title: { display: true, text: tx } },
      y: { title: { display: true, text: ty } }
    });

    // --- Módulo 2 · contar en cuadrantes -----------------------------
    SIMULADORES['cap4-cuadrantes'] = function (raiz) {
      const q = D4.m2.urbana, h = D4.m2.urbana_hist;
      const ctx = raiz.querySelector('canvas').getContext('2d');
      const g = new Chart(ctx, {
        data: {
          labels: h.centros.map(c => n5(c, 0)),
          datasets: [
            { type: 'bar', label: 'celdas observadas', data: h.conteo,
              backgroundColor: C4.verde },
            { type: 'line', label: 'referencia: una Poisson de la misma media',
              data: h.teorico, borderColor: C4.naranja, borderDash: [6, 4],
              pointRadius: 0, tension: 0.3 }
          ]
        },
        options: { responsive: true, maintainAspectRatio: false,
          scales: { y: { beginAtZero: true, title: { display: true, text: 'celdas' } },
                    x: { title: { display: true, text: 'sedes en la celda' } } } }
      });
      lectura4(raiz, [
        ['rejilla', q.nx + ' × ' + q.ny],
        ['celdas vivas', q.celdas],
        ['índice de dispersión', n5(q.dispersion, 3)],
        ['bajo Poisson valdría', '1'],
        ['χ²', n5(q.chi2, 2)],
        ['la celda más poblada', q.maximo + ' sedes'],
        ['celdas con esperanza < 5', q.celdas_esperanza_baja]
      ]);
      return [g];
    };

    // --- Módulo 3 · los tres regímenes -------------------------------
    SIMULADORES['cap4-regimenes'] = function (raiz) {
      const CLAVES = ['cells', 'swedishpines', 'japanesepines', 'redwood', 'bogota'];
      const ETQ = ['Células', 'Pinos suecos', 'Pinos japoneses', 'Secuoyas', 'Sedes de Bogotá'];
      let i = 0;
      const ctx = raiz.querySelector('canvas').getContext('2d');
      const g = new Chart(ctx, {
        type: 'bar',
        data: { labels: [], datasets: [{ label: 'puntos', data: [], backgroundColor: C4.verde }] },
        options: { responsive: true, maintainAspectRatio: false,
          scales: { y: { beginAtZero: true, title: { display: true, text: 'puntos' } },
                    x: { title: { display: true, text: 'distancia al vecino más próximo' } } } }
      });
      const pinta = () => {
        const d = D4.m3[CLAVES[i]], h = d.histograma_nn;
        g.data.labels = h.centros.map(c => n5(c, c > 10 ? 0 : 3));
        g.data.datasets[0].data = h.conteo;
        g.data.datasets[0].backgroundColor =
          d.clark_evans > 1 ? C4.azul : (d.clark_evans < 0.95 ? C4.rojo : C4.verde);
        g.update();
        lectura4(raiz, [
          ['patrón', d.nombre], ['n', miles4(d.n)],
          ['d̄ observada', n5(d.nn_media, d.nn_media > 10 ? 1 : 4)],
          ['d̄ bajo azar', n5(d.nn_esperada, d.nn_esperada > 10 ? 1 : 4)],
          ['R de Clark-Evans', n5(d.clark_evans)],
          ['régimen', d.regimen]
        ]);
      };
      botones4(raiz, CLAVES.map((c, k) => ({ etiqueta: ETQ[k], valor: k })),
               k => { i = k; pinta(); }, 0);
      pinta();
      return [g];
    };

    // --- Módulo 4 · las dos propiedades de CSR -----------------------
    SIMULADORES['cap4-poisson'] = function (raiz) {
      const m = D4.m4;
      let vista = 'conteo';
      const ctx = raiz.querySelector('canvas').getContext('2d');
      const g = new Chart(ctx, {
        data: { labels: [], datasets: [] },
        options: { responsive: true, maintainAspectRatio: false,
          scales: { y: { beginAtZero: true, title: { display: true, text: 'realizaciones' } },
                    x: { title: { display: true, text: '' } } } }
      });
      const pinta = () => {
        if (vista === 'conteo') {
          g.data.labels = m.hist_k;
          g.data.datasets = [
            { type: 'bar', label: 'simulaciones', data: m.hist_obs, backgroundColor: C4.verde },
            { type: 'line', label: 'Poisson teórica', data: m.hist_teorico,
              borderColor: C4.naranja, borderDash: [6, 4], pointRadius: 0, tension: 0.3 }
          ];
          g.options.scales.x.title.text = 'puntos en la realización';
          lectura4(raiz, [
            ['realizaciones', miles4(m.n_realizaciones)],
            ['λ|W|', m.lambda],
            ['media del conteo', n5(m.conteo_media, 3)],
            ['varianza del conteo', n5(m.conteo_var, 3)],
            ['recorrido', m.conteo_min + ' – ' + m.conteo_max]
          ]);
        } else {
          g.data.labels = m.R_csr.hist_centros.map(c => n5(c, 3));
          g.data.datasets = [
            { type: 'bar', label: 'R de realizaciones de CSR PURO',
              data: m.R_csr.hist_conteo, backgroundColor: C4.morado }
          ];
          g.options.scales.x.title.text = 'índice de Clark-Evans';
          lectura4(raiz, [
            ['media de R', n5(m.R_csr.media)],
            ['recorrido', n5(m.R_csr.min, 3) + ' – ' + n5(m.R_csr.max, 3)],
            ['intervalo central 95 %', n5(m.R_csr.q025, 3) + ' – ' + n5(m.R_csr.q975, 3)],
            ['darían «agregado» leyendo R < 1', miles4(m.R_csr.bajo_1) + ' de ' + miles4(m.R_csr.n)]
          ]);
        }
        g.update();
      };
      botones4(raiz, [{ etiqueta: '(1) el número de puntos', valor: 'conteo' },
                      { etiqueta: '(2) cuánto se mueve R', valor: 'R' }],
               v => { vista = v; pinta(); });
      pinta();
      return [g];
    };

    // --- Módulo 6 · el barrido del cuadrante -------------------------
    SIMULADORES['cap4-barrido'] = function (raiz) {
      const CLAVES = ['redwood', 'japanesepines', 'bogota'];
      const ETQ = ['Secuoyas (agregado)', 'Pinos japoneses (aleatorio)', 'Sedes de Bogotá'];
      let i = 0;
      const ctx = raiz.querySelector('canvas').getContext('2d');
      const g = new Chart(ctx, {
        data: { labels: [], datasets: [] },
        options: { responsive: true, maintainAspectRatio: false,
          scales: { y: { type: 'logarithmic', title: { display: true, text: 'χ² (escala log)' } },
                    x: { title: { display: true, text: 'lado de la rejilla (nx)' } } } }
      });
      const pinta = () => {
        const b = D4.m6[CLAVES[i]];
        g.data.labels = b.nx;
        g.data.datasets = [{ type: 'bar', label: 'χ²', data: b.chi2,
          backgroundColor: b.rechaza.map(r => r ? C4.rojo : C4.gris) }];
        g.update();
        const rech = b.rechaza.reduce((a, v) => a + v, 0);
        const primeraBaja = b.nx[b.celdas_esperanza_baja.findIndex(v => v > 0)];
        lectura4(raiz, [
          ['patrón', ETQ[i]],
          ['tamaños barridos', b.nx.length],
          ['rechazan al 5 %', rech + ' de ' + b.nx.length],
          ['esperanza < 5 desde nx', primeraBaja == null ? '—' : primeraBaja],
          ['χ² con nx = 2', n5(b.chi2[0], 2)],
          ['χ² con nx = 20', n5(b.chi2[b.chi2.length - 1], 2)]
        ]);
      };
      botones4(raiz, CLAVES.map((c, k) => ({ etiqueta: ETQ[k], valor: k })),
               k => { i = k; pinta(); }, 0);
      pinta();
      return [g];
    };

    // --- Módulo 7 · G y F --------------------------------------------
    SIMULADORES['cap4-gf'] = function (raiz) {
      const CLAVES = ['cells', 'japanesepines', 'redwood', 'bogota'];
      const ETQ = ['Células', 'Pinos japoneses', 'Secuoyas', 'Sedes de Bogotá'];
      let i = 2;
      const ctx = raiz.querySelector('canvas').getContext('2d');
      const g = new Chart(ctx, {
        type: 'line', data: { datasets: [] },
        options: { responsive: true, maintainAspectRatio: false, parsing: false,
          scales: ejesXY('r', 'probabilidad') }
      });
      const pinta = () => {
        const d = D4.m7[CLAVES[i]];
        g.data.datasets = [
          { label: 'G observada', data: curva4(d.r_g, d.g_obs), borderColor: C4.verde,
            pointRadius: 0, tension: 0.2 },
          { label: 'G bajo CSR', data: curva4(d.r_g, d.g_teo), borderColor: C4.verde,
            borderDash: [5, 4], pointRadius: 0, tension: 0.2 },
          { label: 'F observada', data: curva4(d.r_f, d.f_obs), borderColor: C4.naranja,
            pointRadius: 0, tension: 0.2 },
          { label: 'F bajo CSR', data: curva4(d.r_f, d.f_teo), borderColor: C4.naranja,
            borderDash: [5, 4], pointRadius: 0, tension: 0.2 }
        ];
        g.update();
        lectura4(raiz, [
          ['patrón', d.nombre], ['n', miles4(d.n)],
          ['puntos coincidentes', d.coincidentes],
          ['G empírica en r = 0', n5(d.g_emp_en_cero, 6)],
          ['mediana de la distancia al vecino', n5(d.g_mediana, d.g_mediana > 10 ? 1 : 4)]
        ]);
      };
      botones4(raiz, CLAVES.map((c, k) => ({ etiqueta: ETQ[k], valor: k })),
               k => { i = k; pinta(); }, 2);
      pinta();
      return [g];
    };

    // --- Módulo 8 · K y L --------------------------------------------
    SIMULADORES['cap4-kl'] = function (raiz) {
      const CLAVES = ['cells', 'japanesepines', 'redwood', 'bogota'];
      const ETQ = ['Células', 'Pinos japoneses', 'Secuoyas', 'Sedes de Bogotá'];
      let i = 3, vista = 'L';
      const ctx = raiz.querySelector('canvas').getContext('2d');
      const g = new Chart(ctx, {
        type: 'line', data: { datasets: [] },
        options: { responsive: true, maintainAspectRatio: false, parsing: false,
          scales: ejesXY('r', '') }
      });
      const pinta = () => {
        const d = D4.m8[CLAVES[i]];
        if (vista === 'K') {
          g.data.datasets = [
            { label: 'K observada', data: curva4(d.r, d.k_obs), borderColor: C4.verde,
              pointRadius: 0, tension: 0.2 },
            { label: 'K bajo CSR (π r²)', data: curva4(d.r, d.k_teo), borderColor: C4.gris,
              borderDash: [5, 4], pointRadius: 0, tension: 0.2 }
          ];
          g.options.scales.y.title.text = 'K(r)';
        } else {
          g.data.datasets = [
            { label: 'L(r) − r', data: curva4(d.r, d.l_menos_r), borderColor: C4.naranja,
              pointRadius: 0, tension: 0.2 },
            { label: 'CSR', data: curva4(d.r, d.r.map(() => 0)), borderColor: C4.gris,
              borderDash: [5, 4], pointRadius: 0 }
          ];
          g.options.scales.y.title.text = 'L(r) − r';
        }
        g.update();
        lectura4(raiz, [
          ['patrón', d.nombre], ['corrección', d.correccion],
          ['máx |L − r|', n5(d.max_desvio, d.max_desvio > 10 ? 2 : 5)],
          ['a distancia r', n5(d.r_max_desvio, d.r_max_desvio > 10 ? 0 : 4)],
          ['lectura', d.l_menos_r[50] > 0 ? 'agregado' : 'regular']
        ]);
      };
      const cont = raiz.querySelector('.simulador-controles');
      botones4(raiz, CLAVES.map((c, k) => ({ etiqueta: ETQ[k], valor: k })),
               k => { i = k; pinta(); }, 3);
      const sep = document.createElement('span');
      sep.className = 'sim-sep';
      cont.appendChild(sep);
      [['Ver K', 'K'], ['Ver L − r', 'L']].forEach(([etq, v], j) => {
        const b = document.createElement('button');
        b.className = 'sim-btn' + (v === vista ? ' active' : '');
        b.textContent = etq;
        b.onclick = () => {
          cont.querySelectorAll('.sim-btn').forEach(x => {
            if (x.textContent.startsWith('Ver')) x.classList.remove('active');
          });
          b.classList.add('active');
          vista = v; pinta();
        };
        cont.appendChild(b);
      });
      pinta();
      return [g];
    };

    // --- Módulo 9 · K contra g ---------------------------------------
    SIMULADORES['cap4-kg'] = function (raiz) {
      const CLAVES = ['cells', 'japanesepines', 'redwood', 'bogota'];
      const ETQ = ['Células', 'Pinos japoneses', 'Secuoyas', 'Sedes de Bogotá'];
      let i = 2;
      const ctx = raiz.querySelector('canvas').getContext('2d');
      const g = new Chart(ctx, {
        type: 'line', data: { datasets: [] },
        options: { responsive: true, maintainAspectRatio: false, parsing: false,
          scales: {
            x: { type: 'linear', title: { display: true, text: 'r' } },
            y: { title: { display: true, text: 'g(r)' } },
            y2: { position: 'right', title: { display: true, text: 'K(r) / K teórica' },
                  grid: { drawOnChartArea: false } }
          } }
      });
      const pinta = () => {
        const gg = D4.m9[CLAVES[i]], kk = D4.m8[CLAVES[i]];
        const razon = kk.r.map((r, j) => kk.k_teo[j] > 0 ? kk.k_obs[j] / kk.k_teo[j] : null);
        g.data.datasets = [
          { label: 'g(r): mira solo el anillo', data: curva4(gg.r, gg.g_obs),
            borderColor: C4.morado, pointRadius: 0, tension: 0.2 },
          { label: 'g bajo CSR', data: curva4(gg.r, gg.g_teo), borderColor: C4.gris,
            borderDash: [5, 4], pointRadius: 0 },
          { label: 'K observada / K teórica: arrastra', yAxisID: 'y2',
            data: curva4(kk.r, razon), borderColor: C4.verde, pointRadius: 0, tension: 0.2 }
        ];
        g.update();
        lectura4(raiz, [
          ['patrón', gg.nombre],
          ['g máxima', n5(gg.g_max, 3)],
          ['a distancia r', n5(gg.r_g_max, gg.r_g_max > 10 ? 0 : 4)],
          ['g vuelve a 1 pasada r', n5(gg.r_ultimo_cruce, gg.r_ultimo_cruce > 10 ? 0 : 4)],
          ['máx |L − r| de K', n5(kk.max_desvio, kk.max_desvio > 10 ? 2 : 5)]
        ]);
      };
      botones4(raiz, CLAVES.map((c, k) => ({ etiqueta: ETQ[k], valor: k })),
               k => { i = k; pinta(); }, 2);
      pinta();
      return [g];
    };

    // --- Módulo 10 · las correcciones de borde -----------------------
    SIMULADORES['cap4-bordes'] = function (raiz) {
      const m = D4.m10;
      const COL = { none: C4.rojo, border: C4.gris, translate: C4.verde, isotropic: C4.azul };
      const ETQ = { none: 'sin corregir', border: 'de borde', translate: 'de traslación',
                    isotropic: 'isotrópica' };
      const activos = { none: true, border: false, translate: true, isotropic: false };
      const ctx = raiz.querySelector('canvas').getContext('2d');
      const g = new Chart(ctx, {
        type: 'line', data: { datasets: [] },
        options: { responsive: true, maintainAspectRatio: false, parsing: false,
          scales: ejesXY('r (metros)', 'K(r)') }
      });
      const pinta = () => {
        g.data.datasets = m.correcciones.filter(c => activos[c.correccion]).map(c => ({
          label: 'K, ' + ETQ[c.correccion], data: curva4(m.r, c.k),
          borderColor: COL[c.correccion], pointRadius: 0, tension: 0.2
        }));
        g.data.datasets.push({ label: 'K bajo CSR', data: curva4(m.r, m.k_teo),
          borderColor: C4.gris, borderDash: [5, 4], pointRadius: 0 });
        g.update();
        const iso = m.correcciones.find(c => c.correccion === 'isotropic');
        const tra = m.correcciones.find(c => c.correccion === 'translate');
        lectura4(raiz, [
          ['sesgo máximo sin corregir', n5(m.sesgo_max_pct, 2) + ' %'],
          ['a distancia r', n5(m.r_sesgo_max, 0) + ' m'],
          ['piezas de la ventana', m.ventana.piezas],
          ['vértices', miles4(m.ventana.vertices)],
          ['isotrópica / traslación', '×' + n5(m.coste.veces_isotropica_sobre_traslacion, 0)],
          ['envolvente isotrópica', n5(m.coste.horas_envolvente_isotropica, 1) + ' h']
        ]);
      };
      const cont = raiz.querySelector('.simulador-controles');
      cont.innerHTML = '';
      Object.keys(ETQ).forEach(k => {
        const b = document.createElement('button');
        b.className = 'sim-btn' + (activos[k] ? ' active' : '');
        b.textContent = ETQ[k];
        b.onclick = () => {
          activos[k] = !activos[k];
          b.classList.toggle('active', activos[k]);
          pinta();
        };
        cont.appendChild(b);
      });
      pinta();
      return [g];
    };

    // --- Módulo 11 · la envolvente -----------------------------------
    SIMULADORES['cap4-envolvente'] = function (raiz) {
      const CLAVES = ['japanesepines', 'redwood', 'bogota'];
      const ETQ = ['Pinos japoneses', 'Secuoyas', 'Sedes de Bogotá'];
      let i = 0;
      const ctx = raiz.querySelector('canvas').getContext('2d');
      const g = new Chart(ctx, {
        type: 'line', data: { datasets: [] },
        options: { responsive: true, maintainAspectRatio: false, parsing: false,
          scales: ejesXY('r', 'K(r)') }
      });
      const pinta = () => {
        const e = D4.m11[CLAVES[i]];
        g.data.datasets = [
          { label: 'techo de la banda', data: curva4(e.r, e.hi), borderColor: C4.gris,
            pointRadius: 0, fill: '+1', backgroundColor: 'rgba(138,138,138,0.18)' },
          { label: 'suelo de la banda', data: curva4(e.r, e.lo), borderColor: C4.gris,
            pointRadius: 0 },
          { label: 'K observada', data: curva4(e.r, e.obs), borderColor: C4.verde,
            borderWidth: 3, pointRadius: 0, tension: 0.2 },
          { label: 'K bajo CSR', data: curva4(e.r, e.teo), borderColor: C4.naranja,
            borderDash: [5, 4], pointRadius: 0 }
        ];
        g.update();
        const ts = D4.m11.tasa_salida_bogota;
        lectura4(raiz, [
          ['patrón', e.nombre],
          ['simulaciones', miles4(e.nsim)],
          ['corrección', e.correccion],
          ['¿se sale la observada?', e.sale ? 'sí' : 'no'],
          ['p mínimo posible', n5(D4.m11.p_minimo)],
          ['simulaciones de CSR que se salen', n5(ts.pct, 1) + ' %']
        ]);
      };
      botones4(raiz, CLAVES.map((c, k) => ({ etiqueta: ETQ[k], valor: k })),
               k => { i = k; pinta(); }, 0);
      pinta();
      return [g];
    };

    // --- Módulo 11 · cuántas simulaciones ----------------------------
    SIMULADORES['cap4-nsim'] = function (raiz) {
      const esc = D4.m11.escala_nsim;
      const ctx = raiz.querySelector('canvas').getContext('2d');
      const g = new Chart(ctx, {
        data: {
          labels: esc.map(z => 'nsim = ' + z.nsim),
          datasets: [
            { type: 'bar', label: 'banda por defecto (nrank = 1)',
              data: esc.map(z => z.ancho_defecto), backgroundColor: C4.rojo },
            { type: 'bar', label: 'banda a nivel fijo del 5 %',
              data: esc.map(z => z.ancho_5pct), backgroundColor: C4.verde }
          ]
        },
        options: { responsive: true, maintainAspectRatio: false,
          scales: { y: { beginAtZero: true, title: { display: true, text: 'ancho medio de la banda' } } } }
      });
      let i = 0;
      const pinta = () => {
        const z = esc[i];
        lectura4(raiz, [
          ['nsim', z.nsim],
          ['nivel de la banda por defecto', n5(z.nivel_defecto, 4)],
          ['nrank para el 5 %', n5(z.nrank_para_5pct, 2)],
          ['¿alcanza el 5 %?', z.alcanza_5pct ? 'sí' : 'no'],
          ['p mínimo', n5(z.p_minimo)],
          ['por defecto se ensancha', '×' + n5(D4.m11.escala_resumen.veces_defecto, 2)]
        ]);
      };
      botones4(raiz, esc.map((z, k) => ({ etiqueta: 'nsim = ' + z.nsim, valor: k })),
               k => { i = k; pinta(); }, 0);
      pinta();
      return [g];
    };
"""


# =====================================================================
# Las doce preguntas: cuatro en el módulo 6 y ocho en el 12
#
# Los cuatro tipos que el motor conoce son 'opcion', 'multiple',
# 'numerica' y 'grafico'. Inventarse un tipo tumba media página (A.12).
# Ninguna respuesta lleva cifras escritas: salen de D4.
# =====================================================================
QUIZ_JS = r"""
    AUTOEVALUACIONES['cap4-trampas'] = [
      {
        tipo: 'opcion',
        pregunta: 'Un informe dice «en Bogotá hay 5,7 colegios por km²». ¿Qué le falta para ser una afirmación completa?',
        opciones: [
          { texto: 'Decir cuál es la ventana de observación', correcta: true,
            respuesta: 'Eso es. Con el perímetro urbano salen ' + n5(D4.m1.urbana.lambda_km2, 4) + ' sedes/km²; con el Distrito Capital entero, ' + n5(D4.m1.dc.lambda_km2, 4) + '. La misma ciudad y el mismo dato, con un factor de ' + n5(D4.m1.factor_lambda, 2) + ' entre las dos.' },
          { texto: 'Nada: la intensidad es una propiedad del dato',
            respuesta: 'No lo es. La intensidad es n dividido por el área de la ventana, y la ventana la elige quien analiza.' },
          { texto: 'Decir cuántos colegios hay en total',
            respuesta: 'Ayuda, pero no arregla el problema: el número de sedes apenas cambia entre las dos ventanas — sube un ' + n5(D4.m1.aumento_n_pct, 1) + ' % — y la intensidad se cuadruplica.' },
          { texto: 'Usar hectáreas en vez de km²',
            respuesta: 'La unidad no cambia el problema: la misma cifra en hectáreas es ' + n5(D4.m2.lambda_urbana_ha, 4) + ', y sigue dependiendo de qué ventana se usó.' }
        ] },
      {
        tipo: 'opcion',
        pregunta: 'Dos patrones tienen exactamente el mismo χ² en el test de cuadrantes. ¿Qué se puede concluir?',
        opciones: [
          { texto: 'Nada sobre su estructura a escala menor que la celda', correcta: true,
            respuesta: 'Correcto, y el módulo 5 lo construye a propósito: los dos patrones dan χ² = ' + n5(D4.m5.original.chi2, 4) + ' y su distancia media al vecino se multiplica por ' + n5(D4.m5.nn_cociente, 2) + '.' },
          { texto: 'Que son el mismo patrón',
            respuesta: 'No. El χ² solo usa cuántos puntos hay en cada celda, así que dos repartos idénticos por celda le dan el mismo número aunque los puntos estén colocados de forma opuesta.' },
          { texto: 'Que los dos son aleatorios',
            respuesta: 'Tampoco: el χ² del módulo 5 rechaza en los dos casos. Lo que no distingue es la estructura DENTRO de cada celda.' },
          { texto: 'Que tienen la misma intensidad',
            respuesta: 'Eso sí es cierto si comparten ventana y n, pero es mucho menos de lo que la pregunta pide.' }
        ] },
      {
        tipo: 'multiple',
        pregunta: 'El test de cuadrantes sobre las sedes de Bogotá con una rejilla 10×10 rechaza con un p-valor minúsculo. ¿Qué afirmaciones son correctas?',
        opciones: [
          { texto: 'La intensidad no es constante en la ventana', correcta: true,
            respuesta: 'Sí: el índice de dispersión vale ' + n5(D4.m2.urbana.dispersion, 2) + ' y bajo Poisson valdría 1.' },
          { texto: 'Parte de las celdas tienen esperanza menor que 5, así que la aproximación χ² es discutible', correcta: true,
            respuesta: 'Cierto: son ' + D4.m2.urbana.celdas_esperanza_baja + ' de ' + D4.m2.urbana.celdas + ' celdas vivas, porque la ventana las recorta.' },
          { texto: 'Los colegios se atraen entre sí',
            respuesta: 'El test de cuadrantes no puede decir eso: solo mira conteos por celda, no relaciones entre puntos.' },
          { texto: 'Con otra rejilla el veredicto sería el mismo',
            respuesta: 'No está garantizado. Sobre las secuoyas, el barrido del módulo 6 rechaza en ' + D4.m6.redwood_rechazos + ' de ' + D4.m6.nxs.length + ' tamaños; el más grueso no rechaza.' }
        ] },
      {
        tipo: 'numerica',
        pregunta: 'Con 999 simulaciones, ¿cuál es el p-valor más pequeño que una envolvente puede dar?',
        respuesta: D4.m11.p_minimo, tolerancia: 0.0002,
        explicacion: 'Es 1/(nsim+1) = ' + n5(D4.m11.p_minimo) + '. No es una convención ni un redondeo: con 999 simulaciones no existe un p menor, por bien que se separe la curva observada.'
      }
    ];

    AUTOEVALUACIONES['cap4-quiz'] = [
      {
        tipo: 'opcion',
        pregunta: '¿Cuáles son las DOS propiedades que definen la aleatoriedad espacial completa (CSR)?',
        opciones: [
          { texto: 'El número de puntos en una región es Poisson, y dado ese número las posiciones son uniformes e independientes', correcta: true,
            respuesta: 'Eso es, y la primera es la que se olvida. Por eso dos realizaciones del mismo proceso no tienen el mismo n: en ' + miles4(D4.m4.n_realizaciones) + ' simulaciones el conteo va de ' + D4.m4.conteo_min + ' a ' + D4.m4.conteo_max + '.' },
          { texto: 'Las posiciones son uniformes y el número de puntos es fijo',
            respuesta: 'La segunda mitad es falsa: si n fuera fijo no habría variabilidad de conteos, y la varianza observada es ' + n5(D4.m4.conteo_var, 2) + ', prácticamente igual a la media.' },
          { texto: 'Los puntos están equiespaciados y no se tocan',
            respuesta: 'Eso describe un patrón REGULAR, que es lo contrario de aleatorio. Las células tienen R = ' + n5(D4.m3.cells.clark_evans, 4) + '.' },
          { texto: 'La intensidad es constante y los puntos se atraen débilmente',
            respuesta: 'La atracción, aunque sea débil, ya no es CSR: sería un proceso de conglomerado.' }
        ] },
      {
        tipo: 'opcion',
        pregunta: 'Una realización de CSR PURO da un índice de Clark-Evans de 0,90. ¿Qué se concluye?',
        opciones: [
          { texto: 'Nada, porque el azar solo ya produce ese valor con frecuencia', correcta: true,
            respuesta: 'Exacto. Sobre ' + miles4(D4.m4.R_csr.n) + ' realizaciones de azar puro, R recorrió de ' + n5(D4.m4.R_csr.min, 3) + ' a ' + n5(D4.m4.R_csr.max, 3) + ', y ' + miles4(D4.m4.R_csr.bajo_1) + ' de ellas quedaron por debajo de 1.' },
          { texto: 'Que el patrón está agregado',
            respuesta: 'Ese es justo el error que el módulo 4 desmonta: comparar una R contra 1 sin saber cuánto se mueve el azar.' },
          { texto: 'Que hay un error en la simulación',
            respuesta: 'No: el intervalo central del 95 % de R bajo CSR va de ' + n5(D4.m4.R_csr.q025, 3) + ' a ' + n5(D4.m4.R_csr.q975, 3) + ', y 0,90 cae dentro.' },
          { texto: 'Que la ventana es demasiado pequeña',
            respuesta: 'El tamaño de la ventana influye en la precisión, pero el valor observado es perfectamente compatible con CSR.' }
        ] },
      {
        tipo: 'opcion',
        pregunta: '¿Qué distingue a la función G de la función F?',
        opciones: [
          { texto: 'G mide desde los puntos del patrón; F, desde sitios cualesquiera de la ventana', correcta: true,
            respuesta: 'Eso es. Por eso separan los regímenes en direcciones opuestas: un patrón agregado tiene vecinos cerca (G sube pronto) y deja huecos grandes (F sube tarde).' },
          { texto: 'G usa distancias y F usa conteos',
            respuesta: 'Las dos usan distancias. Lo que cambia es desde dónde se miden.' },
          { texto: 'G corrige el efecto de borde y F no',
            respuesta: 'Las dos admiten corrección de borde; ninguna la lleva incorporada por definición.' },
          { texto: 'G vale para patrones agregados y F para regulares',
            respuesta: 'Las dos valen para cualquier patrón: son descripciones, no tests específicos de un régimen.' }
        ] },
      {
        tipo: 'numerica',
        pregunta: 'La G empírica de las sedes de Bogotá vale 0,037494 en r = 0. ¿Cuántas sedes comparten coordenada exacta con otra?',
        respuesta: D4.m7.bogota.coincidentes, tolerancia: 0.5,
        explicacion: 'Son ' + D4.m7.bogota.coincidentes + ' sedes, el ' + n5(D4.m7.bogota.coincidentes_pct, 2) + ' % del patrón, con hasta ' + D4.m7.duplicados.maximo_por_sitio + ' en un mismo punto: sedes distintas en el mismo edificio. Un patrón con duplicados no es un proceso puntual simple, y el salto de G en r = 0 es exactamente esa fracción.'
      },
      {
        tipo: 'opcion',
        pregunta: 'K(r) de un patrón sigue por encima de su valor teórico a 500 m, aunque la agregación real ocurre a 20 m. ¿Por qué?',
        opciones: [
          { texto: 'Porque K es acumulativa y arrastra los vecinos ya contados', correcta: true,
            respuesta: 'Eso es, y es lo que g(r) arregla mirando solo el anillo de radio r. Sobre las secuoyas, g alcanza ' + n5(D4.m9.redwood.g_max, 2) + ' en r = ' + n5(D4.m9.redwood.r_g_max, 4) + ' y vuelve a 1 mucho antes de que K se despegue.' },
          { texto: 'Porque el efecto de borde infla K a distancias grandes',
            respuesta: 'El efecto de borde va en el sentido contrario: sin corregir, K se queda por DEBAJO, hasta un ' + n5(D4.m10.sesgo_max_pct, 1) + ' % en este capítulo.' },
          { texto: 'Porque la corrección de traslación falla a r grande',
            respuesta: 'No: el arrastre es una propiedad de la definición de K, no un defecto de la corrección.' },
          { texto: 'Porque la ventana no es rectangular',
            respuesta: 'El arrastre ocurre igual en una ventana rectangular. Es acumulación, no geometría.' }
        ] },
      {
        tipo: 'multiple',
        pregunta: 'Sobre el efecto de borde, ¿qué es cierto?',
        opciones: [
          { texto: 'Sin corregir, K queda por debajo de su valor real', correcta: true,
            respuesta: 'Siempre, y por eso el sesgo tiene dirección: un punto del borde tiene vecinos fuera que nadie observó. Aquí llega al ' + n5(D4.m10.sesgo_max_pct, 1) + ' %.' },
          { texto: 'Ignorarlo hace que el patrón parezca más regular de lo que es', correcta: true,
            respuesta: 'Correcto: faltan vecinos, nunca sobran, así que el patrón parece menos agregado.' },
          { texto: 'La corrección isotrópica y la de traslación cuestan lo mismo',
            respuesta: 'No sobre una ventana real: aquí la isotrópica cuesta ×' + n5(D4.m10.coste.veces_isotropica_sobre_traslacion, 0) + ' lo que la de traslación, porque recorre el perímetro pareja a pareja.' },
          { texto: 'El sesgo crece con r', correcta: true,
            respuesta: 'Sí: a r grande casi todos los discos tocan el borde. El máximo se alcanza en r = ' + n5(D4.m10.r_sesgo_max, 0) + ' m.' }
        ] },
      {
        tipo: 'opcion',
        pregunta: 'La curva observada se sale de la banda del 95 % en un tramo corto de r. ¿Qué se puede afirmar?',
        opciones: [
          { texto: 'Poco: la banda es puntual y mirarla entera son muchos contrastes a la vez', correcta: true,
            respuesta: 'Eso es. De las ' + miles4(D4.m11.tasa_salida_bogota.nsim) + ' simulaciones de CSR puro con que se construyó la banda, el ' + n5(D4.m11.tasa_salida_bogota.pct, 1) + ' % se sale de ella en algún r. Para la curva entera hace falta un test global.' },
          { texto: 'Que el patrón no es CSR, con p < 0,05',
            respuesta: 'Ese es exactamente el error que el módulo 11 desmonta: el 5 % es el nivel de CADA r por separado, no el de la curva.' },
          { texto: 'Que hay que aumentar nsim hasta que deje de salirse',
            respuesta: 'Peor todavía: subir nsim con la banda por defecto la ENSANCHA, porque su nivel es 2/(nsim+1) y cambia con nsim.' },
          { texto: 'Que la corrección de borde es insuficiente',
            respuesta: 'No hay nada en el enunciado que apunte al borde; y la banda se construye con la misma corrección que la curva.' }
        ] },
      {
        tipo: 'opcion',
        pregunta: 'Se pasa de 39 a 999 simulaciones sin tocar nada más. ¿Qué le ocurre a la banda por defecto de envelope()?',
        opciones: [
          { texto: 'Se ensancha, porque su nivel puntual es 2/(nsim+1) y ha cambiado', correcta: true,
            respuesta: 'Eso es, y es contraintuitivo: la banda por defecto es el mínimo-máximo de las simulaciones. A lo largo del barrido se ensancha ×' + n5(D4.m11.escala_resumen.veces_defecto, 2) + '. Manteniendo el nivel fijo al 5 %, en cambio, se estrecha.' },
          { texto: 'Se estrecha, porque hay más información',
            respuesta: 'Es lo que uno espera y no es lo que pasa: con nrank = 1 el nivel pasa de ' + n5(D4.m11.escala_nsim[1].nivel_defecto, 3) + ' a ' + n5(D4.m11.escala_nsim[3].nivel_defecto, 3) + ', o sea que son contrastes distintos.' },
          { texto: 'No cambia: la banda solo depende del patrón',
            respuesta: 'Depende de las simulaciones, y por tanto de cuántas haya.' },
          { texto: 'Se estrecha exactamente a la mitad',
            respuesta: 'Ni se estrecha ni hay una regla tan simple.' }
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
        sys.exit(f"PARADO: la región de {que} tiene {nl} líneas y el mínimo es {min_lineas}; "
                 "el ancla de cierre casó demasiado pronto")
    return texto[:i] + nuevo + texto[j + len(cierra):]


def sustituye(texto, ancla, nuevo, que):
    if texto.count(ancla) != 1:
        sys.exit(f"PARADO: el ancla de {que} aparece {texto.count(ancla)} veces")
    return texto.replace(ancla, nuevo)


def main() -> int:
    doc = PLANTILLA.read_text(encoding="utf-8")
    print(f"\n=== ensambla_cap4.py ===\nplantilla: {len(doc)/1024:.0f} KB\n")

    doc = sustituye(doc, "<title>Plantilla de capítulo — Estadística Espacial</title>",
                    "<title>Capítulo 4 · Patrones puntuales — "
                    "Estadística Espacial</title>", "título")
    doc = sustituye(doc, "PLANTILLA BASE •\n              5 MÓDULOS DE DEMOSTRACIÓN • UNBOSQUE 2026-II",
                    "CAPÍTULO 4 • PATRONES PUNTUALES: CSR Y FUNCIONES DE RESUMEN •\n"
                    f"              SEMANAS {D['meta']['semanas']} • UNBOSQUE 2026-II",
                    "subtítulo de la cabecera")
    doc = sustituye(doc, "Estadística Espacial (20929) • Plantilla de\n          capítulo • UnBosque 2026-II",
                    "Estadística Espacial (20929) • Capítulo 4 de 10 •\n"
                    f"          Semanas {D['meta']['semanas']} • UnBosque 2026-II", "pie")

    doc = reemplaza_region(doc, "    const courseData = {", "\n    };\n", COURSE_DATA,
                           "courseData + DATOS_CAP4", max_lineas=20)

    doc = reemplaza_region(
        doc,
        "  <!-- ============================================================ -->\n"
        "  <!-- MÓDULO 1 · Cajas y tipografía",
        "\n  <script>", MODULOS.lstrip("\n") + "\n  <script>",
        "los doce módulos", max_lineas=600)

    vieja = [l for l in doc.splitlines() if l.startswith("    GEOMAPAS['demo-mapa'] =")]
    if len(vieja) != 1:
        sys.exit(f"PARADO: {len(vieja)} registros de GEOMAPAS['demo-mapa'], se esperaba 1")
    doc = sustituye(doc, vieja[0], GEOMAPAS_JS.rstrip("\n"), "los siete .geomapa")

    # El glosario de notación es del capítulo 1; aquí se retira sin sustituto.
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
                           QUIZ_JS, "AUTOEVALUACIONES", max_lineas=90)

    DESTINO.parent.mkdir(parents=True, exist_ok=True)
    DESTINO.write_text(doc, encoding="utf-8")

    # --- El recuento, contado y no recordado --------------------------
    marcado = doc[:doc.rindex("\n  <script>")]
    mods = doc.count('<template id="module-')
    sims = marcado.count('data-simulador="')
    mapas = marcado.count('data-geomapa="cap4-')
    bl_r = doc.count('class="language-r"')
    bl_py = doc.count('class="language-python"')
    cifras = doc.count("#&gt;")
    lienzos = marcado.count("<canvas")
    con_alt = sum(1 for c in marcado.split("<canvas")[1:] if "aria-label" in c.split(">")[0])
    ejercicios = marcado.count('class="ejercicio-guiado"')
    quices = marcado.count('data-quiz="')
    kb = DESTINO.stat().st_size / 1024

    print(f"{DESTINO.relative_to(RAIZ)}  {kb:.0f} KB")
    print(f"  {mods} módulos · {sims} simuladores · {mapas} mapas · "
          f"{bl_r} bloques de R y {bl_py} de Python · {cifras} cifras anunciadas")
    print(f"  {lienzos} lienzos, {con_alt} con aria-label · "
          f"{ejercicios} ejercicios guiados · {quices} autoevaluaciones")

    problemas = []
    if mods != 12:
        problemas.append(f"módulos: {mods} (se esperan 12)")
    if ejercicios != 5:
        problemas.append(f"ejercicios: {ejercicios} (la desviación declarada son 5)")
    if quices != 2:
        problemas.append(f"autoevaluaciones: {quices} (se esperan 2: trampas y quiz)")
    if bl_r != bl_py:
        problemas.append(f"R y Python descuadrados: {bl_r} y {bl_py}")
    if lienzos != con_alt:
        problemas.append(f"lienzos sin aria-label: {lienzos - con_alt}")
    if problemas:
        print("\n  PROBLEMAS:")
        for p in problemas:
            print(f"   - {p}")
        return 1
    print("\n  Capítulo 4 ensamblado.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
