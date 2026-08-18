#!/usr/bin/env python3
"""
ensambla_taller1.py — construye el Taller 1 (capítulos 1 y 2) · C5a

Material de Estadística Espacial 2026-II (20929). Ver PLAN_Taller_1_Caps_1_2.md.

C5a trae el esqueleto y los módulos 1 a 4: las instrucciones con el
buscador de variante, T1, T2 y T3. C5b añadirá T4 a T7, la rúbrica y el
banco de la defensa. Cada paso deja un HTML que ABRE Y FUNCIONA: la
navegación declara solo los módulos que existen, así que el taller a medio
construir se puede leer entero sin botones que lleven a un módulo vacío.

LO QUE ESTE ARCHIVO NO PUEDE ESCRIBIR, Y ES LA REGLA QUE MANDA.

Ninguna cifra a mano (D10), como en los capítulos. Pero además: **ninguna
respuesta**. El JSON entero viaja dentro del HTML —el buscador lo
necesita— así que todo lo que se interpole aquí es legible con «ver código
fuente». Lo que se publica es el enunciado y los datos; los veredictos de
T1 y T3 no están en ninguna parte del archivo.

CÓMO SE INDIVIDUALIZA, y por qué el navegador no calcula nada.

El estudiante escribe su documento y el componente busca su fila en la
tabla de 1000 variantes que precalculó R. Se guarda en `localStorage`
porque **los módulos se cargan de uno en uno**: `loadModule()` vacía
`mainContent` en cada salto, así que la variante tiene que sobrevivir al
cambio de módulo o el mapa de T1 no sabría qué patrón pintar.

EL MAPA DEL PATRÓN SE REGISTRA COMO FUNCIÓN, y eso tiene un coste que hay
que decir: `audita_texto_base.geomapas()` solo sabe mirar dentro de un
`.geomapa` cuya fuente sea un literal, así que esa familia del auditor de
prosa se queda sin nada que comprobar aquí. No es un descuido y no queda
sin cubrir: el mapa TIENE que ser dinámico —depende del documento— y
`audita_taller1.py` audita los 30 mapas directamente contra el JSON, uno
por uno, con más detalle del que el auditor de prosa alcanzaría.

Uso:  python3 precalculo/ensambla_taller1.py
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

    Mismo convenio que los ensambladores de capítulo: es lo que permite que
    un arnés de inyección construya desde JSON envenenados sin escribir
    jamás sobre lo publicado.
    """
    p = pathlib.Path(os.environ.get(var) or defecto)
    if var.endswith("DESTINO"):
        return p
    if not p.exists():
        sys.exit(f"PARADO: falta {p}")
    return p


PLANTILLA = _ruta("TALLER1_PLANTILLA", RAIZ / "plantilla" / "plantilla-capitulo.html")
DESTINO = _ruta("TALLER1_DESTINO", RAIZ / "Htmls_Espacial" / "taller-1-caps-1-2.html")

D = json.loads(_ruta("TALLER1_DATOS", SALIDAS / "taller1_datos.json")
               .read_text(encoding="utf-8"))
M = json.loads(_ruta("TALLER1_MAPAS", SALIDAS / "taller1_mapas.json")
               .read_text(encoding="utf-8"))

meta, reglas = D["meta"], D["reglas"]
t3, t5, t6, t7 = D["t3"], D["t5"], D["t6"], D["t7"]


def n(x, d=5):
    """Cinco decimales, la regla del material desde el 2026-08-03."""
    return f"{float(x):.{d}f}"


def n5(x):
    return n(x, 5)


def ent(x):
    """Entero con separador de millar fino (U+202F), fuera de fórmulas."""
    return f"{int(round(float(x))):,}".replace(",", "\u202f")


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

    Va en TODOS los módulos de tarea a propósito: quien está en T3 no
    debería tener que volver al módulo 1 para recordar qué municipio le
    tocó. El componente es el mismo —se registra una vez— y se rellena solo
    con lo que haya guardado el navegador.
    """
    return f"""      <div class="simulador" data-simulador="taller1-variante">
        <h4><i class="fas fa-fingerprint" aria-hidden="true"></i> Tu variante</h4>
        <p class="simulador-intro">Escribe los <strong>tres últimos dígitos</strong> de tu número de
          documento. {nota}</p>
        <div class="simulador-controles"></div>
        <div class="simulador-lectura"></div>
      </div>
"""


def tarea(num, peso, titulo, enunciado, literales, pista):
    """Un enunciado de tarea, con pista y SIN panel de solución.

    El componente `.ejercicio-guiado` de la plantilla trae dos botones,
    Pista y Solución. Aquí se usa solo el primero: la decisión de Javier fue
    taller sin solucionario, y el panel de solución no se deja vacío —se
    omite—, porque un botón que abre una caja vacía se lee como un error del
    material y no como una decisión.
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
# Las reglas de IA van AQUÍ y por escrito, y la decisión es de Javier
# (2026-08-13): uso libre sin pedir permiso, declaración obligatoria de qué
# se consultó y qué se verificó, y aviso explícito de la recalificación en
# la defensa. La alternativa —no decir nada— no es neutral: castiga al que
# se autolimita y premia al que supone que todo vale.
MOD1 = cabecera(
    1, "Cómo se trabaja este taller", "Read this first",
    "Nada. Este módulo no se califica: fija las reglas, resuelve tu variante "
    "y dice cómo se califica todo lo demás.") + f"""
      <p>Este taller cubre los capítulos 1 y 2. No se evalúa que sepas escribir código ni que recuerdes
        fórmulas: se evalúa que <strong>uses un concepto para decidir</strong>, que digas qué
        <em>no</em> significa una cifra, y que reconozcas un procedimiento equivocado cuyo resultado se
        ve perfectamente razonable. Son tres cosas distintas y las tres se califican por separado.</p>

      <div class="definition">
        <h3>Sobre usar inteligencia artificial: úsala</h3>
        <p>No hace falta pedir permiso ni justificarse. Puedes consultar cualquier modelo, para
          cualquier parte, tantas veces como quieras. El taller está diseñado dando por hecho que lo
          vas a hacer, y por eso <strong>ninguna tarea se contesta con lo que un modelo sabe sin tus
          datos</strong>: cada quien trabaja sobre un municipio, un patrón y unas estaciones distintas.</p>
        <p>Dos condiciones, y las dos son parte de la nota:</p>
        <ol class="lista-literales" type="1">
          <li><strong>Declara al final qué consultaste y qué verificaste.</strong> Una frase por
            consulta basta: qué preguntaste, qué te respondió y cómo comprobaste si era cierto. Vale el
            <strong>10&nbsp;%</strong> de la nota del escrito, y se califica la honestidad y la
            precisión de la declaración, no la cantidad de consultas. Declarar «usé IA para todo y
            verifiqué las cifras contra mi propia salida» puntúa; no declarar nada, no.</li>
          <li><strong>Cualquier decisión que entregues tienes que poder sostenerla en la defensa.</strong>
            Si en la defensa no puedes explicar por qué elegiste lo que elegiste, esa tarea
            <strong>se recalifica</strong>. No es una amenaza: es lo que hace que valga la pena entender
            lo que entregas, y es la razón por la que la defensa pesa el 40&nbsp;%.</li>
        </ol>
        <p style="margin-bottom:0;">Dicho de otro modo: la IA te puede ahorrar el trabajo mecánico. No
          te puede ahorrar el criterio, porque el criterio es lo único que se evalúa.</p>
      </div>

      <div class="note">
        <p style="margin-bottom:0;"><strong>El material que necesitas.</strong> Todo lo que se pide
          está en los dos capítulos, y conviene tenerlos abiertos al lado:
          <a href="capitulo-1-datos-espaciales.html">capítulo 1 · Datos espaciales y la primera ley
          de la geografía</a> y <a href="capitulo-2-crs-georreferenciacion.html">capítulo 2 · SIG,
          sistemas de referencia y georreferenciación con sf</a>. El
          <a href="capitulo-3-cartografia-maup.html">capítulo 3</a> no entra en este taller.</p>
      </div>

      <p>La entrega es un <strong>informe en PDF</strong>, compilado con LaTeX a partir de la
        plantilla que hay aquí abajo, más una <strong>defensa de 5 a 7 minutos</strong> en clase. En la
        defensa te tocan tres preguntas al azar de un banco que está publicado con este taller, y ese
        banco cubre <em>todo</em> el temario de los dos capítulos, no solo lo que aparece en las
        tareas.</p>

      <div class="note">
        <p><strong>Cómo se entrega.</strong> Un solo PDF por <strong>Brightspace</strong>, con el
          nombre <code>T1_Apellido_XXX.pdf</code>, donde <code>XXX</code> son tus tres últimos
          dígitos. Máximo <strong>13 páginas</strong> sin contar el anexo, y cada tarea trae su
          límite de palabras impreso en la plantilla.</p>
        <p><strong>Fecha de entrega: martes 25 de agosto de 2026, 9:00&nbsp;a.&nbsp;m.</strong> Es
          una semana desde que se reparte, y la defensa va después: lo que entregues ese martes es
          lo que se te preguntará en clase. <strong>No se aceptan entregas tarde</strong>: lo que no
          esté en Brightspace a esa hora no se califica.</p>
        <p><strong>La plantilla:</strong>
          <a href="../entrega/plantilla_taller1.tex" download target="_blank" rel="noopener">descargar
          la plantilla (<code>.tex</code>)</a> ·
          <a href="../entrega/plantilla_taller1.pdf" target="_blank" rel="noopener">ver el PDF
          compilado</a>. Los dos se abren aparte para que no pierdas esta página.
          Si no tienes LaTeX instalado, sube el <code>.tex</code> a Overleaf y compila allí: no usa
          ningún paquete fuera de lo estándar ni ningún archivo externo, así que no hay nada que
          configurar.</p>
        <p style="margin-bottom:0;">Trae una <strong>hoja de cifras</strong> en la página 2 con todo
          lo que se te pide calcular. Rellénala <em>antes</em> de escribir prosa: es lo que hace que
          cada tarea discuta números ya decididos en vez de irlos improvisando.</p>
      </div>

      <p>Lo primero es resolver tu variante. Los datos de casi todas las tareas dependen de ella, así
        que si te equivocas aquí te equivocas en todo lo demás.</p>

{variante("Se queda guardada en este navegador, así que aparece resuelta en cada tarea.")}
      <div class="warning">
        <p style="margin-bottom:0;"><strong>Comprueba el dígito de verificación antes de seguir.</strong>
          Tus {meta['n_estaciones']} estaciones no vienen en una lista: vienen definidas por una regla,
          y {reglas['estaciones'][0].lower() + reglas['estaciones'][1:]} Si la suma no coincide,
          seleccionaste otras estaciones y todo lo que construyas encima estará mal —sin que nada te
          avise—. Esa es, por sí sola, media lección del capítulo 2.</p>
      </div>

      <div class="note">
        <p style="margin-bottom:0;"><strong>Qué pesa cada cosa.</strong> El escrito vale el
          60&nbsp;% y la defensa el 40&nbsp;%. Dentro del escrito: T1 el 10&nbsp;%, T2 el 15&nbsp;%,
          T3 el 20&nbsp;%, T4 el 15&nbsp;%, T5 el 15&nbsp;%, T6 el 10&nbsp;% y T7 el 15&nbsp;%. La
          rúbrica completa —con las cinco dimensiones y qué distingue el nivel alto en cada una— está
          en el último módulo, y conviene leerla <em>antes</em> de escribir, no después.</p>
      </div>
""" + CIERRE


