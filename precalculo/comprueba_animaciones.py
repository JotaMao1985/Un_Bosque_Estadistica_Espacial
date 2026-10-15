#!/usr/bin/env python3
"""
comprueba_animaciones.py — cada capítulo lleva el motor que hay en su archivo

Material de Estadística Espacial 2026-II (20929).

POR QUÉ EXISTE. El motor de una animación se edita en `precalculo/anim2d/*.js` y
`ensambla_capN.py` lo copia en línea al capítulo. Si alguien edita el motor y no
reensambla, el capítulo publica la versión VIEJA y nada lo ve: el auditor de cifras
lee la prosa, no el JavaScript, y la consola sale limpia. Aquí se comprueba, byte a
byte, que el texto de cada motor esté dentro de cada página que debe llevarlo.

`PAGINAS` es la tabla: página → motores que lleva, en el orden en que los lleva. Una
animación nueva añade su fila. Y como la cáscara (`anim2d.js`) la llevan varias páginas,
tocarla obliga a reensamblar TODAS: esta tabla es la que lo recuerda.

    python3 precalculo/comprueba_animaciones.py   # sale con 1 si algún capítulo lleva un motor viejo
"""
from __future__ import annotations

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from motores import lee_motor  # noqa: E402

RAIZ = pathlib.Path(__file__).resolve().parent.parent

PAGINAS = {
    "Htmls_Espacial/capitulo-4-patrones-puntuales.html": [
        "precalculo/anim2d/anim2d.js",
        "precalculo/anim2d/kanillo2d.js",
    ],
    "Htmls_Espacial/capitulo-6-pesos-espaciales.html": [
        "precalculo/anim2d/anim2d.js",
        "precalculo/anim2d/rezago2d.js",
    ],
}


def main() -> int:
    mal = 0
    for pagina, motores in PAGINAS.items():
        ruta = RAIZ / pagina
        if not ruta.exists():
            print(f"{pagina}: NO EXISTE")
            mal += 1
            continue
        html = ruta.read_text(encoding="utf-8")
        for motor in motores:
            lleva = lee_motor(RAIZ / motor) in html
            print(f"{pagina}: {motor.split('/')[-1]} {'al día' if lleva else 'DESACTUALIZADO (hay que reensamblar el capítulo)'}")
            mal += not lleva
    return 1 if mal else 0


if __name__ == "__main__":
    sys.exit(main())
