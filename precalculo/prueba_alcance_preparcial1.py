#!/usr/bin/env python3
"""
prueba_alcance_preparcial1.py — le inyecta defectos al alcance del preparcial

Material de Estadística Espacial 2026-II (20929). P0.1 del
PLAN_Preparcial_Corte_1.md.

Por la razón de siempre en este repositorio: el verde de una comprobación que
nunca se ha visto fallar no significa nada (A.3). Aquí importa el doble, porque
lo que `alcance_preparcial1.py` afirma es una NUMERACIÓN, y una numeración se
rompe callada: los módulos siguen siendo doce, siguen yendo del 1 al 12 y
siguen teniendo título.

La inyección nº 2 es la que justifica el archivo. Pasó en verde la primera vez:
al quitarle el glosario al capítulo 1 la autoevaluación se corrió al módulo 11,
el ancla del 12 no se comprobó **porque ya no había módulo 12**, y el alcance
devolvió sus 30 módulos con la autoevaluación del capítulo dentro. Un ancla
sobre algo que desaparece no falla; deja de existir.

Trabaja sobre copias en un directorio temporal. Nunca toca lo publicado.

Uso:  python3 precalculo/prueba_alcance_preparcial1.py
"""
from __future__ import annotations

import pathlib
import re
import shutil
import sys
import tempfile

RAIZ = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "precalculo"))
import alcance_preparcial1 as A  # noqa: E402

CAP1 = "capitulo-1-datos-espaciales.html"
CAP2 = "capitulo-2-crs-georreferenciacion.html"
CAP3 = "capitulo-3-cartografia-maup.html"


def quitar_glosario(s: str) -> str:
    """Le quita el m11 al capítulo 1 y corre la autoevaluación al 11."""
    s2 = re.sub(r'\s*\{ id: 11, title: "Glosario de notación del curso"[^}]*\},',
                '', s, count=1)
    return s2.replace('{ id: 12, title: "Autoevaluación y ejercicios guiados"',
                      '{ id: 11, title: "Autoevaluación y ejercicios guiados"', 1)


def truncar_en_7(s: str) -> str:
    """Deja el capítulo 3 en siete módulos: el alcance pide hasta el 8."""
    i = s.find('{ id: 8, title: "MAUP I')
    j = s.find("]", i)
    return s[:i] + s[j:]


def romper_orden(s: str) -> str:
    return s.replace('{ id: 3, title: "Proyectar es elegir qué destruir"',
                     '{ id: 33, title: "Proyectar es elegir qué destruir"', 1)


def vaciar_titulo(s: str) -> str:
    return s.replace('{ id: 4, title: "EPSG en la práctica"',
                     '{ id: 4, title: "   "', 1)


def sin_coursedata(s: str) -> str:
    return s.replace("const courseData", "const otraCosaCualquiera", 1)


INYECCIONES = [
    (CAP3, "el m8 del cap. 3 se renombra: la frontera del temario se mueve",
     lambda s: s.replace('{ id: 8, title: "MAUP I · el efecto escala"',
                         '{ id: 8, title: "Un módulo intercalado"', 1)),
    (CAP1, "al cap. 1 le quitan el glosario y la autoevaluación sube al 11",
     quitar_glosario),
    (CAP2, "el m5 del cap. 2 deja de ser el de st_transform vs st_set_crs",
     lambda s: s.replace('{ id: 5, title: "Reproyectar no es reetiquetar"',
                         '{ id: 5, title: "Otra cosa"', 1)),
    (CAP3, "el cap. 3 se queda en 7 módulos y el alcance pide hasta el 8",
     truncar_en_7),
    (CAP2, "los módulos del cap. 2 dejan de ir 1..N", romper_orden),
    (CAP2, "un módulo del cap. 2 se queda sin título", vaciar_titulo),
    (CAP1, "el cap. 1 deja de declarar courseData", sin_coursedata),
    (CAP3, "el m9 del cap. 3 deja de ser MAUP II: lo que queda fuera cambia",
     lambda s: s.replace('{ id: 9, title: "MAUP II · el efecto zonificación"',
                         '{ id: 9, title: "Otra cosa distinta"', 1)),
]


def main() -> None:
    tmp = pathlib.Path(tempfile.mkdtemp(prefix="alcance_preparcial1_"))
    limpio = tmp / "limpio"
    limpio.mkdir()
    for p in (RAIZ / "Htmls_Espacial").glob("capitulo-*.html"):
        shutil.copy2(p, limpio / p.name)

    fallos = 0

    # Control. Sin esto, un arnés en el que TODO falla se leería como perfecto.
    A.HTMLS = limpio
    try:
        dentro, afuera = A._construye()
        if len(dentro) == 30 and len(afuera) == 3:
            print("  CONTROL   sobre copias intactas: 30 dentro, 3 fuera · OK")
        else:
            print(f"  CONTROL   FALLA: {len(dentro)} dentro, {len(afuera)} fuera")
            fallos += 1
    except SystemExit as e:
        print(f"  CONTROL   FALLA: paró sobre copias intactas — {e}")
        fallos += 1

    print(f"\n  {len(INYECCIONES)} inyecciones:\n")
    for i, (archivo, que, muta) in enumerate(INYECCIONES, 1):
        caso = tmp / f"caso{i}"
        if caso.exists():
            shutil.rmtree(caso)
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
