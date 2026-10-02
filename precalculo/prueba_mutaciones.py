#!/usr/bin/env python3
"""
prueba_mutaciones.py — ¿SABE FALLAR la prueba de una animación?

Material de Estadística Espacial 2026-II (20929).

POR QUÉ EXISTE. Una prueba que nunca ha fallado puede estar bien escrita o puede ser
incapaz de fallar, y desde fuera las dos se ven igual. `prueba_texto.py` lo resuelve para
los capítulos (inyecta un defecto en una copia del HTML y exige que el auditor lo cace);
las animaciones tenían la mitad del arnés —`prueba_nucleo3d.py` lee la variable
`NUCLEO3D_MOTOR` «para comprobar que la prueba sabe fallar»— pero nadie fabricaba las copias
mutadas, así que la comprobación existía en el papel. Este archivo la ejecuta.

CÓMO. Para cada sujeto: (1) CONTROL, la copia sin tocar tiene que pasar; (2) cada DEFECTO es
un par «buscar → poner» sobre el código fuente, que se aplica a una copia y se redirige a la
prueba por la variable de entorno del sujeto; la prueba tiene que salir con error; (3) CONTROL
FINAL, el original sigue limpio. Un defecto cuyo texto «buscar» no aparece EXACTAMENTE una vez
no se aplica y cuenta como fallo: con una ancla ambigua se estaría mutando otra cosa.

Los defectos son los errores que de verdad se cometen al escribir esta matemática (una constante
mal puesta, dividir en el punto equivocado, olvidar los medios pesos del borde), no mutaciones
al azar. Cada uno lleva el nombre de lo que rompería.

    python3 precalculo/prueba_mutaciones.py             # todos los sujetos
    python3 precalculo/prueba_mutaciones.py nucleo3d    # uno
"""
from __future__ import annotations

import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent

# ---------------------------------------------------------------------------------------------
# Los defectos del motor 3D (`precalculo/nucleo3d/nucleo3d.js`): (nombre, buscar, poner).
# ---------------------------------------------------------------------------------------------
DEFECTOS_NUCLEO3D = [
    # --- el módulo 1: los núcleos y el test de cuadrantes ---
    ("el soporte del Epanechnikov es √5σ y no √6σ",
     "const H2 = { epanechnikov: 6, quartic: 8, disc: 4 };",
     "const H2 = { epanechnikov: 5, quartic: 8, disc: 4 };"),
    ("el Epanechnikov no está normalizado",
     "return r2 < h2 ? 2 / (Math.PI * h2) * (1 - r2 / h2) : 0; },\n      masa:",
     "return r2 < h2 ? 1 / (Math.PI * h2) * (1 - r2 / h2) : 0; },\n      masa:"),
    ("el punto sobre una línea de la rejilla va a la celda de la derecha (intervalos [a, b) y no (a, b])",
     "const dentro = (v, a, b, primera) => (primera ? v >= a : v > a) && v <= b;",
     "const dentro = (v, a, b, primera) => v >= a && (primera ? v <= b : v < b);"),
    # --- el módulo 4: e(u), las tres superficies y sus masas ---
    ("e vale 1: no hay corrección",
     "return t / DIRECCIONES;",
     "return 1;"),
    ("la distancia al lado izquierdo se mide hacia el derecho",
     "const tx = c > 0 ? (V - x) / c : (-V - x) / c;",
     "const tx = c > 0 ? (V - x) / c : (V - x) / c;"),
    ("la masa del gaussiano usa 1/σ² en vez de 1/(2σ²)",
     "masa: (R, s) => 1 - Math.exp(-R * R / (2 * s * s))",
     "masa: (R, s) => 1 - Math.exp(-R * R / (s * s))"),
    ("la masa del disco no se detiene en 1",
     "masa: (R, s) => Math.min(1, R * R / (H2.disc * s * s))",
     "masa: (R, s) => R * R / (H2.disc * s * s)"),
    ("la masa del cuártico usa el soporte del Epanechnikov",
     "const q = Math.min(1, R * R / (H2.quartic * s * s));",
     "const q = Math.min(1, R * R / (H2.epanechnikov * s * s));"),
    ("la división por e(u) se le aplica a Diggle y no a la corrección por defecto",
     "if (modo === 'defecto') t /= eMalla[j * n + i];",
     "if (modo === 'diggle') t /= eMalla[j * n + i];"),
    ("la corrección por defecto multiplica por e en vez de dividir",
     "if (modo === 'defecto') t /= eMalla[j * n + i];",
     "if (modo === 'defecto') t *= eMalla[j * n + i];"),
    ("la integral por defecto olvida los medios pesos del borde",
     "wj = j === 0 || j === n - 1 ? 0.5 : 1;",
     "wj = 1;"),
    ("la masa sin corregir de cada punto es 1",
     "({ sin: ePts[q], defecto: defecto[q], diggle: 1 })",
     "({ sin: 1, defecto: defecto[q], diggle: 1 })"),
    ("e se calcula en un cuadrante y no se copia a las demás esquinas",
     "salida[(n - 1 - j) * n + i] = v;",
     "salida[(n - 1 - j) * n + i] = 1;"),
    ("e se integra con 36 direcciones y no con 360",
     "const DIRECCIONES = 360;",
     "const DIRECCIONES = 36;"),
    # --- hallados por la revisión independiente (2026-10-01): la prueba solo comparaba SUMAS, y las barras y la lectura
    #     «la sede aporta» de cada sede salen de `por[q]` ---
    ("lo que aporta cada sede se acumula siempre en la primera",
     "defecto[q] += w * k(dx * dx + dy * dy, s);",
     "defecto[0] += w * k(dx * dx + dy * dy, s);"),
    ("las sedes salen en orden inverso en el desglose",
     "defecto: defecto[q], diggle: 1 })",
     "defecto: defecto[pts.length - 1 - q], diggle: 1 })"),
    ("el techo de la cámara ignora las superficies corregidas",
     "techo = Math.max(techo, base.alto * superficieBorde(nuc, pts, sg.min, n, modo, eM, ePts, tmp));",
     "techo = Math.max(techo, 0);"),
    ("las escalas de la escena «borde» usan el rango de σ del módulo 1",
     "const base = escalas(pts, sg), n = 61,",
     "const base = escalas(pts), n = 61,"),
]

