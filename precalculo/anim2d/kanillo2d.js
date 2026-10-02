/* =====================================================================
   kanillo2d.js — «K cuenta un disco, g mira un anillo»

   Material de Estadística Espacial 2026-II (20929). Capítulo 4, módulos 8 y 9.
   Corre sobre la cáscara `anim2d.js` (`Anim2D.monta`). Es su segunda pieza, después del rezago del
   capítulo 6.

   DOS ESCENAS, UN MOTOR (`opc.escena`):
     · 'disco', en el módulo 8: un punto y su disco (lo que cuenta K), el disco que crece y no suelta a
       nadie, todas las parejas que la fórmula suma, y el borde que esconde vecinos (el peso w_ij).
     · 'anillo', en el módulo 9: el disco de un punto de un grupo, el mismo disco más lejos (sigue
       contando lo de cerca), el anillo de esa distancia (lo que mira g), y todas las parejas en uno y
       en otro. Es la lección del módulo: K es acumulativa y no sabe decir DÓNDE está la estructura.

   LO QUE SE CALCULA AQUÍ Y LO QUE SE LEE. K se calcula aquí, exacta, pareja a pareja, con el peso de
   traslación del capítulo (|W| / |W ∩ (W + xᵢ − xⱼ)|) o sin él; y las cuentas de cada punto en su disco
   o en su anillo. `prueba_kanillo2d.py` lo compara con `Kest` y con las cuentas de R
   (`genera_cap4_kanillo2d.R`). La g NO se calcula: se traza la publicada (`D4.m9`, de `pcf`), porque
   spatstat la suaviza en la escala del área con un núcleo, y un anillo de ancho fijo no la reproduce
   (en las secuoyas, con ancho 0.02, la cuenta cruda pasa de 5 donde `pcf` da 3.28). El anillo se dibuja
   para VER qué parejas están a esa distancia; su ancho (2 · H_ANILLO) va declarado en el pie.

   UNA PAREJA A DISTANCIA r ESTÁ EN EL DISCO DE RADIO r. Las coordenadas de los pinos y las secuoyas
   vienen en una rejilla de 0.01, y muchas parejas caen exactamente en un nodo de r: se cuentan dentro
   (d ≤ r, con una tolerancia EPS para que no decida la raíz en coma flotante). `Kest` no siempre lo hace
   así en esos nodos, y la curva publicada del capítulo los cuenta a medias (interpola la rejilla de
   `Kest`): por eso esta K puede diferir de la del simulador de abajo en distancias cortas, y el pie lo
   dice.

   LO QUE LA LECTURA NO DICE: «significativo». Sin la banda del azar (módulo 11) una desviación sola no
   establece nada, y la lectura habla de exceso o de déficit frente al azar, nunca de un veredicto. Y el
   texto no afirma que g se quede en 1 después de volver (en las secuoyas vuelve a pasarlo, 1.04 en
   r = 0.15), ni que su máximo marque la escala: son dos lecturas equivocadas frecuentes.

   CADA FRASE DE UN PASO TIENE QUE SER CIERTA EN CUALQUIER ESTADO al que se llegue con los mandos (revisión
   del 2026-10-02): «arrastra» solo pasado el r en que la g publicada vuelve a 1 (los pinos no vuelven, y su
   K/πr² de 1.55 en r = 0.01 es UNA pareja empatada); «frente a las M del disco» solo si el anillo tiene
   menos; sin K que comparar, no se compara; y un anillo vacío no tiene «más parejas que el azar».
   ===================================================================== */