# =====================================================================
# MÓDULO 2 · T1 · El régimen que no se ve
# =====================================================================
# El enunciado NO dice cuántas familias de patrón hay ni cómo se llaman: la
# clasificación es la respuesta. Y no ofrece el contraste de cuadrantes,
# que es la evidencia que el literal (a) pide producir.
MOD2 = cabecera(
    2, "El régimen que no se ve", "T1 · Clark-Evans",
    "Interpretar un índice: qué decide, a qué escala, y qué se queda sin "
    "ver. Vale el 10 % del escrito.") + f"""
""" + variante() + f"""
      <p>Arriba tienes <strong>tu</strong> patrón puntual, con las cifras que lo describen. Las cifras
        ya están calculadas: esta tarea no es de cómputo. Lo que se evalúa es qué concluyes con ellas
        y —sobre todo— qué te cuidas de <em>no</em> concluir.</p>

      <div class="geomapa" data-geomapa="taller1-patron"></div>

      <div class="definition">
        <h3>Lo que tienes delante</h3>
        <p>De tu patrón se publican \\(n\\), el área de la ventana, la distancia media observada al
          vecino más próximo \\(\\bar{{d}}_{{\\min}}\\), la que daría el azar
          \\(E[\\bar{{d}}_{{\\min}}] = 1/(2\\sqrt{{\\lambda}})\\), y el índice de Clark-Evans
          \\(R = \\bar{{d}}_{{\\min}} / E[\\bar{{d}}_{{\\min}}]\\) en sus dos versiones: la ingenua y la
          corregida por efecto de borde (Donnelly).</p>
        <p style="margin-bottom:0;">El módulo 3 del capítulo 1 tiene la deducción de
          \\(1/(2\\sqrt{{\\lambda}})\\) en su derivación plegable, y el recuadro sobre qué le pasa a
          \\(R\\) cuando la repulsión de cerca y la agregación de lejos se compensan. Los dos hacen
          falta aquí.</p>
      </div>

""" + tarea(1, 10, "El régimen que no se ve",
       "Con las cifras de tu patrón y su mapa:",
       ["Di en qué régimen está tu patrón y <strong>justifícalo con las dos distancias</strong>, no "
        "con el índice solo. Si tu conclusión no se sostiene mirando el mapa, dilo: eso es parte de "
        "la respuesta y no un problema.",
        "¿Qué <strong>no</strong> prueba tu \\(R\\)? Contesta con la escala a la que mira el índice, "
        "no con significancia estadística.",
        "Un compañero tiene un \\(R\\) casi igual al tuyo con un \\(n\\) muy distinto. ¿Significan "
        "lo mismo los dos números? Justifica con la fórmula del denominador.",
        "Tu \\(R\\) corregido por borde es menor que el ingenuo. Explica en una frase por qué la "
        "corrección va en esa dirección y no en la otra, y di si el cambio te movería la "
        "conclusión de (a)."],
       "La cifra sola no decide: hay al menos dos familias de patrón que producen el mismo \\(R\\). "
       "Si el índice no te alcanza para (a), no lo fuerces —busca una segunda medición que mire una "
       "escala distinta a la del vecino más próximo, y dila—. El capítulo 4 vive de eso, pero para "
       "este taller basta con algo que puedas contar sobre el mapa.") + f"""
      <div class="note">
        <p style="margin-bottom:0;"><strong>Si quieres rehacer las cifras, aquí está por dónde.</strong>
          No es obligatorio —las cifras publicadas son las buenas— pero (a) se contesta mucho mejor si
          además mides algo por tu cuenta.</p>
      </div>

""" + tabs("Tu patrón, en R y en Python",
      """library(spatstat.geom)

# Las coordenadas de tu patron estan debajo del mapa de arriba: despliega
# "Ver los datos en una tabla" y copia las dos columnas, que ya vienen en
# la ventana unidad. (Tambien viajan en el codigo fuente de la pagina, en
# MAPAS_T1, bajo la clave que dice el titulo de tu mapa, cuantizadas a
# 0..4096: por ahi hay que dividirlas entre 4096.)
p &lt;- ppp(x, y, window = owin(c(0, 1), c(0, 1)))

mean(nndist(p))                       # la observada
0.5 / sqrt(npoints(p) / area.owin(p$window))   # la que daria el azar

# Y una segunda medicion, a otra escala:
quadratcount(p, nx = 4, ny = 4)""",
      """import numpy as np
from scipy.spatial import cKDTree

# xy: tus puntos, dos columnas, sobre la ventana unidad. Salen de la
# tabla que hay debajo del mapa de arriba, en "Ver los datos en una tabla".
arbol = cKDTree(xy)
d, _ = arbol.query(xy, k=2)
d[:, 1].mean()                        # la observada
0.5 / np.sqrt(len(xy))                # la que daria el azar

# La misma segunda medicion, contando por cuadrantes:
np.histogram2d(xy[:, 0], xy[:, 1], bins=4, range=[[0, 1], [0, 1]])[0]""") + CIERRE


