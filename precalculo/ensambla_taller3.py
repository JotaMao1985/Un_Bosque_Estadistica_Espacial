#!/usr/bin/env python3
"""
ensambla_taller3.py — construye el Taller 3 (capítulos 1 a 5, en QGIS)

Material de Estadística Espacial 2026-II (20929). Ver PLAN_Taller_3_SIG.md.

QUÉ ES ESTE TALLER Y EN QUÉ SE DISTINGUE DE LOS OTROS DOS. Es GUIADO: cada
tarea trae sus pasos, con el nombre de la herramienta de QGIS tal como
aparece en la interfaz en español. Lo que se califica no es haber dado
los clics, sino dos cosas: que las cifras de control salgan —eso prueba
que el recorrido se hizo sobre la variante propia— y que se diga qué
calculó cada botón. El hilo es el del capítulo 2, módulo 1: «un clic no
deja rastro». Aquí se le obliga a dejarlo.

LO QUE ESTE ARCHIVO NO PUEDE ESCRIBIR. Ninguna cifra a mano y ninguna
respuesta, como en los Talleres 1 y 2. El JSON que viaja dentro del HTML
(`taller3_datos.json`) solo lleva la variante —una localidad y cuatro
números— y, de cada localidad, n, área y lambda. Las cifras de control
están en `precalculo/cache/`, fuera del repositorio.

Y por eso la prosa no adelanta ni el signo de un resultado: no dice si el
índice de vecino más próximo sube o baja al corregir el área (depende de
la localidad), ni cuánto se infla un área en EPSG:3857, ni si la curva L
sale de la banda.

LOS NOMBRES DE LAS HERRAMIENTAS SON LOS DE LA TRADUCCIÓN OFICIAL de QGIS
3.44 (`qgis_es.qm`), leídos de la aplicación y no escritos de memoria,
con sus erratas incluidas («Crear cuadricula», «Extraer por ubicacion»):
el estudiante tiene que encontrar en su pantalla lo que el enunciado
nombra. Cada herramienta lleva también su identificador, que no cambia
con el idioma.

EL CALENDARIO, EN UN SOLO SITIO: las dos constantes de abajo. El auditor
de prosa exige que la página y la plantilla de entrega digan lo mismo.

Uso:  python3 precalculo/ensambla_taller3.py
      (desde la carpeta `Estadistica espacial/`)
"""
from __future__ import annotations

import json
import os
import pathlib
import re
import sys

RAIZ = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "precalculo"))
SALIDAS = RAIZ / "precalculo" / "salidas"

from pon_boton_indice import aplica as aplica_boton  # noqa: E402


def _ruta(var: str, defecto: pathlib.Path) -> pathlib.Path:
    """Una ruta que el arnés de inyección puede desviar por variable de entorno."""
    v = os.environ.get(var)
    return pathlib.Path(v) if v else defecto


PLANTILLA = _ruta("TALLER3_PLANTILLA", RAIZ / "plantilla" / "plantilla-capitulo.html")
DESTINO = _ruta("TALLER3_DESTINO", RAIZ / "Htmls_Espacial" / "taller-3-sig-caps-1-5.html")
D = json.loads(_ruta("TALLER3_DATOS", SALIDAS / "taller3_datos.json").read_text(encoding="utf-8"))

ENTREGA = "martes 17 de noviembre de 2026"
HORA_LIMITE = "11:00"
QGIS_VERSION = "3.44.15"
SEMILLA_ENVOLVENTE = D["semilla"]
PESOS = {1: 15, 2: 20, 3: 30, 4: 20, 5: 15}


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


def lista(valores):
    """«3, 4 o 5», para decir qué valores puede traer una variante."""
    v = [str(x) for x in valores]
    return ", ".join(v[:-1]) + " o " + v[-1]


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


def variante(nota=""):
    """La tira que resuelve el documento, repetida en cada tarea."""
    return f"""      <div class="simulador" data-simulador="taller3-variante">
        <h4><i class="fas fa-fingerprint" aria-hidden="true"></i> Tu variante</h4>
        <p class="simulador-intro">Escribe tu número de documento <strong>completo</strong>,
          no los tres últimos dígitos. {nota}</p>
        <div class="simulador-controles"></div>
        <div class="simulador-lectura"></div>
      </div>
"""


def pasos(titulo, items):
    """El recorrido en QGIS: una lista numerada de pasos."""
    li = "\n".join(f"          <li>{x}</li>" for x in items)
    return f"""      <div class="pasos-qgis">
        <h4><i class="fas fa-route" aria-hidden="true"></i> {titulo}</h4>
        <ol>
{li}
        </ol>
      </div>
"""


def herr(nombre, ident):
    """Una herramienta de la caja de procesos: su nombre en pantalla y su identificador."""
    return f'<strong>{nombre}</strong> <code class="id-alg">{ident}</code>'


