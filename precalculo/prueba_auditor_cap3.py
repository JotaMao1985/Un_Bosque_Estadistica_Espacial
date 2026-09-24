#!/usr/bin/env python3
"""
prueba_auditor_cap3.py — le rompe el precálculo al auditor y exige que lo cace

Material de Estadística Espacial 2026-II (20929). T2.4b.

POR QUÉ EXISTE. Un auditor que informa «0 fallos» la primera vez que corre
no ha demostrado nada: puede estar comprobando bien o puede estar
comprobando cosas incapaces de fallar. Es la regla 1 de
[[feedback-auditar-trabajo]], y en T0.5 ese recuento empezó siendo 14 de 76.

La maquinaria vive en `prueba_auditor_base.py`. Aquí solo se declara QUÉ
romper, que es lo único propio del capítulo.

LAS FAMILIAS DE DEFECTO. Cada una imita un fallo que ya ocurrió de verdad
en este proyecto o que este capítulo puede sufrir:

   1. cifra publicada que deja de cuadrar con la fuente primaria
   2. cifra derivada que deja de cuadrar con las que la generan
   3. relación cualitativa que se rompe (monotonías, órdenes, signos)
   4. BANDERA que deja de coincidir con el hecho que afirma   ← T1.1, regla 4
   5. propiedad TEÓRICA exacta que se viola (corr = 1 de los cartogramas)
   6. discrepancia declarada que pierde su explicación         ← A.2
   7. simulación de daltonismo alterada                        ← T2.4
   8. cortes, capas, caja o cuantización del .geomapa          ← T0.3
   9. tilde convertida en bytes crudos <c3><b3>                ← T0.5
  10. flotante con más decimales de los declarados             ← T0.5
  11. solución de un ejercicio guiado alterada
  12. coherencia entre módulos rota
  13. recuento del gerrymandering que no cuadra con su rejilla

UNA INYECCIÓN NO PUEDE USAR UN VALOR QUE YA ESTÉ EN EL ARCHIVO. Si la
cifra falsa coincide con otra real, el auditor podría «cazarla» por el
motivo equivocado y el arnés se felicitaría solo.

Uso:  python3 precalculo/prueba_auditor_cap3.py
Devuelve 1 si algún defecto se cuela.
"""
from __future__ import annotations

import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from prueba_auditor_base import arnes

RAIZ = pathlib.Path(__file__).resolve().parent.parent
PRECALCULO = RAIZ / "precalculo"
SALIDAS = PRECALCULO / "salidas"
AUDITOR = PRECALCULO / "audita_cap3.py"

ARCHIVOS = {
    "datos": ("CAP3_DATOS", "cap3_datos.json"),
    "mapas": ("CAP3_MAPAS", "cap3_mapas.json"),
    "soluciones": ("CAP3_SOLUCIONES", "cap3_soluciones.json"),
}

PY = json.loads((PRECALCULO / "versiones_py.json").read_text(
    encoding="utf-8"))["ejecutable"]


