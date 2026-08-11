#!/usr/bin/env python3
"""
ensambla_cap2.py — construye el capítulo 2 del material (T2.2b)

Material de Estadística Espacial 2026-II (20929).
«SIG, sistemas de referencia y georreferenciación con sf» · semanas 2-3

MISMO REPARTO QUE EL CAPÍTULO 1, y es deliberado (Checkpoint 1: el
capítulo 1 es el molde):

  · La **prosa** vive en f-strings y se interpola aquí desde el JSON. Es
    lo que audita `audita_texto_cap2.py`.
  · El **JavaScript** NO se interpola: recibe el JSON entero como
    `DATOS_CAP2` y saca de ahí sus cifras con `n5()`. Así una pregunta
    del quiz no puede quedarse con un número viejo, porque no tiene
    ninguno escrito.
  · Los **mapas** se registran con su JSON LITERAL, no con una función:
    `audita_texto_base.geomapas()` solo puede comprobar los cortes, el n
    y el peso de un mapa cuya fuente sea un objeto.

LAS DOS DESVIACIONES DEL MOLDE, decididas por Javier el 2026-08-04 y
declaradas aquí porque el Checkpoint 1 exige declararlas:

  1. **12 preguntas en vez de 8.** El quiz de 8 del módulo 12 más un
     bloque de 4 «trampas de CRS» a mitad de capítulo, después del
     módulo 6. Motivo: este capítulo cubre DOS semanas de clase y sus
     errores son los que de verdad se cometen en la práctica.
  2. **5 ejercicios guiados en vez de 4.**

Y LA REGLA DEL RITMO (§9.1 del plan), que aquí rige entera: ningún módulo
abre pidiendo trabajo · todo componente interactivo va con dos párrafos,
el que lo motiva y **el que lo cierra** · el encabezado del módulo es un
contrato. Esa regla no la caza ninguna comprobación automática.

Uso:  python3 precalculo/ensambla_cap2.py
      (desde la carpeta `Estadistica espacial/`)
"""
from __future__ import annotations

import json
import re
import pathlib
import sys

RAIZ = pathlib.Path(__file__).resolve().parent.parent
PLANTILLA = RAIZ / "plantilla" / "plantilla-capitulo.html"
SALIDAS = RAIZ / "precalculo" / "salidas"
DESTINO = RAIZ / "Htmls_Espacial" / "capitulo-2-crs-georreferenciacion.html"

D = json.loads((SALIDAS / "cap2_datos.json").read_text(encoding="utf-8"))
M = json.loads((SALIDAS / "cap2_mapas.json").read_text(encoding="utf-8"))
S = json.loads((SALIDAS / "cap2_soluciones.json").read_text(encoding="utf-8"))

el, gr, pr = D["elipsoide"], D["grados"], D["proyecciones"]
ep, et, md = D["epsg"], D["etiquetar"], D["medir"]
fo, cs, po = D["formatos"], D["csv_sf"], D["posicional"]
tp, ig = D["topologia"], D["ingenieria"]
PT = pr["tabla"]


def n(x, d=5):
    """Cinco decimales por defecto: la regla de publicación de T0.5."""
    return f"{float(x):.{d}f}"


def ent(x):
    """Entero con espacio fino U+202F. NO usar dentro de KaTeX."""
    return f"{int(round(float(x))):,}".replace(",", "\u202f")


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

    El envoltorio es `.grafico-wrapper` CON ALTURA EXPLÍCITA, que es el
    contrato de la plantilla. La primera versión de esto inventó una
    clase `.simulador-lienzo` que no existe en el CSS: el canvas medía
    cero de alto, Chart.js creaba el gráfico sin quejarse y los diez
    simuladores salían en blanco. Consola limpia, cero errores, cero
    píxeles — solo se ve midiendo la tinta del lienzo, que es para lo que
    existe el recorrido instrumentado de T*n*.3.
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
    """Una fila de tabla, con la primera celda como encabezado.

    Existe para poder construir las tablas FUERA de los f-strings de la
    prosa: en Python 3.10 la parte de expresión de un f-string no admite
    una contrabarra, así que un `\\"` dentro del `{...}` es un
    SyntaxError. Sacarlo aquí también deja la prosa legible.
    """
    cab, resto = celdas[0], celdas[1:]
    return ('            <tr><th scope="row">' + str(cab) + '</th>'
            + ''.join('<td>' + str(c) + '</td>' for c in resto) + '</tr>\n')


def quiz_html(ident, titulo, bajada):
    """El marcado que el motor de autoevaluaciones espera, entero.

    Un `<div class="quiz-container">` a secas no basta: `renderAutoevaluacion`
    busca `.quiz-preguntas`, `.quiz-resumen`, `.quiz-progreso-barra` y
    `.quiz-conteo`, y si falta el primero revienta con un TypeError que
    tumba `iniciarAutoevaluaciones()` — y con él todo lo que `loadModule()`
    llama después, que es exactamente el defecto nº 2 de A.12.
    """
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
        <div class="geomapa-controles"></div>
        <div class="geomapa-pie-caja"></div>
      </div>
"""


# =====================================================================
# MÓDULO 1 · La Tierra no es plana ni una esfera
# =====================================================================
# Regla del ritmo, primera: el módulo NO abre pidiendo trabajo. Abre
# situando, y el primer componente llega cuando ya hay algo que mirar.
_dt = el["datum"]
MOD1 = cabecera(
    1, "La Tierra no es plana ni una esfera", "Geoid, ellipsoid, datum",
    "Distinguir geoide, elipsoide y datum, y medir qué cuesta confundirlos."
) + f"""
      <p>Todo lo que este curso va a hacer —contar puntos, comparar áreas, ajustar un
      variograma— empieza por una pregunta que parece de otra asignatura: <em>¿sobre qué
      superficie estamos midiendo?</em> La respuesta corta es que sobre ninguna sola. La Tierra
      tiene una forma física irregular, el <strong>geoide</strong>, que se aproxima con una
      superficie matemática manejable, el <strong>elipsoide</strong>, y esa aproximación hay
      que anclarla al terreno con un <strong>datum</strong>. Tres cosas distintas que en el
      lenguaje corriente se llaman «el sistema de coordenadas».</p>

      <p>La idea que sostiene el capítulo entero es esta: <strong>un sistema de referencia mal
      puesto no da error, da un resultado equivocado con buena cara</strong>. No hay excepción
      ni mensaje de aviso. Por eso los once módulos que siguen no discuten cuál es el sistema
      correcto en abstracto: <em>miden</em> lo que cuesta cada equivocación concreta.</p>

      <div class="definition">
        <h3>El elipsoide WGS84, en números</h3>
        <p>El elipsoide de referencia del GPS y de casi todo dato global es un elipsoide de
        revolución achatado por los polos. Sus dos parámetros están <em>definidos</em>, no
        medidos: el semieje mayor vale exactamente {firma(ent(el['a']), ' m')} y el
        aplanamiento inverso, exactamente {firma(n(el['aplanamiento_inv'], 9))}. De ahí sale
        todo lo demás: el semieje menor, {firma(n(el['b'], 4), ' m')}, y con él un
        abultamiento ecuatorial de {firma(n(el['a_menos_b'], 4), ' m')} — algo más de
        veintiún kilómetros de diferencia entre el radio del ecuador y el del polo.</p>
      </div>

      <p>Ese achatamiento no es un adorno: cambia el tamaño de las cosas según dónde estén. La
      curvatura del elipsoide se describe con dos radios que no coinciden —el del meridiano,
      \\(M\\), y el del primer vertical, \\(N\\)— y su cociente mide cuánto se aparta la
      superficie de una esfera en cada latitud. El simulador siguiente los recorre: fíjate en
      que en el ecuador \\(N\\) supera a \\(M\\) en más de treinta kilómetros y que la
      diferencia se cierra según se sube hacia el polo.</p>

      <p>\\( M(\\varphi) = \\dfrac{{a\\,(1-e^2)}}{{(1-e^2\\sin^2\\varphi)^{{3/2}}}}
      \\qquad N(\\varphi) = \\dfrac{{a}}{{(1-e^2\\sin^2\\varphi)^{{1/2}}}} \\)</p>

{sim('radios', 'Los dos radios de curvatura del elipsoide, por latitud',
     'Con la primera excentricidad al cuadrado e² = ' + n(el['e2'], 8) + '.')}
      <p>Lo que el simulador enseña es que la Tierra no tiene «un radio». En cuanto una
      fórmula pide uno —y la geodesia esférica lo pide todo el rato— hay que decir cuál, y esa
      elección se paga. El módulo 6 pondrá cifra a ese pago sobre el área de Colombia; aquí
      basta con una distancia larga.</p>

      <div class="warning-box">
        <h3>La esfera contra el elipsoide, sobre {el['esfera_vs_elipsoide']['origen']}–{el['esfera_vs_elipsoide']['destino']}</h3>
        <p>La geodésica sobre el elipsoide mide
        {firma(ent(el['esfera_vs_elipsoide']['d_elipsoide_m']), ' m')} y la de la esfera que
        usa <code>s2</code>, {firma(ent(el['esfera_vs_elipsoide']['d_esfera_m']), ' m')}. La
        diferencia es de {firma(n(el['esfera_vs_elipsoide']['dif_m'], 3), ' m')}, un
        {firma(n(el['esfera_vs_elipsoide']['dif_pct']) + ' %')} del total. Sobre nueve mil
        kilómetros es poco; en el módulo 6 verás que sobre un área no lo es.</p>
      </div>

      <p>Falta la tercera pieza, y es la que más silencio hace. El <strong>datum</strong> es lo
      que ata el elipsoide al terreno: dice dónde está su centro y cómo está orientado.
      Cambiar de datum sin cambiar las cifras de latitud y longitud no produce ningún error
      —las cifras siguen siendo latitudes y longitudes válidas— pero señala otro punto del
      suelo. Colombia usó durante décadas el datum <em>Bogotá 1975</em> (EPSG&nbsp;{_dt['destino_epsg']}),
      cuyo desplazamiento respecto de WGS84 está publicado como
      ({', '.join(str(int(v)) for v in _dt['towgs84'])})&nbsp;m.</p>

      <div class="tabla-caja">
        <table>
          <caption>Cuánto se mueve un punto si sus coordenadas de {_dt['destino_nombre']} se
            leen como si fueran WGS84.</caption>
          <thead><tr><th scope="col">Ciudad</th><th scope="col">Desplazamiento (m)</th></tr></thead>
          <tbody>
{''.join(f'            <tr><th scope="row">{c}</th><td>{n(v, 2)}</td></tr>' + chr(10) for c, v in zip(_dt['ciudad'], _dt['desplazamiento_m']))}          </tbody>
        </table>
      </div>

      <p>Entre {firma(n(_dt['desp_min_m'], 2), ' m')} y {firma(n(_dt['desp_max_m'], 2), ' m')},
      con una media de {firma(n(_dt['desp_medio_m'], 2), ' m')}. Medio kilómetro de error
      sistemático, sin un solo mensaje en consola. Un mapa cartográfico antiguo de Colombia
      superpuesto sobre una capa de GPS sin reproyectar se descoloca exactamente eso.</p>

{tabs('El elipsoide desde el código',
      '''library(sf)
source("precalculo/fuentes.R")     # carga_municipios() y las rutas del curso
cr &lt;- st_crs(4326)
round(as.numeric(cr$SemiMajor), 1)
#&gt; [1] ''' + ent(el['a']).replace(chr(0x202f), '') + '''

# El datum viejo: mismas cifras, otro punto del suelo
p &lt;- st_sfc(st_point(c(-74.0721, 4.7110)), crs = 4326)
q &lt;- st_transform(p, 4218)
sf_use_s2(FALSE)
qq &lt;- st_sfc(st_point(st_coordinates(q)[1, ]), crs = 4326)
round(as.numeric(st_distance(p, qq)), 2)
#&gt; [1] ''' + n(_dt['desplazamiento_m'][0], 2),
      '''import pyproj
eli = pyproj.CRS(4326).ellipsoid
print(round(eli.semi_major_metre, 1))
#&gt; ''' + n(el['a'], 1) + '''

g = pyproj.Geod(ellps="WGS84")
tr = pyproj.Transformer.from_crs(4326, 4218, always_xy=True)
lo, la = tr.transform(-74.0721, 4.7110)
print(round(g.inv(-74.0721, 4.7110, lo, la)[2], 2))
#&gt; ''' + n(_dt['desplazamiento_m'][0], 2))}
      <p>Con el elipsoide y el datum en su sitio, la pregunta siguiente es la que separa a
      quien sabe usar coordenadas de quien cree que las sabe usar: <em>¿son la latitud y la
      longitud unas coordenadas cartesianas cualesquiera?</em> El módulo 2 la contesta con un
      metro en la mano.</p>
""" + CIERRE


# =====================================================================
# MÓDULO 2 · Latitud y longitud no son coordenadas cartesianas
# =====================================================================
_eu = gr["euclidea"]
MOD2 = cabecera(
    2, "Latitud y longitud no son coordenadas cartesianas", "Degrees are not metres",
    "Medir cuánto vale un grado según dónde se esté, y qué le hace eso a una distancia."
) + f"""
      <p>Un par de columnas llamadas <code>lon</code> y <code>lat</code> tiene todo el aspecto
      de un par de coordenadas cartesianas: dos números reales, uno por eje. Casi cualquier
      biblioteca las tratará como tales si se lo pides, y ninguna se quejará. El problema es
      que <strong>un grado no mide lo mismo en los dos ejes, ni lo mismo en todas partes</strong>,
      y una resta entre grados no es una distancia.</p>

      <p>El grado de <em>longitud</em> es un arco sobre un paralelo, y los paralelos se
      encogen hacia los polos: su longitud va con el coseno de la latitud. El grado de
      <em>latitud</em> es un arco sobre el meridiano y sería constante sobre una esfera; sobre
      el elipsoide crece un poco hacia el polo, porque allí la curvatura es menor. Las dos
      cosas se ven a la vez en el simulador.</p>

{sim('grados', 'Cuánto mide un grado, según la latitud',
     'Distancias geodésicas sobre el elipsoide WGS84.')}
      <p>En el ecuador un grado de longitud mide {firma(n(gr['lon_m_elipsoide'][0], 2), ' m')}
      y uno de latitud {firma(n(gr['lat_m_elipsoide'][0], 2), ' m')}; a 80° el de longitud ha
      caído a {firma(n(gr['lon_m_elipsoide'][-1], 2), ' m')}, un
      {firma(n(gr['lon_pct_del_ecuador'][-1]) + ' %')} de lo que medía. Y hay un detalle que
      conviene no pasar por alto: <strong>sobre la esfera el grado de latitud es constante</strong>
      —su recorrido en la tabla es de {n(gr['lat_esfera_constante'], 8)}&nbsp;m— mientras que
      sobre el elipsoide recorre {firma(n(gr['lat_elipsoide_recorrido_m'], 2), ' m')}. La
      constancia es el artefacto, no el dato.</p>

      <div class="insight-box">
        <h3>Bogotá contra Oslo</h3>
        <p>A la latitud de Bogotá un grado de longitud mide
        {firma(n(gr['bogota_vs_oslo'], 4), ' veces')} lo que mide a la de Oslo. El mismo
        código, la misma unidad, el mismo número escrito en el CSV — y más del doble de
        terreno. Colombia está tan cerca del ecuador que aquí casi todo el mundo se libra de
        este error; por eso el código que se escribe aquí y se reutiliza en otra latitud es
        justamente el que lo sufre.</p>
      </div>

      <p>La consecuencia práctica se mide sobre dato real. Tomando
      {ent(_eu['n_pares'])} pares de las {ent(_eu['n_estaciones'])} estaciones del IDEAM y
      comparando la distancia euclídea en grados con la geodésica, la razón kilómetros por
      grado va de {firma(n(_eu['km_por_grado_min'], 4))} a
      {firma(n(_eu['km_por_grado_max'], 4))}: un recorrido del
      {firma(n(_eu['recorrido_pct']) + ' %')}. Si la euclídea fuera una distancia, esa razón
      sería constante.</p>

      <p>Y sin embargo la correlación entre las dos es {firma(n(_eu['corr']))}. Las dos cosas
      son ciertas al mismo tiempo, y aprender a sostenerlas juntas es la mitad del capítulo:
      <strong>una medida puede ser buenísima en promedio y romper igualmente la decisión que
      se toma con ella</strong>. El ejercicio 4 del módulo 12 lo lleva hasta el final con los
      grafos de vecindad del capítulo 6.</p>

