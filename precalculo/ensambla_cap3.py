#!/usr/bin/env python3
"""
ensambla_cap3.py — construye el capítulo 3 del material (T2.5)

Material de Estadística Espacial 2026-II (20929).
«Cartografía estadística y el MAUP» · semana 4

MISMO REPARTO QUE LOS CAPÍTULOS 1 Y 2 (Checkpoint 1: el capítulo 1 es el
molde):

  · La **prosa** vive en f-strings y se interpola aquí desde el JSON. Es
    lo que audita `audita_texto_cap3.py`.
  · El **JavaScript** NO se interpola: recibe el JSON entero como
    `DATOS_CAP3` y saca de ahí sus cifras con `n5()`. Así una pregunta
    del quiz no puede quedarse con un número viejo.
  · Los **mapas** se registran con su JSON LITERAL, no con una función:
    `audita_texto_base.geomapas()` solo puede comprobar los cortes, el n
    y el peso de un mapa cuya fuente sea un objeto.

VUELTA AL MOLDE, y por eso NO hay desviaciones que declarar: el capítulo
2 subió a 12 preguntas y 5 ejercicios porque cubría dos semanas. El 3
cubre **una sola** (la semana 4), así que vuelve a **8 preguntas y 4
ejercicios**, que es lo que el §6 del plan fija.

LO QUE SÍ ESTRENA, y va declarado:
  · Un mapa con **cuatro capas sobre una sola geometría** —los 1 122
    municipios—, porque pagar esa geometría cuatro veces se lleva el
    presupuesto entero del capítulo. Ver A.14.
  · El **conmutador de daltonismo del motor**, que alcanza a los mapas de
    los capítulos 1 y 2 y no solo a los de éste.

Y LA REGLA DEL RITMO (§9.1 del plan), que aquí rige entera: ningún módulo
abre pidiendo trabajo · todo componente interactivo va con dos párrafos,
el que lo motiva y **el que lo cierra** · el encabezado del módulo es un
contrato.

Uso:  python3 precalculo/ensambla_cap3.py
      (desde la carpeta `Estadistica espacial/`)
"""
from __future__ import annotations

import json
import pathlib
import re
import sys
from baraja_opciones import baraja_documento

RAIZ = pathlib.Path(__file__).resolve().parent.parent
PLANTILLA = RAIZ / "plantilla" / "plantilla-capitulo.html"
SALIDAS = RAIZ / "precalculo" / "salidas"
DESTINO = RAIZ / "Htmls_Espacial" / "capitulo-3-cartografia-maup.html"

D = json.loads((SALIDAS / "cap3_datos.json").read_text(encoding="utf-8"))
M = json.loads((SALIDAS / "cap3_mapas.json").read_text(encoding="utf-8"))
S = json.loads((SALIDAS / "cap3_soluciones.json").read_text(encoding="utf-8"))

m1, m2, m3, m4 = D["m1"], D["m2"], D["m3"], D["m4"]
m5, m6, m7, m8 = D["m5"], D["m6"], D["m7"], D["m8"]
m9, m10, m11 = D["m9"], D["m10"], D["m11"]
GY = m9["gerrymandering"]


# ---------------------------------------------------------------------
# Ayudantes de formato. Los mismos que el capítulo 2, y por el mismo
# motivo: la regla de publicación de T0.5 son CINCO decimales para toda
# cifra de la que el texto argumente.
# ---------------------------------------------------------------------
def n(x, d=5):
    return f"{float(x):.{d}f}"


def ent(x):
    """Entero con espacio fino U+202F. NO usar dentro de KaTeX."""
    return f"{int(round(float(x))):,}".replace(",", " ")


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

    `iniciarGeomapas()` REESCRIBE el `innerHTML` del div del mapa para
    montar su marco, su lienzo, su leyenda y su tabla de respaldo. Un
    `<div class="geomapa-controles">` puesto dentro desaparece en ese
    momento: el capítulo se ve perfecto, la consola está limpia y los
    botones no existen. Por eso el banco de pruebas los pone como
    HERMANO del mapa, y aquí se hace igual.
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


# =====================================================================
# MÓDULO 1 · Del dato al mapa
# =====================================================================
_vac = ", ".join(f"{c['esquema']}/k={c['k']}" for c in m1["clases_vacias"][:3])
MOD1 = cabecera(
    1, "Del dato al mapa", "From data to map",
    "Ver cuántas decisiones hay dentro de un coropleto, y cuántos mapas distintos admite un mismo dato."
) + f"""      <p>Un coropleto parece una fotografía del dato: se toma una variable, se pinta cada
        unidad del color que le toca y ya está. No es eso. Entre el dato y el mapa hay una
        cadena de decisiones —qué variable, normalizada o no, en cuántas clases, con qué
        regla de corte, con qué colores, sobre qué unidades territoriales— y ninguna de
        ellas es neutra. Este capítulo entero trata de esa cadena.</p>

      <p>Empecemos midiendo el tamaño del problema. Tenemos la deserción escolar de los
        {firma(ent(m1['n_con_dato']))} municipios colombianos que la reportan
        —media {firma(n(m1['desercion']['media'], 5), ' %')}, mediana
        {firma(n(m1['desercion']['mediana'], 5), ' %')}, y un recorrido que va de
        {n(m1['desercion']['min'], 5)} a {firma(n(m1['desercion']['max'], 5), ' %')}—.
        Con cinco esquemas de clasificación y valores de <em>k</em> entre
        {m1['ks'][0]} y {m1['ks'][1]} clases hay {firma(ent(m1['n_configuraciones']))}
        formas de dibujar ese mismo dato.</p>

      <div class="key-insight">
        <p style="margin:0;">De esas {ent(m1['n_configuraciones'])} configuraciones,
        {firma(ent(m1['n_mapas_distintos']))} producen una partición <em>realmente</em>
        distinta de los municipios —el {firma(n(m1['pct_distintos'], 5), ' %')}—. No son
        {ent(m1['n_configuraciones'])} variantes de un mapa: son
        {ent(m1['n_mapas_distintos'])} mapas, y todos son defendibles.</p>
      </div>

      <p>Que dos configuraciones den la misma partición no es raro: lo que se compara aquí
        es <strong>a qué clase va cada municipio</strong>, no los cortes impresos. Son cosas
        distintas, y confundirlas produce falsos negativos —el anexo del módulo 3 tiene el
        caso—. Y hay una patología que conviene ver ya: {firma(ent(m1['n_con_clase_vacia']))}
        de esas configuraciones dejan <strong>alguna clase sin un solo municipio</strong>
        ({_vac}…). La leyenda anuncia <em>k</em> clases y el mapa pinta menos, sin avisar.</p>

      <p>El simulador de abajo recorre las {ent(m1['n_configuraciones'])} configuraciones y
        cuenta cuántos municipios caen en cada clase. Mira sobre todo la clase más alta —la
        que un titular llamaría «los peores del país»— y cómo su tamaño salta al cambiar
        de esquema.</p>

{sim('cap3-config', 'Las 35 formas de dibujar el mismo dato',
     'Elige el esquema y el número de clases: la barra muestra cuántos municipios caen en cada una.', 300)}

      <p>Lo que acabas de mover no es una preferencia estética. Al cambiar de esquema cambia
        quién está en el grupo de alarma, y con él cambia a quién señala el mapa. Por eso
        el resto del capítulo trata cada una de esas decisiones por separado, empezando por
        la primera y la más consecuente: qué variable se pinta.</p>

{tabs('El mismo dato bajo dos esquemas',
      '''library(sf); library(classInt); library(dplyr)
source("precalculo/fuentes.R")

mun &lt;- carga_municipios()
des &lt;- mun$desercion[is.finite(mun$desercion)]

# Dos esquemas, mismo k, mismo dato
q &lt;- classIntervals(des, n = 5, style = "quantile")
e &lt;- classIntervals(des, n = 5, style = "equal")

table(findCols(q))
#&gt;
#&gt;   1   2   3   4   5
#&gt; 224 219 230 223 225
table(findCols(e))
#&gt;
#&gt;   1   2   3   4   5
#&gt; 482 545  89   3   2''',
      '''import pandas as pd, mapclassify as mc, numpy as np

llave = pd.read_csv("datos/procesado/municipios_llave.csv", dtype={"divipola": str})
des = llave["desercion"].dropna().to_numpy()

q = mc.Quantiles(des, k=5)
e = mc.EqualInterval(des, k=5)
print(np.bincount(q.yb, minlength=5))
#&gt; [226 224 223 225 223]
print(np.bincount(e.yb, minlength=5))
#&gt; [482 545  89   3   2]

# OJO: los cuantiles NO dan lo mismo que en R (224/219/230/223/225).
# Los intervalos iguales SÍ. Es el hallazgo del módulo 3, ocurriendo
# aquí sobre la deserción municipal: R cierra [a, b) y Python (a, b].''')}
""" + CIERRE


# =====================================================================
# MÓDULO 2 · Normalizar o mentir
# =====================================================================
_t10 = "".join(fila(t["municipio"], t["depto"], ent(t["n"]), n(t["punt"], 2))
               for t in m2["top10_conteo"][:6])
MOD2 = cabecera(
    2, "Normalizar o mentir", "Counts versus rates",
    "Entender por qué el mapa de conteos es casi siempre el mapa de la población, y qué hacer en su lugar."
) + f"""      <p>La primera decisión de la cadena es qué número se pinta. Y hay una respuesta que
        parece obvia y casi siempre está mal: pintar el conteo. Un mapa de «número de casos»,
        «número de delitos» o «número de estudiantes» es, con muy poca variación,
        <strong>un mapa de dónde vive la gente</strong>.</p>

      <p>Lo medimos sobre Saber 11. Tenemos {firma(ent(m2['n_estudiantes']))} estudiantes
        repartidos en {firma(ent(m2['n_municipios']))} municipios, y dos formas de mirarlos:
        el <em>conteo</em> de estudiantes por municipio y su <em>puntaje global medio</em>.
        Son dos mapas del mismo archivo.</p>

      <div class="key-insight">
        <p style="margin:0;">Los diez municipios más oscuros del mapa de conteos son el
        {firma(n(m2['pct_municipios_top10'], 5), ' %')} de los municipios del país y
        concentran el {firma(n(m2['pct_estudiantes_top10'], 5), ' %')} de los estudiantes.
        Ese mapa no responde «dónde les va peor»: responde «dónde hay gente».</p>
      </div>

      <div class="table-wrapper">
        <table>
          <caption>Los seis municipios que encabezan el mapa de conteos, con su puntaje medio.</caption>
          <thead><tr><th scope="col">Municipio</th><th scope="col">Departamento</th>
            <th scope="col">Estudiantes</th><th scope="col">Puntaje medio</th></tr></thead>
          <tbody>
{_t10}          </tbody>
        </table>
      </div>

      <p>Y las dos listas casi no se tocan. La correlación de Pearson entre conteo y puntaje
        medio es {firma(n(m2['r_conteo_tasa'], 5))} —prácticamente nada— y la de Spearman,
        que mira el orden, es {firma(n(m2['rho_conteo_tasa'], 5))}: <strong>negativa</strong>.
        De los veinte primeros de cada lista, comparten
        {firma(ent(m2['solape_top20']))} municipio.</p>

{sim('cap3-conteo-tasa', 'Conteo contra tasa: dos mapas del mismo archivo',
     'Conmuta entre las dos variables y mira cómo se reordena el país.', 300)}

{mapa_html('cap3-conteo-tasa-mapa', 'Los 1 122 municipios: conteo de estudiantes contra puntaje medio')}

      <p>La lección no es «usa siempre la tasa». La tasa trae su propio problema, y es el
        espejo del anterior: en los municipios diminutos la media de un puñado de estudiantes
        se mueve sola, así que los extremos del mapa de tasas los ocupan unidades con muy
        pocos datos. La respuesta correcta es <strong>la tasa más algo que controle el
        tamaño</strong> —un umbral de <em>n</em> declarado, un intervalo por unidad o un
        suavizado— y decirlo en el pie del mapa. Esa misma decisión reaparece en el capítulo 7,
        donde separa un punto caliente real de un municipio con pocos datos.</p>

{tabs('Conteo contra tasa',
      '''library(dplyr)
s11 &lt;- read.csv("precalculo/salidas/cap3_municipios_conteo_tasa.csv",
                colClasses = c(divipola = "character"))

cor(s11$n, s11$punt)
#&gt; [1] 0.1002125
cor(s11$n, s11$punt, method = "spearman")
#&gt; [1] -0.03833912

# Los veinte primeros de cada lista, y cuántos comparten
top_n &lt;- head(s11[order(-s11$n), "divipola"], 20)
top_p &lt;- head(s11[order(-s11$punt), "divipola"], 20)
length(intersect(top_n, top_p))
#&gt; [1] 1''',
      '''import pandas as pd
s11 = pd.read_csv("precalculo/salidas/cap3_municipios_conteo_tasa.csv",
                  dtype={"divipola": str})

print(round(s11["n"].corr(s11["punt"]), 7))
#&gt; 0.1002125
print(round(s11["n"].corr(s11["punt"], method="spearman"), 8))
#&gt; -0.03833912

top_n = set(s11.nlargest(20, "n")["divipola"])
top_p = set(s11.nlargest(20, "punt")["divipola"])
print(len(top_n & top_p))
#&gt; 1''')}
""" + CIERRE


# =====================================================================
# MÓDULO 3 · Esquemas de clasificación
# =====================================================================
_esq = "".join(fila(e["etiqueta"], "/".join(str(t) for t in e["tam"]),
                    " · ".join(n(c, 2) for c in e["cortes"]))
               for e in m3["esquemas"])
