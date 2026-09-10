#!/usr/bin/env python3
"""
ensambla_taller2.py — construye el Taller 2 (capítulo 4) · C5a

Material de Estadística Espacial 2026-II (20929). Ver PLAN_Taller_2_Cap_4.md.

C5a trae el esqueleto y los módulos 1 a 3: las instrucciones con el
buscador de variante, T1 y T2. C5b añadirá T3, T4, T5 y las dos rúbricas;
C6, el banco de 36 preguntas y las 12 afirmaciones falsas. Cada paso deja
un HTML que ABRE Y FUNCIONA: la navegación declara solo los módulos que
existen, así que el taller a medio construir se puede leer entero sin
botones que lleven a un panel en blanco.

LO QUE ESTE ARCHIVO NO PUEDE ESCRIBIR, Y ES LA REGLA QUE MANDA.

Ninguna cifra a mano (D10), como en los capítulos. Pero además: **ninguna
respuesta**. El JSON entero viaja dentro del HTML —el buscador lo
necesita— así que todo lo que se interpole aquí es legible con «ver
código fuente». Lo que se publica es el enunciado y los datos; ni los dos
p-valores de T1, ni el régimen de ningún patrón de T2 están en ninguna
parte de este archivo.

Y por eso el enunciado no publica el recorrido de ninguna cifra medida.
El plan cita en T1(a) que la fracción de caja fuera va del 32,8 % al
61,7 % según la localidad: eso es una horquilla que estrecha la respuesta
del estudiante y se queda en el plan.

CÓMO SE INDIVIDUALIZA, y por qué el navegador no calcula nada.

El estudiante escribe su documento y el componente busca su fila en la
tabla de 1000 variantes que precalculó R. Se guarda en `localStorage`
porque **los módulos se cargan de uno en uno**: `loadModule()` vacía
`mainContent` en cada salto, así que la variante tiene que sobrevivir al
cambio de módulo o los mapas de T2 no sabrían qué trío pintar.

EL ANCLAJE DEL §5.2 VIVE AQUÍ, y nace de un fallo real: al calificar el
Taller 1 el 2026-09-03, tres estudiantes de doce habían resuelto una
variante ajena de punta a punta —tecleando 102 en vez de 480, 181, 103— y
el dígito de verificación no lo atrapó, porque le cuadra a quien resolvió
otra variante entera. La causa raíz era que el estudiante NUNCA VEÍA SU
PROPIO DOCUMENTO: escribía tres dígitos y recibía un municipio. Aquí el
buscador pide el documento COMPLETO —por debajo de seis dígitos no
resuelve nada, y lo dice— y lo imprime en pantalla TAL COMO SE TECLEÓ,
dentro de la línea que el enunciado obliga a copiar literal en la
portada. Quien teclee mal verá su propio documento mal escrito en la
portada que él mismo copia. Eso sí se ve.

LOS MAPAS SE REGISTRAN COMO FUNCIÓN, no como literal, y eso tiene un
coste que hay que decir: `audita_texto_base.geomapas()` solo sabe mirar
dentro de un `.geomapa` cuya fuente sea un literal, así que esa familia
del auditor de prosa se queda sin nada que comprobar aquí. No es un
descuido —el mapa TIENE que ser dinámico, depende del documento— y no
queda sin cubrir: `audita_taller2.py` audita los mapas contra el JSON.

EL ORDEN DE LOS TRES MAPAS DE T2 NO ES EL DE LAS TRES CURVAS, y la
permutación está en `ORDEN_MAPAS`, unas líneas más abajo. Medido antes de
escribir: en el JSON, `trios[i][k]` y `MAPAS_T2.trios[i][k]` son el mismo
patrón para las tres posiciones de los doce tríos, así que enseñarlos en
el mismo orden convertía T2(a) en «A con 1, B con 2, C con 3» y todo el
mundo acertaba sin mirar. Coste declarado: quien lea el código fuente
puede deshacer la permutación. No es evitable —las coordenadas viajan en
el CSV que el estudiante descarga, así que el emparejamiento SIEMPRE es
recalculable— y por eso T2(a) dice en el enunciado que un emparejamiento
sin argumento no puntúa: lo que se califica es la justificación.

Uso:  python3 precalculo/ensambla_taller2.py
      (desde la carpeta `Estadistica espacial/`)
"""
from __future__ import annotations

import json
import os
import pathlib
import re
import sys

RAIZ = pathlib.Path(__file__).resolve().parent.parent
SALIDAS = RAIZ / "precalculo" / "salidas"


def _ruta(var: str, defecto: pathlib.Path) -> pathlib.Path:
    """La ruta publicada, o la copia que apunte la variable de entorno.

    Mismo convenio que `ensambla_taller1.py` y que los ensambladores de
    capítulo: es lo que permite que un arnés de inyección construya desde
    JSON envenenados sin escribir jamás sobre lo publicado.
    """
    p = pathlib.Path(os.environ.get(var) or defecto)
    if var.endswith("DESTINO"):
        return p
    if not p.exists():
        sys.exit(f"PARADO: falta {p}")
    return p


PLANTILLA = _ruta("TALLER2_PLANTILLA", RAIZ / "plantilla" / "plantilla-capitulo.html")
DESTINO = _ruta("TALLER2_DESTINO", RAIZ / "Htmls_Espacial" / "taller-2-cap-4.html")

D = json.loads(_ruta("TALLER2_DATOS", SALIDAS / "taller2_datos.json")
               .read_text(encoding="utf-8"))
M = json.loads(_ruta("TALLER2_MAPAS", SALIDAS / "taller2_mapas.json")
               .read_text(encoding="utf-8"))

meta = D["meta"]

# La permutación con la que se enseñan los tres mapas de cada trío frente
# a sus tres parejas de curvas. Una fila por trío, y ninguna es la
# identidad: ver la cabecera de este archivo. Se comprueba en main().
ORDEN_MAPAS = ((1, 2, 0), (2, 0, 1), (0, 2, 1), (1, 0, 2),
               (2, 1, 0), (1, 2, 0), (2, 0, 1), (0, 2, 1),
               (2, 1, 0), (1, 0, 2), (1, 2, 0), (2, 0, 1))


def n(x, d=5):
    """Cinco decimales, la regla del material desde el 2026-08-03."""
    return f"{float(x):.{d}f}"


def n5(x):
    return n(x, 5)


def ent(x):
    """Entero con separador de millar fino (U+202F), fuera de fórmulas."""
    return f"{int(round(float(x))):,}".replace(",", " ")


def ent_mate(x):
    """El mismo entero para DENTRO de una fórmula: KaTeX no mide el U+202F."""
    return f"{int(round(float(x))):,}".replace(",", r"\,")


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
            <h3 class="font-bold text-gray-800 text-sm" style="margin:0;">Qué se evalúa aquí</h3>
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

    En un taller los bloques son CÓDIGO DE ARRANQUE, no resultados: no
    llevan línea `#>`. Es deliberado y no una omisión —anunciar la salida
    sería adelantar la respuesta— y encaja con `verifica_bloques.py`, que
    contrasta las cifras anunciadas contra la ejecución real: sin cifras
    anunciadas no hay nada que contrastar, y el estudiante no recibe un
    número que pueda copiar sin ejecutar.
    """
    return f"""      <div class="code-tabs">
        <div class="code-tabs-nav" role="tablist" aria-label="{etiqueta}">
          <button class="code-tab-btn active" data-lang="r" role="tab" aria-selected="true">R</button>
          <button class="code-tab-btn" data-lang="python" role="tab" aria-selected="false">Python</button>
        </div>
        <div class="code-tab-panel" data-lang="r">
          <pre><code class="language-r arranque">{r_code}</code></pre>
        </div>
        <div class="code-tab-panel" data-lang="python" hidden>
          <pre><code class="language-python arranque">{py_code}</code></pre>
        </div>
      </div>
"""


def variante(nota=""):
    """La tira que resuelve el documento, repetida en cada tarea.

    Va en TODOS los módulos a propósito: quien está en T2 no debería
    tener que volver al módulo 1 para recordar qué trío le tocó. El
    componente es el mismo —se registra una vez— y se rellena solo con lo
    que haya guardado el navegador.
    """
    return f"""      <div class="simulador" data-simulador="taller2-variante">
        <h4><i class="fas fa-fingerprint" aria-hidden="true"></i> Tu variante</h4>
        <p class="simulador-intro">Escribe tu número de documento <strong>completo</strong>,
          no los tres últimos dígitos. {nota}</p>
        <div class="simulador-controles"></div>
        <div class="simulador-lectura"></div>
      </div>
"""


def tarea(num, peso, titulo, enunciado, literales, pista):
    """Un enunciado de tarea, con pista y SIN panel de solución.

    El componente `.ejercicio-guiado` de la plantilla trae dos botones,
    Pista y Solución. Aquí se usa solo el primero: la decisión de Javier
    en el Taller 1 fue taller sin solucionario, y el panel de solución no
    se deja vacío —se omite—, porque un botón que abre una caja vacía se
    lee como un error del material y no como una decisión.
    """
    items = "\n".join(f"          <li>{x}</li>" for x in literales)
    return f"""      <div class="ejercicio-guiado">
        <p class="ejercicio-enunciado"><span class="ejercicio-numero">T{num}.</span><strong>{titulo}
          </strong> <span class="badge-peso">{peso}&nbsp;%</span><br>{enunciado}</p>
        <ol class="lista-literales" type="a">
{items}
        </ol>
        <div class="ejercicio-acciones">
          <button type="button" class="ejercicio-boton" aria-expanded="false" aria-controls="t{num}-pista">
            <i class="fas fa-lightbulb" aria-hidden="true"></i> Pista
            <i class="fas fa-chevron-down" aria-hidden="true"></i>
          </button>
        </div>
        <div class="ejercicio-panel pista" id="t{num}-pista" hidden>
          <p style="margin:0;">{pista}</p>
        </div>
      </div>
