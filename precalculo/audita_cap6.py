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
def reina_municipal(mun, ruta: pathlib.Path, criterio: str = "reina") -> dict:
    st = ruta.stat()
    llave = f"{st.st_size}·{int(st.st_mtime)}·{len(mun)}"
    f = PRECALCULO / "cache" / f"audita_cap6_{criterio}.json"
    if f.exists():
        guardado = json.loads(f.read_text(encoding="utf-8"))
        if guardado.get("llave") == llave:
            return {int(k): v for k, v in guardado["vecinos"].items()}
    clase = weights.Queen if criterio == "reina" else weights.Rook
    v = de_w(clase.from_dataframe(mun, use_index=True))
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


# =====================================================================
# LO QUE AÑADIÓ LA AUDITORÍA DE CONTENIDO DEL 2026-11-03
#
# Cinco frases del capítulo eran falsas con las cifras bien calculadas: la
# reina como «la de Anselin», el umbral municipal atribuido a San Andrés,
# Leticia y Manizales de vecinas, «Moran supone una W simétrica» y la serie
# de órdenes que «se queda sin sitios». La prosa nueva se apoya en cifras
# nuevas, y cada una se recalcula aquí por un camino que no pasa por spdep.
# =====================================================================
def cuello_mst(d: np.ndarray) -> float:
    """La arista más larga del árbol generador mínimo (Prim): el umbral
    mínimo con el que el grafo de distancias queda de una pieza."""
    n = len(d)
    dentro = np.zeros(n, dtype=bool)
    dentro[0] = True
    mejor = d[0].copy()
    mx = 0.0
    for _ in range(n - 1):
        mejor[dentro] = np.inf
        j = int(np.argmin(mejor))
        mx = max(mx, float(mejor[j]))
        dentro[j] = True
        mejor = np.minimum(mejor, d[j])
    return mx


def distancias_bfs(vecinos: dict) -> np.ndarray:
    """La distancia en el grafo entre cada par, por recorridos en anchura."""
    n = len(vecinos)
    dist = np.full((n, n), -1, dtype=int)
    for s in vecinos:
        dist[s, s] = 0
        cola = deque([s])
        while cola:
            u = cola.popleft()
            for v in vecinos[u]:
                if dist[s, v] < 0:
                    dist[s, v] = dist[s, u] + 1
                    cola.append(v)
    return dist


def moran_i(y: np.ndarray, Wm: np.ndarray, n_ajustado: int | None = None) -> float:
    """I = (n / S0) · z'Wz / z'z, con el n que se le diga (el de spdep con
    `adjust.n = TRUE` descuenta las unidades sin vecinos)."""
    z = y - y.mean()
    n = len(y) if n_ajustado is None else n_ajustado
    return float(n / Wm.sum() * (z @ Wm @ z) / (z @ z))


