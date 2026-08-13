#!/usr/bin/env python3
"""
ensambla_cap1.py — construye el capítulo 1 del material (T1.2)

Material de Estadística Espacial 2026-II (20929).

POR QUÉ ESTO ES UN GUION Y NO UN HTML ESCRITO A MANO.

D10 del plan dice que ninguna cifra del material se escribe a mano. En
Diseño de Experimentos eso era una disciplina: se copiaban los números del
JSON y el auditor de prosa los contrastaba después. En Muestreo esa
disciplina falló —se colaron tres cifras escritas de memoria **mientras se
corregía justamente ese problema**—. Aquí deja de ser disciplina: el HTML
sale de este guion, y cada número está interpolado desde
`salidas/cap1_datos.json`, `cap1_mapas.json` y `cap1_soluciones.json`. Para
publicar una cifra falsa habría que escribirla en el precálculo, que es
donde `audita_cap1.py` la recalcularía desde las fuentes primarias.

CÓMO SE REPARTE EL TRABAJO, que también es deliberado:

  · La **prosa** vive en f-strings de Python y se interpola aquí. Es lo que
    audita `audita_texto_cap1.py`.
  · El **JavaScript** (simuladores, quiz, mapas) NO se interpola: recibe el
    JSON entero como `DATOS_CAP1` y saca de ahí sus cifras con `n5()`. Así
    las llaves de JS no pelean con las de los f-strings, y sobre todo: una
    pregunta del quiz no puede quedarse con una cifra vieja, porque no
    tiene ninguna cifra escrita.
  · Los **mapas estáticos** se registran con su JSON literal, no con una
    función. Es a propósito: `audita_texto_base.geomapas()` solo puede
    comprobar los cortes, el n y el peso de un mapa cuya fuente sea un
    literal. Registrarlos todos como función habría dejado esa familia
    entera sin comprobar, en verde.

Cada sustitución sobre la plantilla exige que su ancla aparezca
exactamente una vez, y cada región que se reemplaza declara un tope MÁXIMO
y otro MÍNIMO de líneas. Las tres guardas están porque las tres hicieron
falta: la primera por cómo el capítulo 7 de Muestreo sobrescribió al 6; la
segunda porque el ensamblador del fixture de T0.5 se comió 276 líneas del
motor buscando un `];` que estaba dentro de un comentario, y aun así
informó «limpio»; y la tercera —el mínimo— porque aquí, en T1.2, el ancla
de cierre casó DEMASIADO PRONTO y dejó vivos dos simuladores de
demostración, con el archivo bien formado y el informe en verde.

Y las guardas de SALIDA no son menos importantes que las de entrada: que
el guion escriba no significa que haya escrito bien. Comprueba que haya
doce módulos, que ningún lienzo se quede sin `aria-label`, que las dos
autoevaluaciones usen **solo tipos que el motor conoce y los cuatro que
tiene** —un tipo inventado no da error de sintaxis: revienta en tiempo de
ejecución y se lleva por delante todo lo que `loadModule()` llama
después—, y que ninguna fórmula lleve un espacio fino de Unicode, que
KaTeX no sabe medir.

Uso:  python3 precalculo/ensambla_cap1.py
      (desde la carpeta `Estadistica espacial/`)
"""
from __future__ import annotations

import json
import os
import re
import pathlib
import sys

RAIZ = pathlib.Path(__file__).resolve().parent.parent
SALIDAS = RAIZ / "precalculo" / "salidas"


def _ruta(var: str, defecto: pathlib.Path) -> pathlib.Path:
    """La ruta publicada, o la copia que apunte la variable de entorno.

    Mismo convenio que `audita_base.carga` y que `CAP1_HTML` del auditor de
    prosa, y por la misma razón: es lo que permite que un arnés de inyección
    ensamble desde JSON envenenados **sin escribir jamás sobre lo publicado**.

    Importa que `CAP1_DESTINO` exista además de las tres entradas: el
    ensamblador escribe el HTML ANTES de correr sus guardas, así que un arnés
    que solo redirigiera la entrada dejaría el capítulo publicado construido
    con datos rotos cada vez que inyecta. Con la salida redirigida, el arnés
    es de solo lectura sobre el árbol de verdad. (T1.3.n)
    """
    p = pathlib.Path(os.environ.get(var) or defecto)
    if var.endswith("DESTINO"):
        return p
    if not p.exists():
        sys.exit(f"PARADO: falta {p}")
    return p


PLANTILLA = _ruta("CAP1_PLANTILLA", RAIZ / "plantilla" / "plantilla-capitulo.html")
DESTINO = _ruta("CAP1_DESTINO",
                RAIZ / "Htmls_Espacial" / "capitulo-1-datos-espaciales.html")

D = json.loads(_ruta("CAP1_DATOS", SALIDAS / "cap1_datos.json")
               .read_text(encoding="utf-8"))
M = json.loads(_ruta("CAP1_MAPAS", SALIDAS / "cap1_mapas.json")
               .read_text(encoding="utf-8"))
S = json.loads(_ruta("CAP1_SOLUCIONES", SALIDAS / "cap1_soluciones.json")
               .read_text(encoding="utf-8"))

sn, pc, ac, gc = D["snow"], D["puntual_canonico"], D["area_canonico"], D["geo_canonico"]
co, tb, inf = D["colombia"], D["tobler"], D["inferencia"]
ir, ne, ur = D["inferencia_real"], D["n_efectivo"], D["una_realizacion"]
rv = D["realizaciones_vistas"]
rt = ne["rho_del_titular"]
es, ec, ag = D["escala"], D["escala_correlacion"], D["agregacion"]
eco, an, cv = D["ecosistema"], D["anatomia"], D["cv_espacial"]
sop = ac["soporte"]
agn, agco = D["agregacion_soporte"]["nc"], D["agregacion_soporte"]["colombia"]
cc = agn["condado_caso"]        # el condado que el mapa del módulo 7 señala
dm = D["diseno_modelo"]


def n(x, d=5):
    """Cinco decimales por defecto.

    Es la regla que Javier fijó el 2026-08-03 y no es una preferencia
    estética: `mide_punto_ciego.py` MIDIÓ que por debajo de cinco el
    índice de comparaciones del auditor absorbe las perturbaciones de un
    dígito —con cuatro se cuela el 8,65 %, con uno el 63 %—. Con cinco
    baja al 4,63 %.
    """
    return f"{float(x):.{d}f}"


def ent(x):
    """Entero con separador de millar fino, como en el resto del material.

    El separador es U+202F (espacio fino de no separación), que es lo
    tipográficamente correcto en español. **Pero KaTeX no lo entiende**:
    dentro de una fórmula avisa «Unrecognized Unicode character (8239)» y
    deja un hueco sin métrica. Para las fórmulas está `ent_mate()`, y el
    guarda de `main()` comprueba que no se cuele ninguno — porque se coló:
    el módulo 5 publicaba \\(n = 1 000\\) con este carácter dentro.
    """
    return f"{int(round(float(x))):,}".replace(",", " ")


def ent_mate(x):
    """El mismo entero, pero para DENTRO de una fórmula de KaTeX.

    Con `\\,`, que es el espacio fino de LaTeX y sí tiene métrica.
    """
    return f"{int(round(float(x))):,}".replace(",", r"\,")


def firma(valor, unidad=""):
    return f"<strong>{valor}</strong>{unidad}"


def cabecera(num, titulo, ingles, objetivo):
    """La cabecera común de los doce módulos."""
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
    """Un par de pestañas R/Python.

    Python NO es decorativo: los bloques se EJECUTAN encadenados en el
    entorno `geo_env` y sus `#>` se contrastan contra la salida real
    (`verifica_bloques.py`). Donde Python no tiene el paquete —HistData,
    spatstat.data, sp no existen allí— la pestaña lee el CSV que el
    precálculo exportó justo para eso, en vez de fingir un equivalente.
    """
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


# =====================================================================
# MÓDULO 1 · El mapa que cambió la epidemiología
# =====================================================================
# Abre con la prueba diagnóstica de entrada (decisión de Javier del
# 2026-08-04: dentro del capítulo, sin nota). Va ANTES de Snow y no al
# final: una diagnóstica que se hace después de leer el capítulo mide otra
# cosa.
#
# PERO NO ES LO PRIMERO QUE SE LEE, y esa corrección es de la misma fecha,
# por la tarde. La primera versión pegaba la caja del quiz al encabezado
# del módulo y saltaba de la octava pregunta a «Londres, verano de 1854»
# sin una palabra por medio. Son dos defectos y no uno: al lector se le
# pedía producir antes de haberle dado nada —este módulo es su primer
# contacto con todo el material—, y el corte del cuestionario al relato no
# lo amortiguaba nadie. Ahora el módulo abre con la prosa que sitúa el
# curso, la diagnóstica va detrás, y un párrafo puente la cierra y entrega
# el relato de Snow.
#
# La apertura tiene además una restricción que no se ve: no puede regalar
# ninguna de las ocho respuestas. Por eso enuncia el supuesto que se rompe
# —que una observación no dice nada sobre la siguiente— y NO dice en qué
# dirección se rompe el error estándar (pregunta 2), ni que la ventana
# forma parte del estimador (pregunta 8), ni cuáles son los tres tipos
# (pregunta 1).
MOD1 = cabecera(
    1, "El mapa que cambió la epidemiología", "Snow, 1854",
    "Ver un patrón puntual convertirse en un argumento, y medir exactamente "
    "cuánto argumenta.") + f"""
      <p>Casi toda la estadística que has visto hasta ahora descansa en un supuesto que nadie enuncia en voz
        alta: que una observación no dice nada sobre la siguiente. En cuanto cada dato lleva pegadas unas
        coordenadas, ese supuesto deja de ser inocente. Dos estaciones climáticas separadas por tres kilómetros
        no son dos observaciones independientes, y dos municipios vecinos tampoco. De qué se rompe cuando eso
        pasa, de cuánto se rompe —siempre con una cifra delante— y de qué se hace entonces trata el curso
        entero.</p>

      <p>Este capítulo es el mapa de los otros nueve, y no empieza por una definición sino por un dibujo de
        1854 que todavía abre los libros de la disciplina. Antes del dibujo, ocho preguntas para ti.</p>

      <div class="note">
        <p><strong>Ocho preguntas, cinco minutos, sin nota.</strong> No cuentan para nada y no hace falta que
          sepas las respuestas: están para que veas qué trae el curso y para que, cuando aciertes por intuición,
          sepas que la intuición ya la tenías. Cada retroalimentación te dice a qué módulo ir.</p>
        <p style="margin-bottom:0;">Si fallas muchas, estás exactamente donde tienes que estar en la semana 1.</p>
      </div>

      <div class="quiz" data-quiz="cap1-diagnostica">
        <h4><i class="fas fa-compass" aria-hidden="true"></i> Diagnóstica de entrada (sin nota)</h4>
        <p class="text-sm" style="margin-bottom:0;">Ocho preguntas sobre lo que el capítulo va a construir.</p>
        <div class="quiz-progreso" role="presentation"><div class="quiz-progreso-barra"></div></div>
        <div class="quiz-preguntas"></div>
        <div class="quiz-resumen" role="status" hidden></div>
        <div class="quiz-marcador">
          <span class="quiz-conteo"></span>
          <button type="button" class="quiz-reiniciar">Reiniciar</button>
        </div>
      </div>

      <p>Sea cual sea el resultado, el capítulo empieza igual. Ninguna de esas ocho preguntas se contesta de
        memoria: todas se contestan mirando un dato y midiendo, que es lo único que este curso va a pedirte. Y
        la primera vez que alguien contestó una de ellas —si un puñado de puntos sobre un plano está diciendo
        algo o es casualidad— no había estadística espacial que valiera: había un médico, un brote y un
        plano.</p>

      <p>Londres, verano de 1854. En el Soho mueren <strong>{sn['n_muertes']}</strong> personas de cólera en poco más
        de un mes. La teoría médica del momento culpa al aire viciado. John Snow sospecha del agua, no tiene con qué
        demostrarlo, y hace algo que entonces no era un método: <em>dibuja los muertos en un plano</em>, con las
        <strong>{sn['n_bombas']}</strong> bombas públicas del barrio encima.</p>

      <p>Ese plano es el primer objeto de este curso, y conviene mirarlo antes de definir nada. Ponlo en
        <em>Broad Street contra el resto</em> y fíjate en dónde cae la mancha.</p>

      <div class="simulador" data-simulador="snow-mapa">
        <h4><i class="fas fa-map-location-dot" aria-hidden="true"></i> El mapa de Snow, capa a capa</h4>
        <p class="simulador-intro">Las <strong>{sn['n_segmentos']}</strong> calles del Soho de fondo, las
          {sn['n_muertes']} muertes digitalizadas por Dodson y Tobler (NCGIA, 1992) y las {sn['n_bombas']} bombas en
          rombo. Conmuta entre colorear por bomba más próxima y resaltar solo Broad Street.</p>
        <div class="simulador-controles"></div>
        <div class="geomapa" data-geomapa="cap1-snow"></div>
        <div class="simulador-lectura"></div>
      </div>

      <p>La cifra que sostiene el mapa: de las {sn['n_muertes']} muertes,
        <strong>{sn['n_mas_cerca_broad']}</strong> tienen la bomba de Broad Street como la más próxima. Eso es el
        <strong>{n(sn['pct_mas_cerca_broad'])}&nbsp;%</strong>. Si las muertes se repartieran por igual entre las
        {sn['n_bombas']} bombas, a cada una le tocaría el {n(sn['pct_esperado_uniforme'])}&nbsp;%: Broad Street
        concentra <strong>{n(sn['razon_sobre_uniforme'])} veces</strong> lo que le tocaría.</p>

      <div class="definition">
        <h3>Y ahora la parte formal: qué es un patrón puntual</h3>
        <p>Lo que acabas de ver es un <strong>patrón puntual</strong>: un conjunto de localizaciones
          \\(\\{{s_1, \\dots, s_n\\}}\\) dentro de un dominio \\(D\\), donde <strong>lo aleatorio es dónde están los
          puntos</strong> — y también cuántos hay. No se ha medido nada en cada muerte: la muerte <em>es</em> el
          dato, y su valor es su posición.</p>
        <p style="margin-bottom:0;">Esa frase —«qué es aleatorio»— es la que reparte los diez capítulos del curso, y
          el módulo 2 la usa para separar los tres tipos de dato espacial.</p>
      </div>

      <p>La asignación de cada muerte a su bomba se calcula por distancia euclídea, y se contrasta con los polígonos
        de Thiessen que Tobler distribuye con el dato: coinciden en
        <strong>{sn['n_coinciden_tobler']} de {sn['n_muertes']}</strong>. Son dos construcciones distintas de la
        misma idea, y si discreparan habría que averiguar cuál está mal antes de publicar ninguna de las dos.</p>

""" + tabs(
    "La concentración alrededor de Broad Street, en R y en Python",
    """library(HistData)
data(Snow.deaths); data(Snow.pumps)

muertes &lt;- as.matrix(Snow.deaths[, c("x", "y")])
bombas  &lt;- as.matrix(Snow.pumps[,  c("x", "y")])
d &lt;- as.matrix(dist(rbind(muertes, bombas)))[1:nrow(muertes),
                                             nrow(muertes) + 1:nrow(bombas)]
mas_cerca &lt;- max.col(-d, ties.method = "first")
i_broad   &lt;- which(Snow.pumps$label == "Broad St")

cat(sprintf("%d de %d = %.5f %%\\n",
            sum(mas_cerca == i_broad), nrow(muertes),
            100 * mean(mas_cerca == i_broad)))
#&gt; """ + f"{sn['n_mas_cerca_broad']} de {sn['n_muertes']} = {n(sn['pct_mas_cerca_broad'])} %",
    """# HistData no existe en Python. El precalculo exporta el mismo dato a
# CSV (cap1_snow.csv) justo para que esta pestana no tenga que fingir.
import pandas as pd, numpy as np
from scipy.spatial import cKDTree

sw = pd.read_csv("precalculo/salidas/cap1_snow.csv")
mu = sw[sw.tipo == "muerte"][["x", "y"]].to_numpy()
bo = sw[sw.tipo == "bomba"]
i_broad = int(np.flatnonzero(bo.etiqueta.to_numpy() == "Broad St")[0])

_, mas_cerca = cKDTree(bo[["x", "y"]].to_numpy()).query(mu)
print(f"{(mas_cerca == i_broad).sum()} de {len(mu)} = "
      f"{100 * (mas_cerca == i_broad).mean():.5f} %")
#> """ + f"{sn['n_mas_cerca_broad']} de {sn['n_muertes']} = {n(sn['pct_mas_cerca_broad'])} %") + f"""
      <p>Hay una segunda mitad de la historia, y es la que suele contarse mal. El 8 de septiembre de 1854 la
        parroquia retiró el mango de la bomba de Broad Street, y el brote se apagó. La lectura cómoda es que lo apagó
        la retirada del mango. El dato dice otra cosa: el <strong>{n(sn['pct_ataques_antes_mango'])}&nbsp;%</strong>
        de los ataques había ocurrido <em>antes</em> de ese día, y desde el pico del {sn['fecha_pico']}
        —{sn['ataques_pico']} ataques— hasta el {sn['fecha_mango']} —{sn['ataques_dia_mango']}— ya habían caído un
        <strong>{n(sn['caida_hasta_mango_pct'])}&nbsp;%</strong>.</p>

      <div class="simulador" data-simulador="snow-serie">
        <h4><i class="fas fa-chart-line" aria-hidden="true"></i> La curva del brote y el día del mango</h4>
        <p class="simulador-intro">Ataques y muertes por día, del {sn['serie_fecha'][0]} al
          {sn['serie_fecha'][-1]}, con el día en que se retiró el mango marcado por la banda
          vertical. Conmuta a <strong>acumulado</strong> y mira por dónde va ya la curva cuando
          llega a la banda: el párrafo de arriba, dibujado.</p>
        <div class="simulador-controles"></div>
        <div class="grafico-wrapper" style="height:250px;">
          <canvas aria-label="Ataques y muertes diarias del brote de cólera del Soho, con el día de la retirada del mango marcado" role="img"></canvas>
        </div>
        <div class="simulador-lectura"></div>
      </div>

      <div class="warning">
        <p><strong>Lo que el mapa NO demuestra, y es la lección de método.</strong> El patrón demuestra una
          concentración alrededor de un punto. No distingue el agua de cualquier otra cosa que estuviera en esa
          esquina: una fábrica, una taberna, una parada. El argumento de Snow es <strong>geométrico</strong>, y lo
          que lo convierte en evidencia sobre el agua es el mecanismo que él ya sospechaba, no el mapa solo.</p>
        <p style="margin-bottom:0;">Guarda esa distinción. Vuelve en el capítulo 3 con la falacia ecológica y en el 8
          con los tres orígenes posibles de la dependencia espacial, que llevan a tres modelos distintos.</p>
      </div>
""" + CIERRE


# =====================================================================
# MÓDULO 2 · Los tres tipos de dato espacial
# =====================================================================
# Decisión de Javier del 2026-08-04: cada tipo se presenta DOS veces, con
# su canónico de la literatura y su gemelo colombiano. El canónico permite
# contrastar las cifras contra Baddeley, Cressie y Pebesma; el colombiano
# arranca el hilo del país en la semana 1 en vez de en el capítulo 3.
MOD2 = cabecera(
    2, "Los tres tipos de dato espacial", "Point, areal, geostatistical",
    "Aprender a preguntar «¿qué es aleatorio aquí?» —y después «¿de qué trozo "
    "de la unidad habla el número?»— antes de elegir ninguna herramienta. Cada "
    "tipo, dos veces: el canónico y el colombiano.") + f"""
      <p>Los tres tipos no se distinguen por el aspecto del mapa —los tres pueden verse como puntos de colores— sino
        por <strong>qué parte del dato es aleatoria</strong>. Esa pregunta decide el resto: qué se estima, qué se
        contrasta y qué software sirve.</p>

      <p>Conviene comprobar de entrada que eso no es una figura retórica. El módulo 3 pone tres patrones puntuales
        uno al lado del otro —secuoyas, pinos y células— y los tres son el mismo dibujo: unas decenas de puntos
        —{pc['redwood']['n']}, {pc['japanesepines']['n']} y {pc['cells']['n']}— sobre una ventana unitaria. Y sin
        embargo son tres procesos distintos, y la cifra que los separa cabe en una
        línea: la distancia media de cada punto a su vecino más próximo vale
        <strong>{n(pc['redwood']['nn_media'])}</strong> en las secuoyas,
        <strong>{n(pc['japanesepines']['nn_media'])}</strong> en los pinos y
        <strong>{n(pc['cells']['nn_media'])}</strong> en las células. El primero está agregado, el
        segundo no se distingue del azar y el tercero es más regular que el azar —y contra qué hay que comparar
        esas tres distancias para poder afirmarlo es exactamente lo que mide el módulo 3—. Tres imágenes
        parecidas, tres procesos distintos. Si el ojo no separa tres patrones <em>del mismo tipo</em>, con más
        razón no va a separar los tres tipos entre sí.</p>

      <p>Vienen seis mapas, que en realidad son <strong>tres pares</strong>: cada tipo dos veces, con su caso
        canónico de la literatura y su gemelo colombiano. Míralos antes de leer lo que va debajo de cada uno, y
        hazlo con la pregunta correcta. No es «¿qué se ve?», que es la que el ojo contesta solo y contesta mal. Es
        <strong>«¿qué saldría distinto si volviéramos a tomar el dato?»</strong>.</p>

      <div class="definition">
        <h3>1 · Patrón puntual — lo aleatorio es <em>dónde</em></h3>
        <p style="margin-bottom:0;">Los {pc['japanesepines']['n']} pinos de Numata (1961) sobre su ventana unitaria,
          y las {ent(co['puntual']['n'])} sedes educativas de Bogotá. En los dos casos no se ha medido nada en cada
          punto: el punto <em>es</em> el dato.</p>
      </div>
      <div class="geomapa" data-geomapa="cap1-pinos"></div>

      <p>Los pinos son el <strong>caso nulo</strong>, y por eso son el canónico. Su distancia media al vecino más
        próximo —<strong>{n(pc['japanesepines']['nn_media'])}</strong> en unidades de la ventana— es
        prácticamente la que daría tirar los {pc['japanesepines']['n']} puntos al azar sobre el cuadrado, que es
        <strong>{n(pc['japanesepines']['nn_esperada'])}</strong>. No hay nada que explicar en
        este mapa, y esa es exactamente su función: es la referencia contra la que se mide todo lo demás. Fíjate,
        eso sí, en que la ventana viene <em>con</em> el dato: área {pc['japanesepines']['area']}. De ahí sale la
        primera cifra que se le calcula a cualquier patrón puntual.</p>

      <div class="definition">
        <h3>La intensidad \\(\\lambda\\), que es lo primero que se mide de un patrón puntual</h3>
        <p>Es la <strong>densidad de puntos</strong>: cuántos hay por unidad de área. Con \\(n\\) puntos sobre una
          ventana \\(W\\) de área \\(|W|\\),</p>
        <p style="text-align:center;">$$\\lambda = \\frac{{n}}{{|W|}}$$</p>
        <p>Con los pinos, \\(n = {pc['japanesepines']['n']}\\) y \\(|W| = {pc['japanesepines']['area']}\\), así que
          \\(\\lambda = {pc['japanesepines']['lambda']}\\) árboles por unidad de área. Se lee como cualquier
          densidad —habitantes por km², árboles por hectárea— y, como cualquier densidad, <strong>tiene
          unidades</strong>: el mismo patrón medido en km² o en hectáreas da dos números distintos sin que se
          mueva un solo punto. Cuando en este curso veas un \\(\\lambda\\) suelto, pregunta siempre «¿por unidad de
          qué?».</p>
        <p style="margin-bottom:0;">Y ahora la parte incómoda, que es la razón de presentarla aquí y no en una
          tabla de fórmulas. El numerador lo pone el dato: los puntos están donde están y son los que son. El
          denominador lo pones <strong>tú</strong>, al decidir dónde acaba la ventana. \\(\\lambda\\) es de las
          pocas cifras del curso que se puede cambiar sin tocar el dato: mueve el borde y cambia, sin que se mueva
          un solo pino. Con los pinos no se nota, porque la ventana viene con ellos. Con el mapa que sigue, sí.</p>
      </div>

      <div class="geomapa" data-geomapa="cap1-bogota"></div>

      <p>Bogotá hace lo contrario, y por eso va al lado. Las <strong>{ent(co['puntual']['n'])}</strong> sedes no
        están tiradas al azar: dibujan las calles, y con ellas la densidad de la ciudad. Aquí sí hay algo que
        explicar. Y fíjate en el borde, que es donde este mapa se pone interesante:
        <strong>{ent(co['puntual']['n_urbana'])}</strong> de las {ent(co['puntual']['n'])} caen dentro del
        perímetro urbano y <strong>{ent(co['puntual']['n_dc'])}</strong> dentro del Distrito Capital. El mismo
        patrón admite al menos tres bordes distintos, y elegir no es cuestión de gusto: la <em>ventana</em> de un
        patrón puntual es, por definición, la región sobre la que el dato es <strong>exhaustivo</strong> —aquella
        donde puedes afirmar que no falta ningún punto—. Con ese criterio el perímetro urbano no es una ventana
        sino un recorte, y el propio dato lo delata: las dos cifras de arriba no coinciden porque hay sedes dentro
        del Distrito y fuera del perímetro. La nota que cierra este módulo le pone precio a confundirlos.</p>

      <p>Lo que comparten los dos mapas es justo lo que define el tipo: en ninguno se ha medido nada <em>en</em> el
        punto. No existe el «valor del pino» ni el «valor de la sede». Si volviéramos a tomar el dato, lo que
        saldría distinto sería <strong>dónde</strong> caen los puntos —y cuántos hay—.</p>

      <div class="definition">
        <h3>2 · Dato de área — lo aleatorio es el <em>valor</em>, sobre unidades fijas</h3>
        <p style="margin-bottom:0;">La tasa de muerte súbita infantil en los {ac['n']} condados de Carolina del
          Norte ({ac['nombre'].split(', ')[-1]}) y la deserción escolar en los {es['n_departamental']} departamentos
          de Colombia. Las unidades no se mueven; lo que varía es lo que se mide en ellas. Los cortes de clase de
          los dos mapas los calculó <code>classInt</code> en R y viajan en el JSON: el navegador solo pinta.</p>
      </div>
      <div class="geomapa" data-geomapa="cap1-nc"></div>

      <p>Carolina del Norte se lee con la leyenda en la mano: cinco clases por cuantiles. La tasa va de
        <strong>{ac['tasa_min']}</strong> a <strong>{n(ac['tasa_max'])}</strong> por mil según el condado, con
        media <strong>{n(ac['tasa_media'])}</strong>. Pero hay una segunda cifra que conviene ver ya, porque es una
        grieta y no un detalle: la tasa del estado entero —todas las muertes sobre todos los nacimientos— vale
        <strong>{n(ac['tasa_global'])}</strong>, no {n(ac['tasa_media'])}. Discrepan un
        <strong>{n(ac['diferencia_media_global_pct'])}&nbsp;%</strong>.</p>

      <p>Ninguna de las dos está mal: <strong>no calculan lo mismo</strong>. Sumar las {ac['n']} tasas y dividir
        entre {ac['n']} le da a cada condado el mismo peso, tenga cien nacimientos o diez mil, y contesta a la
        pregunta «¿cuánto vale la tasa en un condado <em>típico</em>?». Dividir todas las muertes entre todos los
        nacimientos pesa cada condado por su tamaño, y contesta a otra: «¿qué riesgo corrió un recién nacido
        <em>cualquiera</em> de Carolina del Norte?». Son dos preguntas distintas y por eso dan dos números
        distintos. Lo que hay que saber es cuál de las dos se está publicando.</p>

      <p>Y hay que saber, además, de qué depende la distancia entre ellas, porque no es
        una constante del universo. Las dos coincidirían si todos los condados tuvieran el mismo tamaño, o si la
        tasa no tuviera nada que ver con el tamaño. Aquí los condados son muy desiguales pero la tasa apenas
        depende de cuántos nazcan —la sección de <em>soporte</em>, más abajo en este módulo, le pone las dos cifras
        a esa frase—, y por eso la brecha se queda en un decimal que no le molesta a nadie. Cuando sí depende,
        cuando las unidades grandes tienen valores sistemáticamente distintos de las pequeñas, esa misma grieta se
        ensancha hasta invertir conclusiones: es la <strong>falacia ecológica</strong>, y con el MAUP forma el
        capítulo 3 entero.</p>

      <div class="geomapa" data-geomapa="cap1-desercion"></div>

      <p>El mapa colombiano es el mismo objeto con otras unidades: <strong>{es['n_departamental']}</strong>
        departamentos, los mismos cinco cortes por cuantiles. Y trae una trampa que conviene destapar desde la
        semana 1: el dato original no es departamental. Son <strong>{ent(co['area']['n'])}</strong> municipios,
        <strong>{ent(co['area']['n_con_dato'])}</strong> de ellos con dato. Lo que estás mirando es <em>una</em> de
        las dos fotografías posibles del mismo fenómeno, y elegir entre ellas no es inocente: el módulo 7 mide qué
        se pierde por el camino.</p>

      <p>Lo que comparten: las unidades no se mueven. Los {ac['n']} condados y los {es['n_departamental']}
        departamentos estaban ahí antes del dato y seguirán estando después. Si volviéramos a tomar el dato, lo que
        saldría distinto sería <strong>el valor</strong> de cada unidad, nunca la unidad.</p>

      <div class="definition">
        <h3>3 · Geoestadístico — el valor existe en <em>todo</em> punto y se observa en unos pocos</h3>
        <p style="margin-bottom:0;">El zinc en {gc['n']} puntos de la vega del Mosa y la temperatura media anual en
          {co['geo']['n']} estaciones del IDEAM. Hay zinc y hay temperatura entre los puntos medidos; simplemente no
          se midieron. Por eso aquí —y solo aquí— tiene sentido predecir dónde no hay dato.</p>
      </div>
      <div class="geomapa" data-geomapa="cap1-meuse"></div>

      <p>El mapa del Mosa parece manchas de color hasta que uno sabe por dónde va el río. El zinc va de
        <strong>{gc['zinc_min']}</strong> a <strong>{ent(gc['zinc_max'])}</strong> ppm, con media
        <strong>{n(gc['zinc_media'])}</strong> y desviación <strong>{n(gc['zinc_sd'])}</strong>, y con una
        asimetría de <strong>{n(gc['asimetria_zinc'])}</strong> que es la razón de que en este dato se trabaje
        siempre con el logaritmo —el capítulo 9 lo hará—. El patrón tampoco es un capricho: la correlación del zinc
        con la distancia al río vale <strong>{n(gc['corr_dist_rio'])}</strong>. Lo que estás viendo es una llanura
        de inundación, y el metal lo trajeron las crecidas.</p>

      <div class="geomapa" data-geomapa="cap1-ideam"></div>

      <p>Las <strong>{co['geo']['n']}</strong> estaciones del IDEAM hacen lo mismo con otra variable. La
        temperatura media anual va de <strong>{n(co['geo']['t_min'], 1)}</strong> a
        <strong>{n(co['geo']['t_max'], 1)}</strong> °C, un rango que sorprende en un país ecuatorial hasta que se
        mira la otra columna del dato: hay estaciones a <strong>{ent(co['geo']['alt_max'])}</strong> m. Estás
        viendo la cordillera, no el clima. El módulo 3 mide cuánto de lo que parece «lo cercano se parece» es en
        realidad «lo cercano está a la misma altura», y la cifra incomoda.</p>

      <p>Lo que comparten: entre dos estaciones <em>hay</em> temperatura, y entre dos puntos de la vega <em>hay</em>
        zinc. Simplemente no se midieron. Si volviéramos a tomar el dato en otras localizaciones, el campo de
        debajo sería el mismo; lo único que cambiaría es <strong>dónde lo miramos</strong>. De ahí sale el permiso
        para predecir, que es justo lo que los otros dos tipos no tienen.</p>

      <p>Vuelve ahora al párrafo del principio. Los seis mapas se parecen bastante entre sí —puntos y polígonos de
        colores— y sin embargo la pregunta «¿qué saldría distinto si volviéramos a tomar el dato?» los ha partido
        limpiamente en tres: cambian las <em>posiciones</em>, cambian los <em>valores</em> sobre unidades fijas, o
        cambia <em>dónde miramos</em> un campo que ya estaba ahí. La tabla resume lo que acabas de hacer.</p>

      <!-- Los tres tipos van en las COLUMNAS y los cinco atributos en las filas,
           que es la transpuesta de como se escribiría de primeras. Dos razones.
           La de forma: al revés, las celdas de prosa —«El valor de algo que
           existe en todo punto y se observa en unos pocos»— caían cada una en su
           columna y llevaban la tabla a 2 143 px dentro de un contenedor de 812,
           con la cabecera de fila fuera de cuadro al desplazarse.
           La de fondo, que es la que manda: lo que este módulo compara son los
           tres tipos ENTRE SÍ, y comparar se hace mirando en paralelo, no en
           fila. Con los tipos por columnas cada fila pasa a ser una pregunta
           —«¿qué es aleatorio?»— contestada tres veces una al lado de la otra,
           que es exactamente el gesto que pide el párrafo de arriba. -->
      <table class="tabla-matriz">
        <caption>Los tres tipos de dato espacial: qué es aleatorio, qué se estima y en qué capítulo se desarrolla.</caption>
        <thead>
          <tr><td></td>
            <th scope="col">Patrón puntual</th>
            <th scope="col">Dato de área</th>
            <th scope="col">Geoestadístico</th></tr>
        </thead>
        <tbody>
          <tr><th scope="row">Qué es aleatorio</th>
            <td>La <strong>localización</strong> de los eventos, y cuántos hay</td>
            <td>El <strong>valor</strong>, sobre unidades territoriales fijas</td>
            <td>El <strong>valor</strong> de algo que existe en todo punto y se observa en unos pocos</td></tr>
          <tr><th scope="row">Qué se estima</th>
            <td>Intensidad \\(\\lambda\\), agregación o regularidad</td>
            <td>Autocorrelación, modelos SAR/SEM</td>
            <td>Variograma, predicción por kriging</td></tr>
          <tr><th scope="row">Canónico</th>
            <td>{pc['japanesepines']['nombre']} ({pc['japanesepines']['n']})</td>
            <td>{ac['nombre']} ({ac['n']})</td>
            <td>{gc['nombre']} ({gc['n']})</td></tr>
          <tr><th scope="row">Colombiano</th>
            <td>{co['puntual']['nombre']} ({ent(co['puntual']['n'])})</td>
            <td>{co['area']['nombre']} ({ent(co['area']['n'])})</td>
            <td>{co['geo']['nombre']} ({co['geo']['n']})</td></tr>
          <tr><th scope="row">Capítulos</th>
            <td>4 y 5</td>
            <td>6, 7 y 8</td>
            <td>9</td></tr>
        </tbody>
      </table>

      <p>Y ahora la segunda pregunta, que la tabla deja sin hacer y que decide tanto como la primera. No es «¿qué es
        aleatorio?» sino <strong>«¿de qué trozo de la unidad habla el número?»</strong>. Pebesma y Bivand la
        introducen ya en el capítulo 1 de su libro y le dedican el 5 entero: la llaman el <em>soporte</em> del
        dato.</p>

      <div class="definition">
        <h3>El soporte: a qué parte de la geometría se refiere el valor</h3>
        <ul>
          <li><strong>Soporte puntual:</strong> el valor vale en <em>cada punto</em> de la geometría. El tipo de
            suelo de un polígono de un mapa de suelos es el mismo en el centro que en el borde, y lo sigue siendo
            en cualquier trozo que recortes.</li>
          <li><strong>Soporte de bloque:</strong> el valor <em>resume</em> la geometría entera. La tasa de SIDS de
            un condado no está en ningún punto del condado: está en el condado, y no sobrevive a que lo partas.</li>
        </ul>
        <p style="margin-bottom:0;">Y aquí está lo que hay que destapar, porque es lo que rompe la lectura fácil de
          la tabla de arriba: <strong>el soporte no lo decide la geometría</strong>. Un mapa de suelos y el de
          Carolina del Norte se guardan igual —polígonos— y uno tiene soporte puntual y el otro de bloque.
          «Polígono» no significa «dato de área», y el Mosa lo enseña por el otro lado: se dibuja con puntos y no es
          un patrón puntual.</p>
      </div>

      <p>El soporte no es vocabulario: se paga en el mapa, y se puede medir. La variable que Carolina del Norte trae
        de fábrica no es la tasa sino el <strong>conteo</strong> de muertes por condado
        —{ac['sid74_total']} en total—, que es <em>extensiva</em>: crece con la unidad.
        Pintarla tal cual sería pintar, sobre todo, cuántos niños nacieron en cada condado. La correlación entre el
        conteo y los nacimientos vale <strong>{n(sop['cor_conteo_nacimientos'])}</strong>; dividir por los
        nacimientos —volverla <em>intensiva</em>— la deja en
        <strong>{n(sop['cor_tasa_nacimientos'])}</strong>. Por eso el mapa que has mirado es una tasa y no un
        conteo, y no era una decisión de estilo.</p>

      <p>Hay un segundo paso, y es donde la receta de manual se queda corta. «Divide por el área» es lo que suele
        decirse para pasar de extensiva a intensiva, y en este dato <em>no</em> es lo correcto: el conteo sigue al
        área bastante menos —<strong>{n(sop['cor_conteo_area'])}</strong>— que a los nacimientos. En un dato de
        salud el denominador es la población en riesgo, no la superficie. Y no es un denominador disimuladamente
        constante: entre el condado que más nacimientos aporta y el que menos hay un factor de
        <strong>{n(sop['razon_nacimientos'])}</strong>. Eso mueve el soporte de sitio: la tasa de un condado ya no
        resume un territorio sino una población, y ahí queda un cabo suelto que conviene ver desde ahora. Dos
        condados separados por ese factor no conocen su tasa con la misma precisión —el pequeño la tiene mucho peor
        estimada—, y sin embargo el mapa los pinta con el mismo derecho. Pintar bien no es lo mismo que saber.</p>

      <p>Conviene separar los dos filos, porque es fácil confundirlos. El módulo 7 mide qué pasa cuando se
        <em>cambia de unidades</em> —el mismo fenómeno sobre municipios o sobre departamentos—; el soporte es qué
        significa el número <em>dentro</em> de una unidad. Se pueden romper por separado, y casi siempre se rompen
        juntos.</p>

      <div class="definition">
        <h3>La formalización, ahora que ya has visto los seis mapas</h3>
        <p>En los tres casos hay un proceso \\(Z(s)\\) sobre un dominio \\(D \\subset \\mathbb{{R}}^2\\). Lo que cambia
          es <strong>qué es aleatorio</strong>:</p>
        <ul>
          <li><strong>Patrón puntual:</strong> aleatorio es el propio conjunto de índices. \\(D\\) es fijo (la
            <em>ventana</em>) y lo que se observa es \\(\\{{s_1, \\dots, s_N\\}}\\), con \\(N\\) también aleatorio.</li>
          <li><strong>Dato de área:</strong> los índices son un conjunto <em>fijo y numerable</em> de unidades
            \\(A_1, \\dots, A_n\\) —los municipios—, y aleatorio es \\(Z(A_i)\\).</li>
          <li><strong>Geoestadístico:</strong> \\(Z(s)\\) existe para <em>todo</em> \\(s \\in D\\) —hay una
            temperatura en cada punto de Colombia— y solo se observa en \\(n\\) localizaciones elegidas.</li>
        </ul>
        <p style="margin-bottom:0;">De ahí sale una consecuencia que conviene tener presente desde ya: en el caso
          geoestadístico <strong>tiene sentido predecir dónde no se ha medido</strong>, y en el de área no. Preguntar
          «¿cuánta deserción hay entre dos municipios?» no significa nada — y ahora se puede decir <em>por qué</em>,
          que es mejor que decirlo por decreto: la deserción de un municipio tiene <strong>soporte de bloque</strong>,
          así que no hay ninguna función definida sobre los puntos que se pueda interpolar. \\(Z(A_i)\\) no es
          \\(Z(s)\\) evaluada en ningún \\(s\\); es otra cosa que se escribe parecido.</p>
      </div>

      <div class="warning">
        <p style="margin-bottom:0;"><strong>El mismo fenómeno puede ser de los tres tipos, y eso no es una
          ambigüedad: es una decisión.</strong> Los colegios de Bogotá son un patrón puntual si la pregunta es
          «¿dónde se concentran?»; son dato de área si se cuentan por localidad; y serían geoestadísticos si lo que
          se midiera fuera algo que existe en todo punto —la accesibilidad, por ejemplo—. Elegir el tipo es elegir
          el modelo, y el capítulo 3 enseña lo caro que sale elegirlo en silencio.</p>
      </div>

      <p>Falta rematarlo por el lado que más caro sale en la práctica, que no es confundir los tres tipos entre sí:
        es <strong>leer el tipo en la geometría del archivo</strong>. Pebesma y Bivand separan el <em>fenómeno</em>
        —lo que hay en el mundo: un campo, un objeto o un agregado— de la <em>geometría</em> con la que se guarda, y
        avisan de que entre los dos no hay correspondencia simple. La tabla lo enseña de la única forma convincente:
        no tiene ni una casilla vacía.</p>

      <table>
        <caption>La geometría de un archivo no dice de qué fenómeno se trata. Cada fila admite las tres columnas.</caption>
        <thead>
          <tr><th scope="col">Geometría</th>
            <th scope="col">Campo <span class="text-gray-400 font-normal">— hay valor en todo punto</span></th>
            <th scope="col">Objeto <span class="text-gray-400 font-normal">— cosas en sitios discretos</span></th>
            <th scope="col">Agregado <span class="text-gray-400 font-normal">— resumen sobre una región</span></th></tr>
        </thead>
        <tbody>
          <tr><th scope="row">Punto</th>
            <td>Estación del IDEAM: una muestra de la temperatura</td>
            <td>Sede educativa de Bogotá: el objeto <em>es</em> el dato</td>
            <td>El centroide de un condado con la tasa dentro — y ahí ya hay un error</td></tr>
          <tr><th scope="row">Línea</th>
            <td>Una curva de nivel</td>
            <td>Un río, una calle</td>
            <td>El tránsito medio diario de un tramo</td></tr>
          <tr><th scope="row">Polígono o píxel</th>
            <td>Tipo de suelo, zona climática</td>
            <td>La huella de un edificio</td>
            <td>Deserción por municipio, SIDS por condado</td></tr>
        </tbody>
      </table>

      <p>Las nueve casillas salen del mismo <code>st_read()</code> y se dibujan igual. La geometría es lo que el
        archivo sabe; el fenómeno es lo que sabes tú, y no viaja en el archivo. La casilla incómoda es la de arriba
        a la derecha, porque es la que se produce sola: basta con pedir centroides.</p>

""" + tabs(
    "Leer un patrón puntual, un dato de área y uno geoestadístico",
    """library(sf); library(spatstat.geom)

# 1) Patron puntual: la clase `ppp` lleva SIEMPRE su ventana dentro.
data(japanesepines, package = "spatstat.data")
cat(sprintf("ppp: n = %d, area de la ventana = %.5f, lambda = %.5f\\n",
            japanesepines$n, area(japanesepines$window),
            intensity(japanesepines)))
#&gt; """ + f"ppp: n = {pc['japanesepines']['n']}, area de la ventana = {n(pc['japanesepines']['area'])}, "
    f"lambda = {n(pc['japanesepines']['lambda'])}" + """

# 2) Dato de area: geometria + atributos en la misma tabla.
nc &lt;- st_read(system.file("shape/nc.shp", package = "sf"), quiet = TRUE)
cat(sprintf("sf: %d unidades, tasa media de SIDS = %.5f por mil\\n",
            nrow(nc), mean(1000 * nc$SID74 / nc$BIR74)))
#&gt; """ + f"sf: {ac['n']} unidades, tasa media de SIDS = {n(ac['tasa_media'])} por mil" + """

# 3) Geoestadistico: puntos con un valor medido en cada uno.
data(meuse, package = "sp")
cat(sprintf("meuse: n = %d, zinc medio = %.5f ppm, sd = %.5f\\n",
            nrow(meuse), mean(meuse$zinc), sd(meuse$zinc)))
#&gt; """ + f"meuse: n = {gc['n']}, zinc medio = {n(gc['zinc_media'])} ppm, sd = {n(gc['zinc_sd'])}" + """

# 4) El soporte no es teoria, y no hay que creerselo: sf lo dice solo.
#    Sustituir cada condado por su centroide es la casilla de arriba a la
#    derecha de la tabla — un agregado montado sobre un punto —, y la
#    tasa que viaja dentro deja de significar lo que significaba.
aviso &lt;- tryCatch({ st_centroid(nc[, c("BIR74", "SID74", "NAME")]); "sin aviso" },
                  warning = function(w) conditionMessage(w))
cat(aviso, "\\n")
#&gt; st_centroid assumes attributes are constant over geometries""",
    """import geopandas as gpd, pandas as pd, numpy as np, json

# 1) spatstat no existe en Python: pointpats trabaja con el array y la
#    ventana POR SEPARADO, que es justo la diferencia de diseno que el
#    modulo 9 comenta. El dato va por CSV.
pp = pd.read_csv("precalculo/salidas/cap1_ppp.csv")
jp = pp[pp.patron == "japanesepines"]
print(f"n = {len(jp)}, area de la ventana = {1.0:.5f}, "
      f"lambda = {len(jp) / 1.0:.5f}")
#> """ + f"n = {pc['japanesepines']['n']}, area de la ventana = {n(pc['japanesepines']['area'])}, "
    f"lambda = {n(pc['japanesepines']['lambda'])}" + """

# 2) Dato de area: GeoDataFrame, el equivalente de un objeto sf.
ver = json.load(open("precalculo/versiones.json"))
nc = gpd.read_file(ver["rutas"]["nc_shp"])
print(f"{len(nc)} unidades, tasa media de SIDS = "
      f"{(1000 * nc.SID74 / nc.BIR74).mean():.5f} por mil")
#> """ + f"{ac['n']} unidades, tasa media de SIDS = {n(ac['tasa_media'])} por mil" + """

# 3) Geoestadistico.
me = pd.read_csv("precalculo/salidas/cap1_meuse.csv")
print(f"n = {len(me)}, zinc medio = {me.zinc.mean():.5f} ppm, "
      f"sd = {me.zinc.std(ddof=1):.5f}")
#> """ + f"n = {gc['n']}, zinc medio = {n(gc['zinc_media'])} ppm, sd = {n(gc['zinc_sd'])}" + """

# 4) La MISMA operacion en geopandas tambien avisa... de otra cosa. Se
#    queja del CRS y calla el soporte; sf se queja del soporte y calla el
#    CRS. Ninguna de las dos avisa de las dos, asi que el aviso que no
#    salta no es permiso: es que esa libreria no mira por ahi.
import warnings
with warnings.catch_warnings(record=True) as ws:
    warnings.simplefilter("always")
    nc.centroid
print([str(w.message).split(".")[0] for w in ws])
#> ['Geometry is in a geographic CRS']""") + f"""
      <div class="note">
        <p style="margin-bottom:0;"><strong>La ventana no es un detalle,</strong> y aquí está la factura de
          moverla. La intensidad \\(\\lambda\\) de las sedes de
          Bogotá vale <strong>{n(co['puntual']['lambda_urbana'])}</strong> sedes/km² sobre el perímetro urbano
          ({n(co['puntual']['area_urbana_km2'], 1)} km²) y <strong>{n(co['puntual']['lambda_dc'])}</strong> sobre el
          Distrito Capital completo ({n(co['puntual']['area_dc_km2'], 1)} km², Sumapaz incluido). Mismo dato, mismas
          sedes, y un factor de <strong>{n(co['puntual']['factor_lambda'])}</strong> según dónde se ponga el borde.
          Y no son dos estimaciones rivales de lo mismo: una es la de una ventana y la otra la de un recorte. El
          capítulo 4 empieza justo ahí.</p>
      </div>
""" + CIERRE