"""


# =====================================================================
# MÓDULO 1 · Cómo se trabaja este taller
# =====================================================================
# Las reglas de IA van AQUÍ y por escrito, con la misma decisión que en el
# Taller 1 (Javier, 2026-08-13): uso libre sin pedir permiso, declaración
# obligatoria de qué se consultó y qué se verificó, y aviso explícito de
# la recalificación en la defensa. Lo que cambia es el peso: allí la
# defensa era el 40 % y confirmaba; aquí es el 60 % y ES el instrumento.
MOD1 = cabecera(
    1, "Cómo se trabaja este taller", "Read this first",
    "Nada. Este módulo no se califica: fija las reglas, resuelve tu variante "
    "y dice cómo se califica todo lo demás.") + f"""
      <p>Este taller cubre el <strong>capítulo 4 entero</strong> —los once módulos de contenido—
        y, por una sola tarea, los tres primeros del capítulo 5. No se evalúa que sepas escribir
        código ni que recuerdes fórmulas: se evalúa que <strong>uses un concepto para
        decidir</strong>, que digas qué <em>no</em> significa una cifra, y que reconozcas un
        procedimiento equivocado cuyo resultado se ve perfectamente razonable. Son tres cosas
        distintas y las tres se califican por separado.</p>

      <div class="warning">
        <p style="margin-bottom:0;"><strong>Lo primero que conviene saber: aquí la defensa pesa
          más que el escrito.</strong> El escrito vale el <strong>40&nbsp;%</strong> y la
          sustentación oral el <strong>60&nbsp;%</strong>. En el Taller 1 era al revés. El
          escrito no es el entregable: es <em>la evidencia que vas a defender</em>, y está
          diseñado para que cada tarea produzca una <strong>decisión</strong> que puedas
          sostener, no una respuesta que puedas entregar.</p>
      </div>

      <div class="definition">
        <h3>Sobre usar inteligencia artificial: úsala</h3>
        <p>No hace falta pedir permiso ni justificarse. Puedes consultar cualquier modelo, para
          cualquier parte, tantas veces como quieras. El taller está diseñado dando por hecho que
          lo vas a hacer, y por eso <strong>ninguna tarea se contesta con lo que un modelo sabe
          sin tus datos</strong>: cada quien trabaja sobre una localidad de Bogotá y unos patrones
          distintos.</p>
        <p>Dos condiciones, y las dos son parte de la nota:</p>
        <ol class="lista-literales" type="1">
          <li><strong>La bitácora es obligatoria y va en la portada.</strong> Media página: qué
            consultaste con IA, qué te respondió y <em>cómo verificaste</em> si era cierto. Una
            frase por consulta basta. Es el artefacto sobre el que se califica la dimensión de
            comunicación y honestidad, y <strong>sin ella la entrega está incompleta</strong>. Se
            califica la precisión de la declaración, no la cantidad de consultas: «usé IA para
            todo y comprobé las cifras contra mi propia salida» puntúa; no declarar nada, no.</li>
          <li><strong>Cualquier decisión que entregues tienes que poder sostenerla en la
            sustentación.</strong> Si no puedes explicar por qué elegiste lo que elegiste, esa
            tarea <strong>se recalifica</strong>. No es una amenaza: es lo que hace que valga la
            pena entender lo que entregas, y es la razón por la que la defensa pesa el
            60&nbsp;%.</li>
        </ol>
        <p style="margin-bottom:0;">Dicho de otro modo: la IA te puede ahorrar el trabajo
          mecánico. No te puede ahorrar el criterio, porque el criterio es lo único que se
          evalúa.</p>
      </div>

      <div class="note">
        <p style="margin-bottom:0;"><strong>El material que necesitas.</strong> Todo lo que se
          pide está publicado, y conviene tenerlo abierto al lado: el
          <a href="capitulo-4-patrones-puntuales.html">capítulo 4 · Patrones puntuales:
          descripción, CSR y funciones de resumen</a> entero, y del
          <a href="capitulo-5-intensidad-nucleos.html">capítulo 5 · Intensidad y estimación por
          núcleos</a> solo sus tres primeros módulos, que son los que necesita T5.</p>
      </div>

      <h3>Las cinco tareas, y qué dato usa cada una</h3>

      <p>El escrito son <strong>cinco tareas</strong> que valen <strong>8&nbsp;% cada una</strong>.
        Cuatro de las cinco son de refutación: no te piden producir un resultado, te piden decidir
        si un resultado que ya está sobre la mesa se sostiene. Cada una usa una parte distinta de
        tu variante, y por eso resolver la variante es lo primero:</p>

      <table>
        <caption>Qué tarea usa qué parte de tu variante</caption>
        <thead>
          <tr><th scope="col">Tarea</th><th scope="col">De qué va</th>
              <th scope="col">Qué dato tuyo usa</th></tr>
        </thead>
        <tbody>
          <tr><th scope="row">T1</th><td>La ventana que no declaraste</td>
              <td>tu <strong>localidad</strong></td></tr>
          <tr><th scope="row">T2</th><td>El régimen que las dos funciones no ven igual</td>
              <td>tu <strong>trío</strong> de patrones</td></tr>
          <tr><th scope="row">T3</th><td>Dónde está la estructura</td>
              <td>tu <strong>patrón</strong> y tu localidad</td></tr>
          <tr><th scope="row">T4</th><td>El borde y la banda</td>
              <td>tu <strong>envolvente</strong> y tu localidad de <strong>contraste</strong></td></tr>
          <tr><th scope="row">T5</th><td>El mismo problema con otro mando</td>
              <td>tu <strong>localidad</strong> otra vez</td></tr>
        </tbody>
      </table>

      <div class="note">
        <p style="margin-bottom:0;"><strong>T1 y T5 son la misma decisión con dos nombres, y eso
          es deliberado.</strong> En T1 eliges un tamaño de cuadrante y en T5 un ancho de banda.
          T5 te va a pedir que compares las dos elecciones —las tuyas, no las de nadie— así que
          <strong>guarda lo que decidas en T1</strong>: lo vas a necesitar tres tareas más
          adelante.</p>
      </div>

      <h3>Cómo se entrega, y cómo se sustenta</h3>

      <div class="note">
        <p><strong>El escrito: un solo PDF, el martes 6 de octubre de 2026.</strong> Se entrega
          por <strong>Brightspace</strong>, con el nombre
          <code>T2_Apellido_TuDocumento.pdf</code>. No se aceptan entregas tarde.</p>
        <p><strong>La portada lleva dos cosas obligatorias</strong>, y sin cualquiera de las dos
          la entrega está incompleta: la <strong>línea de identificación</strong> que te da el
          buscador de aquí abajo, copiada <em>literal</em>, y la <strong>bitácora</strong> de
          media página.</p>
        <p style="margin-bottom:0;"><strong>La sustentación: jueves 8 de octubre, en clase, una
          sola sesión.</strong> Son <strong>siete minutos</strong> por persona, repartidos en tres
          bloques: <strong>2 min</strong> defendiendo <em>una</em> decisión de tu escrito, que
          elige el profesor después de haberlo leído (30&nbsp;% de la defensa);
          <strong>3 min</strong> con <strong>tres preguntas</strong> de un banco publicado con
          este taller (45&nbsp;%); y <strong>2 min</strong> de refutación en vivo, donde se te lee
          una afirmación falsa sobre el capítulo y dices por qué lo es (25&nbsp;%). El banco y las
          dos rúbricas —la del escrito y la de la defensa— se publican con el enunciado.</p>
      </div>

      <div class="warning">
        <p style="margin-bottom:0;"><strong>En una clase de la semana del 28 de septiembre traes
          tres cifras.</strong> Tu localidad, su <em>n</em> y su λ, en voz alta, y nada más. No se
          califica y no hay que entregar nada: es un control para atrapar a tiempo a quien esté
          resolviendo una variante que no es la suya. Si eso pasa y se descubre el 6 de octubre,
          ya no hay nada que hacer; si se descubre esa semana, quedan días de sobra.</p>
      </div>

      <div class="note">
        <p><strong>Los datos que necesitas.</strong> Son tres archivos, y son exactamente los
          mismos con los que se construyó este taller: no están recortados ni simplificados.
          Descárgalos a una carpeta llamada <code>datos/</code> <strong>al lado de tu
          script</strong>. Los bloques de código de las tareas están escritos con esas rutas, así
          que corren tal cual y no tienes que tocar ninguna.</p>
        <ul class="lista-literales">
          <li><a href="../entrega/datos/taller2_sedes.gpkg" download target="_blank" rel="noopener">
            descargar <code>taller2_sedes.gpkg</code></a> — las sedes educativas de Bogotá con sus
            atributos. De aquí salen <strong>las tuyas</strong>, y la regla de cuáles son las
            tuyas es <strong>geométrica</strong>: las que caen dentro del polígono de tu
            localidad. Es el archivo de <strong>T1</strong> y de <strong>T5</strong>.</li>
          <li><a href="../entrega/datos/taller2_localidades.gpkg" download target="_blank" rel="noopener">
            descargar <code>taller2_localidades.gpkg</code></a> — las localidades del Distrito,
            todas, con su geometría completa. La tuya está aquí, y también la de
            <strong>contraste</strong> que necesita <strong>T4</strong>.</li>
          <li><a href="../entrega/datos/taller2_patrones.csv" download target="_blank" rel="noopener">
            descargar <code>taller2_patrones.csv</code></a> — los patrones generados, con un
            identificador y dos columnas de coordenadas sobre la ventana unidad. Es el dato de
            <strong>T2</strong> y de <strong>T3</strong>. El identificador no dice nada de lo que
            se te pide clasificar: eso es la respuesta.</li>
        </ul>
        <p style="margin-bottom:0;">Los dos GeoPackage se abren con <code>st_read()</code> en R o
          con <code>geopandas.read_file()</code> en Python, y llegan ya en
          <strong>EPSG:9377</strong> —coordenadas en metros—, así que no hay que reproyectar nada.
          Son datos de terceros que se redistribuyen <strong>con atribución</strong>: las sedes
          educativas y los límites de localidad vienen de los datos abiertos del
          <strong>Distrito</strong>, y su procedencia completa está en el capítulo 4.</p>
      </div>

      <h3>Resuelve tu variante</h3>

      <p>Los datos de las cinco tareas dependen de ella, así que si te equivocas aquí te
        equivocas en todo lo demás. Y esto no es una advertencia teórica: <strong>en el Taller 1,
        tres de doce resolvieron una variante ajena</strong>, cada uno de forma perfectamente
        coherente de principio a fin, y no se supo hasta calificar. Por eso ahora el buscador te
        pide el documento <strong>completo</strong> y te lo devuelve escrito en pantalla: lo que
        tienes que copiar en la portada incluye <em>tu propio número tal como lo tecleaste</em>,
        de modo que un dedo equivocado se ve antes de entregar y no después.</p>

