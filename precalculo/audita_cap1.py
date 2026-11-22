#!/usr/bin/env python3
"""
audita_cap1.py — auditoría independiente del precálculo del capítulo 1 (T1.1)

Material de Estadística Espacial 2026-II (20929).

NO comprueba que los JSON existan: comprueba que sus NÚMEROS sean ciertos,
por caminos que no pasan por R.

POR QUÉ EN PYTHON, Y NO EN R. Es la lección metodológica de A.10, que
costó 295 724 estudiantes desaparecidos en silencio: `verifica_t04.R`
recalculaba desde el crudo por otro camino y daba 90/90, pero **los dos
caminos corrían en el mismo locale roto** y se equivocaban igual. Un
control que comparte el entorno con lo que audita no es independiente.
Aquí el intérprete es otro, las bibliotecas son otras (geopandas, shapely,
libpysal, esda, scipy en vez de sf, spdep, spatstat) y la lectura del
disco es otra. Si los dos coinciden, coinciden de verdad.

HASTA DÓNDE LLEGA LA INDEPENDENCIA, DECLARADO Y NO INSINUADO
  · TOTAL para `nc.shp`, los GeoPackage colombianos y los CSV de
    municipios: geopandas los lee del original, sin pasar por R.
  · PARCIAL para Snow, los patrones de `spatstat.data` y `meuse`: esos
    paquetes no existen en Python, así que se auditan sobre los CSV que
    exporta el generador. Sobre ellos este guion verifica el ANÁLISIS,
    no la lectura del paquete — la lectura la ancla `genera_cap1.R`
    contra las cifras que publican HistData, Numata, Ripley y Burrough,
    y para si no cuadran.

CUATRO FRENTES
  1. R <-> PYTHON. Recalcula desde las fuentes primarias.
  2. COHERENCIA INTERNA. Que las cifras derivadas cuadren con las de las
     que salen, y que las relaciones que el capítulo afirma se sostengan.
  3. LOS MAPAS. Cortes, geometría, presupuesto y relación de aspecto.
  4. FORMATO. JSON válido, tildes intactas, sin NaN, redondeo declarado.

Uso:  python3 precalculo/audita_cap1.py     (desde `Estadistica espacial/`)
Con el intérprete de geo_env; `audita_todo.sh` ya lo hace.
Devuelve 1 si algo falla.

Las variables de entorno CAP1_DATOS, CAP1_MAPAS y CAP1_SOLUCIONES
permiten apuntar a copias con defectos inyectados: es lo que hace
`prueba_auditor_cap1.py`. Los archivos publicados no se tocan nunca.

LOS RÓTULOS TIENEN PRESUPUESTO: 57 CARACTERES, PREFIJO INCLUIDO.
`Auditoria.cierto()` rellena el rótulo hasta 58 antes del detalle, así que
uno de 58 o más queda pegado a su detalle por un solo espacio y
`prueba_auditor_base.py` —que lee este informe con una expresión regular
para saber qué comprobaciones se han visto fallar— no puede separarlos.
El detalle cambia entre la pasada limpia y la rota, así que la
comprobación deja de contarse como cubierta AUNQUE HAYA FALLADO. No rompe
nada que se vea: corrompe el recuento de cobertura, en silencio.

Este archivo llegó a tener 83 rótulos pasados. Se acortaron el 2026-08-24
sin perder nada, moviendo el matiz al DETALLE, que no paga presupuesto, y
quitando lo que la propia comparación ya demuestra —`a.igual()` imprime
las dos cifras, así que «es el de su campo» sobra en el rótulo—.
Veintidós quedan entre 55 y 57: al añadir o renombrar cualquier cosa
aquí, medir.
"""
from __future__ import annotations

import json
import math
import os
import pathlib
import sys
import warnings

warnings.filterwarnings("ignore")

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

RAIZ = pathlib.Path(__file__).resolve().parent.parent
PRECALCULO = RAIZ / "precalculo"
SALIDAS = PRECALCULO / "salidas"
PROCESADO = RAIZ / "datos" / "procesado"


# =====================================================================
# El contador, el registro de fallos y el formato del informe viven ahora
# en `audita_base.py`. Se sacaron de aquí en T2.1d, al escribir el
# auditor del capítulo 2: con dos copias del núcleo todavía se puede
# arreglar un fallo en un sitio; con diez, no. Es la misma lección que
# `audita_texto_base.py` aprendió en T0.5.
from audita_base import Auditoria, carga as _carga, decimales


def carga(var: str, nombre: str):
    return _carga(var, nombre, SALIDAS)


# =====================================================================
# LA REFERENCIA DE THIESSEN CON PUNTOS UNIFORMES, simulada AQUÍ (R1 · T1.4)
#
# El módulo 10 compara la razón entre la mayor y la menor celda de Thiessen
# de la red del IDEAM con la que saldría de puntos uniformes. R la simula
# con `sf`; este auditor la simula por su cuenta, con otro generador (el de
# numpy), otra semilla y otra biblioteca geométrica (shapely), y no lee
# nada de lo que R publicó.
#
# Son ~0.25 s por muestra, cuatro minutos las mil, y el ARNÉS ejecuta el
# auditor una vez por inyección: se guarda, con las dos cautelas de la
# caché de `audita_cap6.py`:
#
#   · guarda lo que ESTE auditor simuló, no lo que R publicó;
#   · la llave lleva el tamaño y la fecha del .gpkg del país, el número de
#     puntos, el de muestras y la semilla: si cambia algo, se descarta.
# =====================================================================
N_REF_AUDITOR = 1000
SEMILLA_REF_AUDITOR = 20929


def razones_thiessen_uniforme(pais, ruta: pathlib.Path, n_puntos: int) -> list:
    """Razón máx./mín. del área de Thiessen en N_REF_AUDITOR muestras uniformes."""
    import numpy as np
    import shapely
    from shapely import MultiPoint, voronoi_polygons

    st = ruta.stat()
    llave = (f"{st.st_size}·{int(st.st_mtime)}·{n_puntos}·{N_REF_AUDITOR}·"
             f"{SEMILLA_REF_AUDITOR}")
    f = PRECALCULO / "cache" / "audita_cap1_thiessen_uniforme.json"
    if f.exists():
        guardado = json.loads(f.read_text(encoding="utf-8"))
        if guardado.get("llave") == llave:
            return guardado["razones"]
    shapely.prepare(pais)
    x0, y0, x1, y1 = pais.bounds
    rng = np.random.default_rng(SEMILLA_REF_AUDITOR)

    def muestra() -> "np.ndarray":
        # Rechazo sobre la caja del país.
        xy = np.empty((0, 2))
        while len(xy) < n_puntos:
            c = np.column_stack([rng.uniform(x0, x1, 2 * n_puntos),
                                 rng.uniform(y0, y1, 2 * n_puntos)])
            xy = np.vstack([xy, c[shapely.contains_xy(pais, c[:, 0], c[:, 1])]])
        return xy[:n_puntos]

    razones = []
    for _ in range(N_REF_AUDITOR):
        celdas = np.array(voronoi_polygons(MultiPoint(muestra()),
                                           extend_to=pais.envelope).geoms)
        # Solo se recortan las celdas que no caen enteras dentro del país.
        dentro = shapely.contains(pais, celdas)
        ar = shapely.area(celdas)
        ar[~dentro] = shapely.area(shapely.intersection(celdas[~dentro], pais))
        assert len(ar) == n_puntos and (ar > 0).all()
        razones.append(float(ar.max() / ar.min()))
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(json.dumps({"llave": llave, "razones": razones}), encoding="utf-8")
    return razones


