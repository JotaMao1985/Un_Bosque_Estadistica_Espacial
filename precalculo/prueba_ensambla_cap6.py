#!/usr/bin/env python3
"""
prueba_ensambla_cap6.py — las guardas de «Describir el mapa» saben parar el
ensamblado

Material de Estadística Espacial 2026-II (20929). 2026-11-02.

POR QUÉ EXISTE. Desde esa fecha los dos mapas del capítulo 6 llevan una
descripción larga —lo que se VE en ellos, para quien no los ve—: el grafo
de Columbus, una por cada uno de sus diez criterios de vecindad, y la red de
contigüidad de los 1 122 municipios. `ensambla_cap6.py` comprueba contra el
dato lo que esas frases afirman: que cada criterio tiene un comienzo de
frase, que las parejas y los puntos rojos que se cuentan son los que el mapa
dibuja, que Gabriel tiene menos parejas que Delaunay, que la red municipal
se apiña en el centro y el norte del dibujo. Un `MAL` que nadie ha visto
salir puede estar bien escrito o puede ser incapaz de dispararse, y desde
fuera se ven igual: es la lección de T0.5. Aquí cada guarda se rompe a
propósito y tiene que parar.

CÓMO. El ensamblador se ejecuta en COPIA, en un directorio temporal, con
`CAP6_DESTINO` fuera de lo publicado (escribe el HTML antes de correr sus
guardas) y con UNA sustitución cada vez. Unos mutantes rompen el texto o el
cableado; otros, el dato que una frase afirma, inyectado justo después de que
el ensamblador lo lea: las dos cosas son lo que la guarda vigila. Cada copia
tiene que salir con error y nombrar el defecto. Un mutante cuya cadena no
aparece exactamente una vez es INERTE y también falla: no estaría probando
nada. Y antes de los mutantes, una copia SIN mutar tiene que salir limpia;
si no, un «cazado» no diría nada.

Uso:  python3 precalculo/prueba_ensambla_cap6.py
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
ENSAMBLADOR = RAIZ / "precalculo" / "ensambla_cap6.py"
CAPITULO = RAIZ / "Htmls_Espacial" / "capitulo-6-pesos-espaciales.html"

# Donde se inyecta un dato: con todas las descripciones ya escritas y antes de
# las guardas, que corren en `main()`. La guarda ve el dato roto; el texto se
# escribió con el bueno, que es justo el desajuste que tiene que cazar.
ANTES_DE_LA_TABLA = "DESCRIPCIONES = {"

# (nombre, texto que aparece UNA vez en `ensambla_cap6.py`, su sustituto, lo
# que la salida tiene que decir).
MUTANTES = [
    ("el mapa municipal sin `descripcion` en el registro",
     '''        "dibujados en rojo.") + ",\\n      descripcion: " + json.dumps(DESC_MUNICIPIOS, ensure_ascii=False))''',
     '''        "dibujados en rojo."))''', "no trae `descripcion`"),
    ("el grafo de Columbus sin `descripcion` en el registro",
     '''        + ",\\n      descripcion: () => DESC6_W[estadoCap6.w]")''', "        )", "no trae `descripcion`"),
    ("la descripción municipal, corta",
     ANTES_DE_LA_TABLA, 'DESC_MUNICIPIOS = "Corto."\n' + ANTES_DE_LA_TABLA, "caracteres"),
    ("un criterio sin comienzo de frase",
     ANTES_DE_LA_TABLA, '_LEAD["reinas"] = _LEAD.pop("reina")\n' + ANTES_DE_LA_TABLA, "comienzo de frase"),
    ("el texto cuenta puntos rojos que el mapa no dibuja",
     ANTES_DE_LA_TABLA, '_CRIT["d_mitad"]["islas"] = 3\n' + ANTES_DE_LA_TABLA, "puntos rojos"),
    ("Gabriel con más parejas que Delaunay",
     ANTES_DE_LA_TABLA, '_CRIT["gabriel"]["pares"] = 200\n' + ANTES_DE_LA_TABLA, "Gabriel"),
    ("las aristas del oriente, cortas",
     ANTES_DE_LA_TABLA, 'M["cap6-municipios"]["variantes"]["reina"]["aristas"] = [1, 2] * 3285\n' + ANTES_DE_LA_TABLA,
     "unas pocas líneas largas"),
    ("la red municipal deja de apiñarse en el centro",
     ANTES_DE_LA_TABLA, '_VM6["zona"][0], _VM6["zona"][1] = "norte", "centro"\n' + ANTES_DE_LA_TABLA,
     "se apiña en el centro"),
]

# La copia vive en un directorio temporal: sus dos rutas relativas a
# `__file__` se fijan al árbol de verdad, y la salida va a `CAP6_DESTINO`.
RUTAS_DE_LA_COPIA = [
    ("RAIZ = pathlib.Path(__file__).resolve().parent.parent",
     f"RAIZ = pathlib.Path({str(RAIZ)!r})"),
]


def ensambla_en_copia(fuente: str, tmp: pathlib.Path) -> tuple[int, str]:
    for viejo, nuevo in RUTAS_DE_LA_COPIA:
        fuente = fuente.replace(viejo, nuevo)
    copia = tmp / "ensambla_cap6.py"
    copia.write_text(fuente, encoding="utf-8")
    entorno = dict(os.environ, CAP6_DESTINO=str(tmp / "salida.html"),
                   PYTHONPATH=str(RAIZ / "precalculo"))
    r = subprocess.run([sys.executable, str(copia)], cwd=RAIZ, env=entorno,
                       capture_output=True, text=True, timeout=600)
    return r.returncode, r.stdout + r.stderr


def main() -> int:
    if not CAPITULO.exists():
        sys.exit(f"PARADO: no existe {CAPITULO.relative_to(RAIZ)}; ensámblalo con ensambla_cap6.py")
    fuente = ENSAMBLADOR.read_text(encoding="utf-8")
    publicado_antes = CAPITULO.read_bytes()
    print("=== prueba_ensambla_cap6.py — las guardas de «Describir el mapa» ===")
    for viejo, _ in RUTAS_DE_LA_COPIA:
        if fuente.count(viejo) != 1:
            print(f"  MAL  la copia del ensamblador no se puede fijar al árbol: «{viejo}» "
                  f"aparece {fuente.count(viejo)} veces")
            return 1

    cazados, colados, inertes = 0, [], []
    with tempfile.TemporaryDirectory(prefix="prueba_ensambla_cap6_") as d:
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
        print("  MAL  el capítulo publicado cambió durante los mutantes: CAP6_DESTINO no lo protegió")
    print("\n" + "=" * 70)
    print(f"  {cazados} de {len(MUTANTES)} mutantes paran el ensamblado"
          + (f" · {len(inertes)} inerte(s)" if inertes else "")
          + (f" · {len(colados)} colado(s)" if colados else ""))
    print("=" * 70)
    return 0 if (intacto and not colados and not inertes) else 1


if __name__ == "__main__":
    sys.exit(main())
