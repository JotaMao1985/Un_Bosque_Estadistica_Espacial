#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""El banco de Brightspace contrastado contra el documento del que salió.

`audita_paquete.py` —el de la skill— comprueba que el ZIP sea un paquete D2L
coherente: identificadores únicos, puntuación en todas las opciones, la retro
enlazada, las imágenes declaradas donde están. Todo eso puede estar perfecto y
el banco seguir mal de la única manera que importa: **con la clave equivocada**.
Ningún auditor que solo mire el ZIP puede verlo, porque dentro del ZIP no hay
nada con qué contrastarla.

Esto lo hace: vuelve a leer el HTML publicado, lee el ZIP por su lado con un
analizador de XML —no con el código que lo escribió— y los enfrenta.

    · cobertura: ninguna pregunta se perdió por el camino sin decirlo
    · el texto de las opciones, uno a uno
    · QUÉ opciones puntúan, contra las `correcta: true` del documento
    · la retroalimentación de cada opción, contra la suya
    · Multi-Select si y solo si la pregunta era de varias respuestas
    · las numéricas convertidas: la correcta dentro de su tolerancia y
      **todos los distractores fuera**, que es lo que hace la pregunta
      contestable
    · las imágenes citadas, presentes en el ZIP y en el manifiesto

Uso:

    precalculo/audita_brightspace.py \
        --html Htmls_Espacial/preparcial-corte-1.html \
        --datos precalculo/salidas/preparcial1_datos.json \
        --zip parcial/brightspace/banco_brightspace.zip
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "precalculo"))

from audita_base import Auditoria            # noqa: E402
from audita_preparcial1 import lee_autoevaluaciones   # noqa: E402

D2L = "{http://desire2learn.com/xsd/d2lcp_v2p0}"


# =====================================================================
# EL LADO DEL ZIP — leído con ElementTree, no con el guion que lo escribió
# =====================================================================
def lee_paquete(ruta: str) -> tuple[dict, set, set]:
    with zipfile.ZipFile(ruta) as z:
        xml = z.read("questiondb.xml").decode("utf-8")
        manifiesto = z.read("imsmanifest.xml").decode("utf-8")
        dentro = {n for n in z.namelist() if n.startswith("images/")}

    raiz = ET.fromstring(xml)
    items = {}
    for it in raiz.iter("item"):
        et = it.get("label")
        lid = it.find(".//response_lid")
        opciones = {}
        for rl in it.iter("response_label"):
            opciones[rl.get("ident")] = rl.find(".//mattext").text or ""
        puntos, retro_de = {}, {}
        for rc in it.iter("respcondition"):
            ve = rc.find(".//varequal")
            if ve is None:
                continue
            puntos[ve.text] = float(rc.find("setvar").text)
            df = rc.find("displayfeedback")
            if df is not None:
                retro_de[ve.text] = df.get("linkrefid")
        retros = {fb.get("ident"): (fb.find(".//mattext").text or "")
                  for fb in it.iter("itemfeedback")}
        items[et] = {
            "titulo": it.get("title"),
            "enunciado": it.find(".//presentation//mattext").text or "",
            "cardinalidad": lid.get("rcardinality"),
            "opciones": opciones,
            "puntos": puntos,
            "retro": {opciones[k]: retros.get(v, "") for k, v in retro_de.items()},
            "correctas": {opciones[k] for k, v in puntos.items() if v > 0},
            "orden": list(opciones.values()),
        }
    citadas = set(re.findall(r'src="(images/[^"]+)"', xml))
    en_manifiesto = set(re.findall(r'href="(images/[^"]+)"', manifiesto))
    return items, citadas, dentro & en_manifiesto


