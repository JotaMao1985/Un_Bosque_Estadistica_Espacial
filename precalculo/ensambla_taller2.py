#!/usr/bin/env python3
"""
ensambla_taller2.py — construye el Taller 2 (capítulo 4) · C5a + C5b

Material de Estadística Espacial 2026-II (20929). Ver PLAN_Taller_2_Cap_4.md.

C5a trajo el esqueleto y los módulos 1 a 3 —las instrucciones con el
buscador de variante, T1 y T2— y C5b añade T3, T4, T5 y las dos rúbricas.
Falta C6: el banco de 36 preguntas y las 12 afirmaciones falsas. Cada paso
deja un HTML que ABRE Y FUNCIONA: la navegación declara solo los módulos
que existen, así que el taller a medio construir se puede leer entero sin
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

LO QUE C5b TUVO QUE CAMBIAR DEL PLAN, y está declarado en su §0. T4(a)
no puede «entregar el sesgo ya medido»: el JSON publica de cada localidad
solo identidad, n, área y λ, así que ni el sesgo de borde ni el cociente
perímetro/área viajan — el estudiante los calcula, con el bloque que se le
da, y eso sigue sin repetir el ejercicio e5 del capítulo porque no pide
las tres correcciones. Y T4(b) no puede pedir el test global: la
envolvente viaja como curvas y el patrón que la produjo NO se publica.
Lo que sí se puede pedir —contar, comparar el recuento con lo esperado y
decir por qué el recuento tampoco decide— es lo que se pide.

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
# La lista del banco que se lee DESDE FUERA del taller: la necesita el
# blueprint del parcial 2 para no repetir una pregunta ya publicada.
BANCO_FUERA = _ruta("TALLER2_BANCO_DESTINO", SALIDAS / "taller2_banco.md")

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
# EL CALENDARIO, EN UN SOLO SITIO. Se movió dos veces —del viernes 18 de
# septiembre al martes 6 / jueves 8 de octubre el 2026-09-09, y al
# domingo 11 / martes 13 el 2026-09-11— y la segunda vez las fechas
# estaban escritas a mano en cuatro sitios de la prosa, y la hora en
# ninguno. `audita_texto_taller2.py` exige las de aquí y para si reaparece
# cualquiera de las viejas.
ENTREGA      = "domingo 11 de octubre de 2026"
HORA_LIMITE  = "13:00"
SUSTENTACION = "martes 13 de octubre"
CONTROL      = "la semana del 28 de septiembre"   # el control de C10b (§5.3)

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
          <a href="capitulo-5-intensidad-nucleos.html">capítulo 5 · Intensidad por
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
        <p><strong>El escrito: un solo PDF, el {ENTREGA}, a más tardar a las {HORA_LIMITE}.</strong>
          Se entrega
          por <strong>Brightspace</strong>, con el nombre
          <code>T2_Apellido_TuDocumento.pdf</code>. No se aceptan entregas tarde.</p>
        <p><strong>La portada lleva dos cosas obligatorias</strong>, y sin cualquiera de las dos
          la entrega está incompleta: la <strong>línea de identificación</strong> que te da el
          buscador de aquí abajo, copiada <em>literal</em>, y la <strong>bitácora</strong> de
          media página.</p>
        <p style="margin-bottom:0;"><strong>La sustentación: {SUSTENTACION}, presencial, en el
          espacio de la clase, una sola sesión.</strong> Son <strong>siete minutos</strong> por persona, repartidos en tres
          bloques: <strong>2 min</strong> defendiendo <em>una</em> decisión de tu escrito, que
          elige el profesor después de haberlo leído (30&nbsp;% de la defensa);
          <strong>3 min</strong> con <strong>tres preguntas</strong> de un banco publicado con
          este taller (45&nbsp;%); y <strong>2 min</strong> de refutación en vivo, donde se te lee
          una afirmación falsa sobre el capítulo y dices por qué lo es (25&nbsp;%). El banco y las
          dos rúbricas —la del escrito y la de la defensa— se publican con el enunciado.</p>
      </div>

      <div class="warning">
        <p style="margin-bottom:0;"><strong>En una clase de {CONTROL} traes cinco
          cosas.</strong> Tu localidad, su <em>n</em> y su λ, tu patrón y tu trío —las cinco están
          en la tabla que te da el buscador—, en voz alta, y nada más. No se califica y no hay que
          entregar nada: es un control para atrapar a tiempo a quien esté resolviendo una variante
          que no es la suya. Si eso pasa y se descubre el día de la entrega, ya no hay nada que
          hacer; si se descubre esa semana, quedan días de sobra.</p>
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
        <p><strong>Qué pesa cada cosa.</strong> El escrito vale el 40&nbsp;% y la sustentación el
          60&nbsp;%. Dentro del escrito, las cinco tareas <strong>pesan lo mismo</strong>: un
          8&nbsp;% de la nota del taller cada una. Eso dice <em>cuánto ocupa</em> cada tarea en el
          informe, no cómo se puntúa: <strong>la nota del escrito sale de las cinco dimensiones de
          la rúbrica aplicadas al informe completo</strong>, no de sumar cinco notas por tarea.
          Dejar una tarea sin hacer no resta un 8&nbsp;% redondo: resta en las dimensiones que esa
          tarea alimentaba, y son varias.</p>
        <p><strong>Y contra el syllabus del curso</strong>, que califica los talleres con tres
          criterios: la <em>pertinencia del método espacial elegido</em> es lo que miden las
          dimensiones <strong>A</strong> y <strong>C</strong> —elegir la ventana, la rejilla, el
          \(r\), el σ, y sostenerlo—; la <em>corrección técnica del análisis en R</em> es
          <strong>C</strong>, y el taller la exige además por otra vía: varios enunciados piden que
          tus cifras <strong>reproduzcan exactamente</strong> las del bloque, porque aquí no se
          evalúa que escribas código sino que corras el que se te da y leas bien lo que sale; y la
          <em>interpretación de los resultados</em> es <strong>B</strong>. Las
          dimensiones <strong>D</strong> —refutar— y <strong>E</strong> —declarar el uso de IA— son
          de este taller, y van por encima de lo que el syllabus pide.</p>
        <p style="margin-bottom:0;">Las dos rúbricas están en el último módulo, y conviene leerlas
          <em>antes</em> de escribir, no después.</p>
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
#
# LO QUE CAMBIÓ LA AUDITORÍA DE CONTENIDO (A1, 2026-09-12). Seis arreglos,
# ninguno de ellos en el JSON: la tarea es la misma y las 1000 variantes
# no se tocan.
#
#   · (c) ACOTA LA BÚSQUEDA A k = 2, 3, 4, 5 Y PROHÍBE k = 1. Decía «la
#     rejilla más fina en la que ninguna celda baje de 5, y si no existe
#     ninguna, dilo». Siempre existe una: k = 1, una sola celda con
#     esperanza n, y `quadrat.test(nx = 1, ny = 1)` devuelve X2 = 0 con
#     0 grados de libertad y «p-value < 2.2e-16», que parece un rechazo
#     rotundo y es un artefacto. En Usme, Tunjuelito y Los Mártires era la
#     ÚNICA legible: tres de las dieciséis localidades daban un veredicto
#     falso siguiendo la letra. El calificador ya buscaba entre 2 y 12 sin
#     decirlo, así que además lo daba por mal. Medido el 2026-09-12 sobre
#     las dieciséis: ninguna tiene rejilla legible por encima de k = 5, así
#     que la horquilla que ahora se publica es la búsqueda entera.
#
#   · Y PIDE LA TABLA DE LOS CUATRO, no la primera que pase. En Engativá el
#     conjunto legible NO es contiguo —k = 2 no pasa (4,70), k = 3 sí
#     (6,03)—, y quien buscara subiendo y parara en el primer fallo
#     concluía «ninguna». La pista decía además que bajar el k sube las
#     esperadas; es verdad de la media y no de la mínima, que es la que
#     manda. Las dos frases están corregidas.
#
#   · (d) DICE QUÉ SE REFUTA. «A mí también me rechazó con la caja» daba
#     por hecho lo que a Los Mártires no le pasa —su caja no rechaza,
#     p = 0,0605—, y «no todas las localidades se comportan igual» empujaba
#     a buscar un veredicto que cambiara, cosa que solo tienen tres de
#     dieciséis. Lo que se refuta es «el error no importa», y eso se puede
#     refutar desde cualquiera de las dieciséis.
#
#   · EL COMENTARIO DEL BLOQUE DE R DECÍA CUÁL ES LA BUENA. «las esperadas
#     del contraste bueno», tres párrafos después de prometer que «nadie te
#     va a decir cuál de las dos está mal». `audita_texto_taller2.py`
#     prohibía la frase en la prosa y no miraba los comentarios del código;
#     ahora los mira, y el arnés lo inyecta.
#
#   · EL BLOQUE DE PYTHON NO IMPRIMÍA NADA corrido como guion, no calculaba
#     λ ni las áreas —que es todo (a)— y tiraba las esperanzas con `[:3]`,
#     que es lo que necesita (c). El de R hacía las tres cosas.
#
#   · «el defecto de spatstat» quería decir «el valor por defecto», en una
#     tarea cuyo verbo es «nombra el defecto».
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

# Y el supuesto, celda a celda, sobre las celdas RECORTADAS por la
# ventana: tile.areas() da el area de cada cuadrante ya recortado, y es
# esa area la que reparte las esperadas.
esperadas &lt;- function(k) {
  a &lt;- tile.areas(as.tess(quadratcount(p_poly, nx = k, ny = k)))
  npoints(p_poly) * a / sum(a)
}
esp &lt;- esperadas(5)
c(celdas = length(esp), bajas = sum(esp &lt; 5))

# La tabla de los cuatro k que pide (c). Programar la busqueda no es lo
# que se califica —lo que se califica es lo que decidas con ella—, asi
# que va hecha.
t(sapply(2:5, function(k) {
  e &lt;- esperadas(k)
  c(k = k, celdas = length(e), minima = min(e))
}))''',
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
    # DOS COLAS, que es lo que hace spatstat::quadrat.test POR DEFECTO,
    # y lo que corre tu R. La cola superior sola da otro p-valor, y sobre
    # estos datos llega a cambiar el veredicto: no es un decimal.
    sup = chi2.sf(x2, gl)
    return x2, gl, 2 * min(sup, 1 - sup), esp

# Las dos ventanas, con lo que pide (a) —area e intensidad— y lo que
# pide (c) —el recuento de esperanzas bajas—. Va con print() a proposito:
# sin el, corrido como guion, este bloque no escribe nada en pantalla.
def informe(nombre, poly, caja):
    a_km2 = (box(*poly.bounds).area if caja else poly.area) / 1e6
    x2, gl, p, esp = cuadrantes(xy, poly, caja=caja)
    print(nombre, "· area km2:", round(a_km2, 4),
          "· lambda:", round(len(xy) / a_km2, 4))
    print("   X2:", round(x2, 4), "· gl:", gl, "· p:", p)
    return esp

informe("caja", mia, caja=True)
esp = informe("poligono", mia, caja=False)

# Y el supuesto, sobre las MISMAS celdas recortadas que mira el bloque de
# R: ar[viva] aqui y tile.areas() alli son la misma area.
print("celdas:", esp.size, "· con esperanza menor que 5:", int((esp &lt; 5).sum()))

# La tabla de los cuatro k que pide (c), con la misma cuenta. Programar
# la busqueda no es lo que se califica.
for k in (2, 3, 4, 5):
    e = cuadrantes(xy, mia, k=k, caja=False)[3]
    print("k =", k, "· celdas:", e.size,
          "· esperanza minima:", round(float(e.min()), 4))''')}

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
        "decide si tu p-valor se puede leer o no. Si no se puede, busca una rejilla "
        "\\(k \\times k\\) que sí lo sea: <strong>prueba \\(k = 2, 3, 4, 5\\)</strong> —los cuatro, sin parar en el primero "
        "que falle—, da la esperanza <strong>mínima</strong> de cada uno, quédate con el \\(k\\) "
        "más grande que no baje de 5 y di qué veredicto da ese. <strong>\\(k = 1\\) no "
        "vale</strong>: una sola celda no compara nada contra nada, y el contraste sale con cero "
        "grados de libertad y un p-valor que no significa nada. Si no pasa ninguno de los cuatro, "
        "dilo y sostenlo: también es una respuesta.",
        "Un compañero te dice: «a mí me rechazó con la caja y también con el polígono, así que "
        "el error no importa». Lo que tienes que refutar es <strong>que el error no "
        "importa</strong>, no que su veredicto cambie: un procedimiento puede acertar el "
        "veredicto por el camino equivocado, y eso no lo vuelve correcto. Hazlo <strong>con su "
        "cifra y con la tuya</strong> —pídele las suyas, porque no todas las localidades se "
        "comportan igual—.",
        "¿Por qué este defecto <strong>no</strong> se vería mirando el mapa del patrón?"],
       "Las dos ventanas contienen los mismos puntos, así que lo que cambia no es el patrón: es "
       "el área contra la que lo estás comparando, y con ella lo que el contraste considera "
       "«uniforme». Para (c), fíjate en que bajar el \\(k\\) sube la esperanza media y baja "
       "la resolución: hay que elegir, y elegir es la tarea. Pero la que decide es la esperanza "
       "<strong>mínima</strong>, y esa no siempre sube al bajar el \\(k\\): depende de cómo tu "
       "contorno corte las celdas del borde. Y para (e): pregúntate qué parte de todo esto se "
       "dibuja.") + f"""
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
        sin convertir nada. Bajo cada mapa hay un desplegable con <strong>las coordenadas del
        dibujo</strong>, listas para <code>ppp()</code>: son las del patrón encajadas en el
        recuadro y redondeadas a cuatro decimales, así que la <em>forma</em> es la misma y las
        cifras no del todo: una \\(G\\) calculada desde la tabla no reproduce la curva publicada.
        Los <strong>mismos puntos con toda su precisión</strong>
        viajan en el CSV que descargaste, bajo el identificador de tu trío, y es el CSV el que hay
        que usar para cualquier cifra que entregues.</p>

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
        "lo afirmas</strong>: da el \\(r\\) en el que tu curva decide —y si alguna no decide en "
        "ningún \\(r\\), dilo y sostenlo: también es una respuesta—, y di qué pasaría con tu "
        "veredicto si solo miraras \\(r\\) por encima de ese valor.",
        "\\(G\\) y \\(F\\) no tienen por qué decir lo mismo. <strong>Compara cada una con la "
        "que daría la CSR</strong> —\\(1 - e^{-\\lambda \\pi r^2}\\) para las dos, con tu "
        "\\(\\lambda\\)— y di, para cada uno de tus tres patrones, a qué régimen apunta "
        "\\(G\\) y a cuál apunta \\(F\\). ¿Hay alguno donde no apunten al mismo? Si en los tres "
        "apuntan al mismo, <strong>construye</strong> el caso en que no lo harían —descríbelo con "
        "precisión suficiente para que otra persona lo pueda generar— y di qué mira cada una para "
        "que eso ocurra."],
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