{variante("Se queda guardada en este navegador, así que aparece resuelta en cada tarea.")}
      <div class="warning">
        <p style="margin-bottom:0;"><strong>El <em>n</em> y la λ que te salen arriba son tu dígito
          de verificación.</strong> Cuando construyas tu patrón en T1, el número de sedes tiene
          que dar exactamente ese <em>n</em>. Si no coincide, seleccionaste otras sedes —o otra
          localidad— y todo lo que construyas encima estará mal <em>sin que nada te avise</em>.
          Comprueba eso antes de escribir una sola línea de informe.</p>
      </div>

      <div class="note">
        <p style="margin-bottom:0;"><strong>Qué pesa cada cosa.</strong> El escrito vale el
          40&nbsp;% y la sustentación el 60&nbsp;%. Dentro del escrito, las cinco tareas valen
          8&nbsp;% cada una. La rúbrica del escrito —con sus cinco dimensiones y qué distingue el
          nivel alto en cada una— y la rúbrica de la defensa están en el último módulo, y conviene
          leerlas <em>antes</em> de escribir, no después.</p>
      </div>
""" + CIERRE


# =====================================================================
# MÓDULO 2 · T1 · La ventana que no declaraste
# =====================================================================
# El enunciado NO dice cuál de las dos ventanas es la correcta, ni publica
# ninguno de los dos p-valores: los dos los produce el estudiante
# ejecutando el código que se le da. Tampoco publica el recorrido medido
# de la fracción de caja fuera —del 32,8 % al 61,7 %— porque eso estrecha
# la respuesta de (a) a una horquilla de un factor dos.
#
# LA CAJA ES LA DEL POLÍGONO, NO LA DE LOS PUNTOS, y la diferencia no es
# de estilo. Medido el 2026-09-09 sobre las dieciséis: con la caja del
# polígono vuelcan Antonio Nariño, Rafael Uribe y Barrios Unidos —que es
# la tabla M-2 del plan, dígito a dígito, incluidos el 0,0106 de Barrios
# Unidos y el 0,0605 de Los Mártires—; con la caja de los puntos vuelcan
# Antonio Nariño, Rafael Uribe y LOS MÁRTIRES. Es exactamente la forma de
# M-6: el conjunto que vuelca cambia con la convención. Ver §0 del plan.
MOD2 = cabecera(
    2, "La ventana que no declaraste", "T1 · The undeclared window",
    "Producir un defecto, nombrarlo y decidir con una cifra propia si un "
    "p-valor se puede leer. Vale el 8 % del taller.") + variante() + f"""
      <p>Tu localidad tiene un contorno, y ese contorno <strong>forma parte del estimador</strong>:
        no es el fondo del mapa, es el denominador. Esta tarea empieza construyendo el mismo
        patrón puntual dos veces, con dos ventanas distintas, y corriendo el mismo contraste sobre
        los dos. <strong>Nadie te va a decir cuál de las dos está mal.</strong></p>

      <div class="geomapa" data-geomapa="taller2-localidad"></div>

      <div class="definition">
        <h3>Lo que vas a hacer, en orden</h3>
        <p>Primero seleccionas <strong>tus</strong> sedes: las que caen dentro del polígono de tu
          localidad. La regla es geométrica y no de atributo, y eso importa —hay sedes cuyo código
          de localidad dice una cosa y cuya coordenada dice otra—. El <em>n</em> que te dio el
          buscador es el geométrico: si el tuyo no cuadra, para y revisa antes de seguir.</p>
        <p style="margin-bottom:0;">Después construyes el <code>ppp</code> <strong>dos
          veces</strong>, con los mismos puntos y dos ventanas: el rectángulo que encierra a tu
          localidad y el polígono de tu localidad. Sobre cada uno corres un test de cuadrantes con
          una rejilla de <strong>{meta['rejilla_t1']}&nbsp;×&nbsp;{meta['rejilla_t1']}</strong>.
          Son dos llamadas a la misma función y difieren en un argumento.</p>
      </div>

{tabs('Las dos ventanas, y los dos contrastes',
      '''library(sf)
library(spatstat.geom)
library(spatstat.explore)

# Los dos datos que te dio el buscador. El nombre va EXACTO y sin
# tildes ("Antonio Narino", "Los Martires", "Usaquen"...), y el n esta
# aqui para que el guion PARE si te equivocas de localidad, en vez de
# calcular tranquilamente la de otra persona.
MI_LOCALIDAD &lt;- ""    # rellena esto
MI_N         &lt;- 0     # y esto

loc &lt;- st_read("datos/taller2_localidades.gpkg", quiet = TRUE)
sed &lt;- st_read("datos/taller2_sedes.gpkg",       quiet = TRUE)

mia &lt;- loc[loc$localidad == MI_LOCALIDAD, ]
stopifnot(nrow(mia) == 1)          # si para aqui, el nombre no es el tuyo
xy  &lt;- st_coordinates(sed)

# LAS DOS VENTANAS. La caja es el rectangulo que encierra a tu localidad.
bb     &lt;- st_bbox(mia)
w_caja &lt;- owin(xrange = c(bb[["xmin"]], bb[["xmax"]]),
               yrange = c(bb[["ymin"]], bb[["ymax"]]))
w_poly &lt;- as.owin(st_union(mia))

# ppp() DESCARTA lo que cae fuera de la ventana y sigue, con un aviso que
# nadie lee. Aqui eso es lo que selecciona TUS sedes.
p_poly &lt;- ppp(xy[, 1], xy[, 2], window = w_poly)
p_caja &lt;- ppp(p_poly$x, p_poly$y, window = w_caja)

stopifnot(npoints(p_poly) == MI_N)   # tu digito de verificacion
npoints(p_caja) == npoints(p_poly)   # los mismos puntos, otra ventana

# Las dos areas en km2 y las dos intensidades en sedes por km2
c(caja = area.owin(w_caja), poligono = area.owin(w_poly)) / 1e6
c(caja = intensity(p_caja), poligono = intensity(p_poly)) * 1e6

# Los dos contrastes
quadrat.test(p_caja, nx = 5, ny = 5)
quadrat.test(p_poly, nx = 5, ny = 5)

# Y el supuesto, celda a celda: las esperadas del contraste bueno.
# tile.areas() da el area de cada cuadrante YA RECORTADO por la ventana.
ar  &lt;- tile.areas(as.tess(quadratcount(p_poly, nx = 5, ny = 5)))
esp &lt;- npoints(p_poly) * ar / sum(ar)
c(celdas = length(esp), bajas = sum(esp &lt; 5))''',
      '''import geopandas as gpd, numpy as np
from shapely.geometry import box
from scipy.stats import chi2

MI_LOCALIDAD = ""    # el nombre EXACTO del buscador, sin tildes
MI_N = 0             # y tu n, para que esto PARE si te equivocas

loc = gpd.read_file("datos/taller2_localidades.gpkg")
sed = gpd.read_file("datos/taller2_sedes.gpkg")

filas = loc[loc.localidad == MI_LOCALIDAD]
assert len(filas) == 1, "ese nombre no esta en el archivo: revisa el buscador"
mia = filas.geometry.union_all()
mias = sed[sed.geometry.covered_by(mia)]
xy = np.c_[mias.geometry.x, mias.geometry.y]
assert len(xy) == MI_N, "no son tus sedes: revisa tu variante"

# El binado de quadratcount() es el de cut(): (a, b], con el mas bajo
# cerrado por los dos lados. Reproducirlo importa (modulo 5 del cap. 4).
def celda(v, lo, hi, k):
    b = np.linspace(lo, hi, k + 1)
    return np.clip(np.searchsorted(b, v, side="left") - 1, 0, k - 1)

def cuadrantes(pts, poly, k=5, caja=False):
    x0, y0, x1, y1 = poly.bounds       # LA MISMA rejilla en los dos casos
    ix = celda(pts[:, 0], x0, x1, k); iy = celda(pts[:, 1], y0, y1, k)
    obs = np.zeros((k, k), int); np.add.at(obs, (ix, iy), 1)
    bx = np.linspace(x0, x1, k + 1); by = np.linspace(y0, y1, k + 1)
    if caja:                           # la ventana es el rectangulo entero
        ar = np.full((k, k), (x1 - x0) * (y1 - y0) / k ** 2)
    else:                              # la ventana es el poligono
        ar = np.array([[poly.intersection(box(bx[i], by[j], bx[i+1], by[j+1])).area
                        for j in range(k)] for i in range(k)])
    viva = ar &gt; 0
    esp = len(pts) * ar[viva] / ar[viva].sum()
    x2 = float(((obs[viva] - esp) ** 2 / esp).sum()); gl = esp.size - 1
    # DOS COLAS, que es el defecto de spatstat::quadrat.test y lo que
    # corre tu R. La cola superior sola da otro p-valor, y sobre estos
    # datos llega a cambiar el veredicto: el convenio no es un decimal.
    sup = chi2.sf(x2, gl)
    return x2, gl, 2 * min(sup, 1 - sup), esp

cuadrantes(xy, mia, caja=True)[:3]
cuadrantes(xy, mia, caja=False)[:3]''')}

      <div class="warning">
        <p style="margin-bottom:0;"><strong>Si corres el bloque de Python, lee el comentario de
          las dos colas.</strong> <code>quadrat.test()</code> de <code>spatstat</code> es de dos
          colas por defecto y <code>1 - chi2.cdf()</code> es solo la superior. Sobre estos datos
          el mismo χ² con los mismos grados de libertad puede dar dos p-valores muy distintos, y
          <em>no cambia un decimal: cambia qué localidades rechazan</em>. En este taller manda R,
          porque es lo que corre el capítulo 4 en sus cuatro llamadas.</p>
      </div>

