#!/usr/bin/env python3
"""
audita_preparcial2.py — auditoría independiente del preparcial del Corte II (P1.2)

Material de Estadística Espacial 2026-II (20929). Ver PLAN_Preparcial_Corte_2.md.

Comprueba que los números del preparcial sean ciertos por caminos que no pasan
por R, y que lo publicado diga lo que el precálculo calculó. Es el hermano de
`audita_preparcial1.py` y hereda sus dos razones de ser —la SINCRONÍA con los
capítulos de los que cita cifras, y que las preguntas no viven en el JSON sino
en el HTML— más una tercera, propia de este documento: los cinco ejercicios
sobre Murchison, cuyas cifras salen de un patrón que ningún capítulo calculó.

LAS SIETE FAMILIAS

  1. **Cifras nuevas**, rehechas en Python desde la fuente: los `.gpkg` de
     Bogotá, las coordenadas del rebarajado que publicó el capítulo 4 y los
     CSV de Murchison que exporta el generador. Lo que solo sabe hacer
     spatstat —selectores, `ppm`, `kppm`, envolventes, `rhohat`— NO se finge
     rehecho: se comprueba su coherencia interna y se dice que es eso.
  2. **Sincronía** — cada cifra reutilizada y cada serie de gráfico contra su
     ruta en `cap4/cap5_datos.json`, y el JSON incrustado contra el del disco.
  3. **Cobertura** — 22 de 22 módulos con pregunta, ninguna fuera, y el
     `repaso` de cada una resuelto contra el capítulo publicado.
  4. **Retroalimentación completa** — toda opción con su retro, distinta de
     sus hermanas, y el número de correctas que pide su tipo.
  5. **No filtración** — ni el enunciado ni la pista regalan la correcta; ni
     la posición ni la LONGITUD la delatan (§13.3 del plan del Corte I).
  6. **Ejercicios** — toda demanda del enunciado contestada bajo su fragmento
     literal, y toda cifra de una respuesta presente en el JSON.
  7. **Catálogo** — cada error cita cifras que existen y apunta dentro del
     alcance.

UNA CIFRA QUE PYTHON NO REPRODUCE, Y POR QUÉ (2026-10-03)

La K̂(10 km) con corrección de traslación dentro del greenstone sale 499.70 en
R y 487.48 rehecha aquí con los solapes EXACTOS de shapely. No es un error de
ninguno de los dos: sobre una ventana poligonal, `Kest` calcula el solape de
la ventana con su trasladada aproximando la covarianza del conjunto con una
rejilla de píxeles, y el greenstone —133 anillos, piezas estrechas— es justo
la ventana donde esa aproximación se nota. El ejercicio publica la cifra que
el estudiante obtendrá en R, y aquí se exige que la exacta quede a menos de un
3 % y que el orden que la respuesta afirma —sin corregir < πr² < corregida— se
cumpla con las dos.

Uso:  <geo_env>/python precalculo/audita_preparcial2.py
PREPARCIAL2_DATOS, PREPARCIAL2_HTML, PREPARCIAL2_CAPS y PREPARCIAL2_MURCHISON apuntan a copias con
defectos inyectados (lo hace `prueba_auditor_preparcial2.py`).
"""
from __future__ import annotations

import html as html_mod
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
PROCESADO = RAIZ / "datos" / "procesado"
HTMLS = RAIZ / "Htmls_Espacial"

from audita_base import Auditoria  # noqa: E402
from audita_preparcial1 import lee_autoevaluaciones  # noqa: E402
import alcance_preparcial2 as ALC  # noqa: E402

RUTA_DATOS = pathlib.Path(os.environ.get("PREPARCIAL2_DATOS") or SALIDAS / "preparcial2_datos.json")
RUTA_HTML = pathlib.Path(os.environ.get("PREPARCIAL2_HTML") or HTMLS / "preparcial-corte-2.html")
RUTA_CAPS = pathlib.Path(os.environ.get("PREPARCIAL2_CAPS") or SALIDAS)
# Los CSV de Murchison son salida del generador, no de un capítulo: viven
# aparte para que el arnés los pueda envenenar sin tocar los capítulos.
RUTA_MURCH = pathlib.Path(os.environ.get("PREPARCIAL2_MURCHISON") or SALIDAS)

# Constantes de DISEÑO que la prosa de los ejercicios puede escribir sin que
# salgan del JSON: la semilla, el 5 del supuesto del χ², el 10 de «10⁶», el 0
# y el 1 de una covariable indicadora y de «J = 1», el 2 de «2n». Ninguna es un
# resultado. Si una respuesta escribe otra cifra, tiene que estar en el JSON.
DISENO = {0.0, 1.0, 2.0, 5.0, 10.0, 2026.0}

# Las demandas de un enunciado, como en genera_preparcial2.R pero escritas
# aquí otra vez: una copia de la misma regla en otro lenguaje es lo que hace
# que esta comprobación no herede un error del generador.
DEMANDA = re.compile(r"(?<![^\W\d_])(?:[Dd]i|[Ee]xplica|[Cc]ontesta|[Cc]ompara|[Dd]ecide)(?![^\W\d_])|¿")

POSICIONALES = [
    re.compile(r"\blas (dos|tres|cuatro) primeras\b", re.I),
    re.compile(r"\bla (primera|segunda|tercera|cuarta|última) opción\b", re.I),
    re.compile(r"\bla opción [a-e]\)", re.I),
    re.compile(r"\blas primeras\b", re.I),
    re.compile(r"\bla de arriba\b|\bla de abajo\b", re.I),
    re.compile(r"\bque la anterior\b|\bla opción siguiente\b|\bla de antes\b", re.I),
]


def en_ruta(obj, ruta: str):
    """El resolutor de rutas de R, con los índices en base 1."""
    cur = obj
    for p in ruta.split("."):
        m = re.match(r"^([^\[]*)(\[(\d+)\])?$", p)
        if not m:
            return None
        nombre, idx = m.group(1), m.group(3)
        if nombre:
            if not isinstance(cur, dict) or nombre not in cur:
                return None
            cur = cur[nombre]
        if idx:
            i = int(idx) - 1
            if not isinstance(cur, list) or i >= len(cur):
                return None
            cur = cur[i]
    return cur


def plano(t: str) -> str:
    return html_mod.unescape(re.sub(r"<[^>]+>", "", t))


def iguales(a, b, rel=1e-9) -> bool:
    if isinstance(a, list) and isinstance(b, list):
        return len(a) == len(b) and all(iguales(x, y, rel) for x, y in zip(a, b))
    if isinstance(a, (int, float)) and isinstance(b, (int, float)) and not isinstance(a, bool):
        return abs(float(a) - float(b)) <= rel * max(1.0, abs(float(a)), abs(float(b)))
    return a == b