# =====================================================================
# MÓDULO 3 · La primera ley de Tobler
# =====================================================================
MOD3 = cabecera(
    3, "La primera ley de Tobler", "Tobler's first law",
    "Medir la primera ley en vez de citarla, con un control que la niega y "
    "un caso donde lo que parece dependencia es otra cosa.") + f"""
      <p>La cita es de 1970 y es la frase más repetida del área: <em>«todo está relacionado con todo lo demás, pero
        las cosas cercanas están más relacionadas que las lejanas»</em>. Dicha así no es una ley: es una impresión.
        Lo que la convierte en algo utilizable es que se puede <strong>medir</strong>, y medirla es lo que hace el
        correlograma.</p>

      <p>Toma las <strong>{co['geo']['n']}</strong> estaciones climáticas del IDEAM con normal 1991-2020. Agrupa
        todas las parejas de estaciones por su distancia y calcula, banda a banda, cuánto se parecen sus
        temperaturas. Si Tobler tiene razón, el parecido tiene que decaer.</p>

      <div class="simulador" data-simulador="correlograma">
        <h4><i class="fas fa-signal" aria-hidden="true"></i> El correlograma: la primera ley, medida</h4>
        <p class="simulador-intro">Índice de Moran por bandas de distancia. Tres series que puedes
          <strong>encender y apagar</strong>: el dato real, el mismo dato con las temperaturas
          <strong>permutadas al azar</strong> —el control— y los residuos tras quitar la altitud.
          E[I] bajo independencia se queda siempre, porque es la referencia contra la que se leen
          las otras tres. Deja solo el permutado y mira qué aspecto tiene un correlograma sin nada
          dentro; enciende luego el real y compara.</p>
        <div class="simulador-controles"></div>
        <div class="grafico-wrapper" style="height:270px;">
          <canvas aria-label="Índice de Moran por bandas de distancia para las estaciones del IDEAM, su versión permutada y sus residuos tras quitar la altitud" role="img"></canvas>
        </div>
        <div class="simulador-lectura"></div>
      </div>

      <p>La primera banda ({tb['ideam']['bandas'][0]['d1']}–{tb['ideam']['bandas'][0]['d2']} km) da
        <strong>{n(tb['ideam']['bandas'][0]['I'])}</strong>; la última
        ({tb['ideam']['bandas'][-1]['d1']}–{tb['ideam']['bandas'][-1]['d2']} km) da
        <strong>{n(tb['ideam']['bandas'][-1]['I'])}</strong>, que ya no se distingue del valor esperado bajo
        independencia, <strong>{n(tb['ideam']['esperado'], 6)}</strong>. Eso es la primera ley con una cifra
        delante.</p>

      <div class="definition">
        <h3>El índice de Moran, que es la herramienta de todo el curso</h3>
        <p>Con \\(n\\) unidades, valores \\(z_i\\) centrados y una matriz de pesos \\(W\\) que declara quién es vecino
          de quién,</p>
        <p style="text-align:center;">$$I = \\frac{{n}}{{S_0}} \\cdot
          \\frac{{\\sum_i \\sum_j w_{{ij}} z_i z_j}}{{\\sum_i z_i^2}},
          \\qquad S_0 = \\sum_i \\sum_j w_{{ij}}, \\qquad E[I] = -\\frac{{1}}{{n-1}}$$</p>
        <p style="margin-bottom:0;">Con las {co['geo']['n']} estaciones, \\(E[I] = {n(tb['ideam']['esperado'], 6)}\\).
          Fíjate en que <strong>\\(I\\) no vale cero bajo la hipótesis nula</strong>, vale un poco menos: es el
          artefacto de comparar cada unidad consigo misma excluida. El capítulo 7 lo desarrolla.</p>
      </div>

      <div class="warning">
        <p><strong>Y aquí el capítulo se muerde la cola, con dos decimales de por medio.</strong> Buena parte de esa
          dependencia no es dependencia: es una <em>covariable disfrazada</em>. La temperatura en Colombia la manda
          la altitud —corr = <strong>{n(co['geo']['corr_alt'])}</strong>, un gradiente de
          <strong>{n(co['geo']['gradiente'])}</strong> °C por cada 1 000 m, que es exactamente el rango físico
          esperable—. Al quitarla, la I de la primera banda baja de {n(tb['ideam']['bandas'][0]['I'])} a
          <strong>{n(tb['residuos_altitud']['bandas'][0]['I'])}</strong>: un
          <strong>{n(tb['caida_por_altitud_pct'])}&nbsp;%</strong> menos.</p>
        <p style="margin-bottom:0;">Queda dependencia —{n(tb['residuos_altitud']['bandas'][0]['I'])} sigue siendo
          mucho—, pero casi un tercio de lo que parecía «lo cercano se parece» era «lo cercano está a la misma
          altura». El capítulo 9 le pone nombre a esto: <em>kriging con deriva externa</em>.</p>
      </div>

      <p>El control es la otra mitad del argumento. Permutando las temperaturas entre las mismas estaciones
        —mismas posiciones, mismas distancias, mismos pesos— la primera banda cae a
        <strong>{n(tb['permutado']['bandas'][0]['I'])}</strong>. Si el correlograma del dato real y el del permutado
        se parecieran, la estructura que estamos midiendo la estaría poniendo la geometría y no el fenómeno.</p>

""" + tabs(
    "El correlograma por bandas, en R y en Python",
    """library(sf); library(spdep)

est &lt;- st_read("datos/procesado/colombia_estaciones_clima.gpkg", quiet = TRUE)
d   &lt;- as.numeric(st_distance(est)) / 1000        # a km; quita las unidades
dim(d) &lt;- c(nrow(est), nrow(est))

banda &lt;- function(lo, hi) {
  nb &lt;- dnearneigh(st_coordinates(est), lo * 1000, hi * 1000)
  moran.test(est$t_media_anual, nb2listw(nb, style = "W", zero.policy = TRUE),
             zero.policy = TRUE)$estimate[["Moran I statistic"]]
}
cat(sprintf("0-25 km: I = %.5f   |   500-800 km: I = %.5f\\n",
            banda(0, 25), banda(500, 800)))
#&gt; """ + f"0-25 km: I = {n(tb['ideam']['bandas'][0]['I'])}   |   "
    f"500-800 km: I = {n(tb['ideam']['bandas'][-1]['I'])}",
    """import geopandas as gpd, numpy as np

# Aqui la I se calcula A MANO, y no con esda, por una razon que el modulo 9
# desarrolla: los dos programas no cuentan igual las unidades sin vecinos.
# Escribir la formula deja el convenio a la vista en vez de heredarlo.
est = gpd.read_file("datos/procesado/colombia_estaciones_clima.gpkg")
xy = np.c_[est.geometry.x, est.geometry.y]
t = est.t_media_anual.to_numpy()
dm = np.sqrt(((xy[:, None, :] - xy[None, :, :]) ** 2).sum(-1)) / 1000

def banda(lo, hi):
    A = ((dm > lo) & (dm <= hi)).astype(float)   # 0 < d <= hi, banda a banda
    np.fill_diagonal(A, 0.0)
    grado = A.sum(1)
    con = grado > 0                              # las unidades CON vecinos
    W = np.zeros_like(A)
    W[con] = A[con] / grado[con, None]           # estandarizada por filas
    z = t - t.mean()
    # n = unidades con vecinos: el convenio de spdep con zero.policy = TRUE
    return (con.sum() / W.sum()) * (z @ W @ z) / (z @ z)

print(f"0-25 km: I = {banda(0, 25):.5f}   |   "
      f"500-800 km: I = {banda(500, 800):.5f}")
#> """ + f"0-25 km: I = {n(tb['ideam']['bandas'][0]['I'])}   |   "
    f"500-800 km: I = {n(tb['ideam']['bandas'][-1]['I'])}") + f"""
      <div class="note">
        <p style="margin-bottom:0;"><strong>Fíjate en que la pestaña de Python escribe la fórmula en vez de llamar a
          <code>esda</code>.</strong> No es pedantería: los dos programas no cuentan igual las unidades sin vecinos,
          y llamar a la función de cada uno habría dado dos números distintos sin decir por qué. Escrita la fórmula,
          el convenio está a la vista. El módulo 9 lo mide y el capítulo 6 lo convierte en su caso trabajado de
          <code>zero.policy</code>.</p>
      </div>

      <p>La primera ley no vale solo para valores medidos: también describe <strong>dónde están las cosas</strong>.
        Aquí están los tres patrones que anunció el módulo 2, uno al lado del otro y sobre ventanas del mismo
        tamaño. Los rótulos ya dicen cuál es cuál —no hay adivinanza—; lo que no dice ninguno es <em>cuánto</em>,
        ni con qué se compara para decidirlo.</p>

      <div class="grid md:grid-cols-3 gap-4 items-start">
        <div class="geomapa" data-geomapa="cap1-secuoyas"></div>
        <div class="geomapa" data-geomapa="cap1-pinos"></div>
        <div class="geomapa" data-geomapa="cap1-celulas"></div>
      </div>

      <p>Detente en el del medio, que es el que enseña algo sobre quien mira. Ese es el patrón compatible con el
        azar, y tiene huecos y tiene grumos —el azar los produce—; puestos a ordenar los tres a ojo, es fácil
        ponerlo del lado de la agregación. Un patrón aleatorio no se ve repartido: se ve apelotonado, porque
        repartido es justo lo que <em>no</em> es. Por eso la pregunta «¿está agrupado?» no se contesta mirando, y
        por eso hace falta un número.</p>

      <div class="definition">
        <h3>El índice de Clark-Evans, que pone ese número</h3>
        <p>Se mide, para cada uno de los \\(n\\) puntos, la distancia al punto más próximo, y se promedian las
          \\(n\\) distancias. Eso es \\(\\bar{{d}}_{{\\min}}\\): la cifra que el módulo 2 ya dio tres veces. Sola
          no dice nada, porque depende de la densidad —con más puntos en la misma ventana, todo el mundo tiene un
          vecino más cerca—. Necesita una <strong>referencia</strong>, y la referencia es la aleatoriedad
          completa: puntos tirados de forma independiente y uniforme sobre la ventana, que es la hipótesis nula de
          los patrones puntuales y se conoce como <strong>CSR</strong> (<em>complete spatial randomness</em>).
          Bajo CSR, con intensidad \\(\\lambda\\) puntos por unidad de área, ese promedio se sabe de antemano:</p>
        <p style="text-align:center;">$$E[\\bar{{d}}_{{\\min}}] = \\frac{{1}}{{2\\sqrt{{\\lambda}}}},
          \\qquad\\qquad R = \\frac{{\\bar{{d}}_{{\\min}}}}{{E[\\bar{{d}}_{{\\min}}]}}$$</p>
        <p style="margin-bottom:0;">Ese cociente \\(R\\) es el <strong>índice de Clark-Evans</strong> (1954), y es
          una división entre dos distancias: cuánto se separan los puntos de verdad, dividido entre cuánto se
          separarían por puro azar. De ahí le vienen sus dos propiedades: no tiene unidades, y su referencia es el
          <strong>1</strong>. Por debajo de 1 los puntos están <em>más cerca</em> de lo que daría el azar
          —agregación—; por encima, más lejos —regularidad—. Con los {pc['japanesepines']['n']} pinos sobre su
          ventana de área {pc['japanesepines']['area']} sale λ = {pc['japanesepines']['lambda']}, y con ella
          \\(E[\\bar{{d}}_{{\\min}}] = {n(pc['japanesepines']['nn_esperada'])}\\): contra esa cifra se compara la
          distancia observada de {n(pc['japanesepines']['nn_media'])} que viste en el módulo 2, y el cociente da
          {n(pc['japanesepines']['clark_evans'])}.</p>
      </div>

      <p>Ese denominador no es un convenio ni una constante tabulada: sale de la definición de CSR en cinco pasos,
        y vale la pena recorrerlos porque por el camino aparecen dos cosas que el curso usa después —la función
        \\(G\\) del capítulo 4, que asoma sola en el paso 3, y el punto exacto por donde se cuela la ventana
        infinita del efecto de borde—.</p>

      <div class="derivacion">
        <button type="button" class="derivacion-boton" aria-expanded="false" aria-controls="der-vecino-csr">
          <i class="fas fa-square-root-variable" aria-hidden="true"></i>
          <span class="derivacion-texto">Ver de dónde sale \\(E[\\bar{{d}}_{{\\min}}] = 1/(2\\sqrt{{\\lambda}})\\)</span>
          <i class="fas fa-chevron-down" aria-hidden="true"></i>
        </button>
        <div class="derivacion-panel" id="der-vecino-csr" hidden>
          <ol class="derivacion-pasos">
            <li>
              <p>Se parte de lo único que afirma CSR, que es una regla sobre <strong>conteos</strong> y no sobre
                distancias: el número de puntos que caen en una región de área \\(A\\) es Poisson de media
                \\(\\lambda A\\), y regiones disjuntas no se enteran unas de otras. No se añade nada más en todo
                el desarrollo.</p>
              $$N(A) \\sim \\text{{Poisson}}(\\lambda A)$$
            </li>
            <li>
              <p>La distancia \\(D\\) al vecino más próximo no es un conteo, pero su <em>cola</em> sí lo es, y ese
                es el truco entero: que el vecino esté a más de \\(r\\) es exactamente que el disco de radio
                \\(r\\) centrado en el punto esté <strong>vacío</strong>. El disco tiene área \\(\\pi r^2\\), así
                que basta pedirle a la Poisson de media \\(\\lambda\\pi r^2\\) la probabilidad de que no salga
                nadie:</p>
              $$P(D > r) = P\\bigl(N(\\pi r^2) = 0\\bigr) = e^{{-\\lambda \\pi r^2}}$$
            </li>
            <li>
              <p>Fíjate en que eso no es un paso intermedio cualquiera: es la <strong>distribución completa</strong>
                de la distancia al vecino, no solo su promedio. Su acumulada, \\(G(r) = 1 - e^{{-\\lambda\\pi r^2}}\\),
                es la <strong>función \\(G\\) teórica</strong> bajo CSR, la curva contra la que el capítulo 4
                compara la \\(G\\) empírica de un patrón. Clark-Evans se queda con un solo resumen de esta curva
                —su media—, y esa renuncia es justo la que le cuesta la escala.</p>
            </li>
            <li>
              <p>Para una variable no negativa la media es el área bajo la cola, así que no hace falta derivar
                \\(G\\) para conseguir la densidad ni integrar por partes: se integra lo que ya se tiene.</p>
              $$E[D] = \\int_0^{{\\infty}} P(D > r)\\, dr = \\int_0^{{\\infty}} e^{{-\\lambda \\pi r^2}}\\, dr$$
            </li>
            <li>
              <p>Y lo que queda es la integral gaussiana,
                \\(\\int_0^{{\\infty}} e^{{-a r^2}}\\, dr = \\tfrac{{1}}{{2}}\\sqrt{{\\pi/a}}\\), con
                \\(a = \\lambda\\pi\\). El \\(\\pi\\) que trajo el área del disco se cancela contra el de la
                integral y no sobrevive ni una constante suelta:</p>
              $$E[D] = \\frac{{1}}{{2}}\\sqrt{{\\frac{{\\pi}}{{\\lambda\\pi}}}} = \\frac{{1}}{{2\\sqrt{{\\lambda}}}}$$
            </li>
          </ol>
          <p class="derivacion-resultado">Ese es el denominador de la cuarta columna de la tabla, y la fórmula se
            lee sola: \\(\\lambda\\) son puntos por unidad de área, luego \\(1/\\sqrt{{\\lambda}}\\) es una
            distancia —por eso \\(R\\) sale sin unidades por construcción y no por convenio—. La raíz avisa
            además de que la densidad no se paga en línea recta: al doblar \\(\\lambda\\), la distancia esperada
            al vecino no cae a la mitad, sino a \\(1/\\sqrt{{2}}\\) de lo que era.</p>
        </div>
      </div>

      <p>Y conviene retener de dónde salió, porque se paga más abajo: el disco del paso 2 se contó
        <strong>entero</strong>, y eso supone que el proceso sigue existiendo más allá del borde de la ventana.
        Para un punto pegado al borde eso es falso —parte de su disco cae donde nadie observó nada—, y de ahí, y
        no de ningún ajuste empírico, viene la corrección que se comenta tras la tabla.</p>

      <p>La tabla hace esa misma división para los tres. Lleva a propósito la columna del denominador, que suele
        omitirse: sin ella el índice hay que creérselo, y con ella se comprueba con una calculadora.</p>

      <table>
        <caption>Los tres regímenes de un patrón puntual, medidos con el índice de Clark-Evans sobre los datos
          canónicos de spatstat. La tercera columna dividida entre la cuarta da la quinta.</caption>
        <thead>
          <tr><th scope="col">Patrón</th><th scope="col">n</th><th scope="col">Distancia media al vecino</th>
            <th scope="col">La que daría el azar</th>
            <th scope="col">Clark-Evans</th><th scope="col">Régimen</th></tr>
        </thead>
        <tbody>
          <tr><th scope="row">{pc['redwood']['nombre']}</th><td>{pc['redwood']['n']}</td>
            <td>{n(pc['redwood']['nn_media'])}</td><td>{n(pc['redwood']['nn_esperada'])}</td>
            <td>{n(pc['redwood']['clark_evans'])}</td>
            <td>Agregado</td></tr>
          <tr><th scope="row">{pc['japanesepines']['nombre']}</th><td>{pc['japanesepines']['n']}</td>
            <td>{n(pc['japanesepines']['nn_media'])}</td><td>{n(pc['japanesepines']['nn_esperada'])}</td>
            <td>{n(pc['japanesepines']['clark_evans'])}</td>
            <td>Compatible con el azar</td></tr>
          <tr><th scope="row">{pc['cells']['nombre']}</th><td>{pc['cells']['n']}</td>
            <td>{n(pc['cells']['nn_media'])}</td><td>{n(pc['cells']['nn_esperada'])}</td>
            <td>{n(pc['cells']['clark_evans'])}</td>
            <td>Regular</td></tr>
        </tbody>
      </table>

      <p>Fíjate en que la columna del azar <em>no</em> es la misma en las tres filas —{n(pc['redwood']['nn_esperada'])},
        {n(pc['japanesepines']['nn_esperada'])} y {n(pc['cells']['nn_esperada'])}—, y ahí está el trabajo que hace
        el índice: las células tienen menos puntos, así que bajo puro azar ya les tocaría estar más separadas.
        Comparar las distancias observadas entre sí sería comparar tres densidades distintas; dividir cada una por
        la suya es lo que las vuelve comparables.</p>

      <div class="note">
        <p><strong>Si ejecutas <code>clarkevans()</code> vas a ver tres números, no uno.</strong> La tabla publica
          el que la función llama <code>naive</code>, que es la división de arriba tal cual. Los otros dos
          corrigen el <strong>efecto de borde</strong>, y conviene saber de qué va porque reaparece en todo el
          capítulo 4. La fórmula \\(E[\\bar{{d}}_{{\\min}}] = 1/(2\\sqrt{{\\lambda}})\\) vale para una ventana
          infinita. En una finita, un punto pegado al borde puede tener su vecino de verdad <em>fuera</em> del
          cuadrado, donde nadie lo midió; la distancia que se le apunta es la del vecino de dentro, que está más
          lejos. El numerador sale inflado, y \\(R\\) con él.</p>
        <p style="margin-bottom:0;">La corrección de Donnelly (1978) lo compensa, y en los tres patrones el índice
          <strong>baja</strong>: {n(pc['redwood']['clark_evans'])} →
          <strong>{n(pc['redwood']['clark_evans_donnelly'])}</strong> en las secuoyas,
          {n(pc['japanesepines']['clark_evans'])} →
          <strong>{n(pc['japanesepines']['clark_evans_donnelly'])}</strong> en los pinos y
          {n(pc['cells']['clark_evans'])} →
          <strong>{n(pc['cells']['clark_evans_donnelly'])}</strong> en las células. Ninguno cambia de régimen, así
          que la tabla se sostiene —y los pinos quedan aún más pegados al 1 de lo que ya estaban—. Pero fíjate en
          el tamaño del ajuste: en las células vale más de una décima. Sobre una ventana pequeña, o con pocos
          puntos, el borde deja de ser un decimal.</p>
      </div>

      <div class="warning">
        <p><strong>Y una advertencia sobre la fila del medio.</strong> {n(pc['japanesepines']['clark_evans'])}
          está cerca de 1, y la tabla dice «compatible con el azar», no «aleatorio». La diferencia no es cautela
          retórica: \\(R\\) se construye <em>solo</em> con la distancia al vecino <strong>más próximo</strong>, así
          que solo ve la escala más corta del patrón y es ciego a todo lo que pase más allá.</p>
        <p style="margin-bottom:0;">El caso que lo rompe es corriente en ecología, que es de donde salen las
          secuoyas: árboles que compiten con el de al lado y por eso se separan a corta distancia, pero que
          crecen en manchas grandes marcadas por el suelo o la humedad. La repulsión de cerca <em>sube</em>
          \\(R\\); la agregación de lejos, que ocurre a una escala mucho mayor que la del vecino inmediato, apenas
          pesa en la cuenta. Las dos cosas se compensan y \\(R\\) puede quedarse en 1 sobre un patrón que a la
          escala de las manchas está claramente agregado. Que \\(R\\) valga 1 no prueba que el patrón sea
          aleatorio: prueba que <em>a la escala del vecino más próximo</em> no se distingue de serlo.</p>
      </div>

      <p style="margin-bottom:0;">Y ahí está la razón de dividir por la distancia esperada en vez de comparar las
        observadas: descontada la densidad, lo que queda en \\(R\\) es la <em>disposición</em> —pero solo a una
        escala—. El capítulo 4 sustituye este único número por las funciones \\(G\\), \\(F\\), \\(K\\) y \\(g\\),
        que dicen a qué distancia ocurre cada cosa en vez de resumirlo todo en un escalar, y son exactamente la
        herramienta que le falta a la advertencia de arriba.</p>
""" + CIERRE


# =====================================================================
# MÓDULO 4 · Por qué se rompe la inferencia clásica
# =====================================================================
# Decisión de Javier del 2026-08-04: se mide por DOS frentes. Monte Carlo
# sobre un campo gaussiano simulado —donde se conoce la verdad— y
# remuestreo por bloques sobre la deserción municipal real —donde no—. Uno
# solo de los dos siempre deja la duda de si el efecto es del montaje.
# Por phi y no por posición. El módulo entero habla de phi = 4 y todas sus
# cifras salen de esta fila: con un índice fijo, reordenar PHIS en R la
# dejaría apuntando a otro alcance y la prosa seguiría leyéndose bien. Es
# el defecto de T1.2 en su versión de compilación, y T2.1 ya retiró dos
# índices mágicos de `cuadra()` por lo mismo.
# Con `next(...)` a secas, una rejilla sin phi = 4 reventaría aquí con un
# StopIteration pelado: código 1 y ni una línea de diagnóstico. Es el error
# que la inyección de T1.3.i cazó dos veces, así que se informa.
r4 = next((f for f in inf["rejilla"] if f["phi"] == 4), None)
if r4 is None:
    sys.exit("PARADO: inferencia.rejilla ya no trae la fila de phi = 4, y de ella "
             "salen todas las cifras del módulo 4.\n"
             f"        Alcances disponibles: {[f['phi'] for f in inf['rejilla']]}")
