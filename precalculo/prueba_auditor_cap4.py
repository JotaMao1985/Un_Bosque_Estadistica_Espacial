#!/usr/bin/env python3
"""
prueba_auditor_cap4.py — le rompe el precálculo al auditor y exige que lo cace

Material de Estadística Espacial 2026-II (20929). T3.1b.

POR QUÉ EXISTE. Un auditor que informa «0 fallos» la primera vez que corre
no ha demostrado nada: puede estar comprobando bien o puede estar
comprobando cosas incapaces de fallar. `audita_cap4.py` dio 390/0 en su
primera pasada limpia —después de cazar cuatro defectos reales—, y sin
este arnés esa cifra sería una promesa.

La maquinaria vive en `prueba_auditor_base.py`. Aquí solo se declara QUÉ
romper, que es lo único propio del capítulo.

LAS FAMILIAS DE DEFECTO. Cada una imita un fallo que ya ocurrió en este
proyecto o que este capítulo puede sufrir:

   1. cifra publicada que deja de cuadrar con la fuente primaria
   2. cifra derivada que deja de cuadrar con las que la generan
   3. relación cualitativa que se rompe (órdenes, monotonías, signos)
   4. BANDERA que deja de coincidir con el hecho que afirma   ← T1.1, regla 4
   5. propiedad TEÓRICA exacta violada (K = pi r², g = 1, p = 1/(nsim+1))
   6. la demostración del módulo 5, que se apoya en un chi2 IDÉNTICO
   7. una curva alterada en un solo nodo                       ← lo caza la
      reimplementación de K, no una comparación consigo misma
   8. caja, cuantización o contenido de un `.geomapa`          ← T0.3
   9. tilde convertida en bytes crudos <c3><b3>                ← T0.5
  10. flotante con más decimales de los declarados             ← T0.5
  11. solución de un ejercicio guiado alterada
  12. coherencia entre módulos rota
  13. el conteo de piezas y agujeros de la ventana             ← el defecto
      REAL que este auditor cazó: `partes` no eran partes

UNA INYECCIÓN NO PUEDE USAR UN VALOR QUE YA ESTÉ EN EL ARCHIVO. Si la
cifra falsa coincidiera con otra real, el auditor podría «cazarla» por el
motivo equivocado y el arnés se felicitaría solo. De ahí los valores con
pinta de matrícula: 0,1717171717 y 41,3131313131 no salen de ningún
cálculo de este capítulo.

Uso:  python3 precalculo/prueba_auditor_cap4.py
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
AUDITOR = PRECALCULO / "audita_cap4.py"

ARCHIVOS = {
    "datos": ("CAP4_DATOS", "cap4_datos.json"),
    "mapas": ("CAP4_MAPAS", "cap4_mapas.json"),
    "soluciones": ("CAP4_SOLUCIONES", "cap4_soluciones.json"),
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
    obj("1 · la lambda urbana deja de cuadrar con la ventana y las sedes",
        "datos", lambda d: d["m1"]["urbana"].__setitem__("lambda_km2", 5.7171717171))
    obj("1 · el área de la ventana urbana cambia",
        "datos", lambda d: d["m1"]["urbana"].__setitem__("area_km2", 371.3131313131))
    obj("1 · el perímetro de la ventana del D.C. cambia",
        "datos", lambda d: d["m1"]["dc"].__setitem__("perimetro_km", 313.1313131313))
    obj("1 · las sedes dentro del perímetro urbano cambian",
        "datos", lambda d: d["m1"]["urbana"].__setitem__("n", 2103))
    obj("1 · las sedes descartadas por caer fuera cambian",
        "datos", lambda d: d["m1"]["urbana"].__setitem__("fuera", 97))
    obj("1 · el total de sedes del GeoPackage cambia",
        "datos", lambda d: d["m1"].__setitem__("sedes_total", 2213))
    obj("1 · la distancia media al vecino de cells cambia",
        "datos", lambda d: d["m3"]["cells"].__setitem__("nn_media", 0.1313131313))
    obj("1 · la R de Clark-Evans de redwood cambia",
        "datos", lambda d: d["m3"]["redwood"].__setitem__("clark_evans", 0.7171717171))
    obj("1 · la R de Donnelly de swedishpines cambia",
        "datos", lambda d: d["m3"]["swedishpines"].__setitem__(
            "clark_evans_donnelly", 1.3131313131))
    obj("1 · el número de puntos de japanesepines cambia",
        "datos", lambda d: d["m3"]["japanesepines"].__setitem__("n", 67))
    obj("1 · las sedes coincidentes del módulo 7 cambian",
        "datos", lambda d: d["m7"]["bogota"].__setitem__("coincidentes", 83))
    obj("1 · el máximo de sedes en un mismo punto cambia",
        "datos", lambda d: d["m7"]["duplicados"].__setitem__("maximo_por_sitio", 4))
    obj("1 · las coordenadas repetidas cambian",
        "datos", lambda d: d["m7"]["duplicados"].__setitem__("repetidos", 47))

    # --- 13. Piezas y agujeros: EL defecto que este auditor cazó ------
    obj("13 · las piezas de la ventana urbana vuelven a ser las componentes",
        "datos", lambda d: d["m1"]["urbana"].__setitem__("piezas", 27))
    obj("13 · los agujeros de la ventana urbana cambian",
        "datos", lambda d: d["m1"]["urbana"].__setitem__("agujeros", 2))
    obj("13 · piezas y agujeros dejan de sumar las componentes",
        "datos", lambda d: d["m1"]["dc"].__setitem__("componentes_frontera", 4))

    # --- 2. Cifras derivadas que dejan de cuadrar ---------------------
    obj("2 · el factor entre las dos lambdas no sale de sus dos lambdas",
        "datos", lambda d: d["m1"].__setitem__("factor_lambda", 4.1717171717))
    obj("2 · el cociente de áreas no sale de sus dos áreas",
        "datos", lambda d: d["m1"].__setitem__("cociente_area", 4.3131313131))
    obj("2 · lambda en m² deja de ser la de km² entre un millón",
        "datos", lambda d: d["m2"].__setitem__("lambda_urbana_m2", 0.0000061717))
    obj("2 · el índice de dispersión no sale de su media y su varianza",
        "datos", lambda d: d["m2"]["urbana"].__setitem__("dispersion", 7.1717171717))
    obj("2 · el log10 del p-valor no corresponde al p-valor",
        "datos", lambda d: d["m2"]["urbana"].__setitem__("p_log10", -41.3131313131))
    obj("2 · el porcentaje de coincidentes no sale de su conteo",
        "datos", lambda d: d["m7"]["bogota"].__setitem__("coincidentes_pct", 4.1717171717))
    obj("2 · el máximo desvío de L no es el de su propia curva",
        "datos", lambda d: d["m8"]["redwood"].__setitem__("max_desvio", 0.1717171717))
    obj("2 · la r del máximo desvío no es la de su curva",
        "datos", lambda d: d["m8"]["cells"].__setitem__("r_max_desvio", 0.1313131313))
    obj("2 · la g máxima no es el máximo de su curva",
        "datos", lambda d: d["m9"]["redwood"].__setitem__("g_max", 4.1717171717))
    obj("2 · el sesgo máximo por no corregir no es el de las curvas",
        "datos", lambda d: d["m10"].__setitem__("sesgo_max_pct", 41.3131313131))
    obj("2 · la r del sesgo máximo no es la de las curvas",
        "datos", lambda d: d["m10"].__setitem__("r_sesgo_max", 4171.7171717171))
    obj("2 · las veces que la isotrópica supera a la traslación no cuadran",
        "datos", lambda d: d["m10"]["coste"].__setitem__(
            "veces_isotropica_sobre_traslacion", 417.1717171717))
    obj("2 · las horas de la envolvente isotrópica no salen de su tiempo",
        "datos", lambda d: d["m10"]["coste"].__setitem__(
            "horas_envolvente_isotropica", 41.3131313131))
    obj("2 · el porcentaje de salidas no sale de sus dos conteos",
        "datos", lambda d: d["m11"]["tasa_salida_bogota"].__setitem__("pct", 41.7171717171))
    obj("2 · los grados de libertad dejan de ser celdas menos una",
        "datos", lambda d: d["m2"]["urbana"].__setitem__("gl", 71))

    # --- 5. Propiedades teóricas exactas ------------------------------
    obj("5 · la K teórica deja de ser pi r²",
        "datos", lambda d: d["m8"]["cells"]["k_teo"].__setitem__(50, 0.1717171717))
    obj("5 · la g teórica deja de valer 1",
        "datos", lambda d: d["m9"]["cells"]["g_teo"].__setitem__(30, 1.1717171717))
    obj("5 · L deja de ser la raíz de K entre pi",
        "datos", lambda d: d["m8"]["redwood"]["l_obs"].__setitem__(40, 0.3131313131))
    obj("5 · L - r deja de corresponder a L y a r",
        "datos", lambda d: d["m8"]["japanesepines"]["l_menos_r"].__setitem__(
            60, 0.1717171717))
    obj("5 · el p mínimo deja de ser 1/(nsim+1)",
        "datos", lambda d: d["m11"].__setitem__("p_minimo", 0.0017171717))
    obj("5 · el nivel de la banda por defecto deja de ser 2/(nsim+1)",
        "datos", lambda d: d["m11"]["escala_nsim"][2].__setitem__(
            "nivel_defecto", 0.0317171717))
    obj("5 · el nrank que daría el 5 % deja de cuadrar con nsim",
        "datos", lambda d: d["m11"]["escala_nsim"][3].__setitem__(
            "nrank_para_5pct", 17.1717171717))
    obj("5 · chi² deja de ser la dispersión por los grados de libertad",
        "datos", lambda d: d["m2"]["japanesepines"].__setitem__("chi2", 31.3131313131))
    obj("5 · la G empírica en r=0 deja de ser la fracción de coincidentes",
        "datos", lambda d: d["m7"]["duplicados"].__setitem__(
            "g_empirica_en_cero", 0.0417171717))
    obj("5 · la G de Kaplan-Meier en r=0 deja de valer cero",
        "datos", lambda d: d["m7"]["duplicados"].__setitem__("g_km_en_cero", 0.0171717171))
    obj("5 · la curva teórica del histograma deja de ser la Poisson",
        "datos", lambda d: d["m4"]["hist_teorico"].__setitem__(10, 41.7171717171))
    obj("5 · el histograma deja de sumar las realizaciones",
        "datos", lambda d: d["m4"]["hist_obs"].__setitem__(5, 171))
    obj("5 · K en r=0 sin corregir deja de ser las parejas coincidentes",
        "datos", lambda d: d["m10"].__setitem__("k_cero_sin_corregir", 7171.7171717171))

    # --- 3. Relaciones cualitativas ----------------------------------
    obj("3 · los tres regímenes dejan de ordenarse",
        "datos", lambda d: d["m3"]["cells"].__setitem__("clark_evans", 0.9171717171))
    obj("3 · G deja de ser no decreciente",
        "datos", lambda d: d["m7"]["redwood"]["g_obs"].__setitem__(60, 0.0171717171))
    obj("3 · la banda por defecto deja de ensancharse con nsim",
        "datos", lambda d: d["m11"]["escala_nsim"][1].__setitem__(
            "ancho_defecto", 0.0917171717))
    obj("3 · a nivel fijo la banda deja de estrecharse",
        "datos", lambda d: d["m11"]["escala_nsim"][3].__setitem__(
            "ancho_5pct", 0.0717171717))
    obj("3 · sin corregir, K deja de quedar por debajo en algún r > 0",
        "datos", lambda d: [c for c in d["m10"]["correcciones"]
                           if c["correccion"] == "none"][0]["k"].__setitem__(
            80, 99171717.17))
    obj("3 · la g del agregado deja de superar a la del aleatorio",
        "datos", lambda d: d["m9"]["japanesepines"].__setitem__("g_max", 9.1717171717))
    obj("3 · la tasa de salida bajo CSR se parece al 5 %",
        "datos", lambda d: d["m11"]["tasa_salida_bogota"].__setitem__("fuera", 41))

    # --- 4. Banderas que dejan de coincidir con su hecho --------------
    obj("4 · la bandera «se sale de la banda» miente",
        "datos", lambda d: d["m11"]["bogota"].__setitem__("sale", 0))
    # La fila 0 de redwood (nx = 2) tiene p = 0,178 y NO rechaza, así que
    # poner ahí un 0 no cambiaba nada: el arnés se lo reprochó a sí mismo
    # como inyección inerte, que es exactamente para lo que existe esa
    # comprobación. Se afirma un rechazo donde el p-valor no lo permite.
    obj("4 · una bandera afirma rechazo con p = 0,178",
        "datos", lambda d: d["m6"]["redwood"]["rechaza"].__setitem__(0, 1))
    obj("4 · una bandera niega el rechazo con p minúsculo",
        "datos", lambda d: d["m6"]["redwood"]["rechaza"].__setitem__(3, 0))
    obj("4 · la bandera de «alcanza el 5 %» miente",
        "datos", lambda d: d["m11"]["escala_nsim"][0].__setitem__("alcanza_5pct", 1))
    obj("4 · la ventana de Bogotá se declara rectangular",
        "datos", lambda d: d["m3"]["bogota"].__setitem__("ventana_rectangular", 1))
    obj("4 · una ventana canónica se declara NO rectangular",
        "datos", lambda d: d["m3"]["cells"].__setitem__("ventana_rectangular", 0))
    obj("4 · la corrección declarada en la metainformación cambia",
        "datos", lambda d: d["meta"].__setitem__("correccion_envolventes", "isotropic"))
    obj("4 · un módulo declara una corrección que no es la del capítulo",
        "datos", lambda d: d["m9"]["bogota"].__setitem__("correccion", "isotropic"))

    # --- 6. La demostración del módulo 5 ------------------------------
    obj("6 · el rebarajado deja de conservar el conteo de una celda",
        "datos", lambda d: d["m5"]["x2"].__setitem__(0, 0.9171717171))
    obj("6 · los dos chi² del módulo 5 dejan de ser el mismo",
        "datos", lambda d: d["m5"]["rebarajado"].__setitem__("chi2", 64.7171717171))
    obj("6 · el chi² publicado deja de ser el de sus conteos",
        "datos", lambda d: (d["m5"]["original"].__setitem__("chi2", 61.3131313131),
                            d["m5"]["rebarajado"].__setitem__("chi2", 61.3131313131)))
    obj("6 · la distancia media al vecino del rebarajado cambia",
        "datos", lambda d: d["m5"].__setitem__("nn_rebarajado", 0.0717171717))
    obj("6 · rebarajar deja de separar a los vecinos",
        "datos", lambda d: d["m5"].__setitem__("nn_cociente", 1.0171717171))

    # --- 7. Curvas alteradas en un solo nodo --------------------------
    obj("7 · la K de cells cambia en un nodo interior",
        "datos", lambda d: d["m8"]["cells"]["k_obs"].__setitem__(50, 0.0717171717))
    obj("7 · la K de redwood cambia en un nodo interior",
        "datos", lambda d: d["m8"]["redwood"]["k_obs"].__setitem__(30, 0.0317171717))
    obj("7 · la K sin corregir de Bogotá cambia en un nodo",
        "datos", lambda d: [c for c in d["m10"]["correcciones"]
                           if c["correccion"] == "none"][0]["k"].__setitem__(
            40, 17171717.17))
    obj("7 · el suelo de la banda supera al techo en un nodo",
        "datos", lambda d: d["m11"]["redwood"]["lo"].__setitem__(50, 91.7171717171))

    # --- 12. Coherencia entre módulos ---------------------------------
    obj("12 · el módulo 10 describe otra ventana que el módulo 1",
        "datos", lambda d: d["m10"]["ventana"].__setitem__("piezas", 19))
    obj("12 · el nsim del módulo 11 no es el de la metainformación",
        "datos", lambda d: d["m11"].__setitem__("nsim", 499))
    obj("12 · una envolvente declara otro nsim que su módulo",
        "datos", lambda d: d["m11"]["japanesepines"].__setitem__("nsim", 499))
    obj("12 · el conteo de anclas del generador desaparece",
        "datos", lambda d: d["meta"].__setitem__("n_anclas", 3))
    obj("12 · dos semillas del capítulo se repiten",
        "datos", lambda d: d["meta"]["semillas"].__setitem__("ciego", 4026))
    obj("12 · una semilla repite la semilla global",
        "datos", lambda d: d["meta"]["semillas"].__setitem__("thomas", 2026))

    # --- 11. Las soluciones de los ejercicios -------------------------
    obj("11 · E1: el área de la envolvente convexa cambia",
        "soluciones", lambda s: s["e1"]["solucion"]["casco"].__setitem__(
            "area_km2", 1717.1717171717))
    obj("11 · E1: la envolvente convexa deja fuera sedes",
        "soluciones", lambda s: s["e1"]["solucion"].__setitem__("casco_deja_fuera", 17))
    obj("11 · E1: su lambda urbana deja de ser la del módulo 1",
        "soluciones", lambda s: s["e1"]["solucion"]["urbana"].__setitem__(
            "lambda_km2", 5.7171717171))
    obj("11 · E2: los dos chi² dejan de ser el mismo",
        "soluciones", lambda s: s["e2"]["solucion"]["rebarajado"].__setitem__(
            "chi2", 18.7171717171))
    obj("11 · E2: la caída de R no sale de sus dos R",
        "soluciones", lambda s: s["e2"]["solucion"].__setitem__("ce_cae", 0.3131313131))
    obj("11 · E4: el porcentaje de nodos fuera no sale de sus conteos",
        "soluciones", lambda s: s["e4"]["solucion"].__setitem__("pct_fuera", 41.7171717171))
    obj("11 · E4: sobre L deja de rechazar y se cae el giro del ejercicio",
        "soluciones", lambda s: s["e4"]["solucion"].__setitem__("dclf_L", 0.7171717171))
    obj("11 · E5: corregir el borde deja de bajar R",
        "soluciones", lambda s: s["e5"]["solucion"].__setitem__(
            "clark_evans_cdf", 0.9171717171))
    obj("11 · E5: Donnelly se declara disponible para una ventana poligonal",
        "soluciones", lambda s: s["e5"]["solucion"].__setitem__("donnelly_disponible", 1))
    obj("11 · E5: trabaja sobre otras sedes que el módulo 1",
        "soluciones", lambda s: s["e5"]["solucion"].__setitem__("n", 2071))
    obj("11 · un ejercicio se queda sin lectura",
        "soluciones", lambda s: s["e3"].__setitem__("lectura", ""))
    obj("11 · un ejercicio se queda sin pasos intermedios",
        "soluciones", lambda s: s["e2"].__setitem__("pasos", s["e2"]["pasos"][:2]))
    obj("11 · las soluciones dicen ser de otro capítulo",
        "soluciones", lambda s: s["meta"].__setitem__("capitulo", 5))

    # --- 8. Los mapas -------------------------------------------------
    obj("8 · el mapa urbano pinta otras tantas sedes",
        "mapas", lambda m: m["patron_urbano"].__setitem__("n", 2071))
    obj("8 · la caja de un mapa se desordena",
        "mapas", lambda m: m["redwood"].__setitem__(
            "caja", [1.0, 0.0, 0.0, -1.0]))
    obj("8 · la cuantización declarada de un mapa cambia",
        "mapas", lambda m: m["cells"].__setitem__("q", 1024))
    obj("8 · un mapa cambia de modo",
        "mapas", lambda m: m["japanesepines"].__setitem__("modo", "poligonos"))
    obj("8 · el contorno urbano se empalma en una sola polilínea",
        "mapas", lambda m: m["patron_urbano"].__setitem__(
            "lineas", [m["patron_urbano"]["lineas"][0]]))
    obj("8 · los dos patrones del módulo 5 dejan de tener los mismos puntos",
        "mapas", lambda m: m["ceguera_rebarajado"].__setitem__("n", 61))

    # --- 9 y 10. Formato ----------------------------------------------
    txt("9 · una tilde se convierte en bytes crudos",
        "datos", "Perímetro urbano", "PerÃ­metro urbano")
    obj("10 · un flotante pasa de los 10 decimales declarados",
        "datos", lambda d: d["m1"].__setitem__("factor_lambda", 4.21101234567891))
    obj("10 · se cuela un NaN en una curva",
        "datos", lambda d: d["m8"]["cells"]["k_obs"].__setitem__(
            50, float("nan")))

    return D


def main() -> int:
    return arnes("prueba_auditor_cap4.py — el arnés de inyección del capítulo 4",
                 PY, AUDITOR, SALIDAS, ARCHIVOS, defectos(),
                 "genera_cap4.R y genera_soluciones.R 4")


if __name__ == "__main__":
    sys.exit(main())