def tarea(num, titulo, enunciado, literales, pista):
    """Lo que se entrega de una tarea, con pista y SIN panel de solución."""
    items = "\n".join(f"          <li>{x}</li>" for x in literales)
    return f"""      <div class="ejercicio-guiado">
        <p class="ejercicio-enunciado"><span class="ejercicio-numero">T{num}.</span><strong>{titulo}
          </strong> <span class="badge-peso">{PESOS[num]}&nbsp;%</span><br>{enunciado}</p>
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


CIFRA = '<span class="cifra-control">cifra</span>'
FRASE = '<span class="frase-control">lectura</span>'

# =====================================================================
# MÓDULO 1 · Cómo se trabaja este taller
# =====================================================================
MOD1 = cabecera(
    1, "Cómo se trabaja este taller", "Read this first",
    "Nada. Este módulo no se califica: instala lo que hace falta, resuelve tu variante y dice "
    "qué se entrega.") + f"""
      <p>Este taller recorre <strong>los capítulos 1 a 5</strong> en un SIG de escritorio,
        <strong>QGIS</strong>. Es <strong>guiado</strong>: cada tarea trae sus pasos, con el nombre
        de cada herramienta tal como sale en tu pantalla. No se evalúa que sepas dónde está un
        botón. Se evalúan dos cosas: que <strong>tus cifras de control salgan</strong> —eso prueba
        que hiciste el recorrido, y sobre tu variante— y que digas <strong>qué calculó cada
        botón</strong>: con qué ventana, con qué borde, y por qué su cifra no es la que daría R.</p>

      <div class="definition">
        <h3>Por qué un SIG ahora, si el curso se escribe</h3>
        <p style="margin-bottom:0;">El <a href="capitulo-2-crs-georreferenciacion.html">capítulo 2</a>
          lo dijo en su primer módulo: el SIG de este curso se escribe en vez de pulsarse, porque
          <strong>un clic no deja rastro</strong>. Eso sigue en pie. Pero fuera de aquí vas a
          recibir mapas y cifras hechos con clics, y hay que saber leerlos. Este taller hace las
          dos cosas: usa QGIS para lo que QGIS hace bien, y le obliga a dejar rastro —el proyecto,
          el GeoPackage de resultados y el historial de procesos se entregan—. Y donde QGIS no
          llega, lo dice, y vuelve a R.</p>
      </div>

      <div class="warning">
        <p style="margin-bottom:0;"><strong>Qué vale y cuándo se entrega.</strong> El taller cuenta
          como <strong>uno de los quices del Corte III</strong>. Se entrega el <strong>{ENTREGA}, a
          más tardar a las {HORA_LIMITE}</strong>, por Brightspace. No se aceptan entregas tarde. El
          trabajo completo son unas <strong>cuatro horas</strong>; no lo dejes para la víspera,
          porque la primera media hora es instalar.</p>
      </div>

      <h3>Lo que hay que instalar, en este orden</h3>

      <ol class="lista-literales" type="1">
        <li><strong>QGIS {QGIS_VERSION}</strong>, que es la versión de largo plazo (LTR). Se
          descarga gratis de <a href="https://qgis.org/download/" target="_blank"
          rel="noopener">qgis.org/download</a>: en Windows, el instalador de la «Long Term
          Version»; en macOS, el de «Long Term Release». Es libre: no hay licencia que pedir. El
          taller se construyó y se comprobó con esa versión; con otra, tus cifras de control
          pueden no coincidir.</li>
        <li><strong>El complemento del taller.</strong>
          <a class="enlace-plantilla" href="../entrega/qgis/taller3_espacial.zip" download target="_blank"
          rel="noopener">Descarga <code>taller3_espacial.zip</code></a> y <strong>no lo
          descomprimas</strong>. En QGIS: menú <strong>Complementos ▸ Administrar e instalar
          complementos…</strong>, pestaña <strong>Instalar a partir de ZIP</strong>, elige el archivo
          y pulsa <strong>Instalar complemento</strong>. QGIS avisa de que es código de un origen que
          no conoce; es el del curso, y puedes abrir el ZIP y leerlo. No instala nada más.</li>
        <li><strong>La caja de herramientas.</strong> Menú <strong>Procesos ▸ Caja de
          herramientas</strong>. Al final de la lista tiene que aparecer el grupo <strong>«Taller 3 ·
          Estadística espacial»</strong>, con cuatro herramientas numeradas del 0 al 3. Si no
          aparece, el complemento no se instaló.</li>
        <li><strong>R</strong>, el que ya usas en el curso, con <code>sf</code> y
          <code>spatstat</code>. Solo lo pide la última tarea.</li>
      </ol>

      <div class="note">
        <p><strong>Los datos.</strong> Dos archivos. Guárdalos en una carpeta nueva, por ejemplo
          <code>taller3/</code>, y trabaja siempre ahí.</p>
        <ul class="lista-literales">
          <li><a href="../entrega/datos/taller3.gpkg" download target="_blank" rel="noopener">
            descargar <code>taller3.gpkg</code></a> — un GeoPackage con dos capas en
            <strong>EPSG:9377</strong>: <code>localidades</code>, las {D["ciudad"]["localidades"]}
            del Distrito, y <code>perimetro_urbano</code>.</li>
          <li><a href="../entrega/datos/taller3_sedes_3857.geojson" download target="_blank"
            rel="noopener">descargar <code>taller3_sedes_3857.geojson</code></a> — las
            {ent(D["ciudad"]["sedes"])} sedes educativas de Bogotá. Vienen <strong>en otro sistema
            de referencia, a propósito</strong>: reproyectarlas es la primera tarea, y todo lo
            demás depende de haberlo hecho bien.</li>
        </ul>
        <p style="margin-bottom:0;">Ninguna capa trae conteos, áreas ni densidades: los calculas
          tú. Y las sedes no traen su localidad: <strong>la pertenencia es geométrica</strong>, son
          tuyas las que caen dentro del polígono de tu localidad.</p>
      </div>

      <h3>Tres ajustes del proyecto, antes de empezar</h3>

      <p>Abre QGIS, crea un proyecto nuevo y guárdalo en tu carpeta como
        <code>taller3.qgz</code>. Después, en <strong>Proyecto ▸ Propiedades…</strong>:</p>

      <ol class="lista-literales" type="1">
        <li>Pestaña <strong>SRC</strong>: elige <strong>EPSG:9377</strong> (MAGNA-SIRGAS / Origen
          Nacional). Es el sistema en el que se mide en este taller.</li>
        <li>Pestaña <strong>General</strong>, apartado <strong>Mediciones</strong>: comprueba que en
          <strong>Elipsoide</strong> diga <strong>Ninguno/Planimétrico</strong>, y si no, elígelo. Con un elipsoide
          puesto, QGIS mide distancias y áreas sobre la superficie curva y no sobre el plano de la
          proyección: es la diferencia del capítulo 2, módulo 6, y mueve las últimas cifras
          de varias de tus cifras de control.</li>
        <li>Para las áreas, en este taller se escribe siempre <code>area($geometry)</code>, que
          mide en el plano de la capa, y <strong>no</strong> <code>$area</code>, que obedece al
          ajuste anterior. Con el elipsoide en «Ninguno» dan lo mismo; escribir la primera te
          protege si se te olvidó.</li>
      </ol>

      <div class="note">
        <p style="margin-bottom:0;"><strong>Cómo se guarda una capa, que el enunciado no va a
          repetir.</strong> Cada herramienta de la caja deja, por omisión, una capa
          <em>temporal</em>, que se pierde al cerrar QGIS. Al terminar cada tarea guarda las capas
          que el enunciado nombra en <code>monoespaciada</code>: botón derecho sobre la capa ▸
          <strong>Exportar ▸ Guardar objetos como…</strong>, formato GeoPackage, archivo
          <code>resultados.gpkg</code> en tu carpeta, y como nombre de capa el que el enunciado le
          da. Todas en el mismo archivo. Los rásteres del mapa de calor se guardan aparte, como
          <code>.tif</code>, desde el propio diálogo de la herramienta.</p>
      </div>

      <h3>Tu variante</h3>

      <p>Cada quien trabaja una <strong>localidad</strong> de Bogotá y cuatro números: el lado de la
        rejilla de cuadrantes ({lista(D["opciones"]["nx"])}), el radio en que se leen G y F
        ({lista(D["opciones"]["r_gf"])} metros), el radio en que se lee L
        ({lista(D["opciones"]["r_kl"])} metros) y el radio del mapa de calor
        ({lista(D["opciones"]["radio"])} metros). Los fija tu documento.</p>

""" + variante("Es lo primero: todo el taller depende de lo que salga aquí.") + f"""

      <div class="definition">
        <h3>Sobre usar inteligencia artificial: úsala</h3>
        <p style="margin-bottom:0;">Como en los otros talleres: sin pedir permiso, para lo que
          quieras. Dos condiciones. La <strong>bitácora</strong> es obligatoria: unas líneas en la
          portada con qué consultaste, qué te respondió y cómo comprobaste que era cierto. Y una
          advertencia práctica: un modelo no puede darte tus cifras de control, porque salen de
          correr QGIS sobre tu localidad, y suele equivocarse justo en lo que aquí se pregunta
          —qué área usa una herramienta, qué hace en el borde—. Compruébalo contra tu pantalla.</p>
      </div>

      <h3>Qué se entrega</h3>

      <div class="note">
        <p><strong>Dos archivos, por Brightspace, el {ENTREGA} a más tardar a las
          {HORA_LIMITE}.</strong></p>
        <ol class="lista-literales" type="1">
          <li><code>T3_Apellido_TuDocumento.pdf</code> — el escrito. La portada lleva tres cosas, y
            sin cualquiera de ellas la entrega está incompleta: la <strong>línea de
            identificación</strong> del buscador de arriba, la <strong>línea de entorno</strong>
            que te da la herramienta 0 en la primera tarea, y la <strong>bitácora</strong>.
            Después, por cada tarea, sus cifras de control y sus lecturas, con las letras del
            enunciado. <a class="enlace-plantilla" href="../entrega/plantilla_taller3.tex" download
            target="_blank" rel="noopener">Descargar la plantilla (<code>.tex</code>)</a> ·
            <a class="enlace-plantilla" href="../entrega/plantilla_taller3.pdf" target="_blank"
            rel="noopener">ver el PDF</a>. La plantilla es una ayuda, no una obligación: vale
            cualquier editor mientras el resultado sea un PDF con esa estructura.</li>
          <li><code>T3_Apellido_TuDocumento.zip</code> — tu proyecto <code>taller3.qgz</code> y tu
            <code>resultados.gpkg</code>. Es el rastro: las cifras del escrito tienen que poder
            leerse en esas capas.</li>
        </ol>
        <p style="margin-bottom:0;">Las cifras se escriben con <strong>cinco decimales</strong>
          cuando la herramienta los da, y con punto o coma decimal, como prefieras. Una cifra de
          control cuenta como correcta si coincide con la del curso en sus <strong>tres primeras
          cifras significativas</strong>.</p>
      </div>
