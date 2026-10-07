#!/usr/bin/env python3
"""
alcance_preparcial2.py — los 22 módulos que entran en el parcial del Corte II

Material de Estadística Espacial 2026-II (20929). P0.1 del
PLAN_Preparcial_Corte_2.md.

QUÉ ES Y POR QUÉ EXISTE

El Parcial 2 evalúa los capítulos 4 y 5, **módulos 1 a 11** de cada uno (D1
del plan). Los módulos 12 y 13 de los dos no son contenido: el 12 es la
autoevaluación y el 13 el simulacro del quiz. Esa frontera aparece en tres
sitios —el módulo 1 del preparcial, que se la dice al estudiante; el
generador, que decide qué cifras referenciar; y el auditor, que prohíbe
preguntas fuera de ella— y escribirla tres veces es escribirla mal dos.

Aquí se declara una vez, y **los títulos no se escriben**: se leen del
`courseData` de los capítulos publicados, que es la única copia que el
estudiante llega a ver. Es `alcance_preparcial1.py` con otros dos capítulos.

LA FRONTERA NO SE CREE A SÍ MISMA

Diez anclas de título —las dos autoevaluaciones, los dos simulacros y seis
módulos de contenido repartidos por los dos capítulos— y el número total de
módulos de cada uno. Lo segundo es nuevo respecto del Corte I y tiene un
motivo concreto: el capítulo 5 ganó su módulo 13 (el simulacro) después de
escribirse su plan, y un módulo que se añade AL FINAL no rompe ninguna ancla
de las de arriba. El alcance seguiría diciendo «22» y el módulo 1 del
preparcial no nombraría al nuevo entre los que quedan fuera.

Uso:
    python3 precalculo/alcance_preparcial2.py        # imprime la tabla
    import alcance_preparcial2 as a; a.ALCANCE       # las 22 entradas
"""
from __future__ import annotations

import pathlib
import re
import sys

RAIZ = pathlib.Path(__file__).resolve().parent.parent
HTMLS = RAIZ / "Htmls_Espacial"

# Los dos capítulos que evalúa el parcial, con el archivo que los publica.
DOCS = {
    "cap4": "capitulo-4-patrones-puntuales.html",
    "cap5": "capitulo-5-intensidad-nucleos.html",
}

# Los módulos evaluables: del 1 al 11 en los dos (D1 del plan).
EVALUABLES = {
    "cap4": range(1, 12),
    "cap5": range(1, 12),
}

# Lo que el módulo 1 del preparcial tiene que nombrar como «no entra».
FUERA = {"cap4": [12, 13], "cap5": [12, 13]}

# Cuántos módulos publica cada capítulo cuando se escribió el alcance. Si
# cambia, la frontera hay que volver a pensarla, no a contarla.
N_MODULOS = {"cap4": 13, "cap5": 13}

# Las anclas de numeración: un fragmento del título, en minúsculas.
ANCLAS_TITULO = {
    ("cap4", 7): "funciones g y f",
    ("cap4", 8): "función k",
    ("cap4", 11): "envolventes",
    ("cap4", 12): "autoevaluación",
    ("cap4", 13): "simulacro",
    ("cap5", 4): "borde",
    ("cap5", 9): "ppm",
    ("cap5", 11): "conglomerado",
    ("cap5", 12): "autoevaluación",
    ("cap5", 13): "simulacro",
}

N_ALCANCE = 22

_RE_MODULO = re.compile(r'\{\s*id:\s*(\d+)\s*,\s*title:\s*"((?:[^"\\]|\\.)*)"')


def _para(mensaje: str) -> None:
    sys.exit(f"PARADO · alcance_preparcial2: {mensaje}")


def _html(doc: str) -> str:
    ruta = HTMLS / DOCS[doc]
    if not ruta.exists():
        _para(f"falta el capítulo publicado {ruta.name}")
    return ruta.read_text(encoding="utf-8")


def modulos(doc: str) -> list[dict]:
    """Los módulos de un capítulo, leídos de su `courseData`.

    Solo el bloque entre `const courseData` y su cierre: fuera de ahí hay
    comentarios del motor que escriben `id:` y `title:` de ejemplo.
    """
    h = _html(doc)
    i = h.find("const courseData")
    if i < 0:
        _para(f"{DOCS[doc]} no declara `courseData`")
    j = h.find("};", i)
    bloque = h[i:j]
    encontrados = [{"id": int(n), "titulo": t} for n, t in _RE_MODULO.findall(bloque)]
    if not encontrados:
        _para(f"{DOCS[doc]} declara `courseData` sin módulos legibles")
    if [m["id"] for m in encontrados] != list(range(1, len(encontrados) + 1)):
        _para(f"{DOCS[doc]} no numera sus módulos 1..N: "
              f"{[m['id'] for m in encontrados]}")
    for m in encontrados:
        if not m["titulo"].strip():
            _para(f"{DOCS[doc]} módulo {m['id']} sin título")
    return encontrados


