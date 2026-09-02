#!/usr/bin/env python3
"""
prueba_texto.py — le inyecta defectos al auditor de prosa y exige que los cace

Material de Estadística Espacial 2026-II (20929). T0.5.

POR QUÉ EXISTE. **Un auditor que sale limpio no demuestra nada por sí
solo.** Es la lección que costó cara en Muestreo y que en Diseño de
Experimentos se pagó otra vez: hasta que se construyó este arnés, cinco
auditores de prosa retiraban las fórmulas de KaTeX ANTES de extraer los
números, de modo que **ninguna cifra escrita dentro de una fórmula se
auditaba jamás**. Los cinco informaban «limpio». Entre el 18 % y el 29 %
de los decimales publicados vivían en ese punto ciego.

Un auditor sin arnés no es un auditor verificado: es un auditor cuyo
silencio no se ha interrogado.

Y la lección hermana: **la prueba de una prueba también hay que
probarla.** Cada tanda empieza con un CONTROL sin inyectar nada y exige
que el auditor informe limpio; si el control fallara, cualquier «acierto»
posterior sería falso. Y termina con otro control, para descartar que el
propio arnés haya dejado el capítulo tocado.

CÓMO FUNCIONA. Copia el capítulo, le aplica una sustitución de texto que
introduce un defecto concreto, ejecuta el auditor contra la copia y
comprueba que devuelve código distinto de cero. **El capítulo publicado
no se toca nunca**: el auditor se ejecuta con su variable de entorno
apuntando a la copia, y al final se comprueba byte a byte que el original
sigue igual.

LAS FAMILIAS DE DEFECTO. Cada una imita un fallo que ya ocurrió de verdad
en este proyecto o en los anteriores, que es lo que las hace algo más que
una colección de casos bonitos:

   1. cifra inventada DENTRO de una fórmula de KaTeX   ← el punto ciego
   2. cifra inventada en el texto corrido
   3. cifra inventada en la solución de un ejercicio
   4. un tema del temario que desaparece
   5. una fuente citada que desaparece
   6. un <canvas> que se queda sin aria-label
   7. un enlace local que no resuelve
   8. el marcador del quiz aplanado DENTRO del resumen  ← la regresión que
      en DOE vivió del capítulo 6 al 8 sin que la viera nadie
   9. un CORTE DE CLASE del .geomapa cambiado           ← propia de este curso
  10. el `n` declarado del .geomapa deja de cuadrar con su geometría
  11. una tilde convertida en bytes crudos <c3><b3>     ← propia, T0.5
      o en el escape <U+00F3> de R                     ← propia, T3.3
  12. una afirmación que el capítulo no puede dejar de decir
  13. una cifra de la tabla de discrepancias declaradas

Las 9 y 10 no existían en Diseño de Experimentos porque allí no hay
mapas. Son el punto ciego nuevo de este curso: los cortes de clase, la
leyenda y la geometría viven en JSON dentro del `<script>`, y el auditor
de prosa corta el documento antes de ahí. En T0.3 ya se cobró una pieza
—la leyenda que no se repintaba— con el componente pareciendo perfecto.

La 11 tampoco: se encontró en T0.5 sobre un JSON YA PUBLICADO de T0.4.

**LO QUE ESTE ARNÉS NO PUEDE PROBAR TODAVÍA, dicho en voz alta.** La
comprobación «el capítulo enlaza con el resto del sitio» se ARMA SOLA en
cuanto aparece un `index.html` u otro capítulo al lado, y hoy no hay
ninguno: el sitio es de la Fase 7. Se verificó a mano —creando un hermano
de mentira, el auditor falla— pero no tiene inyección permanente, porque
fabricar un archivo hermano no cabe en un arnés que sustituye texto sin
tocar el proyecto. **Su inyección entra en T7.1**, donde quitar el enlace
del capítulo será una sustitución de texto como las demás. Lo que sí se
inyecta desde ya es un enlace local ROTO, que ejercita la otra rama.

**CADA CIFRA INYECTADA TIENE QUE SER NUEVA.** Si el valor falso ya existe
en el archivo, el auditor lo encuentra en el precálculo y no falla — y el
arnés registraría un «no detectado» que no es del auditor sino del
diseño de la prueba. Se comprueba antes de inyectar.

Uso:  python3 precalculo/prueba_texto.py
Devuelve 1 si algún defecto pasa inadvertido.
"""
from __future__ import annotations

import json
import os
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile

RAIZ = pathlib.Path(__file__).resolve().parent
PROYECTO = RAIZ.parent
SALIDAS = RAIZ / "salidas"

# (auditor, variable de entorno, carpeta, archivo)
SUJETOS = {
    "demo": ("audita_texto_demo.py", "DEMO_HTML",
             PROYECTO / "Htmls_Espacial", "prueba-auditoria.html"),
    "cap1": ("audita_texto_cap1.py", "CAP1_HTML",
             PROYECTO / "Htmls_Espacial", "capitulo-1-datos-espaciales.html"),
    "cap2": ("audita_texto_cap2.py", "CAP2_HTML",
             PROYECTO / "Htmls_Espacial", "capitulo-2-crs-georreferenciacion.html"),
    "cap3": ("audita_texto_cap3.py", "CAP3_HTML",
             PROYECTO / "Htmls_Espacial", "capitulo-3-cartografia-maup.html"),
    "cap4": ("audita_texto_cap4.py", "CAP4_HTML",
             PROYECTO / "Htmls_Espacial", "capitulo-4-patrones-puntuales.html"),
    "cap5": ("audita_texto_cap5.py", "CAP5_HTML",
             PROYECTO / "Htmls_Espacial", "capitulo-5-intensidad-nucleos.html"),
}


