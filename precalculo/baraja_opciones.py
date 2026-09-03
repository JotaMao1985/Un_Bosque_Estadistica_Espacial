#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""El orden de las opciones de una autoevaluación, decidido aquí.

QUÉ ARREGLA
La revisión del capítulo 5 (2026-09-02) contó las posiciones sobre los cinco
capítulos publicados y encontró lo mismo que el preparcial había encontrado el
26 de agosto: **la respuesta correcta caía la primera en las 51 preguntas con
opciones**, 100 % en los cinco. El motor no baraja —`renderAutoevaluacion()`
dibuja `p.opciones.map((op, j) => …)` en el orden escrito—, así que las cinco
autoevaluaciones se aprobaban marcando siempre la (a), sin leer una palabra.

Cada pregunta era impecable por separado: cuatro opciones distintas, una sola
correcta, cuatro retroalimentaciones distintas. **El defecto solo existe en el
agregado**, y en el agregado no miraba nadie. Es la misma clase que el §12.6
del preparcial dejó dicha: hay defectos que no están en ninguna pieza y están
en el montón.

POR QUÉ AQUÍ Y NO EN CADA ENSAMBLADOR
El preparcial baraja sus preguntas como estructuras de Python, porque allí las
preguntas SON estructuras de Python. En los capítulos el cuestionario se emite
como texto JavaScript —y el del capítulo 3 vive dentro de una f-string, con sus
llaves dobladas—, así que no hay una estructura común que barajar. Lo que sí es
común es **el documento ya escrito**, y ahí es donde entra esto: se llama con el
HTML completo, justo antes de guardarlo, y vale igual para los cinco.

POR QUÉ BARAJAR Y NO REORDENAR A MANO
Lo dice el §12.6 y se cumplió al pie de la letra: «un orden escrito a mano hay
que mantenerlo, y la pregunta que se escriba mañana nacerá otra vez con la
correcta delante: es lo natural, primero se piensa la respuesta y luego los
distractores». El capítulo 5 se escribió CUATRO DÍAS después de aquella lección
y nació con el defecto entero.

REPRODUCIBLE BYTE A BYTE
La semilla sale del documento, del bloque y del número de la pregunta, así que
el orden es el mismo en cada reensamblado y **añadir una pregunta no reordena
las demás**. No se usa el reloj ni el azar del sistema.

LA CONSECUENCIA QUE HAY QUE RESPETAR AL REDACTAR
Ninguna retroalimentación puede nombrar una posición. «Las correctas son la
primera y la tercera» deja de ser cierto en cuanto esto corre, y es falso de la
peor manera: **sigue leyéndose bien**. Lo vigila `POSICIONALES`, y el
ensamblador para si aparece una.

Uso:
    from baraja_opciones import baraja_documento
    doc = baraja_documento(doc, "cap5")          # antes de escribir el archivo

    python3 precalculo/baraja_opciones.py --prueba
