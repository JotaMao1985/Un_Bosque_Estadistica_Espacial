#!/usr/bin/env python3
"""
prueba_califica_taller1.py — le rompe la hoja al calificador

Material de Estadística Espacial 2026-II (20929).

POR QUÉ EXISTE. `califica_taller1.py` imprime una nota y no se queja, y
ese silencio no significa nada por sí solo: un calificador cuyas anclas no
se han interrogado no es un calificador verificado. Es la lección que este
proyecto ya pagó con cinco auditores que jamás miraron dentro de KaTeX y
con dos comprobaciones de T0.5 que eran incapaces de fallar.

Y aquí pesa más que en un capítulo. De estas cuentas salen doce notas: una
ancla que se calle no deja una errata en un HTML, deja a un estudiante
calificado sobre una cuenta que nadie rehízo.

CÓMO FUNCIONA. Monta un curso de mentira en una carpeta temporal
—`CALIFICA_RAIZ`, el mismo convenio de `_ruta()` de los ensambladores—,
copia allí las cifras esperadas de una variante real, genera su hoja con
la propia herramienta, y a partir de esa hoja buena fabrica una copia
rota por cada defecto. **Las hojas de verdad no se tocan nunca.**

LAS DOS REGLAS DEL ARNÉS, heredadas de prueba_auditor_taller1.py:

  1. Cada tanda empieza y acaba con un CONTROL sin romper nada. Si el
     calificador no sale limpio sobre la hoja buena, cualquier «acierto»
     posterior es falso.
  2. No basta con que pare: tiene que parar por la razón correcta, así
     que cada caso declara un trozo del mensaje que espera ver.

LAS FAMILIAS DE DEFECTO:

  1. la rúbrica se sale de su rango o le falta una tarea
  2. la defensa no tiene la forma que la nota supone
  3. la recalificación no es defendible (tarea inexistente, sin motivo)
  4. la hoja y las cifras esperadas hablan de variantes distintas
  5. la columna de la cifra CORRECTA se editó         <- la más peligrosa
  6. la aritmética responde a lo que dice la hoja      (no es un PARADO:
     se comprueba que la nota CAMBIA o NO cambia según toque)

Uso:  python3 precalculo/prueba_califica_taller1.py
Devuelve 1 si algún defecto se cuela o si un control falla.
"""
from __future__ import annotations

import json
import os
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile

AQUI = pathlib.Path(__file__).resolve().parent
RAIZ = AQUI.parent
GUION = AQUI / "califica_taller1.py"
VARIANTE = 509
DOCUMENTO = "1000000509"


def corre(raiz: pathlib.Path, *args: str) -> tuple[int, str]:
    entorno = {**os.environ, "CALIFICA_RAIZ": str(raiz)}
    r = subprocess.run([sys.executable, str(GUION), *args],
                       cwd=RAIZ, capture_output=True, text=True, env=entorno)
    return r.returncode, r.stdout + r.stderr


