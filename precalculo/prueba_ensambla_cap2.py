#!/usr/bin/env python3
"""
prueba_ensambla_cap2.py — las guardas de «Describir el mapa» y de los botones
de las proyecciones saben parar el ensamblado

Material de Estadística Espacial 2026-II (20929). 2026-11-02.

POR QUÉ EXISTE. Desde esa fecha cada mapa del capítulo 2 lleva una
descripción larga —lo que se VE en él, para quien no lo ve— y
`ensambla_cap2.py` comprueba contra el dato lo que esas frases afirman de la
forma: que con Mercator las elipses crecen hasta las filas extremas, que el
error de 3116 es más claro en la franja central, que las estaciones
invertidas caen al sur del golfo de Guinea… El mismo día los dos mapas de
proyecciones ganaron los botones de vista que su prosa prometía desde el
primer día, y otra guarda vigila que sigan ahí. Un `MAL` que nadie ha visto
salir puede estar bien escrito o puede ser incapaz de dispararse, y desde
fuera se ven igual: es la lección de T0.5. Aquí cada guarda se rompe a
propósito y tiene que parar.

CÓMO. El ensamblador se ejecuta en COPIA, en un directorio temporal, con
`CAP2_DESTINO` fuera de lo publicado (escribe el HTML antes de correr sus
guardas) y con UNA sustitución cada vez. Unos mutantes rompen el texto o el
cableado; otros, el dato que una frase afirma, inyectado justo después de que
el ensamblador lo lea: las dos cosas son lo que la guarda vigila. Cada copia
tiene que salir con error y nombrar el defecto. Un mutante cuya cadena no
aparece exactamente una vez es INERTE y también falla: no estaría probando
nada. Y antes de los mutantes, una copia SIN mutar tiene que salir limpia;
si no, un «cazado» no diría nada.

Uso:  python3 precalculo/prueba_ensambla_cap2.py
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
ENSAMBLADOR = RAIZ / "precalculo" / "ensambla_cap2.py"
CAPITULO = RAIZ / "Htmls_Espacial" / "capitulo-2-crs-georreferenciacion.html"

# Donde se inyecta un dato: justo después de que el ensamblador arme sus
# atajos, antes de escribir ninguna descripción.
TRAS_LOS_DATOS = '_IC = {v["nombre"]: k for k, v in enumerate(_PCV)}\n'

# (nombre, texto que aparece UNA vez en `ensambla_cap2.py`, su sustituto, lo
# que la salida tiene que decir).
MUTANTES = [
    ("un mapa de proyecciones sin `descripcion` en el registro",
     '              vista="vistaCo2", descripcion=DESC_COLOMBIA)',
     '              vista="vistaCo2", descripcion=DESC_COLOMBIA).replace("      descripcion:", "      nada:")',
     "no trae `descripcion`"),
    ("la descripción del sesgo, corta",
     "DESCRIPCIONES = {", 'DESC_SESGO = "Corto."\nDESCRIPCIONES = {', "caracteres"),
    ("la descripción del geohash, igual a su etiqueta",
     "DESCRIPCIONES = {",
     'DESC_GEOHASH = "Las celdas son rectángulos de la rejilla del geohash, no unidades administrativas."'
     '\nDESCRIPCIONES = {',
     "repite la etiqueta"),
    ("Mercator deja de ser redonda",
     TRAS_LOS_DATOS, TRAS_LOS_DATOS + 'PT["omega_max_grados"][_IV["Mercator"]] = 0.5\n', "Mercator:"),
    ("la rejilla del mundo, con la longitud corrida",
     TRAS_LOS_DATOS, TRAS_LOS_DATOS + '_RM["lon"] = _RM["lon"][1:] + _RM["lon"][:1]\n',
     "en las esquinas» ya no vale"),
    ("la azimutal, con la más lejana en otro sitio",
     TRAS_LOS_DATOS, TRAS_LOS_DATOS + '_RM["dist_centro_km"][0] = 19000.0\n', "azimutal:"),
    ("el meridiano de 3116, en otra columna",
     TRAS_LOS_DATOS, TRAS_LOS_DATOS + '_RC["meridiano_3116"] = -71.0\n', "Colombia, MAGNA-SIRGAS / Bogotá"),
    ("el error de 3116, lo más claro fuera de la franja central",
     TRAS_LOS_DATOS, TRAS_LOS_DATOS + '_VI["error_3116"]["menores"][1]["zona"] = "oriente"\n',
     "lo más claro ya no está en la franja central"),
    ("las invertidas, lejos del meridiano de Greenwich",
     TRAS_LOS_DATOS, TRAS_LOS_DATOS + 'cs["caja_mal"][0] = 1.5\n', "al sur del golfo de Guinea"),
    ("el sesgo nombra una tasa que el mapa no pinta",
     TRAS_LOS_DATOS, TRAS_LOS_DATOS + '_VI["sesgo"]["pct"][0] = 12.9\n', "sesgo:"),
    ("las celdas claras del geohash, repartidas",
     TRAS_LOS_DATOS, TRAS_LOS_DATOS + '_VI["geohash"]["claras_n"][0] = 4\n', "geohash:"),
    ("los botones de las proyecciones, sin la llamada que los pone",
     '                    "        iniciarGeomapas();\\n        cablearCap2();\\n",',
     '                    "        iniciarGeomapas();\\n        cablearCap2 && 0;\\n",',
     "sin botones de vista"),
]

# La copia vive en un directorio temporal: sus dos rutas relativas a
# `__file__` se fijan al árbol de verdad, y la salida va a `CAP2_DESTINO`.
RUTAS_DE_LA_COPIA = [
    ("RAIZ = pathlib.Path(__file__).resolve().parent.parent",
     f"RAIZ = pathlib.Path({str(RAIZ)!r})"),
]


def ensambla_en_copia(fuente: str, tmp: pathlib.Path) -> tuple[int, str]:
    for viejo, nuevo in RUTAS_DE_LA_COPIA:
        fuente = fuente.replace(viejo, nuevo)
    copia = tmp / "ensambla_cap2.py"
    copia.write_text(fuente, encoding="utf-8")
    entorno = dict(os.environ, CAP2_DESTINO=str(tmp / "salida.html"),
                   PYTHONPATH=str(RAIZ / "precalculo"))
    r = subprocess.run([sys.executable, str(copia)], cwd=RAIZ, env=entorno,
                       capture_output=True, text=True, timeout=600)
    return r.returncode, r.stdout + r.stderr


def main() -> int:
    if not CAPITULO.exists():
        sys.exit(f"PARADO: no existe {CAPITULO.relative_to(RAIZ)}; ensámblalo con ensambla_cap2.py")
    fuente = ENSAMBLADOR.read_text(encoding="utf-8")
    publicado_antes = CAPITULO.read_bytes()
    print("=== prueba_ensambla_cap2.py — las guardas de «Describir el mapa» y de los botones ===")
    for viejo, _ in RUTAS_DE_LA_COPIA:
        if fuente.count(viejo) != 1:
            print(f"  MAL  la copia del ensamblador no se puede fijar al árbol: «{viejo}» "
                  f"aparece {fuente.count(viejo)} veces")
            return 1

    cazados, colados, inertes = 0, [], []
    with tempfile.TemporaryDirectory(prefix="prueba_ensambla_cap2_") as d:
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
        print("  MAL  el capítulo publicado cambió durante los mutantes: CAP2_DESTINO no lo protegió")
    print("\n" + "=" * 70)
    print(f"  {cazados} de {len(MUTANTES)} mutantes paran el ensamblado"
          + (f" · {len(inertes)} inerte(s)" if inertes else "")
          + (f" · {len(colados)} colado(s)" if colados else ""))
    print("=" * 70)
    return 0 if (intacto and not colados and not inertes) else 1


if __name__ == "__main__":
    sys.exit(main())
