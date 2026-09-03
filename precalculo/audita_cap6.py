#!/usr/bin/env python3
"""
audita_cap6.py — auditoría independiente del precálculo del capítulo 6 (T4.1b)

Material de Estadística Espacial 2026-II (20929).

NO comprueba que los JSON existan: comprueba que sus NÚMEROS sean ciertos,
por caminos que no pasan por R ni por `spdep`.

QUÉ HACE QUE ESTO SEA UN CONTROL, Y NO UNA SEGUNDA OPINIÓN DEL MISMO
El capítulo entero es «qué es un vecino», y esa pregunta tiene DOS
implementaciones maduras e independientes: `spdep` en R, que es la que
generó las cifras, y **`libpysal` en Python, que es la que las recalcula
aquí**. Son dos bibliotecas escritas por gente distinta, con estructuras
de datos distintas y algoritmos de indexación distintos. Que la
contigüidad reina de Columbus dé 118 parejas en las dos no es una
coincidencia amable: es la única forma de que la cifra signifique algo.

Y lo que NO viene de libpysal se reimplementa aquí por definición:

  · LOS CINCO ESTILOS DE PESO, desde la adyacencia binaria. B es 1; W
    divide por el grado; C escala para que el total sea n; U para que sea
    1; y S es el de estabilización de varianza —dividir por la raíz de la
    suma de cuadrados de la fila y reescalar a n—, que es el único con
    una fórmula que se puede escribir mal sin que nada falle.
  · LAS COMPONENTES CONEXAS Y LAS ISLAS, con un recorrido en anchura
    escrito aquí. No se importa un `n_components`: se cuenta.
  · LA ASIMETRÍA de las vecindades de k vecinos, contando los pares
    (i, j) en los que j es vecino de i pero i no lo es de j.
  · EL REZAGO como producto de matrices, y su contracción.

HASTA DÓNDE LLEGA LA INDEPENDENCIA, DECLARADO Y NO INSINUADO
  · TOTAL para la contigüidad reina y torre, los k vecinos, el umbral de
    distancia, Delaunay, Gabriel, la vecindad relativa, los cinco
    estilos, el rezago, las componentes y toda la aritmética.
  · PARCIAL para la geometría: GEOS es el mismo motor debajo de `sf` y de
    `geopandas`, así que dos áreas que coincidan no prueban dos cálculos
    independientes. Se dice y no se disimula.
  · NULA para la ESFERA DE INFLUENCIA: `libpysal` no la trae. Se auditan
    sus propiedades —simetría, que esté entre Gabriel y Delaunay en
    número de aristas, grados coherentes— y no su valor.
  · NULA para la comparación `spdep` ↔ `sfdep` del módulo 8: son dos
    interfaces del mismo motor, y eso ya lo dice el propio módulo.

Ejecutar con el Python de geo_env:
    "$(python3 -c 'import json;print(json.load(open("precalculo/versiones_py.json"))["ejecutable"])')" \\
        precalculo/audita_cap6.py

LOS RÓTULOS TIENEN PRESUPUESTO: 57 CARACTERES, PREFIJO INCLUIDO. Uno de
58 o más queda pegado a su detalle y el arnés deja de contar esa
comprobación como cubierta, en silencio. Ver `audita_cap4.py`.
"""
from __future__ import annotations

import json
import pathlib
import sys
import warnings
from collections import deque

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from audita_base import (Auditoria, audita_geomapa, carga as _carga,  # noqa: E402
                         decimales)

import numpy as np                      # noqa: E402
import geopandas as gpd                 # noqa: E402
import libpysal                         # noqa: E402
from libpysal import weights            # noqa: E402

warnings.filterwarnings("ignore")

RAIZ = pathlib.Path(__file__).resolve().parent.parent
PRECALCULO = RAIZ / "precalculo"
SALIDAS = PRECALCULO / "salidas"
PROCESADO = RAIZ / "datos" / "procesado"


def carga(var: str, nombre: str):
    return _carga(var, nombre, SALIDAS)


