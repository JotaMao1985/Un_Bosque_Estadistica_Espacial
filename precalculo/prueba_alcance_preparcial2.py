#!/usr/bin/env python3
"""
prueba_alcance_preparcial2.py — le inyecta defectos al alcance del preparcial
del Corte II

Material de Estadística Espacial 2026-II (20929). P0.1 del
PLAN_Preparcial_Corte_2.md. Calcado de `prueba_alcance_preparcial1.py`, y por
la misma razón: lo que el alcance afirma es una NUMERACIÓN, y una numeración
se rompe callada —los módulos siguen yendo del 1 al N y siguen teniendo
título—.

Dos inyecciones son propias de este documento:

  · **un módulo 14 añadido al final del capítulo 5.** No mueve ninguna de las
    diez anclas —todas viven en el 13 o antes— y el alcance seguiría diciendo
    22. Es exactamente lo que pasó con el simulacro del quiz, que llegó al
    capítulo después de su plan. Lo caza el recuento de módulos.
  · **la autoevaluación del capítulo 4 sube al 11** al quitarle uno de
    contenido. Es la inyección 2 del Corte I trasladada: el ancla del 12 deja
    de existir en vez de fallar si se comprueba recorriendo los módulos.

Trabaja sobre copias en un directorio temporal. Nunca toca lo publicado.

Uso:  python3 precalculo/prueba_alcance_preparcial2.py
"""
from __future__ import annotations

import pathlib
import re
import shutil
import sys
import tempfile

RAIZ = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "precalculo"))
import alcance_preparcial2 as A  # noqa: E402

CAP4 = A.DOCS["cap4"]
CAP5 = A.DOCS["cap5"]


def _titulo(s: str, n: int) -> str:
    m = re.search(rf'\{{ id: {n}, title: "((?:[^"\\]|\\.)*)"', s)
    if not m:
        raise SystemExit(f"la inyección no encuentra el módulo {n}")
    return m.group(1)


def renombrar(n: int, nuevo: str):
    def f(s: str) -> str:
        viejo = _titulo(s, n)
        return s.replace(f'{{ id: {n}, title: "{viejo}"',
                         f'{{ id: {n}, title: "{nuevo}"', 1)
    return f


def quitar_g_y_f(s: str) -> str:
    """Quita el m7 del cap. 4, corre todos los siguientes uno hacia arriba y
    añade un 13 al final para que el capítulo siga teniendo trece módulos.

    Sin el 13 de relleno la para el recuento de módulos antes de llegar a
    las anclas, y entonces esta inyección no prueba lo que dice probar: que
    las anclas se comprueban recorriendo las ANCLAS y no los módulos."""
    i = s.find("const courseData")
    j = s.find("};", i)
    bloque = s[i:j]
    bloque = re.sub(r'\s*\{ id: 7, title: "[^"]*"[^}]*\},', "", bloque, count=1)
    for n in range(8, 14):
        bloque = bloque.replace(f"{{ id: {n}, title:", f"{{ id: {n - 1}, title:", 1)
    k = bloque.rfind("}")
    bloque = (bloque[:k + 1]
              + ',\n        { id: 13, title: "Un módulo de relleno", duration: "5 min" }'
              + bloque[k + 1:])
    return s[:i] + bloque + s[j:]


def anadir_14(s: str) -> str:
    """Añade un módulo 14 al final del cap. 5, sin tocar ninguno de los demás."""
    i = s.find("const courseData")
    j = s.find("};", i)
    bloque = s[i:j]
    k = bloque.rfind("}")
    nuevo = bloque[:k + 1] + ',\n        { id: 14, title: "Preparcial del Corte II", duration: "90 min" }' + bloque[k + 1:]
    return s[:i] + nuevo + s[j:]


def romper_orden(s: str) -> str:
    return s.replace("{ id: 3, title:", "{ id: 33, title:", 1)


def vaciar_titulo(s: str) -> str:
    viejo = _titulo(s, 4)
    return s.replace(f'{{ id: 4, title: "{viejo}"', '{ id: 4, title: "   "', 1)


def sin_coursedata(s: str) -> str:
    return s.replace("const courseData", "const otraCosaCualquiera", 1)


INYECCIONES = [
    (CAP4, "el m11 del cap. 4 deja de ser el de las envolventes",
     renombrar(11, "Un módulo intercalado")),
    (CAP4, "al cap. 4 le quitan G y F y la autoevaluación sube al 11",
     quitar_g_y_f),
    (CAP5, "el cap. 5 gana un módulo 14 al final, sin mover ninguna ancla",
     anadir_14),
    (CAP5, "el m9 del cap. 5 deja de ser el de ppm", renombrar(9, "Otra cosa")),
    (CAP5, "el m13 del cap. 5 deja de ser el simulacro: lo que queda fuera cambia",
     renombrar(13, "Un módulo de contenido nuevo")),
    (CAP4, "los módulos del cap. 4 dejan de ir 1..N", romper_orden),
    (CAP5, "un módulo del cap. 5 se queda sin título", vaciar_titulo),
    (CAP4, "el cap. 4 deja de declarar courseData", sin_coursedata),
]


def main() -> None:
    tmp = pathlib.Path(tempfile.mkdtemp(prefix="alcance_preparcial2_"))
    limpio = tmp / "limpio"
    limpio.mkdir()
    for p in (RAIZ / "Htmls_Espacial").glob("capitulo-*.html"):
        shutil.copy2(p, limpio / p.name)

    fallos = 0

    # Control. Sin esto, un arnés en el que TODO falla se leería como perfecto.
    A.HTMLS = limpio
    try:
        dentro, afuera = A._construye()
        if len(dentro) == A.N_ALCANCE and len(afuera) == 4:
            print(f"  CONTROL   sobre copias intactas: {len(dentro)} dentro, "
                  f"{len(afuera)} fuera · OK")
        else:
            print(f"  CONTROL   FALLA: {len(dentro)} dentro, {len(afuera)} fuera")
            fallos += 1
    except SystemExit as e:
        print(f"  CONTROL   FALLA: paró sobre copias intactas — {e}")
        fallos += 1

    print(f"\n  {len(INYECCIONES)} inyecciones:\n")
    for i, (archivo, que, muta) in enumerate(INYECCIONES, 1):
        caso = tmp / f"caso{i}"
        shutil.copytree(limpio, caso)
        p = caso / archivo
        antes = p.read_text(encoding="utf-8")
        despues = muta(antes)
        if antes == despues:
            print(f"  {i:>2}. LA INYECCIÓN NO MUTÓ NADA — {que}")
            fallos += 1
            continue
        p.write_text(despues, encoding="utf-8")
        A.HTMLS = caso
        try:
            A._construye()
            print(f"  {i:>2}. NO CAZADA — {que}")
            fallos += 1
        except SystemExit as e:
            print(f"  {i:>2}. cazada — {que}")
            print(f"      → {str(e).splitlines()[0][:120]}")

    A.HTMLS = RAIZ / "Htmls_Espacial"
    shutil.rmtree(tmp, ignore_errors=True)

    print()
    if fallos:
        sys.exit(f"  {fallos} FALLO(S) en el arnés del alcance")
    print(f"  {len(INYECCIONES)}/{len(INYECCIONES)} cazadas, control en verde")


if __name__ == "__main__":
    main()
