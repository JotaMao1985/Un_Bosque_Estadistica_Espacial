#!/usr/bin/env python3
"""
verifica_bloques.py — ejecuta los bloques de código y contrasta sus `#>`

Material de Estadística Espacial 2026-II (20929). Portado de Diseño de
Experimentos en T0.5, con cuatro cambios que aquí no son opcionales.

QUÉ HACE
  1. Extrae los bloques `language-r` y `language-python` del HTML, en
     orden de aparición.
  2. Los ejecuta ENCADENADOS —todos los de R en una sesión, todos los de
     Python en otra—, porque así los ejecutaría un estudiante que sigue
     el capítulo de arriba abajo: si un bloque usa un objeto que nunca se
     definió, se ve aquí.
  3. Para cada bloque, extrae los números de sus líneas `#>` y comprueba
     que aparezcan en la salida real de ESE bloque.

Los comentarios `#>` son la mayor fuente de errores de este material: son
plausibles, nadie los ejecuta y acaban publicados. En Series de Tiempo
este guion cazó 11 de 22 en un solo capítulo.

QUÉ CAMBIA RESPECTO A LA VERSIÓN DE DISEÑO DE EXPERIMENTOS

  · **El intérprete de R.** Allí bastaba `Rscript`. Aquí el `Rscript` del
    PATH es Homebrew 4.6.0 y **no tiene `sf`**: verificar con él daría un
    fallo masivo que no es del material. Se usa `precalculo/rscript.sh`,
    que además arranca en UTF-8 (ver `utf8.R`).

  · **El intérprete de Python.** No es `python3` a secas: es el del
    entorno `geo_env`, el único con geopandas y PySAL. La ruta se lee de
    `versiones_py.json`, no se cablea.

  · **El directorio de trabajo es la carpeta del curso**, no
    `precalculo/`. Los bloques de los capítulos leen `datos/procesado/…`
    y `precalculo/salidas/…`, que es lo que un estudiante tendría
    delante.

  · **Un capítulo sin ninguna línea `#>` es un FALLO, no un aprobado.**
    La versión de DOE habría informado «0 de 0 cifras» en verde sobre la
    plantilla de este curso, que tiene cinco bloques y cero `#>`. Un
    verificador que sale limpio porque no había nada que comprobar es
    exactamente la falsa calma que T0.5 existe para impedir.

Uso:
    python3 precalculo/verifica_bloques.py --html Htmls_Espacial/prueba-auditoria.html
    python3 precalculo/verifica_bloques.py --todos
Devuelve 1 si alguna cifra anunciada no aparece en la salida real.
"""
from __future__ import annotations

import argparse
import html as html_mod
import json
import os
import re
import subprocess
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent
# `Htmls_Espacial/` mientras se escribe; `sitio/estadistica-espacial/`
# cuando la Fase 7 publique. Se busca en las dos y se avisa de cuál se usó.
FUENTES = [RAIZ / "sitio" / "estadistica-espacial", RAIZ / "Htmls_Espacial"]
TMP = Path(os.environ.get("TMPDIR", "/tmp")) / "verifica_espacial"

SEP = "###BLOQUE-%d###"
BLOQUE_RE = re.compile(
    r'<pre><code class="language-(r|python)">(.*?)</code></pre>', re.S)
# Números con signo, decimales y notación científica; `1e-13` incluido.
NUM_RE = re.compile(r'-?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?')

RSCRIPT = AQUI / "rscript.sh"


def python_geo() -> str:
    """El intérprete del entorno geo_env, tal como lo congeló T0.1."""
    f = AQUI / "versiones_py.json"
    if not f.exists():
        sys.exit(f"PARADO: falta {f}. Ejecuta antes precalculo/entorno.py")
    ruta = json.loads(f.read_text(encoding="utf-8"))["ejecutable"]
    if not Path(ruta).exists():
        sys.exit(f"PARADO: versiones_py.json apunta a {ruta}, que no existe")
    return ruta


def extrae(textos):
    bloques = []
    for nombre, texto in textos:
        for lang, cuerpo in BLOQUE_RE.findall(texto):
            bloques.append({
                "archivo": nombre,
                "lang": lang,
                "codigo": html_mod.unescape(cuerpo),
            })
    return bloques


def esperados(codigo):
    """Números anunciados en las líneas `#>` del bloque."""
    fuera = []
    for linea in codigo.splitlines():
        s = linea.strip()
        marca = "#>" if s.startswith("#>") else ("#&gt;" if s.startswith("#&gt;") else None)
        if marca is None:
            continue
        fuera.extend(NUM_RE.findall(s[len(marca):]))
    return fuera


def limpia(codigo):
    """El código sin sus líneas `#>`, que es lo que de verdad se ejecuta."""
    return "\n".join(l for l in codigo.splitlines()
                     if not l.strip().startswith(("#>", "#&gt;")))