def defectos_demo() -> list[tuple[str, str, str]]:
    """Los defectos del fixture, construidos DESDE el precálculo.

    No se escriben a mano por la misma razón que las cifras del capítulo:
    si el precálculo cambia, una lista escrita a mano deja de encontrar su
    texto y el arnés informa «no detectado» cuando en realidad no llegó a
    inyectar nada. Aquí el texto que se busca se construye con las mismas
    cifras que usó el ensamblador.
    """
    D = json.loads((SALIDAS / "demo_auditoria.json").read_text(encoding="utf-8"))
    M = json.loads((SALIDAS / "demo_auditoria_mapa.json").read_text(encoding="utf-8"))
    esc, des, ven, cli, col, nc = (D["escala"], D["desercion"], D["ventanas"],
                                   D["clima"], D["columbus"], D["nc"])

    def f(x, d=5):
        return f"{float(x):.{d}f}"

    def perturba(x, d=5):
        """Cambia el ÚLTIMO decimal. Cinco decimales es la regla de
        publicación de T0.5; con menos, el índice de comparaciones absorbe
        la perturbación, y eso está medido en mide_punto_ciego.py."""
        s = f(x, d)
        ult = s[-1]
        return s[:-1] + ("1" if ult != "1" else "2")

    return [
        # --- 1. Dentro de una fórmula de KaTeX. El punto ciego. --------
        ("cifra inventada DENTRO de una fórmula de KaTeX",
         f"E[I] = {f(des['moran_esperado'], 6)}",
         f"E[I] = {perturba(des['moran_esperado'], 6)}"),
        ("otra cifra inventada dentro de KaTeX (la intensidad urbana)",
         f"= {f(ven['lambda_urbana'])}\n        \\ \\text{{sedes/km}}",
         f"= {perturba(ven['lambda_urbana'])}\n        \\ \\text{{sedes/km}}"),

        # --- 2. Texto corrido -----------------------------------------
        ("cifra inventada en el texto corrido (la caída del I de Moran)",
         f"<strong>{f(esc['caida_pct'])}&nbsp;%</strong>",
         f"<strong>{perturba(esc['caida_pct'])}&nbsp;%</strong>"),
        ("cifra inventada en el texto corrido (el gradiente térmico)",
         f"<strong>{f(cli['gradiente'])}&nbsp;°C",
         f"<strong>{perturba(cli['gradiente'])}&nbsp;°C"),

        # --- 3. Solución de un ejercicio ------------------------------
        ("cifra inventada en la solución de un ejercicio",
         f"<strong>{f(des['recorrido_en_sd'])} desviaciones típicas.</strong>",
         f"<strong>{perturba(des['recorrido_en_sd'])} desviaciones típicas.</strong>"),

        # --- 13. La tabla de discrepancias declaradas -----------------
        ("una cifra de la tabla de discrepancias declaradas",
         f"Municipal: {f(esc['moran_municipal'])} · departamental",
         f"Municipal: {perturba(esc['moran_municipal'])} · departamental"),

        # --- 4. El temario --------------------------------------------
        ("se cae un tema del temario (zero.policy)",
         "zero.policy", "cualquier.cosa"),
        ("se cae un tema del temario (Fisher-Jenks)",
         "Fisher-Jenks", "Otro método"),

        # --- 5. Una fuente --------------------------------------------
        ("se cae la fuente de los límites administrativos (geoBoundaries)",
         "geoBoundaries", "Alguien"),
        ("se cae el texto guía (Pebesma)",
         "Pebesma", "Alguien"),

        # --- 12. Una afirmación que no se puede perder ----------------
        ("se cae la afirmación de que la unidad de análisis es una decisión",
         "decisión de modelado", "cuestión de estilo"),

        # --- 6. Accesibilidad -----------------------------------------
        ("un canvas se queda sin aria-label",
         'aria-label="Serie simulada con tendencia y ruido ajustables"',
         'data-etiqueta="Serie simulada con tendencia y ruido ajustables"'),

        # --- 8. El marcador del quiz, aplanado dentro del resumen -----
        # Marcado válido, equilibrado, con las siete clases presentes y la
        # consola limpia: el motor arranca cada pasada con
        # `resumen.innerHTML = ''`, así que el contador acaba escribiendo
        # en un nodo desconectado. El estudiante no ve NUNCA el contador en
        # vivo ni puede repetir el quiz sin recargar.
        ("el marcador del quiz vuelve a caer DENTRO del resumen",
         '        <div class="quiz-resumen" role="status" hidden></div>\n'
         '        <div class="quiz-marcador">\n'
         '          <span class="quiz-conteo"></span>\n',
         '        <div class="quiz-resumen" hidden>\n'
         '          <p class="quiz-marcador"></p>\n'
         '          <span class="quiz-conteo"></span>\n'),

        # --- 7. Un enlace local que no resuelve -----------------------
        ("un enlace local apunta a un archivo que no existe",
         'href="prueba-geomapa.html"', 'href="prueba-geomapas.html"'),

        # --- 9. Un corte de clase del .geomapa ------------------------
        # El punto ciego propio de este curso. Un corte cambiado no rompe
        # NADA: el mapa se pinta igual de bonito y la leyenda rotula unas
        # clases que ya no son las que R calculó.
        #
        # El texto que se busca se SERIALIZA igual que lo serializó el
        # ensamblador (`json.dumps` con sus separadores por defecto) en vez
        # de escribirse a ojo. La primera versión ponía `"cortes":[…]` sin
        # el espacio y no encontraba nada: el arnés informaba «no
        # detectado» cuando en realidad no había llegado a inyectar. Un
        # fallo de la prueba disfrazado de fallo del auditor es lo peor
        # que le puede pasar a un arnés.
        ("un CORTE DE CLASE del .geomapa deja de ser el que calculó R",
         '"cortes": ' + json.dumps(M["cortes"])[:40],
         '"cortes": ' + json.dumps([M["cortes"][0],
                                    round(float(M["cortes"][1]) + 0.137, 10)]
                                   + M["cortes"][2:])[:40]),

        # --- 10. El n declarado del mapa ------------------------------
        ("el n declarado del .geomapa deja de cuadrar con su geometría",
         f'"n": {M["n"]}, "geom"', f'"n": {int(M["n"]) + 1}, "geom"'),

        # --- 11. Una tilde convertida en bytes crudos -----------------
        # Exactamente lo que jsonlite escribe —sin fallar— cuando R arranca
        # fuera de UTF-8. Encontrado en T0.5 sobre saber11_20224_cifras.json,
        # que ya estaba publicado desde T0.4.
        ("una tilde del mapa sale como bytes crudos <c3><b3>",
         '"titulo": "Deserción escolar',
         '"titulo": "Deserci<c3><b3>n escolar'),
        # LA OTRA FORMA, y la que no cazaba nadie hasta T3.3: la notación
        # `<U+00F3>` con que R imprime lo que su regional no representa.
        # Es peor que la anterior porque NO SE VE: tiene forma de etiqueta,
        # así que el navegador se la traga y la letra desaparece sin más.
        # Los capítulos 2 y 3 se publicaron así.
        ("una tilde del mapa sale como escape de R <U+00F3>",
         '"leyenda": "deserci',
         '"leyenda": "deserci<U+00F3>'),

        # --- Segunda tanda: mecanismos que la primera dejó sin probar ---
        #
        # No están aquí para redondear el marcador. Están porque la
        # primera tanda dejó 62 de 76 comprobaciones **sin haberse visto
        # fallar nunca**, y una comprobación que no ha fallado nunca puede
        # estar bien escrita o ser incapaz de fallar: desde fuera se ven
        # igual. Cada una de éstas ataca un CAMINO DE CÓDIGO distinto, no
        # otra instancia del mismo.
        ("un canvas pierde su role=\"img\"",
         '<canvas aria-label="Función de autocorrelación de la serie elegida" role="img">',
         '<canvas aria-label="Función de autocorrelación de la serie elegida">'),
        ("un desplegable pierde su aria-expanded",
         'class="ejercicio-boton" aria-expanded="false" aria-controls="demo-e1-pista"',
         'class="ejercicio-boton" aria-controls="demo-e1-pista"'),
        ("se cae el <caption> de las tablas",
         "<caption>", "<p class=\"sin-caption\">"),
        ("se cae el scope de las cabeceras de columna",
         'scope="col"', 'class="col"'),
        ("se cae el role=tablist de las pestañas de código",
         'role="tablist"', 'data-rol="tablist"'),
        ("el .geomapa se queda sin su modo declarado",
         '"modo": "poligonos"', '"tipo": "poligonos"'),
        ("el .geomapa se queda sin tabla de respaldo",
         "      tabla: function (d) {", "      _tabla: function (d) {"),
        ("el .geomapa se queda sin etiqueta accesible",
         "      etiqueta: 'Coropleto", "      _etiqueta: 'Coropleto"),
        ("se cae la declaración de que los cortes los calcula classInt",
         "classInt", "algún paquete"),
        ("el documento deja de declarar su codificación",
         'charset="UTF-8"', 'charset="ISO-8859-1"'),
        ("aparece un carácter de reemplazo U+FFFD",
         "La deserción escolar del MEN", "La deserci�n escolar del MEN"),
        ("una plantilla de módulo se queda sin cerrar",
         '<template id="module-6">', '<template id="module-6"><template id="module-6b">'),
        ("se cae una orden de LaTeX que el capítulo debe usar",
         "\\hat", "\\widehat" + "X"),
        ("se cae un símbolo que el capítulo debe conservar (λ)",
         "λ", "@LAMBDA@"),

        # --- Tercera tanda: los cinco mecanismos que seguían sin una
        # sola instancia probada. Salieron de clasificar por familias las
        # comprobaciones que el arnés nunca había visto fallar; sin esa
        # cuenta, «31 de 31» habría tapado que cinco caminos de código no
        # se habían ejercitado jamás.
        ("un contenedor .geomapa se queda sin su registro",
         'data-geomapa="demo-mapa"', 'data-geomapa="demo-mapa-2"'),
        ("el .geomapa se queda sin cortes de clase",
         '"cortes": ' + json.dumps(M["cortes"]), '"_cortes": ' + json.dumps(M["cortes"])),
        ("la geometría del .geomapa se sale del presupuesto",
         '"geom": [', '"relleno": "' + "x" * 130_000 + '", "geom": ['),
        ("el capítulo se sale del presupuesto de peso",
         "</body>", "<!--" + "y" * 320_000 + "-->\n</body>"),
        ("el capítulo se queda sin bloque de autoevaluación",
         '<div class="quiz" data-quiz="demo">', '<div class="cuestionario" data-quiz="demo">'),
    ]


