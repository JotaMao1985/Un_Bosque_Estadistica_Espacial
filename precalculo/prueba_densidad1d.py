#!/usr/bin/env python3
"""
prueba_densidad1d.py — la matemática de los simuladores del apéndice A, contra R

Material de Estadística Espacial 2026-II (20929). Apéndice A.

POR QUÉ EXISTE. `precalculo/densidad1d.js` dibuja en vivo histogramas, el
ASH, el KDE con cinco núcleos y el k-NN. Una constante mal puesta —el
soporte del Epanechnikov es √5·bw y no √6·bw— no rompe nada: la curva se ve
igual de bonita y enseña un estimador que no es el que R calcula. Y el
lector del simulador no tiene cómo saberlo. Se prueba igual que el motor 3D
del capítulo 5: contra R.

Tres bloques:

  1. CONTRA LO PUBLICADO. Las cifras que `genera_apendicea.R` escribió en
     `apendicea_datos.json` y que el motor tiene que reproducir EXACTAS
     (tolerancia 1e-9): las modas de los histogramas de `faithful` según
     ancho y origen, la distancia del ASH al triangular, el ejemplo a mano
     del ASH, los valores de Parzen, las modas y diferencias de los núcleos,
     el k-NN de la mezcla y las modas de cada selector. Si el motor y el
     generador discrepan, el simulador enseñaría otra cosa que la prosa.
  2. CONTRA R EN VIVO. `hist()` y `density()` llamados aquí, sobre los mismos
     datos: los conteos tienen que ser idénticos —la tolerancia de `hist()`
     con los datos que caen justo en un corte es exactamente lo que este
     bloque vigila— y el KDE tiene que coincidir con `density()` salvo el
     binado de su FFT (tolerancia declarada: 0.5 % del pico; 1 % para la caja,
     cuyos saltos la FFT reparte entre dos nodos — medido, 0.75 %).
  3. LAS MUTACIONES. Se rompe una copia del motor de siete maneras —el
     soporte del Epanechnikov, la tolerancia de los cortes, la regla de las
     mesetas de las modas, la malla del ASH, el 2 del k-NN, la forma del triangular y la
     escala del KDE— y se exige que los bloques 1 y 2 fallen con cada una.
     Una prueba que no sabe fallar no prueba nada.

    python3 precalculo/prueba_densidad1d.py
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
MOTOR = Path(os.environ.get("D1_MOTOR", RAIZ / "precalculo" / "densidad1d.js"))
RSCRIPT = RAIZ / "precalculo" / "rscript.sh"
DATOS = json.loads((RAIZ / "precalculo" / "salidas" / "apendicea_datos.json").read_text(encoding="utf-8"))
SOLO_BLOQUES = os.environ.get("D1_SIN_MUTACIONES") == "1"

fallos: list[str] = []


def ok(cond: bool, msg: str) -> None:
    print(("  OK   " if cond else "  MAL  ") + msg)
    if not cond:
        fallos.append(msg)


def node(codigo: str, entrada=None):
    prog = (f"const D1 = require({json.dumps(str(MOTOR))});\n"
            f"const E = {json.dumps(entrada)};\n" + codigo)
    r = subprocess.run(["node", "-e", prog], capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit(f"PARADO: node falló\n{r.stderr[-1500:]}")
    return json.loads(r.stdout)


def cerca(a, b, tol=1e-9):
    return abs(float(a) - float(b)) <= tol


def bloque_publicado() -> None:
    print("\n1 · contra lo publicado en apendicea_datos.json (exacto)")
    m2, m3, m5, m6, m7, m10 = (DATOS[k] for k in ("m2", "m3", "m5", "m6", "m7", "m10"))

    r = node("""
      const x = E.eru, sal = { min: [], max: [] };
      for (const h of E.anchos) {
        const ms = E.fracs.map(f => D1.modas(D1.histograma(x, h, f).densidad));
        sal.min.push(Math.min(...ms)); sal.max.push(Math.max(...ms));
      }
      console.log(JSON.stringify(sal));
    """, {"eru": m2["eruptions"], "anchos": m2["anchos"], "fracs": m2["fracs"]})
    ok(r["min"] == m2["modas_min"] and r["max"] == m2["modas_max"],
       f"histograma: modas mínima y máxima en los {len(m2['anchos'])} anchos × "
       f"{len(m2['fracs'])} orígenes")

    t = m3["triangular"]
    r = node("""
      const x = E.eru, h = E.h, g = D1.secuencia(D1.minimo(x) - 1, D1.maximo(x) + 1, E.paso);
      const tri = D1.kdeTriangular(x, h, g);
      console.log(JSON.stringify(E.m.map(m => D1.distanciaMaxima(D1.ash(x, h, m, g), tri))));
    """, {"eru": m2["eruptions"], "h": t["h"], "paso": t["paso_rejilla"], "m": t["m"]})
    ok(all(cerca(a, b, 1e-7) for a, b in zip(r, t["distancia"])),
       "ASH contra el triangular: las " + str(len(t["m"])) + " distancias, una por m")

    ej = m3["ejemplo"]
    r = node("console.log(JSON.stringify(D1.ash(E.x, E.h, E.m, E.p)));",
             {"x": ej["datos"], "h": ej["h"], "m": ej["m"], "p": ej["puntos"]})
    ok(all(cerca(a, b, 1e-7) for a, b in zip(r, ej["f_ash"])),
       "ASH del ejemplo a mano en x = 3, 5, 7 y 9")

    r = node("""
      console.log(JSON.stringify({
        u: D1.kdeSoporte(E.x15, E.x15, 1, 'rectangular'),
        g4: D1.kdeSoporte(E.x5, [4], 1, 'gaussian')[0],
        tabla: E.hs.map(h => [D1.kdeSoporte(E.x5, [4], h, 'rectangular')[0],
                              D1.kdeSoporte(E.x5, [4], h, 'gaussian')[0]]),
        modas: E.hm.map(h => D1.modas(D1.kdeSoporte(E.x5, D1.rejilla(-1, 11, 500), h, 'gaussian')))
      }));
    """, {"x15": m5["uniforme"]["datos"], "x5": m5["gaussiano"]["datos"],
          "hs": [f["h"] for f in m5["tabla"]], "hm": m5["modas"]["h"]})
    ok(all(cerca(a, b, 1e-7) for a, b in zip(r["u"], m5["uniforme"]["f"])),
       "Parzen uniforme sobre {1..5} con h = 1")
    ok(cerca(r["g4"], m5["gaussiano"]["f"], 1e-7), "Parzen gaussiano en x = 4")
    ok(all(cerca(a[0], f["uniforme"], 1e-7) and cerca(a[1], f["gaussiano"], 1e-7)
           for a, f in zip(r["tabla"], m5["tabla"])), "la tabla de f̂(4) con tres anchos")
    ok(r["modas"] == m5["modas"]["modas"], "modas del KDE gaussiano con cuatro anchos")

    tri_m = m6["muestra_trimodal"]
    r = node("""
      const x = E.x, bw = E.bw, a = D1.minimo(x) - 3 * bw, b = D1.maximo(x) + 3 * bw;
      const g = D1.rejilla(a, b, 2048);
      const G = D1.kde(x, g, bw, 'gaussian'), R = D1.kde(x, g, bw, 'rectangular'),
            P = D1.kde(x, g, bw, 'epanechnikov');
      console.log(JSON.stringify({ max: Math.max(...G), dr: D1.distanciaMaxima(G, R),
        de: D1.distanciaMaxima(G, P), mg: D1.modas(G), mr: D1.modas(R), me: D1.modas(P) }));
    """, {"x": tri_m, "bw": m6["trimodal"]["bw"]})
    tm = m6["trimodal"]
    ok(cerca(r["max"], tm["max_gauss"], 1e-7) and cerca(r["dr"], tm["dif_rect"], 1e-7)
       and cerca(r["de"], tm["dif_epan"], 1e-7), "núcleos en la trimodal: pico y diferencias")
    ok((r["mg"], r["mr"], r["me"]) == (tm["modas_gauss"], tm["modas_rect"], tm["modas_epan"]),
       f"núcleos en la trimodal: modas {r['mg']}, {r['mr']} y {r['me']}")

    mz = m7["mezcla"]
    r = node("""
      const g = D1.rejilla(E.desde, E.hasta, E.puntos);
      console.log(JSON.stringify(E.k.map(k => {
        const y = D1.knn(E.x, g, k);
        // El valle, EN valle_x y no en el nodo más cercano (revisión 2).
        const valle = D1.knn(E.x, [E.vx], k)[0];
        return { modas: D1.modas(y), area: D1.trapecio(g, y), valle, max: Math.max(...y) };
      })));
    """, {"x": mz["muestra"], "desde": mz["rejilla"]["desde"], "hasta": mz["rejilla"]["hasta"],
          "puntos": mz["rejilla"]["puntos"], "k": [p["k"] for p in mz["por_k"]],
          "vx": mz["valle_x"]})
    ok(all(a["modas"] == p["modas"] and cerca(a["area"], p["area"], 1e-6)
           and cerca(a["valle"], p["f_valle"], 1e-7)
           # El pico con k = 3 vive donde d_k es diminuta (unas milésimas) y amplifica
           # el redondeo de la muestra publicada: tolerancia RELATIVA de 1e-5, medida
           # (la discrepancia real es de 2e-7).
           and abs(a["max"] / p["maximo"] - 1) < 1e-5
           for a, p in zip(r, mz["por_k"])), "k-NN de la mezcla: modas, área, valle y pico por k")

    hs = [m10["selectores"]["ucv"], m10["selectores"]["SJ"], m10["selectores"]["bcv"]]
    r = node("""
      const x = E.eru, g = D1.rejilla(D1.minimo(x) - 1, D1.maximo(x) + 1, 2048);
      console.log(JSON.stringify({ sel: E.hs.map(h => D1.modas(D1.kde(x, g, h, 'gaussian'))),
                                   curva: E.hh.map(h => D1.modas(D1.kde(x, g, h, 'gaussian'))) }));
    """, {"eru": m2["eruptions"], "hs": hs, "hh": m10["curvas"]["h"]})
    ok(r["sel"] == [m10["modas"]["ucv"], m10["modas"]["SJ"], m10["modas"]["bcv"]],
       "modas del KDE con bw.ucv, bw.SJ y bw.bcv")
    ok(r["curva"] == m10["curvas"]["modas"], "modas del KDE en los " +
       str(len(m10["curvas"]["h"])) + " anchos del simulador de validación cruzada")


def bloque_r() -> None:
    print("\n2 · contra R en vivo: hist() y density()")
    eru = DATOS["m2"]["eruptions"]
    tri_m = DATOS["m6"]["muestra_trimodal"]
    casos = [(0.25, 0.0), (0.25, 0.25), (0.3, 0.5), (0.1, 0.35), (0.6, 0.95)]
    r = node("""
      console.log(JSON.stringify({
        h: E.casos.map(c => D1.histograma(E.eru, c[0], c[1])),
        g: D1.rejilla(-2, 12, 200),
        k: ['gaussian', 'rectangular', 'epanechnikov', 'triangular', 'biweight']
             .map(n => D1.kde(E.tri, D1.rejilla(-2, 12, 200), 0.5, n))
      }));
    """, {"eru": eru, "casos": casos, "tri": tri_m})
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        (tmp / "e.json").write_text(json.dumps({"eru": eru, "tri": tri_m,
                                                "cortes": [h["cortes"] for h in r["h"]]}))
        (tmp / "r.R").write_text(f"""
