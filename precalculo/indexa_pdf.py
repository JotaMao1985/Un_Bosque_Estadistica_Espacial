#!/usr/bin/env python3
"""
indexa_pdf.py — qué localizadores existen en un ejemplar, y en qué página impresa

Material de Estadística Espacial 2026-II (20929). Idea tomada de Muestreo (20939),
reducida a lo que necesita este curso.

Un índice DELGADO: sección, figura y tabla → páginas impresas donde aparecen. No guarda
ni una línea del texto, así que se versiona (el repo es público) y permite que el auditor
de citas descarte un localizador imposible en un clon sin el corpus. Ningún localizador
se cuenta a mano ni se le cree a un subagente: se consulta aquí.

  · secciones  «1.2.1» → [primera, última] página impresa. El intervalo es GENEROSO: va de
               donde empieza hasta donde empieza la siguiente, inclusive, porque dos
               secciones pueden compartir página.
  · figuras, tablas  «Figure 8.31.» / «Table 7.1.» en el cuerpo → página impresa del rótulo.

La página impresa sale del `desfase` de bibliografia/ejemplares.yml, que se midió y se
puso a mano. No se indexan ecuaciones: en un PDF no hay manera fiable.

Uso:  python3 precalculo/indexa_pdf.py CLAVE
      python3 precalculo/indexa_pdf.py CLAVE --comprobar
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys

import yaml

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from fuentes_config import BIB, CORPUS  # noqa: E402

# Cómo se reconoce cada cosa en cada ejemplar. Añadir un PDF es añadir una entrada aquí.
PERFILES = {
    "baddeley2015spatial": {
        # Las secciones salen de la tabla de contenido (páginas 10–14 del PDF): número,
        # puntos conductores y página impresa. Los encabezados del cuerpo no sirven: un
        # renglón de código que empieza por «4.7» se comía los capítulos 5 a 16.
        "indice": (10, 14),
        "linea_indice": re.compile(r"^\s*(\d{1,2}\.\d{1,2}(?:\.\d{1,2})?)\s+\S.*?\s(\d{1,3})\s*$"),
        "figura": re.compile(r"^\s*Figure (\d{1,2}\.\d{1,2})\.\s"),
        "tabla": re.compile(r"^\s*Table (\d{1,2}\.\d{1,2})\.\s"),
        "desde_pagina_pdf": 20,   # antes está el índice general, que repite los encabezados
    },
}


def clave_seccion(s: str) -> tuple[int, ...]:
    return tuple(int(x) for x in s.split("."))


def indexa(clave: str) -> dict:
    perfil = PERFILES[clave]
    ficha = (yaml.safe_load((BIB / "ejemplares.yml").read_text("utf-8")) or {}).get(clave) or {}
    desfase = ficha.get("desfase")
    if not isinstance(desfase, int):
        sys.exit(f"FALLA  «{clave}» no tiene `desfase` entero en ejemplares.yml")
    carpeta = CORPUS / "texto" / clave
    hojas = sorted(h for h in carpeta.glob("p*.txt") if re.fullmatch(r"p\d{4}\.txt", h.name))
    if not hojas:
        sys.exit(f"FALLA  no hay texto de «{clave}» en {carpeta}: corre extrae_fuente.py")
    inicios: dict[str, int] = {}
    desde, hasta = perfil["indice"]
    for n in range(desde, hasta + 1):
        for linea in (carpeta / f"p{n:04d}.txt").read_text("utf-8").splitlines():
            if m := perfil["linea_indice"].match(linea):
                inicios.setdefault(m.group(1), int(m.group(2)))
    figuras: dict[str, int] = {}
    tablas: dict[str, int] = {}
    ultima = 0
    for hoja in hojas:
        n = int(hoja.stem[1:])
        if n < perfil["desde_pagina_pdf"]:
            continue
        impresa = n - desfase
        ultima = max(ultima, impresa)
        for linea in hoja.read_text("utf-8").splitlines():
            if m := perfil["figura"].match(linea):
                figuras.setdefault(m.group(1), impresa)
            if m := perfil["tabla"].match(linea):
                tablas.setdefault(m.group(1), impresa)
    orden = sorted(inicios, key=clave_seccion)
    retrocesos = [s for a, s in zip(orden, orden[1:]) if inicios[s] < inicios[a]]
    if retrocesos:
        sys.exit(f"FALLA  la tabla de contenido retrocede en {retrocesos[:5]}: revisa el perfil")
    secciones = {}
    for i, s in enumerate(orden):
        fin = inicios[orden[i + 1]] if i + 1 < len(orden) else ultima
        secciones[s] = [inicios[s], max(inicios[s], fin)]
    return {
        "clave": clave,
        "extractor": "indexa_pdf@2",
        "sha256_ejemplar": ficha.get("sha256"),
        "desfase": desfase,
        "paginas_impresas": [perfil["desde_pagina_pdf"] - desfase, ultima],
        "secciones": secciones,
        "figuras": dict(sorted(figuras.items(), key=lambda kv: clave_seccion(kv[0]))),
        "tablas": dict(sorted(tablas.items(), key=lambda kv: clave_seccion(kv[0]))),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    ap.add_argument("clave", choices=sorted(PERFILES))
    ap.add_argument("--comprobar", action="store_true", help="no escribe; sale con 1 si cambió")
    args = ap.parse_args()
    indice = indexa(args.clave)
    ruta = BIB / "indices" / f"{args.clave}.json"
    texto = json.dumps(indice, ensure_ascii=False, indent=1) + "\n"
    if args.comprobar:
        igual = ruta.exists() and ruta.read_text("utf-8") == texto
        print(f"{'OK    ' if igual else 'FALLA '} indices/{args.clave}.json {'al día' if igual else 'desfasado'}")
        return 0 if igual else 1
    ruta.parent.mkdir(exist_ok=True)
    ruta.write_text(texto, "utf-8")
    print(f"OK     indices/{args.clave}.json: {len(indice['secciones'])} secciones, "
          f"{len(indice['figuras'])} figuras, {len(indice['tablas'])} tablas, "
          f"pp. {indice['paginas_impresas'][0]}–{indice['paginas_impresas'][1]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