# =====================================================================
# MÓDULO 3 · T2 · El intervalo que miente
# =====================================================================
MOD3 = cabecera(
    3, "El intervalo que miente", "T2 · Broken standard errors",
    "Medir sobre datos propios y traducir el resultado a una frase "
    "defendible. Vale el 15 % del escrito.") + variante() + f"""
      <p>Aquí sí hay que calcular, y sobre <strong>tus</strong> {meta['n_estaciones']} estaciones. El
        capítulo 1 midió esto mismo sobre las {t7['n_estaciones']} del país; tú lo vas a hacer sobre un
        vecindario, que es donde la dependencia espacial pega más fuerte.</p>

      <div class="warning">
        <p style="margin-bottom:0;">Antes de nada, <strong>verifica tu selección</strong> con el dígito
          de la tira de arriba. Un intervalo perfectamente calculado sobre las estaciones equivocadas
          se ve idéntico a uno correcto, y esa es exactamente la clase de error que este curso enseña a
          no cometer.</p>
      </div>

""" + tarea(2, 15, "El intervalo que miente",
       "Con la temperatura media anual de tus estaciones:",
       ["Calcula la media, el intervalo de confianza al 95&nbsp;% <em>clásico</em> —el que supone "
        "independencia—, la correlación con el vecino más próximo, el tamaño de muestra efectivo "
        "\\(n_{\\text{eff}}\\) y el intervalo corregido. Repórtalos en una tabla.",
        "Escribe <strong>una sola frase</strong>, sin jerga, que un funcionario de la Secretaría de "
        "Ambiente pueda leer y usar. Que se entienda qué se sabe y con cuánta certeza.",
        "El intervalo clásico estaba mal. ¿El problema está en la <strong>estimación</strong> o en la "
        "<strong>confianza</strong>? No respondas «en las dos»: decide y justifica.",
        "\\(n_{\\text{eff}}\\) supone que todas las parejas están igual de correlacionadas. Eso es "
        "falso en el espacio. Di por qué es falso y —lo que importa— <strong>en qué dirección</strong> "
        "te engaña el resultado que acabas de calcular."],
       "Los dos intervalos tienen que tener el MISMO centro: si no, hay un error de montaje y no un "
       "hallazgo. Lo que cambia es la anchura. Y para (c), pregúntate qué cifra se movió al corregir: "
       "si el centro no se movió, la respuesta se cae sola.") + tabs(
      "El intervalo corregido, en R y en Python",
      """library(sf); library(spdep)

est &lt;- st_read("datos/procesado/colombia_estaciones_clima.gpkg", quiet = TRUE)
mun &lt;- st_read("datos/procesado/colombia_adm2.gpkg", quiet = TRUE)

# Tu municipio, por su llave (la tienes en la tira de arriba):
yo  &lt;- mun[mun$shapeID == TU_LLAVE, ]
p   &lt;- st_point_on_surface(st_geometry(yo))

# Las 40 mas proximas EN 9377, que es como esta definida la regla:
d   &lt;- as.numeric(st_distance(p, est))
mis &lt;- est[order(d)[1:40], ]
sum(mis$altitud_m)          # tu digito de verificacion

t &lt;- mis$t_media_anual
n &lt;- length(t)
media &lt;- mean(t)
ee_clasico &lt;- sd(t) / sqrt(n)

# La correlacion con el vecino mas proximo, que es lo que rompe el ee:
nb   &lt;- knn2nb(knearneigh(st_coordinates(mis), k = 1))
rho  &lt;- moran.test(t, nb2listw(nb, style = "W"))$estimate[["Moran I statistic"]]
n_eff &lt;- n / (1 + (n - 1) * rho)""",
      """import geopandas as gpd, numpy as np
from scipy.spatial import cKDTree

est = gpd.read_file("datos/procesado/colombia_estaciones_clima.gpkg")
mun = gpd.read_file("datos/procesado/colombia_adm2.gpkg")

yo = mun[mun.shapeID == TU_LLAVE]
p  = yo.geometry.representative_point().iloc[0]

d   = np.hypot(est.geometry.x - p.x, est.geometry.y - p.y)
mis = est.iloc[np.argsort(d.to_numpy(), kind="stable")[:40]]
mis.altitud_m.sum()          # tu digito de verificacion

t = mis.t_media_anual.to_numpy()
n = len(t)
ee_clasico = t.std(ddof=1) / np.sqrt(n)

# La correlacion con el vecino mas proximo, a mano y sin heredar convenios:
xy = np.c_[mis.geometry.x, mis.geometry.y]
_, vec = cKDTree(xy).query(xy, k=2)
z = t - t.mean()
rho = (z * z[vec[:, 1]]).sum() / (z ** 2).sum()
n_eff = n / (1 + (n - 1) * rho)""") + CIERRE


# =====================================================================
# MÓDULO 4 · T3 · La auditoría
# =====================================================================
# El enunciado DICE que uno de los dos está mal (decisión de Javier,
# 2026-08-13): ya es la tarea más cara del taller, y añadirle el paso de
# decidir si hay algo que encontrar la volvería una adivinanza. En T5, en
# cambio, no se avisa: allí el defecto lo produce el propio estudiante al
# ejecutar el código.
#
# Las dos columnas se llaman A y B, y cuál es cuál lo sorteó la semilla del
# precálculo. Aquí no se sabe: el ensamblador imprime lo que le den.
def fila_t3(fa, fb):
    return (f"""          <tr><th scope="row">{int(fa['d1'])}–{int(fa['d2'])}</th>"""
            f"""<td>{ent(fa['n_pares'])}</td><td>{int(fa['sin_vecinos'])}</td>"""
            f"""<td>{n5(fa['I'])}</td>"""
            f"""<td>{ent(fb['n_pares'])}</td><td>{int(fb['sin_vecinos'])}</td>"""
            f"""<td>{n5(fb['I'])}</td></tr>""")


TABLA_T3 = "\n".join(fila_t3(a, b) for a, b in zip(t3["A"], t3["B"]))

MOD4 = cabecera(
    4, "La auditoría", "T3 · Which one is wrong",
    "Encontrar el procedimiento equivocado detrás de un resultado que se ve "
    "razonable. Vale el 20 % del escrito, y es la tarea más difícil.") + f"""
      <p>Las dos tablas de abajo son <strong>correlogramas reales</strong> de la temperatura media anual
        de las {t7['n_estaciones']} estaciones del IDEAM, por bandas de distancia. Las produjo el mismo
        guion, sobre los mismos datos, cambiando <strong>una línea</strong>. Los dos decaen. Los dos
        parecen razonables.</p>

      <p><strong>Uno de los dos está mal.</strong> No es un error de cálculo: es un procedimiento que
        mide algo distinto de lo que dice medir. Esta tarea es idéntica para todos —no depende de tu
        variante— porque lo que se evalúa es auditar un procedimiento, y el procedimiento es el mismo
        para cualquiera.</p>

      <table>
        <caption>Dos correlogramas de la misma variable sobre las mismas
          {t7['n_estaciones']} estaciones, con las mismas {t3['bandas']} bandas. «Parejas» son las
          parejas de estaciones que caen en la banda; «sin vecino», las estaciones que no tienen
          ninguna a esa distancia.</caption>
        <thead>
          <tr><th scope="col" rowspan="2">Banda (km)</th>
            <th scope="col" colspan="3">Resultado A</th>
            <th scope="col" colspan="3">Resultado B</th></tr>
          <tr><th scope="col">Parejas</th><th scope="col">Sin vecino</th><th scope="col">I</th>
            <th scope="col">Parejas</th><th scope="col">Sin vecino</th><th scope="col">I</th></tr>
        </thead>
        <tbody>
{TABLA_T3}
        </tbody>
      </table>

      <div class="note">
        <p style="margin-bottom:0;">Las columnas de <strong>parejas</strong> y <strong>sin vecino</strong>
          no están de adorno. Casi ningún informe publica esas dos columnas, y por eso casi ningún
          correlograma publicado se puede auditar. Aquí sí.</p>
      </div>

""" + tarea(3, 20, "La auditoría",
       "Sobre los dos resultados de la tabla:",
       ["Di cuál está mal. La evidencia tiene que ser <strong>interna a la tabla</strong>: algo que "
        "se pueda comprobar con los números que ves, sin recalcular nada y sin apelar a lo que ya "
        "sabías. Escribe la comprobación que hiciste, con cifras.",
        "Nombra el procedimiento equivocado: ¿qué mide de verdad la columna mala, si no es lo que su "
        "encabezado dice?",
        "Cuantifica el daño en la banda donde más se note, y explica por qué se nota justo ahí y no "
        "en otra.",
        "El resultado correcto tiene una banda con \\(I\\) <strong>negativo</strong> y el equivocado "
        "no. Un lector apresurado diría que el negativo es el error. Explica por qué el negativo es "
        "esperable y qué significa.",
        "¿Por qué este error <strong>no</strong> se vería mirando un mapa de las estaciones?"],
       "Compara las dos columnas de parejas entre sí, no cada una contra tu intuición. Y fíjate en la "
       "primera banda: es idéntica en los dos. Que un defecto no aparezca en la primera fila te dice "
       "en qué consiste el defecto.") + f"""
      <div class="warning">
        <p style="margin-bottom:0;"><strong>Un aviso sobre pedirle esto a un modelo.</strong> Puedes
          hacerlo, y conviene que lo hagas: preguntale «¿está bien este correlograma?» y guarda la
          respuesta para T7. Lo que se califica aquí es tu comprobación con cifras, así que una
          respuesta que diga «parece correcto, decae como se espera» no te sirve —pero es un dato
          valiosísimo sobre qué preguntas contesta bien un modelo y cuáles no—.</p>
      </div>
""" + CIERRE