MOD4 = cabecera(
    4, "Por qué se rompe la inferencia clásica", "Broken standard errors",
    "Medir cuánto miente un intervalo de confianza calculado como si las "
    "observaciones fueran independientes. Dos frentes: simulación y dato real.") + f"""
      <p>Este es el módulo que justifica el curso. Todo lo que aprendiste en inferencia —el error estándar
        \\(s/\\sqrt{{n}}\\), el intervalo al 95&nbsp;%, el valor p— descansa en un supuesto que en el espacio es casi
        siempre falso: que las observaciones son independientes. La pregunta no es si el supuesto falla, sino
        <strong>cuánto</strong>.</p>

      <p>Primer frente, la simulación, porque es donde se conoce la respuesta. Se generan campos gaussianos sobre una
        retícula de {inf['k']}×{inf['k']} = {inf['n']} celdas, todas con media cero y varianza
        \\(\\sigma^2 = {inf['sigma']}\\), y con correlación \\(\\rho(h) = e^{{-h/\\phi}}\\) donde
        <strong>{inf['escala_h']}</strong>: dos celdas contiguas están a \\(h = 1\\) y dos en diagonal a
        \\(h = \\sqrt{{2}}\\). Se calcula la media y su intervalo al 95&nbsp;% <em>como si</em> las
        {inf['n']} celdas fueran independientes; y se cuenta cuántas veces el intervalo contiene la media
        verdadera, que se sabe que es cero. Con
        {ent(inf['nrep'])} réplicas por valor de \\(\\phi\\), y una perturbación de \\(10^{{-9}}\\) sumada a la
        diagonal —invisible frente a una varianza de 1— para que la factorización de Cholesky no falle por redondeo
        con \\(\\phi\\) grande. Se dice porque forma parte del modelo que se simula, no del que se enseña.</p>

      <div class="simulador" data-simulador="ee-ingenuo">
        <h4><i class="fas fa-triangle-exclamation" aria-hidden="true"></i> El error estándar ingenuo, medido</h4>
        <p class="simulador-intro">Recorre el alcance de la correlación con el deslizador. Las curvas no se mueven,
          y es a propósito: el alcance ya es el eje horizontal, así que están dibujadas todas a la vez. Lo que se
          mueve es el marcador que dice dónde estás, el campo simulado de debajo y la lectura. Empieza por la
          izquierda, en \\(\\phi = 0\\) —el mismo ruido, todavía sin correlación— y mira dónde la cobertura se
          despega del 95&nbsp;% que el intervalo promete.</p>
        <div class="simulador-controles"></div>
        <div class="grafico-wrapper" style="height:250px;">
          <canvas aria-label="Error estándar ingenuo frente al real, y cobertura del intervalo al 95 por ciento, en función del alcance de la correlación. Un marcador vertical señala el alcance elegido con el deslizador" role="img"></canvas>
        </div>
        <div class="geomapa" data-geomapa="cap1-campo"></div>
        <div class="simulador-lectura"></div>
      </div>

      <p>Sin correlación el método funciona: la cobertura sale <strong>{n(inf['cobertura_independiente'])}</strong>,
        que es el 95&nbsp;% prometido. Con \\(\\phi = {r4['phi']}\\) —vecinos inmediatos correlacionados a
        {n(r4['rho_vecino'])}— la cobertura se desploma a <strong>{n(r4['cobertura'])}</strong>
        (± {n(r4['emc_cobertura'])} de error de Monte Carlo). Un intervalo que promete equivocarse una vez de cada
        veinte se equivoca <strong>cuatro de cada cinco</strong>.</p>

      <div class="definition">
        <h3>De dónde sale el destrozo, en tres pasos</h3>
        <p>La varianza de una media <em>no</em> es \\(\\sigma^2/n\\) cuando hay covarianzas:</p>
        <p style="text-align:center;">$$\\operatorname{{Var}}(\\bar{{Z}}) =
          \\frac{{1}}{{n^2}}\\left[\\sum_i \\operatorname{{Var}}(Z_i)
          + \\sum_{{i \\neq j}} \\operatorname{{Cov}}(Z_i, Z_j)\\right]
          = \\frac{{\\sigma^2}}{{n}}\\left[1 + \\frac{{1}}{{n}}\\sum_{{i \\neq j}} \\rho_{{ij}}\\right]$$</p>
        <p>El corchete es el <strong>factor de inflación por diseño</strong>. Vale 1 solo si todas las correlaciones
          se anulan. De \\(\\phi = {r4['phi']}\\) a las cifras que publica el módulo hay tres pasos, y conviene
          verlos separados porque el tercero es el que casi nadie cuenta.</p>
        <p><strong>Uno · de \\(\\phi\\) a la correlación.</strong> Como \\(h\\) va en pasos de retícula, dos celdas
          contiguas están a \\(h = 1\\), así que su correlación es \\(e^{{-1/\\phi}}\\). Con
          \\(\\phi = {r4['phi']}\\), \\(e^{{-1/4}} = {n(r4['rho_vecino'])}\\); las de la diagonal, a
          \\(h = \\sqrt{{2}}\\), quedan en {n(r4['rho_diagonal'])}. Ahí se ve que \\(h\\) es distancia y no
          vecindad.</p>
        <p><strong>Dos · de la correlación al efecto de diseño.</strong> Sumar el corchete entero sobre las
          {inf['n']} celdas da <strong>{n(r4['efecto_diseno'])}</strong>: la media varía esas veces más de lo que
          variaría con {inf['n']} datos independientes. Leído al revés, las {inf['n']} celdas informan como
          <strong>{n(r4['n_eff'])}</strong>, que es el tamaño efectivo del módulo siguiente. Este es el número que
          continúa el hilo del capítulo.</p>
        <p><strong>Tres · y lo que el software declara se queda todavía más corto.</strong> Porque \\(s^2\\) también
          se encoge con la correlación: parte de la variabilidad entre celdas se la ha comido la dependencia, y su
          esperanza ya no es \\(\\sigma^2\\) sino</p>
        <p style="text-align:center;">$$\\mathbb{{E}}[s^2] = \\sigma^2\\,\\frac{{n}}{{n-1}}
          \\left(1 - \\frac{{1}}{{n_{{\\text{{eff}}}}}}\\right) = {n(r4['s2_esperada'])}$$</p>
        <p style="margin-bottom:0;">El programa divide una \\(s\\) ya menguada entre \\(\\sqrt{{n}}\\), así que el
          error estándar que imprime es aún menor. Medido: el real es <strong>{n(r4['factor'])} veces</strong> el
          suyo, y como el error estándar entra al cuadrado en la varianza, <strong>la varianza que declara se queda
          {n(r4['inflacion_varianza'])} veces corta</strong> — que es {n(r4['factor'])}². Los dos cocientes no son
          el mismo número porque no miden lo mismo: {n(r4['efecto_diseno'])} es cuánto se ensancha la varianza
          <em>verdadera</em> de la media; {n(r4['inflacion_varianza'])} es cuánto se queda corta la que el programa
          <em>declara</em>. La dependencia cobra dos veces, y la segunda vez no se ve.</p>
      </div>

      <div class="warning">
        <p style="margin-bottom:0;"><strong>Y no es un problema de sesgo.</strong> La media sigue estando bien
          estimada: la simulación da {n(ur['media_de_las_medias'])} frente a una media verdadera de
          {ur['media_del_proceso']}. Lo que está mal no es la estimación, es <strong>la confianza</strong>. Ése es
          justo el fallo que nadie ve, porque el número que se publica parece correcto.</p>
      </div>

      <p>Segundo frente, el dato real, donde no hay verdad conocida y hay que medir de otra manera. La deserción
        escolar de los <strong>{ent(ir['n_municipios'])}</strong> municipios colombianos tiene media
        {n(ir['media'])}&nbsp;%. Su error estándar se estima dos veces por remuestreo con
        {ent(ir['nboot'])} réplicas: remuestreando <em>municipios sueltos</em> —que es suponer independencia— y
        remuestreando <strong>departamentos enteros</strong>, que respeta la dependencia dentro de cada uno.</p>

      <table>
        <caption>Error estándar de la deserción media municipal por dos remuestreos, y el intervalo al 95 % que
          produce cada uno.</caption>
        <thead>
          <tr><th scope="col">Remuestreo</th><th scope="col">Error estándar</th><th scope="col">IC al 95 %</th>
            <th scope="col">Ancho</th></tr>
        </thead>
        <tbody>
          <tr><th scope="row">Municipios sueltos (i.i.d.)</th><td>{n(ir['ee_bootstrap_iid'])}</td>
            <td>[{n(ir['ic_iid'][0])}, {n(ir['ic_iid'][1])}]</td><td>{n(ir['ancho_iid'])}</td></tr>
          <tr><th scope="row">Departamentos enteros (bloques)</th><td>{n(ir['ee_bootstrap_bloques'])}</td>
            <td>[{n(ir['ic_bloques'][0])}, {n(ir['ic_bloques'][1])}]</td><td>{n(ir['ancho_bloques'])}</td></tr>
        </tbody>
      </table>

      <p>Factor <strong>{n(ir['factor'])}</strong>. El intervalo honesto es cuatro veces más ancho que el ingenuo, y
        eso con dato real, sin simular nada. Los dos están centrados en el mismo sitio.</p>

""" + tabs(
    "El error estándar ingenuo frente al de bloques, sobre la deserción real",
    """source("precalculo/fuentes.R")

mun &lt;- carga_municipios()
ok  &lt;- mun[!is.na(mun$desercion), ]
ok$dpto &lt;- substr(ok$divipola, 1, 2)
bloques &lt;- split(ok$desercion, ok$dpto)
B &lt;- 4000

# Las semillas son las del precalculo (2026 + 200 y 2026 + 201), asi que
# esto reproduce sus cifras EXACTAMENTE. Un bootstrap "parecido" daria un
# numero parecido, y un numero parecido no verifica nada.
set.seed(2226)
ee_iid &lt;- sd(replicate(B, mean(sample(ok$desercion, nrow(ok), replace = TRUE))))
set.seed(2227)
ee_blq &lt;- sd(replicate(B, {
  sel &lt;- sample(seq_along(bloques), length(bloques), replace = TRUE)
  mean(unlist(bloques[sel], use.names = FALSE))
}))
cat(sprintf("i.i.d. = %.5f | bloques = %.5f | factor = %.5f\\n",
            ee_iid, ee_blq, ee_blq / ee_iid))
#&gt; """ + f"i.i.d. = {n(ir['ee_bootstrap_iid'])} | bloques = "
    f"{n(ir['ee_bootstrap_bloques'])} | factor = {n(ir['factor'])}",
    """import pandas as pd, numpy as np

mun = pd.read_csv("datos/procesado/municipios_llave.csv", dtype={"divipola": str})
d = mun.dropna(subset=["desercion"])
x = d.desercion.to_numpy()
dep = d.divipola.str[:2].to_numpy()
grupos = [x[dep == k] for k in np.unique(dep)]

# OJO: esto NO reproduce las cifras de R, y no es un fallo del codigo.
# R y numpy tienen generadores distintos: la misma semilla no da la misma
# secuencia. Ni siquiera el primer decimal aguanta —R da 4.2 y esto 4.3—,
# asi que se imprime REDONDEADO A ENTERO, que es lo que de verdad
# garantiza un remuestreo con 4 000 replicas. Anunciar un decimal que no
# se sostiene seria mentir sobre lo que una semilla asegura.
rng = np.random.default_rng(2026)
B = 4000
ee_iid = np.std([rng.choice(x, x.size, replace=True).mean()
                 for _ in range(B)], ddof=1)
ee_blq = np.std([np.concatenate([grupos[i] for i in
                 rng.integers(0, len(grupos), len(grupos))]).mean()
                 for _ in range(B)], ddof=1)
print(f"n = {len(x)}, {len(grupos)} bloques, "
      f"el e.e. de bloques es {ee_blq / ee_iid:.0f} veces el i.i.d.")
#> """ + f"n = {ir['n_municipios']}, {ir['n_departamentos']} bloques, "
    f"el e.e. de bloques es {n(ir['factor'], 0)} veces el i.i.d.") + f"""
      <div class="note">
        <p style="margin-bottom:0;"><strong>Los dos frentes dicen lo mismo con números distintos, y eso importa.</strong>
          La simulación da un factor de {n(r4['factor'])} con una correlación que elegimos nosotros; el dato real da
          {n(ir['factor'])} con la que tiene Colombia. El primero demuestra el mecanismo, el segundo demuestra que
          pasa de verdad. Publicar solo el primero sería enseñar un montaje; publicar solo el segundo dejaría la
          duda de si el efecto es otra cosa.</p>
      </div>
""" + CIERRE


# =====================================================================
# MÓDULO 5 · Tamaño de muestra efectivo
# =====================================================================
MOD5 = cabecera(
    5, "Tamaño de muestra efectivo", "Effective sample size",
    "Traducir «hay dependencia» a una cifra que se entienda: cuántas "
    "observaciones independientes valen las que tienes.") + f"""
      <p>El módulo 4 dejó una pregunta incómoda: si el intervalo honesto es {n(ir['factor'])} veces más ancho, ¿de
        cuántos municipios estamos hablando en realidad? El <strong>tamaño de muestra efectivo</strong> responde
        justo eso.</p>

      <p>La respuesta para Colombia, primero, y la fórmula después. Los <strong>{ent(ne['desercion_n'])}</strong>
        municipios con dato de deserción informan como <strong>{n(ne['desercion_municipal'])}</strong> municipios
        independientes. Es el <strong>{n(ne['desercion_pct'])}&nbsp;%</strong> de la información que aparentaban
        tener.</p>

      <div class="definition">
        <h3>De dónde sale ese 5 %</h3>
        <p>Se define \\(n_{{\\text{{eff}}}}\\) como el número de observaciones independientes que darían la misma
          varianza de la media. Con correlación constante \\(\\rho\\) entre todos los pares,</p>
        <p style="text-align:center;">$$n_{{\\text{{eff}}}} = \\frac{{n}}{{1 + (n-1)\\rho}}$$</p>
        <p style="margin-bottom:0;">Y con eso a la vista aparece lo que de verdad enseña este módulo: cuando
          \\(n \\to \\infty\\), \\(n_{{\\text{{eff}}}} \\to 1/\\rho\\). <strong>Hay un techo.</strong> Con
          \\(\\rho = 0{{,}}01\\) —una correlación que nadie llamaría preocupante— ese techo son 100 observaciones,
          da igual cuántas se recojan.</p>
      </div>

      <div class="simulador" data-simulador="n-efectivo">
        <h4><i class="fas fa-compress" aria-hidden="true"></i> El techo de la información</h4>
        <p class="simulador-intro">Mueve \\(\\rho\\) y mira cuánto aporta pasar de
          {ent_mate(ne['enes'][0])} a {ent_mate(ne['enes'][-1])} observaciones: la curva se despega de la
          diagonal —el caso sin correlación— y se aplasta contra el techo \\(1/\\rho\\), que se mueve con el
          deslizador. El rombo es Colombia, y ahora lleva <strong>dos curvas fijas</strong> detrás: la del
          \\(\\rho\\) que <em>implica</em> ese {n(ne['desercion_municipal'])} —pasa por el rombo, porque de ahí se
          despeja— y la del \\(\\rho\\) <em>medido</em> sobre el mapa, que pasa muy por encima. La distancia entre
          las dos es el asunto del recuadro de abajo.</p>
        <div class="simulador-controles"></div>
        <div class="grafico-wrapper" style="height:300px;">
          <canvas aria-label="Tamaño de muestra efectivo frente al número de observaciones, para la correlación que fija el deslizador, con el techo un partido por rho, la diagonal sin correlación, el punto de Colombia y las dos curvas de referencia: la del rho implícito, que pasa por ese punto, y la del rho medido en el mapa, que pasa por encima" role="img"></canvas>
        </div>
        <div class="simulador-lectura"></div>
      </div>

      <p>Con \\(n = {ent_mate(ne['enes'][-1])}\\) y \\(\\rho = {ne['rhos'][1]}\\) el tamaño efectivo es
        <strong>{n(ne['rejilla'][-1]['n_eff'][1])}</strong>: el
        <strong>{n(ne['rejilla'][-1]['pct'][1])}&nbsp;%</strong>. Y con
        \\(\\rho = {ne['rhos'][4]}\\) baja a <strong>{n(ne['rejilla'][-1]['n_eff'][4])}</strong>. Mil observaciones
        que valen por diez.</p>

      <div class="definition">
        <h3>De dónde sale el {n(ne['desercion_municipal'])}, y qué \\(\\rho\\) hay detrás</h3>
        <p>Ninguno. Esa cifra <strong>no viene de estimar un \\(\\rho\\)</strong>: viene del módulo 4, del cociente
          entre los dos remuestreos, \\(n \\cdot (ee_{{\\text{{iid}}}}/ee_{{\\text{{bloques}}}})^2\\). La
          equicorrelación no interviene en ningún paso. Así que la pregunta honesta no es cuál es el \\(\\rho\\)
          escondido —no lo hay— sino <strong>cuáles son los dos \\(\\rho\\) que se pueden poner ahí</strong>, y en
          qué se separan.</p>
        <ul>
          <li><strong>El \\(\\rho\\) implícito, {n(rt['implicito'])}.</strong> El que la equicorrelación
            <em>necesitaría</em> para explicar la pérdida medida. Se despeja de la fórmula,
            \\(\\rho = (n/n_{{\\text{{eff}}}} - 1)/(n-1)\\), así que reproduce el
            {n(ne['desercion_municipal'])} por construcción. <strong>No es una estimación de nada:</strong> es una
            retro-transformación, y por eso su curva pasa por el rombo — no puede no pasar.</li>
          <li><strong>El \\(\\rho\\) medido, {n(rt['estimado'])}.</strong> La correlación media entre pares,
            estimada sobre el mapa con el mismo método del ejercicio 3: un correlograma de
            {ent(rt['n_bandas'])} bandas, la I de Moran de cada una y el promedio ponderado por sus pares. Con él,
            los {ent(ne['desercion_n'])} municipios informarían como <strong>{n(rt['n_eff_con_estimado'])}</strong>,
            no como {n(ne['desercion_municipal'])}.</li>
        </ul>
        <p style="margin-bottom:0;">Se separan un factor <strong>{n(rt['razon_rho'])}</strong> en \\(\\rho\\) y
          <strong>{n(rt['razon_n_eff'])}</strong> en información. Y esa discrepancia no es un fallo del montaje:
          <strong>es la medida del supuesto</strong>. Sigue leyendo.</p>
      </div>

      <div class="warning">
        <p><strong>La fórmula supone equicorrelación, y eso es falso en el espacio.</strong>
          El correlograma del módulo 3 dice justo lo contrario: la correlación decae con la distancia. Así que
          \\(n_{{\\text{{eff}}}}\\) sirve como <strong>orden de magnitud</strong> y como argumento —«no tengo
          {ent(ne['desercion_n'])} datos, tengo el {n(ne['desercion_pct'])}&nbsp;% de esa información»—, no como cifra de
          diseño muestral. El cálculo exacto necesita la matriz de covarianzas entera, y eso llega en el capítulo 9.
          Se dice aquí y no en una nota al pie porque es la clase de matiz que se pierde al citar.</p>
        <p style="margin-bottom:0;"><strong>Y ahora esa advertencia trae número.</strong> Mira por qué se separan
          los dos \\(\\rho\\). Entre municipios vecinos —la primera banda, de 0 a
          {ent(rt['bandas'][0]['d2'])}&nbsp;km— la I vale <strong>{n(rt['I_primera_banda'])}</strong>, que es mucho;
          pero entre {ent(rt['bandas'][4]['d1'])} y {ent(rt['bandas'][5]['d2'])}&nbsp;km se vuelve
          <em>negativa</em>, y ahí están {ent(rt['pares_lejanos'])} de los {ent(rt['pares_totales'])} pares. La
          equicorrelación obliga a resumir todo eso en <strong>un</strong> número, y el promedio se hunde hacia
          cero. Por eso el \\(\\rho\\) que haría falta para explicar la pérdida real es
          {n(rt['razon_rho'])} veces el que se mide: no es que la medición falle, es que
          <strong>el supuesto no cabe en el dato</strong>. Un \\(\\rho\\) solo no puede describir a la vez a los
          vecinos y a los municipios que están a {ent(rt['bandas'][6]['d2'])}&nbsp;km.</p>
      </div>

      <p>Sobre el campo simulado del módulo 4 la cuenta se puede hacer <em>exacta</em>, porque la covarianza se
        conoce. Con \\(\\phi = {r4['phi']}\\), las {inf['n']} celdas valen
        <strong>{n(ne['exacto_campo'][4]['n_eff'])}</strong>: un
        {n(ne['exacto_campo'][4]['pct'])}&nbsp;% de la información. La aproximación por equicorrelación y el cálculo
        exacto cuentan la misma historia.</p>

""" + tabs(
    "El tamaño efectivo, y su techo",
    """n_eff &lt;- function(n, rho) n / (1 + (n - 1) * rho)

for (rho in c(0.01, 0.1)) {
  cat(sprintf("rho = %.2f -> n = 1000 da n_eff = %.5f (techo %.5f)\\n",
              rho, n_eff(1000, rho), 1 / rho))
}
#&gt; """ + f"rho = 0.01 -> n = 1000 da n_eff = {n(ne['rejilla'][-1]['n_eff'][1])} (techo {n(100)})"
    + """
#&gt; """ + f"rho = 0.10 -> n = 1000 da n_eff = {n(ne['rejilla'][-1]['n_eff'][4])} (techo {n(10)})",
    """def n_eff(n, rho):
    return n / (1 + (n - 1) * rho)

for rho in (0.01, 0.1):
    print(f"rho = {rho:.2f} -> n = 1000 da n_eff = {n_eff(1000, rho):.5f} "
          f"(techo {1/rho:.5f})")
#> """ + f"rho = 0.01 -> n = 1000 da n_eff = {n(ne['rejilla'][-1]['n_eff'][1])} (techo {n(100)})"
    + """
#> """ + f"rho = 0.10 -> n = 1000 da n_eff = {n(ne['rejilla'][-1]['n_eff'][4])} (techo {n(10)})") + CIERRE


# =====================================================================
# MÓDULO 6 · Estacionariedad, isotropía y una sola realización
# =====================================================================
MOD6 = cabecera(
    6, "Estacionariedad, isotropía y una sola realización", "One realization",
    "Ver el problema que hace difícil toda la estadística espacial: del "
    "proceso que se quiere estudiar solo existe una realización.") + f"""
      <p>Mira los tres mapas de abajo. Son <strong>tres realizaciones del mismo proceso</strong>: misma media, misma
        covarianza, mismos parámetros. Y no se parecen. No están escogidas: son <strong>las tres primeras</strong> de
        las {ent(ur['n_realizaciones'])} que simula el generador, y de ese mismo lote salen la banda del gráfico y
        todas las cifras de este módulo. Elegir las tres más distintas habría dado una figura más vistosa y un
        argumento peor.</p>

      <div class="simulador" data-simulador="una-realizacion">
        <h4><i class="fas fa-dice" aria-hidden="true"></i> Tres veces el mismo proceso</h4>
        <p class="simulador-intro">Tres realizaciones de un campo gaussiano con media {ur['media_del_proceso']} y
          alcance \\(\\phi = {ur['phi']}\\) sobre {ur['k']}×{ur['k']} celdas. <strong>Cambia de realización</strong> y
          mira moverse las tres cosas a la vez: el mapa, la lectura y —debajo— el variograma <em>de esa</em>
          realización contra el teórico y la banda del 5&nbsp;% al 95&nbsp;%.</p>
        <div class="simulador-controles"></div>
        <div class="geomapa" data-geomapa="cap1-realizacion"></div>
        <div class="grafico-wrapper" style="height:250px;">
          <canvas aria-label="Variograma de una realización frente al teórico, con la banda del 5 al 95 por ciento sobre mil realizaciones" role="img"></canvas>
        </div>
        <div class="simulador-lectura"></div>
      </div>

      <p>Las medias espaciales de las tres son {n(D['realizaciones_vistas'][0]['media'])},
        {n(D['realizaciones_vistas'][1]['media'])} y {n(D['realizaciones_vistas'][2]['media'])}, cuando la media del
        proceso es <strong>{ur['media_del_proceso']}</strong>. Sobre {ent(ur['n_realizaciones'])} realizaciones, las
        medias van de {n(ur['media_min'])} a {n(ur['media_max'])} con desviación típica
        <strong>{n(ur['sd_de_las_medias'])}</strong>.</p>

      <div class="warning">
        <p><strong>La cifra que hay que recordar de este módulo.</strong> De esas {ent(ur['n_realizaciones'])}
          realizaciones —todas del mismo proceso, todas con media verdadera {ur['media_del_proceso']}— el análisis
          ingenuo declararía significativa la media en el <strong>{n(ur['pct_rechaza_ingenuo'])}&nbsp;%</strong> de
          los casos (± {n(ur['emc_rechaza'])}), cuando debería hacerlo en el
          {n(ur['pct_esperado_si_valiera'])}&nbsp;%.</p>
        <p style="margin-bottom:0;">Y aquí conviene ver que ese {n(ur['pct_rechaza_ingenuo'])}&nbsp;% es el módulo 4
          del revés: allí la <em>cobertura</em> con \\(\\phi = {r4['phi']}\\) salía {n(r4['cobertura'])}, o sea un
          {n(ur['pct_rechaza_modulo4'])}&nbsp;% de rechazo. Los dos números miden lo mismo por caminos distintos y se
          separan {n(ur['discrepancia_con_modulo4'])} puntos, que es poco más de un error de Monte Carlo. El
          generador del capítulo <strong>comprueba esa coherencia y se detiene</strong> si los dos módulos se
          separan más de tres errores conjuntos: dos cifras que deberían coincidir y viven a dos módulos de
          distancia son justo las que nadie compara.</p>
      </div>

      <div class="definition">
        <h3>Estacionariedad: el supuesto que hace posible estimar algo</h3>
        <p>Si solo hay una realización, ¿cómo se estima una media o una covarianza? Solo hay una salida: suponer que
          <strong>distintas partes del mapa son repeticiones del mismo mecanismo</strong>. Eso es la
          estacionariedad.</p>
        <ul>
          <li><strong>De segundo orden:</strong> \\(E[Z(s)] = \\mu\\) para todo \\(s\\), y
            \\(\\operatorname{{Cov}}(Z(s), Z(s+h)) = C(h)\\) depende solo de la separación \\(h\\), no de dónde
            estén los dos puntos.</li>
          <li><strong>Intrínseca:</strong> más débil, y por eso más usada. Solo pide que las diferencias sean
            estacionarias: \\(\\tfrac{{1}}{{2}}\\operatorname{{Var}}(Z(s+h) - Z(s)) = \\gamma(h)\\). Un proceso puede
            ser intrínseco sin tener varianza finita —el movimiento browniano lo es— y por eso el variograma es más
            general que la covarianza.</li>
          <li><strong>Isotropía:</strong> además, que \\(C\\) y \\(\\gamma\\) dependan solo de \\(\\lVert h \\rVert\\)
            y no de la dirección. Es una comodidad, no una ley: la anisotropía del capítulo 9 es lo que pasa cuando
            no se cumple.</li>
        </ul>
        <p style="margin-bottom:0;">Sin estacionariedad no hay repetición, y sin repetición no hay estimación. El
          precio: si la media cambia de sitio a sitio —una <em>tendencia</em>—, ese cambio se contabiliza como
          dependencia. Es exactamente lo que pasaba con la altitud en el módulo 3.</p>
      </div>

      <div class="warning">
        <p style="margin-bottom:0;"><strong>Estacionariedad no es estacionalidad</strong>, aunque en español se
          parezcan tanto que la confusión es casi obligatoria. La <em>estacionalidad</em> es un patrón que se repite
          con las estaciones del año —julio se parece a julio— y es un concepto de <strong>series de tiempo</strong>:
          en el espacio no hay estaciones. La <strong>estacionariedad</strong> es esto otro: que las propiedades
          estadísticas del proceso no cambien según <em>dónde</em> se mire. En inglés ni se rozan —<em>seasonality</em>
          y <em>stationarity</em>—, y por eso la trampa es nuestra y no de la literatura. Si en algún momento de este
          curso lees «estacionariedad» y te suena a estaciones del año, vuelve a este recuadro.</p>
      </div>

      <p>El variograma del simulador enseña el otro lado del problema, y por eso <strong>cambia con el
        botón</strong>: cada realización trae el suyo. Las tres se apartan del teórico, en su peor rezago, en
        {n(rv[0]['desvio_rel_max'])}, {n(rv[1]['desvio_rel_max'])} y {n(rv[2]['desvio_rel_max'])} veces su valor
        —rezagos {ent(rv[0]['lag_desvio_max'])}, {ent(rv[1]['lag_desvio_max'])} y
        {ent(rv[2]['lag_desvio_max'])}—, y la banda del 5&nbsp;% al 95&nbsp;% en el rezago 4 tiene una anchura de
        <strong>{n(ur['banda_rel_lag4'])}</strong> veces el valor teórico. Es tan ancha que las tres caben dentro de
        ella en los ocho rezagos —en el 4 se apartan {n(rv[0]['desvio_rel_lag4'])},
        {n(rv[1]['desvio_rel_lag4'])} y {n(rv[2]['desvio_rel_lag4'])}—, y conviene no leer eso como un aprobado:
        <strong>caber en la banda no es parecerse al proceso</strong>, porque la banda mide lo que puede pasar, no lo
        que pasó. Con una realización no se puede saber si lo que se ve es el proceso o el azar de esa realización:
        es el problema fundamental de la disciplina, no una limitación del método.</p>

      <div class="note">
        <p style="margin-bottom:0;"><strong>Por qué el mapa y la curva son ahora el mismo experimento.</strong> Hasta
          esta versión los tres mapas venían de una simulación <em>aparte</em>, con otra rejilla y otra semilla, y la
          curva de abajo era la de un campo que no estaba en ningún mapa. Las cifras eran todas correctas y la prosa
          también: lo que estaba mal era el cableado, y eso no lo ve ningún auditor de números. Si alguna vez heredas
          una figura de otra persona, la pregunta que más rinde no es «¿son correctos estos números?» sino
          <strong>«¿son de este dato?»</strong>.</p>
      </div>

""" + tabs(
    "Una realización no es el proceso",
    """# La semilla es la del precalculo (2026 + 300), asi que esto
# reproduce sus cifras EXACTAMENTE. Ojo con cual: la del bootstrap del
# modulo 4 es otra, y con ella el bloque da un 0.44541 muy parecido y
# equivocado. Un numero parecido es lo peor que puede devolver una
# verificacion, porque no se distingue de uno correcto.
set.seed(2326)
k &lt;- 16; n &lt;- k^2
rej &lt;- expand.grid(x = 1:k, y = 1:k)
S   &lt;- exp(-as.matrix(dist(rej)) / 4)        # phi = 4
L   &lt;- chol(S + diag(1e-9, n))

medias &lt;- replicate(1000, mean(crossprod(L, rnorm(n))))
cat(sprintf("sd de las medias = %.5f | recorrido [%.5f, %.5f]\\n",
            sd(medias), min(medias), max(medias)))
#&gt; """ + f"sd de las medias = {n(ur['sd_de_las_medias'])} | recorrido "
    f"[{n(ur['media_min'])}, {n(ur['media_max'])}]",
    """import numpy as np

# Aqui NO se busca reproducir la cifra de R: numpy tiene otro generador,
# asi que la misma semilla da otra secuencia. Lo que tiene que salir
# igual es el ORDEN DE MAGNITUD, y por eso se imprime con un decimal.
rng = np.random.default_rng(2326)
k = 16; n = k * k
xy = np.array([(i, j) for j in range(1, k + 1) for i in range(1, k + 1)], float)
S = np.exp(-np.sqrt(((xy[:, None] - xy[None, :]) ** 2).sum(-1)) / 4)
L = np.linalg.cholesky(S + 1e-9 * np.eye(n))

medias = np.array([(L @ rng.standard_normal(n)).mean() for _ in range(1000)])
print(f"media del proceso = 0 | sd de las medias = {medias.std(ddof=1):.1f}")
#> """ + f"media del proceso = 0 | sd de las medias = {n(ur['sd_de_las_medias'], 1)}") + CIERRE


