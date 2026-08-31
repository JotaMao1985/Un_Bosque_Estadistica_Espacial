#!/usr/bin/env python3
"""
audita_preparcial1.py — auditoría independiente del preparcial del Corte I (P1.2)

Material de Estadística Espacial 2026-II (20929). Ver PLAN_Preparcial_Corte_1.md.

NO comprueba que el JSON exista: comprueba que sus números sean ciertos, por
caminos que no pasan por R. Mismo motivo que en los capítulos y en el taller
—un control que comparte entorno con lo que audita no es independiente—, y
aquí con dos agravantes propios de este documento.

EL PRIMERO, Y ES LA RAZÓN DE QUE ESTE ARCHIVO EXISTA: LA SINCRONÍA.

El preparcial es el único documento del sitio que **cita cifras de otros**.
Las 119 entradas de `reutilizado` no son copias: cada una guarda de qué
archivo y de qué ruta salió. El día que un capítulo se regenere y una de esas
cifras cambie, la pregunta del preparcial queda mintiendo **sin que nada lo
diga**, porque su JSON sigue siendo internamente coherente. La familia 2
vuelve a resolver las 119 rutas contra los capítulos publicados, que es la
única comprobación que ni los capítulos ni el taller necesitan tener.

Tardó una tarde en cobrarse: ver §12.4 del plan. Y tiene un segundo piso, que
la familia 2 también mira: el HTML publicado lleva el JSON incrustado, así que
regenerar el precálculo **y no reensamblar** deja las preguntas citando cifras
viejas con el JSON del disco ya corregido. Se compara el uno contra el otro.

EL SEGUNDO: LAS PREGUNTAS NO ESTÁN EN EL JSON, ESTÁN EN EL HTML.

`preparcial1_datos.json` trae las cifras; los enunciados, las opciones y la
retroalimentación los escribe `ensambla_preparcial1.py` y solo existen en el
documento publicado. Auditar el JSON y dar el preparcial por auditado sería
mirar la mitad. Las familias 3, 4 y 5 leen las cuatro autoevaluaciones del
HTML —con un analizador propio, más abajo— y comprueban lo que el ensamblador
no puede ver desde dentro.

LO QUE DESTAPÓ AL ESCRIBIRSE, y las dos cosas son de contenido:

  · **La correcta caía la primera en las 29 preguntas con opciones.** Cada
    pregunta era impecable por separado y las cinco guardas del ensamblador
    miraban una pregunta cada vez; juntas, el preparcial se aprobaba marcando
    siempre la (a). Es la familia 5 de aquí, y obligó a barajar las opciones
    en el ensamblador y a reescribir catorce retroalimentaciones que decían
    «las dos primeras».
  · **La esfera de s2 no es el radio medio del WGS84.** El bloque de código
    del módulo 5 la construía con 6 371 008,8 m; s2 usa 6 371 010,0 m, y con
    ese —y solo con ese— pyproj reproduce la columna «esfera» del capítulo 2
    a 4·10⁻¹¹ m. Dos centímetros por grado que `verifica_bloques.py` no podía
    ver, porque el bloque publica la cifra redondeada a metros.

LAS CINCO FAMILIAS

  1. **Cifras nuevas** — las cuatro de `nuevo`, rehechas desde la fuente
     primaria: el CSV de municipios, el GeoPackage de estaciones, el de
     condados, y pyproj en vez de lwgeom y de s2.
  2. **Sincronía** — las 119 reutilizadas contra su ruta en `capN_datos.json`,
     y el JSON incrustado en el HTML contra el JSON del disco.
  3. **Cobertura** — los 30 módulos con pregunta, ninguna fuera del alcance,
     y el `repaso` de cada pregunta resuelto contra el capítulo publicado:
     título, archivo y `<template>` de destino.
  4. **Retroalimentación completa** — toda opción con `retro` no vacía y
     distinta de sus hermanas, y el número de correctas que exige cada tipo.
  5. **No filtración** — el enunciado y la pista no regalan la opción
     correcta, y **la posición tampoco**.

Uso:  <geo_env>/python precalculo/audita_preparcial1.py
      (desde la carpeta `Estadistica espacial/`)
Con el intérprete de geo_env: necesita geopandas, pyproj y mapclassify.
Devuelve 1 si algo falla.

PREPARCIAL1_DATOS, PREPARCIAL1_HTML y PREPARCIAL1_CAPS permiten apuntar a
copias con defectos inyectados, que es lo que hará
`prueba_auditor_preparcial1.py` en P1.3. Los archivos publicados no se tocan
nunca.

La tercera hace falta y las otras dos no bastaban: la familia 2 compara el
preparcial contra los CAPÍTULOS, y la desincronización que existe de verdad
—§12.4— no la provoca este documento, la provoca que un capítulo se regenere
debajo. Envenenar el preparcial prueba la comprobación por el lado que nunca
falla solo. `PREPARCIAL1_CAPS` apunta a una carpeta con copias de
`capN_datos.json`, y así se puede mover el capítulo sin escribir en
`precalculo/salidas/`.
"""
from __future__ import annotations

import datetime
import json
import math
import os
import pathlib
import re
import sys
import warnings

warnings.filterwarnings("ignore")
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

RAIZ = pathlib.Path(__file__).resolve().parent.parent
SALIDAS = RAIZ / "precalculo" / "salidas"
PROCESADO = RAIZ / "datos" / "procesado"
HTMLS = RAIZ / "Htmls_Espacial"

from audita_base import Auditoria, carga, sin_nan  # noqa: E402
import alcance_preparcial1 as ALC  # noqa: E402

# El radio de la esfera sobre la que mide s2. NO es el radio medio del WGS84
# —6 371 008,8 m, que es (2a+b)/3 y la respuesta que parece—: es 6 371 010,0.
# La diferencia son 1,2 m de radio y 2 cm por grado de longitud, y se
# comprueba abajo reproduciendo la columna entera del capítulo 2 con las dos.
RADIO_S2 = 6371010.0
RADIO_MEDIO_WGS84 = 6371008.8


# =====================================================================
# EL ANALIZADOR DE LAS AUTOEVALUACIONES
#
# Las preguntas viajan como literales de JavaScript dentro del HTML, y no
# son JSON: las claves van sin comillas y `dibujar` guarda una función de
# flecha. Se podía haber sacado a golpe de expresión regular, y no: una
# regular que se deje una pregunta no falla, informa de menos, y el
# recuento de cobertura sale bien con una pregunta menos vigilada. Por eso
# hay un analizador de verdad —objetos, listas, cadenas JSON, números,
# booleanos— y un único caso especial: cualquier valor que no empiece por
# uno de esos se consume entero contando llaves y respetando las cadenas.
# Así la función de dibujo se salta sola.
#
# Y se comprueba a sí mismo: el número de preguntas que devuelve tiene que
# coincidir con el de marcas `tipo:` que cuenta `cuenta_sitio.py`.
# =====================================================================
_ESPACIO = " \t\r\n"
_RE_NUM = re.compile(r"-?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?")


