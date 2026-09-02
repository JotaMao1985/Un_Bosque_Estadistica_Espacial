#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""censo_banco.py — cuántas preguntas hay, de qué módulo y cuáles llevan cifra

Material de Estadística Espacial 2026-II (20929).

QUÉ ES Y POR QUÉ EXISTE

La decisión del parcial 2 —individualizar por SELECCIÓN o por DATOS— no es de
criterio, es aritmética, y la aritmética necesita tres números que hoy nadie ha
contado:

  1. cuántos ítems hay por celda del temario;
  2. cuántos de ellos BEBEN DEL PRECÁLCULO, que son los que la máquina de
     variantes del Taller 1 individualiza gratis;
  3. cuántos son prosa pura, que solo se individualizan escribiendo más.

Sin (2) y (3) la conversación se queda en «hay 96 preguntas», que es verdad y
no sirve para decidir nada.

DE DÓNDE SALE EL DATO

Del **HTML publicado**, que es la superficie que el estudiante vio, por el
mismo motivo que la usan `audita_preparcial1.py` y `exporta_brightspace.py`.
Los títulos de módulo se leen del `courseData`; aquí no se escribe ninguno.

LAS DOS FUENTES NO GUARDAN LO MISMO, Y SE DICE

  · Los capítulos son JS escrito a mano: el enunciado es una concatenación
    viva —`'... ' + n5(D4.m1.urbana.lambda_km2, 4) + ' ...'`— así que la
    referencia al precálculo SIGUE AHÍ y el módulo se lee de ella.
  · El preparcial lo ensambla Python con f-strings: al publicarse, la cifra ya
    está horneada y la ruta se perdió. A cambio, cada pregunta declara su
    `repaso`, y de ahí sale el módulo.

Ninguna de las dos se rellena con la otra. La columna «bebe del precálculo» es
EXACTA en los capítulos y NO MEDIBLE en el preparcial, y la tabla lo dice en
vez de poner un cero que se leería como «ninguna».

Uso:
    python3 precalculo/censo_banco.py             # las tres tablas
    python3 precalculo/censo_banco.py --json      # lo mismo, para otra máquina
    python3 precalculo/censo_banco.py --examen 20 --alumnos 12
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys
from collections import Counter, defaultdict

RAIZ = pathlib.Path(__file__).resolve().parent.parent
HTMLS = RAIZ / "Htmls_Espacial"
sys.path.insert(0, str(RAIZ / "precalculo"))

# El analizador de literales de JavaScript vive en el auditor del preparcial y
# de ahí se importa, por lo mismo que lo importa `exporta_brightspace.py`: dos
# copias de un convenio se desincronizan sin que nada falle.
from audita_preparcial1 import lee_autoevaluaciones  # noqa: E402
import alcance_preparcial1 as alc  # noqa: E402

DOCS = {
    "cap1": "capitulo-1-datos-espaciales.html",
    "cap2": "capitulo-2-crs-georreferenciacion.html",
    "cap3": "capitulo-3-cartografia-maup.html",
    "cap4": "capitulo-4-patrones-puntuales.html",
    "cap5": "capitulo-5-intensidad-nucleos.html",
}
PREPARCIAL = "preparcial-corte-1.html"

# Los dos capítulos que evalúa el parcial del Corte II. Es la única cifra de
# alcance que este guion declara, y es la decisión de §0.4 del plan.
CORTE_II = ["cap4", "cap5"]

# =====================================================================
# LAS CUATRO FORMAS DE CITAR EL PRECÁLCULO, QUE SON CUATRO Y NO UNA
#
# Medido, no supuesto (2026-08-31), sobre los cinco capítulos publicados:
#
#     cap1  D1.<tema>          58 referencias, NO indexadas por módulo
#     cap2  DATOS_CAP2.<tema>  NO indexadas por módulo
#     cap3  D3.mN              22, indexadas por módulo
#     cap4  D4.mN              40, indexadas por módulo
#     cap5  D5.mN              58, indexadas por módulo
#
# Importa aquí porque una expresión que solo entienda `DN.mN` daría CERO en
# los capítulos 1 y 2, y un cero se lee como «ninguna pregunta lleva cifra»
# cuando lo cierto es «no sé leerlas». Por eso la raíz se declara por capítulo
# y se comprueba: si un capítulo cita una raíz que no está en esta tabla, el
# censo PARA en vez de contar de menos.
# =====================================================================
RAICES = {"cap1": "D1", "cap2": "DATOS_CAP2", "cap3": "D3",
          "cap4": "D4", "cap5": "D5"}

