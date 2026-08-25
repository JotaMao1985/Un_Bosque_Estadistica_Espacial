#!/usr/bin/env python3
"""
audita_cap4.py — auditoría independiente del precálculo del capítulo 4 (T3.1b)

Material de Estadística Espacial 2026-II (20929).

NO comprueba que los JSON existan: comprueba que sus NÚMEROS sean ciertos,
por caminos que no pasan por R ni por spatstat.

POR QUÉ EN PYTHON, y qué significa «independiente» AQUÍ. Es la lección de
A.10: un control que comparte el entorno con lo que audita no es un
control. En este capítulo la independencia es más fuerte que en ninguno
anterior, porque **la función K de Ripley se vuelve a implementar entera**:

  · las distancias entre puntos salen de scipy.spatial, no de spatstat;
  · el peso de la corrección de traslación se escribe AQUÍ con su fórmula
    cerrada para ventanas rectangulares —(a-|dx|)(b-|dy|)—, que es una
    segunda derivación de la misma matemática, no una llamada a la misma;
  · los conteos por cuadrante se binan aquí con el convenio de `cut()`,
    reproducido a mano;
  · las esperanzas de cada celda salen de recortar la celda contra la
    ventana con shapely;
  · la Poisson del módulo 4 la pone scipy.stats.

TRES CONVENIOS QUE SE FIJARON MIDIENDO, NO SUPONIENDO. Los tres se
probaron contra las cifras publicadas antes de escribir una línea de esto,
y cada uno costaba una auditoría entera de falsos fallos:

  1. LA NORMALIZACIÓN ES n(n-1), NO n². Con n² la K recalculada se separa
     un 2 % de la publicada en `cells` y en `redwood`; con n(n-1) coincide
     a 5e-6, que es el redondeo a 6 cifras significativas del JSON.
  2. SE CUENTA CON `<=`, NO CON `<`. Lo decide `cells`, que tiene una
     pareja a distancia exactamente igual a un nodo de la rejilla (r =
     0,125) y spatstat la INCLUYE: con `<` la K cae un 16 % en ese nodo.
  3. EL ÚLTIMO NODO ES OTRA HISTORIA. `japanesepines` tiene DOCE parejas
     a distancia exactamente r_max = 0,25 —sus coordenadas están a dos
     decimales— y ahí spatstat NO las cuenta, al revés que en los nodos
     interiores. En todos los demás nodos el acuerdo es de 4e-6; solo en
     ése se va al 1,5 %. No se disimula con una tolerancia ancha: el
     auditor DETECTA los empates exactos y salta ese nodo diciéndolo.

HASTA DÓNDE LLEGA LA INDEPENDENCIA, DECLARADO Y NO INSINUADO
  · TOTAL para K, las distancias al vecino más próximo, Clark-Evans, la G
    empírica, los cuadrantes, el chi2 y toda la aritmética.
  · PARCIAL para las áreas: GEOS es el MISMO motor en los dos lados
    (shapely y sf lo llaman igual). Se verifica el ANÁLISIS de lo que GEOS
    devolvió, no que GEOS acierte.
  · NULA para `pcf` (g) y para los estimadores Kaplan-Meier de G y F: son
    suavizados y estimadores de supervivencia con convenios internos de
    spatstat, y no hay segunda implementación. Lo que sí se comprueba son
    sus PROPIEDADES: que g teórica valga 1, que G empírica en r = 0 sea
    exactamente la fracción de puntos coincidentes, y que los resúmenes
    publicados correspondan a las curvas publicadas.
  · NULA para las envolventes: dependen del generador de números
    aleatorios de R. Se auditan sus PROPIEDADES —orden de la banda,
    niveles, p mínimo, monotonías que el capítulo afirma— y no sus valores.
  · NULA, y declarada dos veces, para los TIEMPOS del módulo 10: dependen
    de la máquina. Lo que se audita es la relación entre ellos.

Ejecutar con el Python de geo_env (el que tiene geopandas):
    "$(python3 -c 'import json;print(json.load(open("precalculo/versiones_py.json"))["ejecutable"])')" \\
        precalculo/audita_cap4.py
"""
from __future__ import annotations

import json
import math
import pathlib
import sys
import warnings

warnings.filterwarnings("ignore")

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from audita_base import (Auditoria, audita_geomapa, carga as _carga,
                         decimales, sin_nan)

import numpy as np
import pandas as pd
import geopandas as gpd
from scipy.spatial import cKDTree
from scipy.stats import poisson
from shapely.geometry import box

RAIZ = pathlib.Path(__file__).resolve().parent.parent
PRECALCULO = RAIZ / "precalculo"
SALIDAS = PRECALCULO / "salidas"
PROCESADO = RAIZ / "datos" / "procesado"

# El JSON publica las curvas con 6 cifras significativas, y K crece como
# r²: sobre una curva empinada, ese redondeo se amplifica. La tolerancia
# relativa de las curvas es 1e-4 por eso y no por comodidad; las cifras
# sueltas se exigen a 1e-6 como en el resto del proyecto.
TOL_CURVA = 1e-4


def carga(var: str, nombre: str):
    return _carga(var, nombre, SALIDAS)


# =====================================================================
# El convenio de celda de `cut()`, reproducido a mano
#
# `quadratcount()` bina con `cut()`: intervalos abiertos por la izquierda
# y cerrados por la derecha, con el más bajo cerrado por los dos lados.
# Reproducirlo aquí es lo que hace que este control sea un control: si se
# llamara a la misma función que el generador, no comprobaría nada.
# =====================================================================
def celda_cut(v, lo, hi, n):
    bordes = np.linspace(lo, hi, n + 1)
    idx = np.searchsorted(bordes, v, side="left") - 1
    idx = np.clip(idx, 0, n - 1)          # include.lowest para el borde bajo
    return idx


def conteos_rejilla(x, y, caja, nx, ny):
    """La matriz de conteos por celda, con el convenio de `cut()`."""
    ix = celda_cut(x, caja[0], caja[2], nx)
    iy = celda_cut(y, caja[1], caja[3], ny)
    m = np.zeros((nx, ny), dtype=int)
    np.add.at(m, (ix, iy), 1)
    return m


def areas_celdas(poligono, caja, nx, ny):
    """Área de cada celda RECORTADA contra la ventana, con shapely."""
    bx = np.linspace(caja[0], caja[2], nx + 1)
    by = np.linspace(caja[1], caja[3], ny + 1)
    a = np.zeros((nx, ny))
    for i in range(nx):
        for j in range(ny):
            a[i, j] = poligono.intersection(
                box(bx[i], by[j], bx[i + 1], by[j + 1])).area
    return a


def chi2_cuadrantes(obs, esp):
    ok = esp > 0
    return float(np.sum((obs[ok] - esp[ok]) ** 2 / esp[ok])), int(np.sum(ok))