class Familias:
    """El recuento POR FAMILIA, que es lo que hace legible un fallo."""

    def __init__(self, a: Auditoria):
        self.a, self.marcas, self.actual = a, [], None

    def abre(self, k: int, titulo: str):
        self.cierra()
        self.a.titulo(f"{k}. {titulo}")
        self.actual = (k, titulo, self.a.n, len(self.a.fallos))

    def cierra(self):
        if self.actual:
            k, t, n0, f0 = self.actual
            self.marcas.append((k, t, self.a.n - n0, len(self.a.fallos) - f0))
            self.actual = None

    def resumen(self):
        self.cierra()
        print("\n=== Recuento por familia " + "=" * 38)
        for k, t, n, f in self.marcas:
            print(f"  {k}. {t[:46]:<46} {n:>4} comprobaciones · {f} fallos")


# =====================================================================
# FAMILIA 1 · las cifras nuevas
# =====================================================================
def _dentro(geoms, xs, ys):
    import geopandas as gpd
    pts = gpd.GeoSeries(gpd.points_from_xy(xs, ys))
    return pts.within(geoms).to_numpy()


def _nn_medio(P):
    from scipy.spatial import cKDTree
    d, _ = cKDTree(P).query(P, k=2)
    return float(d[:, 1].mean())


def _binado(v, lo, hi, k):
    """El de quadratcount: celdas abiertas por la izquierda y cerradas por la
    derecha, salvo la más baja, cerrada por los dos lados (cut())."""
    import numpy as np
    cortes = np.linspace(lo, hi, k + 1)
    return np.clip(np.searchsorted(cortes, v, "left") - 1, 0, k - 1)


def _chi2_rect(P, caja, k):
    import numpy as np
    x0, x1, y0, y1 = caja
    ix, iy = _binado(P[:, 0], x0, x1, k), _binado(P[:, 1], y0, y1, k)
    O = np.zeros((k, k))
    np.add.at(O, (ix, iy), 1)
    E = len(P) / k ** 2
    return float(((O - E) ** 2 / E).sum()), E


