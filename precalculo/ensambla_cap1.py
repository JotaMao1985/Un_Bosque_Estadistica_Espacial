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
import math
import re
import subprocess
import pathlib
import sys
from baraja_opciones import baraja_documento

RAIZ = pathlib.Path(__file__).resolve().parent.parent
from pon_boton_indice import aplica as aplica_boton
import genera_referencias
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
vg6 = ur["variograma"]      # módulo 6: teórico en h entero, teórico de la clase, media y banda
rt = ne["rho_del_titular"]
# Módulo 5: la demostración del centrado y la tabla del techo. `rt` conserva
# solo el rho medio que corresponde al titular; el «rho medido» se retiró.
cz, tc = ne["centrado"], ne["techo"]
es, ec, ag = D["escala"], D["escala_correlacion"], D["agregacion"]
eco, an, cv = D["ecosistema"], D["anatomia"], D["cv_espacial"]
sop = ac["soporte"]
agn, agco = D["agregacion_soporte"]["nc"], D["agregacion_soporte"]["colombia"]
cc = agn["condado_caso"]        # el condado que el mapa del módulo 7 señala
dm = D["diseno_modelo"]
ru = dm["referencia_uniforme"]   # módulo 10: Thiessen de puntos uniformes, la referencia de la red
# Módulo 4 (R1 · T1.6): dónde caen las réplicas del remuestreo, cuánto mueve
# la semilla y cuánto mueve quitar un departamento.
rp, osm, sud = ir["replicas"], ir["otras_semillas"], ir["sin_un_departamento"]
b0 = tb["ideam"]["bandas"][0]    # módulo 3: la banda corta, la que tiene estaciones sin vecinos
pb1 = tb["permutacion_banda1"]   # y su esperanza, comprobada permutando
# El alto de la caja de las tres gráficas de R2 · T2.4: 360 px. Era una
# cuenta en línea que crecía hasta 440 px en el teléfono, para que la
# leyenda apilada no se comiera el trazado (G-11). Desde R2 · T2.1 eso lo
# hace la plantilla con todos los gráficos —leyenda al pie y un alto mínimo
# de trazado—, así que aquí queda solo el alto de pantalla ancha.
ALTO_T24 = "height:360px;"
# R2 · T2.4: las tres gráficas nuevas. Cada una dibuja una cifra que el
# capítulo ya publicaba y solo se leía.
al = sn["aleatorizacion"]        # módulo 1: la prueba de aleatorización de Snow
env3 = tb["envolvente"]          # módulo 3: la envolvente de permutación del correlograma
ci = inf["cien_ic"]              # módulo 4: cien intervalos de las réplicas de phi = 4
# Segunda ronda de T2.4: lo que las tres gráficas dejaban sin decir.
mc1 = al["marcos"]               # módulo 1: la parte de calle según el marco del plano
ma3 = tb["mas_alla"]             # módulo 3: las parejas que el eje deja fuera
su3 = tb["sumas"]                # módulo 3: la suma de z_i z_j por banda
NIVEL4 = f"{inf['nivel_pct']:g}"  # módulo 4: el nivel de los intervalos, de R


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
# El marco más estrecho —el rectángulo de las muertes— y las filas de la tabla.
MARCO_MIN = mc1[0]
FILAS_MARCOS = "\n".join(
    f"          <tr><th scope=\"row\">{m['marco'][0].upper() + m['marco'][1:]}</th>"
    f"<td>{n(m['pct_longitud'], 2)}</td><td>{n(m['pct_calle_broad'])}</td>"
    f"<td>{n(m['razon_sobre_calle'])}</td><td>{n(m['z_binomial'], 2)}</td></tr>"
    for m in mc1)
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

      <p><span data-afirma="c1-m1-01">Londres, verano de 1854. En el Soho mueren <strong>{sn['n_muertes']}</strong> personas de cólera en poco más
        de un mes. La teoría médica del momento culpa al aire viciado. John Snow sospecha del agua, no tiene con qué
        demostrarlo, y hace algo que entonces no era un método: <em>dibuja los muertos en un plano</em>, con las
        <strong>{sn['n_bombas']}</strong> bombas públicas del barrio encima
        <cite class="cita" data-ref="baddeley2015spatial" data-loc="p. 261"></cite></span>.</p>

      <p>Ese plano es el primer objeto de este curso, y conviene mirarlo antes de definir nada. Ponlo en
        <em>Broad Street contra el resto</em> y fíjate en dónde cae la mancha.</p>

      <div class="simulador" data-simulador="snow-mapa">
        <h4><i class="fas fa-map-location-dot" aria-hidden="true"></i> El mapa de Snow, capa a capa</h4>
        <p class="simulador-intro">Las <strong>{sn['n_segmentos']}</strong> calles del Soho de fondo, las
          {sn['n_muertes']} muertes digitalizadas por Dodson y Tobler (NCGIA, 1992) y las {sn['n_bombas']} bombas en
          rombo. Conmuta entre colorear por bomba más próxima y resaltar solo Broad Street. Las líneas a
          trazos parten el plano en las celdas de las bombas: dentro de cada celda, la bomba más próxima es
          la suya.</p>
        <div class="simulador-controles"></div>
        <div class="geomapa" data-geomapa="cap1-snow"></div>
        <div class="simulador-lectura"></div>
      </div>

      <p>La cifra que sostiene el mapa: de las {sn['n_muertes']} muertes,
        <strong>{sn['n_mas_cerca_broad']}</strong> tienen la bomba de Broad Street como la más próxima. Eso es el
        <strong>{n(sn['pct_mas_cerca_broad'])}&nbsp;%</strong>. Como referencia sirve un <strong>reparto
        ingenuo</strong>: si las muertes se repartieran por igual entre las {sn['n_bombas']} bombas, a cada una le
        tocaría el {n(sn['pct_esperado_uniforme'])}&nbsp;%, y Broad Street concentra
        <strong>{n(sn['razon_sobre_uniforme'])} veces</strong> esa parte. El reparto es ingenuo porque ignora dos
        cosas: que las bombas no sirven áreas del mismo tamaño dentro del plano y que no las usa la misma población.
        La primera se puede medir con lo que el plano trae; la segunda, no.</p>

      <p>La primera se mide con una <strong>prueba de aleatorización</strong>. Se recolocan las
        {sn['n_muertes']} muertes al azar sobre las calles del plano —cada una en un punto sorteado con
        probabilidad proporcional a la longitud de calle— y se vuelve a calcular el mismo porcentaje: cuántas
        tienen la bomba de Broad Street como la más próxima. Repetido {ent(al['n_recolocaciones'])} veces, eso da
        la distribución de ese porcentaje cuando lo único que decide dónde cae una muerte es cuánta calle hay en
        cada sitio. Esa es la <strong>hipótesis nula</strong>, y el histograma la dibuja junto al dato.</p>

      <div class="simulador" data-simulador="snow-nula">
        <h4><i class="fas fa-shuffle" aria-hidden="true"></i> La prueba de aleatorización: el dato frente a
          {ent(al['n_recolocaciones'])} repartos al azar</h4>
        <p class="simulador-intro">En gris, cuántas de las {ent(al['n_recolocaciones'])} recolocaciones dieron
          cada porcentaje de muertes más cerca de Broad Street. La línea naranja es el porcentaje observado, y la
          de trazos, el reparto ingenuo. La curva fina es una binomial: como cada muerte se recoloca por
          separado y cae en la parte de Broad Street con la misma probabilidad, aquí la nula tiene además
          fórmula, y sirve de control de que la simulación está bien hecha. Se simula de todos modos porque recolocar es el procedimiento que
          sigue sirviendo cuando no hay fórmula. Con <strong>acercar a la nula</strong> el eje se cierra sobre el
          histograma y el dato se sale del gráfico por la derecha.</p>
        <div class="simulador-controles"></div>
        <div class="grafico-wrapper" style="{ALTO_T24}">
          <canvas aria-label="Histograma del porcentaje de muertes cuya bomba más próxima es Broad Street en {ent(al['n_recolocaciones'])} recolocaciones al azar sobre las calles: va del {n(al['min_nula_pct'])} al {n(al['max_nula_pct'])} por ciento, con media {n(al['media_nula_pct'])}. Una línea vertical marca el {n(sn['pct_mas_cerca_broad'])} por ciento observado, muy a la derecha de todo el histograma" role="img"></canvas>
        </div>
        <div class="simulador-lectura"></div>
      </div>

      <p>A Broad Street le toca el <strong>{n(al['pct_calle_broad'])}&nbsp;%</strong> de la longitud de calle del
        plano: es la parte de calle que queda más cerca de esa bomba que de cualquier otra, y es la media de la
        nula. Se calcula sin simular, tramo a tramo, y las recolocaciones la reproducen: promedian
        {n(al['media_nula_pct'])}&nbsp;%, con un error de Monte Carlo de {n(al['emc_media_pct'])}. Es algo más que
        el {n(sn['pct_esperado_uniforme'])}&nbsp;% del reparto ingenuo: con el plano entero, el observado es
        <strong>{n(al['razon_sobre_calle'])} veces</strong> lo que le tocaría por calle, donde el reparto ingenuo
        decía {n(sn['razon_sobre_uniforme'])}.</p>

      <p>Ninguna de las {ent(al['n_recolocaciones'])} recolocaciones llega al
        {n(sn['pct_mas_cerca_broad'])}&nbsp;% observado. La mayor da {n(al['max_nula_pct'])}&nbsp;%, y el dato queda
        a {n(al['z_observado'])} desviaciones típicas de la media de la nula. El valor p de la prueba es, por tanto,
        \\(p \\le 1/(B + 1) = {n(al['p_cota'])}\\), con \\(B = {ent_mate(al['n_recolocaciones'])}\\)
        recolocaciones: el dato cuenta como una más. Se da como cota y no como cero: la simulación no puede
        afirmar nada más fino que una entre \\(B + 1\\). La binomial, que es la fórmula de esta misma
        nula, da una cifra mucho menor. No se publica porque un valor p tan extremo solo valdría si el modelo
        fuera exacto —muertes independientes entre sí, este marco del plano y no otro—, y no lo es. La cota
        dice lo que hace falta sin aparentar una precisión que el modelo no tiene.</p>

      <p>La parte de calle, en cambio, no es una cifra firme: depende de hasta dónde llega el plano. Las
        calles digitalizadas cubren bastante más terreno que las muertes, y cuanta más calle lejana entra en
        la cuenta, menor es la parte que le toca a Broad Street. La tabla rehace la cuenta con las calles
        recortadas al rectángulo que encierra las muertes y a ese rectángulo ensanchado; las distancias van
        en las unidades del plano, que no tiene escala publicada.</p>

      <table>
        <caption>La parte de calle de Broad Street según el marco que se le ponga al plano. La última
          columna es la distancia del dato a lo que la nula espera, en desviaciones típicas de la
          binomial.</caption>
        <thead>
          <tr><th scope="col">Calles que entran</th><th scope="col">% de la calle del plano</th>
            <th scope="col">Parte de Broad St (%)</th><th scope="col">Observado / parte</th>
            <th scope="col">Desviaciones típicas</th></tr>
        </thead>
        <tbody>
{FILAS_MARCOS}
        </tbody>
      </table>

      <p>Con solo las calles del rectángulo de las muertes, a Broad Street le toca el
        {n(MARCO_MIN['pct_calle_broad'])}&nbsp;% y el observado es {n(MARCO_MIN['razon_sobre_calle'])} veces esa
        parte, no {n(al['razon_sobre_calle'])}. Lo que no cambia con el marco es el rechazo: también con el más
        estrecho el dato queda a {n(MARCO_MIN['z_binomial'], 2)} desviaciones típicas de lo que la nula espera.
        Cuánta de la concentración explica la calle no se puede decir con una sola cifra. Que no la explica
        entera, sí.</p>

      <div class="note">
        <p><strong>Lo que esa nula permite concluir, y lo que no.</strong> Permite concluir una cosa:
          la concentración alrededor de Broad Street no se explica por la cantidad de calle que esa bomba tiene
          más cerca que las demás. No permite más. La nula no sabe cuánta gente vivía en cada tramo: dos tramos
          que miden lo mismo cuentan igual, estén llenos de viviendas o no. Tampoco sabe de qué bomba bebía cada
          quien, que no tiene por qué ser la más próxima. Y no fija el marco: qué calles entran lo decide
          hasta dónde se dibujó el plano, no el brote.</p>
        <p style="margin-bottom:0;">Además recoloca cada muerte por separado, como si las muertes fueran
          independientes entre sí. Varias muertes de una misma casa no lo son, y con muertes agrupadas la nula
          sería más ancha que la del histograma. Con el dato a {n(al['z_observado'])} desviaciones típicas eso no
          cambia la conclusión; sí es una razón para leer el valor p como una cota y no como una medida fina.</p>
      </div>

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
        la retirada del mango. El dato no permite atribuírselo: el
        <strong>{n(sn['pct_ataques_antes_mango'])}&nbsp;%</strong> de los ataques había ocurrido <em>antes</em> de
        ese día, y desde el pico del {sn['fecha_pico']} —{sn['ataques_pico']} ataques— hasta el
        {sn['fecha_mango']} —{sn['ataques_dia_mango']}— ya habían caído un
        <strong>{n(sn['caida_hasta_mango_pct'])}&nbsp;%</strong>. Los ataques ya venían cayendo. Tampoco permite
        decir lo contrario, que la retirada no sirviera de nada: entre beber el agua y enfermar pasa un tiempo, así
        que parte de los ataques de los días siguientes corresponde a exposiciones anteriores a la retirada, y la
        curva no puede medir su efecto.</p>

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
#
# LA TABLA DE LOS TRES TIPOS SE DESPLAZA DENTRO DE SU CAJA EN EL TELÉFONO.
# A ≤768 px la plantilla pone toda tabla en `display:block` y a
# `max-content`: ninguna celda partía, la tabla medía 1 304 px, y el MathML
# de KaTeX de la λ —en posición absoluta— escapaba del recorte del
# envoltorio y llevaba la página a 416 px en un visor de 375. Es la receta
# de la tabla ancha del módulo 9 del capítulo 4: `width:100%` anula el
# `max-content`, `position:relative` mete el MathML dentro del envoltorio,
# y `overflow:visible` deja que el `sticky` de la columna de preguntas se
# agarre al envoltorio que desplaza, así que al leer una fila de lado se
# sigue viendo qué pregunta contesta. La esquina va fija también, con un
# `z-index` más, para que las cabeceras de columna pasen por debajo.
# El mínimo es `min-content` y no un número de rem, como en el capítulo 4.
# Con tres columnas no hace falta impedir que se aplasten: ninguna celda
# baja de su palabra más larga, y eso deja la tabla en 507 px en el
# teléfono, donde cada tipo —de 114 a 142 px— cabe entero junto a la
# pregunta fija en los 303 px del envoltorio. Sin mínimo, la caja se
# quedaría en esos 303 y el contenido le sobresaldría. Y un mínimo en rem
# se pasaba de largo en las tabletas: con 40rem la tabla medía 640 px y
# se desplazaba donde antes cabía (hacia 1 100 px de pantalla, con la
# barra lateral). `min-content` no crea desplazamiento que el contenido no
# imponga ya. En escritorio la tabla ocupa sus 812 px, como antes.
FIJA = "position:sticky; left:0; z-index:1;"
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
        <p>Es la <strong>densidad de puntos</strong> del proceso que generó el patrón: cuántos se esperan por
          unidad de área. Si el proceso es <em>homogéneo</em> —la misma densidad en todas partes—, el número de
          puntos que caen en una región \\(B\\), \\(N(B)\\), tiene una esperanza proporcional al área de la
          región:</p>
        <p style="text-align:center;">$$E[N(B)] = \\lambda\\,|B|$$</p>
        <p>Esa constante \\(\\lambda\\) es la intensidad. Es una propiedad del proceso y no se observa: se
          <strong>estima</strong>. Con \\(n\\) puntos sobre una ventana \\(W\\) de área \\(|W|\\), el estimador
          es</p>
        <p style="text-align:center;">$$\\hat{{\\lambda}} = \\frac{{n}}{{|W|}}$$</p>
        <p>Con los pinos, \\(n = {pc['japanesepines']['n']}\\) y \\(|W| = {pc['japanesepines']['area']}\\), así que
          \\(\\hat{{\\lambda}} = {pc['japanesepines']['lambda']}\\) árboles por unidad de área. Se lee como cualquier
          densidad —habitantes por km², árboles por hectárea— y, como cualquier densidad, <strong>tiene
          unidades</strong>: el mismo patrón medido en km² o en hectáreas da dos números distintos sin que se
          mueva un solo punto. Cuando en este curso veas un \\(\\lambda\\) suelto, pregunta siempre «¿por unidad de
          qué?».</p>
        <p style="margin-bottom:0;">Y ahora la parte incómoda, que es la razón de presentarla aquí y no en una
          tabla de fórmulas. El numerador lo pone el dato: los puntos están donde están y son los que son. El
          denominador lo pones <strong>tú</strong>, al decidir dónde acaba la ventana. \\(\\hat{{\\lambda}}\\) es
          de las pocas cifras del curso que se puede cambiar sin tocar el dato: mueve el borde y cambia, sin que se
          mueva un solo pino. Lo que cambia es la <em>estimación</em>. Si el proceso es homogéneo, su intensidad
          no se entera de dónde se dibuje el borde; si no lo es, cada borde estima además otra cosa, la intensidad
          media de la región que encierra, y la nota que cierra este módulo lo mide. Con los pinos no se nota, porque la ventana viene con ellos. Con el mapa que
          sigue, sí.</p>
      </div>

      <div class="geomapa" data-geomapa="cap1-bogota"></div>

      <p>Bogotá hace lo contrario, y por eso va al lado. Las <strong>{ent(co['puntual']['n'])}</strong> sedes no
        están tiradas al azar: dibujan las calles, y con ellas la densidad de la ciudad. Aquí sí hay algo que
        explicar. Y conviene mirar el borde, que es donde este mapa se pone interesante:
        <strong>{ent(co['puntual']['n_urbana'])}</strong> de las {ent(co['puntual']['n'])} caen dentro del
        perímetro urbano y <strong>{ent(co['puntual']['n_dc'])}</strong> dentro del Distrito Capital. El mismo
        patrón admite al menos tres bordes distintos, y elegir no es cuestión de gusto: la <em>ventana</em> de un
        patrón puntual es, por definición, una región sobre la que el dato es <strong>exhaustivo</strong> —aquella
        donde se puede afirmar que no falta ningún punto—. Con ese criterio valen las dos que se acaban de
        nombrar, el perímetro urbano y el Distrito: si el dato es exhaustivo en el Distrito, lo es en cualquier
        región contenida en él, y el perímetro urbano lo está. Lo que no vale es una ventana que se salga de la
        región donde el dato es exhaustivo, porque el área que sobra entra en el denominador sin que nadie haya
        buscado puntos en ella. Entre dos ventanas válidas se elige por la región que se quiere describir, y las
        dos cifras de arriba ya avisan de que no describen la misma: hay sedes dentro del Distrito y fuera del
        perímetro. La nota que cierra este módulo mide cuánto cambia la respuesta.</p>

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

      <p>El mapa del Mosa parece manchas de color hasta que uno sabe por dónde va el río. Las dos líneas del
        mapa son sus orillas. El zinc va de
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
        zinc. Simplemente no se midieron. En el marco de este curso —el <em>basado en el modelo</em>, que el
        módulo 10 separa del basado en el diseño— lo aleatorio es el propio campo \\(Z(\\cdot)\\): el mapa entero
        de temperaturas es una realización de un proceso, y las \\(n\\) localizaciones donde se mide se toman como
        fijas. Si se volviera a tomar el dato, lo que saldría distinto serían <strong>los valores</strong>, en esos
        puntos y en todos los demás. Que haya un valor en todo punto, y no solo donde se midió, es lo que da
        permiso para predecir, y es justo lo que los otros dos tipos no tienen. La otra lectura —el campo quieto
        y lo aleatorio, dónde se mide— es la del muestreo, y se deja para el módulo 10.</p>

      <p>Vuelve ahora al párrafo del principio. Los seis mapas se parecen bastante entre sí —puntos y polígonos de
        colores— y sin embargo la pregunta «¿qué saldría distinto si volviéramos a tomar el dato?» los ha partido
        limpiamente en tres: cambian las <em>posiciones</em>, cambian los <em>valores</em> sobre unidades fijas, o
        cambian los valores de un <em>campo</em> que existe en todo punto y se observa en unos pocos. La tabla
        resume lo que acabas de hacer.</p>

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
      <table class="tabla-matriz" style="position:relative; overflow:visible; width:100%; min-width:min-content;">
        <caption>Los tres tipos de dato espacial: qué es aleatorio, qué se estima y en qué capítulo se desarrolla.</caption>
        <thead>
          <tr><td style="position:sticky; left:0; z-index:2;"></td>
            <th scope="col">Patrón puntual</th>
            <th scope="col">Dato de área</th>
            <th scope="col">Geoestadístico</th></tr>
        </thead>
        <tbody>
          <tr><th scope="row" style="{FIJA}">Qué es aleatorio</th>
            <td>La <strong>localización</strong> de los eventos, y cuántos hay</td>
            <td>El <strong>valor</strong>, sobre unidades territoriales fijas</td>
            <td>El <strong>valor</strong> de algo que existe en todo punto y se observa en unos pocos</td></tr>
          <tr><th scope="row" style="{FIJA}">Qué se estima</th>
            <td>Intensidad \\(\\lambda\\), agregación o regularidad</td>
            <td>Autocorrelación, modelos SAR/SEM</td>
            <td>Variograma, predicción por kriging</td></tr>
          <tr><th scope="row" style="{FIJA}">Canónico</th>
            <td>{pc['japanesepines']['nombre']} ({pc['japanesepines']['n']})</td>
            <td>{ac['nombre']} ({ac['n']})</td>
            <td>{gc['nombre']} ({gc['n']})</td></tr>
          <tr><th scope="row" style="{FIJA}">Colombiano</th>
            <td>{co['puntual']['nombre']} ({ent(co['puntual']['n'])})</td>
            <td>{co['area']['nombre']} ({ent(co['area']['n'])})</td>
            <td>{co['geo']['nombre']} ({co['geo']['n']})</td></tr>
          <tr><th scope="row" style="{FIJA}">Capítulos</th>
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
        <p>En los tres casos hay un dominio \\(D \\subset \\mathbb{{R}}^2\\) y algo aleatorio sobre él. Lo que
          cambia es <strong>qué es aleatorio</strong>:</p>
        <ul>
          <li><strong>Patrón puntual:</strong> no hay ningún valor \\(Z(s)\\) que observar. Lo aleatorio es el
            propio conjunto de puntos \\(\\{{s_1, \\dots, s_N\\}}\\) dentro de \\(D\\) —que aquí es fijo: la
            <em>ventana</em>—, con \\(N\\) también aleatorio. Dicho de otro modo, lo aleatorio es el conteo
            \\(N(B)\\), el número de puntos que caen en cada región \\(B\\) de la ventana.</li>
          <li><strong>Dato de área:</strong> los índices son un conjunto <em>fijo y numerable</em> de unidades
            \\(A_1, \\dots, A_n\\) —los municipios—, y aleatorio es el valor \\(Z(A_i)\\) de cada una.</li>
          <li><strong>Geoestadístico:</strong> hay un valor \\(Z(s)\\) para <em>todo</em> \\(s \\in D\\) —una
            temperatura en cada punto de Colombia—. Aleatorio es ese campo entero, y solo se observa en \\(n\\)
            localizaciones, que se toman como fijas.</li>
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
          moverla. La intensidad estimada \\(\\hat{{\\lambda}} = n/|W|\\) de las sedes de
          Bogotá vale <strong>{n(co['puntual']['lambda_urbana'])}</strong> sedes/km² sobre el perímetro urbano
          ({n(co['puntual']['area_urbana_km2'], 1)} km²) y <strong>{n(co['puntual']['lambda_dc'])}</strong> sobre el
          Distrito Capital completo ({n(co['puntual']['area_dc_km2'], 1)} km², Sumapaz incluido). Mismo dato, y
          un factor de <strong>{n(co['puntual']['factor_lambda'])}</strong> según dónde se ponga el borde.
          Y no son dos estimaciones rivales de lo mismo, ni una buena y otra mala: las dos ventanas son válidas, y
          cada cociente \\(n/|W|\\) estima la intensidad <em>media</em> de su propia región,
          \\(\\frac{{1}}{{|W|}}\\int_W \\lambda(s)\\,ds\\), donde \\(\\lambda(s)\\) es la intensidad en cada
          sitio. El factor no mide un error: mide cuánto cambia la intensidad de un sitio a otro —la
          <em>inhomogeneidad</em> del patrón—, porque el Distrito añade al perímetro un territorio extenso y casi
          sin sedes. Elegir ventana es elegir qué región se describe. El capítulo 4 empieza justo ahí.</p>
      </div>
