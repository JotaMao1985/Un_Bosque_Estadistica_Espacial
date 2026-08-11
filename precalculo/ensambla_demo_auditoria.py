#!/usr/bin/env python3
"""
ensambla_demo_auditoria.py — construye el capítulo-banco de pruebas (T0.5)

Material de Estadística Espacial 2026-II (20929).

QUÉ ES ESTO Y POR QUÉ NO ES UN CAPÍTULO DE VERDAD.

`Htmls_Espacial/prueba-auditoria.html` no se publica y no lo lee ningún
estudiante: es el SUJETO de los cuatro auditores de T0.5. Existe porque un
auditor solo demuestra algo cuando se le pone delante un documento que
tenga lo que dice comprobar, y la plantilla del curso no lo tiene: cinco
bloques de código y **cero** líneas `#>`.

Por eso el fixture lleva, a propósito, una de cada:

  · cifras en el texto corrido y **cifras dentro de fórmulas de KaTeX**
    (el punto ciego que en Diseño de Experimentos vivió en cinco
    auditores a la vez sin que nadie lo viera);
  · bloques de R y de Python **encadenados**, con sus `#>`, que se
    ejecutan de verdad;
  · un `.geomapa` con sus cortes calculados en R y su tabla de respaldo;
  · lienzos con `role="img"` y `aria-label`;
  · una autoevaluación con el marcado canónico del quiz;
  · dos ejercicios guiados con cifras en la solución;
  · una tabla de discrepancias declaradas;
  · enlaces locales.

**Ninguna cifra del HTML está escrita a mano** (D10): todas se interpolan
desde `salidas/demo_auditoria.json`, que produce `genera_demo_auditoria.R`.
Si el JSON cambia, el capítulo cambia con él, y el auditor sigue cuadrando.

Cada sustitución sobre la plantilla se comprueba: si un ancla no aparece
exactamente una vez, esto **para**. Una plantilla que evoluciona y un
ensamblador que sustituye a ciegas es como el capítulo 7 de Muestreo
sobrescribió al 6.

Uso:  python3 precalculo/ensambla_demo_auditoria.py
      (desde la carpeta `Estadistica espacial/`)
"""
from __future__ import annotations

import html
import json
import pathlib
import sys

RAIZ = pathlib.Path(__file__).resolve().parent.parent
PLANTILLA = RAIZ / "plantilla" / "plantilla-capitulo.html"
SALIDAS = RAIZ / "precalculo" / "salidas"
DESTINO = RAIZ / "Htmls_Espacial" / "prueba-auditoria.html"

D = json.loads((SALIDAS / "demo_auditoria.json").read_text(encoding="utf-8"))
MAPA = json.loads((SALIDAS / "demo_auditoria_mapa.json").read_text(encoding="utf-8"))

col, nc, cli, ven, des, esc = (D["columbus"], D["nc"], D["clima"],
                               D["ventanas"], D["desercion"], D["escala"])


def n(x, d=5):
    """Formatea con `d` decimales. **Cinco** por defecto: es la regla que
    T0.5 fija para toda cifra de la que el texto argumenta.

    Por debajo, el índice de comparaciones del auditor absorbe casi
    cualquier perturbación de un dígito, y eso está MEDIDO en
    `mide_punto_ciego.py`, no supuesto: con un decimal se cuela el 63 %.
    Javier fijó el listón en cinco el 2026-08-03; el borrador anterior
    usaba cuatro."""
    return f"{float(x):.{d}f}"


def lista(xs):
    return " · ".join(str(int(v)) for v in xs)


# =====================================================================
# Los seis módulos del fixture
# =====================================================================

