#!/usr/bin/env python3
"""
prueba_auditor_cap6.py — le rompe el precálculo al auditor y exige que lo cace

Material de Estadística Espacial 2026-II (20929). T4.1b.

POR QUÉ EXISTE. Un auditor que informa «0 fallos» la primera vez no ha
demostrado nada: puede estar comprobando bien o puede estar comprobando
cosas incapaces de fallar. `audita_cap6.py` dio **207/0 en su primera
pasada**, y esa cifra no es la que vale: lo que vale es que en esa misma
pasada **cazó un defecto real del núcleo compartido** —`geo_grafo_multi`
perdía aristas en toda vecindad asimétrica— que llevaba latente desde
T0.3 porque ningún capítulo anterior publicó un grafo asimétrico.

La maquinaria vive en `prueba_auditor_base.py`. Aquí solo se declara QUÉ
romper, que es lo único propio del capítulo.

LAS FAMILIAS DE DEFECTO, y cada una imita algo que este capítulo puede
sufrir de verdad:

   1. cifra que deja de cuadrar con la fuente primaria (el dato leído)
   2. cifra derivada que deja de cuadrar con las que la generan
   3. ENLACES CONTRA PAREJAS                          ← el defecto propio
      de este capítulo: en una vecindad asimétrica no son el doble uno del
      otro, y la primera versión del generador publicaba «73,5 aristas»
   4. la simetría declarada que no es la que el grafo tiene
   5. islas y componentes: quitar islas NO conecta el grafo
   6. el anidamiento geométrico roto (relativa ⊆ Gabriel ⊆ Delaunay)
   7. un estilo de peso mal escalado — B, W, S, C y U por separado
   8. el rezago, su correlación y su contracción
   9. la identidad D⁻¹A = W, que es la conexión con las GNN
  10. caja, cuantización o contenido de un `.geomapa`
  11. las aristas del mapa que dejan de ser las parejas del módulo
  12. tilde convertida en bytes crudos
  13. flotante con más decimales de los declarados
  14. metainformación que deja de decir la verdad

UNA INYECCIÓN NO PUEDE USAR UN VALOR QUE YA ESTÉ EN EL ARCHIVO. Si la
cifra falsa coincidiera con otra real, el auditor podría «cazarla» por el
motivo equivocado y el arnés se felicitaría solo. De ahí los valores con
pinta de matrícula.

Uso:  python3 precalculo/prueba_auditor_cap6.py
Devuelve 1 si algún defecto se cuela.
"""
from __future__ import annotations

import json
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from prueba_auditor_base import arnes                       # noqa: E402

RAIZ = pathlib.Path(__file__).resolve().parent.parent
PRECALCULO = RAIZ / "precalculo"
SALIDAS = PRECALCULO / "salidas"
AUDITOR = PRECALCULO / "audita_cap6.py"

ARCHIVOS = {
    "datos": ("CAP6_DATOS", "cap6_datos.json"),
    "mapas": ("CAP6_MAPAS", "cap6_mapas.json"),
}

PY = json.loads((PRECALCULO / "versiones_py.json").read_text(
    encoding="utf-8"))["ejecutable"]


def crit(d, ident):
    """El criterio `ident` del módulo 2, que es una lista y no un dict."""
    return next(c for c in d["m2"]["criterios"] if c["id"] == ident)