""" + tarea(1, 8, "La ventana que no declaraste",
       "Con tus dos ventanas, tus dos contrastes y tus esperadas:",
       ["Da la λ bajo las dos ventanas, en sedes por km², y di qué <strong>fracción de tu "
        "caja cae fuera</strong> del polígono de tu localidad. Con esa fracción delante: "
        "¿de qué es intensidad la cifra de la caja, si no es de tu localidad?",
        "Da los dos χ² y los dos p-valores. <strong>Nombra el síntoma antes de arreglarlo</strong>: "
        "di qué está mal en el procedimiento, no qué habría que hacer en su lugar.",
        "<strong>Antes de leer ningún p-valor</strong>, comprueba el supuesto: cuenta cuántas de "
        "tus celdas tienen esperanza menor que 5 y da el porcentaje. Con <em>esa cifra tuya</em> "
        "decide si tu p-valor se puede leer o no. Si no se puede, busca la rejilla "
        "\\(k \\times k\\) <strong>más fina</strong> —el \\(k\\) más grande— en la que ninguna "
        "celda baje de 5, y di qué veredicto da esa. Si no existe ninguna, dilo y sostenlo: "
        "también es una respuesta.",
        "Un compañero te dice: «a mí también me rechazó con la caja, así que el error no "
        "importa». Refútalo <strong>con su cifra y con la tuya</strong> —pídele las suyas, "
        "porque no todas las localidades se comportan igual—.",
        "¿Por qué este defecto <strong>no</strong> se vería mirando el mapa del patrón?"],
       "Las dos ventanas contienen los mismos puntos, así que lo que cambia no es el patrón: es "
       "el área contra la que lo estás comparando, y con ella lo que el contraste considera "
       "«uniforme». Para (c), fíjate en que bajar el \\(k\\) sube las esperadas y baja la "
       "resolución: hay que elegir, y elegir es la tarea. Y para (e): pregúntate qué parte de "
       "todo esto se dibuja.") + f"""
      <div class="note">
        <p style="margin-bottom:0;"><strong>Dónde está esto en el capítulo.</strong> La ventana
          como parte del estimador es el módulo 1; la intensidad, el 2; el test de cuadrantes y su
          supuesto, el 5; y qué le pasa al veredicto cuando cambias el tamaño de la celda, el 6
          —que es el MAUP otra vez, con otro nombre—. Los cuatro hacen falta aquí, y ninguno de
          los cinco ejercicios guiados del capítulo responde a esta tarea: el que más se le
          acerca compara <em>dos ventanas legítimas</em> sobre Bogotá entera, y aquí lo que se
          compara es una ventana correcta contra un defecto de procedimiento sobre
          <strong>una</strong> localidad.</p>
      </div>
""" + CIERRE


# =====================================================================
# MÓDULO 3 · T2 · El régimen que las dos funciones no ven igual
# =====================================================================
# Los tres mapas van SIN etiquetar y en un orden distinto al de las tres
# parejas de curvas (ORDEN_MAPAS, arriba). El enunciado no dice cuántas
# familias de patrón hay, ni cómo se llaman, ni que en cada trío haya una
# de cada: eso es exactamente lo que la tarea pide decidir.
MOD3 = cabecera(
    3, "El régimen que las dos funciones no ven igual", "T2 · G and F",
    "Leer dos funciones de distancia contra tres dibujos y clasificar "
    "diciendo a qué escala. Vale el 8 % del taller.") + variante() + f"""
      <p>Aquí tienes <strong>tres patrones</strong> generados y sus <strong>tres parejas de curvas
        \\(G\\) y \\(F\\)</strong>. Los mapas se llaman <strong>A</strong>, <strong>B</strong> y
        <strong>C</strong>; las curvas, <strong>Par 1</strong>, <strong>Par 2</strong> y
        <strong>Par 3</strong>. <strong>El orden no coincide</strong>, y emparejarlos es la
        tarea.</p>

      <p>Las tres ventanas son el cuadrado unidad, así que las escalas son comparables entre sí
        sin convertir nada. Bajo cada mapa hay un desplegable con sus coordenadas, listas para
        <code>ppp()</code>; los mismos puntos viajan en el CSV que descargaste, bajo el
        identificador de tu trío.</p>

      <div class="trio-rejilla">
        <div class="geomapa" data-geomapa="taller2-trio-a"></div>
        <div class="geomapa" data-geomapa="taller2-trio-b"></div>
        <div class="geomapa" data-geomapa="taller2-trio-c"></div>
      </div>

      <div class="simulador" data-simulador="taller2-trio-curvas">
        <h4><i class="fas fa-chart-line" aria-hidden="true"></i> Las tres parejas de curvas</h4>
        <p class="simulador-intro">\\(G(r)\\) y \\(F(r)\\) de los tres patrones de tu trío, sobre
          la misma rejilla de \\(r\\). Las tres parejas están en un orden que <strong>no</strong>
          es el de los mapas de arriba.</p>
        <div class="trio-rejilla">
          <div>
            <p class="grafico-titulo">Par 1</p>
            <div class="grafico-wrapper" style="height:230px;">
              <canvas role="img" aria-label="Funciones G y F del primer par de curvas de tu trío"></canvas>
            </div>
          </div>
          <div>
            <p class="grafico-titulo">Par 2</p>
            <div class="grafico-wrapper" style="height:230px;">
              <canvas role="img" aria-label="Funciones G y F del segundo par de curvas de tu trío"></canvas>
            </div>
          </div>
          <div>
            <p class="grafico-titulo">Par 3</p>
            <div class="grafico-wrapper" style="height:230px;">
              <canvas role="img" aria-label="Funciones G y F del tercer par de curvas de tu trío"></canvas>
            </div>
          </div>
        </div>
        <div class="simulador-lectura"></div>
      </div>

      <div class="definition">
        <h3>Lo que tienes delante</h3>
        <p>\\(G(r)\\) es la función de distribución de la distancia de cada punto a su vecino más
          próximo. \\(F(r)\\) es la de la distancia desde una posición cualquiera de la ventana
          hasta el punto más cercano. Las dos crecen de 0 a 1 y las dos se miden en la misma
          \\(r\\); lo que cambia es <strong>desde dónde</strong> se mide, y por eso pueden no
          contar la misma historia sobre el mismo patrón.</p>
        <p style="margin-bottom:0;">El módulo 7 del capítulo 4 las construye las dos y explica qué
          le pasa a cada una cuando el patrón se agrupa y cuando se separa. El módulo 3 es el que
          da los nombres de los regímenes.</p>
      </div>

""" + tarea(2, 8, "El régimen que las dos funciones no ven igual",
       "Sobre tus tres mapas y tus tres parejas de curvas:",
       ["<strong>Empareja</strong> cada pareja de curvas con su mapa: 1 con A, B o C, y así las "
        "tres. La justificación tiene que decir <strong>qué mira cada función</strong> y "
        "apoyarse en un valor de \\(r\\) concreto de tus curvas. Un emparejamiento sin argumento "
        "no puntúa —las coordenadas están publicadas y comprobar el emparejamiento es legítimo, "
        "pero comprobarlo no es responderlo—.",
        "Nombra el <strong>régimen</strong> de cada uno de los tres <strong>y la escala a la que "
        "lo afirmas</strong>: da el \\(r\\) en el que tu curva decide, y di qué pasaría con tu "
        "veredicto si solo miraras \\(r\\) por encima de ese valor.",
        "\\(G\\) y \\(F\\) no tienen por qué decir lo mismo. Mira tus tres: ¿hay alguno donde "
        "discrepen? Si en los tres coinciden, <strong>construye</strong> el caso en que no "
        "coincidirían —descríbelo con precisión suficiente para que otra persona lo pueda "
        "generar— y di qué mira cada una para que eso ocurra."],
       "Ninguna de las tres curvas decide sola: lo que decide es <em>cuándo</em> despega cada una "
       "y cuánto se separan entre sí. Un patrón con huecos grandes y grumos apretados es el que "
       "más las separa, y uno que mantiene a sus puntos a distancia es el que más retrasa una de "
       "las dos. Y cuidado con el eje: decir «agregado» sin decir a qué escala no es una "
       "clasificación, es una impresión.") + f"""
      <div class="note">
        <p style="margin-bottom:0;"><strong>Si quieres rehacer las curvas, aquí está por dónde.</strong>
          No es obligatorio —las curvas publicadas son las buenas—, pero (a) se sostiene mucho
          mejor si además mides algo por tu cuenta. Las coordenadas salen del desplegable de cada
          mapa o del CSV, y el identificador de tu trío te lo dio el buscador.</p>
      </div>

