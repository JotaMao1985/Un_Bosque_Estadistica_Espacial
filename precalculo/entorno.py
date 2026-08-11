"""
T0.1 — Entorno de Python del precálculo + prueba de humo.

Material de Estadística Espacial 2026-II (20929).

El intérprete es el del entorno `geo_env` de mambaforge, NO el `python3`
del PATH (que es el base y no tiene nada geoespacial):

    /opt/homebrew/Caskroom/mambaforge/base/envs/geo_env/bin/python

Igual que en R, esto comprueba que los paquetes CALCULEN, no que
importen. Y la última sección hace la parte que de verdad importa para el
material: **contrastar Python contra R sobre el mismo dato**. Las
pestañas R/Python del capítulo prometen al estudiante que las dos vías
dan lo mismo; si no lo dan, hay que decirlo como nota didáctica, no
esconderlo.
"""

import json
import warnings
from pathlib import Path

SEMILLA = 2026

# Mismo criterio que en entorno.R: lo que afecte al formato de la salida
# va aquí Y dentro del primer bloque publicado.
import numpy as np
import pandas as pd

pd.set_option("display.width", 100)
pd.set_option("display.max_columns", 20)
np.random.seed(SEMILLA)

PAQUETES = [
    "geopandas", "shapely", "pyproj", "libpysal", "esda", "spreg",
    "pointpats", "splot", "skgstat", "rasterio", "contextily",
    "mapclassify", "numpy", "pandas", "scipy", "sklearn", "matplotlib",
]


def versiones():
    import importlib
    out = {}
    for m in PAQUETES:
        try:
            out[m] = getattr(importlib.import_module(m), "__version__", "?")
        except Exception:
            out[m] = None
    return out


