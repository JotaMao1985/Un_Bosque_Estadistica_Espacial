#!/usr/bin/env python3
"""
verifica_cifras_cap5.py — cotejo de TODAS las cifras de las presentaciones del capítulo 5.

Material de Estadística Espacial 2026-II (20929). Presentaciones: `capitulo_5_sesion_1.md`
y `capitulo_5_sesion_2.md`. Es el hermano de `verifica_cifras.py` (capítulo 4): misma idea y
mismo formato de registro, con una diferencia que aquí sí se puede aprovechar: R y spatstat
están, así que casi cada cifra tiene una segunda fuente que se vuelve a CALCULAR.

QUÉ HACE
  1. Lee cada fuente (diapositivas y notas) y extrae cada número que aparece.
  2. Exige que cada número esté en el REGISTRO (más abajo): cifra → de dónde sale y cómo se
     comprobó. Un número sin registrar es un ERROR.
  3. Cotejo, según el tipo de entrada:
       rj      la cifra coincide con `cap5_datos.json` (lo que publica el capítulo) Y con
               `recomputo_cap5.json` (lo que `recomputa_cap5.R` volvió a calcular en R).
       r       solo en el recómputo en R (el JSON del capítulo no la trae).
       json    solo en el JSON del capítulo.
       aritm   se recompone con una cuenta a partir de otras cifras ya verificadas.
       texto   solo figura en la prosa del capítulo (o en `FUENTES.md`): la frase existe.
       ext     dato de un conjunto o de una referencia, cotejado con la ficha de ayuda del
               paquete (que `recomputa_cap5.R` guarda en el recómputo).
       medida  medición de tiempo: depende de la máquina; se acepta con tolerancia.
       param   parámetro de diseño del capítulo (rejilla, semilla, σ elegido…).
       sinver  NO se pudo comprobar: se marca [SIN VERIFICAR] en la diapositiva.
  4. Escribe `registro_cifras_cap5_s1.md` (y `_s2`): cada cifra con su diapositiva, su
     contexto, su fuente y su estado.

Ejecutar (desde cualquier carpeta; solo necesita Python 3, sin R):
    python3 Htmls_Espacial/diapositivas/fuentes/verifica_cifras_cap5.py            # las dos sesiones
    python3 …/verifica_cifras_cap5.py --sesion 1                                    # una
    python3 …/verifica_cifras_cap5.py --tokens --sesion 1                           # lista los números
    python3 …/verifica_cifras_cap5.py --fuente OTRO.md --sin-escribir               # pruebas de defectos
Sale con código 1 si algo no coincide o no está registrado. Para refrescar el recómputo:
    precalculo/rscript.sh Htmls_Espacial/diapositivas/fuentes/recomputa_cap5.R todo
"""
from __future__ import annotations

import json
import math
import re
import sys
import unicodedata
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[2]
SALIDAS = RAIZ / "precalculo" / "salidas"
CAPITULO_HTML = RAIZ / "Htmls_Espacial" / "capitulo-5-intensidad-nucleos.html"
FUENTES_MD = {1: AQUI / "capitulo_5_sesion_1.md", 2: AQUI / "capitulo_5_sesion_2.md"}
REGISTROS_MD = {1: AQUI / "registro_cifras_cap5_s1.md", 2: AQUI / "registro_cifras_cap5_s2.md"}


# ----------------------------------------------------------------------------------------
# 1 · La fuente: secciones, diapositivas, notas (misma numeración que la presentación construida)
# ----------------------------------------------------------------------------------------
def leer_fuente(ruta: Path) -> list[dict]:
    lineas = ruta.read_text(encoding="utf-8").splitlines()
    encabezado = ""
    if lineas and lineas[0].strip() == "---":
        fin = next(k for k in range(1, len(lineas)) if lineas[k].strip() == "---")
        encabezado = "\n".join(l for l in lineas[1:fin] if l.split(":")[0] in ("etiqueta", "objetivo", "temas", "subtitulo"))
        lineas = lineas[fin + 1:]
    piezas = [{"n": 1, "tipo": "portada", "titulo": "Portada", "cuerpo": encabezado, "notas": ""},
              {"n": 2, "tipo": "hoja", "titulo": "Hoja de ruta", "cuerpo": "", "notas": ""}]
    actual, en_codigo, en_comentario = None, False, False
    for l in lineas:
        s = l.strip()
        if en_comentario:
            if "-->" in s:
                en_comentario = False
            continue
        if s.startswith("<!--") and not en_codigo:
            if "-->" not in s:
                en_comentario = True
            continue
        if s.startswith("```"):
            en_codigo = not en_codigo
        m = None if en_codigo else re.match(r"^(#{1,2})\s+(.*)$", l)
        if m:
            nivel = len(m.group(1))
            titulo = re.sub(r"\s*\{[^{}]*\}\s*$", "", m.group(2)).strip()
            actual = {"n": len(piezas) + 1, "tipo": "divisor" if nivel == 1 else "diapo", "titulo": titulo, "lineas": []}
            piezas.append(actual)
            continue
        if actual is not None:
            actual["lineas"].append(l)
    for p in piezas:
        if "lineas" in p:
            cuerpo, notas, en_notas = [], [], False
            for l in p.pop("lineas"):
                if l.strip() == "???":
                    en_notas = True
                    continue
                (notas if en_notas else cuerpo).append(l)
            p["cuerpo"], p["notas"] = "\n".join(cuerpo), "\n".join(notas)
    return piezas