# =====================================================================
# La K de Ripley, reimplementada
# =====================================================================
def k_traslacion_rect(x, y, caja, r_nodos, n_fino=513):
    """K con corrección de traslación sobre una ventana RECTANGULAR.

    El peso de traslación es el área de solape de la ventana consigo misma
    desplazada por el vector que une los dos puntos. Para un rectángulo
    a x b eso es exactamente (a-|dx|)(b-|dy|), sin integrar nada: es la
    fórmula cerrada, escrita aquí, no la de spatstat.

    Devuelve (K interpolada a r_nodos, empates exactos por nodo).
    """
    a = caja[2] - caja[0]
    b = caja[3] - caja[1]
    W = a * b
    n = len(x)
    dx = np.abs(x[:, None] - x[None, :])
    dy = np.abs(y[:, None] - y[None, :])
    dist = np.hypot(dx, dy)
    solape = np.clip(a - dx, 0, None) * np.clip(b - dy, 0, None)
    fuera_diag = ~np.eye(n, dtype=bool)
    d = dist[fuera_diag]
    w = 1.0 / solape[fuera_diag]
    orden = np.argsort(d)
    d, w = d[orden], w[orden]
    acum = np.concatenate([[0.0], np.cumsum(w)])
    r_fino = np.linspace(0, float(np.max(r_nodos)), n_fino)
    # `side="right"` es el `<=` del convenio 2 de la cabecera.
    K_fino = acum[np.searchsorted(d, r_fino, side="right")] / (n * (n - 1) / W ** 2)
    K = np.interp(r_nodos, r_fino, K_fino)
    empates = np.array([int(np.sum(d == rr)) for rr in r_nodos])
    return K, empates


def k_sin_correccion(x, y, area, r_nodos, n_fino=513):
    """K SIN corregir el borde: el conteo crudo de parejas.

    Con 2 107 puntos son 2,2 millones de parejas; el árbol k-d las cuenta
    sin materializar la matriz de distancias, que ocuparía 35 GB.
    """
    n = len(x)
    arbol = cKDTree(np.c_[x, y])
    r_fino = np.linspace(0, float(np.max(r_nodos)), n_fino)
    pares = arbol.count_neighbors(arbol, r_fino) - n     # quita la diagonal
    K_fino = pares * area / (n * (n - 1))
    return np.interp(r_nodos, r_fino, K_fino)


def clark_evans_ingenuo(x, y, area):
    n = len(x)
    arbol = cKDTree(np.c_[x, y])
    d, _ = arbol.query(np.c_[x, y], k=2)
    nn = d[:, 1]
    return float(np.mean(nn) / (0.5 / math.sqrt(n / area))), nn