{tabs('Rehacer G y F de un patrón',
      '''library(spatstat.geom)
library(spatstat.explore)

pat &lt;- read.csv("datos/taller2_patrones.csv")

# Los tres del trio 3 son t03a, t03b y t03c: te lo dice el buscador. La
# letra es POSICION dentro del CSV, no familia, y tampoco es la letra del
# mapa: el orden de los mapas de arriba es otro.
MI_TRIO &lt;- ""                         # "t03" si el tuyo es el 3

uno &lt;- subset(pat, patron == paste0(MI_TRIO, "a"))
stopifnot(nrow(uno) &gt; 0)              # si para, ese trio no es el tuyo
p   &lt;- ppp(uno$x, uno$y, window = owin(c(0, 1), c(0, 1)))

plot(Gest(p))
plot(Fest(p))

# Y las dos en la MISMA rejilla de r que las curvas de arriba. Ojo: a
# Fest() no se le puede pedir esa rejilla directamente —exige un paso
# mucho mas fino y para con un error—, asi que se calcula en la suya y se
# interpola. Es lo que hizo el precalculo, y por eso las cifras coinciden.
rg &lt;- seq(0, 0.25, length.out = 51)
aG &lt;- Gest(p); aF &lt;- Fest(p)
G  &lt;- approx(aG$r, aG$km, xout = rg, rule = 2)$y
FF &lt;- approx(aF$r, aF$km, xout = rg, rule = 2)$y
head(data.frame(r = rg, G = G, F = FF), 12)''',
      '''import numpy as np, pandas as pd
from scipy.spatial import cKDTree

MI_TRIO = ""          # "t03" si el tuyo es el 3: lo dice el buscador

pat = pd.read_csv("datos/taller2_patrones.csv")
uno = pat[pat.patron == MI_TRIO + "a"][["x", "y"]].to_numpy()
assert len(uno), "ese trio no es el tuyo"

rg = np.linspace(0, 0.25, 51)

# G: desde cada PUNTO, hasta su vecino mas proximo.
d, _ = cKDTree(uno).query(uno, k=2)
G = np.array([(d[:, 1] &lt;= r).mean() for r in rg])

# F: desde una posicion CUALQUIERA de la ventana, hasta el punto mas
# cercano. Se muestrea la ventana en una rejilla fina.
gx, gy = np.meshgrid(np.linspace(0, 1, 200), np.linspace(0, 1, 200))
sondas = np.c_[gx.ravel(), gy.ravel()]
dv, _ = cKDTree(uno).query(sondas, k=1)
F = np.array([(dv &lt;= r).mean() for r in rg])

# ESTAS DOS NO SON LAS PUBLICADAS, y la diferencia no es un decimal:
# las de arriba llevan la correccion de Kaplan-Meier de spatstat y estas
# van crudas, asi que cerca del borde se quedan cortas. Sirven para ver
# la FORMA; para citar un valor, usa las curvas del enunciado o R.
print(np.c_[rg, G, F][:12])''')}
""" + CIERRE


# =====================================================================
# El ensamblado
# =====================================================================
MODULOS = MOD1 + MOD2 + MOD3

# La navegación declara SOLO los módulos que existen. Con más módulos
# declarados que escritos, `loadModule()` encontraría `template` nulo y
# dejaría el panel en blanco sin un solo error en consola: es el modo de
# fallo más caro de este motor y el que más tardó en encontrarse en el
# Taller 1.
MODULOS_NAV = [
    ("Cómo se trabaja este taller", "8 min"),
    ("T1 · La ventana que no declaraste", "50 min"),
    ("T2 · El régimen que las dos funciones no ven igual", "45 min"),
]

_mods = ",\n".join(
    f'        {{ id: {i + 1}, title: "{t}", duration: "{d}" }}'
    for i, (t, d) in enumerate(MODULOS_NAV))

COURSE_DATA = f"""    const courseData = {{
      modules: [
{_mods}
      ]
    }};

    // El taller entero, tal como sale de precalculo/genera_taller2.R. Nada
    // de lo que hay aquí es una respuesta: son los datos del enunciado.
    const DATOS_T2 = {json.dumps(D, ensure_ascii=False)};
    const MAPAS_T2 = {json.dumps(M, ensure_ascii=False)};

    // El orden en que se enseñan los tres mapas de cada trío, que NO es el
    // de sus tres parejas de curvas. Ver la cabecera de ensambla_taller2.py.
    const ORDEN_MAPAS_T2 = {json.dumps([list(x) for x in ORDEN_MAPAS])};
    const LETRAS_T2 = ['A', 'B', 'C'];

    const n5 = (x, d = 5) => Number(x).toFixed(d);
    const escT2 = s => String(s).replace(/&/g, '&amp;')
      .replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');

    // La variante viva. Sobrevive al cambio de módulo porque loadModule()
    // vacía mainContent en cada salto: sin esto, los mapas de T2 no
    // sabrían qué trío pintar en cuanto el estudiante navegara.
    //
    // Se guarda el documento COMPLETO Y TAL COMO SE TECLEÓ, no la clave de
    // tres dígitos, porque lo que el §5.2 exige devolverle al estudiante
    // es su propio número escrito: si aquí guardáramos solo la clave, la
    // portada volvería a decir «variante 102» y nadie vería el dedazo.
    const T2_LLAVE = 'taller2-documento';
    const T2_MIN_DIGITOS = 6;
    let T2_DOC = '';
    try {{
      T2_DOC = window.localStorage.getItem(T2_LLAVE) || '';
    }} catch (e) {{ /* navegador sin almacenamiento: se pide cada vez */ }}

    const t2Digitos = txt => String(txt).replace(/\\D/g, '');

    function t2Resuelve(txt) {{
      const d = t2Digitos(txt);
      if (d.length < T2_MIN_DIGITOS) return null;
      const clave = d.slice(-3);
      const v = DATOS_T2.variantes.find(x => x.clave === clave);
      if (!v) return null;
      return {{
        documento: String(txt),
        clave: clave,
        v: v,
        loc: DATOS_T2.localidades[v.localidad],
        // El trío y sus mapas se buscan por el MISMO índice: si alguna vez
        // dejaran de ir emparejados, el estudiante emparejaría curvas de
        // un trío contra dibujos de otro y nada se pondría en rojo.
        trio: DATOS_T2.trios[v.trio - 1],
        mapas_trio: MAPAS_T2.trios[v.trio - 1],
        mapa_loc: MAPAS_T2.localidades[v.localidad]
      }};
    }}

    // El mapa que va en la casilla A, B o C (i = 0, 1, 2).
    function t2MapaTrio(i) {{
      const r = t2Resuelve(T2_DOC);
      if (!r || !r.mapas_trio) return null;
      const k = ORDEN_MAPAS_T2[r.v.trio - 1][i];
      return Object.assign({{}}, r.mapas_trio[k], {{
        titulo: 'Mapa ' + LETRAS_T2[i],
        leyenda: 'patrón sin etiquetar, en la ventana unidad'
      }});
    }}
"""

# La tabla de respaldo de un mapa de puntos, y por qué no es un adorno.
#
# El lienzo es un `<canvas>`: los puntos son PÍXELES, no elementos, así que
# inspeccionar el mapa no devuelve una sola coordenada. Sin esta tabla la
# única vía para rehacer las cifras era abrir el código fuente.
#
# Y hay una razón más seria que la comodidad. T2 se responde MIRANDO tres
# dibujos —esa es la tarea—, así que sin tabla la única tarea del taller
# que exige ver algo era, para quien usa lector de pantalla, «Mapa A, 103
# unidades» y nada más. Para quien no ve el mapa, la tabla ES el mapa.
#
# Las coordenadas van ya divididas por `q` —en la ventana unidad, que es
# como las pide `ppp()`— y no en los enteros 0..4096 del JSON: el
# estudiante no tiene por qué deshacer una cuantización que existe para
# ahorrar bytes. Cuatro decimales, que es justo lo que 1/4096 resuelve.
TABLA_PUNTOS_JS = """      tabla: function (d) {
        const filas = [];
        for (let i = 0; i < d.n; i++) {
          filas.push(`<tr><th scope="row">${i + 1}</th>`
            + `<td>${(d.pts[2 * i] / d.q).toFixed(4)}</td>`
            + `<td>${(d.pts[2 * i + 1] / d.q).toFixed(4)}</td></tr>`);
        }
        return `<table><caption>${d.titulo}: las ${d.n} coordenadas, en la `
          + `ventana unidad y listas para <code>ppp()</code>.</caption><thead><tr>`
          + `<th scope="col">Punto</th><th scope="col">x</th>`
          + `<th scope="col">y</th></tr></thead><tbody>${filas.join('')}</tbody></table>`;
      }"""

# Los mapas, como FUNCIÓN y no como literal: dependen del documento. El
# coste para el auditor de prosa está declarado en la cabecera.
#
# `etiqueta` es un GETTER a propósito. El motor arma las opciones con
# `Object.assign({}, spec, …)` en cada repintado, y eso invoca al getter
# entonces: es la única forma de que el texto alternativo diga el nombre de
# la localidad que hay pintada AHORA. Con una cadena fija, quien usa lector
# de pantalla oiría siempre la misma descripción aunque el mapa cambiara, y
# describir mal es peor que no describir.
GEOMAPAS_JS = """    GEOMAPAS['taller2-localidad'] = {
      fuente: function () {
        const r = t2Resuelve(T2_DOC);
        if (!r || !r.mapa_loc) return null;
        return Object.assign({}, r.mapa_loc, { titulo: r.loc.localidad });
      },
      get etiqueta() {
        const r = t2Resuelve(T2_DOC);
        return r ? ('El contorno de ' + r.loc.localidad + ', la ventana de tu patrón. '
          + 'Dentro caen ' + r.loc.n + ' sedes educativas y su área es de '
          + n5(r.loc.area_km2, 2) + ' kilómetros cuadrados.') : 'Mapa sin variante resuelta';
      },
      paleta: 'verde',
      alto: 340,
    };

    GEOMAPAS['taller2-trio-a'] = {
      fuente: function () { return t2MapaTrio(0); },
      paleta: 'verde',
      alto: 260,
""" + TABLA_PUNTOS_JS + """,
    };

    GEOMAPAS['taller2-trio-b'] = {
      fuente: function () { return t2MapaTrio(1); },
      paleta: 'verde',
      alto: 260,
""" + TABLA_PUNTOS_JS + """,
    };

    GEOMAPAS['taller2-trio-c'] = {
      fuente: function () { return t2MapaTrio(2); },
      paleta: 'verde',
      alto: 260,
""" + TABLA_PUNTOS_JS + """,
    };