# ----------------------------------------------------------------------------------------
# 2 · Extraer números
# ----------------------------------------------------------------------------------------
NBSP = "\u00a0\u202f"                          # espacio duro y espacio duro fino
MILES = rf"\d{{1,3}}(?:[ {NBSP}]\d{{3}})+"      # 2 107 · 145 362
NUM = rf"(?:{MILES}|\d+)(?:[.,]\d+)?"
RE_TOKEN = re.compile(rf"(?<![\w.,])([−+\-]?)({NUM})(?![\w])")
RE_SCI = re.compile(r"(?<![\w.,])([−+\-]?)(\d+(?:\.\d+)?[eE][−+\-]?\d+)(?![\w])")      # 1.794e-10 · 6.567e+08

QUITAR = [
    (re.compile(r"```.*?```", re.S), " "),                                 # bloques de código (se verifican aparte)
    (re.compile(r"<sup>[^<]*</sup>"), " "),                                 # exponentes: n<sup>−1/6</sup>
    (re.compile(r"(?i)\b\d{1,2}\s+(?:ene|feb|mar|abr|may|jun|jul|ago|sep|oct|nov|dic)\w*\s+\d{4}\b"), " "),   # fechas «29 sep 2026»
    (re.compile(r"`[^`]*`"), " "),                                          # código en línea
    (re.compile(r"!\[([^\]]*)\]\([^)]*\)(\{[^}]*\})?"), r"\1"),            # figuras: solo el pie
    (re.compile(r"<[^>]+>"), " "),                                          # etiquetas html
    (re.compile(r"\]\([^)]*\)"), "]"),                                      # destinos de enlaces
    (re.compile(r"\{[.#]?[\w:=. \"-]+\}"), " "),                           # atributos {columnas=3}
    (re.compile(r"(?i)\b(módulos?|mód\.|capítulos?|cap\.|ejercicios?|diapositivas?|fuentes?|semanas?|sesión|sesiones)\s+\d+(?!\d|\.\d)"
                r"(?:\s*(?:a|y|,|–)\s*\d+(?!\d|\.\d))*"), " "),             # «módulos 3 a 9»
    (re.compile(r"(?i)\b(la|las|opción|opciones)\s+[1-4](?![\d.,\u00a0\u202f])"), " "),   # «La 4», «opción 3» (no «las 2 107»)
    (re.compile(r"(?m)^\s*\d+[.)]\s+"), ""),                                # numeración de listas
    (re.compile(r"\b1/2\b"), " "),
]
RE_GRILLA = re.compile(r"(?<![\d.])(\d+)\s*[×x]\s*(\d+)(?![\d.])")
RE_DECIMALES_X = re.compile(r"(\d+\.\d+)\s*×\s*(\d+\.\d+)")
RE_VERSION = re.compile(r"\b\d+\.\d+\.\d+\b")
RE_FORMULA = re.compile(r"\$\$(.+?)\$\$|\\\((.+?)\\\)", re.S)
TRIVIALES = {"0", "1", "2"}


def norm_num(txt: str) -> str:
    return re.sub(rf"[ {NBSP}]", "", txt).replace(",", ".")