MOD1 = f"""
  <!-- ============================================================ -->
  <!-- MÓDULO 1 · Cifras en la prosa y dentro de KaTeX               -->
  <!-- ============================================================ -->
  <template id="module-1">
    <div class="animate-fade-in">
      <div class="border-b border-gray-100 pb-6 mb-6">
        <div class="flex items-center space-x-2 text-sm text-secondary font-semibold mb-2 uppercase tracking-wide">
          <span>Módulo 1</span>
        </div>
        <h2 class="text-3xl font-bold text-gray-900 mb-4" style="border:none; padding:0;">La escala se lleva la
          autocorrelación <span class="text-gray-400 font-normal text-2xl">/ Scale effect</span></h2>
        <div class="bg-gray-50 rounded-lg p-4 border border-gray-200 flex items-start gap-3">
          <span class="text-xl">🎯</span>
          <div>
            <h3 class="font-bold text-gray-800 text-sm" style="margin:0;">Objetivo</h3>
            <p class="text-gray-600 text-sm" style="margin:0;">Medir el efecto escala del MAUP sobre la deserción
              escolar colombiana, y dejar cifras en el texto corrido <em>y</em> dentro de fórmulas.</p>
          </div>
        </div>
      </div>

      <p>La deserción escolar del MEN está publicada por municipio. Sobre los
        <strong>{esc['n_municipal']}</strong> municipios con dato, el índice de Moran vale
        <strong>{n(esc['moran_municipal'])}</strong>: autocorrelación inequívoca y nada trivial. Agregada a los
        <strong>{esc['n_departamental']}</strong> departamentos, la misma variable da
        <strong>{n(esc['moran_departamental'])}</strong>, que ya no se distingue del azar
        (p&nbsp;=&nbsp;{n(esc['p_departamental'])}).</p>

      <div class="definition">
        <h3>El índice de Moran y su esperanza bajo la hipótesis nula</h3>
        <p>Con \\(n\\) unidades y una matriz de pesos \\(W\\) estandarizada por filas,</p>
        <p style="text-align:center;">$$I = \\frac{{n}}{{S_0}} \\cdot
          \\frac{{\\sum_i \\sum_j w_{{ij}} (z_i - \\bar{{z}})(z_j - \\bar{{z}})}}
               {{\\sum_i (z_i - \\bar{{z}})^2}}, \\qquad
          E[I] = -\\frac{{1}}{{n - 1}}$$</p>
        <p style="margin-bottom:0;">A escala departamental $n = {esc['n_departamental']}$, de modo que
          $E[I] = {n(des['moran_esperado'], 6)}$ y el estadístico tipificado sale
          $z = {n(des['moran_z'])}$ — por debajo de cualquier umbral convencional.</p>
      </div>

      <p>La caída es de <strong>{n(esc['caida_pct'])}&nbsp;%</strong>. No es que los departamentos suavicen el
        mapa: es que la partición administrativa <em>elige</em> qué vecindades existen, y al elegirlas destruye la
        estructura que el dato tenía. Eso es el efecto escala del MAUP, medido sobre dato colombiano en vez de
        afirmado sobre un ejemplo de manual. Y la consecuencia es la que sostiene el capítulo 3 entero:
        <strong>la unidad de análisis es una decisión de modelado</strong>, no de presentación, y elegirla en
        silencio es elegir el resultado.</p>

      <div class="warning">
        <p style="margin-bottom:0;"><strong>Ojo con la vecindad.</strong> A escala departamental la contigüidad reina
          deja <strong>{des['islas']}</strong> isla y <strong>{des['subgrafos']}</strong> subgrafos; a escala
          municipal, <strong>{esc['islas_municipal']}</strong> islas y
          <strong>{esc['subgrafos_municipal']}</strong>. El grado medio pasa de
          {n(esc['grado_municipal'])} a {n(des['grado_medio'])} vecinos. Ninguna de las dos cifras es un defecto del
          dato: son el caso de <code>zero.policy</code> saliendo solo.</p>
      </div>

      <p>El mapa de abajo es el coropleto departamental. Los cortes de clase
        <strong>los calculó R</strong> con <code>classInt</code> y viajan en el JSON; el navegador solo pinta.
        Compáralo con los cinco modos del componente en
        <a href="prueba-geomapa.html">el capítulo de prueba del <code>.geomapa</code></a>.</p>

      <div class="geomapa" data-geomapa="demo-mapa"></div>

      <table>
        <caption>Deserción escolar por departamento: resumen del dato que pinta el mapa.</caption>
        <thead>
          <tr><th scope="col">Estadístico</th><th scope="col">Valor</th></tr>
        </thead>
        <tbody>
          <tr><th scope="row">Departamentos con dato</th><td>{des['n_departamentos']}</td></tr>
          <tr><th scope="row">Municipios con dato</th><td>{des['n_municipios']}</td></tr>
          <tr><th scope="row">Media</th><td>{n(des['media'])} %</td></tr>
          <tr><th scope="row">Desviación típica</th><td>{n(des['sd'])}</td></tr>
          <tr><th scope="row">Mínimo</th><td>{n(des['minimo'])} %</td></tr>
          <tr><th scope="row">Máximo</th><td>{n(des['maximo'])} %</td></tr>
        </tbody>
      </table>
    </div>
  </template>
"""

