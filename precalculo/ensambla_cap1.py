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
import html
import mide_duraciones_cap1
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
erg = ur["ergodicidad"]     # módulo 6 (R3 · T3.3): la media de una realización al rellenar y al ampliar
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
# R3 · T3.3: la prueba de Clark-Evans del módulo 3 (la constante del error típico
# y la corrección que se publica); las z y los p de cada patrón viven en `pc`.
cep = D["clark_evans_prueba"]
ALFA = D["inferencia"]["alfa"]   # el nivel con que la tabla del módulo 3 lee el régimen


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


def p_ce(f):
    """El valor p de la prueba de Clark-Evans de un patrón, para la tabla del módulo 3.

    Con cinco decimales un p de 10⁻⁹ se imprimiría «0.00000», que es un cero que
    no es. Entonces se escribe la cota que R publica, 10 elevado a `ce_p_exp`
    (el primer entero por encima de log10 p): ni la cifra ni el exponente se
    calculan aquí.
    """
    if round(f["ce_p"], 5) > 0:
        return n(f["ce_p"])
    return f"\\(&lt; 10^{{{f['ce_p_exp']}}}\\)"


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

# R4 · T4.2 (2026-11-23). La lista de fuentes de cada módulo que cita. La
# escribe `genera_referencias.genera()` entre los dos marcadores, con las
# obras de las <cite class="cita"> de ESE módulo, y cada cita enlaza a su
# entrada (`#ref-mN-clave`): solo el módulo abierto está en el DOM, así que
# la lista del capítulo, que vive en el módulo 12, no sirve de destino.
# Va en los módulos que citan y no en `CIERRE`: un módulo sin citas se
# quedaría con el título y la lista vacía.
FUENTES_MODULO = """
      <aside class="fuentes-modulo" style="margin-top:1.5rem; border-top:1px solid #d9e2dd; padding-top:0.75rem;">
        <h4 style="margin:0;">Fuentes citadas en este módulo</h4>
        <!--FUENTES-MODULO:inicio--><!--FUENTES-MODULO:fin-->
      </aside>
"""
CIERRE_FUENTES = FUENTES_MODULO + CIERRE


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
# R3 · T3.5 (D9, H-07): el extracto de datos y dónde se descarga
# =====================================================================
# Los bloques leían `datos/procesado/…` y `precalculo/salidas/…`, que no
# viajan al sitio, y llamaban a `carga_municipios()`: quien copiaba un bloque
# desde GitHub Pages no lo podía ejecutar. Ahora leen `entrega/datos/`, que
# escribe `genera_datos_cap1.R` (lo llama genera_cap1.R), y los tamaños y
# los conteos que se publican junto a cada enlace vienen de `D["extracto"]`.
# Cada módulo que lee datos lleva UNA nota, delante de su primer bloque, con
# los enlaces y la frase de la ruta, como el ejercicio 3. `guardas_de_t35()`
# comprueba que ningún bloque vuelva a leer lo que no viaja.
EX = D["extracto"]
CARPETA_DATOS = EX["carpeta"]
# La atribución, con la frase que el material ya usa para estos datos (el
# módulo 1 del Taller 1) y las licencias de `datos/procesado/procedencia.json`.
ATRIB_IDEAM = ("las estaciones son del <strong>IDEAM</strong> (normales climatológicas, "
               "CC BY-SA 4.0)")
ATRIB_DANE = ("del <strong>DANE</strong> (Marco Geoestadístico Nacional) por vía de "
              "geoBoundaries (CC BY 4.0)")


def tam_archivo(f):
    """El tamaño de un archivo del extracto, en KB o en MB, tal como lo midió R."""
    return f"{f['mb']}&nbsp;MB" if f["bytes"] >= 1e6 else f"{f['kb']}&nbsp;KB"


def enlace_datos(clave):
    f = EX[clave]
    return (f'<a href="../{f["ruta"]}" download target="_blank" rel="noopener">'
            f'<code>{f["archivo"]}</code></a> ({tam_archivo(f)})')


def nota_datos(texto, varios=True, cola=""):
    """La nota de descarga de un módulo: los enlaces y la frase de la ruta."""
    ruta = ("los busca en <code>{c}/</code>: esa ruta se cambia por la del lugar donde se hayan "
            "guardado." if varios else
            "lo busca en <code>{c}/</code>: esa ruta se cambia por la del lugar donde se haya "
            "guardado.").format(c=CARPETA_DATOS)
    return f"""      <p class="text-sm nota-datos" style="margin:0 0 0.5rem;">{texto} El código
        {ruta}{(' ' + cola) if cola else ''}</p>

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
        1854. <span data-afirma="c1-m1-02">La investigación de la que salió es uno de los ejemplos más conocidos
        del análisis espacial <cite class="cita" data-ref="moraga2019geospatial" data-loc="§1.1"></cite></span>. Antes del dibujo, ocho preguntas para ti.</p>

      <div class="note">
        <p><strong>Ocho preguntas, sin nota.</strong> No cuentan para nada y no hace falta que
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
        una de ellas —si un puñado de puntos sobre un plano está diciendo algo o es casualidad— es la que el
        capítulo le hace enseguida a un plano de 1854, el de un brote de cólera en Londres. Con una advertencia
        que el módulo sostiene más abajo: a quien lo dibujó, el plano no le sirvió para descubrir la causa del
        brote, sino para documentar lo que ya había averiguado.</p>

      <p><span data-afirma="c1-m1-03">Londres, verano de 1854. En el Soho, la tabla que John Snow publicó
        del brote cuenta <strong>{sn['muertes_tabla']}</strong> muertes de cólera en seis semanas, y en su
        plano no entraron las que no tenían número de casa conocido
        <cite class="cita" data-ref="snow1855mode" data-loc="p. 46; pp. 49–50"></cite></span>. El plano, tal como hoy está
        digitalizado, sitúa <strong>{sn['n_muertes']}</strong>. <span data-afirma="c1-m1-04">La explicación que Snow tenía por el mejor intento
        anterior al suyo culpaba al aire: efluvios del enfermo que otros respiraban
        <cite class="cita" data-ref="snow1855mode" data-loc="p. 113"></cite></span>. Es lo que aquí se llama el aire viciado. <span data-afirma="c1-m1-05">Snow sospecha del agua de la bomba de Broad
        Street. El examen del agua no lo saca de dudas, y lo que lo decide es preguntar, muerte por muerte, de
        qué bomba bebía cada uno: no encuentra nada más que tengan en común
        <cite class="cita" data-ref="snow1855mode" data-loc="pp. 39–40"></cite></span>. <span data-afirma="c1-m1-01">El dibujo llega después, y no como
        hallazgo sino como documento: Snow ya traía su hipótesis antes de pisar el Soho, y preparó el mapa
        cuando la bomba estaba fuera de servicio <cite class="cita" data-ref="pebesma2023spatial" data-loc="§15.1"></cite>. Con él enseña que
        la mayoría de los muertos vivía más cerca de la bomba de Broad Street que de ninguna otra
        <cite class="cita" data-ref="baddeley2015spatial" data-loc="p. 261"></cite></span>. El plano <em>dibuja los muertos</em>, casa por
        casa, y en su versión digitalizada trae encima <strong>{sn['n_bombas']}</strong> bombas públicas.</p>

      <p>Ese plano es el primer objeto de este curso, y conviene mirarlo antes de definir nada. Ponlo en
        <em>Broad Street contra el resto</em> y fíjate en dónde cae la mancha.</p>

      <div class="simulador" data-simulador="snow-mapa">
        <h4><i class="fas fa-map-location-dot" aria-hidden="true"></i> El mapa de Snow, capa a capa</h4>
        <p class="simulador-intro">Las <strong>{sn['n_segmentos']}</strong> calles del Soho de fondo, las
          {sn['n_muertes']} muertes y las {sn['n_bombas']} bombas, estas en rombo. <span data-afirma="c1-m1-11">Según
          la ayuda del paquete <cite class="cita" data-ref="friendly2009histdata"></cite>, el plano lo digitalizó en 1992 Rusty Dodson, del NCGIA, a partir del mapa que trae <em>Snow on
          Cholera</em> (Oxford University Press, 1936), y el paquete lo toma de Tobler (1994)</span>. Conmuta entre colorear por bomba más próxima y resaltar solo Broad Street. Las líneas a
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
          \\(\\{{s_1, \\dots, s_n\\}}\\) dentro de la región que se observó, la <em>ventana</em> \\(W\\), donde
          <span data-afirma="c1-m1-06"><strong>lo aleatorio es dónde están los puntos</strong>
          <cite class="cita" data-ref="moraga2019geospatial" data-loc="§2.1.3"></cite></span> — y también cuántos hay. No se ha medido nada en cada muerte: la muerte <em>es</em> el
          dato, y su valor es su posición.</p>
        <p style="margin-bottom:0;">Esa frase —«qué es aleatorio»— es la que reparte los diez capítulos del curso, y
          el módulo 2 la usa para separar los tres tipos de dato espacial.</p>
      </div>

      <p>La asignación de cada muerte a su bomba se calcula por distancia euclídea, y se contrasta con los polígonos
        de Thiessen que acompañan al dato en <code>HistData</code>. <span data-afirma="c1-m1-12">El paquete trae,
        junto a las muertes y las bombas, los vértices del polígono de Thiessen de cada bomba: el área que
        queda más cerca de ella que de cualquier otra <cite class="cita" data-ref="friendly2009histdata"></cite></span>. Coinciden en
        <strong>{sn['n_coinciden_tobler']} de {sn['n_muertes']}</strong>. Son dos construcciones distintas de la
        misma idea, y si discreparan habría que averiguar cuál está mal antes de publicar ninguna de las dos.</p>

""" + nota_datos(
    f"La pestaña de Python lee las muertes y las bombas de un archivo, {enlace_datos('snow')}, porque "
    "<code>HistData</code> es un paquete de R; la de R no necesita descargar nada.", varios=False,
    cola="Qué paquetes hay que instalar, y cómo, lo dice el recuadro «Prepara tu entorno» del "
         "módulo 8.") + tabs(
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
    """# HistData no existe en Python: el mismo dato viaja en un CSV
# (cap1_snow.csv) para que esta pestana no tenga que fingir.
import pandas as pd, numpy as np
from scipy.spatial import cKDTree

sw = pd.read_csv("entrega/datos/cap1_snow.csv")
mu = sw[sw.tipo == "muerte"][["x", "y"]].to_numpy()
bo = sw[sw.tipo == "bomba"]
i_broad = int(np.flatnonzero(bo.etiqueta.to_numpy() == "Broad St")[0])

_, mas_cerca = cKDTree(bo[["x", "y"]].to_numpy()).query(mu)
print(f"{(mas_cerca == i_broad).sum()} de {len(mu)} = "
      f"{100 * (mas_cerca == i_broad).mean():.5f} %")
#> """ + f"{sn['n_mas_cerca_broad']} de {sn['n_muertes']} = {n(sn['pct_mas_cerca_broad'])} %") + f"""
      <p>Hay una segunda mitad de la historia, y es la que suele contarse mal. <span data-afirma="c1-m1-07">El 8 de septiembre de 1854 la
        parroquia retiró el mango de la bomba de Broad Street, al día siguiente de que Snow le expusiera lo que
        había averiguado <cite class="cita" data-ref="snow1855mode" data-loc="p. 40; p. 51"></cite></span>, y el brote se apagó. La lectura cómoda es que lo apagó
        la retirada del mango. El dato no permite atribuírselo: el
        <strong>{n(sn['pct_ataques_antes_mango'])}&nbsp;%</strong> de los ataques había ocurrido <em>antes</em> de
        ese día, y desde el pico del {sn['fecha_pico']} —{sn['ataques_pico']} ataques— hasta el
        {sn['fecha_mango']} —{sn['ataques_dia_mango']}— ya habían caído un
        <strong>{n(sn['caida_hasta_mango_pct'])}&nbsp;%</strong>. <span data-afirma="c1-m1-08">Los ataques ya venían cayendo, y
        el propio Snow lo escribe: habían disminuido tanto antes de que se dejara de usar el agua que no se
        puede decidir si el pozo seguía contaminado. Anota además que la mortalidad bajó mucho por la huida de
        la población, que empezó poco después del brote: otra cosa que la curva no separa
        <cite class="cita" data-ref="snow1855mode" data-loc="pp. 51–52"></cite></span>. Tampoco permite
        decir lo contrario, que la retirada no sirviera de nada: <span data-afirma="c1-m1-09">entre beber el
        agua y enfermar pasa un tiempo, que Snow cifra, en general, entre veinticuatro y cuarenta y ocho horas
        <cite class="cita" data-ref="snow1855mode" data-loc="p. 16"></cite></span>, así
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
          que lo convierte en evidencia sobre el agua es el mecanismo que él ya sospechaba, no el mapa solo.
          <span data-afirma="c1-m1-10">Que Snow dedujera del mapa la causa del cólera es un relato inexacto: ya
          traía su hipótesis, y el mapa la documentó después
          <cite class="cita" data-ref="pebesma2023spatial" data-loc="§15.1"></cite></span>.</p>
        <p style="margin-bottom:0;">Guarda esa distinción. Vuelve en el capítulo 3 con la falacia ecológica y en el 8
          con los tres orígenes posibles de la dependencia espacial, que llevan a tres modelos distintos.</p>
      </div>
""" + CIERRE_FUENTES


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
# R3 · T3.4 (D7): el recuadro del dato de área decía que los cortes «viajan en
# el JSON: el navegador solo pinta». Es la arquitectura del material, no algo
# que el estudiante necesite: los cortes los calcula `classInt` en R
# (precalculo/geo.R), se incrustan en el HTML con su mapa, y el JavaScript no
# recalcula ninguno. La prosa conserva lo que sí le sirve: quién los calcula y
# que son una decisión, que es el módulo 1 del capítulo 3.
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
        parecidas, tres procesos distintos. <span data-afirma="c1-m2-01">El ojo es mal juez de si un patrón es
        aleatorio, y por eso hace falta algún análisis objetivo <cite class="cita" data-ref="baddeley2015spatial" data-loc="p. 4"></cite></span>. Si no separa tres
        patrones <em>del mismo tipo</em>, con más razón no va a separar los tres tipos entre sí.</p>

      <p>Vienen seis mapas, que en realidad son <strong>tres pares</strong>: cada tipo dos veces, con su caso
        canónico de la literatura y su gemelo colombiano. Míralos antes de leer lo que va debajo de cada uno, y
        hazlo con la pregunta correcta. No es «¿qué se ve?», que es la que el ojo contesta solo y contesta mal. Es
        <strong>«¿qué saldría distinto si volviéramos a tomar el dato?»</strong>.</p>

      <div class="definition">
        <h3>1 · Patrón puntual — lo aleatorio es <em>dónde</em></h3>
        <p style="margin-bottom:0;">Los {pc['japanesepines']['n']} pinos japoneses sobre su ventana unitaria
          —<span data-afirma="c1-m2-17">brinzales de pino negro japonés en un cuadrado de un bosque natural, que
          recogió Numata (1961) y que el paquete toma de un libro de Diggle
          <cite class="cita" data-ref="baddeley2017spatstatdata"></cite></span>—, y las {ent(co['puntual']['n'])} sedes educativas de Bogotá. En los dos casos no se ha medido nada en cada
          punto: el punto <em>es</em> el dato.</p>
      </div>
      <div class="geomapa" data-geomapa="cap1-pinos-ventana"></div>
      <p class="geomapa-pie" id="aleatorio-pinos" hidden style="font-size:0.9rem;color:#012820;margin:0.25rem 0 1rem 0;"><strong>Lo aleatorio es dónde.</strong> Si se volviera a tomar el dato, los pinos caerían en otros sitios y podrían ser más o menos. La ventana, no: es la región donde se contaron, y se fija antes de mirarlos. Como \\(\\hat{{\\lambda}} = n/|W|\\), cambiar de ventana cambia la intensidad estimada sin mover un pino. El rectángulo que ciñe a los puntos no es una ventana: lo dibujan los propios pinos, así que es tan aleatorio como ellos, y por construcción no deja ninguno fuera. Por eso su \\(\\hat{{\\lambda}}\\) sale siempre más alto que con la ventana del dato, que lo contiene.</p>

      <p>Los pinos son aquí el <strong>caso nulo</strong>, el canónico. Su distancia media al vecino más
        próximo —<strong>{n(pc['japanesepines']['nn_media'])}</strong> en unidades de la ventana— es
        prácticamente la que daría tirar los {pc['japanesepines']['n']} puntos al azar sobre el cuadrado, que es
        <strong>{n(pc['japanesepines']['nn_esperada'])}</strong>. Medido así, no hay nada que explicar en
        este mapa, y esa es exactamente su función: es la referencia contra la que se mide todo lo demás.
        <span data-afirma="c1-m2-02">Lo nulo es este patrón medido con esa distancia, no el bosque: en un conjunto
        mayor de pinos negros japoneses, un análisis detallado encontró que la densidad cambia de un sitio a otro
        y que los árboles tienden a no crecer juntos, señal de competencia entre vecinos
        <cite class="cita" data-ref="baddeley2015spatial" data-loc="p. 4"></cite></span>. Fíjate,
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
          media de la región que encierra, y la nota que cierra este módulo lo mide. El cambio se puede provocar en el
          mapa de los pinos: con el rectángulo que ciñe a los puntos, el área pasa de {pc['japanesepines']['area']} a
          {n(pc['japanesepines']['area_caja'], 3)} y \\(\\hat{{\\lambda}}\\), de {pc['japanesepines']['lambda']} a
          {n(pc['japanesepines']['lambda_caja'])}, sin que se mueva un pino. Pero ese rectángulo no es otra ventana:
          no se fijó antes de mirar, lo dibujan los propios pinos, que por construcción quedan todos dentro, y por eso
          infla \\(\\hat{{\\lambda}}\\). Con los pinos no hay nada que elegir, porque la ventana viene con el dato.
          Con el mapa que sigue, sí.</p>
      </div>

      <div class="geomapa" data-geomapa="cap1-bogota"></div>
      <p class="geomapa-pie" id="aleatorio-bogota" hidden style="font-size:0.9rem;color:#012820;margin:0.25rem 0 1rem 0;"><strong>Lo aleatorio es dónde.</strong> Si se volviera a tomar el dato, los puntos caerían en otros sitios y podrían ser más o menos. La ventana, no: es una región donde el dato es exhaustivo, y se fija antes de mirar. Como \\(\\hat{{\\lambda}} = n/|W|\\), el perímetro urbano y el Distrito dan dos intensidades distintas sin mover una sede. El rectángulo que ciñe a las sedes no vale como ventana por dos razones: lo dibujan los propios puntos, y se sale del Distrito, así que su área cuenta suelo donde nadie buscó sedes.</p>

      <p>Bogotá hace lo contrario, y por eso va al lado. Las <strong>{ent(co['puntual']['n'])}</strong> sedes no
        están tiradas al azar: dibujan las calles, y con ellas la densidad de la ciudad. Aquí sí hay algo que
        explicar. Y conviene mirar el borde, que es donde este mapa se pone interesante:
        <strong>{ent(co['puntual']['n_urbana'])}</strong> de las {ent(co['puntual']['n'])} caen dentro del
        perímetro urbano y <strong>{ent(co['puntual']['n_dc'])}</strong> dentro del Distrito Capital. El mismo
        patrón admite al menos tres bordes distintos, y elegir no es cuestión de gusto: <span data-afirma="c1-m2-03">la <em>ventana</em> de un
        patrón puntual se toma como una región sobre la que el dato es <strong>exhaustivo</strong> —aquella
        donde se puede afirmar que no falta ningún punto— <cite class="cita" data-ref="pebesma2023spatial" data-loc="§10.2"></cite></span>. Con ese criterio valen las dos que se acaban de
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
          los dos mapas los calcula <code>classInt</code> en R, y son una decisión: el capítulo 3 empieza por
          cuántos mapas distintos admite un mismo dato según cómo se corte.</p>
      </div>
      <div class="geomapa" data-geomapa="cap1-nc"></div>
      <p class="geomapa-pie" id="aleatorio-nc" hidden style="font-size:0.9rem;color:#012820;margin:0.25rem 0 1rem 0;"><strong>Lo aleatorio es el valor de cada unidad.</strong> Si se volviera a tomar el dato, cambiarían los valores y, con ellos, los colores. Los límites no: las unidades estaban ahí antes del dato y seguirán después.</p>

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
        ensancha hasta invertir conclusiones: <span data-afirma="c1-m2-04">es la <strong>falacia ecológica</strong>,
        en la que una asociación medida entre agregados lleva a conclusiones distintas de las que daría la misma
        medida entre individuos <cite class="cita" data-ref="moraga2019geospatial" data-loc="§5.5"></cite></span>. Con el MAUP forma el capítulo 3 entero.</p>

      <div class="geomapa" data-geomapa="cap1-desercion"></div>
      <p class="geomapa-pie" id="aleatorio-desercion" hidden style="font-size:0.9rem;color:#012820;margin:0.25rem 0 1rem 0;"><strong>Lo aleatorio es el valor de cada unidad.</strong> Si se volviera a tomar el dato, cambiarían los valores y, con ellos, los colores. Los límites no: las unidades estaban ahí antes del dato y seguirán después.</p>

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
      <p class="geomapa-pie" id="aleatorio-meuse" hidden style="font-size:0.9rem;color:#012820;margin:0.25rem 0 1rem 0;"><strong>Lo aleatorio es el campo entero.</strong> Si se volviera a tomar el dato, cambiarían los valores: en los puntos medidos y en todos los demás, donde también hay un valor que nadie midió. Los sitios donde se mide se toman como fijos.</p>

      <p>El mapa del Mosa parece manchas de color hasta que uno sabe por dónde va el río. Las dos líneas del
        mapa son sus orillas. El zinc va de
        <strong>{gc['zinc_min']}</strong> a <strong>{ent(gc['zinc_max'])}</strong> ppm, con media
        <strong>{n(gc['zinc_media'])}</strong> y desviación <strong>{n(gc['zinc_sd'])}</strong>, y con una
        asimetría de <strong>{n(gc['asimetria_zinc'])}</strong> que es la razón de que el capítulo 9 trabaje
        este dato con el logaritmo. <span data-afirma="c1-m2-18">Las muestras se tomaron en una llanura de
        inundación del Mosa, cerca del pueblo de Stein, en los Países Bajos, y el dato trae para cada punto
        una clase de frecuencia de inundación <cite class="cita" data-ref="pebesma2005sp"></cite></span>. El patrón
        tampoco es un capricho: la correlación del zinc
        con la distancia al río vale <strong>{n(gc['corr_dist_rio'])}</strong>. Cuanto más cerca del río, más
        zinc: es lo que se vería si el metal lo dejaran las crecidas sobre la vega, y la correlación, sola, no
        llega a probarlo.</p>

      <div class="geomapa" data-geomapa="cap1-ideam"></div>
      <p class="geomapa-pie" id="aleatorio-ideam" hidden style="font-size:0.9rem;color:#012820;margin:0.25rem 0 1rem 0;"><strong>Lo aleatorio es el campo entero.</strong> Si se volviera a tomar el dato, cambiarían los valores: en los puntos medidos y en todos los demás, donde también hay un valor que nadie midió. Los sitios donde se mide se toman como fijos.</p>

      <p>Las <strong>{co['geo']['n']}</strong> estaciones del IDEAM hacen lo mismo con otra variable. La
        temperatura media anual va de <strong>{n(co['geo']['t_min'], 1)}</strong> a
        <strong>{n(co['geo']['t_max'], 1)}</strong> °C, un rango que sorprende en un país ecuatorial hasta que se
        mira la otra columna del dato: hay estaciones a <strong>{ent(co['geo']['alt_max'])}</strong> m. Estás
        viendo la cordillera, no el clima. El módulo 3 mide cuánto de lo que parece «lo cercano se parece» es en
        realidad «lo cercano está a la misma altura», y la cifra incomoda.</p>

      <p>Lo que comparten: entre dos estaciones <em>hay</em> temperatura, y entre dos puntos de la vega <em>hay</em>
        zinc. Simplemente no se midieron. <span data-afirma="c1-m2-05">En el marco de este curso —el <em>basado en el modelo</em>, que el
        módulo 10 separa del basado en el diseño— lo aleatorio es el propio campo \\(Z(\\cdot)\\), del que el dato es
        una realización, y en el caso geoestadístico el dominio \\(D\\) es fijo
        <cite class="cita" data-ref="cressie1993statistics" data-loc="p. 8"></cite></span>. El mapa entero de temperaturas es una realización
        de un proceso, y las \\(n\\) localizaciones donde se mide se toman también como fijas. Si se volviera a tomar el dato, lo que saldría distinto serían <strong>los valores</strong>, en esos
        puntos y en todos los demás. Que haya un valor en todo punto, y no solo donde se midió, es lo que da
        permiso para predecir, y es justo lo que los otros dos tipos no tienen. La otra lectura —el campo quieto
        y lo aleatorio, dónde se mide— es la del muestreo, y se deja para el módulo 10.</p>

      <p>Vuelve ahora al párrafo del principio. Los seis mapas se parecen bastante entre sí —puntos y polígonos de
        colores— y sin embargo la pregunta «¿qué saldría distinto si volviéramos a tomar el dato?» los ha partido
        limpiamente en tres: cambian las <em>posiciones</em>, cambian los <em>valores</em> sobre unidades fijas, o
        cambian los valores de un <em>campo</em> que existe en todo punto y se observa en unos pocos. La tabla
        resume lo que acabas de hacer. <span data-afirma="c1-m2-06">Su segunda fila reparte los métodos por tipo de
        dato, como hacen <cite class="cita" data-ref="pebesma2023spatial" data-loc="§10.2" data-modo="narrativa"></cite>: unos para los puntos en su ventana, otros para las
        áreas que cubren el territorio y otros para lo que se mide en puntos de un campo continuo.</span></p>

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
        aleatorio?» sino <strong>«¿de qué trozo de la unidad habla el número?»</strong>. <span data-afirma="c1-m2-07"><cite class="cita" data-ref="pebesma2023spatial" data-loc="§1.6; cap. 5" data-modo="narrativa"></cite> la
        introducen ya en el capítulo 1 de su libro y la desarrollan en el 5: la llaman el <em>soporte</em> del
        dato.</span></p>

      <div class="definition">
        <h3>El soporte: a qué parte de la geometría se refiere el valor</h3>
        <ul>
          <li><span data-afirma="c1-m2-08"><strong>Soporte puntual:</strong> el valor vale en <em>cada punto</em> de la geometría
            <cite class="cita" data-ref="pebesma2023spatial" data-loc="§1.6"></cite></span>. El tipo de
            suelo de un polígono de un mapa de suelos es el mismo en el centro que en el borde, y lo sigue siendo
            en cualquier trozo que recortes.</li>
          <li><span data-afirma="c1-m2-16"><strong>Soporte de bloque:</strong> el valor <em>resume</em> la geometría entera
            <cite class="cita" data-ref="pebesma2023spatial" data-loc="§1.6"></cite></span>. La tasa de SIDS de
            un condado no está en ningún punto del condado: está en el condado, y no sobrevive a que lo partas.</li>
        </ul>
        <p style="margin-bottom:0;">Y aquí está lo que hay que destapar, porque es lo que rompe la lectura fácil de
          la tabla de arriba: <span data-afirma="c1-m2-09"><strong>el soporte no lo decide la geometría</strong>:
          entre los tipos de geometría y los tipos de fenómeno no hay correspondencia simple
          <cite class="cita" data-ref="pebesma2023spatial" data-loc="§5.1"></cite></span>. Un mapa de suelos y el de
          Carolina del Norte se guardan igual —polígonos— y uno tiene soporte puntual y el otro de bloque.
          «Polígono» no significa «dato de área», y el Mosa lo enseña por el otro lado: se dibuja con puntos y no es
          un patrón puntual.</p>
      </div>

      <p>El soporte no es vocabulario: se paga en el mapa, y se puede medir. La variable que Carolina del Norte trae
        de fábrica no es la tasa sino el <strong>conteo</strong> de muertes por condado
        —{ac['sid74_total']} en total—, que es <em>extensiva</em>: crece con la unidad.
        <span data-afirma="c1-m2-10">Pintarla tal cual sería pintar, sobre todo, cuántos niños nacieron en cada
        condado: es el riesgo de llevar una variable extensiva a un mapa de coropletas, que lo que se acabe
        viendo sea el tamaño de las unidades <cite class="cita" data-ref="pebesma2023spatial" data-loc="§10.2"></cite></span>. La correlación entre el
        conteo y los nacimientos vale <strong>{n(sop['cor_conteo_nacimientos'])}</strong>; dividir por los
        nacimientos —volverla <em>intensiva</em>— la deja en
        <strong>{n(sop['cor_tasa_nacimientos'])}</strong>. Por eso el mapa que has mirado es una tasa y no un
        conteo, y no era una decisión de estilo.</p>

      <p>Hay un segundo paso, y es donde la receta de manual se queda corta. «Divide por el área» es lo que suele
        decirse para pasar de extensiva a intensiva, y en este dato <em>no</em> es lo correcto: el conteo sigue al
        área bastante menos —<strong>{n(sop['cor_conteo_area'])}</strong>— que a los nacimientos.
        <span data-afirma="c1-m2-11">En un dato de salud el denominador es la población de cada unidad, no su
        superficie: los conteos se pasan a tasas dividiendo por ella
        <cite class="cita" data-ref="pebesma2023spatial" data-loc="§10.2"></cite></span>. Aquí esa población, la que está en riesgo,
        son los nacimientos. Y no es un denominador disimuladamente
        constante: entre el condado que más nacimientos aporta y el que menos hay un factor de
        <strong>{n(sop['razon_nacimientos'])}</strong>. Eso mueve el soporte de sitio: la tasa de un condado ya no
        resume un territorio sino una población, y ahí queda un cabo suelto que conviene ver desde ahora. Dos
        condados separados por ese factor no conocen su tasa con la misma precisión. Si las muertes de un condado
        son un conteo de Poisson, de media igual a su tasa por sus nacimientos, la varianza de la tasa estimada es
        la tasa dividida entre los nacimientos: a menos nacimientos, más varianza. El pequeño la tiene mucho peor
        estimada, y sin embargo el mapa los pinta con el mismo derecho. Pintar bien no es lo mismo que saber.</p>

      <p>Conviene separar los dos filos, porque es fácil confundirlos. El módulo 7 mide qué pasa cuando se
        <em>cambia de unidades</em> —el mismo fenómeno sobre municipios o sobre departamentos—; el soporte es qué
        significa el número <em>dentro</em> de una unidad. Se pueden romper por separado, y casi siempre se rompen
        juntos.</p>

      <div class="definition">
        <h3>La formalización, ahora que ya has visto los seis mapas</h3>
        <p data-afirma="c1-m2-12">En los tres casos hay un dominio \\(D \\subset \\mathbb{{R}}^2\\) y algo aleatorio sobre él. Lo que
          cambia es <strong>qué es aleatorio</strong>, y los tres son casos de un mismo modelo
          <cite class="cita" data-ref="cressie1993statistics" data-loc="pp. 8–9"></cite>:</p>
        <ul>
          <li><strong>Patrón puntual:</strong> no hay ningún valor \\(Z(s)\\) que observar. Lo aleatorio es el
            propio conjunto de puntos \\(\\{{s_1, \\dots, s_N\\}}\\) que caen en la región observada, la
            <em>ventana</em> \\(W \\subset D\\), que se fija antes de mirar. Cuántos caen también es aleatorio:
            \\(N\\), en mayúscula, es ese número como variable aleatoria, y \\(n\\) el que se observó. Dicho de
            otro modo, lo aleatorio es el conteo \\(N(B)\\), el número de puntos que caen en cada región
            \\(B\\) de la ventana.</li>
          <li><strong>Dato de área:</strong> los índices son un conjunto <em>fijo y numerable</em> de unidades
            \\(A_1, \\dots, A_n\\) —los municipios—, y aleatorio es el valor \\(Z(A_i)\\) de cada una.</li>
          <li><strong>Geoestadístico:</strong> hay un valor \\(Z(s)\\) para <em>todo</em> \\(s \\in D\\) —una
            temperatura en cada punto de Colombia—. Aleatorio es ese campo entero, y solo se observa en \\(n\\)
            localizaciones, que se toman como fijas.</li>
        </ul>
        <p style="margin-bottom:0;">De ahí sale una consecuencia que conviene tener presente desde ya: en el caso
          geoestadístico <strong>tiene sentido predecir en un punto donde no se ha medido</strong>, y en el de área no. Preguntar
          «¿cuánta deserción hay en un punto entre dos municipios?» no significa nada — y ahora se puede decir <em>por qué</em>,
          que es mejor que decirlo por decreto: la deserción de un municipio tiene <strong>soporte de bloque</strong>,
          así que no hay ninguna función definida sobre los puntos que se pueda interpolar. \\(Z(A_i)\\) no es
          \\(Z(s)\\) evaluada en ningún \\(s\\); es otra cosa que se escribe parecido.
          <span data-afirma="c1-m2-13">Lo que un dato de bloque sí admite es pasar a <em>otras áreas</em> —la
          interpolación areal, un cambio de soporte—, y eso obliga a suponer cómo se reparte el valor dentro de
          cada unidad: de manera uniforme si la variable es extensiva, constante si es intensiva
          <cite class="cita" data-ref="pebesma2023spatial" data-loc="§5.4"></cite></span>.</p>
      </div>

      <div class="warning">
        <p style="margin-bottom:0;"><strong>El mismo fenómeno puede ser de los tres tipos, y eso no es una
          ambigüedad: es una decisión.</strong> Los colegios de Bogotá son un patrón puntual si la pregunta es
          «¿dónde se concentran?»; son dato de área si se cuentan por localidad; y serían geoestadísticos si lo que
          se midiera fuera algo que existe en todo punto —la accesibilidad, por ejemplo—. Elegir el tipo es elegir
          el modelo, y el capítulo 3 enseña lo caro que sale elegirlo en silencio.</p>
      </div>

      <p>Falta rematarlo por el lado que más caro sale en la práctica, que no es confundir los tres tipos entre sí:
        es <strong>leer el tipo en la geometría del archivo</strong>. <span data-afirma="c1-m2-14"><cite class="cita" data-ref="pebesma2023spatial" data-loc="§5.1" data-modo="narrativa"></cite> separan el <em>fenómeno</em>
        —lo que hay en el mundo: un campo, un objeto o un agregado— de la <em>geometría</em> con la que se guarda, y
        avisan de que entre los dos no hay correspondencia simple.</span> La tabla lo enseña de la única forma convincente:
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

""" + nota_datos(
    "La pestaña de Python lee tres archivos, porque los tres datos vienen en paquetes de R: "
    f"{enlace_datos('pinos')}, los {EX['pinos']['filas']} pinos de <code>spatstat.data</code>; "
    f"{enlace_datos('nc')}, los {EX['nc']['filas']} condados de Carolina del Norte que trae <code>sf</code> "
    "(el módulo 9 abre este archivo por dentro); y "
    f"{enlace_datos('meuse')}, el zinc de <code>sp</code> con sus coordenadas. La pestaña de R los toma "
    "de los paquetes.") + tabs(
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
    """import geopandas as gpd, pandas as pd, numpy as np