def main() -> int:
    a = Auditoria("Precálculo del capítulo 4 verificado")
    D, p_datos = carga("CAP4_DATOS", "cap4_datos.json")
    M, p_mapas = carga("CAP4_MAPAS", "cap4_mapas.json")
    S, p_sol = carga("CAP4_SOLUCIONES", "cap4_soluciones.json")

    # -----------------------------------------------------------------
    a.titulo("1 · Los datos primarios, releídos con geopandas")
    # -----------------------------------------------------------------
    cole = gpd.read_file(PROCESADO / "bogota_colegios.gpkg")
    v_urb = gpd.read_file(PROCESADO / "bogota_ventana_urbana.gpkg")
    v_dc = gpd.read_file(PROCESADO / "bogota_ventana_dc.gpkg")
    a.igual(len(cole), D["m1"]["sedes_total"], "sedes leídas del GeoPackage")
    a.cierto(cole.crs.to_epsg() == 9377, "el CRS de las sedes es EPSG:9377",
             str(cole.crs.to_epsg()))

    w_urb = v_urb.union_all() if hasattr(v_urb, "union_all") else v_urb.unary_union
    w_dc = v_dc.union_all() if hasattr(v_dc, "union_all") else v_dc.unary_union
    XY = np.c_[cole.geometry.x.values, cole.geometry.y.values]

    a.salta("que GEOS acierte las áreas",
            "shapely y sf llaman al MISMO GEOS: aquí se audita el análisis, no el motor")

    for clave, w in (("urbana", w_urb), ("dc", w_dc)):
        pub = D["m1"][clave]
        a.cerca(w.area / 1e6, pub["area_km2"], f"m1/{clave}: área en km²", 1e-6)
        a.cerca(w.length / 1000, pub["perimetro_km"],
                f"m1/{clave}: perímetro en km", 1e-6)
        # PIEZAS Y AGUJEROS, POR SEPARADO. Esta comprobación falló la
        # primera vez y tenía razón: el generador publicaba
        # `length(owin$bdry)` bajo el nombre `partes`, y eso no son
        # piezas —son componentes de frontera, o sea piezas MÁS
        # agujeros—. Aquí las piezas las cuenta shapely y los agujeros
        # son los anillos interiores, que es la estructura explícita.
        piezas = list(w.geoms) if hasattr(w, "geoms") else [w]
        agujeros = sum(len(g.interiors) for g in piezas)
        a.igual(len(piezas), pub["piezas"], f"m1/{clave}: piezas disjuntas de la ventana")
        a.igual(agujeros, pub["agujeros"], f"m1/{clave}: agujeros de la ventana")
        a.igual(len(piezas) + agujeros, pub["componentes_frontera"],
                f"m1/{clave}: piezas y agujeros suman las componentes de frontera")
        # Los puntos dentro, con el criterio de shapely. Que coincida con
        # el de spatstat NO es trivial —son dos motores decidiendo qué es
        # «dentro»— y por eso se comprueba en vez de suponerse.
        dentro = gpd.GeoSeries(cole.geometry).covered_by(w).values
        a.igual(int(dentro.sum()), pub["n"], f"m1/{clave}: sedes dentro de la ventana")
        a.igual(len(cole) - int(dentro.sum()), pub["fuera"],
                f"m1/{clave}: sedes descartadas por caer fuera")
        a.cerca(int(dentro.sum()) / (w.area / 1e6), pub["lambda_km2"],
                f"m1/{clave}: lambda por km²", 1e-6)

    dentro_urb = gpd.GeoSeries(cole.geometry).covered_by(w_urb).values
    dentro_dc = gpd.GeoSeries(cole.geometry).covered_by(w_dc).values
    XU = XY[dentro_urb]
    A_URB = w_urb.area
    a.cerca(D["m1"]["urbana"]["lambda_km2"] / D["m1"]["dc"]["lambda_km2"],
            D["m1"]["factor_lambda"], "m1: el factor entre las dos lambdas", 1e-9)
    a.igual(int(dentro_dc.sum()) - int(dentro_urb.sum()), D["m1"]["diferencia_n"],
            "m1: cuántas sedes más caben en la ventana grande")
    a.cerca(w_dc.area / w_urb.area, D["m1"]["cociente_area"],
            "m1: cuántas veces más grande es la ventana del D.C.", 1e-9)
    # La afirmación del módulo, comprobada como afirmación y no como cifra:
    # el numerador apenas se mueve y el denominador se cuadruplica.
    a.cierto(D["m1"]["aumento_n_pct"] < 10 and D["m1"]["cociente_area"] > 4,
             "m1: n sube poco y el área se multiplica (la tesis del módulo)",
             f"n +{D['m1']['aumento_n_pct']:.1f} %, área x{D['m1']['cociente_area']:.2f}")

    # -----------------------------------------------------------------
    a.titulo("2 · Intensidad y cuadrantes, recontados con el convenio de cut()")
    # -----------------------------------------------------------------
    q = D["m2"]["urbana"]
    caja_u = np.array(w_urb.bounds)[[0, 1, 2, 3]]
    obs = conteos_rejilla(XU[:, 0], XU[:, 1], caja_u, q["nx"], q["ny"])
    a.igual(int(obs.sum()), q["n_obs"], "m2: los conteos suman las sedes de dentro")
    esp = areas_celdas(w_urb, caja_u, q["nx"], q["ny"]) / A_URB * int(obs.sum())
    # Las celdas que no tocan la ventana no son celdas: spatstat las
    # descarta y aquí también, o los grados de libertad no cuadran.
    vivas = esp > 0
    a.igual(int(vivas.sum()), q["celdas"], "m2: celdas que tocan la ventana")
    a.igual(int(vivas.sum()) - 1, q["gl"], "m2: grados de libertad = celdas - 1")
    chi2, _ = chi2_cuadrantes(obs[vivas], esp[vivas])
    a.cerca(chi2, q["chi2"], "m2: chi² del test de cuadrantes", 1e-3)
    a.igual(float(np.mean(obs[vivas])), q["media"], "m2: media de conteos por celda", 1e-6)
    a.cerca(float(np.var(obs[vivas], ddof=1)), q["var"], "m2: varianza de los conteos", 1e-6)
    a.cerca(float(np.var(obs[vivas], ddof=1) / np.mean(obs[vivas])), q["dispersion"],
            "m2: índice de dispersión = var/media", 1e-6)
    a.igual(int(np.sum(obs[vivas] == 0)), q["vacios"], "m2: celdas vacías")
    a.igual(int(np.max(obs[vivas])), q["maximo"], "m2: la celda más poblada")
    a.igual(int(np.sum(esp[vivas] < 5)), q["celdas_esperanza_baja"],
            "m2: celdas con esperanza < 5 (el supuesto que el módulo 5 discute)")
    a.cierto(q["p_valor"] > 0, "m2: el p-valor publicado no es cero",
             f"{q['p_valor']:.3g}")
    a.cerca(math.log10(q["p_valor"]), q["p_log10"], "m2: el log10 del p-valor", 1e-6)
    # Las tres unidades de la misma intensidad, que el módulo publica para
    # que el estudiante reconozca 5,7e-06 cuando lo calcule en m².
    # LA TOLERANCIA AQUÍ ES ABSOLUTA, y no por comodidad. El JSON redondea
    # a 10 DECIMALES, no a 10 cifras significativas, y lambda en m² vale
    # 5,7e-06: a diez decimales de eso solo sobreviven cinco cifras. Una
    # tolerancia relativa de 1e-9 exigiría una precisión que el propio
    # formato de publicación ya destruyó. Se comprueba contra el redondeo
    # que de verdad hay.
    a.igual(D["m2"]["lambda_urbana_km2"] / 1e6, D["m2"]["lambda_urbana_m2"],
            "m2: lambda en m² es la de km² dividida por 1e6", 1e-10)
    a.cerca(D["m2"]["lambda_urbana_km2"] / 100, D["m2"]["lambda_urbana_ha"],
            "m2: lambda en hectáreas", 1e-9)

    # La identidad exacta que el generador ancla: en celdas de ÁREA IGUAL,
    # el chi2 es el índice de dispersión por los grados de libertad. Vale
    # para japanesepines (cuadrado unidad) y no para Bogotá.
    qj = D["m2"]["japanesepines"]
    a.cerca(qj["dispersion"] * qj["gl"], qj["chi2"],
            "m2: chi² = dispersión x gl en celdas de igual área", 1e-6)
    a.cierto(abs(q["dispersion"] * q["gl"] - q["chi2"]) > 1e-6,
             "m2: y NO vale sobre la ventana urbana, cuyas celdas no son iguales",
             f"{q['dispersion'] * q['gl']:.2f} contra {q['chi2']:.2f}")

    # -----------------------------------------------------------------
    a.titulo("3 · Los tres regímenes, con las distancias de scipy")
    # -----------------------------------------------------------------
    reg = pd.read_csv(SALIDAS / "cap4_regimenes.csv")
    a.salta("que R leyera bien spatstat.data",
            "las coordenadas canónicas vienen del CSV que escribió R; aquí se audita "
            "la matemática sobre ellas, no la lectura del paquete")
    # CUATRO en el módulo 3 y TRES con curva. `swedishpines` publica
    # cifras y no tiene mapa ni funciones de resumen; separarlos evita
    # auditar lo que no existe y, sobre todo, evita NO auditar lo que sí:
    # hasta que el arnés lo señaló, swedishpines no lo miraba nadie.
    CANON = ("cells", "japanesepines", "redwood", "swedishpines")
    CON_CURVA = ("cells", "japanesepines", "redwood")
    for nm in CANON:
        d = reg[reg.patron == nm]
        pub = D["m3"][nm]
        x, y = d.x.values, d.y.values
        a.igual(len(x), pub["n"], f"m3/{nm}: número de puntos")
        v = pub["ventana"]
        a.cerca((v[2] - v[0]) * (v[3] - v[1]), pub["area"],
                f"m3/{nm}: el área es la de su ventana rectangular", 1e-9)
        a.cierto(pub["ventana_rectangular"] == 1,
                 f"m3/{nm}: la ventana es un rectángulo")
        a.cerca(2 * ((v[2] - v[0]) + (v[3] - v[1])), pub["perimetro"],
                f"m3/{nm}: perímetro del rectángulo", 1e-9)
        a.cierto(x.min() >= v[0] and x.max() <= v[2] and
                 y.min() >= v[1] and y.max() <= v[3],
                 f"m3/{nm}: todos los puntos caen dentro de la ventana publicada")
        ce, nn = clark_evans_ingenuo(x, y, pub["area"])
        a.cerca(float(np.mean(nn)), pub["nn_media"], f"m3/{nm}: distancia media al vecino")
        a.cerca(float(np.std(nn, ddof=1)), pub["nn_sd"], f"m3/{nm}: desviación de esa distancia")
        a.cerca(float(np.min(nn)), pub["nn_min"], f"m3/{nm}: la menor")
        a.cerca(float(np.max(nn)), pub["nn_max"], f"m3/{nm}: la mayor")
        a.cerca(0.5 / math.sqrt(len(x) / pub["area"]), pub["nn_esperada"],
                f"m3/{nm}: la distancia que daría el azar, 1/(2 raíz de lambda)")
        a.cerca(ce, pub["clark_evans"], f"m3/{nm}: R de Clark-Evans ingenuo")
        # Donnelly, escrito aquí con su fórmula: es la tercera vez que se
        # escribe en el proyecto (R, el capítulo 1 y esto) y las tres tienen
        # que coincidir o alguna transcribió mal el 0,0412.
        n_, ar = len(x), pub["area"]
        den = (0.5 * math.sqrt(ar / n_) +
               (0.0514 + 0.0412 / math.sqrt(n_)) * pub["perimetro"] / n_)
        a.cerca(float(np.mean(nn)) / den, pub["clark_evans_donnelly"],
                f"m3/{nm}: R con la corrección de Donnelly")

    ce_bog, nn_bog = clark_evans_ingenuo(XU[:, 0], XU[:, 1], A_URB)
    a.cerca(ce_bog, D["m3"]["bogota"]["clark_evans"], "m3/bogota: R de Clark-Evans")
    a.cierto(D["m3"]["bogota"]["ventana_rectangular"] == 0,
             "m3/bogota: su ventana NO es un rectángulo")
    a.cierto(D["m3"]["swedishpines"]["clark_evans"] > 1,
             "m3/swedishpines: es regular, como el módulo afirma",
             f"{D['m3']['swedishpines']['clark_evans']:.4f}")
    a.cierto(D["m3"]["cells"]["clark_evans"] > 1 > D["m3"]["redwood"]["clark_evans"],
             "m3: los regímenes se ordenan como el módulo afirma",
             f"cells {D['m3']['cells']['clark_evans']:.4f} > 1 > "
             f"redwood {D['m3']['redwood']['clark_evans']:.4f}")

    # -----------------------------------------------------------------
    a.titulo("4 · CSR: la Poisson, con scipy")
    # -----------------------------------------------------------------
    m4 = D["m4"]
    a.igual(len(m4["hist_k"]), len(m4["hist_obs"]), "m4: el histograma tiene tantas alturas como valores")
    a.igual(int(np.sum(m4["hist_obs"])), m4["n_realizaciones"],
            "m4: el histograma suma las realizaciones simuladas")
    teo = poisson.pmf(np.array(m4["hist_k"]), m4["lambda"]) * m4["n_realizaciones"]
    a.cierto(float(np.max(np.abs(teo - np.array(m4["hist_teorico"])))) < 1e-4,
             "m4: la curva teórica publicada es la Poisson de scipy",
             f"máxima diferencia {float(np.max(np.abs(teo - np.array(m4['hist_teorico'])))):.2e}")
    # Las dos propiedades de Poisson que el módulo enseña.
    a.cierto(abs(m4["conteo_media"] - m4["lambda"]) < 0.6,
             "m4: la media del conteo es lambda|W|", f"{m4['conteo_media']:.3f}")
    a.cierto(abs(m4["conteo_var"] - m4["lambda"]) < 3.5,
             "m4: la varianza también, que es la firma de Poisson",
             f"{m4['conteo_var']:.3f}")
    R = m4["R_csr"]
    a.igual(R["bajo_1"] + R["sobre_1"], R["n"],
            "m4: las R por debajo y por encima de 1 suman todas")
    a.cierto(R["min"] < 0.9 and R["max"] > 1.1,
             "m4: el azar puro llega a R lejos de 1 por los dos lados",
             f"[{R['min']:.4f}, {R['max']:.4f}]")
    a.cierto(R["q025"] > R["min"] and R["q975"] < R["max"],
             "m4: el intervalo central queda dentro del recorrido")
    for i, z in enumerate(m4["realizaciones"]):
        a.igual(len(z["x"]), z["n"], f"m4: la realización {i+1} publica tantas x como puntos")
        a.igual(len(z["y"]), z["n"], f"m4: y tantas y como puntos")

    # -----------------------------------------------------------------
    a.titulo("5 · La ceguera del chi², rehecha desde las coordenadas publicadas")
    # -----------------------------------------------------------------
    m5 = D["m5"]
    v_red = D["m3"]["redwood"]["ventana"]
    x1, y1 = np.array(m5["x1"]), np.array(m5["y1"])
    x2, y2 = np.array(m5["x2"]), np.array(m5["y2"])
    a.igual(len(x1), m5["n"], "m5: el patrón original publica n coordenadas")
    a.igual(len(x2), m5["n"], "m5: el rebarajado publica las mismas")
    c1 = conteos_rejilla(x1, y1, v_red, m5["nx"], m5["nx"])
    c2 = conteos_rejilla(x2, y2, v_red, m5["nx"], m5["nx"])
    # LA COMPROBACIÓN QUE SOSTIENE EL MÓDULO. No se compara el chi2: se
    # comparan los CONTEOS celda a celda, que es lo que la rebaraja
    # promete conservar. Dos vectores distintos pueden dar chi2 parecidos.
    a.cierto(np.array_equal(c1, c2),
             "m5: el rebarajado conserva EXACTAMENTE el conteo de cada celda",
             f"difieren en {int(np.sum(c1 != c2))} celdas")

    # LOS 25 CONTEOS PUBLICADOS, uno a uno contra este recuento (T3.3).
    #
    # El capítulo los saca a la tabla de respaldo del mapa: para quien no
    # ve los dos lienzos, esa tabla ES el módulo, así que sus cifras
    # necesitan el mismo control que las de la prosa. Hasta aquí el
    # auditor comprobaba que c1 y c2 coinciden ENTRE SÍ, que es otra cosa:
    # los dos podrían coincidir y ninguno ser el reparto que el JSON
    # publica.
    #
    # ORIENTACIÓN, que es donde esto se rompe si se rompe: el JSON publica
    # las filas de ARRIBA ABAJO —el orden en que `quadratcount()` las
    # imprime y en que se ven en el mapa— mientras que `conteos_rejilla`
    # indexa [ix, iy] con iy creciendo HACIA ARRIBA. La fila k de arriba
    # es, por tanto, iy = ny - 1 - k. Comparar sin darle la vuelta pasaría
    # sobre una matriz simétrica y fallaría sobre cualquier otra.
    cel = m5["celdas"]
    ny5 = cel["ny"]
    a.igual(len(cel["original"]), ny5, "m5: la tabla publica ny filas")
    a.igual(len(cel["columnas_x"]), cel["nx"], "m5: y nx columnas")
    pub1 = np.array([[cel["original"][k][i] for i in range(cel["nx"])]
                     for k in range(ny5)])
    pub2 = np.array([[cel["rebarajado"][k][i] for i in range(cel["nx"])]
                     for k in range(ny5)])
    rec = np.array([[int(c1[i, ny5 - 1 - k]) for i in range(cel["nx"])]
                    for k in range(ny5)])
    a.cierto(np.array_equal(pub1, rec),
             "m5: los 25 conteos publicados son los del recuento independiente",
             f"difieren en {int(np.sum(pub1 != rec))} celdas")
    a.cierto(np.array_equal(pub2, rec),
             "m5: y los del rebarajado, los mismos",
             f"difieren en {int(np.sum(pub2 != rec))} celdas")
    a.igual(int(pub1.sum()), m5["n"], "m5: los 25 conteos suman los puntos del patrón")
    esp5 = np.full(c1.shape, c1.sum() / c1.size)
    chi5, _ = chi2_cuadrantes(c1.ravel(), esp5.ravel())
    a.cerca(chi5, m5["original"]["chi2"], "m5: chi² del original, recalculado", 1e-6)
    a.cerca(chi5, m5["rebarajado"]["chi2"], "m5: y el del rebarajado es el mismo", 1e-6)
    a.igual(m5["original"]["chi2"], m5["rebarajado"]["chi2"],
            "m5: los dos chi² publicados coinciden hasta el último decimal", 1e-9)
    # Y lo que sí los separa.
    arb1 = cKDTree(np.c_[x1, y1]); arb2 = cKDTree(np.c_[x2, y2])
    nn1 = arb1.query(np.c_[x1, y1], k=2)[0][:, 1]
    nn2 = arb2.query(np.c_[x2, y2], k=2)[0][:, 1]
    a.cerca(float(np.mean(nn1)), m5["nn_original"], "m5: distancia media al vecino, original")
    a.cerca(float(np.mean(nn2)), m5["nn_rebarajado"], "m5: la del rebarajado")
    a.cerca(float(np.mean(nn2) / np.mean(nn1)), m5["nn_cociente"], "m5: su cociente")
    a.cierto(m5["nn_cociente"] > 1.2,
             "m5: rebarajar separa a los vecinos de forma apreciable",
             f"x{m5['nn_cociente']:.2f}")

    # -----------------------------------------------------------------
    a.titulo("6 · El barrido del tamaño de cuadrante")
    # -----------------------------------------------------------------
    m6 = D["m6"]
    for clave in ("redwood", "japanesepines", "bogota"):
        b = m6[clave]
        n_filas = len(b["nx"])
        a.igual(n_filas, len(m6["nxs"]), f"m6/{clave}: una fila por tamaño barrido")
        for campo in ("celdas", "chi2", "gl", "p_valor", "dispersion", "rechaza"):
            a.igual(len(b[campo]), n_filas, f"m6/{clave}: la columna `{campo}` está completa")
        a.cierto(all(b["gl"][i] == b["celdas"][i] - 1 for i in range(n_filas)),
                 f"m6/{clave}: los grados de libertad son celdas - 1")
        a.cierto(all((b["p_valor"][i] < 0.05) == (b["rechaza"][i] == 1)
                     for i in range(n_filas)),
                 f"m6/{clave}: la bandera de rechazo corresponde a su p-valor")
        a.cierto(all(b["celdas"][i] <= m6["nxs"][i] ** 2 for i in range(n_filas)),
                 f"m6/{clave}: nunca hay más celdas vivas que celdas de la rejilla")
    # La afirmación del módulo: al afinar la celda se rompe el supuesto.
    b = m6["redwood"]
    primera = next((m6["nxs"][i] for i in range(len(b["nx"]))
                    if b["celdas_esperanza_baja"][i] > 0), None)
    a.igual(primera, m6["redwood_nx_esperanza_baja"],
            "m6: el primer tamaño con esperanza < 5 es el publicado")
    a.igual(sum(b["rechaza"]), m6["redwood_rechazos"], "m6: el conteo de rechazos de redwood")

    # -----------------------------------------------------------------
    a.titulo("7 · G y F: el átomo de los duplicados")
    # -----------------------------------------------------------------
    m7 = D["m7"]
    dup = m7["duplicados"]
    XU_t = [tuple(p) for p in np.round(XU, 6)]
    unicos = len(set(XU_t))
    a.igual(len(XU_t) - unicos, dup["repetidos"],
            "m7: coordenadas repetidas contadas con python puro")
    arb = cKDTree(XU)
    nn_u = arb.query(XU, k=2)[0][:, 1]
    a.igual(int(np.sum(nn_u == 0)), dup["implicados"],
            "m7: sedes con un vecino a distancia cero")
    a.igual(int(np.sum(nn_u == 0)), m7["bogota"]["coincidentes"],
            "m7: y el módulo publica ese mismo número")
    from collections import Counter
    a.igual(max(Counter(XU_t).values()), dup["maximo_por_sitio"],
            "m7: el máximo de sedes en un mismo punto")
    # LA IDENTIDAD DEL MÓDULO: la G empírica en r = 0 ES la fracción de
    # puntos coincidentes. Es exacta, así que se exige exacta.
    a.cerca(float(np.mean(nn_u == 0)), dup["g_empirica_en_cero"],
            "m7: G empírica en r=0 = fracción de puntos coincidentes", 1e-6)
    a.igual(dup["g_km_en_cero"], 0.0,
            "m7: y el estimador de Kaplan-Meier la pone a cero por convenio")
    a.cerca(100 * float(np.mean(nn_u == 0)), m7["bogota"]["coincidentes_pct"],
            "m7: el porcentaje de coincidentes", 1e-6)
    a.salta("los estimadores km de G y F",
            "son estimadores de supervivencia con convenio interno de spatstat; "
            "no hay segunda implementación. Se audita la G empírica, que sí es exacta")
    for nm in ("cells", "japanesepines", "redwood", "bogota"):
        g = m7[nm]
        a.igual(len(g["r_g"]), len(g["g_obs"]), f"m7/{nm}: la curva G tiene una r por valor")
        a.igual(len(g["r_f"]), len(g["f_obs"]), f"m7/{nm}: y la F también")
        a.cierto(all(g["g_obs"][i] <= g["g_obs"][i + 1] + 1e-9
                     for i in range(len(g["g_obs"]) - 1)),
                 f"m7/{nm}: G no decrece (es una función de distribución)")
        a.cierto(g["g_obs"][-1] <= 1.0 + 1e-9, f"m7/{nm}: G no pasa de 1")
        a.cierto(0 <= g["g_mediana"], f"m7/{nm}: la mediana de la distancia al vecino es positiva")

    # -----------------------------------------------------------------
    a.titulo("8 · K de Ripley, reimplementada")
    # -----------------------------------------------------------------
    a.cierto(D["meta"]["correccion_envolventes"] == "translate",
             "la corrección declarada en el dato es la de traslación (decisión 1)")
    for nm in CON_CURVA:
        d = reg[reg.patron == nm]
        pub = D["m8"][nm]
        v = D["m3"][nm]["ventana"]
        r = np.array(pub["r"])
        K, empates = k_traslacion_rect(d.x.values, d.y.values, v, r)
        # El último nodo, aparte: si hay parejas a esa distancia exacta,
        # spatstat NO las cuenta y este control sí, así que se salta
        # DICIÉNDOLO en vez de ensanchar la tolerancia hasta que pase.
        n_comp = len(r) - 1 if empates[-1] > 0 else len(r)
        if empates[-1] > 0:
            a.salta(f"m8/{nm}: el último nodo de K (r = {r[-1]:g})",
                    f"hay {empates[-1]} parejas a esa distancia EXACTA y el convenio de "
                    f"empate del último nodo difiere; los otros {n_comp} nodos sí se comparan")
        err = float(np.max(np.abs(K[:n_comp] - np.array(pub["k_obs"][:n_comp])) /
                           np.maximum(np.abs(pub["k_obs"][:n_comp]), 1e-12)))
        a.cierto(err < TOL_CURVA,
                 f"m8/{nm}: K con corrección de traslación, reimplementada",
                 f"error relativo máximo {err:.2e} en {n_comp} nodos")
        # K teórica ES pi r², exacto.
        a.cierto(float(np.max(np.abs(np.array(pub["k_teo"]) - math.pi * r ** 2))) < 1e-5,
                 f"m8/{nm}: la K teórica publicada es pi r²")
        # L = raíz(K/pi), y L - r, exactos sobre lo publicado.
        L = np.sqrt(np.array(pub["k_obs"]) / math.pi)
        a.cierto(float(np.max(np.abs(L - np.array(pub["l_obs"])))) < 1e-4,
                 f"m8/{nm}: L es la raíz de K/pi")
        a.cierto(float(np.max(np.abs(L - r - np.array(pub["l_menos_r"])))) < 1e-4,
                 f"m8/{nm}: L - r corresponde a L y a r")
        i = int(np.argmax(np.abs(np.array(pub["l_menos_r"]))))
        a.cerca(abs(pub["l_menos_r"][i]), pub["max_desvio"],
                f"m8/{nm}: el máximo desvío publicado es el de su curva", 1e-6)
        a.cerca(r[i], pub["r_max_desvio"], f"m8/{nm}: y la r en que ocurre", 1e-6)

    # -----------------------------------------------------------------
    a.titulo("9 · La correlación de pares g(r)")
    # -----------------------------------------------------------------
    a.salta("la estimación de g(r)",
            "`pcf` es un suavizado por núcleo con ancho de banda y convenios internos "
            "de spatstat; no hay segunda implementación. Se auditan sus propiedades")
    for nm in ("cells", "japanesepines", "redwood", "bogota"):
        g = D["m9"][nm]
        a.igual(len(g["r"]), len(g["g_obs"]), f"m9/{nm}: la curva tiene una r por valor")
        a.cierto(all(abs(v - 1.0) < 1e-12 for v in g["g_teo"]),
                 f"m9/{nm}: g teórica vale 1 en todo r (es la definición de CSR)")
        a.cerca(max(g["g_obs"][1:]), g["g_max"],
                f"m9/{nm}: la g máxima publicada es la de su curva", 1e-6)
        a.cierto(g["correccion"] == "translate", f"m9/{nm}: declara la corrección usada")
    a.cierto(D["m9"]["redwood"]["g_max"] > D["m9"]["japanesepines"]["g_max"],
             "m9: el patrón agregado tiene la g más alta que el aleatorio")

    # -----------------------------------------------------------------
    a.titulo("10 · Efectos de borde")
    # -----------------------------------------------------------------
    m10 = D["m10"]
    r10_ = np.array(m10["r"])
    corr = {c["correccion"]: c for c in m10["correcciones"]}
    a.cierto(set(corr) == {"none", "border", "translate", "isotropic"},
             "m10: están las cuatro correcciones", str(sorted(corr)))
    # LA K SIN CORREGIR SE RECALCULA ENTERA sobre las 2 107 sedes: es el
    # conteo crudo de parejas, y ahí no hay convenio de borde que valga.
    K_un = k_sin_correccion(XU[:, 0], XU[:, 1], A_URB, r10_)
    err = float(np.nanmax(np.abs(K_un[1:] - np.array(corr["none"]["k"][1:])) /
                          np.maximum(np.abs(corr["none"]["k"][1:]), 1e-12)))
    a.cierto(err < TOL_CURVA,
             "m10: la K SIN corregir, recontada con un árbol k-d sobre 2,2 millones de parejas",
             f"error relativo máximo {err:.2e}")
    # La dirección del sesgo: sin corregir SIEMPRE por debajo. Es la
    # afirmación del módulo y se comprueba nodo a nodo, no de media.
    kn = np.array(corr["none"]["k"]); kt = np.array(corr["translate"]["k"])
    # EN r > 0, y el «> 0» lo puso esta comprobación al fallar. En r = 0
    # la K sin corregir NO vale cero: vale lo que aportan las parejas a
    # distancia exactamente cero, que son las 79 sedes coincidentes del
    # módulo 7. El átomo de los duplicados se cuela también en K, y ahí
    # la desigualdad se invierte por un motivo que es material del
    # capítulo, no un defecto.
    a.cierto(bool(np.all(kn[1:] <= kt[1:] + 1e-9)),
             "m10: para r > 0, K sin corregir queda por debajo de la corregida en TODOS los nodos",
             f"nodos incumplidos: {int(np.sum(kn[1:] > kt[1:] + 1e-9))}")
    a.igual(kn[0], m10["k_cero_sin_corregir"],
            "m10: la K sin corregir en r = 0 es la publicada")
    a.igual(kt[0], m10["k_cero_traslacion"], "m10: y la corregida vale cero ahí")
    a.cierto(m10["k_cero_sin_corregir"] > 0,
             "m10: el átomo de los duplicados asoma en K, igual que en G",
             f"K(0) sin corregir = {m10['k_cero_sin_corregir']:g}")
    # Y la identidad que lo cierra: ese K(0) son exactamente las parejas
    # coincidentes, con la normalización del estimador.
    n_u = len(XU)
    pares_cero = int(np.sum(cKDTree(XU).count_neighbors(cKDTree(XU), 0.0)) - n_u)
    a.cerca(pares_cero * A_URB / (n_u * (n_u - 1)), m10["k_cero_sin_corregir"],
            "m10: y ese valor son las parejas a distancia cero, recontadas", TOL_CURVA)
    i = int(np.argmax((kt - kn) / np.maximum(kt, 1e-9)))
    a.cerca(100 * (kt[i] - kn[i]) / kt[i], m10["sesgo_max_pct"],
            "m10: el sesgo máximo publicado es el de las curvas publicadas", 1e-4)
    a.cerca(r10_[i], m10["r_sesgo_max"], "m10: y la r en que ocurre", 1e-4)
    a.igual(m10["ventana"]["piezas"], D["m1"]["urbana"]["piezas"],
            "m10: la ventana que describe es la misma del módulo 1")
    a.igual(m10["ventana"]["componentes_frontera"],
            D["m1"]["urbana"]["componentes_frontera"],
            "m10: y con las mismas componentes de frontera")
    a.igual(m10["ventana"]["vertices"], D["m1"]["urbana"]["vertices"],
            "m10: y con los mismos vértices")
    # LOS TIEMPOS: no reproducibles, declarados dos veces.
    a.salta("los segundos que tarda cada corrección",
            "dependen de la máquina; no son reproducibles por naturaleza. Se audita "
            "la RELACIÓN entre ellos, que es lo que el capítulo afirma")
    coste = m10["coste"]
    t_iso = corr["isotropic"]["segundos"]; t_tr = corr["translate"]["segundos"]
    a.cierto(t_iso > t_tr, "m10: la isotrópica es más cara que la de traslación",
             f"{t_iso:.1f} s contra {t_tr:.2f} s")
    a.cerca(t_iso / t_tr, coste["veces_isotropica_sobre_traslacion"],
            "m10: cuántas veces más cara, contra los tiempos publicados", 1e-4)
    a.cerca(t_iso * D["meta"]["nsim_envolventes"] / 3600,
            coste["horas_envolvente_isotropica"],
            "m10: las horas que costaría una envolvente isotrópica", 1e-4)
    a.cerca(t_tr * D["meta"]["nsim_envolventes"] / 60,
            coste["minutos_envolvente_traslacion"],
            "m10: los minutos que cuesta con traslación", 1e-4)
    a.cierto(coste["veces_isotropica_sobre_traslacion"] > 50,
             "m10: la diferencia de coste es de dos órdenes de magnitud (la decisión 1)",
             f"x{coste['veces_isotropica_sobre_traslacion']:.0f}")

    # -----------------------------------------------------------------
    a.titulo("11 · Envolventes: propiedades, no valores")
    # -----------------------------------------------------------------
    a.salta("los valores de las envolventes",
            "salen del generador de números aleatorios de R y no hay forma de "
            "reproducirlos desde Python. Se auditan sus propiedades")
    m11 = D["m11"]
    a.cerca(1 / (m11["nsim"] + 1), m11["p_minimo"],
            "m11: el p mínimo alcanzable es 1/(nsim+1)", 1e-9)
    a.igual(m11["nsim"], D["meta"]["nsim_envolventes"],
            "m11: el nsim del módulo es el declarado en la metainformación")
    for nm in ("bogota", "redwood", "japanesepines"):
        e = m11[nm]
        lo, hi, obs = np.array(e["lo"]), np.array(e["hi"]), np.array(e["obs"])
        a.igual(len(lo), len(hi), f"m11/{nm}: la banda tiene tantos suelos como techos")
        a.cierto(bool(np.all(lo <= hi + 1e-12)),
                 f"m11/{nm}: el suelo de la banda nunca supera al techo")
        sale = bool(np.any((obs < lo - 1e-9) | (obs > hi + 1e-9)))
        a.igual(int(sale), e["sale"],
                f"m11/{nm}: la bandera «se sale» corresponde a la curva y a la banda")
        a.cierto(e["correccion"] == "translate", f"m11/{nm}: declara su corrección")
        a.igual(e["nsim"], m11["nsim"], f"m11/{nm}: declara su nsim")
    # LA CIFRA DEL MÓDULO: la tasa de salida bajo CSR no se parece al 5 %.
    for clave in ("tasa_salida_bogota", "tasa_salida_redwood"):
        ts = m11[clave]
        a.cerca(100 * ts["fuera"] / ts["nsim"], ts["pct"],
                f"m11: {clave} es el porcentaje de sus propios conteos", 1e-6)
        a.cierto(ts["fuera"] <= ts["nsim"], f"m11: {clave} no cuenta más salidas que simulaciones")
    a.cierto(m11["tasa_salida_bogota"]["pct"] > 20,
             "m11: bajo CSR, la banda puntual al 95 % la cruza muchísimo más del 5 %",
             f"{m11['tasa_salida_bogota']['pct']:.1f} %")
    # La escala de nsim, y las dos afirmaciones opuestas del módulo.
    esc = m11["escala_nsim"]
    for z in esc:
        a.cerca(2 / (z["nsim"] + 1), z["nivel_defecto"],
                f"m11/nsim={z['nsim']}: el nivel de la banda por defecto es 2/(nsim+1)", 1e-9)
        a.cerca((z["nsim"] + 1) * 0.05 / 2, z["nrank_para_5pct"],
                f"m11/nsim={z['nsim']}: el nrank que daría el 5 %", 1e-9)
        a.cerca(2 * z["nrank_usado"] / (z["nsim"] + 1), z["nivel_real"],
                f"m11/nsim={z['nsim']}: el nivel que de verdad se consigue", 1e-9)
        a.cerca(1 / (z["nsim"] + 1), z["p_minimo"],
                f"m11/nsim={z['nsim']}: su p mínimo", 1e-9)
        a.igual(int(abs(z["nivel_real"] - 0.05) < 0.005), z["alcanza_5pct"],
                f"m11/nsim={z['nsim']}: la bandera de alcanzable corresponde a su nivel")
    anchos_def = [z["ancho_defecto"] for z in esc]
    a.cierto(all(anchos_def[i] < anchos_def[i + 1] for i in range(len(anchos_def) - 1)),
             "m11: a nrank = 1 la banda SE ENSANCHA con nsim (lo contrario de lo que se supone)",
             str([round(v, 5) for v in anchos_def]))
    alc = [z for z in esc if z["alcanza_5pct"] == 1]
    a.cierto(len(alc) >= 2, "m11: al menos dos nsim del barrido alcanzan el 5 %")
    anchos5 = [z["ancho_5pct"] for z in alc]
    a.cierto(all(anchos5[i] >= anchos5[i + 1] for i in range(len(anchos5) - 1)),
             "m11: a nivel FIJO la banda se estrecha, que es la dirección contraria",
             str([round(v, 5) for v in anchos5]))
    a.cierto(esc[0]["alcanza_5pct"] == 0,
             "m11: con 19 simulaciones la banda al 5 % no existe (nrank tendría que ser 0,5)",
             f"nrank necesario {esc[0]['nrank_para_5pct']}")
    tg = m11["test_global"]
    for k, v in tg.items():
        a.cierto(0 < v <= 1, f"m11: el p-valor de {k} está en (0, 1]", str(v))
        a.cierto(v >= m11["p_minimo"] - 1e-12,
                 f"m11: {k} no baja del p mínimo que permite nsim", str(v))

    # -----------------------------------------------------------------
    a.titulo("12 · Los cinco ejercicios")
    # -----------------------------------------------------------------
    a.igual(S["meta"]["n_ejercicios"], 5, "las soluciones traen cinco ejercicios")
    a.igual(S["meta"]["capitulo"], 4, "y dicen ser del capítulo 4")
    a.cierto(all(f"e{i}" in S for i in range(1, 6)), "están E1 a E5")
    for i in range(1, 6):
        e = S[f"e{i}"]
        for campo in ("titulo", "enunciado", "pasos", "solucion", "lectura"):
            a.cierto(campo in e and e[campo], f"E{i}: tiene `{campo}`")
        a.cierto(len(e["pasos"]) >= 5, f"E{i}: publica al menos cinco pasos intermedios",
                 str(len(e["pasos"])))
    # E1: las tres ventanas, recalculadas.
    s1 = S["e1"]["solucion"]
    casco = gpd.GeoSeries(cole.geometry).union_all().convex_hull \
        if hasattr(gpd.GeoSeries(cole.geometry), "union_all") \
        else gpd.GeoSeries(cole.geometry).unary_union.convex_hull
    a.cerca(casco.area / 1e6, s1["casco"]["area_km2"],
            "E1: el área de la envolvente convexa, con shapely", 1e-6)
    a.igual(s1["casco"]["n"], len(cole), "E1: la envolvente convexa no deja fuera ninguna sede")
    a.igual(s1["casco_deja_fuera"], 0, "E1: y el propio dato lo dice")
    a.cerca(len(cole) / (casco.area / 1e6), s1["casco"]["lambda_km2"],
            "E1: la lambda del casco", 1e-6)
    a.cerca(s1["lambda_max"] / s1["lambda_min"], s1["factor"],
            "E1: el factor entre la mayor y la menor lambda", 1e-9)
    a.cerca(s1["urbana"]["lambda_km2"], D["m1"]["urbana"]["lambda_km2"],
            "E1: su lambda urbana es la misma que la del módulo 1", 1e-9)
    # E2: el chi2 idéntico, otra vez y sobre otro patrón.
    s2 = S["e2"]["solucion"]
    a.igual(s2["original"]["chi2"], s2["rebarajado"]["chi2"],
            "E2: los dos chi² son el mismo número", 1e-9)
    a.igual(s2["chi2_identico"], 1, "E2: y la bandera lo declara")
    a.cierto(s2["original"]["clark_evans"] != s2["rebarajado"]["clark_evans"],
             "E2: y sin embargo Clark-Evans sí los separa")
    # E2 trabaja sobre `swedishpines`, y ahora que sus coordenadas viajan
    # en el CSV se puede recalcular en vez de creerlo.
    dsw = reg[reg.patron == "swedishpines"]
    a.igual(len(dsw), s2["n"], "E2: trabaja sobre las 71 coordenadas de swedishpines")
    vsw = D["m3"]["swedishpines"]["ventana"]
    c_sw = conteos_rejilla(dsw.x.values, dsw.y.values, vsw, s2["nx"], s2["nx"])
    esp_sw = np.full(c_sw.shape, c_sw.sum() / c_sw.size)
    chi_sw, _ = chi2_cuadrantes(c_sw.ravel(), esp_sw.ravel())
    a.cerca(chi_sw, s2["original"]["chi2"], "E2: su chi² recalculado con el convenio de cut()", 1e-6)
    ce_sw, _ = clark_evans_ingenuo(dsw.x.values, dsw.y.values,
                                   D["m3"]["swedishpines"]["area"])
    a.cerca(ce_sw, s2["original"]["clark_evans"], "E2: y su R de Clark-Evans")
    a.cerca(s2["original"]["clark_evans"] - s2["rebarajado"]["clark_evans"], s2["ce_cae"],
            "E2: la caída de R publicada corresponde a las dos R", 1e-9)
    # E3: los dos barridos.
    s3 = S["e3"]["solucion"]
    for clave in ("urbana", "dc"):
        b = s3[clave]
        a.igual(len(b["nx"]), len(s3["nxs"]), f"E3/{clave}: una fila por tamaño")
        a.cierto(all((b["p_valor"][i] < 0.05) == (b["rechaza"][i] == 1)
                     for i in range(len(b["nx"]))),
                 f"E3/{clave}: la bandera de rechazo corresponde al p-valor")
    a.cierto(s3["dc"]["pct_vacias"][s3["nxs"].index(10)] >
             s3["urbana"]["pct_vacias"][s3["nxs"].index(10)],
             "E3: la ventana del D.C. tiene más celdas vacías (la tesis del ejercicio)")
    # E4: los p-valores y su recorrido.
    s4 = S["e4"]["solucion"]
    a.cerca(100 * s4["nodos_fuera"] / s4["nodos"], s4["pct_fuera"],
            "E4: el porcentaje de nodos fuera de la banda", 1e-6)
    ps = [t["dclf_p"] for t in s4["tramos"]] + [s4["dclf_L"]]
    a.cierto(max(ps) / min(ps) > 10,
             "E4: los p-valores del mismo patrón se separan en más de un orden de magnitud",
             f"de {min(ps)} a {max(ps)}")
    a.cierto(s4["dclf_L"] < 0.05 <= max(t["dclf_p"] for t in s4["tramos"]),
             "E4: sobre L rechaza y sobre la K cruda en todo el rango no (el giro del ejercicio)")
    # E5: el sesgo y la corrección que no existe.
    s5 = S["e5"]["solucion"]
    a.cierto(s5["sesgo_max_pct"] > 0, "E5: el sesgo sin corregir es positivo")
    a.cierto(s5["clark_evans_cdf"] < s5["clark_evans_naive"],
             "E5: corregir el borde baja R, o sea que sin corregir parecía menos agregado")
    a.igual(s5["donnelly_disponible"], 0,
            "E5: la corrección de Donnelly NO existe para esta ventana")
    a.igual(s5["ventana_rectangular"], 0, "E5: porque la ventana no es un rectángulo")
    a.cierto(s5["donnelly_en_cells"] > 0,
             "E5: y sobre `cells`, que sí vive en un rectángulo, existe",
             str(s5["donnelly_en_cells"]))
    a.cerca(s5["n"], D["m1"]["urbana"]["n"], "E5: trabaja sobre las mismas sedes que el módulo 1")

    # -----------------------------------------------------------------
    a.titulo("13 · Los mapas")
    # -----------------------------------------------------------------
    esperados = ("patron_urbano", "patron_dc", "cells", "japanesepines", "redwood",
                 "ceguera_original", "ceguera_rebarajado")
    for nombre in esperados:
        a.cierto(nombre in M, f"mapas: está `{nombre}`")
        if nombre in M:
            audita_geomapa(a, M[nombre], nombre, presupuesto_kb=150.0)
            a.cierto(M[nombre]["modo"] == "puntos",
                     f"mapas/{nombre}: es del modo `puntos`, que es el del capítulo")
    a.igual(M["patron_urbano"]["n"], D["m1"]["urbana"]["n"],
            "mapas: el mapa urbano pinta tantas sedes como el módulo 1 cuenta")
    a.igual(M["patron_dc"]["n"], D["m1"]["dc"]["n"],
            "mapas: y el del D.C., las suyas")
    a.igual(M["redwood"]["n"], D["m3"]["redwood"]["n"], "mapas: redwood, sus plántulas")
    a.igual(M["ceguera_original"]["n"], M["ceguera_rebarajado"]["n"],
            "mapas: los dos patrones del módulo 5 tienen el mismo número de puntos")
    a.cierto(len(M["patron_urbano"].get("lineas", [])) > 1,
             "mapas: el contorno urbano viaja como varias polilíneas, no como una",
             f"{len(M['patron_urbano'].get('lineas', []))} partes")
    # El contorno DIBUJADO es más simple que el ANALIZADO, a propósito, y
    # el capítulo lo dice. Aquí se comprueba que de verdad lo sea.
    vert_dibujados = sum(len(l) // 2 for l in M["patron_urbano"].get("lineas", []))
    a.cierto(vert_dibujados < D["m1"]["urbana"]["vertices"],
             "mapas: el contorno que se dibuja está simplificado frente al que se analiza",
             f"{vert_dibujados} contra {D['m1']['urbana']['vertices']}")
    kb = p_mapas.stat().st_size / 1024
    a.cierto(kb <= 150, "mapas: el archivo cabe en el presupuesto declarado de 150 KB",
             f"{kb:.1f} KB")

    # -----------------------------------------------------------------
    a.titulo("14 · Formato")
    # -----------------------------------------------------------------
    for nombre, obj in (("datos", D), ("mapas", M), ("soluciones", S)):
        nans = list(sin_nan(obj))
        a.cierto(not nans, f"{nombre}: sin NaN ni infinitos", str(nans[:3]))
    txt = p_datos.read_text(encoding="utf-8")
    a.cierto("Ã" not in txt and "�" not in txt,
             "datos: las tildes están intactas en el archivo")
    a.cierto("ó" in txt or "í" in txt, "y hay tildes de verdad que comprobar")
    excesivos = [(r, n) for r, n in decimales(D) if n > 10]
    a.cierto(not excesivos, "datos: ningún flotante pasa de 10 decimales",
             str(excesivos[:3]))
    a.igual(D["meta"]["capitulo"], 4, "la metainformación dice capítulo 4")
    a.cierto(D["meta"]["n_anclas"] >= 20, "el generador comprobó sus anclas",
             f"{D['meta']['n_anclas']} anclas")
    sem = D["meta"]["semillas"]
    a.cierto(len(set(sem.values())) == len(sem),
             "las semillas del capítulo son todas distintas", str(sem))
    a.cierto(D["meta"]["semilla"] not in sem.values(),
             "y ninguna repite la semilla global", str(D["meta"]["semilla"]))

    return a.cierre()


if __name__ == "__main__":
    sys.exit(main())
