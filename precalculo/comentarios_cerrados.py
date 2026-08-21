#!/usr/bin/env python3
"""
comentarios_cerrados.py — ningún `*/` suelto dentro de un `<style>`

Material de Estadística Espacial 2026-II (20929).

POR QUÉ EXISTE. El injerto del glosario y la rúbrica desde Muestreo (T0.2)
copió los dos componentes con su encabezado `/* ==== … ==== */` delante. Al
refundir los encabezados se borraron las primeras líneas de dos de ellos y
quedaron los cierres: dos `*/` huérfanos, en la plantilla y —por reensamblado—
en las cinco páginas que salen de ella.

Lo que hace un `*/` huérfano NO es cosmético, y ahí está la trampa. El parser
de CSS no lo descarta: lo lee como parte del prelude de la regla siguiente, el
selector entero queda inválido y esa regla se DESCARTA. Se perdieron
`.glosario-notacion` y `.rubrica` —el contenedor de la rúbrica del Taller 1 se
pintaba sin borde, sin fondo, sin radio y sin `overflow: hidden`—, mientras las
cuarenta reglas `.rubrica-*` que vienen detrás seguían vivas. Por eso no lo
caza ninguna comprobación de comportamiento: el componente aparece, se lee y
funciona; solo le falta la caja. Y el navegador no dice nada, porque para él
no hay error: hay una regla con un selector que no entiende.

Es el mismo hueco que `campos_vivos.py` mira por el otro lado. Aquél compara la
declaración con la lectura; éste comprueba que el CSS que se escribió es el CSS
que el navegador llega a leer. Los dos existen porque auditar el resultado deja
pasar lo que no llega a producir resultado.

Descubre los documentos, no los lista: el capítulo 4 lo hereda sin tocar nada.
Y mira TODO el HTML del proyecto, bancos de prueba incluidos —fue otra vez el
banco hecho a mano en T0.3 el último en quedar limpio, como en `campos_vivos`—.

Uso:  python3 precalculo/comentarios_cerrados.py
      python3 precalculo/comentarios_cerrados.py --prueba   (se rompe a sí mismo)
Devuelve 1 si algún `<style>` tiene un comentario descuadrado.
"""
from __future__ import annotations

import pathlib
import re
import sys
import tempfile

RAIZ = pathlib.Path(__file__).resolve().parent.parent
BLOQUE = re.compile(r"<style\b[^>]*>(.*?)</style>", re.S | re.I)


def documentos() -> list[pathlib.Path]:
    """Todo HTML del proyecto con un `<style>`, descubierto."""
    rutas = sorted((RAIZ / "Htmls_Espacial").glob("*.html"))
    rutas += [RAIZ / "plantilla" / "plantilla-capitulo.html", RAIZ / "index.html"]
    return [r for r in rutas
            if r.exists() and BLOQUE.search(r.read_text(encoding="utf-8"))]