def numeros_de(texto: str) -> list[tuple[str, str]]:
    out = []

    def anota(tok, ini, fin, base):
        ctx = re.sub(r"\s+", " ", base[max(0, ini - 38):fin + 30].replace("\n", " ")).strip()
        out.append((tok, ctx))

    base = texto
    formulas = []
    for m in RE_FORMULA.finditer(base):
        formulas.append(m.group(1) or m.group(2))
    base = RE_FORMULA.sub(" ", base)
    for rx, rep in QUITAR:
        base = rx.sub(rep, base)
    base = RE_DECIMALES_X.sub(r"\1 \2", base)                      # «7.5 × 7.7» son dos números, no una rejilla
    for m in RE_GRILLA.finditer(base):
        anota(f"{m.group(1)}x{m.group(2)}", m.start(), m.end(), base)
    base = RE_GRILLA.sub(" ", base)
    for m in RE_VERSION.finditer(base):
        anota(m.group(0), m.start(), m.end(), base)
    base = RE_VERSION.sub(" ", base)
    for m in RE_SCI.finditer(base):
        signo = "-" if m.group(1) in ("−", "-") else ""
        anota(signo + m.group(2).replace("−", "-").lower(), m.start(), m.end(), base)
    base = RE_SCI.sub(" ", base)
    for m in RE_TOKEN.finditer(base):
        signo = "-" if m.group(1) in ("−", "-") else ""
        tok = norm_num(m.group(2))
        if tok in TRIVIALES:
            continue
        anota(signo + tok, m.start(), m.end(), base)
    for f in formulas:
        f2 = re.sub(r"\\[a-zA-Z]+", " ", f).replace("\\,", "")
        f2 = re.sub(r"\^\{?\d+\}?|_\{?\d+\}?|\{[^{}]*\}", " ", f2) if False else re.sub(r"\^\{?\d+\}?|_\{?\d+\}?", " ", f2)
        for m in RE_TOKEN.finditer(f2):
            tok = norm_num(m.group(2))
            if tok in TRIVIALES:
                continue
            out.append((tok, "fórmula: " + re.sub(r"\s+", " ", f)[:70]))
    return out


def extrae_todo(piezas: list[dict]) -> list[dict]:
    occ = []
    for p in piezas:
        for donde, txt in (("titulo", p["titulo"]), ("cuerpo", p["cuerpo"]), ("notas", p["notas"])):
            if p["tipo"] == "portada" and donde != "cuerpo":
                continue
            for tok, ctx in numeros_de(txt):
                occ.append({"n": p["n"], "titulo": p["titulo"], "donde": donde, "token": tok, "ctx": ctx})
    return occ


# ----------------------------------------------------------------------------------------
# 3 · Datos de partida
# ----------------------------------------------------------------------------------------
def _cargar(ruta: Path):
    return json.loads(ruta.read_text(encoding="utf-8")) if ruta.exists() else {}


D = _cargar(SALIDAS / "cap5_datos.json")               # lo que publica el capítulo 5
D4 = _cargar(SALIDAS / "cap4_datos.json")              # el capítulo 4 (coste de la corrección de K)
def _cargar_recomputos():
    """`recomputo_cap5.json` (sesión 1) y `recomputo_cap5_<módulo>.json` (sesión 2), en un solo diccionario.
    El `meta` de cada archivo de la sesión 2 queda en `meta_s2[<módulo>]`."""
    rc = _cargar(AQUI / "recomputo_cap5.json")
    metas = {}
    for f in sorted(AQUI.glob("recomputo_cap5_*.json")):
        for k, val in _cargar(f).items():
            if k == "meta":
                metas[f.stem.replace("recomputo_cap5_", "")] = val
            else:
                rc[k] = val
    if metas:
        rc["meta_s2"] = metas
    return rc


RC = _cargar_recomputos()                              # lo que se volvió a calcular en R
PROC = _cargar(RAIZ / "datos" / "procesado" / "procedencia.json")


def _plano(html: str) -> str:
    import html as _h
    t = re.sub(r"<style.*?</style>", " ", html, flags=re.S)
    t = re.sub(r"<[^>]+>", " ", t)
    t = _h.unescape(t)
    t = unicodedata.normalize("NFKC", t).lower()
    return re.sub(r"\s+", " ", t)


TEXTO_CAP = _plano(CAPITULO_HTML.read_text(encoding="utf-8")) if CAPITULO_HTML.exists() else ""
_f = RAIZ / "precalculo" / "FUENTES.md"
TEXTO_FUENTES = _plano(_f.read_text(encoding="utf-8")) if _f.exists() else ""


def get(obj, ruta: str):
    """`m6.chorley.casos` → obj['m6']['chorley']['casos'];  `maximos[3]` indexa listas."""
    for parte in ruta.split("."):
        m = re.match(r"^([\w-]+)(?:\[(\d+)\])?$", parte)
        obj = obj[m.group(1)]
        if m.group(2) is not None:
            obj = obj[int(m.group(2))]
    return obj


def redondea(v, dec: int) -> Decimal:
    return Decimal(repr(float(v))).quantize(Decimal(1).scaleb(-dec), rounding=ROUND_HALF_UP)


def decimales(tok: str) -> int:
    return len(tok.split(".")[1]) if "." in tok else 0