def defectos():
    """(nombre, archivo, tipo, acción). tipo ∈ {'obj', 'txt'}."""
    D = []

    def obj(nombre, clave, fn):
        D.append((nombre, clave, "obj", fn))

    def txt(nombre, clave, busca, pone):
        D.append((nombre, clave, "txt", (busca, pone)))

    # --- 1. Contra la fuente primaria ---------------------------------
    obj("1 · los barrios de Columbus dejan de ser 49",
        "datos", lambda d: d["m1"]["columbus"].__setitem__("n", 47))
    obj("1 · la media de CRIME cambia",
        "datos", lambda d: d["m1"]["columbus"]["variables"]["crime"].__setitem__(
            "media", 37.1717171717))
    obj("1 · la desviación de CRIME cambia",
        "datos", lambda d: d["m1"]["columbus"]["variables"]["crime"].__setitem__(
            "sd", 17.1313131313))
    obj("1 · los municipios dejan de ser 1 122",
        "datos", lambda d: d["m1"]["municipios"].__setitem__("n", 1131))
    obj("1 · los municipios con dato cambian",
        "datos", lambda d: d["m1"]["municipios"].__setitem__("con_dato", 1113))
    obj("1 · la media de deserción cambia",
        "datos", lambda d: d["m1"]["municipios"]["desercion"].__setitem__(
            "media", 3.1717171717))
    obj("1 · los ceros exactos de deserción cambian",
        "datos", lambda d: d["m1"]["municipios"]["desercion"].__setitem__("ceros", 13))

    # --- 2. Las diez W, contra libpysal -------------------------------
    obj("2 · la reina de Columbus pierde parejas",
        "datos", lambda d: crit(d, "reina").__setitem__("pares", 113))
    obj("2 · la reina de Columbus cambia de grado",
        "datos", lambda d: crit(d, "reina").__setitem__("grado", 4.7131))
    obj("2 · la torre de Columbus pierde parejas",
        "datos", lambda d: crit(d, "torre").__setitem__("pares", 97))
    obj("2 · Delaunay cambia de tamaño",
        "datos", lambda d: crit(d, "delaunay").__setitem__("pares", 131))
    obj("2 · Gabriel cambia de tamaño",
        "datos", lambda d: crit(d, "gabriel").__setitem__("pares", 87))
    obj("2 · el umbral sin islas de Columbus cambia",
        "datos", lambda d: d["m2"].__setitem__("umbral_sin_islas_m", 0.7131313131))

    # --- 3. Enlaces contra parejas (el defecto propio) ----------------
    obj("3 · k3 dice que sus enlaces son sus parejas",
        "datos", lambda d: crit(d, "k3").__setitem__("enlaces", crit(d, "k3")["pares"]))
    obj("3 · k1 duplica sus parejas como si fuera simétrica",
        "datos", lambda d: crit(d, "k1").__setitem__(
            "pares", crit(d, "k1")["enlaces"] // 2))
    obj("3 · k6 pierde enlaces dirigidos",
        "datos", lambda d: crit(d, "k6").__setitem__("enlaces", 287))

    # --- 4. La simetría declarada -------------------------------------
    obj("4 · k3 se declara simétrica",
        "datos", lambda d: crit(d, "k3").__setitem__("simetrica", True))
    obj("4 · los pares asimétricos de k=4 cambian",
        "datos", lambda d: d["m4"]["columbus"][3].__setitem__("asimetricos", 71))
    obj("4 · una k deja de dar grado k",
        "datos", lambda d: d["m4"]["columbus"][2].__setitem__("grado", 3.7131))
    obj("4 · la esfera se declara asimétrica",
        "datos", lambda d: crit(d, "esfera").__setitem__("simetrica", False))

    # --- 5. Islas y componentes ---------------------------------------
    obj("5 · las islas municipales dejan de ser dos",
        "datos", lambda d: d["m9"].__setitem__("islas", 4))
    obj("5 · los subgrafos municipales cambian",
        "datos", lambda d: d["m9"].__setitem__("subgrafos", 7))
    obj("5 · el subgrafo mayor cambia de tamaño",
        "datos", lambda d: d["m9"]["tamanos_subgrafo"].__setitem__(0, 1013))
    obj("5 · las islas cambian de nombre",
        "datos", lambda d: d["m9"].__setitem__("islas_nombre", ["Leticia", "Mitú"]))
    obj("5 · el umbral municipal se queda sin islas y conexo",
        "datos", lambda d: d["m5"]["municipios"]["en_el_umbral"].__setitem__(
            "subgrafos", 1))
    obj("5 · el umbral municipal deja islas",
        "datos", lambda d: d["m5"]["municipios"]["en_el_umbral"].__setitem__("islas", 3))
    obj("5 · el grado del umbral municipal se vuelve razonable",
        "datos", lambda d: d["m5"]["municipios"]["en_el_umbral"].__setitem__(
            "grado", 7.1313))
    obj("5 · la curva de Columbus pierde una isla",
        "datos", lambda d: d["m5"]["columbus"]["curva"][0].__setitem__("islas", 17))
    obj("5 · el umbral mayor de Columbus deja una isla",
        "datos", lambda d: d["m5"]["columbus"]["curva"][-1].__setitem__("islas", 3))
    obj("6 · la esfera se sale del rango entre Gabriel y Delaunay",
        "datos", lambda d: crit(d, "esfera").__setitem__("pares", 171))
    obj("10 · el mapa de Columbus cambia de modo",
        "mapas", lambda m: m["cap6-w"].__setitem__("modo", "puntos"))
    obj("5 · el error de R deja de mencionar zero.policy",
        "datos", lambda d: d["m9"].__setitem__(
            "error_sin_zero_policy", "Empty neighbour sets found"))
    obj("5 · el rezago de una isla deja de ser cero",
        "datos", lambda d: d["m9"].__setitem__("lag_isla", 3.1313))

    # --- 6. El anidamiento geométrico ---------------------------------
    obj("6 · la relativa deja de estar en Gabriel",
        "datos", lambda d: d["m6"]["anidamiento"].__setitem__("relativa_en_gabriel", False))
    obj("6 · Gabriel deja de estar en Delaunay",
        "datos", lambda d: d["m6"]["anidamiento"].__setitem__("gabriel_en_delaunay", False))
    obj("6 · la vecindad relativa cambia de tamaño",
        "datos", lambda d: next(
            g for g in d["m6"]["columbus"] if g["id"] == "relativa").__setitem__("pares", 71))

    # --- 7. Los cinco estilos -----------------------------------------
    for e, falso in (("B", 231.0), ("W", 47.0), ("S", 51.0), ("C", 53.0), ("U", 1.7131)):
        obj(f"7 · el estilo {e} deja de sumar lo suyo",
            "datos", lambda d, e=e, f=falso: next(
                x for x in d["m7"]["estilos"] if x["id"] == e).__setitem__("suma_total", f))
    obj("7 · el peso de la unidad grande en W cambia",
        "datos", lambda d: next(
            x for x in d["m7"]["estilos"] if x["id"] == "W").__setitem__("peso_max", 0.1313))
    obj("7 · la unidad de más vecinos cambia de grado",
        "datos", lambda d: d["m7"]["unidad_max"].__setitem__("grado", 13))
    obj("7 · la correlación del rezago con CRIME cambia",
        "datos", lambda d: next(
            x for x in d["m7"]["estilos"] if x["id"] == "W").__setitem__(
                "cor_con_crime", 0.7131))

    # --- 8. El rezago sobre la deserción ------------------------------
    obj("8 · la correlación entre y y su rezago cambia",
        "datos", lambda d: d["m10"].__setitem__("correlacion", 0.7131))
    obj("8 · la desviación del rezago cambia",
        "datos", lambda d: d["m10"]["wy"].__setitem__("sd", 1.7131))
    obj("8 · la contracción cambia",
        "datos", lambda d: d["m10"].__setitem__("contraccion_pct", 17.1313))
    obj("8 · el rezago deja de contraer",
        "datos", lambda d: d["m10"].__setitem__("contraccion_pct", -13.1313))
    obj("8 · los municipios con dato del rezago cambian",
        "datos", lambda d: d["m10"].__setitem__("n", 1013))

    # --- 9. W como matriz ---------------------------------------------
    obj("9 · las casillas ocupadas de Columbus cambian",
        "datos", lambda d: d["m11"]["columbus"].__setitem__("no_ceros", 231))
    obj("9 · la densidad de Columbus cambia",
        "datos", lambda d: d["m11"]["columbus"].__setitem__("densidad_pct", 13.1313))
    obj("9 · D⁻¹A deja de ser la estandarizada por filas",
        "datos", lambda d: d["m11"]["columbus"].__setitem__("d_inv_a_igual_w", 0.1313))
    obj("9 · el rezago deja de ser el producto por W",
        "datos", lambda d: d["m11"]["columbus"].__setitem__("lag_es_producto", 0.1717))
    obj("9 · la matriz municipal deja de ser dispersa",
        "datos", lambda d: d["m11"]["municipios"].__setitem__("densidad_pct", 3.1313))
    obj("9 · las casillas ocupadas municipales cambian",
        "datos", lambda d: d["m11"]["municipios"].__setitem__("no_ceros", 6131))

    # --- 10 y 11. Los mapas -------------------------------------------
    obj("10 · la caja del mapa de Columbus se desordena",
        "mapas", lambda m: m["cap6-w"].__setitem__(
            "caja", [m["cap6-w"]["caja"][2], m["cap6-w"]["caja"][1],
                     m["cap6-w"]["caja"][0], m["cap6-w"]["caja"][3]]))
    obj("10 · la cuantización del mapa cambia",
        "mapas", lambda m: m["cap6-w"].__setitem__("q", 1313))
    obj("10 · el mapa municipal cambia de modo",
        "mapas", lambda m: m["cap6-municipios"].__setitem__("modo", "poligonos"))
    obj("11 · una variante del mapa pierde aristas",
        "mapas", lambda m: m["cap6-w"]["variantes"]["reina"].__setitem__("n_aristas", 113))
    obj("11 · una variante del mapa gana islas",
        "mapas", lambda m: m["cap6-w"]["variantes"]["d_mitad"].__setitem__("islas", 17))
    obj("11 · el mapa se queda sin una de las diez variantes",
        "mapas", lambda m: m["cap6-w"]["variantes"].pop("esfera"))

    # --- Los mecanismos que la primera tanda dejó sin atacar ----------
    obj("2 · las islas de un criterio cambian",
        "datos", lambda d: crit(d, "d_mitad").__setitem__("islas", 17))
    obj("2 · los subgrafos de un criterio cambian",
        "datos", lambda d: crit(d, "k1").__setitem__("subgrafos", 7))
    obj("4 · una k se declara simétrica en el módulo 4",
        "datos", lambda d: d["m4"]["columbus"][2].__setitem__("simetrica", True))
    obj("5 · las parejas de un umbral cambian",
        "datos", lambda d: d["m5"]["columbus"]["curva"][1].__setitem__("pares", 71))
    obj("6 · Delaunay cambia de tamaño en el módulo 6",
        "datos", lambda d: next(
            g for g in d["m6"]["columbus"] if g["id"] == "delaunay").__setitem__("pares", 171))
    obj("6 · Gabriel cambia de tamaño en el módulo 6",
        "datos", lambda d: next(
            g for g in d["m6"]["columbus"] if g["id"] == "gabriel").__setitem__("pares", 71))
    obj("7 · la media del rezago de un estilo cambia",
        "datos", lambda d: next(
            x for x in d["m7"]["estilos"] if x["id"] == "W").__setitem__("lag_medio", 37.1313))
    obj("7 · la unidad de menos vecinos cambia de grado",
        "datos", lambda d: d["m7"]["unidad_min"].__setitem__("grado", 7))
    obj("8 · las dos vías dejan de contar lo mismo",
        "datos", lambda d: d["m8"].__setitem__("n_pares_sfdep", 113))
    obj("8 · el rezago de las dos vías deja de coincidir",
        "datos", lambda d: d["m8"].__setitem__("dif_max", 0.1313))
    obj("8 · spdep deja de coincidir con libpysal",
        "datos", lambda d: d["m8"].__setitem__("n_pares_spdep", 117) or
                           d["m8"].__setitem__("n_pares_sfdep", 117))
    obj("8 · las islas del subconjunto del rezago cambian",
        "datos", lambda d: d["m10"].__setitem__("islas_en_el_subconjunto", 7))
    obj("3 · las parejas que solo tiene la reina cambian",
        "datos", lambda d: d["m3"].__setitem__("solo_reina", 13))
    obj("5 · el umbral municipal se declara conexo",
        "datos", lambda d: d["m5"]["municipios"]["en_el_umbral"].__setitem__("subgrafos", 1))
    obj("10 · el mapa municipal desaparece del JSON",
        "mapas", lambda m: m.pop("cap6-municipios"))
    obj("10 · el modo de un mapa deja de ser de los cinco",
        "mapas", lambda m: m["cap6-w"].__setitem__("modo", "grafito"))
    obj("10 · la codificación de un mapa no va declarada",
        "mapas", lambda m: m["cap6-w"].__setitem__("codificacion", "cruda"))
    obj("10 · la q de un mapa se infla",
        "mapas", lambda m: m["cap6-w"].__setitem__("q", m["cap6-w"]["q"] * 4))

    obj("10 · el mapa se sale del presupuesto de KB",
        "mapas", lambda m: m["cap6-w"].__setitem__("relleno", "x" * 500_000))
    obj("5 · el umbral de Columbus queda sin islas y conexo",
        "datos", lambda d: [c.__setitem__("subgrafos", 1)
                            for c in d["m5"]["columbus"]["curva"] if c["islas"] == 0])

    # --- 12, 13 y 14. Formato y metainformación -----------------------
    txt("12 · una tilde se convierte en bytes crudos",
        "datos", "ó", "Ã³")
    obj("13 · un flotante pasa de diez decimales",
        "datos", lambda d: d["m10"].__setitem__("correlacion", 0.56771313131313131))
    obj("14 · la metainformación cambia de capítulo",
        "datos", lambda d: d["meta"].__setitem__("capitulo", 7))
    obj("14 · la metainformación cambia de semanas",
        "datos", lambda d: d["meta"].__setitem__("semanas", "12-13"))
    obj("14 · el generador dice que no comprobó anclas",
        "datos", lambda d: d["meta"].__setitem__("anclas", 0))

    return D


def tipo_de(nombre: str) -> str:
    """Colapsa las instancias de un mismo mecanismo en un solo nombre.

    Este capítulo mira DIEZ criterios de vecindad con las mismas seis
    preguntas, así que sin esto el informe tendría sesenta «tipos» que son
    seis mecanismos. Atacar `d_conexo: parejas` prueba exactamente lo mismo
    que atacar `reina: parejas`: que el auditor recalcula las parejas.

    Lo que NO se colapsa son cosas distintas con nombre parecido: las
    parejas y los enlaces son dos mecanismos, y confundirlos es el defecto
    que este capítulo tuvo.
    """
    CRIT = ("reina|torre|k1|k3|k6|k=\\d+|d_mitad|d_conexo|delaunay|gabriel|"
            "relativa|esfera|municipios reina")
    reglas = [
        (rf"^({CRIT}): parejas distintas$",            "2 · las parejas de un criterio"),
        (rf"^({CRIT}): parejas \\(libpysal\\)$",         "6 · las parejas de una geométrica"),
        (rf"^({CRIT}): parejas$",                      "2 · las parejas de un criterio"),
        (rf"^({CRIT}): enlaces dirigidos$",            "2 · los enlaces de un criterio"),
        (rf"^({CRIT}): grado medio$",                  "2 · el grado de un criterio"),
        (rf"^({CRIT}): islas$",                        "2 · las islas de un criterio"),
        (rf"^({CRIT}): subgrafos$",                    "2 · los subgrafos de un criterio"),
        (rf"^({CRIT}): la simetría publicada es la real$", "4 · la simetría de un criterio"),
        (r"^k=\d+: el grado es exactamente k$",        "4 · el grado vale k"),
        (r"^k=\d+: pares asimétricos$",                "4 · los pares asimétricos"),
        (r"^k=\d+: se publica como asimétrica$",       "4 · la asimetría declarada"),
        (r"^umbral [\d.]+: parejas$",                  "5 · las parejas de un umbral"),
        (r"^umbral [\d.]+: islas$",                    "5 · las islas de un umbral"),
        (r"^deserción: (media|desviación|máximo|ceros exactos)$",
         "1 · un estadístico de la deserción"),
        (r"^Columbus: (media|desviación) de CRIME$",   "1 · un estadístico de CRIME"),
        (r"^estilo [BWSCU]: (.+)$",                    r"7 · \1, de un estilo"),
        (r"^mapa (.+): sus aristas son las parejas$",  "11 · las aristas de una variante"),
        (r"^mapa (.+): sus islas$",                    "11 · las islas de una variante"),
        (r"^cap6-[a-z]+: (.+)$",                       r"10 · \1, de un mapa"),
        (r"^Anselin: (.+)$",                           "2 · un ancla de Anselin"),
    ]
    for pat, destino in reglas:
        m = re.match(pat, nombre)
        if m:
            return re.sub(pat, destino, nombre) if "\\1" in destino else destino
    return nombre


# Las comprobaciones que este arnés NO PUEDE romper, y no es una laguna:
# no leen el JSON que él envenena. Contrastan contra la fuente primaria o
# auditan la propia reimplementación del auditor.
INATACABLES = frozenset({
    "2 · un ancla de Anselin",
    "4 · el grado vale k",
    "relativa está contenida en Gabriel",
    "Gabriel está contenido en Delaunay",
    "y la torre está contenida en la reina",
    "D⁻¹A es la estandarizada por filas",
    "todas las k dan grado k, que es el punto",
    "y hay tildes de verdad que comprobar",
})


if __name__ == "__main__":
    raise SystemExit(arnes(
        "prueba_auditor_cap6.py — el arnés del auditor del capítulo 6",
        PY, AUDITOR, SALIDAS, ARCHIVOS, defectos(),
        "precalculo/rscript.sh precalculo/genera_cap6.R",
        agrupa=tipo_de, inatacables=INATACABLES))
