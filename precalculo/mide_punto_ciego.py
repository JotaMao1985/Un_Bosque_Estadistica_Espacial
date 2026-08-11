#!/usr/bin/env python3
"""
mide_punto_ciego.py — cuánto NO protege el auditor de prosa, medido

Material de Estadística Espacial 2026-II (20929). T0.5.

EL PROBLEMA. `audita_texto_base.py` indexa, además de las cifras del
precálculo, las **razones y los excesos porcentuales entre ellas**. Sin
eso habría cientos de falsos positivos —el material compara todo el
rato— pero el conjunto de «conocidos» se infla hasta cientos de miles de
cadenas, y entonces una cifra inventada puede caer dentro por puro azar.

`prueba_texto.py` demuestra que el auditor caza los defectos que se le
inyectan. Lo que NO puede demostrar es qué defectos no se le inyectaron
porque no se le ocurrieron a nadie. Este guion mide justo eso: **la
probabilidad de que una cifra falsa se cuele**, por número de decimales.

En Diseño de Experimentos la medición dio, para dos decimales, entre un
30 % y un 91 % de cifras absorbidas según el capítulo. O sea: **una cifra
de dos decimales inventada tenía nueve posibilidades de cada diez de
colarse.** Eso no es un fallo del auditor, es su diseño, y la respuesta
correcta no es apretarlo a ciegas —se llenaría de falsos positivos— sino
saber dónde está el borde.

LA DECISIÓN QUE SALE DE AQUÍ (T0.5, aprobada por Javier): **toda cifra de
la que el texto argumenta se publica con CINCO decimales.** Javier fijó el
listón ahí el 2026-08-03; el borrador de esta tarea proponía cuatro. Es lo
que hace que el 100 % de `prueba_texto.py` signifique algo.

DOS MEDICIONES, PORQUE MIDEN COSAS DISTINTAS

  A. **Cifras al azar** en el recorrido de las del material. Es la cota
     optimista: mide cuán poblado está el conjunto.
  B. **Perturbaciones de un dígito de las cifras REALMENTE publicadas.**
     Es el modo de fallo de verdad —una errata, un número mal recordado—
     y es la cifra que hay que mirar.

Uso:  python3 precalculo/mide_punto_ciego.py
No devuelve error: es una medición, no una comprobación.
"""
from __future__ import annotations

import random
import sys

from audita_texto_base import Auditor
# La MISMA lista de estructurales que usa el auditor de verdad. Importarla
# en vez de construir un Auditor pelado no es un detalle: sin ella la
# medición contaba como «cifra peor protegida» el 4.0 de «CC BY 4.0» y el
# 0.5 de «T0.5». Medir con una configuración distinta de la que se audita
# es medir otra cosa.
from audita_texto_demo import ESTRUCTURALES

SEMILLA = 2026
N = 4000
DECIMALES = [1, 2, 3, 4, 5, 6]


def esta(conocidos: set[str], s: str) -> bool:
    return s in conocidos or s.rstrip("0").rstrip(".") in conocidos


def main() -> int:
    a = Auditor(capitulo="prueba-auditoria.html", var_entorno="DEMO_HTML",
                jsons=["demo_auditoria.json"], estructurales=ESTRUCTURALES)
    conocidos = a.conocidos
    rng = random.Random(SEMILLA)

    print("\n=== mide_punto_ciego.py ===")
    print(f"capítulo   : {a.ruta.name}")
    print(f"conjunto   : {len(conocidos):,} cadenas conocidas".replace(",", " "))
    print(f"prosa      : {len(a.crudos)} cifras leídas")
    print(f"semilla    : {SEMILLA} · {N} sorteos por celda\n")

    # El recorrido sobre el que se sortea sale de las propias cifras del
    # material: sortear en [0, 1] cuando el material publica áreas de
    # 1 600 km² daría una absorción irreal.
    publicadas = []
    for c in a.crudos:
        try:
            publicadas.append(abs(float(c.replace(",", "."))))
        except ValueError:
            pass
    publicadas = [v for v in publicadas if v > 0]
    lo, hi = min(publicadas), max(publicadas)

    print("A · cifras AL AZAR en el recorrido del material "
          f"[{lo:.4g}, {hi:.4g}]")
    print("    decimales   absorbidas por el conjunto")
    for d in DECIMALES:
        golpes = sum(esta(conocidos, f"{rng.uniform(lo, hi):.{d}f}")
                     for _ in range(N))
        print(f"    {d:>9}   {100*golpes/N:>6.2f} %")

    print("\nB · PERTURBACIÓN DE UN DÍGITO de las cifras ya publicadas")
    print("    (el modo de fallo de verdad: la errata, el número mal recordado)")
    print()
    print("    Se agrupan por los decimales que la cifra tiene EN EL TEXTO, no")
    print("    por un formato impuesto: rellenar «33» hasta «33.0000» y perturbar")
    print("    sus ceros no es una errata que nadie vaya a cometer, y medirlo así")
    print("    daba un 15,8 % de absorción a cuatro decimales que no significaba")
    print("    nada. Una métrica ciega falla en las dos direcciones (A.5).")
    print()
    print("    decimales   se cuelan   perturbaciones   cifras")
    por_dec: dict[int, list[str]] = {}
    for c in a.crudos:
        s = c.replace(",", ".")
        if "." not in s or s in a.estructurales:
            continue
        por_dec.setdefault(len(s.split(".")[1]), []).append(s)

    flojas: list[tuple[str, int, int]] = []
    for d in sorted(por_dec):
        pruebas = colados = 0
        for s in por_dec[d]:
            entero, _, dec = s.partition(".")
            n_s = n_col = 0
            for pos in range(len(dec)):
                for delta in (-1, 1):
                    nuevo = int(dec[pos]) + delta
                    if not 0 <= nuevo <= 9:
                        continue
                    n_s += 1
                    n_col += esta(
                        conocidos, f"{entero}.{dec[:pos]}{nuevo}{dec[pos+1:]}")
            pruebas += n_s
            colados += n_col
            if n_col:
                flojas.append((s, n_col, n_s))
        if pruebas:
            print(f"    {d:>9}   {100*colados/pruebas:>7.2f} %   {pruebas:>14}"
                  f"   {len(por_dec[d]):>6}")

    # Una medición sin destinatario no sirve de nada: éstas son las cifras
    # CONCRETAS del capítulo que el auditor protege peor, y son las que
    # `prueba_texto.py` debería estar inyectando.
    if flojas:
        flojas.sort(key=lambda x: -x[1] / x[2])
        print(f"\n    Las {min(10, len(flojas))} cifras peor protegidas de este "
              f"capítulo ({len(flojas)} en total):")
        for s, col, tot in flojas[:10]:
            print(f"      {s:<16} {col} de {tot} perturbaciones se colarían")

    print("\n  Lectura: la fila de 5 decimales es la que sostiene la regla de")
    print("  publicación de T0.5. Por debajo de ella el auditor protege peor, y")
    print("  el material lo sabe en vez de suponerlo.\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