# 1) spatstat.data no existe en Python: el dato va por CSV, y la
#    ventana, que en R viaja dentro del objeto, aqui se escribe aparte
#    (el cuadrado unidad).
jp = pd.read_csv("entrega/datos/cap1_japanesepines.csv")
print(f"n = {len(jp)}, area de la ventana = {1.0:.5f}, "
      f"lambda = {len(jp) / 1.0:.5f}")
#> """ + f"n = {pc['japanesepines']['n']}, area de la ventana = {n(pc['japanesepines']['area'])}, "
    f"lambda = {n(pc['japanesepines']['lambda'])}" + """

# 2) Dato de area: GeoDataFrame, el equivalente de un objeto sf.
nc = gpd.read_file("entrega/datos/cap1_nc.gpkg")
print(f"{len(nc)} unidades, tasa media de SIDS = "
      f"{(1000 * nc.SID74 / nc.BIR74).mean():.5f} por mil")
#> """ + f"{ac['n']} unidades, tasa media de SIDS = {n(ac['tasa_media'])} por mil" + """

# 3) Geoestadistico.
me = pd.read_csv("entrega/datos/cap1_meuse.csv")
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
          <span data-afirma="c1-m2-15">cada cociente \\(n/|W|\\) estima la intensidad <em>media</em> de su propia región,
          \\(\\frac{{1}}{{|W|}}\\int_W \\lambda(s)\\,ds\\), donde \\(\\lambda(s)\\) es la intensidad en cada
          sitio: el número esperado de puntos de una región es la integral de \\(\\lambda(s)\\) sobre ella
          <cite class="cita" data-ref="baddeley2015spatial" data-loc="p. 162; p. 164"></cite></span>. El factor no mide un error: mide cuánto cambia la intensidad de un sitio a otro —la
          <em>inhomogeneidad</em> del patrón—, porque el Distrito añade al perímetro un territorio extenso y casi
          sin sedes. Elegir ventana es elegir qué región se describe. El capítulo 4 empieza justo ahí.</p>
      </div>
""" + CIERRE_FUENTES


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
# R3 · T3.4 (H-03, D8): el módulo hace dos preguntas y ahora lo dice al
# entrar y en su objetivo. El puente a Clark-Evans decía «La primera ley no
# vale solo para valores medidos: también describe dónde están las cosas», y
# eso mezcla la autocorrelación de un atributo con la disposición de unos
# puntos. Un patrón agregado no prueba dependencia entre puntos: una
# intensidad inhomogénea los junta con los puntos independientes. El puente
# nuevo dice que cambia la pregunta y por qué no es la misma ley.
MOD3 = cabecera(
    3, "La primera ley de Tobler", "Tobler's first law",
    "Medir la primera ley en vez de citarla, con un control que la niega y "
    "un caso donde lo que parece dependencia es otra cosa. Y, en un patrón "
    "puntual, medir con el índice de Clark-Evans si los puntos están más juntos "
    "o más separados de lo que los dejaría el azar.") + f"""
      <p>El módulo 2 separó los datos espaciales por lo que tienen de aleatorio y por el trozo de espacio del que
        habla cada número. Este módulo hace dos preguntas que salen de ahí. La primera es de los datos que traen un
        valor medido en cada sitio: si los valores cercanos se parecen más que los lejanos. La segunda, en la
        segunda mitad, es de los patrones puntuales, donde no hay valor que comparar: si los puntos están más
        juntos o más separados de lo que los dejaría el azar.</p>

      <p><span data-afirma="c1-m3-01">La cita es de 1970: <em>«todo está
        relacionado con todo lo demás, pero las cosas cercanas están más relacionadas que las lejanas»</em>
        <cite class="cita" data-ref="tobler1970computer" data-via="pebesma2023spatial" data-loc="§15.1"></cite></span>. Dicha así no es una ley: es una impresión.
        Lo que la convierte en algo utilizable es que se puede <strong>medir</strong>, y aquí se mide con un
        <em>correlograma</em>: la I de Moran calculada por bandas de distancia. <span data-afirma="c1-m3-03">El
        mismo nombre designa otra cosa en geoestadística, y es la cantidad que usan los analistas de series de
        tiempo: la función de autocorrelación de un proceso estacionario, la covarianza a cada separación
        dividida entre la varianza
        <cite class="cita" data-ref="cressie1993statistics" data-loc="p. 67"></cite></span>. El de este módulo hace el mismo papel con otro estadístico, y no es el mismo
        objeto.</p>

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
        <p data-afirma="c1-m3-04">Con \\(n\\) unidades, valores \\(z_i\\) centrados y la matriz de pesos \\(\\mathbf{{W}}\\), de
          elementos \\(w_{{ij}}\\), que declara quién es vecino de quién, el índice es el cociente que sigue
          <cite class="cita" data-ref="pebesma2023spatial" data-loc="§15.1"></cite>:</p>
        <p style="text-align:center;">$$I = \\frac{{n}}{{S_0}} \\cdot
          \\frac{{\\sum_i \\sum_j w_{{ij}} z_i z_j}}{{\\sum_i z_i^2}},
          \\qquad S_0 = \\sum_i \\sum_j w_{{ij}}, \\qquad E[I] = -\\frac{{1}}{{n-1}}$$</p>
        <p>Con las {co['geo']['n']} estaciones, \\(E[I] = {n(tb['ideam']['esperado'], 6)}\\). Es el valor
          esperado bajo la hipótesis nula de <strong>permutación</strong>: los mismos valores, repartidos al azar
          entre las mismas posiciones. Lo que queda un poco por debajo de cero bajo esa nula es
          <strong>\\(E[I]\\)</strong>, no \\(I\\), que en cada reparto sale distinta. Y queda por debajo por el
          <strong>centrado</strong>: los \\(z_i\\) suman cero, así que los productos \\(z_i z_j\\) entre unidades
          distintas suman \\(-\\sum_i z_i^2\\), y su promedio es negativo con cualquier dato. La cuenta entera
          está en el desarrollo de abajo.</p>
        <div class="derivacion">
          <button type="button" class="derivacion-boton" aria-expanded="false" aria-controls="der-esperanza-moran">
            <i class="fas fa-square-root-variable" aria-hidden="true"></i>
            <span class="derivacion-texto">Ver por qué \\(E[I] = -1/(n-1)\\) con cualquier \\(\\mathbf{{W}}\\)</span>
            <i class="fas fa-chevron-down" aria-hidden="true"></i>
          </button>
          <div class="derivacion-panel" id="der-esperanza-moran" hidden>
            <ol class="derivacion-pasos">
              <li>
                <p>Bajo la nula de permutación los valores no cambian: se reparten. Un reparto es una
                  permutación \\(\\pi\\) de las \\(n\\) unidades, todas igual de probables, y la unidad \\(i\\)
                  recibe el valor \\(z_{{\\pi(i)}}\\). El denominador suma los mismos cuadrados en cualquier
                  orden, así que no se mueve: lo aleatorio es solo el numerador. Y en el numerador solo hay
                  pares de unidades distintas, porque \\(w_{{ii}} = 0\\): nadie es vecino de sí mismo.</p>
                $$I_\\pi = \\frac{{n}}{{S_0}} \\cdot
                  \\frac{{\\sum_{{i \\neq j}} w_{{ij}}\\, z_{{\\pi(i)}} z_{{\\pi(j)}}}}{{\\sum_k z_k^2}}$$
              </li>
              <li>
                <p>Para dos unidades distintas \\(i \\neq j\\), el par \\((\\pi(i), \\pi(j))\\) es un par
                  ordenado de índices distintos elegido al azar entre los \\(n(n-1)\\) posibles. La esperanza
                  del producto es su promedio sobre todos ellos, y no depende de qué dos unidades sean:</p>
                $$E\\bigl[z_{{\\pi(i)}} z_{{\\pi(j)}}\\bigr] = \\frac{{1}}{{n(n-1)}} \\sum_{{k \\neq l}} z_k z_l$$
              </li>
              <li>
                <p>Aquí entra el <strong>centrado</strong>. Los \\(z_k\\) suman cero, así que el cuadrado de su
                  suma también es cero, y al desarrollarlo los productos entre índices distintos quedan iguales a
                  la suma de cuadrados cambiada de signo:</p>
                $$\\sum_{{k \\neq l}} z_k z_l = \\Bigl(\\sum_k z_k\\Bigr)^2 - \\sum_k z_k^2 = -\\sum_k z_k^2$$
                $$E\\bigl[z_{{\\pi(i)}} z_{{\\pi(j)}}\\bigr] = -\\frac{{\\sum_k z_k^2}}{{n(n-1)}}$$
              </li>
              <li>
                <p>Queda sumar. Todos los términos del numerador tienen esa misma esperanza, y la suma de sus
                  pesos es \\(S_0\\) entero, porque fuera de la diagonal está todo:</p>
                $$E\\Bigl[\\sum_{{i \\neq j}} w_{{ij}}\\, z_{{\\pi(i)}} z_{{\\pi(j)}}\\Bigr] =
                  -S_0\\, \\frac{{\\sum_k z_k^2}}{{n(n-1)}}$$
                <p>Al dividir entre \\(\\sum_k z_k^2\\) la suma de cuadrados se cancela; al multiplicar por
                  \\(n/S_0\\) se cancela \\(S_0\\), y no queda nada ni de \\(\\mathbf{{W}}\\) ni del dato:</p>
                $$E[I] = \\frac{{n}}{{S_0}} \\cdot S_0 \\cdot \\frac{{-1}}{{n(n-1)}} = -\\frac{{1}}{{n-1}}$$
              </li>
            </ol>
            <p class="derivacion-resultado">Con las {co['geo']['n']} estaciones,
              \\(E[I] = {n(tb['ideam']['esperado'], 6)}\\). Hacen falta las dos piezas, y se ve dónde entra cada
              una. Sin el centrado, el paso 3 dejaría \\((\\sum_k z_k)^2 - \\sum_k z_k^2\\) y la esperanza
              dependería del dato. Con diagonal, cada \\(w_{{ii}}\\) sumaría un término
              \\(w_{{ii}}\\, z_{{\\pi(i)}}^2\\) de esperanza positiva, \\(w_{{ii}} \\sum_k z_k^2 / n\\), y el paso 4
              ya no daría \\(-1/(n-1)\\). Cuando todos los pares son vecinos y pesan lo mismo, el paso 2 sobra:
              \\(I\\) vale \\(-1/(n-1)\\) en cada reparto, no solo en promedio, y el módulo 5 vuelve sobre ese
              caso. Y si el factor de delante cuenta \\(n'\\) unidades en vez de \\(n\\), la misma cuenta da
              \\(-n'/(n(n-1))\\), que es lo que dice el último párrafo de este recuadro.</p>
          </div>
        </div>
        <p><strong>La I de Moran no es una correlación.</strong> Se lee como una correlación entre cada valor y
          los de sus vecinos, pero no lo es: su rango no es \\([-1, 1]\\), y su referencia bajo la nula es
          \\(E[I]\\), no 0. El módulo 2 del capítulo 7 explica de dónde salen sus extremos.</p>
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
          <strong>{n(co['geo']['gradiente'])}</strong> °C por cada 1 000 m—. Al quitarla, la I de la primera banda baja de {n(tb['ideam']['bandas'][0]['I'])} a
          <strong>{n(tb['residuos_altitud']['bandas'][0]['I'])}</strong>: un
          <strong>{n(tb['caida_por_altitud_pct'])}&nbsp;%</strong> menos.</p>
        <p style="margin-bottom:0;">Queda dependencia —{n(tb['residuos_altitud']['bandas'][0]['I'])} sigue siendo
          mucho—, pero casi un tercio de lo que parecía «lo cercano se parece» era «lo cercano está a la misma
          altura». <span data-afirma="c1-m3-05">No es una rareza de este dato: una variable que se deja fuera del
          modelo y que varía en el espacio se suma a la dependencia espacial que se mide
          <cite class="cita" data-ref="cressie1993statistics" data-loc="p. 25"></cite></span>. <span data-afirma="c1-m3-06">El capítulo 9 le pone remedio metiendo la
          covariable en la media del modelo, como una tendencia lineal; al predecir así, <code>krige()</code>
          avisa en su salida de que usa <em>kriging universal</em>
          <cite class="cita" data-ref="pebesma2023spatial" data-loc="§12.7"></cite></span>.</p>
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

""" + nota_datos(
    f"Los dos bloques leen las {EX['estaciones']['filas']} estaciones del archivo del Taller&nbsp;1, "
    f"{enlace_datos('estaciones')}. Son datos de terceros que se redistribuyen con atribución: "
    f"{ATRIB_IDEAM}.", varios=False) + tabs(
    "El correlograma por bandas, en R y en Python",
    """library(sf); library(spdep)

est &lt;- st_read("entrega/datos/taller1_estaciones.gpkg", quiet = TRUE)

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
est = gpd.read_file("entrega/datos/taller1_estaciones.gpkg")
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

      <p>Aquí el módulo cambia de pregunta. Hasta ahora había un valor medido en cada estación, y se preguntaba si
        los valores cercanos se parecen. En un patrón puntual no hay valor: el dato es la posición, y lo que se
        pregunta es cómo están <strong>dispuestos los puntos</strong> —más juntos, más separados o como los dejaría
        el azar—. No es la primera ley con otros datos. Un patrón agregado no dice por sí solo que los puntos
        dependan unos de otros: una intensidad que cambia de un sitio a otro también los junta, aunque cada punto
        se coloque sin mirar a los demás.</p>

      <p>Abajo están los tres patrones que anunció el módulo 2, uno al lado del otro y sobre ventanas del mismo
        tamaño. Los rótulos ya dicen cuál es cuál —no hay adivinanza—; lo que no dice ninguno es <em>cuánto</em>,
        ni con qué se compara para decidirlo.</p>

      <div class="grid md:grid-cols-3 gap-4 items-start">
        <div class="geomapa" data-geomapa="cap1-secuoyas"></div>
        <div class="geomapa" data-geomapa="cap1-pinos"></div>
        <div class="geomapa" data-geomapa="cap1-celulas"></div>
      </div>

      <p>Detente en el del medio, que es el que enseña algo sobre quien mira. Ese es el patrón compatible con el
        azar, y tiene huecos y tiene grumos —el azar los produce—; puestos a ordenar los tres a ojo, es fácil
        ponerlo del lado de la agregación. Un patrón aleatorio no se ve repartido, porque
        repartido es justo lo que <em>no</em> es: se ve con grumos y con huecos. Por
        eso la pregunta «¿está agrupado?» no se contesta mirando. <span data-afirma="c1-m3-07">De la pregunta
        contraria, si unos puntos están más separados de lo que los dejaría el azar, se ha escrito que el ojo
        la juzga mal y que hace falta un análisis objetivo
        <cite class="cita" data-ref="baddeley2015spatial" data-loc="pp. 3–4"></cite></span>. Con esta pasa lo mismo: hace falta un número.</p>

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

      <p>Ese denominador no es un convenio ni una constante tabulada: sale de la definición de CSR paso a paso,
        y los dos últimos pasos dan además su <strong>error típico</strong>, que es lo que la tabla necesita para
        decir si una \\(R\\) se aparta del 1 más de lo que daría el azar. Vale la pena recorrerlos porque por el
        camino aparecen dos cosas que el curso usa después —la función \\(G\\) del capítulo 4, que asoma sola en
        el paso 4, y el punto exacto por donde se cuela la ventana infinita del efecto de borde—.</p>

      <div class="derivacion">
        <button type="button" class="derivacion-boton" aria-expanded="false" aria-controls="der-vecino-csr">
          <i class="fas fa-square-root-variable" aria-hidden="true"></i>
          <span class="derivacion-texto">Ver de dónde sale \\(E[\\bar{{d}}_{{\\min}}] = 1/(2\\sqrt{{\\lambda}})\\), y su error típico</span>
          <i class="fas fa-chevron-down" aria-hidden="true"></i>
        </button>
        <div class="derivacion-panel" id="der-vecino-csr" hidden>
          <ol class="derivacion-pasos">
            <li>
              <p>Se parte de lo único que afirma CSR, que es una regla sobre <strong>conteos</strong> y no sobre
                distancias: el número de puntos \\(N(B)\\) que caen en una región \\(B\\) de área \\(|B|\\) es
                Poisson de media \\(\\lambda|B|\\), y regiones disjuntas no se enteran unas de otras. No se añade
                nada más hasta el paso 8; el 9 añade una aproximación, y lo dice.</p>
              $$N(B) \\sim \\text{{Poisson}}(\\lambda\\,|B|)$$
            </li>
            <li>
              <p>El recuadro de arriba definió CSR de otra manera: puntos independientes y uniformes sobre la
                ventana. Son la misma definición vista desde dos lados, y se comprueba condicionando al total. Si
                la ventana se parte en regiones disjuntas \\(B_1, \\dots, B_k\\) y se sabe que dentro cayeron
                \\(N(W) = n\\) puntos, el cociente entre el producto de las \\(k\\) Poisson y la Poisson del total
                es una multinomial:</p>
              $$P\\bigl(N(B_1) = n_1, \\dots, N(B_k) = n_k \\mid N(W) = n\\bigr)$$
              $$= \\frac{{n!}}{{n_1! \\cdots n_k!}} \\prod_{{j=1}}^{{k}} \\left(\\frac{{|B_j|}}{{|W|}}\\right)^{{n_j}}$$
              <p>Es exactamente lo que dan \\(n\\) puntos tirados uno a uno, independientes, cada uno con
                probabilidad \\(|B_j|/|W|\\) de caer en \\(B_j\\): dado el número de puntos, un proceso de
                Poisson homogéneo es eso, \\(n\\) puntos <strong>i.i.d. uniformes</strong> en la ventana. La
                definición de los conteos deja \\(n\\) al azar; la de los puntos lo fija.</p>
            </li>
            <li>
              <p>La distancia \\(d_i\\) del punto \\(i\\) a su vecino más próximo —la letra del capítulo 4;
                \\(\\bar{{d}}_{{\\min}}\\) es la media de las \\(n\\)— no es un conteo, pero su <em>cola</em> sí
                lo es, y ese es el truco entero: que el vecino esté a más de \\(r\\) es exactamente que el disco
                \\(B_r\\) de radio \\(r\\) centrado en el punto esté <strong>vacío</strong>. El disco tiene área
                \\(|B_r| = \\pi r^2\\), así que basta pedirle a la Poisson de media \\(\\lambda\\pi r^2\\) la
                probabilidad de que no salga nadie:</p>
              $$P(d_i > r) = P\\bigl(N(B_r) = 0\\bigr) = e^{{-\\lambda \\pi r^2}}$$
              <p>Hay un detalle que la cuenta pasa deprisa. El disco no está centrado en un sitio cualquiera, sino
                en un punto <em>del propio patrón</em>, y lo que se usa es que los demás puntos siguen siendo
                Poisson de intensidad \\(\\lambda\\) a su alrededor: que se colocan sin saber que ese está ahí. <span data-afirma="c1-m3-08">En un
                proceso de Poisson, lo que se ve desde uno de sus puntos, quitado ese punto, tiene la misma
                distribución que el proceso <cite class="cita" data-ref="baddeley2015spatial" data-loc="pp. 294–295"></cite></span>. Es el resultado
                que el capítulo 4 enuncia en su módulo 7 con el nombre de <strong>teorema de Slivnyak</strong>. Con \\(n\\)
                fijo no hace falta: los otros \\(n-1\\) puntos son independientes del punto \\(i\\) por la
                definición del paso 2, el disco queda vacío si caen todos fuera de él,
                \\(P(d_i > r) = (1 - \\pi r^2/|W|)^{{n-1}}\\) con el disco dentro de la ventana, y eso tiende a
                \\(e^{{-\\lambda\\pi r^2}}\\) cuando la ventana crece con \\(n/|W| = \\lambda\\) fijo.</p>
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
              $$E[d_i] = \\int_0^{{\\infty}} P(d_i > r)\\, dr = \\int_0^{{\\infty}} e^{{-\\lambda \\pi r^2}}\\, dr$$
            </li>
            <li>
              <p>Y lo que queda es la integral gaussiana,
                \\(\\int_0^{{\\infty}} e^{{-a r^2}}\\, dr = \\tfrac{{1}}{{2}}\\sqrt{{\\pi/a}}\\), con
                \\(a = \\lambda\\pi\\). El \\(\\pi\\) que trajo el área del disco se cancela contra el de la
                integral y no sobrevive ni una constante suelta:</p>
              $$E[d_i] = \\frac{{1}}{{2}}\\sqrt{{\\frac{{\\pi}}{{\\lambda\\pi}}}} = \\frac{{1}}{{2\\sqrt{{\\lambda}}}}$$
            </li>
            <li>
              <p>Falta pasar de una distancia a la media de las \\(n\\). La esperanza de una media es la media de
                las esperanzas —eso es la linealidad—, y si todas las \\(d_i\\) tienen la misma ley, todas tienen
                la misma esperanza. Que la tengan es otra vez la ventana infinita: todo punto ve alrededor el
                mismo proceso, y junto al borde eso deja de ser verdad.</p>
              $$E[\\bar{{d}}_{{\\min}}] = \\frac{{1}}{{n}} \\sum_{{i=1}}^{{n}} E[d_i] = E[d_i] = \\frac{{1}}{{2\\sqrt{{\\lambda}}}}$$
            </li>
            <li>
              <p>Para decidir si una \\(\\bar{{d}}_{{\\min}}\\) observada se aparta de esa esperanza más de lo que
                daría el azar hace falta su dispersión, y sale de la misma cola. El segundo momento de una
                variable no negativa es \\(\\int_0^\\infty 2r\\,P(d_i > r)\\,dr\\), y esta integral ya es
                inmediata. Restando el cuadrado de la media queda la varianza:</p>
              $$E[d_i^2] = \\int_0^{{\\infty}} 2r\\,e^{{-\\lambda\\pi r^2}}\\, dr = \\frac{{1}}{{\\pi\\lambda}}$$
              $$\\operatorname{{Var}}(d_i) = \\frac{{1}}{{\\pi\\lambda}} - \\frac{{1}}{{4\\lambda}}
                = \\frac{{4 - \\pi}}{{4\\pi\\lambda}}$$
            </li>
            <li>
              <p>La desviación típica de una distancia es entonces \\(c/\\sqrt{{\\lambda}}\\), con
                \\(c = \\sqrt{{(4-\\pi)/(4\\pi)}} = {n(cep['constante_ee'])}\\). Para la media de las \\(n\\) se
                divide además entre \\(\\sqrt{{n}}\\), y eso trata las \\(n\\) distancias como independientes. No
                lo son del todo —dos puntos pueden ser cada uno el vecino más próximo del otro, y entonces su
                distancia cuenta dos veces—, pero es la aproximación que usa <code>clarkevans.test</code>: su
                estadístico \\(z\\) se compara con una normal estándar. <span data-afirma="c1-m3-09">La
                prueba lleva el nombre del índice, no la firma de sus autores: Clark y Evans lo pensaron como
                una medida de cuánto se aparta un patrón del azar, no para contrastarlo con una aproximación
                normal <cite class="cita" data-ref="clark1954distance" data-via="cressie1993statistics" data-loc="p. 605"></cite></span>.</p>
              $$\\operatorname{{ee}}(\\bar{{d}}_{{\\min}}) = \\frac{{c}}{{\\sqrt{{n\\lambda}}}}, \\qquad
                z = \\frac{{\\bar{{d}}_{{\\min}} - 1/(2\\sqrt{{\\lambda}})}}{{\\operatorname{{ee}}(\\bar{{d}}_{{\\min}})}}$$
            </li>
          </ol>
          <p class="derivacion-resultado">La esperanza del paso 7 es el denominador de la cuarta columna de la
            tabla, y la fórmula se lee sola: \\(\\lambda\\) son puntos por unidad de área, luego
            \\(1/\\sqrt{{\\lambda}}\\) es una distancia —por eso \\(R\\) sale sin unidades por construcción y no
            por convenio—. La raíz avisa además de que la densidad no se paga en línea recta: al doblar
            \\(\\lambda\\), la distancia esperada al vecino no cae a la mitad, sino a \\(1/\\sqrt{{2}}\\) de lo
            que era. Y el paso 9 da las dos columnas de la prueba. En los pinos,
            \\(\\operatorname{{ee}} = {n(pc['japanesepines']['nn_ee'])}\\), y la distancia observada,
            {n(pc['japanesepines']['nn_media'])}, queda a \\(z = {n(pc['japanesepines']['ce_z'])}\\) errores
            típicos de la esperada, {n(pc['japanesepines']['nn_esperada'])}: un valor p bilateral de
            <strong>{n(pc['japanesepines']['ce_p'])}</strong>.</p>
        </div>
      </div>

      <p>Y conviene retener de dónde salió, porque se paga más abajo: el disco del paso 3 se contó
        <strong>entero</strong>, y eso supone que el proceso sigue existiendo más allá del borde de la ventana.
        Para un punto pegado al borde eso es falso —parte de su disco cae donde nadie observó nada—, y de ahí
        viene la necesidad de corregir. De dónde sale la corrección misma es otra cuestión, y la nota que sigue
        a la tabla la contesta.</p>

      <p>La tabla hace esa misma división para los tres. Lleva a propósito la columna del denominador, que suele
        omitirse: sin ella el índice hay que creérselo, y con ella se comprueba con una calculadora.</p>

      <table>
        <caption>Los tres regímenes de un patrón puntual, medidos con el índice de Clark-Evans sobre los datos
          canónicos de spatstat. La tercera columna dividida entre la cuarta da la quinta. La sexta y la
          séptima son la prueba de Clark-Evans de <code>clarkevans.test</code>: aproximación normal, bilateral y
          sin corrección de borde, con la \\(z\\) del paso 9 del desarrollo. El régimen se lee de ella con
          \\(\\alpha = {ALFA}\\): agregado o regular si el valor p queda por debajo, según el signo de \\(z\\), y
          compatible con el azar si no.</caption>
        <thead>
          <tr><th scope="col">Patrón</th><th scope="col">n</th><th scope="col">Distancia media al vecino</th>
            <th scope="col">La que daría el azar</th>
            <th scope="col">Clark-Evans</th><th scope="col">\\(z\\)</th><th scope="col">Valor p</th>
            <th scope="col">Régimen</th></tr>
        </thead>
        <tbody>
          <tr><th scope="row">{pc['redwood']['nombre']}</th><td>{pc['redwood']['n']}</td>
            <td>{n(pc['redwood']['nn_media'])}</td><td>{n(pc['redwood']['nn_esperada'])}</td>
            <td>{n(pc['redwood']['clark_evans'])}</td>
            <td>{n(pc['redwood']['ce_z'])}</td><td>{p_ce(pc['redwood'])}</td>
            <td>Agregado</td></tr>
          <tr><th scope="row">{pc['japanesepines']['nombre']}</th><td>{pc['japanesepines']['n']}</td>
            <td>{n(pc['japanesepines']['nn_media'])}</td><td>{n(pc['japanesepines']['nn_esperada'])}</td>
            <td>{n(pc['japanesepines']['clark_evans'])}</td>
            <td>{n(pc['japanesepines']['ce_z'])}</td><td>{p_ce(pc['japanesepines'])}</td>
            <td>Compatible con el azar</td></tr>
          <tr><th scope="row">{pc['cells']['nombre']}</th><td>{pc['cells']['n']}</td>
            <td>{n(pc['cells']['nn_media'])}</td><td>{n(pc['cells']['nn_esperada'])}</td>
            <td>{n(pc['cells']['clark_evans'])}</td>
            <td>{n(pc['cells']['ce_z'])}</td><td>{p_ce(pc['cells'])}</td>
            <td>Regular</td></tr>
        </tbody>
      </table>

      <p>Fíjate en que la columna del azar <em>no</em> es la misma en las tres filas —{n(pc['redwood']['nn_esperada'])},
        {n(pc['japanesepines']['nn_esperada'])} y {n(pc['cells']['nn_esperada'])}—, y ahí está el trabajo que hace
        el índice: las células tienen menos puntos, así que bajo puro azar ya les tocaría estar más separadas.
        Comparar las distancias observadas entre sí sería comparar tres densidades distintas; dividir cada una por
        la suya es lo que las vuelve comparables.</p>

      <p><strong>Y una cautela sobre la tercera fila.</strong> «Regular» describe cómo están repartidos los
        puntos, no por qué. <span data-afirma="c1-m3-17">Los {pc['cells']['n']} puntos de esa fila son centros de
        células biológicas en un corte histológico <cite class="cita" data-ref="baddeley2015spatial" data-loc="p. 93; p. 157"></cite></span>, y una célula ocupa sitio: dos
        centros no pueden quedar más cerca de lo que ese tamaño deja. <span data-afirma="c1-m3-16">Cuando los
        puntos son los centros de objetos de tamaño apreciable, encontrar que están repartidos con regularidad,
        o que se inhiben, puede ser solo un artefacto de ese tamaño: de tratar como puntos ideales lo que no lo
        es <cite class="cita" data-ref="baddeley2015spatial" data-loc="p. 146; p. 210"></cite></span>. La tabla mide bien, y los centros están más
        separados de lo que daría el azar. Lo que no puede decir es si detrás hay algo más que el sitio que
        ocupa cada célula: para afirmar que se repelen haría falta descontar antes su tamaño.</p>

      <div class="note">
        <p><strong>Si ejecutas <code>clarkevans()</code> vas a ver tres números, no uno.</strong> <span data-afirma="c1-m3-12">Los imprime
          con las etiquetas <code>naive</code>, <code>Donnelly</code> y <code>cdf</code>, y su argumento
          <code>correction</code> elige la corrección de borde <cite class="cita" data-ref="baddeley2015spatial" data-loc="p. 259"></cite></span>. La tabla publica
          el <code>naive</code>, que es la división de arriba tal cual: tercera columna entre cuarta. Los otros dos
          corrigen el <strong>efecto de borde</strong>, y conviene saber de qué va porque reaparece en todo el
          capítulo 4. La fórmula \\(E[\\bar{{d}}_{{\\min}}] = 1/(2\\sqrt{{\\lambda}})\\) vale para una ventana
          infinita. <span data-afirma="c1-m3-10">En una finita, un punto pegado al borde puede tener su vecino de verdad <em>fuera</em> del
          cuadrado, donde nadie lo midió; la distancia que se le apunta es la del vecino de dentro, que está más
          lejos. El numerador sale inflado, y \\(R\\) con él <cite class="cita" data-ref="baddeley2015spatial" data-loc="pp. 258–259"></cite></span>.</p>
        <p style="margin-bottom:0;">La corrección que la función llama
          <code>Donnelly</code> lo compensa. El borde explica por qué hace falta corregir; de dónde sale la
          corrección es otra cosa. <span data-afirma="c1-m3-11">La de Donnelly para el estadístico de Clark y Evans
          es un ajuste empírico, y no se generaliza a regiones de forma arbitraria
          <cite class="cita" data-ref="cressie1993statistics" data-loc="p. 607"></cite></span>. En los tres patrones el índice
          <strong>baja</strong>: {n(pc['redwood']['clark_evans'])} →
          <strong>{n(pc['redwood']['clark_evans_donnelly'])}</strong> en las secuoyas,
          {n(pc['japanesepines']['clark_evans'])} →
          <strong>{n(pc['japanesepines']['clark_evans_donnelly'])}</strong> en los pinos y
          {n(pc['cells']['clark_evans'])} →
          <strong>{n(pc['cells']['clark_evans_donnelly'])}</strong> en las células. Ninguno cambia de régimen, así
          que la tabla se sostiene —y los pinos quedan aún más pegados al 1 de lo que ya estaban—. La prueba lo
          confirma. Con la corrección de Donnelly, que es la que <code>clarkevans.test</code> aplica si no se le
          pide otra en una ventana rectangular, el error típico es el mismo y cambia la esperanza: la \\(z\\) de
          los pinos baja a {n(pc['japanesepines']['ce_z_donnelly'])} y su valor p sube a
          {n(pc['japanesepines']['ce_p_donnelly'])}, mientras los valores p de las secuoyas y las células siguen
          por debajo de \\(\\alpha = {ALFA}\\), con \\(z\\) de {n(pc['redwood']['ce_z_donnelly'])} y
          {n(pc['cells']['ce_z_donnelly'])}. Pero fíjate en
          el tamaño del ajuste: en las células vale más de una décima. Sobre una ventana pequeña, o con pocos
          puntos, el borde deja de ser un decimal.</p>
      </div>

      <div class="warning">
        <p><strong>Y una advertencia sobre la fila del medio.</strong> {n(pc['japanesepines']['clark_evans'])}
          está cerca de 1, y la tabla dice «compatible con el azar», no «aleatorio». Lo dice con la prueba de
          Clark-Evans: un valor p bilateral de {n(pc['japanesepines']['ce_p'])}, que con \\(\\alpha = {ALFA}\\) no permite
          rechazar la aleatoriedad. No rechazarla no es demostrarla, y esa diferencia no es cautela
          retórica: \\(R\\) se construye <em>solo</em> con la distancia al vecino <strong>más próximo</strong>, y de
          ella solo con la media. <span data-afirma="c1-m3-13">Es un único número, y esa es la debilidad de los
          índices de este tipo: comprimen toda la información espacial en una cifra y mezclan lo que pasa a
          escalas distintas <cite class="cita" data-ref="baddeley2015spatial" data-loc="p. 260"></cite></span>. En un único número dos estructuras opuestas pueden
          compensarse.</p>
        <p style="margin-bottom:0;">El caso que lo rompe se arma con dos mecanismos a dos escalas, y va aquí
          como escenario, no como dato: árboles que compiten con el de al lado y por eso se separan a corta
          distancia, pero que crecen en manchas grandes marcadas por el suelo o la humedad.
          <span data-afirma="c1-m3-14">No es un escenario rebuscado: un análisis detallado de un bosque de pinos
          negros japoneses encontró las dos cosas a la vez, variación de la densidad y árboles que tienden a no
          crecer juntos <cite class="cita" data-ref="baddeley2015spatial" data-loc="p. 4"></cite></span>. <span data-afirma="c1-m3-15">Y no es lo que pasa con las secuoyas
          de la tabla: sus grupos se atribuyen a la propagación desde un árbol padre que ya murió
          <cite class="cita" data-ref="baddeley2015spatial" data-loc="p. 189"></cite></span>. Las dos cosas tiran de \\(R\\) en sentidos
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
""" + CIERRE_FUENTES


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
      <p>El módulo 3 midió que lo cercano se parece: entre estaciones a menos de {b0['d2']} km, la I de Moran de la
        temperatura vale {n(b0['I'])}, y aun quitada la altitud, que explicaba casi un tercio, la de los residuos
        sigue en {n(tb['residuos_altitud']['bandas'][0]['I'])}, muy por encima de su franja de permutación. Cuando
        dos observaciones vecinas se parecen más de lo que daría el azar, contarlas como independientes es contar
        de más, y eso tiene un precio.</p>

      <p>Este es el módulo que justifica el curso. Todo lo que aprendiste en inferencia —el error estándar
        \\(s/\\sqrt{{n}}\\), el intervalo al 95&nbsp;%, el valor p— descansa en un supuesto: que las observaciones
        son independientes. <span data-afirma="c1-m4-01">Con datos espaciales ese supuesto a menudo no es realista: la dependencia
        espacial está en todas partes, y con ella los procedimientos clásicos rinden mal
        <cite class="cita" data-ref="cressie1993statistics" data-loc="p. 22; p. 25"></cite></span>. La pregunta no es si el supuesto falla, sino
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

      <p>El error estándar verdadero es el que sale de sumar todas las correlaciones, como en el recuadro de
        abajo: \\(\\sqrt{{\\mathbf{{1}}^\\top \\mathbf{{R}}\\,\\mathbf{{1}}}}/n = {n(ci['ee_exacto'])}\\), donde
        \\(\\mathbf{{R}}\\) es la matriz de las correlaciones entre celdas. Con él, las medias no se
        mueven: son las mismas {ci['n']}. Cambia el largo de los segmentos, cuyo semiancho pasa de
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
        <p>Aquí \\(\\rho_{{ij}}\\) es la correlación entre las observaciones \\(i\\) y \\(j\\). La segunda
          igualdad supone que todas tienen la misma varianza \\(\\sigma^2\\), y el paso tres pide además la
          misma media; el campo simulado cumple las dos cosas por construcción. El corchete es el
          <strong>efecto de diseño</strong>. Vale 1 cuando la suma de las
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

      <div class="derivacion">
        <button type="button" class="derivacion-boton" aria-expanded="false" aria-controls="der-s2-esperada">
          <i class="fas fa-square-root-variable" aria-hidden="true"></i>
          <span class="derivacion-texto">Ver de dónde sale \\(\\mathbb{{E}}[s^2] = \\sigma^2\\,\\frac{{n}}{{n-1}}(1 - 1/n_{{\\text{{eff}}}})\\)</span>
          <i class="fas fa-chevron-down" aria-hidden="true"></i>
        </button>
        <div class="derivacion-panel" id="der-s2-esperada" hidden>
          <ol class="derivacion-pasos">
            <li>
              <p>La suma de cuadrados de \\(s^2\\) se parte en dos alrededor de un número \\(\\mu\\). Es
                álgebra, sin probabilidad, y vale para cualquier \\(\\mu\\): dentro del paréntesis se resta y se
                suma \\(\\mu\\), y el término cruzado vale \\(-2n(\\bar{{Z}} - \\mu)^2\\) y se junta con el
                último. Los supuestos entran en el paso siguiente.</p>
              $$\\sum_i (Z_i - \\bar{{Z}})^2 = \\sum_i (Z_i - \\mu)^2 - n\\,(\\bar{{Z}} - \\mu)^2$$
            </li>
            <li>
              <p>Aquí entran dos supuestos, y son los del campo simulado: todas las celdas tienen la misma
                media, que es el \\(\\mu\\) del paso 1, y la misma varianza \\(\\sigma^2\\). Al tomar esperanzas,
                cada \\((Z_i - \\mu)^2\\) da entonces la varianza de una celda, porque la media de
                cada celda es \\(\\mu\\), y \\((\\bar{{Z}} - \\mu)^2\\) da la varianza de la media, porque
                la media de \\(\\bar{{Z}}\\) también es \\(\\mu\\). La segunda es la del paso «Dos» del recuadro de
                arriba,
                \\(\\sigma^2/n_{{\\text{{eff}}}}\\): es lo que significa que las celdas informen como
                \\(n_{{\\text{{eff}}}}\\).</p>
              $$\\mathbb{{E}}\\Bigl[\\sum_i (Z_i - \\bar{{Z}})^2\\Bigr] = \\sum_i \\operatorname{{Var}}(Z_i) -
                n\\operatorname{{Var}}(\\bar{{Z}})$$
              $$= n\\sigma^2 - n\\,\\frac{{\\sigma^2}}{{n_{{\\text{{eff}}}}}}
                = n\\sigma^2\\left(1 - \\frac{{1}}{{n_{{\\text{{eff}}}}}}\\right)$$
              <p>Sin correlación \\(n_{{\\text{{eff}}}} = n\\) y la suma vale en promedio \\((n-1)\\sigma^2\\):
                ese \\(n - 1\\) es la razón de dividir entre \\(n - 1\\) y no entre \\(n\\).</p>
            </li>
            <li>
              <p>\\(s^2\\) es esa suma dividida entre \\(n-1\\), y ya está:</p>
              $$\\mathbb{{E}}[s^2] = \\sigma^2\\,\\frac{{n}}{{n-1}}\\left(1 - \\frac{{1}}{{n_{{\\text{{eff}}}}}}\\right)$$
            </li>
          </ol>
          <p class="derivacion-resultado">Con \\(\\sigma^2 = {inf['sigma']}\\), \\(n = {inf['n']}\\) y
            \\(n_{{\\text{{eff}}}} = {n(r4['n_eff'])}\\) sale \\(\\mathbb{{E}}[s^2] = {n(r4['s2_esperada'])}\\),
            y la media de las \\(s^2\\) de las {ent(inf['nrep'])} réplicas es {n(r4['s2_medida'])}. Cuanto menor
            es \\(n_{{\\text{{eff}}}}\\), más se aleja \\(s^2\\) de \\(\\sigma^2\\): la parte de la
            variabilidad que la dependencia mete en la media común es justo la que deja de verse entre celdas.</p>
        </div>
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
        remuestreando <strong>departamentos enteros</strong>, que conserva la dependencia dentro de cada uno.
        <span data-afirma="c1-m4-02">Lo segundo es un remuestreo por bloques. Con datos dependientes, aplicar a
        ciegas el remuestreo clásico puede dar respuestas incorrectas, y lo que se propone en su lugar es
        remuestrear subregiones enteras, que en esa propuesta son congruentes: del mismo tamaño y la misma forma
        <cite class="cita" data-ref="cressie1993statistics" data-loc="pp. 491–492"></cite></span>. Los departamentos no lo son, y esa diferencia tiene una consecuencia que
        se mide más abajo.</p>

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
          sí mucho más de lo que se parecerían {ent(ir['n_departamentos'])} estimaciones independientes. <span data-afirma="c1-m4-03">El
          <em>jackknife</em> clásico recalcula el estimador quitando una observación cada vez; aquí lo que se
          quita es un bloque entero, y de esa versión espacial, que elimina una subregión, se advierte que dista
          de ser obvio cómo hacerla <cite class="cita" data-ref="cressie1993statistics" data-loc="p. 489; p. 492"></cite></span>. Con esa reserva, repone lo que falta: toma la dispersión de los \\(K = {ir['n_departamentos']}\\)
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

""" + nota_datos(
    f"Los dos bloques leen {enlace_datos('municipios')}: los {ent(EX['municipios']['filas'])} municipios, "
    "cada uno con un punto interior y cinco columnas, "
    + ", ".join(f"<code>{c}</code>" for c in EX["municipios"]["columnas"][:-1])
    + f" y <code>{EX['municipios']['columnas'][-1]}</code>. El departamento lo sacan los bloques de los "
    "dos primeros dígitos de <code>divipola</code>. Son datos de terceros que se redistribuyen con "
    "atribución: la deserción y la cobertura neta son del <strong>Ministerio de Educación "
    "Nacional</strong> (CC BY-SA 4.0), los resultados de Saber 11, del <strong>ICFES</strong> "
    f"(CC BY-SA 4.0), y los municipios, {ATRIB_DANE}.", varios=False) + tabs(
    "El error estándar ingenuo frente al de bloques, sobre la deserción real",
    """library(sf)

mun &lt;- st_read("entrega/datos/cap1_municipios.gpkg", quiet = TRUE)
ok  &lt;- mun[!is.na(mun$desercion), ]
ok$dpto &lt;- substr(ok$divipola, 1, 2)      # el departamento
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
    """import geopandas as gpd, numpy as np

mun = gpd.read_file("entrega/datos/cap1_municipios.gpkg")
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
""" + CIERRE_FUENTES


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
        <p><span data-afirma="c1-m5-01">Se define \\(n_{{\\text{{eff}}}}\\) como el número de observaciones <em>independientes</em> que darían la
          misma varianza de la media que las \\(n\\) observaciones correlacionadas que se tienen
          <cite class="cita" data-ref="cressie1993statistics" data-loc="pp. 14–15"></cite></span>. Si todas tienen
          la misma varianza, ese número tiene fórmula cerrada:</p>
        <p style="text-align:center;">$$n_{{\\text{{eff}}}} = \\frac{{n}}{{1 + (n-1)\\,\\bar{{\\rho}}}}$$</p>
        <p style="text-align:center;">$$\\bar{{\\rho}} = \\frac{{1}}{{n(n-1)}} \\sum_{{i \\neq j}} \\rho_{{ij}}$$</p>
        <p style="margin-bottom:0;">Aquí \\(\\rho_{{ij}}\\) es la correlación entre las observaciones \\(i\\) y
          \\(j\\) —si solo depende de la distancia que las separa, \\(\\rho(h_{{ij}})\\)— y \\(\\bar{{\\rho}}\\) es su
          <strong>media sobre todos los pares</strong>. La fórmula no es una aproximación ni exige que todos los
          pares se parezcan lo mismo: <strong>es una identidad</strong>. La correlación puede decaer con la
          distancia, como decae el parecido que el correlograma del módulo 3 mide con la I de Moran —que no es
          una correlación—; a la varianza de la media solo le llega su promedio.</p>
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
#> """ + f"rho = 0.10 -> n = 1000 da n_eff = {n(ne['rejilla'][-1]['n_eff'][4])} (techo {n(10)})") + CIERRE_FUENTES


# =====================================================================
# MÓDULO 6 · Estacionariedad, isotropía y una sola realización
# =====================================================================
# R3 · T3.4 (D7): tres frases de este módulo contaban la producción.
#   · «las 1 000 que simula el generador»: era genera_cap1.R, no un generador
#     de números aleatorios; ahora «que se simularon».
#   · «El generador del capítulo comprueba esa coherencia y se detiene si los
#     dos módulos se separan más de tres errores conjuntos»: es cierto
#     —genera_cap1.R para si m4 y m6 se separan más de 3 errores de Monte
#     Carlo conjuntos—, pero al estudiante le sirve el método, no el guion:
#     «Cuadrarlas es parte del método».
#   · La nota «Por qué el mapa y la curva son ahora el mismo experimento»
#     contaba que, «hasta esta versión», los tres mapas venían de una
#     simulación aparte, con otra rejilla y otra semilla, y la curva era de un
#     campo que no estaba en ningún mapa: las cifras y la prosa eran correctas
#     y lo que fallaba era el cableado, que ningún auditor de cifras veía. Se
#     queda la lección («¿son de este dato?»), dicha sin la historia.
MOD6 = cabecera(
    6, "Estacionariedad, isotropía y una sola realización", "One realization",
    "Ver el problema que hace difícil toda la estadística espacial: del "
    "proceso que se quiere estudiar solo existe una realización.") + f"""
      <p>Mira los tres mapas de abajo. Son <strong>tres realizaciones del mismo proceso</strong>: misma media, misma
        covarianza, mismos parámetros. Y no se parecen. No están escogidas: son <strong>las tres primeras</strong> de
        las {ent(ur['n_realizaciones'])} que se simularon, y de ese mismo lote salen la banda del gráfico y
        todas las cifras de este módulo. Elegir las tres más distintas habría dado una figura más vistosa y un
        argumento peor.</p>

      <div class="simulador" data-simulador="una-realizacion">
        <h4><i class="fas fa-dice" aria-hidden="true"></i> Tres veces el mismo proceso</h4>
        <p class="simulador-intro">Tres realizaciones de un campo gaussiano con media {ur['media_del_proceso']} y
          alcance \\(\\phi = {ur['phi']}\\) sobre {ur['k']}×{ur['k']} celdas. <strong>Cambia de realización</strong> y
          mira moverse las tres cosas a la vez: el mapa, la lectura y —debajo— el variograma <em>de esa</em>
          realización contra el teórico y la banda del 5&nbsp;% al 95&nbsp;%. La curva punteada es el teórico
          promediado sobre los pares de cada clase de distancia; el texto de debajo del simulador explica por
          qué no es \\(\\gamma(k)\\), evaluada en la distancia \\(k\\) de la clase.</p>
        <div class="simulador-controles"></div>
        <div class="geomapa" data-geomapa="cap1-realizacion"></div>
        <div class="grafico-wrapper" style="height:290px;">
          <canvas aria-label="Variograma de una realización frente al teórico promediado en cada clase de distancia, con la banda del 5 al 95 por ciento sobre mil realizaciones" role="img"></canvas>
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
          separan {n(ur['discrepancia_con_modulo4'])} puntos, que es poco más de un error de Monte Carlo.
          <strong>Cuadrarlas es parte del método:</strong> si se separaran más de tres errores conjuntos, habría
          que averiguar cuál de las dos está mal antes de publicar ninguna. Dos cifras que deberían coincidir y
          viven a dos módulos de distancia son justo las que nadie compara.</p>
      </div>

      <div class="definition">
        <h3>Estacionariedad: el supuesto que hace posible estimar algo</h3>
        <p>Si solo hay una realización, ¿cómo se estima una media o una covarianza? El primer paso es suponer que
          <strong>distintas partes del mapa son repeticiones del mismo mecanismo</strong>. Eso es la
          estacionariedad, y hace falta, pero no basta: el último punto de la lista dice qué más.</p>
        <ul>
          <li><strong>De segundo orden:</strong> \\(E[Z(s)] = \\mu\\) para todo \\(s\\), y
            \\(\\operatorname{{Cov}}(Z(s), Z(s+h)) = C(h)\\) depende solo de la separación \\(h\\), no de dónde
            estén los dos puntos.</li>
          <li><strong>Intrínseca:</strong> más débil, y por eso más general. <span data-afirma="c1-m6-01">Pide dos cosas: que la media sea la misma
            en todas partes, \\(E[Z(s)] = \\mu\\), y que la varianza de las <em>diferencias</em> dependa solo de
            la separación,
            \\(\\tfrac{{1}}{{2}}\\operatorname{{Var}}(Z(s+h) - Z(s)) = \\gamma(h)\\)
            <cite class="cita" data-ref="cressie1993statistics" data-loc="pp. 60–61"></cite></span>. De la primera sale que las diferencias tienen
            media cero, \\(E[Z(s+h) - Z(s)] = 0\\); lo que ya no se pide es una covarianza \\(C(h)\\). <span data-afirma="c1-m6-02">Todo proceso estacionario de
            segundo orden es intrínseco, con \\(\\gamma(h) = C(0) - C(h)\\), pero no al revés. Un ejemplo
            es el movimiento browniano <cite class="cita" data-ref="cressie1993statistics" data-loc="pp. 67–68"></cite></span>. En la recta tiene varianza finita en cada punto,
            \\(\\operatorname{{Var}}B(t) = t\\), pero esa varianza crece con \\(t\\), así que no existe una \\(C(h)\\)
            que valga igual en todas partes y el proceso no es estacionario de segundo orden. Sus diferencias, en
            cambio, cumplen las dos condiciones, con \\(\\gamma(h) = |h|/2\\). Por eso el variograma es más general
            que la covarianza. <span data-afirma="c1-m6-03">Más general no quiere decir obligatoria: suponer una
            u otra es a menudo cuestión de gusto de quien modela <cite class="cita" data-ref="cressie1993statistics" data-loc="p. 70"></cite></span>.</li>
          <li><strong>Isotropía:</strong> además, que \\(C\\) y \\(\\gamma\\) dependan solo de \\(\\lVert h \\rVert\\)
            y no de la dirección. Es una comodidad, no una ley: la anisotropía del capítulo 9 es lo que pasa cuando
            no se cumple.</li>
          <li><strong>Ergodicidad:</strong> <span data-afirma="c1-m6-04">que los promedios sobre el espacio de <em>una</em> realización
            converjan a los del proceso cuando la región crece sin límite: es la propiedad que deja estimar
            esperanzas con promedios espaciales <cite class="cita" data-ref="cressie1993statistics" data-loc="p. 53; p. 57"></cite></span>. Se refiere al <em>proceso</em>, no al
            mapa. Para la media pide que la covarianza media entre los puntos de la región tienda a cero;
            en la práctica, que la covarianza decaiga con la distancia. La estacionariedad dice que hay algo fijo
            que estimar; la ergodicidad, que una sola realización basta para estimarlo, y la primera no da la
            segunda. El contraejemplo es corto: \\(Z(s) = Y\\) en todo \\(s\\), con \\(Y\\) aleatoria. Es
            estacionario, con \\(\\rho(h) = 1\\) a toda distancia y \\(\\bar{{\\rho}} = 1\\), y la media de una
            realización es \\(Y\\), que no se acerca a la del proceso por mucho que crezca la región. El proceso
            de arriba, en cambio, <strong>es ergódico</strong>: su correlación \\(e^{{-h/\\phi}}\\) decae con la
            distancia. Aun así la media de una realización se aparta de la del proceso con desviación típica
            {n(ur['sd_de_las_medias'])}, porque la región es finita y pequeña frente al alcance. Aprovechar la
            ergodicidad con un solo mapa exige además una región grande frente al alcance: es una condición
            práctica sobre el diseño, no parte de la definición.</li>
        </ul>
        <p style="margin-bottom:0;">Sin estacionariedad no hay repetición, y sin ergodicidad la repetición no alcanza.
          El precio de suponer estacionariedad: si la media cambia de sitio a sitio —una <em>tendencia</em>—, lo que se rompe es la primera
          condición de la intrínseca, porque \\(E[Z(s+h) - Z(s)]\\) deja de ser cero. <span data-afirma="c1-m6-05">El variograma empírico promedia
          diferencias al cuadrado, y si \\(m(s)\\) es la media en cada sitio, la esperanza de cada sumando ya no es
          \\(\\gamma(h)\\) sino \\(\\gamma(h) + \\tfrac{{1}}{{2}}\\,(m(s+h) - m(s))^2\\)
          <cite class="cita" data-ref="cressie1993statistics" data-loc="p. 69"></cite></span>. Con una tendencia lineal ese
          término de más crece como \\(h^2\\): el cambio de media se contabiliza como
          dependencia. Es exactamente lo que pasaba con la altitud en el módulo 3.</p>
      </div>

      <div class="derivacion">
        <button type="button" class="derivacion-boton" aria-expanded="false" aria-controls="der-ergodicidad">
          <i class="fas fa-square-root-variable" aria-hidden="true"></i>
          <span class="derivacion-texto">Ver por qué la media de una realización converge solo si \\(\\bar{{\\rho}} \\to 0\\)</span>
          <i class="fas fa-chevron-down" aria-hidden="true"></i>
        </button>
        <div class="derivacion-panel" id="der-ergodicidad" hidden>
          <ol class="derivacion-pasos">
            <li>
              <p>Se parte de la varianza de la media del módulo 5, que solo pide lo que da la estacionariedad de
                segundo orden: la misma media y la misma varianza \\(\\sigma^2\\) en todas las observaciones. Se
                separa en sus dos términos:</p>
              $$\\operatorname{{Var}}(\\bar{{Z}}) = \\frac{{\\sigma^2}}{{n}} \\bigl[1 + (n-1)\\,\\bar{{\\rho}}\\bigr]
                = \\frac{{\\sigma^2}}{{n}} + \\sigma^2\\,\\frac{{n-1}}{{n}}\\,\\bar{{\\rho}}$$
            </li>
            <li>
              <p>Al crecer \\(n\\) el primer término se va a cero siempre: es el de la independencia. El segundo
                se comporta como \\(\\sigma^2\\bar{{\\rho}}\\). Así que la media de una realización converge a
                la del proceso —su varianza se va a cero— si y solo si la correlación media entre pares se va a
                cero.</p>
              $$\\operatorname{{Var}}(\\bar{{Z}}) \\to 0 \\iff \\bar{{\\rho}} \\to 0$$
            </li>
            <li>
              <p>La estacionariedad fija \\(\\rho(h)\\), pero no \\(\\bar{{\\rho}}\\): \\(\\bar{{\\rho}}\\) es el
                promedio de \\(\\rho(h)\\) sobre los pares que caben en la región, y depende de cómo crezca. Es
                la tabla del módulo 5, ahora leída en desviaciones típicas de la media. Al
                <strong>rellenar</strong> el cuadrado de lado {tc['lado_relleno']}, \\(\\bar{{\\rho}}\\) tiende a
                \\(\\bar{{\\rho}}_\\infty\\) y la desviación típica de la media, a
                \\(\\sigma\\sqrt{{\\bar{{\\rho}}_\\infty}} = {n(erg['sd_media_relleno_limite'])}\\): con
                {ent(erg['n_ultima'])} observaciones ya vale {n(erg['sd_media_relleno_ultima'])}, y por mucho que se
                rellene no bajará de {n(erg['sd_media_relleno_limite'])}.
                Al <strong>ampliar</strong> la región, \\(\\bar{{\\rho}}\\) tiende a cero porque \\(\\rho(h)\\)
                decae con la distancia, y con {erg['k_ultima']}×{erg['k_ultima']} celdas la desviación típica ya
                ha bajado a {n(erg['sd_media_ampliacion_ultima'])}.</p>
              $$\\text{{rellenar: }} \\operatorname{{sd}}(\\bar{{Z}}) \\to \\sigma\\sqrt{{\\bar{{\\rho}}_\\infty}} > 0$$
              $$\\text{{ampliar: }} \\operatorname{{sd}}(\\bar{{Z}}) \\to 0$$
            </li>
            <li>
              <p>La retícula de este módulo es la del módulo 4: {ur['k']}×{ur['k']} celdas con
                \\(\\phi = {ur['phi']}\\) y \\(\\sigma^2 = {inf['sigma']}\\). Sus {ur['n']} celdas informan como
                \\(n_{{\\text{{eff}}}} = {n(ur['n_eff'])}\\), así que la desviación típica exacta de la media de
                una realización es</p>
              $$\\operatorname{{sd}}(\\bar{{Z}}) = \\frac{{\\sigma}}{{\\sqrt{{n_{{\\text{{eff}}}}}}}} = {n(ur['sd_exacta_de_la_media'])}$$
              <p>Medida sobre las {ent(ur['n_realizaciones'])} realizaciones sale {n(ur['sd_de_las_medias'])}. La
                desviación típica medida tiene su propio error de Monte Carlo, {n(ur['emc_sd_de_las_medias'])}, y
                la diferencia es de {n(ur['sd_medida_a_emc'])} errores: ruido de la simulación.</p>
            </li>
          </ol>
          <p class="derivacion-resultado">El proceso es estacionario y ergódico —el paso 3 lo muestra: al
            ampliar, la desviación típica de la media baja hacia cero—, y aun así una realización se aparta de su
            media con desviación típica {n(ur['sd_exacta_de_la_media'])}. No es un fallo de ergodicidad: es el
            precio de una región finita, y esta es pequeña frente al alcance. El
            {n(ur['pct_rechaza_ingenuo'])}&nbsp;% de rechazos del análisis ingenuo es otro problema, el del
            módulo 4, y ampliar la región no lo arregla: la media converge, pero el error estándar ingenuo sigue
            sin contar las correlaciones. La misma cuenta tiene versión
            continua, sobre una región \\(D\\) y con la covarianza \\(C\\):
            \\(\\operatorname{{Var}}(\\bar{{Z}}_D) = \\frac{{1}}{{|D|^2}} \\iint_D C(s-u)\\,ds\\,du\\), la
            covarianza media entre dos puntos de \\(D\\). La media es ergódica si esa covarianza media se va a
            cero al crecer \\(D\\), y para eso basta que \\(\\int |C(h)|\\,dh\\) sea finita: con \\(u\\) fijo,
            la integral de \\(|C(s-u)|\\) sobre los \\(s\\) de \\(D\\) no pasa de la de \\(|C(h)|\\) sobre el
            plano entero, así que la covarianza media no pasa de \\(\\frac{{1}}{{|D|}}\\int |C(h)|\\,dh\\), que se
            va a cero cuando \\(|D|\\) crece. Estimar la
            covarianza o el variograma pide la misma idea con más cuenta, y este capítulo no la hace.</p>
        </div>
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
        botón</strong>: cada realización trae el suyo. Antes de leerlo hay que decir contra qué se compara. <span data-afirma="c1-m6-06">El
        estimador agrupa los pares por <strong>clases de distancia</strong>, como un histograma agrupa los datos
        de una variable <cite class="cita" data-ref="cressie1993statistics" data-loc="p. 70"></cite></span>: en la clase \\(k\\) promedia todos
        los pares de celdas cuya distancia queda a menos de media celda de \\(k\\), medida en pasos de
        retícula, y esos pares no están todos a distancia \\(k\\): en la clase 1 entran los vecinos de lado,
        a distancia 1, y también los diagonales, a \\(\\sqrt{{2}}\\). La referencia justa de cada clase no es entonces
        \\(\\gamma(k)\\), sino \\(\\gamma\\) promediada sobre esos mismos pares, \\(\\bar\\gamma_k\\), que es la curva
        punteada del gráfico. En la clase 1 vale <strong>{n(vg6['teorico_clase'][0])}</strong> frente a
        \\(\\gamma(1) = {n(vg6['teorico'][0])}\\), y la media de las {ent(ur['n_realizaciones'])} realizaciones,
        {n(vg6['media'][0])}, cae sobre la primera y no sobre la segunda.</p>

      <p>Contra esa referencia, las tres realizaciones se apartan, en su peor clase, en
        {n(rv[0]['desvio_rel_max'])}, {n(rv[1]['desvio_rel_max'])} y {n(rv[2]['desvio_rel_max'])} veces su valor
        —clases {ent(rv[0]['lag_desvio_max'])}, {ent(rv[1]['lag_desvio_max'])} y
        {ent(rv[2]['lag_desvio_max'])}—, y la banda del 5&nbsp;% al 95&nbsp;% en la clase 4 tiene una anchura de
        <strong>{n(ur['banda_rel_lag4'])}</strong> veces el valor de referencia. Es tan ancha que las tres caben
        dentro de ella en las ocho clases —en la 4 se apartan {n(rv[0]['desvio_rel_lag4'])},
        {n(rv[1]['desvio_rel_lag4'])} y {n(rv[2]['desvio_rel_lag4'])}—, y conviene no leer eso como un aprobado:
        <strong>caber en la banda no es parecerse al proceso</strong>, porque la banda mide lo que puede pasar, no lo
        que pasó. <span data-afirma="c1-m6-07">Con una realización no se puede saber si lo que se ve es el proceso o el azar de esa realización, y
        sin algún supuesto más sobre el proceso no hay inferencia posible <cite class="cita" data-ref="cressie1993statistics" data-loc="p. 53"></cite></span>:
        es un problema de fondo, no una limitación del método.</p>

      <div class="note">
        <p style="margin-bottom:0;"><strong>Por qué el mapa y la curva son el mismo experimento.</strong> El
          variograma que cambia con el botón es el de la realización que enseña el mapa, y la banda y todas las
          cifras del módulo salen del mismo lote de {ent(ur['n_realizaciones'])} realizaciones. Si los mapas
          vinieran de una simulación <em>aparte</em>, con otra rejilla y otra semilla, cada cifra podría ser
          correcta y la prosa también, y la curva seguiría siendo la de un campo que no está en ningún mapa: un
          error de cableado, que comprobar los números no ve. Si alguna vez heredas una figura de otra persona, la
          pregunta que más rinde no es «¿son correctos estos números?» sino <strong>«¿son de este dato?»</strong>.</p>
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
#> """ + f"media del proceso = 0 | sd de las medias = {n(ur['sd_de_las_medias'], 1)}") + CIERRE_FUENTES


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
      <p>Los módulos 4 a 6 midieron la dependencia entre unidades que estaban dadas: las celdas de una retícula,
        los municipios. Pero la unidad también se elige, y con ella cambia la cifra. Es el soporte del módulo 2,
        ahora con consecuencias.</p>

      <p>La deserción escolar de los {ent(es['n_municipal'])} municipios colombianos tiene un índice de Moran de
        <strong>{n(es['moran_municipal'])}</strong>: autocorrelación inequívoca, a {n(es['z_municipal'])}
        desviaciones estándar de lo que daría el azar. Agrega esos municipios a los {es['n_departamental']}
        departamentos y la misma variable da <strong>{n(es['moran_departamental'])}</strong>, a
        {n(es['z_departamental'])} desviaciones: ya no se distingue del azar
        (p&nbsp;=&nbsp;{n(es['p_departamental'])}). Es la prueba de Moran bajo aleatorización y a una cola, la
        de la autocorrelación positiva. <span data-afirma="c1-m7-01">Es lo que hace <code>moran.test</code> si no
        se le pide otra cosa: sus argumentos valen por defecto <code>randomisation = TRUE</code> y
        <code>alternative = "greater"</code> <cite class="cita" data-ref="pebesma2023spatial" data-loc="§15.2"></cite></span>.</p>

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
        <em>problema de la unidad de área modificable</em> —el MAUP—, y es lo que el capítulo 3 desarrolla entero.
        <span data-afirma="c1-m7-02">Se llama así a que las conclusiones pueden cambiar cuando los mismos datos
        se agregan a otro nivel espacial, y junta dos efectos. El de escala es el de arriba: los mismos datos
        en unidades cada vez mayores. El de zonificación aparece al formar las unidades de otra manera, con otra forma, a la
        misma escala o a una parecida <cite class="cita" data-ref="moraga2019geospatial" data-loc="§5.5"></cite></span>.</p>

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
        <h3>Por qué sube al agregar: lo que el promedio le hace al ruido</h3>
        <p><span data-afirma="c1-m7-03">Que la correlación entre dos variables se aleje de cero cuanto más se
          agrega es lo que se observa de ordinario, y a esa dependencia de la correlación respecto del soporte
          también se la ha llamado problema de la unidad de área modificable
          <cite class="cita" data-ref="cressie1993statistics" data-loc="p. 285"></cite></span>. El mecanismo se puede escribir.
          Descompón cada variable en un componente <em>compartido</em> —que es lo que las correlaciona— y un ruido
          propio de cada celda. Al promediar \\(m\\) celdas, el compartido apenas cambia porque es suave y las celdas
          vecinas tienen casi el mismo valor; el ruido, en cambio, se cancela: su varianza se divide por \\(m\\).
          La covarianza entre las dos variables es la del componente compartido, y el promedio la reduce poco,
          porque el compartido es suave. La varianza de cada una es la del compartido más la del ruido, y el
          promedio divide la del ruido entre \\(m\\). La correlación es la covarianza dividida entre el producto
          de las dos desviaciones típicas: el numerador encoge poco y el denominador mucho, así que sube su valor
          absoluto, \\(|r|\\).</p>
        <p style="margin-bottom:0;"><strong>Y ahí está la condición del fenómeno:</strong>
          el efecto necesita que el ruido <em>no</em> tenga estructura espacial. Si el componente independiente
          también fuera un campo suave, promediar se llevaría los dos por igual y no pasaría nada. {ag['mecanismo']}</p>
      </div>

      <div class="warning">
        <p><strong>Ahora la parte incómoda: agregar no siempre infla.</strong> La versión corta de esta lección —«al
          agregar, la correlación se hace más fuerte»— no es una ley: describe lo que pasa de ordinario, y basta el
          dato colombiano para ver que no pasa siempre. <span data-afirma="c1-m7-04">Tampoco es una rareza de
          este dato: agregando de varias maneras unas mismas observaciones de áreas pequeñas se ha obtenido
          un recorrido amplio de coeficientes de correlación, positivos y negativos
          <cite class="cita" data-ref="cressie1993statistics" data-loc="p. 285"></cite></span>. Sobre
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
        <strong>{ent(agn['total_rectangulos'])}</strong>, un <strong>{n(agn['inflacion_pct'])}&nbsp;%</strong> más.
        <span data-afirma="c1-m7-05">El ejemplo no es de este curso: es el de
        <cite class="cita" data-ref="pebesma2023spatial" data-loc="§5.2" data-modo="narrativa"></cite>, con la misma rejilla sobre los mismos
        condados y los mismos dos totales</span>.</p>
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
        <p><span data-afirma="c1-m7-06">Agregar por <em>grupos</em> —todos los municipios de un departamento— asigna cada unidad a exactamente
          un grupo. De ahí sale una propiedad: <strong>la suma de las sumas es la suma</strong>. Para las
          variables que son cantidades no se pierde nada y no se inventa nada, y la geometría del grupo es la
          unión de las que lo forman <cite class="cita" data-ref="pebesma2023spatial" data-loc="§5.2"></cite></span>. Conviene
          usarla como control de rutina.</p>
        <p style="margin-bottom:0;">En cuanto el destino <em>no</em> es una unión de los originales —una rejilla,
          una cuenca, un área metropolitana, una localidad que parte municipios— esa garantía se cae, y hay que
          <strong>repartir</strong> en vez de emparejar. <span data-afirma="c1-m7-07">La herramienta se llama
          <em>interpolación ponderada por área</em>: mira cuánto solapa cada unidad de origen con cada una de
          destino y pesa con ese solape el valor del origen
          <cite class="cita" data-ref="pebesma2023spatial" data-loc="§5.3"></cite></span>. A cada trozo de solape le toca su parte
          proporcional. Sobre los mismos rectángulos de antes
          devuelve <strong>{n(agn['total_por_area'])}</strong> muertes —el total exacto—, y que lo devuelva no es
          una casualidad: es la comprobación de que está bien hecha.</p>
      </div>

      <p>Con una bifurcación que hay que decir en voz alta, porque es la del módulo 2 otra vez: repartir un
        <em>conteo</em> y repartir una <em>tasa</em> no se hacen igual. <span data-afirma="c1-m7-08">Al conteo
        —extensivo— le toca la parte proporcional del origen que lo cede: el área del trozo entre el área del
        origen. A la tasa —intensiva— le corresponde un promedio ponderado sobre el destino: el área del trozo
        entre el área del destino. Las dos reglas suponen algo. La primera, que el conteo está repartido de
        manera uniforme dentro de cada origen; la segunda, que la tasa es constante dentro de él
        <cite class="cita" data-ref="pebesma2023spatial" data-loc="§5.3"></cite></span>. Pedir la que no era no da error: da un
        número, y el número es plausible.</p>

      <p><strong>Y ahora lo mismo, aplicado a este capítulo.</strong> La deserción departamental de más arriba —la
        que da I&nbsp;=&nbsp;{n(es['moran_departamental'])}— se calculó promediando las tasas municipales
        <em>sin ponderar</em>: cada municipio pesa lo mismo, tenga quinientos habitantes o dos millones. Es una
        elección legítima, y es una elección. Repartiendo por área sobre los mismos
        {agco['n_departamentos']} departamentos, las dos versiones se parecen —correlacionan
        <strong>{n(agco['cor_reglas'])}</strong>— pero no coinciden: difieren
        <strong>{n(agco['dif_media_abs'])}</strong> puntos de media y
        <strong>{n(agco['dif_max'])}</strong> en el departamento donde más.</p>

      <p>Y el titular de este módulo se mueve con ellas. La I de Moran pasa de
        <strong>{n(agco['moran_sin_ponderar'])}</strong> a <strong>{n(agco['moran_por_area'])}</strong>
        <em>sin que se mueva una sola frontera</em>. La escala no era la única decisión que se toma al agregar:
        también se decide la regla, y esa suele tomarse sin mirar.</p>

      <div class="note">
        <p style="margin-bottom:0;"><strong>Ninguna de las dos es «la buena», y conviene decirlo antes de que
          alguien elija la que le convenga.</strong> Una tasa es un cociente, y la de un departamento es la
          suma de los numeradores de sus municipios entre la suma de sus denominadores. Eso es lo mismo que
          promediar las tasas municipales con el denominador como peso: la deserción se debería ponderar por
          <strong>matrícula</strong> —es lo que el módulo 2 midió sobre Carolina del Norte—, y esta base no la
          trae. Así que entre las dos que sí se pueden calcular no se elige entre lo correcto y lo
          incorrecto: se elige entre dos aproximaciones, y lo honesto es decir cuál se usó.</p>
      </div>

