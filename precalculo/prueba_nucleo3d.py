#!/usr/bin/env python3
"""
prueba_nucleo3d.py — la matemática de la animación 3D, contra R

Material de Estadística Espacial 2026-II (20929). Capítulo 5, módulos 1 y 4.

POR QUÉ EXISTE. `precalculo/nucleo3d/nucleo3d.js` dibuja la superficie
λ̂(u) = Σ k_σ(u − xᵢ) con CUATRO funciones de peso escritas a mano en
JavaScript. Una constante mal puesta —el soporte del Epanechnikov es √6·σ y
no √5·σ— no rompe nada: la loma se ve igual de bonita y enseña un núcleo que
no es el que `density()` calcula. Es el mismo defecto que el material
persigue en todas partes, y se prueba igual: contra R.

Cuatro bloques, y el segundo y el cuarto son los que deciden:

  1. LAS PROPIEDADES, sin R. Cada núcleo integra 1 sobre el plano y tiene
     desviación típica σ en cada coordenada —la convención que el módulo 2
     advierte («al mismo σ» es a la misma DESVIACIÓN TÍPICA, no al mismo
     soporte)—. Se integra en polar y se exige 1 ± 1e-3.
  2. LA INTENSIDAD, contra `density.ppp` de spatstat. Mismo patrón (los
     diecinueve puntos del motor), mismos cuatro núcleos, tres σ, SIN
     corrección de borde (`edge = FALSE`, que es lo que la animación pinta) y
     sobre los centros de los píxeles de R. El JS evalúa la suma EXACTA en
     esos mismos centros; el error se mide contra el máximo de R.

LA TOLERANCIA SE DECLARA CON SU CAUSA, Y SE MIDIÓ. R no evalúa la suma exacta:
coloca cada punto en el centro de su píxel y convoluciona. Comparado a pelo, el
JS se aleja de R entre un 0.5 y un 2 % del pico —más cuanto más estrecho σ— y
parece un error de la fórmula. No lo es: pegando los diecinueve puntos al
centro de su píxel antes de evaluar, que es lo que R hace, la diferencia cae a
**0.0000 %** en el gaussiano y el cuártico y a 0.002 % en el Epanechnikov. Esa
es la comparación que decide (la «cruda» se imprime al lado para que se vea la
brecha que explica R, no la fórmula). El disco es discontinuo: su borde cae
entre píxeles y la convolución de R lo reparte, así que sobre unos pocos
píxeles de borde la diferencia llega al 0.4 % del pico; de ahí su tope aparte.
La masa total de las dos vías coincide en el 0.1 %.

  3. EL TEST DE CUADRANTES, contra `quadratcount` de spatstat, en los 26 valores
     del deslizador de la rejilla. Aquí hay un riesgo que el bloque 2 no ve: con
     la rejilla desplazada, un punto cae EXACTAMENTE sobre una línea (el patrón
     tiene coordenadas de un decimal y el deslizador avanza de 0.05 en 0.05), y
     quién se queda con el punto depende de la convención de cada extremo y del
     ruido de coma flotante de la arista. R usa intervalos (a, b]; el motor tiene
     que usar los mismos o «celda más llena» y «celdas vacías» saltarían entre
     valores vecinos del deslizador sin regla alguna.

  4. LA CORRECCIÓN DE BORDE (escena «borde», módulo 4), contra `density(edge = TRUE)` y
     `density(diggle = TRUE)`. Tres superficies —sin corregir, «por defecto» (divide en el
     sitio u) y Diggle (divide en cada dato xᵢ)— y la fracción e del núcleo que cae dentro de
     la ventana, que el motor calcula por direcciones y que R calcula en píxeles. Se comprueba:
       a. e en los píxeles de R, como el cociente `edge = FALSE` / `edge = TRUE` de una sede
          pegada al borde, otra pegada a la esquina y otra a 0.7 del borde;
       b. las dos superficies corregidas sobre los píxeles de R, con los puntos pegados al
          centro de su píxel (el mismo ajuste del bloque 2);
       c. las tres masas —lo que la animación escribe en pantalla—;
       d. propiedades exactas, sin R: e vale ½ en el medio de un lado y ¼ en una esquina (con σ
          estrecho), y el gaussiano coincide con el producto de dos funciones de error.
     Las tolerancias salen de MEDIR el error y cada una lleva su causa en el código.

    python3 precalculo/prueba_nucleo3d.py
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
# `NUCLEO3D_MOTOR` redirige el motor a una copia: así se comprueba que la prueba sabe fallar.
MOTOR = Path(os.environ.get("NUCLEO3D_MOTOR", RAIZ / "precalculo" / "nucleo3d" / "nucleo3d.js"))
RSCRIPT = RAIZ / "precalculo" / "rscript.sh"

SIGMAS = [0.5, 0.8, 1.6]
SIGMAS_BORDE = [0.5, 0.8, 1.6, 2.2]
NUCLEOS = ["gaussian", "epanechnikov", "quartic", "disc"]
# Error máximo contra el pico de R, con los puntos pegados a su píxel (ver arriba).
TOLERANCIA = {"gaussian": 0.0001, "epanechnikov": 0.0001, "quartic": 0.0001, "disc": 0.01}

# --- Bloque 4. Tolerancias MEDIDAS (R 4.4, spatstat.explore 3.8.0). Cada una lleva su causa. -------------------
# e(u) contra el cociente de R: R suma por píxeles de 0.039 y el motor integra por direcciones. Medido: el error
# máximo es 0.0009 en los tres núcleos de borde suave y 0.0017 en el disco, cuyo borde brusco cae entre píxeles.
TOL_E = {"gaussian": 0.002, "epanechnikov": 0.002, "quartic": 0.002, "disc": 0.004}
# Las dos superficies corregidas, error máximo contra el pico de R (puntos pegados a su píxel). Medido: 0.006 % en
# los suaves y 0.41 % en el disco, por la misma causa que en el bloque 2 (de ahí su tope aparte).
TOL_SUPERFICIE = {"gaussian": 0.0005, "epanechnikov": 0.0005, "quartic": 0.0005, "disc": 0.01}
# Las masas, relativas a la suma de píxeles de R. `sin` es una fórmula exacta (medido ≤ 3e-4, el disco); `defecto` es
# un trapecio sobre 96 × 96 vértices y R es una suma de píxeles, así que cada uno se aleja del valor exacto: ≤ 3e-4
# en los núcleos suaves y 3.6e-3 en el disco con σ = 0.5 (0.07 sobre 19.5: lo que la pantalla escribe con un decimal).
TOL_MASA_SIN = {"gaussian": 1e-4, "epanechnikov": 1e-4, "quartic": 1e-4, "disc": 1e-3}
TOL_MASA_DEFECTO = {"gaussian": 1e-3, "epanechnikov": 1e-3, "quartic": 1e-3, "disc": 6e-3}

fallos: list[str] = []


def ok(cond: bool, msg: str) -> None:
    print(("  OK   " if cond else "  MAL  ") + msg)
    if not cond:
        fallos.append(msg)


def node(codigo: str, entrada: dict | None = None) -> dict:
    """Corre JavaScript contra el motor REAL (el mismo archivo que se publica)."""
    prog = (f"const M = require({json.dumps(str(MOTOR))}).matematica;\n"
            f"const ENTRADA = {json.dumps(entrada)};\n" + codigo)
    r = subprocess.run(["node", "-e", prog], capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit(f"PARADO: node falló\n{r.stderr}")
    return json.loads(r.stdout)


def main() -> int:
    print("\n=== prueba_nucleo3d.py ===")

    # ---- 1 · propiedades de cada núcleo -------------------------------------
    print("\n1 · masa 1 y desviación típica σ por coordenada (integración polar)")
    prop = node("""
      const sal = {};
      for (const k of M.ORDEN_NUCLEOS) {
        sal[k] = {};
        for (const s of [0.5, 1, 2.3]) {
          const f = M.NUCLEOS[k].k, R = 6 * s, N = 40000, dr = R / N;
          let masa = 0, m2 = 0;
          for (let i = 0; i < N; i++) {
            const r = (i + 0.5) * dr, v = f(r * r, s) * 2 * Math.PI * r * dr;
            masa += v; m2 += v * r * r;
          }
          sal[k][s] = { masa, sd: Math.sqrt(m2 / masa / 2) };
        }
      }
      console.log(JSON.stringify(sal));
    """)
    for k in NUCLEOS:
        for s, d in prop[k].items():
            ok(abs(d["masa"] - 1) < 1e-3 and abs(d["sd"] / float(s) - 1) < 1e-3,
               f"{k:<12} σ={s:<4} masa={d['masa']:.5f} sd/σ={d['sd'] / float(s):.5f}")

    print("\n1b · la masa radial cerrada `masa(R, σ)` contra la integral numérica de `k`")
    radial = node("""
      const sal = [];
      for (const k of M.ORDEN_NUCLEOS) for (const s of [0.5, 1.3]) for (const q of [0.3, 1, 1.7, 2.2, 5]) {
        const R = q * s, N = 20000, dr = R / N;
        let masa = 0;
        for (let i = 0; i < N; i++) { const r = (i + 0.5) * dr; masa += M.NUCLEOS[k].k(r * r, s) * 2 * Math.PI * r * dr; }
        sal.push({ k, s, q, num: masa, cerrada: M.NUCLEOS[k].masa(R, s) });
      }
      console.log(JSON.stringify(sal));
    """)
    peor = max(radial, key=lambda c: abs(c["num"] - c["cerrada"]))
    ok(all(abs(c["num"] - c["cerrada"]) < 2e-4 for c in radial),
       f"las {len(radial)} masas radiales coinciden con la integral numérica (peor: {peor['k']} σ={peor['s']} R={peor['q']}σ, "
       f"diferencia {abs(peor['num'] - peor['cerrada']):.1e}; tope 2e-4, diez veces lo medido)")

    # ---- 2 · la intensidad, contra density.ppp ------------------------------
    print("\n2 · intensidad sobre los píxeles de R (sin corrección de borde)")
    patron = node("console.log(JSON.stringify({ pts: M.PATRON, V: M.V }));")
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        (tmp / "patron.json").write_text(json.dumps(patron))
        (tmp / "r.R").write_text(f"""