if __name__ == "__main__":
    warnings.filterwarnings("ignore")

    resultados = {}

    def prueba(nombre, fn):
        """`fn` DEBE ser un invocable (lambda), no un valor ya evaluado.

        R evalúa `expr` de forma perezosa y allí basta pasar la expresión;
        en Python `prueba("x", len(nc))` evalúa primero y luego intenta
        llamar al int resultante. Ese descuido marcó las 17
        comprobaciones como FALLO cuando lo roto era el arnés.
        """
        if not callable(fn):
            raise TypeError(f"prueba('{nombre}'): pásame una lambda, no un valor ya evaluado")
        try:
            val = fn()
            resultados[nombre] = {"ok": True, "valor": val}
            print(f"{nombre:26s} OK    {val}")
        except Exception as e:  # noqa: BLE001
            resultados[nombre] = {"ok": False, "valor": str(e)}
            print(f"{nombre:26s} FALLO {e}")

    import sys
    print("=== PRUEBA DE HUMO DEL ENTORNO ESPACIAL (Python) ===")
    print(sys.version.split()[0], "|", sys.executable, "\n")

    import geopandas as gpd
    import libpysal
    from libpysal.weights import Queen, KNN
    import esda

    # --- 1. geopandas: leer y reproyectar ----------------------------
    # El mismo nc.shp que usa el lado de R, para que la comparación sea
    # sobre el MISMO dato y no sobre dos copias parecidas. La ruta la
    # escribe entorno.R en versiones.json: la biblioteca de R vive en el
    # directorio del usuario, no dentro del framework, así que
    # codificarla a mano aquí se rompe en cuanto cambie.
    vjson = Path(__file__).parent / "versiones.json"
    if not vjson.exists():
        raise SystemExit("Falta versiones.json — corre antes precalculo/entorno.R")
    NC = json.loads(vjson.read_text())["rutas"]["nc_shp"]
    if not Path(NC).exists():
        raise SystemExit(f"nc.shp no está donde dice versiones.json: {NC}")
    nc = gpd.read_file(NC)
    prueba("geopandas.read_file", lambda: len(nc))
    prueba("geopandas.to_crs", lambda: nc.to_crs(3857).crs.to_epsg())
    prueba("geopandas.area",
           lambda: round(nc.to_crs(32617).area.sum() / 1e9, 1))

    # --- 2. libpysal: vecindad ---------------------------------------
    w = Queen.from_dataframe(nc, use_index=False)
    w.transform = "r"
    prueba("libpysal.Queen", lambda: w.n)
    prueba("libpysal.card_media", lambda: round(np.mean(list(w.cardinalities.values())), 4))
    prueba("libpysal.KNN", lambda: KNN.from_dataframe(nc, k=4).n)

    # --- 3. esda: Moran global y local -------------------------------
    mi = esda.Moran(nc["SID74"].values, w)
    prueba("esda.Moran", lambda: round(mi.I, 6))
    lm = esda.Moran_Local(nc["SID74"].values, w, seed=SEMILLA)
    prueba("esda.Moran_Local", lambda: len(lm.Is))
    g = esda.G_Local(nc["SID74"].values, w, seed=SEMILLA)
    prueba("esda.G_Local", lambda: len(g.Gs))

    # --- 4. spreg: econometría espacial ------------------------------
    from spreg import ML_Lag, ML_Error
    y = nc[["SID74"]].values.astype(float)
    X = nc[["BIR74"]].values.astype(float)
    ml_lag = ML_Lag(y, X, w=w)
    prueba("spreg.ML_Lag_rho", lambda: round(float(ml_lag.rho), 6))
    ml_err = ML_Error(y, X, w=w)
    prueba("spreg.ML_Error_lam", lambda: round(float(ml_err.lam), 6))

    # --- 5. pointpats: patrones puntuales ----------------------------
    from pointpats import PointPattern, k
    rng = np.random.default_rng(SEMILLA)
    pts = rng.random((100, 2))
    pp = PointPattern(pts)
    prueba("pointpats.PointPattern", lambda: pp.n)
    prueba("pointpats.lambda", lambda: round(pp.lambda_window, 4))

    # --- 6. skgstat: variograma --------------------------------------
    import skgstat as skg
    coords = rng.random((120, 2)) * 100
    vals = np.sin(coords[:, 0] / 20) + rng.normal(0, 0.2, 120)
    V = skg.Variogram(coords, vals, n_lags=12, model="spherical")
    prueba("skgstat.Variogram", lambda: len(V.bins))
    prueba("skgstat.range", lambda: round(float(V.parameters[0]), 3))

    # --- 7. mapclassify: cortes de clase (cap. 3) --------------------
    import mapclassify
    fj = mapclassify.FisherJenks(nc["SID74"].values, k=5)
    prueba("mapclassify.FisherJenks", lambda: [round(b, 3) for b in fj.bins])
    qt = mapclassify.Quantiles(nc["SID74"].values, k=5)
    prueba("mapclassify.Quantiles", lambda: [round(b, 3) for b in qt.bins])

    # =================================================================
    # Verificación cruzada R <-> Python
    #
    # No basta con que las dos corran: el material promete que dan lo
    # mismo. Se compara contra las cifras que imprimió entorno.R sobre el
    # MISMO nc.shp. Las discrepancias que aparezcan aquí son material
    # didáctico, no cosas que tapar.
    # =================================================================
    print("\n=== VERIFICACIÓN CRUZADA R <-> Python (mismo nc.shp) ===")

    R = {                      # salidas de entorno.R, 29/29 OK
        "n":            100,
        "epsg":         3857,
        "area_km2":     127.1,
        "card_media":   4.9,
        "moran_I":      0.147741,
        "lambda_SEM":   0.339925,
        "rho_SAR":      0.131721,
        # Cortes de clase: se comparan las PARTICIONES (cuántos condados
        # caen en cada clase), no los cortes impresos. Comparar los cortes
        # da un falso negativo, porque las dos bibliotecas los REPORTAN
        # distinto aunque clasifiquen igual. Ver la nota de abajo.
        "fisher_tam":   [32, 34, 19, 11, 4],
        "quant_tam":    [13, 25, 13, 26, 23],
    }

    cruces = []

    def cruza(nombre, r_val, py_val, tol=1e-4, explicada=None):
        """`explicada`: si difieren A PROPÓSITO, el porqué en una frase.

        Una discrepancia documentada es material didáctico; una sin
        explicar es un fallo. El resumen las cuenta por separado para que
        una nunca se disfrace de la otra.
        """
        try:
            igual = np.allclose(np.asarray(r_val, dtype=float),
                                np.asarray(py_val, dtype=float), atol=tol)
        except Exception:
            igual = r_val == py_val
        cruces.append((nombre, r_val, py_val, igual, explicada))
        marca = "==" if igual else ("!=*" if explicada else "!=")
        print(f"{nombre:22s} R={str(r_val):32s} {marca} Py={py_val}")
        if not igual and explicada:
            print(f"{'':22s} * esperada: {explicada}")

    cruza("n_condados",   R["n"],          len(nc))
    cruza("epsg",         R["epsg"],       nc.to_crs(3857).crs.to_epsg())
    cruza("area_km2",     R["area_km2"],   round(nc.to_crs(32617).area.sum() / 1e9, 1), tol=0.15)
    cruza("card_media",   R["card_media"],
          round(np.mean(list(w.cardinalities.values())), 4))
    cruza("moran_I",      R["moran_I"],    round(mi.I, 6))
    cruza("rho_SAR",      R["rho_SAR"],    round(float(ml_lag.rho), 6), tol=1e-3)
    cruza("lambda_SEM",   R["lambda_SEM"], round(float(ml_err.lam), 6), tol=1e-3)
    cruza("fisher_tam",   R["fisher_tam"],  [int(c) for c in fj.counts])
    cruza("quant_tam",    R["quant_tam"],   [int(c) for c in qt.counts],
          explicada="classInt usa [a,b) y mapclassify (a,b]; SID74 tiene "
                    "39 empates justo en los cortes. Caso trabajado del cap. 3.")

    # -----------------------------------------------------------------
    # HALLAZGO DEL CAPÍTULO 3 — verificado, no supuesto.
    #
    # Fisher-Jenks: MISMA partición en R y en Python (32, 34, 19, 11, 4),
    # con los mismos mínimos y máximos por clase. Lo único que difiere es
    # cómo se REPORTA la frontera:
    #   R  (classInt): el punto medio entre el máximo de una clase y el
    #                  mínimo de la siguiente -> 2.5, 6.5, 12.5, 26, 44,
    #                  y además antepone el mínimo global (n+1 = 6 cortes).
    #   Py (mapclassify): el máximo real de cada clase -> 2, 6, 12, 23, 44
    #                  (n = 5 cortes).
    # Es convención de impresión, no desacuerdo. El mapa sale idéntico.
    #
    # Cuantiles: la partición SÍ difiere de verdad.
    #   R  : 13, 25, 13, 26, 23      Py: 24, 27, 11, 19, 19
    # La causa NO es el algoritmo sino el lado cerrado del intervalo:
    #   R  (classInt/findCols) usa  [a, b)   -> el empate sube de clase
    #   Py (mapclassify)       usa  (a, b]   -> el empate baja de clase
    # SID74 tiene 39 condados empatados justo EN los cortes (11 con el
    # valor 1, 13 con 4, 11 con 5, 4 con 10). Solo en la primera clase eso
    # mueve 11 condados: R deja los 13 ceros y Python mete ceros y unos
    # (13 + 11 = 24). Dos mapas visiblemente distintos del mismo dato,
    # con la misma "clasificación por cuantiles".
    #
    # Va al capítulo 3 como caso trabajado. Es el mismo tipo de trampa que
    # los nueve convenios de `qrule` en el material de Muestreo.
    # -----------------------------------------------------------------

    # --- informe ------------------------------------------------------
    ok = sum(1 for v in resultados.values() if v["ok"])
    print(f"\n=== {ok} de {len(resultados)} comprobaciones OK ===")
    fallos = [k_ for k_, v in resultados.items() if not v["ok"]]
    if fallos:
        print("FALLAN:", ", ".join(fallos))

    coinciden   = [c[0] for c in cruces if c[3]]
    documentadas = [c[0] for c in cruces if not c[3] and c[4]]
    sin_explicar = [c[0] for c in cruces if not c[3] and not c[4]]

    print(f"=== {len(coinciden)} de {len(cruces)} cruces R<->Python coinciden ===")
    if documentadas:
        print(f"    {len(documentadas)} discrepancia(s) DOCUMENTADA(s):",
              ", ".join(documentadas), "-> van al material como caso trabajado")
    if sin_explicar:
        print(f"    {len(sin_explicar)} discrepancia(s) SIN EXPLICAR:",
              ", ".join(sin_explicar), "-> esto es un FALLO, hay que investigarlo")

    destino = Path(__file__).parent / "versiones_py.json"
    destino.write_text(json.dumps({
        "python": sys.version.split()[0],
        "ejecutable": sys.executable,
        "semilla": SEMILLA,
        "paquetes": versiones(),
        "cruces_r_python": {c[0]: {"r": c[1], "python": c[2],
                                   "coincide": bool(c[3]), "explicada": c[4]}
                            for c in cruces},
    }, indent=2, ensure_ascii=False, default=float))
    print("versiones_py.json escrito.")

    # Una discrepancia sin explicar es tan grave como un paquete que no
    # calcula: las dos tumban la tarea.
    if fallos or sin_explicar:
        sys.exit(1)