_emp = ", ".join(f"{ent(e['n_iguales'])} en {n(e['corte'], 2)}"
                 for e in m3["empates_en_cortes"])
MOD3 = cabecera(
    3, "Esquemas de clasificación", "Class interval schemes",
    "Conocer los cinco esquemas, qué optimiza cada uno, y por qué dos programas pueden discrepar sobre el mismo."
) + f"""      <p>Clasificar es partir un recorrido continuo en <em>k</em> cajones. Hay muchas reglas
        para hacerlo y cada una optimiza algo distinto, así que la pregunta no es cuál es «la
        buena» sino <strong>qué pregunta quieres que el mapa conteste</strong>.</p>

      <ul>
        <li><strong>Intervalos iguales</strong> parte el recorrido en trozos del mismo ancho.
          Conserva la escala del dato, y por eso con una variable asimétrica amontona casi
          todo en la primera clase.</li>
        <li><strong>Cuantiles</strong> pone el mismo número de unidades en cada clase. El mapa
          sale bien repartido de color, pero los anchos de clase son arbitrarios: dos valores
          casi idénticos pueden caer a lados distintos de un corte.</li>
        <li><strong>Fisher-Jenks</strong> busca los cortes que minimizan la varianza dentro de
          las clases. Es el que respeta los agrupamientos naturales del dato.</li>
        <li><strong>Desviación estándar</strong> clasifica por distancia a la media. Solo
          tiene sentido si la variable es aproximadamente simétrica.</li>
        <li><strong>Head/tails</strong> parte repetidamente por la media, y está diseñado
          para distribuciones de cola pesada. Con un dato simétrico degenera.</li>
      </ul>

      <p>Los aplicamos al dato canónico de la literatura: las muertes súbitas de lactantes
        (<code>SID74</code>) en los {firma(ent(m3['n']))} condados de Carolina del Norte, con
        <em>k</em> = {m3['k']}. Media {firma(n(m3['sid_resumen']['media'], 2))},
        máximo {firma(ent(m3['sid_resumen']['max']))}, y
        {firma(ent(m3['sid_resumen']['n_ceros']))} condados con cero casos.</p>

      <div class="table-wrapper">
        <table>
          <caption>Los cinco esquemas sobre <code>SID74</code>: tamaños de clase y cortes.</caption>
          <thead><tr><th scope="col">Esquema</th><th scope="col">Tamaños</th>
            <th scope="col">Cortes</th></tr></thead>
          <tbody>
{_esq}          </tbody>
        </table>
      </div>

{sim('cap3-esquemas', 'Los cinco esquemas sobre el mismo dato canónico',
     'Los tamaños de clase que produce cada esquema sobre SID74, con k = 5.', 280)}

{mapa_html('cap3-nc', 'Carolina del Norte · SID74 bajo los cinco esquemas', controles=True)}

      <p>Fíjate en la primera columna. Intervalos iguales deja
        {firma("/".join(str(t) for t in m3['esquemas'][0]['tam']))} y cuantiles
        {firma("/".join(str(t) for t in m3['esquemas'][1]['tam']))}: es el mismo dato.</p>

      <div class="warning-box">
        <h4>El caso que rompe la confianza: R y Python no clasifican igual por cuantiles</h4>
        <p>Sobre este mismo <code>SID74</code>, con los mismos cinco cuantiles,
        <code>classInt</code> (R) y <code>mapclassify</code> (Python) producen
        <strong>particiones distintas</strong>. No es un fallo de ninguno de los dos, ni un
        problema de redondeo: <strong>es el lado cerrado del intervalo</strong>. R clasifica
        con <code>{m3['convenio_r']}</code> y Python con <code>{m3['convenio_python']}</code>.</p>
        <p style="margin-bottom:0;">La diferencia solo se nota si hay <em>empates justo en un
        corte</em>, y aquí los hay: {firma(ent(m3['n_empatados']))} condados
        ({_emp}). Dos mapas visiblemente distintos del mismo dato, los dos rotulados
        «clasificación por cuantiles». <strong>Fisher-Jenks, en cambio, coincide exactamente</strong>
        en los dos programas: lo que cambia allí es solo cómo se imprime la frontera.</p>
      </div>

{tabs('La discrepancia de cuantiles, medida',
      '''library(sf); library(classInt)
nc  &lt;- st_read(system.file("shape/nc.shp", package = "sf"), quiet = TRUE)
sid &lt;- nc$SID74

q &lt;- classIntervals(sid, n = 5, style = "quantile")
as.vector(table(findCols(q)))
#&gt; [1] 13 25 13 26 23

# La causa: cuántos condados EMPATAN justo en un corte
cortes &lt;- q$brks[-c(1, length(q$brks))]
sum(sapply(cortes, function(c0) sum(sid == c0)))
#&gt; [1] 39''',
      '''import pandas as pd, mapclassify as mc, numpy as np
sid = pd.read_csv("precalculo/salidas/cap3_nc.csv")["sid74"].to_numpy()

q = mc.Quantiles(sid, k=5)
print(np.bincount(q.yb, minlength=5))
#&gt; [24 27 11 19 19]

# Fisher-Jenks SÍ coincide con R
f = mc.FisherJenks(sid, k=5)
print(np.bincount(f.yb, minlength=5))
#&gt; [32 34 19 11  4]''')}

      <p>La consecuencia práctica es una regla de higiene: <strong>el esquema, el <em>k</em> y
        el programa forman parte del resultado</strong>, y un mapa que no los declara en su
        leyenda está incompleto. El módulo siguiente enseña cuánto cuesta callarlos.</p>
""" + CIERRE


# =====================================================================
# MÓDULO 4 · El mismo dato, cinco mapas
# =====================================================================
_pares = "".join(fila(f"{p['etiqueta_a']} vs. {p['etiqueta_b']}", n(p["pct_cambian"], 5) + " %")
                 for p in sorted(m4["pares"], key=lambda z: -z["pct_cambian"])[:6])
_alta = " / ".join(ent(v) for v in m4["n_en_clase_alta"])
_mv = m4["municipio_volatil"]
MOD4 = cabecera(
    4, "El mismo dato, cinco mapas", "One dataset, five maps",
    "Medir cuántas unidades cambian de clase al cambiar de esquema, y ver que elegir el mapa es una decisión de modelado."
) + f"""      <p>El módulo anterior mostró que los esquemas dan particiones distintas. Ahora hay que
        ponerle un número a «distintas», porque «el mapa cambia» es una impresión y el
        material de este curso no publica impresiones.</p>

      <p>Tomamos la deserción de los {firma(ent(m4['n']))} municipios con dato, fijamos
        <em>k</em> = {m4['k']} y clasificamos con los cinco esquemas. Después contamos, para
        cada pareja, qué porcentaje de municipios recibe una clase distinta.</p>

      <div class="table-wrapper">
        <table>
          <caption>Municipios que cambian de clase entre esquemas (k = {m4['k']}, n = {ent(m4['n'])}).</caption>
          <thead><tr><th scope="col">Pareja de esquemas</th>
            <th scope="col">Cambian de clase</th></tr></thead>
          <tbody>
{_pares}          </tbody>
        </table>
      </div>

      <div class="key-insight">
        <p style="margin:0;">Entre {m4['par_mas_discordante']['etiqueta_a'].lower()} y
        {m4['par_mas_discordante']['etiqueta_b'].lower()} cambian de clase el
        {firma(n(m4['pct_max'], 5), ' %')} de los municipios. Solo
        {firma(ent(m4['n_estables']))} de {ent(m4['n'])} —el
        {firma(n(m4['pct_estables'], 5), ' %')}— reciben la misma clase en los cinco esquemas.</p>
      </div>

      <p>Y el dato que cierra el argumento: <strong>cuántos municipios acaban en la clase más
        alta</strong>, la que un mapa de alarma pintaría de rojo. Según el esquema, son
        {firma(_alta)}. El mismo país, la misma variable, el mismo número de clases: de dos
        municipios en alerta a doscientos veinticinco, o a ninguno.</p>

      <p>Un caso concreto: {firma(_mv['municipio'])} ({_mv['depto']}), con una deserción de
        {firma(n(_mv['desercion'], 2), ' %')}, recibe las clases
        {firma(", ".join(str(c) for c in _mv['clases']))} según el esquema —un recorrido de
        {firma(ent(m4['rango_max']))} clases—, y no es una rareza:
        {firma(ent(m4['n_con_rango_max']))} municipios tienen ese mismo recorrido.</p>

{sim('cap3-discordancia', 'La matriz de discordancia',
     'Cada barra es una pareja de esquemas y su altura, el porcentaje de municipios que cambian de clase.', 300)}

{mapa_html('cap3-desercion', 'Colombia · deserción escolar municipal bajo los cinco esquemas', controles=True)}

      <p>Conmuta el esquema en el mapa y mira el norte del país. No estás mirando cinco
        versiones de un mapa: estás mirando cinco afirmaciones distintas sobre dónde está el
        problema, todas ciertas y ninguna completa. Por eso el capítulo insiste en que
        <strong>elegir el mapa es una decisión de modelado, no de presentación</strong>, y en
        que la honestidad no consiste en elegir bien sino en <em>declarar</em> lo que se eligió
        —y, cuando importa, publicar el mapa junto a su sensibilidad—.</p>

{tabs('La matriz de discordancia',
      '''library(classInt)
d &lt;- read.csv("precalculo/salidas/cap3_desercion.csv",
              colClasses = c(divipola = "character"))
cl &lt;- d[, c("clase_equal", "clase_quantile", "clase_fisher",
            "clase_sd", "clase_headtails")]

# Cuántos municipios reciben la MISMA clase en los cinco
sum(apply(cl, 1, function(v) length(unique(v)) == 1))
#&gt; [1] 224

# Y cuántos van a la clase más alta segun el esquema
sapply(cl, function(v) sum(v == 5))
#&gt;    clase_equal clase_quantile   clase_fisher       clase_sd clase_headtails
#&gt;              2            225             48              1               0''',
      '''import pandas as pd, numpy as np
d = pd.read_csv("precalculo/salidas/cap3_desercion.csv", dtype={"divipola": str})
cols = ["clase_equal", "clase_quantile", "clase_fisher",
        "clase_sd", "clase_headtails"]
cl = d[cols].to_numpy()

print(int((cl.max(axis=1) == cl.min(axis=1)).sum()))
#&gt; 224

print([int((d[c] == 5).sum()) for c in cols])
#&gt; [2, 225, 48, 1, 0]''')}
""" + CIERRE


# =====================================================================
# MÓDULO 5 · Color
# =====================================================================
_pal = "".join(fila(p["id"], p["tipo"], n(p["dmin_normal"], 3),
                    n(p["simulaciones"][0]["dmin"], 3),
                    n(p["simulaciones"][0]["caida_pct"], 2) + " %",
                    n(p["rango_luminosidad"], 2))
               for p in m5["paletas"])