(function (global) {
  'use strict';

  /* ===================================================================
     1 · MATEMÁTICA. Sin DOM.
     =================================================================== */
  const EPS = 1e-9;            // una pareja a distancia r (empate) está dentro del disco de radio r
  const H_ANILLO = 0.01;       // medio ancho del anillo que se dibuja
  const PASO_R = 0.0025;       // la rejilla de r de las curvas del capítulo: 101 nodos, de 0 a 0.25
  const NODOS = 100;
  const R_GRUPO = 0.145;       // el r con que se elige el punto de un grupo (y el del paso 2 del anillo si g no vuelve)
  const R_BORDE = 0.15;        // el r con que se elige el punto del borde
  const PATRONES = ['cells', 'japanesepines', 'redwood'];
  const rDe = i => i * PASO_R;

  // Todo lo de un patrón que no depende del estado: distancias y pesos de cada pareja, una vez.
  function prepara(p) {
    const n = p.x.length;
    if (!(n >= 2) || p.y.length !== n) throw new Error('kanillo2d: un patrón necesita al menos dos puntos y tantas y como x');
    const v = p.ventana, a = v[2] - v[0], b = v[3] - v[1], A = a * b;
    if (!(a > 0 && b > 0)) throw new Error('kanillo2d: la ventana no tiene área');
    const d = new Float64Array(n * n), w = new Float64Array(n * n);
    for (let i = 0; i < n; i++) {
      for (let j = 0; j < n; j++) {
        const dx = p.x[i] - p.x[j], dy = p.y[i] - p.y[j];
        d[i * n + j] = Math.sqrt(dx * dx + dy * dy);                         // como R: sqrt(dx^2 + dy^2)
        w[i * n + j] = A / ((a - Math.abs(dx)) * (b - Math.abs(dy)));        // traslación: |W| / |W ∩ (W + xᵢ − xⱼ)|
      }
    }
    return { nombre: p.nombre, n, A, a, b, v, x: p.x, y: p.y, d, w };
  }

  const dentroDisco = (dd, r) => dd <= r + EPS;
  const dentroAnillo = (dd, r, h) => dd >= Math.max(0, r - h) - EPS && dd <= r + h + EPS;

  // Los vecinos de un punto en su disco (con peso o sin él) y en su anillo (sin peso: es para verlos).
  function cuentaDisco(P, i, r, peso) {
    let s = 0;
    for (let j = 0; j < P.n; j++) if (j !== i && dentroDisco(P.d[i * P.n + j], r)) s += peso ? P.w[i * P.n + j] : 1;
    return s;
  }
  function cuentaAnillo(P, i, r, h) {
    let s = 0;
    for (let j = 0; j < P.n; j++) if (j !== i && dentroAnillo(P.d[i * P.n + j], r, h)) s++;
    return s;
  }

  // K̂(r) = |W| / (n (n − 1)) · Σ_{i≠j} w_ij 1{d_ij ≤ r}, con w_ij = 1 si no se corrige.
  function K(P, r, peso) {
    let s = 0;
    for (let i = 0; i < P.n; i++) s += cuentaDisco(P, i, r, peso);
    return P.A / (P.n * (P.n - 1)) * s;
  }
  const curvaK = (P, peso) => Array.from({ length: NODOS + 1 }, (_, i) => K(P, rDe(i), peso));

  // Lo que daría el azar a UN punto en un disco o un anillo ENTERO: la intensidad de los otros, (n − 1)/|W|, por el área.
  const lambdaOtros = P => (P.n - 1) / P.A;
  const azarDisco = (P, r) => lambdaOtros(P) * Math.PI * r * r;
  const azarAnillo = (P, r, h) => lambdaOtros(P) * Math.PI * ((r + h) * (r + h) - Math.pow(Math.max(0, r - h), 2));

  // Las parejas (i < j) que entran: en el disco de radio r, o en el anillo [r − h, r + h].
  function parejas(P, r, h, anillo) {
    const out = [];
    for (let i = 0; i < P.n; i++) {
      for (let j = i + 1; j < P.n; j++) {
        const dd = P.d[i * P.n + j];
        if (anillo ? dentroAnillo(dd, r, h) : dentroDisco(dd, r)) out.push(i, j);
      }
    }
    return out;
  }

  const borde = (P, i) => Math.min(P.x[i] - P.v[0], P.v[2] - P.x[i], P.y[i] - P.v[1], P.v[3] - P.y[i]);

  // El punto de partida: el de más vecinos a R_GRUPO entre los que tienen ese disco entero dentro de la ventana
  // (en las secuoyas, uno de un grupo); a igualdad, el de más vecinos muy cerca, y después el de índice menor.
  function focoGrupo(P) {
    let mejor = -1, c1 = -1, c2 = -1;
    for (let i = 0; i < P.n; i++) {
      if (borde(P, i) < R_GRUPO) continue;
      const a = cuentaDisco(P, i, R_GRUPO, false), b = cuentaDisco(P, i, 0.04, false);
      if (a > c1 || (a === c1 && b > c2)) { mejor = i; c1 = a; c2 = b; }
    }
    return mejor < 0 ? 0 : mejor;
  }

  // El del paso del borde: el más pegado a él entre los que tienen al menos tres vecinos a R_BORDE.
  function focoBorde(P) {
    let mejor = -1, db = Infinity;
    for (let pasada = 0; pasada < 2 && mejor < 0; pasada++) {
      for (let i = 0; i < P.n; i++) {
        if (pasada === 0 && cuentaDisco(P, i, R_BORDE, false) < 3) continue;
        if (borde(P, i) < db) { db = borde(P, i); mejor = i; }
      }
    }
    return mejor;
  }

  // ---- la geometría: el cuadrado de la ventana dentro del lienzo, sin deformar ----
  function ajuste(w, h, v, m) {
    const dw = v[2] - v[0], dh = v[3] - v[1];
    const aw = w - m.l - m.r, ah = h - m.t - m.b;
    const s = Math.max(1e-9, Math.min(aw / dw, ah / dh));
    const ox = m.l + (aw - dw * s) / 2, oy = m.t + (ah - dh * s) / 2;
    return {
      s, ox, oy,
      x: u => ox + (u - v[0]) * s,
      y: u => oy + (v[3] - u) * s,                // y hacia arriba, como en el mapa
      ux: px => v[0] + (px - ox) / s,
      uy: py => v[3] - (py - oy) / s
    };
  }

  // El punto más cercano a un píxel, si está a menos de `tol` píxeles; si no, −1.
  function puntoEn(P, aj, px, py, tol) {
    let mejor = -1, dm = tol;
    for (let i = 0; i < P.n; i++) {
      const dd = Math.hypot(aj.x(P.x[i]) - px, aj.y(P.y[i]) - py);
      if (dd <= dm) { dm = dd; mejor = i; }
    }
    return mejor;
  }

  const Mat = { EPS, H_ANILLO, PASO_R, NODOS, R_GRUPO, R_BORDE, PATRONES, rDe, prepara, cuentaDisco, cuentaAnillo, K, curvaK,
                lambdaOtros, azarDisco, azarAnillo, parejas, borde, focoGrupo, focoBorde, ajuste, puntoEn };

  /* ===================================================================
     2 · LA PIEZA. Lo que se dibuja y lo que se cuenta; el resto es de `Anim2D`.
     =================================================================== */
  const VERDE = '#1a7358', MORADO = '#7B3FA0', NARANJA = '#FF6600', TINTA = '#012820', GRIS = '#64748b';   // gris de 4.8:1 sobre blanco (el de antes daba 2.6)
  const ESCENAS = ['disco', 'anillo'];
  const f2 = x => x.toFixed(2), f4 = x => x.toFixed(4);
  const rTxt = i => f4(rDe(i));
  const ent = x => String(Math.round(x));
  // Frente al azar, en palabras que no son un veredicto: un 10 % arriba o abajo y ya se dice hacia dónde.
  const frente = q => !(q >= 0) ? 'sin referencia' : q > 1.1 ? 'por encima' : q < 0.9 ? 'por debajo' : 'casi encima';

  function creaDef(datos, opc) {
    opc = opc || {};
    const escena = opc.escena || 'anillo';
    if (ESCENAS.indexOf(escena) < 0) throw new Error('kanillo2d: escena desconocida «' + escena + '»');
    const ANILLO = escena === 'anillo';
    if (!datos || !datos.patrones || !datos.g) throw new Error('kanillo2d: faltan los patrones o la g publicada');
    const P = {}, C = {};
    for (const nm of PATRONES) {
      if (!datos.patrones[nm] || !datos.g[nm]) throw new Error('kanillo2d: falta el patrón ' + nm);
      P[nm] = prepara(datos.patrones[nm]);
      const g = datos.g[nm];
      if (!(g.r && g.r.length === NODOS + 1 && g.g_obs && g.g_obs.length === NODOS + 1) ||
          g.r.some((r, i) => Math.abs(r - rDe(i)) > 1e-9))
        throw new Error('kanillo2d: la g publicada de ' + nm + ' no está en la rejilla de 101 nodos de 0 a 0.25');
      const tr = curvaK(P[nm], true), sin = curvaK(P[nm], false);
      const razon = tr.map((k, i) => i ? k / (Math.PI * rDe(i) * rDe(i)) : null);
      const tope = v => Math.ceil(v * 2) / 2;
      C[nm] = {
        trasl: tr, sin, razon, g: g.g_obs,
        // la r a la que vuelve g a 1 (la del capítulo), en nodos; si no vuelve, la de los grupos
        iVuelta: Math.round((g.r_vuelve_a_1 != null ? g.r_vuelve_a_1 : R_GRUPO) / PASO_R),
        iVueltaG: g.r_vuelve_a_1 != null ? Math.round(g.r_vuelve_a_1 / PASO_R) : null,   // null: g no vuelve a 1 en el barrido
        grupo: focoGrupo(P[nm]), borde: focoBorde(P[nm]),
        maxK: Math.max(Math.max.apply(null, tr), Math.PI * 0.0625) * 1.06,
        maxRazon: Math.min(6, tope(Math.max(Math.max.apply(null, razon.slice(1)), Math.max.apply(null, g.g_obs.filter(v => v != null))) + 0.25))
      };
    }

    // Lo que se lee de un estado, con el r del estado (un nodo).
    function cuenta(E) {
      const Q = P[E.patron], c = C[E.patron], r = rDe(E.ir), peso = !ANILLO && E.peso === 'ninguno' ? false : true;
      const K1 = (peso ? c.trasl : c.sin)[E.ir], pir2 = Math.PI * r * r;
      return {
        r, peso,
        nDisco: cuentaDisco(Q, E.foco, r, false), nDiscoPeso: cuentaDisco(Q, E.foco, r, true), nAnillo: cuentaAnillo(Q, E.foco, r, H_ANILLO),
        azarDisco: azarDisco(Q, r), azarAnillo: azarAnillo(Q, r, H_ANILLO),
        K: K1, Ktr: c.trasl[E.ir], Ksin: c.sin[E.ir], pir2,
        q: E.ir ? K1 / pir2 : NaN, qtr: E.ir ? c.trasl[E.ir] / pir2 : NaN, qsin: E.ir ? c.sin[E.ir] / pir2 : NaN,
        g: c.g[E.ir], borde: borde(Q, E.foco)
      };
    }
    const nParejas = (E, anillo) => parejas(P[E.patron], rDe(E.ir), H_ANILLO, anillo).length / 2;

    /* ---- el dibujo ---- */
    const margen = c => ({ l: 10, r: 10, t: c.w > 560 ? 30 : 10, b: 10 });
    let aj = null;
    const ajusteDe = (c, nm) => {
      const m = margen(c), v = P[nm].v;
      if (aj && aj.w === c.w && aj.h === c.h && aj.nm === nm) return aj;
      return (aj = Object.assign({ w: c.w, h: c.h, nm }, ajuste(c.w, c.h, v, m)));
    };
    const radioPunto = a => Math.max(2.6, Math.min(4.6, a.s / 110));

    // La geometría visible: el radio exterior e interior del disco o del anillo, con los animables a medio camino.
    function geometria(V) {
      const r = rDe(V.ir), hueco = ANILLO ? Math.max(0, Math.min(1, V.hueco)) : 0;
      return { r, rin: hueco * Math.max(0, r - H_ANILLO), rout: r + hueco * H_ANILLO, hueco };
    }
    const enGeo = (dd, G) => dd >= G.rin - (G.hueco ? EPS : Infinity) && dd <= G.rout + EPS;

    function circulo(ctx, x, y, rr) { ctx.beginPath(); ctx.arc(x, y, Math.max(0, rr), 0, 2 * Math.PI); }

    function dibuja(c, E, V) {
      const { ctx } = c, Q = P[E.patron], a = ajusteDe(c, E.patron), G = geometria(V);
      const color = G.hueco > 0.5 ? MORADO : VERDE, relleno = G.hueco > 0.5 ? 'rgba(123,63,160,.15)' : 'rgba(26,115,88,.11)';
      const x0 = a.x(Q.v[0]), y0 = a.y(Q.v[3]), lado = (Q.v[2] - Q.v[0]) * a.s, alto = (Q.v[3] - Q.v[1]) * a.s;
      const fx = a.x(Q.x[E.foco]), fy = a.y(Q.y[E.foco]), pr = radioPunto(a);
      // 1. la ventana
      ctx.fillStyle = '#fff'; ctx.fillRect(x0, y0, lado, alto);
      // 2. el disco o el anillo del punto en foco: la parte de fuera de la ventana, solo en contorno discontinuo
      if (!E.todos) {
        ctx.save(); ctx.setLineDash([4, 4]); ctx.strokeStyle = 'rgba(71,85,105,.55)'; ctx.lineWidth = 1.2;
        circulo(ctx, fx, fy, G.rout * a.s); ctx.stroke();
        if (G.rin > 0) { circulo(ctx, fx, fy, G.rin * a.s); ctx.stroke(); }
        ctx.restore();
        ctx.save(); ctx.beginPath(); ctx.rect(x0, y0, lado, alto); ctx.clip();
        ctx.beginPath(); ctx.arc(fx, fy, G.rout * a.s, 0, 2 * Math.PI);
        if (G.rin > 0) { ctx.moveTo(fx + G.rin * a.s, fy); ctx.arc(fx, fy, G.rin * a.s, 0, 2 * Math.PI, true); }
        ctx.fillStyle = relleno; ctx.fill('evenodd');
        ctx.strokeStyle = color; ctx.lineWidth = 1.6; circulo(ctx, fx, fy, G.rout * a.s); ctx.stroke();
        if (G.rin > 0) { circulo(ctx, fx, fy, G.rin * a.s); ctx.stroke(); }
        ctx.restore();
      }
      // 3. con «todas las parejas», un segmento por pareja (la de dentro del disco o del anillo visibles)
      if (E.todos) {
        ctx.save(); ctx.beginPath(); ctx.rect(x0, y0, lado, alto); ctx.clip();
        // el anillo deja pocas parejas y se pintan más fuertes; las del disco son cientos, y más tenues para que se lean los puntos
        ctx.strokeStyle = G.hueco > 0.5 ? 'rgba(123,63,160,.62)' : 'rgba(26,115,88,.30)'; ctx.lineWidth = G.hueco > 0.5 ? 1.4 : 1;
        ctx.beginPath();
        for (let i = 0; i < Q.n; i++) {
          for (let j = i + 1; j < Q.n; j++) {
            if (!enGeo(Q.d[i * Q.n + j], G)) continue;
            ctx.moveTo(a.x(Q.x[i]), a.y(Q.y[i])); ctx.lineTo(a.x(Q.x[j]), a.y(Q.y[j]));
          }
        }
        ctx.stroke(); ctx.restore();
      }
      // 4. el borde de la ventana, encima del relleno
      ctx.strokeStyle = TINTA; ctx.lineWidth = 1.2; ctx.strokeRect(x0 + 0.5, y0 + 0.5, lado - 1, alto - 1);
      // 5. los puntos: los que cuentan para el punto en foco, en el color del disco o del anillo
      for (let i = 0; i < Q.n; i++) {
        if (i === E.foco) continue;
        const cuenta = !E.todos && enGeo(Q.d[E.foco * Q.n + i], G);
        circulo(ctx, a.x(Q.x[i]), a.y(Q.y[i]), cuenta ? pr + 0.9 : pr);
        ctx.fillStyle = cuenta ? color : GRIS; ctx.fill();
        if (cuenta) { ctx.lineWidth = 1; ctx.strokeStyle = '#fff'; ctx.stroke(); }
      }
      // 6. el radio, con su r, en una dirección que quede dentro del lienzo
      if (!E.todos && G.r > 0) {
        const L = G.r * a.s;
        const angs = [-Math.PI / 4, -3 * Math.PI / 4, Math.PI / 4, 3 * Math.PI / 4, -Math.PI / 2, 0, Math.PI];
        const ang = angs.find(t => { const ex = fx + L * Math.cos(t), ey = fy + L * Math.sin(t); return ex > 14 && ex < c.w - 14 && ey > 14 && ey < c.h - 14; });
        const t = ang === undefined ? -Math.PI / 4 : ang;
        ctx.save(); ctx.strokeStyle = TINTA; ctx.lineWidth = 1.2;
        ctx.beginPath(); ctx.moveTo(fx, fy); ctx.lineTo(fx + L * Math.cos(t), fy + L * Math.sin(t)); ctx.stroke();
        if (L > 22) {
          ctx.font = "italic 600 12px 'Montserrat', sans-serif"; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
          const mx = fx + (L / 2) * Math.cos(t) - 9 * Math.sin(t), my = fy + (L / 2) * Math.sin(t) + 9 * Math.cos(t);
          ctx.lineWidth = 3.5; ctx.strokeStyle = 'rgba(255,255,255,.92)'; ctx.strokeText('r', mx, my);
          ctx.fillStyle = TINTA; ctx.fillText('r', mx, my);
        }
        ctx.restore();
      }
      // 7. el punto bajo el puntero y el punto en foco, encima de todo
      if (E.hover >= 0 && E.hover !== E.foco) {
        circulo(ctx, a.x(Q.x[E.hover]), a.y(Q.y[E.hover]), pr + 3.5); ctx.lineWidth = 2; ctx.strokeStyle = 'rgba(255,102,0,.75)'; ctx.stroke();
      }
      circulo(ctx, fx, fy, pr + 2.2); ctx.fillStyle = NARANJA; ctx.fill(); ctx.lineWidth = 1.6; ctx.strokeStyle = '#fff'; ctx.stroke();
      circulo(ctx, fx, fy, pr + 3.4); ctx.lineWidth = 1; ctx.strokeStyle = TINTA; ctx.stroke();     // el naranja solo da 2.9:1 sobre blanco
    }

    /* ---- el panel de al lado ---- */
    function ejes(ctx, c, m, ymax, fmt) {
      const W = c.w - m.l - m.r, H = c.h - m.t - m.b;
      const px = r => m.l + (r / 0.25) * W, py = v => m.t + (1 - v / ymax) * H;
      ctx.font = "10px 'Fira Code', monospace"; ctx.lineWidth = 1; ctx.strokeStyle = '#cbd5e1'; ctx.fillStyle = '#475569';
      ctx.textAlign = 'right'; ctx.textBaseline = 'middle';
      [0, ymax].forEach(v => { ctx.beginPath(); ctx.moveTo(m.l, py(v) + 0.5); ctx.lineTo(m.l + W, py(v) + 0.5); ctx.stroke(); ctx.fillText(fmt(v), m.l - 4, py(v)); });
      ctx.textAlign = 'center'; ctx.textBaseline = 'top';
      [0, 0.1, 0.2].forEach(r => ctx.fillText(String(r), px(r), m.t + H + 4));
      return { px, py, W, H };
    }
    function serie(ctx, ax, vals, color, ancho, raya) {
      ctx.save(); ctx.strokeStyle = color; ctx.lineWidth = ancho; if (raya) ctx.setLineDash(raya);
      ctx.beginPath();
      let dentro = false;
      vals.forEach((v, i) => {
        if (v == null || !isFinite(v)) { dentro = false; return; }
        const X = ax.px(rDe(i)), Y = ax.py(v);
        if (dentro) ctx.lineTo(X, Y); else { ctx.moveTo(X, Y); dentro = true; }
      });
      ctx.stroke(); ctx.restore();
    }
    function marca(ctx, ax, rv, vals, color, m) {
      const i0 = Math.min(NODOS, Math.floor(rv / PASO_R)), i1 = Math.min(NODOS, i0 + 1), f = rv / PASO_R - i0;
      if (vals[i0] == null || vals[i1] == null) return;
      const v = vals[i0] * (1 - f) + vals[i1] * f;
      if (!isFinite(v)) return;
      ctx.fillStyle = color; circulo(ctx, ax.px(rv), ax.py(Math.min(v, ax.ymax)), 3.8); ctx.fill();
      ctx.strokeStyle = '#fff'; ctx.lineWidth = 1.4; ctx.stroke();
    }
    function leyenda(ctx, m, items, ancho) {
      ctx.font = "600 10px 'Montserrat', sans-serif"; ctx.textAlign = 'left'; ctx.textBaseline = 'middle';
      // si no cabe (un panel de 200 px), cada entrada se queda con su forma corta, la tercera de su lista
      const total = items.reduce((s, it) => s + 25 + ctx.measureText(it[0]).width, 0);
      if (ancho && total > ancho) items = items.map(it => [it[3] || it[0], it[1], it[2]]);
      let x = m.l + 2;
      items.forEach(([txt, color, raya]) => {
        ctx.save(); ctx.strokeStyle = color; ctx.lineWidth = 2; if (raya) ctx.setLineDash(raya);
        ctx.beginPath(); ctx.moveTo(x, 8); ctx.lineTo(x + 12, 8); ctx.stroke(); ctx.restore();
        ctx.fillStyle = '#334155'; ctx.fillText(txt, x + 15, 8);
        x += 15 + ctx.measureText(txt).width + 10;
      });
    }

    function panel(c, id, E, V) {
      const { ctx } = c, k = C[E.patron], rv = rDe(V.ir);
      const m = { l: 36, r: 8, t: 18, b: 18 };
      if (id === 'k') {
        const peso = E.peso !== 'ninguno';
        const ax = Object.assign(ejes(ctx, c, m, k.maxK, v => v.toFixed(2)), { ymax: k.maxK });
        serie(ctx, ax, k.trasl.map((_, i) => Math.PI * rDe(i) * rDe(i)), '#64748b', 1.3, [4, 3]);
        if (!peso) serie(ctx, ax, k.trasl, 'rgba(26,115,88,.45)', 1.3, [2, 2]);
        const vals = peso ? k.trasl : k.sin;
        serie(ctx, ax, vals, VERDE, 1.9);
        ctx.save(); ctx.strokeStyle = 'rgba(255,102,0,.55)'; ctx.setLineDash([2, 2]);
        ctx.beginPath(); ctx.moveTo(ax.px(rv), m.t); ctx.lineTo(ax.px(rv), m.t + ax.H); ctx.stroke(); ctx.restore();
        marca(ctx, ax, rv, vals, NARANJA);
        leyenda(ctx, m, [[peso ? 'K observada' : 'K sin corregir', VERDE, null, peso ? 'K' : 'K sin peso']]
          .concat(peso ? [] : [['K con peso', 'rgba(26,115,88,.55)', [2, 2], 'con peso']]).concat([['π r²', '#64748b', [4, 3]]]), c.w - m.l);
      } else {
        const ax = Object.assign(ejes(ctx, c, m, k.maxRazon, v => v.toFixed(1)), { ymax: k.maxRazon });
        ctx.save(); ctx.setLineDash([4, 3]); ctx.strokeStyle = '#64748b'; ctx.lineWidth = 1.3;
        ctx.beginPath(); ctx.moveTo(m.l, ax.py(1)); ctx.lineTo(m.l + ax.W, ax.py(1)); ctx.stroke(); ctx.restore();
        const rec = vals => vals.map(v => v == null ? v : Math.min(v, k.maxRazon));
        serie(ctx, ax, rec(k.razon), VERDE, 1.9);
        serie(ctx, ax, rec(k.g), MORADO, 1.9);
        ctx.save(); ctx.strokeStyle = 'rgba(255,102,0,.55)'; ctx.setLineDash([2, 2]);
        ctx.beginPath(); ctx.moveTo(ax.px(rv), m.t); ctx.lineTo(ax.px(rv), m.t + ax.H); ctx.stroke(); ctx.restore();
        marca(ctx, ax, rv, k.razon, VERDE);
        marca(ctx, ax, rv, k.g, MORADO);
        leyenda(ctx, m, [['disco: K / π r²', VERDE, null, 'K / π r²'], ['anillo: g', MORADO, null, 'g'], ['azar: 1', '#64748b', [4, 3], '1']], c.w - m.l);
      }
    }

    /* ---- los textos ---- */
    const vecinos = n => n === 1 ? '1 vecino' : ent(n) + ' vecinos';
    const disco = 'disco', anillo = 'anillo';
    // Las dos variantes de cada frase condicional miden parecido, para que el texto no empuje el mapa al cambiar de estado.
    const fueraVentana = (E, cu) => cu.borde < cu.r ? ' Parte de su disco cae fuera de la ventana: ahí no se ve a nadie.'
                                                    : ' Su disco cabe entero en la ventana: todo lo que hay dentro se ve.';
    const anilloTxt = cu => cu.r < H_ANILLO ? '0 y ' + f4(cu.r + H_ANILLO) + ' (con r tan pequeño, el anillo empieza en 0)'
                                            : f4(cu.r - H_ANILLO) + ' y ' + f4(cu.r + H_ANILLO);
    // «Arrastra» solo donde la g publicada ya volvió a 1 y K sigue claramente por encima: no en un patrón cuya g no vuelve.
    const arrastra = (E, cu) => { const iv = C[E.patron].iVueltaG; return iv != null && E.ir >= iv - 1 && cu.q > 1.1 && Math.abs(cu.g - 1) <= 0.1; };

    const pasosDisco = [
      { corto: 'Un punto', titulo: 'Un punto y su disco',
        texto: E => {
          const cu = cuenta(E);
          return 'K pregunta cuántos otros puntos tiene un punto a distancia r o menos: los que caen en su disco. Este tiene <strong>' + vecinos(cu.nDisco) +
                 '</strong> a r = ' + rTxt(E.ir) + '. Si los demás estuvieran repartidos al azar con la misma intensidad, en un disco entero como este habría de media <strong>' +
                 f2(cu.azarDisco) + '</strong>, que es (n − 1) π r² / |W|.' + fueraVentana(E, cu) + ' Haz clic en otro punto para ver el suyo.';
        },
        estado: E => ({ ir: 24, todos: 0, peso: 'traslacion', foco: C[E.patron].grupo }), pausa: 4.5 },
      { corto: 'El disco crece', titulo: 'El disco crece, y no suelta a nadie',
        texto: E => {
          const cu = cuenta(E);
          return 'Al crecer r el disco solo gana vecinos: los que ya estaban siguen dentro. Este punto tiene ' + vecinos(cu.nDisco) + ' a r = ' + rTxt(E.ir) +
                 ' (el azar, en un disco entero: ' + f2(cu.azarDisco) + '). La curva de al lado es K para todo el patrón: los vecinos de cada punto' +
                 (cu.peso ? ', con su peso,' : '') + ' promediados y divididos por (n − 1)/|W|. ' +
                 (E.ir ? 'Ahora va ' + frente(cu.q) + ' de π r², la de CSR: K vale ' + f2(cu.q) + ' veces π r².' : 'En r = 0 no hay ningún vecino que contar.');
        },
        estado: { ir: NODOS }, tween: { ir: 7 }, pausa: 2.5 },
      { corto: 'Todas las parejas', titulo: 'Todas las parejas a r o menos',
        texto: E => {
          const cu = cuenta(E), m = nParejas(E, false);
          return 'Cada segmento une dos puntos a r = ' + rTxt(E.ir) + ' o menos: son las <strong>' + ent(m) + '</strong> parejas que suma K, cada una dos veces (una desde cada punto)' +
                 (cu.peso ? ' y con su peso' : ', sin peso') + '. La suma, por |W| / (n (n − 1)), da K = ' + f4(cu.K) + (E.ir ? ', que es ' + f2(cu.q) + ' veces π r².' : '.');
        },
        estado: { todos: 1, ir: 40 }, pausa: 4 },
      { corto: 'El borde', titulo: 'El borde esconde vecinos',
        texto: E => {
          const cu = cuenta(E);
          const sitio = cu.borde < cu.r
            ? 'Este punto está a ' + f4(cu.borde) + ' del borde: con r = ' + rTxt(E.ir) + ' parte de su disco cae fuera de la ventana, y los vecinos que tendría allí no se ven. '
            : 'El disco de este punto, con r = ' + rTxt(E.ir) + ', cabe entero en la ventana; acércate al borde (o sube r) para ver lo que pasa allí. ';
          const compara = !(cu.Ktr > 0)
            ? 'A este r no hay todavía ninguna pareja en todo el patrón: K vale 0 con peso y sin él, y no hay nada que corregir. '
            : f2(cu.qsin) === f2(cu.qtr)
              ? 'A este r las dos K casi coinciden (' + f2(cu.qtr) + ' veces π r²): las parejas son cortas y el borde apenas las esconde. '
              : 'Sin corregir (todos los pesos a 1), K se queda corta en todo el patrón: ' + f2(cu.qsin) + ' veces π r², frente a ' + f2(cu.qtr) + ' con el peso de traslación. ';
          return sitio + compara +
            'Ese peso no adivina a los de fuera: cuenta cada pareja algo más de una vez, más cuanto más le cuesta a la ventana dejarla ver entera, y en el conjunto compensa lo que el borde esconde. Cambia el peso para comparar.';
        },
        estado: E => ({ foco: C[E.patron].borde, ir: 60, todos: 0, peso: 'ninguno' }), pausa: 5 }
    ];

    const pasosAnillo = [
      { corto: 'El disco', titulo: 'El disco: K cuenta todo lo que hay hasta r',
        texto: E => {
          const cu = cuenta(E);
          return 'Este punto tiene <strong>' + vecinos(cu.nDisco) + '</strong> a r = ' + rTxt(E.ir) + ' o menos; en un disco entero, el azar le daría ' + f2(cu.azarDisco) +
                 '. Eso es lo que cuenta K, y para todo el patrón vale ' + (E.ir ? f2(cu.q) + ' veces π r² (la curva verde de al lado).' : '0 en r = 0.') + fueraVentana(E, cu);
        },
        estado: E => ({ ir: 16, hueco: 0, todos: 0, foco: C[E.patron].grupo }), pausa: 4 },
      { corto: 'Más lejos', titulo: 'Más lejos, el disco sigue contando lo de antes',
        texto: E => {
          const cu = cuenta(E);
          return 'A r = ' + rTxt(E.ir) + ' el disco contiene a todos los discos más pequeños: los vecinos de cerca siguen contados. Este punto tiene ahora ' + vecinos(cu.nDisco) +
                 ' (el azar, en un disco entero: ' + f2(cu.azarDisco) + '), y para todo el patrón K vale ' + (E.ir ? f2(cu.q) + ' veces π r², ' + frente(cu.q) + ' de lo que daría el azar.' : '0.');
        },
        estado: E => ({ ir: C[E.patron].iVuelta, hueco: 0, todos: 0 }), tween: { ir: 3.5 }, pausa: 3.5 },
      { corto: 'El anillo', titulo: 'El anillo: g mira solo esa distancia',
        texto: E => {
          const cu = cuenta(E);
          const g = cu.g, vacio = nParejas(E, true) === 0;
          const enG = vacio ? 'en todo el patrón no hay ninguna pareja a esa distancia, y ese valor es el suavizado de pcf, que recoge parejas algo más lejanas'
            : g > 1.1 ? 'a esa distancia hay más parejas de las que daría el azar' : g < 0.9 ? 'a esa distancia hay menos parejas de las que daría el azar'
            : 'a esa distancia hay casi las parejas que daría el azar';
          return 'g se queda con las parejas que están a esa distancia: el anillo entre ' + anilloTxt(cu) + '. Este punto tiene ' + vecinos(cu.nAnillo) +
                 ' en él; en un anillo entero, el azar le daría ' + f2(cu.azarAnillo) + '. Para todo el patrón, g vale <strong>' + f2(g) + '</strong>: ' + enG + '.' +
                 (!E.ir ? '' : arrastra(E, cu) ? ' En el mismo r, K vale todavía ' + f2(cu.q) + ' veces π r²: arrastra lo que contó más cerca.'
                                               : ' En el mismo r, K vale ' + f2(cu.q) + ' veces π r²: el disco y el anillo, comparados con el azar.');
        },
        // los pasos 3 a 5 hablan del r en que g vuelve a 1: lo ponen, por si se llega a ellos sin pasar por el 2
        estado: E => ({ ir: C[E.patron].iVuelta, hueco: 1, todos: 0 }), tween: { hueco: 1 }, pausa: 5 },
      { corto: 'Todas, disco', titulo: 'Todas las parejas del disco',
        texto: E => { const m = nParejas(E, false);
          return m === 0 ? 'A r = ' + rTxt(E.ir) + ' no hay todavía ninguna pareja: ningún punto tiene a otro tan cerca. Sube r para verlas aparecer.'
            : 'Las <strong>' + ent(m) + '</strong> parejas a r = ' + rTxt(E.ir) + ' o menos, de todos los puntos: las que suma K. ' +
              'Las más cortas siguen ahí, porque un disco grande contiene a todos los pequeños.'; },
        estado: E => ({ ir: C[E.patron].iVuelta, todos: 1, hueco: 0 }), tween: { hueco: 1 }, pausa: 3.5 },
      { corto: 'Todas, anillo', titulo: 'Todas las parejas del anillo',
        // El anillo [r − h, r + h] se sale del disco de radio r: con r pequeño puede tener MÁS parejas que él.
        texto: E => { const na = nParejas(E, true), nd = nParejas(E, false);
          return 'Solo las parejas que están entre ' + anilloTxt(cuenta(E)) + ': <strong>' + ent(na) + '</strong>' +
                 (na < nd ? ', frente a las ' + ent(nd) + ' del disco.' : '; el disco de radio r tiene ' + ent(nd) + '.') +
                 ' Son las que mira g, y por eso g dice a qué distancia está la estructura y K no.'; },
        estado: E => ({ ir: C[E.patron].iVuelta, todos: 1, hueco: 1 }), tween: { hueco: 1 }, pausa: 4 }
    ];
    const pasos = ANILLO ? pasosAnillo : pasosDisco;

    const nombres = { cells: 'Células', japanesepines: 'Pinos', redwood: 'Secuoyas' };
    // la clave de colores del pie; con colores forzados, sin esto los ● perdían su color y la clave no se leía
    const punto = col => '<span style="color:' + col + ';forced-color-adjust:none">●</span>';
    const mandos = [
      { tipo: 'deslizador', id: 'ir', etiqueta: 'Radio r', min: 0, max: NODOS, paso: 1, salida: i => rTxt(i) },
      { tipo: 'botones', id: 'patron', etiqueta: 'Patrón', opciones: PATRONES.map(nm => [nm, nombres[nm]]) }
    ].concat(ANILLO
      ? [{ tipo: 'botones', id: 'hueco', etiqueta: 'Qué se cuenta', opciones: [[0, 'Disco (K)'], [1, 'Anillo (g)']] }]
      : [{ tipo: 'botones', id: 'peso', etiqueta: 'Peso de cada pareja', opciones: [['traslacion', 'Traslación'], ['ninguno', 'Sin corregir']] }]
    ).concat([
      { tipo: 'botones', id: 'todos', etiqueta: 'Mirar', opciones: [[0, 'Un punto'], [1, 'Todas las parejas']] },
      { tipo: 'ciclo', id: 'foco', etiqueta: 'Punto en foco', n: E => P[E.patron].n, anterior: 'Punto anterior', siguiente: 'Punto siguiente',
        texto: (i, E) => 'punto ' + (i + 1) + ' de ' + P[E.patron].n }
    ]);

    // El arrastre del borde del círculo: el radio sigue al puntero. Vive aquí porque `puntero` no guarda estado.
    let arrastrando = false;
    const def = {
      id: 'kanillo-' + escena,
      css: '.a2d.kanillo .a2d-panel{height:9.5rem}',
      aria: 'Un patrón de puntos en un cuadrado de lado 1. Hay un punto en foco, con un ' + (ANILLO ? 'disco o un anillo' : 'disco') +
            ' de radio r alrededor; la descripción de debajo dice cuántos vecinos caen dentro y cuántos daría el azar. ' +
            'La gráfica de al lado muestra ' + (ANILLO ? 'K dividida por π r² y g contra r, frente a 1.' : 'K contra r, frente a π r².'),
      ayuda: 'Clic en un punto para ponerlo en foco · arrastra el borde del círculo para cambiar r',
      ayudaTeclado: 'Con el lienzo enfocado, las flechas izquierda y derecha cambian el punto en foco, arriba y abajo cambian r de ' + PASO_R + ' en ' + PASO_R +
                    ', Re Pág y Av Pág de diez en diez, e Inicio y Fin lo llevan a 0 y a 0.25. Los mandos de debajo hacen lo mismo.',
      pie: 'Células (Crick y Ripley), pinos japoneses (Numata) y plántulas de secuoya (Strauss): los tres canónicos del capítulo, en un cuadrado de lado 1, así que r se mide en lados de la ventana. ' +
           punto(VERDE) + (ANILLO ? '/' + punto(MORADO) : '') + ' cuenta para el punto en foco · ' + punto(GRIS) + ' no cuenta · ' +
           punto(NARANJA) + ' punto en foco. K se calcula aquí exacta, pareja a pareja' + (ANILLO ? ', con el peso de traslación' : '') +
           '; la curva publicada de los simuladores interpola la rejilla de <code>Kest</code> y puede diferir de esta, sobre todo en K / π r² a r pequeño, donde π r² es diminuto.' +
           (ANILLO ? ' El anillo dibujado mide ' + 2 * H_ANILLO + ' de ancho, solo para ver qué parejas están a esa distancia; la g de la gráfica es la de <code>pcf</code>, que suaviza con su propio núcleo.' : ''),
      sinLienzo: ANILLO
        ? 'Dice lo mismo que el texto del módulo 9: K cuenta los vecinos de cada punto dentro de un disco de radio r, así que lo que encontró cerca lo sigue contando lejos; g mira solo el anillo de radio r, y por eso dice a qué distancia está la estructura.'
        : 'Dice lo mismo que el texto del módulo 8: K cuenta, alrededor de cada punto, los otros que caen dentro de un disco de radio r, los promedia y los divide por la intensidad, y lo compara con π r², lo que daría el azar.',
      paneles: [ANILLO
        ? { id: 'razones', etiqueta: 'El disco y el anillo, frente al azar (todo el patrón)', aria: 'K dividida por π r² y la g publicada, contra r de 0 a 0.25, con la referencia del azar en 1' }
        : { id: 'k', etiqueta: 'K observada y π r² (todo el patrón)', aria: 'K contra r de 0 a 0.25, con π r², la referencia del azar' }],
      mandos,
      animables: { ir: 1.1, hueco: 0.8 },
      // los estados que alargan los textos (r casi 0: el anillo empieza en 0 y está vacío; r máximo; otros patrones):
      // la leyenda reserva su alto desde el principio y no empuja el mapa la primera vez que aparecen
      sondas: [{ ir: 2 }, { ir: 1 }, { ir: NODOS }, { patron: 'cells', ir: 30 }, { patron: 'japanesepines', ir: 4 }],
      pasoImpresion: pasos.length,
      pasos,
      inicial: () => ({ paso: 1, patron: 'redwood', ir: ANILLO ? 16 : 24, hueco: 0, peso: 'traslacion', todos: 0, foco: C.redwood.grupo, hover: -1 }),
      normaliza: (p, E) => {
        const out = Object.assign({}, p);
        if ('patron' in out && PATRONES.indexOf(out.patron) < 0) delete out.patron;
        const nm = out.patron || E.patron, n = P[nm].n;
        // otro patrón: el punto en foco (si no viene) pasa a ser el de partida de ese patrón, y la marca se va
        if ('patron' in out && out.patron !== E.patron) {
          if (!('foco' in out)) out.foco = C[nm].grupo;
          out.hover = -1;
          aj = null;
        }
        if ('ir' in out) out.ir = Math.min(NODOS, Math.max(0, Math.round(out.ir)));
        if ('foco' in out) out.foco = Math.min(n - 1, Math.max(0, Math.round(out.foco)));
        if ('hover' in out) out.hover = Math.min(n - 1, Math.max(-1, Math.round(out.hover)));
        if ('paso' in out) out.paso = Math.min(pasos.length, Math.max(1, Math.round(out.paso)));
        if ('hueco' in out) out.hueco = ANILLO && out.hueco ? 1 : 0;
        if ('todos' in out) out.todos = out.todos ? 1 : 0;
        if ('peso' in out) out.peso = !ANILLO && out.peso === 'ninguno' ? 'ninguno' : 'traslacion';
        // EL PASO SIGUE A LOS CONMUTADORES: el texto que se ve tiene que hablar de lo que se dibuja. Con el anillo pulsado
        // en el paso 1, la leyenda hablaba del disco; con «todas las parejas» en el paso 1, de un punto.
        if (!('paso' in out) && ('hueco' in out || 'todos' in out || 'peso' in out)) {
          const sig = Object.assign({}, E, out);
          if (ANILLO) out.paso = sig.todos ? (sig.hueco ? 5 : 4) : (sig.hueco ? 3 : (E.paso <= 2 ? E.paso : 2));
          else out.paso = sig.todos ? 3 : sig.peso === 'ninguno' ? 4 : (E.paso <= 2 ? E.paso : 2);
        }
        return out;
      },
      dibuja, panel,
      puntero: (ev, E, V, c) => {
        if (!c || !c.w) return null;
        const Q = P[E.patron], a = ajusteDe(c, E.patron);
        if (ev.tipo === 'sale') { arrastrando = false; return { poner: { hover: -1 }, cursor: '' }; }
        const radioDe = () => Math.hypot(a.ux(ev.x) - Q.x[E.foco], a.uy(ev.y) - Q.y[E.foco]) / PASO_R;
        const distBorde = () => Math.abs(Math.hypot(ev.x - a.x(Q.x[E.foco]), ev.y - a.y(Q.y[E.foco])) - geometria(V).rout * a.s);
        const enBorde = () => !E.todos && distBorde() <= 9;
        if (ev.tipo === 'abajo') {
          // El borde gana si el toque cae a 9 px o menos de él y más cerca de él que del punto más próximo: con el dedo y la
          // tolerancia de 18 px, antes casi cualquier punto del borde tenía un punto al lado y el arrastre no empezaba nunca.
          const i = puntoEn(Q, a, ev.x, ev.y, ev.tactil ? 18 : 12);
          const dBorde = distBorde(), dPunto = i >= 0 ? Math.hypot(a.x(Q.x[i]) - ev.x, a.y(Q.y[i]) - ev.y) : Infinity;
          if (!E.todos && dBorde <= 9 && dBorde < dPunto) { arrastrando = true; return { poner: { ir: radioDe() }, captura: true, cursor: 'grabbing' }; }
          if (i >= 0) return { poner: { foco: i } };
          return null;
        }
        if (ev.tipo === 'mueve') {
          if (arrastrando) return { poner: { ir: radioDe() }, cursor: 'grabbing' };
          const i = puntoEn(Q, a, ev.x, ev.y, 12);
          return { poner: { hover: i }, cursor: i >= 0 ? 'pointer' : enBorde() ? 'grab' : '' };
        }
        if (ev.tipo === 'arriba') { arrastrando = false; return null; }
        return null;
      },
      tecla: (ev, E) => {
        const n = P[E.patron].n;
        switch (ev.key) {
          case 'ArrowRight': return { foco: (E.foco + 1) % n };
          case 'ArrowLeft': return { foco: (E.foco + n - 1) % n };
          case 'ArrowUp': return { ir: E.ir + 1 };
          case 'ArrowDown': return { ir: E.ir - 1 };
          case 'PageUp': return { ir: E.ir + 10 };
          case 'PageDown': return { ir: E.ir - 10 };
          case 'Home': return { ir: 0 };
          case 'End': return { ir: NODOS };
          default: return null;
        }
      },
      lectura: E => {
        const cu = cuenta(E), enAnillo = ANILLO && E.hueco;
        const l = [['r', rTxt(E.ir)],
          ['vecinos de este punto', enAnillo ? ent(cu.nAnillo) + ' <span class="a2d-r">en el anillo</span>'
            : ent(cu.nDisco) + (!ANILLO && cu.peso ? ' <span class="a2d-r">(con sus pesos, ' + f2(cu.nDiscoPeso) + ')</span>' : '')],
          ['el azar, ' + (enAnillo ? 'en un anillo entero' : 'en un disco entero'), f2(enAnillo ? cu.azarAnillo : cu.azarDisco)]];
        if (ANILLO) {
          l.push(['K / π r², todo el patrón', E.ir ? f2(cu.q) : '—'], ['g, todo el patrón', f2(cu.g)]);
        } else {
          l.push([cu.peso ? 'K observada' : 'K sin corregir', f4(cu.K)], ['π r²', f4(cu.pir2)], ['K / π r²', E.ir ? f2(cu.q) : '—']);
        }
        if (E.todos) l.push(['parejas dibujadas', ent(nParejas(E, !!enAnillo))]);
        return l;
      },
      alt: E => {
        const cu = cuenta(E), Q = P[E.patron], enAnillo = ANILLO && E.hueco;
        return 'Patrón ' + nombres[E.patron].toLowerCase() + ', ' + Q.n + ' puntos en un cuadrado de lado 1. Punto en foco: el ' + (E.foco + 1) + ', en (' + f2(Q.x[E.foco]) + ', ' + f2(Q.y[E.foco]) + '). ' +
               'Con r = ' + rTxt(E.ir) + ' tiene ' + vecinos(enAnillo ? cu.nAnillo : cu.nDisco) + ' en su ' + (enAnillo ? 'anillo, entre ' + anilloTxt(cu) : 'disco') +
               '; el azar daría ' + f2(enAnillo ? cu.azarAnillo : cu.azarDisco) + ' en un ' + (enAnillo ? 'anillo' : 'disco') + ' entero. ' +
               (E.ir ? 'Para todo el patrón, K vale ' + f2(cu.q) + ' veces π r²' + (cu.peso ? '' : ' sin corregir') : 'En r = 0 no hay vecinos') +
               (ANILLO ? ', y g vale ' + f2(cu.g) + '.' : '.') + (E.todos ? ' Se dibujan las ' + ent(nParejas(E, !!enAnillo)) + ' parejas de todos los puntos.' : '');
      }
    };
    def.interno = { P, C, cuenta, nParejas, geometria, ajusteDe, margen, escena };     // para las pruebas
    return def;
  }

  function monta(cont, datos, opc) {
    opc = opc || {};
    if (!global.Anim2D) throw new Error('kanillo2d: falta anim2d.js');
    const api = global.Anim2D.monta(cont, creaDef(datos, opc), opc);
    cont.classList.add('kanillo');
    return api;
  }

  const KAnillo2D = { monta, creaDef, matematica: Mat };
  global.KAnillo2D = KAnillo2D;
  if (typeof module === 'object' && module.exports) module.exports = KAnillo2D;
})(typeof window !== 'undefined' ? window : globalThis);