# =====================================================================
# MÓDULO 5 · T4 · Cuatro sistemas, una decisión
# =====================================================================
# NO se publica ninguna de las cuatro áreas ni la distancia al origen de
# 3116: eso es exactamente lo que la tarea pide medir. Lo único que el
# estudiante recibe es su municipio.
MOD5 = cabecera(
    5, "Cuatro sistemas, una decisión", "T4 · Picking a CRS",
    "Elegir un sistema de referencia con una cifra de distorsión delante, "
    "no con una consigna. Vale el 15 % del escrito.") + variante() + f"""
      <p>Tu municipio se puede medir en cuatro sistemas, y los cuatro son legítimos. Ninguno es «el
        correcto» en abstracto: cada uno destruye algo distinto, y cuál conviene depende de qué vas a
        hacer y —esto es lo que casi nunca se dice— <strong>de dónde está tu municipio</strong>.</p>

      <div class="definition">
        <h3>Los cuatro</h3>
        <ul style="margin-bottom:0;">
          <li><strong>EPSG:4326</strong> — WGS 84, grados. Con <code>sf</code> las medidas salen por s2,
            sobre una esfera de radio {ent(t7['radio_esfera_s2_m'])} m.</li>
          <li><strong>EPSG:3857</strong> — Web Mercator, el de los mapas del navegador.</li>
          <li><strong>EPSG:3116</strong> — MAGNA-SIRGAS / Bogotá, con origen en Bogotá.</li>
          <li><strong>EPSG:9377</strong> — MAGNA-SIRGAS / Origen Nacional, el que usa el material.</li>
        </ul>
      </div>

""" + tarea(4, 15, "Cuatro sistemas, una decisión",
       "Sobre el municipio que te tocó:",
       ["Mide su <strong>área</strong> y una <strong>distancia</strong> característica —el ancho de "
        "su caja envolvente, por ejemplo— en los cuatro sistemas. Preséntalo en una tabla con las "
        "ocho cifras y di cuál tomas como referencia y por qué.",
        "Elige uno para trabajar y justifícalo <strong>con la cifra de distorsión que mediste</strong>. "
        "«Es el oficial de Colombia» no puntúa: eso no es una medición.",
        "¿En cuál de los cuatro un <em>buffer</em> de 500 m mide de verdad 500 m? Compruébalo y "
        "explica por qué en los otros no.",
        "Tu compañero de al lado tiene un municipio en otra parte del país. ¿Su respuesta a (b) "
        "tiene que ser la misma que la tuya? Explica de qué depende, nombrando el origen de "
        "EPSG:3116."],
       "El área en 4326 no es un número que se pueda leer sin más: fíjate en las UNIDADES que "
       "devuelve <code>st_area</code> en cada caso, y no compares grados cuadrados con metros "
       "cuadrados. Y para (d), busca dónde está el origen de 3116 antes de opinar.") + tabs(
      "Los cuatro sistemas, en R y en Python",
      """library(sf); library(units)

mun &lt;- st_read("datos/procesado/colombia_adm2.gpkg", quiet = TRUE)
yo  &lt;- mun[mun$shapeID == TU_LLAVE, ]

for (epsg in c(4326, 3857, 3116, 9377)) {
  y &lt;- st_transform(yo, epsg)
  cat(epsg, ": area =", format(st_area(y)), "\n")
}

# Y el buffer, que es donde se nota:
b &lt;- st_buffer(st_transform(yo, 9377), 500)""",
      """import geopandas as gpd

mun = gpd.read_file("datos/procesado/colombia_adm2.gpkg")
yo = mun[mun.shapeID == TU_LLAVE]

for epsg in (4326, 3857, 3116, 9377):
    y = yo.to_crs(epsg)
    print(epsg, y.area.iloc[0], y.total_bounds)

# Ojo: geopandas avisa al calcular areas en grados, y el aviso es el
# punto de la tarea. No lo silencies: leelo.""") + CIERRE


# =====================================================================
# MÓDULO 6 · T5 · Reetiquetar no es reproyectar
# =====================================================================
# Aquí NO se avisa de que hay un defecto (decisión de Javier): el
# estudiante lo produce él mismo ejecutando el código, y la tarea empieza
# cuando mira la salida. El ejemplo resuelto va sobre un municipio neutral
# que no le toca a nadie, para enseñar el síntoma sin dar el caso propio.
MOD6 = cabecera(
    6, "Reetiquetar no es reproyectar", "T5 · st_set_crs vs st_transform",
    "Reconocer, por sus síntomas, un objeto espacial perfectamente bien "
    "formado y completamente equivocado. Vale el 15 % del escrito.") + variante() + f"""
      <p>Las dos funciones se parecen en el nombre y no se parecen en nada más.
        <code>st_transform</code> <strong>recalcula</strong> las coordenadas; <code>st_set_crs</code>
        se limita a <strong>declarar</strong> que ya estaban en ese sistema. Si la declaración es
        falsa, no falla nada: el objeto queda bien formado, sin avisos, y todo lo que venga después
        estará mal.</p>

      <div class="note">
        <p><strong>Un ejemplo resuelto, sobre un municipio que no le toca a nadie.</strong> Se tomaron
          las {t5['n_puntos']} estaciones más próximas a {t5['municipio']} ({t5['departamento']}), en
          grados, y se declararon —sin transformar— como metros de EPSG:9377. Las dos primeras
          estaciones están a <strong>{n(t5['d_real_km'], 2)} km</strong> la una de la otra. Después de
          la declaración falsa, <code>st_distance</code> devuelve
          <strong>{n(t5['d_declarada_m'])}</strong> «metros»: la misma pareja, medida dos veces, con
          un factor de <strong>{ent(t5['veces'])}</strong> entre las dos cifras.</p>
        <p style="margin-bottom:0;">Y el síntoma que se ve sin calcular nada: el país entero cabe en
          una caja de <strong>{n(t5['area_declarada_m2'], 4)}</strong> «metros cuadrados», así que un
          <em>buffer</em> de 500 m se traga las {t5['en_buffer_500']} estaciones de golpe.</p>
      </div>

""" + tarea(5, 15, "Reetiquetar no es reproyectar",
       "Ejecuta el código de abajo sobre <strong>tus</strong> estaciones y mira la salida:",
       ["Describe lo que ves. ¿Qué síntoma delata que algo va mal? Nómbralo <strong>antes</strong> "
        "de arreglarlo y sin usar la palabra «error»: di qué cifra concreta es imposible y por qué.",
        "Arréglalo. Muestra la misma medición antes y después, y di qué función usaste y por qué "
        "esa y no la otra.",
        "¿Qué habría pasado aguas abajo si nadie lo nota? Haz un <em>join</em> espacial de tus "
        "estaciones contra los municipios con el objeto mal declarado y cuenta cuántas se quedan "
        "sin municipio. Después repítelo bien.",
        "Si <code>st_set_crs</code> es tan peligroso, ¿por qué existe? Describe un caso real en que "
        "<strong>sí</strong> es la función correcta y <code>st_transform</code> sería el error."],
       "Mira la caja envolvente (<code>st_bbox</code>) antes que ninguna otra cosa: es donde el "
       "disparate se ve de un golpe y sin calcular nada. Y para (d), piensa en un archivo que llega "
       "SIN sistema declarado y del que sabes de dónde salió.") + tabs(
      "El defecto, para que lo produzcas tú",
      """library(sf)

est &lt;- st_read("datos/procesado/colombia_estaciones_clima.gpkg", quiet = TRUE)
mis &lt;- est[TUS_40, ]                  # las tuyas, con la regla del modulo 1

# Se pasan a grados, que es como llegan la mayoria de los CSV del mundo:
mis_ll &lt;- st_transform(mis, 4326)

# Y ahora la linea del defecto. NO transforma: solo declara.
mal &lt;- st_set_crs(mis_ll, 9377)

st_bbox(mal)
st_distance(mal[1, ], mal[2, ])
sum(lengths(st_intersects(st_buffer(mal[1, ], 500), mal)))""",
      """import geopandas as gpd

est = gpd.read_file("datos/procesado/colombia_estaciones_clima.gpkg")
mis = est.iloc[TUS_40]

mis_ll = mis.to_crs(4326)

# La misma linea, en geopandas: set_crs(allow_override=True) no reproyecta.
mal = mis_ll.set_crs(9377, allow_override=True)

print(mal.total_bounds)
print(mal.geometry.iloc[0].distance(mal.geometry.iloc[1]))
print(mal.buffer(500).iloc[0].intersects(mal.geometry).sum())""") + CIERRE


