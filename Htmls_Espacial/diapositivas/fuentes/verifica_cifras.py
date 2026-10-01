#!/usr/bin/env python3
"""
verifica_cifras.py — cotejo de TODAS las cifras de la presentación del capítulo 4.

Material de Estadística Espacial 2026-II (20929). Presentación: `capitulo_4.md`.

QUÉ HACE
  1. Lee `capitulo_4.md` (diapositivas y notas) y extrae cada número que aparece.
  2. Exige que cada número esté en el REGISTRO (`REGISTRO`, más abajo): cifra → de
     dónde sale y cómo se comprobó. Un número sin registrar es un ERROR.
  3. Cotejo, según el tipo de entrada:
       json      la cifra, redondeada a los decimales con que se muestra, coincide con
                 la salida de R del precálculo (`cap4_datos.json`, `cap4_soluciones.json`).
       indep     además se RECOMPUTA por un camino que no pasa por R ni por spatstat, con
                 los CSV de `precalculo/salidas/` (distancias con scipy, χ² a mano, etc.).
       aritm     se recompone con aritmética a partir de otras cifras del JSON.
       texto     solo figura en la prosa del capítulo publicado: se comprueba que la
                 frase existe en `capitulo-4-patrones-puntuales.html`.
       ext       referencia bibliográfica externa, cotejada con su ficha (URL en el registro).
       param     parámetro de diseño del capítulo (rejilla, semilla, nsim…), cotejado con el JSON.
       sinver    NO se pudo comprobar aquí: se marca [SIN VERIFICAR] en la diapositiva.
  4. Escribe `registro_cifras_cap4.md`: cada cifra con su diapositiva, su contexto, su fuente
     y su estado.

QUÉ NO HACE (y se dice)
  · No ejecuta R ni spatstat: en este entorno no están, y `datos/procesado/` (los .gpkg de
    la ventana urbana) no se versiona. Por eso las cifras que dependen de la geometría de la
    ventana (áreas, χ² de Bogotá, K de Bogotá) y las de estimadores internos de spatstat
    (Kaplan-Meier de G, pcf, envolventes) se cotejan contra el JSON, no se recomputan.
  · Los enteros 0, 1 y 2 usados como constantes de definición («R < 1», «1 − G», «Poisson de
    media λ|A|») no se registran: son definiciones, no mediciones.

Ejecutar:  python3 Htmls_Espacial/diapositivas/fuentes/verifica_cifras.py
           (numpy, scipy y pandas; sale con código 1 si algo no coincide o no está registrado)
           python3 …/verifica_cifras.py --tokens    lista los números por diapositiva
           python3 …/verifica_cifras.py --fuente OTRO.md --sin-escribir    (pruebas de defectos)
"""
from __future__ import annotations

import json
import math
import re
import sys
import unicodedata
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[2]
SALIDAS = RAIZ / "precalculo" / "salidas"
FUENTE = AQUI / "capitulo_4.md"
CAPITULO_HTML = RAIZ / "Htmls_Espacial" / "capitulo-4-patrones-puntuales.html"
REGISTRO_MD = AQUI / "registro_cifras_cap4.md"


# ----------------------------------------------------------------------------------------
# 1 · La fuente: secciones, diapositivas, notas
# ----------------------------------------------------------------------------------------
def leer_fuente(ruta: Path = FUENTE) -> list[dict]:
    """Devuelve una lista de 'piezas' en el orden de la presentación construida:
    portada (1), hoja de ruta (2), y luego, por sección, su divisor y sus diapositivas."""
    lineas = ruta.read_text(encoding="utf-8").splitlines()
    if lineas and lineas[0].strip() == "---":
        fin = next(k for k in range(1, len(lineas)) if lineas[k].strip() == "---")
        # de la portada solo se muestran estas claves; `modulo:` y `agenda:` son configuración
        encabezado = "\n".join(l for l in lineas[1:fin] if l.split(":")[0] in ("etiqueta", "objetivo", "temas"))
        lineas = lineas[fin + 1:]
    else:
        encabezado = ""
    piezas = [{"n": 1, "tipo": "portada", "titulo": "Portada", "cuerpo": encabezado, "notas": ""},
              {"n": 2, "tipo": "hoja", "titulo": "Hoja de ruta", "cuerpo": "", "notas": ""}]
    actual = None
    en_comentario = False
    for l in lineas:
        s = l.strip()
        if en_comentario:
            if "-->" in s:
                en_comentario = False
            continue
        if s.startswith("<!--"):
            if "-->" not in s:
                en_comentario = True
            continue
        m = re.match(r"^(#{1,2})\s+(.*)$", l)
        if m:
            nivel = len(m.group(1))
            titulo = re.sub(r"\s*\{[^{}]*\}\s*$", "", m.group(2)).strip()
            actual = {"n": len(piezas) + 1, "tipo": "divisor" if nivel == 1 else "diapo",
                      "titulo": titulo, "lineas": []}
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
NBSP = "   "
MILES = rf"\d{{1,3}}(?:[ {NBSP}]\d{{3}})+"          # 2 107 · 13 767 · 160 000
NUM = rf"(?:{MILES}|\d+)(?:[.,]\d+)?"
RE_TOKEN = re.compile(rf"(?<![\w.,])([−+\-]?)({NUM})(?![\w])")

# lo que se quita ANTES de buscar cifras (referencias estructurales, no mediciones)
QUITAR = [
    (re.compile(r"`[^`]*`"), " "),                                    # código en línea
    (re.compile(r"!\[([^\]]*)\]\([^)]*\)(\{[^}]*\})?"), r"\1"),      # figuras: solo el pie
    (re.compile(r"<[^>]+>"), " "),                                    # etiquetas html
    (re.compile(r"\]\([^)]*\)"), "]"),                                # destinos de enlaces
    (re.compile(r"\{[.#]?[\w:=. \"-]+\}"), " "),                     # atributos {columnas=3}
    (re.compile(r"(?i)\b(módulos?|mód\.|capítulos?|cap\.|ejercicios?|diapositivas?|fuentes?|semanas?)\s+\d+(?!\d|\.\d)"
                r"(?:\s*(?:a|y|,|–)\s*\d+(?!\d|\.\d))*"), " "),           # «módulos 3 a 9»
    (re.compile(r"(?i)\b(la|las|opción|opciones)\s+[1-4]\b"), " "),      # «La 4», «opción 3»
    (re.compile(r"(?m)^\s*\d+[.)]\s+"), ""),                          # numeración de listas
    (re.compile(r"(?m)^\|\s*\d\s*·\s*"), "| "),                       # «| 1 · La ventana…»
    (re.compile(r"\b(?:1|2k?)/\(?nsim\s*\+\s*1\)?"), " "),             # 1/(nsim + 1)
    (re.compile(r"\b1/2\b"), " "),                                    # «llega a 1/2»
]
RE_GRILLA = re.compile(r"\b(\d+)\s*[×x]\s*(\d+)\b")
RE_VERSION = re.compile(r"\b\d+\.\d+\.\d+\b")
RE_FORMULA = re.compile(r"\$\$(.+?)\$\$|\\\((.+?)\\\)")
RE_EXP = re.compile(r"10<sup>\s*([−-]?\d+(?:\.\d+)?)\s*</sup>")
TRIVIALES = {"0", "1", "2"}


