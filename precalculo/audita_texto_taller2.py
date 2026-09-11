#!/usr/bin/env python3
"""
audita_texto_taller2.py — las cifras de la prosa del Taller 2 (C7)

Material de Estadística Espacial 2026-II (20929). Ver PLAN_Taller_2_Cap_4.md.

Mismo núcleo que los auditores de prosa de los capítulos —`audita_texto_base`—
y por la misma razón: la maquinaria vive una vez, cada documento declara
QUÉ hay que comprobar. Ver la cabecera de ese archivo para el porqué.

QUÉ CAMBIA EN UN TALLER, Y POR QUÉ NO SE LLAMAN TODAS LAS FAMILIAS

Un taller no es un capítulo, y forzarlo a pasar las comprobaciones de uno
sería peor que no hacerlas: se aprueban por vacuidad y el informe queda
verde sobre algo que nadie miró. Se declara aquí qué NO se llama, con el
mismo criterio que el Taller 1:

  · `accesibilidad()` — exige al menos un bloque de autoevaluación, y este
    taller no lleva quiz: la evaluación ES el taller, y el banco de la
    defensa son preguntas orales. Llamarla daría MAL sobre un documento
    correcto. Lo que sí aplica —los plegables con `aria-expanded` y
    `aria-controls`, y los lienzos con `aria-label`— se comprueba aquí
    abajo y a mano.

  · `geomapas()` — solo sabe mirar un `.geomapa` cuya fuente sea un
    LITERAL. Los seis de este taller son FUNCIONES, porque dependen del
    documento del estudiante. No queda sin cubrir: `audita_taller2.py`
    audita los mapas contra el JSON. El coste está declarado igual en la
    cabecera de `ensambla_taller2.py` y en el §7.1 del plan.

  · `soluciones()` — el taller no tiene solucionario. Esa fue la decisión.

LO QUE SÍ COMPRUEBA, Y ES LO PROPIO DE UN TALLER: que la prosa YA
ENSAMBLADA no contenga ninguna respuesta. Hay TRES superficies distintas y
cada una la vigila alguien: `audita_taller2.py` mira el JSON,
`ensambla_taller2.py` mira su propia salida antes de escribirla, y este
mira el texto que el estudiante lee. Un despiste al redactar no lo caza
ninguno de los otros dos.

EL TOPE DE PESO, Y SU ARITMÉTICA

`TOPE_KB` de la casa vale 700 y este documento pesa más del doble, así que
tiene el suyo. No es una marca de agua levantada bajo presión: es una cota
con dos extremos, y los dos importan.

  · Por abajo, el tamaño de hoy: **1 141 KB**. De ellos, **698** son los
    dos JSON incrustados —el buscador los necesita enteros, M-11 del
    plan— y **266** el motor de la plantilla, así que la prosa propia del
    taller son unos **177 KB**. El tope tiene que quedar por encima o el
    documento no pasa su propia comprobación.

  · Por arriba, la ceguera del arnés: `prueba_texto.py` tumba esta
    comprobación inyectando **+312 KB** de comentario. Si el tope pasara
    de 1 141 + 312 = **1 453 KB**, la inyección ya no lo rebasaría y la
    comprobación se quedaría sin poder fallar — verde para siempre y
    valiendo nada.

  **1 250 KB** cae dentro de esa horquilla con margen por los dos lados:
  deja **109 KB** de crecimiento —más de la mitad de la prosa que hay hoy—
  y se queda **203 KB** por debajo del punto ciego. Si algún día el taller
  se acerca a 1 250, lo que hay que revisar es el número Y la inyección,
  no solo el número: subirlo por encima de 1 453 deja la comprobación
  verde para siempre.

Uso:  cd precalculo && python3 audita_texto_taller2.py
Devuelve 1 si algo falla. TALLER2_HTML apunta a una copia con defectos.
"""
from __future__ import annotations

import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from audita_texto_base import Auditor  # noqa: E402

# El tope propio. La aritmética que lo sostiene está en la cabecera, y no
# es adorno: el arnés comprueba que siga siendo rebasable.
TOPE_KB_TALLER2 = 1250.0

# Las cifras que son ESTRUCTURA del taller y no resultados: pesos, fechas,
# minutos y los rangos de las dos rúbricas. Ninguna sale del precálculo
# porque ninguna es una medición —son decisiones de diseño— y por eso se
# declaran una a una en vez de aflojar la comprobación.
ESTRUCTURALES = {
    # Los pesos: cinco tareas al 8 %, escrito 40 % y defensa 60 %.
    "8", "40", "60", "100",
    # Los tres bloques de la defensa y sus pesos dentro de ella.
    "30", "45", "25",
    # Los rangos de los cuatro niveles de las dos rúbricas. Van uno a uno
    # a propósito: son veinte celdas escritas a mano y una errata en
    # cualquiera de ellas es una rúbrica que no suma.
    "0", "3", "4", "6", "7", "9", "10", "13", "15", "16", "17", "18", "19",
    "20", "21", "22", "26", "27", "28", "29", "39",
    # Las fechas del calendario y los minutos de la navegación.
    "2026", "50",
    # El banco: 36 = 12 × 3, y las 12 afirmaciones falsas.
    "36",
    # La banda de la envolvente y el umbral de los p-valores.
    "95", "05",
    # El armazón que la plantilla pone en todas las páginas del curso: el
    # código de la asignatura y los años de las versiones de los CDN. No
    # son cifras del taller y ningún precálculo las respalda.
    "20929", "1993", "2013", "2014", "2015", "2019", "2023",
}

