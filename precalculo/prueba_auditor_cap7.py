#!/usr/bin/env python3
"""
prueba_auditor_cap7.py — le rompe el precálculo al auditor y exige que lo cace

Material de Estadística Espacial 2026-II (20929). T4.4b.

POR QUÉ EXISTE. `audita_cap7.py` dio **576/0/4** cuando dejó de llamar
defecto a los convenios, y esa cifra no es la que vale: lo que vale es
que en el camino **cazó dos cosas reales** —que `spdep` permuta CON
reemplazo por defecto y GeoDa y `esda` sin él, y que la z de Gi* de
`esda` con pesos por filas lleva una varianza ocho veces mayor de la que
dan las ecuaciones de Ord y Getis— y que aquí se comprueba que cada una
de sus comprobaciones puede fallar.

La maquinaria vive en `prueba_auditor_base.py`. Aquí solo se declara QUÉ
romper, que es lo único propio del capítulo.

LAS FAMILIAS DE DEFECTO, y cada una imita algo que este capítulo puede
sufrir de verdad:

   1. cifra que deja de cuadrar con la fuente primaria (Columbus, los
      municipios, la rejilla de Getis-Ord)
   2. la I de Moran y sus piezas: E[I], las dos varianzas, los estilos,
      el rango real
   3. la inferencia: el p que deja de ser el suelo, las réplicas que no
      cuadran con su resumen, la potencia que no vale alfa en rho = 0
   4. el diagrama: la pendiente que deja de ser I           ← lo propio
      del capítulo: es la identidad que sostiene el módulo 4
   5. Geary y el barrio disparado
   6. el correlograma y el join count, contra la reimplementación
   7. las once W: parejas, islas y la I bajo cada una
   8. los I locales: Ii, cuadrantes, p, el factor n/(n-1) y el I de esda
   9. el mapa LISA: códigos, recuentos, islas
  10. LA MULTIPLICIDAD                                        ← el riesgo
      declarado del capítulo: Bonferroni, FDR, el suelo, BH a mano
  11. Getis-Ord: la celda 120, el barrido, los códigos, el cruce
  12. caja, cuantización, capas categóricas y aristas de un `.geomapa`
  13. tilde convertida en bytes crudos; flotante con más decimales
  14. metainformación y discrepancias que dejan de decir la verdad

UNA INYECCIÓN NO PUEDE USAR UN VALOR QUE YA ESTÉ EN EL ARCHIVO. De ahí
los valores con pinta de matrícula.

Uso:  python3 precalculo/prueba_auditor_cap7.py
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
AUDITOR = PRECALCULO / "audita_cap7.py"

ARCHIVOS = {
    "datos": ("CAP7_DATOS", "cap7_datos.json"),
    "mapas": ("CAP7_MAPAS", "cap7_mapas.json"),
}

PY = json.loads((PRECALCULO / "versiones_py.json").read_text(
    encoding="utf-8"))["ejecutable"]


def w7(d, ident):
    return next(c for c in d["m7"]["columbus"] if c["id"] == ident)


def w7m(d, ident):
    return next(c for c in d["m7"]["municipios"] if c["id"] == ident)


def capa(m, mapa, ident):
    return next(c for c in m[mapa]["capas"] if c["id"] == ident)


def cruce(d, cual, lisa):
    return next(c for c in d["m11"][cual]["cruce"] if c["lisa"] == lisa)


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
        "datos", lambda d: d["m1"]["columbus"].__setitem__("media", 37.1717))
    obj("1 · la correlación de CRIME con su rezago cambia",
        "datos", lambda d: d["m1"]["columbus"].__setitem__("cor_con_rezago", 0.7171))
    obj("1 · los municipios con dato cambian",
        "datos", lambda d: d["m3"]["municipios"]["aleatorizacion"].__setitem__("n", 1117))
    obj("1 · los municipios con vecinos cambian",
        "datos", lambda d: d["m3"]["municipios"]["aleatorizacion"].__setitem__("n_con_vecinos", 1117))
    obj("1 · la rejilla de Getis-Ord deja de tener 256 celdas",
        "datos", lambda d: d["m11"]["getisord"].__setitem__("n", 255))
    obj("1 · la GAL pierde parejas",
        "datos", lambda d: d["m2"]["columbus"].__setitem__("pares_gal", 113))

    # --- 2. La I de Moran y sus piezas --------------------------------
    obj("2 · la I de CRIME cambia",
        "datos", lambda d: d["m2"]["columbus"].__setitem__("I", 0.5171717171))
    obj("2 · E[I] deja de ser -1/(n-1)",
        "datos", lambda d: d["m2"]["columbus"].__setitem__("EI", -0.0217))
    obj("2 · la varianza por aleatorización cambia",
        "datos", lambda d: d["m2"]["columbus"].__setitem__("var_aleat", 0.0091717))
    obj("2 · la z por aleatorización cambia",
        "datos", lambda d: d["m2"]["columbus"].__setitem__("z_aleat", 5.7171))
    obj("2 · z'Wz deja de cuadrar",
        "datos", lambda d: d["m2"]["columbus"].__setitem__("z_Wz", 25.1717))
    obj("2 · el estilo B cambia de I",
        "datos", lambda d: next(e for e in d["m2"]["estilos"] if e["id"] == "B").__setitem__("I", 0.5317171717))
    obj("2 · el máximo del rango real cambia",
        "datos", lambda d: d["m2"]["rango"].__setitem__("columbus_gal", [-0.7053, 1.1717]))
    obj("2 · el E[I] del retículo cambia",
        "datos", lambda d: d["m1"]["reticulo"].__setitem__("EI", -0.0117))

    # --- 3. La inferencia ---------------------------------------------
    obj("3 · el p por permutación deja de ser el suelo",
        "datos", lambda d: d["m3"]["columbus"]["permutacion"].__setitem__("p", 0.017))
    obj("3 · alguna réplica alcanza la I observada",
        "datos", lambda d: d["m3"]["columbus"]["permutacion"].__setitem__("rango_observado", 3))
    obj("3 · una réplica publicada se dispara",
        "datos", lambda d: d["m3"]["columbus"]["permutacion"]["replicas"].__setitem__(0, 0.9171))
    obj("3 · la media de las réplicas no cuadra con ellas",
        "datos", lambda d: d["m3"]["columbus"]["permutacion"].__setitem__("media_sim", 0.1717))
    obj("3 · la curtosis de CRIME cambia",
        "datos", lambda d: d["m3"]["columbus"]["aleatorizacion"].__setitem__("curtosis", 3.1717))
    obj("3 · el p municipal por permutación deja de ser el suelo",
        "datos", lambda d: d["m3"]["municipios"]["permutacion"][0].__setitem__("p", 0.017))
    obj("3 · la I municipal cambia",
        "datos", lambda d: d["m3"]["municipios"]["aleatorizacion"].__setitem__("I", 0.371717))
    obj("3 · la potencia en rho = 0 deja de valer alfa",
        "datos", lambda d: d["m3"]["potencia"]["curvas"][2]["potencia"].__setitem__(0, 0.3131))
    obj("3 · la potencia en n = 100, rho = 0,5 cambia",
        "datos", lambda d: d["m3"]["potencia"]["curvas"][2]["potencia"].__setitem__(5, 0.1717))
    obj("3 · la potencia deja de crecer con n",
        "datos", lambda d: d["m3"]["potencia"]["curvas"][3]["potencia"].__setitem__(3, 0.0717))

    # --- 4. El diagrama de Moran (lo propio) --------------------------
    obj("4 · la pendiente deja de ser I",
        "datos", lambda d: d["m4"]["columbus"].__setitem__("pendiente", 0.4747474747))
    obj("4 · la pendiente sin tipificar cambia",
        "datos", lambda d: d["m4"]["columbus"].__setitem__("pendiente_sin_tipificar", 0.4747474747))
    obj("4 · un cuadrante cambia de recuento",
        "datos", lambda d: d["m4"]["columbus"]["cuadrantes"].__setitem__("AA", 27))
    obj("4 · un punto pierde su POLYID",
        "datos", lambda d: d["m4"]["columbus"]["puntos"]["polyid"].__setitem__(0, 99))
    obj("4 · una z publicada cambia",
        "datos", lambda d: d["m4"]["columbus"]["puntos"]["z"].__setitem__(0, 1.71717))
    obj("4 · la pendiente municipal sobre todas deja de ser I",
        "datos", lambda d: d["m4"]["municipios"].__setitem__("pendiente_todas", 0.371717))
    obj("4 · los influyentes dejan de ser coherentes",
        "datos", lambda d: d["m4"]["columbus"].__setitem__("influyentes_polyid", [7, 20, 30, 11, 99]))

    # --- 5. Geary ------------------------------------------------------
    obj("5 · la c de Geary cambia",
        "datos", lambda d: d["m5"]["columbus"].__setitem__("c", 0.5717171717))
    obj("5 · la z de Geary cambia",
        "datos", lambda d: d["m5"]["columbus"].__setitem__("z", 4.1717))
    obj("5 · 1 - c deja de cuadrar",
        "datos", lambda d: d["m5"]["columbus"].__setitem__("uno_menos_c", 0.4171717171))
    obj("5 · la I de HOVAL cambia",
        "datos", lambda d: d["m5"]["tres_variables"][1].__setitem__("I", 0.2171))
    obj("5 · la curva del pico deja de hundir a I",
        "datos", lambda d: d["m5"]["pico_en_alto"]["curva"][-1].__setitem__("I", 0.4171))
    obj("5 · el pico en alto cambia de barrio",
        "datos", lambda d: d["m5"]["pico_en_alto"].__setitem__("unidad", 3))
    obj("5 · la c municipal cambia",
        "datos", lambda d: d["m5"]["municipios"].__setitem__("c", 0.617171))

    # --- 6. Correlograma y join count ---------------------------------
    obj("6 · la I del orden 2 cambia",
        "datos", lambda d: d["m6"]["correlograma"]["columbus"][1].__setitem__("I", 0.171717))
    obj("6 · el orden 6 deja de tener unidades sin vecinos",
        "datos", lambda d: d["m6"]["correlograma"]["columbus"][5].__setitem__("sin_vecinos", 0))
    obj("6 · las parejas del orden 3 municipal cambian",
        "datos", lambda d: d["m6"]["correlograma"]["municipios"][2].__setitem__("pares", 13131))
    obj("6 · la I municipal del orden 4 cambia",
        "datos", lambda d: d["m6"]["correlograma"]["municipios"][3].__setitem__("I", 0.091717))
    obj("6 · un join count observado cambia",
        "datos", lambda d: d["m6"]["join_count"]["columbus_cp"]["tabla"][0].__setitem__("observado", 11.7171))
    obj("6 · un join count esperado cambia",
        "datos", lambda d: d["m6"]["join_count"]["columbus_cp"]["tabla"][0].__setitem__("esperado", 6.7171))
    obj("6 · el join count municipal esperado cambia",
        "datos", lambda d: d["m6"]["join_count"]["municipios_desercion"]["tabla"][2].__setitem__("esperado", 279.1717))
    obj("6 · las unidades por nivel cambian",
        "datos", lambda d: d["m6"]["join_count"]["columbus_cp"].__setitem__("n_por_nivel", [27, 22]))
    obj("6 · el p del join count sale del suelo",
        "datos", lambda d: d["m6"]["join_count"]["columbus_cp"]["p_permutacion"][0].__setitem__("p", 0.3117))

    # --- 7. Las once W --------------------------------------------------
    obj("7 · la I bajo k3 cambia",
        "datos", lambda d: w7(d, "k3").__setitem__("I", 0.517171))
    obj("7 · las islas del umbral a medias cambian",
        "datos", lambda d: w7(d, "d_mitad").__setitem__("islas", 17))
    obj("7 · las parejas de Delaunay cambian",
        "datos", lambda d: w7(d, "delaunay").__setitem__("pares", 131))
    obj("7 · las parejas municipales del umbral de 50 km cambian",
        "datos", lambda d: w7m(d, "d50").__setitem__("pares", 13171))
    obj("7 · la I municipal bajo k8 cambia",
        "datos", lambda d: w7m(d, "k8").__setitem__("I", 0.371717))
    obj("7 · el máximo de las once I cambia",
        "datos", lambda d: d["m7"]["resumen"].__setitem__("columbus_I", [0.3827, 0.7171]))
    obj("7 · la reina y la GAL difieren en más parejas",
        "datos", lambda d: d["m7"]["gal_vs_reina"].__setitem__("solo_reina", 5))
    obj("7 · el p máximo deja de ser el del umbral a medias",
        "datos", lambda d: w7(d, "d_mitad").__setitem__("p", 0.0117))

    # --- 8. Los I locales ------------------------------------------------
    obj("8 · los significativos de Columbus cambian",
        "datos", lambda d: d["m8"]["columbus"].__setitem__("significativos", 31))
    obj("8 · la media de los Ii deja de ser I",
        "datos", lambda d: d["m8"]["columbus"].__setitem__("media_Ii", 0.517171))
    obj("8 · el p mínimo cambia",
        "datos", lambda d: d["m8"]["columbus"].__setitem__("p_min", 0.00171))
    obj("8 · un Ii del JSON deja de ser el del CSV",
        "datos", lambda d: d["m8"]["columbus"]["Ii"].__setitem__(0, 0.71717))
    obj("8 · el I de esda equivalente cambia",
        "datos", lambda d: d["m8"]["municipios"].__setitem__("I_esda_equivalente", 0.371717))
    obj("8 · el factor de las islas cambia",
        "datos", lambda d: d["m8"]["municipios"].__setitem__("factor_islas", 1.0117))
    obj("8 · el municipio de mayor Ii cambia",
        "datos", lambda d: d["m8"]["municipios"]["top5"][0].__setitem__("municipio", "Envigado"))
    obj("8 · la suma de Ii entre S0 cambia",
        "datos", lambda d: d["m8"]["municipios"].__setitem__("suma_Ii_sobre_S0", 0.371717))
    obj("8 · las réplicas del módulo 8 dejan de ser las del capítulo",
        "datos", lambda d: d["m8"].__setitem__("nsim", 999))

    # --- 9. El mapa LISA --------------------------------------------------
    obj("9 · el recuento LISA de Columbus cambia",
        "datos", lambda d: d["m9"]["columbus"].__setitem__("conteo", [31, 10, 6, 1, 2]))
    obj("9 · un alto-alto desaparece de la lista",
        "datos", lambda d: d["m9"]["columbus"]["alto_alto_polyid"].pop())
    obj("9 · el recuento LISA municipal cambia",
        "datos", lambda d: d["m9"]["municipios"].__setitem__("conteo", [791, 140, 153, 19, 16]))
    obj("9 · las islas del mapa cambian de número",
        "datos", lambda d: d["m9"]["municipios"].__setitem__("sin_vecinos", 3))
    obj("9 · las islas cambian de nombre",
        "datos", lambda d: d["m9"]["municipios"]["islas"].__setitem__("municipio", ["Malpelo", "Providencia"]))
    obj("9 · el departamento con más alto-alto cambia",
        "datos", lambda d: d["m9"]["municipios"]["alto_alto_por_departamento"][0].__setitem__("n", 71))
    obj("9 · los colores dejan de ser cinco",
        "datos", lambda d: d["m9"].__setitem__("colores", d["m9"]["colores"][:4]))

    # --- 10. La multiplicidad (el riesgo declarado) -----------------------
    obj("10 · las réplicas mínimas de Bonferroni cambian",
        "datos", lambda d: d["m10"]["suelo"]["municipios"].__setitem__("nsim_minimo", 999))
    obj("10 · el umbral de Bonferroni cambia",
        "datos", lambda d: d["m10"]["suelo"]["municipios"].__setitem__("umbral_bonferroni", 0.000171))
    obj("10 · Bonferroni municipal cambia de recuento",
        "datos", lambda d: d["m10"]["municipios"]["tabla"]["plegado_nsim"].__setitem__("bonferroni", 17))
    obj("10 · FDR municipal cambia de recuento",
        "datos", lambda d: d["m10"]["municipios"]["tabla"]["plegado_nsim"].__setitem__("fdr", 171))
    obj("10 · sin corregir cambia de recuento",
        "datos", lambda d: d["m10"]["columbus"]["tabla"]["plegado_nsim"].__setitem__("sin_corregir", 21))
    obj("10 · el recuento del mapa con FDR cambia",
        "datos", lambda d: d["m10"]["municipios"].__setitem__("conteo_fdr", [1023, 47, 42, 5, 2]))
    obj("10 · el k de Benjamini-Hochberg cambia",
        "datos", lambda d: d["m10"]["columbus"]["bh"].__setitem__("k", 9))
    obj("10 · los umbrales de BH cambian",
        "datos", lambda d: d["m10"]["columbus"]["bh"]["umbrales"].__setitem__(0, 0.0171))
    obj("10 · los cuadrantes cambian con las réplicas",
        "datos", lambda d: d["m10"]["municipios"].__setitem__("cuadrantes_cambian", 7))
    obj("10 · la tabla pierde la fila analítica",
        "datos", lambda d: d["m10"]["columbus"]["tabla"].pop("analitico"))
    obj("10 · Bonferroni con 999 réplicas deja de dar cero",
        "datos", lambda d: d["m10"]["municipios"]["tabla"]["plegado_999"].__setitem__("bonferroni", 7))
    obj("10 · Holm rechaza menos que Bonferroni",
        "datos", lambda d: d["m10"]["municipios"]["tabla"]["plegado_nsim"].__setitem__("holm", 3))

    # --- 11. Getis-Ord ---------------------------------------------------
    obj("11 · la Gi* de la celda 120 cambia",
        "datos", lambda d: d["m11"]["getisord"].__setitem__("G_estrella", 1.7171))
    obj("11 · el ancla de Getis y Ord se mueve",
        "datos", lambda d: d["m11"]["getisord"].__setitem__("G_estrella_n1", 1.5171))
    obj("11 · el barrido a 60 cambia",
        "datos", lambda d: d["m11"]["getisord"]["barrido"][1].__setitem__("G_estrella", 2.7171))
    obj("11 · la celda del ejemplo cambia",
        "datos", lambda d: d["m11"]["getisord"].__setitem__("celda", 121))
    obj("11 · la mayor diferencia Gi frente a Gi* cambia",
        "datos", lambda d: d["m11"]["getisord"].__setitem__("dif_max_G_Gestrella", 0.7171))
    obj("11 · el recuento de Gi* de Columbus cambia",
        "datos", lambda d: d["m11"]["columbus"].__setitem__("conteo", [3, 5, 5, 22, 3, 5, 6]))
    obj("11 · la z máxima de Columbus cambia",
        "datos", lambda d: d["m11"]["columbus"].__setitem__("z_max", 3.7171))
    obj("11 · el POLYID de la z máxima cambia",
        "datos", lambda d: d["m11"]["columbus"].__setitem__("polyid_z_max", 17))
    obj("11 · el cruce alto-alto con calientes cambia",
        "datos", lambda d: cruce(d, "columbus", "Alto-alto").__setitem__("caliente", 7))
    obj("11 · los alto-bajo municipales dejan de salir fríos",
        "datos", lambda d: cruce(d, "municipios", "Alto-bajo").__setitem__("frio", 0))
    obj("11 · el municipio de mayor Gi* cambia",
        "datos", lambda d: d["m11"]["municipios"].__setitem__("municipio_z_max", "Bogotá, D.C."))
    obj("11 · el recuento municipal de Gi* cambia",
        "datos", lambda d: d["m11"]["municipios"].__setitem__("conteo", [83, 90, 52, 671, 72, 84, 67]))

    # --- 12. Los mapas ----------------------------------------------------
    obj("12 · un código LISA del mapa se sale de 1..5",
        "mapas", lambda m: capa(m, "cap7-columbus", "lisa")["valor"].__setitem__(0, 7))
    obj("12 · un código LISA del mapa deja de ser el del CSV",
        "mapas", lambda m: capa(m, "cap7-columbus", "lisa")["valor"].__setitem__(0, 2 if capa(m, "cap7-columbus", "lisa")["valor"][0] != 2 else 3))
    obj("12 · el recuento por nivel de una capa miente",
        "mapas", lambda m: capa(m, "cap7-columbus", "gistar").__setitem__("tam", [3, 5, 5, 22, 3, 5, 6]))
    obj("12 · una capa categórica pierde un nivel",
        "mapas", lambda m: capa(m, "cap7-columbus", "lisa").__setitem__("niveles", capa(m, "cap7-columbus", "lisa")["niveles"][:4]))
    obj("12 · una capa categórica pierde un color",
        "mapas", lambda m: capa(m, "cap7-municipios", "gistar").__setitem__("colores", capa(m, "cap7-municipios", "gistar")["colores"][:6]))
    obj("12 · una capa deja de declararse categórica",
        "mapas", lambda m: capa(m, "cap7-columbus", "lisa_fdr").pop("tipo"))
    obj("12 · el mapa de Columbus pierde un POLYID",
        "mapas", lambda m: m["cap7-columbus"]["polyid"].__setitem__(0, 99))
    obj("12 · la capa CRIME deja de ser CRIME",
        "mapas", lambda m: capa(m, "cap7-columbus", "crime")["valor"].__setitem__(0, 71.717))
    obj("12 · la capa municipal de deserción pierde su hueco",
        "mapas", lambda m: capa(m, "cap7-municipios", "desercion")["valor"].__setitem__(
            capa(m, "cap7-municipios", "desercion")["valor"].index(None), 3.17))
    obj("12 · una capa municipal cambia sus sin dato",
        "mapas", lambda m: capa(m, "cap7-municipios", "lisa").__setitem__("n_sin_dato", 4))
    obj("12 · un código municipal deja de ser el del CSV",
        "mapas", lambda m: capa(m, "cap7-municipios", "lisa_bonferroni")["valor"].__setitem__(5, 2))
    obj("12 · una variante del grafo pierde aristas",
        "mapas", lambda m: m["cap7-w"]["variantes"]["reina"].__setitem__("n_aristas", 117))
    obj("12 · una arista del grafo cambia de destino",
        "mapas", lambda m: m["cap7-w"]["variantes"]["k3"]["aristas"].__setitem__(1, 49))
    obj("12 · el grafo pierde la GAL",
        "mapas", lambda m: m["cap7-w"]["variantes"].pop("gal"))
    obj("12 · la rejilla deja de ser 16 × 16",
        "mapas", lambda m: m["cap7-getisord-valor"].__setitem__("nx", 15))
    obj("12 · el rango de la rejilla de Gi* cambia",
        "mapas", lambda m: m["cap7-getisord-g"].__setitem__("rango", [-2.8387, 4.7171]))
    obj("12 · el mapa de Columbus cambia de modo",
        "mapas", lambda m: m["cap7-columbus"].__setitem__("modo", "grafo"))
    obj("12 · la caja de un mapa se desordena",
        "mapas", lambda m: m["cap7-columbus"].__setitem__("caja", list(reversed(m["cap7-columbus"]["caja"]))))
    obj("12 · la cuantización de un mapa se inventa",
        "mapas", lambda m: m["cap7-municipios"].__setitem__("q", 777))


    # --- Lo que la primera tanda dejó sin ver fallar (109 tipos) -------
    obj("1 · la desviación de CRIME cambia",
        "datos", lambda d: d["m1"]["columbus"].__setitem__("sd", 17.1717))
    obj("1 · la reina de libpysal deja de tener 118 parejas",
        "datos", lambda d: d["m7"]["gal_vs_reina"].__setitem__("pares_reina", 117))
    obj("1 · la GAL gana una pareja propia",
        "datos", lambda d: d["m7"]["gal_vs_reina"].__setitem__("solo_gal", 2))
    obj("2 · S0 con estilo W deja de ser n",
        "datos", lambda d: d["m2"]["columbus"].__setitem__("S0", 47))
    obj("2 · z'z deja de ser n - 1",
        "datos", lambda d: d["m2"]["columbus"].__setitem__("z_z", 47))
    obj("2 · la varianza por normalidad cambia",
        "datos", lambda d: d["m2"]["columbus"].__setitem__("var_norm", 0.0091717))
    obj("2 · la z por normalidad cambia",
        "datos", lambda d: d["m2"]["columbus"].__setitem__("z_norm", 5.7171))
    obj("3 · las dos varianzas se igualan",
        "datos", lambda d: d["m3"]["columbus"]["normalidad"].__setitem__("var", d["m3"]["columbus"]["aleatorizacion"]["var"]))
    obj("2 · el S0 del estilo W cambia",
        "datos", lambda d: next(e for e in d["m2"]["estilos"] if e["id"] == "W").__setitem__("S0", 47))
    obj("2 · el S0 del estilo U cambia",
        "datos", lambda d: next(e for e in d["m2"]["estilos"] if e["id"] == "U").__setitem__("S0", 2))
    obj("2 · el mínimo del rango real cambia",
        "datos", lambda d: d["m2"]["rango"].__setitem__("columbus_gal", [-0.6171, 1.0417]))
    obj("2 · el máximo del retículo cambia",
        "datos", lambda d: d["m2"]["rango"].__setitem__("reticulo_10", [-1.0028, 1.1717]))
    obj("2 · la sd del retículo cambia",
        "datos", lambda d: d["m1"]["reticulo"].__setitem__("sd_norm", 0.0717))
    obj("3 · el p por normalidad cambia",
        "datos", lambda d: d["m3"]["columbus"]["normalidad"].__setitem__("p", 1.717e-08))
    obj("3 · el p por aleatorización cambia",
        "datos", lambda d: d["m3"]["columbus"]["aleatorizacion"].__setitem__("p", 1.717e-08))
    obj("3 · las réplicas dejan de ser 999",
        "datos", lambda d: d["m3"]["columbus"]["permutacion"].__setitem__("nsim", 998))
    obj("3 · se pierde una réplica publicada",
        "datos", lambda d: d["m3"]["columbus"]["permutacion"]["replicas"].pop())
    obj("3 · la desviación de las réplicas no cuadra",
        "datos", lambda d: d["m3"]["columbus"]["permutacion"].__setitem__("sd_sim", 0.1717))
    obj("3 · con 99 999 réplicas el p sale del suelo",
        "datos", lambda d: d["m3"]["columbus"]["permutacion_99999"].__setitem__("p", 0.00017))
    obj("3 · el p municipal con 9 999 réplicas sale del suelo",
        "datos", lambda d: d["m3"]["municipios"]["permutacion"][1].__setitem__("p", 0.0017))
    obj("3 · la rejilla de potencia pierde un rho",
        "datos", lambda d: d["m3"]["potencia"]["rhos"].pop())
    obj("3 · la potencia en n = 25, rho = 0,3 cambia",
        "datos", lambda d: d["m3"]["potencia"]["curvas"][0]["potencia"].__setitem__(3, 0.7171))
    obj("4 · el alto-alto municipal cambia",
        "datos", lambda d: d["m4"]["municipios"]["cuadrantes"].__setitem__("AA", 351))
    obj("4 · la pendiente municipal con vecinos cambia",
        "datos", lambda d: d["m4"]["municipios"].__setitem__("pendiente_con_vecinos", 0.371717))
    obj("4 · la pendiente con vecinos pasa a ser I",
        "datos", lambda d: d["m4"]["municipios"].__setitem__("pendiente_con_vecinos", d["m4"]["municipios"]["I"]))
    obj("5 · la varianza de Geary cambia",
        "datos", lambda d: d["m5"]["columbus"].__setitem__("var", 0.0117))
    obj("5 · 1 - c pasa a ser I",
        "datos", lambda d: d["m5"]["columbus"].__setitem__("uno_menos_c", d["m5"]["columbus"]["I"]))
    obj("5 · la c de INC cambia",
        "datos", lambda d: d["m5"]["tres_variables"][2].__setitem__("c", 0.7171))
    obj("5 · la curva del pico en bajo deja de subir c",
        "datos", lambda d: d["m5"]["pico_en_bajo"]["curva"][-1].__setitem__("c", 0.4171))
    obj("5 · el pico en bajo cambia de barrio",
        "datos", lambda d: d["m5"]["pico_en_bajo"].__setitem__("unidad", 3))
    obj("6 · las parejas del orden 2 cambian",
        "datos", lambda d: d["m6"]["correlograma"]["columbus"][1].__setitem__("pares", 201))
    obj("6 · los subgrafos del orden 6 cambian",
        "datos", lambda d: d["m6"]["correlograma"]["columbus"][5].__setitem__("subgrafos", 7))
    obj("6 · la I del orden 2 sube por encima de la del 1",
        "datos", lambda d: d["m6"]["correlograma"]["columbus"][1].__setitem__("I", 0.6171))
    obj("6 · la I municipal deja de caer en el orden 6",
        "datos", lambda d: d["m6"]["correlograma"]["municipios"][5].__setitem__("I", 0.0617))
    obj("6 · los mixtos dejan de ser menos de lo esperado",
        "datos", lambda d: d["m6"]["join_count"]["columbus_cp"]["tabla"][2].__setitem__("z", 1.717))
    obj("6 · los mixtos observados cambian",
        "datos", lambda d: d["m6"]["join_count"]["columbus_cp"]["tabla"][2].__setitem__("observado", 5.7171))
    obj("7 · las islas municipales del umbral de 50 km cambian",
        "datos", lambda d: w7m(d, "d50").__setitem__("islas", 41))
    obj("7 · el mínimo de las once I cambia",
        "datos", lambda d: d["m7"]["resumen"].__setitem__("columbus_I", [0.2171, 0.5968]))
    obj("7 · alguna W deja de rechazar al 5 %",
        "datos", lambda d: d["m7"]["resumen"].__setitem__("columbus_p_max", 0.0717))
    obj("7 · una W municipal deja de rechazar de sobra",
        "datos", lambda d: d["m7"]["resumen"].__setitem__("municipios_p_max", 0.017))
    obj("8 · los significativos municipales cambian",
        "datos", lambda d: d["m8"]["municipios"].__setitem__("significativos", 321))
    obj("8 · el p mínimo municipal cambia",
        "datos", lambda d: d["m8"]["municipios"].__setitem__("p_min", 0.00017))
    obj("8 · el Ii máximo cambia",
        "datos", lambda d: d["m8"]["municipios"].__setitem__("Ii_max", 9.7171))
    obj("8 · el primero del top cambia de Ii",
        "datos", lambda d: d["m8"]["municipios"]["top5"][0].__setitem__("Ii", 9.1717))
    obj("9 · alfa deja de ser el 5 %",
        "datos", lambda d: d["m9"].__setitem__("alfa", 0.1))
    obj("9 · un bajo-bajo desaparece de la lista",
        "datos", lambda d: d["m9"]["columbus"]["bajo_bajo_polyid"].pop())
    obj("9 · aparece un atípico que no existe",
        "datos", lambda d: d["m9"]["columbus"]["atipicos_polyid"].append(99))
    obj("9 · el departamento con más bajo-bajo cambia",
        "datos", lambda d: d["m9"]["municipios"]["bajo_bajo_por_departamento"][0].__setitem__("n", 71))
    obj("10 · el n del suelo cambia",
        "datos", lambda d: d["m10"]["suelo"]["columbus"].__setitem__("n", 47))
    obj("10 · el p bilateral rechaza más que el plegado",
        "datos", lambda d: d["m10"]["municipios"]["tabla"]["bilateral_nsim"].__setitem__("sin_corregir", 371))
    obj("10 · la fila de 999 dice otras réplicas",
        "datos", lambda d: d["m10"]["municipios"]["tabla"]["plegado_999"].__setitem__("nsim", 499))
    obj("10 · FDR rechaza menos que Holm",
        "datos", lambda d: d["m10"]["municipios"]["tabla"]["plegado_nsim"].__setitem__("fdr", 3))
    obj("10 · Bonferroni con las réplicas del capítulo deja cero",
        "datos", lambda d: d["m10"]["municipios"]["tabla"]["plegado_nsim"].__setitem__("bonferroni", 0))
    obj("10 · el p normal permutado cambia de recuento",
        "datos", lambda d: d["m10"]["municipios"]["tabla"]["normal_permutado_nsim"].__setitem__("sin_corregir", 171))
    obj("10 · los p ordenados de BH dejan de ser los del CSV",
        "datos", lambda d: d["m10"]["columbus"]["bh"]["p_ordenados"].__setitem__(0, 0.0171))
    obj("10 · el umbral de Bonferroni de BH cambia",
        "datos", lambda d: d["m10"]["columbus"]["bh"].__setitem__("umbral_bonferroni", 0.0017))
    obj("10 · el conjunto significativo deja de cambiar",
        "datos", lambda d: d["m10"]["municipios"].__setitem__("significativos_cambian", 0))
    obj("11 · los vecinos medios a 30 cambian",
        "datos", lambda d: d["m11"]["getisord"].__setitem__("vecinos_medio", 3.17))
    obj("11 · las celdas calientes cambian",
        "datos", lambda d: d["m11"]["getisord"].__setitem__("calientes_95", 71))
    obj("11 · el cruce bajo-bajo con fríos cambia",
        "datos", lambda d: cruce(d, "columbus", "Bajo-bajo").__setitem__("frio", 3))
    obj("11 · el cruce municipal alto-alto con calientes cambia",
        "datos", lambda d: cruce(d, "municipios", "Alto-alto").__setitem__("caliente", 131))
    # --- 12. Los mapas, lo que faltaba -------------------------------------
    obj("12 · un mapa se sale del presupuesto",
        "mapas", lambda m: m["cap7-columbus"].__setitem__("relleno", "x" * 250000))
    obj("12 · una rejilla se sale del presupuesto",
        "mapas", lambda m: m["cap7-getisord-g"].__setitem__("relleno", "x" * 250000))
    obj("12 · un código de Gi* se sale de 1..7",
        "mapas", lambda m: capa(m, "cap7-columbus", "gistar")["valor"].__setitem__(0, 9))
    obj("12 · un mapa declara un modo que no existe",
        "mapas", lambda m: m["cap7-w"].__setitem__("modo", "hexbin"))
    obj("12 · una rejilla declara un modo que no existe",
        "mapas", lambda m: m["cap7-getisord-g"].__setitem__("modo", "raster"))
    obj("12 · el grafo se publica como polígonos",
        "mapas", lambda m: m["cap7-w"].__setitem__("modo", "poligonos"))
    obj("12 · la rejilla se publica como polígonos",
        "mapas", lambda m: m["cap7-getisord-valor"].__setitem__("modo", "poligonos"))
    obj("12 · la rejilla cambia de cuantización",
        "mapas", lambda m: m["cap7-getisord-g"].__setitem__("zqmax", 999))
    obj("12 · la rejilla pierde sus valores",
        "mapas", lambda m: m["cap7-getisord-valor"].__setitem__("zq", []))
    obj("12 · el grafo desaparece del JSON",
        "mapas", lambda m: m.pop("cap7-w"))
    obj("12 · una rejilla desaparece del JSON",
        "mapas", lambda m: m.pop("cap7-getisord-g"))
    obj("12 · la caja de una rejilla se desordena",
        "mapas", lambda m: m["cap7-getisord-valor"].__setitem__("caja", list(reversed(m["cap7-getisord-valor"]["caja"]))))
    obj("12 · una capa municipal desaparece",
        "mapas", lambda m: m["cap7-municipios"]["capas"].pop(3))
    obj("12 · un mapa declara una codificación que no existe",
        "mapas", lambda m: m["cap7-columbus"].__setitem__("codificacion", "zip"))
    obj("12 · una rejilla declara una codificación que no existe",
        "mapas", lambda m: m["cap7-getisord-valor"].__setitem__("codificacion", "zip"))
    obj("12 · una rejilla trae una q inválida",
        "mapas", lambda m: m["cap7-getisord-g"].__setitem__("q", 777))
    obj("12 · la rejilla pierde un lado",
        "mapas", lambda m: m["cap7-getisord-g"].pop("ny"))
    obj("12 · el mapa municipal deja de tener 1 122",
        "mapas", lambda m: m["cap7-municipios"].__setitem__("n", 1121))
    obj("12 · una celda se sale de la cuantización",
        "mapas", lambda m: m["cap7-getisord-g"]["zq"].__setitem__(0, 1001))
    obj("12 · una celda cae por debajo de -1",
        "mapas", lambda m: m["cap7-getisord-valor"]["zq"].__setitem__(0, -2))
    obj("12 · la capa CRIME pierde sus cortes",
        "mapas", lambda m: capa(m, "cap7-columbus", "crime").pop("cortes"))
    obj("12 · una capa municipal gana un sin dato",
        "mapas", lambda m: capa(m, "cap7-municipios", "lisa_fdr")["valor"].__setitem__(0, None))
    obj("12 · el mínimo de una rejilla cambia",
        "mapas", lambda m: m["cap7-getisord-valor"].__setitem__("rango", [1.0, m["cap7-getisord-valor"]["rango"][1]]))
    obj("12 · el mapa de Columbus pierde la capa CRIME",
        "mapas", lambda m: m["cap7-columbus"]["capas"].pop(0))
    obj("12 · una capa pierde un rasgo",
        "mapas", lambda m: capa(m, "cap7-municipios", "gistar")["valor"].pop())
    obj("12 · la q de un mapa está inflada",
        "mapas", lambda m: m["cap7-columbus"].__setitem__(
            "geom", [[[c // 4 for c in parte] for parte in rasgo] for rasgo in m["cap7-columbus"]["geom"]]))

    obj("4 · el bajo-bajo municipal cambia",
        "datos", lambda d: d["m4"]["municipios"]["cuadrantes"].__setitem__("BB", 461))
    obj("12 · la rejilla pierde su cuantización declarada",
        "mapas", lambda m: m["cap7-getisord-valor"].pop("zqmax"))

    # --- 13. Formato -------------------------------------------------------
    txt("13 · una tilde se convierte en bytes crudos", "datos", "ó", "Ã³")
    obj("13 · un flotante con más decimales de los declarados",
        "datos", lambda d: d["m2"]["columbus"].__setitem__("var_norm", 0.008780000000123456))

    # --- 14. Metainformación y discrepancias ----------------------------
    obj("14 · el capítulo dice ser el 8",
        "datos", lambda d: d["meta"].__setitem__("capitulo", 8))
    obj("14 · las semanas cambian",
        "datos", lambda d: d["meta"].__setitem__("semanas", "10-11"))
    obj("14 · las anclas comprobadas bajan",
        "datos", lambda d: d["meta"].__setitem__("anclas", 3))
    obj("14 · las réplicas del capítulo dejan de ser 24 999",
        "datos", lambda d: d["meta"].__setitem__("nsim", 9999))
    obj("14 · el p del capítulo deja de ser el plegado",
        "datos", lambda d: d["meta"].__setitem__("p", "Pr(z != E(Ii))"))
    obj("14 · la discrepancia de las islas desaparece",
        "datos", lambda d: d["discrepancias"].pop(0))
    obj("14 · el valor de Python de la discrepancia cambia",
        "datos", lambda d: d["discrepancias"][0].__setitem__("valor_python", 0.371717))

    return D


def tipo_de(nombre: str) -> str:
    """Colapsa las instancias de un mismo mecanismo en un solo tipo."""
    reglas = [
        (r"^estilo [BWSCU]: I$",                              "2 · la I bajo un estilo"),
        (r"^estilo [BWSCU]: S0 = .+$",                        "2 · el S0 de un estilo"),
        (r"^potencia n=\d+: en rho = 0 vale alfa$",           "3 · la potencia vale alfa en rho = 0"),
        (r"^potencia n=\d+: crece con rho$",                  "3 · la potencia crece con rho"),
        (r"^potencia n=\d+, rho=[\d,]+, recalculada$",        "3 · una celda de potencia recalculada"),
        (r"^cuadrante (AA|BB|AB|BA)$",                        "4 · un cuadrante de Columbus"),
        (r"^(CRIME|HOVAL|INC): (I|c)$",                       r"5 · la \2 de una variable"),
        (r"^pico_en_\w+ ×[\d.]+: (I|c)$",                     r"5 · la \1 de un pico"),
        (r"^pico_en_\w+: (.+)$",                              r"5 · \1, de un pico"),
        (r"^orden \d+: (.+)$",                                r"6 · \1, de un orden"),
        (r"^municipios orden \d+: (.+)$",                     r"6 · \1, de un orden municipal"),
        (r"^jc \S+: .+ obs$",                                 "6 · join count: un par observado"),
        (r"^jc \S+: .+ esp$",                                 "6 · join count: un par esperado"),
        (r"^jc \S+: (.+)$",                                   r"6 · join count: \1"),
        (r"^W \w+: (.+)$",                                    r"7 · \1, de una W"),
        (r"^municipios W \w+: (.+)$",                         r"7 · \1, de una W municipal"),
        (r"^suelo \w+: (.+)$",                                r"10 · el suelo: \1"),
        (r"^(columbus|municipios): (.+)$",                    r"tablero · \2"),
        (r"^barrido d=\d+: (.+)$",                            "11 · el barrido de Getis-Ord"),
        (r"^cruce (.+): (calientes|fríos)$",                  r"11 · el cruce LISA × Gi*: \2"),
        (r"^municipios cruce (.+): (calientes|fríos)$",       r"11 · el cruce municipal: \2"),
        (r"^variante \w+: (.+)$",                             r"12 · \1, de una variante"),
        (r"^mapa \w+/\w+: (.+)$",                             r"12 · \1, de una capa"),
        (r"^go-\w+: (.+)$",                                   r"12 · \1, de una rejilla"),
        (r"^mapa \w+: (.+)$",                                 r"12 · \1, de un mapa"),
        (r"^Anselin \(1995\): (.+)$",                         "2 · un ancla de Anselin"),
    ]
    for pat, destino in reglas:
        m = re.match(pat, nombre)
        if m:
            return re.sub(pat, destino, nombre) if "\\" in destino else destino
    return nombre


# Las comprobaciones que este arnés NO PUEDE romper, y no es una laguna:
# no leen el JSON que él envenena. Contrastan contra la fuente primaria o
# auditan la propia reimplementación del auditor, o el CSV, que el arnés
# no toca.
INATACABLES = frozenset({
    "2 · un ancla de Anselin",
    "el CSV recorre los 49 POLYID una vez",
    "el CSV y el shapefile cuentan el mismo CRIME",
    "la GAL es simétrica",
    "los índices 0-basados del CSV son los 1-basados menos uno",
    "y vale -1/48",
    "y el rango no es [-1, 1]",
    "esda también da el suelo",
    "el CSV municipal trae la deserción",
    "z del CSV = CRIME tipificado",
    "Wz del CSV = W·z",
    "tablero · z del CSV",
    "tablero · Wz del CSV",
    "los cuadrantes de esda son los de spdep",
    "y son los signos de z y Wz",
    "Ii = esda × n/(n-1), los 49",
    "la media de los Ii es I",
    "la suma de los Ii entre S0 es I",
    "los p por rangos coinciden hasta el error de Monte Carlo",
    "y no baja del suelo",
    "tablero · Ii = esda × n/(n-1)",
    "y las islas tienen Ii = 0",
    "suma de Ii entre S0",
    "el p municipal es NA solo en las islas",
    "tablero · p por rangos hasta el error de Monte Carlo",
    "Columbus: los códigos LISA salen del p y el cuadrante",
    "tablero · los códigos LISA salen del p y el cuadrante",
    "y spdep les asigna bajo-bajo con rezago cero",
    "Gi (z) en las 256 celdas",
    "Gi* (z) en las 256",
    "Columbus: Gi* (z) en los 49, esda en binario",
    "y con las ecuaciones de Ord y Getis (1995) a mano",
    "esda con pesos por filas NO da esa z: defecto declarado",
    "Columbus: p de Gi* hasta el error de Monte Carlo",
    "Columbus: los siete códigos salen de z y p",
    "tablero · Gi* (z), con esda",
    "tablero · p de Gi* hasta el error de Monte Carlo",
    "tablero · códigos de Gi* desde z y p, islas sin código",
    "y hay tildes de verdad que comprobar",
    "la GAL va la primera de las once",
    "y es 16 × 16",
    "las dos discrepancias van declaradas",
    "moran_islas: el valor de Python ES el de esda",
    "y ES el I de esda, con n = todas",
    "esfera: entre Gabriel y Delaunay",
    "ningún alto-alto sale frío",
    "tablero · los códigos con Bonferroni, desde el p",
    "tablero · el recuento con Bonferroni",
    "tablero · el recuento con FDR",
    "tablero · sin corregir, desde el CSV",
    "tablero · Bonferroni, desde el CSV",
    "tablero · FDR por Benjamini-Hochberg, a mano",
    "y esda cuenta casi los mismos",
})


if __name__ == "__main__":
    raise SystemExit(arnes(
        "prueba_auditor_cap7.py — el arnés del auditor del capítulo 7",
        PY, AUDITOR, SALIDAS, ARCHIVOS, defectos(),
        "precalculo/rscript.sh precalculo/genera_cap7.R",
        agrupa=tipo_de, inatacables=INATACABLES))