def norm_num(txt: str) -> str:
    t = re.sub(rf"[ {NBSP}]", "", txt)
    return t.replace(",", ".")


def numeros_de(texto: str) -> list[tuple[str, str]]:
    """[(token normalizado, contexto)] de un fragmento de texto."""
    out = []

    def anota(tok, ini, fin, base):
        ctx = base[max(0, ini - 38):fin + 30].replace("\n", " ")
        out.append((tok, re.sub(r"\s+", " ", ctx).strip()))

    base = texto
    # 1 · exponentes 10<sup>-59.5</sup>
    for m in RE_EXP.finditer(base):
        anota("10^" + norm_num(m.group(1).replace("−", "-")), m.start(), m.end(), base)
    base = RE_EXP.sub(" ", base)
    # 2 · fórmulas: se buscan aparte (y se quitan del texto llano)
    formulas = []
    for m in RE_FORMULA.finditer(base):
        formulas.append(m.group(1) or m.group(2))
    base = RE_FORMULA.sub(" ", base)
    # 3 · quitar referencias estructurales
    for rx, rep in QUITAR:
        base = rx.sub(rep, base)
    # 4 · rejillas NxN y versiones
    for m in RE_GRILLA.finditer(base):
        anota(f"{m.group(1)}x{m.group(2)}", m.start(), m.end(), base)
    base = RE_GRILLA.sub(" ", base)
    for m in RE_VERSION.finditer(base):
        anota(m.group(0), m.start(), m.end(), base)
    base = RE_VERSION.sub(" ", base)
    # 5 · el resto de números
    for m in RE_TOKEN.finditer(base):
        signo = "-" if m.group(1) in ("−", "-") else ("+" if m.group(1) == "+" else "")
        tok = norm_num(m.group(2))
        if tok in TRIVIALES:
            continue
        anota(signo + tok if signo == "-" else tok, m.start(), m.end(), base)
    # 6 · números dentro de fórmulas (sin comandos TeX, sin constantes triviales)
    for f in formulas:
        f2 = re.sub(r"\\[a-zA-Z]+", " ", f).replace("\\,", "")
        f2 = re.sub(r"\^\{?\d+\}?|_\{?\d+\}?", " ", f2)                # exponentes y subíndices
        for m in RE_TOKEN.finditer(f2):
            tok = norm_num(m.group(2))
            if tok in TRIVIALES:
                continue
            out.append((tok, "fórmula: " + re.sub(r"\s+", " ", f)[:70]))
    return out


def extrae_todo(piezas: list[dict]) -> list[dict]:
    """Ocurrencias: {n, titulo, donde: 'cuerpo'|'notas'|'titulo', token, contexto}."""
    occ = []
    for p in piezas:
        for donde, txt in (("titulo", p["titulo"]), ("cuerpo", p["cuerpo"]), ("notas", p["notas"])):
            if p["tipo"] == "portada" and donde != "cuerpo":
                continue
            for tok, ctx in numeros_de(txt):
                occ.append({"n": p["n"], "titulo": p["titulo"], "donde": donde, "token": tok, "ctx": ctx})
    return occ


if __name__ == "__main__" and "--tokens" in sys.argv:
    piezas = leer_fuente()
    occ = extrae_todo(piezas)
    por = {}
    for o in occ:
        por.setdefault((o["n"], o["titulo"]), []).append(o)
    for (n, t), lst in por.items():
        print(f"\n[{n}] {t[:70]}")
        for o in lst:
            print(f"   {o['donde'][:1]} {o['token']:<12} | {o['ctx'][:100]}")
    print(f"\n{len(occ)} ocurrencias · {len({o['token'] for o in occ})} números distintos · {len(piezas)} piezas")
    sys.exit(0)


# ----------------------------------------------------------------------------------------
# 3 · Datos de partida (JSON de R, CSV del precálculo, texto del capítulo)
# ----------------------------------------------------------------------------------------
from decimal import Decimal, ROUND_HALF_UP, InvalidOperation

import numpy as np
import pandas as pd
from scipy.spatial import cKDTree
from scipy.stats import chi2 as chi2_dist

D = json.loads((SALIDAS / "cap4_datos.json").read_text(encoding="utf-8"))
SOL = json.loads((SALIDAS / "cap4_soluciones.json").read_text(encoding="utf-8"))
REG = pd.read_csv(SALIDAS / "cap4_regimenes.csv")
BOG = pd.read_csv(SALIDAS / "cap4_bogota_urbana.csv")


def _plano(html: str) -> str:
    import html as _h
    t = re.sub(r"<style.*?</style>", " ", html, flags=re.S)
    t = re.sub(r"<[^>]+>", " ", t)
    t = _h.unescape(t)
    t = unicodedata.normalize("NFKC", t).lower()
    return re.sub(r"\s+", " ", t)


TEXTO_CAP = _plano(CAPITULO_HTML.read_text(encoding="utf-8"))
TEXTO_FUENTES = _plano((RAIZ / "precalculo" / "FUENTES.md").read_text(encoding="utf-8"))


def get(obj, ruta: str):
    """`m6.redwood.chi2[3]` → obj['m6']['redwood']['chi2'][3]."""
    for parte in ruta.split("."):
        m = re.match(r"^(\w+)(?:\[(\d+)\])?$", parte)
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
        return any(igual(token, x) for x in v)                   # «el token es uno de estos valores»
    if token.startswith("10^"):                       # 10^-59.5
        return redondea(v, decimales(token[3:])) == Decimal(token[3:])
    if "x" in token and re.fullmatch(r"\d+x\d+", token):
        a, b = token.split("x")
        permitidos = {int(k) for k in (v if isinstance(v, (list, tuple)) else [v])}
        return a == b and int(a) in permitidos
    try:
        t = Decimal(token)
    except InvalidOperation:
        return False
    return redondea(v, decimales(token)) == t


# ----------------------------------------------------------------------------------------
# 4 · Recomputos independientes (no pasan por R ni por spatstat)
# ----------------------------------------------------------------------------------------
AREA_PAT = {"cells": 1.0, "japanesepines": 1.0, "redwood": 1.0, "swedishpines": 9600.0}
VENT_REDWOOD = ((0.0, 1.0), (-1.0, 0.0))


def _nn(xy):
    return cKDTree(xy).query(xy, k=2)[0][:, 1]


def _celda(v, lo, hi, k):
    b = np.linspace(lo, hi, k + 1)
    return np.clip(np.searchsorted(b, v, side="left") - 1, 0, k - 1)


def _chi2_conteos(c):
    e = c.mean()
    return float(((c - e) ** 2 / e).sum())


def _chi2_redwood(k):
    d = REG[REG.patron == "redwood"]
    c = np.zeros((k, k), int)
    np.add.at(c, (_celda(d.x.to_numpy(), 0, 1, k), _celda(d.y.to_numpy(), -1, 0, k)), 1)
    return _chi2_conteos(c)


def _p_dos_colas(chi, gl):
    """quadrat.test() de spatstat es bilateral por defecto: p = 2 · min(cola inf., cola sup.)."""
    return 2 * min(chi2_dist.sf(chi, gl), chi2_dist.cdf(chi, gl))


