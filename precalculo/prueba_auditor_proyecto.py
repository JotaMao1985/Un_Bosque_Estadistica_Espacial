#!/usr/bin/env python3
"""prueba_auditor_proyecto.py — ¿Caza el auditor lo que dice que caza?

Inyecta un defecto por vez en una COPIA de la guía publicada y exige dos cosas:
que `audita_proyecto.py` falle, y que falle EN EL FRENTE al que ese defecto
pertenece. Un auditor que para por la razón equivocada solo acierta por suerte.
Antes y después corre un control limpio: si el original no pasa, el arnés no
mide nada.

    python3 precalculo/prueba_auditor_proyecto.py

El frente E (código R) solo se corre en los defectos que lo necesitan: tarda
medio minuto y los demás no lo tocan. Los dos últimos cambian la PLANTILLA
.Rmd, no la guía, y se la pasan al auditor por PROYECTO_RMD.
"""
from __future__ import annotations

import os
import pathlib
import re
import subprocess
import sys
import tempfile

AQUI = pathlib.Path(__file__).resolve().parent
RAIZ = AQUI.parent
PUBLICADO = RAIZ / "Htmls_Espacial" / "proyecto-integrador-corte-iii.html"
AUDITOR = AQUI / "audita_proyecto.py"
RMD_FUENTE = RAIZ / "proyecto" / "plantilla-informe.Rmd"
FINO = " "


def cambia(viejo: str, nuevo: str, todas: bool = False):
    def f(t: str) -> str:
        if viejo not in t:
            raise SystemExit(f"!! el arnés no encuentra «{viejo[:60]}»: el defecto no se inyectaría")
        return t.replace(viejo, nuevo, -1 if todas else 1)
    return f


def sub(patron: str, nuevo: str):
    def f(t: str) -> str:
        r, n = re.subn(patron, nuevo, t, count=1, flags=re.S)
        if not n:
            raise SystemExit(f"!! el arnés no encuentra /{patron[:60]}/: el defecto no se inyectaría")
        return r
    return f


def antes_de_style(extra: str):
    def f(t: str) -> str:
        i = t.index("</style>")
        return t[:i] + extra + t[i:]
    return f


def en_modulo(n: int, extra: str):
    def f(t: str) -> str:
        marca = f'<template id="module-{n}">'
        i = t.index(marca) + len(marca)
        return t[:i] + extra + t[i:]
    return f


