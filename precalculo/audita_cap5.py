#!/usr/bin/env python3
"""
audita_cap5.py — auditoría independiente del precálculo del capítulo 5 (T3.4b)

Material de Estadística Espacial 2026-II (20929).

NO comprueba que los JSON existan: comprueba que sus NÚMEROS sean ciertos,
por caminos que no pasan por R ni por spatstat.

QUÉ SE REIMPLEMENTA AQUÍ, que es lo que hace que esto sea un control:

  · LA KDE ENTERA. El numerador se calcula por SUMA DIRECTA del núcleo
    gaussiano sobre las coordenadas publicadas, en cada centro de píxel.
    spatstat no hace eso: bina los puntos y convoluciona por FFT. Son dos
    algoritmos distintos que convergen al mismo sitio, y esa es la única
    forma de que el acuerdo signifique algo.
  · LAS TRES CORRECCIONES DE BORDE, con su definición y no con su nombre:
    sin corregir es la suma pelada; la de por defecto divide por e(u), la
    masa de núcleo que cae dentro de la ventana MIRANDO DESDE EL PÍXEL; la
    de Diggle divide por e(x_i), mirando DESDE CADA DATO. Escribir las dos
    por separado es lo que permite comprobar cuál conserva el conteo.
  · EL RIESGO RELATIVO, como cociente de dos KDE recalculadas. Es la
    comprobación más importante del archivo: el generador publicó una vez
    P(privado) creyendo que era P(oficial) —`relrisk` devuelve el SEGUNDO
    nivel del factor— y todo daba verde. Aquí se recalcula P(oficial) por
    definición y se compara con lo publicado, así que esa inversión no
    puede volver a pasar en silencio.
  · `bw.scott`, que tiene fórmula cerrada: sd por eje por n^(-1/6).
  · EL ÍNDICE DE DISPERSIÓN DEL HAWKES, desde los tiempos publicados.

HASTA DÓNDE LLEGA LA INDEPENDENCIA, DECLARADO Y NO INSINUADO
  · TOTAL para la KDE, las tres correcciones, el riesgo relativo,
    `bw.scott`, la identidad de la EMV del Poisson homogéneo, la
    dispersión del Hawkes y toda la aritmética.
  · PARCIAL para e(u): el núcleo se convoluciona con la máscara por FFT,
    que es el mismo ALGORITMO que usa spatstat aunque no la misma
    implementación. Y parcial para las áreas y la pertenencia a la
    ventana: GEOS es el mismo motor de los dos lados.
  · NULA para `bw.diggle`, `bw.ppl` y `bw.CvL`: son criterios de
    validación cruzada con convenios internos de spatstat. Se auditan sus
    PROPIEDADES —que estén dentro de su intervalo de búsqueda, el orden
    entre ellos, la razón publicada— y no sus valores.
  · NULA para `rhohat` y para `kppm`: suavizado y contraste mínimo. Se
    audita lo que SÍ es comprobable —los cuantiles del bulto salen de la
    covariable, la divergencia entre correcciones es aritmética sobre los
    parámetros publicados— y se dice lo que no.
  · NULA para la envolvente: depende del generador de R. Se auditan sus
    propiedades y no sus valores.

Ejecutar con el Python de geo_env:
    "$(python3 -c 'import json;print(json.load(open("precalculo/versiones_py.json"))["ejecutable"])')" \\
        precalculo/audita_cap5.py

LOS RÓTULOS TIENEN PRESUPUESTO: 57 CARACTERES, PREFIJO INCLUIDO. Ver la
cabecera de `audita_cap4.py`: uno de 58 o más queda pegado a su detalle y
el arnés deja de contar esa comprobación como cubierta, en silencio.
"""
from __future__ import annotations

import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from audita_base import (Auditoria, audita_geomapa, carga as _carga,  # noqa: E402
                         decimales, sin_nan)

import numpy as np                      # noqa: E402
import pandas as pd                     # noqa: E402
import geopandas as gpd                 # noqa: E402
from scipy.signal import fftconvolve    # noqa: E402

RAIZ = pathlib.Path(__file__).resolve().parent.parent
PRECALCULO = RAIZ / "precalculo"
SALIDAS = PRECALCULO / "salidas"
PROCESADO = RAIZ / "datos" / "procesado"

# La KDE de este auditor y la de spatstat son dos DISCRETIZACIONES
# distintas de la misma integral —suma directa contra binado y FFT—, así
# que su acuerdo tiene un suelo que no es el redondeo del JSON. Medido: se
# quedan dentro del 2 % en la superficie y dentro del 0,5 % en las
# integrales. La tolerancia es esa y está declarada, no ajustada hasta que
# pase.
TOL_SUP = 2e-2
TOL_MASA = 5e-3

# Las intensidades pequeñas —lambda del orden de 1e-06, los rho de 1e-07—
# NO se pueden publicar con `r10()`: redondea DECIMALES y a esa escala se
# come las cifras. Van con `r6`, seis SIGNIFICATIVAS, que es el convenio
# de la casa (el `r6` del capítulo 4 y su TOL_CURVA nacieron de lo mismo).
# Lo que aquí se recalcula desde las coordenadas tiene todas las cifras,
# así que la comparación no puede exigir más de lo que el JSON publica.
TOL_R6 = 1e-5


def carga(var: str, nombre: str):
    return _carga(var, nombre, SALIDAS)