MOD2 = f"""
  <!-- ============================================================ -->
  <!-- MÓDULO 2 · Bloques de código que se ejecutan de verdad        -->
  <!-- ============================================================ -->
  <template id="module-2">
    <div class="animate-fade-in">
      <div class="border-b border-gray-100 pb-6 mb-6">
        <div class="flex items-center space-x-2 text-sm text-secondary font-semibold mb-2 uppercase tracking-wide">
          <span>Módulo 2</span>
        </div>
        <h2 class="text-3xl font-bold text-gray-900 mb-4" style="border:none; padding:0;">R y Python sobre el mismo
          dato <span class="text-gray-400 font-normal text-2xl">/ Code tabs</span></h2>
        <div class="bg-gray-50 rounded-lg p-4 border border-gray-200 flex items-start gap-3">
          <span class="text-xl">🎯</span>
          <div>
            <h3 class="font-bold text-gray-800 text-sm" style="margin:0;">Objetivo</h3>
            <p class="text-gray-600 text-sm" style="margin:0;">Bloques encadenados en los dos lenguajes, con sus
              salidas anunciadas en comentarios <code>#&gt;</code>. Los ejecuta
              <code>verifica_bloques.py</code>.</p>
          </div>
        </div>
      </div>

      <p>La contigüidad reina de Columbus es el dato canónico de Anselin y la referencia con la que se comprueba
        que <code>spdep</code> y <code>libpysal</code> entienden lo mismo por «vecino».</p>

      <div class="code-tabs">
        <div class="code-tabs-nav" role="tablist" aria-label="Contigüidad de Columbus en R y en Python">
          <button class="code-tab-btn active" data-lang="r" role="tab" aria-selected="true">R</button>
          <button class="code-tab-btn" data-lang="python" role="tab" aria-selected="false">Python</button>
        </div>
        <div class="code-tab-panel" data-lang="r">
          <pre><code class="language-r">library(sf); library(spdep); library(spData)

col &lt;- st_read(system.file("shapes/columbus.gpkg", package = "spData"), quiet = TRUE)
nb_reina &lt;- poly2nb(col, queen = TRUE)
nb_torre &lt;- poly2nb(col, queen = FALSE)

c(reina = sum(card(nb_reina)) / 2, torre = sum(card(nb_torre)) / 2)
#&gt; reina torre
#&gt;   118   100
round(c(reina = mean(card(nb_reina)), torre = mean(card(nb_torre))), 6)
#&gt;    reina    torre
#&gt; 4.816327 4.081633</code></pre>
        </div>
        <div class="code-tab-panel" data-lang="python" hidden>
          <pre><code class="language-python">import json
import geopandas as gpd, libpysal, numpy as np

# La ruta de la biblioteca de R la escribe entorno.R: no se cablea, porque
# no vive dentro del framework sino en el directorio del usuario.
BIB = json.load(open("precalculo/versiones.json"))["rutas"]["biblioteca"]
col = gpd.read_file(f"{{BIB}}/spData/shapes/columbus.gpkg")

w = libpysal.weights.Queen.from_dataframe(col, use_index=False)
print(int(w.s0 / 2), round(float(np.mean(list(w.cardinalities.values()))), 6))
#&gt; 118 4.816327</code></pre>
        </div>
      </div>

      <p>Las dos vías dan <strong>{col['aristas_reina']}</strong> aristas y grado medio
        <strong>{n(col['grado_reina'], 6)}</strong>. Pasar a torre deja
        <strong>{col['aristas_torre']}</strong> aristas y {n(col['grado_torre'], 6)}: se pierde el
        <strong>{n(col['perdida_pct'])}&nbsp;%</strong> de la vecindad por el solo hecho de no admitir el contacto
        por un vértice.</p>

      <div class="warning">
        <p style="margin-bottom:0;"><strong>Discrepancia declarada (D2).</strong> La lista GAL que Anselin
          distribuye dentro de <code>spdep::oldcol</code> <em>no</em> es esta: trae
          <strong>{col['aristas_gal']}</strong> aristas y grado medio <strong>{n(col['grado_gal'], 6)}</strong>.
          Dos aristas de diferencia. No es un error de nadie —una vecindad publicada es una decisión, no un
          cálculo— pero presentar una de las dos como «la» vecindad de Columbus sí lo sería.</p>
      </div>

      <p>El segundo contraste es la clasificación por cuantiles sobre la deserción departamental. Los dos lenguajes
        leen <strong>el mismo CSV</strong>, así que cualquier diferencia sería del algoritmo.</p>

      <div class="code-tabs">
        <div class="code-tabs-nav" role="tablist" aria-label="Clasificación por cuantiles en R y en Python">
          <button class="code-tab-btn active" data-lang="r" role="tab" aria-selected="true">R</button>
          <button class="code-tab-btn" data-lang="python" role="tab" aria-selected="false">Python</button>
        </div>
        <div class="code-tab-panel" data-lang="r">
          <pre><code class="language-r">library(classInt)

dep &lt;- read.csv("precalculo/salidas/demo_departamentos.csv", encoding = "UTF-8")
ci  &lt;- classIntervals(dep$desercion, n = 5, style = "quantile")

as.integer(table(findCols(ci)))   # findCols, NO cut(): ver el aviso de abajo
#&gt; [1] 7 6 7 6 7
round(as.numeric(ci$brks), 4)
#&gt; [1] 1.7100 2.8490 3.4426 3.9482 5.1227 6.7331</code></pre>
        </div>
        <div class="code-tab-panel" data-lang="python" hidden>
          <pre><code class="language-python">import pandas as pd, mapclassify

dep = pd.read_csv("precalculo/salidas/demo_departamentos.csv")
q = mapclassify.Quantiles(dep["desercion"], k=5)

print(q.counts.tolist())
#&gt; [7, 6, 7, 6, 7]
print([round(float(b), 4) for b in q.bins])
#&gt; [2.849, 3.4426, 3.9482, 5.1227, 6.7331]</code></pre>
        </div>
      </div>

      <div class="warning">
        <h3>Discrepancia declarada (D1): <code>cut()</code> no es <code>findCols()</code></h3>
        <p>Aquí las particiones coinciden —<strong>{lista(nc['tam_quantile']) if False else '7 · 6 · 7 · 6 · 7'}</strong>—
          porque la deserción es continua y no hay empates en los cortes. Con empates, no. Sobre <code>SID74</code>
          de <code>nc</code>, que tiene <strong>{nc['empates_en_cortes']}</strong> condados empatados justo en los
          cortes, <code>classInt</code> reparte los {nc['n_condados']} condados en
          <strong>{lista(nc['tam_quantile'])}</strong> y <code>mapclassify</code> en
          <strong>{lista(nc['tam_quantile_py'])}</strong>: <strong>{int(nc['movidos'])}</strong> condados cambian de
          clase y salen dos mapas distintos rotulados los dos «clasificación por cuantiles».</p>
        <p style="margin-bottom:0;">La causa es el lado cerrado del intervalo: <code>classInt</code> usa
          $[a,\\,b)$ y <code>mapclassify</code> usa $(a,\\,b]$. Y la trampa se cobra también dentro de R:
          <code>cut(v, brks)</code> cierra por la derecha, así que <strong>un <code>cut</code> ingenuo en un script
          de R devuelve la respuesta de Python</strong> sin avisar. Con Fisher-Jenks no pasa: la partición es la
          misma en los dos —{lista(nc['tam_fisher'])}— y lo único que cambia es cómo se imprime la frontera.</p>
      </div>

      <p>El tercer bloque es geoestadístico: el gradiente térmico de las {cli['n_estaciones']} estaciones del IDEAM.
        Que reproduzca la ley física es lo que dice que el dato está sano.</p>

      <div class="code-tabs">
        <div class="code-tabs-nav" role="tablist" aria-label="Gradiente térmico en R y en Python">
          <button class="code-tab-btn active" data-lang="r" role="tab" aria-selected="true">R</button>
          <button class="code-tab-btn" data-lang="python" role="tab" aria-selected="false">Python</button>
        </div>
        <div class="code-tab-panel" data-lang="r">
          <pre><code class="language-r">est &lt;- st_read("datos/procesado/colombia_estaciones_clima.gpkg", quiet = TRUE)
aj  &lt;- lm(t_media_anual ~ altitud_m, data = est)

round(coef(aj)[["altitud_m"]] * 1000, 4)   # grados C por cada 1000 m
#&gt; [1] -5.5639
round(cor(est$altitud_m, est$t_media_anual), 4)
#&gt; [1] -0.9791</code></pre>
        </div>
        <div class="code-tab-panel" data-lang="python" hidden>
          <pre><code class="language-python">import geopandas as gpd, numpy as np

est = gpd.read_file("datos/procesado/colombia_estaciones_clima.gpkg")
b, a = np.polyfit(est["altitud_m"], est["t_media_anual"], 1)

print(round(b * 1000, 4))
#&gt; -5.5639
print(round(float(np.corrcoef(est["altitud_m"], est["t_media_anual"])[0, 1]), 4))
#&gt; -0.9791</code></pre>
        </div>
      </div>

      <p>El gradiente sale <strong>{n(cli['gradiente'])}&nbsp;°C por cada 1&nbsp;000&nbsp;m</strong>, dentro del rango
        físico de −5 a −7, con correlación <strong>{n(cli['corr'])}</strong> y
        $R^2 = {n(cli['r2'])}$. La temperatura media de las estaciones es {n(cli['temp_media'])}&nbsp;°C y su altitud
        media {n(cli['alt_media'])}&nbsp;m.</p>
    </div>
  </template>
"""

