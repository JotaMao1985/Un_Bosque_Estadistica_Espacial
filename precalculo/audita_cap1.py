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
    for e in ne["exacto_campo"]:
        a.igual(100 * e["n_eff"] / D["inferencia"]["n"], e["pct"],
                f"campo phi={e['phi']}: porcentaje de información", 1e-6)
    a.igual(ne["desercion_municipal"], ir["n_eff"], "el n_eff real coincide con el suyo")
    a.igual(ne["desercion_pct"], ir["pct_informacion"], "y su porcentaje también")

    # --- Los dos rho del titular (T2.1) -------------------------------
    #
    # El módulo publica DOS rho y su discrepancia, así que hay que verificar
    # los dos por caminos distintos: el implícito es álgebra —se despeja de
    # n_eff y tiene que devolverlo— y el estimado es una medición sobre el
    # mapa, que se rehace aquí desde el GeoPackage original con geopandas y
    # libpysal, sin pasar por R.
    from libpysal.weights import DistanceBand, W
    rt = ne["rho_del_titular"]
    a.igual(rt["n"], ir["n_municipios"], "el rho del titular habla de los mismos municipios")
    a.igual(rt["n_eff_publicado"], ir["n_eff"], "y del mismo n_eff")
    nr = rt["n"]
    # 1 · El implícito es un despeje, así que la ida y la vuelta cierran.
    #
    # LAS TOLERANCIAS DE ESTE BLOQUE ESTÁN MEDIDAS, NO ESTIMADAS, y son más
    # anchas de lo que uno escribiría a ojo. El JSON redondea a diez
    # decimales, y ese error de 5e-11 se AMPLIFICA al pasar por un cociente
    # de rho pequeños o por la fórmula del n_eff:
    #
    #     despeje del implícito   4.3e-11   ->  1e-9   (23x de margen)
    #     razón entre los dos rho 1.4e-07   ->  1e-5   (72x)
    #     n_eff con el estimado   4.0e-06   ->  1e-3   (247x)
    #     vuelta al n_eff titular 1.8e-07   ->  1e-5   (56x)
    #
    # El rho estimado vale 0.0021, así que un redondeo en la undécima cifra
    # es un error relativo de 2e-8 — y multiplicado por 331 de n_eff, cuatro
    # millonésimas. Escribir 1e-6 aquí habría puesto rojo un capítulo
    # correcto, que es la forma más rápida de enseñar a ignorar el informe.
    a.igual((nr / rt["n_eff_publicado"] - 1) / (nr - 1), rt["implicito"],
            "el rho implícito es el despeje de n_eff", 1e-9)
    a.igual(nr / (1 + (nr - 1) * rt["implicito"]), rt["n_eff_publicado"],
            "y devuelve el n_eff del titular", 1e-5)
    a.cierto(rt["implicito"] > rt["estimado"],
             "el rho que la equicorrelación necesita supera al medido",
             f"{rt['implicito']:.7f} > {rt['estimado']:.7f}")
    a.igual(rt["implicito"] / rt["estimado"], rt["razon_rho"],
            "la razón entre los dos rho", 1e-5)
    a.igual(nr / (1 + (nr - 1) * rt["estimado"]), rt["n_eff_con_estimado"],
            "el n_eff que daría el rho medido", 1e-3)
    a.igual(rt["n_eff_con_estimado"] / rt["n_eff_publicado"], rt["razon_n_eff"],
            "y la razón de información entre los dos", 1e-7)

    # 2 · El estimado, rehecho desde el original.
    #
    # Se lee el GeoPackage y la llave, no el CSV del generador: independencia
    # TOTAL. Los puntos son `representative_point()` contra el
    # `st_point_on_surface()` de sf — el mismo concepto en las dos
    # bibliotecas—, y las bandas se construyen restando dos DistanceBand.
    #
    # LA CONVENCIÓN, que aquí no se puede esquivar. `spdep::moran.test` con
    # `zero.policy = TRUE` toma n = unidades CON vecinos y `esda.Moran` toma
    # n = todas: es la discrepancia `moran_islas` que el módulo 7 declara, y
    # en la banda de 0 a 25 km son 156 islas de 1 121, así que cambia la I en
    # la SEGUNDA cifra, no en la cuarta. Las dos convenciones se convierten
    # exactamente una en otra, y por eso el capítulo publica `islas` por
    # banda: sin ese entero, esta comprobación sería imposible y habría que
    # declararla saltada.
    gm = gpd.read_file(PROCESADO / "colombia_adm2.gpkg")
    llave = pd.read_csv(PROCESADO / "municipios_llave.csv", dtype=str)
    gm = gm.merge(llave[["shapeID", "desercion"]], on="shapeID", how="left")
    gm["desercion"] = pd.to_numeric(gm["desercion"], errors="coerce")
    gm = gm[gm["desercion"].notna()].reset_index(drop=True)
    a.igual(len(gm), rt["n"], "los municipios con dato, contados por geopandas")
    ptos = gm.geometry.representative_point()
    xy_m = np.c_[ptos.x.values, ptos.y.values]
    y_m = gm["desercion"].to_numpy()
    a.igual(len(rt["bandas"]), rt["n_bandas"], "el correlograma trae las bandas que declara")
    suma_pares = suma_I = 0.0
    for b in rt["bandas"]:
        etq = f"rho {b['d1']}-{b['d2']} km"
        vec = DistanceBand(xy_m, threshold=b["d2"] * 1000, binary=True,
                           silence_warnings=True).neighbors
        if b["d1"] > 0:
            dentro = DistanceBand(xy_m, threshold=b["d1"] * 1000, binary=True,
                                  silence_warnings=True).neighbors
            vec = {k: sorted(set(vec[k]) - set(dentro[k])) for k in vec}
        a.igual(sum(len(v) for v in vec.values()) / 2, b["pares"], f"{etq}: los pares")
        a.igual(sum(1 for v in vec.values() if not v), b["islas"], f"{etq}: las islas")
        w = W(vec, silence_warnings=True)
        w.transform = "r"
        # 1e-9: la I publicada viene redondeada a diez decimales, y la
        # conversión de convención no añade error propio (medido: 5e-11).
        a.igual(Moran(y_m, w, permutations=0).I, b["I"] * nr / (nr - b["islas"]),
                f"{etq}: la I de Moran, con la convención de esda", 1e-9)
        suma_pares += b["pares"]
        suma_I += b["I"] * b["pares"]
    a.igual(suma_pares, rt["pares_totales"], "los pares del correlograma suman los declarados")
    a.igual(suma_I / suma_pares, rt["estimado"],
            "el rho estimado es la media de las I ponderada por pares", 1e-9)
    a.igual(rt["bandas"][0]["I"], rt["I_primera_banda"],
            "la I de la primera banda que publica la prosa")
    a.igual(sum(b["pares"] for b in rt["bandas"] if b["I"] < 0), rt["pares_lejanos"],
            "los pares con correlación negativa que cita la prosa")
    a.cierto(rt["bandas"][0]["I"] > 10 * rt["estimado"],
             "entre vecinos la correlación supera su promedio",
             f"{rt['bandas'][0]['I']:.5f} contra {rt['estimado']:.7f}")

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
        rel = [abs(fila["variograma"][k] - vg["teorico"][k]) / vg["teorico"][k]
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

    e3 = S["e3"]["solucion"]
    a.igual(e3["n"], D["colombia"]["geo"]["n"], "E3: las mismas estaciones")
    a.igual(e3["n"] / (1 + (e3["n"] - 1) * e3["rho_medio"]), e3["n_eff"],
            "E3: el n efectivo por la fórmula", 1e-7)
    a.igual(1 / e3["rho_medio"], e3["techo"], "E3: el techo es 1/rho", 1e-7)
    a.igual(100 * e3["n_eff"] / e3["n"], e3["pct_informacion"], "E3: el porcentaje", 1e-6)
    a.cierto(e3["n_eff"] < e3["techo"], "E3: el n efectivo respeta su techo")
    a.cierto(e3["objetivo_25_alcanzable"] and not e3["objetivo_50_alcanzable"],
             "E3: 25 estaciones independientes se alcanzan y 50 no")
    a.cierto(not e3["objetivo_100_alcanzable"], "E3:   y 100 tampoco")
    a.cierto(25 < e3["techo"] < 50, "E3: el techo separa los dos objetivos",
             f"{e3['techo']:.5f}")
    a.igual(len(e3["moran_por_banda"]), len(e3["bandas_km"]) - 1,
            "E3: una I por banda")

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
    a.cierto(kb_tot <= 120, "y el conjunto de mapas también", f"{kb_tot:.1f} KB")

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