# =====================================================================
# LA CACHE DE LA CONTIGÜIDAD MUNICIPAL, y por qué es legítima
#
# Construir la reina de los 1 122 municipios con libpysal cuesta ~8 s. El
# auditor la necesita entera, y el ARNÉS lo ejecuta una vez por inyección:
# cincuenta y siete veces ocho segundos son ocho minutos de esperar a que
# se recalcule lo mismo. Se guarda, con dos cautelas que la hacen honesta:
#
#   · La cache guarda lo que ESTE auditor calculó con libpysal, no lo que
#     R publicó. La independencia no se toca.
#   · La llave es el tamaño y la fecha del .gpkg. Si el dato cambia, la
#     cache se descarta sola. Una cache que sobrevive a su fuente es un
#     auditor que aprueba lo que ya no está mirando.
# =====================================================================
def reina_municipal(mun, ruta: pathlib.Path) -> dict:
    st = ruta.stat()
    llave = f"{st.st_size}·{int(st.st_mtime)}·{len(mun)}"
    f = PRECALCULO / "cache" / "audita_cap6_reina.json"
    if f.exists():
        guardado = json.loads(f.read_text(encoding="utf-8"))
        if guardado.get("llave") == llave:
            return {int(k): v for k, v in guardado["vecinos"].items()}
    v = de_w(weights.Queen.from_dataframe(mun, use_index=True))
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(json.dumps({"llave": llave, "vecinos": v}), encoding="utf-8")
    return v


# =====================================================================
# LA TEORÍA DE GRAFOS, ESCRITA AQUÍ
#
# `libpysal` trae `n_components`, pero importarlo sería auditar una
# biblioteca con esa misma biblioteca. Un recorrido en anchura cabe en
# diez líneas y no depende de nadie.
# =====================================================================
def componentes(vecinos: dict) -> tuple[int, list[int]]:
    """(número de componentes, tamaños ordenados de mayor a menor)."""
    visto, tam = set(), []
    for s in vecinos:
        if s in visto:
            continue
        n, cola = 0, deque([s])
        visto.add(s)
        while cola:
            u = cola.popleft()
            n += 1
            for v in vecinos[u]:
                if v not in visto:
                    visto.add(v)
                    cola.append(v)
        tam.append(n)
    return len(tam), sorted(tam, reverse=True)


def resumen(vecinos: dict) -> dict:
    """Lo mismo que publica `resumen_nb()` del generador, recalculado.

    `enlaces` cuenta i→j y `pares` cuenta {i, j}: en una vecindad de k
    vecinos NO son el doble uno del otro, y confundirlos es lo que hacía
    que la primera versión del generador publicara «73,5 aristas».
    """
    n = len(vecinos)
    grados = np.array([len(vecinos[i]) for i in vecinos])
    pares = {tuple(sorted((i, j))) for i in vecinos for j in vecinos[i]}
    nc, _ = componentes(simetrizar(vecinos))
    return dict(enlaces=int(grados.sum()), pares=len(pares),
                grado=float(grados.mean()), grado_min=int(grados.min()),
                grado_max=int(grados.max()), islas=int((grados == 0).sum()),
                subgrafos=nc,
                densidad_pct=100.0 * grados.sum() / (n * (n - 1)))


def simetrizar(vecinos: dict) -> dict:
    """El grafo NO dirigido que subyace, para contar componentes.

    Sin esto, una vecindad de k vecinos daría componentes distintas según
    por dónde se empiece a recorrer, que es un número sin significado.
    """
    s = {i: set(js) for i, js in vecinos.items()}
    for i, js in vecinos.items():
        for j in js:
            s[j].add(i)
    return {i: sorted(js) for i, js in s.items()}


def vecinos_de(vecinos: dict, j: int) -> list:
    return vecinos.get(j, [])


def asimetricos(vecinos: dict) -> int:
    return sum(1 for i in vecinos for j in vecinos[i] if i not in vecinos[j])


def crime_de(col):
    return col["CRIME"].to_numpy(dtype=float)


def de_w(w) -> dict:
    """Los vecinos de un objeto de libpysal, con índices 0..n-1."""
    orden = {k: i for i, k in enumerate(w.id_order)}
    return {orden[k]: sorted(orden[v] for v in w.neighbors[k]) for k in w.id_order}