# (nombre, frente esperado, transformación, ¿corre R?)
DEFECTOS = [
    # --- A · Calendario
    ("día de la semana equivocado", "A", cambia("martes 27 de octubre", "miércoles 27 de octubre", todas=True), False),
    ("la ficha vuelve en una fecha suelta", "A", cambia("jueves 29 de octubre", "jueves 22 de octubre"), False),
    ("una semana mal en la tabla de hitos", "A",
     cambia("<td>martes 10 de noviembre</td><td>15</td>", "<td>martes 10 de noviembre</td><td>14</td>"), False),
    ("una hora de cierre distinta", "A", cambia("a las 11:00", "a las 12:30"), False),
    ("un día fijo para la exposición, que se acuerda en clase", "A",
     cambia("<td>se acuerda en clase</td>", "<td>martes 17 de noviembre</td>"), False),
    ("el informe pasa al festivo del lunes 16", "A",
     cambia("domingo 15 de noviembre a las 11:00", "lunes 16 de noviembre a las 11:00", todas=True), False),
    ("la exposición en un día sin clase de Espacial", "A",
     cambia("el jueves 19 de noviembre", "el miércoles 18 de noviembre"), False),
    # --- B · Pesos
    ("un criterio que ya no suma (la rúbrica da 101)", "B",
     cambia("<td><strong>I3</strong></td><td>La autocorrelación global</td><td>8</td>",
            "<td><strong>I3</strong></td><td>La autocorrelación global</td><td>9</td>"), False),
    ("la tabla de pesos con otro porcentaje del corte", "B",
     cambia("<td>15 %</td><td><strong>7,5 %</strong>", "<td>15 %</td><td><strong>8 %</strong>"), False),
    ("los quices con otro peso: el corte ya no suma 100", "B",
     cambia("el otro <strong>50 %</strong>", "el otro <strong>40 %</strong>"), False),
    ("la cabecera con otro peso", "B", cambia("50&nbsp;% DEL CORTE", "20&nbsp;% DEL CORTE"), False),
    ("un descuento tardío compuesto, no sobre la nota original", "B",
     cambia("<tr><td>2</td><td>30 %</td><td>2,8</td></tr>", "<tr><td>2</td><td>30 %</td><td>2,89</td></tr>"), False),
    ("una fila del tope mal calculada", "B",
     sub(r"(Proyecto impecable que no sabe defender</td>.*?<td><strong>)(\d,\d+)(</strong>)", r"\g<1>2,56\3"), False),
    ("una exposición que la rúbrica no puede dar", "B",
     sub(r"(Proyecto impecable que no sabe defender</td><td>\d,\d+</td><td>)\d,\d+", r"\g<1>4,5"), False),
    ("un nivel del componente con puntos que no son puntos × nivel / 5", "B",
     cambia('"rango": "4,9"', '"rango": "5,9"'), False),
    # --- C · Decisiones
    ("tríos en vez de parejas", "C", cambia("individual o en parejas", "individual o en tríos", todas=True), False),
    ("meuse vuelve a valer", "C", cambia("<code>meuse</code>,", ""), False),
    ("otro N mínimo en el módulo 2", "C",
     cambia("<strong>al menos 25 unidades</strong>", "<strong>al menos 20 unidades</strong>"), False),
    ("el ejemplo que no cumple pasa a cumplir", "C",
     cambia("las 20 localidades de Bogotá (20)", "las 20 localidades de Bogotá (26)"), False),
    ("vuelve el examen final", "C", cambia("no tiene examen final", "tiene examen final"), False),
    ("vuelven los Talleres 4 y 5", "C", en_modulo(1, "<p>Los Talleres 4 y 5 valen el 10 % cada uno.</p>"), False),
    ("otro usuario para invitar al docente", "C", cambia("<code>JotaMao1985</code>", "<code>JotaMao1958</code>"), False),
    ("el guion de la exposición se pasa del tiempo", "C",
     cambia("<td>El Moran, su sensibilidad a la W y el mapa LISA corregido</td><td>4</td>",
            "<td>El Moran, su sensibilidad a la W y el mapa LISA corregido</td><td>5</td>"), False),
    ("la declaración de IA deja de ser obligatoria", "C",
     sub(r"la declaración de uso es\s+obligatoria", "la declaración de uso es opcional"), False),
    ("el kriging vuelve a aprobarse como núcleo", "C", cambia("no se aprueba como núcleo", "se aprueba como núcleo"), False),
    # --- D · Estructura
    ("un enlace roto", "D", cambia('href="capitulo-6-pesos-espaciales.html"', 'href="capitulo-6-pesos.html"'), False),
    ("un enlace local con ancla", "D",
     cambia('href="capitulo-6-pesos-espaciales.html"', 'href="capitulo-6-pesos-espaciales.html#modulo-9"'), False),
    ("un id repetido", "D", en_modulo(2, '<span id="dup"></span><span id="dup"></span>'), False),
    ("un resto de la plantilla", "D", en_modulo(3, "<p>PLANTILLA BASE</p>"), False),
    ("mojibake", "D", en_modulo(4, "<p>regiÃ³n</p>"), False),
    ("un «>» sin escapar en el código", "D", cambia("nsim + 1 &gt; 40 N", "nsim + 1 > 40 N"), False),
    ("un selector CSS de más", "D", antes_de_style("\n    .selector-de-mas { color: red; }\n"), False),
    ("una tabla sin caption", "D", en_modulo(6, "<table><tr><td>x</td></tr></table>"), False),
    ("sin el botón al índice", "D", cambia('href="../index.html"', 'href="index.html"'), False),
    # --- E · Código R
    ("un bloque de R que no corre", "E",
     cambia("reina &lt;- poly2nb(unidades, queen = TRUE)", "reina &lt;- poly2nbx(unidades, queen = TRUE)"), True),
    # --- F · Contenido
    ("una referencia a un módulo que trata otra cosa", "F", cambia("El módulo 9 del", "El módulo 8 del"), False),
    ("un módulo citado con otro título", "F", cambia("«Moran es sensible a W»", "«Moran depende de W»"), False),
    ("una casilla de la potencia que no es la del JSON", "F", cambia("<td>46,0 %</td>", "<td>56,0 %</td>"), False),
    ("la prosa lee mal la tabla de potencia", "F",
     cambia("<strong>46 veces de cada 100</strong>", "<strong>56 veces de cada 100</strong>"), False),
    # --- G · Exigencias
    ("el ejemplo de réplicas vuelve a 40·N − 1", "G", sub(rf"nsim ≥\s+1{FINO}320", f"nsim ≥ 1{FINO}319"), False),
    ("las 999 dejan de alcanzar en otro N", "G", cambia("desde 25 unidades", "desde 30 unidades"), False),
    ("se pierde el aviso del p plegado", "G",
     sub(r"Y el p plegado de GeoDa leído como si fuera el bilateral: marca el\s+10 % como si fuera el 5 %\.", ""), False),
    ("I6 deja de nombrar la falacia ecológica", "G",
     cambia("la escala, la falacia ecológica y la potencia", "la escala y la potencia"), False),
    # La revisión de contenido del 21 oct 2026: cada defecto devuelve el texto de antes.
    ("vuelven los vecinos en grados como error", "G",
     en_modulo(5, "<p>Los vecinos en grados son otros vecinos: knearneigh() mide distancias que no son distancias.</p>"), False),
    ("vuelve el umbral de 64 para leer la potencia", "G",
     cambia("un Moran no significativo nunca se lee", "con menos de 64 unidades, un Moran no significativo no se lee"), False),
    # --- H · Conjunta
    ("el enlace a Series apunta a otro módulo", "H", cambia("#modulo-8", "#modulo-7"), False),
    ("una regla de la conjunta copiada aquí", "H", en_modulo(8, "<p>El informe conjunto tiene hasta 15 páginas.</p>"), False),
    ("las preguntas de la conjunta por su letra", "H",
     en_modulo(8, "<p>Se elige la pregunta (a) o la (b).</p>"), False),
    ("ya no dice que las reglas viven solo en Series", "H", cambia("solo ese módulo", "ese módulo"), False),
    ("se pierde el aviso del autoplagio", "H", cambia("autoplagio", "un descuido", todas=True), False),
    ("se pierde el acuerdo individual por escrito", "H",
     cambia("o con un <strong>acuerdo individual por\n          escrito</strong> con el docente, que fija las suyas",
            "y en ningún otro caso"), False),
    ("vuelve la «única excepción»", "H",
     cambia("<strong>Fuera de esto, es autoplagio.</strong>", "<strong>Es la única excepción.</strong>"), False),
    ("I4 pierde su descriptor de la conjunta", "H", cambia("<strong>En la conjunta:</strong> el LISA", "El LISA"), False),
    # --- E · La plantilla (PROYECTO_RMD)
    ("la plantilla vuelve a escribir los datos de ejemplo en datos/", "E", "rmd",
     cambia('  unidades$tasa <- 1000 * unidades$SID79 / unidades$BIR79\n',
            '  unidades$tasa <- 1000 * unidades$SID79 / unidades$BIR79\n'
            '  dir.create("datos", showWarnings = FALSE); st_write(unidades, "datos/ejemplo.gpkg", quiet = TRUE)\n')),
    ("la plantilla pierde el aviso de los datos de ejemplo", "E", "rmd",
     cambia('if (ejemplo) cat(', 'if (FALSE) cat(')),
    ("la plantilla vuelve al alto-bajo naranja", "E", "rmd", cambia('"#f4a582"', '"#fdae61"')),
    ("la plantilla vuelve a pintar las islas como no significativas", "E", "rmd",
     cambia('ifelse(is.na(p), "Isla (sin vecinos)",', 'ifelse(FALSE, "Isla (sin vecinos)",')),
    ("la plantilla vuelve a pedir copiar el conteo a mano", "E", "rmd",
     cambia("Di por qué se perdió cada una.", "Copia aquí lo que imprime R/datos.R. Di por qué se perdió cada una.")),
]