def defectos_cap1() -> list[tuple[str, str, str]]:
    """Los defectos del capítulo 1, construidos DESDE su precálculo.

    Cubre las trece familias del fixture y estrena CUATRO propias del
    capítulo, todas alrededor de la marca de un mapa de puntos:

     14. `marcas_tipo` desaparece  → el navegador tendría que ADIVINAR si
         trece enteros son categorías o una escala, y adivinar bien casi
         siempre es el modo de fallo de este proyecto;
     15. `niveles` desaparece      → un mapa que colorea por categoría sin
         decir cuáles son sus categorías;
     16. un código de marca se sale del rango de niveles;
     17. deja de haber una marca por punto.

    Y una familia que aquí NO se puede probar y se dice en voz alta: el
    capítulo 1 no tiene enlaces LOCALES —todas sus referencias son
    externas—, así que la comprobación de enlaces rotos no tiene sujeto.
    Callarlo la convertiría en una comprobación imaginaria, que sobre el
    informe se lee igual que una que sí corrió.
    """
    D = json.loads((SALIDAS / "cap1_datos.json").read_text(encoding="utf-8"))
    M = json.loads((SALIDAS / "cap1_mapas.json").read_text(encoding="utf-8"))
    S = json.loads((SALIDAS / "cap1_soluciones.json").read_text(encoding="utf-8"))
    sn, tb, es = D["snow"], D["tobler"], D["escala"]
    ir, cv, ag = D["inferencia_real"], D["cv_espacial"], D["agregacion"]

    def f(x, d=5):
        return f"{float(x):.{d}f}"

    def perturba(x, d=5):
        s = f(x, d)
        return s[:-1] + ("1" if s[-1] != "1" else "2")

    return [
        # --- 1. Dentro de una fórmula de KaTeX. El punto ciego. --------
        ("cifra inventada DENTRO de una fórmula de KaTeX",
         f"E[I] = {f(tb['ideam']['esperado'], 6)}",
         f"E[I] = {perturba(tb['ideam']['esperado'], 6)}"),
        # --- 2. En el texto corrido -----------------------------------
        ("la cifra estrella del capítulo, cambiada en la prosa",
         f"{f(sn['pct_mas_cerca_broad'])}&nbsp;%",
         f"{perturba(sn['pct_mas_cerca_broad'])}&nbsp;%"),
        ("el factor del error estándar por bloques, cambiado",
         f"<strong>{f(ir['factor'])}</strong>",
         f"<strong>{perturba(ir['factor'])}</strong>"),
        ("la caída del I de Moran al agregar, cambiada",
         f"{f(es['caida_pct'])}&nbsp;%",
         f"{perturba(es['caida_pct'])}&nbsp;%"),
        ("la inflación del RMSE de la CV aleatoria, cambiada",
         f"{f(cv['inflacion_pct'])}&nbsp;%",
         f"{perturba(cv['inflacion_pct'])}&nbsp;%"),
        ("la subida de la correlación al agregar, cambiada",
         f"{f(ag['subida_pct'])}&nbsp;%",
         f"{perturba(ag['subida_pct'])}&nbsp;%"),
        # --- 3. En la solución de un ejercicio ------------------------
        ("una cifra de la solución del ejercicio 1",
         f"<td>{f(S['e1']['solucion']['factor_suyas'])}</td>",
         f"<td>{perturba(S['e1']['solucion']['factor_suyas'])}</td>"),
        ("una cifra de la solución del ejercicio 3",
         f"<td>{f(S['e3']['solucion']['n_eff'])}</td>",
         f"<td>{perturba(S['e3']['solucion']['n_eff'])}</td>"),
        # --- 4. Un tema del temario que desaparece --------------------
        ("el capítulo deja de hablar de estacionariedad",
         "estacionariedad", "invariancia-en-el-espacio", True),
        ("el capítulo deja de hablar del MAUP",
         "MAUP", "problema-de-la-unidad", True),
        ("el capítulo deja de nombrar classInt",
         "classInt", "cortesDeClase", True),
        # --- 5. Una fuente que desaparece -----------------------------
        ("desaparece la cita a Cressie", "Cressie", "Un autor", True),
        ("desaparece la cita al IDEAM", "IDEAM", "la agencia", True),
        # --- 6. Accesibilidad -----------------------------------------
        ("un <canvas> se queda sin aria-label",
         'aria-label="Ataques y muertes diarias', 'data-label="Ataques y muertes diarias'),
        ("el marcador del quiz se aplana dentro del resumen",
         '<div class="quiz-resumen" role="status" hidden></div>\n        <div class="quiz-marcador">',
         '<div class="quiz-resumen" role="status" hidden>\n        <div class="quiz-marcador">'),
        # --- 9 y 10. El .geomapa --------------------------------------
        ("un corte de clase del mapa de nc cambia",
         f'"cortes": [0, {M["nc"]["cortes"][1]}',
         f'"cortes": [0, {M["nc"]["cortes"][1] + 0.011}'),
        ("un corte de clase del mapa de la deserción cambia",
         f'"cortes": [{M["desercion"]["cortes"][0]}, {M["desercion"]["cortes"][1]}',
         f'"cortes": [{M["desercion"]["cortes"][0]}, {M["desercion"]["cortes"][1] + 0.017}'),
        ("el n declarado del mapa de Snow deja de cuadrar con su geometría",
         f'"q": 4096, "n": {sn["n_muertes"]}, "pts"',
         f'"q": 4096, "n": {sn["n_muertes"] - 3}, "pts"'),
        # --- 11. La codificación --------------------------------------
        ("una tilde se convierte en bytes crudos",
         "Deserción escolar", "Deserci<c3><b3>n escolar"),
        # --- 12. Una afirmación que no puede desaparecer --------------
        # La inyección va contra la FRASE del módulo 7, no contra el «no
        # siempre» suelto. Con el adverbio a secas la prueba era frágil por
        # los dos lados: sustituía la primera aparición fuera cual fuera, y
        # su veneno («casi siempre») es una expresión corriente que cualquier
        # párrafo nuevo podía estrenar — y la estrenó el módulo 2 al explicar
        # el soporte. Aquí el veneno INVIERTE la afirmación en vez de
        # reescribir una palabra, que además es lo que dice el nombre de la
        # prueba.
        ("el capítulo deja de decir que agregar no siempre infla",
         "agregar no siempre infla", "agregar siempre infla"),
        ("el capítulo deja de declarar la frontera con el capítulo 10",
         "es del capítulo 10", "se ve más adelante"),
        ("el capítulo deja de advertir que la CV por bloques no es la buena siempre",
         "no es «la buena» siempre", "es la recomendada"),
        # --- 14 a 17. LAS NUEVAS: la marca de un mapa de puntos -------
        ("el mapa de Snow deja de declarar de qué tipo es su marca",
         '"marcas_tipo": "categoria"', '"marcas_tipo_": "categoria"'),
        ("el mapa de Snow se queda sin los niveles de su marca categórica",
         '"niveles": ["Oxford Market"', '"niveles_": ["Oxford Market"'),
        ("un código de marca se sale del rango de niveles",
         '"marcas": [7, 6, 10, 10', '"marcas": [77, 6, 10, 10'),
        ("deja de haber una marca por punto (se pierde una del IDEAM)",
         '"marcas": [26.1, 19.6,', '"marcas": [19.6,'),
        # --- 7. Un enlace local que no resuelve ------------------------
        # El capítulo no tiene enlaces LOCALES hoy —el sitio es de la Fase
        # 7—, así que la comprobación no tiene sujeto y el auditor lo dice
        # en voz alta. Aquí se le fabrica uno: se convierte una referencia
        # externa en un enlace local a un archivo que no existe. Sin esto,
        # la rama `rotos` del auditor no se habría ejercitado NUNCA, y es
        # la que va a importar en cuanto haya diez capítulos enlazándose.
        ("un enlace local apunta a un archivo que no existe",
         'href="https://r-spatial.org/book/"', 'href="capitulo-99-inexistente.html"'),
        # --- Peso ------------------------------------------------------
        ("el capítulo se pasa del presupuesto de peso",
         "</body>", "<!--" + "y" * 320_000 + "-->\n</body>"),
        # El SEGUNDO quiz, a propósito: la versión anterior del auditor
        # miraba solo el primero y este defecto pasaba inadvertido.
        ("el bloque de la autoevaluación final se queda sin marcador",
         '<div class="quiz" data-quiz="cap1">', '<div class="cuestionario" data-quiz="cap1">'),
        ("el bloque de la diagnóstica de entrada se queda sin marcador",
         '<div class="quiz" data-quiz="cap1-diagnostica">',
         '<div class="cuestionario" data-quiz="cap1-diagnostica">'),
    ]