suppressMessages({{library(spatstat); library(jsonlite)}})
P <- fromJSON("{tmp / 'patron.json'}")
V <- P$V; xy <- P$pts
W <- owin(c(-V, V), c(-V, V))
p <- ppp(xy[, 1], xy[, 2], window = W)
sal <- list()
for (k in c({', '.join(f'"{n}"' for n in NUCLEOS)})) for (s in c({', '.join(map(str, SIGMAS))})) {{
  d <- density(p, sigma = s, kernel = k, edge = FALSE, dimyx = c(256, 256))
  m <- as.matrix(d)
  # una muestra de píxeles regularmente repartida, con sus centros
  fi <- seq(8, 256, by = 16); co <- seq(8, 256, by = 16)
  sal[[paste(k, s)]] <- list(k = k, s = s, pico = max(m), masa = sum(m) * (d$xstep * d$ystep),
    x = d$xcol[co], y = d$yrow[fi], v = m[fi, co], vx = as.vector(d$xcol), vy = as.vector(d$yrow))
}}
write(toJSON(sal, auto_unbox = TRUE, digits = 12), "{tmp / 'r.json'}")
""")
        r = subprocess.run([str(RSCRIPT), str(tmp / "r.R")], capture_output=True, text=True)
        if r.returncode != 0:
            sys.exit(f"PARADO: R falló\n{r.stderr[-1500:]}")
        rjson = json.loads((tmp / "r.json").read_text())

        cmp = node("""
          const R = ENTRADA, sal = [];
          for (const c of Object.values(R)) {
            let e = 0, eRaw = 0;
            // R coloca cada punto en el centro de su píxel antes de convolucionar:
            // se pega igual para que lo que quede sea la FÓRMULA, no el binning.
            const x0 = c.vx[0], h = c.vx[1] - c.vx[0];
            const pegado = M.PATRON.map(p => [x0 + Math.round((p[0] - x0) / h) * h, x0 + Math.round((p[1] - x0) / h) * h]);
            c.y.forEach((y, a) => c.x.forEach((x, b) => {
              const r = c.v[a][b];
              e = Math.max(e, Math.abs(M.intensidadEn(c.k, pegado, c.s, x, y) - r));
              eRaw = Math.max(eRaw, Math.abs(M.intensidadEn(c.k, M.PATRON, c.s, x, y) - r));
            }));
            // masa de la animación: la suma sobre la ventana de los píxeles de R
            let masa = 0; const hm = c.vx[1] - c.vx[0];
            for (const y of c.vy) for (const x of c.vx) masa += M.intensidadEn(c.k, M.PATRON, c.s, x, y) * hm * hm;
            sal.push({ k: c.k, s: c.s, pico: c.pico, err: e, errCrudo: eRaw, masaR: c.masa, masaJS: masa });
          }
          console.log(JSON.stringify(sal));
        """, rjson)
    for c in cmp:
        rel = c["err"] / c["pico"]
        ok(rel < TOLERANCIA[c["k"]] and abs(c["masaJS"] / c["masaR"] - 1) < 0.01,
           f"{c['k']:<12} σ={c['s']:<4} error/pico={rel:.4%} (tope {TOLERANCIA[c['k']]:.2%}; "
           f"sin pegar los puntos: {c['errCrudo'] / c['pico']:.2%}) masa JS/R={c['masaJS'] / c['masaR']:.4f}")

    # ---- 3 · el test de cuadrantes, contra quadratcount ---------------------
    print("\n3 · conteo por celdas con la rejilla desplazada (26 posiciones del deslizador)")
    ds = [round(0.05 * k, 2) for k in range(26)]
    rej2 = node("""
      const sal = [];
      for (const d of ENTRADA) {
        const c = M.cuadrantes(M.PATRON, d);
        sal.push({ d, celdas: c.celdas.map(z => ({ ancho: Math.min(z.x1 - z.x0, z.y1 - z.y0) })) });
      }
      console.log(JSON.stringify({ rej: sal }));
    """, ds)
    rej = node("""
      const sal = [];
      for (const d of ENTRADA) {
        const c = M.cuadrantes(M.PATRON, d);
        sal.push({ d, aristas: c.aristas, celdas: c.celdas.map(z => ({ i: z.i, j: z.j, n: z.n, area: z.area })) });
      }
      console.log(JSON.stringify({ pts: M.PATRON, V: M.V, rej: sal }));
    """, ds)
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        (tmp / "rej.json").write_text(json.dumps(rej))
        (tmp / "q.R").write_text(f"""