def _K_traslacion(x, y, a, b, r):
    n = len(x)
    W = a * b
    dx = np.abs(x[:, None] - x[None, :])
    dy = np.abs(y[:, None] - y[None, :])
    dist = np.hypot(dx, dy)
    sol = np.clip(a - dx, 0, None) * np.clip(b - dy, 0, None)
    m = ~np.eye(n, dtype=bool)
    w, dd = 1 / sol[m], dist[m]
    return np.array([w[dd <= rr].sum() for rr in r]) / (n * (n - 1) / W ** 2)


def _Lr_max(pat):
    """Mayor desvío con signo de L − r sobre la rejilla publicada (101 nodos, sin el último:
    japanesepines tiene doce parejas a exactamente r = 0.25 y ahí spatstat no las cuenta)."""
    d = REG[REG.patron == pat]
    r = np.arange(0, 100) * 0.0025
    K = _K_traslacion(d.x.to_numpy(), d.y.to_numpy(), 1.0, 1.0, r)
    dev = np.sqrt(K / math.pi) - r
    return float(dev[int(np.argmax(np.abs(dev)))])


def _dups():
    xy = list(map(tuple, np.round(BOG[["x", "y"]].to_numpy(), 6)))
    cuenta = pd.Series(xy).value_counts()
    dup = cuenta[cuenta > 1]
    return {"sedes": int(dup.sum()), "sitios": int(len(dup)), "max": int(dup.max()),
            "sobrantes": int(len(xy) - len(cuenta)), "distintos": int(len(cuenta)),
            "sitios2": int((dup == 2).sum())}


def _pois():
    k, o = np.array(D["m4"]["hist_k"]), np.array(D["m4"]["hist_obs"])
    n = int(o.sum())
    m = float((k * o).sum() / n)
    return {"n": n, "media": m, "var": float((o * (k - m) ** 2).sum() / (n - 1)),
            "min": int(k[o > 0].min()), "max": int(k[o > 0].max())}


class Independiente:
    """Cifras recomputadas con los CSV del precálculo, por clave. Se calculan al pedirlas."""

    def __init__(self):
        self._c = {}

    def __getitem__(self, clave):
        if clave not in self._c:
            self._c[clave] = self._calcula(clave)
        return self._c[clave]

    def _calcula(self, k):
        p = k.split(":")
        if k == "n_bog":
            return len(BOG)
        if p[0] == "n":
            return int((REG.patron == p[1]).sum())
        if p[0] == "ce" and p[1] in AREA_PAT:
            d = REG[REG.patron == p[1]][["x", "y"]].to_numpy()
            return float(_nn(d).mean() / (0.5 / math.sqrt(len(d) / AREA_PAT[p[1]])))
        if k == "ce:bogota":
            xy = BOG[["x", "y"]].to_numpy()
            return float(_nn(xy).mean() / (0.5 / math.sqrt(len(xy) / D["m3"]["bogota"]["area"])))
        if k == "nnmax:bogota":
            return float(_nn(BOG[["x", "y"]].to_numpy()).max())
        if k in ("nn:redwood", "ce:redwood"):
            d = REG[REG.patron == "redwood"][["x", "y"]].to_numpy()
            nn = float(_nn(d).mean())
            return nn if k == "nn:redwood" else nn / (0.5 / math.sqrt(len(d)))
        if k in ("nn:reb", "ce:reb"):
            xy = np.c_[D["m5"]["x2"], D["m5"]["y2"]]
            nn = float(_nn(xy).mean())
            return nn if k == "nn:reb" else nn / (0.5 / math.sqrt(len(xy)))
        if p[0] == "chi2" and p[1] == "redwood":
            return _chi2_redwood(int(p[2]))
        if p[0] == "p" and p[1] == "redwood":
            kk = int(p[2])
            return _p_dos_colas(_chi2_redwood(kk), kk * kk - 1)
        if k == "chi2:celdas_reb":                       # χ² a partir de los conteos del patrón rebarajado
            return _chi2_conteos(np.array(D["m5"]["celdas"]["rebarajado"], float))
        if p[0] == "pois":
            return _pois()[p[1]]
        if k == "lam_urb":
            return len(BOG) / D["m1"]["urbana"]["area_km2"]
        if p[0] == "csrmed" and p[1] in ("cells", "japanesepines", "redwood", "bogota"):
            lam = D["m3"][p[1]]["lambda"]
            return math.sqrt(math.log(2) / (lam * math.pi))
        if p[0] == "dup":
            d = _dups()
            return {"sedes": d["sedes"], "sitios": d["sitios"], "max": d["max"], "sobrantes": d["sobrantes"],
                    "distintos": d["distintos"], "sitios2": d["sitios2"],
                    "pct": 100 * d["sedes"] / len(BOG)}[p[1]]
        if k == "g0:bogota":
            return _dups()["sedes"] / len(BOG)
        if k == "j0:bogota":
            return 1 - _dups()["sedes"] / len(BOG)
        if k == "pares1km":
            arbol = cKDTree(BOG[["x", "y"]].to_numpy())
            return int(arbol.count_neighbors(arbol, 1000.0) - len(BOG))
        if k == "crudas1km":
            return self["pares1km"] / len(BOG)
        if p[0] == "Lr":
            return _Lr_max(p[1])
        raise KeyError(k)


IND = Independiente()


# ----------------------------------------------------------------------------------------
# 5 · El registro: cada cifra → de dónde sale y cómo se comprobó
# ----------------------------------------------------------------------------------------
class Spec:
    def __init__(self, tipo, desc, vals=(), url=None, frase=None, corpus=None, tol=None):
        self.tipo, self.desc, self.vals = tipo, desc, list(vals)
        self.url, self.frase, self.corpus, self.tol = url, frase, corpus, tol


def J(ruta, desc=""):
    return Spec("json", desc or f"datos › {ruta}", [("datos › " + ruta, lambda r=ruta: get(D, r))])


def JS(ruta, desc=""):
    return Spec("json", desc or f"soluciones › {ruta}", [("soluciones › " + ruta, lambda r=ruta: get(SOL, r))])


def A(fn, desc):
    return Spec("aritm", desc, [(desc, fn)])


def I(ref, clave, desc="", tol=None):
    """JSON (o aritmética) + recómputo independiente con los CSV. `tol`: cota absoluta para el recómputo."""
    if isinstance(ref, str):
        vj = ("datos › " + ref, lambda r=ref: get(D, r))
        d = desc or f"datos › {ref}; recómputo `{clave}`"
    else:
        vj = (desc, ref)
        d = desc
    return Spec("indep", d, [vj, ("recómputo independiente «" + clave + "»", lambda c=clave: IND[c])], tol=tol)


def IO(clave, desc):
    return Spec("indep", desc, [("recómputo independiente «" + clave + "»", lambda c=clave: IND[c])])


def E(desc, url):
    return Spec("ext", desc, url=url)


def P(desc, ruta=None, fn=None):
    if ruta:
        return Spec("param", desc, [("datos › " + ruta, lambda r=ruta: get(D, r))])
    if fn:
        return Spec("param", desc, [(desc, fn)])
    return Spec("param", desc)


def T(frase, corpus="cap", desc=""):
    return Spec("texto", desc or f"texto del capítulo: «{frase}»", frase=frase, corpus=corpus)