def igual(token: str, v) -> bool:
    """¿La cifra `token` es `v` redondeado a los decimales con que se muestra?"""
    if isinstance(v, str):
        return token in v
    if isinstance(v, (list, tuple)) and not re.fullmatch(r"\d+x\d+", token):
        return any(igual(token, x) for x in v)
    if re.fullmatch(r"\d+x\d+", token):
        a, b = token.split("x")
        permitidos = {int(k) for k in (v if isinstance(v, (list, tuple)) else [v])}
        return a == b and int(a) in permitidos
    try:
        t = Decimal(token)
    except InvalidOperation:
        return False
    if re.search(r"[eE]", token):                        # notación científica: se compara la mantisa con sus decimales
        dec = decimales(token.lower().split("e")[0].lstrip("-"))
        return Decimal(format(float(v), f".{dec}e")) == t
    return redondea(v, decimales(token)) == t


def d(ruta):            # un valor del JSON del capítulo
    return get(D, ruta)


def r(ruta):            # un valor del recómputo en R
    return get(RC, ruta)


# ----------------------------------------------------------------------------------------
# 4 · El registro: cada cifra → de dónde sale y cómo se comprobó
# ----------------------------------------------------------------------------------------
class Spec:
    def __init__(self, tipo, desc, vals=(), frase=None, corpus=None, tol=None):
        self.tipo, self.desc, self.vals = tipo, desc, list(vals)
        self.frase, self.corpus, self.tol = frase, corpus, tol


def RJ(ruta_json, ruta_rec, desc=""):
    """JSON del capítulo Y recómputo en R: los dos tienen que dar la cifra."""
    return Spec("rj", desc, [("datos › " + ruta_json, lambda: d(ruta_json)), ("recomputo › " + ruta_rec, lambda: r(ruta_rec))])


def J4(ruta, desc=""):
    return Spec("json", desc, [("cap4_datos.json › " + ruta, lambda: get(D4, ruta))])


def Rr(ruta_rec, desc=""):
    return Spec("r", desc, [("recomputo › " + ruta_rec, lambda: r(ruta_rec))])


def J(ruta_json, desc=""):
    return Spec("json", desc, [("datos › " + ruta_json, lambda: d(ruta_json))])


def A(fn, desc):
    return Spec("aritm", desc, [(desc, fn)])


def T(frase, corpus="cap", desc=""):
    return Spec("texto", desc or f"texto del capítulo: «{frase}»", frase=frase, corpus=corpus)


def E(ruta_rec, frase, desc=""):
    """Dato de la ficha de ayuda de un conjunto (guardada en el recómputo): `frase` debe figurar en ella."""
    return Spec("ext", desc or f"ayuda de spatstat.data (recomputo › {ruta_rec}): «{frase}»", frase=frase, corpus=("ayuda", ruta_rec))


def M(ruta_rec, tol, desc=""):
    return Spec("medida", desc or f"recomputo › {ruta_rec} (±{tol:g}, depende de la máquina)", [("recomputo › " + ruta_rec, lambda: r(ruta_rec))], tol=tol)


def P(desc, ruta=None):
    if ruta:
        return Spec("param", desc, [("datos › " + ruta, lambda: d(ruta))])
    return Spec("param", desc)


def X(desc):
    return Spec("sinver", desc)


REG_ENTRADAS = []


def REG(tokens, spec, en=None, cx=None):
    """`en`: prefijos de título de las diapositivas donde vale; `cx`: expresión regular que debe
    aparecer en el contexto inmediato de la cifra (para números con varios significados)."""
    tokens = [tokens] if isinstance(tokens, str) else tokens
    specs = spec if isinstance(spec, list) else [spec]
    REG_ENTRADAS.append({"tokens": tokens, "specs": specs, "en": en, "cx": cx})


HALLAZGOS: list[tuple] = []                           # (título, texto) de la sesión 1, o (sesión, título, texto)
AFIRMACIONES: list[tuple[int, str, object]] = []      # (sesión, afirmación no numérica, función → bool)


def AF(sesion, texto, fn):
    AFIRMACIONES.append((sesion, texto, fn))


TABLAS: list[tuple[int, str, object]] = []            # (sesión, prefijo del título de la diapositiva, filas esperadas)


def TAB(sesion, titulo, filas):
    """`filas`: lista de filas; cada fila, lista de celdas; cada celda, None (no se comprueba) o la
    lista de valores que deben igualar, en orden, a los números de la celda."""
    TABLAS.append((sesion, titulo, filas))

# (el REGISTRO propiamente dicho vive en `registro_cifras_cap5_entradas.py`, que se importa abajo)
try:
    from registro_cifras_cap5_entradas import cargar_entradas      # noqa: E402
