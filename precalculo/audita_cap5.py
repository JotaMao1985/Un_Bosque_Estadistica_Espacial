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
import re
import sys
from statistics import NormalDist

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


def puntos_de(g):
    """Las coordenadas reales de un mapa de modo `puntos`, como las pinta el navegador.

    `geomapaCajaQ` cuantiza en el CUADRADO de lado max(ancho, alto) centrado en la caja, no en la
    caja: descuantizar contra la caja rectangular corre el eje corto.
    """
    x0, y0, x1, y1 = g["caja"]
    q = g.get("q", 4096)
    lado = max(x1 - x0, y1 - y0)
    p = np.asarray(g["pts"], dtype=float).reshape(-1, 2)
    return ((x0 + x1) / 2 - lado / 2 + p[:, 0] / q * lado,
            (y0 + y1) / 2 - lado / 2 + p[:, 1] / q * lado)


def muestrea(g, X, Y, reflejo=False):
    """El valor cuantizado de un mapa `rejilla` en (X, Y), con la fila 0 ARRIBA (el norte),
    que es como la pinta `geomapaPintaRejilla`. Con `reflejo`, leído al revés. -1 = sin dato."""
    x0, y0, x1, y1 = g["caja"]
    nx, ny = g["nx"], g["ny"]
    c = np.floor((X - x0) / (x1 - x0) * nx).astype(int)
    f = np.floor((y1 - Y) / (y1 - y0) * ny).astype(int)
    if reflejo:
        f = ny - 1 - f
    ok = (c >= 0) & (c < nx) & (f >= 0) & (f < ny)
    zq = np.asarray(g["zq"], dtype=float)
    z = np.full(len(X), -1.0)
    z[ok] = zq[f[ok] * nx + c[ok]]
    return z


# =====================================================================
# Cada «di», «explica», «encuentra», «contesta», «compara» y cada «¿» de un
# enunciado es una pregunta que la solución tiene que contestar (M5). `\w`
# en Python ya es Unicode: «Encuéntralo» no se parte por la tilde, y
# «compárala» —que pide un número, no una frase— no casa con «compara».
DEMANDA = re.compile(
    r"(?<!\w)(?:[Dd]i|[Ee]xplica|[Ee]ncuéntralo|[Ee]ncuentra|[Cc]ontesta|[Cc]ompara)(?!\w)|¿")


def sin_contestar(e) -> list[str]:
    """Las demandas del enunciado que no caen dentro de ninguna respuesta.

    Reimplementa la guarda de `genera_soluciones.R` sin mirarla: una
    demanda queda contestada si cae dentro del trozo literal que ancla
    alguna respuesta, o si presenta a otra —«Contesta: ¿…?»— y una
    respuesta empieza detrás de ella sin que medie un punto.
    """
    en = e.get("enunciado", "")
    tramos = []
    for r in e.get("solucion", {}).get("respuestas") or []:
        pide = r.get("pide") or ""
        i = en.find(pide) if pide else -1
        if i >= 0:
            tramos.append((i, i + len(pide)))
    fuera = []
    for m in DEMANDA.finditer(en):
        p = m.start()
        dentro = any(ini <= p < fin for ini, fin in tramos)
        if not dentro and en[m.end():m.end() + 1] == ":":
            despues = [ini for ini, _ in tramos if ini > p]
            dentro = bool(despues) and "." not in en[p:min(despues)]
        if not dentro:
            fuera.append(en[p:p + 30])
    return fuera


