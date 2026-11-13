#!/usr/bin/env python3
"""
prueba_ensambla_cap4.py — las guardas de «Describir el mapa» saben parar el
ensamblado

Material de Estadística Espacial 2026-II (20929). 2026-11-02.

POR QUÉ EXISTE. Desde esa fecha cada mapa del capítulo 4 lleva una
descripción larga —lo que se VE en él, para quien no lo ve—, y
`ensambla_cap4.py` comprueba contra el dato lo que esas frases afirman: que
las sedes se apiñan más en unas zonas del dibujo que en otras, que en el
D.C. casi todas caen en el tercio norte, que las células se reparten casi
como una rejilla, que las secuoyas guardan poco más de la mitad de la
distancia que daría el azar, que la rebaraja conserva las cuentas por celda.
Un `MAL` que nadie ha visto salir puede estar bien escrito o puede ser
incapaz de dispararse, y desde fuera se ven igual: es la lección de T0.5.
Aquí cada guarda se rompe a propósito y tiene que parar.

CÓMO. El ensamblador se ejecuta en COPIA, en un directorio temporal, con
`CAP4_DESTINO` fuera de lo publicado (escribe el HTML antes de correr sus
guardas) y con UNA sustitución cada vez. Unos mutantes rompen el texto o el
cableado; otros, el dato que una frase afirma, inyectado justo después de que
el ensamblador lo lea: las dos cosas son lo que la guarda vigila. Cada copia
tiene que salir con error y nombrar el defecto. Un mutante cuya cadena no
aparece exactamente una vez es INERTE y también falla: no estaría probando
nada. Y antes de los mutantes, una copia SIN mutar tiene que salir limpia;
si no, un «cazado» no diría nada.

Uso:  python3 precalculo/prueba_ensambla_cap4.py
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
ENSAMBLADOR = RAIZ / "precalculo" / "ensambla_cap4.py"
CAPITULO = RAIZ / "Htmls_Espacial" / "capitulo-4-patrones-puntuales.html"

# Donde se inyecta un dato: con todas las descripciones ya escritas y antes de
# las guardas, que corren en `main()`. La guarda ve el dato roto; el texto se
# escribió con el bueno, que es justo el desajuste que tiene que cazar.
ANTES_DE_LA_TABLA = "DESCRIPCIONES = {\n"

# (nombre, texto que aparece UNA vez en `ensambla_cap4.py`, su sustituto, lo
# que la salida tiene que decir).
MUTANTES = [
    ("el mapa urbano sin `descripcion` en el registro",
     '''            + ", descripcion: " + json.dumps(DESC_URBANO, ensure_ascii=False))''', "            )",
     "no trae `descripcion`"),
    ("la descripción del D.C., corta",
     ANTES_DE_LA_TABLA, 'DESC_DC = "Corto."\n' + ANTES_DE_LA_TABLA, "caracteres"),
    ("la de las células, igual a su etiqueta",
     ANTES_DE_LA_TABLA,
     'DESC_CELLS = "Patrón regular: 42 células biológicas, más separadas entre sí de lo que daría el azar."\n'
     + ANTES_DE_LA_TABLA, "repite la etiqueta"),
    ("las zonas del urbano, de menos densa a más",
     ANTES_DE_LA_TABLA, "_zu.reverse()\n" + ANTES_DE_LA_TABLA, "urbano:"),
    ("el D.C. con sus sedes repartidas",
     ANTES_DE_LA_TABLA, '_fr["norte"] = (1500, _fr["norte"][1])\n' + ANTES_DE_LA_TABLA, "D.C.:"),
    ("las células dejan de ser casi una rejilla",
     ANTES_DE_LA_TABLA, '_C["clark_evans"] = 1.1\n' + ANTES_DE_LA_TABLA, "células:"),
    ("los pinos se apartan del azar",
     ANTES_DE_LA_TABLA, '_J["clark_evans"] = 1.3\n' + ANTES_DE_LA_TABLA, "pinos:"),
    ("las secuoyas dejan de estar en grumos",
     ANTES_DE_LA_TABLA, '_R["clark_evans"] = 0.9\n' + ANTES_DE_LA_TABLA, "secuoyas:"),
    ("los claros del urbano, desordenados",
     ANTES_DE_LA_TABLA, "_cr.reverse()\n" + ANTES_DE_LA_TABLA, "los claros"),
    ("la rebaraja cambia las cuentas por celda",
     ANTES_DE_LA_TABLA, '_RB["vacios"] = 4\n' + ANTES_DE_LA_TABLA, "ceguera:"),
]

# La copia vive en un directorio temporal: sus dos rutas relativas a
# `__file__` se fijan al árbol de verdad, y la salida va a `CAP4_DESTINO`.
RUTAS_DE_LA_COPIA = [
    ("RAIZ = pathlib.Path(__file__).resolve().parent.parent",
     f"RAIZ = pathlib.Path({str(RAIZ)!r})"),
]


def ensambla_en_copia(fuente: str, tmp: pathlib.Path) -> tuple[int, str]:
    for viejo, nuevo in RUTAS_DE_LA_COPIA:
        fuente = fuente.replace(viejo, nuevo)
    copia = tmp / "ensambla_cap4.py"
    copia.write_text(fuente, encoding="utf-8")
    entorno = dict(os.environ, CAP4_DESTINO=str(tmp / "salida.html"),
                   PYTHONPATH=str(RAIZ / "precalculo"))
    r = subprocess.run([sys.executable, str(copia)], cwd=RAIZ, env=entorno,
                       capture_output=True, text=True, timeout=600)
    return r.returncode, r.stdout + r.stderr


def main() -> int:
    if not CAPITULO.exists():
        sys.exit(f"PARADO: no existe {CAPITULO.relative_to(RAIZ)}; ensámblalo con ensambla_cap4.py")
    fuente = ENSAMBLADOR.read_text(encoding="utf-8")
    publicado_antes = CAPITULO.read_bytes()
    print("=== prueba_ensambla_cap4.py — las guardas de «Describir el mapa» ===")
    for viejo, _ in RUTAS_DE_LA_COPIA:
        if fuente.count(viejo) != 1:
            print(f"  MAL  la copia del ensamblador no se puede fijar al árbol: «{viejo}» "
                  f"aparece {fuente.count(viejo)} veces")
            return 1

    cazados, colados, inertes = 0, [], []
    with tempfile.TemporaryDirectory(prefix="prueba_ensambla_cap4_") as d:
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
        print("  MAL  el capítulo publicado cambió durante los mutantes: CAP4_DESTINO no lo protegió")
    print("\n" + "=" * 70)
    print(f"  {cazados} de {len(MUTANTES)} mutantes paran el ensamblado"
          + (f" · {len(inertes)} inerte(s)" if inertes else "")
          + (f" · {len(colados)} colado(s)" if colados else ""))
    print("=" * 70)
    return 0 if (intacto and not colados and not inertes) else 1


if __name__ == "__main__":
    sys.exit(main())
