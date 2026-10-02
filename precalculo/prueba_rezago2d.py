#!/usr/bin/env python3
"""
prueba_rezago2d.py — la animación 2D del rezago, probada contra R y por dentro

Material de Estadística Espacial 2026-II (20929). Capítulo 6, módulo 10.

POR QUÉ EXISTE. `precalculo/anim2d/rezago2d.js` calcula Wᵏy en el navegador, y esa
aritmética es de las que ningún auditor de prosa ve: un `s / (v.length - 1)` que pasa a
`s / v.length`, una arista que se lee en base 0, una media simple donde va la ponderada por
el grado, la pendiente que se confunde con la correlación (justo lo que el capítulo acaba de
corregir). La página se ve igual de bien. Se prueba contra `spdep`, y lo que no es aritmética
—el clic, el guion, las transiciones, el teclado— se prueba en Node sin DOM, que es lo más
que permite un repo sin jsdom.

Seis bloques:

  1. LA ARITMÉTICA, contra R. `cap6_rezago2d.json` sale de `genera_cap6_rezago2d.R` (spdep:
     poly2nb, nb2listw, lag.listw). Se exige, con las aristas del MAPA del capítulo (no con las
     de R): los mismos vecinos, la misma serie (media, sd, cor, pendiente) para k = 0…70 a
     1e-11, los mismos vectores enteros en seis k, el mismo límite, y que el I de Moran sea la
     pendiente de Wy sobre y. Las dos vecindades, reina y torre.
  2. LAS PROPIEDADES, sin R. W·1 = 1; la media de y y el límite NO coinciden (el paso 4 lo
     afirma); iterar mucho converge al límite; la desviación baja en cada k; y lo que debe fallar,
     falla (una isla, una arista impar o fuera de rango).
  3. LA GEOMETRÍA. `cajaQ` y `ajuste` dan lo mismo que las originales de la plantilla (se
     extraen de ella y se evalúan: si la plantilla cambia, esto lo dice), y el clic encuentra el
     barrio que otro algoritmo (número de vueltas, en Python) encuentra, en 4 000 puntos.
  4. LA MÁQUINA de `anim2d.js`: `poner` rechaza lo que no es un número finito, una transición llega
     exactamente a su destino, el guion recorre los pasos, un gesto lo interrumpe, y la API real y
     la inerte salen de la misma lista de claves.
  5. LO QUE LEE LA PERSONA, para los 49 barrios × 61 k × 2 vecindades: ningún texto, lectura ni
     descripción lleva NaN, undefined ni Infinity; la cuenta del barrio en foco es la de R.
  6. EL DIBUJO, con un lienzo falso: ningún número que llegue a un método de trazo es NaN ni
     infinito, para cada paso, tamaño de lienzo, k fraccionario, vecindad y foco.

`REZAGO2D_MOTOR` y `ANIM2D_NUCLEO` redirigen los dos archivos a copias: así
`prueba_mutaciones_anim2d.py` comprueba que esta prueba sabe fallar.

    python3 precalculo/prueba_rezago2d.py
"""
from __future__ import annotations

import json
import os
import random
import re
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
PRE = RAIZ / "precalculo"
REZAGO = Path(os.environ.get("REZAGO2D_MOTOR", PRE / "anim2d" / "rezago2d.js"))
NUCLEO = Path(os.environ.get("ANIM2D_NUCLEO", PRE / "anim2d" / "anim2d.js"))
PLANTILLA = RAIZ / "plantilla" / "plantilla-capitulo.html"
REF = PRE / "salidas" / "cap6_rezago2d.json"
MAPAS = PRE / "salidas" / "cap6_mapas.json"

TOL = 1e-11         # contra R: doble precisión sobre 49 números; medido ≤ 5e-14, con 200 veces de margen
fallos: list[str] = []


def ok(cond: bool, msg: str) -> None:
    print(("  OK   " if cond else "  MAL  ") + msg)
    if not cond:
        fallos.append(msg)