_rv = m5["rojo_verde"]
MOD5 = cabecera(
    5, "Color", "Colour in thematic mapping",
    "Elegir la familia de paleta que corresponde al dato, y medir —no suponer— si sobrevive al daltonismo."
) + f"""      <p>El color de un mapa no es decoración: es el eje que el lector usa para leer el dato.
        Hay tres familias y elegir la que no toca desinforma con eficacia.</p>

      <ul>
        <li><strong>Secuencial</strong> para variables ordenadas sin punto medio natural
          (densidad, tasa, conteo): una rampa de claro a oscuro.</li>
        <li><strong>Divergente</strong> cuando hay un punto medio con significado (la media,
          el cero, un objetivo): dos rampas que salen de un centro neutro.</li>
        <li><strong>Cualitativa</strong> para categorías sin orden: matices distintos y
          luminosidad parecida.</li>
      </ul>

      <p>Las paletas de este capítulo salen de <strong>ColorBrewer</strong> (Brewer, Harrower y
        el Pennsylvania State University), que es el catálogo estándar para cartografía
        temática y clasifica sus paletas justo en esas tres familias.</p>

      <p>La trampa clásica es usar una divergente para un dato sin centro: el mapa inventa un
        punto de inflexión que el dato no tiene. Y la segunda trampa, menos conocida, es
        suponer que una paleta que se ve bien se ve bien <em>para todo el mundo</em>. Cerca del
        8&nbsp;% de los hombres tiene alguna forma de daltonismo, así que eso hay que medirlo.</p>

      <p>Se mide con la <strong>distancia perceptual mínima entre clases contiguas</strong> en
        CIELAB: una paleta no se rompe cuando «se ve rara», se rompe cuando dos clases vecinas
        dejan de distinguirse. Debajo, esa distancia con visión normal y bajo deuteranopía,
        para las siete paletas del capítulo.</p>

      <div class="table-wrapper">
        <table>
          <caption>Distancia perceptual mínima entre clases contiguas (ΔE en CIELAB), k = 5.</caption>
          <thead><tr><th scope="col">Paleta</th><th scope="col">Familia</th>
            <th scope="col">Normal</th><th scope="col">Deuteranopía</th>
            <th scope="col">Caída</th><th scope="col">Recorrido de L*</th></tr></thead>
          <tbody>
{_pal}          </tbody>
        </table>
      </div>

      <div class="key-insight">
        <p style="margin:0;">La última columna explica las demás. Las paletas que sobreviven
        son las que tienen <strong>recorrido de luminosidad</strong>: aunque el matiz colapse,
        el claro-oscuro se conserva. Las que se hunden son las de luminosidad plana —las
        cualitativas—, y con ellas el mapa deja de leerse.</p>
      </div>

      <p>El caso extremo se construye a propósito: un rojo y un verde <strong>a la misma
        luminosidad</strong> (L* = {n(_rv['luminosidad'][0], 2)} y
        {n(_rv['luminosidad'][1], 2)}). Con visión normal distan
        {firma(n(_rv['dE_normal'], 5), ' ΔE')}; bajo deuteranopía,
        {firma(n(_rv['dE_deuteranopia'], 5), ' ΔE')}. Un
        {firma(n(_rv['caida_pct'], 5), ' %')} menos: dejan de ser dos colores.</p>

{sim('cap3-paletas', 'Las paletas bajo los tres tipos de daltonismo',
     'Elige la paleta y el tipo de visión: las barras son la distancia perceptual entre clases contiguas.', 300)}

      <div class="tip-box">
        <h4>El conmutador vale para todo el material</h4>
        <p style="margin-bottom:0;">Los botones de abajo no simulan el daltonismo en este
        simulador: lo simulan <strong>en el motor de mapas</strong>. Conmútalo y vuelve a
        cualquier mapa de este capítulo —o de los capítulos 1 y 2— y lo verás como lo vería
        un lector con esa visión. La simulación es la de Machado, Oliveira y Fernandes (2009),
        la misma que calcula R, y el capítulo trae {firma(ent(m5['n_comparaciones_cvd']))}
        anclas para comprobar que las dos implementaciones coinciden color a color.</p>
      </div>

      <div class="geomapa-controles" id="cap3-ctrl-cvd">
        <button type="button" class="geomapa-boton activo" data-cvd="">Visión normal</button>
        <button type="button" class="geomapa-boton" data-cvd="deuteranopia">Deuteranopía</button>
        <button type="button" class="geomapa-boton" data-cvd="protanopia">Protanopía</button>
        <button type="button" class="geomapa-boton" data-cvd="tritanopia">Tritanopía</button>
      </div>

      <p>Dos reglas prácticas para cerrar: usa paletas con recorrido de luminosidad siempre
        que puedas —sobreviven al daltonismo y también a una fotocopia en gris—, y no confíes
        en el matiz como único portador de información. Si el mapa deja de leerse al conmutar
        el botón de arriba, el mapa está mal, no el lector.</p>

{tabs('Medir si una paleta sobrevive',
      '''library(colorspace); library(RColorBrewer)

dmin &lt;- function(hex) {{
  lab &lt;- as(hex2RGB(hex), "LAB")@coords
  min(sqrt(rowSums((lab[-1, ] - lab[-nrow(lab), ])^2)))
}}

p &lt;- brewer.pal(5, "YlOrRd")
round(dmin(p), 3)
#&gt; [1] 24.447
round(dmin(deutan(p, severity = 1)), 3)
#&gt; [1] 13.125''',
      '''import sys; sys.path.insert(0, "precalculo")
from audita_cap3 import dmin_lab, cvd    # el CIELAB y las matrices, a mano

p = ["#FFFFB2", "#FECC5C", "#FD8D3C", "#F03B20", "#BD0026"]
print(round(dmin_lab(p), 3))
#&gt; 24.447
print(round(dmin_lab(cvd(p, "deuteranopia")), 3))
#&gt; 13.125''')}
""" + CIERRE


# =====================================================================
# MÓDULO 6 · tmap
# =====================================================================
MOD6 = cabecera(
    6, "La gramática del mapa temático", "tmap and the grammar of maps",
    "Escribir mapas con una gramática por capas en R y en Python, y reconocer qué versión de tmap se está leyendo."
) + f"""      <p>Hasta aquí hemos hablado de decisiones. Toca escribirlas. <code>tmap</code> es a los
        mapas lo que <code>ggplot2</code> a los gráficos: una gramática por capas donde el
        mapa se compone sumando términos, y donde cada decisión del capítulo tiene su propia
        ranura explícita —la variable, la escala de clases, la paleta, la leyenda—.</p>

      <div class="warning-box">
        <h4>La versión importa, y casi todo lo que hay escrito está desactualizado</h4>
        <p style="margin-bottom:0;">Este material usa <strong>tmap {m6['version_tmap']}</strong>.
        La versión 4 cambió la API respecto de la 3: la estética va en
        <code>fill=</code> y la clasificación en un objeto <code>tm_scale_*()</code>, donde
        antes había <code>col=</code> y <code>style=</code>. La mayoría de tutoriales en línea
        son de la 3 y <strong>no corren</strong> aquí. Los
        {firma(ent(m6['n_verbos']))} verbos que usa este capítulo están verificados contra el
        paquete instalado, no escritos de memoria.</p>
      </div>

      <p>Los tres bloques de abajo dibujan <em>el mismo</em> coropleto de tres formas: con la
        gramática de <code>tmap</code>, con <code>ggplot2</code> —que también sabe dibujar
        objetos <code>sf</code>— y con GeoPandas. Compararlos ayuda a ver que la gramática es
        la misma en los tres y que lo único que cambia es el vocabulario.</p>

{tabs('El mismo mapa con tmap 4 y con GeoPandas',
      '''library(tmap); library(sf)
source("precalculo/fuentes.R")
mun &lt;- carga_municipios()

tm_shape(mun) +
  tm_polygons(
    fill = "desercion",
    fill.scale = tm_scale_intervals(n = 5, style = "quantile",
                                    values = "brewer.yl_or_rd"),
    fill.legend = tm_legend(title = "Deserción (%)"),
    col = "white", lwd = 0.2) +
  tm_layout(frame = FALSE)

as.character(packageVersion("tmap"))
#&gt; [1] "4.2"''',
      '''import geopandas as gpd, pandas as pd

mun = gpd.read_file("datos/procesado/colombia_adm2.gpkg")
llave = pd.read_csv("datos/procesado/municipios_llave.csv",
                    dtype={"divipola": str})
mun = mun.merge(llave, on="shapeID")

mun.plot(column="desercion", scheme="quantiles", k=5,
         cmap="YlOrRd", edgecolor="white", linewidth=0.2,
         legend=True, legend_kwds={"title": "Deserción (%)"})''')}

      <div class="table-wrapper">
        <table>
          <caption>La misma decisión, en los tres vocabularios.</caption>
          <thead><tr><th scope="col">Decisión</th><th scope="col">tmap 4</th>
            <th scope="col">ggplot2</th><th scope="col">GeoPandas</th></tr></thead>
          <tbody>
{fila("Qué variable", "<code>fill=</code>", "<code>aes(fill=)</code>", "<code>column=</code>")}{fila("Esquema de clases", "<code>tm_scale_intervals(style=)</code>", "<code>scale_fill_fermenter()</code>", "<code>scheme=</code>")}{fila("Número de clases", "<code>n=</code>", "<code>n.breaks=</code>", "<code>k=</code>")}{fila("Paleta", "<code>values=</code>", "<code>palette=</code>", "<code>cmap=</code>")}{fila("Leyenda", "<code>tm_legend()</code>", "<code>labs(fill=)</code>", "<code>legend_kwds=</code>")}          </tbody>
        </table>
      </div>

      <p>La tabla tiene una lectura que va más allá del vocabulario: <strong>los tres sistemas
        te obligan a declarar el esquema y el número de clases</strong>. Ninguno los adivina, y
        eso es una virtud. El problema del módulo 4 no era que las herramientas escondieran la
        decisión, sino que el mapa publicado no la contaba.</p>
""" + CIERRE


# =====================================================================
# MÓDULO 7 · Más allá del coropleto
# =====================================================================
_ct = "".join(fila(c["nombre"], c["origen"], n(c["corr"], 6), n(c["max_error_rel"], 5))
              for c in m7["cartogramas"])
_bc = " → ".join(f"{b['itermax']}: {n(b['corr'], 4)}" for b in m7["barrido_contiguo"])
MOD7 = cabecera(
    7, "Más allá del coropleto", "Beyond the choropleth",
    "Conocer cuatro alternativas al coropleto y la propiedad exacta que juzga a cada una."
) + f"""      <p>El coropleto tiene un sesgo estructural que no se arregla con ninguna paleta:
        <strong>pinta área, y el área no es la variable</strong>. Un municipio enorme y vacío
        ocupa más tinta que una ciudad entera, así que el mapa siempre exagera lo rural. Hay
        cuatro familias de respuesta, y cada una compra algo a cambio de algo.</p>

      <p>Las probamos sobre los {firma(ent(m7['n_departamentos']))} departamentos con el número
        de estudiantes de Saber 11 ({firma(ent(m7['total_estudiantes']))} en total), una
        variable donde el departamento mayor tiene {firma(n(m7['simbolos']['razon_valor'], 2))}
        veces el valor del menor.</p>

      <h3>Símbolos proporcionales</h3>
      <p>Un círculo sobre cada unidad, con el <strong>área</strong> proporcional al valor —no el
        radio: confundirlos es el error clásico y exagera las diferencias al cuadrado—. Con
        esta variable el círculo mayor tiene {firma(n(m7['simbolos']['radio_max_rel'], 5))} veces
        el radio del menor. Rompe el sesgo de área pero se solapa donde las unidades son
        pequeñas.</p>

      <h3>Dot density</h3>
      <p>Un punto por cada {firma(ent(m7['dot_density']['por_punto']))} estudiantes, colocado
        <strong>al azar</strong> dentro de su unidad. Da una sensación de densidad muy legible,
        y trae una propiedad que hay que decir en voz alta: <strong>el mapa depende de la
        semilla</strong>. Al repetir el sorteo, cada punto se desplaza
        {firma(n(m7['dot_density']['dmin_media_km'], 5), ' km')} de media
        (mediana {n(m7['dot_density']['dmin_mediana_km'], 5)} km, máximo
        {n(m7['dot_density']['dmin_max_km'], 5)} km). El punto no dice dónde está nadie.</p>

      <h3>Hexbin</h3>
      <p>Se sustituyen las unidades administrativas por una rejilla regular de
        {firma(ent(m7['hexbin']['n_hexagonos']))} hexágonos de {m7['hexbin']['lado_km']} km y se
        reparte el valor proporcionalmente al área. Elimina el sesgo de las unidades
        desiguales… <strong>creando unas nuevas</strong>: es el MAUP otra vez, y los módulos
        siguientes tratan justo de eso.</p>

      <h3>Cartogramas</h3>
      <p>Se deforma la geometría hasta que el área <em>sea</em> la variable. Hay tres, y los
        juzga una propiedad exacta: si el área es proporcional al valor, la correlación entre
        las dos tiene que valer 1.</p>

      <div class="table-wrapper">
        <table>
          <caption>Los tres cartogramas y su proporcionalidad, medida.</caption>
          <thead><tr><th scope="col">Cartograma</th><th scope="col">Origen</th>
            <th scope="col">corr(área, valor)</th><th scope="col">Error relativo máx.</th></tr></thead>
          <tbody>
{_ct}          </tbody>
        </table>
      </div>

      <div class="key-insight">
        <p style="margin:0;">Los dos primeros dan <strong>1 exacta</strong>: son
        proporcionales por construcción. El contiguo <strong>no puede</strong> serlo, y no es
        un defecto de implementación: tiene que conservar la topología —que los vecinos sigan
        siendo vecinos— y esa restricción compite con el área. Al aumentar las iteraciones
        mejora y se estanca ({_bc}). Un cartograma contiguo es siempre un compromiso, y saberlo
        forma parte de leerlo.</p>
      </div>

{sim('cap3-carto-sim', 'Hasta dónde llega cada cartograma',
     'La correlación entre área y valor: exacta en los dos propios, y un límite en el contiguo.', 280)}

{mapa_html('cap3-carto', 'Los 33 departamentos · coropleto, símbolos proporcionales y dot density', controles=True)}

{mapa_html('cap3-carto-ncont', 'Cartograma no contiguo (Olson): el área ES el número de estudiantes')}

{mapa_html('cap3-carto-dorling', 'Cartograma de Dorling: círculos proporcionales con repulsión')}

{mapa_html('cap3-carto-cont', 'Cartograma contiguo (Dougenik): conserva la vecindad, y por eso no es exacto')}

{mapa_html('cap3-hexbin', 'Hexbin: se cambian las unidades administrativas por una rejilla regular')}

      <p>Conmuta entre las seis vistas con la misma caja de referencia: lo que se ve encoger o
        crecer es área de verdad, no un cambio de encuadre. Y fíjate en Bogotá, que en el
        coropleto es un punto y en los cartogramas es el país entero. Ninguna de las seis vistas
        es «la correcta»: cada una contesta una pregunta distinta, y la elección vuelve a ser
        de modelado.</p>

{tabs('Los tres cartogramas y su propiedad exacta',
      '''library(sf); library(cartogram)
source("precalculo/geo.R")
dep &lt;- readRDS("precalculo/cache/dep_disuelto_1122.rds")
dep$n_est &lt;- read.csv("precalculo/salidas/cap3_departamentos.csv")$n_est

# Olson, implementación propia: área proporcional POR CONSTRUCCIÓN
o &lt;- geo_carto_ncont(dep, dep$n_est)
round(cor(as.numeric(st_area(o)), dep$n_est), 10)
#&gt; [1] 1

# El contiguo NO alcanza la proporcionalidad exacta
c60 &lt;- cartogram_cont(dep, "n_est", itermax = 60, verbose = FALSE)
round(cor(as.numeric(st_area(c60)), dep$n_est), 6)
#&gt; [1] 0.816941''',
      '''import geopandas as gpd, numpy as np, pandas as pd
from shapely import affinity

dep = gpd.read_file("datos/procesado/colombia_adm1.gpkg")
val = pd.read_csv("precalculo/salidas/cap3_departamentos.csv")["n_est"].to_numpy()

# Olson a mano: escalar cada polígono alrededor de su centroide.
# `scale` no acepta un vector, así que se aplica UNO A UNO — y ese
# detalle es justo el que hace que la propiedad exacta se cumpla.
d = val / dep.geometry.area.to_numpy()
k = np.sqrt(d / d.max())
carto = [affinity.scale(g, xfact=f, yfact=f, origin="centroid")
         for g, f in zip(dep.geometry, k)]
a = np.array([g.area for g in carto])
print(round(float(np.corrcoef(a, val)[0, 1]), 10))
#&gt; 1.0''')}
""" + CIERRE