def familia_1(a: Auditoria, D: dict, caps: dict):
    import numpy as np
    import pandas as pd
    import geopandas as gpd
    from scipy.stats import chi2 as chi2_dist
    NV, EJ = D["nuevo"], D["ejercicios"]

    # --- A3 · la R ingenua de las mismas sedes con dos ventanas -----------
    cole = gpd.read_file(PROCESADO / "bogota_colegios.gpkg")
    for nombre, archivo, clave_n, clave_ce in (
            ("urbana", "bogota_ventana_urbana.gpkg", "n_urb", "ce_urb"),
            ("D.C.", "bogota_ventana_dc.gpkg", "n_dc", "ce_dc")):
        W = gpd.read_file(PROCESADO / archivo).geometry.union_all()
        m = cole.geometry.within(W).to_numpy()
        P = np.column_stack([cole.geometry.x.to_numpy()[m], cole.geometry.y.to_numpy()[m]])
        a.igual(m.sum(), NV["ce_ventana"][clave_n], f"A3 · sedes dentro de la ventana {nombre}", tol=0)
        ce = _nn_medio(P) * 2 * math.sqrt(len(P) / W.area)
        a.cerca(ce, NV["ce_ventana"][clave_ce], f"A3 · R ingenua, ventana {nombre}", rel=1e-6)
    a.cierto(NV["ce_ventana"]["ce_dc"] < NV["ce_ventana"]["ce_urb"],
             "A3 · con el D.C. la R baja, como dice la pregunta")

    # --- A5 · el rebarajado a 5 × 5 y a 10 × 10 ---------------------------
    m5 = caps["cap4"]["m5"]
    for etiqueta, xs, ys in (("original", m5["x1"], m5["y1"]), ("rebarajado", m5["x2"], m5["y2"])):
        P = np.column_stack([xs, ys])
        for k in (5, 10):
            x2, _ = _chi2_rect(P, (0, 1, -1, 0), k)
            clave = f"chi2_{k}_{'orig' if etiqueta == 'original' else 'reb'}"
            a.cerca(x2, NV["rebarajado"][clave], f"A5 · χ² {k}×{k} del {etiqueta}", rel=1e-8)
    a.igual(NV["rebarajado"]["chi2_5_orig"], NV["rebarajado"]["chi2_5_reb"],
            "A5 · a 5×5 los dos χ² empatan", tol=1e-9)

    # --- A1 · el resto del Distrito, por geometría -------------------------
    from shapely import affinity
    Wu = gpd.read_file(PROCESADO / "bogota_ventana_urbana.gpkg").geometry.union_all()
    Wd = gpd.read_file(PROCESADO / "bogota_ventana_dc.gpkg").geometry.union_all()
    en_u = cole.geometry.within(Wu).to_numpy()
    en_d = cole.geometry.within(Wd).to_numpy()
    rd = NV["resto_dc"]
    a.igual(int((en_d & ~en_u).sum()), rd["n_resto"], "A1 · sedes del D.C. fuera del perímetro urbano", tol=0)
    a.cerca(Wd.difference(Wu).area / 1e6, rd["area_resto_km2"], "A1 · área del resto del Distrito", rel=1e-6)
    lam_u = en_u.sum() / Wu.area * 1e6
    a.cerca(lam_u / (rd["n_resto"] / rd["area_resto_km2"]), rd["correcto"],
            "A1 · cociente λ urbana / λ del resto", rel=1e-6)

    # --- A4 · diez veces más puntos, con una simulación propia --------------
    # Python no comparte generador con R: se comprueba la PROPIEDAD con otra
    # simulación del mismo montaje, con tolerancias de Monte Carlo.
    dn = NV["denso"]
    rng = np.random.default_rng(2026)
    Rs = []
    for _ in range(dn["n_real"]):
        k = rng.poisson(dn["lambda"])
        Rs.append(_nn_medio(rng.random((k, 2))) * 2 * math.sqrt(k))
    Rs = np.array(Rs)
    a.cerca(float(Rs.mean()), dn["R_media"], "A4 · media de R con diez veces λ (otra simulación)", rel=0.003)
    a.cierto(abs(100 * float((Rs < 1).mean()) - dn["pct_bajo1"]) < 3,
             "A4 · proporción bajo 1, otra simulación (±3 puntos)",
             f"{100 * float((Rs < 1).mean()):.2f} frente a {dn['pct_bajo1']}")
    a.cierto(dn["R_media"] < en_ruta(caps["cap4"], "m4.R_csr.media") and dn["R_media"] > 1,
             "A4 · el sesgo baja con la densidad sin desaparecer")
    a.cierto(abs(dn["pct_bajo1"] - 100 * en_ruta(caps["cap4"], "m4.R_csr.bajo_1")
                 / en_ruta(caps["cap4"], "m4.n_realizaciones")) < 3,
             "A4 · la proporción bajo 1, como en el capítulo")

    # --- A10 · el peso de traslación sobre la ventana urbana -----------------
    tr = NV["traslacion"]
    for clave, dx_, dy_ in (("frac_este_100", tr["d_corta_m"], 0), ("frac_norte_100", 0, tr["d_corta_m"]),
                            ("frac_este_1000", tr["d_larga_m"], 0)):
        f = Wu.intersection(affinity.translate(Wu, dx_, dy_)).area / Wu.area
        a.cerca(100 * f, tr[clave], f"A10 · área que conserva ({clave})", rel=1e-6)
    a.cerca(100 / tr["frac_este_100"], tr["peso_este_100"], "A10 · el peso es el inverso del solape", rel=1e-9)
    a.cierto(tr["peso_este_1000"] > tr["peso_este_100"] > 1, "A10 · el peso pasa de 1 y crece con la distancia")
    # Lo que hace falsa la opción c: la norte-sur pesa menos, y la ciudad es
    # más larga de norte a sur.
    x0, y0, x1, y1 = Wu.bounds
    a.cierto(tr["peso_norte_100"] < tr["peso_este_100"] and (y1 - y0) > (x1 - x0),
             "A10 · norte-sur pesa menos; ciudad más larga N-S")

    # --- B1 y B8 · Kennedy, rehecha con su polígono -------------------------
    locs = gpd.read_file(PROCESADO / "bogota_localidades.gpkg")
    Wk = locs.loc[locs.localidad == "Kennedy"].geometry.union_all()
    n_ken = int(cole.geometry.covered_by(Wk).sum())
    fz = NV["forzado"]
    a.igual(n_ken, fz["n"], "B8 · sedes de Kennedy por geometría", tol=0)
    a.cerca(Wk.area / 1e6, fz["area_km2"], "B8 · área de Kennedy", rel=1e-6)
    a.cerca(n_ken / (Wk.area / 1e6), fz["distractores"][0]["valor"], "B8 · la fórmula cerrada es n/|W|", rel=1e-6)
    a.cerca(fz["correcto"] * fz["suma_pesos_km2"], fz["n"], "B8 · λ̂ forzada por Σw es n", rel=1e-8)
    a.cierto(fz["suma_pesos_km2"] < fz["area_km2"] and fz["correcto"] > fz["distractores"][0]["valor"],
             "B8 · la cuadratura ve menos área y sube λ̂")
    a.cerca(fz["area_km2"] - fz["suma_pesos_km2"], fz["sin_contar_km2"], "B8 · área sin contar", rel=1e-6)
    lm = NV["limite"]
    a.cierto(abs(lm["corregida_min_km2"] / fz["distractores"][0]["valor"] - 1) < 1e-3
             and abs(lm["corregida_max_km2"] / fz["distractores"][0]["valor"] - 1) < 1e-3,
             "B1 · con σ enorme la KDE corregida vale n/|W|")
    # --- A7 · las medianas de los pinos suecos ------------------------------
    gf = NV["gf_suecos"]
    a.cerca(math.sqrt(math.log(2) / (math.pi * gf["n"] / (gf["lado_x_m"] * gf["lado_y_m"]))),
            gf["csr_mediana_m"], "A7 · mediana de CSR, √(ln 2 / λπ)", rel=1e-8)
    a.cierto(gf["g_mediana_m"] > gf["csr_mediana_m"] > gf["f_mediana_m"], "A7 · G tarde y F pronto")
    a.cierto(gf["j_sobre_1"] == gf["j_nodos"], "A7 · la J sobre 1 en todo el tramo, como dice el texto")
    # --- B9 · el coeficiente en su escala -------------------------------------
    eb = NV["ebeta"]
    xc = en_ruta(caps["cap5"], "m9.centrado.coef[2]")
    a.cerca(math.exp(xc), eb["factor_por_km"], "B9 · exp(β) por kilómetro", rel=1e-8)
    a.cerca(100 * (1 - math.exp(xc)), eb["pct_por_km"], "B9 · porcentaje que baja por km", rel=1e-8)
    # --- B10 y C1 · el σ por defecto de Kinhom sobre la ventana urbana --------
    x0_, y0_, x1_, y1_ = Wu.bounds
    a.cerca(min(x1_ - x0_, y1_ - y0_) / 8, NV["kinhom_nucleo"]["sigma_nucleo_m"],
            "B10 · σ de Kinhom: un octavo del lado corto", rel=1e-8)
    esc = NV["escalas"]
    a.cerca(en_ruta(caps["cap5"], "m11.ajustes[1].parametros.scale") * math.sqrt(math.pi / 2),
            esc["thomas_media_m"], "B11 · distancia media con Thomas, σ·√(π/2)", rel=1e-9)
    a.cerca(en_ruta(caps["cap5"], "m11.ajustes[3].parametros.scale") * 2 / 3,
            esc["matern_media_m"], "B11 · distancia media con Matérn, 2R/3", rel=1e-9)
    a.cierto(esc["razon_escalas"] > 1.5 and esc["dif_media_pct"] < 5,
             "B11 · doble en la tabla, igual en distancia")
    # C2 · la mayor diferencia entre la K isotrópica y la de traslación del
    # 4.10, rehecha sobre las dos curvas del capítulo (sin el r = 0, donde la
    # de traslación vale 0).
    co = {x["correccion"]: x["k"] for x in en_ruta(caps["cap4"], "m10.correcciones")}
    r10_ = en_ruta(caps["cap4"], "m10.r")
    difs = [(abs(i_ / t_ - 1), r_) for i_, t_, r_ in zip(co["isotropic"], co["translate"], r10_) if t_ > 0]
    d_max, r_dmax = max(difs)
    a.cerca(100 * d_max, NV["iso_tras"]["max_dif_pct"], "C2 · mayor diferencia isotrópica/traslación",
            rel=1e-9)
    a.igual(r_dmax, NV["iso_tras"]["r_max_dif_m"], "C2 · radio de esa diferencia", tol=1e-6)
    a.igual(100 * en_ruta(caps["cap4"], "m11.bogota.tasa_salida.nivel"),
            NV["niveles"]["cap4_cobertura_pct"], "C3 · cobertura de la banda de cuantiles", tol=1e-9)
    rw = en_ruta(caps["cap4"], "m6.redwood")
    sin_sup = sum(1 for r_, e_ in zip(rw["rechaza"], rw["esperanza_min"]) if r_ and e_ < 5)
    a.igual(sin_sup, NV["supuesto_rw"]["rechazos_sin_supuesto"],
            "catálogo · rechazos de las secuoyas sin supuesto", tol=0)

    # --- aritmética de A11, B3, B6, C3 y C5 --------------------------------
    nr = NV["nrank"]
    a.igual((nr["nsim"] + 1) * nr["nivel"] / 2, nr["correcto"], "A11 · nrank = nivel·(nsim+1)/2", tol=0)
    a.igual(100 * 2 / (nr["nsim"] + 1), nr["nivel_defecto_pct"], "A11 · nivel por defecto 2/(nsim+1)")
    a.igual(1 / (nr["nsim"] + 1), nr["p_minimo"], "A11 · p mínimo 1/(nsim+1)")
    tp = NV["tope_ppl"]
    a.igual(math.hypot(tp["lado_x_m"], tp["lado_y_m"]) / 2, tp["correcto"], "B3 · la mitad de la diagonal")
    a.cierto(tp["csr_chocan_en_el_tope"] * 2 >= tp["csr_realizaciones"],
             "B3 · chocar es lo normal en CSR, como dice la retro")
    a.igual(tp["csr_chocan_en_el_tope"] + tp["csr_no_chocan"], tp["csr_realizaciones"],
            "B3 · los que chocan y los que no suman veinte", tol=0)
    a.cierto(tp["csr_sigma_min_m"] <= tp["csr_sigma_max_m"] < tp["correcto"],
             "B3 · los que no chocan, por debajo del tope")
    a.cerca(tp["csr_lambda_km2"] * tp["lado_x_m"] * tp["lado_y_m"] / 1e6, tp["csr_puntos_esperados"],
            "B3 · puntos esperados por patrón", rel=1e-9)
    p = en_ruta(caps["cap5"], "m6.chorley.p_max")
    a.igual(p / (1 - p), NV["riesgo_relativo"]["correcto"], "B6 · r = p/(1 − p)", tol=1e-9)
    a.igual(100 * (1 - en_ruta(caps["cap4"], "m11.bogota.tasa_salida.nivel")),
            NV["niveles"]["cap4_pct"], "C3 · nivel puntual de la banda del cap. 4", tol=1e-9)
    infl = en_ruta(caps["cap5"], "m11.tendencia.ajustes[3].inflacion[1]")
    nb = en_ruta(caps["cap5"], "m11.tendencia.n")
    a.cerca(nb / infl ** 2, NV["n_efectivo"]["correcto"], "C5 · n efectivo = n / inflación²", rel=1e-9)

    # --- los ejercicios: Murchison desde sus CSV -------------------------
    oro = pd.read_csv(RUTA_MURCH / "preparcial2_murchison_oro.csv").to_numpy()
    ven = pd.read_csv(RUTA_MURCH / "preparcial2_murchison_ventana.csv").iloc[0]
    caja = (ven.xmin, ven.xmax, ven.ymin, ven.ymax)
    A_rect = (ven.xmax - ven.xmin) * (ven.ymax - ven.ymin)
    from shapely.geometry import Polygon
    from shapely.ops import unary_union
    an = pd.read_csv(RUTA_MURCH / "preparcial2_murchison_greenstone.csv")
    exteriores = [Polygon(g[["x", "y"]].to_numpy()) for _, g in an[~an.agujero].groupby("anillo")]
    agujeros = [Polygon(g[["x", "y"]].to_numpy()) for _, g in an[an.agujero].groupby("anillo")]
    GS = unary_union(exteriores).difference(unary_union(agujeros))
    e1, e2, e3, e4, e5 = (EJ[f"e{i}"]["solucion"] for i in range(1, 6))
    n = len(oro)
    dgs = _dentro(GS, oro[:, 0], oro[:, 1])
    n_gs = int(dgs.sum())
    a.igual(n, e1["n"], "E1 · yacimientos", tol=0)
    a.cerca(A_rect, e1["area_rect"], "E1 · área del rectángulo", rel=1e-6)
    a.igual(n_gs, e1["n_gs"], "E1 · yacimientos dentro del greenstone", tol=0)
    a.cerca(GS.area, e1["area_gs"], "E1 · área del greenstone", rel=1e-6)
    lam_gs, lam_f = n_gs / GS.area, (n - n_gs) / (A_rect - GS.area)
    a.cerca(lam_gs / lam_f, e1["cociente"], "E1 · cociente de intensidades", rel=1e-6)
    for z in e1["cuadrantes"]:
        x2, E = _chi2_rect(oro, caja, z["k"])
        a.cerca(x2, z["chi2"], f"E1 · χ² {z['k']}×{z['k']}", rel=1e-7)
        a.cerca(E, z["esperanza_min"], f"E1 · esperanza de cada celda {z['k']}×{z['k']}", rel=1e-7)
        # En log10: con p del orden de 1e-110, `cerca()` compara contra un
        # suelo absoluto y no podría fallar nunca (lo destapó el arnés). Y
        # BILATERAL: `quadrat.test` contrasta por defecto las dos colas, así
        # que su p es el doble de la cola superior —con la cola sola, el log10
        # se separaba exactamente log10(2)—.
        gl = z["k"] ** 2 - 1
        p_bil = 2 * min(chi2_dist.sf(x2, gl), chi2_dist.cdf(x2, gl))
        a.cerca(math.log10(p_bil), math.log10(z["p"]),
                f"E1 · p-valor {z['k']}×{z['k']}, bilateral (log10)", rel=1e-5)
    resp = [z["k"] for z in e1["cuadrantes"] if z["esperanza_min"] >= 5]
    a.cierto(resp == e1["respetan"], "E1 · las rejillas que respetan el supuesto", str(resp))
    from shapely.geometry import box
    fuera = box(caja[0], caja[2], caja[1], caja[3]).difference(GS)
    n_resta = int(_dentro(fuera, oro[:, 0], oro[:, 1]).sum())
    a.igual(n_resta, e1["n_fuera_resta"], "E1 · los de fuera, por la resta de ventanas", tol=0)
    a.igual(n - n_gs - n_resta, 1, "E1 · la resta pierde exactamente un yacimiento", tol=0)
    a.cerca(lam_gs / (n_resta / fuera.area), e1["cociente_resta"], "E1 · cociente con la resta", rel=1e-6)
    a.cierto(all(r == e1["nsim_greenstone"] for r in e1["rechazos_greenstone"]),
             "E1 · el Poisson del greenstone rechaza siempre")
    obs_resp = [z["chi2"] for z in e1["cuadrantes"] if z["k"] in e1["respetan"]]
    a.cierto(len(obs_resp) == len(e1["chi2_mediana_greenstone"])
             and all(o > m for o, m in zip(obs_resp, e1["chi2_mediana_greenstone"])),
             "E1 · el χ² del oro, sobre la mediana simulada")

    # E2 · Clark-Evans y K dentro del greenstone, y la geometría
    P = oro[dgs]
    ce_gs = _nn_medio(P) * 2 * math.sqrt(n_gs / GS.area)
    a.cerca(ce_gs, e2["ce_naive"], "E2 · R ingenua dentro del greenstone", rel=1e-6)
    a.cerca(_nn_medio(oro) * 2 * math.sqrt(n / A_rect), e2["ce_rect"], "E2 · R ingenua en el rectángulo", rel=1e-6)
    a.igual(len(exteriores), e2["piezas"], "E2 · piezas del greenstone", tol=0)
    a.igual(len(agujeros), e2["agujeros"], "E2 · agujeros del greenstone", tol=0)
    a.igual(len(an), e2["vertices"], "E2 · vértices del contorno", tol=0)
    a.cerca(GS.length, e2["perimetro_km"], "E2 · perímetro del greenstone", rel=1e-6)
    d = np.hypot(P[:, None, 0] - P[None, :, 0], P[:, None, 1] - P[None, :, 1])
    np.fill_diagonal(d, np.inf)
    I, J = np.where(d <= 10)
    a.cerca(GS.area * len(I) / (n_gs * (n_gs - 1)), e2["K_none"], "E2 · K(10 km) sin corregir", rel=1e-6)
    from shapely import affinity
    pesos = [GS.area / GS.intersection(affinity.translate(GS, P[j, 0] - P[i, 0], P[j, 1] - P[i, 1])).area
             for i, j in zip(I, J) if i < j]
    k_tr_exacta = GS.area * 2 * sum(pesos) / (n_gs * (n_gs - 1))
    a.cierto(abs(k_tr_exacta / e2["K_trans"] - 1) < 0.03,
             "E2 · K(10 km) de traslación: exacta a < 3 % de R",
             f"{k_tr_exacta:.2f} frente a {e2['K_trans']:.2f}")
    a.cierto(e2["K_none"] < e2["pir2"] < min(e2["K_trans"], k_tr_exacta),
             "E2 · sin corregir < πr² < corregida, con las dos")
    # Cuánto borde hay: los puntos más cerca del borde que de su vecino.
    from scipy.spatial import cKDTree
    def _cerca_borde(W, Q):
        dnn = cKDTree(Q).query(Q, k=2)[0][:, 1]
        db = gpd.GeoSeries(gpd.points_from_xy(Q[:, 0], Q[:, 1])).distance(W.boundary).to_numpy()
        return 100 * float((db < dnn).mean()), float(np.median(db)), float(np.median(dnn))
    pct_gs, med_b, med_v = _cerca_borde(GS, P)
    a.cerca(pct_gs, e2["pct_borde_gs"], "E2 · yacimientos más cerca del borde que del vecino", rel=1e-6)
    a.cerca(med_b, e2["mediana_borde_km"], "E2 · mediana de la distancia al borde", rel=1e-6)
    a.cerca(med_v, e2["mediana_vecino_km"], "E2 · mediana de la distancia al vecino", rel=1e-6)
    Pu = np.column_stack([cole.geometry.x.to_numpy()[en_u], cole.geometry.y.to_numpy()[en_u]])
    pct_bog = _cerca_borde(Wu, Pu)[0]
    a.cerca(pct_bog, e2["pct_borde_bogota"], "E2 · lo mismo con las sedes de Bogotá", rel=1e-6)
    a.cierto(e2["ce_rect_cdf"] < e2["ce_rect"], "E2 · en el rectángulo la corregida queda por debajo")
    # Lo que la explicación nueva afirma, rehecho: quiénes tienen su vecino
    # —entre los 255— fuera del greenstone, las distancias medias y las del
    # azar, el cociente K/πr² y la parte del greenstone a más de 10 km.
    arbol = cKDTree(oro)
    _, vec = arbol.query(oro, k=2)
    idx_gs = np.where(dgs)[0]
    a.igual(int((~dgs[vec[idx_gs, 1]]).sum()), e2["vecino_fuera"], "E2 · vecino más próximo fuera", tol=0)
    a.cerca(float(cKDTree(P).query(P, k=2)[0][:, 1].mean()), e2["nn_media_gs_km"], "E2 · vecino medio dentro", rel=1e-6)
    a.cerca(float(arbol.query(oro, k=2)[0][:, 1].mean()), e2["nn_media_rect_km"], "E2 · vecino medio, rectángulo", rel=1e-6)
    a.cerca(0.5 / math.sqrt(lam_gs), e2["nn_esperada_gs_km"], "E2 · vecino del azar, greenstone", rel=1e-6)
    a.cerca(0.5 / math.sqrt(n / A_rect), e2["nn_esperada_rect_km"], "E2 · vecino del azar, rectángulo", rel=1e-6)
    I2, _ = np.where(d <= 2)
    a.cerca(GS.area * len(I2) / (n_gs * (n_gs - 1)) / (math.pi * 4), e2["K_none_sobre_pir2_2km"],
            "E2 · K sin corregir / πr² a 2 km", rel=1e-6)
    RRp = np.arange(0, 241) / 20
    coc = np.array([GS.area * (d <= r).sum() / (n_gs * (n_gs - 1)) / (math.pi * r * r) if r > 0 else np.nan
                    for r in RRp])
    i_c = next(i for i, r in enumerate(RRp) if r >= 2 and coc[i] < 1)
    a.cerca(RRp[i_c], e2["r_cruce_km"], "E2 · radio en que K sin corregir cruza πr²", rel=1e-9)
    a.cierto(all(coc[(RRp >= 2) & (RRp < e2["r_cruce_km"] - 1e-9)] > 1), "E2 · de 2 km al cruce, sobre πr²")
    # spatstat (erosion) y shapely (buffer negativo) aproximan los arcos
    # distinto: 0.240 frente a 0.228. La página lo publica con un decimal.
    a.cerca(100 * GS.buffer(-10).area / GS.area, e2["pct_area_a_mas_de_10km"],
            "E2 · greenstone a más de 10 km del borde", rel=0.1)
    a.cierto(e2["K_none"] > e2["ref_K_cuantiles"][2] and e2["ce_naive"] < e2["ref_R_cuantiles"][0],
             "E2 · sin corregir, agregado contra su azar")

    # E3 · lo que se puede rehacer de los núcleos
    sig = [s["sigma"] for s in e3["selectores"]]
    a.cerca(max(sig) / min(sig), e3["razon"], "E3 · cociente entre selectores", rel=1e-8)
    a.cierto(not any(s["choco"] or s["en_extremo"] for s in e3["selectores"]),
             "E3 · ningún selector en el extremo")
    from scipy.stats import norm
    x0, x1, y0, y1 = caja
    for sel, masas in (("diggle", e3["masas_diggle"]), ("CvL", e3["masas_cvl"])):
        s_ = next(s["sigma"] for s in e3["selectores"] if s["selector"] == sel)
        masa_exacta = float(((norm.cdf((x1 - oro[:, 0]) / s_) - norm.cdf((x0 - oro[:, 0]) / s_))
                             * (norm.cdf((y1 - oro[:, 1]) / s_) - norm.cdf((y0 - oro[:, 1]) / s_))).sum())
        a.cerca(masa_exacta, masas["sin"], f"E3 · masa sin corregir, σ de bw.{sel} (exacta)",
                rel=0.002)
        a.igual(masas["dig"], n, f"E3 · Diggle integra n con el σ de bw.{sel}", tol=0.05)
    a.cierto(e3["masas_diggle"]["def"] < n < e3["masas_cvl"]["def"],
             "E3 · por defecto: corta con un σ, larga con el otro")
    pk = e3["picos"]
    a.cierto(pk["CvL"] < e3["lambda_gs"] < pk["ppl"] < pk["diggle"],
             "E3 · picos a los lados de la λ del greenstone")
    a.cerca(e3["lambda_gs"], lam_gs, "E3 · la λ del greenstone es la del E1", rel=1e-8)
    a.cierto(3 * max(e3["celda_defecto_km"]) > next(s["sigma"] for s in e3["selectores"] if s["selector"] == "ppl")
             and 3 * max(e3["celda_fina_km"]) < min(sig),
             "E3 · tres celdas: no con 128, sí con la rejilla fina")

    # E4 · la distancia a la falla y la identidad de unidades
    fa = pd.read_csv(RUTA_MURCH / "preparcial2_murchison_fallas.csv").to_numpy()
    ax, ay, bx, by = fa[:, 0], fa[:, 1], fa[:, 2], fa[:, 3]
    dx, dy = bx - ax, by - ay
    L2 = np.where(dx ** 2 + dy ** 2 > 0, dx ** 2 + dy ** 2, 1.0)
    t = np.clip(((oro[:, [0]] - ax) * dx + (oro[:, [1]] - ay) * dy) / L2, 0, 1)
    dist = np.hypot(oro[:, [0]] - (ax + t * dx), oro[:, [1]] - (ay + t * dy)).min(axis=1)
    q05, q95 = np.quantile(dist, [0.05, 0.95])
    a.cerca(q05, e4["bulto"][0], "E4 · percentil 5 de la distancia a la falla", rel=1e-6)
    a.cerca(q95, e4["bulto"][1], "E4 · percentil 95 de la distancia a la falla", rel=1e-6)
    a.cerca(dist.max(), e4["dist_max_oro"], "E4 · yacimiento más alejado de una falla", rel=1e-6)
    a.cerca(2 * n * math.log(1e6), e4["dif_aic"], "E4 · AIC metros − km = 2n·ln(10⁶)", rel=1e-8)
    a.cerca(lam_gs / lam_f, e4["cociente_exacto"], "E4 · el cociente exacto es el del E1", rel=1e-8)
    a.cierto(e4["eb_defecto"] < e4["eb_400"] < e4["cociente_exacto"],
             "E4 · la cuadratura fina acerca e^β al exacto")
    a.cierto(abs(e4["pesos_gs_400"] - GS.area) < abs(e4["pesos_gs_defecto"] - GS.area),
             "E4 · con nd = 400 los pesos aciertan más el área")
    a.cierto(e4["rho_min"] == 0 and e4["razon_total_infinita"], "E4 · el ρ mínimo es 0: razón infinita")
    a.cierto(e4["primer_cero_km"] > e4["dist_max_oro"], "E4 · los ceros de ρ, pasado el último yacimiento")
    a.cerca(math.hypot(ven.xmin, ven.ymin), e4["dist_origen_km"], "E4 · distancia del origen al rectángulo", rel=1e-8)
    a.cerca(100 * (e4["beta_400"] / e4["beta_defecto"] - 1), e4["cambio_beta_pct"], "E4 · cambio de β en %",
            rel=1e-8)
    a.cerca(math.exp(e4["beta_400"]), e4["eb_400"], "E4 · e^β es la exponencial de β", rel=1e-8)

    # E5 · coherencia de lo que solo calcula spatstat
    p_min = 1 / (e5["nsim"] + 1)
    todas = [e5[c_][k_] for c_ in ("envolvente_D", "envolvente_GD") for k_ in ("dclf_p", "dclf_p_corto")]
    todas += e5["dclf_GD_otras_semillas"] + e5["dclf_GD_corto_otras_semillas"]
    a.cierto(all(x >= p_min - 1e-12 for x in todas), "E5 · ningún p baja de 1/(nsim+1)")
    a.cierto(e5["envolvente_D"]["dclf_p"] <= 0.05 and e5["envolvente_D"]["dclf_p_corto"] <= 0.05,
             "E5 · ~ D rechaza en los dos tramos")
    a.cierto(e5["envolvente_GD"]["dclf_p"] > 0.05 and e5["envolvente_GD"]["dclf_p_corto"] <= 0.05,
             "E5 · ~ G + D: no rechaza en el largo, sí en el corto")
    a.cierto(all(x > 0.05 for x in e5["dclf_GD_otras_semillas"])
             and all(x <= 0.05 for x in e5["dclf_GD_corto_otras_semillas"]),
             "E5 · el veredicto se repite con las otras semillas")
    a.cierto(iguales(e5["dclf_GD_rango"], [min(e5["dclf_GD_otras_semillas"]), max(e5["dclf_GD_otras_semillas"])])
             and iguales(e5["dclf_GD_corto_rango"],
                         [min(e5["dclf_GD_corto_otras_semillas"]), max(e5["dclf_GD_corto_otras_semillas"])]),
             "E5 · los rangos citados son los de las semillas")
    a.cerca(min(ven.xmax - ven.xmin, ven.ymax - ven.ymin) / 4, e5["envolvente_GD"]["r_max_km"],
            "E5 · el rango por defecto es un cuarto del lado corto", rel=1e-6)
    a.cerca(min(ven.xmax - ven.xmin, ven.ymax - ven.ymin) / 8, e5["sigma_kinhom_km"],
            "E5 · σ de Kinhom: un octavo del lado corto", rel=1e-6)
    el = e5["envolvente_GD_lambda"]
    a.cierto(el["dclf_p"] >= p_min - 1e-12 and el["dclf_p_corto"] <= 0.05 and el["dclf_p"] > 0.05,
             "E5 · con la λ del modelo, el veredicto no cambia")
    a.cierto(e5["varianza"]["veces"] > 1 and 0 < e5["varianza"]["pct_tramo_corto"] < 50,
             "E5 · la varianza de K̂ crece con r")
    zc = e5["z_critico"]
    a.cierto(abs(e5["ppm_z"][2]) > zc and all(abs(k["z_D"]) < zc for k in e5["kppm"]),
             "E5 · la z de D cae bajo el valor crítico")
    a.cierto(all(abs(k["z_G"]) > zc for k in e5["kppm"]), "E5 · la z de G sobrevive")


