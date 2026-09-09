#!/usr/bin/env python3
"""
audita_cap7.py — auditoría independiente del precálculo del capítulo 7 (T4.4b)

Material de Estadística Espacial 2026-II (20929).

NO comprueba que los JSON existan: comprueba que sus NÚMEROS sean ciertos,
por caminos que no pasan por R ni por `spdep`.

QUÉ HACE QUE ESTO SEA UN CONTROL, Y NO UNA SEGUNDA OPINIÓN DEL MISMO
El capítulo entero es «¿lo cercano se parece más de lo esperable?», y esa
pregunta tiene dos implementaciones maduras y ajenas: `spdep` en R, que
generó las cifras, y **`esda` en Python (PySAL), que las recalcula aquí**:
la I de Moran con sus tres inferencias, la c de Geary, los I locales y la
Gi* de Getis-Ord. Dos bibliotecas escritas por gente distinta, con
convenios distintos que hay que conocer ANTES de comparar, o el auditor
llama defecto a una diferencia de convenio (A.11, A.28):

  · CON ISLAS, `spdep` toma n = unidades con vecinos y `esda` n = todas.
    El paso entre los dos I globales es exactamente n_con/n, y se aplica
    donde hay islas: los municipios (2), el umbral a medias de Columbus
    (28) y el orden 6 del correlograma (5).
  · LOS I LOCALES: `spdep` (mlvar = TRUE) tipifica con la varianza
    poblacional y `esda` con la muestral. El factor es n/(n-1), exacto.
  · LOS p POR PERMUTACIÓN salen de dos generadores distintos: los Iᵢ
    coinciden al bit y los p solo hasta el error de Monte Carlo. Se
    comparan con esa tolerancia —4·sqrt(2p(1-p)/nsim) + 2/nsim, porque los DOS
    p son estimaciones— y los
    recuentos con un margen de unas pocas unidades; lo EXACTO se
    comprueba desde los p publicados en el CSV, que es donde tiene que
    ser exacto. Y la tolerancia solo vale si los dos permutan IGUAL: por
    defecto `spdep` muestrea los vecinos CON reemplazo y GeoDa y `esda`
    sin él, y eso hacía los p de `spdep` sistemáticamente mayores en 17
    de 49 unidades. El generador usa `no_repeat_in_row = TRUE` (A.29).
  · `esda` da el p de Moran BILATERAL por defecto, la z de Geary con el
    signo contrario a `spdep`, y su c con islas lleva n en vez de n_con:
    el factor es (n_con − 1)/(n − 1).
  · CON ISLAS, la esperanza del join count de `spdep` mezcla convenios:
    n_B y n_W se cuentan sobre todas las unidades y el denominador
    n(n − 1) usa n_con. Se reproduce tal cual, y se dice.
  · LA z DE Gi* CON PESOS POR FILAS: `esda` 2.9.0 la calcula con una
    varianza ocho veces mayor de lo que dan las ecuaciones de Ord y Getis
    (1995) escritas a mano, que sí coinciden con `spdep`. En binario las
    tres coinciden al bit, y la z de Gi* es INVARIANTE a reescalar las
    filas, así que se audita con pesos binarios y se declara el defecto.

Y lo que `esda` no trae se reimplementa aquí por definición: el join
count ponderado por W con su esperanza bajo muestreo sin reemplazo, el
correlograma por órdenes (`higher_order` de libpysal para los vecinos, la
I con esda), el procedimiento de Benjamini-Hochberg, los cuadrantes desde
los signos de z y Wz, la potencia con campos SAR simulados en numpy, y el
rango real de I por los valores propios de (W + W')/2.

HASTA DÓNDE LLEGA LA INDEPENDENCIA, DECLARADO Y NO INSINUADO
  · TOTAL para I, E[I], las dos varianzas, Geary, los Iᵢ, las Gi y Gi*,
    los estilos, el rango, el join count, el correlograma, la potencia y
    toda la aritmética de recuentos y categorías.
  · PARCIAL para los p por permutación (error de Monte Carlo declarado).
  · NULA para la GAL de Anselin como tal: `libpysal` trae `columbus.gal`,
    pero es la REINA de 118 parejas, no la GAL de 1988 de 116. La GAL se
    lee del CSV publicado y se valida por sus diferencias con la reina,
    que sí se recalcula: una pareja solo en la GAL y tres solo en la reina.
  · NULA para la esfera de influencia, para las medidas de influencia de
    `moran.plot`, para la comparación entre 999 y 24 999 réplicas (dos
    generadores), y para el p LOCAL analítico (esda no lo trae): de esos
    se auditan propiedades, no valores. Todos en la lista de saltadas.

Ejecutar con el Python de geo_env:
    "$(python3 -c 'import json;print(json.load(open("precalculo/versiones_py.json"))["ejecutable"])')" \\
        precalculo/audita_cap7.py

LOS RÓTULOS TIENEN PRESUPUESTO: 57 CARACTERES, PREFIJO INCLUIDO.
"""
from __future__ import annotations

import json
import pathlib
import sys
import warnings

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from audita_base import (Auditoria, audita_geomapa, carga as _carga,  # noqa: E402
                         decimales)
from audita_cap6 import (reina_municipal, de_w, componentes, simetrizar,  # noqa: E402
                         banda)

import numpy as np                      # noqa: E402
import pandas as pd                     # noqa: E402
import geopandas as gpd                 # noqa: E402
import libpysal                         # noqa: E402
from libpysal import weights            # noqa: E402
from esda import Moran, Moran_Local, Geary, G_Local  # noqa: E402

warnings.filterwarnings("ignore")

RAIZ = pathlib.Path(__file__).resolve().parent.parent
PRECALCULO = RAIZ / "precalculo"
SALIDAS = PRECALCULO / "salidas"
PROCESADO = RAIZ / "datos" / "procesado"
CACHE = PRECALCULO / "cache"
ALFA = 0.05
SEMILLA = 2026


def carga(var: str, nombre: str):
    return _carga(var, nombre, SALIDAS)


# =====================================================================
# Herramientas
# =====================================================================
def w_de(nbrs: dict, transform: str = "r") -> weights.W:
    w = weights.W({int(k): [int(j) for j in v] for k, v in nbrs.items()}, silence_warnings=True)
    w.transform = transform
    return w


def pares_de(nbrs: dict) -> set:
    return {tuple(sorted((i, j))) for i in nbrs for j in nbrs[i]}


def tol_p(p: float, nsim: int) -> float:
    """El error de Monte Carlo de la DIFERENCIA entre dos p por rangos.

    Los dos p son estimaciones —el de spdep y el de esda—, así que la
    diferencia tiene varianza 2·p(1−p)/nsim, no p(1−p)/nsim: sin el √2
    ocho municipios de 2 238 comparaciones caían a 4,0–4,5 sigmas sin
    sesgo alguno, que es justo lo que una tolerancia corta produce.
    Cuatro sigmas de la diferencia, más dos pasos de rejilla.
    """
    p = min(max(float(p), 1.0 / (nsim + 1)), 0.5)
    return 4.0 * np.sqrt(2.0 * p * (1 - p) / nsim) + 2.0 / nsim


def bh(p: np.ndarray, alfa: float = ALFA) -> int:
    """Benjamini-Hochberg escrito a mano: cuántos rechaza."""
    p = np.sort(np.asarray(p, dtype=float))
    n = len(p)
    umb = np.arange(1, n + 1) * alfa / n
    ok = np.where(p <= umb)[0]
    return 0 if len(ok) == 0 else int(ok.max()) + 1


def rango_I(W: np.ndarray) -> tuple[float, float]:
    ev = np.linalg.eigvalsh((W + W.T) / 2)
    return float(ev.min()), float(ev.max())


def moran_con_islas(y: np.ndarray, w: weights.W) -> float:
    """El I de Moran con el convenio de spdep: n = unidades con vecinos."""
    m = Moran(y, w, transformation="r", permutations=0)
    n = len(y)
    n_con = sum(1 for k in w.neighbors if len(w.neighbors[k]) > 0)
    return float(m.I) * n_con / n


def cuadrante(z: np.ndarray, wz: np.ndarray) -> np.ndarray:
    """Los cuatro cuadrantes desde los signos, con los nombres de spdep."""
    return np.where(z >= 0, np.where(wz >= 0, "High-High", "High-Low"),
                    np.where(wz >= 0, "Low-High", "Low-Low"))


def lisa_codigo(cuad: np.ndarray, p: np.ndarray, corte: float = ALFA) -> np.ndarray:
    cod = np.array([{"High-High": 2, "Low-Low": 3, "High-Low": 4, "Low-High": 5}[q] for q in cuad], dtype=float)
    cod[(~np.isnan(p)) & (p >= corte)] = 1
    cod[np.isnan(p)] = np.nan
    return cod


