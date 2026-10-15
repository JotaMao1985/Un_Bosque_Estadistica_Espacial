#!/usr/bin/env python3
"""
verifica_bloques_cap5.py — ejecuta en R los bloques de código de las presentaciones del
capítulo 5 y contrasta sus líneas `#>` con la salida real.

Es el hermano de `verifica_cifras_cap5.py` (que cotejaba los números del texto): aquí se
comprueba lo que se proyecta como código. Los bloques de las diapositivas son extractos
recortados de los del capítulo, así que se ejecutan ENCADENADOS (los de la sesión 1 y luego los
de la 2, como un estudiante que sigue las diapositivas de arriba abajo), después de la misma
preparación del capítulo (`library`, lectura de las capas).

Para cada bloque:
  1. el código se ejecuta de verdad (si R da error, el bloque falla);
  2. cada número y cada palabra de sus líneas `#>` tiene que aparecer en la salida real de ESE
     bloque; y cada línea de salida real que lleve una cifra tiene que estar anunciada.

Uso, desde la raíz del repositorio:
    python3 Htmls_Espacial/diapositivas/fuentes/verifica_bloques_cap5.py            # las dos sesiones
    python3 …/verifica_bloques_cap5.py --sesion 1
    python3 …/verifica_bloques_cap5.py --sesion 2 --vuelca CARPETA     # además guarda la salida real de cada bloque
Requiere R 4.4 con spatstat y sf (se usa `precalculo/rscript.sh`). Sale con código 1 si algo falla.
"""
from __future__ import annotations

import re
import subprocess
import sys
import tempfile
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[2]
FUENTES = {1: AQUI / "capitulo_5_sesion_1.md", 2: AQUI / "capitulo_5_sesion_2.md"}

# La misma preparación del capítulo (módulos 1, 5, 8 y 9): lo que los bloques de las diapositivas dan por hecho.
PREAMBULO = r'''
suppressPackageStartupMessages({ library(sf); library(spatstat) })
options(scipen = 999, digits = 7, warn = 1)
set.seed(2026)
cole  <- st_read("datos/procesado/bogota_colegios.gpkg", quiet = TRUE)
loc   <- st_read("datos/procesado/bogota_localidades.gpkg", quiet = TRUE)
v_urb <- st_read("datos/procesado/bogota_ventana_urbana.gpkg", quiet = TRUE)
s11   <- st_read("datos/procesado/bogota_colegios_saber11.gpkg", quiet = TRUE)
xy    <- st_coordinates(cole)
WU <- as.owin(st_geometry(st_union(v_urb)))
pu <- suppressWarnings(ppp(xy[, 1], xy[, 2], window = WU))
'''

NUM = re.compile(r"-?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?")
PALABRA = re.compile(r"[A-Za-z_][A-Za-z_0-9.]*")


LENGUAJES = {"", "r", "python", "pseudo", "vba", "sql", "shell", "dockerfile", "yaml", "toml", "json", "js", "text", "http", "env", "ini"}


def bloques(ruta: Path) -> list[dict]:
    out, titulo, en, buf, lang = [], "", False, [], ""
    for l in ruta.read_text(encoding="utf-8").splitlines():
        if not en and l.startswith("## "):
            titulo = re.sub(r"\s*\{[^{}]*\}\s*$", "", l[3:]).strip()
        if l.strip().startswith("```"):
            if not en:
                en, buf, lang = True, [], l.strip()[3:].split()[0] if l.strip()[3:].split() else ""
            else:
                en = False
                if lang == "r":
                    out.append({"titulo": titulo, "codigo": "\n".join(buf)})
                elif lang not in LENGUAJES:          # p. ej. ```R: no se ejecutaría y su `#>` quedaría sin comprobar
                    out.append({"titulo": titulo, "codigo": "", "lenguaje_raro": lang})
            continue
        if en:
            buf.append(l)
    return out


def _lit_r(s: str) -> str:
    """Una cadena de Python como literal de R."""
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n") + '"'