# La rejilla de r es la MISMA de las curvas de arriba. A Gest() no se le
# puede pedir directamente, asi que se calcula en la suya y se interpola.
rg &lt;- seq(0, 0.25, length.out = 51)

# LA F NO SALE DE Fest(), Y NO ES UN CAPRICHO. `Fest()` se apoya en
# distmap(), y en esta version de spatstat distmap() devuelve distancias
# AL CUADRADO que Fest() lee como distancias: la curva sale disparada a 1
# en el segundo o el tercer nodo. La prueba cabe en una linea —un solo
# punto en el centro del cuadrado unidad tiene F(0,1) = pi*0,01 = 0,0314
# y Fest() publica 0,4020—, y si corres Fest() aqui veras que no se
# parece a la F de tu grafico. Si tu instalacion la tiene sana, mejor:
# esto le da igual, porque no la usa.
#
# Asi que la F se escribe, que es ademas su definicion. Muestra reducida:
# de los sitios de la ventana que estan a MAS de r del borde —los unicos
# donde la respuesta no depende de lo que no se observo—, la fraccion que
# tiene un punto a distancia r o menos. Es lo que hizo el precalculo, y
# por eso las cifras coinciden hasta el ultimo decimal publicado.
# Las sondas se calculan UNA vez: son las mismas para los tres patrones.
sondas &lt;- expand.grid(x = seq(0, 1, length.out = 400),
                      y = seq(0, 1, length.out = 400))
sp &lt;- ppp(sondas$x, sondas$y, window = owin(c(0, 1), c(0, 1)), check = FALSE)
bb &lt;- bdist.points(sp)                  # distancia al borde de la ventana

# LOS TRES DE UNA VEZ. (a) los empareja los tres, asi que el bucle va
# hecho: escribirlo no es lo que se califica.
curvas &lt;- function(letra) {
  uno &lt;- subset(pat, patron == paste0(MI_TRIO, letra))
  stopifnot(nrow(uno) &gt; 0)              # si para, ese trio no es el tuyo
  p  &lt;- ppp(uno$x, uno$y, window = owin(c(0, 1), c(0, 1)))
  aG &lt;- Gest(p)
  dd &lt;- nncross(sp, p, what = "dist")   # distancia al punto mas cercano
  data.frame(patron = paste0(MI_TRIO, letra), r = rg,
             G = approx(aG$r, aG$km, xout = rg, rule = 2)$y,
             F = sapply(rg, function(r) mean(dd[bb &gt; r] &lt;= r)))
}
tres &lt;- do.call(rbind, lapply(c("a", "b", "c"), curvas))

op &lt;- par(mfrow = c(1, 3))
for (l in c("a", "b", "c")) {
  d &lt;- subset(tres, patron == paste0(MI_TRIO, l))
  plot(d$r, d$G, type = "l", ylim = c(0, 1), main = paste0(MI_TRIO, l),
       xlab = "r", ylab = "")
  lines(d$r, d$F, lty = 2)
  legend("bottomright", c("G", "F"), lty = c(1, 2), bty = "n")
}
par(op)

# Los tres en los nodos que mas separan las dos curvas
subset(tres, r %in% c(0.02, 0.05, 0.10))''',
      '''import numpy as np, pandas as pd
from scipy.spatial import cKDTree

MI_TRIO = ""          # "t03" si el tuyo es el 3: lo dice el buscador

pat = pd.read_csv("datos/taller2_patrones.csv")
rg = np.linspace(0, 0.25, 51)

# Las sondas de la F se calculan UNA vez: son las mismas para los tres.
# Se usan SOLO las que estan a mas de r del borde —muestra reducida—, que
# es lo mismo que hace el bloque de R y lo que hizo el precalculo. Sin
# ese filtro la curva se queda corta cerca del borde, hasta 0,22.
gx, gy = np.meshgrid(np.linspace(0, 1, 400), np.linspace(0, 1, 400))
sondas = np.c_[gx.ravel(), gy.ravel()]
bo = np.minimum(sondas.min(1), 1 - sondas.max(1))   # distancia al borde

# LOS TRES DE UNA VEZ. (a) los empareja los tres, asi que el bucle va
# hecho: escribirlo no es lo que se califica.
def curvas(letra):
    uno = pat[pat.patron == MI_TRIO + letra][["x", "y"]].to_numpy()
    assert len(uno), "ese trio no es el tuyo"
    arbol = cKDTree(uno)
    d, _ = arbol.query(uno, k=2)          # G: de cada PUNTO a su vecino
    dv, _ = arbol.query(sondas, k=1)      # F: de cada SITIO al punto
    return (np.array([(d[:, 1] &lt;= r).mean() for r in rg]),
            np.array([(dv[bo &gt; r] &lt;= r).mean() for r in rg]))

tres = {letra: curvas(letra) for letra in "abc"}

# LA F ES LA PUBLICADA; LA G NO DEL TODO. La de arriba lleva la
# correccion de Kaplan-Meier de spatstat y esta va cruda: sobre estos
# patrones se apartan hasta 0,09 en el tramo empinado. Para citar un
# valor de G usa las curvas del enunciado o R; la forma es la misma.
for letra, (G, F) in tres.items():
    print(MI_TRIO + letra, "· G y F en r = 0.02, 0.05 y 0.10:")
    for r in (0.02, 0.05, 0.10):
        i = int(round(r / 0.005))
        print("   r =", r, "· G =", round(float(G[i]), 4),
              "· F =", round(float(F[i]), 4))''')}
""" + CIERRE


# =====================================================================
# MÓDULO 4 · T3 · Dónde está la estructura
# =====================================================================
# El informe que se pone a auditar se RENDERIZA en el navegador, no se
# escribe aquí, y no es un capricho: su premisa cita el último r en que
# L − r sigue siendo positiva, que es distinto para cada patrón. Escrita
# a mano sería una cifra sin respaldo en el JSON (D10) y, peor, sería
# falsa para alguno de los veinticuatro. La premisa es cierta para los 24
# —comprobado en el navegador: p16 renderiza 0,210 y p24, 0,250—.
#
# LA CONCLUSIÓN, EN CAMBIO, NO ES FALSA PARA TODOS, y aquí este comentario
# decía que sí. Lo midió la auditoría de contenido el 2026-09-12 sobre los
# 24: **p24 no tiene ningún r en el que g vuelva a 1**. Su g baja hasta
# 1,0687 en r = 0,140 y remonta hasta 1,1982 en el último nodo, así que en
# todo el rango publicado hay más vecinos de los que daría la CSR y la
# frase del informe —«la agregación se extiende a lo largo de todo ese
# rango»— es la que hay que CONFIRMAR. Le toca a 32 de las 1000 variantes:
# en una clase de doce, un 32 % de probabilidad de que alguien la tenga.
# Regenerar para quitar p24 sería peor que el defecto, así que lo que se
# arregla es la letra: (a) y (b) admiten ahora «no vuelve a 1 en el rango»,
# igual que T1(c) admite «no hay rejilla legible». El calificador imprimía
# «g vuelve a 1 en r = NA» y ya no.
#
# Y DOS COSAS MÁS QUE MIDIÓ LA MISMA PASADA, y que la letra tenía que
# recoger: en 14 de los 24 la g vuelve a asomar por encima de 1 después de
# su primer regreso —hasta 1,99 en p13—, así que «en qué r vuelve a 1» hay
# que pedirlo por la PRIMERA vez y avisar de que la curva es ruidosa (T3 no
# publica banda con la que separar el ruido); y en 23 de los 24 el máximo
# de g cae en r = 0, que es justo el nodo del que el módulo 9 del capítulo
# dice que «no es una escala característica: es donde empieza a mirarse».
MOD4 = cabecera(
    4, "Dónde está la estructura", "T3 · K, L and g",
    "Refutar una conclusión correcta de premisa con la función que sí "
    "resuelve la escala. Vale el 8 % del taller.") + variante() + f"""
      <p>Las dos tareas anteriores miraban el vecino más próximo y el espacio vacío. Las dos son
        funciones de <em>una</em> distancia por punto, y las dos se quedan sin decir nada en cuanto
        la pregunta es <strong>a qué distancia</strong> pasa lo que pasa. Para eso están \(K\) y
        \(g\), que son el módulo 8 y el módulo 9.</p>

      <p>Aquí trabajas sobre <strong>tu patrón</strong> —el que el buscador llama
        <code>p</code> más dos dígitos—, que no es ninguno de los tres de T2.</p>

      <div class="geomapa" data-geomapa="taller2-propio"></div>

      <div class="simulador" data-simulador="taller2-propio-curvas">
        <h4><i class="fas fa-chart-line" aria-hidden="true"></i> Las tres curvas de tu patrón</h4>
        <p class="simulador-intro">\(K(r)\) contra su valor bajo CSR, la transformación
          \(L(r) - r\) contra el cero, y \(g(r)\) contra el uno. Las tres sobre la misma
          rejilla de \(r\), y las tres con corrección de traslación.</p>
        <div class="trio-rejilla">
          <div>
            <p class="grafico-titulo">K(r) y πr²</p>
            <div class="grafico-wrapper" style="height:230px;">
              <canvas role="img" aria-label="Función K de tu patrón frente a su valor teórico bajo CSR"></canvas>
            </div>
          </div>
          <div>
            <p class="grafico-titulo">L(r) − r</p>
            <div class="grafico-wrapper" style="height:230px;">
              <canvas role="img" aria-label="Transformación L menos r de tu patrón, contra la línea del cero"></canvas>
            </div>
          </div>
          <div>
            <p class="grafico-titulo">g(r)</p>
            <div class="grafico-wrapper" style="height:230px;">
              <canvas role="img" aria-label="Correlación de pares g de tu patrón, contra la línea del uno"></canvas>
            </div>
          </div>
        </div>
        <div class="simulador-lectura"></div>
      </div>

      <p>Y este es el informe que tienes que auditar. Lo produjo un modelo de lenguaje al que se le
        dieron estas mismas curvas, y se cita <strong>literal</strong>:</p>

      <div class="cita-ia" data-informe="t3"></div>

      <div class="definition">
        <h3>Lo que separa a las dos funciones</h3>
        <p>\(K(r)\) cuenta, alrededor de cada punto, <strong>todos</strong> los vecinos que hay
          hasta la distancia \(r\). Es acumulada: lo que entra en el círculo a 20 m sigue dentro
          del círculo a 500 m. \(g(r)\) mira solo el <strong>anillo</strong> de radio \(r\), y
          por eso puede volver a su valor de referencia cuando la estructura se acaba.</p>
        <p style="margin-bottom:0;">Los módulos 8 y 9 del capítulo 4 construyen las dos, y el 9
          explica por qué \(g\) es más legible. La corrección de traslación con la que están
          calculadas es el módulo 10, y es la misma que usa el bloque de código de aquí abajo.</p>
      </div>

""" + tarea(3, 8, "Dónde está la estructura",
       "Con tus tres curvas y el informe de arriba:",
       ["¿Es cierta la conclusión del informe? <strong>Refútala o confírmala con \(g\)</strong>, "
        "y di <strong>hasta qué \(r\)</strong> llega de verdad la agregación de tu patrón —y si "
        "tu \(g\) no vuelve a 1 en todo el rango, dilo y sostenlo: también es una respuesta—. "
        "Fíjate en que la <em>premisa</em> del informe es correcta: compruébala antes de discutir "
        "la conclusión.",
        "Da <strong>tres cifras tuyas</strong>: cuánto vale \(g\) en su punto más alto —y en qué "
        "\(r\) cae ese punto: si es el primero del barrido, el módulo 9 del capítulo dice qué "
        "es y qué no es—, en qué \(r\) vuelve \(g\) a 1 <strong>por primera vez</strong> —la "
        "curva es ruidosa y puede volver a asomar por encima después; y si no vuelve en todo el "
        "rango, esa es la cifra que no tienes—, y cuánto vale \(K\) en ese segundo \(r\), "
        "comparado con lo que valdría bajo CSR. Con esas cifras escribe <strong>la frase que el "
        "informe tendría que haber escrito</strong>.",
        "Ahora sobre <strong>tu localidad real</strong>, la de T1: calcula \(K\) y \(g\) de sus "
        "sedes. ¿Dicen lo mismo a todas las escalas, o se separan como en tu patrón generado? "
        "¿Contradice eso lo que acabas de responder en (a)? Nombra el módulo del capítulo 4 que "
        "explica la diferencia."],
       "La premisa y la conclusión del informe no se comprueban con la misma curva, y ahí está la "
       "tarea: la premisa la lees en \(L - r\), y la conclusión solo la decide \(g\). Para (b), "
       "si tu \(g\) vuelve a 1, la cifra que más cuesta leer es la tercera: \(K\) en un \(r\) "
       "donde \(g\) ya volvió a 1 no dice que siga habiendo agregación <em>ahí</em>, dice otra "
       "cosa — y decir cuál es la respuesta. Para (c), acuérdate de qué supone \(K\) sobre λ.") + f"""
      <div class="note">
        <p style="margin-bottom:0;"><strong>Cómo rehacer las tres curvas.</strong> Salen del CSV que
          descargaste, y con estas líneas dan <em>exactamente</em> las de arriba. Para (c) reutiliza
          el <code>p_poly</code> que construiste en T1.</p>
      </div>

{tabs('K, L y g de tu patrón',
      '''library(spatstat.geom)
library(spatstat.explore)

MI_PATRON &lt;- ""              # "p19" si el tuyo es el 19: lo dice el buscador

pat &lt;- read.csv("datos/taller2_patrones.csv")
uno &lt;- subset(pat, patron == MI_PATRON)
stopifnot(nrow(uno) &gt; 0)      # si para, ese patron no es el tuyo
p   &lt;- ppp(uno$x, uno$y, window = owin(c(0, 1), c(0, 1)))

# La MISMA rejilla y la MISMA correccion que las curvas de arriba. K y g
# se calculan en su rejilla nativa y se interpolan, que es lo que hizo el
# precalculo: con esto las cifras coinciden hasta el noveno decimal.
rg &lt;- seq(0, 0.25, length.out = 51)
aK &lt;- Kest(p, correction = "translate")
ag &lt;- pcf(p, correction = "translate")
K  &lt;- approx(aK$r, aK$trans, xout = rg, rule = 2)$y
g  &lt;- approx(ag$r, ag$trans, xout = rg, rule = 2)$y
L  &lt;- sqrt(pmax(K, 0) / pi) - rg

datos &lt;- data.frame(r = rg, K = K, teorica = pi * rg^2, L_menos_r = L, g = g)
head(datos, 12)