def _salta(s: str, i: int) -> int:
    while i < len(s) and s[i] in _ESPACIO:
        i += 1
    return i


def _cadena(s: str, i: int, comilla: str = '"'):
    j = i + 1
    while j < len(s):
        if s[j] == "\\":
            j += 2
            continue
        if s[j] == comilla:
            crudo = s[i:j + 1]
            if comilla == '"':
                return json.loads(crudo), j + 1
            return crudo[1:-1], j + 1
        j += 1
    raise ValueError(f"cadena sin cerrar en la posición {i}")


def _opaco(s: str, i: int):
    """Un valor que no es JSON —la función de dibujo— consumido entero."""
    prof, j = 0, i
    while j < len(s):
        c = s[j]
        if c in "\"'":
            _, j = _cadena(s, j, c)
            continue
        if c in "{[(":
            prof += 1
        elif c in "}])":
            if prof == 0:
                break
            prof -= 1
        elif c == "," and prof == 0:
            break
        j += 1
    return s[i:j].strip(), j


def _valor(s: str, i: int):
    i = _salta(s, i)
    c = s[i]
    if c == '"':
        return _cadena(s, i)
    if c == "{":
        obj, j = {}, _salta(s, i + 1)
        if s[j] == "}":
            return obj, j + 1
        while True:
            j = _salta(s, j)
            if s[j] == '"':
                clave, j = _cadena(s, j)
            else:
                k = j
                while s[k] not in _ESPACIO + ":":
                    k += 1
                clave, j = s[j:k], k
            j = _salta(s, j)
            if s[j] != ":":
                raise ValueError(f"falta «:» tras «{clave}»")
            valor, j = _valor(s, j + 1)
            obj[clave] = valor
            j = _salta(s, j)
            if s[j] == ",":
                j += 1
                continue
            if s[j] == "}":
                return obj, j + 1
            raise ValueError(f"objeto mal cerrado tras «{clave}»")
    if c == "[":
        arr, j = [], _salta(s, i + 1)
        if s[j] == "]":
            return arr, j + 1
        while True:
            valor, j = _valor(s, j)
            arr.append(valor)
            j = _salta(s, j)
            if s[j] == ",":
                j = _salta(s, j + 1)
                continue
            if s[j] == "]":
                return arr, j + 1
            raise ValueError("lista mal cerrada")
    for lit, v in (("true", True), ("false", False), ("null", None)):
        if s.startswith(lit, i):
            return v, i + len(lit)
    m = _RE_NUM.match(s, i)
    if m:
        t = m.group(0)
        return (float(t) if "." in t or "e" in t.lower() else int(t)), m.end()
    return _opaco(s, i)


def lee_autoevaluaciones(html: str) -> dict:
    bloques = {}
    for m in re.finditer(r"\n    AUTOEVALUACIONES\['([^']+)'\] = ", html):
        i = html.index("[", m.end() - 1)
        valor, _ = _valor(html, i)
        bloques[m.group(1)] = valor
    return bloques


# =====================================================================
# EL RESOLUTOR DE RUTAS de `reutilizado`, gemelo del `en_ruta()` de
# `genera_preparcial1.R`. Los índices vienen EN BASE 1 porque los escribió
# R —`tobler.ideam.bandas[1].I`—, así que aquí se restan. Escribirlos en
# base 0 «porque esto es Python» leería la banda equivocada y devolvería
# un número perfectamente plausible.
# =====================================================================
def _flotantes(o, ruta=""):
    """(ruta, decimales, valor) de cada flotante en notación decimal.

    Es `decimales()` de `audita_base.py` devolviendo TAMBIÉN el valor. La
    primera versión recorría el objeto dos veces y emparejaba los dos
    generadores con `zip`, que funciona mientras los dos filtren igual —y
    el día que uno de los dos cambie, el aviso señalará la ruta de un
    número y el valor de otro sin que nada falle.
    """
    if isinstance(o, dict):
        for k, v in o.items():
            yield from _flotantes(v, f"{ruta}.{k}")
    elif isinstance(o, list):
        for i, v in enumerate(o):
            yield from _flotantes(v, f"[{i}]" if not ruta else f"{ruta}[{i}]")
    elif isinstance(o, float):
        t = repr(o)
        if "." in t and "e" not in t and "E" not in t:
            yield ruta, len(t.split(".")[1]), o


def _significativas(x: float) -> int:
    t = repr(abs(x)).replace(".", "").lstrip("0")
    return len(t.rstrip("0")) or 1


def _primera_diferencia(a, b, ruta=""):
    """Dónde empiezan a diferir dos objetos, dicho por su ruta.

    Sin esto, el aviso de que el HTML lleva un precálculo distinto se
    quedaba en las dos marcas de tiempo, que son iguales en el caso que
    importa: el JSON se regeneró y el HTML no. Lo que hace falta saber es
    QUÉ cifra se movió.
    """
    if type(a) is not type(b) and not (isinstance(a, (int, float))
                                       and isinstance(b, (int, float))):
        return f"{ruta or '.'}: {type(a).__name__} contra {type(b).__name__}"
    if isinstance(a, dict):
        for k in sorted(set(a) | set(b)):
            if k not in a or k not in b:
                return f"{ruta}.{k}: solo está en uno de los dos"
            d = _primera_diferencia(a[k], b[k], f"{ruta}.{k}")
            if d:
                return d
        return ""
    if isinstance(a, list):
        if len(a) != len(b):
            return f"{ruta}: {len(a)} elementos contra {len(b)}"
        for i, (x, y) in enumerate(zip(a, b)):
            d = _primera_diferencia(x, y, f"{ruta}[{i}]")
            if d:
                return d
        return ""
    return "" if a == b else f"{ruta}: {a!r} contra {b!r}"


_AUSENTE = object()
_RE_PASO = re.compile(r"^([^\[]*)((?:\[\d+\])*)$")


def en_ruta(obj, ruta: str):
    cur = obj
    for paso in ruta.split("."):
        m = _RE_PASO.match(paso)
        if not m:
            return _AUSENTE
        nombre, corchetes = m.group(1), re.findall(r"\[(\d+)\]", m.group(2))
        if nombre:
            if not isinstance(cur, dict) or nombre not in cur:
                return _AUSENTE
            cur = cur[nombre]
        for k in corchetes:
            i = int(k) - 1
            if not isinstance(cur, list) or not (0 <= i < len(cur)):
                return _AUSENTE
            cur = cur[i]
    return cur


