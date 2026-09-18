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
import re
import pathlib
import sys
from baraja_opciones import baraja_documento

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
    """Entero con espacio fino U+202F. NO usar dentro de KaTeX.

    El espacio ES el fino irrompible, y hubo que decirlo dos veces: la
    revisión del 2026-09-08 encontró que el docstring prometía U+202F y la
    línea de abajo escribía un U+0020 corriente, así que «2 209» podía
    partirse de renglón como «2» y «209». Los capítulos 1, 2 y 3 sí usaban
    el fino —38, 45 y 33 en lo publicado—; el 4 tenía UNO, y venía del
    ayudante de JavaScript. Los capítulos 5 y 6 heredaron la misma errata.
    """
    return f"{int(round(float(x))):,}".replace(",", "\u202f")


def ent_mate(x):
    """El mismo entero para DENTRO de una fórmula: KaTeX no entiende U+202F."""
    return f"{int(round(float(x))):,}".replace(",", r"\,")


def n_signo(x, d=5):
    """La cifra con su signo explícito y el menos tipográfico U+2212.

    Existe para el módulo 8, donde lo que se lee no es la magnitud sino el
    signo: «-0,08463» con guion corto, en un capítulo que escribe «L − r»
    con menos tipográfico, es la misma inconsistencia que el informe
    señalaba en los ejercicios.
    """
    return f"{float(x):+.{d}f}".replace("-", "\u2212")


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


def sim(ident, titulo, pie="", alto=260, mandos=True):
    """Un simulador con su lienzo de Chart.js —o una figura fija, si no lleva mandos.

    `mandos=False` es para los que no tienen ninguno. `cap4-cuadrantes` es una
    figura fija —la rejilla la fija el precálculo— y publicaba un contenedor de
    mandos vacío, un icono de deslizadores y un párrafo que decía «Elige el
    tamaño de la rejilla». Lo destapó la revisión del capítulo 5 (2026-09-02)
    buscando el gemelo de su módulo 8.

    `.grafico-wrapper` CON ALTURA EXPLÍCITA es el contrato de la
    plantilla: inventarse una clase deja el canvas a cero de alto,
    Chart.js crea el gráfico sin quejarse y el simulador sale en blanco
    con la consola limpia (defecto nº 5 de A.13).
    """
    icono = "fa-sliders" if mandos else "fa-chart-column"
    return f"""      <div class="simulador" data-simulador="{ident}">
        <h4><i class="fas {icono}" aria-hidden="true"></i> {titulo}</h4>
        {f'<p class="simulador-intro">{pie}</p>' if pie else ''}
{'        <div class="simulador-controles"></div>' + chr(10) if mandos else ''}\
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
    ("Las funciones G y F", "Distancias al vecino y al espacio vacío, y su cociente J"),
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
        {firma(n(m1['dc']['area_km2'], 5), ' km²')} y {firma(ent(m1['dc']['n']))}.</p>

      <p><strong>Ninguna de las dos es {ent(m1['sedes_total'])}</strong>, y conviene entender
        por qué antes de seguir: elegir una ventana no es solo elegir un denominador, es
        elegir también <em>qué sedes cuentan</em>. Cada recinto se queda con las que caen
        dentro y descarta el resto —{firma(ent(m1['urbana']['fuera']))} quedan fuera del
        perímetro urbano y {firma(ent(m1['dc']['fuera']))} del Distrito Capital—, así que la
        n cambia con la ventana igual que cambia el área. Los tres números son correctos y
        son tres cosas distintas: las georreferenciadas, las del D.C. y las urbanas.</p>

      <p>Fíjate ahora en lo que pasa con esos dos pares de números. Al pasar de una ventana a
        otra el numerador sube un {n(m1['aumento_n_pct'], 5)} %, porque el suelo rural del
        D.C. casi no tiene colegios; el denominador se multiplica por
        {n(m1['cociente_area'], 5)}.</p>

      <div class="key-insight">
        <p style="margin:0;">La misma ciudad, el mismo dato y dos intensidades que se llevan
        un factor de {firma(n(m1['factor_lambda'], 5))}:
        {firma(n(m1['urbana']['lambda_km2'], 5), ' sedes/km²')} contra
        {firma(n(m1['dc']['lambda_km2'], 5))}. Ninguna de las dos es un error. Lo que sería
        un error es publicar una sin decir cuál es la ventana, porque entonces la cifra no
        es ni verdadera ni falsa: está incompleta.</p>
      </div>

      <p>Y ese descarte tiene una propiedad que el mapa esconde y el código no: lo hace
        <code>ppp()</code> por su cuenta, con un aviso que nadie lee. El dibujo se ve igual,
        nada falla y el recuento ya es otro — <strong>cambia n sin cambiar nada visible</strong>.
        Ahí empieza a decidirse el resultado, y es la primera de las tres decisiones que este
        capítulo obliga a declarar.</p>

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
) + f"""      <p>La intensidad λ es el número esperado de puntos por unidad de área: cuántas sedes
        cabe esperar en cada kilómetro cuadrado de la ventana. Su estimador más simple es una
        división —n entre el área de la ventana—, y sobre el perímetro urbano da
        {firma(n(m2['lambda_urbana_km2'], 5), ' sedes/km²')}, que es la cifra que el módulo 1
        ya publicó.</p>

      <p>Esa misma intensidad se puede escribir en otras unidades:
        {n(m2['lambda_urbana_ha'], 5)} por hectárea, o {n(m2['lambda_urbana_m2'], 10)} por
        metro cuadrado. No son tres resultados: es uno solo medido con tres varas distintas, y
        conviene reconocerlo en las tres porque el código no elige por ti. Devuelve λ en la
        unidad del CRS, y el CRS de este capítulo mide en metros, así que lo que aparece en
        pantalla es la tercera —la que parece un cero—; el <code>* 1e6</code> del bloque del
        módulo 1 es justamente el paso a kilómetros cuadrados.</p>

      <div class="formula-box">
        <p>$$\\hat{{\\lambda}} = \\frac{{n}}{{|W|}} = \\frac{{{ent_mate(m1['urbana']['n'])}}}{{{n(m1['urbana']['area_km2'], 2)}\\ \\text{{km}}^2}}
          = {n(m2['lambda_urbana_km2'], 4)}\\ \\text{{sedes/km}}^2$$</p>
      </div>

      <p>Ese número describe el patrón <strong>solo si λ es constante</strong>; es decir,
        solo si la ventana está igual de poblada en todas partes. Comprobarlo no necesita
        teoría: se parte la ventana en cuadrantes, se cuentan los puntos que caen en cada uno
        y se mira si los conteos se parecen entre sí. Si la intensidad fuera la misma en todo
        el recinto, se parecerían salvo por el azar del propio conteo.</p>

      <p>Con una rejilla de {m2['urbana']['nx']}×{m2['urbana']['ny']} sobre el perímetro
        urbano quedan {firma(ent(m2['urbana']['celdas']))} celdas con algo de área dentro de
        la ventana —las que de aquí en adelante llamaremos <em>celdas vivas</em>—, y el
        reparto no se parece a nada uniforme: salen {n(m2['urbana']['media'], 5)} sedes por
        celda de promedio, la celda más poblada tiene
        {firma(ent(m2['urbana']['maximo']))} y hay {firma(ent(m2['urbana']['vacios']))} con
        cero.</p>

      <p>El paso siguiente, en casi todos los libros, es el <strong>índice de
        dispersión</strong>: la varianza de los conteos dividida por su media. Aquí vale
        {firma(n(m2['urbana']['dispersion'], 5))}, y la frase que suele venir detrás —«bajo
        Poisson valdría 1»— <strong>aquí sería falsa</strong>. Vale la pena ver por qué,
        porque el motivo reaparece en el resto del capítulo.</p>

      <p>Ese 1 sale de que en una distribución de Poisson la media y la varianza valen lo
        mismo, y solo se sostiene si todas las celdas son comparables entre sí: si en todas se
        espera el mismo número de puntos. Llamemos <strong>esperanza de una celda</strong> a
        los puntos que caerían dentro de ella si λ fuera constante —la intensidad multiplicada
        por el área de la celda—. Sobre una rejilla dibujada en el aire, todas las celdas miden
        igual y todas tienen la misma esperanza. Sobre Bogotá no: el perímetro urbano es un
        contorno irregular que recorta las celdas del borde y deja a unas con apenas una
        esquina dentro de la ventana y a otras enteras. Sus esperanzas van de
        {n(m2['urbana']['esperanza_min'], 2)} a {n(m2['urbana']['esperanza_max'], 1)} sedes.
        Con celdas tan desiguales, un Poisson <em>homogéneo</em> no daría 1: daría
        {firma(n(m2['urbana']['dispersion_nula'], 5))}.</p>

      <div class="key-insight">
        <p style="margin:0;">Buena parte del exceso sobre 1 no lo pone el patrón: lo pone la
        rejilla. Si las celdas tienen esperanzas E<sub>j</sub>, lo que un Poisson homogéneo da
        de media sobre esa misma rejilla es <strong>1 + S²(E)/Ē</strong>: uno, más la varianza
        de esas esperanzas dividida por su media. Cuando todas las celdas miden lo mismo esa
        varianza es cero y se recupera el 1 de los libros; aquí no lo es, y la referencia sube
        hasta {n(m2['urbana']['dispersion_nula'], 2)}. Así que el
        {n(m2['urbana']['dispersion'], 2)} observado no se compara con 1, sino con ese
        {n(m2['urbana']['dispersion_nula'], 2)}, y lo único que el patrón tiene que explicar es
        lo que sobra por encima.</p>
      </div>

      <p>El estadístico χ² del test de cuadrantes <strong>no</strong> arrastra ese problema,
        y por eso es el que se publica: en vez de comparar los conteos entre sí, compara cada
        conteo con la esperanza de su propia celda, λ|A<sub>j</sub>|, donde |A<sub>j</sub>| es
        el área de esa celda <em>ya recortada</em> contra la ventana. Vale
        {firma(n(m2['urbana']['chi2'], 2))} con {ent(m2['urbana']['gl'])} grados de libertad y
        un p-valor del orden de 10<sup>{n(m2['urbana']['p_log10'], 1)}</sup>: el test
        <strong>rechaza</strong>, y con un margen enorme. Qué es exactamente lo que queda
        rechazado —y por qué no basta con decir «λ no es constante»— lo precisa el módulo 5.</p>

      <p>Antes de celebrar ese rechazo, una advertencia que el módulo 6 va a cobrarse. El χ²
        da por supuesto que ninguna celda tiene una esperanza minúscula —la regla de andar por
        casa pide al menos 5 puntos esperados en cada una—, y aquí
        {firma(ent(m2['urbana']['celdas_esperanza_baja']))} de las
        {ent(m2['urbana']['celdas'])} celdas vivas tienen esperanza menor que 5, otra vez
        porque la ventana las recorta. El estadístico sigue siendo enorme y la conclusión no
        cambia, pero conviene saber sobre qué se apoya.</p>

      <p>El simulador de abajo usa esa misma rejilla y pone una junto a otra las dos cosas
        que acabamos de comparar: en barras, cuántas celdas tienen cada conteo; en línea,
        cuántas lo tendrían si λ fuera constante. Mira cómo se separan.</p>

{sim('cap4-cuadrantes', 'Contar en cuadrantes',
     'La rejilla es fija —la que declara la lectura—: la barra es el reparto observado de sedes por celda y la línea, el que daría una intensidad constante.', 300, mandos=False)}

      <p>Lo que acabas de ver no es que Bogotá tenga «mucha» o «poca» intensidad, sino que
        <strong>no tiene una sola</strong>. Una λ que cambia de un sitio a otro se llama
        <strong>inhomogénea</strong>, y es el caso normal, no la excepción. A partir de aquí un
        número deja de servir y hay que describir el patrón con funciones: de eso se ocupan los
        módulos 7 a 9, y antes hace falta saber contra qué compararlas.</p>