""" + CIERRE


# =====================================================================
# MÓDULO 3 · La primera ley de Tobler
# =====================================================================
# R2 · T2.4: la envolvente de permutación. Lo que la prosa dice de cada
# banda —«por encima», «dentro», «por debajo»— se LEE de `posicion`, que
# es de R, y los recuentos de aquí abajo son longitudes de listas, no
# aritmética sobre cifras. Las guardas de `main()` atan cada frase a esas
# posiciones.
POS3 = {"encima": "por encima", "dentro": "dentro", "debajo": "por debajo"}
_pos_t = [e["posicion"] for e in env3["ideam"]]
_pos_r = [e["posicion"] for e in env3["residuos_altitud"]]
# Cuántas bandas seguidas, desde la primera, quedan por encima.
N_ENCIMA3 = next((i for i, x in enumerate(_pos_t) if x != "encima"), len(_pos_t))
N_ENCIMA3_RES = next((i for i, x in enumerate(_pos_r) if x != "encima"), len(_pos_r))
if "debajo" not in _pos_t or not 0 < N_ENCIMA3_RES < len(_pos_r):
    sys.exit("PARADO: tobler.envolvente ya no trae una banda de la temperatura por debajo de su "
             "franja, o los residuos no pasan de «encima» a otra cosa: el módulo 3 lo afirma.")
I_DEB3 = _pos_t.index("debajo")
B_DEB3, E_DEB3 = tb["ideam"]["bandas"][I_DEB3], env3["ideam"][I_DEB3]
FILAS_ENV3 = "\n".join(
    f"          <tr><th scope=\"row\">{b['d1']}–{b['d2']}</th><td>{n(b['I'])}</td>"
    f"<td>{n(e['lo'])} a {n(e['hi'])}</td><td>{POS3[e['posicion']]}</td>"
    f"<td>{n(r['I'])}</td><td>{n(f['lo'])} a {n(f['hi'])}</td><td>{POS3[f['posicion']]}</td></tr>"
    for b, e, r, f in zip(tb["ideam"]["bandas"], env3["ideam"],
                          tb["residuos_altitud"]["bandas"], env3["residuos_altitud"]))
MOD3 = cabecera(
    3, "La primera ley de Tobler", "Tobler's first law",
    "Medir la primera ley en vez de citarla, con un control que la niega y "
    "un caso donde lo que parece dependencia es otra cosa.") + f"""
      <p><span data-afirma="c1-m3-01">La cita es de 1970 y es la frase más repetida del área: <em>«todo está
        relacionado con todo lo demás, pero las cosas cercanas están más relacionadas que las lejanas»</em>
        <cite class="cita" data-ref="tobler1970computer" data-via="pebesma2023spatial" data-loc="§15.1"></cite></span>. Dicha así no es una ley: es una impresión.
        Lo que la convierte en algo utilizable es que se puede <strong>medir</strong>, y medirla es lo que hace el
        correlograma.</p>

      <p>Toma las <strong>{co['geo']['n']}</strong> estaciones climáticas del IDEAM con normal 1991-2020. Agrupa
        todas las parejas de estaciones por su distancia y calcula, banda a banda, cuánto se parecen sus
        temperaturas. Si Tobler tiene razón, el parecido tiene que decaer.</p>

      <div class="simulador" data-simulador="correlograma">
        <h4><i class="fas fa-signal" aria-hidden="true"></i> El correlograma: la primera ley, medida</h4>
        <p class="simulador-intro">Índice de Moran por bandas de distancia. El eje horizontal va en
          kilómetros y cada punto está en el centro de su banda, así que las bandas cortas quedan juntas a
          la izquierda: es la escala real del decaimiento. La franja gris es la
          <strong>envolvente de permutación</strong>: en cada banda, el intervalo donde cae el
          {env3['nivel_pct']:g}&nbsp;% de las {ent(env3['nperm'])} I que salen al repartir los mismos valores
          al azar entre las mismas estaciones. La línea de puntos es la media de esas I, E[I] bajo
          permutación. Tres series se pueden <strong>encender y apagar</strong>: el dato real, los residuos
          tras quitar la altitud y <strong>una</strong> permutación suelta, que es un reparto al azar como
          los que forman la franja.</p>
        <div class="simulador-controles"></div>
        <div class="grafico-wrapper" style="{ALTO_T24}">
          <canvas aria-label="Índice de Moran de la temperatura de las estaciones del IDEAM por bandas de distancia, de 0 a {tb['ideam']['bandas'][-1]['d2']} kilómetros, con la envolvente de permutación del {env3['nivel_pct']:g} por ciento. La temperatura queda por encima de la envolvente en las {N_ENCIMA3} bandas hasta {tb['ideam']['bandas'][N_ENCIMA3 - 1]['d2']} kilómetros, por debajo entre {B_DEB3['d1']} y {B_DEB3['d2']} y dentro en la última. Se dibujan también los residuos tras quitar la altitud y una permutación suelta, que queda dentro en todas las bandas" role="img"></canvas>
        </div>
        <p class="simulador-intro" style="margin-top:0.75rem;">La franja dibujada es la de la temperatura;
          si la única serie encendida son los residuos, es la suya, que es casi la misma. Con
          <strong>acercar a la franja</strong> el eje vertical se cierra sobre ella: es la vista para leer
          las bandas largas, donde la franja es estrecha.</p>
        <div class="simulador-lectura"></div>
      </div>

      <p>La primera banda ({tb['ideam']['bandas'][0]['d1']}–{tb['ideam']['bandas'][0]['d2']} km) da
        <strong>{n(tb['ideam']['bandas'][0]['I'])}</strong>, muy por encima de su franja, que va de
        {n(env3['ideam'][0]['lo'])} a {n(env3['ideam'][0]['hi'])}. Las {N_ENCIMA3} bandas hasta
        {tb['ideam']['bandas'][N_ENCIMA3 - 1]['d2']} km quedan todas por encima: a esas distancias dos estaciones
        se parecen más de lo que se parecerían con las temperaturas repartidas al azar. La última del
        gráfico ({tb['ideam']['bandas'][-1]['d1']}–{tb['ideam']['bandas'][-1]['d2']} km) da
        <strong>{n(tb['ideam']['bandas'][-1]['I'])}</strong> y cae dentro de la suya, de
        {n(env3['ideam'][-1]['lo'])} a {n(env3['ideam'][-1]['hi'])}: ya no se distingue de un reparto al azar,
        cuyo valor esperado es <strong>{n(tb['ideam']['esperado'], 6)}</strong>. Eso es la primera ley con una
        cifra delante: el parecido es grande entre estaciones cercanas y se pierde con la distancia.</p>

      <p>El eje acaba en {ma3['d1']} km y la red no. La pareja de estaciones más alejada está a
        {ent(ma3['d_max'])} km, y quedan fuera del gráfico {ent(ma3['n_pares'])} de las
        {ent(ma3['n_pares_total'])} parejas, el {n(ma3['pct_pares'])}&nbsp;%. Tratadas como una banda más, dan
        \\(I = {n(ma3['I'])}\\), por debajo de su franja, que va de {n(ma3['lo'])} a {n(ma3['hi'])}. No se
        dibujan porque el eje tendría que llegar casi al triple y las bandas cortas, que son las que enseñan
        la ley, se quedarían sin sitio. Pero cuentan, y lo que sigue explica por qué salen negativas.</p>

      <p>Entre las bandas que quedan por encima y la que cae dentro hay una, además, por debajo. De
        {B_DEB3['d1']} a {B_DEB3['d2']} km la I vale <strong>{n(B_DEB3['I'])}</strong>, y la franja ahí va de
        {n(E_DEB3['lo'])} a {n(E_DEB3['hi'])}. Es autocorrelación <em>negativa</em>: a esa distancia dos
        estaciones se parecen menos que dos tomadas al azar. No contradice la primera ley: es su
        contrapartida, y que la haya es obligado. Las temperaturas están centradas en la media de todas las
        estaciones, y eso fija una cuenta. Sumados los productos \\(z_i z_j\\) de todas las parejas, y
        medidos en unidades de \\(\\tfrac{{1}}{{2}}\\sum_i z_i^2\\), el total es exactamente \\(-1\\),
        con cualquier dato. Las parejas a menos de {B_DEB3['d1']} km suman {n(su3['cortas'])}; las demás
        tienen que sumar, por tanto, {n(su3['largas'])}. Con las bandas cortas tan positivas,
        tiene que haber bandas negativas. Lo que el dato decide es dónde caen: {n(su3['bandas'][I_DEB3]['suma'])} en la
        de {B_DEB3['d1']}–{B_DEB3['d2']} km, {n(su3['bandas'][-1]['suma'])} en la de
        {tb['ideam']['bandas'][-1]['d1']}–{tb['ideam']['bandas'][-1]['d2']} km y {n(su3['mas_alla'])} más
        allá de {ma3['d1']} km. La franja no avisa de esto, porque permutar deshace también el parecido a
        corta distancia: compara cada banda con un reparto en el que las demás tampoco tienen nada.</p>

      <p>La franja es <strong>puntual</strong>: cada banda tiene su propio {env3['nivel_pct']:g}&nbsp;%. Con
        {len(tb['ideam']['bandas'])} bandas no es raro que alguna se salga por puro azar: en el
        {n(env3['pct_alguna_fuera'])}&nbsp;% de las {ent(env3['nperm'])} permutaciones se sale al menos una.
        Una banda suelta que asoma apenas fuera de la franja no prueba nada. Aquí no es el caso: la
        temperatura se sale en {env3['n_fuera_ideam']} de las {len(tb['ideam']['bandas'])}.</p>

      <div class="definition">
        <h3>El índice de Moran, que es la herramienta de todo el curso</h3>
        <p>Con \\(n\\) unidades, valores \\(z_i\\) centrados y una matriz de pesos \\(W\\) que declara quién es vecino
          de quién,</p>
        <p style="text-align:center;">$$I = \\frac{{n}}{{S_0}} \\cdot
          \\frac{{\\sum_i \\sum_j w_{{ij}} z_i z_j}}{{\\sum_i z_i^2}},
          \\qquad S_0 = \\sum_i \\sum_j w_{{ij}}, \\qquad E[I] = -\\frac{{1}}{{n-1}}$$</p>
        <p>Con las {co['geo']['n']} estaciones, \\(E[I] = {n(tb['ideam']['esperado'], 6)}\\). Es el valor
          esperado bajo la hipótesis nula de <strong>permutación</strong>: los mismos valores, repartidos al azar
          entre las mismas posiciones. Lo que queda un poco por debajo de cero bajo esa nula es
          <strong>\\(E[I]\\)</strong>, no \\(I\\), que en cada reparto sale distinta. Y queda por debajo por el
          <strong>centrado</strong>: los \\(z_i\\) suman cero, así que los productos \\(z_i z_j\\) entre unidades
          distintas suman \\(-\\sum_i z_i^2\\), y su promedio es negativo con cualquier dato. El capítulo 7 hace
          la cuenta entera.</p>
        <p style="margin-bottom:0;">Esa referencia cambia en las bandas donde hay estaciones sin vecinos. En
          la de {b0['d1']}–{b0['d2']} km solo <strong>{b0['n_con_vecinos']}</strong> de las {co['geo']['n']}
          tienen alguna otra a esa distancia. <code>spdep</code> las deja fuera al contar —multiplica por
          \\(n' = {b0['n_con_vecinos']}\\) en vez de por \\(n\\)—, pero siguen dentro del centrado y de la suma de
          cuadrados, así que la esperanza por permutación de la \\(I\\) que publica es
          \\(-n'/(n(n-1)) = {n(b0['esperado'], 6)}\\). Permutando de verdad las temperaturas
          {ent(pb1['nperm'])} veces, la media sale \\({n(pb1['media'], 6)}\\), con un error de Monte Carlo de
          {n(pb1['emc'], 6)}. La línea de referencia del gráfico está dibujada así, banda a banda.
          <code>moran.test</code> imprime como esperanza otra cifra, \\(-1/(n'-1) = {n(b0['esperado_programa'], 6)}\\):
          es la convención del programa, no la media por permutación de la \\(I\\) que calcula.</p>
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
        <strong>{n(tb['permutado']['bandas'][0]['I'])}</strong>. Eso es una permutación, y una sola no dice
        cuánto puede moverse la I por puro azar: lo dice la franja, que reúne {ent(env3['nperm'])}. La
        permutación suelta queda dentro de la franja en las {len(tb['ideam']['bandas'])} bandas. Si el
        correlograma del dato real quedara también dentro, la estructura que se está midiendo la estaría
        poniendo la geometría de la red y no el fenómeno.</p>

      <p>La tabla reúne las {len(tb['ideam']['bandas'])} bandas, cada serie con su propia franja. Los residuos
        tras quitar la altitud se leen como la temperatura en las {N_ENCIMA3_RES} primeras; entre
        {tb['ideam']['bandas'][N_ENCIMA3_RES]['d1']} y {tb['ideam']['bandas'][N_ENCIMA3_RES]['d2']} km ya caen
        dentro de su franja, y en las dos últimas, por debajo. Quitada la altitud, la dependencia a corta
        distancia sigue ahí y se agota antes. La franja de los residuos es una aproximación: salen de un
        ajuste y no son intercambiables entre estaciones como lo son los datos.</p>

      <table>
        <caption>Índice de Moran por banda y envolvente de permutación del {env3['nivel_pct']:g} %
          (cuantiles del {env3['cuantil_lo_pct']:g} y del {env3['cuantil_hi_pct']:g} % de
          {ent(env3['nperm'])} permutaciones), para la temperatura y para sus residuos tras quitar la
          altitud. La envolvente es puntual: vale banda a banda.</caption>
        <thead>
          <tr><th scope="col">Banda (km)</th><th scope="col">I, temperatura</th>
            <th scope="col">Su franja</th><th scope="col">Queda</th>
            <th scope="col">I, residuos</th><th scope="col">Su franja</th><th scope="col">Queda</th></tr>
        </thead>
        <tbody>
{FILAS_ENV3}
        </tbody>
      </table>

""" + tabs(
    "El correlograma por bandas, en R y en Python",
    """library(sf); library(spdep)

est &lt;- st_read("datos/procesado/colombia_estaciones_clima.gpkg", quiet = TRUE)

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
        <p style="margin-bottom:0;"><span data-afirma="c1-m3-02">Ese cociente \\(R\\) es el <strong>índice de
          Clark-Evans</strong> <cite class="cita" data-ref="clark1954distance" data-via="baddeley2015spatial"
          data-loc="p. 258"></cite>, y es
          una división entre dos distancias: cuánto se separan los puntos de verdad, dividido entre cuánto se
          separarían por puro azar. De ahí le vienen sus dos propiedades: no tiene unidades, y su referencia es el
          <strong>1</strong>. Por debajo de 1 los puntos están <em>más cerca</em> de lo que daría el azar
          —agregación—; por encima, más lejos —regularidad—.</span> Con los {pc['japanesepines']['n']} pinos sobre su
          ventana de área {pc['japanesepines']['area']} sale \\(\\hat{{\\lambda}} = {pc['japanesepines']['lambda']}\\), y con ella
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
          retórica: \\(R\\) se construye <em>solo</em> con la distancia al vecino <strong>más próximo</strong>, y de
          ella solo con la media. Es un único número, y en un único número dos estructuras opuestas pueden
          compensarse.</p>
        <p style="margin-bottom:0;">El caso que lo rompe es corriente en ecología, que es de donde salen las
          secuoyas: árboles que compiten con el de al lado y por eso se separan a corta distancia, pero que
          crecen en manchas grandes marcadas por el suelo o la humedad. Las dos cosas tiran de \\(R\\) en sentidos
          opuestos. La repulsión alarga la distancia al vecino más próximo y <em>sube</em> \\(R\\). Las manchas
          hacen lo contrario, aunque sean mucho mayores que esa distancia: concentran los puntos, la densidad
          dentro de cada mancha es mayor que la del conjunto de la ventana —que es la que entra en la distancia
          esperada—, y los vecinos quedan más cerca de lo que esa densidad media anuncia. Eso <em>baja</em>
          \\(R\\). Los dos efectos pueden cancelarse en la media, y \\(R\\) quedarse en 1 sobre un patrón que a
          la escala de las manchas está claramente agregado. Que \\(R\\) valga 1 no prueba que el patrón sea
          aleatorio: prueba que la distancia <em>media</em> al vecino más próximo es la que daría el azar con
          esa densidad.</p>
      </div>

      <p style="margin-bottom:0;">Y ahí está la razón de dividir por la distancia esperada en vez de comparar las
        observadas: descontada la densidad, lo que queda en \\(R\\) es la <em>disposición</em> —pero resumida en
        un solo número—. El capítulo 4 sustituye este único número por las funciones \\(G\\), \\(F\\), \\(K\\) y \\(g\\),
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
# La fila gemela del módulo 5 —el n_eff exacto y el de la fórmula con su rho
# medio—, buscada por el mismo valor y no por posición, por lo mismo.
e4 = next((e for e in ne["exacto_campo"] if e["phi"] == r4["phi"]), None)
if e4 is None:
    sys.exit("PARADO: n_efectivo.exacto_campo ya no trae la fila de phi = 4, y el "
             "módulo 5 compara sobre ella el n_eff exacto con el de la fórmula.")
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
        <p class="simulador-intro">El deslizador recorre el alcance de la correlación. Las curvas no se mueven,
          y es a propósito: el alcance ya es el eje horizontal, así que están dibujadas todas a la vez, en dos
          paneles que comparten ese eje. Arriba van los dos errores estándar y abajo, la cobertura, cada
          magnitud en su escala. Lo que se mueve es el marcador que señala el alcance elegido, el campo de
          debajo y la lectura. El campo es un ejemplo sobre la misma retícula de {inf['k']}×{inf['k']} de la
          simulación: en \\(\\phi = {ci['phi']}\\) es la primera de las {ent(inf['nrep'])} réplicas que miden
          las cifras, y en los demás alcances es ese mismo ruido pasado por la correlación de cada uno. El
          blanco es el cero. Conviene empezar por la izquierda, en \\(\\phi = 0\\) —el ruido solo, todavía sin
          correlación—, y ver dónde la cobertura se despega del {NIVEL4}&nbsp;% que el intervalo promete.</p>
        <div class="simulador-controles"></div>
        <p class="grafico-etiqueta">Error estándar de la media: el que se calcularía y el real</p>
        <div class="grafico-wrapper" style="height:230px;">
          <canvas data-panel="ee" aria-label="Error estándar ingenuo de la media frente al real, en función del alcance de la correlación. Un marcador vertical señala el alcance elegido con el deslizador" role="img"></canvas>
        </div>
        <p class="grafico-etiqueta">Cobertura del intervalo al {NIVEL4}&nbsp;%</p>
        <div class="grafico-wrapper" style="height:210px;">
          <canvas data-panel="cobertura" aria-label="Cobertura del intervalo de confianza al {NIVEL4} por ciento, en función del alcance de la correlación, frente a la cobertura prometida. Un marcador vertical señala el alcance elegido con el deslizador" role="img"></canvas>
        </div>
        <div class="geomapa" data-geomapa="cap1-campo"></div>
        <div class="simulador-lectura"></div>
      </div>

      <p>Sin correlación el método funciona: la cobertura sale <strong>{n(inf['cobertura_independiente'])}</strong>,
        que es el 95&nbsp;% prometido. Con \\(\\phi = {r4['phi']}\\) —vecinos inmediatos correlacionados a
        {n(r4['rho_vecino'])}— la cobertura se desploma a <strong>{n(r4['cobertura'])}</strong>
        (± {n(r4['emc_cobertura'])} de error de Monte Carlo). Un intervalo que promete equivocarse una vez de cada
        veinte se equivoca <strong>cuatro de cada cinco</strong>.</p>

      <p>Esa cobertura se puede ver. El gráfico toma {ci['n']} de las {ent(inf['nrep'])} réplicas de
        \\(\\phi = {ci['phi']}\\) —las {ci['n']} primeras, sin elegirlas— y dibuja el intervalo de cada una como un
        segmento vertical, con su media en el centro. La línea horizontal es la media verdadera, cero. Un
        intervalo que la cruza acierta; uno que no la toca, en naranja, se equivoca.</p>

      <div class="simulador" data-simulador="cien-ic">
        <h4><i class="fas fa-grip-lines-vertical" aria-hidden="true"></i> {ci['n']} intervalos al
          {NIVEL4}&nbsp;%, uno por réplica</h4>
        <p class="simulador-intro">Cada segmento es el intervalo de una réplica y cada punto, su media. Las
          {ci['n']} medias son las mismas en las dos vistas: lo único que cambia al conmutar es el largo de los
          segmentos. En la primera vista el error estándar es el que calcula el programa,
          \\(s/\\sqrt{{n}}\\); en la segunda, el verdadero, que aquí se conoce porque el campo se ha
          simulado. El primer segmento, el de la izquierda, es el del campo que dibuja el simulador anterior
          en \\(\\phi = {ci['phi']}\\).</p>
        <div class="simulador-controles"></div>
        <div class="grafico-wrapper" style="{ALTO_T24}">
          <canvas aria-label="{ci['n']} intervalos de confianza al {NIVEL4} por ciento de la media, uno por réplica del campo con alcance {ci['phi']}, dibujados en vertical alrededor de la media verdadera, cero. Con el error estándar ingenuo cubren el cero {ci['n_cubren_ingenuo']} de los {ci['n']}; con el error estándar verdadero, {ci['n_cubren_exacto']}" role="img"></canvas>
        </div>
        <div class="simulador-lectura"></div>
      </div>

      <p>De estos {ci['n']} intervalos ingenuos cubren el cero <strong>{ci['n_cubren_ingenuo']}</strong>. Ese
        recuento no es la cobertura del módulo, sino el de una muestra de {ci['n']} réplicas: sobre las
        {ent(inf['nrep'])} réplicas la cobertura es {n(r4['cobertura'])}, y otras {ci['n']} réplicas darían otro
        recuento cercano. Lo que el dibujo enseña es la razón del fallo. Las medias se reparten a un lado y a
        otro del cero, sin irse hacia ninguno, y cada segmento es mucho más corto que la distancia que separa unas
        medias de otras.</p>

      <p>Con el error estándar verdadero, \\(\\sqrt{{\\mathbf{{1}}^\\top R\\,\\mathbf{{1}}}}/n =
        {n(ci['ee_exacto'])}\\) —el que sale de sumar todas las correlaciones, como en el recuadro de abajo—, las
        medias no se mueven: son las mismas {ci['n']}. Cambia el largo de los segmentos, cuyo semiancho pasa de
        {n(ci['semiancho_ingenuo_medio'])} en promedio a {n(ci['semiancho_exacto'])}, que es
        <strong>{n(ci['razon_semianchos'])} veces</strong> el primero, y entonces cubren el cero
        <strong>{ci['n_cubren_exacto']}</strong> de los {ci['n']}. Ese cociente no es el {n(r4['factor'])} del
        recuadro de abajo, aunque los dos dicen lo mismo: aquí se dividen los semianchos de estas {ci['n']}
        réplicas, cada uno con su cuantil; allí, la desviación típica de las {ent(inf['nrep'])} medias entre
        su error estándar ingenuo medio. Sobre las {ent(inf['nrep'])} réplicas, ese
        intervalo cubre {n(ci['cobertura_exacto'])} (± {n(ci['emc_cobertura_exacto'])}), el {NIVEL4}&nbsp;%
        prometido.
        La media estaba bien en las dos vistas. Lo que estaba mal era el largo del segmento, es decir, el error
        estándar.</p>

      <div class="definition">
        <h3>De dónde sale el destrozo, en tres pasos</h3>
        <p>La varianza de una media <em>no</em> es \\(\\sigma^2/n\\) cuando hay covarianzas:</p>
        <p style="text-align:center;">$$\\operatorname{{Var}}(\\bar{{Z}}) =
          \\frac{{1}}{{n^2}}\\left[\\sum_i \\operatorname{{Var}}(Z_i)
          + \\sum_{{i \\neq j}} \\operatorname{{Cov}}(Z_i, Z_j)\\right]
          = \\frac{{\\sigma^2}}{{n}}\\left[1 + \\frac{{1}}{{n}}\\sum_{{i \\neq j}} \\rho_{{ij}}\\right]$$</p>
        <p>El corchete es el <strong>factor de inflación por diseño</strong>. Vale 1 cuando la suma de las
          correlaciones se anula —en particular, si todas son cero—. De \\(\\phi = {r4['phi']}\\) a las cifras que publica el módulo hay tres pasos, y conviene
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
        remuestreando <strong>departamentos enteros</strong>, que conserva la dependencia dentro de cada uno.</p>

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

      <p>Factor <strong>{n(ir['factor'])}</strong>. El intervalo por bloques es cuatro veces más ancho que el
        ingenuo, y eso con dato real, sin simular nada. Los dos comparten centro porque los dos se han construido
        alrededor de la media muestral, {n(ir['media'])}, sumándole y restándole el error estándar de cada
        remuestreo multiplicado por el cuantil normal.</p>

      <p>Las réplicas, en cambio, no comparten centro. Las del remuestreo de municipios sueltos promedian
        {n(rp['media_iid'])}, a menos de un error de Monte Carlo de la media muestral. Las del remuestreo por
        departamentos tienen otra esperanza: calculada con {ent(rp['nrep_esperanza'])} réplicas, vale
        <strong>{n(rp['esperanza_bloques'])}</strong>, {n(rp['desvio_esperanza'])} por encima de la media muestral,
        con un error de Monte Carlo de {n(rp['emc_esperanza'])}. Las {ent(ir['nboot'])} réplicas de la tabla
        promedian {n(rp['media_bloques'])}, dentro de su propio ruido alrededor de esa esperanza. El desvío no es
        ruido, y tiene explicación. Los departamentos tienen entre {rp['bloque_min']} y {rp['bloque_max']}
        municipios, así que cada réplica reúne un número distinto de municipios y su media es un cociente de dos
        sumas que cambian a la vez —un <em>estimador de razón</em>—, cuya esperanza no es la media de partida.
        El desvío es pequeño, el {n(rp['desvio_esperanza_pct_ee'])}&nbsp;% del error estándar por bloques, y no
        cambia la tabla. El intervalo se centra en la media muestral porque ésa es la estimación y el intervalo se
        construye a su alrededor; el desvío es un motivo más para no recentrarlo en la media de las réplicas.</p>

      <div class="warning">
        <p><strong>Lo que ese error estándar supone, y cuánto se le puede creer.</strong> Remuestrear departamentos
          enteros conserva la dependencia <em>dentro</em> de cada departamento y, a cambio, trata los
          {ent(ir['n_departamentos'])} departamentos como <strong>independientes entre sí</strong>. Si los
          departamentos vecinos se parecen, esa dependencia queda fuera de la cuenta y el error estándar por
          bloques también se queda corto: corrige al ingenuo, pero no es el verdadero.</p>
        <p>Además es una estimación hecha con {ent(ir['n_departamentos'])} bloques de tamaños muy desiguales, y
          ella misma es incierta. Una primera mirada es quitar un departamento cada vez y repetir los dos
          remuestreos con los {ent(sud['n_departamentos_quedan'])} que quedan, con {ent(sud['nboot'])} réplicas
          para que el ruido de Monte Carlo no decida. El factor va de <strong>{n(sud['factor_min'])}</strong> a
          <strong>{n(sud['factor_max'])}</strong>, y el tamaño efectivo que el módulo 5 saca de él, de
          <strong>{n(sud['n_eff_min'])}</strong> a <strong>{n(sud['n_eff_max'])}</strong> municipios. El factor
          más bajo y el tamaño efectivo más alto salen al quitar {sud['extremo']['departamento']}, que tiene
          {ent(sud['extremo']['municipios'])} de los {ent(ir['n_municipios'])} municipios: sin él, el factor queda
          por debajo del de la tabla y el tamaño efectivo, por encima.</p>
        <p>Ese recorrido mide la <strong>sensibilidad a un solo departamento</strong>, no la incertidumbre, y como
          medida de la incertidumbre se queda corto. Cada uno de esos {ent(ir['n_departamentos'])} cálculos
          comparte con cualquier otro todos sus departamentos menos uno, así que sus resultados se parecen entre
          sí mucho más de lo que se parecerían {ent(ir['n_departamentos'])} estimaciones independientes. El
          <em>jackknife</em> repone lo que falta: toma la dispersión de los \\(K = {ir['n_departamentos']}\\)
          valores \\(f_i\\) alrededor de su media y la amplía con el número de bloques,</p>
        <p style="text-align:center;">$$\\widehat{{ee}}_{{\\text{{jk}}}} =
          \\sqrt{{\\frac{{K-1}}{{K}} \\sum_{{i=1}}^{{K}} \\left(f_i - \\bar{{f}}\\right)^2}}$$</p>
        <p style="margin-bottom:0;">Da un error estándar de <strong>{n(sud['ee_jackknife_factor'])}</strong> para
          el factor y de <strong>{n(sud['ee_jackknife_n_eff'])}</strong> municipios para el tamaño efectivo, el
          {n(sud['ee_jackknife_n_eff_pct'])}&nbsp;% de la cifra publicada: más que medio recorrido en los dos
          casos. Con {ent(ir['n_departamentos'])} bloques, el tamaño efectivo se conoce solo en orden de magnitud:
          queda muy lejos de los {ent(ir['n_municipios'])} municipios, pero la cifra de la tabla,
          {n(ir['n_eff'])}, no se puede leer con sus decimales. Cambiar de semilla mueve las cifras
          bastante menos que quitar un departamento: con otras {ent(osm['n'])} parejas de semillas y los
          {ent(ir['n_departamentos'])} departamentos, el tamaño efectivo va de {n(osm['n_eff_min'])} a
          {n(osm['n_eff_max'])}. La incertidumbre que pesa no es la del generador de números aleatorios: es la de
          contar con {ent(ir['n_departamentos'])} bloques.</p>
      </div>

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
rep_blq &lt;- replicate(B, {
  sel &lt;- sample(seq_along(bloques), length(bloques), replace = TRUE)
  mean(unlist(bloques[sel], use.names = FALSE))
})
ee_blq &lt;- sd(rep_blq)
cat(sprintf("i.i.d. = %.5f | bloques = %.5f | factor = %.5f\\n",
            ee_iid, ee_blq, ee_blq / ee_iid))
#&gt; """ + f"i.i.d. = {n(ir['ee_bootstrap_iid'])} | bloques = "
    f"{n(ir['ee_bootstrap_bloques'])} | factor = {n(ir['factor'])}" + """

# Las replicas por bloques NO tienen por esperanza la media muestral: cada
# una reune un numero distinto de municipios, y su media es un cociente de
# dos sumas. Con 4 000 replicas la diferencia apenas se separa del ruido,
# asi que la esperanza se calcula aparte: remuestrear departamentos es
# sortear cuantas veces sale cada uno (una multinomial).
sumas &lt;- sapply(bloques, sum)
tams  &lt;- lengths(bloques)
K &lt;- length(bloques)
set.seed(2230)
total &lt;- 0
for (lote in 1:10) {
  veces &lt;- rmultinom(200000, K, rep(1 / K, K))        # K x 200 000
  total &lt;- total + sum(as.vector(crossprod(veces, sumas)) /
                       as.vector(crossprod(veces, tams)))
}
cat(sprintf("media muestral = %.5f | replicas de arriba = %.5f | su esperanza = %.5f\\n",
            mean(ok$desercion), mean(rep_blq), total / 2e6))
#&gt; """ + f"media muestral = {n(ir['media'])} | replicas de arriba = "
    f"{n(rp['media_bloques'])} | su esperanza = {n(rp['esperanza_bloques'])}" + """

# Cuanto depende ese factor de un solo departamento: se quita uno cada vez
# y se repiten los dos remuestreos con los que quedan, con mas replicas
# para que el ruido no decida. Tarda alrededor de medio minuto.
B_sin &lt;- """ + str(sud['nboot']) + """
sin_uno &lt;- sapply(names(bloques), function(d) {
  q  &lt;- ok$dpto != d
  y  &lt;- ok$desercion[q]
  bl &lt;- split(y, ok$dpto[q])
  set.seed(""" + str(sud['semilla_iid']) + """)
  e_i &lt;- sd(replicate(B_sin, mean(sample(y, length(y), replace = TRUE))))
  set.seed(""" + str(sud['semilla_bloques']) + """)
  e_b &lt;- sd(replicate(B_sin, {
    sel &lt;- sample(seq_along(bl), length(bl), replace = TRUE)
    mean(unlist(bl[sel], use.names = FALSE))
  }))
  c(factor = e_b / e_i, n_eff = length(y) * (e_i / e_b)^2)
})
cat(sprintf("factor: de %.5f a %.5f | n efectivo: de %.5f a %.5f\\n",
            min(sin_uno["factor", ]), max(sin_uno["factor", ]),
            min(sin_uno["n_eff", ]), max(sin_uno["n_eff", ])))
#&gt; """ + f"factor: de {n(sud['factor_min'])} a {n(sud['factor_max'])} | n efectivo: de "
    f"{n(sud['n_eff_min'])} a {n(sud['n_eff_max'])}" + """

# Ese recorrido es la sensibilidad a un departamento, no la incertidumbre:
# los 33 calculos comparten casi todos sus departamentos. El error estandar
# jackknife la repone con esos mismos valores.
ee_jk &lt;- apply(sin_uno, 1, function(v) {
  sqrt((length(v) - 1) / length(v) * sum((v - mean(v))^2))
})
cat(sprintf("e.e. jackknife: factor %.5f | n efectivo %.5f\\n",
            ee_jk[["factor"]], ee_jk[["n_eff"]]))
#&gt; """ + f"e.e. jackknife: factor {n(sud['ee_jackknife_factor'])} | n efectivo "
    f"{n(sud['ee_jackknife_n_eff'])}",
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
# Las filas de la tabla «rellenar frente a ampliar». Se montan fuera del
# f-string del módulo porque llevan un bucle; las cifras, todas de R.
FILAS_TECHO = "\n".join(
    f"""          <tr><th scope="row">{f['k']}</th><td>{ent(f['n'])}</td>
            <td>{n(f['relleno']['rho_medio'])}</td><td>{n(f['relleno']['n_eff'])}</td>
            <td>{n(f['ampliacion']['rho_medio'])}</td><td>{n(f['ampliacion']['n_eff'])}</td></tr>"""
    for f in tc["rejilla"])

MOD5 = cabecera(
    5, "Tamaño de muestra efectivo", "Effective sample size",
    "Traducir «hay dependencia» a una cifra que se entienda: cuántas "
    "observaciones independientes valen las que tienes.") + f"""
      <p>El módulo 4 dejó una pregunta incómoda: si el intervalo por bloques es {n(ir['factor'])} veces más ancho, ¿de
        cuántos municipios se trata en realidad? El <strong>tamaño de muestra efectivo</strong> responde
        justo eso.</p>

      <p>La respuesta para Colombia, primero, y la fórmula después. Los <strong>{ent(ne['desercion_n'])}</strong>
        municipios con dato de deserción informan como <strong>{n(ne['desercion_municipal'])}</strong> municipios
        independientes. Es el <strong>{n(ne['desercion_pct'])}&nbsp;%</strong> de la información que aparentaban
        tener.</p>

      <div class="definition">
        <h3>Qué cuenta el tamaño efectivo</h3>
        <p>Se define \\(n_{{\\text{{eff}}}}\\) como el número de observaciones <em>independientes</em> que darían la
          misma varianza de la media que las \\(n\\) observaciones correlacionadas que se tienen. Si todas tienen
          la misma varianza, ese número tiene fórmula cerrada:</p>
        <p style="text-align:center;">$$n_{{\\text{{eff}}}} = \\frac{{n}}{{1 + (n-1)\\,\\bar{{\\rho}}}}$$</p>
        <p style="text-align:center;">$$\\bar{{\\rho}} = \\frac{{1}}{{n(n-1)}} \\sum_{{i \\neq j}} \\rho_{{ij}}$$</p>
        <p style="margin-bottom:0;">Aquí \\(\\rho_{{ij}}\\) es la correlación entre las observaciones \\(i\\) y
          \\(j\\) —si solo depende de la distancia que las separa, \\(\\rho(h_{{ij}})\\)— y \\(\\bar{{\\rho}}\\) es su
          <strong>media sobre todos los pares</strong>. La fórmula no es una aproximación ni exige que todos los
          pares se parezcan lo mismo: <strong>es una identidad</strong>. La correlación puede decaer con la
          distancia, como en el correlograma del módulo 3; a la varianza de la media solo le llega su promedio.</p>
      </div>

      <div class="derivacion">
        <button type="button" class="derivacion-boton" aria-expanded="false" aria-controls="der-n-eff">
          <i class="fas fa-square-root-variable" aria-hidden="true"></i>
          <span class="derivacion-texto">Ver de dónde sale \\(n_{{\\text{{eff}}}} = n/(1+(n-1)\\bar{{\\rho}})\\)</span>
          <i class="fas fa-chevron-down" aria-hidden="true"></i>
        </button>
        <div class="derivacion-panel" id="der-n-eff" hidden>
          <ol class="derivacion-pasos">
            <li>
              <p>La media es una suma dividida entre \\(n\\), y la varianza de una suma es la suma de
                <strong>todas</strong> las covarianzas: cada observación con cada una, incluida ella misma.</p>
              $$\\operatorname{{Var}}(\\bar{{Z}}) = \\frac{{1}}{{n^2}} \\sum_{{i=1}}^{{n}} \\sum_{{j=1}}^{{n}}
                \\operatorname{{Cov}}(Z_i, Z_j)$$
            </li>
            <li>
              <p>En esa suma doble hay dos clases de términos. Los \\(n\\) de la diagonal, con \\(i = j\\), son
                varianzas. Los \\(n(n-1)\\) restantes son covarianzas entre observaciones distintas, y si todas
                tienen la misma varianza \\(\\sigma^2\\) cada una vale \\(\\sigma^2 \\rho_{{ij}}\\). Es el único
                supuesto de todo el desarrollo.</p>
              $$\\operatorname{{Var}}(\\bar{{Z}}) = \\frac{{1}}{{n^2}} \\Bigl( n\\,\\sigma^2 +
                \\sigma^2 \\sum_{{i \\neq j}} \\rho_{{ij}} \\Bigr)$$
            </li>
            <li>
              <p>La suma de las correlaciones es el número de pares por su media,
                \\(\\sum_{{i \\neq j}} \\rho_{{ij}} = n(n-1)\\,\\bar{{\\rho}}\\). Eso no supone que las
                \\(\\rho_{{ij}}\\) sean iguales: solo le pone nombre a su promedio.</p>
              $$\\operatorname{{Var}}(\\bar{{Z}}) = \\frac{{\\sigma^2}}{{n}} \\bigl[ 1 + (n-1)\\,\\bar{{\\rho}} \\bigr]$$
            </li>
            <li>
              <p>Con \\(m\\) observaciones independientes la varianza de la media sería \\(\\sigma^2/m\\). El
                tamaño efectivo es el \\(m\\) que iguala las dos.</p>
              $$\\frac{{\\sigma^2}}{{n_{{\\text{{eff}}}}}} = \\frac{{\\sigma^2}}{{n}} \\bigl[ 1 + (n-1)\\,\\bar{{\\rho}} \\bigr]
                \\quad\\Longrightarrow\\quad n_{{\\text{{eff}}}} = \\frac{{n}}{{1 + (n-1)\\,\\bar{{\\rho}}}}$$
            </li>
          </ol>
          <p class="derivacion-resultado">El corchete del paso 3 es el mismo del módulo 4, que lo dejó escrito
            como \\(1 + \\tfrac{{1}}{{n}}\\sum_{{i \\neq j}} \\rho_{{ij}}\\): es el efecto de diseño, las veces que la
            varianza de la media supera a la que habría con independencia. Y como la suma doble del paso 1 recorre
            la matriz de covarianzas entera, calcular \\(n_{{\\text{{eff}}}}\\) con esa matriz o con
            \\(\\bar{{\\rho}}\\) es hacer la misma cuenta por dos caminos.</p>
        </div>
      </div>

      <p>Con la fórmula a la vista aparece lo que enseña este módulo. Si \\(\\bar{{\\rho}}\\) se mantiene fijo
        mientras \\(n\\) crece, \\(n_{{\\text{{eff}}}} \\to 1/\\bar{{\\rho}}\\): <strong>hay un techo.</strong> Con
        \\(\\bar{{\\rho}} = {ne['rhos'][1]}\\) —una correlación media que nadie llamaría preocupante— ese techo son
        {ent(ne['caso_quiz']['techo_otro'])} observaciones. La condición «si \\(\\bar{{\\rho}}\\) se mantiene fijo» no es un
        tecnicismo: se examina justo después del simulador.</p>

      <div class="simulador" data-simulador="n-efectivo">
        <h4><i class="fas fa-compress" aria-hidden="true"></i> El techo de la información</h4>
        <p class="simulador-intro">Mueve \\(\\bar{{\\rho}}\\) y mira cuánto aporta pasar de
          {ent(ne['enes'][0])} a {ent(ne['enes'][-1])} observaciones: la curva se despega de la
          diagonal —el caso sin correlación— y se aplasta contra el techo \\(1/\\bar{{\\rho}}\\), que se mueve con
          el deslizador. Cada curva mantiene \\(\\bar{{\\rho}}\\) fijo a lo largo de todo el eje. El rombo es
          Colombia, y la curva fija que pasa por él es la del \\(\\bar{{\\rho}}\\) que corresponde a ese
          {n(ne['desercion_municipal'])}; de dónde sale se explica más abajo.</p>
        <div class="simulador-controles"></div>
        <div class="grafico-wrapper" style="height:300px;">
          <canvas aria-label="Tamaño de muestra efectivo frente al número de observaciones, para la correlación media entre pares que fija el deslizador, con el techo uno partido por esa correlación media, la diagonal sin correlación, el punto de Colombia y la curva de la correlación media que corresponde a ese punto, que pasa por él" role="img"></canvas>
        </div>
        <div class="simulador-lectura"></div>
      </div>

      <p>Con \\(n = {ent_mate(ne['enes'][-1])}\\) y \\(\\bar{{\\rho}} = {ne['rhos'][1]}\\) el tamaño efectivo es
        <strong>{n(ne['rejilla'][-1]['n_eff'][1])}</strong>: el
        <strong>{n(ne['rejilla'][-1]['pct'][1])}&nbsp;%</strong>. Y con
        \\(\\bar{{\\rho}} = {ne['rhos'][4]}\\) baja a <strong>{n(ne['rejilla'][-1]['n_eff'][4])}</strong>. Mil
        observaciones que valen por diez.</p>

      <div class="warning">
        <p><strong>Que haya techo depende de cómo se añadan los datos.</strong> \\(\\bar{{\\rho}}\\) no es una
          constante del fenómeno: es el promedio de \\(\\rho(h)\\) sobre los pares que se tienen, y cambia cuando
          cambian los pares. Hay dos maneras de pasar de {ent(tc['rejilla'][0]['n'])} a
          {ent(tc['rejilla'][-1]['n'])} observaciones, y llevan a sitios opuestos.</p>
        <ul style="margin-bottom:0;">
          <li><strong>Rellenar.</strong> La región no cambia y la red se hace más densa. Las distancias entre
            pares se reparten cada vez más como las de dos puntos tomados al azar dentro de la región, así que
            \\(\\bar{{\\rho}}\\) tiende a una constante positiva, \\(\\bar{{\\rho}}_\\infty\\), que solo
            depende de la región y de \\(\\rho(h)\\). Esa constante es la que crea el techo:
            \\(n_{{\\text{{eff}}}}\\) se estanca en \\(1/\\bar{{\\rho}}_\\infty\\).</li>
          <li><strong>Ampliar.</strong> La separación entre observaciones no cambia y la región crece. Entran
            pares cada vez más lejanos y los cercanos pesan cada vez menos en el promedio, así que
            \\(\\bar{{\\rho}}\\) cae hacia cero: no hay techo.</li>
        </ul>
      </div>

      <p>La tabla hace las dos cuentas sobre el campo del módulo 4, con \\(\\rho(h) = e^{{-h/\\phi}}\\) y
        \\(\\phi = {tc['phi']}\\). Al rellenar, la región es siempre el cuadrado de lado {tc['lado_relleno']}
        que ocupan las celdas de aquella retícula, partido en celdas cada vez más pequeñas con una observación
        en el centro de cada una; al ampliar, el paso entre observaciones es siempre
        {tc['paso_ampliacion']}.</p>

      <table>
        <caption>Tamaño efectivo de la media al pasar de {tc['rejilla'][0]['k']} a {tc['rejilla'][-1]['k']} celdas
          por lado, rellenando la misma región o ampliándola. Con {inf['k']} celdas por lado las dos son la
          retícula del módulo 4.</caption>
        <thead>
          <tr><th scope="col">Celdas por lado</th><th scope="col">\\(n\\)</th>
            <th scope="col">\\(\\bar{{\\rho}}\\) al rellenar</th>
            <th scope="col">\\(n_{{\\text{{eff}}}}\\) al rellenar</th>
            <th scope="col">\\(\\bar{{\\rho}}\\) al ampliar</th>
            <th scope="col">\\(n_{{\\text{{eff}}}}\\) al ampliar</th></tr>
        </thead>
        <tbody>
{FILAS_TECHO}
        </tbody>
      </table>

      <p>Al rellenar, \\(n\\) se multiplica por {tc['factor_n']} y el tamaño efectivo apenas se mueve: pasa de
        {n(tc['rejilla'][0]['relleno']['n_eff'])} a {n(tc['rejilla'][-1]['relleno']['n_eff'])},
        {n(tc['factor_relleno'])} veces el de partida, y el último salto —de {ent(tc['rejilla'][-2]['n'])} a
        {ent(tc['rejilla'][-1]['n'])} observaciones— lo sube un {n(tc['ultimo_salto_pct'])}&nbsp;%. Se está
        estancando, y el límite se puede calcular: la correlación media entre dos puntos tomados al azar en esa
        región es \\(\\bar{{\\rho}}_\\infty = {n(tc['rho_inf'])}\\), y su inverso,
        \\(1/\\bar{{\\rho}}_\\infty = \\) <strong>{n(tc['techo_inf'])}</strong>, es el techo. La última fila
        queda a un {n(tc['falta_techo_pct'])}&nbsp;% de él, y por debajo: con este diseño el tamaño efectivo se
        acerca al techo desde abajo. Lo que no depende de dónde se pongan los puntos es el límite: mientras se
        repartan por igual en toda la región, por muchas observaciones que se añadan, el tamaño efectivo de su
        media acaba en \\(1/\\bar{{\\rho}}_\\infty\\).</p>

      <p>Al ampliar, el mismo aumento de \\(n\\) multiplica el tamaño efectivo por
        <strong>{n(tc['factor_ampliacion'])}</strong>, porque \\(\\bar{{\\rho}}\\) cae de
        {n(tc['rejilla'][0]['ampliacion']['rho_medio'])} a {n(tc['rejilla'][-1]['ampliacion']['rho_medio'])}: ahí
        no hay límite. Más puntos en la misma región no es más región. Lo que separa un caso del otro es hasta
        dónde llega \\(\\rho(h)\\) comparado con el tamaño de la región, y esa función es la que el módulo 6
        mira con el variograma.</p>

      <div class="definition">
        <h3>Qué \\(\\bar{{\\rho}}\\) hay detrás del {n(ne['desercion_municipal'])} de Colombia</h3>
        <p>Esa cifra no salió de medir correlaciones: viene del módulo 4, del cociente entre los dos remuestreos,
          \\(n \\cdot (ee_{{\\text{{iid}}}}/ee_{{\\text{{bloques}}}})^2\\). Leída con la fórmula, a esa
          varianza le corresponde una correlación media, que se despeja:</p>
        <p style="text-align:center;">$$\\bar{{\\rho}} = \\frac{{n/n_{{\\text{{eff}}}} - 1}}{{n - 1}} =
          {n(rt['implicito'])}$$</p>
        <p>Es la correlación media entre pares de municipios <strong>que corresponde a la varianza que midió el
          remuestreo por departamentos</strong>, y su curva pasa por el rombo del simulador porque de ahí se
          despeja. No es una medición aparte, y es aproximada por tres lados.</p>
        <ul style="margin-bottom:0;">
          <li>Hereda la incertidumbre del remuestreo —el módulo 4 le pone un error estándar, y es de
            {n(sud['ee_jackknife_n_eff'])} municipios— y su supuesto, que los {ent(ir['n_departamentos'])} departamentos son bloques independientes entre sí. Si entre departamentos vecinos queda dependencia
            positiva, el remuestreo subestima la varianza y este \\(\\bar{{\\rho}}\\) se queda corto.</li>
          <li>La identidad pide la misma varianza en todas las observaciones, y los municipios no la
            tienen.</li>
          <li>El error estándar ingenuo sale de \\(s^2\\), que se encoge con la correlación: la esperanza que
            dio el módulo 4 equivale a \\(\\sigma^2(1 - \\bar{{\\rho}})\\). Así que el cociente de remuestreos
            no estima \\(n/(1+(n-1)\\bar{{\\rho}})\\) sino
            \\(n(1-\\bar{{\\rho}})/(1+(n-1)\\bar{{\\rho}})\\). Despejando de esta segunda expresión sale
            {n(rt['implicito_con_s2'])}, un {n(rt['diferencia_s2_pct'])}&nbsp;% menos. La corrección es pequeña,
            pero deja claro que la cifra es una lectura de la varianza y no una medida de la correlación.</li>
        </ul>
      </div>

      <p>Lo natural sería no pasar por el remuestreo y medir \\(\\bar{{\\rho}}\\) directamente sobre el mapa, como
        se mide cualquier correlación: centrar cada dato con la media, promediar los productos de todos los pares
        y dividir por la varianza. <strong>No se puede</strong>, y la razón no es el ruido. Ese promedio vale
        \\(-1/(n-1)\\) para cualquier conjunto de datos que no sea constante, tenga la correlación que
        tenga.</p>

      <div class="derivacion">
        <button type="button" class="derivacion-boton" aria-expanded="false" aria-controls="der-centrado">
          <i class="fas fa-square-root-variable" aria-hidden="true"></i>
          <span class="derivacion-texto">Ver por qué el promedio de todos los pares vale siempre \\(-1/(n-1)\\)</span>
          <i class="fas fa-chevron-down" aria-hidden="true"></i>
        </button>
        <div class="derivacion-panel" id="der-centrado" hidden>
          <ol class="derivacion-pasos">
            <li>
              <p>El estimador que se escribiría sin pensarlo dos veces: arriba, la media de los productos cruzados
                sobre los \\(n(n-1)\\) pares; abajo, la varianza muestral. Las dos con la media muestral
                \\(\\bar{{z}}\\), que es la única que se tiene.</p>
              $$r = \\frac{{\\dfrac{{1}}{{n(n-1)}} \\displaystyle\\sum_{{i \\neq j}} (z_i - \\bar{{z}})(z_j - \\bar{{z}})}}
                {{\\dfrac{{1}}{{n}} \\displaystyle\\sum_{{i}} (z_i - \\bar{{z}})^2}}$$
            </li>
            <li>
              <p>Las desviaciones respecto de la media muestral suman cero. No es una propiedad del dato: es lo
                que significa haber restado \\(\\bar{{z}}\\).</p>
              $$\\sum_{{i}} (z_i - \\bar{{z}}) = 0$$
            </li>
            <li>
              <p>El cuadrado de esa suma también es cero, y al desarrollarlo aparecen justo las dos sumas del
                estimador: los cuadrados y los productos cruzados.</p>
              $$0 = \\Bigl( \\sum_{{i}} (z_i - \\bar{{z}}) \\Bigr)^2 = \\sum_{{i}} (z_i - \\bar{{z}})^2 +
                \\sum_{{i \\neq j}} (z_i - \\bar{{z}})(z_j - \\bar{{z}})$$
            </li>
            <li>
              <p>Así que los productos cruzados no traen información propia: son la suma de cuadrados cambiada de
                signo. Al sustituir, la suma de cuadrados se cancela y no queda nada del dato.</p>
              $$r = \\frac{{-\\dfrac{{1}}{{n(n-1)}} \\displaystyle\\sum_{{i}} (z_i - \\bar{{z}})^2}}
                {{\\dfrac{{1}}{{n}} \\displaystyle\\sum_{{i}} (z_i - \\bar{{z}})^2}} = -\\frac{{1}}{{n-1}}$$
            </li>
          </ol>
          <p class="derivacion-resultado">En ningún paso ha intervenido la correlación, la distribución ni el
            espacio. Es la misma cuenta que deja \\(E[I] = -1/(n-1)\\) en el módulo 3: la I de Moran con todos los
            pares como vecinos y el mismo peso para todos es exactamente este cociente. Por eso promediar un
            correlograma sobre todas las distancias no mide \\(\\bar{{\\rho}}\\): si entran todos los pares y
            cada uno pesa lo mismo, el promedio es exactamente \\(-1/(n-1)\\), y lo que salga positivo de cerca
            tiene que compensarse con negativo en otras distancias.</p>
        </div>
      </div>

      <p>La comprobación, sobre el campo simulado del módulo 4, donde la respuesta se conoce. Con
        \\(\\phi = {cz['phi']}\\) la correlación media verdadera entre las {cz['n']} celdas es
        <strong>{n(cz['rho_medio_verdadero'])}</strong>. En las {ent(cz['nrep'])} réplicas, el promedio centrado
        de todos los pares va de {n(cz['centrado_min'])} a {n(cz['centrado_max'])}: el mismo número en todas, y es
        \\(-1/(n-1)\\) con \\(n = {cz['n']}\\). Sobre la deserción de los {ent(cz['colombia']['n'])} municipios
        sale <strong>{n(cz['colombia']['centrado'])}</strong>, otra vez \\(-1/(n-1)\\): lo que daría cualquier
        otra variable medida en esos municipios.</p>

      <p>Hay dos obstáculos, y la simulación los separa. El primero es el <strong>centrado</strong>. En la
        simulación la media verdadera del proceso se conoce —es {cz['media']}, con varianza {cz['varianza']}—, y
        el mismo promedio calculado con ella en lugar de \\(\\bar{{z}}\\) sí apunta a \\(\\bar{{\\rho}}\\): su
        media sobre las réplicas es {n(cz['con_media_verdadera']['media'])}, con un error de Monte Carlo de
        {n(cz['con_media_verdadera']['emc'])}. El segundo es la <strong>realización única</strong>: aun con la
        media verdadera, de una réplica a otra ese promedio varía con desviación típica
        <strong>{n(cz['con_media_verdadera']['sd'])}</strong>, más que el valor que busca, y en el
        {n(cz['con_media_verdadera']['pct_negativas'])}&nbsp;% de las réplicas sale negativo. Con una sola
        realización, y con la media estimada sobre ese mismo dato, \\(\\bar{{\\rho}}\\) no se puede identificar
        sin un modelo de la covarianza. Es el problema que ocupa el módulo 6.</p>

      <p>Sobre ese campo se ve también que la fórmula no aproxima nada. Con \\(\\phi = {r4['phi']}\\), el tamaño
        efectivo de las {inf['n']} celdas calculado con la matriz de correlaciones entera es
        <strong>{n(e4['n_eff'])}</strong>; el que da la fórmula con \\(\\bar{{\\rho}} = {n(e4['rho_medio'])}\\) es
        <strong>{n(e4['n_eff_formula'])}</strong>. No se parecen: son el mismo número, un
        {n(e4['pct'])}&nbsp;% de la información.</p>

      <div class="warning">
        <p style="margin-bottom:0;"><strong>La fórmula es para la media, y solo para ella.</strong> Todo el
          desarrollo parte de \\(\\operatorname{{Var}}(\\bar{{Z}})\\). Para otro estimador —una pendiente de
          regresión, una varianza, la correlación entre dos variables— la cuenta es otra y el tamaño efectivo
          también. «Tengo el {n(ne['desercion_pct'])}&nbsp;% de la información» es una afirmación sobre la media
          de la deserción, no sobre cualquier cosa que se calcule con esos {ent(ne['desercion_n'])}
          municipios.</p>
      </div>

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
          realización contra el teórico y la banda del 5&nbsp;% al 95&nbsp;%. La curva punteada es el teórico
          promediado sobre los pares de cada rezago; el texto de debajo del simulador explica por qué no es
          \\(\\gamma\\) en el rezago entero.</p>
        <div class="simulador-controles"></div>
        <div class="geomapa" data-geomapa="cap1-realizacion"></div>
        <div class="grafico-wrapper" style="height:290px;">
          <canvas aria-label="Variograma de una realización frente al teórico promediado en cada rezago, con la banda del 5 al 95 por ciento sobre mil realizaciones" role="img"></canvas>
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
          realizaciones —todas del mismo proceso, todas con media verdadera {ur['media_del_proceso']}— la prueba que
          haría el análisis ingenuo, una \\(t\\) de una muestra para \\(H_0\\!: \\mu = {ur['media_del_proceso']}\\),
          bilateral y con \\(\\alpha = {D['inferencia']['alfa']}\\), rechaza en el
          <strong>{n(ur['pct_rechaza_ingenuo'])}&nbsp;%</strong> de los casos (± {n(ur['emc_rechaza'])}), cuando
          debería hacerlo en el {n(ur['pct_esperado_si_valiera'])}&nbsp;%.</p>
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
          <li><strong>Intrínseca:</strong> más débil, y por eso más usada. No pide nada del proceso en sí, solo
            de sus <em>diferencias</em>, y pide dos cosas: que su media sea cero,
            \\(E[Z(s+h) - Z(s)] = 0\\), y que su varianza dependa solo de la separación,
            \\(\\tfrac{{1}}{{2}}\\operatorname{{Var}}(Z(s+h) - Z(s)) = \\gamma(h)\\). Todo proceso estacionario de
            segundo orden es intrínseco, con \\(\\gamma(h) = C(0) - C(h)\\), pero no al revés. El ejemplo de siempre
            es el movimiento browniano en la recta: tiene varianza finita en cada punto,
            \\(\\operatorname{{Var}}B(t) = t\\), pero esa varianza crece con \\(t\\), así que no existe una \\(C(h)\\)
            que valga igual en todas partes y el proceso no es estacionario de segundo orden. Sus diferencias, en
            cambio, cumplen las dos condiciones, con \\(\\gamma(h) = |h|/2\\). Por eso el variograma es más general
            que la covarianza.</li>
          <li><strong>Isotropía:</strong> además, que \\(C\\) y \\(\\gamma\\) dependan solo de \\(\\lVert h \\rVert\\)
            y no de la dirección. Es una comodidad, no una ley: la anisotropía del capítulo 9 es lo que pasa cuando
            no se cumple.</li>
        </ul>
        <p style="margin-bottom:0;">Sin estacionariedad no hay repetición, y sin repetición no hay estimación. El
          precio: si la media cambia de sitio a sitio —una <em>tendencia</em>—, lo que se rompe es la primera
          condición de la intrínseca, porque \\(E[Z(s+h) - Z(s)]\\) deja de ser cero. El variograma empírico promedia
          diferencias al cuadrado, y si \\(m(s)\\) es la media en cada sitio, la esperanza de cada sumando ya no es
          \\(\\gamma(h)\\) sino \\(\\gamma(h) + \\tfrac{{1}}{{2}}\\,(m(s+h) - m(s))^2\\). Con una tendencia lineal ese
          término de más crece como \\(h^2\\): el cambio de media se contabiliza como
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
        botón</strong>: cada realización trae el suyo. Antes de leerlo hay que decir contra qué se compara. El
        estimador promedia, en el rezago \\(k\\), todos los pares de celdas cuya distancia queda a menos de media
        celda de \\(k\\), y esos pares no están todos a distancia \\(k\\): en el rezago 1 entran los vecinos de lado,
        a distancia 1, y también los diagonales, a \\(\\sqrt{{2}}\\). La referencia justa de cada rezago no es entonces
        \\(\\gamma(k)\\), sino \\(\\gamma\\) promediada sobre esos mismos pares, \\(\\bar\\gamma_k\\), que es la curva
        punteada del gráfico. En el rezago 1 vale <strong>{n(vg6['teorico_clase'][0])}</strong> frente a
        \\(\\gamma(1) = {n(vg6['teorico'][0])}\\), y la media de las {ent(ur['n_realizaciones'])} realizaciones,
        {n(vg6['media'][0])}, cae sobre la primera y no sobre la segunda.</p>

      <p>Contra esa referencia, las tres realizaciones se apartan, en su peor rezago, en
        {n(rv[0]['desvio_rel_max'])}, {n(rv[1]['desvio_rel_max'])} y {n(rv[2]['desvio_rel_max'])} veces su valor
        —rezagos {ent(rv[0]['lag_desvio_max'])}, {ent(rv[1]['lag_desvio_max'])} y
        {ent(rv[2]['lag_desvio_max'])}—, y la banda del 5&nbsp;% al 95&nbsp;% en el rezago 4 tiene una anchura de
        <strong>{n(ur['banda_rel_lag4'])}</strong> veces el valor de referencia. Es tan ancha que las tres caben
        dentro de ella en los ocho rezagos —en el 4 se apartan {n(rv[0]['desvio_rel_lag4'])},
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
av = ec["caso_aviso"]
inf = av["influyente"]
# La prosa del recuadro y la del aviso están escritas para UN cambio de
# signo, que cae entre los que bajan y es el par con aviso; para un
# municipio que declaró el estrato más alto de la escala sin internet en
# casa y que sube a su departamento al primer puesto; y para un barrido
# que deja la r departamental en casi cero. Si el dato deja de decir eso,
# la prosa miente, y se para aquí.
_bajan_sin = av["bajan_sin_estrato"]
if not (ec["n_invierten"] == 1 and ec["n_invierten_entre_bajan"] == ec["n_invierten"]
        and ec["n_suben"] + ec["n_bajan"] == ec["n_pares"]
        and [p for p in ec["pares"] if p["invierte_signo"]][0]["a"] == av["a"]
        and [p for p in ec["pares"] if p["invierte_signo"]][0]["b"] == av["b"]
        and av["p_departamental"] > 0.05
        and inf["estrato_medio"] == 6 and inf["pct_internet"] == 0
        and inf["puesto_con"] == 1 and inf["puesto_sin"] > 1
        and inf["r_departamental_sin_el"] == av["loo_max"]
        and av["loo_min"] < av["r_departamental"] < av["loo_max"] < 0
        and abs(av["r_departamental_sin_bajo_umbral"]) < 0.05 and abs(av["r_departamental_n30"]) < 0.05
        and _bajan_sin):
    sys.exit("PARADO: el módulo 7 cuenta un solo cambio de signo, el del estrato, y dice que no "
             "aguanta el barrido; el dato de escala_correlacion ya no lo sostiene")


def _une(frases):
    """«a, b y c», con «e» delante de una palabra que suena a i."""
    if len(frases) == 1:
        return frases[0]
    ult = frases[-1]
    conj = "e" if ult[:1].lower() in ("i", "í") or (ult[:2].lower() == "hi" and ult[:3].lower() != "hie") else "y"
    return ", ".join(frases[:-1]) + f" {conj} " + ult


_nombres_bajan = _une([f"{q['a_corta']} × {q['b_corta']}" for q in _bajan_sin])
MOD7 = cabecera(
    7, "Escala, soporte y agregación", "Scale and the MAUP",
    "Primera pincelada del MAUP: la misma variable cambia de valor —y a "
    "veces de signo— según sobre qué unidades se mida. Y, con las unidades "
    "quietas, según cómo se agregue.") + f"""
      <p>La deserción escolar de los {ent(es['n_municipal'])} municipios colombianos tiene un índice de Moran de
        <strong>{n(es['moran_municipal'])}</strong>: autocorrelación inequívoca, a {n(es['z_municipal'])}
        desviaciones estándar de lo que daría el azar. Agrega esos municipios a los {es['n_departamental']}
        departamentos y la misma variable da <strong>{n(es['moran_departamental'])}</strong>, a
        {n(es['z_departamental'])} desviaciones: ya no se distingue del azar
        (p&nbsp;=&nbsp;{n(es['p_departamental'])}, en la prueba de Moran bajo aleatorización y a una cola, la de
        la autocorrelación positiva, que es la que hace <code>moran.test</code>).</p>

      <p>La I departamental es un <strong>{n(es['caida_pct'])}&nbsp;%</strong> menor que la municipal. Ese
        porcentaje describe las dos cifras, pero no mide cuánta autocorrelación «se pierde» al agregar: las dos I
        no se obtienen con la misma regla. Cada una usa su propia matriz de pesos —contigüidad entre municipios,
        contigüidad entre departamentos— y su propio \\(n\\), y la desviación estándar de la I bajo la nula con
        {es['n_departamental']} unidades es {n(es['razon_ee'])} veces la de {ent(es['n_municipal'])}.</p>

      <p>La \\(z\\) sitúa cada I en su propia nula, y es ella, con su p, la que dice que la municipal es
        inequívoca y que la departamental no se distingue del azar. Pero tampoco las dos \\(z\\) se comparan entre
        sí como medida de cuánta autocorrelación queda, porque la \\(z\\) crece con \\(n\\). Si la I departamental
        fuera <em>igual</em> a la municipal, {n(es['moran_municipal'])}, su \\(z\\) sería
        <strong>{n(es['z_departamental_si_igual'])}</strong>, no {n(es['z_municipal'])}. Que la departamental no
        se distinga del azar mezcla dos cosas: que la I baja, y que con {es['n_departamental']} unidades la prueba
        tiene mucha menos potencia.</p>

      <p>No se ha cambiado el dato, ni la variable, ni el país. Se ha cambiado <strong>la unidad de análisis</strong>,
        y la unidad de análisis es una <strong>decisión de modelado</strong>, no de presentación. Eso es el
        <em>problema de la unidad de área modificable</em> —el MAUP—, y es lo que el capítulo 3 desarrolla entero.</p>

      <div class="simulador" data-simulador="agregacion">
        <h4><i class="fas fa-object-group" aria-hidden="true"></i> Agregar cambia la correlación</h4>
        <p class="simulador-intro">Sobre {ent(ag['niveles'][0]['n_unidades'])} celdas con correlación conocida, se
          promedian bloques cada vez más grandes y se recalcula la correlación. El segundo botón cambia a los
          {ec['n_pares']} pares reales de variables colombianas: cada renglón une la correlación del par entre
          municipios, el círculo hueco, con la del mismo par entre departamentos, el círculo lleno.</p>
        <div class="simulador-controles"></div>
        <div class="grafico-wrapper" style="height:250px;">
          <canvas aria-label="Correlación entre dos variables según el tamaño del bloque de agregación; y, con el segundo botón, la correlación de cada uno de los {ec['n_pares']} pares reales entre municipios y entre departamentos, sobre un eje de menos uno a uno, con el par de aviso en naranja" role="img"></canvas>
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
          agregar, la correlación se hace más fuerte»— es falsa, y basta el dato colombiano para verlo. Sobre
          {ec['n_variables']} variables municipales, los {ec['n_pares']} pares con correlación apreciable se reparten
          así al pasar de municipio a departamento: en <strong>{ec['n_suben']}</strong> la correlación <strong>se
          aleja del cero</strong> —se hace más fuerte, sea positiva o negativa— y en
          <strong>{ec['n_bajan']}</strong> <strong>se acerca al cero</strong>, es decir, se debilita. Lo que se
          cuenta es el valor absoluto, \\(|r|\\): una correlación negativa que se debilita se mueve hacia la
          derecha en el gráfico, y aun así pierde fuerza. Uno de los pares que se acercan al cero llega a
          cruzarlo y cambia de signo, y es el único de los {ec['n_pares']} que no aguanta la comprobación que el
          módulo hace justo después.</p>
        <p style="margin-bottom:0;">Agregar <em>cambia</em> la correlación. En qué dirección, depende de cómo estén
          repartidos el componente compartido y el ruido, y eso no se sabe de antemano.</p>
      </div>

      <p>El par principal —puntaje medio de Saber 11 frente a hogares con internet— va de
        <strong>{n(pr['r_municipal'])}</strong> por municipio a <strong>{n(pr['r_departamental'])}</strong> por
        departamento. Y no lo ponen los municipios diminutos: barriendo el umbral de tamaño, entre incluirlos todos
        y exigir al menos {pr['barrido'][2]['umbral']} estudiantes la correlación municipal se mueve
        <strong>{n(pr['diferencia_umbral_30'])}</strong>.</p>

      <div class="note">
        <p style="margin-bottom:0;"><strong>Ese barrido no es celo.</strong> Un porcentaje de cambio entre dos
          correlaciones solo significa algo si las dos están lejos de cero. Cuando las dos son ruido alrededor de
          cero, el cociente entre ellas puede dar cualquier cosa —un cambio de varios cientos por ciento entre dos
          cifras que no se distinguen de cero—, y si además tienen signos opuestos lo único que crece es el valor
          absoluto \\(|r|\\), no la correlación. Por eso, antes de publicar cuánto cambia una correlación al
          agregar, se comprueba que las dos cifras se sostienen: se barre el umbral de tamaño en vez de dar una
          cifra sola.</p>
      </div>

      <div class="warning">
        <p><strong>Y esa receta tumba el único cambio de signo del recuadro.</strong> Es el par
          {av['a_corta']} × {av['b_corta']}, en naranja en la gráfica de los {ec['n_pares']} pares:
          <strong>{n(av['r_municipal'])}</strong> por municipio, <strong>{n(av['r_departamental'])}</strong> por
          departamento. Con {av['n_departamentos']} departamentos, esa cifra departamental no se distingue de cero
          (p&nbsp;=&nbsp;{n(av['p_departamental'])}, en la prueba bilateral de la correlación de Pearson). Y el estrato arrastra un problema propio: lo declara cada
          estudiante, no todos lo declaran, y la fracción que lo declara va con el puntaje
          (r&nbsp;=&nbsp;{n(av['cor_cobertura_puntaje'])} entre municipios). Donde lo declaran pocos, el «estrato
          medio» es el de un subgrupo, y no uno cualquiera.</p>
        <p>El caso extremo es <strong>{inf['municipio']}</strong>, en {inf['departamento']}: de
          {ent(inf['n_estudiantes'])} estudiantes, los {ent(inf['n_con_estrato'])} que declararon su estrato dijeron
          {ent(inf['estrato_medio'])}, el más alto de la escala, en un municipio con un
          {ent(inf['pct_internet'])}&nbsp;% de hogares con internet. Con ese municipio, {inf['departamento']} sale
          como el departamento de estrato medio más alto del país —{n(inf['estrato_departamento_con'])}, por
          encima de {inf['segundo']}, con {n(inf['estrato_segundo'])}—; sin él, se queda en
          {n(inf['estrato_departamento_sin'])}. Y quitando solo ese municipio, la r departamental pasa de
          {n(av['r_departamental'])} a <strong>{n(inf['r_departamental_sin_el'])}</strong>. Es el extremo de un
          recorrido que da que pensar: quitando un municipio cualquiera —uno solo de los
          {ent(av['n_municipios_con_estrato'])} que tienen estrato—, la r departamental va de
          {n(av['loo_min'])} a {n(av['loo_max'])}. Una cifra que un solo municipio mueve tanto no sostiene un
          signo.</p>
        <p style="margin-bottom:0;">Pásale el barrido del par principal. Sin los {ent(av['n_bajo_umbral'])}
          municipios donde menos de la mitad de los estudiantes declaró el estrato, la r departamental queda en
          <strong>{n(av['r_departamental_sin_bajo_umbral'])}</strong>; con el umbral de {av['umbral_n']}
          estudiantes, en <strong>{n(av['r_departamental_n30'])}</strong>. Lo que sobrevive es que agregar se
          lleva esa correlación a cero, no que le dé la vuelta. Y la tesis del recuadro no depende de este par:
          {_nombres_bajan} también se acercan al cero, y lo siguen haciendo con el umbral de
          {av['umbral_n']} estudiantes.</p>
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
          {cc['n_celdas_toca']} celdas que toca. El mapa abre acercado a esas celdas, que es donde se lee la
          cifra que recibe cada una; el segundo par de botones cambia al estado entero, para situarlas.</p>
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
          es cómo se reparten, y los dos mapas de debajo lo enseñan: cada estación lleva el color de su
          pliegue. En el gráfico del RMSE, la línea de trazos es la desviación típica de la variable, que es
          prácticamente el error que se cometería prediciendo siempre la media: la barra de los bloques la
          pasa por poco, y por eso cada barra lleva su cifra encima.</p>
        <div class="simulador-controles"></div>
        <div class="grafico-wrapper" style="height:260px;">
          <canvas aria-label="RMSE y R cuadrado de la validación cruzada aleatoria frente a la validación por bloques espaciales. En el RMSE, una línea de trazos marca la desviación típica de la variable, que la barra de los bloques supera; en el R cuadrado, la barra de los bloques queda por debajo de cero" role="img"></canvas>
        </div>
        <div class="grid md:grid-cols-2 gap-4 items-start" style="margin-top:1rem;">
          <div class="geomapa" data-geomapa="cap1-pliegues-azar"></div>
          <div class="geomapa" data-geomapa="cap1-pliegues-bloques"></div>
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

      <p>El error al predecir en una zona no medida es un <strong>{n(cv['inflacion_pct'])}&nbsp;%</strong> mayor
        que el que anuncia la validación aleatoria. Y el R² es la cifra que más duele: pasa de <strong>{n(cv['r2_aleatoria'])}</strong> —un modelo
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
            falta postular ningún modelo: sumar cada observación dividida por su probabilidad de inclusión, y
            dividir esa suma por el tamaño de la población —el estimador de Horvitz–Thompson—, estima sin sesgo
            la media poblacional. La media muestral sin ponderar, en general,
            solo es insesgada cuando todas las probabilidades son iguales; si no lo son, se
            sesga hacia lo que el diseño sobrerrepresenta. Y algo que sorprende: en un muestreo aleatorio simple,
            dos extracciones distintas son (casi) incorreladas aunque el campo de debajo sea suave, porque lo que
            se repite al imaginar otra muestra no son ellas sino los sorteos. Es una propiedad de ese diseño y no
            de todos: si lo que se sortea son conglomerados de sitios vecinos, dos extracciones del mismo
            conglomerado sí están correlacionadas.</li>
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
        estación representa. Esas áreas no saldrían iguales ni con un muestreo de igual probabilidad, así que
        hace falta una referencia. En {ent(ru['n_muestras'])} muestras de {ent(ru['n_puntos'])} puntos repartidos
        al azar y de manera uniforme sobre el país, con sus polígonos construidos y recortados igual que los de la
        red, la celda mayor es, en la mediana, <strong>{n(ru['razon_mediana'], 1)}</strong> veces la menor, y en
        nueve de cada diez muestras esa razón queda entre {n(ru['razon_p05'], 1)} y
        {n(ru['razon_p95'], 1)}.</p>

      <p>En la red del IDEAM las áreas van de <strong>{n(dm['area_min_km2'], 2)}</strong> a
        <strong>{ent(dm['area_max_km2'])}</strong> km², una razón de <strong>{n(dm['razon_areas'], 1)}</strong>:
        {n(ru['red_sobre_mediana'], 1)} veces la mediana de la referencia y {n(ru['red_sobre_p95'], 1)} veces su
        percentil 95. Ninguna de las {ent(ru['n_muestras'])} muestras llega a esa razón. La red no se parece a
        un muestreo de igual probabilidad.</p>

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
          verdad.</strong> Pesar por Thiessen hace aquí un papel análogo al de ponderar por la inversa de la
          probabilidad de inclusión —darle más peso a lo que la muestra representa de menos—, pero no es lo mismo:
          el área de un polígono no es una probabilidad de inclusión, porque nadie sorteó nada. Supone que cada
          estación representa exactamente su territorio más próximo, que es una suposición tan discutible como la
          anterior — solo que menos ingenua. No es «la
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


def ejercicio(k, e, datos="", codigo=""):
    """Un ejercicio guiado, con su pista y su solución calculada.

    Ni el enunciado ni las cifras se escriben aquí: salen de
    `genera_soluciones.R`, que resuelve el ejercicio de verdad en R. Un
    ejercicio cuya solución se escribe de memoria es una solución sin
    verificar delante de un estudiante que se la va a creer.

    `datos` va debajo del enunciado, a la vista: es el enlace de descarga
    del archivo que el ejercicio usa. `codigo` va dentro de la solución,
    detrás de la lectura: el código que da las cifras de la tabla. La
    lectura puede traer varios párrafos, separados por una línea en blanco.
    """
    parrafos = [t.strip() for t in e["lectura"].split("\n\n") if t.strip()]
    lectura = "\n".join(
        f"""            <p{' style="margin-bottom:0;"' if i == len(parrafos) - 1 and not codigo else ''}>{t}</p>"""
        for i, t in enumerate(parrafos))
    pasos = "\n".join(
        f"""            <tr><th scope="row">{p['paso']}</th><td>{
            valor_paso(p['valor'])}</td></tr>"""
        for p in e["pasos"])
    return f"""
        <div class="ejercicio-guiado">
          <p class="ejercicio-enunciado"><span class="ejercicio-numero">{k}.</span><strong>{e['titulo']}.</strong>
            {e['enunciado'].replace('`', '')}</p>
{datos}          <div class="ejercicio-acciones">
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
{lectura}
{codigo}          </div>
        </div>
"""


PISTAS = [
    "No calcules las distancias dos veces: la matriz muerte × bomba ya la tienes. Quitar una bomba es quedarse "
    "con las otras doce columnas y volver a tomar el mínimo por fila. Y separa los dos grupos ANTES de promediar; "
    "si promedias las 578 juntas, el efecto se diluye y no verás nada.",
    "Los dos intervalos se centran en la MISMA cifra, la media de los municipios, y lo que cambia entre ellos es "
    "la anchura. La media de las réplicas es otra cosa: la del remuestreo por departamentos no tiene por qué "
    "coincidir con la de los municipios, porque los departamentos no son del mismo tamaño, y una diferencia "
    "pequeña ahí no es un error del montaje. Para la última parte, no compares los dos intervalos entero contra "
    "entero: mira los dos tramos donde uno llega y el otro no.",
    "El apartado (a) es el módulo 4 con otro dato: entre los dos remuestreos solo cambia lo que se saca de la "
    "urna, estaciones sueltas o departamentos enteros con todas sus estaciones dentro. Para (b), despeja la "
    "correlación media de la fórmula del módulo 5 y escribe el límite de esa fórmula cuando n crece con la "
    "correlación fija. Para (c), vuelve a la tabla del módulo 5 que compara rellenar con ampliar. Para (d), los "
    "residuos se remuestrean igual que la temperatura: lo único que cambia es qué se ha tomado por media.",
    "Agrupa por CERCANÍA, no por departamento: así el efecto que veas será de la escala y no de dónde estén las "
    "fronteras. Y antes de responder «¿cuál es la correlación?», pregúntate si la pregunta está bien planteada.",
]

# Lo que el ejercicio 3 lleva además de su enunciado y su tabla: el enlace al
# archivo público —el mismo del Taller 1— y el código de la solución. Hasta
# R1 el ejercicio leía `datos/procesado/`, que no se publica, y no se podía
# hacer desde fuera.
e3s = S["e3"]["solucion"]
E3_ARCHIVO = pathlib.PurePosixPath(e3s["archivo"]).name
E3_DATOS = f"""          <p class="text-sm" style="margin:0.25rem 0 0.5rem;"><a href="../{e3s['archivo']}" download target="_blank" rel="noopener">
            Descargar <code>{E3_ARCHIVO}</code></a> — el archivo de estaciones del Taller&nbsp;1. El código de la
            solución lo busca en <code>{e3s['archivo']}</code>: esa ruta se cambia por la del lugar donde se
            haya guardado.</p>
"""
e3r = e3s["residuos"]
E3_CODIGO = tabs(
    "El ejercicio 3: los dos remuestreos, el tamaño efectivo y lo que implica",
    f"""library(sf)

# El archivo descargado: la ruta se cambia por la del lugar donde se guardo.
est3 &lt;- st_read("{e3s['archivo']}", quiet = TRUE)
temp &lt;- est3$t_media_anual
# El orden de los bloques, fijado por bytes ("radix"): si se deja al
# orden alfabetico de la maquina, la misma semilla elige otros
# departamentos en otra configuracion regional.
dep3 &lt;- factor(est3$departamento,
               levels = sort(unique(est3$departamento), method = "radix"))

# Las semillas y el orden son los del precalculo, asi que esto reproduce
# las cifras de la tabla EXACTAMENTE con el generador por defecto de R
# (el que da RNGkind(): Mersenne-Twister, Inversion, Rejection). Estan
# calculadas con {S['meta']['r'].split(' (')[0]}; con otro generador salen otras.
n_efectivo &lt;- function(y, B = {e3s['nboot']}) {{
  bloques &lt;- split(y, dep3)
  set.seed({e3s['semilla_iid']})
  ee_iid &lt;- sd(replicate(B, mean(sample(y, length(y), replace = TRUE))))
  set.seed({e3s['semilla_bloques']})
  ee_blq &lt;- sd(replicate(B, {{
    sel &lt;- sample(seq_along(bloques), length(bloques), replace = TRUE)
    mean(unlist(bloques[sel], use.names = FALSE))
  }}))
  c(ee_iid = ee_iid, ee_blq = ee_blq, n_eff = length(y) * (ee_iid / ee_blq)^2)
}}
# La correlacion media que corresponde a esa varianza, despejada de
# n_eff = n / (1 + (n - 1) rho), y lo que implica SI se mantiene fija.
n_para &lt;- function(m, rho) if (m * rho &gt;= 1) Inf else m * (1 - rho) / (1 - m * rho)
resume &lt;- function(r, n = length(temp)) {{
  rho &lt;- (n / r[["n_eff"]] - 1) / (n - 1)
  cat(sprintf("rho = %.5f | techo = %.5f | para {e3s['objetivos'][0]}: %.5f | para {e3s['objetivos'][1]}: %.5f\\n",
              rho, 1 / rho, n_para({e3s['objetivos'][0]}, rho), n_para({e3s['objetivos'][1]}, rho)))
}}

# (a) y (b), con la temperatura
a &lt;- n_efectivo(temp)
cat(sprintf("i.i.d. = %.5f | bloques = %.5f | n_eff = %.5f\\n",
            a[["ee_iid"]], a[["ee_blq"]], a[["n_eff"]]))
#&gt; i.i.d. = {n(e3s['ee_iid'])} | bloques = {n(e3s['ee_bloques'])} | n_eff = {n(e3s['n_eff'])}
resume(a)
#&gt; rho = {n(e3s['rho_medio'])} | techo = {n(e3s['techo'])} | para {e3s['objetivos'][0]}: {n(e3s['n_para_25'])} | para {e3s['objetivos'][1]}: Inf

# (d), con los residuos de la regresion sobre la altitud
ajuste &lt;- lm(temp ~ est3$altitud_m)
d &lt;- n_efectivo(unname(residuals(ajuste)))
cat(sprintf("R2 = %.5f | n_eff = %.5f\\n", summary(ajuste)$r.squared, d[["n_eff"]]))
#&gt; R2 = {n(e3r['r2'])} | n_eff = {n(e3r['n_eff'])}
resume(d)
#&gt; rho = {n(e3r['rho_medio'])} | techo = {n(e3r['techo'])} | para {e3s['objetivos'][0]}: {n(e3r['n_para_25'])} | para {e3s['objetivos'][1]}: {n(e3r['n_para_50'])}""",
    f"""import geopandas as gpd, numpy as np

est3 = gpd.read_file("{e3s['archivo']}")
temp = est3.t_media_anual.to_numpy()
dep = est3.departamento.to_numpy()

# OJO: esto NO reproduce las cifras de R. numpy y R tienen generadores
# distintos y la misma semilla no da las mismas replicas: las cifras salen
# parecidas, no iguales. Lo que no cambia es la conclusion, y es lo unico
# que se imprime.
def techo(y, B={e3s['nboot']}):
    rng = np.random.default_rng({e3s['semilla_iid']})
    grupos = [y[dep == k] for k in np.unique(dep)]
    ee_iid = np.std([rng.choice(y, y.size, replace=True).mean()
                     for _ in range(B)], ddof=1)
    ee_blq = np.std([np.concatenate([grupos[i] for i in
                     rng.integers(0, len(grupos), len(grupos))]).mean()
                     for _ in range(B)], ddof=1)
    n_eff = y.size * (ee_iid / ee_blq) ** 2
    return (y.size - 1) / (y.size / n_eff - 1)       # 1 / rho

# (a) y (b), con la temperatura
t_temp = techo(temp)
print(f"n = {{temp.size}}, {{np.unique(dep).size}} bloques | {e3s['objetivos'][0]} bajo el techo: "
      f"{{{e3s['objetivos'][0]} &lt; t_temp}} | {e3s['objetivos'][1]} bajo el techo: {{{e3s['objetivos'][1]} &lt; t_temp}}")
#> n = {e3s['n']}, {e3s['n_bloques']} bloques | {e3s['objetivos'][0]} bajo el techo: {e3s['objetivo_25_alcanzable']} | {e3s['objetivos'][1]} bajo el techo: {e3s['objetivo_50_alcanzable']}

# (d), con los residuos de la regresion sobre la altitud
alt = est3.altitud_m.to_numpy()
res = temp - np.polyval(np.polyfit(alt, temp, 1), alt)
t_res = techo(res)
print(f"con los residuos | {e3s['objetivos'][1]} bajo el techo: {{{e3s['objetivos'][1]} &lt; t_res}} | el techo sube: {{t_res &gt; t_temp}}")
#> con los residuos | {e3s['objetivos'][1]} bajo el techo: {e3r['objetivo_50_alcanzable']} | el techo sube: {e3r['techo_sube']}""")

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
{ejercicio(1, S['e1'])}{ejercicio(2, S['e2'])}{ejercicio(3, S['e3'], datos=E3_DATOS, codigo=E3_CODIGO)}{ejercicio(4, S['e4'])}
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
          nacionales del Ministerio de Educación Nacional traen coordenadas con dos decimales —1.1 km de
          resolución—, y en Bogotá las sedes con coordenada colapsaban en unos pocos cientos de posiciones
          distintas. Eso no es un patrón puntual, es una retícula de redondeo, y las funciones del capítulo 4
          estarían midiendo el redondeo. No se construye material sobre coordenadas que no se sostienen, por
          conveniente que sea el resto de sus campos.</p>
      </div>

      <div class="references">
        <h3><i class="fas fa-book-open mr-2" aria-hidden="true"></i>Lecturas de este capítulo</h3>
        <!-- Generada: el texto de cada cita y la lista de abajo los escribe genera_referencias.py
             desde bibliografia/referencias.json (Zotero). Solo las obras con ejemplar en el corpus
             llevan localizador, y cada uno está contrastado en bibliografia/contraste/cap1.yml. -->
        <ul style="margin-bottom:0;">
          <li data-afirma="c1-m12-01"><cite class="cita" data-ref="pebesma2023spatial" data-loc="§1.6" data-modo="narrativa"></cite>,
            el soporte de un dato espacial, y
            <cite class="cita" data-ref="pebesma2023spatial" data-loc="§7.1" data-modo="narrativa"></cite>, la anatomía de
            un objeto <code>sf</code>. Acceso abierto:
            <a href="https://r-spatial.org/book/" target="_blank" rel="noopener">r-spatial.org/book</a>.</li>
          <li data-afirma="c1-m12-02"><cite class="cita" data-ref="baddeley2015spatial" data-loc="cap. 3" data-modo="narrativa"></cite>,
            el objeto <code>ppp</code> y la ventana, y
            <cite class="cita" data-ref="baddeley2015spatial" data-loc="cap. 6" data-modo="narrativa"></cite>, la intensidad.</li>
          <li><cite class="cita" data-ref="cressie1993statistics" data-modo="narrativa"></cite>, para la teoría de los tres
            tipos de dato con más profundidad que este curso.</li>
          <li><cite class="cita" data-ref="bivand2013applied" data-modo="narrativa"></cite>, el ecosistema de paquetes
            de R espacial.</li>
          <li><cite class="cita" data-ref="tobler1970computer" data-modo="narrativa"></cite>, el artículo de la primera ley.
            <span data-afirma="c1-m12-03">Que llamarla «ley» es prematuro lo recogen
            <cite class="cita" data-ref="pebesma2023spatial" data-loc="§15.1" data-modo="narrativa"></cite>.</span></li>
          <li data-afirma="c1-m12-04"><cite class="cita" data-ref="moraga2019geospatial" data-loc="§1.1" data-modo="narrativa"></cite>,
            el caso de Snow, uno de los ejemplos más conocidos del análisis espacial. Acceso abierto:
            <a href="https://www.paulamoraga.com/book-geospatial/" target="_blank" rel="noopener">paulamoraga.com/book-geospatial</a>.</li>
        </ul>
        <h4 style="margin-top:1rem;">Referencias de este capítulo</h4>
        <!--REFERENCIAS-CAPITULO:inicio--><!--REFERENCIAS-CAPITULO:fin-->
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
# LAS DURACIONES DE LOS MÓDULOS 1, 3, 4, 7 Y 10 (R2 · T2.2). Los tres
# primeros crecieron con las gráficas de R2 · T2.4 y seguían anunciando lo
# de antes; el 7 y el 10 crecieron aquí.
#
# LA REGLA, para que se pueda rehacer: a la duración que el módulo tenía al
# cerrar R1 se le suma un minuto por cada 200 palabras de prosa añadidas
# (redondeando al minuto más próximo), dos por cada simulador nuevo y uno si
# gana mapas sin ganar simulador.
#
# EL RECUENTO: las palabras de cada `<template id="module-N">` del HTML
# publicado, quitando los bloques `<pre>`, las fórmulas `\(...\)` y `$$...$$`
# y las etiquetas, y partiendo por espacios. La referencia es el capítulo del
# commit cd97da7, el último de R1. Con ese recuento:
#   módulo 1    993 -> 1 860 palabras (+867) y un simulador más   12 -> 18 min
#   módulo 3  2 240 -> 3 014 (+774)                               10 -> 14 min
#   módulo 4  1 512 -> 1 975 (+463) y un simulador más            12 -> 16 min
#   módulo 7  1 999 -> 2 107 (+108)                               14 -> 15 min
#   módulo 10 1 254 -> 1 316 (+62) y los dos mapas de pliegues    13 -> 14 min
# El guion que cuenta está en `diagnostico_cap1/palabras_por_modulo.py`.
MODULOS_NAV = [
    ("El mapa que cambió la epidemiología", "18 min"),
    ("Los tres tipos de dato espacial", "14 min"),
    ("La primera ley de Tobler", "14 min"),
    ("Por qué se rompe la inferencia clásica", "16 min"),
    ("Tamaño de muestra efectivo", "8 min"),
    ("Estacionariedad y una sola realización", "10 min"),
    ("Escala, soporte y agregación", "15 min"),
    ("El ecosistema de R espacial", "8 min"),
    ("Anatomía de un objeto sf", "8 min"),
    ("Dependencia espacial en ciencia de datos", "14 min"),
    ("Glosario de notación del curso", "5 min"),
    ("Autoevaluación y ejercicios guiados", "15 min"),
]

_mods = ",\n".join(
    f'        {{ id: {i + 1}, title: "{t}", duration: "{d}" }}'
    for i, (t, d) in enumerate(MODULOS_NAV))

_sim = {"campos": M["campos"], "realizaciones": M["realizaciones"]}

COURSE_DATA = f"""    const courseData = {{
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
    // Millares con el espacio fino, como `ent()` en la prosa. Hasta el
    // 2026-09-25 esto era `toLocaleString('es-CO')`, que agrupa con PUNTO:
    // la lectura del módulo 7 escribía «2.621 donde había 667», y en un
    // capítulo que escribe los decimales con punto eso se lee «dos y
    // pico». `audita_texto_cap1.py` para el documento si vuelve.
    const miles1 = x => String(Math.round(Number(x))).replace(/\\B(?=(\\d{{3}})+$)/g, '\\u202f');
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

# R2 · T2.2 (G-24): las tablas de respaldo de los mapas que no la tenían.
# Ninguna calcula una cifra nueva: las coordenadas de un patrón puntual se
# leen de los mismos enteros que pinta el lienzo —deshaciendo la
# cuantización, que es una regla de tres— y los resúmenes vienen de R.

# La rampa de la temperatura (G-05): secuencial, de oscuro a claro y de
# frío a cálido. Son siete paradas de la escala «plasma».
PALETA_TERMICA = ["#0d0887", "#5c01a6", "#9c179e", "#cc4778", "#ed7953", "#fdb42f", "#f0f921"]

# De los enteros del mapa a las unidades del dato: la inversa exacta de
# `geo_qxy()` de R. Va como función suelta porque la usan tres tablas.
COORDS_JS = """    // De los enteros cuantizados de un mapa a las unidades de su dato.
    function coordsDeMapa(d) {
      const c = d.caja, rx = c[2] - c[0], ry = c[3] - c[1], r = Math.max(rx, ry);
      const x0 = c[0] + rx / 2 - r / 2, y0 = c[1] + ry / 2 - r / 2;
      const xy = [];
      for (let i = 0; i < d.pts.length; i += 2) {
        xy.push([d.pts[i] / d.q * r + x0, d.pts[i + 1] / d.q * r + y0]);
      }
      return xy;
    }
"""

# Los tres patrones canónicos: sus coordenadas, con tres decimales, que es
# la resolución del lienzo sobre una ventana de lado 1 (1/4096). La guarda
# de salida las compara con las del dato, punto a punto.
TABLA_PUNTOS = """      tabla: function (d) {
        const filas = coordsDeMapa(d).map((p, i) => `<tr><th scope="row">${i + 1}</th>`
          + `<td>${p[0].toFixed(3)}</td><td>${p[1].toFixed(3)}</td></tr>`).join('');
        return `<table><caption>Coordenadas de los ${d.n} puntos de «${d.titulo}», en unidades de la `
          + `ventana.</caption><thead><tr><th scope="col">Punto</th><th scope="col">x</th>`
          + `<th scope="col">y</th></tr></thead><tbody>${filas}</tbody></table>`;
      }"""

# El Mosa: posición y zinc de cada punto. Las coordenadas salen del lienzo,
# cuya resolución aquí es de un metro escaso: van al metro, y la guarda de
# salida comprueba que ninguna se aparta más de uno de la del dato.
TABLA_MEUSE = """      tabla: function (d) {
        const filas = coordsDeMapa(d).map((p, i) => `<tr><th scope="row">${i + 1}</th>`
          + `<td>${Math.round(p[0])}</td><td>${Math.round(p[1])}</td><td>${d.marcas[i]}</td></tr>`).join('');
        return `<table><caption>${d.titulo}: posición y zinc de los ${d.n} puntos de muestreo. `
          + `Las coordenadas van en metros del sistema holandés (EPSG:${D1.geo_canonico.crs_epsg}), `
          + `leídas del dibujo y redondeadas al metro.</caption><thead><tr>`
          + `<th scope="col">Punto</th><th scope="col">x (m)</th><th scope="col">y (m)</th>`
          + `<th scope="col">zinc (ppm)</th></tr></thead><tbody>${filas}</tbody></table>`;
      }"""

# Bogotá: 2 209 filas de coordenadas no son una tabla que alguien lea. Va
# lo que el mapa deja ver, contado por R: cuántas sedes hay en cada tercio
# del dibujo, de norte a sur.
TABLA_BOGOTA = """      tabla: function (d) {
        const v = D1.visto.bogota;
        const filas = v.franja.map((f, i) => `<tr><th scope="row">tercio ${f}</th>`
          + `<td>${miles1(v.n[i])}</td><td>${n5(100 * v.n[i] / d.n, 1)}</td></tr>`).join('');
        return `<table><caption>${d.titulo}: las ${miles1(d.n)} sedes por tercio del dibujo, de norte a sur. `
          + `Las coordenadas de cada una están en el archivo de datos del curso.</caption><thead><tr>`
          + `<th scope="col">Franja</th><th scope="col">Sedes</th><th scope="col">% del total</th>`
          + `</tr></thead><tbody>${filas}</tbody></table>`;
      }"""

# IDEAM: las estaciones por franja de altitud, con su temperatura media.
# Es la tabla que dice lo que el mapa enseña con el color.
TABLA_IDEAM = """      tabla: function (d) {
        const filas = D1.visto.ideam.por_altitud.map(f => `<tr><th scope="row">de ${miles1(f.desde)} a `
          + `menos de ${miles1(f.hasta)} m</th><td>${f.n}</td><td>${n5(f.t_media, 1)}</td></tr>`).join('');
        return `<table><caption>${d.titulo}: las ${d.n} estaciones por franja de altitud.</caption>`
          + `<thead><tr><th scope="col">Altitud</th><th scope="col">Estaciones</th>`
          + `<th scope="col">Temperatura media (°C)</th></tr></thead><tbody>${filas}</tbody></table>`;
      }"""

# Las retículas simuladas: cuántas celdas caen en cada clase de la leyenda.
# El recuento lo trae R (`tam`), con los mismos cortes.
TABLA_REJILLA = """      tabla: function (d) {
        const filas = d.tam.map((k, i) => `<tr><th scope="row">de ${n5(d.cortes[i], 2)} a `
          + `${n5(d.cortes[i + 1], 2)}</th><td>${k}</td></tr>`).join('');
        return `<table><caption>${d.titulo}: celdas en cada clase de la leyenda, de las `
          + `${d.nx * d.ny}.</caption><thead><tr><th scope="col">Valor de z</th>`
          + `<th scope="col">Celdas</th></tr></thead><tbody>${filas}</tbody></table>`;
      }"""

# Los pliegues de la validación cruzada: cuántas estaciones tiene cada uno.
TABLA_PLIEGUES = """      tabla: function (d) {
        const cuenta = new Array(D1.cv_espacial.n_pliegues).fill(0);
        d.marcas.forEach(m => { cuenta[m - 1]++; });
        const filas = cuenta.map((k, i) => `<tr><th scope="row">pliegue ${i + 1}</th>`
          + `<td>${k}</td></tr>`).join('');
        return `<table><caption>${d.titulo}: estaciones en cada pliegue, de las ${d.n}.</caption>`
          + `<thead><tr><th scope="col">Pliegue</th><th scope="col">Estaciones</th></tr></thead>`
          + `<tbody>${filas}</tbody></table>`;
      }"""

# =====================================================================
# «Describir el mapa» (2026-11-02)
# =====================================================================
# Lo que se VE en cada mapa, para quien no lo ve: la etiqueta dice qué es
# el mapa; esto, qué enseña. El motor lo pone en el desplegable «Describir
# el mapa» y lo enlaza al lienzo para el lector de pantalla (ver
# `describe_mapa.py`). Los mapas que cambian con un control —Snow, el campo,
# las realizaciones, la agregación— llevan un texto por estado, y el
# registro lo elige con la misma variable que elige lo que se pinta. Las
# cifras salen del JSON —lo que faltaba lo publica R en `visto`—, y cada
# frase sobre la forma tiene su guarda en `guardas_de_las_descripciones()`.
from describe_mapa import lista_y, revisa_textos  # noqa: E402

_VI = D["visto"]
_SN = D["snow"]
_D1_SNOW = {
    "broad": (
        f"Las {ent(_SN['n_muertes'])} muertes se apiñan en las calles alrededor de una sola bomba, la de "
        f"Broad Street, resaltada: {ent(_SN['n_mas_cerca_broad'])} de ellas, el "
        f"{n(_SN['pct_mas_cerca_broad'], 1)} %, la tienen como la más próxima, "
        f"{n(_SN['razon_sobre_uniforme'], 1)} veces lo que le tocaría si se repartieran parejo entre las "
        f"{ent(_SN['n_bombas'])} bombas. Unas líneas a trazos parten el plano en las {ent(_SN['n_bombas'])} "
        f"celdas de las bombas —lo que queda más cerca de cada una—, y la de Broad Street, en el centro, "
        f"lleva el borde naranja: esas muertes son las que caen dentro."),
    "todas": (
        f"Un color por cada una de las {ent(_SN['n_bombas'])} bombas, según cuál le queda más cerca a cada "
        f"muerte: el de Broad Street, naranja, cubre la mancha del centro, con "
        f"{ent(_SN['n_mas_cerca_broad'])} de las {ent(_SN['n_muertes'])}, y las demás bombas se reparten el "
        f"resto. Las líneas a trazos son los bordes de las celdas: cada color queda dentro de la suya."),
    "sinlineas": (
        f"Sin las calles de fondo, las {ent(_SN['n_muertes'])} muertes siguen formando la misma mancha, "
        f"apretada alrededor de la bomba de Broad Street: no la dibujaban las calles."),
}
_T1_SNOW = {
    "broad": "Muertes por cólera, Soho, 1854: las que tienen más cerca la bomba de Broad Street, contra el resto",
    "todas": "Muertes por cólera, Soho, 1854, coloreadas por su bomba más próxima",
    "sinlineas": "Muertes por cólera, Soho, 1854, coloreadas por su bomba más próxima, sin las calles",
}
_PC = D["puntual_canonico"]
DESC_PINOS = (
    f"Los {ent(_PC['japanesepines']['n'])} pinos se reparten sin orden aparente, sin grumos marcados ni "
    f"distancias regulares: la distancia media al vecino más próximo, "
    f"{n(_PC['japanesepines']['nn_media'], 3)}, es casi la que daría el azar, "
    f"{n(_PC['japanesepines']['nn_esperada'], 3)}.")
DESC_SECUOYAS = (
    f"Las {ent(_PC['redwood']['n'])} plántulas se amontonan en grumos, con mucho vacío entre ellos: la "
    f"distancia media al vecino más próximo, {n(_PC['redwood']['nn_media'], 3)}, es poco más de la mitad "
    f"de la que daría el azar, {n(_PC['redwood']['nn_esperada'], 3)}.")
DESC_CELULAS = (
    f"Las {ent(_PC['cells']['n'])} células se reparten casi como una rejilla, sin parejas pegadas: la "
    f"distancia media al vecino más próximo, {n(_PC['cells']['nn_media'], 3)}, es "
    f"{n(_PC['cells']['clark_evans'], 1)} veces la que daría el azar, {n(_PC['cells']['nn_esperada'], 3)}.")
_BG = dict(zip(_VI["bogota"]["franja"], _VI["bogota"]["n"]))
DESC_BOGOTA = (
    f"Las {ent(D['colombia']['puntual']['n'])} sedes se apiñan en el tercio norte del dibujo, que es la "
    f"ciudad: {ent(_BG['norte'])}. El tercio del medio y el del sur, el suelo rural del Distrito, tienen "
    f"{ent(_BG['centro'])} y {ent(_BG['sur'])}.")
_NC1 = M["nc"]
_nc_top = sorted(zip(_NC1["valor"], _NC1["etiquetas"]), key=lambda t: (-t[0], t[1]))
_VNC1 = _VI["nc"]
DESC_NC = (
    f"Con cuantiles cada color reúne unos {ent(_NC1['tam'][-1])} condados. Los "
    f"{ent(_VNC1['clase_alta_n'])} de la clase más oscura, de {n(_NC1['cortes'][-2], 2)} a "
    f"{n(_NC1['cortes'][-1], 2)} muertes por 1 000 nacimientos, salen repartidos por todo el estado, con "
    f"más en el {_VNC1['zona'][0]} del dibujo ({ent(_VNC1['n'][0])}); los más altos son "
    + lista_y([f"{nom} ({n(v, 2)})" for v, nom in _nc_top[:2]]) + ".")
_DS = _VI["desercion"]
_corto = lambda d: "el archipiélago de San Andrés" if d.startswith("Archipiélago") else d
DESC_DESERCION = (
    f"Lo más oscuro está en el sur y el oriente del país: "
    + lista_y([f"{_corto(f['departamento'])} ({n(f['pct'], 2)} %)" for f in _DS["mayores"]])
    + ". Lo más claro, en "
    + lista_y([f"{_corto(f['departamento'])} ({n(f['pct'], 2)} %)" for f in _DS["menores"]]) + ".")
_GC = D["geo_canonico"]
DESC_MEUSE = (
    f"Los {ent(_GC['n'])} puntos de muestreo, coloreados por su zinc, de {ent(_GC['zinc_min'])} a "
    f"{ent(_GC['zinc_max'])} ppm, en una nube alargada en diagonal. El río, dibujado con las dos líneas "
    f"de sus orillas, la bordea por el noroeste y la rodea por el sur. Los puntos más oscuros se alinean "
    f"a lo largo de ese borde noroeste, pegados a la orilla, y el color se aclara al alejarse de ella: la "
    f"correlación del zinc con la distancia al río es {n(_GC['corr_dist_rio'], 2)}. El color recorre el "
    f"logaritmo del zinc.")
_GEO = D["colombia"]["geo"]
_FR, _CA = _VI["ideam"]["frias"], _VI["ideam"]["calidas"]
DESC_IDEAM = (
    f"Las {ent(_GEO['n'])} estaciones, con el contorno del país de fondo, coloreadas por su temperatura "
    f"media. Las del archipiélago de San Andrés, arriba a la izquierda, se ven sobre el mar: a esta escala "
    f"las islas son más pequeñas que un punto. La temperatura va de "
    f"{n(_GEO['t_min'], 1)} °C, en violeta oscuro, a {n(_GEO['t_max'], 1)} °C, en amarillo. Las más frías, de {n(_VI['ideam']['frias_umbral'], 1)} °C o menos, caen "
    f"casi todas en el {_FR['zona'][0]} del dibujo ({ent(_FR['n'][0])}), donde están las más altas: la "
    f"temperatura cambia {n(_GEO['gradiente'], 1)} °C por cada kilómetro de altura. Las más cálidas, de "
    f"{n(_VI['ideam']['calidas_umbral'], 1)} °C o más, en el {_CA['zona'][0]} ({ent(_CA['n'][0])}) y en el "
    f"{_CA['zona'][1]} ({ent(_CA['n'][1])}).")


def _palabra_campo(rho):
    if rho == 0:
        return "un granulado sin manchas, cada celda por su lado"
    if rho < 0.5:
        return "manchas pequeñas, de pocas celdas"
    if rho < 0.85:
        return "manchas de varias celdas"
    return "manchas grandes y suaves"


DESC_CAMPO = {
    str(c["phi"]): (
        f"Con alcance {ent(c['phi']) if c['phi'] == int(c['phi']) else n(c['phi'], 1)}, dos celdas vecinas "
        f"de la retícula tienen correlación "
        f"{n(c['rho_vecino'], 2)} y el I de Moran del mapa es {n(c['moran'], 2)}: "
        f"{_palabra_campo(c['rho_vecino'])}.")
    for c in M["campos"]}
DESC_REAL = {
    str(r["id"]): (
        f"La realización {ent(r['id'])} del mismo proceso: la retícula tiene media {n(r['media_espacial'], 2)} "
        f"y desviación {n(r['sd_espacial'], 2)}. De una realización a otra las manchas cambian de sitio y "
        f"de tamaño, y la media se mueve, aunque el proceso que las genera es el mismo.")
    for r in M["realizaciones"]}
_AG = D["agregacion_soporte"]["nc"]
_CC = _AG["condado_caso"]
_apor = [r["aporte_area"] for r in _CC["reparto"]]
_ZM = M["agregacion"]["zoom"]
_BASE_AGREG = {
    "estado": (
        f"Los condados, coloreados por sus muertes súbitas, bajo una rejilla de {ent(_AG['n_celdas'])} "
        f"rectángulos que no sigue ningún límite. {_CC['nombre']}, en naranja, cae en "
        f"{ent(_CC['n_celdas_toca'])} celdas, resaltadas. "),
    "zoom": (
        f"La zona de {_CC['nombre']}, acercada: {ent(_ZM['n_celdas'])} rectángulos enteros de los "
        f"{ent(_AG['n_celdas'])} de la rejilla, en {ent(_ZM['columnas'])} columnas y {ent(_ZM['filas'])} "
        f"filas, con el borde de los que los rodean asomando por los lados, sobre los condados coloreados "
        f"por sus muertes súbitas. El condado, en naranja, cae en "
        f"{ent(_CC['n_celdas_toca'])} celdas, resaltadas. "),
}
_REGLA_AGREG = {
    "predicado": (
        f"Con «se tocan», esas {ent(_CC['n_celdas_toca'])} celdas reciben todas lo mismo, "
        f"{ent(_CC['sids'])}: el condado entero en cada una."),
    "area": (
        f"Repartiendo por área, esas {ent(_CC['n_celdas_toca'])} celdas reciben cifras distintas, de "
        f"{n(min(_apor), 4)} en la que apenas roza a {n(max(_apor), 2)} en la que más condado cubre, y "
        f"entre todas suman sus {ent(_CC['sids'])}."),
}
# Una descripción por estado del mapa: la regla y el encuadre. Solo el
# encuadre acercado lleva las cifras escritas dentro de las celdas.
DESC_AGREG = {
    f"{regla}-{vista}": _BASE_AGREG[vista] + _REGLA_AGREG[regla]
    + (" Cada celda resaltada lleva su cifra escrita dentro." if vista == "zoom" else "")
    for regla in _REGLA_AGREG for vista in _BASE_AGREG}
_CV = D["cv_espacial"]
DESC_PLIEGUES = {
    "aleatorio": (
        f"Cada estación lleva el color de su pliegue, y los {ent(_CV['n_pliegues'])} colores salen mezclados "
        f"por todo el mapa: de las {ent(_CV['n'])} estaciones, solo "
        f"{ent(_CV['vecina_en_su_pliegue_aleatoria'])} tienen a su vecina más próxima en su mismo pliegue. "
        f"Cuando a una estación le toca la prueba, casi siempre tiene al lado una del entrenamiento."),
    "bloques": (
        f"Cada estación lleva el color de su pliegue, y cada color ocupa una región del mapa: "
        f"{ent(_CV['vecina_en_su_pliegue_bloques'])} de las {ent(_CV['n'])} estaciones tienen a su vecina "
        f"más próxima en su mismo pliegue. Cuando a una región le toca la prueba, sus estaciones se "
        f"predicen con las de otras regiones."),
}
TITULO_PLIEGUES = {
    "aleatorio": f"Los {ent(_CV['n_pliegues'])} pliegues, repartidos al azar",
    "bloques": f"Los {ent(_CV['n_pliegues'])} pliegues, por bloques espaciales",
}
DESCRIPCIONES = {
    "cap1-pliegues-azar": [DESC_PLIEGUES["aleatorio"]], "cap1-pliegues-bloques": [DESC_PLIEGUES["bloques"]],
    "cap1-snow": [_D1_SNOW["broad"], _D1_SNOW["todas"], _D1_SNOW["sinlineas"]],
    "cap1-pinos": [DESC_PINOS], "cap1-secuoyas": [DESC_SECUOYAS], "cap1-celulas": [DESC_CELULAS],
    "cap1-bogota": [DESC_BOGOTA], "cap1-nc": [DESC_NC], "cap1-desercion": [DESC_DESERCION],
    "cap1-meuse": [DESC_MEUSE], "cap1-ideam": [DESC_IDEAM],
    "cap1-campo": list(DESC_CAMPO.values()), "cap1-realizacion": list(DESC_REAL.values()),
    "cap1-agregacion": list(DESC_AGREG.values()),
}


def guardas_de_las_descripciones() -> list[str]:
    """Lo que las descripciones afirman de la forma de cada mapa, contra el dato."""
    malos = []

    def exige(cond, que):
        if not cond:
            malos.append(que)

    exige(_SN["pct_mas_cerca_broad"] > 50 and _SN["razon_sobre_uniforme"] > 2,
          "Snow: «se apiñan alrededor de una sola bomba» ya no vale")
    exige(abs(_PC["japanesepines"]["clark_evans"] - 1) < 0.15, "pinos: «casi lo que daría el azar» ya no vale")
    exige(0.5 < _PC["redwood"]["clark_evans"] < 0.75, "secuoyas: «poco más de la mitad del azar» ya no vale")
    exige(_PC["cells"]["clark_evans"] > 1.3, "células: «casi como una rejilla» ya no vale")
    exige(_BG["norte"] * 20 > D["colombia"]["puntual"]["n"] * 19 and sum(_VI["bogota"]["n"]) == D["colombia"]["puntual"]["n"],
          "Bogotá: «se apiñan en el tercio norte» ya no vale, o las franjas no reparten las sedes")
    exige(_VNC1["clase_alta_n"] == _NC1["tam"][-1] and len(_VNC1["zona"]) >= 5 and _VNC1["n"][0] > _VNC1["n"][1],
          "Carolina del Norte: «repartidos por todo el estado, con más en una zona» ya no vale")
    exige(all(f["zona"] in ("sur", "oriente", "suroriente") for f in _DS["mayores"]),
          "deserción: «lo más oscuro en el sur y el oriente» ya no vale")
    exige(_GC["corr_dist_rio"] < -0.5, "zinc: «se pegan al río» y la correlación con la distancia no es negativa y fuerte")
    # «A lo largo de su borde noroeste»: con los puntos y el zinc del mapa
    # PUBLICADO, el eje principal de la nube y, de los 16 con más zinc (el
    # décimo superior), cuántos caen del lado noroeste de ese eje.
    import math
    mz = M["meuse"]
    px, py, zz = mz["pts"][0::2], mz["pts"][1::2], mz["marcas"]
    mx, my = sum(px) / len(px), sum(py) / len(py)
    sxx = sum((a - mx) ** 2 for a in px)
    syy = sum((b - my) ** 2 for b in py)
    sxy = sum((a - mx) * (b - my) for a, b in zip(px, py))
    ang = 0.5 * math.atan2(2 * sxy, sxx - syy)
    nx, ny = -math.sin(ang), math.cos(ang)
    if nx > 0 or ny < 0:
        nx, ny = -nx, -ny
    top = sorted(range(len(zz)), key=lambda i: -zz[i])[:max(1, len(zz) // 10)]
    nw = sum(((px[i] - mx) * nx + (py[i] - my) * ny) > 0 for i in top)
    exige(len(px) == len(zz) and nw * 4 >= len(top) * 3 and sxy > 0,
          f"zinc: «a lo largo de su borde noroeste, en una nube en diagonal» ya no vale ({nw} de {len(top)})")
    exige(_GEO["corr_alt"] < -0.9 and _FR["n"][0] * 10 > sum(_FR["n"]) * 7,
          "IDEAM: «las frías, casi todas en una zona, donde están las más altas» ya no vale")
    rhos = [c["rho_vecino"] for c in M["campos"]]
    morans = [c["moran"] for c in M["campos"]]
    exige(rhos == sorted(rhos) and morans == sorted(morans) and rhos[0] == 0,
          "campo: la correlación entre vecinas o el I de Moran ya no crecen con el alcance")
    exige({str(r["phi"]) for r in D["inferencia"]["rejilla"]} == set(DESC_CAMPO),
          "campo: los alcances del deslizador no son los que tienen texto")
    exige({str(v["id"]) for v in D["realizaciones_vistas"]} == set(DESC_REAL),
          "realizaciones: las vistas no son las que tienen texto")
    exige(_CC["n_celdas_toca"] == len(_CC["reparto"]) and len(set(_apor)) == len(_apor)
          and abs(sum(_apor) - _CC["sids"]) < 1e-6,
          "agregación: «cifras distintas que suman sus muertes» ya no vale")
    return malos



# =====================================================================
# Las guardas de R2 · T2.2: lo que las gráficas y los mapas afirman
# =====================================================================
def _coords_de_mapa(g):
    """La inversa de `geo_qxy()`: de los enteros del mapa a las unidades del dato.

    La misma cuenta que `coordsDeMapa()` en el navegador, escrita aparte.
    """
    c = g["caja"]
    rx, ry = c[2] - c[0], c[3] - c[1]
    r = max(rx, ry)
    x0, y0 = c[0] + rx / 2 - r / 2, c[1] + ry / 2 - r / 2
    return [(g["pts"][i] / g["q"] * r + x0, g["pts"][i + 1] / g["q"] * r + y0)
            for i in range(0, len(g["pts"]), 2)]


def _dentro(x, y, pol):
    """¿Cae (x, y) dentro del polígono `pol` (lista plana de vértices)?"""
    n, dentro = len(pol) // 2, False
    for i in range(n):
        x1, y1 = pol[2 * i], pol[2 * i + 1]
        x2, y2 = pol[2 * ((i + 1) % n)], pol[2 * ((i + 1) % n) + 1]
        if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1) + x1:
            dentro = not dentro
    return dentro


def _a_borde(x, y, pol):
    """La distancia de (x, y) al borde del polígono, en las unidades del polígono."""
    import math
    n, mejor = len(pol) // 2, float("inf")
    for i in range(n):
        x1, y1 = pol[2 * i], pol[2 * i + 1]
        x2, y2 = pol[2 * ((i + 1) % n)], pol[2 * ((i + 1) % n) + 1]
        dx, dy = x2 - x1, y2 - y1
        t = 0 if dx == dy == 0 else max(0, min(1, ((x - x1) * dx + (y - y1) * dy) / (dx * dx + dy * dy)))
        mejor = min(mejor, math.hypot(x - x1 - t * dx, y - y1 - t * dy))
    return mejor


def _claridad(hexa):
    """Luminancia relativa de un color `#rrggbb` (sRGB)."""
    def lin(u):
        u /= 255
        return u / 12.92 if u <= 0.04045 else ((u + 0.055) / 1.055) ** 2.4
    r, g, b = (int(hexa[i:i + 2], 16) for i in (1, 3, 5))
    return 0.2126 * lin(r) + 0.7152 * lin(g) + 0.0722 * lin(b)


def guardas_de_t22(plantilla: str, marcado: str) -> list[str]:
    """Lo que los mapas y gráficos de R2 · T2.2 dan por sabido, contra el dato."""
    import csv
    malos = []
    # Los CSV del dato crudo, que escribe R junto a los JSON. Con el arnés de
    # inyección este guion corre desde una copia: `ESPACIAL_RAIZ` dice dónde
    # está el árbol de verdad, como para la bibliografía.
    crudos = pathlib.Path(os.environ.get("ESPACIAL_RAIZ") or RAIZ) / "precalculo" / "salidas"

    def exige(cond, que):
        if not cond:
            malos.append(que)

    # --- G-09: la banda del marcador, en unidades del eje -----------------
    exige("eje.getPixelForValue(i - medio)" in SIMULADORES_JS and "fillRect(x - 10" not in SIMULADORES_JS,
          "marcador: la banda vuelve a medirse en píxeles y no en unidades del eje")

    # --- G-20: las celdas de Snow y el naranja de Broad Street ------------
    sn, ms = D["snow"], M["snow"]
    celdas = ms.get("celdas", [])
    exige(len(celdas) == sn["n_bombas"], "Snow: no hay una celda por bomba")
    if len(celdas) == sn["n_bombas"]:
        fuera = 0
        for i, marca in enumerate(ms["marcas"]):
            x, y = ms["pts"][2 * i], ms["pts"][2 * i + 1]
            pol = celdas[marca - 1]
            # Dos unidades de la cuantización de holgura: una muerte pegada
            # al borde de su celda puede caer del otro lado al redondear.
            if not _dentro(x, y, pol) and _a_borde(x, y, pol) > 2:
                fuera += 1
        exige(fuera == 0, f"Snow: {fuera} muerte(s) fuera de la celda de la bomba que llevan por marca")
        # Cada bomba, dentro de su propia celda.
        exige(all(_dentro(ms["puntos2"][2 * k], ms["puntos2"][2 * k + 1], celdas[k])
                  for k in range(sn["n_bombas"])), "Snow: alguna bomba no cae en su celda")
    exige(ms.get("leyenda") == "", "Snow: el mapa vuelve a llevar pie de leyenda, debajo de las entradas")
    import re as _re
    m = _re.search(r"const GEOMAPA_CUALITATIVA = \[(.*?)\];", plantilla, _re.S)
    cual = _re.findall(r"'(#[0-9A-Fa-f]{6})'", m.group(1)) if m else []
    exige(len(cual) >= sn["n_bombas"] and cual.count("#D55E00") == 1
          and cual.index("#D55E00") != sn["bomba_broad"] - 1,
          "Snow: la paleta cualitativa de la plantilla ya no es la que el cambio de color da por sabida")
    exige(cual.count("#E69F00") == 1 and "#F0E442" not in [c.upper() for c in cual],
          "Snow: la paleta de la plantilla ya no trae el ámbar que se cambia por amarillo, o ya trae ese amarillo")
    exige("#FF6600" not in [c.upper() for c in cual],
          "Snow: la paleta cualitativa ya trae el naranja del acento: dos bombas saldrían del mismo color")
    exige("const GEOMAPA_ACENTO = '#FF6600';" in plantilla, "Snow: el acento de la plantilla ya no es el naranja")

    # --- G-04: el Mosa -----------------------------------------------------
    mm = M["meuse"]
    exige(mm.get("marcas_escala") == "log" and min(mm["marcas"]) > 0,
          "Mosa: la rampa del zinc ya no recorre el logaritmo")
    exige(len(mm.get("lineas", [])) == 2 and all(len(l) >= 8 for l in mm["lineas"]),
          "Mosa: el mapa no trae las dos orillas del río")
    with open(crudos / "cap1_meuse.csv", encoding="utf-8") as f:
        crudo = list(csv.DictReader(f))
    xy = _coords_de_mapa(mm)
    exige(len(crudo) == len(xy) and all(
        abs(round(px) - float(c["x"])) <= 1 and abs(round(py) - float(c["y"])) <= 1
        and float(c["zinc"]) == z for (px, py), c, z in zip(xy, crudo, mm["marcas"])),
        "Mosa: la tabla de respaldo no da la posición (al metro) o el zinc del dato")

    # --- G-24: las coordenadas de los tres patrones ------------------------
    with open(crudos / "cap1_ppp.csv", encoding="utf-8") as f:
        ppp = list(csv.DictReader(f))
    for clave in ("japanesepines", "redwood", "cells"):
        dato = [(float(c["x"]), float(c["y"])) for c in ppp if c["patron"] == clave]
        mapa = _coords_de_mapa(M[clave])
        exige(len(dato) == len(mapa) and all(
            f"{a:.3f}" == f"{round(b, 3) + 0:.3f}" and f"{c:.3f}" == f"{round(d, 3) + 0:.3f}"
            for (a, c), (b, d) in zip(mapa, dato)),
            f"{clave}: la tabla de respaldo no da las coordenadas del dato a tres decimales")

    # --- G-05: la temperatura ------------------------------------------------
    luz = [_claridad(c) for c in PALETA_TERMICA]
    exige(all(a < b for a, b in zip(luz, luz[1:])),
          "IDEAM: la rampa de la temperatura no va de oscuro a claro de punta a punta")
    exige(_re.search(r"\btermica\s*:", plantilla) is None,
          "IDEAM: la plantilla ya trae una paleta «termica» y este capítulo la pisaría")
    exige(len(M["ideam"].get("lineas", [])) >= 1, "IDEAM: el mapa no trae el contorno del país")
    # «Las del archipiélago de San Andrés, arriba a la izquierda, se ven sobre
    # el mar»: hay estaciones en la esquina noroeste del dibujo, y ninguna de
    # ellas cae dentro de un anillo del contorno que se llegue a ver (los de
    # las islas miden menos que un punto).
    mi = M["ideam"]
    esquina = [(mi["pts"][i], mi["pts"][i + 1]) for i in range(0, len(mi["pts"]), 2)
               if mi["pts"][i] < mi["q"] / 4 and mi["pts"][i + 1] > 3 * mi["q"] / 4]
    visibles = [l for l in mi.get("lineas", [])
                if max(l[0::2]) - min(l[0::2]) > 40 or max(l[1::2]) - min(l[1::2]) > 40]
    exige(esquina and visibles and not any(_dentro(x, y, l) for x, y in esquina for l in visibles),
          "IDEAM: «las de San Andrés, arriba a la izquierda, se ven sobre el mar» ya no vale")
    pa = D["visto"]["ideam"]["por_altitud"]
    exige(sum(f["n"] for f in pa) == D["colombia"]["geo"]["n"]
          and all(a["hasta"] == b["desde"] for a, b in zip(pa, pa[1:]))
          and all(a["t_media"] > b["t_media"] for a, b in zip(pa, pa[1:])),
          "IDEAM: las franjas de altitud no reparten las estaciones, o la temperatura ya no baja con la altura")

    # --- G-06 y G-07: los campos y las realizaciones ------------------------
    inf = D["inferencia"]
    for familia, lista in (("campo", M["campos"]), ("realización", M["realizaciones"])):
        for g in lista:
            c = g["cortes"]
            exige(g.get("centro") == 0 and abs(g["rango"][0] + g["rango"][1]) < 1e-6
                  and all(abs(c[k] + c[-1 - k]) < 1e-6 for k in range(len(c)))
                  and len(c) % 2 == 0,
                  f"{familia}: la escala ya no es simétrica y centrada en 0 («{g['titulo']}»)")
            exige(sum(g.get("tam", [])) == g["nx"] * g["ny"] and len(g.get("tam", [])) == len(c) - 1,
                  f"{familia}: `tam` no reparte las celdas entre las clases («{g['titulo']}»)")
        exige(len({tuple(g["rango"]) for g in lista}) == 1,
              f"{familia}: los mapas de la familia ya no comparten escala")
    exige(all(g["nx"] == inf["k"] and g["ny"] == inf["k"] for g in M["campos"]),
          "campo: el mapa ya no va en la retícula de la simulación")
    c4 = [g for g in M["campos"] if g["phi"] == inf["cien_ic"]["phi"]]
    exige(len(c4) == 1 and abs(c4[0]["media_espacial"] - inf["cien_ic"]["media"][0]) < 1e-6,
          "campo: el del alcance destacado ya no es la réplica 1 de la simulación")
    exige(not any("rango" in g["titulo"] for g in M["campos"]),
          "campo: el título vuelve a llamar «rango» al alcance")

    # --- G-13: el encuadre acercado ------------------------------------------
    ma = M["agregacion"]
    z = ma.get("zoom", {})
    cj, cz = ma["caja"], z.get("caja", [0, 0, 0, 0])
    exige(cj[0] - 1e-6 <= cz[0] < cz[2] <= cj[2] + 1e-6 and cj[1] - 1e-6 <= cz[1] < cz[3] <= cj[3] + 1e-6,
          "agregación: la ventana del acercamiento se sale de la caja del mapa")
    exige(z.get("n_celdas") == z.get("columnas", 0) * z.get("filas", 0),
          "agregación: las celdas del acercamiento no son columnas por filas")
    rx, ry = cj[2] - cj[0], cj[3] - cj[1]
    r = max(rx, ry)
    o = (cj[0] + rx / 2 - r / 2, cj[1] + ry / 2 - r / 2)
    for k in ma["lineas_resaltadas"]:
        seg = ma["lineas"][k - 1]
        xs = [v / ma["q"] * r + o[0] for v in seg[0::2]]
        ys = [v / ma["q"] * r + o[1] for v in seg[1::2]]
        tol = 2 * r / ma["q"]
        exige(cz[0] - tol <= min(xs) and max(xs) <= cz[2] + tol and cz[1] - tol <= min(ys) and max(ys) <= cz[3] + tol,
              f"agregación: la celda resaltada {k} queda fuera del acercamiento")

    # --- G-21: una proporción sobre mil lleva un decimal ----------------------
    ur = D["una_realizacion"]
    cuenta = ur["pct_rechaza_ingenuo"] * ur["n_realizaciones"] / 100
    exige(abs(cuenta - round(cuenta)) < 1e-9 and abs(ur["pct_rechaza_ingenuo"] * 10 - round(ur["pct_rechaza_ingenuo"] * 10)) < 1e-9,
          "módulo 6: el porcentaje de rechazos ya no cabe en un decimal y la lectura lo escribe con uno")

    # --- G-18: las pesas ------------------------------------------------------
    ec = D["escala_correlacion"]
    aleja = sum(abs(p["r_departamental"]) > abs(p["r_municipal"]) for p in ec["pares"])
    cruza = sum(p["r_departamental"] * p["r_municipal"] < 0 for p in ec["pares"])
    exige(aleja == ec["n_suben"] and len(ec["pares"]) - aleja == ec["n_bajan"] and cruza == ec["n_invierten"]
          and ec["n_invierten_entre_bajan"] == cruza
          and all(-1 <= p["r_municipal"] <= 1 and -1 <= p["r_departamental"] <= 1 for p in ec["pares"]),
          "módulo 7: «se alejan del 0», «se acercan» y «lo cruzan» ya no cuentan lo que R publica")
    exige(all(abs(q["r_departamental_n30"]) < abs(q["r_municipal_n30"])
              for q in ec["caso_aviso"]["bajan_sin_estrato"]),
          "módulo 7: los pares sin estrato ya no «se acercan al cero» con el umbral de estudiantes")

    # --- G-15: los dos repartos de la validación cruzada ----------------------
    cv, mi = D["cv_espacial"], M["ideam"]
    for clave in ("pliegue_aleatorio", "pliegue_bloques"):
        v = mi.get(clave, [])
        exige(len(v) == cv["n"] and set(v) == set(range(1, cv["n_pliegues"] + 1)),
              f"módulo 10: `{clave}` no reparte las estaciones en los pliegues")
    exige(sorted(mi.get("pliegue_bloques", []).count(k) for k in range(1, cv["n_pliegues"] + 1))
          == cv["tam_pliegues"], "módulo 10: los pliegues del mapa no tienen los tamaños publicados")
    exige(cv["vecina_en_su_pliegue_aleatoria"] * 4 < cv["n"] < cv["vecina_en_su_pliegue_bloques"] * 4 / 3,
          "módulo 10: «casi nunca» y «casi siempre» ya no describen dónde queda la vecina más próxima")
    exige(cv["rmse_bloques"] > cv["sd_variable"] > cv["rmse_aleatoria"] and cv["r2_bloques"] < 0 < cv["r2_aleatoria"],
          "módulo 10: la barra de los bloques ya no supera la desviación típica, o el R² ya no es negativo")

    # --- G-25: el deslizador de rho lleva el de Colombia ----------------------
    exige("rt.implicito]))].sort(" in SIMULADORES_JS and "ne.rhos.filter(v => v <= RHO_MAX)" in SIMULADORES_JS,
          "módulo 5: las posiciones del deslizador ya no salen de la rejilla de R y del rho de Colombia")
    rt = D["n_efectivo"]["rho_del_titular"]["implicito"]
    exige(0 < rt < 0.3 and all(abs(rt - v) > 5e-4 for v in D["n_efectivo"]["rhos"] + [0.001, 0.002, 0.005, 0.03, 0.075, 0.15]),
          "módulo 5: el rho de Colombia coincide con otra posición del deslizador, o queda fuera de su recorrido")

    # --- G-08: dos paneles ------------------------------------------------------
    exige('data-panel="ee"' in marcado and 'data-panel="cobertura"' in marcado and "yAxisID" not in SIMULADORES_JS,
          "módulo 4: los errores estándar y la cobertura vuelven a compartir lienzo con dos ejes")
    return malos


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
                        "Street resaltada, y a trazos las celdas de las bombas. La tabla de respaldo "
                        "da las muertes por bomba."),
              extra=("      nombre2: 'bombas de agua',\n"
                     "      get marcaResaltada() { return snowModo === 'broad' ? D1.snow.bomba_broad : null; },\n"
                     "      get lineas() { return snowModo !== 'sinlineas'; },\n"
                     # El título dice qué significa el color en cada vista: es el
                     # título de la leyenda, y va encima de ella (G-20).
                     "      get titulo() { return TITULO1_SNOW[snowModo]; },\n"
                     "      descripcion: () => DESC1_SNOW[snowModo]"),
              tabla=TABLA_SNOW)
    # Los pinos salen DOS veces —módulo 2 como caso nulo, módulo 3 en la
    # terna—, y con un solo registro: el motor pinta cada `.geomapa` en su
    # propio lienzo, así que reusar el identificador no duplica los 130
    # enteros de las coordenadas en el JS.
    + geomapa("cap1-pinos", "japanesepines", tabla=TABLA_PUNTOS,
              extra="      descripcion: " + json.dumps(DESC_PINOS, ensure_ascii=False))
    # Secuoyas y células llevaban desde T1.2 calculadas en `genera_cap1.R`,
    # exportadas a cap1_mapas.json y sin dibujarse en ninguna parte,
    # mientras el módulo 2 afirmaba que «el módulo 3 pone tres patrones
    # puntuales uno al lado del otro» y el módulo 3 ponía una tabla. Se
    # registran aquí porque la terna ES el argumento: sin ver los tres, la
    # frase «el ojo no los separa» hay que creérsela. (2026-08-10)
    + geomapa("cap1-secuoyas", "redwood", tabla=TABLA_PUNTOS,
              extra="      descripcion: " + json.dumps(DESC_SECUOYAS, ensure_ascii=False))
    + geomapa("cap1-celulas", "cells", tabla=TABLA_PUNTOS,
              extra="      descripcion: " + json.dumps(DESC_CELULAS, ensure_ascii=False))
    + geomapa("cap1-bogota", "bogota", tabla=TABLA_BOGOTA,
              extra="      descripcion: " + json.dumps(DESC_BOGOTA, ensure_ascii=False))
    + geomapa("cap1-nc", "nc", paleta="verde", tabla=TABLA_CLASES,
              extra="      descripcion: " + json.dumps(DESC_NC, ensure_ascii=False))
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
                     "      get etiqueta() { return agregAlt(); },\n"
                     "      descripcion: () => DESC1_AGREG[agregModo + '-' + agregVista]"),
              tabla=TABLA_AGREGACION)
    # EL ENCUADRE ACERCADO (R2 · T2.2, G-13). El literal de arriba es el mapa
    # entero, y es lo que el auditor de texto comprueba. La vista acercada no
    # trae geometría nueva: son los mismos vértices, pasados del marco de la
    # caja entera al de la ventana que calcula R (`zoom.caja`). Es un cambio
    # de marco —una resta y un cociente por coordenada—, no un cálculo: las
    # clases, los cortes, el resalte y la rejilla son los del literal. El
    # registro entrega una u otra según el botón.
    + """    (function () {
      const base = GEOMAPAS['cap1-agregacion'].fuente, z = base.zoom;
      const marco = c => {
        const rx = c[2] - c[0], ry = c[3] - c[1], r = Math.max(rx, ry);
        return { r: r, o: [c[0] + rx / 2 - r / 2, c[1] + ry / 2 - r / 2] };
      };
      const m0 = marco(base.caja), m1 = marco(z.caja);
      const pasa = v => v.map((t, i) => ((t / base.q * m0.r + m0.o[i % 2]) - m1.o[i % 2]) / m1.r * base.q);
      const cerca = Object.assign({}, base, {
        caja: z.caja,
        geom: base.geom.map(rasgo => rasgo.map(pasa)),
        lineas: base.lineas.map(pasa),
        // El lienzo deja ver, además de los rectángulos de la ventana, el
        // borde de los que la rodean: el título dice lo que se ve.
        titulo: 'La zona de ' + AGREG_CASO().nombre + ': ' + z.n_celdas + ' rectángulos enteros de los '
          + D1.agregacion_soporte.nc.n_celdas + ' de la rejilla, y el borde de sus vecinos'
      });
      Object.defineProperty(GEOMAPAS['cap1-agregacion'], 'fuente', {
        get() { return agregVista === 'zoom' ? cerca : base; }
      });
    })();
"""
    + geomapa("cap1-desercion", "desercion", paleta="naranja", tabla=TABLA_CLASES,
              extra="      descripcion: " + json.dumps(DESC_DESERCION, ensure_ascii=False))
    # El río, en el azul de la casa y más grueso que una calle: es lo que
    # hace legible el mapa, no un fondo (G-04).
    + geomapa("cap1-meuse", "meuse", paleta="naranja", tabla=TABLA_MEUSE,
              extra=("      colorLineas: 'rgba(14, 116, 144, 0.9)',\n"
                     "      anchoLineas: 1.6,\n"
                     "      descripcion: " + json.dumps(DESC_MEUSE, ensure_ascii=False)))
    # LA TEMPERATURA NO DIVERGE (G-05). Iba con la paleta divergente: el tono
    # neutro caía en la mitad del recorrido, un valor sin significado, y el
    # frío salía naranja. Va con una rampa secuencial propia de este capítulo,
    # de oscuro a claro y de frío a cálido —violeta, magenta, naranja,
    # amarillo—, que sigue leyéndose en gris porque la claridad crece de punta
    # a punta; la guarda de salida lo comprueba.
    + "    GEOMAPA_PALETAS.termica = " + json.dumps(PALETA_TERMICA) + ";\n"
    + geomapa("cap1-ideam", "ideam", paleta="termica", tabla=TABLA_IDEAM,
              extra=("      colorLineas: 'rgba(1, 40, 32, 0.45)',\n"
                     "      anchoLineas: 1,\n"
                     "      descripcion: " + json.dumps(DESC_IDEAM, ensure_ascii=False)))
    # Los dos repartos de la validación cruzada del módulo 10 (G-15): las
    # mismas estaciones y el mismo contorno que el mapa de arriba, con el
    # pliegue por marca. La fuente es una función porque se deriva de ese
    # literal; no lleva `niveles`, así que la leyenda no gasta diez casillas
    # en decir «pliegue 1… pliegue 10»: lo que importa es si los colores se
    # mezclan o se agrupan.
    + """    function pliegues1(clave, titulo) {
      const base = GEOMAPAS['cap1-ideam'].fuente;
      return Object.assign({}, base, {
        titulo: titulo, marcas: base['pliegue_' + clave], marcas_tipo: 'categoria',
        marcas_escala: undefined,
        leyenda: 'un color por pliegue · de fondo, el contorno del país'
      });
    }
"""
    + "".join(
        f"""    const PLIEGUES1_{ident.upper()} = pliegues1('{clave}', {json.dumps(TITULO_PLIEGUES[clave], ensure_ascii=False)});
    GEOMAPAS['cap1-pliegues-{ident}'] = {{
      fuente: () => PLIEGUES1_{ident.upper()},
      colorLineas: 'rgba(1, 40, 32, 0.45)',
      anchoLineas: 1,
      etiqueta: {json.dumps(TITULO_PLIEGUES[clave] + ": las " + ent(_CV["n"]) + " estaciones del IDEAM, con el contorno del país de fondo, cada una con el color de su pliegue.", ensure_ascii=False)},
      descripcion: {json.dumps(DESC_PLIEGUES[clave], ensure_ascii=False)},
{TABLA_PLIEGUES}
    }};
""" for ident, clave in (("azar", "aleatorio"), ("bloques", "bloques")))
    + COORDS_JS
    + "    // Lo que se ve en cada estado de los mapas que cambian con un control\n"
      "    // (ver «Describir el mapa» en el ensamblador).\n"
    + "    const DESC1_SNOW = " + json.dumps(_D1_SNOW, ensure_ascii=False) + ";\n"
    + "    const TITULO1_SNOW = " + json.dumps(_T1_SNOW, ensure_ascii=False) + ";\n"
    # EL NARANJA ES DE BROAD STREET EN LAS DOS VISTAS (R2 · T2.2, G-20). La
    # paleta cualitativa del motor reparte sus trece colores por orden, y a la
    # bomba de Broad Street le tocaba el rosa mientras el bermellón iba a otra:
    # el naranja significaba Broad Street en una vista y otra bomba en la
    # siguiente. Aquí, y solo en este capítulo, el color de la casilla de Broad
    # Street pasa a ser el acento del material y su rosa va a la casilla que
    # tenía el bermellón, que deja de usarse. La guarda de salida comprueba
    # que la paleta de la plantilla sigue siendo la que esto da por sabida.
    + "    (function () {\n"
      "      const iBroad = D1.snow.bomba_broad - 1, iBermellon = GEOMAPA_CUALITATIVA.indexOf('#D55E00');\n"
      "      if (iBermellon < 0 || iBermellon === iBroad) return;\n"
      "      GEOMAPA_CUALITATIVA[iBermellon] = GEOMAPA_CUALITATIVA[iBroad];\n"
      "      GEOMAPA_CUALITATIVA[iBroad] = GEOMAPA_ACENTO;\n"
      # Y el ámbar de la primera casilla —Oxford Market—, que en la leyenda
      # quedaba al lado del naranja y se confundía con él, pasa al amarillo
      # de la misma familia de Okabe e Ito.
      "      const iAmbar = GEOMAPA_CUALITATIVA.indexOf('#E69F00');\n"
      "      if (iAmbar >= 0 && iAmbar !== iBroad) GEOMAPA_CUALITATIVA[iAmbar] = '#F0E442';\n"
      "    })();\n"
    + "    const DESC1_CAMPO = " + json.dumps(DESC_CAMPO, ensure_ascii=False) + ";\n"
    + "    const DESC1_REAL = " + json.dumps(DESC_REAL, ensure_ascii=False) + ";\n"
    + "    const DESC1_AGREG = " + json.dumps(DESC_AGREG, ensure_ascii=False) + ";\n"
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
      get etiqueta() {
        return 'Campo gaussiano simulado sobre una retícula de ' + D1.inferencia.k + ' por '
          + D1.inferencia.k + ' celdas, la de la simulación; el alcance de la correlación se controla '
          + 'con el deslizador. El blanco es el cero, el naranja lo negativo y el verde lo positivo.';
      },
      descripcion: () => DESC1_CAMPO[String(D1.inferencia.rejilla[campoIdx].phi)],
TABLA_REJILLA_AQUI
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
      get etiqueta() {
        return 'Una de las ' + D1.realizaciones_vistas.length + ' primeras realizaciones del lote de '
          + miles1(D1.una_realizacion.n_realizaciones) + ', del mismo proceso gaussiano, sobre una retícula de '
          + D1.una_realizacion.k + ' por ' + D1.una_realizacion.k + ' celdas. El blanco es el cero, el '
          + 'naranja lo negativo y el verde lo positivo, con la misma escala en las tres.';
      },
      descripcion: () => DESC1_REAL[String(D1.realizaciones_vistas[realIdx].id)],
TABLA_REJILLA_AQUI
    };
    // La tabla de respaldo de un mapa se escribe una vez, al crearlo. La de
    // estos dos tiene que seguir al control: se rehace con el dato de ahora.
    function refrescaTabla1(raizMapa, ident) {
      const vieja = raizMapa && raizMapa.querySelector('details.geomapa-tabla:not(.geomapa-describe) table');
      if (!vieja) return;
      const caja = document.createElement('div');
      caja.innerHTML = GEOMAPAS[ident].tabla(GEOMAPAS[ident].fuente());
      vieja.innerHTML = caja.querySelector('table').innerHTML;
    }
""".replace("TABLA_REJILLA_AQUI", TABLA_REJILLA)
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
    // El encuadre del mapa del módulo 7: acercado a las celdas del caso, o el
    // estado entero. Arranca acercado, que es donde se leen las cifras.
    let agregVista = 'zoom';

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
    //
    // Solo en el encuadre acercado (R2 · T2.2, G-13). Con el estado entero
    // cada celda mide en el teléfono unos 23 × 8 px: los rótulos no caben, y
    // numerados se montaban unos sobre otros. Ese encuadre queda para ver
    // dónde está la rejilla; las cifras se leen en el otro.
    function agregEtiquetas() {
      const c = AGREG_CASO();
      if (agregVista !== 'zoom') return null;
      return agregModo === 'area'
        ? c.reparto.map(r => n5(r.aporte_area, 2))
        : c.reparto.map(() => String(c.sids));
    }

    function agregAlt() {
      const g = D1.agregacion_soporte.nc, c = g.condado_caso;
      const z = GEOMAPAS['cap1-agregacion'].fuente.zoom;
      const base = (agregVista === 'zoom'
        ? `La zona de ${c.nombre}, acercada: ${z.n_celdas} rectángulos enteros de los ${g.n_celdas} de la `
          + `rejilla, y el borde de sus vecinos, sobre los condados de Carolina del Norte, coloreados por `
          + `sus muertes súbitas. `
        : `Los ${D1.area_canonico.n} condados de Carolina del Norte coloreados por sus muertes `
          + `súbitas, con una rejilla de ${g.n_celdas} rectángulos superpuesta. `)
        + `${c.nombre}, en naranja, cae en ${c.n_celdas_toca} celdas, resaltadas con borde grueso`;
      if (agregVista !== 'zoom') {
        return agregModo === 'area'
          ? `${base}. Repartiendo por área, las ${c.n_celdas_toca} reciben entre todas las ${c.sids} `
            + `muertes del condado.`
          : `${base}. Emparejar por «se tocan» entrega las ${c.sids} muertes del condado a cada una: `
            + `${c.aporte_predicado} en total.`;
      }
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
        const eje = chart.scales.x;
        const x = eje.getPixelForValue(i);
        const a = chart.chartArea, ctx = chart.ctx;
        // LA BANDA SE MIDE EN UNIDADES DEL EJE, no en píxeles (R2 · T2.2, G-09).
        // Medía 20 px fijos: a 375 px cada día de la serie de Snow ocupa unos
        // 4, y la banda del mango cubría cinco días cuando el dato dice uno.
        // Ahora va de media categoría antes a media después —un día, en esa
        // serie—, o lo que diga `$marcadorAncho`, también en categorías.
        const medio = (chart.$marcadorAncho === undefined ? 1 : chart.$marcadorAncho) / 2;
        const x0 = Math.max(a.left, eje.getPixelForValue(i - medio));
        const x1 = Math.min(a.right, eje.getPixelForValue(i + medio));
        ctx.save();
        // Fuera de COLORES_GRAFICO a propósito: los cuatro colores están
        // gastados y un marcador del color de una serie se lee como serie.
        ctx.fillStyle = 'rgba(1, 40, 32, 0.10)';
        ctx.fillRect(x0, a.top, x1 - x0, a.bottom - a.top);
        ctx.strokeStyle = 'rgba(1, 40, 32, 0.75)';
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.moveTo(x, a.top);
        ctx.lineTo(x, a.bottom);
        ctx.stroke();
        ctx.restore();
      }
    });

    // Una recta horizontal de referencia que cruza TODO el trazado, con su
    // rótulo, y la cifra de cada barra encima de ella (R2 · T2.2). Las
    // «líneas» de `crearGraficoBarras` son una serie más: van del centro de
    // la primera barra al de la última y no llevan cifra. Inerte mientras
    // nadie ponga `$rectaY` o `$cifrasBarras`.
    Chart.register({
      id: 'rectaY',
      afterDatasetsDraw(chart) {
        const a = chart.chartArea, ctx = chart.ctx, eje = chart.scales.y;
        ctx.save();
        ctx.font = "600 11px 'Fira Code', monospace";
        ctx.textBaseline = 'bottom';
        // Las cajas de las cifras, para que el rótulo de la recta no las pise.
        const cajas = [];
        if (chart.$cifrasBarras) {
          ctx.textAlign = 'center';
          ctx.fillStyle = '#012820';
          chart.getDatasetMeta(0).data.forEach((barra, i) => {
            const t = chart.$cifrasBarras[i], w = ctx.measureText(t).width;
            const y = Math.min(barra.y, eje.getPixelForValue(0)) - 4;
            ctx.fillText(t, barra.x, y);
            cajas.push({ x0: barra.x - w / 2, x1: barra.x + w / 2, y0: y - 13, y1: y });
          });
        }
        const r = chart.$rectaY;
        chart.$rotuloPisado = false;
        if (r) {
          const y = eje.getPixelForValue(r.valor);
          // El rótulo va a la izquierda, sobre la recta. Si con su texto
          // largo alcanzara la cifra de una barra —en el teléfono—, va el
          // corto; y si aun así la pisara, se dice (`$rotuloPisado`), que es
          // lo que la medición del capítulo lee.
          const pisa = t => cajas.some(c => a.left + 6 + ctx.measureText(t).width + 4 > c.x0
            && a.left + 6 < c.x1 && y - 3 > c.y0 && y - 16 < c.y1);
          const rotulo = pisa(r.rotulo) ? r.corto : r.rotulo;
          chart.$rotuloPisado = pisa(rotulo);
          ctx.strokeStyle = COLORES_GRAFICO.secundario;
          ctx.lineWidth = 1.5;
          ctx.setLineDash([5, 4]);
          ctx.beginPath();
          ctx.moveTo(a.left, y);
          ctx.lineTo(a.right, y);
          ctx.stroke();
          ctx.textAlign = 'left';
          ctx.fillStyle = '#8a3d00';
          ctx.fillText(rotulo, a.left + 6, y - 3);
        }
        ctx.restore();
      }
    });

    function lectura(raiz, filas) {
      const caja = raiz.querySelector('.simulador-lectura');
      if (!caja) return;
      caja.innerHTML = filas.map(f =>
        `<span class="lectura-item"><span class="lectura-etiqueta">${f[0]}</span> ` +
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
    //
    // `grupo` (R2 · T2.2) es para el simulador que lleva DOS botoneras: con
    // él la botonera no vacía el contenedor, sino que se añade como un grupo
    // con nombre —`role="group"` y `aria-label`— en su propio renglón, y solo
    // atiende a sus botones. Sin él, todo como estaba.
    function botonera(raiz, opciones, alPulsar, valorInicial, grupo) {
      const cont0 = raiz.querySelector('.simulador-controles');
      // Si el valor no está entre las opciones se marca la primera, como
      // hacía siempre: mejor un mando coherente consigo mismo que ninguno.
      const ini = Math.max(0, opciones.findIndex(o => String(o[0]) === String(valorInicial)));
      let cont = cont0;
      if (grupo) {
        cont = document.createElement('div');
        cont.setAttribute('role', 'group');
        cont.setAttribute('aria-label', grupo);
        cont.style.cssText = 'display:flex;flex-wrap:wrap;gap:0.5rem;flex-basis:100%;';
        cont0.appendChild(cont);
      }
      cont.innerHTML = opciones.map((o, i) =>
        `<button type="button" class="geomapa-boton${i === ini ? ' activo' : ''}" ` +
        `aria-pressed="${i === ini}" data-v="${o[0]}">${o[1]}</button>`).join('');
      cont.addEventListener('click', e => {
        const b = e.target.closest('.geomapa-boton');
        if (!b || b.parentElement !== cont) return;
        cont.querySelectorAll('.geomapa-boton').forEach(x => {
          x.classList.remove('activo');
          x.setAttribute('aria-pressed', 'false');
        });
        b.classList.add('activo');
        b.setAttribute('aria-pressed', 'true');
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
      const d = GEOMAPAS['cap1-snow'].fuente;
      const mapa = () => raiz.querySelector('[data-geomapa="cap1-snow"]');
      // LAS CELDAS DE LAS TRECE BOMBAS (R2 · T2.2, G-20). La lectura habla de
      // «la celda de Broad St» y el mapa no la dibujaba. Son los polígonos de
      // Voronoi que calcula R (`celdas`), cuantizados contra la misma caja que
      // los puntos. El motor no tiene una segunda capa de líneas, así que se
      // trazan ENCIMA de lo que él pinta, con el mismo ajuste que devuelve su
      // `dibuja()`: a trazos finos las trece y, en el modo de Broad Street, la
      // suya con borde naranja. Sin las calles no van: ese modo existe para
      // ver la mancha sola.
      const pintaCeldas = aj => {
        const m = mapa();
        if (!aj || !m || !d.celdas || snowModo === 'sinlineas') return;
        const ctx = m.__geomapa.canvas.getContext('2d');
        const dpr = window.devicePixelRatio || 1;
        const traza = c => {
          ctx.beginPath();
          for (let i = 0; i < c.length; i += 2) {
            if (i) ctx.lineTo(aj.x(c[i]), aj.y(c[i + 1]));
            else ctx.moveTo(aj.x(c[i]), aj.y(c[i + 1]));
          }
          ctx.closePath();
        };
        ctx.save();
        ctx.lineJoin = 'round';
        ctx.setLineDash([5 * dpr, 4 * dpr]);
        ctx.strokeStyle = 'rgba(1, 40, 32, 0.6)';
        ctx.lineWidth = dpr;
        d.celdas.forEach(c => { traza(c); ctx.stroke(); });
        if (snowModo === 'broad') {
          ctx.setLineDash([]);
          ctx.strokeStyle = GEOMAPA_ACENTO;
          ctx.lineWidth = 2.2 * dpr;
          traza(d.celdas[s.bomba_broad - 1]);
          ctx.stroke();
        }
        ctx.restore();
        // Y la leyenda las explica. El motor la reescribe en cada trazo, así
        // que se añaden después de él, como las celdas.
        const ley = m.querySelector('.geomapa-leyenda');
        if (ley && !ley.querySelector('.celdas-snow')) {
          const entrada = (borde, texto) => `<span class="geomapa-clase celdas-snow">`
            + `<span class="geomapa-muestra" style="background:transparent;border:${borde}"></span>`
            + `<span>${texto}</span></span>`;
          ley.insertAdjacentHTML('beforeend',
            entrada('1px dashed rgba(1, 40, 32, 0.7)', 'celda de cada bomba: lo que le queda más cerca')
            + (snowModo === 'broad' ? entrada('2px solid ' + GEOMAPA_ACENTO, 'celda de Broad St') : ''));
        }
      };
      const pinta = () => { const m = mapa(); if (m && m.__geomapa) pintaCeldas(m.__geomapa.dibuja()); };
      // El motor repinta el mapa por su cuenta cuando cambia de tamaño, y ese
      // trazo se lleva las celdas. Se vuelven a poner en el cuadro siguiente:
      // dentro del mismo aviso de tamaño no se puede, porque el del motor
      // puede llegar después. El primer trazo va por la misma vía: al
      // construirse el simulador el mapa todavía no existe.
      let cuadro = 0;
      const repinta = () => { cancelAnimationFrame(cuadro); cuadro = requestAnimationFrame(pinta); };
      const vigia = new ResizeObserver(repinta);
      vigia.observe(mapa());
      const lee = () => {
        if (snowModo === 'todas') {
          lectura(raiz, [['bombas', s.n_bombas],
            ['un color por bomba', 'trece categorías: más de las que una paleta cualitativa separa'],
            ['en naranja', 'Broad Street: sus muertes y su rombo, como en la otra vista'],
            ['a trazos', 'la celda de cada bomba: lo que le queda más cerca que cualquier otra']]);
        } else if (snowModo === 'sinlineas') {
          lectura(raiz, [['muertes', s.n_muertes],
            ['sin el fondo', 'la mancha sigue ahí: no la dibujaban las calles']]);
        } else {
          lectura(raiz, [['muertes de la celda de Broad St, la del borde naranja', `${s.n_mas_cerca_broad} de ${s.n_muertes}`],
            ['porcentaje', n5(s.pct_mas_cerca_broad) + ' %'],
            ['reparto ingenuo, por igual entre bombas', n5(s.pct_esperado_uniforme) + ' %'],
            ['razón sobre ese reparto', n5(s.razon_sobre_uniforme) + '×']]);
        }
      };
      botonera(raiz, [['broad', 'Broad Street contra el resto'],
                      ['todas', 'Un color por bomba (' + s.n_bombas + ')'],
                      ['sinlineas', 'Sin las calles']],
        v => { snowModo = v; pinta(); lee(); }, snowModo);
      lee();
      // Lo que se destruye al salir del módulo: el vigía y el cuadro pendiente.
      return [{ destroy() { vigia.disconnect(); cancelAnimationFrame(cuadro); } }];
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
      // `lectura()` pegaba el rótulo y el valor sin separador —ninguna regla
      // pintaba `.lectura-etiqueta`—, y por eso los valores de aquí empiezan
      // por una cifra o por una comilla angular. Desde el 2026-09-23
      // `lectura()` escribe un espacio entre los dos y la plantilla les da
      // color, así que la redacción ya no tiene que esquivar nada.
      const lee = () => {
        if (agregModo === 'area') {
          lectura(raiz, [['la regla', '«repartir por área» — st_interpolate_aw'],
            ['a cada celda', '«su parte», proporcional al área que le cae'],
            [`${c.nombre} aporta`, `${c.sids} en total, que son las que tiene`],
            ['la celda que solo roza', `${n5(c.roce_pct)} % del condado → ${n5(c.roce_aporte_area)} muertes`],
            ['total sobre la rejilla', `${miles1(g.total_por_area)}, el exacto`]]);
        } else {
          lectura(raiz, [['la regla', '«se tocan» — st_intersects'],
            ['a cada celda', `${c.sids}: el conteo entero del condado`],
            [`${c.nombre} aporta`, `${c.sids} × ${c.n_celdas_toca} = ${c.aporte_predicado}`],
            ['de más, solo él', `${c.exceso} muertes, el ${n5(c.pct_del_exceso)} % del exceso`],
            ['total sobre la rejilla', `${miles1(g.total_rectangulos)} donde había ${g.total_condados}`]]);
        }
      };
      botonera(raiz, [['predicado', 'Emparejar por «se tocan»'],
                      ['area', 'Repartir por área']],
        v => { agregModo = v; pinta(); lee(); }, agregModo, 'Regla de agregación');
      botonera(raiz, [['zoom', 'Acercar a ' + c.nombre],
                      ['estado', 'El estado entero']],
        v => { agregVista = v; pinta(); }, agregVista, 'Encuadre del mapa');
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
        // Cinco fechas a lo sumo: con más, en el teléfono se pisaban.
        { scales: { x: { title: { display: true, text: 'día (mes/día de 1854)' }, ticks: { maxTicksLimit: 5 } },
                    y: { title: { display: true, text: 'casos por día' } } } });
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

    // Las tres gráficas de R2 · T2.4 llevan el eje horizontal LINEAL, no de
    // categorías. Desde que `crearGraficoLinea` funde las opciones en
    // profundidad (R2 · T2.1) ya no declaran la letra, la rejilla ni la
    // rotación: las heredan de la casa, como cualquier otro gráfico, y la
    // leyenda baja sola al pie en el teléfono. Aquí queda lo único propio:
    // que el eje es lineal y que sus marcas no se saltan.
    const EJE_X_LINEAL = (titulo, extra) => fusionarOpcionesGrafico(
      { type: 'linear', title: { display: true, text: titulo }, ticks: { autoSkip: false } },
      extra || {});
    // ¿Teléfono? Se pregunta en cada trazo y no una vez al cargar: quien gira
    // el teléfono cambia de respuesta con la página abierta.
    const estrecho = () => window.matchMedia('(max-width: 480px)').matches;

    // 1.3 · La prueba de aleatorización --------------------------------
    // El histograma de la nula y el dato, en el mismo eje. Todo sale de
    // `snow.aleatorizacion`: R recolocó, contó y publicó cuántas veces salió
    // cada recuento. Aquí solo se pasa de muertes a porcentaje —dividir
    // entre las muertes— para que el eje sea el del titular del módulo.
    SIMULADORES['snow-nula'] = function (raiz) {
      const s = D1.snow, a = s.aleatorizacion;
      const canvas = raiz.querySelector('canvas');
      const pct = k => 100 * k / s.n_muertes;
      const u = a.hist_n.length - 1;
      // Un escalón centrado en cada recuento posible, con un cero a cada lado
      // para que el histograma cierre contra el eje.
      const barras = [{ x: pct(a.hist_n[0] - 1), y: 0 }]
        .concat(a.hist_n.map((k, i) => ({ x: pct(k), y: a.hist_frec[i] })))
        .concat([{ x: pct(a.hist_n[u] + 1), y: 0 }]);
      const techo = Math.max.apply(null, a.hist_frec);
      const obs = s.pct_mas_cerca_broad;
      const INGENUO = 'Reparto ingenuo, 1/' + s.n_bombas;
      const vertical = x => [{ x: x, y: 0 }, { x: x, y: techo }];
      // Los dos encuadres. El completo llega hasta la decena que contiene al
      // observado; el otro se cierra sobre la nula.
      const VISTAS = {
        completa: { min: 0, max: 10 * Math.ceil(obs / 10), paso: 10 },
        nula: { min: Math.floor(a.min_nula_pct), max: Math.ceil(a.max_nula_pct), paso: 1 }
      };
      let vista = 'completa';
      const g = crearGraficoLinea(canvas, [], [
        { label: 'Recolocaciones al azar sobre las calles', data: barras, stepped: 'middle',
          fill: true, backgroundColor: 'rgba(148, 163, 184, 0.40)',
          borderColor: COLORES_GRAFICO.gris, borderWidth: 1, pointRadius: 0 },
        { label: 'Binomial: la nula, con fórmula',
          data: a.hist_n.map((k, i) => ({ x: pct(k), y: a.hist_binomial[i] })),
          borderColor: COLORES_GRAFICO.primario, backgroundColor: COLORES_GRAFICO.primario,
          borderWidth: 1.5, pointRadius: 0 },
        { label: INGENUO, data: vertical(s.pct_esperado_uniforme),
          borderColor: COLORES_GRAFICO.terciario, backgroundColor: COLORES_GRAFICO.terciario,
          borderDash: [4, 3], borderWidth: 1.5, pointRadius: 0 },
        { label: 'Observado', data: vertical(obs), borderColor: COLORES_GRAFICO.secundario,
          backgroundColor: COLORES_GRAFICO.secundario, borderWidth: 3, pointRadius: 0 }
      ], {
        interaction: { mode: 'nearest', axis: 'x', intersect: false },
        plugins: {
          legend: { onClick: () => {} },
          tooltip: {
            filter: it => it.datasetIndex === 0 && it.dataIndex > 0 && it.dataIndex <= u + 1,
            callbacks: {
              title: its => its.length
                ? a.hist_n[its[0].dataIndex - 1] + ' de ' + s.n_muertes + ' muertes, el '
                  + n5(pct(a.hist_n[its[0].dataIndex - 1]), 2) + ' %' : '',
              label: it => it.parsed.y + ' de ' + miles1(a.n_recolocaciones) + ' recolocaciones'
            }
          }
        },
        scales: {
          x: EJE_X_LINEAL('% de las muertes más cerca de Broad Street', {
            min: VISTAS.completa.min, max: VISTAS.completa.max,
            ticks: { stepSize: VISTAS.completa.paso } }),
          y: { title: { display: true, text: 'recolocaciones' }, beginAtZero: true }
        }
      });
      // Lo dibujado contra lo que R publica por otro lado: el histograma
      // tiene que sumar las recolocaciones, dar la media publicada y quedar
      // entero a la izquierda del observado.
      const cuadra = () => {
        const mal = [];
        const total = a.hist_frec.reduce((x, y) => x + y, 0);
        if (total !== a.n_recolocaciones) {
          mal.push('el histograma suma ' + total + ' y R publica ' + a.n_recolocaciones
            + ' recolocaciones');
        }
        const media = a.hist_n.reduce((x, k, i) => x + pct(k) * a.hist_frec[i], 0) / total;
        if (!(Math.abs(media - a.media_nula_pct) <= 1e-6)) {
          mal.push('la media del histograma es ' + media + ' y R publica ' + a.media_nula_pct);
        }
        if (g.data.datasets[3].data[0].x !== s.pct_mas_cerca_broad) {
          mal.push('la línea del observado no está en ' + s.pct_mas_cerca_broad);
        }
        if (!(a.hist_n[u] < s.n_mas_cerca_broad) || a.n_mayor_o_igual !== 0) {
          mal.push('alguna recolocación alcanza al observado y la lectura dice que ninguna');
        }
        if (!mal.length) return true;
        console.error('snow-nula: ' + mal.length + ' descuadre(s) entre lo dibujado y el JSON — '
          + mal.join(' · '));
        return false;
      };
      const pinta = () => {
        const v = VISTAS[vista];
        g.options.scales.x.min = v.min;
        g.options.scales.x.max = v.max;
        g.options.scales.x.ticks.stepSize = v.paso;
        g.update('none');
      };
      const lee = () => {
        const filas = [
          ['observado', n5(obs) + ' %'],
          ['media de la nula: la parte de calle de Broad St', n5(a.pct_calle_broad) + ' %'],
          ['observado / media de la nula', n5(a.razon_sobre_calle) + ' veces'],
          ['la recolocación más alta', n5(a.max_nula_pct) + ' %'],
          ['recolocaciones que igualan o superan al observado',
            a.n_mayor_o_igual + ' de ' + miles1(a.n_recolocaciones)],
          ['valor p', '≤ ' + n5(a.p_cota)],
          ['con solo las calles del rectángulo de las muertes', n5(a.marcos[0].pct_calle_broad)
            + ' % · observado ' + n5(a.marcos[0].razon_sobre_calle) + ' veces']];
        if (vista === 'nula') {
          filas.push(['reparto ingenuo', n5(s.pct_esperado_uniforme) + ' %'],
            ['el observado, fuera del encuadre', 'a ' + n5(a.z_observado)
              + ' desviaciones típicas de la media']);
        }
        lectura(raiz, filas);
      };
      botonera(raiz, [['completa', 'La nula y el dato'], ['nula', 'Acercar a la nula']],
        v => { vista = v; pinta(); lee(); }, vista);
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
      // R2 · T2.4 (G-16): el eje horizontal es la distancia, lineal. Antes
      // era un eje de categorías y las siete bandas, de 25 a 300 km de ancho,
      // salían equiespaciadas: el decaimiento quedaba deformado.
      const env = t.envolvente;
      const u7 = t.ideam.bandas.length - 1;
      // Cada serie, un punto en el centro de su banda.
      const puntos = d => d.bandas.map(b => ({ x: b.centro, y: b.I }));
      // La franja y la referencia valen a lo ancho de la banda: dos puntos por
      // banda, en sus dos bordes, que unidos dibujan el escalón.
      const escalon = (filas, campo) => filas.reduce((v, f) =>
        v.concat([{ x: f.d1, y: f[campo] }, { x: f.d2, y: f[campo] }]), []);
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
        { clave: 'permutado', etiqueta: 'Una permutación al azar', d: t.permutado,
          color: '#64748b', dash: [5, 4] }
      ];
      const ESPERADO = 'E[I] bajo permutación';
      const FRANJA = 'Envolvente de permutación, ' + env.nivel_pct + ' %';
      const BORDE = 'borde superior de la envolvente';
      // El cuarto interruptor no enciende una serie: cierra el eje vertical
      // sobre la franja. A la escala del dato entero, la franja de las bandas
      // largas mide un par de píxeles, y es ahí donde la prosa dice que una
      // banda cae dentro y otra por debajo.
      const ZOOM = 'Acercar a la franja';
      const params = { real: true, altitud: true, permutado: true, zoom: false };
      const LIM_ZOOM = Math.ceil(20 * 1.5 * Math.max.apply(null,
        env.ideam.concat(env.residuos_altitud).map(f => Math.max(Math.abs(f.lo), Math.abs(f.hi)))))
        / 20;
      // Qué envolvente va detrás. La de la temperatura vale también para la
      // permutación suelta, que reparte sus mismos valores; la de los
      // residuos solo cuando son la única serie del dato encendida. R para si
      // la lectura de alguna banda dependiera de cuál de las dos se dibuja.
      // La permutación suelta reparte TEMPERATURAS: con ella encendida la
      // franja es la de la temperatura, para no leerla contra una ajena.
      const cualEnv = () => (!params.real && params.altitud && !params.permutado)
        ? 'residuos_altitud' : 'ideam';
      // Las marcas del eje, en los bordes de banda que caben: los de las tres
      // primeras están a 25 km uno de otro y se pisarían.
      const bordes = [t.ideam.bandas[0].d1].concat(t.ideam.bandas.map(b => b.d2));
      // Se guarda un borde si queda a 75 km o más del anterior guardado; en el
      // teléfono, a 100 o más. Se decide en cada composición del eje.
      const marcas = () => bordes.reduce((v, x) => (!v.length
        || x - v[v.length - 1] >= (estrecho() ? 100 : 75)) ? v.concat([x]) : v, []);
      const g = crearGraficoLinea(canvas, [],
        // La franja va primero para quedar debajo de las series: el borde
        // superior sin trazo, y el inferior relleno hasta él.
        [{ label: BORDE, data: escalon(env.ideam, 'hi'), borderWidth: 0, pointRadius: 0,
           borderColor: 'rgba(148, 163, 184, 0)' },
         { label: FRANJA, data: escalon(env.ideam, 'lo'), borderWidth: 0, pointRadius: 0,
           borderColor: 'rgba(148, 163, 184, 0)', backgroundColor: 'rgba(148, 163, 184, 0.38)',
           fill: '-1' }]
        .concat(SERIES.map(x => ({ label: x.etiqueta, data: puntos(x.d),
          borderColor: x.color, backgroundColor: x.color, borderDash: x.dash, borderWidth: 2,
          pointRadius: 3 })))
          // Banda a banda: con unidades sin vecinos, spdep multiplica por n'
          // y no por n, y la esperanza por permutación es -n'/(n(n - 1)).
          .concat([{ label: ESPERADO, data: escalon(t.ideam.bandas, 'esperado'),
            borderColor: COLORES_GRAFICO.primario, backgroundColor: COLORES_GRAFICO.primario,
            borderDash: [2, 3], borderWidth: 1.5, pointRadius: 0 }]),
        { interaction: { mode: 'nearest', axis: 'x', intersect: false },
          plugins: {
            // El borde superior no es una serie: es media franja. Fuera de la leyenda.
            legend: { labels: { filter: it => it.text !== BORDE } },
            tooltip: {
              filter: it => SERIES.some(x => x.etiqueta === it.dataset.label),
              callbacks: {
                title: its => its.length ? 'banda de ' + t.ideam.bandas[its[0].dataIndex].d1 + ' a '
                  + t.ideam.bandas[its[0].dataIndex].d2 + ' km' : '',
                label: it => it.dataset.label + ': ' + n5(it.parsed.y)
              }
            }
          },
          scales: {
            x: EJE_X_LINEAL('distancia entre estaciones (km)', {
              min: bordes[0], max: bordes[bordes.length - 1],
              afterBuildTicks: eje => { eje.ticks = marcas().map(v => ({ value: v })); } }),
            y: { title: { display: true, text: 'I de Moran' } }
          } });
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
                     'Una permutación al azar': t.permutado };
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
          const dib = g.data.datasets[i].data.map(p => p.y);
          if (dib.length !== json.length || dib.some((v, k) => v !== json[k])) {
            mal.push('«' + etiqueta + '» dibuja ' + dib[0] + ' en la primera banda y su serie del '
              + 'JSON trae ' + json[0]);
          }
          // Y cada punto en el centro de SU banda: con el eje lineal, un
          // punto corrido de banda se dibuja sin protestar.
          if (g.data.datasets[i].data.some((p, k) => !(t.ideam.bandas[k].d1 < p.x
              && p.x < t.ideam.bandas[k].d2))) {
            mal.push('«' + etiqueta + '» tiene algún punto fuera de su banda');
          }
        });
        // La franja dibujada es la que toca, entera, y la serie que la lleva
        // detrás cae donde R dice: por encima, dentro o por debajo.
        const cual = cualEnv(), fr = env[cual];
        const iLo = idx(FRANJA), iHi = idx(BORDE);
        const mismo = (i, campo) => i >= 0 && g.data.datasets[i].data.length === 2 * fr.length
          && fr.every((f, k) => g.data.datasets[i].data[2 * k].y === f[campo]
            && g.data.datasets[i].data[2 * k + 1].y === f[campo]
            && g.data.datasets[i].data[2 * k].x === f.d1
            && g.data.datasets[i].data[2 * k + 1].x === f.d2);
        if (!mismo(iLo, 'lo') || !mismo(iHi, 'hi') || !g.isDatasetVisible(iLo)
            || !g.isDatasetVisible(iHi)) {
          mal.push('la franja dibujada no es la envolvente de «' + cual + '» que publica R');
        }
        t[cual].bandas.forEach((b, k) => {
          const donde = b.I > fr[k].hi ? 'encima' : b.I < fr[k].lo ? 'debajo' : 'dentro';
          if (donde !== fr[k].posicion) {
            mal.push('la banda ' + b.d1 + '–' + b.d2 + ' de «' + cual + '» se dibuja ' + donde
              + ' de la franja y R dice ' + fr[k].posicion);
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
        const fr = env[cualEnv()];
        g.data.datasets[idx(BORDE)].data = escalon(fr, 'hi');
        g.data.datasets[idx(FRANJA)].data = escalon(fr, 'lo');
        g.options.scales.y.min = params.zoom ? -LIM_ZOOM : undefined;
        g.options.scales.y.max = params.zoom ? LIM_ZOOM : undefined;
        g.update('none');
      };
      // «por encima», «dentro», «por debajo»: la palabra sale de la posición
      // que publica R, no de una comparación hecha aquí.
      const QUEDA = { encima: 'por encima', dentro: 'dentro', debajo: 'por debajo' };
      const franja = f => n5(f.lo) + ' a ' + n5(f.hi);
      const lee = () => {
        const u = u7;
        const cual = cualEnv(), fr = env[cual];
        const iNeg = env.ideam.findIndex(f => f.posicion === 'debajo');
        const filas = [[ESPERADO + ', con las ' + t.ideam.bandas[u].n_con_vecinos + ' estaciones',
          n5(t.ideam.esperado, 6)],
          ['y en la primera banda, con las ' + t.ideam.bandas[0].n_con_vecinos + ' que tienen vecinos',
            n5(t.ideam.bandas[0].esperado, 6)],
          ['franja dibujada: la de ' + (cual === 'ideam' ? 'la temperatura' : 'los residuos')
            + ', primera banda', franja(fr[0])],
          ['y última banda', franja(fr[u])]];
        if (params.real) {
          filas.push(['primera banda, dato real', n5(t.ideam.bandas[0].I) + ' · '
              + QUEDA[env.ideam[0].posicion]],
            ['última banda, dato real', n5(t.ideam.bandas[u].I) + ' · '
              + QUEDA[env.ideam[u].posicion]]);
          if (iNeg >= 0) {
            filas.push(['banda de ' + t.ideam.bandas[iNeg].d1 + '–' + t.ideam.bandas[iNeg].d2
              + ' km, dato real', n5(t.ideam.bandas[iNeg].I) + ' · ' + QUEDA.debajo
              + ' (franja: ' + franja(env.ideam[iNeg]) + ')']);
          }
          filas.push(['bandas del dato real fuera de su franja',
            env.n_fuera_ideam + ' de ' + (u + 1)],
            ['parejas a más de ' + t.mas_alla.d1 + ' km, fuera del eje', n5(t.mas_alla.I) + ' · '
              + QUEDA[t.mas_alla.posicion] + ' (franja: ' + n5(t.mas_alla.lo) + ' a '
              + n5(t.mas_alla.hi) + ')']);
        }
        if (params.altitud) filas.push(['primera banda, sin la altitud',
          n5(t.residuos_altitud.bandas[0].I) + ' · ' + QUEDA[env.residuos_altitud[0].posicion]],
          ['bandas de los residuos fuera de su franja', env.n_fuera_residuos + ' de ' + (u + 1)]);
        // Solo con las dos encendidas: es una comparación entre ellas, y
        // enseñarla con una apagada sería publicar la conclusión de un
        // contraste que el estudiante no tiene delante.
        if (params.real && params.altitud) filas.push(['cuánto de la I era altitud',
          n5(t.caida_por_altitud_pct) + ' %']);
        if (params.permutado) filas.push(['primera banda, la permutación suelta',
          n5(t.permutado.bandas[0].I)],
          ['bandas de la permutación suelta fuera de la franja',
            env.n_fuera_permutado + ' de ' + (u + 1)]);
        lectura(raiz, filas);
      };
      crearInterruptores(raiz.querySelector('.simulador-controles'),
        SERIES.map(x => ({ clave: x.clave, etiqueta: x.etiqueta }))
          .concat([{ clave: 'zoom', etiqueta: ZOOM }]), params,
        () => { pinta(); cuadra(); lee(); });
      pinta();
      cuadra();
      lee();
      return [g];
    };

    // 4 · El error estándar ingenuo -----------------------------------
    SIMULADORES['ee-ingenuo'] = function (raiz) {
      const r = D1.inferencia.rejilla;
      const ejes = r.map(f => f.phi);
      // DOS PANELES Y NO DOS EJES (R2 · T2.2, G-08). Los errores estándar y la
      // cobertura iban en el mismo lienzo, cada uno con su eje vertical, y
      // dos escalas sin relación fabricaban un cruce —«e.e. real» con
      // «cobertura», en phi = 2— que no significa nada. Ahora cada magnitud
      // tiene su panel y su escala, y comparten el eje horizontal: el alcance.
      const lienzo = k => raiz.querySelector('canvas[data-panel="' + k + '"]');
      const ejeX = { title: { display: true, text: 'alcance φ' } };
      // El mismo ancho para el eje vertical de los dos: así los siete
      // alcances caen en la misma vertical arriba y abajo.
      const ANCHO_EJE = 58;
      const ejeY = extra => fusionarOpcionesGrafico({ afterFit: eje => { eje.width = ANCHO_EJE; } }, extra);
      const gEE = crearGraficoLinea(lienzo('ee'), ejes, [
        { label: 'e.e. que se calcularía (ingenuo)', data: r.map(f => f.ee_ingenuo),
          borderColor: COLORES_GRAFICO.gris, tension: 0.2, pointRadius: 3 },
        { label: 'e.e. real', data: r.map(f => f.ee_real),
          borderColor: COLORES_GRAFICO.secundario, tension: 0.2, pointRadius: 3 }
      ], { scales: { x: ejeX,
                     y: ejeY({ beginAtZero: true, title: { display: true, text: 'error estándar' } }) } });
      const PROMETIDO = n5(1 - D1.inferencia.alfa, 2) + ' prometido';
      const gCob = crearGraficoLinea(lienzo('cobertura'), ejes, [
        { label: 'cobertura del IC al ' + D1.inferencia.nivel_pct + ' %', data: r.map(f => f.cobertura),
          borderColor: COLORES_GRAFICO.terciario, tension: 0.2, pointRadius: 3 },
        { label: PROMETIDO, data: r.map(() => 1 - D1.inferencia.alfa),
          borderColor: COLORES_GRAFICO.primario, borderDash: [2, 3], pointRadius: 0 }
      ], { scales: { x: ejeX,
                     y: ejeY({ min: 0, max: 1, title: { display: true, text: 'cobertura' } }) } });
      const PANELES = [gEE, gCob];
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
        lectura(raiz, [['alcance φ', f.phi],
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
      // alcance ya es el eje horizontal, y va en los dos paneles. La recta de
      // la cobertura prometida no lleva punto que marcar. La banda mide un
      // tercio de categoría: aquí señala una posición, no un intervalo.
      const pinta = () => {
        PANELES.forEach(g => {
          g.$marcadorX = campoIdx;
          g.$marcadorAncho = 1 / 3;
          g.data.datasets.filter(ds => ds.label !== PROMETIDO).forEach(ds => {
            ds.pointRadius = ejes.map((_, i) => i === campoIdx ? 7 : 3);
          });
          g.update('none');
        });
      };
      // Las posiciones del control se DERIVAN de la intersección de las dos
      // rejillas, no se escriben: si R exporta o quita un campo, el control
      // se ajusta solo y nunca ofrece una posición sin campo detrás.
      const conCampo = r.map((f, i) => [i, 'φ = ' + f.phi])
                        .filter(p => campoDePhi(r[p[0]].phi));
      // El control manda sobre el estado, y no al revés: si el arranque
      // cayera en un alcance sin campo, `findIndex` daría −1, el <input> lo
      // redondearía a 0 y volveríamos a tener dos índices discrepando.
      const ini = Math.max(0, conCampo.findIndex(p => p[0] === campoIdx));
      campoIdx = conCampo[ini][0];
      deslizador(raiz, conCampo, 'alcance de la correlación', ini, v => {
          campoIdx = v;
          const m = raiz.querySelector('[data-geomapa="cap1-campo"]');
          if (cuadra() && m && m.__geomapa) { m.__geomapa.dibuja(); refrescaTabla1(m, 'cap1-campo'); }
          lee();
          pinta();
        });
      cuadra();
      lee();
      pinta();
      return PANELES;
    };

    // 4.2 · Cien intervalos --------------------------------------------
    // La cobertura del módulo, vista. Las cien medias y los semianchos son
    // los de las cien primeras réplicas de phi = 4, tal como salen de R; aquí
    // solo se decide el color de cada segmento —¿contiene al cero?— y se
    // CUENTA, y el recuento se contrasta con el que R publica.
    SIMULADORES['cien-ic'] = function (raiz) {
      const inf = D1.inferencia, c = inf.cien_ic;
      const f4 = inf.rejilla.find(f => f.phi === c.phi);
      const canvas = raiz.querySelector('canvas');
      let modo = 'ingenuo';
      const semi = i => modo === 'ingenuo' ? c.semiancho_ingenuo[i] : c.semiancho_exacto;
      const cubre = i => Math.abs(c.media[i]) <= semi(i);
      // Un segmento vertical por réplica: sus dos extremos y un hueco, para
      // que la línea no una un intervalo con el siguiente.
      const segmentos = quiere => c.media.reduce((v, m, i) => cubre(i) !== quiere ? v
        : v.concat([{ x: i + 1, y: m - semi(i) }, { x: i + 1, y: m + semi(i) },
                    { x: i + 1, y: null }]), []);
      // El eje vertical NO cambia al conmutar: se fija con el intervalo más
      // ancho, para que la diferencia de largo se vea sobre la misma escala.
      // Redondeado al medio punto de arriba, para que las marcas del eje
      // caigan en medios puntos y una de ellas sea el cero.
      const tope = Math.ceil(2 * (Math.max.apply(null, c.media.map(Math.abs))
        + c.semiancho_exacto)) / 2;
      const CUBRE = 'Cubre la media verdadera', NO_CUBRE = 'No la cubre';
      const g = crearGraficoLinea(canvas, [], [
        { label: CUBRE, data: [], borderColor: COLORES_GRAFICO.primario,
          backgroundColor: COLORES_GRAFICO.primario, borderWidth: () => estrecho() ? 1 : 1.5,
          pointRadius: 0, spanGaps: false },
        { label: NO_CUBRE, data: [], borderColor: COLORES_GRAFICO.secundario,
          backgroundColor: COLORES_GRAFICO.secundario, borderWidth: () => estrecho() ? 1 : 1.5,
          pointRadius: 0, spanGaps: false },
        // La media, como una rayita horizontal y no como un punto: el
        // segmento ingenuo mide unos diez píxeles y un punto lo tapaba.
        { label: 'Media de la réplica', data: c.media.map((m, i) => ({ x: i + 1, y: m })),
          showLine: false, pointStyle: 'line', pointRadius: () => estrecho() ? 1.5 : 3,
          pointBorderWidth: 1.5, pointBorderColor: '#64748b', borderColor: '#64748b',
          backgroundColor: '#64748b' },
        { label: 'Media verdadera, 0', data: [{ x: 0, y: 0 }, { x: c.n + 1, y: 0 }],
          borderColor: COLORES_GRAFICO.terciario, backgroundColor: COLORES_GRAFICO.terciario,
          borderDash: [5, 3], borderWidth: 1.5, pointRadius: 0 }
      ], {
        events: [],
        plugins: { legend: { onClick: () => {} }, tooltip: { enabled: false } },
        scales: {
          x: EJE_X_LINEAL('réplica', { min: 0, max: c.n + 1,
            ticks: { stepSize: 20, includeBounds: false } }),
          y: { title: { display: true, text: 'media y su intervalo' }, min: -tope, max: tope,
               ticks: { stepSize: 0.5, includeBounds: false } }
        }
      });
      const cuenta = () => c.media.filter((_, i) => cubre(i)).length;
      const cuadra = () => {
        const debe = modo === 'ingenuo' ? c.n_cubren_ingenuo : c.n_cubren_exacto;
        const mal = [];
        if (cuenta() !== debe) {
          mal.push('se dibujan ' + cuenta() + ' intervalos que cubren y R publica ' + debe);
        }
        if (c.media.length !== c.n || c.semiancho_ingenuo.length !== c.n) {
          mal.push('no hay ' + c.n + ' medias con sus ' + c.n + ' semianchos');
        }
        if (!f4) mal.push('la rejilla no trae la fila de phi = ' + c.phi);
        if (!mal.length) return true;
        console.error('cien-ic: ' + mal.join(' · '));
        return false;
      };
      const pinta = () => {
        g.data.datasets[0].data = segmentos(true);
        g.data.datasets[1].data = segmentos(false);
        g.update('none');
        canvas.setAttribute('aria-label', c.n + ' intervalos de confianza al ' + inf.nivel_pct
          + ' por ciento de la media, uno por réplica del campo con alcance ' + c.phi + ', en vertical alrededor de la '
          + 'media verdadera, cero. Con el error estándar '
          + (modo === 'ingenuo' ? 'ingenuo' : 'verdadero') + ' cubren el cero ' + cuenta()
          + ' de los ' + c.n + '; los que no lo cubren van en naranja.');
      };
      const lee = () => {
        if (!f4) return;
        lectura(raiz, modo === 'ingenuo' ? [
          ['cubren la media verdadera', cuenta() + ' de estos ' + c.n],
          ['semiancho medio de los ' + c.n, n5(c.semiancho_ingenuo_medio)],
          ['cobertura sobre las ' + miles1(inf.nrep) + ' réplicas',
            n5(f4.cobertura) + ' ± ' + n5(f4.emc_cobertura)],
          ['cobertura prometida', n5(1 - inf.alfa, 2)]
        ] : [
          ['cubren la media verdadera', cuenta() + ' de estos ' + c.n],
          ['semiancho, el mismo para todos', n5(c.semiancho_exacto)],
          ['veces el ingenuo', n5(c.razon_semianchos)],
          ['cobertura sobre las ' + miles1(inf.nrep) + ' réplicas',
            n5(c.cobertura_exacto) + ' ± ' + n5(c.emc_cobertura_exacto)],
          ['cobertura prometida', n5(1 - inf.alfa, 2)]]);
      };
      botonera(raiz, [['ingenuo', 'Error estándar ingenuo, s/√n'],
                      ['exacto', 'Error estándar verdadero']],
        v => { modo = v; pinta(); cuadra(); lee(); }, modo);
      pinta();
      cuadra();
      lee();
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
      //
      // En el teléfono van uno de cada dos, contando desde el último: con los
      // seis, «500» y «1 000» se pisaban a 375 px (R2 · T2.2).
      const fijos = (lista, ralea) => ({
        afterBuildTicks: a => {
          const u = lista.length - 1;
          a.ticks = lista.filter((_, i) => !(ralea && a.chart.width < 420 && (u - i) % 2))
            .map(value => ({ value }));
        },
        ticks: { callback: mil, autoSkip: false }
      });
      const DIEZ = [];
      for (let p = 1; p <= XMAX; p *= 10) DIEZ.push(p);
      const params = { rho: ne.rhos[1] };
      // La curva de referencia de Colombia: la del rho medio que corresponde
      // al n_eff del titular. Pasa por el rombo porque ese rho se despeja de
      // ahí, y se queda fija; la que se mueve es la del deslizador. No hay
      // curva de una correlación media «leída del mapa»: ese promedio vale
      // -1/(n-1) para cualquier dato (`n_efectivo.centrado`) y no la estima.
      const rt = ne.rho_del_titular;
      // Tres decimales, salvo el de Colombia, que lleva los cinco de la casa:
      // con tres se confundiría con la posición de al lado.
      const fmtRho = v => v === rt.implicito ? n5(v) : v.toFixed(3);
      const curva = rho => EJE.map(n => ({ x: n, y: nEff(n, rho) }));
      // Por referencia y no por índice: `cuadra()` leía `datasets[0]` y
      // `datasets[3]` a mano, y meter series nuevas entre ellas era
      // exactamente el descuadre silencioso de T1.2. Ahora cada serie tiene
      // nombre en el código.
      const dsMovil = { label: 'n efectivo con este rho medio', data: [], borderWidth: 2.5,
          borderColor: COLORES_GRAFICO.secundario, pointRadius: 0 };
      const dsTecho = { label: 'techo 1/rho medio', data: [], borderColor: '#111',
          borderDash: [3, 3], pointRadius: 0 };
      const dsImpl = { label: 'el rho medio que corresponde a Colombia (' + n5(rt.implicito) + ')',
          data: curva(rt.implicito), borderColor: COLORES_GRAFICO.terciario,
          borderWidth: 1.5, pointRadius: 0 };
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
        dsImpl, dsRombo
      ], { scales: {
        x: Object.assign({ type: 'logarithmic', min: XMIN, max: XMAX,
          title: { display: true, text: 'observaciones, n' } }, fijos(ne.enes, true)),
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
        // Que la curva del rho medio de Colombia PASE por el rombo, leída de
        // lo dibujado y no recalculada aparte: la prosa dice que pasa, y es la
        // única forma de que no se quede en promesa. Tolerancia 1e-6: el rho
        // del JSON viene redondeado a diez decimales y el punto está sobre 64.
        const yImpl = dsImpl.data.find(p => p.x === ne.desercion_n);
        if (!yImpl || Math.abs(yImpl.y - ne.desercion_municipal) > 1e-6) {
          mal.push('la curva del rho medio de Colombia pasa por '
            + (yImpl ? yImpl.y : 'ningún punto en n = ' + ne.desercion_n)
            + ' y el rombo está en ' + ne.desercion_municipal);
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
          ['rho medio entre pares', fmtRho(r)],
          ['techo 1/rho medio', r > 0 ? n5(1 / r) : 'sin correlación no hay techo'],
          ['n = ' + mil(n0) + ' informan como', n5(nEff(n0, r))],
          ['n = ' + mil(n1) + ' informan como', n5(nEff(n1, r))],
          ['lo que aporta pasar de uno a otro', n5(nEff(n1, r) - nEff(n0, r))],
          ['Colombia: ' + mil(ne.desercion_n) + ' municipios valen', n5(ne.desercion_municipal)],
          ['con este rho medio valdrían', n5(nEff(ne.desercion_n, r))],
          ['el rho medio que corresponde a ese ' + n5(ne.desercion_municipal), n5(rt.implicito)]]);
      };
      // EL DESLIZADOR RECORRE UNA LISTA DE POSICIONES, no un tramo continuo
      // (R2 · T2.2, G-25). De 0 a 0.3 con paso 0.001, las correlaciones medias
      // que importan —las de pocas centésimas— caían en el primer 5 % del
      // recorrido, unos 12 px en el teléfono, y no había forma de dejar el
      // dedo sobre ellas. La lista aprieta las posiciones donde el techo
      // cambia deprisa: lleva los rho de la rejilla de R hasta el tope —las
      // anclas que `cuadra()` compara una a una—, el rho medio que corresponde
      // a Colombia, exacto, y unas pocas posiciones intermedias. Y con
      // `deslizador()` el lector de pantalla anuncia la correlación, no la
      // posición (G-24).
      const POSICIONES = [...new Set(ne.rhos.filter(v => v <= RHO_MAX)
        .concat([0.001, 0.002, 0.005, 0.03, 0.075, 0.15, rt.implicito]))].sort((a, b) => a - b);
      deslizador(raiz,
        POSICIONES.map(v => [v, fmtRho(v) + (v === rt.implicito ? ' · el de Colombia' : '')]),
        'correlación media rho', POSICIONES.indexOf(params.rho),
        v => { params.rho = v; pinta(); cuadra(); lee(); });
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
        { label: 'teórico, promediado en la clase', data: v.teorico_clase, borderColor: COLORES_GRAFICO.primario,
          borderDash: [4, 3], pointRadius: 0 },
        { label: 'media de ' + miles1(u.n_realizaciones) + ' realizaciones', data: v.media,
          borderColor: COLORES_GRAFICO.terciario, pointRadius: 2 },
        dsUna,
        { label: 'banda 5 %–95 %', data: v.q05, borderColor: 'rgba(148,163,184,.5)',
          pointRadius: 0, fill: '+1' },
        // El borde de arriba de la banda no es otra serie: va sin nombre y
        // fuera de la leyenda, que antes le dejaba una casilla vacía (G-17).
        { label: '', data: v.q95, borderColor: 'rgba(148,163,184,.5)', pointRadius: 0 }
      ], { plugins: { legend: { labels: { filter: it => it.text !== '' } },
                      tooltip: { filter: it => it.dataset.label !== '' } },
           // Una semivarianza se lee desde cero, y el rezago va en pasos de retícula.
           scales: { x: { title: { display: true, text: 'rezago (pasos de retícula)' } },
                     y: { beginAtZero: true, title: { display: true, text: 'semivarianza' } } } });
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
          ['su variograma se aparta del teórico de la clase', n5(r.desvio_rel_max) + ' (rezago ' + r.lag_desvio_max + ')'],
          ['rezagos fuera de la banda', r.lags_fuera_banda + ' de ' + v.lags.length],
          ['sd de las medias sobre ' + miles1(u.n_realizaciones), n5(u.sd_de_las_medias)],
          // Una proporción sobre mil realizaciones tiene un decimal, no cinco;
          // y el nivel de la prueba se escribe como se eligió (G-21).
          ['engañarían al análisis ingenuo', n5(u.pct_rechaza_ingenuo, 1) + ' % de las '
            + miles1(u.n_realizaciones)],
          ['deberían ser', u.pct_esperado_si_valiera + ' %']]);
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
          if (cuadra() && m && m.__geomapa) { m.__geomapa.dibuja(); refrescaTabla1(m, 'cap1-realizacion'); }
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
      const caja = raiz.querySelector('.grafico-wrapper');
      // EL ALTO DE LA CAJA SIGUE AL ANCHO DE LA VENTANA, no al momento en que
      // se pulsó el botón. Trece renglones con rótulo de dos líneas no caben
      // en 250 px; y en el teléfono la leyenda baja al pie y los rótulos van
      // de dos a cuatro líneas, así que hace falta más. Antes se decidía solo
      // al pulsar: quien abría los pares con el teléfono tumbado y lo giraba
      // se quedaba con la caja baja y los trece rótulos montados. Ahora lo
      // decide esta función, que se llama al dibujar y cada vez que la
      // ventana cambia de tamaño. No hay bucle: el alto depende solo de la
      // vista y del ancho de la ventana, nunca del alto que resulta.
      const ajustaAlto = () => {
        const alto = vista === 'sim' ? '250px'
          : (window.matchMedia('(max-width: 640px)').matches ? '840px' : '470px');
        if (caja.style.height !== alto) caja.style.height = alto;
      };
      window.addEventListener('resize', ajustaAlto);
      const dibuja = () => {
        if (g) { g.destroy(); const i = graficosActivos.indexOf(g); if (i >= 0) graficosActivos.splice(i, 1); }
        ajustaAlto();
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
          // UN RENGLÓN POR PAR, DE −1 A 1 (R2 · T2.2, G-18). Antes era el
          // cambio relativo de la correlación, en tanto por ciento, que es
          // inestable cerca de 0 y convertía un cambio de signo —de 0.28 a
          // −0.20— en «−170 %». Ahora cada par es una pesa: el círculo hueco
          // es su correlación entre municipios, el lleno la de entre
          // departamentos, y el trazo que los une es lo que mueve agregar. El
          // 0 lleva línea propia, así que cruzarlo se ve. El par con aviso va
          // en naranja: la prosa lo nombra y hay que poder encontrarlo.
          const av = e.caso_aviso;
          const conAviso = p => p.a === av.a && p.b === av.b;
          const color = p => conAviso(p) ? COLORES_GRAFICO.secundario : COLORES_GRAFICO.primario;
          const MUN = 'entre municipios', DEP = 'entre departamentos';
          g = crearGraficoLinea(canvas, [], [
            { label: MUN, data: e.pares.map((p, i) => ({ x: p.r_municipal, y: i })), showLine: false,
              pointRadius: 5, pointBorderWidth: 2, pointBackgroundColor: '#ffffff',
              pointBorderColor: e.pares.map(color), borderColor: COLORES_GRAFICO.primario,
              backgroundColor: '#ffffff' },
            { label: DEP, data: e.pares.map((p, i) => ({ x: p.r_departamental, y: i })), showLine: false,
              pointRadius: 5, pointBorderWidth: 2, pointBackgroundColor: e.pares.map(color),
              pointBorderColor: e.pares.map(color), borderColor: COLORES_GRAFICO.primario,
              backgroundColor: COLORES_GRAFICO.primario },
            // El trazo de cada pesa: dos puntos y un hueco, para que no una
            // un par con el siguiente. Va el último para quedar debajo.
            { label: '', data: e.pares.reduce((v, p, i) => v.concat([{ x: p.r_municipal, y: i },
                { x: p.r_departamental, y: i }, { x: null, y: null }]), []),
              segment: { borderColor: c => color(e.pares[Math.floor(c.p0DataIndex / 3)]) },
              borderWidth: 2, pointRadius: 0, spanGaps: false, order: 1 },
            { label: 'en naranja, el par con aviso', data: [], borderColor: COLORES_GRAFICO.secundario,
              backgroundColor: COLORES_GRAFICO.secundario, pointRadius: 0 }
          ], {
            interaction: { mode: 'nearest', axis: 'y', intersect: false },
            plugins: {
              legend: { onClick: () => {}, labels: { filter: it => it.text !== '' } },
              tooltip: {
                filter: (it, k) => k === 0 && it.dataset.label !== '',
                callbacks: {
                  title: its => its.length ? e.pares[its[0].dataIndex].a_corta + ' × '
                    + e.pares[its[0].dataIndex].b_corta : '',
                  label: it => 'municipios ' + n5(e.pares[it.dataIndex].r_municipal)
                    + ' → departamentos ' + n5(e.pares[it.dataIndex].r_departamental)
                }
              }
            },
            scales: {
              x: { type: 'linear', min: -1, max: 1,
                   title: { display: true, text: 'correlación entre las dos variables' },
                   ticks: { stepSize: 0.5 },
                   grid: { display: true, lineWidth: c => c.tick && c.tick.value === 0 ? 1.5 : 1,
                           color: c => c.tick && c.tick.value === 0
                             ? 'rgba(1, 40, 32, 0.7)' : 'rgba(148, 163, 184, 0.2)' } },
              // Un renglón por par, el primero arriba; el rótulo, en dos
              // líneas para que quepa en el teléfono.
              y: { type: 'linear', reverse: true, min: -0.6, max: e.pares.length - 0.4,
                   afterBuildTicks: eje => { eje.ticks = e.pares.map((_, i) => ({ value: i })); },
                   ticks: { autoSkip: false, font: { family: 'Fira Code', size: 10 },
                            // En el teléfono el eje no pasa de la mitad del lienzo:
                            // el renglón de más de quince letras se parte por su
                            // último espacio.
                            callback: function (v) {
                              const par = e.pares[v];
                              if (!par) return '';
                              const lineas = [par.a_corta, '× ' + par.b_corta];
                              if (this.chart.width >= 400) return lineas;
                              return lineas.reduce((out, t) => {
                                const k = t.lastIndexOf(' ');
                                return out.concat(t.length > 15 && k > 1 ? [t.slice(0, k), t.slice(k + 1)] : [t]);
                              }, []);
                            } },
                   grid: { display: false } }
            }
          });
          // Lo dibujado contra lo que R cuenta: cuántas pesas se alejan del 0,
          // cuántas se acercan y cuántas lo cruzan.
          const seAleja = e.pares.filter(p => Math.abs(p.r_departamental) > Math.abs(p.r_municipal)).length;
          const cruza = e.pares.filter(p => p.r_departamental * p.r_municipal < 0).length;
          if (seAleja !== e.n_suben || e.pares.length - seAleja !== e.n_bajan || cruza !== e.n_invierten
              || g.data.datasets[0].data.length !== e.n_pares) {
            console.error('agregacion: las pesas dibujadas no cuentan lo que publica R — se alejan del 0 '
              + seAleja + ' (R: ' + e.n_suben + '), cruzan el 0 ' + cruza + ' (R: ' + e.n_invierten + ')');
          }
          lectura(raiz, [['pares examinados', e.n_pares],
            ['se alejan del 0 al agregar', e.n_suben],
            ['se acercan al 0', e.n_bajan], ['de los que se acercan, lo cruzan', e.n_invierten_entre_bajan],
            ['en naranja, el par con aviso', av.a_corta + ' × ' + av.b_corta + ': '
              + n5(av.r_municipal) + ' → ' + n5(av.r_departamental)],
            ['ese par, sin ' + av.influyente.municipio, n5(av.influyente.r_departamental_sin_el)],
            ['par principal, municipal', n5(e.principal.r_municipal)],
            ['par principal, departamental', n5(e.principal.r_departamental)]]);
        }
      };
      botonera(raiz, [['sim', 'Simulación controlada'], ['real', 'Los ' + e.n_pares + ' pares reales']],
        v => { vista = v; dibuja(); });
      dibuja();
      // Lo que se destruye al salir del módulo: el gráfico que haya entonces
      // —no el primero, que es el que se devolvía— y la escucha del tamaño.
      return [{ destroy() { window.removeEventListener('resize', ajustaAlto); if (g) g.destroy(); } }];
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
      // El suelo del eje del R²: el quinto de punto por debajo del menor.
      const R2_MIN = Math.floor(5 * Math.min(0, c.r2_aleatoria, c.r2_bloques)) / 5;
      const dibuja = () => {
        if (g) { g.destroy(); const i = graficosActivos.indexOf(g); if (i >= 0) graficosActivos.splice(i, 1); }
        const datos = vista === 'rmse' ? [c.rmse_aleatoria, c.rmse_bloques]
                                       : [c.r2_aleatoria, c.r2_bloques];
        // En el RMSE, la desviación típica de la variable como recta de
        // referencia (R2 · T2.2, G-15): es el error de predecir siempre la
        // media, y la barra de los bloques la supera. Eso es lo que quiere
        // decir un R² negativo, y antes solo estaba en la lectura.
        //
        // La recta cruza el trazado entero y cada barra lleva su cifra
        // encima: la de los bloques pasa de la recta por siete centésimas de
        // grado, un par de píxeles, y sin las cifras «la supera» no se veía.
        // El eje sigue saliendo de 0, y no se acerca a esa diferencia: las
        // dos barras se comparan por su largo, y la razón entre ellas es la
        // cifra del módulo. Cortar el eje la falsearía.
        g = crearGraficoBarras(canvas, ['CV aleatoria', 'CV por bloques'], datos,
          vista === 'rmse' ? { etiqueta: 'RMSE (°C)', tituloValor: 'RMSE (°C)', min: 0,
                               max: Math.ceil(Math.max(c.rmse_bloques, c.sd_variable) + 1) }
                           : { etiqueta: 'R²', tituloValor: 'R²', min: R2_MIN, max: 1 });
        g.$cifrasBarras = datos.map(v => n5(v));
        if (vista === 'rmse') g.$rectaY = { valor: c.sd_variable, rotulo: 'sd de la variable: ' + n5(c.sd_variable),
                                            corto: 'sd: ' + n5(c.sd_variable) };
        g.options.plugins.legend.display = false;
        g.update('none');
        if (vista === 'r2') {
          // EL CERO, MARCADO (G-14). El eje iba de −1 a 1 con paso 0.4: ni una
          // marca ni una línea en 0, y el R² negativo de los bloques —la
          // lección— era un trazo de un píxel sin referencia. Ahora el eje
          // baja solo hasta donde hace falta, va de quinto en quinto y el 0
          // lleva la línea oscura.
          const ey = g.options.scales.y, cero = t => t.tick && Math.abs(t.tick.value) < 1e-9;
          ey.min = R2_MIN;
          ey.max = 1;
          ey.ticks.stepSize = 0.2;
          ey.ticks.callback = v => Math.abs(v) < 1e-9 ? '0' : Number(v).toFixed(1);
          ey.grid.color = t => cero(t) ? 'rgba(1, 40, 32, 0.75)' : 'rgba(148, 163, 184, 0.2)';
          ey.grid.lineWidth = t => cero(t) ? 1.5 : 1;
          g.update('none');
        }
        graficosActivos.push(g);
        const vecinas = [
          ['estaciones con su vecina más próxima en su mismo pliegue, al azar',
            c.vecina_en_su_pliegue_aleatoria + ' de ' + c.n],
          ['y por bloques', c.vecina_en_su_pliegue_bloques + ' de ' + c.n]];
        lectura(raiz, (vista === 'rmse'
          ? [['RMSE aleatoria', n5(c.rmse_aleatoria)], ['RMSE por bloques', n5(c.rmse_bloques)],
             ['en una zona no medida el error es mayor en', n5(c.inflacion_pct) + ' %'],
             ['sd de la variable', n5(c.sd_variable)]]
          : [['R² aleatoria', n5(c.r2_aleatoria)], ['R² por bloques', n5(c.r2_bloques)],
             ['lectura', 'negativo: predecir la media global lo haría mejor']]).concat(vecinas));
      };
      botonera(raiz, [['rmse', 'RMSE'], ['r2', 'R²']], v => { vista = v; dibuja(); });
      dibuja();
      return [];
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
        pregunta: '¿Verdadero o falso? Con datos espaciales positivamente correlacionados —lo cercano se '
          + 'parece—, el error estándar clásico $s/\\sqrt{n}$ sale demasiado PEQUEÑO, y por eso los intervalos de '
          + 'confianza salen más estrechos de lo que deberían.',
        pista: 'Piensa en si dos observaciones vecinas aportan información nueva o información repetida.',
        opciones: [
          { texto: 'Verdadero', correcta: true,
            retro: 'Y el capítulo lo mide: con dato colombiano real, el error estándar que conserva la '
              + 'dependencia dentro de cada departamento es ' + n5(D1.inferencia_real.factor) + ' veces el ingenuo. '
              + 'El signo importa: con correlación negativa pasaría lo contrario.' },
          { texto: 'Falso', correcta: false,
            retro: 'Observaciones que se parecen aportan menos información de la que su número sugiere, así que '
              + 'la fórmula clásica infla la confianza. Sería falso con correlación negativa, y por eso la '
              + 'pregunta dice «positivamente». Módulo 4.' }
        ],
        retroAcierto: 'Y no es un matiz: la cobertura de un intervalo nominal al 95 % baja a '
          + n5(D1.inferencia.cobertura_phi4) + ' en el ejemplo del módulo 4.',
        retroFallo: 'Módulo 4.'
      },
      {
        tipo: 'opcion', modulo: 5,
        // Ninguna cifra a mano: todas son de `n_efectivo.caso_quiz`, que R
        // publica y el auditor rehace desde la rejilla.
        pregunta: 'Tienes ' + miles1(D1.n_efectivo.caso_quiz.n) + ' observaciones cuya correlación media '
          + 'entre parejas es ' + n5(D1.n_efectivo.caso_quiz.rho, 2) + '. '
          + '¿A cuántas observaciones independientes equivalen para estimar la media?',
        pista: 'La fórmula es n / (1 + (n-1) rho), con rho la correlación media entre parejas. Haz la cuenta '
          + 'con la cabeza antes de mirar.',
        opciones: [
          { texto: 'Alrededor de ' + D1.n_efectivo.caso_quiz.n_eff_redondo, correcta: true,
            retro: 'Exactamente ' + n5(D1.n_efectivo.caso_quiz.n_eff)
              + '. Y no es que "pierdas" ' + D1.n_efectivo.caso_quiz.sobran + ': es que nunca las tuviste.' },
          { texto: 'Alrededor de ' + D1.n_efectivo.caso_quiz.ingenuo, correcta: false,
            retro: 'Esa sería la intuición de "pierdo un ' + D1.n_efectivo.caso_quiz.pct_ingenuo
              + ' %", y falla por dos órdenes de magnitud. Módulo 5.' },
          { texto: 'Alrededor de ' + D1.n_efectivo.caso_quiz.techo_otro, correcta: false,
            retro: 'Cerca del techo con una correlación media de ' + n5(D1.n_efectivo.caso_quiz.rho_otro, 2)
              + ', no de ' + n5(D1.n_efectivo.caso_quiz.rho, 2) + '. Con '
              + n5(D1.n_efectivo.caso_quiz.rho, 2) + ' el techo es ' + D1.n_efectivo.caso_quiz.techo
              + '. Módulo 5.' },
          { texto: 'Las ' + miles1(D1.n_efectivo.caso_quiz.n)
              + ': la correlación no afecta al tamaño de muestra.', correcta: false,
            retro: 'Afecta, y mucho. Ése es justo el módulo 5.' }
        ],
        retroAcierto: 'Y lo importante es el techo: mientras la correlación media no cambie, n_eff tiende a '
          + '1/rho. Al añadir datos dentro de la misma región la correlación media tiende a una constante y el '
          + 'tamaño efectivo se estanca; al ampliar la región, si la correlación decae con la distancia, la '
          + 'correlación media baja y no hay techo.',
        retroFallo: 'Módulo 5. La respuesta corta: con la correlación media fija hay un techo, y está en 1/rho.'
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
          { texto: 'Agregar no siempre refuerza la correlación: a veces la debilita o le cambia el signo.', correcta: true,
            retro: 'De los ' + D1.escala_correlacion.n_pares + ' pares reales del capítulo, en '
              + D1.escala_correlacion.n_suben + ' la correlación se aleja del cero al agregar y en '
              + D1.escala_correlacion.n_bajan + ' se acerca a él: se cuenta su valor absoluto. '
              + 'Cambiar de signo también puede pasar —el capítulo 3 lo cuenta con Robinson—, pero el único '
              + 'par del módulo que lo hace, ' + D1.escala_correlacion.caso_aviso.a_corta + ' × '
              + D1.escala_correlacion.caso_aviso.b_corta + ', no aguanta el barrido.' },
          { texto: 'La cifra departamental es la buena, porque tiene menos ruido.', correcta: false,
            retro: 'Ninguna de las dos es "la buena": responden a preguntas distintas. Módulo 7 y ejercicio 4.' },
          { texto: 'Si difieren, es que una de las dos está mal calculada.', correcta: false,
            retro: 'Las dos pueden estar perfectamente calculadas. Eso es exactamente el MAUP.' }
        ],
        retroAcierto: 'Las dos. La unidad de análisis es una decisión de modelado, no de presentación.',
        retroFallo: 'Las dos ciertas son que las dos cifras pueden diferir con el mismo dato y que agregar no siempre refuerza la correlación. Módulo 7.'
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
          { texto: 'El desempeño estimado saldrá mejor del que el modelo tendrá en una zona donde no se ha medido.',
            correcta: true,
            retro: 'El capítulo lo mide: el RMSE al predecir en una zona no medida es un '
              + n5(D1.cv_espacial.inflacion_pct) + ' % mayor que el que anuncia la CV aleatoria. Módulo 10.' },
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
        retroAcierto: 'Y frente al ' + n5(D1.snow.pct_esperado_uniforme) + ' % de un reparto ingenuo, por igual '
          + 'entre las ' + D1.snow.n_bombas + ' bombas, son ' + n5(D1.snow.razon_sobre_uniforme) + ' veces. Ingenuo '
          + 'porque ignora el área que sirve cada bomba y la población que la usa.',
        retroFallo: 'Son ' + D1.snow.n_mas_cerca_broad + ' de ' + D1.snow.n_muertes + ', o sea el '
          + n5(D1.snow.pct_mas_cerca_broad) + ' %.'
      },
      {
        tipo: 'opcion', modulo: 1,
        pregunta: 'El ' + n5(D1.snow.pct_ataques_antes_mango) + ' % de los ataques ocurrió ANTES de que se '
          + 'retirara el mango de la bomba. ¿Qué se sigue de ahí?',
        pista: 'Ojo con confundir "el brote se apagó después" con "se apagó por eso".',
        opciones: [
          { texto: 'Que el dato no permite atribuirle a la retirada del mango el final del brote.', correcta: true,
            retro: 'Ese día los ataques diarios ya habían caído un '
              + n5(D1.snow.fecha_mango === null ? 0 : D1.snow.caida_hasta_mango_pct)
              + ' % desde el pico. Tampoco prueba que la retirada no sirviera: solo que el descenso no la necesitó '
              + 'para empezar.' },
          { texto: 'Que la retirada del mango fue lo que apagó el brote.', correcta: false,
            retro: 'Es la lectura cómoda, y el dato no la sostiene: la curva ya venía cayendo antes. Módulo 1.' },
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
        retroFallo: 'Las dos ciertas son que buena parte de la dependencia la explica la altitud y que permutar las temperaturas entre las mismas estaciones desploma la I. Módulo 3.'
      },
      {
        tipo: 'grafico', modulo: 4,
        alto: 210,
        descripcionGrafico: 'Dos curvas frente al alcance de la correlación: el error estándar que se calcularía, '
          + 'el ingenuo, casi plano, y el error estándar real, que crece sin parar.',
        pregunta: 'Lectura de gráfico. Las dos curvas son el error estándar de la MISMA media sobre el mismo '
          + 'campo simulado. ¿Qué está pasando?',
        pista: 'Fíjate en cuál de las dos casi no se mueve, y pregúntate por qué no se entera de nada.',
        dibujar: canvas => {
          const r = D1.inferencia.rejilla;
          return crearGraficoLinea(canvas, r.map(f => String(f.phi)), [
            // Los mismos nombres de serie que el simulador del módulo 4 (G-12).
            { label: 'e.e. que se calcularía (ingenuo)', data: r.map(f => f.ee_ingenuo),
              borderColor: COLORES_GRAFICO.gris, tension: 0.2, pointRadius: 3 },
            { label: 'e.e. real', data: r.map(f => f.ee_real),
              borderColor: COLORES_GRAFICO.secundario, tension: 0.2, pointRadius: 3 }
          ], { scales: { x: { title: { display: true, text: 'alcance φ' } },
                         y: { beginAtZero: true, title: { display: true, text: 'error estándar' } } } });
        },
        opciones: [
          { texto: 'El e.e. ingenuo no ve la correlación, así que subestima cada vez más al crecer phi.',
            correcta: true,
            retro: 'Con phi = ' + D1.inferencia.rejilla[4].phi + ' el real es '
              + n5(D1.inferencia.rejilla[4].factor) + ' veces el ingenuo. La fórmula clásica solo mira la '
              + 'dispersión de los datos, no cómo se relacionan entre sí.' },
          { texto: 'La estimación de la media se sesga cada vez más al crecer phi.', correcta: false,
            retro: 'No hay sesgo, con ningún phi: la esperanza de una suma es la suma de las esperanzas, así '
              + 'que la media de las celdas tiene por esperanza la media del proceso, haya la correlación que '
              + 'haya. El ' + n5(D1.una_realizacion.media_de_las_medias) + ' que promedian las medias de '
              + D1.una_realizacion.n_realizaciones + ' realizaciones con phi = ' + D1.una_realizacion.phi
              + ' es ruido de la simulación, no sesgo: cada una de esas medias tiene desviación típica '
              + n5(D1.una_realizacion.sd_de_las_medias) + '. Lo que crece con phi es esa dispersión —el e.e. '
              + 'real pasa de ' + n5(D1.inferencia.rejilla[0].ee_real) + ' a '
              + n5(D1.inferencia.rejilla[D1.inferencia.rejilla.length - 1].ee_real) + ' en el gráfico—, y el '
              + 'e.e. ingenuo no se entera.' },
          { texto: 'El e.e. real crece porque la varianza del proceso crece con phi.', correcta: false,
            retro: 'La varianza marginal es la misma para todo phi; lo que cambia es la covarianza entre celdas.' },
          { texto: 'Con phi grande hay menos datos, y por eso sube el error.', correcta: false,
            retro: 'Hay siempre ' + D1.inferencia.n + ' celdas. Lo que baja es la información que aportan: el n '
              + 'efectivo pasa de ' + D1.inferencia.n + ' a ' + n5(D1.inferencia.n_eff_phi4) + '.' }
        ],
        retroAcierto: 'Y no es un sesgo de la estimación, que sigue centrada en la media verdadera aunque cada '
          + 'vez con menos precisión: es un sesgo de la confianza.',
        retroFallo: 'Módulo 4.'
      },
      {
        tipo: 'numerica', modulo: 7,
        pregunta: 'El I de Moran de la deserción pasa de ' + n5(D1.escala.moran_municipal) + ' entre los '
          + D1.escala.n_municipal + ' municipios a ' + n5(D1.escala.moran_departamental) + ' entre los '
          + D1.escala.n_departamental + ' departamentos. ¿Qué porcentaje cae? Dos decimales.',
        respuesta: Number(n5(D1.escala.caida_pct, 2)), tolerancia: 0.05,
        pista: 'Es una caída porcentual normal y corriente sobre el valor municipal.',
        retroAcierto: 'Y no ha cambiado ni el dato ni la variable: solo la unidad de análisis. El porcentaje '
          + 'describe las dos cifras, no mide cuánta autocorrelación se pierde: las dos I usan pesos y n distintos. '
          + 'Tampoco sus z (' + n5(D1.escala.z_municipal) + ' y ' + n5(D1.escala.z_departamental) + ') se comparan '
          + 'sin más: con ' + D1.escala.n_departamental + ' unidades, una I igual a la municipal tendría z = '
          + n5(D1.escala.z_departamental_si_igual) + '.',
        retroFallo: 'Cae el ' + n5(D1.escala.caida_pct) + ' %. Es una descripción de las dos cifras, no una medida '
          + 'de cuánta autocorrelación se pierde: las dos I usan pesos y n distintos. Tampoco sus z ('
          + n5(D1.escala.z_municipal) + ' y ' + n5(D1.escala.z_departamental) + ') se comparan sin más: con '
          + D1.escala.n_departamental + ' unidades, una I igual a la municipal tendría z = '
          + n5(D1.escala.z_departamental_si_igual) + '. Módulo 7.'
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
        retroFallo: 'Las dos ciertas son la del tipo de la CAPA frente al de cada rasgo y la de las unidades sin vecinos en el I de Moran. Módulo 9.'
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

    # La plantilla trae un simulacro de demostración desde 2026-09-18. Este
    # documento no publica ninguno, así que su registro se borra en vez de
    # viajar muerto: el ÚNICO que lo sustituye por uno real es el capítulo 4.
    doc = reemplaza_region(doc, "    SIMULACROS['demo'] = {", "\n    };\n",
                           "", "el simulacro de demostración", max_lineas=40)

    # Y la tabla de ranking de demostración, por lo mismo. Esta llevaba ahí
    # desde que existe el componente: el preparcial la borraba —su guarda no
    # deja sobrevivir ningún demo— y nadie más, así que viajaba en nueve de los
    # once documentos sin que ninguno tenga un `data-tabla-ranking` que pintar.
    doc = reemplaza_region(doc, "    TABLAS_RANKING['demo'] = function () {", "\n    };\n",
                           "", "la tabla de ranking de demostración", max_lineas=40)

    DESTINO.parent.mkdir(parents=True, exist_ok=True)
    # El orden de las opciones se decide en `baraja_opciones.py`, y es la
    # corrección del 2026-09-02: escritas de una en una, las 51 preguntas de
    # los cinco capítulos tenían la correcta la PRIMERA, y el motor no baraja.
    doc = baraja_documento(doc, "cap1")

    doc = aplica_boton(doc, DESTINO, RAIZ, "franja")
    # Capa de fuentes (2026-11-12): el texto de las <cite class="cita"> y la lista de
    # referencias del capítulo los escribe genera_referencias.py desde la instantánea de
    # Zotero. Nadie los teclea; audita_citas.py (F02) comprueba que no se desfasen.
    doc = genera_referencias.genera(doc, *genera_referencias.carga_biblioteca())
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
    # Y al revés: `\,` es el espacio fino de LaTeX y solo existe DENTRO de una
    # fórmula. En la prosa sale tal cual, y el módulo 5 publicó «pasar de 25 a
    # 1\,000 observaciones» porque `ent_mate()` se usó fuera de `\(...\)`.
    prosa = re.sub(r"\\\(.*?\\\)|\$\$.*?\$\$|<script.*?</script>|<pre.*?</pre>",
                   " ", marcado, flags=re.S)
    crudos = [" ".join(m.group(0).split()) for m in re.finditer(r"[^<>]{0,30}\\,[^<>]{0,12}", prosa)]
    if crudos:
        problemas.append(f"{len(crudos)} espacio(s) fino(s) de LaTeX fuera de una fórmula, que salen "
                         f"crudos en la prosa: {crudos[:3]} — fuera de \\(...\\) va ent()")
    # Una barra invertida SUELTA en la prosa de este archivo no llega al HTML
    # como barra: Python la lee como secuencia de escape y `\\bar`, `\\rho`,
    # `\\frac` y `\\text` escritos con una sola barra se convierten en un
    # retroceso, un retorno de carro, un salto de página y un tabulador. La
    # fórmula deja de serlo, KaTeX protesta en la consola de UN módulo y los
    # auditores de cifras siguen en verde, porque las cifras están. Pasó al
    # reescribir el módulo 5 y lo vio solo la comprobación en el navegador.
    control = sorted({f"U+{ord(c):04X}" for c in doc if ord(c) < 32 and c not in "\n\t"})
    if control or "\t" in marcado:
        problemas.append(f"el documento lleva caracteres de control ({control or ['U+0009']}): "
                         f"casi seguro una fórmula escrita con una sola barra invertida")
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

    # El ejercicio 3, sobre lo que su lectura AFIRMA. La lectura la escribe R
    # con las cifras dentro, así que cada número existe en el JSON; lo que
    # ningún auditor de cifras ve son las frases: «la red actual ya la
    # supera», «la de 50 no la alcanza ninguna red», «siempre entre 25 y 50»,
    # «aquí −0.00278». Y que el ejercicio se pueda hacer: el archivo que
    # enlaza tiene que existir donde el enlace dice.
    g3, t3 = S["e3"]["solucion"], S["e3"]
    texto3 = " ".join([t3["enunciado"], t3["lectura"]] + [str(p["paso"]) for p in t3["pasos"]]
                      + [str(p["valor"]) for p in t3["pasos"]])
    # `ESPACIAL_RAIZ` es la raíz de verdad cuando el arnés ejecuta una copia
    # del ensamblador desde un temporal: el archivo se busca en el repo.
    raiz_repo = pathlib.Path(os.environ.get("ESPACIAL_RAIZ") or RAIZ)
    if not (raiz_repo / g3["archivo"]).is_file():
        problemas.append(f"el ejercicio 3 enlaza {g3['archivo']}, que no está en el repo")
    if not g3["archivo"].startswith("entrega/datos/"):
        problemas.append(f"el ejercicio 3 lee {g3['archivo']}, que no es un archivo publicado")
    if f'href="../{g3["archivo"]}"' not in doc:
        problemas.append("el ejercicio 3 no enlaza la descarga de su archivo")
    if not (0 < g3["n_eff"] < g3["n"] and g3["rho_medio"] > 0):
        problemas.append("ejercicio 3: el remuestreo por bloques no ensancha, y todo el "
                         "apartado (b) parte de que sí")
    if abs((g3["n"] / g3["n_eff"] - 1) / (g3["n"] - 1) - g3["rho_medio"]) > 1e-9:
        problemas.append("ejercicio 3: la correlación media no es la que se despeja del n_eff")
    obj_bajo, obj_alto = g3["objetivos"]
    if not (g3["objetivo_25_alcanzable"] and not g3["objetivo_50_alcanzable"]
            and obj_bajo < g3["techo"] < obj_alto):
        problemas.append(f"ejercicio 3: el techo ({g3['techo']}) ya no separa {obj_bajo} de "
                         f"{obj_alto}, y la lectura y la tabla dicen que sí")
    if not (obj_bajo < g3["otras_semillas"]["techo_min"]
            <= g3["otras_semillas"]["techo_max"] < obj_alto):
        problemas.append("ejercicio 3: con otras semillas el techo se sale de entre los dos "
                         "objetivos, y la lectura dice «siempre»")
    if not (g3["n_para_25"] <= g3["estaciones_para_25"] < g3["n_para_25"] + 1
            and g3["estaciones_para_25"] < g3["n"]):
        problemas.append("ejercicio 3: las estaciones para el primer objetivo no son el "
                         "redondeo hacia arriba, o la red actual ya no las supera")
    for clave in ("ee_iid", "ee_bloques", "factor", "n_eff", "pct_informacion", "rho_medio",
                  "techo", "n_para_25"):
        if n(g3[clave]) not in t3["lectura"]:
            problemas.append(f"ejercicio 3: la lectura no cita {clave} = {n(g3[clave])}")
    esperado3 = -1 / (g3["n"] - 1)
    if abs(g3["centrado_todos_los_pares"] - esperado3) > 1e-9 or \
            n(g3["centrado_todos_los_pares"]).replace("-", "−") not in t3["lectura"]:
        problemas.append("ejercicio 3: el promedio centrado de todos los pares no es "
                         "−1/(n − 1), o la lectura no lo cita")
    for vetada in ("equicorrelaci", "estima la correlación", "todos los pares:",
                   "datos/procesado"):
        if vetada in texto3.lower():
            problemas.append(f"ejercicio 3: vuelve «{vetada}», que es el planteamiento que "
                             f"R1 retiró")
    for campo in ("bandas_km", "moran_por_banda", "pares_por_banda"):
        if campo in g3:
            problemas.append(f"ejercicio 3: vuelve el campo {campo} del correlograma por bandas")
    # El archivo tiene que estar VERSIONADO, no solo en el disco: `datos/` existe
    # en la máquina de quien ensambla y no en el sitio. Si git no está o esto no
    # es un repo, la comprobación se salta y se dice; no se da por buena.
    try:
        en_git = subprocess.run(["git", "ls-files", "--error-unmatch", g3["archivo"]],
                                cwd=str(raiz_repo), capture_output=True, text=True)
        if en_git.returncode == 1:
            problemas.append(f"el ejercicio 3 enlaza {g3['archivo']}, que no está versionado: "
                             f"no llegará al sitio")
        elif en_git.returncode != 0:
            print(f"  ejercicio 3: git no pudo decir si {g3['archivo']} está versionado "
                  f"(código {en_git.returncode}); no se comprueba")
    except OSError:
        print(f"  ejercicio 3: git no está disponible; no se comprueba que {g3['archivo']} "
              f"esté versionado")

    # (b), segunda mitad: «frente al dato, no». La lectura nombra los dos
    # departamentos de los extremos y dice que UNO SOLO voltea la respuesta.
    jk3 = g3["jackknife"]
    techos_jk = [d["techo"] for d in jk3["por_departamento"]]
    if len(techos_jk) != g3["n_bloques"]:
        problemas.append("ejercicio 3: el jackknife no trae un techo por departamento")
    if jk3["minimo"]["techo"] != min(techos_jk) or jk3["maximo"]["techo"] != max(techos_jk):
        problemas.append("ejercicio 3: el mínimo o el máximo del jackknife no son los de su lista")
    sobre_jk = sum(t > obj_alto for t in techos_jk)
    if sobre_jk != jk3["n_sobre_objetivo"] or sobre_jk != 1 or not jk3["maximo"]["techo"] > obj_alto:
        problemas.append(f"ejercicio 3: {sobre_jk} departamento(s) llevan el techo por encima de "
                         f"{obj_alto} al quitarlos, y la lectura dice que uno solo voltea la respuesta")
    if not obj_bajo < jk3["minimo"]["techo"] < g3["techo"] < jk3["maximo"]["techo"]:
        problemas.append("ejercicio 3: el techo de la red entera no queda entre los dos extremos "
                         "del jackknife")
    # «Aquí pesa más que la semilla»: el recorrido del jackknife contiene al de las semillas.
    if not (jk3["minimo"]["techo"] < g3["otras_semillas"]["techo_min"]
            and g3["otras_semillas"]["techo_max"] < jk3["maximo"]["techo"]):
        problemas.append("ejercicio 3: quitar un departamento ya no mueve el techo más que "
                         "cambiar de semilla, y la lectura dice que sí")
    for extremo in ("minimo", "maximo"):
        if f"{n(jk3[extremo]['techo'])} sin {jk3[extremo]['departamento']}" not in t3["lectura"]:
            problemas.append(f"ejercicio 3: la lectura no cita el techo sin "
                             f"{jk3[extremo]['departamento']}")
        if not any(p["paso"].endswith(f"sin {jk3[extremo]['departamento']}")
                   and p["valor"] == jk3[extremo]["techo"] for p in t3["pasos"]):
            problemas.append(f"ejercicio 3: la tabla no trae el techo sin "
                             f"{jk3[extremo]['departamento']}")
    # (c): con pesos por filas el promedio «sale positivo» y «depende de la elección».
    pf3 = g3["pesos_filas"]
    if not all(v > 0 for v in pf3["promedio"]) or len({n(v) for v in pf3["promedio"]}) != len(pf3["promedio"]):
        problemas.append("ejercicio 3: el promedio con pesos por filas no es positivo o no cambia "
                         "con el ancho de banda, y la lectura dice las dos cosas")
    for ancho, v in zip(pf3["anchos_km"], pf3["promedio"]):
        if f"{ancho} km" not in t3["lectura"] or n(v) not in t3["lectura"]:
            problemas.append(f"ejercicio 3: la lectura no cita el promedio con bandas de {ancho} km")
    # (d): con los residuos «la correlación baja» y 50 «pide ahora» un número finito.
    r3 = g3["residuos"]
    if not (0 < r3["rho_medio"] < g3["rho_medio"] and r3["techo"] > obj_alto
            and r3["objetivo_50_alcanzable"] and r3["techo_sube"]
            and g3["otras_semillas"]["residuos_techo_min"] > obj_alto):
        problemas.append(f"ejercicio 3: con los residuos de la altitud el techo ({r3['techo']}) ya "
                         f"no pasa de {obj_alto}, o no con todas las semillas, y el apartado (d) "
                         f"dice que sí")
    if abs((g3["n"] / r3["n_eff"] - 1) / (g3["n"] - 1) - r3["rho_medio"]) > 1e-9:
        problemas.append("ejercicio 3: la correlación media de los residuos no se despeja de su n_eff")
    if not r3["n_para_50"] <= r3["estaciones_para_50"] < r3["n_para_50"] + 1:
        problemas.append("ejercicio 3: las estaciones para 50 con los residuos no son el redondeo "
                         "hacia arriba")
    for clave in ("r2", "n_eff", "rho_medio", "techo", "caida_rho_pct", "n_para_50"):
        if n(r3[clave]) not in t3["lectura"]:
            problemas.append(f"ejercicio 3: la lectura no cita residuos.{clave} = {n(r3[clave])}")
    if not 0.5 < r3["r2"] < 1:
        problemas.append("ejercicio 3: la altitud ya no explica «casi toda» la temperatura")
    for apartado in ("(a)", "(b)", "(c)", "(d)"):
        if apartado not in t3["enunciado"] or f"{apartado} " not in t3["lectura"]:
            problemas.append(f"ejercicio 3: el apartado {apartado} no está en el enunciado y en la lectura")
    print(f"  ejercicio 3: n_eff {n(g3['n_eff'])} de {g3['n']}, techo {n(g3['techo'])} "
          f"entre {obj_bajo} y {obj_alto}; lee {g3['archivo']}")

    # El módulo 5, sobre lo que su prosa AFIRMA y ningún auditor ve. El de
    # prosa comprueba que cada cifra exista en el JSON y el del precálculo
    # comprueba cada cifra por su lado; ninguno lee las frases que las unen
    # —«el mismo número en todas», «no sube», «más que el valor que busca»—.
    # Hasta R1 esta guarda protegía la discrepancia entre un rho «implícito»
    # y otro «medido»; el segundo se retiró porque no estimaba nada (el
    # promedio centrado de todos los pares vale -1/(n-1) con cualquier dato)
    # y la guarda vigila ahora que no vuelva.
    rtg, czg, tcg = ne["rho_del_titular"], ne["centrado"], ne["techo"]
    inf5 = D["inferencia"]      # `inf` a secas es otra cosa dentro de main()
    if rtg["n"] != ne["desercion_n"]:
        problemas.append(f"el rho del titular habla de {rtg['n']} municipios y el módulo "
                         f"publica {ne['desercion_n']}")
    if abs(rtg["n"] / (1 + (rtg["n"] - 1) * rtg["implicito"])
           - ne["desercion_municipal"]) > 1e-5:
        problemas.append(f"el rho medio {rtg['implicito']} ya no reproduce el "
                         f"{ne['desercion_municipal']} del titular, y la prosa dice que su "
                         f"curva pasa por el rombo porque de ahí se despeja")
    RETIRADOS = {"estimado", "n_eff_con_estimado", "razon_rho", "razon_n_eff",
                 "I_primera_banda", "n_bandas", "pares_totales", "pares_lejanos",
                 "bandas", "metodo"}
    if RETIRADOS & set(rtg):
        problemas.append(f"vuelve el «rho medido» al JSON: {sorted(RETIRADOS & set(rtg))} — "
                         f"ese promedio por bandas no estima el rho medio")
    # «Es exacta»: los dos n_eff del campo se imprimen uno junto al otro y la
    # prosa dice que son el mismo número.
    if n(e4["n_eff"]) != n(e4["n_eff_formula"]):
        problemas.append(f"el n_eff exacto ({e4['n_eff']}) y el de la fórmula "
                         f"({e4['n_eff_formula']}) ya no se imprimen iguales, y la prosa "
                         f"dice que son el mismo número")
    # La demostración del centrado.
    if (czg["n"], czg["phi"], czg["nrep"]) != (inf5["n"], r4["phi"], inf5["nrep"]):
        problemas.append("la demostración del centrado ya no corre sobre las réplicas del "
                         "módulo 4 con phi = 4, que es lo que dice la prosa")
    if czg["rho_medio_verdadero"] != e4["rho_medio"]:
        problemas.append("el rho medio verdadero de la demostración no es el de la fila de "
                         "phi = 4 de exacto_campo")
    if not (n(czg["centrado_min"]) == n(czg["centrado_max"]) == n(czg["menos_inv_n1"])):
        problemas.append(f"el promedio centrado va de {czg['centrado_min']} a "
                         f"{czg['centrado_max']} y -1/(n-1) vale {czg['menos_inv_n1']}: la "
                         f"prosa dice «el mismo número en todas»")
    if (czg["colombia"]["n"] != ne["desercion_n"]
            or n(czg["colombia"]["centrado"]) != n(czg["colombia"]["menos_inv_n1"])):
        problemas.append("sobre la deserción el promedio centrado ya no se imprime como "
                         "-1/(n-1), o habla de otros municipios")
    cmv = czg["con_media_verdadera"]
    if abs(cmv["media"] - czg["rho_medio_verdadero"]) > 4 * cmv["emc"]:
        problemas.append(f"con la media verdadera el promedio da {cmv['media']} y la prosa "
                         f"dice que apunta a {czg['rho_medio_verdadero']}")
    if not cmv["sd"] > czg["rho_medio_verdadero"]:
        problemas.append(f"la desviación típica entre réplicas ({cmv['sd']}) ya no supera "
                         f"al rho medio ({czg['rho_medio_verdadero']}): la prosa dice «más que "
                         f"el valor que busca»")
    # La media y la varianza que la prosa nombra son las que R usó, y el
    # proceso es el del módulo 4, que declara su sigma.
    if czg["varianza"] != inf5["sigma"] ** 2:
        problemas.append(f"la demostración del centrado declara varianza {czg['varianza']} y "
                         f"el módulo 4 declara sigma = {inf5['sigma']}: ya no es el mismo proceso")
    # El rho medio de Colombia y su corrección por s^2: la prosa dice «un
    # tanto por ciento MENOS» y «la corrección es pequeña».
    if not (rtg["implicito_con_s2"] < rtg["implicito"] and 0 < rtg["diferencia_s2_pct"] < 5):
        problemas.append(f"la corrección por s² del rho medio de Colombia ya no es una rebaja "
                         f"pequeña ({rtg['diferencia_s2_pct']} %), y la prosa lo dice así")
    # La tabla «rellenar frente a ampliar» y las frases que la leen.
    tf = tcg["rejilla"]
    f16 = next((f for f in tf if f["k"] == inf5["k"]), None)
    if f16 is None or not (n(f16["relleno"]["n_eff"]) == n(f16["ampliacion"]["n_eff"])
                           == n(e4["n_eff"])):
        problemas.append(f"la tabla del techo no trae la fila de {inf5['k']} celdas por lado, "
                         f"o ya no coincide con la retícula del módulo 4 como dice su pie")
    if tcg["phi"] != r4["phi"] or tcg["lado_relleno"] != inf5["k"]:
        problemas.append("la tabla del techo ya no usa el alcance ni el lado del módulo 4")
    if tcg["factor_n"] * tf[0]["n"] != tf[-1]["n"]:
        problemas.append("factor_n no es el cociente entre la última fila y la primera")
    # El relleno SE ESTANCA, y la prosa lo dice con tres frases: «apenas se
    # mueve», «la última fila queda a un … % de él» y «se acerca al techo
    # desde abajo». Las cotas son las del generador (medido: 0,059 % el
    # último salto y 0,017 % lo que falta), con la misma holgura.
    if not abs(tcg["ultimo_salto_pct"]) < 0.25:
        problemas.append(f"al rellenar, el último salto mueve el n_eff un "
                         f"{tcg['ultimo_salto_pct']} %: la prosa dice que se estanca")
    if not 0 <= tcg["falta_techo_pct"] < 0.1:
        problemas.append(f"al rellenar, la última fila queda a {tcg['falta_techo_pct']} % de "
                         f"1/rho_inf: la prosa dice que está en el límite y por debajo")
    if any(f["relleno"]["n_eff"] > tcg["techo_inf"] for f in tf):
        problemas.append("al rellenar, alguna fila supera 1/rho_inf, y la prosa dice que con "
                         "este diseño el n_eff se acerca al techo desde abajo")
    if abs(1 / tcg["rho_inf"] - tcg["techo_inf"]) > 1e-6:
        problemas.append("techo_inf ya no es 1/rho_inf, y la prosa lo llama su inverso")
    if not (tf[-1]["ampliacion"]["rho_medio"] < tf[0]["ampliacion"]["rho_medio"]
            and tcg["factor_ampliacion"] > 1):
        problemas.append("al ampliar, el rho medio no cae o el n_eff no crece: la prosa "
                         "dice lo contrario")
    # La prosa da el techo de rhos[1] sin dividir (sin_aritmetica.py): lo lee de
    # caso_quiz.techo_otro, que R calcula para la misma correlación. Si R cambiara
    # uno sin el otro, la frase mentiría.
    cq = ne["caso_quiz"]
    if not (cq["rho_otro"] == ne["rhos"][1] and abs(cq["techo_otro"] * ne["rhos"][1] - 1) < 1e-9):
        problemas.append("el módulo 5 da el techo de rhos[1] con caso_quiz.techo_otro, y ya no son "
                         "la misma correlación o el techo no es su inverso")
    print(f"  módulo 5: rho medio de Colombia {n(rtg['implicito'], 7)} · n_eff exacto y de "
          f"fórmula {n(e4['n_eff'])} · centrado {n(czg['centrado_min'], 7)} en "
          f"{czg['nrep']} réplicas · tabla del techo de {len(tf)} filas")

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

    # ----------------------------------------------------------------
    # R1 · T1.4. Las afirmaciones nuevas de los módulos 2, 6 y 10 y de la
    # pregunta del gráfico que dependen de una cifra. Cada una es una frase
    # que quedaría falsa, con todos los auditores de cifras en verde, si el
    # dato cambiara de dirección.
    # ----------------------------------------------------------------
    # Módulo 2: «el perímetro urbano está contenido en el Distrito» y «el
    # Distrito añade un territorio extenso y casi sin sedes». Lo segundo se
    # mide: la intensidad de lo que el Distrito añade, por debajo de una
    # décima de la del perímetro (medido: 0.08 frente a 5.69 sedes/km²).
    pu = co["puntual"]
    # Estricto en las sedes: la prosa afirma que HAY sedes dentro del Distrito
    # y fuera del perímetro.
    if not (pu["n_urbana"] < pu["n_dc"] and pu["area_urbana_km2"] < pu["area_dc_km2"]):
        problemas.append("módulo 2: el perímetro urbano ya no cabe en el Distrito con sedes de "
                         "sobra (tantas o más sedes, o más área): la prosa dice que está "
                         "contenido en él y que hay sedes dentro del Distrito y fuera del perímetro")
    else:
        lam_resto = ((pu["n_dc"] - pu["n_urbana"])
                     / (pu["area_dc_km2"] - pu["area_urbana_km2"]))
        if not lam_resto < 0.1 * pu["lambda_urbana"]:
            problemas.append(f"módulo 2: lo que el Distrito añade al perímetro tiene {lam_resto:.3f} "
                             f"sedes/km², y la prosa lo llama «casi sin sedes»")
    if not pu["factor_lambda"] > 1:
        problemas.append("módulo 2: la intensidad del perímetro ya no supera a la del Distrito")

    # Módulo 6: la referencia del variograma es el teórico PROMEDIADO EN LA
    # CLASE. La prosa dice (a) que en el rezago 1 no coincide con gamma(1),
    # (b) que la media de las realizaciones cae sobre el primero y no sobre
    # el segundo, y (c) «contra esa referencia» da tres desvíos y sus
    # rezagos: se rehacen aquí contra `teorico_clase`, de modo que si R
    # volviera a medirlos contra gamma en h entero la frase no saldría.
    tcl, ten, vme = vg6.get("teorico_clase", []), vg6["teorico"], vg6["media"]
    if len(tcl) != n_lags:
        problemas.append(f"módulo 6: el teórico de la clase trae {len(tcl)} rezagos y la "
                         f"banda {n_lags}: la curva punteada no se podría dibujar")
    else:
        if n(tcl[0]) == n(ten[0]):
            problemas.append("módulo 6: en el rezago 1 el teórico de la clase y gamma(1) se "
                             "publican iguales, y la prosa los distingue")
        if not abs(vme[0] - tcl[0]) < 0.1 * abs(vme[0] - ten[0]):
            problemas.append(f"módulo 6: la media de las realizaciones en el rezago 1 "
                             f"({vme[0]}) ya no cae sobre el teórico de la clase ({tcl[0]}) "
                             f"y lejos de gamma(1) ({ten[0]}), como dice la prosa")
        for fila in rv:
            if len(fila.get("variograma", [])) != n_lags:
                continue                      # ya denunciada arriba
            rel = [abs(v - t) / t for v, t in zip(fila["variograma"], tcl)]
            if (abs(max(rel) - fila["desvio_rel_max"]) > 1e-7
                    or vg6["lags"][rel.index(max(rel))] != fila["lag_desvio_max"]
                    or abs(rel[vg6["lags"].index(4)] - fila["desvio_rel_lag4"]) > 1e-7):
                problemas.append(f"realización {fila['id']}: sus desvíos publicados no son "
                                 f"los medidos contra el teórico de la clase, que es la "
                                 f"referencia que la prosa declara")

    # Módulo 10: la red frente a la referencia de puntos uniformes. El
    # argumento se sostiene solo si la red queda MUY por encima: diez veces
    # el percentil 95 y por encima de la mayor razón simulada. Si deja de
    # estarlo, el ensamblado para y el párrafo se reescribe.
    if not (ru["n_puntos"] == dm["n"]):
        problemas.append("módulo 10: la referencia uniforme no usa tantos puntos como "
                         "estaciones tiene la red")
    if not (ru["razon_p05"] < ru["razon_mediana_ic95"][0] <= ru["razon_mediana"]
            <= ru["razon_mediana_ic95"][1] < ru["razon_p95"] <= ru["razon_max"]):
        problemas.append("módulo 10: los cuantiles de la referencia uniforme no están en orden "
                         "(p05 < IC de la mediana < p95 <= máximo)")
    if not (dm["razon_areas"] > 10 * ru["razon_p95"] and dm["razon_areas"] > ru["razon_max"]):
        problemas.append(f"módulo 10: la razón de áreas de la red ({dm['razon_areas']}) ya no "
                         f"queda claramente por encima de la referencia uniforme (p95 = "
                         f"{ru['razon_p95']}, máx. = {ru['razon_max']}): el argumento no se "
                         f"sostiene como está escrito")
    if (abs(dm["razon_areas"] / ru["razon_mediana"] - ru["red_sobre_mediana"]) > 1e-6
            or abs(dm["razon_areas"] / ru["razon_p95"] - ru["red_sobre_p95"]) > 1e-6):
        problemas.append("módulo 10: «veces la mediana» o «veces el percentil 95» no son el "
                         "cociente de las cifras que la misma frase publica")

    # Q4: la retroalimentación del distractor dice que la media es
    # insesgada (el promedio de las medias, a menos de cuatro errores de
    # Monte Carlo de la media verdadera) y que el e.e. real CRECE de un
    # extremo al otro de la rejilla del gráfico.
    emc_media = ur["sd_de_las_medias"] / ur["n_realizaciones"] ** 0.5
    if not abs(ur["media_de_las_medias"] - ur["media_del_proceso"]) < 4 * emc_media:
        problemas.append(f"Q4: el promedio de las medias ({ur['media_de_las_medias']}) queda a "
                         f"más de cuatro errores de Monte Carlo de la media verdadera: la "
                         f"retroalimentación dice «no hay sesgo»")
    rej4 = D["inferencia"]["rejilla"]
    if not rej4[-1]["ee_real"] > 2 * rej4[0]["ee_real"]:
        problemas.append("Q4: el e.e. real ya no crece de un extremo al otro de la rejilla, "
                         "y la retroalimentación dice que la media es cada vez menos precisa")
    print(f"  T1.4: perímetro dentro del Distrito · teórico de clase {n(tcl[0]) if tcl else '—'} "
          f"frente a gamma(1) = {n(ten[0])} · red {n(dm['razon_areas'], 1)} frente a p95 "
          f"{n(ru['razon_p95'], 1)} de la referencia")

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
        # R1 · T1.6 (C1-12). La referencia se dibuja banda a banda con la de
        # `ideam`; vale para las tres porque comparten estaciones y bandas.
        if [(b["n_con_vecinos"], b["esperado"], b["esperado_programa"]) for b in tb[nombre]["bandas"]] != \
                [(b["n_con_vecinos"], b["esperado"], b["esperado_programa"]) for b in tb["ideam"]["bandas"]]:
            problemas.append(f"la E[I] por banda de tobler.{nombre} no es la de ideam: la línea de "
                             f"referencia del correlograma solo sería la de una de las tres series")
    # Lo que el módulo 3 AFIRMA de esa referencia (C1-12): que es la esperanza
    # por permutación, -n'/(n(n - 1)), con n' las estaciones con vecinos; que
    # el programa imprime otra, -1/(n' - 1); que permutando de verdad sale la
    # primera y no la segunda; que en la banda corta faltan estaciones y en
    # la última están todas —la lectura del simulador empareja el -1/(n - 1)
    # del conjunto con el n de esa banda—.
    n_est3 = co["geo"]["n"]
    for b in tb["ideam"]["bandas"]:
        if abs(b["esperado"] + b["n_con_vecinos"] / (n_est3 * (n_est3 - 1))) > 1e-9:
            problemas.append(f"la E[I] de la banda {b['d1']}-{b['d2']} ({b['esperado']}) no es "
                             f"-n'/(n(n - 1)) con n' = {b['n_con_vecinos']}, y la prosa lo dice")
        if abs(b["esperado_programa"] + 1 / (b["n_con_vecinos"] - 1)) > 1e-9:
            problemas.append(f"la esperanza que imprime el programa en la banda {b['d1']}-{b['d2']} "
                             f"({b['esperado_programa']}) no es -1/(n' - 1), y la prosa dice que sí")
    if not (abs(pb1["media"] - b0["esperado"]) < 4 * pb1["emc"]
            < abs(pb1["media"] - b0["esperado_programa"])):
        problemas.append(f"la media de las permutaciones de la primera banda ({pb1['media']} ± {pb1['emc']}) "
                         f"ya no respalda -n'/(n(n - 1)) frente a la convención del programa")
    if not b0["n_con_vecinos"] < n_est3:
        problemas.append(f"en la primera banda las {b0['n_con_vecinos']} estaciones tienen vecinos: el "
                         f"módulo 3 dice que solo las tienen algunas de las {n_est3}")
    if tb["ideam"]["bandas"][-1]["n_con_vecinos"] != n_est3:
        problemas.append("en la última banda ya no tienen vecinos todas las estaciones: su referencia "
                         "no es el -1/(n - 1) del conjunto que la prosa y la lectura le ponen al lado")
    # La fila «cuánto de la I era altitud» solo sale con las dos series
    # encendidas, y es exactamente esta cuenta entre ellas.
    i_r, i_a = tb["ideam"]["bandas"][0]["I"], tb["residuos_altitud"]["bandas"][0]["I"]
    if abs(100 * (i_r - i_a) / i_r - tb["caida_por_altitud_pct"]) > 5e-8:
        problemas.append(f"caida_por_altitud_pct ({tb['caida_por_altitud_pct']}) no es la caída "
                         f"de {i_r} a {i_a} entre las dos series que el interruptor compara")
    print(f"  módulo 3: {len(bandas_ref)} bandas comunes a las 3 series · "
          f"E[I] = {n(tb['ideam']['esperado'], 6)} para las tres")

    # --- R1 · T1.6 · lo que el módulo 4 afirma de su remuestreo ---------
    #
    # Ninguna de estas frases es una cifra, así que ningún auditor las lee:
    # «por encima», «no es ruido», «a menos de un error de Monte Carlo»,
    # «muy desiguales», «el extremo lo pone», «baja», «sube», «bastante
    # menos». Cada una depende de un signo o de un orden que R podría cambiar
    # con otro dato.
    irg = D["inferencia_real"]
    rpg, osg, sug = irg["replicas"], irg["otras_semillas"], irg["sin_un_departamento"]
    if not rpg["desvio_esperanza"] > 0 or \
            abs(rpg["esperanza_bloques"] - irg["media"] - rpg["desvio_esperanza"]) > 1e-8:
        problemas.append(f"la esperanza de las réplicas por departamentos es {rpg['esperanza_bloques']} y la "
                         f"media muestral {irg['media']}: el módulo 4 dice «{rpg['desvio_esperanza']} por encima»")
    if not rpg["desvio_esperanza"] > 10 * rpg["emc_esperanza"]:
        problemas.append(f"el desvío de la esperanza ({rpg['desvio_esperanza']}) no supera diez veces su "
                         f"error de Monte Carlo ({rpg['emc_esperanza']}), y el módulo 4 dice que no es ruido")
    if not abs(rpg["media_bloques"] - rpg["esperanza_bloques"]) < 3 * rpg["emc_media_bloques"]:
        problemas.append(f"las réplicas de la tabla promedian {rpg['media_bloques']}, fuera de su ruido "
                         f"alrededor de la esperanza {rpg['esperanza_bloques']}: la prosa dice «dentro»")
    if not abs(rpg["desvio_iid"]) < rpg["emc_media_iid"]:
        problemas.append(f"las réplicas i.i.d. se desvían {rpg['desvio_iid']} de la media muestral, más "
                         f"que un error de Monte Carlo ({rpg['emc_media_iid']}), y la prosa dice que menos")
    if not rpg["bloque_max"] >= 10 * rpg["bloque_min"]:
        problemas.append(f"los departamentos tienen entre {rpg['bloque_min']} y {rpg['bloque_max']} "
                         f"municipios: ya no son «de tamaños muy desiguales»")
    filas_jk = sug["por_departamento"]
    if len(filas_jk) != irg["n_departamentos"] or \
            sug["n_departamentos_quedan"] != irg["n_departamentos"] - 1 or \
            sum(f["municipios"] for f in filas_jk) != irg["n_municipios"]:
        problemas.append("la lista de «un departamento menos» no recorre los departamentos del módulo 4 "
                         "o sus municipios no suman los del remuestreo")
    else:
        fac_jk = [f["factor"] for f in filas_jk]
        nef_jk = [f["n_eff"] for f in filas_jk]
        if (min(fac_jk), max(fac_jk), min(nef_jk), max(nef_jk)) != \
                (sug["factor_min"], sug["factor_max"], sug["n_eff_min"], sug["n_eff_max"]):
            problemas.append("los recorridos del factor y del tamaño efectivo sin un departamento no son "
                             "el mínimo y el máximo de la lista que R publica")
        ext = sug["extremo"]
        if ext != filas_jk[fac_jk.index(min(fac_jk))] or ext["n_eff"] != max(nef_jk):
            problemas.append(f"{ext['departamento']} no es el departamento cuya ausencia da el factor "
                             f"más bajo y el tamaño efectivo más alto, y la prosa lo nombra")
        if not (ext["factor"] < irg["factor"] and ext["n_eff"] > irg["n_eff"]):
            problemas.append(f"sin {ext['departamento']} el factor ya no queda por debajo del de la "
                             f"tabla del módulo 4, o el tamaño efectivo por encima")
    if not (sug["factor_min"] < irg["factor"] < sug["factor_max"]
            and sug["n_eff_min"] < irg["n_eff"] < sug["n_eff_max"]):
        problemas.append("el factor o el tamaño efectivo del titular quedan fuera del recorrido que da "
                         "quitar un departamento")
    # El recorrido NO es la incertidumbre: el error estándar jackknife sale de
    # los mismos valores, supera a medio recorrido y deja el tamaño efectivo
    # «en orden de magnitud».
    if len(filas_jk) == irg["n_departamentos"]:
        def _ee_jk(v):
            m_ = sum(v) / len(v)
            return ((len(v) - 1) / len(v) * sum((x - m_) ** 2 for x in v)) ** 0.5
        if abs(_ee_jk([f["factor"] for f in filas_jk]) - sug["ee_jackknife_factor"]) > 1e-7 or \
                abs(_ee_jk([f["n_eff"] for f in filas_jk]) - sug["ee_jackknife_n_eff"]) > 1e-6:
            problemas.append("el error estándar jackknife publicado no sale de los valores de la lista "
                             "«un departamento menos»")
    if not ((sug["factor_max"] - sug["factor_min"]) / 2 < sug["ee_jackknife_factor"]
            and (sug["n_eff_max"] - sug["n_eff_min"]) / 2 < sug["ee_jackknife_n_eff"]):
        problemas.append("medio recorrido ya no queda por debajo del error estándar jackknife, y el "
                         "módulo 4 dice que el recorrido se queda corto")
    # «Queda muy lejos de los 1 121»: ni a tres errores estándar jackknife por encima llega a la cuarta
    # parte de los municipios.
    if not irg["n_eff"] + 3 * sug["ee_jackknife_n_eff"] < irg["n_municipios"] / 4:
        problemas.append(f"el tamaño efectivo más tres e.e. jackknife ({irg['n_eff']} + 3 × "
                         f"{sug['ee_jackknife_n_eff']}) llega a la cuarta parte de los municipios: «muy lejos "
                         f"de los {irg['n_municipios']}» ya no se sostiene")
    if not sug["ee_jackknife_n_eff_pct"] > 25 or \
            abs(100 * sug["ee_jackknife_n_eff"] / irg["n_eff"] - sug["ee_jackknife_n_eff_pct"]) > 1e-6:
        problemas.append(f"el e.e. jackknife del tamaño efectivo es el {sug['ee_jackknife_n_eff_pct']} % "
                         f"de la cifra: «solo en orden de magnitud» ya no se sostiene")
    if not (osg["n_eff_max"] - osg["n_eff_min"]) < 0.5 * (sug["n_eff_max"] - sug["n_eff_min"]):
        problemas.append(f"cambiar de semilla mueve el tamaño efectivo de {osg['n_eff_min']} a "
                         f"{osg['n_eff_max']}: ya no es «bastante menos» que quitar un departamento")
    # El módulo 6 nombra la prueba y su nivel; el 5 % que «debería» rechazar
    # es ese mismo alfa.
    if abs(100 * D["inferencia"]["alfa"] - ur["pct_esperado_si_valiera"]) > 1e-9:
        problemas.append(f"el módulo 6 enuncia la prueba con alfa = {D['inferencia']['alfa']} y dice que "
                         f"debería rechazar en el {ur['pct_esperado_si_valiera']} %")
    # El módulo 7 acompaña cada I de su z y dice qué se sigue de ellas.
    if not (es["z_municipal"] > 3 and es["p_departamental"] > D["inferencia"]["alfa"]):
        problemas.append(f"la I municipal (z = {es['z_municipal']}) ya no es inequívoca o la departamental "
                         f"(p = {es['p_departamental']}) ya se distingue del azar: el módulo 7 dice lo contrario")
    if not es["z_departamental"] < es["z_departamental_si_igual"] < es["z_municipal"]:
        problemas.append(f"la z de una I departamental igual a la municipal ({es['z_departamental_si_igual']}) "
                         f"ya no queda entre las dos z: el módulo 7 la usa para separar potencia de efecto")
    if not es["razon_ee"] > 1 or \
            abs(es["ee_departamental"] / es["ee_municipal"] - es["razon_ee"]) > 1e-7:
        problemas.append(f"bajo la nula la I departamental ya no varía más que la municipal "
                         f"(razón {es['razon_ee']}), y la prosa dice cuántas veces más")
    # El ejercicio 2: sus intervalos se centran en la media muestral POR
    # CONSTRUCCIÓN, y la lectura dice hacia qué lado caen las réplicas.
    g2, t2 = S["e2"]["solucion"], S["e2"]
    if any(abs((g2[k][0] + g2[k][1]) / 2 - g2["media"]) > 1e-7 for k in ("ic_iid", "ic_bloques")):
        problemas.append("ejercicio 2: algún intervalo ya no está centrado en la media de los municipios, "
                         "y la lectura y la pista dicen que los dos lo están")
    lado2 = "por debajo" if g2["desvio_esperanza"] < 0 else "por encima"
    if n(g2["esperanza_replicas_bloques"]) not in t2["lectura"] or f" {lado2} de la media" not in t2["lectura"] \
            or abs(g2["esperanza_replicas_bloques"] - g2["media"] - g2["desvio_esperanza"]) > 1e-8 \
            or not abs(g2["desvio_esperanza"]) > 10 * g2["emc_esperanza"]:
        problemas.append(f"ejercicio 2: la lectura no dice que la esperanza de las réplicas por departamentos "
                         f"es {n(g2['esperanza_replicas_bloques'])}, {lado2} de la media de los municipios, "
                         f"o ese desvío ya no supera su error de Monte Carlo")
    # El ejercicio 3: su recorrido es sensibilidad, y la lectura da el e.e. jackknife.
    jk3b = S["e3"]["solucion"]["jackknife"]
    if n(jk3b["ee_techo"]) not in S["e3"]["lectura"] or \
            not (jk3b["maximo"]["techo"] - jk3b["minimo"]["techo"]) / 2 < jk3b["ee_techo"]:
        problemas.append("ejercicio 3: la lectura no da el error estándar jackknife del techo, o medio "
                         "recorrido ya no queda por debajo de él")
    print(f"  módulo 4: esperanza de las réplicas por bloques {n(rpg['desvio_esperanza'])} por encima de la "
          f"media · sin un departamento, n_eff de {n(sug['n_eff_min'])} a {n(sug['n_eff_max'])} · e.e. "
          f"jackknife {n(sug['ee_jackknife_n_eff'])} · extremo: {sug['extremo']['departamento']}")

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

    # --- R2 · T2.4 · las tres gráficas nuevas ---------------------------
    #
    # Las cifras de las tres las rehace `audita_cap1.py`. Lo que se vigila
    # aquí son las FRASES que la prosa pone entre ellas, y el cableado de lo
    # que el navegador dibuja. Varias dependen de un Monte Carlo: R ya para
    # si el ruido las pudiera voltear, y aquí se comprueba otra vez sobre lo
    # publicado, porque el JSON puede llegar de otra parte.
    #
    # MÓDULO 1 · la prueba de aleatorización.
    n_m1, k_obs1 = sn["n_muertes"], sn["n_mas_cerca_broad"]
    if not (len(al["hist_n"]) == len(al["hist_frec"]) == len(al["hist_binomial"])
            and sum(al["hist_frec"]) == al["n_recolocaciones"]
            and al["hist_n"] == list(range(al["min_nula_n"], al["max_nula_n"] + 1))):
        problemas.append("módulo 1: el histograma de la nula no trae una barra por recuento, o sus "
                         "barras no suman las recolocaciones que la prosa dice")
    if abs(sum(k * f for k, f in zip(al["hist_n"], al["hist_frec"])) * 100 / n_m1
           / al["n_recolocaciones"] - al["media_nula_pct"]) > 1e-6:
        problemas.append("módulo 1: la media de la nula publicada no es la del histograma que se dibuja")
    if abs(al["max_nula_pct"] - 100 * al["max_nula_n"] / n_m1) > 1e-6 or \
            abs(al["min_nula_pct"] - 100 * al["min_nula_n"] / n_m1) > 1e-6:
        problemas.append("módulo 1: el máximo o el mínimo de la nula en porcentaje no son los de su "
                         "recuento de muertes")
    # «Ninguna llega», «la mayor da», y el p como COTA 1/(B + 1).
    if not (al["n_mayor_o_igual"] == 0 and al["max_nula_n"] < k_obs1
            and abs(al["p_cota"] - 1 / (al["n_recolocaciones"] + 1)) < 1e-12):
        problemas.append("módulo 1: alguna recolocación alcanza al observado, o el valor p ya no es la "
                         "cota 1/(B + 1): la prosa dice «ninguna» y «se da como cota»")
    # «Es la media de la nula» y «las recolocaciones la reproducen».
    if not abs(al["media_nula_pct"] - al["pct_calle_broad"]) < 4 * al["emc_media_pct"]:
        problemas.append(f"módulo 1: las recolocaciones promedian {al['media_nula_pct']} y la parte de calle "
                         f"de Broad St es {al['pct_calle_broad']}: ya no la reproducen dentro de su error")
    i_b1 = sn["bomba_broad"] - 1
    if not (len(al["pct_calle_por_bomba"]) == sn["n_bombas"] == len(al["bombas"])
            and abs(sum(al["pct_calle_por_bomba"]) - 100) < 1e-6
            and al["pct_calle_por_bomba"][i_b1] == al["pct_calle_broad"]
            and al["bombas"][i_b1] == "Broad St"):
        problemas.append("módulo 1: las partes de calle de las bombas no suman la calle entera, o la de "
                         "Broad St no es la que la prosa publica")
    # «Algo más que el reparto ingenuo», y el cociente.
    if not (sn["pct_esperado_uniforme"] < al["pct_calle_broad"]
            and 1 < al["razon_sobre_calle"] < sn["razon_sobre_uniforme"]):
        problemas.append("módulo 1: la parte de calle de Broad St ya no es «algo más» que el reparto "
                         "ingenuo, o el observado deja de superarla")
    # Segunda ronda · el marco del plano. La tabla y el párrafo que la lee:
    # la última fila es el plano entero y trae las cifras del titular; cada
    # razón es el observado entre su parte de calle; al ensanchar el marco la
    # parte de calle baja; y «lo que no cambia es el rechazo» —el dato a más
    # de diez desviaciones típicas también con el marco más estrecho—
    # mientras la razón cambia a más del doble.
    if not (mc1[-1]["margen"] is None and mc1[-1]["pct_calle_broad"] == al["pct_calle_broad"]
            and mc1[-1]["razon_sobre_calle"] == al["razon_sobre_calle"]
            and MARCO_MIN["margen"] == 0 and abs(mc1[-1]["pct_longitud"] - 100) < 1e-9):
        problemas.append("módulo 1: la tabla de marcos no acaba en el plano entero con las cifras del "
                         "titular, o no empieza en el rectángulo de las muertes")
    if any(abs(m["razon_sobre_calle"] - sn["pct_mas_cerca_broad"] / m["pct_calle_broad"]) > 1e-6
           or abs(m["z_binomial"] - (k_obs1 - n_m1 * m["pct_calle_broad"] / 100)
                  / math.sqrt(n_m1 * m["pct_calle_broad"] / 100 * (1 - m["pct_calle_broad"] / 100))) > 1e-6
           for m in mc1):
        problemas.append("módulo 1: en algún marco la razón no es el observado entre su parte de calle, "
                         "o las desviaciones típicas no son las de su binomial")
    if not (all(a_["pct_calle_broad"] > b_["pct_calle_broad"] and a_["pct_longitud"] < b_["pct_longitud"]
                for a_, b_ in zip(mc1, mc1[1:]))
            and 2 * MARCO_MIN["razon_sobre_calle"] < al["razon_sobre_calle"]):
        problemas.append("módulo 1: la parte de calle ya no baja al ensanchar el marco, o la razón ya no "
                         "cambia tanto como para decir que no cabe en una sola cifra")
    if not all(m["z_binomial"] > 10 for m in mc1):
        problemas.append(f"módulo 1: con algún marco el dato queda a menos de diez desviaciones típicas "
                         f"({[round(m['z_binomial'], 1) for m in mc1]}); la prosa dice que el rechazo no "
                         f"cambia con el marco")
    if abs(al["razon_sobre_calle"] - sn["pct_mas_cerca_broad"] / al["pct_calle_broad"]) > 1e-6:
        problemas.append("módulo 1: «veces lo que le tocaría por calle» no es el observado entre la parte "
                         "de calle")
    # «Eso no cambia la conclusión»: el dato tiene que quedar lejísimos.
    if not al["z_observado"] > 10:
        problemas.append(f"módulo 1: el observado queda a {al['z_observado']} desviaciones típicas de la "
                         f"nula; la nota dice que la dependencia entre muertes no cambia la conclusión")
    print(f"  módulo 1: {ent(al['n_recolocaciones'])} recolocaciones sobre {al['n_tramos']} tramos · a Broad St "
          f"le toca el {n(al['pct_calle_broad'])} % de la calle · observado {n(al['razon_sobre_calle'])} "
          f"veces · ninguna de las recolocaciones pasa de {n(al['max_nula_pct'])} %")

    # MÓDULO 3 · la envolvente de permutación.
    nb3 = len(tb["ideam"]["bandas"])
    for serie in ("ideam", "residuos_altitud"):
        fr = env3[serie]
        if [(e["d1"], e["d2"]) for e in fr] != bandas_ref:
            problemas.append(f"módulo 3: la envolvente de {serie} no va sobre las bandas del correlograma")
            continue
        for b, e in zip(tb[serie]["bandas"], fr):
            donde = "encima" if b["I"] > e["hi"] else "debajo" if b["I"] < e["lo"] else "dentro"
            if donde != e["posicion"] or not e["lo"] < b["esperado"] < e["hi"]:
                problemas.append(f"módulo 3: en la banda {b['d1']}-{b['d2']} de {serie}, la posición "
                                 f"publicada ({e['posicion']}) no es la de su I frente a la franja, o la "
                                 f"franja no contiene a E[I]")
            if abs(e["media"] - b["esperado"]) > 4 * e["emc"]:
                problemas.append(f"módulo 3: la envolvente de {serie} en {b['d1']}-{b['d2']} km no está "
                                 f"centrada en la E[I] que el gráfico dibuja como referencia")
    # Lo que la prosa dice de la temperatura: por encima hasta la antepenúltima,
    # UNA por debajo —y por debajo de todas las permutaciones— y la última dentro.
    if _pos_t != ["encima"] * (nb3 - 2) + ["debajo", "dentro"] or N_ENCIMA3 != nb3 - 2:
        problemas.append(f"módulo 3: la temperatura ya no va «por encima … por debajo, dentro» "
                         f"({_pos_t}); la prosa dice que la última banda no se distingue del azar")
    if not B_DEB3["I"] < E_DEB3["min"] < E_DEB3["lo"]:
        problemas.append("módulo 3: la banda negativa ya no queda por debajo de todas las permutaciones")
    if not tb["ideam"]["bandas"][0]["I"] > 3 * env3["ideam"][0]["hi"]:
        problemas.append("módulo 3: la primera banda ya no queda «muy por encima» de su franja")
    # Y de los residuos: como la temperatura al principio, una dentro, y las dos últimas por debajo.
    if _pos_r != ["encima"] * N_ENCIMA3_RES + ["dentro", "debajo", "debajo"] or not N_ENCIMA3_RES < N_ENCIMA3:
        problemas.append(f"módulo 3: los residuos ya no van «por encima, dentro, y las dos últimas por "
                         f"debajo» ({_pos_r}), o no se agotan antes que la temperatura")
    if env3["n_fuera_ideam"] != sum(x != "dentro" for x in _pos_t) or \
            env3["n_fuera_residuos"] != sum(x != "dentro" for x in _pos_r):
        problemas.append("módulo 3: el recuento de bandas fuera de la franja no es el de sus posiciones")
    # La permutación suelta, contra la franja de la temperatura: «en ninguna».
    fuera_perm = sum(not e["lo"] <= b["I"] <= e["hi"]
                     for b, e in zip(tb["permutado"]["bandas"], env3["ideam"]))
    if fuera_perm != 0 or env3["n_fuera_permutado"] != 0:
        problemas.append(f"módulo 3: la permutación suelta se sale de la franja en {fuera_perm} banda(s), "
                         f"y la prosa dice que queda dentro en todas")
    # El gráfico dibuja UNA franja cada vez, y «son casi la misma»: los
    # residuos tienen que leerse igual contra la de la temperatura, y los
    # bordes de las dos no pueden separarse más de un 10 % del ancho.
    if [("encima" if b["I"] > e["hi"] else "debajo" if b["I"] < e["lo"] else "dentro")
            for b, e in zip(tb["residuos_altitud"]["bandas"], env3["ideam"])] != _pos_r:
        problemas.append("módulo 3: los residuos se leen distinto contra la franja de la temperatura que "
                         "contra la suya, y el gráfico dibuja una sola")
    if any(max(abs(a["lo"] - b["lo"]), abs(a["hi"] - b["hi"])) > 0.10 * (a["hi"] - a["lo"])
           for a, b in zip(env3["ideam"], env3["residuos_altitud"])):
        problemas.append("módulo 3: las dos envolventes ya no son «casi la misma»")
    # Segunda ronda · las parejas que el eje deja fuera, la suma por bandas
    # y «no es raro que alguna se salga».
    n_e3 = co["geo"]["n"]
    if not (ma3["posicion"] == "debajo" and ma3["I"] < ma3["lo"] < ma3["hi"]
            and ma3["d1"] == tb["ideam"]["bandas"][-1]["d2"]
            and ma3["n_pares_total"] == n_e3 * (n_e3 - 1) // 2
            and abs(ma3["pct_pares"] - 100 * ma3["n_pares"] / ma3["n_pares_total"]) < 1e-6
            and 2.5 < ma3["d_max"] / ma3["d1"] < 3):
        problemas.append("módulo 3: las parejas de más allá del eje ya no quedan por debajo de su franja, "
                         "su porcentaje no cuadra o el eje ya no tendría que llegar «casi al triple»")
    s_b3 = [s["suma"] for s in su3["bandas"]]
    if not ([(s["d1"], s["d2"], s["n_pares"]) for s in su3["bandas"]]
            == [(b["d1"], b["d2"], b["n_pares"]) for b in tb["ideam"]["bandas"]]
            and sum(s["n_pares"] for s in su3["bandas"]) + ma3["n_pares"] == ma3["n_pares_total"]
            and abs(sum(s_b3) + su3["mas_alla"] + 1) < 1e-7 and abs(su3["total"] + 1) < 1e-7):
        problemas.append("módulo 3: las sumas por banda no van sobre las parejas del correlograma, o no "
                         "reúnen todas las parejas con total -1, y la prosa dice «exactamente»")
    if not (su3["n_bandas_cortas"] == N_ENCIMA3 == I_DEB3
            and abs(su3["cortas"] - sum(s_b3[:N_ENCIMA3])) < 1e-7
            and abs(su3["largas"] + su3["cortas"] + 1) < 1e-7):
        problemas.append("módulo 3: «las parejas a menos de … km» no son las bandas que quedan por encima, "
                         "o las demás no suman lo que falta hasta -1")
    if not (all(x > 0 for x in s_b3[:N_ENCIMA3]) and su3["cortas"] > 5
            and all(x < 0 for x in s_b3[N_ENCIMA3:]) and su3["mas_alla"] < 0
            and s_b3[I_DEB3] < 0.5 * su3["largas"]):
        problemas.append("módulo 3: las bandas cortas ya no suman en positivo y las largas en negativo, o "
                         "la banda bajo la franja ya no se lleva la mayor parte: la prosa lo lee así")
    if not env3["pct_alguna_fuera"] - 4 * env3["emc_alguna_fuera_pct"] > 10:
        problemas.append(f"módulo 3: solo en el {env3['pct_alguna_fuera']} % de las permutaciones se sale "
                         f"alguna banda; «no es raro» ya no se sostiene")
    # El nivel y los cuantiles que el pie de la tabla escribe.
    if not (env3["nivel_pct"] == 95 and abs(env3["cuantil_lo_pct"] - (100 - env3["nivel_pct"]) / 2) < 1e-9
            and abs(env3["cuantil_lo_pct"] + env3["cuantil_hi_pct"] - 100) < 1e-9
            and abs(env3["orden_lo"] - (env3["nperm"] + 1) * env3["cuantil_lo_pct"] / 100) < 1e-9
            and env3["orden_lo"] + env3["orden_hi"] == env3["nperm"] + 1):
        problemas.append("módulo 3: el nivel de la envolvente, sus cuantiles o sus estadísticos de orden "
                         "no cuadran entre sí")
    print(f"  módulo 3: envolvente del {env3['nivel_pct']:g} % con {ent(env3['nperm'])} permutaciones · "
          f"temperatura {_pos_t.count('encima')} por encima, {_pos_t.count('debajo')} por debajo, "
          f"{_pos_t.count('dentro')} dentro · residuos {_pos_r.count('encima')}/{_pos_r.count('debajo')}/"
          f"{_pos_r.count('dentro')} · la permutación suelta, {fuera_perm} fuera")

    # MÓDULO 4 · cien intervalos.
    n_ci = ci["n"]
    cub_ing = sum(abs(m) <= s for m, s in zip(ci["media"], ci["semiancho_ingenuo"]))
    cub_exa = sum(abs(m) <= ci["semiancho_exacto"] for m in ci["media"])
    if not (len(ci["media"]) == len(ci["semiancho_ingenuo"]) == n_ci and ci["phi"] == r4["phi"]):
        problemas.append("módulo 4: los intervalos dibujados no son tantos como dice la prosa, o no son "
                         "los del alcance que el módulo destaca")
    if cub_ing != ci["n_cubren_ingenuo"] or cub_exa != ci["n_cubren_exacto"]:
        problemas.append(f"módulo 4: se dibujan {cub_ing} y {cub_exa} intervalos que cubren el cero y la "
                         f"prosa publica {ci['n_cubren_ingenuo']} y {ci['n_cubren_exacto']}")
    # «Una muestra de ella»: el recuento de los cien, compatible con la cobertura.
    if abs(cub_ing / n_ci - r4["cobertura"]) > 3 * math.sqrt(r4["cobertura"] * (1 - r4["cobertura"]) / n_ci):
        problemas.append("módulo 4: el recuento de los intervalos dibujados ya no es compatible con la "
                         "cobertura publicada, y la prosa lo llama una muestra de ella")
    # El error estándar verdadero es el de la fila de phi, y los semianchos cuadran.
    if not (abs(ci["ee_exacto"] - r4["ee_exacto"]) < 1e-9
            and abs(ci["semiancho_exacto"] - ci["z_critico"] * ci["ee_exacto"]) < 1e-8
            and abs(ci["semiancho_ingenuo_medio"] - sum(ci["semiancho_ingenuo"]) / n_ci) < 1e-8
            and abs(ci["razon_semianchos"] - ci["semiancho_exacto"] / ci["semiancho_ingenuo_medio"]) < 1e-7):
        problemas.append("módulo 4: el error estándar verdadero de los intervalos no es el de la rejilla, "
                         "o los semianchos y su cociente no cuadran")
    # «Entonces cubren casi todos» y «el 95 % prometido».
    if not (cub_exa >= 0.9 * n_ci and cub_ing < cub_exa
            and abs(ci["cobertura_exacto"] - (1 - D["inferencia"]["alfa"])) < 4 * ci["emc_cobertura_exacto"]):
        problemas.append("módulo 4: con el error estándar verdadero los intervalos ya no cubren lo "
                         "prometido, y la prosa dice que sí")
    # Segunda ronda · el cociente de semianchos y el factor del recuadro: «no
    # es el mismo, aunque los dos dicen lo mismo». Y el nivel, que sale de R.
    if not (n(ci["razon_semianchos"]) != n(r4["factor"])
            and abs(ci["razon_semianchos"] / r4["factor"] - 1) < 0.05):
        problemas.append(f"módulo 4: el cociente de semianchos ({ci['razon_semianchos']}) y el factor del "
                         f"recuadro ({r4['factor']}) ya son la misma cifra o ya no se parecen: la prosa "
                         f"dice que son distintos y dicen lo mismo")
    if abs(D["inferencia"]["nivel_pct"] - 100 * (1 - D["inferencia"]["alfa"])) > 1e-9:
        problemas.append("módulo 4: el nivel de los intervalos que la prosa escribe no es el de alfa")
    # «A un lado y a otro del cero, sin irse hacia ninguno» y «mucho más corto».
    pos_ci = sum(m > 0 for m in ci["media"])
    media_ci = sum(ci["media"]) / n_ci
    sd_ci = math.sqrt(sum((m - media_ci) ** 2 for m in ci["media"]) / (n_ci - 1))
    if abs(pos_ci - n_ci / 2) > 1.5 * math.sqrt(n_ci) or not sd_ci > 2 * max(ci["semiancho_ingenuo"]):
        problemas.append(f"módulo 4: {pos_ci} de las medias dibujadas son positivas, o los segmentos ya "
                         f"no son más cortos que lo que se separan las medias: la prosa lee las dos cosas")
    print(f"  módulo 4: {n_ci} intervalos de phi = {ci['phi']} · cubren {cub_ing} con el e.e. ingenuo y "
          f"{cub_exa} con el verdadero · {pos_ci} medias positivas · semiancho ×{n(ci['razon_semianchos'])}")

    # «DESCRIBIR EL MAPA» (2026-11-02). Cada mapa que el documento usa trae
    # su descripción —los que cambian con un control, una por estado—, y lo
    # que esas frases afirman de la forma se comprueba contra el dato.
    problemas += revisa_textos(marcado, GEOMAPAS_JS + SIMULADORES_JS, DESCRIPCIONES)
    problemas += guardas_de_las_descripciones()
    # R2 · T2.2: lo que las gráficas y los mapas afirman, contra el dato.
    problemas += guardas_de_t22(PLANTILLA.read_text(encoding="utf-8"), marcado)
    if problemas:
        for p in problemas:
            print(f"  MAL  {p}")
        return 1
    print("\n  Ensamblado limpio.\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