def lee_gal(ruta: pathlib.Path) -> dict:
    """Un archivo GAL: cabecera, y luego pares de líneas «id n» / «vecinos»."""
    filas = [l.split() for l in ruta.read_text(encoding="utf-8").splitlines() if l.strip()]
    vec, k = {}, 1
    while k < len(filas):
        i = int(filas[k][0])
        vec[i] = [int(x) for x in filas[k + 1]] if int(filas[k][1]) > 0 else []
        k += 2 if int(filas[k][1]) > 0 else 1
    return vec


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
    # LA ESFERA DE INFLUENCIA, POR SU DEFINICIÓN. libpysal no la trae, y
    # hasta el 2026-11-03 este auditor se conformaba con que su tamaño cayera
    # «entre Gabriel y Delaunay», que es justo la propiedad que `soi.graph`
    # fabrica al partir de la triangulación. Ahora se calcula: i y j son
    # vecinos si d_ij <= r_i + r_j, con r el radio al más próximo. La de spdep
    # tiene que ser esa misma esfera RESTRINGIDA a Delaunay, y la definición
    # tiene parejas fuera de Delaunay.
    r_nn = d.min(axis=1)
    p_soi = {(i, j) for i in range(len(xy)) for j in range(i + 1, len(xy))
             if d[i, j] <= r_nn[i] + r_nn[j]}
    p_del = {tuple(sorted((i, j))) for i in nb_col["delaunay"] for j in nb_col["delaunay"][i]}
    p_gab = {tuple(sorted((i, j))) for i in nb_col["gabriel"] for j in nb_col["gabriel"][i]}
    p_soi_del = p_soi & p_del
    ed = D["m6"]["esfera_definicion"]
    esf = pub["esfera"]
    a.igual(len(p_soi), ed["pares"], "esfera por definición: parejas")
    a.igual(len(p_soi - p_del), ed["fuera_de_delaunay"], "esfera por definición: fuera de Delaunay")
    a.cierto(len(p_soi - p_del) > 0, "la esfera por definición NO está contenida en Delaunay")
    a.igual(len(p_soi_del), esf["pares"], "la esfera de spdep es la definición restringida a Delaunay")
    a.igual(esf["pares"], ed["pares_spdep"], "y el JSON lo publica dos veces igual")
    a.cierto(esf["simetrica"], "esfera: es simétrica, como debe")
    an = D["m6"]["anidamiento"]
    a.cierto(an["gabriel_en_esfera"] == (p_gab <= p_soi_del), "¿Gabriel dentro de la esfera?, recalculado",
             f"publicado {an['gabriel_en_esfera']}")
    a.cierto(an["esfera_en_gabriel"] == (p_soi_del <= p_gab), "¿la esfera dentro de Gabriel?, recalculado",
             f"publicado {an['esfera_en_gabriel']}")

    # Las anclas del tablero: la reina y la torre de los POLÍGONOS, que dan
    # igual poly2nb y libpysal. Hasta el 2026-11-03 se llamaban «de Anselin»,
    # y la W de Anselin, la GAL de 1988, tiene 116 parejas (sección 3).
    a.igual(resumen(nb_col["reina"])["pares"], 118, "reina de los polígonos: 118 parejas")
    a.igual(resumen(nb_col["reina"])["grado"], 4.8163, "reina de los polígonos: grado 4.8163", tol=1e-4)
    a.igual(resumen(nb_col["torre"])["pares"], 100, "torre de los polígonos: 100 parejas")

    # -----------------------------------------------------------------
    a.titulo("3 · Contigüidad: reina, torre y los órdenes")
    p_r = {tuple(sorted((i, j))) for i in nb_col["reina"] for j in nb_col["reina"][i]}
    p_t = {tuple(sorted((i, j))) for i in nb_col["torre"] for j in nb_col["torre"][i]}
    a.igual(len(p_r - p_t), D["m3"]["solo_reina"],
            "las parejas que solo tiene la reina")
    a.cierto(p_t <= p_r, "y la torre está contenida en la reina")
    a.igual(100 * len(p_r - p_t) / len(p_r), D["m3"]["pct_esquina"],
            "qué parte de la reina son esquinas", tol=1e-3)
    # LOS ÓRDENES, HASTA EL DIÁMETRO, por distancias en el grafo. `nblag`
    # cuenta el orden k como los que están a distancia EXACTAMENTE k: es lo
    # mismo que un recorrido en anchura, sin pasar por spdep.
    dist_r = distancias_bfs(nb_col["reina"])
    sup = dist_r[np.triu_indices(len(dist_r), 1)]
    a.cierto(bool((sup > 0).all()), "la reina de Columbus es conexa (toda pareja tiene distancia)")
    por_orden = np.bincount(sup)[1:]
    a.igual(len(por_orden), D["m3"]["diametro"], "el diámetro de la reina")
    a.igual(len(D["m3"]["ordenes"]), D["m3"]["diametro"], "se publica un orden por cada paso del diámetro")
    a.igual(len(sup), D["m3"]["parejas_posibles"], "las parejas posibles, n(n − 1)/2")
    acum = np.cumsum(por_orden)
    for o in D["m3"]["ordenes"]:
        k = o["orden"]
        a.igual(por_orden[k - 1], o["pares"], f"orden {k}: parejas (BFS)")
        a.igual(acum[k - 1], o["acumuladas"], f"orden {k}: acumuladas")
        a.igual(100 * acum[k - 1] / len(sup), o["pct_acumulado"], f"orden {k}: % acumulado", tol=1e-3)
    cima = int(np.argmax(por_orden)) + 1
    a.cierto(cima == 3, "la serie hace cima en el orden 3, que es lo que el módulo lee", f"cima en {cima}")
    # LA GAL DE ANSELIN no está en Python (es el `COL.nb` de spdep), así que
    # se comprueba lo que se puede: que sus cuentas cuadren con la reina, y
    # que el otro generador, el de la animación, publique las mismas parejas.
    g = D["m3"]["gal"]
    a.igual(g["pares"], D["m3"]["reina"]["pares"] - g["solo_reina"] + g["solo_gal"],
            "GAL: reina − las que solo tiene la reina + las que solo tiene la GAL")
    a.igual(g["enlaces"], 2 * g["pares"], "GAL: es simétrica, enlaces = 2 · parejas")
    a.igual(g["grado"], g["enlaces"] / D["m1"]["columbus"]["n"], "GAL: grado medio", tol=1e-4)
    a.cierto(g["solo_reina_esquinas"] <= min(g["solo_reina"], D["m3"]["solo_reina"]),
             "GAL: las esquinas que le faltan no son más que las que tiene la reina")
    RS = json.loads((SALIDAS / "cap6_rezago2d_resumen.json").read_text(encoding="utf-8"))
    a.igual(g["pares"], RS["parejas_gal"], "GAL: las mismas parejas que publica la animación")
    # La biblioteca de R del usuario o la del sistema, la que la tenga.
    gal_sp = next((f for raiz, patron in (
        (pathlib.Path.home() / "Library" / "R", "*/*/library/spData/weights/columbus.gal"),
        (pathlib.Path("/Library/Frameworks/R.framework/Versions"),
         "*/Resources/library/spData/weights/columbus.gal"))
        if raiz.exists() for f in raiz.glob(patron)), None)
    if gal_sp is None:
        a.salta("el columbus.gal de spData", "no está instalado en esta máquina")
    else:
        vg = lee_gal(gal_sp)
        a.igual(len({tuple(sorted((i, j))) for i in vg for j in vg[i]}), g["pares_spdata"],
                "el columbus.gal de spData: parejas, leído del archivo")
    mun_q = reina_municipal(mun, PROCESADO / "colombia_adm2.gpkg")
    rm = resumen(mun_q)
    a.igual(rm["pares"], D["m3"]["municipios"]["reina"]["pares"],
            "municipios reina: parejas")
    a.igual(rm["grado"], D["m3"]["municipios"]["reina"]["grado"],
            "municipios reina: grado medio", tol=1e-4)
    a.igual(rm["islas"], D["m3"]["municipios"]["reina"]["islas"], "municipios reina: islas")
    a.igual(rm["subgrafos"], D["m3"]["municipios"]["reina"]["subgrafos"],
            "municipios reina: subgrafos")
    mun_t = reina_municipal(mun, PROCESADO / "colombia_adm2.gpkg", "torre")
    pm_r = {tuple(sorted((i, j))) for i in mun_q for j in mun_q[i]}
    pm_t = {tuple(sorted((i, j))) for i in mun_t for j in mun_t[i]}
    a.igual(len(pm_t), D["m3"]["municipios"]["torre"]["pares"], "municipios torre: parejas")
    a.igual(len(pm_r - pm_t), D["m3"]["municipios"]["solo_reina"], "municipios: las que solo tiene la reina")
    a.igual(100 * len(pm_r - pm_t) / len(pm_r), D["m3"]["municipios"]["pct_esquina"],
            "municipios: qué parte de la reina son esquinas", tol=1e-3)

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
    # Moran con la W de k = 3 tal como viene, y simetrizada antes: la prosa
    # decía que Moran «supone una W simétrica», y las dos cifras difieren.
    v3 = de_w(weights.KNN.from_dataframe(col, k=3, use_index=True))
    mk = D["m4"]["moran_k3"]
    I_asim = moran_i(crime_de(col), pesos_estilo(v3, "W"))
    I_sim = moran_i(crime_de(col), pesos_estilo(simetrizar(v3), "W"))
    a.igual(I_asim, mk["asimetrica"], "Moran con k = 3 sin simetrizar", tol=1e-4)
    a.igual(I_sim, mk["simetrizada"], "Moran con k = 3 simetrizada", tol=1e-4)
    a.cierto(abs(I_asim - I_sim) > 0.01, "simetrizar cambia el índice", f"{I_asim:.4f} frente a {I_sim:.4f}")
    Wr = pesos_estilo(nb_col["reina"], "W")
    a.cierto(mk["reina_por_filas_simetrica"] == bool(np.allclose(Wr, Wr.T)),
             "la reina por filas no es simétrica, y así se publica")

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

    # EL UMBRAL QUE CONECTA COLUMBUS: la arista más larga del árbol
    # generador mínimo. La prosa decía «hace falta subir hasta 0.7426», que
    # es solo el punto siguiente del barrido.
    c5 = D["m5"]["columbus"]
    u_con = cuello_mst(np.where(np.isinf(d), 0.0, d))
    a.igual(u_con, c5["umbral_conexo"], "Columbus: el umbral mínimo que conecta", tol=1e-3)
    rc = resumen(banda(d, u_con))
    a.igual(rc["subgrafos"], 1, "Columbus: en ese umbral, una sola pieza")
    a.igual(rc["subgrafos"], c5["en_el_conexo"]["subgrafos"], "y así se publica")
    a.igual(rc["pares"], c5["en_el_conexo"]["pares"], "Columbus: parejas en el umbral conexo")
    a.igual(rc["grado"], c5["en_el_conexo"]["grado"], "Columbus: grado en el umbral conexo", tol=1e-4)
    a.cierto(resumen(banda(d, u_con * (1 - 1e-9)))["subgrafos"] > 1,
             "Columbus: justo por debajo, más de una pieza")
    a.cierto(c5["umbral_sin_islas"] < c5["umbral_conexo"] < c5["curva"][4]["umbral"],
             "el conexo cae entre el sin islas y el punto siguiente del barrido")

    # QUIÉN FIJA EL UMBRAL MUNICIPAL, y lo que pasa con el archipiélago. La
    # prosa lo atribuía a San Andrés, y es de Puerto Carreño.
    cen_m = mun.geometry.centroid
    xym = np.c_[cen_m.x, cen_m.y]
    dm = np.sqrt(((xym[:, None, :] - xym[None, :, :]) ** 2).sum(-1))
    np.fill_diagonal(dm, np.inf)
    nn_m = dm.min(axis=1)
    nom = mun["municipio"].to_numpy()
    dep = mun["departamento"].to_numpy()
    i_f = int(np.argmax(nn_m))
    fu = mm["fija_el_umbral"]
    a.igual(nn_m.max() / 1000, mm["umbral_sin_islas_km"], "municipios: el umbral sin islas, en km", tol=1e-3)
    a.cierto(nom[i_f] == fu["municipio"] and dep[i_f] == fu["departamento"],
             "lo fija el municipio que se publica", f"{nom[i_f]} ({dep[i_f]})")
    a.cierto(nom[int(np.argmin(dm[i_f]))] == fu["vecino"], "y su vecino más próximo es el publicado",
             nom[int(np.argmin(dm[i_f]))])
    a.igual(nn_m[i_f] / 1000, fu["km"], "a esa distancia", tol=1e-3)
    sa = int(np.where(np.array([len(mun_q[i]) for i in mun_q]) == 0)[0][0])
    a.cierto(nom[sa] == mm["san_andres"]["municipio"] == D["m9"]["islas_nombre"][0],
             "la primera isla de la reina es San Andrés", nom[sa])
    sam = mm["san_andres"]
    a.cierto(nom[int(np.argmin(dm[sa]))] == sam["vecino"], "el vecino más próximo de San Andrés",
             nom[int(np.argmin(dm[sa]))])
    a.igual(nn_m[sa] / 1000, sam["vecino_km"], "y a qué distancia", tol=1e-3)
    a.cierto(nn_m[sa] < nn_m.max(), "San Andrés NO es quien fija el umbral")
    en_u = np.where(dm[sa] <= nn_m.max())[0]
    a.cierto(set(nom[en_u]) == {sam["vecinos_en_el_umbral"]} if isinstance(sam["vecinos_en_el_umbral"], str)
             else set(nom[en_u]) == set(sam["vecinos_en_el_umbral"]),
             "en el umbral, San Andrés solo tiene a los vecinos publicados", str(sorted(set(nom[en_u]))))
    arch = dep == dep[sa]
    costa = np.where(~arch)[0]
    dc = dm[np.ix_(np.where(arch)[0], costa)]
    jc = costa[np.unravel_index(np.argmin(dc), dc.shape)[1]]
    a.cierto(nom[jc] == sam["costa"] and dep[jc] == sam["costa_departamento"],
             "el municipio de la costa más cercano al archipiélago", f"{nom[jc]} ({dep[jc]})")
    a.igual(dc.min() / 1000, sam["costa_km"], "y su distancia", tol=1e-3)
    d0 = np.where(np.isinf(dm), 0.0, dm)
    a.igual(cuello_mst(d0[np.ix_(~arch, ~arch)]) / 1000, mm["umbral_conecta_continente_km"],
            "el umbral que conecta el continente", tol=1e-3)
    a.igual(cuello_mst(d0) / 1000, mm["umbral_conecta_todo_km"], "el que conecta todo, archipiélago incluido",
            tol=1e-3)
    il = int(np.where((nom == "Leticia") & (dep == "Amazonas"))[0][0])
    im = int(np.where((nom == "Manizales") & (dep == "Caldas"))[0][0])
    lm = mm["leticia_manizales"]
    grado_u = (dm <= nn_m.max()).sum(axis=1)
    a.igual(dm[il, im] / 1000, lm["km"], "Leticia–Manizales, en km", tol=1e-3)
    a.cierto(lm["vecinas"] == bool(dm[il, im] <= nn_m.max()), "¿vecinas en esa W?, recalculado",
             f"publicado {lm['vecinas']}")
    a.igual(grado_u[il], lm["grado_leticia"], "los vecinos de Leticia en esa W")
    a.igual(grado_u[im], lm["grado_manizales"], "los de Manizales")
    a.igual(grado_u.max(), mm["en_el_umbral"]["grado_max"], "el más conectado: su grado")
    a.cierto(nom[int(np.argmax(grado_u))] == mm["mas_conectado"]["municipio"]
             and int(grado_u.max()) == mm["mas_conectado"]["grado"],
             "y quién es", f"{nom[int(np.argmax(grado_u))]} con {int(grado_u.max())}")
    # San Andrés con k = 4: a qué distancia lo une el criterio con la costa
    sk = D["m4"]["san_andres_k4"]
    v4 = np.argsort(dm[sa])[:4]
    dk = dm[sa, v4][dep[v4] != dep[sa]] / 1000
    a.igual(len(dk), sk["vecinos_costa"], "k = 4: vecinos de San Andrés en la costa")
    a.igual(dk.min(), sk["costa_min_km"], "k = 4: el más cercano, en km", tol=1e-3)
    a.igual(dk.max(), sk["costa_max_km"], "k = 4: el más lejano, en km", tol=1e-3)

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

    # ISLAS Y PEDAZOS SON DOS CUENTAS, y el módulo las publica juntas desde
    # que la prosa afirmó que la esfera de influencia unía el archipiélago a
    # la costa: no lo une, lo deja en un subgrafo propio.
    for g in D["m6"]["municipios"]:
        tam = g["tamanos_subgrafo"]
        a.igual(len(tam), g["subgrafos"], f"m6/{g['id']}: un tamaño por subgrafo")
        a.igual(sum(tam), D["m1"]["municipios"]["n"],
                f"m6/{g['id']}: los tamaños suman los municipios")
        a.igual(min(tam), g["subgrafo_menor_n"], f"m6/{g['id']}: el subgrafo menor")
        a.cierto(bool(tam == sorted(tam, reverse=True)),
                 f"m6/{g['id']}: los tamaños van de mayor a menor")
        nombres = g["subgrafo_menor_municipios"]
        a.cierto(len(nombres) == (g["subgrafo_menor_n"] if 1 < g["subgrafos"]
                                  and g["subgrafo_menor_n"] <= 5 else 0),
                 f"m6/{g['id']}: los municipios del menor, o ninguno",
                 f"{nombres}")

    # -----------------------------------------------------------------
    a.titulo("7 · Los cinco estilos, desde la adyacencia")
    crime = col["CRIME"].to_numpy(dtype=float)
    pube = {e["id"]: e for e in D["m7"]["estilos"]}
    i_max = D["m7"]["unidad_max"]["i"] - 1      # R indexa desde 1
    i_min = D["m7"]["unidad_min"]["i"] - 1
    grados = np.array([len(nb_col["reina"][i]) for i in nb_col["reina"]])
    a.igual(grados[i_max], D["m7"]["unidad_max"]["grado"], "la unidad de más vecinos")
    a.igual(grados[i_min], D["m7"]["unidad_min"]["grado"], "la de menos")
    a.igual(grados[i_max] / grados[i_min], D["m7"]["razon_w"],
            "cuántas veces pesa más, con W, el vecino de la de menos", tol=1e-4)
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
    a.salta("nb2listw se niega también con el estilo B",
            "es un comportamiento de spdep, no una cifra; lo mide el generador")

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
    # La prosa dice que la media de Wy NO tiene por qué ser la de y, y que lo que W por filas conserva (vecindad
    # simétrica) es la media ponderada por el grado (2026-10-02; antes decía «tiene que serlo»). Las dos mitades,
    # sobre el dato: la ponderada coincide a la precisión de la máquina, y la simple se mueve.
    g = np.array([len(nb_sub[i]) for i in nb_sub], dtype=float)
    a.igual((g * wy).sum() / g.sum(), (g * y).sum() / g.sum(),
            "W por filas conserva la media ponderada por el grado", tol=1e-10)
    a.cierto(abs(wy[con].mean() - y[con].mean()) > 1e-3,
             "la media simple sí se mueve: no «tiene que» coincidir",
             f"{y[con].mean():.4f} → {wy[con].mean():.4f}")
    a.igual(int(con.sum()), D["m10"]["n_con_vecinos"], "municipios con dato y con vecinos")

    # QUÉ LE HACE EL CERO DE LAS ISLAS A LOS RESÚMENES (módulo 9). La prosa
    # decía que los tira todos hacia abajo; la correlación sube. Moran, con el
    # n de spdep: `adjust.n = TRUE` descuenta las unidades sin vecinos.
    ec = D["m9"]["efecto_cero"]
    islas_sub = np.where(~con)[0]
    for k_, (calc, publ) in enumerate(zip(y[islas_sub], ec["desercion_islas"]), 1):
        a.igual(calc, publ, f"la deserción de la isla {k_}", tol=1e-4)
    a.igual(y.mean(), ec["media_y"], "la media de la deserción", tol=1e-4)
    a.igual(wy.mean(), ec["media_wy_con_ceros"], "media de Wy con el cero de las islas", tol=1e-4)
    a.igual(wy[con].mean(), ec["media_wy_sin_islas"], "media de Wy sin las islas", tol=1e-4)
    a.igual(np.corrcoef(y, wy)[0, 1], ec["cor_con_ceros"], "cor(y, Wy) con el cero", tol=1e-4)
    a.igual(np.corrcoef(y[con], wy[con])[0, 1], ec["cor_sin_islas"], "cor(y, Wy) sin las islas", tol=1e-4)
    a.cierto(ec["cor_con_ceros"] > ec["cor_sin_islas"], "con este dato, el cero SUBE la correlación")
    a.igual(moran_i(y, Wsub, int(con.sum())), ec["moran_con_islas"], "Moran con las islas (adjust.n)",
            tol=1e-5)
    a.igual(moran_i(y, Wsub), ec["moran_con_islas_sin_ajuste"], "Moran con las islas (sin ajuste)", tol=1e-5)
    a.igual(moran_i(y[con], Wsub[np.ix_(con, con)]), ec["moran_sin_islas"], "Moran sin las islas", tol=1e-5)

    # LA MISMA CORRELACIÓN CON OTRAS W (módulo 10): torre, k = 4 y 30 km.
    def cor_w(vec_todos):
        nbs = {i: [idx[j] for j in vec_todos[v] if j in idx] for i, v in enumerate(sub)}
        Ws = pesos_estilo(nbs, "W")
        w_ = Ws @ y
        cv = np.array([len(nbs[i]) for i in nbs]) > 0
        return float(np.corrcoef(y[cv], w_[cv])[0, 1]), int((~cv).sum())
    knn4 = {i: [int(j) for j in np.argsort(dm[i])[:4]] for i in range(len(dm))}
    b30 = {i: [int(j) for j in np.where(dm[i] <= 30000.0)[0]] for i in range(len(dm))}
    ow = D["m10"]["otras_w"]
    for clave, vec_t in (("torre", mun_t), ("k4", knn4), ("umbral_30km", b30)):
        r_, sv = cor_w(vec_t)
        a.igual(r_, ow[clave]["correlacion"], f"correlación con la W {clave}", tol=1e-4)
        a.igual(sv, ow[clave]["sin_vecinos"], f"municipios sin vecinos con la W {clave}")

    # El módulo dice que el I de Moran del capítulo 7 es la PENDIENTE de Wy
    # sobre y —no su correlación— cuando W va por filas. Es una identidad,
    # y aquí se comprueba sobre los dos datos del capítulo en vez de darla
    # por sabida: I = z'Wz / z'z a mano, contra `esda`, contra la pendiente
    # de mínimos cuadrados y contra cor · sd(Wy)/sd(y). Y se comprueba que
    # la correlación está lejos de I, que es lo que la frase vieja negaba.
    from esda.moran import Moran
    wq = weights.Queen.from_dataframe(col, use_index=True)
    wq.transform = "r"
    cuadros = [
        ("Columbus", crime_de(col), pesos_estilo(nb_col["reina"], "W")),
        ("municipios", y[con], Wsub[np.ix_(con, con)]),
    ]
    for nombre, yy, Wm in cuadros:
        wyy = Wm @ yy
        zz = yy - yy.mean()
        i_mano = float(zz @ Wm @ zz / (zz @ zz))
        r_yy = float(np.corrcoef(yy, wyy)[0, 1])
        a.igual(np.polyfit(yy, wyy, 1)[0], i_mano,
                f"{nombre}: I es la pendiente de Wy sobre y", tol=1e-9)
        a.igual(r_yy * wyy.std(ddof=1) / yy.std(ddof=1), i_mano,
                f"{nombre}: I = cor · sd(Wy) / sd(y)", tol=1e-9)
        a.cierto(abs(r_yy - i_mano) > 0.1,
                 f"{nombre}: y I no es la correlación",
                 f"I {i_mano:.4f} frente a cor {r_yy:.4f}")
        if nombre == "Columbus":
            a.igual(Moran(yy, wq, permutations=0).I, i_mano,
                    "Columbus: I a mano contra esda", tol=1e-9)

    # -----------------------------------------------------------------
    # LA ANIMACIÓN DEL REZAGO. `cap6_rezago2d.json` sale de `spdep` (R) y es
    # lo contra lo que `prueba_rezago2d.py` mide la aritmética del navegador.
    # Aquí se recalcula todo con numpy y libpysal, que no pasan por R.
    # -----------------------------------------------------------------
    a.titulo("10b · La animación del rezago, recalculada")
    R2, _ = carga("CAP6_REZAGO2D", "cap6_rezago2d.json")
    yc = crime_de(col)
    a.igual(np.abs(np.array(R2["y"]["crime"]) - yc).max(), 0.0,
            "CRIME del JSON es el de Columbus, dato a dato", tol=1e-9)
    a.igual(R2["y"]["media"], yc.mean(), "media de CRIME", tol=1e-9)
    a.igual(R2["y"]["sd"], yc.std(ddof=1), "desviación de CRIME", tol=1e-9)
    ks = R2["meta"]["k_max"]
    a.igual(ks, 70, "el deslizador llega hasta k = 70")
    w_lp = {"reina": weights.Queen.from_dataframe(col, use_index=True),
            "torre": weights.Rook.from_dataframe(col, use_index=True)}
    recalc = {}                     # lo recalculado aquí, para contrastar el resumen de la prosa más abajo
    for nombre in ("reina", "torre"):
        rf = R2["vecindades"][nombre]
        nb = de_w(w_lp[nombre])
        Wm = pesos_estilo(nb, "W")
        malos = sum(1 for i in range(len(yc))
                    if sorted(j + 1 for j in nb[i]) != sorted(rf["vecinos"][i]))
        a.igual(malos, 0, f"{nombre}: los vecinos de libpysal son los de R")
        a.igual(rf["n_aristas"], sum(len(v) for v in nb.values()) // 2, f"{nombre}: las parejas")
        # La serie de Wᵏy y lo que el módulo lee de ella.
        v = yc.copy()
        dif = {"media": 0.0, "sd": 0.0, "cor": 0.0, "pendiente": 0.0}
        vectores = {}
        for k in range(ks + 1):
            if k:
                v = Wm @ v
            s = rf["serie"][k]
            cov = np.cov(yc, v)[0, 1]
            calc = {"media": v.mean(), "sd": v.std(ddof=1),
                    "cor": np.corrcoef(yc, v)[0, 1], "pendiente": cov / yc.var(ddof=1)}
            for c in dif:
                dif[c] = max(dif[c], abs(calc[c] - s[c]))
            if str(k) in rf["vectores"]:
                vectores[k] = np.abs(v - np.array(rf["vectores"][str(k)])).max()
        for c, d in dif.items():
            a.igual(d, 0.0, f"{nombre}: {c} de Wᵏy, k = 0…{ks}", tol=1e-9)
        a.igual(max(vectores.values()), 0.0, f"{nombre}: Wᵏy barrio a barrio", tol=1e-9)
        a.igual(len(vectores), len(R2["meta"]["k_vectores"]), f"{nombre}: los k con vector")
        # A dónde va: la media ponderada por el grado, no la media.
        grado = np.array([len(nb[i]) for i in range(len(yc))], dtype=float)
        a.igual(rf["limite"], (grado * yc).sum() / grado.sum(), f"{nombre}: el límite Σ dᵢ yᵢ / Σ dᵢ", tol=1e-9)
        recalc[f"limite_{nombre}"] = (grado * yc).sum() / grado.sum()
        if nombre == "reina":
            recalc["W_reina"] = Wm
        a.cierto(abs(rf["limite"] - yc.mean()) > 1.5,
                 f"{nombre}: el límite no es la media de y", f"{rf['limite']:.4f} contra {yc.mean():.4f}")
        a.igual(rf["media_simple"], yc.mean(), f"{nombre}: la media simple publicada", tol=1e-9)
        # El segundo valor propio manda la velocidad, y de él salen los k para bajar al 5 %.
        mod = np.sort(np.abs(np.linalg.eigvals(Wm)))[::-1]
        a.igual(mod[0], 1.0, f"{nombre}: el mayor valor propio vale 1", tol=1e-9)
        a.igual(rf["lambda2"], mod[1], f"{nombre}: el segundo valor propio, en módulo", tol=1e-9)
        v, k5 = yc.copy(), None
        for k in range(1, 2001):
            v = Wm @ v
            if v.std(ddof=1) <= 0.05 * yc.std(ddof=1):
                k5 = k
                break
        a.igual(rf["k_5pct"], k5, f"{nombre}: aplicaciones para bajar al 5 %")
        # La prosa del módulo 10 cita esas aplicaciones: el lector tiene que poder llevar el deslizador hasta ellas.
        a.cierto(k5 is not None and k5 <= ks, f"{nombre}: el deslizador llega al k del 5 %", f"{k5} ≤ {ks}")
        recalc[f"lambda2_{nombre}"], recalc[f"k5_{nombre}"] = mod[1], k5
    # El I de Moran del capítulo 7: con la reina, es la pendiente de Wy sobre y.
    mo = Moran(yc, wq, permutations=0).I
    a.igual(R2["moran"]["I"], mo, "I de Moran de la reina, contra esda", tol=1e-9)
    a.igual(R2["moran"]["cor"] * R2["moran"]["razon_sd"], mo, "I = cor · sd(Wy)/sd(y)", tol=1e-9)

    # EL RESUMEN QUE CITA LA PROSA (`cap6_rezago2d_resumen.json`, 8 números) es lo único de todo esto que lee el
    # auditor de cifras del capítulo. Se contrasta con lo recalculado aquí, no con el JSON grande.
    a.titulo("10c · El resumen que cita la prosa del módulo 10")
    RS, _ = carga("CAP6_REZAGO2D_RESUMEN", "cap6_rezago2d_resumen.json")
    wy1 = recalc["W_reina"] @ yc
    a.igual(RS["y_media"], yc.mean(), "resumen: la media de CRIME", tol=1e-9)
    a.igual(RS["limite_reina"], recalc["limite_reina"], "resumen: el límite con la reina", tol=1e-9)
    a.igual(RS["limite_torre"], recalc["limite_torre"], "resumen: el límite con la torre", tol=1e-9)
    a.igual(RS["lambda2_reina"], recalc["lambda2_reina"], "resumen: el segundo valor propio", tol=1e-9)
    a.igual(RS["k_5pct_reina"], recalc["k5_reina"], "resumen: las aplicaciones al 5 %")
    a.igual(RS["moran_I"], mo, "resumen: el I de Moran", tol=1e-9)
    a.igual(RS["moran_cor"], np.corrcoef(yc, wy1)[0, 1], "resumen: la correlación de y con Wy", tol=1e-9)
    a.igual(RS["moran_razon_sd"], wy1.std(ddof=1) / yc.std(ddof=1), "resumen: sd(Wy) / sd(y)", tol=1e-9)

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