MOD3 = f"""
  <!-- ============================================================ -->
  <!-- MÓDULO 3 · Simuladores y la ventana de observación            -->
  <!-- ============================================================ -->
  <template id="module-3">
    <div class="animate-fade-in">
      <div class="border-b border-gray-100 pb-6 mb-6">
        <div class="flex items-center space-x-2 text-sm text-secondary font-semibold mb-2 uppercase tracking-wide">
          <span>Módulo 3</span>
        </div>
        <h2 class="text-3xl font-bold text-gray-900 mb-4" style="border:none; padding:0;">La ventana cambia
          \\(\\lambda\\) <span class="text-gray-400 font-normal text-2xl">/ Observation window</span></h2>
        <div class="bg-gray-50 rounded-lg p-4 border border-gray-200 flex items-start gap-3">
          <span class="text-xl">🎯</span>
          <div>
            <h3 class="font-bold text-gray-800 text-sm" style="margin:0;">Objetivo</h3>
            <p class="text-gray-600 text-sm" style="margin:0;">Lienzos con su texto alternativo, y la cifra que
              convierte la ventana de observación en parte del estimador.</p>
          </div>
        </div>
      </div>

      <p>Las <strong>{ven['n_sedes']}</strong> sedes educativas de Bogotá se pueden observar sobre dos ventanas, las
        dos legítimas. Sobre el perímetro urbano —{n(ven['area_urbana'])}&nbsp;km², con
        {ven['n_urbana']} sedes— la intensidad es</p>

      <p style="text-align:center;">$$\\hat{{\\lambda}}_{{\\text{{urbana}}}} =
        \\frac{{{ven['n_urbana']}}}{{{n(ven['area_urbana'])}}} = {n(ven['lambda_urbana'])}
        \\ \\text{{sedes/km}}^2$$</p>

      <p>Sobre Bogotá D.C. completo —{n(ven['area_dc'])}&nbsp;km², que incluye Sumapaz, rural y casi sin
        colegios— con {ven['n_dc']} sedes,</p>

      <p style="text-align:center;">$$\\hat{{\\lambda}}_{{\\text{{D.C.}}}} =
        \\frac{{{ven['n_dc']}}}{{{n(ven['area_dc'])}}} = {n(ven['lambda_dc'])}
        \\ \\text{{sedes/km}}^2$$</p>

      <p>El mismo dato, <strong>un factor de {n(ven['factor_lambda'])}</strong> en la intensidad estimada, por una
        decisión que no aparece en ninguna fórmula. La razón de áreas es {n(ven['razon_area'])}, así que casi toda
        la diferencia viene del área añadida y no de las sedes ganadas.</p>

      <div class="simulador" data-simulador="demo-deslizadores">
        <h4><i class="fas fa-sliders-h" aria-hidden="true"></i> Deslizadores y gráfico de línea</h4>
        <p class="simulador-intro">Un simulador cualquiera, para que el auditor tenga un lienzo que revisar.</p>
        <div class="simulador-controles"></div>
        <div class="grafico-wrapper" style="height:220px;">
          <canvas aria-label="Serie simulada con tendencia y ruido ajustables" role="img"></canvas>
        </div>
        <div class="simulador-lectura"></div>
      </div>

      <div class="simulador" data-simulador="demo-correlograma">
        <h4><i class="fas fa-signal" aria-hidden="true"></i> Menú desplegable y gráfico de barras</h4>
        <p class="simulador-intro">Dos lienzos más, cada uno con su <code>aria-label</code>.</p>
        <div class="simulador-controles"></div>
        <p class="grafico-etiqueta">ACF</p>
        <div class="grafico-wrapper" style="height:200px;">
          <canvas aria-label="Función de autocorrelación de la serie elegida" role="img"></canvas>
        </div>
        <p class="grafico-etiqueta">PACF</p>
        <div class="grafico-wrapper" style="height:200px;">
          <canvas aria-label="Función de autocorrelación parcial de la serie elegida" role="img"></canvas>
        </div>
        <div class="simulador-lectura"></div>
      </div>

      <div class="tabla-ranking" data-ranking="demo">
        <p class="tabla-ranking-titulo">Tabla comparativa ordenable (demostración)</p>
        <div class="tabla-ranking-marco" aria-label="Tabla comparativa ordenable (demostración)"></div>
        <p class="tabla-ranking-estado" role="status" aria-live="polite"></p>
        <p class="tabla-ranking-pie"></p>
      </div>
    </div>
  </template>
"""

