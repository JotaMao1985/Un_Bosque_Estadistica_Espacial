#!/usr/bin/env python3
"""
prueba_ensambla_cap7.py — las guardas de «Describir el mapa» saben parar el
ensamblado

Material de Estadística Espacial 2026-II (20929). 2026-11-02.

POR QUÉ EXISTE. Desde esa fecha los once mapas del capítulo 7 llevan una
descripción larga —lo que se VE en ellos, para quien no los ve—, casi todos
una por estado: Columbus o los municipios, la corrección por
multiplicidad, la capa, las once vecindades. `ensambla_cap7.py` comprueba
contra el dato que cada categoría que se nombra es la del mapa, con sus
unidades; que la clase alta y la baja tienen las del mapa; que las parejas y
los puntos rojos de cada vecindad son los que se dibujan; que hay celdas
calientes y frías. Un `MAL` que nadie ha visto salir puede estar bien escrito
o puede ser incapaz de dispararse, y desde fuera se ven igual: es la lección
de T0.5. Aquí cada guarda se rompe a propósito y tiene que parar.

CÓMO. El ensamblador se ejecuta en COPIA, en un directorio temporal, con
`CAP7_DESTINO` fuera de lo publicado (escribe el HTML antes de correr sus
guardas) y con UNA sustitución cada vez. Unos mutantes rompen el texto o el
cableado; otros, el dato que una frase afirma, inyectado justo después de que
el ensamblador lo lea: las dos cosas son lo que la guarda vigila. Cada copia
tiene que salir con error y nombrar el defecto. Un mutante cuya cadena no
aparece exactamente una vez es INERTE y también falla: no estaría probando
nada. Y antes de los mutantes, una copia SIN mutar tiene que salir limpia;
si no, un «cazado» no diría nada.

Uso:  python3 precalculo/prueba_ensambla_cap7.py
      (sale con 0 solo si todo está en verde; no toca lo publicado)
`audita_todo.sh` la recoge sola: busca `prueba_ensambla_cap${N}.py`.
"""
from __future__ import annotations

import os
import pathlib
import subprocess
import sys
import tempfile

RAIZ = pathlib.Path(__file__).resolve().parent.parent
ENSAMBLADOR = RAIZ / "precalculo" / "ensambla_cap7.py"
CAPITULO = RAIZ / "Htmls_Espacial" / "capitulo-7-autocorrelacion.html"

# Donde se inyecta un dato: con todas las descripciones ya escritas y antes de
# las guardas, que corren en `main()`. La guarda ve el dato roto; el texto se
# escribió con el bueno, que es justo el desajuste que tiene que cazar.
ANTES_DE_LA_TABLA = "DESCRIPCIONES = {\n"

# (nombre, texto que aparece UNA vez en `ensambla_cap7.py`, su sustituto, lo
# que la salida tiene que decir).
MUTANTES = [
    ("el mapa de CRIME sin `descripcion` en el registro",
     "paleta: 'naranja', descripcion: DESC7.m1,", "paleta: 'naranja',", "no trae `descripcion`"),
    ("el grafo de vecindades sin `descripcion` en el registro",
     "      descripcion: () => DESC7.w[E7.w],\n", "", "no trae `descripcion`"),
    ("la descripción del LISA de Columbus, corta",
     ANTES_DE_LA_TABLA, 'DESC7_COLUMBUS_LISA = "Corto."\n' + ANTES_DE_LA_TABLA, "caracteres"),
    ("una categoría con unidades que el mapa no tiene",
     ANTES_DE_LA_TABLA, '_VG7["col"]["lisa"][0]["n"] = 11\n' + ANTES_DE_LA_TABLA, "las categorías que se nombran"),
    ("la clase alta de CRIME con unidades de más",
     ANTES_DE_LA_TABLA, '_VG7["col"]["crime"]["alta"]["zona_n"][0] = 99\n' + ANTES_DE_LA_TABLA, "la clase alta o la baja"),
    ("una vecindad con parejas que el grafo no dibuja",
     ANTES_DE_LA_TABLA, 'D["m7"]["columbus"][0]["pares"] = 117\n' + ANTES_DE_LA_TABLA, "parejas o puntos rojos"),
    ("Getis-Ord sin celdas frías",
     ANTES_DE_LA_TABLA, '_GO["frios"]["zona"] = []\n' + ANTES_DE_LA_TABLA, "calientes y frías"),
    # El 2026-11-02 los municipios decían siempre «sobre todo en» sus tres
    # departamentos (la clase alta de la deserción: 69 de 225), y Columbus
    # nombraba dos zonas con «entre» aunque la clase cayera en cinco.
    ("«sobre todo» con departamentos que no pasan de la mitad",
     "        if sum(k for _, k in ds) * 2 > tot:\n", "        if True:\n",
     "dice más de lo que sostienen"),
    ("«sobre todo» con una zona que no pasa de la mitad",
     "    if ks[0] * 2 > tot and ks[1] * 2 < ks[0]:\n", "    if True:\n",
     "dice más de lo que sostienen"),
]