# =====================================================================
# MÓDULO 7 · Escala, soporte y agregación
# =====================================================================
pr = ec["principal"]
MOD7 = cabecera(
    7, "Escala, soporte y agregación", "Scale and the MAUP",
    "Primera pincelada del MAUP: la misma variable cambia de valor —y a "
    "veces de signo— según sobre qué unidades se mida. Y, con las unidades "
    "quietas, según cómo se agregue.") + f"""
      <p>La deserción escolar de los {ent(es['n_municipal'])} municipios colombianos tiene un índice de Moran de
        <strong>{n(es['moran_municipal'])}</strong>: autocorrelación inequívoca. Agrega esos municipios a los
        {es['n_departamental']} departamentos y la misma variable da <strong>{n(es['moran_departamental'])}</strong>,
        que ya no se distingue del azar (p&nbsp;=&nbsp;{n(es['p_departamental'])}). Una caída del
        <strong>{n(es['caida_pct'])}&nbsp;%</strong>.</p>

      <p>No se ha cambiado el dato, ni la variable, ni el país. Se ha cambiado <strong>la unidad de análisis</strong>,
        y la unidad de análisis es una <strong>decisión de modelado</strong>, no de presentación. Eso es el
        <em>problema de la unidad de área modificable</em> —el MAUP—, y es lo que el capítulo 3 desarrolla entero.</p>

      <div class="simulador" data-simulador="agregacion">
        <h4><i class="fas fa-object-group" aria-hidden="true"></i> Agregar cambia la correlación</h4>
        <p class="simulador-intro">Sobre {ent(ag['niveles'][0]['n_unidades'])} celdas con correlación conocida, se
          promedian bloques cada vez más grandes y se recalcula la correlación. Y al lado, los
          {ec['n_pares']} pares reales de variables colombianas a las dos escalas.</p>
        <div class="simulador-controles"></div>
        <div class="grafico-wrapper" style="height:250px;">
          <canvas aria-label="Correlación entre dos variables según el tamaño del bloque de agregación, y los trece pares reales a escala municipal y departamental" role="img"></canvas>
        </div>
        <div class="simulador-lectura"></div>
      </div>

      <p>En la versión controlada el efecto es brutal: la correlación pasa de
        <strong>{n(ag['corr_base'])}</strong> con las celdas sueltas —base teórica {ag['corr_teorica_base']}— a
        <strong>{n(ag['corr_max'])}</strong> agregando en bloques de
        {int(ag['niveles'][-1]['celdas_por_unidad'] ** 0.5)}×{int(ag['niveles'][-1]['celdas_por_unidad'] ** 0.5)}
        celdas: un <strong>{n(ag['subida_pct'])}&nbsp;%</strong> más.</p>

      <div class="definition">
        <h3>Por qué sube: el efecto Gehlke–Biehl</h3>
        <p>Descompón cada variable en un componente <em>compartido</em> —que es lo que las correlaciona— y un ruido
          propio de cada celda. Al promediar \\(m\\) celdas, el compartido apenas cambia porque es suave y las celdas
          vecinas tienen casi el mismo valor; el ruido, en cambio, se cancela: su varianza se divide por \\(m\\).
          La correlación es el cociente entre lo que sobrevive y lo que había, así que sube.</p>
        <p style="margin-bottom:0;"><strong>Y ahí está la condición del fenómeno, que es lo que se suele omitir:</strong>
          el efecto necesita que el ruido <em>no</em> tenga estructura espacial. Si el componente independiente
          también fuera un campo suave, promediar se llevaría los dos por igual y no pasaría nada. {ag['mecanismo']}</p>
      </div>

      <div class="warning">
        <p><strong>Ahora la parte incómoda: agregar no siempre infla.</strong> La versión corta de esta lección —«al
          agregar sube la correlación»— es falsa, y basta el dato colombiano para verlo. Sobre
          {ec['n_variables']} variables municipales, los {ec['n_pares']} pares con correlación apreciable se comportan
          así al pasar de municipio a departamento: <strong>{ec['n_suben']} suben</strong>,
          <strong>{ec['n_bajan']} bajan</strong> y <strong>{ec['n_invierten']} invierte el signo</strong>.</p>
        <p style="margin-bottom:0;">Agregar <em>cambia</em> la correlación. En qué dirección, depende de cómo estén
          repartidos el componente compartido y el ruido, y eso no se sabe de antemano.</p>
      </div>

      <p>El par principal —puntaje medio de Saber 11 frente a hogares con internet— va de
        <strong>{n(pr['r_municipal'])}</strong> por municipio a <strong>{n(pr['r_departamental'])}</strong> por
        departamento. Y no lo ponen los municipios diminutos: barriendo el umbral de tamaño, entre incluirlos todos
        y exigir al menos {pr['barrido'][2]['umbral']} estudiantes la correlación municipal se mueve
        <strong>{n(pr['diferencia_umbral_30'])}</strong>.</p>

      <div class="note">
        <p style="margin-bottom:0;"><strong>Ese barrido no es celo, es una cicatriz.</strong> La primera versión de
          este módulo iba a publicar que la correlación subía un 345&nbsp;% al agregar, con otro par de variables.
          Era cierto en el sentido aritmético y falso en el que importa: las dos cifras eran ruido con signos
          opuestos —0,02 y −0,09— y el «345&nbsp;%» era el cociente entre dos ceros. Lo salvó barrer el umbral en
          vez de publicar una cifra sola, que es la misma receta que ya había salvado la falacia ecológica del
          capítulo 3 en la fase anterior.</p>
      </div>

      <p>Hasta aquí la <strong>escala</strong>: cambiar el tamaño de la unidad cambia el resultado. Queda la otra
        mitad del título, más mundana y que se rompe bastante más a menudo — <strong>cómo</strong> se agrega. Al
        pasar de {ent(es['n_municipal'])} municipios a {es['n_departamental']} departamentos no solo cambias de
        unidad: cambias el <em>soporte</em>, y el módulo 2 ya dijo qué significa eso. El número dejaba de hablar de
        un municipio y pasa a hablar de un departamento entero. Lo que viene es qué puede salir mal en ese paso.</p>

      <div class="warning">
        <p><strong>El error más caro de la agregación cabe en una línea.</strong> Toma los condados de Carolina
        del Norte, ponles encima una rejilla de {agn['n_celdas']} rectángulos que no tiene nada que ver con sus
        fronteras, y suma las muertes de cada rectángulo con la orden más natural del mundo: la que empareja
        por «se tocan». Eran <strong>{agn['total_condados']}</strong> muertes. Salen
        <strong>{ent(agn['total_rectangulos'])}</strong>, un <strong>{n(agn['inflacion_pct'])}&nbsp;%</strong> más.</p>
        <p style="margin-bottom:0;">No hay ningún fallo de programación. <strong>{cc['nombre']}</strong> toca
        {cc['n_celdas_toca']} rectángulos y aporta sus {cc['sids']} muertes <em>enteras</em> a los
        {cc['n_celdas_toca']}, porque «intersecta» es cierto {cc['n_celdas_toca']} veces: donde había
        {cc['sids']} salen <strong>{cc['aporte_predicado']}</strong>. El total deja de conservarse y nadie avisa:
        sale un mapa, con su leyenda y sus colores.</p>
      </div>

      <p>Antes de la explicación, míralo. La rejilla no respeta ni una frontera, y <strong>{cc['nombre']}</strong>
        —el condado en naranja— cae en {cc['n_celdas_toca']} celdas a la vez. Conmuta entre las dos reglas y fíjate
        en el número que aparece dentro de cada celda resaltada: primero lo que le entrega «se tocan», después lo
        que le tocaría repartiendo.</p>

      <div class="simulador" data-simulador="agregacion-rejilla">
        <h4><i class="fas fa-table-cells-large" aria-hidden="true"></i> El doble conteo, celda a celda</h4>
        <p class="simulador-intro">Los {ac['n']} condados coloreados por sus muertes súbitas, con la rejilla de
          {agn['n_celdas']} rectángulos encima. En naranja, {cc['nombre']}; con borde grueso, las
          {cc['n_celdas_toca']} celdas que toca.</p>
        <div class="simulador-controles"></div>
        <div class="geomapa" data-geomapa="cap1-agregacion"></div>
        <div class="simulador-lectura"></div>
      </div>

      <div class="note">
        <p><strong>La celda que lo dice todo es la del roce.</strong> Una de las
        {cc['n_celdas_toca']} apenas la toca: dentro de ella cae el <strong>{n(cc['roce_pct'])}&nbsp;%</strong> de
        la superficie de {cc['nombre']}, que repartiendo serían <strong>{n(cc['roce_aporte_area'])}</strong>
        muertes. Y «se tocan» le entrega las {cc['sids']} enteras, exactamente igual que a la celda donde el
        condado tiene su núcleo. El predicado no mide cuánto solapa: contesta sí o no.</p>
        <p style="margin-bottom:0;">Y de ahí sale el titular sin aproximar nada. Si \\(k_i\\) es el número de
        celdas que toca el condado \\(i\\) y \\(y_i\\) su conteo, lo que sobra es
        \\(\\sum_i (k_i - 1)\\, y_i\\): cada condado se cuenta una vez de más por cada celda extra en la que cae.
        Esa suma vale <strong>{ent(cc['exceso_total'])}</strong>, que es exactamente
        {ent(agn['total_rectangulos'])} menos {agn['total_condados']}. Y {cc['nombre']}, siendo el que más infla
        de los {ac['n']}, solo pone <strong>{cc['exceso']}</strong> de esos: el
        <strong>{n(cc['pct_del_exceso'])}&nbsp;%</strong>. El destrozo no lo hace un condado raro — lo hacen todos
        a la vez.</p>
      </div>

      <div class="definition">
        <h3>La prueba que separa una agregación buena de una rota</h3>
        <p>Agregar por <em>grupos</em> —todos los municipios de un departamento— asigna cada unidad a exactamente
          un grupo. De ahí sale una propiedad que conviene usar como control de rutina: <strong>la suma de las
          sumas es la suma</strong>. No se pierde nada y no se inventa nada, y la geometría del grupo es la unión
          de las que lo forman.</p>
        <p style="margin-bottom:0;">En cuanto el destino <em>no</em> es una unión de los originales —una rejilla,
          una cuenca, un área metropolitana, una localidad que parte municipios— esa garantía se cae, y hay que
          <strong>repartir</strong> en vez de emparejar. La herramienta se llama <em>interpolación ponderada por
          área</em>: a cada trozo de solape le toca su parte proporcional. Sobre los mismos rectángulos de antes
          devuelve <strong>{n(agn['total_por_area'])}</strong> muertes —el total exacto—, y que lo devuelva no es
          una casualidad: es la comprobación de que está bien hecha.</p>
      </div>

      <p>Con una bifurcación que hay que decir en voz alta, porque es la del módulo 2 otra vez: repartir un
        <em>conteo</em> y repartir una <em>tasa</em> no se hacen igual. Al conteo —extensivo— le toca la parte
        proporcional del origen que lo cede; a la tasa —intensiva— le corresponde un promedio ponderado sobre el
        destino. Pedir la que no era no da error: da un número, y el número es plausible.</p>

      <p><strong>Y ahora lo mismo, aplicado a este capítulo.</strong> La deserción departamental de más arriba —la
        que da I&nbsp;=&nbsp;{n(es['moran_departamental'])}— se calculó promediando las tasas municipales
        <em>sin ponderar</em>: cada municipio pesa lo mismo, tenga quinientos habitantes o dos millones. Es una
        elección legítima, y es una elección. Repartiendo por área sobre los mismos
        {agco['n_departamentos']} departamentos, las dos versiones se parecen —correlacionan
        <strong>{n(agco['cor_reglas'])}</strong>— pero no coinciden: difieren
        <strong>{n(agco['dif_media_abs'])}</strong> puntos de media y
        <strong>{n(agco['dif_max'])}</strong> en el departamento donde más.</p>

      <p>Y el titular de este módulo se mueve con ellas. El I de Moran pasa de
        <strong>{n(agco['moran_sin_ponderar'])}</strong> a <strong>{n(agco['moran_por_area'])}</strong>
        <em>sin que se mueva una sola frontera</em>. La escala no era la única decisión que se toma al agregar:
        también se decide la regla, y esa suele tomarse sin mirar.</p>

      <div class="note">
        <p style="margin-bottom:0;"><strong>Ninguna de las dos es «la buena», y conviene decirlo antes de que
          alguien elija la que le convenga.</strong> Una tasa de deserción se debería ponderar por
          <strong>matrícula</strong>, que es su denominador —lo que el módulo 2 midió sobre Carolina del Norte—, y
          esta base no la trae. Así que entre las dos que sí se pueden calcular no se elige entre lo correcto y lo
          incorrecto: se elige entre dos aproximaciones, y lo honesto es decir cuál se usó.</p>
      </div>

""" + tabs(
    "Agregar por predicado y agregar repartiendo",
    """library(sf)

ncp &lt;- st_transform(st_read(system.file("shape/nc.shp", package = "sf"),
                            quiet = TRUE), 2264)
rej &lt;- st_sf(geom = st_make_grid(ncp))    # 10 x 10 rectangulos

# 1) Emparejar por "se tocan", que es el predicado por defecto: cada
#    condado aporta su conteo ENTERO a cada rectangulo que toca.
por_rect &lt;- sum(aggregate(ncp["SID74"], rej, sum)$SID74, na.rm = TRUE)
cat(sprintf("condados = %d | rectangulos = %d\\n", sum(ncp$SID74), por_rect))
#&gt; """ + f"condados = {agn['total_condados']} | rectangulos = {agn['total_rectangulos']}" + """

# 2) Repartir por area. `extensive = TRUE` porque SID74 es un CONTEO: a
#    cada trozo le toca la parte proporcional del condado que lo cede.
#    Si el total no volviera, el reparto estaria mal.
aw &lt;- st_interpolate_aw(ncp["SID74"], rej, extensive = TRUE)
cat(sprintf("repartido por area = %.5f\\n", sum(aw$SID74, na.rm = TRUE)))
#&gt; """ + f"repartido por area = {n(agn['total_por_area'])}",
    """import geopandas as gpd, json
from shapely.geometry import box

ver = json.load(open("precalculo/versiones.json"))
ncp = gpd.read_file(ver["rutas"]["nc_shp"]).to_crs(2264)
x0, y0, x1, y1 = ncp.total_bounds
dx, dy = (x1 - x0) / 10, (y1 - y0) / 10
rej = gpd.GeoDataFrame(geometry=[
    box(x0 + i * dx, y0 + j * dy, x0 + (i + 1) * dx, y0 + (j + 1) * dy)
    for i in range(10) for j in range(10)], crs=ncp.crs)

# 1) El sjoin por "intersects" hace exactamente lo que aggregate() en R.
u = gpd.sjoin(ncp[["SID74", "geometry"]], rej, predicate="intersects")
print(f"condados = {ncp.SID74.sum()} | "
      f"rectangulos = {int(u.groupby('index_right').SID74.sum().sum())}")
#> """ + f"condados = {agn['total_condados']} | rectangulos = {agn['total_rectangulos']}" + """

# 2) geopandas no trae st_interpolate_aw, asi que la formula se escribe a
#    mano — que ademas es la del libro: peso = area del trozo / area del
#    origen, por ser una variable extensiva.
t = gpd.overlay(ncp[["SID74", "geometry"]].assign(a=ncp.geometry.area),
                rej, how="intersection")
print(f"repartido por area = {(t.SID74 * t.geometry.area / t.a).sum():.5f}")
#> """ + f"repartido por area = {n(agn['total_por_area'])}") + tabs(
    "La misma variable a dos escalas",
    """library(sf); library(spdep); source("precalculo/fuentes.R")

mun &lt;- carga_municipios()
ok  &lt;- mun[!is.na(mun$desercion), ]
nb  &lt;- poly2nb(ok, queen = TRUE)
I_mun &lt;- moran.test(ok$desercion, nb2listw(nb, style = "W", zero.policy = TRUE),
                    zero.policy = TRUE)$estimate[["Moran I statistic"]]
cat(sprintf("municipal: n = %d, I = %.5f\\n", nrow(ok), I_mun))
#&gt; """ + f"municipal: n = {es['n_municipal']}, I = {n(es['moran_municipal'])}" + """

# Islas y subgrafos: no son un defecto del dato, son el caso trabajado
# del modulo 9 del capitulo 6.
cat(sprintf("islas = %d, subgrafos = %d, grado medio = %.5f\\n",
            sum(card(nb) == 0), n.comp.nb(nb)$nc, mean(card(nb))))
#&gt; """ + f"islas = {es['islas_municipal']}, subgrafos = {es['subgrafos_municipal']}, "
    f"grado medio = {n(es['grado_municipal'])}",
    """import geopandas as gpd, pandas as pd, numpy as np
from libpysal.weights import Queen

geo = gpd.read_file("datos/procesado/colombia_adm2.gpkg")
atr = pd.read_csv("datos/procesado/municipios_llave.csv", dtype={"divipola": str})
mun = geo.merge(atr, on="shapeID")           # la union va por shapeID
ok = mun.dropna(subset=["desercion"]).reset_index(drop=True)

w = Queen.from_dataframe(ok, use_index=False, silence_warnings=True)
islas = [i for i, v in w.neighbors.items() if not v]
print(f"n = {len(ok)}, islas = {len(islas)}, "
      f"grado medio = {np.mean([len(v) for v in w.neighbors.values()]):.5f}")
#> """ + f"n = {es['n_municipal']}, islas = {es['islas_municipal']}, "
    f"grado medio = {n(es['grado_municipal'])}") + CIERRE


# =====================================================================
# MÓDULO 8 · El ecosistema de R espacial
# =====================================================================
filas_paq = "\n".join(
    f"""          <tr><th scope="row"><code>{p['nombre']}</code></th><td>{p['papel']}</td>
            <td>{p['version']}</td></tr>""" for p in eco["paquetes"])

MOD8 = cabecera(
    8, "El ecosistema de R espacial", "The R-spatial stack",
    "Saber qué paquete resuelve qué pregunta, y por qué el mapa de "
    "paquetes es el mapa de los tres tipos de dato.") + f"""
      <p>El ecosistema parece caótico hasta que se ve que <strong>está organizado por tipo de dato</strong>. Un
        paquete para patrones puntuales, otro para datos de área, otro para geoestadística, y por debajo de todos,
        <code>sf</code>, que es quien sabe leer y proyectar la geometría.</p>

      <p>Antes de la tabla, prueba el árbol: contesta qué es aleatorio en tu dato y adónde te lleva.</p>

      <div class="simulador" data-simulador="arbol-decision">
        <h4><i class="fas fa-code-branch" aria-hidden="true"></i> ¿Qué método necesito?</h4>
        <p class="simulador-intro">Dos preguntas y una respuesta con su capítulo. El recorrido se queda a la vista,
          porque en un árbol de decisión el camino enseña tanto como el destino.</p>
        <div class="arbol">
          <div class="arbol-ruta" role="list" aria-label="Camino recorrido"></div>
          <div class="arbol-cuerpo"></div>
          <button type="button" class="arbol-reiniciar">Empezar de nuevo</button>
        </div>
        <div class="simulador-lectura"></div>
      </div>

      <table>
        <caption>Los paquetes del curso, con la versión exacta con la que se calculó este material.</caption>
        <thead>
          <tr><th scope="col">Paquete</th><th scope="col">Qué resuelve</th><th scope="col">Versión</th></tr>
        </thead>
        <tbody>
{filas_paq}
        </tbody>
      </table>

      <div class="definition">
        <h3>Las tres bibliotecas de sistema, que son la parte que de verdad importa</h3>
        <p>Por debajo de todos los paquetes de R hay tres bibliotecas escritas en C++ que hacen el trabajo pesado, y
          son las mismas que usan QGIS, PostGIS y GeoPandas:</p>
        <ul>
          <li><strong>GDAL {eco['sistema']['GDAL']}</strong> — leer y escribir formatos. Todos: shapefile,
            GeoPackage, GeoJSON, ráster.</li>
          <li><strong>GEOS {eco['sistema']['GEOS']}</strong> — las operaciones geométricas planas: intersecar,
            unir, medir, validar.</li>
          <li><strong>PROJ {eco['sistema']['PROJ']}</strong> — las transformaciones entre sistemas de referencia.
            Es el capítulo 2 entero.</li>
        </ul>
        <p style="margin-bottom:0;">Que R y Python den el mismo resultado en una intersección no es casualidad ni
          suerte: es que están llamando <em>a la misma biblioteca</em>. Y cuando no lo dan —los cuantiles del
          capítulo 3, la I de Moran del módulo 9— es porque el desacuerdo está en la capa de arriba, no en la
          geometría.</p>
      </div>

      <div class="note">
        <p style="margin-bottom:0;"><strong>Este material se calculó con {eco['r_version']}</strong>, y las versiones
          de la tabla están congeladas en <code>precalculo/versiones.json</code>. No es burocracia: los cortes de
          clase, los cuantiles y hasta el trato de las islas cambian entre versiones, y un material que no dice con
          qué se hizo no es reproducible.</p>
      </div>
""" + CIERRE


# =====================================================================
# MÓDULO 9 · Anatomía de un objeto sf
# =====================================================================
disc_nc = next(d for d in D["discrepancias"] if d["id"] == "tipo_geometria_nc")
disc_mor = next(d for d in D["discrepancias"] if d["id"] == "moran_islas")
MOD9 = cabecera(
    9, "Anatomía de un objeto sf", "Inside an sf object",
    "Abrir el objeto por dentro: geometría y atributos en la misma tabla, "
    "las tres clases anidadas, y lo que cuesta cada una.") + f"""
      <p>Un objeto <code>sf</code> es un <code>data.frame</code> con una columna rara. Esa columna guarda la
        geometría, y el resto es una tabla normal, con lo cual todo lo que ya sabes de <code>dplyr</code> sigue
        valiendo. Es la decisión de diseño que hizo que <code>sf</code> se comiera a <code>sp</code>.</p>

      <p>Los {an['nc']['filas']} condados de <code>nc</code> ocupan {ent(an['nc']['bytes_sf'])} bytes en memoria.
        De ellos, <strong>{ent(an['nc']['bytes_geometria'])}</strong> son geometría —el
        <strong>{n(an['nc']['pct_geometria'])}&nbsp;%</strong>— y solo {ent(an['nc']['bytes_atributos'])} son las
        {an['nc']['columnas_atributo']} columnas de atributos. La geometría es cara: {ent(an['nc']['n_vertices'])}
        vértices para {an['nc']['filas']} polígonos.</p>

      <div class="definition">
        <h3>Las tres clases, de dentro afuera</h3>
        <ul>
          <li><code>sfg</code> — <strong>una</strong> geometría suelta, sin CRS. Un punto ocupa
            {an['clases']['sfg_bytes']} bytes: <code>{an['clases']['sfg']}</code>.</li>
          <li><code>sfc</code> — la <strong>columna</strong> de geometrías. Aquí sí vive el CRS, y vive
            <em>una vez</em> para toda la columna, no una por rasgo: <code>{an['clases']['sfc']}</code>.</li>
          <li><code>sf</code> — la <strong>tabla</strong>: la <code>sfc</code> más los atributos.
            <code>{an['clases']['sf']}</code>. Fíjate en que también es un <code>data.frame</code>: por eso
            <code>nrow()</code>, <code>$</code> y <code>merge()</code> funcionan sin más.</li>
        </ul>
        <p style="margin-bottom:0;">Y el <code>ppp</code> de <code>spatstat</code> es otra cosa: los
          {an['ppp']['n']} pinos japoneses ocupan {ent(an['ppp']['bytes'])} bytes e incluyen
          <strong>la ventana de observación</strong> ({an['ppp']['ventana_tipo']}, área
          {n(an['ppp']['ventana_area'])}). Un <code>sf</code> de puntos no sabe cuál es su ventana, y para un patrón
          puntual la ventana es parte del dato — el módulo 2 ya midió lo que cuesta olvidarla.</p>
      </div>

""" + tabs(
    "Abrir el objeto por dentro",
    """library(sf)
nc &lt;- st_read(system.file("shape/nc.shp", package = "sf"), quiet = TRUE)

cat(sprintf("filas = %d, columnas = %d, vertices = %d\\n",
            nrow(nc), ncol(nc), nrow(st_coordinates(nc))))
#&gt; """ + f"filas = {an['nc']['filas']}, columnas = {an['nc']['columnas']}, "
    f"vertices = {an['nc']['n_vertices']}" + """

# El tipo que informa sf es el de la CAPA, no el de cada rasgo.
cat(as.character(unique(st_geometry_type(nc))), "\\n")
#&gt; """ + f"{an['nc']['tipo_geom']}" + """
cat(sprintf("rasgos con mas de una parte: %d de %d\\n",
            sum(lengths(st_geometry(nc)) &gt; 1), nrow(nc)))
#&gt; """ + f"rasgos con mas de una parte: {an['nc']['n_partes_multiples']} de {an['nc']['filas']}",
    """import geopandas as gpd, json

ver = json.load(open("precalculo/versiones.json"))
nc = gpd.read_file(ver["rutas"]["nc_shp"])
print(f"filas = {len(nc)}, columnas = {nc.shape[1]}")
#> """ + f"filas = {an['nc']['filas']}, columnas = {an['nc']['columnas']}" + """

# shapely mira CADA geometria, no la capa: por eso el conteo no coincide
# con el de sf. La geometria es la misma; lo que difiere es que se
# considera "el tipo" de un rasgo.
print(nc.geom_type.value_counts().to_dict())
#> """ + f"{{'Polygon': {disc_nc['valor_r'] - disc_nc['valor_python']}, "
    f"'MultiPolygon': {disc_nc['valor_python']}}}") + f"""
      <div class="warning">
        <h3 style="margin-top:0;">Discrepancia declarada D1 · el tipo de geometría de <code>nc</code></h3>
        <p><strong>{disc_nc['que']}.</strong> <code>sf</code> informa
          <strong>{disc_nc['valor_r']}</strong> MULTIPOLYGON y <code>geopandas</code> informa solo
          <strong>{disc_nc['valor_python']}</strong>. {disc_nc['causa']}</p>
        <p style="margin-bottom:0;">No es un error de ninguno de los dos, y por eso está aquí y no escondido: los
          dos responden a preguntas distintas. Si comparas dos programas y te sale una diferencia, la primera
          pregunta es siempre <em>«¿estamos midiendo lo mismo?»</em>, no <em>«¿cuál está mal?»</em>.</p>
      </div>

      <div class="warning">
        <h3 style="margin-top:0;">Discrepancia declarada D2 · la I de Moran de la deserción</h3>
        <p>La misma variable, el mismo grafo de vecindad, la misma fórmula, y dos números:
          <code>spdep</code> da <strong>{n(disc_mor['valor_r'])}</strong> y <code>esda</code>
          <strong>{n(disc_mor['valor_python'])}</strong>. {disc_mor['causa']}</p>
        <p style="margin-bottom:0;">Se recupera el valor de R multiplicando el de Python por
          \\((n - \\text{{islas}})/n\\). Va al {disc_mor['va_a']}, que es donde el curso decide qué hacer con una
          unidad que no tiene vecinos. Y es la razón de que la pestaña de Python del módulo 3 escriba la fórmula a
          mano en vez de llamar a la función: así el convenio se ve.</p>
      </div>

      <div class="note">
        <p style="margin-bottom:0;"><strong>Las discrepancias se declaran o son errores.</strong> El auditor de este
          capítulo lleva una lista de las diferencias conocidas entre R y Python; si encuentra una que está en la
          lista, la trata como material didáctico, y si encuentra una que no está, <strong>falla</strong>. Que una
          discrepancia documentada y una sin explicar se lean igual sobre un informe es lo que convierte un auditor
          en un adorno.</p>
      </div>
""" + CIERRE


# =====================================================================
# MÓDULO 10 · Dependencia espacial en ciencia de datos
# =====================================================================
# Decisión de Javier del 2026-08-04: aquí se MIDE un caso pequeño y el
# desarrollo se remite al capítulo 10. La frontera está declarada dentro
# del propio JSON (`cv_espacial.frontera`), no solo en el plan, para que no
# se pierda al retomar.
MOD10 = cabecera(
    10, "Dependencia espacial en ciencia de datos", "Spatial leakage",
    "Ver por qué un modelo predictivo con datos espaciales parece mejor de "
    "lo que es, y por qué con esta red de estaciones no queda más remedio "
    "que modelar. Las dos diferencias, medidas sobre dato real.") + f"""
      <p>Este módulo es para quien vaya a usar aprendizaje automático con datos que tienen coordenadas, que hoy es
        casi todo el mundo. La conclusión es incómoda: <strong>la validación cruzada aleatoria miente</strong>, y
        miente hacia arriba.</p>

      <p>El experimento, con las {cv['n']} estaciones del IDEAM: predecir la {cv['variable']} de cada estación a
        partir de sus {cv['k_vecinos']} vecinas más próximas, y evaluar con {cv['n_pliegues']} pliegues de dos
        maneras: repartiendo las estaciones <em>al azar</em>, y repartiéndolas <em>por bloques espaciales</em>.</p>

      <div class="simulador" data-simulador="cv-espacial">
        <h4><i class="fas fa-scissors" aria-hidden="true"></i> Validación cruzada aleatoria contra por bloques</h4>
        <p class="simulador-intro">Mismo modelo, mismo dato, mismos {cv['n_pliegues']} pliegues. Lo único que cambia
          es cómo se reparten.</p>
        <div class="simulador-controles"></div>
        <div class="grafico-wrapper" style="height:240px;">
          <canvas aria-label="RMSE y R cuadrado de la validación cruzada aleatoria frente a la validación por bloques espaciales" role="img"></canvas>
        </div>
        <div class="simulador-lectura"></div>
      </div>

      <table>
        <caption>El mismo modelo evaluado de dos maneras sobre las estaciones del IDEAM.</caption>
        <thead>
          <tr><th scope="col">Reparto de los pliegues</th><th scope="col">RMSE (°C)</th><th scope="col">R²</th></tr>
        </thead>
        <tbody>
          <tr><th scope="row">Aleatorio</th><td>{n(cv['rmse_aleatoria'])}</td><td>{n(cv['r2_aleatoria'])}</td></tr>
          <tr><th scope="row">Por bloques espaciales</th><td>{n(cv['rmse_bloques'])}</td>
            <td>{n(cv['r2_bloques'])}</td></tr>
        </tbody>
      </table>

      <p>El error real es un <strong>{n(cv['inflacion_pct'])}&nbsp;%</strong> mayor que el que anuncia la validación
        aleatoria. Y el R² es la cifra que más duele: pasa de <strong>{n(cv['r2_aleatoria'])}</strong> —un modelo
        que parece explicar dos tercios de la variación— a <strong>{n(cv['r2_bloques'])}</strong>, que es
        <em>negativo</em>: predecir la media global lo haría mejor.</p>

      <div class="definition">
        <h3>Por qué pasa: fuga de información entre entrenamiento y prueba</h3>
        <p>Reparte {cv['n']} estaciones al azar en {cv['n_pliegues']} pliegues. Para casi cada estación del pliegue
          de prueba hay una estación <em>a pocos kilómetros</em> en el de entrenamiento — y a pocos kilómetros la
          temperatura es casi la misma, como midió el correlograma del módulo 3
          (I = {n(tb['ideam']['bandas'][0]['I'])} en la primera banda). El modelo no está prediciendo: está
          <strong>interpolando entre vecinos que ya ha visto</strong>.</p>
        <p style="margin-bottom:0;">Con bloques espaciales, el pliegue de prueba es una <em>región entera</em> que el
          modelo no ha visto. Eso es lo que de verdad pasa cuando se aplica el modelo a una zona nueva, que es para
          lo que suele querer usarse.</p>
      </div>

      <div class="warning">
        <p style="margin-bottom:0;"><strong>Y la advertencia simétrica, que también hay que dar.</strong> La
          validación por bloques no es «la buena» siempre: es la que responde a la pregunta <em>«¿cuánto me fío en
          una zona donde no he medido?»</em>. Si la pregunta fuera <em>«¿cuánto me fío rellenando huecos entre
          estaciones existentes?»</em>, la aleatoria sería la adecuada. Elegir el reparto es declarar a qué pregunta
          se responde, y hacerlo por defecto es responder a la que no era.</p>
      </div>

      <p>Esa advertencia tiene nombre, y conviene ponérselo porque debajo no hay una preferencia de método sino
        <strong>dos marcos de inferencia distintos</strong>. Pebesma y Bivand los separan así:</p>

      <div class="definition">
        <h3>Basado en el diseño y basado en el modelo</h3>
        <ul>
          <li><strong>Basado en el diseño:</strong> lo aleatorio es <em>el muestreo</em>. Exige que el dato venga de
            un muestreo probabilístico, con probabilidades de inclusión conocidas y positivas. A cambio no hace
            falta postular ningún modelo: la media muestral estima la media poblacional, y punto. Y algo que
            sorprende: bajo este marco dos observaciones vecinas <em>no</em> están correlacionadas, porque lo que
            se repite al imaginar otra muestra no son ellas sino los sorteos.</li>
          <li><strong>Basado en el modelo:</strong> lo aleatorio es <em>el proceso</em>. Se supone que lo observado
            es una realización de \\(Z(s)\\) y se postula su estructura de covarianza. No exige saber cómo se
            eligieron las localizaciones — y es el único que permite predecir en un punto concreto.</li>
        </ul>
        <p style="margin-bottom:0;">No compiten: responden a preguntas distintas y ambos pueden ser válidos sobre el
          mismo dato. Lo que no se puede es usar uno y reclamar las garantías del otro.</p>
      </div>

      <p>Y aquí está lo que decide cuál te toca, que no es una preferencia: <strong>la red del IDEAM no se
        muestreó, se ubicó</strong> — donde había cómo llegar y a quién servir. Sin probabilidades de inclusión, el
        marco basado en el diseño sencillamente no está disponible. Se puede medir lo que eso cuesta. Reparte
        Colombia en polígonos de Thiessen, uno por estación: el área de cada polígono es el territorio que esa
        estación representa. Bajo un muestreo de igual probabilidad esas áreas serían parecidas. Van de
        <strong>{n(dm['area_min_km2'], 2)}</strong> a <strong>{ent(dm['area_max_km2'])}</strong> km², una razón de
        <strong>{n(dm['razon_areas'])}</strong>.</p>

      <table>
        <caption>La temperatura media anual de Colombia según se pese cada estación por igual o por el territorio que representa.</caption>
        <thead>
          <tr><th scope="col">Cómo se pesa cada estación</th><th scope="col">Temperatura media (°C)</th>
            <th scope="col">Altitud media (m)</th></tr>
        </thead>
        <tbody>
          <tr><th scope="row">Todas igual (la media muestral)</th><td>{n(dm['t_media_simple'])}</td>
            <td>{n(dm['alt_media_simple'])}</td></tr>
          <tr><th scope="row">Por el territorio que representa</th><td>{n(dm['t_media_area'])}</td>
            <td>{n(dm['alt_media_area'])}</td></tr>
        </tbody>
      </table>

      <p>La brecha es de <strong>{n(dm['brecha_c'])}&nbsp;°C</strong>, y la segunda columna dice por qué. Las
        estaciones están, en promedio, a <strong>{n(dm['alt_media_simple'])}</strong> m, pero el territorio que
        representan está a <strong>{n(dm['alt_media_area'])}</strong> m: la red sobremuestrea la cordillera y deja
        casi vacías la Amazonía y la Orinoquía, que son enormes, bajas y calientes. Promediar las
        {dm['n']} estaciones como si fueran una muestra aleatoria del país no estima la temperatura de Colombia:
        estima la temperatura de donde el IDEAM puso estaciones. El módulo 2 ya lo había dicho sin cifra —«estás
        viendo la cordillera, no el clima»—; esto es la cifra.</p>

      <div class="warning">
        <p style="margin-bottom:0;"><strong>Y ahora el freno, porque la columna de la derecha tampoco es la
          verdad.</strong> Pesar por Thiessen supone que cada estación representa exactamente su territorio más
          próximo, que es una suposición tan discutible como la anterior — solo que menos ingenua. No es «la
          respuesta correcta»: es la prueba de que la media muestral <em>no</em> lo era. Hacerlo bien exige un
          modelo del campo, con su estructura de covarianza, y eso es el kriging del capítulo 9.</p>
      </div>

      <div class="note">
        <p style="margin-bottom:0;"><strong>Dónde sigue esto.</strong> {cv['frontera']} Aquí se mide un caso y se
          deja la frontera dicha, para que ni el capítulo 1 se coma el 10 ni el 10 dé por sabido lo que nadie
          enseñó. Los pliegues de este ejemplo, por cierto, salen muy desiguales —de {cv['tam_pliegue_min']} a
          {cv['tam_pliegue_max']} estaciones— y eso también es material: un bloque espacial no reparte en partes
          iguales, y quien espere pliegues equilibrados va a llevarse una sorpresa.</p>
      </div>
""" + tabs(
    "Pesar cada estación por el territorio que representa",
    """library(sf)

estac &lt;- st_read("datos/procesado/colombia_estaciones_clima.gpkg", quiet = TRUE)
pais  &lt;- st_union(st_read("datos/procesado/colombia_adm1.gpkg", quiet = TRUE))

# Thiessen: cada celda es el territorio mas proximo a una estacion.
vor &lt;- st_collection_extract(
  st_voronoi(st_union(st_geometry(estac)), st_as_sfc(st_bbox(pais))), "POLYGON")
vor &lt;- st_sf(geom = vor)

# OJO: st_voronoi NO devuelve las celdas en el orden de los puntos de
# entrada. Se emparejan por CONTENCION; fiarse del orden pegaria cada
# temperatura al area de otra estacion, y el numero saldria plausible.
vor &lt;- vor[unlist(st_within(st_geometry(estac), st_geometry(vor))), ]
vor$id &lt;- seq_len(nrow(vor))
rec &lt;- suppressWarnings(st_intersection(vor, pais))
a &lt;- rep(NA_real_, nrow(estac))
a[rec$id] &lt;- as.numeric(st_area(rec)) / 1e6

t &lt;- estac$t_media_anual
cat(sprintf("simple = %.5f | ponderada = %.5f | brecha = %.5f\\n",
            mean(t), sum(t * a) / sum(a), sum(t * a) / sum(a) - mean(t)))
#&gt; """ + f"simple = {n(dm['t_media_simple'])} | ponderada = {n(dm['t_media_area'])} | "
    f"brecha = {n(dm['brecha_c'])}",
    """import geopandas as gpd
from shapely.geometry import MultiPoint
from shapely.ops import voronoi_diagram

estac = gpd.read_file("datos/procesado/colombia_estaciones_clima.gpkg")
pais = gpd.read_file("datos/procesado/colombia_adm1.gpkg").geometry.union_all()

cel = gpd.GeoDataFrame(geometry=list(voronoi_diagram(
    MultiPoint(list(estac.geometry)), envelope=pais.envelope).geoms),
    crs=estac.crs)

# El mismo cuidado que en R: emparejar por contencion, no por orden.
emp = gpd.sjoin(estac[["geometry"]], cel.assign(c=range(len(cel))),
                predicate="within")
emp = emp[~emp.index.duplicated(keep="first")].sort_index()
a = cel.geometry.iloc[emp.c.to_numpy()].intersection(pais).area.to_numpy() / 1e6

t = estac.t_media_anual.to_numpy()
print(f"simple = {t.mean():.5f} | ponderada = {(t * a).sum() / a.sum():.5f} | "
      f"brecha = {(t * a).sum() / a.sum() - t.mean():.5f}")
#> """ + f"simple = {n(dm['t_media_simple'])} | ponderada = {n(dm['t_media_area'])} | "
    f"brecha = {n(dm['brecha_c'])}") + CIERRE