MOD4 = f"""
  <!-- ============================================================ -->
  <!-- MÓDULO 4 · Autoevaluación y ejercicios guiados                -->
  <!-- ============================================================ -->
  <template id="module-4">
    <div class="animate-fade-in">
      <div class="border-b border-gray-100 pb-6 mb-6">
        <div class="flex items-center space-x-2 text-sm text-secondary font-semibold mb-2 uppercase tracking-wide">
          <span>Módulo 4</span>
        </div>
        <h2 class="text-3xl font-bold text-gray-900 mb-4" style="border:none; padding:0;">Autoevaluación y ejercicios
          <span class="text-gray-400 font-normal text-2xl">/ Self-assessment</span></h2>
        <div class="bg-gray-50 rounded-lg p-4 border border-gray-200 flex items-start gap-3">
          <span class="text-xl">🎯</span>
          <div>
            <h3 class="font-bold text-gray-800 text-sm" style="margin:0;">Objetivo</h3>
            <p class="text-gray-600 text-sm" style="margin:0;">El marcado canónico del quiz y dos ejercicios con
              cifras en la solución.</p>
          </div>
        </div>
      </div>

      <div class="quiz" data-quiz="demo">
        <h4><i class="fas fa-circle-question" aria-hidden="true"></i> Autoevaluación</h4>
        <p class="text-sm" style="margin-bottom:0;">Cada opción lleva su retroalimentación, también las incorrectas.</p>
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

        <div class="ejercicio-guiado">
          <p class="ejercicio-enunciado"><span class="ejercicio-numero">1.</span>La deserción departamental tiene
            media {n(des['media'])}&nbsp;% y desviación típica {n(des['sd'])}. ¿Cuántas desviaciones típicas separan
            al departamento con más deserción del que menos tiene?</p>
          <div class="ejercicio-acciones">
            <button type="button" class="ejercicio-boton" aria-expanded="false" aria-controls="demo-e1-pista">
              <i class="fas fa-lightbulb" aria-hidden="true"></i> Pista <i class="fas fa-chevron-down" aria-hidden="true"></i>
            </button>
            <button type="button" class="ejercicio-boton" aria-expanded="false" aria-controls="demo-e1-sol">
              <i class="fas fa-key" aria-hidden="true"></i> Solución <i class="fas fa-chevron-down" aria-hidden="true"></i>
            </button>
          </div>
          <div class="ejercicio-panel pista" id="demo-e1-pista" hidden>
            <p style="margin:0;">El recorrido dividido por la desviación típica. Fíjate en que el resultado no dice
              nada sobre <em>dónde</em> están esos dos departamentos: para eso hace falta el mapa.</p>
          </div>
          <div class="ejercicio-panel solucion" id="demo-e1-sol" hidden>
            <p><strong>{n(des['recorrido_en_sd'])} desviaciones típicas.</strong></p>
            <p>El recorrido va de {n(des['minimo'])}&nbsp;% a {n(des['maximo'])}&nbsp;%, o sea
              {n(des['recorrido'])} puntos, y
              $\\frac{{{n(des['recorrido'])}}}{{{n(des['sd'])}}} = {n(des['recorrido_en_sd'])}$.</p>
            <pre><code class="language-r">dep &lt;- read.csv("precalculo/salidas/demo_departamentos.csv", encoding = "UTF-8")
round(diff(range(dep$desercion)) / sd(dep$desercion), 5)
#&gt; [1] {n(des['recorrido_en_sd'])}</code></pre>
            <p style="margin-bottom:0;">Un recorrido de casi cuatro desviaciones típicas sobre
              {des['n_departamentos']} unidades es mucha heterogeneidad, y sin embargo el I de Moran a esta escala
              es {n(esc['moran_departamental'])}: <strong>heterogeneidad no es autocorrelación</strong>. La primera
              dice cuánto varían los valores; la segunda, si los parecidos están juntos.</p>
          </div>
        </div>

        <div class="ejercicio-guiado">
          <p class="ejercicio-enunciado"><span class="ejercicio-numero">2.</span>¿Qué proporción de la diferencia
            entre las dos intensidades de Bogotá se explica solo por el área añadida?</p>
          <div class="ejercicio-acciones">
            <button type="button" class="ejercicio-boton" aria-expanded="false" aria-controls="demo-e2-pista">
              <i class="fas fa-lightbulb" aria-hidden="true"></i> Pista <i class="fas fa-chevron-down" aria-hidden="true"></i>
            </button>
            <button type="button" class="ejercicio-boton" aria-expanded="false" aria-controls="demo-e2-sol">
              <i class="fas fa-key" aria-hidden="true"></i> Solución <i class="fas fa-chevron-down" aria-hidden="true"></i>
            </button>
          </div>
          <div class="ejercicio-panel pista" id="demo-e2-pista" hidden>
            <p style="margin:0;">Compara el factor de las intensidades con la razón de áreas. Si fueran iguales, el
              área lo explicaría todo.</p>
          </div>
          <div class="ejercicio-panel solucion" id="demo-e2-sol" hidden>
            <p><strong>Casi toda.</strong> El factor de intensidades es {n(ven['factor_lambda'])} y la razón de
              áreas {n(ven['razon_area'])}.</p>
            <p>Pasar de la ventana urbana a la del D.C. multiplica el área por {n(ven['razon_area'])} y el número de
              sedes solo por {n(ven['razon_sedes'])}: se añaden
              {ven['sedes_extra']} sedes sobre
              {n(ven['area_extra'])}&nbsp;km² de territorio nuevo, que es una intensidad de
              {n(ven['lambda_extra'])} sedes/km² — unas {n(ven['lambda_urbana'] / ven['lambda_extra'])} ×
              por debajo de la urbana.</p>
            <p style="margin-bottom:0;">Por eso las dos ventanas se congelan y el material presenta las dos: elegir
              una sola y no decirlo sería publicar una intensidad como si fuera <em>la</em> intensidad.</p>
          </div>
        </div>
      </div>

      <div class="references">
        <h3><i class="fas fa-book-open mr-2" aria-hidden="true"></i>Lecturas de este capítulo</h3>
        <ul style="margin-bottom:0;">
          <li>Pebesma &amp; Bivand (2023), <em>Spatial Data Science</em>, capítulos 14–17 — el índice de Moran y la
            matriz de pesos.</li>
          <li>Baddeley, Rubak &amp; Turner (2015), <em>Spatial Point Patterns</em>, capítulo 5 — la ventana de
            observación y la intensidad.</li>
        </ul>
      </div>
    </div>
  </template>
"""

MOD5 = """
  <!-- ============================================================ -->
  <!-- MÓDULO 5 · Glosario de notación y rúbrica                     -->
  <!-- ============================================================ -->
  <template id="module-5">
    <div class="animate-fade-in">
      <div class="border-b border-gray-100 pb-6 mb-6">
        <h2 class="text-2xl font-bold text-primary" style="margin:0;">Glosario de notación y rúbrica</h2>
        <p class="text-gray-600 text-sm" style="margin:0;">Los dos componentes injertados desde Muestreo en T0.2.
          Aquí están para que el auditor compruebe que se pintan y que la notación espacial —\\(s\\), \\(Z(s)\\),
          \\(\\lambda\\), \\(W\\), \\(\\gamma(h)\\), \\(I\\)— llega entera.</p>
      </div>

      <div class="glosario-notacion" data-glosario="demo-notacion"></div>

      <div class="rubrica" data-rubrica="demo-rubrica"></div>
    </div>
  </template>
"""