def revisa(ruta: pathlib.Path) -> tuple[int, list[str]]:
    """(comentarios bien cerrados, quejas). Cada queja dice qué regla se pierde.

    Las cadenas del CSS se saltan enteras: un `content: "*/"` es legítimo y
    contarlo sería un falso positivo, que en una guarda cuesta más que el
    defecto —una guarda que grita sin motivo se acaba desactivando—.
    """
    texto = ruta.read_text(encoding="utf-8")
    quejas, cerrados = [], 0
    for m in BLOQUE.finditer(texto):
        css, base = m.group(1), m.start(1)
        i, dentro, abierto_en = 0, False, 0
        while i < len(css):
            par = css[i:i + 2]
            if not dentro and css[i] in "\"'":
                comilla, i = css[i], i + 1
                while i < len(css) and css[i] != comilla and css[i] != "\n":
                    i += 2 if css[i] == "\\" else 1
                i += 1
            elif par == "/*":
                if dentro:
                    # Un `/*` DENTRO de un comentario. Los comentarios de CSS no
                    # anidan, así que esto no se escribe a propósito: significa
                    # que a un comentario anterior le falta el cierre y se ha
                    # tragado el CSS de en medio, que desaparece sin descuadrar
                    # nada —el `/*` huérfano se empareja con el `*/` siguiente y
                    # el conteo sale a la par—. Es firma limpia: ni uno solo
                    # de los comentarios del sitio trae un `/*` dentro.
                    quejas.append(
                        f"línea {texto.count(chr(10), 0, base + i) + 1}: `/*` "
                        f"dentro de un comentario abierto en la línea "
                        f"{texto.count(chr(10), 0, base + abierto_en) + 1} — a "
                        f"ése le falta el cierre y se traga el CSS de en medio")
                    i += 2
                else:
                    dentro, abierto_en, i = True, i, i + 2
            elif par == "*/":
                i += 2
                if dentro:
                    dentro, cerrados = False, cerrados + 1
                else:
                    sel = re.search(r"([.#@:\[][^{\n]*?)\s*\{", css[i:i + 400])
                    quejas.append(
                        f"línea {texto.count(chr(10), 0, base + i) + 1}: `*/` sin "
                        f"su `/*` — se descarta la regla "
                        f"`{sel.group(1).strip() if sel else '(indeterminada)'}`")
            else:
                i += 1
        if dentro:
            quejas.append(
                f"línea {texto.count(chr(10), 0, base + abierto_en) + 1}: `/*` "
                f"sin cerrar — se traga el CSS que sigue")
    return cerrados, quejas


def barre(rutas: list[pathlib.Path]) -> int:
    fallos = 0
    for r in rutas:
        cerrados, quejas = revisa(r)
        for q in quejas:
            print(f"  MAL  {r.name}: {q}")
        fallos += len(quejas)
        if not quejas:
            print(f"  OK   {r.name} · {cerrados} comentarios, todos cerrados")
    return fallos


def prueba() -> int:
    """Se rompe a sí mismo. Una comprobación que nadie ha visto fallar puede
    estar bien escrita o ser incapaz de fallar, y desde fuera se ven igual."""
    print("\n=== Autoprueba: se le inyecta el defecto de T0.2 ===")
    original = RAIZ / "plantilla" / "plantilla-capitulo.html"
    texto = original.read_text(encoding="utf-8")
    ancla = "    .rubrica {"
    casos = [
        ("el `*/` huérfano de T0.2, delante de una regla",
         ancla, "       ======== */\n" + ancla, True),
        ("un `/*` sin cerrar, que se traga la regla siguiente",
         ancla, "    /* se abre y no se cierra\n" + ancla, True),
        ("un `/*` sin cerrar al final del bloque, sin nada que lo empareje",
         "\n  </style>", "\n    /* y aquí se acaba\n  </style>", True),
        ("un `*/` dentro de una cadena, que es legítimo",
         ancla, '    .x::after { content: "*/"; }\n' + ancla, False),
        ("un `/*` dentro de una cadena, que también lo es",
         ancla, '    .x::after { content: "/*"; }\n' + ancla, False),
        ("un comentario normal, abierto y cerrado",
         ancla, "    /* un comentario cualquiera */\n" + ancla, False),
    ]
    tmp = pathlib.Path(tempfile.mkdtemp(prefix="comentarios_cerrados_"))
    fallos = 0
    if revisa(original)[1]:
        print("  MAL  el control no está limpio: la plantilla ya viene rota")
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
    print("\n=== comentarios_cerrados.py · ningún `*/` suelto en un <style> ===")
    rutas = documentos()
    if not rutas:
        print("  MAL  no se encontró ningún documento con <style>")
        return 1
    fallos = barre(rutas)
    if "--prueba" in argv:
        fallos += prueba()
    print()
    if fallos:
        print(f"  {fallos} problema(s).\n")
        return 1
    print(f"  {len(rutas)} documentos revisados · ningún comentario descuadrado, "
          f"ninguna regla descartada en silencio.\n")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
