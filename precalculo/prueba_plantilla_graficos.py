#!/usr/bin/env python3
"""
prueba_plantilla_graficos.py — las reglas compartidas de las gráficas, por dentro

Material de Estadística Espacial 2026-II (20929). Ronda R2, tarea T2.1 (2026-11-17).

POR QUÉ EXISTE.

La revisión de gráficas del capítulo 1 (`diagnostico_cap1/graficas.md`) encontró que
varios defectos no eran de un simulador sino de la plantilla, y que por eso se
repetían en todos los documentos:

  R-D  `crearGraficoLinea` fundía las opciones con un `Object.assign` superficial, y
       quien pasaba `scales` perdía la letra, `maxRotation: 0`, `maxTicksLimit` y la
       rejilla de la casa.
  R-E  la leyenda iba arriba en una caja de alto fijo: a 375 px el trazado se quedaba
       en 73–150 px.
  R-F  el suelo de la letra de los rótulos del lienzo estaba en píxeles de
       dispositivo: 4.5 px de pantalla con densidad 2.
  R-C  la paleta divergente no tenía centro, los puntos no tenían filo ni un radio
       que bajara con su número, y la clase más clara de un coropleto se perdía
       contra el fondo.
  R-B  la tabla ordenable escribía las cifras con `toLocaleString('es-CO')`.

Ninguna se ve en el arnés, que lee texto y cifras: un gráfico con la fuente del
sistema y los rótulos girados pasa todos los auditores. Esto ejecuta el JavaScript
de la plantilla —el de verdad, extraído por anclas, no una copia— en Node, con un
`Chart` y un lienzo de mentira que apuntan lo que se les pide, y comprueba cada regla.

Y SABE FALLAR. Una prueba que nunca se ha visto en rojo no prueba nada: a la
plantilla se le inyecta, uno por uno, el defecto que cada regla arregló —y los que
dejarían la regla a medias—, y cada inyección tiene que poner la prueba en rojo.

Uso:  python3 precalculo/prueba_plantilla_graficos.py
      (desde la carpeta `Estadistica espacial/`). Devuelve 1 si algo falla.
"""
from __future__ import annotations

import json
import pathlib
import re
import subprocess
import sys
import tempfile

RAIZ = pathlib.Path(__file__).resolve().parent.parent
PLANTILLA = RAIZ / "plantilla" / "plantilla-capitulo.html"

# Las dos regiones de JavaScript que se ejecutan, con sus anclas. Cada una tiene que
# aparecer exactamente una vez: un ancla que casa dos veces ejecuta otra cosa.
REGIONES = [
    ("    // Paleta y defaults de la casa para gráficos de líneas.\n",
     "    // Generador congruencial mulberry32", "los gráficos"),
    ("    const GEOMAPAS = {};\n",
     "    GEOMAPAS['demo-mapa'] = ", "el motor de los mapas"),
    ("    const TABLAS_RANKING = {};\n",
     "    function iniciarTablasRanking() {", "la tabla ordenable"),
]


def region(texto: str, abre: str, cierra: str, que: str) -> str:
    if texto.count(abre) != 1:
        sys.exit(f"PARADO: el ancla de apertura de {que} aparece {texto.count(abre)} veces")
    i = texto.index(abre)
    j = texto.find(cierra, i)
    if j < 0:
        sys.exit(f"PARADO: no está el ancla de cierre de {que}")
    return texto[i:j]