suppressMessages({{library(spatstat); library(jsonlite)}})
P <- fromJSON("{tmp / 'rej.json'}", simplifyVector = FALSE)
xy <- do.call(rbind, lapply(P$pts, unlist))
W <- owin(c(-P$V, P$V), c(-P$V, P$V))
p <- ppp(xy[, 1], xy[, 2], window = W)
sal <- lapply(P$rej, function(r) {{
  a <- unlist(r$aristas)
  q <- unclass(quadratcount(p, xbreaks = a, ybreaks = a))
  list(d = r$d, m = q[nrow(q):1, , drop = FALSE])      # fila 1 = la y más baja, como el motor
}})
write(toJSON(sal, auto_unbox = TRUE, digits = 12), "{tmp / 'q.json'}")
""")
        r = subprocess.run([str(RSCRIPT), str(tmp / "q.R")], capture_output=True, text=True)
        if r.returncode != 0:
            sys.exit(f"PARADO: R falló\n{r.stderr[-1500:]}")
        qjson = json.loads((tmp / "q.json").read_text())
    malos = []
    ties = 0
    for mio, r in zip(rej["rej"], qjson):
        m = r["m"]
        area = sum(c["area"] for c in mio["celdas"])
        total = sum(c["n"] for c in mio["celdas"])
        dif = [(c["i"], c["j"], c["n"], m[c["j"]][c["i"]]) for c in mio["celdas"] if c["n"] != m[c["j"]][c["i"]]]
        # ¿algún punto cae exactamente sobre una arista? (el caso que decide la convención)
        sobre = any(abs(x - a) < 1e-9 for pt in rej["pts"] for x in pt for a in mio["aristas"])
        ties += sobre
        if dif or abs(area - 100) > 1e-6 or total != len(rej["pts"]):
            malos.append(f"d={r['d']:.2f} distintas={dif[:3]} área={area:.4f} puntos={total}")
    ok(not malos, f"las celdas coinciden con quadratcount en las 26 posiciones ({ties} de ellas con un punto sobre una línea)"
       + ("" if not malos else ": " + "; ".join(malos[:3])))
    ok(ties >= 5, "la prueba SÍ ejercita los empates (si el patrón cambiara y dejara de haberlos, no probaría lo que dice)")
    # Las astillas (auditoría del 2026-10-02): con la rejilla desplazada 0.05 la primera columna medía 0.05 y la lectura
    # pasaba de 16 a 25 celdas. Fundida con su vecina, siempre son 4 × 4 y ninguna mide menos de media celda.
    estrechas = [(m["d"], round(min(c["ancho"] for c in m["celdas"]), 3)) for m in rej2["rej"]
                 if min(c["ancho"] for c in m["celdas"]) < 1.25 - 1e-9]
    cuentas = sorted({len(m["celdas"]) for m in rej2["rej"]})
    ok(not estrechas and cuentas == [16],
       f"en las 26 posiciones hay 16 celdas y ninguna más estrecha que media celda (cuentas {cuentas}; estrechas {estrechas[:3]})")


    # ---- 4 · la corrección de borde, contra density(edge = TRUE) y density(diggle = TRUE) ---------
    print("\n4 · corrección de borde: e(u), las dos superficies corregidas y las tres masas")
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        (tmp / "patron.json").write_text(json.dumps(patron))
        (tmp / "b.R").write_text(f"""