def defectos_cap2() -> list[tuple[str, str, str]]:
    """Los defectos del capítulo 2, construidos DESDE su precálculo.

    Cubre las mismas familias que el capítulo 1 y estrena DOS que solo
    este capítulo puede probar:

     18. **el enlace local roto**, que en el capítulo 1 no tenía sujeto
         porque no había ningún hermano publicado al que enlazar. Ahora
         el capítulo 2 enlaza al 1, así que la rama que `enlaces()` tenía
         declarada como hueco por fin se ejercita — la comprobación se
         armó sola en cuanto apareció el hermano, que es exactamente para
         lo que se escribió así;
     19. **la afirmación del teorema de Tissot**, que si desaparece deja
         el capítulo diciendo que hay proyecciones perfectas.
    """
    D = json.loads((SALIDAS / "cap2_datos.json").read_text(encoding="utf-8"))
    S = json.loads((SALIDAS / "cap2_soluciones.json").read_text(encoding="utf-8"))
    el, gr, ep = D["elipsoide"], D["grados"], D["epsg"]
    md, po, ig = D["medir"], D["posicional"], D["ingenieria"]
    PT = D["proyecciones"]["tabla"]

    def f(x, d=5):
        return f"{float(x):.{d}f}"

    def perturba(x, d=5):
        s = f(x, d)
        return s[:-1] + ("1" if s[-1] != "1" else "2")

    return [
        # --- 1. Dentro de una fórmula de KaTeX. El punto ciego. --------
        ("una cifra inventada DENTRO de una fórmula de KaTeX",
         r"k^2 = 0.998401", r"k^2 = 0.998411"),
        # --- 2. En el texto corrido -----------------------------------
        ("el desplazamiento medio del datum, cambiado en la prosa",
         f"<strong>{f(el['datum']['desp_medio_m'], 2)}</strong>",
         f"<strong>{perturba(el['datum']['desp_medio_m'], 2)}</strong>"),
        ("el exceso de área de la esfera, cambiado",
         f"<strong>{f(md['colombia']['dif_esfera_pct'])} %</strong>",
         f"<strong>{perturba(md['colombia']['dif_esfera_pct'])} %</strong>"),
        ("la razón mínima de 9377, que es k al cuadrado, cambiada",
         f"<strong>{f(ep['filas'][1]['razon_min'], 6)}</strong>",
         f"<strong>{perturba(ep['filas'][1]['razon_min'], 6)}</strong>"),
        ("la tasa máxima del sesgo posicional, cambiada",
         f"<strong>{f(po['sesgo']['tasa_max_pct'])} %</strong>",
         f"<strong>{perturba(po['sesgo']['tasa_max_pct'])} %</strong>"),
        ("la correlación del sesgo con perímetro/área, cambiada",
         f"<strong>{f(po['sesgo']['corr_pearson'])}</strong>",
         f"<strong>{perturba(po['sesgo']['corr_pearson'])}</strong>"),
        ("un grado de longitud en el ecuador, cambiado",
         f"<strong>{f(gr['lon_m_elipsoide'][0], 2)}", 
         f"<strong>{perturba(gr['lon_m_elipsoide'][0], 2)}"),
        # Aquí NO se perturba el último dígito, y hay que decir por qué: el
        # valor publicado es 57.62068 y el índice guarda 57.6206792983, así
        # que un cambio en la quinta decimal cae DENTRO del punto ciego que
        # `mide_punto_ciego.py` midió en el 4,63 % con cinco decimales.
        # Ajustar el auditor hasta que este caso pase sería maquillar la
        # cobertura; lo honesto es inyectar el error que de verdad se comete
        # —una cifra mal transcrita— y dejar el límite declarado.
        ("la deformación angular máxima de Equal Earth, mal transcrita",
         f"<strong>{f(PT['omega_max_grados'][3])}°</strong>",
         f"<strong>{f(PT['omega_max_grados'][3] + 30)}°</strong>"),
        ("la mediana de la distancia al vecino más próximo, cambiada",
         f"<strong>{f(ig['geohash']['d_vecino_mediana_m'], 1)}",
         f"<strong>{perturba(ig['geohash']['d_vecino_mediana_m'], 1)}"),
        # --- 3. En la solución de un ejercicio ------------------------
        ("una cifra de la solución del ejercicio 1",
         f"<td>{f(S['e1']['solucion']['area_elipsoide_km2'][0])}, ",
         f"<td>{perturba(S['e1']['solucion']['area_elipsoide_km2'][0])}, "),
        ("una cifra de la solución del ejercicio 5",
         f"<td>{f(S['e5']['solucion']['sigma_max_m'])}</td>",
         f"<td>{perturba(S['e5']['solucion']['sigma_max_m'])}</td>"),
        # --- 4. Un tema del temario que desaparece --------------------
        ("el capítulo deja de hablar de la indicatriz",
         "indicatriz", "figurita", True),
        ("el capítulo deja de hablar del geohash",
         "geohash", "codigo-de-celda", True),
        ("el capítulo deja de nombrar st_set_crs",
         "st_set_crs", "ponerLaEtiqueta", True),
        ("el capítulo deja de hablar de DE-9IM",
         "DE-9IM", "matriz-de-nueve", True),
        # --- 5. Una fuente que desaparece -----------------------------
        ("desaparece la cita a Snyder", "Snyder", "Un autor", True),
        ("desaparece la cita al IGAC", "IGAC", "la agencia", True),
        ("desaparece la cita al IDEAM", "IDEAM", "el instituto", True),
        # --- 6. Una afirmación que el capítulo TIENE que hacer --------
        ("desaparece el teorema de Tissot",
         "ninguna de las seis es conforme y", "todas las seis son conformes y", True),
        ("desaparece la advertencia de que el CRS mal puesto no da error",
         "no da error", "se comporta raro", True),
        ("desaparece que el shapefile desfigura y no trunca",
         "No los trunca", "Los acorta", True),
        # --- 7. Accesibilidad y marcado ------------------------------
        ("un lienzo se queda sin aria-label",
         'canvas role="img" aria-label="Los dos radios',
         'canvas role="img" data-label="Los dos radios'),
        # --- 8. La codificación --------------------------------------
        ("una tilde se rompe en bytes crudos", "Bogotá", "Bogot<c3><a1>"),
        # --- 9. EL ENLACE LOCAL ROTO, que en el cap. 1 no tenía sujeto -
        ("el enlace al capítulo 1 apunta a un archivo que no existe",
         'href="capitulo-1-datos-espaciales.html"',
         'href="capitulo-1-datos-espacialess.html"'),
    ]