# =====================================================================
# MÓDULO 11 · Glosario de notación
# =====================================================================
MOD11 = cabecera(
    11, "Glosario de notación del curso", "Notation",
    "La notación unificada de los diez capítulos, en un sitio, con su "
    "equivalencia en el texto guía y en R.") + f"""
      <p>La estadística espacial junta tres tradiciones que se desarrollaron por separado —procesos puntuales,
        datos de área y geoestadística— y cada una trae su notación. Esta tabla es la del curso: cuando un capítulo
        escriba \\(\\gamma(h)\\) o \\(G_i^*\\), significa lo que aquí dice.</p>

      <div class="glosario-notacion" data-glosario="cap1-notacion"></div>

      <div class="note">
        <p style="margin-bottom:0;">Las columnas <em>Texto guía</em> y <em>En R</em> están para que puedas ir del
          material al libro y del libro al código sin traducir de cabeza. Si un símbolo del curso no está aquí, es
          un descuido: dilo.</p>
      </div>
""" + CIERRE


# =====================================================================
# MÓDULO 12 · Autoevaluación y ejercicios guiados
# =====================================================================
def valor_paso(v):
    """El valor de un paso de solución, formateado SEGÚN SU TIPO.

    Antes esto era `v if isinstance(v, str) else n(v)`, y ese `else` metía
    por el mismo embudo dos cosas distintas: una medida y un conteo. El
    resultado eran tablas que publicaban «359.00000» muertes, «1121.00000»
    municipios y «33.00000» departamentos. No es un problema de precisión
    —los cinco decimales están MEDIDOS, `mide_punto_ciego.py` los defiende—
    sino de tipo: cinco decimales sobre un conteo no comunican precisión,
    comunican que nadie miró.

    El JSON ya trae la distinción hecha: `jsonlite` escribe `359` para un
    entero y `1.611682076` para un doble, así que Python los lee como `int`
    y `float`. Aquí solo hay que dejar de ignorarla.

    UN CASO BORDE, decidido y no barrido: el ejercicio 1 publica un factor
    que vale EXACTAMENTE 1 —quitar la bomba de Broad Street no mueve a las
    muertes que ya tenían otra más cerca—. `jsonlite` lo escribe `1`, así
    que aquí llega como entero y sale «1», no «1.00000». Es lo correcto:
    ese 1 no es una medida que redondeó bonito, es una identidad por
    construcción, y escribirlo sin decimales dice justo eso.
    """
    if isinstance(v, str):
        return v
    if isinstance(v, int):          # conteos: 359 muertes, 1 121 municipios
        return ent(v)
    return n(v)                     # medidas: cinco decimales, como manda D10


def ejercicio(k, e):
    """Un ejercicio guiado, con su pista y su solución calculada.

    Ni el enunciado ni las cifras se escriben aquí: salen de
    `genera_soluciones.R`, que resuelve el ejercicio de verdad en R. Un
    ejercicio cuya solución se escribe de memoria es una solución sin
    verificar delante de un estudiante que se la va a creer.
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
            <button type="button" class="ejercicio-boton" aria-expanded="false" aria-controls="cap1-e{k}-pista">
              <i class="fas fa-lightbulb" aria-hidden="true"></i> Pista <i class="fas fa-chevron-down" aria-hidden="true"></i>
            </button>
            <button type="button" class="ejercicio-boton" aria-expanded="false" aria-controls="cap1-e{k}-sol">
              <i class="fas fa-key" aria-hidden="true"></i> Solución <i class="fas fa-chevron-down" aria-hidden="true"></i>
            </button>
          </div>
          <div class="ejercicio-panel pista" id="cap1-e{k}-pista" hidden>
            <p style="margin:0;">{PISTAS[k - 1]}</p>
          </div>
          <div class="ejercicio-panel solucion" id="cap1-e{k}-sol" hidden>
            <table>
              <caption>Los pasos de la solución, calculados en R por <code>precalculo/genera_soluciones.R</code>.</caption>
              <thead><tr><th scope="col">Paso</th><th scope="col">Valor</th></tr></thead>
              <tbody>
{pasos}
              </tbody>
            </table>
            <p style="margin-bottom:0;">{e['lectura']}</p>
          </div>
        </div>
"""


PISTAS = [
    "No calcules las distancias dos veces: la matriz muerte × bomba ya la tienes. Quitar una bomba es quedarse "
    "con las otras doce columnas y volver a tomar el mínimo por fila. Y separa los dos grupos ANTES de promediar; "
    "si promedias las 578 juntas, el efecto se diluye y no verás nada.",
    "Los dos remuestreos tienen que dar la MISMA media: si no, hay un error en el montaje, no un hallazgo. Lo que "
    "cambia es la anchura. Y para la última parte, no compares los dos intervalos entero contra entero: mira los "
    "dos tramos donde uno llega y el otro no.",
    "El apartado (c) es una pregunta con trampa, y la trampa es buena. Escribe el límite de la fórmula cuando n "
    "crece sin parar, con rho fijo, y mira qué queda.",
    "Agrupa por CERCANÍA, no por departamento: así el efecto que veas será de la escala y no de dónde estén las "
    "fronteras. Y antes de responder «¿cuál es la correlación?», pregúntate si la pregunta está bien planteada.",
]

MOD12 = cabecera(
    12, "Autoevaluación y ejercicios guiados", "Self-assessment",
    "Comprobar que lo del capítulo se sostiene sin mirar, y resolver cuatro "
    "problemas con la solución calculada en R.") + f"""
      <p>Ocho preguntas de los cuatro tipos. Cada opción lleva su propia retroalimentación —también las
        incorrectas—, así que falla a propósito alguna: se aprende más de la explicación de un error que de la
        confirmación de un acierto.</p>

      <div class="quiz" data-quiz="cap1">
        <h4><i class="fas fa-circle-question" aria-hidden="true"></i> Autoevaluación del capítulo 1</h4>
        <p class="text-sm" style="margin-bottom:0;">Ocho preguntas sobre los once módulos anteriores.</p>
        <div class="quiz-progreso" role="presentation"><div class="quiz-progreso-barra"></div></div>
        <div class="quiz-preguntas"></div>
        <div class="quiz-resumen" role="status" hidden></div>
        <div class="quiz-marcador">
          <span class="quiz-conteo"></span>
          <button type="button" class="quiz-reiniciar">Reiniciar</button>
        </div>
      </div>

      <div class="exercise">
        <h4><i class="fas fa-pen-to-square mr-2" aria-hidden="true"></i>Ejercicios propuestos</h4>
        <p class="text-sm" style="margin-bottom:0.5rem;">Intenta cada uno <strong>antes</strong> de abrir nada. La
          pista dice por dónde entrar sin dar la respuesta; la solución trae los pasos con sus cifras, calculadas en
          R por <code>precalculo/genera_soluciones.R</code> y no escritas de memoria.</p>
{ejercicio(1, S['e1'])}{ejercicio(2, S['e2'])}{ejercicio(3, S['e3'])}{ejercicio(4, S['e4'])}
      </div>

      <div class="definition">
        <h3>De dónde sale cada dato de este capítulo</h3>
        <p>Nada de lo que has leído se puede comprobar si no se sabe de dónde viene. Ésta es la procedencia
          completa; la hoja larga, con URL, licencia, huella SHA-256 y fecha de descarga, está en
          <code>precalculo/FUENTES.md</code>.</p>
        <table>
          <caption>Procedencia de los conjuntos de datos del capítulo 1.</caption>
          <thead>
            <tr><th scope="col">Dato</th><th scope="col">n</th><th scope="col">Origen</th>
              <th scope="col">Vía</th></tr>
          </thead>
          <tbody>
            <tr><th scope="row">Muertes y bombas de Soho, 1854</th><td>{sn['n_muertes']} y {sn['n_bombas']}</td>
              <td>John Snow, digitalizado por <strong>Dodson</strong> y <strong>Tobler</strong> (NCGIA, 1992)</td>
              <td><code>HistData</code></td></tr>
            <tr><th scope="row">{pc['japanesepines']['nombre']}</th><td>{pc['japanesepines']['n']}</td>
              <td><strong>{pc['japanesepines']['fuente'].split(', vía')[0]}</strong></td>
              <td><code>spatstat.data</code></td></tr>
            <tr><th scope="row">{pc['redwood']['nombre']}</th><td>{pc['redwood']['n']}</td>
              <td><strong>{pc['redwood']['fuente'].split(', vía')[0]}</strong></td>
              <td><code>spatstat.data</code></td></tr>
            <tr><th scope="row">{pc['cells']['nombre']}</th><td>{pc['cells']['n']}</td>
              <td><strong>{pc['cells']['fuente'].split(', vía')[0]}</strong></td>
              <td><code>spatstat.data</code></td></tr>
            <tr><th scope="row">{ac['nombre']}</th><td>{ac['n']}</td>
              <td><strong>{ac['fuente'].split(', vía')[0]}</strong></td>
              <td><code>sf</code> ({ac['crs_nombre']})</td></tr>
            <tr><th scope="row">{gc['nombre']}</th><td>{gc['n']}</td>
              <td><strong>{gc['fuente'].split(', vía')[0]}</strong></td>
              <td><code>sp</code> (EPSG:{gc['crs_epsg']})</td></tr>
            <tr><th scope="row">{co['puntual']['nombre']}</th><td>{ent(co['puntual']['n'])}</td>
              <td><strong>{co['puntual']['fuente'].split(', v.')[0]}</strong>, v. 12.25, CC BY-SA 4.0</td>
              <td>datos abiertos de Bogotá</td></tr>
            <tr><th scope="row">{co['area']['nombre']}</th><td>{ent(co['area']['n_con_dato'])}</td>
              <td><strong>{co['area']['fuente'].split(',')[0]}</strong>, 2024; geometría del Marco Geoestadístico
                Nacional del DANE vía geoBoundaries (CC BY 4.0)</td>
              <td>datos.gov.co</td></tr>
            <tr><th scope="row">{co['geo']['nombre']}</th><td>{co['geo']['n']}</td>
              <td><strong>{co['geo']['fuente'].split(', vía')[0]}</strong>, normales climatológicas 1991-2020</td>
              <td>datos.gov.co</td></tr>
          </tbody>
        </table>
        <p style="margin-bottom:0;">Una fuente <strong>descartada</strong>, y se dice por qué: las sedes educativas
          nacionales del Ministerio de Educación Nacional traen coordenadas con dos decimales —1,1 km de
          resolución—, y en Bogotá las sedes con coordenada colapsaban en unos pocos cientos de posiciones
          distintas. Eso no es un patrón puntual, es una retícula de redondeo, y las funciones del capítulo 4
          estarían midiendo el redondeo. No se construye material sobre coordenadas que no se sostienen, por
          conveniente que sea el resto de sus campos.</p>
      </div>

      <div class="references">
        <h3><i class="fas fa-book-open mr-2" aria-hidden="true"></i>Lecturas de este capítulo</h3>
        <ul style="margin-bottom:0;">
          <li>Pebesma y Bivand, <em>Spatial Data Science</em>, <strong>caps. 1 y 3</strong> — los tipos de dato y la
            anatomía de <code>sf</code>. Acceso abierto:
            <a href="https://r-spatial.org/book/" target="_blank" rel="noopener">r-spatial.org/book</a>.</li>
          <li>Cressie, <em>Statistics for Spatial Data</em>, <strong>§1.1–1.3</strong> — la clasificación en tres
            tipos y el problema de la realización única. Es la fuente de casi todo este capítulo.</li>
          <li>Baddeley, Rubak y Turner, <em>Spatial Point Patterns</em>, <strong>caps. 3 y 5</strong> — el objeto
            <code>ppp</code>, la ventana y la intensidad.</li>
          <li>Bivand, Pebesma y Gómez-Rubio, <em>Applied Spatial Data Analysis with R</em>,
            <strong>cap. 1</strong> — el ecosistema de paquetes y de dónde viene cada uno.</li>
          <li>Tobler, W. (1970). «A Computer Movie Simulating Urban Growth in the Detroit Region»,
            <em>Economic Geography</em>, 46, 234-240 — la primera ley, en su contexto original, que es más modesto
            de lo que la cita sugiere.</li>
          <li>Moraga, <em>Geospatial Health Data</em> — el caso de Snow y la epidemiología espacial. Acceso abierto:
            <a href="https://www.paulamoraga.com/book-geospatial/" target="_blank" rel="noopener">paulamoraga.com/book-geospatial</a>.</li>
        </ul>
      </div>

      <div class="definition">
        <h3>Lo que viene</h3>
        <p style="margin-bottom:0;">El <a href="capitulo-2-crs-georreferenciacion.html">capítulo 2</a>
        toma el relevo: sistemas de referencia, proyecciones y georreferenciación con
        <code>sf</code>. Ahí se mide lo que cuesta cada equivocación al poner un dato en su
        sitio, que es el paso que todo este capítulo daba por hecho.</p>
      </div>
""" + CIERRE

# El enlace de arriba NO es cosmético. `enlaces()` de audita_texto_base
# está escrita para ARMARSE SOLA en cuanto aparece un hermano publicado
# al lado: mientras el capítulo 1 estuvo solo, declaraba en voz alta que
# no tenía con qué enlazar; en T2.2c apareció el capítulo 2 y la
# comprobación pasó a exigirlo, sin que nadie tuviera que acordarse. Es
# exactamente para lo que se escribió así (ver A.12).

MODULOS = (MOD1 + MOD2 + MOD3 + MOD4 + MOD5 + MOD6 + MOD7 + MOD8 + MOD9
           + MOD10 + MOD11 + MOD12)


# =====================================================================
# El bloque de configuración: courseData + los datos del precálculo
# =====================================================================
# El JSON entero viaja al navegador. Los simuladores y el quiz sacan de
# ahí sus cifras con `n5()`, así que NINGUNA cifra del JavaScript está
# escrita: no puede quedarse vieja cuando el precálculo cambie.
MODULOS_NAV = [
    ("El mapa que cambió la epidemiología", "Snow", "12 min"),
    ("Los tres tipos de dato espacial", "Tres tipos", "14 min"),
    ("La primera ley de Tobler", "Tobler", "10 min"),
    ("Por qué se rompe la inferencia clásica", "Inferencia rota", "12 min"),
    ("Tamaño de muestra efectivo", "n efectivo", "8 min"),
    ("Estacionariedad y una sola realización", "Una realización", "10 min"),
    ("Escala, soporte y agregación", "Escala y MAUP", "14 min"),
    ("El ecosistema de R espacial", "Ecosistema", "8 min"),
    ("Anatomía de un objeto sf", "Anatomía de sf", "8 min"),
    ("Dependencia espacial en ciencia de datos", "CV espacial", "13 min"),
    ("Glosario de notación del curso", "Glosario", "5 min"),
    ("Autoevaluación y ejercicios guiados", "Autoevaluación", "15 min"),
]

_mods = ",\n".join(
    f'        {{ id: {i + 1}, title: "{t}", shortTitle: "{s}", duration: "{d}" }}'
    for i, (t, s, d) in enumerate(MODULOS_NAV))

_sim = {"campos": M["campos"], "realizaciones": M["realizaciones"]}

COURSE_DATA = f"""    const courseData = {{
      title: "Estadística Espacial",
      modules: [
{_mods}
      ]
    }};

    // Las cifras del capítulo, tal como salen de precalculo/genera_cap1.R.
    // Todo lo que el JavaScript publica se lee de aquí con n5(): una cifra
    // escrita a mano en un simulador o en una pregunta es una cifra que se
    // queda vieja en cuanto el precálculo cambia, y nadie lo nota.
    const DATOS_CAP1 = {json.dumps(D, ensure_ascii=False)};
    const SOL_CAP1 = {json.dumps(S, ensure_ascii=False)};
    // Las rejillas simuladas van aparte de los mapas geográficos: no son
    // territorio, y el presupuesto de 120 KB del §4 es de geometría.
    const MAPAS_SIM = {json.dumps(_sim, ensure_ascii=False)};

    const D1 = DATOS_CAP1;
    const n5 = (x, d = 5) => Number(x).toFixed(d);
    const milC = x => Number(x).toLocaleString('es-CO');
"""


# =====================================================================
# Los mapas
# =====================================================================
def geomapa(ident, clave, paleta=None, etiqueta=None, tabla=None, extra=""):
    """Un registro de GEOMAPAS con su fuente como LITERAL.

    El literal no es un capricho: `audita_texto_base.geomapas()` solo puede
    comprobar los cortes, el n declarado y el peso de un mapa cuya fuente
    sea un objeto. Registrarlos todos como función —que es lo cómodo— habría
    dejado esa familia entera del auditor sin nada que mirar, informando en
    verde.
    """
    partes = [f"      fuente: {json.dumps(M[clave], ensure_ascii=False)}"]
    if paleta:
        partes.append(f"      paleta: '{paleta}'")
    if etiqueta:
        partes.append(f"      etiqueta: '{etiqueta}'")
    if extra:
        partes.append(extra)
    if tabla:
        partes.append(tabla)
    return f"    GEOMAPAS['{ident}'] = {{\n" + ",\n".join(partes) + "\n    };\n"


TABLA_CLASES = """      tabla: function (d) {
        const filas = d.valor.map((v, i) => `<tr><th scope="row">${(d.etiquetas || [])[i] || (i + 1)}</th>`
          + `<td>${v.toFixed(5)}</td><td>${d.clase[i]}</td></tr>`).join('');
        return `<table><caption>${d.titulo}: valor y clase de cada unidad.</caption><thead><tr>`
          + `<th scope="col">Unidad</th><th scope="col">${d.leyenda}</th>`
          + `<th scope="col">Clase</th></tr></thead><tbody>${filas}</tbody></table>`;
      }"""

# La tabla de respaldo del mapa del módulo 7. No repite el coropleto —los
# 100 condados y su clase ya los tiene `cap1-nc`—: da lo que el lienzo dice
# con colores y rótulos y nadie más dice, que es el reparto celda a celda.
# Para quien no ve el mapa, ESTA tabla es el mapa, y por eso lleva las dos
# reglas una al lado de la otra: sin la columna de comparación habría que
# recordar la anterior de memoria.
TABLA_AGREGACION = """      tabla: function () {
        const c = D1.agregacion_soporte.nc.condado_caso;
        const filas = c.reparto.map(r => `<tr><th scope="row">fila ${r.fila}, columna ${r.columna}</th>`
          + `<td>${n5(r.fraccion_pct, 4)}</td><td>${c.sids}</td><td>${n5(r.aporte_area, 4)}</td></tr>`).join('');
        return `<table><caption>${c.nombre} toca ${c.n_celdas_toca} de los `
          + `${D1.agregacion_soporte.nc.n_celdas} rectángulos: lo que aporta a cada uno con las dos reglas.`
          + `</caption><thead><tr><th scope="col">Celda</th>`
          + `<th scope="col">% del condado que cae ahí</th>`
          + `<th scope="col">Por «se tocan»</th><th scope="col">Repartiendo por área</th></tr></thead>`
          + `<tbody>${filas}</tbody><tfoot><tr><th scope="row">Total</th>`
          + `<td>${n5(c.fraccion_total_pct, 4)}</td><td>${c.aporte_predicado}</td>`
          + `<td>${c.sids}</td></tr></tfoot></table>`;
      }"""

TABLA_SNOW = """      tabla: function (d) {
        const cuenta = new Array(d.niveles.length).fill(0);
        d.marcas.forEach(m => { cuenta[m - 1]++; });
        const filas = d.niveles.map((nv, i) => `<tr><th scope="row">${nv}</th>`
          + `<td>${cuenta[i]}</td><td>${(100 * cuenta[i] / d.n).toFixed(5)}</td></tr>`).join('');
        return `<table><caption>Muertes por bomba más próxima (n = ${d.n}).</caption><thead><tr>`
          + `<th scope="col">Bomba</th><th scope="col">Muertes</th>`
          + `<th scope="col">% del total</th></tr></thead><tbody>${filas}</tbody></table>`;
      }"""

GEOMAPAS_JS = (
    "    // ----------------------------------------------------------------\n"
    "    // Los mapas del capítulo. La geometría llega cuantizada desde\n"
    "    // precalculo/geo.R y los cortes de clase los calculó `classInt` en R:\n"
    "    // reimplementar Fisher-Jenks o los cuantiles en JS introduciría un\n"
    "    // TERCER convenio de empates junto a los dos del anexo A.2.\n"
    "    // ----------------------------------------------------------------\n"
    + geomapa("cap1-snow", "snow",
              etiqueta=("Mapa de Snow: las 578 muertes por cólera del Soho en 1854, sobre 528 "
                        "segmentos de calle, con las 13 bombas de agua en rombo y la de Broad "
                        "Street resaltada. La tabla de respaldo da las muertes por bomba."),
              extra=("      nombre2: 'bombas de agua',\n"
                     "      get marcaResaltada() { return snowModo === 'broad' ? D1.snow.bomba_broad : null; },\n"
                     "      get lineas() { return snowModo !== 'sinlineas'; }"),
              tabla=TABLA_SNOW)
    # Los pinos salen DOS veces —módulo 2 como caso nulo, módulo 3 en la
    # terna—, y con un solo registro: el motor pinta cada `.geomapa` en su
    # propio lienzo, así que reusar el identificador no duplica los 130
    # enteros de las coordenadas en el JS.
    + geomapa("cap1-pinos", "japanesepines")
    # Secuoyas y células llevaban desde T1.2 calculadas en `genera_cap1.R`,
    # exportadas a cap1_mapas.json y sin dibujarse en ninguna parte,
    # mientras el módulo 2 afirmaba que «el módulo 3 pone tres patrones
    # puntuales uno al lado del otro» y el módulo 3 ponía una tabla. Se
    # registran aquí porque la terna ES el argumento: sin ver los tres, la
    # frase «el ojo no los separa» hay que creérsela. (2026-08-10)
    + geomapa("cap1-secuoyas", "redwood")
    + geomapa("cap1-celulas", "cells")
    + geomapa("cap1-bogota", "bogota")
    + geomapa("cap1-nc", "nc", paleta="verde", tabla=TABLA_CLASES)
    # El mapa del módulo 7. Su `fuente` es un literal como los demás —lo
    # exige `audita_texto_base.geomapas()`, que sobre una función no puede
    # comprobarle cortes, n ni peso— y lo único que cambia con el botón son
    # los ROTULOS de las celdas y el texto accesible, que son opciones. La
    # geometría, el resalte y las clases son las mismas en los dos estados,
    # así que no hay dos mapas: hay uno con dos lecturas.
    + geomapa("cap1-agregacion", "agregacion", paleta="verde",
              extra=("      nombreLineas: 'rectángulos de la rejilla',\n"
                     "      get nombreResaltado() { return AGREG_CASO().nombre; },\n"
                     "      get nombreLineasResaltadas() { return 'celdas que toca'; },\n"
                     "      get etiquetasLineas() { return agregEtiquetas(); },\n"
                     "      get etiqueta() { return agregAlt(); }"),
              tabla=TABLA_AGREGACION)
    + geomapa("cap1-desercion", "desercion", paleta="naranja", tabla=TABLA_CLASES)
    + geomapa("cap1-meuse", "meuse", paleta="naranja")
    + geomapa("cap1-ideam", "ideam", paleta="divergente")
    + """    // Los dos de simulador: su fuente cambia al mover un control, así que
    // es una función. El auditor lo dice en voz alta en vez de darlos por
    // comprobados — sus cortes los verifica audita_cap1.py sobre el JSON.

    // Busca el campo POR SU phi, nunca por su posición: son dos rejillas
    // distintas y emparejarlas por índice ya las descuadró una vez, en
    // silencio. Anexo T1.2.
    function campoDePhi(phi) {
      return MAPAS_SIM.campos.find(c => c.phi === phi);
    }
    GEOMAPAS['cap1-campo'] = {
      fuente: () => campoDePhi(D1.inferencia.rejilla[campoIdx].phi),
      paleta: 'divergente',
      etiqueta: 'Campo gaussiano simulado sobre una retícula de 28 por 28 celdas; el alcance de la correlación se controla con el deslizador.'
    };
    // Y lo mismo con las realizaciones: la fila de cifras manda y el mapa
    // se busca POR SU id. Antes se indexaba `MAPAS_SIM.realizaciones` con
    // el mismo entero que la fila, y las dos listas ni siquiera salían de
    // la misma simulación. Anexo T1.3.
    function realizacionDeId(id) {
      return MAPAS_SIM.realizaciones.find(r => r.id === id);
    }
    GEOMAPAS['cap1-realizacion'] = {
      fuente: () => realizacionDeId(D1.realizaciones_vistas[realIdx].id),
      paleta: 'divergente',
      etiqueta: 'Una de las tres primeras realizaciones del lote de mil, del mismo proceso gaussiano, sobre una retícula de 16 por 16 celdas.'
    };
"""
)