""" + nota_datos(
    f"La pestaña de Python del primer bloque lee {enlace_datos('nc')}, el del módulo 2. El segundo bloque "
    f"lee {enlace_datos('municipios')}, el del módulo 4, y la vecindad de reina de los municipios, "
    f"{enlace_datos('reina')}, en GAL, un formato de texto que leen <code>spdep</code> y "
    "<code>libpysal</code>. La vecindad viaja ya calculada porque el polígono municipal completo no "
    f"viaja: son {ent(EX['poligonos']['vertices'])} vértices y {EX['poligonos']['mb']}&nbsp;MB, y "
    "simplificarlo para que pese menos podría cambiar los vecinos y, con ellos, la I. El bloque de R "
    "deja escrita, comentada, la línea que la calculó.") + tabs(
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
    """import geopandas as gpd
from shapely.geometry import box

ncp = gpd.read_file("entrega/datos/cap1_nc.gpkg").to_crs(2264)
x0, y0, x1, y1 = ncp.total_bounds
dx, dy = (x1 - x0) / 10, (y1 - y0) / 10
rej = gpd.GeoDataFrame(geometry=[
    box(x0 + i * dx, y0 + j * dy, x0 + (i + 1) * dx, y0 + (j + 1) * dy)
    for i in range(10) for j in range(10)], crs=ncp.crs)