# =====================================================================
# La KDE, reimplementada
# =====================================================================
def rejilla_de(caja, nx, ny):
    """Los centros de píxel, con el convenio de spatstat: la caja se parte
    en nx por ny celdas iguales y el valor vive en el CENTRO de cada una."""
    dx = (caja[2] - caja[0]) / nx
    dy = (caja[3] - caja[1]) / ny
    xc = caja[0] + (np.arange(nx) + 0.5) * dx
    yc = caja[1] + (np.arange(ny) + 0.5) * dy
    return xc, yc, dx, dy


def nucleo_gauss(dx, dy, sigma, nx, ny):
    """El núcleo gaussiano muestreado en la rejilla, para convolucionar."""
    rx = int(np.ceil(4 * sigma / dx)); ry = int(np.ceil(4 * sigma / dy))
    gx = (np.arange(-rx, rx + 1)) * dx
    gy = (np.arange(-ry, ry + 1)) * dy
    k = np.exp(-(gx[None, :] ** 2 + gy[:, None] ** 2) / (2 * sigma ** 2))
    return k / (2 * np.pi * sigma ** 2)


def kde_directa(px, py, sigma, xc, yc):
    """Suma directa del núcleo sobre los puntos, en cada centro de píxel.

    NO es lo que hace spatstat —que bina y convoluciona por FFT— y ahí
    está la independencia: dos algoritmos distintos para la misma
    integral. Cuesta O(pixeles x puntos), que aquí son 2,5 millones de
    evaluaciones y se hace de una vez con numpy.
    """
    # Se acumula punto a punto en vez de levantar el tensor entero: sobre
    # la ciudad son 2 107 puntos por 27 904 píxeles, que en un solo array
    # son 470 MB. El algoritmo es el mismo —suma directa—, la contabilidad
    # de la memoria no.
    X, Y = np.meshgrid(xc, yc)                       # (ny, nx)
    out = np.zeros_like(X, dtype=float)
    for k in range(len(px)):
        out += np.exp(-((X - px[k]) ** 2 + (Y - py[k]) ** 2) / (2 * sigma ** 2))
    return out / (2 * np.pi * sigma ** 2)


def borde_e(mask, dx, dy, sigma, nx, ny):
    """e(u): la fracción de masa del núcleo que cae DENTRO de la ventana,
    vista desde cada píxel. Es la convolución de la máscara con el núcleo.

    Aquí la independencia es PARCIAL y se declara: el algoritmo es el
    mismo que el de spatstat (convolución), la implementación no.
    """
    k = nucleo_gauss(dx, dy, sigma, nx, ny)
    return fftconvolve(mask.astype(float), k, mode="same") * dx * dy


def masas(px, py, sigma, caja, nx, ny, mask):
    """Las tres integrales del módulo 4, por definición y no por nombre."""
    xc, yc, dx, dy = rejilla_de(caja, nx, ny)
    cruda = kde_directa(px, py, sigma, xc, yc)
    e = borde_e(mask, dx, dy, sigma, nx, ny)
    celda = dx * dy

    sin_corr = float(cruda[mask].sum() * celda)
    con_e = np.where(e > 0, cruda / np.maximum(e, 1e-300), 0.0)
    defecto = float(con_e[mask].sum() * celda)

    # Diggle divide DESDE EL DATO: e evaluada en cada punto, no en cada
    # píxel. Se interpola el e del píxel más cercano a cada punto.
    # e(x_i) por INTERPOLACIÓN BILINEAL y no por el píxel más cercano: con
    # el píxel más cercano el error de Diggle se iba al 0,4 %, que es del
    # orden de lo que se quiere distinguir. El suelo de esta comprobación
    # tiene que estar por debajo del fenómeno que mide.
    fx = np.clip((px - xc[0]) / dx, 0, nx - 1.001)
    fy = np.clip((py - yc[0]) / dy, 0, ny - 1.001)
    i0 = fx.astype(int); j0 = fy.astype(int)
    tx = fx - i0; ty = fy - j0
    e_pt = ((1 - tx) * (1 - ty) * e[j0, i0] + tx * (1 - ty) * e[j0, i0 + 1] +
            (1 - tx) * ty * e[j0 + 1, i0] + tx * ty * e[j0 + 1, i0 + 1])
    dig = np.zeros_like(cruda)
    X, Y = np.meshgrid(xc, yc)
    for k in range(len(px)):
        if e_pt[k] <= 0:
            continue
        d2 = (X - px[k]) ** 2 + (Y - py[k]) ** 2
        dig += np.exp(-d2 / (2 * sigma ** 2)) / (2 * np.pi * sigma ** 2) / e_pt[k]
    diggle = float(dig[mask].sum() * celda)
    return sin_corr, defecto, diggle