# =====================================================================
# Los simuladores
# =====================================================================
# Ninguno calcula nada pesado: todo viene precalculado en R (D9 del plan).
# Lo que hacen es dejar VER una cifra que ya está medida, que es distinto
# de simularla en el navegador con otro generador y otro convenio.
SIMULADORES_JS = r"""
    // Estado de los mapas que un control cambia. `campoIdx` es SIEMPRE el
    // índice en `inferencia.rejilla`; el mapa se busca por phi. Arranca en
    // 4 —phi = 4— que es el caso del que habla la prosa de debajo.
    let snowModo = 'broad', campoIdx = 4, realIdx = 0, agregModo = 'predicado';

    // ---- El mapa del módulo 7, sus dos lecturas ----------------------
    // Viven aquí arriba y no dentro del simulador porque los tres las
    // necesitan a la vez: el registro del mapa (que las lee en getters), la
    // botonera y la lectura de cifras. Ninguna calcula nada — todos los
    // números salen de `agregacion_soporte.nc.condado_caso`, que es lo que R
    // midió y `audita_cap1.py` rehace en Python.
    function AGREG_CASO() { return D1.agregacion_soporte.nc.condado_caso; }

    // Los rótulos que van DENTRO de cada celda resaltada, en el mismo orden
    // que `lineas_resaltadas` — que es el de `reparto`, y el ensamblador
    // comprueba que sigan siendo el mismo orden. Con «se tocan» las cinco
    // dicen lo mismo, y ver el conteo repetido cinco veces ES la lección.
    function agregEtiquetas() {
      const c = AGREG_CASO();
      return agregModo === 'area'
        ? c.reparto.map(r => n5(r.aporte_area, 2))
        : c.reparto.map(() => String(c.sids));
    }

    function agregAlt() {
      const g = D1.agregacion_soporte.nc, c = g.condado_caso;
      const base = `Los ${D1.area_canonico.n} condados de Carolina del Norte coloreados por sus muertes `
        + `súbitas, con una rejilla de ${g.n_celdas} rectángulos superpuesta. ${c.nombre}, en naranja, `
        + `cae en ${c.n_celdas_toca} celdas, resaltadas con borde grueso`;
      return agregModo === 'area'
        ? `${base}. Cada celda lleva escrito lo que le tocaría repartiendo por área; las `
          + `${c.n_celdas_toca} cifras suman las ${c.sids} muertes del condado.`
        : `${base}. Cada celda lleva escritas las ${c.sids} muertes del condado, enteras: emparejar por `
          + `«se tocan» se las entrega ${c.n_celdas_toca} veces, ${c.aporte_predicado} en total.`;
    }

    // Marcador vertical sobre un eje de categorías: Chart.js no lo dibuja
    // sin el plugin de anotaciones, que no está en el CDN. Inerte mientras
    // nadie ponga `$marcadorX`.
    Chart.register({
      id: 'marcadorX',
      afterDatasetsDraw(chart) {
        const i = chart.$marcadorX;
        if (i === undefined || i === null) return;
        const x = chart.scales.x.getPixelForValue(i);
        const a = chart.chartArea, ctx = chart.ctx;
        ctx.save();
        // Fuera de COLORES_GRAFICO a propósito: los cuatro colores están
        // gastados y un marcador del color de una serie se lee como serie.
        ctx.fillStyle = 'rgba(1, 40, 32, 0.10)';
        ctx.fillRect(x - 10, a.top, 20, a.bottom - a.top);
        ctx.strokeStyle = 'rgba(1, 40, 32, 0.75)';
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.moveTo(x, a.top);
        ctx.lineTo(x, a.bottom);
        ctx.stroke();
        ctx.restore();
      }
    });

    function lectura(raiz, filas) {
      const caja = raiz.querySelector('.simulador-lectura');
      if (!caja) return;
      caja.innerHTML = filas.map(f =>
        `<span class="lectura-item"><span class="lectura-etiqueta">${f[0]}</span>` +
        `<span class="lectura-valor">${f[1]}</span></span>`).join('');
    }

    // `valorInicial` existe porque el estado de dos simuladores vive FUERA
    // de su función —`snowModo` y `realIdx`, arriba— y sobrevive a salir del
    // módulo y volver. Sin él la botonera se redibujaba con el PRIMERO
    // marcado mientras el mapa, la curva y la lectura seguían en el que el
    // estudiante había elegido: dos mandos sobre un mismo estado que pueden
    // discrepar, que es lo que T1.4.e cerró para la leyenda de Chart.js y lo
    // que la verificación de T1.3 encontró aquí. Sin el argumento se comporta
    // como antes, así que las botoneras de estado local no se enteran.
    function botonera(raiz, opciones, alPulsar, valorInicial) {
      const cont = raiz.querySelector('.simulador-controles');
      // Si el valor no está entre las opciones se marca la primera, como
      // hacía siempre: mejor un mando coherente consigo mismo que ninguno.
      const ini = Math.max(0, opciones.findIndex(o => String(o[0]) === String(valorInicial)));
      cont.innerHTML = opciones.map((o, i) =>
        `<button type="button" class="geomapa-boton${i === ini ? ' activo' : ''}" ` +
        `data-v="${o[0]}">${o[1]}</button>`).join('');
      cont.addEventListener('click', e => {
        const b = e.target.closest('.geomapa-boton');
        if (!b) return;
        cont.querySelectorAll('.geomapa-boton').forEach(x => x.classList.remove('activo'));
        b.classList.add('activo');
        alPulsar(b.dataset.v);
      });
    }

    // Deslizador sobre una lista DISCRETA de posiciones medidas; `opciones`
    // tiene la forma de botonera(): [[valor, rótulo]]. No usa
    // `crearControles` —aquella mapea un parámetro continuo y publica el
    // valor crudo, y aquí el valor es una posición y lo que se lee es el
    // phi— pero sí su CSS, `.control-slider`. Anexo T1.2.
    function deslizador(raiz, opciones, etiqueta, iniPos, alCambiar) {
      const cont = raiz.querySelector('.simulador-controles');
      const id = 'ctl-' + Math.random().toString(36).slice(2, 10);
      const caja = document.createElement('div');
      caja.className = 'control-slider';
      // `.simulador-controles` es una rejilla de dos columnas pensada para
      // pares de deslizadores; uno solo se quedaría en la mitad izquierda.
      caja.style.gridColumn = '1 / -1';

      const rotulo = document.createElement('label');
      rotulo.setAttribute('for', id);
      rotulo.append(etiqueta);
      const salida = document.createElement('output');
      rotulo.appendChild(salida);

      const input = document.createElement('input');
      input.type = 'range';
      input.id = id;
      input.min = 0;
      input.max = opciones.length - 1;
      input.step = 1;
      input.value = iniPos;

      const pinta = () => {
        const o = opciones[+input.value];
        salida.textContent = o[1];
        // Sin `aria-valuetext` un lector de pantalla anuncia la POSICIÓN
        // («4 de 7»), no la magnitud que el capítulo enseña.
        input.setAttribute('aria-valuetext', etiqueta + ': ' + o[1]);
      };
      input.addEventListener('input', () => {
        pinta();
        alCambiar(opciones[+input.value][0]);
      });
      pinta();

      caja.appendChild(rotulo);
      caja.appendChild(input);
      cont.appendChild(caja);
    }

    // 1.1 · El mapa de Snow -------------------------------------------
    SIMULADORES['snow-mapa'] = function (raiz) {
      const s = D1.snow;
      const mapa = () => raiz.querySelector('[data-geomapa="cap1-snow"]');
      const pinta = () => { const m = mapa(); if (m && m.__geomapa) m.__geomapa.dibuja(); };
      const lee = () => {
        if (snowModo === 'todas') {
          lectura(raiz, [['bombas', s.n_bombas],
            ['un color por bomba', 'trece categorías: más de las que una paleta cualitativa separa'],
            ['la del centro', 'Broad Street, en rombo naranja']]);
        } else if (snowModo === 'sinlineas') {
          lectura(raiz, [['muertes', s.n_muertes],
            ['sin el fondo', 'la mancha sigue ahí: no la dibujaban las calles']]);
        } else {
          lectura(raiz, [['muertes de la celda de Broad St', `${s.n_mas_cerca_broad} de ${s.n_muertes}`],
            ['porcentaje', n5(s.pct_mas_cerca_broad) + ' %'],
            ['si se repartieran por igual', n5(s.pct_esperado_uniforme) + ' %'],
            ['razón', n5(s.razon_sobre_uniforme) + '×']]);
        }
      };
      botonera(raiz, [['broad', 'Broad Street contra el resto'],
                      ['todas', 'Un color por bomba (13)'],
                      ['sinlineas', 'Sin las calles']],
        v => { snowModo = v; pinta(); lee(); }, snowModo);
      lee();
      return [];
    };

    // 7.1 · El doble conteo, celda a celda -----------------------------
    // El módulo 7 DECÍA el mecanismo y no lo mostraba. Esto lo muestra: el
    // mismo mapa bajo las dos reglas, con lo que el condado aporta escrito
    // dentro de cada celda que toca. El botón no cambia de mapa —la
    // geometría, el resalte y las clases son las mismas—: cambia lo que las
    // cinco celdas dicen, que es justo lo que separa una regla de la otra.
    SIMULADORES['agregacion-rejilla'] = function (raiz) {
      const g = D1.agregacion_soporte.nc, c = AGREG_CASO();
      const mapa = () => raiz.querySelector('[data-geomapa="cap1-agregacion"]');
      const pinta = () => { const m = mapa(); if (m && m.__geomapa) m.__geomapa.dibuja(); };
      // OJO CON LA REDACCIÓN, y no es una manía: `lectura()` pega el rótulo
      // y el valor sin separador —`.lectura-etiqueta` no lleva margen en
      // ningún capítulo—, así que un valor que empieza por letra se lee
      // pegado al rótulo («la reglaemparejar por…»). Los de aquí empiezan
      // por una cifra o por una comilla angular, que sí separan. Arreglarlo
      // en el CSS tocaría las lecturas de los tres capítulos publicados, y
      // eso no es de esta tarea.
      const lee = () => {
        if (agregModo === 'area') {
          lectura(raiz, [['la regla', '«repartir por área» — st_interpolate_aw'],
            ['a cada celda', '«su parte», proporcional al área que le cae'],
            [`${c.nombre} aporta`, `${c.sids} en total, que son las que tiene`],
            ['la celda que solo roza', `${n5(c.roce_pct, 4)} % del condado → ${n5(c.roce_aporte_area, 4)} muertes`],
            ['total sobre la rejilla', `${milC(g.total_por_area)}, el exacto`]]);
        } else {
          lectura(raiz, [['la regla', '«se tocan» — st_intersects'],
            ['a cada celda', `${c.sids}: el conteo entero del condado`],
            [`${c.nombre} aporta`, `${c.sids} × ${c.n_celdas_toca} = ${c.aporte_predicado}`],
            ['de más, solo él', `${c.exceso} muertes, el ${n5(c.pct_del_exceso)} % del exceso`],
            ['total sobre la rejilla', `${milC(g.total_rectangulos)} donde había ${g.total_condados}`]]);
        }
      };
      botonera(raiz, [['predicado', 'Emparejar por «se tocan»'],
                      ['area', 'Repartir por área']],
        v => { agregModo = v; pinta(); lee(); }, agregModo);
      lee();
      return [];
    };

    // 1.2 · La curva del brote ----------------------------------------
    // Diario y acumulado son la MISMA serie leída de dos maneras, y la
    // segunda es la que enseña el argumento del módulo: al llegar al día del
    // mango la curva ya va por el porcentaje que la prosa publica. Se acumula
    // en el navegador —D9 lo autoriza: es una suma— y en % del total, no en
    // casos, para que la marca del mango caiga sobre la cifra publicada en
    // vez de sobre un 516 que habría que dividir de cabeza. Anexo T1.4.
    SIMULADORES['snow-serie'] = function (raiz) {
      const s = D1.snow;
      const canvas = raiz.querySelector('canvas');
      const iMango = s.serie_fecha.indexOf(s.fecha_mango);
      const corto = f => f.slice(5).replace('-', '/');
      const acumPct = v => {
        const total = v.reduce((a, b) => a + b, 0);
        let suma = 0;
        return v.map(x => 100 * (suma += x) / total);
      };
      // Una sola lista manda: de aquí salen el dataset y las dos lecturas,
      // así que no hay dos índices paralelos que puedan descuadrarse.
      const SERIES = [
        { etiqueta: 'Ataques', diario: s.serie_ataques, color: COLORES_GRAFICO.secundario,
          fondo: 'rgba(255,102,0,.12)' },
        { etiqueta: 'Muertes', diario: s.serie_muertes, color: COLORES_GRAFICO.primario,
          fondo: undefined }
      ];
      SERIES.forEach(x => { x.acumulado = acumPct(x.diario); });
      let modo = 'diario';
      const g = crearGraficoLinea(canvas, s.serie_fecha.map(corto),
        SERIES.map(x => ({ label: x.etiqueta, data: x.diario, borderColor: x.color,
          backgroundColor: x.fondo, fill: x.fondo !== undefined, tension: 0.25, pointRadius: 0 })),
        { scales: { y: { title: { display: true, text: 'casos por día' } } } });
      // El día del mango, con el marcador de T1.2. Antes era un dataset de 43
      // valores con UNO no nulo y pointRadius 0: un punto suelto sin vecinos
      // y sin radio no pinta nada, así que la serie existía solo en la
      // leyenda mientras la intro prometía «marcada». Medido: ocultarla
      // cambiaba 0 de 96 425 px del área de trazado. Anexo T1.4.
      g.$marcadorX = iMango;
      // Contrasta lo DIBUJADO contra las cifras que R calculó por su cuenta.
      // En acumulado el anclaje es afiladísimo: la víspera del mango tiene
      // que dar el porcentaje publicado, y una suma corrida un día —el
      // defecto natural de este gráfico— daría otro. En diario comprueba que
      // la serie y el eje no se hayan desalineado.
      const cuadra = () => {
        const mal = [], A = g.data.datasets[0].data, M = g.data.datasets[1].data;
        if (s.serie_fecha[g.$marcadorX] !== s.fecha_mango) {
          mal.push('la banda cae en ' + s.serie_fecha[g.$marcadorX] + ' y el mango se retiró el '
            + s.fecha_mango);
        }
        if (modo === 'acumulado') {
          if (!(Math.abs(A[iMango - 1] - s.pct_ataques_antes_mango) <= 1e-9)) {
            mal.push('la víspera del mango la curva va por ' + A[iMango - 1]
              + ' % y R publica ' + s.pct_ataques_antes_mango + ' %');
          }
          [['ataques', A], ['muertes', M]].forEach(p => {
            if (!(Math.abs(p[1][p[1].length - 1] - 100) <= 1e-9)) {
              mal.push('el acumulado de ' + p[0] + ' termina en ' + p[1][p[1].length - 1] + ' %');
            }
          });
        } else {
          if (A[iMango] !== s.ataques_dia_mango) {
            mal.push('el día del mango la curva pone ' + A[iMango] + ' ataques y R publica '
              + s.ataques_dia_mango);
          }
          if (Math.max.apply(null, A) !== s.ataques_pico) {
            mal.push('el pico dibujado es ' + Math.max.apply(null, A) + ' y R publica '
              + s.ataques_pico);
          }
        }
        if (!mal.length) return true;
        console.error('snow-serie: ' + mal.length + ' descuadre(s) entre lo dibujado y el JSON — '
          + mal.join(' · '));
        return false;
      };
      const pinta = () => {
        SERIES.forEach((x, i) => { g.data.datasets[i].data = x[modo]; });
        g.options.scales.y.title.text = modo === 'acumulado'
          ? '% del total acumulado' : 'casos por día';
        g.options.scales.y.max = modo === 'acumulado' ? 100 : undefined;
        g.update('none');
      };
      const lee = () => {
        const total = s.ataques_antes_mango + s.ataques_desde_mango;
        if (modo === 'acumulado') {
          lectura(raiz, [
            ['ataques hasta la víspera del mango', `${s.ataques_antes_mango} de ${total}`],
            ['o sea, del brote entero', n5(g.data.datasets[0].data[iMango - 1]) + ' %'],
            ['muertes ya acumuladas ese día', n5(g.data.datasets[1].data[iMango]) + ' %'],
            ['ataques desde el mango en adelante', `${s.ataques_desde_mango} de ${total}`]]);
        } else {
          lectura(raiz, [
            ['pico', `${s.fecha_pico}, ${s.ataques_pico} ataques`],
            ['retirada del mango', `${s.fecha_mango}, ${s.ataques_dia_mango} ataques`],
            ['ataques anteriores al mango', n5(s.pct_ataques_antes_mango) + ' %'],
            ['caída ya acumulada ese día', n5(s.caida_hasta_mango_pct) + ' %']]);
        }
      };
      botonera(raiz, [['diario', 'Casos por día'],
                      ['acumulado', 'Acumulado, % del total']],
        v => { modo = v; pinta(); cuadra(); lee(); });
      pinta();
      cuadra();
      lee();
      return [g];
    };

    // 3 · El correlograma ---------------------------------------------
    // Los interruptores están para que la comparación sea del estudiante y
    // no del autor: el módulo afirma que buena parte de la I es altitud y
    // que el permutado no tiene estructura, y ahora las dos cosas se apagan
    // y se encienden. E[I] no lleva interruptor porque es la referencia
    // contra la que se leen las otras tres. Anexo T1.4.
    SIMULADORES['correlograma'] = function (raiz) {
      const t = D1.tobler;
      const canvas = raiz.querySelector('canvas');
      const ejes = t.ideam.bandas.map(b => `${b.d1}–${b.d2}`);
      // Una sola lista manda: de aquí salen el dataset, el interruptor y las
      // filas de la lectura. El rótulo del interruptor ES el de la leyenda,
      // a propósito: el estudiante ve qué trazo apaga cada casilla, y la
      // guarda puede emparejarlos sin una tabla de traducción que se
      // desincronice — que es la clase de defecto de T1.2, no su instancia.
      const SERIES = [
        { clave: 'real', etiqueta: 'Temperatura (dato real)', d: t.ideam,
          color: COLORES_GRAFICO.secundario, dash: [] },
        { clave: 'altitud', etiqueta: 'Residuos tras quitar la altitud', d: t.residuos_altitud,
          color: COLORES_GRAFICO.terciario, dash: [] },
        { clave: 'permutado', etiqueta: 'Permutado al azar (control)', d: t.permutado,
          color: COLORES_GRAFICO.gris, dash: [5, 4] }
      ];
      const ESPERADO = 'E[I] bajo independencia';
      const params = { real: true, altitud: true, permutado: true };
      const g = crearGraficoLinea(canvas, ejes,
        SERIES.map(x => ({ label: x.etiqueta, data: x.d.bandas.map(b => b.I),
          borderColor: x.color, borderDash: x.dash, tension: 0.2, pointRadius: 3 }))
          .concat([{ label: ESPERADO, data: ejes.map(() => t.ideam.esperado),
            borderColor: COLORES_GRAFICO.primario, borderDash: [2, 3], pointRadius: 0 }]),
        { scales: { x: { title: { display: true, text: 'banda de distancia (km)' } },
                    y: { title: { display: true, text: 'I de Moran' } } } });
      const idx = etiqueta => g.data.datasets.findIndex(ds => ds.label === etiqueta);
      // La leyenda de Chart.js también oculta trazos al pulsarla, y sería un
      // segundo mando sobre el mismo estado: pulsarla dejaría la casilla
      // diciendo una cosa y el gráfico otra, que es el defecto de T1.2 vuelto
      // a sembrar. Se redirige al interruptor, que queda como estado único.
      // E[I] no tiene interruptor, así que su leyenda no hace nada.
      const redirige = (ev, item) => {
        const x = SERIES.find(y => y.etiqueta === item.text);
        if (x) casilla(x.etiqueta).querySelector('input').click();
      };
      g.options.plugins.legend.onClick = redirige;
      // El interruptor se busca por su ROTULO en el DOM, no por posición ni
      // por un puntero guardado al crearlo: así la guarda lee lo mismo que
      // ve el estudiante. Una guarda que contrasta el estado interno consigo
      // mismo da verde con el defecto dentro — T1.2.d.
      const casilla = etiqueta => [...raiz.querySelectorAll('.control-interruptor')]
        .find(l => l.textContent.trim() === etiqueta);
      // El emparejamiento rótulo↔serie del JSON, dicho por SEGUNDA VEZ y
      // aparte de SERIES. Contrastar el trazo contra `x.d` sería tautológico
      // —trazo y referencia saldrían de la misma casilla, así que darían
      // verde con la serie cambiada dentro—, que es exactamente lo que le
      // pasó a la primera guarda de T1.2. Dos afirmaciones independientes
      // que tienen que coincidir. Anexo T1.4.
      const DEBE = { 'Temperatura (dato real)': t.ideam,
                     'Residuos tras quitar la altitud': t.residuos_altitud,
                     'Permutado al azar (control)': t.permutado };
      const cuadra = () => {
        const mal = [];
        Object.keys(DEBE).forEach(etiqueta => {
          const c = casilla(etiqueta), i = idx(etiqueta);
          if (!c || i < 0) { mal.push('falta el interruptor o el trazo de «' + etiqueta + '»'); return; }
          // `isDatasetVisible` es el veredicto del propio Chart.js sobre si
          // ese trazo se dibuja, no la propiedad que acabamos de escribir.
          const marcada = c.querySelector('input').checked, visible = g.isDatasetVisible(i);
          if (marcada !== visible) {
            mal.push('«' + etiqueta + '» está ' + (marcada ? 'marcada y no se dibuja'
              : 'sin marcar y se dibuja'));
          }
          const json = DEBE[etiqueta].bandas.map(b => b.I);
          const dib = g.data.datasets[i].data;
          if (dib.length !== json.length || dib.some((v, k) => v !== json[k])) {
            mal.push('«' + etiqueta + '» dibuja ' + dib[0] + ' en la primera banda y su serie del '
              + 'JSON trae ' + json[0]);
          }
        });
        const e = idx(ESPERADO);
        if (e < 0 || !g.isDatasetVisible(e)) {
          mal.push(ESPERADO + ' no se dibuja, y es la referencia de las otras tres');
        }
        // Que el redirigido de arriba haya LLEGADO a la leyenda. Chart.js
        // resuelve las opciones de sus plugins aparte de `chart.options`, y
        // asignar el manejador solo surte efecto tras un update —el
        // `update('none')` de `pinta()` basta, medido—. La guarda está
        // porque esa cadena es interna de Chart.js: si un día deja de
        // propagarse, la leyenda vuelve a ocultar trazos por su cuenta y las
        // casillas se quedan mintiendo sin que nadie avise. Anexo T1.4.
        if (g.legend.options.onClick !== redirige) {
          mal.push('la leyenda no está redirigida al interruptor: puede ocultar un trazo por su '
            + 'cuenta y dejar la casilla diciendo otra cosa');
        }
        if (!mal.length) return true;
        console.error('correlograma: ' + mal.length + ' descuadre(s) entre los interruptores y '
          + 'lo dibujado — ' + mal.join(' · '));
        return false;
      };
      const pinta = () => {
        SERIES.forEach(x => g.setDatasetVisibility(idx(x.etiqueta), params[x.clave]));
        g.update('none');
      };
      const lee = () => {
        const u = t.ideam.bandas.length - 1;
        const filas = [[ESPERADO, n5(t.ideam.esperado, 6)]];
        if (params.real) {
          filas.push(['primera banda, dato real', n5(t.ideam.bandas[0].I)],
            ['última banda, dato real', n5(t.ideam.bandas[u].I)]);
        }
        if (params.altitud) filas.push(['primera banda, sin la altitud',
          n5(t.residuos_altitud.bandas[0].I)]);
        // Solo con las dos encendidas: es una comparación entre ellas, y
        // enseñarla con una apagada sería publicar la conclusión de un
        // contraste que el estudiante no tiene delante.
        if (params.real && params.altitud) filas.push(['cuánto de la I era altitud',
          n5(t.caida_por_altitud_pct) + ' %']);
        if (params.permutado) filas.push(['primera banda, permutado',
          n5(t.permutado.bandas[0].I)]);
        lectura(raiz, filas);
      };
      crearInterruptores(raiz.querySelector('.simulador-controles'),
        SERIES.map(x => ({ clave: x.clave, etiqueta: x.etiqueta })), params,
        () => { pinta(); cuadra(); lee(); });
      pinta();
      cuadra();
      lee();
      return [g];
    };

    // 4 · El error estándar ingenuo -----------------------------------
    SIMULADORES['ee-ingenuo'] = function (raiz) {
      const r = D1.inferencia.rejilla;
      const canvas = raiz.querySelector('canvas');
      const ejes = r.map(f => f.phi);
      const g = crearGraficoLinea(canvas, ejes, [
        { label: 'e.e. que se calcularía (ingenuo)', data: r.map(f => f.ee_ingenuo),
          borderColor: COLORES_GRAFICO.gris, tension: 0.2, pointRadius: 3 },
        { label: 'e.e. real', data: r.map(f => f.ee_real),
          borderColor: COLORES_GRAFICO.secundario, tension: 0.2, pointRadius: 3 },
        { label: 'cobertura del IC al 95 %', data: r.map(f => f.cobertura),
          borderColor: COLORES_GRAFICO.terciario, tension: 0.2, pointRadius: 3, yAxisID: 'y2' },
        { label: '0,95 prometido', data: r.map(() => 0.95), borderColor: COLORES_GRAFICO.primario,
          borderDash: [2, 3], pointRadius: 0, yAxisID: 'y2' }
      ], { scales: { x: { title: { display: true, text: 'alcance de la correlación, phi' } },
                     y: { title: { display: true, text: 'error estándar' } },
                     y2: { position: 'right', min: 0, max: 1, grid: { display: false },
                           title: { display: true, text: 'cobertura' } } } });
      // La única guarda posible contra un descuadre que solo existe en
      // tiempo de ejecución. `campo` DEBE salir de la misma `fuente()` que
      // invoca el motor: buscarlo aquí por phi la vuelve tautológica —así
      // estaba escrita, y dio verde con el defecto dentro—. Y se llama
      // ANTES de repintar: con el campo ausente, `dibuja()` lanza dentro
      // del motor y se lleva por delante el resto del manejador, que es
      // como el quinto botón se congelaba en silencio. Tolerancia 1e-6: el
      // JSON de mapas redondea a ocho decimales y el de cifras trae diez, y
      // dos alcances vecinos distan 0.10. Anexo T1.2.
      const cuadra = () => {
        const f = r[campoIdx], campo = GEOMAPAS['cap1-campo'].fuente();
        if (campo && Math.abs(campo.rho_vecino - f.rho_vecino) <= 1e-6) return true;
        console.error('ee-ingenuo: el campo dibujado no es el de la lectura. '
          + 'La fila dice phi = ' + f.phi + ' y el campo '
          + (campo ? 'phi = ' + campo.phi : 'no existe'));
        return false;
      };
      const lee = () => {
        const f = r[campoIdx];
        lectura(raiz, [['phi', f.phi],
          ['correlación entre vecinos', n5(f.rho_vecino)],
          ['e.e. ingenuo', n5(f.ee_ingenuo)], ['e.e. real', n5(f.ee_real)],
          ['factor', n5(f.factor)],
          // Los dos cocientes de T2.2, juntos y con nombre distinto: la
          // brecha entre ellos crece con phi, y verla moverse es el
          // argumento del recuadro de arriba.
          ['la varianza declarada se queda corta', n5(f.inflacion_varianza) + ' veces'],
          ['efecto de diseño (varianza real / independiente)', n5(f.efecto_diseno) + ' veces'],
          ['cobertura del IC al 95 %', n5(f.cobertura) + ' ± ' + n5(f.emc_cobertura)],
          ['de las ' + D1.inferencia.n + ' celdas, informan', n5(f.n_eff)]]);
      };
      // El marcador dice DÓNDE estás sobre unas curvas que no se mueven: el
      // alcance ya es el eje horizontal. La cuarta serie —la recta del
      // 0,95— no lleva punto que marcar.
      const pinta = () => {
        g.$marcadorX = campoIdx;
        g.data.datasets.slice(0, 3).forEach(ds => {
          ds.pointRadius = ejes.map((_, i) => i === campoIdx ? 7 : 3);
        });
        g.update('none');
      };
      // Las posiciones del control se DERIVAN de la intersección de las dos
      // rejillas, no se escriben: si R exporta o quita un campo, el control
      // se ajusta solo y nunca ofrece una posición sin campo detrás.
      const conCampo = r.map((f, i) => [i, 'phi = ' + f.phi])
                        .filter(p => campoDePhi(r[p[0]].phi));
      // El control manda sobre el estado, y no al revés: si el arranque
      // cayera en un alcance sin campo, `findIndex` daría −1, el <input> lo
      // redondearía a 0 y volveríamos a tener dos índices discrepando.
      const ini = Math.max(0, conCampo.findIndex(p => p[0] === campoIdx));
      campoIdx = conCampo[ini][0];
      deslizador(raiz, conCampo, 'alcance de la correlación', ini, v => {
          campoIdx = v;
          const m = raiz.querySelector('[data-geomapa="cap1-campo"]');
          if (cuadra() && m && m.__geomapa) m.__geomapa.dibuja();
          lee();
          pinta();
        });
      cuadra();
      lee();
      pinta();
      return [g];
    };

    // 5 · El tamaño efectivo ------------------------------------------
    // El eje x es n y rho va al deslizador, al contrario que antes: con rho
    // en el eje no hay nada que redibujar y el techo 1/rho no puede moverse.
    // Anexo T1.1.
    SIMULADORES['n-efectivo'] = function (raiz) {
      const ne = D1.n_efectivo;
      const canvas = raiz.querySelector('canvas');
      // El único cómputo que este capítulo hace en el navegador, y D9 lo
      // autoriza por escrito: n/(1+(n-1)rho) es aritmética cerrada. Que su
      // resultado sea el de R lo demuestra `cuadra()`, no la buena fe.
      const nEff = (n, rho) => n / (1 + (n - 1) * rho);
      // Tope del deslizador. La guarda de salida del ensamblador lee ESTA
      // línea y exige que sea un rho de la rejilla, para que los dos
      // extremos del control sean cifras que R audita.
      const RHO_MAX = 0.3;
      const ULT = ne.enes.length - 1;
      // Los extremos del eje se DERIVAN del dato: si mañana cambian los enes
      // o el n de Colombia, el rombo no se sale del lienzo en silencio.
      const XMIN = Math.floor(ne.enes[0] * 0.8);
      const XMAX = Math.ceil(Math.max(ne.enes[ULT], ne.desercion_n) * 1.2);
      // La rejilla del trazo lleva dentro los enes de R: por eso la curva
      // pasa por las anclas y `cuadra()` puede compararlas una a una.
      const EJE = [...new Set([...ne.enes, ne.desercion_n, XMIN, XMAX,
        ...Array.from({ length: 48 }, (_, j) =>
          Math.round(XMIN * Math.pow(XMAX / XMIN, j / 47)))])].sort((a, b) => a - b);
      // Millares con el espacio fino de la casa: «1,000» se lee como uno en
      // español, y el eje de este gráfico es justo el tamaño de muestra.
      const mil = v => String(v).replace(/\B(?=(\d{3})+$)/g, '\u202f');
      // Los ticks del eje x SON los enes de R, no los que elija Chart.js: el
      // estudiante ve la rejilla publicada y no una escala paralela.
      const fijos = lista => ({
        afterBuildTicks: a => { a.ticks = lista.map(value => ({ value })); },
        ticks: { callback: mil, autoSkip: false }
      });
      const DIEZ = [];
      for (let p = 1; p <= XMAX; p *= 10) DIEZ.push(p);
      const params = { rho: ne.rhos[1] };
      // T2.1. Las dos curvas de referencia que contestan «¿de dónde sale el
      // 64.52155?». La del rho IMPLÍCITO pasa por el rombo por construcción
      // —ese rho se despeja de ahí— y la del ESTIMADO no pasa: la distancia
      // entre las dos ES la advertencia del módulo sobre la equicorrelación,
      // dibujada en vez de escrita. Se quedan fijas; la que se mueve sigue
      // siendo la del deslizador.
      const rt = ne.rho_del_titular;
      const curva = rho => EJE.map(n => ({ x: n, y: nEff(n, rho) }));
      // Por referencia y no por índice: `cuadra()` leía `datasets[0]` y
      // `datasets[3]` a mano, y meter series nuevas entre ellas era
      // exactamente el descuadre silencioso de T1.2. Ahora cada serie tiene
      // nombre en el código.
      const dsMovil = { label: 'n efectivo con este rho', data: [], borderWidth: 2.5,
          borderColor: COLORES_GRAFICO.secundario, pointRadius: 0 };
      const dsTecho = { label: 'techo 1/rho', data: [], borderColor: '#111',
          borderDash: [3, 3], pointRadius: 0 };
      const dsImpl = { label: 'el rho que implica el dato (' + n5(rt.implicito) + ')',
          data: curva(rt.implicito), borderColor: COLORES_GRAFICO.terciario,
          borderWidth: 1.5, pointRadius: 0 };
      const dsEst = { label: 'el rho medido en el mapa (' + n5(rt.estimado) + ')',
          data: curva(rt.estimado), borderColor: COLORES_GRAFICO.primario,
          borderWidth: 1.5, borderDash: [2, 2], pointRadius: 0 };
      const dsRombo = { label: 'Colombia (' + mil(ne.desercion_n) + ')',
          data: [{ x: ne.desercion_n, y: ne.desercion_municipal }],
          borderColor: COLORES_GRAFICO.terciario,
          backgroundColor: COLORES_GRAFICO.terciario,
          showLine: false, pointStyle: 'rectRot', pointRadius: 8 };
      const g = crearGraficoLinea(canvas, [], [
        dsMovil, dsTecho,
        { label: 'sin correlación', borderColor: COLORES_GRAFICO.gris,
          data: [{ x: XMIN, y: XMIN }, { x: XMAX, y: XMAX }],
          borderDash: [6, 4], pointRadius: 0 },
        dsImpl, dsEst, dsRombo
      ], { scales: {
        x: Object.assign({ type: 'logarithmic', min: XMIN, max: XMAX,
          title: { display: true, text: 'observaciones, n' } }, fijos(ne.enes)),
        y: Object.assign({ type: 'logarithmic', min: 1, max: XMAX,
          title: { display: true, text: 'n efectivo' } }, fijos(DIEZ)) } });
      // La guarda que hacía falta desde que el navegador EVALÚA la fórmula:
      // que su curva pase por la rejilla que R calculó aparte. Lee
      // `datasets[0].data` —lo que el gráfico tiene dentro— y no una segunda
      // evaluación propia: en T1.2 una guarda que recalculaba por su cuenta
      // dio verde con el defecto dentro. Tolerancia 1e-9: R redondea a diez
      // decimales, así que la diferencia legítima no pasa de 5e-11, y entre
      // dos celdas vecinas de la rejilla hay unidades. Anexo T1.1.
      const cuadra = () => {
        const y = new Map(dsMovil.data.map(p => [p.x, p.y]));
        const col = dsRombo.data[0];
        const mal = [];
        if (col.x !== ne.desercion_n || col.y !== ne.desercion_municipal) {
          mal.push('el rombo dibuja (' + col.x + ', ' + col.y + ') y el JSON dice ('
            + ne.desercion_n + ', ' + ne.desercion_municipal + ')');
        }
        // T2.1: que la curva del rho implícito PASE por el rombo, leída de lo
        // dibujado y no recalculada aparte. Es la afirmación que el módulo
        // estrena —«este rho es el que explica ese punto»— y la única forma de
        // que no se quede en promesa. Tolerancia 1e-6: el rho del JSON viene
        // redondeado a diez decimales y el punto está sobre 64.
        const yImpl = dsImpl.data.find(p => p.x === ne.desercion_n);
        if (!yImpl || Math.abs(yImpl.y - ne.desercion_municipal) > 1e-6) {
          mal.push('la curva del rho implícito pasa por '
            + (yImpl ? yImpl.y : 'ningún punto en n = ' + ne.desercion_n)
            + ' y el rombo está en ' + ne.desercion_municipal);
        }
        // Y que la del estimado NO pase: si algún día coincidieran, la prosa
        // que habla de su discrepancia habría dejado de ser cierta.
        const yEst = dsEst.data.find(p => p.x === ne.desercion_n);
        if (yEst && Math.abs(yEst.y - ne.desercion_municipal) <= 1e-6) {
          mal.push('la curva del rho estimado pasa también por el rombo: el módulo '
            + 'publica una discrepancia que ya no existe');
        }
        const k = ne.rhos.indexOf(params.rho);
        if (k >= 0) {
          ne.rejilla.forEach(f => {
            if (!(Math.abs(y.get(f.n) - f.n_eff[k]) <= 1e-9)) {
              mal.push('en n = ' + f.n + ' con rho = ' + params.rho + ' la curva pone '
                + y.get(f.n) + ' y R publica ' + f.n_eff[k]);
            }
          });
        }
        if (!mal.length) return true;
        console.error('n-efectivo: ' + mal.length + ' descuadre(s) entre lo dibujado '
          + 'y la rejilla de R — ' + mal.join(' · '));
        return false;
      };
      const pinta = () => {
        dsMovil.data = curva(params.rho);
        // Sin correlación no hay techo, y dibujarlo en el infinito sería
        // peor que no dibujarlo.
        dsTecho.data = params.rho > 0
          ? [{ x: XMIN, y: 1 / params.rho }, { x: XMAX, y: 1 / params.rho }] : [];
        g.update('none');
      };
      const lee = () => {
        const r = params.rho, n0 = ne.enes[0], n1 = ne.enes[ULT];
        lectura(raiz, [
          ['rho', r.toFixed(3)],
          ['techo 1/rho', r > 0 ? n5(1 / r) : 'sin correlación no hay techo'],
          ['n = ' + mil(n0) + ' informan como', n5(nEff(n0, r))],
          ['n = ' + mil(n1) + ' informan como', n5(nEff(n1, r))],
          ['lo que aporta pasar de uno a otro', n5(nEff(n1, r) - nEff(n0, r))],
          ['Colombia: ' + mil(ne.desercion_n) + ' municipios valen', n5(ne.desercion_municipal)],
          ['con este rho valdrían', n5(nEff(ne.desercion_n, r))],
          ['el rho que implica ese 64.52155', n5(rt.implicito)],
          ['el rho medido en el mapa', n5(rt.estimado)],
          ['con el medido valdrían', n5(rt.n_eff_con_estimado)]]);
      };
      // Sí se usa `crearControles`, la fábrica de la plantilla que T1.2
      // descartó: allí el valor del control era una posición y había que
      // repintar el <output> a mano; aquí el valor ES rho, que es lo que hay
      // que leer. Arranca en rho = 0.01, el caso del que habla la prosa.
      // `cuadra()` va DESPUÉS de `pinta()` —al revés que en T1.2— porque
      // aquí lo que comprueba es lo ya dibujado, y nada puede lanzar.
      crearControles(raiz.querySelector('.simulador-controles'),
        [{ clave: 'rho', etiqueta: 'correlación rho', min: 0, max: RHO_MAX,
           paso: 0.001, decimales: 3 }],
        params, () => { pinta(); cuadra(); lee(); }
      // La rejilla de `.simulador-controles` es de dos columnas, pensada
      // para pares de deslizadores; uno solo se quedaría en la mitad.
      ).rho.parentElement.style.gridColumn = '1 / -1';
      pinta();
      cuadra();
      lee();
      return [g];
    };

    // 6 · Una realización ---------------------------------------------
    // El botón movía el mapa y dejaba la curva quieta, así que la tesis del
    // módulo —de una realización no se sabe si lo que ves es el proceso o
    // el azar— se afirmaba en vez de demostrarse. Peor: la curva no era la
    // de ninguno de los tres mapas. Eran dos simulaciones distintas, de
    // rejilla y semilla distintas, emparejadas por el índice. Ahora los
    // tres mapas SON tres de las mil que hacen la banda. Anexo T1.3.
    SIMULADORES['una-realizacion'] = function (raiz) {
      const u = D1.una_realizacion, v = u.variograma;
      const VISTAS = D1.realizaciones_vistas;
      // `realIdx` sobrevive a salir del módulo y volver (hallazgo 4), así que
      // puede llegar aquí de una visita anterior. Si R publicara menos
      // realizaciones que entonces quedaría fuera de rango y el simulador
      // reventaría al construirse, con el módulo entero en blanco.
      if (!(realIdx >= 0 && realIdx < VISTAS.length)) realIdx = 0;
      const canvas = raiz.querySelector('canvas');
      // Por referencia y no por posición en `datasets`: añadir una serie
      // encima movería un índice escrito a mano y la curva que se actualiza
      // pasaría a ser otra, en silencio.
      const dsUna = { label: 'una realización', data: VISTAS[realIdx].variograma,
                      borderColor: COLORES_GRAFICO.secundario, pointRadius: 3 };
      const g = crearGraficoLinea(canvas, v.lags.map(String), [
        { label: 'teórico', data: v.teorico, borderColor: COLORES_GRAFICO.primario,
          borderDash: [4, 3], pointRadius: 0 },
        { label: 'media de ' + u.n_realizaciones + ' realizaciones', data: v.media,
          borderColor: COLORES_GRAFICO.terciario, pointRadius: 2 },
        dsUna,
        { label: 'banda 5 %–95 %', data: v.q05, borderColor: 'rgba(148,163,184,.5)',
          pointRadius: 0, fill: '+1' },
        { label: '', data: v.q95, borderColor: 'rgba(148,163,184,.5)', pointRadius: 0 }
      ], { scales: { x: { title: { display: true, text: 'rezago' } },
                     y: { title: { display: true, text: 'semivarianza' } } } });
      // Guarda de ejecución, y la única capaz de ver este descuadre: las
      // cifras del JSON eran correctas y la prosa también: lo que estaba mal
      // era el cableado, y eso solo existe cuando el navegador ya dibujó.
      //
      // `mapa` se pide a la MISMA `fuente()` que invoca el motor —buscarlo
      // aquí por su cuenta la volvería tautológica, que es como la primera
      // guarda de T1.2 dio verde con el defecto dentro— y se compara por
      // `media_espacial`, que R calcula sobre el vector del mapa, contra
      // `media`, que calcula sobre la matriz de las mil. Dos rutas, una
      // cifra: comparar el `id` consigo mismo no comprobaría nada, porque
      // `fuente()` ya busca por `id`.
      //
      // Lo que esta guarda NO puede ver —que la curva de la fila sea la del
      // campo de ese mapa— lo comprueba `audita_cap1.py` recalculando el
      // variograma desde el `zq` del propio mapa. D9 no deja ajustar un
      // variograma en el navegador, y con razón.
      //
      // Tolerancia 1e-6: cap1_mapas.json guarda ocho cifras significativas
      // y cap1_datos.json diez, mientras las medias de las tres distan 0.09.
      const cuadra = () => {
        const mapa = GEOMAPAS['cap1-realizacion'].fuente(), fila = VISTAS[realIdx];
        if (mapa && fila && Math.abs(mapa.media_espacial - fila.media) <= 1e-6) return true;
        console.error('una-realizacion: el mapa dibujado no es el de la curva. '
          + 'La fila es la realización ' + (fila ? fila.id : '?') + ', de media '
          + (fila ? fila.media : '?') + ', y el mapa '
          + (mapa ? 'tiene media ' + mapa.media_espacial : 'no existe'));
        return false;
      };
      const pinta = () => {
        dsUna.data = VISTAS[realIdx].variograma;
        g.update('none');
      };
      const lee = () => {
        const r = VISTAS[realIdx];
        lectura(raiz, [['realización', r.id],
          ['su media espacial', n5(r.media)], ['la del proceso', u.media_del_proceso],
          ['su sd espacial', n5(r.sd)],
          ['su variograma se aparta del teórico', n5(r.desvio_rel_max) + ' (rezago ' + r.lag_desvio_max + ')'],
          ['rezagos fuera de la banda', r.lags_fuera_banda + ' de ' + v.lags.length],
          ['sd de las medias sobre ' + u.n_realizaciones, n5(u.sd_de_las_medias)],
          ['engañarían al análisis ingenuo', n5(u.pct_rechaza_ingenuo) + ' %'],
          ['deberían ser', n5(u.pct_esperado_si_valiera) + ' %']]);
      };
      // Los rótulos salen del `id` de cada fila y no de su posición: si R
      // enseñara otras tres, el botón diría cuáles sin tocar esta línea.
      botonera(raiz, VISTAS.map(r => [String(r.id), 'Realización ' + r.id]),
        v2 => {
          // Si el rótulo dejara de corresponder a una fila, `findIndex` daría
          // −1 y el simulador pasaría a leer `VISTAS[-1]`: se queda donde
          // estaba y `cuadra()` lo dice, en vez de romperse en silencio.
          const i = VISTAS.findIndex(r => r.id === +v2);
          if (i >= 0) realIdx = i;
          const m = raiz.querySelector('[data-geomapa="cap1-realizacion"]');
          if (cuadra() && m && m.__geomapa) m.__geomapa.dibuja();
          pinta();
          lee();
        }, VISTAS[realIdx].id);
      cuadra();
      pinta();
      lee();
      return [g];
    };

    // 7 · La agregación ------------------------------------------------
    SIMULADORES['agregacion'] = function (raiz) {
      const a = D1.agregacion, e = D1.escala_correlacion;
      const canvas = raiz.querySelector('canvas');
      let vista = 'sim';
      let g = null;
      const dibuja = () => {
        if (g) { g.destroy(); const i = graficosActivos.indexOf(g); if (i >= 0) graficosActivos.splice(i, 1); }
        if (vista === 'sim') {
          g = crearGraficoLinea(canvas, a.niveles.map(x => x.bloque + '×' + x.bloque), [
            { label: 'correlación', data: a.niveles.map(x => x.corr),
              borderColor: COLORES_GRAFICO.secundario, tension: 0.2, pointRadius: 4 },
            { label: 'base teórica', data: a.niveles.map(() => a.corr_teorica_base),
              borderColor: COLORES_GRAFICO.primario, borderDash: [3, 3], pointRadius: 0 }
          ], { scales: { x: { title: { display: true, text: 'tamaño del bloque agregado' } },
                         y: { min: 0, max: 1, title: { display: true, text: 'correlación' } } } });
          lectura(raiz, [['celdas sueltas', n5(a.corr_base)],
            ['base teórica', a.corr_teorica_base],
            ['bloques de 16×16', n5(a.corr_max)], ['subida', n5(a.subida_pct) + ' %'],
            ['mecanismo', a.mecanismo]]);
        } else {
          g = crearGraficoBarras(canvas, e.pares.map((p, i) => 'par ' + (i + 1)),
            e.pares.map(p => p.cambio_pct),
            { indexAxis: 'y',
              scales: { x: { title: { display: true, text: 'cambio de la correlación al agregar (%)' } } } });
          lectura(raiz, [['pares examinados', e.n_pares], ['suben', e.n_suben],
            ['bajan', e.n_bajan], ['invierten el signo', e.n_invierten],
            ['par principal, municipal', n5(e.principal.r_municipal)],
            ['par principal, departamental', n5(e.principal.r_departamental)]]);
        }
      };
      botonera(raiz, [['sim', 'Simulación controlada'], ['real', 'Los 13 pares reales']],
        v => { vista = v; dibuja(); });
      dibuja();
      return g ? [g] : [];
    };

    // 8 · El árbol de decisión -----------------------------------------
    // No dibuja nada: es marcado. Y la ruta recorrida se queda a la vista,
    // porque en un árbol el camino enseña tanto como el destino.
    SIMULADORES['arbol-decision'] = function (raiz) {
      const A = D1.arbol;
      const caja = raiz.querySelector('.arbol');
      const porId = {};
      A.nodos.forEach(x => { porId[x.id] = x; });
      let actual = A.raiz;
      const ruta = [];

      function pintaRuta() {
        const barra = caja.querySelector('.arbol-ruta');
        barra.innerHTML = ruta.map(p =>
          `<span class="arbol-paso" role="listitem">${p}</span>`).join('');
      }
      function pinta() {
        pintaRuta();
        const cuerpo = caja.querySelector('.arbol-cuerpo');
        const nodo = porId[actual];
        if (nodo) {
          cuerpo.innerHTML =
            `<div class="arbol-pregunta"><h5>${nodo.pregunta}</h5>` +
            `<div class="arbol-opciones">` +
            nodo.opciones.map((o, i) =>
              `<button type="button" class="arbol-opcion" data-i="${i}">${o.texto}</button>`).join('') +
            `</div></div>`;
          cuerpo.querySelectorAll('.arbol-opcion').forEach(b => {
            b.addEventListener('click', () => {
              const o = nodo.opciones[+b.dataset.i];
              ruta.push(o.texto);
              if (porId[o.destino]) { actual = o.destino; pinta(); }
              else { hoja(o); }
            });
          });
        }
      }
      function hoja(o) {
        pintaRuta();
        caja.querySelector('.arbol-cuerpo').innerHTML =
          `<div class="arbol-hoja"><p class="arbol-accion">${o.metodo}</p>` +
          `<p>Se desarrolla en el <strong>capítulo ${o.capitulo}</strong> de este material.</p>` +
          `<p class="arbol-cifras">Ruta: ${ruta.join(' → ')}</p></div>`;
      }
      caja.querySelector('.arbol-reiniciar').addEventListener('click', () => {
        actual = A.raiz; ruta.length = 0; pinta();
      });
      pinta();
      lectura(raiz, [['pregunta que reparte el curso', '¿qué es aleatorio en tu dato?'],
        ['ramas', A.nodos.length - 1], ['destinos', 9]]);
      return [];
    };

    // 10 · La validación cruzada ---------------------------------------
    SIMULADORES['cv-espacial'] = function (raiz) {
      const c = D1.cv_espacial;
      const canvas = raiz.querySelector('canvas');
      let vista = 'rmse';
      let g = null;
      const dibuja = () => {
        if (g) { g.destroy(); const i = graficosActivos.indexOf(g); if (i >= 0) graficosActivos.splice(i, 1); }
        const datos = vista === 'rmse' ? [c.rmse_aleatoria, c.rmse_bloques]
                                       : [c.r2_aleatoria, c.r2_bloques];
        g = crearGraficoBarras(canvas, ['CV aleatoria', 'CV por bloques'], datos,
          { scales: { y: { title: { display: true,
              text: vista === 'rmse' ? 'RMSE (°C)' : 'R²' } } } });
        lectura(raiz, vista === 'rmse'
          ? [['RMSE aleatoria', n5(c.rmse_aleatoria)], ['RMSE por bloques', n5(c.rmse_bloques)],
             ['el error real es mayor en', n5(c.inflacion_pct) + ' %'],
             ['sd de la variable', n5(c.sd_variable)]]
          : [['R² aleatoria', n5(c.r2_aleatoria)], ['R² por bloques', n5(c.r2_bloques)],
             ['lectura', 'negativo: predecir la media global lo haría mejor']]);
      };
      botonera(raiz, [['rmse', 'RMSE'], ['r2', 'R²']], v => { vista = v; dibuja(); });
      dibuja();
      return g ? [g] : [];
    };
"""