""" + CIERRE


# =====================================================================
# MÓDULO 2 · T1 · Entorno y sistema de referencia (capítulos 1 y 2)
# =====================================================================
MOD2 = cabecera(
    2, "T1 · Reproyectar no es reetiquetar", "Coordinate reference systems",
    "Que distingas cambiar las coordenadas de cambiar la etiqueta, que sepas qué le hace una "
    "proyección a un área, y que digas qué es lo aleatorio en cada capa.") + f"""
      <p>Cubre el <a href="capitulo-1-datos-espaciales.html">capítulo 1</a> (módulo 2, los tipos de
        dato) y el <a href="capitulo-2-crs-georreferenciacion.html">capítulo 2</a> (módulos 3 a 6:
        qué destruye una proyección, los EPSG, reproyectar frente a reetiquetar, y medir).</p>

""" + variante() + f"""

""" + pasos("El recorrido en QGIS", [
    f"Caja de herramientas ▸ grupo «Taller 3 · Estadística espacial» ▸ <strong>0 · Entorno y línea "
    f"de identificación</strong>. Elige tu <code>taller3.gpkg</code>, escribe tu documento y pulsa "
    f"Ejecutar. En la pestaña <strong>Registro</strong> sale una línea que empieza por "
    f"<code>T3 · doc</code>: cópiala tal cual, va en la portada.",
    "Arrastra <code>taller3.gpkg</code> a la ventana de QGIS y carga sus dos capas. Arrastra "
    "después <code>taller3_sedes_3857.geojson</code>. Botón derecho sobre la capa de sedes ▸ "
    "<strong>Propiedades ▸ Información</strong>: anota su SRC y su número de objetos.",
    f"{herr('Reproyectar capa', 'native:reprojectlayer')}: capa de entrada, las sedes; SRC "
    f"objetivo, <strong>EPSG:9377</strong>. Guarda el resultado como <code>sedes</code>. "
    f"<strong>Esta es la capa de sedes con la que se trabaja el resto del taller.</strong>",
    f"{herr('Asignar proyección', 'native:assignprojection')}: capa de entrada, otra vez las sedes "
    f"<em>originales</em>; SRC asignado, EPSG:9377. Guarda el resultado como "
    f"<code>sedes_reetiquetadas</code>.",
    f"{herr('Contar puntos en un polígono', 'native:countpointsinpolygon')}: polígonos, "
    f"<code>localidades</code>; puntos, <code>sedes_reetiquetadas</code>. Abre la tabla de "
    f"atributos del resultado y mira la columna <code>NUMPOINTS</code>. Haz después «Zum a la "
    f"capa» sobre <code>sedes_reetiquetadas</code> y mira dónde quedó.",
    f"{herr('Reproyectar capa', 'native:reprojectlayer')} sobre <code>localidades</code>, ahora "
    f"hacia <strong>EPSG:3857</strong>. Guárdala como <code>localidades_3857</code>.",
    f"{herr('Calculadora de campos', 'native:fieldcalculator')}, una vez sobre "
    f"<code>localidades</code> y otra sobre <code>localidades_3857</code>: campo nuevo "
    f"<code>area_km2</code>, tipo decimal, precisión 5, fórmula "
    f"<code>area($geometry) / 1000000</code>. Lee el área de <strong>tu</strong> localidad en las "
    f"dos tablas.",
]) + f"""

""" + tarea(1, "Reproyectar no es reetiquetar",
       "Con lo que acabas de hacer, entrega:",
       [
    f"{CIFRA} El SRC con el que llega la capa de sedes y cuántos objetos trae.",
    f"{CIFRA} Cuántas sedes de <code>sedes_reetiquetadas</code> caen dentro de alguna localidad. "
    f"{FRASE} En dos líneas: qué hizo «Asignar proyección» con las coordenadas, qué hizo "
    f"«Reproyectar capa», y dónde quedaron en el mapa las sedes reetiquetadas.",
    f"{CIFRA} El área de tu localidad en EPSG:9377 y en EPSG:3857, en km², y cuánto por ciento "
    f"difieren. {FRASE} Cuál de las dos usarías para calcular una densidad de sedes y por qué; y "
    f"si esa diferencia sería mayor, menor o igual para una ciudad a 60° de latitud.",
    f"{FRASE} De las dos capas con las que vas a trabajar —las sedes y las localidades con su "
    f"conteo de sedes—, di qué tipo de dato espacial es cada una y <strong>qué es lo "
    f"aleatorio</strong> en cada una.",
       ],
       "Para (c), el capítulo 2 midió el error de área de cada municipio en cada sistema (módulo 4) "
       "y dijo qué conserva y qué destruye una proyección conforme (módulo 3). Para (d), la tabla "
       "de los tres tipos del capítulo 1, módulo 2, tiene una columna que se llama justo así.") + f"""
""" + CIERRE


# =====================================================================
# MÓDULO 3 · T2 · Del conteo al mapa (capítulo 3)
# =====================================================================
MOD3 = cabecera(
    3, "T2 · Del conteo al mapa, y otra vez", "Choropleths and the MAUP",
    "Que normalices antes de mapear, que veas que el esquema de clases decide el mapa, y que "
    "reconozcas el problema de la unidad de área modificable cuando cambias las unidades.") + f"""
      <p>Cubre el <a href="capitulo-3-cartografia-maup.html">capítulo 3</a>: normalizar (módulo 2),
        los esquemas de clasificación (módulos 3 y 4) y el efecto escala del MAUP (módulo 8).</p>

""" + variante() + f"""

""" + pasos("El recorrido en QGIS", [
    f"{herr('Contar puntos en un polígono', 'native:countpointsinpolygon')}: polígonos, "
    f"<code>localidades</code>; puntos, <code>sedes</code> (la reproyectada). Guarda el resultado "
    f"como <code>localidades_conteo</code>.",
    f"{herr('Calculadora de campos', 'native:fieldcalculator')} sobre "
    f"<code>localidades_conteo</code>: campo nuevo <code>densidad</code>, decimal, precisión 5, "
    f"fórmula <code>\"NUMPOINTS\" / (area($geometry) / 1000000)</code>. Son sedes por km². Guarda "
    f"el resultado encima de <code>localidades_conteo</code> o con ese mismo nombre.",
    "Abre la tabla de atributos y ordénala, pulsando la cabecera, primero por "
    "<code>NUMPOINTS</code> y luego por <code>densidad</code>, de mayor a menor. Anota el puesto de "
    "tu localidad en cada orden.",
    "Botón derecho sobre la capa ▸ <strong>Propiedades ▸ Simbología</strong>: tipo "
    "<strong>Graduado</strong>, valor <code>densidad</code>, <strong>5 clases</strong>, modo "
    "<strong>Conteo igual (cuantil)</strong>, y pulsa Clasificar. Anota en qué clase cae tu "
    "localidad, contando desde la más baja (1) hasta la más alta (5).",
    "Duplica la capa (botón derecho ▸ Duplicar capa) y en la copia cambia el modo a "
    "<strong>Rupturas naturales (Jenks)</strong>, con las mismas 5 clases. Anota otra vez la clase "
    "de tu localidad, y cuenta cuántas de las "
    f"{D['ciudad']['localidades']} localidades no están en la misma clase en los dos mapas.",
    f"{herr('Crear cuadricula', 'native:creategrid')}: tipo de cuadrícula, <strong>Rectángulo "
    f"(polígono)</strong>; extensión de la cuadrícula, «Calcular a partir de capa» ▸ "
    f"<code>perimetro_urbano</code>; espaciado horizontal y vertical, <strong>2000</strong> metros; "
    f"SRC, EPSG:9377. Repite con <strong>4000</strong>.",
    f"{herr('Contar puntos en un polígono', 'native:countpointsinpolygon')} sobre cada cuadrícula, "
    f"con <code>sedes</code>. Guarda los resultados como <code>rejilla_2000</code> y "
    f"<code>rejilla_4000</code>. De cada una necesitas tres números de su columna "
    f"<code>NUMPOINTS</code>: cuántas celdas tienen al menos una sede, el máximo y la suma. Los da "
    f"{herr('Basic statistics for fields', 'native:basicstatisticsforfields')} —su nombre sale en inglés—, o el panel "
    f"<strong>Ver ▸ Paneles ▸ Estadísticas</strong>.",
]) + f"""