# 1) El sjoin por "intersects" hace exactamente lo que aggregate() en R.
u = gpd.sjoin(ncp[["SID74", "geometry"]], rej, predicate="intersects")
print(f"condados = {int(ncp.SID74.sum())} | "
      f"rectangulos = {int(u.groupby('index_right').SID74.sum().sum())}")
#> """ + f"condados = {agn['total_condados']} | rectangulos = {agn['total_rectangulos']}" + """

# 2) Aqui el reparto se escribe a mano, con la regla del conteo de mas
#    arriba: peso = area del trozo / area del origen, por ser una
#    variable extensiva.
t = gpd.overlay(ncp[["SID74", "geometry"]].assign(a=ncp.geometry.area),
                rej, how="intersection")
print(f"repartido por area = {(t.SID74 * t.geometry.area / t.a).sum():.5f}")
#> """ + f"repartido por area = {n(agn['total_por_area'])}") + tabs(
    "La misma variable a dos escalas",
    """library(sf); library(spdep)

mun &lt;- st_read("entrega/datos/cap1_municipios.gpkg", quiet = TRUE)
# La vecindad de reina de todos, calculada sobre los poligonos completos
# (que no viajan) con
#   poly2nb(poligonos, queen = TRUE, row.names = divipola)
# Se lee emparejando por divipola, no por posicion.
reina &lt;- read.gal("entrega/datos/cap1_municipios_reina.gal",
                  region.id = mun$divipola)
ok &lt;- !is.na(mun$desercion)
nb &lt;- subset(reina, ok)      # solo los vecinos que tienen dato
I_mun &lt;- moran.test(mun$desercion[ok], nb2listw(nb, style = "W", zero.policy = TRUE),
                    zero.policy = TRUE)$estimate[["Moran I statistic"]]
cat(sprintf("municipal: n = %d, I = %.5f\\n", sum(ok), I_mun))
#&gt; """ + f"municipal: n = {es['n_municipal']}, I = {n(es['moran_municipal'])}" + """

# Islas y subgrafos: no son un defecto del dato, son el caso trabajado
# del modulo 9 del capitulo 6.
cat(sprintf("islas = %d, subgrafos = %d, grado medio = %.5f\\n",
            sum(card(nb) == 0), n.comp.nb(nb)$nc, mean(card(nb))))
#&gt; """ + f"islas = {es['islas_municipal']}, subgrafos = {es['subgrafos_municipal']}, "
    f"grado medio = {n(es['grado_municipal'])}",
    """import geopandas as gpd, numpy as np, libpysal
from libpysal.weights import w_subset

mun = gpd.read_file("entrega/datos/cap1_municipios.gpkg")
# La misma vecindad de reina; libpysal toma divipola como identificador.
reina = libpysal.io.open("entrega/datos/cap1_municipios_reina.gal").read()
ok = mun.loc[mun.desercion.notna(), "divipola"].tolist()
w = w_subset(reina, ok, silence_warnings=True)   # solo los que tienen dato
islas = [i for i, v in w.neighbors.items() if not v]
print(f"n = {len(ok)}, islas = {len(islas)}, "
      f"grado medio = {np.mean([len(v) for v in w.neighbors.values()]):.5f}")
#> """ + f"n = {es['n_municipal']}, islas = {es['islas_municipal']}, "
    f"grado medio = {n(es['grado_municipal'])}" + """

# Y la I con los pesos de libpysal, escrita a mano como en el modulo 3:
# estandarizada por filas (style = "W") y con n = los que tienen vecinos,
# el convenio de spdep con zero.policy = TRUE. Tiene que dar la del bloque
# de R. (Con los poligonos, libpysal.weights.Queen.from_dataframe() da
# esta misma vecindad, municipio a municipio.)
w.transform = "r"
z = mun.set_index("divipola").loc[ok, "desercion"].to_numpy()
z = z - z.mean()
W = w.sparse
n_con = len(ok) - len(islas)
print(f"I = {(n_con / W.sum()) * (z @ (W @ z)) / (z @ z):.5f}, la de spdep")
#> """ + f"I = {n(es['moran_municipal'])}, la de spdep") + CIERRE_FUENTES


# =====================================================================
# MÓDULO 8 · El ecosistema de R espacial
# =====================================================================
# R3 · T3.5 (H-07): «Prepara tu entorno». El syllabus pide en la semana 1 la
# «Instalación del entorno de trabajo en R», y el capítulo no traía ni un
# `install.packages`. Va en el módulo 8, y no en el 1, porque es el módulo de
# los paquetes y de la tabla de versiones a la que remite; el módulo 1 deja
# dicho, junto a su primer bloque, dónde está.
#
# Lo que el recuadro dice de las bibliotecas de sistema es SOLO lo que se leyó
# el 2026-11-23 en la documentación de sf (README de r-spatial/sf y su página
# de CRAN): que en Windows y macOS CRAN instala el binario, que para macOS pide
# `type = "binary"` si R intenta compilar, y que en Linux pide GDAL, GEOS y
# PROJ, con la orden de Ubuntu que se copia aquí. La activación del entorno de
# Python es la de la documentación de `venv`. Ver diagnostico_cap1/R3_T3.5_estado.md.
#
# Las listas de paquetes NO se escriben aquí: `completa_entorno()` las saca, en
# main(), de los library() y los import de los bloques ya ensamblados, y
# sustituye las marcas @@…@@. Un bloque que cargue un paquete nuevo lo añade
# solo a la orden de instalación.
R_HUMO = """library(HistData); library(sf); library(spatstat.geom)
library(spatstat.data); library(sp); library(spdep)

mun &lt;- st_read("entrega/datos/cap1_municipios.gpkg", quiet = TRUE)
cat(sprintf("%d municipios, EPSG:%d, %d con desercion\\n",
            nrow(mun), st_crs(mun)$epsg, sum(!is.na(mun$desercion))))
#&gt; """ + (f"{EX['municipios']['filas']} municipios, EPSG:{EX['municipios']['crs_epsg']}, "
          f"{EX['municipios']['n_desercion']} con desercion")
PY_HUMO = """import geopandas as gpd, shapely, pandas, numpy, scipy, libpysal

mun = gpd.read_file("entrega/datos/cap1_municipios.gpkg")
print(f"{len(mun)} municipios, EPSG:{mun.crs.to_epsg()}, "
      f"{mun.desercion.notna().sum()} con desercion")
#> """ + (f"{EX['municipios']['filas']} municipios, EPSG:{EX['municipios']['crs_epsg']}, "
        f"{EX['municipios']['n_desercion']} con desercion")
# R3 · T3.5, ronda 2. La licencia del extracto la decidió Javier el
# 2026-11-23: los archivos cap1_* se publican bajo CC BY-SA 4.0, con la
# atribución que el material ya usa (la frase del Taller 1 y procedencia.json).
# `guardas_de_t35()` exige esta frase, una vez, dentro del recuadro.
LICENCIA_EXTRACTO = "se publican bajo la licencia <strong>CC BY-SA 4.0</strong>"
# Corrección del mismo día: la CC BY-SA 4.0 es SOLO para lo que deriva de los
# datos del MEN, el ICFES y el DANE/geoBoundaries. Los cuatro archivos que
# salen de paquetes de R no se pueden relicenciar: van con la licencia de su
# paquete, el campo License de su DESCRIPTION, leído con packageDescription()
# el 2026-11-23 (HistData 1.0.0, spatstat.data 3.1.9, sp 2.2.0, sf 1.0.22).
# Qué permiten esas licencias sobre los datos no se ha leído y no se dice.
CC_EXTRACTO = ("cap1_municipios.gpkg", "cap1_municipios_reina.gal")
# R4 · T4.2 (A-148): el diccionario estaba escrito a mano. Ahora lo publica
# genera_cap1.R (`ecosistema.licencias_datos`), que le pregunta a cada paquete
# su campo License; aquí solo se le da forma.
LICENCIAS_PAQUETES = {
    l["archivo"]: (l["paquete"], html.escape(l["licencia"], quote=False))
    for l in D["ecosistema"]["licencias_datos"]
}
if sorted(LICENCIAS_PAQUETES) != ["cap1_japanesepines.csv", "cap1_meuse.csv", "cap1_nc.gpkg", "cap1_snow.csv"]:
    sys.exit("PARADO: `ecosistema.licencias_datos` no trae los cuatro archivos del extracto que salen de "
             "paquetes de R")
_lic_paq = [f"<code>{f}</code>, de <code>{p}</code> ({lic})" for f, (p, lic) in LICENCIAS_PAQUETES.items()]
LICENCIAS_PAQUETES_TXT = "; ".join(_lic_paq[:-1]) + "; y " + _lic_paq[-1]
# La orden que da la documentación de venv para PowerShell. Cada palabra va
# en un trozo que no se parte: el navegador cortaba en el guion de «-Scope»
# y en el teléfono se leía «- Scope». Copiada, sigue siendo la misma orden.
ORDEN_PS = " ".join(f'<span style="white-space:nowrap">{t}</span>' for t in
                    "Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser".split())
ENTORNO = f"""
      <div class="definition" id="prepara-tu-entorno">
        <h3>Prepara tu entorno</h3>
        <p>Para ejecutar los bloques del capítulo fuera de esta página hacen falta R, o Python, con los paquetes
          que usan los bloques, y los archivos de datos que leen. No hace falta instalar las versiones de la
          tabla de arriba: son las que calcularon el material, y sirven para saber con qué se obtuvo una cifra
          publicada si en otro equipo sale otra.</p>
        <p><strong>R.</strong> Estas líneas instalan los paquetes de los bloques con todo lo que necesitan. La
          primera guarda la lista en <code>paq</code>:</p>
        <pre><code class="language-r arranque">paq &lt;- c(@@PAQUETES_R@@)

# Windows y macOS:
install.packages(paq,
  type = "binary")

# Linux, despues de las
# bibliotecas de abajo:
install.packages(paq)</code></pre>
        <p><span data-afirma="c1-m8-08">En Windows y macOS, instalar <code>sf</code> desde CRAN trae el paquete ya
          compilado, salvo que R esté configurado para instalar desde el código fuente. Para macOS, su
          documentación recomienda vivamente el binario y, si R intenta compilar, pedirlo con
          <code>type = "binary"</code> <cite class="cita" data-ref="pebesma2016sf"></cite></span>.
          <span data-afirma="c1-m8-07">Instalado así, en binario, <code>sf</code> trae dentro una copia de las
          bibliotecas externas que necesita, con sus dependencias <cite class="cita" data-ref="pebesma2023spatial" data-loc="§1.7"></cite></span>:
          por eso ahí no hay que instalar nada más. En Linux, <code>sf</code> se compila al instalarlo y necesita antes unas bibliotecas del sistema.
          <span data-afirma="c1-m8-09">La página de <code>sf</code> en CRAN declara como requisitos GDAL, GEOS,
          PROJ y SQLite, y su documentación da para Ubuntu los paquetes <code>libudunits2-dev</code>,
          <code>libgdal-dev</code>, <code>libgeos-dev</code>, <code>libproj-dev</code> y
          <code>libsqlite3-dev</code> <cite class="cita" data-ref="pebesma2016sf"></cite></span>.
          <span data-afirma="c1-m8-10"><code>s2</code>, un paquete que <code>sf</code> usa, declara en CRAN cmake,
          OpenSSL y Abseil, y su README da para Debian y Ubuntu <code>libssl-dev</code> y <code>libabsl-dev</code>
          <cite class="cita" data-ref="dunnington2016s2"></cite></span>. Esta orden de Ubuntu reúne los nombres que
          dan las dos, y no se ha probado:</p>
        <pre><code class="language-bash">sudo apt install cmake \\
  libudunits2-dev \\
  libgdal-dev \\
  libgeos-dev \\
  libproj-dev \\
  libsqlite3-dev \\
  libssl-dev \\
  libabsl-dev</code></pre>
        <p><strong>Python.</strong> Un entorno virtual, que deja estos módulos aparte de los del sistema. Se crea
          una vez y se activa en cada sesión con la línea de tu sistema; dentro de él, <code>pip</code> instala
          los módulos que importan los bloques:</p>
        <pre><code class="language-bash">python -m venv geo

# macOS y Linux:
source geo/bin/activate
# Windows, cmd.exe:
geo\\Scripts\\activate.bat
# Windows, PowerShell:
geo\\Scripts\\Activate.ps1

@@ORDEN_PIP@@</code></pre>
        <p>En PowerShell, la documentación de <code>venv</code> advierte que puede hacer falta permitir antes el
          guion de activación, con <code>{ORDEN_PS}</code>. El lado de Windows no se ha probado.</p>
        <p><strong>Los datos.</strong> Cada módulo enlaza los archivos que leen sus bloques, junto al primero de
          ellos. Son estos, y el código los busca en <code>{CARPETA_DATOS}/</code>:</p>
        <ul>
@@LISTA_DATOS@@
        </ul>
        <p>Los dos archivos de los municipios, <code>cap1_municipios.gpkg</code> y
          <code>cap1_municipios_reina.gal</code>, {LICENCIA_EXTRACTO}, con la atribución de sus fuentes: la
          deserción y la cobertura neta son del <strong>Ministerio de Educación Nacional</strong> (CC BY-SA 4.0);
          los resultados de Saber 11, del <strong>ICFES</strong> (CC BY-SA 4.0); y los municipios,
          {ATRIB_DANE}. Los otros cuatro <code>cap1_*</code> salen de paquetes de R y se distribuyen con la
          licencia que declara el paquete del que salen: {LICENCIAS_PAQUETES_TXT}. Su origen está en la tabla de
          procedencia del módulo 12. Los dos <code>taller1_*</code> son los del Taller&nbsp;1, con la atribución
          que dan los módulos 3 y 10.</p>
        <p style="margin-bottom:0;"><strong>La prueba.</strong> Si este bloque corre y escribe lo mismo que su
          última línea, el entorno está listo.</p>
      </div>

""" + tabs("La prueba del entorno, en R y en Python", R_HUMO, PY_HUMO)

filas_paq = "\n".join(
    f"""          <tr><th scope="row"><code>{p['nombre']}</code></th><td>{p['papel']}</td>
            <td>{p['version']}</td></tr>""" for p in eco["paquetes"])

# R3 · T3.4 (H-02, D8): los módulos 8 y 9 son herramientas entre la escala
# (7) y la validación cruzada (10). No se renumeran; ganan una entrada que dice
# por qué están aquí —ya se han usado, y aquí se ve por qué funcionan como
# funcionan— y el 10 una que vuelve al hilo de la dependencia.
# R4 · T4.2 (A-144): qué paquete necesita `sf` lo dice el DESCRIPTION de cada
# uno, leído en R (`ecosistema.necesitan_sf`). La frase decía cinco y son
# seis: faltaba spatialreg. Lo que la prosa añade —que spatstat trae su
# propio objeto— exige que spatstat esté entre los que no lo necesitan.
if "spatstat" not in eco["sin_sf"] or not eco["necesitan_sf"]:
    sys.exit("PARADO: el módulo 8 dice que spatstat va por su cuenta y que otros paquetes necesitan sf; "
             "`ecosistema` ya no lo sostiene")
_NECESITAN_SF = _une([f"<code>{p}</code>" for p in eco["necesitan_sf"]])
_SIN_SF = _une([f"<code>{p}</code>" for p in eco["sin_sf"]])
MOD8 = cabecera(
    8, "El ecosistema de R espacial", "The R-spatial stack",
    "Saber qué paquete resuelve qué pregunta, y por qué el mapa de "
    "paquetes es el mapa de los tres tipos de dato.") + f"""
      <p>Los módulos anteriores midieron con R, y con Python al lado, y por el camino aparecieron
        <code>sf</code>, <code>spdep</code>, <code>spatstat</code> y <code>classInt</code> sin que se dijera qué
        hace cada uno. Este módulo y el siguiente se detienen en las herramientas, ahora que ya se han usado: qué
        paquete resuelve qué pregunta, qué hay dentro de <code>sf</code> y por qué dos programas
        pueden dar dos cifras distintas sobre el mismo dato, que ya asomó en el módulo 3. El módulo 10 vuelve
        después a la dependencia.</p>

      <p>El ecosistema parece caótico hasta que se ordena <strong>por tipo de dato</strong>, que es como lo
        ordena este curso: <code>spatstat</code> para patrones puntuales, <code>spdep</code> para datos de área,
        <code>gstat</code> para geoestadística. <span data-afirma="c1-m8-01">Son los mismos tres grupos en que
        <cite class="cita" data-ref="pebesma2023spatial" data-loc="§10.2" data-modo="narrativa"></cite> reparten sus capítulos
        de métodos: unos para los patrones puntuales, otros para los datos geoestadísticos y otros para los
        datos de área</span>. Muchos paquetes
        se apoyan en <code>sf</code>, que es quien sabe leer y proyectar la geometría vectorial: de los de la
        tabla de abajo, {_NECESITAN_SF} lo declaran entre los paquetes que necesitan para funcionar.
        {_SIN_SF} no: van por su cuenta, y <code>spatstat</code> trae su propio objeto.</p>

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

      <p data-afirma="c1-m8-06">Para ir de la tabla al libro: en <cite class="cita" data-ref="pebesma2023spatial" data-loc="§7.1; §7.4; §8.2; §8.5" data-modo="narrativa"></cite>
        están, por ese orden, <code>sf</code>, <code>stars</code>, los cortes de clase de <code>classInt</code>
        y <code>tmap</code>.</p>

      <div class="definition">
        <h3>Las bibliotecas de sistema, que son la parte que de verdad importa</h3>
        <p>Por debajo de <code>sf</code> —y, a través de él, de los paquetes que se apoyan en él— hay
          bibliotecas de sistema que hacen el trabajo pesado. <span data-afirma="c1-m8-02">Están escritas en C
          o en C++ y no son de R: las desarrollan, las mantienen y las usan comunidades grandes y en su mayoría distintas de la de R.
          La lista completa es más larga que la de aquí; trae también s2geometry, de la que se habla abajo,
          y otras como liblwgeom, NetCDF y udunits2 <cite class="cita" data-ref="pebesma2023spatial" data-loc="§1.7"></cite></span>.
          <code>terra</code>, que no pasa por <code>sf</code>, enlaza por su cuenta las tres de abajo:
          <code>terra::gdal(lib = "all")</code> las lista. Son las que este capítulo ve trabajar, con la
          versión con la que se calculó:</p>
        <ul>
          <li><strong>GDAL {eco['sistema']['GDAL']}</strong> — leer y escribir formatos. Todos: shapefile,
            GeoPackage, GeoJSON, ráster. <span data-afirma="c1-m8-03">Fuera de R la usan Python, QGIS, PostGIS
            y más de un centenar de proyectos <cite class="cita" data-ref="pebesma2023spatial" data-loc="§1.7"></cite></span>.</li>
          <li><strong>GEOS {eco['sistema']['GEOS']}</strong> — las operaciones geométricas en el plano: medir
            una longitud, un área o una distancia; contestar un predicado, como si dos geometrías se tocan; y
            construir una geometría nueva, como una intersección.</li>
          <li><strong>PROJ {eco['sistema']['PROJ']}</strong> — las transformaciones entre sistemas de referencia.
            Es el capítulo 2 entero.</li>
        </ul>
        <p><span data-afirma="c1-m8-04">El reparto de papeles —GDAL lee y escribe, GEOS mide y opera en el
          plano, PROJ convierte coordenadas de un sistema de referencia a otro— es el que describen
          <cite class="cita" data-ref="pebesma2023spatial" data-loc="§1.7" data-modo="narrativa"></cite></span>.</p>
        <p><strong>¿Llaman R y Python a la misma biblioteca? Depende de las coordenadas.</strong>
          <span data-afirma="c1-m8-05">Con coordenadas proyectadas, <code>sf</code> hace las operaciones
          geométricas con GEOS. Con coordenadas elipsoidales —longitud y latitud— las hace, si no se le pide
          otra cosa, con s2geometry, que trabaja sobre la esfera
          <cite class="cita" data-ref="pebesma2023spatial" data-loc="§7.1; §7.3"></cite></span>. GeoPandas opera con
          <code>shapely</code>, que es GEOS: opera siempre sobre el plano. Así que R y Python llaman a la misma
          biblioteca para leer y escribir, para proyectar, y para la geometría <em>mientras el dato esté
          proyectado</em>. Es el caso de los bloques de este capítulo que intersecan y reparten: los del módulo
          7 proyectan antes los condados de Carolina del Norte, así que las dos pestañas operan sobre el mismo plano y con la misma biblioteca. Con
          el dato en longitud y latitud, <code>sf</code> opera sobre la esfera y GeoPandas sobre el plano, y
          una misma área o una misma intersección pueden no coincidir.</p>
        <p style="margin-bottom:0;">Los desacuerdos entre R y Python que este material declara —los
          cuantiles del capítulo 3 y, en el módulo 9, el tipo de geometría y la I de Moran— no vienen de ahí: están en la capa de arriba,
          no en la geometría.</p>
      </div>

      <div class="note">
        <p style="margin-bottom:0;"><strong>Este material se calculó con {eco['r_version']}</strong>, y las versiones
          de la tabla están congeladas en <code>precalculo/versiones.json</code>. No es burocracia: lo que devuelve
          una función puede cambiar de una versión a otra —un valor por defecto, un convenio como el de las
          unidades sin vecinos—, y un material que no dice con qué se hizo no es reproducible.</p>
      </div>
""" + ENTORNO + CIERRE_FUENTES