def X(desc, ruta=None, fn=None):
    vals = []
    if ruta:
        vals = [("datos › " + ruta, lambda r=ruta: get(D, r))]
    elif fn:
        vals = [(desc, fn)]
    return Spec("sinver", desc, vals)


def m6(campo, nx, pat="redwood"):
    return lambda: D["m6"][pat][campo][D["m6"]["nxs"].index(nx)]


def m6d(campo, nx, desc):
    return (desc, m6(campo, nx))


REG_ENTRADAS = []


def R(tokens, spec, en=None, cx=None):
    """`en`: prefijos de título de las diapositivas donde vale; `cx`: expresión regular que debe
    aparecer en el contexto inmediato de la cifra (para números con varios significados)."""
    tokens = [tokens] if isinstance(tokens, str) else tokens
    specs = spec if isinstance(spec, list) else [spec]
    REG_ENTRADAS.append({"tokens": tokens, "specs": specs, "en": en, "cx": cx})


# Títulos (prefijo) de las diapositivas, para filtrar los números ambiguos
PORT, CL, LEY = "Portada", "Cómo leer", "Cada cifra"
A1, A2, A3, A4 = "En un patrón puntual", "Misma ciudad", "Un informe dice", "Con λ ="
B1, B2, B3, B4, B5 = "Los tres regímenes", "Clark-Evans:", "CSR es un modelo", "Dos mil realizaciones", "Una R de 0.95"
C1, C2, C3, C4, C5 = "El χ² de cuadrantes", "Dos patrones con el mismo", "El veredicto cambia", "Afinar la rejilla", "Sobre las secuoyas el test"
D3, D4, D5, D6 = "En los patrones de libro", "En Bogotá G y F", "La G sin corregir", "J junta"
E1, E2, E3, E4, E5, E6, E7, E8 = ("K cuenta vecinos", "A 1 km", "L − r pone", "K sigue por encima", "g mira solo",
                                  "K mira todas", "Cinco resúmenes", "K, L − r y g")
F1, F2, F3, F4, G2 = "Ignorar el borde", "Una banda", "El test global", "De 39 a 999", "Cinco ejercicios"

URL_JP = "https://www.quantargo.com/help/r/latest/packages/spatstat.data/2.1-0/japanesepines"
URL_RW = "https://rdrr.io/cran/spatstat.data/man/redwood.html"
URL_SW = "https://rdrr.io/cran/spatstat.data/man/swedishpines.html"
URL_BS = "https://www.rdocumentation.org/packages/spatstat/versions/1.64-1/topics/rcell"
URL_VLB = "https://arxiv.org/pdf/1008.4504"
URL_BVB = ("https://www.cambridge.org/core/journals/advances-in-applied-probability/article/abs/"
           "remark-on-the-van-lieshout-and-baddeley-jfunction-for-point-processes/457DB4680394D8980714DFAE09CAD710")

# ---- portada y arranque ------------------------------------------------------------------
R("90", P("duración de la clase pedida por el docente (90 min); no es un dato del capítulo"), en=(PORT,))
R("0.82371", I("m3.bogota.clark_evans", "ce:bogota"), en=(CL, B2, E7))
R("3.5.1", J("meta.paquetes.spatstat"), en=(LEY,))
# ---- A · ventana e intensidad ------------------------------------------------------------
R("2209", [J("m1.sedes_total"),
           A(lambda: D["m1"]["urbana"]["n"] + D["m1"]["urbana"]["fuera"], "sedes dentro + fuera de la ventana urbana")])
R("12.25", [J("m3.bogota.fuente"), T("versión 12.25", "fuentes", "versión de la fuente (FUENTES.md, fuente 3)")])
R("2107", [I("m1.urbana.n", "n_bog")])
R("2208", [J("m1.dc.n"), JS("e1.solucion.dc.n")], en=(A2,))
R("370.08982", J("m1.urbana.area_km2"))
R("370.09", J("m1.urbana.area_km2"))
R("1633.14040", J("m1.dc.area_km2"))
R("5.69321", I("m1.urbana.lambda_km2", "lam_urb", "λ urbana = n (filas del CSV) / área (JSON)"), en=(A2,))
R("1.35200", [J("m1.dc.lambda_km2"), A(lambda: D["m1"]["dc"]["n"] / D["m1"]["dc"]["area_km2"], "n / área del D.C.")], en=(A2,))
R("4.21097", [J("m1.factor_lambda"), A(lambda: D["m1"]["urbana"]["lambda_km2"] / D["m1"]["dc"]["lambda_km2"], "λ urbana / λ D.C.")], en=(A2,))
R("4.21", J("m1.factor_lambda"), en=(A3,))
R("4.79355", [J("m1.aumento_n_pct"), A(lambda: (D["m1"]["dc"]["n"] - D["m1"]["urbana"]["n"]) / D["m1"]["urbana"]["n"] * 100, "(n D.C. − n urbana) / n urbana · 100")], en=(A2,))
R("4.8", J("m1.aumento_n_pct"), en=(A3,))
R("4.41282", [J("m1.cociente_area"), A(lambda: D["m1"]["dc"]["area_km2"] / D["m1"]["urbana"]["area_km2"], "área D.C. / área urbana")], en=(A2,))
R("5.7", A(lambda: D["m1"]["urbana"]["lambda_km2"], "5,7 = λ urbana (5.6932) redondeada a 1 decimal"), en=(A3, G2))
R("5.6932", J("m1.urbana.lambda_km2"), en=(A3, A4))
R("1.3520", J("m1.dc.lambda_km2"), en=(A3,))
R("0.0569", J("m2.lambda_urbana_ha"), en=(A3,))
R("0.05693", J("m2.lambda_urbana_ha"), en=(A4,))
R("0.0000056932", J("m2.lambda_urbana_m2"), en=(A4,))
R("10x10", P("rejilla 10×10 del módulo 2", fn=lambda: [D["m2"]["urbana"]["nx"]]), en=(A4, C1))
R("65", J("m2.urbana.celdas"), en=(A4, C1))
R("32.41538", [J("m2.urbana.media"), A(lambda: D["m2"]["urbana"]["n_obs"] / D["m2"]["urbana"]["celdas"], "sedes / celdas vivas")], en=(A4,))
R("96", J("m2.urbana.maximo"), en=(A4,))
R("9", J("m2.urbana.vacios"), en=(A4,))
R("25.90966", J("m2.urbana.dispersion"), en=(A4,))
R("15.22998", J("m2.urbana.dispersion_nula"), en=(A4,))
# ---- B · regímenes y CSR -----------------------------------------------------------------
R("42", I("m3.cells.n", "n:cells"))
R("65", J("m4.lambda"), en=(B3, B4))
R("65", I("m3.japanesepines.n", "n:japanesepines"), en=(B1, B2, E1, F2))
R("62", I("m3.redwood.n", "n:redwood"))
R("71", I("m3.swedishpines.n", "n:swedishpines"), en=(B2,))
R("9600", J("m3.swedishpines.area"), en=(B2,))
R("1961", E("Numata (1961): saplings de pino negro japonés, `japanesepines`; 65 puntos", URL_JP))
R("1972", E("Strand (1972): `swedishpines`; 71 árboles en una parcela de 9.6 × 10 m", URL_SW))
R("1975", E("Strauss (1975): `redwood`; 62 plántulas (subconjunto de Ripley)", URL_RW))
R("1977", E("Ripley (1977): subconjunto de `redwood` reescalado al cuadrado unidad", URL_RW))
R("1984", E("Baddeley y Silverman (1984), Biometrics 40, 1089–1094: el «cell process» con K = πr²", URL_BS))
R(["40", "1089", "1094"], E("volumen y páginas de Baddeley y Silverman (1984), cotejados por búsqueda web", URL_BS), en=(E6,))
R("1996", E("van Lieshout y Baddeley (1996), Statistica Neerlandica 50(3), 344–361: la función J", URL_VLB))
R("1997", E("Bedford y van den Berg (1997), Advances in Applied Probability 29, 19–25: procesos con J ≡ 1", URL_BVB))
R(["50", "3", "344", "361", "29", "19", "25"],
  E("volumen, número y páginas de las dos referencias de la diapositiva de J (cotejados por búsqueda web)", URL_VLB), en=(D6,))