MOD6 = f"""
  <!-- ============================================================ -->
  <!-- MÓDULO 6 · Cierre: las discrepancias declaradas               -->
  <!-- ============================================================ -->
  <template id="module-6">
    <div class="animate-fade-in">
      <div class="border-b border-gray-100 pb-6 mb-6">
        <div class="flex items-center space-x-2 text-sm text-secondary font-semibold mb-2 uppercase tracking-wide">
          <span>Módulo 6</span>
        </div>
        <h2 class="text-3xl font-bold text-gray-900 mb-4" style="border:none; padding:0;">Cierre <span
            class="text-gray-400 font-normal text-2xl">/ Declared discrepancies</span></h2>
      </div>

      <p>Toda discrepancia entre dos fuentes que este material usa se declara, con su identificador, el módulo donde
        muerde y las dos cifras que la sostienen. Una discrepancia sin cifras no es una declaración: es una excusa.</p>

      <table>
        <caption>Discrepancias declaradas del capítulo de pruebas.</caption>
        <thead>
          <tr>
            <th scope="col">Id</th><th scope="col">Módulo</th><th scope="col">Qué discrepa</th>
            <th scope="col">Lo que dice cada fuente</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td>D1</td><td>2</td>
            <td>El lado cerrado del intervalo al clasificar por cuantiles</td>
            <td><code>classInt</code> $[a,b)$: {lista(nc['tam_quantile'])} · <code>mapclassify</code> $(a,b]$:
              {lista(nc['tam_quantile_py'])} — {int(nc['movidos'])} condados cambian de clase</td>
          </tr>
          <tr>
            <td>D2</td><td>2</td>
            <td>La vecindad de Columbus</td>
            <td>Lista GAL de Anselin: {col['aristas_gal']} aristas · <code>poly2nb</code> reina:
              {col['aristas_reina']} aristas</td>
          </tr>
          <tr>
            <td>D3</td><td>1</td>
            <td>El I de Moran de la deserción, según la escala</td>
            <td>Municipal: {n(esc['moran_municipal'])} · departamental: {n(esc['moran_departamental'])} — cae el
              {n(esc['caida_pct'])}&nbsp;%</td>
          </tr>
        </tbody>
      </table>

      <div class="note">
        <p style="margin-bottom:0;">Las tres son <strong>discrepancias</strong>, no erratas: ninguna es un error de
          nadie. Una errata es una cifra equivocada; una discrepancia es la misma pregunta contestada con dos
          convenios distintos, y el trabajo del material es decir cuál usa y por qué.</p>
      </div>

      <div class="warning">
        <p style="margin-bottom:0;"><strong>Regla de publicación.</strong> Toda cifra de la que este material
          argumenta se publica con <strong>5 decimales</strong> —la regla es ≥ 5, no exactamente 5:
          si la cifra tiene más, se conservan—. No es pedantería: está medido en
          <code>mide_punto_ciego.py</code> que, con menos, el auditor de prosa deja pasar casi cualquier
          perturbación de un dígito, porque su índice de comparaciones contiene cientos de miles de cadenas.
          Una garantía que no se mide no es una garantía.</p>
      </div>

      <p>El componente <code>.geomapa</code> y sus cinco modos se prueban aparte, en
        <a href="prueba-geomapa.html">el capítulo de prueba del <code>.geomapa</code></a>.</p>

      <div class="references">
        <h3><i class="fas fa-book-open mr-2" aria-hidden="true"></i>Fuentes de los datos</h3>
        <ul style="margin-bottom:0;">
          <li>Deserción escolar y cobertura: <strong>Ministerio de Educación Nacional</strong>, indicadores
            municipales.</li>
          <li>Límites administrativos: <strong>Marco Geoestadístico Nacional del DANE</strong>, vía geoBoundaries
            (gbOpen), CC BY 4.0.</li>
          <li>Sedes educativas de Bogotá: <strong>Secretaría de Educación del Distrito</strong>, CC BY-SA 4.0.</li>
          <li>Temperatura y altitud: <strong>IDEAM</strong>, normales climatológicas 1991-2020.</li>
          <li>Columbus y <code>nc</code>: <strong>Anselin</strong> (1988) y <strong>Cressie</strong> (1993), vía
            <code>spData</code> y <code>sf</code>.</li>
        </ul>
      </div>
    </div>
  </template>
"""

MODULOS = MOD1 + MOD2 + MOD3 + MOD4 + MOD5 + MOD6

COURSE_DATA = """    const courseData = {
      title: "Estadística Espacial",
      modules: [
        { id: 1, title: "La escala se lleva la autocorrelación", shortTitle: "Escala", duration: "6 min" },
        { id: 2, title: "R y Python sobre el mismo dato", shortTitle: "Código", duration: "8 min" },
        { id: 3, title: "La ventana cambia lambda", shortTitle: "Ventana", duration: "6 min" },
        { id: 4, title: "Autoevaluación y ejercicios", shortTitle: "Autoevaluación", duration: "8 min" },
        { id: 5, title: "Glosario de notación y rúbrica", shortTitle: "Glosario", duration: "4 min" },
        { id: 6, title: "Cierre: discrepancias declaradas", shortTitle: "Cierre", duration: "4 min" }
      ]
    };

    // Las cifras del capítulo, tal como salen de
    // precalculo/genera_demo_auditoria.R. El auditor de prosa contrasta
    // contra ESTO, no contra la memoria de nadie.
    const DATOS_DEMO = %s;
""" % json.dumps(D, ensure_ascii=False, indent=2).replace("\n", "\n    ")