# =====================================================================
# MÓDULO 8 · MAUP I — el efecto escala
# =====================================================================
_curva = "".join(fila(ent(c["zonas"]), n(c["media"], 5), n(c["sd"], 5))
                 for c in m8["curva"])
_ca = m8["cartografica"]
MOD8 = cabecera(
    8, "MAUP I · el efecto escala", "MAUP: the scale effect",
    "Medir cómo cambia una correlación al cambiar el nivel de agregación, y entender por qué cambia."
) + f"""      <p>Llegamos al problema que da nombre a la mitad del capítulo. El <strong>problema de la
        unidad de área modificable</strong> (MAUP) dice que los resultados de un análisis
        dependen de las unidades territoriales en que se agregan los datos, y que esas unidades
        son casi siempre arbitrarias. Tiene dos caras: el <em>efecto escala</em> —cuántas
        unidades— y el <em>efecto zonificación</em> —dónde se trazan sus fronteras—. Esta es
        la primera.</p>

      <p>El experimento necesita un dato con niveles reales, y lo tenemos: Saber 11 relaciona,
        para {firma(ent(m8['n_estudiantes']))} estudiantes, la educación de la madre con el
        puntaje global. Podemos medir la correlación a nivel de <strong>estudiante</strong>, y
        después agregar a los {ent(m8['n_municipios'])} municipios y a los
        {ent(m8['n_departamentos'])} departamentos y volver a medirla.</p>

      <div class="key-insight">
        <p style="margin:0;">Individuo {firma(n(m8['r_individuo'], 5))} →
        municipio {firma(n(m8['r_municipio'], 5))} →
        departamento {firma(n(m8['r_departamento'], 5))}. Es el mismo dato y la misma pareja de
        variables. Al pasar de estudiante a departamento la correlación sube un
        {firma(n(m8['subida_ind_dep_pct'], 5), ' %')}.</p>
      </div>

      <p>Y ni siquiera es monótono. Si se construyen zonas intermedias —agrupando municipios
        contiguos al azar hasta tener <em>k</em> zonas— la correlación sube, hace cima y baja:</p>

      <div class="table-wrapper">
        <table>
          <caption>Correlación media según el número de zonas ({m8['n_rep']} particiones contiguas por escala).</caption>
          <thead><tr><th scope="col">Zonas</th><th scope="col">r medio</th>
            <th scope="col">Desv. típica</th></tr></thead>
          <tbody>
{_curva}          </tbody>
        </table>
      </div>

{sim('cap3-escala', 'La correlación en función del número de zonas',
     'Cada punto es la media de 30 particiones contiguas aleatorias con ese número de zonas.', 300)}

      <p>La causa no es magia estadística, es aritmética. Al agregar se destruye la variación
        <em>dentro</em> de cada unidad y solo sobrevive la que hay <em>entre</em> unidades. Con
        estos datos, la varianza entre municipios es apenas el
        {firma(n(D['m8']['pct_var_entre'], 5), ' %')} de la varianza total del puntaje: el
        {firma(n(m10['pct_var_dentro'], 5), ' %')} restante vive dentro de los municipios y
        desaparece en cuanto se promedia. Lo que queda es una relación más limpia, más fuerte
        y <strong>referida a otra cosa</strong>.</p>

      <div class="warning-box">
        <h4>Un detalle que no es un detalle: quién entra en el mapa</h4>
        <p style="margin-bottom:0;">La escalera de arriba usa todos los estudiantes con código
        de municipio. Pero {firma(ent(_ca['n_fuera_del_mapa']))} de ellos viven en municipios
        que <strong>el mapa no tiene</strong>, y en cuanto el análisis pasa por la geometría
        desaparecen. La correlación departamental pasa de {n(m8['r_departamento'], 5)} a
        {firma(n(_ca['r_departamento'], 5))}: un desvío de
        {firma(n(_ca['desvio_departamental'], 5))}. Es pequeño y aquí no cambia ninguna
        conclusión, pero se mide y se publica — y el módulo 11 cuenta a quién pertenecen esos
        estudiantes.</p>
      </div>

{tabs('La escalera, medida',
      '''library(data.table)
v &lt;- fread("precalculo/salidas/cap3_municipios_edu_madre.csv",
           colClasses = c(divipola = "character"))

# A nivel de municipio (los agregados ya vienen del microdato)
round(cor(v$x, v$p), 7)
#&gt; [1] 0.3033294

# Y agregando esos municipios a departamento, ponderando por n
dep &lt;- v[, .(x = sum(n * x) / sum(n), p = sum(n * p) / sum(n)),
         by = .(dpto = substr(divipola, 1, 2))]
round(cor(dep$x, dep$p), 7)
#&gt; [1] 0.5126097

# La MISMA cuenta, solo con los municipios que existen en el mapa: los
# huerfanos se caen y la cifra se mueve. Es la medida del modulo 11.
mapa &lt;- read.csv("datos/procesado/municipios_llave.csv",
                 colClasses = c(divipola = "character"))$divipola
dm &lt;- v[divipola %chin% mapa,
        .(x = sum(n * x) / sum(n), p = sum(n * p) / sum(n)),
        by = .(dpto = substr(divipola, 1, 2))]
round(cor(dm$x, dm$p), 7)
#&gt; [1] 0.5076394''',
      '''import pandas as pd, numpy as np
v = pd.read_csv("precalculo/salidas/cap3_municipios_edu_madre.csv",
                dtype={"divipola": str})

print(round(v["x"].corr(v["p"]), 7))
#&gt; 0.3033294

v["dpto"] = v["divipola"].str[:2]
pond = lambda s: pd.Series({"x": np.average(s.x, weights=s.n),
                            "p": np.average(s.p, weights=s.n)})
g = v.groupby("dpto")[["x", "p", "n"]].apply(pond)
print(round(g["x"].corr(g["p"]), 7))
#&gt; 0.5126097

mapa = set(pd.read_csv("datos/procesado/municipios_llave.csv",
                       dtype={"divipola": str})["divipola"])
gm = v[v["divipola"].isin(mapa)].groupby("dpto")[["x", "p", "n"]].apply(pond)
print(round(gm["x"].corr(gm["p"]), 7))
#&gt; 0.5076394''')}
""" + CIERRE


# =====================================================================
# MÓDULO 9 · MAUP II — el efecto zonificación
# =====================================================================
_co, _ar, _sp = m9["contiguas"], m9["arbitrarias"], m9["sin_ponderar"]
_dist = "".join(fila(ent(d["escanos"]), ent(d["n"]), n(d["pct"], 2) + " %")
                for d in GY["distribucion"] if d["n"])
MOD9 = cabecera(
    9, "MAUP II · el efecto zonificación", "MAUP: the zoning effect",
    "Ver que a igual número de zonas el trazado de las fronteras cambia el resultado, y medir cuánto."
) + f"""      <p>La segunda cara del MAUP es más incómoda que la primera. El efecto escala al menos
        se ve venir: nadie espera que un análisis municipal y uno departamental den lo mismo.
        El efecto zonificación dice algo peor: <strong>a igual número de zonas, mover las
        fronteras cambia el resultado</strong>.</p>

      <p>Lo medimos así. Colombia tiene {firma(ent(m9['n_zonas']))} departamentos, con tamaños
        que van de {ent(m9['tam_zonas_reales']['min'])} a
        {ent(m9['tam_zonas_reales']['max'])} municipios. Generamos
        {firma(ent(m9['n_particiones']))} particiones alternativas de los mismos municipios en
        {m9['n_zonas']} zonas <strong>contiguas</strong>, y para cada una recalculamos la
        correlación entre educación de la madre y puntaje.</p>

      <div class="key-insight">
        <p style="margin:0;">Con la partición departamental real, r =
        {firma(n(m9['r_real'], 5))}. Con {ent(m9['n_particiones'])} particiones contiguas del
        mismo número de zonas, r va de {firma(n(_co['min'], 5))} a
        {firma(n(_co['max'], 5))} —un recorrido de
        {firma(n(m9['recorrido_contiguas'], 5))}—, con media {n(_co['media'], 5)}. La
        partición real cae en el <strong>percentil {n(_co['percentil_real'], 5)}</strong>: no
        tiene nada de especial.</p>
      </div>

{sim('cap3-zonificacion', 'Mil trazados distintos del mismo país',
     'La distribución de la correlación sobre 1 000 particiones, con el trazado departamental real marcado.', 300)}

      <p>Y hay una segunda distribución que enseña el mecanismo. Si en vez de zonas contiguas
        se reparten los municipios <strong>al azar</strong>, sin mirar dónde están —conservando
        los tamaños reales—, la correlación no baja: <strong>sube</strong>, a
        {firma(n(_ar['media'], 5))} de media, y la real cae en su percentil {firma(n(_ar['percentil_real'], 5))}.</p>

      <div class="warning-box">
        <h4>Por qué las zonas arbitrarias dan correlaciones MÁS altas</h4>
        <p>Es lo contrario de lo que casi todo el mundo espera, así que conviene comprobar el
        mecanismo en vez de contar una historia. La causa es el <strong>ponderador</strong>: una
        zona arbitraria reúne municipios de todo el país, así que su media ponderada acaba
        fijada por el municipio grande que le tocó, y comparar 33 zonas así se parece a comparar
        33 ciudades grandes, donde la relación es más fuerte. Una zona contigua reúne vecinos,
        que ya se parecen entre sí, y promediarlos añade poco.</p>
        <p style="margin-bottom:0;">La prueba: al quitar el ponderador, la brecha entre las dos
        familias pasa de {firma(n(_sp['brecha_ponderada'], 5))} a
        {firma(n(_sp['brecha_sin_ponderar'], 5))}, y las contiguas caen hasta
        {firma(n(_sp['contiguas_media'], 5))}. <strong>El ponderador es parte del trazado
        aunque no se dibuje.</strong></p>
      </div>

      <h3>El caso donde el trazado se elige a propósito</h3>
      <p>Si mover fronteras cambia resultados, alguien acabará moviéndolas a conveniencia. Eso
        tiene nombre —<em>gerrymandering</em>— y se ve mejor en una rejilla de juguete que en un
        mapa real, porque en la rejilla la aritmética queda a la vista y no hay que discutir
        ninguna política concreta.</p>

      <p>Una rejilla de {GY['lado']}×{GY['lado']} casillas, {firma(ent(GY['n_A']))} del partido A
        y {firma(ent(GY['n_B']))} del B —el {firma(n(GY['pct_A'], 5), ' %')} para A—, repartida
        en {GY['n_distritos']} distritos <strong>contiguos</strong> de {GY['casillas_por_distrito']}
        casillas. Proporcionalmente le tocarían {firma(n(GY['escanos_proporcionales'], 2))}
        escaños. Buscando entre {firma(ent(GY['n_particiones_probadas']))} trazados aleatorios
        aparecieron {firma(ent(GY['n_particiones_validas']))} válidos, y con ellos A saca:</p>

      <div class="table-wrapper">
        <table>
          <caption>Escaños de A sobre {ent(GY['n_particiones_validas'])} trazados contiguos válidos.</caption>
          <thead><tr><th scope="col">Escaños de A</th><th scope="col">Trazados</th>
            <th scope="col">%</th></tr></thead>
          <tbody>
{_dist}          </tbody>
        </table>
      </div>

      <p>Con los mismos votos, el trazado decide entre {firma(ent(GY['escanos_min']))} y
        {firma(ent(GY['escanos_max']))} escaños de {GY['n_distritos']}. Nadie cambió un voto.</p>

{sim('cap3-gerry', 'La misma votación, tres trazados',
     'Cada trazado reparte las mismas 25 casillas en 5 distritos contiguos de 5.', 280)}

      <p>La conclusión del módulo no es que los mapas mientan, sino que <strong>la unidad
        geográfica es un parámetro del análisis</strong>, y como todo parámetro hay que
        declararlo, justificarlo y —cuando se puede— comprobar que el resultado no depende de
        él. Publicar un solo trazado sin decir que hay mil más es publicar media conclusión.</p>
""" + CIERRE


# =====================================================================
# MÓDULO 10 · La falacia ecológica
# =====================================================================
_barr = "".join(fila(ent(b["umbral"]), ent(b["n_municipios"]), n(b["r"], 5))
                for b in m10["barrido"])
_TABS_M10 = tabs(
    'El barrido de umbral',
    """library(data.table)
v &lt;- fread("precalculo/salidas/cap3_municipios_edu_madre.csv",
           colClasses = c(divipola = "character"))

for (u in c(0, 30, 300, 1000)) {
  s &lt;- v[n &gt;= u]
  cat(sprintf("n &gt;= %5d  %4d municipios  r = %+.4f\\n",
              u, nrow(s), cor(s$x, s$p)))
}
#&gt; n &gt;=     0  1114 municipios  r = +0.3033
#&gt; n &gt;=    30  1092 municipios  r = +0.3037
#&gt; n &gt;=   300   487 municipios  r = +0.5727
#&gt; n &gt;=  1000   141 municipios  r = +0.7173""",
    """import pandas as pd
v = pd.read_csv("precalculo/salidas/cap3_municipios_edu_madre.csv",
                dtype={"divipola": str})

for u in (0, 30, 300, 1000):
    s = v[v["n"] >= u]
    print(f"n >= {u:5d}  {len(s):4d} municipios  r = {s.x.corr(s.p):+.4f}")
#&gt; n &gt;=     0  1114 municipios  r = +0.3033
#&gt; n &gt;=    30  1092 municipios  r = +0.3037
#&gt; n &gt;=   300   487 municipios  r = +0.5727
#&gt; n &gt;=  1000   141 municipios  r = +0.7173""")


