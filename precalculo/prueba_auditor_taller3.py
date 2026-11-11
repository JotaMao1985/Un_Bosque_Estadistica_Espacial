#!/usr/bin/env python3
"""
prueba_auditor_taller3.py — arnés de inyección del auditor del Taller 3

Material de Estadística Espacial 2026-II (20929). Ver PLAN_Taller_3_SIG.md.

Sin esto, `audita_taller3.py` es una opinión: unas dos mil comprobaciones en
verde no dicen nada si ninguna sabe ponerse en rojo. Aquí se envenena una
COPIA del JSON público, de las tres claves y de la página, un defecto cada
vez, y se comprueba que el auditor falla en todos y pasa sobre la copia sin
tocar. Los archivos de verdad no se tocan nunca: se mide su huella antes y
después.

LAS TRES REGLAS DE `prueba_auditor_base.py`, que aquí se heredan enteras:
  1. cada tanda empieza y acaba con un control sin inyectar;
  2. «N de N cazados» no basta: se cuenta cuántas comprobaciones DISTINTAS se
     han visto fallar, por TIPO y no por instancia;
  3. una mutación que no cambia el archivo es error del arnés.

LO PROPIO DE ESTE TALLER

  · Los defectos de las claves NO están escritos a mano uno a uno: se
    GENERAN. Se recorre la clave de QGIS, se agrupa cada hoja por su TIPO
    (la ruta con la localidad, NX, r y radio borrados) y se perturba una de
    cada tipo en un 1 %. Así, el día que `claves_qgis_taller3.py` publique
    una cifra nueva, el arnés la ataca sin que nadie se acuerde de venir
    aquí; y si el auditor no la lee, el arnés lo dice.

  · LO QUE UN 1 % NO PUEDE DETECTAR, DECLARADO. Tres cifras de la clave de R
    se auditan con una tolerancia ancha porque `density()` reparte los
    puntos en píxeles y no coincide con el estimador exacto:
    `pico_sin` y `pico_con` (5 %). Se perturban un 15 %. Y los coeficientes y
    los z de `ppm` no tienen implementación independiente (cabecera del
    auditor): solo se les exige ser números, así que se les inyecta un `null`
    y no un 1 %. Un 1 % sobre ellos pasaría el auditor, y es verdad.

  · SI FALTAN LAS CLAVES (clon limpio: `precalculo/cache/` no está en git) el
    arnés no se puede parar: ataca solo lo que el auditor sí audita sin ellas
    —el JSON público y la página— y lo dice. Un arnés que exigiera las claves
    pondría en rojo `audita_todo.sh` en cualquier máquina que no sea la de
    Javier.

  · EL AUDITOR PAGA ~10 s POR SU RECÁLCULO. El arnés le pasa una caché
    (`TALLER3_RECOMPUTO`) que lleva la huella de los datos y del propio
    auditor, así que no puede quedar obsoleta, y la borra al terminar.

Uso:  python3 precalculo/prueba_auditor_taller3.py   (desde `Estadistica espacial/`)
      Tarda un par de minutos. Devuelve 1 si algún defecto se escapa.
"""
from __future__ import annotations

import copy
import hashlib
import json
import os
import pathlib
import re
import shutil
import sys
import tempfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

RAIZ = pathlib.Path(__file__).resolve().parent.parent
PRECALCULO = RAIZ / "precalculo"
AUDITOR = PRECALCULO / "audita_taller3.py"

from prueba_auditor_base import arnes  # noqa: E402

REALES = {
    "datos": PRECALCULO / "salidas" / "taller3_datos.json",
    "mac": PRECALCULO / "cache" / "taller3_claves_qgis_mac.json",
    "linux": PRECALCULO / "cache" / "taller3_claves_qgis_linux.json",
    "r": PRECALCULO / "cache" / "taller3_claves_r.json",
    "html": RAIZ / "Htmls_Espacial" / "taller-3-sig-caps-1-5.html",
}
VARIABLES = {"datos": "TALLER3_DATOS", "mac": "TALLER3_CLAVES_MAC", "linux": "TALLER3_CLAVES_LINUX",
             "r": "TALLER3_CLAVES_R", "html": "TALLER3_HTML"}
PUBLICAS = ("datos", "html")

try:
    PY = json.loads((PRECALCULO / "versiones_py.json").read_text(encoding="utf-8"))["ejecutable"]
except (OSError, KeyError, json.JSONDecodeError):
    PY = sys.executable