# =====================================================================
# Las dos autoevaluaciones
# =====================================================================
# La diagnóstica va al principio del módulo 1 y no cuenta para nada; el
# quiz de ocho, al final. Ninguna cifra está escrita: todas salen de D1.
QUIZ_JS = r"""
    // ----------------------------------------------------------------
    // Diagnóstica de entrada (sin nota). Cierra la pregunta abierta nº 2
    // del plan: va DENTRO del capítulo 1, antes de nada, porque una
    // diagnóstica que se contesta después de leer mide otra cosa.
    // ----------------------------------------------------------------
    AUTOEVALUACIONES['cap1-diagnostica'] = [
      {
        tipo: 'opcion', modulo: 1,
        pregunta: 'Tienes las coordenadas de todos los accidentes de tránsito de una ciudad durante un año. '
          + '¿Qué tipo de dato espacial es?',
        pista: 'Pregúntate qué es lo aleatorio: ¿dónde ocurren, o cuánto vale algo en sitios fijos?',
        opciones: [
          { texto: 'Un patrón puntual: lo aleatorio es dónde ocurren.', correcta: true,
            retro: 'Eso es. Y por eso la pregunta natural será «¿se agrupan más de lo que cabría esperar por azar?», '
              + 'que es el capítulo 4.' },
          { texto: 'Dato de área, porque los accidentes pasan en calles.', correcta: false,
            retro: 'Sería dato de área si contaras accidentes POR barrio. Con las coordenadas sueltas, la '
              + 'localización es el dato. Módulo 2.' },
          { texto: 'Dato geoestadístico: hay un valor en cada punto de la ciudad.', correcta: false,
            retro: 'No hay "cantidad de accidente" en cada esquina esperando a ser medida. Eso sí pasa con la '
              + 'temperatura, y es la diferencia que separa los dos tipos. Módulo 2.' },
          { texto: 'Depende del software que uses.', correcta: false,
            retro: 'El tipo lo pone la pregunta, no la herramienta. El software viene después.' }
        ],
        retroAcierto: 'La pregunta «¿qué es aleatorio?» es la que reparte los diez capítulos.',
        retroFallo: 'Ve al módulo 2: los tres tipos, cada uno con su canónico y su gemelo colombiano.'
      },
      {
        tipo: 'opcion', modulo: 4,
        pregunta: '¿Verdadero o falso? Con datos espaciales correlacionados, el error estándar clásico '
          + '$s/\\sqrt{n}$ sale demasiado PEQUEÑO, y por eso los intervalos de confianza salen más estrechos de '
          + 'lo que deberían.',
        pista: 'Piensa en si dos observaciones vecinas aportan información nueva o información repetida.',
        opciones: [
          { texto: 'Verdadero', correcta: true,
            retro: 'Y el capítulo lo mide: con dato colombiano real el error estándar honesto es '
              + n5(D1.inferencia_real.factor) + ' veces el ingenuo.' },
          { texto: 'Falso', correcta: false,
            retro: 'Observaciones que se parecen aportan menos información de la que su número sugiere, así que '
              + 'la fórmula clásica infla la confianza. Módulo 4.' }
        ],
        retroAcierto: 'Y no es un matiz: la cobertura de un intervalo nominal al 95 % baja a '
          + n5(D1.inferencia.cobertura_phi4) + ' en el ejemplo del módulo 4.',
        retroFallo: 'Módulo 4.'
      },
      {
        tipo: 'opcion', modulo: 5,
        pregunta: 'Tienes 1 000 observaciones con una correlación de 0,10 entre todas las parejas. '
          + '¿A cuántas observaciones independientes equivalen?',
        pista: 'La fórmula es n / (1 + (n-1) rho). Haz la cuenta con la cabeza antes de mirar.',
        opciones: [
          { texto: 'Alrededor de 10', correcta: true,
            retro: 'Exactamente ' + n5(D1.n_efectivo.rejilla[D1.n_efectivo.rejilla.length - 1].n_eff[4])
              + '. Y no es que "pierdas" 990: es que nunca las tuviste.' },
          { texto: 'Alrededor de 900', correcta: false,
            retro: 'Esa sería la intuición de "pierdo un 10 %", y falla por dos órdenes de magnitud. Módulo 5.' },
          { texto: 'Alrededor de 100', correcta: false,
            retro: 'Cerca del techo con rho = 0,01, no con 0,10. Con rho = 0,10 el techo es 10. Módulo 5.' },
          { texto: 'Las 1 000: la correlación no afecta al tamaño de muestra.', correcta: false,
            retro: 'Afecta, y mucho. Ése es justo el módulo 5.' }
        ],
        retroAcierto: 'Y lo importante es el techo: n_eff tiende a 1/rho, así que añadir datos deja de servir.',
        retroFallo: 'Módulo 5. La respuesta corta: hay un techo, y está en 1/rho.'
      },
      {
        tipo: 'multiple', modulo: 7,
        pregunta: 'Calculas la correlación entre dos variables por municipio y luego por departamento. '
          + 'Marca <strong>todo</strong> lo que sea cierto.',
        pista: 'Son dos. Y una de ellas contradice la versión corta que suele contarse.',
        opciones: [
          { texto: 'Las dos cifras pueden ser muy distintas aunque el dato sea el mismo.', correcta: true,
            retro: 'El par principal del capítulo va de ' + n5(D1.escala_correlacion.principal.r_municipal)
              + ' a ' + n5(D1.escala_correlacion.principal.r_departamental) + '.' },
          { texto: 'Agregar no siempre sube la correlación: a veces la baja o le cambia el signo.', correcta: true,
            retro: 'De los ' + D1.escala_correlacion.n_pares + ' pares reales del capítulo, '
              + D1.escala_correlacion.n_suben + ' suben, ' + D1.escala_correlacion.n_bajan + ' bajan y '
              + D1.escala_correlacion.n_invierten + ' invierte el signo.' },
          { texto: 'La cifra departamental es la buena, porque tiene menos ruido.', correcta: false,
            retro: 'Ninguna de las dos es "la buena": responden a preguntas distintas. Módulo 7 y ejercicio 4.' },
          { texto: 'Si difieren, es que una de las dos está mal calculada.', correcta: false,
            retro: 'Las dos pueden estar perfectamente calculadas. Eso es exactamente el MAUP.' }
        ],
        retroAcierto: 'Las dos. La unidad de análisis es una decisión de modelado, no de presentación.',
        retroFallo: 'Las correctas son las dos primeras. Módulo 7.'
      },
      {
        tipo: 'opcion', modulo: 6,
        pregunta: '¿Verdadero o falso? Con una sola realización de un proceso espacial se pueden estimar su media '
          + 'y su covarianza sin ningún supuesto adicional.',
        pista: '¿De dónde saldría la «repetición» que toda estimación necesita?',
        opciones: [
          { texto: 'Falso: hace falta suponer estacionariedad', correcta: true,
            retro: 'Estacionariedad es exactamente suponer que distintas partes del mapa son repeticiones del '
              + 'mismo mecanismo. Sin esa suposición no hay repetición, y sin repetición no hay estimación.' },
          { texto: 'Verdadero: los datos hablan por sí solos', correcta: false,
            retro: 'Es el problema fundamental de la disciplina, no un tecnicismo. Módulo 6.' }
        ],
        retroAcierto: 'Y el precio de suponerla se ve en el módulo 3: una tendencia no declarada —la altitud— se '
          + 'contabiliza como dependencia.',
        retroFallo: 'Módulo 6.'
      },
      {
        tipo: 'opcion', modulo: 10,
        pregunta: 'Entrenas un modelo con datos que tienen coordenadas y lo validas con validación cruzada '
          + 'aleatoria de 10 pliegues. ¿Qué esperas que pase?',
        pista: 'Piensa en qué tan lejos está cada punto de prueba del punto de entrenamiento más próximo.',
        opciones: [
          { texto: 'El desempeño estimado saldrá mejor de lo que el modelo consigue de verdad.', correcta: true,
            retro: 'El capítulo lo mide: el RMSE real es un ' + n5(D1.cv_espacial.inflacion_pct)
              + ' % mayor que el que anuncia la CV aleatoria. Módulo 10.' },
          { texto: 'Saldrá peor, porque los pliegues rompen la estructura espacial.', correcta: false,
            retro: 'Al revés: la CV aleatoria deja vecinos en entrenamiento y prueba, y eso AYUDA al modelo de '
              + 'forma artificial. Módulo 10.' },
          { texto: 'Saldrá igual: la validación cruzada es insensible al tipo de dato.', correcta: false,
            retro: 'El R² del ejemplo pasa de ' + n5(D1.cv_espacial.r2_aleatoria) + ' a '
              + n5(D1.cv_espacial.r2_bloques) + '. No es igual. Módulo 10.' },
          { texto: 'Depende del algoritmo: con árboles no pasa.', correcta: false,
            retro: 'Pasa con cualquier algoritmo. La fuga la pone el reparto de los pliegues, no el modelo.' }
        ],
        retroAcierto: 'Y el remedio no es "usar siempre bloques": es saber a qué pregunta responde cada reparto.',
        retroFallo: 'Módulo 10.'
      },
      {
        tipo: 'opcion', modulo: 9,
        pregunta: '¿Verdadero o falso? Si R y Python dan resultados distintos sobre el mismo dato espacial, uno '
          + 'de los dos tiene necesariamente un error.',
        pista: 'Piensa en si los dos están respondiendo exactamente a la misma pregunta.',
        opciones: [
          { texto: 'Falso: pueden estar midiendo cosas distintas', correcta: true,
            retro: 'Este capítulo publica discrepancias documentadas entre R y Python y ninguna es un error: son '
              + 'convenios distintos. sf dice que los ' + D1.anatomia.nc.filas + ' condados de nc son '
              + 'MULTIPOLYGON y shapely dice que solo ' + D1.anatomia.nc.n_partes_multiples + '.' },
          { texto: 'Verdadero: el mismo cálculo da el mismo número', correcta: false,
            retro: 'Solo si de verdad es el mismo cálculo. La primera pregunta ante una diferencia es «¿estamos '
              + 'midiendo lo mismo?», no «¿cuál está mal?». Módulo 9.' }
        ],
        retroAcierto: 'Y la distinción que importa: una discrepancia DECLARADA es material didáctico; una sin '
          + 'explicar es un fallo.',
        retroFallo: 'Módulo 9.'
      },
      {
        tipo: 'opcion', modulo: 2,
        pregunta: 'Calculas la intensidad de un patrón puntual como n dividido por el área. Cambias la ventana '
          + 'de observación por otra más grande, con casi los mismos puntos dentro. ¿Qué pasa?',
        pista: 'Mira qué hay en el denominador y qué NO aparece en la notación.',
        opciones: [
          { texto: 'La intensidad cambia, y puede cambiar mucho: la ventana es parte del estimador.',
            correcta: true,
            retro: 'Con las sedes de Bogotá el factor es ' + n5(D1.colombia.puntual.factor_lambda)
              + ' según se use el perímetro urbano o el Distrito completo. Módulo 2.' },
          { texto: 'No cambia: la intensidad es una propiedad del patrón.', correcta: false,
            retro: 'Ojalá. El área está en el denominador, así que elegir la ventana es elegir el resultado.' },
          { texto: 'Cambia poco, porque los puntos son casi los mismos.', correcta: false,
            retro: 'Los puntos sí, el área no. En Bogotá las sedes se multiplican por poco más de 1 y el área por '
              + 'mucho más.' },
          { texto: 'Solo cambia si la ventana deja fuera algún punto.', correcta: false,
            retro: 'Cambia igual aunque no deje fuera ninguno: basta con que crezca el área.' }
        ],
        retroAcierto: 'Por eso el material congela LAS DOS ventanas de Bogotá en vez de elegir una en silencio.',
        retroFallo: 'Módulo 2, y el capítulo 4 entero.'
      }
    ];

    // ----------------------------------------------------------------
    // La autoevaluación del capítulo: ocho preguntas de los cuatro tipos.
    // ----------------------------------------------------------------
    AUTOEVALUACIONES['cap1'] = [
      {
        tipo: 'numerica', modulo: 1,
        pregunta: 'De las ' + D1.snow.n_muertes + ' muertes del brote de Soho, ¿qué porcentaje tiene la bomba de '
          + 'Broad Street como la más próxima? Responde con dos decimales.',
        respuesta: Number(n5(D1.snow.pct_mas_cerca_broad, 2)), tolerancia: 0.05,
        pista: 'Está en el módulo 1, y es la cifra que sostiene el mapa entero.',
        retroAcierto: 'Y frente al ' + n5(D1.snow.pct_esperado_uniforme) + ' % que daría un reparto uniforme entre '
          + 'las ' + D1.snow.n_bombas + ' bombas, son ' + n5(D1.snow.razon_sobre_uniforme) + ' veces.',
        retroFallo: 'Son ' + D1.snow.n_mas_cerca_broad + ' de ' + D1.snow.n_muertes + ', o sea el '
          + n5(D1.snow.pct_mas_cerca_broad) + ' %.'
      },
      {
        tipo: 'opcion', modulo: 1,
        pregunta: 'El ' + n5(D1.snow.pct_ataques_antes_mango) + ' % de los ataques ocurrió ANTES de que se '
          + 'retirara el mango de la bomba. ¿Qué se sigue de ahí?',
        pista: 'Ojo con confundir "el brote se apagó después" con "se apagó por eso".',
        opciones: [
          { texto: 'Que el mapa no puede atribuirle a la retirada del mango el final del brote.', correcta: true,
            retro: 'El ' + n5(D1.snow.fecha_mango === null ? 0 : D1.snow.caida_hasta_mango_pct)
              + ' % de la caída ya había ocurrido ese día. Snow tenía razón sobre el agua, pero no por este dato.' },
          { texto: 'Que la retirada del mango fue lo que apagó el brote.', correcta: false,
            retro: 'Es la lectura cómoda, y el dato la contradice: la curva ya venía cayendo. Módulo 1.' },
          { texto: 'Que los datos de Snow están mal digitalizados.', correcta: false,
            retro: 'Están bien: coinciden con los polígonos de Thiessen en '
              + D1.snow.n_coinciden_tobler + ' de ' + D1.snow.n_muertes + '.' },
          { texto: 'Que la teoría del aire viciado era la correcta.', correcta: false,
            retro: 'Nada de esto rehabilita el miasma. Lo que dice es que ESTE dato no prueba lo que se le atribuye.' }
        ],
        retroAcierto: 'El argumento de Snow es geométrico: una concentración alrededor de un punto.',
        retroFallo: 'Módulo 1, la segunda mitad.'
      },
      {
        tipo: 'multiple', modulo: 3,
        pregunta: 'El correlograma de las estaciones del IDEAM da I = ' + n5(D1.tobler.ideam.bandas[0].I)
          + ' en la primera banda. Marca <strong>todo</strong> lo que sea cierto.',
        pista: 'Son dos. Una tiene que ver con el control, la otra con la altitud.',
        opciones: [
          { texto: 'Buena parte de esa dependencia la explica la altitud, no la distancia.', correcta: true,
            retro: 'Al quitarla, la I baja a ' + n5(D1.tobler.residuos_altitud.bandas[0].I) + ': un '
              + n5(D1.tobler.caida_por_altitud_pct) + ' % menos.' },
          { texto: 'Permutando las temperaturas entre las mismas estaciones, la I se desploma.', correcta: true,
            retro: 'Cae a ' + n5(D1.tobler.permutado.bandas[0].I) + '. Ese control es lo que descarta que la '
              + 'estructura la ponga la geometría.' },
          { texto: 'Un valor tan alto solo puede salir de un error de cálculo.', correcta: false,
            retro: 'Es un valor perfectamente normal en un dato climático. Módulo 3.' },
          { texto: 'Como la altitud explica parte, la dependencia espacial desaparece.', correcta: false,
            retro: 'No desaparece: queda ' + n5(D1.tobler.residuos_altitud.bandas[0].I) + ', que sigue siendo '
              + 'mucho. Baja, no se anula.' }
        ],
        retroAcierto: 'Y eso anuncia el capítulo 9: el kriging con deriva externa.',
        retroFallo: 'Las correctas son las dos primeras. Módulo 3.'
      },
      {
        tipo: 'grafico', modulo: 4,
        alto: 210,
        descripcionGrafico: 'Dos curvas frente al alcance de la correlación: el error estándar que se calcularía '
          + 'suponiendo independencia, casi plano, y el error estándar real, que crece sin parar.',
        pregunta: 'Lectura de gráfico. Las dos curvas son el error estándar de la MISMA media sobre el mismo '
          + 'campo simulado. ¿Qué está pasando?',
        pista: 'Fíjate en cuál de las dos casi no se mueve, y pregúntate por qué no se entera de nada.',
        dibujar: canvas => {
          const r = D1.inferencia.rejilla;
          return crearGraficoLinea(canvas, r.map(f => String(f.phi)), [
            { label: 'e.e. suponiendo independencia', data: r.map(f => f.ee_ingenuo),
              borderColor: COLORES_GRAFICO.gris, tension: 0.2, pointRadius: 3 },
            { label: 'e.e. real', data: r.map(f => f.ee_real),
              borderColor: COLORES_GRAFICO.secundario, tension: 0.2, pointRadius: 3 }
          ], { scales: { x: { title: { display: true, text: 'alcance de la correlación, phi' } },
                         y: { title: { display: true, text: 'error estándar' } } } });
        },
        opciones: [
          { texto: 'El e.e. ingenuo no ve la correlación, así que subestima cada vez más al crecer phi.',
            correcta: true,
            retro: 'Con phi = ' + D1.inferencia.rejilla[4].phi + ' el real es '
              + n5(D1.inferencia.rejilla[4].factor) + ' veces el ingenuo. La fórmula clásica solo mira la '
              + 'dispersión de los datos, no cómo se relacionan entre sí.' },
          { texto: 'La media está cada vez peor estimada al crecer phi.', correcta: false,
            retro: 'La media sigue bien estimada: la simulación da '
              + n5(D1.una_realizacion.media_de_las_medias) + ' con media verdadera '
              + D1.una_realizacion.media_del_proceso + '. Lo que falla es la CONFIANZA, no la estimación. '
              + 'Ésa es la parte que hace el fallo difícil de ver.' },
          { texto: 'El e.e. real crece porque la varianza del proceso crece con phi.', correcta: false,
            retro: 'La varianza marginal es la misma para todo phi; lo que cambia es la covarianza entre celdas.' },
          { texto: 'Con phi grande hay menos datos, y por eso sube el error.', correcta: false,
            retro: 'Hay siempre ' + D1.inferencia.n + ' celdas. Lo que baja es la información que aportan: el n '
              + 'efectivo pasa de ' + D1.inferencia.n + ' a ' + n5(D1.inferencia.n_eff_phi4) + '.' }
        ],
        retroAcierto: 'Y no es un sesgo de la estimación: es un sesgo de la confianza.',
        retroFallo: 'Módulo 4.'
      },
      {
        tipo: 'numerica', modulo: 7,
        pregunta: 'El I de Moran de la deserción pasa de ' + n5(D1.escala.moran_municipal) + ' entre los '
          + D1.escala.n_municipal + ' municipios a ' + n5(D1.escala.moran_departamental) + ' entre los '
          + D1.escala.n_departamental + ' departamentos. ¿Qué porcentaje cae? Dos decimales.',
        respuesta: Number(n5(D1.escala.caida_pct, 2)), tolerancia: 0.05,
        pista: 'Es una caída porcentual normal y corriente sobre el valor municipal.',
        retroAcierto: 'Y no ha cambiado ni el dato ni la variable: solo la unidad de análisis.',
        retroFallo: 'Cae el ' + n5(D1.escala.caida_pct) + ' %. Módulo 7.'
      },
      {
        tipo: 'opcion', modulo: 6,
        pregunta: 'De ' + D1.una_realizacion.n_realizaciones + ' realizaciones del mismo proceso, con media '
          + 'verdadera ' + D1.una_realizacion.media_del_proceso + ', el análisis ingenuo declara la media '
          + 'significativa en el ' + n5(D1.una_realizacion.pct_rechaza_ingenuo) + ' % de los casos. '
          + '¿Con qué otra cifra del capítulo hay que cuadrar ésta?',
        pista: 'Rechazar y no cubrir son la misma cosa vista del derecho y del revés.',
        opciones: [
          { texto: 'Con la cobertura del módulo 4: ' + n5(D1.inferencia.cobertura_phi4)
              + ', o sea un ' + n5(D1.una_realizacion.pct_rechaza_modulo4) + ' % de rechazo.', correcta: true,
            retro: 'Se separan ' + n5(D1.una_realizacion.discrepancia_con_modulo4) + ' puntos, algo más de un '
              + 'error de Monte Carlo. El generador comprueba esa coherencia y se detiene si se rompe.' },
          { texto: 'Con el I de Moran de la deserción.', correcta: false,
            retro: 'Son cosas distintas: una es autocorrelación de un dato real, la otra la tasa de error de un '
              + 'contraste sobre un campo simulado.' },
          { texto: 'Con el n efectivo de los municipios.', correcta: false,
            retro: 'El n efectivo cuantifica la pérdida de información, no la tasa de rechazo.' },
          { texto: 'Con ninguna: es una cifra independiente.', correcta: false,
            retro: 'Justo eso es lo que hay que desconfiar. Dos módulos midiendo lo mismo sin compararse es como '
              + 'se cuelan las incoherencias. Módulos 4 y 6.' }
        ],
        retroAcierto: 'Dos cifras que deberían coincidir y viven a dos módulos de distancia son las que nadie compara.',
        retroFallo: 'Módulo 6, la caja de aviso.'
      },
      {
        tipo: 'multiple', modulo: 9,
        pregunta: 'Sobre las discrepancias declaradas entre R y Python, marca <strong>todo</strong> lo que sea cierto.',
        pista: 'Son dos, y las dos tienen que ver con qué se está midiendo, no con quién se equivoca.',
        opciones: [
          { texto: 'sf informa el tipo de la CAPA y shapely el de cada rasgo; por eso los conteos difieren.',
            correcta: true,
            retro: 'sf dice ' + D1.anatomia.nc.n_multipolygon + ' MULTIPOLYGON y shapely solo '
              + D1.anatomia.nc.n_partes_multiples + '. La geometría es idéntica.' },
          { texto: 'spdep y esda cuentan distinto las unidades sin vecinos al calcular el I de Moran.',
            correcta: true,
            retro: n5(D1.escala.moran_municipal) + ' frente a ' + n5(D1.escala.moran_municipal_n_total)
              + '. Se recupera uno desde el otro multiplicando por (n − islas)/n.' },
          { texto: 'Una discrepancia sin explicar y una documentada valen lo mismo si el material las publica.',
            correcta: false,
            retro: 'No: el auditor del capítulo lleva la lista de las conocidas y FALLA ante una que no esté. '
              + 'Ésa es la diferencia entre material didáctico y un error.' },
          { texto: 'Las discrepancias vienen de que GDAL y GEOS son distintos en cada lenguaje.', correcta: false,
            retro: 'Son las MISMAS bibliotecas: R y Python las llaman a las dos. El desacuerdo está en la capa de '
              + 'arriba. Módulo 8.' }
        ],
        retroAcierto: 'Ante una diferencia, la primera pregunta es «¿estamos midiendo lo mismo?».',
        retroFallo: 'Las correctas son las dos primeras. Módulo 9.'
      },
      {
        tipo: 'opcion', modulo: 10,
        pregunta: '¿Verdadero o falso? Siempre que el dato tenga coordenadas, la validación cruzada por bloques '
          + 'espaciales es la correcta.',
        pista: 'Depende de a qué pregunta quieras que responda el modelo.',
        opciones: [
          { texto: 'Falso: depende de la pregunta', correcta: true,
            retro: 'La de bloques responde a «¿cuánto me fío en una zona donde no he medido?». Si la pregunta '
              + 'fuera rellenar huecos entre estaciones existentes, la aleatoria sería la adecuada.' },
          { texto: 'Verdadero: con coordenadas, siempre bloques', correcta: false,
            retro: 'Es la conclusión fácil de un módulo que se pasa midiendo lo mal que sale la aleatoria. Pero '
              + 'elegir el reparto es declarar a qué pregunta se responde, y hacerlo por defecto es responder a '
              + 'la que no era. Módulo 10.' }
        ],
        retroAcierto: 'Y por eso el material publica las dos y dice qué mide cada una.',
        retroFallo: 'Módulo 10, la caja de aviso final.'
      }
    ];
"""


# =====================================================================
# El glosario de notación
# =====================================================================
GLOSARIO_JS = (
    "    // El glosario se generalizó en T0.2: sus columnas ya no vienen\n"
    "    // cableadas con los rótulos de Muestreo. Aquí las declara el propio\n"
    "    // precálculo, que es quien sabe qué texto guía corresponde a cada\n"
    "    // símbolo de este curso.\n"
    "    GLOSARIOS['cap1-notacion'] = "
    + json.dumps({"titulo": D["glosario"]["titulo"], "nota": D["glosario"]["nota"],
                  "columnas": D["glosario"]["columnas"], "filas": D["glosario"]["filas"]},
                 ensure_ascii=False) + ";\n")


# =====================================================================
# El ensamblado
# =====================================================================
def reemplaza_region(texto, abre, cierra, nuevo, que, max_lineas, min_lineas=0):
    """Sustituye entre `abre` y el primer `cierra` posterior, con DOS topes.

    El máximo no es decorativo. La primera versión del ensamblador del
    fixture de T0.5 buscaba el cierre de `courseData` con `doc.index("];")`
    y encontró uno que estaba dentro de un COMENTARIO 270 líneas más abajo.
    Se llevó `renderNavigation` y `loadModule`, el archivo salió MÁS GRANDE
    que la plantilla, todas las anclas siguientes se encontraron y el
    informe salió en verde. Solo abrirlo en el navegador —contenido en
    blanco— lo destapó.

    El MÍNIMO se añadió aquí, en T1.2, por el fallo simétrico: el ancla de
    cierre `\\n    };\\n` casó con el final del PRIMER simulador de
    demostración y dejó vivos los otros dos. El archivo salió bien formado,
    la consola limpia y el ensamblador en verde; los dos simuladores
    zombis solo se vieron en la línea «registrados y no usados» del propio
    informe. Sustituir de menos es tan silencioso como sustituir de más.
    """
    if texto.count(abre) != 1:
        sys.exit(f"PARADO: el ancla de apertura de «{que}» aparece "
                 f"{texto.count(abre)} veces, no 1")
    i = texto.index(abre)
    j = texto.index(cierra, i) + len(cierra)
    n_lineas = texto[i:j].count("\n")
    if n_lineas > max_lineas:
        sys.exit(f"PARADO: la región de «{que}» ocupa {n_lineas} líneas y el tope es "
                 f"{max_lineas}.\n        El cierre {cierra!r} se encontró DEMASIADO "
                 f"LEJOS; la plantilla ha cambiado.")
    if n_lineas < min_lineas:
        sys.exit(f"PARADO: la región de «{que}» ocupa solo {n_lineas} líneas y el "
                 f"mínimo es {min_lineas}.\n        El cierre {cierra!r} se encontró "
                 f"DEMASIADO PRONTO: quedaría dentro del archivo lo que había que "
                 f"sustituir.")
    print(f"  OK   {que}  ({n_lineas} líneas sustituidas)")
    return texto[:i] + nuevo + texto[j:]


def sustituye(texto, ancla, nuevo, que):
    veces = texto.count(ancla)
    if veces != 1:
        sys.exit(f"PARADO: el ancla de «{que}» aparece {veces} veces, no 1.\n"
                 f"        {ancla[:90]!r}")
    print(f"  OK   {que}")
    return texto.replace(ancla, nuevo, 1)