def ejecuta(todos: list[dict]) -> list[str]:
    """Ejecuta los bloques encadenados, en una sola sesión de R; devuelve la salida de cada uno."""
    partes = [PREAMBULO]
    for i, b in enumerate(todos):
        codigo = "\n".join(l for l in b["codigo"].splitlines() if not l.lstrip().startswith("#>"))
        # sesión 1: números en notación fija; sesión 2: la notación por defecto de R (sus bloques imprimen 5.69321e-06)
        partes.append(f'options(scipen = {0 if b["sesion"] == 2 else 999})\ncat("###BLOQUE-{i}###\\n")\nsource(textConnection({_lit_r(codigo)}), echo = FALSE, print.eval = TRUE)\n')
    partes.append('cat("###BLOQUE-FIN###\\n")\n')
    with tempfile.TemporaryDirectory() as td:
        guion = Path(td) / "bloques.R"
        guion.write_text("\n".join(partes), encoding="utf-8")
        r = subprocess.run([str(RAIZ / "precalculo" / "rscript.sh"), str(guion)], cwd=RAIZ, capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit("R terminó con error:\n" + r.stdout[-2500:] + "\n" + r.stderr[-2500:])
    salida = r.stdout
    res = []
    for i in range(len(todos)):
        marca = f"###BLOQUE-{i}###"
        ini = salida.index(marca) + len(marca)
        fin = salida.index(f"###BLOQUE-{i + 1}###") if f"###BLOQUE-{i + 1}###" in salida else salida.index("###BLOQUE-FIN###")
        res.append(salida[ini:fin])
    return res


def main() -> int:
    sesiones = [1, 2]
    if "--sesion" in sys.argv:
        sesiones = [int(sys.argv[sys.argv.index("--sesion") + 1])]
    todos = []
    for s in sesiones:
        if FUENTES[s].exists():
            for b in bloques(FUENTES[s]):
                todos.append({**b, "sesion": s})
    raros = [b for b in todos if "lenguaje_raro" in b]
    todos = [b for b in todos if "lenguaje_raro" not in b]
    salidas = ejecuta(todos)
    if "--vuelca" in sys.argv:                       # la salida real de cada bloque, para pegarla tal cual en la diapositiva
        carpeta = Path(sys.argv[sys.argv.index("--vuelca") + 1])
        carpeta.mkdir(parents=True, exist_ok=True)
        for i, (b, real) in enumerate(zip(todos, salidas), 1):
            (carpeta / f"bloque-{i:02d}-s{b['sesion']}.txt").write_text(f"# {b['titulo']}\n{real}", encoding="utf-8")
    fallos, cifras = [], 0
    for i, (b, real) in enumerate(zip(todos, salidas)):
        anunciado = [l for l in b["codigo"].splitlines() if l.lstrip().startswith("#>")]
        txt_anun = "\n".join(anunciado)
        # 1 · lo anunciado tiene que estar en la salida real
        for l in anunciado:
            cuerpo = l.lstrip()[2:]
            for n in NUM.findall(cuerpo):
                cifras += 1
                if n not in NUM.findall(real) and n.lstrip("-") not in real:
                    fallos.append(f"sesión {b['sesion']} · «{b['titulo'][:45]}»: {n} (en «{cuerpo.strip()[:50]}») no aparece en la salida real")
            for w in PALABRA.findall(cuerpo):
                if w not in real:
                    fallos.append(f"sesión {b['sesion']} · «{b['titulo'][:45]}»: la palabra «{w}» no aparece en la salida real")
        # 2 · lo que la salida real trae con cifras tiene que estar anunciado
        for l in real.splitlines():
            ll = l.strip()
            if not ll or ll.startswith(("Aviso", "Warning", "In ", "Loading")):
                continue
            for n in NUM.findall(ll):
                if n not in txt_anun:
                    fallos.append(f"sesión {b['sesion']} · «{b['titulo'][:45]}»: la salida real trae {n} («{ll[:50]}») y la diapositiva no lo anuncia")
        # 3 · la salida anunciada es la literal de R: mismas líneas y la misma alineación (el ojo ve la forma, no solo los números)
        real_lineas = [l.rstrip() for l in real.splitlines() if l.strip()]
        esperado = []
        for l in anunciado:
            resto = l.lstrip()[2:].rstrip()
            esperado.append(resto[1:] if resto[:1] == " " else resto)
        if esperado != real_lineas:
            k = next((j for j in range(max(len(esperado), len(real_lineas)))
                      if (esperado[j] if j < len(esperado) else None) != (real_lineas[j] if j < len(real_lineas) else None)), 0)
            e_k = esperado[k] if k < len(esperado) else "(no hay línea)"
            r_k = real_lineas[k] if k < len(real_lineas) else "(no hay línea)"
            fallos.append(f"sesión {b['sesion']} · «{b['titulo'][:45]}»: la salida anunciada no es la literal de R (línea {k + 1}: «{e_k}» contra «{r_k}»)")
        print(f"bloque {i + 1}/{len(todos)} · sesión {b['sesion']} · «{b['titulo'][:50]}» · {len(anunciado)} líneas `#>`")
    for b in raros:
        fallos.append(f"sesión {b['sesion']} · «{b['titulo'][:45]}»: la etiqueta de lenguaje «{b['lenguaje_raro']}» no se reconoce: el bloque NO se ejecutó (¿es ```r?)")
    print(f"\n{len(todos)} bloques de R ejecutados · {cifras} cifras anunciadas")
    if fallos:
        print(f"\n{len(fallos)} PROBLEMAS:")
        for f in dict.fromkeys(fallos):
            print("  ✗", f)
        return 1
    print("✓ todas las cifras anunciadas aparecen en la salida real, y toda cifra de la salida está anunciada")
    return 0


if __name__ == "__main__":
    sys.exit(main())