if not pathlib.Path(PY).exists():
    PY = sys.executable

LOCALIDADES = ["Antonio Narino", "Barrios Unidos", "Bosa", "Chapinero", "Ciudad Bolivar", "Engativa",
               "Fontibon", "Kennedy", "La Candelaria", "Los Martires", "Puente Aranda",
               "Rafael Uribe Uribe", "San Cristobal", "Santa Fe", "Suba", "Sumapaz", "Teusaquillo",
               "Tunjuelito", "Usaquen", "Usme"]

# Las comprobaciones que este arnés NO PUEDE romper por construcción: no leen ni el JSON, ni
# las claves, ni la página que él envenena. Contrastan el recálculo del auditor contra lo que
# dicen los datos entregados (GeoPackage y GeoJSON, que el taller reparte y que no se mutan
# aquí: si cambiaran, las claves también serían de otros datos) o contra una constante.
INATACABLES = frozenset({
    "EPSG de las localidades",
    "EPSG del perímetro urbano",
    "EPSG de las sedes (a propósito, otro)",
    "localidades en el GeoPackage",
    "sedes en el GeoJSON",
    "polígonos en el perímetro urbano",
    "localidades que pasan el mínimo",
    # Las cuatro siguientes leen solo el recálculo: son propiedades de los datos que hacen
    # que las demás comparaciones tengan sentido.
    "ninguna sede reetiquetada cae en una localidad",
    "sin empates: los puestos no dependen del orden de capa",
    "ningún punto cae en una celda sin área",
    "la banda contiene a 0 en los 48 radios (plausible)",
})

# Lo que un defecto del 1 % no puede alcanzar y por qué (ver la cabecera).
FACTOR_ANCHO = {"pico_sin": 1.15, "pico_con": 1.15}
SOLO_NULO = {("ppm", "x"), ("ppm", "z_x"), ("ppm", "y"), ("ppm", "z_y")}


# =====================================================================
# Perturbaciones
# =====================================================================
def hojas(o, ruta=()):
    if isinstance(o, dict):
        for k, v in o.items():
            yield from hojas(v, ruta + (k,))
    else:
        yield ruta, o


def lleva(o, ruta):
    for k in ruta[:-1]:
        o = o[k]
    return o


def perturba(o, ruta, factor=1.01):
    """Cambia UNA hoja. Devuelve nada: la mutación se ve en el objeto."""
    padre, k = lleva(o, ruta), ruta[-1]
    v = padre[k]
    if isinstance(v, bool):
        padre[k] = not v
    elif isinstance(v, int):
        padre[k] = v + 1
    elif isinstance(v, float):
        padre[k] = v * factor if v != 0.0 else 0.01
    elif isinstance(v, str):
        padre[k] = v + "x"
    elif isinstance(v, list) and v and isinstance(v[0], (int, float)):
        v[0] = v[0] * factor
    elif isinstance(v, list):
        v.append("Kennedy")
    else:
        padre[k] = "?"


def plantilla(ruta):
    """El TIPO de una hoja: la ruta sin la localidad, NX, r ni radio."""
    r = list(ruta)
    if r[0] == "localidades" and len(r) > 1:
        r[1] = "L"
        if len(r) > 4 and r[2] in ("cuadrantes", "gf", "kl", "calor"):
            r[3] = "V"
    elif r[0] == "t2" and len(r) > 3 and r[1] == "rejillas":
        r[2] = "LADO"
    elif r[0] in LOCALIDADES:                         # la clave de R: localidad en la raíz
        r[0] = "L"
        if len(r) > 3 and r[1] == "calor":
            r[2] = "V"
    return "/".join(r)


def una_de_cada_tipo(clave):
    """[(tipo, ruta)] con la primera hoja de cada TIPO."""
    vistos = {}
    for ruta, _ in hojas(clave):
        if ruta[0] == "plataforma":
            continue
        vistos.setdefault(plantilla(ruta), ruta)
    return sorted(vistos.items())