# =====================================================================
# El recuento POR FAMILIA, que es lo que pide P1.2. `Auditoria` cuenta el
# total; aquí se toman marcas antes y después de cada familia y al final se
# imprime la tabla. Vive en este archivo y no en `audita_base.py` a
# propósito: subirlo obligaría a retropropagar a los cinco auditores que
# ya están en verde, y el requisito es de este documento.
# =====================================================================
class Familias:
    def __init__(self, a: Auditoria) -> None:
        self.a, self.filas, self._abierta = a, [], None

    def abre(self, n: int, titulo: str) -> None:
        self.cierra()
        self._abierta = (n, titulo, self.a.n, len(self.a.fallos),
                         len(self.a.saltadas))
        self.a.titulo(f"Familia {n} · {titulo}" if n else titulo)

    def cierra(self) -> None:
        if self._abierta is None:
            return
        n, titulo, n0, f0, s0 = self._abierta
        self.filas.append((n, titulo, self.a.n - n0,
                           len(self.a.fallos) - f0, len(self.a.saltadas) - s0))
        self._abierta = None

    def informe(self) -> None:
        self.cierra()
        print("\n=== Recuento por familia " + "=" * 38)
        for n, titulo, comp, fallos, saltadas in self.filas:
            marca = "OK " if not fallos else "MAL"
            etq = f"{n}. {titulo}" if n else titulo
            print(f"  {marca}  {etq:<46} {comp:>4} compr. "
                  f"{fallos:>3} fallos {saltadas:>3} saltadas")