def defectos_cap3() -> list[tuple[str, str, str]]:
    """Los defectos del capítulo 3, construidos DESDE su precálculo.

    Cubre las mismas familias que los dos anteriores y estrena TRES que
    solo este capítulo puede probar:

     20. **la discrepancia declarada de A.2**, que si se «arregla» deja el
         capítulo afirmando que R y Python clasifican igual — una
         discrepancia sin explicar es un fallo, pero una explicada que
         desaparece también lo es;
     21. **la explicación del mecanismo del módulo 9**, sin la cual el
         resultado contraintuitivo (las zonas arbitrarias dan
         correlaciones MÁS altas) se queda en anécdota;
     22. **la tabla de respaldo de un mapa de capas**, que es la única vía
         al dato para quien no ve el mapa.
    """
    D = json.loads((SALIDAS / "cap3_datos.json").read_text(encoding="utf-8"))

    def f(x, d=5):
        return f"{float(x):.{d}f}"

    def perturba(x, d=5):
        t = f(x, d)
        return t[:-1] + ("1" if t[-1] != "1" else "2")

    return [
        # --- 1. Cifras del texto corrido ------------------------------
        ("la deserción media deja de cuadrar con el precálculo",
         f(D["m1"]["desercion"]["media"]), perturba(D["m1"]["desercion"]["media"])),
        ("el % de municipios que cambian de clase cambia",
         f(D["m4"]["pct_max"]), perturba(D["m4"]["pct_max"])),
        ("la correlación individual de la escalera cambia",
         f(D["m8"]["r_individuo"]), perturba(D["m8"]["r_individuo"])),
        ("la caída del rojo/verde bajo daltonismo cambia",
         f(D["m5"]["rojo_verde"]["caida_pct"]), perturba(D["m5"]["rojo_verde"]["caida_pct"])),
        ("el percentil del trazado real cambia",
         f(D["m9"]["contiguas"]["percentil_real"]),
         perturba(D["m9"]["contiguas"]["percentil_real"])),
        # --- 2. Cifras de una tabla -----------------------------------
        ("una cifra de la tabla de cartogramas cambia",
         f(D["m7"]["cartogramas"][2]["corr"], 6),
         perturba(D["m7"]["cartogramas"][2]["corr"], 6)),
        # --- 3. Cobertura del temario ---------------------------------
        ("el capítulo deja de hablar del gerrymandering",
         "gerrymandering", "reparto de distritos", True),
        ("el capítulo deja de nombrar los símbolos proporcionales",
         "ímbolos proporcionales", "urbujas de tamaño variable", True),
        # --- 4. Fuentes -----------------------------------------------
        ("desaparece la cita a Robinson", "Robinson", "un autor", True),
        ("desaparece la cita a Machado", "Machado", "los autores", True),
        # --- 5. Afirmaciones que el capítulo TIENE que hacer -----------
        ("desaparece que elegir el mapa es una decisión de modelado",
         "decisión de modelado", "cuestión de gusto", True),
        ("desaparece que el cartograma contiguo no puede ser exacto",
         "conservar la topología", "hacer otras cosas", True),
        ("desaparece que el ponderador es parte del trazado",
         "parte del trazado", "un detalle más", True),
        # --- 6. LA DISCREPANCIA DECLARADA DE A.2 ----------------------
        ("desaparece la causa de que R y Python clasifiquen distinto",
         "lado cerrado del intervalo", "una diferencia de implementación", True),
        ("desaparece que Fisher-Jenks sí coincide",
         "coincide exactamente", "también difiere", True),
        # --- 7. EL MECANISMO DEL MÓDULO 9 -----------------------------
        ("desaparece la explicación del resultado contraintuitivo",
         "Es lo contrario de lo que casi todo el mundo espera",
         "Es lo que cabía esperar", True),
        # --- 8. Accesibilidad y marcado -------------------------------
        ("un lienzo se queda sin aria-label",
         'canvas role="img" aria-label="Las 35 formas',
         'canvas role="img" data-label="Las 35 formas'),
        ("TODOS los mapas de capas se quedan sin tabla de respaldo",
         "tabla: d => tablaCapa", "sinTabla: d => tablaCapa", True),
        # --- 9. La codificación ---------------------------------------
        ("una tilde se rompe en bytes crudos", "Bogotá", "Bogot<c3><a1>"),
        # --- 10. El enlace local roto ---------------------------------
        ("el enlace al capítulo 2 apunta a un archivo que no existe",
         'href="capitulo-2-crs-georreferenciacion.html"',
         'href="capitulo-2-crs-georreferenciacionn.html"'),
    ]


def defectos_cap4() -> list[tuple[str, str, str]]:
    """Los defectos del capítulo 4, construidos DESDE su precálculo.

    Cubre las familias de los anteriores y estrena TRES que solo este
    capítulo puede probar:

     23. **la tabla de respaldo de los dos mapas del módulo 5**, que es la
         única vía al dato de quien no ve los dos lienzos: el módulo
         afirma que la rebaraja conserva el conteo de cada celda y remata
         con «Míralos». Sin la tabla, esa afirmación no es comprobable
         para ese lector, y el capítulo entero se apoya en ella;
     24. **la corrección de borde declarada**, que es la decisión cara de
         la Fase 3: si desaparece la frase, el capítulo usa traslación y
         no lo dice, que es exactamente el atajo silencioso que la
         decisión existe para no dar;
     25. **la aritmética del p-valor mínimo**, sin la cual el módulo 11
         deja de explicar por qué 1/(nsim+1) no es una convención.

    UNA FAMILIA QUE AQUÍ NO SE PUEDE PROBAR, y se dice en voz alta: los
    siete mapas de este capítulo son de modo `puntos` y **ninguno
    clasifica**, así que no hay un solo corte de clase que alterar. La
    inyección 9 —el corte del `.geomapa` cambiado— no tiene sujeto en el
    capítulo 4. La rama hermana sí se ejercita: el `n` declarado que deja
    de cuadrar con su geometría.
    """
    D = json.loads((SALIDAS / "cap4_datos.json").read_text(encoding="utf-8"))
    S = json.loads((SALIDAS / "cap4_soluciones.json").read_text(encoding="utf-8"))
    m1, m2, m3, m5 = D["m1"], D["m2"], D["m3"], D["m5"]
    m7, m8, m9, m10, m11 = D["m7"], D["m8"], D["m9"], D["m10"], D["m11"]

    def f(x, d=5):
        return f"{float(x):.{d}f}"

    def perturba(x, d=5):
        t = f(x, d)
        return t[:-1] + ("1" if t[-1] != "1" else "2")

    return [
        # --- 1. Dentro de una fórmula de KaTeX. El punto ciego. --------
        # La lambda urbana aparece DOS veces con dos redondeos distintos:
        # a cinco decimales en la prosa y a cuatro dentro de la fórmula.
        # Ésta es la de la fórmula, que es la que el auditor de DOE no
        # miraba.
        ("cifra inventada DENTRO de una fórmula de KaTeX",
         f"= {f(m1['urbana']['lambda_km2'], 4)}\\ \\text{{sedes/km}}^2",
         f"= {perturba(m1['urbana']['lambda_km2'], 4)}\\ \\text{{sedes/km}}^2"),
        # --- 2. En el texto corrido -----------------------------------
        ("el área de la ventana urbana, cambiada en la prosa",
         f"<strong>{f(m1['urbana']['area_km2'])}</strong> km²",
         f"<strong>{perturba(m1['urbana']['area_km2'])}</strong> km²"),
        ("el factor entre las dos intensidades, cambiado",
         f"<strong>{f(m1['factor_lambda'])}</strong>",
         f"<strong>{perturba(m1['factor_lambda'])}</strong>"),
        ("el índice de dispersión de los cuadrantes, cambiado",
         f"<strong>{f(m2['urbana']['dispersion'])}</strong>",
         f"<strong>{perturba(m2['urbana']['dispersion'])}</strong>"),
        ("la R de Clark-Evans de las sedes, cambiada en su tabla",
         f"<strong>{f(m3['bogota']['clark_evans'])}</strong>",
         f"<strong>{perturba(m3['bogota']['clark_evans'])}</strong>"),
        ("el átomo de G en r = 0, cambiado",
         f"<strong>{f(m7['bogota']['g_emp_en_cero'], 6)}</strong>",
         f"<strong>{perturba(m7['bogota']['g_emp_en_cero'], 6)}</strong>"),
        ("el máximo de g sobre las secuoyas, cambiado",
         f"<strong>{f(m9['redwood']['g_max'])}</strong>",
         f"<strong>{perturba(m9['redwood']['g_max'])}</strong>"),
        ("el sesgo máximo de la K sin corregir, cambiado",
         f"<strong>{f(m10['sesgo_max_pct'])}</strong> %",
         f"<strong>{perturba(m10['sesgo_max_pct'])}</strong> %"),
        ("el porcentaje de simulaciones nulas que se salen, cambiado",
         f"<strong>{f(m11['tasa_salida_bogota']['pct'])}</strong> %",
         f"<strong>{perturba(m11['tasa_salida_bogota']['pct'])}</strong> %"),
        ("cuánto se ensancha la banda por defecto, cambiado",
         f"—{f(m11['escala_resumen']['veces_defecto'])} veces",
         f"—{perturba(m11['escala_resumen']['veces_defecto'])} veces"),
        # --- 3. En la solución de un ejercicio ------------------------
        ("una cifra de la solución del ejercicio 1",
         f"<td>{S['e1']['solucion']['area_km2'] if 'area_km2' in S['e1']['solucion'] else S['e1']['pasos'][3]['valor']}</td>",
         f"<td>{perturba(S['e1']['pasos'][3]['valor'], 10)}</td>"),
        ("una cifra de la solución del ejercicio 5",
         f"<td>{S['e5']['pasos'][3]['valor']}</td>",
         f"<td>{perturba(S['e5']['pasos'][3]['valor'], 10)}</td>"),
        # --- 4. Un tema del temario que desaparece --------------------
        ("el capítulo deja de hablar del MAUP",
         "MAUP", "problema-de-la-unidad", True),
        ("el capítulo deja de nombrar la correlación de pares",
         "correlación de pares", "la otra función", True),
        ("el capítulo deja de nombrar el test de desviación global",
         "desviación global", "el otro contraste", True),
        # --- 5. Una fuente que desaparece -----------------------------
        ("desaparece la cita a Ripley", "Ripley", "un autor", True),
        ("desaparece la cita a Besag", "Besag", "otro autor", True),
        ("desaparece la cita a Donnelly", "Donnelly", "la del libro", True),
        # --- 6. Accesibilidad -----------------------------------------
        ("un <canvas> se queda sin aria-label",
         'aria-label="K y L sobre el mismo patrón',
         'data-label="K y L sobre el mismo patrón'),
        ("el marcador del quiz se aplana dentro del resumen",
         '<div class="quiz-resumen" role="status" hidden></div>\n        <div class="quiz-marcador">',
         '<div class="quiz-resumen" role="status" hidden>\n        <div class="quiz-marcador">'),
        # --- 23. LA TABLA DE RESPALDO DEL MÓDULO 5 --------------------
        ("los dos mapas del módulo 5 se quedan sin tabla de respaldo",
         ", tabla: function () {", ", sinTabla: function () {", True),
        # --- 10. El .geomapa: el n que deja de cuadrar ----------------
        ("el n declarado del patrón urbano deja de cuadrar con su geometría",
         f'"n": {m1["urbana"]["n"]}, "pts"',
         f'"n": {m1["urbana"]["n"] - 4}, "pts"'),
        # --- 11. La codificación --------------------------------------
        ("una tilde se convierte en bytes crudos",
         "Perímetro urbano", "Per<c3><ad>metro urbano"),
        ("una tilde se convierte en el escape <U+00ED> de R",
         "Perímetro urbano", "Per<U+00ED>metro urbano", True),
        # --- 12. Afirmaciones que el capítulo no puede dejar de decir --
        ("desaparece que ignorar el borde no añade ruido sino dirección",
         "no añade ruido", "no cambia gran cosa", True),
        ("desaparece la razón del signo del sesgo",
         "Faltan vecinos, nunca sobran", "Los vecinos van y vienen", True),
        # --- 24. LA CORRECCIÓN DECLARADA, la decisión cara de la Fase 3
        # OJO CON LA MAYÚSCULA Y CON EL SALTO DE LÍNEA. El auditor busca
        # sobre `texto_plano`, que va en minúsculas y con los espacios
        # colapsados; el arnés sustituye sobre el HTML CRUDO, donde la
        # frase abre oración y la siguiente lleva un salto y ocho espacios
        # en medio. Escribir aquí la forma del auditor da «el texto a
        # sustituir no aparece», que es un fallo de la prueba disfrazado
        # de fallo del capítulo.
        ("desaparece que la corrección elegida no es un atajo silencioso",
         "No es un atajo silencioso", "Es lo que se suele hacer", True),
        # --- 25. LA ARITMÉTICA DEL P-VALOR MÍNIMO --------------------
        ("desaparece que el p-valor mínimo es aritmética y no convención",
         "aritmética.", "lo habitual.", True),
        ("desaparece que subir nsim cambia de contraste",
         "cambia de contraste", "afina la misma banda", True),
        # --- 7. El enlace local roto ---------------------------------
        ("el enlace al capítulo 3 apunta a un archivo que no existe",
         'href="capitulo-3-cartografia-maup.html"',
         'href="capitulo-3-cartografia-maupp.html"'),
    ]


