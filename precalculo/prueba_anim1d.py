#!/usr/bin/env python3
"""
prueba_anim1d.py — los fotogramas de las animaciones del apéndice A, contra R

Material de Estadística Espacial 2026-II (20929). Apéndice A.

POR QUÉ EXISTE. `precalculo/anim1d.js` decide qué se ve en cada momento de las
tres animaciones (módulos 3, 5 y 7). Toma la matemática de `densidad1d.js`,
que ya se prueba contra R, pero la COREOGRAFÍA es suya: dónde está el cursor,
qué histogramas quedan sellados, qué datos cuenta la ventana, qué tramo de la
curva va trazado. Un error ahí no rompe nada a la vista —la animación se
mueve igual de bien— y enseña una cifra distinta de la de la tabla que tiene
al lado. Por eso se prueba como el motor: contra lo que R publicó.

Tres bloques:

  1. CONTRA LO PUBLICADO en `apendicea_datos.json` (tolerancia 1e-8, la de sus 8 decimales): en el
     módulo 3, los cortes y conteos de los tres histogramas sellados, las
     alturas de cada uno y su promedio en x = 3, 5, 7 y 9 (la tabla del
     módulo) y la distancia al triangular en cada escalón de m; en el 5, el
     0.3 de la caja y los cinco pesos de la campana en x = 4, con los tres
     anchos de la tabla; en el 7, el d_k, los datos encerrados, la altura y
     el «globo» del ejemplo de x = 30, y los picos y las dos áreas de cada k.
  2. LO QUE LA ANIMACIÓN DICE SIN CIFRAS: correr el origen un ancho entero
     devuelve el mismo histograma; el tallo de cada dato mide lo que su loma
     en x (la simetría del núcleo); el rectángulo del k-NN tiene siempre
     área k/n; la curva a medio trazar no cuenta como pico la punta del trazo.
  3. LAS MUTACIONES. Se rompe una copia de `anim1d.js` de quince maneras y se
     exige que los bloques 1 y 2 fallen con cada una.

    python3 precalculo/prueba_anim1d.py
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
D1_MOTOR = RAIZ / "precalculo" / "densidad1d.js"
ANIM = Path(os.environ.get("A1D_MOTOR", RAIZ / "precalculo" / "anim1d.js"))
DATOS = json.loads((RAIZ / "precalculo" / "salidas" / "apendicea_datos.json").read_text(encoding="utf-8"))
SOLO_BLOQUES = os.environ.get("A1D_SIN_MUTACIONES") == "1"

fallos: list[str] = []


def ok(cond: bool, msg: str) -> None:
    print(("  OK   " if cond else "  MAL  ") + msg)
    if not cond:
        fallos.append(msg)


def node(codigo: str, entrada=None):
    # El D1 se pone en globalThis ANTES de cargar anim1d.js: así una copia
    # mutada en una carpeta temporal encuentra el motor sin ruta relativa.
    prog = (f"globalThis.D1 = require({json.dumps(str(D1_MOTOR))});\n"
            f"const A1D = require({json.dumps(str(ANIM))});\n"
            f"const E = {json.dumps(entrada)};\n" + codigo)
    r = subprocess.run(["node", "-e", prog], capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit(f"PARADO: node falló\n{r.stderr[-1500:]}")
    return json.loads(r.stdout)


# El JSON guarda las cifras con 8 decimales (jsonlite, `digits = 10`): contra
# él, 1e-8 es exacto. Los invariantes del bloque 2 se miden a 1e-12.
TOL = 1e-8


def cerca(a, b, tol=TOL):
    return abs(float(a) - float(b)) <= tol


def todos_cerca(a, b, tol=TOL):
    return len(a) == len(b) and all(cerca(x, y, tol) for x, y in zip(a, b))


# ---------------------------------------------------------------------
def bloque_origenes() -> None:
    print("\n1a · orígenes (módulo 3): el ASH del ejemplo a mano")
    e, an = DATOS["m3"]["ejemplo"], DATOS["m3"]["animacion"]
    cfg = {"x": e["datos"], "h": e["h"], "m": e["m"], "desde": e["extendida"]["desde"],
           "hasta": e["extendida"]["hasta"], "paso": an["paso"], "escalera": an["m"]}
    r = node("""
      const A = A1D.origenes(E.cfg), m = E.cfg.m, L = E.cfg.escalera.length;
      const span = E.cfg.hasta - E.cfg.desde;
      const out = {
        sellos: A.sellos.map(s => ({ cortes: s.cortes, conteos: s.conteos })),
        sellados: [...Array(m).keys()].map(j => A.fotograma(1, j / m).sellados),
        caidos_fin: A.fotograma(0, 1).barras.conteos,
        caidos_mitad: A.fotograma(0, 0.5).caidos,
        cursor: E.puntos.map(t => A.fotograma(2, (t - E.cfg.desde) / span).cursor),
        escalera: E.cfg.escalera.map((_, i) => { const f = A.fotograma(3, (i + 0.5) / L);
                                                 return { m: f.m, d: f.distancia }; }),
        ash_completo: A.fotograma(2, 1).cuantos === A.g.length,
        // Correr el origen un ancho entero devuelve el mismo histograma.
        periodo: (() => { const b = A.fotograma(1, 1).barras;
                          return Math.max(...A.g.map(t => Math.abs(A.alturaEn(b, t) - A.alturaEn(A.base, t)))); })(),
        // El primer dato que cae aterriza sobre una casilla vacía: altura 1/(nh).
        destino0: A.fotograma(0, 0.01).cae.destino,
        // El cursor va a un nodo y su promedio es la punta del ASH trazado.
        cursorPunta: Math.max(...[...Array(37).keys()].map(i => { const f = A.fotograma(2, (i * 0.618034) % 1);
          return Math.abs(f.cursor.media - f.ash[f.ash.length - 1]); }))
      };
      console.log(JSON.stringify(out));
    """, {"cfg": cfg, "puntos": e["puntos"]})
    ok(all(todos_cerca(s["cortes"], d["cortes"], 1e-8) and s["conteos"] == d["conteos"]
           for s, d in zip(r["sellos"], e["desplazados"])),
       f"los {e['m']} histogramas sellados: los cortes y conteos de la tabla")
    ok(all(s == list(range(j + 1)) for j, s in enumerate(r["sellados"])),
       "cada histograma queda sellado justo cuando el origen pasa por jδ")
    ok(r["caidos_fin"] == e["desplazados"][0]["conteos"] and r["caidos_mitad"] == len(e["datos"]) // 2,
       "los datos caen uno a uno y acaban en los conteos del histograma de base")
    ok(all(todos_cerca(c["alturas"], f) and cerca(c["media"], a)
           for c, f, a in zip(r["cursor"], e["f_j"], e["f_ash"])),
       "el cursor en x = " + ", ".join(str(p) for p in e["puntos"]) + ": las alturas y el promedio de la tabla")
    ok(all(s["m"] == m and cerca(s["d"], d) for s, m, d in zip(r["escalera"], an["m"], an["distancia"])),
       "la escalera de m y la distancia al triangular en cada escalón")
    ok(r["ash_completo"], "al final del barrido el ASH está trazado entero")
    ok(r["periodo"] < 1e-12, "correr el origen un ancho entero devuelve el mismo histograma")
    ok(cerca(r["destino0"], 1 / (len(e["datos"]) * e["h"])), "el primer dato aterriza a altura 1/(nh)")
    ok(r["cursorPunta"] < 1e-15, "el promedio del cursor es la punta del ASH trazado, en todo momento")


def bloque_desliza() -> None:
    print("\n1b · la ventana que se desliza (módulo 5)")
    m5 = DATOS["m5"]
    gs, an = m5["gaussiano"], m5["animacion"]
    casos = []
    for t in m5["tabla"]:
        casos.append({"x": gs["datos"], "h": t["h"], "x0": gs["x"], "desde": an["desde"],
                      "hasta": an["hasta"], "paso": an["paso"]})
    r = node("""
      const out = E.casos.map(cfg => {
        const A = A1D.desliza(cfg), span = cfg.hasta - cfg.desde, u0 = (cfg.x0 - cfg.desde) / span;
        const caja = A.fotograma(0, u0), campana = A.fotograma(1, 1);
        // La simetría: el tallo de cada dato mide lo que su loma en x, y la
        // suma de las lomas es la curva, en nodos de la rejilla.
        let sim = 0, sumaLomas = 0;
        for (let i = 0; i <= 20; i++) {
          const k = Math.round(i * (A.g.length - 1) / 20), f = A.fotograma(3, k / (A.g.length - 1));
          f.enLomas.forEach((v, j) => { sim = Math.max(sim, Math.abs(v - f.tallos[j])); });
          sumaLomas = Math.max(sumaLomas, Math.abs(f.enLomas.reduce((a, b) => a + b, 0) - A.curvaCampana[k]));
        }
        const ini = A.fotograma(1, 0);
        // La parada: alrededor de u0 la caja se queda en x0. Y la ventana va
        // siempre a un nodo, donde la punta de la columna es la del trazo.
        const parada = [-0.04, -0.015, 0, 0.015, 0.04].map(d => A.fotograma(0, A.u0 + d))
                                               .every(f => f.x === cfg.x0 && Math.abs(f.f - caja.f) < 1e-15);
        let nodos = 0, punta = 0;
        for (let i = 0; i < 37; i++) {
          const u = (i * 0.618034) % 1;
          for (const p of [0, 2]) {
            const f = A.fotograma(p, u), j = Math.round((f.x - cfg.desde) / cfg.paso);
            nodos = Math.max(nodos, Math.abs(f.x - A.g[j]));
            punta = Math.max(punta, Math.abs(f.f - f.traza[f.traza.length - 1]));
          }
        }
        return { parada: parada, nodos: nodos, punta: punta, cajaF: caja.f, cajaDentro: cfg.x.filter((_, i) => caja.tallos[i] > 0),
                 campF: campana.f, campPesos: campana.pesos, sim: sim, sumaLomas: sumaLomas,
                 continuo: Math.abs(ini.f - caja.f), x0: caja.x,
                 traza: A.fotograma(2, 1).cuantos === A.g.length };
      });
      console.log(JSON.stringify(out));
    """, {"casos": casos})
    for t, o in zip(m5["tabla"], r):
        ok(cerca(o["x0"], gs["x"]) and cerca(o["cajaF"], t["uniforme"]) and cerca(o["campF"], t["gaussiano"]),
           f"h = {t['h']}: en x = {gs['x']} la caja da {t['uniforme']} y la campana {t['gaussiano']:.4f}")
        ok(o["sim"] < 1e-15 and o["sumaLomas"] < 1e-12,
           f"h = {t['h']}: cada tallo mide lo que su loma en x, y las lomas suman la curva")
        ok(o["continuo"] < 1e-15 and o["traza"], f"h = {t['h']}: la campana nace de la caja, y el barrido traza la curva entera")
        ok(o["parada"], f"h = {t['h']}: la caja se detiene en x = {gs['x']} un momento del paso 1")
        ok(o["nodos"] == 0 and o["punta"] < 1e-15, f"h = {t['h']}: la ventana va a un nodo y su columna es la punta del trazo")
    uno = r[[t["h"] for t in m5["tabla"]].index(gs["h"])]
    ok(todos_cerca(uno["campPesos"], gs["terminos"]), "h = 1: los cinco pesos de la campana en x = 4, los del cálculo a mano")
    ok(uno["cajaDentro"] == an["caja_x4"], "h = 1: la caja de x = 4 encierra " + ", ".join(str(v) for v in an["caja_x4"]))


def bloque_vecinos() -> None:
    print("\n1c · la ventana del k-NN (módulo 7)")
    ed, an = DATOS["m7"]["edades"], DATOS["m7"]["animacion"]
    base = {"x": ed["datos"], "x0": ed["x"], "desde": an["desde"], "hasta": an["hasta"],
            "lejos": an["lejos"], "paso": an["paso"]}
    r = node("""
      const out = E.ks.map(k => {
        const A = A1D.vecinos(Object.assign({ k: k }, E.base));
        const ej = A.fotograma(0, 1), fin = A.fotograma(1, 1), cola = A.fotograma(2, 1);
        // El rectángulo: base 2 d_k, altura k/(2n d_k), área k/n en todo x.
        let area = 0;
        for (let i = 1; i < 40; i++) { const f = A.fotograma(1, i / 40);
          if (f.ventana.dk > 0) area = Math.max(area, Math.abs(f.ventana.alto * 2 * f.ventana.dk - k / E.base.x.length)); }
        // A medio subir hacia el primer pico, todavía ningún pico formado.
        const span = E.base.hasta - E.base.desde, x = E.base.x.slice().sort((a, b) => a - b);
        const subida = A.fotograma(1, ((x[0] + x[k - 1]) / 2 - 0.5 - E.base.desde) / span);
        const ini = A.fotograma(2, 0);
        // La ventana y la curva trazada son la misma cuenta: en cada nodo, la
        // altura del rectángulo es el último punto del trazo.
        let casa = 0;
        for (let i = 1; i <= 40; i++) { const f = A.fotograma(1 + (i % 2), (i * 0.618034) % 1);
          const a = f.ventana.alto, c = f.traza[f.traza.length - 1];
          if (Number.isFinite(a) && Number.isFinite(c)) casa = Math.max(casa, Math.abs(a - c)); }
        const dks = E.xs.map(t => A.dk(t));
        // Dónde caen los picos de la curva que la animación traza.
        const donde = [];
        for (let i = 1; i < A.g.length - 1 && A.g[i] <= E.base.hasta; i++)
          if (A.curva[i] > A.curva[i - 1] && A.curva[i] >= A.curva[i + 1]) donde.push(A.g[i]);
        return { donde: donde, casa: casa, dks: dks, dk: ej.ventana.dk, dentro: ej.ventana.dentro.length, alto: ej.ventana.alto,
                 globo: ej.ventana.globo, picos: fin.picos, areaDatos: fin.area, areaCola: cola.area,
                 rect: area, subida: subida.picos, iniCola: ini.x, mitad: A.fotograma(0, 0.2).dentro.length };
      });
      console.log(JSON.stringify(out));
    """, {"base": base, "ks": [p["k"] for p in an["por_k"]], "xs": XS_DK})
    for p, o in zip(an["por_k"], r):
        k = p["k"]
        # El k-ésimo vecino, por su cuenta: ordenar en Python. En x = 30 el
        # tercero y el cuarto empatan, y leer el equivocado daba la misma
        # cifra; en estos puntos no hay empate que lo tape.
        esperado = [sorted(abs(v - t) for v in ed["datos"])[k - 1] for t in XS_DK]
        ok(todos_cerca(o["dks"], esperado, 1e-12), f"k = {k}: d_k en {len(XS_DK)} puntos, contra el orden en Python")
        ok(o["casa"] < 1e-12, f"k = {k}: la altura de la ventana es la del trazo en cada nodo")
        if k == ed["k"]:
            ok(cerca(o["dk"], ed["d_k"]) and o["dentro"] == ed["dentro"],
               f"k = {k}, x = {ed['x']}: la ventana llega a d_k = {ed['d_k']} y encierra {ed['dentro']}")
            ok(cerca(o["alto"], ed["f"]) and cerca(o["globo"], ed["balloon"]),
               f"k = {k}: cobra k y da {ed['f']:.4f}; contando los {ed['dentro']}, {ed['balloon']:.4f}")
            ok(o["mitad"] < ed["dentro"], f"k = {k}: a medio crecer la ventana encierra menos que al final")
        ok(o["picos"] == p["picos"] and todos_cerca(o["donde"], p["donde"], 1e-9),
           f"k = {k}: {p['picos']} picos entre {an['desde']} y {an['hasta']}, en " + ", ".join(f"{v:g}" for v in p["donde"]))
        if p["area_datos"] is None:
            ok(o["areaDatos"] is None or o["areaDatos"] > 1e300,
               f"k = {k}: la curva es infinita en cada dato y el área no existe")
        else:
            ok(cerca(o["areaDatos"], p["area_datos"]) and cerca(o["areaCola"], p["area_cola"]),
               f"k = {k}: área {p['area_datos']:.4f} entre los datos y {p['area_cola']:.4f} con la cola")
        ok(o["rect"] < 1e-12, f"k = {k}: el rectángulo de la ventana tiene siempre área k/n")
        ok(o["subida"] == 0, f"k = {k}: subiendo hacia el primer pico, todavía no cuenta ninguno")
        ok(cerca(o["iniCola"], an["hasta"]), f"k = {k}: la cola arranca donde acaba el barrido")


# Puntos sin empates en el k-ésimo vecino para ningún k de 1 a 4.
XS_DK = [12.5, 21.3, 24.1, 27.7, 33.2, 38.9, 46.0]


MUTACIONES = [
    ("el promedio entre m", "media: suma(alt) / m }", "media: suma(alt) / n }"),
    ("los cortes corridos", "c[i] = cfg.desde + o + h * i;", "c[i] = cfg.desde + h * i;"),
    ("la casilla del cursor", "? hi.alturas[i - 1] : 0;", "? hi.alturas[Math.min(i, hi.alturas.length - 1)] : 0;"),
    ("el sello de cada origen", "if (s * delta <= o + 1e-9)", "if (s * delta < o)"),
    ("la escalera de m", "Math.floor(u * L)", "Math.round(u * L)"),
    ("el n·h del aporte", "return peso(s, t, c) / (n * h);", "return peso(s, t, c) / n;"),
    ("el centro de la ventana", "var v = (t - c) / h;", "var v = (t - c + 0.05) / h;"),
    ("la caja que se vuelve campana", "paso === 1 ? suave(u) : 1;", "paso === 1 ? 1 - suave(u) : 1;"),
    ("los empates del k-NN", "if (Math.abs(x[i] - t) <= r2) ids.push(i);", "if (Math.abs(x[i] - t) < r) ids.push(i);"),
    ("el k-ésimo vecino", "return d[k - 1];", "return d[k];"),
    ("la altura de la ventana", "alto: d > 0 ? k / (2 * n * d) : Infinity,", "alto: d > 0 ? k / (n * d) : Infinity,"),
    ("los picos ya formados", "picos: picos(tr) };", "picos: D1.modas(tr) };"),
    ("dónde arranca la cola", ": cfg.hasta + u * (cfg.lejos - cfg.hasta));", ": cfg.desde + u * (cfg.lejos - cfg.desde));"),
    ("la parada en x0", "var PARADA = 0.05,", "var PARADA = 0,"),
    ("el nodo de la ventana", "return { i: i, x: g[i] };", "return { i: i, x: t };"),
]


def bloque_mutaciones() -> None:
    print("\n3 · mutaciones: cada una tiene que tumbar la prueba")
    fuente = ANIM.read_text(encoding="utf-8")
    for que, de, a in MUTACIONES:
        if fuente.count(de) != 1:
            ok(False, f"la mutación «{que}» no encuentra su línea en el motor ({fuente.count(de)} veces)")
            continue
        with tempfile.TemporaryDirectory() as tmp:
            copia = Path(tmp) / "anim1d.js"
            copia.write_text(fuente.replace(de, a), encoding="utf-8")
            env = dict(os.environ, A1D_MOTOR=str(copia), A1D_SIN_MUTACIONES="1")
            rr = subprocess.run([sys.executable, __file__], capture_output=True, text=True, env=env)
            ok(rr.returncode != 0, f"cazada: {que}")


def main() -> int:
    print("\n=== prueba_anim1d.py ===" + (f"  (motor: {ANIM})" if SOLO_BLOQUES else ""))
    bloque_origenes()
    bloque_desliza()
    bloque_vecinos()
    if not SOLO_BLOQUES:
        bloque_mutaciones()
    print(f"\n{'PRUEBA EN VERDE' if not fallos else 'PRUEBA EN ROJO'}: "
          f"{len(fallos)} fallo(s)")
    return 1 if fallos else 0


if __name__ == "__main__":
    sys.exit(main())