# Y (c), sobre tu localidad real: el mismo par de funciones sobre el
# `p_poly` de T1. Ojo con las unidades: aqui r va en METROS.
# plot(Kest(p_poly, correction = "translate"))
# plot(pcf(p_poly,  correction = "translate"))''',
      '''import numpy as np, pandas as pd

MI_PATRON = ""               # "p19" si el tuyo es el 19

pat = pd.read_csv("datos/taller2_patrones.csv")
uno = pat[pat.patron == MI_PATRON][["x", "y"]].to_numpy()
assert len(uno), "ese patron no es el tuyo"

# El peso de la correccion de traslacion es el area de solape de la
# ventana consigo misma desplazada por el vector que une los dos puntos.
# Para el cuadrado unidad eso es exactamente (1-|dx|)(1-|dy|). Es la
# misma funcion que publica el modulo 8 del capitulo 4.
def K_traslacion(x, y, r):
    n = len(x)
    dx = np.abs(x[:, None] - x[None, :]); dy = np.abs(y[:, None] - y[None, :])
    dist = np.hypot(dx, dy)
    sol = np.clip(1 - dx, 0, None) * np.clip(1 - dy, 0, None)
    m = ~np.eye(n, dtype=bool)
    return np.array([float((1 / sol[m])[dist[m] &lt;= rr].sum())
                     for rr in r]) / (n * (n - 1))

rg = np.linspace(0, 0.25, 51)
K = K_traslacion(uno[:, 0], uno[:, 1], rg)
L = np.sqrt(np.maximum(K, 0) / np.pi) - rg

# g por derivada numerica de K: g(r) = K'(r) / (2 pi r). La K de arriba
# es buena —se aparta de la tabla menos de 0,001—, pero esta g NO suaviza
# con un nucleo como la de spatstat, y eso se nota: sirve para ver la
# FORMA de la curva y el orden de magnitud, y NO para citar ninguna de
# las tres cifras de (b). Ni el maximo ni el r en que vuelve a 1: ese r
# puede caer un nodo antes o despues que en la tabla, y sobre estos
# patrones baila en mas de la mitad. Las cifras, de la tabla o de R.
g = np.gradient(K, rg) / (2 * np.pi * np.maximum(rg, 1e-9))

print(np.c_[rg, K, np.pi * rg ** 2, L, g][:12])''')}
""" + CIERRE


# =====================================================================
# MÓDULO 5 · T4 · El borde y la banda
# =====================================================================
# Dos mitades y las dos de refutación. La primera NO pide calcular las
# tres correcciones —eso es el ejercicio e5 del capítulo, §3.5— sino dos,
# sobre DOS ventanas de forma opuesta, y preguntar por la forma. La
# segunda tuvo que reescribirse contra lo que el JSON publica: la
# envolvente viaja como curvas (r, obs, lo, hi, teo) y el patrón que la
# produjo NO se publica, así que el test global que el plan preveía no lo
# puede correr el estudiante. Lo que sí puede es contar, comparar el
# recuento con lo que esperaría, y decir por qué el recuento tampoco
# decide. Declarado en el §0.
#
# LA VENTANA DE CONTRASTE ROTA DESDE EL 2026-09-10 (M-20). Hasta ese día
# el generador emparejaba cada localidad con «la más opuesta» y, como
# Antonio Nariño y Usme son los dos extremos del cociente, el 81,4 % de
# las variantes recibía la misma: el déficit y el perímetro/área de esa
# ventana eran la misma pareja de cifras para casi toda la clase, y el
# bloque de aquí abajo —que llama `mide("Antonio Narino")` de ejemplo—
# se podía correr sin tocar una letra. Ahora el contraste rota entre las
# que doblan el cociente, y por eso los dos bloques dicen en voz alta
# que sus nombres son un ejemplo.
MOD5 = cabecera(
    5, "El borde y la banda", "T4 · Edge and envelope",
    "Dos refutaciones: un sesgo que siempre empuja al mismo lado, y una "
    "banda leída al revés. Vale el 8 % del taller.") + variante() + f"""
      <h3>La primera mitad · el borde</h3>

      <p>Cuando cuentas vecinos alrededor de un punto que está cerca del límite de la ventana, parte
        de su círculo cae fuera y ahí no hay datos. Si no se corrige, esos vecinos que no se pueden
        contar se cuentan como <strong>ausencias</strong>. Aquí lo vas a medir en dos ventanas de
        forma deliberadamente opuesta: <strong>la tuya</strong> y la de contraste que te asignó el
        buscador. «Opuesta» aquí es una promesa con número: una de las dos tiene al menos el
        <strong>doble</strong> de perímetro/área que la otra. <em>Cuál de las dos</em> no te lo dice
        el enunciado — lo dice tu cálculo, y es la mitad de lo que se pregunta.</p>

      <div class="trio-rejilla">
        <div class="geomapa" data-geomapa="taller2-localidad"></div>
        <div class="geomapa" data-geomapa="taller2-contraste"></div>
      </div>

      <h3>La segunda mitad · la banda</h3>

      <p>Debajo tienes una envolvente de simulación calculada sobre un patrón que <strong>no es el
        tuyo</strong> ni tiene por qué serlo: lo que se audita es <em>la lectura que alguien hizo de
        ella</em>. A la izquierda, el rango completo de \(r\). A la derecha, <strong>el mismo
        cálculo</strong> —las mismas simulaciones, la misma curva— recortado al tramo que el informe
        eligió <em>después</em> de mirar.</p>

      <div class="simulador" data-simulador="taller2-envolvente">
        <h4><i class="fas fa-wave-square" aria-hidden="true"></i> La envolvente, entera y recortada</h4>
        <p class="simulador-intro">La banda es la de <code>envelope()</code> con las simulaciones que
          declara la lectura de abajo. Los dos paneles son el mismo cálculo: cambia el rango que se
          mira, no lo que se calculó.</p>
        <div class="trio-rejilla">
          <div>
            <p class="grafico-titulo">Todo el rango de r</p>
            <div class="grafico-wrapper" style="height:250px;">
              <canvas role="img" aria-label="Envolvente de K sobre todo el rango de r, con la banda de simulación y la curva observada"></canvas>
            </div>
          </div>
          <div>
            <p class="grafico-titulo">El tramo que eligió el informe</p>
            <div class="grafico-wrapper" style="height:250px;">
              <canvas role="img" aria-label="La misma envolvente restringida al tramo que el informe eligió después de mirar la curva"></canvas>
            </div>
          </div>
        </div>
        <div class="simulador-lectura"></div>
      </div>

      <p>Y este es el informe, citado <strong>literal</strong>:</p>

      <div class="cita-ia" data-informe="t4"></div>

""" + tarea(4, 8, "El borde y la banda",
       "Las dos mitades, y las dos son de refutación:",
       ["<strong>El borde.</strong> Calcula \(K\) con corrección de traslación y sin corregir, "
        "en tu localidad y en la de contraste, y da el <strong>déficit</strong> de la versión sin "
        "corregir en un \(r\) que declares. <strong>¿Cuál de las dos ventanas sufre más, y por "
        "cuánto?</strong> (Con dos correcciones basta: no calcules las tres.)",
        "Da el cociente <strong>perímetro/área</strong> de las dos ventanas y ponlo al lado de los "
        "dos déficits. <strong>¿Por qué ese cociente predice cuál de las dos sufre más?</strong> "
        "Contesta con lo que le pasa a un punto cualquiera de cada ventana, no con la correlación "
        "entre las dos columnas.",
        "<strong>La banda.</strong> El informe restringe \(r\) a un tramo y da un p-valor. Di por "
        "qué <strong>ese p-valor no es un p-valor</strong>. La respuesta tiene que nombrar "
        "<em>cuándo</em> se eligió el tramo.",
        "Cuenta cuántos nodos se salen de la banda en <strong>todo</strong> el rango y da el "
        "porcentaje. Con una banda puntual al 5&nbsp;%, ¿cuántos esperarías si el patrón fuera "
        "CSR? Compara las dos cifras — y después explica por qué <strong>tu recuento tampoco "
        "decide</strong>: qué haría falta suponer sobre los nodos para que el 5&nbsp;% fuera el "
        "listón, y por qué \(K\) no lo cumple.",
        "La envolvente simula CSR. De las <strong>dos</strong> propiedades que definen CSR, ¿cuál "
        "está usando <code>envelope()</code> al generar cada réplica con el mismo \(n\) que el "
        "patrón observado, y cuál está dando por buena <strong>sin comprobarla</strong>?"],
       "Para (a) y (b): que el sesgo va siempre en la misma dirección ya lo trabajaste en el "
       "ejercicio 5 del capítulo, así que aquí no se pregunta. Lo que aquí se pregunta es por qué "
       "las dos ventanas no lo sufren igual — piensa en un punto pegado al borde y en uno del "
       "centro, y en qué proporción de cada ventana está «pegada al borde». Para (c), la pregunta "
       "no es si el tramo es raro: es en qué orden ocurrieron mirar y elegir, y decir solo que «no "
       "es un p-valor» no es responderla. Y para (d), fíjate en que \(K\) es acumulada: lo que "
       "pasa en un nodo no es independiente de lo que pasa en el siguiente.") + f"""
      <div class="note">
        <p style="margin-bottom:0;"><strong>Dónde está esto en el capítulo, y qué NO se repite.</strong>
          El efecto de borde es el módulo 10 y las envolventes el 11. El ejercicio guiado 5 del
          capítulo ya te hizo calcular las tres correcciones y explicar por qué el sesgo tiene
          siempre el mismo signo: <em>eso no se vuelve a preguntar aquí</em>. Lo que aquí se
          pregunta es por qué dos ventanas distintas lo sufren de forma distinta, que es la forma
          de la ventana y no aparece en ningún ejercicio. Y el ejercicio 4 restringe el rango de
          \(r\) <strong>declarándolo de antemano</strong>; el informe de abajo lo restringe
          <strong>después de mirar</strong>, y esa es toda la diferencia.</p>
      </div>

      <div class="note">
        <p style="margin-bottom:0;"><strong>El bloque de abajo resuelve la primera mitad.</strong>
          La segunda no lleva código: la envolvente y su banda están publicadas arriba y en el
          código fuente de esta página, y contar nodos fuera de banda es contar.</p>
      </div>

{tabs('El sesgo de borde en dos ventanas de forma opuesta',
      '''library(sf)
library(spatstat.geom)
library(spatstat.explore)

loc &lt;- st_read("datos/taller2_localidades.gpkg", quiet = TRUE)
sed &lt;- st_read("datos/taller2_sedes.gpkg",       quiet = TRUE)
xy  &lt;- st_coordinates(sed)

# El deficit de K sin corregir, y la forma de la ventana, en una sola
# funcion para poder llamarla dos veces sin copiar nada.
mide &lt;- function(nombre, r_ref = 1000) {
  mia &lt;- loc[loc$localidad == nombre, ]
  stopifnot(nrow(mia) == 1)
  p   &lt;- ppp(xy[, 1], xy[, 2], window = as.owin(st_union(mia)))
  rg  &lt;- seq(0, 2000, by = 50)
  kn  &lt;- Kest(p, correction = "none",      r = rg)   # sin corregir
  kt  &lt;- Kest(p, correction = "translate",  r = rg)   # corregida
  i   &lt;- which(rg == r_ref)
  per &lt;- as.numeric(st_length(st_cast(st_geometry(mia), "MULTILINESTRING"))) / 1000
  are &lt;- as.numeric(st_area(mia)) / 1e6
  c(n = npoints(p), deficit_pct = 100 * (1 - kn$un[i] / kt$trans[i]),
    perimetro_area = per / are)
}

# Los dos nombres son un EJEMPLO: cambialos por los tuyos. El buscador
# te da los dos, y la pareja de cada quien es distinta.
rbind(propia    = mide("Suba"),            # <-- tu localidad
      contraste = mide("Antonio Narino"))  # <-- la de contraste''',
      '''import geopandas as gpd, numpy as np

loc = gpd.read_file("datos/taller2_localidades.gpkg")
sed = gpd.read_file("datos/taller2_sedes.gpkg")

# Python no tiene Kest, asi que la correccion de traslacion hay que
# escribirla. Para una ventana POLIGONAL el peso ya no es el producto de
# dos lados: es el area de solape del poligono consigo mismo desplazado.
def K_dos(nombre, r_ref=1000.0):
    mia = loc[loc.localidad == nombre].geometry.union_all()
    pts = sed[sed.geometry.covered_by(mia)]
    x = pts.geometry.x.to_numpy(); y = pts.geometry.y.to_numpy()
    n = len(x); A = mia.area
    dx = x[:, None] - x[None, :]; dy = y[:, None] - y[None, :]
    d = np.hypot(dx, dy)
    m = ~np.eye(n, dtype=bool)
    cerca = m &amp; (d &lt;= r_ref)
    sin = A * cerca.sum() / (n * (n - 1))          # sin corregir
    # El peso de traslacion, poligono a poligono. Son pocos pares: solo
    # los que estan a menos de r_ref, y sobre esos se paga el solape.
    from shapely import affinity
    ii, jj = np.where(cerca)
    peso = np.array([mia.intersection(
        affinity.translate(mia, float(dx[a, b]), float(dy[a, b]))).area
        for a, b in zip(ii, jj)])
    con = A * A * np.sum(1 / peso) / (n * (n - 1) * A)
    per = mia.exterior.length if mia.geom_type == "Polygon" else mia.length
    return dict(n=n, deficit_pct=100 * (1 - sin / con),
                perimetro_area=(per / 1000) / (A / 1e6))

# Los dos nombres son un EJEMPLO: cambialos por los tuyos.
print(K_dos("Suba"))              # <-- tu localidad
print(K_dos("Antonio Narino"))    # <-- la de contraste''')}
""" + CIERRE


# =====================================================================
# MÓDULO 6 · T5 · El mismo problema con otro mando
# =====================================================================
# El taller NO publica ninguna superficie de KDE: el capítulo 5 midió
# 39,8 KB por superficie y dieciséis serían 640 KB (C2). Se publica el σ y
# lo que el informe afirma, y la superficie la calcula el estudiante.
#
# LA REJILLA VA FIJADA EN EL BLOQUE DE CÓDIGO, y hace falta: tanto el
# recuento de componentes conexas como el cociente pico/media dependen del
# ráster. `dimyx = 256` es la MISMA constante que usa el precálculo —el
# `DIMYX` de `genera_taller2.R`—, y que lo sea no es cosmético: mientras
# el precálculo estuvo en 80 y este bloque en 256, quince de los dieciséis
# cocientes publicados no cuadraban a los dos decimales con que el informe
# los cita, y el estudiante que siguiera el bloque al pie de la letra
# encontraba una discrepancia que el enunciado le decía que no existía.
# Es M-18 del plan, cerrada el 2026-09-10. Con las dos en 256, los
# dieciséis cocientes y los dieciséis recuentos se reproducen exactos, y
# `verifica_taller2.R` lo comprueba en cada pasada.
#
# El instrumento de la tarea sigue siendo el cociente pico/media —que es
# lo que M-9 decidió—: es continuo y separa los cuatro selectores en las
# dieciséis, mientras que el entero de los focos empata a menudo.
MOD6 = cabecera(
    6, "El mismo problema con otro mando", "T5 · The bandwidth",
    "Reconocer la misma decisión bajo otro nombre, y sostener una elección "
    "ante quien va a usarla. Vale el 8 % del taller.") + variante() + f"""
      <p>Llevas tres capítulos encontrándote la misma pregunta con tres nombres. En el capítulo 3
        era el tamaño de la unidad; en el módulo 6 del capítulo 4, el tamaño del cuadrante —el que
        elegiste tú en <strong>T1</strong>—; y ahora es el <strong>ancho de banda</strong> de una
        estimación por núcleos. Esta tarea es la única que sale del capítulo 4, y se queda en los
        <strong>tres primeros módulos</strong> del capítulo 5.</p>

      <p>Alguien mandó a la Secretaría de Educación un informe sobre <strong>tu</strong> localidad.
        Se cita <strong>literal</strong>:</p>

      <div class="cita-ia" data-informe="t5"></div>

      <div class="definition">
        <h3>Qué es «un foco», exactamente</h3>
        <p>Sin una definición no hay nada que contar, así que el informe declara la suya y tú usas
          <strong>la misma</strong>: un foco es una <strong>componente conexa</strong> de la región
          donde la intensidad estimada supera <strong>el doble de la intensidad media</strong> de la
          superficie.</p>
        <p style="margin-bottom:0;">Es una definición razonable y es arbitraria, las dos cosas a la
          vez. Y el entero que produce <strong>depende de la rejilla</strong> sobre la que dibujes
          la superficie, así que el bloque de código de abajo <em>fija la rejilla</em>: úsala tal
          cual, y si aun así tu recuento no coincide con el del informe, eso es parte de lo que
          tienes que contar en (a).</p>
      </div>

      <p>El taller <strong>no publica ninguna superficie</strong>: publica el σ y lo que se afirma
        con él. El mapa lo haces tú, que es de lo que va la tarea.</p>