def corre(bloques, lang, cabecera, comando, sufijo, sep_fmt):
    idx = [i for i, b in enumerate(bloques) if b["lang"] == lang]
    if not idx:
        return {}
    TMP.mkdir(parents=True, exist_ok=True)
    partes = [cabecera]
    for k, i in enumerate(idx):
        partes.append(sep_fmt % k)
        partes.append(limpia(bloques[i]["codigo"]))
    ruta = TMP / f"bloques{sufijo}"
    ruta.write_text("\n\n".join(partes), encoding="utf-8")

    # cwd = la carpeta del curso: es desde donde los bloques resuelven
    # `datos/procesado/...`, igual que lo haría un estudiante.
    res = subprocess.run(comando + [str(ruta)], capture_output=True, text=True,
                         cwd=str(RAIZ), timeout=3600)
    salida = res.stdout + "\n" + res.stderr
    trozos = {}
    partes_salida = re.split(r"###BLOQUE-(\d+)###", salida)
    # partes_salida = [preludio, '0', texto0, '1', texto1, ...]
    for j in range(1, len(partes_salida) - 1, 2):
        trozos[idx[int(partes_salida[j])]] = partes_salida[j + 1]
    return {"trozos": trozos, "codigo_salida": res.returncode, "todo": salida,
            "guion": ruta}


def capitulos():
    for d in FUENTES:
        rutas = sorted(d.glob("*.html"))
        if rutas:
            return d, rutas
    return None, []


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--html", default=None, help="HTML a verificar")
    ap.add_argument("--todos", action="store_true",
                    help="verifica todos los .html publicados")
    args = ap.parse_args()

    if args.html:
        p = Path(args.html)
        if not p.is_absolute():
            p = RAIZ / p
        if not p.exists():
            raise SystemExit(f"ABORTA: no existe {p}")
        textos = [(p.name, p.read_text(encoding="utf-8"))]
    elif args.todos:
        d, rutas = capitulos()
        if not rutas:
            raise SystemExit(f"ABORTA: no hay .html en {[str(x) for x in FUENTES]}")
        print(f"Fuente: {d.relative_to(RAIZ)}")
        textos = [(p.name, p.read_text(encoding="utf-8")) for p in rutas]
    else:
        raise SystemExit("ABORTA: indica --html <ruta> o --todos")

    bloques = extrae(textos)
    n_r = sum(b["lang"] == "r" for b in bloques)
    n_py = sum(b["lang"] == "python" for b in bloques)
    n_anunciadas = sum(len(esperados(b["codigo"])) for b in bloques)
    print(f"Bloques encontrados: {n_r} de R, {n_py} de Python · "
          f"{n_anunciadas} cifras anunciadas\n")

    # La guarda que la versión de DOE no tenía. Sin ella este guion sale
    # en verde sobre cualquier documento que no anuncie nada, y el verde
    # se lee como «comprobado».
    if not bloques:
        print("!! ABORTA: el documento no tiene ningún bloque de código.")
        return 1
    if n_anunciadas == 0:
        print("!! ABORTA: hay bloques de código pero NINGUNA línea `#>`.")
        print("   No hay nada que contrastar, así que este guion no puede")
        print("   decir que el capítulo esté bien. Un 0 de 0 en verde es")
        print("   una mentira por omisión.")
        return 1

    resultados = {}
    # Los paquetes del curso, precargados. Si un bloque se olvida de su
    # `library()`, eso lo caza la revisión de autonomía del capítulo, no
    # este guion: aquí interesa que las CIFRAS cuadren.
    resultados["r"] = corre(
        bloques, "r",
        'suppressMessages({library(sf); library(sp); library(spdep);\n'
        '  library(spatialreg); library(gstat); library(spatstat);\n'
        '  library(spData); library(classInt); library(jsonlite)})\n'
        'options(warn = 1)',
        [str(RSCRIPT), "--vanilla"], ".R", 'cat("\\n' + SEP + '\\n")')
    resultados["python"] = corre(
        bloques, "python",
        "import warnings; warnings.filterwarnings('ignore')",
        [python_geo()], ".py", 'print("\\n' + SEP + '\\n")')

    total_ok = total = 0
    fallos = []
    for i, b in enumerate(bloques):
        r = resultados[b["lang"]]
        if not r:
            continue
        salida = r["trozos"].get(i, "")
        esp = esperados(b["codigo"])
        vistos = set(NUM_RE.findall(salida))
        faltan = []
        for e in esp:
            total += 1
            if e in vistos or e in salida:
                total_ok += 1
            else:
                faltan.append(e)
        if faltan:
            fallos.append((i, b, faltan, salida))

    for i, b, faltan, salida in fallos:
        primera = next((l for l in b["codigo"].splitlines() if l.strip()), "")
        print(f"--- bloque #{i} ({b['lang']}, {b['archivo']}) ---")
        print(f"    empieza por: {primera.strip()[:78]}")
        print(f"    NO aparecen en la salida: {faltan}")
        print("    salida real:")
        for l in salida.strip().splitlines()[:22]:
            print("      " + l)
        print()

    roto = False
    for lang in ("r", "python"):
        r = resultados[lang]
        if r and r["codigo_salida"] != 0:
            roto = True
            print(f"!! la sesión de {lang} terminó con código {r['codigo_salida']}"
                  f"  ({r['guion']})")
            print("\n".join(r["todo"].strip().splitlines()[-25:]))

    print(f"\n=== {total_ok} de {total} cifras anunciadas aparecen en la salida real "
          f"({len(fallos)} bloques con discrepancias) ===")
    return 0 if (total_ok == total and not roto) else 1


if __name__ == "__main__":
    sys.exit(main())