def node(codigo: str, entrada: dict | None = None) -> dict:
    """Corre JavaScript contra los motores REALES (los mismos archivos que se publican)."""
    prog = (f"const A = require({json.dumps(str(NUCLEO))}); global.Anim2D = A;\n"
            f"const R = require({json.dumps(str(REZAGO))}); const M = R.matematica;\n"
            f"const ENTRADA = {json.dumps(entrada)};\n"
            "const T = [];\n"
            "const t = (nombre, cond) => T.push([nombre, !!cond]);\n" + codigo)
    r = subprocess.run(["node", "-"], input=prog, capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit(f"PARADO: node falló\n{r.stderr}")
    return json.loads(r.stdout)


def muestra(res: dict) -> None:
    for nombre, bien in res["T"]:
        ok(bien, nombre)


def extrae_funcion(texto: str, nombre: str) -> str:
    """El código de `function nombre(...) { ... }` de la plantilla, por conteo de llaves."""
    i = texto.find(f"function {nombre}(")
    if i < 0:
        sys.exit(f"PARADO: la plantilla ya no tiene {nombre}")
    j = texto.index("{", i)
    prof = 0
    for k in range(j, len(texto)):
        if texto[k] == "{":
            prof += 1
        elif texto[k] == "}":
            prof -= 1
            if prof == 0:
                return texto[i:k + 1]
    sys.exit(f"PARADO: no cierra {nombre}")


def vueltas(px: float, py: float, anillo: list[float]) -> bool:
    """Punto en polígono por NÚMERO DE VUELTAS: otro algoritmo que el trazado de rayos del motor."""
    wn, n = 0, len(anillo) // 2
    for i in range(n):
        x0, y0 = anillo[2 * i], anillo[2 * i + 1]
        x1, y1 = anillo[2 * ((i + 1) % n)], anillo[2 * ((i + 1) % n) + 1]
        cruz = (x1 - x0) * (py - y0) - (px - x0) * (y1 - y0)
        if y0 <= py:
            if y1 > py and cruz > 0:
                wn += 1
        elif y1 <= py and cruz < 0:
            wn -= 1
    return wn != 0


def centroide(anillo: list[float]) -> tuple[float, float]:
    a = cx = cy = 0.0
    n = len(anillo) // 2
    for i in range(n):
        x0, y0 = anillo[2 * i], anillo[2 * i + 1]
        x1, y1 = anillo[2 * ((i + 1) % n)], anillo[2 * ((i + 1) % n) + 1]
        c = x0 * y1 - x1 * y0
        a += c
        cx += (x0 + x1) * c
        cy += (y0 + y1) * c
    return cx / (3 * a), cy / (3 * a)


def main() -> int:
    print("\n=== prueba_rezago2d.py ===")
    ref = json.loads(REF.read_text(encoding="utf-8"))
    mapa = json.loads(MAPAS.read_text(encoding="utf-8"))["cap6-w"]
    plantilla = PLANTILLA.read_text(encoding="utf-8")
    entrada = {"ref": ref, "mapa": mapa}

    # ---- 1 · la aritmética, contra R ----------------------------------------
    print("\n1 · la aritmética, contra spdep (aristas del mapa del capítulo, no las de R)")
    res = node(r"""
      const sal = {};
      const y = ENTRADA.ref.y.crime;
      for (const nombre of ['reina', 'torre']) {
        const rf = ENTRADA.ref.vecindades[nombre];
        const vec = M.vecinosDe(ENTRADA.mapa.variantes[nombre].aristas, y.length);
        let vecinosDistintos = 0, gradosDistintos = 0;
        vec.forEach((nb, i) => {
          const r = rf.vecinos[i].map(x => x - 1).sort((a, b) => a - b);
          if (nb.join(',') !== r.join(',')) vecinosDistintos++;
          if (nb.length !== rf.grados[i]) gradosDistintos++;
        });
        const cs = M.capas(vec, y, ENTRADA.ref.meta.k_max);
        const d = { media: 0, sd: 0, cor: 0, pendiente: 0 };
        rf.serie.forEach(s => {
          const r = M.resumen(y, cs[s.k]);
          for (const c of Object.keys(d)) d[c] = Math.max(d[c], Math.abs(r[c] - s[c]));
        });
        let dVec = 0;
        for (const k of Object.keys(rf.vectores)) cs[+k].forEach((v, i) => { dVec = Math.max(dVec, Math.abs(v - rf.vectores[k][i])); });
        sal[nombre] = { vecinosDistintos, gradosDistintos, series: rf.serie.length, d, dVec,
                        dLimite: Math.abs(M.limite(vec, y) - rf.limite) };
      }
      const vec = M.vecinosDe(ENTRADA.mapa.variantes.reina.aristas, y.length);
      const r1 = M.resumen(y, M.capas(vec, y, 1)[1]);
      sal.moran = { dI: Math.abs(r1.pendiente - ENTRADA.ref.moran.I),
                    dProducto: Math.abs(r1.cor * (r1.sd / M.sd(y)) - ENTRADA.ref.moran.I) };
      sal.kMax = M.K_MAX;
      console.log(JSON.stringify({ sal }));
    """, entrada)["sal"]
    for nombre in ("reina", "torre"):
        s = res[nombre]
        ok(s["vecinosDistintos"] == 0 and s["gradosDistintos"] == 0,
           f"{nombre}: los vecinos de las aristas del mapa son los de spdep ({s['vecinosDistintos']} barrios distintos)")
        ok(s["series"] == res["kMax"] + 1, f"{nombre}: la serie de R llega hasta k = {res['kMax']}")
        for c in ("media", "sd", "cor", "pendiente"):
            ok(s["d"][c] < TOL, f"{nombre}: {c} de Wᵏy, k = 0…{res['kMax']}: diferencia máxima {s['d'][c]:.1e}")
        ok(s["dVec"] < TOL, f"{nombre}: Wᵏy barrio a barrio en k = {', '.join(map(str, ref['meta']['k_vectores']))}: {s['dVec']:.1e}")
        ok(s["dLimite"] < 1e-12, f"{nombre}: el límite Σ dᵢ yᵢ / Σ dᵢ coincide con el de R: {s['dLimite']:.1e}")
    ok(res["moran"]["dI"] < 1e-12, f"I de Moran = pendiente de Wy sobre y: {res['moran']['dI']:.1e}")
    ok(res["moran"]["dProducto"] < 1e-12, f"I de Moran = cor · sd(Wy)/sd(y): {res['moran']['dProducto']:.1e}")

    # ---- 2 · propiedades, sin R ---------------------------------------------
    print("\n2 · propiedades exactas, sin R")
    muestra(node(r"""
      const y = ENTRADA.ref.y.crime, n = y.length;
      for (const nombre of ['reina', 'torre']) {
        const vec = M.vecinosDe(ENTRADA.mapa.variantes[nombre].aristas, n);
        const unos = M.rezago(vec, new Array(n).fill(1));
        t(nombre + ': W·1 = 1 (cada fila suma 1)', unos.every(v => Math.abs(v - 1) < 1e-15));
        const lim = M.limite(vec, y), m0 = M.media(y);
        t(nombre + ': el límite NO es la media de y (' + lim.toFixed(2) + ' contra ' + m0.toFixed(2) + ')', Math.abs(lim - m0) > 1.5);   // medido: 2.69 (reina) y 1.76 (torre)
        let v = y.slice();
        for (let k = 0; k < 4000; k++) v = M.rezago(vec, v);
        t(nombre + ': iterar 4 000 veces converge al límite', v.every(x => Math.abs(x - lim) < 1e-9));
        const cs = M.capas(vec, y, M.K_MAX), s = cs.map(c => M.sd(c));
        t(nombre + ': la desviación baja en cada k de 0 a ' + M.K_MAX, s.every((x, k) => k === 0 || x < s[k - 1]));
        t(nombre + ': la media de Wy se aparta de la de y (no se conserva)', Math.abs(M.media(cs[1]) - m0) > 0.01);
        // la prosa cita cuántas aplicaciones bajan la desviación al 5 % (66 con la reina): el deslizador tiene que llegar
        t(nombre + ': el deslizador llega al k en que la desviación baja del 5 % de la de y (' + ENTRADA.ref.vecindades[nombre].k_5pct + ' ≤ ' + M.K_MAX + ')',
          ENTRADA.ref.vecindades[nombre].k_5pct <= M.K_MAX && s[M.K_MAX] <= 0.05 * s[0]);
        const f = M.focoDidactico(vec, y);
        t(nombre + ': el barrio de partida tiene al menos cuatro vecinos', vec[f].length >= 4);
      }
      const falla = (f) => { try { f(); return false; } catch (e) { return true; } };
      t('un barrio sin vecinos no tiene media (lanza)', falla(() => M.rezago([[1], []], [1, 2])));
      t('una lista de aristas de longitud impar se rechaza', falla(() => M.vecinosDe([1, 2, 3], 5)));
      t('una arista fuera de rango se rechaza', falla(() => M.vecinosDe([1, 9], 5)));
      t('una arista de un barrio consigo mismo se rechaza', falla(() => M.vecinosDe([2, 2], 5)));
      t('las aristas en base 1 dan vecinos en base 0', JSON.stringify(M.vecinosDe([1, 2], 2)) === '[[1],[0]]');
      console.log(JSON.stringify({ T }));
    """, entrada))

    # ---- 3 · la geometría ----------------------------------------------------
    print("\n3 · la geometría: las originales de la plantilla y otro algoritmo para el clic")
    geom = [g[0] for g in mapa["geom"]]
    interior = []
    for i, an in enumerate(geom):
        cx, cy = centroide(an)
        if vueltas(cx, cy, an):
            interior.append([i, cx, cy])
    xs = [v for an in geom for v in an[0::2]]
    ys = [v for an in geom for v in an[1::2]]
    azar = random.Random(2026)
    puntos = []
    for _ in range(4000):
        px, py = azar.uniform(min(xs), max(xs)), azar.uniform(min(ys), max(ys))
        dueno = next((i for i, an in enumerate(geom) if vueltas(px, py, an)), -1)
        puntos.append([px, py, dueno])
    ok(len(interior) >= 40, f"hay {len(interior)} barrios con un punto interior que Python confirma")
    ok(any(p[2] < 0 for p in puntos) and any(p[2] >= 0 for p in puntos), "los 4 000 puntos caen dentro de algún barrio y fuera de todos")
    muestra(node(r"""
      const orig = new Function('return [' + ENTRADA.cajaQ + ',' + ENTRADA.ajuste + ']')();
      const cqO = orig[0](ENTRADA.mapa.caja, ENTRADA.mapa.q), cq = M.cajaQ(ENTRADA.mapa.caja, ENTRADA.mapa.q);
      t('cajaQ da lo mismo que geomapaCajaQ de la plantilla',
        ['x0', 'y0', 'x1', 'y1'].every(c => Math.abs(cq[c] - cqO[c]) < 1e-9));
      let dif = 0;
      for (const [w, h, m] of [[540, 405, 6], [340, 306, 6], [800, 300, 10], [260, 240, 0]]) {
        const a = orig[1]({ width: w, height: h }, cq, m), b = M.ajuste(w, h, cq, { l: m, r: m, t: m, b: m });
        dif = Math.max(dif, Math.abs(a.s - b.s), Math.abs(a.ox - b.ox), Math.abs(a.oy - b.oy));
        for (const [qx, qy] of [[0, 0], [1000, 2000], [4096, 4096], [cq.x0, cq.y1]]) dif = Math.max(dif, Math.abs(a.x(qx) - b.x(qx)), Math.abs(a.y(qy) - b.y(qy)));
      }
      t('ajuste da lo mismo que geomapaAjuste de la plantilla (escala, origen y las dos transformaciones): ' + dif.toExponential(1), dif < 1e-9);
      const a = M.ajuste(540, 405, cq, { l: 8, r: 8, t: 8, b: 44 });
      let ida = 0;
      for (const [qx, qy] of [[900, 2100], [2048, 2048], [3000, 3400]]) ida = Math.max(ida, Math.abs(a.qx(a.x(qx)) - qx), Math.abs(a.qy(a.y(qy)) - qy));
      t('píxel → cuantizado es la inversa de cuantizado → píxel: ' + ida.toExponential(1), ida < 1e-9);
      const interiores = ENTRADA.interior.filter(([i, x, y]) => M.barrioEn(ENTRADA.geom.map(g => [g]), x, y) === i).length;
      t('el clic encuentra el barrio de cada punto interior (' + interiores + ' de ' + ENTRADA.interior.length + ')', interiores === ENTRADA.interior.length);
      const g = ENTRADA.geom.map(a => [a]);
      const malos = ENTRADA.puntos.filter(([x, y, d]) => M.barrioEn(g, x, y) !== d).length;
      t('en 4 000 puntos al azar, el clic y el número de vueltas dan el mismo barrio (' + malos + ' distintos)', malos === 0);
      console.log(JSON.stringify({ T }));
    """, dict(entrada, cajaQ=extrae_funcion(plantilla, "geomapaCajaQ"), ajuste=extrae_funcion(plantilla, "geomapaAjuste"),
              interior=interior, puntos=puntos, geom=geom)))

    # ---- 4 · la máquina ------------------------------------------------------
    print("\n4 · la máquina de estados de anim2d.js")
    muestra(node(r"""
      const y = ENTRADA.ref.y.crime;
      const def = R.creaDef({ y, mapa: ENTRADA.mapa }, {});
      const nueva = (ganchos) => A.maquina(R.creaDef({ y, mapa: ENTRADA.mapa }, {}), ganchos || {});
      let m = nueva();
      t('el estado inicial es el paso 1, k = 0, reina', m.E.paso === 1 && m.E.k === 0 && m.E.vecindad === 'reina' && m.V.k === 0);

      for (const malo of [NaN, Infinity, -Infinity, 'tres', null, undefined]) m.poner({ k: malo });
      t('poner rechaza NaN, ±Infinity, texto, null y undefined en una clave numérica', m.E.k === 0 && m.V.k === 0);
      m.poner({ inventada: 3 });
      t('poner ignora una clave que el estado no tiene', !('inventada' in m.E));
      m.poner({ vecindad: 'dama' });
      t('poner no admite una vecindad que no existe', m.E.vecindad === 'reina');
      m.poner({ k: 99 });
      t('k se acota a K_MAX (' + M.K_MAX + ')', m.E.k === M.K_MAX);
      m.poner({ k: -4 });
      t('k no baja de 0', m.E.k === 0);
      m.poner({ k: 2.6 });
      t('k se redondea a un entero', m.E.k === 3);

      m = nueva();
      m.poner({ k: 10 });
      t('al poner, E ya vale el destino y V todavía no', m.E.k === 10 && m.V.k === 0);
      m.avanza(0.5);
      t('a media transición V está entre el origen y el destino', m.V.k > 0 && m.V.k < 10);
      m.avanza(60);
      t('la transición llega EXACTAMENTE al destino', m.V.k === 10);
      m.poner({ k: 5 }, { corte: true });
      t('con corte no hay transición', m.V.k === 5 && m.E.k === 5);
      const mr = nueva({ reducido: true });
      mr.poner({ k: 7 });
      t('con prefers-reduced-motion las transiciones saltan', mr.V.k === 7);

      m = nueva();
      t('ir(0) y ir(5) no existen', m.ir(0) === false && m.ir(5) === false && m.E.paso === 1);
      t('ir(2.4) va al paso 2 y pone k = 1', m.ir(2.4) === true && m.E.paso === 2 && m.E.k === 1);

      m = nueva();
      m.poner({ lupa: 1 });
      const cajaNueva = m.E.vx0 !== m.V.vx0;
      m.avanza(Infinity);
      t('con la lupa, E ya tiene la caja nueva, V todavía no, y V la alcanza al acabar la transición',
        cajaNueva && m.V.vx0 === m.E.vx0 && m.V.vy1 === m.E.vy1 && m.V.vx1 === m.E.vx1 && m.V.vy0 === m.E.vy0);
      m = nueva();
      m.poner({ lupa: 1 }, { corte: true });
      const vecM = M.vecinosDe(ENTRADA.mapa.variantes.reina.aristas, y.length);
      const aZ = def.interno.ajusteDe(540, 405, def.interno.cajaDe(m.V));
      const veci = ENTRADA.interior.find(([i]) => vecM[m.E.foco].indexOf(i) >= 0);
      const pz = def.puntero({ tipo: 'abajo', x: aZ.x(veci[1]), y: aZ.y(veci[2]) }, m.E, m.V, { w: 540, h: 405 });
      t('con la lupa puesta, un clic sobre un vecino lo pone en foco (el clic usa la caja que se ve)', pz && pz.poner.foco === veci[0]);
      const pm = def.puntero({ tipo: 'abajo', x: aZ.x(veci[1]), y: aZ.y(veci[2]) }, m.E, Object.assign({}, m.V, { vx0: def.interno.cq.x0, vy0: def.interno.cq.y0, vx1: def.interno.cq.x1, vy1: def.interno.cq.y1 }), { w: 540, h: 405 });
      t('y con la caja del mapa entero ese mismo píxel NO es ese barrio', !pm || pm.poner.foco !== veci[0]);

      const ev = [];
      m = nueva({ guion: on => ev.push(on) });
      m.reproducir();
      t('reproducir arranca el guion y avisa', m.guion.activo === true && ev.join() === 'true');
      m.avanza(Infinity);
      t('el guion recorre los cuatro pasos y se detiene en el último', m.E.paso === 4 && m.guion.activo === false && ev.join() === 'true,false');
      t('y deja el mapa en k = ' + M.K_MAX + ' (visible, no solo destino)', m.E.k === M.K_MAX && m.V.k === M.K_MAX);
      m.reproducir();
      t('reproducir al final del guion lo empieza otra vez, desde el paso 1', m.E.paso === 1 && m.guion.activo === true);
      // La espera da tiempo a LEER (auditoría del 2026-10-02: «Reproducir» pasaba los pasos a 450–1 000 palabras por minuto).
      const m4 = nueva(); m4.ir(4, { desdeGuion: true });
      const lee4 = m4.lectura(def.pasos[3]);
      t('la espera del paso 4 es lo que tarda su transición (9 s) más lo que se tarda en leerlo (' + lee4.toFixed(1) + ' s, más que su pausa de 3,5 s)',
        lee4 > 3.5 && Math.abs(m4.espera(4) - (9 + lee4)) < 1e-12);
      for (let i = 1; i <= def.pasos.length; i++) {
        const mi = nueva(); mi.ir(i, { desdeGuion: true });
        const p = def.pasos[i - 1];
        const pal = [p.titulo, p.texto].map(x => typeof x === 'function' ? x(mi.E) : x).join(' ').replace(/<[^>]+>/g, ' ').split(/\s+/).filter(Boolean).length;
        t('el guion se queda en el paso ' + i + ' lo bastante para leer sus ' + pal + ' palabras a 210 por minuto (' + mi.espera(i).toFixed(1) + ' s)',
          mi.espera(i) >= pal / 3.5 - 1e-9);
      }

      m = nueva();
      m.reproducir(); m.avanza(1);
      m.poner({ foco: 3 });
      t('cualquier gesto del usuario interrumpe el guion', m.guion.activo === false);
      m = nueva();
      m.reproducir(); m.avanza(1);
      m.poner({ hover: 2 }, { desdeGuion: true });
      t('pero lo que hace el propio guion no lo interrumpe', m.guion.activo === true);
      m.pausar(); m.reinicia();
      t('reiniciar vuelve al paso 1, k = 0, y sin guion', m.E.paso === 1 && m.E.k === 0 && m.V.k === 0 && !m.guion.activo);
      m = nueva(); m.avanza(Infinity);
      t('avanza con nada en marcha no hace nada', m.E.k === 0 && m.V.k === 0);

      t('la API inerte sale de la misma lista de claves que la real',
        JSON.stringify(Object.keys(A.sinAnimacion({ innerHTML: '', classList: { remove() {} } }, 'x', def))) === JSON.stringify(A.CLAVES));
      t('y su estado y su visual están vacíos', Object.keys(A.sinAnimacion({ innerHTML: '', classList: { remove() {} } }, 'x', def).estado).length === 0);
      let lanza = false;
      try { A.armaApi({ destruir() {} }); } catch (e) { lanza = true; }
      t('una API a la que le falta un método se rechaza al armarla', lanza);

      // el teclado y el clic, sobre la pieza real
      const ajuste = def.interno.ajusteDe(540, 405);
      const [i, qx, qy] = ENTRADA.interior[10];
      const p = def.puntero({ tipo: 'abajo', x: ajuste.x(qx), y: ajuste.y(qy) }, m.E, m.V, { w: 540, h: 405 });
      t('un clic sobre el barrio ' + (i + 1) + ' lo pone en foco', p && p.poner.foco === i);
      const mv = def.puntero({ tipo: 'mueve', x: ajuste.x(qx), y: ajuste.y(qy) }, m.E, m.V, { w: 540, h: 405 });
      t('pasar el puntero lo marca y cambia el cursor', mv && mv.poner.hover === i && mv.cursor === 'pointer');
      t('un clic fuera de todo barrio no cambia nada', def.puntero({ tipo: 'abajo', x: 1, y: 1 }, m.E, m.V, { w: 540, h: 405 }) === null);
      t('salir del lienzo quita la marca', def.puntero({ tipo: 'sale' }, m.E, m.V, { w: 540, h: 405 }).poner.hover === -1);
      t('antes del primer dibujo no hay lienzo y no se encuentra ningún barrio', def.puntero({ tipo: 'abajo', x: 100, y: 100 }, m.E, m.V, { w: 0, h: 0 }) === null);
      const E0 = { k: 5, foco: 48 };
      t('→ en el último barrio vuelve al primero', def.tecla({ key: 'ArrowRight' }, E0).foco === 0);
      t('← en el primero va al último', def.tecla({ key: 'ArrowLeft' }, { k: 5, foco: 0 }).foco === 48);
      t('↑ y ↓ suben y bajan k', def.tecla({ key: 'ArrowUp' }, E0).k === 6 && def.tecla({ key: 'ArrowDown' }, E0).k === 4);
      t('Inicio y Fin llevan a k = 0 y k = ' + M.K_MAX, def.tecla({ key: 'Home' }, E0).k === 0 && def.tecla({ key: 'End' }, E0).k === M.K_MAX);
      t('otra tecla no hace nada', def.tecla({ key: 'a' }, E0) === null);

      // EL PASO SIGUE A LA CAPA. El deslizador y el teclado cambian k sin pasar por `ir`; la leyenda que se ve tiene
      // que ser la de esa capa (revisión del 2026-10-02: la del paso 1 se quedaba encima de W³⁰y).
      m = nueva();
      m.poner({ k: 30 });
      t('mover k a 30 desde el paso 1 lleva al paso 4', m.E.paso === 4);
      m.poner({ k: 1 }); const p1 = m.E.paso; m.poner({ k: 2 }); const p2 = m.E.paso; m.poner({ k: 0 });
      t('y k = 1, 2 y 0 llevan a los pasos 2, 3 y 1', p1 === 2 && p2 === 3 && m.E.paso === 1);
      m.ir(4);
      t('pero ir a un paso respeta el k que ese paso pone', m.E.paso === 4 && m.E.k === M.K_MAX);
      const t4 = k => { const E = Object.assign(def.inicial(), { paso: 4, k }); return def.pasos[3].titulo(E) + ' | ' + def.pasos[3].texto(E); };
      t('el paso 4 no dice «casi un solo color» con k = 3 (la desviación es el ' + Math.round(100 * def.interno.de('reina').res[3].sd / M.sd(y)) + ' % de la de y)',
        !/casi un solo color|casi de un solo color/.test(t4(3)));
      t('y sí lo dice con k = ' + M.K_MAX, /casi un solo color/.test(t4(M.K_MAX)));
      t('y nombra la vecindad cuyo límite da', /vecindad de la reina/.test(t4(M.K_MAX)) &&
        /vecindad de la torre/.test(def.pasos[3].texto(Object.assign(def.inicial(), { paso: 4, k: M.K_MAX, vecindad: 'torre' }))));

      // EL GESTO (anim2d.gestos), con un puntero falso que hace lo que hacen las piezas: elige al bajar, marca al pasar.
      {
        const llamadas = [];
        const falso = (ev) => { llamadas.push(ev.tipo); if (ev.tipo === 'abajo') return { poner: { foco: 7 } }; if (ev.tipo === 'mueve') return { poner: { hover: 3 }, cursor: 'pointer' }; if (ev.tipo === 'sale') return { poner: { hover: -1 }, cursor: '' }; return null; };
        let g = A.gestos(falso);
        const r1 = g({ tipo: 'abajo', x: 10, y: 10 });
        t('con el ratón, bajar elige y es un gesto que interrumpe el guion', r1 && r1.poner.foco === 7 && r1.interrumpe === true);
        const r2 = g({ tipo: 'mueve', x: 30, y: 10 });
        t('pasar por encima marca, pero no interrumpe el guion', r2 && r2.poner.hover === 3 && r2.interrumpe === false);
        const r3 = g({ tipo: 'sale', x: 0, y: 0 });
        t('salir del lienzo quita la marca y NO interrumpe el guion (antes lo paraba)', r3 && r3.poner.hover === -1 && r3.interrumpe === false);
        g = A.gestos(falso);
        t('con el dedo, bajar NO elige todavía', g({ tipo: 'abajo', x: 10, y: 10, tactil: true }) === null);
        t('y moverlo sin arrastre no marca nada (con el dedo no hay «pasar por encima»)', g({ tipo: 'mueve', x: 12, y: 11, tactil: true }) === null);
        const r4 = g({ tipo: 'arriba', x: 12, y: 11, tactil: true });
        t('levantarlo cerca de donde bajó elige, como un gesto', r4 && r4.poner.foco === 7 && r4.interrumpe === true);
        g = A.gestos(falso);
        g({ tipo: 'abajo', x: 10, y: 10, tactil: true });
        t('levantarlo a más de ' + A.UMBRAL_TOQUE + ' px (desplazaba la página) no elige', g({ tipo: 'arriba', x: 10, y: 10 + A.UMBRAL_TOQUE + 12, tactil: true }) === null);
        g = A.gestos(falso);
        g({ tipo: 'abajo', x: 10, y: 10, tactil: true }); g({ tipo: 'mueve', x: 10, y: 40, tactil: true });
        t('un dedo que se fue lejos y volvió tampoco elige', g({ tipo: 'arriba', x: 10, y: 11, tactil: true }) === null);
        g = A.gestos(falso);
        g({ tipo: 'abajo', x: 10, y: 10, tactil: true }); g({ tipo: 'cancela' });
        t('si el navegador se queda el gesto (pointercancel), no elige', g({ tipo: 'arriba', x: 10, y: 10, tactil: true }) === null);
        const arrastra = (ev) => ev.tipo === 'abajo' ? { poner: { k: 1 }, captura: true } : ev.tipo === 'mueve' ? { poner: { k: 2 } } : null;
        g = A.gestos(arrastra);
        const a1 = g({ tipo: 'abajo', x: 5, y: 5, tactil: true });
        t('si la pieza pide capturar (un arrastre), el dedo actúa al bajar', a1 && a1.captura === true && a1.poner.k === 1);
        const a2 = g({ tipo: 'mueve', x: 25, y: 5, tactil: true });
        t('y sus movimientos son del arrastre e interrumpen el guion', a2 && a2.poner.k === 2 && a2.interrumpe === true);
        g({ tipo: 'arriba', x: 25, y: 5, tactil: true });
        t('al soltar, el dedo vuelve a no marcar al pasar', g({ tipo: 'mueve', x: 26, y: 5, tactil: true }) === null);
        // y la máquina real, con lo que el gesto devuelve: salir del lienzo no para «Reproducir»
        m = nueva(); m.reproducir(); m.avanza(1);
        const sal = A.gestos((ev, E, V, c) => def.puntero(ev, E, V, c))({ tipo: 'sale' }, m.E, m.V, { w: 540, h: 405 });
        m.poner(sal.poner, { desdeGuion: !sal.interrumpe });
        t('con la pieza real, salir del lienzo con el guion en marcha no lo para', m.guion.activo === true);
      }

      // UN PASO PUEDE PONER UN ESTADO QUE DEPENDE DE DÓNDE SE ESTÁ (lo usa la animación de K y g)
      {
        const d = { inicial: () => ({ paso: 1, a: 0, b: 5 }), pasos: [{ estado: { a: 1 } }, { estado: E => ({ a: E.b * 2 }) }] };
        const mm = A.maquina(d, {});
        mm.poner({ b: 4 });
        mm.ir(2, { corte: true });
        t('`estado` puede ser una función del estado actual', mm.E.paso === 2 && mm.E.a === 8);
      }
      console.log(JSON.stringify({ T }));
    """, dict(entrada, interior=interior)))

    # la API real (la de `monta`) no se puede construir sin DOM: se comprueba, en el texto, que declara cada clave
    nucleo = NUCLEO.read_text(encoding="utf-8")
    cola = nucleo[nucleo.index("return armaApi({", nucleo.index("function monta(")):]
    claves = re.search(r"const CLAVES = \[(.*?)\];", nucleo, re.S).group(1)
    faltan = [k for k in re.findall(r"'(\w+)'", claves) if not re.search(rf"\b{k}\b", cola.split("});")[0])]
    ok(not faltan, f"la API de monta() declara todas las claves de CLAVES (le faltan: {faltan or 'ninguna'})")

    # ---- 5 · lo que lee la persona ------------------------------------------
    print("\n5 · textos, lectura y descripción, para todos los barrios, k y vecindades")
    muestra(node(r"""
      const y = ENTRADA.ref.y.crime;
      const def = R.creaDef({ y, mapa: ENTRADA.mapa }, {});
      const malo = s => /NaN|undefined|Infinity|null/.test(s);
      // un estado completo: lo que `poner` dejaría, con la caja de la lupa que le toca
      const est = o => { const E = Object.assign(def.inicial(), o); return Object.assign(E, def.normaliza({ lupa: E.lupa, foco: E.foco, vecindad: E.vecindad }, E)); };
      let n = 0, mal = 0, dCuenta = 0, dPrevia = 0;
      for (const vecindad of ['reina', 'torre']) {
        for (let k = 0; k <= M.K_MAX; k++) {
          for (let foco = 0; foco < y.length; foco++) {
            const E = est({ paso: 1, k, vecindad, foco, lupa: foco % 2 });
            def.pasos.forEach((p, i) => {
              const s = (typeof p.titulo === 'function' ? p.titulo(E) : p.titulo) + ' ' + (typeof p.texto === 'function' ? p.texto(E) : p.texto);
              n++; if (malo(s)) mal++;
            });
            for (const l of def.lectura(E)) { n++; if (malo(l[0] + l[1])) mal++; }
            n++; if (malo(def.alt(E))) mal++;
          }
        }
        const rf = ENTRADA.ref.vecindades[vecindad];
        for (const k of Object.keys(rf.vectores)) {
          for (let foco = 0; foco < y.length; foco++) {
            const cu = def.interno.cuenta({ k: +k, vecindad, foco });
            dCuenta = Math.max(dCuenta, Math.abs(cu.valor - rf.vectores[k][foco]));
            if (+k === 2) dPrevia = Math.max(dPrevia, ...cu.nb.map(j => Math.abs(cu.previa[j] - rf.vectores['1'][j])));
          }
        }
      }
      t('ningún texto, lectura ni descripción lleva NaN, undefined, Infinity ni null (' + n + ' cadenas revisadas, ' + mal + ' malas)', mal === 0);
      t('la cuenta del barrio en foco es la de R en los seis k publicados: ' + dCuenta.toExponential(1), dCuenta < 1e-11);
      t('y los valores de sus vecinos son los de la capa anterior de R: ' + dPrevia.toExponential(1), dPrevia < 1e-11);
      const E0 = est({ paso: 1, k: 0, vecindad: 'reina', foco: 6 });
      t('en k = 0 no hay cuenta (nada se ha promediado)', def.interno.cuenta(E0) === null);
      const l1 = def.lectura(est({ paso: 2, k: 1, vecindad: 'reina', foco: 6 }));
      t('con k = 1 la lectura dice que la pendiente es el I de Moran', l1.some(x => /I de Moran/.test(x[1])));
      t('y con k = 2 no lo dice', !def.lectura(est({ paso: 3, k: 2, vecindad: 'reina', foco: 6 })).some(x => /I de Moran/.test(x[1])));
      const nor = def.normaliza({ k: -7, foco: 99, hover: -9, paso: 9, vecindad: 'dama', lupa: 7 }, E0);
      t('normaliza acota k, foco, hover y paso, pasa la lupa a 0/1, y descarta una vecindad que no existe', nor.k === 0 && nor.foco === 48 && nor.hover === -1 && nor.paso === 4 && nor.lupa === 1 && !('vecindad' in nor));
      // Lo que la revisión del 2026-10-02 encontró afirmado de más. La cuenta del paso 2 se escribe con términos
      // redondeados a dos decimales, y en el 13 % de los estados rehacerla con ellos da otra centésima: «≈», no «=».
      const tx2 = def.pasos[1].texto(est({ paso: 2, k: 1, foco: 12 }));
      t('la cuenta del paso 2 se escribe con «≈» (sus términos van redondeados)', / \/ \d+ ≈ <strong>/.test(tx2) && !/ \/ \d+ = <strong>/.test(tx2));
      // W² llega a un vecino de siempre solo si es vecino de otro vecino: en Columbus fallan 2 de 236 (reina) y 14 de 200 (torre).
      t('el paso 3 no da por seguro que W² cuente a todos los vecinos de siempre', /casi siempre/.test(def.pasos[2].texto(est({ paso: 3, k: 2 }))));
      t('el paso 4 anuncia, con cifras del cálculo, el límite ponderado y no la media de y',
        def.pasos[3].texto(est({ paso: 4, k: 60 })).indexOf(ENTRADA.ref.vecindades.reina.limite.toFixed(2)) >= 0 &&
        def.pasos[3].texto(est({ paso: 4, k: 60 })).indexOf(ENTRADA.ref.y.media.toFixed(2)) >= 0);
      // la lupa: la caja que se ve contiene al barrio en foco y a sus vecinos, y sin lupa es el mapa entero
      {
        const vec = M.vecinosDe(ENTRADA.mapa.variantes.reina.aristas, y.length);
        let dentroTodos = true, mas = true;
        for (let foco = 0; foco < y.length; foco++) {
          const b = def.normaliza({ lupa: 1, foco }, def.inicial());
          for (const i of [foco].concat(vec[foco])) {
            const xs = ENTRADA.mapa.geom[i][0].filter((_, p) => p % 2 === 0), ys = ENTRADA.mapa.geom[i][0].filter((_, p) => p % 2 === 1);
            if (!(b.vx0 <= Math.min(...xs) && b.vx1 >= Math.max(...xs) && b.vy0 <= Math.min(...ys) && b.vy1 >= Math.max(...ys))) dentroTodos = false;
          }
          if (!(b.vx1 - b.vx0 < def.interno.cq.x1 - def.interno.cq.x0)) mas = false;
        }
        t('con la lupa, la caja contiene al barrio en foco y a todos sus vecinos (los 49 barrios)', dentroTodos);
        t('y es más estrecha que el mapa entero (acerca de verdad)', mas);
        const b0 = def.normaliza({ lupa: 0, foco: 6 }, def.inicial());
        t('sin la lupa la caja es exactamente el mapa entero', b0.vx0 === def.interno.cq.x0 && b0.vy1 === def.interno.cq.y1 && b0.vx1 === def.interno.cq.x1);
        t('cambiar de barrio con la lupa puesta mueve la caja', def.normaliza({ foco: 20 }, est({ lupa: 1, foco: 6 })).vx0 !== est({ lupa: 1, foco: 6 }).vx0);
      }
      // Las etiquetas de los vecinos (los números que se ven sobre el mapa con la lupa) no se pisan: la función, y los 49 barrios.
      {
        const sep = M.separaEtiquetas([[10, 10], [12, 11], [14, 10], [11, 40]], 40, 15, [{ x: 30, y: 30, w: 58, h: 24 }], { x0: 0, y0: 0, x1: 120, y1: 80 });
        const solapan = (p, q) => Math.abs(p[0] - q[0]) < 40 && Math.abs(p[1] - q[1]) < 15;
        let hayChoque = false;
        for (let i = 0; i < sep.length; i++) for (let j = i + 1; j < sep.length; j++) if (solapan(sep[i], sep[j])) hayChoque = true;
        t('separaEtiquetas deja sin pisarse cuatro etiquetas amontonadas', !hayChoque);
        t('y las aparta del valor fijo del foco', sep.every(q => Math.abs(q[0] - 30) >= 49 || Math.abs(q[1] - 30) >= 19.5));
        t('y las deja dentro del límite', sep.every(q => q[0] >= 20 && q[0] <= 100 && q[1] >= 7.5 && q[1] <= 72.5));
        t('y es determinista', JSON.stringify(sep) === JSON.stringify(M.separaEtiquetas([[10, 10], [12, 11], [14, 10], [11, 40]], 40, 15, [{ x: 30, y: 30, w: 58, h: 24 }], { x0: 0, y0: 0, x1: 120, y1: 80 })));
        t('una etiqueta que no choca con nadie no se mueve', JSON.stringify(M.separaEtiquetas([[50, 50], [200, 50]], 40, 15, [], null)) === '[[50,50],[200,50]]');
        const I = def.interno;
        let choques = 0, casos = 0, fuera = 0;
        for (const [w, h] of [[296, 266], [340, 306], [540, 405], [800, 600]]) {
          for (const vecindad of ['reina', 'torre']) {
            for (let foco = 0; foco < y.length; foco++) {
              const E = est({ k: 1, lupa: 1, foco, vecindad });
              const a = I.ajusteDe(w, h, I.cajaDe(E)), pos = I.posicionesEtiquetas(a, E, { w, h });
              const fx = a.x(ENTRADA.mapa.nodos[2 * foco]), fy = a.y(ENTRADA.mapa.nodos[2 * foco + 1]);
              casos++;
              let c = 0;
              for (let i = 0; i < pos.length; i++) {
                for (let j = i + 1; j < pos.length; j++) if (Math.abs(pos[i][0] - pos[j][0]) < I.ETQ.w && Math.abs(pos[i][1] - pos[j][1]) < I.ETQ.h) c++;
                if (Math.abs(pos[i][0] - fx) < (I.ETQ.w + I.PASTILLA.w) / 2 && Math.abs(pos[i][1] - fy) < (I.ETQ.h + I.PASTILLA.h) / 2) c++;
                if (pos[i][0] < I.ETQ.w / 2 || pos[i][0] > w - I.ETQ.w / 2 || pos[i][1] < I.ETQ.h / 2 || pos[i][1] > h - I.MARGEN.b + 4 - I.ETQ.h / 2) fuera++;
              }
              if (c) choques++;
            }
          }
        }
        t('los números de los vecinos no se pisan entre sí ni con el valor del foco: ' + casos + ' casos (4 tamaños de lienzo, 49 barrios, 2 vecindades), ' + choques + ' con choques', choques === 0);
        t('y se quedan dentro de la zona del mapa', fuera === 0);
      }
      let lanza = false;
      try { R.creaDef({ y, mapa: Object.assign({}, ENTRADA.mapa, { variantes: { reina: Object.assign({}, ENTRADA.mapa.variantes.reina, { grados: ENTRADA.mapa.variantes.reina.grados.map((g, i) => i === 0 ? g + 1 : g) }), torre: ENTRADA.mapa.variantes.torre } }) }, {}).interno.de('reina'); } catch (e) { lanza = true; }
      t('si los grados del mapa no son los de sus aristas, la pieza se niega a montar', lanza);
      console.log(JSON.stringify({ T }));
    """, entrada))

    # ---- 6 · el dibujo, con un lienzo falso ---------------------------------
    print("\n6 · el dibujo, con un lienzo falso: ningún NaN llega a un método de trazo")
    muestra(node(r"""
      const y = ENTRADA.ref.y.crime;
      const def = R.creaDef({ y, mapa: ENTRADA.mapa }, {});
      const num = [], props = [];
      let cuentas = {};
      const ctx = new Proxy({}, {
        get(o, k) {
          if (k in o) return o[k];
          if (k === 'measureText') return s => ({ width: 6 * String(s).length });
          return (...a) => { cuentas[k] = (cuentas[k] || 0) + 1; a.forEach(v => { if (typeof v === 'number') num.push(String(k) + ' ' + v); }); };
        },
        set(o, k, v) { o[k] = v; props.push(String(k) + ' ' + v); return true; }
      });
      const est = o => { const E = Object.assign(def.inicial(), o); return Object.assign(E, def.normaliza({ lupa: E.lupa, foco: E.foco, vecindad: E.vecindad }, E)); };
      let casos = 0, excepciones = 0, noFinitos = 0, propsMalas = 0, sinBarrios = 0;
      const tamanos = [[540, 405], [340, 306], [260, 240], [800, 600]];
      for (const [w, h] of tamanos) {
        for (const vecindad of ['reina', 'torre']) {
          for (const k of [0, 1, 2, 30, M.K_MAX]) {
            for (const foco of [0, 6, 48]) {
              for (const [vk, hover, lupa, f] of [[k, -1, 0, 1], [k, 3, 1, 1], [Math.max(0, k - 0.5), -1, 1, 0.5], [Math.min(M.K_MAX, k + 0.37), 5, 0, 0]]) {
                const E = est({ paso: 2, k, vecindad, foco, hover, lupa }), cq = def.interno.cq;
                // la caja que se ve: entre el mapa entero y la de la lupa, como a media transición
                const V = Object.assign({}, E, { k: vk, vx0: cq.x0 + (E.vx0 - cq.x0) * f, vy0: cq.y0 + (E.vy0 - cq.y0) * f,
                                                 vx1: cq.x1 + (E.vx1 - cq.x1) * f, vy1: cq.y1 + (E.vy1 - cq.y1) * f });
                num.length = 0; props.length = 0; cuentas = {}; casos++;
                try {
                  def.dibuja({ ctx, w, h, dpr: 1 }, E, V);
                  // en k = 0 no hay flechas ni cuenta: lo único que se rellena son los barrios, uno a uno
                  if (k === 0 && vk === 0 && cuentas.fill !== y.length) sinBarrios++;
                  if (!(cuentas.fill >= y.length)) sinBarrios++;
                  def.panel({ ctx, w: Math.round(w / 2.4), h: 112, dpr: 1 }, 'sd', E, V);
                  def.panel({ ctx, w: Math.round(w / 2.4), h: 112, dpr: 1 }, 'media', E, V);
                } catch (e) { excepciones++; }
                noFinitos += num.filter(s => !Number.isFinite(+s.split(' ')[1])).length;
                propsMalas += props.filter(s => /NaN|undefined/.test(s)).length;
              }
            }
          }
        }
      }
      // La escala de color es la de y para TODAS las capas (la advertencia del módulo): con k grande los barrios
      // se parecen y hay pocos colores distintos; con una escala por capa saldrían tantos como con k = 0.
      const distintos = k => {
        props.length = 0; cuentas = {};
        const E = est({ paso: 4, k, vecindad: 'reina', foco: 6 });
        def.dibuja({ ctx, w: 540, h: 405, dpr: 1 }, E, Object.assign({}, E));
        return new Set(props.filter(s => s.startsWith('fillStyle ')).slice(0, y.length)).size;
      };
      const d0 = distintos(0), d60 = distintos(60);
      t('la escala de color es fija: con k = 60 hay ' + d60 + ' colores distintos y con k = 0, ' + d0, d60 * 2 <= d0);
      const dMax = distintos(M.K_MAX);
      t('y con k = ' + M.K_MAX + ', ' + dMax, dMax * 2 <= d0);
      t('dibujar ' + casos + ' estados (4 tamaños, 2 vecindades, 5 k, 3 focos, con y sin lupa, k y caja a media transición) no lanza ninguna excepción', excepciones === 0);
      t('ningún número que llega a un método de trazo es NaN o infinito', noFinitos === 0);
      t('ningún color, fuente ni ancho se escribe con NaN o undefined', propsMalas === 0);
      t('en todos los estados se rellenan los ' + y.length + ' barrios (y solo ellos cuando k = 0)', sinBarrios === 0);
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
