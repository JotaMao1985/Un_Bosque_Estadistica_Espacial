#!/usr/bin/env python3
"""
prueba_nucleo3d.py — la matemática de la animación 3D, contra R

Material de Estadística Espacial 2026-II (20929). Capítulo 5, módulo 1.

POR QUÉ EXISTE. `precalculo/nucleo3d/nucleo3d.js` dibuja la superficie
λ̂(u) = Σ k_σ(u − xᵢ) con CUATRO funciones de peso escritas a mano en
JavaScript. Una constante mal puesta —el soporte del Epanechnikov es √6·σ y
no √5·σ— no rompe nada: la loma se ve igual de bonita y enseña un núcleo que
no es el que `density()` calcula. Es el mismo defecto que el material
persigue en todas partes, y se prueba igual: contra R.

Dos bloques, y el segundo es el que decide:

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
NUCLEOS = ["gaussian", "epanechnikov", "quartic", "disc"]
# Error máximo contra el pico de R, con los puntos pegados a su píxel (ver arriba).
TOLERANCIA = {"gaussian": 0.0001, "epanechnikov": 0.0001, "quartic": 0.0001, "disc": 0.01}

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