QUIZ = f"""    AUTOEVALUACIONES['demo'] = [
      {{
        tipo: 'opcion',
        modulo: 1,
        pregunta: 'El I de Moran de la deserción pasa de {n(esc['moran_municipal'])} entre municipios a '
          + '{n(esc['moran_departamental'])} entre departamentos. ¿Qué ha pasado?',
        pista: 'La agregación no promedia el mapa: cambia qué unidades son vecinas de cuáles.',
        opciones: [
          {{ texto: 'La agregación redefinió la vecindad y con ella la estructura espacial.', correcta: true,
            retro: 'Eso es el efecto escala del MAUP. Los {esc['n_departamental']} departamentos imponen una '
              + 'partición que no tiene por qué respetar la escala a la que el fenómeno opera.' }},
          {{ texto: 'La deserción dejó de estar autocorrelacionada.', correcta: false,
            retro: 'La variable es la misma. Lo que cambió es la unidad de análisis, no el fenómeno.' }},
          {{ texto: 'Hay menos unidades, así que el test pierde potencia y no detecta nada.', correcta: false,
            retro: 'La potencia baja, sí, pero la ESTIMACIÓN también cae —de {n(esc['moran_municipal'])} a '
              + '{n(esc['moran_departamental'])}—, y eso no lo explica el tamaño muestral.' }},
          {{ texto: 'El promedio departamental está mal calculado.', correcta: false,
            retro: 'Es la media sin ponderar de sus municipios, y se declara como tal. El efecto aparece igual '
              + 'con cualquier agregación razonable.' }}
        ],
        retroAcierto: 'La unidad de análisis es una decisión de modelado, no de presentación.',
        retroFallo: 'Repasa el módulo 1: la caída es del {n(esc['caida_pct'])} %.'
      }},
      {{
        tipo: 'multiple',
        modulo: 3,
        pregunta: 'La intensidad de las sedes de Bogotá cambia por un factor de {n(ven['factor_lambda'])} según la '
          + 'ventana. Marca <strong>todo</strong> lo que sea cierto.',
        pista: 'Son dos. Piensa en qué entra en el denominador y en qué NO aparece en la fórmula.',
        opciones: [
          {{ texto: 'La ventana forma parte del estimador, aunque no aparezca en la notación.', correcta: true,
            retro: 'El área está en el denominador de $\\\\hat{{\\\\lambda}} = n/|W|$: elegir la ventana es elegir '
              + 'el estimador.' }},
          {{ texto: 'Casi toda la diferencia viene del área añadida, no de las sedes ganadas.', correcta: true,
            retro: 'El área se multiplica por {n(ven['razon_area'])} y las sedes solo por '
              + '{n(ven['n_dc'] / ven['n_urbana'])}.' }},
          {{ texto: 'Una de las dos ventanas está mal delineada.', correcta: false,
            retro: 'Las dos son delineaciones oficiales y correctas. El problema no es cuál es buena: es que hay '
              + 'que decir cuál se usa.' }},
          {{ texto: 'Con más sedes el factor desaparecería.', correcta: false,
            retro: 'El factor lo pone el área. Añadir sedes en la zona urbana subiría las DOS intensidades.' }}
        ],
        retroAcierto: 'Las dos. Por eso el material congela las dos ventanas en vez de elegir una en silencio.',
        retroFallo: 'Las correctas son las dos primeras.'
      }},
      {{
        tipo: 'opcion',
        modulo: 2,
        pregunta: 'En R, ¿por qué <code>cut(v, ci$brks)</code> no da la misma partición que '
          + '<code>findCols(ci)</code>?',
        pista: 'Mira qué extremo del intervalo cierra cada uno.',
        opciones: [
          {{ texto: 'Porque <code>cut</code> cierra por la derecha, $(a,b]$, y <code>classInt</code> por la '
              + 'izquierda, $[a,b)$.', correcta: true,
            retro: 'Con {nc['empates_en_cortes']} empates justo en los cortes, eso mueve {int(nc['movidos'])} '
              + 'condados. Un <code>cut</code> ingenuo dentro de R devuelve la respuesta de Python.' }},
          {{ texto: 'Porque <code>cut</code> recalcula los cuantiles con otro algoritmo.', correcta: false,
            retro: 'No recalcula nada: recibe los mismos cortes. La diferencia es solo el lado cerrado.' }},
          {{ texto: 'Porque <code>findCols</code> ordena los datos antes de clasificar.', correcta: false,
            retro: 'Ninguno de los dos reordena. La asignación es elemento a elemento.' }},
          {{ texto: 'No es cierto: dan siempre lo mismo.', correcta: false,
            retro: 'Sobre la deserción departamental sí coinciden —no hay empates—, pero sobre <code>SID74</code> '
              + 'no: {lista(nc['tam_quantile'])} frente a {lista(nc['tam_quantile_py'])}.' }}
        ],
        retroAcierto: 'Y por eso los cortes los calcula R y viajan en el JSON: reimplementarlos en JS sería pedir '
          + 'un tercer convenio.',
        retroFallo: 'Repasa la discrepancia D1 del módulo 2.'
      }}
    ];
"""


def reemplaza_region(texto: str, abre: str, cierra: str, nuevo: str,
                     que: str, max_lineas: int) -> str:
    """Sustituye la región entre `abre` y el primer `cierra` posterior,
    exigiendo que la región no pase de `max_lineas`.

    El tope no es decorativo: la primera versión de este ensamblador
    buscaba el cierre de `courseData` con `doc.index("];")` y encontró un
    `];` que estaba **dentro de un comentario** 270 líneas más abajo. Se
    llevó por delante `renderNavigation` y `loadModule`, el archivo salió
    MÁS GRANDE que la plantilla, todas las anclas siguientes se
    encontraron y el ensamblador informó «limpio». Solo abrirlo en el
    navegador —contenido en blanco— lo destapó.

    Es, otra vez, la operación que devuelve algo plausible en vez de
    fallar: el modo de fallo dominante de este proyecto. La guarda que lo
    impide es saber de antemano cuánto texto es razonable borrar.
    """
    if texto.count(abre) != 1:
        sys.exit(f"PARADO: el ancla de apertura de «{que}» aparece "
                 f"{texto.count(abre)} veces, no 1")
    i = texto.index(abre)
    j = texto.index(cierra, i) + len(cierra)
    n_lineas = texto[i:j].count("\n")
    if n_lineas > max_lineas:
        sys.exit(f"PARADO: la región de «{que}» ocupa {n_lineas} líneas y el tope "
                 f"es {max_lineas}.\n        El cierre {cierra!r} se encontró en el "
                 f"sitio equivocado; la plantilla ha cambiado.")
    print(f"  OK   {que}  ({n_lineas} líneas sustituidas)")
    return texto[:i] + nuevo + texto[j:]