def texto_modulo(doc: str, n: int) -> str:
    """El marcado del `<template id="module-n">` de un capítulo publicado.

    Lo necesita el auditor: una pregunta que manda repasar un módulo tiene
    que poder contrastarse contra lo que ese módulo dice de verdad.
    """
    h = _html(doc)
    m = re.search(rf'<template id="module-{n}"[^>]*>(.*?)</template>', h, re.S)
    if not m:
        _para(f"{DOCS[doc]} no tiene `<template id=\"module-{n}\">`")
    return m.group(1)


def _comprueba_anclas(doc: str, mods: list[dict]) -> None:
    """Las anclas, comprobadas UNA A UNA y recorriendo las anclas, no los
    módulos: un ancla sobre un módulo que desaparece no falla, deja de
    existir (lo aprendió el arnés del Corte I, inyección 2)."""
    por_id = {m["id"]: m["titulo"] for m in mods}
    for (d, n), fragmento in ANCLAS_TITULO.items():
        if d != doc:
            continue
        if n not in por_id:
            _para(f"ANCLA ROTA · {doc} ya no tiene módulo {n}, y ahí vivía "
                  f"«{fragmento}». El capítulo se renumeró: la frontera del "
                  "temario ya no es la que dice el plan")
        if fragmento not in por_id[n].lower():
            _para(f"ANCLA ROTA · {doc} módulo {n} se llama «{por_id[n]}» y "
                  f"tenía que contener «{fragmento}». Algo se renumeró: la "
                  "frontera del temario ya no es la que dice el plan")


def _construye() -> tuple[list[dict], list[dict]]:
    dentro: list[dict] = []
    afuera: list[dict] = []
    for doc, archivo in DOCS.items():
        mods = modulos(doc)
        if len(mods) != N_MODULOS[doc]:
            _para(f"{archivo} publica {len(mods)} módulos y el alcance se "
                  f"escribió sobre {N_MODULOS[doc]}: lo que queda fuera ya no "
                  "es lo que el módulo 1 del preparcial dice")
        _comprueba_anclas(doc, mods)
        pedidos = list(EVALUABLES[doc])
        for m in mods:
            fila = {"doc": doc, "modulo": m["id"], "titulo": m["titulo"],
                    "archivo": archivo, "ancla": f"{archivo}#m{m['id']}"}
            if m["id"] in pedidos:
                dentro.append(fila)
            elif m["id"] in FUERA.get(doc, []):
                afuera.append(fila)
            else:
                _para(f"{archivo} módulo {m['id']} no está ni dentro ni fuera "
                      "del alcance")
    if len(dentro) != N_ALCANCE:
        _para(f"el alcance da {len(dentro)} módulos y el plan dice {N_ALCANCE}")
    return dentro, afuera


ALCANCE, FUERA_DE_ALCANCE = _construye()
CLAVES = {f"{f['doc']}.m{f['modulo']}" for f in ALCANCE}


def en_alcance(doc: str, modulo: int) -> bool:
    return f"{doc}.m{modulo}" in CLAVES


def main() -> None:
    print(f"ALCANCE DEL PREPARCIAL DEL CORTE II · {len(ALCANCE)} módulos evaluables\n")
    actual = None
    for f in ALCANCE:
        if f["doc"] != actual:
            actual = f["doc"]
            print(f"  {actual} · {DOCS[actual]}")
        print(f"    m{f['modulo']:<3} {f['titulo']}")
    print(f"\nFUERA DEL PARCIAL · {len(FUERA_DE_ALCANCE)} módulos "
          "que el módulo 1 tiene que nombrar\n")
    for f in FUERA_DE_ALCANCE:
        print(f"    {f['doc']} m{f['modulo']:<3} {f['titulo']}")
    print(f"\n  {len(ANCLAS_TITULO)} anclas de numeración y "
          f"{len(N_MODULOS)} recuentos de módulos comprobados, ninguno roto.")


if __name__ == "__main__":
    main()