# =====================================================================
def main() -> int:
    a = Auditoria("Precálculo del capítulo 5 verificado")

    D, p_datos = carga("CAP5_DATOS", "cap5_datos.json")
    M, p_mapas = carga("CAP5_MAPAS", "cap5_mapas.json")
    S, p_sols = carga("CAP5_SOLUCIONES", "cap5_soluciones.json")
    ken = pd.read_csv(SALIDAS / "cap5_kennedy.csv")
    urb = pd.read_csv(SALIDAS / "cap5_bogota_urbana.csv")
    fam_csv = pd.read_csv(SALIDAS / "cap5_familia_sigma.csv")
    haw = pd.read_csv(SALIDAS / "cap5_hawkes.csv")

    # LOS MAPAS QUE HACEN FALTA, COMPROBADOS ANTES DE USARLOS. La guarda
    # vivía al final, en la familia de los mapas, y el módulo 6 tira de
    # `proporcion_oficial` mucho antes: borrar ese mapa mataba al auditor
    # en la familia 5 y nunca llegaba a su propia comprobación. Un auditor
    # informa; para informar hay que llegar vivo al informe.
    MAPAS_NECESARIOS = ("kennedy_familia", "kennedy_puntos", "ciudad_oferta",
                        "ciudad_estudiantes", "proporcion_oficial", "sector_puntos")
    faltan_mapas = [n for n in MAPAS_NECESARIOS if n not in M]
    for nombre in MAPAS_NECESARIOS:
        a.cierto(nombre in M, f"mapas: está `{nombre}`")
    if faltan_mapas:
        a.cierto(False, "mapas: no falta ninguno para poder auditarlos",
                 ", ".join(faltan_mapas))
        return a.cierre()

    # -----------------------------------------------------------------
    a.titulo("1 · La ventana de Kennedy, releída con geopandas")
    # -----------------------------------------------------------------
    locs = gpd.read_file(PROCESADO / "bogota_localidades.gpkg")
    cole = gpd.read_file(PROCESADO / "bogota_colegios.gpkg")
    W = locs.loc[locs["localidad"] == "Kennedy", "geometry"].union_all()
    m1 = D["m1"]["ventana"]

    a.igual(len(ken), m1["n"], "Kennedy: el CSV trae las sedes que declara")
    a.cerca(W.area / 1e6, m1["area_km2"], "Kennedy: el área, recalculada con shapely", 1e-6)
    a.cerca(m1["n"] / m1["area_km2"], m1["lambda_km2"], "Kennedy: lambda es n entre el área", 1e-9)

    dentro = cole.geometry.within(W).to_numpy()
    a.igual(int(dentro.sum()), m1["n"], "Kennedy: la pertenencia geométrica cuadra")
    fr = D["m1"]["frontera"]
    a.igual(int((cole["localidad"] == "Kennedy").sum()), fr["n_atributo"],
            "Kennedy: y el conteo por atributo, también")
    a.igual(int(dentro.sum()), fr["n_geometria"], "Kennedy: geometría y atributo, cada uno el suyo")
    disc = np.where(dentro != (cole["localidad"] == "Kennedy").to_numpy())[0]
    a.igual(len(disc), fr["n_discrepan"], "Kennedy: las sedes que discrepan son las que dice")
    d_borde = cole.geometry.iloc[disc].distance(W.boundary).to_numpy()
    a.cerca(float(d_borde.max()), fr["dist_max_m"], "Kennedy: la más lejos del borde, a su distancia", 1e-6)
    a.cierto(float(d_borde.max()) < 200, "Kennedy: las tres siguen siendo casos de frontera",
             f"{d_borde.max():.0f} m")

    # -----------------------------------------------------------------
    a.titulo("2 · La KDE, recalculada por suma directa del núcleo")
    # -----------------------------------------------------------------
    fam = D["m2"]["familia"]
    caja_ken = M["kennedy_familia"][0]["caja"]
    nx, ny = fam["nx"], fam["ny"]
    xc, yc, dx, dy = rejilla_de(caja_ken, nx, ny)
    X, Y = np.meshgrid(xc, yc)
    mask = gpd.GeoSeries(gpd.points_from_xy(X.ravel(), Y.ravel())).within(W).to_numpy().reshape(ny, nx)
    px = ken["x"].to_numpy(); py = ken["y"].to_numpy()

    a.cerca((caja_ken[2] - caja_ken[0]) / nx, fam["celda_m"],
            "familia: la celda mide lo que declara", 1e-9)
    a.cierto(fam["celda_m"] * fam["celdas_por_sigma"] <= min(fam["sigmas_m"]) + 1e-9,
             "familia: la celda cabe tres veces en el sigma menor",
             f"{min(fam['sigmas_m'])/fam['celda_m']:.2f} celdas")

    # Los máximos de las siete superficies, recalculados. Es la afirmación
    # del módulo 2 —al abrir el núcleo la superficie se aplana— y aquí se
    # comprueba contra una KDE que no es la de spatstat.
    maxs = []
    for s in fam["sigmas_m"]:
        cr = kde_directa(px, py, s, xc, yc)
        e = borde_e(mask, dx, dy, s, nx, ny)
        sup = np.where((e > 0) & mask, cr / np.maximum(e, 1e-300), np.nan)
        maxs.append(float(np.nanmax(sup)) * 1e6)
    for i, s in enumerate(fam["sigmas_m"]):
        a.cerca(maxs[i], fam["max_km2"][i],
                f"familia: el máximo con sigma={s:.0f} m", TOL_SUP)
    a.cierto(all(np.diff(maxs) < 0), "familia: el máximo cae al abrir el núcleo",
             " ".join(f"{v:.1f}" for v in maxs))
    a.cerca(100 * (maxs[0] - maxs[-1]) / maxs[0], fam["caida_pct"],
            "familia: la caída total, recalculada", TOL_SUP)
    a.igual(len(fam_csv), len(fam["sigmas_m"]), "familia: el CSV trae las siete")
    a.cerca(float(fam_csv["max_km2"].iloc[0]), fam["max_km2"][0],
            "familia: el CSV y el JSON dicen lo mismo", 1e-9)

    # -----------------------------------------------------------------
    a.titulo("3 · Las tres correcciones de borde, por definición")
    # -----------------------------------------------------------------
    m4 = D["m4"]
    for fila in m4["tabla"]:
        s = fila["sigma_m"]
        sin_c, defec, dig = masas(px, py, s, caja_ken, nx, ny, mask)
        n = m4["n"]
        a.cerca(100 * (defec / n - 1), fila["exceso_defecto_pct"],
                f"borde: el exceso del defecto a sigma={s:.0f}", 0.25)
        a.cerca(100 * (sin_c / n - 1), fila["fuga_sin_corregir_pct"],
                f"borde: la fuga sin corregir a sigma={s:.0f}", 0.05)
        a.cierto(abs(100 * (dig / n - 1)) < 0.5,
                 f"borde: Diggle conserva el conteo a sigma={s:.0f}",
                 f"{100*(dig/n-1):+.4f} %")
        a.cierto(fila["fuga_sin_corregir_pct"] < 0 < fila["exceso_defecto_pct"],
                 f"borde: una se pasa y otra se queda corta, sigma={s:.0f}")
        a.cierto(abs(fila["error_diggle_pct"]) * 100 < abs(fila["exceso_defecto_pct"]),
                 f"borde: Diggle, cien veces más cerca a sigma={s:.0f}",
                 f"{fila['error_diggle_pct']:+.6f} contra {fila['exceso_defecto_pct']:+.4f}")
    exc = [f["exceso_defecto_pct"] for f in m4["tabla"]]
    fug = [f["fuga_sin_corregir_pct"] for f in m4["tabla"]]
    a.cierto(all(np.diff(exc) > 0) and all(np.diff(fug) < 0),
             "borde: las dos desviaciones crecen con sigma")
    a.cerca(max(exc) - min(fug), m4["horquilla_pct"],
            "borde: la horquilla entre las dos, recalculada", 1e-9)

    # -----------------------------------------------------------------
    a.titulo("4 · Los selectores de ancho de banda")
    # -----------------------------------------------------------------
    m3 = D["m3"]
    # `bw.scott` TIENE fórmula cerrada y se reimplementa: la desviación
    # típica por eje por n^(-1/6). Es el único de los cuatro que se puede
    # recalcular; los otros tres son validación cruzada y se auditan por
    # sus propiedades, dicho arriba.
    scott = float(np.std(px, ddof=1) * len(px) ** (-1 / 6))
    a.cerca(scott, m3["kennedy"]["sigmas_m"]["scott"],
            "selectores: bw.scott, con su fórmula cerrada", 1e-6)
    for donde, n_esp in (("kennedy", m1["n"]), ("urbana", None)):
        sg = m3[donde]["sigmas_m"]
        a.cierto(all(v > 0 for v in sg.values()), f"selectores/{donde}: los cuatro son positivos")
        a.cerca(max(sg.values()) / min(sg.values()), m3[donde]["razon"],
                f"selectores/{donde}: la razón entre extremos", 1e-9)
    # El rótulo va corto A PROPÓSITO: 57 caracteres contando el prefijo. El
    # matiz —que la ciudad discrepa más— baja al detalle, que no paga
    # presupuesto. Ver la cabecera de `audita_cap4.py`.
    a.cierto(m3["urbana"]["razon"] > m3["kennedy"]["razon"],
             "selectores: la ciudad discrepa más que Kennedy",
             f"{m3['urbana']['razon']:.2f} contra {m3['kennedy']['razon']:.2f}")
    a.igual(m3["kennedy"]["n"], m1["n"], "selectores: los de Kennedy son de sus sedes")
    for t in m3["topes"]:
        a.cierto(t["choco"] is True, f"selectores: {t['nombre'][:28]} chocó con su tope")
        a.cierto(t["sigma"] > 0, f"selectores: y su valor es finito y positivo")
    a.igual(len(m3["topes"]), 2, "selectores: los dos casos de tope están")

    # -----------------------------------------------------------------
    a.titulo("5 · El riesgo relativo, recalculado por definición")
    # -----------------------------------------------------------------
    # LA COMPROBACIÓN MÁS IMPORTANTE DE ESTE ARCHIVO. `relrisk` devuelve la
    # probabilidad del SEGUNDO nivel del factor, y el generador publicó una
    # vez P(privado) creyendo que era P(oficial) —con el título, la mediana
    # y la conclusión geográfica invertidos, y todo el arnés en verde—.
    # Aquí P(oficial) se recalcula por definición: el cociente de dos KDE
    # sobre la misma rejilla. Si el orden de niveles se vuelve a mover, esta
    # familia lo dice.
    v_urb = gpd.read_file(PROCESADO / "bogota_ventana_urbana.gpkg").union_all()
    m6 = D["m6"]["bogota"]
    mg = M["proporcion_oficial"]
    nxc, nyc = mg["nx"], mg["ny"]
    xcc, ycc, dxc, dyc = rejilla_de(mg["caja"], nxc, nyc)
    Xc, Yc = np.meshgrid(xcc, ycc)
    mask_c = gpd.GeoSeries(gpd.points_from_xy(Xc.ravel(), Yc.ravel())).within(
        v_urb).to_numpy().reshape(nyc, nxc)
    ofi = urb["sector"].to_numpy() == "Oficial"
    sg = m6["sigma_m"]
    k_ofi = kde_directa(urb["x"].to_numpy()[ofi], urb["y"].to_numpy()[ofi], sg, xcc, ycc)
    k_pri = kde_directa(urb["x"].to_numpy()[~ofi], urb["y"].to_numpy()[~ofi], sg, xcc, ycc)
    tot = k_ofi + k_pri
    prop = np.where((tot > 0) & mask_c, k_ofi / np.maximum(tot, 1e-300), np.nan)
    med = float(np.nanmedian(prop))

    a.igual(int(ofi.sum()), m6["oficiales"], "riesgo: las sedes oficiales son las que dice")
    a.igual(int((~ofi).sum()), m6["privadas"], "riesgo: y las privadas, también")
    a.cerca(float(ofi.mean()), m6["prop_global"], "riesgo: la proporción global, recontada", 1e-9)
    a.cierto(abs(med - m6["p_mediana"]) < 0.02,
             "riesgo: el mapa publicado ES P(oficial)",
             f"recalculada {med:.4f} contra {m6['p_mediana']:.4f} publicada")
    a.cierto(abs(med - (1 - m6["p_mediana"])) > 0.05,
             "riesgo: y NO es P(privado), que es el defecto de relrisk",
             f"{med:.4f} contra {1-m6['p_mediana']:.4f}")
    # Absoluta y no relativa: los dos sumandos vienen redondeados a diez
    # decimales, así que su diferencia no puede exigirse mejor que eso.
    a.igual(m6["p_mediana"] - m6["prop_global"], m6["brecha_mediana_menos_global"],
            "riesgo: la brecha entre la mediana y la global", 1e-9)
    a.cierto((m6["p_mediana"] < m6["prop_global"]) == m6["concentrado"],
             "riesgo: el veredicto de concentración cuadra con su cifra",
             "concentrado" if m6["concentrado"] else "repartido")
    a.cierto(m6["orientacion_verificada"] > m6["prop_global"],
             "riesgo: donde el mapa es máximo dominan los oficiales",
             f"{100*m6['orientacion_verificada']:.0f} % de los 50 vecinos")
    ch = D["m6"]["chorley"]
    a.igual(ch["casos"] + ch["controles"], 1036, "riesgo: chorley suma sus 1 036 puntos")
    a.cerca(ch["casos"] / (ch["casos"] + ch["controles"]), ch["prop_global"],
            "riesgo: la proporción de casos de chorley", 1e-9)
    a.cierto(ch["orientacion_verificada"] > ch["prop_global"],
             "riesgo: y su mapa también pinta los casos",
             f"{100*ch['orientacion_verificada']:.0f} % de los vecinos")

    # -----------------------------------------------------------------
    a.titulo("6 · Los tres mapas del módulo 5")
    # -----------------------------------------------------------------
    m5 = D["m5"]
    a.igual(m5["capas"]["oferta"]["n"], len(urb), "calor: la oferta son todas las sedes")
    con11 = urb["s11_n"].notna().to_numpy()
    a.igual(int(con11.sum()), m5["capas"]["grado_11"]["n"],
            "calor: las sedes con grado 11, recontadas")
    a.cerca(100 * con11.mean(), m5["capas"]["grado_11"]["pct_de_las_sedes"],
            "calor: y su porcentaje sobre el total", 1e-6)
    a.igual(int(urb.loc[con11, "s11_n"].sum()), m5["capas"]["estudiantes"]["total"],
            "calor: los evaluados suman lo que declara")
    a.cierto(0.5 < m5["cor_oferta_estudiantes"] < 0.99,
             "calor: oferta y estudiantes ni idénticos ni ajenos",
             f"r = {m5['cor_oferta_estudiantes']:.3f}")
    rj = m5["rejilla"]
    a.cerca(rj["celda_m"] * D["m2"]["familia"]["celdas_por_sigma"], rj["sigma_minimo_dibujable_m"],
            "calor: el sigma mínimo dibujable, recalculado", 1e-9)
    a.cierto(all(D["m3"]["urbana"]["sigmas_m"][s] < rj["sigma_minimo_dibujable_m"]
                 for s in rj["selectores_descartados"]),
             "calor: los descartados no llegan al mínimo",
             ", ".join(rj["selectores_descartados"]))
    a.cierto(m5["sigma_m"] == min(D["m3"]["urbana"]["sigmas_m"][s]
                                  for s in rj["selectores_dibujables"]),
             "calor: el mapa usa el dibujable más estrecho", m5["sigma_selector"])
    a.cierto(m5["caso_demirel"] is None,
             "calor: el caso de Demirel sigue declarado y vacío",
             "la decisión 2 pide su fuente antes de escribirlo")

    # -----------------------------------------------------------------
    a.titulo("7 · rhohat: el bulto y la cola")
    # -----------------------------------------------------------------
    m7 = D["m7"]
    cx = float(urb["x"].mean()); cy = float(urb["y"].mean())
    dist = np.hypot(urb["x"].to_numpy() - cx, urb["y"].to_numpy() - cy)
    q5, q95 = np.quantile(dist, [0.05, 0.95])
    a.cerca(q5, m7["bogota"]["curva"]["bulto_desde"],
            "rhohat: el percentil 5 de la distancia", TOL_R6)
    a.cerca(q95, m7["bogota"]["curva"]["bulto_hasta"],
            "rhohat: y el percentil 95", TOL_R6)
    for etq, c in (("bei/elev", m7["bei"]["elevacion"]), ("bei/grad", m7["bei"]["pendiente"]),
                   ("bogotá", m7["bogota"]["curva"])):
        a.cerca(c["razon"] / c["razon_bulto"], c["cola_infla"],
                f"rhohat: cuánto infla la cola en {etq}", TOL_R6)
        a.cierto(c["cola_infla"] > 1, f"rhohat: la cola infla, no encoge, en {etq}",
                 f"{c['cola_infla']:.1f}x")
        a.cerca(c["rho_max"] / c["rho_min"], c["razon"],
                f"rhohat: la razón total en {etq}", TOL_R6)
    a.cierto(m7["bogota"]["curva"]["razon_bulto"] < m7["bei"]["elevacion"]["razon_bulto"]
             < m7["bei"]["pendiente"]["razon_bulto"],
             "rhohat: el orden en el bulto es el que el módulo cuenta")

    # -----------------------------------------------------------------
    a.titulo("8 · ppm: la identidad de la EMV y la cuadratura")
    # -----------------------------------------------------------------
    m8 = D["m8"]
    area_urb = v_urb.area
    a.cerca(len(urb) / area_urb, m8["homogeneo"]["lambda_mle_m2"],
            "ppm: la EMV homogénea es n entre el área", TOL_R6)
    a.cerca(m8["homogeneo"]["lambda_mle_m2"] * 1e6, m8["homogeneo"]["lambda_km2"],
            "ppm: y la misma cifra en km²", TOL_R6)
    a.cierto(m8["homogeneo"]["dif_relativa"] < 1e-9,
             "ppm: R y la fórmula coinciden a precisión de máquina",
             f"{m8['homogeneo']['dif_relativa']:.1e}")
    tab = m8["cuadratura"]["tabla"]
    a.cierto(all(t2["ficticios"] > t1["ficticios"] for t1, t2 in zip(tab, tab[1:])),
             "ppm: más nd, más puntos ficticios")
    a.igual(tab[1]["ficticios"], m8["cuadratura"]["defecto_ficticios"],
            "ppm: el defecto es nd = 100")
    pend = [t2["pendiente"] for t2 in tab]
    a.cerca((max(pend) - min(pend)) / tab[1]["ee_pendiente"],
            m8["cuadratura"]["rango_pendiente_en_ee"],
            "ppm: la pendiente se mueve, en errores estándar", 1e-6)
    aics = [t2["aic"] for t2 in tab]
    a.cerca(max(aics) - min(aics), m8["cuadratura"]["rango_aic"],
            "ppm: y el AIC se mueve, en puntos", 1e-6)
    a.cierto(m8["cuadratura"]["rango_aic"] > 2,
             "ppm: el AIC se mueve más que un parámetro de más",
             f"{m8['cuadratura']['rango_aic']:.1f} puntos")

    m9 = D["m9"]
    a.cierto(m9["crudo"]["singular"] is True, "ppm: con coordenadas crudas, singular")
    a.cierto(m9["centrado"]["singular"] is False, "ppm: y centradas, no")
    a.cierto(m9["crudo"]["ee"] is None, "ppm: el crudo no publica errores estándar")
    a.igual(len(m9["centrado"]["ee"]), len(m9["centrado"]["coef"]),
            "ppm: el centrado tiene un ee por coeficiente")
    a.cierto(m9["crudo"]["cond_reciproco"] < m9["centrado"]["cond_reciproco"],
             "ppm: centrar mejora el condicionamiento",
             f"{m9['crudo']['cond_reciproco']:.1e} -> {m9['centrado']['cond_reciproco']:.1e}")
    a.cerca(m9["centrado"]["cond_reciproco"] / m9["crudo"]["cond_reciproco"],
            m9["mejora_condicion"], "ppm: cuánto mejora, recalculado", 1e-3)

    # -----------------------------------------------------------------
    a.titulo("9 · La envolvente: propiedades, no valores")
    # -----------------------------------------------------------------
    m10 = D["m10"]
    c = m10["curva"]
    r = np.array(c["r"]); obs = np.array(c["obs"])
    lo = np.array(c["lo"]); hi = np.array(c["hi"])
    a.igual(len(r), m10["n_nodos"], "envolvente: los nodos que declara")
    a.cierto(bool(np.all(np.diff(r) > 0)), "envolvente: la rejilla de r es creciente")
    a.cierto(bool(np.all(lo <= hi)), "envolvente: la banda nunca se cruza")
    a.cerca(100 * 2 / (m10["nsim"] + 1), m10["nivel_puntual_pct"],
            "envolvente: el nivel puntual es 2/(nsim+1)", 1e-9)
    dentro_r = r > 0
    fuera = (obs > hi) | (obs < lo)
    a.cerca(100 * fuera[dentro_r].mean(), m10["pct_r_fuera_de_banda"],
            "envolvente: el porcentaje fuera de banda", 1e-6)
    a.cierto(m10["pct_r_fuera_de_banda"] > 0,
             "envolvente: el patrón se sale del modelo ajustado",
             f"{m10['pct_r_fuera_de_banda']:.1f} % de los r")
    a.cerca(float(r[dentro_r][fuera[dentro_r]].min()), m10["primer_r_fuera_m"],
            "envolvente: el primer r que se sale", 1e-6)
    a.cierto(m10["correccion"] == "translate",
             "envolvente: la corrección viaja en el dato", m10["correccion"])

    # -----------------------------------------------------------------
    a.titulo("10 · Conglomerado, y el Hawkes recalculado")
    # -----------------------------------------------------------------
    m11 = D["m11"]
    a.igual(len(m11["ajustes"]), 6, "kppm: los tres modelos por las dos correcciones")
    # UN AUDITOR NO SE MUERE ANTE UN ARCHIVO ROTO: INFORMA. Buscar con
    # `[...][0]` estallaba en cuanto una inyección truncaba la lista de
    # ajustes, y el arnés contaba ese reventón como captura porque solo
    # miraba el código de salida. La lección subió a `revento()` en el
    # núcleo del arnés; aquí lo que toca es no morirse.
    def busca_ajuste(modelo, corr):
        for x in m11["ajustes"]:
            if x.get("modelo") == modelo and x.get("correccion") == corr:
                return x
        return None
    for d in m11["divergencia"]:
        aj_iso = busca_ajuste(d["modelo"], "iso")
        aj_tra = busca_ajuste(d["modelo"], "translate")
        if aj_iso is None or aj_tra is None:
            a.cierto(False, f"kppm/{d['modelo']}: están sus dos ajustes",
                     f"iso {'sí' if aj_iso else 'NO'}, translate {'sí' if aj_tra else 'NO'}")
            continue
        a.cerca(100 * abs(aj_tra["mu"] - aj_iso["mu"]) / abs(aj_iso["mu"]), d["mu_pct"],
                f"kppm/{d['modelo']}: la divergencia en mu", 1e-6)
        a.cierto(aj_iso["segundos"] > aj_tra["segundos"],
                 f"kppm/{d['modelo']}: la isotrópica cuesta más",
                 f"{aj_iso['segundos']:.1f} s contra {aj_tra['segundos']:.2f}")
    a.cierto(max(d["mu_pct"] for d in m11["divergencia"]) > 10,
             "kppm: cambiar la corrección cambia la respuesta",
             f"hasta {max(d['mu_pct'] for d in m11['divergencia']):.1f} % en mu")
    dup = m11["duplicados"]
    a.igual(dup["n_con"] - dup["n_sin"], dup["repetidos"], "kppm: los repetidos, recontados")
    a.cierto(dup["cambio_maximo_pct"] < 15,
             "kppm: los duplicados no descuadran el ajuste",
             f"como mucho {dup['cambio_maximo_pct']:.1f} %")

    h = m11["hawkes"]
    a.cerca(h["alpha"] / h["beta"], h["razon_ramificacion"],
            "hawkes: la razón de ramificación es alpha/beta", 1e-9)
    a.cerca(h["mu"] / (1 - h["razon_ramificacion"]), h["tasa_teorica"],
            "hawkes: la tasa teórica, recalculada", 1e-9)
    th = haw.loc[haw["proceso"] == "hawkes", "t"].to_numpy()
    tp = haw.loc[haw["proceso"] == "poisson", "t"].to_numpy()
    a.igual(len(th), h["n_eventos"], "hawkes: el CSV trae los eventos que dice")
    a.igual(len(tp), len(th), "hawkes: y su Poisson, los mismos")
    a.cerca(len(th) / h["T"], h["tasa_simulada"], "hawkes: la tasa simulada, recontada", 1e-9)
    a.cierto(abs(h["tasa_simulada"] - h["tasa_teorica"]) / h["tasa_teorica"] < 0.10,
             "hawkes: la simulación cuadra con la teoría",
             f"{h['tasa_simulada']:.3f} contra {h['tasa_teorica']:.3f}")

    def dispersion(ev, k=200):
        cnt, _ = np.histogram(ev, bins=np.linspace(0, h["T"], k + 1))
        return float(cnt.var(ddof=1) / cnt.mean())
    a.cerca(dispersion(th), h["dispersion_hawkes"],
            "hawkes: el índice de dispersión, recalculado", 1e-6)
    a.cerca(dispersion(tp), h["dispersion_poisson"], "hawkes: y el de su Poisson", 1e-6)
    a.cierto(dispersion(th) > dispersion(tp),
             "hawkes: el autoexcitado sale más agregado",
             f"{dispersion(th):.2f} contra {dispersion(tp):.2f}")

    # -----------------------------------------------------------------
    a.titulo("11 · Los cinco ejercicios")
    # -----------------------------------------------------------------
    a.igual(S["meta"]["n_ejercicios"], 5, "ejercicios: son cinco, por la decisión 1")
    faltan = [k for k in ("e1", "e2", "e3", "e4", "e5") if k not in S]
    for k in ("e1", "e2", "e3", "e4", "e5"):
        a.cierto(k in S, f"ejercicios: está {k}")
        if k in S:
            a.cierto(len(S[k]["pasos"]) >= 4, f"ejercicios/{k}: publica sus pasos",
                     f"{len(S[k]['pasos'])} pasos")
            a.cierto(bool(S[k]["enunciado"].strip()), f"ejercicios/{k}: tiene enunciado")
    if faltan:
        # Sin el ejercicio no se puede comprobar su contenido, y fingir que
        # sí es como se muere un auditor. Se informa y se sigue.
        a.cierto(False, "ejercicios: no falta ninguno para poder auditarlos",
                 ", ".join(faltan))
        return a.cierre()
    a.cierto(S["e1"]["solucion"]["n_chocaron"] >= 1,
             "ejercicios/e1: hay un selector que chocó")
    a.cierto(all(abs(f["diggle_pct"]) * 100 < abs(f["defecto_pct"])
                 for f in S["e2"]["solucion"]["tabla"]),
             "ejercicios/e2: Diggle sigue cien veces más cerca")
    a.cierto(S["e3"]["solucion"]["cola_infla"] > 1,
             "ejercicios/e3: la cola infla también en bei",
             f"{S['e3']['solucion']['cola_infla']:.1f}x")
    a.cierto(S["e4"]["solucion"]["dif_relativa_pendientes"] < 1e-6,
             "ejercicios/e4: desplazar no mueve las pendientes",
             f"{S['e4']['solucion']['dif_relativa_pendientes']:.1e}")
    a.cierto(max(S["e5"]["solucion"]["diferencias_pct"].values()) > 5,
             "ejercicios/e5: las dos correcciones divergen en redwood")

    # -----------------------------------------------------------------
    a.titulo("12 · Los mapas")
    # -----------------------------------------------------------------
    # La presencia de cada mapa se comprobó al arrancar, antes de que
    # ninguna familia tirara de ellos.
    a.igual(len(M["kennedy_familia"]), D["m2"]["familia"]["n"],
            "mapas: la familia trae sus siete superficies")
    # CADA SUPERFICIE LLEVA SU SIGMA, y esa es la lección de T1.2/T1.3: el
    # deslizador busca por parámetro y no por posición. Sin el sigma dentro,
    # emparejar las dos listas volvería a ser por índice.
    sig_map = [g["sigma_m"] for g in M["kennedy_familia"]]
    a.cierto(sig_map == D["m2"]["familia"]["sigmas_m"],
             "mapas: cada superficie lleva su sigma, y en orden")
    esc = M["kennedy_familia"][0]["escala_comun"]
    a.cierto(all(g["escala_comun"] == esc for g in M["kennedy_familia"]),
             "mapas: las siete comparten UNA escala")
    zmax = [max(g["zq"]) for g in M["kennedy_familia"]]
    a.cierto(all(z2 <= z1 for z1, z2 in zip(zmax, zmax[1:])),
             "mapas: el máximo cuantizado cae, como la intensidad",
             " ".join(str(z) for z in zmax))
    a.cierto(zmax[0] > zmax[-1] * 2,
             "mapas: y cae lo bastante para verse",
             f"{zmax[0]} contra {zmax[-1]}")
    for nombre in ("kennedy_puntos", "sector_puntos"):
        a.cierto(M[nombre]["modo"] == "puntos", f"mapas/{nombre}: es del modo puntos")
    for nombre in ("ciudad_oferta", "ciudad_estudiantes", "proporcion_oficial"):
        g = M[nombre]
        a.cierto(g["modo"] == "rejilla", f"mapas/{nombre}: es del modo rejilla")
        a.igual(len(g["zq"]), g["nx"] * g["ny"], f"mapas/{nombre}: el ráster tiene sus celdas")
        a.cierto(min(g["zq"]) == -1, f"mapas/{nombre}: marca las celdas de fuera")
        a.cierto(max(g["zq"]) <= g["zqmax"], f"mapas/{nombre}: nada se sale de la cuantización")
    # EL CONTRATO DEL RÁSTER, CERRADO EN EL NÚCLEO Y NO DECLARADO ABIERTO.
    # Los mapas de modo `rejilla` no llevan `q` —ni aquí ni en los diez del
    # capítulo 1— y `audita_geomapa()` la exigía, así que el modo llevaba
    # desde T0.3 en la lista de los cinco SIN UNA SOLA COMPROBACIÓN PROPIA
    # del núcleo. No era un descuido de quien publica: un ráster no tiene
    # vértices que cuantizar. El núcleo pasa a pedirle lo suyo —que la
    # rejilla declare sus lados, que haya una celda por posición, que -1
    # sea el único negativo y que nada se salga de la cuantización— y los
    # rásteres cruzan la misma puerta que los demás mapas.
    for nombre in ("kennedy_puntos", "sector_puntos", "ciudad_oferta",
                   "ciudad_estudiantes", "proporcion_oficial"):
        audita_geomapa(a, M[nombre], nombre, presupuesto_kb=560.0)
    for i, g in enumerate(M["kennedy_familia"]):
        audita_geomapa(a, g, f"familia[{i}]", presupuesto_kb=560.0)
    p_ofi = np.array(M["proporcion_oficial"]["zq"], dtype=float)
    dentro_z = p_ofi >= 0
    zqm = M["proporcion_oficial"]["zqmax"]
    if not zqm or not dentro_z.any():
        a.cierto(False, "mapas: el ráster de proporción es legible",
                 f"zqmax = {zqm}, celdas con dato = {int(dentro_z.sum())}")
    else:
        a.cierto(abs(float(np.median(p_ofi[dentro_z])) / zqm
                     - D["m6"]["bogota"]["p_mediana"]) < 0.02,
                 "mapas: el ráster de proporción pinta P(oficial)",
                 f"mediana {np.median(p_ofi[dentro_z])/zqm:.4f}")

    # -----------------------------------------------------------------
    a.titulo("13 · Formato")
    # -----------------------------------------------------------------
    for nombre, obj in (("datos", D), ("mapas", M), ("soluciones", S)):
        nans = list(sin_nan(obj))
        a.cierto(not nans, f"{nombre}: sin NaN ni infinitos", str(nans[:3]))
    txt = p_datos.read_text(encoding="utf-8")
    a.cierto("Ã" not in txt and "\ufffd" not in txt,
             "datos: las tildes están intactas en el archivo")
    a.cierto("ó" in txt or "í" in txt, "y hay tildes de verdad que comprobar")
    excesivos = [(r2, n) for r2, n in decimales(D) if n > 10]
    a.cierto(not excesivos, "datos: ningún flotante pasa de 10 decimales", str(excesivos[:3]))
    a.igual(D["meta"]["capitulo"], 5, "la metainformación dice capítulo 5")
    a.cierto(D["meta"]["semanas"] == "8-10",
             "y que cubre las semanas 8 a 10", D["meta"]["semanas"])
    a.cierto(D["meta"]["n_anclas"] >= 15, "el generador comprobó sus anclas",
             f"{D['meta']['n_anclas']} anclas")
    sem = D["meta"]["semillas"]
    a.cierto(len(set(sem.values())) == len(sem),
             "las semillas del capítulo son todas distintas", str(sem))
    a.cierto(D["meta"]["semilla"] not in sem.values(),
             "y ninguna repite la semilla global", str(D["meta"]["semilla"]))
    a.igual(D["meta"]["duplicados"]["repetidos"],
            D["m11"]["duplicados"]["repetidos"],
            "los duplicados dicen lo mismo en los dos sitios")

    return a.cierre()


if __name__ == "__main__":
    raise SystemExit(main())