""" + tarea(2, "Del conteo al mapa, y otra vez",
       "Entrega:",
       [
    f"{CIFRA} El número de sedes de tu localidad, su densidad en sedes por km², y su puesto entre "
    f"las {D['ciudad']['localidades']} por conteo y por densidad. {FRASE} En una línea: qué "
    f"pregunta contesta el mapa del conteo y cuál el de la densidad.",
    f"{CIFRA} La clase de tu localidad (de 1 a 5) con cuantiles y con Jenks, y cuántas localidades "
    f"cambian de clase entre los dos mapas. {FRASE} Qué optimiza cada esquema, y cuál de los dos "
    f"elegirías para <em>esta</em> variable, mirando cómo se reparten sus {D['ciudad']['localidades']} "
    f"valores.",
    f"{CIFRA} Para la rejilla de 2 km y para la de 4 km: celdas con al menos una sede, máximo de "
    f"sedes en una celda y suma de sedes contadas. {FRASE} Por qué la suma no es "
    f"{ent(D['ciudad']['sedes'])}; y qué le pasó al mapa —y a su máximo— al cambiar el tamaño de la "
    f"unidad sin cambiar un solo dato. Di qué nombre tiene eso en el capítulo 3.",
       ],
       "El conteo de tu localidad tiene que ser el <em>n</em> que te dio el buscador. Si no lo es, "
       "no sigas: el error está en T1, en la capa de sedes. Para (b), el capítulo 3 enseñó el mismo "
       "dato con cinco esquemas (módulo 4) y contó cuántos municipios cambiaban de clase.") + f"""
""" + CIERRE


# =====================================================================
# MÓDULO 4 · T3 · El patrón de tu localidad (capítulo 4)
# =====================================================================
MOD4 = cabecera(
    4, "T3 · El patrón de tu localidad", "Point patterns in a real window",
    "Que sepas qué ventana usa cada herramienta, qué hipótesis contrasta cada cifra, y qué deja "
    "afirmar —y qué no— una curva que sale de su banda.") + f"""
      <p>Cubre el <a href="capitulo-4-patrones-puntuales.html">capítulo 4</a> entero: la ventana
        (módulo 1), el test de cuadrantes y su tamaño (5 y 6), G y F (7), K y L (8), el borde (10) y
        las envolventes (11). La ventana es <strong>el polígono de tu localidad</strong>, no su caja.</p>

""" + variante() + f"""

""" + pasos("El recorrido en QGIS", [
    f"{herr('Extraer por expresión', 'native:extractbyexpression')} sobre "
    f"<code>localidades</code>, con la expresión <code>\"localidad\" = 'Tu localidad'</code>, con el "
    f"nombre <strong>exacto</strong> del buscador. Guarda el resultado como "
    f"<code>mi_localidad</code>.",
    f"{herr('Extraer por ubicacion', 'native:extractbylocation')}: extraer objetos de "
    f"<code>sedes</code>; predicado geométrico, <strong>intersecan</strong>; comparando con los "
    f"objetos de <code>mi_localidad</code>. Guarda el resultado como <code>mis_sedes</code>. Su "
    f"número de objetos tiene que ser tu <em>n</em>.",
    f"Grupo del taller ▸ <strong>1 · Test de cuadrantes (χ²) sobre la ventana real</strong>: capa "
    f"de puntos, <code>sedes</code>; capa de polígonos, <code>localidades</code>; filtro de la "
    f"ventana, la misma expresión del primer paso; columnas y filas, el <strong>NX</strong> de tu "
    f"variante en las dos. Guarda la capa «Cuadrantes recortados» como <code>cuadrantes</code> y "
    f"lee las cifras en el Registro o en el informe.",
    f"{herr('Análisis de vecinos más próximos', 'native:nearestneighbouranalysis')} sobre "
    f"<code>mis_sedes</code>. Devuelve cinco cifras: distancia media observada, distancia media "
    f"esperada, índice de vecinos más próximos, número de puntos y puntaje Z.",
    "A mano, o en la calculadora que prefieras: la distancia esperada bajo un Poisson homogéneo es "
    "\\(0.5 / \\sqrt{n / A}\\). Calcúlala con el <strong>área de tu localidad</strong> en m² "
    "—la tienes de T1— y divide la distancia observada por ella. Ese es el índice con la ventana "
    "real. Despeja también, de la distancia esperada que dio QGIS, qué área usó QGIS.",
    f"Grupo del taller ▸ <strong>2 · Funciones G, F y J con corrección de borde</strong>: mismas "
    f"capas y mismo filtro; radio máximo 600, paso 10, sitios por lado 200, y como radio de lectura "
    f"el <strong>radio de G y F</strong> de tu variante. Guarda la tabla como <code>gf</code> y abre "
    f"el informe: trae la gráfica.",
    f"Grupo del taller ▸ <strong>3 · K y L de Ripley con envolvente de simulación</strong>: mismas "
    f"capas y mismo filtro; radio máximo 1000, paso 25, <strong>99</strong> simulaciones, semilla "
    f"<strong>{SEMILLA_ENVOLVENTE}</strong>, y como radio de lectura el <strong>radio de L</strong> "
    f"de tu variante. Guarda la tabla como <code>kl</code> y abre el informe.",
]) + f"""

      <div class="note">
        <p style="margin-bottom:0;"><strong>Las tres herramientas del taller son código que puedes
          leer.</strong> Están en el ZIP que instalaste: <code>nucleo.py</code> tiene las cuentas, en
          menos de cuatrocientas líneas y sin nada de QGIS. Corrigen el borde por <em>muestra
          reducida</em> —para cada r solo cuentan los puntos a más de r del borde de la ventana—,
          que es la corrección <code>"border"</code> del capítulo 4, módulo 10. Se contrastaron
          contra <code>spatstat</code> sobre estas mismas localidades.</p>
      </div>

""" + tarea(3, "El patrón de tu localidad",
       "Entrega:",
       [
    f"{CIFRA} Del test de cuadrantes: χ², grados de libertad, p de la cola derecha y el menor "
    f"conteo esperado. {FRASE} Qué hipótesis nula se contrasta —entera, no solo «λ constante»—; "
    f"por qué los grados de libertad pueden no ser NX² − 1; y si con ese menor esperado la "
    f"aproximación χ² se sostiene.",
    f"{CIFRA} El índice de vecino más próximo que da QGIS, el área que usó QGIS (en km²), y el "
    f"índice recalculado con el área de tu localidad. {FRASE} Qué ventana usó QGIS sin decírtelo, "
    f"por qué no es la tuya, y en qué dirección movió tu índice. Di también qué corrección de borde "
    f"aplica esa herramienta.",
    f"{CIFRA} G, F y la curva de Poisson en tu radio de lectura. {FRASE} Qué mide cada una —desde "
    f"dónde se mide la distancia en G y desde dónde en F—, y qué dice de tu localidad el orden en "
    f"que quedan las tres.",
    f"{CIFRA} L(r) − r en tu radio de lectura, los dos extremos de la banda en ese radio, y cuántos "
    f"de tus <em>n</em> puntos están a más de r del borde. {FRASE} Si tu patrón queda dentro o "
    f"fuera de la banda; a qué nivel es ese contraste con 99 simulaciones y un r fijado de "
    f"antemano; y por qué no podrías decir lo mismo si hubieras elegido el r mirando la gráfica.",
       ],
       "Para (b): el informe de QGIS no nombra el área, pero la fórmula de la distancia esperada "
       "solo tiene una incógnita. Para (d): el capítulo 4, módulo 11, distingue la banda puntual de "
       "la global, y dice cuánto vale el nivel de una banda de mínimo y máximo con 99 simulaciones.") + f"""
""" + CIERRE


# =====================================================================
# MÓDULO 5 · T4 · La intensidad (capítulo 5, módulos 1 a 5)
# =====================================================================
MOD5 = cabecera(
    5, "T4 · El mapa de calor es un estimador", "Kernel intensity in a GIS",
    "Que leas un mapa de calor como una estimación de la intensidad, con sus unidades, su ancho "
    "de banda y su borde, y no como un dibujo.") + f"""
      <p>Cubre el <a href="capitulo-5-intensidad-nucleos.html">capítulo 5</a>, módulos 1 a 5: de
        contar a suavizar, el ancho de banda, y la corrección de borde, con el
        <a href="apendice-a-densidad.html">apéndice A</a> detrás.</p>