{tabs('Un grado, medido',
      '''p1 &lt;- st_sfc(st_point(c(0, 0)), crs = 4326)
p2 &lt;- st_sfc(st_point(c(1, 0)), crs = 4326)
format(round(as.numeric(st_distance(p1, p2)), 2), nsmall = 2)   # s2 apagado
#&gt; [1] ''' + n(gr['lon_m_elipsoide'][0], 2) + '''

q1 &lt;- st_sfc(st_point(c(0, 59.9139)), crs = 4326)
q2 &lt;- st_sfc(st_point(c(1, 59.9139)), crs = 4326)
format(round(as.numeric(st_distance(q1, q2)), 2), nsmall = 2)
#&gt; [1] ''' + n(gr['lon_m_elipsoide'][8], 2) + '''''',
      '''print(f"{g.inv(0, 0, 1, 0)[2]:.2f}")
#&gt; ''' + n(gr['lon_m_elipsoide'][0], 2) + '''
print(f"{g.inv(0, 59.9139, 1, 59.9139)[2]:.2f}")
#&gt; ''' + n(gr['lon_m_elipsoide'][8], 2))}
      <p>Si los grados no son metros, la salida obvia es convertirlos: aplanar la Tierra sobre
      un plano y trabajar allí. Eso es proyectar, y tiene un precio que el módulo 3 no
      describe sino que mide.</p>
""" + CIERRE


# =====================================================================
# MÓDULO 3 · Proyectar es elegir qué destruir
# =====================================================================
def _fila_proy(i):
    return (f"            <tr><th scope=\"row\">{PT['nombre'][i]}</th>"
            f"<td>{PT['familia'][i]}</td>"
            # CINCO decimales, no tres: de esta tabla argumenta el texto
            # —«tres lecturas, y las tres se sostienen en la tabla»— y la
            # regla de publicación de T0.5 es >= 5 para toda cifra de la
            # que se argumente. Con tres, una perturbación del último
            # dígito la absorbe el índice del auditor.
            f"<td>{n(PT['omega_max_grados'][i])}°</td>"
            f"<td>{n(PT['s_min'][i])} – {n(PT['s_max'][i])}</td>"
            f"<td>{n(PT['razon_med'][i])}</td>"
            f"<td>{n(PT['estiramiento'][i])}</td></tr>\n")


_i_merc, _i_3857 = 0, 1
_i_ee = PT["nombre"].index("Equal Earth")
MOD3 = cabecera(
    3, "Proyectar es elegir qué destruir", "There is no perfect projection",
    "Medir la distorsión de área y de ángulo de seis proyecciones, y comprobar el teorema de Tissot."
) + f"""
      <p>Una superficie curva no se puede desplegar sobre un plano sin romperla. No es una
      limitación de las herramientas: es un teorema, y sus consecuencias son las que hacen que
      no exista «el mapa correcto». Toda proyección conserva algunas propiedades y destruye
      otras, y la pregunta profesional nunca es cuál es la buena sino <em>qué estoy dispuesto
      a perder para esto que estoy haciendo</em>.</p>

      <p>Las tres familias clásicas se nombran por lo que salvan. Una proyección
      <strong>conforme</strong> conserva los ángulos en cada punto —y por tanto las formas
      locales— a cambio de deformar las áreas. Una <strong>equivalente</strong> conserva las
      áreas y deforma las formas. Una <strong>equidistante</strong> conserva las distancias,
      pero solo desde un punto o a lo largo de unas líneas concretas. Ninguna conserva las
      tres cosas, y ninguna conserva las dos primeras a la vez.</p>

      <div class="definition">
        <h3>La indicatriz de Tissot</h3>
        <p>Nicolas Auguste Tissot propuso en 1859 una forma de <em>ver</em> la deformación:
        dibujar sobre el mapa un círculo infinitesimal del terreno y mirar en qué se convierte.
        Si sale un círculo, en ese punto no hay deformación angular. Si sale una elipse muy
        alargada, la hay mucha. Y si sale grande, es que el área se está inflando. Los dos
        semiejes de esa elipse, \\(a\\) y \\(b\\), lo dicen todo: la deformación angular máxima
        es \\(\\omega = 2\\arcsin\\frac{{a-b}}{{a+b}}\\) y la escala de área es el producto
        \\(s = a\\,b\\). <strong>Conforme</strong> equivale a \\(\\omega = 0\\);
        <strong>equivalente</strong>, a \\(s = 1\\).</p>
      </div>

      <p>En el mapa siguiente los círculos naranjas son indicatrices de verdad: cada uno es un
      círculo de {firma(ent(pr['radio_km']), ' km')} sobre el terreno, proyectado. Cambia de
      proyección con los botones y mira dos cosas a la vez: si las elipses siguen siendo
      redondas y si cambian de tamaño de un sitio a otro. La primera vista trata la longitud y
      la latitud como si fueran coordenadas planas, que es lo que hace cualquier programa al
      que no se le dice nada.</p>

{mapa_html('cap2-proyecciones', 'El mundo bajo seis proyecciones, con la distorsión medida')}
      <p>Mercator mantiene todas las elipses redondas y las hincha hacia los polos; Mollweide
      y Equal Earth las mantienen del mismo tamaño y las aplastan; Robinson no hace ni una
      cosa ni la otra. Eso que se ve, medido sobre las {ent(pr['n_indicatrices'])}
      indicatrices de la rejilla y sobre los {ent(pr['n_paises'])} países de
      <code>spData::world</code>, es esta tabla.</p>

      <div class="tabla-caja">
        <table>
          <caption>Distorsión medida de las seis proyecciones. La razón de área es la del área
            proyectada de cada país frente a su área geodésica sobre el elipsoide.</caption>
          <thead><tr><th scope="col">Proyección</th><th scope="col">Familia</th>
            <th scope="col">ω máx.</th><th scope="col">Escala de área</th>
            <th scope="col">Razón mediana</th><th scope="col">Estiramiento</th></tr></thead>
          <tbody>
{''.join(_fila_proy(i) for i in range(len(PT['nombre'])))}          </tbody>
        </table>
      </div>

      <p>Tres lecturas, y las tres se sostienen en la tabla. La primera:
      <strong>Mercator es conforme de verdad</strong> —su ω máxima es
      {n(PT['omega_max_grados'][_i_merc])}°, cero hasta donde el cálculo llega— y por eso
      infla las áreas sin límite: su escala de área llega a
      {firma(n(PT['s_max'][_i_merc]))} en la rejilla, y sobre los países reales el peor
      sale {firma(n(PT['razon_max'][_i_merc], 2), ' veces')} más grande de lo que es.</p>

      <p>La segunda: <strong>Equal Earth es equivalente exacta</strong>, con la escala de área
      pegada a {n(PT['s_min'][_i_ee])}–{n(PT['s_max'][_i_ee])} y una deformación angular
      que llega a {firma(n(PT['omega_max_grados'][_i_ee]) + '°')}. Ese es el intercambio,
      y está en la misma fila.</p>

      <p>Y la tercera, que es el teorema: <strong>ninguna de las seis es conforme y
      equivalente a la vez</strong>. No es una casualidad de la muestra. Una proyección
      conforme tiene \\(a = b\\) en todo punto, así que su escala de área es \\(a^2\\); para
      que además fuera equivalente haría falta \\(a^2 = 1\\), es decir escala 1 en todas
      partes, y eso es una isometría — que es justo lo que la curvatura prohíbe. El generador
      del capítulo <em>comprueba</em> esa incompatibilidad y se detiene si alguna vez saliera
      lo contrario.</p>

{tabs('Proyectar y medir la distorsión',
      '''# Mercator es conforme: su escala de AREA es el cuadrado de la lineal
k45 &lt;- ''' + n(pr['mercator']['escala'][2]) + '''
round(k45^2, 5)
#&gt; [1] ''' + n(pr['mercator']['escala'][2] ** 2) + '''

# y el capitulo la mide sobre la propia proyeccion:
round(''' + n(pr['mercator']['area'][2]) + ''', 5)
#&gt; [1] ''' + n(pr['mercator']['area'][2]),
      '''import numpy as np
# sec(45 grados) al cuadrado es 2 sobre la esfera
print(f"{1 / np.cos(np.radians(45)) ** 2:.5f}")
#&gt; 2.00000
# sobre el elipsoide, medido:
print(f"{''' + n(pr['mercator']['area'][2]) + ''':.5f}")
#&gt; ''' + n(pr['mercator']['area'][2]))}
      <p>Con la teoría medida, el paso siguiente es operativo: en el trabajo real no se elige
      «una proyección conforme» sino un <strong>código EPSG</strong>, y hay cuatro que este
      curso usa todo el rato. El módulo 4 los pone a prueba sobre los
      {ent(ep['n_municipios'])} municipios de Colombia.</p>
""" + CIERRE


# =====================================================================
# MÓDULO 4 · EPSG en la práctica
# =====================================================================
_f = {x["codigo"]: x for x in ep["filas"]}
_co, _ar = ep["continente"], ep["archipielago"]
MOD4 = cabecera(
    4, "EPSG en la práctica: 4326, 3857, 3116 y 9377", "Picking a CRS for Colombia",
    "Elegir entre los dos sistemas oficiales de Colombia con una cifra, y no con una costumbre."
) + f"""
      <p>El registro EPSG es un catálogo de sistemas de referencia, cada uno con un número. En
      el trabajo diario aparecen siempre los mismos cuatro, y conviene tener claro qué es cada
      uno antes de teclearlo. <strong>EPSG:4326</strong> no es una proyección: es el sistema
      geográfico WGS84, longitud y latitud en grados. <strong>EPSG:3857</strong> es el
      Web&nbsp;Mercator de las teselas de mapa web. Y para Colombia hay dos oficiales:
      <strong>EPSG:3116</strong>, MAGNA-SIRGAS con origen en el observatorio de Bogotá, y
      <strong>EPSG:9377</strong>, el Origen-Nacional único que el IGAC adoptó después.</p>

      <p>Los dos colombianos son transversas de Mercator, o sea conformes, y se diferencian en
      dos cosas: dónde ponen el meridiano central y qué factor de escala usan. 3116 lo pone en
      el observatorio y usa \\(k = 1\\); 9377 lo pone en el meridiano 73 y usa
      \\(k = 0{{.}}9992\\). Ese \\(k\\) menor que uno no es un capricho: es la forma clásica de
      repartir el error de una transversa de Mercator sobre una franja ancha. La cuestión es
      si funciona, y eso se mide.</p>

      <div class="insight-box">
        <h3>Dos propiedades que salen exactas, y sirven de control</h3>
        <p>Una transversa de Mercator es conforme, así que su escala de área es el cuadrado de
        la lineal, y esa alcanza su mínimo en el meridiano central, donde vale \\(k\\). Por
        tanto <strong>la razón de área mínima sobre todo el país tiene que ser exactamente
        \\(k^2\\)</strong>. Medida sobre los {ent(ep['n_municipios'])} municipios: 9377 da
        {firma(n(_f[9377]['razon_min'], 6))} y \\(k^2 = {n(_f[9377]['razon_min'], 6)}\\); 3116 da
        {firma(n(_f[3116]['razon_min'], 6))} y su \\(k\\) es 1. Cuadran a la sexta cifra. No es
        una comprobación decorativa: es la que descubrió que la referencia de área que este
        capítulo usaba al principio estaba mal.</p>
      </div>

      <p>El mapa siguiente muestra Colombia bajo tres sistemas, otra vez con sus indicatrices;
      el segundo colorea los departamentos por el error de área que comete 3116. Mira el
      contraste entre el centro del país y los extremos oriental y occidental.</p>

{mapa_html('cap2-proyecciones-co', 'Colombia bajo tres sistemas de referencia')}
{mapa_html('cap2-error-3116', 'Exceso de área de EPSG:3116, por departamento')}
      <p>El patrón es el que la teoría anuncia: el error de una transversa de Mercator crece
      al alejarse de su meridiano central, y crece rápido. Repartiendo los municipios por su
      distancia al meridiano de 3116 se ve dónde cada sistema gana.</p>

      <div class="tabla-caja">
        <table>
          <caption>Error mediano de área, en %, por distancia del centroide municipal al
            meridiano central de EPSG:3116.</caption>
          <thead><tr><th scope="col">Distancia</th><th scope="col">Municipios</th>
            <th scope="col">EPSG:3116</th><th scope="col">EPSG:9377</th></tr></thead>
          <tbody>
{''.join(f'            <tr><th scope="row">{b}</th><td>{ent(k)}</td><td>{n(a)}</td><td>{n(c)}</td></tr>' + chr(10) for b, k, a, c in zip(ep['bandas']['banda'], ep['bandas']['n'], ep['bandas']['err_3116_pct'], ep['bandas']['err_9377_pct']))}          </tbody>
        </table>
      </div>

      <p>Cerca del meridiano 3116 es imbatible —vale cero por construcción— y más allá de los
      cinco grados pierde por un factor grande. Con eso podríamos cerrar el módulo
      recomendando 9377 y quedarnos tranquilos. <strong>El dato no deja.</strong></p>

      <div class="warning-box">
        <h3>El archipiélago da la vuelta a la recomendación</h3>
        <p>Sobre los {ent(_co['n'])} municipios <em>continentales</em>, 9377 gana el peor caso
        con holgura: {firma(n(_co['max_9377_pct']) + ' %')} frente a
        {firma(n(_co['max_3116_pct']) + ' %')} de 3116 — el peor es
        {_co['peor_municipio']} ({_co['peor_dpto']}). Pero pierde la mediana:
        {firma(n(_co['med_3116_pct']) + ' %')} de 3116 contra
        {firma(n(_co['med_9377_pct']) + ' %')} de 9377, porque el factor de escala se paga en
        todas partes. Y con {' y '.join(_ar['municipios'])} dentro, 3116 gana también el peor
        caso nacional ({n(_ar['max_3116_pct'])} % contra {n(_ar['max_9377_pct'])} %): el
        archipiélago está setecientos kilómetros mar adentro y le queda más cerca el meridiano
        de 3116 que el de 9377. <strong>Dos municipios de {ent(ep['n_municipios'])} cambian la
        respuesta.</strong></p>
      </div>

      <p>La lección no es «usa 9377» ni «usa 3116». Es que la pregunta «¿qué CRS uso?» no
      tiene respuesta sin decir <em>para qué</em>, <em>sobre qué extensión</em> y <em>con qué
      criterio</em> —peor caso o caso típico—, y que cambiar cualquiera de las tres cosas puede
      invertir la recomendación. El ejercicio 1 del módulo 12 hace ese recorrido entero.</p>

      <p>Y una nota sobre 3857, que aparece en la tabla del módulo 3 y aquí: su razón de área
      mediana sobre los municipios es {firma(n(_f[3857]['razon_med'], 5))} y su peor caso
      llega a {firma(n(_f[3857]['razon_max'], 5))}. Hay
      {firma(ent(_f[3857]['n_sobre_1pct']))} municipios que se pasan del 1&nbsp;% de error con
      él, frente a {ent(_f[9377]['n_sobre_1pct'])} con 9377. Web&nbsp;Mercator sirve para
      pintar teselas, no para medir.</p>