"""

SIMULADORES_JS = """    // --- El buscador de variante -------------------------------------
    // Ninguna aritmética: la fila viene precalculada en R. El navegador
    // busca, no calcula, y por eso no hay ninguna función de dispersión
    // escrita dos veces en dos lenguajes.
    //
    // Y aquí vive la corrección del §5.2: se pide el documento COMPLETO y
    // se devuelve escrito. Por debajo de seis dígitos NO resuelve, y lo
    // dice: si tecleando tres dígitos saliera un resultado, estaríamos
    // reconstruyendo el mismo agujero por el que en el Taller 1 tres de
    // doce resolvieron la variante de otro.
    SIMULADORES['taller2-variante'] = function (raiz) {
      const controles = raiz.querySelector('.simulador-controles');
      const lectura = raiz.querySelector('.simulador-lectura');
      const idInput = 'doc-' + Math.random().toString(36).slice(2, 8);
      controles.innerHTML = `
        <div class="control-grupo">
          <label for="${idInput}">Tu número de documento, completo</label>
          <input id="${idInput}" type="text" inputmode="numeric" maxlength="20"
                 autocomplete="off" placeholder="1012345678"
                 style="max-width:14rem; font-family:'Fira Code', monospace;
                 font-size:1.05rem; text-align:center; padding:0.4rem;">
        </div>`;
      const campo = controles.querySelector('input');

      function pinta() {
        const r = t2Resuelve(T2_DOC);
        if (!r) {
          const d = t2Digitos(T2_DOC);
          lectura.innerHTML = d.length === 0
            ? `<p style="margin:0;">Escribe tu número de documento <strong>completo</strong>
                 para ver qué te toca.</p>`
            : `<p style="margin:0;">Llevas <strong>${d.length}</strong>
                 ${d.length === 1 ? 'dígito' : 'dígitos'}. Hacen falta al menos
                 <strong>${T2_MIN_DIGITOS}</strong>: este buscador pide el documento
                 <strong>completo</strong>, no los tres últimos dígitos, y esa es la
                 diferencia entre ver tu error y no verlo.</p>`;
          return;
        }
        const v = r.v, L = r.loc;
        // La línea que va LITERAL en la portada. Va en ASCII a propósito:
        // se copia dentro de un documento y un carácter que el compilador
        // no digiera convierte el anclaje en un problema de tipografía.
        const linea = `${escT2(r.documento)} · variante ${v.clave} · ${v.localidad}`
          + ` · n = ${L.n} · lambda = ${n5(L.lambda)} sedes/km2`
          + ` · patron ${String(v.propio).padStart(2, '0')}`
          + ` · trio ${String(v.trio).padStart(2, '0')}`
          + ` · envolvente ${String(v.envolvente).padStart(2, '0')}`
          + ` · contraste ${v.contraste}`;
        lectura.innerHTML = `
          <p style="margin:0 0 0.5rem 0;">Esta línea va <strong>copiada literal</strong> en la
            portada de tu informe. Compruébala carácter a carácter: el número que aparece aquí
            es el que tú tecleaste.</p>
          <code class="linea-id">${linea}</code>
          <table>
            <caption class="sr-only">Tu variante del taller</caption>
            <tbody>
              <tr><th scope="row">Tu documento, como lo escribiste</th>
                  <td><code>${escT2(r.documento)}</code></td></tr>
              <tr><th scope="row">Variante</th><td><code>${v.clave}</code></td></tr>
              <tr><th scope="row">Tu localidad</th><td><strong>${v.localidad}</strong></td></tr>
              <tr><th scope="row">Sus sedes (tu <em>n</em>)</th><td><strong>${L.n}</strong></td></tr>
              <tr><th scope="row">Su área</th><td>${n5(L.area_km2)} km²</td></tr>
              <tr><th scope="row">Su λ</th><td>${n5(L.lambda)} sedes/km²</td></tr>
              <tr><th scope="row">Tu patrón (T3)</th>
                  <td><code>p${String(v.propio).padStart(2, '0')}</code></td></tr>
              <tr><th scope="row">Tu trío (T2)</th>
                  <td><code>t${String(v.trio).padStart(2, '0')}a</code>,
                      <code>t${String(v.trio).padStart(2, '0')}b</code> y
                      <code>t${String(v.trio).padStart(2, '0')}c</code></td></tr>
              <tr><th scope="row">Tu envolvente (T4)</th>
                  <td><code>${String(v.envolvente).padStart(2, '0')}</code></td></tr>
              <tr><th scope="row">Tu localidad de contraste (T4)</th>
                  <td>${v.contraste}</td></tr>
            </tbody>
          </table>`;
        // A mano, porque esta tabla nace DESPUÉS de que loadModule() haya
        // llamado a envolverTablas(): sin esto, a 318 px la tabla empuja
        // la página entera y aparece el desplazamiento horizontal que el
        // capítulo 1 midió y arregló para todas las demás.
        envolverTablas();
      }

      function aplica(txt) {
        T2_DOC = txt;
        try { window.localStorage.setItem(T2_LLAVE, txt); } catch (e) { /* sin almacenamiento */ }
        // Todas las tiras de la página, no solo esta: un módulo puede
        // tener dos y quedarían discrepando entre sí.
        document.querySelectorAll('.simulador[data-simulador="taller2-variante"]')
          .forEach(otra => { if (otra.__t2pinta) otra.__t2pinta(); });
        // Las curvas del trío, si el módulo actual las tiene.
        document.querySelectorAll('.simulador[data-simulador="taller2-trio-curvas"]')
          .forEach(otra => { if (otra.__t2curvas) otra.__t2curvas(); });
        // Y los mapas. Ojo con el caso que se comió T1 entero en la
        // verificación del Taller 1: si el módulo se abrió SIN variante,
        // `iniciarGeomapas()` se fue por su rama de «sin datos» —`fuente()`
        // devuelve null— y salió sin dejar `__geomapa` en el contenedor.
        // Repintar entonces no repinta nada: quien escribe su documento
        // DENTRO de T2, que es donde está la segunda tira y por tanto el
        // camino natural, veía la ficha resolverse y los mapas seguir sin
        // aparecer. Así que un contenedor sin cablear no se repinta: se
        // CABLEA, y para eso hay que llamar al inicializador.
        const mapas = [...document.querySelectorAll('[data-geomapa^="taller2-"]')];
        if (mapas.some(g => !g.__geomapa)) iniciarGeomapas();
        mapas.forEach(g => {
          if (!g.__geomapa) return;
          g.__geomapa.dibuja();
          // Y la tabla de respaldo A MANO, porque `dibuja()` no la toca:
          // `iniciarGeomapas()` la pinta UNA vez con el dato inicial y
          // luego solo se repintan lienzo y leyenda. Sin esta línea, quien
          // corrige un dígito ve los mapas nuevos con las coordenadas del
          // trío anterior debajo, y aquí la tabla no es un resumen: es EL
          // dato con el que se rehacen las curvas.
          const det = g.querySelector('.geomapa-tabla');
          const spec = GEOMAPAS[g.dataset.geomapa];
          const d = spec && (typeof spec.fuente === 'function' ? spec.fuente() : spec.fuente);
          if (det && d && spec.tabla)
            det.innerHTML = '<summary>Ver los datos en una tabla</summary>' + spec.tabla(d);
        });
        envolverTablas();
      }

      raiz.__t2pinta = pinta;
      campo.addEventListener('input', () => aplica(campo.value));
      campo.value = T2_DOC;
      pinta();
    };

    // --- Las tres parejas de curvas de T2 -----------------------------
    // Tres gráficos, uno por pareja, y NO uno con seis series: con seis
    // líneas en un lienzo el estudiante emparejaría por color y no por
    // forma, que es justo lo que la tarea no quiere.
    //
    // Los tres se crean siempre, aunque no haya variante todavía, y se
    // rellenan después. Crearlos a demanda obligaría a devolverlos al
    // motor fuera de `iniciarSimuladores()`, y entonces `destruirSimuladores()`
    // no los conocería: son los gráficos huérfanos que se acumulan al
    // cambiar de módulo.
    SIMULADORES['taller2-trio-curvas'] = function (raiz) {
      const lienzos = [...raiz.querySelectorAll('canvas')];
      const lectura = raiz.querySelector('.simulador-lectura');
      const graficos = lienzos.map((lienzo, i) => crearGraficoLinea(lienzo, [], [
        { label: 'G(r)', data: [], borderColor: COLORES_GRAFICO.primario,
          backgroundColor: COLORES_GRAFICO.primario, borderWidth: 2, pointRadius: 0 },
        { label: 'F(r)', data: [], borderColor: COLORES_GRAFICO.secundario,
          backgroundColor: COLORES_GRAFICO.secundario, borderWidth: 2,
          borderDash: [5, 3], pointRadius: 0 }
      ], {
        scales: {
          x: { title: { display: true, text: 'r' },
               ticks: { maxTicksLimit: 6, font: { family: 'Montserrat', size: 11 } },
               grid: { display: false } },
          y: { min: 0, max: 1, ticks: { font: { family: 'Fira Code', size: 11 } },
               grid: { color: 'rgba(148, 163, 184, 0.2)' } }
        }
      }));

      function pinta() {
        const r = t2Resuelve(T2_DOC);
        if (!r) {
          graficos.forEach(g => {
            g.data.labels = [];
            g.data.datasets.forEach(ds => { ds.data = []; });
            g.update('none');
          });
          lectura.innerHTML = `<p style="margin:0;">Resuelve tu variante arriba y aquí
            aparecerán las tres parejas de curvas de tu trío.</p>`;
          return;
        }
        const etiquetas = r.trio[0].r.map(x => n5(x, 3));
        graficos.forEach((g, i) => {
          g.data.labels = etiquetas;
          g.data.datasets[0].data = r.trio[i].G;
          g.data.datasets[1].data = r.trio[i].F;
          g.update('none');
          g.canvas.setAttribute('aria-label',
            'Funciones G y F del par ' + (i + 1) + ' de tu trío, sobre r de '
            + etiquetas[0] + ' a ' + etiquetas[etiquetas.length - 1]
            + '. Los valores están en la tabla que hay debajo.');
        });

        // La tabla de respaldo de las curvas: para quien no ve los
        // gráficos ES el gráfico, y para todos los demás es lo que
        // permite citar un r concreto, que es lo que (a) pide.
        const paso = 5;
        const filas = [];
        for (let j = 0; j < r.trio[0].r.length; j += paso) {
          let f = `<tr><th scope="row">${n5(r.trio[0].r[j], 3)}</th>`;
          for (let i = 0; i < 3; i++)
            f += `<td>${n5(r.trio[i].G[j], 3)}</td><td>${n5(r.trio[i].F[j], 3)}</td>`;
          filas.push(f + '</tr>');
        }
        lectura.innerHTML = `<details class="geomapa-tabla"><summary>Ver las seis curvas en
          una tabla</summary><table><caption>G y F de las tres parejas, una fila de cada
          ${paso} valores de r.</caption><thead><tr><th scope="col">r</th>
          <th scope="col">G · Par 1</th><th scope="col">F · Par 1</th>
          <th scope="col">G · Par 2</th><th scope="col">F · Par 2</th>
          <th scope="col">G · Par 3</th><th scope="col">F · Par 3</th></tr></thead>
          <tbody>${filas.join('')}</tbody></table></details>`;
        envolverTablas();
      }

      raiz.__t2curvas = pinta;
      pinta();
      return graficos;
    };