MOD10 = cabecera(
    10, "La falacia ecológica", "The ecological fallacy",
    "Distinguir una correlación entre agregados de una correlación entre individuos, y saber por qué no se deducen."
) + f"""      <p>El módulo 8 dejó una escalera: la misma relación mide
        {n(m10['r_individuo'], 5)} entre estudiantes, {n(m10['r_municipio'], 5)} entre
        municipios y {n(m10['r_departamento'], 5)} entre departamentos. La pregunta que queda
        es qué se puede decir con cada una, y la respuesta es la lección que Robinson publicó
        en 1950: <strong>una correlación entre agregados no dice nada directamente sobre los
        individuos que los componen</strong>. Suponer que sí es la falacia ecológica.</p>

      <p>Aquí las tres cifras van en la misma dirección, así que la falacia no salta a la vista
        —en el caso de Robinson llegaba a invertir el signo—. Pero la magnitud cambia lo
        bastante como para que una política dimensionada con la cifra departamental esté
        hablando de otra cosa que una dimensionada con la individual.</p>

{sim('cap3-falacia', 'La nube individual contra la nube agregada',
     'El puntaje medio por nivel educativo de la madre, y la misma relación vista entre municipios.', 300)}

      <p>Y hay una variante del error que es más sutil y más frecuente: <strong>la cifra
        agregada depende de a quién dejes entrar</strong>. Si se filtran los municipios por
        tamaño, la correlación se mueve sola:</p>

      <div class="table-wrapper">
        <table>
          <caption>Correlación municipal según el umbral de estudiantes por municipio.</caption>
          <thead><tr><th scope="col">Umbral (n ≥)</th><th scope="col">Municipios</th>
            <th scope="col">r</th></tr></thead>
          <tbody>
{_barr}          </tbody>
        </table>
      </div>

      <p>De {firma(n(m10['barrido'][0]['r'], 5))} sin filtrar a
        {firma(n(m10['barrido'][-1]['r'], 5))} con los municipios de mil estudiantes o más. Y
        ponderando por el número de estudiantes en vez de filtrar,
        {firma(n(m10['r_municipio_ponderado'], 5))}. Ninguna de las tres está mal calculada;
        las tres responden preguntas distintas, y <strong>publicar una sola sin decir cuál
        convierte una decisión metodológica en un hecho</strong>.</p>

      <div class="key-insight">
        <p style="margin:0;">La regla práctica: una correlación ecológica es válida como
        afirmación <em>sobre las unidades</em> —«los departamentos con madres más educadas
        puntúan más»— y no como afirmación sobre personas. Para lo segundo hace falta el dato
        individual, o un modelo que declare explícitamente cómo salta de un nivel al otro.</p>
      </div>

{_TABS_M10}
""" + CIERRE


# =====================================================================
# MÓDULO 11 · Cartografía y ética
# =====================================================================
_tipo = "".join(fila(t["tipo"], ent(t["n"]), n(t["media"], 5))
                for t in m11["por_tipo"])
_est = m11["estrato"]
_sp11 = m11["sin_poligono"]
_casos = "".join(
    f"""        <li><strong>{c['titulo']}</strong> ({c['anos']}). {c['leccion'].capitalize()}.
          <br><span class="text-sm text-gray-500">Fuente: {c['fuente']} · <a href="{c['url']}">{c['url']}</a></span></li>\n"""
    for c in m11["casos_citados"])
MOD11 = cabecera(
    11, "Cartografía y ética", "Maps, classification and consequence",
    "Reconocer que el sesgo entra por la unidad geográfica, y qué obligaciones impone eso al que dibuja el mapa."
) + f"""      <p>Los diez módulos anteriores han establecido una cosa técnica: la unidad geográfica y
        el esquema de clases son parámetros del análisis, y moverlos mueve el resultado. Este
        módulo saca la consecuencia. Cuando un mapa se usa para decidir —dónde va el
        presupuesto, quién recibe crédito, dónde patrulla la policía—, <strong>esos parámetros
        dejan de ser técnicos</strong>.</p>

      <p>El orden importa: primero la medida, después el juicio. Empecemos por un caso
        colombiano donde el dato está a mano.</p>

      <h3>Un caso de aviso: el estrato</h3>
      <p>La estratificación socioeconómica es, literalmente, una clasificación cartográfica
        oficial: a cada manzana le corresponde un estrato, y de él dependen tarifas y subsidios.
        Es cartografía estadística con consecuencia material. Miremos qué pasa al correlacionar
        el estrato medio municipal con el puntaje de Saber 11, sobre
        {firma(ent(_est['n_estudiantes']))} estudiantes en
        {firma(ent(_est['n_municipios']))} municipios.</p>

      <div class="warning-box">
        <h4>La misma variable, dos signos</h4>
        <p style="margin-bottom:0;">Sin filtrar, r = {firma(n(_est['r_sin_umbral'], 5))}:
        <strong>negativa</strong>. Con los {ent(_est['n_municipios_umbral_1000'])} municipios de
        mil estudiantes o más, r = {firma(n(_est['r_umbral_1000'], 5))}:
        <strong>positiva y fuerte</strong>. El signo lo decide un puñado de municipios diminutos,
        y la decisión de filtrarlos o no casi nunca se declara. Un informe que citara la primera
        cifra y otro que citara la segunda dirían cosas opuestas sin que ninguno mintiera en un
        número.</p>
      </div>

      <h3>Quien no tiene polígono no sale en el mapa</h3>
      <p>Hay un sesgo anterior a cualquier clasificación: existir en la capa. La cohorte trae
        {firma(ent(_sp11['n_estudiantes']))} estudiantes —el
        {firma(n(_sp11['pct_cohorte'], 5), ' %')}— cuyo código de municipio
        <strong>no corresponde a ningún polígono</strong> del marco geoestadístico:
        <strong>no salen en el mapa</strong>. Son de
        Belén de Bajirá, un territorio en disputa donde tres entidades del Estado dan tres
        respuestas distintas: el DIVIPOLA lo reconoce con un código, el ICFES codifica a sus
        estudiantes con otro, y la cartografía no tiene polígono para él.</p>

      <p>El efecto sobre las cifras es pequeño —la correlación departamental se mueve
        {firma(n(_sp11['desvio_departamental'], 5))}— y el efecto sobre las personas no lo es:
        esos estudiantes existen en la tabla y no en el mapa, así que cualquier política
        asignada cartográficamente los salta.</p>

{mapa_html('cap3-presencia', 'Municipios sin un solo estudiante en la cohorte 20224')}

      <p>La misma capa permite ver otra brecha, esta sí grande. Los territorios se clasifican
        por tipo, y el puntaje medio no es igual en todos:</p>

      <div class="table-wrapper">
        <table>
          <caption>Puntaje global medio por tipo de entidad territorial.</caption>
          <thead><tr><th scope="col">Tipo</th><th scope="col">Estudiantes</th>
            <th scope="col">Puntaje medio</th></tr></thead>
          <tbody>
{_tipo}          </tbody>
        </table>
      </div>

      <h3>Dos casos documentados, para poner nombre al patrón</h3>
      <p>El patrón —una clasificación por zonas que se convierte en criterio de decisión— tiene
        historia, y conviene conocerla con su fuente:</p>

      <ul>
{_casos}      </ul>

      <div class="key-insight">
        <p style="margin:0;">Lo que estos casos tienen en común no es la mala fe: es que
        <strong>la unidad geográfica sustituye al individuo</strong>. Un mapa asigna a cada
        persona el valor de su zona, y a partir de ahí la zona decide. Eso es la falacia
        ecológica del módulo 10 convertida en política, y es el motivo por el que el MAUP no es
        una curiosidad metodológica.</p>
      </div>

      <p>Las obligaciones que se derivan son técnicas, no morales, y por eso se pueden exigir:
        <strong>declarar</strong> la unidad, el esquema, el <em>k</em> y el filtro;
        <strong>comprobar</strong> que la conclusión aguanta otras elecciones razonables; y
        <strong>decir quién falta</strong> del mapa. Las tres se han hecho en este capítulo, y
        las tres se pueden pedir a cualquier mapa que llegue con una decisión detrás.</p>
""" + CIERRE


# =====================================================================
# MÓDULO 12 · Autoevaluación y ejercicios guiados
# =====================================================================
def ejercicio(k, e):
    """El marcado de la CASA, no uno inventado.

    La primera versión usaba `data-ejercicio` y `.ejercicio-solucion`, que
    no existen: `cuenta_sitio.py` contaba **cero ejercicios** sobre un
    capítulo que tiene cuatro, el desplegable no se cableaba, y el
    Checkpoint 2 exige que los tres capítulos del Corte I compartan el
    mismo conjunto de selectores. Es el mismo modo de fallo que la clase
    `.simulador-lienzo` inventada de A.13: marcado plausible que no
    existe, sin ningún error en consola.
    """
    pasos = "".join(
        f"                <tr><th scope=\"row\">{p['paso']}</th><td>{p['valor']}</td></tr>\n"
        for p in e["pasos"])
    return f"""
        <div class="ejercicio-guiado">
          <p class="ejercicio-enunciado"><span class="ejercicio-numero">{k}.</span><strong>{e['titulo']}.</strong>
            {e['enunciado'].replace('`', '')}</p>
          <div class="ejercicio-acciones">
            <button type="button" class="ejercicio-boton" aria-expanded="false" aria-controls="cap3-e{k}-sol">
              <i class="fas fa-key" aria-hidden="true"></i> Solución <i class="fas fa-chevron-down" aria-hidden="true"></i>
            </button>
          </div>
          <div class="ejercicio-panel solucion" id="cap3-e{k}-sol" hidden>
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


EJ = "".join(ejercicio(i + 1, e) for i, e in enumerate(S["ejercicios"]))

MOD12 = cabecera(
    12, "Autoevaluación y ejercicios guiados", "Self-assessment and guided exercises",
    "Comprobar lo aprendido y practicar las cuatro decisiones del capítulo sobre datos reales."
) + f"""      <p>El capítulo ha defendido una sola idea desde el módulo 1: el mismo dato produce mapas
        que dicen cosas distintas, y elegir el mapa es una decisión de modelado. Antes de pasar
        a los patrones puntuales conviene comprobar que la idea quedó, y sobre todo que quedaron
        sus consecuencias prácticas.</p>

      <p>Ocho preguntas, sin nota. Cada opción trae su explicación, así que equivocarse aquí
        vale tanto como acertar.</p>

{quiz_html('cap3-quiz', 'Autoevaluación del capítulo 3',
           'Ocho preguntas sobre clasificación, normalización, MAUP y falacia ecológica.')}

      <p>Y cuatro ejercicios guiados con su solución calculada. Los cuatro terminan en una
        decisión —qué publicar, qué exigir, qué declarar—, que es lo que este capítulo entrena
        de verdad.</p>

{EJ}
      <div class="tip-box">
        <h4>Los otros capítulos del Corte I</h4>
        <p style="margin-bottom:0;">Este capítulo cierra el Corte I. Los dos anteriores son
        <a href="capitulo-1-datos-espaciales.html">Datos espaciales y la primera ley de la
        geografía</a> y <a href="capitulo-2-crs-georreferenciacion.html">SIG, sistemas de
        referencia y georreferenciación con <code>sf</code></a>.</p>
      </div>

      <div class="tip-box">
        <h4>Lo que viene</h4>
        <p style="margin-bottom:0;">Con esto se cierra el Corte I.
        <a href="capitulo-4-patrones-puntuales.html">El capítulo 4</a> cambia de tipo
        de dato: deja los polígonos y pasa a los <strong>patrones puntuales</strong>, donde lo
        aleatorio no es el valor sino <em>la posición</em>. Y allí reaparece el MAUP con otro
        disfraz: el tamaño del cuadrante con que se cuenta un patrón es exactamente la misma
        decisión que el <em>k</em> de este capítulo, y su módulo 6 lo dice con esas palabras.</p>
      </div>