# =====================================================================
# MÓDULO 9 · Anatomía de un objeto sf
# =====================================================================
disc_nc = next(d for d in D["discrepancias"] if d["id"] == "tipo_geometria_nc")
disc_mor = next(d for d in D["discrepancias"] if d["id"] == "moran_islas")
# R3 · T3.4 (D7): la nota final decía «El auditor de este capítulo lleva una
# lista de las diferencias conocidas entre R y Python; si encuentra una que
# está en la lista, la trata como material didáctico, y si encuentra una que
# no está, falla». Sigue siendo así —`D["discrepancias"]` y audita_cap1.py—,
# pero es cómo se produce el material. Al estudiante se le dice el método:
# quien compara dos programas lleva esa lista, y lo que no está en ella es un
# error hasta que se explique. La retroalimentación del quiz (módulo 9) dice
# lo mismo; el texto de la OPCIÓN («si el material las publica») es de R5.
MOD9 = cabecera(
    9, "Anatomía de un objeto sf", "Inside an sf object",
    "Abrir el objeto por dentro: geometría y atributos en la misma tabla, "
    "las tres clases anidadas, y lo que cuesta cada una.") + f"""
      <p><code>sf</code> es el objeto sobre el que trabajan <code>spdep</code>, <code>gstat</code> y
        <code>tmap</code>; <code>spatstat</code> lleva el suyo, el <code>ppp</code>. Este módulo abre el primero
        por dentro y lo compara con el segundo, que guarda además la ventana.</p>

      <p><span data-afirma="c1-m9-01">Un objeto <code>sf</code> es un <code>data.frame</code> —o un
        <code>tibble</code>— con al menos una columna rara: una columna-lista que guarda la geometría de cada fila
        <cite class="cita" data-ref="pebesma2023spatial" data-loc="§7.1"></cite></span>. El resto es una tabla normal, con lo cual
        todo lo que ya sabes de <code>dplyr</code> sigue valiendo. <span data-afirma="c1-m9-02">Y no es un
        accidente: <code>sf</code> se hizo para suceder y reemplazar a <code>sp</code>, con tres propósitos
        declarados. Acercar el análisis espacial en R a los estándares, apoyarlo en versiones más modernas de
        las bibliotecas de código abierto, y permitir que se integre con el tidyverse
        <cite class="cita" data-ref="pebesma2023spatial" data-loc="§7.1"></cite></span>.</p>

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
        <p data-afirma="c1-m9-03">La anidación es la del paquete: un objeto <code>sf</code> lleva al menos una
          columna-lista de clase <code>sfc</code>, cada elemento de esa columna es un <code>sfg</code>, y el
          sistema de referencia es un atributo de la columna
          <cite class="cita" data-ref="pebesma2023spatial" data-loc="§7.1"></cite>.</p>
        <p style="margin-bottom:0;">Y el <code>ppp</code> de <code>spatstat</code> es otra cosa: los
          {an['ppp']['n']} pinos japoneses ocupan {ent(an['ppp']['bytes'])} bytes e incluyen
          <strong>la ventana de observación</strong> ({an['ppp']['ventana_tipo']}, área
          {n(an['ppp']['ventana_area'])}). <span data-afirma="c1-m9-04">Un patrón puntual tiene ventana de
          observación, y un <code>ppp</code> es eso: los puntos y su ventana. Si se crea desde unos puntos sin
          decir cuál es, se toma su caja <cite class="cita" data-ref="pebesma2023spatial" data-loc="§11.1"></cite></span>.
          Un <code>sf</code> de puntos no sabe cuál es su ventana, y para un patrón
          puntual la ventana es parte del dato — el módulo 2 ya midió lo que cuesta olvidarla.</p>
      </div>

""" + nota_datos(
    f"La pestaña de Python lee {enlace_datos('nc')}, el del módulo 2; la de R, el <code>nc.shp</code> que "
    "trae <code>sf</code>.", varios=False) + tabs(
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
    """import geopandas as gpd

nc = gpd.read_file("entrega/datos/cap1_nc.gpkg")
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
        <p style="margin-bottom:0;"><strong>Las discrepancias se declaran o son errores.</strong> Comparar dos
          programas exige llevar la lista de las diferencias conocidas, cada una con su causa, como las dos de
          arriba. Una diferencia que está en la lista es material para entender los dos programas; una que no
          está es <strong>un error hasta que se explique</strong>. Que una discrepancia documentada y una sin
          explicar se lean igual sobre un informe es lo que convierte una comparación en un adorno.</p>
      </div>
""" + CIERRE_FUENTES


# =====================================================================
# MÓDULO 10 · Dependencia espacial en ciencia de datos
# =====================================================================
# Decisión de Javier del 2026-08-04: aquí se MIDE un caso pequeño y el
# desarrollo se remite al capítulo 10. La frontera está declarada dentro
# del propio JSON (`cv_espacial.frontera`), no solo en el plan, para que no
# se pierda al retomar.
# R4 · T4.2 (A-103): «la Amazonía y la Orinoquía, que son enormes, bajas y
# calientes» era geografía sin cifra. `diseno_modelo.mayores` la mide: las
# estaciones con la celda de Thiessen mayor. La prosa dice que están más
# bajas y más calientes que la red, y se para si deja de ser verdad.
my = dm["mayores"]
# Ronda 3 (V1): «deja casi vacías las bajas» era falso. Lo que la prosa dice
# ahora —que las estaciones de abajo son pocas para lo que cubren— sale de
# `diseno_modelo.bajas`, y se para si deja de ser verdad.
bj = dm["bajas"]
if not (bj["pct_area"] > bj["pct_red"] and bj["razon_territorio"] > 1 and 0 < bj["n"] < dm["n"]):
    sys.exit("PARADO: el módulo 10 dice que las estaciones bajas son pocas para el territorio que "
             "representan; `diseno_modelo.bajas` ya no lo sostiene")
if not (my["alt_media"] < dm["alt_media_area"] < dm["alt_media_simple"]
        and my["t_media"] > dm["t_media_area"] > dm["t_media_simple"] and my["pct_area"] > 25):
    sys.exit("PARADO: el módulo 10 dice que las estaciones con más territorio son bajas y calientes y "
             "representan buena parte del país; `diseno_modelo.mayores` ya no lo sostiene")
MOD10 = cabecera(
    10, "Dependencia espacial en ciencia de datos", "Spatial leakage",
    "Ver por qué un modelo predictivo con datos espaciales parece mejor de "
    "lo que es, y por qué con esta red de estaciones no queda más remedio "
    "que modelar. Las dos diferencias, medidas sobre dato real.") + f"""
      <p>Con las herramientas a la vista, el capítulo vuelve a la dependencia para medir una consecuencia que no está
        en un intervalo sino en la evaluación de una predicción. El módulo 4 midió cuánto se engaña un intervalo cuando las observaciones
        vecinas se parecen; este mide cuánto se engaña la evaluación de un modelo por la misma razón, y después qué
        marco de inferencia queda cuando la red de estaciones no salió de un sorteo.</p>

      <p>Este módulo es para quien vaya a usar aprendizaje automático con datos que tienen coordenadas, que hoy es
        casi todo el mundo. La conclusión es incómoda: <strong>la validación cruzada aleatoria puede mentir</strong>,
        y cuando miente lo hace hacia arriba. <span data-afirma="c1-m10-01">No es un defecto de ningún programa:
        esa validación supone observaciones independientes, que con datos espaciales a menudo no es un supuesto
        razonable, y sus cifras pueden pecar de optimistas cuando se toman como medida de lo bien que se
        predice en el espacio <cite class="cita" data-ref="pebesma2023spatial" data-loc="§10.1; §10.5"></cite></span>. «Puede» no es
        cortesía: cuánto miente depende del dato y de para qué se quiera el modelo, y aquí se mide en un
        caso.</p>

      <p>El experimento, con las {cv['n']} estaciones del IDEAM: predecir la {cv['variable']} de cada estación a
        partir de sus {cv['k_vecinos']} vecinas más próximas, y evaluar con {cv['n_pliegues']} pliegues de dos
        maneras: repartiendo las estaciones <em>al azar</em>, y repartiéndolas <em>por bloques espaciales</em>.</p>

      <div class="simulador" data-simulador="cv-espacial">
        <h4><i class="fas fa-scissors" aria-hidden="true"></i> Validación cruzada aleatoria contra por bloques</h4>
        <p class="simulador-intro">Mismo modelo, mismo dato y el mismo número de pliegues, {cv['n_pliegues']}. Lo
          único que cambia es cómo se reparten las estaciones entre ellos —al azar, o en bloques de estaciones
          cercanas—, y los dos mapas de debajo lo enseñan: cada estación lleva el color de su
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
          lo que suele querer usarse. Aquí se toma como una forma de validación cruzada espacial.
          <span data-afirma="c1-m10-02">De las validaciones adaptadas, como la validación cruzada espacial, se
          dice que pueden dar medidas más pertinentes de lo que acierta una predicción
          <cite class="cita" data-ref="pebesma2023spatial" data-loc="§10.5"></cite></span>.</p>
      </div>

      <div class="warning">
        <p style="margin-bottom:0;"><strong>Y la advertencia simétrica, que también hay que dar.</strong> La
          validación por bloques no es «la buena» siempre: es la que responde a la pregunta <em>«¿cuánto me fío en
          una zona donde no he medido?»</em>. Si la pregunta fuera <em>«¿cuánto me fío en sitios que se parecen a
          los de la muestra, como los huecos entre estaciones que ya existen?»</em>, la aleatoria es la que más
          se le acerca. Esa respuesta tiene respaldo, pero en un caso que no es el de esta red.
          <span data-afirma="c1-m10-03">Cuando la muestra se sorteó sobre la zona, suponer que las observaciones
          son independientes puede estar justificado, y el marco del diseño permite predecir el valor de un
          sitio nuevo elegido también al azar <cite class="cita" data-ref="pebesma2023spatial" data-loc="§10.5"></cite></span>. Elegir el reparto es declarar a qué pregunta
          se responde, y hacerlo por defecto es responder a la que no era.</p>
      </div>

      <p>Esa advertencia tiene nombre, y conviene ponérselo porque debajo no hay una preferencia de método sino
        <strong>dos marcos de inferencia distintos</strong>, el basado en el diseño y el basado en el
        modelo:</p>

      <div class="definition">
        <h3>Basado en el diseño y basado en el modelo</h3>
        <ul>
          <li><strong>Basado en el diseño:</strong> <span data-afirma="c1-m10-04">lo aleatorio es <em>el
            muestreo</em>. Exige que el dato venga de un muestreo probabilístico, con probabilidades de inclusión
            conocidas y positivas. A cambio no hace falta postular ningún modelo: con esas probabilidades basta
            para estimar medias con su error estándar, y con una muestra aleatoria simple la media poblacional
            se estima con la media muestral sin ponderar
            <cite class="cita" data-ref="pebesma2023spatial" data-loc="§10.4"></cite></span>. Cuando las probabilidades no son
            iguales, cada observación entra con un peso. <span data-afirma="c1-m10-05">En el estimador de
            Horvitz–Thompson cada elemento de la muestra se pesa por el inverso de su probabilidad de muestreo
            <cite class="cita" data-ref="baddeley2015spatial" data-loc="p. 181"></cite></span>. Para la media, se suma cada
            observación dividida por su probabilidad de inclusión y esa suma se divide por el tamaño de la
            población, no por la suma de los pesos.
            Es insesgado, y se ve sin fórmulas: cada unidad de la población entra en la muestra con su
            probabilidad de inclusión y, cuando entra, pesa el inverso de esa probabilidad, así que en promedio
            sobre todos los sorteos aporta su valor exactamente una vez. La media muestral sin ponderar, en
            general, solo es insesgada cuando todas las probabilidades son iguales; si no lo son, se
            sesga hacia lo que el diseño sobrerrepresenta.
            <span data-afirma="c1-m10-06">Y algo que sorprende: en un muestreo aleatorio simple,
            dos extracciones distintas son (casi) incorreladas aunque el campo de debajo sea suave, porque lo que
            se repite al imaginar otra muestra no son ellas sino los sorteos. Creer que dos observaciones cercanas están siempre correlacionadas es un malentendido:
            eso solo pasa cuando se trabaja en el marco del modelo
            <cite class="cita" data-ref="pebesma2023spatial" data-loc="§10.4"></cite></span>. Es una propiedad de ese diseño y no
            de todos: si lo que se sortea son conglomerados de sitios vecinos, dos extracciones del mismo
            conglomerado sí están correlacionadas, porque caen siempre juntas: salga el conglomerado que salga,
            las dos están una al lado de la otra, y sobre un campo suave cuando una es alta la otra también.</li>
          <li><strong>Basado en el modelo:</strong> <span data-afirma="c1-m10-07">lo aleatorio es <em>el
            proceso</em>. Se supone que lo observado es una realización de \\(Z(s)\\) y se postula su estructura
            de covarianza. No exige saber cómo se eligieron las localizaciones, y a cambio todo lo que se
            concluye depende de que el modelo postulado valga
            <cite class="cita" data-ref="pebesma2023spatial" data-loc="§10.4"></cite></span>. <span data-afirma="c1-m10-08">Es el
            que hace falta para predecir en un punto concreto, o cuando el dato no salió de un sorteo: el marco
            del diseño da promedios de áreas, no interpolaciones
            <cite class="cita" data-ref="pebesma2023spatial" data-loc="§10.5"></cite></span>.</li>
        </ul>
        <p style="margin-bottom:0;"><span data-afirma="c1-m10-09">Las dos situaciones pueden darse a la vez sin
          contradicción: son consecuencia del marco en que se elige trabajar, y cuál se elige depende del
          propósito del estudio y de cómo se recogió el dato
          <cite class="cita" data-ref="pebesma2023spatial" data-loc="§10.4"></cite></span>. Responden a preguntas distintas, y lo
          que no se puede es usar uno y reclamar las garantías del otro. Que no compitan es una manera de verlo, no un acuerdo cerrado.
          <span data-afirma="c1-m10-10">Entre los métodos de inferencia basados en el modelo y los basados en
          el diseño hay una controversia en la teoría clásica del muestreo
          <cite class="cita" data-ref="cressie1993statistics" data-loc="p. 52"></cite></span>.</p>
      </div>

      <p>Y aquí está lo que decide cuál te toca, que no es una preferencia: <strong>la red del IDEAM no trae
        probabilidades de inclusión</strong>. El dato no dice que las estaciones se sortearan, y lo que se mide
        a continuación es que su reparto no se parece al de un sorteo de igual probabilidad. Por qué está cada
        estación donde está, este dato no lo cuenta, y el capítulo no lo supone. Sin probabilidades de
        inclusión, el marco basado en el diseño sencillamente no está disponible. Se puede medir lo que eso cuesta. Reparte
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
        representan está a <strong>{n(dm['alt_media_area'])}</strong> m: la red sobremuestrea las tierras altas. Abajo hay estaciones, pero
        pocas para lo que cubren: las {ent(bj['n'])} que están por debajo de {ent(bj['umbral_m'])} m son el
        <strong>{n(bj['pct_red'])}&nbsp;%</strong> de la red y representan el
        <strong>{n(bj['pct_area'])}&nbsp;%</strong> del territorio. A cada una le toca, de media,
        {n(bj['razon_territorio'])} veces el territorio de una de las de arriba. Y el reparto es más desigual
        todavía en el extremo: las {my['k']} estaciones con las celdas mayores —están en
        {_une(my['departamentos'])}— representan ellas solas el <strong>{n(my['pct_area'])}&nbsp;%</strong> del territorio, y están a
        {n(my['alt_media'])} m y {n(my['t_media'])}&nbsp;°C de media; ninguna pasa de {ent(my['alt_max'])} m.
        Promediar las
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

""" + nota_datos(
    f"Los dos bloques leen {enlace_datos('estaciones')}, el del módulo 3, y los departamentos del "
    f"Taller&nbsp;1, {enlace_datos('departamentos')}, para recortar las celdas al contorno del país. Los "
    f"departamentos son datos de terceros que se redistribuyen con atribución: son {ATRIB_DANE}.") + tabs(
    "Pesar cada estación por el territorio que representa",
    """library(sf)

estac &lt;- st_read("entrega/datos/taller1_estaciones.gpkg", quiet = TRUE)
pais  &lt;- st_union(st_read("entrega/datos/taller1_departamentos.gpkg", quiet = TRUE))

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

estac = gpd.read_file("entrega/datos/taller1_estaciones.gpkg")
pais = gpd.read_file("entrega/datos/taller1_departamentos.gpkg").geometry.union_all()

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
    f"brecha = {n(dm['brecha_c'])}") + CIERRE_FUENTES


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
        <p>Las columnas <em>Texto guía</em> y <em>En R</em> están para que puedas ir del
          material al libro y del libro al código sin traducir de cabeza. Donde dice «—», la fila todavía no remite
          al libro, o el capítulo no ejecuta ninguna función para ese símbolo.</p>
        <p style="margin-bottom:0;">No tienen fila las letras que una deducción define en el mismo sitio donde
          las usa —un \\(m\\), un \\(k\\), el \\(t\\) del movimiento browniano— ni las de cualquier curso de
          estadística, como \\(\\alpha\\), \\(p\\) o \\(H_0\\). Si un símbolo del curso no está aquí, es un
          descuido: dilo.</p>
      </div>

      <div class="references">
        <h3><i class="fas fa-book-open mr-2" aria-hidden="true"></i>A qué remite la columna «Texto guía»</h3>
        <p>La columna da el apellido y la sección. Estas son las obras y lo que cada sección trae; todas se
          leyeron para escribir la tabla.</p>
        <ul style="margin-bottom:0;">
          <li data-afirma="c1-m11-01"><cite class="cita" data-ref="cressie1993statistics" data-loc="§1.1" data-modo="narrativa"></cite>: la localización
            \\(s\\), el conjunto \\(D\\) sobre el que varía y el proceso \\(Z(s)\\), que es el modelo general
            del libro.</li>
          <li><span data-afirma="c1-m11-02"><cite class="cita" data-ref="cressie1993statistics" data-loc="§1.3" data-modo="narrativa"></cite>: el número
            equivalente de observaciones independientes, que aquí se escribe \\(n_{{\\text{{eff}}}}\\)</span>.
            El nombre «efecto de diseño» para \\(n/n_{{\\text{{eff}}}}\\), que la tabla da en la misma fila, no
            es de esa sección: lo pone este capítulo en el módulo 4.</li>
          <li data-afirma="c1-m11-03"><cite class="cita" data-ref="cressie1993statistics" data-loc="§2.3" data-modo="narrativa"></cite>: la covarianza
            estacionaria \\(C(h)\\), o covariograma.</li>
          <li data-afirma="c1-m11-04"><cite class="cita" data-ref="cressie1993statistics" data-loc="§2.3.1" data-modo="narrativa"></cite>: el
            variograma, que depende solo del incremento entre dos localizaciones —la \\(h\\) de la tabla—, y
            su mitad, el semivariograma \\(\\gamma(h)\\).</li>
          <li data-afirma="c1-m11-05"><cite class="cita" data-ref="baddeley2015spatial" data-loc="§6.2" data-modo="narrativa"></cite>: la intensidad
            \\(\\lambda\\), los puntos esperados por unidad de área, y cómo se estima.</li>
          <li data-afirma="c1-m11-06"><cite class="cita" data-ref="baddeley2015spatial" data-loc="§8.2" data-modo="narrativa"></cite>: las distancias
            al vecino más próximo y el índice de Clark-Evans.</li>
          <li data-afirma="c1-m11-07"><cite class="cita" data-ref="moraga2019geospatial" data-loc="§5.1" data-modo="narrativa"></cite>: la matriz
            de vecindad y sus elementos \\(w_{{ij}}\\), que conectan las áreas y se pueden leer como
            pesos.</li>
          <li data-afirma="c1-m11-08"><cite class="cita" data-ref="pebesma2023spatial" data-loc="§15.1" data-modo="narrativa"></cite>: la fórmula de
            la I de Moran y su prueba.</li>
          <li data-afirma="c1-m11-09"><cite class="cita" data-ref="pebesma2023spatial" data-loc="§15.3" data-modo="narrativa"></cite>: el estadístico
            local de Getis-Ord y su forma \\(G_i^*\\).</li>
          <li data-afirma="c1-m11-10"><cite class="cita" data-ref="pebesma2023spatial" data-loc="§17.1" data-modo="narrativa"></cite>: el modelo de
            rezago espacial y su coeficiente, que allí se escribe con un subíndice.</li>
        </ul>
      </div>
""" + CIERRE_FUENTES


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
# R3 · T3.5 (D9): los ejercicios 2 y 4 leen el archivo de municipios del
# capítulo, y lo enlazan igual que el 3. Hasta aquí el 2 decía «Con
# carga_municipios()» y el 4 no decía de dónde sacar el dato.


def datos_ejercicio(sol, que):
    f = next(v for v in EX.values() if isinstance(v, dict) and v.get("ruta") == sol["archivo"])
    return f"""          <p class="text-sm" style="margin:0.25rem 0 0.5rem;"><a href="../{sol['archivo']}" download target="_blank" rel="noopener">
            Descargar <code>{f['archivo']}</code></a> ({tam_archivo(f)}) — {que} La ruta
            <code>{sol['archivo']}</code> se cambia por la del lugar donde se haya guardado.</p>
"""


E2_DATOS = datos_ejercicio(S["e2"]["solucion"], "el archivo de municipios de los módulos 4 y 7.")
E4_DATOS = datos_ejercicio(S["e4"]["solucion"], "el mismo del ejercicio 2.")
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

# R3 · T3.1 (H-01): el arco. El módulo 1 abre con la tesis del curso —qué se
# rompe cuando una observación sí dice algo de la siguiente, cuánto y qué se
# hace— y el capítulo acababa sin volver a ella. La síntesis va AQUÍ, al
# empezar el módulo 12 y antes de la autoevaluación, y no al final del 10:
#   · reúne cifras de los módulos 4 a 10, no solo del 10, y el 10 ya cierra
#     con su propia frontera (el capítulo 10) y un bloque de código;
#   · entre el 10 y el 12 está el glosario, que cortaría el cierre en dos;
#   · leída antes del cuestionario hace de repaso: el estudiante llega a las
#     preguntas con las cifras del capítulo juntas.
# Ronda 2: el error estándar por bloques se queda corto SI los departamentos
# vecinos se parecen (la condición del m4); los 13 pares son correlaciones de
# Pearson, no I; los pliegues son el mismo número, no los mismos.
# Cada cifra es un campo del JSON, interpolada igual que en su módulo y dicha
# con su referencia: la cobertura de phi = 4 (no un «porcentaje de error»), el
# factor del error estándar real sobre el que calcula el programa, la t de una
# muestra bilateral con alfa, el factor de bloques sobre municipios sueltos, el
# RMSE por bloques frente al de la aleatoria con el mismo número de pliegues
# (10) y otro reparto: genera_cap1.R sortea uno al azar (SEMILLA + 500) y
# saca el otro de k-medias sobre las coordenadas (SEMILLA + 501). No son los
# mismos pliegues, y la prosa no lo dice (ronda 2, V-12).
#   · La caída de la I al agregar va con la advertencia del módulo 7: ese
#     porcentaje describe dos cifras con pesos y n distintos y NO mide cuánta
#     autocorrelación se pierde, y agregar no tiene dirección fija (n_suben y
#     n_bajan de los 13 pares). Una síntesis que dijera «agregar baja la I»
#     contradiría la lección del módulo.
#   · Snow entra por lo que el módulo 1 sí argumenta: la prueba de
#     aleatorización del capítulo —no de Snow, que no hizo ninguna—
#     recolocaba cada muerte por separado, como si fueran independientes, y
#     esa es UNA de las razones para leer su p como cota; la otra, que el m1
#     da primero, es la resolución de Monte Carlo, 1/(B+1). NO se dice que las muertes «no son localizaciones
#     independientes»: un racimo alrededor de una bomba lo explica igual una
#     intensidad que cae con la distancia (primer orden), con puntos
#     independientes. Confundirlo es enseñar al revés el capítulo 4.
#   · Ningún capítulo posterior se nombra: las promesas a los caps. 8-10 son
#     de otra tarea (H-15, H-16).
MOD12 = cabecera(
    12, "Autoevaluación y ejercicios guiados", "Self-assessment",
    "Comprobar que lo del capítulo se sostiene sin mirar, y resolver cuatro "
    "problemas con la solución calculada en R.") + f"""
      <div class="definition">
        <h3>La pregunta del módulo 1, con las cifras del capítulo</h3>
        <p>El capítulo empezó con una pregunta: qué se rompe cuando una observación sí dice algo de la siguiente,
          cuánto se rompe y qué se hace entonces. En la media, lo que se rompe es la confianza y no la estimación.
          Con \\(\\phi = {r4['phi']}\\), el intervalo al {NIVEL4}&nbsp;% que trata las {D['inferencia']['n']} celdas como
          independientes tiene una cobertura de <strong>{n(r4['cobertura'])}</strong>, porque el error estándar real
          de la media es <strong>{n(r4['factor'])} veces</strong> el que calcula el programa (módulo 4). La prueba
          \\(t\\) de ese mismo análisis, bilateral, con \\(\\alpha = {D['inferencia']['alfa']}\\), rechaza
          \\(H_0\\!: \\mu = {ur['media_del_proceso']}\\) en el <strong>{n(ur['pct_rechaza_ingenuo'])}&nbsp;%</strong>
          de {ent(ur['n_realizaciones'])} realizaciones de un proceso de media {ur['media_del_proceso']}, cuando
          debería hacerlo en el {n(ur['pct_esperado_si_valiera'])}&nbsp;% (módulo 6). Con el dato real pasa lo mismo.
          En la deserción de los {ent(ne['desercion_n'])} municipios, el error estándar que conserva la dependencia
          dentro de cada departamento es <strong>{n(ir['factor'])} veces</strong> el de remuestrear municipios
          sueltos; y si los departamentos vecinos se parecen, aun ese se queda corto, porque supone que un
          departamento no dice nada del de al lado (módulo 4). Para la media, esos municipios informan como el
          <strong>{n(ne['desercion_pct'])}&nbsp;%</strong> de los que son, una cifra que con
          {ent(ir['n_departamentos'])} departamentos vale por su orden de magnitud y no por sus decimales (módulos 4
          y 5).</p>
        <p>Se rompe también la evaluación de un modelo. Con el mismo modelo y el mismo número de pliegues,
          {cv['n_pliegues']}, repartidos por bloques espaciales y no al azar, el RMSE de la validación es un
          <strong>{n(cv['inflacion_pct'])}&nbsp;%</strong> mayor que el que anuncia la aleatoria, y es el que
          responde a cuánto fiarse en una zona sin medir (módulo 10). Y la propia medida de la dependencia depende
          de la unidad. La I de Moran de la deserción es {n(es['moran_municipal'])} entre municipios y
          {n(es['moran_departamental'])} entre departamentos, un {n(es['caida_pct'])}&nbsp;% menor, pero ese
          porcentaje no mide cuánta autocorrelación se pierde, porque cada I usa su matriz de pesos y su
          \\(n\\). Y agregar no tiene una dirección fija ni siquiera para la correlación entre dos variables: de
          los {ec['n_pares']} pares de variables del módulo 7, la correlación de Pearson entre las dos se aleja del
          cero en {ec['n_suben']} y se acerca en {ec['n_bajan']}.</p>
        <p style="margin-bottom:0;">Lo que se hace entonces, el capítulo lo deja en su primer paso: remuestrear
          bloques en vez de unidades sueltas, contar el tamaño efectivo, suponer un proceso estacionario y ergódico
          y medirlo en una región grande frente a su alcance, declarar la unidad y la regla de agregación, y elegir
          la validación según la pregunta. Son primeros pasos, no un modelo de la dependencia. Hasta la prueba de
          aleatorización del módulo 1, sobre el mapa de Snow, recolocaba cada muerte por separado, como si fueran
          independientes entre sí, y esa es una de las razones para leer su valor p como una cota.</p>
      </div>

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
{ejercicio(1, S['e1'])}{ejercicio(2, S['e2'], datos=E2_DATOS)}{ejercicio(3, S['e3'], datos=E3_DATOS, codigo=E3_CODIGO)}{ejercicio(4, S['e4'], datos=E4_DATOS)}
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
              <td>John Snow; digitalizado por <strong>Dodson</strong> (NCGIA, 1992) y tomado de
                <strong>Tobler</strong> (1994)</td>
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
        <p>La columna «Origen» de los conjuntos clásicos repite lo que dice de cada uno la ayuda del paquete
          que lo distribuye; lo que se pudo leer además en los libros va con su cita.
          <span data-afirma="c1-m12-10">Según la ayuda de <code>HistData</code>
          <cite class="cita" data-ref="friendly2009histdata"></cite>, el plano de Snow lo digitalizó Dodson en 1992, y el
          paquete da como fuente a Tobler (1994)</span>.
          <span data-afirma="c1-m12-11">Según la de <code>spatstat.data</code>
          <cite class="cita" data-ref="baddeley2017spatstatdata"></cite>, los pinos los recogió Numata (1961)</span>; <span data-afirma="c1-m12-14">no es el trabajo
          posterior del mismo autor que cita el libro de Baddeley, donde el conjunto descrito es mayor
          <cite class="cita" data-ref="baddeley2015spatial" data-loc="p. 4; p. 244; p. 779"></cite></span>.
          <span data-afirma="c1-m12-07">Las secuoyas son un dato de
          <cite class="cita" data-ref="strauss1975model" data-via="baddeley2015spatial" data-loc="p. 189" data-modo="narrativa"></cite>, del que
          <cite class="cita" data-ref="ripley1977modelling" data-via="baddeley2015spatial" data-loc="p. 189" data-modo="narrativa"></cite> tomó el
          subconjunto que se usa</span>. <span data-afirma="c1-m12-08">Las células vienen de
          <cite class="cita" data-ref="ripley1977modelling" data-via="baddeley2015spatial" data-loc="p. 157" data-modo="narrativa"></cite> y de un libro
          posterior del mismo autor</span>; <span data-afirma="c1-m12-12">las registraron Crick y Ripley
          <cite class="cita" data-ref="baddeley2017spatstatdata"></cite></span>. <span data-afirma="c1-m12-09">Los conteos de Carolina del
          Norte son los de 1974 a 1978: <cite class="cita" data-ref="cressie1993statistics" data-loc="p. 383; p. 390" data-modo="narrativa"></cite>
          los analiza, y dice que los habían presentado y ampliado otros trabajos</span>.
          <span data-afirma="c1-m12-13">Los datos del Mosa los tomaron en campo Van Rijn y Rikken, cuyo
          informe es de 1993, y los preparó para R Pebesma; la ayuda da también como referencia el libro de
          Burrough y McDonnell <cite class="cita" data-ref="pebesma2005sp"></cite></span>.</p>
        <p style="margin-bottom:0;">Una fuente <strong>descartada</strong>, y se dice por qué: las sedes educativas
          nacionales del Ministerio de Educación Nacional traen coordenadas con dos decimales —1.1 km de
          resolución—, y en Bogotá las sedes con coordenada colapsaban en unos pocos cientos de posiciones
          distintas. Eso no es un patrón puntual, es una retícula de redondeo, y las funciones del capítulo 4
          estarían midiendo el redondeo. <span data-afirma="c1-m12-05">No es un escrúpulo: discretizar las
          coordenadas es una de las causas corrientes de los puntos duplicados, y puede fabricar una
          regularidad aparente que es un artefacto del tratamiento del dato
          <cite class="cita" data-ref="baddeley2015spatial" data-loc="p. 146; p. 210"></cite></span>. No se construye material sobre coordenadas que no se sostienen, por
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
          <li><span data-afirma="c1-m12-06"><cite class="cita" data-ref="cressie1993statistics" data-loc="§1.1" data-modo="narrativa"></cite>, el modelo
            general del que los tres tipos de dato son casos particulares</span>. Va con más profundidad que
            este curso.</li>
          <li><cite class="cita" data-ref="bivand2013applied" data-modo="narrativa"></cite>, el ecosistema de paquetes
            de R espacial.</li>
          <li><cite class="cita" data-ref="gehlke1934certain" data-modo="narrativa"></cite>, un artículo temprano
            sobre lo que agrupar unidades le hace al tamaño de un coeficiente de correlación, el asunto del
            módulo 7. Va como lectura: no se ha podido consultar para este capítulo.</li>
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
""" + CIERRE_FUENTES

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
# LAS DURACIONES SE MIDEN (R3 · T3.4, H-08, D8). Hasta R2 cada ronda sumaba
# a ojo «un minuto por cada 200 palabras añadidas» desde la duración que el
# módulo tenía al cerrar R1, y la lectura de estudiante del 2026-11-13 encontró
# el módulo 2 y el 3 a once minutos de lo declarado. Ahora las mide
# `precalculo/mide_duraciones_cap1.py` sobre el HTML ensamblado, con las tasas
# escritas y justificadas en su cabecera (200 palabras/min, ×1.4 en los
# bloques con fórmula, 2.5 min por simulador, 1 min por mapa, tabla o figura,
# 7.5 líneas de código por minuto en un solo lenguaje, 1.2 min por pregunta),
# y `guardas_de_t34()` para el ensamblado si una de las de abajo se sale de
# ±15 % de su medida. Cada cifra es la medida redondeada al minuto:
#
#     python3 precalculo/mide_duraciones_cap1.py
#
# Son las del CAMINO PRINCIPAL: sin los paneles plegables de deducción, que
# son opcionales y el medidor da aparte, y, en el módulo 12, leer y hacer el
# cuestionario y leer los enunciados de los ejercicios, no resolverlos. El
# total, con y sin los seis paneles, lo imprime el medidor: aquí no se
# copia, para que no se quede viejo.
MODULOS_NAV = [
    ("El mapa que cambió la epidemiología", "32 min"),
    ("Los tres tipos de dato espacial", "33 min"),
    ("La primera ley de Tobler", "31 min"),
    ("Por qué se rompe la inferencia clásica", "29 min"),
    ("Tamaño de muestra efectivo", "14 min"),
    # R3 · T3.2 (H-20): el mismo título que la cabecera del módulo.
    ("Estacionariedad, isotropía y una sola realización", "14 min"),
    ("Escala, soporte y agregación", "24 min"),
    ("El ecosistema de R espacial", "16 min"),
    ("Anatomía de un objeto sf", "6 min"),
    ("Dependencia espacial en ciencia de datos", "18 min"),
    ("Glosario de notación del curso", "10 min"),
    ("Autoevaluación y ejercicios guiados", "21 min"),
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

# EL PRESUPUESTO DE GEOMETRÍA DEL CAPÍTULO, Y POR QUÉ SUBE A 135 KB (R2 · T2.3).
# Eran 120 KB, medidos aquí como se incrusta el JSON en el HTML —con un
# espacio tras cada separador, que es como lo escribe `json.dumps`—. Al
# cerrar T2.2 la geometría iba por 115.3 KB. Los tres bordes de Bogotá que
# pide G-03 —el perímetro urbano, el Distrito y el rectángulo de las sedes,
# simplificados a 220 y 160 vértices— añaden 4.5 KB: 119.8, a dos décimas
# del tope. El tope pasa a 135: lo de entonces más un margen de 15 KB, que
# es lo que ocupan tres capas de borde como estas. Después entró el borde en
# que cae cada sede (`dentro`, una cifra por sede para la lectura del mapa),
# 6.4 KB más: 126.2.
# No es un presupuesto de contenido sino una alarma contra una geometría
# sin simplificar —un mapa municipal entero son varios cientos de KB—, y a
# 135 sigue saltando ante eso. El auditor del precálculo mide otra cosa, el
# archivo tal como lo escribe R, sin espacios: ahí van 105.2 de 120.
PRESUPUESTO_GEO_KB = 135

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

M2_JS = r'''    // ================================================================
    // LOS SEIS MAPAS DEL MÓDULO 2, CABLEADOS (R2 · T2.3)
    //
    // Cada par enseña lo que le es propio a su tipo, y los seis comparten el
    // mismo interruptor: «¿Qué es aleatorio aquí?». La respuesta está
    // escrita debajo de cada mapa y el interruptor la enseña; así la
    // pregunta del módulo se contesta sobre el mapa, con el mismo gesto en
    // los seis.
    //   · puntuales: la VENTANA se puede cambiar sin mover un punto, y la
    //     intensidad estimada cambia con ella;
    //   · de área: cada unidad dice su valor y la CLASE en que cae;
    //   · geoestadísticos: cada punto dice el VALOR MEDIDO en él.
    // Ninguna cifra se calcula aquí: las intensidades, las áreas y los
    // cortes vienen de R.
    // ================================================================
    // El interruptor: su estado es el propio párrafo de la respuesta, que
    // está en el marcado del módulo. Así no hay un segundo estado que pueda
    // discrepar de lo que se ve al volver al módulo.
    function interruptorAleatorio(ident) {
      const parrafo = () => document.getElementById('aleatorio-' + ident);
      // `controla`: el motor pone la respuesta justo debajo del botón (donde
      // se ve al pulsar, también en el teléfono) y la enlaza con aria-controls
      // y aria-expanded.
      return { etiqueta: 'La pregunta del módulo', controla: 'aleatorio-' + ident,
               opciones: [[true, '¿Qué es aleatorio aquí?']],
               valor: () => { const p = parrafo(); return !!p && !p.hidden; },
               alPulsar: v => { const p = parrafo(); if (p) p.hidden = !v; } };
    }
    // El rectángulo que ciñe a los puntos de un mapa, en sus unidades
    // cuantizadas: es geometría de lo que ya está dibujado.
    function cajaDePuntos1(d) {
      let x0 = Infinity, x1 = -Infinity, y0 = Infinity, y1 = -Infinity;
      for (let i = 0; i < d.pts.length; i += 2) {
        x0 = Math.min(x0, d.pts[i]); x1 = Math.max(x1, d.pts[i]);
        y0 = Math.min(y0, d.pts[i + 1]); y1 = Math.max(y1, d.pts[i + 1]);
      }
      return [x0, y0, x1, y0, x1, y1, x0, y1];
    }
    const BORDE_PUESTO = { color: '#012820', ancho: 2.2, cierra: true };
    // El rótulo del borde puesto: «ventana» solo si lo es. El rectángulo que
    // ciñe a los puntos no lo es en ningún mapa (lo eligen los datos).
    // «de» + artículo: «del perímetro urbano», no «de el perímetro urbano».
    const DE1 = s => s.startsWith('el ') ? 'del ' + s.slice(3) : 'de ' + s;
    const PUESTO1 = noValido => noValido ? 'borde puesto, que no es una ventana: ' : 'ventana: ';
    const BORDE_OTRO = { color: 'rgba(100, 116, 139, 0.9)', ancho: 1, trazo: [4, 4], cierra: true };

    // --- Los pinos del módulo 2: el mismo dato que el de la terna del
    // módulo 3, con sus dos bordes. La fuente se deriva de aquel literal sin
    // su `ventana`, porque aquí los dos rectángulos son capas con nombre.
    let pinosVentana = 'dato';
    const PINOS1 = Object.assign({}, GEOMAPAS['cap1-pinos'].fuente);
    const PINOS1_BORDES = { dato: [[PINOS1.ventana[0], PINOS1.ventana[1], PINOS1.ventana[2], PINOS1.ventana[1],
                                    PINOS1.ventana[2], PINOS1.ventana[3], PINOS1.ventana[0], PINOS1.ventana[3]]],
                            caja: [cajaDePuntos1(PINOS1)] };
    delete PINOS1.ventana;
    const PINOS1_NOMBRE = { dato: 'la ventana que viene con el dato', caja: 'el rectángulo que ciñe a los puntos' };
    GEOMAPAS['cap1-pinos-ventana'] = {
      fuente: () => PINOS1,
      get titulo() {
        const p = D1.puntual_canonico.japanesepines;
        // Un entero se escribe entero, como en la prosa (área 1, intensidad 65).
        const cifra = (x, dec) => Number.isInteger(x) ? String(x) : n5(x, dec);
        return pinosVentana === 'dato'
          ? `Pinos japoneses. Con la ventana del dato: ${p.n} pinos en un área de ${cifra(p.area, 3)}, intensidad estimada ${cifra(p.lambda, 5)}`
          : `Pinos japoneses. Con el rectángulo de los puntos: ${p.n} pinos en un área de ${cifra(p.area_caja, 3)}, intensidad estimada ${cifra(p.lambda_caja, 5)}. No es una ventana válida`;
      },
      get capasLineas() {
        const otra = pinosVentana === 'dato' ? 'caja' : 'dato';
        return [Object.assign({ lineas: PINOS1_BORDES[otra], etiqueta: 'el otro borde: ' + PINOS1_NOMBRE[otra] }, BORDE_OTRO),
                Object.assign({ lineas: PINOS1_BORDES[pinosVentana], etiqueta: PUESTO1(pinosVentana === 'caja') + PINOS1_NOMBRE[pinosVentana] }, BORDE_PUESTO)];
      },
      get etiqueta() {
        // La etiqueta dice el patrón, no solo qué hay (G-24).
        return 'Los ' + PINOS1.n + ' pinos japoneses, repartidos por el cuadrado sin un orden que se vea. '
          + (pinosVentana === 'caja' ? 'Borde continuo: ' : 'Ventana: ')
          + PINOS1_NOMBRE[pinosVentana] + (pinosVentana === 'caja' ? ', que no es una ventana válida' : '')
          + '; a trazos, ' + PINOS1_NOMBRE[pinosVentana === 'dato' ? 'caja' : 'dato'] + '.';
      },
      controles: [{ etiqueta: 'El borde con que se cuenta', opciones: [['dato', 'La ventana del dato'], ['caja', 'El rectángulo de los puntos']],
                    valor: () => pinosVentana, alPulsar: v => { pinosVentana = v; } },
                  interruptorAleatorio('pinos')],
      lectura: (i, d) => { const p = coordsDeMapa(d)[i];
        return `Pino ${i + 1} de ${d.n}, en x = ${p[0].toFixed(3)}, y = ${p[1].toFixed(3)}. No lleva ningún valor: su posición es el dato.`; },
      descripcion: () => DESC1_PINOS_VENTANA[pinosVentana],
__TABLA_PUNTOS__
    };

    // --- Bogotá: los tres bordes de los que habla la prosa.
    let bogotaVentana = 'urbano';
    const BOGOTA1_DONDE = ['fuera del Distrito Capital', 'en el Distrito Capital, fuera del perímetro urbano',
                           'dentro del perímetro urbano, y por tanto del Distrito Capital'];
    const BOGOTA1_NOMBRE = { urbano: 'el perímetro urbano', distrito: 'el Distrito Capital',
                             caja: 'el rectángulo que ciñe a las sedes' };
    // `defineProperties` con los descriptores, y no `Object.assign`: este
    // último LEE los getters al copiar y deja escrito su valor de ese
    // momento, así que el título, el borde y la etiqueta se quedaban para
    // siempre en la primera ventana mientras el botón marcaba otra.
    Object.defineProperties(GEOMAPAS['cap1-bogota'], Object.getOwnPropertyDescriptors({
      opacidadPuntos: 0.45,
      // El Distrito es cuatro veces más alto que ancho: con el alto por
      // defecto la ciudad se quedaba en una mancha de 40 px.
      alto: 600,
      get titulo() {
        const p = D1.colombia.puntual;
        if (bogotaVentana === 'urbano') return `Sedes educativas de Bogotá. Con el perímetro urbano por ventana: ${miles1(p.n_urbana)} sedes en ${n5(p.area_urbana_km2, 2)} km², ${n5(p.lambda_urbana)} por km²`;
        if (bogotaVentana === 'distrito') return `Sedes educativas de Bogotá. Con el Distrito Capital por ventana: ${miles1(p.n_dc)} sedes en ${n5(p.area_dc_km2, 2)} km², ${n5(p.lambda_dc)} por km²`;
        return `Sedes educativas de Bogotá. Con el rectángulo de las sedes: ${miles1(p.n)} sedes en ${n5(p.area_caja_km2, 2)} km², ${n5(p.lambda_caja)} por km². No es una ventana válida`;
      },
      get capasLineas() {
        const b = GEOMAPAS['cap1-bogota'].fuente.bordes;
        const capas = Object.keys(BOGOTA1_NOMBRE).filter(k => k !== bogotaVentana)
          .map((k, j) => Object.assign({ lineas: b[k] }, BORDE_OTRO, j === 0 ? { etiqueta: 'los otros dos bordes' } : {}));
        return capas.concat([Object.assign({ lineas: b[bogotaVentana],
          etiqueta: PUESTO1(bogotaVentana === 'caja') + BOGOTA1_NOMBRE[bogotaVentana] }, BORDE_PUESTO)]);
      },
      get etiqueta() {
        // El patrón y los bordes (G-24): las sedes se apiñan en el tercio norte
        // del dibujo, que es la ciudad (`visto.bogota`, contado por R).
        return 'Las ' + miles1(D1.colombia.puntual.n) + ' sedes educativas de Bogotá, apiñadas en el norte, que es la ciudad; '
          + 'el sur rural del Distrito casi no tiene. Borde continuo: ' + BOGOTA1_NOMBRE[bogotaVentana] + '; a trazos, los otros dos.';
      },
      controles: [{ etiqueta: 'El borde con que se cuenta', opciones: [['urbano', 'Perímetro urbano'], ['distrito', 'Distrito Capital'],
                                                   ['caja', 'Rectángulo de las sedes']],
                    valor: () => bogotaVentana, alPulsar: v => { bogotaVentana = v; } },
                  interruptorAleatorio('bogota')],
      // Cada sede dice en qué borde cae y si entra en la cuenta de la
      // ventana puesta. La pertenencia la escribe R (`dentro`: 2 perímetro
      // urbano, 1 resto del Distrito, 0 fuera de él), la misma que cuentan
      // `n_urbana` y `n_dc`; aquí no se decide nada con geometría.
      lectura: (i, d) => {
        const k = d.dentro[i];
        const donde = BOGOTA1_DONDE[k];
        const cuenta = bogotaVentana === 'caja' || (bogotaVentana === 'distrito' ? k >= 1 : k === 2);
        return `Sede ${miles1(i + 1)} de ${miles1(d.n)}: ${donde}. `
          + (bogotaVentana === 'caja' ? 'Con el rectángulo de las sedes entra en la cuenta, como todas.'
             : (cuenta ? 'Entra' : 'No entra') + ' en la cuenta ' + DE1(BOGOTA1_NOMBRE[bogotaVentana]) + '.');
      },
      descripcion: () => DESC1_BOGOTA[bogotaVentana]
    }));

    // --- Los dos de área: cada unidad dice su valor y su clase.
    const lecturaClase = (unidad, medida) => (i, d) => {
      const k = d.clase[i];
      return `${d.etiquetas[i]}: ${n5(d.valor[i], 2)} ${medida}. Clase ${k} de ${d.cortes.length - 1}, de ${n5(d.cortes[k - 1], 2)} a `
        + `${n5(d.cortes[k], 2)}. ${unidad} es fijo: lo que cambiaría al volver a tomar el dato es este valor.`;
    };
    Object.assign(GEOMAPAS['cap1-nc'], { controles: [interruptorAleatorio('nc')],
      lectura: lecturaClase('El condado', 'muertes súbitas por 1\u202f000 nacimientos') });
    Object.assign(GEOMAPAS['cap1-desercion'], { controles: [interruptorAleatorio('desercion')],
      lectura: lecturaClase('El departamento', '% de deserción') });

    // --- Los dos geoestadísticos: cada punto dice lo que se midió en él.
    Object.assign(GEOMAPAS['cap1-meuse'], { controles: [interruptorAleatorio('meuse')],
      lectura: (i, d) => `Punto de muestreo ${i + 1} de ${d.n}: ${miles1(d.marcas[i])} ppm de zinc. Es lo medido aquí; entre este punto y los de al lado también hay zinc, sin medir.` });
    Object.assign(GEOMAPAS['cap1-ideam'], { controles: [interruptorAleatorio('ideam')],
      lectura: (i, d) => `Estación ${i + 1} de ${d.n}: ${n5(d.marcas[i], 1)} °C de temperatura media anual. Es lo medido aquí; entre esta estación y las de al lado también hay temperatura, sin medir.` });

    // --- Y el mapa de Snow: cada muerte dice su bomba más próxima.
    Object.assign(GEOMAPAS['cap1-snow'], {
      lectura: (i, d) => `Muerte ${i + 1} de ${d.n}: su bomba más próxima es la de ${d.niveles[d.marcas[i] - 1]}.` });
'''

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
# R2 · T2.3 (ronda 2): los dos tercios del sur no son «el suelo rural del
# Distrito» sin más. Una de sus sedes cae fuera del Distrito, y el perímetro
# urbano acaba a pocos metros del corte. R cuenta las dos cosas (`urbana`,
# `fuera_dc`, `margen_urbano_m`) y la frase dice lo que cuentan.
_BGU = dict(zip(_VI["bogota"]["franja"], _VI["bogota"]["urbana"]))
_BGF = dict(zip(_VI["bogota"]["franja"], _VI["bogota"]["fuera_dc"]))
_BG_FUERA_SUR = _BGF["centro"] + _BGF["sur"]
# (Ronda 5.) «Cabe entero» sale de `urbano_en_tercio_norte` (R cubre el
# perímetro con el tercio norte de la caja), y el lado del corte, del signo
# del margen, que se escribe sin signo.
_MG = _VI["bogota"]["margen_urbano_m"]
DESC_BOGOTA = (
    f"Las {ent(D['colombia']['puntual']['n'])} sedes se apiñan en el tercio norte del dibujo, que es la "
    f"ciudad: {ent(_BG['norte'])}, entre ellas las {ent(_BGU['norte'])} del perímetro urbano, que "
    f"{'cabe' if _VI['bogota'].get('urbano_en_tercio_norte') else 'no cabe'} entero "
    f"en ese tercio y acaba {n(abs(_MG), 1)} m {'al norte' if _MG > 0 else 'al sur'} del corte. El tercio del "
    f"medio y el del sur, fuera del perímetro, tienen {ent(_BG['centro'])} y {ent(_BG['sur'])}, "
    + ("todas dentro del Distrito." if _BG_FUERA_SUR == 0 else
       "dentro del Distrito salvo una, que cae fuera de él." if _BG_FUERA_SUR == 1 else
       f"dentro del Distrito salvo {ent(_BG_FUERA_SUR)}, que caen fuera de él."))
_PJ = _PC["japanesepines"]
DESC_PINOS_VENTANA = {
    "dato": DESC_PINOS + (
        f" El borde continuo es la ventana que viene con el dato, de área {_PJ['area']}: con ella la "
        f"intensidad estimada es {_PJ['lambda']} pinos por unidad de área. A trazos, el rectángulo que "
        f"ciñe a los puntos."),
    "caja": DESC_PINOS + (
        f" El borde continuo es ahora el rectángulo que ciñe a los puntos, de área {n(_PJ['area_caja'], 3)}: "
        f"sin que se haya movido un pino, la intensidad estimada pasa a {n(_PJ['lambda_caja'])}. No es una "
        f"ventana: lo dibujan los propios pinos, que quedan todos dentro. A trazos, la ventana que viene con el "
        f"dato."),
}
_BP = D["colombia"]["puntual"]
DESC_BOGOTA_V = {
    "urbano": DESC_BOGOTA + (
        f" El borde continuo es el perímetro urbano, que ciñe la mancha del norte: dentro caen "
        f"{ent(_BP['n_urbana'])} sedes, {n(_BP['lambda_urbana'])} por km². A trazos, el Distrito Capital, "
        f"que baja mucho más al sur, y el rectángulo que ciñe a las sedes."),
    "distrito": DESC_BOGOTA + (
        f" El borde continuo es el Distrito Capital, que incluye todo el sur rural casi vacío: dentro caen "
        f"{ent(_BP['n_dc'])} sedes, {n(_BP['lambda_dc'])} por km². A trazos, el perímetro urbano, mucho "
        f"menor, y el rectángulo que ciñe a las sedes."),
    "caja": DESC_BOGOTA + (
        f" El borde continuo es el rectángulo que ciñe a las sedes: el {n(_BP['pct_caja_fuera_dc'])} % de "
        f"su área queda fuera del Distrito, donde nadie buscó sedes, y por eso no es una ventana válida. Con "
        f"él saldrían {n(_BP['lambda_caja'])} sedes por km². A trazos, el perímetro urbano y el Distrito."),
}
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
# R2 · T2.3 (ronda 3): «lo más oscuro está en el sur y el oriente» era falso
# para la clase más oscura, que tiene departamentos del centro y del norte.
# Lo que sí está en el sur y el oriente son los tres valores más altos. La
# clase más oscura se cuenta por zona, con la tabla que publica R.
_ZD = _DS["clase_alta"]["zonas"]
DESC_DESERCION = (
    f"Los tres valores más altos están en el sur y el oriente del país: "
    + lista_y([f"{_corto(f['departamento'])} ({n(f['pct'], 2)} %)" for f in _DS["mayores"]])
    + f". La clase más oscura, de {n(M['desercion']['cortes'][-2], 2)} a {n(M['desercion']['cortes'][-1], 2)} %, "
    f"reúne {ent(_DS['clase_alta']['n'])} departamentos repartidos por el país: "
    + lista_y([f"{ent(k)} en el {z}" for z, k in zip(_ZD["zona"], _ZD["n"])])
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
# R2 · T2.3 (ronda 4): «donde están las más altas», leído solo, se entendía
# como «las temperaturas más altas». Ahora dice «las estaciones de mayor
# altitud», con su cifra (el décimo más alto, por zona), y «baja» con el
# signo que publica R (`baja_por_km`).
# (Ronda 5.) «29 de las 37 de 2 560 m o más», sin sustantivo, chocaba con
# «las 37 más frías» de la misma frase: se oía «29 de las 37 más frías». La
# cifra de las altas lleva ahora «estaciones situadas a» y su zona.
_AL = _VI["ideam"]["altas"]
_PATRON_IDEAM = (f"{ent(_FR['n'][0])} están en el {_FR['zona'][0]} del dibujo, donde se concentran las estaciones "
                 f"de mayor altitud")
DESC_IDEAM = (
    f"Las {ent(_GEO['n'])} estaciones, con el contorno del país de fondo, coloreadas por su temperatura "
    f"media. Las del archipiélago de San Andrés, arriba a la izquierda, se ven sobre el mar: a esta escala "
    f"las islas son más pequeñas que un punto. La temperatura va de "
    f"{n(_GEO['t_min'], 1)} °C, en azul índigo, a {n(_GEO['t_max'], 1)} °C, en amarillo. De las "
    f"{ent(_VI['ideam']['n_frias'])} más frías, de {n(_VI['ideam']['frias_umbral'], 1)} °C o menos, "
    f"{_PATRON_IDEAM}: {ent(_AL['zonas']['n'][0])} de las {ent(_AL['n'])} estaciones situadas a "
    f"{ent(_AL['umbral_m'])} m o más están en el {_AL['zonas']['zona'][0]}. La temperatura "
    f"{'baja' if _VI['ideam']['baja_por_km'] > 0 else 'sube'} {n(abs(_VI['ideam']['baja_por_km']), 1)} °C por cada "
    f"kilómetro de altura. Las "
    f"{ent(_VI['ideam']['n_calidas'])} más cálidas, de "
    f"{n(_VI['ideam']['calidas_umbral'], 1)} °C o más: "
    + lista_y([f"{ent(k_)} en el {z_}" for z_, k_ in zip(_CA["zona"], _CA["n"])]) + ".")


# LA ETIQUETA ACCESIBLE DE LOS SIETE MAPAS QUE NO LA TENÍAN (R2 · T2.3, G-24).
# Sin `etiqueta`, el motor componía «título, n unidades. palabra de la
# leyenda», que dice qué hay pero no qué se ve. Cada etiqueta lleva el patrón,
# y el patrón es una frase de su descripción larga, que ya tiene guarda en
# `guardas_de_las_descripciones()`: aquí no se afirma nada que allí no se
# compruebe. La guarda de abajo exige que la frase esté en las dos.
PATRON1 = {
    "cap1-pinos": "se reparten sin orden aparente, sin grumos marcados ni distancias regulares",
    "cap1-secuoyas": "se amontonan en grumos, con mucho vacío entre ellos",
    "cap1-celulas": "se reparten casi como una rejilla, sin parejas pegadas",
    "cap1-nc": f"salen repartidos por todo el estado, con más en el {_VNC1['zona'][0]} del dibujo",
    "cap1-desercion": "valores más altos están en el sur y el oriente del país",
    "cap1-meuse": "pegados a la orilla",
    "cap1-ideam": _PATRON_IDEAM,
}
DESC_DE1 = {"cap1-pinos": DESC_PINOS, "cap1-secuoyas": DESC_SECUOYAS, "cap1-celulas": DESC_CELULAS,
            "cap1-nc": DESC_NC, "cap1-desercion": DESC_DESERCION, "cap1-meuse": DESC_MEUSE,
            "cap1-ideam": DESC_IDEAM}
ETIQUETA1 = {
    "cap1-pinos": f"Pinos japoneses: los {ent(_PC['japanesepines']['n'])} árboles "
                  f"{PATRON1['cap1-pinos']}.",
    "cap1-secuoyas": f"Plántulas de secuoya: las {ent(_PC['redwood']['n'])} "
                     f"{PATRON1['cap1-secuoyas']}.",
    "cap1-celulas": f"Células: las {ent(_PC['cells']['n'])} {PATRON1['cap1-celulas']}.",
    "cap1-nc": f"Tasa de muerte súbita infantil en los {ent(_NC1['n'])} condados de Carolina del Norte, en "
               f"{ent(len(_NC1['tam']))} clases por cuantiles: los de la clase más alta "
               f"{PATRON1['cap1-nc']}.",
    "cap1-desercion": f"Deserción escolar en los {ent(M['desercion']['n'])} departamentos de Colombia, en "
                      f"{ent(len(M['desercion']['tam']))} clases por cuantiles: los tres "
                      f"{PATRON1['cap1-desercion']}, y la clase más alta reúne {ent(_DS['clase_alta']['n'])} "
                      f"departamentos repartidos por {ent(len(_ZD['zona']))} zonas del dibujo, "
                      f"{ent(_ZD['n'][0])} de ellos en el {_ZD['zona'][0]}.",
    "cap1-meuse": f"Zinc en los {ent(_GC['n'])} puntos de muestreo de la vega del Mosa: los más altos se "
                  f"alinean a lo largo del borde noroeste de la nube, {PATRON1['cap1-meuse']} del río, y el zinc "
                  f"baja al alejarse de ella.",
    "cap1-ideam": f"Temperatura media anual en las {ent(_GEO['n'])} estaciones del IDEAM: de las "
                  f"{ent(_VI['ideam']['n_frias'])} más frías, {PATRON1['cap1-ideam']}.",
}

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
        f"{n(c['rho_vecino'], 2)} y la I de Moran del mapa es {n(c['moran'], 2)}: "
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
    "cap1-pinos-ventana": list(DESC_PINOS_VENTANA.values()),
    "cap1-bogota": list(DESC_BOGOTA_V.values()), "cap1-nc": [DESC_NC], "cap1-desercion": [DESC_DESERCION],
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
    # El margen se MIDE: el perímetro urbano tiene que acabar al norte del corte
    # (y por tanto los tercios del sur, «fuera del perímetro», no tener sedes
    # urbanas), y las sedes de fuera del Distrito son las que dice la frase.
    exige(_VI["bogota"]["margen_urbano_m"] > 0 and _VI["bogota"].get("urbano_en_tercio_norte") is True
          and _BGU["centro"] == 0 and _BGU["sur"] == 0
          and _BGU["norte"] == D["colombia"]["puntual"]["n_urbana"],
          "Bogotá: el perímetro urbano ya no cabe en el tercio norte, y los del sur no están «fuera del perímetro»")
    exige(sum(_VI["bogota"]["fuera_dc"]) == D["colombia"]["puntual"]["n"] - D["colombia"]["puntual"]["n_dc"]
          and _BGF["norte"] + _BG_FUERA_SUR == sum(_VI["bogota"]["fuera_dc"]),
          "Bogotá: las sedes fuera del Distrito por tercio no cuadran con las del dato")
    exige(_VNC1["clase_alta_n"] == _NC1["tam"][-1] and len(_VNC1["zona"]) >= 5 and _VNC1["n"][0] > _VNC1["n"][1],
          "Carolina del Norte: «repartidos por todo el estado, con más en una zona» ya no vale")
    exige(all(f["zona"] in ("sur", "oriente", "suroriente") for f in _DS["mayores"]),
          "deserción: «los tres valores más altos, en el sur y el oriente» ya no vale")
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
          "campo: la correlación entre vecinas o la I de Moran ya no crecen con el alcance")
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


# =====================================================================
# LO QUE DICEN LAS LECTURAS, LOS TÍTULOS Y LAS RESPUESTAS (R2 · T2.3, ronda 2)
# =====================================================================
# Los textos del módulo 2 se componen en el navegador: la lectura de cada
# unidad, el título y los rótulos de cada estado de los mandos. Las guardas
# de arriba miran el dato; esta mira lo que el JavaScript ESCRIBE con él. Se
# ejecuta el documento ya ensamblado en Node, con el DOM sustituido por un
# objeto que todo lo acepta, se piden al registro de cada mapa su lectura de
# TODAS las unidades y su título y rótulos en cada estado, y se comparan con
# lo que dice el JSON, escrito aquí por otra vía (Python, sin pasar por el JS).
# Lo que se compara son cifras y frases que el capítulo afirma: si el código
# lee la marca del vecino, el corte de la clase siguiente o la etiqueta de
# otra ventana, la cifra o la frase dejan de cuadrar y el ensamblado para.
_NODE_LECTURAS = r"""
const fs = require('fs'), vm = require('vm');
const html = fs.readFileSync(process.argv[2], 'utf8');
const scripts = [...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m => m[1]);
const nada = () => new Proxy(function () {}, {
  get: (t, k) => k === Symbol.toPrimitive ? () => '' : k === 'then' ? undefined : nada(),
  set: () => true, apply: () => nada(), construct: () => nada() });
const base = { console, Math, JSON, Number, String, Array, Object, Set, Map, WeakMap, Date, RegExp, Error, TypeError,
  Promise, parseFloat, parseInt, isFinite, isNaN, Symbol, Infinity, NaN, Boolean, Function, Reflect, Proxy, Intl,
  setTimeout: () => 0, clearTimeout: () => 0, setInterval: () => 0, clearInterval: () => 0,
  requestAnimationFrame: () => 0, cancelAnimationFrame: () => 0 };
const ctx = new Proxy(base, { has: () => true,
  get: (t, k) => (k in t ? t[k] : (k === Symbol.unscopables ? undefined : nada())),
  set: (t, k, v) => { t[k] = v; return true; } });
vm.createContext(ctx);
const errores = [];
for (const s of scripts) { try { vm.runInContext(s, ctx); } catch (e) { errores.push(String(e).slice(0, 200)); } }
let out = {};
try {
  out = vm.runInContext(`(() => {
    const G = GEOMAPAS, f = r => typeof r.fuente === 'function' ? r.fuente() : r.fuente;
    const todas = r => { const d = f(r); const L = []; for (let i = 0; i < geomapaNumUnidades(d); i++) L.push(String(r.lectura(i, d, r))); return L; };
    const estado = (id, v) => { const r = G[id]; r.controles[0].alPulsar(v);
      return { titulo: String(r.titulo), etiqueta: String(r.etiqueta),
               capas: r.capasLineas.map(c => c.etiqueta || ''), leyenda: String(geomapaLeyenda(f(r), r)),
               lecturas: r.lectura ? todas(r) : [] }; };
    const o = { bogota: {}, pinos: {}, lect: {}, alt: {} };
    ['urbano', 'distrito', 'caja'].forEach(v => { o.bogota[v] = estado('cap1-bogota', v); });
    ['dato', 'caja'].forEach(v => { o.pinos[v] = estado('cap1-pinos-ventana', v); });
    ['cap1-nc', 'cap1-desercion', 'cap1-meuse', 'cap1-ideam', 'cap1-snow'].forEach(k => { o.lect[k] = todas(G[k]); });
    Object.keys(G).forEach(k => { o.alt[k] = String(geomapaAlt(f(G[k]), G[k])); });
    o.controla = {};
    ['pinos-ventana', 'bogota', 'nc', 'desercion', 'meuse', 'ideam'].forEach(k => {
      o.controla[k] = (G['cap1-' + k].controles || []).map(g => g.controla || null); });
    return JSON.stringify(o); })()`, ctx);
} catch (e) { errores.push('al pedir las lecturas: ' + String(e).slice(0, 300)); }
process.stdout.write(JSON.stringify({ errores, out: typeof out === 'string' ? JSON.parse(out) : {} }));
"""


def guardas_de_lecturas(doc: str, marcado: str) -> list[str]:
    """Lo que escriben las lecturas, los títulos y las respuestas del módulo 2, contra el JSON."""
    import shutil, subprocess, tempfile
    # `problemas.append` y no un `exige` de closure: así cada guarda entra en el
    # inventario de prueba_ensambla_cap1.py y se ve disparar por su línea.
    problemas = []

    node = shutil.which("node") or "/opt/homebrew/bin/node"
    with tempfile.TemporaryDirectory() as tmp:
        html = pathlib.Path(tmp) / "cap1.html"
        html.write_text(doc, encoding="utf-8")
        guion = pathlib.Path(tmp) / "lecturas.js"
        guion.write_text(_NODE_LECTURAS, encoding="utf-8")
        try:
            r = subprocess.run([node, str(guion), str(html)], capture_output=True, text=True, timeout=120)
            res = json.loads(r.stdout or "{}")
        except Exception as e:  # sin Node no hay guarda, y eso para el ensamblado
            problemas.append(f"lecturas: no se pudo ejecutar el documento en Node ({e})")
            return problemas
    if not (not res.get("errores")):
        problemas.append(f"lecturas: el documento no se ejecuta entero en Node: {res.get('errores')}")
    o = res.get("out") or {}
    if not o:
        problemas.append("lecturas: Node no devolvió las lecturas")
        return problemas

    def miles(x):
        return f"{int(x):,}".replace(",", " ")

    # --- Bogotá: cada sede, en cada ventana --------------------------------
    bp, mb = D["colombia"]["puntual"], M["bogota"]
    donde = {2: "dentro del perímetro urbano, y por tanto del Distrito Capital",
             1: "en el Distrito Capital, fuera del perímetro urbano", 0: "fuera del Distrito Capital"}
    cuenta_de = {"urbano": lambda k: k == 2, "distrito": lambda k: k >= 1, "caja": lambda k: True}
    nombre_de = {"urbano": "del perímetro urbano", "distrito": "del Distrito Capital"}
    cifras = {"urbano": (bp["n_urbana"], bp["area_urbana_km2"], bp["lambda_urbana"]),
              "distrito": (bp["n_dc"], bp["area_dc_km2"], bp["lambda_dc"]),
              "caja": (bp["n"], bp["area_caja_km2"], bp["lambda_caja"])}
    for v in ("urbano", "distrito", "caja"):
        e = o["bogota"].get(v, {})
        lect = e.get("lecturas", [])
        if not (len(lect) == mb["n"]):
            problemas.append(f"Bogotá ({v}): la lectura no cubre las {mb['n']} sedes")
        mal = []
        for i, t in enumerate(lect):
            k = mb["dentro"][i]
            pide = f"Sede {miles(i + 1)} de {miles(mb['n'])}: {donde[k]}. "
            pide += ("Con el rectángulo de las sedes entra en la cuenta, como todas." if v == "caja" else
                     ("Entra" if cuenta_de[v](k) else "No entra") + f" en la cuenta {nombre_de[v]}.")
            if t != pide:
                mal.append((i, t))
        if not (not mal):
            problemas.append(f"Bogotá ({v}): {len(mal)} lecturas no dicen el borde o la cuenta del dato, p. ej. {mal[:1]}")
        nv, av, lv = cifras[v]
        if not (f"{miles(nv)} sedes en {av:.2f} km², {lv:.5f} por km²" in e.get("titulo", "")):
            problemas.append(f"Bogotá ({v}): el título no da las sedes, el área y la intensidad de su ventana: «{e.get('titulo')}»")
        puesto = (e.get("capas") or [""])[-1]
        if v == "caja":
            if not ("No es una ventana válida" in e.get("titulo", "") and not puesto.startswith("ventana")
                  and "<span>ventana: el rectángulo" not in e.get("leyenda", "")):
                problemas.append("Bogotá: el rectángulo de las sedes se rotula como ventana, o el título no dice que no lo es")
        else:
            if not (puesto.startswith("ventana: ")):
                problemas.append(f"Bogotá ({v}): el borde puesto no se rotula como ventana")

    # --- Pinos: los dos bordes ---------------------------------------------
    pj = D["puntual_canonico"]["japanesepines"]
    cifra = lambda x, dec: str(int(x)) if float(x).is_integer() else f"{x:.{dec}f}"
    for v, (a_, l_) in (("dato", (pj["area"], pj["lambda"])), ("caja", (pj["area_caja"], pj["lambda_caja"]))):
        e = o["pinos"].get(v, {})
        if not (f"en un área de {cifra(a_, 3)}, intensidad estimada {cifra(l_, 5)}" in e.get("titulo", "")):
            problemas.append(f"pinos ({v}): el título no da el área y la intensidad de ese borde: «{e.get('titulo')}»")
        puesto = (e.get("capas") or [""])[-1]
        if v == "caja":
            if not ("No es una ventana válida" in e.get("titulo", "") and not puesto.startswith("ventana")
                  and "Ventana: el rectángulo" not in e.get("etiqueta", "")
                  and "<span>ventana: el rectángulo" not in e.get("leyenda", "")):
                problemas.append("pinos: el rectángulo de los puntos se rotula como ventana: la eligen los datos")
        else:
            if not (puesto.startswith("ventana: ")):
                problemas.append("pinos: la ventana del dato no se rotula como ventana")

    # --- Los de área: valor y clase de cada unidad --------------------------
    for k_, clave in (("cap1-nc", "nc"), ("cap1-desercion", "desercion")):
        g, lect = M[clave], o["lect"].get(k_, [])
        nk = len(g["cortes"]) - 1
        mal = [i for i, t in enumerate(lect)
               if not t.startswith(f"{g['etiquetas'][i]}: {g['valor'][i]:.2f} ")
               or f"Clase {g['clase'][i]} de {nk}, de {g['cortes'][g['clase'][i] - 1]:.2f} a "
                  f"{g['cortes'][g['clase'][i]]:.2f}." not in t]
        if not (len(lect) == g["n"] and not mal):
            problemas.append(f"{k_}: {len(mal)} lecturas no dan el valor o la clase del dato, p. ej. {[lect[i] for i in mal[:1]]}")
    gm, lect = M["meuse"], o["lect"].get("cap1-meuse", [])
    mal = [i for i, t in enumerate(lect)
           if not t.startswith(f"Punto de muestreo {i + 1} de {gm['n']}: {miles(round(gm['marcas'][i]))} ppm de zinc.")]
    if not (len(lect) == gm["n"] and not mal):
        problemas.append(f"meuse: {len(mal)} lecturas no dan el zinc de su punto")
    gi, lect = M["ideam"], o["lect"].get("cap1-ideam", [])
    mal = [i for i, t in enumerate(lect)
           if not t.startswith(f"Estación {i + 1} de {gi['n']}: {gi['marcas'][i]:.1f} °C")]
    if not (len(lect) == gi["n"] and not mal):
        problemas.append(f"IDEAM: {len(mal)} lecturas no dan la temperatura de su estación")
    gs, lect = M["snow"], o["lect"].get("cap1-snow", [])
    mal = [i for i, t in enumerate(lect)
           if not t.endswith(f"su bomba más próxima es la de {gs['niveles'][gs['marcas'][i] - 1]}.")]
    if not (len(lect) == gs["n"] and not mal):
        problemas.append(f"Snow: {len(mal)} lecturas no dan la bomba de su muerte")
    if not (not any(" de el " in t for e in o["bogota"].values() for t in e.get("lecturas", []))):
        problemas.append("Bogotá: la lectura escribe «de el»")

    # --- Las etiquetas accesibles: el patrón, no la palabra de la leyenda (G-24)
    # (Ronda 4.) La deserción no exige la frase literal en la descripción: su
    # guarda propia, más abajo, LEE las zonas de las dos y las compara con R, y
    # «el oriente y el sur» dice lo mismo que «el sur y el oriente».
    # (Ronda 5.) Pero el resto de la frase sí se exige, con un patrón fijo
    # aquí y no copiado de PATRON1: «los tres valores más altos están en …
    # del país», en la etiqueta y en la descripción. Con la excepción a secas,
    # «más bajos» en PATRON1 pasaba.
    import re as _re5
    _ZONAS5 = r"(?:nororiente|noroccidente|suroriente|suroccidente|norte|sur|oriente|occidente|centro)"
    _RX_MAYORES = (r"\b[Ll]os tres valores más altos están en (el " + _ZONAS5 + r"(?:(?:, | y )el " + _ZONAS5
                   + r")*) del país[,:]")
    for k_, etq in ETIQUETA1.items():
        literal = (bool(_re5.search(_RX_MAYORES, DESC_DE1[k_]) and _re5.search(_RX_MAYORES, etq))
                   if k_ == "cap1-desercion" else PATRON1[k_] in DESC_DE1[k_])
        if not (literal and PATRON1[k_] in etq and o["alt"].get(k_) == etq):
            problemas.append(f"{k_}: la etiqueta accesible no es la que lleva el patrón de su descripción")
    ley = {k_: M[c].get("leyenda", "") for k_, c in (("cap1-nc", "nc"), ("cap1-desercion", "desercion"),
                                                      ("cap1-meuse", "meuse"), ("cap1-ideam", "ideam"))}
    if not (not [k_ for k_, l_ in ley.items() if l_ and l_ in o["alt"].get(k_, "")]):
        problemas.append("una etiqueta accesible arrastra la palabra de la leyenda")

    # --- Las respuestas a «¿qué es aleatorio aquí?», por tipo ---------------
    import re as _re3
    plano = _re3.sub(r"\s+", " ", marcado)
    resp = {m_.group(1): m_.group(2) for m_ in _re3.finditer(r'<p class="geomapa-pie" id="aleatorio-(\w+)"[^>]*>(.*?)</p>', plano)}
    tipo = {"pinos": "Lo aleatorio es dónde.", "bogota": "Lo aleatorio es dónde.",
            "nc": "Lo aleatorio es el valor de cada unidad.", "desercion": "Lo aleatorio es el valor de cada unidad.",
            "meuse": "Lo aleatorio es el campo entero.", "ideam": "Lo aleatorio es el campo entero."}
    if not (all(resp.get(k_, "").startswith(f"<strong>{t}</strong>") for k_, t in tipo.items())):
        problemas.append("módulo 2: una respuesta a «¿qué es aleatorio aquí?» no es la de su tipo de dato")
    if not ("no es una ventana" in resp.get("pinos", "") and "no vale como ventana" in resp.get("bogota", "")
          and not any("antes de mirar, y por eso" in t for t in resp.values())):
        problemas.append("módulo 2: la respuesta de los puntuales no dice por qué el rectángulo de los puntos no es una ventana, "
          "o vuelve a atribuir el cambio de λ̂ a que la ventana se fije antes de mirar")
    if not (f"el área pasa de {pj['area']} a {n(pj['area_caja'], 3)} y" in plano
          and f"de {pj['lambda']} a {n(pj['lambda_caja'])}, sin que se mueva un pino" in plano):
        problemas.append("módulo 2: la prosa no da el área y la intensidad de los dos bordes de los pinos")
    # --- R2 · T2.3 (ronda 3) ----------------------------------------------
    # Cada frase fija que describe una dirección, un sentido o una zona se
    # LEE y se compara con la cifra de R que dice lo mismo; no con una copia
    # de sí misma.
    import re as _re4
    _ZONAS = r"(nororiente|noroccidente|suroriente|suroccidente|norte|sur|oriente|occidente|centro)"
    # Deserción: las zonas que nombra la frase de los tres mayores, contra las
    # zonas de R; y el reparto de la clase más oscura, contra su tabla.
    _ds = D["visto"]["desercion"]
    # (Ronda 5.) Las dos se leen con el mismo patrón entero («los tres valores
    # más altos están en … del país»), la etiqueta publicada incluida.
    _mde = _re4.search(_RX_MAYORES, ETIQUETA1["cap1-desercion"])
    _dichas = set(_re4.findall(r"\bel " + _ZONAS + r"\b", _mde.group(1))) if _mde else {"(sin la frase)"}
    _mdd = _re4.search(_RX_MAYORES, DESC_DE1["cap1-desercion"])
    _dichas_d = set(_re4.findall(r"\bel " + _ZONAS + r"\b", _mdd.group(1))) if _mdd else {"(sin la frase)"}
    if not (_dichas == _dichas_d == {f_["zona"] for f_ in _ds["mayores"]}):
        problemas.append(f"deserción: la frase sitúa los valores más altos en {sorted(_dichas)} y R, en "
                         f"{sorted({f_['zona'] for f_ in _ds['mayores']})}")
    # (Ronda 6.) Los tres departamentos que nombra la frase, con su cifra, se
    # LEEN y tienen que ser los tres valores más altos del mapa que dibuja R
    # (`M["desercion"]`), no de la lista de `visto` con que se escribe la frase:
    # llenarla con `menores` pasaba. Y la lista de `visto` cuyas zonas se
    # comprueban arriba tiene que ser la de esos mismos tres.
    # (Ronda 7.) La frase de los tres más bajos («Lo más claro, en …») pasa por
    # la misma guarda, con el mapa ordenado al revés y `visto.menores`: llenarla
    # con `mayores` publicaba «Lo más claro, en Caquetá (6.73 %), …».
    _gd = M["desercion"]

    def _tres_extremos(cuales: str, rx_lista: str, lista_visto: list) -> None:
        """Lee (departamento, cifra) de la frase y los contrasta con el mapa de R.

        `cuales` es «altos» o «bajos»; `rx_lista` captura la lista de la frase en
        su grupo `lista`. Los tres tienen que ser los tres extremos de
        `M["desercion"]` en ese sentido, sin empate con el cuarto, y la lista de
        `visto` con que se escribe la frase tiene que ser la de esos mismos tres.
        """
        orden = sorted(zip(_gd["valor"], _gd["etiquetas"]), key=lambda t: t[0], reverse=cuales == "altos")
        r_ = sorted((_corto(e_), n(v_, 2)) for v_, e_ in orden[:3])
        lt_ = _re4.search(rx_lista, DESC_DE1["cap1-desercion"])
        piezas_ = (list(_re4.finditer(r"(?:^|, | y )([^()]+?) \((-?\d+(?:\.\d+)?)\s%\)", lt_.group("lista")))
                   if lt_ else [])
        dichos_ = sorted((m_.group(1), m_.group(2)) for m_ in piezas_)
        # La lista se lee entera: lo que no case con «departamento (cifra %)»
        # (una cifra con coma, un cuarto departamento metido con «junto con»)
        # no se salta en silencio.
        if lt_ and "".join(m_.group(0) for m_ in piezas_) != lt_.group("lista"):
            problemas.append(f"deserción: la lista de los tres valores más {cuales} no se lee entera como "
                             f"«departamento (cifra %)» separados por «, » e «y»: «{lt_.group('lista')}»")
        if orden[2][0] == orden[3][0]:
            problemas.append(f"deserción: el tercer valor más {cuales[:-1]} del mapa de R ({orden[2][1]}, {orden[2][0]}) "
                             f"empata con el cuarto ({orden[3][1]}, {orden[3][0]}): «los tres más {cuales}» no está definido")
        if dichos_ != r_:
            problemas.append(f"deserción: la frase da como los tres valores más {cuales} {dichos_} y los tres más "
                             f"{cuales} del mapa de R son {r_}")
        visto_ = sorted((_corto(f_["departamento"]), n(f_["pct"], 2)) for f_ in lista_visto)
        if visto_ != r_:
            problemas.append(f"deserción: la lista de `visto` de los tres más {cuales} es {visto_} y los tres más "
                             f"{cuales} del mapa de R son {r_}")

    if not (len(_gd["valor"]) == len(_gd["etiquetas"]) == _gd["n"] >= 4):
        problemas.append(f"deserción: el mapa de R trae {len(_gd['valor'])} valores y {len(_gd['etiquetas'])} "
                         f"etiquetas y declara {_gd['n']} departamentos (hacen falta los mismos, y 4 o más)")
    else:
        _tres_extremos("altos", _RX_MAYORES + r" (?P<lista>.+?)\. La clase más oscura", _ds["mayores"])
        _tres_extremos("bajos", r"\. Lo más claro, en (?P<lista>.+?\s%\))\.(?:\s|$)", _ds["menores"])
    _za = _ds["clase_alta"]["zonas"]
    _rep = lista_y([f"{ent(k_)} en el {z_}" for z_, k_ in zip(_za["zona"], _za["n"])])
    if not (sum(_za["n"]) == _ds["clase_alta"]["n"] == M["desercion"]["tam"][-1]
            and f"reúne {ent(_ds['clase_alta']['n'])} departamentos repartidos por el país: {_rep}." in DESC_DE1["cap1-desercion"]):
        problemas.append("deserción: el reparto de la clase más oscura por zonas no es el que cuenta R")
    _md = _re4.search(r"reúne (\d+) departamentos repartidos por (\d+) zonas del dibujo, (\d+) de ellos en el " + _ZONAS,
                      ETIQUETA1["cap1-desercion"])
    if not (_md and int(_md.group(1)) == _ds["clase_alta"]["n"] and int(_md.group(2)) == len(_za["zona"])
            and int(_md.group(3)) == _za["n"][0] and _md.group(4) == _za["zona"][0]):
        problemas.append(f"deserción: la etiqueta no reparte la clase más alta como R: «{ETIQUETA1['cap1-desercion']}»")
    # IDEAM: «las más frías/cálidas, n de N, en el ZONA»: la palabra elige la
    # tabla de R y la cifra y la zona tienen que ser las de esa tabla; «donde
    # están las más altas» solo vale para las frías, con la correlación con la
    # altitud negativa.
    _vi = D["visto"]["ideam"]
    # (Ronda 4.) La frase entera es obligatoria —su cola ya no es opcional—, en la
    # etiqueta y en la descripción. Las de MAYOR altitud solo pueden ir con las
    # frías si la temperatura baja con la altura, y su zona tiene que ser la del
    # décimo más alto que cuenta R, y ser mayoría en él.
    _al = _vi["altas"]
    # (Ronda 5.) El umbral, si la frase lo da, se lee y tiene que ser el de la
    # tabla que eligió la palabra («o menos» con las frías, «o más» con las
    # cálidas); y la descripción lo tiene que dar, como el de las cálidas.
    _rx = (r"[Dd]e las (\d+) más (frías|cálidas)(?:, de ([\d.]+) °C o (menos|más))?, (\d+) están en el " + _ZONAS
           + r" del dibujo, donde se concentran las estaciones de (mayor|menor) altitud")
    _ok_ideam = True
    for _txt in (ETIQUETA1["cap1-ideam"], DESC_DE1["cap1-ideam"]):
        _m = _re4.search(_rx, _txt)
        _fria = bool(_m) and _m.group(2) == "frías"
        _tab = None if not _m else (_vi["frias"], _vi["n_frias"], _vi["frias_umbral"]) if _fria else (_vi["calidas"], _vi["n_calidas"], _vi["calidas_umbral"])
        _ok_ideam = _ok_ideam and bool(
            _m and _tab and int(_m.group(1)) == _tab[1] and int(_m.group(5)) == _tab[0]["n"][0]
            and (_m.group(3) is None or (_m.group(3) == n(_tab[2], 1) and _m.group(4) == ("menos" if _fria else "más")))
            and _m.group(6) == _tab[0]["zona"][0] and sum(_tab[0]["n"]) == _tab[1]
            and _m.group(7) == ("mayor" if _fria == (D["colombia"]["geo"]["corr_alt"] < 0) else "menor")
            and _m.group(6) == _al["zonas"]["zona"][0] and _al["zonas"]["n"][0] * 2 > _al["n"] == sum(_al["zonas"]["n"]))
    # (Ronda 5.) La cifra de las de mayor altitud lleva su sustantivo y su zona
    # («29 de las 37 estaciones situadas a 2 560 m o más están en el centro»):
    # sin él se oía «29 de las 37 más frías». Se lee y cada pieza va contra R.
    _rxa = (r"de mayor altitud: (\d+) de las (\d+) estaciones situadas a ([\d\u202f]+) m o más están en el "
            + _ZONAS + r"\.")
    _ma = _re4.search(_rxa, DESC_DE1["cap1-ideam"])
    if not (_ok_ideam and PATRON1["cap1-ideam"] in DESC_DE1["cap1-ideam"]
            and f"De las {ent(_vi['n_frias'])} más frías, de {n(_vi['frias_umbral'], 1)} °C o menos, " in DESC_DE1["cap1-ideam"]
            and _ma and _ma.group(1) == ent(_al["zonas"]["n"][0]) and _ma.group(2) == ent(_al["n"])
            and _ma.group(3) == ent(_al["umbral_m"]) and _ma.group(4) == _al["zonas"]["zona"][0]):
        problemas.append(f"IDEAM: la etiqueta o la descripción no dicen lo que cuenta R de las estaciones extremas: «{ETIQUETA1['cap1-ideam']}»")
    # (Ronda 6.) «La temperatura va de X °C, en C1, a Y °C, en C2»: X y Y se
    # leen y tienen que ser, en ese orden, el mínimo y el máximo de las
    # temperaturas que pinta el mapa de R (`M["ideam"]["marcas"]`), y cada
    # color, el de su punta de la rampa: el de la primera parada con el mínimo
    # y el de la última con el máximo. Con `t_min` y `t_max` cruzadas pasaba.
    import colorsys as _cs6

    def _es_color6(nombre, hexa):
        h_, l_, _s = _cs6.rgb_to_hls(*(int(hexa[i:i + 2], 16) / 255 for i in (1, 3, 5)))
        h_ *= 360
        return {"azul índigo": 225 <= h_ <= 265 and l_ < 0.35,
                "amarillo": 45 <= h_ <= 70 and l_ > 0.5}.get(nombre, False)
    _tmin6, _tmax6 = min(M["ideam"]["marcas"]), max(M["ideam"]["marcas"])
    _mt = _re4.search(r"La temperatura va de (-?\d+(?:\.\d+)?) °C, en ([a-záéíóúñ ]+?), a (-?\d+(?:\.\d+)?) °C, "
                      r"en ([a-záéíóúñ ]+?)\.", DESC_DE1["cap1-ideam"])
    if not (_mt and _tmin6 < _tmax6 and _mt.group(1) == n(_tmin6, 1) and _mt.group(3) == n(_tmax6, 1)
            and _es_color6(_mt.group(2), PALETA_TERMICA[0]) and _es_color6(_mt.group(4), PALETA_TERMICA[-1])):
        _dice6 = (f"va de {_mt.group(1)} °C, en {_mt.group(2)}, a {_mt.group(3)} °C, en {_mt.group(4)}" if _mt
                  else "no dice de dónde a dónde va la temperatura")
        problemas.append(f"IDEAM: la descripción {_dice6}, y el mapa de R va de {n(_tmin6, 1)} °C, en la primera "
                         f"parada de la rampa ({PALETA_TERMICA[0]}), a {n(_tmax6, 1)} °C, en la última "
                         f"({PALETA_TERMICA[-1]})")
    # «Baja» o «sube», con el signo que publica R; la cifra, sin signo.
    _verbo = "baja" if _vi["baja_por_km"] > 0 else "sube"
    if not (abs(_vi["baja_por_km"] + D["colombia"]["geo"]["gradiente"]) < 1e-6
            and f"La temperatura {_verbo} {n(abs(_vi['baja_por_km']), 1)} °C por cada kilómetro" in DESC_DE1["cap1-ideam"]):
        problemas.append(f"IDEAM: la descripción no dice que la temperatura {_verbo} con la altura, como dice R")
    # Las cálidas, con su número.
    if not (f"Las {ent(_vi['n_calidas'])} más cálidas, de" in DESC_DE1["cap1-ideam"]):
        problemas.append("IDEAM: la descripción no da el número de las más cálidas que cuenta R")
    _lc = lista_y([f"{ent(k_)} en el {z_}" for z_, k_ in zip(_vi["calidas"]["zona"], _vi["calidas"]["n"])])
    if not (sum(_vi["calidas"]["n"]) == _vi["n_calidas"] and f"más cálidas, de {n(_vi['calidas_umbral'], 1)} °C o más: {_lc}."
            in DESC_DE1["cap1-ideam"]):
        problemas.append("IDEAM: la descripción no reparte las más cálidas como R")
    # Meuse: el borde que nombran la etiqueta y la descripción es el lado del
    # eje principal donde R encuentra el décimo con más zinc.
    _vm = D["visto"]["meuse"]
    _bordes = set(_re4.findall(r"borde (noroeste|sureste|nordeste|suroeste)", ETIQUETA1["cap1-meuse"] + " " + DESC_DE1["cap1-meuse"]))
    if not (_bordes == {_vm["lado"]} and _vm["top_noroeste"] * 4 >= _vm["top_n"] * 3 and _vm["diagonal"]):
        problemas.append(f"meuse: la frase pone el zinc alto en el borde {sorted(_bordes)} y R, en el {_vm['lado']}")
    # Pinos y Bogotá: el sentido de lo que hace el rectángulo, contra sus cifras.
    _pj = D["puntual_canonico"]["japanesepines"]
    _sentido = "más alto" if _pj["lambda_caja"] > _pj["lambda"] else "más bajo"
    if not (_pj["area_caja"] <= _pj["area"] and f"sale siempre {_sentido} que con la ventana del dato" in resp.get("pinos", "")):
        problemas.append(f"pinos: la respuesta no dice que el rectángulo da un λ̂ {_sentido} que la ventana")
    _sale = "se sale del Distrito" if D["colombia"]["puntual"]["pct_caja_fuera_dc"] > 0 else "cabe en el Distrito"
    if not (_sale in resp.get("bogota", "")):
        problemas.append(f"Bogotá: la respuesta no dice que el rectángulo {_sale} ({n(D['colombia']['puntual']['pct_caja_fuera_dc'])} % fuera)")
    # La lectura de los pinos: las coordenadas de cada pino, rehechas aquí.
    _mp = M["japanesepines"]
    _c = _mp["caja"]; _r = max(_c[2] - _c[0], _c[3] - _c[1])
    _x0, _y0 = _c[0] + (_c[2] - _c[0]) / 2 - _r / 2, _c[1] + (_c[3] - _c[1]) / 2 - _r / 2
    for v_ in ("dato", "caja"):
        _lp = o["pinos"].get(v_, {}).get("lecturas", [])
        _malp = [i for i, t in enumerate(_lp)
                 if not t.startswith(f"Pino {i + 1} de {_mp['n']}, en x = {_mp['pts'][2 * i] / _mp['q'] * _r + _x0:.3f}, "
                                     f"y = {_mp['pts'][2 * i + 1] / _mp['q'] * _r + _y0:.3f}.")]
        if not (len(_lp) == _mp["n"] and not _malp):
            problemas.append(f"pinos ({v_}): {len(_malp)} lecturas no dan las coordenadas de su pino")
    # Los tercios de Bogotá: la frase que se elige, contra las sedes que R cuenta fuera.
    _fs = sum(D["visto"]["bogota"]["fuera_dc"][1:])
    _esp = ("todas dentro del Distrito." if _fs == 0 else "dentro del Distrito salvo una, que cae fuera de él." if _fs == 1
            else f"dentro del Distrito salvo {ent(_fs)}, que caen fuera de él.")
    _mg = D["visto"]["bogota"]["margen_urbano_m"]
    if not (f"acaba {n(abs(_mg), 1)} m {'al norte' if _mg > 0 else 'al sur'} del corte" in DESC_BOGOTA):
        problemas.append("Bogotá: la descripción pone el final del perímetro urbano del otro lado del corte")
    # (Ronda 5.) «Cabe / no cabe entero en ese tercio», leído, contra la
    # cobertura que mide R (el tercio norte de la caja cubre el perímetro) y
    # contra el margen: si cabe, el borde sur del perímetro queda al norte del corte.
    _cb = _re4.search(r"del perímetro urbano, que (no )?cabe entero en ese tercio y acaba", DESC_BOGOTA)
    _cabe_r = D["visto"]["bogota"].get("urbano_en_tercio_norte")
    # (Ronda 6.) El mensaje nombra lo que choca: la frase contra R, o R contra
    # su propio margen (cabe, y el margen no es positivo), con el signo.
    _signo6 = "positivo" if _mg > 0 else "negativo" if _mg < 0 else "cero"
    # (Ronda 7.) El valor crudo, con `:g`: redondeado a un decimal, -0.04 salía
    # «-0.0 m, negativo».
    _mg_crudo = f"{_mg:g}"
    if not _cb:
        problemas.append("Bogotá: la descripción no dice si el perímetro urbano cabe entero en el tercio norte")
    elif not isinstance(_cabe_r, bool):
        problemas.append(f"Bogotá: R no publica `urbano_en_tercio_norte` como verdadero o falso (publica {_cabe_r!r})")
    elif (_cb.group(1) is None) != _cabe_r:
        problemas.append(f"Bogotá: la descripción dice que el perímetro urbano {'no ' if _cb.group(1) else ''}cabe "
                         f"en el tercio norte y R (`urbano_en_tercio_norte`) dice {_cabe_r}")
    elif _cabe_r and not _mg > 0:
        problemas.append(f"Bogotá: R dice que el perímetro urbano cabe en el tercio norte (`urbano_en_tercio_norte` = "
                         f"True), pero su margen al corte (`margen_urbano_m`) es {_mg_crudo} m, {_signo6}: el borde "
                         f"sur del perímetro no queda al norte del corte")
    if not (DESC_BOGOTA.endswith(_esp)):
        problemas.append(f"Bogotá: la descripción de los tercios no dice las {_fs} sedes de fuera del Distrito")
    # Cada pregunta del módulo 2 controla su respuesta (la pone bajo su botón).
    _sin = [k_ for k_, gs in o.get("controla", {}).items() if f"aleatorio-{k_.replace('-ventana', '')}" not in gs]
    if not (len(o.get("controla", {})) == 6 and not _sin):
        problemas.append(f"módulo 2: la pregunta no controla su respuesta en {_sin}")
    return problemas

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

    # --- R2 · T2.3: los bordes de Bogotá, la caja de los pinos y las respuestas --
    bp, mb = D["colombia"]["puntual"], M["bogota"]
    bordes = mb.get("bordes", {})
    exige(set(bordes) == {"urbano", "distrito", "caja"} and all(len(a) >= 8 for v in bordes.values() for a in v[:1]),
          "Bogotá: el mapa no trae los tres bordes de los que habla la prosa")
    exige(bp["lambda_urbana"] > bp["lambda_dc"] > bp["lambda_caja"] > 0 and bp["n_urbana"] <= bp["n_dc"] <= bp["n"],
          "Bogotá: las tres intensidades ya no bajan del perímetro urbano al Distrito y al rectángulo")
    exige(all(abs(c / a - l) < 1e-6 for c, a, l in ((bp["n_urbana"], bp["area_urbana_km2"], bp["lambda_urbana"]),
                                                   (bp["n_dc"], bp["area_dc_km2"], bp["lambda_dc"]),
                                                   (bp["n"], bp["area_caja_km2"], bp["lambda_caja"]))),
          "Bogotá: una intensidad del título no es sus sedes entre su área")
    dentro = mb.get("dentro") or []
    exige(len(dentro) == mb["n"] and set(dentro) <= {0, 1, 2}
          and sum(v == 2 for v in dentro) == bp["n_urbana"] and sum(v >= 1 for v in dentro) == bp["n_dc"],
          "Bogotá: lo que la lectura dice de cada sede no cuadra con las sedes de cada ventana")
    exige(bp["pct_caja_fuera_dc"] > 5, "Bogotá: el rectángulo de las sedes ya no se sale del Distrito y el mapa dice que no es una ventana válida")
    if bordes.get("caja"):
        cj_ = bordes["caja"][0]
        exige(abs(min(cj_[0::2]) - min(mb["pts"][0::2])) <= 1 and abs(max(cj_[0::2]) - max(mb["pts"][0::2])) <= 1
              and abs(min(cj_[1::2]) - min(mb["pts"][1::2])) <= 1 and abs(max(cj_[1::2]) - max(mb["pts"][1::2])) <= 1,
              "Bogotá: el rectángulo dibujado no es el que ciñe a las sedes")
    pj = D["puntual_canonico"]["japanesepines"]
    exige(pj["area_caja"] < pj["area"] and pj["lambda_caja"] > pj["lambda"]
          and abs(pj["n"] / pj["area_caja"] - pj["lambda_caja"]) < 1e-6,
          "pinos: con el rectángulo de los puntos la intensidad ya no sube, o no es sus pinos entre su área")
    faltan = [k for k in ("pinos", "bogota", "nc", "desercion", "meuse", "ideam")
              if f'id="aleatorio-{k}" hidden' not in marcado or f"interruptorAleatorio('{k}')" not in GEOMAPAS_JS]
    exige(not faltan, f"módulo 2: mapas sin su respuesta a «¿qué es aleatorio aquí?», o sin el mando que la enseña: {faltan}")
    # Un getter copiado con `Object.assign` se queda en su primer valor: el
    # mapa dejaría de seguir a su mando. Los registros que se amplían con
    # getters lo hacen con sus descriptores.
    import re as _re2
    congelados = [m_.group(1) for m_ in _re2.finditer(r"Object\.assign\(GEOMAPAS\['([^']+)'\], \{(.*?)\n    \}\);", GEOMAPAS_JS, _re2.S)
                  if _re2.search(r"\bget \w+\(\)", m_.group(2))]
    exige(not congelados, f"mapas cuyo título o cuyas capas se copian con Object.assign y no siguen a su mando: {congelados}")
    exige("GEOMAPA_CUALITATIVA[" not in GEOMAPAS_JS + SIMULADORES_JS,
          "Snow: el capítulo vuelve a escribir en la paleta cualitativa del motor")

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
                     # Las celdas de las bombas (G-20), como capas de líneas del
                     # motor: a trazos las trece y, en la vista de Broad Street,
                     # la suya con borde naranja. Sin las calles no van.
                     "      get capasLineas() {\n"
                     "        const d = GEOMAPAS['cap1-snow'].fuente;\n"
                     "        if (snowModo === 'sinlineas') return [];\n"
                     "        const capas = [{ lineas: d.celdas, color: 'rgba(1, 40, 32, 0.6)', ancho: 1, trazo: [5, 4],\n"
                     "                         cierra: true, etiqueta: 'celda de cada bomba: lo que le queda más cerca' }];\n"
                     "        if (snowModo === 'broad') capas.push({ lineas: [d.celdas[D1.snow.bomba_broad - 1]],\n"
                     "          color: GEOMAPA_ACENTO, ancho: 2.2, cierra: true, etiqueta: 'celda de Broad St' });\n"
                     "        return capas;\n"
                     "      },\n"
                     "      get coloresCategoria() { return COLORES1_SNOW; },\n"
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
    # de oscuro a claro y de frío a cálido —índigo, violeta, magenta, naranja,
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
    + "    const DESC1_PINOS_VENTANA = " + json.dumps(DESC_PINOS_VENTANA, ensure_ascii=False) + ";\n"
    + "    const DESC1_BOGOTA = " + json.dumps(DESC_BOGOTA_V, ensure_ascii=False) + ";\n"
    + M2_JS.replace("__TABLA_PUNTOS__", TABLA_PUNTOS)
    + "    // La etiqueta accesible con el patrón (G-24), en los siete que no la traían.\n"
    + "    const ETIQUETA1 = " + json.dumps(ETIQUETA1, ensure_ascii=False) + ";\n"
    + "    Object.keys(ETIQUETA1).forEach(k => { GEOMAPAS[k].etiqueta = ETIQUETA1[k]; });\n"
    + "    // Lo que se ve en cada estado de los mapas que cambian con un control\n"
      "    // (ver «Describir el mapa» en el ensamblador).\n"
    + "    const DESC1_SNOW = " + json.dumps(_D1_SNOW, ensure_ascii=False) + ";\n"
    + "    const TITULO1_SNOW = " + json.dumps(_T1_SNOW, ensure_ascii=False) + ";\n"
    # EL NARANJA ES DE BROAD STREET EN LAS DOS VISTAS (G-20). La paleta
    # cualitativa del motor reparte sus trece colores por orden, y a la bomba
    # de Broad Street le tocaba el rosa mientras el bermellón iba a otra.
    # Desde R2 · T2.3 el motor admite una lista de colores por mapa
    # (`coloresCategoria`), y esta es la de Snow: la de la casa con tres
    # cambios. La casilla de Broad Street lleva el acento; su rosa pasa a la
    # del bermellón, que deja de usarse; y el ámbar de la primera, que en la
    # leyenda quedaba junto al naranja, pasa al amarillo. La paleta de la
    # casa ya no se toca: los demás mapas la usan tal cual.
    + """    const COLORES1_SNOW = (function () {
      const lista = GEOMAPA_CUALITATIVA.slice();
      const iBroad = D1.snow.bomba_broad - 1, iBermellon = lista.indexOf('#D55E00'), iAmbar = lista.indexOf('#E69F00');
      if (iBermellon >= 0 && iBermellon !== iBroad) lista[iBermellon] = lista[iBroad];
      lista[iBroad] = GEOMAPA_ACENTO;
      if (iAmbar >= 0 && iAmbar !== iBroad) lista[iAmbar] = '#F0E442';
      return lista;
    })();
"""
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
      const mapa = () => raiz.querySelector('[data-geomapa="cap1-snow"]');
      // Las celdas de las bombas y el naranja de Broad Street los pinta el
      // motor desde R2 · T2.3 (`capasLineas` y `coloresCategoria` en el
      // registro del mapa): aquí solo queda repintar al cambiar de vista.
      const pinta = () => { const m = mapa(); if (m && m.__geomapa) m.__geomapa.dibuja(); };
      const lee = () => {
        if (snowModo === 'todas') {
          lectura(raiz, [['bombas', s.n_bombas],
            ['un color por bomba', 'una categoría por bomba: en este mapa cuesta distinguirlas todas de un vistazo'],
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
           // Una semivarianza se lee desde cero, y la clase de distancia va en pasos de retícula.
           scales: { x: { title: { display: true, text: 'clase de distancia (pasos de retícula)' } },
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
          ['su variograma se aparta del teórico de la clase', n5(r.desvio_rel_max) + ' (clase ' + r.lag_desvio_max + ')'],
          ['clases de distancia fuera de la banda', r.lags_fuera_banda + ' de ' + v.lags.length],
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
        pista: 'La fórmula es $n_{\\text{eff}} = n/(1 + (n-1)\\,\\bar{\\rho})$, con $\\bar{\\rho}$ la correlación media entre parejas. Haz la cuenta '
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
        retroAcierto: 'Y lo importante es el techo: mientras la correlación media no cambie, $n_{\\text{eff}}$ tiende a '
          + '$1/\\bar{\\rho}$. Al añadir datos dentro de la misma región la correlación media tiende a una constante y el '
          + 'tamaño efectivo se estanca; al ampliar la región, si la correlación decae con la distancia, la '
          + 'correlación media baja y no hay techo.',
        retroFallo: 'Módulo 5. La respuesta corta: con la correlación media fija hay un techo, y está en $1/\\bar{\\rho}$.'
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
              + 'Cambiar de signo también puede pasar —el capítulo 3 vuelve sobre ello con la falacia ecológica—, pero el único '
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
            retro: 'Estacionariedad es suponer que distintas partes del mapa son repeticiones del mismo '
              + 'mecanismo, y sin ella no hay repetición. Hace falta, pero no basta, y por dos razones distintas. '
              + 'Una es del proceso: hace falta además ergodicidad, que los promedios de una realización '
              + 'converjan a los del proceso cuando la región crece; en la práctica, que la covarianza decaiga '
              + 'con la distancia. La otra es del mapa: para aprovechar la ergodicidad con una sola realización, '
              + 'la región tiene que ser grande frente al alcance de la covarianza. Módulo 6.' },
          { texto: 'Verdadero: los datos hablan por sí solos', correcta: false,
            retro: 'Es un problema de fondo, no un tecnicismo. Módulo 6.' }
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
            retro: 'No depende de que sean árboles. La fuga la pone el reparto de los pliegues, y alcanza a todo método que trate las observaciones como independientes: la mayoría de los de aprendizaje automático lo hace.' }
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
            retro: 'Nada de esto rehabilita la teoría del aire viciado. Lo que dice es que ESTE dato no prueba lo que se le atribuye.' }
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
        retroAcierto: 'Y eso anuncia el capítulo 9: el kriging universal, con la covariable en la media.',
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
        pregunta: 'La I de Moran de la deserción pasa de ' + n5(D1.escala.moran_municipal) + ' entre los '
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
              + 'error de Monte Carlo. Si se separaran más de tres errores conjuntos, habría que averiguar cuál '
              + 'de las dos está mal: cuadrarlas es parte del método.' },
          { texto: 'Con la I de Moran de la deserción.', correcta: false,
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
          { texto: 'spdep y esda cuentan distinto las unidades sin vecinos al calcular la I de Moran.',
            correcta: true,
            retro: n5(D1.escala.moran_municipal) + ' frente a ' + n5(D1.escala.moran_municipal_n_total)
              + '. Se recupera uno desde el otro multiplicando por (n − islas)/n.' },
          { texto: 'Una discrepancia sin explicar y una documentada valen lo mismo si el material las publica.',
            correcta: false,
            retro: 'No: la documentada tiene su causa dicha y está en la lista de las conocidas; la que no está '
              + 'en la lista es un error hasta que se explique. Ésa es la diferencia entre material didáctico y un error.' },
          { texto: 'Las discrepancias vienen de que GDAL y GEOS son distintos en cada lenguaje.', correcta: false,
            retro: 'GDAL y GEOS son las mismas bibliotecas en los dos lenguajes, no una por lenguaje. Las dos '
              + 'discrepancias de este módulo están en la capa de arriba. Donde R sí puede usar otra biblioteca '
              + 'es con longitud y latitud, que sf opera con s2. Módulo 8.' }
        ],
        retroAcierto: 'Ante una diferencia, la primera pregunta es «¿estamos midiendo lo mismo?».',
        retroFallo: 'Las dos ciertas son la del tipo de la CAPA frente al de cada rasgo y la de las unidades sin vecinos en la I de Moran. Módulo 9.'
      },
      {
        tipo: 'opcion', modulo: 10,
        pregunta: '¿Verdadero o falso? Siempre que el dato tenga coordenadas, la validación cruzada por bloques '
          + 'espaciales es la correcta.',
        pista: 'Depende de a qué pregunta quieras que responda el modelo.',
        opciones: [
          { texto: 'Falso: depende de la pregunta', correcta: true,
            retro: 'La de bloques responde a «¿cuánto me fío en una zona donde no he medido?». Si la pregunta '
              + 'fuera por sitios que se parecen a los de la muestra, como los huecos entre estaciones que ya '
              + 'existen, la aleatoria es la que más se le acerca.' },
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
# R3 · T3.2: la notación del capítulo (D6), leída del documento ensamblado
# =====================================================================
# Cuatro convenciones que el capítulo rompía sin que ninguna cifra se
# moviera: la W que era a la vez ventana y matriz de pesos, el «rezago» que
# era a la vez la media de los vecinos y una distancia del variograma, «el
# I de Moran» junto a «la I», y un glosario que no recogía la mitad de los
# símbolos y le daba a ρ un sentido que el capítulo no usa. Las guardas leen
# `doc` —el HTML ya ensamblado, plantilla, cuestionario y glosario
# incluidos— y no una copia de las frases (la lección de R2).
_FORMULA_PROSA = re.compile(r"\\\((.+?)\\\)|\$\$(.+?)\$\$", re.S)
_FORMULA_QUIZ = re.compile(r"\$([^$\n]+?)\$")
# Una W que no es parte de una palabra. Detrás puede ir la y o la z del
# rezago: «Wy» es W por y, y es justo lo que se busca. La negrita —con o sin
# llaves, \mathbf, \boldsymbol o \bm— se quita antes de buscar.
_W_SIN_NEGRITA = re.compile(r"(?<![A-Za-z\\{])W(?![a-xA-Z])")
_W_NEGRITA = re.compile(r"\\(?:mathbf|boldsymbol|bm)\s*(?:\{\s*W\s*\}|W(?![A-Za-z]))")
# El papel de una W, leído en la propia fórmula: de matriz si multiplica o se
# traspone (Wy, Wz, W^\top, W^2, W_{ij}, W + …); de ventana si se mide o se
# integra o contiene (|W|, \int_W, W \subset, \in W, \cap W).
_W_MATRIZ = re.compile(r"(?<![A-Za-z\\{_])W\s*(?:[yz](?![A-Za-z])|\^|_\{?[ij]|\\top|[+\-]\s*\\?[A-Za-z])")
_W_VENTANA = re.compile(r"\|W\||\\int_\{?W|W\s*\\subset|\\in\s*W\b|\\cap\s*W\b|\\subset\s*W\b")
# Y si la fórmula es una W pelada, la frase que la contiene: una frase que
# habla de pesos, vecinos, adyacencia o rezago la está usando de matriz.
_FRASE_MATRIZ = re.compile(r"matri|peso|vecin|adyacen|rezago", re.I)
_OTRO_CAP = re.compile(r"\bcaps?\.\s*\d")
# Fin de frase: punto, punto y coma, cierre de interrogación o exclamación,
# salvo el punto de «cap.» y «caps.».
_FIN_FRASE = re.compile(r"(?<!\bcap)(?<!caps)[.;!?](?:\s|$)")
_REZAGO = re.compile(r"\brezagos?\b(?!\s+(?:espacial(?:es)?|de distancia)\b)", re.I)
# «el I» en masculino, venga detrás lo que venga: «el I de Moran», «el I
# departamental», «este I». La I tiene que ir en mayúscula y suelta.
_EL_I = re.compile(r"\b(?:[Ee]l|[Dd]el|[Aa]l|[Uu]n|[Ee]ste|[Ee]se|[Aa]quel|[Oo]tro|[Mm]ismo|[Pp]rimer|"
                   r"[Úú]ltimo)\s+I\b(?![-_^=(\w]|\.\w)")
# Un comentario de JavaScript, también a mitad de línea (no el «//» de una URL).
_COMENTARIO_JS = re.compile(r"(^|[\s;,{}()\]])//.*$", re.M)



def _sin_espacios(s: str) -> str:
    """Una fórmula sin espacios ni llaves: «\\hat{\\lambda}» y «\\hat\\lambda» son el mismo símbolo."""
    return re.sub(r"[\s{}]", "", s)


def _texto_plano(s: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", s))


# Lo que el glosario tiene que traer si el capítulo lo escribe en una
# fórmula: (símbolo del glosario, cómo se reconoce en las fórmulas, nombre).
# Los detectores leen las fórmulas sin espacios ni llaves.
_GLOSARIO_EXIGE = [
    ("W", lambda f: "|W|" in f or "\\int_W" in f, "la ventana W"),
    ("|W|", lambda f: "|W|" in f, "el área de la ventana |W|"),
    ("n", lambda f: re.search(r"(?<![A-Za-z\\])n(?![A-Za-z])", f), "n"),
    ("N", lambda f: "s_N" in f, "N, el número aleatorio de puntos"),
    ("N(B)", lambda f: "N(B" in f, "N(B)"),
    ("\\hat\\lambda", lambda f: "\\hat\\lambda" in f, "λ̂"),
    ("d_i", lambda f: re.search(r"(?<![A-Za-z\\])d_i(?![A-Za-z])", f), "d_i"),
    ("G(r)", lambda f: "G(r)" in f, "G(r)"),
    ("\\rho(h)", lambda f: "\\rho(h" in f, "ρ(h)"),
    ("\\rho_ij", lambda f: "\\rho_ij" in f, "ρ_ij"),
    ("\\bar\\rho", lambda f: "\\bar\\rho" in f, "ρ̄"),
    ("\\phi", lambda f: "\\phi" in f, "φ"),
    ("\\sigma^2", lambda f: "\\sigma^2" in f, "σ²"),
    ("E[I]", lambda f: "E[I]" in f, "E[I]"),
    ("S_0", lambda f: "S_0" in f, "S_0"),
    ("w_ij", lambda f: "w_ij" in f, "w_ij"),
    ("n_\\texteff", lambda f: "n_\\texteff" in f, "n_eff"),
    ("\\mathbfW", lambda f: "\\mathbfW" in f, "la matriz de pesos en negrita"),
    ("m(s)", lambda f: "m(s" in f, "m(s), la media que cambia de sitio"),
]


def _papel_w(f: str, antes: str, despues: str) -> str | None:
    """«matriz», «ventana», «otro capítulo» o None si la fórmula no lleva una W sin negrita.

    Se decide por el papel del símbolo, no por la palabra «ventana» cerca: primero
    lo que hace la W dentro de la fórmula, y solo si es una W pelada, la frase
    que la contiene (no los 140 caracteres de antes, que alcanzaban a la frase
    anterior: «Elegir ventana … En los datos de área, la matriz de pesos \(W\)»
    pasaba).
    """
    g = _W_NEGRITA.sub("", f)
    if not _W_SIN_NEGRITA.search(g):
        return None
    frase = _FIN_FRASE.split(antes)[-1] + " ⟨W⟩ " + _FIN_FRASE.split(despues)[0]
    if _OTRO_CAP.search(frase):
        return "otro capítulo"      # «En los caps. 6 y 7 se escribe \(W\)»
    if _W_MATRIZ.search(g):
        return "matriz"
    if _W_VENTANA.search(g):
        return "ventana"
    return "matriz" if _FRASE_MATRIZ.search(frase) else "ventana"


def guardas_de_notacion(doc: str) -> list[str]:
    """W, rezago, «la I de Moran» y el glosario, contra el documento ensamblado."""
    problemas = []
    fin_marcado = doc.rfind("\n  <script>")
    fin_marcado = fin_marcado if fin_marcado > 0 else len(doc)
    marcado = re.sub(r"<pre\b.*?</pre>", " ", doc[:fin_marcado], flags=re.S)

    # Las fórmulas del capítulo —prosa y cuestionario—, cada una con el texto
    # que la rodea: (fórmula, antes, después). Y aparte, las del glosario.
    def con_contexto(texto, regex, lado):
        return [(m.group(1) or (m.group(2) if regex.groups > 1 else "") or "",
                 _texto_plano(texto[max(0, m.start() - lado):m.start()]),
                 _texto_plano(texto[m.end():m.end() + lado]))
                for m in regex.finditer(texto)]
    cap = con_contexto(marcado, _FORMULA_PROSA, 400)
    i0 = doc.find("AUTOEVALUACIONES['cap1-diagnostica']")
    i1 = doc.find("\n    ];\n", doc.find("AUTOEVALUACIONES['cap1'] ="))
    if i0 >= 0 and i1 > i0:
        cap += con_contexto(doc[i0:i1].replace("\\\\", "\\"), _FORMULA_QUIZ, 200)
    g = re.search(r"GLOSARIOS\['cap1-notacion'\] = (\{.*?\});\n", doc)
    try:
        filas = json.loads(g.group(1))["filas"] if g else []
    except (ValueError, KeyError):
        filas = []
    glo = []
    for f in filas:
        glo.append((f.get("simbolo", ""), "", f.get("nombre", "")))
        glo += con_contexto(f.get("nombre", ""), _FORMULA_PROSA, 400)

    # 1 · Una W sin negrita solo es la ventana (o la de otro capítulo, dicha
    # como tal). La matriz de pesos de este capítulo es \mathbf{W}.
    malas_w = [f for f, antes, despues in cap + glo if _papel_w(f, antes, despues) == "matriz"]
    if malas_w:
        problemas.append(f"notación: una W sin negrita hace de matriz de pesos, que en este capítulo es "
                         f"\\mathbf{{W}}: {malas_w[:3]}")
    # 2 · La matriz de pesos, en negrita en la prosa (el recuadro de Moran),
    # no solo en el glosario.
    corpus = [_sin_espacios(f) for f, _, _ in cap]
    if not any(_W_NEGRITA.search(f) for f, _, _ in cap):
        problemas.append("notación: la prosa del capítulo ya no escribe la matriz de pesos como "
                         "\\mathbf{W}")

    # 3 · «Rezago» solo como «rezago espacial» o «rezago de distancia». Los
    # comentarios del JavaScript —también los de mitad de línea— no los ve
    # nadie y se quitan; el marcado se lee entero.
    visible = doc[:fin_marcado] + _COMENTARIO_JS.sub(r"\1", doc[fin_marcado:])
    rez = [visible[max(0, m.start() - 40):m.end() + 25].replace("\n", " ")
           for m in _REZAGO.finditer(visible)]
    if rez:
        problemas.append(f"notación: «rezago» que no es «rezago espacial» ni «rezago de distancia» "
                         f"({len(rez)}): {rez[:3]}")

    # 4 · «la I de Moran», en femenino, en todo el documento.
    eles = [doc[max(0, m.start() - 30):m.end() + 25].replace("\n", " ") for m in _EL_I.finditer(doc)]
    if eles:
        problemas.append(f"notación: vuelve «el I» de Moran, en masculino ({len(eles)}): {eles[:3]}")

    # 5 · El glosario trae una fila para cada símbolo de D6 que el capítulo
    # escribe en una fórmula, y para la sigla CSR. Sin glosario en el
    # documento, faltan todas. La fila de ρ, además, dice lo que ρ es aquí:
    # cita sus tres marcas, dice «correlación» y no lo niega.
    en_glosario = {_sin_espacios(f.get("simbolo", "")) for f in filas}
    exige = [(s, any(usa(f) for f in corpus), nombre) for s, usa, nombre in _GLOSARIO_EXIGE]
    exige.append(("\\textCSR", "CSR" in _texto_plano(marcado), "la sigla CSR"))
    for simbolo, usado, nombre in exige:
        if usado and simbolo not in en_glosario:
            problemas.append(f"notación: el capítulo escribe {nombre} y el glosario no le da fila")
    rho = next((f for f in filas if _sin_espacios(f.get("simbolo", "")) == "\\rho"), None)
    nom = rho.get("nombre", "") if rho else ""
    if not (all(x in _sin_espacios(nom) for x in ("\\rho(h)", "\\rho_ij", "\\bar\\rho"))
            and "correlación" in nom
            and not re.search(r"\bno\s+(?:es|son|sea)\b[^.]{0,40}correlaci", nom)):
        problemas.append("notación: la fila de ρ del glosario no dice que en este capítulo ρ es una "
                         "correlación, con sus tres marcas")
    return problemas


# =====================================================================
# R3 · T3.3 · Los paneles de deducción y la ergodicidad
#
# Las guardas leen el DOCUMENTO ENSAMBLADO, no una copia de la frase (la
# lección de R2): que cada panel exista una vez, que su botón lo nombre, que
# arranque oculto y que su cierre lleve la cifra del JSON en la que acaba. Y
# lo que la prosa de los módulos 3 y 6 afirma con esas cifras.
# =====================================================================
# id del panel -> (qué deduce, [(campo, texto que tiene que estar en su cierre)])
def _paneles_t33() -> dict[str, tuple[str, list[tuple[str, str]]]]:
    pj = pc["japanesepines"]
    return {
        "der-vecino-csr": ("E[d̄] y el error típico de Clark-Evans", [
            ("puntual_canonico.japanesepines.nn_ee", n(pj["nn_ee"])),
            ("puntual_canonico.japanesepines.ce_z", n(pj["ce_z"])),
            ("puntual_canonico.japanesepines.ce_p", n(pj["ce_p"]))]),
        "der-esperanza-moran": ("E[I] = −1/(n − 1)", [
            ("tobler.ideam.esperado", n(tb["ideam"]["esperado"], 6))]),
        "der-s2-esperada": ("E[s²]", [
            ("inferencia.rejilla[phi=4].s2_esperada", n(r4["s2_esperada"]))]),
        "der-ergodicidad": ("la ergodicidad de la media", [
            ("una_realizacion.sd_exacta_de_la_media", n(ur["sd_exacta_de_la_media"]))]),
    }


def _modulo(marcado: str, num: int) -> str:
    i = marcado.find(f'<template id="module-{num}">')
    j = marcado.find("</template>", i)
    return marcado[i:j] if i >= 0 and j > i else ""


def guardas_de_t33(doc: str) -> list[str]:
    problemas = []
    fin = doc.rfind("\n  <script>")
    marcado = doc[:fin if fin > 0 else len(doc)]
    for pid, (que, cifras) in _paneles_t33().items():
        abre = f'<div class="derivacion-panel" id="{pid}" hidden>'
        if marcado.count(f'id="{pid}"') != 1 or marcado.count(abre) != 1:
            problemas.append(f"T3.3: el panel {pid} ({que}) no está una sola vez, oculto, en el documento")
            continue
        if marcado.count(f'aria-expanded="false" aria-controls="{pid}"') != 1:
            problemas.append(f"T3.3: ningún botón de derivación nombra el panel {pid} en aria-controls")
        cuerpo = marcado[marcado.index(abre):]
        m = re.search(r'<p class="derivacion-resultado">(.*?)</p>', cuerpo, re.S)
        cierre = m.group(1) if m and m.start() < cuerpo.find("</ol>") + 400 else ""
        faltan = [campo for campo, txt in cifras if txt not in cierre]
        if faltan:
            problemas.append(f"T3.3: el cierre del panel {pid} ({que}) no lleva la cifra en que acaba: {faltan}")
    # El módulo 6 nombra la ergodicidad en su prosa: no en un comentario, ni en
    # el id del panel (der-ergodicidad), que es marcado y no se lee.
    m6 = _texto_plano(re.sub(r"<!--.*?-->", " ", _modulo(marcado, 6), flags=re.S))
    if "ergodicidad" not in m6.lower():
        problemas.append("T3.3: el módulo 6 no dice «ergodicidad»: con una realización la estacionariedad "
                         "sola no basta para estimar")
    # La columna «Régimen» se lee de la prueba: p frente a alfa, y el signo de z.
    m3 = _modulo(marcado, 3)
    for k in ("redwood", "japanesepines", "cells"):
        f = pc[k]
        esperado = ("Compatible con el azar" if f["ce_p"] >= ALFA
                    else "Agregado" if f["ce_z"] < 0 else "Regular")
        fila = re.search(rf'<th scope="row">{re.escape(f["nombre"])}</th>(.*?)</tr>', m3, re.S)
        celdas = re.findall(r"<td>(.*?)</td>", fila.group(1), re.S) if fila else []
        if not celdas or celdas[-1].strip() != esperado:
            problemas.append(f"T3.3: la tabla de Clark-Evans rotula {f['nombre']} como "
                             f"«{celdas[-1].strip() if celdas else '—'}» y la prueba "
                             f"(z = {f['ce_z']}, p = {f['ce_p']}, alfa = {ALFA}) dice «{esperado}»")
    # La nota del borde: con Donnelly el p de los pinos SUBE y los otros dos
    # siguen por debajo de alfa.
    if not (pc["japanesepines"]["ce_p_donnelly"] > pc["japanesepines"]["ce_p"]
            and pc["redwood"]["ce_p_donnelly"] < ALFA and pc["cells"]["ce_p_donnelly"] < ALFA):
        problemas.append("T3.3: con Donnelly el p de los pinos ya no sube, o las secuoyas o las células ya no "
                         "quedan por debajo de alfa, y la nota del borde lo dice")
    # El cierre del módulo 6: la medida y la exacta difieren por ruido; al
    # rellenar la desviación típica ya está en su límite y al ampliar cae.
    if ur["sd_medida_a_emc"] >= 4:
        problemas.append(f"T3.3: la sd medida de las medias queda a {ur['sd_medida_a_emc']} errores de Monte "
                         f"Carlo de la exacta, y el panel lo llama ruido de la simulación")
    if not (0 < erg["sd_media_relleno_ultima"] - erg["sd_media_relleno_limite"]
            < 1e-3 * erg["sd_media_relleno_limite"]
            and erg["sd_media_ampliacion_ultima"] < ur["sd_exacta_de_la_media"]):
        problemas.append("T3.3: al rellenar la sd de la media ya no está en su límite, o al ampliar no cae: "
                         "el panel de la ergodicidad dice que sí")
    if erg["k_ultima"] != tc["rejilla"][-1]["k"]:
        problemas.append("T3.3: la última fila de la ergodicidad no es la última de la tabla del techo")

    # --- Ronda 2 (🟡 8 de la verificación): QUÉ cifra hay en cada sitio del
    # texto. Las de arriba atan campos del JSON entre sí; estas leen el texto.
    def panel(pid):
        i = marcado.find(f'id="{pid}"')
        j = marcado.find('<p class="derivacion-resultado">', i)
        k = marcado.find("</p>", j)
        return (marcado[i:j], marcado[j:k]) if i >= 0 and j > i and k > j else ("", "")

    # A · las celdas z y p de cada fila de la tabla de Clark-Evans.
    for k in ("redwood", "japanesepines", "cells"):
        f = pc[k]
        fila = re.search(rf'<th scope="row">{re.escape(f["nombre"])}</th>(.*?)</tr>', m3, re.S)
        celdas = [c.strip() for c in re.findall(r"<td>(.*?)</td>", fila.group(1), re.S)] if fila else []
        if len(celdas) < 7 or celdas[4] != n(f["ce_z"]) or celdas[5] != p_ce(f):
            problemas.append(f"T3.3r2: la tabla de Clark-Evans no da en la fila de {f['nombre']} la z "
                             f"({n(f['ce_z'])}) y el p ({p_ce(f)}) de la prueba: {celdas[4:6]}")
    # J · el pie de la tabla dice la corrección que la tabla publica.
    pie = re.search(r"<caption>Los tres regímenes de un patrón puntual(.*?)</caption>", m3, re.S)
    pie = " ".join(pie.group(1).split()) if pie else ""
    if cep["correccion"] != "none" or "sin corrección de borde" not in pie or "Donnelly" in pie:
        problemas.append("T3.3r2: el pie de la tabla de Clark-Evans no dice «sin corrección de borde», que es "
                         f"la prueba que publica (correccion = {cep['correccion']})")
    # G · la nota del borde da la z y el p de Donnelly de los pinos, y la z de
    # Donnelly de las otras dos.
    pj, prw, pce_ = pc["japanesepines"], pc["redwood"], pc["cells"]
    nota = " ".join(m3.split())
    if not (re.search(rf"de los pinos baja a {re.escape(n(pj['ce_z_donnelly']))} y su valor p sube a "
                      rf"{re.escape(n(pj['ce_p_donnelly']))},", nota)
            and re.search(rf"con \\\(z\\\) de {re.escape(n(prw['ce_z_donnelly']))} y "
                          rf"{re.escape(n(pce_['ce_z_donnelly']))}\.", nota)):
        problemas.append("T3.3r2: la nota del borde no da la z y el p de Donnelly de los pinos, o la z de "
                         "Donnelly de las secuoyas y las células")
    # E · el cierre de E[I]: −1/(n−1) con n, y con n′ delante −n′/(n(n−1)).
    _, cierre_ei = panel("der-esperanza-moran")
    if "\\(-n'/(n(n-1))\\)" not in cierre_ei or "n'-1" in cierre_ei.replace(" ", ""):
        problemas.append("T3.3r2: el cierre de E[I] ya no dice que con n′ delante la cuenta da −n′/(n(n−1)), "
                         "lo que dice el párrafo de las islas")
    # K · el cierre de E[s²]: la esperada y la media de las réplicas, cada una en su sitio.
    _, cierre_s2 = panel("der-s2-esperada")
    c2 = " ".join(cierre_s2.split())
    if (f"\\mathbb{{E}}[s^2] = {n(r4['s2_esperada'])}\\)" not in c2
            or f"réplicas es {n(r4['s2_medida'])}." not in c2):
        problemas.append("T3.3r2: el cierre de E[s²] no da s2_esperada como esperanza y s2_medida como media "
                         "de las réplicas")
    # B · el relleno: el límite, el valor con n_ultima y el «no bajará de» el límite.
    pasos_erg, _ = panel("der-ergodicidad")
    pe = " ".join(pasos_erg.split())
    lim, ult = n(erg["sd_media_relleno_limite"]), n(erg["sd_media_relleno_ultima"])
    if not (f"= {lim}\\): con" in pe and f"ya vale {ult}," in pe and f"no bajará de {lim}." in pe):
        problemas.append(f"T3.3r2: el panel de la ergodicidad no dice el límite del relleno ({lim}), el valor "
                         f"con {erg['n_ultima']} observaciones ({ult}) y que no bajará del límite, en ese orden")
    # H · la sd de la ampliación vive solo en el paso 3 del panel; la definición
    # cita la sd de las medias del proceso de arriba.
    m6t = _modulo(marcado, 6)
    li = re.search(r"<li><strong>Ergodicidad:</strong>(.*?)</li>", m6t, re.S)
    li = li.group(1) if li else ""
    amp = n(erg["sd_media_ampliacion_ultima"])
    if (n(ur["sd_de_las_medias"]) not in li or amp in li
            or m6t.count(amp) != pasos_erg.count(amp) or pasos_erg.count(amp) != 1):
        problemas.append("T3.3r2: la definición de ergodicidad no cita la sd de las medias del proceso de "
                         "arriba, o la sd de la ampliación aparece fuera del paso 3 del panel")
    return problemas


# =====================================================================
# R3 · T3.4 · La crónica de producción, fuera (D7), y las duraciones medidas
#
# Dos guardas, y las dos leen el DOCUMENTO ENSAMBLADO:
#
#   · `cronica_visible()` busca en lo que el estudiante lee —la prosa de los
#     doce módulos sin comentarios ni bloques de código, y las cadenas del
#     JavaScript que acaban en pantalla: preguntas, opciones, pistas,
#     retroalimentaciones y lecturas— las palabras de la producción del
#     material: «auditor», «ensamblador», «generador» y «JSON». El generador
#     de números aleatorios es otra cosa y se queda: el módulo 4 lo nombra
#     para decir que la incertidumbre que pesa no es la suya. «GeoJSON» es un
#     formato y la frontera de palabra lo deja pasar; `versiones.json`, en
#     minúscula, es el nombre de un archivo. Quedan fuera las cadenas de los
#     avisos para quien depura —`console.…(…)`, `mal.push(…)`, `throw new
#     Error(…)`—, que no ve el estudiante.
#   · `guardas_de_t34()` compara además la duración que la barra declara para
#     cada módulo con la que mide `mide_duraciones_cap1.py` sobre este mismo
#     documento, y para si se sale de ±15 % (el criterio del plan).
# =====================================================================
# Ronda 2 de la verificación: sin distinguir mayúsculas («Auditor aparte.» a
# principio de frase se colaba, V-04); con las otras formas de la misma
# crónica —«ensamblado», «auditoría», «versión anterior», «primera versión»
# (V-09)—; y lo legítimo se deja pasar por CONTEXTO, no por mayúscula: el
# generador de números (pseudo)aleatorios (V-08), y «json» pegado a una letra,
# un punto o una barra, que es «GeoJSON» o el nombre de un archivo.
_CRONICA = re.compile(r"\bauditor(?:es|ía|ías)?\b|\bensamblad(?:or|ores|o)\b"
                      r"|\bgenerador(?:es)?\b(?!\s+de\s+números\s+(?:pseudo)?aleatorios)"
                      r"|(?<![\w./-])json\b"
                      r"|\b(?:primera|anterior)\s+versión\b|\bversión\s+anterior\b", re.I)
# Los atributos que también se leen (o se oyen, con un lector de pantalla), V-05.
_ATRIBUTOS_LEIDOS = re.compile(r'\b(?:aria-label|title|alt|placeholder)="([^"]*)"')
_AVISOS_JS = ("console.", "mal.push(", "throw new Error(")


def _sin_avisos(js: str) -> str:
    """El JavaScript sin las llamadas cuyos textos solo ve quien depura."""
    trozos, i = [], 0
    while True:
        cand = [(js.find(p, i), p) for p in _AVISOS_JS]
        cand = [(j, p) for j, p in cand if j >= 0]
        if not cand:
            trozos.append(js[i:])
            return "".join(trozos)
        j, _ = min(cand)
        trozos.append(js[i:j])
        k = js.find("(", j)
        prof, comilla, m = 0, None, k
        while 0 <= m < len(js):
            c = js[m]
            if comilla:
                if c == "\\":
                    m += 2
                    continue
                if c == comilla:
                    comilla = None
            elif c in "'\"`":
                comilla = c
            elif c == "(":
                prof += 1
            elif c == ")":
                prof -= 1
                if prof == 0:
                    break
            m += 1
        i = m + 1 if m > 0 else len(js)


def _plano(s: str) -> str:
    """Sin etiquetas y DESPUÉS sin entidades: al revés, un «&lt;» de una fórmula
    se volvería «<» y se comería el texto hasta el siguiente «>»."""
    return " ".join(html.unescape(re.sub(r"<[^>]+>", " ", s)).split())


def cronica_visible(doc: str) -> list[str]:
    """Cada aparición de la crónica de producción en lo que el estudiante lee."""
    fin = doc.rfind("\n  <script>")
    ini = doc.find('<template id="module-1">')
    marcado = doc[ini:fin] if 0 <= ini < fin else ""
    t = re.sub(r"<!--.*?-->", " ", marcado, flags=re.S)
    t = re.sub(r"<pre\b.*?</pre>", " ", t, flags=re.S)
    t = re.sub(r"<(script|style)\b.*?</\1>", " ", t, flags=re.S)
    piezas = [("la prosa", _plano(t))]
    piezas += [("un atributo leído", _plano(v)) for v in _ATRIBUTOS_LEIDOS.findall(t)]
    js = re.sub(r"/\*.*?\*/", " ", doc[fin:], flags=re.S)
    js = _COMENTARIO_JS.sub(r"\1", js)
    js = _sin_avisos(js)
    for lit in re.findall(r"'(?:[^'\\\n]|\\.)*'|\"(?:[^\"\\\n]|\\.)*\"|`(?:[^`\\]|\\.)*`", js):
        piezas.append(("el JavaScript", _plano(lit[1:-1])))
    return [f"{donde}: «…{texto[max(0, m.start() - 50):m.end() + 30]}…»"
            for donde, texto in piezas for m in _CRONICA.finditer(texto)]


def guardas_de_t34(doc: str) -> list[str]:
    problemas = []
    for h in cronica_visible(doc):
        problemas.append(f"T3.4: crónica de producción en lo que lee el estudiante, {h}")
    # Medir no puede reventar: una excepción aquí se llevaría por delante el
    # informe de todas las guardas anteriores (la lección de T1.3.i).
    try:
        medidas = mide_duraciones_cap1.mide(doc)
        decl = mide_duraciones_cap1.declaradas(doc)
    except (SystemExit, Exception) as ex:   # noqa: BLE001
        problemas.append(f"T3.4: no se pueden medir las duraciones del documento: {ex}")
        return problemas
    if len(decl) != len(medidas):
        problemas.append(f"T3.4: la barra declara {len(decl)} duraciones para {len(medidas)} módulos")
    for e, d in zip(medidas, decl):
        med = e["min_principal"]
        if abs(d - med) > mide_duraciones_cap1.TOLERANCIA * med:
            problemas.append(f"T3.4: la duración declarada del módulo {e['modulo']} ({d} min) se sale de "
                             f"±15 % de la medida ({med:.1f} min, mide_duraciones_cap1.py)")
    return problemas


# =====================================================================
# R3 · T3.5 (D9, H-07): el entorno y el extracto
# =====================================================================
# Los bloques que se EJECUTAN (los mismos que lee verifica_bloques.py: la
# clase exacta, sin «arranque»).
_BLOQUE_EJECUTABLE = re.compile(r'<pre><code class="language-(r|python)">(.*?)</code></pre>', re.S)
_TODO_BLOQUE = re.compile(r'<pre><code class="language-[^"]*">(.*?)</code></pre>', re.S)
_R_BASE = {"base", "stats", "utils", "graphics", "grDevices", "methods", "datasets", "tools", "grid",
           "parallel", "splines", "stats4", "tcltk", "compiler"}
# El nombre con que se importa un módulo y el que pide pip. Un import que no
# esté aquí PARA el ensamblado: la orden publicada no se adivina.
_PIP = {"geopandas": "geopandas", "shapely": "shapely", "pandas": "pandas", "numpy": "numpy",
        "scipy": "scipy", "libpysal": "libpysal", "esda": "esda", "pointpats": "pointpats"}
# Lo que no viaja al sitio y por eso ningún bloque puede leer. Ronda 2 (V-02):
# cualquier ruta de `datos/` que no sea `entrega/datos/`, no solo `procesado`;
# y se mira el código SIN sus comentarios, que pueden nombrarlo (V-F).
_NO_VIAJA = (re.compile(r"(?<!entrega/)\bdatos/"), re.compile(r"precalculo/"),
             re.compile(r"\bsource\("), re.compile(r"carga_municipios"),
             re.compile(r"versiones\.json"))
# Cargar un paquete de R: library(), require() y requireNamespace(). Ronda 2
# (V-07): con `character.only = TRUE` o sin comillas en requireNamespace() el
# nombre puede ser una variable, y entonces la orden de instalación no lo
# sabría: se exige un literal entre comillas.
_CARGA_R = re.compile(r'\b(library|require|requireNamespace)\(([^()]*)\)')
_RUTA_DATOS = re.compile(r'entrega/datos/[\w.-]+')


def _sin_comentarios(codigo: str) -> str:
    return "\n".join(l for l in codigo.splitlines() if not l.lstrip().startswith("#"))


def paquetes_de_los_bloques(doc: str) -> tuple[list[str], list[str]]:
    """Los paquetes de R y los módulos de Python que cargan los bloques, en el
    orden en que aparecen por primera vez."""
    r, py = [], []
    for lang, cuerpo in _BLOQUE_EJECUTABLE.findall(doc):
        c = _sin_comentarios(html.unescape(cuerpo))
        if lang == "r":
            hallados = []
            for m in _CARGA_R.finditer(c):
                args = [x.strip() for x in m.group(2).split(",")]
                lit = re.fullmatch(r'["\']([A-Za-z][\w.]*)["\']', args[0])
                desnudo = re.fullmatch(r'[A-Za-z][\w.]*', args[0])
                calculado = any(re.match(r"character\.only\s*=\s*(TRUE|T)\b", x) for x in args[1:])
                if lit:
                    hallados.append((m.start(), lit.group(1)))
                elif desnudo and not calculado and m.group(1) != "requireNamespace":
                    hallados.append((m.start(), args[0]))
                else:
                    sys.exit(f"PARADO: un bloque carga un paquete por un nombre calculado "
                             f"({m.group(0)[:60]}): la orden de instalación no puede saber cuál es")
            for m in re.finditer(r'\bpackage\s*=\s*"([A-Za-z][\w.]*)"|\b([A-Za-z][\w.]*)::', c):
                hallados.append((m.start(), next(g for g in m.groups() if g)))
            for _, p in sorted(hallados):
                if p not in _R_BASE and p not in r:
                    r.append(p)
            continue
        for l in c.splitlines():
            de = re.match(r'\s*from\s+([\w.]+)\s+import\b', l)
            im = re.match(r'\s*import\s+(.+)', l)
            nombres = [de.group(1)] if de else (
                [x.strip().split(" as ")[0] for x in im.group(1).split(",")] if im else [])
            for x in nombres:
                top = x.split(".")[0].strip()
                if top and top not in sys.stdlib_module_names and top not in py:
                    py.append(top)
    return r, py


def _modulos_del_doc(doc: str) -> list[tuple[int, str]]:
    return [(int(m.group(1)), m.group(2)) for m in
            re.finditer(r'<template id="module-(\d+)">(.*?)</template>', doc, re.S)]


def _y(xs: list[str]) -> str:
    return xs[0] if len(xs) == 1 else ", ".join(xs[:-1]) + " y " + xs[-1]


ANCHO_TELEFONO = 24


def completa_entorno(doc: str) -> str:
    """Rellena las marcas del recuadro del módulo 8 desde los bloques ya ensamblados."""
    r, py = paquetes_de_los_bloques(doc)
    raros = [m for m in py if m not in _PIP]
    if raros:
        sys.exit(f"PARADO: los bloques importan {raros}, que no tienen nombre de pip declarado en _PIP")
    # El vector y la orden de pip, partidos a ANCHO_TELEFONO columnas: a 375 px
    # caben 24 caracteres en un bloque del recuadro abierto (medido en la
    # ronda 2, V-06: 247 px a 8.4 px por carácter, menos 42 de relleno), y
    # una línea más larga obliga a desplazar el bloque de lado.
    vector, actual = [], "paq <- c("
    for k, p in enumerate(r):
        pieza = f'"{p}"' + ("," if k < len(r) - 1 else ")")
        candidato = actual + ("" if actual.endswith("(") else " ") + pieza
        if len(candidato) > ANCHO_TELEFONO and not actual.endswith("("):
            vector.append(actual)
            actual = "  " + pieza
        else:
            actual = candidato
    vector.append(actual)
    doc = doc.replace("paq &lt;- c(@@PAQUETES_R@@)", "\n".join(vector).replace("<", "&lt;"))
    pip, actual = [], "pip install"
    for m in py:
        if actual != "pip install" and len(actual) + 1 + len(_PIP[m]) > ANCHO_TELEFONO:
            pip.append(actual)
            actual = "pip install"
        actual += " " + _PIP[m]
    pip.append(actual)
    doc = doc.replace("@@ORDEN_PIP@@", "\n".join(pip))
    filas = []
    for clave in ("snow", "pinos", "nc", "meuse", "estaciones", "municipios", "reina", "departamentos"):
        f = EX[clave]
        donde = [str(k) for k, cuerpo in _modulos_del_doc(doc)
                 if k != 8 and f'href="../{f["ruta"]}"' in cuerpo]
        if not donde:
            sys.exit(f"PARADO: ningún módulo enlaza {f['archivo']}, y el recuadro del módulo 8 lo lista")
        filas.append(f"          <li>{enlace_datos(clave)}, "
                     f"{'módulo' if len(donde) == 1 else 'módulos'} {_y(donde)}</li>")
    return doc.replace("@@LISTA_DATOS@@", "\n".join(filas))


def _enunciado_de(doc: str, k: int) -> str:
    """Del número del ejercicio k a su panel de pista: el enunciado y su descarga."""
    i = doc.find(f'<span class="ejercicio-numero">{k}.</span>')
    j = doc.find(f'id="cap1-e{k}-pista"', i)
    return doc[i:j] if 0 <= i < j else ""


def guardas_de_t35(doc: str) -> list[str]:
    problemas = []
    raiz_repo = pathlib.Path(os.environ.get("ESPACIAL_RAIZ") or RAIZ)
    # 1. Ningún bloque lee lo que no viaja al sitio.
    for cuerpo in _TODO_BLOQUE.findall(doc):
        c = _sin_comentarios(html.unescape(cuerpo))
        for vetado in _NO_VIAJA:
            if vetado.search(c):
                primera = next((l for l in c.splitlines() if vetado.search(l)), "").strip()
                problemas.append(f"T3.5: un bloque lee «{vetado.pattern}», que no viaja al sitio: "
                                 f"{primera[:70]}")
    # 2. Lo que leen los bloques está en el extracto, en el disco, enlazado y fuera del .gitignore.
    rutas_ex = {v["ruta"]: v for v in EX.values() if isinstance(v, dict) and "ruta" in v}
    leidas = sorted({m for _, cuerpo in _BLOQUE_EJECUTABLE.findall(doc)
                     for m in _RUTA_DATOS.findall(html.unescape(cuerpo))})
    if not leidas:
        problemas.append("T3.5: ningún bloque lee el extracto; la comprobación de rutas no tiene sujeto")
    for ruta in leidas:
        if ruta not in rutas_ex:
            problemas.append(f"T3.5: un bloque lee {ruta}, que no está en el extracto")
        if not (raiz_repo / ruta).is_file():
            problemas.append(f"T3.5: un bloque lee {ruta}, que no está en el disco")
        if f'href="../{ruta}"' not in doc:
            problemas.append(f"T3.5: un bloque lee {ruta} y el capítulo no lo enlaza")
    for ruta, f in rutas_ex.items():
        p = raiz_repo / ruta
        if p.is_file() and p.stat().st_size != f["bytes"]:
            problemas.append(f"T3.5: {f['archivo']} pesa {p.stat().st_size} B y el capítulo publica "
                             f"{f['bytes']}: el extracto cambió sin regenerar el capítulo")
        try:
            ig = subprocess.run(["git", "check-ignore", "-q", ruta], cwd=str(raiz_repo),
                                capture_output=True, text=True)
            if ig.returncode == 0:
                problemas.append(f"T3.5: {ruta} está en el .gitignore y no llegará al sitio")
            elif ig.returncode != 1:
                print(f"  AVISO  git check-ignore no respondió para {ruta}: no se comprueba")
        except OSError:
            print("  AVISO  sin git: no se comprueba el .gitignore del extracto")
    # 3. Una nota de descarga por módulo, y solo en los que leen datos. El 8
    #    no la lleva: su recuadro lista todos los archivos. El 12 enlaza el suyo
    #    debajo de cada enunciado.
    for k, cuerpo in _modulos_del_doc(doc):
        notas = cuerpo.count('class="text-sm nota-datos"')
        lee = sorted({m for _, b in _BLOQUE_EJECUTABLE.findall(cuerpo)
                      for m in _RUTA_DATOS.findall(html.unescape(b))})
        if notas > 1:
            problemas.append(f"T3.5: el módulo {k} lleva {notas} notas de descarga; va una por módulo")
        if k not in (8, 12) and lee and notas != 1:
            problemas.append(f"T3.5: el módulo {k} lee {lee} y no lleva su nota de descarga")
        # Ronda 2 (V-03): la nota enlaza lo que leen los bloques de SU módulo.
        nota = re.search(r'<p class="text-sm nota-datos"[^>]*>(.*?)</p>', cuerpo, re.S)
        if k not in (8, 12) and nota:
            for ruta in lee:
                if f'href="../{ruta}"' not in nota.group(1):
                    problemas.append(f"T3.5: la nota del módulo {k} no enlaza {ruta}, que leen sus bloques")
        if k not in (8, 12) and notas and cuerpo.find('class="text-sm nota-datos"') > cuerpo.find("<pre><code"):
            problemas.append(f"T3.5: la nota de descarga del módulo {k} va detrás de su primer bloque")
    # 4b. La licencia del extracto (decisión de Javier, ronda 2): una vez, en el
    #     recuadro, con la atribución de las fuentes de los cap1_*.
    i_r = doc.find('id="prepara-tu-entorno"')
    recuadro = doc[i_r:doc.find("</div>", doc.find("<strong>La prueba.</strong>", i_r))] if i_r >= 0 else ""
    if doc.count(LICENCIA_EXTRACTO) != 1 or LICENCIA_EXTRACTO not in recuadro:
        problemas.append("T3.5: la licencia del extracto (CC BY-SA 4.0) no está una sola vez, en el recuadro")
    else:
        parrafo = recuadro[recuadro.rfind("<p>", 0, recuadro.find(LICENCIA_EXTRACTO)):]
        parrafo = parrafo[:parrafo.find("</p>")]
        for fuente in ("Ministerio de Educación Nacional", "ICFES", "DANE", "geoBoundaries"):
            if fuente not in parrafo:
                problemas.append(f"T3.5: la frase de la licencia del extracto no nombra «{fuente}»")
        # El reparto: la CC BY-SA cubre los dos archivos de los municipios y
        # NADA más; cada archivo de un paquete de R va con la licencia de su
        # paquete, y ninguno cae en la frase de la CC BY-SA.
        antes_cc = parrafo[:parrafo.find(LICENCIA_EXTRACTO)]
        for f in CC_EXTRACTO:
            if f"<code>{f}</code>" not in antes_cc:
                problemas.append(f"T3.5: la licencia CC BY-SA del extracto no nombra {f}")
        if "cap1_*" in antes_cc or any(f in antes_cc for f in LICENCIAS_PAQUETES):
            problemas.append("T3.5: la licencia CC BY-SA del extracto cubre archivos de paquetes de R, que "
                             "van con la licencia de su paquete")
        for f, (paq, lic) in LICENCIAS_PAQUETES.items():
            if f"<code>{f}</code>, de <code>{paq}</code> ({lic})" not in parrafo:
                problemas.append(f"T3.5: {f} no lleva la licencia de {paq} ({html.unescape(lic)})")
    # 4. El recuadro: relleno, y la prueba carga todo lo que manda instalar.
    # Ninguna línea de los bloques del recuadro se sale a 375 px (V-06).
    for cuerpo in _TODO_BLOQUE.findall(recuadro):
        largas = [l for l in html.unescape(cuerpo).splitlines() if len(l) > ANCHO_TELEFONO]
        if largas:
            problemas.append(f"T3.5: el recuadro tiene líneas de más de {ANCHO_TELEFONO} caracteres, que "
                             f"en el teléfono se desplazan de lado: {largas[0][:40]!r}")
    if "@@" in doc:
        problemas.append("T3.5: queda una marca @@…@@ sin rellenar en el recuadro del entorno")
    r, py = paquetes_de_los_bloques(doc)
    i = doc.find('id="prepara-tu-entorno"')
    # Solo lo que queda del módulo 8: si la prueba se pierde, no vale la del 9.
    prueba = _BLOQUE_EJECUTABLE.findall(doc[i:doc.find("</template>", i)])[:2] if i >= 0 else []
    if len(prueba) != 2:
        problemas.append("T3.5: el recuadro «Prepara tu entorno» no lleva su prueba en R y en Python")
    else:
        carga_r = set(re.findall(r'\blibrary\(([\w.]+)\)', html.unescape(prueba[0][1])))
        _, carga_py = paquetes_de_los_bloques(f'<pre><code class="language-python">{prueba[1][1]}</code></pre>')
        if set(r) - carga_r:
            problemas.append(f"T3.5: la prueba del entorno no carga {sorted(set(r) - carga_r)}, "
                             f"que la orden manda instalar")
        if set(py) - set(carga_py):
            problemas.append(f"T3.5: la prueba del entorno no importa {sorted(set(py) - set(carga_py))}")
    for k in ("e2", "e4"):
        if "carga_municipios" in S[k]["enunciado"] or S[k]["solucion"].get("archivo") not in rutas_ex:
            problemas.append(f"T3.5: el ejercicio {k[1]} no lee el archivo de municipios del extracto")
        elif f'href="../{S[k]["solucion"]["archivo"]}"' not in _enunciado_de(doc, int(k[1])):
            problemas.append(f"T3.5: el ejercicio {k[1]} no enlaza la descarga de su archivo")
    return problemas


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
    # R3 · T3.5: las listas del recuadro del entorno, desde los bloques.
    doc = completa_entorno(doc)

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
          f"(presupuesto: {PRESUPUESTO_GEO_KB} KB la geometría, 120 KB las rejillas)")
    if kb_geo > PRESUPUESTO_GEO_KB or kb_sim > 120:
        problemas.append(f"la geometría se sale del presupuesto de {PRESUPUESTO_GEO_KB} KB")

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
    # El enlace, DENTRO del ejercicio: desde R3 · T3.5 el mismo archivo lo
    # enlazan también los módulos 3, 8 y 10, y buscarlo en todo el documento
    # dejaba pasar un ejercicio sin su descarga.
    if f'href="../{g3["archivo"]}"' not in _enunciado_de(doc, 3):
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
                                 f"{len(fila.get('variograma', []))} clases de distancia y la banda "
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
                         f"en las ocho clases de distancia, y {fuera} se salen: hay que reescribirla")
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
          f"y sd · {n_lags} clases de distancia por curva · las curvas se separan {sep:.5f}")

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
        problemas.append(f"módulo 6: el teórico de la clase trae {len(tcl)} clases de distancia y la "
                         f"banda {n_lags}: la curva punteada no se podría dibujar")
    else:
        if n(tcl[0]) == n(ten[0]):
            problemas.append("módulo 6: en la clase 1 el teórico de la clase y gamma(1) se "
                             "publican iguales, y la prosa los distingue")
        if not abs(vme[0] - tcl[0]) < 0.1 * abs(vme[0] - ten[0]):
            problemas.append(f"módulo 6: la media de las realizaciones en la clase 1 "
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
    # R2 · T2.3 (ronda 2): lo que el JavaScript escribe con el dato.
    problemas += guardas_de_lecturas(doc, marcado)
    # R3 · T3.2: la notación (D6), contra el documento ensamblado.
    problemas += guardas_de_notacion(doc)
    # R3 · T3.3: los paneles de deducción, la prueba de Clark-Evans y la ergodicidad.
    problemas += guardas_de_t33(doc)
    # R3 · T3.4: la crónica de producción fuera de lo que se lee, y las duraciones medidas.
    problemas += guardas_de_t34(doc)
    # R3 · T3.5: el extracto y el entorno.
    problemas += guardas_de_t35(doc)
    if problemas:
        for p in problemas:
            print(f"  MAL  {p}")
        return 1
    print("\n  Ensamblado limpio.\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