# ---------------------------------------------------------------------------------------------
# Los sujetos. `entorno` es la variable con la que la prueba redirige el código a una copia.
# ---------------------------------------------------------------------------------------------
SUJETOS = {
    "nucleo3d": dict(
        fuente=RAIZ / "precalculo" / "nucleo3d" / "nucleo3d.js",
        entorno="NUCLEO3D_MOTOR",
        orden=[sys.executable, str(RAIZ / "precalculo" / "prueba_nucleo3d.py")],
        defectos=DEFECTOS_NUCLEO3D,
    ),
}


def corre(sujeto: dict, copia: Path) -> tuple[int, str]:
    """Corre la prueba del sujeto contra la copia."""
    entorno = dict(os.environ, **{sujeto["entorno"]: str(copia)})
    r = subprocess.run(sujeto["orden"], capture_output=True, text=True, cwd=str(RAIZ), env=entorno)
    return r.returncode, r.stdout + r.stderr


def primer_fallo(salida: str) -> str:
    """La primera comprobación que dijo MAL: qué bloque cazó el defecto."""
    for linea in salida.splitlines():
        if re.match(r"\s*MAL\s", linea):
            return re.sub(r"\s+", " ", linea.strip())[:118]
    return "(salió con error sin una línea MAL)"


def prueba(clave: str) -> tuple[int, int]:
    """Devuelve (defectos cazados, defectos inyectados). Un control que falla devuelve (0, n)."""
    sujeto = SUJETOS[clave]
    fuente: Path = sujeto["fuente"]
    defectos = sujeto["defectos"]
    print(f"\n--- {clave} ({fuente.relative_to(RAIZ)}) " + "-" * 20)
    original = fuente.read_text(encoding="utf-8")
    with tempfile.TemporaryDirectory(prefix=f"mutaciones_{clave}_") as tmp:
        copia = Path(tmp) / fuente.name

        copia.write_text(original, encoding="utf-8")
        codigo, salida = corre(sujeto, copia)
        print(f"  {'OK ' if codigo == 0 else 'MAL'}  control · sin inyectar nada")
        if codigo != 0:
            print("  PARADO: el control falla, así que el arnés no prueba nada.")
            print("        " + primer_fallo(salida))
            return 0, len(defectos)

        cazados = 0
        for nombre, busca, pone in defectos:
            veces = original.count(busca)
            if veces != 1:
                print(f"  MAL  {nombre}")
                print(f"        el texto a sustituir aparece {veces} veces (tiene que ser 1): {busca[:70]!r}")
                continue
            copia.write_text(original.replace(busca, pone, 1), encoding="utf-8")
            codigo, salida = corre(sujeto, copia)
            caza = codigo != 0
            cazados += caza
            print(f"  {'OK ' if caza else 'MAL'}  {nombre}")
            print(f"        {primer_fallo(salida) if caza else 'LA PRUEBA NO LO NOTÓ'}")

        copia.write_text(original, encoding="utf-8")
        codigo, salida = corre(sujeto, copia)
        print(f"  {'OK ' if codigo == 0 else 'MAL'}  control final · el original sigue limpio")
        if codigo != 0:
            return 0, len(defectos)
    return cazados, len(defectos)


def main() -> int:
    claves = sys.argv[1:] or list(SUJETOS)
    desconocidos = [c for c in claves if c not in SUJETOS]
    if desconocidos:
        sys.exit(f"sujeto desconocido: {desconocidos}; hay: {list(SUJETOS)}")
    print("\n=== prueba_mutaciones.py ===")
    mal = 0
    for clave in claves:
        cazados, total = prueba(clave)
        print(f"\n  {clave}: {cazados} de {total} defectos cazados")
        mal += total - cazados
    print()
    if mal:
        print(f"  {mal} defecto(s) sin cazar: la prueba correspondiente NO sabe fallar ahí.")
        return 1
    print("  Todos los defectos inyectados fueron cazados.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