except ModuleNotFoundError:                                          # pragma: no cover
    sys.path.insert(0, str(AQUI))
    from registro_cifras_cap5_entradas import cargar_entradas        # noqa: E402

ETIQUETA = {"rj": "VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo",
            "r": "VERIFICADA · re-ejecutada en R",
            "aritm": "VERIFICADA · aritmética sobre cifras verificadas",
            "json": "CONTRASTADA · salida de R (JSON del capítulo)",
            "texto": "CONTRASTADA · texto del capítulo",
            "ext": "REFERENCIA · ficha de ayuda del paquete",
            "medida": "MEDIDA · depende de la máquina (con tolerancia)",
            "param": "PARÁMETRO de diseño",
            "sinver": "[SIN VERIFICAR]"}
PRIORIDAD = ["rj", "r", "aritm", "json", "medida", "texto", "ext", "param", "sinver"]


def evalua(spec: Spec, token: str):
    if spec.tipo == "texto":
        corpus = TEXTO_CAP if spec.corpus == "cap" else TEXTO_FUENTES
        f = unicodedata.normalize("NFKC", spec.frase).lower()
        return (f in corpus), spec.desc + ("" if f in corpus else " · NO ENCONTRADA")
    if spec.tipo == "ext":
        try:
            txt = get(RC, spec.corpus[1])
        except Exception as ex:
            return False, f"{spec.desc}: ERROR {ex!r}"
        txt = re.sub(r"\s+", " ", unicodedata.normalize("NFKC", txt if isinstance(txt, str) else json.dumps(txt, ensure_ascii=False)).lower())
        f = re.sub(r"\s+", " ", unicodedata.normalize("NFKC", spec.frase).lower())
        return (f in txt), spec.desc + ("" if f in txt else " · NO ENCONTRADA")
    if spec.tipo == "param" and not spec.vals:
        return True, spec.desc
    if spec.tipo == "sinver" and not spec.vals:
        return True, spec.desc
    partes, ok = [], True
    for etq, fn in spec.vals:
        try:
            v = fn()
        except Exception as ex:
            return False, f"{etq}: ERROR {ex!r}"
        if spec.tipo == "medida":
            good = abs(float(token) - float(v)) <= spec.tol
            partes.append(f"{etq} = {float(v):.5g} (tolerancia ±{spec.tol:g})")
        elif spec.tipo == "aritm":
            good = igual(token, v)
            partes.append(f"{spec.desc} = {float(v):.10g}")
        else:
            good = igual(token, v)
            vs = v if isinstance(v, (str, int)) else (f"{float(v):.10g}" if not isinstance(v, (list, tuple)) else v)
            partes.append(f"{etq} = {vs}")
        ok = ok and good
    return ok, "; ".join(partes) + ("" if ok else "  ← NO COINCIDE")


def busca(entradas, token, titulo, ctx=""):
    out = []
    for e in entradas:
        en_tabla = "|" in ctx                           # las celdas de tabla las clava `comprueba_tablas` en su casilla
        if (token in e["tokens"] and (e["en"] is None or any(titulo.replace("\u00a0", " ").startswith(p.replace("\u00a0", " ")) for p in e["en"]))
                and (e.get("cx") is None or en_tabla or re.search(e["cx"], ctx))):
            out.append(e)
    return out


def verifica(occ):
    filas, errores, cache = [], [], {}
    for o in occ:
        cands = busca(REG_ENTRADAS, o["token"], o["titulo"], o["ctx"])
        if not cands:
            errores.append(f"SIN REGISTRAR · diapositiva {o['n']} «{o['titulo'][:40]}» ({o['donde']}): {o['token']}  ← …{o['ctx']}…")
            filas.append({**o, "estado": "SIN REGISTRAR", "detalle": "", "tipo": None})
            continue
        mejor = None
        for e in cands:
            clave = (id(e), o["token"])
            if clave not in cache:
                res = [evalua(s, o["token"]) for s in e["specs"]]
                cache[clave] = (all(x[0] for x in res), " | ".join(x[1] for x in res))
            ok, det = cache[clave]
            tipo = min((s.tipo for s in e["specs"]), key=PRIORIDAD.index)
            if ok:
                mejor = (tipo, det)
                break
            mejor = mejor or ("error", det)
        if mejor[0] == "error":
            errores.append(f"NO COINCIDE · diapositiva {o['n']} «{o['titulo'][:40]}»: {o['token']} → {mejor[1]}")
            filas.append({**o, "estado": "ERROR", "detalle": mejor[1], "tipo": None})
        else:
            filas.append({**o, "estado": ETIQUETA[mejor[0]], "detalle": mejor[1], "tipo": mejor[0]})
    return filas, errores