# ---------------------------------------------------------------------------------
# El banco de pruebas, en JavaScript. `__PLANTILLA__` se sustituye por las regiones.
# Devuelve por la salida estándar la lista de comprobaciones que NO se cumplen.
# ---------------------------------------------------------------------------------
BANCO = r"""
'use strict';
const fallos = [];
const pide = (cond, que) => { if (!cond) fallos.push(que); };
const cerca = (a, b) => Math.abs(a - b) < 1e-9;
// Lee `a.b.c` sin reventar si falta un eslabón: un defecto inyectado tiene que
// dar un valor malo y una frase que lo nombre, no un TypeError.
const lee = (o, ruta) => ruta.split('.').reduce((x, k) => (x === null || x === undefined) ? undefined : x[k], o);
// Cada sección corre aparte: si una se cae, se dice, y las demás siguen.
const seccion = (nombre, f) => { try { f(); } catch (e) { fallos.push('CAÍDA en la sección ' + nombre + ': ' + String(e && e.message).slice(0, 140)); } };

// ---- un navegador de mentira: lo justo que la plantilla toca ----
let ESTRECHO = false, DPR = 2;
const window = { get devicePixelRatio() { return DPR; },
                 matchMedia: q => ({ matches: ESTRECHO, media: q }),
                 // la caja de un gráfico: 12 px de relleno y 1 de borde, como `.grafico-wrapper`
                 getComputedStyle: el => ({ boxSizing: el.cajaContenido ? 'content-box' : 'border-box',
                                            paddingTop: '12px', paddingBottom: '12px',
                                            borderTopWidth: '1px', borderBottomWidth: '1px' }) };
// Los nodos que la plantilla crea apuntan en ESCRITO todo el HTML que reciben.
const ESCRITO = [];
const nodoFalso = () => ({ set innerHTML(v) { ESCRITO.push(String(v)); }, textContent: '', className: '', partes: [],
                           querySelectorAll: () => [], querySelector: () => null, addEventListener() {},
                           setAttribute() {}, appendChild() {}, append(...x) { this.partes.push(...x); }, focus() {},
                           classList: { add() {}, remove() {}, toggle() {} } });
const document = { createElement: nodoFalso, getElementById: () => null };
const mainContent = { lista: [], querySelectorAll() { return this.lista; } };
class ResizeObserver { observe() {} disconnect() {} }
const PLUGINS = [];
class Escala { getLabelForValue(v) { return String(v); } }
class Chart {
  constructor(canvas, cfg) { this.canvas = canvas; this.cfg = cfg; }
  static register(p) { PLUGINS.push(p); }
}
Chart.defaults = { font: { family: 'la de Chart.js', size: 12 }, scale: { ticks: {} },
                   scales: { linear: { ticks: { callback: v => String(v) } },
                             logarithmic: { ticks: { callback: v => String(v) } },
                             radialLinear: { ticks: { callback: v => String(v) } } },
                   plugins: { tooltip: {},
                              // las entradas por defecto de Chart.js: una por serie
                              legend: { labels: { generateLabels: ch => ch.config.data.datasets.map((s, i) => (
                                { text: s.label, datasetIndex: i, hidden: false, fillStyle: '#036', strokeStyle: '#036', lineWidth: 1 })) } } } };
Chart.overrides = {};
Chart.helpers = { toFont: f => { const tam = (f && f.size) || 12; return { size: tam, lineHeight: tam * 1.2, string: tam + 'px X' }; } };
// La composición de Chart.js, de mentira: vuelve a preguntarle a cada eje cuánto ocupa.
Chart.layouts = { update(g) { g.reajustes = (g.reajustes || 0) + 1; Object.values(g.scales).forEach(e => pasoEje(e, e.anunciado !== undefined ? e.anunciado : (e.$h ? e.width : e.height))); } };
Chart.LinearScale = class extends Escala {};
Chart.LogarithmicScale = class extends Escala {};
Chart.RadialLinearScale = class extends Escala {};
class Path2D { moveTo() {} lineTo() {} closePath() {} }

// Un contexto 2D que apunta lo que se le pide, en orden.
function lienzoFalso(ancho, alto) {
  const log = [];
  const ctx = {
    canvas: { width: ancho, height: alto }, log,
    font: '', fillStyle: '', strokeStyle: '', lineWidth: 1,
    save() {}, restore() {}, beginPath() {}, closePath() {}, moveTo() {}, lineTo() {},
    arc(x, y, r) { log.push(['arc', r]); },
    fill(p) { log.push(['fill', ctx.fillStyle]); },
    stroke(p) { log.push(['stroke', ctx.strokeStyle, ctx.lineWidth]); },
    strokeRect() {}, fillRect() { log.push(['fillRect', ctx.fillStyle]); },
    // una letra de ancho 0.6 del cuerpo: «14.51» a 22 px mide 66
    measureText(t) { return { width: String(t).length * 0.6 * parseFloat(/(\d+(?:\.\d+)?)px/.exec(ctx.font)[1]) }; },
    strokeText(t) { log.push(['halo', t, ctx.font]); },
    fillText(t) { log.push(['texto', t, ctx.font]); },
    setTransform() {}, clearRect() {}, createPattern() { return 'rayado'; }
  };
  return ctx;
}
const ultimoDe = a => a[a.length - 1];
const cuerpo = fuente => parseFloat(/(\d+(?:\.\d+)?)px/.exec(fuente)[1]);
// Un <canvas> de mentira que `pintarGeomapa` puede medir y dimensionar.
const lienzoMapa = anchoCSS => {
  const ctx = lienzoFalso(0, 0);
  let W = 0, H = 0;
  const cv = { style: {}, clientWidth: anchoCSS, getContext: () => ctx, setAttribute() {},
               getBoundingClientRect: () => ({ width: anchoCSS }),
               get width() { return W; }, set width(v) { W = v; }, get height() { return H; }, set height(v) { H = v; } };
  ctx.canvas = cv;
  return { cv, ctx };
};
const identidad = { s: 1, ox: 0, oy: 0, x: v => v, y: v => v };

__PLANTILLA__

// =========================== R-D · la fusión profunda ===========================
seccion('R-D', () => {
  const escriptable = ctx => 9;
  const mias = { scales: { y: { title: { display: true, text: 'casos' } },
                           y2: { position: 'right', min: 0, max: 1, grid: { display: false } },
                           xArriba: { position: 'top' }, x2: { min: 0 } },
                 plugins: { legend: { labels: { boxWidth: escriptable } } },
                 marcas: undefined };
  const copia = JSON.stringify(mias.scales);
  const g = crearGraficoLinea(null, [], [{ borderDash: [2, 3] }], mias);
  const o = g.cfg.options, x = lee(o, 'scales.x'), y = lee(o, 'scales.y') || {};
  pide(x && x.ticks && x.ticks.maxRotation === 0, 'R-D: quien pasa scales.y pierde `maxRotation: 0` del eje x');
  pide(x && x.ticks && x.ticks.maxTicksLimit === 12, 'R-D: quien pasa scales.y pierde `maxTicksLimit` del eje x');
  pide(x && x.ticks && x.ticks.font && x.ticks.font.family === 'Montserrat', 'R-D: el eje x pierde Montserrat');
  pide(x && x.grid && x.grid.display === false, 'R-D: el eje x pierde la rejilla apagada');
  pide(lee(y, 'ticks.font.family') === 'Fira Code', 'R-D: quien titula el eje y pierde su Fira Code');
  pide(y.grid && /148, 163, 184/.test(y.grid.color || ''), 'R-D: quien titula el eje y pierde la rejilla de la casa');
  pide(y.title && y.title.text === 'casos', 'R-D: el título que pasa el simulador no llega');
  pide(lee(o, 'scales.y2.ticks.font.family') === 'Fira Code', 'R-D: un segundo eje vertical no hereda la letra de la casa');
  pide(lee(o, 'scales.y2.grid.display') === false && lee(o, 'scales.y2.max') === 1,
       'R-D: lo que el simulador fija en su segundo eje se pierde');
  pide(lee(o, 'scales.xArriba.ticks.font.family') === 'Montserrat', 'R-D: un eje horizontal propio no hereda Montserrat');
  // un eje propio que no dice su lado: manda la primera letra de su nombre
  pide(lee(o, 'scales.x2.ticks.font.family') === 'Montserrat', 'R-D: un eje `x2` sin lado declarado se toma por vertical');
  pide(lee(o, 'plugins.legend.labels.boxWidth') === escriptable, 'R-D: una opción que es función no sustituye a la de la casa');
  pide(lee(o, 'plugins.legend.labels.font.family') === 'Montserrat', 'R-D: quien toca la leyenda pierde su letra');
  pide(lee(o, 'plugins.tooltip.backgroundColor') === '#012820', 'R-D: quien toca `plugins` pierde la ventana emergente de la casa');
  pide(lee(o, 'interaction.mode') === 'index', 'R-D: se pierde `interaction` de la casa');
  pide(!('marcas' in o), 'R-D: una clave `undefined` no es no haber dicho nada');
  pide(JSON.stringify(mias.scales) === copia, 'R-D: la fusión modifica las opciones del simulador');
  // dos gráficos seguidos no comparten objetos: lo que toque uno no lo ve el otro
  const g2 = crearGraficoLinea(null, [], [], {});
  pide(lee(g2, 'cfg.options.scales.y.title') === undefined, 'R-D: las opciones de un gráfico se cuelan en el siguiente');
  pide(lee(g2, 'cfg.options.scales.x') !== x && lee(g2, 'cfg.options.scales.x.ticks') !== lee(x, 'ticks'),
       'R-D: dos gráficos comparten el mismo objeto de opciones');
  // lo que el simulador dice, manda: un arreglo y un valor sustituyen enteros
  const g3 = crearGraficoLinea(null, [], [], { scales: { x: { ticks: { maxRotation: 50 }, grid: { display: true } } },
                                               plugins: { legend: { display: false } } });
  pide(lee(g3, 'cfg.options.scales.x.ticks.maxRotation') === 50 && lee(g3, 'cfg.options.scales.x.grid.display') === true,
       'R-D: el simulador no puede sobrescribir a propósito lo de la casa');
  pide(lee(g3, 'cfg.options.plugins.legend.display') === false, 'R-D: `display: false` no llega');
  pide(Array.isArray(fusionProfunda({ a: [1, 2, 3, 4] }, { a: [9] }).a) &&
       fusionProfunda({ a: [1, 2, 3, 4] }, { a: [9] }).a.length === 1, 'R-D: un arreglo se funde en vez de sustituir');
});

// =========================== R-E · la leyenda, abajo ===========================
// Un gráfico de mentira que hace lo que Chart.js hace en cada `update()`, en su
// orden: el plugin de la leyenda le da a la caja de la leyenda sus opciones y su
// posición, cada eje recibe las suyas, avisan los plugins (`beforeUpdate`), los
// ejes deciden su giro, y avisan otra vez (`afterLayout`). El lienzo mide 236 px.
const PLUGIN_RE = () => PLUGINS.find(p => p.id === 'leyendaEstrecha');
const cajaFalsa = (altoEnLinea) => { const c = new Set(), v = {}; return { variables: v,
  classList: { add: x => c.add(x), remove: x => c.delete(x), has: x => c.has(x) },
  style: { height: altoEnLinea === undefined ? '260px' : altoEnLinea, setProperty: (k, x) => { v[k] = x; }, removeProperty: k => { delete v[k]; } } }; };
function graficoFalso(op, series, altoEnLinea) {
  const g = {
    config: { options: op, type: 'line', data: { datasets: series || [{ label: 'una' }, { label: 'otra' }] } },
    // las opciones «resueltas»: las del simulador sobre los valores por defecto de Chart.js
    get options() {
      const o = this.config.options, p = o.plugins || {}, l = (p.legend && typeof p.legend === 'object') ? p.legend : {};
      const et = Object.assign({ boxWidth: 40, padding: 10, generateLabels: Chart.defaults.plugins.legend.labels.generateLabels }, l.labels);
      return { maintainAspectRatio: o.maintainAspectRatio === undefined ? true : o.maintainAspectRatio,
               plugins: { legend: Object.assign({ display: true, position: 'top' }, l, { labels: et }) }, scales: o.scales || {} };
    },
    canvas: { parentNode: cajaFalsa(altoEnLinea), isConnected: true }, ctx: lienzoFalso(472, 548), width: 236, height: 274,
    legend: { options: null, position: null }, scales: {}, actualizaciones: 0,
    // (con tope: un defecto que recomponga sin fin tiene que dar una frase, no desbordar la pila)
    update() { this.actualizaciones++; if (this.actualizaciones <= 5) actualiza(this); }
  };
  g.$caja = g.canvas.parentNode;
  return g;
}
// un eje de mentira: recuerda con qué alto máximo decidió su giro
const GIRO_BASE = function () { this.girosCon.push(this.maxHeight); };
// Lo que Chart.js hace en un eje de verdad, reducido a lo que aquí importa: fabrica
// los rótulos de sus marcas, decide el giro y dice cuánto ocupa (`fit`), y cada vez
// apunta con cuántos renglones de título lo hizo.
const PROTO_EJE = { calculateLabelRotation: GIRO_BASE, isHorizontal() { return this.$h; },
  generateTickLabels(lista) { lista.forEach(m => { m.label = m.crudo; }); },
  fit() { const x = lee(this, 'options.title.text'); this.renglonesAlOcupar.push(Array.isArray(x) ? x.length : 1); } };
const ejeFalso = (horizontal, largo, titulo, categorias) => Object.assign(Object.create(PROTO_EJE), { $h: horizontal, width: largo, height: largo,
  maxHeight: 0, maxWidth: 0, girosCon: [], renglonesAlOcupar: [], options: null, ctx: lienzoFalso(10, 10), type: categorias ? 'category' : 'linear',
  marcas: (categorias || []).map(c => ({ crudo: c, label: null })),
  crudo: { title: titulo === undefined ? { display: false } : { display: true, text: titulo, font: { size: 12 } },
           ticks: { autoSkip: true, font: { size: 11 }, maxRotation: 50, minRotation: 0 } },
  configurado: 0, configure() { this.configurado++; } });
// Un paso de composición de un eje, con el largo que se le anuncia.
const pasoEje = (e, largo) => { if (e.$h) e.maxWidth = largo; else e.maxHeight = largo; e.generateTickLabels(e.marcas); e.fit(); };
function actualiza(g, trazado) {
  const plugin = PLUGIN_RE();
  const res = g.options;
  g.legend.options = res.plugins.legend; g.legend.position = res.plugins.legend.position;
  Object.values(g.scales).forEach(e => { e.options = e.crudo; });
  if (typeof plugin.beforeUpdate === 'function') plugin.beforeUpdate(g); else pide(false, 'R-E: el plugin no tiene el gancho `beforeUpdate`');
  g.boxes = Object.values(g.scales);
  Object.values(g.scales).forEach(e => { e.maxHeight = g.height / 2; e.calculateLabelRotation(); pasoEje(e, e.anunciado !== undefined ? e.anunciado : (e.$h ? e.width : e.height)); });
  if (trazado !== undefined) g.chartArea = { top: 10, bottom: 10 + trazado };
  if (typeof plugin.afterLayout === 'function') plugin.afterLayout(g); else pide(false, 'R-E: el plugin no tiene el gancho `afterLayout`');
}
const destruyeFalso = g => { const p = PLUGIN_RE();
  if (typeof p.beforeDestroy === 'function') p.beforeDestroy(g);
  g.canvas = null; g.ctx = null;                       // Chart.js 4.4 suelta el lienzo ANTES de su último aviso
  if (typeof p.afterDestroy === 'function') p.afterDestroy(g); };

seccion('R-E', () => {
  pide(!!PLUGIN_RE(), 'R-E: no se registra el plugin `leyendaEstrecha`');
  if (!PLUGIN_RE()) return;
  const crecida = g => g.$caja.classList.has('grafico-leyenda-abajo');
  const pedido = g => g.$caja.variables['--grafico-alto-minimo'];
  const nace = (op, series, alto) => { const g = graficoFalso(op, series, alto); actualiza(g, 200); return g; };
  const leyenda = g => g.legend.options || {};

  // --- el caso corriente: `new Chart` a secas, sin nada dicho sobre la leyenda
  ESTRECHO = true;
  const opA = { maintainAspectRatio: false };
  const a = nace(opA);
  pide(leyenda(a).position === 'bottom' && a.legend.position === 'bottom', 'R-E: en el teléfono la leyenda no baja al pie');
  pide(lee(a, 'legend.options.labels.boxWidth') === 12, 'R-E: en el teléfono la muestra de la leyenda no pasa a 12 px');
  pide(crecida(a), 'R-E: la caja del gráfico no recibe `.grafico-leyenda-abajo`');
  pide(a.config.options === opA && JSON.stringify(opA) === '{"maintainAspectRatio":false}', 'R-E: se escribe en las opciones del gráfico, o se le cambian por otras');
  pide(lee(a, 'legend.options.display') === true && lee(a, 'legend.options.labels.padding') === 10, 'R-E: el velo de la leyenda no deja pasar lo que no cambia');
  ESTRECHO = false; actualiza(a, 200);
  pide(leyenda(a).position === 'top' && a.legend.position === 'top' && lee(a, 'legend.options.labels.boxWidth') === 40,
       'R-E: al volver a una pantalla ancha la leyenda no vuelve arriba con su muestra');
  pide(!crecida(a), 'R-E: al volver a una pantalla ancha la caja se queda crecida');

  // --- ROJO A: lo que el simulador escribe en sus opciones sobrevive a cualquier cruce
  ESTRECHO = true;
  const opS = { maintainAspectRatio: false, scales: { y: { title: { display: true, text: 'conteo' } } } };
  const s = nace(opS);
  s.config.options.scales.y.title.text = 'segundos'; s.config.options.scales.y.type = 'logarithmic';   // el simulador, en el teléfono
  actualiza(s, 200);
  ESTRECHO = false; actualiza(s, 200);                                                                  // gira a horizontal
  pide(s.config.options === opS && lee(s, 'config.options.scales.y.title.text') === 'segundos' && lee(s, 'config.options.scales.y.type') === 'logarithmic',
       'R-E: al cruzar a pantalla ancha se pierde lo que el simulador escribió en sus opciones en el teléfono');
  s.config.options.scales.y.max = 140;                                                                  // escribe en ancho
  ESTRECHO = true; actualiza(s, 200);                                                                   // vuelve a vertical
  pide(lee(s, 'config.options.scales.y.max') === 140 && lee(s, 'config.options.scales.y.title.text') === 'segundos',
       'R-E: al cruzar a pantalla estrecha se pierde lo que el simulador escribió en ancho');
  s.config.options.scales.y.title.text = 'minutos';                                                     // y otra vez en el teléfono
  for (let k = 0; k < 4; k++) { ESTRECHO = !ESTRECHO; actualiza(s, 200); }
  pide(JSON.stringify(s.config.options) === '{"maintainAspectRatio":false,"scales":{"y":{"title":{"display":true,"text":"minutos"},"type":"logarithmic","max":140}}}',
       'R-E: tras varios cruces las opciones del gráfico no son exactamente las que escribió el simulador: ' + JSON.stringify(s.config.options));
  // y el mismo ancho da el mismo resultado, venga de donde venga
  ESTRECHO = false; actualiza(s, 200);
  pide(leyenda(s).position === 'top' && lee(s, 'legend.options.labels.boxWidth') === 40 && !crecida(s) && pedido(s) === undefined,
       'R-E: la leyenda en pantalla ancha depende de si antes se pasó por el teléfono');

  // --- el de la casa: muestra de 24
  ESTRECHO = true;
  const opB = { maintainAspectRatio: false, plugins: { legend: { labels: { boxWidth: 24 } } } };
  const b = nace(opB);
  pide(lee(b, 'legend.options.labels.boxWidth') === 12, 'R-E: la muestra de 24 de la casa no baja a 12');
  pide(opB.plugins.legend.labels.boxWidth === 24 && opB.plugins.legend.position === undefined, 'R-E: se escribe en la leyenda de las opciones del simulador');

  // --- lo que el simulador fijó, se respeta
  const c = nace({ maintainAspectRatio: false, plugins: { legend: { position: 'right', labels: { boxWidth: 8 } } } });
  pide(leyenda(c).position === 'right' && c.legend.position === 'right', 'R-E: pisa la posición que fijó el simulador');
  pide(lee(c, 'legend.options.labels.boxWidth') === 8, 'R-E: pisa una muestra que ya era de 12 px o menos');
  const c2 = nace({ maintainAspectRatio: false, plugins: { legend: { position: 'top' } } });
  pide(leyenda(c2).position === 'bottom', 'R-E: una leyenda con `position: top` no baja en el teléfono');

  // --- lo que no se toca: sin leyenda, de las dos maneras de decirlo
  const d = nace({ maintainAspectRatio: false, plugins: { legend: { display: false } } }); actualiza(d, 110);
  pide(leyenda(d).position === 'top' && !crecida(d) && pedido(d) === undefined, 'R-E: toca un gráfico sin leyenda (`display: false`)');
  const opD2 = { maintainAspectRatio: false, plugins: { legend: false } };
  const d2 = nace(opD2); actualiza(d2, 110);
  pide(opD2.plugins.legend === false && d2.legend.position === 'top' && !crecida(d2) && pedido(d2) === undefined,
       'R-E: `legend: false` hace bajar la leyenda o crecer la caja en el teléfono');
  // un gráfico que guarda su proporción baja la leyenda pero no crece
  const e = nace({}); actualiza(e, 110);
  pide(!crecida(e) && pedido(e) === undefined, 'R-E: hace crecer la caja de un gráfico que guarda su proporción');
  // en una pantalla ancha, nada
  ESTRECHO = false;
  const h = nace({ maintainAspectRatio: false }); actualiza(h, 110);
  pide(leyenda(h).position === 'top' && !crecida(h) && pedido(h) === undefined, 'R-E: actúa en una pantalla ancha');

  // --- destruir: Chart.js suelta el lienzo ANTES de su último aviso
  ESTRECHO = true;
  const k = nace({ maintainAspectRatio: false }); actualiza(k, 110);
  pide(crecida(k) && pedido(k) !== undefined, 'R-E: (control) el gráfico que se va a destruir no había crecido');
  destruyeFalso(k);
  pide(!crecida(k), 'R-E: un gráfico destruido deja su caja con la clase `.grafico-leyenda-abajo`');
  pide(pedido(k) === undefined, 'R-E: un gráfico destruido deja pedido su alto en la caja');

  // --- dos gráficos con EL MISMO objeto de opciones: ni se pisan ni lo modifican
  const comun = { maintainAspectRatio: false };
  const g1 = nace(comun), g2 = nace(comun);
  destruyeFalso(g1); actualiza(g2, 200);
  pide(leyenda(g2).position === 'bottom' && lee(g2, 'legend.options.labels.boxWidth') === 12,
       'R-E: al destruir un gráfico, el que compartía sus opciones pierde la leyenda al pie');
  pide(JSON.stringify(comun) === '{"maintainAspectRatio":false}', 'R-E: las opciones compartidas por dos gráficos acaban modificadas');

  // --- la muestra de una serie a trazos, esté desde el principio o llegue después
  const tr = nace({ maintainAspectRatio: false }, [{ label: 'continua' }, { label: 'a trazos', borderDash: [6, 4] }]);
  pide(lee(tr, 'legend.options.labels.boxWidth') >= 16, 'R-E: en la muestra de la leyenda no cabe un trazo discontinuo `[6, 4]`');
  pide(lee(tr, 'legend.options.labels.boxWidth') <= 24, 'R-E: la muestra de una serie a trazos pasa de 24 px');
  const pt = nace({ maintainAspectRatio: false }, [{ label: 'punteada', borderDash: [2, 3] }]);
  pide(lee(pt, 'legend.options.labels.boxWidth') === 12, 'R-E: un punteado fino ensancha la muestra sin necesidad');
  const tarde = nace({ maintainAspectRatio: false }, [{ label: 'continua' }]);
  tarde.config.data.datasets.push({ label: 'llega después', borderDash: [6, 4] });
  actualiza(tarde, 200);
  pide(lee(tarde, 'legend.options.labels.boxWidth') >= 16, 'R-E: una serie a trazos añadida después de crear el gráfico se queda con la muestra de 12 px');
  tarde.config.data.datasets.pop(); actualiza(tarde, 200);
  pide(lee(tarde, 'legend.options.labels.boxWidth') === 12, 'R-E: al quitar la serie a trazos la muestra no vuelve a 12 px');

  // --- una entrada más ancha que el lienzo se parte, y no empieza fuera de él
  const larga = 'Distancia sobre el elipsoide de referencia, en kilómetros por grado';   // 67 letras: 482 px a 12 px
  const lg = nace({ maintainAspectRatio: false }, [{ label: 'corta' }, { label: larga }, { label: 'cero' }]);
  const genera = lee(lg, 'legend.options.labels.generateLabels');
  pide(typeof genera === 'function', 'R-E: la leyenda del teléfono no parte las entradas que no caben');
  if (typeof genera === 'function') {
    const items = genera.call(lg.legend, lg) || [];
    lg.ctx.font = '12px X';
    const ancho = it => 12 + 6 + lg.ctx.measureText(it.text).width + 20;   // muestra + media letra + texto + relleno
    const limpio = t => String(t).replace(/\u00a0+$/, '');
    const suyas = items.filter(it => it.datasetIndex === 1);
    pide(suyas.length > 1, 'R-E: una entrada más ancha que el lienzo no se parte en renglones');
    pide(items.every(it => typeof it.text === 'string'), 'R-E: una entrada partida lleva un arreglo, que la leyenda horizontal de Chart.js 4.4 no sabe medir');
    pide(items.every(it => ancho(it) <= 236), 'R-E: un renglón de la leyenda sigue siendo más ancho que el lienzo, y su muestra queda fuera (' + items.map(it => Math.round(ancho(it))) + ')');
    pide(suyas.map(it => limpio(it.text)).join(' ') === larga, 'R-E: al partir una entrada se pierde o se desordena su texto');
    pide(items.filter(it => it.datasetIndex === 0).length === 1 && items[0].text === 'corta', 'R-E: una entrada que cabe se parte o cambia');
    pide(suyas.length > 1 && suyas.slice(1).every(it => it.fillStyle === 'transparent' && it.strokeStyle === 'transparent'),
         'R-E: los renglones de continuación repiten la muestra de color');
    pide(suyas.length > 0 && suyas[0].fillStyle !== 'transparent', 'R-E: el primer renglón de una entrada partida pierde su muestra');
    // cada renglón de la entrada partida llena su fila: la entrada siguiente («cero», 68 px) no cabe a su lado
    const sigue = ancho(items[items.length - 1]);
    pide(suyas.every(it => ancho(it) + sigue > 236), 'R-E: un renglón de una entrada partida comparte fila con la entrada siguiente, y se leen como una sola');
  }
  // quien trae su propio generateLabels sigue fabricando sus entradas
  const mio = ch => [{ text: 'solo esta', datasetIndex: 0, fillStyle: '#123' }];
  const pr = nace({ maintainAspectRatio: false, plugins: { legend: { labels: { generateLabels: mio } } } });
  const gen2 = lee(pr, 'legend.options.labels.generateLabels');
  pide(typeof gen2 === 'function' && (gen2.call(pr.legend, pr) || []).map(it => it.text).join() === 'solo esta',
       'R-E: se pierden las entradas de leyenda que fabrica el simulador');

  // --- el alto del trazado, garantizado: una leyenda de cinco filas en una caja de 300 px.
  // El lienzo mide 274 (300 menos 26 de relleno y borde) y su trazado, 110: 164 px
  // no son trazado, y la caja necesita 164 + 170 + 26.
  const t1 = graficoFalso({ maintainAspectRatio: false });
  const compone = (g, alto, trazado) => { g.height = alto; actualiza(g, trazado); };
  compone(t1, 274, 110);
  pide(pedido(t1) === '360px', 'R-E: a un trazado de 110 px no se le pide el alto que le falta (' + pedido(t1) + ')');
  // la caja ya creció y el lienzo todavía no (Chart.js espera al siguiente fotograma):
  // un `update()` del simulador en ese rato no pide más
  compone(t1, 274, 110); compone(t1, 274, 110);
  pide(pedido(t1) === '360px', 'R-E: con la caja crecida y el lienzo aún sin crecer se pide más alto a cada trazo (' + pedido(t1) + ')');
  // el lienzo alcanza a su caja: el trazado mide su mínimo, y se pide lo mismo
  compone(t1, 334, 170);
  pide(pedido(t1) === '360px', 'R-E: con el trazado ya en su mínimo cambia el alto pedido y el gráfico oscila');
  // un píxel de redondeo no vuelve a pedir nada
  compone(t1, 334.6, 169.4);
  pide(pedido(t1) === '360px', 'R-E: un píxel de redondeo cambia el alto pedido');
  // una medida pasajera no deja la caja crecida: si la leyenda pierde filas, se pide menos
  compone(t1, 334.6, 230);
  pide(pedido(t1) === '301px', 'R-E: una medida pasajera deja la caja crecida para siempre (' + pedido(t1) + ')');
  ESTRECHO = false; compone(t1, 334.6, 230);
  pide(pedido(t1) === undefined, 'R-E: al volver a una pantalla ancha la caja conserva el alto pedido');
  ESTRECHO = true;
  // una caja que no cuenta el relleno en su alto no lo suma
  const t0 = graficoFalso({ maintainAspectRatio: false });
  t0.$caja.cajaContenido = true;
  compone(t0, 274, 110);
  pide(pedido(t0) === '334px', 'R-E: en una caja `content-box` se suma un relleno que no cuenta (' + pedido(t0) + ')');

  // --- el giro de los rótulos se decide con el alto que la caja trae escrito, crezca lo que crezca
  const gr = graficoFalso({ maintainAspectRatio: false }, null, '260px');
  gr.scales = { x: ejeFalso(true, 200), y: ejeFalso(false, 170) };
  const ultimo = e => e.girosCon[e.girosCon.length - 1];
  compone(gr, 234, 90);                    // la caja de 260: el lienzo mide 234, y el eje x dispone de 117
  pide(cerca(ultimo(gr.scales.x), 117), 'R-E: (control) con la caja sin crecer el eje x no gira con la mitad del lienzo (' + ultimo(gr.scales.x) + ')');
  compone(gr, 380, 170);                   // la caja creció a 406: sin acotar, el eje dispondría de 190
  pide(cerca(ultimo(gr.scales.x), 117), 'R-E: con la caja crecida el eje x decide su giro con más alto, y se pelea con el trazado (' + ultimo(gr.scales.x) + ')');
  pide(cerca(gr.scales.x.maxHeight, 190), 'R-E: al acotar el giro se le quita al eje su alto de verdad');
  pide(cerca(ultimo(gr.scales.y), 190), 'R-E: se acota el giro de un eje vertical');
  // un gráfico cuyo PRIMER trazo ya llega con la caja crecida: el envoltorio se instala con la mitad, no con el alto entero
  const nuevo = graficoFalso({ maintainAspectRatio: false }, null, '260px');
  nuevo.scales = { x: ejeFalso(true, 200) };
  compone(nuevo, 380, 170);
  pide(cerca(ultimo(nuevo.scales.x), 117), 'R-E: al instalarse, el tope del giro no es la mitad del lienzo de la caja sin crecer (' + ultimo(nuevo.scales.x) + ')');
  // y no depende de la historia: otro ancho, otro alto, y de vuelta
  gr.width = 275; compone(gr, 398, 170); gr.width = 236; compone(gr, 380, 170);
  pide(cerca(ultimo(gr.scales.x), 117), 'R-E: tras cambiar de ancho dentro del teléfono el giro se decide con otro alto (' + ultimo(gr.scales.x) + ')');
  pide(JSON.stringify(gr.config.options) === '{"maintainAspectRatio":false}', 'R-E: el giro se escribe en las opciones del gráfico');
  // en pantalla ancha el eje vuelve a decidir como siempre
  ESTRECHO = false; compone(gr, 380, 250);
  pide(cerca(ultimo(gr.scales.x), 190), 'R-E: en pantalla ancha el giro sigue acotado');
  // una caja sin alto escrito no se acota: no hay con qué
  ESTRECHO = true;
  const sinAlto = graficoFalso({ maintainAspectRatio: false }, null, '');
  sinAlto.scales = { x: ejeFalso(true, 200) };
  compone(sinAlto, 380, 170);
  pide(cerca(ultimo(sinAlto.scales.x), 190), 'R-E: se acota el giro de un gráfico cuya caja no trae alto escrito');
  ESTRECHO = false;
});

// =========================== C · el título de un eje cabe en su eje ===========================
seccion('C', () => {
  ESTRECHO = false;
  const largo = 'máximo de la superficie por kilómetro cuadrado (escala log)';     // 59 letras: 425 px a 12 px
  const g = graficoFalso({ maintainAspectRatio: false });
  g.scales = { y: ejeFalso(false, 170, largo), x: ejeFalso(true, 600, 'radio'), y2: ejeFalso(false, 170) };
  actualiza(g, 170);
  const texto = lee(g, 'scales.y.options.title.text');
  pide(Array.isArray(texto) && texto.length > 1, 'C: el título de un eje vertical más largo que su eje no se parte en renglones');
  if (Array.isArray(texto)) {
    g.ctx.font = '12px X';
    pide(texto.every(r => g.ctx.measureText(r).width <= 170), 'C: un renglón del título sigue sin caber en el largo del eje');
    pide(texto.join(' ') === largo, 'C: al partir el título se pierde o se desordena su texto');
    pide(ultimoDe(g.scales.y.renglonesAlOcupar) === texto.length, 'C: el eje dice cuánto ocupa antes de que su título esté partido, y no le hace sitio');
  }
  pide(g.actualizaciones === 0, 'C: partir un título hace recomponer el gráfico (' + g.actualizaciones + ' veces): tiene que decidirse dentro de la composición');
  pide(lee(g, 'scales.y.options.title.display') === true && lee(g, 'scales.y.options.title.font.size') === 12, 'C: el velo del título no deja pasar lo demás');
  pide(lee(g, 'scales.x.options.title.text') === 'radio', 'C: se parte un título que cabe');
  pide(g.scales.y.crudo.title.text === largo, 'C: el título partido se escribe en las opciones del gráfico');

  // --- LA OSCILACIÓN: la composición le anuncia al eje dos largos que se alternan (partir el
  // título ensancha el eje, eso estrecha el trazado, eso alarga el otro eje…). Dentro de una
  // composición los renglones solo pueden aumentar, así que termina.
  const o = graficoFalso({ maintainAspectRatio: false });
  o.scales = { y: ejeFalso(false, 150, largo) };
  actualiza(o, 170);
  const e = o.scales.y;
  e.renglonesAlOcupar.length = 0;
  for (let k = 0; k < 60; k++) pasoEje(e, k % 2 ? 150 : 600);                       // 600: cabría en una línea
  const serie = e.renglonesAlOcupar;
  pide(serie.every((n, k) => k === 0 || n >= serie[k - 1]), 'C: dentro de una composición el título vuelve de dos renglones a uno, y dos composiciones se alternan sin fin (' + serie.slice(0, 8) + '…)');
  pide(new Set(serie.slice(2)).size === 1, 'C: tras los primeros pasos la partición del título no se queda quieta');
  pide(o.actualizaciones === 0, 'C: la oscilación de la composición dispara recomposiciones del gráfico (' + o.actualizaciones + ')');
  // y la composición siguiente empieza de cero: con el eje largo, el título vuelve a una línea
  e.height = 600; actualiza(o, 170);
  pide(lee(o, 'scales.y.options.title.text') === largo, 'C: un título que ya cabe sigue partido por lo que pasó en la composición anterior');
  e.height = 150; actualiza(o, 170); const n1 = (lee(o, 'scales.y.options.title.text') || []).length;
  actualiza(o, 170); actualiza(o, 170);
  pide((lee(o, 'scales.y.options.title.text') || []).length === n1, 'C: la misma composición repetida da particiones distintas');

  // --- la holgura: un título que cabe por 5 px se parte, porque la composición aún puede quitarle esos 5
  const justo = graficoFalso({ maintainAspectRatio: false });
  justo.scales = { x: ejeFalso(true, 149, 'veinte letras justas') };                // 20 letras: 144 px
  actualiza(justo, 170);
  pide(Array.isArray(lee(justo, 'scales.x.options.title.text')), 'C: un título que cabe por 5 px no se parte, y queda recortado si la composición le quita esos píxeles');
  const holgado = graficoFalso({ maintainAspectRatio: false });
  holgado.scales = { x: ejeFalso(true, 170, 'veinte letras justas') };
  actualiza(holgado, 170);
  pide(lee(holgado, 'scales.x.options.title.text') === 'veinte letras justas', 'C: se parte un título al que le sobran 26 px');

  // --- EL REAJUSTE: a un eje se le anuncian 300 px y al final le quedan 150. Con el gráfico
  // compuesto se ve que el título no cabe, y se compone UNA vez más con ese largo por tope.
  const r = graficoFalso({ maintainAspectRatio: false });
  r.scales = { y: ejeFalso(false, 150, largo), x: ejeFalso(true, 600, 'radio') };
  r.scales.y.anunciado = 300;
  actualiza(r, 170);
  const tr = lee(r, 'scales.y.options.title.text');
  r.ctx.font = '12px X';
  pide(Array.isArray(tr) && tr.every(x => r.ctx.measureText(x).width <= 150), 'C: un título queda más largo que el eje que la composición le dejó al final (' + (Array.isArray(tr) ? tr.map(x => Math.round(r.ctx.measureText(x).width)) : 'sin partir') + ' en 150 px)');
  pide(Array.isArray(tr) && tr.join(' ') === largo, 'C: al reajustar el título se pierde o se desordena su texto');
  pide(r.reajustes === 1, 'C: el título que no cabe al final no provoca exactamente un reajuste de la composición (' + (r.reajustes || 0) + ')');
  pide(r.scales.y.configurado >= 1 && r.scales.x.configurado >= 1, 'C: tras reajustar la composición no se vuelven a colocar las cajas (`configure`)');
  pide(r.actualizaciones === 0, 'C: el reajuste del título pasa por un `update()` del gráfico, y puede pintar contra una composición vieja');
  // el mismo número de renglones no es el mismo ancho: «aaaaaaaaaa bbbbbbbbbb cccccccccc dd» se parte en dos
  // para 250 px (230 + 14) y también en dos para 164 (151 + 94); tiene que quedar la segunda
  const dos = graficoFalso({ maintainAspectRatio: false });
  dos.scales = { y: ejeFalso(false, 180, 'aaaaaaaaaa bbbbbbbbbb cccccccccc dd') };
  dos.scales.y.anunciado = 266;
  actualiza(dos, 170);
  const td = lee(dos, 'scales.y.options.title.text');
  pide(Array.isArray(td) && td.length === 2 && td.every(x => r.ctx.measureText(x).width <= 180),
       'C: un título partido en dos para un largo mayor no se vuelve a partir —también en dos— para el largo que le quedó (' + JSON.stringify(td) + ')');
  // si todo cabe a la primera, no hay reajuste
  pide(!g.reajustes, 'C: se reajusta la composición de un gráfico cuyos títulos ya cabían (' + g.reajustes + ')');
  // y es UNO: una palabra sola que no cabe en nada no provoca un segundo intento
  const terco = graficoFalso({ maintainAspectRatio: false });
  terco.scales = { y: ejeFalso(false, 40, 'Supercalifragilisticoespialidoso') };
  actualiza(terco, 170);
  pide(terco.reajustes === 1, 'C: un título que no puede caber dispara ' + terco.reajustes + ' reajustes en vez de uno');
  // sin la composición de Chart.js a mano, no se cae
  const guardada = Chart.layouts; Chart.layouts = undefined;
  const sin = graficoFalso({ maintainAspectRatio: false });
  sin.scales = { y: ejeFalso(false, 150, largo) }; sin.scales.y.anunciado = 300;
  let cayo = false; try { actualiza(sin, 170); } catch (e) { cayo = true; }
  Chart.layouts = guardada;
  pide(!cayo, 'C: sin `Chart.layouts` el reajuste del título tumba el trazo');

  // --- el simulador cambia el título: se pinta el nuevo
  g.scales.y.crudo.title.text = 'conteo';
  actualiza(g, 170);
  pide(lee(g, 'scales.y.options.title.text') === 'conteo', 'C: al cambiar el simulador el título se sigue pintando el anterior, partido');
  // un título que es función no se toca
  const f = () => 'calculado';
  const g2 = graficoFalso({ maintainAspectRatio: false });
  g2.scales = { y: ejeFalso(false, 20, 'x') }; g2.scales.y.crudo.title.text = f;
  actualiza(g2, 170);
  pide(lee(g2, 'scales.y.options.title.text') === f, 'C: se toca un título de eje que el simulador calcula con una función');
});

// =========================== R3-3 · un eje de pocas categorías: ninguna se salta, ninguna se pisa ===========================
seccion('R3-3', () => {
  ESTRECHO = true;
  const marcasDe = (g, id) => g.scales[id].marcas.map(m => m.label);
  const tic = (g, id, k) => lee(g, 'scales.' + id + '.options.ticks.' + k);
  // --- SALIDA 1: todos caben partidos. Tres barras en 150 px: 50 de paso, 44 de hueco.
  const g = graficoFalso({ maintainAspectRatio: false });
  g.scales = { x: ejeFalso(true, 150, undefined, ['Thomas', 'Matern con dos padres', 'LGCP']), y: ejeFalso(false, 170) };
  actualiza(g, 170);
  const x = g.scales.x;
  pide(tic(g, 'x', 'autoSkip') === false, 'R3-3: un eje horizontal de tres categorías puede saltarse alguna (`autoSkip` sigue encendido)');
  pide(x.crudo.ticks.autoSkip === true && x.crudo.ticks.maxRotation === 50, 'R3-3: la regla se aplica escribiendo en las opciones del gráfico');
  pide(tic(g, 'x', 'font') && tic(g, 'x', 'font').size === 11, 'R3-3: el velo de las marcas no deja pasar lo demás');
  const medio = x.marcas[1].label;
  pide(Array.isArray(medio) && medio.length > 1, 'R3-3: el rótulo de una categoría que no cabe en su hueco no se parte en renglones');
  if (Array.isArray(medio)) {
    x.ctx.font = '11px X';
    pide(medio.join(' ') === 'Matern con dos padres', 'R3-3: al partir el rótulo se pierde o se desordena su texto');
    pide(medio.every(r => x.ctx.measureText(r).width <= 44), 'R3-3: un renglón del rótulo sigue sin caber en el hueco de su categoría');
  }
  pide(x.marcas[0].label === 'Thomas' && x.marcas[2].label === 'LGCP', 'R3-3: se toca el rótulo de una categoría que ya cabía');
  pide(x.marcas[1].crudo === 'Matern con dos padres', 'R3-3: el rótulo partido se escribe en los datos del gráfico');
  pide(tic(g, 'x', 'maxRotation') === 0 && tic(g, 'x', 'minRotation') === 0, 'R3-3: unos rótulos partidos en renglones además pueden girar, y se intercalan con los del vecino');

  // --- SALIDA 2: seis nombres de una palabra en 172 px, y el simulador prohíbe girar. El paso es
  // 28.7 px y «Mollweide» mide 59: ni caben ni se pueden partir. Van enteros y giran lo justo.
  const pr = graficoFalso({ maintainAspectRatio: false });
  pr.scales = { x: ejeFalso(true, 172, undefined, ['Mercator', 'Mollweide', 'Equal Earth', 'Robinson', 'Azimutal', 'Winkel']) };
  pr.scales.x.crudo.ticks.maxRotation = 0;
  actualiza(pr, 170);
  pide(tic(pr, 'x', 'autoSkip') === false, 'R3-3: un eje de seis categorías puede saltarse alguna');
  pide(marcasDe(pr, 'x').every(l => typeof l === 'string'), 'R3-3: unos rótulos que van a girar además se parten en renglones (' + JSON.stringify(marcasDe(pr, 'x')) + ')');
  // el alto de un renglón (13.2) más 2 px, sobre un paso de 28.67: asin(0.53) = 32.01°
  pide(tic(pr, 'x', 'minRotation') === 33, 'R3-3: seis rótulos que no caben ni partidos no giran lo necesario para no pisarse (giro mínimo ' + tic(pr, 'x', 'minRotation') + '°)');
  pide(tic(pr, 'x', 'maxRotation') >= tic(pr, 'x', 'minRotation'), 'R3-3: el `maxRotation: 0` del simulador deja los rótulos encimados');
  // el giro mínimo basta: el paso, visto de lado, da para el alto del renglón
  pide(28.67 * Math.sin(tic(pr, 'x', 'minRotation') * Math.PI / 180) >= 13.2, 'R3-3: con el giro mínimo dos rótulos vecinos se siguen tocando');
  // unos rótulos largos de varias palabras, con alguna que no cabe: enteros, y el giro del simulador se respeta si es mayor
  const cp = graficoFalso({ maintainAspectRatio: false });
  cp.scales = { x: ejeFalso(true, 150, undefined, ['Oferta: todas las sedes', 'Bachillerato: con grado 11', 'Estudiantes: evaluados']) };
  actualiza(cp, 170);
  pide(marcasDe(cp, 'x').every(l => typeof l === 'string'), 'R3-3: si un rótulo no cabe ni partido, los demás se parten igualmente, y partidos y girados se intercalan');
  pide(tic(cp, 'x', 'minRotation') === 18 && tic(cp, 'x', 'maxRotation') === 50, 'R3-3: el giro de unos rótulos enteros no va del mínimo que evita el solape al máximo del simulador (' + tic(cp, 'x', 'minRotation') + '–' + tic(cp, 'x', 'maxRotation') + ')');
  // con un paso menor que el alto del renglón, vertical
  const ap = graficoFalso({ maintainAspectRatio: false });
  ap.scales = { x: ejeFalso(true, 60, undefined, ['Mercator', 'Mollweide', 'Robinson', 'Azimutal', 'Winkel', 'Lambert']) };
  actualiza(ap, 170);
  pide(tic(ap, 'x', 'minRotation') === 90, 'R3-3: con un paso menor que el alto de un renglón los rótulos no van en vertical');

  // --- un rótulo girado que no es el primero tampoco se sale del lienzo: el eje se da el relleno que haga falta
  // Seis rótulos a 30°, de 28.7 px de paso. Chart.js ha puesto 20 px de relleno por el primero («Mercator», 53 px);
  // el segundo mide 125 y su marca está a 43 px del borde del eje: sobresale 125·cos 30° − 43 = 65.
  const sal = graficoFalso({ maintainAspectRatio: false });
  sal.scales = { x: ejeFalso(true, 172, undefined, ['Mercator', 'Web Mercator (3857)', 'Mollweide', 'Equal Earth', 'Robinson', 'Azimutal']) };
  const xs = sal.scales.x;
  xs.ticks = xs.marcas;
  Object.assign(xs, { labelRotation: 30, position: 'bottom', left: 40, paddingLeft: 20, _margins: { left: 20, right: 0, top: 0, bottom: 0 },
    _getLabelSizes() { return { widths: [53, 125, 59, 73, 53, 53], highest: { height: 13.2 } }; }, getPixelForTick(k) { return this.left + (k + 0.5) * 172 / 6; } });
  actualiza(sal, 170);
  const hace = Math.max(53 * Math.cos(Math.PI / 6) - 172 / 12, 125 * Math.cos(Math.PI / 6) - 1.5 * 172 / 6);
  pide(xs.paddingLeft >= hace + 6 && xs.paddingLeft <= hace + 14, 'R3-3: un rótulo girado que no es el primero se sale del lienzo por la izquierda (relleno del eje ' + xs.paddingLeft + ' px, hacen falta ' + Math.ceil(hace) + ')');
  pide(xs._margins.left >= hace, 'R3-3: el relleno que despeja los rótulos no llega a los márgenes de la composición');
  // con los rótulos sin girar, o en un eje de muchas categorías, el relleno es el de Chart.js
  const quieto = graficoFalso({ maintainAspectRatio: false });
  quieto.scales = { x: ejeFalso(true, 172, undefined, ['a', 'b', 'c']) };
  quieto.scales.x.ticks = quieto.scales.x.marcas;
  Object.assign(quieto.scales.x, { labelRotation: 0, position: 'bottom', left: 40, paddingLeft: 7, _getLabelSizes() { return { widths: [300, 300, 300] }; }, getPixelForTick(k) { return this.left + k * 10; } });
  actualiza(quieto, 170);
  pide(quieto.scales.x.paddingLeft === 7, 'R3-3: se cambia el relleno de un eje cuyos rótulos no están girados');
  // un relleno que ya basta no se rebaja
  const sobra = graficoFalso({ maintainAspectRatio: false });
  sobra.scales = { x: ejeFalso(true, 172, undefined, ['Mercator', 'Web Mercator (3857)', 'Mollweide', 'Equal Earth', 'Robinson', 'Azimutal']) };
  sobra.scales.x.ticks = sobra.scales.x.marcas;
  Object.assign(sobra.scales.x, { labelRotation: 30, position: 'bottom', left: 40, paddingLeft: 200, _getLabelSizes() { return { widths: [53, 125, 59, 73, 53, 53] }; }, getPixelForTick(k) { return this.left + (k + 0.5) * 172 / 6; } });
  actualiza(sobra, 170);
  pide(sobra.scales.x.paddingLeft === 200, 'R3-3: se rebaja un relleno del eje que ya bastaba');

  // --- hasta dónde llega la regla: seis sí, siete no; una sola categoría tampoco
  const seis = graficoFalso({ maintainAspectRatio: false });
  seis.scales = { x: ejeFalso(true, 400, undefined, ['a', 'b', 'c', 'd', 'e', 'f']) };
  actualiza(seis, 170);
  pide(tic(seis, 'x', 'autoSkip') === false, 'R3-3: la regla no alcanza a un eje de seis categorías');
  const muchas = graficoFalso({ maintainAspectRatio: false });
  muchas.scales = { x: ejeFalso(true, 150, undefined, ['uno dos', 'tres cuatro', 'cinco seis', 'siete ocho', 'nueve diez', 'once doce', 'trece catorce']) };
  actualiza(muchas, 170);
  pide(tic(muchas, 'x', 'autoSkip') === true && marcasDe(muchas, 'x').every(l => typeof l === 'string') && tic(muchas, 'x', 'maxRotation') === 50,
       'R3-3: la regla alcanza a un eje de más de seis categorías');
  const una = graficoFalso({ maintainAspectRatio: false });
  una.scales = { x: ejeFalso(true, 40, undefined, ['una sola categoría larguísima']) };
  actualiza(una, 170);
  pide(tic(una, 'x', 'autoSkip') === true && typeof una.scales.x.marcas[0].label === 'string', 'R3-3: la regla alcanza a un eje de una sola categoría');
  // un eje vertical de categorías (barras horizontales) y un eje de cifras no se tocan
  const otros = graficoFalso({ maintainAspectRatio: false });
  otros.scales = { y: ejeFalso(false, 150, undefined, ['Thomas', 'Matern con dos padres', 'LGCP']), x: ejeFalso(true, 150) };
  otros.scales.x.marcas = [{ crudo: '0 a 10', label: null }, { crudo: '10 a 20 kilómetros', label: null }];
  actualiza(otros, 170);
  pide(tic(otros, 'y', 'autoSkip') === true && marcasDe(otros, 'y').every(l => typeof l === 'string'), 'R3-3: se toca un eje vertical de categorías');
  pide(tic(otros, 'x', 'autoSkip') === true && marcasDe(otros, 'x').every(l => typeof l === 'string'), 'R3-3: se toca un eje que no es de categorías');
  ESTRECHO = false;
});

// =========================== G-10 · la letra de la casa ===========================
seccion('G-10', () => {
  pide(lee(Chart, 'defaults.font.family') === 'Montserrat', 'G-10: un gráfico creado con `new Chart` no sale en Montserrat');
  const letra = lee(Chart, 'defaults.scale.ticks.font');
  pide(typeof letra === 'function', 'G-10: las marcas de los ejes no tienen la letra de la casa por defecto');
  if (typeof letra === 'function') {
    const de = (axis, type) => letra({ scale: { axis, type } }) || {};
    pide(de('y', 'linear').family === 'Fira Code' && de('y', 'logarithmic').family === 'Fira Code', 'G-10: las cifras de un eje vertical no van en Fira Code');
    pide(de('x', 'category').family === 'Montserrat' && de('x', 'linear').family === 'Montserrat', 'G-10: el eje horizontal no va en Montserrat');
    pide(de('y', 'category').family === 'Montserrat', 'G-10: los nombres de un eje vertical de categorías van en Fira Code');
    pide(de('y', 'linear').size === 11 && de('x', 'category').size === 11, 'G-10: las marcas de los ejes no van a 11 px');
    pide((letra({}) || {}).family === 'Montserrat', 'G-10: la letra de las marcas falla sin eje');
    // el renglón de las cifras mide lo que medía a 12 px: los ejes no ganan marcas
    const cif = de('y', 'linear');
    const renglon = cif.size * (cif.lineHeight || 1.2);
    pide(renglon >= 14.5 && renglon < 14.7, 'G-10: el renglón de las cifras del eje vertical no mide 14.5 px (' + renglon.toFixed(2) + '), y el eje cambia de marcas');
  }
  pide(lee(Chart, 'defaults.plugins.tooltip.bodyFont.family') === 'Fira Code', 'G-10: las cifras de la ventana emergente no van en Fira Code');
});
// Al llegar las fuentes se recomponen los gráficos que ya están en pantalla.
const FUENTES = async () => {
  const pedidas = [];
  document.fonts = { load: f => { pedidas.push(f); return Promise.resolve([]); } };
  const visto = { canvas: { isConnected: true }, n: 0, orden: [], stop() { this.orden.push('stop'); }, update(m) { this.n++; this.modo = m; this.orden.push('update'); } };
  const suelto = { canvas: { isConnected: false }, n: 0, stop() {}, update() { this.n++; } };
  Chart.instances = { 0: visto, 1: suelto };
  pide(typeof recomponerGraficosConLetra === 'function', 'G-10: no hay con qué recomponer los gráficos al llegar las fuentes');
  if (typeof recomponerGraficosConLetra === 'function') await recomponerGraficosConLetra();
  pide(pedidas.some(f => /Fira Code/.test(f)) && pedidas.some(f => /Montserrat/.test(f)), 'G-10: no se piden las dos fuentes de la casa (' + pedidas + ')');
  pide(visto.n === 1 && visto.modo === 'none', 'G-10: al llegar las fuentes no se recompone el gráfico que ya estaba en pantalla, y se queda con la letra de respaldo');
  pide(visto.orden.join() === 'stop,update', 'G-10: al llegar las fuentes se recompone sin parar antes la animación, y las barras quedan pintadas contra la escala vieja (' + visto.orden + ')');
  pide(suelto.n === 0, 'G-10: se recompone un gráfico que ya no está en la página');
  Chart.instances = {}; delete document.fonts;
};

// =========================== R-F · el suelo de la letra ===========================
seccion('R-F', () => {
  // Una rejilla de dos celdas resaltadas. En un lienzo de teléfono (277 × 150 px
  // de pantalla, densidad 2) la celda mide 46 × 17 px de dispositivo.
  const dato = (w, h) => ({ lineas: [[0, 0, w, 0, w, h, 0, h], [w, 0, 2 * w, 0, 2 * w, h, w, h]],
                            lineas_resaltadas: [1, 2] });
  DPR = 2;
  let ctx = lienzoFalso(554, 300);
  let clave = geomapaPintaLineas(ctx, dato(46, 17), identidad, { etiquetasLineas: ['14.51', '6.47'] });
  let textos = ctx.log.filter(l => l[0] === 'texto');
  pide(textos.length === 2, 'R-F: no se pintan los dos rótulos');
  pide(textos.every(l => cuerpo(l[2]) >= 11 * DPR - 1e-9),
       'R-F: a densidad 2 la letra de los rótulos baja de 11 px de pantalla (' + textos.map(l => cuerpo(l[2]) / DPR) + ')');
  pide(Array.isArray(clave) && clave.length === 2 && clave[0][0] === '1' && clave[0][1] === '14.51' && clave[1][1] === '6.47',
       'R-F: unos rótulos que no caben en su celda no devuelven la clave');
  pide(textos.map(l => l[1]).join() === '1,2', 'R-F: unos rótulos que no caben se pintan encimados en vez de numerarse');
  pide(textos.every(l => ctx.measureText(l[1]).width <= 46), 'R-F: el número de la celda tampoco cabe');

  // En el escritorio (740 × 400 de pantalla) caben, y se pintan como siempre.
  ctx = lienzoFalso(1480, 800);
  clave = geomapaPintaLineas(ctx, dato(124, 46), identidad, { etiquetasLineas: ['14.51', '6.47'] });
  textos = ctx.log.filter(l => l[0] === 'texto');
  pide(clave === null, 'R-F: unos rótulos que caben devuelven clave');
  pide(textos.map(l => l[1]).join() === '14.51,6.47', 'R-F: unos rótulos que caben no se pintan tal cual');
  pide(textos.every(l => cuerpo(l[2]) >= 11 * DPR), 'R-F: en el escritorio la letra baja del suelo');

  // Con densidad 1 el suelo son 11 px, no 22.
  DPR = 1;
  ctx = lienzoFalso(277, 150);
  geomapaPintaLineas(ctx, dato(23, 8), identidad, { etiquetasLineas: ['14.51', '6.47'] });
  textos = ctx.log.filter(l => l[0] === 'texto');
  pide(textos.every(l => cerca(cuerpo(l[2]), 11)), 'R-F: con densidad 1 el suelo no son 11 px');
  DPR = 2;
  // sin rótulos, ni clave ni texto
  ctx = lienzoFalso(554, 300);
  pide(geomapaPintaLineas(ctx, dato(46, 17), identidad, {}) === null && !ctx.log.some(l => l[0] === 'texto'),
       'R-F: una rejilla sin rótulos pinta texto o devuelve clave');
});

// =========================== R-C · el color de las marcas ===========================
seccion('R-C', () => {
  // --- el centro de la divergente
  const sim = [-3, -1, 1, 3];
  pide(cerca(geomapaTClase(sim, 2, 0), 0.5), 'R-C: la clase que contiene el centro no es el tono neutro');
  pide(cerca(geomapaTClase(sim, 1, 0) + geomapaTClase(sim, 3, 0), 1), 'R-C: la divergente con centro no es simétrica');
  pide(cerca(geomapaTClase(sim, 1, 0), 0) && cerca(geomapaTClase(sim, 3, 0), 1), 'R-C: con cortes simétricos los extremos no llegan a los extremos de la rampa');
  // la clase que CONTIENE el centro es el neutro aunque el centro no caiga en su mitad
  pide(cerca(geomapaTClase([-1, -0.2, 0.6, 3], 2, 0), 0.5), 'R-C: la clase que contiene el centro, descentrada, no es el tono neutro');
  // unos cortes que NO son simétricos: [-1,0] y [0,1] quedan a la misma distancia
  const asim = [-1, 0, 1, 5];
  pide(cerca(geomapaTClase(asim, 1, 0) + geomapaTClase(asim, 2, 0), 1) && geomapaTClase(asim, 1, 0) < 0.5 && geomapaTClase(asim, 2, 0) > 0.5,
       'R-C: con cortes asimétricos el signo no queda a cada lado del centro');
  pide(cerca(geomapaTClase(asim, 3, 0), 1) && geomapaTClase(asim, 1, 0) > 0.3, 'R-C: el lado corto alcanza la misma intensidad que el largo');
  // sin centro, lo de siempre: por orden de clase
  pide([1, 2, 3].every(k => cerca(geomapaTClase(sim, k, null), (k - 1) / 2)), 'R-C: sin centro cambia el reparto de siempre');
  pide(cerca(geomapaTClase([0, 1], 1, null), 0.5), 'R-C: una sola clase sin centro deja de ir a media rampa');
  // el centro solo lo atienden las divergentes, y solo si es un número
  pide(geomapaCentro('divergente', { centro: 0 }) === 0, 'R-C: la divergente no lee el centro del dato');
  pide(geomapaCentro('frio_caliente', { centro: 1 }, { centro: 2 }) === 2, 'R-C: el centro de la capa no manda sobre el del dato');
  pide(geomapaCentro('verde', { centro: 0 }) === null, 'R-C: una paleta secuencial atiende al centro');
  pide(geomapaCentro('divergente', {}) === null && geomapaCentro('divergente', { centro: 'cero' }) === null,
       'R-C: se inventa un centro que el dato no trae');
  // --- la rampa de las marcas
  const marcas = [2, 10, 50, 250];
  const dp = extra => Object.assign({ modo: 'puntos', marcas: marcas.slice(), marcas_tipo: 'numero', pts: [0, 0, 1, 1, 2, 2, 3, 3] }, extra);
  pide(cerca(geomapaTRampa(dp({}), 126, { paleta: 'verde' }), 0.5), 'R-C: la rampa por defecto deja de ser lineal');
  pide(cerca(geomapaTRampa(dp({ marcas_escala: 'log' }), Math.sqrt(500), { paleta: 'verde' }), 0.5), 'R-C: `marcas_escala: log` no recorre el logaritmo');
  pide(geomapaEscalaMarcas({ marcas: [0, 5, 9], marcas_escala: 'log' }) === 'lineal', 'R-C: toma logaritmos de un valor que no es positivo');
  const cen = dp({ marcas: [-1, 0, 4], centro: 0 });
  pide(cerca(geomapaTRampa(cen, 0, { paleta: 'divergente' }), 0.5) &&
       cerca(geomapaTRampa(cen, -1, { paleta: 'divergente' }) + geomapaTRampa(cen, 1, { paleta: 'divergente' }), 1) &&
       cerca(geomapaTRampa(cen, 4, { paleta: 'divergente' }), 1),
       'R-C: la rampa continua con centro no es simétrica alrededor de él');
  pide(geomapaLeyenda(dp({ marcas_escala: 'log' }), { paleta: 'verde' }).includes('escala logarítmica'),
       'R-C: la leyenda calla que la rampa es logarítmica');
  pide(!geomapaLeyenda(dp({}), { paleta: 'verde' }).includes('logarítmica'), 'R-C: la leyenda anuncia un logaritmo que no hay');
  // la leyenda de clases lleva el mismo color que el mapa
  const pol = { modo: 'poligonos', cortes: asim, clase: [1, 2, 3], centro: 0, geom: [] };
  const ley = geomapaLeyenda(pol, { paleta: 'divergente' });
  pide([1, 2, 3].every(k => ley.includes('background:' + geomapaColorClase('divergente', asim, k, 0))),
       'R-C: la leyenda de un coropleto con centro no lleva los colores del mapa');
  // --- el radio
  const con = n => ({ pts: new Array(2 * n).fill(0) });
  pide(cerca(geomapaRadioPuntos(con(65)), 2.6) && cerca(geomapaRadioPuntos(con(600)), 2.6), 'R-C: el radio de un mapa de pocos puntos cambia');
  pide(geomapaRadioPuntos(con(2209)) < 2 && geomapaRadioPuntos(con(2209)) >= 1.4, 'R-C: el radio no baja con el número de puntos');
  pide(geomapaRadioPuntos(con(900)) > geomapaRadioPuntos(con(2209)), 'R-C: el radio no baja de forma gradual');
  pide(geomapaRadioPuntos(con(900000)) >= 1.4, 'R-C: el radio baja del suelo');
  pide(geomapaRadioPuntos(Object.assign(con(2209), { radio: 3.5 })) === 3.5, 'R-C: el radio que fija el dato no manda');
  // --- el filo
  let ctx = lienzoFalso(600, 400);
  geomapaPintaPuntos(ctx, { pts: [1, 1, 2, 2, 3, 3] }, identidad, { radio: 5.2, dpr: 2 });
  let filos = ctx.log.filter(l => l[0] === 'stroke');
  pide(filos.length === 3, 'R-C: los puntos no llevan filo');
  pide(filos.every(l => l[2] > 0 && l[2] <= 5.2 / 5 + 1e-9 && l[2] <= 0.6 * 2 + 1e-9), 'R-C: el filo es más grueso que un quinto del radio');
  ctx = lienzoFalso(600, 400);
  geomapaPintaPuntos(ctx, { pts: [1, 1, 2, 2, 3, 3] }, identidad, { radio: 5.2, dpr: 2, filo: false });
  pide(!ctx.log.some(l => l[0] === 'stroke'), 'R-C: `filo: false` no quita el filo');
  ctx = lienzoFalso(600, 400);
  geomapaPintaPuntos(ctx, { pts: [1, 1, 2, 2, 3, 3], marcas: [1, 2, 2], marcas_tipo: 'categoria', niveles: ['a', 'b'] },
                     identidad, { radio: 5.2, dpr: 2, marcaResaltada: 1 });
  pide(ctx.log.filter(l => l[0] === 'stroke').length === 1, 'R-C: los puntos apagados de «ésta contra el resto» llevan filo');
  // --- la silueta del coropleto
  const cuad = { modo: 'poligonos', geom: [[[0, 0, 10, 0, 10, 10, 0, 10]], [[10, 0, 20, 0, 20, 10, 10, 10]]],
                 cortes: [0, 1, 2], clase: [1, 2] };
  ctx = lienzoFalso(600, 400);
  geomapaPintaPoligonos(ctx, cuad, identidad, { paleta: 'verde' });
  const primerRelleno = ctx.log.findIndex(l => l[0] === 'fill');
  const antes = ctx.log.slice(0, primerRelleno).filter(l => l[0] === 'stroke');
  pide(antes.length === 2, 'R-C: el coropleto no traza su silueta antes de rellenar');
  pide(antes.every(l => l[2] >= 2 * DPR - 1e-9), 'R-C: la silueta es demasiado fina para asomar bajo el borde blanco');
  ctx = lienzoFalso(600, 400);
  geomapaPintaPoligonos(ctx, cuad, identidad, { paleta: 'verde', silueta: false });
  pide(ctx.log.findIndex(l => l[0] === 'fill') === 0, 'R-C: `silueta: false` no la quita');
  // --- la rejilla con centro
  const rej = { modo: 'rejilla', nx: 3, ny: 1, zq: [0, 200, 1000], zqmax: 1000, rango: [-1, 4], centro: 0,
                caja: [0, 0, 3, 1], q: 4096, cortes: [-1, 0, 4] };
  ctx = lienzoFalso(600, 400);
  geomapaPintaRejilla(ctx, rej, identidad, { paleta: 'divergente' });
  const celdas = ctx.log.filter(l => l[0] === 'fillRect').map(l => l[1]);
  pide(celdas[1] === geomapaColor('divergente', 0.5), 'R-C: en un ráster con centro el valor del centro no es el tono neutro');
  pide(celdas[0] === geomapaColor('divergente', 0.375) && celdas[2] === geomapaColor('divergente', 1),
       'R-C: el ráster con centro no es simétrico alrededor de él');
  ctx = lienzoFalso(600, 400);
  geomapaPintaRejilla(ctx, Object.assign({}, rej, { centro: undefined }), identidad, { paleta: 'divergente' });
  pide(ctx.log.filter(l => l[0] === 'fillRect')[1][1] === geomapaColor('divergente', 0.2), 'R-C: un ráster sin centro cambia');
});

// =========================== R-F y R-C · de punta a punta ===========================
// Lo de arriba prueba cada pieza suelta. Esto las prueba ENCADENADAS, por el
// camino que recorre un mapa de verdad —`iniciarGeomapas` → `dibuja` →
// `pintarGeomapa` → el pintor de cada modo—: una clave que el pintor devuelve y
// nadie escribe en la página, o un centro que la leyenda lee y el relleno no,
// pasan todas las pruebas de pieza.
seccion('R-F', () => {
  // un lienzo de mentira que `pintarGeomapa` puede dimensionar
  // 2 × 1 unidades con una rejilla de dos celdas resaltadas encima, pequeñas
  const q = 4096;
  const dato = () => ({ modo: 'poligonos', titulo: 'Prueba', caja: [0, 0, 2, 1], q,
    geom: [[[0, 1024, 2048, 1024, 2048, 3072, 0, 3072]], [[2048, 1024, 4096, 1024, 4096, 3072, 2048, 3072]]],
    lineas: [[1600, 1900, 1900, 1900, 1900, 2000, 1600, 2000], [1900, 1900, 2200, 1900, 2200, 2000, 1900, 2000]],
    lineas_resaltadas: [1, 2] });
  DPR = 2;
  // --- pintarGeomapa entrega la clave que devuelve el pintor de polígonos
  let l = lienzoMapa(277);
  let aj = pintarGeomapa(l.cv, dato(), { etiquetasLineas: ['14.51', '6.47'] });
  pide(!!aj && Array.isArray(aj.clave) && aj.clave.length === 2 && aj.clave[1][1] === '6.47',
       'R-F: la clave de los rótulos que no caben no sale de `pintarGeomapa`');
  l = lienzoMapa(1200);
  aj = pintarGeomapa(l.cv, dato(), {});
  pide(!!aj && aj.clave === null, 'R-F: un mapa sin rótulos sale de `pintarGeomapa` con clave');

  // --- y `dibuja()` la escribe en la página, debajo de la leyenda
  const hijos = [];
  const cajaLeyenda = { innerHTML: '', appendChild(n) { hijos.push(n); } };
  l = lienzoMapa(277);
  const raiz = { dataset: { geomapa: 'prueba-clave' }, set innerHTML(v) {}, contains: () => false,
                 querySelector: s => s === '.geomapa-lienzo' ? l.cv : s === '.geomapa-caja-leyenda' ? cajaLeyenda : null };
  GEOMAPAS['prueba-clave'] = { fuente: dato(), etiquetasLineas: ['14.51', '6.47'] };
  mainContent.lista = [raiz];
  iniciarGeomapas();
  mainContent.lista = [];
  const escrita = hijos.find(n => /geomapa-clave/.test(n.className || ''));
  pide(!!escrita, 'R-F: la clave de los rótulos no se escribe en la página');
  if (escrita) {
    const texto = (escrita.partes || []).map(p => typeof p === 'string' ? p : (p.textContent || '')).join('');
    pide(texto.includes('1 → 14.51') && texto.includes('2 → 6.47'), 'R-F: la clave escrita en la página no empareja cada número con su rótulo (' + texto + ')');
  }
  pide(hijos.length === 1, 'R-F: la clave se escribe ' + hijos.length + ' veces');

  // --- el criterio de «cabe»: también el ALTO de la celda cuenta
  const baja = { lineas: [[0, 0, 200, 0, 200, 10, 0, 10]], lineas_resaltadas: [1] };   // ancha y de 10 px de alto
  let ctx = lienzoFalso(554, 300);
  pide(Array.isArray(geomapaPintaLineas(ctx, baja, identidad, { etiquetasLineas: ['14.51'] })),
       'R-F: un rótulo más alto que su celda se da por cabido');
  // --- los números de la clave van a la letra del suelo, no a la grande del lienzo
  ctx = lienzoFalso(2400, 1600);                                                       // la letra «grande» serían 60 px
  geomapaPintaLineas(ctx, { lineas: [[0, 0, 40, 0, 40, 40, 0, 40]], lineas_resaltadas: [1] }, identidad, { etiquetasLineas: ['14.51'] });
  const numeros = ctx.log.filter(x => x[0] === 'texto');
  pide(numeros.length === 1 && numeros[0][1] === '1' && cerca(cuerpo(numeros[0][2]), 11 * DPR),
       'R-F: los números de la clave se pintan a la letra grande del lienzo, no a la del suelo');
});

seccion('R-C', () => {
  DPR = 2;
  const asim = [-1, 0, 1, 5];
  // --- el RELLENO de un coropleto atiende al centro, no solo su leyenda
  const pol = { modo: 'poligonos', caja: [0, 0, 3, 1], q: 4096, cortes: asim, clase: [1, 2, 3], centro: 0,
                geom: [[[0, 0, 100, 0, 100, 100, 0, 100]], [[100, 0, 200, 0, 200, 100, 100, 100]], [[200, 0, 300, 0, 300, 100, 200, 100]]] };
  let l = lienzoMapa(600);
  pintarGeomapa(l.cv, pol, { paleta: 'divergente' });
  const rellenos = l.ctx.log.filter(x => x[0] === 'fill').map(x => x[1]);
  pide(rellenos.length === 3 && [1, 2, 3].every(k => rellenos[k - 1] === geomapaColorClase('divergente', asim, k, 0)),
       'R-C: el relleno de un coropleto ignora el centro que su leyenda sí lee');
  pide(rellenos[0] !== geomapaColorClase('divergente', asim, 1, null), 'R-C: (control) con estos cortes el centro no cambia el color');
  // --- y las MARCAS con cortes
  const marc = { modo: 'puntos', caja: [0, 0, 1, 1], q: 4096, pts: [10, 10, 20, 20, 30, 30], marcas: [-0.5, 0.5, 3],
                 marcas_tipo: 'numero', cortes: asim, clase: [1, 2, 3], centro: 0 };
  pide([0, 1, 2].every(i => geomapaColorMarca(marc, i, { paleta: 'divergente' }) === geomapaColorClase('divergente', asim, i + 1, 0)),
       'R-C: las marcas clasificadas ignoran el centro');
  const leyM = geomapaLeyenda(marc, { paleta: 'divergente' });
  pide([1, 2, 3].every(k => leyM.includes('background:' + geomapaColorClase('divergente', asim, k, 0))),
       'R-C: la leyenda de unas marcas clasificadas con centro no lleva los colores del mapa');
  // --- la leyenda de un ráster con centro lleva el color de sus celdas
  const rej = { modo: 'rejilla', nx: 3, ny: 1, zq: [0, 200, 1000], zqmax: 1000, rango: [-1, 4], centro: 0,
                caja: [0, 0, 3, 1], q: 4096, cortes: [-1, 0, 4] };
  const leyR = geomapaLeyenda(rej, { paleta: 'divergente' });
  pide(leyR.includes('background:' + geomapaColor('divergente', geomapaTCentrado(-0.5, 0, 4))) &&
       leyR.includes('background:' + geomapaColor('divergente', geomapaTCentrado(2, 0, 4))),
       'R-C: la leyenda de un ráster con centro no lleva los colores de sus celdas');
  // --- la barra de la rampa recorre los colores que pinta el mapa
  const cen = { modo: 'puntos', pts: [0, 0, 1, 1, 2, 2], marcas: [-1, 0, 4], marcas_tipo: 'numero', centro: 0 };
  const leyC = geomapaLeyenda(cen, { paleta: 'divergente' });
  // el valor 0 —el centro— está a un quinto de la barra, y ahí tiene que estar el tono neutro
  const paradas = (/linear-gradient\(to right,([^"]*)\)"/.exec(leyC) || ['', ''])[1].split(/,(?=rgb)/);
  pide(paradas.length === 21 && paradas[4] === geomapaColor('divergente', 0.5) && paradas[20] === geomapaColor('divergente', 1) &&
       paradas[0] === geomapaColor('divergente', geomapaTRampa(cen, -1, { paleta: 'divergente' })),
       'R-C: la barra de la leyenda no recorre los colores que el mapa da a cada valor');
  // --- el radio llega al lienzo en píxeles de dispositivo
  l = lienzoMapa(600);
  pintarGeomapa(l.cv, { modo: 'puntos', caja: [0, 0, 1, 1], q: 4096, pts: [10, 10, 20, 20] }, {});
  let arcos = l.ctx.log.filter(x => x[0] === 'arc').map(x => x[1]);
  pide(arcos.length === 2 && arcos.every(r => cerca(r, 2.6 * DPR)), 'R-C: el radio de los puntos no se multiplica por la densidad de la pantalla (' + arcos + ')');
  // --- el filo: no en los puntos pequeños, cuyo tono oscurece
  const muchos = { modo: 'puntos', caja: [0, 0, 1, 1], q: 4096, pts: new Array(2 * 2209).fill(100) };
  l = lienzoMapa(600);
  pintarGeomapa(l.cv, muchos, {});
  pide(!l.ctx.log.some(x => x[0] === 'stroke'), 'R-C: un mapa de dos mil puntos lleva filo, y el tono del punto ya no es el de su leyenda');
  l = lienzoMapa(600);
  pintarGeomapa(l.cv, { modo: 'puntos', caja: [0, 0, 1, 1], q: 4096, pts: [10, 10, 20, 20] }, {});
  pide(l.ctx.log.filter(x => x[0] === 'stroke').length === 2, 'R-C: un mapa de pocos puntos pierde el filo');
  // --- la silueta: solo donde las unidades se tocan
  const sueltas = { modo: 'poligonos', geom: [[[0, 0, 10, 0, 10, 10, 0, 10]], [[30, 0, 40, 0, 40, 10, 30, 10]]], cortes: [0, 1, 2], clase: [1, 2] };
  let ctx = lienzoFalso(600, 400);
  geomapaPintaPoligonos(ctx, sueltas, identidad, { paleta: 'verde' });
  pide(ctx.log.findIndex(x => x[0] === 'fill') === 0,
       'R-C: unas unidades que no se tocan —un cartograma, donde el área es el dato— llevan silueta');
  ctx = lienzoFalso(600, 400);
  geomapaPintaPoligonos(ctx, Object.assign({}, sueltas), identidad, { paleta: 'verde', silueta: true });
  pide(ctx.log.findIndex(x => x[0] === 'fill') === 2, 'R-C: `silueta: true` no la fuerza');
  pide(cerca(geomapaFronteraComun(sueltas.geom), 0), 'R-C: se ven fronteras comunes donde no las hay');
  pide(geomapaFronteraComun([[[0, 0, 10, 0, 10, 10, 0, 10]], [[10, 0, 20, 0, 20, 10, 10, 10]]]) > 0.3, 'R-C: no se ve la frontera común de dos unidades vecinas');
  // un solo vértice compartido por una unidad consigo misma no es frontera
  pide(cerca(geomapaFronteraComun([[[0, 0, 10, 0, 10, 10, 0, 0]]]), 0), 'R-C: una unidad hace frontera consigo misma');
});

// =========================== R-B · la tabla ordenable ===========================
seccion('R-B', () => {
  // `formatea` es interna de pintarTablaRanking: se le pide una tabla y se lee.
  ESCRITO.length = 0;
  const piezas = { '.tabla-ranking-marco': nodoFalso(), '.tabla-ranking-pie': nodoFalso(), '.tabla-ranking-estado': nodoFalso() };
  const raiz = { querySelector: s => piezas[s] || null, querySelectorAll: () => [] };
  let html = '';
  try {
    pintarTablaRanking(raiz, { columnas: [{ clave: 'm', titulo: 'modelo', tipo: 'texto' },
                                          { clave: 'v', titulo: 'valor', decimales: 2 }],
                               filas: [{ m: 'a', v: 2621.5 }, { m: 'b', v: 0.25 }] });
  } catch (e) { html += ' EXC ' + e.message; }
  html += ESCRITO.join(' | ');
  pide(!html.includes(' EXC '), 'R-B: la tabla ordenable no se pinta:' + html.slice(0, 120));
  pide(html.includes('2\u202f621.50'), 'R-B: la tabla ordenable no escribe «2 621.50» (punto decimal, millares con espacio fino)');
  pide(html.includes('0.25') && !html.includes('0,25'), 'R-B: la tabla ordenable escribe la coma decimal');
  pide(!html.includes('2.621'), 'R-B: la tabla ordenable separa los millares con punto');
});

// Las dos secciones asíncronas, y al final el resultado.
(async () => {
  for (const [nombre, f] of [['G-10', FUENTES]]) {
    try { await f(); } catch (e) { fallos.push('CAÍDA en la sección ' + nombre + ': ' + String(e && e.message).slice(0, 140)); }
  }
  console.log(JSON.stringify(fallos));
})();
"""