# =====================================================================
# MÓDULO 7 · T6 · La fuga
# =====================================================================
MOD7 = cabecera(
    7, "La fuga", "T6 · Spatial leakage",
    "Decidir qué número reportar cuando hay dos, los dos son correctos y "
    "no dicen lo mismo. Vale el 10 % del escrito.") + f"""
      <p>Un modelo predice el <strong>{t6['variable']}</strong> a partir de la posición: la media de
        los {t6['k_vecinos']} municipios más próximos del conjunto de entrenamiento. Nada sofisticado,
        y a propósito: lo que sigue no lo produce el modelo.</p>

      <p>Se validó dos veces sobre los mismos {ent(t6['n'])} municipios, con
        {t6['n_pliegues']} pliegues las dos veces. Lo único que cambia es <strong>cómo se reparten</strong>
        los municipios entre pliegues: al azar, o por bloques geográficos.</p>

      <table>
        <caption>El mismo modelo, los mismos datos, dos formas de repartir los pliegues.</caption>
        <thead>
          <tr><th scope="col">Reparto de los pliegues</th><th scope="col">RMSE</th>
            <th scope="col">R²</th></tr>
        </thead>
        <tbody>
          <tr><th scope="row">Al azar</th><td>{n(t6['rmse_aleatoria'], 4)}</td>
            <td>{n(t6['r2_aleatoria'], 4)}</td></tr>
          <tr><th scope="row">Por bloques geográficos</th><td>{n(t6['rmse_bloques'], 4)}</td>
            <td>{n(t6['r2_bloques'], 4)}</td></tr>
        </tbody>
      </table>

      <div class="note">
        <p style="margin-bottom:0;">Los bloques geográficos salen <strong>desiguales</strong> —de
          {min(t6['tam_pliegues'])} a {max(t6['tam_pliegues'])} municipios— y eso no es un defecto del
          montaje: es la geografía del país, con los municipios apiñados en la región andina. El RMSE
          se calculó agrupando los errores de los {t6['n_pliegues']} pliegues, no promediando
          {t6['n_pliegues']} valores de RMSE, justamente para que un pliegue pequeño no pese lo mismo
          que uno grande.</p>
      </div>

""" + tarea(6, 10, "La fuga",
       "Con las dos filas de la tabla:",
       ["Explica la diferencia con el vocabulario de los capítulos. ¿Qué información tenía el "
        "modelo en la validación aleatoria que no tiene en la de bloques?",
        "¿Cuál de los dos R² reportarías a la Secretaría de Educación, y <strong>qué pregunta "
        "responde cada uno</strong>? Las dos partes cuentan: hay un uso legítimo para cada cifra.",
        "El modelo solo usa la posición. Si le añadieras una covariable —digamos el porcentaje de "
        "colegios oficiales— ¿esperarías que la brecha entre los dos R² se agrandara o se "
        "encogiera? Justifica; no hace falta que lo calcules."],
       "La pregunta de (a) no es «cuál está bien». Las dos validaciones están bien calculadas: "
       "responden a preguntas distintas sobre dónde va a usarse el modelo. Piensa en un municipio "
       "cuyos vecinos SÍ están en el entrenamiento y en otro cuyo vecindario entero quedó fuera.") + CIERRE


# =====================================================================
# MÓDULO 8 · T7 · Auditar a la IA
# =====================================================================
# Las tres afirmaciones están escritas AQUÍ y no salen de R, porque son
# prosa y no cifras. Las cifras que hacen falta para darles un veredicto sí
# salen de R, y son las que el módulo publica debajo. La afirmación (2) es
# la interesante: es cierta en su magnitud y falsa en su conclusión, y la
# brecha esfera/elipsoide —que nadie mira— es MAYOR que el error del que
# habla.
MOD8 = cabecera(
    8, "Auditar a la IA", "T7 · Grade the machine",
    "Emitir un veredicto sobre tres afirmaciones plausibles, con una cifra "
    "detrás de cada uno. Vale el 15 % del escrito.") + f"""
      <p>A un modelo de lenguaje se le preguntó por el material de estos dos capítulos. Esto fue lo que
        contestó, literalmente. <strong>Una de las tres afirmaciones es correcta, una es cierta a
        medias y una es falsa.</strong></p>

      <blockquote class="cita-ia">
        <p><strong>1.</strong> «Bajo la hipótesis nula de independencia, el valor esperado del índice
          de Moran no es cero sino \(-1/(n-1)\). Con las {t7['n_estaciones']} estaciones del IDEAM
          eso da {n(t7['moran_esperado'], 6)}, así que un \(I\) ligeramente negativo no indica
          repulsión: indica ausencia de estructura.»</p>
        <p><strong>2.</strong> «En Colombia da prácticamente igual calcular distancias sobre
          coordenadas geográficas o sobre coordenadas proyectadas, porque el país está sobre el
          ecuador y ahí un grado de longitud mide casi lo mismo que uno de latitud. El error que se
          comete es despreciable para cualquier análisis práctico.»</p>
        <p style="margin-bottom:0;"><strong>3.</strong> «Un índice de Clark-Evans igual a 1 demuestra
          que el patrón es aleatorio, es decir, que fue generado por un proceso de Poisson homogéneo.
          Si \(R\) da 1, se acepta la hipótesis de aleatoriedad espacial completa.»</p>
      </blockquote>

      <div class="definition">
        <h3>Las cifras que necesitas para el veredicto</h3>
        <p>Todas salen del mismo dato con el que trabajaste en T2 y T3 —las
          {t7['n_estaciones']} estaciones del IDEAM— y están calculadas sobre sus
          {ent(t7['n_parejas'])} parejas:</p>
        <ul>
          <li>Tomar «un grado son {n(t7['km_por_grado_manual'], 2)} km» y medir en línea recta sobre grados se desvía de la
            distancia real un <strong>{n(t7['error_grados_pct_mediano'], 2)}&nbsp;%</strong> de
            mediana, y hasta un <strong>{n(t7['error_grados_pct_max'], 2)}&nbsp;%</strong>.</li>
          <li>Un grado de longitud mide {n(t7['km_por_grado_lon_sur'], 2)} km en el extremo sur del
            país (latitud {n(t7['lat_min'], 2)}°) y {n(t7['km_por_grado_lon_norte'], 2)} km en el
            norte (latitud {n(t7['lat_max'], 2)}°).</li>
          <li>Y una que casi nunca se mira: la <strong>misma</strong> distancia medida sobre la esfera
            que usa <code>sf</code> y sobre el elipsoide WGS 84 difiere un
            <strong>{n(t7['brecha_esfera_elipsoide_pct_mediana'], 2)}&nbsp;%</strong> de mediana, y
            hasta un {n(t7['brecha_esfera_elipsoide_pct_max'], 2)}&nbsp;%.</li>
        </ul>
        <p style="margin-bottom:0;">Compara esas tres cifras entre sí antes de escribir nada. El orden
          en que quedan es el corazón de esta tarea.</p>
      </div>

""" + tarea(7, 15, "Auditar a la IA",
       "Sobre las tres afirmaciones de arriba:",
       ["Clasifica cada una como <strong>correcta</strong>, <strong>a medias</strong> o "
        "<strong>falsa</strong>, y sustenta cada veredicto con una cifra o con un contraejemplo. "
        "Un veredicto sin evidencia no puntúa, aunque acierte.",
        "La que sea falsa: reescríbela de modo que quede correcta <strong>sin cambiar de tema</strong>. "
        "Tiene que seguir hablando de lo mismo.",
        "La que sea «a medias»: di exactamente dónde se rompe. Qué parte es cierta, qué parte no lo "
        "es, y qué cifra de las de arriba lo demuestra.",
        "Cierra con una frase: ¿qué tipo de pregunta contesta bien un modelo sobre este material y "
        "qué tipo contesta mal? Apóyate en lo que te pasó al usarlo durante el taller, no en una "
        "opinión general."],
       "Para la falsa, el contraejemplo lo tienes en tu propio módulo 2: hay más de una forma de que "
       "un patrón dé \(R\) cerca de 1. Para la de a medias, no discutas si el error es grande o "
       "pequeño: compáralo con OTRA fuente de error que la afirmación no menciona y que está en la "
       "lista de arriba.") + CIERRE


# =====================================================================
# MÓDULO 9 · Cómo se califica, y la defensa
# =====================================================================
BANCO_DEFENSA = [
    ("Cap. 1 · Snow", "El mapa de Snow es un argumento geométrico, no epidemiológico. "
     "¿Qué quiere decir eso, y qué NO probó Snow con su mapa?"),
    ("Cap. 1 · Tipos de dato", "Los tres tipos de dato espacial se distinguen por QUÉ es aleatorio. "
     "Dilo para los tres, y pon un ejemplo colombiano de cada uno."),
    ("Cap. 1 · Ventana", "¿Por qué la ventana de observación forma parte del estimador en un patrón "
     "puntual? Enseña qué le pasa a λ si la cambias."),
    ("Cap. 1 · Tobler", "El correlograma del capítulo cae al quitar la altitud. ¿Qué parte de la "
     "dependencia era dependencia y qué parte era una covariable disfrazada?"),
    ("Cap. 1 · Moran", "¿Por qué E[I] no vale cero bajo la hipótesis nula? ¿De dónde sale el −1/(n−1)?"),
    ("Cap. 1 · Inferencia", "Con autocorrelación positiva, ¿el error estándar clásico sale grande o "
     "pequeño? ¿Y qué le pasa entonces a la cobertura del intervalo?"),
    ("Cap. 1 · n efectivo", "n_eff tiene un techo cuando n crece. ¿Cuál es y qué significa "
     "tenerlo delante?"),
    ("Cap. 1 · Estacionariedad", "Estacionariedad e isotropía no son lo mismo. Da un fenómeno "
     "colombiano que sea estacionario y anisótropo."),
    ("Cap. 1 · Una realización", "¿Por qué el problema de la realización única no se arregla "
     "tomando más datos?"),
    ("Cap. 1 · Escala y MAUP", "El efecto escala y el efecto zonificación del MAUP son distintos. "
     "Explica los dos con la deserción municipal."),
    ("Cap. 1 · Soporte", "¿Qué es el soporte de un dato y por qué no se puede cambiar sin pagar algo?"),
    ("Cap. 1 · Ecosistema", "¿Qué hace sf que sp no hacía, y por qué el curso usa terra y no raster?"),
    ("Cap. 1 · Anatomía de sf", "Un objeto sf, uno sfc y uno sfg. ¿Qué guarda cada uno y dónde vive "
     "el CRS?"),
    ("Cap. 1 · CV espacial", "¿Por qué una validación cruzada aleatoria infla el desempeño de un "
     "modelo espacial? Explícalo sin usar la palabra «fuga»."),
    ("Cap. 2 · Geoide", "Geoide, elipsoide y datum. ¿Cuál de los tres es una superficie física?"),
    ("Cap. 2 · Grados", "¿Por qué un grado de longitud no mide lo mismo en Leticia que en la "
     "Guajira? Da las dos cifras aproximadas."),
    ("Cap. 2 · Proyecciones", "«Proyectar es elegir qué destruir». ¿Qué destruye Web Mercator y "
     "por qué se usa igual?"),
    ("Cap. 2 · EPSG", "3116 y 9377 son los dos MAGNA-SIRGAS. ¿En qué se diferencian y cuándo "
     "conviene cada uno?"),
    ("Cap. 2 · set_crs", "Enseña con un ejemplo la diferencia entre st_set_crs y st_transform, y "
     "di cómo se detecta el error si alguien las confunde."),
    ("Cap. 2 · s2", "¿Qué cambia en sf cuando s2 está activado? ¿Sobre qué superficie mide?"),
    ("Cap. 2 · Formatos", "Shapefile, GeoPackage y GeoJSON. Da una razón técnica para no usar "
     "shapefile en este curso."),
    ("Cap. 2 · Topología", "¿Qué es una geometría inválida y por qué st_make_valid no siempre es "
     "la respuesta?"),
    ("Cap. 2 · Joins", "¿Para qué sirve un índice espacial en un join, y qué pasa si los dos "
     "objetos están en CRS distintos?"),
    ("Transversal", "De todo lo que entregaste, ¿qué decisión te costó más y por qué? Defiéndela."),
]