R("1.67168", I("m3.cells.clark_evans", "ce:cells"), en=(B2,))
R("1.36008", I("m3.swedishpines.clark_evans", "ce:swedishpines"), en=(B2,))
R("1.06400", I("m3.japanesepines.clark_evans", "ce:japanesepines"), en=(B2, B5))
R("0.61865", I("m3.redwood.clark_evans", "ce:redwood"), en=(B2, C2))
R("41", I("m4.conteo_min", "pois:min", "mínimo de n en las 2 000 realizaciones (a partir del histograma)"), en=(B4,))
R("95", I("m4.conteo_max", "pois:max", "máximo de n en las 2 000 realizaciones (a partir del histograma)"), en=(B4,))
R("95", P("intervalo central del 95 % (cuantiles 0.025 y 0.975 de R bajo CSR)", fn=lambda: 100 * (0.975 - 0.025)), en=(B5,))
R("95", A(lambda: D["m11"]["nivel_puntual"] * 100, "nivel puntual de la banda = 0.95"), en=(F2,))
R("2000", I("m4.n_realizaciones", "pois:n", "número de realizaciones (suma del histograma)"))
R("4026", P("semilla de las simulaciones de CSR", "meta.semillas.csr"), en=(B4,))
R("64.979", I("m4.conteo_media", "pois:media"), en=(B4,))
R("67.673", I("m4.conteo_var", "pois:var"), en=(B4,))
R("0.95", T("índice de clark-evans de 0.95", desc="R = 0.95 es el valor hipotético del enunciado del cuestionario del capítulo"), en=(B5,))
R("0.83013", J("m4.R_csr.min"), en=(B5,))
R("1.34170", J("m4.R_csr.max"), en=(B5,))
R("0.91306", J("m4.R_csr.q025"), en=(B5,))
R("1.20460", J("m4.R_csr.q975"), en=(B5,))
R("438", J("m4.R_csr.bajo_1"), en=(B5,))
R("1.05843", J("m4.R_csr.media"), en=(B5,))
R("1.00751", J("m3.japanesepines.clark_evans_donnelly"), en=(B5,))
# ---- C · cuadrantes ----------------------------------------------------------------------
R("10^-59.5", J("m2.urbana.p_log10"), en=(C1,))
R("456.12", J("m2.urbana.chi2"), en=(C1,))
R("64", J("m2.urbana.gl"), en=(C1,))
R("12", J("m2.urbana.celdas_esperanza_baja"), en=(C1,))
R("5", T("al menos 5 puntos esperados", desc="regla del capítulo: al menos 5 puntos esperados por celda"), en=(C1, C3, C4), cx=r"puntos")
R("5", P("nivel de significancia del 5 %", fn=lambda: 5), en=(C3, F4), cx=r"5 %")
R("0.05", P("umbral convencional de significancia (p < 0.05)", fn=lambda: 0.05), en=(F2,))
R("64.612903", [I("m5.original.chi2", "chi2:redwood:5"), J("m5.rebarajado.chi2"),
                IO("chi2:celdas_reb", "χ² del patrón rebarajado, a partir de sus conteos por celda")], en=(C2,))