def css_ok(texto: str) -> list[str]:
    """La mitad de R-E que no es JavaScript: el alto mínimo de la hoja."""
    m = re.search(r"@media \(max-width: 640px\) \{(?:[^{}]|\{[^{}]*\})*?"
                  r"\.grafico-leyenda-abajo \{\s*min-height: max\((\d+)px, var\(--grafico-alto-minimo, 0px\)\);", texto)
    if not m:
        return ["R-E: la hoja no da un alto mínimo a `.grafico-leyenda-abajo` por debajo de 640 px"]
    if int(m.group(1)) < 300:
        return [f"R-E: el alto mínimo de `.grafico-leyenda-abajo` es {m.group(1)} px, menos de 300"]
    # LOS NOMBRES QUE LOS DOCUMENTOS LE PASAN A LA PLANTILLA. En la segunda ronda de
    # esta tarea un `sed` cambió `spec.rotuloAnula` por `spec.letreroAnula` en la
    # rúbrica, y los talleres 2 y 3 —que pasan `rotuloAnula`— se habrían quedado sin
    # su rótulo sin que nada saltara. La rúbrica tiene que leer el nombre que le pasan.
    if "spec.rotuloAnula ||" not in texto:
        return ["R-B: la rúbrica de la plantilla ya no lee `spec.rotuloAnula`, que es el nombre que le pasan los talleres"]
    for taller in ("ensambla_taller2.py", "ensambla_taller3.py"):
        ruta = RAIZ / "precalculo" / taller
        if ruta.exists() and "rotuloAnula" not in ruta.read_text(encoding="utf-8"):
            return [f"R-B: {taller} ya no pasa `rotuloAnula` a la rúbrica; la guarda de la plantilla vigila un nombre que nadie usa"]
    # Y la de R-F: la clave sustituye a unos rótulos cuyo suelo son 11 px de pantalla.
    c = re.search(r"\.geomapa-clave \{\s*font-size: max\((\d+(?:\.\d+)?)px,", texto)
    if not c:
        return ["R-F: la hoja no fija un suelo en px para la letra de `.geomapa-clave`"]
    if float(c.group(1)) < 11:
        return [f"R-F: la clave de los rótulos puede bajar a {c.group(1)} px, menos que el suelo de 11"]
    return []