_RE_RAIZ = re.compile(r"\b(D\d+|DATOS_CAP\d+)\.")

_RE_MODULO = re.compile(r'\{\s*id:\s*(\d+)\s*,\s*title:\s*"((?:[^"\\]|\\.)*)"')
_RE_REF = re.compile(r"\bD(\d+)\.m(\d+)\b")
_RE_ETIQUETA = re.compile(r"Cap\.\s*(\d+)\s*·\s*módulo\s*(\d+)")
_RE_ORDEN = re.compile(r"'orden':\s*(\d+)")


def _para(mensaje: str) -> None:
    sys.exit(f"PARADO · censo_banco: {mensaje}")


def _html(archivo: str) -> str:
    ruta = HTMLS / archivo
    if not ruta.exists():
        _para(f"falta el documento publicado {ruta.relative_to(RAIZ)}")
    return ruta.read_text(encoding="utf-8")


# =====================================================================
# LOS MÓDULOS, LEÍDOS DEL courseData
#
# `alcance_preparcial1.modulos()` hace exactamente esto para los capítulos 1
# a 3. No se le puede pedir el 4 ni el 5 —su `DOCS` es el alcance del Corte I,
# y ampliárselo cambiaría lo que ese archivo afirma—, así que la lectura se
# repite aquí y SE CONTRASTA contra la suya donde las dos existen. Repetir un
# convenio sin contrastarlo es el defecto que este repositorio persigue;
# repetirlo con un careo delante es tener dos testigos.
# =====================================================================
def modulos(doc: str) -> list[dict]:
    h = _html(DOCS[doc])
    i = h.find("const courseData")
    if i < 0:
        _para(f"{DOCS[doc]} no declara `courseData`")
    bloque = h[i:h.find("};", i)]
    mods = [{"id": int(n), "titulo": t} for n, t in _RE_MODULO.findall(bloque)]
    if not mods:
        _para(f"{DOCS[doc]} declara `courseData` sin módulos legibles")
    if [m["id"] for m in mods] != list(range(1, len(mods) + 1)):
        _para(f"{DOCS[doc]} no numera sus módulos 1..N")
    if doc in alc.DOCS:
        suyos = [(m["id"], m["titulo"]) for m in alc.modulos(doc)]
        if suyos != [(m["id"], m["titulo"]) for m in mods]:
            _para(f"{doc}: leo módulos distintos que `alcance_preparcial1`. "
                  "Uno de los dos lectores está mal y no sé cuál")
    return mods


# =====================================================================
# UNA PREGUNTA, NORMALIZADA
# =====================================================================
def _limpia(v) -> str:
    """El texto de un literal de JS tal como lo devolvió el analizador."""
    t = str(v).strip()
    if len(t) >= 2 and t[0] == t[-1] and t[0] in "'\"":
        return t[1:-1]
    return t


def _opciones(q) -> list[dict]:
    ops = q.get("opciones")
    return ops if isinstance(ops, list) else []


def _es_correcta(o) -> bool:
    v = o.get("correcta", False)
    return v is True or str(v).strip().lower() == "true"


def _explicacion(o) -> str:
    """La retro por opción. Los capítulos la llaman `respuesta`; el
    preparcial, `retro`. Se aceptan las dos y se cuenta cuántas hay, porque
    una opción sin explicación no puede viajar al banco del LMS."""
    for k in ("retro", "respuesta"):
        if k in o and _limpia(o[k]).strip():
            return _limpia(o[k])
    return ""


def _fuente_bruta(q) -> str:
    """Todo el texto crudo de la pregunta: enunciado, opciones y explicaciones.

    Crudo a propósito: es donde sobreviven las referencias `D4.m1...`, que es
    lo único que dice de qué precálculo bebe el ítem."""
    trozos = [str(q.get("pregunta", "")), str(q.get("pista", "")),
              str(q.get("explicacion", "")), str(q.get("retroAcierto", "")),
              str(q.get("retroFallo", "")), str(q.get("respuesta", ""))]
    for o in _opciones(q):
        trozos += [str(o.get("texto", "")), str(o.get("retro", "")),
                   str(o.get("respuesta", ""))]
    return " ".join(trozos)