def gistar_codigo(z: np.ndarray, p: np.ndarray) -> np.ndarray:
    cod = np.full(len(z), 4.0)
    m = ~np.isnan(p)
    for umbral, cal, frio in ((0.10, 5, 3), (0.05, 6, 2), (0.01, 7, 1)):
        s = m & (p < umbral)
        cod[s] = np.where(z[s] > 0, cal, frio)
    cod[~m | np.isnan(z)] = np.nan
    return cod


def conteo(cod: np.ndarray, k: int) -> list[int]:
    return [int(np.sum(cod == i)) for i in range(1, k + 1)]


def bonferroni(p: np.ndarray, alfa: float = ALFA) -> int:
    p = p[~np.isnan(p)]
    return int(np.sum(np.minimum(p * len(p), 1.0) < alfa))


def join_count(x: np.ndarray, W: np.ndarray) -> dict:
    """El join count PONDERADO por W, como joincount.multi con estilo W.

    Observado: ½ Σ w_ij 1[i∈A] 1[j∈B]. Esperado bajo muestreo sin
    reemplazo: ½ S0 n_A (n_A − 1) / (n (n − 1)) para AA y
    S0 n_A n_B / (n (n − 1)) para AB. La z se recalcula por signo.

    CON ISLAS, spdep mezcla dos convenios y aquí se reproduce tal cual:
    n_A y n_B se cuentan sobre TODAS las unidades, pero el n del
    denominador es el de las unidades CON vecinos. Sin eso la esperanza
    municipal sale un 0,36 % más baja y el auditor llama defecto a un
    convenio.
    """
    n = len(x)
    n_con = int((W.sum(axis=1) > 0).sum())
    S0 = W.sum()
    b = x.astype(float)
    nb, nw = b.sum(), n - b.sum()
    n = n_con
    BB = 0.5 * b @ W @ b
    WW = 0.5 * (1 - b) @ W @ (1 - b)
    BW = 0.5 * (b @ W @ (1 - b) + (1 - b) @ W @ b)
    return dict(BB=float(BB), WW=float(WW), BW=float(BW),
                E_BB=0.5 * S0 * nb * (nb - 1) / (n * (n - 1)),
                E_WW=0.5 * S0 * nw * (nw - 1) / (n * (n - 1)),
                E_BW=S0 * nb * nw / (n * (n - 1)))


def potencia_celda(k: int, rho: float, reps: int = 1000, semilla: int = 7) -> float:
    """Campos SAR sobre un retículo torre, en numpy, y la potencia al 5 %."""
    rng = np.random.default_rng(semilla)
    w = weights.lat2W(k, k, rook=True)
    w.transform = "r"
    W = w.full()[0]
    n = k * k
    A = np.linalg.inv(np.eye(n) - rho * W)
    Y = A @ rng.standard_normal((n, reps))
    Z = (Y - Y.mean(axis=0)) / Y.std(axis=0, ddof=1)
    I = (Z * (W @ Z)).sum(axis=0) / (Z * Z).sum(axis=0)
    m0 = Moran(Y[:, 0], w, transformation="r", permutations=0)
    zc = (I - m0.EI) / np.sqrt(m0.VI_norm)
    from scipy.stats import norm
    return float(np.mean(zc > norm.ppf(1 - ALFA)))


def gistar_a_mano(x: np.ndarray, nbrs: dict) -> np.ndarray:
    """Gi* con la propia unidad dentro, pesos estandarizados por filas.

    Ord y Getis (1995): G = Σ w x / Σ x, E = W_i / n y
    Var = (n S1 − W_i²) / (n − 1) · s² / (n² x̄²), con s² poblacional.
    """
    n = len(x)
    A = np.eye(n)
    for i, js in nbrs.items():
        for j in js:
            A[i, j] = 1.0
    W = A / A.sum(axis=1, keepdims=True)
    Wi = W.sum(axis=1)
    S1 = (W ** 2).sum(axis=1)
    xbar = x.mean()
    s2 = ((x - xbar) ** 2).mean()
    G = (W @ x) / x.sum()
    E = Wi / n
    V = (n * S1 - Wi ** 2) / (n - 1) * s2 / (xbar ** 2 * n ** 2)
    return (G - E) / np.sqrt(V)


def cache_local(llave: str, calcula):
    """Los locales de esda sobre los municipios, con la llave del .gpkg."""
    f = CACHE / "audita_cap7_local.json"
    if f.exists():
        g = json.loads(f.read_text(encoding="utf-8"))
        if g.get("llave") == llave:
            return {k: np.array(v, dtype=float) for k, v in g["valores"].items()}
    v = calcula()
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(json.dumps({"llave": llave, "valores": {k: [None if np.isnan(x) else float(x) for x in a]
                                                          for k, a in v.items()}}), encoding="utf-8")
    return v


def torre_municipal(mun, ruta: pathlib.Path) -> dict:
    st = ruta.stat()
    llave = f"{st.st_size}·{int(st.st_mtime)}·{len(mun)}"
    f = CACHE / "audita_cap7_torre.json"
    if f.exists():
        g = json.loads(f.read_text(encoding="utf-8"))
        if g.get("llave") == llave:
            return {int(k): v for k, v in g["vecinos"].items()}
    v = de_w(weights.Rook.from_dataframe(mun, use_index=True))
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(json.dumps({"llave": llave, "vecinos": v}), encoding="utf-8")
    return v