"""
from __future__ import annotations

import random
import re
import sys

# =====================================================================
# LAS FORMAS DE NOMBRAR UNA POSICIÓN
#
# Las cinco primeras vienen del preparcial, que las estrenó cazando catorce.
# La sexta es de la revisión del capítulo 5: allí las tres que había decían
# «Las correctas son la primera y la tercera», que ninguna de las cinco veía.
#
# Los patrones nombran LA OPCIÓN, no la palabra suelta: «la primera pregunta
# ante una diferencia», «Módulo 1, la segunda mitad» y «la primera clase» son
# español correcto y no son posiciones.
# =====================================================================
POSICIONALES = [
    re.compile(r"\blas (dos|tres|cuatro) primeras\b", re.I),
    re.compile(r"\bla (primera|segunda|tercera|cuarta|última) opción\b", re.I),
    re.compile(r"\bla opción [a-d]\)", re.I),
    re.compile(r"\blas primeras\b", re.I),
    re.compile(r"\bla de arriba\b|\bla de abajo\b", re.I),
    re.compile(r"\b(las correctas son|la correcta es|son)\s+(la|las)\s+"
               r"(primera|segunda|tercera|cuarta|última)\b", re.I),
]

# Los campos de una pregunta que lee un estudiante. `respuesta` está aquí
# porque los capítulos 3 y 4 usan ese nombre (la deuda A.23.2): aunque hoy no
# se dibujen, si algún día se arreglan no pueden estrenarse mintiendo.
CAMPOS_DE_TEXTO = ("pregunta", "pista", "retro", "respuesta", "explicacion",
                   "retroAcierto", "retroFallo")

_PAREJA = {"{": "}", "[": "]"}


def _fin(txt: str, i: int) -> int:
    """Índice siguiente al bloque que abre en `txt[i]`.

    Respeta las cadenas de JavaScript —el material escribe `'...'` con
    comillas dobles dentro, y a veces llaves— y los comentarios de línea. Un
    contador de llaves a secas se rompe con `factor(c("oficial", "privado"))`
    el día que alguien meta una llave en un texto.
    """
    abre = txt[i]
    cierra = _PAREJA[abre]
    hondo = 0
    j = i
    while j < len(txt):
        c = txt[j]
        if c in "\"'":
            comilla = c
            j += 1
            while j < len(txt):
                if txt[j] == "\\":
                    j += 2
                    continue
                if txt[j] == comilla:
                    break
                j += 1
        elif c == "/" and txt[j + 1:j + 2] == "/":
            salto = txt.find("\n", j)
            j = len(txt) if salto < 0 else salto
            continue
        elif c == abre:
            hondo += 1
        elif c == cierra:
            hondo -= 1
            if hondo == 0:
                return j + 1
        j += 1
    raise ValueError(f"bloque «{abre}» sin cerrar en la posición {i}")


def _bloques(txt: str, ini: int, fin: int) -> list[tuple[int, int]]:
    """Los `{...}` de primer nivel dentro de `txt[ini:fin]`."""
    fuera = []
    j = ini
    while j < fin:
        c = txt[j]
        if c in "\"'":
            comilla = c
            j += 1
            while j < fin:
                if txt[j] == "\\":
                    j += 2
                    continue
                if txt[j] == comilla:
                    break
                j += 1
        elif c == "{":
            k = _fin(txt, j)
            fuera.append((j, k))
            j = k
            continue
        j += 1
    return fuera


def _campo(bloque: str, nombre: str) -> str:
    """El texto crudo de un campo, con sus concatenaciones y todo, o ''."""
    m = re.search(rf"\b{nombre}\s*:\s*", bloque)
    if not m:
        return ""
    j = m.end()
    trozos = []
    while j < len(bloque):
        c = bloque[j]
        if c in "\"'":
            k = j + 1
            while k < len(bloque):
                if bloque[k] == "\\":
                    k += 2
                    continue
                if bloque[k] == c:
                    break
                k += 1
            trozos.append(bloque[j + 1:k])
            j = k + 1
        elif c in ",}":
            break
        else:
            j += 1
    return " ".join(trozos)


def _revisa_posiciones(bloque: str, ref: str, problemas: list) -> None:
    for campo in CAMPOS_DE_TEXTO:
        for m in re.finditer(rf"\b{campo}\s*:\s*", bloque):
            texto = _campo(bloque[m.start():], campo)
            for pat in POSICIONALES:
                hit = pat.search(texto)
                if hit:
                    problemas.append(
                        f"{ref}: «{hit.group(0)}» en `{campo}` nombra una posición, "
                        f"y las opciones van barajadas")
                    break


def baraja_documento(doc: str, ident_doc: str, verboso: bool = True) -> str:
    """Baraja las opciones de todas las autoevaluaciones del documento.

    Devuelve el documento nuevo. Para el proceso —`sys.exit`— si alguna
    retroalimentación nombra una posición, porque publicarla barajada la
    convierte en mentira y nadie volvería a mirarla.
    """
    problemas: list[str] = []
    reparto: dict[int, int] = {}
    n_preguntas = 0
    fuera = []
    pos = 0

    for m in re.finditer(r"\n    AUTOEVALUACIONES\['([^']+)'\] = \[", doc):
        clave = m.group(1)
        ini = doc.index("[", m.end() - 1)
        fin = _fin(doc, ini)
        fuera.append(doc[pos:ini + 1])
        cuerpo_ini, cuerpo_fin = ini + 1, fin - 1
        preguntas = _bloques(doc, cuerpo_ini, cuerpo_fin)
        trozo = []
        anterior = cuerpo_ini
        for n, (qi, qf) in enumerate(preguntas, 1):
            trozo.append(doc[anterior:qi])
            bloque = doc[qi:qf]
            ref = f"{ident_doc}·{clave} #{n}"
            _revisa_posiciones(bloque, ref, problemas)
            bloque = _baraja_bloque(bloque, f"{ident_doc}·{clave}·{n}", ref,
                                    reparto, problemas)
            if "opciones" in bloque:
                n_preguntas += 1
            trozo.append(bloque)
            anterior = qf
        trozo.append(doc[anterior:cuerpo_fin])
        fuera.append("".join(trozo))
        pos = cuerpo_fin

    fuera.append(doc[pos:])
    nuevo = "".join(fuera)

    if problemas:
        sys.exit("PARADO: la autoevaluación no se puede barajar tal como está.\n  - "
                 + "\n  - ".join(problemas))

    if verboso and n_preguntas:
        cuenta = " · ".join(f"{k}: {v}" for k, v in sorted(reparto.items()))
        print(f"  Opciones barajadas en {n_preguntas} preguntas · "
              f"la correcta cae en {cuenta}")
    return nuevo


def _baraja_bloque(bloque: str, semilla: str, ref: str,
                   reparto: dict, problemas: list) -> str:
    """Una pregunta: reordena su lista `opciones` y anota dónde cae la correcta."""
    m = re.search(r"\bopciones\s*:\s*\[", bloque)
    if not m:
        return bloque                      # numérica: no tiene opciones
    ini = bloque.index("[", m.end() - 1)
    fin = _fin(bloque, ini)
    ops = _bloques(bloque, ini + 1, fin - 1)
    if len(ops) < 2:
        problemas.append(f"{ref}: {len(ops)} opción(es); se esperaban al menos 2")
        return bloque

    textos = [bloque[a:b] for a, b in ops]
    separadores = [bloque[ops[i][1]:ops[i + 1][0]] for i in range(len(ops) - 1)]
    cabeza = bloque[ini + 1:ops[0][0]]
    cola = bloque[ops[-1][1]:fin - 1]

    orden = list(range(len(textos)))
    random.Random(semilla).shuffle(orden)
    nuevos = [textos[i] for i in orden]

    # Dónde quedó la correcta, para el recuento del ensamblador. En las
    # `multiple` cuentan todas.
    for j, t in enumerate(nuevos, 1):
        if re.search(r"\bcorrecta\s*:\s*true\b", t):
            reparto[j] = reparto.get(j, 0) + 1

    sep = separadores[0] if separadores else ",\n          "
    cuerpo = cabeza + sep.join(nuevos) + cola
    return bloque[:ini + 1] + cuerpo + bloque[fin - 1:]


# =====================================================================
# EL ARNÉS. Cuatro cosas, y las cuatro han fallado en algún material de la
# casa o son la razón de que esto exista.
# =====================================================================
def _prueba() -> int:
    fallos = []

    def exige(cond, que):
        print(("  OK   " if cond else "  FALLA ") + que)
        if not cond:
            fallos.append(que)

    doc = """
    AUTOEVALUACIONES['x-quiz'] = [
      {
        tipo: 'opcion',
        pregunta: '¿Cuál?',
        opciones: [
          { texto: 'La buena, con una llave { dentro y un "entrecomillado"', correcta: true,
            retro: 'Eso es.' },
          { texto: 'Mala 1', retro: 'No.' },
          { texto: 'Mala 2', retro: 'Tampoco.' },
          { texto: 'Mala 3', retro: 'Menos.' }
        ] },
      {
        tipo: 'numerica',
        pregunta: '¿Cuánto?', respuesta: 3, tolerancia: 1
      }
    ];