{tabs('Comparar sistemas sobre el mismo dato',
      '''mun &lt;- st_transform(carga_municipios(), 4326)
verdad &lt;- as.numeric(st_area(mun))            # s2 apagado: elipsoide
razon9377 &lt;- as.numeric(st_area(st_transform(mun, 9377))) / verdad
round(min(razon9377), 6)
#&gt; [1] ''' + n(_f[9377]['razon_min'], 6) + '''
round(0.9992^2, 6)
#&gt; [1] 0.998401''',
      '''import geopandas as gpd, numpy as np
mun = gpd.read_file("datos/procesado/colombia_adm2.gpkg").to_crs(4326)
verdad = np.array([abs(g.geometry_area_perimeter(x)[0]) for x in mun.geometry])
razon = mun.to_crs(9377).area.values / verdad
print(round(razon.min(), 6), round(0.9992 ** 2, 6))
#&gt; ''' + n(_f[9377]['razon_min'], 6) + ''' 0.998401''')}
      <p>Elegido el sistema, queda ponerlo. Y ahí está el error más frecuente de todos, el que
      aparece en cada revisión de código y en cada respuesta de un modelo de lenguaje: el
      módulo 5.</p>
""" + CIERRE


# =====================================================================
# MÓDULO 5 · st_transform vs. st_set_crs
# =====================================================================
_si = et["silencioso"]
MOD5 = cabecera(
    5, "Reproyectar no es reetiquetar", "st_transform vs st_set_crs",
    "Separar las dos operaciones que todo el mundo confunde, y medir qué hace cada una."
) + f"""
      <p>Hay dos operaciones distintas que se parecen mucho al escribirlas y no se parecen en
      nada al ejecutarlas. <code>st_transform()</code> <strong>reproyecta</strong>: recalcula
      todas las coordenadas para expresarlas en otro sistema.
      <code>st_set_crs()</code> <strong>reetiqueta</strong>: deja las coordenadas exactamente
      donde están y cambia la etiqueta que dice en qué sistema se supone que están. La primera
      cambia los números y conserva el sitio; la segunda conserva los números y cambia el
      sitio.</p>

      <p>El syllabus del curso señala esta confusión como el error número uno que cometen los
      modelos de lenguaje cuando se les pide código geoespacial, y la razón es fácil de ver:
      las dos líneas se leen igual de bien y solo una de ellas es la que hacía falta. Aquí se
      mide sobre las {ent(et['n_localidades'])} localidades de Bogotá, que vienen en
      {et['crs_original']}.</p>

      <div class="tabla-caja">
        <table>
          <caption>Qué le hace cada operación a los {ent(et['n_vertices'])} vértices de la
            capa.</caption>
          <thead><tr><th scope="col"></th><th scope="col">Vértices movidos</th>
            <th scope="col">Máximo desplazamiento</th></tr></thead>
          <tbody>
            <tr><th scope="row"><code>st_set_crs(x, 4326)</code></th><td>0</td>
              <td>{n(et['set_crs_max_delta'], 5)}</td></tr>
            <tr><th scope="row"><code>st_transform(x, 4326)</code></th>
              <td>{ent(et['transform_n_movidas'])}</td>
              <td>{ent(et['transform_max_delta'])}</td></tr>
          </tbody>
        </table>
      </div>

      <p>Cero contra {ent(et['transform_n_movidas'])}: no es una diferencia de grado. Y el
      resultado de reetiquetar no es un error, es un objeto perfectamente válido que dice
      estar en grados y contiene metros. Su caja envolvente llega a una «longitud» de
      {firma(ent(et['lon_absurda']), ' grados')} — ese número absurdo es el único delator que
      hay, y solo si alguien mira.</p>

{sim('etiquetar', 'Las dos operaciones, sobre la misma capa',
     'La capa original está en ' + et['crs_original'] + '.')}
      <p>Fíjate en que la superficie tampoco avisa. Bien reproyectada, la suma de las
      localidades da {firma(n(et['area_bien_km2'], 3), ' km²')}, que es el área de Bogotá; el
      objeto reetiquetado o bien devuelve un disparate o bien devuelve
      <code>NaN</code> según la biblioteca, y ninguna de las dos cosas es un mensaje que
      explique lo que pasó.</p>

      <div class="insight-box">
        <h3>No toda etiqueta equivocada hace daño, y saber cuál sí es el trabajo</h3>
        <p>Reetiquetar un dato de MAGNA-SIRGAS geográfico (EPSG:{_si['desde']}) como
        WGS84 (EPSG:{_si['hasta']}) desplaza {firma(n(_si['desplazamiento_m'], 2), ' m')}: los
        dos sistemas coinciden a nivel de centímetros y el error es inocuo. Reetiquetar el
        datum viejo, EPSG:{_si['contraste_desde']}, desplaza
        {firma(n(_si['contraste_desplazamiento_m'], 2), ' m')}. La misma clase de error, tres
        órdenes de magnitud de diferencia. Por eso «nunca uses <code>st_set_crs</code>» es un
        consejo malo: <code>st_set_crs</code> es exactamente la herramienta correcta cuando el
        dato viene <em>sin</em> CRS declarado y sabes cuál es. Lo que no se puede es usarla
        para cambiar de sistema.</p>
      </div>

{tabs('Las dos operaciones, lado a lado',
      '''loc &lt;- st_read("datos/procesado/bogota_localidades.gpkg", quiet = TRUE)
bien &lt;- st_transform(loc, 4326)      # RECALCULA
mal  &lt;- st_set_crs(loc, 4326)        # solo cambia la etiqueta
max(abs(st_coordinates(mal)[, 1:2] - st_coordinates(loc)[, 1:2]))
#&gt; [1] 0

sprintf("%.1f", as.numeric(st_bbox(mal))[1])
#&gt; [1] ''' + n(et['bbox_mal'][0], 1) + '''''',
      '''loc = gpd.read_file("datos/procesado/bogota_localidades.gpkg")
mal = loc.set_crs(4326, allow_override=True)   # solo la etiqueta
print((mal.geometry == loc.geometry).all())
#&gt; True
print(round(mal.total_bounds[0], 1))
#&gt; ''' + n(et['bbox_mal'][0], 1))}
      <p>Puesto el sistema y puesto bien, llega el momento de medir de verdad. Y ahí aparece
      una discrepancia que no es un error de nadie: dos funciones que se llaman igual dan
      números distintos, y las dos tienen razón. Es el módulo 6.</p>
""" + CIERRE


# =====================================================================
# MÓDULO 6 · Medir sobre la Tierra
# =====================================================================
_mc, _mm, _mdi = md["colombia"], md["municipios"], md["distancias"]
MOD6 = cabecera(
    6, "Medir sobre la Tierra", "s2, GEOS and the ellipsoid",
    "Saber sobre qué superficie mide cada función, y cuánto separa a unas de otras."
) + f"""
      <p>Cuando se le pide a <code>sf</code> el área de un polígono en longitud y latitud, la
      respuesta depende de un interruptor global que casi nadie toca:
      <code>sf_use_s2()</code>. Con él encendido —que es lo de fábrica— manda la biblioteca
      <strong>s2</strong> de Google, que hace geometría <em>sobre una esfera</em>. Con él
      apagado, el cálculo geodésico lo hace <strong>lwgeom</strong> <em>sobre el
      elipsoide</em>. Las dos son correctas; miden cosas distintas.</p>

      <p>La diferencia entre una esfera y el elipsoide sonaba pequeña en el módulo 1 —medio
      kilómetro sobre nueve mil— porque una distancia larga promedia el achatamiento a lo
      largo del camino. Un área no promedia nada: acumula. Sobre Colombia entera, la cifra es
      esta.</p>

      <div class="warning-box">
        <h3>La misma Colombia, dos superficies</h3>
        <p>Sobre el elipsoide, {firma(ent(_mc['area_elipsoide_km2']), ' km²')}. Sobre la
        esfera de <code>s2</code>, {firma(ent(_mc['area_esfera_km2']), ' km²')}. La esfera la
        infla en {firma(ent(_mc['dif_esfera_km2']), ' km²')}, un
        {firma(n(_mc['dif_esfera_pct']) + ' %')} — más superficie que la suma de los
        {ent(_mm['equivalente_a_municipios'])} municipios más pequeños del país. Y proyectar a
        EPSG:9377 se queda a {firma(n(abs(_mc['dif_9377_pct'])) + ' %')} del elipsoide: la
        proyección conforme se acerca más a la verdad que la esfera.</p>
      </div>

      <p>Este es el tipo de discrepancia que hay que <em>declarar</em>, no esconder. Un
      capítulo que publicara el área de Colombia sin decir sobre qué superficie la midió
      estaría publicando un número sin unidades. El simulador deja recorrer las tres medidas
      sobre el país y sobre los municipios.</p>

{sim('medir', 'La misma geometría, medida de tres formas',
     'Sobre los ' + ent(_mm['n']) + ' municipios; la referencia es el elipsoide GRS80.')}
      <p>Sobre los municipios uno a uno la razón esfera/elipsoide va de
      {firma(n(_mm['razon_min'], 5))} a {firma(n(_mm['razon_max'], 5))}, con mediana
      {firma(n(_mm['razon_med'], 5))}. Es un sesgo, no un ruido: la esfera se equivoca siempre
      en la misma dirección a esta latitud, y por eso no se compensa al sumar. En las
      distancias el efecto es mucho menor —sobre {ent(_mdi['n_pares'])} pares de estaciones,
      la mediana de la diferencia es {firma(n(_mdi['dif_med_m'], 2), ' m')}—, y esa asimetría
      entre áreas y distancias es justo lo que hay que recordar.</p>

      <div class="insight-box">
        <h3>La regla operativa</h3>
        <p>Para <strong>medir</strong> —áreas, longitudes, buffers, distancias que van a
        entrar en un modelo— proyecta primero a un CRS métrico adecuado a la extensión del
        trabajo, y hazlo explícito en el código. Deja el cálculo geodésico sobre lon/lat para
        lo que de verdad es global, donde ninguna proyección plana sirve. Y si un resultado
        va a publicarse, di sobre qué superficie se midió: en este capítulo son
        {ent(_mc['dif_esfera_km2'])} km² de diferencia entre callarlo y decirlo.</p>
      </div>

{tabs('El interruptor que cambia el número',
      '''col &lt;- st_union(st_geometry(mun))
sf_use_s2(TRUE);  a_esf &lt;- as.numeric(st_area(col)) / 1e6
sf_use_s2(FALSE); a_eli &lt;- as.numeric(st_area(col)) / 1e6
round(a_esf - a_eli, 2)
#&gt; [1] ''' + str(round(md['colombia']['dif_esfera_km2'], 2)) + '''
round(a_eli / 1000, 3)
#&gt; [1] ''' + str(round(md['colombia']['area_elipsoide_km2'] / 1000, 3)),
      '''col = mun.geometry.union_all()
print(round(abs(g.geometry_area_perimeter(col)[0]) / 1e6, 2))
#&gt; ''' + n(md['colombia']['area_elipsoide_km2'], 2) + '''
# GeoPandas .area sobre lon/lat da GRADOS CUADRADOS, que no es un area
print(round(mun.to_crs(9377).area.sum() / 1e6, 2))
#&gt; ''' + n(md['colombia']['area_9377_km2'], 2))}
      <p>Hasta aquí el sistema de referencia. La segunda mitad del capítulo es el otro frente
      por el que un dato espacial se estropea sin avisar: cómo se guarda, cómo se lee y de
      dónde salieron las coordenadas. Antes de seguir, cuatro preguntas para comprobar que las
      trampas de esta primera mitad han quedado claras.</p>

{quiz_html('cap2-trampas', 'Cuatro trampas de CRS',
           'Las cuatro equivocaciones de la primera mitad del capítulo. Sin nota.')}

      <p>Si alguna se te ha resistido, el número del módulo que la contesta va en la
      retroalimentación. Y ahora sí, los formatos.</p>
""" + CIERRE


# =====================================================================
# MÓDULO 7 · Formatos vectoriales
# =====================================================================
_sh, _pa = fo["shapefile"], fo["pais"]
MOD7 = cabecera(
    7, "Formatos vectoriales: shapefile, GeoPackage y GeoJSON", "Where the data lives",
    "Medir las limitaciones del shapefile en vez de citarlas, y saber cuándo importan."
) + f"""
      <p>El shapefile lleva desde 1998 siendo el formato de intercambio por defecto del mundo
      geoespacial, y sigue siéndolo aunque casi todas las listas de «sus limitaciones» se
      repiten de memoria sin comprobarlas. Este módulo las comprueba: se escribe una capa real
      —{ent(fo['n_rasgos'])} municipios con {ent(_sh['n_campos'])} campos, entre ellos fechas,
      lógicos y nombres largos— y se vuelve a leer, a ver qué llega.</p>

      <p>Lo primero que se nota es que un shapefile no es un archivo: son
      {firma(ent(_sh['n_archivos']))} ({', '.join('<code>' + a.split('.')[-1] + '</code>' for a in _sh['archivos'])}),
      y si uno se pierde por el camino la capa deja de abrirse o pierde su sistema de
      referencia. Y no trae <code>.cpg</code>, así que <strong>el archivo de atributos no
      declara en qué codificación están sus textos</strong>: quien lo lea tiene que
      adivinarlo, y ahí es donde mueren las tildes al cruzar de un sistema a otro.</p>

      <p>Lo segundo es lo que le pasa a los nombres de campo, que es peor de lo que la lista
      de memoria cuenta.</p>

      <div class="tabla-caja">
        <table>
          <caption>Qué le hace el shapefile a los nombres de campo de más de 10 caracteres.
            {ent(_sh['n_campos_largos'])} de los {ent(_sh['n_campos'])} campos.</caption>
          <thead><tr><th scope="col">Nombre original</th><th scope="col">Nombre al releer</th></tr></thead>
          <tbody>
{''.join(f'            <tr><th scope="row"><code>{a}</code></th><td><code>{b}</code></td></tr>' + chr(10) for a, b in zip(_sh['ejemplos_antes'], _sh['ejemplos_despues']))}          </tbody>
        </table>
      </div>

      <p><strong>No los trunca: los desfigura.</strong> Para que los diez caracteres sigan
      siendo únicos, GDAL les quita vocales, y el resultado ya no se reconoce a ojo ni se
      puede deshacer. Un guion que espere una columna llamada
      <code>{_sh['ejemplos_antes'][0]}</code> no falla con un mensaje claro: falla con un
      «columna no encontrada» sobre un nombre que nadie escribió nunca.</p>

      <p>Los tipos también se pierden. El GeoPackage, en cambio, devuelve los nombres
      {'intactos' if _sh else ''} y los tipos donde estaban, y pesa
      {firma(n(fo['gpkg']['razon_sobre_shp'], 3), '×')} lo que el shapefile. El GeoJSON
      es el más pesado de los tres, {firma(n(fo['geojson']['razon_sobre_shp'], 3), '×')} el
      shapefile — sobre el país entero, {firma(n(_pa['geojson_mb'], 1), ' MB')} de GeoJSON
      frente a {firma(n(_pa['gpkg_mb'], 1), ' MB')} de GeoPackage, un factor de
      {firma(n(_pa['razon'], 3))}.</p>

{sim('formatos', 'Los tres formatos, sobre el mismo dato',
     'Los megabytes del país son los ' + ent(ep['n_municipios']) + ' municipios sin simplificar.')}
      <p>La conclusión práctica no es «no uses shapefiles»: seguirás recibiéndolos. Es que en
      cuanto un dato entra en tu proyecto conviene pasarlo a GeoPackage y trabajar desde ahí,
      y que si tienes que <em>entregar</em> un shapefile, los nombres de campo se eligen antes
      de escribirlo y no después. Este curso guarda todo en GeoPackage por ese motivo.</p>

