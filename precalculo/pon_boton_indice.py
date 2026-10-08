#!/usr/bin/env python3
"""El botón «← Índice» de las páginas del curso: vuelve a index.html desde cualquier pieza.

Dos formas, según la página:
  franja   las que tienen cabecera (capítulos, apéndice, talleres, preparciales y la animación): una línea a la derecha,
           justo debajo de </header>. No tapa nada, en ningún ancho.
  pildora  las láminas: una píldora fija en la esquina superior derecha (una cabecera encima del botón
           lo taparía, y la animación de núcleos la tiene).

El bloque va entre dos marcas (`boton-indice:inicio` y `fin`): ponerlo otra vez lo reemplaza y no lo duplica,
y `quita()` lo deshace byte a byte. Dentro de un <iframe> el bloque se borra solo: la animación que las láminas
incrustan no muestra un segundo botón.

Como módulo, lo llaman los ensambladores y construir.py:
    aplica(doc, destino, raiz=None, estilo="franja") -> str
Por línea de órdenes reescribe las páginas del sitio (sin argumentos: todas; el propio index.html y los bancos
prueba-*.html quedan fuera). Con --quitar, las deja sin el botón:
    python3 precalculo/pon_boton_indice.py [--quitar] [ruta ...]
"""
from __future__ import annotations

import os
import pathlib
import re
import sys

RAIZ_DEL_SITIO = pathlib.Path(__file__).resolve().parent.parent
ESTILOS = ("franja", "pildora")
CARPETAS_DE_LAMINAS = ("diapositivas",)  # estas llevan la píldora; el resto, la franja

INICIO = "<!-- boton-indice:inicio -->"
FIN = "<!-- boton-indice:fin -->"
RE_BLOQUE = re.compile(r"\n[ \t]*" + re.escape(INICIO) + r".*?" + re.escape(FIN), re.S)
RE_CUERPO = re.compile(r"<body\b[^>]*>")

CSS = """<style>
    .boton-indice{display:inline-flex;align-items:center;gap:.35em;padding:.4em .95em;border:1px solid #94A3B8;border-radius:999px;background:#fff;color:#012820;font-family:inherit;font-size:14px;font-weight:600;line-height:1.25;text-decoration:none;box-shadow:0 2px 8px rgba(1,40,32,.18)}
    .boton-indice:hover{border-color:#FF6600;color:#B84A00}
    .boton-indice:focus-visible{outline:3px solid #FF6600;outline-offset:3px}
    .boton-indice-franja{display:flex;justify-content:flex-end;box-sizing:border-box;width:100%;max-width:80rem;margin:0 auto;padding:12px 16px 8px}
    .boton-indice--pildora{position:fixed;top:14px;right:14px;z-index:60}
    @media print{.boton-indice-franja,.boton-indice--pildora{display:none}}
  </style>"""

GUARDIA = ("<script>if(window.top!==window.self)document.querySelectorAll("
           "'.boton-indice-franja,.boton-indice--pildora').forEach(function(e){e.remove()});</script>")


def href_al_indice(destino: pathlib.Path, raiz: pathlib.Path) -> str:
    """Ruta relativa de index.html desde la carpeta del archivo: ../index.html, ../../index.html…"""
    return os.path.relpath(raiz / "index.html", start=destino.parent).replace(os.sep, "/")


def bloque(href: str, estilo: str) -> str:
    clase = "boton-indice" + (" boton-indice--pildora" if estilo == "pildora" else "")
    enlace = f'<a class="{clase}" href="{href}"><span aria-hidden="true">←</span> Índice</a>'
    if estilo == "franja":
        enlace = f'<div class="boton-indice-franja">{enlace}</div>'
    return f"\n  {INICIO}\n  {CSS}\n  {enlace}\n  {GUARDIA}\n  {FIN}"


def quita(doc: str) -> str:
    """El documento sin el botón: lo que había antes de ponerlo, byte a byte."""
    if INICIO not in doc and FIN not in doc:
        return doc
    sin, n = RE_BLOQUE.subn("", doc)
    if n != 1 or INICIO in sin or FIN in sin:
        raise ValueError(f"bloque del botón dañado: {n} bloque(s) completo(s) con sus marcas")
    return sin


def aplica(doc: str, destino, raiz=None, estilo: str = "franja") -> str:
    """El documento con el botón puesto (o reemplazado) para un archivo que se escribirá en `destino`."""
    if estilo not in ESTILOS:
        raise ValueError(f"estilo desconocido: {estilo!r}")
    raiz = pathlib.Path(raiz or RAIZ_DEL_SITIO).resolve()
    destino = pathlib.Path(destino).resolve()
    if raiz not in destino.parents:
        raise ValueError(f"{destino} está fuera de {raiz}")
    base = quita(doc)
    b = bloque(href_al_indice(destino, raiz), estilo)
    if estilo == "franja":
        if base.count("</header>") != 1:
            raise ValueError(f"{destino.name}: hace falta exactamente un </header>")
        i = base.index("</header>") + len("</header>")
    else:
        cuerpos = list(RE_CUERPO.finditer(base))
        if len(cuerpos) != 1:
            raise ValueError(f"{destino.name}: hace falta exactamente una etiqueta <body>")
        i = cuerpos[0].end()
    return base[:i] + b + base[i:]


def estilo_de(ruta) -> str:
    return "pildora" if pathlib.Path(ruta).parent.name in CARPETAS_DE_LAMINAS else "franja"


def paginas_del_sitio(raiz: pathlib.Path = RAIZ_DEL_SITIO) -> list[pathlib.Path]:
    """Las páginas que llevan botón: Htmls_Espacial/*.html salvo los bancos prueba-*, y las carpetas de láminas y animaciones."""
    h = raiz / "Htmls_Espacial"
    rutas = [p for p in sorted(h.glob("*.html")) if not p.name.startswith("prueba-")]
    for carpeta in ("diapositivas", "animaciones"):
        rutas += sorted((h / carpeta).glob("*.html"))
    return rutas


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    quitar = "--quitar" in argv
    rutas = [pathlib.Path(a) for a in argv if a != "--quitar"] or paginas_del_sitio()
    for ruta in rutas:
        ruta = pathlib.Path(ruta).resolve()
        original = ruta.read_bytes().decode("utf-8")
        nuevo = quita(original) if quitar else aplica(original, ruta, RAIZ_DEL_SITIO, estilo_de(ruta))
        if nuevo == original:
            estado = "sin cambios"
        else:
            ruta.write_bytes(nuevo.encode("utf-8"))
            estado = "quitado" if quitar else "puesto"
        print(f"{estado:12} {ruta.relative_to(RAIZ_DEL_SITIO)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
