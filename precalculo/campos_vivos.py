#!/usr/bin/env python3
"""
campos_vivos.py — ningún campo de `courseData` se declara y no se lee

Material de Estadística Espacial 2026-II (20929).

POR QUÉ EXISTE. El 2026-08-14, escribiendo la entrada sobre el SIG, salió que
la barra lateral pintaba solo `title`. `courseData` declaraba además
`shortTitle` y `duration` —y en los capítulos 2 y 3, `subtitle`—, y
`renderNavigation()` no leía ninguno. Cien cadenas escritas con cuidado entre
tres capítulos, un taller, dos bancos y la plantilla, muertas en el HTML.

Lo grave no es que estuvieran muertas: es lo que eso permitió encima. Como
NADA de aquello se pintaba, el esquema pudo PARTIRSE EN DOS sin que se notara
—capítulo 1 y taller con `{shortTitle, duration}`, capítulos 2 y 3 con
`{subtitle}`— y ningún auditor podía verlo. Un campo que no se lee no tiene
comportamiento, así que no hay comprobación de comportamiento que lo cace: ni
el arnés de prosa, ni las guardas del ensamblador, ni la consola del navegador.
Solo se ve mirando la DECLARACIÓN contra la LECTURA, que es lo que hace esto.

Es el mismo hueco que `sin_aritmetica.py` cubre por el otro lado: aquél mira el
código que escribe las cifras en vez de las cifras; éste mira el contrato entre
el dato y quien lo pinta. Los dos existen porque auditar solo el resultado deja
pasar lo que no llega a producir resultado.

Descubre los documentos, no los lista: el capítulo 4 lo hereda sin tocar nada.

Uso:  python3 precalculo/campos_vivos.py
      python3 precalculo/campos_vivos.py --prueba   (se rompe a sí mismo)
Devuelve 1 si algún campo declarado no lo lee nadie.
"""
from __future__ import annotations

import pathlib
import re
import sys
import tempfile

RAIZ = pathlib.Path(__file__).resolve().parent.parent
ABRE = "    const courseData = {"
CIERRA = "\n    };\n"

# `id` se lee en `loadModule(${module.id})` y en las comparaciones con
# `currentModuleId`; queda cubierto por la búsqueda normal. No hay exenciones,
# y es a propósito: una lista de exenciones es donde se esconde el campo
# siguiente.


def documentos() -> list[pathlib.Path]:
    """Todo HTML del proyecto que declare un `courseData`, descubierto."""
    rutas = sorted((RAIZ / "Htmls_Espacial").glob("*.html"))
    rutas += [RAIZ / "plantilla" / "plantilla-capitulo.html"]
    return [r for r in rutas if r.exists() and ABRE in r.read_text(encoding="utf-8")]


def _sin_cadenas(texto: str) -> str:
    """Vacía los literales de cadena: «5 min» no declara ningún campo, y un
    valor con dos puntos dentro —«T1 · El régimen: lo que no se ve»— daría un
    campo inventado que no existe y que nadie podría satisfacer."""
    texto = re.sub(r'"(?:[^"\\]|\\.)*"', '""', texto)
    return re.sub(r"'(?:[^'\\]|\\.)*'", "''", texto)


def revisa(ruta: pathlib.Path) -> tuple[list[str], list[str]]:
    """(campos declarados, campos que no lee nadie)."""
    doc = ruta.read_text(encoding="utf-8")
    i = doc.index(ABRE)
    j = doc.index(CIERRA, i) + len(CIERRA)
    bloque, resto = doc[i:j], doc[:i] + doc[j:]

    declarados = sorted(set(re.findall(r"(\w+)\s*:", _sin_cadenas(bloque))))
    muertos = []
    for campo in declarados:
        leido = (re.search(rf"\.{campo}\b", resto)
                 or re.search(rf"\[\s*['\"]{campo}['\"]\s*\]", resto))
        if not leido:
            muertos.append(campo)
    return declarados, muertos