{tabs('El viaje de ida y vuelta',
      '''x &lt;- carga_municipios()[1:60, c("divipola", "municipio")]
x$desercion_escolar_2024 &lt;- 0
tmp &lt;- file.path(tempdir(), "prueba.shp")
suppressWarnings(st_write(x, tmp, quiet = TRUE, delete_dsn = TRUE))
names(st_read(tmp, quiet = TRUE))[3]
#&gt; [1] "''' + fo['shapefile']['ejemplos_despues'][0] + '''"

length(list.files(tempdir(), pattern = "^prueba[.]"))
#&gt; [1] ''' + str(fo['shapefile']['n_archivos']),
      '''x = mun.head(60)[["shapeID", "geometry"]].copy()
x["desercion_escolar_2024"] = 0.0
x.to_file("/tmp/prueba.shp")
print("desercion_escolar_2024" in gpd.read_file("/tmp/prueba.shp").columns)
#&gt; False
x.to_file("/tmp/prueba.gpkg", driver="GPKG")
print("desercion_escolar_2024" in gpd.read_file("/tmp/prueba.gpkg").columns)
#&gt; True''')}
      <p>El formato es el envase. Lo que viene dentro —unas columnas de números que alguien
      decidió llamar <code>lon</code> y <code>lat</code>— tiene sus propias trampas, y la
      primera es de las que mandan un dato al otro lado del planeta sin decir nada.</p>
""" + CIERRE


# =====================================================================
# MÓDULO 8 · De un CSV a un objeto sf
# =====================================================================
_dest = cs["destino"]
_i_max = max(range(len(_dest["n"])), key=lambda i: _dest["n"][i])
MOD8 = cabecera(
    8, "De un CSV a un objeto sf", "st_as_sf and the lon/lat trap",
    "Construir geometría desde columnas, y cazar el error de orden antes de que viaje."
) + f"""
      <p>La mayoría de los datos espaciales de este curso no llegan como mapas: llegan como
      tablas con dos columnas de coordenadas. Convertirlas en geometría es una línea
      —<code>st_as_sf(x, coords = c("lon", "lat"), crs = 4326)</code>— y en esa línea caben
      dos errores que no producen ningún mensaje.</p>

      <p>El primero es el orden. Media informática geoespacial escribe las coordenadas como
      (longitud, latitud), que es el orden (x, y) del plano, y la otra media las escribe como
      (latitud, longitud), que es como se dicen en voz alta. Ninguna de las dos convenciones es
      incorrecta; lo que es incorrecto es no saber cuál trae el archivo. Y el resultado de
      equivocarse es un objeto perfectamente válido, porque las cifras siguen siendo
      latitudes y longitudes posibles.</p>

      <p>El mapa siguiente lo enseña con las {ent(cs['n'])} estaciones del IDEAM: los rombos
      son sus posiciones correctas y los puntos, las mismas estaciones con las dos columnas
      cambiadas de sitio.</p>

{mapa_html('cap2-invertidos', 'Las estaciones del IDEAM con la longitud y la latitud intercambiadas')}
      <p>Colombia está entre las longitudes {n(cs['caja_bien'][0], 2)} y
      {n(cs['caja_bien'][2], 2)} y las latitudes {n(cs['caja_bien'][1], 2)} y
      {n(cs['caja_bien'][3], 2)}. Al intercambiarlas, las estaciones aterrizan en
      <strong>{_dest['nombre'][_i_max]}</strong> —{firma(ent(_dest['n'][_i_max]))} de las
      {ent(cs['n'])}, y las {ent(cs['n_en_mar'])} restantes en mar abierto—, a una media de
      {firma(ent(cs['desplazamiento_km_med']), ' km')} de donde deberían estar. La más
      cercana a su sitio se queda a {firma(ent(cs['desplazamiento_km_min']), ' km')}.
      <strong>Ninguna cae en Colombia</strong>, y <code>st_as_sf</code> no dio ni un aviso.</p>

{sim('invertir', 'Qué pasa al intercambiar las dos columnas',
     'Las ' + ent(cs['n']) + ' estaciones del IDEAM, con temperatura media 1991-2020.')}
      <p>Que el desastre sea tan grande es, paradójicamente, una suerte: aquí el error se ve a
      simple vista en cuanto alguien pinta el mapa. El caso peligroso es el país cuyos rangos
      de longitud y de latitud <em>se solapan</em>, donde una fila invertida puede caer dentro
      del propio territorio y no hay forma geométrica de distinguirla. El ejercicio 3 del
      módulo 12 construye la regla de detección y mide exactamente cuándo funciona y cuándo
      no.</p>

      <div class="warning-box">
        <h3>El segundo error, y este es muy de aquí: la coma decimal</h3>
        <p>Un CSV exportado desde una hoja de cálculo en configuración regional española trae
        las coordenadas con coma: <code>{cs['coma_decimal']['ejemplo_lon']}</code>.
        <code>read.csv</code> no falla — lee la columna como <strong>texto</strong>. Si después
        se convierte con <code>as.numeric</code>, las cinco coordenadas de la prueba se
        convierten en {firma(ent(cs['coma_decimal']['n_na']))} <code>NA</code>, y una fila con
        coordenada <code>NA</code> desaparece del mapa sin ruido. Es el mismo patrón que se
        llevó por delante casi trescientos mil estudiantes en la Fase 0 de este curso: <em>la
        operación que devuelve un valor plausible en vez de fallar</em>.</p>
      </div>

{tabs('De columnas a geometría',
      '''est &lt;- read.csv("precalculo/salidas/cap2_estaciones.csv")
bien &lt;- st_as_sf(est, coords = c("lon", "lat"), crs = 4326)
mal  &lt;- st_as_sf(est, coords = c("lat", "lon"), crs = 4326)   # invertido
round(mean(as.numeric(st_distance(bien, mal, by_element = TRUE))) / 1000, 1)
#&gt; [1] ''' + n(cs['desplazamiento_km_med'], 1) + '''

round(as.numeric(st_bbox(mal))[2], 2)
#&gt; [1] ''' + n(cs['caja_mal'][1], 2),
      '''import pandas as pd
est = pd.read_csv("precalculo/salidas/cap2_estaciones.csv")
d = g.inv(est.lon.values, est.lat.values, est.lat.values, est.lon.values)[2] / 1000
print(round(d.mean(), 1))
#&gt; ''' + n(cs['desplazamiento_km_med'], 1) + '''
print(round(est.lon.min(), 2))
#&gt; ''' + n(cs['caja_mal'][1], 2))}
      <p>Un error de diez mil kilómetros se caza mirando. El módulo siguiente trata de los que
      no se cazan mirando: los errores de cien metros, que no mueven el mapa y sí mueven el
      resultado.</p>
""" + CIERRE


# =====================================================================
# MÓDULO 9 · Error posicional y quién lo paga
# =====================================================================
_r2 = po["redondeos"][2]
_TABLA_REDONDEOS = "".join(
    fila(r["decimales"], ent(r["n_posiciones"]), n(r["desplaz_med_m"], 1) + " m",
         ent(r["n_cambian"]) + " (" + n(r["pct_cambian"]) + " %)")
    for r in po["redondeos"])
_men, _sg = po["men_descartada"], po["sesgo"]
_ru = po["ruidos"]
MOD9 = cabecera(
    9, "Error posicional, y quién lo paga", "Geocoding error is not uniform",
    "Medir qué rompe un error de posición pequeño, y comprobar que no lo rompe igual en todas partes."
) + f"""
      <p>Casi ningún dato espacial nace con coordenadas: nace con direcciones, y alguien las
      convierte. Ese alguien —un geocodificador— acierta con un error que casi nunca es cero
      y casi nunca se publica. La pregunta de este módulo no es cuánto se equivoca, que
      depende del proveedor, sino <strong>qué se rompe cuando se equivoca, y si se rompe igual
      para todos</strong>.</p>

      <p>Para medirlo hace falta un dato cuya posición se conozca bien, y luego estropearlo a
      propósito. Aquí son las {ent(po['n_sedes'])} sedes educativas de Bogotá, con las
      coordenadas precisas de la Secretaría de Educación, degradadas de dos formas: redondeando
      las coordenadas geográficas —que es lo que hacen muchas fuentes al publicarlas— y
      añadiendo ruido en metros, que es como se comporta de verdad un geocodificador.</p>

      <div class="tabla-caja">
        <table>
          <caption>Efecto de redondear las coordenadas geográficas de las
            {ent(po['n_sedes'])} sedes.</caption>
          <thead><tr><th scope="col">Decimales</th><th scope="col">Posiciones distintas</th>
            <th scope="col">Desplazamiento medio</th><th scope="col">Cambian de localidad</th></tr></thead>
          <tbody>
{_TABLA_REDONDEOS}          </tbody>
        </table>
      </div>

      <p>Con dos decimales —una resolución de poco más de un kilómetro— las
      {ent(po['n_sedes'])} sedes colapsan en {firma(ent(_r2['n_posiciones']), ' posiciones')}
      distintas, {firma(n(po['sedes_por_posicion_2dec'], 4))} sedes por posición. Eso ya no es
      un patrón puntual: es una retícula de redondeo, y cualquier función que mida agrupamiento
      mediría el redondeo.</p>

      <div class="insight-box">
        <h3>El ancla externa: esto no es un experimento de laboratorio</h3>
        <p>La Fase 0 de este curso descartó una fuente nacional del MEN por exactamente este
        motivo: publicaba las coordenadas con dos decimales, y sus
        {ent(_men['n_sedes'])} sedes de Bogotá colapsaban en {ent(_men['n_posiciones'])}
        posiciones — {firma(n(_men['sedes_por_posicion'], 4))} sedes por posición. Degradar
        nuestro dato bueno a dos decimales reproduce esa densidad casi exactamente. La
        simulación y la fuente real cuentan lo mismo.</p>
      </div>

      <p>El mapa deja ver el colapso: los puntos son las posiciones que quedan y los rombos,
      una muestra de las reales.</p>

{mapa_html('cap2-degradado', 'Las sedes de Bogotá con la coordenada redondeada a dos decimales')}
      <p>El redondeo es un caso extremo y fácil de detectar. El ruido en metros no se detecta:
      con {firma(ent(_ru[1]['sigma_m']), ' m')} de desviación —una precisión que cualquier
      geocodificador anunciaría como buena— el desplazamiento medio es de
      {n(_ru[1]['desplaz_med_m'], 1)}&nbsp;m y el mapa se ve idéntico. Y aun así cambian de
      localidad {firma(ent(_ru[1]['n_cambian']), ' sedes')}.</p>

{sim('degradar', 'Cuánto se rompe según cuánto se degrade',
     'Cada punto es un promedio sobre réplicas; el requisito del ejercicio 5 es el 1 %.')}
      <p>Hasta aquí el tamaño del daño. Falta el reparto, que es lo que de verdad convierte
      esto en un problema y no en una molestia. Promediando {firma(ent(_sg['n_replicas']), ' realizaciones')}
      del ruido de {_sg['sigma_m']}&nbsp;m —una sola daba correlaciones que bailaban entre 0,38
      y 0,72, así que no era una medida sino una anécdota— la tasa global de reasignación es
      {firma(n(_sg['tasa_global_pct']) + ' %')} con un error de Monte Carlo de
      {n(_sg['emc_global_pct'])} puntos.</p>

{mapa_html('cap2-sesgo', 'Sedes que cambian de localidad con 150 m de error posicional')}
      <p>Ese {n(_sg['tasa_global_pct'])} %&nbsp;global va de
      {firma(n(_sg['tasa_min_pct']) + ' %')} en {_sg['mejor']} a
      {firma(n(_sg['tasa_max_pct']) + ' %')} en {_sg['peor']}: un factor de
      {firma(n(_sg['razon_max_min'], 2))}. <strong>El mismo error posicional cuesta cincuenta
      veces más en unas localidades que en otras.</strong></p>

      <div class="definition">
        <h3>Y lo que lo explica es geometría, no otra cosa</h3>
        <p>La probabilidad de que un punto cruce el borde de su unidad escala con el perímetro
        por la desviación del error, repartido sobre el área. Medida contra el cociente
        perímetro/área, la tasa de reasignación por localidad correlaciona
        {firma(n(_sg['corr_pearson']))} (Pearson) y {firma(n(_sg['corr_spearman']))}
        (Spearman). Es decir: <strong>el sesgo es predecible antes de tener el dato</strong>,
        y lo predice la forma de las unidades. Por estrato socioeconómico, en cambio, no hay
        patrón monótono — y decirlo también es un resultado, porque es la lectura que un
        lector esperaría encontrar.</p>
      </div>

      <p>La consecuencia para el trabajo aplicado es incómoda y hay que decirla entera: un
      estudio que agregue por unidad geográfica un dato geocodificado tiene un error de
      medición que <em>no es aleatorio ni homogéneo</em>, y su geografía es la de las unidades
      pequeñas y de borde largo — que en casi todas las ciudades son las centrales y las
      densas. No es una razón para no hacer el estudio; es una razón para declarar la
      tolerancia posicional que exige, que es el ejercicio 5.</p>

{tabs('Degradar y medir',
      '''sedes &lt;- read.csv("precalculo/salidas/cap2_sedes.csv")
length(unique(paste(round(sedes$lon, 2), round(sedes$lat, 2))))
#&gt; [1] ''' + str(_r2['n_posiciones']) + '''

round(nrow(sedes) / ''' + str(_r2['n_posiciones']) + ''', 4)
#&gt; [1] ''' + n(po['sedes_por_posicion_2dec'], 4),
      '''sedes = pd.read_csv("precalculo/salidas/cap2_sedes.csv")
pos = set(zip(sedes.lon.round(2), sedes.lat.round(2)))
print(len(pos))
#&gt; ''' + str(_r2['n_posiciones']) + '''
print(round(len(sedes) / len(pos), 4))
#&gt; ''' + n(po['sedes_por_posicion_2dec'], 4))}
      <p>Un punto puede estar donde no debe. Un polígono puede estar directamente mal
      construido, y eso tiene su propia forma de pasar desapercibido: el módulo 10.</p>
""" + CIERRE


# =====================================================================
# MÓDULO 10 · Validación topológica y DE-9IM
# =====================================================================
_lz, _de, _bf = tp["lazo"], tp["de9im"], tp["buffer"]
MOD10 = cabecera(
    10, "Validación topológica y predicados espaciales", "st_is_valid and DE-9IM",
    "Detectar geometría inválida antes de que devuelva un número, y leer la matriz DE-9IM."
) + f"""
      <p>Un polígono es una lista de vértices, y no toda lista de vértices describe un
      polígono. Si los lados se cruzan entre sí, si un anillo interior se sale del exterior o
      si dos vértices consecutivos son el mismo, la geometría es <em>inválida</em>: existe
      como dato y no tiene un interior bien definido. El problema es lo que pasa después.</p>

      <p>El ejemplo canónico es el lazo, un cuadrilátero cuyos lados se cruzan en el centro.
      <code>st_is_valid</code> lo detecta y dice por qué: «{_lz['razon']}». Pero si nadie
      pregunta, <code>st_area</code> devuelve {firma(n(_lz['area_antes'], 5))} — sin error, sin
      aviso, sin nada. Un cero perfectamente utilizable que viaja hacia adelante y se suma con
      los demás.</p>

      <p>Reparado con <code>st_make_valid</code>, el mismo lazo pasa a ser un
      {_lz['tipo_despues']} de {ent(_lz['n_partes_despues'])} partes con área
      {firma(n(_lz['area_despues'], 5))}. La reparación no es cosmética: <strong>cambia el
      número</strong>. Y por eso validar tiene que ser lo primero que se hace con una capa que
      llega de fuera, no lo que se hace cuando algo sale raro.</p>

      <div class="insight-box">
        <h3>Este es el modo de fallo dominante de todo el curso</h3>
        <p>«El área de una geometría inválida es cero» es la misma familia que
        «<code>st_as_sf</code> con las columnas invertidas no avisa», que «la coma decimal se
        lee como texto» y que «reetiquetar el CRS no da error»:
        <strong>la operación que devuelve un valor plausible en vez de fallar</strong>. En la
        Fase 0 de este curso esa familia costó cuatro defectos reales. La defensa no es tener
        cuidado: es comprobar de oficio.</p>
      </div>

      <p>Las capas de este curso pasan esa comprobación —{ent(tp['municipios']['n'])} municipios
      y {ent(tp['crudo']['n'])} departamentos con {firma(ent(tp['municipios']['n_invalidos']))}
      geometrías inválidas—, y eso no es casualidad: se validaron al construirlas.</p>

      <p>Validada la geometría, la pregunta siguiente es cómo se relacionan dos de ellas. El
      estándar de la OGC responde con una matriz de nueve celdas, la
      <strong>DE-9IM</strong>, que cruza el interior, la frontera y el exterior de cada
      geometría y anota la dimensión de cada intersección. Los predicados con nombre
      —<code>st_touches</code>, <code>st_overlaps</code>, <code>st_within</code>— son atajos
      para patrones concretos de esa matriz. El simulador recorre las cinco relaciones
      canónicas.</p>