def _modulos_preparcial(q) -> list[tuple[str, int]]:
    """El módulo que la pregunta manda repasar, con su etiqueta de careo.

    `orden` es 100·capítulo + módulo, y `etiqueta` lo dice en prosa. Se
    comprueban el uno contra la otra: si algún día dejan de coincidir, el
    resumen de «qué repasar» está mandando a un sitio y diciendo otro."""
    bruto = str(q.get("repaso", ""))
    mo = _RE_ORDEN.search(bruto)
    me = _RE_ETIQUETA.search(bruto)
    if not mo or not me:
        _para(f"una pregunta del preparcial no declara `repaso` legible: {bruto[:80]}")
    orden = int(mo.group(1))
    cap, mod = orden // 100, orden % 100
    if (cap, mod) != (int(me.group(1)), int(me.group(2))):
        _para(f"repaso incoherente: orden {orden} contra «{me.group(0)}»")
    return [(f"cap{cap}", mod)]


def lee_documento(archivo: str, es_preparcial: bool,
                  doc: str | None = None) -> list[dict]:
    html = _html(archivo)
    bloques = lee_autoevaluaciones(html)
    if not bloques:
        _para(f"{archivo} no publica ninguna autoevaluación")
    filas = []
    for bloque, preguntas in bloques.items():
        for i, q in enumerate(preguntas, 1):
            ops = _opciones(q)
            bruto = _fuente_bruta(q)
            conteo = Counter((f"cap{c}", int(m)) for c, m in _RE_REF.findall(bruto))
            raices = set(_RE_RAIZ.findall(bruto))
            if doc:
                ajenas = raices - {RAICES[doc]}
                if ajenas:
                    _para(f"{doc} {bloque} #{i} cita raíces que esta tabla no "
                          f"declara: {sorted(ajenas)}. Añádelas a RAICES o "
                          "arréglalas, pero no las cuente de menos en silencio")
            filas.append({
                "archivo": archivo,
                "bloque": bloque,
                "indice": i,
                "tipo": _limpia(q.get("tipo", "opcion")),
                "n_opciones": len(ops),
                "n_correctas": sum(1 for o in ops if _es_correcta(o)),
                "n_explicadas": sum(1 for o in ops if _explicacion(o)),
                # De dónde bebe. En el preparcial la cifra viene horneada por
                # el ensamblador y la ruta ya no está en la página: no es cero,
                # es no medible desde aquí, y así se marca.
                "refs": (_modulos_preparcial(q) if es_preparcial
                         else sorted(conteo)),
                "conteo": ({k: 1 for k in _modulos_preparcial(q)}
                           if es_preparcial else dict(conteo)),
                # «cita» es la señal ancha —¿bebe del precálculo?— y funciona
                # con las cuatro raíces. `conteo` es la estrecha —¿de QUÉ
                # módulo?— y solo existe donde la raíz indexa por módulo.
                "cita": bool(raices) if not es_preparcial else None,
                "medible": not es_preparcial,
            })
    return filas


def primario(fila: dict):
    """El módulo al que se le imputa el ítem cuando toca varios.

    El más referenciado; a igualdad, el menor. Los ítems que tocan más de uno
    se cuentan aparte, para que nadie lea la columna como si cada pregunta
    viviera en un solo sitio."""
    if not fila["conteo"]:
        return None
    return min(fila["conteo"].items(), key=lambda kv: (-kv[1], kv[0]))[0]


# =====================================================================
# EL CENSO
# =====================================================================
def censo() -> dict:
    filas = []
    for doc, archivo in DOCS.items():
        for f in lee_documento(archivo, es_preparcial=False, doc=doc):
            f["doc"] = doc
            filas.append(f)
    for f in lee_documento(PREPARCIAL, es_preparcial=True):
        f["doc"] = "preparcial"
        filas.append(f)
    return {"filas": filas,
            "modulos": {d: modulos(d) for d in DOCS}}