# La copia vive en un directorio temporal: sus dos rutas relativas a
# `__file__` se fijan al árbol de verdad, y la salida va a `CAP7_DESTINO`.
RUTAS_DE_LA_COPIA = [
    ("RAIZ = pathlib.Path(__file__).resolve().parent.parent",
     f"RAIZ = pathlib.Path({str(RAIZ)!r})"),
]


def ensambla_en_copia(fuente: str, tmp: pathlib.Path) -> tuple[int, str]:
    for viejo, nuevo in RUTAS_DE_LA_COPIA:
        fuente = fuente.replace(viejo, nuevo)
    copia = tmp / "ensambla_cap7.py"
    copia.write_text(fuente, encoding="utf-8")
    entorno = dict(os.environ, CAP7_DESTINO=str(tmp / "salida.html"),
                   PYTHONPATH=str(RAIZ / "precalculo"))
    r = subprocess.run([sys.executable, str(copia)], cwd=RAIZ, env=entorno,
                       capture_output=True, text=True, timeout=600)
    return r.returncode, r.stdout + r.stderr


def main() -> int:
    if not CAPITULO.exists():
        sys.exit(f"PARADO: no existe {CAPITULO.relative_to(RAIZ)}; ensámblalo con ensambla_cap7.py")
    fuente = ENSAMBLADOR.read_text(encoding="utf-8")
    publicado_antes = CAPITULO.read_bytes()
    print("=== prueba_ensambla_cap7.py — las guardas de «Describir el mapa» ===")
    for viejo, _ in RUTAS_DE_LA_COPIA:
        if fuente.count(viejo) != 1:
            print(f"  MAL  la copia del ensamblador no se puede fijar al árbol: «{viejo}» "
                  f"aparece {fuente.count(viejo)} veces")
            return 1

    cazados, colados, inertes = 0, [], []
    with tempfile.TemporaryDirectory(prefix="prueba_ensambla_cap7_") as d:
        tmp = pathlib.Path(d)
        cod, sal = ensambla_en_copia(fuente, tmp)
        if cod != 0:
            print("  MAL  la copia del ensamblador SIN mutar no sale limpia; los mutantes no medirían nada")
            print("       " + sal[-400:].replace("\n", "\n       "))
            return 1
        print("  OK   control: la copia sin mutar ensambla limpia fuera de lo publicado")
        for nombre, viejo, nuevo, espera in MUTANTES:
            if fuente.count(viejo) != 1:
                inertes.append(nombre)
                print(f"  INERTE  «{nombre}»: la cadena a mutar aparece {fuente.count(viejo)} veces y debía ser 1")
                continue
            cod, sal = ensambla_en_copia(fuente.replace(viejo, nuevo), tmp)
            linea = next((l.strip() for l in sal.splitlines() if espera in l), None)
            if cod != 0 and linea:
                cazados += 1
                print(f"  OK   mutante «{nombre}» para el ensamblado: {linea[:90]}")
            else:
                colados.append(nombre)
                print(f"  MAL  mutante «{nombre}» NO para el ensamblado (código {cod}; "
                      f"la salida no dice «{espera}»)")
                print("       " + sal[-300:].replace("\n", "\n       "))

    intacto = CAPITULO.read_bytes() == publicado_antes
    if not intacto:
        print("  MAL  el capítulo publicado cambió durante los mutantes: CAP7_DESTINO no lo protegió")
    print("\n" + "=" * 70)
    print(f"  {cazados} de {len(MUTANTES)} mutantes paran el ensamblado"
          + (f" · {len(inertes)} inerte(s)" if inertes else "")
          + (f" · {len(colados)} colado(s)" if colados else ""))
    print("=" * 70)
    return 0 if (intacto and not colados and not inertes) else 1


if __name__ == "__main__":
    sys.exit(main())