def main() -> int:
    doc = PLANTILLA.read_text(encoding="utf-8")
    print(f"\n=== ensambla_cap1.py ===\nplantilla: {len(doc)/1024:.0f} KB\n")

    # --- 1. Textos meta ------------------------------------------------
    doc = sustituye(doc, "<title>Plantilla de capítulo — Estadística Espacial</title>",
                    f"<title>Capítulo 1 · {D['meta']['titulo']} — Estadística Espacial</title>",
                    "título")
    doc = sustituye(doc, "PLANTILLA BASE •\n              5 MÓDULOS DE DEMOSTRACIÓN • UNBOSQUE 2026-II",
                    f"CAPÍTULO 1 • {D['meta']['titulo'].upper()} •\n"
                    f"              SEMANA {D['meta']['semana']} • UNBOSQUE 2026-II",
                    "subtítulo de la cabecera")
    doc = sustituye(doc, "Estadística Espacial (20929) • Plantilla de\n          capítulo • UnBosque 2026-II",
                    f"Estadística Espacial (20929) • Capítulo 1 de 10 •\n"
                    f"          Semana {D['meta']['semana']} • UnBosque 2026-II",
                    "pie")

    # --- 2. courseData + los datos del precálculo ----------------------
    doc = reemplaza_region(doc, "    const courseData = {", "\n    };\n", COURSE_DATA,
                           "courseData + DATOS_CAP1", max_lineas=20)

    # --- 3. Los doce módulos -------------------------------------------
    doc = reemplaza_region(
        doc,
        "  <!-- ============================================================ -->\n"
        "  <!-- MÓDULO 1 · Cajas y tipografía",
        "\n  <script>", MODULOS.lstrip("\n") + "\n  <script>",
        "los doce módulos", max_lineas=600)

    # --- 4. Los mapas ---------------------------------------------------
    vieja = [l for l in doc.splitlines() if l.startswith("    GEOMAPAS['demo-mapa'] =")]
    if len(vieja) != 1:
        sys.exit(f"PARADO: {len(vieja)} registros de GEOMAPAS['demo-mapa'], se esperaba 1")
    doc = sustituye(doc, vieja[0], GEOMAPAS_JS.rstrip("\n"), "los once .geomapa")

    # --- 5. El glosario (se lleva por delante el de demostración) -------
    doc = reemplaza_region(doc, "    GLOSARIOS['demo-notacion'] = {", "\n    };\n",
                           GLOSARIO_JS, "GLOSARIOS", max_lineas=40)

    # --- 6. Los simuladores ---------------------------------------------
    # El cierre NO es `\n    };\n`: eso casaba con el final del PRIMER
    # simulador de demostración y dejaba vivos los otros dos, que luego
    # aparecían como «registrados y no usados». Sustituir de menos es tan
    # silencioso como sustituir de más —el archivo sale bien formado y la
    # consola limpia—, así que el ancla de cierre es el comienzo de la
    # sección siguiente, que sí es inequívoco, y hay TOPE MÍNIMO además de
    # máximo.
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

    # --- 7. Las dos autoevaluaciones ------------------------------------
    doc = reemplaza_region(doc, "    AUTOEVALUACIONES['demo'] = [", "\n    ];\n",
                           QUIZ_JS, "AUTOEVALUACIONES", max_lineas=90)

    DESTINO.parent.mkdir(parents=True, exist_ok=True)
    DESTINO.write_text(doc, encoding="utf-8")

    # --- Guardas de salida ----------------------------------------------
    # Que el ensamblador escriba no significa que haya escrito bien: en
    # T0.5 escribió un archivo más grande que la plantilla, con el motor
    # mutilado, e informó «limpio».
    marcado = doc[:doc.rindex("\n  <script>")]
    mods = doc.count('<template id="module-')
    bloques_r = doc.count('class="language-r"')
    bloques_py = doc.count('class="language-python"')
    # Las dos formas: R las escribe escapadas y Python no. Contar solo una
    # daba 14 donde hay 28, y sobre ese 14 el guarda de abajo se disparaba
    # sin motivo — una alarma falsa gasta la confianza igual que un fallo
    # que se calla.
    cifras = doc.count("#&gt;") + doc.count("#>")
    lienzos = marcado.count("<canvas")
    con_alt = sum(1 for c in marcado.split("<canvas")[1:]
                  if "aria-label" in c.split(">")[0])
    ejercicios = marcado.count('<div class="ejercicio-guiado">')

    # `registrados` se busca solo en las líneas que NO son comentario: la
    # documentación del motor escribe `GEOMAPAS['id'] = { fuente, … }` y ese
    # 'id' aparecía como registro fantasma en el informe.
    codigo = "\n".join(l for l in doc.splitlines() if not l.lstrip().startswith("//"))

    def par(attr, registro):
        us = sorted(set(re.findall(attr, marcado)))
        rg = sorted(set(re.findall(registro, codigo)))
        return us, rg

    usados, registrados = par(r'data-geomapa="([^"]+)"', r"GEOMAPAS\['([^']+)'\]\s*=")
    sims_usados, sims_reg = par(r'data-simulador="([^"]+)"', r"SIMULADORES\['([^']+)'\]\s*=")
    quiz_usados, quiz_reg = par(r'data-quiz="([^"]+)"', r"AUTOEVALUACIONES\['([^']+)'\]\s*=")
    glo_usados, glo_reg = par(r'data-glosario="([^"]+)"', r"GLOSARIOS\['([^']+)'\]\s*=")

    # Relativo al árbol cuando sale de él, absoluto cuando `CAP1_DESTINO` lo
    # manda fuera: `relative_to` lanza en vez de devolver la ruta tal cual.
    try:
        donde = DESTINO.relative_to(RAIZ)
    except ValueError:
        donde = DESTINO
    print(f"\n{donde}  {len(doc)/1024:.0f} KB")
    print(f"  {mods} módulos · {len(sims_usados)} simuladores · {len(usados)} mapas · "
          f"{bloques_r} bloques de R y {bloques_py} de Python · {cifras} cifras anunciadas")
    print(f"  {lienzos} lienzos, {con_alt} con aria-label · "
          f"{ejercicios} ejercicios guiados · "
          f"{len(quiz_usados)} autoevaluaciones")

    problemas = []
    if mods != 12:
        problemas.append(f"{mods} plantillas de módulo, se esperaban 12")
    if lienzos != con_alt:
        problemas.append(f"{lienzos - con_alt} lienzo(s) sin aria-label")
    if cifras < 20:
        problemas.append(f"solo {cifras} líneas #> — hay poco que verificar")
    if ejercicios != 4:
        problemas.append(f"{ejercicios} ejercicios guiados, se esperaban 4")
    if len(quiz_usados) != 2:
        problemas.append(f"{len(quiz_usados)} autoevaluaciones, se esperaban 2 "
                         f"(la diagnóstica de entrada y la del capítulo)")
    # El motor del quiz solo entiende CUATRO tipos. Uno inventado no da
    # error de sintaxis: revienta dentro de `iniciarAutoevaluaciones()` y se
    # lleva por delante todo lo que loadModule() llama DESPUÉS —los mapas,
    # las fórmulas—, en un módulo y no en los otros. Así se descubrió, y por
    # eso se comprueba aquí.
    TIPOS_VALIDOS = {"opcion", "multiple", "numerica", "grafico"}
    tipos = set(re.findall(r"tipo:\s*'([a-z]+)'", QUIZ_JS))
    raros = sorted(tipos - TIPOS_VALIDOS)
    if raros:
        problemas.append(f"tipos de pregunta que el motor no conoce: {raros}")
    faltan_tipos = sorted(TIPOS_VALIDOS - tipos)
    if faltan_tipos:
        problemas.append(f"el capítulo no usa los cuatro tipos; faltan {faltan_tipos}")

    # KaTeX no tiene métrica para los espacios finos de Unicode: dentro de
    # una fórmula avisa por consola y deja un hueco. Y el aviso sale en la
    # consola de UN módulo entre doce, así que sin esto se ve solo si a
    # alguien se le ocurre mirar justo ese. Que lo cace el ensamblador es
    # más barato que recordarlo.
    RAROS = {" ": "U+202F espacio fino", " ": "U+2009 thin space",
             " ": "U+00A0 nbsp"}
    formulas = re.findall(r"\\\(.*?\\\)|\$\$.*?\$\$", marcado, re.S)
    sucias = [(f[:60], RAROS[c]) for f in formulas for c in RAROS if c in f]
    if sucias:
        problemas.append(f"{len(sucias)} fórmula(s) con un espacio que KaTeX no "
                         f"entiende: {sucias[:3]} — usa ent_mate()")
    if doc.count("<template") != doc.count("</template>"):
        problemas.append("las plantillas no abren y cierran igual")
    for que, us, rg in [("geomapa", usados, registrados), ("simulador", sims_usados, sims_reg),
                        ("quiz", quiz_usados, quiz_reg), ("glosario", glo_usados, glo_reg)]:
        falta = sorted(set(us) - set(rg))
        if falta:
            problemas.append(f"{que}(s) usados sin registrar: {falta}")
        sobra = sorted(set(rg) - set(us))
        if sobra:
            # No es fallo —la plantilla deja registros de demostración—,
            # pero se dice: un registro huérfano suele ser un componente
            # que alguien quitó del marcado y se olvidó de aquí.
            print(f"  ---  {que}(s) registrados y no usados: {sobra}")
    # El presupuesto del §4 es de GEOMETRÍA, y las rejillas simuladas no
    # son territorio. Se miden por separado, contra el mismo listón, para
    # no ir gastando por la puerta de atrás lo que se ahorra por delante.
    kb_geo = sum(len(json.dumps(M[k], ensure_ascii=False).encode()) for k in
                 ["snow", "japanesepines", "bogota", "nc", "agregacion", "desercion",
                  "meuse", "ideam"]) / 1024
    kb_sim = len(json.dumps(_sim, ensure_ascii=False).encode()) / 1024
    print(f"  geometría {kb_geo:.1f} KB · rejillas simuladas {kb_sim:.1f} KB "
          f"(presupuesto: 120 KB cada uno)")
    if kb_geo > 120 or kb_sim > 120:
        problemas.append("la geometría se sale del presupuesto de 120 KB")

    # Las DOS rejillas del módulo 4, emparejadas aquí y no de palabra: que
    # cada campo tenga fila de cifras y que las dos traigan la misma
    # rho_vecino, que R calcula por separado en cada una. Un descuadre
    # entre ellas no lo ve ningún auditor —comprueban el JSON y la prosa,
    # no el cableado— y ya vivió en el capítulo publicado. Anexo T1.2.
    #
    # Tolerancia 1e-6: cap1_mapas.json redondea rho_vecino a ocho decimales
    # y cap1_datos.json trae diez (3e-9 de diferencia legítima), mientras
    # dos alcances vecinos distan 0.10 largo.
    rej = {f["phi"]: f for f in D["inferencia"]["rejilla"]}
    huerfanos = [c["phi"] for c in M["campos"] if c["phi"] not in rej]
    descuadre = [c["phi"] for c in M["campos"]
                 if c["phi"] in rej
                 and abs(c["rho_vecino"] - rej[c["phi"]]["rho_vecino"]) > 1e-6]
    print(f"  módulo 4: {len(M['campos'])} campos de {len(rej)} alcances de la "
          f"rejilla de cifras · emparejados por phi y con la misma "
          f"rho_vecino: {len(M['campos']) - len(huerfanos) - len(descuadre)}")
    if huerfanos:
        problemas.append(f"campo(s) simulado(s) sin fila en inferencia.rejilla: "
                         f"{huerfanos} — el deslizador ofrecería una posición vacía")
    if descuadre:
        problemas.append(f"el campo y la fila de phi {descuadre} no traen la misma "
                         f"rho_vecino: una de las dos rejillas se movió")

    # --- T2.2 · el puente de phi al factor ----------------------------
    # El módulo publica DOS cocientes que se parecen y no son el mismo, y
    # antes calculaba uno de ellos aquí, en el ensamblador. Ahora los dos
    # salen de R y estas guardas los atan a su definición: sin ellas, el
    # día que R cambie el nombre de un campo la prosa imprimiría `NaN` con
    # los dos auditores en verde, porque ninguno mira el cableado.
    PUENTE = ("rho_diagonal", "efecto_diseno", "inflacion_varianza",
              "s2_esperada", "s2_medida")
    faltan_campos = sorted({c for f in D["inferencia"]["rejilla"]
                            for c in PUENTE if c not in f})
    if faltan_campos:
        problemas.append(f"a inferencia.rejilla le faltan {faltan_campos}: la lectura "
                         f"del simulador y el recuadro del módulo 4 los citan")
    else:
        malas = []
        for f in D["inferencia"]["rejilla"]:
            # inflacion_varianza ES factor^2, y efecto_diseno ES n/n_eff.
            # Se comprueban aquí porque son las dos identidades que la
            # prosa afirma con un «que es» y un «leído al revés».
            if abs(f["inflacion_varianza"] - f["factor"] ** 2) > 1e-6 * max(1, f["inflacion_varianza"]):
                malas.append(f"phi={f['phi']}: inflacion_varianza no es factor^2")
            if abs(f["efecto_diseno"] - D["inferencia"]["n"] / f["n_eff"]) > 1e-6 * max(1, f["efecto_diseno"]):
                malas.append(f"phi={f['phi']}: efecto_diseno no es n/n_eff")
        if malas:
            problemas.append(f"las dos identidades del módulo 4 se rompieron: {malas[:4]}")
    # La afirmación de cierre —«no son el mismo número», y cuál es mayor—
    # SOLO vale en el phi que el módulo destaca. Medido: en phi = 0 y 0.5
    # la desigualdad se invierte, porque ahí s^2 casi no se encoge
    # (s2_esperada 1.00000 y 0.99650) y decide el ruido de Monte Carlo.
    # Escribirla para los siete alcances habría puesto rojo un capítulo
    # correcto, que es la forma más rápida de enseñar a ignorar el informe.
    if not r4["inflacion_varianza"] > r4["efecto_diseno"]:
        problemas.append(f"en phi = {r4['phi']} la varianza declarada ya no se queda más "
                         f"corta ({r4['inflacion_varianza']}) que lo que se ensancha la "
                         f"real ({r4['efecto_diseno']}): la prosa del módulo 4 afirma esa "
                         f"desigualdad y el orden de sus dos cifras")
    if not 0 < r4["s2_esperada"] < 1:
        problemas.append(f"s2_esperada en phi = {r4['phi']} vale {r4['s2_esperada']}: el "
                         f"módulo 4 explica la brecha diciendo que s^2 SE ENCOGE")
    for campo, valor in (("sigma", 1), ):
        if D["inferencia"].get(campo) != valor:
            problemas.append(f"inferencia.{campo} ya no vale {valor}, y la prosa del módulo 4 "
                             f"lo escribe y luego lo da por sabido")
    if not str(D["inferencia"].get("escala_h", "")).strip():
        problemas.append("inferencia.escala_h está vacío: el módulo 4 lo publica en negrita "
                         "como la definición de h, y sin él e^(-1/4) queda sin justificar")
    print(f"  módulo 4: puente de phi={r4['phi']} · rho vecino {r4['rho_vecino']} · "
          f"efecto de diseño {r4['efecto_diseno']} · la varianza declarada se queda "
          f"{r4['inflacion_varianza']} veces corta")

    # El módulo 5 evalúa n_eff en el NAVEGADOR —D9 lo autoriza: es aritmética
    # cerrada— y la rejilla de R pasa a ser la referencia contra la que ese
    # cómputo se contrasta en tiempo de ejecución. Lo que se comprueba aquí es
    # lo que esa guarda no puede ver: que las anclas que la prosa nombra sigan
    # en el índice que el texto da por sabido. Si R reordenara RHOS, la prosa
    # seguiría sacando su cifra del JSON y los dos auditores seguirían en
    # verde diciendo otra cosa. Anexo T1.1.
    ANCLAS = {1: 0.01, 4: 0.1}
    m = re.search(r"RHO_MAX = ([\d.]+)", SIMULADORES_JS)
    rho_max = float(m.group(1)) if m else None
    for i, v in ANCLAS.items():
        if i >= len(ne["rhos"]) or ne["rhos"][i] != v:
            problemas.append(f"n_efectivo.rhos[{i}] ya no vale {v} — la prosa del "
                             f"módulo 5 y la lectura del simulador lo dan por sabido")
    if rho_max is None:
        problemas.append("no se encuentra RHO_MAX en el JS: el tope del deslizador "
                         "de rho ha dejado de ser comprobable")
    else:
        if rho_max not in ne["rhos"]:
            problemas.append(f"el deslizador para en rho = {rho_max}, que no está en "
                             f"la rejilla: su extremo sería una cifra sin auditar")
        fuera = sorted(v for v in ANCLAS.values() if v > rho_max)
        if fuera:
            problemas.append(f"el deslizador no alcanza las anclas {fuera}")
    if ne["enes"][-1] != ne["rejilla"][-1]["n"]:
        problemas.append("enes y rejilla del módulo 5 no van en el mismo orden")
    # El rombo de Colombia enseña que 1 121 municipios valen menos que 1 121.
    # Si el cociente de remuestreos dejara de inflar el error, el punto se
    # subiría por encima de la diagonal y el módulo diría lo contrario.
    if not 0 < ne["desercion_municipal"] < ne["desercion_n"]:
        problemas.append(f"el punto de Colombia ({ne['desercion_n']}, "
                         f"{ne['desercion_municipal']}) no cae bajo la diagonal")
    print(f"  módulo 5: deslizador de rho de 0 a {rho_max} · "
          f"{len(ne['enes'])}×{len(ne['rhos'])} anclas de R contra la curva que "
          f"evalúa el navegador")

    # Los DOS rho del módulo 5 (T2.1). La prosa no publica solo dos cifras:
    # publica una RELACIÓN entre ellas —cuál es mayor, en qué factor, y que
    # una reproduce el titular y la otra no— y además nombra distancias
    # concretas del correlograma por su posición en la lista. Nada de eso lo
    # ve el auditor de prosa, que comprueba que las cifras existan en el JSON,
    # ni el del precálculo, que comprueba cada cifra por su lado.
    rtg = ne["rho_del_titular"]
    if rtg["n"] != ne["desercion_n"]:
        problemas.append(f"el rho del titular habla de {rtg['n']} municipios y el módulo "
                         f"publica {ne['desercion_n']}")
    if abs(rtg["n"] / (1 + (rtg["n"] - 1) * rtg["implicito"])
           - ne["desercion_municipal"]) > 1e-5:
        problemas.append(f"el rho implícito {rtg['implicito']} ya no reproduce el "
                         f"{ne['desercion_municipal']} del titular, y la prosa dice que "
                         f"pasa por el rombo «por construcción»")
    if not rtg["implicito"] > rtg["estimado"]:
        problemas.append(f"el rho implícito ({rtg['implicito']}) ya no supera al medido "
                         f"({rtg['estimado']}): la prosa cuenta la discrepancia al revés")
    # Las bandas que la prosa nombra POR SU POSICIÓN. Si R cambiara el
    # esquema, el texto seguiría sacando las cifras del JSON y diría otras
    # distancias con los dos auditores en verde — el mismo agujero que T1.1
    # tapó con las anclas de `rhos`.
    ANCLAS_BANDA = {(0, "d2"): 25, (4, "d1"): 175, (5, "d2"): 500, (6, "d2"): 800}
    for (i, extremo), valor in sorted(ANCLAS_BANDA.items()):
        if i >= len(rtg["bandas"]) or rtg["bandas"][i][extremo] != valor:
            problemas.append(f"la banda {i} ya no tiene {extremo} = {valor} km: la prosa del "
                             f"módulo 5 nombra esa distancia dándola por sabida")
    if any(b["d2"] != rtg["bandas"][i + 1]["d1"] for i, b in enumerate(rtg["bandas"][:-1])):
        problemas.append("las bandas del rho estimado dejan huecos o se solapan: su promedio "
                         "ponderado no cubriría todos los pares")
    # Y la afirmación central del recuadro: que la correlación se vuelve
    # negativa a media distancia, que es lo que explica por qué el promedio
    # se hunde. Sin esto, la explicación podría quedar desmentida por el dato.
    if not (rtg["bandas"][4]["I"] < 0 and rtg["bandas"][5]["I"] < 0):
        problemas.append(f"la prosa dice que entre {rtg['bandas'][4]['d1']} y "
                         f"{rtg['bandas'][5]['d2']} km la I se vuelve negativa, y vale "
                         f"{rtg['bandas'][4]['I']} y {rtg['bandas'][5]['I']}")
    print(f"  módulo 5, rho del titular: implícito {n(rtg['implicito'], 7)} contra medido "
          f"{n(rtg['estimado'], 7)} · factor {n(rtg['razon_rho'])} · "
          f"{len(rtg['bandas'])} bandas, {rtg['pares_totales']} pares")

    # Las DOS listas del módulo 6, emparejadas aquí y no de palabra. Hasta
    # T1.3 no eran dos vistas de un lote sino dos SIMULACIONES distintas
    # —28×28 con semilla +700 los mapas, 16×16 con semilla +300 la banda y
    # todas las cifras—, de modo que la curva del variograma no era la de
    # ninguno de los tres mapas y la intro anunciaba una rejilla que no se
    # estaba viendo. Ningún auditor podía verlo: cada archivo era correcto
    # por su cuenta, y el defecto vivía en el hueco entre los dos. Anexo T1.3.
    #
    # Tolerancia 1e-6, la misma que la guarda de ejecución: cap1_mapas.json
    # guarda ocho cifras significativas y cap1_datos.json diez.
    mr, k6, n_lags = M["realizaciones"], ur["k"], len(ur["variograma"]["lags"])
    if len(mr) != len(rv):
        problemas.append(f"{len(mr)} mapas de realización y {len(rv)} filas de cifras: "
                         f"el botón ofrecería una posición sin la otra mitad")
    else:
        for mapa, fila in zip(mr, rv):
            quien = f"realización {fila['id']}"
            if mapa.get("id") != fila.get("id"):
                problemas.append(f"{quien}: el mapa dice id {mapa.get('id')} — las dos "
                                 f"listas del módulo 6 van en distinto orden")
            # mean(z) sobre el vector del mapa contra colMeans() sobre la
            # matriz de las mil: dos rutas de R para la misma cifra. Es lo
            # único que delata un emparejamiento torcido, porque comparar
            # una lista consigo misma no delata nada (T1.2.d).
            if abs(mapa["media_espacial"] - fila["media"]) > 1e-6:
                problemas.append(f"{quien}: el mapa tiene media {mapa['media_espacial']} y "
                                 f"su fila {fila['media']} — no son el mismo campo")
            if abs(mapa["sd_espacial"] - fila["sd"]) > 1e-6:
                problemas.append(f"{quien}: el mapa tiene sd {mapa['sd_espacial']} y su "
                                 f"fila {fila['sd']}")
            # La rejilla del mapa contra la que la prosa anuncia. Este es el
            # hilo que ata la frase «sobre 16×16 celdas» a lo que se dibuja:
            # era falsa y los dos auditores estaban en verde.
            if mapa["nx"] != k6 or mapa["ny"] != k6:
                problemas.append(f"{quien}: el mapa es de {mapa['nx']}×{mapa['ny']} y el "
                                 f"módulo publica {k6}×{k6} — la intro mentiría")
            if len(fila.get("variograma", [])) != n_lags:
                problemas.append(f"{quien}: su variograma trae "
                                 f"{len(fila.get('variograma', []))} rezagos y la banda "
                                 f"{n_lags}: se dibujarían sobre ejes distintos")
    # La prosa AFIRMA que las tres caben dentro de la banda en los ocho
    # rezagos, y esa frase es lo único del módulo que no sale de una cifra
    # del JSON sino de una propiedad de los datos. Si mañana una realización
    # se saliera, la frase quedaría falsa y ningún auditor lo vería: el de
    # cifras no la mira porque no lleva números, y el de prosa comprueba que
    # las cifras existan, no que la afirmación siga siendo cierta.
    fuera = [(f["id"], f["lags_fuera_banda"]) for f in rv if f.get("lags_fuera_banda")]
    if fuera:
        problemas.append(f"la prosa del módulo 6 dice que las tres caben dentro de la banda "
                         f"en los ocho rezagos, y {fuera} se salen: hay que reescribirla")
    # Las medias de las tres vistas SON las tres primeras de medias_muestra,
    # que R escribe por su lado. Si el capítulo dejara de enseñar las tres
    # primeras sin decirlo, esto es lo que se pondría rojo.
    for fila, esperada in zip(rv, ur["medias_muestra"]):
        if abs(fila["media"] - esperada) > 1e-9:
            problemas.append(f"realización {fila['id']}: su media {fila['media']} no es la "
                             f"{esperada} de medias_muestra — ya no son las tres primeras")
    # Y las tres curvas, distintas dos a dos. Sin esto «cambiar de realización
    # cambia la curva» vuelve a ser una promesa: tres curvas idénticas pasarían
    # todo lo de arriba con el botón moviendo solo el mapa, que es exactamente
    # el defecto que T1.3 viene a cerrar.
    #
    # Solo sobre las curvas COMPLETAS: a una fila sin variograma ya le ha
    # puesto su MAL el bucle de arriba, y bajar aquí con ella reventaba el
    # ensamblador con un KeyError —código 1, sí, pero sin una sola línea de
    # informe—. Lo encontró la inyección de T1.3.f, no el repaso del código.
    completas = [r["variograma"] for r in rv if len(r.get("variograma", [])) == n_lags]
    sep = min((max(abs(a - b) for a, b in zip(completas[i], completas[j]))
               for i in range(len(completas)) for j in range(i + 1, len(completas))),
              default=0.0)
    if len(completas) > 1 and sep <= 0.01:
        problemas.append(f"dos de los variogramas del módulo 6 se separan {sep:.5f} como "
                         f"máximo: el botón no cambiaría la curva a la vista")
    print(f"  módulo 6: {len(mr)} mapas de {k6}×{k6} emparejados con sus filas por media "
          f"y sd · {n_lags} rezagos por curva · las curvas se separan {sep:.5f}")

    # El módulo 1 estrena el acumulado, que el NAVEGADOR suma desde la serie
    # diaria. Eso vuelve comprobables cuatro cuentas que hasta ahora nadie
    # cruzaba: la serie y las cifras del titular venían de la misma tabla de
    # HistData pero por caminos distintos, y solo la curva acumulada las pone
    # una encima de otra. Si R recortara la serie por un extremo, el
    # acumulado llegaría al mango con otro porcentaje mientras la prosa
    # seguiría publicando el viejo, y los dos auditores en verde. Anexo T1.4.
    i_mango = (sn["serie_fecha"].index(sn["fecha_mango"])
               if sn["fecha_mango"] in sn["serie_fecha"] else -1)
    tot_a, tot_m = sum(sn["serie_ataques"]), sum(sn["serie_muertes"])
    # El largo de la serie contra los días que el capítulo publica. Esto lo
    # añadió el arnés: recortar la serie por la cola —donde los días traen
    # cero ataques— no movía ningún total y pasaba las comprobaciones de
    # abajo enteras, aunque el eje del gráfico perdiera un día y la prosa
    # cambiara su fecha final. El único hilo que ata el largo de la serie a
    # una cifra publicada es este. Anexo T1.4.
    largos = {k: len(sn[k]) for k in ("serie_fecha", "serie_ataques", "serie_muertes")}
    if len(set(largos.values())) != 1:
        problemas.append(f"las tres series del brote no miden lo mismo: {largos}")
    if len(sn["serie_fecha"]) != sn["n_dias_con_fecha"]:
        problemas.append(f"la serie trae {len(sn['serie_fecha'])} días y n_dias_con_fecha dice "
                         f"{sn['n_dias_con_fecha']}")
    if sn["n_dias_con_fecha"] + sn["n_dias_sin_fecha"] != sn["n_dias_tabla"]:
        problemas.append(f"{sn['n_dias_con_fecha']} + {sn['n_dias_sin_fecha']} días no dan los "
                         f"{sn['n_dias_tabla']} de la tabla de HistData")
    if i_mango <= 0:
        problemas.append(f"el día del mango ({sn['fecha_mango']}) no tiene víspera dentro de la "
                         f"serie: el acumulado no puede leerse «antes del mango»")
    else:
        if sum(sn["serie_ataques"][:i_mango]) != sn["ataques_antes_mango"]:
            problemas.append(f"la serie acumula {sum(sn['serie_ataques'][:i_mango])} ataques "
                             f"antes del mango y el titular publica {sn['ataques_antes_mango']}")
        if sn["serie_ataques"][i_mango] != sn["ataques_dia_mango"]:
            problemas.append(f"la serie pone {sn['serie_ataques'][i_mango]} ataques el día del "
                             f"mango y el titular publica {sn['ataques_dia_mango']}")
    if tot_a != sn["ataques_antes_mango"] + sn["ataques_desde_mango"]:
        problemas.append(f"la serie suma {tot_a} ataques y antes+desde el mango dan "
                         f"{sn['ataques_antes_mango'] + sn['ataques_desde_mango']}")
    if tot_m != sn["muertes_tabla"]:
        problemas.append(f"la serie suma {tot_m} muertes y muertes_tabla dice "
                         f"{sn['muertes_tabla']}")
    # La cifra que la curva acumulada va a hacer visible en el punto exacto
    # de la banda. Tolerancia 5e-10: el JSON redondea a diez decimales.
    if tot_a and abs(100 * sn["ataques_antes_mango"] / tot_a
                     - sn["pct_ataques_antes_mango"]) > 5e-10:
        problemas.append(f"pct_ataques_antes_mango ({sn['pct_ataques_antes_mango']}) no es "
                         f"{sn['ataques_antes_mango']}/{tot_a} — el acumulado lo dibuja")
    i_pico = sn["serie_ataques"].index(max(sn["serie_ataques"]))
    if (max(sn["serie_ataques"]) != sn["ataques_pico"]
            or sn["serie_fecha"][i_pico] != sn["fecha_pico"]):
        problemas.append(f"el pico de la serie es {max(sn['serie_ataques'])} el "
                         f"{sn['serie_fecha'][i_pico]} y el titular dice {sn['ataques_pico']} el "
                         f"{sn['fecha_pico']}")
    print(f"  módulo 1: serie de {len(sn['serie_fecha'])} días · el mango en el {i_mango} · "
          f"{tot_a} ataques y {tot_m} muertes, que el navegador acumula contra "
          f"{n(sn['pct_ataques_antes_mango'])} %")

    # Las tres series del correlograma van sobre UN eje de categorías, así
    # que comparten rejilla de bandas por construcción del GRÁFICO y no por
    # construcción del DATO. Con los interruptores el estudiante las
    # superpone de dos en dos a voluntad, de modo que la rejilla común deja
    # de ser un detalle: si R cambiara las bandas de una sola, el capítulo
    # dibujaría dos escalas distintas encima de la misma y ningún auditor lo
    # vería —cada uno comprueba su serie por su lado—. Anexo T1.4.
    bandas_ref = [(b["d1"], b["d2"]) for b in tb["ideam"]["bandas"]]
    for nombre in ("residuos_altitud", "permutado"):
        otras = [(b["d1"], b["d2"]) for b in tb[nombre]["bandas"]]
        if otras != bandas_ref:
            problemas.append(f"las bandas de tobler.{nombre} no son las de tobler.ideam: el "
                             f"correlograma superpondría dos rejillas distintas")
        if tb[nombre]["esperado"] != tb["ideam"]["esperado"]:
            problemas.append(f"tobler.{nombre}.esperado no es el de ideam: E[I] es una sola "
                             f"recta para las tres series")
    # La fila «cuánto de la I era altitud» solo sale con las dos series
    # encendidas, y es exactamente esta cuenta entre ellas.
    i_r, i_a = tb["ideam"]["bandas"][0]["I"], tb["residuos_altitud"]["bandas"][0]["I"]
    if abs(100 * (i_r - i_a) / i_r - tb["caida_por_altitud_pct"]) > 5e-8:
        problemas.append(f"caida_por_altitud_pct ({tb['caida_por_altitud_pct']}) no es la caída "
                         f"de {i_r} a {i_a} entre las dos series que el interruptor compara")
    print(f"  módulo 3: {len(bandas_ref)} bandas comunes a las 3 series · "
          f"E[I] = {n(tb['ideam']['esperado'], 6)} para las tres")

    # --- T2.4 · el mapa del módulo 7 y el caso que señala ---------------
    #
    # Aquí no se recalcula nada: eso es de `audita_cap1.py`, que rehace el
    # reparto en Python y hasta devuelve al terreno los rectángulos que el
    # lienzo dibuja. Lo que se vigila es EL CABLEADO, que es donde ningún
    # auditor llega: el mapa y las cifras viven en dos archivos que R escribe
    # por separado, y el rótulo de cada celda se empareja POR POSICIÓN con
    # `lineas_resaltadas`. Un orden distinto entre las dos listas escribiría
    # 13,50 en la celda que recibe 6,47 — cinco números correctos en cinco
    # sitios equivocados, con los dos auditores en verde.
    ma = M["agregacion"]
    if ma.get("resaltado") != cc["indice"]:
        problemas.append(f"el mapa del módulo 7 resalta el condado {ma.get('resaltado')} y el "
                         f"precálculo señala el {cc['indice']} ({cc['nombre']})")
    if list(ma.get("lineas_resaltadas") or []) != list(cc["celdas_tocadas"]):
        problemas.append(f"las celdas resaltadas del mapa {ma.get('lineas_resaltadas')} no son las "
                         f"{cc['celdas_tocadas']} que publica el precálculo")
    if [r["celda"] for r in cc["reparto"]] != list(cc["celdas_tocadas"]):
        problemas.append("el reparto y las celdas tocadas van en distinto orden: los rótulos del "
                         "mapa se emparejan por posición y caerían en la celda equivocada")
    if len(cc["reparto"]) != cc["n_celdas_toca"]:
        problemas.append(f"el reparto trae {len(cc['reparto'])} celdas y el condado toca "
                         f"{cc['n_celdas_toca']}: alguna celda quedaría sin rótulo")
    if ma.get("n_lineas") != agn["n_celdas"]:
        problemas.append(f"el mapa dibuja {ma.get('n_lineas')} rectángulos y la rejilla del módulo "
                         f"tiene {agn['n_celdas']}")
    # El CRS. La rejilla la construyó `st_make_grid` sobre el State Plane; un
    # mapa proyectado a otra cosa la pondría encima de una Carolina del Norte
    # que no es en la que se hizo la cuenta, y saldría plausible.
    if ma.get("crs") != 2264:
        problemas.append(f"el mapa del módulo 7 va en EPSG:{ma.get('crs')} y la rejilla se hizo "
                         f"sobre 2264: las dos capas serían de dos proyecciones distintas")
    # Las tres identidades que la prosa y la lectura AFIRMAN, no citan.
    if cc["aporte_predicado"] != cc["sids"] * cc["n_celdas_toca"]:
        problemas.append(f"la lectura escribe {cc['sids']} × {cc['n_celdas_toca']} = "
                         f"{cc['aporte_predicado']} y esa multiplicación ya no da")
    if cc["exceso"] != cc["aporte_predicado"] - cc["sids"]:
        problemas.append(f"el exceso publicado ({cc['exceso']}) no es lo que aporta de más "
                         f"({cc['aporte_predicado']} - {cc['sids']})")
    if cc["exceso_total"] != agn["total_rectangulos"] - agn["total_condados"]:
        problemas.append(f"el recuadro dice que los excesos suman {cc['exceso_total']} y el "
                         f"titular va de {agn['total_condados']} a {agn['total_rectangulos']}")
    if not cc["n_celdas_toca"] > 1:
        problemas.append(f"{cc['nombre']} toca {cc['n_celdas_toca']} celda(s): el módulo entero "
                         f"habla de un condado que cae en VARIAS")
    if not cc["roce_pct"] < 1:
        problemas.append(f"la celda del roce recibe el {cc['roce_pct']} % del condado y el "
                         f"recuadro la presenta como un roce")
    if abs(cc["fraccion_total_pct"] - 100) > 1e-6:
        problemas.append(f"el pie de la tabla de respaldo publica {cc['fraccion_total_pct']} % de "
                         f"condado repartido: el reparto ya no lo cubre entero")
    print(f"  módulo 7: {cc['nombre']} toca {cc['n_celdas_toca']} de {agn['n_celdas']} celdas · "
          f"aporta {cc['aporte_predicado']} donde tiene {cc['sids']} · {cc['exceso']} de más, el "
          f"{n(cc['pct_del_exceso'])} % de los {cc['exceso_total']} que sobran")

    if problemas:
        for p in problemas:
            print(f"  MAL  {p}")
        return 1
    print("\n  Ensamblado limpio.\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