"""

# Las dos rúbricas —la del escrito y la de la defensa— llegan en C5b. El
# registro de demostración se retira ya, para que no viaje una rúbrica
# ajena dentro del taller.
RUBRICA_JS = """    // Las dos rúbricas del taller —la del escrito y la de la defensa— se
    // registran en C5b, con el módulo que las muestra. Aquí no queda
    // ninguna: una rúbrica de demostración dentro de un taller que se
    // califica se lee como la rúbrica del taller.
"""

# El taller no lleva autoevaluación: la evaluación ES el taller, y el banco
# de la defensa es oral. El registro de demostración se retira para que no
# quede un quiz huérfano esperando un marcado que nunca llega.
QUIZ_JS = """    // Sin autoevaluación: en un taller la evaluación es el propio taller,
    // y el banco de la defensa (C6) son preguntas orales, no un quiz.
"""

CSS_EXTRA = """
    /* El distintivo de peso de cada tarea. Va pegado al título del
       enunciado porque el peso es parte del enunciado: saber que una tarea
       vale el 8 % cambia cuánto tiempo merece. */
    .badge-peso {
      display: inline-block;
      background: #012820;
      color: #fff;
      font-size: 0.7rem;
      font-weight: 700;
      padding: 0.1rem 0.5rem;
      border-radius: 50px;
      vertical-align: middle;
      margin-left: 0.35rem;
    }

    /* Los literales de una tarea: a), b), c)… con aire entre ellos, que es
       lo que hace que se lean como preguntas distintas y no como un párrafo
       troceado. */
    .lista-literales {
      margin: 0.75rem 0 0 0;
      padding-left: 1.6rem;
    }

    .lista-literales > li {
      margin-bottom: 0.55rem;
      color: #1e293b;
    }

    .lista-literales > li:last-child {
      margin-bottom: 0;
    }

    /* La línea de identificación que va literal en la portada. Se lee como
       lo que es —algo que se copia, no que se interpreta— y por eso va en
       monoespaciada y con el fondo del curso.

       `white-space: pre` con `overflow-x: auto` y no `break-word`: partir
       la línea en dos renglones invita a copiarla partida, y una portada
       con el número de documento cortado a la mitad es exactamente el
       error que esta línea existe para evitar. */
    .linea-id {
      display: block;
      background: #012820;
      color: #e8f3ef;
      font-family: 'Fira Code', monospace;
      font-size: 0.8rem;
      line-height: 1.6;
      padding: 0.6rem 0.75rem;
      border-radius: 0.4rem;
      margin-bottom: 0.9rem;
      white-space: pre;
      overflow-x: auto;
      -webkit-overflow-scrolling: touch;
    }

    /* Los tres mapas de T2 y sus tres gráficos, en la misma rejilla para
       que las casillas se correspondan a simple vista.

       `minmax(230px, 1fr)` y no un número de columnas fijo: a 318 px —el
       ancho más estrecho que este material se compromete a servir— tres
       columnas darían casillas de 90 px, que no son un mapa sino una
       mancha. Con `auto-fit` la rejilla cae sola a una columna. */
    .trio-rejilla {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(230px, 1fr));
      gap: 1rem;
      margin: 1rem 0;
    }

    .grafico-titulo {
      font-weight: 700;
      font-size: 0.85rem;
      color: #012820;
      margin: 0 0 0.3rem 0;
      text-align: center;
    }