""" + tarea(5, 8, "El mismo problema con otro mando",
       "Sobre tu localidad, con el σ del informe y con los cuatro selectores:",
       ["<strong>Reproduce el mapa</strong> con el σ del informe y la rejilla del bloque. "
        "¿Cuántos focos cuentas con la definición de arriba, y cuánto vale tu cociente "
        "<strong>pico/media</strong>? Las dos cifras tienen que darte <em>exactamente</em> las "
        "del informe: si no te dan, algo cambiaste respecto del bloque —y lo más probable es "
        "que sea la rejilla—. Di qué fue, y de paso ya tienes media respuesta a (c).",
        "Vuelve a estimar con los <strong>cuatro selectores</strong> del módulo 3 del capítulo 5. "
        "Da los cuatro σ, y cuánto se mueve el cociente pico/media entre ellos —el factor entre el "
        "mayor y el menor—. <strong>¿La afirmación del informe sobrevive a alguno de los "
        "cuatro?</strong>",
        "En T1 elegiste una rejilla y aquí un ancho. <strong>¿Cuál de las dos decisiones movió más "
        "tu conclusión</strong>, y por qué son <strong>la misma decisión</strong> con dos nombres? "
        "Cita tus dos cifras, las de T1 y las de aquí.",
        "Elige el σ que <strong>defenderías ante la Secretaría de Educación</strong> y sostén la "
        "elección. «El que da <code>bw.diggle</code>» no puntúa si no dices <em>qué optimiza</em> "
        "ese selector y por qué eso es lo que le conviene a esta pregunta."],
       "El informe no miente en su cuenta: con su σ, esos focos están ahí. La pregunta es si "
       "habría escrito lo mismo con otro ancho igual de defendible — y quién decidió que ese ancho "
       "fuera el suyo. Para (c), lo que tienen en común la rejilla y el ancho es que las dos "
       "fijan <strong>a qué escala</strong> se está mirando, y ninguna de las dos sale del dato. "
       "Para (d), cada selector optimiza una cosa distinta y ninguno optimiza «tener razón».") + f"""
      <div class="note">
        <p style="margin-bottom:0;"><strong>La rejilla del bloque no es decorativa.</strong>
          <code>dimyx</code> fija cuántos píxeles tiene la superficie, y de eso dependen
          <strong>las dos</strong> cifras que se te piden: el recuento de focos y el cociente
          pico/media. Con la rejilla del bloque reproduces el informe exactamente; si la cambias,
          cambia tu respuesta a (a) — y ese es, por cierto, un <strong>tercer mando</strong> de la
          misma familia, que nadie te ha pedido que declares y que también decide lo que ves.</p>
      </div>