def main() -> int:  # noqa: C901
    a = Auditoria("Precálculo del capítulo 7 verificado")
    D, p_datos = carga("CAP7_DATOS", "cap7_datos.json")
    M, _ = carga("CAP7_MAPAS", "cap7_mapas.json")
    NSIM = int(D["meta"]["nsim"])
    ccsv = pd.read_csv(SALIDAS / "cap7_columbus.csv")
    gcsv = pd.read_csv(SALIDAS / "cap7_columbus_gal.csv")
    gocsv = pd.read_csv(SALIDAS / "cap7_getisord.csv")
    mcsv = pd.read_csv(SALIDAS / "cap7_municipios_lisa.csv", dtype={"divipola": str})
    pcsv = pd.read_csv(SALIDAS / "cap7_potencia.csv")

    # -----------------------------------------------------------------
    a.titulo("1 · Columbus en el orden de Anselin, y su GAL contra la reina")
    col0 = gpd.read_file(libpysal.examples.get_path("columbus.shp"))
    pol = ccsv["polyid"].to_numpy(dtype=int)
    a.cierto(sorted(pol) == list(range(1, 50)), "el CSV recorre los 49 POLYID una vez")
    col = col0.set_index("POLYID").loc[pol].reset_index()
    n = len(col)
    crime = col["CRIME"].to_numpy(dtype=float)
    a.igual(n, D["m1"]["columbus"]["n"], "Columbus: barrios")
    a.igual(np.abs(crime - ccsv["CRIME"].to_numpy()).max(), 0.0,
            "el CSV y el shapefile cuentan el mismo CRIME", tol=1e-9)
    a.igual(crime.mean(), D["m1"]["columbus"]["media"], "CRIME: media", tol=1e-4)
    a.igual(crime.std(ddof=1), D["m1"]["columbus"]["sd"], "CRIME: desviación", tol=1e-4)

    nb_gal = {i: [] for i in range(n)}
    for i, j in zip(gcsv["i"], gcsv["j"]):
        nb_gal[int(i) - 1].append(int(j) - 1)
        nb_gal[int(j) - 1].append(int(i) - 1)
    nb_gal = {i: sorted(v) for i, v in nb_gal.items()}
    w_gal = w_de(nb_gal)
    a.igual(len(pares_de(nb_gal)), D["m2"]["columbus"]["pares_gal"], "la GAL: parejas")
    a.cierto(all(i in nb_gal[j] for i in nb_gal for j in nb_gal[i]), "la GAL es simétrica")
    a.cierto((gcsv["i0"] == gcsv["i"] - 1).all() and (gcsv["j0"] == gcsv["j"] - 1).all(),
             "los índices 0-basados del CSV son los 1-basados menos uno")
    nb_reina = de_w(weights.Queen.from_dataframe(col, use_index=True))
    pr, pg = pares_de(nb_reina), pares_de(nb_gal)
    gv = D["m7"]["gal_vs_reina"]
    a.igual(len(pr), gv["pares_reina"], "la reina de libpysal: 118 parejas")
    a.igual(len(pg - pr), gv["solo_gal"], "parejas que solo tiene la GAL")
    a.igual(len(pr - pg), gv["solo_reina"], "parejas que solo tiene la reina")
    W_gal = w_gal.full()[0]
    a.igual(np.corrcoef(crime, W_gal @ crime)[0, 1], D["m1"]["columbus"]["cor_con_rezago"],
            "CRIME y su rezago: correlación", tol=1e-4)

    # -----------------------------------------------------------------
    a.titulo("2 · La I de Moran, con esda")
    m2 = D["m2"]["columbus"]
    mo = Moran(crime, w_gal, transformation="r", permutations=0, two_tailed=False)
    a.igual(mo.I, m2["I"], "I de Moran de CRIME", tol=1e-6)
    a.igual(mo.EI, m2["EI"], "E[I] = -1/(n-1)", tol=1e-6)
    a.igual(-1.0 / (n - 1), m2["EI"], "y vale -1/48", tol=1e-6)
    a.igual(mo.VI_rand, m2["var_aleat"], "varianza por aleatorización", tol=1e-6)
    a.igual(mo.z_rand, m2["z_aleat"], "z por aleatorización", tol=1e-3)
    a.igual(mo.VI_norm, m2["var_norm"], "varianza por normalidad", tol=1e-6)
    a.igual(mo.z_norm, m2["z_norm"], "z por normalidad", tol=1e-3)
    a.igual(mo.I, 0.511, "Anselin (1995): I = 0,511", tol=5e-4)
    a.igual(mo.z_rand, 5.63, "Anselin (1995): z = 5,63", tol=5e-3)
    a.igual(W_gal.sum(), m2["S0"], "S0 con estilo W es n", tol=1e-9)
    z = (crime - crime.mean()) / crime.std(ddof=1)
    a.igual(z @ (W_gal @ z), m2["z_Wz"], "z'Wz", tol=1e-5)
    a.igual(z @ z, m2["z_z"], "z'z = n - 1", tol=1e-6)
    a.igual(m2["z_Wz"] / m2["z_z"], m2["I"], "y su cociente es I", tol=1e-6)
    est = {e["id"]: e for e in D["m2"]["estilos"]}
    for e, tr in (("W", "r"), ("B", "b"), ("S", "v"), ("C", "d"), ("U", "d")):
        a.igual(Moran(crime, w_de(nb_gal, tr), transformation=tr, permutations=0).I,
                est[e]["I"], f"estilo {e}: I", tol=1e-6)
    a.cierto(est["B"]["I"] == est["C"]["I"] == est["U"]["I"],
             "B, C y U dan la misma I: escalar W no mueve el cociente")
    a.igual(est["W"]["S0"], n, "estilo W: S0 = n", tol=1e-9)
    a.igual(est["U"]["S0"], 1.0, "estilo U: S0 = 1", tol=1e-9)
    lo, hi = rango_I(W_gal)
    a.igual(lo, D["m2"]["rango"]["columbus_gal"][0], "rango real de I: mínimo (GAL)", tol=1e-3)
    a.igual(hi, D["m2"]["rango"]["columbus_gal"][1], "rango real de I: máximo (GAL)", tol=1e-3)
    a.cierto(hi > 1.0 and lo > -1.0, "y el rango no es [-1, 1]", f"[{lo:.3f}, {hi:.3f}]")
    ret = weights.lat2W(10, 10, rook=True)
    ret.transform = "r"
    mr = Moran(np.random.default_rng(1).standard_normal(100), ret, transformation="r", permutations=0)
    r1 = D["m1"]["reticulo"]
    a.igual(mr.EI, r1["EI"], "retículo 10×10: E[I]", tol=1e-6)
    a.igual(np.sqrt(mr.VI_norm), r1["sd_norm"], "retículo: sd bajo normalidad", tol=1e-5)
    lo_r, hi_r = rango_I(ret.full()[0])
    a.igual(hi_r, D["m2"]["rango"]["reticulo_10"][1], "retículo: máximo de I", tol=1e-3)

    # -----------------------------------------------------------------
    a.titulo("3 · Las tres inferencias, y la potencia")
    m3 = D["m3"]["columbus"]
    a.cerca(mo.p_norm, m3["normalidad"]["p"], "p por normalidad", rel=1e-3)
    a.cerca(mo.p_rand, m3["aleatorizacion"]["p"], "p por aleatorización", rel=1e-3)
    b2 = np.mean((crime - crime.mean()) ** 4) / np.mean((crime - crime.mean()) ** 2) ** 2
    a.igual(b2, m3["aleatorizacion"]["curtosis"], "la curtosis de CRIME", tol=1e-3)
    a.cierto(m3["aleatorizacion"]["var"] != m3["normalidad"]["var"],
             "las dos varianzas difieren, por la curtosis")
    np.random.seed(SEMILLA)
    mp = Moran(crime, w_gal, transformation="r", permutations=999)
    pe = m3["permutacion"]
    a.igual(pe["nsim"], 999, "permutación: 999 réplicas")
    a.igual(pe["p"], 1.0 / 1000, "y su p es el suelo 1/(nsim+1)", tol=1e-9)
    a.igual(mp.p_sim, pe["p"], "esda también da el suelo", tol=1e-9)
    a.igual(pe["rango_observado"], 0, "ninguna réplica alcanza la I observada")
    rep = np.asarray(pe["replicas"], dtype=float)
    a.igual(len(rep), 999, "las 999 réplicas publicadas")
    a.igual(rep.mean(), pe["media_sim"], "su media, recontada", tol=1e-4)
    a.igual(rep.std(ddof=1), pe["sd_sim"], "su desviación, recontada", tol=1e-4)
    a.igual(rep.max(), pe["max_sim"], "su máximo, recontado", tol=1e-4)
    a.cierto(rep.max() < pe["I"], "y todas quedan por debajo de I")
    a.igual(mp.EI_sim, pe["media_sim"], "media de las permutaciones (esda)", tol=0.02)
    a.igual(mp.seI_sim, pe["sd_sim"], "desviación de las permutaciones (esda)", tol=0.01)
    a.cierto(abs(pe["sd_sim"] - np.sqrt(m2["var_aleat"])) < 0.01,
             "y se parece a la raíz de la varianza por aleatorización",
             f"{pe['sd_sim']:.4f} frente a {np.sqrt(m2['var_aleat']):.4f}")
    p99 = m3["permutacion_99999"]
    a.igual(p99["p"], 1.0 / (p99["nsim"] + 1), "con 99 999 réplicas el p sigue en el suelo", tol=1e-9)

    # los municipios
    mun = gpd.read_file(PROCESADO / "colombia_adm2.gpkg")
    llave = pd.read_csv(PROCESADO / "municipios_llave.csv", dtype={"divipola": str})
    mun = mun.merge(llave, on="shapeID", how="left")
    des = mun["desercion"].to_numpy(dtype=float)
    ok = np.isfinite(des)
    sub = np.where(ok)[0]
    idx = {v: i for i, v in enumerate(sub)}
    mun_q = reina_municipal(mun, PROCESADO / "colombia_adm2.gpkg")
    nb_sub = {i: [idx[j] for j in mun_q[v] if j in idx] for i, v in enumerate(sub)}
    w_sub = w_de(nb_sub)
    y = des[sub]
    con = np.array([len(nb_sub[i]) > 0 for i in range(len(sub))])
    mm = D["m3"]["municipios"]["aleatorizacion"]
    a.igual(len(sub), mm["n"], "municipios con dato")
    a.igual(int(con.sum()), mm["n_con_vecinos"], "y con vecinos")
    me = Moran(y, w_sub, transformation="r", permutations=0)
    a.igual(me.I * con.sum() / len(sub), mm["I"], "I municipal, con el convenio de spdep", tol=1e-6)
    a.igual(mm["I"], 0.3809079, "y es el 0,38091 de T0.4a", tol=1e-6)
    for pm in D["m3"]["municipios"]["permutacion"]:
        a.igual(pm["p"], 1.0 / (pm["nsim"] + 1), f"municipios: p con {pm['nsim']} réplicas es el suelo", tol=1e-9)
    a.igual(np.abs(mcsv["desercion"].to_numpy() - y).max(), 0.0, "el CSV municipal trae la deserción", tol=1e-9)

    # la potencia
    pot = D["m3"]["potencia"]
    curvas = {c["n"]: np.asarray(c["potencia"], dtype=float) for c in pot["curvas"]}
    a.igual(len(pcsv), 4 * len(pot["rhos"]), "el CSV de potencia: 4 n × 10 rho")
    for nn, cu in curvas.items():
        a.cierto(abs(cu[0] - ALFA) < 0.04, f"potencia n={nn}: en rho = 0 vale alfa", f"{cu[0]:.3f}")
        a.cierto(np.all(np.diff(cu) >= -0.02), f"potencia n={nn}: crece con rho")
    a.cierto(curvas[400][3] > curvas[100][3] > curvas[25][3], "y crece con n en rho = 0,3")
    a.igual(potencia_celda(10, 0.5), curvas[100][5], "potencia n=100, rho=0,5, recalculada", tol=0.06)
    a.igual(potencia_celda(5, 0.3), curvas[25][3], "potencia n=25, rho=0,3, recalculada", tol=0.06)

    # -----------------------------------------------------------------
    a.titulo("4 · El diagrama de Moran: la pendiente ES I")
    m4 = D["m4"]["columbus"]
    wz = W_gal @ z
    a.igual(np.abs(z - ccsv["z"].to_numpy()).max(), 0.0, "z del CSV = CRIME tipificado", tol=1e-8)
    a.igual(np.abs(wz - ccsv["wz"].to_numpy()).max(), 0.0, "Wz del CSV = W·z", tol=1e-8)
    pend = np.polyfit(z, wz, 1)[0]
    a.igual(pend, m4["pendiente"], "la pendiente de Wz sobre z", tol=1e-6)
    a.igual(pend, m2["I"], "y es exactamente I", tol=1e-6)
    a.igual(np.polyfit(crime, W_gal @ crime, 1)[0], m4["pendiente_sin_tipificar"],
            "sin tipificar la pendiente sigue siendo I", tol=1e-6)
    cu = cuadrante(z, wz)
    for k, nombre in (("AA", "High-High"), ("BB", "Low-Low"), ("AB", "High-Low"), ("BA", "Low-High")):
        a.igual(int(np.sum(cu == nombre)), m4["cuadrantes"][k], f"cuadrante {k}")
    a.igual(sum(m4["cuadrantes"].values()), n, "los cuadrantes suman 49")
    a.cierto(list(m4["puntos"]["polyid"]) == pol.tolist(), "los 49 puntos llevan su POLYID")
    a.igual(np.abs(np.asarray(m4["puntos"]["z"]) - np.round(z, 5)).max(), 0.0, "sus z", tol=1e-5)
    a.salta("influyentes de moran.plot: recalculados", "son medidas de influencia de R")
    a.cierto(0 <= m4["influyentes"] <= n and len(m4["influyentes_polyid"]) == m4["influyentes"]
             and set(m4["influyentes_polyid"]) <= set(pol.tolist()),
             "influyentes: un recuento y sus POLYID coherentes")
    m4m = D["m4"]["municipios"]
    zm, wzm = mcsv["z"].to_numpy(), mcsv["wz"].to_numpy()
    a.igual(np.abs(zm - (y - y.mean()) / y.std(ddof=1)).max(), 0.0, "municipios: z del CSV", tol=1e-8)
    a.igual(np.abs(wzm - w_sub.full()[0] @ zm).max(), 0.0, "municipios: Wz del CSV", tol=1e-8)
    a.igual(np.polyfit(zm, wzm, 1)[0], m4m["pendiente_todas"], "municipios: pendiente sobre todas", tol=1e-6)
    a.igual(m4m["pendiente_todas"], m4m["I"], "y sobre TODAS es I, islas incluidas", tol=1e-6)
    a.igual(np.polyfit(zm[con], wzm[con], 1)[0], m4m["pendiente_con_vecinos"],
            "municipios: pendiente sobre las que tienen vecinos", tol=1e-6)
    a.cierto(abs(m4m["pendiente_con_vecinos"] - m4m["I"]) > 1e-4,
             "y sobre ésas ya no lo es", f"{m4m['pendiente_con_vecinos']} ≠ {m4m['I']}")
    cum = cuadrante(zm, wzm)[con]
    a.igual(int(np.sum(cum == "High-High")), m4m["cuadrantes"]["AA"], "municipios: alto-alto")
    a.igual(int(np.sum(cum == "Low-Low")), m4m["cuadrantes"]["BB"], "municipios: bajo-bajo")

    # -----------------------------------------------------------------
    a.titulo("5 · La c de Geary, y el barrio disparado")
    m5 = D["m5"]["columbus"]
    ge = Geary(crime, w_gal, transformation="r", permutations=0)
    a.igual(ge.C, m5["c"], "c de Geary de CRIME", tol=1e-6)
    a.igual(ge.VC_rand, m5["var"], "su varianza por aleatorización", tol=1e-6)
    a.igual(-ge.z_rand, m5["z"], "su z (esda la da con el signo contrario)", tol=1e-3)
    a.igual(1 - ge.C, m5["uno_menos_c"], "1 - c", tol=1e-6)
    a.cierto(abs(m5["uno_menos_c"] - m5["I"]) > 0.01, "y 1 - c no es I", f"{m5['uno_menos_c']} frente a {m5['I']}")
    for t in D["m5"]["tres_variables"]:
        v = col[t["variable"]].to_numpy(dtype=float)
        a.igual(Moran(v, w_gal, "r", 0).I, t["I"], f"{t['variable']}: I", tol=1e-4)
        a.igual(Geary(v, w_gal, "r", 0).C, t["c"], f"{t['variable']}: c", tol=1e-4)
    for cual in ("pico_en_alto", "pico_en_bajo"):
        pk = D["m5"][cual]
        i = pk["unidad"] - 1
        a.igual(pol[i], pk["polyid"], f"{cual}: su POLYID")
        a.igual(crime[i], pk["crime"], f"{cual}: su CRIME", tol=1e-4)
        a.igual(len(nb_gal[i]), pk["grado"], f"{cual}: su grado")
        for punto in pk["curva"]:
            x = crime.copy()
            x[i] *= punto["factor"]
            a.igual(Moran(x, w_gal, "r", 0).I, punto["I"], f"{cual} ×{punto['factor']}: I", tol=1e-4)
            a.igual(Geary(x, w_gal, "r", 0).C, punto["c"], f"{cual} ×{punto['factor']}: c", tol=1e-4)
        a.cierto(pk["curva"][-1]["I"] < pk["curva"][0]["I"] / 2, f"{cual}: I se hunde hacia cero")
        a.cierto(pk["curva"][-1]["c"] > pk["curva"][0]["c"], f"{cual}: c sube hacia uno")
    i_alto = D["m5"]["pico_en_alto"]["unidad"] - 1
    a.igual(i_alto, int(np.argmax(crime)), "el pico en alto es el barrio de mayor CRIME")
    a.igual(D["m5"]["pico_en_bajo"]["unidad"] - 1, int(np.argmin(wz)), "y el pico en bajo, el de vecindad más baja")
    gm = Geary(y, w_sub, transformation="r", permutations=0)
    a.igual(gm.C * (con.sum() - 1) / (len(y) - 1), D["m5"]["municipios"]["c"],
            "municipios: c de Geary, con el factor (n_con-1)/(n-1)", tol=1e-5)

    # -----------------------------------------------------------------
    a.titulo("6 · Correlograma y join count, por definición")
    wb = w_de(nb_gal, "b")
    cg = D["m6"]["correlograma"]["columbus"]
    for o in cg:
        k = o["orden"]
        wk = weights.higher_order(wb, k) if k > 1 else wb
        nbk = de_w(wk)
        a.igual(len(pares_de(nbk)), o["pares"], f"orden {k}: parejas")
        a.igual(sum(1 for i in nbk if not nbk[i]), o["sin_vecinos"], f"orden {k}: sin vecinos")
        a.igual(componentes(simetrizar(nbk))[0], o["subgrafos"], f"orden {k}: subgrafos")
        a.igual(moran_con_islas(crime, w_de(nbk)), o["I"], f"orden {k}: I", tol=1e-5)
    a.cierto(cg[0]["I"] > cg[1]["I"] > cg[2]["I"], "la I cae con el orden en Columbus")
    cgm = D["m6"]["correlograma"]["municipios"]
    wbm = w_de(nb_sub, "b")
    for o in cgm:
        k = o["orden"]
        wk = weights.higher_order(wbm, k) if k > 1 else wbm
        nbk = de_w(wk)
        a.igual(len(pares_de(nbk)), o["pares"], f"municipios orden {k}: parejas")
        a.igual(moran_con_islas(y, w_de(nbk)), o["I"], f"municipios orden {k}: I", tol=1e-5)
    a.cierto(all(cgm[i]["I"] > cgm[i + 1]["I"] for i in range(len(cgm) - 1)),
             "la I municipal cae en cada orden")
    jc = D["m6"]["join_count"]
    for nombre, x, W, niv, etq, e in (
            ("columbus_cp", col["CP"].to_numpy(dtype=float), W_gal, ("periferia", "centro"), "jc CP", ("perif", "centro")),
            ("municipios_desercion", (y > np.median(y)).astype(float), w_sub.full()[0],
             ("bajo la mediana", "sobre la mediana"), "jc deserción", ("baja", "alta")),
            ("municipios_tipo", (mun["tipo"].to_numpy()[sub] == "Municipio").astype(float),
             w_sub.full()[0], ("no municipalizada o isla", "municipio"), "jc tipo", ("ANM", "muni"))):
        # Los rótulos llevan alias cortos (`etq`, `e`): con los nombres de
        # nivel enteros pasaban de 57 caracteres y el arnés dejaba de
        # contarlos como cubiertos, en silencio.
        r = join_count(x, W)
        t = {f["par"]: f for f in jc[nombre]["tabla"]}
        a.igual(t[f"{niv[0]}:{niv[0]}"]["observado"], r["WW"], f"{etq}: {e[0]}-{e[0]} obs", tol=1e-4)
        a.igual(t[f"{niv[1]}:{niv[1]}"]["observado"], r["BB"], f"{etq}: {e[1]}-{e[1]} obs", tol=1e-4)
        a.igual(t[f"{niv[1]}:{niv[0]}"]["observado"], r["BW"], f"{etq}: mixtos obs", tol=1e-4)
        a.igual(t[f"{niv[0]}:{niv[0]}"]["esperado"], r["E_WW"], f"{etq}: {e[0]}-{e[0]} esp", tol=1e-4)
        a.igual(t[f"{niv[1]}:{niv[1]}"]["esperado"], r["E_BB"], f"{etq}: {e[1]}-{e[1]} esp", tol=1e-4)
        a.igual(t[f"{niv[1]}:{niv[0]}"]["esperado"], r["E_BW"], f"{etq}: mixtos esp", tol=1e-4)
        a.cierto(list(jc[nombre]["n_por_nivel"]) == [int((x == 0).sum()), int((x == 1).sum())],
                 f"{etq}: unidades por nivel")
        a.cierto(t[f"{niv[1]}:{niv[0]}"]["z"] < 0 and t[f"{niv[1]}:{niv[1]}"]["z"] > 0,
                 f"{etq}: menos mixtos, más iguales")
        a.cierto(all(pp["p"] <= 0.001 for pp in jc[nombre]["p_permutacion"]),
                 f"{etq}: p en el suelo")
    a.salta("join count: varianza y z recalculadas", "se auditan por signo; la fórmula de la varianza es de spdep")

    # -----------------------------------------------------------------
    a.titulo("7 · La I bajo once W de Columbus y seis municipales")
    cent = col.geometry.centroid
    xy = np.c_[cent.x, cent.y]
    d = np.sqrt(((xy[:, None, :] - xy[None, :, :]) ** 2).sum(-1))
    np.fill_diagonal(d, np.inf)
    umbral = d.min(axis=1).max()
    nb_col = {
        "gal": nb_gal, "reina": nb_reina,
        "torre": de_w(weights.Rook.from_dataframe(col, use_index=True)),
        "k1": de_w(weights.KNN.from_dataframe(col, k=1, use_index=True)),
        "k3": de_w(weights.KNN.from_dataframe(col, k=3, use_index=True)),
        "k6": de_w(weights.KNN.from_dataframe(col, k=6, use_index=True)),
        "d_mitad": banda(d, umbral * 0.5), "d_conexo": banda(d, umbral),
        "delaunay": de_w(weights.Delaunay(xy)), "gabriel": de_w(weights.Gabriel(xy)),
    }
    pub7 = {e["id"]: e for e in D["m7"]["columbus"]}
    a.cierto(list(pub7.keys())[0] == "gal", "la GAL va la primera de las once")
    for k, v in nb_col.items():
        p = pub7[k]
        a.igual(len(pares_de(v)), p["pares"], f"W {k}: parejas")
        a.igual(sum(1 for i in v if not v[i]), p["islas"], f"W {k}: islas")
        a.igual(moran_con_islas(crime, w_de(v)), p["I"], f"W {k}: I", tol=1e-5)
    a.salta("esfera: recalculada", "libpysal no trae la esfera de influencia")
    a.cierto(pub7["gabriel"]["pares"] <= pub7["esfera"]["pares"] <= pub7["delaunay"]["pares"],
             "esfera: entre Gabriel y Delaunay")
    Is = [e["I"] for e in D["m7"]["columbus"]]
    a.igual(min(Is), D["m7"]["resumen"]["columbus_I"][0], "el mínimo de las once I", tol=1e-4)
    a.igual(max(Is), D["m7"]["resumen"]["columbus_I"][1], "y el máximo", tol=1e-4)
    a.cierto(max(e["p"] for e in D["m7"]["columbus"]) == D["m7"]["resumen"]["columbus_p_max"],
             "y el p máximo es el publicado")
    a.cierto(D["m7"]["resumen"]["columbus_p_max"] < ALFA, "ninguna W deja de rechazar al 5 %")
    a.cierto(pub7["d_mitad"]["p"] == D["m7"]["resumen"]["columbus_p_max"],
             "y la que más se acerca es el umbral a medias")
    # municipios
    msub = mun.iloc[sub].reset_index(drop=True)
    centm = msub.geometry.centroid
    xym = np.c_[centm.x, centm.y]
    mun_t = torre_municipal(mun, PROCESADO / "colombia_adm2.gpkg")
    nb_mun = {
        "reina": nb_sub,
        "torre": {i: [idx[j] for j in mun_t[v] if j in idx] for i, v in enumerate(sub)},
        "k4": de_w(weights.KNN.from_dataframe(msub, k=4, use_index=True)),
        "k8": de_w(weights.KNN.from_dataframe(msub, k=8, use_index=True)),
        "d50": de_w(weights.DistanceBand.from_array(xym, threshold=50e3, binary=True, silence_warnings=True)),
        "delaunay": de_w(weights.Delaunay(xym)),
    }
    pubm = {e["id"]: e for e in D["m7"]["municipios"]}
    for k, v in nb_mun.items():
        p = pubm[k]
        a.igual(len(pares_de(v)), p["pares"], f"municipios W {k}: parejas")
        a.igual(sum(1 for i in v if not v[i]), p["islas"], f"municipios W {k}: islas")
        a.igual(moran_con_islas(y, w_de(v)), p["I"], f"municipios W {k}: I", tol=1e-5)
    a.cierto(D["m7"]["resumen"]["municipios_p_max"] < 1e-50, "las seis W municipales rechazan de sobra")

    # -----------------------------------------------------------------
    a.titulo("8 · Los I locales, con esda y el factor n/(n-1)")
    m8 = D["m8"]["columbus"]
    a.igual(D["m8"]["nsim"], NSIM, "las réplicas del capítulo")
    a.cierto(D["m8"]["p"] == "Pr(folded) Sim", "y el p es el plegado por rangos")
    ml = Moran_Local(crime, w_gal, transformation="r", permutations=NSIM, seed=SEMILLA, n_jobs=1)
    Ii_pub = ccsv["Ii"].to_numpy()
    a.igual(np.abs(ml.Is * n / (n - 1) - Ii_pub).max(), 0.0, "Ii = esda × n/(n-1), los 49", tol=1e-6)
    a.igual(np.abs(np.asarray(m8["Ii"]) - np.round(Ii_pub, 5)).max(), 0.0, "y los Ii del JSON son los del CSV", tol=1e-5)
    a.igual(Ii_pub.mean(), m8["I"], "la media de los Ii es I", tol=1e-6)
    a.igual(Ii_pub.sum() / m8["S0"], m8["I"], "la suma de los Ii entre S0 es I", tol=1e-6)
    a.igual(m8["media_Ii"], m8["I"], "y el generador lo publica", tol=1e-9)
    qmap = {1: "High-High", 2: "Low-High", 3: "Low-Low", 4: "High-Low"}
    q_esda = np.array([qmap[int(v)] for v in ml.q])
    a.cierto((q_esda == ccsv["cuadrante"].to_numpy()).all(), "los cuadrantes de esda son los de spdep")
    a.cierto((cuadrante(z, wz) == ccsv["cuadrante"].to_numpy()).all(), "y son los signos de z y Wz")
    p_pub = ccsv["p_rangos"].to_numpy()
    fuera = int(np.sum(np.abs(ml.p_sim - p_pub) > np.array([tol_p(p, NSIM) for p in p_pub])))
    a.cierto(fuera == 0, "los p por rangos coinciden hasta el error de Monte Carlo", f"{fuera} fuera de tolerancia")
    a.igual(p_pub.min(), m8["p_min"], "el p mínimo publicado", tol=1e-9)
    a.cierto(p_pub.min() >= 1.0 / (NSIM + 1), "y no baja del suelo", f"{p_pub.min()} ≥ {m8['suelo']}")
    a.igual(m8["suelo"], 1.0 / (NSIM + 1), "el suelo publicado es 1/(nsim+1)", tol=1e-9)
    a.igual(int(np.sum(p_pub < ALFA)), m8["significativos"], "significativos al 5 %, desde el CSV")
    a.cierto(abs(int(np.sum(ml.p_sim < ALFA)) - m8["significativos"]) <= 3,
             "y esda cuenta casi los mismos", f"esda {int(np.sum(ml.p_sim < ALFA))}")
    # municipios
    m8m = D["m8"]["municipios"]
    st = (PROCESADO / "colombia_adm2.gpkg").stat()
    llave_l = f"{st.st_size}·{int(st.st_mtime)}·{len(sub)}·{NSIM}·{SEMILLA}·v2"

    def _locales():
        mlm = Moran_Local(y, w_sub, transformation="r", permutations=NSIM, seed=SEMILLA, n_jobs=1)
        gl = G_Local(y, w_sub, transform="B", star=True, permutations=NSIM, seed=SEMILLA, n_jobs=1)
        return {"Is": mlm.Is, "p_sim": mlm.p_sim, "q": mlm.q.astype(float),
                "p_z_sim": mlm.p_z_sim, "Zs": gl.Zs, "g_p_sim": gl.p_sim}
    L = cache_local(llave_l, _locales)
    nm = len(sub)
    Ii_m = mcsv["Ii"].to_numpy()
    a.igual(np.abs(L["Is"] * nm / (nm - 1) - Ii_m)[con].max(), 0.0, "municipios: Ii = esda × n/(n-1)", tol=1e-6)
    a.igual(np.abs(Ii_m[~con]).max(), 0.0, "y las islas tienen Ii = 0", tol=1e-12)
    a.igual(Ii_m.sum() / w_sub.full()[0].sum(), m8m["suma_Ii_sobre_S0"], "suma de Ii entre S0", tol=1e-6)
    a.igual(m8m["suma_Ii_sobre_S0"], me.I, "y ES el I de esda, con n = todas", tol=1e-6)
    a.igual(m8m["I_esda_equivalente"], me.I, "el generador lo publica con ese nombre", tol=1e-6)
    a.igual(m8m["factor_islas"], nm / con.sum(), "y el factor es n/n_con", tol=1e-6)
    a.igual(m8m["I"] * m8m["factor_islas"], m8m["I_esda_equivalente"], "I de spdep × factor = I de esda", tol=1e-5)
    p_m = mcsv["p_rangos"].to_numpy()
    a.cierto(np.isnan(p_m[~con]).all() and not np.isnan(p_m[con]).any(), "el p municipal es NA solo en las islas")
    fuera = int(np.sum(np.abs(L["p_sim"][con] - p_m[con]) > np.array([tol_p(p, NSIM) for p in p_m[con]])))
    a.cierto(fuera == 0, "municipios: p por rangos hasta el error de Monte Carlo", f"{fuera} fuera")
    a.igual(int(np.sum(p_m[con] < ALFA)), m8m["significativos"], "municipios: significativos, desde el CSV")
    a.cierto(abs(int(np.sum(L["p_sim"][con] < ALFA)) - m8m["significativos"]) <= 6,
             "y esda cuenta casi los mismos", f"esda {int(np.sum(L['p_sim'][con] < ALFA))}")
    a.igual(np.nanmin(p_m), m8m["p_min"], "municipios: p mínimo", tol=1e-9)
    a.igual(Ii_m.max(), m8m["Ii_max"], "el Ii máximo", tol=1e-5)
    top = np.argsort(-np.abs(Ii_m))[:5]
    a.cierto([t["municipio"] for t in m8m["top5"]] == mcsv["municipio"].to_numpy()[top].tolist(),
             "los cinco Ii mayores son los que el JSON nombra")
    a.igual(m8m["top5"][0]["Ii"], Ii_m[top[0]], "y el primero trae su Ii", tol=1e-5)

    # -----------------------------------------------------------------
    a.titulo("9 · El mapa LISA: categorías desde los p publicados")
    m9 = D["m9"]
    a.cierto(len(m9["niveles"]) == 5 and len(m9["colores"]) == 5, "cinco niveles y cinco colores")
    a.igual(m9["alfa"], ALFA, "al 5 %")
    lc = lisa_codigo(ccsv["cuadrante"].to_numpy(), p_pub)
    a.cierto((lc == ccsv["lisa"].to_numpy()).all(), "Columbus: los códigos LISA salen del p y el cuadrante")
    a.cierto(list(m9["columbus"]["conteo"]) == conteo(lc, 5), "Columbus: el recuento por categoría")
    a.igual(sum(m9["columbus"]["conteo"]), n, "y suma 49")
    a.cierto(set(m9["columbus"]["alto_alto_polyid"]) == set(pol[lc == 2].tolist()), "los POLYID alto-alto")
    a.cierto(set(m9["columbus"]["bajo_bajo_polyid"]) == set(pol[lc == 3].tolist()), "los POLYID bajo-bajo")
    a.cierto(set(m9["columbus"]["atipicos_polyid"]) == set(pol[lc >= 4].tolist()), "los atípicos")
    lm_ = lisa_codigo(mcsv["cuadrante"].to_numpy(), p_m)
    lisa_m = mcsv["lisa"].to_numpy(dtype=float)
    a.cierto(np.array_equal(np.isnan(lm_), np.isnan(lisa_m)) and (lm_[con] == lisa_m[con]).all(),
             "municipios: los códigos LISA salen del p y el cuadrante")
    a.cierto(list(m9["municipios"]["conteo"]) == conteo(lisa_m, 5), "municipios: el recuento")
    a.igual(m9["municipios"]["sin_vecinos"], int(np.sum(~con)), "y las islas van sin categoría")
    a.igual(sum(m9["municipios"]["conteo"]) + m9["municipios"]["sin_vecinos"], nm, "y todo suma 1 121")
    isl = m9["municipios"]["islas"]
    a.cierto(set(isl["municipio"]) == set(mcsv["municipio"].to_numpy()[~con].tolist()),
             "las islas son San Andrés y Providencia", str(isl["municipio"]))
    a.cierto(all(q == "Low-Low" for q in isl["cuadrante_spdep"]),
             "y spdep les asigna bajo-bajo con rezago cero")
    dep = mcsv["departamento"].to_numpy()
    tt = pd.Series(dep[lisa_m == 2]).value_counts()
    a.cierto(m9["municipios"]["alto_alto_por_departamento"][0]["departamento"] == tt.index[0]
             and m9["municipios"]["alto_alto_por_departamento"][0]["n"] == int(tt.iloc[0]),
             "el departamento con más alto-alto", f"{tt.index[0]} {int(tt.iloc[0])}")
    tb = pd.Series(dep[lisa_m == 3]).value_counts()
    a.cierto(m9["municipios"]["bajo_bajo_por_departamento"][0]["n"] == int(tb.iloc[0]),
             "y el que más bajo-bajo", f"{tb.index[0]} {int(tb.iloc[0])}")

    # -----------------------------------------------------------------
    a.titulo("10 · La multiplicidad: suelo, tabla y Benjamini-Hochberg")
    m10 = D["m10"]
    for cual, nn in (("columbus", n), ("municipios", nm)):
        s = m10["suelo"][cual]
        a.igual(s["n"], nn, f"suelo {cual}: n")
        a.igual(s["umbral_bonferroni"], ALFA / nn, f"suelo {cual}: alfa/n", tol=1e-6)
        a.igual(s["nsim_minimo"], int(np.ceil(nn / ALFA) - 1), f"suelo {cual}: réplicas mínimas")
    a.cierto(m10["suelo"]["municipios"]["nsim_minimo"] > 999, "con 999 réplicas Bonferroni no es alcanzable")
    a.cierto(NSIM > m10["suelo"]["municipios"]["nsim_minimo"], "y con las del capítulo sí")
    for cual, p_col, csv_ in (("columbus", p_pub, ccsv), ("municipios", p_m, mcsv)):
        t = m10[cual]["tabla"]
        # Un auditor que muere no informa (§0.6, trampa 7): la fila que falte
        # se declara y las comprobaciones que la necesitan fallan, no revientan.
        a.cierto(set(t.keys()) == {"plegado_999", "plegado_nsim", "bilateral_999", "bilateral_nsim",
                                   "normal_permutado_999", "normal_permutado_nsim", "analitico"},
                 f"{cual}: las siete filas de la tabla")
        fila = t.get("plegado_nsim", {})
        a.igual(fila.get("nsim", -1), NSIM, f"{cual}: la fila del capítulo usa sus réplicas")
        pv = p_col[~np.isnan(p_col)]
        a.igual(fila.get("sin_corregir", -1), int(np.sum(pv < ALFA)), f"{cual}: sin corregir, desde el CSV")
        a.igual(fila.get("bonferroni", -1), bonferroni(pv), f"{cual}: Bonferroni, desde el CSV")
        a.igual(fila.get("fdr", -1), bh(pv), f"{cual}: FDR por Benjamini-Hochberg, a mano")
        a.cierto(fila.get("holm", -1) >= fila.get("bonferroni", 0), f"{cual}: Holm no rechaza menos que Bonferroni")
        a.cierto(fila.get("fdr", -1) >= fila.get("holm", 0), f"{cual}: FDR no rechaza menos que Holm")
        a.cierto(t.get("bilateral_nsim", {}).get("sin_corregir", 10 ** 9) <= fila.get("sin_corregir", -1),
                 f"{cual}: el p bilateral rechaza menos que el plegado")
        a.cierto(t.get("plegado_999", {}).get("nsim") == 999 and t.get("analitico", {}).get("nsim") == 0,
                 f"{cual}: la tabla lleva 999 y el analítico")
        cod_b = lisa_codigo(csv_["cuadrante"].to_numpy(), np.where(np.isnan(p_col), np.nan,
                                                                     np.minimum(p_col * len(pv), 1.0)))
        a.cierto(np.array_equal(np.nan_to_num(cod_b, nan=-1), np.nan_to_num(csv_["lisa_bonferroni"].to_numpy(dtype=float), nan=-1)),
                 f"{cual}: los códigos con Bonferroni, desde el p")
        a.cierto(list(m10[cual]["conteo_bonferroni"]) == conteo(csv_["lisa_bonferroni"].to_numpy(dtype=float), 5),
                 f"{cual}: el recuento con Bonferroni")
        a.cierto(list(m10[cual]["conteo_fdr"]) == conteo(csv_["lisa_fdr"].to_numpy(dtype=float), 5),
                 f"{cual}: el recuento con FDR")
        a.igual(sum(m10[cual]["conteo_fdr"][1:]), fila.get("fdr", -1), f"{cual}: FDR cuadra con su mapa")
        a.igual(sum(m10[cual]["conteo_bonferroni"][1:]), fila.get("bonferroni", -1), f"{cual}: Bonferroni cuadra con su mapa")
    a.cierto(m10["municipios"]["tabla"].get("plegado_999", {}).get("bonferroni", -1) == 0,
             "municipios: con 999 réplicas Bonferroni deja cero")
    a.cierto(m10["municipios"]["tabla"].get("plegado_nsim", {}).get("bonferroni", 0) > 0, "y con las del capítulo deja algo")
    pzs = int(np.sum(2 * L["p_z_sim"][con] < ALFA))      # esda lo da unilateral; spdep, bilateral
    a.cierto(abs(pzs - m10["municipios"]["tabla"].get("normal_permutado_nsim", {}).get("sin_corregir", -99)) <= 8,
             "el p normal con momentos permutados, contra el de esda", f"esda {pzs}")
    bhp = m10["columbus"]["bh"]
    a.cierto(np.allclose(np.sort(p_pub), bhp["p_ordenados"], atol=1e-5), "BH: los p ordenados son los del CSV")
    a.cierto(np.allclose(np.arange(1, n + 1) * ALFA / n, bhp["umbrales"], atol=1e-5), "BH: los umbrales i·alfa/n")
    a.igual(bhp["k"], bh(p_pub), "BH: el k, a mano")
    a.cerca(bhp["umbral_bonferroni"], ALFA / n, "y el umbral de Bonferroni", rel=1e-3)
    a.salta("999 frente a 24 999 réplicas: recalculado", "dos generadores; se auditan propiedades")
    a.igual(m10["municipios"]["cuadrantes_cambian"], 0, "los cuadrantes no dependen de las réplicas")
    a.cierto(0 < m10["municipios"]["significativos_cambian"] < 50, "el conjunto significativo sí cambia, poco")

    # -----------------------------------------------------------------
    a.titulo("11 · Getis-Ord: la rejilla original, Columbus y los municipios")
    g = D["m11"]["getisord"]
    val = gocsv["val"].to_numpy(dtype=float)
    gxy = np.c_[gocsv["x"], gocsv["y"]]
    a.igual(len(val), g["n"], "la rejilla: 256 celdas")
    a.cierto(len(np.unique(gxy[:, 0])) == 16 and len(np.unique(gxy[:, 1])) == 16, "y es 16 × 16")
    w30 = weights.DistanceBand.from_array(gxy, threshold=g["umbral"], binary=True, silence_warnings=True)
    a.igual(np.mean([len(w30.neighbors[k]) for k in w30.id_order]), g["vecinos_medio"], "vecinos medios a 30", tol=1e-4)
    G30 = G_Local(val, w30, transform="B", star=False, permutations=0)
    G30s = G_Local(val, w30, transform="B", star=True, permutations=0)
    a.igual(np.abs(G30.Zs - gocsv["G30"].to_numpy()).max(), 0.0, "Gi (z) en las 256 celdas", tol=1e-6)
    a.igual(np.abs(G30s.Zs - gocsv["G30_estrella"].to_numpy()).max(), 0.0, "Gi* (z) en las 256", tol=1e-6)
    c = g["celda"] - 1
    a.igual(G30.Zs[c], g["G"], "celda 120: Gi", tol=1e-4)
    a.igual(G30s.Zs[c], g["G_estrella"], "celda 120: Gi*", tol=1e-4)
    n1 = G30s.Zs[c] * (np.sqrt(((val - val.mean()) ** 2).sum() / len(val)) / val.std(ddof=1))
    a.igual(n1, g["G_estrella_n1"], "celda 120: Gi* con n-1", tol=1e-4)
    a.igual(n1, 1.448, "Getis y Ord (1996), p. 267, vía spdep", tol=1e-3)
    a.igual(np.abs(G30.Zs - G30s.Zs).max(), g["dif_max_G_Gestrella"], "la mayor diferencia Gi frente a Gi*", tol=1e-4)
    for b in g["barrido"]:
        wd = weights.DistanceBand.from_array(gxy, threshold=b["d"], binary=True, silence_warnings=True)
        a.igual(G_Local(val, wd, transform="B", star=True, permutations=0).Zs[c], b["G_estrella"],
                f"barrido d={b['d']}: Gi* de la celda", tol=1e-4)
    gp = G_Local(val, w30, transform="B", star=True, permutations=NSIM, seed=SEMILLA, n_jobs=1)
    a.cierto(abs(gp.p_sim[c] - g["G_estrella_p"]) < tol_p(g["G_estrella_p"], NSIM), "celda 120: p por rangos (esda)")
    cal = int(np.sum((gp.p_sim < ALFA) & (gp.Zs > 0)))
    a.cierto(abs(cal - g["calientes_95"]) <= 6, "celdas calientes al 5 %, casi las mismas", f"esda {cal}")
    # Columbus
    # Con `transform="R"` esda 2.9.0 infla la varianza de Gi* por 8: se
    # audita en binario, que es lo mismo porque la z de Gi* no cambia al
    # reescalar cada fila, y se comprueba además con Ord y Getis a mano.
    gc = G_Local(crime, w_gal, transform="B", star=True, permutations=NSIM, seed=SEMILLA, n_jobs=1)
    gz_pub = ccsv["gistar_z"].to_numpy()
    a.igual(np.abs(gc.Zs - gz_pub).max(), 0.0, "Columbus: Gi* (z) en los 49, esda en binario", tol=1e-6)
    a.igual(np.abs(gistar_a_mano(crime, nb_gal) - gz_pub).max(), 0.0,
            "y con las ecuaciones de Ord y Getis (1995) a mano", tol=1e-6)
    gR = G_Local(crime, w_gal, transform="R", star=True, permutations=0)
    a.cierto(np.abs(gR.Zs - gz_pub).max() > 1.0,
             "esda con pesos por filas NO da esa z: defecto declarado",
             f"máx dif {np.abs(gR.Zs - gz_pub).max():.3f}")
    gpp = ccsv["gistar_p"].to_numpy()
    fuera = int(np.sum(np.abs(gc.p_sim - gpp) > np.array([tol_p(p, NSIM) for p in gpp])))
    a.cierto(fuera == 0, "Columbus: p de Gi* hasta el error de Monte Carlo", f"{fuera} fuera")
    gcod = gistar_codigo(gz_pub, gpp)
    a.cierto((gcod == ccsv["gistar"].to_numpy()).all(), "Columbus: los siete códigos salen de z y p")
    m11c = D["m11"]["columbus"]
    a.cierto(list(m11c["conteo"]) == conteo(gcod, 7), "Columbus: el recuento de Gi*")
    a.igual(gz_pub.max(), m11c["z_max"], "Columbus: z máxima", tol=1e-4)
    a.igual(pol[int(np.argmax(gz_pub))], m11c["polyid_z_max"], "y su POLYID")
    for cr in m11c["cruce"]:
        k = D["m9"]["niveles"].index(cr["lisa"]) + 1
        a.igual(cr["caliente"], int(np.sum((lc == k) & (gcod >= 5))), f"cruce {cr['lisa']}: calientes")
        a.igual(cr["frio"], int(np.sum((lc == k) & (gcod <= 3))), f"cruce {cr['lisa']}: fríos")
    a.cierto(all(cr["frio"] == 0 for cr in m11c["cruce"] if cr["lisa"] == "Alto-alto"),
             "ningún alto-alto sale frío")
    # municipios
    gzm = mcsv["gistar_z"].to_numpy()
    a.igual(np.abs(L["Zs"] - gzm)[con].max(), 0.0, "municipios: Gi* (z), con esda", tol=1e-6)
    gpm = mcsv["gistar_p"].to_numpy()
    fuera = int(np.sum(np.abs(L["g_p_sim"][con] - gpm[con]) > np.array([tol_p(p, NSIM) for p in gpm[con]])))
    a.cierto(fuera == 0, "municipios: p de Gi* hasta el error de Monte Carlo", f"{fuera} fuera")
    gcm = gistar_codigo(gzm, gpm)
    gcm[~con] = np.nan
    gist_m = mcsv["gistar"].to_numpy(dtype=float)
    a.cierto(np.array_equal(np.isnan(gcm), np.isnan(gist_m)) and (gcm[con] == gist_m[con]).all(),
             "municipios: códigos de Gi* desde z y p, islas sin código")
    m11m = D["m11"]["municipios"]
    a.cierto(list(m11m["conteo"]) == conteo(gist_m, 7), "municipios: el recuento de Gi*")
    a.cierto(mcsv["municipio"].to_numpy()[int(np.argmax(gzm))] == m11m["municipio_z_max"],
             "el municipio de mayor Gi*", m11m["municipio_z_max"])
    for cr in m11m["cruce"]:
        k = D["m9"]["niveles"].index(cr["lisa"]) + 1
        a.igual(cr["caliente"], int(np.sum((lisa_m == k) & (gist_m >= 5))), f"municipios cruce {cr['lisa']}: calientes")
        a.igual(cr["frio"], int(np.sum((lisa_m == k) & (gist_m <= 3))), f"municipios cruce {cr['lisa']}: fríos")
    ab = next(cr for cr in m11m["cruce"] if cr["lisa"] == "Alto-bajo")
    a.cierto(ab["frio"] > 0 and ab["caliente"] == 0, "los alto-bajo municipales salen fríos, no calientes")

    # -----------------------------------------------------------------
    a.titulo("12 · Los mapas")
    # Los rótulos NO llevan el id del mapa entero: `cap7-getisord-valor` más
    # el texto del núcleo pasaba de 57 caracteres y el arnés dejaba de
    # contar esa comprobación. Cada mapa lleva un alias corto.
    ETQ = {"cap7-columbus": "mapa columbus", "cap7-w": "mapa w", "cap7-municipios": "mapa municipios",
           "cap7-getisord-valor": "go-valor", "cap7-getisord-g": "go-g"}
    for nombre, modo in (("cap7-columbus", "poligonos"), ("cap7-w", "grafo"), ("cap7-municipios", "poligonos"),
                         ("cap7-getisord-valor", "rejilla"), ("cap7-getisord-g", "rejilla")):
        etq = ETQ[nombre]
        a.cierto(nombre in M, f"{etq}: está en el JSON de mapas")
        if nombre in M:
            audita_geomapa(a, M[nombre], etq, presupuesto_kb=220.0)
            a.cierto(M[nombre].get("modo") == modo, f"{etq}: su modo es {modo}", str(M[nombre].get("modo")))

    def capa_cat(mapa, id_, K, etq):
        cp = next((c for c in mapa.get("capas", []) if c["id"] == id_), None)
        a.cierto(cp is not None, f"{etq}/{id_}: la capa existe")
        if cp is None:
            return None
        a.cierto(cp.get("tipo") == "categoria", f"{etq}/{id_}: es categórica")
        a.cierto(len(cp.get("niveles", [])) == K and len(cp.get("colores", [])) == K,
                 f"{etq}/{id_}: {K} niveles y {K} colores")
        v = np.array([np.nan if x is None else x for x in cp.get("valor", [])], dtype=float)
        a.igual(len(v), mapa.get("n", -1), f"{etq}/{id_}: un valor por rasgo")
        if len(v) != mapa.get("n", -1):
            return None                      # lo demás indexaría fuera: se informa y se sigue
        pres = v[~np.isnan(v)]
        a.cierto(len(pres) == 0 or (pres.min() >= 1 and pres.max() <= K), f"{etq}/{id_}: códigos en 1..{K}")
        a.cierto(list(cp.get("tam", [])) == conteo(v, K), f"{etq}/{id_}: el recuento por nivel")
        a.igual(cp.get("n_sin_dato", -1), int(np.isnan(v).sum()), f"{etq}/{id_}: los sin dato")
        return v

    mc = M.get("cap7-columbus", {})
    a.cierto(list(mc.get("polyid", [])) == pol.tolist(), "mapa columbus: lleva los POLYID en el orden del CSV")
    a.cierto([c["id"] for c in mc.get("capas", [])] == ["crime", "lisa", "lisa_bonferroni", "lisa_fdr", "gistar"],
             "mapa columbus: sus cinco capas")
    cc = next((c for c in mc.get("capas", []) if c["id"] == "crime"), {})
    vc = np.asarray(cc.get("valor", [0]), dtype=float)
    a.cierto(len(vc) == n and np.abs(vc - crime).max() < 1e-6, "mapa columbus/crime: es CRIME")
    a.cierto(cc.get("tipo") is None and "cortes" in cc, "mapa columbus/crime: numérica, con cortes")
    for id_, K, ref in (("lisa", 5, lc), ("lisa_bonferroni", 5, ccsv["lisa_bonferroni"].to_numpy(dtype=float)),
                        ("lisa_fdr", 5, ccsv["lisa_fdr"].to_numpy(dtype=float)), ("gistar", 7, gcod)):
        v = capa_cat(mc, id_, K, "mapa columbus")
        if v is not None:
            a.cierto((v == ref).all(), f"mapa columbus/{id_}: códigos = CSV")
    mmap = M.get("cap7-municipios", {})
    a.igual(mmap.get("n", -1), len(mun), "mapa municipios: los 1 122")
    dcap = next((c for c in mmap.get("capas", []) if c["id"] == "desercion"), {})
    vd = np.array([np.nan if x is None else x for x in dcap.get("valor", [])], dtype=float)
    a.cierto(len(vd) == len(mun) and np.isnan(vd).sum() == 1 and np.allclose(vd[sub], y),
             "mapa municipios/desercion: la deserción, con su hueco")
    for id_, K, ref in (("lisa", 5, lisa_m), ("lisa_bonferroni", 5, mcsv["lisa_bonferroni"].to_numpy(dtype=float)),
                        ("lisa_fdr", 5, mcsv["lisa_fdr"].to_numpy(dtype=float)), ("gistar", 7, gist_m)):
        v = capa_cat(mmap, id_, K, "mapa municipios")
        if v is not None:
            a.cierto(np.array_equal(np.nan_to_num(v[sub], nan=-1), np.nan_to_num(ref, nan=-1)),
                     f"mapa municipios/{id_}: códigos = CSV")
            a.igual(int(np.isnan(v).sum()), 3, f"mapa municipios/{id_}: sin dato + 2 islas = 3")
    gw = M.get("cap7-w", {})
    a.cierto(list(gw.get("variantes", {}).keys()) == list(pub7.keys()), "mapa w: las once variantes, en orden")
    for k, v in gw.get("variantes", {}).items():
        a.igual(v.get("n_aristas", -1), pub7[k]["pares"], f"variante {k}: sus aristas son las parejas")
        if k in nb_col:
            ar = np.asarray(v.get("aristas", []), dtype=int).reshape(-1, 2) - 1
            a.cierto({tuple(sorted(p)) for p in ar.tolist()} == pares_de(nb_col[k]),
                     f"variante {k}: y son las mismas que libpysal")
    for nombre, ref in (("cap7-getisord-valor", val), ("cap7-getisord-g", gocsv["G30_estrella"].to_numpy())):
        r = M.get(nombre, {})
        etq = ETQ[nombre]
        a.cierto(r.get("nx") == 16 and r.get("ny") == 16 and len(r.get("zq", [])) == 256, f"{etq}: 16 × 16")
        a.igual(r.get("rango", [0, 0])[0], ref.min(), f"{etq}: su mínimo", tol=1e-4)
        a.igual(r.get("rango", [0, 0])[1], ref.max(), f"{etq}: su máximo", tol=1e-4)

    # -----------------------------------------------------------------
    a.titulo("13 · Discrepancias declaradas y formato")
    disc = {d["id"]: d for d in D.get("discrepancias", [])}
    a.cierto("moran_islas" in disc and "p_permutacion" in disc, "las dos discrepancias van declaradas")
    if "moran_islas" in disc:
        a.igual(disc["moran_islas"]["valor_python"], me.I, "moran_islas: el valor de Python ES el de esda", tol=1e-6)
        a.igual(disc["moran_islas"]["valor_r"], mm["I"], "moran_islas: el de R es el del módulo 3", tol=1e-9)
    txt = p_datos.read_text(encoding="utf-8")
    a.cierto("Ã" not in txt and "�" not in txt, "datos: las tildes están intactas")
    a.cierto("ó" in txt or "í" in txt, "y hay tildes de verdad que comprobar")
    excesivos = [(r, k) for r, k in decimales(D) if k > 10]
    a.cierto(not excesivos, "ningún flotante pasa de 10 decimales", str(excesivos[:3]))
    a.igual(D["meta"]["capitulo"], 7, "la metainformación dice capítulo 7")
    a.cierto(D["meta"]["semanas"] == "12-13", "y que cubre las semanas 12 y 13", D["meta"]["semanas"])
    a.cierto(D["meta"]["anclas"] >= 13, "el generador comprobó sus anclas", f"{D['meta']['anclas']} anclas")
    a.igual(D["meta"]["nsim"], 24999, "las réplicas del capítulo son 24 999")
    a.cierto(D["meta"]["p"] == "Pr(folded) Sim", "y el p es el plegado por rangos")

    return a.cierre()


if __name__ == "__main__":
    raise SystemExit(main())