""" + variante() + f"""

""" + pasos("El recorrido en QGIS", [
    f"{herr('Mapa de calor (Estimación de Densidad de Núcleo)', 'qgis:heatmapkerneldensityestimation')}: "
    f"capa de puntos, <code>mis_sedes</code>; <strong>Radio</strong>, el <strong>radio del mapa de "
    f"calor</strong> de tu variante, en metros; tamaño de píxel X e Y, <strong>50</strong>; forma "
    f"del núcleo (<em>Kernel shape</em>), <strong>Cuártico</strong>; escala del valor de salida "
    f"(<em>Output value scaling</em>), <strong>Escalado</strong>. Guarda el ráster como "
    f"<code>calor.tif</code>.",
    f"{herr('Estadísticas de capa ráster', 'native:rasterlayerstatistics')} sobre "
    f"<code>calor.tif</code>: anota el <strong>máximo</strong> y la <strong>suma</strong>.",
    f"{herr('Estadísticas de zona', 'native:zonalstatisticsfb')}: capa de entrada, "
    f"<code>mi_localidad</code>; capa ráster, <code>calor.tif</code>; estadísticas a calcular, solo "
    f"<strong>Suma</strong>. Guarda el resultado como <code>calor_zona</code> y lee la suma en su "
    f"tabla de atributos.",
    "Cada píxel mide 50 m × 50 m. Multiplica las dos sumas por el área de un píxel, en m²: la "
    "primera es la <strong>masa total</strong> del mapa y la segunda, la <strong>masa dentro de tu "
    "localidad</strong>. Multiplica el máximo por un millón para leerlo en sedes por km².",
    "Por último, mira el mapa: en <strong>Propiedades ▸ Simbología</strong> elige "
    "«Pseudocolor monobanda» y ponle una rampa secuencial. Súbelo o bájalo de la localidad en el "
    "panel de capas para ver dónde hay mapa fuera del polígono.",
]) + f"""

""" + tarea(4, "El mapa de calor es un estimador",
       "Entrega:",
       [
    f"{CIFRA} El máximo del mapa en sedes por km², la masa total, la masa dentro de tu localidad, y "
    f"qué porcentaje de la masa quedó fuera. {FRASE} Compara el máximo con el λ medio de tu "
    f"localidad —el del buscador— y di qué significa esa razón.",
    f"{FRASE} La masa total, ¿con qué número de tu variante coincide, y por qué tiene que "
    f"coincidir con un núcleo que integra 1? La de dentro es menor: di qué supone el mapa sobre el "
    f"territorio de fuera del polígono, qué hace una corrección de borde con esa masa, y qué "
    f"consecuencia tiene para la intensidad estimada <em>cerca del borde</em>.",
    f"{CIFRA} El σ que corresponde a tu radio: en un núcleo cuártico, \\(\\sigma = "
    f"\\text{{radio}} / \\sqrt{{8}}\\). {FRASE} Por qué el «radio» de QGIS y el σ de "
    f"<code>density()</code> no son el mismo número aunque gobiernen lo mismo; y qué le pasaría al "
    f"máximo y al porcentaje de fuera si duplicaras el radio.",
       ],
       "Para (b), el capítulo 5, módulo 4, comprobó las tres opciones de borde con una sola "
       "pregunta: ¿la integral de la intensidad estimada es <em>n</em>? Para (c), el módulo 2 "
       "movió el núcleo y movió el ancho de banda, y midió cuál de los dos cambia el mapa.") + f"""
""" + CIERRE


# =====================================================================
# MÓDULO 6 · T5 · Lo que el SIG no hace (capítulo 5, módulos 3, 4, 8 y 9)
# =====================================================================
BLOQUE_R = """library(sf)
library(spatstat)

MI_LOCALIDAD &lt;- ""     # el nombre EXACTO del buscador
MI_RADIO     &lt;- 0      # el radio de tu mapa de calor, en metros
MI_N         &lt;- 0      # tu n, para que esto PARE si algo no cuadra

loc   &lt;- st_read("taller3.gpkg", layer = "localidades", quiet = TRUE)
sedes &lt;- st_read("taller3_sedes_3857.geojson", quiet = TRUE)
sedes &lt;- st_transform(sedes, 9377)                 # reproyectar, no reetiquetar
stopifnot(MI_LOCALIDAD %in% loc$localidad, MI_RADIO &gt; 0)

# El patrón: las sedes que caen dentro del polígono, con el polígono por ventana
w  &lt;- as.owin(st_geometry(loc[loc$localidad == MI_LOCALIDAD, ]))
xy &lt;- st_coordinates(sedes)
d  &lt;- inside.owin(xy[, 1], xy[, 2], w)
p  &lt;- ppp(xy[d, 1], xy[d, 2], window = w, check = FALSE)
stopifnot(npoints(p) == MI_N)

# (a) El mapa de calor de QGIS, rehecho: núcleo cuártico, píxel de 50 m
sigma &lt;- MI_RADIO / sqrt(8)
sin &lt;- density(p, sigma = sigma, kernel = "quartic", edge = FALSE, eps = 50)
con &lt;- density(p, sigma = sigma, kernel = "quartic", edge = TRUE, diggle = TRUE, eps = 50)
c(pico_sin = max(sin) * 1e6, masa_sin = integral(sin),
  pico_con = max(con) * 1e6, masa_con = integral(con))

# (b) El ancho de banda que QGIS no elige
s &lt;- c(diggle = bw.diggle(p), ppl = bw.ppl(p))
rbind(sigma = s, radio_qgis = s * sqrt(8))

# (c) Un modelo: la intensidad como función de la posición, centrada y en km
q &lt;- rescale(shift(p, origin = "centroid"), 1000, "km")
coef(summary(ppm(q ~ x + y)))"""

MOD6 = cabecera(
    6, "T5 · Lo que el SIG no hace", "Where the GIS stops",
    "Que digas con precisión qué decisiones toma R que QGIS no te dejó tomar, y qué cambia en "
    "las cifras cuando se toman.") + f"""
      <p>Cubre el <a href="capitulo-5-intensidad-nucleos.html">capítulo 5</a>, módulos 3 (los
        selectores), 4 (el borde), 8 y 9 (el Poisson inhomogéneo y <code>ppm</code>), con una mirada
        al 11. QGIS no trae un selector de ancho de banda, ni corrección de borde en el mapa de
        calor, ni un modelo de la intensidad. R sí, y son las tres cosas que este bloque hace sobre
        <strong>tu misma localidad</strong>.</p>

""" + variante() + f"""

      <p>Copia el bloque en un script, en la carpeta de tus datos, rellena las tres primeras líneas
        y córrelo entero. No hay que escribir nada más.</p>

      <pre><code class="language-r arranque">{BLOQUE_R}</code></pre>

""" + tarea(5, "Lo que el SIG no hace",
       "Entrega:",
       [
    f"{CIFRA} <code>pico_sin</code>, <code>masa_sin</code>, <code>pico_con</code> y "
    f"<code>masa_con</code>. {FRASE} Con cuál de tus cifras de T4 hay que comparar "
    f"<code>masa_sin</code> y con cuál <code>masa_con</code>; y por qué el pico de R y el de QGIS se "
    f"parecen pero no son idénticos aunque el núcleo, el ancho y el píxel sean los mismos.",
    f"{CIFRA} Los dos σ que eligen los selectores y sus dos radios equivalentes en QGIS. {FRASE} "
    f"Qué optimiza cada selector; si tu radio de T4 suavizaba de más o de menos frente a cada uno; "
    f"y qué harías si los dos no se ponen de acuerdo.",
    f"{CIFRA} Los dos coeficientes de <code>x</code> y de <code>y</code> y sus dos valores z. "
    f"{FRASE} Qué dice cada coeficiente sobre hacia dónde crece la intensidad, y si concuerda con tu "
    f"mapa de calor. Y lo que importa: a la vista de tu T3(d), di si esos valores z son de fiar, y "
    f"por qué.",
    f"{FRASE} En tres líneas, el balance: una cosa que QGIS te dio más fácil que R, y las dos "
    f"decisiones que QGIS tomó por ti sin decírtelo en este taller.",
       ],
       "Para (c): el capítulo 5, módulo 9, dice cuándo los errores estándar de un Poisson dejan de "
       "valer, y el módulo 11 midió cuánto se equivocan. Lo que decide es algo que ya mediste en T3.") + f"""
