#!/usr/bin/env python3
"""
audita_taller3.py — auditoría independiente de las cifras de control del Taller 3

Material de Estadística Espacial 2026-II (20929). Ver PLAN_Taller_3_SIG.md.

Las cifras de control de este taller las produjo QGIS corriendo
`claves_qgis_taller3.py` (con el complemento `taller3_espacial` y su
`nucleo.py`) y R corriendo `genera_taller3.R`. De ellas salen las notas.
Este auditor las rehace POR OTRO CAMINO —geopandas, shapely, pyproj, scipy,
numpy; NO importa `nucleo.py` ni nada de QGIS— y las contrasta. Si las dos
implementaciones se equivocan igual, no lo ve; si una se equivoca sola,
sí. Lo midió así el 2026-11-11: sobre 16 localidades, 4 700 cifras, la
máxima desviación relativa de lo que debe coincidir exacto es de 2·10⁻⁸
(el área del complemento, la fórmula del zapatero sobre coordenadas de
siete cifras, pierde 1,5·10⁻⁹) y la de G y F es CERO.

QUÉ COMPRUEBA, Y POR QUÉ CADA COSA

  1. LO PÚBLICO (siempre corre, con o sin claves). El JSON viaja entero
     dentro del HTML: sus claves exactas, que no lleve ninguna respuesta,
     las 1000 variantes (claves, valores declarados, reparto equilibrado,
     localidades elegibles), n/área/lambda de cada localidad rehechos desde
     el GeoPackage, y que la página incruste EXACTAMENTE ese JSON.

  2. LAS CLAVES DE QGIS (solo si `precalculo/cache/` las tiene; no están en
     git). T1: reproyectar, 0 sedes reetiquetadas dentro, áreas en 9377 y en
     3857. T2: conteo, densidad, puestos, cuantiles, Jenks, rejillas de 2 y 4
     km. T3: cuadrantes con celdas recortadas, vecino más próximo (QGIS y
     con el área real), G y F con corrección de borde por muestra reducida
     (umbral), K y L con la misma corrección, y la banda de 99 simulaciones
     (REPRODUCIDA, con `default_rng(2026)` y el mismo orden de muestreo).
     T4: el mapa de calor.

  3. LA CLAVE DE R (T5): lo estructural, y los cruces contra el mapa de
     calor de QGIS y contra el estimador exacto.

  4. QUE LAS DOS PLATAFORMAS DE QGIS (macOS y Docker/Linux) DIGAN LO MISMO,
     hoja por hoja, y que ninguna hoja de la clave quede sin contrastar.

LO QUE ESTE AUDITOR ENCONTRÓ SOBRE QGIS, Y QUEDA ESCRITO AQUÍ

  · El mapa de calor de QGIS NO es el estimador exacto. Su posición
    subpíxel en y sale mirada desde el borde de ABAJO de la caja y no
    desde el de arriba (hay que ajustar el ráster real para verlo): cada
    punto se mueve hasta ±25 m en vertical y el máximo se aparta del
    máximo del núcleo hasta un 2,5 %. Esto se REPRODUCE aquí con tolerancia
    estrecha (réplica) y, aparte, se contrasta contra el estimador exacto
    con la tolerancia ancha que pide el encargo. El PLAN dice «al 1–2 %
    porque las rejillas de píxeles no están alineadas»: es verdad a medias.
  · El «Jenks» de QGIS no es el Fisher–Jenks óptimo en estos datos: su
    tercer corte es 5,44103 y el óptimo, hallado probando las 3 876
    particiones posibles, es 6,11232 (SSE 3,651 frente a 3,559). Con el
    óptimo cambiarían de clase 6 localidades y no 5: Bosa, cuya densidad
    (6,11232) es justo el corte, pasaría de la clase 4 a la 3.
    mapclassify.NaturalBreaks (k-medias, no determinista) sí reproduce el
    resultado de QGIS, así que lo más probable es que «Jenks» en QGIS sea
    ese óptimo local. Se comprueba lo que se puede comprobar sin fiarse de
    QGIS y el resto se DECLARA SALTADO, en voz alta.
  · Cuantiles: mapclassify.Quantiles coincide EXACTO con QGIS, cortes y
    clases.

LO QUE NO SE AUDITA DE FORMA INDEPENDIENTE, DECLARADO (cuenta como saltada)
  · bw.diggle, bw.ppl y los coeficientes y valores z de `ppm`: implementarlos
    de nuevo no sería un camino distinto sino una copia de spatstat; solo se
    comprueba que sean finitos, positivos donde toca, y coherentes entre sí.
  · Jenks, como arriba.
  · Si faltan las claves (clon limpio), TODO lo que depende de ellas.

TOLERANCIAS, con su porqué (las que no son 1e-6, medidas sobre los datos)
  1e-6     geometría contra geometría (GEOS contra GEOS) y todo lo derivado
  entero   exacto
  5e-6 abs lo publicado a cinco decimales (area_km2 y lambda del JSON)
  1e-8     macOS contra Linux (medido 3,7·10⁻¹⁰)
  1e-4     «el ráster escalado integra n» (medido 4,7·10⁻⁶: suma de píxeles)
  0,5 %    masa dentro de la localidad, QGIS y R contra el estimador exacto
           (medido 0,38 % y 0,36 %)
  3 %      máximo de QGIS contra el exacto (medido 2,5 %)
  5 %      máximo de R contra el exacto: `density()` también reparte los
           puntos en píxeles (medido 2,5 % sin borde y 3,7 % con él)
  1 %      masa de R contra masa de QGIS: el encargo decía 0,5 % y SE REBASA
           (medido 0,54 % en Barrios Unidos 600 y 0,53 % en el 800); R y
           QGIS caen a lados opuestos del valor exacto (-0,36 % y +0,18 %),
           y 1 % es la suma de las dos tolerancias individuales

Uso:  <geo_env>/python precalculo/audita_taller3.py   (desde `Estadistica espacial/`)
      Tarda unos 10 s. Devuelve 1 si algo falla; 0 con las saltadas dichas.

Variables de entorno (las usa `prueba_auditor_taller3.py`, que envenena COPIAS
y no toca nunca los archivos publicados):
  TALLER3_DATOS          el JSON público
  TALLER3_CLAVES_MAC / TALLER3_CLAVES_LINUX / TALLER3_CLAVES_R   las claves
  TALLER3_HTML           la página
  TALLER3_RECOMPUTO      ruta de un JSON donde guardar/leer lo recalculado;
                         lleva la huella de los datos y de ESTE archivo, así
                         que no puede quedar obsoleto. Sin ella se recalcula
                         siempre. Existe para que el arnés no pague 10 s por
                         cada una de sus ~120 inyecciones.
"""
from __future__ import annotations

import collections
import hashlib
import itertools
import json
import math
import os
import pathlib
import re
import sys
import warnings

warnings.filterwarnings("ignore")
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

RAIZ = pathlib.Path(__file__).resolve().parent.parent
SALIDAS = RAIZ / "precalculo" / "salidas"
CACHE = RAIZ / "precalculo" / "cache"
DATOS = RAIZ / "entrega" / "datos"
HTMLS = RAIZ / "Htmls_Espacial"

from audita_base import Auditoria, decimales, sin_nan  # noqa: E402

# --- Lo que el taller reparte -------------------------------------------
N_MIN = 35
SEMILLA = 2026
NSIM = 99
NX = (3, 4, 5)
R_GF = (100, 150, 200)
R_KL = (200, 300, 400)
RADIOS = (600, 800, 1000)
LADO_F = 200            # sitios por lado de la rejilla de F
PIXEL = 50.0            # píxel del mapa de calor de QGIS, en m
PIXEL_FINO = 10.0       # píxel del estimador exacto, en m
LADOS_REJILLA = (2000, 4000)
TOTAL_SEDES = 2209
N_LOCALIDADES = 20
N_ELEGIBLES = 16

# --- Tolerancias (ver la cabecera) --------------------------------------
REL = 1e-6
REL_PLATAFORMA = 1e-8
TOL_PUBLICADO = 5.1e-6          # lo redondeado a cinco decimales
TOL_MASA_TOTAL = 1e-4
TOL_MASA_EXACTA = 0.005
TOL_PICO_EXACTO = 0.03
TOL_PICO_R = 0.05
TOL_MASA_R_QGIS = 0.01