def audita(ruta: pathlib.Path, con_r: bool, rmd: pathlib.Path | None = None) -> tuple[int, set, str]:
    env = dict(os.environ, PROYECTO_HTML=str(ruta), PROYECTO_SIN_R="0" if con_r else "1")
    if rmd:
        env["PROYECTO_RMD"] = str(rmd)
    r = subprocess.run([sys.executable, str(AUDITOR)], env=env, capture_output=True, text=True)
    frentes = set(re.findall(r"^  MAL \[([A-H])\]", r.stdout, re.M))
    return r.returncode, frentes, r.stdout


def main() -> int:
    original = PUBLICADO.read_text(encoding="utf-8")
    fallos = []
    with tempfile.TemporaryDirectory() as tmp:
        copia = pathlib.Path(tmp) / "guia.html"

        def control(cuando: str) -> None:
            copia.write_text(original, encoding="utf-8")
            rc, fr, _ = audita(copia, con_r=False)
            ok = rc == 0 and not fr
            print(f"  {'OK ' if ok else 'MAL'}  control limpio ({cuando})")
            if not ok:
                fallos.append(f"control {cuando}: {sorted(fr)}")

        print("=== prueba_auditor_proyecto.py ===\n")
        control("antes")
        rmd = pathlib.Path(tmp) / "plantilla.Rmd"
        for nombre, frente, transforma, con_r in DEFECTOS:
            if transforma == "rmd":
                copia.write_text(original, encoding="utf-8")
                rmd.write_text(con_r(RMD_FUENTE.read_text(encoding="utf-8")), encoding="utf-8")
                rc, fr, _ = audita(copia, True, rmd)
            else:
                copia.write_text(transforma(original), encoding="utf-8")
                rc, fr, _ = audita(copia, con_r)
            ok = rc == 1 and frente in fr
            print(f"  {'OK ' if ok else 'MAL'}  [{frente}] {nombre}"
                  + ("" if ok else f"  (salida {rc}, frentes {sorted(fr)})"))
            if not ok:
                fallos.append(nombre)
        control("después")

    cazados = len(DEFECTOS) - len([f for f in fallos if not f.startswith("control")])
    print(f"\n  {len(DEFECTOS)} defectos inyectados · {cazados} cazados por su frente")
    if fallos:
        print("\nNo cazados o controles sucios:")
        for f in fallos:
            print(f"  · {f}")
        return 1
    print("Todo cazado.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