R("24", [J("m5.original.gl"), A(lambda: D["m5"]["nx"] ** 2 - 1, "gl = celdas − 1 = 5² − 1")], en=(C2,))
R("0.03928", I("m5.nn_original", "nn:redwood"), en=(C2,))
R("0.05755", I("m5.nn_rebarajado", "nn:reb"), en=(C2,))
R("0.90622", I("m5.ce_rebarajado", "ce:reb"), en=(C2,))
R("1.46484", [J("m5.nn_cociente"), A(lambda: D["m5"]["nn_rebarajado"] / D["m5"]["nn_original"], "nn rebarajado / nn original")], en=(C2,))
R("5x5", P("rejilla 5×5 del módulo 5", fn=lambda: [D["m5"]["nx"]]), en=(C2, C4, C5))
R("4027", P("semilla del patrón rebarajado ('ciego')", "meta.semillas.ciego"), en=(C2,))
R(["2x2", "3x3", "10x10", "20x20"], P("rejillas barridas en el módulo 6", fn=lambda: D["m6"]["nxs"]), en=(C3, C4, C5))
R("10", A(lambda: len(D["m6"]["nxs"]), "número de tamaños de rejilla barridos"), en=(C3, C4), cx=r"tamaños|rejillas|0 de 10|de 10\)")
R("10", JS("e3.solucion.rechazos_urbana"), en=(C3,), cx=r"Bogotá[^0-9]{0,6}10")
R("9", J("m6.redwood_rechazos"), en=(C3,))
R("400", A(lambda: max(D["m6"]["nxs"]) ** 2, "celdas de la rejilla 20×20"), en=(C4,))
R("6.52", I(m6("chi2", 2), "chi2:redwood:2", "datos › m6.redwood.chi2 (nx = 2)"), en=(C4,))
R("0.17806", I(m6("p_valor", 2), "p:redwood:2", "datos › m6.redwood.p_valor (nx = 2)"), en=(C4,))
R("64.61", I(m6("chi2", 5), "chi2:redwood:5", "datos › m6.redwood.chi2 (nx = 5)"), en=(C4,))
R("0.00003", I(m6("p_valor", 5), "p:redwood:5", "datos › m6.redwood.p_valor (nx = 5)"), en=(C4,))
R("202.52", I(m6("chi2", 10), "chi2:redwood:10", "datos › m6.redwood.chi2 (nx = 10)"), en=(C4,))
R("0.00000", I(m6("p_valor", 10), "p:redwood:10", "datos › m6.redwood.p_valor (nx = 10)", tol=1e-6), en=(C4,))
R("505.74", I(m6("chi2", 20), "chi2:redwood:20", "datos › m6.redwood.chi2 (nx = 20)"), en=(C4,))
R("0.00045", I(m6("p_valor", 20), "p:redwood:20", "datos › m6.redwood.p_valor (nx = 20)"), en=(C4,))
# ---- D · G, F, J -------------------------------------------------------------------------
R("0.13036", J("m7.cells.g_mediana"), en=(D3,))
R("0.05959", J("m7.cells.f_mediana"), en=(D3,))
R("0.07248", I("m7.cells.csr_mediana", "csrmed:cells", "mediana de 1 − exp(−λπr²): r = √(ln 2 / λπ)"), en=(D3,))
R("0.06403", J("m7.japanesepines.g_mediana"), en=(D3,))
R("0.05964", J("m7.japanesepines.f_mediana"), en=(D3,))
R("0.05826", I("m7.japanesepines.csr_mediana", "csrmed:japanesepines", "mediana de 1 − exp(−λπr²): r = √(ln 2 / λπ)"), en=(D3,))
R("0.02828", J("m7.redwood.g_mediana"), en=(D3,))
R("0.07769", J("m7.redwood.f_mediana"), en=(D3,))
R("0.05965", I("m7.redwood.csr_mediana", "csrmed:redwood", "mediana de 1 − exp(−λπr²): r = √(ln 2 / λπ)"), en=(D3,))
R("145.52", J("m7.bogota.g_mediana"), en=(D4, E7))
R("222.83", J("m7.bogota.f_mediana"), en=(D4, E7))
R("196.86", I("m7.bogota.csr_mediana", "csrmed:bogota", "mediana de 1 − exp(−λπr²) con λ de Bogotá"), en=(D4, E7))
R("160000", J("m7.bogota.f_rejilla"), en=(D4,))
R("62762", J("m7.bogota.f_sitios"), en=(D4,))
R("0.037494", I("m7.bogota.g_emp_en_cero", "g0:bogota", "G sin corregir en r = 0 = sedes coincidentes / n"), en=(D5,))
R("79", I("m7.bogota.coincidentes", "dup:sedes"), en=(D5,))
R("3.74941", I("m7.bogota.coincidentes_pct", "dup:pct"), en=(D5,))
R("3", I("m7.duplicados.maximo_por_sitio", "dup:max"), en=(D5,))
R("39", IO("dup:sitios", "sitios con coordenadas repetidas, contados en el CSV (el capítulo dice 40: ver hallazgos)"), en=(D5,))
R("38", IO("dup:sitios2", "sitios con exactamente dos sedes (CSV)"), en=(D5,))
R("40", [J("m7.duplicados.repetidos"), IO("dup:sobrantes", "n − sitios distintos = 40 sedes «sobrantes» (no 40 sitios)")], en=(D5,))
R("2067", [J("m7.duplicados.distintos"), IO("dup:distintos", "coordenadas distintas (CSV)")], en=(D5,))
R("0.29192", J("m7.japanesepines.j_min"), en=(D6,))
R("1.50037", J("m7.japanesepines.j_max"), en=(D6,))
R("67", J("m7.bogota.j_bajo_1"), en=(D6, E7))
R("0.962506", [I("m7.bogota.j_en_cero", "j0:bogota", "J en r = 0 = 1 − sedes coincidentes / n")], en=(D6,))
R("0.9", J("m7.j_umbral_f"), en=(D6,))
# ---- E · K, L, g -------------------------------------------------------------------------
R("25.87", [J("m8.piezas.vecinas"), A(lambda: D["m8"]["piezas"]["suma_pesos"] / D["m8"]["piezas"]["n"], "suma de pesos / n")], en=(E2,))
R("17.88", [J("m8.piezas.vecinas_csr"), A(lambda: (D["m8"]["piezas"]["n"] - 1) / D["m8"]["piezas"]["area_km2"] * math.pi, "(n − 1)/|W| · π · (1 km)²")], en=(E2,))
R("1.45", [J("m8.piezas.cociente"), A(lambda: D["m8"]["piezas"]["k_km2"] / D["m8"]["piezas"]["pir2_km2"], "K̂ / πr²")], en=(E2, E8))
R("50368", I("m8.piezas.parejas_r", "pares1km", "parejas ordenadas a ≤ 1 km, contadas con scipy en el CSV"), en=(E2,))
R("54511", J("m8.piezas.suma_pesos"), en=(E2,))
R("4.5464", [J("m8.piezas.k_km2"),
             A(lambda: D["m8"]["piezas"]["area_km2"] / (D["m8"]["piezas"]["n"] * (D["m8"]["piezas"]["n"] - 1)) * D["m8"]["piezas"]["suma_pesos"], "|W|/(n(n−1)) · suma de pesos")], en=(E2,))
R("3.1416", [J("m8.piezas.pir2_km2"), A(lambda: math.pi, "π · (1 km)²")], en=(E2,))
R("23.91", [J("m8.piezas.vecinas_crudas"), I(lambda: D["m8"]["piezas"]["vecinas_crudas"], "crudas1km", "parejas a ≤ 1 km / n")], en=(E2,))
R("25.87", J("m8.piezas.vecinas"), en=(E2,))
R("-0.08463", I("m8.cells.desvio_con_signo", "Lr:cells"), en=(E3,))
R("-0.01473", I("m8.japanesepines.desvio_con_signo", "Lr:japanesepines",
                "el recómputo exacto da −0.01485: la 4.ª cifra depende de la rejilla de publicación (101 nodos)", tol=2e-4), en=(E3,))
R("0.05581", I("m8.redwood.desvio_con_signo", "Lr:redwood"), en=(E3,))
R("331.67", J("m8.bogota.max_desvio"), en=(E3, E7, E8))
R("5105", J("m8.bogota.r_max_desvio"), en=(E3, E7, E8))
R("0.30000", J("m11.test_global.dclf_japanesepines_p"), en=(E3, F3))
R(["500", "20"], T("a 500 m, aunque la agregación real ocurre a 20 m", desc="distancias hipotéticas del enunciado del cuestionario"), en=(E4,))
R("3.27862", J("m9.redwood.g_max"), en=(E5,))
R("0.02250", J("m9.redwood.r_g_max"), en=(E5,))
R("0.1450", J("m9.redwood.r_vuelve_a_1"), en=(E5,))
R("1.60833", J("m9.bogota.g_max"), en=(E5, E8))
R("59", J("m9.bogota.r_g_max"), en=(E5, E8))
R("1.01105", A(lambda: D["m9"]["bogota"]["g_obs"][-1], "último nodo de m9.bogota.g_obs (r = 5868 m)"), en=(E5, E8))
R("5868", [J("m10.r_sesgo_max"), A(lambda: D["m8"]["bogota"]["lado_corto"] / 4, "un cuarto del lado corto de la ventana")])
R("2495", [J("m3.bogota.nn_max"), IO("nnmax:bogota", "mayor distancia al vecino más próximo (scipy, CSV)")], en=(E6,))
R("10", JS("e3.solucion.rechazos_urbana"), en=(E7,))
# ---- F · borde y envolventes -------------------------------------------------------------
R("29.6", [J("m10.sesgo_max_pct"), JS("e5.solucion.sesgo_max_pct")], en=(F1,))
R("29.60530", J("m10.sesgo_max_pct"), en=(F1,))
R("29.60510", JS("e5.solucion.sesgo_max_pct"), en=(F1,))
R("555", X("cociente de tiempos medido por el autor (R 4.4.1, Mac de 12 núcleos): no reproducible aquí", "m10.coste.veces_isotropica_sobre_traslacion"), en=(F1,))
R("0.22", X("tiempo de una estimación de K con corrección de traslación: medido por el autor, depende de la máquina",
            fn=lambda: [c["segundos"] for c in D["m10"]["correcciones"] if c["correccion"] == "translate"][0]), en=(F1,))