""" + CIERRE


MODULOS = (MOD1 + MOD2 + MOD3 + MOD4 + MOD5 + MOD6
           + MOD7 + MOD8 + MOD9 + MOD10 + MOD11 + MOD12)

NAV = "".join(
    f"""                <button type="button" class="nav-item{' active' if i == 1 else ''}" onclick="loadModule({i})"{' aria-current="page"' if i == 1 else ''}>
                    {t}
                </button>\n"""
    for i, t in enumerate([
        "Del dato al mapa", "Normalizar o mentir", "Esquemas de clasificación",
        "El mismo dato, cinco mapas", "Color", "La gramática del mapa temático",
        "Más allá del coropleto", "MAUP I · escala", "MAUP II · zonificación",
        "La falacia ecológica", "Cartografía y ética", "Autoevaluación y ejercicios"], 1))


# =====================================================================
# EL JAVASCRIPT
#
# Ni una cifra escrita aquí: todo sale de DATOS_CAP3 con n5(). Los mapas
# se registran con su JSON LITERAL —no con una función— porque
# `audita_texto_base.geomapas()` solo puede comprobar los cortes, el n y
# el peso de un mapa cuya fuente sea un objeto.
# =====================================================================
def geomapa(ident, clave, paleta=None, extra=""):
    fuente = json.dumps(M[clave], ensure_ascii=False)
    p = f", paleta: '{paleta}'" if paleta else ""
    return f"    GEOMAPAS['{ident}'] = {{ fuente: {fuente}{p}{extra} }};\n"


TITULOS = [
    ("Del dato al mapa", "Qué decisiones hay dentro de un coropleto"),
    ("Normalizar o mentir", "Conteos contra tasas"),
    ("Esquemas de clasificación", "Y por qué R y Python discrepan"),
    ("El mismo dato, cinco mapas", "La matriz de discordancia"),
    ("Color", "Paletas, luminosidad y daltonismo"),
    ("La gramática del mapa temático", "tmap 4, ggplot2 y GeoPandas"),
    ("Más allá del coropleto", "Símbolos, dot density, hexbin, cartogramas"),
    ("MAUP I · el efecto escala", "La correlación cambia al agregar"),
    ("MAUP II · el efecto zonificación", "Mil trazados del mismo país"),
    ("La falacia ecológica", "Agregados no son individuos"),
    ("Cartografía y ética", "El sesgo entra por la unidad geográfica"),
    ("Autoevaluación y ejercicios", "8 preguntas y 4 ejercicios"),
]

COURSE_DATA = (
    "    const courseData = {\n      modules: [\n"
    + "".join(f"        {{ id: {i + 1}, title: {json.dumps(t, ensure_ascii=False)}, "
              f"subtitle: {json.dumps(s, ensure_ascii=False)} }},\n"
              for i, (t, s) in enumerate(TITULOS))
    + "      ]\n    };\n\n"
    + "    // Todas las cifras del capítulo, tal como salieron del precálculo.\n"
    + "    // El JavaScript no lleva ninguna escrita: las saca de aquí.\n"
    + "    const DATOS_CAP3 = " + json.dumps(D, ensure_ascii=False) + ";\n"
    + "    const SOL_CAP3 = " + json.dumps(S, ensure_ascii=False) + ";\n"
    + "    const D3 = DATOS_CAP3;\n"
)


# =====================================================================
# Los mapas, con su JSON LITERAL (no una función): `geomapas()` del
# auditor de prosa solo puede comprobar los cortes, el n y el peso de un
# mapa cuya fuente sea un objeto.
# =====================================================================
def geomapa(ident, clave, paleta=None, extra=""):
    fuente = json.dumps(M[clave], ensure_ascii=False)
    pal = f", paleta: '{paleta}'" if paleta else ""
    return f"    GEOMAPAS['{ident}'] = {{ fuente: {fuente}{pal}{extra} }};\n"


# LA GEOMETRÍA MUNICIPAL SE INCRUSTA UNA SOLA VEZ, también aquí.
# El precálculo ya la comparte entre las cuatro capas; registrarla luego
# tres veces en el JS —una por cada div que la usa— la volvía a duplicar
# y el capítulo pesaba 954 KB en vez de 610. Es el mismo error dos
# capas más arriba, y solo se ve mirando el tamaño del archivo.
#
# `fuente` sigue siendo un OBJETO y no una función, que es lo que
# `audita_texto_base.geomapas()` necesita para poder comprobar los
# cortes, el n y el peso.
TABLA_RESPALDO = """    // La tabla de respaldo de los mapas de capas. Para quien no ve el
    // mapa, ESTO es el mapa: por eso describe la capa y el esquema que
    // están activos, y no una vista fija.
    function tablaCapa(d, capa, vista) {
      const cp = (d.capas && d.capas.length)
        ? (typeof capa === 'string' ? d.capas.find(c => c.id === capa) : d.capas[capa || 0])
        : d;
      const base = cp || d;
      const v = (base.vistas && vista != null && base.vistas[vista]) || base;
      const filas = (v.tam || []).map((t, i) =>
        `<tr><th scope="row">${n5(v.cortes[i], 2)} – ${n5(v.cortes[i + 1], 2)}</th>` +
        `<td>${t}</td><td>${n5(100 * t / d.n, 2)} %</td></tr>`).join('');
      const sin = v.n_sin_dato
        ? `<tr><th scope="row">sin dato</th><td>${v.n_sin_dato}</td>` +
          `<td>${n5(100 * v.n_sin_dato / d.n, 2)} %</td></tr>` : '';
      return `<table><caption>${base.etiqueta || d.titulo} · esquema ` +
        `${v.estilo} (n = ${d.n}).</caption><thead><tr>` +
        `<th scope="col">Clase</th><th scope="col">Unidades</th>` +
        `<th scope="col">%</th></tr></thead><tbody>${filas}${sin}</tbody></table>`;
    }