""" + CIERRE


# =====================================================================
# MÓDULO 7 · Cómo se califica
# =====================================================================
MOD7 = cabecera(
    7, "Cómo se califica", "Grading",
    "Nada nuevo: aquí está la rúbrica y la lista de lo que tiene que traer tu entrega.") + f"""
      <p>Las cinco tareas pesan distinto, según lo que cubren:</p>

      <table>
        <caption>Las cinco tareas del taller y su peso</caption>
        <thead>
          <tr><th scope="col">Tarea</th><th scope="col">De qué va</th><th scope="col">Capítulos</th>
              <th scope="col">Peso</th></tr>
        </thead>
        <tbody>
          <tr><th scope="row">T1</th><td>Reproyectar no es reetiquetar</td><td>1 y 2</td>
              <td>{PESOS[1]}&nbsp;%</td></tr>
          <tr><th scope="row">T2</th><td>Del conteo al mapa, y otra vez</td><td>3</td>
              <td>{PESOS[2]}&nbsp;%</td></tr>
          <tr><th scope="row">T3</th><td>El patrón de tu localidad</td><td>4</td>
              <td>{PESOS[3]}&nbsp;%</td></tr>
          <tr><th scope="row">T4</th><td>El mapa de calor es un estimador</td><td>5</td>
              <td>{PESOS[4]}&nbsp;%</td></tr>
          <tr><th scope="row">T5</th><td>Lo que el SIG no hace</td><td>5</td>
              <td>{PESOS[5]}&nbsp;%</td></tr>
        </tbody>
      </table>

      <p>Dentro de cada tarea, cada literal trae marcado qué pide: una {CIFRA} de control, una
        {FRASE}, o las dos. Y las tres dimensiones de la rúbrica se aplican al taller entero:</p>

      <div class="rubrica" data-rubrica="taller3"></div>

      <div class="warning">
        <p style="margin-bottom:0;"><strong>Si resuelves una variante que no es la tuya</strong>, se
          califica la que escribiste en la portada y se descuenta en la tercera dimensión, como en
          los otros talleres. Lo evita mirar una sola cosa antes de empezar T2: que el conteo de tu
          localidad sea el <em>n</em> del buscador.</p>
      </div>

      <div class="note">
        <p style="margin-bottom:0;"><strong>Qué se entrega, otra vez y en corto.</strong> El
          <strong>{ENTREGA}, a más tardar a las {HORA_LIMITE}</strong>, por Brightspace: un PDF con
          la portada completa —línea de identificación, línea de entorno y bitácora— y las cinco
          tareas; y un ZIP con <code>taller3.qgz</code> y <code>resultados.gpkg</code>.</p>
      </div>
""" + CIERRE


# =====================================================================
# El ensamblado
# =====================================================================
MODULOS = MOD1 + MOD2 + MOD3 + MOD4 + MOD5 + MOD6 + MOD7

MODULOS_NAV = [
    ("Cómo se trabaja este taller", "30 min"),
    ("T1 · Reproyectar no es reetiquetar", "35 min"),
    ("T2 · Del conteo al mapa, y otra vez", "45 min"),
    ("T3 · El patrón de tu localidad", "60 min"),
    ("T4 · El mapa de calor es un estimador", "35 min"),
    ("T5 · Lo que el SIG no hace", "35 min"),
    ("Cómo se califica", "5 min"),
]

_mods = ",\n".join(
    f'        {{ id: {i + 1}, title: "{t}", duration: "{d}" }}'
    for i, (t, d) in enumerate(MODULOS_NAV))

COURSE_DATA = f"""    const courseData = {{
      modules: [
{_mods}
      ]
    }};

    // El taller, tal como sale de precalculo/genera_taller3.R. Nada de lo
    // que hay aquí es una respuesta: es la variante de cada documento y,
    // de cada localidad, lo que el enunciado ya dice.
    const DATOS_T3 = {json.dumps(D, ensure_ascii=False)};

    const n5 = (x, d = 5) => Number(x).toFixed(d);
    const escT3 = s => String(s).replace(/&/g, '&amp;')
      .replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');

    // La variante viva. Sobrevive al cambio de módulo porque loadModule()
    // vacía mainContent en cada salto. Se guarda el documento COMPLETO y
    // tal como se tecleó: es lo que el estudiante tiene que ver escrito.
    const T3_LLAVE = 'taller3-documento';
    const T3_MIN_DIGITOS = 6;
    let T3_DOC = '';
    try {{
      T3_DOC = window.localStorage.getItem(T3_LLAVE) || '';
    }} catch (e) {{ /* navegador sin almacenamiento: se pide cada vez */ }}

    const t3Digitos = txt => String(txt).replace(/\\D/g, '');

    function t3Resuelve(txt) {{
      const d = t3Digitos(txt);
      if (d.length < T3_MIN_DIGITOS) return null;
      const clave = d.slice(-3);
      const v = DATOS_T3.variantes.find(x => x.clave === clave);
      if (!v) return null;
      return {{ documento: String(txt), clave: clave, v: v, loc: DATOS_T3.localidades[v.localidad] }};
    }}
"""

SIMULADORES_JS = """    // --- El buscador de variante -------------------------------------
    // Ninguna aritmética: la fila viene precalculada en R. Se pide el
    // documento COMPLETO y se devuelve escrito; por debajo de seis dígitos
    // no resuelve, y lo dice (la lección del Taller 1).
    SIMULADORES['taller3-variante'] = function (raiz) {
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
        const r = t3Resuelve(T3_DOC);
        if (!r) {
          const d = t3Digitos(T3_DOC);
          lectura.innerHTML = d.length === 0
            ? `<p style="margin:0;">Escribe tu número de documento <strong>completo</strong>
                 para ver qué te toca.</p>`
            : `<p style="margin:0;">Llevas <strong>${d.length}</strong>
                 ${d.length === 1 ? 'dígito' : 'dígitos'}. Hacen falta al menos
                 <strong>${T3_MIN_DIGITOS}</strong>: este buscador pide el documento
                 <strong>completo</strong>, no los tres últimos dígitos.</p>`;
          return;
        }
        const v = r.v, L = r.loc;
        // La línea que va LITERAL en la portada, en ASCII a propósito.
        const linea = `${escT3(r.documento)} · variante ${v.clave} · ${v.localidad}`
          + ` · n = ${L.n} · lambda = ${n5(L.lambda)} sedes/km2`
          + ` · NX = ${v.nx} · r de G y F = ${v.r_gf} m · r de L = ${v.r_kl} m`
          + ` · radio = ${v.radio} m`;
        lectura.innerHTML = `
          <p style="margin:0 0 0.5rem 0;">Esta línea va <strong>copiada literal</strong> en la
            portada. Compruébala carácter a carácter: el número que aparece aquí es el que tú
            tecleaste.</p>
          <code class="linea-id">${linea}</code>
          <table>
            <caption class="sr-only">Tu variante del taller</caption>
            <tbody>
              <tr><th scope="row">Tu documento, como lo escribiste</th>
                  <td><code>${escT3(r.documento)}</code></td></tr>
              <tr><th scope="row">Variante</th><td><code>${v.clave}</code></td></tr>
              <tr><th scope="row">Tu localidad</th><td><strong>${v.localidad}</strong></td></tr>
              <tr><th scope="row">Sus sedes (tu <em>n</em>)</th><td><strong>${L.n}</strong></td></tr>
              <tr><th scope="row">Su área</th><td>${n5(L.area_km2)} km²</td></tr>
              <tr><th scope="row">Su λ medio</th><td>${n5(L.lambda)} sedes/km²</td></tr>
              <tr><th scope="row">NX, el lado de tu rejilla de cuadrantes (T3)</th>
                  <td><strong>${v.nx}</strong></td></tr>
              <tr><th scope="row">Tu radio de lectura de G y F (T3)</th>
                  <td><strong>${v.r_gf}</strong> m</td></tr>
              <tr><th scope="row">Tu radio de lectura de L (T3)</th>
                  <td><strong>${v.r_kl}</strong> m</td></tr>
              <tr><th scope="row">Tu radio del mapa de calor (T4 y T5)</th>
                  <td><strong>${v.radio}</strong> m</td></tr>
            </tbody>
          </table>`;
        // A mano: esta tabla nace DESPUÉS de que loadModule() haya llamado
        // a envolverTablas().
        envolverTablas();
      }

      function aplica(txt) {
        T3_DOC = txt;
        try { window.localStorage.setItem(T3_LLAVE, txt); } catch (e) { /* sin almacenamiento */ }
        document.querySelectorAll('.simulador').forEach(s => {
          if (s.__t3repinta) s.__t3repinta();
        });
      }

      raiz.__t3repinta = pinta;
      campo.addEventListener('input', () => aplica(campo.value));
      campo.value = T3_DOC;
      pinta();
    };