# =====================================================================
# FAMILIA 2 · sincronía
# =====================================================================
def familia_2(a: Auditoria, D: dict, caps: dict, html: str):
    archivo = {"cap4_datos.json": caps["cap4"], "cap5_datos.json": caps["cap5"]}
    malas = []
    for clave, e in D["reutilizado"].items():
        v = en_ruta(archivo[e["origen"]], e["ruta"])
        if v is None or not iguales(v, e["valor"]):
            malas.append(f"{clave} ({e['origen']}:{e['ruta']}): capítulo {v!r} · preparcial {e['valor']!r}")
    a.cierto(not malas, f"las {len(D['reutilizado'])} cifras reutilizadas cuadran",
             "; ".join(malas[:3]))
    # Las series de los gráficos, contra su origen. Las que son cocientes se
    # rehacen con las series de origen.
    for nombre, g in D["graficos"].items():
        desde = g.get("desde") or {}
        fuente = {k: en_ruta(archivo[d["origen"]], d["ruta"]) for k, d in desde.items()}
        if any(v is None for v in fuente.values()):
            a.cierto(False, f"{nombre}: todas sus series existen en el capítulo")
            continue
        ok = True
        if nombre == "g_hist":
            ok = all(iguales(g[k], fuente[k]) for k in ("centros", "observado", "referencia"))
        elif nombre == "g_supuesto":
            n_u = en_ruta(caps["cap4"], "m1.urbana.n")
            ok = (all(iguales(g[k], fuente[k]) for k in ("nx", "esperanza_min", "celdas_baja", "celdas"))
                  and iguales(g["rectangulo"], [n_u / k ** 2 for k in fuente["nx"]], 1e-8))
        elif nombre == "g_pcf":
            lec = g["forma"]["lectura"]
            i = min(range(len(fuente["r"])), key=lambda j: abs(fuente["r"][j] - 3000))
            r4 = en_ruta(caps["cap4"], "m11.bogota.r")
            j = min(range(len(r4)), key=lambda k: abs(r4[k] - fuente["r"][i]))
            disco = en_ruta(caps["cap4"], "m11.bogota.obs")[j] / en_ruta(caps["cap4"], "m11.bogota.teo")[j]
            ok = (iguales(g["r"], fuente["r"]) and iguales(g["g"], fuente["g"])
                  and iguales(lec["g"], fuente["g"][i], 1e-8) and iguales(lec["disco"], disco, 1e-6)
                  and iguales(lec["pct"], 100 * (fuente["g"][i] - 1), 1e-6))
        elif nombre == "g_pico":
            ok = iguales(g["sigma"], fuente["sigma"]) and iguales(g["maximo"], fuente["maximo"])
        elif nombre == "g_kinhom":
            idx = [i for i, r in enumerate(fuente["r"]) if r > 0]
            ok = (iguales(g["r"], [fuente["r"][i] for i in idx])
                  and iguales(g["observada"], [fuente["obs"][i] / fuente["mmean"][i] for i in idx], 1e-8)
                  and iguales(g["alta"], [fuente["hi"][i] / fuente["mmean"][i] for i in idx], 1e-8))
        elif nombre == "g_dos":
            idx = [i for i, r in enumerate(fuente["r"]) if r > 0]
            fd = g["forma"]
            e_csr = fuente["obs"][idx[0]] / fuente["teo"][idx[0]] - 1
            e_mod = fuente["obs5"][idx[0]] / fuente["mmean"][idx[0]] - 1
            ok = (iguales(g["csr_observada"], [fuente["obs"][i] / fuente["teo"][i] for i in idx], 1e-8)
                  and iguales(g["mod_observada"], [fuente["obs5"][i] / fuente["mmean"][i] for i in idx], 1e-8)
                  and iguales(fd["llevado_primera_pct"], 100 * (1 - e_mod / e_csr), 1e-6))
        a.cierto(ok, f"gráfico {nombre}: series iguales a su origen")
    m = re.search(r"\n    const DATOS_PRE2 = (\{.*?\});\n", html, re.S)
    if not m:
        a.cierto(False, "el HTML incrusta DATOS_PRE2")
        return
    a.cierto(json.loads(m.group(1)) == D, "el JSON incrustado es el del disco",
             "regenerar sin reensamblar deja el HTML citando cifras viejas")