R("122.66", X("tiempo de una estimación de K con corrección isotrópica: medido por el autor, depende de la máquina",
              fn=lambda: [c["segundos"] for c in D["m10"]["correcciones"] if c["correccion"] == "isotropic"][0]), en=(F1,))
R("4.4.1", J("m10.coste.medido_en"), en=(F1,))
R("12", J("m10.coste.nucleos"), en=(F1,))
R("22", J("m10.ventana.piezas"), en=(F1, F2))
R("5", J("m10.ventana.agujeros"), en=(F1,))
R("13767", J("m10.ventana.vertices"), en=(F1,))
R("999", J("m11.nsim"), en=(F2, F3, F4))
R("52.2523", [J("m11.tasa_salida_bogota.pct"), A(lambda: D["m11"]["tasa_salida_bogota"]["fuera"] / D["m11"]["nsim"] * 100, "fuera / nsim · 100 = 52.25225…")], en=(F2,))
R("52.1522", [J("m11.tasa_salida_redwood.pct"), A(lambda: D["m11"]["tasa_salida_redwood"]["fuera"] / D["m11"]["nsim"] * 100, "fuera / nsim · 100 = 52.15215…")], en=(F2,))
R("51.0511", [J("m11.japanesepines.tasa_salida.pct"), A(lambda: D["m11"]["japanesepines"]["tasa_salida"]["fuera"] / D["m11"]["nsim"] * 100, "fuera / nsim · 100 = 51.05105…")], en=(F2,))
R("52.25230", T("52.25230", desc="cifra tal como la escribe el capítulo (cinco decimales); el JSON guarda cuatro: 52.2523"), en=(F2,))
R("52.15220", T("52.15220", desc="cifra tal como la escribe el capítulo (cinco decimales); el JSON guarda cuatro: 52.1522"), en=(F2,))
R("51.05110", T("51.05110", desc="cifra tal como la escribe el capítulo (cinco decimales); el JSON guarda cuatro: 51.0511"), en=(F2,))
R("522", J("m11.tasa_salida_bogota.fuera"), en=(F2,))
R("52.25225", A(lambda: D["m11"]["tasa_salida_bogota"]["fuera"] / D["m11"]["nsim"] * 100, "522 / 999 · 100"), en=(F2,))
R("513", J("m11.tasa_salida_bogota.nodos_r"), en=(F2,))
R("0.00100", J("m11.test_global.dclf_bogota_p"), en=(F3,), cx=r"dan p = \*\*0\.00100")
R("0.00100", [J("m11.p_minimo"), A(lambda: 1 / (D["m11"]["nsim"] + 1), "1 / (nsim + 1)")], en=(F3,), cx=r"mínimo posible")
R("0.00100", JS("e4.solucion.dclf_L"), en=(F3,), cx=r"L, todo el rango|rechazar al máximo")
R("0.31800", J("m11.test_global.mad_japanesepines_p"), en=(F3,))
R("0.08100", JS("e4.solucion.tramos[2].dclf_p"), en=(F3,))
R("0.04900", JS("e4.solucion.tramos[0].dclf_p"), en=(F3,))
R("0.00500", JS("e4.solucion.tramos[1].dclf_p"), en=(F3,))
R("20", A(lambda: SOL["e4"]["solucion"]["tramos"][0]["fraccion_del_rango"] * 100, "fracción del rango de r del primer tramo (20 %)"), en=(F3,))
R("40", A(lambda: SOL["e4"]["solucion"]["tramos"][1]["fraccion_del_rango"] * 100, "fracción del rango de r del segundo tramo (40 %)"), en=(F3,))
R(["39", "19"], A(lambda: D["meta"]["nsim_escala"], "valores de nsim barridos en el módulo 11"), en=(F4,))
R("0.05000", A(lambda: 2 / (39 + 1), "nivel puntual por defecto = 2 / (nsim + 1) con nsim = 39"), en=(F4,))
R("0.00200", A(lambda: 2 / (999 + 1), "nivel puntual por defecto = 2 / (nsim + 1) con nsim = 999"), en=(F4,))
R("1.84853", J("m11.escala_resumen.veces_defecto"), en=(F4,))
R("1.29989", J("m11.escala_resumen.veces_5pct_alcanzable"), en=(F4,))
R("3x3", A(lambda: [nx for nx, eb, rz in zip(D["m6"]["nxs"], D["m6"]["redwood"]["celdas_esperanza_baja"], D["m6"]["redwood"]["rechaza"])
                    if eb == 0 and rz][0], "única rejilla que respeta el supuesto y rechaza"), en=(C4,))


# ----------------------------------------------------------------------------------------
# 6 · Hallazgos en el material (no son errores de la presentación: son del capítulo)
# ----------------------------------------------------------------------------------------
HALLAZGOS = [
    ("Sitios con sedes coincidentes",
     "El módulo 7 dice que las 79 sedes coincidentes están «repartidas en 40 sitios». Recomputado con las coordenadas "
     "de `cap4_bogota_urbana.csv`: son **39** sitios (38 con dos sedes y 1 con tres). El 40 es `n − distintos` = "
     "2 107 − 2 067, el número de sedes «sobrantes» (`m7.duplicados.repetidos`), no el de sitios. "
     "La diapositiva no cita el número de sitios."),
    ("«Tres decisiones» frente a «cuatro»",
     "El módulo 1 llama a la ventana «la primera de las tres decisiones que este capítulo obliga a declarar»; "
     "los módulos 11 y 12 hablan de «cuatro piezas» y «cuatro cosas» (ventana, escala, borde, referencia). "
     "La presentación no dice un número en el módulo 1 y usa las cuatro en la tesis."),
    ("Sesgo máximo de K sin corregir",
     "El módulo 10 da 29.60530 % (`m10.sesgo_max_pct`) y la solución del ejercicio 5, 29.60510 % "
     "(`e5.solucion.sesgo_max_pct`). Se miden en rejillas distintas; las dos redondean a 29.6 %, que es lo que se proyecta."),
    ("Tasas de salida de la banda con cinco decimales",
     "El módulo 11 escribe 52.25230 %, 52.15220 % y 51.05110 %. El JSON guarda 52.2523, 52.1522 y 51.0511 (cuatro decimales) y "
     "los valores exactos son 522/999 = 52.25225…, 521/999 = 52.15215… y 510/999 = 51.05105…: el cero final es relleno. "
     "La diapositiva usa cuatro decimales."),
    ("Desvío máximo de L − r en los pinos japoneses",
     "El JSON publica −0.01473; el recómputo exacto con los puntos crudos da −0.01485 (misma r = 0.1475). "
     "No es un error: la curva se publica en una rejilla de 101 nodos re-muestreada desde la nativa de spatstat "
     "(513 nodos) y los pinos tienen coordenadas a dos decimales, con muchas parejas exactamente sobre un nodo. "
     "Coinciden en signo, en r y a dos cifras (−0.015)."),
]

ETIQUETA = {"indep": "VERIFICADA · recómputo independiente", "aritm": "VERIFICADA · aritmética sobre el JSON",
            "json": "CONTRASTADA · salida de R (JSON)", "param": "PARÁMETRO de diseño",
            "texto": "CONTRASTADA · texto del capítulo", "ext": "REFERENCIA externa cotejada",
            "sinver": "[SIN VERIFICAR]"}
