#!/usr/bin/env python3
"""Prueba del botón «← Índice» (pon_boton_indice.py), en tres partes.

1. El inyector, con fixtures en una carpeta temporal: quitar lo que se puso devuelve el original byte a byte; ponerlo
   dos veces no cambia nada; el enlace llega a index.html desde cualquier profundidad; la franja va justo después de
   </header> y la píldora justo después de <body>; el bloque lleva su guardia de iframe; un destino fuera de la raíz,
   una página sin ancla y un estilo desconocido se rechazan.
2. Cinco defectos inyectados en el resultado (enlace a otra profundidad, sin guardia, bloque doble, marca sin cerrar,
   resto tras quitar): cada uno tiene que ser cazado por las comprobaciones.
3. Las páginas del sitio: cada una lleva exactamente un bloque, su enlace llega a un index.html que existe, y ponerlo
   otra vez sobre ella no cambia nada. index.html y los bancos prueba-*.html no llevan ninguno.

Sale con 0 solo si todo pasa.
"""
from __future__ import annotations

import pathlib
import re
import sys
import tempfile

import pon_boton_indice as pbi

RAIZ = pathlib.Path(__file__).resolve().parent.parent
FALLOS: list[str] = []
COMPROBACIONES = 0

DOC_FRANJA = ('<!doctype html>\n<html><head><title>Capítulo</title></head>\n<body>\n'
              '  <header class="usta-header">Estadística Espacial</header>\n\n  <main>contenido</main>\n</body>\n</html>\n')
DOC_PILDORA = ('<!doctype html>\n<html><head><title>Láminas</title></head><body>\n'
               '<section class="diapo">lámina</section>\n</body></html>\n')


def chequea(cond: bool, msg: str) -> None:
    global COMPROBACIONES
    COMPROBACIONES += 1
    if not cond:
        FALLOS.append(msg)
        print(f"  FALLA  {msg}")


def problemas(doc, destino, raiz, original, estilo) -> list[str]:
    """Defectos de un documento con el botón puesto. Lista vacía si está bien."""
    p = []
    n_ini, n_fin = doc.count(pbi.INICIO), doc.count(pbi.FIN)
    if n_ini != 1 or n_fin != 1:
        p.append(f"marcas {n_ini}/{n_fin}, hace falta 1/1")
    if n_ini:
        m = re.search(r'href="([^"]*)"', doc[doc.index(pbi.INICIO):])
        if not m:
            p.append("sin enlace")
        elif (pathlib.Path(destino).parent / m.group(1)).resolve() != (pathlib.Path(raiz) / "index.html").resolve():
            p.append(f"el enlace «{m.group(1)}» no llega a index.html desde {pathlib.Path(destino).name}")
    if "window.top!==window.self" not in doc:
        p.append("sin guardia de iframe")
    if estilo == "franja":
        if '<div class="boton-indice-franja">' not in doc or 'boton-indice--pildora"' in doc:
            p.append("no es la franja")
    elif 'class="boton-indice boton-indice--pildora"' not in doc or '<div class="boton-indice-franja">' in doc:
        p.append("no es la píldora")
    try:
        if original is not None and pbi.quita(doc) != original:
            p.append("quitarlo no devuelve el original")
        if pbi.aplica(doc, destino, raiz, estilo) != doc:
            p.append("no es idempotente (ponerlo otra vez cambia algo)")
    except ValueError as ex:
        p.append(f"bloque dañado: {ex}")
    return p