# =====================================================================
def main() -> int:
    import numpy as np
    import pandas as pd
    import geopandas as gpd
    from scipy.spatial import cKDTree
    from shapely.geometry import box, MultiPoint, Polygon
    from shapely.ops import voronoi_diagram
    from libpysal.weights import Queen
    from esda.moran import Moran

    a = Auditoria("Precálculo del capítulo 1 verificado")
    D, ruta_d = carga("CAP1_DATOS", "cap1_datos.json")
    M, ruta_m = carga("CAP1_MAPAS", "cap1_mapas.json")
    S, ruta_s = carga("CAP1_SOLUCIONES", "cap1_soluciones.json")

    print(f"\n=== audita_cap1.py · {ruta_d.name} + {ruta_m.name} + {ruta_s.name} ===")
    print(f"    Python {sys.version.split()[0]} · geopandas {gpd.__version__} "
          f"· numpy {np.__version__}")

    # =================================================================
    a.titulo("1a · Snow, recalculado con scipy")
    # =================================================================
    # Independencia PARCIAL, declarada: HistData no existe en Python.
    a.salta("la lectura de HistData::Snow.*",
            "el paquete no existe en Python; la ancla está en genera_cap1.R")

    sn = pd.read_csv(SALIDAS / "cap1_snow.csv")
    mu = sn[sn.tipo == "muerte"][["x", "y"]].to_numpy()
    bo = sn[sn.tipo == "bomba"][["x", "y"]].to_numpy()
    etiq = sn[sn.tipo == "bomba"]["etiqueta"].tolist()
    s = D["snow"]

    a.igual(len(mu), s["n_muertes"], "muertes")
    a.igual(len(bo), s["n_bombas"], "bombas")
    i_broad = etiq.index("Broad St")
    a.igual(i_broad + 1, s["bomba_broad"], "índice de Broad St (1-basado)")

    # cKDTree en vez de una matriz de distancias: otro algoritmo, no otra
    # escritura del mismo. Si los dos dan lo mismo, el resultado no
    # depende de la implementación.
    arbol = cKDTree(bo)
    d_min, i_min = arbol.query(mu, k=2)
    a.igual((i_min[:, 0] == i_broad).sum(), s["n_mas_cerca_broad"],
            "muertes cuya bomba más próxima es Broad St")
    a.igual(100 * (i_min[:, 0] == i_broad).mean(), s["pct_mas_cerca_broad"],
            "porcentaje sobre el total", tol=1e-7)
    a.igual(100 / len(bo), s["pct_esperado_uniforme"], "porcentaje uniforme")
    a.igual((i_min[:, 0] == i_broad).mean() * len(bo), s["razon_sobre_uniforme"],
            "razón sobre lo uniforme", tol=1e-7)

    d_broad = np.linalg.norm(mu - bo[i_broad], axis=1)
    a.igual(d_broad.mean(), s["dist_media_broad"], "distancia media a Broad St", 1e-7)
    a.igual(np.median(d_broad), s["dist_mediana_broad"], "distancia mediana", 1e-7)
    a.igual(d_min[:, 0].mean(), s["dist_media_su_bomba"], "distancia media a su bomba", 1e-7)
    a.igual((d_min[:, 0] / d_min[:, 1]).mean(), s["razon_primera_segunda"],
            "razón primera/segunda bomba", 1e-7)
    a.cierto(0 < s["razon_primera_segunda"] < 1,
             "la razón primera/segunda está en (0, 1)",
             f"{s['razon_primera_segunda']:.5f}")

    a.igual(s["n_coinciden_tobler"], s["n_en_poligono"],
            "la asignación coincide con los polígonos de Tobler")
    a.igual(s["pct_coinciden_tobler"], 100.0, "y coincide al 100 %")

    fe = pd.read_csv(SALIDAS / "cap1_snow_fechas.csv")
    a.igual(len(fe), s["n_dias_con_fecha"], "días con fecha de la tabla de Snow")
    a.igual(s["n_dias_con_fecha"] + s["n_dias_sin_fecha"], s["n_dias_tabla"],
            "  y los días sin fecha están contados")
    a.igual(len(s["serie_fecha"]), s["n_dias_con_fecha"],
            "  la serie publicada son los días con fecha")
    a.igual(fe["muertes"].sum(), s["muertes_tabla"], "muertes de la tabla")
    a.igual(fe["ataques"].max(), s["ataques_pico"], "pico de ataques")
    a.cierto(fe.loc[fe["ataques"].idxmax(), "fecha"] == s["fecha_pico"],
             "fecha del pico", s["fecha_pico"])
    antes = fe[fe.fecha < s["fecha_mango"]]["ataques"].sum()
    desde = fe[fe.fecha >= s["fecha_mango"]]["ataques"].sum()
    a.igual(antes, s["ataques_antes_mango"], "ataques antes del 8 de septiembre")
    a.igual(desde, s["ataques_desde_mango"], "ataques desde el 8 de septiembre")
    a.igual(100 * antes / (antes + desde), s["pct_ataques_antes_mango"],
            "porcentaje anterior al mango", 1e-7)
    a.igual(antes + desde, fe["ataques"].sum(), "y los dos trozos suman el total")
    a.cierto(s["pct_ataques_antes_mango"] > 50,
             "el brote ya había pasado su peor momento",
             f"{s['pct_ataques_antes_mango']:.5f} %")
    a.igual(100 * (1 - s["ataques_dia_mango"] / s["ataques_pico"]),
            s["caida_hasta_mango_pct"], "caída hasta el día del mango", 1e-7)
    a.igual(len(s["serie_fecha"]), len(fe), "longitud de la serie publicada")
    a.igual(len(s["serie_ataques"]), len(fe), "longitud de la serie de ataques")
    a.igual(sum(s["serie_ataques"]), fe["ataques"].sum(), "suma de la serie de ataques")
    a.igual(sum(s["serie_muertes"]), fe["muertes"].sum(), "suma de la serie de muertes")

    # =================================================================
    a.titulo("1a bis · Snow: la prueba de aleatorización")
    # =================================================================
    # R2 · T2.4 (C1-01). Tres caminos que no pasan por R:
    #   · la parte de calle de cada bomba —la media EXACTA de la nula— se
    #     rehace con otra geometría: R recorta cada tramo con desigualdades
    #     lineales; aquí GEOS construye el diagrama de Voronoi de las bombas
    #     y mide cuánta calle cae en cada celda;
    #   · la nula tiene forma cerrada, Binomial(n, p): el histograma que R
    #     publica se contrasta contra ella con una ji-cuadrado;
    #   · y se recoloca de nuevo aquí, con otro generador.
    # LAS TOLERANCIAS DE MONTE CARLO. La media de B recolocaciones tiene
    # error sd/sqrt(B): se le dejan 4. Una desviación típica estimada con B
    # valores tiene error relativo ~ 1/sqrt(2B): se le dejan 4. La
    # ji-cuadrado se rechaza con p < 0.001. Con la semilla fija nada de esto
    # es un sorteo en cada corrida: o cuadra o no.
    from shapely.geometry import LineString, Point as _Punto
    from scipy import stats as _st1
    al = s["aleatorizacion"]
    ca = pd.read_csv(SALIDAS / "cap1_snow_calles.csv")
    lineas = [LineString(g[["x", "y"]].to_numpy()) for _, g in ca.groupby("calle", sort=True)]
    a.igual(len(lineas), s["n_segmentos"], "calles en el CSV de calles")
    a.igual(sum(len(l.coords) - 1 for l in lineas), al["n_tramos"], "tramos rectos de calle")
    lon_total = sum(l.length for l in lineas)
    x0, y0, x1, y1 = ca.x.min(), ca.y.min(), ca.x.max(), ca.y.max()
    celdas = list(voronoi_diagram(MultiPoint(bo), envelope=box(x0 - 5, y0 - 5, x1 + 5, y1 + 5)).geoms)
    a.igual(len(celdas), len(bo), "celdas de Voronoi, una por bomba")
    parte = []
    for j in range(len(bo)):
        suya = [c for c in celdas if c.contains(_Punto(bo[j]))]
        parte.append(100 * sum(l.intersection(suya[0]).length for l in lineas) / lon_total
                     if len(suya) == 1 else float("nan"))
    a.igual(sum(parte), 100.0, "las celdas se reparten la calle entera", 1e-6)
    a.cierto(al["bombas"] == etiq, "las partes de calle van en el orden de las bombas")
    a.igual(len(al["pct_calle_por_bomba"]), len(bo), "una parte de calle por bomba")
    for j, (calc, pub) in enumerate(zip(parte, al["pct_calle_por_bomba"])):
        a.igual(calc, pub, f"parte de calle de la bomba {j + 1}, por Voronoi", 1e-6)
    a.igual(parte[i_broad], al["pct_calle_broad"], "parte de calle de Broad St", 1e-6)
    a.igual(s["pct_mas_cerca_broad"] / parte[i_broad], al["razon_sobre_calle"],
            "el observado entre la parte de calle", 1e-6)
    a.cierto(s["pct_esperado_uniforme"] < al["pct_calle_broad"]
             and al["razon_sobre_calle"] < s["razon_sobre_uniforme"],
             "a Broad St le toca más calle que el reparto ingenuo",
             f"{al['pct_calle_broad']:.5f} frente a {s['pct_esperado_uniforme']:.5f}")
    n_mu, k_obs, B_rec = s["n_muertes"], s["n_mas_cerca_broad"], al["n_recolocaciones"]
    # Segunda ronda · LA PARTE DE CALLE SEGÚN EL MARCO. Las calles se recortan
    # con GEOS al rectángulo de las muertes y a ese rectángulo ensanchado, y
    # la parte de Broad St se rehace con su celda de Voronoi. R lo hace
    # recortando tramo a tramo (Liang-Barsky) y con desigualdades lineales.
    celda_broad = [c for c in celdas if c.contains(_Punto(bo[i_broad]))][0]
    cm = [mu[:, 0].min(), mu[:, 0].max(), mu[:, 1].min(), mu[:, 1].max()]
    for calc, pub, que in zip(cm, al["caja_muertes"], ("x mín.", "x máx.", "y mín.", "y máx.")):
        a.igual(calc, pub, f"caja de las muertes, {que}", 1e-7)
    for calc, pub, que in zip([x0, x1, y0, y1], al["caja_calles"], ("x mín.", "x máx.", "y mín.", "y máx.")):
        a.igual(calc, pub, f"caja de las calles, {que}", 1e-6)
    a.cierto([m["margen"] for m in al["marcos"]] == [0, 1, 2, None],
             "los marcos son la caja de las muertes, +1, +2 y el plano")
    a.cierto(all(isinstance(m["marco"], str) and m["marco"].strip() for m in al["marcos"])
             and al["marcos"][0]["marco"] == "el rectángulo de las muertes"
             and al["marcos"][-1]["marco"] == "el plano entero"
             and all(str(m["margen"]) in m["marco"] for m in al["marcos"][1:-1]),
             "cada marco lleva el nombre de lo que recorta")
    for m in al["marcos"]:
        rot = "marco entero" if m["margen"] is None else f"marco +{m['margen']}"
        if m["margen"] is None:
            dentro = lineas
        else:
            caja_r = box(cm[0] - m["margen"], cm[2] - m["margen"], cm[1] + m["margen"], cm[3] + m["margen"])
            dentro = [l.intersection(caja_r) for l in lineas]
        lon_m = sum(g.length for g in dentro)
        p_m = sum(g.intersection(celda_broad).length for g in dentro) / lon_m
        a.igual(100 * lon_m / lon_total, m["pct_longitud"], f"{rot}: calle que entra, en % del plano", 1e-6)
        a.igual(100 * p_m, m["pct_calle_broad"], f"{rot}: parte de calle de Broad St", 1e-6)
        a.igual(k_obs / n_mu / p_m, m["razon_sobre_calle"], f"{rot}: observado entre esa parte", 1e-6)
        a.igual((k_obs - n_mu * p_m) / math.sqrt(n_mu * p_m * (1 - p_m)), m["z_binomial"],
                f"{rot}: desviaciones típicas binomiales", 1e-5)
    a.cierto(all(m["z_binomial"] > 10 for m in al["marcos"]),
             "el rechazo se mantiene con cualquiera de los marcos",
             " · ".join(f"{m['z_binomial']:.1f}" for m in al["marcos"]))
    a.cierto(all(x["pct_calle_broad"] > y["pct_calle_broad"] for x, y in zip(al["marcos"], al["marcos"][1:]))
             and 2 * al["marcos"][0]["razon_sobre_calle"] < al["marcos"][-1]["razon_sobre_calle"],
             "la parte explicada sí depende del marco",
             " · ".join(f"{m['razon_sobre_calle']:.2f}" for m in al["marcos"]))
    # El histograma, y todo lo que se resume de él.
    K, F = np.array(al["hist_n"]), np.array(al["hist_frec"])
    a.cierto(B_rec >= 999, "recolocaciones suficientes", str(B_rec))
    # La semilla no se puede rehacer desde aquí; sí que sea propia: entera y
    # distinta de la del guion y de las dos de la envolvente del módulo 3.
    _sem_env = D["tobler"]["envolvente"]
    _sems = [D["meta"]["semilla"], al["semilla"], _sem_env["semilla_ideam"], _sem_env["semilla_residuos"]]
    a.cierto(all(isinstance(x, int) for x in _sems) and len(set(_sems)) == len(_sems),
             "las semillas nuevas son enteras y distintas entre sí", str(_sems))
    a.igual(int(F.sum()), B_rec, "el histograma suma las recolocaciones")
    a.cierto(len(K) == len(F) == al["max_nula_n"] - al["min_nula_n"] + 1
             and list(K) == list(range(al["min_nula_n"], al["max_nula_n"] + 1))
             and F[0] > 0 and F[-1] > 0,
             "el histograma trae una barra por recuento posible")
    media_k = float((K * F).sum() / B_rec)
    sd_k = math.sqrt(float(((K - media_k) ** 2 * F).sum() / (B_rec - 1)))
    a.igual(100 * media_k / n_mu, al["media_nula_pct"], "media de la nula, desde el histograma", 1e-7)
    a.igual(100 * sd_k / n_mu, al["sd_nula_pct"], "su desviación típica", 1e-7)
    a.igual(100 * sd_k / n_mu / math.sqrt(B_rec), al["emc_media_pct"],
            "y el error de Monte Carlo de la media", 1e-8)
    a.igual(100 * al["min_nula_n"] / n_mu, al["min_nula_pct"], "mínimo de la nula, en porcentaje", 1e-7)
    a.igual(100 * al["max_nula_n"] / n_mu, al["max_nula_pct"], "máximo de la nula, en porcentaje", 1e-7)
    a.igual(int(F[K >= k_obs].sum()), al["n_mayor_o_igual"],
            "recolocaciones que igualan o superan al observado")
    a.cierto(al["n_mayor_o_igual"] == 0 and al["max_nula_n"] < k_obs,
             "ninguna recolocación llega al observado",
             f"la mayor, {al['max_nula_n']} muertes frente a {k_obs}")
    a.igual(1 / (B_rec + 1), al["p_cota"], "la cota del valor p es 1/(B + 1)", 1e-12)
    a.igual((k_obs - media_k) / sd_k, al["z_observado"],
            "desviaciones típicas del observado a la nula", 1e-6)
    # La forma cerrada.
    p_b = parte[i_broad] / 100
    a.cierto(np.allclose(B_rec * _st1.binom.pmf(K, n_mu, p_b), al["hist_binomial"],
                         rtol=1e-6, atol=1e-7),
             "la curva binomial es B·P(K = k) con la parte de calle")
    a.igual(100 * math.sqrt(n_mu * p_b * (1 - p_b)) / n_mu, al["sd_binomial_pct"],
            "desviación típica de la binomial", 1e-7)
    a.cierto(abs(al["media_nula_pct"] - parte[i_broad]) < 4 * al["emc_media_pct"],
             "la media simulada reproduce la parte de calle",
             f"{al['media_nula_pct']:.5f} ± {al['emc_media_pct']:.5f} frente a {parte[i_broad]:.5f}")
    a.cierto(abs(al["sd_nula_pct"] / al["sd_binomial_pct"] - 1) < 4 / math.sqrt(2 * B_rec),
             "y la desviación típica simulada, la binomial",
             f"{al['sd_nula_pct']:.5f} frente a {al['sd_binomial_pct']:.5f}")
    # Ji-cuadrado del histograma contra la binomial. Cada cola se agrupa con
    # la primera barra que espera al menos 5 recolocaciones; la binomial es
    # unimodal, así que las de en medio las esperan todas.
    esp_k = B_rec * _st1.binom.pmf(np.arange(n_mu + 1), n_mu, p_b)
    obs_k = np.zeros(n_mu + 1)
    obs_k[K] = F
    _bien = np.flatnonzero(esp_k >= 5)
    k_iz, k_de = int(_bien[0]), int(_bien[-1])
    o_ji = np.r_[obs_k[:k_iz + 1].sum(), obs_k[k_iz + 1:k_de], obs_k[k_de:].sum()]
    e_ji = np.r_[esp_k[:k_iz + 1].sum(), esp_k[k_iz + 1:k_de], esp_k[k_de:].sum()]
    ji = float(((o_ji - e_ji) ** 2 / e_ji).sum())
    p_ji = float(_st1.chi2.sf(ji, len(o_ji) - 1))
    a.cierto(e_ji.min() >= 5 and p_ji > 0.001,
             "el histograma es compatible con la binomial",
             f"ji-cuadrado {ji:.1f} con {len(o_ji) - 1} g. l., p = {p_ji:.3f}")
    # Y se recoloca aquí, con numpy: 2 000 repartos sobre las calles.
    seg = np.array([(x_a, y_a, x_b, y_b) for l in lineas
                    for (x_a, y_a), (x_b, y_b) in zip(l.coords[:-1], l.coords[1:])])
    lon_seg = np.hypot(seg[:, 2] - seg[:, 0], seg[:, 3] - seg[:, 1])
    rng_s = np.random.default_rng(20929)
    N_PY = 2000
    cual = rng_s.choice(len(seg), size=(N_PY, n_mu), p=lon_seg / lon_seg.sum())
    u_s = rng_s.random((N_PY, n_mu))
    pts = np.stack([seg[cual, 0] + u_s * (seg[cual, 2] - seg[cual, 0]),
                    seg[cual, 1] + u_s * (seg[cual, 3] - seg[cual, 1])], axis=-1)
    k_py = (arbol.query(pts.reshape(-1, 2))[1].reshape(N_PY, n_mu) == i_broad).sum(axis=1)
    emc_py = 100 * k_py.std(ddof=1) / n_mu / math.sqrt(N_PY)
    a.cierto(abs(100 * k_py.mean() / n_mu - parte[i_broad]) < 4 * emc_py,
             "2 000 recolocaciones de aquí dan la misma media",
             f"{100 * k_py.mean() / n_mu:.5f} ± {emc_py:.5f}")
    a.cierto(abs(100 * k_py.mean() / n_mu - al["media_nula_pct"]) < 5 * math.hypot(emc_py, al["emc_media_pct"]),
             "  compatible con la media que publica R")
    a.cierto(int(k_py.max()) < k_obs, "  y tampoco aquí llega ninguna al observado",
             f"la mayor, {int(k_py.max())} muertes frente a {k_obs}")

    # =================================================================
    a.titulo("1b · Los patrones puntuales canónicos")
    # =================================================================
    a.salta("la lectura de spatstat.data",
            "el paquete no existe en Python; la ancla está en genera_cap1.R")
    pp = pd.read_csv(SALIDAS / "cap1_ppp.csv")
    for nombre in ("japanesepines", "redwood", "cells"):
        sub = pp[pp.patron == nombre][["x", "y"]].to_numpy()
        pub = D["puntual_canonico"][nombre]
        a.igual(len(sub), pub["n"], f"{nombre}: n")
        # Todos viven en la ventana unidad, así que el área es 1 y lambda = n.
        a.igual(1.0, pub["area"], f"{nombre}: área de la ventana")
        a.igual(len(sub), pub["lambda"], f"{nombre}: intensidad")
        arb = cKDTree(sub)
        dd, _ = arb.query(sub, k=2)
        nn = dd[:, 1]
        a.igual(nn.mean(), pub["nn_media"], f"{nombre}: distancia media al vecino", 1e-7)
        a.igual(nn.std(ddof=1), pub["nn_sd"], f"{nombre}: su desviación", 1e-7)
        # El denominador del índice, que el módulo 3 publica al lado del
        # numerador para que el cociente se pueda hacer a ojo.
        esperada = 0.5 / math.sqrt(len(sub))
        a.igual(esperada, pub["nn_esperada"],
                f"{nombre}: distancia esperada bajo CSR", 1e-7)
        ce = nn.mean() / (0.5 / math.sqrt(len(sub)))
        a.igual(ce, pub["clark_evans"], f"{nombre}: índice de Clark-Evans", 1e-7)
        # Y que las dos cifras publicadas den de verdad el índice publicado:
        # si alguna vez se editaran por separado, esto lo ve.
        a.igual(pub["nn_media"] / pub["nn_esperada"], pub["clark_evans"],
                f"{nombre}: observada / esperada reproduce el índice", 1e-7)
        # La versión corregida por efecto de borde (Donnelly 1978). Las tres
        # ventanas son cuadrados de área 1, así que el perímetro es 4; se
        # comprueba en vez de darse por hecho, porque de ahí salió el
        # defecto de la ventana de redwood.
        a.igual(1.0, pub["area"], f"{nombre}: la ventana sigue siendo de área 1")
        perim = 4.0
        esp_d = (0.5 * math.sqrt(pub["area"] / len(sub))
                 + (0.0514 + 0.0412 / math.sqrt(len(sub))) * perim / len(sub))
        a.igual(nn.mean() / esp_d, pub["clark_evans_donnelly"],
                f"{nombre}: índice de Clark-Evans corregido (Donnelly)", 1e-7)
        # Y la relación que el módulo 3 afirma en prosa: corregir el borde
        # BAJA el índice, en los tres. Si alguna vez subiera, la nota del
        # capítulo estaría diciendo lo contrario que el dato.
        a.cierto(pub["clark_evans_donnelly"] < pub["clark_evans"],
                 f"{nombre}: la corrección de borde baja el índice",
                 f"{pub['clark_evans']:.5f} -> {pub['clark_evans_donnelly']:.5f}")
    # El orden de los tres regímenes es el argumento del módulo 3.
    ce = D["tobler"]["clark_evans"]
    a.cierto(ce["redwood"] < ce["japanesepines"] < ce["cells"],
             "Clark-Evans ordena agregado < aleatorio < regular",
             f"{ce['redwood']:.4f} < {ce['japanesepines']:.4f} < {ce['cells']:.4f}")
    a.cierto(ce["redwood"] < 1 < ce["cells"],
             "y el aleatorio queda a un lado y otro de 1")
    for k in ("redwood", "japanesepines", "cells"):
        a.igual(ce[k], D["puntual_canonico"][k]["clark_evans"],
                f"Clark-Evans de {k}, en las dos secciones")

    # =================================================================
    a.titulo("1c · nc.shp, leído por geopandas")
    # =================================================================
    ver = json.loads((PRECALCULO / "versiones.json").read_text(encoding="utf-8"))
    nc = gpd.read_file(ver["rutas"]["nc_shp"])
    pub = D["area_canonico"]
    a.igual(len(nc), pub["n"], "condados")
    a.igual(nc["SID74"].sum(), pub["sid74_total"], "muertes súbitas 1974-78")
    a.igual(nc["BIR74"].sum(), pub["bir74_total"], "nacimientos 1974-78")
    tasa = 1000 * nc["SID74"] / nc["BIR74"]
    a.igual(tasa.mean(), pub["tasa_media"], "tasa media por condado", 1e-8)
    a.igual(tasa.std(ddof=1), pub["tasa_sd"], "su desviación", 1e-8)
    a.igual(tasa.min(), pub["tasa_min"], "tasa mínima", 1e-8)
    a.igual(tasa.max(), pub["tasa_max"], "tasa máxima", 1e-8)
    a.igual(1000 * nc["SID74"].sum() / nc["BIR74"].sum(), pub["tasa_global"],
            "tasa global", 1e-8)
    a.igual(pub["tasa_media"] - pub["tasa_global"], pub["diferencia_media_global"],
            "la diferencia entre la media de tasas y la tasa global", 1e-8)
    a.igual(100 * (pub["tasa_media"] / pub["tasa_global"] - 1),
            pub["diferencia_media_global_pct"], "  en porcentaje", 1e-6)
    a.cierto(abs(pub["diferencia_media_global"]) > 1e-3,
             "la media de las tasas NO es la tasa global",
             f"{pub['tasa_media']:.5f} frente a {pub['tasa_global']:.5f} "
             f"({pub['diferencia_media_global_pct']:.2f} %)")

    # --- El soporte: extensiva frente a intensiva ---------------------
    # El área se recalcula en la MISMA zona UTM que el generador (32617).
    # Si alguien cambiara allí la proyección y no aquí, esta correlación
    # se movería en el tercer decimal y lo diría este auditor: es de las
    # pocas cifras del capítulo que depende de una elección de CRS.
    sop = pub["soporte"]
    area_km2 = nc.to_crs(32617).area / 1e6
    a.igual(nc["SID74"].corr(nc["BIR74"]), sop["cor_conteo_nacimientos"],
            "soporte: conteo crudo contra los nacimientos", 1e-8)
    a.igual(nc["SID74"].corr(area_km2), sop["cor_conteo_area"],
            "soporte: conteo crudo contra el área", 1e-8)
    a.igual(tasa.corr(nc["BIR74"]), sop["cor_tasa_nacimientos"],
            "soporte: la tasa contra los nacimientos", 1e-8)
    a.igual(nc["BIR74"].max() / nc["BIR74"].min(), sop["razon_nacimientos"],
            "soporte: razón entre el mayor y el menor denominador", 1e-8)
    # Las tres afirmaciones que hace la prosa, comprobadas como
    # afirmaciones y no solo como cifras. Una cifra puede cuadrar contra
    # el JSON y aun así haber dejado de sostener la frase que ilustra.
    a.cierto(sop["cor_conteo_nacimientos"] > 0.8,
             "el conteo crudo es, sobre todo, un mapa del denominador",
             f"r = {sop['cor_conteo_nacimientos']:.5f}")
    a.cierto(abs(sop["cor_tasa_nacimientos"]) < 0.05,
             "y la tasa se queda limpia de él",
             f"r = {sop['cor_tasa_nacimientos']:.5f}")
    a.cierto(sop["cor_conteo_nacimientos"] > sop["cor_conteo_area"],
             "el denominador que importa es la población, no el área",
             f"{sop['cor_conteo_nacimientos']:.5f} frente a "
             f"{sop['cor_conteo_area']:.5f}")
    a.cierto(sop["razon_nacimientos"] > 10,
             "y el denominador varía lo bastante entre condados",
             f"×{sop['razon_nacimientos']:.5f} entre el mayor y el menor")

    an = D["anatomia"]["nc"]
    a.igual(len(nc), an["filas"], "anatomía: filas")
    a.igual(len(nc.columns), an["columnas"], "anatomía: columnas")
    a.igual(len(nc.columns) - 1, an["columnas_atributo"], "anatomía: atributos")
    a.cierto(an["tipo_geom"] == "MULTIPOLYGON", "anatomía: tipo de geometría",
             an["tipo_geom"])
    # OJO: aquí R y Python discrepan a propósito, y la discrepancia está
    # declarada. Lo que sí tiene que cuadrar es el número de condados con
    # más de una parte, que es la cifra sustantiva.
    partes = nc.geometry.apply(
        lambda g: len(g.geoms) if g.geom_type == "MultiPolygon" else 1)
    a.igual((partes > 1).sum(), an["n_partes_multiples"],
            "anatomía: condados con más de una parte")
    a.igual((nc.geometry.geom_type == "MultiPolygon").sum(), an["n_partes_multiples"],
            "anatomía: y shapely los ve como MultiPolygon")
    from shapely import get_coordinates
    a.igual(len(get_coordinates(nc.geometry.values)), an["n_vertices"],
            "anatomía: vértices")
    for i, v in enumerate(nc.total_bounds):
        a.cerca(v, an["bbox"][i], f"anatomía: bbox[{i}]", rel=1e-9)
    a.cierto(an["bytes_geometria"] < an["bytes_sf"],
             "anatomía: la geometría pesa menos que el objeto entero")
    a.igual(100 * an["bytes_geometria"] / an["bytes_sf"], an["pct_geometria"],
            "anatomía: porcentaje de geometría", 1e-6)
    a.cierto(an["pct_geometria"] > 50,
             "anatomía: la geometría es la mayor parte del objeto",
             f"{an['pct_geometria']:.2f} %")

    # =================================================================
    a.titulo("1d · meuse")
    # =================================================================
    a.salta("la lectura de sp::meuse",
            "el paquete no existe en Python; la ancla está en genera_cap1.R")
    me = pd.read_csv(SALIDAS / "cap1_meuse.csv")
    pub = D["geo_canonico"]
    a.igual(len(me), pub["n"], "observaciones de meuse")
    a.igual(me.zinc.mean(), pub["zinc_media"], "zinc medio", 1e-7)
    a.igual(me.zinc.std(ddof=1), pub["zinc_sd"], "su desviación", 1e-7)
    a.igual(me.zinc.min(), pub["zinc_min"], "zinc mínimo")
    a.igual(me.zinc.max(), pub["zinc_max"], "zinc máximo")
    lz = np.log(me.zinc.to_numpy())
    a.igual(lz.mean(), pub["log_zinc_media"], "log-zinc medio", 1e-8)
    a.igual(lz.std(ddof=1), pub["log_zinc_sd"], "su desviación", 1e-8)
    z = (me.zinc.to_numpy() - me.zinc.mean()) / me.zinc.std(ddof=1)
    a.igual((z ** 3).mean(), pub["asimetria_zinc"], "asimetría del zinc", 1e-7)
    a.cierto(pub["asimetria_zinc"] > 0.5,
             "el zinc es asimétrico a la derecha",
             f"{pub['asimetria_zinc']:.5f}, por eso se toma log")
    a.igual(np.corrcoef(lz, me["dist"].to_numpy())[0, 1], pub["corr_dist_rio"],
            "correlación log-zinc con la distancia al río", 1e-8)

    # =================================================================
    a.titulo("2a · El hilo colombiano, leído por geopandas")
    # =================================================================
    est = gpd.read_file(PROCESADO / "colombia_estaciones_clima.gpkg")
    pub = D["colombia"]["geo"]
    a.igual(len(est), pub["n"], "estaciones del IDEAM")
    a.igual(est.t_media_anual.mean(), pub["t_media"], "temperatura media", 1e-8)
    a.igual(est.t_media_anual.std(ddof=1), pub["t_sd"], "su desviación", 1e-8)
    a.igual(est.t_media_anual.min(), pub["t_min"], "temperatura mínima", 1e-8)
    a.igual(est.t_media_anual.max(), pub["t_max"], "temperatura máxima", 1e-8)
    a.igual(est.altitud_m.mean(), pub["alt_media"], "altitud media", 1e-7)
    a.igual(est.altitud_m.max(), pub["alt_max"], "altitud máxima", 1e-7)
    a.igual(np.corrcoef(est.altitud_m, est.t_media_anual)[0, 1], pub["corr_alt"],
            "correlación altitud-temperatura", 1e-8)
    pend = np.polyfit(est.altitud_m.to_numpy(), est.t_media_anual.to_numpy(), 1)[0]
    a.igual(pend * 1000, pub["gradiente"], "gradiente térmico por 1 000 m", 1e-6)
    a.cierto(-7 <= pub["gradiente"] <= -5,
             "el gradiente cae en el rango físico de -5 a -7 °C/km",
             f"{pub['gradiente']:.5f}")

    cole = gpd.read_file(PROCESADO / "bogota_colegios.gpkg")
    v_urb = gpd.read_file(PROCESADO / "bogota_ventana_urbana.gpkg")
    v_dc = gpd.read_file(PROCESADO / "bogota_ventana_dc.gpkg")
    pub = D["colombia"]["puntual"]
    a.igual(len(cole), pub["n"], "sedes educativas de Bogotá")
    a.igual(int(cole.en_urbana.sum()), pub["n_urbana"], "sedes en la ventana urbana")
    a.igual(int(cole.en_ventana_dc.sum()), pub["n_dc"], "sedes en Bogotá D.C.")
    au = v_urb.area.sum() / 1e6
    ad = v_dc.area.sum() / 1e6
    a.cerca(au, pub["area_urbana_km2"], "área urbana en km²", 1e-9)
    a.cerca(ad, pub["area_dc_km2"], "área de Bogotá D.C. en km²", 1e-9)
    a.igual(pub["n_urbana"] / au, pub["lambda_urbana"], "lambda urbana", 1e-7)
    a.igual(pub["n_dc"] / ad, pub["lambda_dc"], "lambda de Bogotá D.C.", 1e-7)
    a.igual(pub["lambda_urbana"] / pub["lambda_dc"], pub["factor_lambda"],
            "el factor entre las dos ventanas", 1e-7)
    a.cierto(pub["factor_lambda"] > 1,
             "la ventana urbana es más densa, como tiene que ser")

    mun = gpd.read_file(PROCESADO / "colombia_adm2.gpkg")
    llave = pd.read_csv(PROCESADO / "municipios_llave.csv", dtype={"divipola": str})
    mun = mun.merge(llave, on="shapeID", how="left")
    pub = D["colombia"]["area"]
    a.igual(len(mun), pub["n"], "municipios")
    d_ok = mun[mun.desercion.notna()]
    a.igual(len(d_ok), pub["n_con_dato"], "municipios con deserción")
    a.igual(d_ok.desercion.mean(), pub["media"], "deserción media", 1e-8)
    a.igual(d_ok.desercion.std(ddof=1), pub["sd"], "su desviación", 1e-8)
    a.igual(d_ok.desercion.min(), pub["minimo"], "deserción mínima", 1e-8)
    a.igual(d_ok.desercion.max(), pub["maximo"], "deserción máxima", 1e-8)

    # =================================================================
    a.titulo("2b · El I de Moran, recalculado con libpysal y esda")
    # =================================================================
    # La cifra estrella del capítulo, por una implementación distinta de
    # la contigüidad y del estadístico.
    d_ok = d_ok.reset_index(drop=True)
    w_mun = Queen.from_dataframe(d_ok, use_index=False)
    w_mun.transform = "r"
    mi = Moran(d_ok.desercion.to_numpy(), w_mun, permutations=0)
    esc = D["escala"]
    a.igual(len(d_ok), esc["n_municipal"], "municipios del cálculo de Moran")
    # esda usa n = todas las unidades; spdep con zero.policy usa n = las
    # que tienen vecinos. La discrepancia está DECLARADA (ver el frente
    # 2d), así que aquí se contrasta contra el convenio de Python, que es
    # el que este guion puede reproducir.
    a.igual(mi.I, esc["moran_municipal_n_total"],
            "I de Moran municipal (convenio n = todas)", 1e-6)
    a.cierto(abs(mi.I - esc["moran_municipal"]) > 1e-9,
             "  y NO coincide con el de spdep",
             f"{mi.I:.7f} frente a {esc['moran_municipal']:.7f}")
    # El convenio de spdep se reconstruye aquí para no darlo por bueno de
    # palabra: I_spdep = I_esda * (n_con_vecinos / n_total).
    n_con = len(d_ok) - len(w_mun.islands)
    a.igual(mi.I * n_con / len(d_ok), esc["moran_municipal"],
            "  y el de spdep se recupera cambiando n", 1e-6)
    a.igual(len(w_mun.islands), esc["islas_municipal"], "islas de la vecindad reina")
    a.igual(np.mean([len(v) for v in w_mun.neighbors.values()]),
            esc["grado_municipal"], "grado medio de la vecindad", 1e-7)
    a.igual(w_mun.n_components, esc["subgrafos_municipal"], "subgrafos")
    a.cierto(esc["islas_municipal"] >= 1,
             "el dato trae islas (zero.policy, cap. 6)",
             str(esc["islas_municipal"]))

    # Y el mismo cálculo a escala departamental, re-derivando la
    # agregación en vez de leer el CSV que escribió R.
    dep = gpd.read_file(PROCESADO / "colombia_adm1.gpkg")
    cen = gpd.GeoDataFrame(geometry=d_ok.geometry.representative_point(),
                           crs=d_ok.crs)
    j = gpd.sjoin(cen, dep[["geometry"]], how="left", predicate="within")
    j = j[~j.index.duplicated(keep="first")]
    d_ok["dep_idx"] = j["index_right"].to_numpy()
    d_ok["dpto"] = d_ok.divipola.str[:2]
    mayor = (d_ok.dropna(subset=["dep_idx"])
             .groupby("dep_idx")["dpto"]
             .agg(lambda v: v.value_counts().index[0]))
    dep["dpto"] = dep.index.map(mayor)
    med = d_ok.groupby("dpto")["desercion"].mean()
    dep["desercion"] = dep["dpto"].map(med)
    dep_ok = dep[dep.desercion.notna()].reset_index(drop=True)
    a.igual(len(dep_ok), esc["n_departamental"], "departamentos con dato")
    w_dep = Queen.from_dataframe(dep_ok, use_index=False)
    w_dep.transform = "r"
    mid = Moran(dep_ok.desercion.to_numpy(), w_dep, permutations=0)
    a.igual(mid.I, esc["moran_departamental_n_total"],
            "I de Moran departamental (convenio n = todas)", 1e-6)
    n_con_d = len(dep_ok) - len(w_dep.islands)
    a.igual(mid.I * n_con_d / len(dep_ok), esc["moran_departamental"],
            "  y el de spdep se recupera cambiando n", 1e-6)
    a.igual(len(w_dep.islands), esc["islas_departamental"],
            "islas de la vecindad departamental")
    a.igual(np.mean([len(v) for v in w_dep.neighbors.values()]),
            esc["grado_departamental"], "grado medio departamental", 1e-7)
    a.igual(100 * (1 - esc["moran_departamental"] / esc["moran_municipal"]),
            esc["caida_pct"], "la caída del I al agregar", 1e-6)
    a.cierto(esc["moran_municipal"] > esc["moran_departamental"] > 0,
             "agregar reduce el I sin llegar a anularlo",
             f"{esc['moran_municipal']:.5f} -> {esc['moran_departamental']:.5f}")
    a.cierto(esc["p_municipal"] < 0.01,
             "el I municipal es inequívoco", f"p = {esc['p_municipal']:.3e}")

    # R1 · T1.6 (C1-27) · la z de cada I, rehecha con la varianza bajo
    # aleatorización escrita aquí y no leída de spdep. El convenio es el de
    # `moran.test(zero.policy = TRUE)`: n cuenta las unidades CON vecinos en
    # la I, en E[I] y en la varianza, y la curtosis K se calcula con todas.
    from scipy import stats as _st

    def z_moran(x, w):
        W = w.sparse.tocsr()
        z_ = x - x.mean()
        n_ = len(x) - len(w.islands)
        s0 = W.sum()
        s1 = 0.5 * (W + W.T).power(2).sum()
        s2 = ((np.asarray(W.sum(axis=1)).ravel() + np.asarray(W.sum(axis=0)).ravel()) ** 2).sum()
        i_ = (n_ / s0) * float(z_ @ (W @ z_)) / float(z_ @ z_)
        k_ = len(x) * (z_ ** 4).sum() / (z_ ** 2).sum() ** 2
        ei = -1 / (n_ - 1)
        vi = n_ * (s1 * (n_ ** 2 - 3 * n_ + 3) - n_ * s2 + 3 * s0 ** 2)
        vi -= k_ * (s1 * (n_ ** 2 - n_) - 2 * n_ * s2 + 6 * s0 ** 2)
        vi = vi / ((n_ - 1) * (n_ - 2) * (n_ - 3) * s0 ** 2) - ei ** 2
        return i_, (i_ - ei) / math.sqrt(vi), math.sqrt(vi)

    i_m, z_m, ee_m = z_moran(d_ok.desercion.to_numpy(), w_mun)
    i_d, z_d, ee_d = z_moran(dep_ok.desercion.to_numpy(), w_dep)
    a.igual(i_m, esc["moran_municipal"], "la I municipal, por la fórmula escrita aquí", 1e-6)
    a.igual(i_d, esc["moran_departamental"], "  y la departamental", 1e-6)
    a.igual(z_m, esc["z_municipal"], "la z de la I municipal (aleatorización)", 1e-5)
    a.igual(z_d, esc["z_departamental"], "la z de la I departamental", 1e-6)
    a.igual(ee_m, esc["ee_municipal"], "la desviación de la I municipal bajo la nula", 1e-7)
    a.igual(ee_d, esc["ee_departamental"], "  y la de la departamental", 1e-7)
    a.igual(esc["ee_departamental"] / esc["ee_municipal"], esc["razon_ee"],
            "cuántas veces más varía la I departamental", 1e-7)
    a.igual(float(_st.norm.sf(esc["z_departamental"])), esc["p_departamental"],
            "el p departamental es el de una cola de esa z", 1e-8)
    # La z que tendría una I departamental IGUAL a la municipal: con la nula
    # departamental (su esperanza y su desviación), no con la municipal.
    a.igual((esc["moran_municipal"] + 1 / (len(dep_ok) - len(w_dep.islands) - 1)) / ee_d,
            esc["z_departamental_si_igual"],
            "la z de una I departamental igual a la municipal", 1e-6)
    a.cierto(esc["z_departamental"] < esc["z_departamental_si_igual"] < esc["z_municipal"],
             "  y queda entre las dos: la z crece con n",
             f"{esc['z_departamental']:.3f} < {esc['z_departamental_si_igual']:.3f} < {esc['z_municipal']:.3f}")
    a.cierto(esc["z_municipal"] > 3 and esc["razon_ee"] > 1,
             "la I municipal queda lejos de su nula y la departamental varía más",
             f"z = {esc['z_municipal']:.3f} · razón {esc['razon_ee']:.3f}")

    # =================================================================
    a.titulo("2b bis · Agregar: el predicado, la conservación y el reparto")
    # =================================================================
    # El módulo 7 mide la ESCALA arriba; esto mide la AGREGACIÓN, que es
    # la otra mitad de su título. Sigue el capítulo 5 de Pebesma y Bivand.
    ags = D["agregacion_soporte"]

    # --- nc: la rejilla del libro, reconstruida aquí -----------------
    # `st_make_grid` por defecto son 10x10 celdas sobre el bbox. Se
    # rehace a mano en vez de leer nada de R: si sf cambiara el defecto,
    # el número de celdas dejaría de cuadrar y se vería.
    nc2264 = nc.to_crs(2264)
    minx, miny, maxx, maxy = nc2264.total_bounds
    dx, dy = (maxx - minx) / 10, (maxy - miny) / 10
    celdas = [box(minx + i * dx, miny + j * dy,
                  minx + (i + 1) * dx, miny + (j + 1) * dy)
              for i in range(10) for j in range(10)]
    rej = gpd.GeoDataFrame({"_j": range(len(celdas))},
                           geometry=celdas, crs=nc2264.crs)
    pub_nc = ags["nc"]
    a.igual(len(rej), pub_nc["n_celdas"], "celdas de la rejilla sobre nc")
    a.igual(nc["SID74"].sum(), pub_nc["total_condados"],
            "SIDS sumados sobre los condados")
    # El predicado por defecto de aggregate.sf: `intersects`. Un condado
    # que toca cuatro rectángulos aporta su conteo ENTERO a los cuatro.
    unida = gpd.sjoin(nc2264[["SID74", "geometry"]], rej,
                      predicate="intersects")
    a.igual(unida.groupby("index_right")["SID74"].sum().sum(),
            pub_nc["total_rectangulos"],
            "y sumados sobre los rectángulos, contando de más")
    a.igual(100 * (pub_nc["total_rectangulos"] / pub_nc["total_condados"] - 1),
            pub_nc["inflacion_pct"], "  la inflación en porcentaje", 1e-6)
    # El reparto por área: |A_ij| / |S_i| por ser extensiva.
    trozos = gpd.overlay(
        nc2264[["SID74", "geometry"]].assign(_a=nc2264.geometry.area),
        rej, how="intersection")
    a.igual((trozos["SID74"] * trozos.geometry.area / trozos["_a"]).sum(),
            pub_nc["total_por_area"],
            "el reparto por área conserva el total", 1e-6)
    a.cierto(abs(pub_nc["total_por_area"] - pub_nc["total_condados"]) < 1e-6,
             "  y conservarlo es la comprobación de que está bien hecho",
             f"{pub_nc['total_por_area']} = {pub_nc['total_condados']}")
    a.cierto(pub_nc["total_rectangulos"] > 3 * pub_nc["total_condados"],
             "el predicado ingenuo infla el total por más de tres",
             f"{pub_nc['total_rectangulos']} frente a {pub_nc['total_condados']}")

    # --- El caso que el mapa del módulo 7 señala (T2.4) ---------------
    #
    # El módulo estrenó un mapa para MOSTRAR lo que hasta T2.3 solo decía:
    # un condado resaltado y las celdas que toca, con lo que aporta a cada
    # una. Aquí se rehace entero —el criterio que elige el condado, sus
    # cifras y el reparto por área celda a celda— y, al final, se comprueba
    # el propio resalte contra la geometría que el mapa DIBUJA. Esto último
    # es lo que importa: que el JSON de cifras y el de mapas coincidan entre
    # sí no dice nada si los dos señalan el rectángulo equivocado.
    caso = pub_nc["condado_caso"]
    par = gpd.sjoin(nc2264[["SID74", "geometry"]], rej, predicate="intersects")
    k_cond = par.groupby(par.index).size().reindex(nc2264.index, fill_value=0)
    exceso = (k_cond - 1) * nc2264["SID74"]
    # La identidad que ata el caso al titular: la inflación entera ES la
    # suma de los excesos condado a condado. Si no lo fuera, el mapa
    # estaría ilustrando un mecanismo distinto del que produce el 2 621.
    a.igual(exceso.sum(), pub_nc["total_rectangulos"] - pub_nc["total_condados"],
            "los excesos condado a condado suman la inflación entera")
    a.igual(exceso.sum(), caso["exceso_total"], "  y es el exceso total que se publica")
    i_caso = int(exceso.to_numpy().argmax())
    a.cierto(int((exceso == exceso.max()).sum()) == 1,
             "el criterio del mapa señala a UN condado",
             f"{int((exceso == exceso.max()).sum())} con el máximo")
    a.cierto(str(nc2264["NAME"].iloc[i_caso]) == caso["nombre"],
             "  y en Python sale el mismo",
             f"{nc2264['NAME'].iloc[i_caso]} / {caso['nombre']}")
    a.igual(i_caso + 1, caso["indice"],
            "  con el índice 1-basado que el mapa usa para resaltarlo")
    a.igual(int(nc2264["SID74"].iloc[i_caso]), caso["sids"], "  sus muertes")
    a.igual(int(k_cond.iloc[i_caso]), caso["n_celdas_toca"], "  las celdas que toca")
    a.igual(int(k_cond.iloc[i_caso]) * int(nc2264["SID74"].iloc[i_caso]),
            caso["aporte_predicado"], "  y lo que aporta emparejando por «se tocan»")
    a.igual(int(exceso.iloc[i_caso]), caso["exceso"], "  su exceso")
    a.igual(100 * exceso.iloc[i_caso] / exceso.sum(), caso["pct_del_exceso"],
            "  y qué parte de la inflación total es", 1e-8)

    # El reparto por área del MISMO condado, celda a celda. Fila y columna
    # se derivan del centroide de la celda —desde el suroeste de la caja—
    # y no del índice: R y este auditor construyen la rejilla en órdenes
    # distintos (`st_make_grid` por filas, el bucle de arriba por
    # columnas), así que emparejar por posición en la lista compararía
    # celdas que no son la misma y daría verde a un mapa torcido.
    gcaso = nc2264.geometry.iloc[i_caso]
    acaso = gcaso.area
    def fila_col(punto):
        return (min(10, int((punto.y - miny) / dy) + 1),
                min(10, int((punto.x - minx) / dx) + 1))
    calc = {}
    for cel in celdas:
        if not cel.intersects(gcaso):
            continue
        calc[fila_col(cel.centroid)] = cel.intersection(gcaso).area / acaso
    pub_rep = {(r["fila"], r["columna"]): r for r in caso["reparto"]}
    a.cierto(set(calc) == set(pub_rep),
             "las celdas del reparto son las que el condado toca",
             f"{sorted(calc)} / {sorted(pub_rep)}")
    for clave in sorted(set(calc) & set(pub_rep)):
        f, c = clave
        a.igual(100 * calc[clave], pub_rep[clave]["fraccion_pct"],
                f"  fila {f}, columna {c}: qué parte del condado cae ahí", 1e-7)
        a.igual(caso["sids"] * calc[clave], pub_rep[clave]["aporte_area"],
                f"    y cuántas muertes le tocan repartiendo", 1e-7)
    a.igual(sum(r["fraccion_pct"] for r in caso["reparto"]), 100,
            "las fracciones reparten el condado entero y nada más", 1e-7)
    a.igual(sum(r["fraccion_pct"] for r in caso["reparto"]),
            caso["fraccion_total_pct"],
            "  y el total que la tabla de respaldo publica es esa suma", 1e-7)
    a.igual(sum(r["aporte_area"] for r in caso["reparto"]), caso["sids"],
            "  y los aportes por área suman sus muertes",   # no cinco veces
            1e-7)
    a.igual(min(r["fraccion_pct"] for r in caso["reparto"]), caso["roce_pct"],
            "la celda del roce es la de menos área", 1e-12)
    a.igual(min(r["aporte_area"] for r in caso["reparto"]), caso["roce_aporte_area"],
            "  y su aporte por área es el menor", 1e-12)
    a.cierto(caso["roce_pct"] < 1,
             "  el roce recibe menos del 1 % del condado",
             f"{caso['roce_pct']} % del área, {caso['aporte_predicado'] // caso['n_celdas_toca']} muertes")

    # --- Y ahora el MAPA, contra la geometría y no contra el otro JSON --
    #
    # Se deshace la cuantización de `geo_partes` —v = q·r/Q + (cx - r/2)—
    # y se pregunta por el terreno: ¿los rectángulos que el lienzo pinta
    # resaltados son los que el condado toca? Un `lineas_resaltadas` que
    # apuntara a otras cinco celdas pasaría cualquier comparación entre los
    # dos JSON, y el mapa saldría dibujado, con su leyenda y sus colores.
    ma = M["agregacion"]
    a.cierto(ma["modo"] == "poligonos", "el mapa del módulo 7 es un coropleto")
    a.igual(ma["n"], len(nc2264), "  con los 100 condados")
    a.igual(ma["n_lineas"], pub_nc["n_celdas"], "  y la rejilla entera encima")
    # El contador contra el array, no solo contra el precálculo. Un
    # `n_lineas` que dijera 100 sobre 96 rectángulos guardados dibujaría una
    # rejilla incompleta sin que nada se quejara: es la misma comprobación
    # que el auditor le hace a `n` contra `geom`, y existe por la misma
    # razón — una cifra declarada que puede discrepar de lo que hay.
    a.igual(len(ma["lineas"]), ma["n_lineas"],
            "  y el n_lineas declarado es el que hay")
    a.igual(ma["resaltado"], caso["indice"], "  el condado del caso, resaltado")
    a.igual(len(ma["lineas_resaltadas"]), caso["n_celdas_toca"],
            "  y tantas celdas resaltadas como toca")
    # El eslabón del CABLEADO: el mapa resalta los índices que el precálculo
    # publica. Es lo que ata la tabla de respaldo —que habla de esas celdas—
    # a los rectángulos que se pintan. El eslabón geométrico va justo debajo.
    a.cierto(list(ma["lineas_resaltadas"]) == list(caso["celdas_tocadas"]),
             "  y son exactamente las que el precálculo publica",
             f"{ma['lineas_resaltadas']} / {caso['celdas_tocadas']}")
    cm = ma["caja"]
    rr = max(cm[2] - cm[0], cm[3] - cm[1])
    ox = cm[0] + (cm[2] - cm[0]) / 2 - rr / 2
    oy = cm[1] + (cm[3] - cm[1]) / 2 - rr / 2
    def desq(plano):
        return [(ox + plano[i] * rr / ma["q"], oy + plano[i + 1] * rr / ma["q"])
                for i in range(0, len(plano), 2)]
    dibujadas = set()
    for k1 in ma["lineas_resaltadas"]:
        anillo = Polygon(desq(ma["lineas"][k1 - 1]))
        dibujadas.add(fila_col(anillo.centroid))
    a.cierto(dibujadas == set(calc),
             "lo que el LIENZO resalta es lo que el condado toca",
             f"{sorted(dibujadas)} / {sorted(calc)}")
    # Y el polígono resaltado es de verdad el condado del caso: el resalte
    # es un índice 1-basado sobre `geom`, y un desplazamiento de uno pinta
    # de naranja al condado vecino sin que nada falle.
    pintado = Polygon(desq(ma["geom"][ma["resaltado"] - 1][0]))
    a.cierto(gcaso.contains(pintado.centroid),
             "  y el naranja cae dentro del condado del caso",
             f"a {gcaso.centroid.distance(pintado.centroid):.0f} pies de su centroide")

    # --- Colombia: la misma variable por dos reglas de agregación ----
    # OJO con la normalización: `st_interpolate_aw(extensive = FALSE)`
    # divide por el área CUBIERTA por las fuentes, no por el área del
    # destino. Aquí no da igual, porque los municipios no teselan los
    # departamentos: la cobertura mínima es del 92,7 %. Dividir por el
    # área del destino da 0.35874 en vez de 0.36824, y esa diferencia en
    # la cuarta cifra es justo la que este auditor existe para no dejar
    # pasar.
    pub_co = ags["colombia"]
    dep_aw = dep.copy()
    dep_aw["_j"] = range(len(dep_aw))
    ov = gpd.overlay(d_ok[["desercion", "geometry"]],
                     dep_aw[["_j", "geometry"]], how="intersection")
    ov["_area"] = ov.geometry.area
    reparto = ov.groupby("_j").apply(
        lambda t: (t["desercion"] * t["_area"]).sum() / t["_area"].sum(),
        include_groups=False)
    dep_aw["desercion_area"] = dep_aw["_j"].map(reparto)
    dos = dep_aw[dep_aw.desercion.notna()
                 & dep_aw.desercion_area.notna()].reset_index(drop=True)
    a.igual(len(dos), pub_co["n_departamentos"],
            "departamentos con las dos reglas")
    a.igual(np.mean(np.abs(dos.desercion - dos.desercion_area)),
            pub_co["dif_media_abs"],
            "diferencia media entre las dos reglas", 1e-7)
    a.igual(np.max(np.abs(dos.desercion - dos.desercion_area)),
            pub_co["dif_max"], "  y la mayor de todas", 1e-7)
    a.igual(dos.desercion.corr(dos.desercion_area), pub_co["cor_reglas"],
            "  correlación entre las dos versiones", 1e-7)
    w_dos = Queen.from_dataframe(dos, use_index=False)
    w_dos.transform = "r"
    k = (len(dos) - len(w_dos.islands)) / len(dos)
    a.igual(Moran(dos.desercion.to_numpy(), w_dos, permutations=0).I * k,
            pub_co["moran_sin_ponderar"],
            "I departamental sin ponderar (convenio spdep)", 1e-6)
    a.igual(Moran(dos.desercion_area.to_numpy(), w_dos, permutations=0).I * k,
            pub_co["moran_por_area"], "  y ponderando por área", 1e-6)
    # La bisagra: si la I sin ponderar NO fuera la que publica el módulo,
    # este bloque estaría comparando contra otra agregación y la lección
    # entera —«la regla cambia el resultado»— no probaría nada.
    a.igual(pub_co["moran_sin_ponderar"], esc["moran_departamental"],
            "y es exactamente la I que el módulo 7 publica", 1e-12)
    a.cierto(pub_co["moran_sin_ponderar"] > pub_co["moran_por_area"],
             "cambiar de regla mueve el I sin mover una sola frontera",
             f"{pub_co['moran_sin_ponderar']:.5f} -> "
             f"{pub_co['moran_por_area']:.5f}")

    # =================================================================
    a.titulo("2d · Las discrepancias R↔Python, declaradas")
    # =================================================================
    # La lección de A.2: una discrepancia DOCUMENTADA es material
    # didáctico y una sin explicar es un fallo, y sobre un informe se
    # leen igual. Así que aquí no basta con que la lista exista: cada
    # entrada tiene que reproducir sus dos valores y traer su causa.
    disc = {d["id"]: d for d in D["discrepancias"]}
    a.cierto("moran_islas" in disc,
             "la discrepancia del I de Moran está declarada")
    a.cierto("moran_islas_dep" in disc,
             "la de la escala departamental también")
    a.cierto("tipo_geometria_nc" in disc,
             "y la del tipo de geometría de nc")
    # Si falta alguna, el auditor tiene que informar del fallo y seguir,
    # no reventar con un KeyError: un traceback también devuelve código
    # distinto de cero y el arnés lo contaría como acierto, pero sobre el
    # informe no se distingue de una caída del propio auditor.
    VACIA = {"valor_r": float("nan"), "valor_python": float("nan"),
             "diferencia": float("nan"), "causa": "", "va_a": ""}
    for d in D["discrepancias"]:
        a.cierto(len(d["causa"]) > 60,
                 f"«{d['id']}»: la causa está explicada",
                 f"{len(d['causa'])} caracteres, no solo el nombre")
        a.cierto("capítulo" in d["va_a"],
                 f"«{d['id']}»: se dice a qué capítulo va", d["va_a"])
        a.igual(abs(d["valor_python"] - d["valor_r"]), d["diferencia"],
                f"«{d['id']}»: la diferencia publicada", 1e-7)
        a.cierto(d["diferencia"] > 0,
                 f"«{d['id']}»: y no es una discrepancia de cero")
    a.igual(disc.get("moran_islas", VACIA)["valor_python"], mi.I,
            "«moran_islas»: Python reproduce el de la ficha", 1e-6)
    a.igual(disc.get("moran_islas", VACIA)["valor_r"], esc["moran_municipal"],
            "«moran_islas»: y el de R es el que publica el módulo 7", 1e-9)
    a.igual(disc.get("moran_islas_dep", VACIA)["valor_python"], mid.I,
            "«moran_islas_dep»: Python reproduce el suyo", 1e-6)
    a.igual(disc.get("tipo_geometria_nc", VACIA)["valor_python"],
            (nc.geometry.geom_type == "MultiPolygon").sum(),
            "«tipo_geometria_nc»: Python reproduce el suyo")
    a.igual(disc.get("tipo_geometria_nc", VACIA)["valor_r"], an["n_multipolygon"],
            "«tipo_geometria_nc»: y el de R es el del módulo 9")

    # =================================================================
    a.titulo("2c · La correlación a dos escalas")
    # =================================================================
    s11 = pd.read_csv(PROCESADO / "municipios_saber11.csv", dtype={"divipola": str})
    ec = D["escala_correlacion"]
    tab = llave.merge(s11, on="divipola", how="left", suffixes=("", "_y"))
    tab["dpto"] = tab.divipola.str[:2]
    dep_tab = tab.groupby("dpto")[["s11_punt_medio", "s11_pct_internet"]].mean()
    rm = tab[["s11_punt_medio", "s11_pct_internet"]].corr().iloc[0, 1]
    rd = dep_tab.corr().iloc[0, 1]
    a.igual(rm, ec["principal"]["r_municipal"], "r municipal del par principal", 1e-6)
    a.igual(rd, ec["principal"]["r_departamental"], "r departamental", 1e-6)
    # OJO CON LAS BANDERAS. La primera versión de estas dos comprobaciones
    # leía `estable_ante_unidades_pequenas` y `monotono` del propio JSON y
    # las daba por buenas. El arnés de inyección lo destapó: cambiando
    # `diferencia_umbral_30` a 0.41 el archivo seguía declarándose estable
    # y el auditor pasaba. Una comprobación que cree la autodeclaración
    # del archivo que audita no comprueba nada — es la misma trampa que
    # las dos comprobaciones «incapaces de fallar» de T0.5. Ahora las dos
    # banderas se RECALCULAN desde el barrido.
    rs = [b["r"] for b in ec["principal"]["barrido"]]
    a.igual(abs(rs[2] - rs[0]), ec["principal"]["diferencia_umbral_30"],
            "la diferencia con el umbral n>=30 sale del barrido", 1e-7)
    a.cierto(ec["principal"]["estable_ante_unidades_pequenas"] ==
             (abs(rs[2] - rs[0]) < 0.05),
             "la bandera de estabilidad dice lo que el barrido dice",
             f"dif {abs(rs[2] - rs[0]):.5f}")
    a.cierto(abs(rs[2] - rs[0]) < 0.05,
             "y la r municipal no la ponen los municipios diminutos")
    a.cierto(ec["principal"]["monotono"] ==
             all(rs[i] <= rs[i + 1] for i in range(len(rs) - 1)),
             "la bandera de monotonía dice lo que el barrido dice")
    a.cierto(all(rs[i] <= rs[i + 1] for i in range(len(rs) - 1)),
             "y el barrido por umbral es monótono",
             " <= ".join(f"{r:.4f}" for r in rs))
    a.igual(max(rs) - min(rs), ec["principal"]["recorrido_barrido"],
            "el recorrido del barrido", 1e-7)
    a.igual(len(ec["pares"]), ec["n_pares"], "pares publicados")
    a.igual(ec["n_suben"] + ec["n_bajan"], ec["n_pares"],
            "todos los pares están clasificados")
    a.cierto(ec["n_suben"] > 0 and ec["n_bajan"] > 0,
             "agregar NO mueve todos los pares en la misma dirección",
             f"{ec['n_suben']} suben, {ec['n_bajan']} bajan")
    a.cierto(ec["n_invierten"] >= 1,
             "y al menos uno invierte el signo",
             f"{ec['n_invierten']}")
    for p in ec["pares"]:
        a.igual(p["r_departamental"] / p["r_municipal"], p["razon"],
                f"razón del par {p['a']}~{p['b']}", 1e-7)
        a.igual(100 * (p["razon"] - 1), p["cambio_pct"],
                f"  y su cambio porcentual", 1e-6)
        a.cierto(abs(p["r_municipal"]) > 0.20,
                 f"{p['a']}~{p['b']}: señal municipal",
                 f"{p['r_municipal']:.5f}")
        a.cierto(p["invierte_signo"] ==
                 (math.copysign(1, p["r_municipal"]) !=
                  math.copysign(1, p["r_departamental"])),
                 f"  la marca de inversión de signo es correcta")

    # Los 13 pares, recalculados desde el CSV y no solo sus cocientes. Hasta
    # el 2026-09-24 este auditor rehacía el par principal y se fiaba del
    # resto, y el recuadro del módulo 7 cuenta los trece.
    dep_todos = tab.groupby("dpto")[list(dict.fromkeys(c for p in ec["pares"] for c in (p["a"], p["b"])))].mean()
    for p in ec["pares"]:
        a.igual(tab[p["a"]].corr(tab[p["b"]]), p["r_municipal"],
                f"r municipal de {p['a_corta']} × {p['b_corta']}", 1e-7)
        a.igual(dep_todos[p["a"]].corr(dep_todos[p["b"]]), p["r_departamental"],
                f"  y la departamental", 1e-7)
    baja = [abs(p["r_departamental"]) <= abs(p["r_municipal"]) for p in ec["pares"]]
    a.igual(len(baja) - sum(baja), ec["n_suben"], "pares que suben, contados aquí")
    a.igual(sum(baja), ec["n_bajan"], "pares que bajan, contados aquí")
    a.igual(sum(p["invierte_signo"] for p in ec["pares"]), ec["n_invierten"],
            "pares que cambian de signo, contados aquí")
    a.igual(sum(p["invierte_signo"] and b for p, b in zip(ec["pares"], baja)),
            ec["n_invierten_entre_bajan"], "los que cambian de signo, dentro de los que bajan")

    # --- El caso de aviso y su barrido ------------------------------------
    # La prosa dice que el único cambio de signo es el del estrato y que no
    # aguanta la receta del par principal. Cada pieza se rehace aquí.
    from scipy import stats
    av = ec["caso_aviso"]
    A, B = av["a"], av["b"]

    def r_dep(t):
        g = t.groupby("dpto")[[A, B]].mean()
        return g[A].corr(g[B]), len(g)

    a.cierto([(p["a"], p["b"]) for p in ec["pares"] if p["invierte_signo"]] == [(A, B)],
             "el único par que cambia de signo es el del aviso")
    dep_av = tab.groupby("dpto")[[A, B]].mean()
    a.igual(len(dep_av), av["n_departamentos"], "departamentos del aviso")
    a.igual(stats.pearsonr(dep_av[A], dep_av[B]).pvalue, av["p_departamental"],
            "p de la r departamental del aviso", 1e-7)
    cob = tab["s11_n_estrato"] / tab["s11_n"]
    a.igual(cob.corr(tab["s11_punt_medio"]), av["cor_cobertura_puntaje"],
            "cobertura del estrato contra puntaje", 1e-7)
    bajo = cob.notna() & (cob < av["cobertura_umbral"])
    a.igual(int(bajo.sum()), av["n_bajo_umbral"], "municipios con el estrato poco declarado")
    r_cob, n_cob = r_dep(tab[cob.notna() & ~bajo])
    a.igual(r_cob, av["r_departamental_sin_bajo_umbral"], "r departamental sin esos municipios", 1e-7)
    a.igual(n_cob, av["n_departamentos"], "  y el filtro no se lleva ningún departamento")
    a.igual(av["umbral_n"], ec["principal"]["barrido"][2]["umbral"],
            "el umbral de n es el del barrido del par principal")
    r_30, n_30 = r_dep(tab[tab["s11_n"] >= av["umbral_n"]])
    a.igual(r_30, av["r_departamental_n30"], "r departamental con n >= 30", 1e-7)
    a.igual(n_30, av["n_departamentos"], "  y el filtro no se lleva ningún departamento")

    con_b = tab.index[tab[B].notna()]
    a.igual(len(con_b), av["n_municipios_con_estrato"], "municipios con estrato")
    loo = pd.Series({i: r_dep(tab.drop(index=i))[0] for i in con_b})
    a.igual(loo.min(), av["loo_min"], "quitar un municipio: la r más baja", 1e-7)
    a.igual(loo.max(), av["loo_max"], "quitar un municipio: la r más alta", 1e-7)
    inf_ = av["influyente"]
    k = loo.idxmax()
    a.cierto(tab.at[k, "municipio"] == inf_["municipio"]
             and tab.at[k, "departamento"] == inf_["departamento"],
             "el municipio que más la mueve", f"{tab.at[k, 'municipio']}, {tab.at[k, 'departamento']}")
    a.igual(r_dep(tab.drop(index=k))[0], inf_["r_departamental_sin_el"], "  la r sin él", 1e-7)
    a.igual(tab.at[k, "s11_n"], inf_["n_estudiantes"], "  sus estudiantes")
    a.igual(tab.at[k, "s11_n_estrato"], inf_["n_con_estrato"], "  los que declararon estrato")
    a.igual(tab.at[k, B], inf_["estrato_medio"], "  su estrato medio", 1e-7)
    a.igual(tab.at[k, A], inf_["pct_internet"], "  sus hogares con internet", 1e-7)
    e_con = tab.groupby("dpto")[B].mean().sort_values(ascending=False)
    e_sin = tab.drop(index=k).groupby("dpto")[B].mean().sort_values(ascending=False)
    dk = tab.at[k, "dpto"]
    a.igual(e_con[dk], inf_["estrato_departamento_con"], "  el estrato de su departamento", 1e-7)
    a.igual(e_sin[dk], inf_["estrato_departamento_sin"], "  y sin él", 1e-7)
    a.igual(list(e_con.index).index(dk) + 1, inf_["puesto_con"], "  el puesto de su departamento")
    a.igual(list(e_sin.index).index(dk) + 1, inf_["puesto_sin"], "  y sin él")
    seg = e_con.index[1]
    a.cierto(tab.loc[tab["dpto"] == seg, "departamento"].iloc[0] == inf_["segundo"],
             "  el departamento que queda segundo", inf_["segundo"])
    a.igual(e_con[seg], inf_["estrato_segundo"], "  y su estrato medio", 1e-7)

    # La tesis del recuadro sin el par dudoso.
    sub30 = tab[tab["s11_n"] >= av["umbral_n"]]
    esperado = [(p["a"], p["b"]) for p, b in zip(ec["pares"], baja) if b and B not in (p["a"], p["b"])]
    a.cierto([(q["a"], q["b"]) for q in av["bajan_sin_estrato"]] == esperado,
             "los pares sin estrato que bajan", str(len(esperado)))
    for q in av["bajan_sin_estrato"]:
        g = sub30.groupby("dpto")[[q["a"], q["b"]]].mean()
        rm30 = sub30[q["a"]].corr(sub30[q["b"]])
        rd30 = g[q["a"]].corr(g[q["b"]])
        a.igual(rm30, q["r_municipal_n30"], f"{q['a_corta']} × {q['b_corta']}, n >= 30", 1e-7)
        a.igual(rd30, q["r_departamental_n30"], "  y su departamental", 1e-7)
        a.cierto(abs(rd30) <= abs(rm30), "  y sigue bajando", f"{rm30:.5f} -> {rd30:.5f}")

    # =================================================================
    a.titulo("3a · El Monte Carlo del error estándar")
    # =================================================================
    inf = D["inferencia"]
    a.igual(inf["k"] ** 2, inf["n"], "la retícula cuadra con su n")
    a.cierto(inf["nrep"] >= 1000, "réplicas suficientes", str(inf["nrep"]))
    fila = inf["rejilla"]
    a.igual(len(fila), 7, "valores de phi tabulados")
    # T2.2 · la retícula se reconstruye AQUÍ, con la escala que el capítulo
    # declara —distancia euclídea entre centros de celda, en pasos de
    # retícula—, para poder rehacer 1'R1 sin pasar por n_eff. Comprobar
    # `efecto_diseno == n/n_eff` sería comprobar una división; esto
    # comprueba el número, y se pone rojo si R cambiara de escala sin
    # decirlo en `escala_h`.
    _xy = np.array([(x, y) for y in range(1, inf["k"] + 1)
                    for x in range(1, inf["k"] + 1)], float)
    _DIST = np.sqrt(((_xy[:, None, :] - _xy[None, :, :]) ** 2).sum(-1))
    a.cierto(str(inf.get("escala_h", "")).strip() != "",
             "la escala de h está declarada", str(inf.get("escala_h", ""))[:46])
    a.igual(inf.get("sigma"), 1, "la varianza marginal declarada es 1")
    # R1 · T1.6 (C1-26) · el nivel de la prueba que el módulo 6 enuncia.
    from scipy import stats as _st4
    a.igual(float(_st4.t.ppf(1 - inf["alfa"] / 2, inf["n"] - 1)), inf["t_critico"],
            "el t crítico es el bilateral de ese alfa", 1e-8)
    a.igual(100 * inf["alfa"], D["una_realizacion"]["pct_esperado_si_valiera"],
            "y el porcentaje que «debería» rechazar es ese alfa")
    cobs, neffs, facs = [], [], []
    for r in fila:
        phi = r["phi"]
        # rho entre vecinos inmediatos: exp(-1/phi)
        esperado = 0.0 if phi <= 0 else math.exp(-1 / phi)
        a.igual(esperado, r["rho_vecino"], f"phi={phi}: correlación entre vecinos", 1e-9)
        # Y la de la diagonal, a h = sqrt(2). Es la que distingue «h es
        # distancia» de «h es adyacencia»: con la segunda valdría lo mismo
        # que la de arriba, y el capítulo publica las dos justo por eso.
        esp_diag = 0.0 if phi <= 0 else math.exp(-math.sqrt(2) / phi)
        a.igual(esp_diag, r["rho_diagonal"], f"phi={phi}: correlación en diagonal", 1e-9)
        Rm = np.eye(inf["n"]) if phi <= 0 else np.exp(-_DIST / phi)
        a.igual(Rm.sum() / inf["n"], r["efecto_diseno"],
                f"phi={phi}: efecto de diseño rehecho desde 1'R1", 1e-6)
        a.igual(inf["n"] ** 2 / Rm.sum(), r["n_eff"],
                f"phi={phi}: y el n_eff de esa misma suma", 1e-6)
        a.igual(r["factor"] ** 2, r["inflacion_varianza"],
                f"phi={phi}: la inflación de varianza es factor^2", 1e-6)
        # E[s^2] = sigma^2 (n/(n-1))(1 - 1/n_eff). Es la identidad con la
        # que el módulo 4 explica por qué sus dos cocientes no coinciden,
        # así que se comprueba la fórmula Y su medida.
        a.igual((inf["n"] / (inf["n"] - 1)) * (1 - 1 / r["n_eff"]), r["s2_esperada"],
                f"phi={phi}: E[s^2] teórica", 1e-7)
        a.cierto(abs(r["s2_medida"] - r["s2_esperada"]) <= 0.06 * r["s2_esperada"],
                 f"phi={phi}: la s^2 simulada cuadra con la teórica",
                 f"{r['s2_medida']:.5f} frente a {r['s2_esperada']:.5f}")
        # Var(Zbar) = 1'R1/n^2 = 1/n_eff  =>  ee_exacto = 1/sqrt(n_eff)
        a.igual(1 / math.sqrt(r["n_eff"]), r["ee_exacto"],
                f"phi={phi}: ee exacto frente a n_eff", 1e-7)
        a.igual(r["ee_real"] / r["ee_ingenuo"], r["factor"],
                f"phi={phi}: el factor sale de sus dos e.e.", 1e-7)
        a.cierto(abs(r["ee_real"] - r["ee_exacto"]) <= 0.06 * r["ee_exacto"],
                 f"phi={phi}: la simulación reproduce el e.e. exacto",
                 f"{r['ee_real']:.5f} frente a {r['ee_exacto']:.5f}")
        emc = math.sqrt(r["cobertura"] * (1 - r["cobertura"]) / inf["nrep"])
        a.igual(emc, r["emc_cobertura"], f"phi={phi}: error de Monte Carlo", 1e-9)
        a.cierto(0 <= r["cobertura"] <= 1, f"phi={phi}: la cobertura es una proporción")
        a.cierto(0 < r["n_eff"] <= inf["n"] + 1e-6,
                 f"phi={phi}: n_eff no supera n", f"{r['n_eff']:.4f}")
        cobs.append(r["cobertura"]); neffs.append(r["n_eff"]); facs.append(r["factor"])

    a.cierto(all(cobs[i] > cobs[i + 1] for i in range(len(cobs) - 1)),
             "la cobertura cae de forma monótona al subir phi")
    a.cierto(all(neffs[i] > neffs[i + 1] for i in range(len(neffs) - 1)),
             "y el n efectivo también")
    a.cierto(all(facs[i] < facs[i + 1] for i in range(len(facs) - 1)),
             "y el factor de subestimación sube")
    a.igual(fila[0]["n_eff"], inf["n"], "sin correlación, n_eff = n", 1e-6)
    a.cierto(abs(cobs[0] - 0.95) <= 4 * fila[0]["emc_cobertura"],
             "sin correlación la cobertura es la nominal del 95 %",
             f"{cobs[0]:.5f} ± {fila[0]['emc_cobertura']:.5f}")
    a.igual(cobs[0], inf["cobertura_independiente"], "la cifra de cierre coincide")
    i4 = [i for i, r in enumerate(fila) if r["phi"] == 4][0]
    a.igual(fila[i4]["cobertura"], inf["cobertura_phi4"], "cobertura con phi=4")
    a.igual(fila[i4]["factor"], inf["factor_phi4"], "factor con phi=4")
    a.igual(fila[i4]["n_eff"], inf["n_eff_phi4"], "n_eff con phi=4")
    # T2.2 · las copias de cierre del puente, y la desigualdad que la prosa
    # afirma. Que sea SOLO en phi = 4 no es pereza: está medido que en
    # phi = 0 y 0.5 se invierte, porque ahí s^2 apenas se encoge.
    a.igual(fila[i4]["efecto_diseno"], inf["efecto_diseno_phi4"], "efecto de diseño con phi=4")
    a.igual(fila[i4]["inflacion_varianza"], inf["inflacion_varianza_phi4"],
            "inflación de varianza con phi=4")
    a.igual(fila[i4]["s2_esperada"], inf["s2_esperada_phi4"], "E[s^2] con phi=4")
    a.cierto(inf["inflacion_varianza_phi4"] > inf["efecto_diseno_phi4"],
             "con phi=4 la declarada se queda más corta que la real",
             f"{inf['inflacion_varianza_phi4']:.5f} frente a {inf['efecto_diseno_phi4']:.5f}")
    a.cierto(0 < inf["s2_esperada_phi4"] < 1,
             "y la razón está publicada: E[s^2] es menor que sigma^2",
             f"{inf['s2_esperada_phi4']:.5f}")

    # R2 · T2.4 · los cien intervalos que el módulo 4 dibuja. Las cien medias
    # y sus semianchos salen del generador de R y no se pueden rehacer aquí;
    # lo que sí: el error estándar verdadero (de 1'R1, con la retícula de
    # arriba), el cuantil, los recuentos, y que las cien se comporten como
    # una muestra de las réplicas que el módulo publica. Tolerancias: una
    # proporción sobre 100 tiene error sqrt(p(1 - p)/100), se le dejan 3; la
    # media de 100 medias, ee_exacto/10, se le dejan 4; una desviación típica
    # de 100 valores, un 7 % (1/sqrt(200)), se le dejan 4.
    a.igual(100 * (1 - inf["alfa"]), inf["nivel_pct"], "el nivel de los intervalos es el de alfa", 1e-9)
    ci = inf["cien_ic"]
    r4a = fila[i4]
    n_ci = ci["n"]
    a.igual(ci["phi"], r4a["phi"], "los cien intervalos son los de phi = 4")
    a.cierto(len(ci["media"]) == len(ci["semiancho_ingenuo"]) == n_ci == 100,
             "cien medias con sus cien semianchos")
    ee_ex4 = math.sqrt(np.exp(-_DIST / ci["phi"]).sum()) / inf["n"]
    a.igual(ee_ex4, ci["ee_exacto"], "e.e. verdadero de la media, desde 1'R1", 1e-8)
    a.igual(float(_st4.norm.ppf(1 - inf["alfa"] / 2)), ci["z_critico"],
            "el cuantil normal bilateral de ese alfa", 1e-8)
    a.igual(ci["z_critico"] * ee_ex4, ci["semiancho_exacto"], "semiancho con el e.e. verdadero", 1e-8)
    m_ci, h_ci = np.array(ci["media"]), np.array(ci["semiancho_ingenuo"])
    a.igual(int((np.abs(m_ci) <= h_ci).sum()), ci["n_cubren_ingenuo"],
            "intervalos ingenuos que cubren el cero, recontados")
    a.igual(int((np.abs(m_ci) <= ci["semiancho_exacto"]).sum()), ci["n_cubren_exacto"],
            "y con el e.e. verdadero, recontados")
    a.igual(float(h_ci.mean()), ci["semiancho_ingenuo_medio"], "semiancho ingenuo medio", 1e-8)
    a.igual(ci["semiancho_exacto"] / float(h_ci.mean()), ci["razon_semianchos"],
            "cociente de los dos semianchos", 1e-7)
    a.cierto(abs(ci["n_cubren_ingenuo"] / n_ci - r4a["cobertura"])
             <= 3 * math.sqrt(r4a["cobertura"] * (1 - r4a["cobertura"]) / n_ci),
             "los cien son compatibles con la cobertura publicada",
             f"{ci['n_cubren_ingenuo']} de {n_ci} frente a {r4a['cobertura']:.5f}")
    a.cierto(abs(float(h_ci.mean()) / inf["t_critico"] - r4a["ee_ingenuo"]) <= 0.06 * r4a["ee_ingenuo"],
             "sus semianchos son t por el e.e. ingenuo del módulo",
             f"{float(h_ci.mean()) / inf['t_critico']:.5f} frente a {r4a['ee_ingenuo']:.5f}")
    a.cierto(abs(float(m_ci.mean())) <= 4 * ee_ex4 / math.sqrt(n_ci),
             "las cien medias se centran en la media verdadera", f"{float(m_ci.mean()):.5f}")
    a.cierto(abs(float(m_ci.std(ddof=1)) / ee_ex4 - 1) <= 4 / math.sqrt(2 * n_ci),
             "y se dispersan como dice el e.e. verdadero",
             f"{float(m_ci.std(ddof=1)):.5f} frente a {ee_ex4:.5f}")
    a.igual(math.sqrt(ci["cobertura_exacto"] * (1 - ci["cobertura_exacto"]) / inf["nrep"]),
            ci["emc_cobertura_exacto"], "error de Monte Carlo de la cobertura exacta", 1e-9)
    a.cierto(abs(ci["cobertura_exacto"] - (1 - inf["alfa"])) <= 4 * ci["emc_cobertura_exacto"],
             "con el e.e. verdadero la cobertura es la nominal",
             f"{ci['cobertura_exacto']:.5f} ± {ci['emc_cobertura_exacto']:.5f}")
    a.cierto(abs(ci["n_cubren_exacto"] / n_ci - ci["cobertura_exacto"])
             <= 3 * math.sqrt(ci["cobertura_exacto"] * (1 - ci["cobertura_exacto"]) / n_ci),
             "y los cien, compatibles con ella", f"{ci['n_cubren_exacto']} de {n_ci}")
    # Y simulando aquí, con numpy: la cobertura con el e.e. verdadero es la
    # nominal y la ingenua es la del módulo. 2 000 campos, otro generador.
    L4 = np.linalg.cholesky(np.exp(-_DIST / ci["phi"]) + inf["jitter"] * np.eye(inf["n"]))
    Z4 = L4 @ np.random.default_rng(20929).standard_normal((inf["n"], 2000))
    med4, ee4 = Z4.mean(axis=0), Z4.std(axis=0, ddof=1) / math.sqrt(inf["n"])
    cob_ex_py = float((np.abs(med4) <= ci["semiancho_exacto"]).mean())
    cob_in_py = float((np.abs(med4) <= inf["t_critico"] * ee4).mean())
    a.cierto(abs(cob_ex_py - ci["cobertura_exacto"])
             <= 4 * math.hypot(ci["emc_cobertura_exacto"], math.sqrt(0.95 * 0.05 / 2000)),
             "2 000 campos de aquí dan la misma cobertura exacta", f"{cob_ex_py:.5f}")
    a.cierto(abs(cob_in_py - r4a["cobertura"])
             <= 4 * math.hypot(r4a["emc_cobertura"], math.sqrt(cob_in_py * (1 - cob_in_py) / 2000)),
             "y la misma cobertura ingenua que el módulo", f"{cob_in_py:.5f}")

    # =================================================================
    a.titulo("3b · La réplica sobre dato real")
    # =================================================================
    ir = D["inferencia_real"]
    a.igual(ir["n_municipios"], esc["n_municipal"], "los mismos municipios que en Moran")
    a.igual(d_ok.desercion.mean(), ir["media"], "media de la deserción", 1e-8)
    a.igual(d_ok.desercion.std(ddof=1) / math.sqrt(len(d_ok)), ir["ee_analitico"],
            "el e.e. analítico bajo independencia", 1e-8)
    # El bootstrap i.i.d. tiene que reproducir el e.e. analítico: son dos
    # caminos al mismo número, y si no coincidieran el remuestreo estaría
    # mal montado y el factor de más abajo no significaría nada.
    a.cierto(abs(ir["ee_bootstrap_iid"] - ir["ee_analitico"]) <=
             0.05 * ir["ee_analitico"],
             "el bootstrap i.i.d. reproduce el e.e. analítico",
             f"{ir['ee_bootstrap_iid']:.5f} frente a {ir['ee_analitico']:.5f}")
    a.igual(ir["ee_bootstrap_bloques"] / ir["ee_bootstrap_iid"], ir["factor"],
            "el factor sale de los dos e.e.", 1e-7)
    a.cierto(ir["factor"] > 1,
             "respetar el espacio ENSANCHA el error estándar",
             f"{ir['factor']:.5f}")
    a.igual(ir["n_municipios"] * (ir["ee_bootstrap_iid"] /
                                  ir["ee_bootstrap_bloques"]) ** 2, ir["n_eff"],
            "el n efectivo sale del factor", 1e-6)
    a.igual(100 * ir["n_eff"] / ir["n_municipios"], ir["pct_informacion"],
            "el porcentaje de información", 1e-6)
    a.cierto(ir["n_eff"] < ir["n_municipios"], "y es menor que n")
    a.igual(ir["ic_iid"][1] - ir["ic_iid"][0], ir["ancho_iid"], "ancho del IC ingenuo", 1e-8)
    a.igual(ir["ic_bloques"][1] - ir["ic_bloques"][0], ir["ancho_bloques"],
            "ancho del IC por bloques", 1e-8)
    a.cierto(ir["ic_bloques"][0] < ir["ic_iid"][0] and
             ir["ic_iid"][1] < ir["ic_bloques"][1],
             "el IC honesto contiene al ingenuo")
    a.igual((ir["ic_iid"][0] + ir["ic_iid"][1]) / 2, ir["media"],
            "los dos IC están centrados en la media", 1e-7)
    a.igual((ir["ic_bloques"][0] + ir["ic_bloques"][1]) / 2, ir["media"],
            "  y el de bloques también", 1e-7)

    # --- R1 · T1.6 (C1-17) · dónde caen las réplicas, y cuánto se le puede
    # creer al error estándar por bloques ---------------------------------
    #
    # Las identidades entre lo publicado, a 1e-8. Y lo que es Monte Carlo,
    # rehecho aquí por otro camino y con otro generador, con tolerancias que
    # se razonan como en el ejercicio 3:
    #   · la media de las réplicas por bloques: R la publica con B = 4 000 y
    #     un error de Monte Carlo `emc_media_bloques`; la referencia de aquí
    #     usa 400 000 réplicas (diez veces menos ruido). Se pide que queden
    #     a menos de cinco de esos errores.
    #   · el factor sin un departamento: R usa B = 20 000 y aquí 50 000. El
    #     ruido relativo de una desviación típica estimada con B réplicas es
    #     1/sqrt(2B) ≈ 0.5 % si las medias fueran normales; no lo son del
    #     todo —colas—, así que se pide un 5 % al factor y un 10 % al n
    #     efectivo, que lleva el factor al cuadrado. Es ancho y aun así
    #     separa lo que la prosa afirma: el departamento del extremo queda a
    #     más de un 5 % del siguiente.
    rp_, os_, su_ = ir["replicas"], ir["otras_semillas"], ir["sin_un_departamento"]
    x_d = d_ok.desercion.to_numpy()
    cod_d = d_ok.divipola.str[:2].to_numpy()
    cods = np.unique(cod_d)
    sum_d = np.array([x_d[cod_d == k].sum() for k in cods])
    tam_d = np.array([(cod_d == k).sum() for k in cods])
    nom_d = [d_ok.departamento[cod_d == k].iloc[0] for k in cods]
    a.igual(len(cods), ir["n_departamentos"], "departamentos (bloques del remuestreo)")
    a.igual(int(tam_d.min()), rp_["bloque_min"], "el departamento más pequeño")
    a.igual(int(tam_d.max()), rp_["bloque_max"], "  y el más grande")
    a.igual(rp_["media_bloques"] - ir["media"], rp_["desvio_bloques"],
            "el desvío de las réplicas por bloques es su media menos la muestral", 1e-8)
    a.igual(rp_["media_iid"] - ir["media"], rp_["desvio_iid"], "  y el de las i.i.d.", 1e-8)
    a.igual(ir["ee_bootstrap_bloques"] / math.sqrt(ir["nboot"]), rp_["emc_media_bloques"],
            "el error de Monte Carlo de la media de las réplicas por bloques", 1e-8)
    a.igual(ir["ee_bootstrap_iid"] / math.sqrt(ir["nboot"]), rp_["emc_media_iid"],
            "  y el de las i.i.d.", 1e-8)
    a.igual(rp_["esperanza_bloques"] - ir["media"], rp_["desvio_esperanza"],
            "el desvío de la esperanza de las réplicas por bloques", 1e-8)
    a.igual(100 * rp_["desvio_esperanza"] / ir["ee_bootstrap_bloques"], rp_["desvio_esperanza_pct_ee"],
            "  y como porcentaje del e.e. por bloques", 1e-6)
    a.cierto(rp_["nrep_esperanza"] >= 1_000_000,
             "la esperanza se calcula con al menos un millón de réplicas", str(rp_["nrep_esperanza"]))
    a.cierto(abs(rp_["desvio_iid"]) < 3 * rp_["emc_media_iid"],
             "las réplicas i.i.d. sí están centradas en la media muestral",
             f"{rp_['desvio_iid']:.5f} frente a un e.M.C. de {rp_['emc_media_iid']:.5f}")
    rng_d = np.random.default_rng(20929)

    def medias_bloques(sumas, tams, lotes):
        out = []
        for _ in range(lotes):
            sel = rng_d.integers(0, len(sumas), (10_000, len(sumas)))
            out.append(sumas[sel].sum(axis=1) / tams[sel].sum(axis=1))
        return np.concatenate(out)

    ref_d = medias_bloques(sum_d, tam_d, 40)
    emc_ref = ref_d.std(ddof=1) / math.sqrt(len(ref_d))
    # R2 de T1.6 · LA ESPERANZA DE LAS RÉPLICAS, y no la media de 4 000. R la
    # calcula con 2·10^6 réplicas multinomiales; aquí, con 400 000 de otro
    # generador. Cada una trae su error de Monte Carlo, y se pide que
    # difieran menos de cinco veces el error conjunto. El error que R declara
    # tiene que ser el de ese número de réplicas: la desviación de una media
    # por bloques entre la raíz de las réplicas, con un 10 % de holgura
    # porque la desviación de aquí también es una estimación.
    a.cierto(abs(rp_["esperanza_bloques"] - ref_d.mean())
             < 5 * math.hypot(rp_["emc_esperanza"], emc_ref),
             "la esperanza de las réplicas por bloques, rehecha con 400 000",
             f"R {rp_['esperanza_bloques']:.5f} ± {rp_['emc_esperanza']:.5f} · "
             f"aquí {ref_d.mean():.5f} ± {emc_ref:.5f}")
    a.cierto(abs(rp_["emc_esperanza"] * math.sqrt(rp_["nrep_esperanza"]) / ref_d.std(ddof=1) - 1) < 0.10,
             "  y su error de Monte Carlo es el de ese número de réplicas",
             f"{rp_['emc_esperanza']:.6f}")
    a.cierto(ref_d.mean() - x_d.mean() > 10 * emc_ref,
             "el desvío no es de la semilla de R: aquí también queda por encima de la muestral",
             f"{ref_d.mean() - x_d.mean():.5f} con un e.M.C. de {emc_ref:.5f}")
    a.cierto(rp_["desvio_esperanza"] > 10 * rp_["emc_esperanza"],
             "en lo publicado el desvío de la esperanza supera diez veces su error",
             f"{rp_['desvio_esperanza'] / rp_['emc_esperanza']:.1f} errores de Monte Carlo")
    a.cierto(abs(rp_["media_bloques"] - rp_["esperanza_bloques"]) < 4 * rp_["emc_media_bloques"],
             "las 4 000 réplicas del módulo son compatibles con esa esperanza",
             f"{rp_['media_bloques']:.5f} frente a {rp_['esperanza_bloques']:.5f}")
    ee_iid_d = x_d.std(ddof=0) / math.sqrt(len(x_d))
    fac_ref = ref_d.std(ddof=1) / ee_iid_d
    neff_ref = len(x_d) / fac_ref ** 2
    a.cierto(abs(ir["factor"] / fac_ref - 1) < 0.06,
             "el factor del módulo, rehecho con 400 000 réplicas",
             f"R {ir['factor']:.5f} · aquí {fac_ref:.5f}")
    # Otras semillas.
    a.cierto(os_["n"] >= 10 and os_["factor_min"] < os_["factor_max"],
             "otras semillas: hay un rango", f"{os_['n']} parejas")
    a.igual(ir["n_municipios"] / os_["factor_max"] ** 2, os_["n_eff_min"],
            "otras semillas: el n efectivo mínimo es el del factor máximo", 1e-6)
    a.igual(ir["n_municipios"] / os_["factor_min"] ** 2, os_["n_eff_max"],
            "  y el máximo, el del mínimo", 1e-6)
    a.cierto(os_["n_eff_min"] <= neff_ref <= os_["n_eff_max"],
             "otras semillas: el rango contiene a la referencia",
             f"{os_['n_eff_min']:.3f} a {os_['n_eff_max']:.3f} · referencia {neff_ref:.3f}")
    a.cierto(0 < os_["factor_sd"] < os_["factor_max"] - os_["factor_min"],
             "otras semillas: la desviación cabe en el rango", f"{os_['factor_sd']:.5f}")
    # Un departamento menos.
    lista_d = su_["por_departamento"]
    a.cierto([f["dpto"] for f in lista_d] == list(cods),
             "sin un departamento: la lista recorre los prefijos DIVIPOLA en orden",
             f"{len(lista_d)} departamentos")
    a.cierto([f["departamento"] for f in lista_d] == nom_d
             and [f["municipios"] for f in lista_d] == [int(v) for v in tam_d],
             "  cada uno con su nombre y sus municipios")
    a.igual(su_["n_departamentos_quedan"], len(cods) - 1, "  y quedan los demás")
    a.cierto(isinstance(su_["semilla_iid"], int) and isinstance(su_["semilla_bloques"], int)
             and su_["semilla_iid"] != su_["semilla_bloques"],
             "sin un departamento: los dos remuestreos llevan semillas enteras y distintas",
             f"{su_['semilla_iid']} y {su_['semilla_bloques']}")
    a.cierto(su_["nboot"] >= 5 * ir["nboot"],
             "sin un departamento: más réplicas que el módulo, para que el ruido no decida",
             str(su_["nboot"]))
    fac_pub = np.array([f["factor"] for f in lista_d])
    nef_pub = np.array([f["n_eff"] for f in lista_d])
    a.cierto(np.allclose((len(x_d) - tam_d) / fac_pub ** 2, nef_pub, atol=1e-6, rtol=0),
             "sin un departamento: cada n efectivo es (n − los suyos)/factor²")
    fac_k = []
    for k in range(len(cods)):
        queda = cod_d != cods[k]
        ee_i = x_d[queda].std(ddof=0) / math.sqrt(queda.sum())
        fac_k.append(medias_bloques(np.delete(sum_d, k), np.delete(tam_d, k), 5).std(ddof=1) / ee_i)
    fac_k = np.array(fac_k)
    peor_d = int(np.argmax(np.abs(fac_pub / fac_k - 1)))
    a.cierto(np.all(np.abs(fac_pub / fac_k - 1) < 0.05),
             "sin un departamento: el factor, rehecho uno a uno con 50 000 réplicas",
             f"el peor: {nom_d[peor_d]}, R {fac_pub[peor_d]:.4f} · aquí {fac_k[peor_d]:.4f}")
    a.cierto(np.all(np.abs(nef_pub / ((len(x_d) - tam_d) / fac_k ** 2) - 1) < 0.10),
             "  y el n efectivo")
    a.igual(fac_pub.min(), su_["factor_min"], "sin un departamento: el factor mínimo es el de la lista", 1e-12)
    a.igual(fac_pub.max(), su_["factor_max"], "  y el máximo", 1e-12)
    a.igual(nef_pub.min(), su_["n_eff_min"], "  el n efectivo mínimo", 1e-12)
    a.igual(nef_pub.max(), su_["n_eff_max"], "  y el máximo", 1e-12)
    i_ext = int(fac_pub.argmin())
    a.cierto(su_["extremo"] == lista_d[i_ext] and int(nef_pub.argmax()) == i_ext,
             "sin un departamento: el extremo es el del factor mínimo y el n efectivo máximo",
             su_["extremo"]["departamento"])
    a.cierto(int(fac_k.argmin()) == i_ext,
             "  y con el remuestreo de aquí es el mismo departamento", nom_d[int(fac_k.argmin())])
    a.cierto(np.sort(fac_pub)[1] / fac_pub[i_ext] - 1 > 0.05,
             "  separado del siguiente por más que la tolerancia",
             f"{fac_pub[i_ext]:.4f} frente a {np.sort(fac_pub)[1]:.4f}")
    # R2 de T1.6 · EL RECORRIDO NO ES LA INCERTIDUMBRE. El error estándar
    # jackknife sale de los 33 valores publicados —identidad— y se rehace
    # además con los 33 factores del remuestreo de aquí. Esos difieren de los
    # de R hasta un 5 % cada uno, y el jackknife amplía las diferencias entre
    # ellos, así que la tolerancia es ancha, un 25 %; lo que la prosa afirma
    # —que supera a medio recorrido y que deja el n efectivo en orden de
    # magnitud— se comprueba con las dos versiones.
    def ee_jk(v):
        v = np.asarray(v, float)
        return math.sqrt((len(v) - 1) / len(v) * ((v - v.mean()) ** 2).sum())

    a.igual(ee_jk(fac_pub), su_["ee_jackknife_factor"], "el e.e. jackknife del factor sale de la lista", 1e-8)
    a.igual(ee_jk(nef_pub), su_["ee_jackknife_n_eff"], "  y el del n efectivo", 1e-7)
    a.igual(100 * su_["ee_jackknife_n_eff"] / ir["n_eff"], su_["ee_jackknife_n_eff_pct"],
            "  que es ese porcentaje del titular", 1e-6)
    nef_k = (len(x_d) - tam_d) / fac_k ** 2
    a.cierto(abs(su_["ee_jackknife_factor"] / ee_jk(fac_k) - 1) < 0.25
             and abs(su_["ee_jackknife_n_eff"] / ee_jk(nef_k) - 1) < 0.25,
             "el e.e. jackknife, rehecho con el remuestreo de aquí",
             f"factor R {su_['ee_jackknife_factor']:.4f} · aquí {ee_jk(fac_k):.4f} | "
             f"n_eff R {su_['ee_jackknife_n_eff']:.3f} · aquí {ee_jk(nef_k):.3f}")
    a.cierto((su_["factor_max"] - su_["factor_min"]) / 2 < su_["ee_jackknife_factor"]
             and (fac_k.max() - fac_k.min()) / 2 < ee_jk(fac_k),
             "medio recorrido del factor queda por debajo de su e.e. jackknife, en R y aquí",
             f"{(su_['factor_max'] - su_['factor_min']) / 2:.4f} < {su_['ee_jackknife_factor']:.4f}")
    a.cierto((su_["n_eff_max"] - su_["n_eff_min"]) / 2 < su_["ee_jackknife_n_eff"],
             "  y medio recorrido del n efectivo, por debajo del suyo")
    a.cierto(su_["ee_jackknife_n_eff_pct"] > 25 and 100 * ee_jk(nef_k) / neff_ref > 25,
             "el n efectivo se conoce solo en orden de magnitud: su e.e. pasa del 25 %",
             f"{su_['ee_jackknife_n_eff_pct']:.1f} %")
    a.cierto(su_["factor_min"] < ir["factor"] < su_["factor_max"]
             and su_["n_eff_min"] < ir["n_eff"] < su_["n_eff_max"],
             "sin un departamento: el recorrido contiene al titular del módulo")
    a.cierto(su_["n_eff_min"] < os_["n_eff_min"] and os_["n_eff_max"] < su_["n_eff_max"],
             "  y es más ancho que el de las semillas")
    a.cierto(abs(su_["factor_todos"] / fac_ref - 1) < 0.05,
             "con los 33 y las mismas réplicas, el factor es el de la referencia",
             f"R {su_['factor_todos']:.5f} · aquí {fac_ref:.5f}")
    a.igual(ir["n_municipios"] / su_["factor_todos"] ** 2, su_["n_eff_todos"],
            "  y su n efectivo sale de él", 1e-6)

    # =================================================================
    a.titulo("4 · El tamaño de muestra efectivo")
    # =================================================================
    ne = D["n_efectivo"]
    for bloque in ne["rejilla"]:
        n = bloque["n"]
        for k, rho in enumerate(ne["rhos"]):
            esperado = n / (1 + (n - 1) * rho)
            a.igual(esperado, bloque["n_eff"][k], f"n_eff(n={n}, rho={rho})", 1e-7)
            a.igual(100 * esperado / n, bloque["pct"][k],
                    f"  su porcentaje", 1e-6)
    a.igual(1000 / (1 + 999 * 0.01), ne["caso_n1000_rho001"],
            "el caso n=1000, rho=0.01", 1e-7)
    a.cierto(ne["caso_n1000_rho001"] < 100,
             "con rho=0.01 y n=1000 queda menos del 10 %",
             f"{ne['caso_n1000_rho001']:.5f}")

    # --- La fórmula es exacta (R1, C1-18) ------------------------------
    #
    # Var(Zbar) = (sigma^2/n)[1 + (n-1) rho_medio] es una identidad, con
    # rho_medio la correlación media entre pares. Así que el n_eff de la
    # fórmula y el exacto del módulo 4 no «cuentan la misma historia»: son
    # el mismo número, en cada phi. El rho medio se rehace AQUÍ desde la
    # retícula, promediando rho(h) sobre el triángulo de pares, sin pasar
    # por R ni por la suma 1'R1 de la sección 3.
    N4 = inf["n"]
    _tri = np.triu_indices(N4, 1)
    a.igual(len(_tri[0]), N4 * (N4 - 1) // 2, "los pares de la retícula son n(n-1)/2")

    def rho_medio(dist_pares, phi):
        return 0.0 if phi <= 0 else float(np.exp(-dist_pares / phi).mean())

    a.igual(len(ne["exacto_campo"]), len(fila), "un n_eff exacto por cada phi del módulo 4")
    rho_de_phi = {}
    for e, r in zip(ne["exacto_campo"], fila):
        phi = e["phi"]
        a.igual(phi, r["phi"], f"campo phi={phi}: el alcance es el de su fila del módulo 4")
        a.igual(e["n_eff"], r["n_eff"], f"campo phi={phi}: el n_eff exacto es el del módulo 4")
        a.igual(100 * e["n_eff"] / N4, e["pct"],
                f"campo phi={phi}: porcentaje de información", 1e-6)
        rm = rho_medio(_DIST[_tri], phi)
        rho_de_phi[phi] = rm
        a.igual(rm, e["rho_medio"], f"campo phi={phi}: rho medio rehecho desde la retícula", 1e-9)
        a.igual(N4 / (1 + (N4 - 1) * rm), e["n_eff"],
                f"campo phi={phi}: n/(1+(n-1) rho medio) ES el n_eff exacto", 1e-9)
        a.igual(e["n_eff_formula"], e["n_eff"],
                f"campo phi={phi}: y R publica los dos iguales", 1e-9)
    a.igual(ne["desercion_municipal"], ir["n_eff"], "el n_eff real coincide con el suyo")
    a.igual(ne["desercion_pct"], ir["pct_informacion"], "y su porcentaje también")
    # El caso de la autoevaluación: el quiz no lleva ninguna cifra a mano,
    # así que todas las que imprime tienen que salir de la rejilla.
    cq = ne["caso_quiz"]
    a.igual(cq["n"], ne["enes"][-1], "quiz: su n es el último de la rejilla")
    a.cierto(cq["rho"] in ne["rhos"] and cq["rho_otro"] in ne["rhos"],
             "quiz: sus dos rho están en la rejilla", f"{cq['rho']} y {cq['rho_otro']}")
    a.igual(cq["n"] / (1 + (cq["n"] - 1) * cq["rho"]), cq["n_eff"], "quiz: su n_eff", 1e-9)
    a.igual(ne["rejilla"][-1]["n_eff"][ne["rhos"].index(cq["rho"])], cq["n_eff"],
            "quiz: que es el de la rejilla", 1e-9)
    a.igual(round(cq["n_eff"]), cq["n_eff_redondo"], "quiz: la respuesta redondeada")
    a.igual(cq["n"] - cq["n_eff_redondo"], cq["sobran"], "quiz: las observaciones que sobran")
    a.igual(round(1 / cq["rho"]), cq["techo"], "quiz: el techo de su rho")
    a.igual(round(1 / cq["rho_otro"]), cq["techo_otro"], "quiz: el techo del otro rho")
    a.igual(round(100 * cq["rho"]), cq["pct_ingenuo"], "quiz: el porcentaje del distractor")
    a.igual(round(cq["n"] * (1 - cq["rho"])), cq["ingenuo"], "quiz: el distractor ingenuo")
    a.cierto(len({cq["n_eff_redondo"], cq["ingenuo"], cq["techo_otro"], cq["n"]}) == 4,
             "quiz: las cuatro opciones son distintas")
    a.cierto("rho_medio" in ne["formula"],
             "la fórmula declarada habla del rho medio entre pares", ne["formula"][:40])

    # --- El rho medio que corresponde al titular -----------------------
    #
    # Es un despeje, así que la ida y la vuelta cierran. Las tolerancias
    # están MEDIDAS: el JSON redondea a diez decimales y ese 5e-11 se
    # amplifica al volver por la fórmula (1.8e-07 medido -> 1e-5).
    rt = ne["rho_del_titular"]
    a.igual(rt["n"], ir["n_municipios"], "el rho del titular habla de los mismos municipios")
    a.igual(rt["n_eff_publicado"], ir["n_eff"], "y del mismo n_eff")
    nr = rt["n"]
    a.igual((nr / rt["n_eff_publicado"] - 1) / (nr - 1), rt["implicito"],
            "el rho medio del titular es el despeje de n_eff", 1e-9)
    a.igual(nr / (1 + (nr - 1) * rt["implicito"]), rt["n_eff_publicado"],
            "y devuelve el n_eff del titular", 1e-5)
    # El despeje es APROXIMADO, y el capítulo cuantifica una de las razones:
    # ee_iid sale de s², que se encoge con la correlación (E[s²] =
    # sigma²(1 - rho medio), sección 3), así que el cociente de remuestreos
    # estima n(1-rho)/(1+(n-1)rho). Se rehace el despeje de esa expresión.
    neff_t = rt["n_eff_publicado"]
    a.igual((nr - neff_t) / (nr + (nr - 1) * neff_t), rt["implicito_con_s2"],
            "el rho medio del titular contando con que s² se encoge", 1e-9)
    a.igual(nr * (1 - rt["implicito_con_s2"]) / (1 + (nr - 1) * rt["implicito_con_s2"]),
            neff_t, "y devuelve el n_eff del titular por la otra expresión", 1e-5)
    # 1e-7: cociente de dos rho de ~0.0146 redondeados a diez decimales
    # (medido: 3,9e-9, 26 veces de holgura).
    a.igual(100 * (1 - rt["implicito_con_s2"] / rt["implicito"]), rt["diferencia_s2_pct"],
            "lo que la corrección por s² rebaja el rho medio, en %", 1e-7)
    a.cierto(0 < rt["diferencia_s2_pct"] < 5, "y es una rebaja pequeña",
             f"{rt['diferencia_s2_pct']:.5f} %")
    # El «rho medido» —la I de Moran por bandas promediada por pares— se
    # retiró en R1 porque no estima el rho medio (C1-19). Que no vuelva.
    CLAVES_RT = {"n", "n_eff_publicado", "implicito", "implicito_con_s2", "diferencia_s2_pct"}
    a.cierto(set(rt) == CLAVES_RT,
             "el titular no publica ningún «rho medido» sobre el mapa",
             ", ".join(sorted(set(rt) ^ CLAVES_RT)))

    # --- Por qué el rho medio no se mide sobre el mapa (C1-19) ---------
    #
    # Centrando con la media muestral, el promedio de los productos cruzados
    # de TODOS los pares, dividido por la varianza (con 1/n), vale -1/(n-1)
    # para cualquier dato. El capítulo lo publica medido sobre las réplicas
    # del módulo 4; aquí se comprueba lo publicado y se rehace la medición
    # con réplicas PROPIAS —otro generador, otra semilla—, por fuerza bruta
    # sobre la matriz de productos.
    cz = ne["centrado"]
    i4c = [i for i, r in enumerate(fila) if r["phi"] == cz["phi"]]
    a.cierto(len(i4c) == 1 and cz["phi"] == 4, "la demostración corre con phi = 4",
             str(cz["phi"]))
    a.igual(cz["n"], N4, "sobre la retícula del módulo 4")
    a.igual(cz["nrep"], inf["nrep"], "y con sus mismas réplicas")
    a.igual(cz["media"], 0, "la media verdadera del proceso simulado es 0")
    a.igual(cz["varianza"], inf["sigma"] ** 2, "y su varianza, la del módulo 4")
    a.igual(rho_de_phi[cz["phi"]], cz["rho_medio_verdadero"],
            "el rho medio verdadero, rehecho desde la retícula", 1e-9)
    a.igual(-1 / (N4 - 1), cz["menos_inv_n1"], "-1/(n-1) con n = 256", 1e-9)
    a.igual(cz["centrado_min"], cz["menos_inv_n1"],
            "el menor promedio centrado de las réplicas es -1/(n-1)", 1e-9)
    a.igual(cz["centrado_max"], cz["menos_inv_n1"],
            "y el mayor también", 1e-9)
    a.cierto(0 <= cz["desviacion_max"] <= 1e-9,
             "la desviación máxima respecto de -1/(n-1) es redondeo",
             f"{cz['desviacion_max']:.1e}")

    def pares_medios(z):
        """Media de z_i z_j sobre los n(n-1) pares i != j, por fuerza bruta."""
        return (np.outer(z, z).sum() - (z ** 2).sum()) / (len(z) * (len(z) - 1))

    def centrado(z):
        zc = z - z.mean()
        return pares_medios(zc) / (zc ** 2).mean()

    NREP_A = 3000
    _R4 = np.exp(-_DIST / cz["phi"])
    _L4 = np.linalg.cholesky(_R4 + 1e-9 * np.eye(N4))
    _Z = _L4 @ np.random.default_rng(20929).standard_normal((N4, NREP_A))
    cen_a = np.array([centrado(_Z[:, k]) for k in range(NREP_A)])
    a.cierto(np.abs(cen_a + 1 / (N4 - 1)).max() < 1e-9,
             "en réplicas propias el promedio centrado también es -1/(n-1)",
             f"desvío máx. {np.abs(cen_a + 1 / (N4 - 1)).max():.1e} en {NREP_A}")
    # Con la media VERDADERA (0) y la varianza verdadera (1) el promedio sí
    # apunta al rho medio, pero con una dispersión entre réplicas mayor que
    # el propio valor. Es una forma cuadrática z'Az de una normal, así que
    # su desviación típica tiene fórmula: sqrt(2 tr((AR)^2)).
    cmv = cz["con_media_verdadera"]
    a.cierto(abs(cmv["media"] - cz["rho_medio_verdadero"]) <= 4 * cmv["emc"],
             "con la media verdadera el promedio apunta al rho medio",
             f"{cmv['media']:.5f} ± {cmv['emc']:.5f} frente a {cz['rho_medio_verdadero']:.5f}")
    a.igual(cmv["sd"] / math.sqrt(cz["nrep"]), cmv["emc"],
            "su error de Monte Carlo es sd/sqrt(réplicas)", 1e-9)
    _A = (np.ones((N4, N4)) - np.eye(N4)) / (N4 * (N4 - 1))
    _AR = _A @ _R4
    sd_teo = math.sqrt(2 * np.trace(_AR @ _AR))
    # 12 %: la sd de una variable casi ji-cuadrado de 1 g.l., estimada con
    # 3 000 réplicas, tiene un error relativo de ~3,4 %.
    a.cierto(abs(cmv["sd"] - sd_teo) <= 0.12 * sd_teo,
             "su desviación típica entre réplicas cuadra con la teórica",
             f"{cmv['sd']:.5f} frente a {sd_teo:.5f}")
    a.cierto(cmv["sd"] > cz["rho_medio_verdadero"],
             "y supera al valor que se quiere estimar",
             f"{cmv['sd']:.5f} > {cz['rho_medio_verdadero']:.5f}")
    con_mu_a = np.array([pares_medios(_Z[:, k] - cz["media"]) / cz["varianza"]
                         for k in range(NREP_A)])
    a.cierto(abs(con_mu_a.mean() - cz["rho_medio_verdadero"])
             <= 4 * con_mu_a.std(ddof=1) / math.sqrt(NREP_A),
             "en réplicas propias también apunta al rho medio",
             f"{con_mu_a.mean():.5f}")
    # El porcentaje de réplicas con promedio negativo se contrasta contra una
    # referencia mucho más fina que las 3 000 réplicas de arriba: 200 000
    # réplicas propias, con el promedio por su forma cerrada
    # ((suma)² - suma de cuadrados) / (n(n-1)), que para esto no hay nada que
    # demostrar por fuerza bruta. La referencia tiene un error típico de 0,07
    # puntos; el de R, con 3 000 réplicas, es sqrt(0,098 · 0,902 / 3000) =
    # 0,54 puntos. Se exigen 2 puntos, 3,7 errores típicos. Con las 3 000
    # réplicas de antes como referencia y 3 puntos de margen, un 13 % pasaba.
    _ZG = _L4 @ np.random.default_rng(929).standard_normal((N4, 200_000))
    _ZG = (_ZG - cz["media"]) / math.sqrt(cz["varianza"])
    con_mu_g = (_ZG.sum(0) ** 2 - (_ZG ** 2).sum(0)) / (N4 * (N4 - 1))
    pct_neg_g = 100 * float((con_mu_g < 0).mean())
    a.cierto(abs(pct_neg_g - cmv["pct_negativas"]) <= 2,
             "el porcentaje de réplicas con promedio negativo, rehecho",
             f"{pct_neg_g:.2f} frente a {cmv['pct_negativas']:.2f}")

    # Y sobre el dato real, leído del GeoPackage y de la llave, no del CSV
    # del generador.
    gm = gpd.read_file(PROCESADO / "colombia_adm2.gpkg")
    llave = pd.read_csv(PROCESADO / "municipios_llave.csv", dtype=str)
    gm = gm.merge(llave[["shapeID", "desercion"]], on="shapeID", how="left")
    gm["desercion"] = pd.to_numeric(gm["desercion"], errors="coerce")
    y_m = gm.loc[gm["desercion"].notna(), "desercion"].to_numpy()
    cc = cz["colombia"]
    a.igual(len(y_m), cc["n"], "los municipios con dato, contados por geopandas")
    a.igual(cc["n"], rt["n"], "que son los del titular")
    a.igual(-1 / (cc["n"] - 1), cc["menos_inv_n1"], "-1/(n-1) con los municipios", 1e-9)
    a.igual(centrado(y_m), cc["centrado"],
            "el promedio centrado de la deserción, rehecho", 1e-9)
    a.igual(cc["centrado"], cc["menos_inv_n1"], "que es -1/(n-1)", 1e-9)

    # --- El techo, rellenando o ampliando (C1-21) ----------------------
    #
    # «n_eff tiende a 1/rho» solo vale con el rho medio fijo. Las dos
    # configuraciones se reconstruyen aquí: la misma región de lado 16
    # partida en k x k celdas con la observación en el CENTRO de cada una
    # (relleno) y paso 1 con k celdas por lado (ampliación).
    from scipy.spatial.distance import pdist
    tc = ne["techo"]
    Lr = tc["lado_relleno"]
    a.igual(tc["phi"], cz["phi"], "la tabla del techo usa el mismo alcance")
    a.igual(Lr, inf["k"], "la región del relleno es la de las celdas del módulo 4")
    a.igual(tc["paso_ampliacion"], 1, "y la ampliación va a paso 1, como aquella retícula")
    a.cierto([f["k"] for f in tc["rejilla"]] == list(tc["ks"]),
             "la tabla trae una fila por cada k declarado", str(tc["ks"]))
    for f in tc["rejilla"]:
        k = f["k"]
        a.igual(k * k, f["n"], f"techo k={k}: n = k²")
        g = np.array([(x, y) for y in range(k) for x in range(k)], float)
        for modo, xy_t in (("relleno", (g + 0.5) * Lr / k),
                           ("ampliacion", g * tc["paso_ampliacion"])):
            rm = rho_medio(pdist(xy_t), tc["phi"])
            a.igual(rm, f[modo]["rho_medio"], f"techo k={k}, {modo}: rho medio", 1e-9)
            # 1e-7: el n_eff llega hasta 48 y la media de 8 millones de
            # pares difiere entre R y numpy en la undécima cifra.
            a.igual(f["n"] / (1 + (f["n"] - 1) * rm), f[modo]["n_eff"],
                    f"techo k={k}, {modo}: n_eff", 1e-7)
        if k == inf["k"]:
            for modo in ("relleno", "ampliacion"):
                a.igual(f[modo]["n_eff"], inf["n_eff_phi4"],
                        f"techo k={k}, {modo}: es la retícula del módulo 4", 1e-8)
    tf = tc["rejilla"]
    a.cierto(inf["k"] in tc["ks"], "la retícula del módulo 4 está en la tabla")

    # El límite del relleno: rho_inf = E[rho(|U-V|)] con U y V uniformes en
    # el cuadrado. R lo saca de una integral doble con `integrate`; aquí va
    # por DOS caminos que no comparten nada con ese:
    #   · una cuadratura de punto medio de 4000 x 4000 sobre la misma
    #     integral (error medido 3,8e-9 -> 1e-7, 26 veces de holgura);
    #   · un Monte Carlo que no usa la integral: 4 millones de pares de
    #     puntos al azar en el cuadrado (error típico 9e-5; se exigen 4).
    _m = 4000
    _x = (np.arange(_m) + 0.5) * Lr / _m
    _X, _Y = np.meshgrid(_x, _x)
    rho_inf_q = float((4 / Lr ** 4) * (np.exp(-np.hypot(_X, _Y) / tc["phi"])
                                       * (Lr - _X) * (Lr - _Y)).sum() * (Lr / _m) ** 2)
    a.igual(rho_inf_q, tc["rho_inf"], "rho_inf del relleno, por cuadratura propia", 1e-7)
    _rng = np.random.default_rng(20929)
    _N = 4_000_000
    _d = _rng.uniform(0, Lr, (_N, 2)) - _rng.uniform(0, Lr, (_N, 2))
    _r = np.exp(-np.hypot(_d[:, 0], _d[:, 1]) / tc["phi"])
    _se = float(_r.std(ddof=1) / math.sqrt(_N))
    a.cierto(abs(_r.mean() - tc["rho_inf"]) <= 4 * _se,
             "rho_inf del relleno, por Monte Carlo de pares al azar",
             f"{_r.mean():.5f} ± {_se:.5f} frente a {tc['rho_inf']:.5f}")
    a.igual(1 / tc["rho_inf"], tc["techo_inf"], "el techo del relleno es 1/rho_inf", 1e-7)

    # Lo que el capítulo afirma del relleno es ESTANCAMIENTO. Las cotas son
    # las del generador, y están medidas: el último salto mueve el n_eff un
    # 0,059 % (se exige < 0,25 %, cuatro veces) y a la última fila le falta
    # un 0,017 % para 1/rho_inf (se exige < 0,1 %, casi seis veces).
    a.igual(100 * (tf[-1]["relleno"]["n_eff"] / tf[-2]["relleno"]["n_eff"] - 1),
            tc["ultimo_salto_pct"], "el último salto del relleno, en %", 1e-6)
    a.igual(100 * (1 - tf[-1]["relleno"]["n_eff"] / tc["techo_inf"]),
            tc["falta_techo_pct"], "lo que le falta a la última fila para su techo, en %", 1e-6)
    a.cierto(abs(tc["ultimo_salto_pct"]) < 0.25,
             "al rellenar el n_eff se estanca: el último salto es pequeño",
             f"{tc['ultimo_salto_pct']:.5f} %")
    a.cierto(0 <= tc["falta_techo_pct"] < 0.1,
             "y la última fila está en 1/rho_inf, por debajo",
             f"{tc['falta_techo_pct']:.5f} %")
    a.cierto(all(f["relleno"]["n_eff"] <= tc["techo_inf"] for f in tf),
             "con este diseño ninguna fila del relleno supera 1/rho_inf")
    a.cierto(all(abs(tf[i + 1]["relleno"]["rho_medio"] - tc["rho_inf"])
                 < abs(tf[i]["relleno"]["rho_medio"] - tc["rho_inf"])
                 for i in range(len(tf) - 1)),
             "al rellenar el rho medio se acerca a rho_inf fila a fila")

    a.igual(tf[-1]["n"] / tf[0]["n"], tc["factor_n"], "por cuánto se multiplica n")
    a.igual(tf[-1]["relleno"]["n_eff"] / tf[0]["relleno"]["n_eff"], tc["factor_relleno"],
            "por cuánto se multiplica n_eff al rellenar", 1e-8)
    a.igual(tf[-1]["ampliacion"]["n_eff"] / tf[0]["ampliacion"]["n_eff"],
            tc["factor_ampliacion"], "y al ampliar", 1e-7)
    a.cierto(all(tf[i]["ampliacion"]["rho_medio"] > tf[i + 1]["ampliacion"]["rho_medio"]
                 and tf[i]["ampliacion"]["n_eff"] < tf[i + 1]["ampliacion"]["n_eff"]
                 for i in range(len(tf) - 1)),
             "al ampliar el rho medio cae y el n_eff crece")
    # Medido: 1,019 al rellenar y 19,18 al ampliar, con n x 64 en los dos.
    a.cierto(abs(tc["factor_relleno"] - 1) < 0.05 and tc["factor_ampliacion"] > 10,
             "multiplicar n apenas mueve el n_eff al rellenar y sí al ampliar",
             f"{tc['factor_relleno']:.5f} y {tc['factor_ampliacion']:.5f}")

    # =================================================================
    a.titulo("5 · Una realización frente a muchas")
    # =================================================================
    ur = D["una_realizacion"]
    a.cierto(ur["n_realizaciones"] >= 200, "realizaciones suficientes",
             str(ur["n_realizaciones"]))
    a.igual(ur["media_del_proceso"], 0, "la media del proceso es 0 por construcción")
    a.cierto(abs(ur["media_de_las_medias"]) < 4 * ur["sd_de_las_medias"] /
             math.sqrt(ur["n_realizaciones"]),
             "la media de las medias es compatible con 0",
             f"{ur['media_de_las_medias']:.5f}")
    a.cierto(ur["media_min"] < 0 < ur["media_max"],
             "hay realizaciones a los dos lados de la media verdadera")
    emc = 100 * math.sqrt((ur["pct_rechaza_ingenuo"] / 100) *
                          (1 - ur["pct_rechaza_ingenuo"] / 100) / ur["n_realizaciones"])
    a.igual(emc, ur["emc_rechaza"], "el error de Monte Carlo del rechazo", 1e-6)
    a.igual(100 * (1 - D["inferencia"]["cobertura_phi4"]), ur["pct_rechaza_modulo4"],
            "el rechazo que mide el módulo 4", 1e-7)
    a.igual(abs(ur["pct_rechaza_ingenuo"] - ur["pct_rechaza_modulo4"]),
            ur["discrepancia_con_modulo4"], "la discrepancia declarada", 1e-7)
    emc_conj = math.sqrt(ur["emc_rechaza"] ** 2 +
                         (100 * D["inferencia"]["rejilla"][i4]["emc_cobertura"]) ** 2)
    a.cierto(ur["discrepancia_con_modulo4"] <= 3 * emc_conj,
             "los módulos 4 y 6 miden lo mismo y cuadran",
             f"{ur['discrepancia_con_modulo4'] / emc_conj:.2f} errores de Monte Carlo")
    a.cierto(ur["pct_rechaza_ingenuo"] > 50,
             "la mayoría engañaría al análisis ingenuo",
             f"{ur['pct_rechaza_ingenuo']:.5f} %")
    vg = ur["variograma"]
    a.igual(len(vg["lags"]), len(vg["teorico"]), "el variograma tiene un teórico por lag")
    for k, h in enumerate(vg["lags"]):
        a.igual(1 - math.exp(-h / ur["phi"]), vg["teorico"][k],
                f"variograma teórico en el lag {h}", 1e-9)
        a.cierto(vg["q05"][k] <= vg["media"][k] <= vg["q95"][k],
                 f"  la media del lag {h} cae dentro de su banda")
        a.cierto(vg["q05"][k] < vg["q95"][k], f"  y la banda del lag {h} no es degenerada")
    a.cierto(all(vg["teorico"][i] < vg["teorico"][i + 1]
                 for i in range(len(vg["teorico"]) - 1)),
             "el variograma teórico crece con el lag")
    # --- La referencia de cada clase, rehecha desde la GEOMETRÍA ----------
    #
    # R1 · T1.4 (C1-25). Las clases del estimador son |d − h| < 0.5, así que
    # la clase h mezcla distancias (la 1: d = 1 y d = √2). Lo que el
    # estimador estima sin sesgo es la media de γ(d) sobre los pares de la
    # clase, no γ(h). Aquí se rehace sin mirar nada de R: se enumeran los
    # desplazamientos (dx, dy) de la retícula k×k, cada uno con su número
    # EXACTO de pares —(k − |dx|)(k − |dy|), contando cada par no ordenado
    # una vez—, y se promedia γ(d) = 1 − exp(−d/φ) con esos pesos. Es otra
    # ruta que la de R (que indexa la matriz de distancias de 256×256) y es
    # exacta: tolerancia 1e-9, la del redondeo del JSON.
    k6, phi6 = ur["k"], ur["phi"]
    suma_g = {h: 0.0 for h in vg["lags"]}
    cuenta = {h: 0 for h in vg["lags"]}
    for dx in range(0, k6):
        for dy in range(-(k6 - 1), k6):
            # media-plano: cada par no ordenado una sola vez
            if dx == 0 and dy <= 0:
                continue
            d = math.hypot(dx, dy)
            pares = (k6 - dx) * (k6 - abs(dy))
            for h in vg["lags"]:
                if abs(d - h) < 0.5:
                    suma_g[h] += pares * (1 - math.exp(-d / phi6))
                    cuenta[h] += pares
    gbar = [suma_g[h] / cuenta[h] for h in vg["lags"]]
    tc_ok = (len(vg.get("teorico_clase", [])) == len(vg["lags"])
             and len(vg.get("n_pares", [])) == len(vg["lags"]))
    a.cierto(tc_ok, "el variograma trae un teórico de clase y un número de pares por rezago")
    if tc_ok:
        for k, h in enumerate(vg["lags"]):
            a.igual(cuenta[h], vg["n_pares"][k], f"pares de la clase {h}, contados en la retícula")
            a.igual(gbar[k], vg["teorico_clase"][k],
                    f"teórico promediado en la clase {h}", 1e-9)
            # La media de las réplicas cae sobre la referencia de la clase.
            # Su error de Monte Carlo no se publica, pero se acota desde la
            # banda: para una distribución de una sola moda, la sd no pasa
            # de (q95 − q05) / 2 con holgura (en la normal es / 3.29), así
            # que emc ≤ (q95 − q05) / (2 √NREAL). Se piden menos de 4 de
            # esas cotas: medido, la peor clase queda a 0.5.
            cota = (vg["q95"][k] - vg["q05"][k]) / (2 * math.sqrt(ur["n_realizaciones"]))
            a.cierto(abs(vg["media"][k] - gbar[k]) < 4 * cota,
                     f"  la media de las réplicas cae sobre él en la clase {h}",
                     f"|{vg['media'][k]:.5f} − {gbar[k]:.5f}| frente a 4 × {cota:.5f}")
        # Lo que la prosa afirma del rezago 1: la referencia de la clase y
        # γ(1) NO son la misma cifra, y la media de las réplicas distingue.
        a.cierto(abs(vg["media"][0] - vg["teorico_clase"][0])
                 < 0.1 * abs(vg["media"][0] - vg["teorico"][0]),
                 "en el rezago 1 la media cae sobre el teórico de la clase y no sobre γ(1)",
                 f"media {vg['media'][0]:.5f}, de clase {vg['teorico_clase'][0]:.5f}, "
                 f"γ(1) = {vg['teorico'][0]:.5f}")
    a.igual((vg["q95"][vg["lags"].index(4)] - vg["q05"][vg["lags"].index(4)])
            / gbar[vg["lags"].index(4)], ur["banda_rel_lag4"],
            "el ancho de la banda en el rezago 4, relativo al teórico de su clase", 1e-7)
    a.cierto(ur["banda_rel_lag4"] > 0.2,
             "una sola realización se desvía del proceso",
             f"{ur['banda_rel_lag4']:.5f}")

    # --- Los tres variogramas del simulador, RECALCULADOS DESDE EL MAPA ---
    #
    # T1.3, y es la comprobación que da sentido a toda la tarea. El botón
    # cambiaba el mapa y dejaba la curva quieta; peor todavía, esa curva no
    # era la de NINGUNO de los tres mapas, porque cifras y mapas salían de
    # dos simulaciones distintas —16×16 con una semilla, 28×28 con otra—.
    # Comparar el JSON de cifras consigo mismo no lo habría visto nunca: hay
    # que rehacer el variograma desde EL CAMPO QUE SE DIBUJA, y ese campo
    # solo existe en el `zq` de `cap1_mapas.json`.
    #
    # `zq` es el campo cuantizado en ZQ = 1000 pasos sobre su recorrido, así
    # que la reconstrucción no puede ser exacta y las tolerancias de abajo
    # son grandes a propósito. **El error dominante no es el que uno espera**:
    # el sesgo del redondeo vale paso²/12 ≈ 2e-6 con un paso de 0.0047, pero
    # lo que se mide son residuos de hasta 2.8e-4, cien veces más. La razón
    # es que sobre 256 celdas —y sobre pares que comparten celda— el término
    # cruzado entre el campo y su error de redondeo no se promedia a cero:
    # su fluctuación muestral es de orden 1e-4 y es la que manda. Medirlo en
    # vez de deducirlo cambió la tolerancia de 1e-3 a 5e-3.
    #
    # Con 5e-3 quedan 18 veces de margen sobre ese ruido y 21 veces por
    # debajo de lo que separa dos de estas curvas (0.10286, que el
    # ensamblador imprime en cada pasada). Entre las dos escalas hay sitio de
    # sobra, y por eso esta comprobación distingue de verdad una curva de
    # otra en vez de aceptarlas todas.
    #
    # El orden de `zq` es por filas —`geo_rejilla` escribe `t(z)`— y el de
    # `CAMPOS` por columnas de `expand.grid`. Da igual: las dos son
    # biyecciones a la misma retícula y la distancia euclídea es simétrica al
    # trasponer, así que los pares de cada rezago son exactamente los mismos.
    rv, mr = D["realizaciones_vistas"], M["realizaciones"]
    a.igual(len(mr), len(rv), "un mapa por cada realización que se enseña")
    i_lag4 = vg["lags"].index(4)
    curvas = []
    for fila, mapa in zip(rv, mr):
        q = f"realización {fila['id']}"
        a.igual(mapa["id"], fila["id"], f"{q}: el mapa y su fila llevan el mismo id")
        a.igual(mapa["nx"], ur["k"], f"{q}: el mapa va en la rejilla del módulo")
        a.igual(mapa["ny"], ur["k"], f"{q}: y es cuadrada")
        # Antes de reconstruir nada: que la rejilla declarada case con las
        # celdas que hay. Sin esto, un `nx` incoherente no daba un informe
        # sino un IndexError a media auditoría —el arnés lo daba por cazado
        # porque el código de salida es distinto de cero igual, pero un
        # auditor que se estrella deja de informar de las 900 comprobaciones
        # restantes, y eso no es cazarlo: es taparlo—. Lo encontró la
        # inyección de T1.3.f, no la lectura del código.
        if mapa["nx"] * mapa["ny"] != len(mapa["zq"]):
            a.cierto(False, f"{q}: las celdas del mapa son las que declara su rejilla",
                     f"{mapa['nx']}×{mapa['ny']} declaradas y {len(mapa['zq'])} celdas: "
                     f"no se puede rehacer su variograma")
            continue
        lo, hi = mapa["rango"]
        z = np.asarray(mapa["zq"], float) / mapa["zqmax"] * (hi - lo) + lo
        a.igual(float(z.mean()), fila["media"],
                f"{q}: su media, rehecha desde el campo", 2e-3)
        a.igual(float(z.std(ddof=1)), fila["sd"], f"{q}: y su sd espacial", 2e-3)
        fil, col = np.divmod(np.arange(mapa["nx"] * mapa["ny"]), mapa["nx"])
        dist = np.hypot(fil[:, None] - fil[None, :], col[:, None] - col[None, :])
        semi = 0.5 * (z[:, None] - z[None, :]) ** 2
        sup = np.triu(np.ones(dist.shape, bool), 1)
        propio = [float(semi[sup & (np.abs(dist - h) < 0.5)].mean()) for h in vg["lags"]]
        # Igual que arriba: si la curva no trae un valor por rezago se dice y
        # se pasa a la siguiente, en vez de estrellarse contra un IndexError y
        # dejar el informe a medias.
        if len(fila.get("variograma", [])) != len(vg["lags"]):
            a.cierto(False, f"{q}: su variograma trae un valor por rezago",
                     f"{len(fila.get('variograma', []))} de {len(vg['lags'])}")
            continue
        curvas.append(fila["variograma"])
        for k, h in enumerate(vg["lags"]):
            a.igual(propio[k], fila["variograma"][k],
                    f"{q}: su variograma en el rezago {h}", 5e-3)
        # Y las cifras que la prosa y la lectura estrenan sobre esa curva.
        # Contra el teórico DE LA CLASE, rehecho arriba desde la retícula
        # (`gbar`), no contra el que publica R ni contra γ en h entero.
        rel = [abs(fila["variograma"][k] - gbar[k]) / gbar[k]
               for k in range(len(vg["lags"]))]
        a.igual(max(rel), fila["desvio_rel_max"], f"{q}: su desvío relativo máximo", 1e-7)
        a.igual(vg["lags"][rel.index(max(rel))], fila["lag_desvio_max"],
                f"{q}: y el rezago en que se da")
        a.igual(rel[i_lag4], fila["desvio_rel_lag4"], f"{q}: su desvío en el rezago 4", 1e-7)
        a.igual(sum(1 for k in range(len(vg["lags"]))
                    if not vg["q05"][k] <= fila["variograma"][k] <= vg["q95"][k]),
                fila["lags_fuera_banda"], f"{q}: los rezagos que se le salen de la banda")
    # Que las tres se distingan A LA VISTA. Sin esto, tres curvas iguales
    # pasarían todo lo anterior y el botón volvería a mover solo el mapa.
    sep = min((max(abs(x - y) for x, y in zip(curvas[i], curvas[j]))
               for i in range(len(curvas)) for j in range(i + 1, len(curvas))), default=0.0)
    a.cierto(len(curvas) > 1 and sep > 0.01,
             "las curvas del simulador se separan a la vista",
             f"{sep:.5f} en el rezago que más las separa, sobre {len(curvas)} curvas")

    # =================================================================
    a.titulo("6 · Tobler: los correlogramas")
    # =================================================================
    for nombre, n_obs in (("meuse", D["geo_canonico"]["n"]),
                          ("ideam", D["colombia"]["geo"]["n"]),
                          ("permutado", D["colombia"]["geo"]["n"]),
                          ("residuos_altitud", D["colombia"]["geo"]["n"])):
        c = D["tobler"][nombre]
        a.igual(-1 / (n_obs - 1), c["esperado"], f"{nombre}: E[I] bajo H0", 1e-9)
        for b in c["bandas"]:
            a.cierto(b["d1"] < b["d2"], f"{nombre}: la banda {b['d1']}-{b['d2']} está ordenada")
            a.igual((b["d1"] + b["d2"]) / 2, b["centro"],
                    f"  centro de la banda {b['d1']}-{b['d2']}", 1e-7)
            a.cierto(b["n_pares"] > 0, f"  y tiene pares", str(b["n_pares"]))
    # R1 · T1.6 (C1-12) · cuántas unidades tienen vecinos en cada banda y la
    # E[I] que les corresponde, rehechas con la matriz de distancias. Las
    # tres series del IDEAM comparten estaciones, así que comparten cuenta.
    def con_vecinos(xy, d1, d2):
        dd = np.sqrt(((xy[:, None, :] - xy[None, :, :]) ** 2).sum(-1))
        A = (dd >= d1) & (dd <= d2)
        np.fill_diagonal(A, False)
        return int(A.any(axis=1).sum())

    xy_est = np.c_[est.geometry.x, est.geometry.y] / 1000
    xy_me = me[["x", "y"]].to_numpy(float)
    for nombre, xy_b in (("meuse", xy_me), ("ideam", xy_est), ("permutado", xy_est),
                         ("residuos_altitud", xy_est)):
        for b in D["tobler"][nombre]["bandas"]:
            a.igual(con_vecinos(xy_b, b["d1"], b["d2"]), b["n_con_vecinos"],
                    f"{nombre}: unidades con vecinos en la banda {b['d1']}-{b['d2']}")
            a.igual(-b["n_con_vecinos"] / (len(xy_b) * (len(xy_b) - 1)), b["esperado"],
                    f"  su esperanza por permutación es −n′/(n(n − 1))", 1e-9)
            a.igual(-1 / (b["n_con_vecinos"] - 1), b["esperado_programa"],
                    f"  y la que imprime el programa, −1/(n′ − 1)", 1e-9)
    b_id = D["tobler"]["ideam"]["bandas"]
    a.cierto(b_id[0]["n_con_vecinos"] < D["colombia"]["geo"]["n"] == b_id[-1]["n_con_vecinos"],
             "ideam: en la banda corta faltan estaciones y en la última están todas",
             f"{b_id[0]['n_con_vecinos']} y {b_id[-1]['n_con_vecinos']}")
    # R2 de T1.6 · LA ESPERANZA SE COMPRUEBA PERMUTANDO, no con la fórmula que
    # se quiere comprobar. Se arma la I con el convenio de spdep —n′ en el
    # factor, las 361 en el centrado y en la suma de cuadrados— y se permutan
    # las temperaturas 20 000 veces con el generador de aquí. La media tiene
    # que caer a menos de cuatro errores de Monte Carlo de −n′/(n(n − 1)) y a
    # más de cuatro de −1/(n′ − 1). Lo mismo se le pide a la media que R
    # publica, y su error tiene que ser el de sus permutaciones.
    b0_ = b_id[0]
    dd0 = np.sqrt(((xy_est[:, None, :] - xy_est[None, :, :]) ** 2).sum(-1))
    A0 = ((dd0 >= b0_["d1"]) & (dd0 <= b0_["d2"])).astype(float)
    np.fill_diagonal(A0, 0.0)
    g0 = A0.sum(1)
    W0 = np.zeros_like(A0)
    W0[g0 > 0] = A0[g0 > 0] / g0[g0 > 0, None]
    z0 = est.t_media_anual.to_numpy() - est.t_media_anual.mean()
    f0 = (g0 > 0).sum() / W0.sum() / (z0 @ z0)
    a.igual(f0 * (z0 @ W0 @ z0), b0_["I"], "ideam: la I de la primera banda, con el convenio de spdep", 1e-7)
    rng_p = np.random.default_rng(20929)
    perm0 = []
    for _ in range(20):
        P = rng_p.permuted(np.tile(z0, (1000, 1)), axis=1)
        perm0.append(f0 * ((P @ W0) * P).sum(axis=1))
    perm0 = np.concatenate(perm0)
    emc0 = perm0.std(ddof=1) / math.sqrt(len(perm0))
    a.cierto(abs(perm0.mean() - b0_["esperado"]) < 4 * emc0 < abs(perm0.mean() - b0_["esperado_programa"]),
             "ideam: 20 000 permutaciones de aquí dan −n′/(n(n − 1)) y no −1/(n′ − 1)",
             f"{perm0.mean():.6f} ± {emc0:.6f} · {b0_['esperado']:.6f} frente a {b0_['esperado_programa']:.6f}")
    pb = D["tobler"]["permutacion_banda1"]
    a.cierto(pb["nperm"] >= 10_000, "ideam: R permuta al menos 10 000 veces", str(pb["nperm"]))
    a.cierto(abs(pb["media"] - b0_["esperado"]) < 4 * pb["emc"] < abs(pb["media"] - b0_["esperado_programa"]),
             "ideam: las permutaciones de R dicen lo mismo",
             f"{pb['media']:.6f} ± {pb['emc']:.6f}")
    a.cierto(abs(pb["emc"] * math.sqrt(pb["nperm"]) / perm0.std(ddof=1) - 1) < 0.10,
             "  y su error de Monte Carlo es el de ese número de permutaciones", f"{pb['emc']:.6f}")
    a.cierto(abs(pb["media"] - perm0.mean()) < 5 * math.hypot(pb["emc"], emc0),
             "  y su media es compatible con la de aquí")
    # R2 · T2.4 (G-16, C1-13) · LA ENVOLVENTE DE PERMUTACIÓN, rehecha aquí.
    # Para cada banda se arma la I con el convenio de spdep y se permutan los
    # valores 1 000 veces con el generador de numpy; de ahí salen unos
    # cuantiles propios contra los que se leen los de R.
    # LA TOLERANCIA. Un cuantil del 2,5 % estimado con B valores tiene error
    # típico sd·sqrt(0.025·0.975/B)/f, y con la densidad normal en 1.96 eso
    # es 0.027 sd con las 9 999 de R y 0.085 sd con las 1 000 de aquí. A la
    # diferencia se le dejan 5 errores combinados (0.44 sd). Es ancha para
    # un cuantil y estrecha para lo que importa: la I de cada banda queda,
    # salvo en una, a más de una desviación típica del borde.
    ev = D["tobler"]["envolvente"]
    a.cierto(ev["nperm"] >= 999, "envolvente: al menos 999 permutaciones", str(ev["nperm"]))
    a.igual(100 * ev["nivel"], ev["nivel_pct"], "envolvente: el nivel, en porcentaje", 1e-9)
    a.igual(100 * (1 - ev["nivel"]) / 2, ev["cuantil_lo_pct"], "envolvente: cuantil inferior", 1e-9)
    a.igual(100 * (1 + ev["nivel"]) / 2, ev["cuantil_hi_pct"], "envolvente: cuantil superior", 1e-9)
    a.igual((ev["nperm"] + 1) * (1 - ev["nivel"]) / 2, ev["orden_lo"],
            "envolvente: el estadístico de orden inferior", 1e-9)
    a.igual((ev["nperm"] + 1) * (1 + ev["nivel"]) / 2, ev["orden_hi"],
            "envolvente: el estadístico de orden superior", 1e-9)
    N_PY_ENV = 1000
    C_Q = math.sqrt(0.025 * 0.975) / float(_st4.norm.pdf(_st4.norm.ppf(0.975)))
    tol_q = 5 * C_Q * math.hypot(1 / math.sqrt(ev["nperm"]), 1 / math.sqrt(N_PY_ENV))
    res_alt = est.t_media_anual.to_numpy() - np.polyval(
        np.polyfit(est.altitud_m.to_numpy(float), est.t_media_anual.to_numpy(), 1),
        est.altitud_m.to_numpy(float))
    rng_e = np.random.default_rng(20929)

    def lee_banda(I, lo, hi):
        return "encima" if I > hi else "debajo" if I < lo else "dentro"

    pos_py = {}
    for serie, valores in (("ideam", est.t_media_anual.to_numpy()), ("residuos_altitud", res_alt)):
        zc = valores - valores.mean()
        P = rng_e.permuted(np.tile(zc, (N_PY_ENV, 1)), axis=1)
        pos_py[serie] = []
        perms_py = []
        a.igual(len(ev[serie]), len(D["tobler"][serie]["bandas"]), f"{serie}: una envolvente por banda")
        for b, e in zip(D["tobler"][serie]["bandas"], ev[serie]):
            rot = f"{serie[:8]} {b['d1']}-{b['d2']}"
            A = ((dd0 >= b["d1"]) & (dd0 <= b["d2"])).astype(float)
            np.fill_diagonal(A, 0.0)
            gr = A.sum(1)
            Wb = np.zeros_like(A)
            Wb[gr > 0] = A[gr > 0] / gr[gr > 0, None]
            fb = (gr > 0).sum() / Wb.sum() / (zc @ zc)
            a.igual(fb * (zc @ Wb @ zc), b["I"], f"{rot}: la I, con el convenio de spdep", 1e-7)
            Ip = fb * ((P @ Wb) * P).sum(axis=1)
            sd_py = float(Ip.std(ddof=1))
            lo_py, hi_py = np.quantile(Ip, [0.025, 0.975])
            a.cierto((e["d1"], e["d2"]) == (b["d1"], b["d2"]), f"{rot}: la envolvente es de esa banda")
            a.cierto(abs(e["lo"] - lo_py) <= tol_q * sd_py and abs(e["hi"] - hi_py) <= tol_q * sd_py,
                     f"{rot}: bordes, contra permutaciones de aquí",
                     f"[{e['lo']:.5f}, {e['hi']:.5f}] frente a [{lo_py:.5f}, {hi_py:.5f}]")
            a.cierto(abs(e["sd"] / sd_py - 1) <= 4 / math.sqrt(2 * N_PY_ENV) + 4 / math.sqrt(2 * ev["nperm"]),
                     f"{rot}: su desviación típica", f"{e['sd']:.5f} frente a {sd_py:.5f}")
            a.igual(e["sd"] / math.sqrt(ev["nperm"]), e["emc"], f"{rot}: su error de Monte Carlo", 1e-8)
            a.cierto(abs(e["media"] - b["esperado"]) <= 4 * e["emc"],
                     f"{rot}: centrada en la E[I] de la banda",
                     f"{e['media']:.6f} ± {e['emc']:.6f} frente a {b['esperado']:.6f}")
            a.cierto(e["min"] <= e["lo"] < b["esperado"] < e["hi"] <= e["max"],
                     f"{rot}: mínimo, bordes y máximo, en orden")
            # El mínimo y el máximo de 9 999 permutaciones no se pueden
            # reproducir con otras 1 000. Sí acotar: el extremo de unos diez
            # mil valores de una distribución de una sola moda queda entre 2
            # y 8 desviaciones típicas de su media (medido aquí: de 3.4 a 6.8).
            a.cierto(2 <= (e["media"] - e["min"]) / e["sd"] <= 8 and 2 <= (e["max"] - e["media"]) / e["sd"] <= 8,
                     f"{rot}: sus extremos, a distancia creíble",
                     f"{(e['media'] - e['min']) / e['sd']:.1f} y {(e['max'] - e['media']) / e['sd']:.1f} sd")
            a.cierto(lee_banda(b["I"], e["lo"], e["hi"]) == e["posicion"],
                     f"{rot}: la posición publicada es la de su I", e["posicion"])
            a.cierto(lee_banda(b["I"], lo_py, hi_py) == e["posicion"],
                     f"{rot}: y la misma contra los bordes de aquí", e["posicion"])
            pos_py[serie].append((b["I"], float(Ip.min())))
            perms_py.append(Ip)
        if serie == "ideam":
            # Segunda ronda · en cuántas permutaciones se sale al menos una
            # banda, contra las franjas que publica R y con las permutaciones
            # de aquí. Tolerancia: 4 errores de las dos proporciones.
            Pm = np.array(perms_py).T
            lo_r = np.array([e["lo"] for e in ev["ideam"]]); hi_r = np.array([e["hi"] for e in ev["ideam"]])
            alguna_py = float((((Pm < lo_r) | (Pm > hi_r)).sum(axis=1) > 0).mean())
            a.igual(math.sqrt(ev["pct_alguna_fuera"] / 100 * (1 - ev["pct_alguna_fuera"] / 100) / ev["nperm"]) * 100,
                    ev["emc_alguna_fuera_pct"], "error de Monte Carlo de «alguna banda fuera»", 1e-8)
            a.cierto(abs(100 * alguna_py - ev["pct_alguna_fuera"])
                     <= 4 * math.hypot(ev["emc_alguna_fuera_pct"],
                                       100 * math.sqrt(alguna_py * (1 - alguna_py) / N_PY_ENV)),
                     "permutaciones con alguna banda fuera de su franja",
                     f"R {ev['pct_alguna_fuera']:.2f} % · aquí {100 * alguna_py:.2f} %")
            a.cierto(ev["pct_alguna_fuera"] - 4 * ev["emc_alguna_fuera_pct"] > 10,
                     "  y no es raro: más de una de cada diez")
            # Las parejas que el eje deja fuera, como una banda más.
            mx = D["tobler"]["mas_alla"]
            a.igual(float(dd0.max()), mx["d_max"], "más allá del eje: la distancia máxima, en km", 1e-5)
            a.igual(mx["d1"], b_id[-1]["d2"], "más allá del eje: empieza donde acaba el gráfico")
            Ax = (dd0 > mx["d1"]).astype(float)
            a.igual(int(Ax.sum() / 2), mx["n_pares"], "más allá del eje: parejas")
            a.igual(len(zc) * (len(zc) - 1) // 2, mx["n_pares_total"], "parejas de la red entera")
            a.igual(100 * mx["n_pares"] / mx["n_pares_total"], mx["pct_pares"],
                    "más allá del eje: porcentaje de las parejas", 1e-7)
            gx = Ax.sum(1)
            a.igual(int((gx > 0).sum()), mx["n_con_vecinos"], "más allá del eje: estaciones con pareja")
            Wx = np.zeros_like(Ax)
            Wx[gx > 0] = Ax[gx > 0] / gx[gx > 0, None]
            fx = (gx > 0).sum() / Wx.sum() / (zc @ zc)
            a.igual(fx * (zc @ Wx @ zc), mx["I"], "más allá del eje: la I, convenio de spdep", 1e-7)
            Ix = fx * ((P @ Wx) * P).sum(axis=1)
            lox, hix = np.quantile(Ix, [0.025, 0.975])
            sdx = float(Ix.std(ddof=1))
            a.cierto(abs(mx["lo"] - lox) <= tol_q * sdx and abs(mx["hi"] - hix) <= tol_q * sdx,
                     "más allá del eje: su franja, contra la de aquí",
                     f"[{mx['lo']:.5f}, {mx['hi']:.5f}] frente a [{lox:.5f}, {hix:.5f}]")
            a.cierto(abs(mx["sd"] / sdx - 1) <= 4 / math.sqrt(2 * N_PY_ENV) + 4 / math.sqrt(2 * ev["nperm"]),
                     "más allá del eje: desviación típica", f"{mx['sd']:.5f} frente a {sdx:.5f}")
            a.cierto(abs(mx["media"] + mx["n_con_vecinos"] / (len(zc) * (len(zc) - 1)))
                     <= 4 * mx["sd"] / math.sqrt(ev["nperm"]),
                     "más allá del eje: la franja se centra en su E[I]", f"{mx['media']:.6f}")
            a.cierto(lee_banda(mx["I"], mx["lo"], mx["hi"]) == mx["posicion"] == "debajo"
                     and lee_banda(mx["I"], lox, hix) == "debajo",
                     "más allá del eje: queda por debajo de su franja", mx["posicion"])
            # La suma de z_i z_j por banda, en unidades de sum(z^2)/2.
            sm = D["tobler"]["sumas"]
            zz = np.outer(zc, zc)
            sup = np.triu(np.ones_like(dd0, dtype=bool), 1)
            mitad = (zc @ zc) / 2
            sumas_py = []
            a.igual(len(sm["bandas"]), len(b_id), "sumas: una por banda del correlograma")
            for b, sb in zip(b_id, sm["bandas"]):
                cual = sup & (dd0 > b["d1"]) & (dd0 <= b["d2"])
                a.cierto((sb["d1"], sb["d2"]) == (b["d1"], b["d2"]),
                         f"sumas {b['d1']}-{b['d2']}: es esa banda")
                a.igual(int(cual.sum()), sb["n_pares"], f"sumas {b['d1']}-{b['d2']}: parejas")
                a.igual(sb["n_pares"], b["n_pares"], f"sumas {b['d1']}-{b['d2']}: las del correlograma")
                a.igual(float(zz[cual].sum() / mitad), sb["suma"], f"sumas {b['d1']}-{b['d2']}: z_i z_j", 1e-7)
                sumas_py.append(float(zz[cual].sum() / mitad))
            fuera_py = float(zz[sup & (dd0 > mx["d1"])].sum() / mitad)
            a.igual(fuera_py, sm["mas_alla"], "sumas: las parejas de más allá del eje", 1e-7)
            a.igual(sum(sumas_py) + fuera_py, -1.0, "sumas: todas las parejas dan −1", 1e-8)
            a.igual(sm["total"], -1.0, "sumas: y el total publicado también", 1e-8)
            nc_ = sm["n_bandas_cortas"]
            a.igual(sum(x == "encima" for x in [e["posicion"] for e in ev["ideam"]]), nc_,
                    "sumas: las bandas cortas son las de por encima")
            a.igual(sum(sumas_py[:nc_]), sm["cortas"], "sumas: las bandas cortas", 1e-7)
            a.igual(sum(sumas_py[nc_:]) + fuera_py, sm["largas"], "sumas: todo lo demás", 1e-7)
            a.cierto(all(x > 0 for x in sumas_py[:nc_]) and all(x < 0 for x in sumas_py[nc_:]) and fuera_py < 0
                     and sumas_py[nc_] < 0.5 * sm["largas"] and sm["cortas"] > 5,
                     "sumas: cortas positivas, largas negativas, y dónde",
                     " ".join(f"{x:.2f}" for x in sumas_py + [fuera_py]))
    pos_t = [e["posicion"] for e in ev["ideam"]]
    pos_r = [e["posicion"] for e in ev["residuos_altitud"]]
    a.igual(sum(x != "dentro" for x in pos_t), ev["n_fuera_ideam"], "bandas de la temperatura fuera")
    a.igual(sum(x != "dentro" for x in pos_r), ev["n_fuera_residuos"], "bandas de los residuos fuera")
    # Lo que el módulo 3 lee en la envolvente.
    a.cierto(pos_t == ["encima"] * (len(pos_t) - 2) + ["debajo", "dentro"],
             "temperatura: encima, una banda debajo y la última dentro", " ".join(pos_t))
    i_neg = pos_t.index("debajo") if "debajo" in pos_t else 0
    a.cierto(b_id[i_neg]["I"] < ev["ideam"][i_neg]["min"] and pos_py["ideam"][i_neg][0] < pos_py["ideam"][i_neg][1],
             "la banda negativa, bajo todas las permutaciones",
             f"{b_id[i_neg]['I']:.5f} frente a un mínimo de {ev['ideam'][i_neg]['min']:.5f}")
    a.cierto(pos_r[-3:] == ["dentro", "debajo", "debajo"] and set(pos_r[:-3]) == {"encima"},
             "residuos: encima, una dentro y las dos últimas debajo", " ".join(pos_r))
    a.cierto([lee_banda(b["I"], e["lo"], e["hi"])
              for b, e in zip(D["tobler"]["residuos_altitud"]["bandas"], ev["ideam"])] == pos_r,
             "los residuos se leen igual contra la otra envolvente")
    pos_p = [lee_banda(b["I"], e["lo"], e["hi"])
             for b, e in zip(D["tobler"]["permutado"]["bandas"], ev["ideam"])]
    a.cierto(pos_p == ev["posicion_permutado"], "la permutación suelta, contra la envolvente",
             " ".join(pos_p))
    a.igual(sum(x != "dentro" for x in pos_p), ev["n_fuera_permutado"],
            "bandas de la permutación suelta fuera")
    a.cierto(ev["n_fuera_permutado"] == 0, "  y no se sale en ninguna")

    # El decaimiento es el contenido del módulo, así que se comprueba.
    for nombre in ("meuse", "ideam"):
        bs = [b["I"] for b in D["tobler"][nombre]["bandas"] if b["I"] is not None]
        a.cierto(bs[0] > bs[-1], f"{nombre}: la I cae de la primera banda a la última",
                 f"{bs[0]:.5f} -> {bs[-1]:.5f}")
        a.cierto(bs[0] > 0.3, f"{nombre}: la primera banda tiene autocorrelación clara",
                 f"{bs[0]:.5f}")
    # El nulo: permutar destruye la estructura y deja la I en torno a E[I].
    perm = [b["I"] for b in D["tobler"]["permutado"]["bandas"] if b["I"] is not None]
    a.cierto(max(abs(x) for x in perm) < 0.10,
             "permutado: el correlograma queda plano en torno a 0",
             f"máximo |I| = {max(abs(x) for x in perm):.5f}")
    a.cierto(max(abs(x) for x in perm) < D["tobler"]["ideam"]["bandas"][0]["I"],
             "y muy por debajo de la primera banda del dato real")
    # La covariable: quitar la altitud se lleva parte de la estructura.
    res0 = D["tobler"]["residuos_altitud"]["bandas"][0]["I"]
    id0 = D["tobler"]["ideam"]["bandas"][0]["I"]
    a.igual(100 * (1 - res0 / id0), D["tobler"]["caida_por_altitud_pct"],
            "la caída de I al quitar la altitud", 1e-6)
    a.cierto(0 < res0 < id0,
             "quitar la altitud reduce la autocorrelación sin anularla",
             f"{id0:.5f} -> {res0:.5f}")

    # =================================================================
    a.titulo("7 · La agregación simulada")
    # =================================================================
    ag = D["agregacion"]
    a.igual(ag["s"] ** 2, ag["corr_teorica_base"], "la correlación teórica de partida", 1e-9)
    corrs = []
    for niv in ag["niveles"]:
        b = niv["bloque"]
        a.igual((ag["k"] // b) ** 2, niv["n_unidades"],
                f"bloque {b}: unidades tras agregar")
        a.igual(b * b, niv["celdas_por_unidad"], f"bloque {b}: celdas por unidad")
        a.cierto(-1 <= niv["corr"] <= 1, f"bloque {b}: la correlación es una correlación")
        corrs.append(niv["corr"])
    a.cierto(all(corrs[i] < corrs[i + 1] for i in range(len(corrs) - 1)),
             "la correlación crece de forma monótona al agregar",
             " < ".join(f"{c:.4f}" for c in corrs))
    a.cierto(abs(corrs[0] - ag["corr_teorica_base"]) < 0.05,
             "y el nivel base reproduce la correlación teórica",
             f"{corrs[0]:.5f} frente a {ag['corr_teorica_base']:.5f}")
    a.igual(corrs[0], ag["corr_base"], "corr_base es la del primer nivel")
    a.igual(corrs[-1], ag["corr_max"], "corr_max es la del último")
    a.igual(100 * (corrs[-1] / corrs[0] - 1), ag["subida_pct"], "la subida publicada", 1e-6)

    # =================================================================
    a.titulo("8 · La validación cruzada")
    # =================================================================
    cv = D["cv_espacial"]
    a.igual(cv["n"], D["colombia"]["geo"]["n"], "las mismas estaciones")
    a.igual(est.t_media_anual.std(ddof=1), cv["sd_variable"], "sd de la variable", 1e-8)
    a.igual(cv["rmse_bloques"] / cv["rmse_aleatoria"], cv["razon"],
            "la razón entre los dos RMSE", 1e-7)
    a.igual(100 * (cv["razon"] - 1), cv["inflacion_pct"], "la inflación publicada", 1e-6)
    a.cierto(cv["rmse_bloques"] > cv["rmse_aleatoria"],
             "la CV espacial es más exigente que la aleatoria",
             f"{cv['rmse_bloques']:.5f} > {cv['rmse_aleatoria']:.5f}")
    var = est.t_media_anual.var(ddof=1)
    a.igual(1 - cv["rmse_aleatoria"] ** 2 / var, cv["r2_aleatoria"],
            "R² con CV aleatoria", 1e-7)
    a.igual(1 - cv["rmse_bloques"] ** 2 / var, cv["r2_bloques"],
            "R² con CV por bloques", 1e-7)
    a.igual(sum(cv["tam_pliegues"]), cv["n"], "los pliegues suman n")
    a.igual(len(cv["tam_pliegues"]), cv["n_pliegues"], "y son los pliegues declarados")
    a.igual(min(cv["tam_pliegues"]), cv["tam_pliegue_min"], "el pliegue menor")
    a.igual(max(cv["tam_pliegues"]), cv["tam_pliegue_max"], "el pliegue mayor")
    a.cierto("capítulo 10" in cv["frontera"],
             "la frontera con el capítulo 10 va en el dato",
             cv["frontera"][:40])

    # =================================================================
    a.titulo("8b · ¿Diseño o modelo? La red del IDEAM, pesada por Thiessen")
    # =================================================================
    # Pebesma y Bivand §10.4. El emparejamiento celda -> estación va por
    # CONTENCIÓN, igual que en R: `voronoi_diagram` no devuelve las celdas
    # en el orden de los puntos de entrada, y fiarse del orden pegaría
    # cada temperatura al área de otra estación. La cifra saldría
    # plausible, que es lo peligroso.
    dm = D["diseno_modelo"]
    pais = dep.geometry.union_all()
    celdas_v = gpd.GeoDataFrame(
        geometry=list(voronoi_diagram(MultiPoint(list(est.geometry)),
                                      envelope=pais.envelope).geoms),
        crs=est.crs)
    emp = gpd.sjoin(est[["geometry"]], celdas_v.assign(_c=range(len(celdas_v))),
                    predicate="within")
    emp = emp[~emp.index.duplicated(keep="first")].sort_index()
    a.igual(len(emp), dm["n"], "cada estación cae en una celda de Thiessen")
    av = (celdas_v.geometry.iloc[emp["_c"].to_numpy()]
          .intersection(pais).area.to_numpy() / 1e6)
    tv = est.t_media_anual.to_numpy()
    hv = est.altitud_m.to_numpy()
    a.igual(av.sum(), dm["area_total_km2"], "área del país reconstruida", 1e-4)
    a.igual(av.min(), dm["area_min_km2"], "la celda menor (km²)", 1e-6)
    a.igual(av.max(), dm["area_max_km2"], "la celda mayor (km²)", 1e-4)
    a.igual(av.max() / av.min(), dm["razon_areas"], "  y su razón", 1e-4)
    a.igual(tv.mean(), dm["t_media_simple"], "temperatura media sin ponderar", 1e-8)
    a.igual((tv * av).sum() / av.sum(), dm["t_media_area"],
            "  y ponderada por el territorio de cada estación", 1e-8)
    a.igual((tv * av).sum() / av.sum() - tv.mean(), dm["brecha_c"],
            "  la brecha, en grados", 1e-8)
    a.igual(hv.mean(), dm["alt_media_simple"], "altitud media de las estaciones", 1e-7)
    a.igual((hv * av).sum() / av.sum(), dm["alt_media_area"],
            "  y la del territorio que representan", 1e-7)
    # Las tres afirmaciones que hace la prosa, comprobadas como tales.
    a.cierto(dm["razon_areas"] > 1000,
             "la red NO es una muestra de igual probabilidad",
             f"×{dm['razon_areas']:.5f} entre la mayor y la menor celda")
    a.cierto(dm["alt_media_simple"] > dm["alt_media_area"],
             "el desequilibrio sobremuestrea la cordillera",
             f"{dm['alt_media_simple']:.5f} m frente a {dm['alt_media_area']:.5f} m")
    a.cierto(dm["brecha_c"] > 1,
             "  así que la media muestral no estima la del país",
             f"{dm['brecha_c']:.5f} °C de brecha")

    # --- La referencia: Thiessen de puntos uniformes (R1 · T1.4, C1-32) ---
    #
    # R publica cuantiles de SU simulación; aquí se contrastan con OTRA
    # simulación independiente, así que la comparación es entre dos Monte
    # Carlo y la tolerancia se razona sin suponer forma (la cola es pesada):
    #
    #   · Si q es el cuantil p de la muestra de R (N_R valores) y F̂ la
    #     fracción de la muestra de aquí (N_A valores) que queda por debajo
    #     de q, entonces F̂ − p tiene desviación típica
    #     sqrt(p(1−p)(1/N_R + 1/N_A)), sea cual sea la distribución. Se
    #     aceptan 4 de esas desviaciones: con mil y mil, ±0.089 en la
    #     mediana y ±0.039 en los percentiles 5 y 95. Un cuantil publicado
    #     que no fuera el suyo (la mediana en el lugar del p95, un p95 de
    #     otra distribución) cae muy lejos de eso.
    #   · El IC de la mediana que R publica no se puede rehacer sin su
    #     muestra; se le exige contener a su mediana, solaparse con el IC
    #     que sale de la muestra de aquí y tener una anchura comparable
    #     (entre la mitad y el doble).
    #   · El máximo de R es un valor extremo y no tiene réplica: se exige
    #     que la muestra de aquí casi nunca lo supere (el número de
    #     excedencias de un máximo de N es ~Poisson(1): 8 o más tiene
    #     probabilidad 1e-5).
    #   · Los dos cocientes, exactos desde las cifras que los forman.
    ru = dm.get("referencia_uniforme")
    a.cierto(isinstance(ru, dict), "el módulo 10 publica la referencia de puntos uniformes")
    if isinstance(ru, dict):
        a.igual(ru["n_puntos"], len(est), "la referencia usa tantos puntos como estaciones hay")
        a.cierto(ru["n_muestras"] >= 400,
                 "  y bastantes muestras para lo que la prosa afirma",
                 f"{ru['n_muestras']} muestras")
        ref = np.sort(np.asarray(razones_thiessen_uniforme(
            pais, PROCESADO / "colombia_adm1.gpkg", len(est))))
        n_a, n_r = len(ref), ru["n_muestras"]
        for campo, p_q in (("razon_p05", 0.05), ("razon_mediana", 0.5), ("razon_p95", 0.95)):
            frac = float((ref < ru[campo]).mean())
            tol = 4 * math.sqrt(p_q * (1 - p_q) * (1 / n_r + 1 / n_a))
            a.cierto(abs(frac - p_q) <= tol,
                     f"{campo}: es el cuantil {p_q} de una simulación independiente",
                     f"deja por debajo el {frac:.4f} de {n_a} muestras propias "
                     f"(se admite {p_q} ± {tol:.4f})")
        lo_a = float(ref[int(np.floor(n_a / 2 - 1.96 * math.sqrt(n_a) / 2)) - 1])
        hi_a = float(ref[int(np.ceil(n_a / 2 + 1.96 * math.sqrt(n_a) / 2))])
        lo_r, hi_r = ru["razon_mediana_ic95"]
        a.cierto(lo_r <= ru["razon_mediana"] <= hi_r,
                 "el IC de la mediana contiene a la mediana",
                 f"{lo_r:.3f} ≤ {ru['razon_mediana']:.3f} ≤ {hi_r:.3f}")
        a.cierto(lo_r <= hi_a and lo_a <= hi_r,
                 "  y se solapa con el de la simulación independiente",
                 f"R {lo_r:.3f}–{hi_r:.3f}, aquí {lo_a:.3f}–{hi_a:.3f}")
        a.cierto(0.5 * (hi_a - lo_a) <= hi_r - lo_r <= 2 * (hi_a - lo_a),
                 "  con una anchura comparable",
                 f"R {hi_r - lo_r:.3f}, aquí {hi_a - lo_a:.3f}")
        exced = int((ref > ru["razon_max"]).sum())
        a.cierto(exced <= 7 and ru["razon_max"] >= ru["razon_p95"],
                 "razon_max es un máximo creíble de la referencia",
                 f"{exced} de {n_a} muestras propias lo superan")
        a.igual(dm["razon_areas"] / ru["razon_mediana"], ru["red_sobre_mediana"],
                "la razón de la red, en veces la mediana de la referencia", 1e-6)
        a.igual(dm["razon_areas"] / ru["razon_p95"], ru["red_sobre_p95"],
                "  y en veces su percentil 95", 1e-6)
        # Lo que la prosa afirma, comprobado contra la simulación de AQUÍ.
        a.cierto(av.max() / av.min() > 10 * float(np.quantile(ref, 0.95))
                 and av.max() / av.min() > float(ref.max()),
                 "la red queda muy por encima de un muestreo de igual probabilidad",
                 f"{av.max() / av.min():.1f} frente a un p95 de "
                 f"{float(np.quantile(ref, 0.95)):.1f} y un máximo de {float(ref.max()):.1f}")
        a.cierto(dm["razon_areas"] > ru["razon_max"],
                 "  y por encima de la mayor razón que R simuló",
                 f"{dm['razon_areas']:.1f} > {ru['razon_max']:.1f}")

    # =================================================================
    a.titulo("9 · Glosario, ecosistema y árbol de decisión")
    # =================================================================
    gl = D["glosario"]
    claves = [c["clave"] for c in gl["columnas"]]
    a.cierto(len(claves) == len(set(claves)), "las columnas del glosario no se repiten")
    # El vocabulario tiene que ir al dia con el del componente, en
    # `iniciarGlosarios()` de la plantilla. `referencia` se anadio para las
    # citas: no son prosa —no deben partirse entre el autor y la seccion— ni
    # matematica —el § no lo es—. Esta guarda es lo unico que ata las dos
    # listas, y se gano el sueldo: canto el dia que el tipo entro en la
    # plantilla y no aqui.
    a.cierto(all(c["tipo"] in ("texto", "referencia", "mate", "codigo")
                 for c in gl["columnas"]),
             "cada columna declara un tipo que el componente entiende")
    simbolos = [f["simbolo"] for f in gl["filas"]]
    a.cierto(len(simbolos) == len(set(simbolos)), "ningún símbolo repetido",
             f"{len(simbolos)} filas")
    a.cierto(len(gl["filas"]) >= 10, "el glosario cubre la notación del curso",
             f"{len(gl['filas'])} entradas")
    for f in gl["filas"]:
        a.cierto(all(k in f and str(f[k]).strip() for k in claves),
                 f"la fila «{f['simbolo']}» trae sus cuatro columnas")

    eco = D["ecosistema"]
    inst = json.loads((PRECALCULO / "versiones.json").read_text())["paquetes"]
    for p in eco["paquetes"]:
        a.cierto(p["version"] not in (None, "", "NA"),
                 f"{p['nombre']}: versión leída de la máquina", str(p["version"]))
        if p["nombre"] in inst:
            a.cierto(p["version"] == inst[p["nombre"]],
                     f"  y coincide con versiones.json", f"{p['version']}")
        a.cierto(len(p["papel"]) > 30, f"  y declara para qué sirve")
    for c in ("GDAL", "GEOS", "PROJ"):
        a.cierto(eco["sistema"][c], f"la versión de {c} está registrada",
                 eco["sistema"][c])

    ar = D["arbol"]
    ids = {n["id"] for n in ar["nodos"]}
    a.cierto(ar["raiz"] in ids, "la raíz del árbol existe", ar["raiz"])
    hojas = 0
    for n in ar["nodos"]:
        for o in n["opciones"]:
            if o["destino"] in ids:
                a.cierto(True, f"«{o['texto'][:24]}»: lleva a un nodo del árbol")
            else:
                hojas += 1
                a.cierto("metodo" in o and "capitulo" in o,
                         f"«{o['texto'][:24]}»: hoja con método y capítulo",
                         str(o.get("capitulo")))
                a.cierto(1 <= o["capitulo"] <= 10,
                         f"  y su capítulo está en el curso")
    a.cierto(hojas >= 8, "el árbol tiene hojas suficientes", str(hojas))

    # =================================================================
    a.titulo("10 · Los ejercicios guiados")
    # =================================================================
    e1 = S["e1"]["solucion"]
    a.igual(e1["n_suyas"], s["n_mas_cerca_broad"],
            "E1: las muertes de Broad St son las mismas del módulo 1")
    a.igual(e1["n_suyas"] + e1["n_otras"], s["n_muertes"], "E1: los dos grupos suman")
    a.igual(e1["d_sin_broad_suyas"] / e1["d_con_broad_suyas"], e1["factor_suyas"],
            "E1: el factor de las suyas", 1e-7)
    a.igual(e1["factor_otras"], 1.0, "E1: quitar la bomba NO mueve a las demás", 1e-9)
    a.igual(e1["d_con_broad_otras"], e1["d_sin_broad_otras"],
            "E1:   y sus distancias son idénticas", 1e-9)
    a.igual(100 * (e1["factor_suyas"] - 1), e1["exceso_pct"], "E1: el exceso publicado", 1e-6)
    a.cierto(e1["factor_suyas"] > 1.5,
             "E1: el alejamiento es sustancial", f"{e1['factor_suyas']:.5f}")

    e2 = S["e2"]["solucion"]
    cob = mun[mun.cobertura.notna()]
    a.igual(len(cob), e2["n"], "E2: municipios con cobertura")
    a.igual(cob.cobertura.mean(), e2["media"], "E2: media de la cobertura", 1e-8)
    a.igual(e2["ee_bloques"] / e2["ee_iid"], e2["factor"], "E2: el factor", 1e-7)
    a.igual(e2["n"] * (e2["ee_iid"] / e2["ee_bloques"]) ** 2, e2["n_eff"],
            "E2: el n efectivo", 1e-6)
    a.cierto(e2["contiene"], "E2: el IC honesto contiene al ingenuo")
    a.igual(e2["ancho_bloques"] - e2["ancho_iid"], e2["ancho_zona_desacuerdo"],
            "E2: el ancho de la zona de desacuerdo", 1e-7)
    a.igual(e2["zona_desacuerdo_inferior"][1], e2["ic_iid"][0],
            "E2: la zona baja termina donde empieza el IC ingenuo", 1e-8)
    a.igual(e2["zona_desacuerdo_superior"][0], e2["ic_iid"][1],
            "E2: la zona alta empieza donde acaba el IC ingenuo", 1e-8)
    a.cierto(e2["factor"] > 1, "E2: el bloque ensancha", f"{e2['factor']:.5f}")
    # R1 · T1.6 · dónde caen las réplicas del E2. Los intervalos se centran
    # en la media de los municipios por construcción; la media de las
    # réplicas por departamentos es otra, y se rehace con 400 000.
    a.igual((e2["ic_iid"][0] + e2["ic_iid"][1]) / 2, e2["media"],
            "E2: el IC ingenuo está centrado en la media de los municipios", 1e-7)
    a.igual((e2["ic_bloques"][0] + e2["ic_bloques"][1]) / 2, e2["media"],
            "E2:   y el de bloques también", 1e-7)
    a.igual(e2["media_replicas_bloques"] - e2["media"], e2["desvio_replicas_bloques"],
            "E2: el desvío de las réplicas por bloques", 1e-8)
    a.igual(e2["ee_bloques"] / math.sqrt(e2["nboot"]), e2["emc_media_bloques"],
            "E2: su error de Monte Carlo", 1e-8)
    a.cierto(abs(e2["media_replicas_iid"] - e2["media"]) < 5 * e2["ee_iid"] / math.sqrt(e2["nboot"]),
             "E2: las réplicas i.i.d. promedian la media de los municipios, salvo Monte Carlo",
             f"{e2['media_replicas_iid']:.5f} frente a {e2['media']:.5f}")
    x_c = cob.cobertura.to_numpy()
    cod_c = cob.divipola.str[:2].to_numpy()
    cods_c = np.unique(cod_c)
    ref_c = medias_bloques(np.array([x_c[cod_c == k].sum() for k in cods_c]),
                           np.array([(cod_c == k).sum() for k in cods_c]), 40)
    a.cierto(abs(e2["media_replicas_bloques"] - ref_c.mean()) < 5 * e2["emc_media_bloques"],
             "E2: la media de las réplicas por bloques, rehecha con 400 000",
             f"R {e2['media_replicas_bloques']:.5f} · aquí {ref_c.mean():.5f}")
    # Y su esperanza, que es lo que la lectura afirma: 2·10^6 réplicas en R,
    # 400 000 aquí, cinco errores conjuntos.
    emc_c = ref_c.std(ddof=1) / math.sqrt(len(ref_c))
    a.igual(e2["esperanza_replicas_bloques"] - e2["media"], e2["desvio_esperanza"],
            "E2: el desvío de la esperanza de las réplicas por bloques", 1e-8)
    a.cierto(abs(e2["esperanza_replicas_bloques"] - ref_c.mean())
             < 5 * math.hypot(e2["emc_esperanza"], emc_c),
             "E2: la esperanza de las réplicas por bloques, rehecha con 400 000",
             f"R {e2['esperanza_replicas_bloques']:.5f} ± {e2['emc_esperanza']:.5f} · "
             f"aquí {ref_c.mean():.5f} ± {emc_c:.5f}")
    a.cierto(e2["nrep_esperanza"] >= 1_000_000
             and abs(e2["emc_esperanza"] * math.sqrt(e2["nrep_esperanza"]) / ref_c.std(ddof=1) - 1) < 0.10,
             "E2:   con su error de Monte Carlo, el de ese número de réplicas")
    a.cierto(abs(e2["desvio_esperanza"]) > 10 * e2["emc_esperanza"]
             and (ref_c.mean() - x_c.mean()) * e2["desvio_esperanza"] > 0
             and abs(ref_c.mean() - x_c.mean()) > 5 * emc_c,
             "E2: el desvío de la esperanza no es ruido, y aquí sale del mismo lado",
             f"R {e2['desvio_esperanza']:.5f} · aquí {ref_c.mean() - x_c.mean():.5f}")
    a.cierto(abs(e2["media_replicas_bloques"] - e2["esperanza_replicas_bloques"])
             < 4 * e2["emc_media_bloques"],
             "E2: las 4 000 réplicas del ejercicio son compatibles con esa esperanza")

    # E3 · El n efectivo al revés, sobre la temperatura de las estaciones.
    #
    # Hasta R1 esta sección comprobaba la aritmética de un rho «medido» con
    # un correlograma por bandas y daba verde sobre un planteamiento que no
    # medía nada. Ahora rehace el ejercicio entero desde el archivo PÚBLICO
    # —el que el enunciado manda descargar—, con su propio remuestreo.
    e3 = S["e3"]["solucion"]
    a.cierto(e3["archivo"].startswith("entrega/datos/") and (RAIZ / e3["archivo"]).is_file(),
             "E3: lee un archivo publicado, y está en el repo", e3["archivo"])
    pub3 = gpd.read_file(RAIZ / e3["archivo"])
    t3 = pub3.t_media_anual.to_numpy()
    n3 = len(t3)
    a.igual(n3, e3["n"], "E3: estaciones del archivo público")
    a.igual(e3["n"], D["colombia"]["geo"]["n"], "E3: las mismas estaciones del módulo 2")
    # El archivo público es una copia del procesado. Si divergen, el
    # ejercicio y el resto del capítulo hablan de datos distintos.
    a.cierto(np.array_equal(np.sort(t3), np.sort(est.t_media_anual.to_numpy())),
             "E3:   y con las mismas temperaturas que el dato procesado")
    a.igual(t3.mean(), e3["media"], "E3: temperatura media", 1e-8)
    dep3 = pub3.departamento.to_numpy()
    nombres3 = np.unique(dep3)
    a.igual(len(nombres3), e3["n_bloques"], "E3: departamentos (bloques)")

    # Los dos remuestreos, por un camino que no es el de R.
    #
    # LA TOLERANCIA ES DE MONTE CARLO Y SE RAZONA, no se elige. R publica
    # cada error estándar con B = 4 000 réplicas: la desviación típica de
    # una réplica a otra de una desviación típica estimada así es, en
    # relativo, 1/sqrt(2B) ≈ 1.1 % si las medias remuestreadas son
    # aproximadamente normales. La referencia de aquí no tiene ese ruido:
    #   · i.i.d.: no se remuestrea. Con B infinito el bootstrap de la media
    #     da EXACTAMENTE sd(ddof=0)/sqrt(n), así que se compara con la
    #     fórmula;
    #   · bloques: 200 000 réplicas (ruido relativo ≈ 0.16 %).
    # Cinco desviaciones típicas de lo publicado son un 5.6 %: se pide 6 %.
    # El n efectivo lleva el cociente al cuadrado, así que su ruido relativo
    # es 2·sqrt(2)·1.1 % ≈ 3.2 %; cinco veces eso, 16 %. Al techo le llega
    # multiplicado por 1/(1 − n_eff/n) ≈ 1.12: 18 %. Son tolerancias anchas
    # porque el ruido lo es; lo que NO es ruido —las identidades entre las
    # cifras publicadas— se comprueba abajo a 1e-9.
    ee_iid_ref = t3.std(ddof=0) / math.sqrt(n3)
    sumas3 = np.array([t3[dep3 == k].sum() for k in nombres3])
    tam3 = np.array([(dep3 == k).sum() for k in nombres3])
    rng3 = np.random.default_rng(20929)
    medias3 = []
    for _ in range(20):
        sel3 = rng3.integers(0, len(nombres3), (10_000, len(nombres3)))
        medias3.append(sumas3[sel3].sum(axis=1) / tam3[sel3].sum(axis=1))
    ee_blq_ref = np.concatenate(medias3).std(ddof=1)
    n_eff_ref = n3 * (ee_iid_ref / ee_blq_ref) ** 2
    techo_ref = (n3 - 1) / (n3 / n_eff_ref - 1)
    a.cierto(abs(e3["ee_iid"] / ee_iid_ref - 1) < 0.06,
             "E3: el e.e. i.i.d. es el de la fórmula, salvo Monte Carlo",
             f"R {e3['ee_iid']:.5f} · exacto {ee_iid_ref:.5f}")
    a.cierto(abs(e3["ee_bloques"] / ee_blq_ref - 1) < 0.06,
             "E3: el e.e. por departamentos, rehecho con 200 000 réplicas",
             f"R {e3['ee_bloques']:.5f} · aquí {ee_blq_ref:.5f}")
    a.cierto(abs(e3["n_eff"] / n_eff_ref - 1) < 0.16,
             "E3: el n efectivo, rehecho", f"R {e3['n_eff']:.3f} · aquí {n_eff_ref:.3f}")
    a.cierto(abs(e3["techo"] / techo_ref - 1) < 0.18,
             "E3: el techo, rehecho", f"R {e3['techo']:.3f} · aquí {techo_ref:.3f}")
    # La conclusión no puede depender del ruido: la referencia sin ruido
    # también deja el techo entre los dos objetivos.
    obj_bajo, obj_alto = e3["objetivos"]
    a.cierto(obj_bajo < techo_ref < obj_alto,
             f"E3: con 200 000 réplicas el techo también queda entre {obj_bajo} y {obj_alto}",
             f"{techo_ref:.3f}")
    a.cierto(e3["otras_semillas"]["n_eff_min"] <= n_eff_ref <= e3["otras_semillas"]["n_eff_max"],
             "E3: el rango de las otras semillas contiene a la referencia",
             f"{e3['otras_semillas']['n_eff_min']:.3f} a {e3['otras_semillas']['n_eff_max']:.3f}")
    a.cierto(obj_bajo < e3["otras_semillas"]["techo_min"]
             <= e3["otras_semillas"]["techo_max"] < obj_alto,
             "E3: y con ninguna de ellas el techo sale de entre los dos objetivos")
    a.cierto(e3["otras_semillas"]["n_eff_min"] < e3["otras_semillas"]["n_eff_max"]
             and e3["otras_semillas"]["techo_min"] < e3["otras_semillas"]["techo_max"],
             "E3:   y el rango es un rango")
    a.igual((n3 - 1) / (n3 / e3["otras_semillas"]["n_eff_min"] - 1),
            e3["otras_semillas"]["techo_min"], "E3:   cuyo techo mínimo es el del n_eff mínimo", 1e-8)
    a.igual((n3 - 1) / (n3 / e3["otras_semillas"]["n_eff_max"] - 1),
            e3["otras_semillas"]["techo_max"], "E3:   y el máximo, el del máximo", 1e-8)

    # Las identidades. Todas se rehacen DESDE n_eff, y no unas de otras: el
    # JSON guarda diez decimales, y un rho redondeado a 1e-10 mueve el
    # techo 1e-7 y las estaciones para 25, 2e-7. Desde n_eff el error de
    # redondeo que se propaga queda por debajo de 2e-10.
    a.igual(e3["ee_bloques"] / e3["ee_iid"], e3["factor"], "E3: el factor", 1e-7)
    a.igual(e3["n"] * (e3["ee_iid"] / e3["ee_bloques"]) ** 2, e3["n_eff"],
            "E3: el n efectivo es n·(ee_iid/ee_bloques)²", 1e-6)
    a.igual(100 * e3["n_eff"] / e3["n"], e3["pct_informacion"], "E3: el porcentaje", 1e-8)
    rho3 = (e3["n"] / e3["n_eff"] - 1) / (e3["n"] - 1)
    a.igual(rho3, e3["rho_medio"], "E3: la correlación media se despeja del n efectivo", 1e-9)
    a.igual(1 / rho3, e3["techo"], "E3: el techo es 1/rho", 1e-9)
    a.igual(obj_bajo * (1 - rho3) / (1 - obj_bajo * rho3), e3["n_para_25"],
            f"E3: las estaciones para la precisión de {obj_bajo} independientes", 1e-9)
    a.igual(math.ceil(e3["n_para_25"]), e3["estaciones_para_25"],
            "E3:   y su redondeo hacia arriba")
    a.cierto(e3["estaciones_para_25"] / (1 + (e3["estaciones_para_25"] - 1) * rho3) >= obj_bajo
             > (e3["estaciones_para_25"] - 1) / (1 + (e3["estaciones_para_25"] - 2) * rho3),
             "E3:   que es la primera red que llega al objetivo")
    a.cierto(e3["estaciones_para_25"] < e3["n"], "E3:   y la red actual ya la supera")
    a.cierto(0 < e3["rho_medio"] and e3["n_eff"] < e3["n"],
             "E3: el remuestreo por bloques ensancha", f"rho = {e3['rho_medio']:.5f}")
    a.cierto(e3["n_eff"] < e3["techo"], "E3: el n efectivo respeta su techo")
    # Las banderas se recalculan, no se creen.
    a.cierto(e3["objetivo_25_alcanzable"] == (obj_bajo * rho3 < 1)
             and e3["objetivo_50_alcanzable"] == (obj_alto * rho3 < 1),
             "E3: las banderas dicen lo que dice el techo")
    a.cierto(e3["objetivo_25_alcanzable"] and not e3["objetivo_50_alcanzable"],
             f"E3: {obj_bajo} independientes se alcanzan y {obj_alto} no",
             f"techo {e3['techo']:.5f}")
    # Apartado (c): el promedio centrado de todos los pares, sobre el dato.
    z3 = t3 - t3.mean()
    centrado3 = ((z3.sum() ** 2 - (z3 ** 2).sum()) / (n3 * (n3 - 1))) / (z3 ** 2).mean()
    a.igual(centrado3, e3["centrado_todos_los_pares"],
            "E3: el promedio centrado de todos los pares, sobre las temperaturas", 1e-9)
    a.igual(-1 / (n3 - 1), e3["centrado_todos_los_pares"], "E3:   y vale −1/(n − 1)", 1e-9)
    a.cierto(not ({"bandas_km", "moran_por_banda", "pares_por_banda"} & set(e3)),
             "E3: no vuelve el correlograma por bandas")
    a.cierto(any(p["paso"] == f"(b) Estaciones para la precisión de {obj_alto}"
                 and isinstance(p["valor"], str) for p in S["e3"]["pasos"]),
             "E3: la tabla responde también al objetivo que no se alcanza")

    # --- E3, segunda vuelta: el dato, la altitud y los pesos por filas ---
    #
    # El orden de los bloques. R los fija con sort(method = "radix"), que es
    # el orden de los bytes; np.unique ordena por punto de código, que en
    # UTF-8 es el mismo orden. Si la lista publicada no viene así, el
    # generador ha vuelto a depender de LC_COLLATE.
    jk3 = e3["jackknife"]
    lista3 = jk3["por_departamento"]
    a.cierto([d["departamento"] for d in lista3] == list(nombres3),
             "E3: los departamentos van en orden de bytes, no en el de la regional",
             f"{len(lista3)} departamentos")
    a.cierto([d["estaciones"] for d in lista3] == [int(v) for v in tam3],
             "E3:   y cada uno con sus estaciones")

    # Un departamento menos. El e.e. i.i.d. sale de la fórmula y el de
    # bloques de 50 000 réplicas propias. R usa B = 20 000: por la regla
    # 1/sqrt(2B) su techo llevaría un ruido relativo de ≈ 1.6 %, pero esa
    # regla supone normalidad y aquí se queda corta —las medias por bloques
    # tienen colas, y dos corridas largas de la red entera difieren más de
    # lo que predice—, así que se pide un 10 % y no cinco veces 1.6 %. Es
    # ancho, y aun así separa lo que importa: el departamento que voltea la
    # respuesta está a más de un 10 % del umbral.
    techos_ref = []
    for k, nombre in enumerate(nombres3):
        queda = dep3 != nombre
        n_k = int(queda.sum())
        ee_i = t3[queda].std(ddof=0) / math.sqrt(n_k)
        s_k, m_k = np.delete(sumas3, k), np.delete(tam3, k)
        medias_k = []
        for _ in range(5):
            sel_k = rng3.integers(0, len(s_k), (10_000, len(s_k)))
            medias_k.append(s_k[sel_k].sum(axis=1) / m_k[sel_k].sum(axis=1))
        ee_b = np.concatenate(medias_k).std(ddof=1)
        ne_k = n_k * (ee_i / ee_b) ** 2
        techos_ref.append((n_k - 1) / (n_k / ne_k - 1))
    techos_ref = np.array(techos_ref)
    techos_pub = np.array([d["techo"] for d in lista3])
    peor3 = int(np.argmax(np.abs(techos_pub / techos_ref - 1)))
    a.cierto(np.all(np.abs(techos_pub / techos_ref - 1) < 0.10),
             "E3: el techo sin cada departamento, rehecho uno a uno",
             f"el peor: {nombres3[peor3]}, R {techos_pub[peor3]:.3f} · aquí {techos_ref[peor3]:.3f}")
    # R2 de T1.6 · el recorrido del E3 es sensibilidad; la lectura da además
    # el error estándar jackknife del techo, que sale de la misma lista.
    a.igual(math.sqrt((len(techos_pub) - 1) / len(techos_pub)
                      * ((techos_pub - techos_pub.mean()) ** 2).sum()), jk3["ee_techo"],
            "E3: el e.e. jackknife del techo sale de la lista", 1e-7)
    a.cierto((techos_pub.max() - techos_pub.min()) / 2 < jk3["ee_techo"],
             "E3:   y medio recorrido queda por debajo de él",
             f"{(techos_pub.max() - techos_pub.min()) / 2:.3f} < {jk3['ee_techo']:.3f}")
    a.igual(techos_pub.min(), jk3["minimo"]["techo"], "E3: el techo mínimo es el de la lista", 1e-12)
    a.igual(techos_pub.max(), jk3["maximo"]["techo"], "E3: y el máximo también", 1e-12)
    a.cierto(jk3["minimo"]["departamento"] == nombres3[int(techos_pub.argmin())]
             and jk3["maximo"]["departamento"] == nombres3[int(techos_pub.argmax())],
             "E3:   cada uno con su departamento",
             f"{jk3['minimo']['departamento']} y {jk3['maximo']['departamento']}")
    a.cierto(jk3["minimo"]["estaciones"] == int(tam3[int(techos_pub.argmin())])
             and jk3["maximo"]["estaciones"] == int(tam3[int(techos_pub.argmax())]),
             "E3:   y con sus estaciones")
    a.igual(int((techos_pub > obj_alto).sum()), jk3["n_sobre_objetivo"],
            f"E3: cuántos departamentos llevan el techo por encima de {obj_alto}")
    a.cierto(jk3["n_sobre_objetivo"] == 1,
             "E3: un solo departamento voltea la respuesta, como dice la lectura")
    # Y lo mismo con el remuestreo de aquí: que no sea cosa de la semilla de R.
    a.cierto(int((techos_ref > obj_alto).sum()) == 1
             and nombres3[int(techos_ref.argmax())] == jk3["maximo"]["departamento"],
             "E3:   y con el remuestreo propio es el mismo departamento",
             f"{nombres3[int(techos_ref.argmax())]}: {techos_ref.max():.3f}")
    a.cierto(jk3["minimo"]["departamento"] in
             {nombres3[i] for i in np.argsort(techos_ref)[:3]},
             "E3:   y el del mínimo está entre los tres más bajos de aquí",
             f"{jk3['minimo']['departamento']}: {techos_ref[list(nombres3).index(jk3['minimo']['departamento'])]:.3f}")
    a.cierto(jk3["minimo"]["techo"] < e3["otras_semillas"]["techo_min"]
             and e3["otras_semillas"]["techo_max"] < jk3["maximo"]["techo"],
             "E3: quitar un departamento mueve el techo más que cambiar de semilla")
    a.cierto(0 < e3["otras_semillas"]["techo_sd"]
             < e3["otras_semillas"]["techo_max"] - e3["otras_semillas"]["techo_min"],
             "E3: la desviación entre semillas cabe en su recorrido",
             f"{e3['otras_semillas']['techo_sd']:.3f}")
    a.cierto(jk3["nboot"] > e3["nboot"], "E3: el jackknife usa más réplicas que el ejercicio",
             f"{jk3['nboot']} frente a {e3['nboot']}")

    # (d) Los residuos de la temperatura sobre la altitud.
    r3 = e3["residuos"]
    alt3 = pub3.altitud_m.to_numpy()
    coef3 = np.polyfit(alt3, t3, 1)
    res3 = t3 - np.polyval(coef3, alt3)
    a.igual(1 - (res3 ** 2).sum() / ((t3 - t3.mean()) ** 2).sum(), r3["r2"],
            "E3 (d): el R² de la temperatura sobre la altitud", 1e-9)
    ee_iid_res = res3.std(ddof=0) / math.sqrt(n3)
    sumas_r = np.array([res3[dep3 == k].sum() for k in nombres3])
    medias_r = []
    for _ in range(20):
        sel_r = rng3.integers(0, len(nombres3), (10_000, len(nombres3)))
        medias_r.append(sumas_r[sel_r].sum(axis=1) / tam3[sel_r].sum(axis=1))
    ee_blq_res = np.concatenate(medias_r).std(ddof=1)
    n_eff_res = n3 * (ee_iid_res / ee_blq_res) ** 2
    techo_res = (n3 - 1) / (n3 / n_eff_res - 1)
    # Las mismas tolerancias de Monte Carlo que arriba, por la misma cuenta.
    a.cierto(abs(r3["ee_iid"] / ee_iid_res - 1) < 0.06,
             "E3 (d): el e.e. i.i.d. de los residuos, salvo Monte Carlo",
             f"R {r3['ee_iid']:.5f} · exacto {ee_iid_res:.5f}")
    a.cierto(abs(r3["ee_bloques"] / ee_blq_res - 1) < 0.06,
             "E3 (d): el e.e. por departamentos de los residuos, rehecho",
             f"R {r3['ee_bloques']:.5f} · aquí {ee_blq_res:.5f}")
    a.cierto(abs(r3["n_eff"] / n_eff_res - 1) < 0.16,
             "E3 (d): el n efectivo de los residuos, rehecho",
             f"R {r3['n_eff']:.3f} · aquí {n_eff_res:.3f}")
    a.cierto(abs(r3["techo"] / techo_res - 1) < 0.18,
             "E3 (d): el techo de los residuos, rehecho",
             f"R {r3['techo']:.3f} · aquí {techo_res:.3f}")
    a.cierto(techo_res > obj_alto and techo_res > techo_ref,
             f"E3 (d): con 200 000 réplicas ese techo también pasa de {obj_alto} y del de (b)",
             f"{techo_res:.3f}")
    a.cierto(obj_alto < e3["otras_semillas"]["residuos_techo_min"]
             < e3["otras_semillas"]["residuos_techo_max"],
             f"E3 (d): con las otras semillas tampoco baja de {obj_alto}",
             f"{e3['otras_semillas']['residuos_techo_min']:.3f} a "
             f"{e3['otras_semillas']['residuos_techo_max']:.3f}")
    a.igual(e3["n"] * (r3["ee_iid"] / r3["ee_bloques"]) ** 2, r3["n_eff"],
            "E3 (d): el n efectivo es n·(ee_iid/ee_bloques)²", 1e-6)
    rho_r = (e3["n"] / r3["n_eff"] - 1) / (e3["n"] - 1)
    a.igual(rho_r, r3["rho_medio"], "E3 (d): la correlación media se despeja del n efectivo", 1e-9)
    a.igual(1 / rho_r, r3["techo"], "E3 (d): el techo es 1/rho", 1e-9)
    a.igual(100 * (1 - rho_r / rho3), r3["caida_rho_pct"],
            "E3 (d): la caída relativa de la correlación", 1e-7)
    a.cierto(0 < r3["caida_rho_pct"] < 100, "E3 (d):   y es una caída",
             f"{r3['caida_rho_pct']:.3f} %")
    a.igual(obj_alto * (1 - rho_r) / (1 - obj_alto * rho_r), r3["n_para_50"],
            f"E3 (d): las estaciones para la precisión de {obj_alto}", 1e-7)
    a.igual(obj_bajo * (1 - rho_r) / (1 - obj_bajo * rho_r), r3["n_para_25"],
            f"E3 (d): y para la de {obj_bajo}", 1e-9)
    a.igual(math.ceil(r3["n_para_50"]), r3["estaciones_para_50"],
            "E3 (d):   con su redondeo hacia arriba")
    a.cierto(r3["objetivo_50_alcanzable"] == (obj_alto * rho_r < 1)
             and r3["techo_sube"] == (r3["techo"] > e3["techo"]),
             "E3 (d): las banderas dicen lo que dicen las cifras")
    a.cierto(r3["objetivo_50_alcanzable"] and r3["techo_sube"],
             f"E3 (d): con los residuos {obj_alto} independientes pasan a ser alcanzables")

    # (c) El promedio por bandas con pesos estandarizados por filas. No hay
    # azar: se rehace exacto. La I de cada banda, con pesos 1/(vecinos de i),
    # ponderada por los pares de la banda; las bandas cubren todos los pares.
    pf3 = e3["pesos_filas"]
    xy3 = np.column_stack([pub3.geometry.x.to_numpy(), pub3.geometry.y.to_numpy()])
    dist3 = np.sqrt(((xy3[:, None, :] - xy3[None, :, :]) ** 2).sum(-1)) / 1000
    for ancho, publicado in zip(pf3["anchos_km"], pf3["promedio"]):
        cortes = np.arange(0, math.ceil(dist3.max() / ancho) * ancho + ancho / 2, ancho)
        num = pares = 0.0
        for lo, hi in zip(cortes[:-1], cortes[1:]):
            A = ((dist3 > lo) & (dist3 <= hi)).astype(float)
            np.fill_diagonal(A, 0)
            card = A.sum(axis=1)
            con = card > 0
            if not con.any():
                continue
            W = A[con] / card[con, None]
            I_b = (n3 / con.sum()) * (W * np.outer(z3[con], z3)).sum() / (z3 ** 2).sum()
            num += I_b * A.sum() / 2
            pares += A.sum() / 2
        a.igual(pares, n3 * (n3 - 1) / 2, f"E3 (c): las bandas de {ancho} km cubren todos los pares")
        a.igual(num / pares, publicado,
                f"E3 (c): el promedio con pesos por filas, bandas de {ancho} km", 1e-9)
    a.cierto(all(v > 0 for v in pf3["promedio"])
             and len({round(v, 5) for v in pf3["promedio"]}) == len(pf3["promedio"]),
             "E3 (c): sale positivo y cambia con el ancho de banda",
             " · ".join(f"{v:.5f}" for v in pf3["promedio"]))
    a.cierto(all(abs(v - e3["centrado_todos_los_pares"]) > 0.01 for v in pf3["promedio"]),
             "E3 (c):   y no es el −1/(n − 1) de los pesos iguales")
    # La tabla publica lo que la lectura afirma.
    pasos3 = {p["paso"]: p["valor"] for p in S["e3"]["pasos"]}
    a.cierto(pasos3.get(f"(b) Techo sin {jk3['minimo']['departamento']}") == jk3["minimo"]["techo"]
             and pasos3.get(f"(b) Techo sin {jk3['maximo']['departamento']}") == jk3["maximo"]["techo"],
             "E3: la tabla trae los dos extremos del jackknife")
    a.cierto(pasos3.get(f"(b) Estaciones para la precisión de {obj_bajo}") == e3["estaciones_para_25"]
             and pasos3.get(f"(d) Estaciones para la precisión de {obj_alto}") == r3["estaciones_para_50"],
             "E3: y las estaciones enteras de (b) y de (d)")

    e4 = S["e4"]["solucion"]
    a.igual(e4["municipal"]["r"], ec["principal"]["r_municipal"],
            "E4: la r municipal coincide con la del módulo 7", 1e-9)
    a.igual(e4["departamental"]["r"], ec["principal"]["r_departamental"],
            "E4: y la departamental también", 1e-9)
    a.igual(e4["k_intermedia"], e4["conglomerado"]["n"], "E4: los conglomerados pedidos")
    # La misma lección que arriba: la bandera se recalcula, no se cree.
    escalera = [e4["municipal"]["r"], e4["conglomerado"]["r"],
                e4["departamental"]["r"]]
    a.cierto(e4["monotona"] ==
             (escalera[0] <= escalera[1] <= escalera[2]),
             "E4: la bandera de monotonía dice lo que dicen las tres r")
    a.cierto(escalera[0] <= escalera[1] <= escalera[2],
             "E4: y la r crece con el tamaño de la unidad",
             " -> ".join(f"{r:.4f}" for r in escalera))
    a.cierto(e4["municipal"]["n"] > e4["conglomerado"]["n"] > e4["departamental"]["n"],
             "E4: y las unidades son cada vez menos")
    a.igual(100 * (e4["departamental"]["r"] / e4["municipal"]["r"] - 1),
            e4["subida_mun_dep_pct"], "E4: la subida publicada", 1e-6)
    for k in ("e1", "e2", "e3", "e4"):
        a.cierto(len(S[k]["enunciado"]) > 100, f"{k}: el enunciado es un enunciado")
        a.cierto(len(S[k]["lectura"]) > 100, f"{k}: trae su lectura")
        a.cierto(len(S[k]["pasos"]) >= 4, f"{k}: trae los pasos intermedios",
                 str(len(S[k]["pasos"])))

    # =================================================================
    a.titulo("11 · Los .geomapa")
    # =================================================================
    esperados = {"snow", "japanesepines", "redwood", "cells", "nc", "meuse",
                 "bogota", "desercion", "ideam", "campos", "realizaciones"}
    a.cierto(esperados <= set(M), "están todos los mapas del capítulo",
             f"faltan: {sorted(esperados - set(M))}")

    geograficos = ["snow", "japanesepines", "redwood", "cells", "nc", "meuse",
                   "bogota", "desercion", "ideam"]
    # Se mide como lo escribe R —sin espacios tras los separadores—, o el
    # informe acusaría de gordo a un archivo que no lo es: `json.dumps`
    # con sus valores por defecto añade 21 KB de espacios que nunca
    # llegan al disco.
    compacto = dict(ensure_ascii=False, separators=(",", ":"))
    kb_geo = sum(len(json.dumps(M[k], **compacto).encode()) / 1024
                 for k in geograficos if k in M)
    kb_tot = sum(len(json.dumps(v, **compacto).encode()) / 1024
                 for v in M.values())
    a.cierto(kb_geo <= 120, "la geometría cabe en el presupuesto de 120 KB",
             f"{kb_geo:.1f} KB")
    # 160 y no 120 desde R2 · T2.3: es la alarma del conjunto que ya usa el
    # generador (geometría más rejillas simuladas); la geometría sola sigue
    # contra sus 120.
    a.cierto(kb_tot <= 160, "y el conjunto de mapas no dispara su alarma", f"{kb_tot:.1f} KB")

    for k in geograficos:
        g = M[k]
        a.cierto(g.get("modo") in ("puntos", "poligonos", "grafo", "rejilla",
                                   "proyeccion"),
                 f"'{k}' declara un modo válido", str(g.get("modo")))
        a.cierto(bool(g.get("titulo")), f"'{k}' trae título")
        cj = g["caja"]
        a.cierto(cj[2] > cj[0] and cj[3] > cj[1], f"'{k}' tiene una caja no degenerada")
        if g["modo"] == "puntos":
            a.igual(len(g["pts"]), 2 * g["n"], f"'{k}': dos coordenadas por punto")
            a.cierto(all(0 <= v <= g["q"] for v in g["pts"]),
                     f"'{k}': todo punto cae dentro de la cuantización")
            if "marcas" in g:
                a.igual(len(g["marcas"]), g["n"], f"'{k}': una marca por punto")
        if g["modo"] == "poligonos":
            a.igual(len(g["geom"]), g["n"], f"'{k}': una geometría por unidad")
            a.igual(len(g["valor"]), g["n"], f"'{k}': un valor por unidad")
            a.igual(len(g["clase"]), g["n"], f"'{k}': una clase por unidad")
            a.igual(len(g["cortes"]), 6, f"'{k}': 5 clases dan 6 cortes")
            a.cierto(all(g["cortes"][i] <= g["cortes"][i + 1]
                         for i in range(len(g["cortes"]) - 1)),
                     f"'{k}': los cortes van en orden")
            a.igual(sum(g["tam"]), g["n"], f"'{k}': los tamaños de clase suman n")
            a.cierto(min(g["valor"]) >= g["cortes"][0] - 1e-9 and
                     max(g["valor"]) <= g["cortes"][-1] + 1e-9,
                     f"'{k}': los cortes cubren el recorrido del valor")
            a.cierto(len(g["etiquetas"]) == g["n"], f"'{k}': una etiqueta por unidad")
            # LA COMPROBACIÓN QUE FALTABA, y la destapó el arnés: cambiar
            # un corte intermedio dejaba los cortes ordenados, los tamaños
            # sumando n y el recorrido cubierto, así que TODO pasaba. Los
            # cortes hay que confrontarlos con la asignación de clase que
            # los acompaña, que es lo único que los ata al dato.
            #
            # Convenio de classInt (hallazgo A.2): [a, b) en todas las
            # clases menos la última, que cierra por la derecha. El de
            # mapclassify es el otro, y ésa es justo la discrepancia que
            # el capítulo 3 trabaja — así que aquí se comprueba EL DE R,
            # que es el que calculó estos cortes.
            cortes, mal = g["cortes"], []
            ultima = len(cortes) - 1
            for idx, (v, cl) in enumerate(zip(g["valor"], g["clase"])):
                lo, hi = cortes[cl - 1], cortes[cl]
                dentro = (lo - 1e-9 <= v < hi + 1e-9) if cl < ultima else \
                         (lo - 1e-9 <= v <= hi + 1e-9)
                if not dentro:
                    mal.append((idx, v, cl))
            a.cierto(not mal,
                     f"'{k}': cada valor cae en la clase de sus cortes",
                     "" if not mal else f"{len(mal)} fuera, p. ej. {mal[:3]}")
            # Y que ninguna clase declarada quede vacía sin que `tam` lo diga.
            for cl in range(1, len(cortes)):
                a.igual(sum(1 for c in g["clase"] if c == cl), g["tam"][cl - 1],
                        f"'{k}': la clase {cl} tiene el tamaño que declara")

    # Los cortes de nc tienen que ser los de la tasa que se publicó.
    a.cierto(abs(M["nc"]["cortes"][0] - D["area_canonico"]["tasa_min"]) < 1e-6,
             "el primer corte de nc es la tasa mínima")
    a.cierto(abs(M["nc"]["cortes"][-1] - D["area_canonico"]["tasa_max"]) < 1e-6,
             "y el último es la máxima")
    a.igual(M["snow"]["n"], s["n_muertes"], "el mapa de Snow lleva las 578 muertes")
    a.igual(M["snow"]["n2"], s["n_bombas"], "y las 13 bombas")
    a.igual(len(M["snow"]["lineas"]), s["n_segmentos"], "y los 528 segmentos de calle")
    a.igual(M["snow"]["resaltado2"], s["bomba_broad"], "con Broad St resaltada")
    a.igual(len(M["snow"]["etiquetas2"]), s["n_bombas"], "y una etiqueta por bomba")
    a.igual(M["bogota"]["n"], D["colombia"]["puntual"]["n"], "el mapa de Bogotá")
    a.igual(M["ideam"]["n"], D["colombia"]["geo"]["n"], "el mapa del IDEAM")
    a.igual(M["desercion"]["n"], esc["n_departamental"], "el mapa de deserción")

    for lista, etq in ((M["campos"], "campo"), (M["realizaciones"], "realización")):
        for i, g in enumerate(lista):
            a.cierto(g["modo"] == "rejilla", f"{etq} {i}: modo rejilla")
            a.igual(len(g["zq"]), g["nx"] * g["ny"], f"{etq} {i}: celdas declaradas")
            a.cierto(all(-1 <= v <= g["zqmax"] for v in g["zq"]),
                     f"{etq} {i}: la cuantización está en rango")
            a.cierto(g["rango"][0] < g["rango"][1], f"{etq} {i}: rango no degenerado")
    for g in M["campos"]:
        # 1e-8 y no 1e-9: `cap1_mapas.json` se escribe con 8 cifras
        # significativas a propósito —la geometría no necesita más y el
        # presupuesto sí lo nota—, así que exigir la décima sería exigir
        # una precisión que el archivo no guarda.
        # phi = 0 es el caso límite —rho(h) = 0 para todo h > 0— y no un
        # valor más: `math.exp(-1/0)` no da 0, lanza ZeroDivisionError.
        esperado = 0.0 if g["phi"] == 0 else math.exp(-1 / g["phi"])
        a.igual(esperado, g["rho_vecino"],
                f"campo phi={g['phi']}: correlación entre vecinos", 1e-8)
        a.cierto(-1 <= g["moran"] <= 1, f"campo phi={g['phi']}: I es un I")
    morans = [g["moran"] for g in M["campos"]]
    a.cierto(all(morans[i] < morans[i + 1] for i in range(len(morans) - 1)),
             "el I de los campos crece con el rango",
             " < ".join(f"{m:.4f}" for m in morans))
    # =================================================================
    a.titulo("11b · Lo que se ve en cada mapa")
    # =================================================================
    # «Describir el mapa» (2026-11-02): DÓNDE caen los extremos de la
    # deserción, la clase alta de Carolina del Norte y las estaciones más
    # frías y más cálidas, y cuántas sedes de Bogotá hay en cada franja de
    # norte a sur. Con geopandas sobre las capas, y los centroides del
    # polígono mayor, como R. Cada mapa con su guarda de «está»: el arnés
    # los rompe a propósito, y un auditor que revienta no informa de nada.
    from collections import Counter
    from describe_mapa import zona_por_tercios

    def _zona(x, y, caja):
        return zona_por_tercios((x - caja[0]) / (caja[2] - caja[0]),
                                1 - (y - caja[1]) / (caja[3] - caja[1]))

    def _centro(g):
        if g.geom_type == "MultiPolygon":
            g = max(g.geoms, key=lambda pp: pp.area)
        return g.centroid

    def _tabla(z):
        return sorted(Counter(z).items(), key=lambda kv: (-kv[1], kv[0]))

    V = D.get("visto", {})
    ds, md = V.get("desercion", {}), M.get("desercion", {})
    if ds and md.get("etiquetas") and md.get("caja"):
        dep_v = gpd.read_file(PROCESADO / "colombia_adm1.gpkg")
        nom = {("Bogotá D. C." if s == "Bogota Capital District" else s): g
               for s, g in zip(dep_v["shapeName"], dep_v.geometry)}
        filas = sorted(zip(md["valor"], md["etiquetas"]), key=lambda f: -f[0])
        ok = True
        for clave, ff in (("mayores", filas[:3]), ("menores", filas[::-1][:3])):
            esp = [(e, round(v, 6), _zona(_centro(nom[e]).x, _centro(nom[e]).y, md["caja"]) if e in nom else "?")
                   for v, e in ff]
            pub = [(f["departamento"], round(f["pct"], 6), f["zona"]) for f in ds.get(clave, [])]
            ok = ok and esp == pub
        a.cierto(ok, "visto: los extremos de la deserción y su zona",
                 f"{filas[0][1]} y {filas[-1][1]}")
        # R2 · T2.3 (ronda 3): la clase más oscura entera, por zona.
        ca_ = ds.get("clase_alta") or {}
        zal = [_zona(_centro(nom[e]).x, _centro(nom[e]).y, md["caja"]) if e in nom else "?"
               for e, k in zip(md["etiquetas"], md["clase"]) if k == max(md["clase"])]
        a.cierto(ca_.get("n") == len(zal)
                 and list(zip((ca_.get("zonas") or {}).get("zona", []), (ca_.get("zonas") or {}).get("n", []))) == _tabla(zal),
                 "visto: deserción, la clase más oscura por zona", ", ".join(f"{z} {k}" for z, k in _tabla(zal)))
        # Y el nombre del Distrito Capital en español, en todo el mapa: la
        # tabla de respaldo lo publicaba en inglés («Bogota Capital District»).
        a.cierto("Bogotá D. C." in md["etiquetas"] and not any("District" in e for e in md["etiquetas"]),
                 "visto: el mapa de deserción nombra Bogotá en español")
    else:
        a.cierto(False, "visto: los extremos de la deserción y su zona", "falta el dato o el mapa")
    vn, mn = V.get("nc", {}), M.get("nc", {})
    if vn and mn.get("clase") and len(mn["clase"]) == len(nc):
        nc_u = nc.to_crs(32617)
        zn = [_zona(_centro(g).x, _centro(g).y, mn["caja"]) for g in nc_u.geometry]
        alta = [z for z, k in zip(zn, mn["clase"]) if k == max(mn["clase"])]
        a.cierto(vn["clase_alta_n"] == len(alta) and list(zip(vn["zona"], vn["n"])) == _tabla(alta),
                 "visto: Carolina del Norte, la clase alta por zona",
                 ", ".join(f"{z} {k}" for z, k in _tabla(alta)[:3]))
    else:
        a.cierto(False, "visto: Carolina del Norte, la clase alta por zona", "falta el dato o el mapa")
    vi, mi = V.get("ideam", {}), M.get("ideam", {})
    if vi and mi.get("caja"):
        q10, q90 = np.quantile(est.t_media_anual.to_numpy(), [0.1, 0.9])
        zi = [_zona(x, y, mi["caja"]) for x, y in zip(est.geometry.x, est.geometry.y)]
        tt = est.t_media_anual.to_numpy()
        fr = _tabla([z for z, v in zip(zi, tt) if v <= q10])
        ca = _tabla([z for z, v in zip(zi, tt) if v >= q90])
        a.cierto(abs(q10 - vi["frias_umbral"]) < 1e-8 and abs(q90 - vi["calidas_umbral"]) < 1e-8
                 and list(zip(vi["frias"]["zona"], vi["frias"]["n"])) == fr
                 and list(zip(vi["calidas"]["zona"], vi["calidas"]["n"])) == ca,
                 "visto: IDEAM, las frías y las cálidas por zona",
                 f"frías {fr[:2]} · cálidas {ca[:2]}")
        # Ronda 4: el décimo más alto por zona, y cuánto baja la temperatura por km.
        alt = est.altitud_m.to_numpy(float)
        qa = float(np.quantile(alt, 0.9))
        za = _tabla([z for z, h in zip(zi, alt) if h >= qa])
        al_ = vi.get("altas") or {}
        a.cierto(abs(qa - al_.get("umbral_m", -1)) < 1e-6 and al_.get("n") == int((alt >= qa).sum())
                 and list(zip((al_.get("zonas") or {}).get("zona", []), (al_.get("zonas") or {}).get("n", []))) == za,
                 "visto: IDEAM, las estaciones más altas por zona", ", ".join(f"{z} {k}" for z, k in za))
        a.igual(-np.polyfit(alt, tt, 1)[0] * 1000, vi.get("baja_por_km"), "visto: IDEAM, cuánto baja la temperatura por km", 1e-6)
        a.cierto(vi.get("n_frias") == int((tt <= q10).sum()) and vi.get("n_calidas") == int((tt >= q90).sum()),
                 "visto: IDEAM, cuántas son las más frías y las más cálidas",
                 f"{int((tt <= q10).sum())} y {int((tt >= q90).sum())}")
    else:
        a.cierto(False, "visto: IDEAM, las frías y las cálidas por zona", "falta el dato o el mapa")
    # R2 · T2.3 (ronda 3): de qué lado del eje principal de la nube de meuse
    # cae el décimo con más zinc. Con numpy, por la vía de los autovectores
    # de la covarianza y no por la del ángulo que usa R.
    vme = V.get("meuse", {})
    mcsv = pd.read_csv(SALIDAS / "cap1_meuse.csv")
    xy_m = mcsv[["x", "y"]].to_numpy(float); zm = mcsv.zinc.to_numpy(float)
    dm = xy_m - xy_m.mean(axis=0)
    val, vec = np.linalg.eigh(dm.T @ dm)
    eje = vec[:, np.argmax(val)]
    nrm = np.array([-eje[1], eje[0]])
    if nrm[0] > 0 or nrm[1] < 0:
        nrm = -nrm
    top = np.argsort(-zm, kind="stable")[:max(1, len(zm) // 10)]
    nw = int(((dm[top] @ nrm) > 0).sum())
    a.cierto(vme.get("top_n") == len(top) and vme.get("top_noroeste") == nw
             and vme.get("lado") == ("noroeste" if 2 * nw > len(top) else "sureste")
             and vme.get("diagonal") == bool((dm[:, 0] * dm[:, 1]).sum() > 0),
             "visto: meuse, el lado de la nube donde cae el zinc alto", f"{nw} de {len(top)}")
    vb, mb = V.get("bogota", {}), M.get("bogota", {})
    if vb and mb.get("caja"):
        cj = mb["caja"]
        fy = (cole.geometry.y.to_numpy() - cj[1]) / (cj[3] - cj[1])
        fr = ["sur" if f < 1 / 3 else ("centro" if f < 2 / 3 else "norte") for f in fy]
        esp = [Counter(fr)[f] for f in ("norte", "centro", "sur")]
        a.cierto(vb["franja"] == ["norte", "centro", "sur"] and vb["n"] == esp,
                 "visto: Bogotá, las sedes por franja", f"{esp}")
        # R2 · T2.3 (ronda 2): por franja, las sedes del perímetro urbano y las
        # de fuera del Distrito, punto a punto contra los polígonos (no contra
        # las columnas del dato), y dónde acaba el perímetro respecto del corte.
        from shapely import contains_xy as _cxy2
        _ur = gpd.read_file(PROCESADO / "bogota_ventana_urbana.gpkg").to_crs(cole.crs).geometry.union_all()
        _dc = gpd.read_file(PROCESADO / "bogota_ventana_dc.gpkg").to_crs(cole.crs).geometry.union_all()
        _xs, _ys = cole.geometry.x.to_numpy(), cole.geometry.y.to_numpy()
        _eu, _ed = _cxy2(_ur, _xs, _ys), _cxy2(_dc, _xs, _ys)
        _urb = [int(sum(1 for f, u in zip(fr, _eu) if f == z and u)) for z in ("norte", "centro", "sur")]
        _fdc = [int(sum(1 for f, d_ in zip(fr, _ed) if f == z and not d_)) for z in ("norte", "centro", "sur")]
        a.cierto(vb.get("urbana") == _urb and vb.get("fuera_dc") == _fdc,
                 "visto: Bogotá, por franja, las sedes urbanas y las de fuera del Distrito",
                 f"urbanas {_urb} · fuera {_fdc}")
        a.igual(_ur.bounds[1] - (cj[1] + 2 / 3 * (cj[3] - cj[1])), vb.get("margen_urbano_m"),
                "visto: Bogotá, a cuántos metros del corte acaba el perímetro urbano", 1e-6)
        # R2 · T2.3 (ronda 5): «cabe entero en ese tercio», con shapely: el
        # rectángulo del tercio norte de la caja cubre el perímetro urbano.
        from shapely.geometry import box as _box5
        _cubre = bool(_box5(cj[0], cj[1] + 2 / 3 * (cj[3] - cj[1]), cj[2], cj[3]).covers(_ur))
        a.cierto(vb.get("urbano_en_tercio_norte") is _cubre,
                 "visto: Bogotá, el perímetro urbano cabe entero en el tercio norte de la caja",
                 f"R {vb.get('urbano_en_tercio_norte')} · shapely {_cubre}")
    else:
        a.cierto(False, "visto: Bogotá, las sedes por franja", "falta el dato o el mapa")


    # =================================================================
    a.titulo("11c · Las gráficas y los mapas de R2 · T2.2")
    # =================================================================
    # Lo que T2.2 añadió a los mapas, rehecho aquí por otra vía. Cada bloque
    # empieza comprobando que su campo está: el arnés los quita a propósito.
    from shapely.geometry import Polygon, Point, box

    def _descuantiza(g, plano):
        """De los enteros de un mapa a las unidades de su dato (inversa de geo_qxy)."""
        cj = g["caja"]
        rx, ry = cj[2] - cj[0], cj[3] - cj[1]
        r = max(rx, ry)
        ox, oy = cj[0] + rx / 2 - r / 2, cj[1] + ry / 2 - r / 2
        v = np.asarray(plano, float)
        return np.column_stack([v[0::2] / g["q"] * r + ox, v[1::2] / g["q"] * r + oy])

    # --- Las celdas de Voronoi de las bombas de Snow -----------------------
    ms = M["snow"]
    celdas = ms.get("celdas")
    if isinstance(celdas, list) and len(celdas) == s["n_bombas"] and all(len(c) >= 6 for c in celdas):
        mu = sn[sn.tipo == "muerte"][["x", "y"]].to_numpy()
        bo = sn[sn.tipo == "bomba"][["x", "y"]].to_numpy()
        # La bomba más próxima a cada muerte, por distancia, sin mirar el mapa.
        cerca = np.argmin(np.hypot(mu[:, None, 0] - bo[None, :, 0], mu[:, None, 1] - bo[None, :, 1]), axis=1)
        pols = [Polygon(_descuantiza(ms, c)) for c in celdas]
        tol = 2 * max(ms["caja"][2] - ms["caja"][0], ms["caja"][3] - ms["caja"][1]) / ms["q"]
        a.cierto(all(pp.is_valid for pp in pols), "Snow: las trece celdas son polígonos válidos")
        a.cierto(all(pols[k].distance(Point(*bo[k])) == 0 for k in range(len(bo))),
                 "Snow: cada bomba cae dentro de su celda")
        fuera = sum(pols[c].distance(Point(*m_)) > tol for c, m_ in zip(cerca, mu))
        a.igual(fuera, 0, "Snow: cada muerte cae en la celda de su bomba más próxima")
        # Y que de verdad sea SU celda y no una mayor que la contenga: en la
        # celda de otra bomba no cae, salvo las que rozan una frontera.
        ajenas = sum(any(pols[k].distance(Point(*m_)) == 0 and pols[k].exterior.distance(Point(*m_)) > tol
                         for k in range(len(pols)) if k != c) for c, m_ in zip(cerca, mu))
        a.igual(ajenas, 0, "Snow: ninguna muerte cae además dentro de la celda de otra bomba")
        marco = box(*ms["caja"])
        a.igual(sum(pp.area for pp in pols), marco.area, "Snow: las celdas reparten el marco del mapa",
                1e-3 * marco.area)
        # Contra el diagrama de Voronoi hecho aquí, celda a celda.
        vor = list(voronoi_diagram(MultiPoint([tuple(b) for b in bo]), envelope=marco).geoms)
        peor = 0.0
        for k in range(len(bo)):
            mia = [v for v in vor if v.contains(Point(*bo[k]))]
            peor = max(peor, mia[0].intersection(marco).symmetric_difference(pols[k]).area if mia else marco.area)
        a.cierto(peor < 1e-3 * marco.area, "Snow: cada celda es la de Voronoi de su bomba",
                 f"peor diferencia {peor:.5f} de {marco.area:.1f}")
    else:
        a.cierto(False, "Snow: el mapa trae una celda por bomba", "falta `celdas` o no son trece")
    a.cierto(ms.get("leyenda") == "", "Snow: el mapa va sin pie de leyenda")

    # --- El Mosa: la escala y el marco ---------------------------------------
    mm = M["meuse"]
    a.cierto(mm.get("marcas_escala") == "log", "Mosa: la rampa del zinc es logarítmica")
    meuse = pd.read_csv(SALIDAS / "cap1_meuse.csv")
    xm, ym = meuse.x.to_numpy(), meuse.y.to_numpy()
    lado = max(xm.max() - xm.min(), ym.max() - ym.min())
    esp = [xm.min() - 0.1 * lado, ym.min() - 0.1 * lado, xm.max() + 0.1 * lado, ym.max() + 0.1 * lado]
    a.cierto(all(abs(u - v) < 1e-6 for u, v in zip(esp, mm["caja"])),
             "Mosa: el marco es la caja de los puntos más un décimo de su lado")
    orillas = mm.get("lineas") or []
    a.igual(len(orillas), 2, "Mosa: el mapa trae las dos orillas del río")
    if len(orillas) == 2 and len(mm["pts"]) == 2 * len(meuse):
        from shapely.geometry import LineString, MultiLineString
        rio = MultiLineString([LineString(_descuantiza(mm, l)) for l in orillas])
        d_rio = np.array([rio.distance(Point(x_, y_)) for x_, y_ in zip(xm, ym)])
        # El río dibujado tiene que ser el del dato: la distancia a sus
        # orillas ordena los puntos como la `dist` de meuse.
        a.cierto(float(np.corrcoef(d_rio, meuse.dist.to_numpy())[0, 1]) > 0.95,
                 "Mosa: la distancia a las orillas dibujadas es la del dato",
                 f"r = {np.corrcoef(d_rio, meuse.dist.to_numpy())[0, 1]:.4f}")
        a.cierto(float(np.corrcoef(np.log(meuse.zinc.to_numpy()), d_rio)[0, 1]) < -0.5,
                 "Mosa: el zinc baja al alejarse de las orillas dibujadas")
        xy_m = _descuantiza(mm, mm["pts"])
        a.cierto(bool(np.all(np.abs(np.round(xy_m[:, 0]) - xm) <= 1) and np.all(np.abs(np.round(xy_m[:, 1]) - ym) <= 1)),
                 "Mosa: las coordenadas de la tabla de respaldo, al metro")

    # --- La ventana del acercamiento del módulo 7 ----------------------------
    mg = M["agregacion"]
    zm = mg.get("zoom")
    if isinstance(zm, dict) and len(zm.get("caja", [])) == 4:
        celdas_r = [_descuantiza(mg, mg["lineas"][k - 1]) for k in mg["lineas_resaltadas"]]
        todo = np.vstack(celdas_r)
        todas = np.vstack([_descuantiza(mg, l) for l in mg["lineas"]])
        px = (todas[:, 0].max() - todas[:, 0].min()) / 10
        py = (todas[:, 1].max() - todas[:, 1].min()) / 10
        esp = [max(mg["caja"][0], todo[:, 0].min() - px), max(mg["caja"][1], todo[:, 1].min() - py),
               min(mg["caja"][2], todo[:, 0].max() + px), min(mg["caja"][3], todo[:, 1].max() + py)]
        tol = 3 * max(mg["caja"][2] - mg["caja"][0], mg["caja"][3] - mg["caja"][1]) / mg["q"]
        a.cierto(all(abs(u - v) < tol for u, v in zip(esp, zm["caja"])),
                 "agregación: la ventana es la caja de las celdas del caso más una celda por lado",
                 f"{[round(v) for v in zm['caja']]}")
        dentro = sum(zm["caja"][0] < l[:, 0].mean() < zm["caja"][2] and zm["caja"][1] < l[:, 1].mean() < zm["caja"][3]
                     for l in (_descuantiza(mg, l)[:-1] for l in mg["lineas"]))
        a.igual(dentro, zm["n_celdas"], "agregación: las celdas que se ven en el acercamiento")
        a.igual(zm["columnas"] * zm["filas"], zm["n_celdas"], "agregación: y son columnas por filas")
    else:
        a.cierto(False, "agregación: el mapa trae la ventana del acercamiento", "falta `zoom`")

    # --- R2 · T2.3: los bordes de Bogotá y la caja de los pinos -----------------
    cpu, mbg = D["colombia"]["puntual"], M["bogota"]
    bx = cole.total_bounds
    a_caja = float((bx[2] - bx[0]) * (bx[3] - bx[1]) / 1e6)
    a.igual(a_caja, cpu.get("area_caja_km2"), "Bogotá: el área del rectángulo de las sedes (km²)", 1e-6)
    a.igual(len(cole) / a_caja, cpu.get("lambda_caja"), "Bogotá: la intensidad con ese rectángulo", 1e-8)
    v_dc_ = gpd.read_file(PROCESADO / "bogota_ventana_dc.gpkg").to_crs(cole.crs)
    v_ur_ = gpd.read_file(PROCESADO / "bogota_ventana_urbana.gpkg").to_crs(cole.crs)
    dc_u, ur_u = v_dc_.geometry.union_all(), v_ur_.geometry.union_all()
    a.igual(100 * (1 - box(*bx).intersection(dc_u).area / 1e6 / a_caja), cpu.get("pct_caja_fuera_dc"),
            "Bogotá: la parte del rectángulo que queda fuera del Distrito", 1e-6)
    bordes = mbg.get("bordes")
    if isinstance(bordes, dict) and all(bordes.get(k) for k in ("urbano", "distrito", "caja")):
        from shapely.ops import unary_union as _une
        def _pol(anillos):
            return _une([Polygon(_descuantiza(mbg, r_)).buffer(0) for r_ in anillos if len(r_) >= 8])
        for clave, real in (("urbano", ur_u), ("distrito", dc_u)):
            dib = _pol(bordes[clave])
            a.cierto(dib.symmetric_difference(real).area < 0.04 * real.area,
                     f"Bogotá: el borde «{clave}» dibujado es el de su ventana, simplificado",
                     f"{100 * dib.symmetric_difference(real).area / real.area:.2f} % de diferencia")
        # Vértice a vértice y no por área: un solo vértice corrido deja casi
        # la misma superficie.
        rc = _descuantiza(mbg, bordes["caja"][0])
        tol_c = 2 * max(mbg["caja"][2] - mbg["caja"][0], mbg["caja"][3] - mbg["caja"][1]) / mbg["q"]
        a.cierto(bool(np.all((np.abs(rc[:, 0] - bx[0]) < tol_c) | (np.abs(rc[:, 0] - bx[2]) < tol_c))
                      and np.all((np.abs(rc[:, 1] - bx[1]) < tol_c) | (np.abs(rc[:, 1] - bx[3]) < tol_c))
                      and abs(Polygon(rc).area - box(*bx).area) < 0.002 * box(*bx).area),
                 "Bogotá: el rectángulo dibujado es el que ciñe a las sedes")
    else:
        a.cierto(False, "Bogotá: el mapa trae los tres bordes", "falta `bordes` o alguno de los tres")
    # Lo que la lectura del mapa dice de cada sede: en qué borde cae. Se
    # rehace con shapely, punto a punto contra los dos polígonos, y no con las
    # columnas `en_urbana`/`en_ventana_dc` del dato, que son lo que R leyó.
    dentro_ = mbg.get("dentro")
    if isinstance(dentro_, list) and len(dentro_) == len(cole):
        from shapely import contains_xy as _cxy
        xs_, ys_ = cole.geometry.x.to_numpy(), cole.geometry.y.to_numpy()
        rehecho = _cxy(ur_u, xs_, ys_).astype(int) + _cxy(dc_u, xs_, ys_).astype(int)
        malas = int(np.sum(rehecho != np.asarray(dentro_)))
        a.cierto(malas == 0, "Bogotá: el borde en que cae cada sede, según la lectura del mapa",
                 f"{malas} de {len(cole)} sedes cambian de borde")
    else:
        a.cierto(False, "Bogotá: el mapa trae el borde de cada sede", "falta `dentro` o no tiene una entrada por sede")
    ppp_ = pd.read_csv(SALIDAS / "cap1_ppp.csv")
    pin_ = ppp_[ppp_.patron == "japanesepines"]
    a_pin = float((pin_.x.max() - pin_.x.min()) * (pin_.y.max() - pin_.y.min()))
    pjc = D["puntual_canonico"]["japanesepines"]
    a.igual(a_pin, pjc.get("area_caja"), "pinos: el área del rectángulo que ciñe a los puntos", 1e-9)
    a.igual(len(pin_) / a_pin, pjc.get("lambda_caja"), "pinos: la intensidad con ese rectángulo", 1e-8)

    # --- IDEAM: el contorno, las franjas de altitud y los pliegues -----------
    mi_ = M["ideam"]
    cont = mi_.get("lineas") or []
    a.cierto(len(cont) >= 1, "IDEAM: el mapa trae el contorno del país")
    if cont:
        from shapely.ops import unary_union
        pais_d = unary_union([Polygon(_descuantiza(mi_, l)) for l in cont if len(l) >= 8])
        real = dep.to_crs(est.crs).geometry.union_all()
        a.cierto(pais_d.symmetric_difference(real).area < 0.03 * real.area,
                 "IDEAM: el contorno dibujado es el del país, simplificado",
                 f"{100 * pais_d.symmetric_difference(real).area / real.area:.2f} % de diferencia")
    pa = D["visto"]["ideam"].get("por_altitud")
    if isinstance(pa, list) and pa:
        alt, tt_ = est.altitud_m.to_numpy(), est.t_media_anual.to_numpy()
        ok = sum(f["n"] for f in pa) == len(est)
        for f in pa:
            en = (alt >= f["desde"]) & (alt < f["hasta"])
            ok = ok and int(en.sum()) == f["n"] and f["hasta"] - f["desde"] == 500 \
                and abs(float(tt_[en].mean()) - f["t_media"]) < 1e-8
        a.cierto(ok, "IDEAM: las estaciones por franja de altitud y su temperatura media",
                 f"{len(pa)} franjas")
    else:
        a.cierto(False, "IDEAM: las estaciones por franja de altitud y su temperatura media", "falta")
    pl_a, pl_b = mi_.get("pliegue_aleatorio"), mi_.get("pliegue_bloques")
    if isinstance(pl_a, list) and isinstance(pl_b, list) and len(pl_a) == len(pl_b) == len(est):
        # LA VALIDACIÓN CRUZADA, REHECHA con los pliegues publicados: la media
        # de las k vecinas más próximas del entrenamiento, y el RMSE agrupando
        # los errores de todos los pliegues. Hasta T2.2 el auditor solo podía
        # comprobar la aritmética entre las cifras; ahora las reproduce.
        xy_e = np.column_stack([est.geometry.x.to_numpy(), est.geometry.y.to_numpy()])
        z_e = est.t_media_anual.to_numpy()
        dd = np.hypot(xy_e[:, None, 0] - xy_e[None, :, 0], xy_e[:, None, 1] - xy_e[None, :, 1])

        def _rmse(pl):
            pl = np.asarray(pl)
            err = []
            for f in sorted(set(pl.tolist())):
                te, tr = np.where(pl == f)[0], np.where(pl != f)[0]
                for i in te:
                    o = tr[np.argsort(dd[i, tr], kind="stable")[:cv["k_vecinos"]]]
                    err.append(z_e[i] - z_e[o].mean())
            return float(np.sqrt(np.mean(np.square(err))))

        a.igual(_rmse(pl_a), cv["rmse_aleatoria"], "CV: el RMSE aleatorio, rehecho con sus pliegues", 1e-6)
        a.igual(_rmse(pl_b), cv["rmse_bloques"], "CV: el RMSE por bloques, rehecho con sus pliegues", 1e-6)
        a.cierto(sorted(np.bincount(pl_b)[1:].tolist()) == cv["tam_pliegues"], "CV: los tamaños de los bloques")
        a.cierto(set(pl_a) == set(pl_b) == set(range(1, cv["n_pliegues"] + 1)), "CV: los dos repartos usan todos los pliegues")
        vec = np.argmin(dd + np.diag(np.full(len(est), np.inf)), axis=1)
        a.igual(int(np.sum(np.asarray(pl_a) == np.asarray(pl_a)[vec])), cv.get("vecina_en_su_pliegue_aleatoria"),
                "CV: estaciones con su vecina más próxima en su pliegue, al azar")
        a.igual(int(np.sum(np.asarray(pl_b) == np.asarray(pl_b)[vec])), cv.get("vecina_en_su_pliegue_bloques"),
                "CV: y por bloques")
    else:
        a.cierto(False, "CV: el mapa trae los dos repartos, estación a estación", "faltan los pliegues")

    # --- Los campos y las realizaciones: la escala y las clases --------------
    for lista, etq in ((M["campos"], "campo"), (M["realizaciones"], "realización")):
        rangos = set()
        for i, g in enumerate(lista):
            q = f"{etq} {i}"
            co = g["cortes"]
            a.igual(g.get("centro"), 0, f"{q}: la escala está centrada en 0")
            a.cierto(abs(g["rango"][0] + g["rango"][1]) < 1e-7
                     and all(abs(co[k] + co[-1 - k]) < 1e-7 for k in range(len(co))),
                     f"{q}: el recorrido y los cortes son simétricos")
            a.cierto(abs(co[0] - g["rango"][0]) < 1e-7 and abs(co[-1] - g["rango"][1]) < 1e-7
                     and np.allclose(np.diff(co), np.diff(co)[0], atol=1e-7),
                     f"{q}: siete clases de anchura igual sobre el recorrido")
            rangos.add(tuple(g["rango"]))
            lo, hi = g["rango"]
            z = np.asarray(g["zq"], float) / g["zqmax"] * (hi - lo) + lo
            tam = g.get("tam")
            if isinstance(tam, list) and len(tam) == len(co) - 1:
                # Las celdas de cada clase, rehechas desde el campo dibujado. La
                # cuantización mueve cada valor hasta media milésima del
                # recorrido: una celda pegada a un corte puede cambiar de clase.
                mio = np.histogram(z, bins=co)[0]
                cerca_ = sum(int(np.sum(np.abs(z - c) < (hi - lo) / g["zqmax"])) for c in co[1:-1])
                a.igual(sum(tam), g["nx"] * g["ny"], f"{q}: las clases reparten todas las celdas")
                a.cierto(int(np.abs(mio - np.asarray(tam)).sum()) <= 2 * cerca_,
                         f"{q}: las celdas de cada clase, rehechas desde el mapa",
                         f"{mio.tolist()} frente a {tam}")
            else:
                a.cierto(False, f"{q}: trae cuántas celdas caen en cada clase", "falta `tam`")
            a.cierto(max(abs(lo), abs(hi)) >= float(np.abs(z).max()) - 1e-9, f"{q}: el recorrido cubre el campo")
        a.igual(len(rangos), 1, f"{etq}: toda la familia comparte escala")
    for lista, etq in ((M["campos"], "campo"), (M["realizaciones"], "realización")):
        tope = max(float(np.abs(np.asarray(g["zq"], float) / g["zqmax"] * (g["rango"][1] - g["rango"][0])
                                + g["rango"][0]).max()) for g in lista)
        a.igual(tope, lista[0]["rango"][1], f"{etq}: el recorrido común es el mayor valor absoluto de la familia", 1e-6)
    inf_ = D["inferencia"]
    for g in M["campos"]:
        a.igual(g["nx"], inf_["k"], f"campo phi={g['phi']}: va en la retícula de la simulación")
        lo, hi = g["rango"]
        z = np.asarray(g["zq"], float) / g["zqmax"] * (hi - lo) + lo
        a.igual(float(z.mean()), g.get("media_espacial"), f"campo phi={g['phi']}: su media, rehecha desde el mapa", 2e-3)
        # Y su I de Moran, con vecindad de reina y pesos por filas, rehecho
        # desde el campo dibujado.
        k_ = g["nx"]
        zc = z.reshape(k_, k_) - z.mean()
        num = den = 0.0
        for f_ in range(k_):
            for c_ in range(k_):
                vs = [zc[f_ + u, c_ + v] for u in (-1, 0, 1) for v in (-1, 0, 1)
                      if (u or v) and 0 <= f_ + u < k_ and 0 <= c_ + v < k_]
                num += zc[f_, c_] * sum(vs) / len(vs)
        den = float((zc ** 2).sum())
        a.igual(num / den, g["moran"], f"campo phi={g['phi']}: su I de Moran, rehecho desde el mapa", 5e-3)
    c4 = [g for g in M["campos"] if g["phi"] == inf_["cien_ic"]["phi"]]
    a.cierto(len(c4) == 1 and abs(c4[0].get("media_espacial", 9) - inf_["cien_ic"]["media"][0]) < 1e-7,
             "campo: el del alcance destacado es la réplica 1 de la simulación",
             f"{c4[0].get('media_espacial') if c4 else '—'} frente a {inf_['cien_ic']['media'][0]}")

    # =================================================================
    a.titulo("12 · Formato, codificación y redondeo")
    # =================================================================
    for nombre, ruta in (("datos", ruta_d), ("mapas", ruta_m), ("soluciones", ruta_s)):
        txt = ruta.read_text(encoding="utf-8")
        a.cierto("<c3>" not in txt and "<c2>" not in txt,
                 f"{nombre}: ningún byte crudo <xx>")
        a.cierto("�" not in txt, f"{nombre}: ningún carácter de reemplazo")
        a.cierto("NaN" not in txt and "Infinity" not in txt,
                 f"{nombre}: ni NaN ni Infinity")
    a.cierto("Deserción" in json.dumps(D, ensure_ascii=False) or
             "deserción" in json.dumps(D, ensure_ascii=False),
             "las tildes llegan enteras al JSON de datos")
    a.cierto("°C" in json.dumps(D, ensure_ascii=False),
             "y los símbolos también")

    # La regla de T0.5: el JSON se guarda con HOLGURA por debajo de lo que
    # se publica. Con 10 decimales, publicar 5 no puede doblar el redondeo.
    for etq, obj in (("datos", D), ("soluciones", S)):
        peor = [(r, n) for r, n in decimales(obj) if n > 10]
        a.cierto(not peor, f"{etq}: ningún flotante pasa de 10 decimales",
                 "" if not peor else f"{len(peor)}, p. ej. {peor[:3]}")

    a.igual(D["meta"]["semilla"], 2026, "la semilla declarada")
    a.igual(D["meta"]["capitulo"], 1, "el capítulo declarado")
    a.cierto(D["meta"]["anclas_verificadas"] >= 15,
             "el generador verificó sus anclas contra la literatura",
             str(D["meta"]["anclas_verificadas"]))
    a.igual(S["meta"]["capitulo"], 1, "las soluciones son del capítulo 1")
    a.igual(S["meta"]["n_ejercicios"], 4, "y son cuatro ejercicios")
    a.igual(S["meta"]["semilla"], D["meta"]["semilla"],
            "los dos guiones comparten semilla")

    return a.cierre()


if __name__ == "__main__":
    sys.exit(main())