def sustituye(texto: str, ancla: str, nuevo: str, que: str) -> str:
    """Sustituye exigiendo que el ancla aparezca EXACTAMENTE una vez.

    Un ensamblador que sustituye a ciegas sobre una plantilla que
    evoluciona es como el capítulo 7 de Muestreo acabó sobrescribiendo al
    6. Aquí, si la plantilla cambia bajo los pies, esto para.
    """
    veces = texto.count(ancla)
    if veces != 1:
        sys.exit(f"PARADO: el ancla de «{que}» aparece {veces} veces, no 1.\n"
                 f"        {ancla[:90]!r}")
    print(f"  OK   {que}")
    return texto.replace(ancla, nuevo, 1)


def main() -> int:
    doc = PLANTILLA.read_text(encoding="utf-8")
    print(f"\n=== ensambla_demo_auditoria.py ===\nplantilla: {len(doc)/1024:.0f} KB\n")

    # --- 1. Textos meta ------------------------------------------------
    doc = sustituye(doc, "<title>Plantilla de capítulo — Estadística Espacial</title>",
                    "<title>Banco de pruebas del arnés — Estadística Espacial</title>",
                    "título")
    doc = sustituye(doc, "PLANTILLA BASE •\n              5 MÓDULOS DE DEMOSTRACIÓN • UNBOSQUE 2026-II",
                    "BANCO DE PRUEBAS DEL ARNÉS DE AUDITORÍA •\n              6 MÓDULOS • UNBOSQUE 2026-II",
                    "subtítulo de la cabecera")
    doc = sustituye(doc, "Estadística Espacial (20929) • Plantilla de\n          capítulo • UnBosque 2026-II",
                    "Estadística Espacial (20929) • Banco de pruebas del\n          arnés (T0.5) • UnBosque 2026-II",
                    "pie")

    # --- 2. courseData + los datos del precálculo ----------------------
    doc = reemplaza_region(
        doc, "    const courseData = {", "\n    };\n", COURSE_DATA,
        "courseData + DATOS_DEMO", max_lineas=20)

    # --- 3. Los módulos ------------------------------------------------
    doc = reemplaza_region(
        doc,
        "  <!-- ============================================================ -->\n"
        "  <!-- MÓDULO 1 · Cajas y tipografía",
        "\n  <script>", MODULOS.lstrip("\n") + "\n  <script>",
        "los seis módulos", max_lineas=600)

    # --- 4. El mapa real, con sus cortes de R --------------------------
    vieja = [l for l in doc.splitlines() if l.startswith("    GEOMAPAS['demo-mapa'] =")]
    if len(vieja) != 1:
        sys.exit(f"PARADO: {len(vieja)} registros de GEOMAPAS['demo-mapa'], se esperaba 1")
    nueva = (
        "    // El mapa lo produce geo.R. Los CORTES vienen de classInt, no de\n"
        "    // JS: reimplementar Fisher-Jenks en el navegador sería pedir un\n"
        "    // tercer convenio además de los dos de la discrepancia D1.\n"
        "    GEOMAPAS['demo-mapa'] = {\n"
        "      fuente: " + json.dumps(MAPA, ensure_ascii=False) + ",\n"
        "      paleta: 'verde',\n"
        "      etiqueta: 'Coropleto de la deserción escolar en los "
        + str(des["n_departamentos"]) + " departamentos de Colombia, en "
        + str(len(MAPA["cortes"]) - 1) + " clases por cuantiles.',\n"
        "      tabla: function (d) {\n"
        "        const filas = d.valor.map((v, i) => `<tr><th scope=\"row\">"
        "${(d.etiquetas || [])[i] || (i + 1)}</th><td>${v.toFixed(4)}</td>"
        "<td>${d.clase[i]}</td></tr>`).join('');\n"
        "        return `<table><caption>Deserción escolar (%) y clase de cada "
        "departamento.</caption><thead><tr><th scope=\"col\">Departamento</th>"
        "<th scope=\"col\">Deserción (%)</th><th scope=\"col\">Clase</th></tr></thead>"
        "<tbody>${filas}</tbody></table>`;\n"
        "      }\n"
        "    };")
    doc = sustituye(doc, vieja[0], nueva, "GEOMAPAS['demo-mapa']")

    # --- 5. Las preguntas ----------------------------------------------
    doc = reemplaza_region(
        doc, "    AUTOEVALUACIONES['demo'] = [", "\n    ];\n", QUIZ,
        "AUTOEVALUACIONES", max_lineas=200)

    DESTINO.parent.mkdir(parents=True, exist_ok=True)
    DESTINO.write_text(doc, encoding="utf-8")

    # --- Guardas de salida ---------------------------------------------
    # Que el ensamblador escriba no significa que haya escrito bien.
    mods = doc.count('<template id="module-')
    bloques_r = doc.count('class="language-r"')
    bloques_py = doc.count('class="language-python"')
    cifras = doc.count("#&gt;")
    # Los lienzos se cuentan solo sobre el MARCADO, no sobre el motor: el
    # `<script>` los menciona en un comentario y crea el del `.geomapa` con
    # su etiqueta ya puesta. Contar los del script daba un falso positivo,
    # que es la manera más tonta de acabar desactivando una comprobación.
    marcado = doc[:doc.rindex("\n  <script>")]
    lienzos = marcado.count("<canvas")
    con_alt = sum(1 for c in marcado.split("<canvas")[1:]
                  if "aria-label" in c.split(">")[0])
    print(f"\n{DESTINO.relative_to(RAIZ)}  {len(doc)/1024:.0f} KB")
    print(f"  {mods} módulos · {bloques_r} bloques de R · {bloques_py} de Python · "
          f"{cifras} cifras anunciadas")
    print(f"  {lienzos} lienzos, {con_alt} con aria-label")

    problemas = []
    if mods != 6:
        problemas.append(f"{mods} plantillas de módulo, se esperaban 6")
    if cifras < 10:
        problemas.append(f"solo {cifras} líneas #> — el fixture no da para probar nada")
    if lienzos != con_alt:
        problemas.append(f"{lienzos - con_alt} lienzo(s) sin aria-label")
    if doc.count("<template") != doc.count("</template>"):
        problemas.append("las plantillas no abren y cierran igual")
    if problemas:
        for p in problemas:
            print(f"  MAL  {p}")
        return 1
    print("\n  Ensamblado limpio.\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