def barre(rutas: list[pathlib.Path], verboso: bool = True) -> int:
    fallos = 0
    for ruta in rutas:
        declarados, muertos = revisa(ruta)
        if verboso:
            print(f"  {'OK ' if not muertos else 'MAL'}  {ruta.name:<38} "
                  f"declara {declarados}")
            for c in muertos:
                print(f"         · «{c}» no lo lee nadie")
        fallos += len(muertos)
    return fallos


def coherencia(rutas: list[pathlib.Path]) -> int:
    """Y además: que todos declaren el MISMO esquema, salvo los opcionales.

    Sin esto, el capítulo 4 puede estrenar `resumen:` y pintarlo, y quedarse
    solo con él para siempre sin que nada lo diga. Es la mitad del defecto
    del 2026-08-14 que la comprobación de arriba no ve: aquélla exige que lo
    declarado se lea; ésta, que lo declarado no diverja.
    """
    print("\n=== Coherencia del esquema ================================")
    OPCIONALES = {"subtitle", "duration"}
    esquemas = {r.name: set(revisa(r)[0]) for r in rutas}
    obligatorios = {n: e - OPCIONALES for n, e in esquemas.items()}
    comun = set.intersection(*obligatorios.values()) if obligatorios else set()
    fallos = 0
    for nombre, campos in sorted(obligatorios.items()):
        sobra = campos - comun
        print(f"  {'OK ' if not sobra else 'MAL'}  {nombre:<38} "
              f"{sorted(campos)}" + (f"  ← solo aquí: {sorted(sobra)}" if sobra else ""))
        fallos += len(sobra)
    print(f"       núcleo común: {sorted(comun)} · opcionales: {sorted(OPCIONALES)}")
    return fallos


def prueba() -> int:
    """Se rompe a sí mismo. Una comprobación que nadie ha visto fallar puede
    estar bien escrita o ser incapaz de fallar, y desde fuera se ven igual."""
    print("\n=== Autoprueba: se le inyecta el defecto del 2026-08-14 ====")
    original = documentos()[0]
    texto = original.read_text(encoding="utf-8")
    linea = re.search(r"\n(\s*\{ id: 1,[^\n]*)", texto).group(1)
    casos = [
        ("un campo declarado que no lee nadie",
         linea, linea.replace(" }", ', shortTitle: "X" }'), True),
        ("un campo declarado que SÍ se lee",
         linea, linea.replace(" }", ', subtitle: "X" }'), False),
        ("un valor con dos puntos dentro, que no declara nada",
         linea, re.sub(r'title: "[^"]*"', 'title: "T1: el régimen"', linea, count=1), False),
    ]
    tmp = pathlib.Path(tempfile.mkdtemp(prefix="campos_vivos_"))
    fallos = 0
    _, limpio = revisa(original)
    if limpio:
        print(f"  MAL  el control no está limpio: {limpio}")
        return 1
    print(f"  OK   control · {original.name} sale limpio sin inyectar nada")
    for nombre, viejo, nuevo, debe_cazarse in casos:
        copia = tmp / original.name
        copia.write_text(texto.replace(viejo, nuevo, 1), encoding="utf-8")
        if copia.read_text(encoding="utf-8") == texto:
            print(f"  MAL  INERTE · «{nombre}» no cambió el archivo")
            fallos += 1
            continue
        cazado = bool(revisa(copia)[1])
        ok = cazado == debe_cazarse
        print(f"  {'OK ' if ok else 'MAL'}  «{nombre}» → "
              + ("cazado" if cazado else "pasa")
              + ("" if debe_cazarse else "  (tiene que pasar)"))
        fallos += 0 if ok else 1
    return fallos


def main(argv: list[str]) -> int:
    print("\n=== campos_vivos.py · ningún campo de courseData se declara "
          "y no se lee ===")
    rutas = documentos()
    if not rutas:
        print("  MAL  no se encontró ningún documento con courseData")
        return 1
    fallos = barre(rutas)
    fallos += coherencia(rutas)
    if "--prueba" in argv:
        fallos += prueba()
    print()
    if fallos:
        print(f"  {fallos} problema(s).\n")
        return 1
    print(f"  {len(rutas)} documentos revisados · todo campo declarado lo lee "
          f"alguien, y el esquema no diverge.\n")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