def parte_1(raiz: pathlib.Path) -> None:
    (raiz / "index.html").write_text("<html></html>", encoding="utf-8")
    casos = [
        ("franja, capítulo", DOC_FRANJA, raiz / "Htmls_Espacial" / "capitulo.html", "franja"),
        ("píldora, lámina", DOC_PILDORA, raiz / "Htmls_Espacial" / "diapositivas" / "lamina.html", "pildora"),
        ("franja, profundidad 3", DOC_FRANJA, raiz / "Htmls_Espacial" / "a" / "b" / "c.html", "franja"),
    ]
    for nombre, doc, destino, estilo in casos:
        a = pbi.aplica(doc, destino, raiz, estilo)
        p = problemas(a, destino, raiz, doc, estilo)
        chequea(not p, f"{nombre}: {p}")
    a = pbi.aplica(DOC_FRANJA, raiz / "Htmls_Espacial" / "capitulo.html", raiz, "franja")
    chequea(a.split("</header>", 1)[1].startswith("\n  " + pbi.INICIO), "la franja no va justo después de </header>")
    b = pbi.aplica(DOC_PILDORA, raiz / "Htmls_Espacial" / "diapositivas" / "lamina.html", raiz, "pildora")
    chequea(b.split("<body>", 1)[1].startswith("\n  " + pbi.INICIO), "la píldora no va justo después de <body>")
    rechazos = [
        ("destino fuera de la raíz", lambda: pbi.aplica(DOC_FRANJA, pathlib.Path("/otra/parte/x.html"), raiz, "franja")),
        ("página sin </header>", lambda: pbi.aplica("<html><body>x</body></html>",
                                                    raiz / "Htmls_Espacial" / "x.html", raiz, "franja")),
        ("página sin <body>", lambda: pbi.aplica("<html>x</html>",
                                                 raiz / "Htmls_Espacial" / "diapositivas" / "x.html", raiz, "pildora")),
        ("estilo desconocido", lambda: pbi.aplica(DOC_FRANJA, raiz / "Htmls_Espacial" / "x.html", raiz, "banner")),
    ]
    for nombre, llamada in rechazos:
        try:
            llamada()
            chequea(False, f"no se rechazó: {nombre}")
        except ValueError:
            chequea(True, nombre)


def doble(d: str) -> str:
    """El mismo bloque puesto dos veces seguidas."""
    i, j = d.index(pbi.INICIO), d.index(pbi.FIN) + len(pbi.FIN)
    ini = d.rindex("\n", 0, i)
    return d[:j] + d[ini:j] + d[j:]


MUTANTES = [
    ("enlace a otra profundidad", "franja", lambda d: re.sub(r'href="[^"]*index\.html"', 'href="index.html"', d)),
    ("sin guardia de iframe", "franja", lambda d: d.replace(pbi.GUARDIA, "")),
    ("bloque puesto dos veces", "franja", doble),
    ("marca de cierre sin poner", "pildora", lambda d: d.replace(pbi.FIN, "", 1)),
    ("resto tras quitar", "pildora", lambda d: d.replace(pbi.FIN, pbi.FIN + " ", 1)),
]


def parte_2(raiz: pathlib.Path) -> None:
    fijas = {
        "franja": (DOC_FRANJA, raiz / "Htmls_Espacial" / "capitulo.html"),
        "pildora": (DOC_PILDORA, raiz / "Htmls_Espacial" / "diapositivas" / "lamina.html"),
    }
    for nombre, estilo, mutar in MUTANTES:
        doc, destino = fijas[estilo]
        bueno = pbi.aplica(doc, destino, raiz, estilo)
        malo = mutar(bueno)
        if malo == bueno:
            chequea(False, f"mutante no aplicado: {nombre}")
            continue
        p = problemas(malo, destino, raiz, doc, estilo)
        chequea(bool(p), f"defecto sin cazar: {nombre}")
        if p:
            print(f"  cazado  {nombre}: {p[0]}")


def parte_3() -> int:
    paginas = pbi.paginas_del_sitio(RAIZ)
    chequea(bool(paginas), "no hay páginas del sitio")
    for ruta in paginas:
        doc = ruta.read_bytes().decode("utf-8")
        p = problemas(doc, ruta, RAIZ, None, pbi.estilo_de(ruta))
        chequea(not p, f"{ruta.relative_to(RAIZ)}: {p}")
    for ruta in [RAIZ / "index.html", *sorted((RAIZ / "Htmls_Espacial").glob("prueba-*.html"))]:
        chequea(pbi.INICIO not in ruta.read_text(encoding="utf-8"), f"{ruta.name} no debe llevar botón")
    return len(paginas)


def main() -> int:
    print("1. El inyector, con fixtures")
    with tempfile.TemporaryDirectory() as tmp:
        raiz = pathlib.Path(tmp)
        parte_1(raiz)
        print("2. Defectos inyectados (cada uno tiene que ser cazado)")
        parte_2(raiz)
    print("3. Las páginas del sitio")
    n = parte_3()
    print(f"   {n} páginas revisadas")
    print(f"\n{COMPROBACIONES} comprobaciones, {len(FALLOS)} fallo(s)")
    return 0 if not FALLOS else 1


if __name__ == "__main__":
    sys.exit(main())