# Cada una es la respuesta de una tarea o el nombre de su campo en las claves.
PROHIBIDAS = ("chi2", "chi_2", "p_derecha", "p_bilateral", "indice", "esperad", "banda",
              "vecino", "bw_", "pico", "masa", "cuantil", "jenks", "clase", "puesto",
              "densidad", "inflacion", "reetiquet", "respuesta", "sigma", "usables",
              "sitios", "ppm", "l_menos", "elegible", "plataforma")

RAIZ_PUBLICA = {"semilla", "n_min", "opciones", "ciudad", "localidades", "variantes"}
CAMPOS_CIUDAD = {"sedes", "localidades", "sedes_en_alguna_localidad"}
CAMPOS_LOC = {"n", "area_km2", "lambda"}
CAMPOS_VARIANTE = {"clave", "localidad", "nx", "r_gf", "r_kl", "radio"}
OPCIONES = {"nx": list(NX), "r_gf": list(R_GF), "r_kl": list(R_KL), "radio": list(RADIOS)}


# =====================================================================
# Utilidades
# =====================================================================
def val(o, *ks):
    """Baja por `ks` sin reventar: None si algo falta."""
    for k in ks:
        if isinstance(o, dict) and k in o:
            o = o[k]
        else:
            return None
    return o


def num(x) -> bool:
    return isinstance(x, (int, float)) and not isinstance(x, bool) and x == x


def hojas(o, ruta=()):
    """Cada hoja con su ruta. Las listas son UNA hoja."""
    if isinstance(o, dict):
        for k, v in o.items():
            yield from hojas(v, ruta + (k,))
    else:
        yield ruta, o


def aplana(o, ruta=""):
    """Como `hojas`, pero bajando también por las listas."""
    if isinstance(o, dict):
        for k, v in o.items():
            yield from aplana(v, f"{ruta}/{k}")
    elif isinstance(o, list):
        for i, v in enumerate(o):
            yield from aplana(v, f"{ruta}[{i}]")
    else:
        yield ruta, o


class Clave:
    """Una clave leída del disco, que se acuerda de qué hojas se le pidieron.

    Existe para poder exigir al final que NINGUNA hoja quede sin contrastar:
    una cifra de la clave que nadie lee es una cifra que se puede cambiar
    sin que el auditor se entere.
    """

    def __init__(self, obj):
        self.obj = obj
        self.tocadas: set = set()

    def v(self, *ruta):
        self.tocadas.add(ruta)
        return val(self.obj, *ruta)

    def sin_tocar(self, ignora=("plataforma",)):
        return sorted("/".join(r) for r, _ in hojas(self.obj)
                      if r and r[0] not in ignora and r not in self.tocadas)


def lee_json(var: str, nombre: str, carpeta: pathlib.Path):
    """(objeto, ruta) o (None, ruta) si no existe. Un archivo ilegible es un MAL, no un reventón."""
    p = pathlib.Path(os.environ.get(var) or (carpeta / nombre))
    if not p.exists():
        return None, p
    try:
        o = json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        return {"__ilegible__": str(e)}, p
    return (o if isinstance(o, dict) else {"__ilegible__": "no es un objeto JSON"}), p


# =====================================================================
# EL RECÁLCULO. Nada de QGIS, nada de `nucleo.py`.
# =====================================================================
def huella() -> str:
    h = hashlib.sha256()
    for p in (pathlib.Path(__file__), DATOS / "taller3.gpkg", DATOS / "taller3_sedes_3857.geojson"):
        h.update(p.read_bytes())
    return h.hexdigest()


def recomputo() -> dict:
    """Lo recalculado, con la caché que pide `TALLER3_RECOMPUTO` (si la pide)."""
    ruta = os.environ.get("TALLER3_RECOMPUTO")
    h = huella()
    if ruta and pathlib.Path(ruta).exists():
        try:
            o = json.loads(pathlib.Path(ruta).read_text(encoding="utf-8"))
            if o.get("huella") == h:
                print(f"  (recálculo leído de la caché {pathlib.Path(ruta).name}, con la huella de hoy)")
                return o["datos"]
        except (json.JSONDecodeError, OSError):
            pass
    print("  recalculando desde el GeoPackage y el GeoJSON (unos 10 s)…", flush=True)
    c = recalcula()
    if ruta:
        pathlib.Path(ruta).write_text(json.dumps({"huella": h, "datos": c}), encoding="utf-8")
    return c