"""


GEOMAPAS_JS = (
    "    // Estado de los mapas conmutables del capítulo.\n"
    "    let ncVista = 1, desVista = 1, ctCapa = 'conteo', cartoSuper = [];\n\n"
    + "    // Los 1 122 municipios, UNA sola vez: tres mapas del capítulo\n"
      "    // los comparten y solo cambian de capa.\n"
    + "    const MAPA_MUNICIPIOS = " + json.dumps(M["municipios"], ensure_ascii=False) + ";\n\n"
    + TABLA_RESPALDO
    + geomapa('cap3-nc', 'nc_esquemas', 'verde',
              ", get vista() { return ncVista; }"
              ", etiqueta: 'Los 100 condados de Carolina del Norte coloreados por SID74,"
              " con el esquema de clasificación que se elija.'"
              ", tabla: d => tablaCapa(d, 0, ncVista)")
    + "    GEOMAPAS['cap3-desercion'] = { fuente: MAPA_MUNICIPIOS, paleta: 'naranja',"
      " capa: 'desercion', get vista() { return desVista; },"
      " etiqueta: 'Los 1 122 municipios de Colombia coloreados por su tasa de deserción"
      " escolar, con el esquema de clasificación que se elija.',"
      " tabla: d => tablaCapa(d, 'desercion', desVista) };\n"
    + "    GEOMAPAS['cap3-conteo-tasa-mapa'] = { fuente: MAPA_MUNICIPIOS, paleta: 'verde',"
      " get capa() { return ctCapa; },"
      " etiqueta: 'Los 1 122 municipios coloreados por el conteo de estudiantes o por su"
      " puntaje medio, según lo que se elija.',"
      " tabla: d => tablaCapa(d, ctCapa, null) };\n"
    + "    GEOMAPAS['cap3-presencia'] = { fuente: MAPA_MUNICIPIOS, paleta: 'divergente',"
      " capa: 'presencia',"
      " etiqueta: 'Los 1 122 municipios, distinguiendo los que aportan al menos un"
      " estudiante a la cohorte de los que no aportan ninguno.',"
      " tabla: d => tablaCapa(d, 'presencia', null) };\n"
    + geomapa('cap3-carto', 'dep_coropleto', 'verde', ", get superpuestas() { return cartoSuper; }")
    + geomapa('cap3-carto-ncont', 'dep_ncont', 'verde')
    + geomapa('cap3-carto-dorling', 'dep_dorling', 'verde')
    + geomapa('cap3-carto-cont', 'dep_cont', 'verde')
    + geomapa('cap3-hexbin', 'dep_hexbin', 'naranja')
)

SIMULADORES_JS = f"""
    // --- los simuladores --------------------------------------------
    //
    // `n5` NO lo trae la plantilla: lo define cada capítulo. Suponerlo
    // costó un ReferenceError que se llevó por delante
    // `iniciarSimuladores()` entero — el mismo modo de fallo del defecto
    // nº 4 de A.13, y con la misma causa: escribir de memoria el nombre
    // de una función en vez de comprobarlo.
    const n5 = (x, d) => Number(x).toFixed(d == null ? 5 : d);
    const miles3 = x => Math.round(Number(x)).toLocaleString('es-ES').replace(/\./g, '\u202f');

    // CONTRATO DEL MOTOR: un simulador DEVUELVE sus gráficos. No existe
    // `registrarGrafico` — escribirla de memoria costó un ReferenceError
    // que se llevó por delante iniciarSimuladores() entero (A.13, nº 4).
    const C3 = {{ verde: '#1a7358', naranja: '#FF6600', gris: '#8a8a8a',
                 azul: '#0072B2', rojo: '#D55E00' }};

    function lectura3(raiz, pares) {{
      const c = raiz.querySelector('.simulador-lectura');
      if (!c) return;
      c.innerHTML = pares.map(([k, v]) =>
        `<span class="lectura-item"><span class="lectura-etiqueta">${{k}}</span>` +
        `<span class="lectura-valor">${{v}}</span></span>`).join('');
    }}

    function botones3(raiz, ops, alPulsar, activo) {{
      const cont = raiz.querySelector('.simulador-controles');
      if (!cont) return;
      cont.innerHTML = '';
      ops.forEach((op, i) => {{
        const b = document.createElement('button');
        b.className = 'sim-btn' + (i === (activo || 0) ? ' active' : '');
        b.textContent = op.etiqueta;
        b.onclick = () => {{
          cont.querySelectorAll('.sim-btn').forEach(x => x.classList.remove('active'));
          b.classList.add('active');
          alPulsar(op.valor);
        }};
        cont.appendChild(b);
      }});
    }}

    // Módulo 1 · las 35 configuraciones
    SIMULADORES['cap3-config'] = function (raiz) {{
      const ESQ = ['equal', 'quantile', 'fisher', 'sd', 'headtails'];
      const ETQ = ['Intervalos iguales', 'Cuantiles', 'Fisher-Jenks',
                   'Desviación estándar', 'Head/tails'];
      const capa = D3 && null;
      const mapaMun = GEOMAPAS['cap3-desercion'].fuente;
      const cp = mapaMun.capas.find(c => c.id === 'desercion');
      let iEsq = 1;
      const ctx = raiz.querySelector('canvas').getContext('2d');
      const g = new Chart(ctx, {{
        type: 'bar',
        data: {{ labels: [], datasets: [{{ label: 'municipios por clase', data: [],
                 backgroundColor: C3.verde }}] }},
        options: {{ responsive: true, maintainAspectRatio: false,
          scales: {{ y: {{ beginAtZero: true, title: {{ display: true, text: 'municipios' }} }} }} }}
      }});
      const pinta = () => {{
        const v = cp.vistas[iEsq];
        g.data.labels = v.tam.map((_, i) => 'clase ' + (i + 1));
        g.data.datasets[0].data = v.tam;
        g.update();
        lectura3(raiz, [
          ['esquema', ETQ[iEsq]],
          ['en la clase más alta', v.tam[v.tam.length - 1] + ' municipios'],
          ['clases vacías', v.tam.filter(t => t === 0).length],
          ['configuraciones del capítulo', D3.m1.n_configuraciones],
          ['mapas realmente distintos', D3.m1.n_mapas_distintos]
        ]);
      }};
      botones3(raiz, ESQ.map((e, i) => ({{ etiqueta: ETQ[i], valor: i }})),
               i => {{ iEsq = i; pinta(); }}, 1);
      pinta();
      return [g];
    }};

    // Módulo 2 · conteo contra tasa
    SIMULADORES['cap3-conteo-tasa'] = function (raiz) {{
      const t = D3.m2;
      const ctx = raiz.querySelector('canvas').getContext('2d');
      let modo = 'conteo';
      const g = new Chart(ctx, {{
        type: 'bar',
        data: {{ labels: [], datasets: [{{ label: '', data: [], backgroundColor: C3.verde }}] }},
        options: {{ indexAxis: 'y', responsive: true, maintainAspectRatio: false,
          scales: {{ x: {{ beginAtZero: true }} }} }}
      }});
      const pinta = () => {{
        const lista = modo === 'conteo' ? t.top10_conteo : t.top10_tasa;
        g.data.labels = lista.map(x => x.municipio);
        g.data.datasets[0].data = lista.map(x => modo === 'conteo' ? x.n : x.punt);
        g.data.datasets[0].label = modo === 'conteo' ? 'estudiantes' : 'puntaje medio';
        g.data.datasets[0].backgroundColor = modo === 'conteo' ? C3.verde : C3.naranja;
        g.update();
        ctCapa = modo === 'conteo' ? 'conteo' : 'tasa';
        const el = document.querySelector('[data-geomapa="cap3-conteo-tasa-mapa"]');
        if (el && el.__geomapa) el.__geomapa.dibuja();
        lectura3(raiz, [
          ['r de Pearson', n5(t.r_conteo_tasa)],
          ['rho de Spearman', n5(t.rho_conteo_tasa)],
          ['comparten del top-20', t.solape_top20 + ' de 20'],
          ['estudiantes en los 10 mayores', n5(t.pct_estudiantes_top10, 2) + ' %']
        ]);
      }};
      botones3(raiz, [{{ etiqueta: 'Conteo de estudiantes', valor: 'conteo' }},
                      {{ etiqueta: 'Puntaje medio', valor: 'tasa' }}],
               m => {{ modo = m; pinta(); }});
      pinta();
      return [g];
    }};

    // Módulo 3 · los cinco esquemas sobre SID74
    SIMULADORES['cap3-esquemas'] = function (raiz) {{
      const E = D3.m3.esquemas;
      const ctx = raiz.querySelector('canvas').getContext('2d');
      const g = new Chart(ctx, {{
        type: 'bar',
        data: {{ labels: E.map(e => e.etiqueta),
                datasets: [0, 1, 2, 3, 4].map(k => ({{
                  label: 'clase ' + (k + 1),
                  data: E.map(e => e.tam[k]),
                  backgroundColor: ['#e8f3ef', '#b8ddd0', '#7cc0aa', '#3f9c7f', '#1a7358'][k]
                }})) }},
        options: {{ responsive: true, maintainAspectRatio: false,
          scales: {{ x: {{ stacked: true }},
                    y: {{ stacked: true, beginAtZero: true,
                         title: {{ display: true, text: 'condados' }} }} }} }}
      }});
      lectura3(raiz, [
        ['condados', D3.m3.n],
        ['empatados en un corte', D3.m3.n_empatados],
        ['convenio de R', D3.m3.convenio_r],
        ['convenio de Python', D3.m3.convenio_python]
      ]);
      return [g];
    }};

    // Módulo 7 · hasta dónde llega cada cartograma
    SIMULADORES['cap3-carto-sim'] = function (raiz) {{
      const C = D3.m7.cartogramas, B = D3.m7.barrido_contiguo;
      const ctx = raiz.querySelector('canvas').getContext('2d');
      const g = new Chart(ctx, {{
        type: 'bar',
        data: {{ labels: C.map(c => c.id),
                datasets: [{{ label: 'corr(área, valor)', data: C.map(c => c.corr),
                             backgroundColor: C.map(c => c.corr > 0.999 ? C3.verde : C3.naranja) }}] }},
        options: {{ responsive: true, maintainAspectRatio: false,
          scales: {{ y: {{ beginAtZero: true, max: 1.05,
                          title: {{ display: true, text: 'correlación entre área y valor' }} }} }} }}
      }});
      lectura3(raiz, [
        ['Olson (propio)', n5(C[0].corr, 6)],
        ['Dorling (propio)', n5(C[1].corr, 6)],
        ['Dougenik (paquete)', n5(C[2].corr, 6)],
        ['y su error tras ' + B[B.length - 1].itermax + ' iteraciones',
         n5(B[B.length - 1].max_error_rel, 5)]
      ]);
      return [g];
    }};

    // Módulo 4 · la matriz de discordancia
    SIMULADORES['cap3-discordancia'] = function (raiz) {{
      const p = D3.m4.pares.slice().sort((a, b) => b.pct_cambian - a.pct_cambian);
      const ctx = raiz.querySelector('canvas').getContext('2d');
      const g = new Chart(ctx, {{
        type: 'bar',
        data: {{ labels: p.map(x => x.a + ' / ' + x.b),
                datasets: [{{ label: '% que cambia de clase', data: p.map(x => x.pct_cambian),
                             backgroundColor: p.map(x => x.pct_cambian > 50 ? C3.rojo : C3.verde) }}] }},
        options: {{ responsive: true, maintainAspectRatio: false,
          scales: {{ y: {{ beginAtZero: true, max: 100,
                          title: {{ display: true, text: '% de municipios' }} }} }} }}
      }});
      lectura3(raiz, [
        ['máximo', n5(D3.m4.pct_max, 2) + ' %'],
        ['mínimo', n5(D3.m4.pct_min, 2) + ' %'],
        ['estables en los cinco', D3.m4.n_estables + ' de ' + D3.m4.n],
        ['en la clase más alta', D3.m4.n_en_clase_alta.join(' / ')]
      ]);
      return [g];
    }};

    // Módulo 5 · las paletas bajo daltonismo
    SIMULADORES['cap3-paletas'] = function (raiz) {{
      const P = D3.m5.paletas;
      let iTipo = 0;
      const ctx = raiz.querySelector('canvas').getContext('2d');
      const g = new Chart(ctx, {{
        type: 'bar',
        data: {{ labels: P.map(p => p.id), datasets: [] }},
        options: {{ responsive: true, maintainAspectRatio: false,
          scales: {{ y: {{ beginAtZero: true, title: {{ display: true, text: 'ΔE mínimo entre clases' }} }} }} }}
      }});
      const pinta = () => {{
        g.data.datasets = [
          {{ label: 'visión normal', data: P.map(p => p.dmin_normal), backgroundColor: C3.verde }},
          {{ label: D3.m5.tipos[iTipo], data: P.map(p => p.simulaciones[iTipo].dmin),
            backgroundColor: C3.naranja }}
        ];
        g.update();
        const peor = P.slice().sort((a, b) =>
          b.simulaciones[iTipo].caida_pct - a.simulaciones[iTipo].caida_pct)[0];
        lectura3(raiz, [
          ['tipo simulado', D3.m5.tipos[iTipo]],
          ['la que más cae', peor.id + ' (' + n5(peor.simulaciones[iTipo].caida_pct, 2) + ' %)'],
          ['su recorrido de L*', n5(peor.rango_luminosidad, 2)],
          ['rojo/verde a igual L*', n5(D3.m5.rojo_verde.caida_pct, 2) + ' % menos']
        ]);
      }};
      botones3(raiz, D3.m5.tipos.map((t, i) => ({{ etiqueta: t, valor: i }})),
               i => {{ iTipo = i; pinta(); }});
      pinta();
      return [g];
    }};

    // Módulo 8 · la curva de escala
    SIMULADORES['cap3-escala'] = function (raiz) {{
      const c = D3.m8.curva;
      const ctx = raiz.querySelector('canvas').getContext('2d');
      const g = new Chart(ctx, {{
        type: 'line',
        data: {{ labels: c.map(x => x.zonas),
                datasets: [
                  {{ label: 'r medio de 30 particiones contiguas', data: c.map(x => x.media),
                    borderColor: C3.verde, backgroundColor: 'rgba(26,115,88,.12)', tension: .3 }},
                  {{ label: 'r con los 33 departamentos reales',
                    data: c.map(() => D3.m8.cartografica.r_departamento),
                    borderColor: C3.naranja, borderDash: [6, 4], pointRadius: 0 }},
                  {{ label: 'r a nivel de estudiante', data: c.map(() => D3.m8.r_individuo),
                    borderColor: C3.gris, borderDash: [2, 3], pointRadius: 0 }}
                ] }},
        options: {{ responsive: true, maintainAspectRatio: false,
          scales: {{ y: {{ title: {{ display: true, text: 'correlación' }} }},
                    x: {{ title: {{ display: true, text: 'número de zonas' }} }} }} }}
      }});
      lectura3(raiz, [
        ['individuo', n5(D3.m8.r_individuo)],
        ['municipio', n5(D3.m8.r_municipio)],
        ['departamento', n5(D3.m8.r_departamento)],
        ['varianza entre municipios', n5(D3.m8.pct_var_entre, 2) + ' %']
      ]);
      return [g];
    }};

    // Módulo 9 · las mil zonificaciones
    SIMULADORES['cap3-zonificacion'] = function (raiz) {{
      const h = D3.m9.hist_contiguas, ha = D3.m9.hist_arbitrarias;
      let cual = 'contiguas';
      const ctx = raiz.querySelector('canvas').getContext('2d');
      const g = new Chart(ctx, {{
        type: 'bar',
        data: {{ labels: [], datasets: [{{ label: 'particiones', data: [], backgroundColor: C3.verde }}] }},
        options: {{ responsive: true, maintainAspectRatio: false,
          scales: {{ y: {{ beginAtZero: true, title: {{ display: true, text: 'particiones' }} }},
                    x: {{ title: {{ display: true, text: 'correlación de la partición' }} }} }} }}
      }});
      const pinta = () => {{
        const H = cual === 'contiguas' ? h : ha;
        const f = cual === 'contiguas' ? D3.m9.contiguas : D3.m9.arbitrarias;
        g.data.labels = H.conteo.map((_, i) => n5((H.cortes[i] + H.cortes[i + 1]) / 2, 2));
        g.data.datasets[0].data = H.conteo;
        g.data.datasets[0].backgroundColor = cual === 'contiguas' ? C3.verde : C3.azul;
        g.update();
        lectura3(raiz, [
          ['trazado real', n5(D3.m9.r_real)],
          ['media de las 1 000', n5(f.media)],
          ['recorrido', n5(f.min) + ' a ' + n5(f.max)],
          ['percentil del real', n5(f.percentil_real, 2)]
        ]);
      }};
      botones3(raiz, [{{ etiqueta: 'Zonas contiguas', valor: 'contiguas' }},
                      {{ etiqueta: 'Zonas arbitrarias', valor: 'arbitrarias' }}],
               c => {{ cual = c; pinta(); }});
      pinta();
      return [g];
    }};

    // Módulo 9 · el gerrymandering
    SIMULADORES['cap3-gerry'] = function (raiz) {{
      const G = D3.m9.gerrymandering;
      let iEj = 0;
      const ctx = raiz.querySelector('canvas').getContext('2d');
      const g = new Chart(ctx, {{
        type: 'bar',
        data: {{ labels: [], datasets: [
          {{ label: 'casillas de A', data: [], backgroundColor: C3.naranja }},
          {{ label: 'casillas de B', data: [], backgroundColor: C3.azul }}] }},
        options: {{ responsive: true, maintainAspectRatio: false,
          scales: {{ x: {{ stacked: true }},
                    y: {{ stacked: true, beginAtZero: true, max: G.casillas_por_distrito,
                         title: {{ display: true, text: 'casillas' }} }} }} }}
      }});
      const pinta = () => {{
        const ej = G.ejemplos[iEj];
        const A = [], B = [];
        for (let d = 1; d <= G.n_distritos; d++) {{
          let a = 0, b = 0;
          ej.particion.forEach((z, i) => {{ if (z === d) (G.rejilla[i] ? a++ : b++); }});
          A.push(a); B.push(b);
        }}
        g.data.labels = A.map((_, i) => 'distrito ' + (i + 1));
        g.data.datasets[0].data = A;
        g.data.datasets[1].data = B;
        g.update();
        lectura3(raiz, [
          ['votos de A', n5(G.pct_A, 2) + ' %'],
          ['escaños proporcionales', n5(G.escanos_proporcionales, 2)],
          ['escaños de A con este trazado', ej.escanos_A + ' de ' + G.n_distritos],
          ['recorrido posible', G.escanos_min + ' a ' + G.escanos_max]
        ]);
      }};
      botones3(raiz, G.ejemplos.map((e, i) => ({{
        etiqueta: e.escanos_A + ' escaños para A', valor: i }})),
               i => {{ iEj = i; pinta(); }});
      pinta();
      return [g];
    }};

    // Módulo 10 · la falacia ecológica
    SIMULADORES['cap3-falacia'] = function (raiz) {{
      const nu = D3.m10.nube_individual;
      const ctx = raiz.querySelector('canvas').getContext('2d');
      const g = new Chart(ctx, {{
        type: 'line',
        data: {{ labels: nu.map(x => D3.m10.niveles_edu[x.nivel] || x.nivel),
                datasets: [{{ label: 'puntaje medio por nivel (individual)',
                             data: nu.map(x => x.media), borderColor: C3.verde,
                             backgroundColor: 'rgba(26,115,88,.12)', tension: .2 }}] }},
        options: {{ responsive: true, maintainAspectRatio: false,
          scales: {{ y: {{ title: {{ display: true, text: 'puntaje global medio' }} }} }} }}
      }});
      lectura3(raiz, [
        ['individuo', n5(D3.m10.r_individuo)],
        ['municipio', n5(D3.m10.r_municipio)],
        ['municipio ponderado', n5(D3.m10.r_municipio_ponderado)],
        ['departamento', n5(D3.m10.r_departamento)]
      ]);
      return [g];
    }};