{tabs('La intensidad por núcleos, los focos y los cuatro selectores',
      '''library(sf)
library(spatstat.geom)
library(spatstat.explore)

MI_LOCALIDAD &lt;- ""      # el nombre EXACTO del buscador
MI_SIGMA     &lt;- 0       # el sigma del informe, en metros

loc &lt;- st_read("datos/taller2_localidades.gpkg", quiet = TRUE)
sed &lt;- st_read("datos/taller2_sedes.gpkg",       quiet = TRUE)
mia &lt;- loc[loc$localidad == MI_LOCALIDAD, ]
stopifnot(nrow(mia) == 1, MI_SIGMA &gt; 0)
xy  &lt;- st_coordinates(sed)
p   &lt;- ppp(xy[, 1], xy[, 2], window = as.owin(st_union(mia)))

# ppp() SELECCIONA tus sedes descartando las de fuera —es lo mismo que
# hiciste en T1—, pero se GUARDA las descartadas y plot() las dibuja
# encima. Sin esta linea el mapa sale con las sedes del resto de Bogota
# sembradas alrededor de tu localidad, y con un aviso que parece un error.
attr(p, "rejects") &lt;- NULL

# La superficie, con la rejilla FIJADA. No la cambies para (a).
focos &lt;- function(sigma) {
  d  &lt;- density(p, sigma = sigma, dimyx = 256)
  m  &lt;- mean(d)                                 # la intensidad media
  ss &lt;- solutionset(d &gt; 2 * m)                  # la region por encima del umbral
  # LA GUARDA NO ES ADORNO. Si NINGUN pixel supera el doble de la media
  # —que pasa con varios de los cuatro selectores de (b), cuando el ancho
  # es tan grande que aplana la superficie— esa region es VACIA, y
  # connected() sobre una region vacia devuelve una imagen con UN nivel.
  # Sin esta linea saldria "focos = 1" donde no hay ninguno, sin avisar.
  # Cero focos es una respuesta, y en (b) es de las mas fuertes.
  nf &lt;- if (is.empty(ss)) 0L else length(levels(connected(ss)))
  c(sigma = sigma, pico_media = max(d) / m, focos = nf)
}

d &lt;- density(p, sigma = MI_SIGMA, dimyx = 256)
plot(d, main = MI_LOCALIDAD); plot(p, add = TRUE, pch = 20, cex = 0.4)
focos(MI_SIGMA)

# Los cuatro selectores del modulo 3. bw.scott devuelve DOS anchos, uno
# por eje —el modulo 3 del capitulo 5 explica por que— y aqui se toma el
# primero. unname() para que la columna se llame "scott" y no
# "scott.sigma.x".
sel &lt;- c(diggle = bw.diggle(p), ppl = bw.ppl(p),
         CvL = bw.CvL(p), scott = unname(bw.scott(p)[1]))
round(sel)
t(sapply(sel, focos))''',
      '''import geopandas as gpd, numpy as np
from scipy.ndimage import gaussian_filter, label

MI_LOCALIDAD = ""       # el nombre EXACTO del buscador
MI_SIGMA = 0            # el sigma del informe, en metros

loc = gpd.read_file("datos/taller2_localidades.gpkg")
sed = gpd.read_file("datos/taller2_sedes.gpkg")
mia = loc[loc.localidad == MI_LOCALIDAD].geometry.union_all()
pts = sed[sed.geometry.covered_by(mia)]
assert len(pts) and MI_SIGMA &gt; 0

# La misma rejilla de 256, y la ventana como MASCARA: fuera del poligono
# no hay superficie, y contar focos sobre el rectangulo entero seria
# contar sobre una ventana que no es la tuya (que es T1 otra vez).
x0, y0, x1, y1 = mia.bounds
nx = ny = 256
gx = np.linspace(x0, x1, nx); gy = np.linspace(y0, y1, ny)
paso = (x1 - x0) / (nx - 1)
rej = np.zeros((ny, nx))
ix = np.clip(((pts.geometry.x - x0) / paso).astype(int), 0, nx - 1)
iy = np.clip(((pts.geometry.y - y0) / paso).astype(int), 0, ny - 1)
np.add.at(rej, (iy, ix), 1.0)

from shapely.geometry import Point
dentro = np.array([[mia.covers(Point(a, b)) for a in gx] for b in gy])
sup = gaussian_filter(rej, MI_SIGMA / paso) / paso ** 2
sup[~dentro] = np.nan

m = np.nanmean(sup)
print("pico/media =", float(np.nanmax(sup) / m))
etiq, n_focos = label(np.nan_to_num(sup) &gt; 2 * m)
print("focos =", int(n_focos))

# AVISO: esto NO es density.ppp. No corrige el borde, y cerca del limite
# se queda corta — que es justo lo que mide el ejercicio e2 del capitulo
# 5. Sirve para ver el mapa; para las cifras que entregues, usa R.''')}
""" + CIERRE


# =====================================================================
# C6 · El banco de la defensa y el catálogo de refutaciones
# =====================================================================
# TREINTA Y SEIS, y el número no es redondo por gusto: es 12 × 3, que es
# lo que exige el sorteo SIN REEMPLAZO del §4.5. Con una sola sesión nadie
# sale del aula, así que el duodécimo ha oído las preguntas de los once
# anteriores; con 36 = 12 × 3 el banco se agota exactamente al terminar y
# a nadie le repiten una pregunta que ya se oyó.
#
# EL REPARTO POR MÓDULO ES EL DEL §4.2: seis del módulo 4 y tres de cada
# uno de los otros diez. El módulo 4 va sobre-representado porque es el
# único que el escrito apenas toca (§3.6) — es el más conceptual, el más
# fácil de responder con una frase memorizada y el que mejor se evalúa en
# vivo. El ensamblador comprueba el reparto y PARA si no cuadra.
#
# CADA UNA COTEJADA CONTRA LAS DOS SUPERFICIES PUBLICADAS, que es la regla
# del §3.7 y la que este plan ya se saltó dos veces: las 12 preguntas de
# autoevaluación del capítulo 4 Y sus 5 ejercicios guiados. Y con la
# ampliación que trajo C5b: se coteja LA PREGUNTA, no el procedimiento —
# T4(a) pasó el cotejo del §3.5 mirando el procedimiento y preguntaba
# literalmente lo mismo que el ejercicio 5.
#
# Lo que quedó fuera por ese cotejo, y conviene que esté escrito para que
# no vuelva a entrar:
#   · «¿qué distingue G de F?» ................. es la pregunta 7
#   · «¿cuáles son las dos propiedades de CSR?» . es la pregunta 5
#   · «¿por qué K sigue por encima si la agregación es a 20 m?» . la 9
#   · «¿en qué dirección empuja el sesgo de borde y por qué siempre en la
#     misma?» .................................. es el ejercicio 5
#   · «cuenta las celdas con esperanza < 5 sobre Bogotá» .. el ejercicio 3
#   · «de 39 a 999 simulaciones, ¿qué le pasa a la banda?» . la 12
#
# NINGUNA CIFRA DEL CAPÍTULO. El §0 del plan lo pide en su punto 4: este
# taller calcula lo suyo desde las fuentes y no reutiliza cifras de otros
# documentos, para que regenerar el capítulo 4 no lo invalide. Las 36 son
# conceptuales por esa razón además de por ser orales.
BANCO_DEFENSA = [
    # --- Módulo 1 · Qué es un proceso puntual ------------------------
    (1, "La ventana es parte del estimador",
     "En los tres capítulos anteriores el dato traía su sitio puesto y lo que variaba era el "
     "valor. Aquí se invierte. Di qué es exactamente lo aleatorio en un patrón puntual, y qué "
     "cosa de los capítulos anteriores deja de existir cuando se invierte."),
    (1, "Coordenadas sin ventana",
     "Alguien te entrega las coordenadas de un patrón y nada más. ¿Qué no puedes calcular "
     "todavía, y por qué no basta con dibujar un rectángulo alrededor de los puntos?"),
    (1, "Del punto al área",
     "Un mismo fenómeno se puede estudiar como patrón puntual o agregado a unidades areales. "
     "¿Qué se pierde al pasar del primero al segundo, y qué se gana?"),

    # --- Módulo 2 · La intensidad λ ----------------------------------
    (2, "Cuándo describe λ al patrón",
     "El estimador de λ es una división. ¿Bajo qué condición ese único número describe el "
     "patrón, y cómo comprobarías si se cumple sin correr ningún test?"),
    (2, "El índice de dispersión que no vale 1",
     "«Bajo Poisson el índice de dispersión vale 1» es falso en cuanto las celdas no miden lo "
     "mismo. Explica por qué, y di contra qué habría que compararlo en su lugar."),
    (2, "Inhomogénea no es agregada",
     "Que λ dependa de la posición y que los puntos se atraigan producen mapas parecidos y son "
     "cosas distintas. Explica la diferencia y di por qué se confunden tanto."),

    # --- Módulo 3 · Los tres regímenes -------------------------------
    (3, "Qué mecanismo produce cada régimen",
     "Los tres regímenes son aleatorio, regular y agregado. Di qué mecanismo físico produce "
     "cada uno, y por qué «regular» no quiere decir «ordenado en cuadrícula»."),
    (3, "De dónde sale el denominador",
     "Clark-Evans divide la distancia media observada al vecino más próximo por la que daría el "
     "azar. ¿De dónde sale ese denominador, y qué tendría que pasar para que la división dejara "
     "de ser informativa?"),
    (3, "Agregado aquí, regular allá",
     "Un patrón puede estar agregado a una escala y ser regular a otra. ¿Qué le pasa entonces al "
     "índice de Clark-Evans, y qué habría que medir para verlo?"),

    # --- Módulo 4 · CSR · seis, por el §3.6 --------------------------
    (4, "Dos realizaciones, dos n",
     "Dos realizaciones del mismo proceso de Poisson homogéneo no tienen el mismo número de "
     "puntos. ¿Por qué, y qué error comete quien espera que sí?"),
    (4, "La firma de Poisson",
     "Que la media y la varianza del número de puntos valgan aproximadamente lo mismo es la "
     "firma de Poisson. ¿Por qué ninguna otra distribución de conteos hace eso, y cómo lo "
     "comprobarías simulando?"),
    (4, "Cuánto se mueve el azar",
     "Sobre realizaciones de CSR puro, el índice de Clark-Evans recorre un intervalo ancho y su "
     "media no cae exactamente en 1. Son dos hechos distintos: explica cada uno."),
    (4, "Una nula que casi nunca es cierta",
     "CSR es la hipótesis nula de casi todo el capítulo, y en datos reales casi nunca se "
     "cumple. ¿Por qué se usa igual como referencia? ¿Qué se gana?"),
    (4, "Qué falla cuando falla",
     "Rechazar CSR no dice cuál de sus dos propiedades falla. Describe un patrón concreto donde "
     "falle una y otro donde falle la otra, y di cómo los distinguirías."),
    (4, "«Se ve aleatorio»",
     "Un colega mira un mapa y dice que el patrón «se ve aleatorio». ¿Por qué eso no es un "
     "argumento, y qué es lo mínimo que habría que enseñar para convertirlo en uno?"),

    # --- Módulo 5 · El test de cuadrantes ----------------------------
    (5, "Contra qué se contrasta",
     "La hipótesis nula del test de cuadrantes no es «λ es constante». ¿Cuál es, y por qué esa "
     "diferencia cambia lo que puedes afirmar cuando rechazas?"),
    (5, "Los esperados de una celda recortada",
     "Cuando la ventana recorta las celdas, los esperados dejan de ser iguales entre sí. ¿De "
     "dónde salen entonces, y qué pasaría si los repartieras por igual de todos modos?"),
    (5, "El convenio del binado",
     "El binado de <code>quadratcount</code> es el de <code>cut()</code>: abierto por la "
     "izquierda, con el más bajo cerrado por los dos lados. ¿Por qué ese convenio puede mover "
     "el χ², y en qué clase de datos lo mueve más?"),

    # --- Módulo 6 · El tamaño del cuadrante --------------------------
    (6, "Resolver contra suponer",
     "«La escala que más resuelve es la que rompe el supuesto.» Explica esa tensión y di qué "
     "hace con ella un analista honesto."),
    (6, "El MAUP con otro nombre",
     "El tamaño del cuadrante y el tamaño de la unidad areal del capítulo 3 son el mismo "
     "problema. Di en qué son el mismo y en qué no."),
    (6, "Qué falta en el pie",
     "¿Qué tiene que aparecer siempre junto al resultado de un test de cuadrantes para que sea "
     "reproducible, y por qué sin eso el resultado está incompleto?"),

    # --- Módulo 7 · Las funciones G y F ------------------------------
    (7, "Las dos y el borde",
     "G y F se estiman sobre una ventana finita, así que las dos sufren el efecto de borde. "
     "¿Lo sufren igual? Di cuál se ve más afectada y por qué."),
    (7, "Los sitios de F",
     "F se mide desde sitios cualesquiera de la ventana. ¿Cómo se eligen esos sitios en la "
     "práctica, y qué decisión del analista se esconde ahí?"),
    (7, "Misma G, distinta F",
     "Dos patrones tienen la misma G y distinta F. ¿Qué sabes de ellos? ¿Y si tuvieran la misma "
     "F y distinta G?"),

    # --- Módulo 8 · La función K de Ripley ---------------------------
    (8, "Por qué se divide por λ",
     "K(r) es el número esperado de vecinos a distancia r o menos de un punto cualquiera, "
     "dividido por la intensidad. ¿Por qué se divide por la intensidad, y qué se consigue?"),
    (8, "La recta de Besag",
     "La transformación de Besag convierte una parábola en una recta. Si la información es la "
     "misma, ¿por qué importa para leer la curva?"),
    (8, "Los pesos del estimador",
     "El estimador de K lleva unos pesos que multiplican cada pareja de puntos. ¿Qué papel "
     "juegan, y qué estarías estimando si todos valieran 1?"),

    # --- Módulo 9 · La correlación de pares g(r) ---------------------
    (9, "El anillo y el disco",
     "g(r) mira el anillo de radio r y K(r) el disco entero. ¿Qué gana g con eso, y qué pierde?"),
    (9, "La distancia a la que g vuelve a 1",
     "La distancia a la que g regresa a 1 se lee como una propiedad física del patrón. ¿Cuál "
     "es, y qué tendrías que ver en el mapa para confirmarla?"),
    (9, "Un máximo en el borde izquierdo",
     "En un patrón real, g puede no tener pico y alcanzar su máximo en el primer nodo del "
     "barrido. ¿Qué significa eso, y por qué NO es una escala característica?"),

    # --- Módulo 10 · Efectos de borde --------------------------------
    (10, "Lo que cuesta corregir",
     "Las tres correcciones clásicas corrigen, y no cuestan lo mismo. ¿Cuál es la cara, por qué "
     "lo es, y en qué clase de ventana se nota la diferencia?"),
    (10, "Descartar o pesar",
     "La corrección de borde descarta puntos y la de traslación los pesa. ¿Qué le pasa a la "
     "precisión del estimador con cada una, y por qué?"),
    (10, "Por qué crece con r",
     "El efecto de borde no pesa igual a todas las distancias. Explica qué fracción de los "
     "discos toca el borde a r pequeño y a r grande, y qué se sigue de ahí."),

    # --- Módulo 11 · Envolventes de simulación -----------------------
    (11, "Las simulaciones contra su propia banda",
     "Construyes una banda con simulaciones de CSR y después compruebas cuántas de esas MISMAS "
     "simulaciones se salen de ella en algún r. ¿Qué esperarías encontrar, y por qué?"),
    (11, "Dos resúmenes de la misma curva",
     "Un test de desviación global resume la curva entera en un número antes de compararla. Di "
     "qué resumen usa el dclf y cuál el MAD, y ante qué clase de desviación se separan."),
    (11, "Simular con la misma ventana",
     "La envolvente simula CSR con la misma ventana y la misma intensidad que el patrón "
     "observado. ¿Por qué las dos cosas tienen que ser las mismas? ¿Qué pasaría si simularas "
     "sobre un rectángulo?"),
]

# LAS DOCE AFIRMACIONES FALSAS, una por estudiante. Doce y no una: con
# sesión única, repetir la refutación se la regala al que defiende al
# final (§4.5).
#
# CADA UNA ES FALSA DE FORMA VERIFICABLE CON EL MATERIAL, no discutible.
# Ese es el criterio de aceptación, y descartó dos candidatas que parecían
# buenas: «si g vale 1 en todo r el patrón es CSR» —cierto que no basta,
# pero el capítulo no da con qué demostrarlo— y «G y F son deducibles una
# de la otra», que exige un contraejemplo que el material no trae.
#
# SE PUBLICAN, y es una decisión que el plan no tomaba. Va declarada en
# el §0. La razón: lo que el §4.5 quiere evitar es que el duodécimo tenga
# ventaja sobre el primero, y eso lo resuelven las DOCE distintas, no el
# secreto. Y publicarlas es coherente con el banco, que se publica «a
# propósito: no se trata de sorprenderte, se trata de que llegues
# sabiendo». Si Javier prefiere que no viajen, se retira este bloque del
# módulo 7 y el catálogo se queda en la lista de `salidas/`.
# SEIS DE LAS DOCE PRIMERAS SE CAYERON AL RELEERLAS, y las razones valen
# más que las afirmaciones:
#   · «dos realizaciones de CSR tienen el mismo n» y «el índice de
#     dispersión vale 1 siempre» eran, palabra por palabra, dos preguntas
#     de este mismo banco. Al mismo estudiante le podían tocar las dos.
#   · «L − r por encima de cero significa agregación a esa distancia» es
#     LO QUE AFIRMA EL INFORME DE T3. Publicarla aquí es publicar la
#     respuesta de una tarea del escrito.
#   · «cambiar la ventana cambia λ pero no el veredicto» era peor: además
#     de rozar T1, NO ES FALSA para la mayoría. Medido en M-2: el
#     veredicto vuelca en 3 de las 16 localidades y en las otras 13 el
#     enunciado literalmente se cumple. Una afirmación «falsa» que resulta
#     cierta para tres cuartas partes del curso no es una refutación, es
#     una trampa.
#   · «se sale de la banda en algún r, luego p < 0,05» es la pregunta 11
#     del capítulo y además el error del informe de T4.
#   · «Clark-Evans vale exactamente 1 si el patrón es aleatorio» es la
#     pregunta 4 de este banco.
AFIRMACIONES_FALSAS = [
    (5, "El test de cuadrantes contrasta la hipótesis de que λ es constante."),
    (11, "La banda de una envolvente es un intervalo de confianza para la K verdadera del "
         "patrón observado."),
    (4, "Si un patrón no rechaza el test de cuadrantes, se puede concluir que es CSR."),
    (10, "Ignorar la corrección de borde le añade ruido a la estimación de K, pero no la sesga."),
    (2, "El estimador n/|W| devuelve la intensidad en las unidades del fenómeno, sea cual sea "
        "el sistema de coordenadas."),
    (7, "F(r) se calcula sobre los puntos del patrón, igual que G(r), pero midiendo hacia atrás."),
    (8, "La transformación de Besag no es solo un cambio de forma: L detecta estructura que K "
        "no llega a ver."),
    (10, "Las tres correcciones de borde devuelven la misma curva K; solo se diferencian en el "
         "tiempo de cómputo."),
    (1, "En un patrón puntual el dato es la posición, así que los mismos puntos observados en "
        "dos ventanas distintas son el mismo patrón."),
    (6, "El tamaño de la celda del test de cuadrantes es un detalle de implementación: el "
        "veredicto no depende de él."),
    (9, "El máximo de g(r) señala el tamaño de los grumos del patrón."),
    (3, "El índice de Clark-Evans mira todas las escalas del patrón a la vez."),
]

_banco = "\n".join(
    f"""          <tr><th scope="row">{i + 1}</th><td>{m}</td><td>{tema}</td><td>{preg}</td></tr>"""
    for i, (m, tema, preg) in enumerate(BANCO_DEFENSA))

_falsas = "\n".join(
    f"""          <tr><th scope="row">{i + 1}</th><td>{m}</td><td>{af}</td></tr>"""
    for i, (m, af) in enumerate(AFIRMACIONES_FALSAS))


# =====================================================================
# MÓDULO 7 · Cómo se califica, y la defensa
# =====================================================================
# Las dos rúbricas se publican DENTRO del taller, con el mismo detalle. La
# de la defensa no es un adorno: con el 60 % del peso, publicarla con
# menos detalle que la del escrito sería calificar a ciegas el instrumento
# que más pesa. El banco de 36 preguntas y las 12 afirmaciones falsas
# llegan en C6.
n_banco, n_falsas = len(BANCO_DEFENSA), len(AFIRMACIONES_FALSAS)

MOD7 = cabecera(
    7, "Cómo se califica, y la defensa", "Rubrics and the oral defence",
    "Nada. Este módulo no se califica: dice cómo se califica todo lo "
    "demás, y conviene leerlo antes de escribir.") + f"""
      <p>El taller tiene <strong>dos instrumentos</strong> y los dos se califican con rúbrica
        publicada: el <strong>escrito</strong>, que vale el 40&nbsp;%, y la <strong>sustentación
        oral</strong>, que vale el 60&nbsp;%. Las dos rúbricas están aquí abajo. Pulsa cualquier
        criterio para ver sus cuatro niveles.</p>

      <h3>La rúbrica del escrito · 40&nbsp;%</h3>

      <div class="rubrica" data-rubrica="taller2-escrito"></div>

      <h3>La rúbrica de la sustentación · 60&nbsp;%</h3>

      <p>La sustentación es el <strong>{SUSTENTACION}</strong>, presencial y en el espacio de la
        clase, en una sola sesión, y son
        <strong>siete minutos</strong> por persona. No es una confirmación del escrito: es el
        instrumento que más pesa, y por eso su rúbrica se publica con el mismo detalle.</p>

      <div class="rubrica" data-rubrica="taller2-defensa"></div>

      <div class="note">
        <p><strong>Cómo se sortean las preguntas del banco, y por qué así.</strong> El banco tiene
          <strong>{n_banco}</strong> preguntas y son doce estudiantes a tres preguntas cada uno:
          12 × 3 = {n_banco}. El sorteo es <strong>sin reemplazo</strong> y se hace <em>antes</em> de
          la sesión, no durante. Eso significa que <strong>a nadie le repiten una pregunta que ya se
          oyó</strong>, y que el orden en que te toque defender no te da ventaja ni te la quita. La
          refutación en vivo funciona igual: hay <strong>{n_falsas} afirmaciones falsas
          distintas</strong>, una por persona.</p>
        <p style="margin-bottom:0;">Las dos listas se publican <strong>con este enunciado</strong>,
          enteras. No hay preguntas sorpresa: hay {n_banco} preguntas y {n_falsas} afirmaciones que
          puedes preparar, y de ellas te tocan tres y una. Que estén publicadas no las hace fáciles:
          casi todas piden un <em>mecanismo</em>, y un mecanismo no se memoriza en la fila.</p>
      </div>

      <h3>El banco de la defensa · {n_banco} preguntas</h3>

      <p>Cubre <strong>los once módulos</strong> del capítulo 4, incluidos los que ninguna tarea del
        escrito toca. El módulo 4 —CSR— va con el doble de preguntas que los demás, y es a propósito:
        es el que el escrito apenas roza y el que mejor se evalúa en voz alta.</p>

      <div class="note">
        <p style="margin-bottom:0;"><strong>Ninguna de estas {n_banco} repite una pregunta de
          autoevaluación ni un ejercicio guiado del capítulo.</strong> Se cotejaron una a una contra
          las dos listas, y varias candidatas se cayeron por eso — entre ellas «¿qué distingue G de
          F?» y «¿cuáles son las dos propiedades de CSR?», que son preguntas del capítulo palabra
          por palabra. Si al prepararte encuentras una que sí se parece a algo ya publicado,
          dilo: es un defecto y se corrige.</p>
      </div>

      <table>
        <caption>El banco de la defensa. Te tocan tres, sorteadas sin reemplazo entre los doce.</caption>
        <thead>
          <tr><th scope="col">#</th><th scope="col">Mód.</th><th scope="col">Tema</th>
              <th scope="col">Pregunta</th></tr>
        </thead>
        <tbody>
{_banco}
        </tbody>
      </table>

      <h3>La refutación en vivo · {n_falsas} afirmaciones falsas</h3>

      <p>En los dos últimos minutos se te lee <strong>una</strong> de estas, y tienes que decir
        <strong>por qué es falsa</strong>. Todas lo son, y todas lo son de forma comprobable con el
        capítulo: no hay ninguna discutible, ninguna que dependa de una convención y ninguna trampa
        de redacción. Decir «es falsa» no puntúa: hay que decir <em>dónde se rompe</em> y, si puedes,
        cómo tendría que estar enunciada para ser cierta.</p>

      <table>
        <caption>El catálogo de refutaciones. Te leen una.</caption>
        <thead>
          <tr><th scope="col">#</th><th scope="col">Mód.</th>
              <th scope="col">Afirmación — todas son FALSAS</th></tr>
        </thead>
        <tbody>
{_falsas}
        </tbody>
      </table>

      <div class="warning">
        <p style="margin-bottom:0;"><strong>La regla que le da dientes a todo lo anterior.</strong>
          Una decisión que entregues por escrito y <strong>no puedas sostener en la
          sustentación</strong> se recalifica. Va aquí, en el enunciado, y no en un correo: es lo
          que hace que valga la pena entender lo que entregas, y es la razón por la que el reparto
          es 40/60 y no al revés.</p>
      </div>

      <div class="note">
        <p style="margin-bottom:0;"><strong>Qué se entrega, otra vez y en corto.</strong> Un PDF, el
          <strong>{ENTREGA}, a más tardar a las {HORA_LIMITE}</strong>, con la <strong>línea de
          identificación</strong> copiada literal en la portada y la <strong>bitácora</strong> de
          media página. Sin cualquiera de las dos, la entrega está incompleta. Y en una clase de
          {CONTROL} traes cinco cosas en voz alta: tu localidad, tu <em>n</em> y tu λ, tu patrón y
          tu trío.</p>
      </div>