def main() -> int:  # noqa: C901
    import geopandas as gpd
    import mapclassify as mc
    import numpy as np
    import pandas as pd
    import pyproj

    a = Auditoria("Preparcial del Corte I verificado")
    fam = Familias(a)

    D, ruta_d = carga("PREPARCIAL1_DATOS", "preparcial1_datos.json", SALIDAS)
    ruta_h = pathlib.Path(os.environ.get("PREPARCIAL1_HTML")
                          or (HTMLS / "preparcial-corte-1.html"))
    if not ruta_h.exists():
        sys.exit(f"PARADO: falta {ruta_h}")
    html = ruta_h.read_text(encoding="utf-8")
    print(f"\n=== audita_preparcial1.py · {ruta_d.name} + {ruta_h.name} ===")

    meta, REU, NUEVO = D["meta"], D["reutilizado"], D["nuevo"]
    ERRORES, GRAFICOS = D["errores"], D["graficos"]
    crudo = ruta_d.read_text(encoding="utf-8")

    # -----------------------------------------------------------------
    fam.abre(0, "Formato: sin NaN, con holgura, sin mojibake")
    a.cierto(not list(sin_nan(D)), "ningún NaN ni infinito en el precálculo")
    # LA HOLGURA TIENE DOS REGÍMENES, Y AQUÍ HACEN FALTA LOS DOS. El resto
    # de los auditores comprueba «ningún flotante pasa de diez decimales»
    # y les basta porque todas sus cifras son de orden 1. Aquí no: el
    # `toJSON(digits = 10)` de jsonlite recorta a diez DECIMALES cuando el
    # valor pasa de 1 y a once cifras SIGNIFICATIVAS cuando no llega —
    # medido, no supuesto: 110945.9086361031 sale con diez decimales y
    # 0.0094988291385 con trece—. Con la regla de los diez decimales a
    # secas, las tres cifras pequeñas de `nuevo` salían en rojo estando
    # perfectamente escritas.
    largos = [(r, d) for r, d, v in _flotantes(D)
              if (d > 10 if abs(v) >= 1 else _significativas(v) > 11)]
    a.cierto(not largos, "ningún flotante lleva más precisión de la escrita",
             str(largos[:3]))
    a.cierto("<U+" not in crudo and "<c3>" not in crudo and "<c2>" not in crudo,
             "las tildes llegaron enteras al JSON")
    a.cierto("<U+" not in html, "y al HTML publicado")
    a.igual(len(REU), meta["n_reutilizadas"], "las reutilizadas que declara meta")
    a.igual(len(NUEVO), meta["n_nuevas"], "los cálculos nuevos que declara meta")
    a.igual(len(GRAFICOS), meta["n_graficos"], "los gráficos que declara meta")
    a.igual(len(ERRORES), meta["n_errores"], "los errores que declara meta")
    a.igual(len(meta["alcance"]), meta["n_modulos_alcance"],
            "el alcance que declara meta")
    a.cierto(sorted(meta["alcance"]) == sorted(ALC.CLAVES),
             "y es exactamente el que lee alcance_preparcial1",
             str(sorted(set(meta["alcance"]) ^ ALC.CLAVES)))
    try:
        datetime.date.fromisoformat(meta["fecha_parcial"])
        fecha_ok = True
    except ValueError:
        fecha_ok = False
    a.cierto(fecha_ok, "la fecha del parcial es una fecha", meta["fecha_parcial"])

    # =================================================================
    fam.abre(1, "Las cifras nuevas, y sus distractores")

    # --- N1 · tamaño efectivo, contra el CSV de municipios ------------
    N1 = NUEVO["n_efectivo"]
    llave = pd.read_csv(PROCESADO / "municipios_llave.csv", dtype={"divipola": str})
    a.igual(int(llave["desercion"].notna().sum()), N1["n"],
            "N1: municipios con deserción, contados por pandas")
    n1, rho = float(N1["n"]), float(N1["rho"])
    neff = lambda n, r: n / (1 + (n - 1) * r)  # noqa: E731
    a.igual(neff(n1, rho), N1["correcto"], "N1: n / (1 + (n-1)·rho)", 1e-9)
    # 1e-6, que es la tolerancia del ancla del propio generador, y por una
    # razón que conviene dejar escrita: el capítulo calculó su n efectivo
    # con el rho SIN redondear, y lo único que el preparcial puede leer es
    # el rho ya escrito en el JSON con diez cifras. Los dos caminos se
    # separan 1,8·10⁻⁷ sobre 64,5. Apretar esto a 1e-9 sería exigir que el
    # preparcial reprodujera un número que no tiene forma de ver.
    a.igual(N1["correcto"], REU["neff_desercion"]["valor"],
            "N1: y es la cifra que publica el capítulo 1", 1e-6)
    a.igual(100 * N1["correcto"] / n1, REU["neff_pct"]["valor"],
            "N1: el % de información que queda", 1e-6)
    dist1 = {d["id"]: d["valor"] for d in N1["distractores"]}
    a.igual(n1 * (1 - rho), dist1["resta_lineal"],
            "N1: el distractor de la resta lineal", 1e-9)
    a.igual(neff(n1, REU["neff_I_primera_banda"]["valor"]),
            dist1["rho_primera_banda"],
            "N1: el que mete el Moran de la primera banda", 1e-9)
    a.igual(n1 * (1 + (n1 - 1) * rho), dist1["multiplica"],
            "N1: el que multiplica por el efecto de diseño", 1e-9)
    nota = N1["nota_n_menos_1"]
    a.igual(n1 / (1 + n1 * rho), nota["con_n"], "N1: la nota, con n en vez de n-1", 1e-9)
    a.igual(neff(25, rho), nota["con_n_menos_1_25"], "N1: la nota, n pequeño con n-1", 1e-9)
    a.igual(25 / (1 + 25 * rho), nota["con_n_25"], "N1: la nota, n pequeño con n", 1e-9)
    a.cierto(abs(nota["con_n_menos_1_25"] - nota["con_n_25"])
             > abs(nota["con_n_menos_1"] - nota["con_n"]),
             "N1: el (n-1) pesa más con n pequeño, que es lo que dice")

    # --- N2 · el grado de longitud, con pyproj en vez de lwgeom -------
    N2 = NUEVO["grado_longitud"]
    semi_a = float(REU["elip_a"]["valor"])
    f = 1.0 / float(REU["elip_f_inv"]["valor"])
    e2 = 2 * f - f * f
    lat = float(N2["lat"])
    phi = math.radians(lat)
    rad_n = semi_a / math.sqrt(1 - e2 * math.sin(phi) ** 2)
    rad_m = semi_a * (1 - e2) / (1 - e2 * math.sin(phi) ** 2) ** 1.5
    geo_eli = pyproj.Geod(a=semi_a, f=f)
    geo_esf = pyproj.Geod(a=RADIO_S2, f=0)
    g_eli = geo_eli.inv(0.0, lat, 1.0, lat)[2]
    g_esf = geo_esf.inv(0.0, lat, 1.0, lat)[2]
    a.igual(g_eli, N2["correcto"], "N2: la geodésica elipsoidal, con pyproj", 1e-6)
    a.igual(N2["correcto"], REU["grad_lon_elip"]["valor"][1],
            "N2: y es la columna elipsoidal del capítulo 2", 1e-6)
    dist2 = {d["id"]: d["valor"] for d in N2["distractores"]}
    a.igual(g_esf, dist2["s2_esfera"], "N2: la esférica, que es la que da s2", 1e-6)
    a.igual(math.radians(1) * rad_n, dist2["olvida_coseno"],
            "N2: el distractor que olvida el coseno", 1e-6)
    a.igual(math.radians(1) * rad_m * math.cos(phi), dist2["radio_meridional"],
            "N2: el que usa el radio meridional", 1e-6)
    a.igual(g_esf - g_eli, N2["dif_s2_m"], "N2: lo que s2 se queda corto por grado", 1e-6)
    arco = math.radians(1) * rad_n * math.cos(phi)
    a.igual(arco, N2["nota_arco"]["valor"], "N2: el arco de paralelo de la nota", 1e-6)
    a.igual(arco - N2["correcto"], N2["nota_arco"]["dif_m"],
            "N2: y lo que se separa de la geodésica", 1e-9)
    # (Δλ)²·sen²φ/24 · L, el término que separa el arco de la geodésica.
    prediccion = (math.radians(1) ** 2) * math.sin(phi) ** 2 / 24 * N2["correcto"]
    a.igual(prediccion, N2["nota_arco"]["dif_m"],
            "N2: la separación es la que predice la teoría", 5e-4)
    # EL RADIO DE s2, y por qué se comprueba: 6 371 008,8 es el radio medio
    # del WGS84 y es la respuesta que parece. La columna del capítulo solo
    # sale con 6 371 010,0. La comprobación no es de estilo: dos centímetros
    # por grado es lo que separa una cifra correcta de una plausible.
    lats = REU["grad_lat"]["valor"]
    col_esf = REU["grad_lon_esfera"]["valor"]
    err_s2 = max(abs(geo_esf.inv(0.0, la, 1.0, la)[2] - v)
                 for la, v in zip(lats, col_esf))
    otro = pyproj.Geod(a=RADIO_MEDIO_WGS84, f=0)
    err_medio = max(abs(otro.inv(0.0, la, 1.0, la)[2] - v)
                    for la, v in zip(lats, col_esf))
    a.cierto(err_s2 < 1e-6, "N2: el radio de s2 reproduce la columna «esfera»",
             f"{RADIO_S2:.1f} m, error máx {err_s2:.2e} m")
    a.cierto(err_medio > 1e-3, "N2: y el radio medio del WGS84 NO la reproduce",
             f"{RADIO_MEDIO_WGS84:.1f} m, error máx {err_medio:.4f} m")
    err_eli = max(abs(geo_eli.inv(0.0, la, 1.0, la)[2] - v)
                  for la, v in zip(lats, REU["grad_lon_elip"]["valor"]))
    a.cierto(err_eli < 1e-6, "N2: y pyproj reproduce la columna elipsoidal",
             f"error máx {err_eli:.2e} m")

    # --- N3 · el convenio del intervalo, contra el CSV y mapclassify --
    N3 = NUEVO["convenio_intervalo"]
    sid = pd.read_csv(SALIDAS / "cap3_nc.csv")["sid74"].to_numpy()
    a.igual(len(sid), N3["n"], "N3: los condados del CSV")
    cortes = [float(x) for x in N3["cortes"]]
    a.cierto(cortes == [float(x) for x in REU["c3m3_cortes"]["valor"]],
             "N3: los cortes son los del capítulo 3", str(cortes))
    k = len(cortes) - 1
    tam_r = [int(((sid >= cortes[i]) & (sid < cortes[i + 1])).sum()) if i < k - 1
             else int(((sid >= cortes[i]) & (sid <= cortes[i + 1])).sum())
             for i in range(k)]
    tam_py = [int((sid <= cortes[1]).sum()) if i == 0
              else int(((sid > cortes[i]) & (sid <= cortes[i + 1])).sum())
              for i in range(k)]
    a.cierto(tam_r == [int(x) for x in N3["tam_r"]],
             "N3: el reparto con [a, b), rehecho con numpy", str(tam_r))
    a.cierto(tam_py == [int(x) for x in N3["tam_python"]],
             "N3: el reparto con (a, b], rehecho con numpy", str(tam_py))
    # Y el camino de verdad independiente: el propio mapclassify, que es la
    # biblioteca cuyo convenio se está describiendo.
    q = mc.Quantiles(sid, k=k)
    a.cierto(list(np.bincount(q.yb, minlength=k)) == [int(x) for x in N3["tam_python"]],
             "N3: y mapclassify da ese mismo reparto",
             str(list(np.bincount(q.yb, minlength=k))))
    a.igual(tam_py[0] - tam_r[0], N3["movidos_primera"],
            "N3: los condados que mueve el convenio")
    a.igual(sum(tam_r), N3["n"], "N3: el reparto de R suma los condados")
    a.igual(sum(tam_py), N3["n"], "N3: y el de Python también")
    a.igual(int(np.isin(sid, cortes[1:-1]).sum()), REU["c3m3_empatados"]["valor"],
            "N3: los condados empatados justo en un corte")

    # --- N4 · euclídea sobre grados, con pyproj sobre las 361 ---------
    N4 = NUEVO["euclidea_grados"]
    est = pd.read_csv(SALIDAS / "cap2_estaciones.csv")
    a.igual(len(est), N4["n_estaciones"], "N4: las estaciones del CSV")
    # La fuente primaria es el GeoPackage; el CSV es su exportación
    # redondeada a dos decimales. Se ata el uno al otro fila a fila: sin
    # esto, el CSV podría haberse quedado atrás sin que nada lo dijera.
    gest = gpd.read_file(PROCESADO / "colombia_estaciones_clima.gpkg").to_crs(4326)
    a.igual(len(gest), N4["n_estaciones"], "N4: y las que trae el GeoPackage")
    a.cierto(np.allclose(est.lon.to_numpy(), gest.geometry.x.round(2).to_numpy())
             and np.allclose(est.lat.to_numpy(), gest.geometry.y.round(2).to_numpy()),
             "N4: el CSV es el GeoPackage redondeado, fila a fila")
    a.igual(REU["grad_lon_elip"]["valor"][0] / 1000, N4["km_por_grado"],
            "N4: los km por grado salen del propio capítulo", 1e-9)
    lon, lat_e = est.lon.to_numpy(), est.lat.to_numpy()
    iu = np.triu_indices(len(est), k=1)
    lo1, lo2 = lon[iu[0]], lon[iu[1]]
    la1, la2 = lat_e[iu[0]], lat_e[iu[1]]
    d_geo = geo_eli.inv(lo1, la1, lo2, la2)[2]
    d_ing = np.hypot(lo1 - lo2, la1 - la2) * N4["km_por_grado"] * 1000
    rel = (d_ing - d_geo) / d_geo * 100
    a.igual(len(rel), N4["n_pares"], "N4: los pares de estaciones")
    a.igual(len(est) * (len(est) - 1) // 2, N4["n_pares"], "N4: y son n(n-1)/2")
    a.igual(rel.mean(), N4["error_med_pct"], "N4: el error medio, con pyproj", 1e-8)
    peor = int(np.argmax(np.abs(rel)))
    a.igual(rel[peor], N4["error_max_pct"], "N4: el error del peor par", 1e-8)
    a.igual(rel.min(), N4["error_min_pct"], "N4: y el del mejor", 1e-8)
    a.igual((rel > 0).mean() * 100, N4["pct_sobreestima"],
            "N4: el % de pares en los que se pasa", 1e-9)
    a.cierto(N4["pct_sobreestima"] == 100,
             "N4: se pasa en TODOS, que es lo que el error afirma")
    a.igual(d_geo[peor] / 1000, N4["peor_par"]["d_geodesica_km"],
            "N4: la geodésica del peor par, en km", 1e-8)
    a.igual(d_ing[peor] / 1000, N4["peor_par"]["d_ingenua_km"],
            "N4: y lo que el método ingenuo le atribuye", 1e-8)
    a.igual(est["estacion"].to_numpy()[iu[0][peor]], N4["peor_par"]["a"],
            "N4: la primera estación del peor par")
    a.igual(est["estacion"].to_numpy()[iu[1][peor]], N4["peor_par"]["b"],
            "N4: y la segunda")

    # --- N5, N6, N8, N9 y los tres de N3 · los quince distractores que
    #     se calcularon para que las cinco numéricas pudieran viajar a un
    #     banco del LMS.
    #
    # La independencia aquí es MENOR que la de N1 a N4, y se dice: no salen
    # de la fuente primaria sino de cifras que este mismo auditor ya verificó
    # contra ella en la familia 2. Lo que se comprueba es la FÓRMULA —qué
    # error concreto produce cada número— y no el dato. Un distractor cuya
    # explicación no corresponda a su valor es peor que no tenerlo: manda al
    # estudiante a buscar un error que no cometió.
    v = lambda k: float(REU[k]["valor"])                        # noqa: E731
    ra, rb = v("cv_rmse_alea"), v("cv_rmse_bloques")
    pb, pc = v("ing_pares_bruta"), v("ing_pares_cajas")
    dn, dd = v("c3m5_dE_normal"), v("c3m5_dE_deuter")
    ri, rd, rmun = v("c3m8_r_ind"), v("c3m8_r_dep"), v("c3m8_r_mun")
    esperado = {
        "cv_inflacion": ((rb - ra) / ra * 100, {
            "base_bloques": (rb - ra) / rb * 100,
            "razon": rb / ra * 100,
            "cuadraticos": (rb ** 2 - ra ** 2) / ra ** 2 * 100}),
        "indice_espacial": (pb / pc, {
            "al_reves": pc / pb,
            "olvida_el_resto": (pb - pc) / pc,
            "pct_reduccion": (pb - pc) / pb * 100}),
        "caida_color": ((dn - dd) / dn * 100, {
            "lo_que_queda": dd / dn * 100,
            "diferencia": dn - dd,
            "base_deuteranopia": (dn - dd) / dd * 100}),
        "efecto_escala": ((rd - ri) / ri * 100, {
            "base_departamento": (rd - ri) / rd * 100,
            "razon": rd / ri * 100,
            "con_municipio": (rmun - ri) / ri * 100}),
        "convenio_intervalo": (None, {
            "ninguno": 0.0,
            "primera_clase_r": float(N3["primera_clase_r"]),
            "todos_los_empates": v("c3m3_empatados")}),
    }
    publica = {"cv_inflacion": "cv_inflacion", "indice_espacial": "ing_reduccion",
               "caida_color": "c3m5_caida", "efecto_escala": "c3m8_subida"}
    for nm, (correcto, ds) in esperado.items():
        bloque = NUEVO[nm]
        if correcto is not None:
            # 1e-6 y no 1e-9: los ingredientes se publican redondeados a diez
            # decimales por `r10()`, así que un porcentaje derivado de ellos
            # arrastra ~1e-9 por construcción. Apretar más no comprobaría la
            # fórmula, comprobaría el redondeo del capítulo. Es la misma
            # tolerancia que usa el ancla del generador.
            a.igual(correcto, bloque["correcto"],
                    f"{nm}: la respuesta sale de sus ingredientes", 1e-6)
            a.igual(bloque["correcto"], v(publica[nm]),
                    f"{nm}: y es la que publicaba el capítulo", 1e-6)
        tiene = {d["id"]: float(d["valor"]) for d in bloque["distractores"]}
        a.cierto(set(tiene) == set(ds), f"{nm}: los tres distractores que se esperan",
                 " · ".join(sorted(tiene)))
        for ident, valor in ds.items():
            a.igual(valor, tiene.get(ident, float("nan")),
                    f"{nm}: el distractor «{ident}»", 1e-9)

    # --- La separación de los distractores, que no es cosmética -------
    # Se recorre TODO lo que tenga distractores, y no una lista escrita a
    # mano: el día que se añada un ítem más, entra solo. Escribirla a mano
    # es como los quince distractores llegaron a publicarse sin que ninguna
    # comprobación los mirara.
    for nombre, bloque in sorted((k, x) for k, x in NUEVO.items()
                                 if x.get("distractores")):
        dec = int(bloque["decimales"])
        vistos = {round(float(bloque["correcto"]), dec): "el correcto"}
        choque = None
        for d in bloque["distractores"]:
            v = round(float(d["valor"]), dec)
            if v in vistos:
                choque = f"{d['id']} y {vistos[v]}"
            vistos[v] = d["id"]
        # El rótulo lleva PRESUPUESTO de 57 caracteres, y los decimales van
        # al detalle por eso: con ellos dentro, «convenio_intervalo» lo
        # pasaba a 64 y rompía el recuento de cobertura del arnés sin que
        # nada fallara. Es la CUARTA vez que este defecto vuelve; ver
        # `avisa_rotulos_largos()`.
        a.cierto(choque is None,
                 f"{nombre}: los distractores se distinguen",
                 f"a {dec} decimal(es)" + (f" · choca {choque}" if choque else ""))

    # =================================================================
    fam.abre(2, "Sincronía: las cifras citadas siguen siendo esas")
    dir_caps = pathlib.Path(os.environ.get("PREPARCIAL1_CAPS") or SALIDAS)
    if dir_caps != SALIDAS:
        print(f"  (los capítulos se leen de {dir_caps})")
    CAPS = {}
    for doc, archivo in (("cap1", "cap1_datos.json"), ("cap2", "cap2_datos.json"),
                         ("cap3", "cap3_datos.json")):
        ruta = dir_caps / archivo
        if not ruta.exists():
            sys.exit(f"PARADO: falta {ruta}")
        CAPS[archivo] = json.loads(ruta.read_text(encoding="utf-8"))
    ARCHIVO_DE = {"cap1": "cap1_datos.json", "cap2": "cap2_datos.json",
                  "cap3": "cap3_datos.json"}

    desincronizadas, ausentes, mal_doc, pies = [], [], [], []
    RELATIVO = re.compile(r"^(Lo mismo|La misma|El mismo|Los mismos|Ídem|Igual )")
    for clave, e in REU.items():
        origen, ruta, doc = e["origen"], e["ruta"], e["doc"]
        if ARCHIVO_DE.get(doc) != origen:
            mal_doc.append(f"{clave}: doc {doc} contra origen {origen}")
            continue
        v = en_ruta(CAPS[origen], ruta)
        if v is _AUSENTE:
            ausentes.append(f"{clave} -> {origen}:{ruta}")
            continue
        if isinstance(v, dict):
            v = len(v)
        if isinstance(v, list) and v and all(isinstance(x, dict) for x in v):
            v = len(v)
        pub = e["valor"]
        # El largo se comprueba ANTES de emparejar: `zip()` exige iterables
        # al construirse, así que con un vector convertido en escalar esto
        # reventaba con un TypeError en vez de informar del defecto.
        if isinstance(pub, list):
            if not isinstance(v, list) or len(v) != len(pub):
                desincronizadas.append(
                    f"{clave}: el vector del capítulo ya no tiene ese largo")
                continue
            pares = list(zip(v, pub))
        else:
            if isinstance(v, list):
                desincronizadas.append(f"{clave}: el capítulo devuelve un vector")
                continue
            pares = [(v, pub)]
        for x, y in pares:
            if isinstance(y, (int, float)) and not isinstance(y, bool):
                if not isinstance(x, (int, float)) or isinstance(x, bool):
                    desincronizadas.append(f"{clave}: dejó de ser un número")
                    break
                if abs(float(x) - float(y)) > 1e-9 * max(abs(float(y)), 1.0):
                    desincronizadas.append(
                        f"{clave} ({origen}:{ruta}): el capítulo dice "
                        f"{float(x):.10g} y el preparcial publica {float(y):.10g}")
                    break
            elif x != y:
                desincronizadas.append(
                    f"{clave} ({origen}:{ruta}): «{x}» contra «{y}»")
                break
        if not str(e["que"]).strip():
            pies.append(f"{clave}: sin pie")
        elif RELATIVO.match(str(e["que"])):
            pies.append(f"{clave}: pie relativo «{e['que']}»")
        elif str(e["que"]).startswith("%"):
            pies.append(f"{clave}: el pie empieza por la unidad")

    a.cierto(not mal_doc, f"las {len(REU)} reutilizadas declaran su capítulo",
             "; ".join(mal_doc[:2]))
    a.cierto(not ausentes, "todas las rutas siguen existiendo en su capítulo",
             "; ".join(ausentes[:2]))
    a.cierto(not desincronizadas, "y ninguna se ha desincronizado",
             "; ".join(desincronizadas[:2]))
    a.cierto(not pies, "cada cifra trae un pie que se basta solo",
             "; ".join(pies[:2]))
    fuera = sorted({f"{e['doc']}.m{e['modulo']}" for e in REU.values()} - ALC.CLAVES)
    a.cierto(not fuera, "ninguna cifra habla de un módulo fuera del alcance", str(fuera))
    sin_cifra = sorted(ALC.CLAVES - {f"{e['doc']}.m{e['modulo']}" for e in REU.values()})
    a.cierto(not sin_cifra, "y los 30 módulos tienen al menos una cifra", str(sin_cifra))

    # El segundo piso de la sincronía: el HTML publicado lleva su propia
    # copia del JSON. Regenerar el precálculo y no reensamblar deja las
    # preguntas citando cifras viejas con el JSON del disco ya corregido, y
    # eso es exactamente lo que pasó el 2026-08-25 (§12.4 del plan).
    m = re.search(r"\n    const DATOS_PRE1 = (\{.*?\});\n", html, re.S)
    if not m:
        a.cierto(False, "el HTML incrusta DATOS_PRE1")
    else:
        incrustado = json.loads(m.group(1))
        a.cierto(incrustado == D,
                 "el HTML lleva ESTE precálculo, no uno anterior",
                 _primera_diferencia(incrustado, D) or "")

    # Los gráficos: series del mismo largo y sacadas de su capítulo.
    for nm, g in GRAFICOS.items():
        series = {k: v for k, v in g.items() if isinstance(v, list)}
        n_dist = {len(v) for v in series.values()}
        a.cierto(len(n_dist) == 1 and series,
                 f"{nm}: sus series miden todas lo mismo",
                 f"{len(series)} series, largos {sorted(n_dist)}")
        a.cierto(g.get("modulo") in ALC.CLAVES,
                 f"{nm}: habla de un módulo del alcance", str(g.get("modulo")))
    a.cierto(GRAFICOS["g_grado"]["elipsoide"] == REU["grad_lon_elip"]["valor"]
             and GRAFICOS["g_grado"]["esfera"] == REU["grad_lon_esfera"]["valor"],
             "g_grado dibuja las dos columnas del capítulo 2")
    curva = en_ruta(CAPS["cap3_datos.json"], "m8.curva")
    a.cierto([c["media"] for c in curva] == GRAFICOS["g_escala"]["media"],
             "g_escala dibuja la curva del capítulo 3")
    pares4 = en_ruta(CAPS["cap3_datos.json"], "m4.pares")
    a.cierto([p["pct_cambian"] for p in pares4] == GRAFICOS["g_discordancia"]["pct"],
             "g_discordancia dibuja los pares del capítulo 3")

    # El catálogo de errores: cada uno dentro del alcance y con cifra.
    malos = []
    for e in ERRORES:
        if f"{e['doc']}.m{e['modulo']}" not in ALC.CLAVES:
            malos.append(f"{e['id']}: fuera del alcance")
        faltan = [c for c in (e["claves"] or []) if c not in REU]
        if faltan:
            malos.append(f"{e['id']}: cita {faltan}")
        for nv in e.get("nuevas") or []:
            if en_ruta(NUEVO, nv["ruta"]) is _AUSENTE:
                malos.append(f"{e['id']}: cita nuevo:{nv['ruta']}")
        if not (e["claves"] or e.get("nuevas")):
            malos.append(f"{e['id']}: sin ninguna cifra")
    a.cierto(not malos, f"los {len(ERRORES)} errores citan cifras que existen",
             "; ".join(malos[:2]))

    # =================================================================
    fam.abre(3, "Cobertura: los 30 módulos, y el repaso resuelto")
    quices = lee_autoevaluaciones(html)
    # El analizador, comprobado contra el mismo recuento que usa
    # `cuenta_sitio.py`: si se dejara una pregunta, el resto de las
    # familias saldría verde sobre una pregunta menos.
    total = sum(len(v) for v in quices.values())
    a.igual(total, len(re.findall(r"\n        tipo: ", html)),
            "el analizador no se deja ninguna pregunta")
    a.cierto(total > 0, f"hay {total} preguntas publicadas en "
                        f"{len(quices)} bloques")
    # En el MARCADO, no en el archivo entero: el motor de la plantilla
    # escribe `data-quiz="id"` dentro de un comentario de JavaScript, y
    # buscando por todo el HTML aparecía un cuestionario llamado «id».
    marcado = "".join(re.findall(r'<template id="module-.*?</template>', html, re.S))
    contenedores = set(re.findall(r'data-quiz="([^"]+)"', marcado))
    a.cierto(contenedores == set(quices),
             "cada cuestionario registrado tiene su contenedor",
             str(sorted(contenedores ^ set(quices))))

    RE_ETIQ = re.compile(r"^Cap\. (\d) · módulo (\d+) — (.+)$")
    TITULO = {(f["doc"], f["modulo"]): f["titulo"] for f in ALC.ALCANCE}
    tocados, sin_repaso, mal_etiqueta, mal_href, fuera_alcance = set(), [], [], [], []
    por_bloque = {}
    for clave, preguntas in quices.items():
        por_bloque[clave] = set()
        for i, q in enumerate(preguntas, 1):
            ref = f"{clave}#{i}"
            rep = q.get("repaso") or {}
            if not rep.get("etiqueta") or not rep.get("href"):
                sin_repaso.append(ref)
                continue
            m = RE_ETIQ.match(rep["etiqueta"])
            if not m:
                mal_etiqueta.append(f"{ref}: «{rep['etiqueta']}»")
                continue
            doc, modulo, titulo = f"cap{m.group(1)}", int(m.group(2)), m.group(3)
            if (doc, modulo) not in TITULO:
                fuera_alcance.append(f"{ref} -> {doc}.m{modulo}")
                continue
            if TITULO[(doc, modulo)] != titulo:
                mal_etiqueta.append(
                    f"{ref}: el capítulo lo llama «{TITULO[(doc, modulo)]}»")
            if rep["href"] != ALC.DOCS[doc]:
                mal_href.append(f"{ref}: {rep['href']}")
            tocados.add(f"{doc}.m{modulo}")
            por_bloque[clave].add((doc, modulo))

    a.cierto(not sin_repaso, "toda pregunta dice adónde volver", str(sin_repaso[:3]))
    a.cierto(not mal_etiqueta, "y el título que cita es el que publica el capítulo",
             "; ".join(mal_etiqueta[:2]))
    a.cierto(not mal_href, "y el enlace lleva a ese capítulo", "; ".join(mal_href[:2]))
    a.cierto(not fuera_alcance, "ninguna pregunta apunta fuera del alcance",
             str(fuera_alcance[:3]))
    a.cierto(tocados == ALC.CLAVES, f"los {len(ALC.CLAVES)} módulos tienen pregunta",
             str(sorted(ALC.CLAVES - tocados)))
    # Y el destino existe de verdad en el capítulo publicado: es lo que hará
    # que el enlace profundo de P0.2 tenga adonde llegar, y lo que caza que
    # un capítulo se quede sin el `<template>` de un módulo que sí declara.
    sin_plantilla = [c for c in sorted(tocados)
                     if not ALC.texto_modulo(c.split(".m")[0], int(c.split(".m")[1]))]
    a.cierto(not sin_plantilla, "y cada destino existe en su capítulo",
             str(sin_plantilla[:3]))

    # El contrato de cada bloque: A, B y C cubren su capítulo módulo a
    # módulo, y D cruza. Se comprueba así y no contando 11/11/8/6 porque el
    # reparto es una consecuencia, no el contrato.
    for clave, doc in (("bloque-a", "cap1"), ("bloque-b", "cap2"),
                       ("bloque-c", "cap3")):
        esperado = {(f["doc"], f["modulo"]) for f in ALC.ALCANCE if f["doc"] == doc}
        visto = por_bloque.get(clave, set())
        a.cierto(visto == esperado,
                 f"{clave} cubre su capítulo módulo a módulo",
                 str(sorted({f"{d}.m{m}" for d, m in visto ^ esperado})))
        a.igual(len(quices.get(clave, [])), len(esperado),
                f"{clave}: una pregunta por módulo, sin repetir")
    caps_d = {d for d, _ in por_bloque.get("bloque-d", set())}
    a.cierto(len(caps_d) >= 2, "el bloque D cruza capítulos de verdad",
             f"toca {sorted(caps_d)}")

    # =================================================================
    fam.abre(4, "Retroalimentación completa, y las correctas que toca")
    TIPOS = {"opcion", "multiple", "numerica", "grafico"}
    problemas = []
    for clave, preguntas in quices.items():
        vistos = {q.get("tipo") for q in preguntas}
        faltan = TIPOS - vistos
        a.cierto(not faltan, f"{clave} trae los cuatro tipos", str(sorted(faltan)))
        a.cierto(not (vistos - TIPOS), f"{clave} no inventa tipos",
                 str(sorted(vistos - TIPOS)))
        for i, q in enumerate(preguntas, 1):
            ref = f"{clave}#{i}"
            tipo = q.get("tipo")
            if not str(q.get("pista", "")).strip():
                problemas.append(f"{ref}: sin pista")
            if tipo == "grafico":
                if not str(q.get("descripcionGrafico", "")).strip():
                    problemas.append(f"{ref}: lienzo sin aria-label")
                if not q.get("dibujar"):
                    problemas.append(f"{ref}: sin función de dibujo")
                if not isinstance(q.get("alto"), (int, float)) or q["alto"] <= 0:
                    problemas.append(f"{ref}: sin alto de lienzo")
            if tipo == "numerica":
                if not isinstance(q.get("respuesta"), (int, float)):
                    problemas.append(f"{ref}: numérica sin respuesta")
                if not isinstance(q.get("tolerancia"), (int, float)) \
                        or q.get("tolerancia", 0) <= 0:
                    problemas.append(f"{ref}: numérica sin tolerancia positiva")
                if not str(q.get("retroFallo", "")).strip():
                    problemas.append(f"{ref}: numérica sin retroFallo")
                if q.get("opciones"):
                    problemas.append(f"{ref}: numérica con opciones")
                continue
            ops = q.get("opciones") or []
            if not ops:
                problemas.append(f"{ref}: sin opciones")
                continue
            correctas = [o for o in ops if o.get("correcta")]
            if tipo in ("opcion", "grafico") and len(correctas) != 1:
                problemas.append(f"{ref}: {len(correctas)} correctas, se esperaba 1")
            if tipo == "multiple":
                if len(correctas) < 2:
                    problemas.append(f"{ref}: «varias respuestas» con "
                                     f"{len(correctas)} correcta(s)")
                if len(correctas) == len(ops):
                    problemas.append(f"{ref}: todas las opciones son correctas")
                for extra in ("retroAcierto", "retroFallo"):
                    if not str(q.get(extra, "")).strip():
                        problemas.append(f"{ref}: multiple sin {extra}")
            retros, textos = [], []
            for j, o in enumerate(ops, 1):
                r = str(o.get("retro", "")).strip()
                if not r:
                    problemas.append(f"{ref} op{j}: sin retroalimentación")
                elif len(re.sub(r"<[^>]+>", "", r)) < 25:
                    # Una retro de dos palabras dice «incorrecto» con otras
                    # letras, y la regla del documento es que las incorrectas
                    # son las que enseñan.
                    problemas.append(f"{ref} op{j}: retroalimentación de "
                                     f"{len(r)} caracteres, no explica nada")
                retros.append(r)
                textos.append(str(o.get("texto", "")).strip())
            if len(set(retros)) != len(retros):
                problemas.append(f"{ref}: dos opciones comparten retroalimentación")
            if len(set(textos)) != len(textos):
                problemas.append(f"{ref}: dos opciones dicen lo mismo")
            if any(not t for t in textos):
                problemas.append(f"{ref}: alguna opción sin texto")
    a.cierto(not problemas, f"las {total} preguntas, opción por opción",
             f"{len(problemas)} problema(s): " + "; ".join(problemas[:3]))

    # =================================================================
    fam.abre(5, "No filtración: ni enunciado, ni pista, ni posición")
    filtra, posicional = [], []
    # «las dos primeras» SOLO cuando va sola —seguida de punto, coma o final
    # de frase— o cuando nombra opciones. «las dos primeras clases» y «la
    # primera banda de distancia» hablan del contenido, no del orden de las
    # opciones, y una guarda que las cazara obligaría a escribir peor.
    POSICIONALES = [re.compile(p, re.I) for p in (
        r"\blas (dos|tres|cuatro) primeras\s*(?:[.,;:)]|$)",
        r"\blas (dos|tres|cuatro) primeras (opciones|respuestas)\b",
        r"\bla (primera|segunda|tercera|cuarta|última) opción\b",
        r"\bla opción [a-d]\)",
    )]
    limpia = lambda t: re.sub(r"<[^>]+>", "", str(t)).strip(" .").lower()  # noqa: E731
    for clave, preguntas in quices.items():
        for i, q in enumerate(preguntas, 1):
            ref = f"{clave}#{i}"
            ops = q.get("opciones") or []
            enunciado = limpia(q.get("pregunta", ""))
            pista = limpia(q.get("pista", ""))
            for o in ops:
                if not o.get("correcta"):
                    continue
                t = limpia(o.get("texto", ""))
                if len(t) > 25 and t in enunciado:
                    filtra.append(f"{ref}: el enunciado copia la correcta")
                if len(t) > 25 and t in pista:
                    filtra.append(f"{ref}: la pista copia la correcta")
            for campo in ("pregunta", "pista", "retroAcierto", "retroFallo",
                          "descripcionGrafico"):
                texto = str(q.get(campo) or "")
                for pat in POSICIONALES:
                    if pat.search(texto):
                        posicional.append(f"{ref}.{campo}: «{pat.search(texto)[0]}»")
            for j, o in enumerate(ops, 1):
                for pat in POSICIONALES:
                    if pat.search(str(o.get("retro") or "")):
                        posicional.append(f"{ref} op{j}: «{pat.search(str(o['retro']))[0]}»")
    a.cierto(not filtra, "ningún enunciado ni pista regala su respuesta",
             "; ".join(filtra[:3]))
    a.cierto(not posicional, "ninguna retroalimentación nombra una posición",
             "; ".join(posicional[:3]))

    # LA FAMILIA QUE DESTAPÓ ESTE AUDITOR. Cada pregunta era impecable por
    # separado; juntas, la correcta caía la primera en las 29. Se mira sobre
    # el documento entero porque es la única escala en la que se ve.
    reparto = {}
    n_una = 0
    for preguntas in quices.values():
        for q in preguntas:
            ops = q.get("opciones") or []
            if not ops or q.get("tipo") == "multiple":
                continue
            n_una += 1
            pos = next((j for j, o in enumerate(ops, 1) if o.get("correcta")), 0)
            reparto[pos] = reparto.get(pos, 0) + 1
    if n_una:
        peor, veces = max(reparto.items(), key=lambda kv: kv[1])
        a.cierto(veces <= n_una * 0.5,
                 "la correcta no se concentra en una posición",
                 " · ".join(f"{k}: {v}" for k, v in sorted(reparto.items()))
                 + f"  (de {n_una})")
        a.cierto(len(reparto) >= 3, "y ocupa al menos tres posiciones distintas",
                 f"{len(reparto)} de las que hay")
    else:
        a.salta("el reparto de la respuesta correcta",
                "no hay ninguna pregunta de respuesta única publicada")

    fam.informe()
    return a.cierre()


if __name__ == "__main__":
    sys.exit(main())
