// =====================================================================
// anim1d.js — los fotogramas de las tres animaciones del apéndice A
//
// Material de Estadística Espacial 2026-II (20929).
//
// QUÉ ES. Funciones PURAS que, dado un paso de una animación y un momento u
// entre 0 y 1, devuelven lo que hay que dibujar: barras, curvas, tallos,
// ventanas y las cifras de la lectura. Sin DOM y sin Chart.js: se prueban en
// Node (`prueba_anim1d.py`) contra las cifras que R escribió en
// `apendicea_datos.json`, y el ensamblador las inyecta en línea detrás de
// `densidad1d.js`, del que toman toda la matemática. Aquí solo hay
// coreografía: qué se ve en cada momento.
//
// LAS TRES (2026-10-03, propuestas en la revisión 2 y pedidas por Javier):
//   · origenes (módulo 3): el ASH del ejemplo a mano, un origen tras otro;
//   · desliza (módulo 5): una ventana que recorre el eje, primero caja y
//     luego campana, y la misma curva leída como suma de lomas;
//   · vecinos (módulo 7): la ventana del k-NN, que crece hasta el k-ésimo
//     dato, recorre el eje y se pierde por la cola.
//
// LAS CONVENCIONES son las de densidad1d.js: intervalos [a, b) con la
// tolerancia de hist(); en el módulo 5, h en la escala de SOPORTE (la caja
// de h = 1 va de x − 1 a x + 1, bordes incluidos) y, en el gaussiano, su
// desviación típica; en el k-NN, dentro de la ventana está todo dato a
// distancia ≤ d_k, y por eso con empates encierra más de k.
// =====================================================================
(function (raiz) {
  'use strict';
  var D1 = raiz.D1 || (typeof require === 'function' ? require('./densidad1d.js') : null);

  function acota(u) { return u < 0 ? 0 : u > 1 ? 1 : u; }
  // Arranque y frenada suaves: el movimiento no empieza ni para de golpe.
  function suave(u) { u = acota(u); return u * u * (3 - 2 * u); }
  function suma(v) { var s = 0; for (var i = 0; i < v.length; i++) s += v[i]; return s; }
  // Cuántos nodos de la rejilla quedan a la izquierda de t (inclusive): lo
  // que la curva lleva trazado cuando la ventana va por t.
  function hasta(g, t) {
    var lo = 0, hi = g.length;
    while (lo < hi) { var mid = (lo + hi) >> 1; if (g[mid] <= t + 1e-9) lo = mid + 1; else hi = mid; }
    return lo;
  }
  // El nodo de la rejilla más cercano a t. La ventana se coloca SIEMPRE en
  // un nodo: así la punta de su columna y la del trazo son el mismo número.
  // Entre nodos, la columna marcaba una altura que la curva no tenía (lo
  // vio la revisión independiente de las animaciones, 2026-10-03).
  function nodo(g, desde, paso, t) {
    var i = Math.max(0, Math.min(g.length - 1, Math.round((t - desde) / paso)));
    return { i: i, x: g[i] };
  }

  // Los picos YA FORMADOS de una curva a medio trazar: mesetas más altas que
  // lo que tienen a los dos lados, sin contar la última, cuyo lado derecho
  // todavía no se ha dibujado (contarla pondría un pico en la punta del
  // trazo). Con la curva entera, si acaba bajando, coincide con D1.modas.
  function picos(y) {
    var r = [];
    for (var i = 0; i < y.length; i++) if (i === 0 || y[i] !== y[i - 1]) r.push(y[i]);
    var c = 0;
    for (var j = 0; j < r.length - 1; j++) {
      var izq = j > 0 ? r[j - 1] : 0;
      if (r[j] > izq && r[j] > r[j + 1] && r[j] > 0) c++;
    }
    return c;
  }

  // ------------------------------------------------------------------
  // 1 · ORÍGENES (módulo 3). cfg = { x, h, m, desde, hasta, paso, escalera }
  //   paso 0 · cada dato cae en su casilla del histograma de base;
  //   paso 1 · el origen se corre un ancho entero, y quedan sellados los m
  //            histogramas de la tabla (corridos 0, δ, 2δ…);
  //   paso 2 · un cursor recorre el eje y promedia los m EN EL MISMO x;
  //   paso 3 · m crece por la escalera y el promedio se acerca al triangular.
  // ------------------------------------------------------------------
  function origenes(cfg) {
    var x = cfg.x, n = x.length, h = cfg.h, m = cfg.m, delta = h / m;
    var g = D1.secuencia(cfg.desde, cfg.hasta, cfg.paso);
    var tri = D1.kdeTriangular(x, h, g);

    // Un histograma de ancho h sobre la malla extendida, corrido o.
    function histo(datos, o) {
      var k = Math.round((cfg.hasta - cfg.desde) / h), c = new Array(k + 1);
      for (var i = 0; i <= k; i++) c[i] = cfg.desde + o + h * i;
      var cn = D1.cuenta(datos, c);
      return { cortes: c, conteos: cn, alturas: cn.map(function (v) { return v / (n * h); }) };
    }
    // La altura de un histograma en t: la de la casilla [c_i, c_i+1) que lo
    // contiene, y 0 fuera de la malla. Es la lectura de ash() en R.
    function alturaEn(hi, t) {
      var i = D1.intervalo(hi.cortes, t);
      return (i >= 1 && i <= hi.cortes.length - 1) ? hi.alturas[i - 1] : 0;
    }

    var base = histo(x, 0), sellos = [];
    for (var j = 0; j < m; j++) sellos.push(histo(x, j * delta));
    var ash = D1.ash(x, h, m, g);
    var porM = {};
    function deM(mm) {
      if (!porM[mm]) {
        var hs = [];
        for (var i = 0; i < mm; i++) hs.push(histo(x, i * h / mm));
        var a = D1.ash(x, h, mm, g);
        porM[mm] = { histos: hs, ash: a, distancia: D1.distanciaMaxima(a, tri) };
      }
      return porM[mm];
    }

    function fotograma(paso, u) {
      u = acota(u);
      if (paso === 0) {
        // Los datos caen en el orden de la muestra, uno por cada 1/n del paso.
        var t = u * n, caidos = Math.min(n, Math.floor(t));
        var parcial = histo(x.slice(0, caidos), 0);
        var cae = null;
        if (caidos < n) {
          var i = D1.intervalo(base.cortes, x[caidos]) - 1;
          cae = { x: x[caidos], destino: (parcial.conteos[i] + 1) / (n * h), avance: suave(t - caidos) };
        }
        return { paso: 0, barras: parcial, caidos: caidos, cae: cae };
      }
      if (paso === 1) {
        var o = u * h, sellados = [];
        for (var s = 0; s < m; s++) if (s * delta <= o + 1e-9) sellados.push(s);
        return { paso: 1, origen: o, barras: histo(x, o), sellados: sellados };
      }
      if (paso === 2) {
        var nd = nodo(g, cfg.desde, cfg.paso, cfg.desde + u * (cfg.hasta - cfg.desde)), xc = nd.x;
        var alt = sellos.map(function (hi) { return alturaEn(hi, xc); });
        var k = nd.i + 1;
        return { paso: 2, cursor: { x: xc, alturas: alt, media: suma(alt) / m },
                 ash: ash.slice(0, k), cuantos: k };
      }
      var L = cfg.escalera.length, iM = Math.min(L - 1, Math.floor(u * L)), mm = cfg.escalera[iM];
      var d = deM(mm);
      return { paso: 3, m: mm, histos: d.histos, ash: d.ash, distancia: d.distancia };
    }
    return { g: g, tri: tri, base: base, sellos: sellos, delta: delta, alturaEn: alturaEn,
             fotograma: fotograma };
  }

  // ------------------------------------------------------------------
  // 2 · LA VENTANA QUE SE DESLIZA (módulo 5). cfg = { x, h, x0, desde, hasta, paso }
  //   paso 0 · una caja de semiancho h recorre el eje;
  //   paso 1 · en x0, la caja se vuelve campana (s va de 0 a 1);
  //   paso 2 · la campana recorre el eje;
  //   paso 3 · la misma curva, como suma de una loma por dato.
  // El aporte de un dato x_i cuando la ventana está en x es K((x_i − x)/h)/(nh),
  // y la loma del dato x_i vale en x K((x − x_i)/h)/(nh): son el mismo número,
  // porque K es simétrico. Eso es lo que el paso 3 deja ver.
  // ------------------------------------------------------------------
  function desliza(cfg) {
    var x = cfg.x, n = x.length, h = cfg.h;
    var g = D1.secuencia(cfg.desde, cfg.hasta, cfg.paso);
    var caja = D1.nucleo('rectangular'), campana = D1.nucleo('gaussian');
    // El peso de un dato a distancia t − c, con la caja convertida en campana
    // en la proporción s. Sin dividir: es el K(u) del cálculo a mano.
    function peso(s, t, c) { var v = (t - c) / h; return (1 - s) * caja(v) + s * campana(v); }
    function aporte(s, t, c) { return peso(s, t, c) / (n * h); }
    var curvaCaja = D1.kdeSoporte(x, g, h, 'rectangular');
    var curvaCampana = D1.kdeSoporte(x, g, h, 'gaussian');
    var lomas = x.map(function (xi) { return g.map(function (t) { return aporte(1, t, xi); }); });
    // La caja del paso 0 se DETIENE un momento en x0, el punto de la tabla:
    // sin la parada ni el reproductor ni el deslizador caían en x0 (saltaban
    // de 3.994 a 4.005) y el 0.3 que cita la leyenda no se veía nunca.
    var PARADA = 0.05, u0 = (cfg.x0 - cfg.desde) / (cfg.hasta - cfg.desde);
    function recorrido(u, conParada) {
      if (!conParada) return cfg.desde + u * (cfg.hasta - cfg.desde);
      if (u < u0 - PARADA) return cfg.desde + u / (u0 - PARADA) * (cfg.x0 - cfg.desde);
      if (u <= u0 + PARADA) return cfg.x0;
      return cfg.x0 + (u - u0 - PARADA) / (1 - u0 - PARADA) * (cfg.hasta - cfg.x0);
    }

    function fotograma(paso, u) {
      u = acota(u);
      var s = paso === 0 ? 0 : paso === 1 ? suave(u) : 1;
      var nd = nodo(g, cfg.desde, cfg.paso, paso === 1 ? cfg.x0 : recorrido(u, paso === 0)), xc = nd.x;
      var tallos = x.map(function (xi) { return aporte(s, xi, xc); });
      var r = { paso: paso, s: s, x: xc,
                ventana: g.map(function (t) { return aporte(s, t, xc); }),
                pesos: x.map(function (xi) { return peso(s, xi, xc); }),
                tallos: tallos, f: suma(tallos), traza: null, cuantos: 0, enLomas: null };
      if (paso === 0) { r.cuantos = nd.i + 1; r.traza = curvaCaja.slice(0, r.cuantos); }
      if (paso === 2) { r.cuantos = nd.i + 1; r.traza = curvaCampana.slice(0, r.cuantos); }
      if (paso === 3) {
        r.cuantos = g.length; r.traza = curvaCampana;
        // La altura de cada loma en x: la misma que el tallo de su dato.
        r.enLomas = x.map(function (xi) { return aporte(1, xc, xi); });
      }
      return r;
    }
    return { g: g, curvaCaja: curvaCaja, curvaCampana: curvaCampana, lomas: lomas, u0: u0,
             parada: PARADA, fotograma: fotograma };
  }

  // ------------------------------------------------------------------
  // 3 · LA VENTANA DEL k-NN (módulo 7). cfg = { x, k, x0, desde, hasta, lejos, paso }
  //   paso 0 · en x0 la ventana crece hasta encerrar el k-ésimo dato
  //            (llega en el 80 % del paso y se queda);
  //   paso 1 · la ventana recorre el eje de `desde` a `hasta`;
  //   paso 2 · sigue por la cola hasta `lejos`, y el área no para de crecer.
  // La ventana se dibuja como el rectángulo de base 2 d_k y altura
  // k / (2n d_k): su área es siempre k/n, y por eso se aplasta al ensancharse.
  // ------------------------------------------------------------------
  function vecinos(cfg) {
    var x = cfg.x, n = x.length, k = cfg.k;
    var g = D1.secuencia(cfg.desde, cfg.lejos, cfg.paso);
    var curva = D1.knn(x, g, k);
    var LLEGA = 0.8;

    function dk(t) {
      var d = x.map(function (v) { return Math.abs(v - t); }).sort(function (a, b) { return a - b; });
      return d[k - 1];
    }
    function dentro(t, r) {
      var r2 = r + 1e-9 * Math.max(1, r), ids = [];
      for (var i = 0; i < n; i++) if (Math.abs(x[i] - t) <= r2) ids.push(i);
      return ids;
    }
    function ventana(t) {
      var d = dk(t), ids = dentro(t, d);
      return { x: t, dk: d, dentro: ids, alto: d > 0 ? k / (2 * n * d) : Infinity,
               globo: d > 0 ? ids.length / (2 * n * d) : Infinity };
    }

    function fotograma(paso, u) {
      u = acota(u);
      if (paso === 0) {
        var d = dk(cfg.x0), listo = u >= LLEGA, r = listo ? d : d * suave(u / LLEGA);
        return { paso: 0, x: cfg.x0, radio: r, dentro: dentro(cfg.x0, r), listo: listo,
                 ventana: listo ? ventana(cfg.x0) : null };
      }
      var nd = nodo(g, cfg.desde, cfg.paso, paso === 1 ? cfg.desde + u * (cfg.hasta - cfg.desde)
                                                      : cfg.hasta + u * (cfg.lejos - cfg.hasta));
      var xc = nd.x, c = nd.i + 1, tr = curva.slice(0, c);
      return { paso: paso, x: xc, ventana: ventana(xc), traza: tr, cuantos: c,
               area: D1.trapecio(g.slice(0, c), tr), picos: picos(tr) };
    }
    return { g: g, curva: curva, dk: dk, ventana: ventana, fotograma: fotograma };
  }

  var A1D = { origenes: origenes, desliza: desliza, vecinos: vecinos, suave: suave, picos: picos };
  if (typeof module !== 'undefined' && module.exports) module.exports = A1D;
  else raiz.A1D = A1D;
})(typeof globalThis !== "undefined" ? globalThis : this);