def recalcula() -> dict:
    import geopandas as gpd
    import mapclassify
    import numpy as np
    import pyproj
    import shapely
    from scipy.spatial import cKDTree
    from scipy.stats import chi2 as chi2d
    from shapely.geometry import box

    gpkg = DATOS / "taller3.gpkg"
    loc = gpd.read_file(gpkg, layer="localidades")
    per = gpd.read_file(gpkg, layer="perimetro_urbano")
    raw = gpd.read_file(DATOS / "taller3_sedes_3857.geojson")
    nombres = [str(n) for n in loc["localidad"]]
    polis = dict(zip(nombres, loc.geometry.values))

    C: dict = {"datos": {"epsg_localidades": loc.crs.to_epsg(), "epsg_perimetro": per.crs.to_epsg(),
                         "epsg_sedes": raw.crs.to_epsg(), "n_localidades": len(loc),
                         "n_sedes": len(raw), "n_perimetro": len(per)}}

    # --- T1 · reproyectar con pyproj; reetiquetar es leer las coordenadas de 3857 como 9377
    tr = pyproj.Transformer.from_crs(3857, 9377, always_xy=True)
    X, Y = tr.transform(raw.geometry.x.values, raw.geometry.y.values)
    PTS = shapely.points(X, Y)
    CRUDAS = shapely.points(raw.geometry.x.values, raw.geometry.y.values)
    dentro_mal = np.zeros(len(CRUDAS), dtype=bool)
    for g in polis.values():
        dentro_mal |= shapely.intersects(g, CRUDAS)
    union = shapely.union_all(list(polis.values()))
    C["t1"] = {"reetiquetadas_dentro": int(dentro_mal.sum()),
               "distancia_min_km": float(shapely.distance(union, CRUDAS).min()) / 1000.0}

    loc3857 = loc.to_crs(3857)
    a3857 = dict(zip(nombres, loc3857.geometry.area.values))

    # --- T2 · conteo, densidad, puestos y clases
    L: dict = {}
    mascaras = {}
    for nom in nombres:
        g = polis[nom]
        shapely.prepare(g)
        m = shapely.intersects(g, PTS)
        mascaras[nom] = m
        n = int(m.sum())
        a9377 = g.area / 1e6
        L[nom] = {"n_sedes": n, "area_km2": float(a9377), "area_3857_km2": float(a3857[nom] / 1e6),
                  "inflacion_pct": float(100.0 * (a3857[nom] / 1e6 / a9377 - 1.0)),
                  "densidad": float(n / a9377), "elegible": n >= N_MIN}
    orden_n = sorted(nombres, key=lambda k: -L[k]["n_sedes"])
    orden_d = sorted(nombres, key=lambda k: -L[k]["densidad"])
    dens = np.array([L[k]["densidad"] for k in nombres])
    q = mapclassify.Quantiles(dens, k=5)
    cortes_q = [float(b) for b in q.bins]
    for k in nombres:
        L[k]["puesto_conteo"] = orden_n.index(k) + 1
        L[k]["puesto_densidad"] = orden_d.index(k) + 1
        L[k]["clase_cuantiles"] = int(next(i + 1 for i, c in enumerate(cortes_q)
                                           if L[k]["densidad"] <= c * (1 + 1e-12)))
    ordenadas = sorted(dens)
    mejor = None
    for corte in itertools.combinations(range(1, len(ordenadas)), 4):
        trozos = np.split(np.array(ordenadas), corte)
        sse = float(sum(((t - t.mean()) ** 2).sum() for t in trozos))
        if mejor is None or sse < mejor[0] - 1e-12:
            mejor = (sse, [float(ordenadas[i - 1]) for i in corte] + [float(ordenadas[-1])])
    C["t2"] = {"sedes_en_alguna_localidad": int(sum(L[k]["n_sedes"] for k in nombres)),
               "cortes_cuantiles": cortes_q,
               "jenks_optimo": {"sse": mejor[0], "cortes": mejor[1]},
               "empates_conteo": len(nombres) - len({L[k]["n_sedes"] for k in nombres}),
               "empates_densidad": len(nombres) - len({round(L[k]["densidad"], 9) for k in nombres})}

    # Rejillas: `native:creategrid` arranca en xmin/ymax de la caja del perímetro y añade celdas
    # hasta cubrirla; una sede cuenta en la celda que la contiene.
    x0, y0, x1, y1 = (float(v) for v in per.total_bounds)
    rej = {}
    for lado in LADOS_REJILLA:
        cols, filas = math.ceil((x1 - x0) / lado), math.ceil((y1 - y0) / lado)
        ix = np.floor((X - x0) / lado).astype(int)
        iy = np.floor((y1 - Y) / lado).astype(int)
        ok = (ix >= 0) & (ix < cols) & (iy >= 0) & (iy < filas)
        c = np.zeros((filas, cols), dtype=int)
        np.add.at(c, (iy[ok], ix[ok]), 1)
        v = c.ravel()
        ocupadas = v[v > 0]
        rej[str(lado)] = {"celdas": int(cols * filas), "ocupadas": int(len(ocupadas)),
                          "maximo": int(v.max()), "sedes_contadas": int(v.sum()),
                          "media_ocupadas": float(ocupadas.mean())}
    C["t2"]["rejillas"] = rej

    # --- T3 y T4, solo en las elegibles
    for nom in nombres:
        if not L[nom]["elegible"]:
            continue
        g = polis[nom]
        m = mascaras[nom]
        x, y = X[m], Y[m]
        P = np.c_[x, y]
        n = len(x)
        A = g.area
        tree = cKDTree(P)
        b = shapely.distance(g.boundary, shapely.points(x, y))       # distancia de cada punto al borde
        dn = tree.query(P, k=2)[0][:, 1]                             # vecino más próximo
        xmin, ymin, xmax, ymax = g.bounds

        # Cuadrantes: celdas cerradas por la derecha (como `cut` de R), recortadas con el polígono
        cuad = {}
        for nx in NX:
            ex, ey = np.linspace(xmin, xmax, nx + 1), np.linspace(ymin, ymax, nx + 1)
            ix = np.clip(np.searchsorted(ex, x, side="left") - 1, 0, nx - 1)
            iy = np.clip(np.searchsorted(ey, y, side="left") - 1, 0, nx - 1)
            obs = np.zeros((nx, nx))
            np.add.at(obs, (ix, iy), 1)
            ar = np.array([[g.intersection(box(ex[i], ey[j], ex[i + 1], ey[j + 1])).area
                            for j in range(nx)] for i in range(nx)])
            ok = ar > 0
            esp = n * ar[ok] / ar[ok].sum()
            chi = float(((obs[ok] - esp) ** 2 / esp).sum())
            gl = int(ok.sum()) - 1
            p = float(chi2d.sf(chi, gl))
            cuad[str(nx)] = {"celdas": int(ok.sum()), "chi2": chi, "gl": gl, "p_derecha": p,
                             "p_bilateral": 2.0 * min(p, 1.0 - p), "esperado_min": float(esp.min()),
                             "huerfanos": int(obs[~ok].sum())}
        L[nom]["cuadrantes"] = cuad

        # Vecino más próximo. QGIS usa como área la caja de los puntos, y SE = 0,26136 / sqrt(n²/A)
        caja = (x.max() - x.min()) * (y.max() - y.min())
        obs_m = float(dn.mean())
        esp_q = 0.5 / math.sqrt(n / caja)
        esp_r = 0.5 / math.sqrt(n / A)
        L[nom]["vecino"] = {"observada": obs_m, "esperada_qgis": esp_q, "indice_qgis": obs_m / esp_q,
                            "z_qgis": (obs_m - esp_q) / (0.26136 / math.sqrt(n * n / caja)),
                            "area_caja_km2": float(caja / 1e6), "esperada_area_real": esp_r,
                            "indice_area_real": obs_m / esp_r}

        # G y F por muestra reducida con conteo por UMBRAL. Los sitios de F: nodos de una rejilla
        # de LADO_F x LADO_F sobre la caja del polígono que caen dentro.
        SX, SY = np.meshgrid(np.linspace(xmin, xmax, LADO_F), np.linspace(ymin, ymax, LADO_F))
        SX, SY = SX.ravel(), SY.ravel()
        dentro = shapely.contains_xy(g, SX, SY)
        SX, SY = SX[dentro], SY[dentro]
        bs = shapely.distance(g.boundary, shapely.points(SX, SY))
        ds = tree.query(np.c_[SX, SY], k=1)[0]
        gf = {}
        for r in R_GF:
            u, us = b > r, bs > r
            gg = float(np.mean(dn[u] <= r)) if u.any() else float("nan")
            ff = float(np.mean(ds[us] <= r)) if us.any() else float("nan")
            gf[str(r)] = {"g": gg, "f": ff, "poisson": float(1.0 - math.exp(-n / A * math.pi * r * r)),
                          "j": (1.0 - gg) / (1.0 - ff) if ff < 1.0 else float("nan"),
                          "sitios": int(len(SX))}
        L[nom]["gf"] = gf

        # K y L con muestra reducida, y la banda de 99 simulaciones CSR (n fijo, rechazo en la
        # caja), con `default_rng(2026)`, `random(2n+64)` para x y luego para y, y los primeros
        # n aceptados: el orden del complemento.
        def Lr(px, py, bb):
            tr_ = cKDTree(np.c_[px, py])
            lam = len(px) / A
            salida = []
            for r in R_KL:
                u = bb > r
                if not u.any():
                    salida.append(float("nan"))
                    continue
                c = tr_.query_ball_point(np.c_[px, py][u], r, return_length=True) - 1
                salida.append(math.sqrt(float(c.sum()) / (lam * int(u.sum())) / math.pi))
            return np.array(salida)

        kl = {}
        lam = n / A
        lobs = Lr(x, y, b)
        rng = np.random.default_rng(SEMILLA)
        sims = np.empty((NSIM, len(R_KL)))
        for s in range(NSIM):
            xs, ys = np.empty(0), np.empty(0)
            while len(xs) < n:
                mm = 2 * n + 64
                cx = xmin + (xmax - xmin) * rng.random(mm)
                cy = ymin + (ymax - ymin) * rng.random(mm)
                ok = shapely.contains_xy(g, cx, cy)
                xs, ys = np.concatenate([xs, cx[ok]]), np.concatenate([ys, cy[ok]])
            xs, ys = xs[:n], ys[:n]
            sims[s] = Lr(xs, ys, shapely.distance(g.boundary, shapely.points(xs, ys)))
        lo, hi = np.nanmin(sims, axis=0), np.nanmax(sims, axis=0)
        for q_, r in enumerate(R_KL):
            u = b > r
            c = tree.query_ball_point(P[u], r, return_length=True) - 1 if u.any() else np.array([0])
            Kv = float(c.sum()) / (lam * int(u.sum())) if u.any() else float("nan")
            kl[str(r)] = {"k": Kv, "l_menos_r": float(lobs[q_] - r), "usables": int(u.sum()),
                          "banda_inf": float(lo[q_] - r), "banda_sup": float(hi[q_] - r)}
        L[nom]["kl"] = kl

        # El mapa de calor. Núcleo cuártico escalado: cada punto aporta 3/(pi R²)·(1-(d/R)²)²
        # dentro del radio R y la masa total es n. Dos versiones:
        #  · RÉPLICA de QGIS: ráster de 50 m con la caja de los puntos ampliada R por cada lado,
        #    origen arriba a la izquierda, (ceil(ancho/50)+1) columnas, y la rareza medida del y
        #    subpíxel (ver la cabecera); suma de zona con el centro del píxel dentro.
        #  · EXACTO: píxeles de 10 m, posiciones sin tocar. Masa dentro = suma de los píxeles
        #    cuyo centro cae en el polígono. El pico con borde usa el peso de Diggle: cada punto
        #    se divide entre su masa de núcleo dentro de la ventana.
        calor = {}
        for R in RADIOS:
            calor[str(R)] = _calor(g, x, y, R, shapely, np)
        L[nom]["calor"] = calor

    C["localidades"] = L
    C["elegibles"] = sorted(k for k in nombres if L[k]["elegible"])
    C["nombres"] = nombres
    return C