# =====================================================================
# Los defectos: (nombre, familia, qué se rompe, qué mensaje se espera)
# =====================================================================
def defectos() -> list[tuple[str, int, object, str]]:
    def cambia(viejo: str, nuevo: str):
        def f(s: str) -> str:
            assert viejo in s, f"el arnés no encontró «{viejo}» en la hoja"
            return s.replace(viejo, nuevo, 1)
        return f

    def borra_linea(patron: str):
        return lambda s: re.sub(patron, "", s, count=1, flags=re.M)

    def añade(texto: str):
        return lambda s: s + "\n" + texto + "\n"

    return [
        ("A por encima de su tope", 1,
         cambia("rubrica T1    18    18    14    14    7", "rubrica T1    26    18    14    14    7"),
         "dimensión A"),
        ("C por encima de su tope", 1,
         cambia("rubrica T2    18    18    14    14    7", "rubrica T2    18    18    21    14    7"),
         "dimensión C"),
        ("puntuación negativa", 1,
         cambia("rubrica T3    18    18    14    14    7", "rubrica T3    18    18    14    -3    7"),
         "dimensión D"),
        ("falta una tarea en la rúbrica", 1, borra_linea(r"^rubrica T6.*$"), "no tiene fila para T6"),
        ("una tarea repetida", 1, añade("rubrica T5    20    20    16    16    8"),
         "aparece dos veces"),
        ("cinco dimensiones y media", 1,
         cambia("rubrica T7    18    18    14    14    7", "rubrica T7    18    18    14    14"),
         "cinco dimensiones"),

        ("falta «decisiones»", 2, borra_linea(r"^defensa decisiones.*$"), "defensa decisiones"),
        ("cuatro preguntas", 2, añade("defensa pregunta 12    70"), "y hay 4"),
        ("dos preguntas", 2, borra_linea(r"^defensa pregunta.*$"), "y hay 2"),
        ("la misma pregunta dos veces", 2,
         lambda s: s.replace("defensa pregunta  -     0", "defensa pregunta  9     70", 2),
         "dos veces en la defensa"),
        ("pregunta fuera del banco", 2,
         cambia("defensa pregunta  -     0", "defensa pregunta 99    70"), "no está en el banco"),
        ("nota de defensa fuera de 0-100", 2,
         cambia("defensa decisiones      0", "defensa decisiones    120"), "va de 0 a 100"),

        ("recalificación a una tarea que no existe", 3,
         añade("recalifica T9  40  lo que sea"), "no es una de las siete tareas"),
        ("recalificación sin motivo", 3, añade("recalifica T4  40"), "sin motivo escrito"),
        ("recalificación fuera de 0-100", 3,
         añade("recalifica T4  140  motivo cualquiera"), "va de 0 a 100"),

        ("la hoja dice otra variante", 4,
         cambia(f"variante:   {VARIANTE:03d}", "variante:   123"), "resuelve la"),
        ("entrega que no es ninguna de las tres", 4,
         cambia("entrega: a tiempo", "entrega: casi"), "no es ninguna de"),
        ("falta una cifra", 4, borra_linea(r"^cifra  T2\.rho.*$"), "faltan 1 cifras"),
        ("una cifra que no es de esta hoja", 4,
         añade("cifra  T9.inventada        1.0                    ok"), "no son de esta hoja"),
        ("palabra que la hoja no entiende", 4,
         añade("rubricas T1 1 2 3 4 5"), "no es ninguna de las palabras"),

        ("la columna CORRECTA, editada", 5,
         cambia("cifra  T2.digito          77919", "cifra  T2.digito          77920"),
         "Esa columna no se edita"),
        ("la columna CORRECTA, con un decimal de más", 5,
         cambia("cifra  T1.R               1.07903", "cifra  T1.R               1.07913"),
         "Esa columna no se edita"),
    ]


# =====================================================================
# Familia 6: que la aritmética responda a la hoja
# =====================================================================
def pruebas_de_aritmetica(raiz: pathlib.Path, hoja: pathlib.Path, base: str) -> list[tuple[str, bool, str]]:
    def nota(texto_hoja: str) -> float:
        hoja.write_text(texto_hoja, encoding="utf-8")
        cod, sal = corre(raiz, "--cuentas", str(hoja))
        assert cod == 0, f"la hoja debería calificar y devolvió {cod}:\n{sal}"
        m = re.search(r"FINAL\s+([\d.]+) / 100", sal)
        assert m, f"no se encontró la nota final en:\n{sal}"
        return float(m.group(1))

    limpia = nota(base)
    salidas = []

    # Una cifra mal NO puede mover la nota: la rúbrica publicada dice que
    # las cifras no son la calificación, y si esto dejara de ser cierto el
    # calificador estaría puntuando algo que el enunciado no anuncia.
    con_cifra_mal = nota(base.replace("cifra  T2.digito          77919                  ok",
                                      "cifra  T2.digito          77919                  12345"))
    salidas.append(("una cifra mal NO mueve la nota", con_cifra_mal == limpia,
                    f"{limpia:.2f} -> {con_cifra_mal:.2f}"))

    # Una celda de rúbrica SÍ tiene que moverla, y por la cantidad exacta:
    # T3 pesa el 20 %, así que subir A de 18 a 25 son 0.20 x 7 = 1.40.
    con_celda = nota(base.replace("rubrica T3    18    18    14    14    7",
                                  "rubrica T3    25    18    14    14    7"))
    esperado = limpia + 0.60 * 0.20 * 7
    salidas.append(("subir A en T3 (peso 20 %) mueve 0.84 en la final",
                    abs(con_celda - esperado) < 0.005, f"{con_celda:.2f} vs {esperado:.2f}"))

    # Y una recalificación tiene que dejar la tarea EXACTAMENTE donde dice.
    con_recal = nota(base + "\nrecalifica T3  40  no la sostuvo\n")
    esperado = limpia + 0.60 * 0.20 * (40 - 71)
    salidas.append(("recalificar T3 a 40 baja 3.72 en la final",
                    abs(con_recal - esperado) < 0.005, f"{con_recal:.2f} vs {esperado:.2f}"))

    # Una entrega tarde no se califica: el escrito va a cero y solo queda
    # la defensa, que es lo que publica el módulo 1.
    con_tarde = nota(base.replace("entrega: a tiempo", "entrega: tarde"))
    salidas.append(("entrega tarde deja el escrito en cero", abs(con_tarde) < 0.005,
                    f"{con_tarde:.2f}"))

    hoja.write_text(base, encoding="utf-8")
    return salidas