def defectos():
    """(nombre, archivo, tipo, acción). tipo ∈ {'obj', 'txt'}."""
    D = []

    def obj(nombre, clave, fn):
        D.append((nombre, clave, "obj", fn))

    def txt(nombre, clave, busca, pone):
        D.append((nombre, clave, "txt", (busca, pone)))

    # --- 1. Cifras contra la fuente primaria --------------------------
    obj("1 · la deserción media deja de cuadrar con el CSV",
        "datos", lambda d: d["m1"]["desercion"].__setitem__("media", 7.7313131313))
    obj("1 · el nº de municipios con dato cambia",
        "datos", lambda d: d["m1"].__setitem__("n_con_dato", 1077))
    obj("1 · los registros publicables de Saber 11 cambian",
        "datos", lambda d: d["fuente"].__setitem__("n_publicable", 1065433))
    obj("1 · la r individual de la escalera deja de ser la del microdato",
        "datos", lambda d: d["m8"].__setitem__("r_individuo", 0.4413131313))
    obj("1 · el nº de condados empatados de nc cambia",
        "datos", lambda d: d["m3"].__setitem__("n_empatados", 37))
    obj("1 · el solape de los dos top-20 del módulo 2 cambia",
        "datos", lambda d: d["m2"].__setitem__("solape_top20", 7))
    obj("1 · los estudiantes sin polígono cambian",
        "datos", lambda d: d["m11"]["sin_poligono"].__setitem__("n_estudiantes", 431))

    # --- 2. Cifras derivadas que dejan de cuadrar ---------------------
    obj("2 · el % de mapas distintos no sale de sus dos números",
        "datos", lambda d: d["m1"].__setitem__("pct_distintos", 71.4285714286))
    obj("2 · la caída de una paleta no sale de sus dos distancias",
        "datos", lambda d: d["m5"]["paletas"][0]["simulaciones"][0].__setitem__(
            "caida_pct", 51.1717171717))
    obj("2 · la brecha ponderada del módulo 9 no sale de sus dos medias",
        "datos", lambda d: d["m9"]["sin_ponderar"].__setitem__(
            "brecha_ponderada", 0.1919191919))
    obj("2 · el radio de los símbolos deja de ser la raíz de la razón",
        "datos", lambda d: d["m7"]["simbolos"].__setitem__("radio_max_rel", 41.1717171717))
    obj("2 · el desvío por quedarse fuera del mapa no sale de sus dos r",
        "datos", lambda d: d["m8"]["cartografica"].__setitem__(
            "desvio_departamental", 0.0313131313))
    obj("2 · el % del top-10 del módulo 2 deja de cuadrar",
        "datos", lambda d: d["m2"].__setitem__("pct_estudiantes_top10", 41.7171717171))

    # --- 3. Relaciones cualitativas ----------------------------------
    obj("3 · la nube individual deja de ser monótona",
        "datos", lambda d: d["m10"]["nube_individual"][7].__setitem__("media", 191.7171717171))
    obj("3 · los cuantiles de una familia del módulo 9 se desordenan",
        "datos", lambda d: d["m9"]["contiguas"].__setitem__("q50", 0.0313131313))
    obj("3 · el cartograma contiguo deja de mejorar al iterar más",
        "datos", lambda d: d["m7"]["barrido_contiguo"][3].__setitem__(
            "max_error_rel", 9.1717171717))
    obj("3 · el histograma del módulo 9 deja de sumar las 1 000",
        "datos", lambda d: d["m9"]["hist_contiguas"]["conteo"].__setitem__(0, 77))
    obj("3 · el mínimo y el máximo de escaños dejan de diferir",
        "datos", lambda d: d["m9"]["gerrymandering"].__setitem__("escanos_min",
                                                                 d["m9"]["gerrymandering"]["escanos_max"]))

    # --- 4. Banderas contra el hecho que afirman ---------------------
    obj("4 · la bandera de inversión de signo del estrato se apaga",
        "datos", lambda d: d["m11"]["estrato"].__setitem__("invierte_signo", False))

    # --- 5. Propiedades teóricas exactas -----------------------------
    obj("5 · el cartograma de Olson deja de ser exactamente proporcional",
        "datos", lambda d: d["m7"]["cartogramas"][0].__setitem__("corr", 0.9917171717))
    obj("5 · el de Dorling publica un error relativo que ya no es exacto",
        "datos", lambda d: d["m7"]["cartogramas"][1].__setitem__(
            "max_error_rel", 0.0313131313))
    obj("5 · el contiguo pasa a declararse exactamente proporcional",
        "datos", lambda d: d["m7"]["cartogramas"][2].__setitem__("corr", 1.0))
    obj("5 · el reparto del hexbin deja de conservar el total",
        "datos", lambda d: d["m7"]["hexbin"].__setitem__("error_reparto_rel", 0.0171717171))
    obj("5 · el Olson propio y el del paquete dejan de diferir en un factor global",
        "datos", lambda d: d["m7"]["contraste_olson"].__setitem__("cv_razon", 0.0031313131))

    # --- 6. La discrepancia declarada de A.2 -------------------------
    obj("6 · los empates en los cortes de cuantiles desaparecen",
        "datos", lambda d: [e.__setitem__("n_iguales", 0)
                            for e in d["m3"]["empates_en_cortes"]])
    obj("6 · el convenio de intervalo de Python se iguala al de R",
        "datos", lambda d: d["m3"].__setitem__("convenio_python", "[a, b)"))
    obj("6 · los cuantiles pasan a coincidir con Python (se pierde A.2)",
        "datos", lambda d: d["m3"]["esquemas"][1].__setitem__("tam", [24, 27, 11, 19, 19]))
    obj("6 · Fisher-Jenks deja de coincidir entre R y Python",
        "datos", lambda d: d["m3"]["esquemas"][2].__setitem__("tam", [30, 36, 19, 11, 4]))

    # --- 7. La simulación de daltonismo ------------------------------
    obj("7 · un color simulado de las anclas cambia",
        "datos", lambda d: d["m5"]["anclas_cvd"][0]["salida"].__setitem__(0, "#7B7B17"))
    obj("7 · la matriz de deuteranopia deja de ser la de Machado",
        "datos", lambda d: d["m5"]["matriz_deuteranopia"].__setitem__(0, 0.3173131313))
    obj("7 · el dE del rojo/verde bajo daltonismo se infla",
        "datos", lambda d: d["m5"]["rojo_verde"].__setitem__(
            "dE_deuteranopia", 71.7171717171))
    obj("7 · el rango de luminosidad de una paleta cambia",
        "datos", lambda d: d["m5"]["paletas"][3].__setitem__(
            "rango_luminosidad", 31.7171717171))

    # --- 8. El .geomapa ----------------------------------------------
    obj("8 · el mapa municipal pierde su cuantización reducida",
        "mapas", lambda m: m["municipios"].__setitem__("q", 4096))
    obj("8 · un municipio queda clasificado fuera de su intervalo",
        "mapas", lambda m: m["municipios"]["capas"][0]["cortes"].__setitem__(
            1, m["municipios"]["capas"][0]["cortes"][1] * 0.31))
    obj("8 · los mapas del módulo 7 dejan de compartir caja",
        "mapas", lambda m: m["dep_ncont"]["caja"].__setitem__(
            0, m["dep_ncont"]["caja"][0] - 171717.0))
    obj("8 · una capa del mapa municipal pierde valores",
        "mapas", lambda m: m["municipios"]["capas"][1].__setitem__(
            "valor", m["municipios"]["capas"][1]["valor"][:1100]))
    obj("8 · el nº de sin-dato declarado deja de cuadrar con los nulos",
        "mapas", lambda m: m["municipios"]["capas"][0].__setitem__("n_sin_dato", 7))
    obj("8 · una capa superpuesta pierde el modo declarado desde R",
        "mapas", lambda m: m["dep_coropleto"]["superpuestos"][0].__setitem__(
            "modo", "inventado"))
    obj("8 · el cartograma de Olson pasa a ocupar más lienzo que el coropleto",
        "mapas", lambda m: m["dep_ncont"].__setitem__(
            "geom", m["dep_coropleto"]["geom"]))
    obj("8 · el mapa de nc pierde uno de sus cinco esquemas",
        "mapas", lambda m: m["nc_esquemas"].__setitem__(
            "vistas", list(m["nc_esquemas"]["vistas"])[:4]))
    obj("8 · las vistas dejan de ser una lista y pasan a ser un objeto",
        "mapas", lambda m: m["nc_esquemas"].__setitem__(
            "vistas", {v["estilo"]: v for v in m["nc_esquemas"]["vistas"]}))

    # --- 9. La codificación ------------------------------------------
    txt("9 · una tilde se convierte en bytes crudos", "datos",
        "Educación profesional completa", "EducaciÃ³n profesional completa")

    # --- 10. El redondeo ---------------------------------------------
    obj("10 · un flotante se publica con más decimales de los declarados",
        "datos", lambda d: d["m8"].__setitem__("r_municipio", 0.303331313131313131))

    # --- 11. Los ejercicios ------------------------------------------
    obj("11 · un ejercicio se queda sin enunciado",
        "soluciones", lambda s: s["ejercicios"][1].__setitem__("enunciado", ""))
    obj("11 · un ejercicio se queda sin solución",
        "soluciones", lambda s: s["ejercicios"][3].__setitem__("solucion", {}))
    obj("11 · un ejercicio se queda sin lectura",
        "soluciones", lambda s: s["ejercicios"][2].__setitem__("lectura", ""))
    obj("11 · un ejercicio se queda con dos pasos",
        "soluciones", lambda s: s["ejercicios"][0].__setitem__(
            "pasos", s["ejercicios"][0]["pasos"][:2]))
    obj("11 · desaparece un ejercicio de los cuatro",
        "soluciones", lambda s: s.__setitem__("ejercicios", s["ejercicios"][:3]))

    # --- 12. Coherencia entre módulos --------------------------------
    obj("12 · dentro + entre deja de sumar el 100 % de la varianza",
        "datos", lambda d: d["m10"].__setitem__("pct_var_dentro", 77.1717171717))
    obj("12 · la referencia del módulo 9 deja de ser la del módulo 8",
        "datos", lambda d: d["m9"].__setitem__("r_real", 0.4713131313))
    obj("12 · dos semillas del capítulo pasan a ser la misma",
        "datos", lambda d: d["meta"]["semillas"].__setitem__(
            "particiones_arbitrarias", d["meta"]["semillas"]["particiones_contiguas"]))

    # --- 13. El gerrymandering ---------------------------------------
    obj("13 · un ejemplo publica más escaños de los que su trazado da",
        "datos", lambda d: d["m9"]["gerrymandering"]["ejemplos"][0].__setitem__(
            "escanos_A", d["m9"]["gerrymandering"]["ejemplos"][0]["escanos_A"] + 1))
    obj("13 · un trazado deja un distrito con una casilla de más",
        "datos", lambda d: d["m9"]["gerrymandering"]["ejemplos"][0]["particion"].__setitem__(
            0, 1 + d["m9"]["gerrymandering"]["ejemplos"][0]["particion"][0] % 5))
    obj("13 · el porcentaje de A deja de cuadrar con su rejilla",
        "datos", lambda d: d["m9"]["gerrymandering"].__setitem__("pct_A", 57.1717171717))
    obj("13 · la distribución deja de sumar las particiones válidas",
        "datos", lambda d: d["m9"]["gerrymandering"]["distribucion"][3].__setitem__("n", 7))

    # --- 15. El par más parecido del módulo 5 (2026-09-24) ------------
    # La medida pasó de «clases contiguas» a «el par más parecido», y el
    # recuadro afirma siete cosas de la tabla. Cada una, rota por separado.
    obj("15 · el par más parecido de una paleta cambia de distancia",
        "datos", lambda d: d["m5"]["paletas"][5]["simulaciones"][0].__setitem__(
            "dpar", 9.9171717171))
    obj("15 · el par que RdYlGn pierde deja de ser el 2-4",
        "datos", lambda d: d["m5"]["paletas"][2]["simulaciones"][0].__setitem__("par", [1, 5]))
    obj("15 · la distancia en gris de una paleta cambia",
        "datos", lambda d: d["m5"]["paletas"][4]["gris"].__setitem__("dpar", 3.1717171717))
    obj("15 · una divergente pasa a tener L* monótona",
        "datos", lambda d: d["m5"]["paletas"][4].__setitem__("luminosidad_monotona", True))
    obj("15 · en gris cae más una divergente",
        "datos", lambda d: d["m5"]["vistas"][3].update(peor="RdBu", peor_tipo="divergente"))
    obj("15 · el suelo de las secuenciales cambia de vista",
        "datos", lambda d: d["m5"]["suelo_secuenciales"].__setitem__("tipo", "tritanopia"))
    obj("15 · la peor secuencial en gris cambia",
        "datos", lambda d: d["m5"].__setitem__("gris_secuenciales_min", 6.0171717171))
    obj("15 · una cualitativa recorre tanta L* como una divergente",
        "datos", lambda d: d["m5"]["paletas"][6].__setitem__("rango_luminosidad", 57.1717171717))
    obj("15 · el recorrido de Set1 en sus órdenes se estrecha",
        "datos", lambda d: d["m5"]["orden_set1"].__setitem__("contiguas_max", 92.8717171717))
    obj("15 · el peor orden de Set1 deja de dar su par",
        "datos", lambda d: d["m5"]["orden_set1"].__setitem__("contiguas_min", 41.1717171717))

    # --- 16. La curva del módulo 8 y su forma (2026-09-24) ------------
    # Con 30 particiones el capítulo leyó en la curva una cima y un bache que
    # eran ruido. Lo que ahora dice de su forma se comprueba, y se rompe aquí.
    obj("16 · el error de la media deja de ser sd/raíz(n)",
        "datos", lambda d: d["m8"]["curva"][3].__setitem__("ee", 0.0031717171))
    obj("16 · la banda deja de ser la media ± 2 errores",
        "datos", lambda d: d["m8"]["curva"][3].__setitem__("hi", 0.5571717171))
    obj("16 · la cima publicada pasa a otra escala",
        "datos", lambda d: d["m8"]["forma"].__setitem__("cima_zonas", 50))
    obj("16 · un paso de la subida deja de medir 3 errores",
        "datos", lambda d: d["m8"]["curva"][5].update(
            media=0.5371717171, lo=0.5371717171 - 2 * d["m8"]["curva"][5]["ee"],
            hi=0.5371717171 + 2 * d["m8"]["curva"][5]["ee"]))
    obj("16 · la desviación deja de crecer al bajar de zonas",
        "datos", lambda d: d["m8"]["curva"][2].update(
            sd=0.0617171717, ee=0.0617171717 / 5000 ** 0.5))
    obj("16 · la razón de desviaciones cambia",
        "datos", lambda d: d["m8"]["forma"].__setitem__("razon_sd", 11.7171717171))
    obj("16 · la curva de 30 deja de ser la que se publicó",
        "datos", lambda d: d["m8"]["curva_30"][3].__setitem__("media", 0.5271717171))
    obj("16 · el bache de la curva de 30 pasa a medir 2 errores",
        "datos", lambda d: d["m8"]["forma_30"].__setitem__("z_bache_max", 2.1717171717))
    obj("16 · el módulo 9 se aparta de la curva del 8",
        "datos", lambda d: d["m9"]["contiguas"].__setitem__("media", 0.5171717171))

    # --- 14. Las fuentes citadas del módulo 11 ------------------------
    obj("14 · un caso histórico se queda sin fuente",
        "datos", lambda d: d["m11"]["casos_citados"][0].__setitem__("fuente", ""))

    return D


def main() -> int:
    return arnes("prueba_auditor_cap3.py — el arnés de inyección del capítulo 3",
                 PY, AUDITOR, SALIDAS, ARCHIVOS, defectos(),
                 "genera_cap3.R y genera_soluciones.R 3")


if __name__ == "__main__":
    sys.exit(main())