def defectos(hay: dict) -> list[tuple[str, str, str, object]]:
    """(nombre, archivo, tipo, acción). tipo ∈ {'obj', 'txt'}."""
    D: list[tuple[str, str, str, object]] = []

    def obj(nombre, archivo, f):
        D.append((nombre, archivo, "obj", f))

    def txt(nombre, archivo, busca, pone):
        D.append((nombre, archivo, "txt", (busca, pone)))

    una = lambda o: next(iter(o["localidades"]))           # noqa: E731

    # --- 1. El JSON público ------------------------------------------
    obj("una variante apunta a una localidad que no es elegible", "datos",
        lambda o: o["variantes"][3].__setitem__("localidad", "Sumapaz"))
    obj("una variante apunta a una localidad inexistente", "datos",
        lambda o: o["variantes"][5].__setitem__("localidad", "Fusagasuga"))
    obj("una clave de variante se repite", "datos",
        lambda o: o["variantes"][500].__setitem__("clave", "499"))
    obj("dos claves se intercambian de sitio", "datos",
        lambda o: (o["variantes"][10].__setitem__("clave", "011"),
                   o["variantes"][11].__setitem__("clave", "010")))
    obj("faltan variantes", "datos", lambda o: o.__setitem__("variantes", o["variantes"][:999]))
    obj("sobra una variante", "datos",
        lambda o: o["variantes"].append(dict(o["variantes"][0], clave="1000")))
    obj("una variante trae un NX que nadie declaró", "datos",
        lambda o: o["variantes"][7].__setitem__("nx", 6))
    obj("una variante trae un radio de G y F que nadie declaró", "datos",
        lambda o: o["variantes"][8].__setitem__("r_gf", 175))
    obj("una variante trae un radio de L que nadie declaró", "datos",
        lambda o: o["variantes"][9].__setitem__("r_kl", 250))
    obj("una variante trae un radio de mapa de calor que nadie declaró", "datos",
        lambda o: o["variantes"][12].__setitem__("radio", 700))
    obj("un valor declarado llega como cadena, no como número", "datos",
        lambda o: o["variantes"][13].__setitem__("nx", "4"))
    obj("una variante publica un campo de más", "datos",
        lambda o: o["variantes"][14].__setitem__("indice", 0.85))
    obj("una variante deja de publicar un campo", "datos",
        lambda o: o["variantes"][15].pop("nx"))
    obj("todas las variantes reciben el mismo NX", "datos",
        lambda o: [v.__setitem__("nx", 3) for v in o["variantes"]])
    obj("todas las variantes reciben la misma combinación", "datos",
        lambda o: [v.update({"localidad": "Suba", "nx": 3, "r_gf": 100, "r_kl": 200, "radio": 600})
                   for v in o["variantes"]])
    obj("una localidad elegible se queda sin ninguna variante", "datos",
        lambda o: [v.__setitem__("localidad", "Suba") for v in o["variantes"]
                   if v["localidad"] == "Los Martires"])
    obj("el n de una localidad se mueve en uno", "datos",
        lambda o: o["localidades"]["Kennedy"].__setitem__("n", o["localidades"]["Kennedy"]["n"] + 1))
    obj("el área de una localidad se mueve un 1 %", "datos",
        lambda o: o["localidades"]["Suba"].__setitem__("area_km2", o["localidades"]["Suba"]["area_km2"] * 1.01))
    obj("lambda de una localidad se mueve un 1 %", "datos",
        lambda o: o["localidades"]["Bosa"].__setitem__("lambda", o["localidades"]["Bosa"]["lambda"] * 1.01))
    obj("desaparece una localidad elegible", "datos", lambda o: o["localidades"].pop("Los Martires"))
    obj("aparece una localidad que no llega al mínimo", "datos",
        lambda o: o["localidades"].__setitem__("Sumapaz", {"n": 23, "area_km2": 779.4695, "lambda": 0.0295}))
    obj("se renombra la clave de una localidad", "datos",
        lambda o: o["localidades"].__setitem__("Suba Norte", o["localidades"].pop("Suba")))
    obj("una localidad publica un campo de más, que es una respuesta", "datos",
        lambda o: o["localidades"][una(o)].__setitem__("chi2", 4.3106))
    obj("una localidad deja de publicar su lambda", "datos",
        lambda o: o["localidades"][una(o)].pop("lambda"))
    obj("aparece una sección más en la raíz", "datos",
        lambda o: o.__setitem__("soluciones", {"t1": "la caja"}))
    obj("desaparece una sección de la raíz", "datos", lambda o: o.pop("ciudad"))
    obj("«ciudad» publica un campo de más", "datos",
        lambda o: o["ciudad"].__setitem__("indice_medio", 1.2))
    obj("las opciones declaran un valor de más", "datos",
        lambda o: o["opciones"].__setitem__("nx", [3, 4, 5, 6]))
    obj("las opciones publican un conjunto de más", "datos",
        lambda o: o["opciones"].__setitem__("rmax", [600]))
    obj("la semilla de la envolvente cambia", "datos", lambda o: o.__setitem__("semilla", 2027))
    obj("el mínimo de sedes cambia", "datos", lambda o: o.__setitem__("n_min", 30))
    obj("el total de sedes cambia", "datos", lambda o: o["ciudad"].__setitem__("sedes", 2210))
    obj("el total dentro de alguna localidad cambia", "datos",
        lambda o: o["ciudad"].__setitem__("sedes_en_alguna_localidad", 2209))
    obj("el total de localidades cambia", "datos", lambda o: o["ciudad"].__setitem__("localidades", 21))
    obj("un campo de respuesta llega con punto", "datos",
        lambda o: o["localidades"][una(o)].__setitem__(".chi_pol", 12.3))
    obj("una palabra de respuesta se cuela en una sección", "datos",
        lambda o: o["ciudad"].__setitem__("nota", "la banda de la envolvente"))
    obj("un flotante con veinte decimales", "datos",
        lambda o: o["localidades"]["Usme"].__setitem__("lambda", 0.49851708946319384123))
    txt("un NaN se cuela en los datos", "datos", '"n":356', '"n":NaN')
    txt("mojibake UTF-8 en el JSON", "datos", "Usaquen", "Usaqu<c3><a9>n")
    txt("el JSON se corta y deja de poder leerse", "datos", '"semilla":2026,', '"semilla":2026,,')

    # --- 2. La página -------------------------------------------------
    txt("la página incrusta otra semilla", "html", '"semilla": 2026', '"semilla": 2027')
    txt("la página cambia una variante", "html",
        '{"clave": "000", "localidad": "Teusaquillo"', '{"clave": "000", "localidad": "Kennedy"')
    txt("la página cambia el n de una localidad", "html", '"Suba": {"n": 356', '"Suba": {"n": 357')
    txt("la página incrusta un campo de más", "html", '{"semilla": 2026,', '{"respuesta": 1, "semilla": 2026,')
    txt("la página declara DATOS_T3 dos veces", "html",
        "    const n5 = ", "    const DATOS_T3 = {};\n    const n5 = ")
    txt("la página deja de declarar DATOS_T3", "html", "const DATOS_T3 = ", "const DATOS_T4 = ")
    txt("la página nombra otra versión de QGIS", "html", "</body>", "<strong>QGIS 3.40.1</strong></body>")

    # --- 3. Las claves de QGIS ---------------------------------------
    # Estas se GENERAN. Un caso por TIPO de hoja, perturbado un 1 %: cada una es una cifra que
    # un estudiante podría escribir y un calificador comparar.
    if hay["mac"]:
        K = json.loads(REALES["mac"].read_text(encoding="utf-8"))
        for tipo, ruta in una_de_cada_tipo(K):
            obj(f"QGIS: se perturba {tipo}", "mac",
                (lambda r: lambda o: perturba(o, r))(ruta))
        obj("QGIS: desaparece una sección de una localidad", "mac",
            lambda o: o["localidades"]["Kennedy"].pop("gf"))
        obj("QGIS: desaparece un radio de lectura", "mac",
            lambda o: o["localidades"]["Kennedy"]["kl"].pop("300"))
        obj("QGIS: desaparece una localidad entera", "mac", lambda o: o["localidades"].pop("Bosa"))
        obj("QGIS: aparece una localidad que no existe", "mac",
            lambda o: o["localidades"].__setitem__("Fusagasuga", copy.deepcopy(o["localidades"]["Bosa"])))
        obj("QGIS: una localidad elegible se marca como no elegible", "mac",
            lambda o: o["localidades"]["Suba"].__setitem__("elegible", False))
        obj("QGIS: la versión de QGIS no es la del enunciado", "mac",
            lambda o: o["plataforma"].__setitem__("qgis", "3.40.1-Bratislava"))
        obj("QGIS: se pierde la sección T2 entera", "mac", lambda o: o.pop("t2"))
        obj("QGIS: se borra la versión de numpy", "mac", lambda o: o["plataforma"].pop("numpy"))
        # Los dos de Jenks son cortes que SON valores de los datos, así que ninguna de las otras
        # comprobaciones de la lista los ve por su cuenta: una cosa es que el corte exista y otra
        # que la partición sea buena, y otra que cierre en el máximo.
        obj("QGIS: Jenks pone los cuatro primeros datos como cortes", "mac",
            lambda o: o["t2"].__setitem__("cortes_jenks", sorted(
                v["densidad"] for v in o["localidades"].values())[:4]
                + [max(v["densidad"] for v in o["localidades"].values())]))
        obj("QGIS: el último corte de Jenks no es el máximo", "mac",
            lambda o: o["t2"]["cortes_jenks"].__setitem__(4, sorted(
                v["densidad"] for v in o["localidades"].values())[-2]))
        obj("QGIS: la clave se cuela como lista", "mac", lambda o: o["localidades"].__setitem__("Kennedy", []))
        obj("QGIS: un cuantil se aparta", "mac",
            lambda o: o["t2"]["cortes_cuantiles"].__setitem__(2, o["t2"]["cortes_cuantiles"][2] * 1.02))
        obj("QGIS: un corte de Jenks deja de ser un dato", "mac",
            lambda o: o["t2"]["cortes_jenks"].__setitem__(2, o["t2"]["cortes_jenks"][2] * 1.02))
        obj("QGIS: la lista de los que cambian de clase pierde uno", "mac",
            lambda o: o["t2"]["cambian_de_clase"].pop())
        obj("QGIS: el pico del mapa de calor sube un 1 % solo", "mac",
            lambda o: o["localidades"]["Usme"]["calor"]["800"].__setitem__(
                "maximo", o["localidades"]["Usme"]["calor"]["800"]["maximo"] * 1.01))
        obj("QGIS: la masa dentro baja un 1 % sin tocar la suma", "mac",
            lambda o: o["localidades"]["Teusaquillo"]["calor"]["600"].__setitem__(
                "masa_dentro", o["localidades"]["Teusaquillo"]["calor"]["600"]["masa_dentro"] * 0.99))
        obj("QGIS: el p bilateral se pone en la cola derecha", "mac",
            lambda o: o["localidades"]["Kennedy"]["cuadrantes"]["4"].__setitem__(
                "p_bilateral", o["localidades"]["Kennedy"]["cuadrantes"]["4"]["p_derecha"]))

    # --- 4. La otra plataforma ---------------------------------------
    if hay["linux"]:
        K = json.loads(REALES["linux"].read_text(encoding="utf-8"))
        for tipo, ruta in una_de_cada_tipo(K)[::9]:
            obj(f"Linux: se perturba {tipo}", "linux",
                (lambda r: lambda o: perturba(o, r))(ruta))
        obj("Linux: desaparece una localidad", "linux", lambda o: o["localidades"].pop("Fontibon"))
        obj("Linux: una cifra cambia en la décima cifra", "linux",
            lambda o: o["localidades"]["Kennedy"]["kl"]["300"].__setitem__(
                "k", o["localidades"]["Kennedy"]["kl"]["300"]["k"] * (1 + 1e-7)))

    # --- 5. La clave de R --------------------------------------------
    if hay["r"]:
        K = json.loads(REALES["r"].read_text(encoding="utf-8"))
        for tipo, ruta in una_de_cada_tipo(K):
            cola = tuple(ruta[-2:]) if len(ruta) >= 2 else ()
            if cola in SOLO_NULO:
                obj(f"R: se anula {tipo}", "r", (lambda r: lambda o: lleva(o, r).__setitem__(r[-1], None))(ruta))
            else:
                f = FACTOR_ANCHO.get(ruta[-1], 1.01)
                obj(f"R: se perturba {tipo}" + (f" un {round((f - 1) * 100)} %" if f != 1.01 else ""), "r",
                    (lambda r, f_: lambda o: perturba(o, r, f_))(ruta, f))
        obj("R: desaparece una localidad", "r", lambda o: o.pop("Bosa"))
        obj("R: aparece una localidad que no es elegible", "r",
            lambda o: o.__setitem__("Sumapaz", copy.deepcopy(o["Bosa"])))
        obj("R: un selector de ancho de banda sale negativo", "r",
            lambda o: o["Kennedy"].__setitem__("bw_ppl", -o["Kennedy"]["bw_ppl"]))
        obj("R: bw.ppl topa con el límite de su rejilla", "r",
            lambda o: o["Suba"].__setitem__("ppl_en_el_limite", True))
        obj("R: el sigma de un radio sale de otra fórmula", "r",
            lambda o: o["Kennedy"]["calor"]["800"].__setitem__("sigma", 800 / 4))
        obj("R: la masa sin borde se aparta un 1 %", "r",
            lambda o: o["Kennedy"]["calor"]["600"].__setitem__(
                "masa_sin", o["Kennedy"]["calor"]["600"]["masa_sin"] * 1.01))

    return D