"""

RUBRICA_JS = """    RUBRICAS['taller3'] = {
      titulo: 'Rúbrica del taller',
      total: 100,
      intro: 'El taller cuenta como uno de los quices del Corte III. Las tres dimensiones se '
        + 'aplican a la entrega completa. Pulsa cada una para ver sus cuatro niveles.',
      nota: 'Los niveles son excluyentes y cada dimensión se puntúa por separado. Una cifra de '
        + 'control cuenta si coincide con la del curso en sus tres primeras cifras significativas.',
      rotuloAnula: 'Sin esto la entrega está incompleta',
      anulan: [
        'La <strong>línea de identificación</strong> del buscador, copiada literal en la portada.',
        'La <strong>línea de entorno</strong> de la herramienta 0, copiada literal en la portada.',
        'El <strong>ZIP</strong> con el proyecto y el GeoPackage de resultados.'
      ],
      criterios: [
        {
          clave: 'A', nombre: 'Cifras de control', puntos: 45,
          foco: 'Mide si <strong>hiciste el recorrido, y sobre tu variante</strong>. Cada cifra '
            + 'se contrasta contra la que da QGIS con tu localidad y tus cuatro números. Una cifra '
            + 'equivocada por un paso anterior mal hecho —unas sedes mal reproyectadas, un elipsoide '
            + 'sin quitar— arrastra a las siguientes: por eso hay que comprobar el <em>n</em> antes '
            + 'de seguir.',
          niveles: [
            { nombre: 'Excelente', rango: '41–45', observa: 'Todas las cifras de las cinco tareas coinciden, o falla una aislada.' },
            { nombre: 'Aceptable', rango: '30–40', observa: 'Coinciden las de cuatro tareas, o fallan cifras sueltas en varias sin que se arrastre un error de fondo.' },
            { nombre: 'Insuficiente', rango: '16–29', observa: 'Un error temprano se arrastra a varias tareas, o faltan las cifras de una o dos tareas.' },
            { nombre: 'No logrado', rango: '0–15', observa: 'Las cifras no corresponden a la variante, o faltan las de la mayoría de las tareas.' }
          ]
        },
        {
          clave: 'B', nombre: 'Lectura de lo que calculó cada herramienta', puntos: 40,
          foco: 'Mide si dices <strong>qué hizo el botón</strong>: con qué ventana, con qué '
            + 'borde, contra qué hipótesis, y qué deja afirmar la cifra y qué no. Repetir la '
            + 'definición no puntúa; usarla sobre tu cifra, sí.',
          niveles: [
            { nombre: 'Excelente', rango: '36–40', observa: 'Cada lectura nombra el supuesto de la herramienta, lo conecta con el módulo del capítulo y dice qué queda fuera de lo que la cifra prueba.' },
            { nombre: 'Aceptable', rango: '26–35', observa: 'Las lecturas son correctas; el supuesto o el límite se menciona solo en algunas.' },
            { nombre: 'Insuficiente', rango: '14–25', observa: 'Se describe lo que se pulsó en vez de lo que se calculó, o se le hace decir a la cifra más de lo que dice.' },
            { nombre: 'No logrado', rango: '0–13', observa: 'Las lecturas contradicen las cifras, o no están.' }
          ]
        },
        {
          clave: 'C', nombre: 'Rastro y honestidad', puntos: 15,
          foco: 'Mide si lo entregado <strong>se puede rehacer</strong>: que las cifras del escrito '
            + 'se lean en las capas del GeoPackage, que el proyecto abra, y que la bitácora diga qué '
            + 'se consultó con IA y cómo se comprobó. Aquí se descuenta resolver una variante ajena, '
            + 'y ese descuento <strong>tiene piso: no baja de 6</strong>.',
          niveles: [
            { nombre: 'Excelente', rango: '14–15', observa: 'El proyecto abre, las capas tienen los nombres del enunciado y las cifras del escrito están en ellas; la bitácora dice qué se verificó.' },
            { nombre: 'Aceptable', rango: '10–13', observa: 'El rastro está, con alguna capa sin guardar o sin nombre; la bitácora es razonable.' },
            { nombre: 'Insuficiente', rango: '6–9', observa: 'Faltan varias capas, o la bitácora es genérica, o las cifras del escrito no están en lo entregado.' },
            { nombre: 'No logrado', rango: '0–5', observa: 'No hay bitácora, o lo que declara es falso.' }
          ]
        }
      ]
    };
"""

QUIZ_JS = """    // Sin autoevaluación: en un taller la evaluación es el propio taller.
"""

CSS_EXTRA = """
    /* El distintivo de peso de cada tarea, pegado al título del enunciado. */
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

    /* Qué pide cada literal: una cifra de control o una lectura. Dos
       etiquetas con texto, no solo con color. */
    .cifra-control,
    .frase-control {
      display: inline-block;
      font-size: 0.68rem;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.03em;
      padding: 0.05rem 0.4rem;
      border-radius: 0.25rem;
      vertical-align: middle;
      margin-right: 0.15rem;
    }

    .cifra-control {
      background: #012820;
      color: #fff;
    }

    .frase-control {
      background: #fff;
      color: #9a3d00;
      border: 1px solid #9a3d00;
    }

    /* El recorrido en QGIS: pasos numerados, en su propia caja para que
       se distingan de lo que se entrega. */
    .pasos-qgis {
      margin: 1.25rem 0;
      padding: 1rem 1.1rem;
      background: #f6faf8;
      border: 1px solid #cfe1da;
      border-left: 4px solid #012820;
      border-radius: 0.5rem;
    }

    .pasos-qgis h4 {
      margin: 0 0 0.6rem 0;
      font-size: 1rem;
      font-weight: 700;
      color: #012820;
    }

    .pasos-qgis ol {
      margin: 0;
      padding-left: 1.5rem;
      list-style: decimal;
    }

    .pasos-qgis ol > li {
      margin-bottom: 0.6rem;
      color: #1e293b;
    }

    .pasos-qgis ol > li:last-child {
      margin-bottom: 0;
    }

    /* El identificador de una herramienta: se busca tal cual en la caja. */
    .id-alg {
      font-size: 0.78rem;
      color: #475569;
      background: #eef2f6;
      padding: 0.05rem 0.3rem;
      border-radius: 0.25rem;
      overflow-wrap: anywhere;
    }

    /* La línea de identificación que va literal en la portada. */
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

    .enlace-plantilla {
      background: #ffe58a;
      color: #012820;
      font-weight: 700;
      text-decoration: underline;
      text-underline-offset: 0.15em;
      padding: 0.05rem 0.3rem;
      border-radius: 0.25rem;
      -webkit-box-decoration-break: clone;
      box-decoration-break: clone;
    }

    .enlace-plantilla:hover {
      background: #ffd23f;
    }

    .enlace-plantilla:focus-visible {
      outline: 2px solid #FF6600;
      outline-offset: 2px;
    }