{sim('de9im', 'Las cinco relaciones canónicas y su matriz DE-9IM',
     'Cada celda cruza interior (I), frontera (B) y exterior (E) de las dos geometrías.')}
      <p>Leer la matriz directamente sirve para los casos que ningún predicado con nombre
      cubre, que en trabajo real aparecen más de lo que parece: «polígonos que se tocan por
      una línea y no solo por un punto», por ejemplo, es un patrón que se escribe a mano y no
      tiene función propia. La tabla siguiente es la referencia.</p>

      <div class="tabla-caja">
        <table>
          <caption>Las cinco relaciones canónicas entre dos polígonos, con su matriz DE-9IM
            y el predicado que las nombra.</caption>
          <thead><tr><th scope="col">Relación</th><th scope="col">DE-9IM</th>
            <th scope="col">Predicado</th></tr></thead>
          <tbody>
{''.join(f'            <tr><th scope="row">{c}</th><td><code>{m}</code></td><td><code>{p}()</code></td></tr>' + chr(10) for c, m, p in zip(_de['caso'], _de['matriz'], _de['predicado']))}          </tbody>
        </table>
      </div>

{sim('buffer', 'El mismo radio de 1 000 m, pedido en tres sistemas',
     'El área verdadera se mide sobre el elipsoide tras deshacer la proyección.')}
      <p>Y una operación que junta todo lo del capítulo en una línea: el <em>buffer</em>. Un
      radio de mil metros pedido sobre EPSG:9377 da un círculo de
      {firma(n(_bf['m9377_area_km2'], 5), ' km²')}, que es \\(\\pi\\) como debe ser. El mismo
      radio pedido sobre EPSG:3857 da un círculo que sobre el terreno mide
      {firma(n(_bf['m3857_radio_real_m'], 2), ' m')} de radio, no mil: Web&nbsp;Mercator infla
      la escala a esta latitud y el buffer hereda la inflación. <strong>Un buffer no mide lo
      que dice salvo que el CRS sea métrico y adecuado al sitio.</strong></p>

{tabs('Validar y relacionar',
      '''lazo &lt;- st_sfc(st_polygon(list(rbind(c(0,0), c(2,2), c(2,0), c(0,2), c(0,0)))))
st_is_valid(lazo)
#&gt; [1] FALSE
as.numeric(st_area(lazo))
#&gt; [1] 0
sum(as.numeric(st_area(st_make_valid(lazo))))
#&gt; [1] 2

A &lt;- st_sfc(st_polygon(list(rbind(c(0,0), c(4,0), c(4,4), c(0,4), c(0,0)))))
B &lt;- st_sfc(st_polygon(list(rbind(c(2,2), c(6,2), c(6,6), c(2,6), c(2,2)))))
st_relate(A, B)[1]
#&gt; [1] "''' + _de['matriz'][2] + '''"''',
      '''from shapely.geometry import Polygon
from shapely.validation import make_valid
lazo = Polygon([(0,0), (2,2), (2,0), (0,2)])
print(lazo.is_valid, lazo.area)
#&gt; False 0.0
print(make_valid(lazo).area)
#&gt; 2.0

A = Polygon([(0,0), (4,0), (4,4), (0,4)])
B = Polygon([(2,2), (6,2), (6,6), (2,6)])
print(A.relate(B))
#&gt; ''' + _de['matriz'][2])}
      <p>Queda un último frente, y es el que aparece cuando el dato deja de caber en la
      memoria: cómo se organiza el espacio para poder buscar en él. El módulo 11 cierra el
      capítulo por ahí.</p>
""" + CIERRE


# =====================================================================
# MÓDULO 11 · Ingeniería de datos geoespaciales
# =====================================================================
_j, _gh = ig["join"], ig["geohash"]
_n5, _n6, _n7 = _gh["niveles"][1], _gh["niveles"][2], _gh["niveles"][3]
_fr = {f["longitud"]: f for f in _gh["frontera"]}
_TABLA_GEOHASH = "".join(
    fila(niv["longitud"], ent(niv["n_celdas"]),
         n(niv["celda_ancho_km"], 3) + " × " + n(niv["celda_alto_km"], 3) + " km",
         n(_fr[niv["longitud"]]["pct_distinto"]) + " %")
    for niv in _gh["niveles"][1:4])
MOD11 = cabecera(
    11, "Ingeniería de datos geoespaciales", "Spatial indexes, joins and geohash",
    "Entender por qué una unión espacial es rápida, y qué se pierde al indexar el espacio con texto."
) + f"""
      <p>Este es el módulo de ciencia de datos del capítulo —el plan del curso permite uno por
      capítulo, y este es el suyo—. La pregunta es de ingeniería: cuando hay que cruzar
      millones de puntos con miles de polígonos, ¿cómo se hace sin comparar todo con todo?</p>

      <p>La respuesta clásica es el <strong>índice espacial</strong>. En vez de evaluar el
      predicado exacto para cada par, se guarda la caja envolvente de cada geometría en un
      árbol y se descartan de golpe todos los pares cuyas cajas ni se tocan. El predicado caro
      solo se evalúa sobre los supervivientes. Sobre la unión de las {ent(_j['n_puntos'])}
      sedes con las {ent(_j['n_poligonos'])} localidades de Bogotá:</p>

      <div class="tabla-caja">
        <table>
          <caption>Lo que el índice ahorra en una unión espacial.</caption>
          <thead><tr><th scope="col">Etapa</th><th scope="col">Pares evaluados</th></tr></thead>
          <tbody>
            <tr><th scope="row">Fuerza bruta (todos contra todos)</th><td>{ent(_j['pares_fuerza_bruta'])}</td></tr>
            <tr><th scope="row">Tras el filtro de cajas envolventes</th><td>{ent(_j['pares_tras_cajas'])}</td></tr>
            <tr><th scope="row">Aciertos exactos</th><td>{ent(_j['aciertos_exactos'])}</td></tr>
          </tbody>
        </table>
      </div>

      <p>El filtro deja {firma(n(_j['reduccion'], 2), '×')} menos pares que evaluar, y esa
      razón crece con el tamaño del problema: es la diferencia entre un cálculo instantáneo y
      uno que no termina. Por eso <code>st_join</code> es rápido sin que haya que pedírselo, y
      por eso conviene saber que lo es <em>por esto</em> — el día que el índice no se pueda
      construir, la operación cambia de categoría.</p>

      <p>La segunda idea es distinta y más moderna: en vez de indexar el espacio con un árbol,
      <strong>codificarlo con texto</strong>. El <em>geohash</em> parte el mundo en dos por la
      longitud, luego en dos por la latitud, y así alternando; cada bit divide, y los bits se
      agrupan de cinco en cinco en un alfabeto de {firma(str(_gh['base']))} caracteres. El
      resultado es que <strong>el prefijo es la celda</strong>: dos puntos con el mismo
      prefijo de seis caracteres están en la misma celda de unos
      {n(_n6['celda_ancho_km'], 2)}&nbsp;×&nbsp;{n(_n6['celda_alto_km'], 2)}&nbsp;km, y eso se
      puede consultar con un <code>LIKE</code> en cualquier base de datos, sin geometría.</p>

{sim('geohash', 'La celda de geohash, según cuántos caracteres',
     'Medido sobre las ' + ent(po['n_sedes']) + ' sedes de Bogotá.')}
      <p>El mapa siguiente pinta las celdas de longitud 5 sobre Bogotá, coloreadas por cuántas
      sedes cae en cada una. Fíjate en que son rectángulos alineados con los meridianos y
      paralelos, no unidades administrativas: el geohash no sabe nada de la ciudad.</p>

{mapa_html('cap2-geohash', 'Celdas de geohash de longitud 5 sobre las sedes de Bogotá')}
      <p>Y aquí está el precio, que es la razón de que exista H3 y otros esquemas
      alternativos. <strong>La proximidad en el texto no es la proximidad en el
      espacio.</strong> Dos puntos vecinos pueden caer a lados distintos de un corte y no
      compartir ni el primer carácter. Medido sobre las sedes, cuya distancia mediana al
      vecino más próximo es de {firma(n(_gh['d_vecino_mediana_m'], 1), ' m')}:</p>

      <div class="tabla-caja">
        <table>
          <caption>Sedes cuyo vecino más próximo cae en otra celda de geohash.</caption>
          <thead><tr><th scope="col">Longitud</th><th scope="col">Celdas</th>
            <th scope="col">Tamaño de celda</th><th scope="col">Vecino en otra celda</th></tr></thead>
          <tbody>
{_TABLA_GEOHASH}          </tbody>
        </table>
      </div>

      <p>Con seis caracteres, el {firma(n(_fr[6]['pct_distinto']) + ' %')} de las sedes tiene
      a su vecino más próximo en otra celda; con siete, el
      {firma(n(_fr[7]['pct_distinto']) + ' %')}. Cuanto más fina la rejilla, más pares
      cercanos quedan partidos. Un sistema que use el prefijo del geohash como «están cerca»
      se equivoca en esa proporción, y se equivoca justo en los bordes, que es donde más
      duele. <strong>Es el MAUP otra vez</strong>, con otra ropa: una partición arbitraria del
      espacio impuesta sobre un fenómeno que no la respeta. El capítulo 3 lo desarrolla.</p>

      <p>Los esquemas jerárquicos hexagonales como el H3 de Uber existen para mitigar
      exactamente esto —un hexágono tiene todos sus vecinos a la misma distancia del centro,
      un rectángulo no—, pero no lo eliminan: mientras haya celdas habrá bordes, y mientras
      haya bordes habrá vecinos partidos.</p>

{tabs('Índices y geohash',
      '''cole &lt;- st_read("datos/procesado/bogota_colegios.gpkg", quiet = TRUE)
locs &lt;- st_read("datos/procesado/bogota_localidades.gpkg", quiet = TRUE)
nrow(cole) * nrow(locs)
#&gt; [1] ''' + str(_j['pares_fuerza_bruta']) + '''
sum(lengths(st_within(cole, locs)))
#&gt; [1] ''' + str(_j['aciertos_exactos']),
      '''cole = gpd.read_file("datos/procesado/bogota_colegios.gpkg")
locs = gpd.read_file("datos/procesado/bogota_localidades.gpkg")
print(len(cole) * len(locs))
#&gt; ''' + str(_j['pares_fuerza_bruta']) + '''
print(len(gpd.sjoin(cole, locs, predicate="within")))
#&gt; ''' + str(_j['aciertos_exactos']))}
      <p>Con esto el capítulo ha recorrido el camino entero: de la forma de la Tierra a la
      celda de una base de datos, midiendo en cada escalón lo que cuesta equivocarse. El
      módulo 12 lo pone a prueba.</p>
""" + CIERRE


# =====================================================================
# MÓDULO 12 · Autoevaluación y ejercicios guiados
# =====================================================================
def valor_paso(v):
    """El valor de un paso de solución, formateado SEGÚN SU TIPO.

    El mismo arreglo que el capítulo 1, y por el mismo motivo: el `else`
    metía por un solo embudo medidas y conteos, y el capítulo publicaba
    «2209.00000» sedes, «43.00000» filas y —lo más delator— «0.00000»
    falsos positivos. Cinco decimales sobre un conteo no comunican
    precisión: comunican que nadie miró.

    No es aflojar la regla de los cinco decimales, que está MEDIDA
    (`mide_punto_ciego.py`) y se mantiene intacta para las medidas. Es
    dejar de aplicársela a lo que no es una medida. `jsonlite` ya escribe
    `43` para un entero y `1.611682076` para un doble, así que Python los
    lee como `int` y `float`: la distinción venía hecha y se ignoraba.
    """
    if isinstance(v, str):
        return v
    if isinstance(v, list):
        return ", ".join(valor_paso(x) for x in v)
    if isinstance(v, int):          # conteos: 2 209 sedes, 43 filas, 0 falsos positivos
        return ent(v)
    if isinstance(v, float):        # medidas: cinco decimales, como manda D10
        return n(v)
    return str(v)


def ejercicio(k, e):
    """Un ejercicio guiado, con su pista y su solución calculada.

    El marcado es el del capítulo 1 y no un `<details>`: el motor de la
    plantilla espera botones con `aria-expanded`/`aria-controls`, y un
    `<details>` deja esa comprobación de accesibilidad sin sujeto —el
    auditor de prosa lo cazó, informando «0 botones».
    """
    pasos = "\n".join(
        f"""            <tr><th scope="row">{p['paso']}</th><td>{
            valor_paso(p['valor'])}</td></tr>"""
        for p in e["pasos"])
    return f"""
        <div class="ejercicio-guiado">
          <p class="ejercicio-enunciado"><span class="ejercicio-numero">{k}.</span><strong>{e['titulo']}.</strong>
            {e['enunciado'].replace('`', '')}</p>
          <div class="ejercicio-acciones">
            <button type="button" class="ejercicio-boton" aria-expanded="false" aria-controls="cap2-e{k}-sol">
              <i class="fas fa-key" aria-hidden="true"></i> Solución <i class="fas fa-chevron-down" aria-hidden="true"></i>
            </button>
          </div>
          <div class="ejercicio-panel solucion" id="cap2-e{k}-sol" hidden>
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


MOD12 = cabecera(
    12, "Autoevaluación y ejercicios guiados", "Check yourself",
    "Comprobar lo aprendido y resolver cinco problemas completos con su solución calculada."
) + f"""
      <p>Ocho preguntas sobre lo que el capítulo ha medido. No hay ninguna que se conteste
      recordando una definición: todas piden decidir algo, que es para lo que sirve saber esto.
      Cada opción, acertada o no, viene con su explicación y con el módulo al que volver.</p>

{quiz_html('cap2-final', 'Autoevaluación del capítulo 2',
           'Ocho preguntas sobre los once módulos anteriores.')}

      <p>Y cinco ejercicios guiados. Los cinco parten de datos que ya tienes en el curso y los
      cinco tienen la solución calculada en R, paso a paso: la idea es que intentes cada uno
      antes de abrirla, porque el valor está en el camino y no en la cifra final. Son cinco y
      no cuatro porque este capítulo cubre dos semanas de clase.</p>

{''.join(ejercicio(k, S[f'e{k}']) for k in range(1, 6))}
      <p>Con esto cierra el capítulo 2. El capítulo 3 da el paso siguiente: ya sabes poner el
      dato en su sitio y medirlo bien, y ahora toca <em>dibujarlo</em> — y descubrir que el
      mismo dato bien puesto produce mapas que dicen cosas opuestas.</p>

      <div class="definition">
        <h3>De dónde sale cada cosa</h3>
        <p>Los límites municipales y departamentales vienen del Marco Geoestadístico Nacional
        del DANE; las sedes educativas de Bogotá, de la <strong>Secretaría de Educación del
        Distrito</strong>; las estaciones climáticas, del <strong>IDEAM</strong>; y la fuente
        nacional de sedes que el módulo 9 cita como caso descartado, del
        <strong>Ministerio de Educación Nacional</strong>. Los sistemas de referencia
        colombianos son los que fija el <strong>IGAC</strong>. La formulación de la indicatriz
        que este capítulo usa está en <strong>Snyder</strong> (1987), <em>Map Projections — A
        Working Manual</em>, pp. 20-24, y la matriz de relaciones es la del estándar
        <strong>OGC</strong> Simple Features.</p>
        <p style="margin-bottom:0;">Y la continuidad: el <a href="capitulo-1-datos-espaciales.html">capítulo 1</a>
        presentó los tres tipos de dato espacial y la primera ley de Tobler; el capítulo 3
        toma el relevo con la cartografía y el MAUP.</p>
      </div>
""" + CIERRE


