#!/usr/bin/env python3
"""
cuenta_sitio.py — cuenta lo que hay DE VERDAD en los capítulos

Material de Estadística Espacial 2026-II (20929). Portado de Muestreo en T0.5.

Los totales del `index.html` y del README se escriben a mano en las fases
finales, y este proyecto ya sabe cómo acaba eso. Esta herramienta los
cuenta sobre los propios archivos publicados. Los objetivos del §8 del
plan —10 capítulos, 120 módulos, ~99 simuladores, ~35 mapas, 80 preguntas,
40 ejercicios— se contrastan contra esta salida, no contra la memoria.

Cambios respecto a la versión de Muestreo:

  · Cuenta los **`.geomapa`**, que allí no existían y aquí son ~35 del
    objetivo, con su desglose por modo. Un capítulo que prometa un mapa
    en modo `grafo` y no lo tenga se ve aquí.
  · Separa los **capítulos** de los **bancos de prueba** (`prueba-*.html`):
    el fixture de T0.5 y el del `.geomapa` no son material del curso y
    sumarlos a los totales sería inflarlos.
  · Cuenta las líneas `#>`, que son las cifras que `verifica_bloques.py`
    contrasta: un capítulo con muchos bloques y pocos `#>` está
    publicando código que nadie comprueba.

    python3 precalculo/cuenta_sitio.py
"""
from __future__ import annotations

import re
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
CARPETAS = [RAIZ / "sitio" / "estadistica-espacial", RAIZ / "Htmls_Espacial"]

CAMPOS = [
    ("módulos",     lambda h, m: h.count('<template id="module-')),
    ("simulad.",    lambda h, m: len(re.findall(r"\n    SIMULADORES\['", h))),
    ("geomapas",    lambda h, m: len(re.findall(r'data-geomapa="', m))),
    ("t-ranking",   lambda h, m: len(re.findall(r"\n    TABLAS_RANKING\['", h))),
    ("preguntas",   lambda h, m: len(re.findall(r"\n        tipo: ", h))),
    ("ejercicios",  lambda h, m: m.count('class="ejercicio-guiado"')),
    ("bloq. R",     lambda h, m: len(re.findall(r'class="language-r"', h))),
    ("bloq. Py",    lambda h, m: len(re.findall(r'class="language-python"', h))),
    # Las DOS formas: los bloques de R escriben `#&gt;` escapado y los de
    # Python `#>` a pelo. Contar solo una daba 14 donde hay 26, y un
    # contador que informa de menos es tan inútil como uno que informa de
    # más: los totales del §8 del plan se cuentan, no se recuerdan.
    ("cifras #>",   lambda h, m: len(re.findall(r"#&gt;", h)) + len(re.findall(r"#>", h))),
]
COMPONENTES = [
    ("glosario", 'data-glosario="'),
    ("rúbrica",  'data-rubrica="'),
    # El árbol no se cablea con `data-arbol`: vive DENTRO de un simulador
    # como `<div class="arbol">`, que es como lo estrenó el capítulo 4 de
    # Diseño de Experimentos. Buscando el atributo, el contador informaba
    # 0 árboles sobre un capítulo que tiene uno.
    ("árbol",    'class="arbol"'),
    ("ciclo",    'data-ciclo="'),
    ("diagrama", 'data-diagrama="'),
]
MODOS = ["poligonos", "puntos", "grafo", "rejilla", "proyeccion"]


def marcado(h: str) -> str:
    """Solo lo que hay DENTRO de los <template> de los módulos.

    El comentario de documentación de cada motor escribe también
    `data-x="id"`, y contarlo duplicaba el total. Es la corrección que ya
    llevaba la versión de Muestreo, y se conserva por el mismo motivo.
    """
    return "".join(re.findall(r'<template id="module-.*?</template>', h, re.S))


def tabla(titulo: str, rutas: list[Path]) -> list[int]:
    cab = ["archivo"] + [n for n, _ in CAMPOS] + [n for n, _ in COMPONENTES]
    anchos = [22] + [max(len(n), 9) for n in cab[1:]]
    print(f"\n{titulo}")
    print("  ".join(c.rjust(a) for c, a in zip(cab, anchos)))
    totales = [0] * (len(CAMPOS) + len(COMPONENTES))
    for p in rutas:
        h = p.read_text(encoding="utf-8")
        m = marcado(h)
        vals = [f(h, m) for _, f in CAMPOS] + [m.count(c) for _, c in COMPONENTES]
        totales = [t + v for t, v in zip(totales, vals)]
        etiqueta = p.stem[:22]
        print("  ".join(x.rjust(a) for x, a in
                        zip([etiqueta] + [str(v) for v in vals], anchos)))
    print("  ".join(x.rjust(a) for x, a in
                    zip(["TOTAL"] + [str(t) for t in totales], anchos)))
    kb = sum(p.stat().st_size for p in rutas) / 1024
    print(f"  {len(rutas)} archivo(s) · {kb:.0f} KB"
          + (f" · {kb/len(rutas):.0f} KB de media" if rutas else ""))
    return totales


def main() -> None:
    carpeta = next((d for d in CARPETAS if d.exists() and any(d.glob("*.html"))), None)
    if carpeta is None:
        raise SystemExit(f"ABORTA: no hay .html en {[str(d) for d in CARPETAS]}")
    print(f"Fuente: {carpeta.relative_to(RAIZ)}")

    caps = sorted(carpeta.glob("capitulo-*.html"))
    bancos = sorted(carpeta.glob("prueba-*.html"))

    if caps:
        t = tabla("CAPÍTULOS DEL CURSO", caps)
        # Los objetivos del §8 del plan, para ver la distancia sin
        # tener que ir a buscarlos.
        objetivos = {"módulos": 120, "simulad.": 99, "geomapas": 35,
                     "preguntas": 80, "ejercicios": 40}
        print("\n  Contra los objetivos del §8 del plan:")
        for (nombre, _), valor in zip(CAMPOS, t):
            if nombre in objetivos:
                o = objetivos[nombre]
                print(f"    {nombre:<12} {valor:>4} de {o:>4}  ({100*valor/o:.0f} %)")
    else:
        print("\nCAPÍTULOS DEL CURSO: todavía ninguno "
              "(la Fase 1 escribe el primero).")

    if bancos:
        tabla("BANCOS DE PRUEBA (no son material del curso)", bancos)

    # Desglose de los modos del .geomapa: el §4 del plan reparte los cinco
    # entre los capítulos, y así se ve cuáles siguen sin estrenarse.
    #
    # Se cuenta el `"modo"` del JSON incrustado, NO el `data-geomapa="…"`:
    # el identificador del contenedor puede llamarse como quiera, y en el
    # capítulo de prueba del .geomapa coincide con el modo solo por
    # casualidad. Contar por el nombre del contenedor habría dado una
    # tabla que parece correcta y no mide lo que dice medir.
    print("\n  Modos del .geomapa en uso (leídos del JSON incrustado):")
    textos = [p.read_text(encoding="utf-8") for p in caps + bancos]
    for modo in MODOS:
        n = sum(len(re.findall(r'"modo":\s*"' + modo + '"', t)) for t in textos)
        print(f"    {modo:<12} {n}")


if __name__ == "__main__":
    main()
