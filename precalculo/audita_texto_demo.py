#!/usr/bin/env python3
"""
audita_texto_demo.py — auditor de prosa del capítulo-banco de pruebas

Material de Estadística Espacial 2026-II (20929). T0.5.

Este archivo es DOS cosas a la vez:

  1. El auditor del fixture `prueba-auditoria.html`, que es lo que
     `prueba_texto.py` somete al arnés de inyección.
  2. **El molde de `audita_texto_capN.py`.** Cuando llegue el capítulo 1,
     se copia esto, se cambian las listas y se acabó: toda la maquinaria
     está en `audita_texto_base.py`.

Fíjate en lo corto que es. Ése es el punto: en Diseño de Experimentos
cada auditor son entre 370 y 677 líneas, y por eso un fallo del núcleo
—las fórmulas de KaTeX retiradas antes de extraer los números— sobrevivió
en cinco de ellos a la vez.

Uso:  python3 precalculo/audita_texto_demo.py
Devuelve 1 si algo falla.
"""
from __future__ import annotations

import sys

from audita_texto_base import Auditor

# Cifras que NO son resultados y no tienen por qué estar en el
# precálculo: identificadores, años, códigos y páginas.
ESTRUCTURALES = {
    "20929",                       # el código de la asignatura
    "2026", "2023", "2013", "2015", "2014", "1993", "2011", "2019",
    "1991", "2020", "1988", "1950",
    "9377", "4326", "3857", "3116",   # códigos EPSG
    "1.2", "4.4", "0.05", "0.01", "95", "90", "99",
    "12.25", "1000", "1 000",
    # Versiones de licencia y códigos de tarea. Son cifras de UN decimal, y
    # `mide_punto_ciego.py` las señalaba como «peor protegidas» — con razón,
    # pero sin sentido: nadie audita el «4.0» de CC BY 4.0. Declararlas
    # estructurales las saca de la medición y deja el número limpio.
    "4.0",            # CC BY 4.0, CC BY-SA 4.0, CC BY-NC-ND 4.0
    "0.5", "0.2", "0.3", "0.4",   # T0.5, T0.2… los códigos de tarea del plan
}

DEBE_CUBRIR = [
    ("el efecto escala del MAUP", "efecto escala"),
    ("el índice de Moran", "moran"),
    ("la hipótesis nula del índice", "hipótesis nula"),
    ("la contigüidad reina", "reina"),
    ("la contigüidad torre", "torre"),
    ("las islas y zero.policy", "zero.policy"),
    ("los subgrafos de la vecindad", "subgrafos"),
    ("la ventana de observación", "ventana"),
    ("la intensidad de un patrón puntual", "intensidad"),
    ("la clasificación por cuantiles", "cuantiles"),
    ("Fisher-Jenks", "fisher-jenks"),
    ("el lado cerrado del intervalo", "lado cerrado"),
    ("el gradiente térmico", "gradiente"),
    ("la diferencia entre errata y discrepancia", "discrepancia"),
    ("que heterogeneidad no es autocorrelación", "heterogeneidad"),
]

# Tokens largos a propósito: buscar «men» daría OK dentro de «momento» y
# la comprobación pasaría siempre. Una comprobación que no puede fallar
# no comprueba nada.
FUENTES = [
    "pebesma", "bivand", "baddeley", "anselin", "cressie",
    "ideam", "marco geoestadístico nacional", "geoboundaries",
    "ministerio de educación nacional", "secretaría de educación del distrito",
]

AFIRMACIONES = [
    ("dice que la unidad de análisis es una decisión, no una presentación",
     "decisión de modelado"),
    ("dice que la ventana forma parte del estimador",
     "parte del estimador"),
    ("advierte de que un cut ingenuo en R devuelve la respuesta de Python",
     "la respuesta de python"),
    ("dice que una discrepancia no es un error de nadie",
     "no es un error de nadie"),
    ("declara que los cortes los calcula R y no el navegador",
     "los calculó r"),
]

# Si el locale se rompe, las tildes no desaparecen: se convierten en otra
# cosa. La comprobación útil es exigir cadenas CONCRETAS intactas —las que
# este capítulo usa de verdad—, no una lista de símbolos aspiracional: un
# «σ» que el capítulo no escribe daría MAL siempre y acabaría enseñando a
# ignorar el informe. Los capítulos 8 y 9 añadirán σ y ρ cuando los usen.
CADENAS = [
    "λ", "γ", "−", "×", "²", "≥",
    "ó", "í", "é", "ñ", "ü",
    "Deserción", "autocorrelación", "contigüidad", "cuantiles",
]

ORDENES = [r"\frac", r"\lambda", r"\hat", r"\sum", r"\text"]


def main() -> int:
    a = Auditor(
        capitulo="prueba-auditoria.html",
        var_entorno="DEMO_HTML",
        jsons=["demo_auditoria.json"],
        estructurales=ESTRUCTURALES,
        presupuesto_geomapa_kb=120.0,
    )
    print(f"\n=== audita_texto_demo.py · {a.ruta.name} ===")
    a.cifras()
    a.temario(DEBE_CUBRIR)
    a.fuentes(FUENTES)
    a.afirmaciones(AFIRMACIONES)
    a.accesibilidad()
    a.geomapas()
    a.formulas_escapadas()
    a.codificacion()
    a.enlaces()
    a.coherencia(CADENAS, ORDENES)
    a.peso(550)   # propio, y más bajo: el fixture pesa la mitad
    return a.cierre()


if __name__ == "__main__":
    sys.exit(main())