def tabla_inventario(filas: list[dict]) -> None:
    tipos = ["opcion", "multiple", "numerica", "grafico"]
    print("\n1 · INVENTARIO DEL BANCO PUBLICADO\n")
    print(f"  {'documento':<12} {'total':>6} " +
          " ".join(f"{t:>9}" for t in tipos) +
          f" {'expl.':>6} {'cifra':>6}  cómo cita el precálculo")
    print("  " + "-" * 96)
    orden = list(DOCS) + ["preparcial"]
    for doc in orden:
        sub = [f for f in filas if f["doc"] == doc]
        c = Counter(f["tipo"] for f in sub)
        exp = sum(f["n_explicadas"] for f in sub)
        ops = sum(f["n_opciones"] for f in sub)
        if doc == "preparcial":
            cif, conv = "n/d", "cifra horneada · no medible"
        else:
            cif = str(sum(1 for f in sub if f["cita"]))
            modular = any(f["conteo"] for f in sub)
            conv = (f"{RAICES[doc]}.mN · indexado por módulo" if modular
                    else f"{RAICES[doc]}.<tema> · NO indexado por módulo")
        print(f"  {doc:<12} {len(sub):>6} " +
              " ".join(f"{c.get(t, 0):>9}" for t in tipos) +
              f" {exp:>3}/{ops:<2} {cif:>6}  {conv}")
    c = Counter(f["tipo"] for f in filas)
    print("  " + "-" * 96)
    print(f"  {'TOTAL':<12} {len(filas):>6} " +
          " ".join(f"{c.get(t, 0):>9}" for t in tipos) +
          f" {sum(f['n_explicadas'] for f in filas):>3}"
          f"/{sum(f['n_opciones'] for f in filas):<2}")
    huerfanas = [f for f in filas if f["n_opciones"] and
                 f["n_explicadas"] < f["n_opciones"]]
    if huerfanas:
        print(f"\n  ⚠ {len(huerfanas)} preguntas con alguna opción SIN "
              "explicación: no pueden viajar al banco del LMS")
    else:
        print("\n  Todas las opciones llevan su explicación.")


def tabla_corte_ii(filas: list[dict], mods: dict) -> dict:
    print("\n2 · CORTE II POR MÓDULO · lo que decide la rama\n")
    print("  «con cifra» = el ítem cita el precálculo (D4.mN / D5.mN) y por")
    print("  tanto la máquina de variantes del Taller 1 lo individualiza sin")
    print("  escribir una pregunta nueva. «prosa» = no cita ninguna.\n")
    resumen = {}
    for doc in CORTE_II:
        if not any(f["conteo"] for f in filas if f["doc"] == doc):
            _para(f"{doc} no indexa sus referencias por módulo ({RAICES[doc]}"
                  ".<tema>): esta tabla no se puede construir para él, y "
                  "rellenarla con ceros diría que no tiene preguntas")
        sub = [f for f in filas if f["doc"] == doc]
        por_mod = defaultdict(list)
        for f in sub:
            m = primario(f)
            por_mod[m[1] if m else None].append(f)
        con_cifra = sum(1 for f in sub if f["conteo"])
        multi = sum(1 for f in sub if len(f["conteo"]) > 1)
        resumen[doc] = {"items": len(sub), "con_cifra": con_cifra,
                        "prosa": len(sub) - con_cifra, "multimodulo": multi,
                        "modulos": len(mods[doc])}
        print(f"  {doc} · {DOCS[doc]} · {len(mods[doc])} módulos, "
              f"{len(sub)} ítems")
        tocados = Counter()
        for f in sub:
            for (d, m) in f["conteo"]:
                if d == doc:
                    tocados[m] += 1
        print(f"    {'m':>3}  {'suyos':>5} {'toca':>4} {'cifra':>5}  título")
        for m in mods[doc]:
            aqui = por_mod.get(m["id"], [])
            cif = sum(1 for f in aqui if f["conteo"])
            t = tocados.get(m["id"], 0)
            marca = " ·" if not t else "  "
            print(f"   {marca}{m['id']:>2}  {len(aqui):>5} {t:>4} {cif:>5}  "
                  f"{m['titulo'][:50]}")
        sin = [m["id"] for m in mods[doc] if not tocados.get(m["id"])]
        print(f"    módulos que NINGUNA pregunta toca: {len(sin)} de "
              f"{len(mods[doc])}" + (f" → {sin}" if sin else ""))
        print(f"    ítems que tocan más de un módulo: {multi}")
        sueltas = [f for f in sub if not f["conteo"]]
        print(f"    prosa pura (sin cifra del precálculo): {len(sueltas)}"
              + "".join(f"\n      · {f['bloque']} #{f['indice']} ({f['tipo']})"
                        for f in sueltas))
        print()
    return resumen