MODULOS = MOD1 + MOD2 + MOD3 + MOD4 + MOD5 + MOD6 + MOD7 + MOD8 + MOD9 + MOD10 + MOD11 + MOD12

# =====================================================================
# courseData + los datos del precálculo
# =====================================================================
TITULOS = [
    ("La Tierra no es plana ni una esfera", "Geoide, elipsoide y datum"),
    ("Latitud y longitud no son cartesianas", "Cuánto mide un grado"),
    ("Proyectar es elegir qué destruir", "Tissot y las tres familias"),
    ("EPSG en la práctica", "4326, 3857, 3116 y 9377"),
    ("Reproyectar no es reetiquetar", "st_transform vs st_set_crs"),
    ("Medir sobre la Tierra", "s2, GEOS y el elipsoide"),
    ("Formatos vectoriales", "Shapefile, GeoPackage, GeoJSON"),
    ("De un CSV a un objeto sf", "La trampa del orden lon/lat"),
    ("Error posicional, y quién lo paga", "El sesgo de la geocodificación"),
    ("Validación topológica", "st_is_valid y DE-9IM"),
    ("Ingeniería de datos geoespaciales", "Índices, join y geohash"),
    ("Autoevaluación y ejercicios", "8 preguntas y 5 ejercicios"),
]
COURSE_DATA = (
    "    const courseData = {\n      modules: [\n"
    + "".join(f"        {{ id: {i + 1}, title: {json.dumps(t, ensure_ascii=False)}, "
              f"subtitle: {json.dumps(s, ensure_ascii=False)} }},\n"
              for i, (t, s) in enumerate(TITULOS))
    + "      ]\n    };\n\n"
    + "    // Todas las cifras del capítulo, tal como salieron del precálculo.\n"
    + "    // El JavaScript no lleva ninguna escrita: las saca de aquí.\n"
    + "    const DATOS_CAP2 = " + json.dumps(D, ensure_ascii=False) + ";\n"
    + "    const SOL_CAP2 = " + json.dumps(S, ensure_ascii=False) + ";\n"
)


# =====================================================================
# Los mapas
# =====================================================================
def geomapa(ident, clave, paleta=None, etiqueta=None, extra=""):
    """Un registro de GEOMAPAS con su fuente como LITERAL (ver cap. 1)."""
    partes = [f"      fuente: {json.dumps(M[clave], ensure_ascii=False)}"]
    if paleta:
        partes.append(f"      paleta: '{paleta}'")
    if etiqueta:
        partes.append(f"      etiqueta: '{etiqueta}'")
    if extra:
        partes.append(extra)
    return f"    GEOMAPAS['{ident}'] = {{\n" + ",\n".join(partes) + "\n    };\n"


VISTAS_MUNDO = """      controles: function (d) {
        return d.vistas.map((v, i) => ({ etiqueta: v.nombre, valor: i }));
      },
      alCambiar: function (valor, o) { o.vista = Number(valor); }"""

GEOMAPAS_JS = (
    "    // ----------------------------------------------------------------\n"
    "    // Los mapas del capítulo 2. La geometría llega cuantizada desde\n"
    "    // precalculo/geo.R, los cortes de clase los calculó classInt en R y\n"
    "    // las indicatrices de Tissot vienen medidas por diferencias finitas\n"
    "    // y descomposición en valores singulares — el navegador no calcula\n"
    "    // ni una de esas cosas, solo las dibuja.\n"
    "    // ----------------------------------------------------------------\n"
    + geomapa("cap2-proyecciones", "proyecciones_mundo",
              etiqueta="Cambia de proyección y compara las elipses: redondas = sin deformación angular; grandes = área inflada.")
    + geomapa("cap2-proyecciones-co", "proyecciones_colombia",
              etiqueta="Colombia bajo Web Mercator y sus dos sistemas oficiales.")
    + geomapa("cap2-error-3116", "error_3116", paleta="divergente",
              etiqueta="Exceso de área de EPSG:3116 frente al área geodésica, por departamento.",
              extra="""      tabla: function (d) {
        const filas = d.valor.map((v, i) => `<tr><th scope="row">${(d.etiquetas || [])[i] || (i + 1)}</th>`
          + `<td>${v.toFixed(5)}</td><td>${d.clase[i]}</td></tr>`).join('');
        return `<table><caption>${d.titulo}: valor y clase de cada unidad.</caption><thead><tr>`
          + `<th scope="col">Unidad</th><th scope="col">${d.leyenda}</th>`
          + `<th scope="col">Clase</th></tr></thead><tbody>${filas}</tbody></table>`;
      }""")
    + geomapa("cap2-invertidos", "invertidos",
              etiqueta="Rombos: las 361 estaciones donde están. Puntos: las mismas con lon y lat intercambiadas.")
    + geomapa("cap2-degradado", "degradado",
              etiqueta="El redondeo a dos decimales convierte un patrón puntual en una retícula.")
    + geomapa("cap2-sesgo", "sesgo_localidades", paleta="naranja",
              etiqueta="Promedio sobre 200 realizaciones de un error posicional de 150 m.")
    + geomapa("cap2-geohash", "geohash", paleta="verde",
              etiqueta="Las celdas son rectángulos de la rejilla del geohash, no unidades administrativas.")
)

# =====================================================================
# Los simuladores
# =====================================================================
# Ninguno calcula nada pesado: todo viene precalculado en R (D9 del plan).
# Y NINGUNO lleva una cifra escrita: todas salen de DATOS_CAP2.
SIMULADORES_JS = r"""
    // EL CONTRATO DEL MOTOR: un simulador DEVUELVE la lista de gráficos
    // de Chart.js que ha creado, y `iniciarSimuladores()` los mete en
    // `graficosActivos` para destruirlos al cambiar de módulo. No hay
    // ninguna función `registrar*`: escribirla de memoria costó un
    // ReferenceError que se llevó por delante `iniciarSimuladores()`
    // entero —y con él todos los simuladores del módulo, no solo el que
    // fallaba—. Es el mismo modo de fallo del defecto nº 2 de A.12.
    const D2 = DATOS_CAP2;
    const n5 = (x, d) => Number(x).toFixed(d == null ? 5 : d);
    const miles = x => Math.round(Number(x)).toLocaleString('es-ES').replace(/\./g, '\u202f');

    function lectura(raiz, filas) {
      const caja = raiz.querySelector('.simulador-lectura');
      if (!caja) return;
      caja.innerHTML = filas.map(f =>
        `<span class="lectura-item"><span class="lectura-etiqueta">${f[0]}</span>` +
        `<span class="lectura-valor">${f[1]}</span></span>`).join('');
    }

    function botonera(raiz, opciones, alPulsar) {
      const cont = raiz.querySelector('.simulador-controles');
      if (!cont) return;
      cont.innerHTML = '';
      opciones.forEach((op, i) => {
        const b = document.createElement('button');
        b.className = 'sim-btn' + (i === 0 ? ' active' : '');
        b.textContent = op.etiqueta;
        b.onclick = () => {
          cont.querySelectorAll('.sim-btn').forEach(x => x.classList.remove('active'));
          b.classList.add('active');
          alPulsar(op.valor);
        };
        cont.appendChild(b);
      });
    }

    // --- Módulo 1 · los dos radios de curvatura ----------------------
    SIMULADORES['radios'] = function (raiz) {
      const r = D2.elipsoide.radios;
      const ctx = raiz.querySelector('canvas').getContext('2d');
      const g = new Chart(ctx, {
        type: 'line',
        data: {
          labels: r.lat.map(v => n5(v, 2) + '\u00b0'),
          datasets: [
            { label: 'N (primer vertical), km', data: r.N.map(v => v / 1000),
              borderColor: '#1a7358', backgroundColor: 'rgba(26,115,88,.1)', tension: .3 },
            { label: 'M (meridiano), km', data: r.M.map(v => v / 1000),
              borderColor: '#FF6600', backgroundColor: 'rgba(255,102,0,.1)', tension: .3 }
          ]
        },
        options: { responsive: true, maintainAspectRatio: false,
          scales: { y: { title: { display: true, text: 'radio de curvatura (km)' } },
                    x: { title: { display: true, text: 'latitud' } } } }
      });
      lectura(raiz, [
        ['N − M en el ecuador', n5((r.N[0] - r.M[0]) / 1000, 3) + ' km'],
        ['N / M en el ecuador', n5(r.razon_N_M[0])],
        ['N / M a 80\u00b0', n5(r.razon_N_M[r.razon_N_M.length - 1])]
      ]);
      return [g];
    };

    // --- Módulo 2 · cuánto mide un grado -----------------------------
    SIMULADORES['grados'] = function (raiz) {
      const g0 = D2.grados;
      const ctx = raiz.querySelector('canvas').getContext('2d');
      const g = new Chart(ctx, {
        type: 'line',
        data: {
          labels: g0.lat.map(v => n5(v, 2) + '\u00b0'),
          datasets: [
            { label: 'un grado de longitud (m)', data: g0.lon_m_elipsoide,
              borderColor: '#FF6600', backgroundColor: 'rgba(255,102,0,.1)', tension: .3 },
            { label: 'un grado de latitud (m)', data: g0.lat_m_elipsoide,
              borderColor: '#1a7358', backgroundColor: 'rgba(26,115,88,.1)', tension: .3 },
            { label: 'un grado de latitud SOBRE LA ESFERA (m)', data: g0.lat_m_esfera,
              borderColor: '#8a3d00', borderDash: [6, 4], tension: .3, pointRadius: 0 }
          ]
        },
        options: { responsive: true, maintainAspectRatio: false,
          scales: { y: { beginAtZero: true, title: { display: true, text: 'metros' } },
                    x: { title: { display: true, text: 'latitud' } } } }
      });
      lectura(raiz, [
        ['longitud, ecuador', n5(g0.lon_m_elipsoide[0], 2) + ' m'],
        ['longitud, 80\u00b0', n5(g0.lon_m_elipsoide[g0.lon_m_elipsoide.length - 1], 2) + ' m'],
        ['Bogot\u00e1 / Oslo', n5(g0.bogota_vs_oslo, 4) + '\u00d7'],
        ['recorrido de la latitud', n5(g0.lat_elipsoide_recorrido_m, 2) + ' m']
      ]);
      return [g];
    };

    // --- Módulo 5 · reetiquetar contra reproyectar -------------------
    SIMULADORES['etiquetar'] = function (raiz) {
      const e = D2.etiquetar;
      const ctx = raiz.querySelector('canvas').getContext('2d');
      const g = new Chart(ctx, {
        type: 'bar',
        data: {
          labels: ['vértices movidos', 'máximo desplazamiento (log\u2081\u2080)'],
          datasets: [
            { label: 'st_set_crs (reetiquetar)',
              data: [0, 0], backgroundColor: '#8a3d00' },
            { label: 'st_transform (reproyectar)',
              data: [e.transform_n_movidas, Math.log10(Math.max(e.transform_max_delta, 1))],
              backgroundColor: '#1a7358' }
          ]
        },
        options: { responsive: true, maintainAspectRatio: false,
          scales: { y: { beginAtZero: true } } }
      });
      lectura(raiz, [
        ['vértices de la capa', miles(e.n_vertices)],
        ['movidos por set_crs', '0'],
        ['movidos por transform', miles(e.transform_n_movidas)],
        ['«longitud» tras reetiquetar', miles(e.lon_absurda) + '\u00b0']
      ]);
      return [g];
    };

    // --- Módulo 6 · la misma geometría, tres medidas -----------------
    SIMULADORES['medir'] = function (raiz) {
      const m = D2.medir.colombia;
      const ctx = raiz.querySelector('canvas').getContext('2d');
      const g = new Chart(ctx, {
        type: 'bar',
        data: {
          labels: ['elipsoide (lwgeom)', 'esfera (s2)', 'proyectada (9377)'],
          datasets: [{ label: 'área de Colombia (km\u00b2)',
            data: [m.area_elipsoide_km2, m.area_esfera_km2, m.area_9377_km2],
            backgroundColor: ['#1a7358', '#FF6600', '#7cc0aa'] }]
        },
        options: { responsive: true, maintainAspectRatio: false,
          plugins: { legend: { display: false } },
          scales: { y: { beginAtZero: false, title: { display: true, text: 'km\u00b2' } } } }
      });
      lectura(raiz, [
        ['la esfera infla', miles(m.dif_esfera_km2) + ' km\u00b2'],
        ['en porcentaje', n5(m.dif_esfera_pct) + ' %'],
        ['equivale a', miles(D2.medir.municipios.equivalente_a_municipios) + ' municipios'],
        ['9377 se queda a', n5(Math.abs(m.dif_9377_pct)) + ' %']
      ]);
      return [g];
    };

    // --- Módulo 7 · los tres formatos --------------------------------
    SIMULADORES['formatos'] = function (raiz) {
      const f = D2.formatos;
      const ctx = raiz.querySelector('canvas').getContext('2d');
      let modo = 'muestra';
      let g = null;
      function pinta() {
        if (g) { g.destroy(); }
        const datos = modo === 'muestra'
          ? [f.shapefile.bytes / 1024, f.gpkg.bytes / 1024, f.geojson.bytes / 1024]
          : [null, f.pais.gpkg_mb * 1024, f.pais.geojson_mb * 1024];
        g = new Chart(ctx, {
          type: 'bar',
          data: { labels: ['Shapefile', 'GeoPackage', 'GeoJSON'],
            datasets: [{ label: modo === 'muestra' ? 'KB (60 municipios)' : 'KB (país entero)',
              data: datos, backgroundColor: ['#8a3d00', '#1a7358', '#FF6600'] }] },
          options: { responsive: true, maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: { y: { beginAtZero: true, title: { display: true, text: 'KB' } } } }
        });
        lectura(raiz, modo === 'muestra' ? [
          ['archivos del shapefile', String(f.shapefile.n_archivos)],
          ['campos desfigurados', f.shapefile.n_campos_largos + ' de ' + f.shapefile.n_campos],
          ['GeoJSON / Shapefile', n5(f.geojson.razon_sobre_shp, 3) + '\u00d7']
        ] : [
          ['GeoPackage', n5(f.pais.gpkg_mb, 1) + ' MB'],
          ['GeoJSON', n5(f.pais.geojson_mb, 1) + ' MB'],
          ['razón', n5(f.pais.razon, 3) + '\u00d7']
        ]);
      }
      botonera(raiz, [{ etiqueta: '60 municipios', valor: 'muestra' },
                      { etiqueta: 'el país entero', valor: 'pais' }],
               v => { modo = v; pinta(); });
      pinta();
      // Este simulador REHACE el gráfico al pulsar, así que no puede
      // devolver la instancia: devuelve un envoltorio que destruye la
      // que esté viva en ese momento. Sin él, `graficosActivos` guardaría
      // el primero y los siguientes se acumularían.
      return [{ destroy: () => { if (g) g.destroy(); } }];
    };

    // --- Módulo 8 · el intercambio de columnas -----------------------
    SIMULADORES['invertir'] = function (raiz) {
      const c = D2.csv_sf;
      const ctx = raiz.querySelector('canvas').getContext('2d');
      const g = new Chart(ctx, {
        type: 'bar',
        data: { labels: c.destino.nombre,
          datasets: [{ label: 'estaciones que aterrizan ahí', data: c.destino.n,
            backgroundColor: ['#8a3d00', '#FF6600', '#1a7358', '#7cc0aa'] }] },
        options: { responsive: true, maintainAspectRatio: false, indexAxis: 'y',
          plugins: { legend: { display: false } },
          scales: { x: { beginAtZero: true } } }
      });
      lectura(raiz, [
        ['estaciones', miles(c.n)],
        ['desplazamiento medio', miles(c.desplazamiento_km_med) + ' km'],
        ['el menos desplazado', miles(c.desplazamiento_km_min) + ' km'],
        ['caen en Colombia', String(c.n_en_colombia)]
      ]);
      return [g];
    };

    // --- Módulo 9 · degradar la posición -----------------------------
    SIMULADORES['degradar'] = function (raiz) {
      const p = D2.posicional;
      const ctx = raiz.querySelector('canvas').getContext('2d');
      const g = new Chart(ctx, {
        type: 'line',
        data: {
          labels: p.ruidos.map(r => '\u03c3 = ' + r.sigma_m + ' m'),
          datasets: [{ label: '% de sedes que cambian de localidad',
            data: p.ruidos.map(r => r.pct_cambian),
            borderColor: '#FF6600', backgroundColor: 'rgba(255,102,0,.15)',
            fill: true, tension: .25 }]
        },
        options: { responsive: true, maintainAspectRatio: false,
          scales: { y: { beginAtZero: true, title: { display: true, text: '%' } } } }
      });
      lectura(raiz, [
        ['tasa global a 150 m', n5(p.sesgo.tasa_global_pct) + ' %'],
        ['error de Monte Carlo', '\u00b1 ' + n5(p.sesgo.emc_global_pct)],
        ['la mejor localidad', n5(p.sesgo.tasa_min_pct) + ' %'],
        ['la peor', n5(p.sesgo.tasa_max_pct) + ' %']
      ]);
      return [g];
    };

    // --- Módulo 10 · las cinco relaciones DE-9IM ---------------------
    SIMULADORES['de9im'] = function (raiz) {
      const t = D2.topologia.de9im;
      const canvas = raiz.querySelector('canvas');
      const ctx = canvas.getContext('2d');
      // Las figuras son las MISMAS que midió R; se declaran aquí porque
      // son geometría de demostración, no dato: el número que importa
      // —la matriz— sí viene del precálculo.
      const FIG = {
        disjuntos: [[6, 6], [8, 6], [8, 8], [6, 8]],
        tocan: [[4, 0], [6, 0], [6, 4], [4, 4]],
        solapan: [[2, 2], [6, 2], [6, 6], [2, 6]],
        contiene: [[1, 1], [3, 1], [3, 3], [1, 3]],
        iguales: [[0, 0], [4, 0], [4, 4], [0, 4]]
      };
      const A = [[0, 0], [4, 0], [4, 4], [0, 4]];
      let cual = t.caso[0];
      function pinta() {
        const dpr = window.devicePixelRatio || 1;
        const w = canvas.parentElement.clientWidth || 400;
        canvas.width = w * dpr; canvas.height = 260 * dpr;
        canvas.style.height = '260px';
        ctx.setTransform(1, 0, 0, 1, 0, 0);
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        const s = Math.min((canvas.width - 20 * dpr) / 9, (canvas.height - 20 * dpr) / 9);
        const ox = (canvas.width - 9 * s) / 2, oy = canvas.height - 10 * dpr;
        const px = v => ox + v * s, py = v => oy - v * s;
        const poli = (pts, relleno, borde) => {
          ctx.beginPath();
          pts.forEach((p, i) => i ? ctx.lineTo(px(p[0]), py(p[1])) : ctx.moveTo(px(p[0]), py(p[1])));
          ctx.closePath();
          ctx.fillStyle = relleno; ctx.fill();
          ctx.strokeStyle = borde; ctx.lineWidth = 2 * dpr; ctx.stroke();
        };
        poli(A, 'rgba(26,115,88,.35)', '#012820');
        poli(FIG[cual], 'rgba(255,102,0,.35)', '#8a3d00');
        const i = t.caso.indexOf(cual);
        lectura(raiz, [
          ['relación', cual],
          ['DE-9IM', t.matriz[i]],
          ['predicado', t.predicado[i] + '()']
        ]);
      }
      botonera(raiz, t.caso.map(c => ({ etiqueta: c, valor: c })),
               v => { cual = v; pinta(); });
      pinta();
      // Sin ResizeObserver a propósito: el motor no tiene dónde
      // registrarlo y un observador que sobrevive al cambio de módulo es
      // una fuga — T0.3 midió esa fuga y la dejó en cero, y no se
      // reintroduce por una comodidad.
      return [];
    };

    // --- Módulo 10 · el buffer según el CRS --------------------------
    SIMULADORES['buffer'] = function (raiz) {
      const b = D2.topologia.buffer;
      const ctx = raiz.querySelector('canvas').getContext('2d');
      const g = new Chart(ctx, {
        type: 'bar',
        data: {
          labels: ['EPSG:9377 (métrico)', 'EPSG:3857 (Web Mercator)', 'grados sobre 4326'],
          datasets: [{ label: 'área real del «buffer de 1 000 m» (km\u00b2)',
            data: [b.m9377_area_km2, b.m3857_area_real_km2, b.grados_area_km2],
            backgroundColor: ['#1a7358', '#FF6600', '#8a3d00'] }]
        },
        options: { responsive: true, maintainAspectRatio: false,
          plugins: { legend: { display: false } },
          scales: { y: { beginAtZero: true, title: { display: true, text: 'km\u00b2' } } } }
      });
      lectura(raiz, [
        ['9377, radio real', '1000.00 m'],
        ['3857, radio real', n5(b.m3857_radio_real_m, 2) + ' m'],
        ['9377, área', n5(b.m9377_area_km2, 5) + ' km\u00b2'],
        ['\u03c0', n5(Math.PI, 5)]
      ]);
      return [g];
    };

    // --- Módulo 11 · la celda del geohash ----------------------------
    SIMULADORES['geohash'] = function (raiz) {
      const gh = D2.ingenieria.geohash;
      const fr = {}; gh.frontera.forEach(f => { fr[f.longitud] = f.pct_distinto; });
      const ctx = raiz.querySelector('canvas').getContext('2d');
      const g = new Chart(ctx, {
        type: 'bar',
        data: {
          labels: gh.niveles.map(v => v.longitud + ' caracteres'),
          datasets: [
            { type: 'bar', label: 'lado de la celda (km)',
              data: gh.niveles.map(v => v.celda_ancho_km),
              backgroundColor: '#7cc0aa', yAxisID: 'y' },
            { type: 'line', label: '% con el vecino en otra celda',
              data: gh.niveles.map(v => fr[v.longitud]),
              borderColor: '#FF6600', yAxisID: 'y2', tension: .25 }
          ]
        },
        options: { responsive: true, maintainAspectRatio: false,
          scales: {
            y: { type: 'logarithmic', title: { display: true, text: 'km (log)' } },
            y2: { position: 'right', beginAtZero: true, max: 100,
                  grid: { drawOnChartArea: false },
                  title: { display: true, text: '%' } } } }
      });
      lectura(raiz, [
        ['round-trip', gh.round_trip.n_dentro + ' de ' + gh.round_trip.n_puntos],
        ['vecino al lado más próximo', n5(gh.d_vecino_mediana_m, 1) + ' m'],
        ['con 6 caracteres', n5(fr[6]) + ' % partidos'],
        ['con 7', n5(fr[7]) + ' % partidos']
      ]);
      return [g];
    };
"""