"""


QUIZ_JS = f"""
    // --- la autoevaluación -------------------------------------------
    // Los cuatro tipos que el motor conoce: opcion, multiple, numerica y
    // grafico. Inventarse un tipo tumba media página (A.12, nº 2).
    AUTOEVALUACIONES['cap3-quiz'] = [
      {{
        tipo: 'opcion',
        pregunta: 'Un mapa muestra el NÚMERO de casos de una enfermedad por municipio. ¿Qué está mostrando sobre todo?',
        opciones: [
          {{ texto: 'Dónde vive más gente', correcta: true,
            respuesta: 'Exacto. Un conteo es casi siempre un mapa de población. En este capítulo, los 10 municipios más oscuros del mapa de conteos concentran el ' + n5(D3.m2.pct_estudiantes_top10, 2) + ' % de los estudiantes.' }},
          {{ texto: 'Dónde el riesgo es mayor',
            respuesta: 'No: para eso hace falta normalizar por población. El conteo y la tasa ordenan el país de formas casi independientes — aquí su rho de Spearman es ' + n5(D3.m2.rho_conteo_tasa) + '.' }},
          {{ texto: 'Dónde el sistema de salud funciona peor',
            respuesta: 'No, y menos aún: eso exigiría normalizar y además controlar por otros factores.' }},
          {{ texto: 'Nada: los conteos no se pueden mapear',
            respuesta: 'Sí se pueden, y a veces conviene (un cartograma con conteos es informativo). Lo que no se puede es leerlos como si fueran tasas.' }}
        ] }},
      {{
        tipo: 'opcion',
        pregunta: '¿Por qué classInt (R) y mapclassify (Python) dan clases distintas con "quantile" sobre el mismo dato?',
        opciones: [
          {{ texto: 'Porque cierran el intervalo por lados distintos y hay empates justo en los cortes', correcta: true,
            respuesta: 'Eso es. R usa [a, b) y Python (a, b]. En SID74 hay ' + D3.m3.n_empatados + ' condados empatados justo en un corte, y ahí se decide todo.' }},
          {{ texto: 'Porque usan algoritmos de cuantiles distintos',
            respuesta: 'No: los cuantiles coinciden. Lo que difiere es a qué lado del corte va un valor que cae exactamente encima.' }},
          {{ texto: 'Por errores de redondeo en coma flotante',
            respuesta: 'No. La diferencia es sistemática y se reproduce exactamente; el redondeo daría discrepancias erráticas.' }},
          {{ texto: 'Porque Python ordena los datos y R no',
            respuesta: 'Los dos ordenan. La diferencia es el convenio del intervalo.' }}
        ] }},
      {{
        tipo: 'multiple',
        pregunta: '¿Cuáles de estas decisiones cambian el mapa sin cambiar ni un dato? (varias)',
        opciones: [
          {{ texto: 'El esquema de clasificación', correcta: true,
            respuesta: 'Sí: entre los dos esquemas más discordantes cambia de clase el ' + n5(D3.m4.pct_max, 2) + ' % de los municipios.' }},
          {{ texto: 'El número de clases k', correcta: true,
            respuesta: 'Sí: las ' + D3.m1.n_configuraciones + ' combinaciones de esquema y k producen ' + D3.m1.n_mapas_distintos + ' particiones distintas.' }},
          {{ texto: 'La unidad territorial de agregación', correcta: true,
            respuesta: 'Sí, y es la más consecuente: es el MAUP.' }},
          {{ texto: 'El número de decimales con que se guarda el dato',
            respuesta: 'Con estos datos no: los cortes no caen en decimales tan finos. No es de la misma familia que las otras tres.' }}
        ] }},
      {{
        tipo: 'numerica',
        pregunta: 'Con k = 5 y la deserción municipal, ¿cuántos municipios reciben la MISMA clase bajo los cinco esquemas?',
        respuesta: D3.m4.n_estables, tolerancia: 0,
        pista: 'Son menos del 20 % de los ' + D3.m4.n + ' municipios con dato.',
        explicacion: 'Solo ' + D3.m4.n_estables + ' de ' + D3.m4.n + ' — el ' + n5(D3.m4.pct_estables, 2) + ' %. Para los demás, la clase es una consecuencia del esquema.' }},
      {{
        tipo: 'opcion',
        pregunta: 'Una paleta rojo-verde se ve perfectamente en tu pantalla. ¿Basta con eso?',
        opciones: [
          {{ texto: 'No: hay que medir si sobrevive al daltonismo, y lo que la salva es el recorrido de luminosidad', correcta: true,
            respuesta: 'Exacto. Un rojo y un verde a la MISMA luminosidad pierden el ' + n5(D3.m5.rojo_verde.caida_pct, 2) + ' % de su distancia perceptual bajo deuteranopía.' }},
          {{ texto: 'Sí, si los colores son suficientemente distintos',
            respuesta: '«Distintos» para quién. La distancia hay que medirla en un espacio perceptual y bajo la visión del lector, no de quien dibuja.' }},
          {{ texto: 'Basta con añadir una leyenda clara',
            respuesta: 'La leyenda ayuda, pero si dos clases del mapa son indistinguibles el lector no puede usarla.' }},
          {{ texto: 'Solo importa si el mapa se va a imprimir',
            respuesta: 'Importa siempre: alrededor del 8 % de los hombres tiene alguna forma de daltonismo.' }}
        ] }},
      {{
        tipo: 'opcion',
        pregunta: 'La correlación educación-puntaje vale ' + n5(D3.m8.r_individuo, 4) + ' entre estudiantes y ' + n5(D3.m8.r_departamento, 4) + ' entre departamentos. ¿Por qué sube?',
        opciones: [
          {{ texto: 'Porque al agregar se destruye la variación dentro de las unidades y solo queda la de entre unidades', correcta: true,
            respuesta: 'Eso es. Aquí la varianza entre municipios es apenas el ' + n5(D3.m8.pct_var_entre, 2) + ' % de la total: el resto desaparece al promediar.' }},
          {{ texto: 'Porque hay menos observaciones y el ruido baja',
            respuesta: 'El número de observaciones afecta a la precisión, no al valor esperado de la correlación. Lo que cambia es qué variación queda.' }},
          {{ texto: 'Porque los departamentos son más homogéneos',
            respuesta: 'Al revés: son más heterogéneos entre sí. Lo que se pierde es la heterogeneidad interna.' }},
          {{ texto: 'Es un artefacto del cálculo y no significa nada',
            respuesta: 'No es un artefacto: es un efecto real y sistemático, y tiene nombre — el efecto escala del MAUP.' }}
        ] }},
      {{
        tipo: 'opcion',
        pregunta: 'Manteniendo 33 zonas y cambiando solo dónde van las fronteras, ¿qué le pasa a la correlación?',
        opciones: [
          {{ texto: 'Varía mucho: sobre 1 000 trazados contiguos va de ' + n5(D3.m9.contiguas.min, 3) + ' a ' + n5(D3.m9.contiguas.max, 3), correcta: true,
            respuesta: 'Sí. Y el trazado departamental real cae en el percentil ' + n5(D3.m9.contiguas.percentil_real, 1) + ': no tiene nada de especial.' }},
          {{ texto: 'No cambia: con el mismo número de zonas el resultado es el mismo',
            respuesta: 'Eso sería cierto si solo importara la escala. El efecto zonificación dice justo lo contrario.' }},
          {{ texto: 'Cambia poco, dentro del error de muestreo',
            respuesta: 'El recorrido es de ' + n5(D3.m9.recorrido_contiguas, 3) + ' unidades de correlación: mucho más que cualquier error de muestreo.' }},
          {{ texto: 'Baja siempre, porque las zonas aleatorias son peores',
            respuesta: 'Ni baja siempre ni las aleatorias son «peores»: con ponderación por tamaño, las arbitrarias dan una media MÁS alta (' + n5(D3.m9.arbitrarias.media, 3) + ').' }}
        ] }},
      {{
        tipo: 'opcion',
        pregunta: 'Un informe dice: «en los departamentos con madres más educadas se puntúa más, luego un estudiante con madre más educada puntúa más». ¿Qué falla?',
        opciones: [
          {{ texto: 'Salta del nivel agregado al individual sin justificarlo: es la falacia ecológica', correcta: true,
            respuesta: 'Exacto. Aquí las dos correlaciones existen pero valen cosas distintas (' + n5(D3.m10.r_departamento, 3) + ' y ' + n5(D3.m10.r_individuo, 3) + '), y en otros casos hasta cambian de signo.' }},
          {{ texto: 'Nada: si vale para los departamentos, vale para las personas',
            respuesta: 'No se deduce. Una correlación entre agregados es una afirmación sobre las unidades, no sobre quienes las componen.' }},
          {{ texto: 'Que la correlación no implica causalidad',
            respuesta: 'También es cierto, pero el error específico aquí es otro: el salto de nivel.' }},
          {{ texto: 'Que 33 departamentos son pocos para correlacionar',
            respuesta: 'El tamaño afecta a la precisión, no al problema de nivel. Con 1 000 departamentos la falacia seguiría siendo falacia.' }}
        ] }}
    ];
"""


CABLEADO_JS = f"""
    // --- cableado del conmutador de daltonismo ------------------------
    // No es de este capítulo: es del motor, así que alcanza también a los
    // mapas de los capítulos 1 y 2.
    function cablearCap3() {{
      const c = mainContent.querySelector('#cap3-ctrl-cvd');
      if (c) c.addEventListener('click', ev => {{
        const b = ev.target.closest('.geomapa-boton');
        if (!b) return;
        c.querySelectorAll('.geomapa-boton').forEach(x => x.classList.remove('activo'));
        b.classList.add('activo');
        geomapaConmutaCVD(b.dataset.cvd || null);
      }});
      const nc = mainContent.querySelector('[data-geomapa="cap3-nc"]');
      if (nc) controlesMapa3(nc, ['equal', 'quantile', 'fisher', 'sd', 'headtails'],
        ['Intervalos iguales', 'Cuantiles', 'Fisher-Jenks', 'Desv. estándar', 'Head/tails'],
        i => {{ ncVista = i; }}, 1);
      const de = mainContent.querySelector('[data-geomapa="cap3-desercion"]');
      if (de) controlesMapa3(de, ['equal', 'quantile', 'fisher', 'sd', 'headtails'],
        ['Intervalos iguales', 'Cuantiles', 'Fisher-Jenks', 'Desv. estándar', 'Head/tails'],
        i => {{ desVista = i; }}, 1);
      const ca = mainContent.querySelector('[data-geomapa="cap3-carto"]');
      if (ca) controlesMapa3(ca, ['nada', 'simbolos', 'densidad'],
        ['Solo coropleto', 'Símbolos proporcionales', 'Dot density'],
        i => {{ cartoSuper = i === 0 ? [] : [i === 1 ? 'simbolos' : 'densidad']; }}, 0);
    }}

    function controlesMapa3(raiz, valores, etiquetas, alPulsar, activo) {{
      // El contenedor es HERMANO del mapa, no hijo: `iniciarGeomapas()`
      // reescribe el innerHTML del div del mapa y se lo llevaría por
      // delante. Se busca por el id que le puso `mapa_html`.
      const cont = document.getElementById('ctrl-' + raiz.dataset.geomapa);
      if (!cont) return;
      cont.innerHTML = '';
      etiquetas.forEach((etq, i) => {{
        const b = document.createElement('button');
        b.type = 'button';
        b.className = 'geomapa-boton' + (i === activo ? ' activo' : '');
        b.textContent = etq;
        b.onclick = () => {{
          cont.querySelectorAll('.geomapa-boton').forEach(x => x.classList.remove('activo'));
          b.classList.add('activo');
          alPulsar(i);
          raiz.__geomapa.dibuja();
        }};
        cont.appendChild(b);
      }});
    }}
"""


# =====================================================================
# Guardas de sustitución
#
# Cada ancla tiene que aparecer EXACTAMENTE UNA VEZ, y una región
# sustituida declara tope MÁXIMO Y MÍNIMO. El mínimo está porque en T1.2
# un ancla de cierre casó demasiado pronto, dejó media sección viva, y el
# archivo salió bien formado y el informe en verde (A.12, nº 1).
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
    print(f"\n=== ensambla_cap3.py ===\nplantilla: {len(doc)/1024:.0f} KB\n")

    doc = sustituye(doc, "<title>Plantilla de capítulo — Estadística Espacial</title>",
                    "<title>Capítulo 3 · Cartografía estadística y el MAUP — "
                    "Estadística Espacial</title>", "título")
    doc = sustituye(doc, "PLANTILLA BASE •\n              5 MÓDULOS DE DEMOSTRACIÓN • UNBOSQUE 2026-II",
                    "CAPÍTULO 3 • CARTOGRAFÍA ESTADÍSTICA Y EL MAUP •\n"
                    f"              SEMANA {D['meta']['semana']} • UNBOSQUE 2026-II",
                    "subtítulo de la cabecera")
    doc = sustituye(doc, "Estadística Espacial (20929) • Plantilla de\n          capítulo • UnBosque 2026-II",
                    "Estadística Espacial (20929) • Capítulo 3 de 10 •\n"
                    f"          Semana {D['meta']['semana']} • UnBosque 2026-II", "pie")

    doc = reemplaza_region(doc, "    const courseData = {", "\n    };\n", COURSE_DATA,
                           "courseData + DATOS_CAP3", max_lineas=20)

    doc = reemplaza_region(
        doc,
        "  <!-- ============================================================ -->\n"
        "  <!-- MÓDULO 1 · Cajas y tipografía",
        "\n  <script>", MODULOS.lstrip("\n") + "\n  <script>",
        "los doce módulos", max_lineas=600)

    vieja = [l for l in doc.splitlines() if l.startswith("    GEOMAPAS['demo-mapa'] =")]
    if len(vieja) != 1:
        sys.exit(f"PARADO: {len(vieja)} registros de GEOMAPAS['demo-mapa'], se esperaba 1")
    doc = sustituye(doc, vieja[0], GEOMAPAS_JS.rstrip("\n"), "los nueve .geomapa")

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
        SIMULADORES_JS + "\n" + CABLEADO_JS
        + "\n    // ================================================================\n"
          "    // Autoevaluación de demostración: una pregunta de cada tipo\n",
        "los simuladores de demostración", max_lineas=140, min_lineas=100)

    doc = reemplaza_region(doc, "    AUTOEVALUACIONES['demo'] = [", "\n    ];\n",
                           QUIZ_JS, "AUTOEVALUACIONES", max_lineas=90)

    # El cableado del capítulo, enganchado al ciclo de carga de módulo,
    # justo donde el banco de pruebas engancha el suyo.
    doc = sustituye(doc, "        iniciarGeomapas();\n",
                    "        iniciarGeomapas();\n        cablearCap3();\n",
                    "la llamada a cablearCap3()")

    DESTINO.parent.mkdir(parents=True, exist_ok=True)
    # El orden de las opciones se decide en `baraja_opciones.py`, y es la
    # corrección del 2026-09-02: escritas de una en una, las 51 preguntas de
    # los cinco capítulos tenían la correcta la PRIMERA, y el motor no baraja.
    doc = baraja_documento(doc, "cap3")

    DESTINO.write_text(doc, encoding="utf-8")

    # --- El recuento, contado y no recordado --------------------------
    marcado = doc[:doc.rindex("\n  <script>")]
    mods = doc.count('<template id="module-')
    sims = marcado.count('data-simulador="')
    mapas = marcado.count('data-geomapa="cap3-')
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
          f"{ejercicios} ejercicios guiados · {quices} autoevaluación")

    problemas = []
    if mods != 12:
        problemas.append(f"módulos: {mods} (se esperan 12)")
    if ejercicios != 4:
        problemas.append(f"ejercicios: {ejercicios} (el molde son 4)")
    if quices != 1:
        problemas.append(f"autoevaluaciones: {quices} (se espera 1)")
    if bl_r != bl_py:
        problemas.append(f"R y Python descuadrados: {bl_r} y {bl_py}")
    if lienzos != con_alt:
        problemas.append(f"lienzos sin aria-label: {lienzos - con_alt}")
    if problemas:
        print("\n  PROBLEMAS:")
        for p in problemas:
            print(f"   - {p}")
        return 1
    print("\n  Capítulo 3 ensamblado.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
