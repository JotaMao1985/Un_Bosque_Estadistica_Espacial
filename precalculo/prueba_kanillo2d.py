#!/usr/bin/env python3
"""
prueba_kanillo2d.py — la animación de K (el disco) y g (el anillo), probada contra R y por dentro

Material de Estadística Espacial 2026-II (20929). Capítulo 4, módulos 8 y 9.

POR QUÉ EXISTE. `precalculo/anim2d/kanillo2d.js` cuenta en el navegador los vecinos de cada punto en
su disco y en su anillo, con el peso de traslación o sin él, y calcula K con esas cuentas. Ningún
auditor de prosa ve esa aritmética: un `n * n` donde va `n * (n - 1)`, un `<` donde va `≤` (y los
pinos y las secuoyas tienen decenas de parejas justo en los nodos de r), un peso sin el valor
absoluto, el eje y sin invertir. La página se ve igual de bien. Se prueba contra R, y lo que no es
aritmética —el clic, el arrastre del borde del círculo, el guion, el teclado— se prueba en Node sin
DOM, que es lo más que permite un repo sin jsdom.

Seis bloques:

  1. LA ARITMÉTICA, contra R. `cap4_kanillo2d.json` sale de `genera_cap4_kanillo2d.R`: K con y sin
     peso en los 101 nodos (a mano en R, y contra `Kest` fuera de los nodos con empates), y las cuentas
     de cada punto en su disco y en su anillo en ocho r. Se exige lo mismo a 1e-12, en los tres patrones.
  2. LAS PROPIEDADES, sin R. Los pesos valen 1 o más y son simétricos; K sin corregir nunca pasa a la
     corregida; K crece con r; el azar de un disco entero es (n − 1)πr²/|W|; los puntos de partida
     cumplen lo que el texto supone; y lo que la prosa del módulo 9 afirma de las secuoyas (en el r donde
     g vuelve a 1, K sigue claramente por encima) es cierto con la K de aquí y la g publicada.
  3. LA GEOMETRÍA: el cuadrado de la ventana sin deformar y con el eje y hacia arriba, el clic que
     encuentra cada punto en su píxel, y el arrastre del borde del círculo que da el radio.
  4. LA MÁQUINA, sobre las dos escenas: `normaliza` (r en nodos, patrón, foco al cambiar de patrón, lo
     que cada escena no admite), el guion que recorre los pasos, los estados que dependen del patrón
     (el r en que g vuelve a 1, el punto del borde), el ciclo de un `n` que cambia con el patrón, el
     teclado y el puntero.
  5. LO QUE LEE LA PERSONA, para los tres patrones × 101 r × focos × vistas × pesos × las dos escenas:
     ningún texto, lectura ni descripción lleva NaN, undefined, Infinity ni null; ninguno dice
     «significativo»; las cifras que escriben son las del cálculo; y la frase «arrastra» solo aparece
     cuando es cierta.
  6. EL DIBUJO, con un lienzo falso: ningún número que llegue a un método de trazo es NaN ni infinito.

`KANILLO2D_MOTOR` y `ANIM2D_NUCLEO` redirigen los dos archivos a copias: así
`prueba_mutaciones_anim2d.py` comprueba que esta prueba sabe fallar.

    python3 precalculo/prueba_kanillo2d.py
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
PRE = RAIZ / "precalculo"
KANILLO = Path(os.environ.get("KANILLO2D_MOTOR", PRE / "anim2d" / "kanillo2d.js"))
NUCLEO = Path(os.environ.get("ANIM2D_NUCLEO", PRE / "anim2d" / "anim2d.js"))
REF = PRE / "salidas" / "cap4_kanillo2d.json"
DATOS = PRE / "salidas" / "cap4_datos.json"

TOL = 1e-12         # contra R: sumas de unas 4 000 parejas en doble precisión; medido ≤ 5e-16
fallos: list[str] = []


def ok(cond: bool, msg: str) -> None:
    print(("  OK   " if cond else "  MAL  ") + msg)
    if not cond:
        fallos.append(msg)


def node(codigo: str, entrada: dict | None = None) -> dict:
    """Corre JavaScript contra los motores REALES (los mismos archivos que se publican)."""
    prog = (f"const A = require({json.dumps(str(NUCLEO))}); global.Anim2D = A;\n"
            f"const KA = require({json.dumps(str(KANILLO))}); const M = KA.matematica;\n"
            f"const ENTRADA = {json.dumps(entrada)};\n"
            "const T = [];\n"
            "const t = (nombre, cond) => T.push([nombre, !!cond]);\n"
            "const DATOS = { patrones: ENTRADA.ref.patrones, g: ENTRADA.g };\n"
            "const nueva = (escena, ganchos) => A.maquina(KA.creaDef(DATOS, { escena }), ganchos || {});\n" + codigo)
    r = subprocess.run(["node", "-"], input=prog, capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit(f"PARADO: node falló\n{r.stderr}")
    return json.loads(r.stdout)


def muestra(res: dict) -> None:
    for nombre, bien in res["T"]:
        ok(bien, nombre)


def main() -> int:
    print("\n=== prueba_kanillo2d.py ===")
    ref = json.loads(REF.read_text(encoding="utf-8"))
    d4 = json.loads(DATOS.read_text(encoding="utf-8"))
    entrada = {"ref": ref, "g": {k: d4["m9"][k] for k in ("cells", "japanesepines", "redwood")},
               "nn_min": {k: d4["m3"][k]["nn_min"] for k in ("cells", "japanesepines", "redwood")}}

    # ---- 1 · la aritmética, contra R ----------------------------------------
    print("\n1 · la aritmética, contra R (K a mano y Kest; las cuentas de cada punto)")
    res = node(r"""
      const sal = {};
      for (const nm of M.PATRONES) {
        const R = ENTRADA.ref.patrones[nm], P = M.prepara(R);
        const kt = M.curvaK(P, true), ks = M.curvaK(P, false);
        let dT = 0, dS = 0, dKestT = 0, dKestS = 0, limpios = 0;
        kt.forEach((v, i) => {
          dT = Math.max(dT, Math.abs(v - R.k_traslacion[i])); dS = Math.max(dS, Math.abs(ks[i] - R.k_sin[i]));
          if (R.empates[i] === 0) { limpios++; dKestT = Math.max(dKestT, Math.abs(v - R.kest_traslacion[i])); dKestS = Math.max(dKestS, Math.abs(ks[i] - R.kest_sin[i])); }
        });
        let dDisco = 0, dPeso = 0, dAnillo = 0, casos = 0;
        for (const c of R.cuentas) for (let i = 0; i < P.n; i++) {
          casos++;
          dDisco = Math.max(dDisco, Math.abs(M.cuentaDisco(P, i, c.r, false) - c.disco[i]));
          dPeso = Math.max(dPeso, Math.abs(M.cuentaDisco(P, i, c.r, true) - c.disco_peso[i]));
          dAnillo = Math.max(dAnillo, Math.abs(M.cuentaAnillo(P, i, c.r, ENTRADA.ref.meta.h_anillo) - c.anillo[i]));
        }
        sal[nm] = { dT, dS, dKestT, dKestS, limpios, nodos: kt.length, dDisco, dPeso, dAnillo, casos,
                    empates: R.empates.filter(e => e > 0).length, rEnRejilla: ENTRADA.ref.meta.r.every((r, i) => Math.abs(r - M.rDe(i)) < 1e-15) };
      }
      sal.hAnillo = M.H_ANILLO === ENTRADA.ref.meta.h_anillo && M.EPS === ENTRADA.ref.meta.eps;
      console.log(JSON.stringify({ sal }));
    """, entrada)["sal"]
    for nm in ("cells", "japanesepines", "redwood"):
        s = res[nm]
        ok(s["nodos"] == 101 and s["rEnRejilla"], f"{nm}: los 101 nodos de r son los de R y los del capítulo")
        ok(s["dT"] < TOL, f"{nm}: K con el peso de traslación, contra la de R a mano: {s['dT']:.1e}")
        ok(s["dS"] < TOL, f"{nm}: K sin corregir, contra la de R a mano: {s['dS']:.1e}")
        ok(s["dKestT"] < TOL and s["dKestS"] < TOL,
           f"{nm}: y contra Kest en los {s['limpios']} nodos sin empates: {max(s['dKestT'], s['dKestS']):.1e} "
           f"({s['empates']} nodos con parejas justo a esa distancia, donde Kest bina a su manera)")
        ok(s["dDisco"] == 0 and s["dAnillo"] == 0,
           f"{nm}: los vecinos de cada punto en su disco y en su anillo, exactos ({s['casos']} casos)")
        ok(s["dPeso"] < TOL, f"{nm}: y con su peso: {s['dPeso']:.1e}")
    ok(res["hAnillo"], "el ancho del anillo y la tolerancia de los empates son los de R")

    # ---- 2 · propiedades, sin R ---------------------------------------------
    print("\n2 · propiedades exactas, sin R")
    muestra(node(r"""
      for (const nm of M.PATRONES) {
        const P = M.prepara(ENTRADA.ref.patrones[nm]), n = P.n;
        let pesosMal = 0, asim = 0;
        for (let i = 0; i < n; i++) for (let j = 0; j < n; j++) {
          if (i !== j && M.rDe(M.NODOS) >= P.d[i * n + j] && !(P.w[i * n + j] >= 1)) pesosMal++;
          if (P.w[i * n + j] !== P.w[j * n + i] || P.d[i * n + j] !== P.d[j * n + i]) asim++;
        }
        t(nm + ': los pesos de traslación valen 1 o más, y pesos y distancias son simétricos', pesosMal === 0 && asim === 0);
        const kt = M.curvaK(P, true), ks = M.curvaK(P, false);
        t(nm + ': K sin corregir nunca pasa a la corregida', ks.every((v, i) => v <= kt[i] + 1e-15));
        t(nm + ': K crece con r (es acumulativa) y vale 0 en r = 0', kt[0] === 0 && kt.every((v, i) => i === 0 || v >= kt[i - 1]));
        const r = 0.1;
        t(nm + ': el azar de un disco entero es (n − 1) π r² / |W|', Math.abs(M.azarDisco(P, r) - (n - 1) * Math.PI * r * r / P.A) < 1e-15);
        t(nm + ': y el de un anillo, (n − 1) π ((r + h)² − (r − h)²) / |W|, sin radio interior negativo',
          Math.abs(M.azarAnillo(P, r, 0.01) - (n - 1) * Math.PI * (0.11 * 0.11 - 0.09 * 0.09) / P.A) < 1e-15 &&
          Math.abs(M.azarAnillo(P, 0.005, 0.01) - (n - 1) * Math.PI * 0.015 * 0.015 / P.A) < 1e-15);
        const g = M.focoGrupo(P);
        t(nm + ': el punto de partida tiene su disco de ' + M.R_GRUPO + ' entero dentro de la ventana', M.borde(P, g) >= M.R_GRUPO);
        const b = M.focoBorde(P);
        t(nm + ': el del paso del borde está más cerca del borde que el de partida, y a menos de ' + M.R_BORDE, b >= 0 && M.borde(P, b) < M.borde(P, g) && M.borde(P, b) < M.R_BORDE);
        let todos = 0; for (let i = 0; i < n; i++) todos += M.cuentaDisco(P, i, 0.1, false);
        t(nm + ': las parejas dibujadas son la mitad de las ordenadas que suma K', M.parejas(P, 0.1, 0.01, false).length / 2 === todos / 2);
      }
      // Lo que la prosa del módulo 9 y el paso 3 del anillo afirman de las secuoyas, con la K de aquí y la g publicada.
      {
        const P = M.prepara(ENTRADA.ref.patrones.redwood), G = ENTRADA.g.redwood;
        const i1 = Math.round(G.r_vuelve_a_1 / M.PASO_R), k = M.K(P, M.rDe(i1), true) / (Math.PI * M.rDe(i1) ** 2);
        t('secuoyas: donde g vuelve a 1 (r = ' + G.r_vuelve_a_1 + '), g vale ' + G.g_obs[i1].toFixed(3) + ' y K/πr² ' + k.toFixed(3) + ': arrastra', Math.abs(G.g_obs[i1] - 1) < 0.05 && k > 1.5);
        let bajo = 0;
        for (let i = 1; i <= M.NODOS; i++) if (M.rDe(i) >= ENTRADA.nn_min.redwood - 1e-12 && M.K(P, M.rDe(i), true) <= Math.PI * M.rDe(i) ** 2) bajo++;
        t('secuoyas: K no baja de π r² en ningún nodo desde su pareja más próxima (' + ENTRADA.nn_min.redwood + ')', bajo === 0);
        const i15 = Math.round(0.15 / M.PASO_R);
        t('secuoyas: g vuelve a pasar de 1 después (no se queda en 1: ' + G.g_obs[i15].toFixed(3) + ' en r = 0.15), y el texto no lo niega', G.g_obs[i15] > 1);
      }
      const falla = f => { try { f(); return false; } catch (e) { return true; } };
      const R0 = ENTRADA.ref.patrones.cells;
      t('un patrón con un solo punto se rechaza', falla(() => M.prepara({ x: [0.5], y: [0.5], ventana: [0, 0, 1, 1] })));
      t('uno con distinto número de x y de y, también', falla(() => M.prepara({ x: [0.1, 0.2], y: [0.1], ventana: [0, 0, 1, 1] })));
      t('y una ventana sin área', falla(() => M.prepara({ x: R0.x, y: R0.y, ventana: [0, 0, 0, 1] })));
      t('una g publicada en otra rejilla hace que la pieza no monte',
        falla(() => KA.creaDef({ patrones: ENTRADA.ref.patrones, g: Object.assign({}, ENTRADA.g, { cells: Object.assign({}, ENTRADA.g.cells, { r: ENTRADA.g.cells.r.map(r => r * 2) }) }) }, { escena: 'anillo' })));
      t('y una escena que no existe, tampoco', falla(() => KA.creaDef(DATOS, { escena: 'cono' })));
      console.log(JSON.stringify({ T }));
    """, entrada))

    # ---- 3 · la geometría ----------------------------------------------------
    print("\n3 · la geometría: el cuadrado, el clic y el arrastre del borde")
    muestra(node(r"""
      for (const nm of M.PATRONES) {
        const P = M.prepara(ENTRADA.ref.patrones[nm]);
        for (const [w, h] of [[540, 405], [298, 268], [800, 600]]) {
          const m = { l: 10, r: 10, t: w > 560 ? 30 : 10, b: 10 }, a = M.ajuste(w, h, P.v, m);
          const lado = (P.v[2] - P.v[0]) * a.s, alto = (P.v[3] - P.v[1]) * a.s;
          const iy = P.y.indexOf(Math.max.apply(null, P.y)), iyB = P.y.indexOf(Math.min.apply(null, P.y));
          t(nm + ' ' + w + '×' + h + ': el cuadrado cabe, sin deformar, y el eje y va hacia arriba',
            Math.abs(lado - alto) < 1e-9 && a.x(P.v[0]) >= m.l - 1e-9 && a.x(P.v[2]) <= w - m.r + 1e-9 && a.y(P.v[3]) >= m.t - 1e-9 && a.y(P.v[1]) <= h - m.b + 1e-9 &&
            a.y(P.y[iy]) < a.y(P.y[iyB]));
          let ida = 0;
          for (let i = 0; i < P.n; i++) ida = Math.max(ida, Math.abs(a.ux(a.x(P.x[i])) - P.x[i]), Math.abs(a.uy(a.y(P.y[i])) - P.y[i]));
          let malos = 0;
          for (let i = 0; i < P.n; i++) if (M.puntoEn(P, a, a.x(P.x[i]), a.y(P.y[i]), 12) !== i) malos++;
          t(nm + ' ' + w + '×' + h + ': píxel → ventana es la inversa (' + ida.toExponential(1) + '), y el clic sobre cada punto lo encuentra (' + malos + ' fallos)', ida < 1e-12 && malos === 0);
          t(nm + ' ' + w + '×' + h + ': un clic lejos de todo punto no encuentra ninguno', M.puntoEn(P, a, -50, -50, 12) === -1);
        }
      }
      // lo que se arrastra se aplica sin transición; un clic puede animarse (anim2d.gestos)
      {
        const g = A.gestos(ev => ev.tipo === 'abajo' ? (ev.x > 50 ? { poner: { ir: 9 }, captura: true } : { poner: { foco: 2 } }) : ev.tipo === 'mueve' ? { poner: { ir: 12 } } : null);
        const c1 = g({ tipo: 'abajo', x: 10, y: 0 });
        t('un clic se aplica con su transición (no lleva corte)', c1 && c1.corte === false);
        const c2 = g({ tipo: 'abajo', x: 60, y: 0 }), c3 = g({ tipo: 'mueve', x: 70, y: 0 });
        t('el principio de un arrastre y cada movimiento, sin transición: el círculo sigue al puntero', c2 && c2.corte === true && c3 && c3.corte === true);
      }
      // el puntero de la pieza: clic, marca, arrastre del borde del círculo
      for (const escena of ['disco', 'anillo']) {
        const def = KA.creaDef(DATOS, { escena }), I = def.interno;
        const m = A.maquina(def, {});
        m.avanza(Infinity);
        const c = { w: 540, h: 405 }, a = I.ajusteDe(c, m.E.patron), P = I.P[m.E.patron];
        const otro = (m.E.foco + 5) % P.n;
        const pc = def.puntero({ tipo: 'abajo', x: a.x(P.x[otro]), y: a.y(P.y[otro]) }, m.E, m.V, c);
        t(escena + ': un clic sobre un punto lo pone en foco', pc && pc.poner.foco === otro);
        const pm = def.puntero({ tipo: 'mueve', x: a.x(P.x[otro]), y: a.y(P.y[otro]) }, m.E, m.V, c);
        t(escena + ': pasar por encima lo marca y pone la mano', pm && pm.poner.hover === otro && pm.cursor === 'pointer');
        // el borde del círculo, en una dirección sin puntos cerca
        const G = I.geometria(m.V), fx = a.x(P.x[m.E.foco]), fy = a.y(P.y[m.E.foco]);
        const ang = [0, 1, 2, 3, 4, 5, 6, 7].map(k => k * Math.PI / 4).find(t0 => M.puntoEn(P, a, fx + G.rout * a.s * Math.cos(t0), fy + G.rout * a.s * Math.sin(t0), 14) < 0);
        const bx = fx + G.rout * a.s * Math.cos(ang), by = fy + G.rout * a.s * Math.sin(ang);
        const pa = def.puntero({ tipo: 'abajo', x: bx, y: by }, m.E, m.V, c);
        t(escena + ': bajar sobre el borde del círculo empieza un arrastre (captura) con el r de ese radio',
          pa && pa.captura === true && Math.abs(pa.poner.ir - G.rout / M.PASO_R) < 1e-6);
        const pd = def.puntero({ tipo: 'mueve', x: fx + 2 * G.rout * a.s * Math.cos(ang), y: fy + 2 * G.rout * a.s * Math.sin(ang) }, m.E, m.V, c);
        t(escena + ': y moverlo lleva el radio con él (el doble de lejos, el doble de r)', pd && Math.abs(pd.poner.ir - 2 * G.rout / M.PASO_R) < 1e-6);
        def.puntero({ tipo: 'arriba', x: bx, y: by }, m.E, m.V, c);
        const pl = def.puntero({ tipo: 'mueve', x: fx + 2 * G.rout * a.s * Math.cos(ang), y: fy + 2 * G.rout * a.s * Math.sin(ang) }, m.E, m.V, c);
        t(escena + ': al soltar, moverse ya no cambia r', !pl || !('ir' in pl.poner));
        // con el dedo, el borde gana a un punto vecino si el toque está más cerca del borde que del punto
        {
          let probados = 0, malos = 0;
          for (let k = 0; k < 72; k++) {
            const t0 = k * Math.PI / 36, bx2 = fx + G.rout * a.s * Math.cos(t0), by2 = fy + G.rout * a.s * Math.sin(t0);
            const i = M.puntoEn(P, a, bx2, by2, 18);
            if (i < 0) continue;
            const dP = Math.hypot(a.x(P.x[i]) - bx2, a.y(P.y[i]) - by2);
            if (dP <= 0.5) continue;                                   // el punto está justo en el borde: gana el punto
            probados++;
            const pt = def.puntero({ tipo: 'abajo', x: bx2, y: by2, tactil: true }, m.E, m.V, c);
            if (!(pt && pt.captura)) malos++;
          }
          t(escena + ': con el dedo sobre el borde y un punto a menos de 18 px pero más lejos que el borde, empieza el arrastre (' + probados + ' sitios, ' + malos + ' mal)', malos === 0);
        }
        t(escena + ': un clic en el vacío no hace nada', def.puntero({ tipo: 'abajo', x: 2, y: 2 }, m.E, m.V, c) === null);
        t(escena + ': antes del primer dibujo no hay lienzo y el puntero no hace nada', def.puntero({ tipo: 'abajo', x: 100, y: 100 }, m.E, m.V, { w: 0, h: 0 }) === null);
      }
      console.log(JSON.stringify({ T }));
    """, entrada))

    # ---- 4 · la máquina ------------------------------------------------------
    print("\n4 · la máquina, sobre las dos escenas")
    muestra(node(r"""
      for (const escena of ['disco', 'anillo']) {
        const def = KA.creaDef(DATOS, { escena }), C = def.interno.C, P = def.interno.P;
        let m = nueva(escena);
        t(escena + ': empieza en el paso 1, con las secuoyas y su punto de partida', m.E.paso === 1 && m.E.patron === 'redwood' && m.E.foco === C.redwood.grupo);
        for (const malo of [NaN, Infinity, 'tres', null, undefined]) m.poner({ ir: malo });
        t(escena + ': poner rechaza lo que no es un número en r', m.E.ir === def.inicial().ir);
        m.poner({ ir: 7.6 }); const r1 = m.E.ir; m.poner({ ir: 400 }); const r2 = m.E.ir; m.poner({ ir: -3 });
        t(escena + ': r va en nodos, de 0 a ' + M.NODOS + ' (redondea y acota)', r1 === 8 && r2 === M.NODOS && m.E.ir === 0);
        m.poner({ patron: 'cono' });
        t(escena + ': un patrón que no existe no entra', m.E.patron === 'redwood');
        m.poner({ patron: 'japanesepines' }); m.poner({ foco: 60, hover: 61 });
        m.poner({ patron: 'cells' });
        t(escena + ': cambiar a un patrón con menos puntos lleva el foco a su punto de partida y quita la marca', m.E.foco === C.cells.grupo && m.E.foco < P.cells.n && m.E.hover === -1);
        m.poner({ patron: 'redwood', foco: 7 });
        t(escena + ': y si el cambio trae su foco, se respeta', m.E.patron === 'redwood' && m.E.foco === 7);
        m.poner({ foco: 999 });
        t(escena + ': el foco se acota a los puntos del patrón', m.E.foco === P.redwood.n - 1);
        m.poner({ hueco: 1, peso: 'ninguno' });
        t(escena + ': ' + (escena === 'disco' ? 'el disco no admite el anillo, y sí el peso a 1' : 'el anillo admite el anillo, y el peso se queda en el de traslación'),
          escena === 'disco' ? m.E.hueco === 0 && m.E.peso === 'ninguno' : m.E.hueco === 1 && m.E.peso === 'traslacion');
        // el paso sigue a los conmutadores: el texto que se ve habla de lo que se dibuja
        const mp = nueva(escena);
        if (escena === 'anillo') {
          mp.poner({ hueco: 1 }); const a1 = mp.E.paso; mp.poner({ todos: 1 }); const a2 = mp.E.paso; mp.poner({ hueco: 0 }); const a3 = mp.E.paso; mp.poner({ todos: 0 });
          t('anillo: pulsar el anillo lleva al paso 3, todas las parejas al 5, el disco con todas al 4, y un punto con el disco al 2', a1 === 3 && a2 === 5 && a3 === 4 && mp.E.paso === 2);
        } else {
          mp.poner({ todos: 1 }); const d1 = mp.E.paso; mp.poner({ todos: 0 }); const d2 = mp.E.paso; mp.poner({ peso: 'ninguno' });
          t('disco: todas las parejas lleva al paso 3, volver a un punto desde ahí al 2, y quitar el peso al 4', d1 === 3 && d2 === 2 && mp.E.paso === 4);
        }
        // el ciclo del punto en foco: su n es el del patrón
        const ciclo = def.mandos.find(x => x.id === 'foco');
        // con dos patrones de n distinto: con uno solo, un n fijo que coincidiera con el suyo pasaría
        const vuelta = nm => { const E1 = Object.assign({}, m.E, { patron: nm, foco: P[nm].n - 1 });
          return A.cicla(ciclo, E1, 1) === 0 && A.cicla(ciclo, Object.assign({}, E1, { foco: 0 }), -1) === P[nm].n - 1; };
        t(escena + ': el ciclo del foco da la vuelta con el n del patrón que se mira (' + P.cells.n + ' células, ' + P.japanesepines.n + ' pinos)', vuelta('cells') && vuelta('japanesepines'));
        t(escena + ': y con un n fijo también', A.cicla({ id: 'k', n: 5 }, { k: 4 }, 1) === 0);
        // el guion
        const ev = [];
        m = nueva(escena, { guion: on => ev.push(on) });
        m.reproducir(); m.avanza(Infinity);
        t(escena + ': el guion recorre los ' + def.pasos.length + ' pasos y se detiene en el último', m.E.paso === def.pasos.length && !m.guion.activo && ev.join() === 'true,false');
        t(escena + ': y al acabar, lo visible es lo que el estado dice', m.V.ir === m.E.ir && m.V.hueco === m.E.hueco);
        // los pasos que dependen del patrón
        for (const nm of M.PATRONES) {
          const mm = nueva(escena); mm.poner({ patron: nm }); mm.ir(1, { corte: true });
          t(escena + ', ' + nm + ': el paso 1 pone el punto de partida de ese patrón', mm.E.foco === C[nm].grupo);
          if (escena === 'anillo') {
            mm.ir(2, { corte: true });
            const rv = ENTRADA.g[nm].r_vuelve_a_1;
            const iv = Math.round((rv == null ? M.R_GRUPO : rv) / M.PASO_R);
            t('anillo, ' + nm + ': el paso 2 va al r en que g vuelve a 1 (' + (rv == null ? 'no vuelve: ' + M.R_GRUPO : rv) + ')', mm.E.ir === iv);
            // y los pasos 3 a 5 también, aunque se llegue a ellos sin pasar por el 2
            const llega = [3, 4, 5].every(k => { const m2 = nueva('anillo'); m2.poner({ patron: nm }); m2.ir(k, { corte: true }); return m2.E.ir === iv; });
            t('anillo, ' + nm + ': y los pasos 3, 4 y 5 ponen ese mismo r aunque se llegue a ellos directamente', llega);
          } else {
            mm.ir(4, { corte: true });
            t('disco, ' + nm + ': el paso 4 pone el punto del borde y quita el peso', mm.E.foco === C[nm].borde && mm.E.peso === 'ninguno');
          }
        }
        m = nueva(escena); m.reproducir(); m.avanza(1); m.poner({ foco: 3 });
        t(escena + ': un gesto interrumpe el guion', !m.guion.activo);
        // teclado
        const E0 = Object.assign(def.inicial(), { foco: P.redwood.n - 1, ir: 50 });
        t(escena + ': → en el último punto vuelve al primero, ← en el primero va al último',
          def.tecla({ key: 'ArrowRight' }, E0).foco === 0 && def.tecla({ key: 'ArrowLeft' }, Object.assign({}, E0, { foco: 0 })).foco === P.redwood.n - 1);
        t(escena + ': ↑ ↓ mueven r un nodo; Re Pág y Av Pág, diez; Inicio y Fin, a los extremos',
          def.tecla({ key: 'ArrowUp' }, E0).ir === 51 && def.tecla({ key: 'ArrowDown' }, E0).ir === 49 && def.tecla({ key: 'PageUp' }, E0).ir === 60 &&
          def.tecla({ key: 'PageDown' }, E0).ir === 40 && def.tecla({ key: 'Home' }, E0).ir === 0 && def.tecla({ key: 'End' }, E0).ir === M.NODOS);
        t(escena + ': otra tecla no hace nada', def.tecla({ key: 'x' }, E0) === null);
        // la geometría visible: el anillo es [r − h, r + h]; el disco, [0, r]
        const Ga = def.interno.geometria({ ir: 58, hueco: 1 }), Gd = def.interno.geometria({ ir: 58, hueco: 0 });
        t(escena + ': ' + (escena === 'anillo' ? 'el anillo visible va de r − h a r + h, y el disco de 0 a r' : 'en el disco no hay anillo aunque se pida'),
          escena === 'anillo' ? Math.abs(Ga.rin - (M.rDe(58) - M.H_ANILLO)) < 1e-15 && Math.abs(Ga.rout - (M.rDe(58) + M.H_ANILLO)) < 1e-15 && Gd.rin === 0 && Gd.rout === M.rDe(58)
                              : Ga.rin === 0 && Ga.rout === M.rDe(58));
      }
      console.log(JSON.stringify({ T }));
    """, entrada))

    # ---- 5 · lo que lee la persona ------------------------------------------
    print("\n5 · textos, lectura y descripción, en todos los estados")
    muestra(node(r"""
      const malo = s => /NaN|undefined|Infinity|null/.test(s);
      for (const escena of ['disco', 'anillo']) {
        const def = KA.creaDef(DATOS, { escena }), I = def.interno;
        const est = o => { const E = Object.assign(def.inicial(), o); return Object.assign(E, def.normaliza(Object.assign({}, o), def.inicial())); };
        let n = 0, mal = 0, signif = 0;
        for (const patron of M.PATRONES) {
          const P = I.P[patron];
          const focos = [0, I.C[patron].grupo, I.C[patron].borde, P.n - 1];
          for (let ir = 0; ir <= M.NODOS; ir++) {
            for (const foco of focos) for (const hueco of [0, 1]) for (const todos of [0, 1]) for (const peso of ['traslacion', 'ninguno']) {
              if (ir % 4 && foco !== I.C[patron].grupo) continue;          // todos los r con el foco de partida; uno de cada cuatro con los demás
              const E = est({ paso: 1, patron, ir, foco, hueco, todos, peso });
              const textos = def.pasos.map(p => (typeof p.titulo === 'function' ? p.titulo(E) : p.titulo) + ' ' + p.texto(E))
                .concat(def.lectura(E).filter(l => l[0] !== '¿es significativo?').map(l => l[0] + ' ' + l[1])).concat([def.alt(E)]);
              textos.forEach(s => { n++; if (malo(s)) mal++; if (/significativ/i.test(s)) signif++; });
            }
          }
        }
        t(escena + ': ningún texto, lectura ni descripción lleva NaN, undefined, Infinity ni null (' + n + ' cadenas, ' + mal + ' malas)', mal === 0);
        t(escena + ': ninguno dice «significativo» (sin la banda del módulo 11 no hay veredicto)', signif === 0);
        // LA AUDITORÍA DE LAS CINCO ANIMACIONES (2026-10-02)
        {
          // ningún texto, en ningún estado, dice «más (o menos) parejas de las que daría el azar», ni «casi», ni «al lado»
          let veredictos = 0, casi = 0, alLado = 0, sinBanda = 0;
          for (const patron of M.PATRONES) for (let ir = 0; ir <= M.NODOS; ir += 1) for (const hueco of (escena === 'anillo' ? [0, 1] : [0])) {
            const Ei = est({ patron, ir, hueco, foco: I.C[patron].grupo });
            const tx = def.pasos.map(pp => (typeof pp.titulo === 'function' ? pp.titulo(Ei) : pp.titulo) + ' ' + pp.texto(Ei)).join(' ');
            if (/parejas de las que daría el azar/.test(tx)) veredictos++;
            if (/casi encima|casi las parejas/.test(tx)) casi++;
            if (/al lado/.test(tx)) alLado++;
            if (!def.lectura(Ei).some(l => l[0] === '¿es significativo?' && /envolvente del módulo 11/.test(l[1]))) sinBanda++;
          }
          t(escena + ': ningún paso dice «más/menos parejas de las que daría el azar» (' + veredictos + ' estados), ni «casi» (' + casi + '), ni «al lado» (' + alLado + ')',
            veredictos === 0 && casi === 0 && alLado === 0 && !/al lado/.test(def.aria));
          t(escena + ': la lectura lleva siempre la fila «¿es significativo?», como el simulador de K y L (' + sinBanda + ' estados sin ella)', sinBanda === 0);
          // el pie nombra los empates (la causa medida de la diferencia con la curva publicada), no «r pequeño»
          t(escena + ': el pie atribuye la diferencia con Kest a los empates', /<strong>empates<\/strong>/.test(def.pie) && !/r pequeño/.test(def.pie));
          // la descripción no da coordenadas negativas en «un cuadrado de lado 1» (la ventana de las secuoyas es [0, 1] × [−1, 0])
          let negativas = 0;
          for (let foco = 0; foco < I.P.redwood.n; foco++) if (/\(-|, -/.test(def.alt(est({ patron: 'redwood', foco })))) negativas++;
          t(escena + ': la descripción no escribe coordenadas negativas (' + negativas + ' puntos)', negativas === 0);
          // la región viva: lo que cambió, con su cuenta; nada si solo se pasa el ratón
          const E0 = est({ patron: 'redwood', ir: 40, foco: I.C.redwood.grupo, hueco: escena === 'anillo' ? 1 : 0 });
          t(escena + ': el anuncio calla si solo se pasa el ratón', def.anuncio(Object.assign({}, E0, { hover: 3 }), E0) === null);
          t(escena + ': dice el punto nuevo con su cuenta y la del azar', /^Punto \d+ de 62: \d+ vecinos? en su (disco|anillo); el azar daría \d+\.\d\d\.$/.test(def.anuncio(est({ patron: 'redwood', ir: 40, foco: 3, hueco: E0.hueco }), E0)));
          const an = def.anuncio(est({ patron: 'redwood', ir: 58, foco: E0.foco, hueco: E0.hueco }), E0);
          t(escena + ': y el r nuevo con K' + (escena === 'anillo' ? ' y g' : '') + ', las del cálculo', an.indexOf('r = 0.1450') === 0 && an.indexOf(I.cuenta(est({ patron: 'redwood', ir: 58, foco: E0.foco })).q.toFixed(2)) > 0 &&
            (escena !== 'anillo' || an.indexOf('g vale ' + ENTRADA.g.redwood.g_obs[58].toFixed(2)) > 0));
          const vt = def.mandos.find(mm => mm.id === 'ir').valorTexto;
          t(escena + ': el deslizador dice a un lector r y K, no solo r', /^r = 0\.1450: K vale \d+\.\d\d veces π r²/.test(vt(58, E0)));
        }
        if (escena === 'disco') {
          // en el paso 4, cambiar el peso es lo que el paso pide: no se va al paso 2
          const m4 = A.maquina(KA.creaDef(DATOS, { escena: 'disco' }), {});
          m4.ir(4, { corte: true }); m4.poner({ peso: 'traslacion' }); const p1 = m4.E.paso; m4.poner({ peso: 'ninguno' });
          t('disco: en el paso 4, pulsar «Traslación» y luego «Sin peso» lo deja en el paso 4', p1 === 4 && m4.E.paso === 4);
          // la cuenta con pesos solo donde el peso está explicado
          const l1 = def.lectura(est({ paso: 1, patron: 'redwood', ir: 24, foco: I.C.redwood.grupo })).map(l => l[1]).join(' ');
          const l4 = def.lectura(est({ paso: 4, patron: 'redwood', ir: 60, foco: I.C.redwood.borde, peso: 'traslacion' })).map(l => l[1]).join(' ');
          t('disco: el paso 1 no da la cuenta «con sus pesos» antes de explicarlos, y el 4 sí', !/con sus pesos/.test(l1) && /con sus pesos/.test(l4));
        }
        // las cifras que se escriben son las del cálculo
        const E = est({ patron: 'redwood', ir: 58, foco: I.C.redwood.grupo, hueco: escena === 'anillo' ? 1 : 0 });
        const cu = I.cuenta(E), lec = def.lectura(E).map(l => l[0] + ' = ' + l[1].replace(/<[^>]+>/g, '')).join(' | ');
        // contra las cifras de R, no contra la propia cuenta del motor (que se daría la razón a sí misma)
        const kR = ENTRADA.ref.patrones.redwood.k_traslacion[58], qR = (kR / (Math.PI * M.rDe(58) ** 2)).toFixed(2);
        t(escena + ': la lectura escribe K/πr² con la K de traslación de R (' + qR + ')', lec.indexOf(qR) >= 0);
        if (escena === 'anillo') {
          t('anillo: y g con la publicada en ese nodo (' + ENTRADA.g.redwood.g_obs[58].toFixed(2) + ')', lec.indexOf('g, todo el patrón = ' + ENTRADA.g.redwood.g_obs[58].toFixed(2)) >= 0);
          t('anillo: con el anillo puesto, los vecinos de la lectura son los del anillo (' + cu.nAnillo + '), no los del disco (' + cu.nDisco + ')',
            lec.indexOf('vecinos de este punto = ' + cu.nAnillo + ' en el anillo') >= 0);
          const Ed = est({ patron: 'redwood', ir: 58, foco: I.C.redwood.grupo, hueco: 0 });
          t('anillo: y con el disco, los del disco', def.lectura(Ed).some(l => l[0] === 'vecinos de este punto' && l[1] === String(I.cuenta(Ed).nDisco)));
          // «arrastra» solo cuando es cierto: pasado el r en que la g PUBLICADA vuelve a 1, con K claramente por encima.
          // La primera versión miraba solo K y g, y lo decía sobre los pinos (el patrón aleatorio) en r = 0.01, donde
          // K/πr² = 1.55 es UNA pareja empatada (revisión del 2026-10-02).
          let mentiras = 0, ciertas = 0, enPinos = 0;
          for (const patron of M.PATRONES) for (let ir = 1; ir <= M.NODOS; ir++) {
            const Ei = est({ patron, ir, hueco: 1 }), c = I.cuenta(Ei), dice = /arrastra/.test(def.pasos[2].texto(Ei));
            const rv = ENTRADA.g[patron].r_vuelve_a_1, iv = rv == null ? null : Math.round(rv / M.PASO_R);
            const cierto = iv != null && ir >= iv && c.q > 1.1 && c.g < 1.1;
            if (dice !== cierto) mentiras++; if (dice) ciertas++; if (dice && patron === 'japanesepines') enPinos++;
          }
          t('anillo: el paso 3 dice que K «arrastra» solo desde el r en que g vuelve a 1, con K más de un 10 % por encima y g sin volver a pasar de 1.1 (' + ciertas + ' estados; ' + mentiras + ' mal)', mentiras === 0 && ciertas > 0);
          // y sin parpadeo en las secuoyas (auditoría del 2026-10-02: aparecía en 0.1425–0.155, se iba, volvía en 0.185–0.19 y
          // faltaba en r = 0.20, g = 0.59, K = 1.34 π r², el caso más claro)
          {
            const iv = Math.round(ENTRADA.g.redwood.r_vuelve_a_1 / M.PASO_R);
            const dice = ir => /arrastra/.test(def.pasos[2].texto(est({ patron: 'redwood', ir, hueco: 1 })));
            let huecos = 0; for (let ir = iv; ir <= M.NODOS; ir++) if (!dice(ir)) huecos++;
            t('anillo: en las secuoyas «arrastra» se dice en todo el tramo desde que g vuelve a 1 hasta 0.25 (' + huecos + ' huecos), también en r = 0.20',
              huecos === 0 && dice(80) && !dice(iv - 1));
          }
          t('anillo: y nunca en los pinos, cuya g no vuelve a 1 porque no tiene de dónde', enPinos === 0);
          // el paso 5 compara con el disco solo cuando el anillo tiene menos parejas (el anillo se sale del disco)
          let malas5 = 0, vacios = 0, masParejas = 0;
          for (const patron of M.PATRONES) for (let ir = 0; ir <= M.NODOS; ir++) {
            const Ei = est({ patron, ir, hueco: 1, todos: 1 }), na = I.nParejas(Ei, true), nd = I.nParejas(Ei, false);
            if (/frente a las/.test(def.pasos[4].texto(Ei)) !== (na < nd)) malas5++;
            if (na === 0) { vacios++; if (/por encima de 1/.test(def.pasos[2].texto(Ei))) masParejas++; }
          }
          t('anillo: el paso 5 dice «frente a las M del disco» solo cuando el anillo tiene menos (' + malas5 + ' mal)', malas5 === 0);
          t('anillo: con el anillo vacío en todo el patrón (' + vacios + ' estados), el paso 3 no dice que g quede por encima de 1', vacios > 0 && masParejas === 0);
        } else {
          t('disco: la lectura escribe la K del peso elegido, la de R (' + kR.toFixed(4) + ' con peso, ' + ENTRADA.ref.patrones.redwood.k_sin[58].toFixed(4) + ' sin él)',
            lec.indexOf('K con peso = ' + kR.toFixed(4)) >= 0 &&
            def.lectura(est({ patron: 'redwood', ir: 58, peso: 'ninguno' })).some(l => l[0] === 'K sin peso' && l[1] === ENTRADA.ref.patrones.redwood.k_sin[58].toFixed(4)));
          const E4 = est({ patron: 'redwood', ir: 60, foco: I.C.redwood.borde, peso: 'ninguno' }), tx = def.pasos[3].texto(E4), c4 = I.cuenta(E4);
          t('disco: el paso 4 da K sin corregir y corregida con las cifras del cálculo (' + c4.qsin.toFixed(2) + ' y ' + c4.qtr.toFixed(2) + ')', tx.indexOf(c4.qsin.toFixed(2)) >= 0 && tx.indexOf(c4.qtr.toFixed(2)) >= 0);
          t('disco: y dice que el disco se sale de la ventana solo cuando se sale', /cae fuera de la ventana/.test(tx) &&
            !/cae fuera de la ventana/.test(def.pasos[3].texto(est({ patron: 'redwood', ir: 20, foco: I.C.redwood.grupo }))));
          // «K se queda corta: 0.00 veces π r², frente a 0.00» salía sin parejas: solo se compara si hay algo que comparar
          let iguales = 0;
          for (const patron of M.PATRONES) for (let ir = 0; ir <= M.NODOS; ir++) {
            const Ei = est({ patron, ir, foco: I.C[patron].borde }), c = I.cuenta(Ei), tx4 = def.pasos[3].texto(Ei);
            if (/se queda corta/.test(tx4) && !(c.Ktr > 0 && c.qsin.toFixed(2) !== c.qtr.toFixed(2))) iguales++;
          }
          t('disco: el paso 4 dice que K «se queda corta» solo cuando las dos cifras que da son distintas (' + iguales + ' mal)', iguales === 0);
        }
      }
      console.log(JSON.stringify({ T }));
    """, entrada))

    # ---- 6 · el dibujo, con un lienzo falso ---------------------------------
    print("\n6 · el dibujo, con un lienzo falso: ningún NaN llega a un método de trazo")
    muestra(node(r"""
      const num = [], props = [];
      const ctx = new Proxy({}, {
        get(o, k) {
          if (k in o) return o[k];
          if (k === 'measureText') return s => ({ width: 6 * String(s).length });
          return (...a) => { a.forEach(v => { if (typeof v === 'number') num.push(String(k) + ' ' + v); }); };
        },
        set(o, k, v) { o[k] = v; props.push(String(k) + ' ' + v); return true; }
      });
      let casos = 0, excepciones = 0, noFinitos = 0, propsMalas = 0;
      for (const escena of ['disco', 'anillo']) {
        const def = KA.creaDef(DATOS, { escena }), I = def.interno;
        for (const [w, h] of [[540, 405], [298, 268], [800, 600], [200, 180]]) {
          for (const patron of M.PATRONES) {
            for (const ir of [0, 1, 16, 58, 100]) {
              for (const [vir, vh, todos, hover] of [[ir, 0, 0, -1], [ir, 1, 0, 3], [Math.max(0, ir - 0.4), 0.5, 1, -1], [Math.min(100, ir + 0.37), 0.2, 0, 5]]) {
                for (const foco of [0, I.C[patron].grupo, I.C[patron].borde]) {
                  const E = Object.assign(def.inicial(), { patron, ir, foco, hover, todos, hueco: escena === 'anillo' ? Math.round(vh) : 0, peso: ir % 2 ? 'ninguno' : 'traslacion' });
                  const V = Object.assign({}, E, { ir: vir, hueco: escena === 'anillo' ? vh : 0 });
                  num.length = 0; props.length = 0; casos++;
                  try {
                    def.dibuja({ ctx, w, h, dpr: 1 }, E, V);
                    def.panel({ ctx, w: Math.round(w / 1.6), h: 150, dpr: 1 }, def.paneles[0].id, E, V);
                  } catch (e) { excepciones++; }
                  noFinitos += num.filter(s => !Number.isFinite(+s.split(' ')[1])).length;
                  propsMalas += props.filter(s => /NaN|undefined/.test(s)).length;
                }
              }
            }
          }
        }
      }
      t('dibujar ' + casos + ' estados (2 escenas, 4 tamaños, 3 patrones, 5 r, a medio camino, 3 focos) no lanza ninguna excepción', excepciones === 0);
      t('ningún número que llega a un método de trazo es NaN o infinito', noFinitos === 0);
      t('ningún color, fuente ni ancho se escribe con NaN o undefined', propsMalas === 0);
      console.log(JSON.stringify({ T }));
    """, entrada))

    print()
    if fallos:
        print(f"HAY {len(fallos)} COMPROBACIONES ROTAS")
        return 1
    print("Todo en verde.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