suppressMessages({{library(spatstat); library(jsonlite)}})
P <- fromJSON("{tmp / 'patron.json'}")
V <- P$V; xy <- P$pts
W <- owin(c(-V, V), c(-V, V))
p <- ppp(xy[, 1], xy[, 2], window = W)
sal <- list()
dens <- function(x, s, k, ...) density(x, sigma = s, kernel = k, dimyx = c(256, 256), ...)
for (k in c({', '.join(f'"{n}"' for n in NUCLEOS)})) for (s in c({', '.join(map(str, SIGMAS_BORDE))})) {{
  d0 <- dens(p, s, k, edge = FALSE)
  d1 <- dens(p, s, k, edge = TRUE)
  d2 <- dens(p, s, k, edge = TRUE, diggle = TRUE)
  px <- d0$xstep * d0$ystep
  fi <- seq(8, 256, by = 16); co <- seq(8, 256, by = 16)
  e <- list()
  # e(u) = lo que R calcula SIN corregir entre lo que calcula CORREGIDO, con una sola sede: el kernel se cancela
  for (pt in list(c(4.5, 0), c(4.4, 4.4), c(-4.3, 2.0))) {{
    q <- ppp(pt[1], pt[2], window = W)
    a <- as.matrix(dens(q, s, k, edge = FALSE)); b <- as.matrix(dens(q, s, k, edge = TRUE))
    ix <- which(a > 0.02 * max(a), arr.ind = TRUE)
    ix <- ix[seq(1, nrow(ix), length.out = min(nrow(ix), 300)), , drop = FALSE]
    e[[length(e) + 1]] <- list(x = d0$xcol[ix[, 2]], y = d0$yrow[ix[, 1]], e = a[ix] / b[ix])
  }}
  sal[[paste(k, s)]] <- list(k = k, s = s, vx = as.vector(d0$xcol), x = d0$xcol[co], y = d0$yrow[fi],
    v1 = as.matrix(d1)[fi, co], v2 = as.matrix(d2)[fi, co], p1 = max(as.matrix(d1)), p2 = max(as.matrix(d2)),
    m0 = sum(d0$v) * px, m1 = sum(d1$v) * px, m2 = sum(d2$v) * px, e = e)
}}
# las sedes SOLAS: lo que aporta a la integral cada una, que es lo que dice el panel y lo que el texto afirma. La primera
# es la del módulo 4 (a 0.5 del borde, σ = 1, gaussiana); las demás cubren el borde, la esquina, el medio y el centro.
casos <- list(list(k = "gaussian", s = 1, x = 4.5, y = 0), list(k = "gaussian", s = 0.8, x = 4.9, y = 0.3),
              list(k = "epanechnikov", s = 1.6, x = 3.4, y = -1), list(k = "disc", s = 0.8, x = 4.8, y = 4.8),
              list(k = "quartic", s = 1.2, x = 2.9, y = 1.1), list(k = "gaussian", s = 2.2, x = 0, y = 0))