# =====================================================================
# Las dos autoevaluaciones
# =====================================================================
QUIZ_JS = r"""
    // ----------------------------------------------------------------
    // Bloque de mitad de capítulo: cuatro trampas de CRS, después del
    // módulo 6. Es una desviación del molde del capítulo 1 (8 preguntas
    // en total) decidida por Javier el 2026-08-04: el capítulo cubre dos
    // semanas y sus errores son los que se cometen en la práctica.
    // Ninguna cifra está escrita: todas salen de DATOS_CAP2.
    // ----------------------------------------------------------------
    AUTOEVALUACIONES['cap2-trampas'] = [
      {
        tipo: 'opcion', modulo: 5,
        pregunta: 'Recibes un GeoPackage cuyas coordenadas son claramente metros, pero el archivo '
          + 'declara EPSG:4326. Sabes que en realidad está en EPSG:9377. ¿Qué haces?',
        pista: 'Pregúntate qué está mal: ¿las coordenadas, o la etiqueta?',
        opciones: [
          { texto: 'st_set_crs(x, 9377): la etiqueta está mal, las coordenadas están bien.', correcta: true,
            retro: 'Eso es. st_set_crs es la herramienta correcta justo aquí: cuando el dato está bien '
              + 'y lo que miente es el metadato. Si además lo quieres en grados, DESPUÉS st_transform.' },
          { texto: 'st_transform(x, 9377): hay que reproyectar a 9377.', correcta: false,
            retro: 'st_transform tomaría esos metros COMO SI fueran grados y los recalcularía desde ahí. '
              + 'El resultado sería un objeto en 9377 con la geometría destruida. Módulo 5.' },
          { texto: 'Nada: 4326 y 9377 describen el mismo elipsoide.', correcta: false,
            retro: 'Comparten el elipsoide GRS80, sí, pero uno es geográfico y el otro proyectado: '
              + 'las unidades son distintas. Módulo 4.' },
          { texto: 'st_transform(x, 4326) para dejarlo en grados de verdad.', correcta: false,
            retro: 'Mismo problema: partiría de una etiqueta falsa. Primero se corrige la etiqueta. Módulo 5.' }
        ],
        retroAcierto: 'La regla: st_set_crs arregla metadatos, st_transform mueve coordenadas.',
        retroFallo: 'Vuelve al módulo 5: reetiquetar y reproyectar hacen cosas opuestas.'
      },
      {
        tipo: 'numerica', modulo: 4,
        pregunta: 'EPSG:9377 es una transversa de Mercator con factor de escala k = 0,9992. '
          + '¿Cuál es, exactamente, la razón de área MÍNIMA que puede dar sobre Colombia?',
        pista: 'Es conforme: la escala de área es el cuadrado de la lineal.',
        respuesta: 0.998401, tolerancia: 0.00005,
        unidad: '',
        retroAcierto: 'k² = 0,998401. Y el capítulo lo mide sobre los 1 122 municipios: sale '
          + 'exactamente eso, lo que confirma de paso que la referencia de área es la correcta.',
        retroFallo: 'En una proyección conforme a = b, así que s = a². En el meridiano central a = k. Módulo 4.'
      },
      {
        tipo: 'multiple', modulo: 6,
        pregunta: '¿Cuáles de estas afirmaciones sobre st_area() en sf son ciertas? '
          + '(Marca todas las que apliquen.)',
        pista: 'Piensa en qué superficie usa cada camino.',
        opciones: [
          { texto: 'Con sf_use_s2(TRUE) sobre lon/lat, mide sobre una esfera.', correcta: true,
            retro: 'Sí: s2 hace geometría esférica, y sobre Colombia eso infla el área un '
              + n5(DATOS_CAP2.medir.colombia.dif_esfera_pct) + ' %.' },
          { texto: 'Con sf_use_s2(FALSE) y lwgeom instalado, mide sobre el elipsoide.', correcta: true,
            retro: 'Correcto, y es la referencia que este capítulo usa para todas sus razones de área.' },
          { texto: 'Sobre un objeto proyectado a EPSG:9377 devuelve metros cuadrados planos.', correcta: true,
            retro: 'Sí. Y para Colombia se queda a ' + n5(Math.abs(DATOS_CAP2.medir.colombia.dif_9377_pct))
              + ' % del área elipsoidal.' },
          { texto: 'Los tres caminos dan el mismo número si el dato es correcto.', correcta: false,
            retro: 'No: sobre Colombia se separan en ' + Math.round(DATOS_CAP2.medir.colombia.dif_esfera_km2)
              + ' km². Que el dato sea correcto no hace que las superficies coincidan. Módulo 6.' }
        ],
        retroAcierto: 'Tres caminos, tres superficies, tres números. Hay que declarar cuál se usó.',
        retroFallo: 'Módulo 6: el interruptor sf_use_s2() cambia la superficie sobre la que se mide.'
      },
      {
        tipo: 'opcion', modulo: 3,
        pregunta: 'Un colega propone una proyección nueva que, según él, conserva a la vez los ángulos '
          + 'y las áreas en todo el planeta. ¿Qué le contestas?',
        pista: 'Piensa en qué implica ser conforme para la escala de área.',
        opciones: [
          { texto: 'Que es imposible: conforme implica s = a², y s = 1 exigiría escala 1 en todo punto, '
              + 'o sea una isometría, que la curvatura prohíbe.', correcta: true,
            retro: 'Exacto. Es el teorema de Tissot, y el capítulo lo comprueba sobre las seis '
              + 'proyecciones: ninguna sale con las dos banderas.' },
          { texto: 'Que puede funcionar si se limita a una región pequeña.', correcta: false,
            retro: 'En una región pequeña el error se hace despreciable, pero no cero; y la afirmación '
              + 'era «en todo el planeta». Módulo 3.' },
          { texto: 'Que sí, es lo que hace Equal Earth.', correcta: false,
            retro: 'Equal Earth es equivalente (s = 1) pero su deformación angular llega a '
              + n5(DATOS_CAP2.proyecciones.tabla.omega_max_grados[3], 3) + '°. Módulo 3.' },
          { texto: 'Que sí, es lo que hace Mercator.', correcta: false,
            retro: 'Mercator es conforme, y por eso mismo su escala de área llega a '
              + n5(DATOS_CAP2.proyecciones.tabla.s_max[0], 3) + ' en la rejilla. Módulo 3.' }
        ],
        retroAcierto: 'Y es un teorema, no una limitación tecnológica.',
        retroFallo: 'Módulo 3: conforme y equivalente son incompatibles.'
      }
    ];

    // ----------------------------------------------------------------
    // El quiz de ocho del módulo 12.
    // ----------------------------------------------------------------
    AUTOEVALUACIONES['cap2-final'] = [
      {
        tipo: 'opcion', modulo: 1,
        pregunta: 'Un mapa cartográfico colombiano de 1980 se superpone sobre una capa de GPS actual '
          + 'sin reproyectar. ¿Qué se ve?',
        pista: 'Piensa en el datum, no en la proyección.',
        opciones: [
          { texto: 'Un desplazamiento sistemático de unos cientos de metros.', correcta: true,
            retro: 'Sí: el datum Bogotá 1975 desplaza en promedio '
              + n5(DATOS_CAP2.elipsoide.datum.desp_medio_m, 2) + ' m respecto de WGS84.' },
          { texto: 'Nada raro: las coordenadas geográficas son universales.', correcta: false,
            retro: 'Una latitud y una longitud no significan nada sin decir sobre qué datum. Módulo 1.' },
          { texto: 'Un error que crece hacia los bordes del mapa.', correcta: false,
            retro: 'Eso describiría un error de proyección. El de datum es aproximadamente constante. Módulo 1.' },
          { texto: 'Un mensaje de error al cargar la capa.', correcta: false,
            retro: 'Ninguna de las dos capas es inválida: las dos son coordenadas legítimas. Módulo 1.' }
        ],
        retroAcierto: 'Y no hay aviso: por eso hay que mirar el datum antes de superponer nada.',
        retroFallo: 'Módulo 1.'
      },
      {
        tipo: 'opcion', modulo: 2,
        pregunta: 'Calculas la matriz de distancias entre unas estaciones con la fórmula euclídea sobre '
          + 'las columnas de longitud y latitud. La correlación con las distancias geodésicas es '
          + n5(DATOS_CAP2.grados.euclidea.corr) + '. ¿Puedes usarla?',
        pista: '¿Para qué la vas a usar? Esa es la pregunta.',
        opciones: [
          { texto: 'Depende: sirve para ordenar, y falla en cuanto haya un umbral de por medio.', correcta: true,
            retro: 'Exacto, y el ejercicio 4 lo mide: el vecino más próximo no cambia para ninguna '
              + 'estación, y un umbral de vecindad a 200 km discrepa en más de cien pares.' },
          { texto: 'Sí, sin más: una correlación tan alta la valida para cualquier uso.', correcta: false,
            retro: 'Una medida puede ser buenísima en promedio y romper la decisión concreta que tomas '
              + 'con ella. Módulo 2.' },
          { texto: 'No, nunca: los grados no son metros.', correcta: false,
            retro: 'Cierto que no son metros, pero eso no la inutiliza para todo. La respuesta honesta '
              + 'es «depende de para qué». Módulo 2.' },
          { texto: 'Sí, porque Colombia está cerca del ecuador.', correcta: false,
            retro: 'Ayuda, pero no es la razón: el problema no es el tamaño del error sino si tu uso '
              + 'es sensible a él. Módulo 2.' }
        ],
        retroAcierto: 'Ordenar y umbralizar son preguntas distintas, y solo una sobrevive.',
        retroFallo: 'Módulo 2, y el ejercicio 4.'
      },
      {
        tipo: 'grafico', modulo: 3,
        pregunta: 'En el gráfico, cada proyección aparece con su deformación angular máxima y su escala '
          + 'de área. ¿Cuál es la única lectura que el gráfico NO permite hacer?',
        datos: 'proyecciones',
        pista: 'Fíjate en si alguna barra está pegada a cero en las dos cosas.',
        opciones: [
          { texto: 'Que existe una proyección con ω = 0 y s = 1 a la vez.', correcta: true,
            retro: 'Correcto: no existe, y el gráfico lo enseña. Es el teorema de Tissot.' },
          { texto: 'Que Mercator conserva los ángulos.', correcta: false,
            retro: 'Eso sí se lee: su ω máxima es '
              + n5(DATOS_CAP2.proyecciones.tabla.omega_max_grados[0], 5) + '°.' },
          { texto: 'Que Equal Earth conserva las áreas.', correcta: false,
            retro: 'También se lee: su escala de área es 1,000 en toda la rejilla.' },
          { texto: 'Que Robinson no conserva ninguna de las dos.', correcta: false,
            retro: 'Se lee igualmente: es la fila de compromiso.' }
        ],
        retroAcierto: 'Y es un teorema, no una casualidad de estas seis.',
        retroFallo: 'Módulo 3.'
      },
      {
        tipo: 'numerica', modulo: 9,
        pregunta: 'Redondeando a dos decimales las coordenadas geográficas de las '
          + DATOS_CAP2.posicional.n_sedes + ' sedes de Bogotá, ¿cuántas posiciones distintas quedan?',
        pista: 'Dos decimales son algo más de un kilómetro de resolución.',
        respuesta: DATOS_CAP2.posicional.redondeos[2].n_posiciones, tolerancia: 0,
        unidad: 'posiciones',
        retroAcierto: 'Y eso es ' + n5(DATOS_CAP2.posicional.sedes_por_posicion_2dec, 4)
          + ' sedes por posición: la fuente del MEN que el curso descartó tenía exactamente esa densidad.',
        retroFallo: 'Módulo 9: el redondeo convierte un patrón puntual en una retícula.'
      },
      {
        tipo: 'opcion', modulo: 9,
        pregunta: 'Con 150 m de error posicional, la tasa de sedes que cambian de localidad va del '
          + n5(DATOS_CAP2.posicional.sesgo.tasa_min_pct) + ' % al '
          + n5(DATOS_CAP2.posicional.sesgo.tasa_max_pct) + ' % según la localidad. ¿Qué lo explica mejor?',
        pista: 'El capítulo mide una correlación concreta.',
        opciones: [
          { texto: 'La geometría de la unidad: perímetro dividido por área.', correcta: true,
            retro: 'Sí, con correlación de ' + n5(DATOS_CAP2.posicional.sesgo.corr_pearson)
              + '. El sesgo es predecible ANTES de tener el dato.' },
          { texto: 'El estrato socioeconómico de las sedes.', correcta: false,
            retro: 'Es la lectura que uno espera, y el dato no la sostiene: por estrato no hay patrón '
              + 'monótono. Módulo 9.' },
          { texto: 'El número de sedes de cada localidad.', correcta: false,
            retro: 'Cuenta para la precisión de la estimación, no para la tasa. Módulo 9.' },
          { texto: 'Nada en particular: es ruido de la simulación.', correcta: false,
            retro: 'Se midió con ' + DATOS_CAP2.posicional.sesgo.n_replicas + ' réplicas y el error de '
              + 'Monte Carlo es de ' + n5(DATOS_CAP2.posicional.sesgo.emc_global_pct) + ' puntos. Módulo 9.' }
        ],
        retroAcierto: 'Unidades pequeñas y de borde largo pagan más: en casi toda ciudad, las centrales.',
        retroFallo: 'Módulo 9.'
      },
      {
        tipo: 'multiple', modulo: 7,
        pregunta: '¿Qué se pierde al guardar una capa como shapefile? (Marca todas las que apliquen.)',
        pista: 'El capítulo lo midió escribiendo y releyendo una capa real.',
        opciones: [
          { texto: 'Los nombres de campo de más de 10 caracteres.', correcta: true,
            retro: 'Y no se truncan: se desfiguran quitando vocales. '
              + DATOS_CAP2.formatos.shapefile.n_campos_largos + ' de '
              + DATOS_CAP2.formatos.shapefile.n_campos + ' campos en la prueba.' },
          { texto: 'La declaración de la codificación de los textos.', correcta: true,
            retro: 'Sí: sin .cpg, quien lo lea tiene que adivinar, y ahí mueren las tildes.' },
          { texto: 'La condición de archivo único.', correcta: true,
            retro: 'Son ' + DATOS_CAP2.formatos.shapefile.n_archivos + ' archivos, y perder uno rompe la capa.' },
          { texto: 'La geometría, que se simplifica al escribir.', correcta: false,
            retro: 'Eso no: el shapefile guarda los vértices tal cual. Lo que pierde son metadatos '
              + 'y tipos. Módulo 7.' }
        ],
        retroAcierto: 'Por eso este curso guarda todo en GeoPackage.',
        retroFallo: 'Módulo 7.'
      },
      {
        tipo: 'opcion', modulo: 11,
        pregunta: 'Un sistema decide que dos registros «están cerca» si comparten los 6 primeros '
          + 'caracteres de su geohash. ¿Cuál es el problema?',
        pista: 'Piensa en dos puntos separados por un corte de la rejilla.',
        opciones: [
          { texto: 'Que el ' + n5(DATOS_CAP2.ingenieria.geohash.frontera[2].pct_distinto)
              + ' % de las sedes tiene a su vecino más próximo en otra celda.', correcta: true,
            retro: 'Exacto. La proximidad en el texto no es la proximidad en el espacio, y falla '
              + 'justo en los bordes. Es el MAUP con otra ropa.' },
          { texto: 'Que el geohash no es determinista.', correcta: false,
            retro: 'Lo es completamente: mismo punto, mismo código siempre. Módulo 11.' },
          { texto: 'Que las celdas son demasiado grandes para una ciudad.', correcta: false,
            retro: 'Con 6 caracteres miden unos '
              + n5(DATOS_CAP2.ingenieria.geohash.niveles[2].celda_ancho_km, 2) + ' km de lado, '
              + 'que es razonable. El problema son los bordes, no el tamaño. Módulo 11.' },
          { texto: 'Que hay que reconstruirlo si el dato cambia de CRS.', correcta: false,
            retro: 'El geohash se define sobre lon/lat, así que eso no es lo que falla. Módulo 11.' }
        ],
        retroAcierto: 'Y afinar la rejilla lo empeora: con 7 caracteres sube al '
          + n5(DATOS_CAP2.ingenieria.geohash.frontera[3].pct_distinto) + ' %.',
        retroFallo: 'Módulo 11.'
      },
      {
        tipo: 'opcion', modulo: 10,
        pregunta: 'Sumas las áreas de una capa de polígonos que te acaban de enviar y el total sale '
          + 'menor de lo que esperabas. ¿Qué compruebas primero?',
        pista: 'Hay un valor que una geometría rota devuelve sin quejarse.',
        opciones: [
          { texto: 'st_is_valid(): una geometría inválida devuelve área 0 sin dar error.', correcta: true,
            retro: 'Eso es. Es el modo de fallo dominante del curso: la operación que devuelve un '
              + 'valor plausible en vez de fallar.' },
          { texto: 'El CRS, porque seguro está en grados.', correcta: false,
            retro: 'Es una buena segunda comprobación, pero un área en grados cuadrados sale absurda, '
              + 'no «un poco menor». Módulo 10.' },
          { texto: 'Que no falten filas en la tabla de atributos.', correcta: false,
            retro: 'Se vería en el conteo. El cero de una geometría inválida no se ve en ningún sitio. Módulo 10.' },
          { texto: 'La versión de GEOS.', correcta: false,
            retro: 'Muy raramente es eso. Primero lo barato y frecuente: validar. Módulo 10.' }
        ],
        retroAcierto: 'Validar es lo primero que se hace con una capa de fuera, no lo último.',
        retroFallo: 'Módulo 10.'
      }
    ];
"""