# Lo que la prosa del taller NO puede decir. Son las respuestas de T1, T2 y
# T3, y el motivo de que estén aquí es que la prosa y el JSON son dos
# superficies distintas: `audita_taller2.py` vigila la primera y este la
# segunda.
#
# La lista es la del ensamblador, y NO incluye «es aleatorio» ni «está
# agregado» sueltos: los dice el informe de T3 —que es material citado
# para refutar— y los dice el catálogo de refutaciones. Una guarda que
# salta con el castellano corriente se acaba desactivando entera.
PROHIBIDAS = [
    "familia del patrón",
    "tu patrón está agregado", "tu patrón es aleatorio", "tu patrón es regular",
    "el régimen de tu patrón",
    "la ventana correcta es", "la ventana buena es", "la ventana defectuosa es",
    "uno de cada familia", "una de cada familia", "uno de cada régimen",
    "el mapa a es el", "el mapa b es el", "el mapa c es el",
    "rthomas", "rssi", "rpoispp", "proceso de thomas",
]


def main() -> int:
    a = Auditor(capitulo="taller-2-cap-4.html", var_entorno="TALLER2_HTML",
                jsons=["taller2_datos.json"], estructurales=ESTRUCTURALES)

    a.cifras()

    a.temario([
        ("las reglas de uso de IA", "no hace falta pedir permiso"),
        ("la bitácora obligatoria", "bitácora"),
        ("la regla de recalificación en la defensa", "se recalifica"),
        ("el reparto escrito/defensa", "la sustentación oral"),
        ("el buscador de variante", "número de documento"),
        ("la línea que va literal en la portada", "copiada literal"),
        ("el dígito de verificación", "revisa antes de seguir"),
        ("el control de la semana 9", "cinco cosas"),
        ("T1 · las dos ventanas y el test de cuadrantes", "la ventana que no declaraste"),
        ("T1 · el supuesto de las esperanzas", "esperanza menor que 5"),
        ("T2 · el emparejamiento de curvas y mapas", "empareja"),
        ("T3 · el informe que hay que refutar", "lo produjo un modelo de lenguaje"),
        ("T4 · el borde y la forma de la ventana", "perímetro/área"),
        ("T4 · la banda y el tramo elegido después", "después de mirar"),
        ("T5 · los cuatro selectores de ancho", "cuatro selectores"),
        ("T5 · la definición de foco", "componente conexa"),
        ("la rúbrica del escrito", "rúbrica del escrito"),
        ("la rúbrica de la sustentación", "rúbrica de la sustentación"),
        ("el banco de la defensa", "banco de la defensa"),
        ("el catálogo de refutaciones", "afirmaciones falsas"),
        ("el sorteo sin reemplazo", "sin reemplazo"),
    ])

    print("\n=== Que la prosa no contenga ninguna respuesta ============")
    for frase in PROHIBIDAS:
        a.exige(frase not in a.texto_plano, f"la prosa no dice «{frase}»")

    # EL CALENDARIO, UNO SOLO. Se movió dos veces, y la segunda las fechas
    # estaban escritas a mano en cuatro sitios de la prosa: una copia que
    # se quedara atrás publicaba dos fechas de entrega en el mismo
    # enunciado. Las de aquí se escriben a mano A PROPÓSITO —son la segunda
    # superficie contra la que se coteja la constante del ensamblador— y
    # las viejas se prohíben todas, con el dígito aislado para que «6 de
    # octubre» no case dentro de «16 de octubre».
    print("\n=== El calendario, uno solo =============================")
    plano = re.sub(r"\s+", " ", a.texto_plano)
    for que, frase in [("la fecha de entrega", "domingo 11 de octubre de 2026"),
                       ("la hora límite", "a más tardar a las 13:00"),
                       ("la fecha de la sustentación", "martes 13 de octubre")]:
        a.exige(frase in plano, f"el enunciado da {que}")
    for vieja, patron in [("viernes 18", r"viernes 18\b"),
                          ("18 de septiembre", r"(?<!\d)18 de septiembre"),
                          ("martes 6", r"martes 6\b"),
                          ("6 de octubre", r"(?<!\d)6 de octubre"),
                          ("jueves 8", r"jueves 8\b"),
                          ("8 de octubre", r"(?<![\d])8 de octubre")]:
        a.exige(not re.search(patron, plano), f"no queda la fecha vieja «{vieja}»")

    # Y EL CONTROL, POR LA MISMA RAZÓN. «cinco cosas» en el temario solo
    # exige que aparezca UNA vez, y el enunciado lo dice en dos sitios. El
    # arnés inyectó «tres datos» en uno solo —el otro está partido en dos
    # líneas en el HTML y la sustitución literal no lo alcanzó— y esto pasó
    # en verde con el enunciado contradiciéndose: 22 de 23 el 2026-09-11.
    # Así que TODA frase que dice qué se trae al control dice cinco cosas.
    traes = re.findall(r"\btraes (\w+) (\w+)", plano)
    a.exige(bool(traes) and all(x == ("cinco", "cosas") for x in traes),
            "todo «traes…» del control dice «cinco cosas»")

    print("\n=== Lo que el taller no puede dejar de decir ==============")
    a.afirmaciones([
        ("dice que se puede usar IA sin pedir permiso", "no hace falta pedir permiso"),
        ("advierte de que sin bitácora la entrega está incompleta",
         "la entrega está incompleta"),
        ("dice que la regla de pertenencia es geométrica", "geométrica y no de atributo"),
        ("advierte de las dos colas de quadrat.test", "dos colas por defecto"),
        ("dice que un emparejamiento sin argumento no puntúa en T2",
         "sin argumento no puntúa"),
        ("declara que el orden de los mapas no es el de las curvas",
         "el orden no coincide"),
        ("dice que la dirección del sesgo ya se trabajó en el capítulo",
         "no se vuelve a preguntar aquí"),
        ("dice que «el que da bw.diggle» no puntúa sin decir qué optimiza",
         "no puntúa si no dices"),
        ("advierte de que el recuento de focos depende de la rejilla",
         "depende de la rejilla"),
        ("dice que las dos rúbricas se leen antes de escribir", "antes de escribir"),
        ("declara que ninguna pregunta del banco repite el capítulo",
         "ni un ejercicio guiado del capítulo"),
    ])

    # Las piezas de accesibilidad que SÍ aplican, a mano, porque la familia
    # entera no se puede llamar (ver la cabecera).
    print("\n=== Accesibilidad de lo que este documento sí tiene =======")
    botones = re.findall(r'<button[^>]*class="(?:derivacion|ejercicio)-boton"[^>]*>',
                         a.cuerpo)
    a.exige(bool(botones) and all("aria-expanded" in b and "aria-controls" in b
                                  for b in botones),
            "los plegables declaran aria-expanded y aria-controls",
            f"{len(botones)} botones")
    huerfanos = [m for b in botones
                 for m in re.findall(r'aria-controls="([^"]+)"', b)
                 if f'id="{m}"' not in a.cuerpo]
    a.exige(not huerfanos, "y cada uno apunta a un panel que existe", str(huerfanos))
    # Los ocho lienzos del marcado son los de las curvas —tres en T2, tres
    # en T3 y dos en T4—. Los de los mapas no están aquí: los fabrica
    # `.geomapa` al cargar el módulo, y su etiqueta se comprueba en el
    # navegador (C8).
    lienzos = re.findall(r"<canvas[^>]*>", a.cuerpo)
    a.exige(bool(lienzos) and all("aria-label" in c for c in lienzos),
            "los lienzos del marcado llevan aria-label",
            f"{len(lienzos)} lienzos")
    campos = re.findall(r"<input[^>]*>", a.cuerpo)
    a.exige(not campos or all("aria-label" in c or "id=" in c for c in campos),
            "los campos de formulario del marcado llevan etiqueta",
            f"{len(campos)} campos en el marcado (el del buscador lo crea el motor)")

    # Y lo que sostiene la sustentación entera: que la aritmética del §4.5
    # esté impresa donde el estudiante la lee. 36 = 12 × 3 no es un detalle
    # de organización, es lo que hace que a nadie le repitan una pregunta.
    print("\n=== La aritmética del sorteo, impresa donde se lee =========")
    filas_banco = len(re.findall(
        r'<tr><th scope="row">\d+</th><td>\d+</td><td>[^<]*</td><td>', a.cuerpo))
    filas_falsas = len(re.findall(
        r'<tr><th scope="row">\d+</th><td>\d+</td><td>[^<]*</td></tr>', a.cuerpo))
    a.exige(filas_banco == 36, "el banco publica sus 36 preguntas", f"{filas_banco} filas")
    a.exige(filas_falsas == 12, "y el catálogo sus 12 afirmaciones falsas",
            f"{filas_falsas} filas")
    a.exige("12 × 3" in a.prosa_txt, "y publica la aritmética que lo sostiene")

    a.enlaces()
    a.formulas_escapadas()
    a.codificacion()
    a.coherencia(
        cadenas=["λ", "²", "—", "«", "»", "ó", "í", "é", "ñ", "¿", "χ²",
                 "Ripley", "envolvente", "cuadrantes", "Bogotá", "tamaño"],
        ordenes=["\\(", "\\times"])
    a.peso(TOPE_KB_TALLER2)

    return a.cierre()


if __name__ == "__main__":
    sys.exit(main())
