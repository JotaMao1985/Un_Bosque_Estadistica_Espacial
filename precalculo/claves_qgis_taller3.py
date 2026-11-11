#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
claves_qgis_taller3.py — recorre el Taller 3 ENTERO dentro de QGIS, sin ventana

Estadística Espacial 2026-II (20929) · Corte III. Ver PLAN_Taller_3_SIG.md.

Hace con la caja de procesos de QGIS exactamente lo que el enunciado le
pide al estudiante, para las 16 localidades y todos los valores que puede
traer una variante, y escribe las cifras de control en un JSON.

POR QUÉ EXISTE. Las cifras de control de este taller no son las de R: son
las que da QGIS, con sus convenciones (la caja envolvente del vecino más
próximo, el mapa de calor sin corrección de borde). Para publicar un
enunciado que diga «tu cifra tiene que ser esta» hay que haberla sacado
de QGIS, y de más de una plataforma.

EL JSON NO SE VERSIONA: son las respuestas. Va a `precalculo/cache/`, que
está fuera del repositorio.

Uso (con el Python que trae QGIS, o dentro de la imagen de Docker):
    python3 claves_qgis_taller3.py <carpeta de datos> <carpeta del complemento> <salida.json>
"""
import json
import os
import platform
import sys
import tempfile

DATOS, COMPLEMENTO, SALIDA = sys.argv[1], sys.argv[2], sys.argv[3]
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from qgis.core import (QgsApplication, QgsClassificationJenks, QgsClassificationQuantile,
                       QgsRasterLayer, QgsVectorLayer, Qgis)

app = QgsApplication([], False)
app.initQgis()
for ruta in (os.path.join(QgsApplication.prefixPath(), "share", "qgis", "python", "plugins"),
             os.path.join(QgsApplication.pkgDataPath(), "python", "plugins"),
             "/usr/share/qgis/python/plugins"):
    if os.path.isdir(ruta) and ruta not in sys.path:
        sys.path.append(ruta)
sys.path.insert(0, os.path.dirname(os.path.abspath(COMPLEMENTO)))

import processing
from processing.core.Processing import Processing

Processing.initialize()
from taller3_espacial.proveedor import ProveedorTaller3

prov = ProveedorTaller3()
QgsApplication.processingRegistry().addProvider(prov)

import numpy as np

TMP = tempfile.mkdtemp(prefix="t3_")
NX = (3, 4, 5)
R_GF = (100, 150, 200)
R_KL = (200, 300, 400)
RADIOS = (600, 800, 1000)
N_MIN = 35                       # una localidad entra al sorteo con 35 sedes o más


def run(alg, **p):
    return processing.run(alg, p)


def capa(ruta, nombre="c"):
    c = QgsVectorLayer(ruta, nombre, "ogr")
    assert c.isValid(), ruta
    return c


gpkg = os.path.join(DATOS, "taller3.gpkg")
loc = capa(gpkg + "|layername=localidades")
urb = capa(gpkg + "|layername=perimetro_urbano")
cruda = capa(os.path.join(DATOS, "taller3_sedes_3857.geojson"))
assert cruda.crs().authid() == "EPSG:3857" and loc.crs().authid() == "EPSG:9377"

res = {"plataforma": {"qgis": Qgis.QGIS_VERSION, "numpy": np.__version__,
                      "sistema": platform.platform()}}

# --- T1 · reproyectar, y lo que cuesta no hacerlo -----------------------
sedes = run("native:reprojectlayer", INPUT=cruda, TARGET_CRS="EPSG:9377",
            OUTPUT=os.path.join(TMP, "sedes.gpkg"))["OUTPUT"]
sedes = capa(sedes)
loc3857 = capa(run("native:reprojectlayer", INPUT=loc, TARGET_CRS="EPSG:3857",
                   OUTPUT=os.path.join(TMP, "loc3857.gpkg"))["OUTPUT"])
a9377 = {f["localidad"]: f.geometry().area() / 1e6 for f in loc.getFeatures()}
a3857 = {f["localidad"]: f.geometry().area() / 1e6 for f in loc3857.getFeatures()}
reetiq = capa(run("native:assignprojection", INPUT=cruda, CRS="EPSG:9377",
                  OUTPUT=os.path.join(TMP, "reetiq.gpkg"))["OUTPUT"])
mal = capa(run("native:countpointsinpolygon", POLYGONS=loc, POINTS=reetiq,
               OUTPUT=os.path.join(TMP, "mal.gpkg"))["OUTPUT"])
res["t1"] = {"reetiquetadas_dentro": int(sum(f["NUMPOINTS"] for f in mal.getFeatures()))}

# --- T2 · contar, normalizar, clasificar, y cambiar las unidades --------
cont = capa(run("native:countpointsinpolygon", POLYGONS=loc, POINTS=sedes,
                OUTPUT=os.path.join(TMP, "cont.gpkg"))["OUTPUT"])
conteo = {f["localidad"]: int(f["NUMPOINTS"]) for f in cont.getFeatures()}
dens = capa(run("native:fieldcalculator", INPUT=cont, FIELD_NAME="densidad", FIELD_TYPE=0,
                FIELD_LENGTH=20, FIELD_PRECISION=10, FORMULA='"NUMPOINTS" / (area($geometry) / 1000000)',
                OUTPUT=os.path.join(TMP, "dens.gpkg"))["OUTPUT"])
densidad = {f["localidad"]: float(f["densidad"]) for f in dens.getFeatures()}


def clases(metodo, campo):
    rangos = metodo.classes(dens, campo, 5)
    cortes = [r.upperBound() for r in rangos]
    de = {}
    for f in dens.getFeatures():
        v = float(f[campo])
        de[f["localidad"]] = next(i + 1 for i, c in enumerate(cortes) if v <= c or i == len(cortes) - 1)
    return cortes, de


cortes_q, clase_q = clases(QgsClassificationQuantile(), "densidad")
cortes_j, clase_j = clases(QgsClassificationJenks(), "densidad")
orden_n = sorted(conteo, key=lambda k: -conteo[k])
orden_d = sorted(densidad, key=lambda k: -densidad[k])
res["t2"] = {"sedes_en_alguna_localidad": sum(conteo.values()),
             "cortes_cuantiles": cortes_q, "cortes_jenks": cortes_j,
             "cambian_de_clase": sorted(k for k in clase_q if clase_q[k] != clase_j[k])}

rejillas = {}
for lado in (2000, 4000):
    g = run("native:creategrid", TYPE=2, EXTENT=urb.extent(), HSPACING=lado, VSPACING=lado,
            CRS="EPSG:9377", OUTPUT=os.path.join(TMP, "g%d.gpkg" % lado))["OUTPUT"]
    gc = capa(run("native:countpointsinpolygon", POLYGONS=capa(g), POINTS=sedes,
                  OUTPUT=os.path.join(TMP, "gc%d.gpkg" % lado))["OUTPUT"])
    v = np.array([f["NUMPOINTS"] for f in gc.getFeatures()], dtype=float)
    ocupadas = v[v > 0]
    rejillas[str(lado)] = {"celdas": int(len(v)), "ocupadas": int(len(ocupadas)),
                           "maximo": int(v.max()), "sedes_contadas": int(v.sum()),
                           "media_ocupadas": float(ocupadas.mean())}
res["t2"]["rejillas"] = rejillas

# --- Por localidad: T3 y T4 ---------------------------------------------
res["localidades"] = {}
for nombre in sorted(conteo):
    L = {"n_sedes": conteo[nombre], "area_km2": a9377[nombre], "area_3857_km2": a3857[nombre],
         "inflacion_pct": 100.0 * (a3857[nombre] / a9377[nombre] - 1.0),
         "densidad": densidad[nombre],
         "puesto_conteo": orden_n.index(nombre) + 1, "puesto_densidad": orden_d.index(nombre) + 1,
         "clase_cuantiles": clase_q[nombre], "clase_jenks": clase_j[nombre],
         "elegible": conteo[nombre] >= N_MIN}
    res["localidades"][nombre] = L
    if not L["elegible"]:
        continue
    filtro = "\"localidad\" = '%s'" % nombre
    mia = capa(run("native:extractbyexpression", INPUT=loc, EXPRESSION=filtro,
                   OUTPUT=os.path.join(TMP, "mia.gpkg"))["OUTPUT"])
    mias = capa(run("native:extractbylocation", INPUT=sedes, PREDICATE=[0], INTERSECT=mia,
                    OUTPUT=os.path.join(TMP, "mias.gpkg"))["OUTPUT"])
    assert mias.featureCount() == conteo[nombre], nombre

    nn = run("native:nearestneighbouranalysis", INPUT=mias,
             OUTPUT_HTML_FILE=os.path.join(TMP, "nn.html"))
    n, a = conteo[nombre], a9377[nombre] * 1e6
    esperada_real = 0.5 / np.sqrt(n / a)
    L["vecino"] = {"observada": nn["OBSERVED_MD"], "esperada_qgis": nn["EXPECTED_MD"],
                   "indice_qgis": nn["NN_INDEX"], "z_qgis": nn["Z_SCORE"],
                   "area_caja_km2": mias.extent().area() / 1e6,
                   "esperada_area_real": float(esperada_real),
                   "indice_area_real": float(nn["OBSERVED_MD"] / esperada_real)}

    L["cuadrantes"] = {}
    for nx in NX:
        r = run("taller3:cuadrantes", PUNTOS=sedes, VENTANA=loc, FILTRO=filtro, NX=nx, NY=nx,
                SALIDA="memory:", INFORME=os.path.join(TMP, "c.html"))
        assert r["N"] == n
        L["cuadrantes"][str(nx)] = {k.lower(): r[k] for k in
                                    ("CELDAS", "CHI2", "GL", "P_DERECHA", "P_BILATERAL", "ESPERADO_MIN")}
    L["gf"] = {}
    for rr in R_GF:
        r = run("taller3:gfj", PUNTOS=sedes, VENTANA=loc, FILTRO=filtro, RMAX=600, PASO=10, LADO=200,
                R_LECTURA=rr, SALIDA="memory:", INFORME=os.path.join(TMP, "g.html"))
        L["gf"][str(rr)] = {"g": r["G_R"], "f": r["F_R"], "poisson": r["TEORICA_R"], "j": r["J_R"],
                            "sitios": r["SITIOS"]}
    L["kl"] = {}
    for rr in R_KL:
        r = run("taller3:ripley", PUNTOS=sedes, VENTANA=loc, FILTRO=filtro, RMAX=1000, PASO=25, NSIM=99,
                SEMILLA=2026, R_LECTURA=rr, SALIDA="memory:", INFORME=os.path.join(TMP, "k.html"))
        L["kl"][str(rr)] = {"k": r["K_R"], "l_menos_r": r["L_MENOS_R"], "banda_inf": r["BANDA_INF"],
                            "banda_sup": r["BANDA_SUP"], "usables": r["USABLES_R"]}
    L["calor"] = {}
    for radio in RADIOS:
        tif = os.path.join(TMP, "calor.tif")
        run("qgis:heatmapkerneldensityestimation", INPUT=mias, RADIUS=radio, PIXEL_SIZE=50,
            KERNEL=0, OUTPUT_VALUE=1, OUTPUT=tif)
        est = run("native:rasterlayerstatistics", INPUT=tif, BAND=1)
        zon = capa(run("native:zonalstatisticsfb", INPUT=mia, INPUT_RASTER=tif, RASTER_BAND=1,
                       COLUMN_PREFIX="z_", STATISTICS=[1], OUTPUT=os.path.join(TMP, "zon.gpkg"))["OUTPUT"])
        dentro = float(next(zon.getFeatures())["z_sum"])
        ras = QgsRasterLayer(tif, "r")
        px = ras.rasterUnitsPerPixelX() * ras.rasterUnitsPerPixelY()
        L["calor"][str(radio)] = {"maximo": est["MAX"], "suma": est["SUM"], "suma_dentro": dentro,
                                  "pixel_m2": px, "masa_total": est["SUM"] * px,
                                  "masa_dentro": dentro * px, "pct_fuera": 100.0 * (1 - dentro / est["SUM"])}
    print("  %-20s n = %3d" % (nombre, n), flush=True)

with open(SALIDA, "w", encoding="utf-8") as f:
    json.dump(res, f, ensure_ascii=False, indent=1, sort_keys=True)
print("escrito:", SALIDA)
app.exitQgis()