def corre(texto: str) -> list[str]:
    js = "\n".join(region(texto, a, c, q) for a, c, q in REGIONES)
    prog = BANCO.replace("__PLANTILLA__", js)
    with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False, encoding="utf-8") as f:
        f.write(prog)
        ruta = f.name
    try:
        r = subprocess.run(["node", ruta], capture_output=True, text=True)
    finally:
        pathlib.Path(ruta).unlink(missing_ok=True)
    if r.returncode != 0:
        # Un defecto inyectado puede romper el guion en vez de dar un valor malo:
        # también es «rojo», y se dice con qué.
        ultima = (r.stderr.strip().splitlines() or ["sin mensaje"])[-1]
        return [f"el JavaScript de la plantilla no se ejecuta: {ultima[:160]}"]
    return json.loads(r.stdout.strip().splitlines()[-1]) + css_ok(texto)


# Los defectos. Cada uno: (qué es, texto que se busca, texto que lo sustituye, la
# regla que tiene que saltar). El texto buscado tiene que estar exactamente una vez.
INYECCIONES = [
    # ------------------------------------------------------------------ R-D
    ("la fusión vuelve a ser superficial",
     "        options: fusionarOpcionesGrafico({", "        options: Object.assign({", "R-D"),
    ("la fusión profunda funde también los arreglos",
     "             Object.getPrototypeOf(v) === Object.prototype;", "             true;", "R-D"),
    ("una clave `undefined` borra lo de la casa",
     "        if (v === undefined) return;\n", "", "R-D"),
    ("un eje propio no hereda la letra",
     "        ejes[id] = fusionProfunda({ ticks: { font: letra } }, e);", "        ejes[id] = e;", "R-D"),
    ("un eje propio sin lado se toma siempre por vertical",
     "          : id[0] !== 'x';", "          : true;", "R-D"),
    # ------------------------------------------------------------------ R-E
    ("la leyenda no baja en el teléfono",
     "        get(t, k) { return k === 'position' && baja ? 'bottom' : k === 'labels' ? etiquetas : t[k]; }",
     "        get(t, k) { return k === 'labels' ? etiquetas : t[k]; }", "R-E"),
    ("la caja de la leyenda no cambia de sitio, solo sus opciones",
     "      if (baja) chart.legend.position = 'bottom';\n", "", "R-E"),
    ("se pisa la posición que fijó el simulador",
     "      const baja = opciones.position === undefined || opciones.position === 'top';",
     "      const baja = true;", "R-E"),
    ("la muestra de la leyenda se queda en 40 px",
     "        get(t, k) { return k === 'boxWidth' ? muestra : k === 'generateLabels' ? genera : t[k]; }",
     "        get(t, k) { return k === 'generateLabels' ? genera : t[k]; }", "R-E"),
    ("se pisa una muestra que ya era estrecha",
     "      const ancha = typeof opciones.labels.boxWidth === 'number' && opciones.labels.boxWidth > 12;",
     "      const ancha = true;", "R-E"),
    ("la muestra no se ensancha para una serie a trazos",
     "          ancho = Math.max(ancho, Math.min(24, 2 * d[0] + (d[1] || d[0])));", "", "R-E"),
    ("la muestra para trazos pasa de 24 px",
     "          ancho = Math.max(ancho, Math.min(24, 2 * d[0] + (d[1] || d[0])));",
     "          ancho = Math.max(ancho, 2 * d[0] + (d[1] || d[0]) + 20);", "R-E"),
    ("`legend: false` deja de respetarse",
     "      if (crudo && crudo.legend === false) return false;\n", "", "R-E"),
    ("`display: false` deja de respetarse",
     "      return !!ley && ley.display !== false;", "      return !!ley;", "R-E"),
    ("la leyenda baja también en pantalla ancha",
     "      if (!estrecho || !chart.legend) return false;", "      if (!chart.legend) return false;", "R-E"),
    ("se escribe la leyenda en las opciones del gráfico, como en la primera ronda",
     "      chart.legend.options = new Proxy(opciones, {",
     "      const crudas = chart.config.options; crudas.plugins = crudas.plugins || {}; crudas.plugins.legend = Object.assign(crudas.plugins.legend || {}, { position: 'bottom' });\n      chart.legend.options = new Proxy(opciones, {", "R-E"),
    ("la caja del gráfico no recibe su clase",
     "        if (estado.crece) estado.caja.classList.add('grafico-leyenda-abajo');",
     "        if (estado.crece) estado.caja.classList.add('grafico-leyenda');", "R-E"),
    ("la caja crece aunque el gráfico guarde su proporción",
     "      estado.crece = aplica && !!estado.caja && chart.options.maintainAspectRatio === false;",
     "      estado.crece = aplica && !!estado.caja;", "R-E"),
    ("al volver a una pantalla ancha la caja se queda crecida",
     "        else soltarCajaGrafico(estado);\n", "", "R-E"),
    ("al destruir se busca la caja por el lienzo, que Chart.js ya soltó",
     "        beforeDestroy(chart) { soltarCajaGrafico(chart.$leyendaEstrecha); }",
     "        afterDestroy(chart) { const c = chart.canvas && chart.canvas.parentNode; if (c) { c.classList.remove('grafico-leyenda-abajo'); c.style.removeProperty('--grafico-alto-minimo'); } }", "R-E"),
    ("un gráfico destruido deja pedido su alto",
     "      estado.caja.style.removeProperty('--grafico-alto-minimo');\n", "", "R-E"),
    ("una entrada larga de la leyenda no se parte",
     "      if (typeof texto !== 'string' || mide(texto) <= ancho) return [texto];", "      return [texto];", "R-E"),
    ("la entrada partida viaja como un arreglo, que la leyenda horizontal no mide",
     "          renglones.forEach((renglon, k) => {\n            partidas.push(k === 0 ? Object.assign({}, it, { text: llena(renglon) })",
     "          [renglones].forEach((renglon, k) => {\n            partidas.push(k === 0 ? Object.assign({}, it, { text: renglon })", "R-E"),
    ("los renglones de continuación repiten la muestra",
     "              : Object.assign({}, it, { text: llena(renglon), fillStyle: 'transparent', strokeStyle: 'transparent',",
     "              : Object.assign({}, it, { text: llena(renglon),", "R-E"),
    ("al partir no se descuenta la muestra, y el renglón sigue sin caber",
     "        const ancho = chart.width - muestra - letra.size / 2 - 2 * (typeof etq.padding === 'number' ? etq.padding : 10);",
     "        const ancho = chart.width;", "R-E"),
    ("un renglón de continuación comparte fila con la entrada siguiente",
     "        const llena = t => t + '\\u00a0'.repeat(Math.max(0, Math.floor((ancho - mide(t)) / duro)));",
     "        const llena = t => t;", "R-E"),
    ("se pierden las entradas que fabrica el simulador",
     "      const genera = etiquetasLeyendaEstrecha(opciones.labels.generateLabels, typeof muestra === 'number' ? muestra : 12);",
     "      const genera = etiquetasLeyendaEstrecha(Chart.defaults.plugins.legend.labels.generateLabels, typeof muestra === 'number' ? muestra : 12);", "R-E"),
    ("el alto mínimo de la hoja baja a 200 px",
     "      .grafico-leyenda-abajo {\n        min-height: max(300px,", "      .grafico-leyenda-abajo {\n        min-height: max(200px,", "R-E"),
    ("la hoja no lee el alto que pide el plugin",
     "min-height: max(300px, var(--grafico-alto-minimo, 0px));", "min-height: 300px;", "R-E"),
    ("al trazado no se le garantiza su alto",
     "          asegurarTrazadoGrafico(chart);\n", "", "R-E"),
    ("el alto garantizado del trazado baja a 100 px",
     "    const GRAFICO_TRAZADO_MIN = 170;", "    const GRAFICO_TRAZADO_MIN = 100;", "R-E"),
    ("el alto se calcula con la caja, y cada trazo pide más",
     "      const alto = Math.ceil(chart.height - (a.bottom - a.top) + GRAFICO_TRAZADO_MIN + marcoCajaGrafico(estado.caja));",
     "      const alto = Math.ceil((estado.alto || 300) - (a.bottom - a.top) + GRAFICO_TRAZADO_MIN);", "R-E"),
    ("el alto pedido olvida el relleno de la caja",
     "        ? px(cs.paddingTop) + px(cs.paddingBottom) + px(cs.borderTopWidth) + px(cs.borderBottomWidth)", "        ? 0", "R-E"),
    ("el alto pedido solo crece, y una medida pasajera se queda",
     "      if (Math.abs(alto - (estado.alto || 0)) > 2) {", "      if (alto > (estado.alto || 0) + 2) {", "R-E"),
    ("un píxel de redondeo hace redibujar el gráfico",
     "      if (Math.abs(alto - (estado.alto || 0)) > 2) {", "      if (alto !== (estado.alto || 0)) {", "R-E"),
    ("el giro de los rótulos no se acota, y se pelea con el alto",
     "          acotarGiroGrafico(chart, chart.$leyendaEstrecha);\n", "", "R-E"),
    ("el giro se acota con el alto de ahora, no con el que la caja trae escrito",
     "      const alto0 = estado.crece ? parseFloat(estado.caja.style && estado.caja.style.height) : NaN;",
     "      const alto0 = estado.crece ? chart.height + 26 : NaN;", "R-E"),
    ("el tope del giro se instala con el alto entero, no con la mitad",
     "      const tope = (alto0 - marco) / 2;", "      const tope = (alto0 - marco);", "R-E"),
    ("el giro se acota también en los ejes verticales",
     "          if (this.isHorizontal() && real > this.$altoGiro) this.maxHeight = this.$altoGiro;",
     "          if (real > this.$altoGiro) this.maxHeight = this.$altoGiro;", "R-E"),
    ("al acotar el giro, el eje se queda con el alto recortado",
     "          try { return propio.call(this); } finally { this.maxHeight = real; }",
     "          return propio.call(this);", "R-E"),
    ("en pantalla ancha el giro sigue acotado",
     "        if (!(alto0 > 0)) { delete eje.calculateLabelRotation; return; }",
     "        if (!(alto0 > 0)) { return; }", "R-E"),
    # -------------------------------------------------------------------- C
    ("el título de un eje que no cabe no se parte",
     "        eje.fit = function () { partirTituloEje(this); const r = ocupa.call(this);",
     "        eje.fit = function () { const r = ocupa.call(this);", "C"),
    ("el título se parte después de que el eje diga cuánto ocupa",
     "        eje.fit = function () { partirTituloEje(this); const r = ocupa.call(this);",
     "        eje.fit = function () { const r = ocupa.call(this); partirTituloEje(this);", "C"),
    ("el título partido no llega al eje",
     "          get(t, k) { return k === 'text' && eje.$tituloRenglones ? eje.$tituloRenglones : t[k]; }",
     "          get(t, k) { return t[k]; }", "C"),
    ("dentro de una composición el título vuelve a una línea, y dos composiciones se alternan",
     "      if (largo < eje.$tituloLargo) {", "      if (true) {", "C"),
    ("el título solo se vuelve a partir si gana renglones, y se queda ancho con los mismos",
     "      if (largo < eje.$tituloLargo) {",
     "      if (renglones.length > (eje.$tituloRenglones ? eje.$tituloRenglones.length : 1)) {", "C"),
    ("la composición siguiente hereda la partición de la anterior",
     "        eje.$tituloRenglones = null;\n        eje.$tituloLargo = Infinity;", "", "C"),
    ("el título se mide sin holgura, y queda recortado por unos píxeles",
     "    const GRAFICO_TITULO_HOLGURA = 16;", "    const GRAFICO_TITULO_HOLGURA = 0;", "C"),
    ("la holgura del título se come títulos que caben de sobra",
     "    const GRAFICO_TITULO_HOLGURA = 16;", "    const GRAFICO_TITULO_HOLGURA = 60;", "C"),
    ("el título se mide contra el alto del eje aunque sea horizontal",
     "      const largo = Math.min((eje.isHorizontal() ? eje.maxWidth : eje.maxHeight) - GRAFICO_TITULO_HOLGURA,",
     "      const largo = Math.min(eje.maxHeight - GRAFICO_TITULO_HOLGURA,", "C"),
    ("al cambiar el simulador el título se sigue pintando el viejo",
     "          ? { entero: titulo.text, letra: Chart.helpers.toFont(titulo.font).string } : null;",
     "          ? (eje.$titulo || { entero: titulo.text, letra: Chart.helpers.toFont(titulo.font).string }) : null;", "C"),
    ("el título partido se escribe en las opciones",
     "        eje.$tituloRenglones = renglones.length > 1 ? renglones : null;",
     "        eje.$tituloRenglones = renglones.length > 1 ? renglones : null; if (eje.$tituloRenglones) eje.options.title.text = renglones;", "C"),
    # ----------------------------------------------------------------- R3-3
    ("un eje de pocas categorías puede saltarse alguna",
     "            if (k === 'autoSkip') return false;\n", "", "R3-3"),
    ("el rótulo de una categoría que no cabe no se parte",
     "        marcas.forEach((m, k) => { if (typeof m.label === 'string' && partidos[k].length > 1) m.label = partidos[k]; });\n", "", "R3-3"),
    ("los rótulos partidos además pueden girar",
     "            if (k === 'maxRotation') return eje.$sinGiro ? 0 : Math.max(t[k] || 0, eje.$giroMinimo);",
     "            if (k === 'maxRotation') return Math.max(t[k] || 0, eje.$giroMinimo);", "R3-3"),
    ("los rótulos que van a girar se parten igualmente",
     "      if (caben) {\n        marcas.forEach(", "      if (true) {\n        marcas.forEach(", "R3-3"),
    ("los rótulos que no caben ni partidos no giran lo necesario",
     "            if (k === 'minRotation') return eje.$sinGiro ? 0 : Math.max(t[k] || 0, eje.$giroMinimo);",
     "            if (k === 'minRotation') return eje.$sinGiro ? 0 : (t[k] || 0);", "R3-3"),
    ("el `maxRotation` del simulador manda sobre el giro que evita el solape",
     "            if (k === 'maxRotation') return eje.$sinGiro ? 0 : Math.max(t[k] || 0, eje.$giroMinimo);",
     "            if (k === 'maxRotation') return eje.$sinGiro ? 0 : t[k];", "R3-3"),
    ("el giro mínimo se calcula sin el alto del renglón",
     "      const alto = renglones * (letra.lineHeight || letra.size * 1.2) + 2;",
     "      const alto = 4;", "R3-3"),
    ("con un paso menor que el renglón los rótulos no van en vertical",
     "      eje.$giroMinimo = alto >= paso ? 90 : Math.ceil(Math.asin(alto / paso) * 180 / Math.PI);",
     "      eje.$giroMinimo = Math.ceil(Math.asin(Math.min(0.7, alto / paso)) * 180 / Math.PI);", "R3-3"),
    ("la regla alcanza solo a cinco categorías",
     "    const GRAFICO_POCAS_CATEGORIAS = 6;", "    const GRAFICO_POCAS_CATEGORIAS = 5;", "R3-3"),
    ("la regla de pocas categorías se aplica a cualquier número",
     "                   marcas.length >= 2 && marcas.length <= GRAFICO_POCAS_CATEGORIAS;",
     "                   marcas.length >= 2;", "R3-3"),
    ("la regla alcanza a un eje de una sola categoría",
     "                   marcas.length >= 2 && marcas.length <= GRAFICO_POCAS_CATEGORIAS;",
     "                   marcas.length >= 1 && marcas.length <= GRAFICO_POCAS_CATEGORIAS;", "R3-3"),
    ("la regla de pocas categorías alcanza a los ejes verticales",
     "      eje.$pocas = eje.type === 'category' && eje.isHorizontal() &&",
     "      eje.$pocas = eje.type === 'category' &&", "R3-3"),
    ("la regla de pocas categorías alcanza a los ejes de cifras",
     "      eje.$pocas = eje.type === 'category' && eje.isHorizontal() &&",
     "      eje.$pocas = eje.isHorizontal() &&", "R3-3"),
    ("el rótulo se parte contra el paso entero, sin el aire entre rótulos",
     "      const hueco = paso - 6;", "      const hueco = paso + 20;", "R3-3"),
    ("la regla se aplica escribiendo en las opciones",
     "      if (!eje.$pocas || !(eje.maxWidth > 0)) return;",
     "      if (eje.$pocas) eje.options.ticks.autoSkip = false;\n      if (!eje.$pocas || !(eje.maxWidth > 0)) return;", "R3-3"),
    ("un rótulo girado que no es el primero se sale del lienzo",
     "const r = ocupa.call(this); despejarRotulosEje(this); return r; };", "const r = ocupa.call(this); return r; };", "R3-3"),
    ("solo se despeja el primer rótulo, como hace Chart.js",
     "        sobresale = Math.max(sobresale, anchos[k] * coseno + canto - centro);",
     "        if (k === 0) sobresale = Math.max(sobresale, anchos[k] * coseno + canto - centro);", "R3-3"),
    ("al despejar un rótulo girado se olvida lo que asoma su alto",
     "        sobresale = Math.max(sobresale, anchos[k] * coseno + canto - centro);",
     "        sobresale = Math.max(sobresale, anchos[k] * coseno - centro);", "R3-3"),
    ("el relleno que despeja los rótulos no llega a los márgenes",
     "        if (eje._margins) eje._margins.left = Math.max(eje._margins.left || 0, relleno);\n", "", "R3-3"),
    ("se despejan rótulos que no están girados",
     "      if (!eje.$pocas || !(eje.labelRotation > 0) || eje.position === 'top') return;",
     "      if (!eje.$pocas || eje.position === 'top') return;", "R3-3"),
    ("se rebaja un relleno que ya bastaba",
     "      if (relleno > (eje.paddingLeft || 0)) {", "      if (true) {", "R3-3"),
    # --------------------------------------------------------- C · reajuste
    ("un título más largo que su eje no se reajusta",
     "          reajustarTitulosGrafico(chart);\n", "", "C"),
    ("el reajuste no pone tope al título",
     "        if (ancho > largo - 2) { eje.$tituloTope = largo - GRAFICO_TITULO_HOLGURA; falta = true; }",
     "        if (ancho > largo - 2) { falta = true; }", "C"),
    ("el título no atiende al tope del reajuste",
     "                             eje.$tituloTope);", "                             Infinity);", "C"),
    ("tras reajustar no se vuelven a colocar las cajas",
     "      (chart.boxes || []).forEach(caja => { if (typeof caja.configure === 'function') caja.configure(); });\n", "", "C"),
    ("el reajuste pasa por un `update()` del gráfico",
     "      Chart.layouts.update(chart, chart.width, chart.height, chart._minPadding || 0);",
     "      chart.update('none');", "C"),
    ("se reajusta aunque todos los títulos quepan",
     "      if (!falta) return;\n      Chart.layouts.update(", "      Chart.layouts.update(", "C"),
    ("sin la composición de Chart.js el reajuste tumba el trazo",
     "      if (!Chart.layouts || typeof Chart.layouts.update !== 'function') return;\n", "", "C"),
    # ----------------------------------------------------------------- G-10
    ("los gráficos de `new Chart` vuelven a la letra de Chart.js",
     "      Chart.defaults.font.family = 'Montserrat';\n", "", "G-10"),
    ("las marcas de los ejes pierden la letra de la casa",
     "      Chart.defaults.scale.ticks.font = letraMarcasGrafico;\n", "", "G-10"),
    ("los nombres de un eje vertical de categorías salen en Fira Code",
     "      const cifras = !!eje && eje.axis === 'y' && eje.type !== 'category';",
     "      const cifras = !!eje && eje.axis === 'y';", "G-10"),
    ("las cifras del eje vertical pierden su interlineado, y el eje dobla sus marcas",
     "      return cifras ? { family: 'Fira Code', size: 11, lineHeight: 1.32 }",
     "      return cifras ? { family: 'Fira Code', size: 11 }", "G-10"),
    ("el interlineado de las cifras se queda una décima corto, y los ejes al borde ganan una marca",
     "      return cifras ? { family: 'Fira Code', size: 11, lineHeight: 1.32 }",
     "      return cifras ? { family: 'Fira Code', size: 11, lineHeight: 1.31 }", "G-10"),
    ("al llegar las fuentes no se recomponen los gráficos",
     "          if (g.canvas && g.canvas.isConnected) { g.stop(); g.update('none'); }\n", "", "G-10"),
    ("al llegar las fuentes se recompone también un gráfico que ya no está",
     "          if (g.canvas && g.canvas.isConnected) { g.stop(); g.update('none'); }\n", "          g.stop(); g.update('none');\n", "G-10"),
    ("al llegar las fuentes se recompone sin parar la animación en marcha",
     "          if (g.canvas && g.canvas.isConnected) { g.stop(); g.update('none'); }\n",
     "          if (g.canvas && g.canvas.isConnected) { g.update('none'); }\n", "G-10"),
    ("no se pide Fira Code",
     """      return Promise.all([document.fonts.load('11px "Fira Code"'), document.fonts.load('12px Montserrat')])""",
     """      return Promise.all([document.fonts.load('12px Montserrat')])""", "G-10"),
    ("las cifras de la ventana emergente pierden Fira Code",
     "      Chart.defaults.plugins.tooltip.bodyFont = { family: 'Fira Code' };\n", "", "G-10"),
    # ------------------------------------------------------------------ R-F
    ("el suelo de la letra vuelve a los píxeles de dispositivo",
     "        const suelo = GEOMAPA_ROTULO_MIN * dprReal;", "        const suelo = GEOMAPA_ROTULO_MIN;", "R-F"),
    ("el suelo de la letra baja a 9",
     "    const GEOMAPA_ROTULO_MIN = 11;", "    const GEOMAPA_ROTULO_MIN = 9;", "R-F"),
    ("los rótulos que no caben se pintan encimados",
     "        if (!celdas.every(cabe)) {", "        if (false) {", "R-F"),
    ("un rótulo más alto que su celda se da por cabido",
     "                          px * 0.72 <= c.y1 - c.y0;", "                          true;", "R-F"),
    ("los números de la clave van a la letra grande",
     "          ctx.font = fuente(suelo);\n", "", "R-F"),
    ("la clave de los rótulos no sale del pintor de líneas",
     "      ctx.restore();\n      return clave;\n", "      ctx.restore();\n      return null;\n", "R-F"),
    ("el pintor de polígonos no devuelve la clave",
     "      geomapaPintaSuperpuestos(ctx, d, aj, o);\n      return clave;",
     "      geomapaPintaSuperpuestos(ctx, d, aj, o);\n      return null;", "R-F"),
    ("`pintarGeomapa` descarta la clave",
     "aj.clave = geomapaPintaPoligonos(ctx, d, aj, o) || null;", "geomapaPintaPoligonos(ctx, d, aj, o);", "R-F"),
    ("la clave no se escribe en la página",
     "            cajaLeyenda.appendChild(p);\n", "", "R-F"),
    ("la clave se escribe sin su clase, a la letra del pie",
     "            p.className = 'geomapa-pie geomapa-clave';", "            p.className = 'geomapa-pie';", "R-F"),
    ("la letra de la clave baja de 11 px",
     "      font-size: max(11px, 0.8125rem);", "      font-size: max(9px, 0.8125rem);", "R-F"),
    # ------------------------------------------------------------------ R-C
    ("la divergente con centro deja de ser simétrica",
     "      return Math.max(0, Math.min(1, 0.5 + 0.5 * (v - c) / semi));",
     "      return Math.max(0, Math.min(1, 0.5 + (v - c) / semi));", "R-C"),
    ("el centro se aplica también a las paletas secuenciales",
     "      if (!GEOMAPA_DIVERGENTES.includes(paleta)) return null;", "", "R-C"),
    ("la clase que contiene el centro no es el tono neutro",
     "      if (cortes[k - 1] < centro && centro < cortes[k]) return 0.5;", "", "R-C"),
    ("la leyenda de clases ignora el centro",
     "          tClase = k => geomapaTClase(cortes, k, cPol);", "", "R-C"),
    ("el relleno del coropleto ignora el centro",
     "      const centro = cat ? null : geomapaCentro(o.paleta, d, cp);", "      const centro = null;", "R-C"),
    ("las marcas clasificadas ignoran el centro",
     "return geomapaColorClase(o.paleta, d.cortes, d.clase[i], geomapaCentro(o.paleta, d));",
     "return geomapaColorClase(o.paleta, d.cortes, d.clase[i], null);", "R-C"),
    ("la leyenda de las marcas clasificadas ignora el centro",
     "cajas.push(muestra(geomapaColorClase(o.paleta, d.cortes, i + 1, cMarcas),",
     "cajas.push(muestra(geomapaColorClase(o.paleta, d.cortes, i + 1, null),", "R-C"),
    ("la leyenda del ráster ignora el centro",
     "          tClase = k => geomapaTCentrado((cortes[k - 1] + cortes[k]) / 2, cRej, semi);\n", "", "R-C"),
    ("la barra de la leyenda no sigue al mapa",
     "paradas.push(geomapaColor(o.paleta, geomapaTRampa(d, v, o)));", "paradas.push(geomapaColor(o.paleta, i / 20));", "R-C"),
    ("el radio no baja con el número de puntos",
     "      return Math.max(GEOMAPA_RADIO_MIN, GEOMAPA_RADIO * Math.sqrt(GEOMAPA_RADIO_N / n));",
     "      return GEOMAPA_RADIO;", "R-C"),
    ("el radio del dato no manda",
     "      if (typeof d.radio === 'number' && d.radio > 0) return d.radio;", "", "R-C"),
    ("el radio llega al lienzo sin la densidad de la pantalla",
     "Object.assign({ radio: geomapaRadioPuntos(d) * dpr, dpr: dpr }, o)",
     "Object.assign({ radio: geomapaRadioPuntos(d), dpr: dpr }, o)", "R-C"),
    ("los puntos se quedan sin filo",
     "        if (filo && c !== GEOMAPA_APAGADO) ctx.stroke();", "", "R-C"),
    ("los puntos apagados también llevan filo",
     "        if (filo && c !== GEOMAPA_APAGADO) ctx.stroke();", "        if (filo) ctx.stroke();", "R-C"),
    ("los puntos pequeños llevan filo, y su tono se oscurece",
     "      const filo = o.filo !== false && r >= GEOMAPA_FILO_MIN * dprP;", "      const filo = o.filo !== false;", "R-C"),
    ("el coropleto se queda sin silueta",
     "      if (o.silueta === true || (o.silueta !== false && geomapaEsTeselado(d, geom))) {", "      if (false) {", "R-C"),
    ("la silueta se traza también donde las unidades no se tocan",
     "      if (o.silueta === true || (o.silueta !== false && geomapaEsTeselado(d, geom))) {",
     "      if (o.silueta !== false) {", "R-C"),
    ("`silueta: true` no la fuerza",
     "      if (o.silueta === true || (o.silueta !== false && geomapaEsTeselado(d, geom))) {",
     "      if (o.silueta !== false && geomapaEsTeselado(d, geom)) {", "R-C"),
    ("una unidad hace frontera consigo misma",
     "          else if (j !== i && j !== -1) { duenio.set(clave, -1); comunes++; }",
     "          else if (j !== -1) { duenio.set(clave, -1); comunes++; }", "R-C"),
    ("la silueta es de medio píxel y no asoma",
     "        ctx.lineWidth = 2 * dprS;", "        ctx.lineWidth = 0.5;", "R-C"),
    ("la escala logarítmica no se aplica",
     "      if (geomapaEscalaMarcas(d) === 'log') return Math.log(m / r.lo) / Math.log(r.hi / r.lo);", "", "R-C"),
    ("la leyenda calla la escala logarítmica",
     "${log ? ' · escala logarítmica' : ''}", "", "R-C"),
    ("el ráster ignora el centro",
     "            ? geomapaTCentrado(lo + (z / d.zqmax) * (hi - lo), centro, semi)\n            : z / d.zqmax);",
     "            ? z / d.zqmax\n            : z / d.zqmax);", "R-C"),
    # ------------------------------------------------------------------ R-B
    ("la rúbrica deja de leer el nombre que le pasan los talleres",
     "spec.rotuloAnula ||", "spec.letreroAnula ||", "R-B"),
    ("la tabla ordenable vuelve a `toLocaleString('es-CO')`",
     "        const partes = Number(valor).toFixed(d).split('.');\n"
     "        partes[0] = partes[0].replace(/\\B(?=(\\d{3})+(?!\\d))/g, '\\u202f');\n"
     "        return partes.join('.') + (columna.sufijo || '');",
     "        return Number(valor).toLocaleString('es-CO', { minimumFractionDigits: d, maximumFractionDigits: d }) + (columna.sufijo || '');",
     "R-B"),
]


