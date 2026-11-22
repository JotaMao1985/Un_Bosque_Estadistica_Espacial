#!/usr/bin/env python3
"""
prueba_ensambla_cap3.py — las guardas de «Describir el mapa» saben parar el
ensamblado

Material de Estadística Espacial 2026-II (20929). 2026-11-02.

POR QUÉ EXISTE. Desde esa fecha cada mapa del capítulo 3 lleva una
descripción larga —lo que se VE en él, para quien no lo ve—, y los
conmutables una por estado: cinco esquemas en Carolina del Norte y cinco en
la deserción, dos capas en el conteo y tres superposiciones en el coropleto
departamental. `ensambla_cap3.py` comprueba contra el dato lo que esas frases
afirman de la forma: que con intervalos iguales casi todo Carolina del Norte
cae en la primera clase, que la clase más oscura de la deserción no tiene
ningún municipio en el norte con intervalos iguales, que Bogotá apenas se ve
en el coropleto, que el contiguo encoge la Amazonía… Un `MAL` que nadie ha
visto salir puede estar bien escrito o puede ser incapaz de dispararse, y
desde fuera se ven igual: es la lección de T0.5. Aquí cada guarda se rompe a
propósito y tiene que parar.

CÓMO. El ensamblador se ejecuta en COPIA, en un directorio temporal, con
`CAP3_DESTINO` fuera de lo publicado (escribe el HTML antes de correr sus
guardas) y con UNA sustitución cada vez. Unos mutantes rompen el texto o el
cableado; otros, el dato que una frase afirma, inyectado justo después de que
el ensamblador lo lea: las dos cosas son lo que la guarda vigila. Cada copia
tiene que salir con error y nombrar el defecto. Un mutante cuya cadena no
aparece exactamente una vez es INERTE y también falla: no estaría probando
nada. Y antes de los mutantes, una copia SIN mutar tiene que salir limpia;
si no, un «cazado» no diría nada.

Uso:  python3 precalculo/prueba_ensambla_cap3.py
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
ENSAMBLADOR = RAIZ / "precalculo" / "ensambla_cap3.py"
CAPITULO = RAIZ / "Htmls_Espacial" / "capitulo-3-cartografia-maup.html"

# Donde se inyecta un dato: con todas las descripciones ya escritas y antes de
# las guardas, que corren en `main()`. La guarda ve el dato roto; el texto se
# escribió con el bueno, que es justo el desajuste que tiene que cazar.
ANTES_DE_LA_TABLA = "DESCRIPCIONES = {\n"

# (nombre, texto que aparece UNA vez en `ensambla_cap3.py`, su sustituto, lo
# que la salida tiene que decir).
MUTANTES = [
    ("Carolina del Norte sin `descripcion` en el registro",
     '''              ", descripcion: () => DESC3_NC[ncVista]")''', '''              "")''',
     "no trae `descripcion`"),
    ("la descripción de la presencia, corta",
     ANTES_DE_LA_TABLA, 'DESC_PRESENCIA = "Corto."\n' + ANTES_DE_LA_TABLA, "caracteres"),
    ("un esquema de Carolina del Norte, igual a la etiqueta",
     ANTES_DE_LA_TABLA,
     'DESC_NC[0] = "Los 100 condados de Carolina del Norte coloreados por SID74, con el esquema de '
     'clasificación que se elija."\n' + ANTES_DE_LA_TABLA, "repite la etiqueta"),
    ("intervalos iguales deja de llenar la primera clase",
     ANTES_DE_LA_TABLA, '_VNC["equal"]["tam"][0] = 40\n' + ANTES_DE_LA_TABLA, "intervalos iguales:"),
    ("los tres puntajes más bajos, de dos departamentos",
     ANTES_DE_LA_TABLA, '_baj[1]["depto"] = "Nariño"\n' + ANTES_DE_LA_TABLA, "puntaje medio:"),
    ("la deserción por intervalos iguales gana un municipio en el norte",
     ANTES_DE_LA_TABLA, '_OSC["equal"]["zonas"] = ["norte", "sur"]\n' + ANTES_DE_LA_TABLA,
     "dos municipios y ninguno en el norte"),
    ("la deserción por Fisher-Jenks se llena de norte",
     ANTES_DE_LA_TABLA, '_OSC["fisher"]["zonas_n"][_OSC["fisher"]["zonas"].index("norte")] = 20\n'
     + ANTES_DE_LA_TABLA, "Fisher-Jenks:"),
    ("head/tails pasa a tres clases",
     ANTES_DE_LA_TABLA, '_VDES["headtails"]["tam"].append(5)\n' + ANTES_DE_LA_TABLA, "head/tails:"),
    ("Bogotá deja de ser casi invisible en el coropleto",
     ANTES_DE_LA_TABLA, '_m7["area_pct_mapa"][_ix[_B]] = 2.0\n' + ANTES_DE_LA_TABLA, "coropleto:"),
    ("el dot density llena el oriente",
     ANTES_DE_LA_TABLA, '_dd["oriente"] = 100\n' + ANTES_DE_LA_TABLA, "dot density:"),
    ("el contiguo hace crecer la Amazonía",
     ANTES_DE_LA_TABLA, '_m7["area_pct_cont"][_ix[_AMZ]] = 12.0\n' + ANTES_DE_LA_TABLA, "contiguo:"),
    ("el hexágono más oscuro deja de ser casi todo de Bogotá",
     ANTES_DE_LA_TABLA, '_m7["hex_max_aporta_pct"] = 40.0\n' + ANTES_DE_LA_TABLA, "hexbin:"),
    # Del 2026-11-17: en un cartograma el área es el dato, y la silueta del motor
    # la falsea. La guarda mira el registro publicado de los cuatro mapas.
    ("el cartograma no contiguo vuelve a llevar silueta",
     '''    + geomapa('cap3-carto-ncont', 'dep_ncont', 'verde',
              ", silueta: false, descripcion: "''', '''    + geomapa('cap3-carto-ncont', 'dep_ncont', 'verde',
              ", descripcion: "''', "no apaga la silueta"),
    ("el cartograma contiguo vuelve a llevar silueta",
     '''    + geomapa('cap3-carto-cont', 'dep_cont', 'verde',
              ", silueta: false, descripcion: "''', '''    + geomapa('cap3-carto-cont', 'dep_cont', 'verde',
              ", descripcion: "''', "no apaga la silueta"),
    ("un municipio sin estudiantes aparece en el norte",
     ANTES_DE_LA_TABLA, '_SIN[0]["zona"] = "norte"\n' + ANTES_DE_LA_TABLA, "presencia:"),
]

# La copia vive en un directorio temporal: sus dos rutas relativas a
# `__file__` se fijan al árbol de verdad, y la salida va a `CAP3_DESTINO`.
RUTAS_DE_LA_COPIA = [
    ("RAIZ = pathlib.Path(__file__).resolve().parent.parent",
     f"RAIZ = pathlib.Path({str(RAIZ)!r})"),
]


def ensambla_en_copia(fuente: str, tmp: pathlib.Path) -> tuple[int, str]:
    for viejo, nuevo in RUTAS_DE_LA_COPIA:
        fuente = fuente.replace(viejo, nuevo)
    copia = tmp / "ensambla_cap3.py"
    copia.write_text(fuente, encoding="utf-8")
    entorno = dict(os.environ, CAP3_DESTINO=str(tmp / "salida.html"),
                   PYTHONPATH=str(RAIZ / "precalculo"))
    r = subprocess.run([sys.executable, str(copia)], cwd=RAIZ, env=entorno,
                       capture_output=True, text=True, timeout=600)
    return r.returncode, r.stdout + r.stderr


def main() -> int:
    if not CAPITULO.exists():
        sys.exit(f"PARADO: no existe {CAPITULO.relative_to(RAIZ)}; ensámblalo con ensambla_cap3.py")
    fuente = ENSAMBLADOR.read_text(encoding="utf-8")
    publicado_antes = CAPITULO.read_bytes()
    print("=== prueba_ensambla_cap3.py — las guardas de «Describir el mapa» ===")
    for viejo, _ in RUTAS_DE_LA_COPIA:
        if fuente.count(viejo) != 1:
            print(f"  MAL  la copia del ensamblador no se puede fijar al árbol: «{viejo}» "
                  f"aparece {fuente.count(viejo)} veces")
            return 1

    cazados, colados, inertes = 0, [], []
    with tempfile.TemporaryDirectory(prefix="prueba_ensambla_cap3_") as d:
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
        print("  MAL  el capítulo publicado cambió durante los mutantes: CAP3_DESTINO no lo protegió")
    print("\n" + "=" * 70)
    print(f"  {cazados} de {len(MUTANTES)} mutantes paran el ensamblado"
          + (f" · {len(inertes)} inerte(s)" if inertes else "")
          + (f" · {len(colados)} colado(s)" if colados else ""))
    print("=" * 70)
    return 0 if (intacto and not colados and not inertes) else 1


if __name__ == "__main__":
    sys.exit(main())