def main() -> int:
    hay = {k: p.exists() for k, p in REALES.items()}
    faltan_publicas = [k for k in PUBLICAS if not hay[k]]
    if faltan_publicas:
        print(f"PARADO: faltan archivos públicos {[REALES[k].name for k in faltan_publicas]}. "
              f"Ejecuta antes precalculo/rscript.sh precalculo/genera_taller3.R y "
              f"python3 precalculo/ensambla_taller3.py")
        return 1
    parcial = not all(hay.values())
    lista = defectos(hay)
    if parcial:
        lista = [d for d in lista if d[1] in PUBLICAS]
        ausentes = [REALES[k].name for k in ("mac", "linux", "r") if not hay[k]]
        print("=" * 66)
        print("  ARNÉS PARCIAL — SALTADO: faltan las claves en precalculo/cache/")
        print(f"  ({', '.join(ausentes)}; no están en git, son las respuestas).")
        print(f"  Se atacan solo el JSON público y la página: {len(lista)} defectos.")
        print("  Esto NO es el arnés completo.")
        print("=" * 66)

    archivos = {k: (VARIABLES[k], REALES[k].name) for k in REALES if hay[k]}
    huella = {k: hashlib.sha256(REALES[k].read_bytes()).hexdigest() for k in archivos}
    tmp = pathlib.Path(tempfile.mkdtemp(prefix="arnes3_"))
    stage = tmp / "copias"
    stage.mkdir()
    for k in archivos:
        shutil.copy(REALES[k], stage / REALES[k].name)
    os.environ["TALLER3_RECOMPUTO"] = str(tmp / "recomputo.json")
    # Las variables que apuntan a claves AUSENTES no se tocan: el auditor las ve ausentes.
    for k in ("mac", "linux", "r"):
        if not hay[k]:
            os.environ[VARIABLES[k]] = str(tmp / "no_existe" / REALES[k].name)

    def tipo(n: str) -> str:
        """Colapsa las instancias de un mismo mecanismo en un solo nombre."""
        n = re.sub(r"^(?:%s): " % "|".join(map(re.escape, LOCALIDADES)), "LOCALIDAD: ", n)
        n = re.sub(r"cuadrantes \dx\d", "cuadrantes NxN", n)
        n = re.sub(r"\(r=\d+\)", "(r=N)", n)
        n = re.sub(r"\b(calor|R) \d+:", r"\1 N:", n)
        n = re.sub(r"rejilla \d+:", "rejilla N:", n)
        n = re.sub(r"corte \d de cuantiles", "corte N de cuantiles", n)
        n = re.sub(r"«[^»]*»", "«X»", n)
        n = re.sub(r"^(nx|r_gf|r_kl|radio): ", "CAMPO: ", n)
        n = re.sub(r"^(claves_qgis|genera_taller3\.R): (NX|R_GF|R_KL|RADIOS) ", r"\1: V ", n)
        n = re.sub(r"la clave de (macOS|Linux) es de QGIS \S+", "la clave de X es de QGIS V", n)
        return n.strip()

    try:
        rc = arnes(
            titulo=f"Arnés del auditor del Taller 3 · {len(lista)} inyecciones",
            py=PY, auditor=AUDITOR, salidas=stage, archivos=archivos, lista=lista,
            pista_generadores="precalculo/rscript.sh precalculo/genera_taller3.R",
            agrupa=tipo, inatacables=INATACABLES)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
        for k in ("mac", "linux", "r"):
            os.environ.pop(VARIABLES[k], None)
        os.environ.pop("TALLER3_RECOMPUTO", None)

    # `arnes` mide la copia; esto mide los archivos de verdad.
    intactos = all(hashlib.sha256(REALES[k].read_bytes()).hexdigest() == huella[k] for k in archivos)
    print(f"  {'OK ' if intactos else 'MAL'}  los archivos REALES (JSON, claves y página) siguen byte a byte igual")
    if parcial:
        print("\n  SALTADO: el arnés de las claves. Corre en una máquina que tenga precalculo/cache/.")
    return 1 if (rc or not intactos) else 0


if __name__ == "__main__":
    sys.exit(main())