solos <- lapply(casos, function(cs) {{
  q <- ppp(cs$x, cs$y, window = W)
  m <- function(...) sum(dens(q, cs$s, cs$k, ...)$v) * (10 / 256)^2
  c(cs, list(sin = m(edge = FALSE), defecto = m(edge = TRUE), diggle = m(edge = TRUE, diggle = TRUE)))
}})
write(toJSON(list(celdas = sal, solos = solos), auto_unbox = TRUE, digits = 12), "{tmp / 'b.json'}")
""")
        r = subprocess.run([str(RSCRIPT), str(tmp / "b.R")], capture_output=True, text=True)
        if r.returncode != 0:
            sys.exit(f"PARADO: R falló\n{r.stderr[-1500:]}")
        rb = json.loads((tmp / "b.json").read_text())

    cmp4 = node("""
      const sal = [], N = 96, k = nuc => M.NUCLEOS[nuc].k;
      for (const c of Object.values(ENTRADA.celdas)) {
        const x0 = c.vx[0], h = c.vx[1] - c.vx[0];
        const pega = p => [x0 + Math.round((p[0] - x0) / h) * h, x0 + Math.round((p[1] - x0) / h) * h];
        const pegado = M.PATRON.map(pega);
        const ePts = pegado.map(p => M.bordeE(c.k, c.s, p[0], p[1]));
        const eM = new Float64Array(N * N); M.mallaE(c.k, c.s, N, eM);
        // a · e(u) contra el cociente de R
        let eErr = 0, eN = 0;
        for (const g of c.e) for (let i = 0; i < g.x.length; i++) { eErr = Math.max(eErr, Math.abs(M.bordeE(c.k, c.s, g.x[i], g.y[i]) - g.e[i])); eN++; }
        // b · las superficies en los píxeles de R: la fórmula, evaluada a pelo, con e en cada sitio
        const en = (modo, x, y) => {
          let t = 0;
          for (let q = 0; q < pegado.length; q++) {
            const dx = x - pegado[q][0], dy = y - pegado[q][1], v = k(c.k)(dx * dx + dy * dy, c.s);
            t += modo === 'diggle' ? v / ePts[q] : v;
          }
          return modo === 'defecto' ? t / M.bordeE(c.k, c.s, x, y) : t;
        };
        const dif = (modo, V) => { let m = 0; c.y.forEach((y, a) => c.x.forEach((x, b) => { m = Math.max(m, Math.abs(en(modo, x, y) - V[a][b])); })); return m; };
        // b' · y la función que DIBUJA la superficie contra esa misma fórmula, en los vértices de una rejilla: sin este
        //      eslabón la fórmula de arriba (que vive en la prueba) coincidiría con R y el motor podría estar mal escrito
        const n4 = 40, e4 = new Float64Array(n4 * n4); M.mallaE(c.k, c.s, n4, e4);
        let motorErr = 0;
        for (const modo of ['sin', 'defecto', 'diggle']) {
          const sal4 = new Float64Array(n4 * n4); M.superficieBorde(c.k, pegado, c.s, n4, modo, e4, ePts, sal4);
          const paso = 2 * M.V / (n4 - 1);
          for (let j = 0; j < n4; j++) for (let i = 0; i < n4; i++) {
            const ref = en(modo, -M.V + i * paso, -M.V + j * paso);
            motorErr = Math.max(motorErr, Math.abs(sal4[j * n4 + i] - ref) / Math.max(1e-12, Math.abs(ref)));
          }
        }
        // c · las masas, con la función que usa la pantalla
        const I = M.integralesBorde(c.k, pegado, c.s, N, eM, ePts);
        sal.push({ k: c.k, s: c.s, eErr, eN, errDef: dif('defecto', c.v1) / c.p1, errDig: dif('diggle', c.v2) / c.p2, motorErr,
                   sin: [I.sin, c.m0], defecto: [I.defecto, c.m1], diggle: [I.diggle, c.m2] });
      }
      // las sedes solas, con la misma cuenta (el punto, pegado al píxel)
      const c0 = Object.values(ENTRADA.celdas)[0], x0 = c0.vx[0], h = c0.vx[1] - c0.vx[0];
      const solos = ENTRADA.solos.map(cs => {
        const p1 = [[x0 + Math.round((cs.x - x0) / h) * h, x0 + Math.round((cs.y - x0) / h) * h]];
        const e1 = [M.bordeE(cs.k, cs.s, p1[0][0], p1[0][1])], eM1 = new Float64Array(N * N); M.mallaE(cs.k, cs.s, N, eM1);
        const I1 = M.integralesBorde(cs.k, p1, cs.s, N, eM1, e1);
        return { k: cs.k, s: cs.s, x: cs.x, y: cs.y, js: { sin: I1.sin, defecto: I1.defecto, diggle: I1.diggle }, r: { sin: cs.sin, defecto: cs.defecto, diggle: cs.diggle } };
      });
      console.log(JSON.stringify({ celdas: sal, solos }));
    """, rb)
    for c in cmp4["celdas"]:
        ok(c["eErr"] < TOL_E[c["k"]],
           f"e(u)  {c['k']:<12} σ={c['s']:<4} máx|JS−R|={c['eErr']:.5f} en {c['eN']} píxeles (tope {TOL_E[c['k']]})")
        ok(c["errDef"] < TOL_SUPERFICIE[c["k"]] and c["errDig"] < TOL_SUPERFICIE[c["k"]] and c["motorErr"] < 1e-9,
           f"λ̂    {c['k']:<12} σ={c['s']:<4} error/pico por defecto={c['errDef']:.4%} Diggle={c['errDig']:.4%} (tope {TOL_SUPERFICIE[c['k']]:.2%}); "
           f"superficieBorde contra la fórmula: {c['motorErr']:.0e} (tope 1e-9)")
        rel = lambda par: abs(par[0] / par[1] - 1)
        ok(rel(c["sin"]) < TOL_MASA_SIN[c["k"]] and rel(c["defecto"]) < TOL_MASA_DEFECTO[c["k"]] and abs(c["diggle"][0] - c["diggle"][1]) < 1e-3,
           f"masa  {c['k']:<12} σ={c['s']:<4} sin {c['sin'][0]:.4f}/{c['sin'][1]:.4f}  defecto {c['defecto'][0]:.4f}/{c['defecto'][1]:.4f}  "
           f"Diggle {c['diggle'][0]:.4f}/{c['diggle'][1]:.4f}  (JS/R)")
    # Las sedes solas, contra R: lo que cada una aporta a la integral con cada corrección. Es lo que el panel de la animación
    # escribe junto a la sede en foco, y la lección que el módulo 4 enseña con ella. Tolerancia 0.01 (0.05 el disco): R suma píxeles.
    solos = cmp4["solos"]
    for c in solos:
        tol = 0.05 if c["k"] == "disc" else 0.01
        ok(all(abs(c["js"][m] - c["r"][m]) < tol for m in ("sin", "defecto", "diggle")),
           f"sede sola {c['k']:<12} σ={c['s']:<4} en ({c['x']}, {c['y']}): sin / por defecto / Diggle = "
           f"{c['js']['sin']:.3f} / {c['js']['defecto']:.3f} / {c['js']['diggle']:.3f} en el motor y "
           f"{c['r']['sin']:.3f} / {c['r']['defecto']:.3f} / {c['r']['diggle']:.3f} en R (tope {tol})")
    sr = solos[0]["r"]
    # La lección que el módulo 4 enseña con ella, medida en los DOS lados: una sede sola, pegada al borde, queda por DEBAJO de 1
    # con la corrección por defecto; las diecinueve del patrón, por ENCIMA de n. «La masa se pasa» no es una propiedad del
    # método sino de dónde caen los puntos, y la animación existe para que se vea moviéndolos.
    pasa = [c for c in cmp4["celdas"] if c["k"] == "gaussian"]
    n_pts = len(patron["pts"])
    masas_pasa = ", ".join("%.2f" % c["defecto"][1] for c in pasa)
    ok(sr["defecto"] < 0.95 and all(c["defecto"][1] > n_pts for c in pasa),
       f"la corrección por defecto se queda corta con una sede ({sr['defecto']:.3f} < 1) y se pasa con las diecinueve "
       f"(R: {masas_pasa} > {n_pts})")

    # El módulo 4 del capítulo dice «diecinueve puntos» con palabras (una cifra con dígitos tendría que venir de un JSON): si el
    # patrón del motor cambia de tamaño, ese texto miente sin que ningún auditor de cifras lo vea.
    palabras = {19: "diecinueve"}.get(n_pts)
    ok(palabras is not None and f"los {palabras} puntos inventados" in (RAIZ / "precalculo" / "ensambla_cap5.py").read_text(encoding="utf-8"),
       f"el patrón tiene {n_pts} puntos y el módulo 4 dice «los diecinueve puntos inventados» (si el patrón cambia, hay que reescribir esa frase)")

    # d · propiedades exactas, sin R
    prop4 = node("""
      const sal = { medio: [], esquina: [], gauss: [] };
      const erf = x => { let s = 0, t = x, n = 0; const N = 4000; for (let i = 0; i < N; i++) { const u = (i + 0.5) / N * x; s += Math.exp(-u * u) * x / N; } return 2 / Math.sqrt(Math.PI) * s; };
      for (const k of M.ORDEN_NUCLEOS) {
        sal.medio.push({ k, e: M.bordeE(k, 0.5, M.V, 0) });                 // en el medio de un lado: la mitad del núcleo
        sal.esquina.push({ k, e: M.bordeE(k, 0.5, M.V, M.V) });             // en una esquina: la cuarta parte
      }
      for (const s of [0.5, 1, 2.2]) for (const [x, y] of [[0, 0], [4.5, 0], [4.9, 4.9], [-4.3, 2], [3, 4.4], [2.1, -1.9]]) {
        const F = (a, b, m) => 0.5 * (erf((b - m) / s / Math.SQRT2) - erf((a - m) / s / Math.SQRT2));
        sal.gauss.push({ s, x, y, e: M.bordeE('gaussian', s, x, y), exacta: F(-M.V, M.V, x) * F(-M.V, M.V, y) });
      }
      console.log(JSON.stringify(sal));
    """)
    ok(all(abs(c["e"] - 0.5) < 1e-6 for c in prop4["medio"]) and all(abs(c["e"] - 0.25) < 1e-6 for c in prop4["esquina"]),
       "e vale ½ en el medio de un lado y ¼ en una esquina, con los cuatro núcleos (σ = 0.5)")
    peor = max(prop4["gauss"], key=lambda c: abs(c["e"] - c["exacta"]))
    ok(abs(peor["e"] - peor["exacta"]) < 1e-4,
       f"el gaussiano coincide con el producto de dos funciones de error en {len(prop4['gauss'])} sitios "
       f"(peor: σ={peor['s']} ({peor['x']}, {peor['y']}), diferencia {abs(peor['e'] - peor['exacta']):.1e}; tope 1e-4)")


    # e · cada sede por separado, y las dos frases del texto con números. Lo que dibuja la barra de cada sede y lo que lee quien
    #     no ve la pantalla sale de `por[q]`: una sede cambiada de sitio o una suma que sale bien con las barras mal pasarían
    #     las comparaciones de arriba (que solo miran sumas), y esto las caza.
    texto4 = node("""
      const N = 96, sal = { por: [], afirma: [] };
      for (const k of M.ORDEN_NUCLEOS) for (const s of [0.8, 1.6, 2.2]) {
        const eM = new Float64Array(N * N); M.mallaE(k, s, N, eM);
        const ePts = M.PATRON.map(p => M.bordeE(k, s, p[0], p[1]));
        const T = M.integralesBorde(k, M.PATRON, s, N, eM, ePts);
        let dif = 0;
        M.PATRON.forEach((p, q) => {
          const I = M.integralesBorde(k, [p], s, N, eM, [ePts[q]]);          // la sede sola: no depende de las demás
          dif = Math.max(dif, Math.abs(I.por[0].defecto - T.por[q].defecto), Math.abs(T.por[q].sin - ePts[q]), Math.abs(T.por[q].diggle - 1));
        });
        sal.por.push({ k, s, dif, difSuma: Math.abs(T.por.reduce((a, o) => a + o.defecto, 0) - T.defecto) + Math.abs(T.por.reduce((a, o) => a + o.sin, 0) - T.sin) });
      }
      // «una sede pegada al borde aporta menos de 1; una a uno y medio o dos σ de él, más»: el eje x, y = 0.3
      for (const k of M.ORDEN_NUCLEOS) for (const s of [0.8, 1.2, 1.6, 2.2]) {
        const eM = new Float64Array(N * N); M.mallaE(k, s, N, eM);
        const aporta = d => { const p = [[M.V - d, 0.3]]; return M.integralesBorde(k, p, s, N, eM, [M.bordeE(k, s, p[0][0], p[0][1])]).por[0].defecto; };
        sal.afirma.push({ k, s, pegada: Math.max(...[0, 0.1, 0.25].map(aporta)), lejos: Math.min(...[1.5, 1.75, 2].map(q => aporta(q * s))) });
      }
      // las escalas de la escena: el techo cubre las tres superficies y el alto sale del rango de σ de ESA escena
      const sg = M.ESCENAS.borde.sigma, E = M.escalasBorde(M.PATRON, sg), n = 61, tmp = new Float64Array(n * n), eM = new Float64Array(n * n);
      let necesario = 0;
      for (const k of M.ORDEN_NUCLEOS) {
        const ePts = M.PATRON.map(p => M.bordeE(k, sg.min, p[0], p[1])); M.mallaE(k, sg.min, n, eM);
        for (const modo of ['sin', 'defecto', 'diggle']) necesario = Math.max(necesario, E.alto * M.superficieBorde(k, M.PATRON, sg.min, n, modo, eM, ePts, tmp));
      }
      const E1 = M.escalas(M.PATRON, sg), E0 = M.escalas(M.PATRON);
      sal.escalas = { techo: E.techo, necesario, alto: E.alto, altoEsperado: E1.alto, altoConteo: E0.alto, color: E.color, colorEsperado: E1.color };
      console.log(JSON.stringify(sal));
    """)
    peor = max(texto4["por"], key=lambda c: max(c["dif"], c["difSuma"]))
    ok(all(c["dif"] < 1e-12 and c["difSuma"] < 1e-9 for c in texto4["por"]),
       f"lo que aporta cada sede es lo mismo solo que con las demás, y las partes suman el total ({len(texto4['por'])} núcleos × σ; "
       f"peor diferencia {max(peor['dif'], peor['difSuma']):.0e})")
    pg = max(texto4["afirma"], key=lambda c: c["pegada"]); lj = min(texto4["afirma"], key=lambda c: c["lejos"])
    ok(pg["pegada"] < 0.95 and lj["lejos"] > 1.02,
       f"«pegada al borde aporta menos de 1, a uno y medio o dos σ más»: con los cuatro núcleos y σ de 0.8 a 2.2, a ≤ 0.25 del borde "
       f"aporta como mucho {pg['pegada']:.3f} ({pg['k']} σ={pg['s']}) y entre 1.5σ y 2σ como poco {lj['lejos']:.3f} ({lj['k']} σ={lj['s']}); topes 0.95 y 1.02")
    ec = texto4["escalas"]
    ok(ec["techo"] >= ec["necesario"] - 1e-9 and abs(ec["alto"] - ec["altoEsperado"]) < 1e-12 and abs(ec["color"] - ec["colorEsperado"]) < 1e-12
       and abs(ec["alto"] - ec["altoConteo"]) > 0.1,
       f"escalas de la escena «borde»: techo {ec['techo']:.3f} ≥ el pico de las tres superficies ({ec['necesario']:.3f}), alto {ec['alto']:.3f} "
       f"del rango de σ de la escena (el del módulo 1 daría {ec['altoConteo']:.3f})")

    print()
    if fallos:
        print(f"  {len(fallos)} FALLO(S):")
        for f in fallos:
            print("   -", f)
        return 1
    print("  La matemática de la animación coincide con density() de R.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