# =====================================================================
def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--html", required=True)
    p.add_argument("--datos", required=True)
    p.add_argument("--zip", required=True)
    a = p.parse_args()

    html = Path(a.html).read_text(encoding="utf-8")
    datos = json.loads(Path(a.datos).read_text(encoding="utf-8"))
    bloques = lee_autoevaluaciones(html)
    items, citadas, presentes = lee_paquete(a.zip)

    au = Auditoria("Banco contrastado contra su documento")

    # --- 1 · cobertura -------------------------------------------------
    au.titulo("1 · cobertura")
    esperadas, ausentes = {}, []
    for nombre, preguntas in bloques.items():
        letra = nombre.split("-")[-1].upper()
        for i, q in enumerate(preguntas, 1):
            et = f"EE_C1_{letra}{i:02d}"
            esperadas[et] = q
            if et not in items:
                ausentes.append((et, q["tipo"]))
    au.cierto(all(t == "numerica" for _, t in ausentes),
              "lo que falta del banco es solo numérica",
              f"{len(ausentes)} fuera: " + ", ".join(f"{e}({t})" for e, t in ausentes))
    au.cierto(not (set(items) - set(esperadas)),
              "el banco no trae nada que el documento no publique",
              f"sobran {sorted(set(items) - set(esperadas))}")
    au.cierto(len(items) + len(ausentes) == sum(len(v) for v in bloques.values()),
              "las cuentas cuadran",
              f"{len(items)} en el banco + {len(ausentes)} fuera = "
              f"{sum(len(v) for v in bloques.values())}")

    # --- 2 · las preguntas con opciones --------------------------------
    au.titulo("2 · opciones, clave y retroalimentación")
    for et, it in sorted(items.items()):
        q = esperadas[et]
        if q["tipo"] == "numerica":
            continue
        fuente = {o["texto"]: o for o in q["opciones"]}
        au.cierto(set(it["opciones"].values()) == set(fuente),
                  f"[{et}] las opciones son las del documento",
                  f"{len(it['opciones'])} contra {len(fuente)}")
        au.cierto(it["correctas"] == {t for t, o in fuente.items() if o["correcta"]},
                  f"[{et}] la clave es la del documento",
                  f"{len(it['correctas'])} correcta(s)")
        malas = [t for t, r in it["retro"].items()
                 if t in fuente and r != fuente[t]["retro"]]
        au.cierto(not malas, f"[{et}] cada retro es la de SU opción",
                  f"{len(malas)} descolocada(s)")
        esperada = "Multiple" if q["tipo"] == "multiple" else "Single"
        au.cierto(it["cardinalidad"] == esperada,
                  f"[{et}] la forma corresponde al tipo",
                  f"{it['cardinalidad']} para «{q['tipo']}»")
        au.cierto(q["pregunta"] in it["enunciado"],
                  f"[{et}] el enunciado es el del documento")

    # --- 3 · las numéricas convertidas ---------------------------------
    au.titulo("3 · las numéricas convertidas a opción múltiple")
    convertidas = [et for et, q in esperadas.items()
                   if q["tipo"] == "numerica" and et in items]
    if not convertidas:
        au.salta("las numéricas convertidas", "no hay ninguna en este banco")
    for et in sorted(convertidas):
        q, it = esperadas[et], items[et]
        tol = q["tolerancia"]
        correcta = float(next(iter(it["correctas"])).replace(",", ""))
        au.cierto(abs(correcta - q["respuesta"]) <= tol,
                  f"[{et}] la correcta cae dentro de la tolerancia",
                  f"{correcta} contra {q['respuesta']} ± {tol}")
        dentro = [t for t in it["opciones"].values()
                  if t not in it["correctas"]
                  and abs(float(t.replace(",", "")) - q["respuesta"]) <= tol]
        # Un distractor dentro de la tolerancia haría la pregunta imposible:
        # dos opciones serían la respuesta y solo una puntuaría.
        au.cierto(not dentro, f"[{et}] ningún distractor cae dentro",
                  f"{dentro}" if dentro else "")
        au.cierto(len(it["opciones"]) == 4, f"[{et}] cuatro opciones",
                  str(len(it["opciones"])))

    # --- 4 · las imágenes ----------------------------------------------
    au.titulo("4 · las imágenes")
    au.cierto(citadas <= presentes,
              "toda imagen citada está en el ZIP y en el manifiesto",
              f"faltan {sorted(citadas - presentes)}" if citadas - presentes
              else f"{len(citadas)} citada(s)")
    au.cierto(presentes <= citadas, "y no sobra ninguna",
              f"sobran {sorted(presentes - citadas)}" if presentes - citadas else "")

    # --- 5 · el reparto de la correcta ---------------------------------
    # El preparcial llegó a publicar la correcta SIEMPRE la primera (§12.6 de
    # su plan). D2L baraja al servir, pero un banco que la deje concentrada
    # se puede acabar usando en un sitio que no baraje.
    au.titulo("5 · el reparto de la respuesta correcta")
    reparto = {}
    unicas = [it for et, it in items.items() if it["cardinalidad"] == "Single"]
    for it in unicas:
        pos = it["orden"].index(next(iter(it["correctas"]))) + 1
        reparto[pos] = reparto.get(pos, 0) + 1
    au.cierto(max(reparto.values()) <= len(unicas) * 0.5,
              "no se concentra en una posición",
              " · ".join(f"{k}: {v}" for k, v in sorted(reparto.items()))
              + f"  (de {len(unicas)})")
    au.cierto(len(reparto) >= 3, "y ocupa al menos tres posiciones",
              f"{len(reparto)}")

    return au.cierre()


if __name__ == "__main__":
    sys.exit(main())