_banco = "\n".join(
    f"""          <tr><th scope="row">{i + 1}</th><td>{tema}</td><td>{preg}</td></tr>"""
    for i, (tema, preg) in enumerate(BANCO_DEFENSA))

MOD9 = cabecera(
    9, "Cómo se califica, y la defensa", "Rubric and viva",
    "Nada. Este módulo se lee ANTES de escribir el informe, no después.") + f"""
      <p>La rúbrica está aquí, entera y por adelantado, porque una rúbrica que se conoce al recibir la
        nota no sirve para aprender nada. Léela antes de escribir: las cinco dimensiones no miden lo
        mismo, y un informe con todas las cifras correctas puede quedarse a mitad de tabla si no dice
        qué significan.</p>

      <div class="rubrica" data-rubrica="taller1"></div>

      <h3>La defensa</h3>
      <p>De 5 a 7 minutos, en clase, individual. Se sacan <strong>tres preguntas al azar</strong> de
        las {len(BANCO_DEFENSA)} de abajo. El banco está publicado a propósito: no se trata de
        sorprenderte, se trata de que llegues sabiendo. Fíjate en que el banco cubre
        <strong>todo</strong> el temario de los dos capítulos, incluidos los módulos que ninguna tarea
        del escrito toca.</p>

      <div class="warning">
        <p style="margin-bottom:0;"><strong>La regla que ata las dos partes.</strong> Además de las
          tres del banco, se te puede preguntar por cualquier decisión que hayas entregado por
          escrito. Si no puedes sostenerla, esa tarea <strong>se recalifica</strong>. No es un castigo
          por usar IA —usarla está bien y se declara—: es lo que distingue haber entendido de haber
          entregado.</p>
      </div>

      <table>
        <caption>El banco de la defensa. Te tocan tres, al azar.</caption>
        <thead>
          <tr><th scope="col">#</th><th scope="col">Tema</th><th scope="col">Pregunta</th></tr>
        </thead>
        <tbody>
{_banco}
        </tbody>
      </table>
""" + CIERRE


# La rúbrica, con las cinco dimensiones del plan. Se publica DENTRO del
# taller y no como anexo del profesor: una rúbrica que se conoce al recibir
# la nota no sirve para aprender nada.
RUBRICA_JS = """    RUBRICAS['taller1'] = {
      titulo: 'Cómo se califica el escrito',
      puntos: 100,
      intro: 'Las cinco dimensiones se puntúan por separado sobre CADA tarea, y la nota del escrito '
           + 'es la suma ponderada por el peso de la tarea. Un informe con todas las cifras correctas '
           + 'puede quedarse a mitad de tabla: las cifras son la dimensión de menos peso.',
      nota: 'La defensa vale aparte el 40 % de la nota final, y puede recalificar cualquier tarea '
          + 'cuya decisión no se sostenga.',
      criterios: [
        {
          clave: 'A', nombre: 'Apropiación conceptual', puntos: 25,
          foco: 'Mide si usas el concepto para <strong>decidir</strong>, no para definirlo. Repetir '
              + 'la definición correcta puntúa poco; aplicarla a tu caso puntúa todo.',
          niveles: [
            { nombre: 'Excelente', rango: '22–25', observa: 'Usa el concepto para tomar una decisión y explica por qué descarta la alternativa.' },
            { nombre: 'Aceptable', rango: '15–21', observa: 'Aplica el concepto correctamente pero no descarta explícitamente lo que no eligió.' },
            { nombre: 'Insuficiente', rango: '8–14', observa: 'Define bien y aplica a medias: el concepto queda de adorno junto a la respuesta.' },
            { nombre: 'No logrado', rango: '0–7', observa: 'Reproduce una definición sin conectarla con el caso.' }
          ]
        },
        {
          clave: 'B', nombre: 'Interpretación de resultados', puntos: 25,
          foco: 'Mide si dices qué significa la cifra <strong>y qué no significa</strong>. El límite '
              + 'de lo que un número prueba es parte de la respuesta, no un añadido.',
          niveles: [
            { nombre: 'Excelente', rango: '22–25', observa: 'Dice qué significa, qué no significa y a qué escala vale. Traduce a lenguaje llano sin perder precisión.' },
            { nombre: 'Aceptable', rango: '15–21', observa: 'Interpreta bien pero no acota: da la conclusión sin sus límites.' },
            { nombre: 'Insuficiente', rango: '8–14', observa: 'Describe la cifra («R es 1.02») en vez de interpretarla.' },
            { nombre: 'No logrado', rango: '0–7', observa: 'Concluye algo que la cifra no sostiene.' }
          ]
        },
        {
          clave: 'C', nombre: 'Comprensión del procedimiento', puntos: 20,
          foco: 'Mide si explicas <strong>por qué</strong> el procedimiento hace lo que hace: qué '
              + 'supone, dónde entra ese supuesto y qué pasa cuando es falso.',
          niveles: [
            { nombre: 'Excelente', rango: '18–20', observa: 'Nombra el supuesto, dice dónde entra y qué consecuencia tiene romperlo.' },
            { nombre: 'Aceptable', rango: '12–17', observa: 'Explica el procedimiento correctamente sin llegar a sus supuestos.' },
            { nombre: 'Insuficiente', rango: '6–11', observa: 'Describe los pasos como una receta.' },
            { nombre: 'No logrado', rango: '0–5', observa: 'Aplica el procedimiento sin poder explicarlo.' }
          ]
        },
        {
          clave: 'D', nombre: 'Auditoría y refutación', puntos: 20,
          foco: 'Mide si detectas lo que está mal con <strong>evidencia interna</strong>, sin apelar '
              + 'a autoridad ni a «me parece». Es lo que se juega en T3 y en T7.',
          niveles: [
            { nombre: 'Excelente', rango: '18–20', observa: 'Encuentra el defecto y lo demuestra con una comprobación reproducible sobre los datos dados.' },
            { nombre: 'Aceptable', rango: '12–17', observa: 'Encuentra el defecto pero la evidencia es parcial o externa.' },
            { nombre: 'Insuficiente', rango: '6–11', observa: 'Sospecha del resultado correcto, o acierta sin poder mostrar por qué.' },
            { nombre: 'No logrado', rango: '0–5', observa: 'Acepta lo que se le da, o rechaza sin argumento.' }
          ]
        },
        {
          clave: 'E', nombre: 'Declaración de uso de IA', puntos: 10,
          foco: 'Mide la <strong>honestidad y la precisión</strong> de la declaración, no la cantidad '
              + 'de consultas. Usar IA para todo y verificarlo todo puntúa el máximo.',
          niveles: [
            { nombre: 'Excelente', rango: '9–10', observa: 'Dice qué preguntó, qué le respondieron y cómo lo comprobó, incluyendo al menos un caso en que el modelo se equivocó.' },
            { nombre: 'Aceptable', rango: '6–8', observa: 'Declara el uso pero no cómo verificó.' },
            { nombre: 'Insuficiente', rango: '3–5', observa: 'Declaración genérica («usé IA de apoyo») sin detalle.' },
            { nombre: 'No logrado', rango: '0–2', observa: 'No declara, o la declaración no corresponde con el informe.' }
          ]
        }
      ]
    };
"""



