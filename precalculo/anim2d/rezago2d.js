/* =====================================================================
   rezago2d.js — «Wy es una media de vecinos, y aplicada una y otra vez aplana el mapa»

   Material de Estadística Espacial 2026-II (20929). Capítulo 6, módulo 10.
   Corre sobre la cáscara `anim2d.js` (`Anim2D.monta`).

   QUÉ ENSEÑA, EN CUATRO PASOS
     1 · el dato: CRIME en los 49 barrios de Columbus, con una escala de color FIJA
         (la de y). Es la advertencia del módulo: si cada capa se pintara contra su
         propio máximo, el aplanado no se vería.
     2 · Wy: cada barrio pasa a valer la MEDIA de sus vecinos, y se ve la cuenta de uno.
     3 · W otra vez, W²y: la media de las medias. NO es la contigüidad de orden 2 —cuenta
         también al propio barrio (ir y volver) y a un vecino de siempre cuando lo es también
         de otro vecino, que es lo habitual pero no lo seguro (en Columbus falla 1 de las 118
         parejas de la reina, 21–34, y 7 de las 100 de la torre)—; es lo que el módulo 11 llama
         apilar capas. Y por la diagonal su correlación con y SUBE (0.68 → 0.78 con la reina):
         el propio barrio pesa de media un 22 % en su W²y. La media de los vecinos de orden 2 de
         verdad correlaciona 0.30. El paso lo dice con las cifras del barrio en foco, y el mapa
         marca con línea discontinua a los de orden 2 (auditoría del 2026-10-02).
     4 · muchas veces: el mapa tiende a un solo valor, y ese valor NO es la media de y sino
         la media PONDERADA POR EL GRADO, Σ dᵢ yᵢ / Σ dᵢ. La W por filas es una cadena de
         Markov y su distribución estacionaria es proporcional al grado.

   LA LETRA ES t, NO k (auditoría del 2026-10-02): en el mismo módulo, k son los vecinos más próximos del módulo 4
   («con k = 4»). Lo que el estudiante lee dice t = veces que se aplica W; el código sigue llamándolo `k`.

   SOLO SE ITERA W (estandarizada por filas). B, C, U y S no son contracciones (los radios
   espectrales medidos son 6.12, 1.27, 1.13 y 0.026): iterarlas no aplana, explota o se
   apaga, y no es lo que el módulo enseña.

   LA MATEMÁTICA ES PURA Y SE PRUEBA CONTRA R. `Mat` no toca el DOM: `prueba_rezago2d.py` la
   compara con `spdep` (poly2nb, nb2listw, lag.listw) a 1e-11 en la media, la desviación,
   la correlación y la pendiente de Wᵏy para k = 0…70, y barrio a barrio en seis k. Lo
   que la página trae de fuera es CRIME (49 números) y el mapa del capítulo (`cap6-w`); las
   cifras que muestra las calcula esta misma aritmética, no se leen de ninguna tabla.

   LA GEOMETRÍA TAMBIÉN ES LOCAL Y SE PRUEBA. Se copian `cajaQ` y `ajuste` de la plantilla
   en vez de llamarlas, para poder probar en Node el clic (qué barrio hay bajo un punto)
   sin un lienzo; `prueba_rezago2d.py` extrae las originales de la plantilla y comprueba que
   dan lo mismo, así que si la plantilla cambia, esto avisa. El color sí se inyecta
   (`opc.color`, que es `geomapaColor` y trae el filtro de daltonismo del capítulo).
   ===================================================================== */