def respuestas_de_los_ejercicios(a, S) -> None:
    """M5 de la segunda revisión (2026-09-24): lo que cada solución contesta.

    Hasta M5 la solución publicaba los pasos y una lectura, y los
    enunciados preguntaban cosas que ni lo uno ni lo otro contestaba. Aquí
    se comprueba lo general —cada ejercicio trae respuestas, ancladas a su
    enunciado, sin demanda huérfana— y lo particular: cada afirmación de
    las respuestas se rehace desde los campos del propio JSON, y cada paso
    nuevo de la tabla dice lo que su campo dice.
    """
    a.titulo("11b · Las respuestas de los ejercicios (M5)")

    def paso(k, empieza):
        """El valor del paso cuya etiqueta empieza así, o None."""
        for p in S[k].get("pasos", []):
            if p.get("paso", "").startswith(empieza):
                return p.get("valor")
        return None

    def mismo(k, empieza, valor, que, rel=1e-9):
        v = paso(k, empieza)
        if v is None or valor is None:
            a.cierto(False, que, f"falta el paso «{empieza}» o su campo")
        else:
            a.cerca(v, valor, que, rel=rel)

    for k in ("e1", "e2", "e3", "e4", "e5"):
        sol = S[k].get("solucion", {})
        resp = sol.get("respuestas") or []
        a.cierto(len(resp) > 0 and all(str(r.get("pide", "")).strip() and
                                       str(r.get("respuesta", "")).strip() for r in resp),
                 f"ejercicios/{k}: trae respuestas, y ninguna vacía", f"{len(resp)}")
        sueltas = [r.get("pide") for r in resp if r.get("pide", "") not in S[k].get("enunciado", "")]
        a.cierto(not sueltas, f"ejercicios/{k}: cada respuesta ancla en su enunciado",
                 "; ".join(map(str, sueltas)))
        fuera = sin_contestar(S[k])
        a.cierto(not fuera, f"ejercicios/{k}: ninguna demanda se queda sin respuesta",
                 " | ".join(fuera))
        a.cierto(bool(str(sol.get("lectura", "")).strip()), f"ejercicios/{k}: trae su lectura")

    # --- E1 · el que chocó, con nombre ------------------------------------
    s1 = S["e1"]["solucion"]
    ch = s1.get("chocado")
    patrones = ("japanesepines", "redwood", "swedishpines")
    if not ch or not all(isinstance(s1.get(p), list) for p in patrones):
        a.cierto(False, "ejercicios/e1: publica el selector que chocó", "falta")
    else:
        valores = [(p, z["selector"], z["sigma"], z["choco"]) for p in patrones for z in s1[p]]
        chocan = [v for v in valores if v[3]]
        a.cierto(len(valores) == 12 and len(chocan) == 1,
                 "ejercicios/e1: chocó uno de doce, como dice el enunciado",
                 f"{len(chocan)} de {len(valores)}")
        a.cierto(bool(chocan) and chocan[0][:3] == (ch["patron"], ch["selector"], ch["sigma"]),
                 "ejercicios/e1: el que publica es el que chocó")
        # En el cuadrado unidad, la mitad del diámetro es la de la diagonal.
        a.igual(ch["tope"], np.hypot(1, 1) / 2, "ejercicios/e1: el tope es la mitad de la diagonal")
        a.igual(ch["sigma"], ch["tope"], "ejercicios/e1: y el que chocó vale el tope")
        a.igual(ch["sigma_ancho"], ch["tope_ancho"], "ejercicios/e1: ensanchado, vuelve a chocar")
        sig = {z["selector"]: z["sigma"] for z in s1[ch["patron"]]}
        resto = [v for s, v in sig.items() if s != ch["selector"]]
        a.cerca(max(resto) / min(resto), ch["razon_sin"], "ejercicios/e1: el cociente sin el que chocó")
        raz = {p: max(z["sigma"] for z in s1[p]) / min(z["sigma"] for z in s1[p]) for p in patrones}
        otros = [raz[p] for p in patrones if p != ch["patron"]]
        a.cierto(raz[ch["patron"]] > max(otros) and ch["razon_sin"] < min(otros),
                 "ejercicios/e1: con él discrepa más; sin él, menos",
                 f"{raz[ch['patron']]:.2f} → {ch['razon_sin']:.2f}")
        a.cierto(f"`bw.{ch['selector']}` sobre `{ch['patron']}`" in
                 (s1.get("respuestas") or [{}])[0].get("respuesta", ""),
                 "ejercicios/e1: la respuesta lo nombra")
        for p in patrones:
            mismo("e1", f"Cociente mayor/menor en {p}", raz[p],
                  f"ejercicios/e1: paso · cociente en {p}"[:57], rel=1e-8)
        mismo("e1", f"sigma de bw.{ch['selector']} en", ch["sigma"], "ejercicios/e1: paso · el que chocó")
        mismo("e1", "Tope de su intervalo", ch["tope"], "ejercicios/e1: paso · el tope")
        mismo("e1", f"sigma de bw.{ch['selector']} con el tope", ch["sigma_ancho"],
              "ejercicios/e1: paso · el tope ensanchado")
        mismo("e1", "Cociente mayor/menor en " + ch["patron"] + " sin", ch["razon_sin"],
              "ejercicios/e1: paso · el cociente sin él")

    # --- E2 · cuál conserva, y qué les pasa a las otras dos ---------------
    s2 = S["e2"]["solucion"]
    t2 = s2.get("tabla") or []
    if not t2 or not all("diggle_fina_pct" in f and "rejilla" in f for f in t2):
        a.cierto(False, "ejercicios/e2: publica la rejilla fina", "falta")
    else:
        dg = [abs(f["diggle_pct"]) for f in t2]
        df = [f["defecto_pct"] for f in t2]
        sc = [f["sin_corregir_pct"] for f in t2]
        a.cierto(min(abs(x) for x in df) / max(dg) > 1000,
                 "ejercicios/e2: Diggle, más de mil veces más cerca",
                 f"{min(abs(x) for x in df) / max(dg):.0f}x")
        a.cierto(all(abs(f["diggle_fina_pct"]) < abs(f["diggle_pct"]) for f in t2),
                 "ejercicios/e2: afinar la rejilla encoge el residuo")
        a.cierto(all(x > 0 for x in df) and all(b > c for c, b in zip(df, df[1:])),
                 "ejercicios/e2: el defecto se pasa, y más al abrir")
        a.cierto(all(x < 0 for x in sc) and all(b < c for c, b in zip(sc, sc[1:])),
                 "ejercicios/e2: sin corregir se queda corto, y más")
        a.cierto(all(abs(s) > abs(d) for s, d in zip(sc, df)),
                 "ejercicios/e2: la fuga crece más que el exceso")
        peor = {"defecto": max(abs(x) for x in df), "diggle": max(dg),
                "sin_corregir": max(abs(x) for x in sc)}
        a.cierto(s2.get("cual_conserva") == min(peor, key=peor.get),
                 "ejercicios/e2: la que conserva es la de menor error", str(s2.get("cual_conserva")))
        mismo("e2", "|Error| máximo de diggle", max(dg), "ejercicios/e2: paso · el mayor error de Diggle")
        mismo("e2", "El mismo, con rejilla", max(abs(f["diggle_fina_pct"]) for f in t2),
              "ejercicios/e2: paso · el mismo con la rejilla fina")
        etq = [p["paso"] for p in S["e2"]["pasos"]]
        a.cierto(any(f"{t2[0]['rejilla']} × {t2[0]['rejilla']}" in e for e in etq) and
                 any(f"{s2.get('rejilla_fina')} × {s2.get('rejilla_fina')}" in e for e in etq),
                 "ejercicios/e2: las etiquetas dicen sus dos rejillas")

    # --- E3 · la z, el cociente que implica y la z con conglomerado -------
    s3 = S["e3"]["solucion"]
    pp, kp, co = s3.get("ppm"), s3.get("kppm"), s3.get("colas")
    if not (pp and kp and co and all(c in kp for c in ("defecto", "isotropica", "traslacion"))):
        a.cierto(False, "ejercicios/e3: publica ppm, kppm y las colas", "falta")
    else:
        a.cerca(pp["coef"] / pp["ee"], s3["z_ppm"], "ejercicios/e3: la z de ppm es coef / ee")
        b3 = s3["bulto"]
        a.cerca(np.exp(pp["coef"] * (b3["hasta"] - b3["desde"])), pp["razon_bulto"],
                "ejercicios/e3: el cociente que implica ppm")
        a.cierto(abs(np.log(pp["razon_bulto"] / s3["razon_bulto"])) <
                 abs(np.log(pp["razon_bulto"] / s3["razon_total"])),
                 "ejercicios/e3: y queda del lado del bulto")
        for c in ("defecto", "isotropica", "traslacion"):
            a.cerca(kp[c]["coef"] / kp[c]["ee"], kp[c]["z"], f"ejercicios/e3: z de kppm, {c}")
        a.cierto(all(abs(kp[c]["coef"] - pp["coef"]) < 1e-8 for c in kp),
                 "ejercicios/e3: kppm no mueve el coeficiente")
        a.igual(kp["defecto"]["z"], kp["isotropica"]["z"], "ejercicios/e3: la de por defecto es la isotrópica")
        infl = [kp[c]["ee"] / pp["ee"] for c in ("isotropica", "traslacion")]
        a.cierto(all(8 <= x <= 13 for x in infl), "ejercicios/e3: el error estándar, por unas diez",
                 " / ".join(f"{x:.1f}" for x in infl))
        zc = NormalDist().inv_cdf(0.975)
        a.igual(s3.get("z_critico"), zc, "ejercicios/e3: el umbral es el de 1.96")
        a.cierto(kp["isotropica"]["z"] < zc < kp["traslacion"]["z"],
                 "ejercicios/e3: una z a cada lado del umbral",
                 f"{kp['isotropica']['z']:.3f} / {kp['traslacion']['z']:.3f}")
        a.cierto(co["mas_empinados"] == 0 and co["x_max"] > b3["hasta"],
                 "ejercicios/e3: el máximo, sin árbol más empinado")
        a.cierto(0 < co["menos_empinados"] < 0.01 * s3.get("n_arboles", 0) and co["x_min"] < b3["desde"],
                 "ejercicios/e3: el mínimo, con unos pocos por debajo",
                 f"{co['menos_empinados']} de {s3.get('n_arboles')}")
        a.cierto(f"set.seed({s3.get('semilla')})" in S["e3"]["enunciado"] and
                 s3.get("semilla") == S["meta"]["semilla"],
                 "ejercicios/e3: el enunciado da la semilla de rhohat")
        mismo("e3", "Árboles más empinados", co["mas_empinados"], "ejercicios/e3: paso · más empinados")
        mismo("e3", "Árboles menos empinados", co["menos_empinados"], "ejercicios/e3: paso · menos empinados")
        mismo("e3", "Coeficiente de la pendiente", pp["coef"], "ejercicios/e3: paso · el coeficiente")
        mismo("e3", "z de la pendiente en ppm", s3["z_ppm"], "ejercicios/e3: paso · la z de ppm")
        mismo("e3", "Cociente que implica ppm", pp["razon_bulto"], "ejercicios/e3: paso · el cociente de ppm")
        mismo("e3", "z de la pendiente en kppm, corrección por defecto", kp["defecto"]["z"],
              "ejercicios/e3: paso · z de kppm por defecto")
        mismo("e3", "z de la pendiente en kppm, corrección de traslación", kp["traslacion"]["z"],
              "ejercicios/e3: paso · z de kppm con traslación")

    # --- E4 · el intercepto se lo lleva todo ------------------------------
    s4 = S["e4"]["solucion"]
    cc, cl = s4.get("coef_cerca") or [], s4.get("coef_lejos") or []
    if len(cc) != 3 or len(cl) != 3:
        a.cierto(False, "ejercicios/e4: publica los dos juegos de coeficientes", "falta")
    else:
        a.cerca(cc[0] - s4["desplazamiento"] * (cc[1] + cc[2]), cl[0],
                "ejercicios/e4: el intercepto absorbe el desplazamiento")
        mismo("e4", "Coeficiente de x", cc[1], "ejercicios/e4: paso · el coeficiente de x")
        mismo("e4", "Coeficiente de y", cc[2], "ejercicios/e4: paso · el coeficiente de y")
        mismo("e4", "Intercepto del ajuste original", cc[0], "ejercicios/e4: paso · intercepto original")
        mismo("e4", "Intercepto del ajuste desplazado", cl[0], "ejercicios/e4: paso · intercepto desplazado")

    # --- E5 · los seis valores que el enunciado pide ----------------------
    s5 = S["e5"]["solucion"]
    iso, tra, dif = s5.get("isotropica"), s5.get("traslacion"), s5.get("diferencias_pct")
    if not (iso and tra and dif):
        a.cierto(False, "ejercicios/e5: publica los dos ajustes", "falta")
    else:
        for par, et in (("kappa", "kappa"), ("escala", "Escala"), ("mu", "mu")):
            mismo("e5", f"{et} con isotrópica", iso[par], f"ejercicios/e5: paso · {par} con isotrópica")
            mismo("e5", f"{et} con traslación", tra[par], f"ejercicios/e5: paso · {par} con traslación")
            a.cerca(100 * abs(tra[par] - iso[par]) / abs(iso[par]), dif[par],
                    f"ejercicios/e5: la diferencia en {par}", rel=1e-6)


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
    # Rótulos de menos de 58 caracteres: el arnés de inyección cuenta la
    # cobertura por rótulo, y uno más largo arrastra su detalle.
    CORTO = {"ciudad_bachillerato": "ciudad_bach11"}
    MAPAS_NECESARIOS = ("kennedy_familia", "kennedy_puntos", "ciudad_oferta", "ciudad_bachillerato",
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

    # El conteo por cuadrantes, cada celda entre SU área. Hasta el 2026-10-27
    # el generador dividía por A_KEN/64 y nadie lo recalculaba: el máximo se
    # publicó en 24.9 sedes por km² siendo 16.8. Aquí, sin spatstat: la
    # rejilla parte la caja, y cada celda se recorta con la ventana.
    cq = D["m1"]["cuadrantes"]
    from shapely.geometry import box as _box
    bx0, by0, bx1, by1 = W.bounds
    xs_q, ys_q = np.linspace(bx0, bx1, cq["nx"] + 1), np.linspace(by0, by1, cq["nx"] + 1)
    kx, ky = ken["x"].to_numpy(), ken["y"].to_numpy()
    ixq = np.clip(np.searchsorted(xs_q, kx, "left") - 1, 0, cq["nx"] - 1)
    iyq = np.clip(np.searchsorted(ys_q, ky, "left") - 1, 0, cq["nx"] - 1)
    cnt_q = np.zeros((cq["nx"], cq["nx"]), int)
    np.add.at(cnt_q, (ixq, iyq), 1)
    area_q = np.array([[_box(xs_q[i], ys_q[j], xs_q[i + 1], ys_q[j + 1]).intersection(W).area
                        for j in range(cq["nx"])] for i in range(cq["nx"])])
    toca_q = area_q > 0
    a.igual(int(toca_q.sum()), cq["n_teselas"], "cuadrantes: las celdas que tocan Kennedy")
    a.cerca((bx1 - bx0) * (by1 - by0) / cq["nx"] ** 2 / 1e6, cq["area_celda_km2"],
            "cuadrantes: el área de una celda entera", 1e-9)
    dens_q = cnt_q[toca_q] / area_q[toca_q] * 1e6
    a.cerca(float(dens_q.max()), cq["intensidad_max_km2"],
            "cuadrantes: la intensidad máxima, conteo / área", 1e-6)
    a.cierto(abs(cq["intensidad_max_km2"] - cq["conteo_max"] / (W.area / 1e6 / cq["nx"] ** 2)) > 1,
             "cuadrantes: y no es conteo / (área de Kennedy / 64)",
             f"{cq['intensidad_max_km2']:.4f} contra {cq['conteo_max'] / (W.area / 1e6 / cq['nx'] ** 2):.4f}")

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
    maxs, sup0 = [], None
    for s in fam["sigmas_m"]:
        cr = kde_directa(px, py, s, xc, yc)
        e = borde_e(mask, dx, dy, s, nx, ny)
        sup = np.where((e > 0) & mask, cr / np.maximum(e, 1e-300), np.nan)
        maxs.append(float(np.nanmax(sup)) * 1e6)
        sup0 = sup if sup0 is None else sup0
    for i, s in enumerate(fam["sigmas_m"]):
        a.cerca(maxs[i], fam["max_km2"][i],
                f"familia: el máximo con sigma={s:.0f} m", TOL_SUP)
    # El simulador del módulo 2 rotula su eje «pasos ×√2»: siete anchos que
    # recorren un factor 8 en seis pasos iguales, 8^(1/6) = √2.
    sgm = np.asarray(fam["sigmas_m"], float)
    a.cierto(np.allclose(sgm[1:] / sgm[:-1], np.sqrt(2), rtol=1e-5)
             and abs(sgm[-1] / sgm[0] - fam["razon"]) < 1e-4 * fam["razon"],
             "familia: los anchos van en pasos de √2",
             " ".join(f"{v:.4f}" for v in sgm[1:] / sgm[:-1]))
    a.cierto(all(np.diff(maxs) < 0), "familia: el máximo cae al abrir el núcleo",
             " ".join(f"{v:.1f}" for v in maxs))
    a.cerca(100 * (maxs[0] - maxs[-1]) / maxs[0], fam["caida_pct"],
            "familia: la caída total, recalculada", TOL_SUP)
    a.igual(len(fam_csv), len(fam["sigmas_m"]), "familia: el CSV trae las siete")

    # LOS FOCOS DEL σ MÁS ESTRECHO SON GRUPOS (tercera revisión, 2026-10-27).
    # El módulo decía «colegios concretos»: una sede sola levanta
    # 1/(2 pi sigma^2), que no pasa del primer tramo de la leyenda, y el foco
    # más alto reúne varias. Las tres cifras, sin spatstat.
    fo = fam["foco"]
    a.cerca(fo["sigma_m"], fam["sigmas_m"][0], "foco: es el de la sigma más estrecha", 1e-12)
    a.cerca(1e6 / (2 * np.pi * fo["sigma_m"] ** 2), fo["pico_una_sede_km2"],
            "foco: lo que levanta una sede sola", 1e-9)
    esc = fam["escala"]
    a.cerca(esc[0] + (esc[1] - esc[0]) / 7, fo["primer_corte_km2"],
            "foco: el primer corte de la leyenda común", 1e-6)
    a.cerca(M["kennedy_familia"][0]["cortes"][1], fo["primer_corte_km2"],
            "foco: y es el que dibuja el mapa", 1e-6)
    iy0, ix0 = np.unravel_index(np.nanargmax(sup0), sup0.shape)
    a.igual(int(((px - xc[ix0]) ** 2 + (py - yc[iy0]) ** 2 <= fo["sigma_m"] ** 2).sum()),
            fo["sedes_a_un_sigma_del_maximo"], "foco: las sedes a un sigma del máximo")
    a.cierto(fo["pico_una_sede_km2"] < fo["primer_corte_km2"] and fo["sedes_a_un_sigma_del_maximo"] >= 3,
             "foco: una sede sola no se ve; el foco es un grupo",
             f"{fo['pico_una_sede_km2']:.2f} < {fo['primer_corte_km2']:.2f} por km², "
             f"{fo['sedes_a_un_sigma_del_maximo']} sedes")
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

    # LA REJILLA DE bw.ppl Y bw.CvL (tercera revisión, 2026-10-27). El cruce
    # que el módulo leía —ppl por encima de diggle en Kennedy, por debajo en
    # la ciudad— es de la rejilla de 16 anchos; con una fina, ppl queda por
    # debajo en las dos. Son validación cruzada: se auditan las propiedades
    # que la prosa afirma, no el valor.
    a.cierto(m3["ns_defecto"]["ppl"] == m3["ns_defecto"]["CvL"] == 16,
             "selectores: la rejilla por defecto es de 16 anchos",
             f"ppl {m3['ns_defecto']['ppl']}, CvL {m3['ns_defecto']['CvL']}")
    a.cierto(m3["ns_fino"] > 10 * m3["ns_defecto"]["ppl"], "selectores: la fina es mucho más fina",
             f"{m3['ns_fino']} anchos")
    sk, su = m3["kennedy"]["sigmas_m"], m3["urbana"]["sigmas_m"]
    a.cierto(sk["ppl"] > sk["diggle"] and su["ppl"] < su["diggle"],
             "selectores: con 16 anchos, ppl y diggle se cruzan",
             f"Kennedy {sk['ppl']:.0f} / {sk['diggle']:.0f}; ciudad {su['ppl']:.0f} / {su['diggle']:.0f}")
    fk, fu = m3["fino"]["kennedy"], m3["fino"]["urbana"]
    a.cierto(fk["ppl"] < sk["diggle"] and fu["ppl"] < su["diggle"],
             "selectores: con la fina, ppl queda debajo en las dos",
             f"Kennedy {fk['ppl']:.0f} / {sk['diggle']:.0f}; ciudad {fu['ppl']:.0f} / {su['diggle']:.0f}")
    a.cierto(all(v > 0 for d in (fk, fu) for v in d.values()), "selectores: los finos son positivos")
    # bw.scott(isotropic = TRUE) es la media geométrica de las dos
    # desviaciones típicas por n^(-1/6): fórmula cerrada, se recalcula.
    ux, uy_ = urb["x"].to_numpy(), urb["y"].to_numpy()
    for donde, (xx, yy) in (("kennedy", (px, py)), ("urbana", (ux, uy_))):
        iso = float(np.sqrt(np.std(xx, ddof=1) * np.std(yy, ddof=1)) * len(xx) ** (-1 / 6))
        a.cerca(iso, m3["scott_isotropico_m"][donde], f"selectores/{donde}: bw.scott isótropo", 1e-6)
    sel_iso = dict(su, scott=m3["scott_isotropico_m"]["urbana"])
    a.cerca(max(sel_iso.values()) / min(sel_iso.values()), m3["razon_urbana_scott_isotropico"],
            "selectores: la razón de la ciudad con el isótropo", 1e-9)

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
    # «¿En qué fracción de la ciudad son mayoría?» es el área con P > 0.5, no
    # la mediana: hasta el 2026-10-27 el módulo le asignaba esa pregunta a la
    # mediana. Recalculada sobre la superficie de arriba (sin corrección de
    # borde, que en un cociente con la de por defecto se cancela).
    a.cerca(100 * float(np.nanmean(prop[mask_c & np.isfinite(prop)] > 0.5)), m6["pct_area_mayoria"],
            "riesgo: la fracción del área donde lo oficial es mayoría", 2.0)
    a.cierto(abs(m6["pct_area_mayoria"] - 100 * m6["p_mediana"]) > 5,
             "riesgo: y no es la mediana leída como porcentaje",
             f"{m6['pct_area_mayoria']:.1f} % contra {100 * m6['p_mediana']:.1f}")
    # El contraste que el pie del mapa de sectores afirma: norte contra sur,
    # por tercios de la caja de la ventana urbana.
    uy = urb["y"].to_numpy()
    ry0, ry1 = v_urb.bounds[1], v_urb.bounds[3]
    t_sur, t_norte = ry0 + (ry1 - ry0) / 3, ry0 + 2 * (ry1 - ry0) / 3
    a.cerca(100 * float(ofi[uy < t_sur].mean()), m6["pct_oficiales_tercio_sur"],
            "riesgo: las oficiales del tercio sur, recontadas", 1e-6)
    a.cerca(100 * float(ofi[uy >= t_norte].mean()), m6["pct_oficiales_tercio_norte"],
            "riesgo: y las del tercio norte", 1e-6)
    a.cierto(m6["pct_oficiales_tercio_sur"] > m6["pct_oficiales_tercio_norte"],
             "riesgo: lo oficial pesa más en el sur, como dice el pie",
             f"{m6['pct_oficiales_tercio_sur']:.1f} % contra {m6['pct_oficiales_tercio_norte']:.1f} %")
    a.cierto(m6["orientacion_verificada"] > m6["prop_global"],
             "riesgo: donde el mapa es máximo dominan los oficiales",
             f"{100*m6['orientacion_verificada']:.0f} % de los 50 vecinos")
    # LA GUARDA SOBRE EL MAPA AL REVÉS (M6-4 de la tercera revisión). Con los
    # niveles por defecto `relrisk` pinta P(privado) = 1 − P(oficial), y su
    # máximo NO es un sitio: vale 1, a nueve decimales, en todos los píxeles sin
    # una oficial a la vista del núcleo. La primera versión de la guarda tomaba
    # el primer empate y publicó un 10 % que era el orden de la matriz; con la
    # rejilla de la ciudad salía un 4 %. Aquí la meseta se rehace con la suma
    # directa —donde P(oficial) no llega a la tolerancia— y se recorre entera.
    gd = m6.get("guarda")
    ux_, uy_ = urb["x"].to_numpy(), urb["y"].to_numpy()

    def vecinos_oficiales(iy, ix):
        d_m = np.hypot(ux_ - xcc[ix], uy_ - ycc[iy])
        return float(ofi[np.argsort(d_m, kind="stable")[:50]].mean())

    # Un auditor no se muere ante un ráster roto: si la superficie recalculada
    # se queda sin un solo valor (una caja desordenada, por ejemplo), lo dice.
    if (a.cierto(isinstance(gd, dict) and {"fijado", "defecto", "tolerancia_meseta"} <= set(gd),
                 "riesgo: está la guarda sobre los dos mapas")
            and a.cierto(bool(np.isfinite(prop).any()), "riesgo: la superficie recalculada tiene valores")):
        iys, ixs = np.nonzero(np.isfinite(prop) & (prop <= gd["tolerancia_meseta"]))
        fr = [vecinos_oficiales(i, j) for i, j in zip(iys, ixs)]
        a.cierto(len(fr) >= 2 and gd["defecto"]["pixeles"] >= 2,
                 "riesgo: el máximo del mapa al revés es una meseta",
                 f"{len(fr)} píxeles aquí, {gd['defecto']['pixeles']} en R")
        if fr:
            # Dos vecinos de cincuenta: la suma directa y el binado de spatstat
            # no tienen por qué dejar fuera de la meseta los mismos píxeles.
            a.igual(min(fr), gd["defecto"]["min"], "riesgo: la meseta, su vecindario menos oficial", 0.041)
            a.igual(max(fr), gd["defecto"]["max"], "riesgo: y el más oficial", 0.041)
        a.cierto(gd["defecto"]["max"] < m6["prop_global"] < gd["fijado"]["min"],
                 "riesgo: la guarda separa los dos mapas, empate a empate",
                 f"hasta {100*gd['defecto']['max']:.0f} % con los niveles por defecto, "
                 f"desde {100*gd['fijado']['min']:.0f} % fijados")
        iy_M, ix_M = np.unravel_index(np.nanargmax(prop), prop.shape)
        a.igual(vecinos_oficiales(iy_M, ix_M), m6["orientacion_verificada"],
                "riesgo: la guarda, recalculada sobre P(oficial)", 0.041)
        a.cierto(gd["fijado"]["pixeles"] == 1
                 and gd["fijado"]["min"] == gd["fijado"]["max"] == m6["orientacion_verificada"],
                 "riesgo: el máximo de P(oficial) es un solo sitio",
                 f"{gd['fijado']['pixeles']} píxel(es), de {gd['fijado']['min']} a {gd['fijado']['max']}")

    # LA REJILLA DE P(oficial), EN LOS DOS LADOS DE LA CELDA (M6-7 de la tercera
    # revisión, 2026-10-27). Hasta entonces salía con la de por defecto de
    # relrisk —128 x 128 sobre una caja alta—: σ cabía 2.3 veces en la
    # vertical, y nada lo miraba, porque las celdas de los demás mapas son
    # cuadradas y bastaba con el ancho.
    fam_celdas = D["m2"]["familia"]["celdas_por_sigma"]
    a.cierto(sg / max(dxc, dyc) >= fam_celdas,
             "riesgo: P(oficial) cumple las tres celdas en los dos lados",
             f"{sg / max(dxc, dyc):.2f} celdas en el lado largo ({dxc:.0f} × {dyc:.0f} m)")
    a.cierto(nxc == M["ciudad_oferta"]["nx"] and nyc == M["ciudad_oferta"]["ny"],
             "riesgo: con la rejilla de los mapas del módulo 5",
             f"{nxc} × {nyc} contra {M['ciudad_oferta']['nx']} × {M['ciudad_oferta']['ny']}")
    rj6, rd = m6["rejilla"], m6["rejilla_por_defecto"]
    a.cierto(rj6["nx"] == nxc and rj6["ny"] == nyc, "riesgo: la rejilla declarada es la del ráster",
             f"{rj6['nx']} × {rj6['ny']}")
    a.cerca(rj6["celda_m"], max(dxc, dyc), "riesgo: su celda, el lado largo", 1e-6)
    a.cerca(rj6["celdas_por_sigma"], sg / max(dxc, dyc), "riesgo: sus celdas por σ, recalculadas", 1e-6)
    caja6 = mg["caja"]
    a.cerca(rd["celda_x_m"], (caja6[2] - caja6[0]) / rd["nx"], "riesgo: la celda por defecto, de ancho", 1e-6)
    a.cerca(rd["celda_y_m"], (caja6[3] - caja6[1]) / rd["ny"], "riesgo: y de alto", 1e-6)
    a.cerca(rd["celdas_por_sigma"], sg / max(rd["celda_x_m"], rd["celda_y_m"]),
            "riesgo: las celdas por σ de la rejilla por defecto", 1e-6)
    a.cierto(rd["celdas_por_sigma"] < fam_celdas, "riesgo: y esa rejilla incumple la regla",
             f"{rd['celdas_por_sigma']:.2f} celdas")
    # Lo que la rejilla por defecto daba, recalculado por suma directa sobre
    # ella, y la frase del módulo: que casi no se nota y que el área de mayoría
    # redondea igual con las dos.
    xd, yd, _, _ = rejilla_de(caja6, rd["nx"], rd["ny"])
    Xd, Yd = np.meshgrid(xd, yd)
    mask_d = gpd.GeoSeries(gpd.points_from_xy(Xd.ravel(), Yd.ravel())).within(
        v_urb).to_numpy().reshape(rd["ny"], rd["nx"])
    ko_d = kde_directa(ux_[ofi], uy_[ofi], sg, xd, yd)
    kt_d = ko_d + kde_directa(ux_[~ofi], uy_[~ofi], sg, xd, yd)
    prop_d = np.where((kt_d > 0) & mask_d, ko_d / np.maximum(kt_d, 1e-300), np.nan)
    if a.cierto(bool(np.isfinite(prop_d).any()), "riesgo: la superficie por defecto tiene valores"):
        a.igual(float(np.nanmedian(prop_d)), rd["p_mediana"], "riesgo: la mediana por defecto, recalculada", 0.02)
        a.igual(100 * float(np.nanmean(prop_d[np.isfinite(prop_d)] > 0.5)), rd["pct_area_mayoria"],
                "riesgo: y su área de mayoría", 2.0)
    a.cierto(abs(rd["p_mediana"] - m6["p_mediana"]) < 0.005
             and round(rd["pct_area_mayoria"], 1) == round(m6["pct_area_mayoria"], 1),
             "riesgo: con las dos rejillas casi no se nota, como dice",
             f"mediana {rd['p_mediana']:.4f} y {m6['p_mediana']:.4f}, "
             f"mayoría {rd['pct_area_mayoria']:.1f} y {m6['pct_area_mayoria']:.1f} %")
    ch = D["m6"]["chorley"]
    a.igual(ch["casos"] + ch["controles"], 1036, "riesgo: chorley suma sus 1 036 puntos")
    a.cerca(ch["casos"] / (ch["casos"] + ch["controles"]), ch["prop_global"],
            "riesgo: la proporción de casos de chorley", 1e-9)
    a.cierto(ch["orientacion_verificada"] > ch["prop_global"],
             "riesgo: y su mapa también pinta los casos",
             f"{100*ch['orientacion_verificada']:.0f} % de los vecinos")
    # El máximo de chorley se publica con los datos que tiene alrededor: la
    # prosa dice que no tiene un solo punto a dos anchos de banda y que cae
    # junto al borde. No hay chorley en Python; se comprueba lo que se puede
    # sin él: que las cifras digan lo que la frase dice y sean coherentes.
    a.igual(ch["maximo_puntos_cerca"], 0, "riesgo: el máximo de chorley no tiene puntos a dos anchos")
    a.cerca(ch["maximo_radio_km"], 2 * ch["sigma"], "riesgo: y esos dos anchos son dos sigmas", 1e-12)
    a.cierto(0 <= ch["maximo_dist_borde_m"] < 1000 * ch["sigma"],
             "riesgo: el máximo de chorley, junto al borde",
             f"{ch['maximo_dist_borde_m']:.0f} m")
    a.cierto((ch["pct_area_mayoria"] == 0) == (ch["p_max"] < 0.5),
             "riesgo: la laringe no es mayoría en ningún sitio",
             f"{ch['pct_area_mayoria']} % con máximo {ch['p_max']:.4f}")

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

    # LA CURVA Y DÓNDE CAEN SUS EXTREMOS (tercera revisión, 2026-10-27). El
    # módulo decía que el máximo y el mínimo viven «casi siempre» en los
    # extremos; lo que se sostiene es que el mínimo cae en una cola en las
    # tres, y el máximo solo en una. La curva publicada son cien nodos
    # interpolados de la de spatstat: no puede salirse de sus extremos.
    curvas = (("bei/elev", m7["bei"]["elevacion"]), ("bei/grad", m7["bei"]["pendiente"]),
              ("bogotá", m7["bogota"]["curva"]))
    for etq, c in curvas:
        cz, cr_ = np.asarray(c["curva_z"], float), np.asarray(c["curva_rho"], float)
        # Con la holgura de las seis cifras significativas de `r6`, que en
        # la elevación de bei (≈150 m, paso de 0.4 m) son 1e-4 m por nodo.
        a.cierto(len(cz) == len(cr_) == 100
                 and np.allclose(np.diff(cz), (cz[-1] - cz[0]) / 99, rtol=0, atol=2e-5 * np.abs(cz).max()),
                 f"rhohat/{etq}: cien nodos equiespaciados")
        a.cierto(cr_.max() <= c["rho_max"] * (1 + 1e-5) and cr_.min() >= c["rho_min"] * (1 - 1e-5),
                 f"rhohat/{etq}: la curva no rebasa sus extremos")
        a.cierto(cz[0] - 1e-6 * abs(cz[0]) <= c["z_del_maximo"] <= cz[-1] * (1 + 1e-6)
                 and cz[0] - 1e-6 * abs(cz[0]) <= c["z_del_minimo"] <= cz[-1] * (1 + 1e-6),
                 f"rhohat/{etq}: sus extremos caen dentro del rango")
        for cual in ("maximo", "minimo"):
            z = c[f"z_del_{cual}"]
            a.igual(int(c["bulto_desde"] <= z <= c["bulto_hasta"]), int(c[f"{cual}_en_el_bulto"]),
                    f"rhohat/{etq}: ¿el {cual} en el bulto?")
    a.cierto(all(int(c["minimo_en_el_bulto"]) == 0 for _, c in curvas),
             "rhohat: el mínimo cae en una cola en las tres")
    a.igual(sum(int(c["maximo_en_el_bulto"]) for _, c in curvas), 2,
            "rhohat: el máximo, dentro del bulto en dos de tres")
    # El centro de masa de las sedes sale de las sedes; el centroide de la
    # ventana, no. El módulo publica la lección con los dos.
    cv = m7["bogota"]["centroide_ventana"]
    cw = v_urb.centroid
    a.cerca(float(np.hypot(cw.x - cx, cw.y - cy)), cv["distancia_al_centro_de_masa_m"],
            "rhohat: del centroide de la ventana al de las sedes", 1e-6)
    a.cierto(cv["razon"] / cv["razon_bulto"] > 1
             and cv["razon_bulto"] < m7["bei"]["elevacion"]["razon_bulto"],
             "rhohat: con el centroide, la lección sobrevive",
             f"{cv['razon']:.1f} en todo el rango, {cv['razon_bulto']:.2f} en el bulto")

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

    # -----------------------------------------------------------------
    a.titulo("8b · la verosimilitud por dentro (M3, 2026-09-24)")
    # -----------------------------------------------------------------
    # El módulo escribe ℓ = Σ log λ(x_i) − ∫λ, dice que ppm no pasa el
    # homogéneo por la cuadratura, que forzado sale n/Σw, que los pesos
    # pierden ciudad en teselas del borde sin ningún punto, y que esa
    # ciudad perdida —no el modelo— es lo que mueve el AIC. Aquí se rehace
    # todo lo que se puede rehacer sin spatstat: las teselas con shapely,
    # la suma de logaritmos con los coeficientes publicados y la integral
    # con una malla propia. Lo que es identidad se exige exacto.
    h8 = m8["homogeneo"]
    fz = m8.get("forzado")
    cp = m8.get("comparacion")
    CLAVES_FILA = ("rejilla_pesos", "pixeles", "teselas_tocan", "teselas_vacias",
                   "sin_contar_km2", "suma_log", "logver_ppm", "integral_exacta",
                   "logver_exacta")
    faltan = [k for k in ("fitter", "n", "logver", "aic") if k not in h8]
    faltan += [k for k in ("forzado", "comparacion") if not isinstance(m8.get(k), dict)]
    faltan += [k for k in ("rango_logver_ppm", "rango_logver_exacta")
               if k not in m8["cuadratura"]]
    faltan += sorted({k for z in tab for k in CLAVES_FILA if k not in z})
    if len(tab) != 4:
        faltan.append("cuatro cuadraturas")
    a.cierto(not faltan, "ppm: el módulo 8 publica su verosimilitud por dentro",
             ", ".join(faltan))
    if not faltan:
        n_u = len(urb)
        area_w = v_urb.area
        a.igual(n_u, h8["n"], "ppm: n son las sedes del patrón urbano", 0)
        a.cierto(h8["fitter"] == "exact",
                 "ppm: el homogéneo sale de la fórmula cerrada", str(h8["fitter"]))
        a.igual(n_u * np.log(n_u / area_w) - n_u, h8["logver"],
                "ppm: el ℓ homogéneo es n·log(n/|W|) − n", 1e-4)
        a.igual(-2 * h8["logver"] + 2, h8["aic"], "ppm: el AIC homogéneo es −2ℓ + 2", 1e-6)

        # Las teselas, sin spatstat. La rejilla de pesos parte la caja de la
        # ventana en `rejilla` × `rejilla`; spatstat pone el ficticio de cada
        # celda en los píxeles de ciudad de una máscara de `pixeles` de lado
        # (`cellmiddles`), más las esquinas de la caja que caigan dentro. Una
        # tesela que toca la ciudad y no tiene píxel ni sede no la cuenta
        # nadie: su área es exactamente lo que les falta a los pesos.
        import shapely
        from shapely.geometry import box as _caja
        x0, y0, x1, y1 = v_urb.bounds
        ux, uy = urb["x"].to_numpy(), urb["y"].to_numpy()

        def teselas(nt, npx):
            dx, dy = (x1 - x0) / nt, (y1 - y0) / nt
            cajas = np.array([_caja(x0 + i * dx, y0 + j * dy, x0 + (i + 1) * dx, y0 + (j + 1) * dy)
                              for j in range(nt) for i in range(nt)])
            ar = shapely.area(shapely.intersection(cajas, v_urb))

            def celda(x, y):
                i = np.clip(np.floor((x - x0) / dx).astype(int), 0, nt - 1)
                j = np.clip(np.floor((y - y0) / dy).astype(int), 0, nt - 1)
                return j * nt + i
            px = x0 + (np.arange(npx) + 0.5) * (x1 - x0) / npx
            py = y0 + (np.arange(npx) + 0.5) * (y1 - y0) / npx
            PX, PY = np.meshgrid(px, py)
            PX, PY = PX.ravel(), PY.ravel()
            dentro = shapely.contains_xy(v_urb, PX, PY)
            llena = np.zeros(nt * nt, bool)
            llena[celda(PX[dentro], PY[dentro])] = True
            llena[celda(ux, uy)] = True
            ex = np.array([x0, x1, x0, x1]); ey = np.array([y0, y0, y1, y1])
            en = shapely.contains_xy(v_urb, ex, ey)
            llena[celda(ex[en], ey[en])] = True
            vac = (ar > 0) & ~llena
            return int((ar > 0).sum()), int(vac.sum()), float(ar[vac].sum())

        # La integral bien hecha, con una malla propia: |W| por la media de
        # λ̂ en los centros de píxel que caen en la ciudad. Con 2048 de lado
        # oscila unas centésimas, como la de R: tolerancia de 0,05 sedes.
        NM = 2048
        mx = x0 + (np.arange(NM) + 0.5) * (x1 - x0) / NM
        my = y0 + (np.arange(NM) + 0.5) * (y1 - y0) / NM
        MX, MY = np.meshgrid(mx, my)
        MX, MY = MX.ravel(), MY.ravel()
        md = shapely.contains_xy(v_urb, MX, MY)
        d_malla = np.hypot(MX[md] - cx, MY[md] - cy)

        for z in tab:
            nd = z["nd"]
            etq = f"cuadratura nd={nd}"
            sano = (isinstance(z["rejilla_pesos"], int) and isinstance(z["pixeles"], int)
                    and 0 < z["rejilla_pesos"] <= z["pixeles"] <= 1000)
            if a.cierto(sano, f"{etq}: rejilla y píxeles con sentido",
                        f"{z['rejilla_pesos']} / {z['pixeles']}"):
                toc, vac, ar_v = teselas(z["rejilla_pesos"], z["pixeles"])
                a.igual(toc, z["teselas_tocan"], f"{etq}: teselas que tocan la ciudad", 0)
                a.igual(vac, z["teselas_vacias"], f"{etq}: teselas que nadie cuenta", 0)
                a.igual(ar_v / 1e6, z["sin_contar_km2"], f"{etq}: la ciudad sin contar", 1e-6)
            sl = float(np.sum(z["intercepto"] + z["pendiente"] * dist))
            a.igual(sl, z["suma_log"], f"{etq}: la suma de log λ en las sedes", 0.01)
            a.igual(z["suma_log"] - n_u, z["logver_ppm"],
                    f"{etq}: el ℓ de ppm es esa suma menos n", 1e-6)
            a.igual(-2 * z["logver_ppm"] + 4, z["aic"], f"{etq}: el AIC es −2ℓ + 2k", 1e-6)
            lam = np.exp(z["intercepto"] + z["pendiente"] * d_malla)
            a.igual(area_w * float(lam.mean()), z["integral_exacta"],
                    f"{etq}: la integral bien hecha", 0.05)
            a.igual(z["suma_log"] - z["integral_exacta"], z["logver_exacta"],
                    f"{etq}: el ℓ bien hecho es la suma menos ella", 1e-6)

        llp = [z["logver_ppm"] for z in tab]
        llx = [z["logver_exacta"] for z in tab]
        sinc = [z["sin_contar_km2"] for z in tab]
        a.igual(max(llp) - min(llp), m8["cuadratura"]["rango_logver_ppm"],
                "cuadratura: lo que se mueve el ℓ de ppm", 1e-6)
        a.igual(max(llx) - min(llx), m8["cuadratura"]["rango_logver_exacta"],
                "cuadratura: lo que se mueve el ℓ bien hecho", 1e-6)
        a.cierto(max(llx) - min(llx) < 0.1 and max(llp) - min(llp) > 20 * (max(llx) - min(llx)),
                 "cuadratura: bien hecha, los cuatro son el mismo modelo",
                 f"{max(llx) - min(llx):.4f} contra {max(llp) - min(llp):.4f}")
        a.cierto(all(not (sinc[i] > sinc[j] + 1e-6) or aics[i] < aics[j]
                     for i in range(4) for j in range(4)),
                 "cuadratura: el AIC sigue a la ciudad sin contar")
        a.cierto(abs(sinc[1] - sinc[2]) < 1e-9
                 and tab[1]["rejilla_pesos"] == tab[2]["rejilla_pesos"]
                 and tab[1]["pixeles"] == tab[2]["pixeles"],
                 "cuadratura: la 2.ª y la 3.ª pierden la misma ciudad")
        a.cierto(int(np.argmin(sinc)) == 3 and int(np.argmax(aics)) == 3,
                 "cuadratura: la última pierde menos y da el AIC más alto")
        a.cierto(aics[1] < aics[0] and abs(aics[2] - aics[1]) < 0.1 and aics[3] > aics[2],
                 "cuadratura: el AIC baja, se queda quieto y vuelve a subir")
        a.cierto(all(z["integral_exacta"] > n_u for z in tab),
                 "cuadratura: todas ponen sedes esperadas de más")

        # El homogéneo forzado por la cuadratura por defecto
        t100 = tab[1]
        a.igual(t100["nd"], m8["cuadratura"]["defecto_nd"],
                "ppm: la segunda fila es la cuadratura por defecto", 0)
        a.cierto(fz.get("fitter") == "glm", "ppm: forzado, el homogéneo pasa por glm",
                 str(fz.get("fitter")))
        a.cerca(area_w / 1e6, fz["area_km2"], "ppm: el área de la ventana en km²", 1e-9)
        a.cerca(fz["area_km2"] - t100["sin_contar_km2"], fz["suma_pesos_km2"],
                "ppm: los pesos suman el área menos lo sin contar", 1e-9)
        a.cerca(n_u / fz["suma_pesos_km2"], fz["lambda_km2"],
                "ppm: forzado, la EMV es n entre los pesos", 1e-8)
        a.igual(100 * (fz["lambda_km2"] / h8["lambda_km2"] - 1), fz["exceso_pct"],
                "ppm: lo que sube la intensidad forzada", 1e-6)
        a.igual(n_u * np.log(n_u / (fz["suma_pesos_km2"] * 1e6)) - n_u, fz["logver"],
                "ppm: el ℓ forzado es n·log(n/Σw) − n", 1e-4)
        a.igual(-2 * fz["logver"] + 2, fz["aic"], "ppm: el AIC forzado es −2ℓ + 2", 1e-6)

        # La comparación de la nota: constante contra distancia
        a.igual(h8["aic"] - t100["aic"], cp["gana_distancia_ppm"],
                "comparación: lo que gana la distancia por ppm", 1e-6)
        a.igual(-2 * t100["logver_exacta"] + 4, cp["aic_distancia_exacto"],
                "comparación: el AIC bien hecho de la distancia", 1e-6)
        a.igual(cp["aic_distancia_exacto"] - h8["aic"], cp["gana_constante_exacta"],
                "comparación: lo que gana el constante, bien hecho", 1e-6)
        a.igual(t100["aic"] - fz["aic"], cp["gana_constante_misma"],
                "comparación: y con la misma cuadratura", 1e-6)
        a.cierto(cp["gana_distancia_ppm"] > 10,
                 "comparación: por ppm, la distancia gana con holgura",
                 f"{cp['gana_distancia_ppm']:.2f} puntos")
        a.cierto(0 < cp["gana_constante_exacta"] < 2 and 0 < cp["gana_constante_misma"] < 2,
                 "comparación: bien hechas, empatan a favor del constante",
                 f"{cp['gana_constante_exacta']:.3f} y {cp['gana_constante_misma']:.3f}")

        # LA EMV CON LA INTEGRAL BIEN HECHA (M8-3): maximizada, no evaluada en
        # los coeficientes de una cuadratura. Dado el coeficiente, el intercepto
        # tiene forma cerrada (la derivada respecto de él es n menos la
        # integral), así que basta una búsqueda en una dimensión, sobre la
        # misma malla de la integral de arriba.
        ex = m8["cuadratura"].get("emv_exacta")
        if a.cierto(isinstance(ex, dict) and all(k in ex for k in ("pendiente", "logver", "aic", "pendiente_en_ee"))
                    and "gana_constante_exacta_max" in cp, "ppm: el módulo 8 publica la EMV exacta"):
            from scipy.optimize import minimize_scalar
            s_d = float(np.sum(dist))

            def menos_perfil(b1):
                b0 = np.log(n_u) - np.log(area_w * float(np.mean(np.exp(b1 * d_malla))))
                return -(n_u * b0 + b1 * s_d - n_u)
            o = minimize_scalar(menos_perfil, bounds=(-1e-4, 1e-4), method="bounded",
                                options={"xatol": 1e-13})
            a.cerca(o.x, ex["pendiente"], "EMV exacta: la pendiente que la maximiza", 0.005)
            a.igual(-o.fun, ex["logver"], "EMV exacta: su log-verosimilitud", 0.05)
            a.igual(-2 * ex["logver"] + 4, ex["aic"], "EMV exacta: su AIC es −2ℓ + 2k", 1e-6)
            a.cerca(abs(ex["pendiente"] - t100["pendiente"]) / t100["ee_pendiente"], ex["pendiente_en_ee"],
                    "EMV exacta: a cuántos e.e. de la de por defecto", 1e-4)
            a.cierto(ex["pendiente"] < min(pend), "EMV exacta: fuera del abanico de las cuatro",
                     f"{ex['pendiente']:.4g} contra {min(pend):.4g}")
            a.cierto(ex["logver"] >= max(llx) - 1e-6, "EMV exacta: supera a las cuatro ℓ bien hechas")
            a.igual(ex["aic"] - h8["aic"], cp["gana_constante_exacta_max"],
                    "comparación: el empate, con la EMV exacta", 1e-6)
            a.cierto(0 < cp["gana_constante_exacta_max"] < cp["gana_constante_exacta"],
                     "comparación: maximizada, el empate se estrecha",
                     f"{cp['gana_constante_exacta_max']:.3f} contra {cp['gana_constante_exacta']:.3f}")
        z9 = D["m9"].get("distancia", {}).get("z") or []
        a.cierto(len(z9) == 2 and abs(z9[1]) < NormalDist().inv_cdf(0.975),
                 "comparación: la z del módulo 9 tampoco ve la distancia",
                 f"{z9[1]:.2f}" if len(z9) == 2 else "sin z")

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
    # EL TRAMO, NO EL UMBRAL. El módulo publicaba solo el primer r y la
    # prosa lo leía como una cola hasta el final del barrido. Se comprueba
    # el otro extremo, que el tramo sea contiguo —la prosa lo cuenta como
    # un intervalo— y que después la curva se quede dentro.
    a.cerca(float(r[dentro_r][fuera[dentro_r]].max()), m10["ultimo_r_fuera_m"],
            "envolvente: el último r que se sale", 1e-6)
    i_fuera = np.flatnonzero(fuera[dentro_r])
    a.cierto(bool(np.all(np.diff(i_fuera) == 1)),
             "envolvente: el tramo de fuera es contiguo")
    a.igual(int(dentro_r.sum()) - (int(i_fuera.max()) + 1),
            m10["nodos_dentro_tras_el_tramo"],
            "envolvente: los nodos dentro tras el tramo")
    a.cierto(m10["ultimo_r_fuera_m"] < m10["r_max_m"],
             "envolvente: vuelve dentro antes del fin del barrido",
             f"{m10['ultimo_r_fuera_m']:.2f} < {m10['r_max_m']:.2f}")
    a.cierto(m10["correccion"] == "translate",
             "envolvente: la corrección viaja en el dato", m10["correccion"])

    # LA BANDA LEÍDA ENTERA (M4 de la segunda revisión). El módulo leía el
    # nivel puntual como la seguridad de la curva entera. Las 999 curvas no
    # viajan —pesarían 4 MB—, así que lo que se comprueba es que cada cifra
    # sea la cuenta que dice ser y que diga lo que la prosa afirma: más
    # salidas que el nivel puntual, y más cuantos más radios se miran.
    ts = m10["tasa_salida"]
    a.igual(ts["nsim"], m10["nsim"], "envolvente: la tasa usa sus simulaciones")
    a.cerca(100 * ts["fuera"] / ts["nsim"], ts["pct"],
            "envolvente: la tasa es el % de sus salidas", 1e-6)
    a.cerca(100 * ts["fuera_simulador"] / ts["nsim"], ts["pct_simulador"],
            "envolvente: y la del simulador, la de las suyas", 1e-6)
    a.igual(ts["nodos_r_simulador"], int(dentro_r.sum()),
            "envolvente: el simulador mira los r de la curva")
    a.cierto(ts["nodos_r"] > ts["nodos_r_simulador"],
             "envolvente: spatstat mira más radios que el lienzo",
             f"{ts['nodos_r']} > {ts['nodos_r_simulador']}")
    a.cerca(ts["pct"] / m10["nivel_puntual_pct"], ts["veces_el_nivel"],
            "envolvente: cuántas veces el nivel puntual", 1e-6)
    a.cierto(ts["pct"] > ts["pct_simulador"] > m10["nivel_puntual_pct"],
             "envolvente: entera se cruza más que radio a radio",
             f"{ts['pct']:.2f} > {ts['pct_simulador']:.2f} > {m10['nivel_puntual_pct']:.2f}")
    tg = m10["test_global"]
    a.cerca(1 / (m10["nsim"] + 1), tg["p_minimo"], "envolvente: el p mínimo es 1/(nsim+1)", 1e-12)
    a.cerca(tg["dclf_p"], tg["p_minimo"], "envolvente: el DCLF da el p mínimo", 1e-12)
    a.cerca((1 + tg["mad_superan"]) / (m10["nsim"] + 1), tg["mad_p"],
            "envolvente: el p del MAD cuenta las que lo superan", 1e-12)
    a.cierto(tg["p_minimo"] < tg["mad_p"] < 0.05,
             "envolvente: el MAD rechaza sin llegar al mínimo", f"p = {tg['mad_p']:g}")
    # Dónde se desvía más la observada, releído en la rejilla publicada:
    # tiene que caer a menos de un paso de la r que declara, y las dos
    # dentro del tramo; las que la superan, pasado él.
    mm = np.array(c["mmean"])
    r_peor = float(r[np.argmax(np.abs(obs - mm))])
    a.cierto(abs(r_peor - tg["r_mad_observada_m"]) <= float(np.diff(r).max()),
             "envolvente: la peor desviación, a un paso de la r",
             f"{r_peor:.1f} contra {tg['r_mad_observada_m']:.1f}")
    a.cierto(tg["r_mad_observada_m"] <= m10["ultimo_r_fuera_m"] < tg["r_min_mad_superan_m"] <= m10["r_max_m"],
             "envolvente: peor dentro del tramo, las otras fuera",
             f"{tg['r_mad_observada_m']:.0f} ≤ {m10['ultimo_r_fuera_m']:.0f} < {tg['r_min_mad_superan_m']:.0f}")

    # LA OTRA λ (tercera revisión, 2026-10-27). La publicada divide por un
    # núcleo, no por el modelo; la del modelo se publica al lado. Releída de su
    # propia curva: el tramo, su porcentaje y que llegue más lejos.
    lm = m10["lambda_modelo"]
    cm = lm["curva"]
    obs_m, lo_m, hi_m = (np.array(cm[k], dtype=float) for k in ("obs", "lo", "hi"))
    if a.cierto(len(obs_m) == len(lo_m) == len(hi_m) == len(cm["mmean"]) == len(r),
                "envolvente λ modelo: una curva por cada r de la otra"):
        fm = ((obs_m > hi_m) | (obs_m < lo_m))[dentro_r]
        a.cerca(100 * fm.mean(), lm["pct_r_fuera_de_banda"], "envolvente λ modelo: el % fuera, releído", 1e-9)
        a.cerca(float(r[dentro_r][fm].max()), lm["ultimo_r_fuera_m"],
                "envolvente λ modelo: el último r fuera, releído", 1e-6)
    a.cierto(lm["ultimo_r_fuera_m"] > m10["ultimo_r_fuera_m"],
             "envolvente: con λ del modelo el exceso llega más lejos",
             f"{lm['ultimo_r_fuera_m']:.0f} contra {m10['ultimo_r_fuera_m']:.0f} m")
    a.cierto(lm["dclf_p"] < 0.05, "envolvente λ modelo: el DCLF también rechaza", f"p = {lm['dclf_p']:g}")
    a.cierto(500 < m10["lambda_nucleo_sigma_m"] < 20000,
             "envolvente: el núcleo por defecto mide kilómetros",
             f"{m10['lambda_nucleo_sigma_m']:.0f} m")
    # EL VEREDICTO, ACOTADO A LO QUE SE CONTRASTÓ. Un polinomio de grado g en
    # dos coordenadas tiene (g+1)(g+2)/2 coeficientes; el de grado bajo sigue
    # rechazando y el de grado alto ya no.
    tf = m10["tendencia_flexible"]
    for t in tf:
        a.igual(t["coeficientes"], (t["grado"] + 1) * (t["grado"] + 2) // 2,
                f"veredicto: coeficientes del grado {t['grado']}")
    a.cierto(tf[0]["dclf_p"] < 0.05 <= tf[-1]["dclf_p"],
             "veredicto: el grado bajo rechaza y el alto no",
             f"grado {tf[0]['grado']}: p = {tf[0]['dclf_p']:g}; grado {tf[-1]['grado']}: p = {tf[-1]['dclf_p']:g}")
    a.cierto("plano" in m10["veredicto"] and "intensidad variable no explica" not in m10["veredicto"],
             "veredicto: dice «un plano», no «la intensidad variable»", m10["veredicto"])

    # -----------------------------------------------------------------
    # LA HIPÓTESIS DE LA MANZANA, CON LO QUE EL DATO MIDE (R16 de la tercera
    # revisión): qué fracción de las sedes tiene otra a menos de 100 m. Las
    # simulaciones del plano no se rehacen aquí; se exige que el patrón quede
    # muy por encima de ellas, que es lo que el módulo dice.
    v100 = m10.get("vecinos_100m")
    if a.cierto(isinstance(v100, dict), "envolvente: publica los vecinos a menos de 100 m"):
        from scipy.spatial import cKDTree
        xy_u = np.c_[urb["x"].to_numpy(), urb["y"].to_numpy()]
        d_nn = cKDTree(xy_u).query(xy_u, k=2)[0][:, 1]
        a.cerca(100 * float(np.mean(d_nn < v100["radio_m"])), v100["pct_patron"],
                "envolvente: sedes con otra a menos de 100 m", 1e-9)
        a.cierto(v100["pct_patron"] > v100["pct_plano_media"] + 5 * v100["pct_plano_sd"],
                 "envolvente: muy por encima de lo que da el plano",
                 f"{v100['pct_patron']:.1f} % contra {v100['pct_plano_media']:.1f} (sd {v100['pct_plano_sd']:.1f})")

    a.titulo("10 · Conglomerado, y el Hawkes recalculado")
    # -----------------------------------------------------------------
    m11 = D["m11"]
    a.igual(len(m11["ajustes"]), 6, "kppm: los tres modelos por las dos correcciones")

    # EL «VALLE» (tercera revisión, 2026-10-27), recalculado desde los
    # parámetros publicados: la K entera de los dos Thomas casi coincide porque
    # las dos llevan pi r^2; el exceso no.
    vl = m11["valle"]
    pa = {(x["modelo"], x["correccion"]): x["parametros"] for x in m11["ajustes"]}
    ki, si = pa[("Thomas", "iso")]["kappa"], pa[("Thomas", "iso")]["scale"]
    kt, st = pa[("Thomas", "translate")]["kappa"], pa[("Thomas", "translate")]["scale"]

    def k_thomas(rr, kap, esc):
        return np.pi * rr ** 2 + (1 - np.exp(-rr ** 2 / (4 * esc ** 2))) / kap

    rv = np.array(vl["r_m"], dtype=float)
    ka, kb = k_thomas(rv, ki, si), k_thomas(rv, kt, st)
    for i, rr in enumerate(rv):
        a.cerca(100 * abs(kb[i] - ka[i]) / ka[i], vl["k_dif_pct"][i],
                f"valle: la diferencia de las K enteras a {rr:.0f} m", 1e-6)
        a.cerca(100 * abs((kb[i] - np.pi * rr ** 2) / (ka[i] - np.pi * rr ** 2) - 1), vl["exceso_dif_pct"][i],
                f"valle: la de sus excesos sobre pi r² a {rr:.0f} m", 1e-6)
    a.cerca(ki * si ** 2, vl["kappa_sigma2"]["iso"], "valle: kappa·sigma², isotrópica", 1e-6)
    a.cerca(kt * st ** 2, vl["kappa_sigma2"]["traslacion"], "valle: kappa·sigma², traslación", 1e-6)
    a.cerca(ki / kt, vl["razon_inv_kappa"], "valle: cuántas veces cambia kappa", 1e-6)
    a.cierto(vl["exceso_dif_pct"][-1] > 5 * vl["k_dif_pct"][-1],
             "valle: el exceso se separa mucho más que la K entera",
             f"{vl['exceso_dif_pct'][-1]:.1f} % contra {vl['k_dif_pct'][-1]:.1f} %")

    # LA z DE LA DISTANCIA, CERRADA: el cuadrático es evidente con Poisson y
    # deja de serlo con los tres conglomerados. El p es el de la chi² de dos
    # grados del Wald publicado.
    from scipy.stats import chi2 as _chi2
    cq = m11["cuadratico_dcen"]
    for x in [cq["poisson"]] + cq["conglomerado"]:
        a.cerca(float(_chi2.sf(x["wald"], 2)), x["p"],
                f"z de la distancia: el p del Wald {x.get('modelo', 'de Poisson')}", 1e-4)
    a.cierto(cq["poisson"]["p"] < 1e-6 and all(x["p"] > 0.05 for x in cq["conglomerado"]),
             "z de la distancia: sí con Poisson, no con conglomerado",
             f"Poisson p = {cq['poisson']['p']:.2g}; "
             + ", ".join(f"{x['modelo']} p = {x['p']:.3f}" for x in cq["conglomerado"]))
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
    # «40 sitios» eran 40 sedes sobrantes en 39 sitios (tercera revisión):
    # se recuentan los sitios y las sedes implicadas, por coordenada exacta.
    a.igual(len(urb), dup["n_con"], "kppm: con duplicados son todas las sedes")
    gr = urb.groupby(["x", "y"]).size()
    a.igual(int((gr >= 2).sum()), dup["sitios"], "kppm: los sitios con más de una sede")
    a.igual(int(gr[gr >= 2].sum()), dup["implicadas"], "kppm: y las sedes implicadas")
    a.igual(dup["implicadas"] - dup["sitios"], dup["repetidos"], "kppm: implicadas menos sitios, sobrantes")
    a.cierto(dup["cambio_maximo_pct"] < 15,
             "kppm: los duplicados no descuadran el ajuste",
             f"como mucho {dup['cambio_maximo_pct']:.1f} %")

    # LA z DEL MÓDULO 9 CON CONGLOMERADO (M2 de la segunda revisión). El
    # auditor no puede reajustar un kppm, pero sí comprobar que el reajuste
    # es el MISMO coeficiente del módulo 9 con otro error, que cada z y cada
    # inflación sean la división que dicen ser, y que la frase del módulo 11
    # —en ninguno de los seis la z llega— sea cierta fila a fila.
    tc = m11["tendencia"]
    ce = m9["centrado"]
    for i, nom in enumerate(tc["coeficientes"]):
        # Si el módulo 9 perdió un error estándar —su propia comprobación lo
        # dice más arriba—, aquí no hay con qué comparar: se informa y se
        # sigue, que un auditor que revienta no informa de nada.
        j = ce["nombres"].index(nom) if nom in ce["nombres"] else None
        if not a.cierto(j is not None and j < len(ce["coef"]) and j < len(ce["ee"] or []),
                        f"tendencia/{nom}: el módulo 9 publica con qué comparar"):
            continue
        a.cerca(tc["coef"][i], ce["coef"][j], f"tendencia/{nom}: el coeficiente del módulo 9", 1e-9)
        a.cerca(tc["poisson"]["ee"][i], ce["ee"][j], f"tendencia/{nom}: el error de Poisson del 9", 1e-9)
        a.cerca(tc["coef"][i] / tc["poisson"]["ee"][i], tc["poisson"]["z"][i],
                f"tendencia/{nom}: la z de Poisson, recalculada", 1e-6)
    a.cerca(NormalDist().inv_cdf(0.975), tc["z_critico"], "tendencia: el 1,96 es el cuantil 0,975", 1e-9)
    combos = {(t["modelo"], t["correccion"]) for t in tc["ajustes"]}
    a.igual(len(combos), 6, "tendencia: los tres modelos por las dos correcciones")
    for t in tc["ajustes"]:
        et = f"tendencia/{t['modelo']}/{t['correccion']}"
        for i, nom in enumerate(tc["coeficientes"]):
            a.cerca(tc["coef"][i] / t["ee"][i], t["z"][i], f"{et}: z de {nom}", 1e-6)
            a.cerca(t["ee"][i] / tc["poisson"]["ee"][i], t["inflacion"][i],
                    f"{et}: inflación de {nom}", 1e-6)
    z_xc = [t["z"][0] for t in tc["ajustes"]]
    inf_xc = [t["inflacion"][0] for t in tc["ajustes"]]
    a.cerca(min(inf_xc), tc["inflacion_xc_min"], "tendencia: la menor inflación de xc", 1e-9)
    a.cerca(max(inf_xc), tc["inflacion_xc_max"], "tendencia: la mayor inflación de xc", 1e-9)
    a.cerca(max(abs(z) for z in z_xc), tc["z_xc_abs_max"], "tendencia: la mayor |z| de xc", 1e-9)
    a.cierto(abs(tc["poisson"]["z"][0]) > tc["z_critico"],
             "tendencia: con Poisson, xc pasa de 1,96",
             f"z = {tc['poisson']['z'][0]:.2f}")
    a.cierto(max(abs(z) for z in z_xc) < tc["z_critico"],
             "tendencia: con conglomerado, en ninguno llega",
             f"|z| ≤ {max(abs(z) for z in z_xc):.2f}")
    a.cierto(min(inf_xc) > 1, "tendencia: el conglomerado infla el error",
             f"entre {min(inf_xc):.2f} y {max(inf_xc):.2f} veces")
    ref = [t for t in tc["ajustes"]
           if (t["modelo"], t["correccion"]) == (tc["referencia"]["modelo"], tc["referencia"]["correccion"])]
    if a.cierto(len(ref) == 1, "tendencia: está el ajuste de referencia"):
        a.cerca(ref[0]["inflacion"][0] ** 2, tc["efecto_diseno"],
                "tendencia: el efecto de diseño es la inflación²", 1e-6)
    a.cerca(tc["n"] / tc["efecto_diseno"], tc["n_efectivo"],
            "tendencia: el n efectivo es n entre el efecto", 1e-6)
    a.igual(tc["n"], len(urb), "tendencia: n son las sedes del patrón urbano")

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

    # El índice depende del ancho del intervalo de conteo, y el módulo lo
    # publica: se recalcula con ESE ancho, no con uno escrito aquí.
    k_int = int(round(h["T"] / h["ancho_intervalo"]))
    a.cerca(h["T"] / k_int, h["ancho_intervalo"], "hawkes: el ancho del intervalo cabe entero en T", 1e-12)

    def dispersion(ev, k=k_int):
        cnt, _ = np.histogram(ev, bins=np.linspace(0, h["T"], k + 1))
        return float(cnt.var(ddof=1) / cnt.mean())
    a.cerca(dispersion(th), h["dispersion_hawkes"],
            "hawkes: el índice de dispersión, recalculado", 1e-6)
    a.cerca(dispersion(tp), h["dispersion_poisson"], "hawkes: y el de su Poisson", 1e-6)
    a.cierto(dispersion(th) > dispersion(tp),
             "hawkes: el autoexcitado sale más agregado",
             f"{dispersion(th):.2f} contra {dispersion(tp):.2f}")
    a.cerca(1 / (1 - h["razon_ramificacion"]) ** 2, h["dispersion_limite"],
            "hawkes: el límite del índice, 1/(1 - a/b)²", 1e-9)
    a.cierto(1 < h["dispersion_hawkes"] < h["dispersion_limite"],
             "hawkes: el índice medido, por debajo de su límite",
             f"{h['dispersion_hawkes']:.2f} contra {h['dispersion_limite']:.2f}")
    # La pregunta del módulo 12 lleva sus propios parámetros, y su respuesta
    # no puede ser la que el módulo 11 ya publica.
    hq = h["pregunta"]
    a.cerca(hq["alpha"] / hq["beta"], hq["razon_ramificacion"], "hawkes/pregunta: la razón de ramificación", 1e-9)
    a.cerca(hq["mu"] / (1 - hq["alpha"] / hq["beta"]), hq["tasa_teorica"],
            "hawkes/pregunta: la tasa teórica", 1e-9)
    a.cierto(hq["razon_ramificacion"] < 1, "hawkes/pregunta: el proceso es estacionario")
    a.cierto(abs(hq["tasa_teorica"] - h["tasa_teorica"]) > 0.05
             and (hq["mu"], hq["alpha"], hq["beta"]) != (h["mu"], h["alpha"], h["beta"]),
             "hawkes/pregunta: no se contesta copiando el módulo",
             f"{hq['tasa_teorica']:.3f} contra {h['tasa_teorica']:.3f}")

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
    respuestas_de_los_ejercicios(a, S)

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
    for clave in ("ciudad_oferta", "ciudad_bachillerato", "ciudad_estudiantes", "proporcion_oficial"):
        g = M[clave]
        nombre = CORTO.get(clave, clave)
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
    for nombre in ("kennedy_puntos", "sector_puntos", "ciudad_oferta", "ciudad_bachillerato",
                   "ciudad_estudiantes", "proporcion_oficial"):
        audita_geomapa(a, M[nombre], CORTO.get(nombre, nombre), presupuesto_kb=560.0)
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
    a.titulo("12b · Los rásteres, al derecho: cada mapa casa con sus propias sedes")
    # -----------------------------------------------------------------
    # Hasta el 2026-10-27 los diez rásteres se publicaron volteados norte-sur
    # (`as.matrix()` de un `im` empieza por el sur y el navegador pinta la fila
    # 0 arriba) y todo lo de arriba estaba en verde: la mediana, el máximo y
    # la escala no dependen del orden de las filas. Aquí no se presupone
    # ningún convenio: cada ráster, leído como lo pinta el navegador, tiene
    # que casar con sus sedes MEJOR que su propio reflejo. Una KDE vale más
    # donde están sus puntos, y la ventana del ráster es la de las sedes.
    def al_derecho(g, X, Y, etq, marcas=None):
        # Un auditor informa: si al ráster le falta un lado, lo dice y sigue.
        nx, ny = g.get("nx"), g.get("ny")
        legible = (isinstance(nx, int) and isinstance(ny, int) and nx > 0 and ny > 0
                   and len(g.get("zq") or []) == nx * ny and g.get("caja") and g.get("zqmax"))
        if not a.cierto(legible, f"orient/{etq}: el ráster se puede leer", f"nx = {nx}, ny = {ny}"):
            return
        z, zr = muestrea(g, X, Y), muestrea(g, X, Y, reflejo=True)
        fuera, fuera_r = int((z < 0).sum()), int((zr < 0).sum())
        a.cierto(fuera <= 0.02 * len(X) and fuera <= fuera_r,
                 f"orient/{etq}: sus sedes caen dentro",
                 f"{fuera} de {len(X)} fuera; {fuera_r} si se volteara")
        if marcas is None:
            v, vr = z[z >= 0].mean(), zr[zr >= 0].mean()
            a.cierto(v > vr, f"orient/{etq}: más alta en sus sedes que volteada",
                     f"{v:.0f} contra {vr:.0f}")
        else:
            uno, otro = (z >= 0) & marcas, (z >= 0) & ~marcas
            uno_r, otro_r = (zr >= 0) & marcas, (zr >= 0) & ~marcas
            d, dr = z[uno].mean() - z[otro].mean(), zr[uno_r].mean() - zr[otro_r].mean()
            a.cierto(d > 0 and d > dr,
                     f"orient/{etq}: mayor en oficiales que en privadas",
                     f"{d:+.0f} sobre {g['zqmax']} ({dr:+.0f} si se volteara)")

    Xk, Yk = puntos_de(M["kennedy_puntos"])
    for g in M["kennedy_familia"]:
        al_derecho(g, Xk, Yk, f"Kennedy σ={g['sigma_m']:.0f}")
    Xs, Ys = puntos_de(M["sector_puntos"])
    ofi_pts = np.asarray(M["sector_puntos"]["marcas"]) == \
        1 + M["sector_puntos"]["niveles"].index("oficial")
    al_derecho(M["ciudad_oferta"], Xs, Ys, "oferta")
    al_derecho(M["ciudad_bachillerato"], Xs, Ys, "bachillerato")
    al_derecho(M["ciudad_estudiantes"], Xs, Ys, "estudiantes")
    al_derecho(M["proporcion_oficial"], Xs, Ys, "P(oficial)", marcas=ofi_pts)

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