""" + CIERRE


# =====================================================================
# El ensamblado
# =====================================================================
MODULOS = MOD1 + MOD2 + MOD3 + MOD4 + MOD5 + MOD6 + MOD7

# La navegación declara SOLO los módulos que existen. Con más módulos
# declarados que escritos, `loadModule()` encontraría `template` nulo y
# dejaría el panel en blanco sin un solo error en consola: es el modo de
# fallo más caro de este motor y el que más tardó en encontrarse en el
# Taller 1.
MODULOS_NAV = [
    ("Cómo se trabaja este taller", "8 min"),
    ("T1 · La ventana que no declaraste", "50 min"),
    ("T2 · El régimen que las dos funciones no ven igual", "45 min"),
    ("T3 · Dónde está la estructura", "45 min"),
    ("T4 · El borde y la banda", "50 min"),
    ("T5 · El mismo problema con otro mando", "45 min"),
    ("Cómo se califica, y la defensa", "12 min"),
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

    // QUÉ NODOS CAEN DENTRO DEL TRAMO DE T4, Y POR QUÉ CON TOLERANCIA.
    // Los dos campos vienen del mismo precálculo y REDONDEADOS DISTINTO:
    // `r` a seis decimales (0.005859) y `tramo` a ocho (0.00585938). Una
    // comparación estricta —`x >= tramo[0] && x <= tramo[1]`— deja fuera
    // el nodo del que se sacó el tramo, y cuando el tramo es UN SOLO nodo
    // se queda vacío: el informe decía «0 de 0 nodos evaluados» y luego
    // concluía que la curva abandona la banda, el panel derecho salía en
    // blanco y la tabla anunciaba un tramo de cero nodos. Le pasaba a las
    // envolventes 3 y 10, que son 168 de las 1000 variantes. Media paso de
    // tolerancia lo arregla y no puede pasarse de largo: la rejilla es
    // uniforme, así que medio paso no alcanza al nodo siguiente.
    // Lo encontró la auditoría de contenido el 2026-09-12, y desde
    // entonces `audita_taller2.py` comprueba el invariante con esta misma
    // regla. NO se sustituya por la comparación estricta.
    const dentroTramoT2 = e => {{
      const paso = (e.r[e.r.length - 1] - e.r[0]) / (e.r.length - 1);
      const lo = e.tramo[0] - paso / 2, hi = e.tramo[1] + paso / 2;
      return e.r.map(x => x >= lo && x <= hi);
    }};

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

    // --- Los informes que las tareas ponen a auditar -------------------
    // Se RENDERIZAN, no se escriben en el ensamblador, y por dos razones.
    // La primera es la regla del material: la premisa del informe de T3
    // cita el último r en que L − r sigue siendo positiva, y ese r es
    // distinto para cada patrón — escrito a mano sería una cifra sin
    // respaldo en el JSON. La segunda es más seria: una premisa falsa
    // hunde la tarea, porque el estudiante refutaría lo que no es. Así
    // cada informe dice una verdad sobre SU variante y saca de ella una
    // conclusión que no se sigue.
    const INFORMES_T2 = {{
      t3: function (r) {{
        const P = DATOS_T2.patrones[r.v.propio - 1];
        let ult = 0;
        for (let i = 0; i < P.r.length; i++) if (P.L[i] > 0) ult = P.r[i];
        return `<p>«He calculado la función K de Ripley y su transformación L sobre el patrón.
          <strong>La curva L − r es positiva hasta r = ${{n5(ult, 3)}}</strong>, de modo que el
          patrón <strong>está agregado hasta esa distancia</strong>. La agregación se extiende, por
          tanto, a lo largo de todo ese rango de escalas.»</p>
          <p style="margin-bottom:0; font-style:italic;">— respuesta de un modelo de lenguaje al que
          se le dieron estas mismas curvas.</p>`;
      }},
      t4: function (r) {{
        // Los dos recuentos se cuentan aquí, sobre las curvas publicadas.
        // La primera versión de este informe decía «en prácticamente
        // todos los nodos» y era FALSA para media docena de las doce
        // envolventes —en la primera son 16 de 159—. Un informe con una
        // premisa falsa hunde la tarea: el estudiante refuta la
        // aritmética y no llega nunca al error, que es de razonamiento.
        const e = DATOS_T2.envolventes[r.v.envolvente - 1];
        const dt = dentroTramoT2(e);          // con tolerancia: ver arriba
        let enTramo = 0, fueraTramo = 0;
        for (let i = 0; i < e.r.length; i++) {{
          if (!dt[i]) continue;
          enTramo++;
          if (e.obs[i] > e.hi[i] || e.obs[i] < e.lo[i]) fueraTramo++;
        }}
        return `<p>«Calculé la envolvente de K con <strong>${{e.nsim}} simulaciones</strong> de CSR
          y examiné el rango <strong>r ∈ [${{n5(e.tramo[0], 4)}}, ${{n5(e.tramo[1], 4)}}]</strong>,
          que es donde la curva observada se separa de la teórica. En ese rango la observada se sale
          de la banda del 95&nbsp;% en <strong>${{fueraTramo}} de ${{enTramo}}</strong>
          ${{enTramo === 1 ? 'nodo evaluado' : 'nodos evaluados'}}. Como la curva abandona la banda del 95&nbsp;%, <strong>el patrón se aparta de
          la aleatoriedad espacial completa con p &lt; 0,05</strong>.»</p>
          <p style="margin-bottom:0; font-style:italic;">— informe recibido junto con la figura de
          arriba.</p>`;
      }},
      t5: function (r) {{
        const t = DATOS_T2.t5[r.v.localidad];
        return `<p>«Estimé la intensidad de las sedes educativas de <strong>${{r.v.localidad}}</strong>
          por el método de núcleos, con un ancho de banda de <strong>σ = ${{t.sigma_informe}}
          metros</strong>. El mapa resultante muestra <strong>${{t.focos_informe}}
          ${{t.focos_informe === 1 ? 'foco' : 'focos'}} de concentración</strong> de oferta
          educativa, con un pico de <strong>${{n5(t.pico_informe, 2)}} veces</strong> la intensidad
          media de la localidad. Recomendamos concentrar la inversión en
          ${{t.focos_informe === 1 ? 'esa zona' : 'esas zonas'}}.»</p>
          <p style="margin-bottom:0; font-style:italic;">— informe entregado a la Secretaría de
          Educación. Un foco es una componente conexa de la región donde la intensidad supera el
          doble de la media.</p>`;
      }}
    }};

    function t2PintaInformes() {{
      const r = t2Resuelve(T2_DOC);
      document.querySelectorAll('[data-informe]').forEach(caja => {{
        const f = INFORMES_T2[caja.dataset.informe];
        caja.innerHTML = (r && f) ? f(r)
          : `<p style="margin:0;">Resuelve tu variante ahí arriba para leer el informe que tienes
             que auditar.</p>`;
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

# Los dos mapas que estrena C5b. Van en su propia constante y no dentro
# de GEOMAPAS_JS para no volver a tocar una cadena que ya estaba probada:
# los dos bloques se concatenan en main().
GEOMAPAS_JS2 = """
    // El patrón propio de T3. Sí lleva título —es «tu patrón», no hay
    // nada que ocultar— y lleva la misma tabla de respaldo: T3(b) pide
    // tres cifras suyas, y quien no ve el lienzo tiene que poder
    // rehacerlas.
    GEOMAPAS['taller2-propio'] = {
      fuente: function () {
        const r = t2Resuelve(T2_DOC);
        if (!r) return null;
        return Object.assign({}, MAPAS_T2.patrones[r.v.propio - 1], {
          leyenda: 'tu patrón generado, en la ventana unidad'
        });
      },
      paleta: 'verde',
      alto: 380,
""" + TABLA_PUNTOS_JS + """,
    };

    // La localidad de CONTRASTE de T4(a). Es un registro aparte y no el
    // mismo con un argumento porque los dos mapas conviven en el mismo
    // módulo: `.geomapa` resuelve su fuente por el id del registro, así
    // que dos vistas distintas a la vez necesitan dos registros.
    GEOMAPAS['taller2-contraste'] = {
      fuente: function () {
        const r = t2Resuelve(T2_DOC);
        if (!r) return null;
        const m = MAPAS_T2.localidades[r.v.contraste];
        if (!m) return null;
        return Object.assign({}, m, { titulo: r.v.contraste });
      },
      get etiqueta() {
        const r = t2Resuelve(T2_DOC);
        if (!r) return 'Mapa sin variante resuelta';
        const L = DATOS_T2.localidades[r.v.contraste];
        return 'El contorno de ' + r.v.contraste + ', la localidad de contraste de T4. '
          + 'Dentro caen ' + L.n + ' sedes educativas y su área es de '
          + n5(L.area_km2, 2) + ' kilómetros cuadrados.';
      },
      paleta: 'verde',
      alto: 340,
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
        // TODO lo que dependa de la variante, de una vez y sin lista: cada
        // simulador del taller deja su repintado en `__t2repinta`, así que
        // añadir uno nuevo no obliga a acordarse de venir aquí. La lista
        // por nombre que había antes es la clase de cosa que se queda a
        // medias en cuanto llegan T3, T4 y T5 — y se queda a medias en
        // silencio, con la ficha resuelta y la curva vieja debajo.
        document.querySelectorAll('.simulador').forEach(s => {
          if (s.__t2repinta) s.__t2repinta();
        });
        t2PintaInformes();
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

      raiz.__t2repinta = pinta;
      campo.addEventListener('input', () => aplica(campo.value));
      campo.value = T2_DOC;
      pinta();
      // Los informes de T3, T4 y T5 viven fuera de cualquier simulador
      // —son citas dentro de la prosa— así que alguien tiene que pintarlos
      // al cargar el módulo. Lo hace la tira, que está en todos.
      t2PintaInformes();
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

      raiz.__t2repinta = pinta;
      pinta();
      return graficos;
    };