(function (global) {
  'use strict';

  /* ===================================================================
     1 · MATEMÁTICA. Sin DOM.
     =================================================================== */
  // Hasta dónde llega el deslizador. 70 y no 60 (revisión del 2026-10-02): la prosa del módulo dice que con la reina
  // hacen falta 66 aplicaciones para dejar la desviación en el 5 % de la de y (56 con la torre), y con 60 el lector no
  // podía comprobarlo: la línea del 5 % del perfil no se cruzaba nunca con la reina.
  const K_MAX = 70;
  const CASI_UNO = 0.10;      // el paso 4 dice «casi un solo color» solo con la desviación en el 10 % de la de y o menos
  const VECINDADES = ['reina', 'torre'];

  // De las aristas del mapa (pares i, j en base 1, aplanados) a la lista de vecinos de cada barrio (base 0).
  function vecinosDe(aristas, n) {
    if (aristas.length % 2) throw new Error('aristas: la lista aplanada tiene longitud impar');
    const conj = Array.from({ length: n }, () => new Set());
    for (let i = 0; i < aristas.length; i += 2) {
      const a = aristas[i] - 1, b = aristas[i + 1] - 1;
      if (!(a >= 0 && a < n && b >= 0 && b < n) || a === b) throw new Error('arista fuera de rango: ' + aristas[i] + '–' + aristas[i + 1]);
      conj[a].add(b);
      conj[b].add(a);
    }
    return conj.map(s => Array.from(s).sort((p, q) => p - q));
  }

  const media = v => { let s = 0; for (let i = 0; i < v.length; i++) s += v[i]; return s / v.length; };
  const sd = v => {                                     // ddof = 1, como R y como el capítulo
    const m = media(v);
    let s = 0;
    for (let i = 0; i < v.length; i++) s += (v[i] - m) * (v[i] - m);
    return Math.sqrt(s / (v.length - 1));
  };
  const cov = (a, b) => {
    const ma = media(a), mb = media(b);
    let s = 0;
    for (let i = 0; i < a.length; i++) s += (a[i] - ma) * (b[i] - mb);
    return s / (a.length - 1);
  };

  // Wy con W estandarizada por filas: la MEDIA de los vecinos. Un barrio sin vecinos no tiene media.
  function rezago(vec, y) {
    return vec.map(nb => {
      if (!nb.length) throw new Error('un barrio sin vecinos no tiene media');
      let s = 0;
      for (let j = 0; j < nb.length; j++) s += y[nb[j]];
      return s / nb.length;
    });
  }

  // [y, Wy, W²y, …, Wᵏy]
  function capas(vec, y, kMax) {
    const out = [y.slice()];
    for (let k = 1; k <= kMax; k++) out.push(rezago(vec, out[k - 1]));
    return out;
  }

  // Lo que se lee de una capa v frente al dato y. La PENDIENTE de v sobre y es cov(y, v)/var(y)
  // = cor · sd(v)/sd(y); con k = 1 es el I de Moran del capítulo 7. NO es la correlación.
  function resumen(y, v) {
    return { media: media(v), sd: sd(v), cor: cov(y, v) / (sd(y) * sd(v)), pendiente: cov(y, v) / cov(y, y) };
  }

  // A dónde va Wᵏy: Σ dᵢ yᵢ / Σ dᵢ (no la media de y).
  function limite(vec, y) {
    let num = 0, den = 0;
    for (let i = 0; i < vec.length; i++) { num += vec[i].length * y[i]; den += vec[i].length; }
    return num / den;
  }

  // Los vecinos de orden 2 de verdad (los de `nblag`): vecinos de un vecino que no son el barrio ni vecinos suyos.
  function orden2(vec) {
    return vec.map((nb, i) => {
      const ya = new Set([i].concat(nb)), s = new Set();
      nb.forEach(j => vec[j].forEach(l => { if (!ya.has(l)) s.add(l); }));
      return Array.from(s).sort((p, q) => p - q);
    });
  }

  // Lo que pesa el propio barrio en su W²y: la diagonal de W², Σ_{j vecino de i} 1/(dᵢ dⱼ) (ir a j y volver).
  const propioW2 = (vec, i) => vec[i].reduce((a, j) => a + 1 / (vec[i].length * vec[j].length), 0);

  // El barrio de partida: el que más cambia al promediar, entre los que tienen al menos cuatro vecinos
  // (con menos, la media de «los demás» casi no se ve como una media).
  function focoDidactico(vec, y) {
    const w = rezago(vec, y);
    let mejor = -1, dif = -1;
    for (let i = 0; i < y.length; i++) {
      if (vec[i].length >= 4 && Math.abs(y[i] - w[i]) > dif) { dif = Math.abs(y[i] - w[i]); mejor = i; }
    }
    return mejor < 0 ? 0 : mejor;
  }

  // ---- La geometría, en unidades cuantizadas del mapa (`cap6-w`: geom, caja, q, nodos). ----

  // Réplica de `geomapaCajaQ` (plantilla): la caja del dato dentro del encuadre CUADRADO de R.
  function cajaQ(caja, q) {
    const rx = caja[2] - caja[0], ry = caja[3] - caja[1];
    const r = Math.max(rx, ry);
    const cx = caja[0] + rx / 2, cy = caja[1] + ry / 2;
    const qx = v => ((v - (cx - r / 2)) / r) * q;
    const qy = v => ((v - (cy - r / 2)) / r) * q;
    return { x0: qx(caja[0]), y0: qy(caja[1]), x1: qx(caja[2]), y1: qy(caja[3]) };
  }

  // Réplica de `geomapaAjuste`, con márgenes por lado y con la inversa (píxel → cuantizado), que la
  // plantilla no tiene porque no hace clic sobre sus mapas. Un solo factor de escala para los dos ejes.
  function ajuste(w, h, cq, margen) {
    const m = Object.assign({ l: 6, r: 6, t: 6, b: 6 }, margen);
    const dw = cq.x1 - cq.x0, dh = cq.y1 - cq.y0;
    const aw = w - m.l - m.r, ah = h - m.t - m.b;
    const s = Math.min(aw / dw, ah / dh);
    const ox = m.l + (aw - dw * s) / 2;
    const oy = m.t + (ah - dh * s) / 2;
    return {
      s, ox, oy,
      x: v => ox + (v - cq.x0) * s,
      y: v => oy + (cq.y1 - v) * s,
      qx: px => cq.x0 + (px - ox) / s,
      qy: py => cq.y1 - (py - oy) / s
    };
  }

  // ¿Está el punto (qx, qy) dentro del anillo plano [x0, y0, x1, y1, …]? Trazado de rayos.
  function dentro(anillo, qx, qy) {
    let ad = false;
    const n = anillo.length / 2;
    for (let i = 0, j = n - 1; i < n; j = i++) {
      const xi = anillo[2 * i], yi = anillo[2 * i + 1], xj = anillo[2 * j], yj = anillo[2 * j + 1];
      if ((yi > qy) !== (yj > qy) && qx < (xj - xi) * (qy - yi) / (yj - yi) + xi) ad = !ad;
    }
    return ad;
  }

  // El barrio bajo un punto en cuantizado, o -1.
  function barrioEn(geom, qx, qy) {
    for (let i = 0; i < geom.length; i++) {
      for (let p = 0; p < geom[i].length; p++) if (dentro(geom[i][p], qx, qy)) return i;
    }
    return -1;
  }

  // Etiquetas rectangulares (w × h) que parten de sus centros `pos`, sin pisarse entre sí ni pisar a los `fijos`
  // ({x, y, w, h}) y dentro de `lim`. Se colocan de una en una, en el orden dado: cada una se queda donde está si cabe, y si
  // no, en el sitio libre MÁS CERCANO (anillos de radio creciente, 18 direcciones). Determinista y sin azar. Una primera
  // versión las empujaba por parejas, y con un obstáculo fijo cerca de la esquina las amontonaba contra el borde; esta no.
  function separaEtiquetas(pos, w, h, fijos, lim) {
    const ocupado = fijos.map(f => ({ x: f.x, y: f.y, w: f.w, h: f.h }));
    const choca = (x, y) => ocupado.some(r => Math.abs(x - r.x) < (w + r.w) / 2 && Math.abs(y - r.y) < (h + r.h) / 2);
    const dentro = (x, y) => lim ? [Math.min(lim.x1 - w / 2, Math.max(lim.x0 + w / 2, x)), Math.min(lim.y1 - h / 2, Math.max(lim.y0 + h / 2, y))] : [x, y];
    return pos.map(q => {
      let sitio = null;
      for (let r = 0; r <= 40 && !sitio; r++) {
        for (let k = 0; k < (r === 0 ? 1 : 18) && !sitio; k++) {
          const ang = k * 2 * Math.PI / 18;
          const c = dentro(q[0] + r * 5 * Math.cos(ang), q[1] + r * 5 * Math.sin(ang));
          if (!choca(c[0], c[1])) sitio = c;
        }
      }
      sitio = sitio || dentro(q[0], q[1]);          // ni en 200 px hay hueco: se queda donde está, y se pisa
      ocupado.push({ x: sitio[0], y: sitio[1], w, h });
      return sitio;
    });
  }

  // El paso cuyo texto describe la capa k: el deslizador y el teclado cambian k sin pasar por `ir`, y sin esto la
  // leyenda del paso 1 («y: el dato») se quedaba encima de W³⁰y.
  const pasoDeK = k => k <= 0 ? 1 : k === 1 ? 2 : k === 2 ? 3 : 4;

  const Mat = { K_MAX, CASI_UNO, pasoDeK, VECINDADES, vecinosDe, rezago, capas, resumen, limite, orden2, propioW2, focoDidactico, media, sd, cov,
                cajaQ, ajuste, dentro, barrioEn, separaEtiquetas };

  /* ===================================================================
     2 · LA PIEZA. Lo que se dibuja y lo que se cuenta; el resto es de `Anim2D`.
     =================================================================== */
  const PALETA_VERDE = ['#e8f3ef', '#b8ddd0', '#7cc0aa', '#3f9c7f', '#1a7358', '#012820'];   // la `verde` de la plantilla
  const NARANJA = '#FF6600', TINTA = '#012820';
  const f2 = x => x.toFixed(2);
  // «19 %» y no «19» al final de un renglón y «%» al principio del otro: en lo que se VE, el espacio antes de % no se parte
  const f4 = x => x.toFixed(4);

  // El color de una capa: `opc.color(paleta, t)` es `geomapaColor` (con su filtro de daltonismo); sin él, la paleta de arriba.
  function colorLocal(t) {
    const x = Math.max(0, Math.min(1, t)) * (PALETA_VERDE.length - 1);
    const i = Math.min(PALETA_VERDE.length - 2, Math.floor(x)), f = x - i;
    const hex = h => [1, 3, 5].map(o => parseInt(h.slice(o, o + 2), 16));
    const a = hex(PALETA_VERDE[i]), b = hex(PALETA_VERDE[i + 1]);
    return 'rgb(' + [0, 1, 2].map(c => Math.round(a[c] + (b[c] - a[c]) * f)).join(',') + ')';
  }

  // Wᵏy con superíndice, para el texto.
  const capa = k => k === 0 ? 'y' : k === 1 ? 'Wy' : 'W<sup>' + k + '</sup>y';
  const capaTxt = k => k === 0 ? 'y' : k === 1 ? 'Wy' : 'W aplicada ' + k + ' veces a y';     // un lector leía «W circunflejo 70 y»

  function creaDef(datos, opc) {
    opc = opc || {};
    const y = datos.y, n = y.length, mapa = datos.mapa;
    if (!y || !mapa || !mapa.variantes) throw new Error('rezago2d: faltan y o el mapa del capítulo');
    if (mapa.codificacion !== 'absoluta' && !opc.geom) throw new Error('rezago2d: el mapa viene codificado en «' + mapa.codificacion + '»; falta opc.geom');
    const geom = opc.geom ? opc.geom(mapa) : mapa.geom;
    const colorDe = opc.color ? t => opc.color('verde', t) : colorLocal;
    const ymin = Math.min.apply(null, y), ymax = Math.max.apply(null, y);
    const sd0 = sd(y), m0 = media(y);
    const cq = cajaQ(mapa.caja, mapa.q);

    // Por vecindad: lo que sale de las aristas, una vez. Comprueba de paso que las aristas y los grados del mapa dicen lo mismo.
    const cache = {};
    const de = nombre => {
      if (cache[nombre]) return cache[nombre];
      const v = mapa.variantes[nombre];
      const vec = vecinosDe(v.aristas, n);
      if (v.grados && v.grados.some((g, i) => g !== vec[i].length)) throw new Error('rezago2d: los grados del mapa no son los de sus aristas (' + nombre + ')');
      const cs = capas(vec, y, K_MAX);
      const o2 = orden2(vec);
      const medO2 = o2.map(s => s.length ? s.reduce((a, j) => a + y[j], 0) / s.length : NaN);
      const conO2 = medO2.map((v, i) => i).filter(i => isFinite(medO2[i]));
      const corO2 = conO2.length > 2 ? resumen(conO2.map(i => y[i]), conO2.map(i => medO2[i])).cor : NaN;
      return (cache[nombre] = { vec, capas: cs, res: cs.map(c => resumen(y, c)), limite: limite(vec, y), orden2: o2, corOrden2: corO2 });
    };

    // Rangos fijos de los dos perfiles, para que no salten al cambiar de vecindad.
    const lims = VECINDADES.map(de).map(s => s.limite);
    const mediasTodas = [m0].concat(lims).concat(VECINDADES.map(de).reduce((a, s) => a.concat(s.res.map(r => r.media)), []));
    const rangoMedia = [Math.floor((Math.min.apply(null, mediasTodas) - 0.4) * 2) / 2, Math.ceil((Math.max.apply(null, mediasTodas) + 0.4) * 2) / 2];

    // ---- el ajuste del mapa al lienzo, con espacio abajo para la barra de color ----
    // La caja que se ve es la del estado (`vx0…vy1`), que se interpola: es la lupa. Con `lupa = 0` es el mapa entero.
    const MARGEN = { l: 8, r: 8, t: 8, b: 52 };
    let aj = null;
    const cajaDe = V => ({ x0: V.vx0, y0: V.vy0, x1: V.vx1, y1: V.vy1 });
    const ajusteDe = (w, h, caja) => {
      const k = caja || cq;
      if (aj && aj.w === w && aj.h === h && aj.x0 === k.x0 && aj.y0 === k.y0 && aj.x1 === k.x1 && aj.y1 === k.y1) return aj;
      return (aj = Object.assign({ w, h, x0: k.x0, y0: k.y0, x1: k.x1, y1: k.y1 }, ajuste(w, h, k, MARGEN)));
    };
    const barrioBajo = (x, yy, c, V) => {
      if (!c || !c.w) return -1;
      const a = ajusteDe(c.w, c.h, V && cajaDe(V));
      return barrioEn(geom, a.qx(x), a.qy(yy));
    };

    // La caja de la lupa: el barrio en foco y sus vecinos, con un margen (y nunca más pequeña que una vecindad típica).
    const cajasBarrio = geom.map(g => {
      let x0 = Infinity, y0 = Infinity, x1 = -Infinity, y1 = -Infinity;
      g.forEach(anillo => { for (let p = 0; p < anillo.length; p += 2) { x0 = Math.min(x0, anillo[p]); x1 = Math.max(x1, anillo[p]); y0 = Math.min(y0, anillo[p + 1]); y1 = Math.max(y1, anillo[p + 1]); } });
      return { x0, y0, x1, y1 };
    });
    const cajaFoco = (foco, vecindad) => {
      const idx = [foco].concat(de(vecindad).vec[foco]);
      const b = { x0: Infinity, y0: Infinity, x1: -Infinity, y1: -Infinity };
      idx.forEach(i => { const c = cajasBarrio[i]; b.x0 = Math.min(b.x0, c.x0); b.y0 = Math.min(b.y0, c.y0); b.x1 = Math.max(b.x1, c.x1); b.y1 = Math.max(b.y1, c.y1); });
      const mx = Math.max(180, 0.16 * (b.x1 - b.x0)), my = Math.max(180, 0.16 * (b.y1 - b.y0));
      return { x0: b.x0 - mx, y0: b.y0 - my, x1: b.x1 + mx, y1: b.y1 + my };
    };

    const valorVisible = (S, i, k) => {                // la capa en un k fraccionario (la transición entre dos capas)
      const k0 = Math.min(K_MAX, Math.max(0, Math.floor(k))), k1 = Math.min(K_MAX, k0 + 1), f = k - k0;
      return S.capas[k0][i] * (1 - f) + S.capas[k1][i] * f;
    };
    const t01 = v => (v - ymin) / (ymax - ymin);

    function cuenta(E) {                                // el cálculo de un barrio en la capa E.k, o null en k = 0
      if (E.k < 1) return null;
      const S = de(E.vecindad), nb = S.vec[E.foco], previa = S.capas[E.k - 1];
      return { nb, previa, valor: S.capas[E.k][E.foco], terminos: nb.map(j => f2(previa[j])).join(' + ') };
    }

    /* ---- el dibujo ---- */
    function trazaBarrio(ctx, a, i) {
      ctx.beginPath();
      geom[i].forEach(anillo => {
        for (let p = 0; p < anillo.length; p += 2) {
          if (p === 0) ctx.moveTo(a.x(anillo[p]), a.y(anillo[p + 1])); else ctx.lineTo(a.x(anillo[p]), a.y(anillo[p + 1]));
        }
        ctx.closePath();
      });
    }
    const centro = (a, i) => [a.x(mapa.nodos[2 * i]), a.y(mapa.nodos[2 * i + 1])];

    // Dónde van los números de los vecinos: junto a su barrio, sin pisarse entre sí ni pisar el valor del foco.
    const ETQ = { w: 40, h: 15 };          // lo que mide «56.71» a 11 px en Fira Code, con su halo
    const PASTILLA = { w: 58, h: 24 };     // la caja del valor del barrio en foco
    function posicionesEtiquetas(a, E, c) {
      const cu = cuenta(E);
      if (!cu) return [];
      const [fx, fy] = centro(a, E.foco);
      return separaEtiquetas(cu.nb.map(j => centro(a, j)), ETQ.w, ETQ.h, [{ x: fx, y: fy, w: PASTILLA.w, h: PASTILLA.h }],
                             { x0: 2, y0: 2, x1: c.w - 2, y1: c.h - MARGEN.b + 4 });
    }

    function halo(ctx, texto, x, yy) {
      ctx.lineWidth = 3.5; ctx.strokeStyle = 'rgba(255,255,255,.92)'; ctx.lineJoin = 'round';
      ctx.strokeText(texto, x, yy);
      ctx.fillStyle = TINTA;
      ctx.fillText(texto, x, yy);
    }

    function flecha(ctx, x0, y0, x1, y1, alfa, antes) {
      const dx = x1 - x0, dy = y1 - y0, L = Math.hypot(dx, dy);
      if (L < antes + 14) return;
      const ux = dx / L, uy = dy / L;
      const ex = x1 - ux * antes, ey = y1 - uy * antes;    // la punta se queda antes del valor del barrio en foco
      ctx.save();
      ctx.globalAlpha = alfa;
      ctx.strokeStyle = NARANJA; ctx.fillStyle = NARANJA; ctx.lineWidth = 1.6;
      ctx.beginPath(); ctx.moveTo(x0 + ux * 11, y0 + uy * 11); ctx.lineTo(ex, ey); ctx.stroke();
      ctx.beginPath();
      ctx.moveTo(ex + ux * 1, ey + uy * 1);
      ctx.lineTo(ex - ux * 7 - uy * 4, ey - uy * 7 + ux * 4);
      ctx.lineTo(ex - ux * 7 + uy * 4, ey - uy * 7 - ux * 4);
      ctx.closePath(); ctx.fill();
      ctx.restore();
    }

    function barraDeColor(ctx, c) {
      const x0 = 10, w = Math.min(240, c.w - 20), yy = c.h - 30, h = 9;
      ctx.font = "600 10.5px 'Montserrat', sans-serif"; ctx.fillStyle = '#334155'; ctx.textBaseline = 'top'; ctx.textAlign = 'left';
      ctx.fillText('CRIME · una sola escala, la de y', x0, yy - 16);
      for (let i = 0; i < w; i++) { ctx.fillStyle = colorDe(i / (w - 1)); ctx.fillRect(x0 + i, yy, 1.2, h); }
      ctx.strokeStyle = 'rgba(1,40,32,.35)'; ctx.lineWidth = 1; ctx.strokeRect(x0 - 0.5, yy - 0.5, w + 1, h + 1);
      ctx.font = "10.5px 'Fira Code', monospace"; ctx.fillStyle = '#334155'; ctx.textBaseline = 'top'; ctx.textAlign = 'left';
      ctx.fillText(f2(ymin), x0, yy + h + 3);
      ctx.textAlign = 'right';
      ctx.fillText(f2(ymax), x0 + w, yy + h + 3);
    }

    function dibuja(c, E, V) {
      const { ctx } = c;
      const a = ajusteDe(c.w, c.h, cajaDe(V));
      const S = de(E.vecindad);
      const cu = cuenta(E);
      // Cuánto de la lupa ha llegado: de 0 (mapa entero) a 1 (barrio y vecinos). Se mide con el ancho de la caja que se ve.
      const wFoco = E.lupa ? (() => { const b = cajaFoco(E.foco, E.vecindad); return b.x1 - b.x0; })() : 0;
      const lupa = E.lupa ? Math.max(0, Math.min(1, (cq.x1 - cq.x0 - (V.vx1 - V.vx0)) / Math.max(1, cq.x1 - cq.x0 - wFoco))) : 0;
      const alfa = Math.max(0, 1 - Math.abs(V.k - E.k) * 2) * lupa;      // la cuenta aparece cuando llegan las dos transiciones
      const implicados = new Set([E.foco].concat(S.vec[E.foco]));
      // todo lo del mapa se recorta a su zona: con la lupa los barrios se salen, y no deben pasar por detrás de la barra de color
      ctx.save();
      ctx.beginPath(); ctx.rect(0, 0, c.w, c.h - MARGEN.b + 4); ctx.clip();
      // 1. los barrios, coloreados por la capa visible (entre dos capas mientras dura la transición); con la lupa, el resto se atenúa
      for (let i = 0; i < n; i++) {
        trazaBarrio(ctx, a, i);
        ctx.globalAlpha = implicados.has(i) ? 1 : 1 - 0.6 * lupa;
        ctx.fillStyle = colorDe(t01(valorVisible(S, i, V.k)));
        ctx.fill();
        ctx.lineWidth = 0.8; ctx.strokeStyle = 'rgba(1,40,32,.28)'; ctx.stroke();
      }
      ctx.globalAlpha = 1;
      // 1b. con W² (k = 2), los vecinos de orden 2 a los que llega, en discontinua: así se ve que W² alcanza más que los
      //     vecinos, y el texto del paso puede decir «línea discontinua» en cualquier vista
      if (E.k === 2) {
        ctx.save(); ctx.setLineDash([4, 3]); ctx.lineWidth = 1.4; ctx.strokeStyle = 'rgba(1,40,32,.8)';
        S.orden2[E.foco].forEach(j => { trazaBarrio(ctx, a, j); ctx.stroke(); });
        ctx.restore();
      }
      // 2. los contornos: los de los vecinos (con la lupa), el del barrio bajo el puntero y el del foco. Van ANTES que
      //    las flechas y los números: dibujado después, el contorno naranja del foco tachaba las etiquetas de los
      //    vecinos que caían encima (barrios con ocho o más vecinos en una columna estrecha).
      if (cu && alfa > 0) {
        ctx.save(); ctx.globalAlpha = alfa; ctx.lineWidth = 2; ctx.strokeStyle = TINTA;
        cu.nb.forEach(j => { trazaBarrio(ctx, a, j); ctx.stroke(); });
        ctx.restore();
      } else if (E.k > 0 && !E.lupa) {
        // sin la lupa, solo se marcan los vecinos: una línea fina, sin números que se pisen
        ctx.save(); ctx.lineWidth = 1.4; ctx.strokeStyle = 'rgba(1,40,32,.75)';
        S.vec[E.foco].forEach(j => { trazaBarrio(ctx, a, j); ctx.stroke(); });
        ctx.restore();
      }
      if (E.hover >= 0 && E.hover !== E.foco) { trazaBarrio(ctx, a, E.hover); ctx.lineWidth = 2; ctx.strokeStyle = 'rgba(255,102,0,.7)'; ctx.stroke(); }
      trazaBarrio(ctx, a, E.foco); ctx.lineWidth = 3; ctx.strokeStyle = NARANJA; ctx.stroke();
      // 3. las flechas y los números de los vecinos, solo con la lupa (sin ella no hay sitio para las etiquetas)
      if (cu && alfa > 0) {
        const [fx, fy] = centro(a, E.foco);
        cu.nb.forEach(j => { const [x0, y0] = centro(a, j); flecha(ctx, x0, y0, fx, fy, alfa, 30); });
        ctx.save(); ctx.globalAlpha = alfa;
        ctx.font = "500 11px 'Fira Code', monospace"; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
        const pos = posicionesEtiquetas(a, E, c);
        cu.nb.forEach((j, q) => {
          const [x0, y0] = centro(a, j);
          if (Math.hypot(pos[q][0] - x0, pos[q][1] - y0) > 7) {        // la etiqueta se apartó de su barrio: una línea guía lo une
            ctx.strokeStyle = 'rgba(1,40,32,.55)'; ctx.lineWidth = 1;
            ctx.beginPath(); ctx.moveTo(x0, y0); ctx.lineTo(pos[q][0], pos[q][1]); ctx.stroke();
          }
          halo(ctx, f2(cu.previa[j]), pos[q][0], pos[q][1]);
        });
        ctx.restore();
      }
      // 4. el valor del barrio en foco, encima de todo
      const [fx, fy] = centro(a, E.foco);
      if (cu && alfa > 0) {
        const txt = f2(cu.valor);
        ctx.save(); ctx.globalAlpha = alfa;
        ctx.font = "500 12px 'Fira Code', monospace"; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
        ctx.fillStyle = '#fff'; ctx.strokeStyle = NARANJA; ctx.lineWidth = 2;
        ctx.beginPath(); ctx.rect(fx - PASTILLA.w / 2 + 4, fy - 10, PASTILLA.w - 8, 20); ctx.fill(); ctx.stroke();
        ctx.fillStyle = TINTA; ctx.fillText(txt, fx, fy + 0.5);
        ctx.restore();
      } else {
        ctx.font = "500 11px 'Fira Code', monospace"; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
        halo(ctx, f2(valorVisible(S, E.foco, V.k)), fx, fy);
      }
      ctx.restore();
      barraDeColor(ctx, c);
    }

    /* ---- los dos perfiles de debajo: la desviación y la media, para todos los k ---- */
    function perfil(c, E, V, o) {
      const { ctx } = c;
      const m = { l: 36, r: 8, t: 10, b: 20 };
      const W = c.w - m.l - m.r, H = c.h - m.t - m.b;
      const px = k => m.l + (k / K_MAX) * W;
      const py = v => m.t + (1 - (v - o.min) / (o.max - o.min)) * H;
      ctx.font = "10px 'Fira Code', monospace"; ctx.lineWidth = 1;
      // ejes y marcas
      ctx.strokeStyle = '#cbd5e1'; ctx.fillStyle = '#475569'; ctx.textBaseline = 'middle'; ctx.textAlign = 'right';
      [o.min, o.max].forEach(v => { ctx.beginPath(); ctx.moveTo(m.l, py(v) + 0.5); ctx.lineTo(m.l + W, py(v) + 0.5); ctx.stroke(); ctx.fillText(o.formato(v), m.l - 4, py(v)); });
      ctx.textAlign = 'center'; ctx.textBaseline = 'top';
      [0, 20, 40, 60].filter(k => k <= K_MAX).forEach(k => ctx.fillText(String(k), px(k), m.t + H + 4));
      // líneas de referencia
      (o.refs || []).forEach(r => {
        ctx.save(); ctx.setLineDash([4, 3]); ctx.strokeStyle = r.color; ctx.fillStyle = r.color; ctx.lineWidth = 1.3;
        ctx.beginPath(); ctx.moveTo(m.l, py(r.v)); ctx.lineTo(m.l + W, py(r.v)); ctx.stroke(); ctx.restore();
        ctx.save(); ctx.fillStyle = r.color; ctx.font = "600 10px 'Montserrat', sans-serif"; ctx.textAlign = 'right'; ctx.textBaseline = r.abajo ? 'top' : 'bottom';
        ctx.fillText(r.texto, m.l + W - 2, py(r.v) + (r.abajo ? 3 : -2)); ctx.restore();
      });
      // la serie
      ctx.strokeStyle = '#1a7358'; ctx.lineWidth = 1.8; ctx.beginPath();
      o.serie.forEach((v, k) => { if (k === 0) ctx.moveTo(px(k), py(v)); else ctx.lineTo(px(k), py(v)); });
      ctx.stroke();
      // el k actual, sobre la serie interpolada
      const k0 = Math.min(K_MAX, Math.floor(V.k)), k1 = Math.min(K_MAX, k0 + 1), f = V.k - k0;
      const vy = o.serie[k0] * (1 - f) + o.serie[k1] * f;
      ctx.strokeStyle = 'rgba(255,102,0,.55)'; ctx.setLineDash([2, 2]);
      ctx.beginPath(); ctx.moveTo(px(V.k), m.t); ctx.lineTo(px(V.k), m.t + H); ctx.stroke(); ctx.setLineDash([]);
      ctx.fillStyle = NARANJA; ctx.beginPath(); ctx.arc(px(V.k), py(vy), 4, 0, 2 * Math.PI); ctx.fill();
      ctx.strokeStyle = '#fff'; ctx.lineWidth = 1.5; ctx.stroke();
    }

    function panel(c, id, E, V) {
      const S = de(E.vecindad);
      if (id === 'sd') {
        perfil(c, E, V, { min: 0, max: sd0 * 1.05, formato: f2, serie: S.res.map(r => r.sd),
          refs: [{ v: 0.05 * sd0, texto: '5 % de la de y', color: '#b34700', abajo: false }] });
      } else {
        perfil(c, E, V, { min: rangoMedia[0], max: rangoMedia[1], formato: v => v.toFixed(1), serie: S.res.map(r => r.media),
          refs: [{ v: m0, texto: 'media de y', color: '#475569', abajo: true },
                 { v: S.limite, texto: 'media por grado', color: '#b34700', abajo: false }] });
      }
    }

    /* ---- los textos ---- */
    // Con un decimal (auditoría del 2026-10-02): redondeado a entero, la lectura decía «5 %» desde t = 63 (5.36 %) hasta
    // t = 68, y la prosa dice que hacen falta 66 aplicaciones para BAJAR del 5 %.
    const pct = (r) => (100 * r.sd / sd0).toFixed(1);
    const casiUno = E => de(E.vecindad).res[E.k].sd <= CASI_UNO * sd0;
    const lista = nb => nb.map(j => j + 1).join(', ');

    const pasos = [
      { corto: 'El dato', titulo: 'y: CRIME en los 49 barrios de Columbus',
        texto: () => 'Cada barrio, pintado con una escala de color <strong>fija</strong>, entre ' + f2(ymin) + ' y ' + f2(ymax) + '. ' +
                     'Todas las capas que siguen usan esta misma escala: si cada una se pintara contra su propio máximo, el aplanado no se vería.',
        estado: { k: 0, lupa: 0 }, pausa: 2.6 },
      { corto: 'Wy', titulo: 'Wy: cada barrio pasa a valer la media de sus vecinos',
        texto: E => {
          const cu = cuenta(E);
          if (!cu) return 'En t = 0 no se ha aplicado W: el barrio vale lo que valía. Sube t a 1 para ver su cuenta.';
          return 'El barrio <strong>' + (E.foco + 1) + '</strong> tiene ' + cu.nb.length + ' vecinos (' + lista(cu.nb) + '). Su valor en ' + capa(E.k) +
                 ' es la media de los que ellos tenían en ' + capa(E.k - 1) + ': (' + cu.terminos + ') / ' + cu.nb.length + ' ≈ <strong>' + f2(cu.valor) + '</strong>; el suyo propio, ' + f2(cu.previa[E.foco]) + ', no entra. ' +
                 'Haz clic en otro barrio, o usa ‹ ›, para ver su cuenta' + (E.lupa ? '.' : ' (con «Barrio y vecinos» el mapa se acerca y se ven los números).');
        },
        estado: { k: 1, lupa: 1 }, pausa: 4.8 },
      // La correlación de W²y con y SUBE respecto de la de Wy (0.68 → 0.78 con la reina), y sin decir por qué invitaba a
      // concluir que «a dos pasos se parecen más», o que W² es la vecindad de orden 2: justo el error que el módulo corrige.
      // Sube por la diagonal de W² (el propio barrio entra en su W²y); el orden 2 de verdad correlaciona 0.30.
      { corto: 'W otra vez', titulo: 'W otra vez: la media de las medias',
        texto: E => {
          const S = de(E.vecindad), c1 = S.res[1].cor, c2 = S.res[2].cor;
          return 'W<sup>2</sup>y promedia lo que ya estaba promediado. Llega a los vecinos de los vecinos (línea discontinua), pero también vuelve al propio barrio ' +
                 '—el ' + (E.foco + 1) + ' pesa un ' + Math.round(100 * propioW2(S.vec, E.foco)) + '\u00a0% en su W<sup>2</sup>y— y, casi siempre, a sus vecinos de siempre: ' +
                 '<strong>no es la contigüidad de orden 2</strong>, es apilar capas (módulo 11). Por eso su correlación con y ' + (c2 > c1 ? 'sube' : 'baja') +
                 ', de ' + f2(c1) + ' a ' + f2(c2) + (c2 > c1 ? ': lleva dentro un trozo del propio y' : '') + '. La media de los vecinos de orden 2 de verdad se parece ' +
                 (S.corOrden2 < c2 - 0.2 ? 'mucho menos' : 'menos') + ' a y (correlación ' + f2(S.corOrden2) + ').';
        },
        estado: { k: 2, lupa: 0 }, pausa: 4.2 },
      // El título y la primera frase dependen de k: el deslizador trae a este paso cualquier k ≥ 3, y con k = 3 decir
      // «casi un solo color» con la desviación en el 60 % de la de y era falso.
      { corto: 'Muchas veces',
        titulo: E => casiUno(E) ? 'Muchas veces: casi un solo color, y no es el de la media' : 'Más veces: el mapa se sigue aplanando',
        texto: E => {
          const S = de(E.vecindad), r = S.res[E.k];
          return 'Con t = ' + E.k + ' la desviación típica es el <strong>' + pct(r) + '\u00a0%</strong> de la de y' + (casiUno(E) ? ', y el mapa ya es casi de un solo color' : '') + '. ' +
                 'Si se sigue aplicando W, el mapa va hacia un solo valor, y ese valor <strong>no es la media de y</strong> (' + f2(m0) + ') sino la media ponderada por el grado: ' +
                 f2(S.limite) + ' con la vecindad de la ' + E.vecindad + '. Los barrios con más vecinos entran en más promedios. ' +
                 'La media de ' + capa(E.k) + ' va de ' + f2(m0) + ' hacia allí (ahora ' + f2(r.media) + ').';
        },
        estado: { k: K_MAX, lupa: 0 }, tween: { k: 9 }, pausa: 3.5 }
    ];

    const def = {
      id: 'rezago',
      // La descripción fija no afirma lo que depende del estado (flechas, la cuenta): eso lo dice la de debajo, que cambia.
      aria: 'Mapa de los ' + n + ' barrios de Columbus, cada uno pintado con el valor de CRIME tras aplicar la matriz de pesos W el número de veces ' +
            'que se elige. Hay un barrio en foco; la descripción de debajo dice qué se ve en cada momento. Dos gráficas debajo ' +
            'muestran la desviación típica y la media de cada capa.',
      ayuda: 'Clic en un barrio para ponerlo en foco · con el mapa enfocado, ← → cambian de barrio y ↑ ↓ cambian t',
      ayudaTeclado: 'Con el lienzo enfocado, las flechas izquierda y derecha cambian el barrio en foco y las flechas arriba y abajo cambian cuántas veces se aplica W. ' +
                    'Inicio lleva a t = 0 y Fin a t = ' + K_MAX + '. Los mandos de debajo hacen lo mismo.',
      pie: 'Columbus (Anselin, 1988): ' + n + ' barrios y la tasa de delitos CRIME, que son los del módulo 1. La vecindad es la del módulo 3, con W estandarizada por filas.',
      sinLienzo: 'Dice lo mismo que el texto del módulo 10: Wy es, en cada barrio, la media de sus vecinos. Aplicada una y otra vez, W aplana el mapa hacia un valor casi constante, ' +
                 'y ese valor no es la media de y sino la media ponderada por el grado de cada barrio.',
      paneles: [
        { id: 'sd', etiqueta: 'Desviación típica de W<sup>t</sup>y', aria: 'Desviación típica de cada capa, de t = 0 a ' + K_MAX + ': baja deprisa al principio y cada vez más despacio' },
        { id: 'media', etiqueta: 'Media de W<sup>t</sup>y', aria: 'Media de cada capa, de t = 0 a ' + K_MAX + ': sale de la media de y y se acerca a la media ponderada por el grado' }
      ],
      mandos: [
        { tipo: 'deslizador', id: 'k', etiqueta: 'Veces que se aplica W (t)', min: 0, max: K_MAX, paso: 1, salida: v => String(v),
          valorTexto: (v, E) => v + (v === 1 ? ' vez' : ' veces') + ': desviación típica ' + pct(de(E.vecindad).res[v]) + ' % de la de y' },
        { tipo: 'botones', id: 'vecindad', etiqueta: 'Vecindad', opciones: [['reina', 'Reina'], ['torre', 'Torre']] },
        { tipo: 'botones', id: 'lupa', etiqueta: 'Vista', opciones: [[0, 'Todo el mapa'], [1, 'Barrio y vecinos']] },
        { tipo: 'ciclo', id: 'foco', etiqueta: 'Barrio en foco', n, anterior: 'Barrio anterior', siguiente: 'Barrio siguiente', texto: i => 'barrio ' + (i + 1) }
      ],
      animables: { k: 1.1, vx0: 0.9, vy0: 0.9, vx1: 0.9, vy1: 0.9 },
      pasoImpresion: 4,
      pasos,
      inicial: () => ({ paso: 1, k: 0, vecindad: 'reina', foco: focoDidactico(de('reina').vec, y), hover: -1, lupa: 0,
                        vx0: cq.x0, vy0: cq.y0, vx1: cq.x1, vy1: cq.y1 }),
      normaliza: (p, E) => {
        const out = Object.assign({}, p);
        if ('k' in out) out.k = Math.min(K_MAX, Math.max(0, Math.round(out.k)));
        if ('k' in out && !('paso' in out)) out.paso = pasoDeK(out.k);          // el texto que se ve es el de la capa que se ve
        if ('foco' in out) out.foco = Math.min(n - 1, Math.max(0, Math.round(out.foco)));
        if ('hover' in out) out.hover = Math.min(n - 1, Math.max(-1, Math.round(out.hover)));
        if ('paso' in out) out.paso = Math.min(pasos.length, Math.max(1, Math.round(out.paso)));
        if ('vecindad' in out && VECINDADES.indexOf(out.vecindad) < 0) delete out.vecindad;
        if ('lupa' in out) out.lupa = out.lupa ? 1 : 0;
        // La caja que se ve sigue al foco y a la lupa: la calcula la pieza, no quien llama.
        if ('lupa' in out || 'foco' in out || 'vecindad' in out) {
          const sig = Object.assign({}, E, out);
          const caja = sig.lupa ? cajaFoco(sig.foco, sig.vecindad) : cq;
          out.vx0 = caja.x0; out.vy0 = caja.y0; out.vx1 = caja.x1; out.vy1 = caja.y1;
        }
        return out;
      },
      dibuja, panel,
      puntero: (ev, E, V, c) => {
        if (ev.tipo === 'sale') return { poner: { hover: -1 }, cursor: '' };
        const i = barrioBajo(ev.x, ev.y, c, V);
        if (ev.tipo === 'mueve') return { poner: { hover: i }, cursor: i >= 0 ? 'pointer' : '' };
        if (ev.tipo === 'abajo' && i >= 0) return { poner: { foco: i } };
        return null;
      },
      tecla: (ev, E) => {
        switch (ev.key) {
          case 'ArrowRight': return { foco: (E.foco + 1) % n };
          case 'ArrowLeft': return { foco: (E.foco + n - 1) % n };
          case 'ArrowUp': return { k: E.k + 1 };
          case 'ArrowDown': return { k: E.k - 1 };
          case 'Home': return { k: 0 };
          case 'End': return { k: K_MAX };
          default: return null;
        }
      },
      lectura: E => {
        const S = de(E.vecindad), r = S.res[E.k];
        return [
          ['t', String(E.k)],
          ['media', f4(r.media)],
          ['desviación típica', f4(r.sd) + ' <span class="a2d-r">(' + pct(r) + '\u00a0% de la de y)</span>'],
          ['correlación con y', f4(r.cor)],
          ['pendiente sobre y', f4(r.pendiente) + (E.k === 1 ? ' <span class="a2d-r">= I de Moran</span>' : '')]
        ];
      },
      alt: E => {
        const S = de(E.vecindad), r = S.res[E.k], cu = cuenta(E);
        return 'Capa ' + capaTxt(E.k) + ' con la vecindad ' + E.vecindad + ': media ' + f4(r.media) + ', desviación típica ' + f4(r.sd) + ' (' + pct(r) + ' por ciento de la de y). ' +
               'Barrio en foco: ' + (E.foco + 1) + ', con ' + S.vec[E.foco].length + ' vecinos (' + lista(S.vec[E.foco]) + '). ' +
               (cu ? 'Su valor es ' + f2(cu.valor) + ', la media de ' + cu.terminos.replace(/ \+ /g, ', ') + '.' : 'Su valor es ' + f2(y[E.foco]) + '.');
      },
      // Lo que dice la región viva cuando el estado cambia sin cambiar de paso: el barrio nuevo con su cuenta, la t nueva
      // con su desviación (el deslizador ya la dice con su `valorTexto`), la otra vecindad con a dónde va. Pasar el ratón
      // y la vista no se anuncian: el primero no es un cambio, y la vista ya la dice su botón pulsado.
      anuncio: (E, antes) => {
        const S = de(E.vecindad), cu = cuenta(E), r = S.res[E.k];
        if (E.foco !== antes.foco) {
          return 'Barrio ' + (E.foco + 1) + ': ' + (cu ? f2(cu.valor) + ', la media de sus ' + cu.nb.length + ' vecinos en ' + capaTxt(E.k - 1) : f2(y[E.foco])) + '.';
        }
        if (E.vecindad !== antes.vecindad) {
          return 'Vecindad ' + E.vecindad + ': desviación típica ' + pct(r) + ' % de la de y; el mapa va hacia ' + f2(S.limite) + '.';
        }
        if (E.k !== antes.k) return 't = ' + E.k + ': desviación típica ' + pct(r) + ' % de la de y.';
        return null;
      }
    };
    def.interno = { de, cuenta, casiUno, K_MAX, ajusteDe, barrioBajo, cajaFoco, cajaDe, cq, posicionesEtiquetas, ETQ, PASTILLA, MARGEN };     // para las pruebas
    return def;
  }

  function monta(cont, datos, opc) {
    opc = opc || {};
    if (!global.Anim2D) throw new Error('rezago2d: falta anim2d.js');
    return global.Anim2D.monta(cont, creaDef(datos, opc), opc);
  }

  const Rezago2D = { monta, creaDef, matematica: Mat };
  global.Rezago2D = Rezago2D;
  if (typeof module === 'object' && module.exports) module.exports = Rezago2D;
})(typeof window !== 'undefined' ? window : globalThis);