# =====================================================================
# El ensamblado
# =====================================================================
MODULOS = MOD1 + MOD2 + MOD3 + MOD4 + MOD5 + MOD6 + MOD7 + MOD8 + MOD9

# La navegación declara SOLO los módulos que existen. Con los nueve
# declarados y cuatro escritos, `loadModule()` encontraría `template` nulo y
# dejaría el panel en blanco sin un solo error en consola: es el modo de
# fallo más caro de este motor y el que T0.5 tardó más en encontrar.
MODULOS_NAV = [
    ("Cómo se trabaja este taller", "6 min"),
    ("T1 · El régimen que no se ve", "20 min"),
    ("T2 · El intervalo que miente", "40 min"),
    ("T3 · La auditoría", "45 min"),
    ("T4 · Cuatro sistemas, una decisión", "40 min"),
    ("T5 · Reetiquetar no es reproyectar", "40 min"),
    ("T6 · La fuga", "20 min"),
    ("T7 · Auditar a la IA", "35 min"),
    ("Cómo se califica, y la defensa", "10 min"),
]

_mods = ",\n".join(
    f'        {{ id: {i + 1}, title: "{t}", duration: "{d}" }}'
    for i, (t, d) in enumerate(MODULOS_NAV))

COURSE_DATA = f"""    const courseData = {{
      modules: [
{_mods}
      ]
    }};

    // El taller entero, tal como sale de precalculo/genera_taller1.R. Nada
    // de lo que hay aquí es una respuesta: son los datos del enunciado.
    const DATOS_T1 = {json.dumps(D, ensure_ascii=False)};
    const MAPAS_T1 = {json.dumps(M, ensure_ascii=False)};

    const n5 = (x, d = 5) => Number(x).toFixed(d);
    const milC = x => Number(x).toLocaleString('es-CO');

    // La variante viva. Sobrevive al cambio de módulo porque loadModule()
    // vacía mainContent en cada salto: sin esto, el mapa de T1 no sabría
    // qué patrón pintar en cuanto el estudiante navegara.
    const T1_LLAVE_GUARDADA = 'taller1-variante';
    let T1_VARIANTE = null;
    try {{
      const g = window.localStorage.getItem(T1_LLAVE_GUARDADA);
      if (g !== null) T1_VARIANTE = parseInt(g, 10);
    }} catch (e) {{ /* navegador sin almacenamiento: se pide cada vez */ }}

    function t1Resuelve(v) {{
      if (!Number.isInteger(v) || v < 0 || v >= DATOS_T1.meta.n_variantes) return null;
      const idx = DATOS_T1.variantes;
      return {{
        variante: v,
        municipio: DATOS_T1.municipios[idx.m0[v]],
        patron: DATOS_T1.patrones[idx.p0[v]],
        // El mapa se busca por el MISMO índice que la ficha de cifras: si
        // alguna vez dejaran de ir emparejados, el estudiante vería un
        // dibujo que no es el de sus números.
        mapa_id: 'patron-' + String(idx.p0[v] + 1).padStart(2, '0'),
      }};
    }}
"""

# El mapa del patrón, como FUNCIÓN y no como literal: depende del documento.
# El coste está declarado en la cabecera de este archivo.
# La tabla de respaldo del mapa de T1, y por qué no es un adorno.
#
# El lienzo es un `<canvas>`: los 40 puntos son PÍXELES, no elementos, así
# que inspeccionar el mapa no devuelve una sola coordenada. Sin esta tabla
# la única vía para rehacer las cifras era abrir el código fuente y buscar
# `MAPAS_T1`, y el propio bloque de arranque llegó a mandar al estudiante a
# «botón derecho, inspeccionar», que no lleva a ninguna parte.
#
# Y hay una razón más seria que la comodidad. T1 se responde MIRANDO el
# mapa —esa es la tarea—, así que sin tabla la única tarea del taller que
# exige ver un dibujo era, para quien usa lector de pantalla, «Patrón 22,
# 40 unidades» y nada más. El componente contempla esta tabla justamente
# para eso: para quien no ve el mapa, la tabla ES el mapa.
#
# Las coordenadas van ya divididas por `q` —en la ventana unidad, que es
# como las pide `ppp()`— y no en los enteros 0..4096 del JSON: el
# estudiante no tiene por qué deshacer una cuantización que existe para
# ahorrar bytes. Cuatro decimales, que es justo lo que 1/4096 resuelve.
TABLA_PATRON_JS = """      tabla: function (d) {
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

GEOMAPAS_JS = """    GEOMAPAS['taller1-patron'] = {
      fuente: function () {
        const r = t1Resuelve(T1_VARIANTE);
        return r ? MAPAS_T1[r.mapa_id] : null;
      },
      paleta: 'verde',
      alto: 380,
""" + TABLA_PATRON_JS + """,
    };
"""

SIMULADORES_JS = """    // --- El buscador de variante -------------------------------------
    // Ninguna aritmética: la fila viene precalculada en R. El navegador
    // busca, no calcula, y por eso no hay ninguna función de dispersión
    // escrita dos veces en dos lenguajes.
    SIMULADORES['taller1-variante'] = function (raiz) {
      const controles = raiz.querySelector('.simulador-controles');
      const lectura = raiz.querySelector('.simulador-lectura');
      const idInput = 'doc-' + Math.random().toString(36).slice(2, 8);
      controles.innerHTML = `
        <div class="control-grupo">
          <label for="${idInput}">Últimos tres dígitos de tu documento</label>
          <input id="${idInput}" type="text" inputmode="numeric" maxlength="3"
                 placeholder="000" style="max-width:7rem; font-family:'Fira Code', monospace;
                 font-size:1.1rem; text-align:center; padding:0.4rem;">
        </div>`;
      const campo = controles.querySelector('input');

      function pinta() {
        const r = t1Resuelve(T1_VARIANTE);
        if (!r) {
          lectura.innerHTML = `<p style="margin:0;">Escribe tus tres últimos dígitos
            (de <code>000</code> a <code>999</code>) para ver qué te toca.</p>`;
          return;
        }
        const m = r.municipio, p = r.patron;
        lectura.innerHTML = `
          <table>
            <caption class="sr-only">Tu variante del taller</caption>
            <tbody>
              <tr><th scope="row">Variante</th><td colspan="3"><code>${String(r.variante).padStart(3, '0')}</code></td></tr>
              <tr><th scope="row">Tu municipio</th>
                  <td colspan="3"><strong>${m.municipio}</strong> (${m.departamento})</td></tr>
              <tr><th scope="row">Su llave en la MGN</th><td colspan="3"><code>${m.llave}</code></td></tr>
              <tr><th scope="row">Dígito de verificación</th>
                  <td colspan="3">la suma de las altitudes de tus ${DATOS_T1.meta.n_estaciones}
                      estaciones tiene que dar <strong>${milC(m.suma_altitud)}</strong> m</td></tr>
              <tr><th scope="row">Tu patrón</th>
                  <td>n = <strong>${p.n}</strong></td>
                  <td>área = ${n5(p.area)}</td>
                  <td>λ = ${n5(p.lambda)}</td></tr>
              <tr><th scope="row">Sus distancias</th>
                  <td>observada = <strong>${n5(p.nn_media)}</strong></td>
                  <td>la del azar = ${n5(p.nn_esperada)}</td>
                  <td></td></tr>
              <tr><th scope="row">Clark-Evans</th>
                  <td>R = <strong>${n5(p.clark_evans)}</strong></td>
                  <td>corregido = ${n5(p.clark_evans_donnelly)}</td>
                  <td></td></tr>
            </tbody>
          </table>`;
      }

      function aplica(v) {
        T1_VARIANTE = v;
        try { window.localStorage.setItem(T1_LLAVE_GUARDADA, String(v)); } catch (e) { /* sin almacenamiento */ }
        // Todas las tiras de la página, no solo esta: el módulo 1 puede
        // tener dos y quedarían discrepando entre sí.
        document.querySelectorAll('.simulador[data-simulador="taller1-variante"]')
          .forEach(otra => { if (otra.__t1pinta) otra.__t1pinta(); });
        // Y el mapa del patrón, si el módulo actual lo tiene. Ojo con el
        // caso que se comió T1 entero en la verificación de C9: si el
        // módulo se abrió SIN variante, `iniciarGeomapas()` se fue por su
        // rama de «sin datos» —`fuente()` devuelve null— y salió sin dejar
        // `__geomapa` en el contenedor. Repintar entonces no repinta nada:
        // el estudiante que escribe sus tres dígitos DENTRO de T1, que es
        // donde está la segunda tira y por tanto el camino natural, veía la
        // ficha resolverse y el mapa seguir sin aparecer. Solo volvía si
        // salía del módulo y regresaba. Así que un contenedor sin cablear
        // no se repinta: se CABLEA, y para eso hay que llamar al
        // inicializador, no al método que ese contenedor todavía no tiene.
        // (`iniciarGeomapas()` recorre todos los mapas del módulo, que hoy
        // es exactamente este; el `some` evita llamarlo cuando ya está.)
        const mapas = [...document.querySelectorAll('[data-geomapa="taller1-patron"]')];
        if (mapas.some(g => !g.__geomapa)) iniciarGeomapas();
        mapas.forEach(g => {
          if (!g.__geomapa) return;
          g.__geomapa.dibuja();
          // Y la tabla de respaldo A MANO, porque `dibuja()` no la toca:
          // `iniciarGeomapas()` la pinta UNA vez con el dato inicial y
          // luego solo se repintan lienzo y leyenda. Sin esta línea, quien
          // corrige un dígito ve el mapa nuevo con las coordenadas del
          // patrón anterior debajo, y la tabla aquí no es un resumen: es
          // EL dato con el que se rehacen las cifras. Es la misma trampa
          // que el componente documenta para la leyenda congelada, un
          // escalón más abajo.
          const det = g.querySelector('.geomapa-tabla');
          const spec = GEOMAPAS[g.dataset.geomapa];
          const d = spec && (typeof spec.fuente === 'function' ? spec.fuente() : spec.fuente);
          if (det && d && spec.tabla)
            det.innerHTML = '<summary>Ver los datos en una tabla</summary>' + spec.tabla(d);
        });
      }

      raiz.__t1pinta = pinta;
      campo.addEventListener('input', () => {
        const limpio = campo.value.replace(/\\D/g, '').slice(0, 3);
        if (limpio !== campo.value) campo.value = limpio;
        if (limpio.length === 3) aplica(parseInt(limpio, 10));
      });
      if (Number.isInteger(T1_VARIANTE)) campo.value = String(T1_VARIANTE).padStart(3, '0');
      pinta();
    };