# ----------------------------------------------------------------------------------------
# 5 · Comprobaciones estructurales (las reglas de la presentación)
# ----------------------------------------------------------------------------------------
def estructura(piezas, filas):
    errs = []
    con_cifras = {}
    for f in filas:
        if f["donde"] in ("cuerpo", "titulo"):
            con_cifras.setdefault(f["n"], []).append(f)
    for p in piezas:
        if p["tipo"] != "diapo" or p["n"] not in con_cifras:
            continue
        if not re.search(r"Fuentes?\s*:", p["cuerpo"]):
            errs.append(f"SIN LÍNEA DE FUENTE · diapositiva {p['n']} «{p['titulo'][:50]}» tiene cifras y no cita su fuente")
        # toda afirmación va como Dato, Interpretación o Criterio (las preguntas, ideas y el cierre se excusan)
        es_especial = bool(re.search(r"\{[^}]*\.(pregunta|idea|cierre)", p.get("crudo", ""))) or p["titulo"].startswith(("Cada cifra", "Lo que se llevan", "Práctica"))
        if not es_especial and not re.search(r":::\s*(info|tip|warn|definicion)\b", p["cuerpo"]):
            errs.append(f"SIN ETIQUETA · diapositiva {p['n']} «{p['titulo'][:50]}» no trae ninguna caja Dato/Interpretación/Criterio")
    for f in filas:
        if f["tipo"] == "sinver":
            p = next(q for q in piezas if q["n"] == f["n"])
            if f["donde"] == "cuerpo" and "SIN VERIFICAR" not in p["cuerpo"]:
                errs.append(f"SIN MARCA VISIBLE · diapositiva {p['n']}: {f['token']} está en la lámina sin la marca [SIN VERIFICAR]")
    return errs


# ----------------------------------------------------------------------------------------
# 6 · El registro en Markdown
# ----------------------------------------------------------------------------------------
def comprueba_afirmaciones(sesion):
    res = []
    for s_, texto, fn in AFIRMACIONES:
        if s_ != sesion:
            continue
        try:
            ok = bool(fn())
        except Exception as ex:                                   # noqa: BLE001
            ok = False
            texto += f" · ERROR {ex!r}"
        res.append((texto, ok))
    return res


def _celdas(linea):
    return [c.strip() for c in linea.strip().strip("|").split("|")]


def tablas_de(texto):
    """Primera tabla de Markdown de un texto: [filas de celdas] sin la cabecera ni la raya."""
    filas, dentro = [], False
    for l in texto.splitlines():
        if l.strip() == "|||":                      # separador de columnas, no una fila
            if dentro:
                break
            continue
        if l.strip().startswith("|"):
            dentro = True
            cel = _celdas(l)
            if all(re.fullmatch(r":?-{3,}:?", c) for c in cel):
                continue
            filas.append(cel)
        elif dentro:
            break
    return filas[1:] if filas else []


def comprueba_tablas(sesion, piezas):
    errs, hechas = [], 0
    for s_, titulo, esperadas in TABLAS:
        if s_ != sesion:
            continue
        p = next((q for q in piezas if q["tipo"] == "diapo" and q["titulo"].replace("\u00a0", " ").startswith(titulo.replace("\u00a0", " "))), None)
        if p is None:
            errs.append(f"TABLA · no encuentro la diapositiva «{titulo}»")
            continue
        real = tablas_de(p["cuerpo"])
        if len(real) != len(esperadas):
            errs.append(f"TABLA · diapositiva {p['n']} «{titulo[:40]}»: tiene {len(real)} filas y se esperaban {len(esperadas)}")
            continue
        for i, (fila, esp) in enumerate(zip(real, esperadas), 1):
            for j, (celda, val) in enumerate(zip(fila, esp), 1):
                if val is None:
                    continue
                valores = [f() if callable(f) else f for f in val]
                toks = [tok for tok, _ in numeros_de(celda)]
                if len(toks) != len(valores):
                    errs.append(f"TABLA · diapositiva {p['n']} fila {i} columna {j}: «{celda}» trae {len(toks)} números y se esperaban {len(valores)}")
                    continue
                for tok, vv in zip(toks, valores):
                    hechas += 1
                    if not igual(tok, vv):
                        errs.append(f"TABLA · diapositiva {p['n']} fila {i} columna {j}: «{tok}» no es {float(vv):.6g} (celda «{celda}»)")
    return errs, hechas