# =====================================================================
# LOS CINCO ESTILOS, POR DEFINICIÓN
# =====================================================================
def pesos_estilo(vecinos: dict, estilo: str) -> np.ndarray:
    n = len(vecinos)
    A = np.zeros((n, n))
    for i, js in vecinos.items():
        for j in js:
            A[i, j] = 1.0
    if estilo == "B":
        return A
    if estilo == "W":
        s = A.sum(axis=1, keepdims=True)
        s[s == 0] = 1.0
        return A / s
    if estilo == "C":
        # Escala GLOBAL: el total de la matriz vale n.
        return A * (n / A.sum())
    if estilo == "U":
        return A / A.sum()
    if estilo == "S":
        # Estabilización de varianza (Tiefelsdorf): cada fila se divide
        # por la raíz de la suma de sus cuadrados y luego TODO se reescala
        # para que el total sea n. Los dos pasos, en ese orden.
        q = np.sqrt((A ** 2).sum(axis=1, keepdims=True))
        q[q == 0] = 1.0
        S = A / q
        return S * (n / S.sum())
    raise ValueError(estilo)


def main() -> int:  # noqa: C901
    a = Auditoria("Precálculo del capítulo 6 verificado")
    D, p_datos = carga("CAP6_DATOS", "cap6_datos.json")
    M, _ = carga("CAP6_MAPAS", "cap6_mapas.json")

    # -----------------------------------------------------------------
    a.titulo("1 · Los dos tableros, releídos con geopandas")
    col = gpd.read_file(libpysal.examples.get_path("columbus.shp"))
    a.igual(len(col), D["m1"]["columbus"]["n"], "Columbus: barrios")
    a.igual(col["CRIME"].mean(), D["m1"]["columbus"]["variables"]["crime"]["media"],
            "Columbus: media de CRIME", tol=1e-4)
    a.igual(col["CRIME"].std(ddof=1), D["m1"]["columbus"]["variables"]["crime"]["sd"],
            "Columbus: desviación de CRIME", tol=1e-4)
    # Y que NO se publique un área: el tablero no tiene CRS y cualquier
    # cifra de superficie sería inventada. Se comprueba la ausencia, que es
    # una decisión y no un olvido.
    a.cierto("area_km2" not in D["m1"]["columbus"],
             "Columbus: no publica área, porque no tiene CRS")

    mun = gpd.read_file(PROCESADO / "colombia_adm2.gpkg")
    llave = __import__("pandas").read_csv(PROCESADO / "municipios_llave.csv",
                                          dtype={"divipola": str})
    mun = mun.merge(llave, on="shapeID", how="left")
    des = mun["desercion"].to_numpy(dtype=float)
    ok = np.isfinite(des)
    m1m = D["m1"]["municipios"]
    a.igual(len(mun), m1m["n"], "municipios: polígonos de la capa")
    a.igual(int(ok.sum()), m1m["con_dato"], "municipios: con dato de deserción")
    a.igual(des[ok].mean(), m1m["desercion"]["media"], "deserción: media", tol=1e-4)
    a.igual(des[ok].std(ddof=1), m1m["desercion"]["sd"], "deserción: desviación", tol=1e-4)
    a.igual(des[ok].max(), m1m["desercion"]["max"], "deserción: máximo", tol=1e-4)
    a.igual(int((des[ok] == 0).sum()), m1m["desercion"]["ceros"], "deserción: ceros exactos")

    # -----------------------------------------------------------------
    a.titulo("2 · Las diez W de Columbus, recalculadas con libpysal")
    cent = col.geometry.centroid
    xy = np.c_[cent.x, cent.y]
    nb_col = {
        "reina": de_w(weights.Queen.from_dataframe(col, use_index=True)),
        "torre": de_w(weights.Rook.from_dataframe(col, use_index=True)),
        "k1": de_w(weights.KNN.from_dataframe(col, k=1, use_index=True)),
        "k3": de_w(weights.KNN.from_dataframe(col, k=3, use_index=True)),
        "k6": de_w(weights.KNN.from_dataframe(col, k=6, use_index=True)),
        "delaunay": de_w(weights.Delaunay(xy)),
        "gabriel": de_w(weights.Gabriel(xy)),
    }
    # El umbral que no deja islas: la mayor distancia al vecino más
    # próximo. Se recalcula aquí desde las coordenadas.
    d = np.sqrt(((xy[:, None, :] - xy[None, :, :]) ** 2).sum(-1))
    np.fill_diagonal(d, np.inf)
    umbral = d.min(axis=1).max()
    a.igual(umbral, D["m2"]["umbral_sin_islas"],
            "Columbus: el umbral que no deja islas", tol=1e-3)
    nb_col["d_mitad"] = banda(d, umbral * 0.5)
    nb_col["d_conexo"] = banda(d, umbral)

    pub = {c["id"]: c for c in D["m2"]["criterios"]}
    for k, v in nb_col.items():
        r = resumen(v)
        p = pub[k]
        a.igual(r["pares"], p["pares"], f"{k}: parejas distintas")
        a.igual(r["enlaces"], p["enlaces"], f"{k}: enlaces dirigidos")
        a.igual(r["grado"], p["grado"], f"{k}: grado medio", tol=1e-4)
        a.igual(r["islas"], p["islas"], f"{k}: islas")
        a.igual(r["subgrafos"], p["subgrafos"], f"{k}: subgrafos")
        # La simetría se RECALCULA, no se lee. El arnés encontró que el
        # auditor la comprobaba en el módulo 4 y no aquí, así que una `k3`
        # declarada simétrica pasaba entera.
        sim = all(i in vecinos_de(v, j) for i in v for j in v[i])
        a.cierto(sim == p["simetrica"], f"{k}: la simetría publicada es la real",
                 f"real {sim} · publicada {p['simetrica']}")
    a.salta("esfera: recalculada", "libpysal no trae la esfera de influencia")
    esf = pub["esfera"]
    a.cierto(pub["gabriel"]["pares"] <= esf["pares"] <= pub["delaunay"]["pares"],
             "esfera: su tamaño cae entre Gabriel y Delaunay",
             f"{pub['gabriel']['pares']} ≤ {esf['pares']} ≤ {pub['delaunay']['pares']}")
    a.cierto(esf["simetrica"], "esfera: es simétrica, como debe")

    # Las anclas de Anselin, comprobadas también desde este lado.
    a.igual(resumen(nb_col["reina"])["pares"], 118, "Anselin: reina, 118 parejas")
    a.igual(resumen(nb_col["reina"])["grado"], 4.8163, "Anselin: reina, grado 4,8163", tol=1e-4)
    a.igual(resumen(nb_col["torre"])["pares"], 100, "Anselin: torre, 100 parejas")

    # -----------------------------------------------------------------
    a.titulo("3 · Contigüidad: reina, torre y los órdenes")
    p_r = {tuple(sorted((i, j))) for i in nb_col["reina"] for j in nb_col["reina"][i]}
    p_t = {tuple(sorted((i, j))) for i in nb_col["torre"] for j in nb_col["torre"][i]}
    a.igual(len(p_r - p_t), D["m3"]["solo_reina"],
            "las parejas que solo tiene la reina")
    a.cierto(p_t <= p_r, "y la torre está contenida en la reina")
    mun_q = reina_municipal(mun, PROCESADO / "colombia_adm2.gpkg")
    rm = resumen(mun_q)
    a.igual(rm["pares"], D["m3"]["municipios"]["reina"]["pares"],
            "municipios reina: parejas")
    a.igual(rm["grado"], D["m3"]["municipios"]["reina"]["grado"],
            "municipios reina: grado medio", tol=1e-4)
    a.igual(rm["islas"], D["m3"]["municipios"]["reina"]["islas"], "municipios reina: islas")
    a.igual(rm["subgrafos"], D["m3"]["municipios"]["reina"]["subgrafos"],
            "municipios reina: subgrafos")

    # -----------------------------------------------------------------
    a.titulo("4 · k vecinos: siempre k, y la simetría rota")
    for p in D["m4"]["columbus"]:
        k = p["k"]
        v = de_w(weights.KNN.from_dataframe(col, k=k, use_index=True))
        a.igual(resumen(v)["grado"], k, f"k={k}: el grado es exactamente k")
        a.igual(asimetricos(v), p["asimetricos"], f"k={k}: pares asimétricos")
        a.cierto(p["simetrica"] is False, f"k={k}: se publica como asimétrica")
    a.cierto(all(p["grado"] == p["k"] for p in D["m4"]["columbus"]),
             "todas las k dan grado k, que es el punto")

    # -----------------------------------------------------------------
    a.titulo("5 · Umbral de distancia, e islas")
    for c in D["m5"]["columbus"]["curva"]:
        v = banda(d, c["umbral"])
        r = resumen(v)
        a.igual(r["pares"], c["pares"], f"umbral {c['umbral']:.3f}: parejas")
        a.igual(r["islas"], c["islas"], f"umbral {c['umbral']:.3f}: islas")
    ult = D["m5"]["columbus"]["curva"][-1]
    a.cierto(ult["islas"] == 0, "el umbral mayor no deja islas", str(ult["islas"]))
    # ESTA COMPROBACIÓN ESTABA ESCRITA CON UN `or True` Y NO PODÍA FALLAR.
    # La cazó el arnés al no verla fallar nunca, que es exactamente para lo
    # que existe: una comprobación que siempre pasa es peor que ninguna,
    # porque suma al recuento. Ahora afirma lo que el módulo enseña.
    sin_islas = [c for c in D["m5"]["columbus"]["curva"] if c["islas"] == 0]
    a.cierto(any(c["subgrafos"] > 1 for c in sin_islas),
             "y quitar islas no implica conectar el grafo",
             f"subgrafos: {[c['subgrafos'] for c in sin_islas]}")
    mm = D["m5"]["municipios"]
    a.cierto(mm["en_el_umbral"]["islas"] == 0,
             "municipios: en el umbral no quedan islas")
    a.cierto(mm["en_el_umbral"]["subgrafos"] >= 2,
             "y sin embargo el grafo sigue partido",
             f"{mm['en_el_umbral']['subgrafos']} subgrafos")
    a.cierto(mm["en_el_umbral"]["grado"] > 100,
             "y su grado medio lo hace impublicable",
             f"{mm['en_el_umbral']['grado']}")

    # -----------------------------------------------------------------
    a.titulo("6 · Vecindades geométricas y su anidamiento")
    geo = {"delaunay": de_w(weights.Delaunay(xy)),
           "gabriel": de_w(weights.Gabriel(xy)),
           "relativa": de_w(weights.Relative_Neighborhood(xy))}
    pubg = {g["id"]: g for g in D["m6"]["columbus"]}
    for k, v in geo.items():
        a.igual(resumen(v)["pares"], pubg[k]["pares"], f"{k}: parejas (libpysal)")
    pr = {tuple(sorted((i, j))) for i in geo["relativa"] for j in geo["relativa"][i]}
    pg = {tuple(sorted((i, j))) for i in geo["gabriel"] for j in geo["gabriel"][i]}
    pd_ = {tuple(sorted((i, j))) for i in geo["delaunay"] for j in geo["delaunay"][i]}
    a.cierto(pr <= pg, "relativa está contenida en Gabriel")
    a.cierto(pg <= pd_, "Gabriel está contenido en Delaunay")
    a.cierto(D["m6"]["anidamiento"]["relativa_en_gabriel"] is True,
             "y el generador publica ese anidamiento")
    a.cierto(D["m6"]["anidamiento"]["gabriel_en_delaunay"] is True,
             "y el otro también")

    # -----------------------------------------------------------------
    a.titulo("7 · Los cinco estilos, desde la adyacencia")
    crime = col["CRIME"].to_numpy(dtype=float)
    pube = {e["id"]: e for e in D["m7"]["estilos"]}
    i_max = D["m7"]["unidad_max"]["i"] - 1      # R indexa desde 1
    i_min = D["m7"]["unidad_min"]["i"] - 1
    grados = np.array([len(nb_col["reina"][i]) for i in nb_col["reina"]])
    a.igual(grados[i_max], D["m7"]["unidad_max"]["grado"], "la unidad de más vecinos")
    a.igual(grados[i_min], D["m7"]["unidad_min"]["grado"], "la de menos")
    for e in ("B", "W", "S", "C", "U"):
        Wm = pesos_estilo(nb_col["reina"], e)
        p = pube[e]
        a.igual(Wm.sum(), p["suma_total"], f"estilo {e}: la suma total", tol=1e-4)
        a.igual(Wm[i_max][nb_col["reina"][i_max][0]], p["peso_max"],
                f"estilo {e}: el peso de la unidad grande", tol=1e-4)
        lag = Wm @ crime
        a.igual(lag.mean(), p["lag_medio"], f"estilo {e}: media del rezago", tol=1e-3)
        a.igual(np.corrcoef(crime, lag)[0, 1], p["cor_con_crime"],
                f"estilo {e}: correlación con CRIME", tol=1e-3)
    a.cierto(abs(pube["W"]["suma_total"] - len(col)) < 1e-6,
             "W suma n, porque cada fila suma 1", str(pube["W"]["suma_total"]))
    a.cierto(abs(pube["U"]["suma_total"] - 1) < 1e-6,
             "y U suma 1, que es la otra convención")

    # -----------------------------------------------------------------
    a.titulo("8 · spdep contra sfdep: lo que sí es comprobable")
    a.salta("sfdep: recalculado", "es otra interfaz del MISMO motor de R")
    a.igual(D["m8"]["n_pares_sfdep"], D["m8"]["n_pares_spdep"],
            "las dos vías cuentan las mismas parejas")
    a.igual(D["m8"]["dif_max"], 0.0, "y su rezago no difiere", tol=1e-9)
    a.igual(D["m8"]["n_pares_spdep"], resumen(nb_col["reina"])["pares"],
            "y coinciden con lo que cuenta libpysal")
    # Los tres rezagos que el bloque de código imprime, recalculados por
    # el producto W·y. Es la misma cifra por la que `verifica_bloques.py`
    # ejecutará el bloque: si el auditor y el bloque no coincidieran,
    # habría dos verdades publicadas en la misma página.
    wy3 = (pesos_estilo(nb_col["reina"], "W") @ crime_de(col))[:3]
    for k, (calc, publ) in enumerate(zip(wy3, D["m8"]["wy_primeros"]), 1):
        a.igual(calc, publ, f"el rezago publicado nº {k}", tol=1e-4)

    # -----------------------------------------------------------------
    a.titulo("9 · Islas y zero.policy, sobre el dato real")
    grados_m = np.array([len(mun_q[i]) for i in mun_q])
    islas_i = np.where(grados_m == 0)[0]
    a.igual(len(islas_i), D["m9"]["islas"], "las islas que hay")
    nc, tam = componentes(simetrizar(mun_q))
    a.igual(nc, D["m9"]["subgrafos"], "las componentes conexas")
    a.igual(tam[0], D["m9"]["tamanos_subgrafo"][0], "el tamaño de la mayor")
    a.cierto(sum(D["m9"]["tamanos_subgrafo"]) == len(mun),
             "y los tamaños suman los municipios",
             str(sum(D["m9"]["tamanos_subgrafo"])))
    nombres = set(mun["municipio"].to_numpy()[islas_i])
    a.cierto(nombres == set(D["m9"]["islas_nombre"]),
             "y son las islas que el capítulo nombra", str(sorted(nombres)))
    a.cierto("zero.policy" in (D["m9"]["error_sin_zero_policy"] or ""),
             "el mensaje de R menciona zero.policy",
             (D["m9"]["error_sin_zero_policy"] or "")[:40])
    a.igual(D["m9"]["lag_isla"], 0.0, "el rezago de una isla vale cero")

    # -----------------------------------------------------------------
    a.titulo("10 · El rezago sobre la deserción")
    sub = np.where(ok)[0]
    idx = {v: i for i, v in enumerate(sub)}
    nb_sub = {i: [idx[j] for j in mun_q[v] if j in idx] for i, v in enumerate(sub)}
    Wsub = pesos_estilo(nb_sub, "W")
    y = des[sub]
    wy = Wsub @ y
    con = np.array([len(nb_sub[i]) for i in nb_sub]) > 0
    a.igual(len(sub), D["m10"]["n"], "municipios con dato")
    a.igual(int((~con).sum()), D["m10"]["islas_en_el_subconjunto"],
            "islas dentro del subconjunto")
    a.igual(np.corrcoef(y[con], wy[con])[0, 1], D["m10"]["correlacion"],
            "correlación entre y y su rezago", tol=1e-3)
    a.igual(wy[con].std(ddof=1), D["m10"]["wy"]["sd"], "desviación del rezago", tol=1e-3)
    a.igual(100 * (1 - wy[con].std(ddof=1) / y.std(ddof=1)),
            D["m10"]["contraccion_pct"], "la contracción, en tanto por ciento", tol=1e-2)
    a.cierto(D["m10"]["contraccion_pct"] > 0,
             "el rezago contrae: es una media de vecinos")

    # -----------------------------------------------------------------
    a.titulo("11 · W como matriz de adyacencia")
    c11 = D["m11"]["columbus"]
    A = pesos_estilo(nb_col["reina"], "B")
    a.igual(int((A > 0).sum()), c11["no_ceros"], "Columbus: casillas ocupadas")
    a.igual(100 * (A > 0).sum() / len(col) ** 2, c11["densidad_pct"],
            "Columbus: densidad de la matriz", tol=1e-3)
    Wrow = pesos_estilo(nb_col["reina"], "W")
    Dinv = np.diag(1.0 / A.sum(axis=1))
    a.igual(np.abs(Wrow - Dinv @ A).max(), 0.0,
            "D⁻¹A es la estandarizada por filas", tol=1e-12)
    a.igual(c11["d_inv_a_igual_w"], 0.0, "y el generador publica esa igualdad", tol=1e-9)
    a.igual(c11["lag_es_producto"], 0.0, "y que el rezago ES el producto", tol=1e-9)
    m11m = D["m11"]["municipios"]
    a.igual(int(grados_m.sum()), m11m["no_ceros"], "municipios: casillas ocupadas")
    a.cierto(m11m["densidad_pct"] < 1.0,
             "y la matriz municipal es dispersa de verdad",
             f"{m11m['densidad_pct']} %")

    # -----------------------------------------------------------------
    a.titulo("12 · Los mapas")
    for nombre in ("cap6-w", "cap6-municipios"):
        a.cierto(nombre in M, f"{nombre}: está en el JSON de mapas")
        if nombre in M:
            audita_geomapa(a, M[nombre], nombre, presupuesto_kb=400.0)
            # `audita_geomapa` exige que el modo sea UNO DE LOS CINCO, no
            # que sea el suyo. Los dos mapas de este capítulo son grafos, y
            # uno que se publicara como `poligonos` se dibujaría sin una
            # sola arista —que es todo el capítulo— sin que nada fallara.
            # Lo encontró el arnés, no la lectura.
            a.cierto(M[nombre].get("modo") == "grafo",
                     f"{nombre}: y su modo es grafo", str(M[nombre].get("modo")))
    g = M.get("cap6-w", {})
    a.cierto(set(g.get("variantes", {}).keys()) == set(pub.keys()),
             "el mapa trae las diez variantes del módulo 2",
             str(len(g.get("variantes", {}))))
    for k, v in g.get("variantes", {}).items():
        a.igual(v["n_aristas"], pub[k]["pares"],
                f"mapa {k}: sus aristas son las parejas")
        a.igual(v["islas"], pub[k]["islas"], f"mapa {k}: sus islas")

    # -----------------------------------------------------------------
    a.titulo("13 · Formato")
    txt = p_datos.read_text(encoding="utf-8")
    a.cierto("Ã" not in txt and "�" not in txt,
             "datos: las tildes están intactas")
    a.cierto("ó" in txt or "í" in txt, "y hay tildes de verdad que comprobar")
    excesivos = [(r, n) for r, n in decimales(D) if n > 10]
    a.cierto(not excesivos, "ningún flotante pasa de 10 decimales", str(excesivos[:3]))
    a.igual(D["meta"]["capitulo"], 6, "la metainformación dice capítulo 6")
    a.cierto(D["meta"]["semanas"] == "10-11", "y que cubre las semanas 10 y 11",
             D["meta"]["semanas"])
    a.cierto(D["meta"]["anclas"] >= 6, "el generador comprobó sus anclas",
             f"{D['meta']['anclas']} anclas")

    return a.cierre()


def banda(d: np.ndarray, umbral: float) -> dict:
    """La vecindad por umbral, desde la matriz de distancias."""
    n = d.shape[0]
    return {i: [j for j in range(n) if j != i and d[i, j] <= umbral] for i in range(n)}


if __name__ == "__main__":
    raise SystemExit(main())