# =====================================================================
# El ensamblado
# =====================================================================
def reemplaza_region(texto, abre, cierra, nuevo, que, max_lineas, min_lineas=0):
    """Sustituye entre `abre` y el primer `cierra` posterior, con DOS topes.

    El máximo está desde que el capítulo 7 de Muestreo sobrescribió al 6;
    el mínimo, desde que en T1.2 un ancla de cierre casó DEMASIADO PRONTO
    y dejó vivos dos simuladores de demostración con el archivo bien
    formado y el informe en verde.
    """
    if texto.count(abre) != 1:
        sys.exit(f"PARADO: el ancla de apertura de {que} aparece {texto.count(abre)} veces")
    i = texto.index(abre)
    j = texto.index(cierra, i)
    if j < 0:
        sys.exit(f"PARADO: no se encontró el cierre de {que}")
    region = texto[i:j + len(cierra)]
    nl = region.count("\n")
    if nl > max_lineas:
        sys.exit(f"PARADO: la región de {que} mide {nl} líneas y el tope es {max_lineas}")
    if nl < min_lineas:
        sys.exit(f"PARADO: la región de {que} mide {nl} líneas y el mínimo es {min_lineas}")
    return texto[:i] + nuevo + texto[j + len(cierra):]


def sustituye(texto, ancla, nuevo, que):
    if texto.count(ancla) != 1:
        sys.exit(f"PARADO: el ancla de {que} aparece {texto.count(ancla)} veces")
    return texto.replace(ancla, nuevo, 1)


def main() -> int:
    doc = PLANTILLA.read_text(encoding="utf-8")
    print(f"\n=== ensambla_cap2.py ===\nplantilla: {len(doc)/1024:.0f} KB\n")

    doc = sustituye(doc, "<title>Plantilla de capítulo — Estadística Espacial</title>",
                    f"<title>Capítulo 2 · {D['meta']['titulo']} — Estadística Espacial</title>",
                    "título")
    doc = sustituye(doc, "PLANTILLA BASE •\n              5 MÓDULOS DE DEMOSTRACIÓN • UNBOSQUE 2026-II",
                    f"CAPÍTULO 2 • CRS Y GEORREFERENCIACIÓN •\n"
                    f"              SEMANAS {D['meta']['semana']} • UNBOSQUE 2026-II",
                    "subtítulo de la cabecera")
    doc = sustituye(doc, "Estadística Espacial (20929) • Plantilla de\n          capítulo • UnBosque 2026-II",
                    f"Estadística Espacial (20929) • Capítulo 2 de 10 •\n"
                    f"          Semanas {D['meta']['semana']} • UnBosque 2026-II",
                    "pie")

    doc = reemplaza_region(doc, "    const courseData = {", "\n    };\n", COURSE_DATA,
                           "courseData + DATOS_CAP2", max_lineas=20)

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

    # El glosario de notación es del capítulo 1: aquí el de demostración
    # se retira sin sustituto, y el módulo que lo usaba no existe.
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
        + "    // ================================================================\n"
          "    // Autoevaluación de demostración: una pregunta de cada tipo\n",
        "los tres simuladores de demostración", max_lineas=140, min_lineas=100)

    doc = reemplaza_region(doc, "    AUTOEVALUACIONES['demo'] = [", "\n    ];\n",
                           QUIZ_JS, "AUTOEVALUACIONES", max_lineas=90)

    DESTINO.parent.mkdir(parents=True, exist_ok=True)
    DESTINO.write_text(doc, encoding="utf-8")

    # --- Guardas de salida ----------------------------------------------
    marcado = doc[:doc.rindex("\n  <script>")]
    mods = doc.count('<template id="module-')
    bloques_r = doc.count('class="language-r"')
    bloques_py = doc.count('class="language-python"')
    cifras = doc.count("#&gt;") + doc.count("#>")
    lienzos = marcado.count("<canvas")
    con_alt = sum(1 for c in marcado.split("<canvas")[1:]
                  if "aria-label" in c.split(">")[0])
    ejercicios = marcado.count('<div class="ejercicio-guiado">')

    codigo = "\n".join(l for l in doc.splitlines() if not l.lstrip().startswith("//"))

    def par(attr, registro):
        return (sorted(set(re.findall(attr, marcado))), sorted(set(re.findall(registro, codigo))))

    usados, registrados = par(r'data-geomapa="([^"]+)"', r"GEOMAPAS\['([^']+)'\]\s*=")
    sims_usados, sims_reg = par(r'data-simulador="([^"]+)"', r"SIMULADORES\['([^']+)'\]\s*=")
    quiz_usados, quiz_reg = par(r'data-quiz="([^"]+)"', r"AUTOEVALUACIONES\['([^']+)'\]\s*=")

    print(f"\n{DESTINO.relative_to(RAIZ)}  {len(doc)/1024:.0f} KB")
    print(f"  {mods} módulos · {len(sims_usados)} simuladores · {len(usados)} mapas · "
          f"{bloques_r} bloques de R y {bloques_py} de Python · {cifras} cifras anunciadas")
    print(f"  {lienzos} lienzos, {con_alt} con aria-label · "
          f"{ejercicios} ejercicios guiados · {len(quiz_usados)} autoevaluaciones")

    problemas = []
    if mods != 12:
        problemas.append(f"hay {mods} módulos y tienen que ser 12")
    if lienzos != con_alt:
        problemas.append(f"{lienzos - con_alt} lienzos sin aria-label")
    if ejercicios != 5:
        problemas.append(f"hay {ejercicios} ejercicios guiados y tienen que ser 5")
    for etq, us, rg in (("mapas", usados, registrados), ("simuladores", sims_usados, sims_reg),
                        ("autoevaluaciones", quiz_usados, quiz_reg)):
        huerfanos = set(us) - set(rg)
        sobrantes = set(rg) - set(us)
        if huerfanos:
            problemas.append(f"{etq} usados y no registrados: {sorted(huerfanos)}")
        if sobrantes:
            problemas.append(f"{etq} registrados y no usados: {sorted(sobrantes)}")

    # Los tipos de pregunta que el motor CONOCE. Un tipo inventado no da
    # error de sintaxis: revienta en tiempo de ejecución dentro de
    # iniciarAutoevaluaciones() y se lleva por delante todo lo que
    # loadModule() llama después. En T1.2 dejó sin pintar un mapa entero
    # en un módulo de doce.
    TIPOS = {"opcion", "multiple", "numerica", "grafico"}
    usados_tipo = set(re.findall(r"tipo:\s*'([a-z]+)'", QUIZ_JS))
    if usados_tipo - TIPOS:
        problemas.append(f"tipos de pregunta que el motor no conoce: {sorted(usados_tipo - TIPOS)}")

    # KaTeX no entiende el espacio fino U+202F: dentro de una fórmula
    # avisa por consola y deja un hueco sin métrica.
    for f in re.findall(r"\\\((.*?)\\\)", doc, re.S):
        if "\u202f" in f:
            problemas.append(f"una fórmula lleva U+202F: {f[:60]!r}")
            break

    if problemas:
        print("\n  PROBLEMAS:")
        for p in problemas:
            print(f"   - {p}")
        return 1
    print("\n  Capítulo 2 ensamblado.\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