def main() -> int:
    texto = PLANTILLA.read_text(encoding="utf-8")
    print("prueba_plantilla_graficos.py — las reglas compartidas de las gráficas (R-B a R-F)\n")

    fallos = corre(texto)
    if fallos:
        print("  ROJO: la plantilla no cumple sus propias reglas:")
        for f in fallos:
            print(f"   - {f}")
        return 1
    print("  la plantilla, tal como está: todas las comprobaciones en verde")

    malas = 0
    for que, busca, pon, regla in INYECCIONES:
        if texto.count(busca) != 1:
            print(f"  PARADO  «{que}»: el texto a sustituir aparece {texto.count(busca)} veces")
            malas += 1
            continue
        salta = corre(texto.replace(busca, pon))
        # «Cazado» es que salte una comprobación DE SU REGLA, con su frase. Que el
        # JavaScript reviente o que una sección se caiga también deja el arnés en
        # rojo, pero no dice qué se rompió: aquí cuenta como no cazado.
        de_la_regla = [f for f in salta if f.startswith(regla + ":")]
        if de_la_regla:
            print(f"  cazado  {regla} · {que}  ({len(salta)} en rojo: {de_la_regla[0][:70]})")
        else:
            print(f"  NO CAZADO  {regla} · {que}" + (f"  (saltó otra cosa: {salta[0][:120]})" if salta else ""))
            malas += 1

    print()
    if malas:
        print(f"  ROJO: {malas} de {len(INYECCIONES)} defectos inyectados no se cazan.")
        return 1
    print(f"  VERDE: los {len(INYECCIONES)} defectos inyectados se cazan, cada uno por su regla.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