def defectos_cap5() -> list[tuple[str, str, str]]:
    """Los defectos del capítulo 5, construidos DESDE su precálculo.

    Cubre las familias de los anteriores y estrena SEIS que solo este
    capítulo puede probar, todas alrededor de lo que estrena el capítulo:
    superficies en vez de geometría.

     26. **un CORTE DE CLASE del `.geomapa` cambiado.** La familia 9 del
         fixture llevaba sin sujeto desde el capítulo 1: los mapas de los
         capítulos 1 a 4 son de puntos y **ninguno clasifica**, así que no
         había un solo corte que alterar —el auditor del 4 lo dejó dicho
         en voz alta—. Los tres rásteres de éste sí clasifican, y aquí la
         rama se ejercita por fin sobre un sujeto de verdad.
     27. **un σ del deslizador que deja de casar con el del dato.** Es la
         trampa de T1.2 y T1.3 en su tercera forma: no emparejar por
         índice, sino emparejar por una clave escrita dos veces. El
         `find()` del navegador devolvería `undefined` y el mapa saldría
         **en blanco con la consola limpia**.
     28. **una superficie con escala de color propia.** Las siete
         comparten escala a propósito: normalizada cada una contra su
         máximo, las siete saldrían igual de intensas y el mapa afirmaría
         justo lo contrario que la tabla del módulo 2.
     29. **una superficie que llega sin empaquetar.** El decodificador de
         la plantilla espera `zqm`/`zqd`; con el array `zq` entero
         dibujaría en blanco, otra vez sin un error en consola.
     30. **la tabla de respaldo del deslizador**, que es la única vía al
         dato de quien no ve el lienzo: el módulo 2 dice «mueve el
         deslizador y mira la ciudad», y de sus siete máximos la prosa
         solo publica el primero y el último. Es el A.20.2 del capítulo 4
         en este capítulo.
     31. **el `niveles` del mapa por sector**, sin el cual un código de
         marca no se puede contrastar contra nada.

    UNA FAMILIA QUE AQUÍ NO SE PUEDE PROBAR, y se dice en voz alta: la 1,
    la cifra inventada DENTRO de una fórmula de KaTeX. Este capítulo
    publica cinco fórmulas y **ninguna lleva una medición dentro**: sus
    únicos dígitos son estructurales —el 1 de `\\frac{1}{e(u)}`, el `i=1`
    de un sumatorio, los subíndices de `\\lambda_1` y `\\beta_0`—. Cambiar
    uno rompería la matemática, no fabricaría una cifra falsa, y además
    caería bajo la regla del entero pequeño del propio auditor: la
    inyección sería INERTE. La rama sí está ejercitada, por los capítulos
    1 a 4, que publican cifras medidas dentro de sus fórmulas.
    """
    D = json.loads((SALIDAS / "cap5_datos.json").read_text(encoding="utf-8"))
    S = json.loads((SALIDAS / "cap5_soluciones.json").read_text(encoding="utf-8"))
    M = json.loads((SALIDAS / "cap5_mapas.json").read_text(encoding="utf-8"))
    m1, m3, m4, m6 = D["m1"], D["m3"], D["m4"], D["m6"]
    m7, m8, m9, m10, m11 = D["m7"], D["m8"], D["m9"], D["m10"], D["m11"]
    dv = {d["modelo"]: d for d in m11["divergencia"]}

    def f(x, d=5):
        return f"{float(x):.{d}f}"

    def perturba(x, d=5):
        t = f(x, d)
        return t[:-1] + ("1" if t[-1] != "1" else "2")

    # Una cifra en notación científica se perturba en su MANTISA, no en su
    # exponente: cambiar 1.794e-10 por 1.794e-11 daría un número de otro
    # orden, que es un defecto mucho más grosero que el que se quiere
    # imitar —el dígito mal copiado—.
    def perturba_g(x):
        t = f"{abs(float(x)):g}"
        mant, _, exp = t.partition("e")
        mant = mant[:-1] + ("1" if mant[-1] != "1" else "2")
        return mant + ("e" + exp if exp else "")

    return [
        # --- 2. En el texto corrido -----------------------------------
        ("el área de la ventana de Kennedy, cambiada en la prosa",
         f"<strong>{f(m1['ventana']['area_km2'], 2)}</strong> km²",
         f"<strong>{perturba(m1['ventana']['area_km2'], 2)}</strong> km²"),
        ("cuánto discrepan los cuatro selectores sobre la ciudad, cambiado",
         f"<strong>{f(m3['urbana']['razon'])}</strong> veces",
         f"<strong>{perturba(m3['urbana']['razon'])}</strong> veces"),
        ("la horquilla entre corregir y no corregir el borde, cambiada",
         f"<strong>{f(m4['horquilla_pct'])}</strong> puntos porcentuales",
         f"<strong>{perturba(m4['horquilla_pct'])}</strong> puntos porcentuales"),
        ("la mediana de la superficie de P(oficial), cambiada",
         f"<strong>{f(m6['bogota']['p_mediana'], 4)}</strong>",
         f"<strong>{perturba(m6['bogota']['p_mediana'], 4)}</strong>"),
        ("la razón del bulto de la curva rhohat colombiana, cambiada",
         f"<strong>{f(m7['bogota']['curva']['razon_bulto'])}</strong> veces",
         f"<strong>{perturba(m7['bogota']['curva']['razon_bulto'])}</strong> veces"),
        ("cuánto mueve la cuadratura al coeficiente, cambiado",
         f"<strong>{f(m8['cuadratura']['rango_pendiente_en_ee'])}</strong> errores estándar",
         f"<strong>{perturba(m8['cuadratura']['rango_pendiente_en_ee'])}</strong> errores estándar"),
        # LA RAMA NUEVA DEL NÚCLEO (T3.6): una cifra en notación
        # científica. Hasta este capítulo el índice guardaba la mantisa
        # suelta y el extractor se llevaba el literal entero, así que
        # ninguna de estas se podía respaldar. Sin esta inyección, el
        # arreglo no tendría quien lo vigile.
        ("el número de condición del ajuste crudo, cambiado en su mantisa",
         f"<strong>{m9['crudo']['cond_reciproco']:g}</strong>",
         f"<strong>{perturba_g(m9['crudo']['cond_reciproco'])}</strong>"),
        ("cuánto mejora el condicionamiento al centrar, cambiado",
         f"<strong>{m9['mejora_condicion']:g}</strong> veces mejor",
         f"<strong>{perturba_g(m9['mejora_condicion'])}</strong> veces mejor"),
        ("el primer radio en que la K se sale de la banda, cambiado",
         f"<strong>{f(m10['primer_r_fuera_m'])}</strong> m",
         f"<strong>{perturba(m10['primer_r_fuera_m'])}</strong> m"),
        ("cuántas veces más rápido es el ajuste con traslación, cambiado",
         f"<strong>{f(dv['Thomas']['veces_mas_rapido'])}</strong> veces más rápido",
         f"<strong>{perturba(dv['Thomas']['veces_mas_rapido'])}</strong> veces más rápido"),
        ("el índice de dispersión del Hawkes, cambiado",
         f"<strong>{f(m11['hawkes']['dispersion_hawkes'])}</strong>",
         f"<strong>{perturba(m11['hawkes']['dispersion_hawkes'])}</strong>"),
        # --- 3. En la solución de un ejercicio ------------------------
        ("una cifra de la solución del ejercicio 2",
         f"<td>{S['e2']['pasos'][2]['valor']:g}</td>",
         f"<td>{perturba(S['e2']['pasos'][2]['valor'], 10)}</td>"),
        ("una cifra de la solución del ejercicio 5",
         f"<td>{S['e5']['pasos'][4]['valor']:g}</td>",
         f"<td>{perturba(S['e5']['pasos'][4]['valor'], 10)}</td>"),
        # --- 4. Un tema del temario que desaparece --------------------
        ("el capítulo deja de hablar de rhohat",
         "rhohat", "la-otra-curva", True),
        ("el capítulo deja de nombrar el contraste mínimo",
         "contraste mínimo", "el otro ajuste", True),
        ("el capítulo deja de formular el proyecto integrador",
         "proyecto integrador", "trabajo de fin de bloque", True),
        # --- 5. Una fuente que desaparece -----------------------------
        ("desaparece la cita a Cronie", "Cronie", "un autor", True),
        ("desaparece la cita a Berman", "Berman", "otro autor", True),
        ("desaparece la cita a Ogata", "Ogata", "cierto autor", True),
        # --- 6. Accesibilidad -----------------------------------------
        ("un <canvas> se queda sin aria-label",
         'aria-label="Kennedy: las 262 sedes',
         'data-label="Kennedy: las 262 sedes'),
        ("el marcador del quiz se aplana dentro del resumen",
         '<div class="quiz-resumen" role="status" hidden></div>\n        <div class="quiz-marcador">',
         '<div class="quiz-resumen" role="status" hidden>\n        <div class="quiz-marcador">'),
        # --- 26. EL CORTE DE CLASE, por fin con sujeto ----------------
        ("un corte de clase del ráster de proporción deja de ser el de R",
         '"cortes": [0, ' + f"{M['proporcion_oficial']['cortes'][1]:g}",
         '"cortes": [0, ' + perturba_g(M['proporcion_oficial']['cortes'][1])),
        # --- 10. El .geomapa: el n que deja de cuadrar ----------------
        ("el n declarado del patrón por sector deja de cuadrar con su geometría",
         f'"n": {M["sector_puntos"]["n"]}, "pts"',
         f'"n": {M["sector_puntos"]["n"] - 3}, "pts"'),
        # --- 31. Los niveles de la marca ------------------------------
        ("el mapa por sector se queda sin los niveles de su marca",
         '"niveles": ["oficial"', '"_niveles": ["oficial"'),
        # --- 27, 28, 29, 30. Las siete superficies del deslizador -----
        ("un σ del deslizador deja de casar con el del dato",
         f'"sigma_m": {json.dumps(D["m2"]["familia"]["sigmas_m"][0])}',
         f'"sigma_m": {perturba(D["m2"]["familia"]["sigmas_m"][0], 4)}'),
        ("una superficie del deslizador se queda con escala propia",
         '"escala_comun"', '"escala_propia"'),
        ("una superficie del deslizador llega sin empaquetar",
         '"zqd"', '"zq"'),
        ("el deslizador se queda sin su tabla de respaldo",
         ", tabla: function () {", ", sinTabla: function () {", True),
        # --- 11. La codificación --------------------------------------
        ("una tilde se convierte en bytes crudos",
         "núcleos", "n<c3><ba>cleos"),
        ("una tilde se convierte en el escape <U+00FA> de R",
         "núcleos", "n<U+00FA>cleos", True),
        # --- 12. Afirmaciones que el capítulo no puede dejar de decir --
        ("desaparece que «el ancho óptimo» no es una propiedad del patrón",
         "no es una propiedad del patrón", "es difícil de elegir", True),
        ("desaparece que las tres correcciones dan mapas igual de plausibles",
         "los tres salen plausibles", "cuesta distinguirlos", True),
        ("desaparece que llamar «demanda» a un mapa es una decisión",
         "es una decisión, no una descripción", "conviene pensarlo", True),
        ("desaparece qué es un residuo en un proceso puntual",
         "No hay un residuo por observación", "Los residuos salen aparte", True),
        ("desaparece que cambiar la corrección de kppm es otra respuesta",
         "es otra respuesta", "tarda menos", True),
        ("desaparece que la fuente del caso trabajado no llegó",
         "La fuente no llegó", "La fuente se consultó", True),
        # --- LOS MECANISMOS QUE NINGÚN CAPÍTULO HABÍA VISTO FALLAR ---
        # El arnés imprime cuántas comprobaciones se ha visto caer, y al
        # mirar la lista de este capítulo quedaban dentro de `geomapas()`
        # y de `accesibilidad()` mecanismos enteros que nadie había
        # tumbado nunca: no instancias repetidas de algo ya demostrado,
        # sino caminos de código distintos. Se atacan aquí uno a uno.
        ("un contenedor .geomapa se queda sin su registro",
         'data-geomapa="cap5-oferta"', 'data-geomapa="cap5-oferta-2"'),
        ("un .geomapa deja de declarar su modo",
         '{"modo": "rejilla", "titulo": "Proporción',
         '{"_modo": "rejilla", "titulo": "Proporción'),
        ("un ráster se queda sin sus cortes de clase",
         '"rango": [0, 1], "cortes"', '"rango": [0, 1], "_cortes"'),
        ("el mapa por sector deja de declarar el tipo de su marca",
         '"marcas_tipo": "categoria"', '"marcas_tipo": "vaya usted a saber"'),
        ("ningún mapa declara ya su etiqueta accesible",
         "etiqueta: ", "rotulo: ", True),
        ("el capítulo deja de declarar que los cortes los calcula classInt",
         "classInt", "otra-cosa", True),
        ("la geometría de un mapa se sale de su presupuesto",
         '"pts": [', '"relleno": "' + "x" * 130_000 + '", "pts": ['),
        ("un <canvas> se queda sin role=\"img\"",
         '<canvas role="img" aria-label="El pico contra',
         '<canvas aria-label="El pico contra'),
        ("un desplegable de ejercicio pierde su aria-controls",
         'aria-expanded="false" aria-controls="cap5-e1-sol"',
         'aria-expanded="false" data-controls="cap5-e1-sol"'),
        # LA FAMILIA 1 POR SU OTRA PUERTA (T3.6). No es «una cifra falsa
        # dentro de una fórmula» —este capítulo no publica ninguna cifra
        # medida dentro de KaTeX— sino lo que la haría INVISIBLE: un `<`
        # sin escapar dentro de una fórmula, tras el cual el despojador de
        # etiquetas se traga todo hasta el siguiente `>`. La fórmula de
        # Hawkes lo llevaba, y por eso existe ahora la guarda del núcleo.
        ("una fórmula recupera su «<» sin escapar",
         r"\sum_{t_i &lt; t}", r"\sum_{t_i < t}"),
        ("un bloque de pestañas R/Python se queda sin role=tablist",
         'class="code-tabs-nav" role="tablist" aria-label="La ventana de Kennedy',
         'class="code-tabs-nav" aria-label="La ventana de Kennedy'),
        ("un bloque de autoevaluación se queda sin su marcado",
         '<div class="quiz" data-quiz="cap5-quiz">',
         '<div class="cuestionario" data-quiz="cap5-quiz">'),
        # --- 7. El enlace local roto ---------------------------------
        ("el enlace al capítulo 4 apunta a un archivo que no existe",
         'href="capitulo-4-patrones-puntuales.html"',
         'href="capitulo-4-patrones-puntualess.html"'),
        # --- Peso -----------------------------------------------------
        ("el capítulo se pasa de su propio tope de peso",
         "</body>", "<!--" + "y" * 320_000 + "-->\n</body>"),
    ]