def comprueba_rutas(piezas):
    """Cada «datos › ruta» o «recomputo › ruta» citado entre comillas invertidas tiene que existir."""
    errs = []
    for p in piezas:
        for fuente, ruta in re.findall(r"`(datos|recomputo) › ([^`]+)`", p["cuerpo"] + "\n" + p["notas"]):
            for una in re.split(r"\s*,\s*", ruta):
                una = una.strip()
                if not una or " " in una:
                    continue
                if una.endswith("_*"):
                    pref = una[:-1]
                    clave = una.split(".")[0] if "." in una else None
                    base = D if fuente == "datos" else RC
                    nivel = base
                    partes = una.split(".")
                    try:
                        for q in partes[:-1]:
                            nivel = nivel[q]
                    except Exception:                                    # noqa: BLE001
                        errs.append(f"RUTA INEXISTENTE · diapositiva {p['n']}: {fuente} › {una}")
                        continue
                    if not any(k.startswith(pref) for k in nivel):
                        errs.append(f"RUTA INEXISTENTE · diapositiva {p['n']}: {fuente} › {una}")
                    continue
                try:
                    get(D if fuente == "datos" else RC, una if fuente == "datos" else una)
                except Exception:                                        # noqa: BLE001
                    errs.append(f"RUTA INEXISTENTE · diapositiva {p['n']}: {fuente} › {una}")
    return errs


def escribe_registro(sesion, piezas, filas):
    cuenta = {}
    for f in filas:
        cuenta[f["estado"]] = cuenta.get(f["estado"], 0) + 1
    unicas = {}
    for f in filas:
        unicas.setdefault(f["token"], f["estado"])
    if sesion == 1:
        meta = RC.get("meta", {})
        fecha, paq, guion = meta.get("fecha", "?"), meta.get("paquetes", {}), "recomputa_cap5.R"
        rver = meta.get("R", "")
    else:
        m2 = next(iter(RC.get("meta_s2", {}).values()), {})
        fecha, rver, guion = m2.get("fecha", "?"), m2.get("R", ""), "recomputa_cap5_s2.R"
        paq = {"spatstat": m2.get("spatstat", "?"), "spatstat.explore": m2.get("spatstat.explore", "?"), "spatstat.model": m2.get("spatstat.model", "?")}
    L = [f"# Registro de cifras · Capítulo 5 · Sesión {sesion}", "",
         f"Generado por `verifica_cifras_cap5.py` a partir de `capitulo_5_sesion_{sesion}.md`. **No se edita a mano**: se regenera.", "",
         f"Recómputo en R del {fecha} ({rver}; spatstat {paq.get('spatstat', '?')}, "
         f"spatstat.explore {paq.get('spatstat.explore', '?')}, spatstat.model {paq.get('spatstat.model', '?')}), "
         f"con `{guion}`.", "",
         "## Cómo se comprobó cada cifra", "",
         "| Estado | Qué significa |", "|---|---|",
         "| VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo | Se volvió a calcular en R con el mismo código del capítulo y coincide con `cap5_datos.json`, redondeada a los decimales que se muestran. |",
         "| VERIFICADA · re-ejecutada en R | Se calculó en R (`recomputa_cap5.R`); el JSON del capítulo no la trae. |",
         "| VERIFICADA · aritmética sobre cifras verificadas | Se recompone con una cuenta a partir de otras cifras ya verificadas. |",
         "| CONTRASTADA · salida de R (JSON del capítulo) | Coincide con `cap5_datos.json`; no se volvió a calcular aquí. |",
         "| CONTRASTADA · texto del capítulo | Solo figura en la prosa del capítulo publicado o en `FUENTES.md`: la frase existe. |",
         "| REFERENCIA · ficha de ayuda del paquete | Dato de un conjunto o de una referencia (año, n, tamaño de la parcela), cotejado con la ayuda de `spatstat.data`. |",
         "| MEDIDA · depende de la máquina | Un tiempo: se vuelve a medir y se acepta con tolerancia. |",
         "| PARÁMETRO de diseño | Rejillas, semillas, σ elegido, duración: decisiones del capítulo o del docente. |",
         "| **[SIN VERIFICAR]** | No se pudo comprobar. Lleva la marca en la diapositiva y no se presenta como dato confirmado. |",
         "", "Los enteros 0, 1 y 2 usados como constantes de definición no se registran: no son mediciones.", "",
         "## Resumen", "",
         f"- {len(filas)} apariciones de cifras en {len({f['n'] for f in filas})} diapositivas; {len(unicas)} cifras distintas.",
         *[f"- {k}: {v}" for k, v in sorted(cuenta.items(), key=lambda kv: -kv[1])], "",
         "## Hallazgos en el material del capítulo", "",
         "Discrepancias que aparecieron al cotejar. No son errores de la presentación: se dicen aquí y en las notas, "
         "y no se corrigen en silencio.", ""]
    for h in HALLAZGOS:
        s_h, t, dsc = h if len(h) == 3 else (1, *h)
        if s_h == sesion:
            L += [f"- **{t}.** {dsc}"]
    af = comprueba_afirmaciones(sesion)
    if af:
        L += ["", "## Afirmaciones que no son una cifra, y cómo se comprobaron", "",
              "Cada una se vuelve a evaluar con el recómputo en R cada vez que se corre el verificador.", ""]
        for texto, ok in af:
            L.append(f"- {'✓' if ok else '✗ FALLA'} {texto}")
    L += ["", "## Cifra por cifra", ""]
    por = {}
    for f in filas:
        por.setdefault((f["n"], f["titulo"]), []).append(f)
    for (n, t), lst in por.items():
        L += [f"### Diapositiva {n} · {t}", "", "| Cifra | Dónde | Contexto | Comprobación | Estado |", "|---|---|---|---|---|"]
        vistos = set()
        for f in lst:
            clave = (f["token"], f["donde"], f["ctx"][:30])
            if clave in vistos:
                continue
            vistos.add(clave)
            ctx = f["ctx"].replace("|", "\\|")[:70]
            det = f["detalle"].replace("|", "\\|")[:230]
            L.append(f"| `{f['token']}` | {f['donde']} | …{ctx}… | {det} | {f['estado']} |")
        L.append("")
    REGISTROS_MD[sesion].write_text("\n".join(L), encoding="utf-8")


