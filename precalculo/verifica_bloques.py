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
  3. Para cada bloque, extrae los números de sus líneas `#>` —y los
     lógicos y las cadenas entre comillas— y comprueba que aparezcan en la
     salida real de ESE bloque.

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

LA PRUEBA DESDE FUERA (`--fuera`, R3 · T3.5 del capítulo 1)

  La corrida normal se hace en la carpeta del curso, con `datos/` y
  `precalculo/` a mano: comprueba las CIFRAS, no que un estudiante pueda
  ejecutar el bloque. `--fuera` comprueba eso otro. Copia `entrega/datos/`
  —lo único que se publica de datos— a un directorio temporal FUERA del
  repositorio, y ejecuta allí CADA bloque en su propio proceso, sin la
  precarga de paquetes de arriba y sin la sesión encadenada: así lo hace
  quien copia un bloque desde la página. Un bloque que lea `datos/`,
  `precalculo/` o un objeto de otro bloque, o que se olvide de su
  `library()`, falla aquí aunque sus cifras sean buenas. Con `--rlib` y
  `--python` se corre contra una biblioteca de R o un intérprete recién
  instalados, que es como se prueba la orden de instalación del módulo 8.

Uso:
    python3 precalculo/verifica_bloques.py --html Htmls_Espacial/prueba-auditoria.html
    python3 precalculo/verifica_bloques.py --todos
    python3 precalculo/verifica_bloques.py --html Htmls_Espacial/capitulo-1-datos-espaciales.html --fuera