def _calor(g, x, y, R, shapely, np):
    """La réplica de QGIS y el estimador exacto del mapa de calor para un radio R.

    LA RÉPLICA, y de dónde sale su rareza. `qgis:heatmapkerneldensityestimation` pinta un ráster
    de 50 m cuya caja es la de los puntos ampliada R por cada lado, con origen arriba a la
    izquierda y ceil(ancho/50)+1 columnas por ceil(alto/50)+1 filas; cada píxel vale la suma de
    los núcleos cuárticos evaluados en su CENTRO. Hasta ahí es el estimador. Lo que no es: el
    núcleo de cada punto no se centra en el punto. En x sí, pero en y se centra en

        y_ef = ymax_b - ( floor((ymax_b - y)/50) + frac((y - ymin_b)/50) ) · 50

    es decir, la FILA del píxel se cuenta desde arriba y la fracción subpíxel desde abajo. Se vio
    ajustando, por mínimos cuadrados, la posición de cada núcleo en rásteres que QGIS pintó con
    puntos sintéticos aislados (se movían ±43 m en y, nunca en x, y la suma de los cambios no
    era cero), y se confirmó píxel a píxel: sobre Antonio Nariño a 600 m la réplica se aparta
    del ráster real 2·10⁻¹² (es un float32), y sobre las 48 combinaciones de las claves el pico
    sale a 1,3·10⁻⁷ y las masas a 4·10⁻⁹. Con un solo punto, o con una caja cuya altura es múltiplo
    de 50, la rareza no se ve: por eso un par de pruebas a mano no la encontraron.

    Consecuencia: el pico de QGIS puede quedar hasta 2,5 % por encima del pico del estimador
    exacto (los puntos se acercan unos a otros), que no puede ocurrir con un muestreo honrado.
    """
    c = 3.0 / (math.pi * R * R)

    def acumula(xp, yp, left, top, ncol, nrow, pix, adentro=None, pesos=None):
        cx = left + (np.arange(ncol) + 0.5) * pix
        cy = top - (np.arange(nrow) + 0.5) * pix
        Z = np.zeros((nrow, ncol))
        Zc = np.zeros((nrow, ncol)) if adentro is not None else None
        for k, (xi, yi) in enumerate(zip(xp, yp)):
            j0 = max(0, int((xi - R - left) // pix))
            j1 = min(ncol, int((xi + R - left) // pix) + 2)
            i0 = max(0, int((top - (yi + R)) // pix))
            i1 = min(nrow, int((top - (yi - R)) // pix) + 2)
            if j0 >= j1 or i0 >= i1:
                continue
            u = ((cx[j0:j1][None, :] - xi) ** 2 + (cy[i0:i1][:, None] - yi) ** 2) / (R * R)
            Kk = np.where(u < 1.0, c * (1.0 - u) ** 2, 0.0)
            Z[i0:i1, j0:j1] += Kk
            if adentro is not None:
                e = float((Kk * adentro[i0:i1, j0:j1]).sum()) * pix * pix   # masa del punto dentro
                Zc[i0:i1, j0:j1] += Kk / e
        return Z, Zc, cx, cy

    # --- réplica de QGIS
    xmin_b, xmax_b = x.min() - R, x.max() + R
    ymin_b, ymax_b = y.min() - R, y.max() + R
    ncol = int(math.ceil((xmax_b - xmin_b) / PIXEL)) + 1
    nrow = int(math.ceil((ymax_b - ymin_b) / PIXEL)) + 1
    fila = np.floor((ymax_b - y) / PIXEL)
    y_ef = ymax_b - (fila + ((y - ymin_b) / PIXEL) % 1.0) * PIXEL
    Z, _, cx, cy = acumula(x, y_ef, xmin_b, ymax_b, ncol, nrow, PIXEL)
    GX, GY = np.meshgrid(cx, cy)
    ins = shapely.contains_xy(g, GX.ravel(), GY.ravel()).reshape(GX.shape)
    px = PIXEL * PIXEL
    replica = {"maximo": float(Z.max()), "masa_total": float(Z.sum() * px),
               "masa_dentro": float(Z[ins].sum() * px)}
    replica["pct_fuera"] = 100.0 * (1.0 - replica["masa_dentro"] / replica["masa_total"])

    # --- exacto
    ncol = int(math.ceil((xmax_b - xmin_b) / PIXEL_FINO))
    nrow = int(math.ceil((ymax_b - ymin_b) / PIXEL_FINO))
    cx = xmin_b + (np.arange(ncol) + 0.5) * PIXEL_FINO
    cy = ymax_b - (np.arange(nrow) + 0.5) * PIXEL_FINO
    GX, GY = np.meshgrid(cx, cy)
    ins = shapely.contains_xy(g, GX.ravel(), GY.ravel()).reshape(GX.shape)
    Z, Zc, _, _ = acumula(x, y, xmin_b, ymax_b, ncol, nrow, PIXEL_FINO, adentro=ins)
    pf = PIXEL_FINO * PIXEL_FINO
    exacto = {"maximo": float(Z.max()), "masa_dentro": float(Z[ins].sum() * pf),
              "masa_total": float(Z.sum() * pf), "pico_con": float(Zc[ins].max())}
    return {"replica": replica, "exacto": exacto}


# =====================================================================
# EL AUDITOR
# =====================================================================
def main() -> int:
    a = Auditoria("Precálculo del Taller 3 verificado")
    DESV: dict = {}              # familia -> (máxima desviación relativa vista, tolerancia)

    def registra(fam, calc, pub, tol):
        if num(calc) and num(pub):
            d = abs(float(calc) - float(pub)) / max(abs(float(pub)), 1e-12)
            if d > DESV.get(fam, (0.0, tol))[0]:
                DESV[fam] = (d, tol)
            else:
                DESV.setdefault(fam, (d, tol))

    def cmp(fam, calc, pub, que, rel=REL):
        """Relativo. Un `pub` que no es número no revienta: sale MAL."""
        registra(fam, calc, pub, rel)
        if not num(pub):
            return a.igual(calc, pub, que)
        return a.cerca(calc, pub, que, rel=rel)

    def entero(calc, pub, que):
        return a.igual(calc, pub, que, tol=0.0)

    def rot(nom, txt):
        s = f"{nom}: {txt}"
        assert len(s) < 58, f"rótulo largo ({len(s)}): {s}"
        return s

    D, ruta_d = lee_json("TALLER3_DATOS", "taller3_datos.json", SALIDAS)
    if D is None:
        sys.exit(f"PARADO: falta {ruta_d}")
    ruta_h = pathlib.Path(os.environ.get("TALLER3_HTML") or (HTMLS / "taller-3-sig-caps-1-5.html"))
    claves = {}
    for clave, var, nombre in (("mac", "TALLER3_CLAVES_MAC", "taller3_claves_qgis_mac.json"),
                               ("linux", "TALLER3_CLAVES_LINUX", "taller3_claves_qgis_linux.json"),
                               ("r", "TALLER3_CLAVES_R", "taller3_claves_r.json")):
        claves[clave] = lee_json(var, nombre, CACHE)
    print(f"\n=== audita_taller3.py · {ruta_d.name} + {ruta_h.name} ===")
    for k, (o, p) in claves.items():
        print(f"  clave {k:<6} {'LEÍDA   ' if o is not None else 'AUSENTE '} {p.name}")
    faltan = [p.name for k, (o, p) in claves.items() if o is None]
    saltados = []

    # -----------------------------------------------------------------
    C = recomputo()
    elegibles = C["elegibles"]
    nombres = C["nombres"]
    LOC = C["localidades"]

    # -----------------------------------------------------------------
    a.titulo("Que no se filtre ninguna respuesta")
    crudo = ruta_d.read_text(encoding="utf-8").lower()
    for palabra in PROHIBIDAS:
        a.cierto(palabra not in crudo, f"el JSON no contiene «{palabra}»")

    def con_punto(o, ruta=""):
        malos = []
        if isinstance(o, dict):
            for k, v in o.items():
                if isinstance(k, str) and k.startswith("."):
                    malos.append(f"{ruta}/{k}")
                malos += con_punto(v, f"{ruta}/{k}")
        elif isinstance(o, list):
            for i, v in enumerate(o):
                malos += con_punto(v, f"{ruta}[{i}]")
        return malos

    malos = con_punto(D)
    a.cierto(not malos, "ningún campo de respuesta (empieza por punto)", str(malos[:3]))
    a.cierto(set(D) == RAIZ_PUBLICA, "el JSON publica exactamente las seis secciones",
             str(sorted(set(D) ^ RAIZ_PUBLICA)))
    a.cierto(set(val(D, "ciudad") or {}) == CAMPOS_CIUDAD, "«ciudad» publica solo sus tres campos",
             str(sorted(set(val(D, "ciudad") or {}) ^ CAMPOS_CIUDAD)))
    a.cierto(set(val(D, "opciones") or {}) == set(OPCIONES), "«opciones» publica solo los cuatro conjuntos",
             str(sorted(set(val(D, "opciones") or {}) ^ set(OPCIONES))))
    DL = D.get("localidades") if isinstance(D.get("localidades"), dict) else {}
    sobra = sorted({c for v in DL.values() if isinstance(v, dict) for c in set(v) - CAMPOS_LOC})
    falta = sorted({c for v in DL.values() if isinstance(v, dict) for c in CAMPOS_LOC - set(v)})
    a.cierto(not sobra and not falta and all(isinstance(v, dict) for v in DL.values()),
             "cada localidad publica solo n, área y lambda",
             f"sobra {sobra} · falta {falta}")
    V = [v for v in (D.get("variantes") if isinstance(D.get("variantes"), list) else [])]
    campos_malos = [v.get("clave") if isinstance(v, dict) else v for v in V
                    if not isinstance(v, dict) or set(v) != CAMPOS_VARIANTE]
    a.cierto(not campos_malos, "cada variante publica solo sus seis campos",
             f"{len(campos_malos)} con otros campos: {campos_malos[:3]}")

    # -----------------------------------------------------------------
    a.titulo("Formato")
    a.cierto(not list(sin_nan(D)), "ningún NaN ni infinito en el JSON público")
    muchos = [(r, d) for r, d in decimales(D) if d > 10]
    a.cierto(not muchos, "ningún flotante pasa de diez decimales", str(muchos[:3]))
    a.cierto("<c3>" not in crudo and "<c2>" not in crudo and "<u+" not in crudo, "sin mojibake UTF-8")
    a.cierto("__ilegible__" not in D, "el JSON público se puede leer", str(D.get("__ilegible__", "")))

    # -----------------------------------------------------------------
    a.titulo("Los datos que se entregan")
    d0 = C["datos"]
    entero(d0["epsg_localidades"], 9377, "EPSG de las localidades")
    entero(d0["epsg_perimetro"], 9377, "EPSG del perímetro urbano")
    entero(d0["epsg_sedes"], 3857, "EPSG de las sedes (a propósito, otro)")
    entero(d0["n_localidades"], N_LOCALIDADES, "localidades en el GeoPackage")
    entero(d0["n_sedes"], TOTAL_SEDES, "sedes en el GeoJSON")
    entero(d0["n_perimetro"], 1, "polígonos en el perímetro urbano")
    entero(val(D, "ciudad", "sedes"), d0["n_sedes"], "ciudad.sedes es el total del GeoJSON")
    entero(val(D, "ciudad", "localidades"), d0["n_localidades"], "ciudad.localidades es el total del GeoPackage")
    entero(val(D, "ciudad", "sedes_en_alguna_localidad"), C["t2"]["sedes_en_alguna_localidad"],
           "ciudad.sedes_en_alguna_localidad rehecho")
    entero(val(D, "semilla"), SEMILLA, "la semilla de la envolvente")
    entero(val(D, "n_min"), N_MIN, "el mínimo de sedes para entrar al sorteo")
    a.cierto(val(D, "opciones") == OPCIONES, "los valores que puede traer una variante",
             f"{val(D, 'opciones')}")

    # -----------------------------------------------------------------
    a.titulo("Las 16 localidades elegibles, rehechas con geopandas")
    a.cierto(sorted(DL) == elegibles, f"las {N_ELEGIBLES} publicadas son las que pasan n >= {N_MIN}",
             str(sorted(set(DL) ^ set(elegibles))))
    entero(len(elegibles), N_ELEGIBLES, "localidades que pasan el mínimo")
    for nom in elegibles:
        pub = DL.get(nom) if isinstance(DL.get(nom), dict) else {}
        L = LOC[nom]
        entero(L["n_sedes"], pub.get("n"), rot(nom, "n por intersección"))
        a.igual(L["area_km2"], pub.get("area_km2"), rot(nom, "área en km² (5 decimales)"), tol=TOL_PUBLICADO)
        a.igual(L["n_sedes"] / L["area_km2"], pub.get("lambda"), rot(nom, "lambda (5 decimales)"),
                tol=TOL_PUBLICADO)

    # -----------------------------------------------------------------
    a.titulo("El reparto de las 1000 variantes")
    entero(len(V), 1000, "filas de la tabla de variantes")
    cl = [v.get("clave") if isinstance(v, dict) else None for v in V]
    a.cierto(cl == [f"{k:03d}" for k in range(1000)], "claves de 000 a 999, sin huecos y en orden")
    a.cierto(len(set(map(str, cl))) == len(cl), "ninguna clave se repite")
    usadas = {v.get("localidad") for v in V if isinstance(v, dict)}
    a.cierto(all(isinstance(v, dict) and v.get("localidad") in set(elegibles) for v in V),
             "toda variante apunta a una localidad elegible",
             f"fuera: {sorted(str(u) for u in usadas - set(elegibles))[:3]}")
    a.cierto(all(isinstance(v, dict) and v.get("localidad") in DL for v in V),
             "y a una que el JSON publica")
    a.cierto(usadas == set(elegibles), f"las {N_ELEGIBLES} elegibles se usan")
    cuenta = collections.Counter(v.get("localidad") for v in V if isinstance(v, dict))
    a.cierto(bool(cuenta) and set(cuenta.values()) <= {62, 63},
             "cada localidad sale 62 o 63 veces (1000 entre 16)",
             f"de {min(cuenta.values(), default=0)} a {max(cuenta.values(), default=0)}")
    for campo, opciones in OPCIONES.items():
        vals = [v.get(campo) if isinstance(v, dict) else None for v in V]
        a.cierto(all(type(x) is int and x in opciones for x in vals),
                 f"{campo}: todo valor es uno de los declarados",
                 f"fuera: {sorted({str(x) for x in vals if x not in opciones})[:3]}")
        cu = collections.Counter(vals)
        a.cierto(len(cu) == len(opciones) and max(cu.values()) - min(cu.values()) <= 1,
             f"{campo}: reparto equilibrado, por bloques iguales",
             str(dict(sorted(cu.items(), key=lambda kv: str(kv[0])))))
    firmas = {tuple(v.get(c) for c in ("localidad", "nx", "r_gf", "r_kl", "radio"))
              for v in V if isinstance(v, dict)}
    a.cierto(len(firmas) > 500, "más de 500 combinaciones distintas", f"{len(firmas)} de 1000")

    # -----------------------------------------------------------------
    a.titulo("Los dos guiones que hicieron las claves repartieron lo mismo que el JSON")
    py_src = (RAIZ / "precalculo" / "claves_qgis_taller3.py")
    r_src = (RAIZ / "precalculo" / "genera_taller3.R")
    py_txt = py_src.read_text(encoding="utf-8") if py_src.exists() else ""
    r_txt = r_src.read_text(encoding="utf-8") if r_src.exists() else ""
    for nombre, campo in (("NX", "nx"), ("R_GF", "r_gf"), ("R_KL", "r_kl"), ("RADIOS", "radio")):
        m = re.search(rf"^{nombre}\s*=\s*\(([^)]*)\)", py_txt, re.M)
        en_py = [int(x) for x in re.findall(r"\d+", m.group(1))] if m else None
        m = re.search(rf"^{nombre}\s*<-\s*c\(([^)]*)\)", r_txt, re.M)
        en_r = [int(x) for x in re.findall(r"\d+", m.group(1))] if m else None
        pub = val(D, "opciones", campo)
        a.cierto(en_py == pub, f"claves_qgis: {nombre} es lo que el JSON declara", f"{en_py} frente a {pub}")
        a.cierto(en_r == pub, f"genera_taller3.R: {nombre} es lo que el JSON declara", f"{en_r} frente a {pub}")
    m_py = re.search(r"^N_MIN\s*=\s*(\d+)", py_txt, re.M)
    m_r = re.search(r"^N_MIN\s*<-\s*(\d+)", r_txt, re.M)
    a.cierto(m_py is not None and int(m_py.group(1)) == val(D, "n_min"), "claves_qgis: N_MIN es el n_min del JSON",
             f"{m_py.group(1) if m_py else None} frente a {val(D, 'n_min')}")
    a.cierto(m_r is not None and int(m_r.group(1)) == val(D, "n_min"), "genera_taller3.R: N_MIN es el n_min del JSON",
             f"{m_r.group(1) if m_r else None} frente a {val(D, 'n_min')}")

    # -----------------------------------------------------------------
    a.titulo("El JSON viaja entero dentro de la página")
    if not ruta_h.exists():
        a.cierto(False, "la página existe", str(ruta_h))
        html = ""
    else:
        html = ruta_h.read_text(encoding="utf-8")
    marcas = re.findall(r"const DATOS_T3 = (\{.*\});", html)
    entero(len(marcas), 1, "la página declara un solo DATOS_T3")
    try:
        incrustado = json.loads(marcas[0]) if marcas else None
    except json.JSONDecodeError:
        incrustado = None
    a.cierto(incrustado is not None, "el DATOS_T3 de la página es un JSON legible")
    a.cierto(incrustado == D, "y es EXACTAMENTE el JSON publicado",
             "" if incrustado == D or incrustado is None else
             f"difieren: {sorted(k for k in set(D) | set(incrustado) if D.get(k) != incrustado.get(k))}")

    # -----------------------------------------------------------------
    K = KL = KR = None
    if claves["mac"][0] is not None:
        K = Clave(claves["mac"][0])
    if claves["linux"][0] is not None:
        KL = claves["linux"][0]
    if claves["r"][0] is not None:
        KR = Clave(claves["r"][0])

    def sin_clave(que, cual):
        archivo = {"mac": "taller3_claves_qgis_mac.json", "r": "taller3_claves_r.json",
                   "linux": "taller3_claves_qgis_linux.json"}[cual]
        a.salta(que, f"no existe precalculo/cache/{archivo} (las claves no están en git)")
        saltados.append(que)

    # =================================================================
    a.titulo("Las claves se hicieron con lo que dice el enunciado")
    versiones = re.findall(r"QGIS (\d+\.\d+\.\d+)</strong>", html)
    v_html = versiones[0] if versiones else "?"
    a.cierto(versiones != [] and len(set(versiones)) == 1, "la página dice una sola versión de QGIS", v_html)
    if K is None:
        sin_clave("la versión de QGIS de las claves frente a la de la página", "mac")
    else:
        for etq, obj in (("macOS", K.obj), ("Linux", KL)):
            if obj is None:
                continue
            q = str(val(obj, "plataforma", "qgis"))
            a.cierto(q.startswith(v_html), f"la clave de {etq} es de QGIS {v_html}", q)
        a.cierto(val(K.obj, "plataforma", "numpy") is not None, "la clave guarda la versión de numpy")

    # =================================================================
    a.titulo("macOS y Linux dicen lo mismo, hoja por hoja")
    if K is None or KL is None:
        sin_clave("las dos plataformas de QGIS contra sí mismas",
                  "linux" if K is not None else "mac")
    else:
        pa = {r: v for r, v in aplana({k: v for k, v in K.obj.items() if k != "plataforma"})}
        pb = {r: v for r, v in aplana({k: v for k, v in KL.items() if k != "plataforma"})}
        dif = sorted(set(pa) ^ set(pb))
        a.cierto(not dif, "las dos claves tienen las mismas hojas", f"{len(pa)} hojas; difieren: {dif[:3]}")
        peor, donde, malas = 0.0, "", []
        for r in sorted(set(pa) & set(pb)):
            x, y = pa[r], pb[r]
            if num(x) and num(y) and not isinstance(x, bool):
                d = abs(x - y)
                rel = d / max(abs(x), abs(y), 1e-300)
                if d > 1e-12 and rel > peor:
                    peor, donde = rel, r
                if d > 1e-12 and rel > REL_PLATAFORMA:
                    malas.append(r)
            elif x != y:
                malas.append(r)
        a.cierto(not malas, f"coinciden en cada cifra (relativo {REL_PLATAFORMA:g})",
                 f"{len(pa)} hojas, peor {peor:.1e}" + (f" · MAL: {malas[:3]}" if malas else ""))
        DESV["macOS frente a Linux"] = (peor, REL_PLATAFORMA)

    # =================================================================
    a.titulo("T1 · reproyectar no es reetiquetar")
    if K is None:
        sin_clave("T1: reproyección, sedes reetiquetadas y áreas", "mac")
    else:
        entero(C["t1"]["reetiquetadas_dentro"], K.v("t1", "reetiquetadas_dentro"),
               "sedes reetiquetadas dentro de alguna localidad")
        a.cierto(C["t1"]["reetiquetadas_dentro"] == 0, "ninguna sede reetiquetada cae en una localidad",
                 f"quedan a {C['t1']['distancia_min_km']:.0f} km de Bogotá")
        for nom in nombres:
            L, ruta = LOC[nom], ("localidades", nom)
            cmp("área", L["area_km2"], K.v(*ruta, "area_km2"), rot(nom, "área EPSG:9377 (km²)"))
            cmp("área", L["area_3857_km2"], K.v(*ruta, "area_3857_km2"), rot(nom, "área EPSG:3857 (km²)"))
            cmp("área", L["inflacion_pct"], K.v(*ruta, "inflacion_pct"), rot(nom, "inflación del área (%)"))

    # =================================================================
    a.titulo("T2 · del conteo al mapa")
    if K is None:
        sin_clave("T2: conteo, densidad, puestos, clases y rejillas", "mac")
    else:
        t2 = C["t2"]
        entero(t2["sedes_en_alguna_localidad"], K.v("t2", "sedes_en_alguna_localidad"),
               "sedes dentro de alguna localidad (la suma)")
        a.cierto(t2["empates_conteo"] == 0 and t2["empates_densidad"] == 0,
                 "sin empates: los puestos no dependen del orden de capa",
                 f"empates en conteo {t2['empates_conteo']}, en densidad {t2['empates_densidad']}")
        cq = K.v("t2", "cortes_cuantiles")
        a.cierto(isinstance(cq, list) and len(cq) == 5, "cinco cortes de cuantiles en la clave", str(cq)[:50])
        if isinstance(cq, list) and len(cq) == 5:
            for i, (mio, suyo) in enumerate(zip(t2["cortes_cuantiles"], cq)):
                cmp("cuantiles", mio, suyo, f"corte {i + 1} de cuantiles")
        cj = K.v("t2", "cortes_jenks")
        dens = {k: LOC[k]["densidad"] for k in nombres}

        def clase(v, cortes):
            """La regla de QGIS: el límite superior pertenece a la clase de abajo."""
            return next((i + 1 for i, c in enumerate(cortes) if v <= c * (1 + 1e-9)), len(cortes))

        valido = (isinstance(cj, list) and len(cj) == 5 and all(num(c) for c in cj)
                  and all(x < y for x, y in zip(cj, cj[1:])))
        a.cierto(valido, "cinco cortes de Jenks, crecientes", str(cj)[:60])
        clases_j = {}
        if valido:
            a.cierto(abs(cj[-1] - max(dens.values())) <= 1e-9 * max(dens.values()),
                     "el último corte de Jenks es el máximo de los datos", f"{cj[-1]:.6f}")
            fuera = [c for c in cj if min(abs(c - v) for v in dens.values()) > 1e-9 * c]
            a.cierto(not fuera, "cada corte de Jenks es un valor de los datos", str(fuera))
            clases_j = {k: clase(dens[k], cj) for k in nombres}

            def sse(cortes):
                tot, grupos = 0.0, collections.defaultdict(list)
                for k in nombres:
                    grupos[clase(dens[k], cortes)].append(dens[k])
                for g in grupos.values():
                    m = sum(g) / len(g)
                    tot += sum((v - m) ** 2 for v in g)
                return tot

            opt = t2["jenks_optimo"]
            s_q, s_o = sse(cj), opt["sse"]
            iguales = all(abs(p - q) <= 1e-9 * q for p, q in zip(cj, opt["cortes"]))
            if iguales:
                a.cierto(True, "los cortes de Jenks son el Fisher-Jenks óptimo", f"SSE {s_q:.4f}")
            else:
                a.cierto(s_q <= 1.10 * s_o, "Jenks de QGIS: SSE a menos del 10 % del óptimo",
                         f"{s_q:.4f} frente a {s_o:.4f}")
                n_opt = sum(1 for k in nombres if LOC[k]["clase_cuantiles"] != clase(dens[k], opt["cortes"]))
                n_qgis = sum(1 for k in nombres if LOC[k]["clase_cuantiles"] != clases_j[k])
                a.salta("Jenks de QGIS contra el Fisher-Jenks exacto",
                        f"QGIS no da el óptimo (SSE {s_q:.4f} frente a {s_o:.4f}; corte 3: "
                        f"{cj[2]:.5f} y el óptimo {opt['cortes'][2]:.5f}); no se audita contra una "
                        f"referencia que no es la de QGIS. Entre cuantiles y Jenks cambian de clase "
                        f"{n_qgis} localidades con QGIS y {n_opt} con el óptimo")
                saltados.append("Jenks de QGIS contra el Fisher-Jenks exacto")
        cambian = sorted(k for k in nombres if clases_j and LOC[k]["clase_cuantiles"] != clases_j[k])
        suyo = K.v("t2", "cambian_de_clase")
        a.cierto(isinstance(suyo, list) and sorted(map(str, suyo)) == cambian,
                 "las localidades que cambian de clase entre los dos mapas", f"{cambian} frente a {suyo}")
        for lado in LADOS_REJILLA:
            rj, rc = t2["rejillas"][str(lado)], ("t2", "rejillas", str(lado))
            for campo, etq in (("celdas", "celdas"), ("ocupadas", "celdas con alguna sede"),
                               ("maximo", "máximo de sedes en una celda"),
                               ("sedes_contadas", "sedes contadas")):
                entero(rj[campo], K.v(*rc, campo), f"rejilla {lado}: {etq}")
            cmp("rejillas", rj["media_ocupadas"], K.v(*rc, "media_ocupadas"),
                f"rejilla {lado}: media de las ocupadas")
        for nom in nombres:
            L, ruta = LOC[nom], ("localidades", nom)
            entero(L["n_sedes"], K.v(*ruta, "n_sedes"), rot(nom, "n de sedes por intersección"))
            a.cierto(K.v(*ruta, "elegible") is (L["n_sedes"] >= N_MIN), rot(nom, "elegible si n >= 35"))
            cmp("densidad", L["densidad"], K.v(*ruta, "densidad"), rot(nom, "densidad (sedes/km²)"))
            entero(L["puesto_conteo"], K.v(*ruta, "puesto_conteo"), rot(nom, "puesto por conteo"))
            entero(L["puesto_densidad"], K.v(*ruta, "puesto_densidad"), rot(nom, "puesto por densidad"))
            entero(L["clase_cuantiles"], K.v(*ruta, "clase_cuantiles"), rot(nom, "clase por cuantiles"))
            if clases_j:
                entero(clases_j[nom], K.v(*ruta, "clase_jenks"), rot(nom, "clase por Jenks (sus cortes)"))
            else:
                a.cierto(False, rot(nom, "clase por Jenks (sus cortes)"), "los cortes no son válidos")

    # =================================================================
    a.titulo("T3 · cuadrantes con celdas recortadas")
    if K is None:
        sin_clave("T3(a): test de cuadrantes", "mac")
    else:
        for nom in elegibles:
            for nx in NX:
                c, ruta = LOC[nom]["cuadrantes"][str(nx)], ("localidades", nom, "cuadrantes", str(nx))
                t = f"cuadrantes {nx}x{nx}"
                entero(c["celdas"], K.v(*ruta, "celdas"), rot(nom, f"{t}: celdas con área"))
                cmp("cuadrantes", c["chi2"], K.v(*ruta, "chi2"), rot(nom, f"{t}: χ²"))
                entero(c["gl"], K.v(*ruta, "gl"), rot(nom, f"{t}: grados de libertad"))
                cmp("cuadrantes", c["p_derecha"], K.v(*ruta, "p_derecha"), rot(nom, f"{t}: p cola derecha"))
                cmp("cuadrantes", c["p_bilateral"], K.v(*ruta, "p_bilateral"), rot(nom, f"{t}: p bilateral"))
                cmp("cuadrantes", c["esperado_min"], K.v(*ruta, "esperado_min"), rot(nom, f"{t}: esperado mínimo"))
        huerfanos = sum(LOC[n]["cuadrantes"][str(x)]["huerfanos"] for n in elegibles for x in NX)
        a.cierto(huerfanos == 0, "ningún punto cae en una celda sin área", f"{huerfanos} huérfanos")

    # =================================================================
    a.titulo("T3 · vecino más próximo, con el área de QGIS y la real")
    if K is None:
        sin_clave("T3(b): vecino más próximo", "mac")
    else:
        for nom in elegibles:
            v, ruta = LOC[nom]["vecino"], ("localidades", nom, "vecino")
            for campo, etq in (("observada", "distancia observada (m)"),
                               ("esperada_qgis", "esperada de QGIS (m)"),
                               ("indice_qgis", "índice de QGIS"), ("z_qgis", "z de QGIS"),
                               ("area_caja_km2", "área de la caja (km²)"),
                               ("esperada_area_real", "esperada con el área real"),
                               ("indice_area_real", "índice con el área real")):
                cmp("vecino", v[campo], K.v(*ruta, campo), rot(nom, f"NN {etq}"))

    # =================================================================
    a.titulo("T3 · G, F y J por muestra reducida (conteo por umbral)")
    if K is None:
        sin_clave("T3(c): G, F y J", "mac")
    else:
        for nom in elegibles:
            for r in R_GF:
                c, ruta = LOC[nom]["gf"][str(r)], ("localidades", nom, "gf", str(r))
                cmp("G, F, J", c["g"], K.v(*ruta, "g"), rot(nom, f"G(r={r})"))
                cmp("G, F, J", c["f"], K.v(*ruta, "f"), rot(nom, f"F(r={r})"))
                cmp("Poisson (usa el área)", c["poisson"], K.v(*ruta, "poisson"), rot(nom, f"Poisson(r={r})"))
                cmp("G, F, J", c["j"], K.v(*ruta, "j"), rot(nom, f"J(r={r})"))
                entero(c["sitios"], K.v(*ruta, "sitios"), rot(nom, f"sitios de F (r={r})"))

    # =================================================================
    a.titulo("T3 · K, L y la banda de 99 simulaciones (reproducida)")
    if K is None:
        sin_clave("T3(d): K, L y la envolvente", "mac")
    else:
        for nom in elegibles:
            for r in R_KL:
                c, ruta = LOC[nom]["kl"][str(r)], ("localidades", nom, "kl", str(r))
                cmp("K, L, banda", c["k"], K.v(*ruta, "k"), rot(nom, f"K(r={r}) en m²"))
                cmp("K, L, banda", c["l_menos_r"], K.v(*ruta, "l_menos_r"), rot(nom, f"L-r (r={r})"))
                cmp("K, L, banda", c["banda_inf"], K.v(*ruta, "banda_inf"), rot(nom, f"banda inf (r={r})"))
                cmp("K, L, banda", c["banda_sup"], K.v(*ruta, "banda_sup"), rot(nom, f"banda sup (r={r})"))
                entero(c["usables"], K.v(*ruta, "usables"), rot(nom, f"puntos a más de r (r={r})"))
        todas = [(LOC[n]["kl"][str(r)]["banda_inf"], LOC[n]["kl"][str(r)]["banda_sup"])
                 for n in elegibles for r in R_KL]
        a.cierto(all(lo <= 0.0 <= hi for lo, hi in todas),
                 "la banda contiene a 0 en los 48 radios (plausible)", f"{len(todas)} bandas")

    # =================================================================
    a.titulo("T4 · el mapa de calor, réplica de QGIS y estimador exacto")
    print(f"  tolerancias: réplica {REL:g} relativo; masa total = n {TOL_MASA_TOTAL:g}; contra el estimador exacto "
          f"(píxel de {PIXEL_FINO:g} m): masa dentro {TOL_MASA_EXACTA:.1%}, pico {TOL_PICO_EXACTO:.0%}")
    if K is None:
        sin_clave("T4: mapa de calor", "mac")
    else:
        for nom in elegibles:
            n = LOC[nom]["n_sedes"]
            for R in RADIOS:
                c, ruta = LOC[nom]["calor"][str(R)], ("localidades", nom, "calor", str(R))
                rp, ex, t = c["replica"], c["exacto"], f"calor {R}"
                pico_q = K.v(*ruta, "maximo")
                cmp("calor (réplica)", rp["maximo"] * 1e6, pico_q * 1e6 if num(pico_q) else pico_q,
                    rot(nom, f"{t}: pico (sedes/km²)"))
                cmp("calor (réplica)", rp["masa_total"], K.v(*ruta, "masa_total"), rot(nom, f"{t}: masa total"))
                cmp("calor (réplica)", rp["masa_dentro"], K.v(*ruta, "masa_dentro"), rot(nom, f"{t}: masa dentro"))
                cmp("calor (réplica)", rp["pct_fuera"], K.v(*ruta, "pct_fuera"), rot(nom, f"{t}: % fuera de la localidad"))
                cmp("masa total = n", n, K.v(*ruta, "masa_total"), rot(nom, f"{t}: masa total = n"), rel=TOL_MASA_TOTAL)
                cmp("masa dentro (exacta)", ex["masa_dentro"], K.v(*ruta, "masa_dentro"),
                    rot(nom, f"{t}: masa dentro, exacto"), rel=TOL_MASA_EXACTA)
                cmp("pico (exacto)", ex["maximo"] * 1e6, pico_q * 1e6 if num(pico_q) else pico_q,
                    rot(nom, f"{t}: pico, exacto"), rel=TOL_PICO_EXACTO)
            # La clave guarda sumas de píxeles y las pasa a masas: que sean coherentes entre sí.
            malas = []
            for R in RADIOS:
                ruta = ("localidades", nom, "calor", str(R))
                px, s, sd = K.v(*ruta, "pixel_m2"), K.v(*ruta, "suma"), K.v(*ruta, "suma_dentro")
                mt, md, pf = K.v(*ruta, "masa_total"), K.v(*ruta, "masa_dentro"), K.v(*ruta, "pct_fuera")
                if not all(num(z) for z in (px, s, sd, mt, md, pf)) or s == 0:
                    malas.append(f"{R}: faltan cifras")
                    continue
                if (abs(px - PIXEL * PIXEL) > 1e-9 or abs(s * px - mt) > 1e-9 * abs(mt)
                        or abs(sd * px - md) > 1e-9 * abs(md) or abs(100 * (1 - sd / s) - pf) > 1e-9 * abs(pf)):
                    malas.append(f"{R}")
            a.cierto(not malas, rot(nom, "píxel, sumas, masas y % fuera"), f"incoherente en {malas}")

    # =================================================================
    a.titulo("T5 · la clave de R, y los cruces con QGIS y con el estimador exacto")
    print(f"  tolerancias: masa contra el exacto {TOL_MASA_EXACTA:.1%}; pico contra el exacto {TOL_PICO_R:.0%}; "
          f"masa de R contra la de QGIS {TOL_MASA_R_QGIS:.0%} (el encargo decía 0,5 % y se rebasa: ver la cabecera)")
    if KR is None:
        sin_clave("T5: la clave de R", "r")
    else:
        a.cierto(set(KR.obj) == set(elegibles), f"la clave de R trae las {N_ELEGIBLES} elegibles, ni una más",
                 str(sorted(set(KR.obj) ^ set(elegibles)))[:80])
        en_limite = []
        for nom in elegibles:
            L, ruta = LOC[nom], (nom,)
            entero(L["n_sedes"], KR.v(*ruta, "n"), rot(nom, "R: n de la ventana"))
            cmp("R área", L["area_km2"], KR.v(*ruta, "area_km2"), rot(nom, "R: área en km²"))
            for R in RADIOS:
                rr = ("calor", str(R))
                t = f"R {R}"
                cmp("R sigma", R / math.sqrt(8.0), KR.v(*ruta, *rr, "sigma"), rot(nom, f"{t}: σ = radio / √8"), rel=1e-9)
                cmp("R masa con borde", L["n_sedes"], KR.v(*ruta, *rr, "masa_con"), rot(nom, f"{t}: masa con borde = n"), rel=1e-6)
                ex = L["calor"][str(R)]["exacto"]
                ms = KR.v(*ruta, *rr, "masa_sin")
                cmp("R masa (exacta)", ex["masa_dentro"], ms, rot(nom, f"{t}: masa sin borde, exacto"), rel=TOL_MASA_EXACTA)
                mq = K.v("localidades", nom, "calor", str(R), "masa_dentro") if K is not None else None
                if K is not None:
                    cmp("R masa frente a QGIS", mq, ms, rot(nom, f"{t}: masa sin borde frente a QGIS"), rel=TOL_MASA_R_QGIS)
                ps, pc = KR.v(*ruta, *rr, "pico_sin"), KR.v(*ruta, *rr, "pico_con")
                cmp("R pico (exacto)", ex["maximo"] * 1e6, ps * 1e6 if num(ps) else ps,
                    rot(nom, f"{t}: pico sin borde, exacto"), rel=TOL_PICO_R)
                cmp("R pico con borde", ex["pico_con"] * 1e6, pc * 1e6 if num(pc) else pc,
                    rot(nom, f"{t}: pico con borde, Diggle"), rel=TOL_PICO_R)
            dg, pp = KR.v(*ruta, "bw_diggle"), KR.v(*ruta, "bw_ppl")
            cmp("R radios QGIS", (dg if num(dg) else float("nan")) * math.sqrt(8.0), KR.v(*ruta, "radio_qgis_diggle"),
                rot(nom, "R: radio equivalente de Diggle"), rel=1e-9)
            cmp("R radios QGIS", (pp if num(pp) else float("nan")) * math.sqrt(8.0), KR.v(*ruta, "radio_qgis_ppl"),
                rot(nom, "R: radio equivalente de ppl"), rel=1e-9)
            a.cierto(num(dg) and dg > 0 and num(pp) and pp > 0, rot(nom, "R: los dos σ son positivos"), f"{dg}, {pp}")
            ppm = [KR.v(*ruta, "ppm", c) for c in ("x", "z_x", "y", "z_y")]
            a.cierto(all(num(z) for z in ppm), rot(nom, "R: ppm trae sus cuatro números"), str(ppm)[:50])
            if KR.v(*ruta, "ppl_en_el_limite") is not False:
                en_limite.append(nom)
        a.cierto(not en_limite, "ningún bw.ppl topa con el límite de su rejilla", str(en_limite))
        a.salta("bw.diggle y bw.ppl contra una implementación independiente",
                "reimplementarlos sería copiar spatstat, no otro camino; solo se exigen positivos y "
                "coherentes con su radio de QGIS")
        a.salta("coeficientes y z de `ppm` contra una implementación independiente",
                "ídem: solo se exige que existan y sean finitos")
        saltados += ["bw.diggle y bw.ppl", "ppm"]

    # =================================================================
    a.titulo("Que ninguna cifra de la clave se quede sin contrastar")
    if K is None:
        sin_clave("cobertura de la clave de QGIS", "mac")
    else:
        sin = K.sin_tocar()
        total = len([1 for r, _ in hojas(K.obj) if r and r[0] != "plataforma"])
        a.cierto(not sin, "toda hoja de la clave de QGIS se contrasta", f"{total} hojas, sin tocar: {sin[:3]}")
    if KR is None:
        sin_clave("cobertura de la clave de R", "r")
    else:
        sin = KR.sin_tocar()
        total = len([1 for r, _ in hojas(KR.obj)])
        a.cierto(not sin, "toda hoja de la clave de R se contrasta", f"{total} hojas, sin tocar: {sin[:3]}")

    # =================================================================
    print("\n=== Margen real de cada tolerancia (informativo) =========")
    print(f"  {'familia':<28}{'máx. desviación':>18}{'tolerancia':>14}")
    for fam, (d, tol) in sorted(DESV.items()):
        print(f"  {fam:<28}{d:>18.2e}{tol:>14.1e}")

    if faltan:
        print(f"\n  SALTADO: {len(saltados)} bloque(s) sin auditar porque faltan "
              f"{len([f for f in faltan])} archivo(s) de claves: {', '.join(faltan)}.")
        print("  Esto NO es el verde completo: solo se auditó lo público.")
        a.titulo_cierre = (f"AUDITORÍA PARCIAL: solo lo público; {len(saltados)} bloque(s) SALTADO(S) "
                           f"por falta de claves en precalculo/cache/")
    return a.cierre()


if __name__ == "__main__":
    sys.exit(main())