DEFECTOS = {"demo": defectos_demo, "cap1": defectos_cap1,
            "cap2": defectos_cap2, "cap3": defectos_cap3,
            "cap4": defectos_cap4, "cap5": defectos_cap5}


def corre(clave: str, ruta_html: pathlib.Path) -> tuple[int, str]:
    auditor, var, _, _ = SUJETOS[clave]
    entorno = dict(os.environ, **{var: str(ruta_html)})
    res = subprocess.run([sys.executable, str(RAIZ / auditor)],
                         capture_output=True, text=True, cwd=str(RAIZ), env=entorno)
    return res.returncode, res.stdout + res.stderr


def resumen(salida: str) -> str:
    m = re.search(r"(\d+) comprobaciones · (\d+) fallos", salida)
    return m.group(0) if m else "(sin resumen)"


def nombres(salida: str, estado: str) -> set[str]:
    """Los nombres de las comprobaciones en un estado dado (OK o MAL).

    Sirve para la pregunta incómoda del final: de todas las
    comprobaciones que el auditor ejecuta, ¿cuántas se ha VISTO fallar?
    Una comprobación que nunca ha fallado puede estar bien escrita o
    puede ser incapaz de fallar, y desde fuera las dos se ven igual.
    """
    fuera = set()
    for linea in salida.splitlines():
        m = re.match(r"\s{2}" + estado + r"\s{2,}(\S.*?)\s{2,}", linea + "  ")
        if m:
            fuera.add(m.group(1).strip())
    return fuera


