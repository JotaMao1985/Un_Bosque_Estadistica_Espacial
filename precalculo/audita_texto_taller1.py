#!/usr/bin/env python3
"""
audita_texto_taller1.py — las cifras de la prosa del Taller 1 (C8)

Material de Estadística Espacial 2026-II (20929). Ver PLAN_Taller_1_Caps_1_2.md.

Mismo núcleo que los auditores de prosa de los capítulos —`audita_texto_base`—
y por la misma razón: la maquinaria vive una vez, cada documento declara
QUÉ hay que comprobar. Ver la cabecera de ese archivo para el porqué.

QUÉ CAMBIA EN UN TALLER, Y POR QUÉ NO SE LLAMAN TODAS LAS FAMILIAS

Un taller no es un capítulo, y forzarlo a pasar las comprobaciones de uno
sería peor que no hacerlas: se aprueban por vacuidad y el informe queda
verde sobre algo que nadie miró. Se declara aquí qué NO se llama:

  · `accesibilidad()` — exige al menos un `<canvas>` con `aria-label` y al
    menos un bloque de autoevaluación. El taller no lleva quiz —la
    evaluación ES el taller— y su único lienzo lo fabrica `.geomapa` en
    tiempo de ejecución, así que en el marcado no hay ninguno. Llamarla
    daría MAL sobre un documento correcto. Lo que sí se comprueba, aquí
    abajo y a mano, son las dos piezas que sí aplican: que los plegables
    lleven `aria-expanded`/`aria-controls` y que apunten a algo que exista.

  · `geomapas()` — solo sabe mirar un `.geomapa` cuya fuente sea un
    LITERAL. La del taller es una función, porque el mapa depende del
    documento del estudiante. No queda sin cubrir: `audita_taller1.py`
    audita los 30 mapas contra el JSON, uno por uno.

  · `soluciones()` — el taller no tiene solucionario. Esa fue la decisión.

LO QUE SÍ COMPRUEBA, Y ES LO PROPIO DE UN TALLER: que la prosa YA
ENSAMBLADA no contenga ninguna respuesta. `audita_taller1.py` lo vigila
sobre el JSON; aquí se vigila sobre el texto que el estudiante lee.

Uso:  cd precalculo && python3 audita_texto_taller1.py
Devuelve 1 si algo falla. TALLER1_HTML apunta a una copia con defectos.
"""
from __future__ import annotations

import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from audita_texto_base import Auditor  # noqa: E402

# Las cifras que son ESTRUCTURA del taller y no resultados: pesos de las
# tareas, reparto escrito/defensa, los cuatro EPSG y los rangos de la
# rúbrica. Ninguna sale del precálculo porque ninguna es una medición —son
# decisiones de diseño— y por eso se declaran una a una en vez de aflojar
# la comprobación.
ESTRUCTURALES = {
    # Pesos de T1..T7 y el reparto escrito/defensa.
    "10", "15", "20", "40", "60", "100",
    # Los cuatro sistemas de referencia que T4 compara.
    "4326", "3857", "3116", "9377",
    # Los rangos de los cuatro niveles de la rúbrica.
    "0", "2", "3", "5", "6", "7", "8", "9", "11", "12", "14", "17", "18", "21",
    "22", "25",
    # Minutos declarados en la navegación y en la defensa.
    "35", "45",
    # El radio de la esfera de s2 sale del JSON, pero con separador fino.
    "6371010",
    # El armazón que la plantilla pone en todas las páginas del curso: el
    # código de la asignatura y los años de las versiones de los CDN. No
    # son cifras del taller y ningún precálculo las respalda.
    "20929", "1993", "2013", "2014", "2015", "2019", "2023",
}

# Lo que la prosa del taller NO puede decir. Son las respuestas de T1 y de
# T3, y el motivo de que estén aquí es que el JSON y la prosa son dos
# superficies distintas: `audita_taller1.py` vigila la primera y este la
# segunda. Un despiste al redactar no lo caza el otro.
PROHIBIDAS = [
    "el correcto es", "el defectuoso es", "está acumulado", "es el acumulado",
    "la familia de tu patrón", "tu patrón es agregado", "tu patrón es regular",
    "el resultado a es el bueno", "el resultado b es el bueno",
]


def main() -> int:
    a = Auditor(capitulo="taller-1-caps-1-2.html", var_entorno="TALLER1_HTML",
                jsons=["taller1_datos.json"], estructurales=ESTRUCTURALES)

    a.cifras()

    a.temario([
        ("las reglas de uso de IA", "declara al final qué consultaste"),
        ("la regla de recalificación en la defensa", "se recalifica"),
        ("el reparto escrito/defensa", "el escrito vale el"),
        ("el buscador de variante", "escribe los"),
        ("el dígito de verificación", "dígito de verificación"),
        ("T1 · el índice de Clark-Evans", "clark-evans"),
        ("T2 · el intervalo y el n efectivo", "n_{\\text{eff}}"),
        ("T3 · los dos correlogramas", "uno de los dos está mal"),
        ("T4 · los cuatro sistemas", "9377"),
        ("T5 · set_crs contra transform", "st_set_crs"),
        ("T6 · la validación cruzada por bloques", "bloques geográficos"),
        ("T7 · auditar la respuesta de un modelo", "esto fue lo que contestó"),
        ("la rúbrica", "cómo se califica"),
        ("el banco de la defensa", "banco de la defensa"),
    ])

    print("\n=== Que la prosa no contenga ninguna respuesta ============")
    for frase in PROHIBIDAS:
        a.exige(frase not in a.texto_plano, f"la prosa no dice «{frase}»")

    print("\n=== Lo que el taller no puede dejar de decir ==============")
    a.afirmaciones([
        ("dice que se puede usar IA sin pedir permiso", "no hace falta pedir permiso"),
        ("advierte de que la evidencia de T3 tiene que ser interna",
         "interna a la tabla"),
        ("dice que «es el oficial de Colombia» no puntúa en T4",
         "no puntúa"),
        ("advierte de que un veredicto sin evidencia no puntúa en T7",
         "sin evidencia no puntúa"),
        ("dice que la rúbrica se lee antes de escribir", "antes de escribir"),
    ])

    # Las dos piezas de accesibilidad que SÍ aplican, a mano, porque la
    # familia entera no se puede llamar (ver la cabecera).
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
    campos = re.findall(r"<input[^>]*>", a.cuerpo)
    a.exige(not campos or all("aria-label" in c or "id=" in c for c in campos),
            "los campos de formulario del marcado llevan etiqueta",
            f"{len(campos)} campos en el marcado (el del buscador lo crea el motor)")

    a.enlaces()
    a.formulas_escapadas()
    a.codificacion()
    a.coherencia(
        cadenas=["λ", "²", "±", "—", "«", "»", "ó", "í", "é", "ñ", "¿",
                 "Clark-Evans", "correlograma", "georreferenciación", "Bogotá"],
        ordenes=["\\lambda", "\\sqrt", "\\text", "\\bar"])
    a.peso()

    return a.cierre()


if __name__ == "__main__":
    sys.exit(main())