suppressMessages(library(jsonlite))
E <- fromJSON("{tmp / 'e.json'}", simplifyVector = FALSE)
x <- unlist(E$eru); tri <- unlist(E$tri)
cnt <- lapply(E$cortes, function(b) hist(x, breaks = unlist(b), plot = FALSE,
                                        right = FALSE)$counts)
den <- lapply(c("gaussian", "rectangular", "epanechnikov", "triangular", "biweight"),
              function(k) density(tri, bw = 0.5, kernel = k, n = 200, from = -2, to = 12)$y)
write(toJSON(list(cnt = cnt, den = den), digits = 12), "{tmp / 'r.json'}")
""")
        rr = subprocess.run([str(RSCRIPT), str(tmp / "r.R")], capture_output=True, text=True)
        if rr.returncode != 0:
            sys.exit(f"PARADO: R falló\n{rr.stderr[-1500:]}")
        R = json.loads((tmp / "r.json").read_text())
    for (h, f), js, rc in zip(casos, r["h"], R["cnt"]):
        ok(js["conteos"] == rc, f"conteos de hist() con h = {h} y origen {f}·h")
    for n, js, rd in zip(["gaussian", "rectangular", "epanechnikov", "triangular", "biweight"],
                         r["k"], R["den"]):
        pico = max(rd)
        err = max(abs(a - b) for a, b in zip(js, rd)) / pico
        # La caja es discontinua y la FFT de `density()` reparte cada salto entre
        # dos nodos: medido, 0.75 % del pico. Los núcleos continuos quedan por
        # debajo del 0.1 %, así que se les exige el 0.5 %.
        tope = 0.01 if n == "rectangular" else 0.005
        ok(err < tope, f"KDE {n:<12} contra density(): {100 * err:.3f} % del pico "
                       f"(tope {100 * tope:.1f} %)")


MUTACIONES = [
    ("el soporte del Epanechnikov", "epanechnikov: Math.sqrt(5)", "epanechnikov: Math.sqrt(6)"),
    ("la tolerancia de los cortes", "if (cortes[mid] - fz <= v)", "if (cortes[mid] + fz <= v)"),
    # NO «>» por «>=»: tras comprimir las mesetas no quedan vecinos iguales, así
    # que esa mutación es EQUIVALENTE y ninguna prueba podría cazarla (medido).
    ("las mesetas de las modas", "if (i === 0 || y[i] !== y[i - 1]) r.push(y[i]);",
     "r.push(y[i]);"),
    ("la malla extendida del ASH", "secuencia(minimo(x) - h, maximo(x) + h + d, h)",
     "secuencia(minimo(x), maximo(x) + h + d, h)"),
    ("el 2 del k-NN", "k / (2 * n * dk)", "k / (n * dk)"),
    ("la forma del triangular", "1 - Math.abs((t - x[i]) / h)", "1 - Math.pow((t - x[i]) / h, 2)"),
    ("la escala del KDE", "return s / (x.length * a);\n    });\n  }\n\n  // KDE en la escala de SOPORTE",
     "return s / (x.length * bw);\n    });\n  }\n\n  // KDE en la escala de SOPORTE"),
]


def bloque_mutaciones() -> None:
    print("\n3 · mutaciones: cada una tiene que tumbar la prueba")
    fuente = MOTOR.read_text(encoding="utf-8")
    for que, de, a in MUTACIONES:
        if fuente.count(de) != 1:
            ok(False, f"la mutación «{que}» no encuentra su línea en el motor")
            continue
        with tempfile.TemporaryDirectory() as tmp:
            copia = Path(tmp) / "densidad1d.js"
            copia.write_text(fuente.replace(de, a), encoding="utf-8")
            env = dict(os.environ, D1_MOTOR=str(copia), D1_SIN_MUTACIONES="1")
            rr = subprocess.run([sys.executable, __file__], capture_output=True, text=True, env=env)
            ok(rr.returncode != 0, f"cazada: {que}")


def main() -> int:
    print("\n=== prueba_densidad1d.py ===" + (f"  (motor: {MOTOR})" if SOLO_BLOQUES else ""))
    bloque_publicado()
    bloque_r()
    if not SOLO_BLOQUES:
        bloque_mutaciones()
    print(f"\n{'PRUEBA EN VERDE' if not fallos else 'PRUEBA EN ROJO'}: "
          f"{len(fallos)} fallo(s)")
    return 1 if fallos else 0


if __name__ == "__main__":
    sys.exit(main())