"""


def reemplaza_region(texto, abre, cierra, nuevo, que, max_lineas, min_lineas=0):
    """Sustituye entre `abre` y el primer `cierra` posterior, con DOS topes."""
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
    if sorted(PESOS) != [1, 2, 3, 4, 5] or sum(PESOS.values()) != 100:
        sys.exit(f"PARADO: los pesos de las cinco tareas suman {sum(PESOS.values())}, no 100")
    if len(D["variantes"]) != 1000:
        sys.exit(f"PARADO: hay {len(D['variantes'])} variantes y el buscador espera 1000")
    sin_localidad = sorted({v["localidad"] for v in D["variantes"]} - set(D["localidades"]))
    if sin_localidad:
        sys.exit(f"PARADO: variantes con una localidad sin ficha: {sin_localidad}")

    doc = PLANTILLA.read_text(encoding="utf-8")
    print(f"\n=== ensambla_taller3.py ===\nplantilla: {len(doc)/1024:.0f} KB\n")

    doc = sustituye(doc, "<title>Plantilla de capítulo — Estadística Espacial</title>",
                    "<title>Taller 3 · Los capítulos 1 a 5 en QGIS — Estadística Espacial</title>",
                    "título")
    doc = sustituye(doc, "PLANTILLA BASE •\n              5 MÓDULOS DE DEMOSTRACIÓN • UNBOSQUE 2026-II",
                    "TALLER 3 • CAPÍTULOS 1 A 5 EN QGIS •\n"
                    "              UNO DE LOS QUICES DEL CORTE III • UNBOSQUE 2026-II",
                    "subtítulo de la cabecera")
    doc = sustituye(doc, "Estadística Espacial (20929) • Plantilla de\n          capítulo • UnBosque 2026-II",
                    "Estadística Espacial (20929) • Taller 3 •\n"
                    "          Corte III • UnBosque 2026-II", "pie")

    doc = sustituye(doc, "    /* ------------------------------------------------------------------\n"
                         "       Componente .ciclo — diagrama de etapas recorrible",
                    CSS_EXTRA + "\n    /* ------------------------------------------------------------------\n"
                                "       Componente .ciclo — diagrama de etapas recorrible",
                    "el CSS propio del taller")

    doc = reemplaza_region(doc, "    const courseData = {", "\n    };\n", COURSE_DATA,
                           "courseData + DATOS_T3", max_lineas=20)

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
    doc = sustituye(doc, vieja[0],
                    "    // Este taller no publica mapas: el mapa lo hace el estudiante, en QGIS.",
                    "el mapa de demostración")

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
    doc = reemplaza_region(doc, "    SIMULACROS['demo'] = {", "\n    };\n",
                           "", "el simulacro de demostración", max_lineas=40)
    doc = reemplaza_region(doc, "    TABLAS_RANKING['demo'] = function () {", "\n    };\n",
                           "", "la tabla de ranking de demostración", max_lineas=40)

    DESTINO.parent.mkdir(parents=True, exist_ok=True)
    doc = aplica_boton(doc, DESTINO, RAIZ, "franja")
    DESTINO.write_text(doc, encoding="utf-8")

    # --- Guardas de salida ----------------------------------------------
    marcado = doc[:doc.rindex("\n  <script>")]
    mods = doc.count('<template id="module-')
    declarados = len(MODULOS_NAV)
    tareas = marcado.count('<div class="ejercicio-guiado">')
    tiras = marcado.count('data-simulador="taller3-variante"')

    try:
        donde = DESTINO.relative_to(RAIZ)
    except ValueError:
        donde = DESTINO
    print(f"\n{donde}  {len(doc)/1024:.0f} KB")
    print(f"  {mods} módulos ({declarados} declarados en la navegación) · "
          f"{tareas} tareas · {tiras} tiras de variante")

    problemas = []
    if mods != declarados:
        problemas.append(f"{mods} plantillas de módulo y {declarados} declaradas en la navegación")
    if tareas != len(PESOS):
        problemas.append(f"{tareas} tareas, se esperaban {len(PESOS)}")
    pesos = [int(x) for x in re.findall(r'class="badge-peso">(\d+)&nbsp;%', marcado)]
    if pesos != [PESOS[k] for k in sorted(PESOS)]:
        problemas.append(f"los pesos de las tareas en la página son {pesos}")

    CON_VARIANTE = {1, 2, 3, 4, 5, 6}
    trozos = dict(zip(
        [int(x) for x in re.findall(r'<template id="module-(\d+)">', marcado)],
        re.split(r'<template id="module-\d+">', marcado)[1:]))
    faltan = sorted(k for k in CON_VARIANTE
                    if 'data-simulador="taller3-variante"' not in trozos.get(k, ""))
    if faltan:
        problemas.append(f"a los módulos {faltan} les falta la tira de variante")

    if 'class="ejercicio-panel solucion"' in marcado:
        problemas.append("hay un panel de solución en el marcado, y este taller no lleva")
    botones = re.findall(r'<button[^>]*class="(?:derivacion|ejercicio)-boton"[^>]*>', marcado)
    for b in botones:
        if "aria-expanded" not in b or "aria-controls" not in b:
            problemas.append("un botón plegable sin aria-expanded/aria-controls")
        m = re.search(r'aria-controls="([^"]+)"', b)
        if m and f'id="{m.group(1)}"' not in marcado:
            problemas.append(f"aria-controls apunta a un id que no existe: {m.group(1)}")

    RAROS = {"\u202f": "U+202F espacio fino", "\u2009": "U+2009 thin space", "\u00a0": "U+00A0 nbsp"}
    formulas = re.findall(r"\\\(.*?\\\)|\$\$.*?\$\$", marcado, re.S)
    sucias = [(f[:60], RAROS[c]) for f in formulas for c in RAROS if c in f]
    if sucias:
        problemas.append(f"{len(sucias)} fórmula(s) con un espacio que KaTeX no entiende: {sucias[:2]}")
    if doc.count("<template") != doc.count("</template>"):
        problemas.append("las plantillas no abren y cierran igual")

    # Lo propio de un taller: que no se haya colado una respuesta. El JSON
    # incrustado solo puede traer estas claves; cualquier otra es una fuga.
    PERMITIDAS = {"semilla", "n_min", "opciones", "ciudad", "localidades", "variantes"}
    if set(D) != PERMITIDAS:
        problemas.append(f"el JSON publicado trae claves que no son del enunciado: "
                         f"{sorted(set(D) - PERMITIDAS)}")
    for nombre, ficha in D["localidades"].items():
        if set(ficha) != {"n", "area_km2", "lambda"}:
            problemas.append(f"la ficha de {nombre} publica algo más que n, área y lambda")
    for v in D["variantes"]:
        if set(v) != {"clave", "localidad", "nx", "r_gf", "r_kl", "radio"}:
            problemas.append(f"la variante {v.get('clave')} publica campos de más")
            break
    PROHIBIDAS = ("tu patrón está agregado", "tu patrón es aleatorio", "tu patrón es regular",
                  "tu índice sube", "tu índice baja", "queda fuera de la banda",
                  "queda dentro de la banda", "indice_qgis", "l_menos_r",
                  "pct_fuera", "bw_diggle")
    filtradas = [p for p in PROHIBIDAS if p in doc.lower()]
    if filtradas:
        problemas.append(f"el documento contiene una respuesta: {filtradas}")

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

    # Lo que el enunciado manda descargar tiene que existir.
    for href in sorted(set(re.findall(r'href="\.\./(entrega/[^"]+)"', marcado))):
        if not (RAIZ / href).is_file():
            problemas.append(f"el enunciado enlaza un archivo que no existe: {href}")

    print()
    if problemas:
        for p in problemas:
            print(f"  MAL  {p}")
        print(f"\n  {len(problemas)} problema(s).\n")
        return 1
    print("  Ensamblado limpio: instrucciones + T1..T5 + la rúbrica.\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