Devuelve 1 si alguna cifra anunciada no aparece en la salida real.
"""
from __future__ import annotations

import argparse
import html as html_mod
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent
# `Htmls_Espacial/` mientras se escribe; `sitio/estadistica-espacial/`
# cuando la Fase 7 publique. Se busca en las dos y se avisa de cuál se usó.
FUENTES = [RAIZ / "sitio" / "estadistica-espacial", RAIZ / "Htmls_Espacial"]
# Cada corrida escribe sus guiones en una carpeta PROPIA. Con una ruta fija
# (`$TMPDIR/verifica_espacial`) dos checkouts que verifican a la vez se
# pisaban el guion: el 2026-09-25 un worktree ejecutó el `bloques.R` que
# otro acababa de escribir con el capítulo 5 anterior a M3, y el paso salió
# en rojo por cifras que su propio HTML sí anunciaba y su código sí daba.

SEP = "###BLOQUE-%d###"
# La clase admite algo DESPUÉS del lenguaje, y eso no es laxitud: es lo
# que permite marcar un bloque como `arranque`. Con el patrón cerrado
# —`class="language-r"` exacto— un bloque con una segunda clase quedaba
# INVISIBLE para este guion, que es la peor de las opciones: ni se
# ejecuta, ni se cuenta, ni se dice. Ahora se ve, se cuenta y se declara.
BLOQUE_RE = re.compile(
    r'<pre><code class="language-(r|python)([^"]*)">(.*?)</code></pre>', re.S)
# Números con signo, decimales y notación científica; `1e-13` incluido.
NUM_RE = re.compile(r'-?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?')
# Los lógicos y las cadenas entre comillas de las líneas `#>`. Solo con
# números, `#> [1] TRUE` y `#> [1] FALSE` daban la misma lista —el «1» del
# índice—, y la línea que comprueba un resultado, que es la que más importa,
# pasaba en verde aunque diera lo contrario (revisión del preparcial del
# Corte II, ronda 6). Se buscan como palabra entera en la salida del bloque.
PALABRA_RE = re.compile(r'\b(TRUE|FALSE|True|False|NULL)\b|("[^"\n]*")')

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
        for lang, extra, cuerpo in BLOQUE_RE.findall(texto):
            bloques.append({
                "archivo": nombre,
                "lang": lang,
                # Un bloque de ARRANQUE es código que el lector va a
                # ejecutar sobre SUS datos: lleva marcadores en vez de
                # valores (`TU_LLAVE`, `TUS_40`) y no anuncia salida,
                # porque no hay una salida única que anunciar. Ejecutarlo
                # aquí daría un error que no es del material, y además
                # envenenaría la sesión encadenada de los capítulos.
                # Nace con el Taller 1; ver PLAN_Taller_1_Caps_1_2.md.
                "arranque": "arranque" in extra,
                "codigo": html_mod.unescape(cuerpo),
            })
    return bloques


def esperados(codigo):
    """Números anunciados en las líneas `#>` del bloque, y después sus lógicos
    y sus cadenas entre comillas (sin los números que lleven dentro, que ya
    se cuentan como cadena)."""
    fuera = []
    for linea in codigo.splitlines():
        s = linea.strip()
        marca = "#>" if s.startswith("#>") else ("#&gt;" if s.startswith("#&gt;") else None)
        if marca is None:
            continue
        resto = s[len(marca):]
        palabras = [m.group(0) for m in PALABRA_RE.finditer(resto)]
        fuera.extend(NUM_RE.findall(PALABRA_RE.sub(" ", resto)))
        fuera.extend(palabras)
    return fuera


def aparece(e, salida, vistos):
    """Un número, entre los de la salida o dentro de ella; un lógico, como
    palabra entera; una cadena, con sus comillas."""
    if e.startswith('"'):
        return e in salida
    if e in ("TRUE", "FALSE", "True", "False", "NULL"):
        return re.search(r"\b" + e + r"\b", salida) is not None
    return e in vistos or e in salida


def limpia(codigo):
    """El código sin sus líneas `#>`, que es lo que de verdad se ejecuta."""
    return "\n".join(l for l in codigo.splitlines()
                     if not l.strip().startswith(("#>", "#&gt;")))


def corre(bloques, lang, cabecera, comando, sufijo, sep_fmt):
    idx = [i for i, b in enumerate(bloques) if b["lang"] == lang]
    if not idx:
        return {}
    tmp = Path(tempfile.mkdtemp(prefix="verifica_bloques_"))
    partes = [cabecera]
    for k, i in enumerate(idx):
        partes.append(sep_fmt % k)
        partes.append(limpia(bloques[i]["codigo"]))
    ruta = tmp / f"bloques{sufijo}"
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


def enlazados(textos):
    """Los archivos de `entrega/datos/` que el documento ENLAZA para descargar."""
    rutas = set()
    for _, texto in textos:
        rutas |= set(re.findall(r'href="\.\./(entrega/datos/[^"]+)"', texto))
    return sorted(rutas)


def corre_fuera(bloques, rlib=None, python=None, archivos=()):
    """Cada bloque, solo, en un temporal que solo tiene lo que el documento
    enlaza de `entrega/datos/` (ronda 2: antes se copiaba la carpeta entera, y
    un bloque que leyera un archivo de otro taller no se habría notado)."""
    fuera = Path(tempfile.mkdtemp(prefix="verifica_fuera_"))
    (fuera / "entrega" / "datos").mkdir(parents=True)
    for ruta in archivos:
        shutil.copy2(RAIZ / ruta, fuera / ruta)
    print(f"Directorio de trabajo: {fuera}")
    print(f"  contiene solo los {len(archivos)} archivos que el documento enlaza: "
          f"{', '.join(Path(r).name for r in archivos)}")
    entorno = dict(os.environ)
    if rlib:
        # Una biblioteca de R recién instalada: la única que se ve, además de
        # la de base del propio R.
        entorno["R_LIBS_USER"] = entorno["R_LIBS_SITE"] = str(Path(rlib).resolve())
    py = python or python_geo()
    salidas = {}
    for i, b in enumerate(bloques):
        sufijo = ".R" if b["lang"] == "r" else ".py"
        guion = fuera / f"bloque_{i:02d}{sufijo}"
        guion.write_text(("options(warn = 1)\n" if b["lang"] == "r" else "")
                         + limpia(b["codigo"]) + "\n", encoding="utf-8")
        cmd = ([str(RSCRIPT), "--vanilla"] if b["lang"] == "r" else [py]) + [guion.name]
        res = subprocess.run(cmd, capture_output=True, text=True, cwd=str(fuera),
                             env=entorno, timeout=3600)
        salidas[i] = (res.returncode, res.stdout + "\n" + res.stderr)
    return fuera, salidas


def lineas_anunciadas(codigo):
    """Las líneas `#>` del bloque, sin la marca: lo que el bloque promete escribir."""
    fuera = []
    for linea in codigo.splitlines():
        s = linea.strip()
        for marca in ("#>", "#&gt;"):
            if s.startswith(marca):
                fuera.append(s[len(marca):].strip())
    return fuera


def main_fuera(bloques, rlib, python, textos):
    ejecutables = [b for b in bloques if not b["arranque"]]
    fuera, salidas = corre_fuera(ejecutables, rlib, python, enlazados(textos))
    total_ok = total = lineas_ok = lineas_total = 0
    malos = 0
    for i, b in enumerate(ejecutables):
        cod, salida = salidas[i]
        esp = esperados(b["codigo"])
        vistos = set(NUM_RE.findall(salida))
        faltan = [e for e in esp if not aparece(e, salida, vistos)]
        # Ronda 2 (V-01): además de los números, la LÍNEA entera, literal. Un
        # «667» anunciado que sale «667.0» pasa por números y no es lo que el
        # estudiante ve en su pantalla.
        hechas = {l.strip() for l in salida.splitlines()}
        prometidas = lineas_anunciadas(b["codigo"])
        no_literal = [f"línea: {l}" for l in prometidas if l not in hechas]
        lineas_total += len(prometidas)
        lineas_ok += len(prometidas) - len(no_literal)
        total += len(esp)
        total_ok += len(esp) - len(faltan)
        n_num = len(esp) - len(faltan)
        faltan += no_literal
        primera = next((l for l in b["codigo"].splitlines() if l.strip()), "").strip()
        estado = "OK  " if cod == 0 and not faltan else "MAL "
        print(f"  {estado} bloque {i:2d} ({b['lang']:6s}) {n_num:3d}/{len(esp):<3d} "
              f"código {cod} · {primera[:60]}")
        if estado == "MAL ":
            malos += 1
            if faltan:
                print(f"         NO aparecen: {faltan}")
            for l in salida.strip().splitlines()[-12:]:
                print("         " + l)
    shutil.rmtree(fuera, ignore_errors=True)
    print(f"\n=== DESDE FUERA: {len(ejecutables) - malos} de {len(ejecutables)} bloques corren solos; "
          f"{total_ok} de {total} cifras, lógicos y cadenas anunciados aparecen; "
          f"{lineas_ok} de {lineas_total} líneas #> salen literales ===")
    return 0 if malos == 0 and total_ok == total and lineas_ok == lineas_total else 1


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
    ap.add_argument("--fuera", action="store_true",
                    help="cada bloque solo, en un temporal con solo entrega/datos/")
    ap.add_argument("--rlib", default=None,
                    help="con --fuera: la biblioteca de R que se usa (instalación limpia)")
    ap.add_argument("--python", default=None,
                    help="con --fuera: el intérprete de Python que se usa (entorno limpio)")
    args = ap.parse_args()
    if args.fuera and not args.html:
        raise SystemExit("ABORTA: --fuera va con --html <capítulo>")

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
    n_arranque = sum(b["arranque"] for b in bloques)
    ejecutables = [b for b in bloques if not b["arranque"]]
    n_anunciadas = sum(len(esperados(b["codigo"])) for b in ejecutables)
    print(f"Bloques encontrados: {n_r} de R, {n_py} de Python · "
          f"{n_anunciadas} cifras anunciadas")
    if n_arranque:
        # Se DICE cuántos se dejan fuera y de qué archivo. Un guion que
        # salta bloques en silencio informa «todo verde» sobre un material
        # que no ha mirado.
        de = sorted({b["archivo"] for b in bloques if b["arranque"]})
        print(f"  {n_arranque} bloque(s) de ARRANQUE, no ejecutados ni "
              f"contrastados: {', '.join(de)}")
    print()

    # La guarda que la versión de DOE no tenía. Sin ella este guion sale
    # en verde sobre cualquier documento que no anuncie nada, y el verde
    # se lee como «comprobado».
    if not bloques:
        print("!! ABORTA: el documento no tiene ningún bloque de código.")
        return 1
    if ejecutables and n_anunciadas == 0:
        print("!! ABORTA: hay bloques de código pero NINGUNA línea `#>`.")
        print("   No hay nada que contrastar, así que este guion no puede")
        print("   decir que el capítulo esté bien. Un 0 de 0 en verde es")
        print("   una mentira por omisión.")
        return 1
    if args.fuera:
        return main_fuera(bloques, args.rlib, args.python, textos)

    resultados = {}
    # Los paquetes del curso, precargados. Si un bloque se olvida de su
    # `library()`, eso lo caza la revisión de autonomía del capítulo, no
    # este guion: aquí interesa que las CIFRAS cuadren.
    resultados["r"] = corre(
        ejecutables, "r",
        'suppressMessages({library(sf); library(sp); library(spdep);\n'
        '  library(spatialreg); library(gstat); library(spatstat);\n'
        '  library(spData); library(classInt); library(jsonlite)})\n'
        'options(warn = 1)',
        [str(RSCRIPT), "--vanilla"], ".R", 'cat("\\n' + SEP + '\\n")')
    resultados["python"] = corre(
        ejecutables, "python",
        "import warnings; warnings.filterwarnings('ignore')",
        [python_geo()], ".py", 'print("\\n' + SEP + '\\n")')

    total_ok = total = 0
    fallos = []
    for i, b in enumerate(ejecutables):
        r = resultados[b["lang"]]
        if not r:
            continue
        salida = r["trozos"].get(i, "")
        esp = esperados(b["codigo"])
        vistos = set(NUM_RE.findall(salida))
        faltan = []
        for e in esp:
            total += 1
            if aparece(e, salida, vistos):
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

    print(f"\n=== {total_ok} de {total} cifras, lógicos y cadenas anunciados aparecen en la salida real "
          f"({len(fallos)} bloques con discrepancias) ===")
    return 0 if (total_ok == total and not roto) else 1


if __name__ == "__main__":
    sys.exit(main())