"""


def reemplaza_region(texto, abre, cierra, nuevo, que, max_lineas, min_lineas=0):
    """Sustituye entre `abre` y el primer `cierra` posterior, con DOS topes.

    Copiada de `ensambla_taller1.py` con sus dos guardas, y las dos hacen
    falta por lo mismo: sustituir de más se llevó 270 líneas del motor con
    el informe en verde, y sustituir de menos dejó vivos dos simuladores de
    demostración con el archivo bien formado y la consola limpia.
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
                 f"DEMASIADO PRONTO.")
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
    # --- Guardas de entrada ---------------------------------------------
    # La permutación de los mapas de T2 decide si la tarea evalúa algo o
    # se contesta por el orden. Se comprueba ANTES de escribir nada.
    if len(ORDEN_MAPAS) != len(D["trios"]):
        sys.exit(f"PARADO: hay {len(D['trios'])} tríos y {len(ORDEN_MAPAS)} "
                 f"permutaciones de mapas")
    for i, fila in enumerate(ORDEN_MAPAS):
        if sorted(fila) != [0, 1, 2]:
            sys.exit(f"PARADO: la permutación del trío {i + 1} no es una "
                     f"permutación de (0, 1, 2): {fila}")
        if fila == (0, 1, 2):
            sys.exit(f"PARADO: la permutación del trío {i + 1} es la identidad, "
                     f"y entonces T2(a) se contesta con «A con 1, B con 2, C con 3»")

    doc = PLANTILLA.read_text(encoding="utf-8")
    print(f"\n=== ensambla_taller2.py (C5a) ===\nplantilla: {len(doc)/1024:.0f} KB\n")

    doc = sustituye(doc, "<title>Plantilla de capítulo — Estadística Espacial</title>",
                    "<title>Taller 2 · Patrones puntuales — Estadística Espacial</title>",
                    "título")
    doc = sustituye(doc, "PLANTILLA BASE •\n              5 MÓDULOS DE DEMOSTRACIÓN • UNBOSQUE 2026-II",
                    "TALLER 2 • CAPÍTULO 4 •\n"
                    "              ESCRITO 40 % + DEFENSA 60 % • UNBOSQUE 2026-II",
                    "subtítulo de la cabecera")
    doc = sustituye(doc, "Estadística Espacial (20929) • Plantilla de\n          capítulo • UnBosque 2026-II",
                    "Estadística Espacial (20929) • Taller 2 •\n"
                    "          Corte II • UnBosque 2026-II", "pie")

    doc = sustituye(doc, "    /* ------------------------------------------------------------------\n"
                         "       Componente .ciclo — diagrama de etapas recorrible",
                    CSS_EXTRA + "\n    /* ------------------------------------------------------------------\n"
                                "       Componente .ciclo — diagrama de etapas recorrible",
                    "el CSS propio del taller")

    doc = reemplaza_region(doc, "    const courseData = {", "\n    };\n", COURSE_DATA,
                           "courseData + DATOS_T2", max_lineas=20)

    doc = reemplaza_region(
        doc,
        "  <!-- ============================================================ -->\n"
        "  <!-- MÓDULO 1 · Cajas y tipografía",
        "\n  <script>", MODULOS.lstrip("\n") + "\n  <script>",
        "los módulos del taller", max_lineas=600)

    doc = reemplaza_region(doc, "    RUBRICAS['demo-rubrica'] = {", "\n    };\n",
                           RUBRICA_JS, "RUBRICAS", max_lineas=40)

    vieja = [l for l in doc.splitlines() if l.startswith("    GEOMAPAS['demo-mapa'] =")]
    if len(vieja) != 1:
        sys.exit(f"PARADO: {len(vieja)} registros de GEOMAPAS['demo-mapa'], se esperaba 1")
    doc = sustituye(doc, vieja[0], GEOMAPAS_JS.rstrip("\n"), "los mapas del taller")

    doc = reemplaza_region(
        doc,
        "    // --- Deslizadores sobre un gráfico de línea ----------------------\n"
        "    SIMULADORES['demo-deslizadores'] = function (raiz) {",
        "    // ================================================================\n"
        "    // Autoevaluación de demostración: una pregunta de cada tipo\n",
        SIMULADORES_JS
        + "    // ================================================================\n"
          "    // Autoevaluación de demostración: una pregunta de cada tipo\n",
        "los simuladores de demostración", max_lineas=140, min_lineas=100)

    doc = reemplaza_region(doc, "    AUTOEVALUACIONES['demo'] = [", "\n    ];\n",
                           QUIZ_JS, "AUTOEVALUACIONES", max_lineas=90)

    DESTINO.parent.mkdir(parents=True, exist_ok=True)
    DESTINO.write_text(doc, encoding="utf-8")

    # --- Guardas de salida ----------------------------------------------
    # Que el guion escriba no significa que haya escrito bien.
    marcado = doc[:doc.rindex("\n  <script>")]
    mods = doc.count('<template id="module-')
    declarados = len(MODULOS_NAV)
    lienzos = marcado.count("<canvas")
    con_alt = sum(1 for c in marcado.split("<canvas")[1:]
                  if "aria-label" in c.split(">")[0])
    tareas = marcado.count('<div class="ejercicio-guiado">')
    tiras = marcado.count('data-simulador="taller2-variante"')

    try:
        donde = DESTINO.relative_to(RAIZ)
    except ValueError:
        donde = DESTINO
    print(f"\n{donde}  {len(doc)/1024:.0f} KB")
    print(f"  {mods} módulos ({declarados} declarados en la navegación) · "
          f"{tareas} tareas · {tiras} tiras de variante")
    print(f"  {lienzos} lienzos en el marcado, {con_alt} con aria-label "
          f"(los de los mapas los fabrica .geomapa al cargar el módulo)")

    problemas = []
    if mods != declarados:
        problemas.append(f"{mods} plantillas de módulo y {declarados} declaradas en la "
                         f"navegación: un botón llevaría a un panel en blanco sin un "
                         f"solo error en consola")
    if lienzos != con_alt:
        problemas.append(f"{lienzos - con_alt} lienzo(s) sin aria-label")

    # C5a escribe DOS tareas de las cinco, y la cuenta se declara aquí en
    # vez de dejarla en 100: un taller a medio construir que exigiera
    # sumar 100 obligaría a mentir en los pesos para pasar su propia
    # guarda, que es peor que no tenerla.
    ESCRITAS = (1, 2)
    PESO_TAREA, TAREAS_TOTALES = 8, 5
    if tareas != len(ESCRITAS):
        problemas.append(f"{tareas} tareas, se esperaban {len(ESCRITAS)} en C5a "
                         f"(T{' y T'.join(str(x) for x in ESCRITAS)})")
    pesos = [int(x) for x in re.findall(r'class="badge-peso">(\d+)&nbsp;%', marcado)]
    if pesos != [PESO_TAREA] * len(ESCRITAS):
        problemas.append(f"los pesos de las tareas son {pesos} y las cinco valen "
                         f"{PESO_TAREA} % cada una")
    if PESO_TAREA * TAREAS_TOTALES != 40:
        problemas.append(f"las {TAREAS_TOTALES} tareas al {PESO_TAREA} % no suman el "
                         f"40 % que pesa el escrito")

    # Qué módulos llevan la tira, declarado y no contado. En C5a la llevan
    # los tres: el de instrucciones porque es donde se resuelve, y los dos
    # de tarea porque las dos dependen del documento y volver al módulo 1 a
    # mirar qué localidad tocó es exactamente la fricción que hace que
    # alguien siga de memoria.
    CON_VARIANTE = {1, 2, 3}
    trozos = dict(zip(
        [int(x) for x in re.findall(r'<template id="module-(\d+)">', marcado)],
        re.split(r'<template id="module-\d+">', marcado)[1:]))
    faltan = sorted(k for k in CON_VARIANTE
                    if 'data-simulador="taller2-variante"' not in trozos.get(k, ""))
    sobran = sorted(k for k in trozos
                    if k not in CON_VARIANTE
                    and 'data-simulador="taller2-variante"' in trozos[k])
    if faltan:
        problemas.append(f"a los módulos {faltan} les falta la tira de variante: sus "
                         f"tareas dependen del documento y obligarían a volver al módulo 1")
    if sobran:
        problemas.append(f"los módulos {sobran} llevan tira de variante y no la necesitan")

    # Ninguna tarea puede llevar panel de solución: la decisión fue taller
    # sin solucionario, y un panel vacío se lee como un defecto.
    if 'class="ejercicio-panel solucion"' in marcado:
        problemas.append("hay un panel de solución en el marcado, y este taller no lleva")
    # Los botones plegables, accesibles: es lo que exige audita_texto_base.
    botones = re.findall(r'<button[^>]*class="(?:derivacion|ejercicio)-boton"[^>]*>', marcado)
    sin_aria = [b for b in botones
                if "aria-expanded" not in b or "aria-controls" not in b]
    if sin_aria:
        problemas.append(f"{len(sin_aria)} botón(es) plegable(s) sin aria-expanded/aria-controls")
    # Los `aria-controls` tienen que apuntar a algo que exista.
    for b in botones:
        m = re.search(r'aria-controls="([^"]+)"', b)
        if m and f'id="{m.group(1)}"' not in marcado:
            problemas.append(f"aria-controls apunta a un id que no existe: {m.group(1)}")
    # KaTeX no mide los espacios finos de Unicode: dentro de una fórmula
    # avisa por consola y deja un hueco, y el aviso sale en la consola de UN
    # módulo entre los que haya.
    RAROS = {" ": "U+202F espacio fino", " ": "U+2009 thin space",
             " ": "U+00A0 nbsp"}
    formulas = re.findall(r"\\\(.*?\\\)|\$\$.*?\$\$", marcado, re.S)
    sucias = [(f[:60], RAROS[c]) for f in formulas for c in RAROS if c in f]
    if sucias:
        problemas.append(f"{len(sucias)} fórmula(s) con un espacio que KaTeX no "
                         f"entiende: {sucias[:2]} — usa ent_mate()")
    if doc.count("<template") != doc.count("</template>"):
        problemas.append("las plantillas no abren y cierran igual")

    # Y la comprobación propia de un taller: que no se haya colado una
    # respuesta en el HTML. Las palabras son las que vigila
    # `audita_taller2.py` sobre el JSON, aquí sobre la prosa YA ENSAMBLADA
    # y sobre el JSON incrustado. «regular» se queda fuera de la lista a
    # propósito: en castellano es palabra corriente —«una rejilla
    # regular»— y una guarda que salta con el lenguaje normal se acaba
    # desactivando entera, que es peor que no tenerla.
    PROHIBIDAS = ("familia del patrón", "está agregado", "es aleatorio",
                  "thomas", "rssi", "rpoispp", "la ventana correcta es",
                  "la ventana buena es", "el régimen es")
    filtradas = [p for p in PROHIBIDAS if p in doc.lower()]
    if filtradas:
        problemas.append(f"el documento contiene una respuesta: {filtradas}")

    # Los componentes usados tienen que estar registrados, y al revés.
    codigo = "\n".join(l for l in doc.splitlines() if not l.lstrip().startswith("//"))
    for que, attr, registro in (
            ("geomapa", r'data-geomapa="([^"]+)"', r"GEOMAPAS\['([^']+)'\]\s*="),
            ("simulador", r'data-simulador="([^"]+)"', r"SIMULADORES\['([^']+)'\]\s*="),
            ("rúbrica", r'data-rubrica="([^"]+)"', r"RUBRICAS\['([^']+)'\]\s*=")):
        usados = sorted(set(re.findall(attr, marcado)))
        registrados = sorted(set(re.findall(registro, codigo)))
        falta = sorted(set(usados) - set(registrados))
        if falta:
            problemas.append(f"{que}(s) usados sin registrar: {falta}")
        sobra = sorted(set(registrados) - set(usados))
        if sobra:
            print(f"  ---  {que}(s) registrados y no usados: {sobra}")

    print()
    if problemas:
        for p in problemas:
            print(f"  MAL  {p}")
        print(f"\n  {len(problemas)} problema(s).\n")
        return 1
    print("  Ensamblado limpio: instrucciones + T1 y T2 (C5a).\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