def prueba(clave: str) -> tuple[int, int]:
    """Devuelve (defectos cazados, defectos inyectados).

    Un control que falla devuelve (0, n): sin control no hay prueba, y
    contarlo como acierto sería exactamente el autoengaño que este arnés
    existe para evitar.
    """
    _, _, carpeta, nombre = SUJETOS[clave]
    capitulo = carpeta / nombre
    defectos = DEFECTOS[clave]()
    print(f"\n--- {nombre} " + "-" * 40)
    if not capitulo.exists():
        print(f"  MAL  falta {capitulo}")
        return 0, len(defectos)

    original = capitulo.read_text(encoding="utf-8")
    tmp = pathlib.Path(tempfile.mkdtemp(prefix=f"prueba_texto_{clave}_"))
    copia = tmp / capitulo.name
    try:
        # --- CONTROL: sin inyectar nada, el auditor tiene que salir limpio.
        shutil.copy(capitulo, copia)
        codigo, salida = corre(clave, copia)
        print(f"  {'OK ' if codigo == 0 else 'MAL'}  control · sin inyectar nada")
        print(f"        {resumen(salida)}")
        if codigo != 0:
            print("  PARADO: el control falla, así que el arnés no prueba nada.")
            for linea in salida.strip().splitlines():
                if linea.strip().startswith("- "):
                    print(f"        {linea.strip()}")
            return 0, len(defectos)

        todas = nombres(salida, "OK ")
        vistas_fallar: set[str] = set()

        cazados = 0
        for defecto in defectos:
            # Tercer campo opcional `todas`: si el defecto es «se cae un
            # tema», hay que quitarlo de TODAS partes, no de la primera
            # aparición — si no, el tema sigue en el documento y el arnés
            # apunta un «no detectado» que es culpa de la prueba, no del
            # auditor. Antes esto se decidía por el PREFIJO del nombre del
            # defecto («se cae…»), y eso es una convención que se rompe en
            # cuanto alguien redacta el nombre de otra manera: el capítulo 1
            # perdió así cinco inyecciones de golpe. Ahora se declara.
            if len(defecto) == 4:
                nombre_d, busca, pone, en_todas = defecto
            else:
                nombre_d, busca, pone = defecto
                en_todas = nombre_d.startswith("se cae")
            if original.count(busca) < 1:
                print(f"  MAL  {nombre_d}")
                print(f"        el texto a sustituir no aparece: {busca[:74]!r}")
                continue
            # La cifra falsa NO puede existir ya en el archivo: si existe,
            # el auditor la da por buena y el «no detectado» sería culpa de
            # la prueba, no del auditor.
            nuevo = original.replace(busca, pone) if en_todas \
                else original.replace(busca, pone, 1)
            solo_nuevo = pone.strip()
            if solo_nuevo and original.count(solo_nuevo) > 0:
                print(f"  MAL  {nombre_d}")
                print(f"        el valor inyectado YA existe en el archivo; "
                      f"la prueba no probaría nada")
                continue
            copia.write_text(nuevo, encoding="utf-8")
            codigo, salida = corre(clave, copia)
            ok = codigo != 0
            cazados += ok
            vistas_fallar |= nombres(salida, "MAL")
            print(f"  {'OK ' if ok else 'MAL'}  {nombre_d}")
            print(f"        {resumen(salida)}")

        # --- CONTROL FINAL: el capítulo original sigue limpio.
        shutil.copy(capitulo, copia)
        codigo, salida = corre(clave, copia)
        print(f"  {'OK ' if codigo == 0 else 'MAL'}  control final · el capítulo sigue limpio")
        print(f"        {resumen(salida)}")
        if codigo != 0:
            return 0, len(defectos)

        # La pregunta que un 17 de 17 no contesta: ¿y las OTRAS
        # comprobaciones? Un arnés mide lo que se le ocurrió inyectar, no
        # lo que el auditor cubre. Se publica la brecha en vez de dejar
        # que el 100 % la tape.
        sin_probar = sorted(todas - vistas_fallar)
        print(f"\n  Cobertura del arnés: {len(vistas_fallar)} de {len(todas)} "
              f"comprobaciones se han VISTO fallar.")
        if sin_probar:
            print(f"  Las otras {len(sin_probar)} pueden estar bien escritas o ser")
            print("  incapaces de fallar; desde fuera se ven igual. Muestra:")
            for x in sin_probar[:8]:
                print(f"    · {x}")
        return cazados, len(defectos)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
        # El capítulo publicado no se ha tocado en ningún momento.
        assert capitulo.read_text(encoding="utf-8") == original, \
            f"el capítulo {nombre} cambió durante la prueba"


def main(argv: list[str]) -> int:
    pedidos = argv or sorted(SUJETOS)
    malos = [c for c in pedidos if c not in SUJETOS]
    if malos:
        sys.exit(f"PARADO: no hay auditor de prosa para {malos}")

    print("\n=== prueba_texto.py ===")
    total_ok = total = 0
    por_sujeto = {}
    for clave in pedidos:
        ok, n = prueba(clave)
        por_sujeto[clave] = (ok, n)
        total_ok += ok
        total += n

    print("\n=== RESULTADO =============================================")
    for clave, (ok, n) in por_sujeto.items():
        print(f"  {clave}: {ok} de {n}"
              + ("" if ok == n else "   ← HAY DEFECTOS QUE PASAN INADVERTIDOS"))
    print(f"\n  {total} defectos inyectados · {total_ok} detectados")
    if total_ok == total:
        print(f"  El auditor de prosa los caza los {total}.\n")
        return 0
    print("  HAY DEFECTOS QUE PASAN INADVERTIDOS.\n")
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
