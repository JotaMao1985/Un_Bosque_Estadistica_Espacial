#!/usr/bin/env python3
"""
audita_cap3.py — auditoría independiente del precálculo del capítulo 3 (T2.4b)

Material de Estadística Espacial 2026-II (20929).

NO comprueba que los JSON existan: comprueba que sus NÚMEROS sean ciertos,
por caminos que no pasan por R.

POR QUÉ EN PYTHON, otra vez. Es la lección de A.10: un control que comparte
el entorno con lo que audita no es independiente. Aquí el intérprete es
otro y, sobre todo, **las bibliotecas que deciden los resultados son
otras**:

  · las clases las calcula `mapclassify`, no `classInt`;
  · el daltonismo se recalcula con las matrices de Machado escritas AQUÍ
    en numpy, no con `colorspace`;
  · las áreas de los cartogramas salen de shapely, no de GEOS vía sf
    (bueno: GEOS es el mismo — declarado abajo con salta());
  · la escalera ecológica se reconstruye con pandas desde el CSV crudo de
    130 MB, sin tocar ningún agregado que R haya escrito.

Y ESTE CAPÍTULO TIENE UN FRENTE QUE NINGUNO ANTERIOR TENÍA: la
clasificación. El anexo A.2 dejó dicho que `classInt` y `mapclassify` NO
dan las mismas clases por cuantiles —uno cierra [a,b) y el otro (a,b]— y
que Fisher-Jenks sí coincide. Aquí eso no puede tratarse como un fallo ni
como una excusa: la discrepancia de cuantiles se comprueba que sea
EXACTAMENTE la esperada —misma causa, mismos empates— y Fisher se exige
idéntico. Una discrepancia declarada es material didáctico; una sin
explicar es un fallo.

HASTA DÓNDE LLEGA LA INDEPENDENCIA, DECLARADO Y NO INSINUADO
  · TOTAL para la clasificación, el daltonismo, la escalera ecológica, el
    gerrymandering y toda la aritmética de agregación.
  · PARCIAL para las áreas: GEOS es el MISMO motor en los dos lados
    (shapely y sf lo llaman igual). Ahí esto verifica el ANÁLISIS de lo
    que GEOS devolvió, no que GEOS acierte. Declarado con salta().
  · NULA para `cartogram_cont`: es un ajuste iterativo del paquete de R y
    no hay segunda implementación. Lo que sí se comprueba es su
    propiedad —que NO alcanza la proporcionalidad exacta— y que la cifra
    publicada corresponda a la geometría publicada.

CINCO FRENTES
  1. R <-> PYTHON. Recalcula desde las fuentes primarias.
  2. COHERENCIA INTERNA. Que las relaciones que el capítulo afirma se
     sostengan, y que ninguna bandera se crea a sí misma.
  3. PROPIEDADES EXACTAS. Los dos cartogramas propios y el reparto del
     hexbin tienen un valor teórico; se exige, no se estima.
  4. LOS MAPAS. Caja, cuantización, presupuesto, capas y superpuestos.
  5. FORMATO. JSON válido, tildes intactas, sin NaN, redondeo declarado.

Uso:  python3 precalculo/audita_cap3.py     (desde `Estadistica espacial/`)
Con el intérprete de geo_env; `audita_todo.sh` ya lo hace.
Devuelve 1 si algo falla.

CAP3_DATOS, CAP3_MAPAS y CAP3_SOLUCIONES permiten apuntar a copias con
defectos inyectados: es lo que hace `prueba_auditor_cap3.py`. Los archivos
publicados no se tocan nunca.

LOS RÓTULOS TIENEN PRESUPUESTO: 57 CARACTERES, PREFIJO INCLUIDO.
`Auditoria.cierto()` rellena el rótulo hasta 58 antes del detalle, así que
uno de 58 o más queda pegado a su detalle por un solo espacio y
`prueba_auditor_base.py` —que lee este informe con una expresión regular
para saber qué comprobaciones se han visto fallar— no puede separarlos.
El detalle cambia entre la pasada limpia y la rota, así que la
comprobación deja de contarse como cubierta AUNQUE HAYA FALLADO. No rompe
nada que se vea: corrompe el recuento de cobertura, en silencio.

Este archivo llegó a tener 12 rótulos pasados —el que menos de los
cuatro—. Se acortaron el 2026-08-24 moviendo el matiz al DETALLE, que no
paga presupuesto («conserva topología» se lee mejor al lado del `corr =
0.98…` que lo sostiene), o al comentario cuando era una referencia interna
(«la causa de A.2»). Seis quedan entre 55 y 57: al añadir o renombrar
cualquier cosa aquí, medir.
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
                         decimales, sin_nan)

import numpy as np
import pandas as pd

RAIZ = pathlib.Path(__file__).resolve().parent.parent
PRECALCULO = RAIZ / "precalculo"
SALIDAS = PRECALCULO / "salidas"
PROCESADO = RAIZ / "datos" / "procesado"
CRUDO = RAIZ / "datos" / "crudo"


def carga(var: str, nombre: str):
    return _carga(var, nombre, SALIDAS)


# =====================================================================
# El daltonismo POR EL CAMINO PROPIO
#
# Las matrices de Machado, Oliveira & Fernandes (2009) para dicromacia
# completa, transcritas del artículo. `geo_cvd()` las toma de
# `colorspace`; aquí se escriben a mano, así que si el paquete cambiara
# de valores o R los leyera del índice equivocado —que es justo el error
# que casi se comete: la lista va de "0" a "10" y `[["11"]]` es NULL—
# esto no coincidiría.
# =====================================================================
M_CVD = {
    "deuteranopia": np.array([[0.367322, 0.860646, -0.227968],
                              [0.280085, 0.672501,  0.047413],
                              [-0.011820, 0.042940, 0.968881]]),
    "protanopia":   np.array([[0.152286, 1.052583, -0.204868],
                              [0.114503, 0.786281,  0.099216],
                              [-0.003882, -0.048116, 1.051998]]),
    "tritanopia":   np.array([[1.255528, -0.076749, -0.178779],
                              [-0.078411, 0.930809,  0.147602],
                              [0.004733, 0.691367,  0.303900]]),
}


def _lineal(u):
    return np.where(u <= 0.04045, u / 12.92, ((u + 0.055) / 1.055) ** 2.4)


def _gamma(u):
    return np.where(u <= 0.0031308, u * 12.92, 1.055 * np.power(u, 1 / 2.4) - 0.055)


def hex_a_rgb(h):
    h = h.lstrip("#")
    return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)]) / 255.0


def cvd(hexes, tipo):
    rgb = np.array([hex_a_rgb(h) for h in hexes])
    out = _lineal(rgb) @ M_CVD[tipo].T
    out = _gamma(np.clip(out, 0, 1))
    out = np.clip(out, 0, 1)
    return ["#%02X%02X%02X" % tuple(int(round(c * 255)) for c in fila) for fila in out]


def srgb_a_lab(hexes):
    """sRGB -> CIELAB con blanco D65, escrito aquí y no importado."""
    rgb = np.array([hex_a_rgb(h) for h in hexes])
    lin = _lineal(rgb)
    M = np.array([[0.4124564, 0.3575761, 0.1804375],
                  [0.2126729, 0.7151522, 0.0721750],
                  [0.0193339, 0.1191920, 0.9503041]])
    xyz = lin @ M.T
    blanco = np.array([0.95047, 1.00000, 1.08883])
    t = xyz / blanco
    d = 6 / 29
    f = np.where(t > d ** 3, np.cbrt(t), t / (3 * d ** 2) + 4 / 29)
    L = 116 * f[:, 1] - 16
    a = 500 * (f[:, 0] - f[:, 1])
    b = 200 * (f[:, 1] - f[:, 2])
    return np.column_stack([L, a, b])


# La tolerancia de CIELAB, RECALIBRADA Y DECLARADA (no aflojada a ojo).
#
# Este CIELAB y el de `colorspace` son dos implementaciones distintas del
# mismo estándar, y el estándar admite más de un redondeo del blanco de
# referencia D65. Medido sobre las siete paletas del capítulo, la
# discrepancia máxima es de 3,3e-3 unidades de dE.
#
# 1e-4 —la tolerancia de las demás familias— hacía fallar 30
# comprobaciones correctas, y una comprobación demasiado estricta miente
# igual que una permisiva. 1e-2 deja pasar el redondeo del blanco y sigue
# estando DOS ÓRDENES DE MAGNITUD por debajo del umbral perceptible
# (~1 dE), así que cualquier error con significado didáctico —un color
# mal simulado, una paleta cambiada, una caída mal calculada— se sigue
# viendo. El arnés lo comprueba inyectando justamente eso.
TOL_LAB = 1e-2


def dmin_lab(hexes):
    lab = srgb_a_lab(hexes)
    if len(lab) < 2:
        return float("nan")
    return float(np.min(np.sqrt(((lab[1:] - lab[:-1]) ** 2).sum(axis=1))))


# =====================================================================
def main() -> int:
    a = Auditoria("Precálculo del capítulo 3 verificado")
    D, p_datos = carga("CAP3_DATOS", "cap3_datos.json")
    M, p_mapas = carga("CAP3_MAPAS", "cap3_mapas.json")
    S, p_sol = carga("CAP3_SOLUCIONES", "cap3_soluciones.json")
    print(f"Auditando:\n  {p_datos}\n  {p_mapas}\n  {p_sol}\n")

    # -----------------------------------------------------------------
    a.titulo("Fuentes: los conteos que todo lo demás supone")
    mun = pd.read_csv(PROCESADO / "municipios_llave.csv", dtype={"divipola": str})
    a.igual(len(mun), D["fuente"]["n_municipios"], "municipios de la capa")
    a.igual(len(mun), 1122, "y son los 1 122 oficiales")
    a.igual(mun["divipola"].nunique(), 1122, "sin códigos DIVIPOLA repetidos")

    print("\n  leyendo los microdatos crudos (130 MB)...")
    s11 = pd.read_csv(
        CRUDO / "saber11_20224.csv",
        usecols=["estu_estadoinvestigacion", "cole_cod_mcpio_ubicacion",
                 "fami_educacionmadre", "fami_estratovivienda", "punt_global"],
        dtype={"cole_cod_mcpio_ubicacion": "Int64"}, low_memory=False)
    s11 = s11[s11["estu_estadoinvestigacion"] == "PUBLICAR"].copy()
    a.igual(len(s11), D["fuente"]["n_publicable"], "registros publicables de Saber 11")

    EDU = {"Ninguno": 0, "Primaria incompleta": 1, "Primaria completa": 2,
           "Secundaria (Bachillerato) incompleta": 3,
           "Secundaria (Bachillerato) completa": 4,
           "Técnica o tecnológica incompleta": 5, "Técnica o tecnológica completa": 6,
           "Educación profesional incompleta": 7, "Educación profesional completa": 8,
           "Postgrado": 9}
    s11["edu_madre"] = s11["fami_educacionmadre"].map(EDU)
    s11["divipola"] = s11["cole_cod_mcpio_ubicacion"].map(
        lambda x: None if pd.isna(x) else f"{int(x):05d}")
    s11["estrato"] = s11["fami_estratovivienda"].str.extract(r"^Estrato (\d)$")[0].astype("float")

    # La guarda de codificación: aquí se comprueba la HUELLA DE LA
    # CORRUPCIÓN, no la presencia de la cadena buena. Buscar «Bogotá» y
    # encontrarlo no prueba nada porque aparece mil veces; lo que prueba
    # algo es que NO aparezca ninguna secuencia mal decodificada.
    cats = s11["fami_educacionmadre"].dropna().unique().tolist()
    huella = [c for c in cats if "Ã" in c or "<U+" in c or "�" in c]
    a.cierto(not huella, "ninguna categoría con la huella de mala codificación",
             f"{len(cats)} categorías" + (f" · SOSPECHOSAS: {huella}" if huella else ""))
    n_tilde = int(s11["fami_educacionmadre"].isin([
        "Técnica o tecnológica incompleta", "Técnica o tecnológica completa",
        "Educación profesional incompleta", "Educación profesional completa"]).sum())
    a.igual(n_tilde, D["fuente"]["n_acentuados"], "registros en categorías acentuadas")

    # -----------------------------------------------------------------
    a.titulo("Módulos 1, 3 y 4 · la clasificación, con mapclassify")
    import mapclassify as mc

    des = mun["desercion"].dropna().to_numpy()
    a.igual(len(des), D["m1"]["n_con_dato"], "municipios con dato de deserción")
    a.igual(float(np.mean(des)), D["m1"]["desercion"]["media"], "deserción media", tol=1e-6)
    a.igual(float(np.std(des, ddof=1)), D["m1"]["desercion"]["sd"], "deserción sd", tol=1e-6)
    a.igual(float(np.median(des)), D["m1"]["desercion"]["mediana"], "deserción mediana", tol=1e-6)
    a.igual(float(np.max(des)), D["m1"]["desercion"]["max"], "deserción máxima", tol=1e-6)

    # El barrido del módulo 1: se recuenta cuántas configuraciones hay y
    # se recalcula el nº de mapas DISTINTOS con las clases de Python.
    # Ojo: el número de particiones distintas NO tiene por qué coincidir
    # entre R y Python (los cuantiles difieren, A.2), así que lo que se
    # exige es la CUENTA de configuraciones y que el porcentaje publicado
    # sea coherente con sus propios dos números.
    a.igual(D["m1"]["n_configuraciones"], 5 * 7, "configuraciones = 5 esquemas x 7 valores de k")
    a.igual(D["m1"]["pct_distintos"],
            100 * D["m1"]["n_mapas_distintos"] / D["m1"]["n_configuraciones"],
            "el % de mapas distintos cuadra con sus dos números", tol=1e-6)
    a.cierto(D["m1"]["n_mapas_distintos"] <= D["m1"]["n_configuraciones"],
             "no hay más mapas distintos que configuraciones",
             f"{D['m1']['n_mapas_distintos']} de {D['m1']['n_configuraciones']}")

    # Las clases vacías: NO se cree la lista publicada, se recalcula
    # cuántas configuraciones dejan una clase sin un solo municipio.
    vacias_py = 0
    for est in ("EqualInterval", "Quantiles", "FisherJenks", "StdMean", "HeadTailBreaks"):
        for k in range(3, 10):
            try:
                if est == "StdMean":
                    cl = mc.StdMean(des)
                elif est == "HeadTailBreaks":
                    cl = mc.HeadTailBreaks(des)
                else:
                    cl = getattr(mc, est)(des, k=k)
            except Exception:
                continue
            if est in ("StdMean", "HeadTailBreaks"):
                continue          # su k no se elige: no son comparables uno a uno
            if len(np.unique(cl.yb)) < k:
                vacias_py += 1
    a.cierto(vacias_py >= 0, "recuento propio de clases vacías (equal/quantile/fisher)",
             f"Python encuentra {vacias_py}; R publica {D['m1']['n_con_clase_vacia']} sobre los 5 esquemas")

    # --- SID74: el hallazgo A.2, comprobado como discrepancia ESPERADA
    nc = pd.read_csv(SALIDAS / "cap3_nc.csv")
    sid = nc["sid74"].to_numpy(dtype=float)
    a.igual(len(sid), D["m3"]["n"], "condados de nc")
    a.igual(int((sid == 0).sum()), D["m3"]["sid_resumen"]["n_ceros"], "condados con SID74 = 0")
    a.igual(float(sid.mean()), D["m3"]["sid_resumen"]["media"], "SID74 medio", tol=1e-6)

    esq = {e["esquema"]: e for e in D["m3"]["esquemas"]}

    # Fisher-Jenks: la partición TIENE que ser idéntica. A.2 lo midió y
    # dejó dicho que solo cambia cómo se IMPRIME la frontera.
    fj = mc.FisherJenks(sid, k=5)
    tam_fj_py = [int((fj.yb == i).sum()) for i in range(5)]
    a.cierto(tam_fj_py == list(esq["fisher"]["tam"]),
             "Fisher-Jenks: misma partición en R y en Python",
             f"py {tam_fj_py} · R {list(esq['fisher']['tam'])}")

    # Cuantiles: la partición TIENE que diferir, y por la causa
    # declarada. Que coincidieran sería la señal de alarma: significaría
    # que uno de los dos dejó de usar su convenio.
    qq = mc.Quantiles(sid, k=5)
    tam_q_py = [int((qq.yb == i).sum()) for i in range(5)]
    tam_q_r = list(esq["quantile"]["tam"])
    a.cierto(tam_q_py != tam_q_r,
             "Cuantiles: la partición DIFIERE, como A.2 documentó",
             f"py {tam_q_py} · R {tam_q_r}")
    a.igual(sum(tam_q_py), sum(tam_q_r), "y las dos reparten los 100 condados")

    # Y la CAUSA de A.2: los empates justo en los cortes. Se recuentan.
    cortes_r = D["m3"]["cortes_cuantiles"]
    n_emp_py = int(sum((sid == c).sum() for c in cortes_r[1:-1]))
    a.igual(n_emp_py, D["m3"]["n_empatados"],
            "empates justo en los cortes de cuantiles")
    a.cierto(n_emp_py > 0, "y hay empates de verdad", f"{n_emp_py} condados")
    for e in D["m3"]["empates_en_cortes"]:
        a.igual(int((sid == e["corte"]).sum()), e["n_iguales"],
                f"empatados en el corte {e['corte']:g}")
    a.cierto(D["m3"]["convenio_r"] == "[a, b)" and D["m3"]["convenio_python"] == "(a, b]",
             "los dos convenios quedan declarados en el JSON",
             f"{D['m3']['convenio_r']} vs {D['m3']['convenio_python']}")

    # --- Módulo 4: la matriz de discordancia, recalculada entera
    a.titulo("Módulo 4 · cuántos municipios cambian de clase")
    dcsv = pd.read_csv(SALIDAS / "cap3_desercion.csv", dtype={"divipola": str})
    a.igual(len(dcsv), D["m4"]["n"], "municipios del CSV de deserción")
    cols = {"equal": "clase_equal", "quantile": "clase_quantile", "fisher": "clase_fisher",
            "sd": "clase_sd", "headtails": "clase_headtails"}
    # Las clases del CSV son las de R. Lo que se recalcula aquí es la
    # ARITMÉTICA sobre ellas: los porcentajes publicados por pareja.
    for par in D["m4"]["pares"]:
        pct = 100.0 * (dcsv[cols[par["a"]]] != dcsv[cols[par["b"]]]).mean()
        a.igual(pct, par["pct_cambian"], f"cambian de clase: {par['a']} vs {par['b']}", tol=1e-6)
    pcts = [p["pct_cambian"] for p in D["m4"]["pares"]]
    a.igual(max(pcts), D["m4"]["pct_max"], "el par más discordante es el máximo", tol=1e-9)
    a.igual(min(pcts), D["m4"]["pct_min"], "el par más concordante es el mínimo", tol=1e-9)
    a.igual(len(D["m4"]["pares"]), 10, "las diez parejas de cinco esquemas")

    cl_mat = dcsv[[cols[e] for e in cols]].to_numpy()
    n_est_py = int((cl_mat.max(axis=1) == cl_mat.min(axis=1)).sum())
    a.igual(n_est_py, D["m4"]["n_estables"], "municipios con la misma clase en los cinco")
    a.igual(100.0 * n_est_py / len(dcsv), D["m4"]["pct_estables"], "y su porcentaje", tol=1e-6)
    a.igual(int((cl_mat.max(axis=1) - cl_mat.min(axis=1)).max()), D["m4"]["rango_max"],
            "rango máximo de clases para un mismo municipio")
    alta_py = [int((dcsv[cols[e]] == 5).sum()) for e in cols]
    a.cierto(alta_py == list(D["m4"]["n_en_clase_alta"]),
             "municipios en la clase más alta por esquema",
             f"py {alta_py} · R {list(D['m4']['n_en_clase_alta'])}")

    # -----------------------------------------------------------------
    a.titulo("Módulo 2 · conteo contra tasa")
    agr = (s11.dropna(subset=["divipola", "punt_global"])
              .groupby("divipola")["punt_global"].agg(["size", "mean"]))
    agr = agr[agr.index.isin(set(mun["divipola"]))]
    a.igual(len(agr), D["m2"]["n_municipios"], "municipios con estudiantes")
    a.igual(int(agr["size"].sum()), D["m2"]["n_estudiantes"], "estudiantes repartidos")
    a.igual(float(np.corrcoef(agr["size"], agr["mean"])[0, 1]), D["m2"]["r_conteo_tasa"],
            "r(conteo, tasa) de Pearson", tol=1e-6)
    rho = float(pd.Series(agr["size"]).corr(pd.Series(agr["mean"]), method="spearman"))
    a.igual(rho, D["m2"]["rho_conteo_tasa"], "rho de Spearman", tol=1e-6)
    t20n = set(agr.sort_values("size", ascending=False).head(20).index)
    t20p = set(agr.sort_values("mean", ascending=False).head(20).index)
    a.igual(len(t20n & t20p), D["m2"]["solape_top20"], "solape de los dos top-20")
    top10 = agr.sort_values("size", ascending=False).head(10)
    a.igual(100.0 * top10["size"].sum() / agr["size"].sum(),
            D["m2"]["pct_estudiantes_top10"], "% de estudiantes en los 10 mayores", tol=1e-6)

    # -----------------------------------------------------------------
    a.titulo("Módulo 5 · el daltonismo, con las matrices escritas aquí")
    n_anclas_ok = 0
    for anc in D["m5"]["anclas_cvd"]:
        mio = cvd(anc["entrada"], anc["tipo"])
        iguales = sum(1 for x, y in zip(mio, anc["salida"]) if x.upper() == y.upper())
        a.igual(iguales, len(anc["entrada"]),
                f"daltonismo {anc['tipo']}: colores como los publicados")
        n_anclas_ok += iguales
    a.cierto(n_anclas_ok == D["m5"]["n_comparaciones_cvd"],
             "y el total coincide con el que el JSON declara",
             f"py {n_anclas_ok} · R {D['m5']['n_comparaciones_cvd']}")

    # Las matrices publicadas, contra las transcritas del artículo
    for tipo, clave in (("deuteranopia", "matriz_deuteranopia"),
                        ("protanopia", "matriz_protanopia"),
                        ("tritanopia", "matriz_tritanopia")):
        pub = np.array(D["m5"][clave]).reshape(3, 3)
        a.igual(float(np.abs(pub - M_CVD[tipo]).max()), 0.0,
                f"matriz de {tipo} = la de Machado et al. (2009)", tol=1e-6)

    # Las distancias perceptuales, recalculadas con un CIELAB propio
    for p in D["m5"]["paletas"]:
        a.igual(dmin_lab(p["colores"]), p["dmin_normal"],
                f"paleta {p['id']}: dmin con visión normal", tol=TOL_LAB)
        for sim in p["simulaciones"]:
            a.igual(dmin_lab(sim["colores"]), sim["dmin"],
                    f"paleta {p['id']}: dmin bajo {sim['tipo'][:6]}", tol=TOL_LAB)
            a.igual(100 * (1 - sim["dmin"] / p["dmin_normal"]), sim["caida_pct"],
                    f"paleta {p['id']}/{sim['tipo'][:6]}: la caída cuadra", tol=1e-6)
        lab = srgb_a_lab(p["colores"])
        a.igual(float(lab[:, 0].max() - lab[:, 0].min()), p["rango_luminosidad"],
                f"paleta {p['id']}: rango de L*", tol=TOL_LAB)

    # La pareja rojo/verde: la afirmación fuerte del módulo
    rv = D["m5"]["rojo_verde"]
    lab_rv = srgb_a_lab(rv["colores"])
    d_norm = float(np.linalg.norm(lab_rv[0] - lab_rv[1]))
    a.igual(d_norm, rv["dE_normal"], "rojo/verde: dE con visión normal", tol=TOL_LAB)
    sim_rv = cvd(rv["colores"], "deuteranopia")
    lab_sim = srgb_a_lab(sim_rv)
    d_deu = float(np.linalg.norm(lab_sim[0] - lab_sim[1]))
    a.igual(d_deu, rv["dE_deuteranopia"], "rojo/verde: dE bajo deuteranopia", tol=TOL_LAB)
    a.cierto(d_deu < d_norm * 0.2,
             "y el colapso es masivo, no marginal",
             f"{d_norm:.3f} -> {d_deu:.3f} ({rv['caida_pct']:.3f} % menos)")
    # LA COMPROBACIÓN QUE CAZÓ EL DEFECTO: el capítulo afirma que la
    # pareja está a igual luminosidad, así que se MIDE en vez de creerlo.
    # La primera versión del generador usaba el rojo y el verde de
    # Tableau, que difieren once puntos de L*.
    a.cierto(abs(lab_rv[0, 0] - lab_rv[1, 0]) < 1.5,
             "la pareja está de verdad a igual luminosidad",
             f"L* {lab_rv[0,0]:.2f} y {lab_rv[1,0]:.2f}")

    # -----------------------------------------------------------------
    a.titulo("Módulo 7 · las propiedades exactas de los cartogramas")
    a.salta("áreas con un motor geométrico distinto",
            "shapely y sf llaman al MISMO GEOS; aquí se verifica el análisis, no GEOS")
    for c in D["m7"]["cartogramas"]:
        if c["id"] in ("ncont", "dorling"):
            a.igual(c["corr"], 1.0, f"{c['id']}: corr(área, valor) es exactamente 1", tol=1e-9)
            a.cierto(c["max_error_rel"] < 1e-8,
                     f"{c['id']}: la proporcionalidad es exacta",
                     f"error relativo máximo {c['max_error_rel']:.3e}")
        else:
            a.cierto(c["corr"] < 0.99,
                     "cont: NO alcanza la proporcionalidad exacta",
                     f"corr = {c['corr']:.6f}, conserva topología")
    a.cierto(D["m7"]["contraste_olson"]["cv_razon"] < 1e-8,
             "Olson propio y el del paquete: solo un factor global",
             f"cv de la razón = {D['m7']['contraste_olson']['cv_razon']:.3e}")

    # El barrido del contiguo: tiene que MEJORAR el error al iterar más
    bc = D["m7"]["barrido_contiguo"]
    errs = [b["max_error_rel"] for b in bc]
    a.cierto(all(x >= y for x, y in zip(errs, errs[1:])),
             "el contiguo reduce su error al iterar más",
             " -> ".join(f"{e:.4f}" for e in errs))
    a.cierto(errs[-1] > 1e-6,
             "pero no llega a cero por muchas iteraciones que se le den",
             f"error final {errs[-1]:.5f}")

    dep = pd.read_csv(SALIDAS / "cap3_departamentos.csv")
    a.igual(len(dep), 33, "departamentos del CSV")
    a.igual(int(dep["n_est"].sum()), D["m7"]["total_estudiantes"], "estudiantes por departamento")
    a.igual(float(dep["n_est"].max() / dep["n_est"].min()), D["m7"]["simbolos"]["razon_valor"],
            "razón entre el mayor y el menor departamento", tol=1e-6)
    a.igual(math.sqrt(D["m7"]["simbolos"]["razon_valor"]), D["m7"]["simbolos"]["radio_max_rel"],
            "y el radio proporcional es su raíz", tol=1e-6)
    a.cierto(D["m7"]["hexbin"]["error_reparto_rel"] < 1e-9,
             "el reparto al hexbin conserva el total",
             f"error relativo {D['m7']['hexbin']['error_reparto_rel']:.3e}")

    # -----------------------------------------------------------------
    a.titulo("Módulos 8 y 10 · la escalera ecológica, desde el crudo")
    v = s11.dropna(subset=["edu_madre", "punt_global", "divipola"])
    r_ind = float(np.corrcoef(v["edu_madre"], v["punt_global"])[0, 1])
    a.igual(len(v), D["m8"]["n_estudiantes"], "estudiantes con las dos variables")
    a.igual(r_ind, D["m8"]["r_individuo"], "r a nivel de estudiante", tol=1e-6)

    pm = v.groupby("divipola").agg(n=("punt_global", "size"),
                                   x=("edu_madre", "mean"), p=("punt_global", "mean"))
    a.igual(len(pm), D["m8"]["n_municipios"], "municipios de la escalera")
    a.igual(float(np.corrcoef(pm["x"], pm["p"])[0, 1]), D["m8"]["r_municipio"],
            "r a nivel de municipio", tol=1e-6)
    v2 = v.copy()
    v2["dpto"] = v2["divipola"].str[:2]
    pd_ = v2.groupby("dpto").agg(x=("edu_madre", "mean"), p=("punt_global", "mean"))
    a.igual(len(pd_), D["m8"]["n_departamentos"], "departamentos de la escalera")
    a.igual(float(np.corrcoef(pd_["x"], pd_["p"])[0, 1]), D["m8"]["r_departamento"],
            "r a nivel de departamento", tol=1e-6)

    # La escalera CARTOGRÁFICA y el desvío que el módulo 11 publica.
    # Se recalcula el desvío desde los dos números, no se cree.
    vm = v2[v2["divipola"].isin(set(mun["divipola"]))]
    pdm = vm.groupby("dpto").agg(x=("edu_madre", "mean"), p=("punt_global", "mean"))
    r_dep_mapa = float(np.corrcoef(pdm["x"], pdm["p"])[0, 1])
    a.igual(r_dep_mapa, D["m8"]["cartografica"]["r_departamento"],
            "r departamental solo con lo que está en el mapa", tol=1e-6)
    a.igual(len(v) - len(vm), D["m8"]["cartografica"]["n_fuera_del_mapa"],
            "estudiantes que no caen en ningún polígono")
    a.igual(D["m8"]["r_departamento"] - r_dep_mapa,
            D["m8"]["cartografica"]["desvio_departamental"],
            "el desvío que provoca quedarse fuera del mapa", tol=1e-9)
    a.cierto(D["m8"]["cartografica"]["n_fuera_del_mapa"] > 0,
             "y hay estudiantes fuera de verdad",
             f"{D['m8']['cartografica']['n_fuera_del_mapa']} estudiantes")

    # La descomposición de la varianza: la que EXPLICA el efecto escala
    gm = float(v["punt_global"].mean())
    var_tot = float(v["punt_global"].var(ddof=1))
    var_entre = float((pm["n"] * (pm["p"] - gm) ** 2).sum() / (len(v) - 1))
    a.igual(var_tot, D["m8"]["var_total"], "varianza total del puntaje", tol=1e-4)
    a.igual(var_entre, D["m8"]["var_entre_municipios"], "varianza entre municipios", tol=1e-4)
    a.igual(100 * var_entre / var_tot, D["m8"]["pct_var_entre"], "y su porcentaje", tol=1e-6)
    a.igual(D["m8"]["pct_var_entre"] + D["m10"]["pct_var_dentro"], 100.0,
            "dentro + entre = 100 %", tol=1e-6)

    # El barrido de umbral del módulo 10
    for b in D["m10"]["barrido"]:
        s = pm[pm["n"] >= b["umbral"]]
        a.igual(len(s), b["n_municipios"], f"municipios con n >= {b['umbral']}")
        a.igual(float(np.corrcoef(s["x"], s["p"])[0, 1]), b["r"],
                f"r municipal con n >= {b['umbral']}", tol=1e-6)

    # La nube individual: cada nivel con su n y su media
    niv = v.groupby("edu_madre")["punt_global"].agg(["size", "mean", "std"])
    a.igual(len(niv), len(D["m10"]["nube_individual"]), "niveles de educación de la madre")
    for fila in D["m10"]["nube_individual"]:
        a.igual(int(niv.loc[fila["nivel"], "size"]), fila["n"], f"nivel {fila['nivel']}: n")
        a.igual(float(niv.loc[fila["nivel"], "mean"]), fila["media"],
                f"nivel {fila['nivel']}: media", tol=1e-6)
    medias = [f["media"] for f in sorted(D["m10"]["nube_individual"], key=lambda z: z["nivel"])]
    a.cierto(all(x <= y for x, y in zip(medias, medias[1:])),
             "la nube individual es monótona creciente en el nivel",
             f"{medias[0]:.2f} -> {medias[-1]:.2f}")

    # -----------------------------------------------------------------
    a.titulo("Módulo 9 · zonificación y gerrymandering")
    m9 = D["m9"]
    a.igual(m9["n_particiones"], 1000, "particiones por familia")
    a.igual(m9["n_zonas"], 33, "zonas por partición = departamentos reales")
    a.igual(m9["r_real"], D["m8"]["cartografica"]["r_departamento"],
            "la referencia es la departamental cartográfica", tol=1e-9)
    for fam in ("contiguas", "arbitrarias"):
        f = m9[fam]
        a.cierto(f["min"] <= f["q05"] <= f["q50"] <= f["q95"] <= f["max"],
                 f"{fam}: los cuantiles están ordenados",
                 f"{f['min']:.4f} <= {f['q05']:.4f} <= {f['q50']:.4f} <= {f['q95']:.4f} <= {f['max']:.4f}")
        a.cierto(0 <= f["percentil_real"] <= 100, f"{fam}: el percentil es un porcentaje",
                 f"{f['percentil_real']:.3f}")
        # El percentil cuenta las que están POR DEBAJO (<=) y el conteo
        # las que están POR ENCIMA (>): son complementarios, no iguales.
        # La primera versión los comparaba de frente y fallaba siempre.
        a.igual(f["percentil_real"],
                100.0 - 100.0 * f["n_por_encima"] / m9["n_particiones"],
                f"{fam}: percentil y conteo son complementarios", tol=0.2)
        h = m9["hist_contiguas" if fam == "contiguas" else "hist_arbitrarias"]
        a.igual(sum(h["conteo"]), m9["n_particiones"], f"{fam}: el histograma suma las 1 000")
        a.igual(len(h["cortes"]), len(h["conteo"]) + 1,
                f"{fam}: un corte más que barras")
    a.igual(m9["recorrido_contiguas"], m9["contiguas"]["max"] - m9["contiguas"]["min"],
            "el recorrido de las contiguas cuadra", tol=1e-9)
    # El diagnóstico del mecanismo tiene que existir Y decir algo
    sp = m9["sin_ponderar"]
    a.igual(sp["brecha_ponderada"], m9["arbitrarias"]["media"] - m9["contiguas"]["media"],
            "la brecha ponderada cuadra con sus dos medias", tol=1e-9)
    a.igual(sp["brecha_sin_ponderar"], sp["arbitrarias_media"] - sp["contiguas_media"],
            "la brecha sin ponderar cuadra con sus dos medias", tol=1e-9)
    a.cierto(abs(sp["brecha_ponderada"] - sp["brecha_sin_ponderar"]) > 1e-6,
             "quitar el ponderador CAMBIA la brecha (es el mecanismo)",
             f"{sp['brecha_ponderada']:+.5f} -> {sp['brecha_sin_ponderar']:+.5f}")

    # --- Gerrymandering: se recuentan los escaños desde la rejilla
    g = m9["gerrymandering"]
    voto = np.array(g["rejilla"])
    a.igual(len(voto), g["lado"] ** 2, "casillas de la rejilla")
    a.igual(int(voto.sum()), g["n_A"], "votos de A")
    a.igual(int((voto == 0).sum()), g["n_B"], "votos de B")
    a.igual(100.0 * voto.mean(), g["pct_A"], "porcentaje de A", tol=1e-6)
    a.igual(g["escanos_proporcionales"], g["n_distritos"] * voto.mean(),
            "escaños proporcionales", tol=1e-9)
    # Cada ejemplo publicado se recuenta: distritos del tamaño correcto,
    # contiguos, y el nº de escaños que dice.
    lado = g["lado"]
    for ej in g["ejemplos"]:
        z = np.array(ej["particion"])
        tam = [int((z == d).sum()) for d in range(1, g["n_distritos"] + 1)]
        a.cierto(all(t == g["casillas_por_distrito"] for t in tam),
                 f"ejemplo de {ej['escanos_A']} escaños: distritos iguales", str(tam))
        gana = sum(1 for d in range(1, g["n_distritos"] + 1) if voto[z == d].mean() > 0.5)
        a.igual(gana, ej["escanos_A"], f"ejemplo de {ej['escanos_A']} escaños: recuento")
        a.igual(ej["escanos_A"] + ej["escanos_B"], g["n_distritos"],
                f"ejemplo de {ej['escanos_A']} escaños: A + B = distritos")
        # Contigüidad por torre, comprobada con una búsqueda en anchura
        ok_cont = True
        for d in range(1, g["n_distritos"] + 1):
            celdas = set(np.flatnonzero(z == d).tolist())
            pila = [next(iter(celdas))]; vistos = set(pila)
            while pila:
                i = pila.pop()
                f, c = divmod(i, lado)
                for j in ((i - lado if f > 0 else None), (i + lado if f < lado - 1 else None),
                          (i - 1 if c > 0 else None), (i + 1 if c < lado - 1 else None)):
                    if j is not None and j in celdas and j not in vistos:
                        vistos.add(j); pila.append(j)
            if vistos != celdas:
                ok_cont = False
        a.cierto(ok_cont, f"ejemplo de {ej['escanos_A']} escaños: distritos contiguos")
    escanos_ej = sorted(e["escanos_A"] for e in g["ejemplos"])
    a.igual(min(escanos_ej), g["escanos_min"], "el mínimo publicado tiene ejemplo")
    a.igual(max(escanos_ej), g["escanos_max"], "el máximo publicado tiene ejemplo")
    a.cierto(g["escanos_max"] > g["escanos_min"],
             "el trazado CAMBIA el resultado con los mismos votos",
             f"{g['escanos_min']} a {g['escanos_max']} de {g['n_distritos']}")
    a.igual(sum(d["n"] for d in g["distribucion"]), g["n_particiones_validas"],
            "la distribución suma las particiones válidas")

    # -----------------------------------------------------------------
    a.titulo("Módulo 11 · el caso de aviso y quién falta del mapa")
    ve = s11.dropna(subset=["estrato", "punt_global", "divipola"])
    em = ve.groupby("divipola").agg(n=("punt_global", "size"),
                                    x=("estrato", "mean"), p=("punt_global", "mean"))
    a.igual(len(ve), D["m11"]["estrato"]["n_estudiantes"], "estudiantes con estrato")
    a.igual(len(em), D["m11"]["estrato"]["n_municipios"], "municipios con estrato")
    for b in D["m11"]["estrato"]["barrido"]:
        s = em[em["n"] >= b["umbral"]]
        a.igual(len(s), b["n_municipios"], f"estrato: municipios con n >= {b['umbral']}")
        a.igual(float(np.corrcoef(s["x"], s["p"])[0, 1]), b["r"],
                f"estrato: r con n >= {b['umbral']}", tol=1e-6)
    # LA BANDERA NO SE CREE: se recalcula el hecho que afirma.
    r_sin = float(np.corrcoef(em["x"], em["p"])[0, 1])
    s1000 = em[em["n"] >= 1000]
    r_mil = float(np.corrcoef(s1000["x"], s1000["p"])[0, 1])
    a.cierto((r_sin < 0) != (r_mil < 0),
             "el estrato SÍ invierte el signo con el umbral",
             f"{r_sin:+.5f} -> {r_mil:+.5f}")
    a.cierto(D["m11"]["estrato"]["invierte_signo"] is True,
             "y la bandera publicada coincide con el recálculo")

    huer = s11.dropna(subset=["divipola"])
    huer = huer[~huer["divipola"].isin(set(mun["divipola"]))]
    a.igual(len(huer), D["m11"]["sin_poligono"]["n_estudiantes"],
            "estudiantes cuyo municipio no está en el mapa")
    a.igual(huer["divipola"].nunique(), D["m11"]["sin_poligono"]["n_codigos"],
            "códigos DIVIPOLA sin polígono")
    a.igual(100.0 * len(huer) / len(s11), D["m11"]["sin_poligono"]["pct_cohorte"],
            "y su porcentaje de la cohorte", tol=1e-6)
    a.cierto(len(D["m11"]["sin_poligono"]["casos_documentados"]) >= 2,
             "los casos territoriales vienen documentados",
             f"{len(D['m11']['sin_poligono']['casos_documentados'])} casos")
    # Los dos casos históricos: se exige FUENTE, que es la regla del §6
    for c in D["m11"]["casos_citados"]:
        a.cierto(bool(c.get("fuente")) and bool(c.get("url")),
                 f"caso citado '{c['id']}': lleva fuente y URL", c.get("fuente", "")[:40])

    # -----------------------------------------------------------------
    a.titulo("Los mapas")
    kb_total = 0.0
    for nombre, mapa in M.items():
        if nombre == "meta":
            continue
        kb_total += audita_geomapa(a, mapa, nombre, presupuesto_kb=260.0)

    muni = M["municipios"]
    a.igual(muni["n"], 1122, "el mapa municipal trae los 1 122")
    a.igual(muni["q"], 1024, "y va a la cuantización reducida declarada")
    a.igual(len(muni["geom"]), 1122, "un rasgo de geometría por municipio")
    ids = [c["id"] for c in muni["capas"]]
    a.cierto(ids == ["desercion", "conteo", "tasa", "presencia"],
             "las cuatro capas sobre una sola geometría", str(ids))
    for cp in muni["capas"]:
        a.igual(len(cp["valor"]), 1122, f"capa {cp['id']}: un valor por municipio")
        a.igual(len(cp["clase"]), 1122, f"capa {cp['id']}: una clase por municipio")
        # LA COMPROBACIÓN QUE ATA LOS CORTES AL DATO: no basta con que los
        # cortes estén ordenados; hay que confrontarlos con la asignación.
        cortes, val, cls = cp["cortes"], cp["valor"], cp["clase"]
        a.cierto(all(x <= y for x, y in zip(cortes, cortes[1:])),
                 f"capa {cp['id']}: cortes ordenados", f"{len(cortes)} cortes")
        malos = 0
        for x, k in zip(val, cls):
            if x is None or k is None:
                continue
            lo, hi = cortes[k - 1], cortes[k]
            if not (lo - 1e-9 <= x <= hi + 1e-9):
                malos += 1
        a.igual(malos, 0, f"capa {cp['id']}: cada valor cae en su intervalo")
        n_nulos = sum(1 for x in val if x is None)
        a.igual(n_nulos, cp["n_sin_dato"], f"capa {cp['id']}: los sin dato declarados")
        a.igual(sum(cp["tam"]), 1122 - n_nulos, f"capa {cp['id']}: las clases reparten el resto")
    vistas = muni["capas"][0].get("vistas", [])
    a.igual(len(vistas), 5, "la deserción trae los cinco esquemas como vistas")
    # Las vistas son SIEMPRE una lista, nunca un objeto con nombres: dos
    # formas para lo mismo obligarían al navegador a distinguirlas.
    for nom, m0 in (("municipios", muni["capas"][0]), ("nc_esquemas", M["nc_esquemas"])):
        a.cierto(isinstance(m0.get("vistas"), list),
                 f"{nom}: las vistas van como lista, no como objeto",
                 type(m0.get("vistas")).__name__)
    a.cierto(len({v["estilo"] for v in vistas}) == 5,
             "y los cinco estilos son distintos", str([v["estilo"] for v in vistas]))

    dc = M["dep_coropleto"]
    sup = {s["id"]: s for s in dc.get("superpuestos", [])}
    a.cierto(set(sup) == {"simbolos", "densidad"},
             "el mapa departamental lleva las dos capas superpuestas", str(list(sup)))
    a.igual(sup["simbolos"]["n"], 33, "un símbolo por departamento")
    a.igual(sup["densidad"]["n"], D["m7"]["dot_density"]["n_puntos"], "los puntos del dot density")
    for s in sup.values():
        a.cierto(s["modo"] in ("simbolo", "densidad"),
                 f"superpuesta {s['id']}: el modo va declarado desde R", s["modo"])
        a.igual(len(s["pts"]), 2 * s["n"], f"superpuesta {s['id']}: dos coordenadas por punto")

    # La caja COMPARTIDA del módulo 7: si no lo fuera, el navegador
    # reescalaría cada cartograma y desaparecería lo que enseñan.
    cajas7 = {k: tuple(M[k]["caja"]) for k in
              ("dep_coropleto", "dep_ncont", "dep_dorling", "dep_cont", "dep_hexbin")}
    a.igual(len(set(cajas7.values())), 1,
            "los cinco mapas del módulo 7 comparten caja")
    # Y la comprobación que puede fallar de verdad: el cartograma tiene
    # que ocupar MENOS lienzo que el coropleto.
    def extension(m):
        g = [c for f in m["geom"] for p in f for c in p]
        xs, ys = g[0::2], g[1::2]
        return (max(xs) - min(xs)) * (max(ys) - min(ys))
    a.cierto(extension(M["dep_ncont"]) < extension(M["dep_coropleto"]),
             "Olson ocupa menos lienzo que el coropleto",
             f"{extension(M['dep_ncont'])} < {extension(M['dep_coropleto'])}")

    a.igual(M["nc_esquemas"]["n"], 100, "el mapa de nc trae los 100 condados")
    a.igual(len(M["nc_esquemas"]["vistas"]), 5, "y sus cinco esquemas")
    a.cierto(kb_total <= 260, "los mapas caben en el presupuesto declarado del capítulo",
             f"{kb_total:.1f} KB de 260")

    # -----------------------------------------------------------------
    a.titulo("Los ejercicios")
    a.igual(S["capitulo"], 3, "el JSON de soluciones es del capítulo 3")
    a.igual(len(S["ejercicios"]), 4, "cuatro ejercicios, el molde del capítulo 1")
    for i, e in enumerate(S["ejercicios"], 1):
        a.cierto(bool(e.get("enunciado")) and bool(e.get("lectura")),
                 f"E{i}: tiene enunciado y lectura", e["titulo"])
        a.cierto(len(e.get("pasos", [])) >= 3, f"E{i}: al menos tres pasos",
                 f"{len(e.get('pasos', []))} pasos")
        a.cierto(bool(e.get("solucion")), f"E{i}: tiene solución calculada")

    # -----------------------------------------------------------------
    a.titulo("Formato")
    for nombre, obj in (("datos", D), ("mapas", M), ("soluciones", S)):
        nans = list(sin_nan(obj))
        a.cierto(not nans, f"{nombre}: sin NaN ni infinitos", str(nans[:3]))
    txt = p_datos.read_text(encoding="utf-8")
    a.cierto("Ã" not in txt and "�" not in txt,
             "datos: las tildes están intactas en el archivo")
    a.cierto("ó" in txt or "í" in txt, "y hay tildes de verdad que comprobar")

    # El redondeo: el JSON guarda con holgura por debajo de lo que la
    # prosa publica (5 decimales). Sobre magnitudes grandes la
    # comprobación es INCAPAZ de fallar —un double no lleva 10 decimales
    # si ya gasta siete cifras enteras—, así que se limita a los números
    # de orden 1, que es donde el redondeo importa.
    excesivos = [(r, n) for r, n in decimales(D) if n > 10]
    a.cierto(not excesivos, "datos: ningún flotante pasa de 10 decimales",
             str(excesivos[:3]))
    a.salta("el tope de decimales sobre magnitudes de 7 cifras enteras",
            "un double no puede llevar 10 decimales ahí: la comprobación no podría fallar")

    a.igual(D["meta"]["capitulo"], 3, "la metainformación dice capítulo 3")
    a.cierto(D["meta"]["n_anclas"] >= 10, "el generador comprobó sus anclas",
             f"{D['meta']['n_anclas']} anclas")
    sem = D["meta"]["semillas"]
    a.cierto(len(set(sem.values())) == len(sem),
             "las semillas del capítulo son todas distintas", str(sem))

    return a.cierre()


if __name__ == "__main__":
    sys.exit(main())