"""

# Los dos simuladores que estrena C5b. Igual que los mapas: en su propia
# constante, y se concatenan en main().
SIMULADORES_JS2 = """
    // --- Las tres curvas del patrón propio (T3) -----------------------
    // K contra πr², L − r contra el cero y g contra el uno. Las tres
    // referencias se dibujan como una serie más y no como una anotación:
    // una línea que se puede leer en la leyenda y apagar con un clic es
    // más honesta que una raya pintada sobre el lienzo.
    SIMULADORES['taller2-propio-curvas'] = function (raiz) {
      const lienzos = [...raiz.querySelectorAll('canvas')];
      const lectura = raiz.querySelector('.simulador-lectura');
      const ejes = tit => ({
        scales: {
          x: { title: { display: true, text: 'r' },
               ticks: { maxTicksLimit: 6, font: { family: 'Montserrat', size: 11 } },
               grid: { display: false } },
          y: { title: { display: true, text: tit },
               ticks: { font: { family: 'Fira Code', size: 11 } },
               grid: { color: 'rgba(148, 163, 184, 0.2)' } }
        }
      });
      const serie = (etq, color, guion) => ({
        label: etq, data: [], borderColor: color, backgroundColor: color,
        borderWidth: guion ? 1.6 : 2, pointRadius: 0,
        borderDash: guion ? [5, 3] : undefined
      });
      const graficos = [
        crearGraficoLinea(lienzos[0], [], [serie('K(r)', COLORES_GRAFICO.primario),
          serie('πr² (CSR)', COLORES_GRAFICO.gris, true)], ejes('K')),
        crearGraficoLinea(lienzos[1], [], [serie('L(r) − r', COLORES_GRAFICO.primario),
          serie('cero', COLORES_GRAFICO.gris, true)], ejes('L − r')),
        crearGraficoLinea(lienzos[2], [], [serie('g(r)', COLORES_GRAFICO.secundario),
          serie('uno (CSR)', COLORES_GRAFICO.gris, true)], ejes('g'))
      ];

      function pinta() {
        const r = t2Resuelve(T2_DOC);
        if (!r) {
          graficos.forEach(g => {
            g.data.labels = [];
            g.data.datasets.forEach(ds => { ds.data = []; });
            g.update('none');
          });
          lectura.innerHTML = `<p style="margin:0;">Resuelve tu variante arriba y aquí aparecerán
            las tres curvas de tu patrón.</p>`;
          return;
        }
        const P = DATOS_T2.patrones[r.v.propio - 1];
        const etiquetas = P.r.map(x => n5(x, 3));
        // πr² se calcula aquí porque es la CURVA DE REFERENCIA, no un dato:
        // es la definición de CSR, no una cifra del precálculo. Todo lo
        // que sí es dato —K, L, g— viene del JSON sin tocarlo.
        const teo = P.r.map(x => Math.PI * x * x);
        graficos[0].data.datasets[0].data = P.K;
        graficos[0].data.datasets[1].data = teo;
        graficos[1].data.datasets[0].data = P.L;
        graficos[1].data.datasets[1].data = P.r.map(() => 0);
        graficos[2].data.datasets[0].data = P.g;
        graficos[2].data.datasets[1].data = P.r.map(() => 1);
        const nombres = ['K de tu patrón frente a πr²', 'L menos r de tu patrón frente al cero',
                         'g de tu patrón frente al uno'];
        graficos.forEach((g, i) => {
          g.data.labels = etiquetas;
          g.update('none');
          g.canvas.setAttribute('aria-label', nombres[i] + ', sobre r de ' + etiquetas[0]
            + ' a ' + etiquetas[etiquetas.length - 1]
            + '. Los valores están en la tabla que hay debajo.');
        });

        const paso = 5;
        const filas = [];
        for (let j = 0; j < P.r.length; j += paso) {
          filas.push(`<tr><th scope="row">${n5(P.r[j], 3)}</th>`
            + `<td>${n5(P.K[j], 5)}</td><td>${n5(Math.PI * P.r[j] * P.r[j], 5)}</td>`
            + `<td>${n5(P.L[j], 5)}</td><td>${n5(P.g[j], 3)}</td></tr>`);
        }
        lectura.innerHTML = `<details class="geomapa-tabla"><summary>Ver las curvas en una
          tabla</summary><table><caption>K, su valor bajo CSR, L − r y g de tu patrón, una fila
          de cada ${paso} valores de r.</caption><thead><tr><th scope="col">r</th>
          <th scope="col">K(r)</th><th scope="col">πr²</th><th scope="col">L(r) − r</th>
          <th scope="col">g(r)</th></tr></thead><tbody>${filas.join('')}</tbody></table></details>`;
        envolverTablas();
      }

      raiz.__t2repinta = pinta;
      pinta();
      return graficos;
    };

    // --- La envolvente de T4(b), entera y recortada --------------------
    // Los DOS paneles salen de las MISMAS series. Eso no es una comodidad
    // de programación: es el enunciado. Si el panel recortado se
    // recalculara, el estudiante podría contestar «son análisis
    // distintos» y tendría razón — y la tarea, que pregunta por el orden
    // entre mirar y elegir, se quedaría sin objeto.
    SIMULADORES['taller2-envolvente'] = function (raiz) {
      const lienzos = [...raiz.querySelectorAll('canvas')];
      const lectura = raiz.querySelector('.simulador-lectura');
      const opciones = {
        plugins: {
          legend: { labels: { font: { family: 'Montserrat', size: 11 }, boxWidth: 22,
            filter: item => item.text !== '' } },
          tooltip: { backgroundColor: '#012820', titleFont: { family: 'Montserrat' },
            bodyFont: { family: 'Fira Code' } }
        },
        scales: {
          x: { title: { display: true, text: 'r' },
               ticks: { maxTicksLimit: 6, font: { family: 'Montserrat', size: 11 } },
               grid: { display: false } },
          y: { title: { display: true, text: 'K(r)' },
               ticks: { font: { family: 'Fira Code', size: 11 } },
               grid: { color: 'rgba(148, 163, 184, 0.2)' } }
        }
      };
      const bandas = () => ([
        { label: 'banda de simulación', data: [], borderColor: 'rgba(26,115,88,.35)',
          backgroundColor: 'rgba(124,192,170,.30)', borderWidth: 1, pointRadius: 0, fill: '+1' },
        { label: '', data: [], borderColor: 'rgba(26,115,88,.35)', borderWidth: 1,
          pointRadius: 0, fill: false },
        { label: 'K teórica (CSR)', data: [], borderColor: COLORES_GRAFICO.gris,
          borderWidth: 1.6, borderDash: [5, 3], pointRadius: 0 },
        { label: 'K observada', data: [], borderColor: COLORES_GRAFICO.secundario,
          borderWidth: 2, pointRadius: 0 }
      ]);
      const graficos = lienzos.map(l => crearGraficoLinea(l, [], bandas(), opciones));

      function pinta() {
        const r = t2Resuelve(T2_DOC);
        if (!r) {
          graficos.forEach(g => {
            g.data.labels = [];
            g.data.datasets.forEach(ds => { ds.data = []; });
            g.update('none');
          });
          lectura.innerHTML = `<p style="margin:0;">Resuelve tu variante arriba y aquí aparecerá
            tu envolvente.</p>`;
          return;
        }
        const e = DATOS_T2.envolventes[r.v.envolvente - 1];
        const dentroTramo = dentroTramoT2(e);   // con tolerancia: ver dentroTramoT2
        const vistas = [e.r.map(() => true), dentroTramo];
        graficos.forEach((g, k) => {
          const m = vistas[k];
          const corta = a => a.filter((_, i) => m[i]);
          g.data.labels = corta(e.r).map(x => n5(x, 4));
          g.data.datasets[0].data = corta(e.lo);
          g.data.datasets[1].data = corta(e.hi);
          g.data.datasets[2].data = corta(e.teo);
          g.data.datasets[3].data = corta(e.obs);
          g.update('none');
          g.canvas.setAttribute('aria-label', (k === 0
            ? 'Envolvente de K sobre todo el rango de r'
            : 'La misma envolvente restringida al tramo que eligió el informe')
            + ', con la banda de simulación, la curva teórica bajo CSR y la observada. '
            + 'Los recuentos están en la tabla que hay debajo.');
        });

        // El recuento se hace AQUÍ, sobre las curvas publicadas, y no se
        // lee del campo `nodos_fuera` del JSON. Las dos cifras tienen que
        // coincidir y el auditor lo comprueba; contarlas otra vez en el
        // navegador es lo que hace que el estudiante pueda repetir el
        // recuento y salirle lo mismo.
        let fuera = 0, fueraTramo = 0, enTramo = 0;
        for (let i = 0; i < e.r.length; i++) {
          const sale = e.obs[i] > e.hi[i] || e.obs[i] < e.lo[i];
          if (sale) fuera++;
          if (dentroTramo[i]) { enTramo++; if (sale) fueraTramo++; }
        }
        lectura.innerHTML = `<table><caption class="sr-only">Recuento de nodos fuera de
          banda</caption><tbody>
          <tr><th scope="row">Simulaciones de la envolvente</th><td>${e.nsim}</td></tr>
          <tr><th scope="row">Nodos de r evaluados</th><td>${e.nodos}</td></tr>
          <tr><th scope="row">Nodos fuera de la banda, en todo el rango</th>
              <td><strong>${fuera}</strong></td></tr>
          <tr><th scope="row">El tramo que eligió el informe</th>
              <td>de r = ${n5(e.tramo[0], 4)} a r = ${n5(e.tramo[1], 4)}, que
                  ${enTramo === 1 ? 'es 1 nodo' : `son ${enTramo} nodos`}</td></tr>
          <tr><th scope="row">Nodos fuera de la banda dentro de ese tramo</th>
              <td><strong>${fueraTramo}</strong></td></tr>
          </tbody></table>`;
        envolverTablas();
      }

      raiz.__t2repinta = pinta;
      pinta();
      return graficos;
    };