# =====================================================================
# FAMILIAS 3, 4 y 5 · las preguntas, leídas del HTML publicado
# =====================================================================
def _preguntas(html: str):
    quices = lee_autoevaluaciones(html)
    return [(k, i, q) for k, qs in quices.items() for i, q in enumerate(qs, 1)]


def familia_3(a: Auditoria, preguntas):
    a.igual(len(preguntas), 28, "el documento publica 28 preguntas", tol=0)
    titulos = {(f["doc"], f["modulo"]): plano(f["titulo"]) for f in ALC.ALCANCE}
    tocados, malas = set(), []
    for k, i, q in preguntas:
        rep = q.get("repaso") or {}
        m = re.match(r"Cap\. (\d) · módulo (\d+) — (.*)$", rep.get("etiqueta", ""))
        if not m:
            malas.append(f"{k}·{i}: repaso sin etiqueta legible")
            continue
        doc, mod, tit = f"cap{m.group(1)}", int(m.group(2)), m.group(3)
        if (doc, mod) not in titulos:
            malas.append(f"{k}·{i}: apunta fuera del alcance ({doc}.m{mod})")
            continue
        if titulos[(doc, mod)] != tit:
            malas.append(f"{k}·{i}: título «{tit}» frente a «{titulos[(doc, mod)]}»")
        if rep.get("href") != ALC.DOCS[doc]:
            malas.append(f"{k}·{i}: enlaza a {rep.get('href')}")
        if rep.get("orden") != int(m.group(1)) * 100 + mod:
            malas.append(f"{k}·{i}: orden de repaso {rep.get('orden')}")
        tocados.add((doc, mod))
    a.cierto(not malas, "todo repaso resuelve contra el capítulo", "; ".join(malas[:3]))
    faltan = sorted(set(titulos) - tocados)
    a.cierto(not faltan, "los 22 módulos tienen pregunta", str(faltan))