# ----------------------------------------------------------------------------------------
# 7 · Principal
# ----------------------------------------------------------------------------------------
def main() -> int:
    args = sys.argv[1:]
    sesiones = [1, 2]
    if "--sesion" in args:
        sesiones = [int(args[args.index("--sesion") + 1])]
    cargar_entradas(sys.modules[__name__], sesiones)
    rc = 0
    for s in sesiones:
        ruta = FUENTES_MD[s]
        if "--fuente" in args:
            ruta = Path(args[args.index("--fuente") + 1])
        if not ruta.exists():
            print(f"(sesión {s}: no hay fuente todavía)")
            continue
        piezas = leer_fuente(ruta)
        occ = extrae_todo(piezas)
        if "--tokens" in args:
            por = {}
            for o in occ:
                por.setdefault((o["n"], o["titulo"]), []).append(o)
            for (n, t), lst in por.items():
                print(f"\n[{n}] {t[:70]}")
                for o in lst:
                    print(f"   {o['donde'][:1]} {o['token']:<12} | {o['ctx'][:100]}")
            print(f"\n{len(occ)} ocurrencias · {len({o['token'] for o in occ})} números distintos · {len(piezas)} piezas")
            continue
        # el texto crudo de cada diapositiva (para reconocer preguntas, ideas y cierres)
        crudo = {}
        cur = None
        for l in ruta.read_text(encoding="utf-8").splitlines():
            m = re.match(r"^(#{1,2})\s+(.*)$", l)
            if m:
                cur = re.sub(r"\s*\{[^{}]*\}\s*$", "", m.group(2)).strip()
                crudo[cur] = l
        for p in piezas:
            p["crudo"] = crudo.get(p["titulo"], "")
        filas, errores = verifica(occ)
        errores += estructura(piezas, filas)
        errores += comprueba_rutas(piezas)
        e_tab, n_tab = comprueba_tablas(s, piezas)
        errores += e_tab
        for texto, ok in comprueba_afirmaciones(s):
            if not ok:
                errores.append(f"AFIRMACIÓN QUE FALLA · {texto}")
        if "--sin-escribir" not in args:
            escribe_registro(s, piezas, filas)
        cuenta = {}
        for f in filas:
            cuenta[f["estado"]] = cuenta.get(f["estado"], 0) + 1
        print(f"\n=== Sesión {s}: {len(filas)} apariciones · {len({f['token'] for f in filas})} cifras distintas · {len(piezas)} piezas · {n_tab} celdas de tabla comprobadas en su casilla")
        for k, v in sorted(cuenta.items(), key=lambda kv: -kv[1]):
            print(f"  {v:4d}  {k}")
        if "--sin-escribir" not in args:
            print(f"registro → {REGISTROS_MD[s].relative_to(RAIZ)}")
        if errores:
            print(f"\n{len(errores)} PROBLEMAS (sesión {s}):")
            for e in errores:
                print("  ✗", e)
            rc = 1
        else:
            print(f"\n✓ sesión {s}: todas las cifras están registradas y coinciden con su fuente")
    return rc


if __name__ == "__main__":
    sys.exit(main())