{tabs('Contar en cuadrantes y contrastar',
      '''qc &lt;- quadratcount(p_urb, nx = 10, ny = 10)
te &lt;- quadrat.test(p_urb, nx = 10, ny = 10)
# Avisa de que algunas esperanzas son pequenas: la ventana recorta celdas.

round(c(chi2 = unname(te$statistic), gl = unname(te$parameter["df"])), 2)
#&gt;   chi2     gl
#&gt; 456.12  64.00

# El indice de dispersion. Con celdas iguales, bajo Poisson valdria 1;
# aqui las celdas estan recortadas y la referencia es 15.23, no 1.
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

      <p>Fíjate en el comentario del bloque de Python, porque no es una nota de estilo. Para
        reproducir el χ² hay que reproducir antes el <strong>binado</strong>: la regla que
        decide a qué celda va un punto que cae justo sobre una línea de la rejilla. El de
        <code>quadratcount</code> es el de <code>cut()</code> —cada celda abierta por la
        izquierda y cerrada por la derecha, salvo la más baja, que se cierra por los dos
        lados—. Con otro convenio salen conteos <em>casi</em> iguales, que es la forma más cara
        de estar mal: el resultado parece correcto y no lo es. El módulo 5 vuelve sobre esto, y
        allí el convenio decide la demostración entera.</p>

""" + CIERRE


# =====================================================================
# MÓDULO 3 · Los tres regímenes
# =====================================================================
MOD3 = cabecera(
    3, "Los tres regímenes", "The three regimes",
    "Reconocer a ojo y con una cifra los tres comportamientos básicos —aleatorio, "
    "regular y agregado— sobre los patrones canónicos de la literatura."
) + f"""      <p>Antes de medir hace falta saber qué se está buscando. Un patrón puntual puede
        comportarse de tres maneras —<strong>regular</strong>, <strong>aleatorio</strong> y
        <strong>agregado</strong>—, y esas tres palabras son las que el resto del capítulo va
        a usar para todo. Los tres conjuntos de abajo son los que la literatura emplea para
        enseñarlas desde hace cincuenta años. Míralos antes de leer ninguna cifra: la
        diferencia se ve.</p>

{mapa_html('cap4-cells', 'Regular: células biológicas')}
{mapa_html('cap4-japanesepines', 'Aleatorio: pinos japoneses')}
{mapa_html('cap4-redwood', 'Agregado: plántulas de secuoya')}

      <p>En el primero los puntos se <strong>estorban</strong>: cada célula ocupa un sitio y
        empuja a las demás, así que quedan más separadas de lo que el azar daría — eso es un
        patrón <strong>regular</strong>. En el tercero se <strong>atraen</strong> —las
        plántulas brotan cerca del árbol madre— y aparecen grumos: ése es el
        <strong>agregado</strong>. El del medio no hace ni una cosa ni la otra, y es el
        <strong>aleatorio</strong>: cada punto se coloca sin mirar dónde están los demás.</p>

      <p>La cifra que los ordena es el índice de Clark-Evans: la distancia media al vecino
        más próximo, dividida por la que daría el azar. Bajo aleatoriedad esa distancia
        esperada vale 1/(2√λ), así que el cociente ronda 1; por debajo hay agregación y por
        encima, regularidad.</p>

      <div class="formula-box">
        <p>$$R = \\frac{{\\bar{{d}}_{{\\min}}}}{{1 / (2\\sqrt{{\\lambda}})}}
          \\qquad R &lt; 1 \\text{{ agregado}} \\qquad R \\approx 1 \\text{{ aleatorio}}
          \\qquad R &gt; 1 \\text{{ regular}}$$</p>
      </div>

      <p>La tabla de abajo lleva un cuarto canónico que no está dibujado arriba, los
        <strong>pinos suecos</strong>, y está por dos razones. La primera es que son un segundo
        patrón regular, para que «regular» no quede colgado de un solo ejemplo. La segunda es
        que son el único de los cuatro cuya ventana <em>no</em> es el cuadrado unidad: su
        superficie es de {ent(m3['swedishpines']['area'])} unidades cuadradas y no de 1, y por
        eso sus distancias se leen en otra escala —{n(m3['swedishpines']['nn_media'], 3)} frente a las
        centésimas de los demás— sin que su R deje de ser comparable. Ahí se ve de un vistazo
        que R es un cociente entre dos distancias y por tanto <strong>no tiene unidades</strong>,
        mientras que la d̄ sí las tiene. Vuelven a aparecer en el ejercicio 2 del módulo 12.</p>

      <table class="tabla-datos">
        <caption>Los cuatro canónicos y el patrón colombiano, con su distancia media al vecino
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

      <p>El simulador de abajo recorre los cinco patrones de la tabla —los cuatro canónicos
        y el colombiano— y enseña la R de cada uno junto a su distribución de distancias al
        vecino. Recórrelos: son cinco procesos distintos, y su R los ordena. Lo que ninguno
        de los cinco puede enseñar, porque cada uno es una sola realización, es cuánto se
        mueve la R de un patrón que NO cambia de naturaleza. Eso lo mide el módulo
        siguiente, y es el problema central del capítulo.</p>

{sim('cap4-regimenes', 'Los tres regímenes, y cuánto se mueve su R',
     'Elige el patrón: la barra es su distribución de distancias al vecino más próximo, y la lectura, su R.', 300)}

      <p>Fíjate en los pinos japoneses, que son los aleatorios: su R no da 1 exacto. Podría
        ser que el patrón no sea del todo aleatorio, o podría ser que el azar, sin más, no
        entregue nunca un 1 clavado. Con una sola realización de cada proceso no hay manera
        de saber cuál de las dos. El módulo siguiente simula dos mil y lo zanja.</p>

{tabs('El índice de Clark-Evans sobre los tres canónicos dibujados',
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

      <p>Las dos pestañas calculan lo mismo por caminos distintos —spatstat en R, un árbol k-d
        en Python— y llegan a la misma cifra hasta el cuarto decimal. Eso es lo que hace
        creíble una R, no que la imprima un paquete con buen nombre. Pero fíjate en cuál se
        pide: <code>clarkevans(p)[["naive"]]</code>, la versión <em>sin corregir</em>. Guarda
        esa palabra: el módulo siguiente va a enseñar que esa R no está centrada en 1, y el 10
        va a decir por qué.</p>

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
        ese algo sea λ|W| —la intensidad por el área de la ventana, que es lo que abrevian
        esas dos barras verticales—, es la <strong>firma de Poisson</strong>. Sus dos vecinas
        caen cada una a un lado: la binomial tiene siempre la varianza <em>por debajo</em> de la media, y la
        binomial negativa, <em>por encima</em>. El recorrido va de
        {ent(m4['conteo_min'])} a {ent(m4['conteo_max'])} puntos.</p>

      <p>La segunda mitad del módulo es la que engancha con el 11. Sobre esas mismas
        realizaciones —todas de azar puro, todas CSR por construcción— el índice de
        Clark-Evans recorre de {firma(n(m4['R_csr']['min'], 5))} a
        {firma(n(m4['R_csr']['max'], 5))}, con media
        {n(m4['R_csr']['media'], 5)} y un intervalo central del 95 % entre
        {n(m4['R_csr']['q025'], 5)} y {n(m4['R_csr']['q975'], 5)}.</p>

      <p>Detente en esa media, porque no es 1 y debería serlo. El módulo 3 enseñó que bajo
        aleatoriedad R ronda 1, y aquí dos mil realizaciones de aleatoriedad pura la dejan en
        {firma(n(m4['R_csr']['media'], 5))}. No es azar: es <strong>sesgo del
        estimador</strong>. R usa la distancia observada al vecino más próximo, y a un punto
        pegado al borde su vecino de verdad puede caer fuera de la ventana, donde nadie
        miró; entonces la distancia que se mide es más larga que la real y R sube. El mismo
        mecanismo que el módulo 10 va a medir sobre K, visto aquí primero. Por eso los pinos
        japoneses del módulo 3, que son los aleatorios, dan
        {n(m3['japanesepines']['clark_evans'], 5)}: casi exactamente el centro de esta nube,
        y no el 1 del libro. Corregido el borde, esa misma R baja a
        {n(m3['japanesepines']['clark_evans_donnelly'], 5)}.</p>

      <p>Léelo despacio, porque tiene consecuencias. Si el criterio fuera «R menor que 1
        significa agregación», {firma(ent(m4['R_csr']['bajo_1']))} de las
        {ent(m4['R_csr']['n'])} realizaciones de azar puro darían veredicto de agregado. Una
        R sola, sin saber cuánto se mueve el azar, no dice nada.</p>

{sim('cap4-poisson', 'Las dos propiedades de CSR',
     'Conmuta entre las dos propiedades: la primera enseña el reparto de conteos contra la Poisson teórica y la segunda, cuánto se mueve la R del azar.', 300)}

      <p>Ese temblor es la razón de ser de las envolventes de simulación, que llegan en el
        módulo 11. Anótalo, porque va a reaparecer con cada una de las funciones que vienen
        ahora: ninguna se lee sola.</p>

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

      <p>El aviso del bloque de Python es el que importa, y vale para todo el capítulo: R y
        Python <strong>no comparten generador de números aleatorios</strong>, así que la misma
        semilla no da las mismas simulaciones. Lo que se reproduce no es la cifra, es la
        <em>propiedad</em> —media y varianza rondando las dos λ|W|—, y por eso el capítulo
        publica las cifras de R y comprueba las propiedades en Python. Con eso ya está dicho
        contra qué se compara un patrón; lo que falta es con qué medirlo, y la herramienta más
        antigua es también la que peor ve.</p>

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
    'G, F, J y el átomo de los duplicados',
    '''g &lt;- Gest(p_urb, correction = c("km", "none"))   # `none` da la columna `raw`

round(c(G_empirica_en_0 = g$raw[1], G_km_en_0 = g$km[1]), 6)
#&gt; G_empirica_en_0       G_km_en_0
#&gt;        0.037494        0.000000

# Y ese 0,037494 son exactamente las sedes con un vecino a distancia cero
sum(nndist(p_urb) == 0)
#&gt; [1] 79

# J A MANO SOBRE LAS SECUOYAS, sin Jest(): llama a Fest() por dentro.
# Los sitios van por ppp() SIN check = FALSE, y no es un detalle: que tire
# los que caen fuera de la ventana es justo lo que se quiere.
w  &lt;- Window(redwood)
s  &lt;- expand.grid(x = seq(w$xrange[1], w$xrange[2], length.out = 400),
                  y = seq(w$yrange[1], w$yrange[2], length.out = 400))
s  &lt;- ppp(s$x, s$y, window = w)
dF &lt;- nncross(s, redwood, what = "dist"); bF &lt;- bdist.points(s)
dG &lt;- nndist(redwood);                    bG &lt;- bdist.points(redwood)

# Muestra reducida en los DOS lados: solo cuenta lo que esta a mas de r del borde
J &lt;- function(r) (1 - mean(dG[bG &gt; r] &lt;= r)) / (1 - mean(dF[bF &gt; r] &lt;= r))
round(sapply(c(0.02, 0.05, 0.08), J), 4)
#&gt; [1] 1.0457 0.1708 0.1147''',
    '''dd, _ = cKDTree(XU).query(XU, k=2)
nn = dd[:, 1]

print([int((nn == 0).sum()), round(float((nn == 0).mean()), 6)])
#&gt; [79, 0.037494]

# La G empirica es la funcion de distribucion de esas distancias, y su
# salto en r = 0 es la fraccion de puntos coincidentes. No hay nada que
# corregir: hay algo que declarar.

# J A MANO SOBRE LAS SECUOYAS, con la muestra reducida en los dos lados.
# La ventana de redwood es [0, 1] x [-1, 0]: la distancia al borde de un
# rectangulo es la menor de las cuatro.
P = reg[reg.patron == "redwood"][["x", "y"]].to_numpy()
gx, gy = np.meshgrid(np.linspace(0, 1, 400), np.linspace(-1, 0, 400))
S = np.c_[gx.ravel(), gy.ravel()]
borde = lambda Q: np.minimum.reduce([Q[:, 0], 1 - Q[:, 0], Q[:, 1] + 1, -Q[:, 1]])
dF, bF = cKDTree(P).query(S, k=1)[0], borde(S)
dG, bG = cKDTree(P).query(P, k=2)[0][:, 1], borde(P)

J = lambda r: (1 - (dG[bG &gt; r] &lt;= r).mean()) / (1 - (dF[bF &gt; r] &lt;= r).mean())
print([round(float(J(r)), 4) for r in (0.02, 0.05, 0.08)])
#&gt; [1.0457, 0.1708, 0.1147]''')

TABS_M8 = tabs(
    'K, L y el desvío máximo',
    '''k &lt;- Kest(p_urb, correction = "translate")
L &lt;- sqrt(k$trans / pi)
i &lt;- which.max(abs(L - k$r))

# OJO: esto sale sobre la rejilla nativa de spatstat (513 nodos). El
# capitulo publica sus curvas en una de 101, asi que el maximo cae en
# una r vecina y el valor difiere en la cuarta cifra.
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
        con el que daría el azar. El estadístico es el χ² de siempre.</p>

      <p>Conviene decir contra qué se contrasta, porque casi todo el mundo lo dice mal. La
        hipótesis nula <strong>no</strong> es «λ es constante»: es el <strong>proceso de
        Poisson homogéneo</strong> del módulo 4, que son las <em>dos</em> propiedades
        juntas —λ constante <em>y</em> puntos independientes—. Un rechazo dice que algo de
        ese paquete falla, y <strong>no dice cuál de las dos</strong>: un patrón con λ
        perfectamente constante cuyos puntos se agrupen rechaza igual. Guarda esta frase:
        el módulo 6 va a apoyarse en ella y una de las preguntas del capítulo la cobra.</p>

      <div class="formula-box">
        <p>$$\\chi^2 = \\sum_{{j=1}}^{{m}} \\frac{{(O_j - E_j)^2}}{{E_j}},
          \\qquad E_j = \\lambda\\,|A_j|$$</p>
      </div>

      <p>En esa suma, <em>O<sub>j</sub></em> es lo <strong>observado</strong> —los puntos
        que de verdad cayeron en la celda <em>j</em>—, <em>E<sub>j</sub></em> es lo
        <strong>esperado</strong> si la nula fuera cierta —la esperanza de esa celda, la del
        módulo 2: la intensidad por su área ya recortada— y <em>m</em> es cuántas celdas vivas
        hay. El estadístico es, literalmente, cuánto se aparta lo que hay de lo que tocaría,
        celda por celda.</p>

      <p>Funciona, y para el patrón de Bogotá rechaza con un margen enorme. Pero tiene una
        ceguera concreta, y la mejor manera de verla no es describirla: es construir dos
        patrones que el test <strong>no pueda distinguir</strong>, y comprobar que son
        distintos.</p>

      <p>Se toma <code>redwood</code> —las plántulas de secuoya del módulo 3, el patrón
        agregado— y se rehace conservando exactamente cuántas caen en cada celda de una
        rejilla {m5['nx']}×{m5['nx']} pero repartiéndolas <em>al azar dentro de la suya</em>.
        Los conteos por celda son los mismos, uno a uno. Luego el χ² es el mismo. Míralos.</p>

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

{TABS_M5}
      <p>La rebaraja del código es la demostración entera, y por eso se escribe en las dos
        pestañas en vez de citarse: se conservan los conteos por celda y se tira todo lo demás.
        Que el χ² salga idéntico <strong>hasta el último decimal</strong> no es una coincidencia
        afortunada, es una consecuencia aritmética de que el estadístico solo lea esos conteos.
        Y deja una pregunta incómoda para el módulo siguiente: si el tamaño de la celda decide
        lo que el test puede ver, <strong>¿quién elige el tamaño?</strong> Y si al cambiarlo
        cambia el veredicto, ¿de quién es el veredicto?</p>
""" + CIERRE


# =====================================================================
# MÓDULO 6 · El tamaño del cuadrante
# =====================================================================
_nx_baja = m6['redwood_nx_esperanza_baja']
_n_tam = len(m6['nxs'])
# Bogotá rompe el supuesto a saltos: la ventana recorta las celdas, y la
# rejilla de 5×5 lo respeta después de que 3×3 y 4×4 lo rompieran. El
# párrafo que cierra el simulador lo cuenta con estas cuatro rejillas, así
# que si un precálculo nuevo lo deja de ser, el ensamblado para.
_bog = m6['bogota']
_kb = {nx: k for k, nx in enumerate(_bog['nx'])}
_bog_baja = {nx: _bog['celdas_esperanza_baja'][_kb[nx]] for nx in (3, 4, 5, 6)}
if not (_bog_baja[3] > 0 and _bog_baja[4] > 0 and _bog_baja[5] == 0 and _bog_baja[6] > 0):
    sys.exit(f"PARADO: el módulo 6 cuenta que Bogotá rompe el supuesto en 3×3 y 4×4, "
             f"lo respeta en 5×5 y lo vuelve a romper en 6×6, y el precálculo dice {_bog_baja}")
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
        {ent(_n_tam)} tamaños rechazan la hipótesis de Poisson homogéneo. El que no
        rechaza es el más grueso, y no porque el patrón sea distinto: porque con cuatro
        celdas no hay resolución para ver los grumos.</p>

      <p>Pero el simulador de abajo barre <strong>tres</strong> patrones, y conviene
        recorrerlos los tres antes de sacar la moraleja, porque solo uno se comporta así.
        Sobre los pinos japoneses —los aleatorios— rechazan
        {firma(ent(m6['japanesepines_rechazos']))} de los {ent(_n_tam)} tamaños: el test no
        grita en ninguna escala cuando no hay nada por lo que gritar. Sobre las sedes de
        Bogotá rechazan los {ent(_n_tam)}, de la rejilla más gruesa a la más fina. El
        veredicto depende de la celda <strong>cuando el patrón está en el filo</strong>;
        cuando es claramente aleatorio o claramente inhomogéneo, la elección no lo mueve.</p>

      <p>Y en el otro extremo el problema se invierte. El p-valor del test no es exacto: sale
        de aproximar el estadístico por una distribución χ², y esa aproximación solo vale si
        ninguna celda espera muy pocos puntos. Es el <strong>supuesto del χ²</strong> que el
        módulo 2 dejó anotado —al menos 5 puntos esperados en cada celda—, y afinar la rejilla
        lo rompe, porque reparte los mismos puntos entre más celdas. Sobre las secuoyas, a
        partir de la rejilla de {firma(ent(_nx_baja))}×{ent(_nx_baja)} —<code>nx</code> es el
        número de celdas por lado— aparecen celdas con esperanza menor que 5.
        <strong>La escala que más resuelve es la que rompe el supuesto</strong>, y entre las
        dos exigencias queda muy poco en pie: de las {ent(_n_tam)} rejillas, solo las dos más
        gruesas respetan el supuesto, y la de 2×2 es justo la que no rechaza. La única que lo
        respeta <em>y</em> además rechaza es la de 3×3. Una, de diez. No hay un tamaño
        «correcto» que la teoría entregue: hay una decisión del analista, que se declara.</p>

{sim('cap4-barrido', 'El veredicto en función de la celda',
     'Barre el tamaño de la rejilla sobre los tres patrones: en rojo los tamaños que rechazan al 5 % y en gris los que no, y en pálido los que rompen el supuesto del χ², porque alguna celda espera menos de 5 puntos. Mira en cuál de los tres cambia el veredicto, y en cuál una rejilla más fina vuelve a respetar el supuesto.', 300)}

      <p>Las sedes de Bogotá enseñan algo que las secuoyas no pueden enseñar. La ventana de
        <code>redwood</code> es un cuadrado: todas sus celdas tienen la misma área, afinar la
        rejilla baja a la vez la esperanza de todas, y una vez roto el supuesto ya no se
        recupera. La ventana urbana no es un rectángulo, y recorta las celdas del borde. Bajo la
        nula, la esperanza de una celda es proporcional a su área <em>recortada</em>, y esa área
        depende de por dónde pasen las líneas de la rejilla, no solo de cuántas haya. Por eso
        el supuesto se rompe a saltos: la rejilla de 3×3 ya tiene celdas con esperanza menor
        que 5 ({ent(_bog_baja[3])} de {ent(_bog['celdas'][_kb[3]])}), la de 4×4 también
        ({ent(_bog_baja[4])} de {ent(_bog['celdas'][_kb[4]])}), la de 5×5 no tiene ninguna
        —su celda más pequeña espera {firma(n(_bog['esperanza_min'][_kb[5]], 2))} puntos— y la
        de 6×6 vuelve a romperlo ({ent(_bog_baja[6])} de {ent(_bog['celdas'][_kb[6]])}).
        «Afinar rompe el supuesto» es la tendencia, no una regla: con una ventana irregular,
        el supuesto se comprueba rejilla por rejilla, mirando la esperanza mínima de cada
        una.</p>

      <p>La lectura del capítulo 3 vale palabra por palabra: la escala no es un detalle de
        implementación, es parte del resultado, y un test de cuadrantes sin su tamaño de
        celda en el pie está incompleto. Las funciones de resumen de los módulos 7 a 9
        quitan de en medio <em>esta</em> elección —no hay ninguna celda que partir—, pero no
        la elección: el módulo 9 traerá un ancho de banda y el 11, un intervalo de r y un
        estadístico. Lo que se gana no es librarse de decidir; es dejar de tener que trocear
        el espacio para poder mirar.</p>

{TABS_M6}
      <p>El bloque enseña cuatro de los {ent(_n_tam)} tamaños, y en esas cuatro líneas está
        la moraleja escrita en p-valores: {n(m6['redwood']['p_valor'][0], 5)} con la rejilla
        de 2×2, {n(m6['redwood']['p_valor'][3], 5)} con la de 5×5, un cero redondeado con la
        de 10×10 — y otra vez {firma(n(m6['redwood']['p_valor'][9], 5))} con la de 20×20. El
        p-valor <strong>deja de mejorar y empeora</strong>. No es que el patrón se vuelva
        menos agregado cuando se mira más fino: es que con {ent(m6['redwood']['celdas'][-1])}
        celdas y {ent(m5['n'])} plántulas cada esperanza es minúscula y el χ² deja de seguir
        la distribución de la que sale su p-valor. La huella del supuesto roto estaba en la
        última línea de la tabla.</p>

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
# LO QUE ENTRÓ EL 2026-09-17, al contrastar el módulo con una explicación
# externa de G, F y J y verificar cada frase contra spatstat, contra los
# artículos originales y contra las curvas de este mismo JSON:
#   · la fórmula de las dos y su curva común bajo CSR, que el Taller 2
#     (T2c) ya daba por enseñada y el módulo no escribía;
#   · la tabla G/F, con el «otro» punto más cercano que la fuente omitía;
#   · de dónde salen los sitios de F, que el banco del Taller 2 pregunta, y
#     la F de Bogotá rehecha: contaba como hueco la caja entera;
#   · la J, con las dos advertencias verificadas que la fuente daba al
#     revés —«J = 1 significa CSR»— o no daba —que la estimada tiembla—.
# Y NO entra, a propósito, ningún patrón en que G y F apunten a regímenes
# distintos: construirlo es T2(c) del Taller 2, repartido el 21 de septiembre.
MOD7 = cabecera(
    7, "Las funciones G y F", "Nearest-neighbour and empty-space functions",
    "Describir el patrón con distancias en vez de con conteos, distinguir qué "
    "mira cada una de las dos funciones y leerlas juntas en la función J."
) + f"""      <p>Las funciones de resumen resuelven el problema del módulo 6 por la vía de no
        tener que elegir ninguna celda: en vez de contar en cajas, miden distancias. Las dos
        primeras son hermanas y se confunden constantemente, así que conviene fijar la
        diferencia antes de mirar ninguna curva.</p>

      <p><strong>G(r)</strong> mira desde los <em>puntos</em>: es la proporción de puntos
        cuyo vecino más próximo está a distancia r o menos. El vecino es el <em>otro</em> punto
        más cercano, porque cada punto está a distancia cero de sí mismo.
        <strong>F(r)</strong> mira desde el <em>espacio vacío</em>: se toman sitios
        cualesquiera de la ventana —no puntos del patrón—, se mide la distancia de cada uno al
        punto más cercano, y F(r) es la proporción de sitios que tienen un punto a r o menos.
        Dicho de otra manera, es la fracción de la ventana que cubren los discos de radio r
        centrados en los puntos. Lo que le falta hasta 1 es el hueco.</p>

      <div class="formula-box">
        <p>$$\\hat{{G}}(r) = \\frac{{1}}{{n}} \\sum_{{i=1}}^{{n}} \\mathbf{{1}}\\{{d_i \\leq r\\}}
          \\qquad
          \\hat{{F}}(r) = \\frac{{1}}{{m}} \\sum_{{j=1}}^{{m}} \\mathbf{{1}}\\{{e_j \\leq r\\}}$$</p>
        <p style="margin-bottom:0;">d<sub>i</sub> es la distancia del punto i a su vecino más
          próximo, y e<sub>j</sub> la del sitio j al punto más cercano. El <strong>1</strong>
          en negrita vale 1 si se cumple lo que va entre llaves y 0 si no, así que cada suma
          cuenta. Son las versiones sin corregir el borde: las corregidas cambian qué casos se
          cuentan o cuánto pesa cada uno, no qué distancia se mide.</p>
      </div>

      <p>Las dos tienen una curva de referencia, y es <strong>la misma</strong>. Bajo CSR, que
        un sitio no tenga ningún punto a distancia r o menos es que el disco de radio r a su
        alrededor esté vacío. Por la primera propiedad del módulo 4, el número de puntos de ese
        disco es una Poisson de media λπr², y la probabilidad de que valga cero es
        e<sup>−λπr²</sup>. Para G el argumento es el mismo por la segunda propiedad: los demás
        puntos se colocan sin saber que ese está ahí, así que mirar desde un punto del patrón
        es mirar desde un sitio cualquiera. El resultado tiene nombre, teorema de Slivnyak, y
        la consecuencia es que bajo CSR las dos funciones no se distinguen:</p>

      <div class="formula-box">
        <p>$$G(r) = F(r) = 1 - e^{{-\\lambda \\pi r^2}} \\qquad \\text{{bajo CSR}}$$</p>
      </div>

      <p>Contra esa curva común separan los regímenes en direcciones opuestas, y por eso se
        enseñan juntas. Un patrón agregado deja mucho hueco: sus puntos tienen vecinos muy
        cerca, así que G sube pronto, pero hay zonas grandes sin nada y F sube tarde. Un patrón
        regular hace lo contrario: ningún punto tiene un vecino muy cerca, así que G tarda en
        despegar, y no quedan huecos grandes, así que F sube antes que la de CSR.</p>

      <table class="tabla-datos">
        <caption>Las dos funciones de distancia, frente a frente.</caption>
        <thead><tr><th scope="col"></th><th scope="col">G(r), vecino más próximo</th>
          <th scope="col">F(r), espacio vacío</th></tr></thead>
        <tbody>
{fila('Desde dónde mide', 'Desde cada punto del patrón', 'Desde sitios de la ventana que no son puntos del patrón')}{fila('Hasta dónde', 'Hasta el <em>otro</em> punto más cercano', 'Hasta el punto más cercano')}{fila('Qué ve', 'Lo cerca que tiene cada punto a su vecino', 'El tamaño de los huecos')}{fila('Patrón agregado', 'Sube antes que la de CSR', 'Sube después que la de CSR')}{fila('Patrón regular', 'Arranca después, y sube más empinada', 'Sube antes que la de CSR')}{fila('Bajo CSR', '1 − e<sup>−λπr²</sup>', 'La misma')}        </tbody>
      </table>

      <p>La fila del patrón regular dice «arranca», y no «queda por debajo», a propósito: lo
        que se lee es cuándo despega cada curva, no si queda encima o debajo en todo r. Una
        cifra por curva lo resume, la r a la que llega a la mitad, y bajo CSR la de las dos es
        la misma. El simulador de abajo la da en su lectura.</p>

{sim('cap4-gf', 'G y F sobre los tres regímenes y sobre Bogotá',
     'Elige el patrón: se dibujan la G y la F observadas contra la curva que las dos tendrían bajo CSR, y en gris punteado la G sin corregir el borde. La lectura da la r a la que cada curva llega a la mitad.', 300)}

      <p>Recorre los tres de libro con la lectura a la vista. En las células la mitad tiene
        su vecina a menos de {firma(n(m7['cells']['g_mediana'], 5))}, la mitad de los sitios
        tiene una célula a menos de {firma(n(m7['cells']['f_mediana'], 5))}, y bajo CSR las dos
        valdrían {n(m7['cells']['csr_mediana'], 5)}: G llega tarde y F pronto. Fíjate además en
        que la G de las células arranca tarde pero, cuando arranca, sube tan empinada que acaba
        por encima de la de CSR, porque todas tienen su vecina a una distancia parecida. En
        las secuoyas el orden se invierte —{n(m7['redwood']['g_mediana'], 5)},
        {n(m7['redwood']['f_mediana'], 5)} y {n(m7['redwood']['csr_mediana'], 5)}—, y en los
        pinos japoneses, los aleatorios, las tres casi coinciden:
        {n(m7['japanesepines']['g_mediana'], 5)}, {n(m7['japanesepines']['f_mediana'], 5)} y
        {n(m7['japanesepines']['csr_mediana'], 5)}.</p>

      <p>Queda por decir de dónde salen los sitios de F, porque la definición dice
        «cualesquiera» y un ordenador necesita una lista. En la práctica son una rejilla
        regular y fina, aquí de {ent(m7['bogota']['f_rejilla'])} sitios sobre el rectángulo que
        encierra la ventana. En los tres patrones de libro la ventana <em>es</em> ese
        rectángulo y cuentan todos. En Bogotá no: caen dentro de la ventana urbana
        {firma(ent(m7['bogota']['f_sitios']))}, y solo esos valen. <strong>Un sitio fuera de la
        ventana no está vacío: está sin observar</strong>, y contarlo como hueco hundiría la F.
        Es la lección del módulo 1 —la ventana forma parte del estimador— aplicada a los
        sitios. Y de los de dentro, para cada r solo se usan los que quedan a más de r del
        borde, porque para los demás la respuesta depende de lo que haya al otro lado. Esa
        manera de corregir el borde, descartando en vez de pesar, se llama <strong>muestra
        reducida</strong>. A
        {n(m7['bogota']['r_f'][-1], 0)} m, la mayor distancia del simulador, sobreviven
        {ent(m7['bogota']['f_sitios_efectivos'])}.</p>

      <p>Con esos sitios, las sedes de Bogotá leen como un patrón agregado: la mitad de las
        sedes tiene otra a menos de {firma(n(m7['bogota']['g_mediana'], 2), ' m')} y la mitad
        de la ventana tiene una sede a menos de {firma(n(m7['bogota']['f_mediana'], 2), ' m')},
        cuando bajo CSR las dos serían {n(m7['bogota']['csr_mediana'], 2)} m. Pero el módulo 2
        ya enseñó que Bogotá no tiene una sola λ, y una intensidad que cambia de una zona a otra
        deja exactamente esa huella: vecinos cerca donde hay muchas sedes y huecos donde hay
        pocas. Lo honesto es leerlo como <strong>exceso de vecinos cercanos y de huecos</strong>
        respecto de CSR, no como la prueba de que las sedes se atraigan.</p>

      <p>Pon el simulador en las sedes, si no lo está ya, y mira la G justo en r = 0. Ahí
        aparece algo que los patrones de libro no tienen, y que conviene mirar de frente en vez
        de barrer debajo de la alfombra.</p>

      <div class="key-insight">
        <p style="margin:0;">La G <em>empírica</em> de las sedes no arranca en cero: vale
        {firma(n(m7['duplicados']['g_empirica_en_cero'], 6))} justo en r = 0. Eso solo puede
        pasar si hay puntos <strong>coincidentes</strong>, y los hay:
        {firma(ent(m7['bogota']['coincidentes']))} sedes —el
        {n(m7['bogota']['coincidentes_pct'], 5)} %— comparten coordenada exacta con otra,
        repartidas en {firma(ent(m7['duplicados']['repetidos']))} sitios y hasta
        {ent(m7['duplicados']['maximo_por_sitio'])} en uno solo. Son sedes distintas en el
        mismo edificio. A ese salto de la curva justo en r = 0 se le llama un
        <strong>átomo</strong>: probabilidad concentrada en un único valor, que aquí es el
        cero.</p>
      </div>

      <p>Un patrón con puntos duplicados <strong>no es un proceso puntual simple</strong>, y
        eso rompe un supuesto de todos los estimadores de este capítulo. No se ha corregido
        —colapsarlos cambiaría n y con él la λ que el módulo 1 publicó— y por tanto se
        declara. El detalle fino: el estimador de Kaplan-Meier de G, que es el que corrige
        el borde, vale {n(m7['duplicados']['g_km_en_cero'], 6)} en r = 0 <em>por
        convenio</em>, así que la corrección y el átomo viven en el mismo punto de la curva
        y el segundo desaparece de la vista. Por eso el capítulo dibuja las dos.</p>

      <p>G y F se leen mejor juntas que por separado, y hay una función que las junta en una
        sola curva: la <strong>función J</strong> de van Lieshout y Baddeley (1996). Es el
        cociente entre lo que le falta a cada una para llegar a 1.</p>

      <div class="formula-box">
        <p>$$J(r) = \\frac{{1 - G(r)}}{{1 - F(r)}}$$</p>
      </div>

      <p>Bajo CSR G y F son la misma curva, así que J vale 1 en todo r, y esa es su ventaja:
        una referencia plana, igual que la L − r del módulo siguiente, que bajo CSR vale cero. En un patrón
        agregado casi todos los puntos tienen ya vecino y todavía queda mucho hueco, así que el
        numerador es pequeño, el denominador grande y J cae por debajo de 1. En uno regular
        pasa lo contrario y J sube por encima. Para que el cociente compare lo mismo, las dos
        funciones se estiman igual: aquí por muestra reducida, contando solo los puntos y los
        sitios que quedan a más de r del borde. Y se dibuja solo mientras F no pasa de
        {n(m7['j_umbral_f'], 1)}, que es el tramo que el propio spatstat recomienda leer.</p>

{sim('cap4-j', 'La función J sobre los tres regímenes y sobre Bogotá',
     'Elige el patrón: se dibuja J(r) contra la recta J = 1 que da CSR. La lectura dice hacia dónde se aparta, no qué régimen es: eso necesita saber cuánto se aparta el azar.', 300)}

      <p>Recórrelos antes de creerle. En las células J queda por encima de 1 en todo su tramo
        y llega a {firma(n(m7['cells']['j_max'], 5))}. En las secuoyas queda por debajo en
        {ent(m7['redwood']['j_bajo_1'])} de sus {ent(m7['redwood']['j_nodos'])} distancias y
        llega a {firma(ent(m7['redwood']['j_min']))}, cero exacto, en r = {n(m7['redwood']['r_j_min'], 5)}:
        a esa distancia todas las plántulas que cuentan tienen ya su vecina, y todavía queda
        hueco. Ahora los pinos japoneses, los aleatorios: su J va de
        {firma(n(m7['japanesepines']['j_min'], 5))} a
        {firma(n(m7['japanesepines']['j_max'], 5))}. Leída con la regla de arriba, llamaría
        regular a un patrón aleatorio en unas distancias y agregado en otras.</p>

      <p>Es el aviso del módulo 4 otra vez —ninguna función se lee sola—, y con J pesa más,
        porque es un cociente. Cuando F se acerca a su tope el denominador es un resto pequeño y
        cualquier temblor se agranda: el mínimo de los pinos está justo en el último nodo
        dibujado, r = {n(m7['japanesepines']['r_j_min'], 5)}. Por eso el tramo se corta, y por
        eso la manera de saber cuánto se aparta el azar —simular CSR y ver dónde cae la curva—
        es la del módulo 11.</p>

      <p>Y el aviso contrario, que es el del módulo 5 con otro estadístico: una J pegada a 1
        <strong>no certifica que el patrón sea CSR</strong>. CSR da J = 1, pero la implicación
        no va en la otra dirección. Bedford y van den Berg (1997) construyeron, sobre la recta,
        procesos que no son de Poisson y tienen J = 1 en todo r; si en una dimensión no basta,
        no hay por qué suponer que baste en dos.</p>

      <p>Sobre las sedes de Bogotá, J queda por debajo de 1 en las
        {ent(m7['bogota']['j_nodos'])} distancias: exceso de vecinos cercanos y de huecos a la
        vez, con la misma cautela que antes sobre quién lo pone. Y no arranca en 1 sino en
        {firma(n(m7['bogota']['j_en_cero'], 6))}. La G de muestra reducida es un recuento sin
        convenio en r = 0, así que ve el átomo que Kaplan-Meier borraba: ese valor es 1 menos la
        fracción de sedes coincidentes.</p>

{TABS_M7}
      <p>La primera parte de las dos pestañas cuenta el átomo de dos maneras, y las dos dan
        {ent(m7['bogota']['coincidentes'])}: en R, leyendo la G empírica en r = 0; en Python,
        contando cuántas distancias al vecino más próximo valen exactamente cero. Que la G
        de spatstat y un recuento directo den la misma cifra es lo que convierte el átomo en
        un hecho del dato y no en un artefacto del estimador. La segunda parte rehace la J de
        las secuoyas a mano, con los sitios dentro de la ventana y la muestra reducida en los
        dos lados del cociente, sin <code>Jest()</code>, que llama por dentro a
        <code>Fest()</code>, la función que en la máquina del precálculo devuelve distancias
        falsas.</p>

      <p>Con eso queda descrito lo que pasa en el entorno inmediato de cada punto. G, F y J
        solo miran el punto más cercano: en cuanto r pasa de la mayor de esas distancias, G
        vale 1 y ya no dice nada más. Lo que pasa más allá necesita otra herramienta.</p>
""" + CIERRE


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

      <p>La fórmula es esa definición, contada a mano. La doble suma recorre todas las parejas
        de puntos distintos, i y j; <strong>1</strong>(d<sub>ij</sub> ≤ r) vale 1 cuando la
        distancia d<sub>ij</sub> entre los dos no pasa de r y 0 cuando pasa, así que la suma
        cuenta las parejas cercanas. El peso w<sub>ij</sub> corrige lo que el borde de la
        ventana esconde, y es el asunto entero del módulo 10. El factor de delante hace el
        resto: como λ̂|W| es el número de puntos, dividir por él reparte la cuenta por punto,
        y el otro λ̂ la divide por la intensidad, que es lo que pide la definición.</p>

      <p>Bajo aleatoriedad completa K vale exactamente πr², que es una parábola. Comparar
        una curva contra una parábola a ojo es incómodo —la vista juzga mal las curvaturas—
        y de ahí la transformación de Besag: L(r) = √(K(r)/π), que bajo CSR es la recta
        L = r. Se dibuja L(r) − r contra r, y entonces CSR es el eje horizontal: por encima
        hay agregación y por debajo, regularidad.</p>

{sim('cap4-kl', 'K y L sobre el mismo patrón',
     'Conmuta entre K y L − r: es la misma información, y solo una de las dos se lee de un vistazo.', 300)}

      <p>Sobre las sedes de Bogotá, L − r alcanza su máximo de
        {firma(n(m8['bogota']['max_desvio'], 2), ' m')} a una distancia de
        {firma(n(m8['bogota']['r_max_desvio'], 0), ' m')}, y no baja de cero en ninguna de las
        distancias medidas. Eso es lo que la curva dice, y conviene no hacerle decir más. Que
        esté por encima de la recta en todo r no prueba que haya estructura a todas las
        escalas —el módulo siguiente enseña por qué K no puede decir <em>dónde</em>—, y
        tampoco prueba que los colegios se atraigan: contra CSR, puntos que se atraen y una
        intensidad que cambia de un barrio a otro dejan la <strong>misma huella</strong>, y el
        módulo 2 ya mostró que λ no es constante sobre Bogotá. Es la advertencia del módulo 5
        sobre el χ² —un rechazo no dice cuál de las dos propiedades falla—, y aquí vale
        igual.</p>

      <p>En los tres canónicos va escrito el <strong>signo</strong>, porque dice hacia dónde
        se aparta la curva: {n_signo(m8['cells']['desvio_con_signo'])} en las células,
        {n_signo(m8['japanesepines']['desvio_con_signo'])} en los pinos y
        {n_signo(m8['redwood']['desvio_con_signo'])} en las secuoyas. Pero fíjate en los
        pinos, que son los aleatorios: su desvío es negativo, del mismo signo que el de las
        células regulares. El signo dice la <em>dirección</em>, no si el apartamiento
        significa algo, y el tamaño solo tampoco lo dice — es la lección del módulo 4, «una R
        sola, sin saber cuánto se mueve el azar, no dice nada», aplicada a una curva entera.
        Lo que decide es si la curva se sale de lo que produce el azar, y eso lo mide el
        módulo 11: allí el test global sobre los pinos da p =
        {n(m11['test_global']['dclf_japanesepines_p'], 5)}, nada que rechazar.</p>

      <p>El bloque de abajo calcula K sobre las sedes con la corrección de traslación y busca
        la distancia a la que L − r se aparta más de cero.</p>

{TABS_M8}
      <p>El comentario del bloque de R señala algo que conviene no pasar por alto: la curva se
        calcula en la rejilla que elige spatstat y se <em>publica</em> en una de 101 nodos, así
        que el máximo cae en una r vecina y el valor difiere en la cuarta cifra. No es un
        error de nadie: es que una curva y su resumen se miden en rejillas distintas, y decirlo
        cuesta menos que dejar al lector comparando dos números que no cuadran.</p>
""" + CIERRE


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
# las cuenta para todas las r de una vez, sin materializar la matriz de
# distancias, que crece con el cuadrado del numero de puntos.
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
        de {firma(n(m9['redwood']['r_g_max'], 5))} y ha vuelto a 1 en
        {firma(n(m9['redwood']['r_vuelve_a_1'], 4))}, <strong>mientras K sigue por encima
        de su teórica y no vuelve</strong>. Esa distancia a la que g regresa es
        <strong>el tamaño de los grumos</strong>, y K no la sabe decir: se despegó al
        principio y arrastra ese despegue hasta el final.</p>

      <p>Antes de mirar Bogotá, pasa el simulador por las células y por los pinos, porque cada
        uno enseña algo que las secuoyas no. En las <strong>células</strong> g se queda pegada
        a 0 en las distancias cortas y no despega de verdad hasta rondar
        {n(m3['cells']['nn_min'], 5)}, que es la distancia de la pareja de células más
        próxima; después sube a {firma(n(m9['cells']['g_max'], 5))} en
        {n(m9['cells']['r_g_max'], 5)}. Ese hueco y ese pico son el «cada célula ocupa un sitio
        y empuja a las demás» del módulo 3, dibujado, y el «por debajo» de 1 que la definición
        anunciaba. En los <strong>pinos</strong>, que son aleatorios, g cruza el 1 una y otra
        vez y acaba el barrido en {n(m9['japanesepines']['g_obs'][-1], 5)}: un patrón sin
        estructura ninguna puede quedar lejos de 1 en una distancia suelta, y por eso un valor
        aislado de g, sin saber cuánto lo mueve el azar, no se lee.</p>

      <p>Sobre las sedes de Bogotá g no tiene pico: vale
        {firma(n(m9['bogota']['g_max'], 5))} en el primer nodo del barrido
        —{n(m9['bogota']['r_g_max'], 0)} m— y de ahí en adelante baja, con vaivenes pequeños
        pero sin volver a acercarse a esa altura. Ese máximo en el borde
        izquierdo <strong>no es una escala característica</strong>: es donde empieza a
        mirarse, y la estructura fina que habría debajo no se ve porque el barrido no llega.
        Lo que sí dice la curva es hasta dónde llega el exceso, y la respuesta es que
        <strong>no se acaba</strong>: g no regresa a 1 en ningún punto del barrido, y en el
        último nodo —{n(m9['bogota']['r'][-1], 0)} m— todavía vale
        {n(m9['bogota']['g_obs'][-1], 5)}. Eso sí lo resuelve g y K no podía: el exceso de
        parejas no es arrastre de las distancias cortas, está en cada anillo, también a escala
        de kilómetros.</p>

      <p>Y aquí hay que frenar, porque lo que la curva no puede decir es <em>por qué</em>.
        Puede ser que los colegios se atraigan —que donde hay uno sea más probable que se abra
        otro al lado—, o puede ser que simplemente haya zonas de la ciudad con muchas sedes y
        zonas con pocas, cada una repartida al azar dentro de la suya. Contra CSR las dos
        dejan exactamente esta huella, y el módulo 2 ya enseñó que λ no es constante sobre
        Bogotá: una intensidad que cambia a escala de kilómetros produce por sí sola un exceso
        de parejas a escala de kilómetros, sin que ningún colegio atraiga a otro. Separar las
        dos lecturas exige estimar primero cómo cambia λ de un sitio a otro y comparar contra
        <em>eso</em> en vez de contra CSR, que es justo donde empieza el capítulo 5. Hasta
        entonces, lo honesto es llamarlo exceso de parejas, no atracción.</p>

      <p>Las dos pestañas de abajo calculan g sobre las secuoyas y, a diferencia de casi todos
        los bloques del capítulo, no llegan a la misma cifra. Es a propósito, y la diferencia
        es la lección.</p>

{TABS_M9}
      <p>La pestaña de Python es aquí la interesante, porque no reproduce a spatstat: calcula la
        g <em>cruda</em>, contando parejas por anillo sin suavizar. Sale más alta y más
        dentada, y esa diferencia es lo que compra el suavizado —a cambio de un ancho de banda
        que hay que elegir, y que el capítulo 5 discute en serio—. Con G, F, K y g el patrón ya
        está descrito; lo que sigue es si podemos creernos las curvas, y la respuesta empieza
        por el borde de la ventana.</p>
""" + CIERRE


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

      <p>Hay tres correcciones clásicas, y las tres son maneras distintas de elegir el peso
        w<sub>ij</sub> de la fórmula del módulo 8. La de <strong>borde</strong> usa pesos de 0
        o 1: descarta como centro todo punto cuyo disco de radio r no cabe entero en la
        ventana. La de <strong>traslación</strong> desplaza la ventana por el vector que une
        los dos puntos de la pareja y mide cuánto se solapa con la original: cuanto menos
        solape, más pesa la pareja, porque parejas así tenían más difícil caer dentro. La
        <strong>isotrópica</strong> de Ripley traza el círculo centrado en uno de los dos
        puntos que pasa por el otro, y pesa según qué fracción de esa circunferencia queda
        dentro de la ventana. Las tres corrigen; no las tres cuestan lo mismo.</p>

{sim('cap4-bordes', 'Las tres correcciones, y la que no corrige',
     'Activa y desactiva cada corrección sobre el patrón colombiano y mira cuánto se mueve la curva.', 300)}

      <p>Enciende a la vez las tres corregidas y la que no corrige. Las tres corregidas no
        coinciden del todo entre sí, pero las tres se despegan de la que no corrige, y cada
        vez más a medida que crece r.</p>

      <p>Los libros de texto hacen estas cuentas sobre rectángulos. La ventana urbana de
        Bogotá tiene
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
        veces lo que la de traslación, y no puede ser por el número de puntos: las dos
        corrigen el mismo patrón, con las mismas {ent(m1['urbana']['n'])} sedes y las mismas
        parejas. Lo que cambia es el borde: la isotrópica tiene que cortar, pareja a pareja,
        un círculo contra un contorno de {ent(m10['ventana']['vertices'])} vértices. Lo que
        se paga es el borde, no n.</p>

      <p>Por eso este capítulo <strong>precalcula sus envolventes con la corrección de
        traslación</strong> y calcula la isotrópica una sola vez por patrón, para poder
        publicar la diferencia. No es un atajo silencioso: es una decisión declarada, y la
        tabla de arriba es su justificación.</p>

      <p>Un último aviso que enlaza con el módulo 7: en r = 0 la K sin corregir
        <em>no</em> vale cero, vale {firma(n(m10['k_cero_sin_corregir'], 2))}. Son las
        parejas a distancia exactamente cero, es decir las sedes coincidentes. La corregida
        por traslación, la que publica el módulo 8, vale ahí
        {ent(m10['k_cero_traslacion'])}: el átomo no se ve. Es lo mismo que el Kaplan-Meier
        le hacía a G en el módulo 7: el átomo asoma en los estimadores sin corregir y
        desaparece de estos dos corregidos, así que para verlo en ellos hay que mirar la
        versión cruda. No de todos los corregidos: la G de muestra reducida con la que el
        módulo 7 arma la J es un recuento sin convenio en r = 0, y lo ve. Y la
        F no lo ve nunca: que dos sedes compartan sitio no cambia la distancia de un lugar
        vacío a la sede más cercana.</p>

{TABS_M10}
      <p>El bloque de R deja fuera, a propósito, los segundos que tarda cada corrección: no son
        reproducibles —dependen de la máquina— y publicarlos como salida esperada sería anunciar
        una cifra que nadie puede comprobar. Se anuncia la <em>relación</em>, que es lo que el
        módulo afirma, y se invita a medir los tiempos en la máquina de cada cual. Con el borde
        corregido, las curvas ya son creíbles.</p>
""" + CIERRE


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
        ventana, se calcula K para cada uno y se dibuja la banda que forman. La lectura que
        tienta es inmediata: si la observada se sale de la banda, hay algo que CSR no
        explica.</p>

      <p>Es la herramienta estándar, y esa lectura, tal cual, está mal. Este módulo existe
        sobre todo para decir por qué, y el recuadro de más abajo mide cuánto.</p>

{sim('cap4-envolvente', 'La envolvente y la curva observada',
     'Elige el patrón: la banda son las simulaciones de CSR y la línea gruesa, el dato.', 300)}

      <div class="key-insight">
        <p style="margin:0;">La banda puntual es un intervalo al 95 % <strong>para cada r por
        separado</strong>. Mirar la curva entera y decir «se sale en algún sitio, luego
        p &lt; 0.05» es hacer un centenar de contrastes y quedarse con el peor. ¿Cuánto
        importa? Se mide: de las {ent(m11['tasa_salida_bogota']['nsim'])} simulaciones de CSR
        <em>puro</em> usadas para construir la banda del patrón colombiano,
        {firma(ent(m11['tasa_salida_bogota']['fuera']))} —el
        {firma(n(m11['tasa_salida_bogota']['pct'], 5), ' %')}— se salen de ella en algún r.
        Todas eran nulas por construcción.</p>
      </div>

      <p>Y esa cifra no es del patrón colombiano. Las simulaciones de las secuoyas se salen
        de su banda un {n(m11['redwood']['tasa_salida']['pct'], 5)} % de las veces, y las de
        los pinos, un {n(m11['japanesepines']['tasa_salida']['pct'], 5)} %. Tres patrones sin
        nada en común —{ent(m3['redwood']['n'])} plántulas y {ent(m3['japanesepines']['n'])}
        pinos en un cuadrado, {ent(m1['urbana']['n'])} sedes en una ventana de
        {ent(m10['ventana']['piezas'])} piezas— y casi la misma tasa. La pone sobre todo el
        procedimiento, no el dato: mirar {ent(m11['tasa_salida_bogota']['nodos_r'])}
        distancias con una banda al 95 % en cada una. En los pinos, además, la curva observada
        no se sale en ningún r, y aun así la mitad de sus propias simulaciones nulas sí lo
        hacen.</p>

      <p>La salida correcta es un <strong>test de desviación global</strong>, que resume la
        curva entera en un número antes de compararla. El de Diggle-Cressie-Loosmore-Ford
        (DCLF) integra a lo largo de r el cuadrado de la separación entre la curva observada
        y la media de las simuladas; el MAD —máxima desviación absoluta— se queda con la
        mayor de esas separaciones. Sobre el patrón colombiano, el DCLF da
        p = {firma(n(m11['test_global']['dclf_bogota_p'], 5))} y el MAD, {n(m11['test_global']['mad_bogota_p'], 5)}; sobre los pinos japoneses,
        {n(m11['test_global']['dclf_japanesepines_p'], 5)} y
        {n(m11['test_global']['mad_japanesepines_p'], 5)}.</p>

      <p>El test global obliga a dos decisiones que la banda escondía: <strong>qué
        estadístico</strong> —el DCLF o el MAD, que no miden lo mismo— y <strong>sobre qué
        intervalo de r</strong> se calcula, porque la separación se integra o se maximiza
        entre dos distancias que alguien elige. Aquí las dos versiones coinciden en lo que
        dicen; no tienen por qué, y por eso las dos elecciones se declaran. El ejercicio 4 lo
        comprueba sobre las células: sin cambiar el patrón ni sus
        {ent(S['e4']['solucion']['nsim'])} simulaciones, el DCLF sobre K da
        p = {n(S['e4']['solucion']['tramos'][2]['dclf_p'], 5)} con todo el intervalo de r,
        {n(S['e4']['solucion']['tramos'][1]['dclf_p'], 5)} si se acorta a las distancias cortas
        y {n(S['e4']['solucion']['dclf_L'], 5)} si se calcula sobre L en vez de sobre K. De no
        rechazar a rechazar al máximo, solo por dos elecciones.</p>

      <p>Queda el otro malentendido, el de cuántas simulaciones hacen falta. La respuesta
        empieza por una cifra que sorprende: con {ent(m11['nsim'])} simulaciones el p-valor
        más pequeño que existe es {firma(n(m11['p_minimo'], 5))}, y no hay separación de la
        curva que lo baje. Es exactamente el p que el DCLF daba sobre Bogotá: la curva
        observada quedó más lejos que todas las simulaciones, y el p ya no podía bajar más. El
        p-valor mínimo es 1/(nsim+1) —nsim es el número de simulaciones— y no es una
        convención: es aritmética.</p>

      <p>Y aquí está la trampa que casi todo el mundo pisa. La banda que <code>envelope()</code>
        dibuja por defecto es el <em>mínimo y el máximo</em> de las simulaciones. En general
        se puede tomar la k-ésima más baja y la k-ésima más alta en vez de los extremos: ese k
        es el <strong>rango</strong> —el argumento <code>nrank</code>—, y con rango k el nivel
        puntual de la banda es 2k/(nsim+1). Por defecto k vale 1, así que el nivel vale
        2/(nsim+1). Con {ent(_e39['nsim'])} simulaciones eso es un contraste al
        {n(_e39['nivel_defecto'], 5)}; con {ent(_e999['nsim'])}, al
        {n(_e999['nivel_defecto'], 5)}. <strong>Subir nsim sin tocar nada más no afina la
        misma banda: cambia de contraste</strong>, y por eso la banda se ENSANCHA
        —{n(m11['escala_resumen']['veces_defecto'], 5)} veces a lo largo del barrido— en vez
        de estrecharse.</p>

      <p>Manteniendo el nivel fijo al 5 %, que exige subir el rango con nsim, la banda sí se
        estrecha: {n(m11['escala_resumen']['veces_5pct_alcanzable'], 5)} veces entre
        {ent(_e39['nsim'])} y {ent(_e999['nsim'])}, los dos valores del barrido donde ese nivel
        se alcanza exactamente. En los otros dos <strong>no se alcanza</strong>: con
        {ent(ESC[19]['nsim'])} simulaciones el rango que haría falta es
        {n(ESC[19]['nrank_para_5pct'], 5)}, y los rangos son enteros. Con
        {ent(ESC[99]['nsim'])} tampoco: haría falta {n(ESC[99]['nrank_para_5pct'], 5)}, y hay
        que conformarse con rango {ent(ESC[99]['nrank_usado'])} y un contraste al
        {n(ESC[99]['nivel_real'], 5)}.</p>

{sim('cap4-nsim', 'Cuántas simulaciones, y a qué nivel',
     'Las cuatro columnas son el barrido entero; el mando resalta una y la lee. En rojo, la banda por defecto; en verde, la de nivel fijo al 5 %.', 300)}

      <p>Recorre los cuatro valores: la roja se ensancha de punta a punta, y la verde se
        estrecha solo entre los valores donde de verdad está al 5 % —la lectura dice en cuáles.
        Elegir nsim no es elegir precisión, es elegir qué contrastes existen.</p>

{TABS_M11}
      <p>Fíjate en la última línea del bloque de R: el test global <strong>reutiliza las mismas
        simulaciones</strong> que la banda —el bloque lo hace con {ent(_e39['nsim'])} y no hacen falta otras
        tantas—, y esa es la razón práctica de que no haya excusa para leer la banda entera
        como si fuera un contraste: el contraste correcto ya está pagado. Mira también qué p da
        para los pinos: no es el {n(m11['test_global']['dclf_japanesepines_p'], 5)} de arriba,
        porque el bloque usa {ent(_e39['nsim'])} simulaciones y el precálculo
        {ent(_e999['nsim'])}. Con {ent(_e39['nsim'])}, el p solo puede valer múltiplos de
        {n(_e39['p_minimo'], 5)}; es la aritmética del p mínimo, aplicada a todos los demás
        valores.</p>

      <p>La pestaña de Python repite a mano la medición del recuadro —cuántas simulaciones de
        CSR puro se salen de su propia banda— sobre el cuadrado unidad y con muchas menos
        distancias. Sale una fracción menor —mira menos distancias y otro patrón—, pero ni de
        lejos el 5 %. Con esto el capítulo tiene sus cuatro
        piezas —una ventana declarada, una escala elegida, una curva corregida y una referencia
        simulada—, y lo que queda es usarlas.</p>
""" + CIERRE


# =====================================================================
# MÓDULO 12 · Autoevaluación y ejercicios guiados
# =====================================================================
def valor_paso(v):
    """El valor de un paso de solución, formateado como el resto del capítulo.

    POR QUÉ AQUÍ Y NO EN R. `genera_soluciones.R` redondea a diez decimales
    con `r10()` y hace bien: el JSON es el precálculo, y el auditor numérico
    lo compara con esa precisión. Lo que estaba mal era volcarlo CRUDO a la
    página: el estudiante leía «Área urbana (km²) 370.0898165101» en un
    capítulo cuya regla de publicación son cinco decimales, y «2107» donde la
    prosa escribe «2 107». Lo destapó la revisión del 2026-09-08 (A.30.11).

    Y no rompe la comprobación de `audita_texto_base.soluciones()`, que es lo
    que había que mirar antes de tocar nada: esa comprobación **lee los
    decimales de la celda** y exige que el valor del JSON redondeado a esos
    mismos coincida, en vez de asumir una tolerancia. Publicar con cinco es
    una promesa que sabe verificar; los millares se los quita antes de
    interpretar el número, incluido el fino.
    """
    if isinstance(v, bool):
        return "sí" if v else "no"
    if isinstance(v, int):
        return ent(v)
    if isinstance(v, float):
        # Un flotante que es un entero se publica como entero: escribir
        # «513.00000» donde hay un conteo es la clase de cifra que
        # `mide_punto_ciego.py` señaló como peor protegida, pero al revés.
        # El menos tipográfico, como en el resto del capítulo. La
        # comprobación de `audita_texto_base` lo convierte a «-» antes de
        # interpretar el número, así que esto no la estorba.
        return (ent(v) if float(v).is_integer()
                else n(v, 5).replace("-", "\u2212"))
    return str(v)


def esc_celda(t):
    """El rótulo de un paso, escapado antes de entrar en el `<th>`.

    Los rótulos vienen de `genera_soluciones.R` y se volcaban crudos. Uno
    traía `r <= 20 % del rango`: se renderiza bien por pura suerte —el
    tokenizador de HTML5 no abre etiqueta con `<` seguido de un carácter que
    no es letra— y bastaba un rótulo que empezara por `<a` para partir la
    tabla. El rótulo ya dice `≤`; esto es el cinturón.
    """
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def ejercicio(k, e):
    """El marcado de la CASA, no uno inventado.

    `cuenta_sitio.py` cuenta los ejercicios por `.ejercicio-guiado` y el
    desplegable se cablea por `.ejercicio-boton`; inventarse selectores
    deja un capítulo que se ve perfecto, con cero ejercicios contados y
    los botones muertos, sin un solo error en consola (A.13).
    """
    pasos = "".join(
        f"                <tr><th scope=\"row\">{esc_celda(p['paso'])}</th>"
        f"<td>{valor_paso(p['valor'])}</td></tr>\n"
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
        escala, la corrección de borde y la referencia contra la que se compara. Cuadrantes,
        G, F, K, g y envolventes son herramientas distintas, y todas obligan a fijar esas
        cuatro cosas y a declararlas.</p>

      <p>Ocho preguntas, sin nota, que se suman a las cuatro del módulo 6. Cada opción trae
        su explicación, así que equivocarse aquí vale tanto como acertar.</p>

{quiz_html('cap4-quiz', 'Autoevaluación del capítulo 4',
           'Ocho preguntas sobre ventana, intensidad, funciones de resumen, borde y envolventes.')}

      <p>Y cinco ejercicios guiados con su solución calculada. Los cinco terminan en una
        decisión que hay que defender, que es lo que este capítulo entrena de verdad.</p>

{EJ}
      <div class="tip-box">
        <h4>Dónde sigue esto</h4>
        <p style="margin-bottom:0;">El capítulo 5 recoge el hilo donde éste lo deja: en vez
        de resumir el patrón con funciones, estima la <strong>intensidad como superficie</strong>
        —el suavizado por núcleos— y luego la modela con covariables. La pregunta que abre
        aquel capítulo es la que el módulo 9 dejó pendiente: si λ no es constante, ¿cómo es?
        Mientras no se conteste, el exceso de parejas de Bogotá no se puede llamar atracción.
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
                   'de la suya: mismo χ², sin grumos.') + TABLA_CEGUERA)
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
    // OJO A LOS CUATRO DÍGITOS. `toLocaleString('es-ES')` NO separa los
    // millares de cuatro cifras —«2000», pero «13 767»—, que es la regla del
    // español; `ent()`, en Python, los separa siempre. Con las dos convivían,
    // la prosa decía «2 000 realizaciones» y la lectura del gráfico de ese
    // mismo módulo «2000». Se agrupa a mano para que el navegador escriba lo
    // que escribe la prosa, y el fino es el mismo U+202F.
    const miles4 = x => String(Math.round(Number(x)))
      .replace(/\B(?=(\d{3})+(?!\d))/g, ' ');

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

    // EL GRUPO ES PARTE DEL BOTÓN, y no lo era. `cap4-kl` mete DOS grupos
    // en el mismo contenedor —los cuatro patrones y las dos vistas— y al
    // limpiar `.sim-btn` a secas, elegir un patrón borraba la marca de la
    // vista: el gráfico seguía enseñando L − r y ningún botón lo decía.
    // Marcando el grupo, cada uno limpia el suyo. Los simuladores de un
    // solo grupo no notan la diferencia.
    function botones4(raiz, ops, alPulsar, activo, grupo) {
      const cont = raiz.querySelector('.simulador-controles');
      if (!cont) return;
      const g = grupo || 'principal';
      cont.innerHTML = '';
      ops.forEach((op, i) => {
        const b = document.createElement('button');
        b.className = 'sim-btn' + (i === (activo || 0) ? ' active' : '');
        b.dataset.grupo = g;
        b.setAttribute('aria-pressed', i === (activo || 0) ? 'true' : 'false');
        b.textContent = op.etiqueta;
        b.onclick = () => {
          cont.querySelectorAll(`.sim-btn[data-grupo="${g}"]`).forEach(x => {
            x.classList.remove('active');
            x.setAttribute('aria-pressed', 'false');
          });
          b.classList.add('active');
          b.setAttribute('aria-pressed', 'true');
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
        // LA NULA CORRECTA, y no el 1 de los libros. Esta fila decía «bajo
        // Poisson valdría 1» sobre una rejilla recortada donde vale 15,23: es
        // el defecto R1 del A.30.3, que se arregló en la prosa y en el quiz y
        // se quedó vivo AQUÍ. Tres superficies para una misma afirmación —el
        // párrafo, la lectura del simulador y la retroalimentación— y la del
        // medio no la mira ningún auditor.
        ['bajo Poisson valdría', n5(q.dispersion_nula, 2) + ' · no 1, porque las celdas no miden igual'],
        ['χ²', n5(q.chi2, 2)],
        ['la celda más poblada', q.maximo + ' sedes'],
        ['celdas con esperanza &lt; 5', q.celdas_esperanza_baja]
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
                    x: { type: 'category', ticks: { callback: function (v) { return this.getLabelForValue(v); } }, title: { display: true, text: '' } } } }
      });
      const pinta = () => {
        if (vista === 'conteo') {
          g.data.labels = m.hist_k;
          g.data.datasets = [
            { type: 'bar', label: 'realizaciones', data: m.hist_obs, backgroundColor: C4.verde },
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
            { type: 'bar', label: 'R de realizaciones de azar puro',
              data: m.R_csr.hist_conteo, backgroundColor: C4.morado }
          ];
          g.options.scales.x.title.text = 'índice de Clark-Evans';
          lectura4(raiz, [
            ['media de R', n5(m.R_csr.media)],
            ['recorrido', n5(m.R_csr.min, 3) + ' – ' + n5(m.R_csr.max, 3)],
            ['intervalo central 95 %', n5(m.R_csr.q025, 3) + ' – ' + n5(m.R_csr.q975, 3)],
            ['darían «agregado» leyendo R &lt; 1', miles4(m.R_csr.bajo_1) + ' de ' + miles4(m.R_csr.n)]
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
          // El color codifica «rechaza al 5 %» y una leyenda de un solo
          // recuadro gris rotulado «χ²» decía justo lo contrario. Se
          // apaga y el código de color va en el pie, en palabras.
          plugins: { legend: { display: false },
            // El tooltip dice el porqué de la barra pálida: cuántas de las
            // celdas vivas de ESA rejilla esperan menos de 5 puntos.
            tooltip: { callbacks: {
              title: its => 'rejilla ' + its[0].label + '×' + its[0].label,
              label: it => 'χ² = ' + n5(it.raw, 2),
              afterLabel: it => {
                const b = D4.m6[CLAVES[i]], k = it.dataIndex;
                return b.celdas_esperanza_baja[k] + ' de ' + b.celdas[k] +
                       ' celdas vivas con esperanza < 5';
              } } } },
          scales: { y: { type: 'logarithmic', title: { display: true, text: 'χ² (escala log)' } },
                    x: { type: 'category', ticks: { callback: function (v) { return this.getLabelForValue(v); } }, title: { display: true, text: 'lado de la rejilla (nx)' } } } }
      });
      const pinta = () => {
        const b = D4.m6[CLAVES[i]];
        g.data.labels = b.nx;
        // DOS CODIFICACIONES, una por cada pregunta del módulo. El color dice
        // si esa rejilla rechaza al 5 %; el relleno, si respeta el supuesto
        // del χ²: llena si ninguna celda viva espera menos de 5 puntos,
        // pálida con borde si alguna sí. La lectura decía «esperanza < 5
        // desde nx = 3» para Bogotá, y era falso: la ventana recorta las
        // celdas, y la de 5×5 lo respeta después de que 3×3 y 4×4 lo
        // rompieran. «Desde» solo vale con celdas iguales, así que la
        // lectura enumera las rejillas en vez de dar un umbral.
        const rompe = b.celdas_esperanza_baja.map(v => v > 0);
        const base = b.rechaza.map(r => r ? C4.rojo : C4.gris);
        g.data.datasets = [{ type: 'bar', label: 'χ²', data: b.chi2,
          backgroundColor: base.map((c, k) => rompe[k] ? c + '40' : c),
          borderColor: base, borderWidth: rompe.map(r => r ? 1.5 : 0) }];
        g.options.scales.y.min = Math.min.apply(null, b.chi2) / 2;
        g.update();
        const rech = b.rechaza.reduce((a, v) => a + v, 0);
        const rejillas = pred => {
          const ks = b.nx.filter((_, k) => pred(k)).map(v => v + '×' + v);
          return ks.length ? ks.join(', ') : 'ninguna';
        };
        lectura4(raiz, [
          ['patrón', ETQ[i]],
          ['rechazan al 5 %', rech + ' de ' + b.nx.length],
          ['respetan el supuesto', rejillas(k => !rompe[k])],
          ['lo respetan y rechazan', rejillas(k => !rompe[k] && b.rechaza[k])],
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
        // UNA SOLA CURVA DE CSR, y no dos. Había una «G bajo CSR» y una
        // «F bajo CSR», cada una de su color, y el módulo dice que son la
        // misma función: dibujadas así parecían dos referencias. Se pinta
        // la de F, que es la fórmula evaluada en sus nodos exactos.
        // Y LA G SIN CORREGIR, que el párrafo de Kaplan-Meier decía dibujar
        // («por eso el capítulo dibuja las dos») y no se dibujaba: estaba
        // en el JSON y nada la leía. En los de libro va casi encima de la
        // corregida; en Bogotá es la única que enseña el átomo en r = 0.
        // Va la ÚLTIMA y punteada: Chart.js pinta en orden, y debajo de la
        // verde no se veía ni el salto que justifica dibujarla.
        g.data.datasets = [
          { label: 'G corregida', data: curva4(d.r_g, d.g_obs), borderColor: C4.verde,
            pointRadius: 0, tension: 0.2 },
          { label: 'F corregida', data: curva4(d.r_f, d.f_obs), borderColor: C4.naranja,
            pointRadius: 0, tension: 0.2 },
          { label: 'CSR, la de las dos', data: curva4(d.r_f, d.f_teo), borderColor: C4.azul,
            borderDash: [5, 4], pointRadius: 0, tension: 0.2 },
          { label: 'G sin corregir', data: curva4(d.r_g, d.g_emp), borderColor: C4.gris,
            borderWidth: 1.5, borderDash: [2, 3], pointRadius: 0, tension: 0 }
        ];
        g.update();
        const dec = x => n5(x, x > 10 ? 2 : 5);
        lectura4(raiz, [
          ['patrón', d.nombre], ['n', miles4(d.n)],
          ['puntos coincidentes', d.coincidentes],
          ['G sin corregir en r = 0', n5(d.g_emp_en_cero, 6)],
          ['G llega a la mitad en r', dec(d.g_mediana)],
          ['F llega a la mitad en r', dec(d.f_mediana)],
          ['las dos, bajo CSR', dec(d.csr_mediana)],
          ['sitios de F dentro de la ventana', miles4(d.f_sitios) + ' de ' + miles4(d.f_rejilla)]
        ]);
      };
      botones4(raiz, CLAVES.map((c, k) => ({ etiqueta: ETQ[k], valor: k })),
               k => { i = k; pinta(); }, 2);
      pinta();
      return [g];
    };

    // --- Módulo 7 · la función J -------------------------------------
    // La J viene hecha del precálculo, con G y F por muestra reducida y
    // solo donde F <= 0,9. Aquí no se divide nada: un cociente calculado en
    // el navegador sería una cifra que no auditó nadie.
    // EJE LINEAL, NO LOGARÍTMICO. En escala log J = 1 quedaría en el centro,
    // pero la J de las secuoyas llega a 0 —todas las plántulas que cuentan
    // tienen ya vecina— y el cero no existe en un eje log: la curva se
    // cortaría justo en el punto que el módulo comenta.
    // Y LA LECTURA NO DA RÉGIMEN, por la lección que ya dejó `cap4-kl`: sin
    // banda del azar, una J de 1,5 no distingue un patrón regular de unos
    // pinos aleatorios, y el módulo lo enseña con esos mismos pinos.
    SIMULADORES['cap4-j'] = function (raiz) {
      const CLAVES = ['cells', 'japanesepines', 'redwood', 'bogota'];
      const ETQ = ['Células', 'Pinos japoneses', 'Secuoyas', 'Sedes de Bogotá'];
      let i = 1;
      const ctx = raiz.querySelector('canvas').getContext('2d');
      const g = new Chart(ctx, {
        type: 'line', data: { datasets: [] },
        options: { responsive: true, maintainAspectRatio: false, parsing: false,
          scales: ejesXY('r', 'J(r)') }
      });
      const pinta = () => {
        const d = D4.m7[CLAVES[i]];
        g.data.datasets = [
          { label: 'J observada', data: curva4(d.r_j, d.j_obs), borderColor: C4.morado,
            pointRadius: 0, tension: 0.2 },
          { label: 'CSR (J = 1)', data: curva4(d.r_j, d.r_j.map(() => 1)), borderColor: C4.gris,
            borderDash: [5, 4], pointRadius: 0 }
        ];
        g.update();
        const dec = x => n5(x, x > 10 ? 1 : 4);
        lectura4(raiz, [
          ['patrón', d.nombre],
          ['tramo dibujado', 'r ≤ ' + dec(d.j_r_lim) + ', donde F ≤ ' + n5(D4.m7.j_umbral_f, 1)],
          ['J en r = 0', n5(d.j_en_cero, 4)],
          ['J mínima', n5(d.j_min, 4) + ' en r = ' + dec(d.r_j_min)],
          ['J máxima', n5(d.j_max, 4) + ' en r = ' + dec(d.r_j_max)],
          ['distancias con J &lt; 1', d.j_bajo_1 + ' de ' + d.j_nodos]
        ]);
      };
      botones4(raiz, CLAVES.map((c, k) => ({ etiqueta: ETQ[k], valor: k })),
               k => { i = k; pinta(); }, 1);
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
        // LO QUE ESTA LECTURA PUEDE DECIR Y LO QUE NO. Antes ponía
        // «regular» en cuanto L − r salía negativa, así que a los pinos
        // japoneses —los ALEATORIOS del capítulo— los llamaba regulares, y
        // ningún patrón podía salir compatible con CSR. Pero este simulador
        // no tiene banda del azar: una desviación sola no establece un
        // régimen, que es exactamente lo que enseña el módulo 4. Así que
        // dice hacia dónde se va la curva, con su signo, y deja el
        // veredicto para la envolvente del módulo 11.
        lectura4(raiz, [
          ['patrón', d.nombre], ['corrección', d.correccion],
          ['L − r en el máximo', (d.desvio_con_signo > 0 ? '+' : '−')
            + n5(Math.abs(d.desvio_con_signo), Math.abs(d.desvio_con_signo) > 10 ? 2 : 5)],
          ['a distancia r', n5(d.r_max_desvio, d.r_max_desvio > 10 ? 0 : 4)],
          ['hacia dónde', d.desvio_con_signo > 0
            ? 'por encima de la recta (agregación)'
            : 'por debajo de la recta (regularidad)'],
          ['¿es significativo?', 'hace falta la envolvente del módulo 11']
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
        b.dataset.grupo = 'vista';
        b.setAttribute('aria-pressed', v === vista ? 'true' : 'false');
        b.textContent = etq;
        b.onclick = () => {
          cont.querySelectorAll('.sim-btn[data-grupo="vista"]').forEach(x => {
            x.classList.remove('active');
            x.setAttribute('aria-pressed', 'false');
          });
          b.classList.add('active');
          b.setAttribute('aria-pressed', 'true');
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
          // DOS CIFRAS, Y NO SON LA MISMA. Esta fila decía «g vuelve a 1
          // pasada r» y enseñaba `r_ultimo_cruce`, que es el último r en
          // que g se APARTA de 1 en cualquier dirección: sobre los pinos y
          // las secuoyas cae en el último nodo del barrido, donde g vale
          // 1.21 y 0.76. El regreso a 1 es `r_vuelve_a_1`, que es la que
          // usa la prosa y la que vale «hasta dónde llega el exceso»; y es
          // nula cuando g no vuelve dentro del rango medido.
          ['g vuelve a 1 en r', gg.r_vuelve_a_1 == null ? 'no vuelve en el barrido'
             : n5(gg.r_vuelve_a_1, gg.r_vuelve_a_1 > 10 ? 0 : 4)],
          ['último r con g lejos de 1', n5(gg.r_ultimo_cruce, gg.r_ultimo_cruce > 10 ? 0 : 4)],
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
        const ts = e.tasa_salida;   // la del patrón elegido, no una cableada
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
      // El barrido entero ya está en el eje x, así que el mando no puede
      // «cambiar el gráfico»: lo que hace es señalar en él. Sin esto los
      // cuatro botones dejaban el lienzo idéntico mientras el pie mandaba
      // moverlos, que es el defecto que la revisión llamó «mando que no
      // mueve el dibujo».
      const apaga = c => c + '55';
      const pinta = () => {
        const z = esc[i];
        g.data.datasets[0].backgroundColor = esc.map((_, k) => k === i ? C4.rojo : apaga(C4.rojo));
        g.data.datasets[1].backgroundColor = esc.map((_, k) => k === i ? C4.verde : apaga(C4.verde));
        g.update();
        lectura4(raiz, [
          ['nsim', z.nsim],
          ['nivel de la banda por defecto', n5(z.nivel_defecto, 4)],
          ['nrank para el 5 %', n5(z.nrank_para_5pct, 2)],
          ['¿alcanza el 5 %?', z.alcanza_5pct ? 'sí' : 'no'],
          ['p mínimo', n5(z.p_minimo)]
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
          { texto: 'Decir cuál es la ventana de observación usada', correcta: true,
            retro: 'Eso es. Con el perímetro urbano salen ' + n5(D4.m1.urbana.lambda_km2, 4) + ' sedes/km²; con el Distrito Capital entero, ' + n5(D4.m1.dc.lambda_km2, 4) + '. La misma ciudad y el mismo dato, con un factor de ' + n5(D4.m1.factor_lambda, 2) + ' entre las dos.' },
          { texto: 'La intensidad es una propiedad del dato, no del recinto',
            retro: 'No lo es. La intensidad es n dividido por el área de la ventana, y la ventana la elige quien analiza.' },
          { texto: 'Decir cuántos colegios hay en total en la ciudad',
            retro: 'Ayuda, pero no arregla el problema: el número de sedes apenas cambia entre las dos ventanas — sube un ' + n5(D4.m1.aumento_n_pct, 1) + ' % — y la intensidad se cuadruplica.' },
          { texto: 'Usar hectáreas, que es la unidad de la escala urbana',
            retro: 'La unidad no cambia el problema: la misma cifra en hectáreas es ' + n5(D4.m2.lambda_urbana_ha, 4) + ', y sigue dependiendo de qué ventana se usó.' }
        ] },
      {
        tipo: 'opcion',
        pregunta: 'Dos patrones tienen exactamente el mismo χ² en el test de cuadrantes. ¿Qué se puede concluir?',
        opciones: [
          { texto: 'Que sus conteos por celda coinciden, y nada de lo que hay dentro', correcta: true,
            retro: 'Correcto, y el módulo 5 lo construye a propósito: los dos patrones dan χ² = ' + n5(D4.m5.original.chi2, 4) + ' y su distancia media al vecino se multiplica por ' + n5(D4.m5.nn_cociente, 2) + '.' },
          { texto: 'Poco: el χ² solo compara la intensidad media de los dos',
            retro: 'No. El χ² solo usa cuántos puntos hay en cada celda, así que dos repartos idénticos por celda le dan el mismo número aunque los puntos estén colocados de forma opuesta.' },
          { texto: 'Que los dos colocan sus puntos de una manera muy parecida',
            retro: 'Tampoco: el χ² del módulo 5 rechaza en los dos casos. Lo que no distingue es la estructura DENTRO de cada celda.' },
          { texto: 'Que ninguno de los dos se aparta de una intensidad constante',
            retro: 'No se puede concluir, ni en un sentido ni en el otro. Que los dos χ² coincidan no dice si son grandes o pequeños; y aunque lo dijera, el test no separa una intensidad variable de un agrupamiento: rechazar no demuestra la primera, y no rechazar no demuestra una intensidad constante.' }
        ] },
      {
        tipo: 'multiple',
        pregunta: 'El test de cuadrantes sobre las sedes de Bogotá con una rejilla 10×10 rechaza con un p-valor minúsculo. ¿Qué afirmaciones son correctas?',
        opciones: [
          { texto: 'El patrón no es compatible con un Poisson homogéneo', correcta: true,
            retro: 'Eso es exactamente lo que dice el test, ni más ni menos: la nula es el Poisson homogéneo, y se rechaza.' },
          { texto: 'Hay celdas con esperanza menor que 5, y ahí el χ² es discutible', correcta: true,
            retro: 'Cierto: son ' + D4.m2.urbana.celdas_esperanza_baja + ' de ' + D4.m2.urbana.celdas + ' celdas vivas, porque la ventana las recorta.' },
          { texto: 'La intensidad no es constante dentro de la ventana urbana observada',
            retro: 'No queda demostrado. La nula que se rechaza son las DOS propiedades juntas, así que el rechazo es compatible con una λ perfectamente constante cuyos puntos se agrupen. El test no reparte la culpa.' },
          { texto: 'Los colegios se atraen entre sí a las distancias más cortas',
            retro: 'No queda demostrado. La nula que se rechaza son las DOS propiedades juntas, así que el rechazo es igual de compatible con puntos independientes sobre una λ que cambia dentro de la ventana, sin atracción ninguna. Le pasa lo mismo que a la afirmación de que la intensidad no es constante: cada una culpa a una sola de las dos propiedades, y el χ² no tiene con qué elegir entre ellas. Solo cuenta puntos por celda; no mide distancias entre ellos, ni cortas ni largas.' }
        ] },
      {
        tipo: 'opcion',
        pregunta: 'Sobre las secuoyas, el test de cuadrantes rechaza con rejilla 5×5 y NO rechaza con 2×2. ¿Qué se hace con eso?',
        opciones: [
          { texto: 'Declarar el tamaño de celda, que es parte del resultado y no del método', correcta: true,
            retro: 'Eso es. De los ' + D4.m6.nxs.length + ' tamaños barridos rechazan ' + D4.m6.redwood_rechazos + '; el que no lo hace es el más grueso, y no porque el patrón cambie sino porque con cuatro celdas no hay resolución. Es el efecto de escala del MAUP, con otro nombre.' },
          { texto: 'Quedarse con la rejilla fina, porque es la que mejor resuelve los grumos',
            retro: 'Es la que más resuelve y también la que rompe el supuesto del χ², que pide al menos 5 puntos esperados en cada celda: desde nx = ' + D4.m6.redwood_nx_esperanza_baja + ' aparecen celdas con esperanza menor que 5. Elegir por resolución es elegir un χ² en el que ya no se puede confiar.' },
          { texto: 'Fiarse de la rejilla gruesa, que es la que respeta la aproximación del χ²',
            retro: 'Respeta el supuesto del χ² —ninguna celda espera menos de 5 puntos— y no ve nada: con 2×2 no rechaza un patrón que está claramente agregado. El supuesto descarta las rejillas demasiado finas, pero no elige entre las que quedan: la de 3×3 también lo respeta, y rechaza.' },
          { texto: 'Promediar los p-valores de los diez tamaños y quedarse con esa media',
            retro: 'No existe tal cosa: los diez contrastes se hacen sobre el mismo dato, no son independientes, y su promedio no tiene distribución nula conocida. La salida no es aritmética: es declarar la escala.' }
        ] }
    ];

    AUTOEVALUACIONES['cap4-quiz'] = [
      {
        tipo: 'opcion',
        pregunta: '¿Cuáles son las DOS propiedades que definen la aleatoriedad espacial completa (CSR)?',
        opciones: [
          { texto: 'El conteo de cada región sigue una Poisson y, dado ese conteo, las posiciones son uniformes e independientes', correcta: true,
            retro: 'Eso es, y la primera es la que se olvida. Por eso dos realizaciones del mismo proceso no tienen el mismo n: en ' + miles4(D4.m4.n_realizaciones) + ' simulaciones el conteo va de ' + D4.m4.conteo_min + ' a ' + D4.m4.conteo_max + '.' },
          { texto: 'Las posiciones son uniformes e independientes y el número total de puntos está fijado',
            retro: 'La segunda mitad es falsa: si n fuera fijo no habría variabilidad de conteos, y la varianza observada es ' + n5(D4.m4.conteo_var, 2) + ', prácticamente igual a la media.' },
          { texto: 'Los puntos guardan entre sí una distancia mínima y por eso se reparten parejos',
            retro: 'Eso describe un patrón REGULAR, que es lo contrario de aleatorio. Las células tienen R = ' + n5(D4.m3.cells.clark_evans, 4) + '.' },
          { texto: 'La intensidad es constante en la ventana y los puntos se atraen entre sí débilmente',
            retro: 'La atracción, aunque sea débil, ya no es CSR: sería un proceso de conglomerado.' }
        ] },
      {
        tipo: 'opcion',
        pregunta: 'Una realización de un proceso CSR da un índice de Clark-Evans de 0.95. ¿Qué se concluye?',
        opciones: [
          { texto: 'Que ese valor cae dentro de lo que el azar produce a menudo', correcta: true,
            retro: 'Exacto. Sobre ' + miles4(D4.m4.R_csr.n) + ' realizaciones de azar puro, R recorrió de ' + n5(D4.m4.R_csr.min, 3) + ' a ' + n5(D4.m4.R_csr.max, 3) + ', y ' + miles4(D4.m4.R_csr.bajo_1) + ' de ellas quedaron por debajo de 1.' },
          { texto: 'Que el patrón está agregado, porque su R quedó por debajo de 1',
            retro: 'Ese es justo el error que el módulo 4 desmonta: comparar una R contra 1 sin saber cuánto se mueve el azar.' },
          { texto: 'Que la simulación falló, porque bajo CSR R debería dar 1',
            retro: 'No: el intervalo central del 95 % de R bajo CSR va de ' + n5(D4.m4.R_csr.q025, 3) + ' a ' + n5(D4.m4.R_csr.q975, 3) + ', y 0.95 cae dentro. No hay nada que arreglar.' },
          { texto: 'Que la ventana es demasiado pequeña para que R sea informativo',
            retro: 'El tamaño de la ventana influye en la precisión, pero el valor observado es perfectamente compatible con CSR.' }
        ] },
      {
        tipo: 'opcion',
        pregunta: '¿Qué distingue a la función G de la función F?',
        opciones: [
          { texto: 'G mide desde los puntos del patrón; F, desde sitios cualesquiera de la ventana', correcta: true,
            retro: 'Eso es. Por eso separan los regímenes en direcciones opuestas: un patrón agregado tiene vecinos cerca (G sube pronto) y deja huecos grandes (F sube tarde).' },
          { texto: 'G mide distancias entre puntos del patrón y F cuenta puntos dentro de discos',
            retro: 'Las dos usan distancias. Lo que cambia es desde dónde se miden.' },
          { texto: 'G lleva incorporada la corrección de borde y F se estima sin corregirla',
            retro: 'Las dos admiten corrección de borde; ninguna la lleva incorporada por definición.' },
          { texto: 'G describe bien los patrones agregados y F describe bien los regulares',
            retro: 'Las dos valen para cualquier patrón: son descripciones, no tests específicos de un régimen.' }
        ] },
      {
        tipo: 'numerica',
        pregunta: 'La G empírica de las sedes de Bogotá EN LA VENTANA URBANA vale 0.037494 en r = 0. ¿Cuántas de esas sedes comparten coordenada exacta con otra?',
        respuesta: D4.m7.bogota.coincidentes, tolerancia: 0.5,
        retroAcierto: 'Son ' + D4.m7.bogota.coincidentes + ' sedes, el ' + n5(D4.m7.bogota.coincidentes_pct, 2) + ' % del patrón, con hasta ' + D4.m7.duplicados.maximo_por_sitio + ' en un mismo punto: sedes distintas en el mismo edificio. Un patrón con duplicados no es un proceso puntual simple, y el salto de G en r = 0 es exactamente esa fracción.',
        retroFallo: 'Son ' + D4.m7.bogota.coincidentes + ' = 0.037494 × ' + miles4(D4.m7.bogota.n) + ', las sedes que caen DENTRO de la ventana urbana. Si te salió 83 multiplicaste por las ' + miles4(D4.m1.sedes_total) + ' georreferenciadas: el módulo 1 avisó de que ppp() descarta las que quedan fuera. La G es una proporción sobre la ventana, siempre.'
      },
      {
        tipo: 'opcion',
        pregunta: 'K(r) de un patrón sigue por encima de su valor teórico a 500 m, aunque la agregación real ocurre a 20 m. ¿Por qué?',
        opciones: [
          { texto: 'Porque K es acumulativa y arrastra los vecinos ya contados', correcta: true,
            retro: 'Eso es, y es lo que g(r) arregla mirando solo el anillo de radio r. Sobre las secuoyas, g alcanza ' + n5(D4.m9.redwood.g_max, 2) + ' en r = ' + n5(D4.m9.redwood.r_g_max, 4) + ' y vuelve a 1 mientras K sigue despegada de su teórica.' },
          { texto: 'Porque el efecto de borde infla K a las distancias grandes',
            retro: 'El efecto de borde va en el sentido contrario: sin corregir, K se queda por DEBAJO, hasta un ' + n5(D4.m10.sesgo_max_pct, 1) + ' % en este capítulo.' },
          { texto: 'Porque la intensidad del patrón crece con la distancia medida',
            retro: 'La intensidad es una propiedad de cada lugar de la ventana, no de la distancia a la que se mire. Lo que crece con r es el disco de K, que a 500 m sigue conteniendo los vecinos que ya contó a 20 m.' },
          { texto: 'Porque la ventana de observación no es un rectángulo simple',
            retro: 'El arrastre ocurre igual en una ventana rectangular. Es acumulación, no geometría.' }
        ] },
      {
        tipo: 'multiple',
        pregunta: 'Sobre el efecto de borde en la estimación de K, ¿qué es cierto?',
        opciones: [
          { texto: 'Ignorarlo hace que el patrón parezca más regular de lo que es', correcta: true,
            retro: 'Correcto, y en una sola dirección: a un punto pegado al borde le faltan vecinos que nadie observó, así que K queda por DEBAJO de su valor real — aquí hasta un ' + n5(D4.m10.sesgo_max_pct, 1) + ' %.' },
          { texto: 'El sesgo crece con r, porque a r grande más discos tocan el borde', correcta: true,
            retro: 'Sí, y de forma monótona: el déficit llega a su máximo del ' + n5(D4.m10.sesgo_max_pct, 1) + ' % en el último r medido, ' + n5(D4.m10.r_sesgo_max, 0) + ' m.' },
          { texto: 'Es ruido: se compensa entre los puntos del centro y los del borde',
            retro: 'No se compensa, y esa es la frase del módulo 10: no añade ruido, añade DIRECCIÓN. A los puntos del centro no les sobran vecinos que cancelen los que le faltan al borde. Faltan siempre, nunca sobran.' },
          { texto: 'La corrección isotrópica y la de traslación cuestan lo mismo de calcular',
            retro: 'No sobre una ventana de verdad: aquí la isotrópica cuesta ' + n5(D4.m10.coste.veces_isotropica_sobre_traslacion, 0) + ' veces lo que la de traslación, porque recorre el perímetro pareja a pareja.' }
        ] },
      {
        tipo: 'opcion',
        pregunta: 'La curva observada se sale de la banda del 95 % en un tramo corto de r. ¿Qué se puede afirmar?',
        opciones: [
          { texto: 'Que la banda es puntual, y mirarla entera son muchos contrastes a la vez', correcta: true,
            retro: 'Eso es. De las ' + miles4(D4.m11.tasa_salida_bogota.nsim) + ' simulaciones de CSR puro con que se construyó la banda, el ' + n5(D4.m11.tasa_salida_bogota.pct, 1) + ' % se sale de ella en algún r. Para la curva entera hace falta un test global.' },
          { texto: 'Que el patrón no es CSR, con un p menor que 0.05 para la curva entera',
            retro: 'Ese es exactamente el error que el módulo 11 desmonta: el 5 % es el nivel de CADA r por separado, no el de la curva.' },
          { texto: 'Que conviene subir nsim para estrechar la banda y así confirmarlo',
            retro: 'Ajustar nsim mirando el resultado es fabricar el resultado. Y además no funciona por un motivo que la última pregunta de este cuestionario te va a pedir: la banda por defecto no es la misma banda cuando cambia nsim.' },
          { texto: 'Que la corrección de borde que se usó es insuficiente en ese tramo',
            retro: 'No hay nada en el enunciado que apunte al borde; y la banda se construye con la misma corrección que la curva.' }
        ] },
      {
        tipo: 'opcion',
        pregunta: 'Se pasa de 39 a 999 simulaciones sin tocar nada más. ¿Qué le ocurre a la banda por defecto de envelope()?',
        opciones: [
          { texto: 'Se ensancha, porque su nivel puntual es 2/(nsim+1) y ha cambiado', correcta: true,
            retro: 'Eso es, y es contraintuitivo: la banda por defecto es el mínimo-máximo de las simulaciones. De 39 a 999 su ancho medio pasa de ' + n5(D4.m11.escala_nsim[1].ancho_defecto, 3) + ' a ' + n5(D4.m11.escala_nsim[3].ancho_defecto, 3) + ', y en el barrido entero, desde 19, se ensancha ×' + n5(D4.m11.escala_resumen.veces_defecto, 2) + '. Manteniendo el nivel fijo al 5 %, en cambio, se estrecha: de ' + n5(D4.m11.escala_nsim[1].ancho_5pct, 3) + ' a ' + n5(D4.m11.escala_nsim[3].ancho_5pct, 3) + '.' },
          { texto: 'Se estrecha, porque con más simulaciones hay más información sobre CSR',
            retro: 'Es lo que uno espera y no es lo que pasa: con nrank = 1 el nivel pasa de ' + n5(D4.m11.escala_nsim[1].nivel_defecto, 3) + ' a ' + n5(D4.m11.escala_nsim[3].nivel_defecto, 3) + ', o sea que son contrastes distintos.' },
          { texto: 'No cambia: la banda queda determinada por el patrón y su ventana',
            retro: 'Depende de las simulaciones, y por tanto de cuántas haya.' },
          { texto: 'Su ancho cae como uno partido por raíz de nsim, así que se reduce',
            retro: 'Ni se estrecha ni hay una regla tan simple.' }
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
    # El orden de las opciones se decide en `baraja_opciones.py`, y es la
    # corrección del 2026-09-02: escritas de una en una, las 51 preguntas de
    # los cinco capítulos tenían la correcta la PRIMERA, y el motor no baraja.
    doc = baraja_documento(doc, "cap4")

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
    # LA CLAVE DE LA RETROALIMENTACIÓN, COMPROBADA Y NO SUPUESTA (A.23.2).
    # Este capítulo escribió `respuesta` y `explicacion` donde el motor lee
    # `retro`, `retroAcierto` y `retroFallo`, y sus explicaciones por opción NO
    # SE DIBUJARON NUNCA: quien acertaba veía «Correcto.» y nada más, y quien
    # fallaba una numérica veía «La respuesta es N. undefined», porque la
    # guarda de `cerrar()` no puede salvar una plantilla que ya interpoló el
    # valor ausente. Se saldó el 2026-09-03; esto es para que no vuelva.
    opciones_quiz = doc.count("{ texto:")
    retros = doc.count("retro: '")
    if "respuesta: '" in doc or "explicacion: '" in doc:
        problemas.append("hay opciones con la clave `respuesta`/`explicacion`: "
                         "el motor lee `retro`, `retroAcierto` y `retroFallo`, "
                         "y lo que no lee no se dibuja")
    if retros != opciones_quiz:
        problemas.append(f"opciones de quiz sin `retro`: {opciones_quiz - retros} "
                         f"de {opciones_quiz}")
    for q in re.finditer(r"tipo: 'numerica'", doc):
        bloque = doc[q.start():q.start() + 1600]
        corte = bloque.find("tipo: '", 12)
        bloque = bloque[:corte] if corte > 0 else bloque
        if "retroAcierto:" not in bloque or "retroFallo:" not in bloque:
            problemas.append("una numérica sin `retroAcierto` o sin `retroFallo`: "
                             "quien falle verá «undefined» detrás de la respuesta")
    if problemas:
        print("\n  PROBLEMAS:")
        for p in problemas:
            print(f"   - {p}")
        return 1
    print("\n  Capítulo 4 ensamblado.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