def main() -> int:
    fuente = RAIZ / "calificacion" / "esperado" / f"{VARIANTE:03d}.json"
    if not fuente.exists():
        print(f"\nPARADO: el arnés necesita {fuente.relative_to(RAIZ)}. Prodúcelo con:\n\n"
              f"  precalculo/rscript.sh precalculo/verifica_taller1.R {DOCUMENTO} "
              f"--json calificacion/esperado/\n")
        return 1

    temporal = pathlib.Path(tempfile.mkdtemp(prefix="prueba_califica_"))
    try:
        (temporal / "esperado").mkdir()
        shutil.copy(fuente, temporal / "esperado" / f"{VARIANTE:03d}.json")

        print("\n=== prueba_califica_taller1.py ===")
        print(f"  curso de mentira en {temporal}")

        cod, sal = corre(temporal, "--nuevo", f"{DOCUMENTO}:Conejillo De Indias")
        if cod != 0:
            print(f"\nPARADO: la herramienta no supo generar la hoja de control:\n{sal}")
            return 1
        hojas = sorted((temporal / "hojas").glob("T1_*.txt"))
        assert len(hojas) == 1
        hoja, base = hojas[0], hojas[0].read_text(encoding="utf-8")

        fallos = 0

        # --- control de entrada ---------------------------------------
        cod, sal = corre(temporal, "--cuentas", str(hoja))
        control_ok = cod == 0 and "PARADO" not in sal
        print(f"\n  {'OK  ' if control_ok else 'XX  '} CONTROL de entrada · la hoja buena califica "
              f"sin quejarse")
        if not control_ok:
            print(sal)
            return 1

        # --- los defectos ---------------------------------------------
        familia_previa = None
        for nombre, familia, romper, esperado in defectos():
            if familia != familia_previa:
                print(f"\n  --- familia {familia} ---")
                familia_previa = familia
            hoja.write_text(romper(base), encoding="utf-8")
            cod, sal = corre(temporal, "--cuentas", str(hoja))
            paro = cod != 0 and "PARADO" in sal
            razon = esperado.lower() in sal.lower()
            bien = paro and razon
            fallos += 0 if bien else 1
            detalle = ("NO PARÓ" if not paro else
                       f"paró por otra cosa, se esperaba «{esperado}»" if not razon else
                       sal.split("PARADO:")[1].strip().split("\n")[0][:62])
            print(f"  {'OK  ' if bien else 'XX  '} {nombre:<42} {detalle}")

        hoja.write_text(base, encoding="utf-8")

        # --- familia 6: la aritmética ----------------------------------
        print(f"\n  --- familia 6: que la nota responda a lo que dice la hoja ---")
        for nombre, bien, detalle in pruebas_de_aritmetica(temporal, hoja, base):
            fallos += 0 if bien else 1
            print(f"  {'OK  ' if bien else 'XX  '} {nombre:<42} {detalle}")

        # --- control de salida -----------------------------------------
        cod, sal = corre(temporal, "--cuentas", str(hoja))
        control_ok = cod == 0 and "PARADO" not in sal
        fallos += 0 if control_ok else 1
        print(f"\n  {'OK  ' if control_ok else 'XX  '} CONTROL de salida · la hoja buena sigue "
              f"calificando igual")

        # --- que los reportes se escriban de verdad --------------------
        cod, sal = corre(temporal)
        hay = (temporal / "reportes" / "curso.html").exists()
        fallos += 0 if (cod == 0 and hay) else 1
        print(f"  {'OK  ' if cod == 0 and hay else 'XX  '} los dos reportes se escriben")

        total = len(defectos()) + 4 + 2 + 1
        print(f"\n  {total - fallos} de {total} comprobaciones en pie.\n")
        return 1 if fallos else 0
    finally:
        shutil.rmtree(temporal, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