"""


# Las dos rúbricas, con los pesos del §6 y del §4.1 del plan. La de la
# defensa NO es un resumen de la del escrito: la defensa vale el 60 %, y
# publicarla con menos detalle sería calificar a ciegas el instrumento que
# más pesa.
#
# «Auditoría y refutación» sube de 20 a 25 % porque CUATRO de las cinco
# tareas son de refutación, y «Comunicación y honestidad» deja de ser un
# criterio sin artefacto: se califica sobre la bitácora. El piso de 6 de
# esa dimensión es el precedente que fijó Javier el 2026-09-03 al calificar
# el Taller 1 — la penalización por resolver la variante ajena no empuja
# ninguna celda a «No logrado».
RUBRICA_JS = """    RUBRICAS['taller2-escrito'] = {
      titulo: 'Rúbrica del escrito',
      total: 100,
      intro: 'El escrito vale el <strong>40&nbsp;%</strong> de la nota del taller. Estas cinco '
        + 'dimensiones se aplican al informe completo, no tarea por tarea: una misma tarea puede '
        + 'estar bien interpretada y mal comunicada. Pulsa cada una para ver sus cuatro niveles.',
      nota: 'Los niveles son excluyentes y cada dimensión se puntúa por separado. Lo que decide el '
        + 'nivel alto nunca es la cantidad de análisis: es que la cifra se use para decidir.',
      rotuloAnula: 'Sin esto la entrega está incompleta',
      anulan: [
        'La <strong>línea de identificación</strong> del buscador, copiada literal en la portada.',
        'La <strong>bitácora</strong>: media página declarando qué consultaste con IA, qué te '
          + 'respondió y cómo lo verificaste.'
      ],
      criterios: [
        {
          clave: 'A', nombre: 'Apropiación conceptual', puntos: 20,
          foco: 'Mide si usas el concepto <strong>para decidir</strong>, no para definir. Repetir '
            + 'qué es una ventana no puntúa; elegir una y sostener por qué, sí. Y el nivel alto '
            + 'pide una cosa más que solo una tarea te pide explícitamente: <strong>nombrar el '
            + 'módulo del capítulo que sostiene cada concepto</strong>. Los enunciados te los '
            + 'nombran todos —hay un recuadro «dónde está esto en el capítulo» en casi todas las '
            + 'tareas—, así que cuesta una línea.',
          niveles: [
            { nombre: 'Excelente', rango: '18–20', observa: 'Cada concepto aparece resolviendo una decisión concreta del análisis, y se nombra el módulo que lo sostiene.' },
            { nombre: 'Aceptable', rango: '13–17', observa: 'Los conceptos son correctos y se aplican, pero alguno queda enunciado sin llegar a decidir nada.' },
            { nombre: 'Insuficiente', rango: '7–12', observa: 'Predomina la definición sobre el uso: se explica qué es cada cosa y después se decide por otra vía.' },
            { nombre: 'No logrado', rango: '0–6', observa: 'Los conceptos se citan mal o no aparecen donde harían falta.' }
          ]
        },
        {
          clave: 'B', nombre: 'Interpretación de resultados', puntos: 25,
          foco: 'Mide si dices qué significa <strong>y qué no significa</strong> la cifra. Una '
            + 'interpretación que no acota su alcance está a medias.',
          niveles: [
            { nombre: 'Excelente', rango: '22–25', observa: 'Cada cifra se lee con su escala y su supuesto, y se dice explícitamente qué queda fuera de lo que prueba.' },
            { nombre: 'Aceptable', rango: '16–21', observa: 'Las lecturas son correctas; el límite de lo que prueban se menciona solo en algunas.' },
            { nombre: 'Insuficiente', rango: '9–15', observa: 'Se leen las cifras en la dirección correcta pero se les hace decir más de lo que dicen.' },
            { nombre: 'No logrado', rango: '0–8', observa: 'La lectura contradice la cifra, o la cifra se reporta sin lectura.' }
          ]
        },
        {
          clave: 'C', nombre: 'Comprensión del procedimiento', puntos: 20,
          foco: 'Mide si explicas <strong>por qué el procedimiento hace lo que hace</strong>: qué '
            + 'calcula, contra qué compara y qué supone para poder compararlo.',
          niveles: [
            { nombre: 'Excelente', rango: '18–20', observa: 'Se explica el mecanismo —qué entra en el estimador y contra qué se contrasta— y se conecta con la decisión tomada.' },
            { nombre: 'Aceptable', rango: '13–17', observa: 'El procedimiento se describe bien; el porqué queda implícito en alguna de las tareas.' },
            { nombre: 'Insuficiente', rango: '7–12', observa: 'Se describe la receta —los pasos— sin llegar al mecanismo.' },
            { nombre: 'No logrado', rango: '0–6', observa: 'El procedimiento se aplica sin que se pueda ver que se entendió.' }
          ]
        },
        {
          clave: 'D', nombre: 'Auditoría y refutación', puntos: 25,
          foco: 'Mide si detectas el defecto <strong>con evidencia interna</strong>: con tus '
            + 'propias cifras, no apelando a autoridad ni a que «suena raro». Cuatro de las cinco '
            + 'tareas son de refutación, y por eso esta dimensión pesa como la B. '
            + '<strong>Nombrar el defecto y arreglarlo son dos cosas distintas</strong>, y no '
            + 'todas las tareas piden las dos: T1(b) pide expresamente que NO se arregle. Esta '
            + 'dimensión mira el informe entero, así que el «qué habría que haber hecho» se '
            + 'espera donde la tarea lo pide, y no donde lo prohíbe.',
          niveles: [
            { nombre: 'Excelente', rango: '22–25', observa: 'Nombra el defecto, lo demuestra con una cifra propia y dice qué habría que haber hecho en su lugar.' },
            { nombre: 'Aceptable', rango: '16–21', observa: 'Detecta los defectos y los sostiene, pero alguno se argumenta sin la cifra que lo probaría.' },
            { nombre: 'Insuficiente', rango: '9–15', observa: 'Sospecha del resultado y no llega a identificar dónde está el error.' },
            { nombre: 'No logrado', rango: '0–8', observa: 'Da por bueno el procedimiento defectuoso, o lo rechaza sin evidencia.' }
          ]
        },
        {
          clave: 'E', nombre: 'Comunicación y honestidad', puntos: 10,
          foco: 'Se califica sobre la <strong>bitácora</strong>, y se contrasta en la '
            + 'sustentación. Aquí también se descuenta resolver una variante que no es la tuya, y '
            + 'ese descuento <strong>tiene piso: no baja de 6</strong>.',
          niveles: [
            { nombre: 'Excelente', rango: '9–10', observa: 'La bitácora dice qué se consultó, qué respondió y cómo se verificó, y lo verificado se puede rastrear en el informe.' },
            { nombre: 'Aceptable', rango: '7–8', observa: 'Declara el uso de IA con precisión razonable; la verificación se menciona sin detallarse.' },
            { nombre: 'Insuficiente', rango: '4–6', observa: 'La bitácora existe pero es genérica, o el informe no cuadra con lo que declara.' },
            { nombre: 'No logrado', rango: '0–3', observa: 'No hay bitácora, o lo que declara es falso.' }
          ]
        }
      ]
    };

    RUBRICAS['taller2-defensa'] = {
      titulo: 'Rúbrica de la sustentación',
      total: 100,
      intro: 'La sustentación vale el <strong>60&nbsp;%</strong> de la nota del taller. Son siete '
        + 'minutos repartidos en tres bloques, y cada bloque tiene su peso dentro de esta rúbrica.',
      nota: 'Los tres bloques se califican por separado. El tiempo no es un criterio: quedarse '
        + 'corto no descuenta si lo dicho responde.',
      rotuloAnula: 'Lo que se recalifica',
      anulan: [
        'Una decisión entregada por escrito que <strong>no se puede sostener aquí</strong>: esa '
          + 'tarea del escrito se vuelve a calificar con lo que se pueda sostener.'
      ],
      criterios: [
        {
          clave: 'I', nombre: 'Su variante · 2 min', puntos: 30,
          foco: 'Defiendes <strong>una</strong> decisión de tu escrito, y la elige el profesor '
            + 'después de haberlo leído. No es un resumen del informe: es sostener una elección.',
          niveles: [
            { nombre: 'Excelente', rango: '27–30', observa: 'Reconstruye la decisión con su cifra, dice qué alternativa descartó y por qué, y reconoce lo que su elección deja fuera.' },
            { nombre: 'Aceptable', rango: '19–26', observa: 'Sostiene la decisión con su cifra; la alternativa descartada queda sin argumentar.' },
            { nombre: 'Insuficiente', rango: '11–18', observa: 'Repite lo que escribió sin poder justificarlo cuando se le pregunta por qué.' },
            { nombre: 'No logrado', rango: '0–10', observa: 'No reconoce su propia decisión, o la contradice.' }
          ]
        },
        {
          clave: 'II', nombre: 'Banco · 3 min, tres preguntas', puntos: 45,
          foco: 'Tres preguntas de un banco de <strong>36 publicado con este enunciado</strong>, '
            + 'sorteadas <strong>sin reemplazo</strong> entre los doce. Cubren los once módulos del '
            + 'capítulo 4, no solo lo que tocan las tareas.',
          niveles: [
            { nombre: 'Excelente', rango: '40–45', observa: 'Las tres bien, con el mecanismo y no solo con la conclusión, y sin necesitar que se le reformule la pregunta.' },
            { nombre: 'Aceptable', rango: '29–39', observa: 'Dos de tres con solvencia, o las tres correctas pero apoyadas en la definición memorizada.' },
            { nombre: 'Insuficiente', rango: '16–28', observa: 'Una de tres, o responde en la dirección correcta sin poder sostener por qué.' },
            { nombre: 'No logrado', rango: '0–15', observa: 'No responde ninguna, o las respuestas contradicen el material.' }
          ]
        },
        {
          clave: 'III', nombre: 'Refutación en vivo · 2 min', puntos: 25,
          foco: 'Se lee una <strong>afirmación falsa</strong> sobre el capítulo —una distinta por '
            + 'persona— y hay que decir por qué lo es. No vale decir que es falsa: hay que decir '
            + 'dónde se rompe.',
          niveles: [
            { nombre: 'Excelente', rango: '22–25', observa: 'Localiza el punto exacto donde la afirmación falla y propone el enunciado correcto.' },
            { nombre: 'Aceptable', rango: '16–21', observa: 'Reconoce que es falsa y señala la zona del error sin acabar de precisarlo.' },
            { nombre: 'Insuficiente', rango: '9–15', observa: 'Duda de la afirmación por intuición, sin poder decir qué está mal.' },
            { nombre: 'No logrado', rango: '0–8', observa: 'Da la afirmación por buena.' }
          ]
        }
      ]
    };
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

    /* El informe que las tareas ponen a auditar. Va con marca de cita y en
       otra familia de color para que se lea como MATERIAL AJENO y no como
       afirmación del taller: la diferencia importa cuando lo que se pide
       es dudar de ella. */
    .cita-ia {
      margin: 1rem 0;
      padding: 0.9rem 1.1rem;
      background: #f1f5f9;
      border-left: 4px solid #64748b;
      border-radius: 0.4rem;
      color: #334155;
      font-size: 0.94rem;
    }

    .cita-ia p {
      margin: 0 0 0.7rem 0;
    }

    .cita-ia p:last-child {
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
    print(f"\n=== ensambla_taller2.py (C5a + C5b) ===\nplantilla: {len(doc)/1024:.0f} KB\n")

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
    doc = sustituye(doc, vieja[0], (GEOMAPAS_JS + GEOMAPAS_JS2).rstrip("\n"),
                    "los mapas del taller")

    doc = reemplaza_region(
        doc,
        "    // --- Deslizadores sobre un gráfico de línea ----------------------\n"
        "    SIMULADORES['demo-deslizadores'] = function (raiz) {",
        "    // ================================================================\n"
        "    // Autoevaluación de demostración: una pregunta de cada tipo\n",
        SIMULADORES_JS + SIMULADORES_JS2
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

    # Con C5b están las CINCO, y sus pesos tienen que sumar el 40 % que
    # pesa el escrito. Es la clase de cuenta que nadie rehace y que deja
    # un taller sobre 32 delante de doce personas.
    ESCRITAS = (1, 2, 3, 4, 5)
    PESO_TAREA, TAREAS_TOTALES = 8, 5
    if tareas != len(ESCRITAS):
        problemas.append(f"{tareas} tareas, se esperaban {len(ESCRITAS)} "
                         f"(T{', T'.join(str(x) for x in ESCRITAS)})")
    pesos = [int(x) for x in re.findall(r'class="badge-peso">(\d+)&nbsp;%', marcado)]
    if pesos != [PESO_TAREA] * len(ESCRITAS):
        problemas.append(f"los pesos de las tareas son {pesos} y las cinco valen "
                         f"{PESO_TAREA} % cada una")
    if PESO_TAREA * TAREAS_TOTALES != 40:
        problemas.append(f"las {TAREAS_TOTALES} tareas al {PESO_TAREA} % no suman el "
                         f"40 % que pesa el escrito")

    # Qué módulos llevan la tira, declarado y no contado. La llevan los
    # seis primeros: el de instrucciones porque es donde se resuelve, y los
    # cinco de tarea porque las cinco dependen del documento — volver al
    # módulo 1 a mirar qué localidad tocó es exactamente la fricción que
    # hace que alguien siga de memoria. El de rúbricas NO la lleva: no
    # depende de la variante, y ponerla ahí sugeriría que sí.
    CON_VARIANTE = {1, 2, 3, 4, 5, 6}
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
    # Dos listas y dos regiones, y la separación es de fondo. En la PROSA
    # no puede aparecer un veredicto: es el taller hablando. Dentro de un
    # informe citado sí puede —el informe de T3 dice literalmente que el
    # patrón «está agregado hasta esa distancia», y esa frase es el objeto
    # de la tarea, no una filtración—, así que los informes viven en el
    # script y se vigilan con la lista corta: los nombres de los
    # generadores, que no tienen ninguna excusa para aparecer en ninguna
    # parte.
    # Las de la prosa se afinaron en C6, y el motivo es instructivo: la
    # lista traía «es aleatorio», que saltó con una AFIRMACIÓN FALSA del
    # catálogo de refutaciones —«el índice de Clark-Evans vale exactamente
    # 1 cuando el patrón es aleatorio»—. Una guarda que salta con el
    # castellano corriente se acaba desactivando entera, que es peor que
    # no tenerla. Una fuga de verdad en este taller siempre habla del
    # patrón DE QUIEN LEE, o de cómo está compuesto un trío, o de cuál de
    # las dos ventanas de T1 es la buena. Eso es lo que se vigila.
    PROHIBIDAS_PROSA = ("familia del patrón",
                        "tu patrón está agregado", "tu patrón es aleatorio",
                        "tu patrón es regular", "el régimen de tu patrón",
                        "la ventana correcta es", "la ventana buena es",
                        "la ventana defectuosa es",
                        "uno de cada familia", "una de cada familia",
                        "uno de cada régimen", "uno de cada uno de los tres",
                        "el mapa a es el", "el mapa b es el", "el mapa c es el")
    PROHIBIDAS_TODO = ("familia del patrón", "rthomas", "rssi", "rpoispp",
                       "proceso de thomas")
    filtradas = [p for p in PROHIBIDAS_PROSA if p in marcado.lower()]
    filtradas += [p for p in PROHIBIDAS_TODO if p in doc.lower()]
    if filtradas:
        problemas.append(f"el documento contiene una respuesta: {sorted(set(filtradas))}")

    # Los informes citados: cada `data-informe` del marcado tiene que
    # tener quien lo escriba. Sin esta guarda, una cita mal nombrada deja
    # una caja gris vacía en mitad de la tarea —el taller pidiendo auditar
    # un informe que no está— y la consola no dice nada, porque el bucle
    # que los pinta simplemente no encuentra la función.
    informes_usados = sorted(set(re.findall(r'data-informe="([^"]+)"', marcado)))
    informes_escritos = sorted(set(re.findall(r"^      (\w+): function \(r\)", doc, re.M)))
    faltan_inf = sorted(set(informes_usados) - set(informes_escritos))
    if faltan_inf:
        problemas.append(f"informe(s) citados sin escribir: {faltan_inf}")
    sobran_inf = sorted(set(informes_escritos) - set(informes_usados))
    if sobran_inf:
        print(f"  ---  informe(s) escritos y no citados: {sobran_inf}")

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

    # --- C6 · el banco, su reparto y el sorteo ---------------------------
    # La tabla de cobertura se IMPRIME, no se supone. Es el criterio de
    # aceptación de C6, y existe porque un banco puede tener 36 preguntas
    # y dejar un módulo entero fuera sin que nada se ponga rojo.
    MODULOS_CAP4 = 11
    PREGUNTAS_POR_MODULO = 3
    MODULO_DOBLE = 4               # CSR, el que el escrito apenas toca (§3.6)
    ALUMNOS, POR_ALUMNO = 12, 3

    cobertura = {m: 0 for m in range(1, MODULOS_CAP4 + 1)}
    for m, _, _ in BANCO_DEFENSA:
        if m in cobertura:
            cobertura[m] += 1
        else:
            problemas.append(f"el banco tiene una pregunta del módulo {m}, "
                             f"que no existe en el capítulo 4")
    print("\n  Banco de la defensa · cobertura por módulo")
    linea = "   ".join(f"{m}:{c}" for m, c in cobertura.items())
    print(f"    {linea}")
    esperado = {m: (PREGUNTAS_POR_MODULO * 2 if m == MODULO_DOBLE else PREGUNTAS_POR_MODULO)
                for m in cobertura}
    if len(BANCO_DEFENSA) != ALUMNOS * POR_ALUMNO:
        problemas.append(f"el banco tiene {len(BANCO_DEFENSA)} preguntas y el sorteo sin "
                         f"reemplazo del §4.5 exige exactamente "
                         f"{ALUMNOS} × {POR_ALUMNO} = {ALUMNOS * POR_ALUMNO}")
    vacios = sorted(m for m, c in cobertura.items() if c == 0)
    if vacios:
        problemas.append(f"módulos del capítulo 4 sin ninguna pregunta en el banco: {vacios}")
    desvia = {m: (cobertura[m], esperado[m]) for m in cobertura if cobertura[m] != esperado[m]}
    if desvia:
        problemas.append(f"el reparto del §4.2 no cuadra (módulo: tiene/debe): {desvia}")
    print(f"    {len(BANCO_DEFENSA)} preguntas · {MODULO_DOBLE} lleva {cobertura[MODULO_DOBLE]} "
          f"y los otros {PREGUNTAS_POR_MODULO} cada uno")

    # Que el banco se agote EXACTAMENTE con doce estudiantes, comprobado
    # sobre doce documentos ficticios y no razonado sobre el papel. Con
    # 36 = 12 × 3 la propiedad es aritmética, pero el que se equivoca en
    # una aritmética evidente delante de doce personas es siempre el que
    # no la comprobó.
    import random as _random
    sorteo = list(range(len(BANCO_DEFENSA)))
    _random.Random(20262).shuffle(sorteo)
    reparto = [sorteo[i * POR_ALUMNO:(i + 1) * POR_ALUMNO] for i in range(ALUMNOS)]
    repartidas = [q for grupo in reparto for q in grupo]
    if sorted(repartidas) != list(range(len(BANCO_DEFENSA))):
        problemas.append("un sorteo de prueba sobre 12 documentos NO agota el banco "
                         "exactamente: alguna pregunta se repite o se queda sin salir")
    elif any(len(g) != POR_ALUMNO for g in reparto):
        problemas.append("el sorteo de prueba no reparte tres preguntas por estudiante")
    else:
        print(f"    sorteo de prueba: {ALUMNOS} estudiantes × {POR_ALUMNO} preguntas "
              f"agotan el banco sin repetir ninguna")

    # Las doce afirmaciones falsas, una por estudiante y ninguna repetida.
    if len(AFIRMACIONES_FALSAS) != ALUMNOS:
        problemas.append(f"hay {len(AFIRMACIONES_FALSAS)} afirmaciones falsas y hacen falta "
                         f"{ALUMNOS}: con sesión única, repetir una se la regala al que "
                         f"defiende al final (§4.5)")
    textos = [a for _, a in AFIRMACIONES_FALSAS]
    if len(set(textos)) != len(textos):
        problemas.append("hay dos afirmaciones falsas iguales")
    mods_falsas = sorted({m for m, _ in AFIRMACIONES_FALSAS})
    sin_falsa = sorted(set(range(1, MODULOS_CAP4 + 1)) - set(mods_falsas))
    if sin_falsa:
        problemas.append(f"módulos del capítulo 4 sin ninguna afirmación falsa: {sin_falsa} "
                         f"— con {len(AFIRMACIONES_FALSAS)} afirmaciones y {MODULOS_CAP4} "
                         f"módulos caben todos")
    print(f"    {len(AFIRMACIONES_FALSAS)} afirmaciones falsas, sobre los módulos {mods_falsas}")

    # Ninguna pregunta puede nombrar la posición de una opción: el banco es
    # ORAL y no tiene opciones, así que la comprobación es que no se haya
    # colado la redacción de un quiz.
    POSICIONES = ("las dos primeras", "la primera opción", "la última opción",
                  "marca todo lo que", "señala la opción")
    coladas = [f"{i + 1}" for i, (_, _, q) in enumerate(BANCO_DEFENSA)
               if any(x in q.lower() for x in POSICIONES)]
    if coladas:
        problemas.append(f"pregunta(s) del banco redactadas como si tuvieran opciones: {coladas}")

    # Y la lista legible DESDE FUERA, que es lo que el blueprint del
    # parcial 2 necesita para no regalar una respuesta ya publicada
    # (§10, riesgo alto). Se escribe siempre, con el mismo guion.
    lista = ["# El banco del Taller 2, legible desde fuera", "",
             "Lo escribe `precalculo/ensambla_taller2.py` cada vez que construye el taller.",
             "**No se edita a mano.**", "",
             "Existe por el riesgo alto del §10 del `PLAN_Taller_2_Cap_4.md`: el parcial 2 cubre",
             "los capítulos 4 y 5, y este banco se publica con el taller. Una pregunta repetida",
             "entre los dos documentos es una respuesta ya publicada. Quien escriba el *blueprint*",
             "del parcial (`PLAN_Parcial_Corte_2.md`, T1.1) tiene que leer esta lista y decidir:",
             "evitarlas, o reutilizarlas **a propósito** y declararlo.", "",
             f"## Las {len(BANCO_DEFENSA)} preguntas del banco", ""]
    for i, (m, tema, preg) in enumerate(BANCO_DEFENSA, 1):
        limpio = re.sub(r"<[^>]+>", "", preg)
        lista.append(f"{i}. **[mód. {m} · {tema}]** {limpio}")
    lista += ["", f"## Las {len(AFIRMACIONES_FALSAS)} afirmaciones falsas de la refutación en vivo",
              "", "Todas son FALSAS. Se leen en voz alta, una por estudiante.", ""]
    for i, (m, af) in enumerate(AFIRMACIONES_FALSAS, 1):
        lista.append(f"{i}. **[mód. {m}]** {af.replace('&lt;', '<').replace('&gt;', '>')}")
    lista.append("")
    BANCO_FUERA.parent.mkdir(parents=True, exist_ok=True)
    BANCO_FUERA.write_text("\n".join(lista), encoding="utf-8")
    try:
        donde_banco = BANCO_FUERA.relative_to(RAIZ)
    except ValueError:
        donde_banco = BANCO_FUERA
    print(f"    lista legible desde fuera: {donde_banco}")

    print()
    if problemas:
        for p in problemas:
            print(f"  MAL  {p}")
        print(f"\n  {len(problemas)} problema(s).\n")
        return 1
    print("  Ensamblado limpio: instrucciones + T1..T5 + las dos rúbricas + el banco "
          "(C5a + C5b + C6).\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
