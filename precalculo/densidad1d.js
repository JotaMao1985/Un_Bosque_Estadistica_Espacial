// =====================================================================
// densidad1d.js — la matemática de los simuladores del apéndice A
//
// Material de Estadística Espacial 2026-II (20929).
//
// QUÉ ES. Las funciones puras con que los simuladores del apéndice dibujan
// en vivo: histograma con ancho y origen, ASH, núcleo triangular, KDE con
// los cinco núcleos de `density()` y k vecinos. Sin DOM y sin Chart.js: se
// prueban en Node contra R (`prueba_densidad1d.py`), y el ensamblador las
// inyecta en línea en el documento.
//
// POR QUÉ HAY JAVASCRIPT QUE CALCULA. La regla de la casa es que toda cifra
// la calcula R. Las cifras de la PROSA salen siempre de
// `apendicea_datos.json`; lo que se calcula aquí es lo que el estudiante
// mueve con un deslizador continuo —una curva por cada ancho de banda—, que
// precalculado serían miles de curvas. Por eso cada función de este archivo
// tiene su gemela en `genera_apendicea.R` y la prueba exige que coincidan.
//
// LAS CONVENCIONES, que son las de R y no otras:
//   · intervalos [a, b) con la tolerancia de `hist()`: un dato que cae a
//     1e-7·h por debajo de un corte cuenta en la casilla de arriba;
//   · en `kde()` el ancho es la DESVIACIÓN TÍPICA del núcleo (`bw` de
//     `density()`), así que la caja llega a ±√3·bw y el Epanechnikov a ±√5·bw;
//   · una moda es una meseta más alta que lo que tiene a los dos lados
//     (fuera del dominio, 0), igual que `modas_secuencia()` en R.
// =====================================================================
(function (raiz) {
  'use strict';

  // Escala de soporte de cada núcleo cuando su desviación típica vale 1.
  var ESCALA = { gaussian: 1, rectangular: Math.sqrt(3), epanechnikov: Math.sqrt(5),
                 triangular: Math.sqrt(6), biweight: Math.sqrt(7) };

  var RAIZ_2PI = Math.sqrt(2 * Math.PI);

  // Los núcleos sobre el soporte [-1, 1] (el gaussiano, sin soporte).
  function nucleo(nombre) {
    switch (nombre) {
      case 'gaussian': return function (u) { return Math.exp(-0.5 * u * u) / RAIZ_2PI; };
      case 'rectangular': return function (u) { return Math.abs(u) <= 1 ? 0.5 : 0; };
      case 'epanechnikov': return function (u) { return Math.abs(u) <= 1 ? 0.75 * (1 - u * u) : 0; };
      case 'triangular': return function (u) { return Math.abs(u) <= 1 ? 1 - Math.abs(u) : 0; };
      case 'biweight': return function (u) {
        var v = 1 - u * u; return Math.abs(u) <= 1 ? (15 / 16) * v * v : 0; };
      default: throw new Error('núcleo desconocido: ' + nombre);
    }
  }

  function minimo(x) { var m = Infinity; for (var i = 0; i < x.length; i++) if (x[i] < m) m = x[i]; return m; }
  function maximo(x) { var m = -Infinity; for (var i = 0; i < x.length; i++) if (x[i] > m) m = x[i]; return m; }

  // La secuencia de R: seq(desde, hasta, by = paso).
  function secuencia(desde, hasta, paso) {
    var n = Math.floor((hasta - desde) / paso + 1e-10) + 1, s = new Array(n);
    for (var i = 0; i < n; i++) s[i] = desde + i * paso;
    return s;
  }

  function rejilla(desde, hasta, n) {
    var s = new Array(n), p = (hasta - desde) / (n - 1);
    for (var i = 0; i < n; i++) s[i] = desde + i * p;
    return s;
  }

  // Cuenta en [b_i, b_{i+1}), con el último cerrado y la tolerancia de hist().
  function cuenta(x, cortes) {
    var k = cortes.length - 1, c = new Array(k), fz = 1e-7 * (cortes[1] - cortes[0]);
    for (var i = 0; i < k; i++) c[i] = 0;
    for (var j = 0; j < x.length; j++) {
      var v = x[j];
      if (v < cortes[0] - fz || v > cortes[k] + fz) continue;
      var lo = 0, hi = k - 1;
      while (lo < hi) {                    // la última casilla con corte_i - fz <= v
        var mid = (lo + hi + 1) >> 1;
        if (cortes[mid] - fz <= v) lo = mid; else hi = mid - 1;
      }
      c[lo]++;
    }
    return c;
  }

  // findInterval() de R: cuántos cortes hay <= t (0 si está a la izquierda).
  function intervalo(cortes, t) {
    var lo = 0, hi = cortes.length;
    while (lo < hi) { var mid = (lo + hi) >> 1; if (cortes[mid] <= t) lo = mid + 1; else hi = mid; }
    return lo;
  }

  // Histograma de ancho h con el origen corrido una fracción `frac` de h.
  function histograma(x, h, frac) {
    var o = frac * h, a = Math.floor((minimo(x) - o) / h) * h + o;
    var k = Math.floor((maximo(x) - a) / h) + 1, cortes = new Array(k + 1);
    for (var i = 0; i <= k; i++) cortes[i] = a + h * i;
    var c = cuenta(x, cortes), d = new Array(k);
    for (var j = 0; j < k; j++) d[j] = c[j] / (x.length * h);
    return { cortes: cortes, conteos: c, densidad: d };
  }

  // El ASH: m histogramas de ancho h, desplazados h/m, sobre la malla
  // EXTENDIDA, y promediados en los MISMOS puntos g.
  function ash(x, h, m, g) {
    var n = x.length, d = h / m, mal = secuencia(minimo(x) - h, maximo(x) + h + d, h);
    var e = new Array(g.length);
    for (var t = 0; t < g.length; t++) e[t] = 0;
    for (var j = 0; j < m; j++) {
      var b = mal.map(function (v) { return v + j * d; });
      var cn = cuenta(x, b);
      for (var s = 0; s < g.length; s++) {
        var i = intervalo(b, g[s]);
        if (i >= 1 && i <= b.length - 1) e[s] += cn[Math.min(i, cn.length) - 1];
      }
    }
    for (var u = 0; u < g.length; u++) e[u] /= (m * n * h);
    return e;
  }

  // Núcleo triangular de SEMIANCHO h: el límite del ASH cuando m crece.
  function kdeTriangular(x, h, g) {
    return g.map(function (t) {
      var s = 0;
      for (var i = 0; i < x.length; i++) { var v = 1 - Math.abs((t - x[i]) / h); if (v > 0) s += v; }
      return s / (x.length * h);
    });
  }

  // KDE en la convención de density(): bw es la desviación típica del núcleo.
  function kde(x, g, bw, nombre) {
    var K = nucleo(nombre || 'gaussian'), a = ESCALA[nombre || 'gaussian'] * bw;
    return g.map(function (t) {
      var s = 0;
      for (var i = 0; i < x.length; i++) s += K((t - x[i]) / a);
      return s / (x.length * a);
    });
  }

  // KDE en la escala de SOPORTE: h es el semiancho del núcleo (la tabla 3.1
  // del texto guía y `KernelDensity` de sklearn). El gaussiano, con sd = h.
  function kdeSoporte(x, g, h, nombre) {
    var K = nucleo(nombre || 'gaussian');
    return g.map(function (t) {
      var s = 0;
      for (var i = 0; i < x.length; i++) s += K((t - x[i]) / h);
      return s / (x.length * h);
    });
  }

  // k vecinos: k / (2 n d_k(t)). El k-ésimo menor de |x - t|, por selección.
  function knn(x, g, k) {
    var n = x.length, d = new Float64Array(n);
    return g.map(function (t) {
      for (var i = 0; i < n; i++) d[i] = Math.abs(x[i] - t);
      var dk = seleccion(d, k - 1);
      return dk > 0 ? k / (2 * n * dk) : Infinity;
    });
  }

  // El k-ésimo menor (base 0) de un Float64Array, sin ordenarlo entero.
  function seleccion(a, k) {
    var v = Float64Array.from(a), lo = 0, hi = v.length - 1;
    while (lo < hi) {
      var p = v[(lo + hi) >> 1], i = lo, j = hi;
      while (i <= j) {
        while (v[i] < p) i++;
        while (v[j] > p) j--;
        if (i <= j) { var tmp = v[i]; v[i] = v[j]; v[j] = tmp; i++; j--; }
      }
      if (k <= j) hi = j; else if (k >= i) lo = i; else return v[k];
    }
    return v[k];
  }

  function modas(y) {
    var r = [];
    for (var i = 0; i < y.length; i++) if (i === 0 || y[i] !== y[i - 1]) r.push(y[i]);
    var c = 0;
    for (var j = 0; j < r.length; j++) {
      var izq = j > 0 ? r[j - 1] : 0, der = j < r.length - 1 ? r[j + 1] : 0;
      if (r[j] > izq && r[j] > der && r[j] > 0) c++;
    }
    return c;
  }

  function trapecio(x, y) {
    var s = 0;
    for (var i = 1; i < x.length; i++) s += (x[i] - x[i - 1]) * (y[i] + y[i - 1]) / 2;
    return s;
  }

  function distanciaMaxima(a, b) {
    var m = 0;
    for (var i = 0; i < a.length; i++) { var v = Math.abs(a[i] - b[i]); if (v > m) m = v; }
    return m;
  }

  var D1 = { ESCALA: ESCALA, secuencia: secuencia, rejilla: rejilla, histograma: histograma,
             ash: ash, kdeTriangular: kdeTriangular, kde: kde, kdeSoporte: kdeSoporte,
             knn: knn, modas: modas, trapecio: trapecio, distanciaMaxima: distanciaMaxima,
             minimo: minimo, maximo: maximo };
  if (typeof module !== 'undefined' && module.exports) module.exports = D1;
  else raiz.D1 = D1;
})(typeof globalThis !== "undefined" ? globalThis : this);