def familia_4(a: Auditoria, preguntas):
    malas = []
    for k, i, q in preguntas:
        ref = f"{k}·{i}"
        if q["tipo"] == "numerica":
            for campo in ("respuesta", "tolerancia", "retroAcierto", "retroFallo"):
                if q.get(campo) in (None, ""):
                    malas.append(f"{ref}: numérica sin {campo}")
            continue
        ops = q.get("opciones") or []
        if not ops:
            malas.append(f"{ref}: sin opciones")
            continue
        retros = [(o.get("retro") or "").strip() for o in ops]
        if any(not r for r in retros):
            malas.append(f"{ref}: opción sin retro")
        if len(set(retros)) != len(retros):
            malas.append(f"{ref}: retros repetidas")
        nc = sum(1 for o in ops if o.get("correcta"))
        if q["tipo"] in ("opcion", "grafico") and nc != 1:
            malas.append(f"{ref}: {nc} correctas")
        if q["tipo"] == "multiple" and nc < 2:
            malas.append(f"{ref}: múltiple con {nc} correctas")
        if q["tipo"] == "grafico" and not plano(q.get("descripcionGrafico") or "").strip():
            malas.append(f"{ref}: gráfico sin descripción")
        if q["tipo"] == "grafico" and "&" in (q.get("descripcionGrafico") or ""):
            malas.append(f"{ref}: la descripción del gráfico lleva entidades HTML")
    a.cierto(not malas, "retroalimentación y correctas completas", "; ".join(malas[:3]))
    tipos = {}
    for k, _, q in preguntas:
        tipos.setdefault(k, set()).add(q["tipo"])
    for k, ts in tipos.items():
        a.cierto(ts >= {"opcion", "multiple", "numerica", "grafico"}, f"{k}: los cuatro tipos",
                 str(sorted(ts)))