"""
    a = baraja_documento(doc, "cap0", verboso=False)
    b = baraja_documento(doc, "cap0", verboso=False)
    exige(a == b, "dos pasadas dan el mismo orden (reproducible byte a byte)")
    exige(a != doc, "el orden cambia: la correcta ya no es la primera")
    exige(baraja_documento(doc, "cap9", verboso=False) != a,
          "cada documento tiene su propia permutación")
    for texto in ("La buena", "Mala 1", "Mala 2", "Mala 3"):
        exige(a.count(texto) == doc.count(texto), f"«{texto}» sigue una sola vez")
    exige(a.count("correcta: true") == 1, "sigue habiendo exactamente una correcta")
    exige("tipo: 'numerica'" in a and "respuesta: 3" in a,
          "la numérica, que no tiene opciones, se queda como estaba")
    exige('llave { dentro y un "entrecomillado"' in a,
          "una llave dentro de una cadena no rompe el escaneo")

    # Añadir una pregunta en otro bloque no puede reordenar las de este.
    doc2 = doc.replace("    AUTOEVALUACIONES['x-quiz']",
                       "    AUTOEVALUACIONES['x-otro'] = [\n      {\n"
                       "        tipo: 'opcion', pregunta: '¿Y?',\n"
                       "        opciones: [\n          { texto: 'A', correcta: true },\n"
                       "          { texto: 'B' }\n        ] }\n    ];\n"
                       "    AUTOEVALUACIONES['x-quiz']")
    trozo = lambda t: t[t.index("x-quiz"):]
    exige(trozo(baraja_documento(doc2, "cap0", verboso=False)) == trozo(a),
          "añadir un bloque nuevo no reordena el que ya estaba")

    # La guarda de las posiciones.
    malo = doc.replace("retro: 'Eso es.'", "retro: 'Las correctas son la primera y la tercera.'")
    try:
        baraja_documento(malo, "cap0", verboso=False)
        exige(False, "una retroalimentación que nombra una posición para el ensamblado")
    except SystemExit as e:
        exige("nombra una posición" in str(e),
              "una retroalimentación que nombra una posición para el ensamblado")

    # Y lo que NO es una posición no puede dispararla.
    bueno = doc.replace("retro: 'Eso es.'",
                        "retro: 'Eso es. La primera pregunta ante una diferencia es de dónde sale.'")
    try:
        baraja_documento(bueno, "cap0", verboso=False)
        exige(True, "«la primera pregunta» no es una posición y no dispara la guarda")
    except SystemExit:
        exige(False, "«la primera pregunta» no es una posición y no dispara la guarda")

    print(f"\n{'FALLA' if fallos else 'OK'} · baraja_opciones.py · "
          f"{len(fallos)} fallo(s)")
    return 1 if fallos else 0


if __name__ == "__main__":
    sys.exit(_prueba() if "--prueba" in sys.argv else
             print(__doc__) or 0)
