#!/usr/bin/env python3
"""
motores.py — leer un motor de animación para llevarlo en línea a un capítulo

Material de Estadística Espacial 2026-II (20929).

Un capítulo es UN solo HTML: sin fetch, sin archivos locales. Los motores de las
animaciones (`precalculo/anim2d/*.js`, `precalculo/nucleo3d/nucleo3d.js`) se editan
como archivos y viajan DENTRO del capítulo, dentro de un `<script>`. `lee_motor`
es el único sitio por donde pasan, y comprueba lo que, en el HTML, rompe sin
avisar:

  · `</script` en el JS cerraría su propia etiqueta a mitad de una función; el
    navegador no protesta, el motor llega cortado y la animación no monta.
  · `@@` es el marcador de las plantillas de estampado (`@@MOTOR@@`, `@@URL@@`…):
    un motor que lo contenga recibiría, sin error, la sustitución de un marcador
    que no es suyo.

Se PARA en vez de escapar: un motor que contiene alguna de las dos cosas se
arregla, no se disimula.
"""
from __future__ import annotations

import pathlib
import sys


def lee_motor(ruta: str | pathlib.Path) -> str:
    ruta = pathlib.Path(ruta)
    js = ruta.read_text(encoding="utf-8")
    if "</script" in js.lower():
        sys.exit(f"PARADO: {ruta.name} contiene «</script» y cerraría su propia etiqueta")
    if "@@" in js:
        sys.exit(f"PARADO: {ruta.name} contiene «@@», el marcador de las plantillas de estampado")
    return js