def familia_5(a: Auditoria, preguntas):
    regala, posiciones, n_una, n_larga, delata, posicional = [], {}, 0, 0, [], []
    for k, i, q in preguntas:
        ref = f"{k}·{i}"
        textos = [q.get("pregunta", ""), q.get("pista", ""), q.get("retroAcierto", ""),
                  q.get("retroFallo", "")] + [o.get("retro", "") for o in q.get("opciones") or []]
        for t in textos:
            if any(p.search(plano(t)) for p in POSICIONALES):
                posicional.append(ref)
                break
        ops = q.get("opciones")
        if not ops:
            continue
        enun = (plano(q.get("pregunta", "")) + " " + plano(q.get("pista", ""))).lower()
        for o in ops:
            if o.get("correcta"):
                lim = plano(o["texto"]).strip(" .").lower()
                if len(lim) > 25 and lim in enun:
                    regala.append(ref)
        if q["tipo"] == "multiple":
            continue
        n_una += 1
        largos = [len(plano(o["texto"])) for o in ops]
        j = next(x for x, o in enumerate(ops) if o.get("correcta"))
        posiciones[j + 1] = posiciones.get(j + 1, 0) + 1
        if largos[j] == max(largos):
            n_larga += 1
        if largos[j] - max(l for x, l in enumerate(largos) if x != j) > 20:
            delata.append(ref)
    a.cierto(not regala, "ningún enunciado regala la correcta", str(regala))
    a.cierto(not posicional, "ninguna retro nombra una posición", str(posicional))
    a.cierto(not delata, "ninguna clave le saca > 20 caracteres", str(delata))
    peor = max(posiciones.values()) if posiciones else 0
    a.cierto(peor <= n_una * 0.5, "la correcta no se concentra en una posición",
             " · ".join(f"{k}: {v}" for k, v in sorted(posiciones.items())))
    a.cierto(n_larga <= n_una * 0.5, "la correcta no es casi siempre la más larga",
             f"{n_larga} de {n_una}")