def tabla_aritmetica(resumen: dict, examen: int, alumnos: int) -> None:
    P = sum(r["items"] for r in resumen.values())
    cifra = sum(r["con_cifra"] for r in resumen.values())
    prosa = sum(r["prosa"] for r in resumen.values())
    k = examen
    print("3 · LA ARITMÉTICA DE LAS DOS RAMAS")
    print(f"    examen de {k} ítems · {alumnos} estudiantes · "
          f"piscina actual de Corte II = {P} ítems\n")

    print("  RAMA «SELECCIÓN» — a cada quien un subconjunto distinto")
    if k > P:
        print(f"    IMPOSIBLE HOY: el examen pide {k} ítems y la piscina "
              f"tiene {P}.")
    solap = k * k / P if P else float("inf")
    print(f"    solapamiento esperado entre dos estudiantes: "
          f"{solap:.1f} de {k} ítems ({100 * solap / k:.0f} %)")
    for objetivo, nombre in ((k / 2, "la mitad"), (k / 3, "un tercio")):
        need = int(-(-k * k // objetivo)) if objetivo else 0
        print(f"    para bajarlo a {nombre} ({objetivo:.0f} ítems) haría "
              f"falta una piscina de {need} → escribir {max(0, need - P)} "
              "preguntas nuevas")
    print(f"    y las {P} existentes están PUBLICADAS con su clave: una "
          "piscina que")
    print("    saca de ahí baraja, no individualiza.\n")

    print("  RAMA «DATOS» — a cada quien sus cifras")
    print(f"    ítems que ya citan el precálculo: {cifra} de {P} "
          f"({100 * cifra / P:.0f} %) → variante gratis")
    print(f"    ítems de prosa pura:              {prosa} de {P} "
          f"({100 * prosa / P:.0f} %) → solo selección o reescritura")
    if cifra >= k:
        print(f"    un examen de {k} ítems cabe entero en los {cifra} "
              "individualizables por dato.")
    else:
        print(f"    un examen de {k} ítems NO cabe en los {cifra} "
              f"individualizables: faltan {k - cifra}.")
    print(f"    preguntas nuevas necesarias: 0 para tener {alumnos} exámenes "
          "distintos.")
    print("\n    (el coste que esta rama NO evita: el precálculo tiene que")
    print("     saber generar cada módulo por variante, y los distractores")
    print("     numéricos hay que recalcularlos y volver a comprobar que")
    print("     ninguno cae dentro de la tolerancia de su correcta.)")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--examen", type=int, default=20,
                    help="ítems del parcial (default 20)")
    ap.add_argument("--alumnos", type=int, default=12,
                    help="estudiantes matriculados (default 12)")
    ap.add_argument("--json", action="store_true",
                    help="vuelca el censo crudo en vez de las tablas")
    a = ap.parse_args()

    c = censo()
    if a.json:
        json.dump({"filas": [{k: v for k, v in f.items() if k != "conteo"}
                             | {"conteo": {f"{d}.m{m}": n
                                           for (d, m), n in f["conteo"].items()}}
                             for f in c["filas"]],
                   "modulos": c["modulos"]},
                  sys.stdout, ensure_ascii=False, indent=2)
        print()
        return

    print("=" * 76)
    print("CENSO DEL BANCO · Estadística Espacial 2026-II (20929)")
    print("leído del HTML publicado, que es lo que el estudiante vio")
    print("=" * 76)
    tabla_inventario(c["filas"])
    resumen = tabla_corte_ii(c["filas"], c["modulos"])
    tabla_aritmetica(resumen, a.examen, a.alumnos)
    print("\nNOTA · la columna «con cifra» NO es medible en el preparcial: sus")
    print("cifras las hornea `ensambla_preparcial1.py` y la ruta no sobrevive")
    print("a la publicación. Por eso el censo del Corte II se hace sobre los")
    print("capítulos 4 y 5, donde la referencia sí está en la página.")


if __name__ == "__main__":
    main()