"""

# El taller no lleva autoevaluación: la evaluación ES el taller. El registro
# de demostración de la plantilla se retira para que no quede un quiz
# huérfano esperando un marcado que nunca llega.
QUIZ_JS = """    AUTOEVALUACIONES['taller1-sin-quiz'] = [];
"""

CSS_EXTRA = """
    /* El distintivo de peso de cada tarea. Va pegado al título del
       enunciado porque el peso es parte del enunciado: saber que una tarea
       vale el 20 % cambia cuánto tiempo merece. */
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

    /* La respuesta del modelo que T7 pone a auditar. Va con marca de cita
       y en otra familia de color para que se lea como material ajeno y no
       como afirmación del taller: la diferencia importa cuando lo que se
       pide es dudar de ella. */
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
"""


def reemplaza_region(texto, abre, cierra, nuevo, que, max_lineas, min_lineas=0):
    """Sustituye entre `abre` y el primer `cierra` posterior, con DOS topes.

    Copiada de `ensambla_cap1.py` con sus dos guardas, y las dos hacen falta
    por lo mismo: sustituir de más se llevó 270 líneas del motor con el
    informe en verde, y sustituir de menos dejó vivos dos simuladores de
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
    doc = PLANTILLA.read_text(encoding="utf-8")
    print(f"\n=== ensambla_taller1.py (C5a) ===\nplantilla: {len(doc)/1024:.0f} KB\n")

    doc = sustituye(doc, "<title>Plantilla de capítulo — Estadística Espacial</title>",
                    f"<title>{meta['titulo']} — Estadística Espacial</title>", "título")
    doc = sustituye(doc, "PLANTILLA BASE •\n              5 MÓDULOS DE DEMOSTRACIÓN • UNBOSQUE 2026-II",
                    "TALLER 1 • CAPÍTULOS 1 Y 2 •\n"
                    "              ESCRITO 60 % + DEFENSA 40 % • UNBOSQUE 2026-II",
                    "subtítulo de la cabecera")
    doc = sustituye(doc, "Estadística Espacial (20929) • Plantilla de\n          capítulo • UnBosque 2026-II",
                    "Estadística Espacial (20929) • Taller 1 de 2 •\n"
                    "          Corte I • UnBosque 2026-II", "pie")

    doc = sustituye(doc, "    /* ------------------------------------------------------------------\n"
                         "       Componente .ciclo — diagrama de etapas recorrible",
                    CSS_EXTRA + "\n    /* ------------------------------------------------------------------\n"
                                "       Componente .ciclo — diagrama de etapas recorrible",
                    "el CSS propio del taller")

    doc = reemplaza_region(doc, "    const courseData = {", "\n    };\n", COURSE_DATA,
                           "courseData + DATOS_T1", max_lineas=20)

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
    doc = sustituye(doc, vieja[0], GEOMAPAS_JS.rstrip("\n"), "el mapa del patrón")

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
    tiras = marcado.count('data-simulador="taller1-variante"')

    try:
        donde = DESTINO.relative_to(RAIZ)
    except ValueError:
        donde = DESTINO
    print(f"\n{donde}  {len(doc)/1024:.0f} KB")
    print(f"  {mods} módulos ({declarados} declarados en la navegación) · "
          f"{tareas} tareas · {tiras} tiras de variante")
    # «0 lienzos, 0 con aria-label» pasaría la comprobación de abajo por
    # vacuidad, y eso se lee igual que un verde de verdad. Aquí el único
    # <canvas> lo crea `.geomapa` en tiempo de ejecución, así que se dice en
    # voz alta en vez de dejar la cuenta a cero informando «bien».
    if lienzos == 0:
        print("  ---  ningún <canvas> en el marcado: el único lo fabrica el componente "
              ".geomapa\n       al cargar el módulo, y su aria-label se comprueba en el "
              "navegador (C9)")
    else:
        print(f"  {lienzos} lienzos, {con_alt} con aria-label")

    problemas = []
    if mods != declarados:
        problemas.append(f"{mods} plantillas de módulo y {declarados} declaradas en la "
                         f"navegación: un botón llevaría a un panel en blanco sin un "
                         f"solo error en consola")
    if lienzos != con_alt:
        problemas.append(f"{lienzos - con_alt} lienzo(s) sin aria-label")
    if tareas != 7:
        problemas.append(f"{tareas} tareas, se esperaban 7 (T1 a T7)")
    # Los pesos de las siete tienen que sumar 100: es la clase de cuenta que
    # nadie rehace y que deja un taller sobre 95 delante de doce personas.
    pesos = [int(x) for x in re.findall(r'class="badge-peso">(\d+)&nbsp;%', marcado)]
    if sum(pesos) != 100:
        problemas.append(f"los pesos de las tareas suman {sum(pesos)} y no 100: {pesos}")
    # Qué módulos llevan la tira, declarado y no contado. La primera
    # versión de esta guarda exigía una tira en todos menos el primero, y
    # se disparó en cuanto llegaron T6 y T7 —que son iguales para todos y
    # no tienen variante que mostrar—. Un umbral numérico no sabía la
    # diferencia; una lista sí, y además deja escrito qué tareas están
    # individualizadas, que es información que el taller necesita tener en
    # algún sitio.
    CON_VARIANTE = {1, 2, 3, 5, 6}      # instrucciones, T1, T2, T4 y T5
    trozos = dict(zip(
        [int(x) for x in re.findall(r'<template id="module-(\d+)">', marcado)],
        re.split(r'<template id="module-\d+">', marcado)[1:]))
    faltan = sorted(k for k in CON_VARIANTE
                    if 'data-simulador="taller1-variante"' not in trozos.get(k, ""))
    sobran = sorted(k for k in trozos
                    if k not in CON_VARIANTE
                    and 'data-simulador="taller1-variante"' in trozos[k])
    if faltan:
        problemas.append(f"a los módulos {faltan} les falta la tira de variante: sus "
                         f"tareas dependen del documento y obligarían a volver al módulo 1")
    if sobran:
        problemas.append(f"los módulos {sobran} llevan tira de variante y no la necesitan: "
                         f"sus tareas son iguales para todos, y la tira sugiere lo contrario")
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
    RAROS = {"\u202f": "U+202F espacio fino", "\u2009": "U+2009 thin space",
             "\u00a0": "U+00A0 nbsp"}
    formulas = re.findall(r"\\\(.*?\\\)|\$\$.*?\$\$", marcado, re.S)
    sucias = [(f[:60], RAROS[c]) for f in formulas for c in RAROS if c in f]
    if sucias:
        problemas.append(f"{len(sucias)} fórmula(s) con un espacio que KaTeX no "
                         f"entiende: {sucias[:2]} — usa ent_mate()")
    if doc.count("<template") != doc.count("</template>"):
        problemas.append("las plantillas no abren y cierran igual")
    # Y la comprobación propia de un taller: que no se haya colado una
    # respuesta en el HTML. Las palabras son las mismas que vigila
    # `audita_taller1.py` sobre el JSON, aquí sobre la prosa YA ENSAMBLADA.
    PROHIBIDAS = ("familia del patrón", "el correcto es", "el defectuoso es",
                  "acumulad", "el régimen es")
    filtradas = [p for p in PROHIBIDAS if p in marcado.lower()]
    if filtradas:
        problemas.append(f"el marcado contiene una respuesta: {filtradas}")

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
    print("  Ensamblado limpio: instrucciones + T1..T7 + rúbrica y defensa.\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