PRIORIDAD = ["indep", "aritm", "json", "texto", "param", "ext", "sinver"]


def evalua(spec: Spec, token: str):
    """→ (ok, detalle). `ok` es True/False; el detalle dice qué se comparó."""
    if spec.tipo in ("ext",):
        return True, spec.desc + (f" · {spec.url}" if spec.url else "")
    if spec.tipo == "texto":
        corpus = TEXTO_CAP if spec.corpus == "cap" else TEXTO_FUENTES
        f = unicodedata.normalize("NFKC", spec.frase).lower()
        return (f in corpus), spec.desc + ("" if f in corpus else " · NO ENCONTRADA")
    partes, ok = [], True
    es_param_sin_val = spec.tipo == "param" and not spec.vals
    if es_param_sin_val:
        return True, spec.desc
    for etq, fn in spec.vals:
        try:
            v = fn()
        except Exception as ex:                                  # ruta inexistente, etc.
            return False, f"{etq}: ERROR {ex!r}"
        es_indep = etq.startswith("recómputo")
        if es_indep and spec.tol is not None and spec.tipo == "indep":
            vj = spec.vals[0][1]()
            good = abs(float(v) - float(vj)) <= spec.tol
            partes.append(f"{etq} = {float(v):.5g} (|Δ| ≤ {spec.tol:g} respecto de {float(vj):.5g})")
        else:
            good = igual(token, v)
            partes.append(f"{etq} = {v if isinstance(v, (str, int)) else f'{float(v):.10g}' if not isinstance(v, (list, tuple)) else v}")
        ok = ok and good
    return ok, "; ".join(partes) + ("" if ok else "  ← NO COINCIDE")


def busca(entradas, token, titulo, ctx=""):
    """Entradas del registro aplicables a (token, título de diapositiva, contexto)."""
    out = []
    for e in entradas:
        if (token in e["tokens"] and (e["en"] is None or any(titulo.startswith(p) for p in e["en"]))
                and (e.get("cx") is None or re.search(e["cx"], ctx))):
            out.append(e)
    return out


def verifica(occ):
    """→ (filas, errores). Una fila por ocurrencia."""
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
                cache[clave] = (all(r[0] for r in res), " | ".join(r[1] for r in res))
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
# 7 · Comprobaciones estructurales
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
    # toda cifra [SIN VERIFICAR] visible debe llevar la marca en la propia diapositiva
    for f in filas:
        if f["tipo"] == "sinver":
            p = next(q for q in piezas if q["n"] == f["n"])
            if "SIN VERIFICAR" not in (p["cuerpo"] + p["notas"]) and "no se pudieron reproducir" not in p["notas"]:
                errs.append(f"SIN MARCA · diapositiva {p['n']}: {f['token']} no se pudo verificar y no lleva [SIN VERIFICAR]")
            if f["donde"] == "cuerpo" and "SIN VERIFICAR" not in p["cuerpo"]:
                errs.append(f"SIN MARCA VISIBLE · diapositiva {p['n']}: {f['token']} está en la lámina sin la marca [SIN VERIFICAR]")
    return errs


# ----------------------------------------------------------------------------------------
# 8 · El registro en Markdown
# ----------------------------------------------------------------------------------------
def escribe_registro(piezas, filas):
    cuenta = {}
    for f in filas:
        cuenta[f["estado"]] = cuenta.get(f["estado"], 0) + 1
    unicas = {}
    for f in filas:
        unicas.setdefault(f["token"], f["estado"])
    L = ["# Registro de cifras · Capítulo 4 · Patrones puntuales", "",
         "Generado por `verifica_cifras.py` a partir de `capitulo_4.md`. **No se edita a mano**: se regenera.", "",
         "## Cómo se comprobó cada cifra", "",
         "| Estado | Qué significa |", "|---|---|",
         "| VERIFICADA · recómputo independiente | La cifra sale del JSON de R **y** se recalculó desde los puntos crudos "
         "(`precalculo/salidas/*.csv`) con scipy, sin pasar por R ni por spatstat, y coincide. |",
         "| VERIFICADA · aritmética sobre el JSON | Se recompone con una cuenta a partir de otras cifras del JSON. |",
         "| CONTRASTADA · salida de R (JSON) | Coincide con `cap4_datos.json` / `cap4_soluciones.json`, redondeada a los decimales que se muestran. "
         "No se pudo recalcular aquí (depende de la geometría de la ventana, que no se versiona, o de estimadores internos de spatstat). |",
         "| CONTRASTADA · texto del capítulo | Solo figura en la prosa del capítulo publicado; la frase existe en el HTML. |",
         "| PARÁMETRO de diseño | Rejillas, semillas, niveles: decisiones del capítulo, cotejadas con el JSON cuando el JSON las trae. |",
         "| REFERENCIA externa cotejada | Año, revista y páginas de una referencia; cotejados por búsqueda web el 2026-09-29 (URL en el detalle). |",
         "| **[SIN VERIFICAR]** | No se pudo comprobar aquí. Lleva la marca en la diapositiva y no se presenta como dato confirmado. |",
         "", "Los enteros 0, 1 y 2 usados como constantes de definición («R < 1», «1 − G») no se registran: no son mediciones.", "",
         "## Resumen", "",
         f"- {len(filas)} apariciones de cifras en {len({f['n'] for f in filas})} diapositivas; {len(unicas)} cifras distintas.",
         *[f"- {k}: {v}" for k, v in sorted(cuenta.items(), key=lambda kv: -kv[1])], "",
         "## Hallazgos en el material del capítulo", "",
         "Discrepancias que aparecieron al cotejar. No son errores de la presentación: se dicen aquí y en las notas, "
         "y no se corrigen en silencio.", ""]
    for t, d in HALLAZGOS:
        L += [f"- **{t}.** {d}"]
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
    REGISTRO_MD.write_text("\n".join(L), encoding="utf-8")


# ----------------------------------------------------------------------------------------
# 9 · Principal
# ----------------------------------------------------------------------------------------
def main() -> int:
    global REGISTRO_MD
    ruta = FUENTE
    if "--fuente" in sys.argv:
        ruta = Path(sys.argv[sys.argv.index("--fuente") + 1])
    piezas = leer_fuente(ruta)
    occ = extrae_todo(piezas)
    filas, errores = verifica(occ)
    errores += estructura(piezas, filas)
    if "--sin-escribir" not in sys.argv:
        escribe_registro(piezas, filas)
    cuenta = {}
    for f in filas:
        cuenta[f["estado"]] = cuenta.get(f["estado"], 0) + 1
    print(f"{len(filas)} apariciones · {len({f['token'] for f in filas})} cifras distintas · {len(piezas)} piezas")
    for k, v in sorted(cuenta.items(), key=lambda kv: -kv[1]):
        print(f"  {v:4d}  {k}")
    if "--sin-escribir" not in sys.argv:
        print(f"registro → {REGISTRO_MD.relative_to(RAIZ)}")
    if errores:
        print(f"\n{len(errores)} PROBLEMAS:")
        for e in errores:
            print("  ✗", e)
        return 1
    print("\n✓ todas las cifras están registradas y coinciden con su fuente")
    return 0


if __name__ == "__main__":
    sys.exit(main())
