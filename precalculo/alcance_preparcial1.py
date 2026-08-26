#!/usr/bin/env python3
"""
alcance_preparcial1.py — los 30 módulos que entran en el parcial del Corte I

Material de Estadística Espacial 2026-II (20929). P0.1 del
PLAN_Preparcial_Corte_1.md.

QUÉ ES Y POR QUÉ EXISTE

El parcial del 1 de septiembre evalúa los capítulos 1 y 2 completos y el
capítulo 3 **hasta el módulo 8**. Esa frontera aparece en tres sitios —el
módulo 1 del preparcial, que se la dice al estudiante; el generador, que
decide qué cifras precalcular; y el auditor, que prohíbe preguntas fuera de
ella— y escribirla tres veces es escribirla mal dos.

Aquí se declara una vez. Y **los títulos no se escriben**: se leen del
`courseData` de los capítulos publicados, que es la única copia que el
estudiante llega a ver.

LA FRONTERA NO SE CREE A SÍ MISMA

Un preparcial que dice «hasta MAUP I» y apunta al módulo 8 se vuelve falso en
silencio el día que alguien inserte un módulo en el capítulo 3: el 8 pasaría a
ser otra cosa y nada avisaría. Por eso el alcance no se conforma con contar
módulos: **ancla seis títulos** —los dos MAUP, las tres autoevaluaciones y el
módulo del error nº 1 de los LLM— y aborta si alguno no está donde dice.

Es la misma idea de las anclas de `genera_capN.R`, aplicada a la numeración en
vez de a las cifras.

Uso:
    python3 precalculo/alcance_preparcial1.py        # imprime la tabla
    import alcance_preparcial1 as a; a.ALCANCE       # las 30 entradas
"""
from __future__ import annotations

import pathlib
import re
import sys

RAIZ = pathlib.Path(__file__).resolve().parent.parent
HTMLS = RAIZ / "Htmls_Espacial"

# Los tres capítulos que evalúa el parcial, con el archivo que los publica.
DOCS = {
    "cap1": "capitulo-1-datos-espaciales.html",
    "cap2": "capitulo-2-crs-georreferenciacion.html",
    "cap3": "capitulo-3-cartografia-maup.html",
}

# Los módulos evaluables. Los m12 de los capítulos 1 y 2 quedan fuera porque
# son la autoevaluación del capítulo, no contenido; el capítulo 3 se corta en
# el 8 por decisión de Javier (D1 del plan), no por casualidad.
EVALUABLES = {
    "cap1": range(1, 12),
    "cap2": range(1, 12),
    "cap3": range(1, 9),
}

# Lo que el módulo 1 del preparcial tiene que nombrar como «no entra». Un
# estudiante no adivina una frontera: hay que dibujársela con los títulos que
# ve en el capítulo.
FUERA = {"cap3": [9, 10, 11]}

# Las anclas de numeración. Si un título deja de contener su fragmento, algo se
# renumeró y este archivo para en vez de mentir. El fragmento se compara en
# minúsculas y sin exigir tildes exactas más allá de lo que ya trae el HTML.
ANCLAS_TITULO = {
    ("cap1", 12): "autoevaluación",
    ("cap2", 5): "reetiquetar",
    ("cap2", 12): "autoevaluación",
    ("cap3", 8): "maup i",
    ("cap3", 9): "maup ii",
    ("cap3", 12): "autoevaluación",
}

_RE_MODULO = re.compile(r'\{\s*id:\s*(\d+)\s*,\s*title:\s*"((?:[^"\\]|\\.)*)"')


def _para(mensaje: str) -> None:
    sys.exit(f"PARADO · alcance_preparcial1: {mensaje}")


def _html(doc: str) -> str:
    ruta = HTMLS / DOCS[doc]
    if not ruta.exists():
        _para(f"falta el capítulo publicado {ruta.relative_to(RAIZ)}")
    return ruta.read_text(encoding="utf-8")


def modulos(doc: str) -> list[dict]:
    """Los módulos de un capítulo, leídos de su `courseData`.

    No se parsea el archivo entero: solo el bloque entre `const courseData` y
    su cierre. Fuera de ahí hay comentarios del motor que escriben `id:` y
    `title:` de ejemplo, y contarlos daba módulos que no existen.
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
    esperados = list(range(1, len(encontrados) + 1))
    if [m["id"] for m in encontrados] != esperados:
        _para(f"{DOCS[doc]} no numera sus módulos 1..N: "
              f"{[m['id'] for m in encontrados]}")
    for m in encontrados:
        if not m["titulo"].strip():
            _para(f"{DOCS[doc]} módulo {m['id']} sin título")
    return encontrados


def texto_modulo(doc: str, n: int) -> str:
    """El marcado del `<template id="module-n">` de un capítulo publicado.

    Lo necesita el auditor: una pregunta que manda repasar el módulo 5 del
    capítulo 2 tiene que citar una cifra que **esté** en ese módulo, no en
    otro. Sin esto, la columna `repaso` sería una etiqueta sin contrastar.
    """
    h = _html(doc)
    m = re.search(rf'<template id="module-{n}"[^>]*>(.*?)</template>', h, re.S)
    if not m:
        _para(f"{DOCS[doc]} no tiene `<template id=\"module-{n}\">`")
    return m.group(1)


def _comprueba_anclas(doc: str, mods: list[dict]) -> None:
    """Las seis anclas de numeración, comprobadas UNA A UNA.

    Recorrer los módulos y mirar si alguno tiene ancla parece lo mismo y no lo
    es: un ancla sobre un módulo que **desaparece** no falla, deja de
    existir. Se vio inyectando la mutilación del glosario en el capítulo 1: al
    quitar su m11 la autoevaluación pasó a ser el 11, el ancla del 12 no se
    comprobó porque ya no había módulo 12, y el alcance se tragó la
    autoevaluación del capítulo como contenido evaluable, con los 30 módulos
    cuadrando y sin una palabra.

    Así que se itera sobre las ANCLAS, no sobre los módulos: que el módulo
    anclado exista es parte de lo que el ancla afirma.
    """
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
        pedidos = list(EVALUABLES[doc])
        if len(mods) < max(pedidos):
            _para(f"{archivo} publica {len(mods)} módulos y el alcance pide "
                  f"hasta el {max(pedidos)}")
        _comprueba_anclas(doc, mods)
        for m in mods:
            fila = {"doc": doc, "modulo": m["id"], "titulo": m["titulo"],
                    "archivo": archivo, "ancla": f"{archivo}#m{m['id']}"}
            if m["id"] in pedidos:
                dentro.append(fila)
            elif m["id"] in FUERA.get(doc, []):
                afuera.append(fila)
    if len(dentro) != 30:
        _para(f"el alcance da {len(dentro)} módulos y el plan dice 30")
    return dentro, afuera


ALCANCE, FUERA_DE_ALCANCE = _construye()
CLAVES = {f"{f['doc']}.m{f['modulo']}" for f in ALCANCE}


def en_alcance(doc: str, modulo: int) -> bool:
    return f"{doc}.m{modulo}" in CLAVES


def main() -> None:
    print(f"ALCANCE DEL PREPARCIAL · {len(ALCANCE)} módulos evaluables\n")
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
    print(f"\n  {len(ANCLAS_TITULO)} anclas de numeración comprobadas, "
          "ninguna rota.")


if __name__ == "__main__":
    main()
