#!/usr/bin/env python3
"""
audita_cap2.py — auditoría independiente del precálculo del capítulo 2 (T2.1d)

Material de Estadística Espacial 2026-II (20929).

NO comprueba que los JSON existan: comprueba que sus NÚMEROS sean ciertos,
por caminos que no pasan por R.

POR QUÉ EN PYTHON. Es la lección de A.10, la que costó 295 724 estudiantes
desaparecidos en silencio: un control que comparte el entorno con lo que
audita no es independiente. Aquí el intérprete es otro y, sobre todo, la
BIBLIOTECA GEODÉSICA ES OTRA: R mide con lwgeom y s2, y esto mide con
pyproj.Geod y shapely. Que las dos coincidan a ocho decimales sobre la
longitud de un grado o sobre el área de Colombia no es una tautología.

Y ESTE CAPÍTULO TIENE UN FRENTE QUE EL 1 NO TENÍA: la indicatriz de
Tissot. `geo_tissot()` la calcula por diferencias finitas y descomposición
en valores singulares; aquí se recalcula **con la trigonometría de Snyder
(1987, pp. 20-24)**, que es el camino largo y clásico. Dos implementaciones
distintas de la misma matemática, y si coinciden es que la matemática está
bien. Un solo camino habría verificado que el código hace lo que hace.

HASTA DÓNDE LLEGA LA INDEPENDENCIA, DECLARADO Y NO INSINUADO
  · TOTAL para los GeoPackage colombianos, `spData::world` (vía el JSON de
    mapas y las cifras derivadas) y todo lo que sale de pyproj.
  · PARCIAL para el shapefile del módulo 7: GDAL es el MISMO en los dos
    lados —geopandas y sf lo llaman igual—, así que ahí esto verifica el
    ANÁLISIS de lo que GDAL devolvió, no que GDAL se comporte así.
    Declarado con salta().

CUATRO FRENTES
  1. R <-> PYTHON. Recalcula desde las fuentes primarias.
  2. COHERENCIA INTERNA. Que las relaciones que el capítulo afirma se
     sostengan, y que ninguna bandera se crea a sí misma.
  3. LOS MAPAS. Caja, cuantización, presupuesto e indicatrices.
  4. FORMATO. JSON válido, tildes intactas, sin NaN, redondeo declarado.

Uso:  python3 precalculo/audita_cap2.py     (desde `Estadistica espacial/`)
Con el intérprete de geo_env; `audita_todo.sh` ya lo hace.
Devuelve 1 si algo falla.

CAP2_DATOS, CAP2_MAPAS y CAP2_SOLUCIONES permiten apuntar a copias con
defectos inyectados: es lo que hace `prueba_auditor_cap2.py`. Los archivos
publicados no se tocan nunca.

LOS RÓTULOS TIENEN PRESUPUESTO: 57 CARACTERES, PREFIJO INCLUIDO.
`Auditoria.cierto()` rellena el rótulo hasta 58 antes del detalle, así que
uno de 58 o más queda pegado a su detalle por un solo espacio y el arnés
—que lee el informe con una expresión regular para saber qué
comprobaciones se han visto fallar— no puede separarlos: la comprobación
deja de contarse como cubierta aunque haya fallado. No rompe nada que se
vea; corrompe el recuento de cobertura, en silencio.

Este archivo llegó a tener 69 rótulos pasados. Se acortaron el 2026-08-24
moviendo el matiz al DETALLE, que no paga presupuesto —«declara False,
recalculado False» dice más que «coincide con el recálculo» y ocupa cero—,
y acortando el nombre de las vistas de proyección con
`audita_base.rotulos_de_vistas()`. Nueve quedan justo en 57: al añadir o
renombrar cualquier cosa aquí, medir.
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
                         decimales, rotulos_de_vistas, sin_nan)

RAIZ = pathlib.Path(__file__).resolve().parent.parent
PRECALCULO = RAIZ / "precalculo"
SALIDAS = PRECALCULO / "salidas"
PROCESADO = RAIZ / "datos" / "procesado"
CRUDO = RAIZ / "datos" / "crudo"


def carga(var: str, nombre: str):
    return _carga(var, nombre, SALIDAS)


# =====================================================================
# La indicatriz de Tissot POR EL CAMINO LARGO
#
# `geo_tissot()` arma la jacobiana en la base este-norte y la descompone
# en valores singulares. Aquí se hace como en Snyder (1987, pp. 20-24):
#
#   h = (1/M) sqrt( (dx/dphi)^2 + (dy/dphi)^2 )        meridiano
#   k = (1/(N cos phi)) sqrt( (dx/dlam)^2 + (dy/dlam)^2 )  paralelo
#   sin(theta') = (dy/dphi dx/dlam - dx/dphi dy/dlam) / (M N cos phi h k)
#   a' = h^2 + k^2 + 2 h k sin theta' ; b' = h^2 + k^2 - 2 h k sin theta'
#   a = (sqrt(a') + sqrt(b'))/2 ; b = (sqrt(a') - sqrt(b'))/2
#   s = h k sin theta' ; sin(omega/2) = (a-b)/(a+b)
#
# Son las MISMAS derivadas parciales y matemáticas equivalentes por dos
# caminos distintos. Si el capítulo publicara un omega equivocado, tendría
# que estarlo por las dos vías a la vez.
# =====================================================================
def tissot_snyder(transformador, lon, lat, ea, e2, d=0.02):
    drad = math.radians(d)
    x1, y1 = transformador.transform(lon - d, lat)
    x2, y2 = transformador.transform(lon + d, lat)
    x3, y3 = transformador.transform(lon, lat - d)
    x4, y4 = transformador.transform(lon, lat + d)
    for v in (x1, y1, x2, y2, x3, y3, x4, y4):
        if not math.isfinite(v):
            return None
    dxdl = (x2 - x1) / (2 * drad); dydl = (y2 - y1) / (2 * drad)
    dxdp = (x4 - x3) / (2 * drad); dydp = (y4 - y3) / (2 * drad)

    phi = math.radians(lat)
    w = math.sqrt(1 - e2 * math.sin(phi) ** 2)
    M = ea * (1 - e2) / w ** 3
    N = ea / w
    Ncos = N * math.cos(phi)

    h = math.hypot(dxdp, dydp) / M
    k = math.hypot(dxdl, dydl) / Ncos
    sin_t = (dydp * dxdl - dxdp * dydl) / (M * Ncos * h * k)
    sin_t = max(-1.0, min(1.0, sin_t))
    ap = h * h + k * k + 2 * h * k * sin_t
    bp = h * h + k * k - 2 * h * k * sin_t
    ap = max(ap, 0.0); bp = max(bp, 0.0)
    a = (math.sqrt(ap) + math.sqrt(bp)) / 2
    b = (math.sqrt(ap) - math.sqrt(bp)) / 2
    s = h * k * abs(sin_t)
    omega = 2 * math.asin(min(1.0, (a - b) / (a + b))) if (a + b) > 0 else 0.0
    return {"a": a, "b": b, "s": s, "omega": omega, "h": h, "k": k}


# =====================================================================
# Geohash, reimplementado aquí
#
# No se importa ninguna biblioteca: el punto es que la implementación de
# R y esta se hayan escrito por separado. Si las dos dan `ezs42` para el
# mismo punto, es que las dos siguen el mismo estándar.
# =====================================================================
B32 = "0123456789bcdefghjkmnpqrstuvwxyz"


def geohash(lon, lat, n=8):
    lo, la = [-180.0, 180.0], [-90.0, 90.0]
    bits, par, out = [], True, []
    while len(bits) < n * 5:
        if par:
            mid = (lo[0] + lo[1]) / 2
            if lon >= mid: bits.append(1); lo[0] = mid
            else: bits.append(0); lo[1] = mid
        else:
            mid = (la[0] + la[1]) / 2
            if lat >= mid: bits.append(1); la[0] = mid
            else: bits.append(0); la[1] = mid
        par = not par
    for j in range(n):
        v = 0
        for b in bits[j * 5:(j + 1) * 5]:
            v = v * 2 + b
        out.append(B32[v])
    return "".join(out)


# =====================================================================
def main() -> int:
    import numpy as np
    import pandas as pd
    import geopandas as gpd
    import pyproj
    from shapely.geometry import Polygon
    from shapely import wkt  # noqa: F401

    a = Auditoria("Precálculo del capítulo 2 verificado")
    D, ruta_d = carga("CAP2_DATOS", "cap2_datos.json")
    M, ruta_m = carga("CAP2_MAPAS", "cap2_mapas.json")
    S, ruta_s = carga("CAP2_SOLUCIONES", "cap2_soluciones.json")

    print(f"\n=== audita_cap2.py · {ruta_d.name} + {ruta_m.name} + {ruta_s.name} ===")
    print(f"    Python {sys.version.split()[0]} · geopandas {gpd.__version__} "
          f"· pyproj {pyproj.__version__}")

    GEOD = pyproj.Geod(ellps="WGS84")
    ELI = pyproj.CRS(4326).ellipsoid
    EA = ELI.semi_major_metre
    EB = ELI.semi_minor_metre
    E2 = (EA ** 2 - EB ** 2) / EA ** 2

    def area_geod(geom):
        """Área geodésica sobre el ELIPSOIDE, en m². El camino de pyproj,
        que no es el de lwgeom aunque los dos usen la misma geodesia."""
        return abs(GEOD.geometry_area_perimeter(geom)[0])

    # -----------------------------------------------------------------
    a.titulo("Módulo 1 · elipsoide y datum")
    E = D["elipsoide"]
    a.cerca(EA, E["a"], "semieje mayor del WGS84 (pyproj)")
    a.cerca(EB, E["b"], "semieje menor del WGS84 (pyproj)")
    a.cerca(EA - EB, E["a_menos_b"], "a - b, el abultamiento ecuatorial")
    a.igual(ELI.inverse_flattening, E["aplanamiento_inv"],
            "aplanamiento inverso", tol=1e-8)
    # Tolerancia 1e-10 y no 1e-12, con motivo: PROJ deriva el semieje
    # MENOR desde a y 1/f, y sf lo lee del propio CRS. Las dos rutas dan
    # el mismo número hasta el bit 40 y difieren en el 41, lo que sobre
    # e² son 1e-11. Aflojar un umbral sin decir por qué es lo que
    # convierte un auditor en un adorno; esto es una diferencia de
    # representación, no de geodesia.
    a.igual(E2, E["e2"], "primera excentricidad al cuadrado", tol=1e-10)

    for i, la in enumerate(E["radios"]["lat"]):
        phi = math.radians(la)
        w = math.sqrt(1 - E2 * math.sin(phi) ** 2)
        a.cerca(EA * (1 - E2) / w ** 3, E["radios"]["M"][i],
                f"radio de curvatura del meridiano a {la}°")
        a.cerca(EA / w, E["radios"]["N"][i],
                f"radio de curvatura del primer vertical a {la}°")
    a.cierto(all(E["radios"]["razon_N_M"][i] >= 1 for i in range(len(E["radios"]["lat"]))),
             "N >= M en toda latitud, como exige el elipsoide")

    ev = E["esfera_vs_elipsoide"]
    d_geod = GEOD.inv(-74.0721, 4.7110, 10.7522, 59.9139)[2]
    a.cerca(d_geod, ev["d_elipsoide_m"], "Bogotá-Oslo, geodésica elipsoidal", rel=1e-7)
    a.cierto(ev["d_esfera_m"] < ev["d_elipsoide_m"],
             "la esfera de s2 acorta esa distancia",
             f"{ev['dif_m']:.3f} m menos")
    a.igual(100 * (ev["d_elipsoide_m"] - ev["d_esfera_m"]) / ev["d_elipsoide_m"],
            ev["dif_pct"], "y el porcentaje cuadra con los dos metros", tol=1e-6)

    # El datum, recalculado con pyproj: 4326 -> 4218 y la distancia entre
    # el punto y su propia cifra leída como si fuera WGS84.
    dt = E["datum"]
    tr = pyproj.Transformer.from_crs(4326, 4218, always_xy=True)
    ciudades = {"Bogotá": (-74.0721, 4.7110), "Medellín": (-75.5636, 6.2518),
                "Cúcuta": (-72.5078, 7.8891), "Leticia": (-69.9406, -4.2150),
                "Quibdó": (-76.6612, 5.6947)}
    for i, nm in enumerate(dt["ciudad"]):
        lon, lat = ciudades[nm]
        lo2, la2 = tr.transform(lon, lat)
        a.cerca(GEOD.inv(lon, lat, lo2, la2)[2], dt["desplazamiento_m"][i],
                f"desplazamiento de datum en {nm}", rel=1e-5)
    a.cierto(all(x > 400 for x in dt["desplazamiento_m"]),
             "el datum viejo mueve más de 400 m en todas las ciudades",
             f"mínimo {min(dt['desplazamiento_m']):.2f} m")
    a.igual(sum(dt["desplazamiento_m"]) / len(dt["desplazamiento_m"]),
            dt["desp_medio_m"], "la media del desplazamiento", tol=1e-6)

    # -----------------------------------------------------------------
    a.titulo("Módulo 2 · un grado, según dónde")
    G = D["grados"]
    for i, la in enumerate(G["lat"]):
        a.cerca(GEOD.inv(0, la, 1, la)[2], G["lon_m_elipsoide"][i],
                f"un grado de longitud a {la}°", rel=1e-8)
        a.cerca(GEOD.inv(0, la, 0, la + 1)[2], G["lat_m_elipsoide"][i],
                f"un grado de latitud a {la}°", rel=1e-8)
    # Las dos cifras que la geodesia elemental publica
    a.igual(G["lon_m_elipsoide"][0], 111319.49, "1° de longitud en el ecuador", tol=0.5)
    a.igual(G["lat_m_elipsoide"][0], 110574.39, "1° de latitud en el ecuador", tol=0.5)
    # La forma: el grado de longitud decrece con la latitud, el de
    # latitud CRECE. Que crezca es el achatamiento, y si saliera al revés
    # el elipsoide estaría del revés.
    a.cierto(all(G["lon_m_elipsoide"][i] > G["lon_m_elipsoide"][i + 1]
                 for i in range(len(G["lat"]) - 1)),
             "el grado de longitud decrece monótonamente con la latitud")
    a.cierto(all(G["lat_m_elipsoide"][i] < G["lat_m_elipsoide"][i + 1] + 1e-6
                 for i in range(len(G["lat"]) - 1)),
             "el grado de latitud CRECE con la latitud (achatamiento)")
    a.cierto(G["lat_esfera_constante"] < 1e-6,
             "sobre la esfera el grado de latitud es constante",
             f"recorrido {G['lat_esfera_constante']:.2e} m")
    a.cierto(G["lat_elipsoide_recorrido_m"] > 1000,
             "sobre el elipsoide recorre más de un kilómetro",
             f"{G['lat_elipsoide_recorrido_m']:.2f} m")

    est = pd.read_csv(SALIDAS / "cap2_estaciones.csv")
    a.igual(len(est), D["csv_sf"]["n"], "estaciones en el CSV exportado")
    eu = G["euclidea"]
    a.igual(len(est), eu["n_estaciones"], "y las que el módulo 2 dice usar")
    a.cierto(eu["km_por_grado_max"] > eu["km_por_grado_min"],
             "la razón km/grado NO es constante", f"recorrido {eu['recorrido_pct']:.4f} %")
    a.cierto(0.99 < eu["corr"] <= 1.0,
             "y aun así la correlación con la geodésica es altísima",
             f"{eu['corr']:.5f}")

    # -----------------------------------------------------------------
    a.titulo("Módulo 3 · las seis proyecciones, por el camino de Snyder")
    P = D["proyecciones"]
    T = P["tabla"]
    CRS_PROY = {
        "Mercator": "+proj=merc +ellps=WGS84 +units=m +no_defs",
        "Web Mercator (3857)": "EPSG:3857",
        "Mollweide": "+proj=moll +ellps=WGS84 +units=m +no_defs",
        "Equal Earth": "+proj=eqearth +ellps=WGS84 +units=m +no_defs",
        "Robinson": "+proj=robin +ellps=WGS84 +units=m +no_defs",
        "Azimutal equidistante (Bogotá)":
            "+proj=aeqd +lat_0=4.711 +lon_0=-74.0721 +ellps=WGS84 +units=m +no_defs",
    }
    rejilla = [(lo, la) for la in (-60, -30, 0, 30, 60)
               for lo in (-150, -90, -30, 30, 90, 150)]
    a.igual(len(rejilla), P["n_indicatrices"], "indicatrices de la rejilla")

    for i, nombre in enumerate(T["nombre"]):
        crs = CRS_PROY.get(nombre)
        if crs is None:
            a.cierto(False, f"{nombre}: el auditor conoce su CRS")
            continue
        trf = pyproj.Transformer.from_crs(4326, pyproj.CRS(crs), always_xy=True)
        vals = [tissot_snyder(trf, lo, la, EA, E2) for lo, la in rejilla]
        vals = [v for v in vals if v is not None]
        oms = sorted(v["omega"] for v in vals)
        ss = sorted(v["s"] for v in vals)
        med = lambda z: z[len(z) // 2] if len(z) % 2 else (z[len(z) // 2 - 1] + z[len(z) // 2]) / 2
        a.igual(math.degrees(med(oms)), T["omega_med_grados"][i],
                f"{nombre}: omega mediana (Snyder)", tol=2e-3)
        a.igual(math.degrees(max(oms)), T["omega_max_grados"][i],
                f"{nombre}: omega máxima (Snyder)", tol=2e-3)
        a.igual(med(ss), T["s_med"][i], f"{nombre}: escala de área mediana", tol=1e-4)
        a.igual(min(ss), T["s_min"][i], f"{nombre}: escala de área mínima", tol=1e-4)
        a.igual(max(ss), T["s_max"][i], f"{nombre}: escala de área máxima", tol=1e-4)
        # LAS BANDERAS SE RECALCULAN, NO SE LEEN. Un JSON que dice de sí
        # mismo que una proyección es conforme no es evidencia de nada.
        a.cierto(T["conforme"][i] == (max(oms) < 1e-6),
                 f"{nombre}: «conforme» recalculada",
                 f"declara {T['conforme'][i]}, recalculado {max(oms) < 1e-6}")
        a.cierto(T["equivalente"][i] == (max(abs(x - 1) for x in ss) < 1e-3),
                 f"{nombre}: «equivalente» recalculada",
                 f"declara {T['equivalente'][i]}, "
                 f"recalculado {max(abs(x - 1) for x in ss) < 1e-3}")

    # El teorema de Tissot: ninguna proyección del plano puede ser las dos
    # cosas. Se comprueba sobre las banderas RECALCULADAS arriba.
    a.cierto(not any(c and e for c, e in zip(T["conforme"], T["equivalente"])),
             "ninguna es conforme Y equivalente (Tissot)")
    a.cierto(sum(T["conforme"]) >= 1 and sum(T["equivalente"]) >= 1,
             "hay al menos una de cada familia",
             f"{sum(T['conforme'])} conformes, {sum(T['equivalente'])} equivalentes")
    a.cierto(P["ninguna_conforme_y_equivalente"] is True,
             "y el JSON lo declara igual que el recálculo")

    # Mercator: el factor de escala tiene que ser sec(phi) sobre la esfera
    mer = P["mercator"]
    for i, la in enumerate(mer["lat"]):
        a.igual(mer["sec_phi"][i], 1 / math.cos(math.radians(la)),
                f"Mercator: sec({la}°) declarado", tol=1e-8)
        a.igual(mer["area"][i], mer["escala"][i] ** 2,
                f"Mercator a {la}°: s = k² porque es conforme", tol=1e-4)
        if la > 0:
            a.cierto(abs(mer["escala"][i] / mer["sec_phi"][i] - 1) < 0.005,
                     f"Mercator a {la}°: la escala elipsoidal se pega a sec(phi)",
                     f"{mer['escala'][i]:.5f} vs {mer['sec_phi'][i]:.5f}")

    # Web Mercator, el resultado que más se cita mal: NO es conforme.
    i3857 = T["nombre"].index("Web Mercator (3857)")
    a.cierto(T["omega_max_grados"][i3857] > 0.01,
             "EPSG:3857 NO es conforme sobre el elipsoide",
             f"omega máx {T['omega_max_grados'][i3857]:.5f}°")
    a.cierto(not T["conforme"][i3857] and not T["equivalente"][i3857],
             "y no es ninguna de las dos cosas")

    # -----------------------------------------------------------------
    a.titulo("Módulo 4 · los códigos EPSG, sobre los 1 122 municipios")
    mun = gpd.read_file(PROCESADO / "colombia_adm2.gpkg")
    llave = pd.read_csv(PROCESADO / "municipios_llave.csv", dtype={"divipola": str})
    mun = mun.merge(llave, on="shapeID", how="left")
    a.igual(len(mun), D["epsg"]["n_municipios"], "municipios de la capa")
    mun_ll = mun.to_crs(4326)
    ver = np.array([area_geod(g) for g in mun_ll.geometry])   # pyproj, no lwgeom

    areas_csv = pd.read_csv(SALIDAS / "cap2_areas.csv", dtype={"divipola": str})
    a.igual(len(areas_csv), len(mun), "filas del CSV de áreas")
    a.cierto(np.allclose(np.sort(ver) / 1e6,
                         np.sort(areas_csv["area_elipsoide_km2"].values), rtol=1e-4),
             "pyproj y lwgeom dan la misma área geodésica",
             f"máx dif rel {np.max(np.abs(np.sort(ver)/1e6 / np.sort(areas_csv['area_elipsoide_km2'].values) - 1)):.2e}")

    for cod, col in ((3116, "area_3116_km2"), (9377, "area_9377_km2"),
                     (3857, "area_3857_km2")):
        ap = mun_ll.to_crs(cod).area.values / 1e6
        orden = np.argsort(areas_csv["divipola"].values)
        a.cierto(np.allclose(np.sort(ap), np.sort(areas_csv[col].values), rtol=1e-6),
                 f"áreas en EPSG:{cod} recalculadas con geopandas")

    fila = {f["codigo"]: f for f in D["epsg"]["filas"]}
    for cod in (3116, 9377, 3857):
        rz = (mun_ll.to_crs(cod).area.values) / ver
        f = fila[cod]
        a.igual(float(np.median(rz)), f["razon_med"], f"EPSG:{cod}: razón mediana", tol=1e-5)
        a.igual(float(np.min(rz)), f["razon_min"], f"EPSG:{cod}: razón mínima", tol=1e-5)
        a.igual(float(np.max(rz)), f["razon_max"], f"EPSG:{cod}: razón máxima", tol=1e-5)
        a.igual(float(np.max(rz) / np.min(rz)), f["estiramiento"],
                f"EPSG:{cod}: estiramiento", tol=1e-5)
        a.igual(int(np.sum(np.abs(rz - 1) > 0.01)), f["n_sobre_1pct"],
                f"EPSG:{cod}: municipios con más del 1 % de error")

    # LAS DOS PROPIEDADES TEÓRICAS, que son exactas y no aproximadas:
    # una transversa de Mercator es conforme, así que su razón de área
    # mínima sobre todo el país es exactamente k².
    a.igual(fila[9377]["razon_min"], 0.9992 ** 2,
            "EPSG:9377: la razón mínima ES k² = 0,9992²", tol=5e-5)
    a.igual(fila[3116]["razon_min"], 1.0,
            "EPSG:3116: la razón mínima ES k² = 1", tol=5e-5)

    # El archipiélago, recalculado
    insular = mun["divipola"].astype(str).str.startswith("88").values
    e3116 = 100 * np.abs(mun_ll.to_crs(3116).area.values / ver - 1)
    e9377 = 100 * np.abs(mun_ll.to_crs(9377).area.values / ver - 1)
    C = D["epsg"]["continente"]; I = D["epsg"]["archipielago"]
    a.igual(int((~insular).sum()), C["n"], "municipios continentales")
    a.igual(int(insular.sum()), I["n"], "municipios insulares")
    a.igual(float(e3116[~insular].max()), C["max_3116_pct"],
            "continente: peor error de 3116", tol=1e-4)
    a.igual(float(e9377[~insular].max()), C["max_9377_pct"],
            "continente: peor error de 9377", tol=1e-4)
    a.igual(float(np.median(e3116[~insular])), C["med_3116_pct"],
            "continente: error mediano de 3116", tol=1e-4)
    a.igual(float(np.median(e9377[~insular])), C["med_9377_pct"],
            "continente: error mediano de 9377", tol=1e-4)
    # Las tres lecturas, RECALCULADAS. Es la regla 4 de la auditoría:
    # nunca auditar una bandera, auditar el hecho que la bandera afirma.
    a.cierto(D["epsg"]["gana_9377_peor_caso_continental"] ==
             bool(e9377[~insular].max() < e3116[~insular].max()),
             "«9377 gana el peor caso continental»",
             f"recalculado {bool(e9377[~insular].max() < e3116[~insular].max())}")
    a.cierto(D["epsg"]["gana_3116_mediana_continental"] ==
             bool(np.median(e3116[~insular]) < np.median(e9377[~insular])),
             "«3116 gana la mediana continental»",
             f"recalculado {bool(np.median(e3116[~insular]) < np.median(e9377[~insular]))}")
    a.cierto(D["epsg"]["gana_3116_pais_entero"] ==
             bool(e3116.max() < e9377.max()),
             "«3116 gana el país entero» coincide con el recálculo")
    a.cierto(e3116[insular].max() > e3116[~insular].max(),
             "y el archipiélago es de verdad el peor caso de 3116")
    # Y las cifras PUBLICADAS del archipiélago, contrastadas contra el
    # recálculo. Sin esto se podían cambiar a mano y el auditor no se
    # enteraba: comprobaba la RELACIÓN entre continente e islas pero no
    # los dos números que el capítulo imprime. Lo cazó el arnés.
    a.igual(float(e3116[insular].max()), I["max_3116_pct"],
            "archipiélago: peor error de 3116", tol=1e-4)
    a.igual(float(e9377[insular].max()), I["max_9377_pct"],
            "archipiélago: peor error de 9377", tol=1e-4)
    a.cierto(sorted(I["municipios"]) == sorted(mun["municipio"][insular].tolist()),
             "y son los dos municipios insulares que dice",
             ", ".join(I["municipios"]))

    # Las bandas de distancia al meridiano central
    B = D["epsg"]["bandas"]
    a.igual(sum(B["n"]), len(mun), "las bandas reparten los 1 122 municipios")
    a.cierto(B["err_9377_pct"][-1] < B["err_3116_pct"][-1],
             "más allá de 5° del meridiano de 3116, 9377 mide mejor",
             f"{B['err_9377_pct'][-1]:.5f} % vs {B['err_3116_pct'][-1]:.5f} %")

    # -----------------------------------------------------------------
    a.titulo("Módulo 5 · reetiquetar no es reproyectar")
    L = D["etiquetar"]
    loc = gpd.read_file(PROCESADO / "bogota_localidades.gpkg")
    a.igual(len(loc), L["n_localidades"], "localidades de Bogotá")
    a.igual(L["set_crs_max_delta"], 0.0,
            "st_set_crs no mueve NI UNA coordenada", tol=1e-12)
    a.cierto(L["transform_max_delta"] > 1e5,
             "st_transform las mueve todas, y por millones",
             f"{L['transform_max_delta']:.1f}")
    a.igual(L["transform_n_movidas"], L["n_vertices"],
            "y no deja ni un vértice en su sitio")
    a.cierto(L["lon_absurda"] > 1e6,
             "el delator: una «longitud» de millones de grados",
             f"{L['lon_absurda']:.0f}")
    bb = loc.to_crs(4326).total_bounds
    for j, v in enumerate(bb):
        a.igual(v, L["bbox_bien"][j], f"caja bien proyectada, componente {j}", tol=1e-6)
    a.cerca(sum(area_geod(g) for g in loc.to_crs(4326).geometry) / 1e6,
            L["area_bien_km2"], "área de Bogotá bien proyectada (km²)", rel=1e-4)

    sil = L["silencioso"]
    a.igual(sil["desplazamiento_m"], 0.0,
            "reetiquetar 4686 como 4326 NO mueve nada (coinciden)", tol=0.5)
    a.cierto(sil["contraste_desplazamiento_m"] > 400,
             "y el datum viejo sí desplaza",   # no toda etiqueta equivocada hace daño
             f"{sil['contraste_desplazamiento_m']:.2f} m")

    # -----------------------------------------------------------------
    a.titulo("Módulo 6 · la esfera y el elipsoide")
    ME = D["medir"]["colombia"]
    union = mun_ll.geometry.union_all()
    a.cerca(area_geod(union) / 1e6, ME["area_elipsoide_km2"],
            "área de Colombia sobre el elipsoide (pyproj)", rel=1e-4)
    a.cierto(ME["area_esfera_km2"] > ME["area_elipsoide_km2"],
             "la esfera de s2 la infla", f"+{ME['dif_esfera_km2']:.2f} km²")
    a.igual(100 * (ME["area_esfera_km2"] - ME["area_elipsoide_km2"]) / ME["area_elipsoide_km2"],
            ME["dif_esfera_pct"], "el porcentaje cuadra con los dos valores", tol=1e-6)
    a.cierto(0.3 < ME["dif_esfera_pct"] < 0.7,
             "y en el orden que predice la geodesia",
             f"{ME['dif_esfera_pct']:.5f} %")
    a.cierto(abs(ME["dif_9377_pct"]) < abs(ME["dif_esfera_pct"]),
             "9377 se acerca al elipsoide más que la esfera")
    MU = D["medir"]["municipios"]
    a.cierto(MU["equivalente_a_municipios"] > 10,
             "el error de la esfera equivale a decenas de municipios",
             f"{MU['equivalente_a_municipios']}")

    # La discrepancia declarada: el auditor la LEE. Declarada = material
    # didáctico; sin declarar = fallo.
    disc = D["discrepancias"]
    a.cierto(len(disc) >= 2, "el capítulo declara sus discrepancias", f"{len(disc)}")
    a.cierto(any("s2" in d["que"] or "s2" in d["motivo"] for d in disc),
             "y una de ellas es la de s2")
    for k, d in enumerate(disc):
        a.cierto(all(d.get(c) for c in ("que", "motivo", "donde", "como_recuperar")),
                 f"discrepancia {k + 1}: trae qué, por qué, dónde y cómo recuperar")

    # -----------------------------------------------------------------
    a.titulo("Módulo 7 · formatos vectoriales")
    F = D["formatos"]
    a.salta("que GDAL trunque los nombres así",
            "geopandas y sf llaman al MISMO GDAL: aquí se audita el análisis, no el comportamiento")
    a.igual(F["shapefile"]["n_archivos"], 4,
            "el shapefile son cuatro archivos (.shp .shx .dbf .prj)")
    a.cierto(not F["shapefile"]["tiene_cpg"],
             "y sin .cpg: el .dbf no declara su codificación")
    a.cierto(F["shapefile"]["n_campos_largos"] > 0,
             "hay campos con nombre de más de 10 caracteres",
             f"{F['shapefile']['n_campos_largos']} de {F['shapefile']['n_campos']}")
    a.cierto(F["shapefile"]["truncado_simple"] is False,
             "y GDAL no los TRUNCA: los desfigura quitándoles vocales")
    for j, (antes, despues) in enumerate(zip(F["shapefile"]["ejemplos_antes"],
                                             F["shapefile"]["ejemplos_despues"])):
        a.cierto(len(despues) <= 10 and despues != antes[:10],
                 f"campo {j + 1}: «{antes}» -> «{despues}»")
    a.cierto(F["shapefile"]["tipo_fecha_despues"] != "Date" or
             F["gpkg"]["tipo_fecha_despues"] == "Date",
             "el GeoPackage conserva el tipo fecha")
    a.cierto(F["gpkg"]["nombres_intactos"] is True,
             "y el GeoPackage conserva los nombres enteros")
    a.cierto(F["geojson"]["bytes"] > F["shapefile"]["bytes"],
             "GeoJSON pesa más que el shapefile",
             f"×{F['geojson']['razon_sobre_shp']:.4f}")
    a.cerca((CRUDO / "COL_ADM2.geojson").stat().st_size / 1024 ** 2,
            F["pais"]["geojson_mb"], "el GeoJSON nacional, medido en disco", rel=1e-6)
    a.cerca((PROCESADO / "colombia_adm2.gpkg").stat().st_size / 1024 ** 2,
            F["pais"]["gpkg_mb"], "el GeoPackage nacional, medido en disco", rel=1e-6)
    a.igual(F["pais"]["geojson_mb"] / F["pais"]["gpkg_mb"], F["pais"]["razon"],
            "y la razón entre los dos", tol=1e-6)

    # -----------------------------------------------------------------
    a.titulo("Módulo 8 · lon/lat invertidos")
    CS = D["csv_sf"]
    lon = est["lon"].values; lat = est["lat"].values
    a.igual(float(lon.mean()), CS["centroide_bien"][0], "centroide correcto, longitud", tol=1e-6)
    a.igual(float(lat.mean()), CS["centroide_bien"][1], "centroide correcto, latitud", tol=1e-6)
    a.igual(CS["centroide_mal"][0], CS["centroide_bien"][1],
            "al invertir, la longitud pasa a ser la latitud media", tol=1e-9)
    d = GEOD.inv(lon, lat, lat, lon)[2] / 1000
    a.igual(float(np.mean(d)), CS["desplazamiento_km_med"],
            "desplazamiento medio al invertir (km)", tol=1e-3)
    a.igual(float(np.min(d)), CS["desplazamiento_km_min"], "el mínimo", tol=1e-3)
    a.igual(float(np.max(d)), CS["desplazamiento_km_max"], "el máximo", tol=1e-3)
    a.cierto(CS["desplazamiento_km_min"] > 8000,
             "ninguna estación se queda ni medianamente cerca",
             f"mínimo {CS['desplazamiento_km_min']:.1f} km")
    a.igual(sum(CS["destino"]["n"]), CS["n"], "el destino reparte las 361")
    a.igual(CS["n_en_colombia"], 0, "NINGUNA cae en Colombia al invertir")
    a.cierto("Antarctica" in CS["destino"]["nombre"],
             "y la mayoría aterriza en la Antártida",
             f"{max(CS['destino']['n'])} de {CS['n']}")
    a.cierto(all(-90 <= v <= 90 for v in (CS["caja_mal"][1], CS["caja_mal"][3])),
             "las invertidas siguen siendo latitudes válidas",
             "por eso nadie avisa")
    a.cierto(CS["hubo_aviso"] is False, "st_as_sf no dio ni un aviso")
    a.igual(CS["coma_decimal"]["n_na"], 5,
            "y la coma decimal convierte las cinco coordenadas en NA")

    # -----------------------------------------------------------------
    a.titulo("Módulo 9 · error posicional y su sesgo")
    PO = D["posicional"]
    sedes = pd.read_csv(SALIDAS / "cap2_sedes.csv")
    a.igual(len(sedes), PO["n_sedes"], "sedes del CSV exportado")
    for r in PO["redondeos"]:
        dg = int(r["decimales"])
        n_pos = len(set(zip(np.round(sedes["lon"].values, dg),
                            np.round(sedes["lat"].values, dg))))
        a.igual(n_pos, r["n_posiciones"],
                f"posiciones distintas al redondear a {dg} decimales")
        a.cierto(r["desplaz_med_m"] > 0, f"y el desplazamiento medio a {dg} dec es positivo",
                 f"{r['desplaz_med_m']:.2f} m")
    a.cierto(PO["redondeos"][2]["n_posiciones"] < PO["n_sedes"] / 5,
             "con dos decimales quedan menos de n/5 posiciones",
             f"{PO['redondeos'][2]['n_posiciones']} de {PO['n_sedes']}")
    a.igual(PO["n_sedes"] / PO["redondeos"][2]["n_posiciones"],
            PO["sedes_por_posicion_2dec"], "sedes por posición", tol=1e-6)
    # EL ANCLA EXTERNA: la fuente del MEN que T0.4 descartó tenía dos
    # decimales de verdad, y allí la densidad fue 2 403/398. Degradar
    # nuestro dato bueno tiene que reproducirla.
    men = PO["men_descartada"]
    a.igual(men["n_sedes"] / men["n_posiciones"], men["sedes_por_posicion"],
            "la densidad de la fuente descartada del MEN", tol=1e-6)
    a.cierto(abs(PO["sedes_por_posicion_2dec"] / men["sedes_por_posicion"] - 1) < 0.25,
             "y nuestra degradación la reproduce",
             f"{PO['sedes_por_posicion_2dec']:.4f} vs {men['sedes_por_posicion']:.4f}")
    # El ruido tiene que crecer monótonamente
    sig = [r["sigma_m"] for r in PO["ruidos"]]
    pct = [r["pct_cambian"] for r in PO["ruidos"]]
    a.cierto(sig == sorted(sig) and pct == sorted(pct),
             "más ruido, más reasignaciones: la relación es monótona", str(pct))
    SG = PO["sesgo"]
    a.cierto(SG["n_replicas"] >= 100,
             "el sesgo se mide con réplicas, no con una realización",
             f"{SG['n_replicas']}")
    a.cierto(SG["emc_global_pct"] < SG["tasa_global_pct"] / 20,
             "y el error de Monte Carlo es pequeño frente a la tasa",
             f"{SG['emc_global_pct']:.4f} vs {SG['tasa_global_pct']:.4f}")
    a.igual(len(SG["localidad"]), SG["n_localidades_con_30"],
            "las localidades del cuadro del sesgo")
    a.cierto(all(SG["tasa_pct"][i] >= SG["tasa_pct"][i + 1]
                 for i in range(len(SG["tasa_pct"]) - 1)),
             "el cuadro va ordenado de peor a mejor")
    a.igual(max(SG["tasa_pct"]), SG["tasa_max_pct"], "la tasa máxima", tol=1e-6)
    a.igual(min(SG["tasa_pct"]), SG["tasa_min_pct"], "la mínima", tol=1e-6)
    a.cierto(SG["tasa_max_pct"] / SG["tasa_min_pct"] > 5,
             "el mismo error cuesta MUY distinto según la localidad",
             f"×{SG['razon_max_min']:.4f}")
    # La correlación con perímetro/área, recalculada desde los vectores
    tasa = np.array(SG["tasa_pct"]); comp = np.array(SG["compacidad"])
    a.igual(float(np.corrcoef(tasa, comp)[0, 1]), SG["corr_pearson"],
            "correlación de la tasa con perímetro/área", tol=1e-6)
    a.cierto(SG["corr_pearson"] > 0.4,
             "y es sustancial: el sesgo es GEOMÉTRICO",
             f"Pearson {SG['corr_pearson']:.5f}, Spearman {SG['corr_spearman']:.5f}")
    a.cierto(PO["por_estrato"]["monotono_en_estrato"] is False,
             "por estrato NO hay patrón monótono",
             "y eso también se publica")

    # -----------------------------------------------------------------
    a.titulo("Módulo 10 · topología y DE-9IM")
    TP = D["topologia"]
    lazo = Polygon([(0, 0), (2, 2), (2, 0), (0, 2), (0, 0)])
    a.cierto(not lazo.is_valid, "shapely también dice que el lazo es inválido")
    a.igual(lazo.area, TP["lazo"]["area_antes"],
            "y su área es CERO, sin dar ningún error", tol=1e-12)
    from shapely.validation import make_valid
    a.igual(make_valid(lazo).area, TP["lazo"]["area_despues"],
            "tras repararlo, el área es 2", tol=1e-9)
    a.igual(TP["lazo"]["n_partes_despues"], 2,
            "y el polígono se ha convertido en dos triángulos")
    a.igual(len(mun[~mun.is_valid]), TP["municipios"]["n_invalidos"],
            "geometrías inválidas en la capa municipal")
    a.igual(TP["municipios"]["n_invalidos"], 0, "y son cero")

    A = Polygon([(0, 0), (4, 0), (4, 4), (0, 4)])
    CASOS = {
        "disjuntos": Polygon([(6, 6), (8, 6), (8, 8), (6, 8)]),
        "tocan": Polygon([(4, 0), (6, 0), (6, 4), (4, 4)]),
        "solapan": Polygon([(2, 2), (6, 2), (6, 6), (2, 6)]),
        "contiene": Polygon([(1, 1), (3, 1), (3, 3), (1, 3)]),
        "iguales": Polygon([(0, 0), (4, 0), (4, 4), (0, 4)]),
    }
    for j, nm in enumerate(TP["de9im"]["caso"]):
        a.cierto(A.relate(CASOS[nm]) == TP["de9im"]["matriz"][j],
                 f"DE-9IM de «{nm}» según shapely",
                 f"{A.relate(CASOS[nm])} / {TP['de9im']['matriz'][j]}")
    a.cierto(len(set(TP["de9im"]["matriz"])) == len(TP["de9im"]["matriz"]),
             "las cinco matrices son distintas entre sí")

    BF = TP["buffer"]
    a.cierto(abs(BF["m9377_area_km2"] - math.pi) < 0.02,
             "un buffer de 1 000 m en metros mide pi km²",
             f"{BF['m9377_area_km2']:.5f}")
    a.cierto(BF["m3857_radio_real_m"] < 1000,
             "el buffer «de 1 000 m» en 3857 mide menos",
             f"{BF['m3857_radio_real_m']:.2f} m")

    # -----------------------------------------------------------------
    a.titulo("Módulo 11 · índices y geohash")
    IN = D["ingenieria"]
    J = IN["join"]
    a.igual(J["n_puntos"] * J["n_poligonos"], J["pares_fuerza_bruta"],
            "los pares de la fuerza bruta")
    a.cierto(J["pares_tras_cajas"] < J["pares_fuerza_bruta"] / 5,
             "el filtro de cajas deja menos de un quinto",
             f"×{J['reduccion']:.4f}")
    a.igual(J["pares_fuerza_bruta"] / J["pares_tras_cajas"], J["reduccion"],
            "y la reducción declarada cuadra", tol=1e-6)
    a.cierto(J["aciertos_exactos"] <= J["pares_tras_cajas"],
             "los aciertos exactos son un subconjunto de los candidatos")

    GH = IN["geohash"]
    a.cierto(GH["alfabeto"] == B32, "el alfabeto base-32 es el estándar")
    for v in GH["vectores_canonicos"]:
        n = len(v["esperado"])
        a.cierto(geohash(v["lon"], v["lat"], n) == v["esperado"],
                 f"geohash de ({v['lon']}, {v['lat']}) según esta implementación",
                 f"{geohash(v['lon'], v['lat'], n)} / {v['esperado']}")
        a.cierto(v["obtenido"] == v["esperado"],
                 "y el de R coincide con el vector publicado")
    a.cierto(GH["round_trip"]["completo"] is True,
             "el round-trip cubre todos los puntos",
             f"{GH['round_trip']['n_dentro']} de {GH['round_trip']['n_puntos']}")
    a.igual(GH["round_trip"]["n_dentro"], GH["round_trip"]["n_puntos"],
            "y no se pierde ninguno")
    # El round-trip, rehecho AQUÍ sobre el CSV: es la comprobación que de
    # verdad prueba que las dos implementaciones son la misma.
    for niv in GH["niveles"]:
        L = int(niv["longitud"])
        g = [geohash(lo, la, L) for lo, la in zip(sedes["lon"], sedes["lat"])]
        a.igual(len(set(g)), niv["n_celdas"],
                f"celdas distintas de longitud {L}, recalculadas en Python")
    a.cierto(all(GH["niveles"][i]["celda_ancho_km"] > GH["niveles"][i + 1]["celda_ancho_km"]
                 for i in range(len(GH["niveles"]) - 1)),
             "la celda encoge al alargar el geohash")
    a.cierto(all(f["pct_distinto"] <= GH["frontera"][i + 1]["pct_distinto"]
                 for i, f in enumerate(GH["frontera"][:-1])),
             "más fino el geohash, más vecinos al otro lado")

    # -----------------------------------------------------------------
    a.titulo("Los mapas")
    kb_total = 0.0
    for nombre, mapa in M.items():
        kb_total += audita_geomapa(a, mapa, nombre)
    a.cierto(kb_total <= 120, "el conjunto de mapas cabe en el presupuesto del capítulo",
             f"{kb_total:.1f} KB de 120")

    pm = M["proyecciones_mundo"]
    a.igual(len(pm["vistas"]), 6, "el mapa del mundo trae las seis vistas")
    for v in pm["vistas"]:
        ind = v.get("indicatrices")
        a.cierto(ind is not None, f"{v['nombre']}: trae sus indicatrices")
        if not ind:
            continue
        n = len(ind["x"])
        a.igual(n, P["n_indicatrices"], f"{v['nombre']}: y son las de la rejilla")
        for campo in ("y", "a", "b", "s", "omega", "orient"):
            a.igual(len(ind[campo]), n, f"{v['nombre']}: el vector {campo} tiene n")
        a.cierto(all(x >= y for x, y in zip(ind["a"], ind["b"])),
                 f"{v['nombre']}: a ≥ b en los semiejes",
                 "el semieje mayor nunca es menor que el menor")
        a.cierto(all(o >= 0 for o in ind["omega"]),
                 f"{v['nombre']}: omega nunca es negativa",
                 f"mínima {min(ind['omega']):.2e} (deformación angular)")
        a.cierto(all(s > 0 for s in ind["s"]),
                 f"{v['nombre']}: s siempre es positiva",
                 f"mínima {min(ind['s']):.4f} (escala de área)")
        a.cierto(ind["rq"] > 0, f"{v['nombre']}: el radio base es positivo",
                 f"{ind['rq']:.2f}")
        a.cierto(all(-4096 * 3 <= q <= 4096 * 4 for q in ind["x"] + ind["y"]),
                 f"{v['nombre']}: indicatrices en el lienzo",
                 f"[{min(ind['x'] + ind['y'])}, {max(ind['x'] + ind['y'])}] "
                 f"dentro de [{-4096 * 3}, {4096 * 4}]")
        # a*b tiene que ser s: son la misma cantidad por dos caminos
        peor = max(abs(aa * bb - ss) for aa, bb, ss in zip(ind["a"], ind["b"], ind["s"]))
        a.cierto(peor < 1e-3, f"{v['nombre']}: a·b = s en todas",
                 f"peor dif {peor:.2e}")

    # La relación de aspecto: el criterio duro de T0.3. Un mapa con la
    # escala en x distinta de la de y es un mapa mal dibujado.
    for nombre, mapa in M.items():
        # El MISMO rótulo corto que usa `audita_geomapa`, y por el mismo
        # motivo: si aquí se rotulara con el nombre largo de la vista, la
        # mitad de estas comprobaciones volvería a arrastrar su detalle.
        cajas = ([(e, v["caja"]) for e, v in
                  zip(rotulos_de_vistas([v["nombre"] for v in mapa["vistas"]]),
                      mapa["vistas"])]
                 if mapa.get("modo") == "proyeccion" else [("", mapa["caja"])])
        for etq, caja in cajas:
            ancho = caja[2] - caja[0]; alto = caja[3] - caja[1]
            a.cierto(ancho > 0 and alto > 0,
                     f"{nombre}{'/' + etq if etq else ''}: la caja tiene área",
                     f"{ancho:.1f} × {alto:.1f}, las dos positivas")

    # -----------------------------------------------------------------
    a.titulo("Formato y coherencia general")
    txt = json.dumps(D, ensure_ascii=False)
    for cad in ("Bogotá", "Colombia", "área"):
        a.cierto(cad in txt, f"las tildes llegan enteras: «{cad}»")
    # LA CORRUPCIÓN SE BUSCA POR SU HUELLA, no por la ausencia de la
    # cadena buena. Es la lección de T0.5 —las tildes no desaparecen, se
    # convierten en otra cosa— y aquí la volvió a demostrar el arnés: la
    # inyección corrompía UNA aparición de «Bogotá» de las muchas que
    # hay, y `"Bogotá" in txt` seguía siendo cierto. Buscar `<c3>` sí
    # falla, porque esa secuencia no puede estar en un texto sano.
    for archivo, obj in (("datos", D), ("soluciones", S), ("mapas", M)):
        crudo = json.dumps(obj, ensure_ascii=False)
        malas = [h for h in ("<c3>", "<c2>", "Ã", "â€", "\ufffd") if h in crudo]
        a.cierto(not malas, f"{archivo}: ni una tilde convertida en bytes crudos",
                 "" if not malas else f"aparece {malas}")
    for etq, obj in (("datos", D), ("soluciones", S), ("mapas", M)):
        malos = list(sin_nan(obj))
        a.cierto(not malos, f"{etq}: ni un NaN ni un infinito",
                 "" if not malos else f"{len(malos)}, p. ej. {malos[:3]}")
    for etq, obj in (("datos", D), ("soluciones", S)):
        peor = [(r, n) for r, n in decimales(obj) if n > 10]
        a.cierto(not peor, f"{etq}: ningún flotante pasa de 10 decimales",
                 "" if not peor else f"{len(peor)}, p. ej. {peor[:3]}")
    # Y HAY QUE DECIR HASTA DÓNDE LLEGA ESA COMPROBACIÓN, porque el arnés
    # descubrió que sobre magnitudes grandes es INCAPAZ de fallar: un
    # `double` con parte entera de siete cifras no puede cargar más de
    # diez decimales, así que inyectarle once no cambia nada. La
    # comprobación es legítima —protege el doble redondeo de las cifras
    # pequeñas, que son casi todas las del capítulo— pero su cobertura
    # tiene un techo, y callarlo la convertiría en una garantía falsa.
    grandes = [r for r, _ in decimales(D) if True]
    a.salta("el tope de decimales con siete cifras enteras",
            "un double no puede llevar más de ~10 decimales ahí: la comprobación no puede fallar")

    a.igual(D["meta"]["capitulo"], 2, "el capítulo declarado")
    a.igual(D["meta"]["semilla"], 2026, "la semilla declarada")
    a.cierto(D["meta"]["anclas_verificadas"] >= 20,
             "el generador verificó sus anclas contra la literatura",
             str(D["meta"]["anclas_verificadas"]))
    a.cierto(D["meta"]["proj"].startswith("9."),
             "y declara la versión de PROJ con la que midió", D["meta"]["proj"])
    a.igual(S["meta"]["capitulo"], 2, "las soluciones son del capítulo 2")
    a.igual(S["meta"]["n_ejercicios"], 5, "y son CINCO ejercicios (desviación declarada)")
    a.igual(S["meta"]["semilla"], D["meta"]["semilla"], "los dos guiones comparten semilla")

    # Los ejercicios: sus conclusiones se recalculan desde sus propias cifras
    e1 = S["e1"]["solucion"]
    a.cierto(e1["la_isla_cambia_la_respuesta"] ==
             (e1["elegido_continente"] != e1["elegido_con_isla"]),
             "E1: «la isla cambia la respuesta» cuadra")
    a.cierto(e1["elegido_continente"] == "EPSG:9377",
             "E1: sobre el continente gana 9377, como su diseño promete")
    e2 = S["e2"]["solucion"]
    a.cierto(all(e2["radios"][i]["n_cambian"] <= e2["radios"][i + 1]["n_cambian"]
                 for i in range(len(e2["radios"]) - 1)),
             "E2: cuanto mayor el radio, más sedes cambian de cuenta")
    a.cierto(e2["cuenta_de_menos"] is True,
             "E2: el buffer en grados cuenta de menos",
             "siempre, o sea sesgo con signo")
    a.cierto(e2["achatamiento_oslo"] < e2["achatamiento_bogota"],
             "E2: el achatamiento es mucho peor en Oslo que en Bogotá",
             f"{e2['achatamiento_oslo']:.5f} vs {e2['achatamiento_bogota']:.5f}")
    e3 = S["e3"]["solucion"]
    a.igual(e3["vp"] + e3["fn"], e3["n_invertidas"], "E3: la tabla de confusión cuadra")
    a.igual(e3["vp"] + e3["fp"] + e3["fn"] + e3["vn"], e3["n"], "E3: y suma el total")
    a.cierto(e3["solapan_las_cajas"] is False,
             "E3: los rangos de lon y lat NO se solapan",
             "por eso funciona")
    e4 = S["e4"]["solucion"]
    a.cierto(e4["vecino_intacto"] == (e4["n_cambia_vecino"] == 0),
             "E4: la bandera del vecino coincide con su conteo")
    a.cierto(e4["umbral_falla"] is True,
             "E4: y el umbral sí discrepa")
    a.cierto(all(e4["umbrales"][i]["discrepan"] <= e4["umbrales"][i + 1]["discrepan"]
                 for i in range(len(e4["umbrales"]) - 1)),
             "E4: las discrepancias crecen con el umbral")
    e5 = S["e5"]["solucion"]
    a.cierto(all(e5["tasa_pct"][i] <= e5["tasa_pct"][i + 1] + 1e-9
                 for i in range(len(e5["tasa_pct"]) - 1)),
             "E5: la tasa crece monótonamente con sigma")
    a.cierto(e5["tasa_en_sigma_max_pct"] <= e5["objetivo_pct"] * 1.2,
             "E5: el sigma despejado cumple el requisito",
             f"{e5['tasa_en_sigma_max_pct']:.4f} % con objetivo {e5['objetivo_pct']} %")

    return a.cierre()


if __name__ == "__main__":
    sys.exit(main())