# =====================================================================
# FAMILIA 6 · los ejercicios
# =====================================================================
_NUM = re.compile(r"(?<![\w.])-?\d{1,3}(?:[  ]\d{3})+(?:\.\d+)?|(?<![\w.])-?\d+(?:\.\d+)?")


def _numeros(o, acc):
    if isinstance(o, bool):
        return acc
    if isinstance(o, (int, float)):
        acc.append(float(o))
    elif isinstance(o, list):
        for x in o:
            _numeros(x, acc)
    elif isinstance(o, dict):
        for x in o.values():
            _numeros(x, acc)
    return acc


def _cifra_en(token, pool):
    t = token.replace(" ", "").replace(" ", "")
    x = float(t)
    dec = len(t.split(".")[1]) if "." in t else 0
    paso = 0.5 * 10 ** (-dec) + 1e-12
    if abs(x) in DISENO:
        return True
    return any(abs(abs(v) - abs(x)) <= paso for v in pool)


def marcado_de(html: str) -> str:
    """Solo el marcado de los módulos. El HTML lleva además el JSON entero
    incrustado, y buscar en todo el archivo hacía imposible que «está en la
    página» fallara: el texto quitado de la página seguía en el JSON."""
    return plano("".join(re.findall(r'<template id="module-.*?</template>', html, re.S)))


def familia_6(a: Auditoria, D: dict, html: str):
    EJ = D["ejercicios"]
    pagina = marcado_de(html)
    a.igual(html.count('class="ejercicio-guiado"'), len(EJ), "el documento pinta los cinco ejercicios", tol=0)
    pool = _numeros(D["ejercicios"], [])
    pool += _numeros({k: v["valor"] for k, v in D["reutilizado"].items()}, [])
    for k in sorted(EJ, key=lambda s: int(s[1:])):
        e = EJ[k]
        en = e["enunciado"]
        rs = e["solucion"]["respuestas"]
        sin_ancla = [r["pide"] for r in rs if r["pide"] not in en]
        a.cierto(not sin_ancla, f"{k} · cada respuesta ancla en su enunciado", str(sin_ancla))
        tramos = [(en.index(r["pide"]), en.index(r["pide"]) + len(r["pide"])) for r in rs if r["pide"] in en]
        huerfanas = []
        for m in DEMANDA.finditer(en):
            dentro = any(i <= m.start() < j for i, j in tramos)
            if not dentro and en[m.end():m.end() + 1] == ":":
                despues = [i for i, _ in tramos if i > m.start()]
                dentro = bool(despues) and "." not in en[m.start():min(despues)]
            if not dentro:
                huerfanas.append(en[m.start():m.start() + 30])
        a.cierto(not huerfanas, f"{k} · toda demanda tiene respuesta", str(huerfanas))
        # Las comillas invertidas del JSON son <code> en la página.
        pintadas = [r for r in rs if plano(r["respuesta"]).replace("`", "")[:60] not in pagina]
        a.cierto(not pintadas, f"{k} · cada respuesta está en la página", str(len(pintadas)))
        sueltas = []
        for texto in [r["respuesta"] for r in rs] + [e["solucion"]["lectura"]]:
            for tok in _NUM.findall(plano(texto)):
                if not _cifra_en(tok, pool):
                    sueltas.append(tok)
        a.cierto(not sueltas, f"{k} · toda cifra de sus respuestas está en el JSON", str(sueltas[:5]))
        fuera = [m for m in e["modulos"] if not ALC.en_alcance(m.split(".")[0], int(m.split(".m")[1]))]
        a.cierto(not fuera, f"{k} · sus módulos están en el alcance", str(fuera))


# =====================================================================
# FAMILIA 7 · el catálogo
# =====================================================================
def familia_7(a: Auditoria, D: dict, html: str):
    errs = D["errores"]
    pagina = marcado_de(html)
    a.igual(len(errs), 15, "el catálogo tiene quince errores", tol=0)
    malas = []
    for e in errs:
        if not isinstance(e["claves"], list):
            malas.append(f"{e['id']}: claves no es una lista")
            continue
        for k in e["claves"]:
            if k not in D["reutilizado"]:
                malas.append(f"{e['id']}: {k} no existe")
        if not ALC.en_alcance(e["doc"], e["modulo"]):
            malas.append(f"{e['id']}: fuera del alcance")
        if plano(e["titulo"]) not in pagina:
            malas.append(f"{e['id']}: su título no está en la página")
    a.cierto(not malas, "cada error cita cifras que existen", "; ".join(malas[:3]))


def main() -> int:
    a = Auditoria("Preparcial del Corte II verificado")
    fam = Familias(a)
    D = json.loads(RUTA_DATOS.read_text(encoding="utf-8"))
    html = RUTA_HTML.read_text(encoding="utf-8")
    caps = {c: json.loads((RUTA_CAPS / f"{c}_datos.json").read_text(encoding="utf-8"))
            for c in ("cap4", "cap5")}
    fam.abre(1, "Cifras nuevas, rehechas en Python")
    familia_1(a, D, caps)
    fam.abre(2, "Sincronía con los capítulos 4 y 5")
    familia_2(a, D, caps, html)
    preguntas = _preguntas(html)
    fam.abre(3, "Cobertura: los 22 módulos y el repaso")
    familia_3(a, preguntas)
    fam.abre(4, "Retroalimentación completa")
    familia_4(a, preguntas)
    fam.abre(5, "No filtración: enunciado, posición y longitud")
    familia_5(a, preguntas)
    fam.abre(6, "Ejercicios: demandas contestadas y cifras del JSON")
    familia_6(a, D, html)
    fam.abre(7, "Catálogo de errores")
    familia_7(a, D, html)
    fam.resumen()
    return a.cierre()


if __name__ == "__main__":
    sys.exit(main())
