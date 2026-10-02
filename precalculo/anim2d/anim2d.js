/* =====================================================================
   anim2d.js — la cáscara común de las animaciones 2D

   Material de Estadística Espacial 2026-II (20929). La usan el capítulo 6 (módulo 10,
   `rezago2d.js`) y el capítulo 4 (módulos 8 y 9, `kanillo2d.js`).

   QUÉ ES. Todo lo que dos animaciones 2D tienen en común y ninguna debería
   escribir dos veces: el andamio (pasos, «Reproducir», leyenda, lienzo, mandos,
   lectura), el lienzo con su DPR, el bucle que solo corre cuando algo se mueve,
   las transiciones, el guion, el puntero con captura, el teclado, la pausa fuera
   de pantalla, `prefers-reduced-motion` y la impresión. Cada pieza declara QUÉ
   dibuja y QUÉ cuenta, en un objeto `def`; la cáscara decide cuándo.

   SE EDITA AQUÍ Y NADA MÁS. El capítulo lo inyecta en línea y `comprueba_animaciones.py`
   comprueba que lo que lleva es lo que hay en este archivo.

   DOS CAPAS, Y POR QUÉ.
     1 · `maquina(def, ganchos)`: el estado, las transiciones y el guion. No toca el DOM,
         así que `prueba_anim2d.py` la prueba en Node: que `poner` rechace lo que no es
         un número, que una transición llegue exactamente a su destino, que el guion
         recorra los pasos y que cualquier gesto del usuario lo interrumpa. El repo no
         tiene jsdom; esto es lo más que se puede probar de la capa de interacción sin él.
     2 · `monta(cont, def, opc)`: el DOM, el lienzo y los eventos. Esa capa la cubre solo
         la revisión en el navegador.

   LA INTERFAZ DE LA PIEZA (`def`)
     id, aria, ayuda, ayudaTeclado, pie, sinLienzo   textos (HTML de confianza: es nuestro)
     inicial()                       estado de partida; DEBE llevar `paso: 1`
     normaliza(patch, E)             deja el parche en lo que el estado admite (opcional)
     animables {clave: segundos}     claves numéricas que se interpolan; `V[clave]` es la visible
     pasos [{corto, titulo, texto, estado, tween, pausa}]   `titulo` y `texto` son HTML o `E => HTML`;
                                     `estado` es un parche o `E => parche` (lo que el paso pone depende de dónde se está)
     mandos [{tipo, id, etiqueta, …}]   deslizador | botones | ciclo (el `n` de un ciclo puede ser `E => n`:
                                     cuántos puntos hay depende del patrón que se mira)
     paneles [{id, etiqueta, aria}]     lienzos pequeños de al lado (perfiles, gráficos)
     dibuja(c, E, V)  panel(c, id, E, V)   `c = {ctx, w, h, dpr}`; se dibuja en píxeles CSS
     puntero(ev, E, V, c) → {poner, cursor, captura} | null      (`gestos` decide cuándo se aplica)
     tecla(ev, E, V) → parche | null
     lectura(E) → [[etiqueta, valor], …]       alt(E) → descripción para lectores de pantalla
     sondas [parche, …]              (opcional) estados con que se escribe, oculta, cada leyenda para medir su alto: los
                                     de las variantes más largas del texto, para que la celda no crezca la primera vez

   EL TEXTO DE CADA PASO TIENE QUE SER CIERTO EN CUALQUIER ESTADO, no solo en el que el paso pone: el deslizador y
   el teclado cambian el estado sin cambiar de paso. Las pruebas de cada pieza recorren todos los estados.

   LO QUE ESTA CÁSCARA TODAVÍA NO TIENE, a propósito: el diseño de dos columnas para un lienzo ancho y el
   «modo clase» para diapositivas (letra grande, lienzo a pantalla completa, flechas reenviadas al visor). Las
   columnas de los capítulos no pasan de ~770 px, y CSS que nadie ejercita no se publica sin verificar: lo añadirá
   la animación que lo necesite, con su revisión en el navegador.

   LA API QUE DEVUELVE `monta` está en `CLAVES`, y la versión inerte (`sinAnimacion`,
   cuando no hay lienzo 2D) se fabrica de esa misma lista: así a una no le falta un
   método que la otra tenga.
   ===================================================================== */
(function (global) {
  'use strict';

  const CLAVES = ['destruir', 'ir', 'poner', 'reproducir', 'pausar', 'avanza', 'reinicia', 'estado', 'visual'];
  const PAUSA_PASO = 2.4;       // segundos que el guion se queda en un paso, además de lo que tarde en llegar
  const PASO_TIEMPO = 1 / 30;   // el reloj de `avanza`, que no corre con rAF
  const TOPE_AVANZA = 600;      // `avanza(Infinity)` simula como mucho diez minutos: un guion que no acabe no cuelga la página

  const suave = t => t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;   // easeInOutCubic

  /* ===================================================================
     1 · LA MÁQUINA. Sin DOM.
     =================================================================== */
  function maquina(def, ganchos) {
    ganchos = ganchos || {};
    const E = def.inicial();                 // el estado al que se va
    const V = Object.assign({}, E);          // el que se ve: igual que E salvo las claves en transición
    const animables = def.animables || {};
    const pasos = def.pasos || [];
    const tw = {};                           // clave → { desde, hasta, t, dur }
    const guion = { activo: false, espera: 0 };
    const avisa = () => { if (ganchos.cambia) ganchos.cambia(); };
    const pinta = () => { if (ganchos.pinta) ganchos.pinta(); };

    // Lo que el estado admite de un parche. Una clave que el estado no tiene no entra, y una
    // clave numérica solo admite números finitos: sin esto un NaN llegaba al lienzo y el mapa
    // se quedaba sin color con la consola limpia.
    function limpia(patch) {
      const out = {};
      if (!patch || typeof patch !== 'object') return out;
      for (const k of Object.keys(patch)) {
        if (!(k in E)) continue;
        const v = patch[k];
        if (typeof E[k] === 'number' && !(typeof v === 'number' && isFinite(v))) continue;
        out[k] = v;
      }
      return def.normaliza ? def.normaliza(out, E) : out;
    }

    // `opc.desdeGuion`: la llama el propio guion y no lo interrumpe; cualquier otro `poner` sí.
    // `opc.corte`: sin transición. `opc.dur`: segundos por clave, para este parche.
    function poner(patch, opc) {
      opc = opc || {};
      if (!opc.desdeGuion) pausar();
      const p = limpia(patch);
      let cambio = false;
      for (const k of Object.keys(p)) {
        if (E[k] === p[k] && !(k in tw)) continue;
        cambio = true;
        const dur = opc.dur && opc.dur[k] != null ? opc.dur[k] : animables[k];
        if (k in animables && !ganchos.reducido && !opc.corte && dur > 0 && V[k] !== p[k]) {
          tw[k] = { desde: V[k], hasta: p[k], t: 0, dur };
        } else {
          V[k] = p[k];
          delete tw[k];
        }
        E[k] = p[k];
      }
      if (cambio) { avisa(); pinta(); }
      return cambio;
    }

    function ir(n, opc) {
      const i = Math.round(n);
      if (!(i >= 1 && i <= pasos.length)) return false;
      const p = pasos[i - 1];
      const est = typeof p.estado === 'function' ? p.estado(E) : p.estado;
      poner(Object.assign({ paso: i }, est), Object.assign({ dur: p.tween }, opc));
      return true;
    }

    // Cuánto se queda el guion en el paso `i`: lo que tarden en llegar sus transiciones, y la pausa.
    function espera(i) {
      const p = pasos[i - 1] || {};
      const durs = Object.keys(tw).map(k => tw[k].dur);
      return (durs.length ? Math.max.apply(null, durs) : 0) + (p.pausa != null ? p.pausa : PAUSA_PASO);
    }

    function reproducir() {
      if (guion.activo || !pasos.length) return;
      const desde = E.paso >= 1 && E.paso < pasos.length ? E.paso : 1;
      ir(desde, { desdeGuion: true });
      guion.activo = true;
      guion.espera = espera(desde);
      if (ganchos.guion) ganchos.guion(true);
      pinta();
    }

    function pausar() {
      if (!guion.activo) return;
      guion.activo = false;
      if (ganchos.guion) ganchos.guion(false);
    }

    // Un instante de tiempo. Devuelve si algo sigue en marcha (y hay que pedir otro fotograma).
    function paso(dt) {
      let sigue = false;
      for (const k of Object.keys(tw)) {
        const a = tw[k];
        a.t += dt / a.dur;
        if (a.t >= 1) { V[k] = a.hasta; delete tw[k]; } else { V[k] = a.desde + (a.hasta - a.desde) * suave(a.t); sigue = true; }
      }
      if (guion.activo) {
        guion.espera -= dt;
        if (guion.espera <= 0) {
          if (E.paso < pasos.length) {
            ir(E.paso + 1, { desdeGuion: true });
            guion.espera = espera(E.paso);
          } else {
            pausar();
          }
        }
        sigue = sigue || guion.activo;
      }
      return sigue;
    }

    const activo = () => guion.activo || Object.keys(tw).length > 0;

    // `avanza(seg)`: adelanta el reloj `seg` segundos de golpe. Las capturas y la impresión
    // lo necesitan porque no hay rAF: `avanza(Infinity)` deja el guion en su estado final.
    function avanza(seg) {
      let resto = seg === Infinity ? TOPE_AVANZA : Math.max(0, +seg || 0);
      while (resto > 0 && activo()) {
        const d = Math.min(PASO_TIEMPO, resto);
        paso(d);
        resto -= d;
      }
      if (ganchos.pintaYa) ganchos.pintaYa(); else pinta();
    }

    function reinicia() {
      pausar();
      poner(def.inicial(), { corte: true, desdeGuion: true });
      ir(1, { corte: true, desdeGuion: true });
    }

    return { E, V, poner, ir, reproducir, pausar, paso, avanza, reinicia, activo, guion, espera };
  }

  /* ===================================================================
     2 · EL GESTO. Cuándo se aplica lo que la pieza devuelve del puntero, y si
         interrumpe el guion. Sin DOM, así que se prueba en Node.
     =================================================================== */
  const UMBRAL_TOQUE = 8;    // px: un dedo que se mueve más que esto está desplazando la página, no eligiendo

  // Tres reglas, cada una de un fallo medido en la revisión del rezago (2026-10-02):
  //   · UN TOQUE NO ELIGE AL BAJAR EL DEDO. El navegador todavía no sabe si es un toque o el principio de un
  //     desplazamiento de la página, y elegir al bajar cambiaba el barrio en foco al desplazar con el dedo
  //     encima del mapa (que en el teléfono ocupa casi toda la pantalla). Elige al levantarlo, si no se movió;
  //     `cancela` (pointercancel: el navegador se quedó el gesto) lo anula. Con el ratón, al bajar.
  //   · SALIR DEL LIENZO NO INTERRUMPE EL GUION, como no lo interrumpe pasar por encima. Antes la salida contaba
  //     como un gesto y paraba «Reproducir».
  //   · CON EL DEDO NO HAY «PASAR POR ENCIMA»: sus movimientos solo cuentan si la pieza pidió capturar al bajar
  //     (un arrastre). Así un desplazamiento tampoco pausa el guion.
  // Y una cuarta, de la revisión de K y g (2026-10-02): LO QUE SE ARRASTRA SE APLICA SIN TRANSICIÓN (`corte`). Cada
  // movimiento reiniciaba la transición desde cero con una curva que arranca casi parada, y el círculo se quedaba
  // atrás del dedo (24 → 24.3 con el estado ya en 100). Un clic sí puede animarse: es un salto, no un seguimiento.
  function gestos(puntero) {
    let toque = null;        // un toque que todavía no ha elegido: { res, x, y }
    let arrastre = false;    // la pieza capturó al bajar: los movimientos siguientes son suyos
    const lejos = (ev, p) => Math.hypot(ev.x - p.x, ev.y - p.y) > UMBRAL_TOQUE;
    const con = (res, interrumpe, corte) => res ? Object.assign({}, res, { interrumpe, corte: !!corte }) : null;
    return function (ev, E, V, c) {
      switch (ev.tipo) {
        case 'cancela':
          toque = null; arrastre = false;
          return null;
        case 'abajo': {
          const res = puntero(ev, E, V, c);
          if (res && res.captura) { toque = null; arrastre = true; return con(res, true, true); }
          if (ev.tactil) { toque = res && res.poner ? { res, x: ev.x, y: ev.y } : null; return null; }
          return con(res, true);
        }
        case 'mueve':
          if (toque && lejos(ev, toque)) toque = null;
          if (ev.tactil && !arrastre) return null;
          return con(puntero(ev, E, V, c), arrastre, arrastre);
        case 'arriba': {
          const elegido = toque && !lejos(ev, toque) ? toque.res : null;
          toque = null;
          const res = puntero(ev, E, V, c);
          const eraArrastre = arrastre;
          arrastre = false;
          if (elegido) return con(elegido, true);
          return con(res, eraArrastre, eraArrastre);
        }
        case 'sale':
          toque = null;
          return con(puntero(ev, E, V, c), false);
        default:
          return null;
      }
    };
  }

  // El siguiente o el anterior de un ciclo, dando la vuelta. `m.n` puede depender del estado.
  function cicla(m, E, sentido) {
    const n = typeof m.n === 'function' ? m.n(E) : m.n;
    return (((E[m.id] + sentido) % n) + n) % n;
  }

  /* ===================================================================
     3 · LA API. Una sola lista de claves para la real y la inerte.
     =================================================================== */
  function armaApi(impl) {
    const api = {};
    CLAVES.forEach(k => {
      const d = Object.getOwnPropertyDescriptor(impl, k);
      if (!d) throw new Error('Anim2D: a la API le falta «' + k + '»');
      // Un descriptor no admite `get` y `value` a la vez, ni siquiera con `value: undefined`.
      Object.defineProperty(api, k, d.get ? { get: d.get, enumerable: true, configurable: true }
                                          : { value: d.value, enumerable: true, configurable: true });
    });
    return api;
  }

  function sinAnimacion(cont, causa, def) {
    cont.innerHTML = '<div class="a2d-sin"><strong>' + causa + '</strong> ' + (def.sinLienzo || '') + '</div>';
    const nada = () => {};
    return armaApi({
      destruir() { cont.innerHTML = ''; cont.classList.remove('a2d'); },
      ir: nada, poner: nada, reproducir: nada, pausar: nada, avanza: nada, reinicia: nada,
      get estado() { return {}; }, get visual() { return {}; }
    });
  }

  /* ===================================================================
     4 · ESTILOS. Un <style> propio, con prefijo a2d-, para no pelear con el
         capítulo ni depender de él. Los de cada pieza van en `def.css`.
     CONTRASTE (revisión del 2026-10-02, medido): blanco sobre el naranja #FF6600 da 2,94:1 y no llega al 4,5
     de AA, así que sobre el naranja va la tinta (5,4:1); el anillo de foco va en #b34700 (5,5:1 sobre blanco,
     el naranja daba 2,9 y no llegaba al 3 de un contorno); y el gris de los textos pequeños pasa de #64748b
     (4,45–4,52 sobre la tarjeta: sin margen) a #475569.
     COLORES FORZADOS (Windows, alto contraste): el modo anula los fondos, así que el botón activo no se distinguía
     de los demás (ahora lleva un contorno), y el fondo del lienzo pasaba a negro bajo una letra de dibujo oscura
     que no se leía (el lienzo y los paneles se quedan con su fondo: lo que hay dentro lo dibujamos nosotros).
     LA LEYENDA NO SALTA: las de todos los pasos van apiladas en la misma celda y solo se ve la del paso actual,
     así que la celda mide lo que la más larga. Antes medía lo que la del paso, y en una columna estrecha el mapa
     y los mandos se movían hasta 110 px al cambiar de paso.
     =================================================================== */
  const CSS = `
.a2d{--a2d-tinta:#012820;--a2d-verde:#1a7358;--a2d-naranja:#FF6600;--a2d-foco:#b34700;--a2d-gris:#475569;--a2d-linea:#cbd5e1;
  container-type:inline-size;font-family:'Montserrat','Helvetica Neue',Helvetica,Arial,sans-serif;color:#1e293b;
  font-size:.9375rem;line-height:1.5;text-align:left}
.a2d *,.a2d *::before,.a2d *::after{box-sizing:border-box}
.a2d-rejilla{display:grid;gap:.75rem 1.25rem;grid-template-columns:minmax(0,1fr);
  grid-template-areas:"pasos" "leyenda" "escena" "paneles" "mandos" "lectura" "pie"}
.a2d-pasos{grid-area:pasos;display:flex;flex-wrap:wrap;gap:.4rem;align-items:center}
.a2d-paso{display:inline-flex;align-items:center;gap:.45rem;font:inherit;font-size:.8125rem;font-weight:600;cursor:pointer;
  padding:.3rem .8rem .3rem .35rem;border:1px solid var(--a2d-linea);border-radius:999px;background:#fff;color:var(--a2d-gris);
  transition:background .2s,border-color .2s,color .2s}
.a2d-paso:hover{border-color:var(--a2d-naranja);color:var(--a2d-tinta)}
.a2d-paso:focus-visible,.a2d-btn:focus-visible,.a2d-play:focus-visible{outline:2px solid var(--a2d-foco);outline-offset:2px}
.a2d-num{display:inline-grid;place-items:center;width:1.45rem;height:1.45rem;border-radius:50%;background:#e8eeeb;
  color:var(--a2d-tinta);font-size:.75rem;font-weight:700;font-family:'Fira Code',monospace}
.a2d-paso[aria-current="step"]{background:linear-gradient(135deg,#0f172a 0%,#1e293b 100%);border-color:transparent;color:#fff}
.a2d-paso[aria-current="step"] .a2d-num{background:var(--a2d-naranja);color:var(--a2d-tinta)}
.a2d-play{margin-left:auto;display:inline-flex;align-items:center;gap:.4rem;font:inherit;font-size:.8125rem;font-weight:600;
  cursor:pointer;padding:.3rem .9rem;border:1px solid var(--a2d-naranja);border-radius:999px;background:#fff;color:var(--a2d-foco)}
.a2d-play:hover{background:rgba(255,102,0,.08)}
.a2d-play[data-activo="true"]{background:var(--a2d-naranja);color:var(--a2d-tinta)}
.a2d-leyenda{grid-area:leyenda;display:grid;min-height:6.6em}
.a2d-ley{grid-area:1/1;min-width:0}
.a2d-ley[aria-hidden="true"]{visibility:hidden}
.a2d-leyenda h5{margin:0 0 .25rem;font-size:1.0625rem;font-weight:700;color:var(--a2d-tinta);line-height:1.3}
.a2d-leyenda p{margin:0;color:#334155}
.a2d-leyenda sub,.a2d-leyenda sup{font-size:.75em;line-height:0}
.a2d-escena{grid-area:escena;position:relative;min-width:0}
.a2d-lienzo{position:relative;width:100%;aspect-ratio:4/3;min-height:240px;border:1px solid #e5e7eb;border-radius:.6rem;overflow:hidden;
  background:#fbfdfc;touch-action:pan-y pinch-zoom;user-select:none;-webkit-user-select:none;-webkit-tap-highlight-color:transparent}
.a2d-lienzo canvas{position:absolute;inset:0;width:100%;height:100%;display:block;cursor:default;outline:none}
.a2d-lienzo canvas:focus-visible{outline:2px solid var(--a2d-foco);outline-offset:-3px}
.a2d-ayuda{position:absolute;left:.7rem;top:.55rem;margin:0;font-size:.6875rem;color:var(--a2d-gris);pointer-events:none;max-width:75%}
.a2d-paneles{grid-area:paneles;display:grid;grid-template-columns:repeat(auto-fit,minmax(min(11rem,100%),1fr));gap:.6rem}
.a2d-fig{margin:0;min-width:0}
.a2d-fig figcaption{font-size:.75rem;font-weight:600;color:var(--a2d-gris);margin-bottom:.15rem}
.a2d-panel{display:block;width:100%;height:7rem;border:1px solid #e5e7eb;border-radius:.4rem;background:#fff}
.a2d-mandos{grid-area:mandos;align-self:start;display:flex;flex-wrap:wrap;gap:.75rem 1.5rem;align-items:flex-end}
.a2d-ctl{display:flex;flex-direction:column;gap:.25rem;min-width:min(11rem,100%);flex:1 1 13rem}
.a2d-ctl[hidden],.a2d-grupo[hidden]{display:none}
.a2d-ctl label{display:flex;justify-content:space-between;align-items:center;gap:.5rem;font-size:.8125rem;font-weight:600;color:#374151}
.a2d-ctl output{font-family:'Fira Code',monospace;font-size:.8125rem;font-weight:600;color:#fff;background:var(--a2d-tinta);
  border-radius:.375rem;padding:.1rem .5rem;min-width:3.25rem;text-align:center}
.a2d-ctl input[type=range]{width:100%;accent-color:var(--a2d-naranja);cursor:pointer}
.a2d-grupo{display:flex;flex-direction:column;gap:.3rem}
.a2d-grupo>span{font-size:.8125rem;font-weight:600;color:#374151}
.a2d-botones{display:flex;flex-wrap:wrap;gap:.35rem;align-items:center}
.a2d-btn{font:inherit;font-size:.8rem;font-weight:500;cursor:pointer;padding:.3rem .7rem;border:1px solid #d8e6e0;border-radius:6px;
  background:#fff;color:var(--a2d-tinta);transition:background .15s,border-color .15s}
.a2d-btn:hover{background:rgba(255,102,0,.07)}
.a2d-btn[aria-pressed="true"]{background:var(--a2d-tinta);border-color:var(--a2d-tinta);color:#fff}
.a2d-ciclo-txt{display:inline-flex;align-items:center;padding:0 .4rem;font-family:'Fira Code',monospace;font-size:.8125rem;color:var(--a2d-tinta)}
.a2d-lectura{grid-area:lectura;display:flex;flex-wrap:wrap;gap:.35rem 1.5rem;font-family:'Fira Code',monospace;font-size:.8125rem;color:#1e293b}
.a2d-lectura b{color:var(--a2d-tinta);font-weight:600}
.a2d-lectura .a2d-r{color:var(--a2d-gris);font-family:'Montserrat',sans-serif;font-size:.75rem}
.a2d-pie{grid-area:pie;margin:0;font-size:.75rem;color:var(--a2d-gris)}
.a2d-sr{position:absolute;width:1px;height:1px;margin:-1px;padding:0;border:0;overflow:hidden;clip:rect(0,0,0,0);white-space:nowrap}
.a2d-cargando{margin:0;min-height:14rem;display:grid;place-items:center;text-align:center;padding:1rem;color:#475569;font-size:.875rem;
  border:1px dashed #cbd5e1;border-radius:.6rem;background:#fff}
.a2d-sin{padding:1rem;border:1px dashed #cbd5e1;border-radius:.5rem;background:#fff;color:#475569;font-size:.875rem}
@container (max-width:560px){
  .a2d-paso:not([aria-current="step"]) .a2d-rot{display:none}
  .a2d-paso:not([aria-current="step"]){padding-right:.35rem}
  .a2d-lienzo{aspect-ratio:1/.9}
  .a2d-ayuda{display:none}
}
@media (prefers-reduced-motion:reduce){.a2d *{transition:none!important}}
@media (forced-colors:active){
  .a2d-lienzo,.a2d-panel{forced-color-adjust:none;background:#fff}
  .a2d-paso[aria-current="step"],.a2d-btn[aria-pressed="true"],.a2d-play[data-activo="true"]{outline:3px solid CanvasText;outline-offset:1px}
}
@media print{.a2d-play,.a2d-mandos,.a2d-pasos,.a2d-ayuda{display:none}.a2d{break-inside:avoid}}
`;

  function estilos(doc, extra) {
    if (!doc.getElementById('a2d-css')) {
      const st = doc.createElement('style');
      st.id = 'a2d-css';
      st.textContent = CSS;
      doc.head.appendChild(st);
    }
    if (extra && extra.id && !doc.getElementById(extra.id)) {
      const st = doc.createElement('style');
      st.id = extra.id;
      st.textContent = extra.css;
      doc.head.appendChild(st);
    }
  }

  /* ===================================================================
     5 · EL MONTAJE. Aquí empieza el DOM.
     =================================================================== */
  const esc = s => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/"/g, '&quot;');

  function andamio(def, ID) {
    const pasos = (def.pasos || []).map((p, i) =>
      `<button type="button" class="a2d-paso" data-paso="${i + 1}" aria-label="Paso ${i + 1}: ${esc(p.corto)}">` +
      `<span class="a2d-num">${i + 1}</span><span class="a2d-rot">${p.corto}</span></button>`).join('');
    const mandos = (def.mandos || []).map((m, i) => {
      if (m.tipo === 'deslizador') {
        return `<div class="a2d-ctl" data-mando="${i}"><label for="${ID}-m${i}">${m.etiqueta} <output for="${ID}-m${i}"></output></label>` +
               `<input type="range" id="${ID}-m${i}" min="${m.min}" max="${m.max}" step="${m.paso || 1}" value="${m.min}"></div>`;
      }
      if (m.tipo === 'botones') {
        return `<div class="a2d-grupo" data-mando="${i}"><span>${m.etiqueta}</span><div class="a2d-botones">` +
               m.opciones.map((o, j) => `<button type="button" class="a2d-btn" data-j="${j}" aria-pressed="false">${o[1]}</button>`).join('') +
               '</div></div>';
      }
      return `<div class="a2d-grupo" data-mando="${i}"><span>${m.etiqueta}</span><div class="a2d-botones">` +
             `<button type="button" class="a2d-btn" data-sentido="-1" aria-label="${esc(m.anterior || 'Anterior')}">‹</button>` +
             '<span class="a2d-ciclo-txt" aria-live="polite"></span>' +
             `<button type="button" class="a2d-btn" data-sentido="1" aria-label="${esc(m.siguiente || 'Siguiente')}">›</button></div></div>`;
    }).join('');
    const paneles = (def.paneles || []).map((p, i) =>
      `<figure class="a2d-fig"><figcaption>${p.etiqueta}</figcaption>` +
      `<canvas class="a2d-panel" data-panel="${i}" role="img" aria-label="${esc(p.aria)}"></canvas></figure>`).join('');
    return `
<div class="a2d-rejilla">
  <div class="a2d-pasos" role="group" aria-label="Pasos de la animación">${pasos}
    <button type="button" class="a2d-play" data-activo="false"><span aria-hidden="true">▶</span><span class="a2d-play-txt">Reproducir</span></button>
  </div>
  <div class="a2d-leyenda">${(def.pasos || []).map((p, i) => `<div class="a2d-ley" data-ley="${i + 1}"><h5></h5><p></p></div>` +
    (def.sondas || []).map(() => '<div class="a2d-ley a2d-sonda" aria-hidden="true"><h5></h5><p></p></div>').join('')).join('')}</div>
  <p class="a2d-sr" aria-live="polite" data-anuncio></p>
  <div class="a2d-escena">
    <div class="a2d-lienzo">
      <canvas class="a2d-principal" tabindex="0" role="img" aria-label="${esc(def.aria)}" aria-describedby="${ID}-ayuda ${ID}-estado"></canvas>
      <p class="a2d-ayuda" aria-hidden="true">${def.ayuda || ''}</p>
    </div>
    <p class="a2d-sr" id="${ID}-ayuda">${def.ayudaTeclado || ''}</p>
    <p class="a2d-sr" id="${ID}-estado"></p>
  </div>
  <div class="a2d-paneles">${paneles}</div>
  <div class="a2d-mandos">${mandos}
    <div class="a2d-grupo"><div class="a2d-botones"><button type="button" class="a2d-btn" data-reinicia>Reiniciar</button></div></div>
  </div>
  <div class="a2d-lectura" role="group" aria-label="Lectura numérica"></div>
  <p class="a2d-pie">${def.pie || ''}</p>
</div>`;
  }

  let contador = 0;

  function monta(cont, def, opc) {
    opc = opc || {};
    const doc = cont.ownerDocument;
    const win = doc.defaultView || global;
    const prueba = doc.createElement('canvas');
    if (!prueba.getContext || !prueba.getContext('2d')) return sinAnimacion(cont, 'Este navegador no puede dibujar el lienzo.', def);
    estilos(doc, def.css ? { id: 'a2d-css-' + def.id, css: def.css } : null);

    // La preferencia se lee cada vez que hace falta, no una al montar: activarla con la página abierta debe valer ya.
    const mqReducido = win.matchMedia ? win.matchMedia('(prefers-reduced-motion: reduce)') : null;
    const ID = 'a2d' + (++contador);
    cont.classList.add('a2d');
    cont.innerHTML = andamio(def, ID);
    const $ = s => cont.querySelector(s);

    const lienzo = $('.a2d-principal');
    const ctx = lienzo.getContext('2d');
    const botonPlay = $('.a2d-play');
    const paneles = Array.prototype.slice.call(cont.querySelectorAll('.a2d-panel')).map((cv, i) => ({ cv, ctx: cv.getContext('2d'), def: def.paneles[i] }));
    let vivo = true, visible = true, raf = 0, previo = 0;

    /* ---- la máquina, con los ganchos que la conectan al DOM ---- */
    const M = maquina(def, {
      get reducido() { return !!(mqReducido && mqReducido.matches); },
      cambia: () => sincroniza(),
      pinta: () => pide(),
      pintaYa: () => pintaYa(),
      guion: on => {
        botonPlay.dataset.activo = on ? 'true' : 'false';
        botonPlay.querySelector('.a2d-play-txt').textContent = on ? 'Pausa' : 'Reproducir';
      }
    });

    /* ---- el tamaño: un lienzo con DPR ≤ 2 ---- */
    const geo = { w: 0, h: 0, dpr: 1 };
    function ajustaLienzo(cv, c2) {
      const dpr = Math.min(win.devicePixelRatio || 1, 2);
      const w = cv.clientWidth, h = cv.clientHeight;
      if (!w || !h) return null;
      if (cv.width !== Math.round(w * dpr) || cv.height !== Math.round(h * dpr)) {
        cv.width = Math.round(w * dpr);
        cv.height = Math.round(h * dpr);
      }
      c2.setTransform(dpr, 0, 0, dpr, 0, 0);
      return { ctx: c2, w, h, dpr };
    }

    function pintaYa() {
      if (!vivo) return;
      const c = ajustaLienzo(lienzo, ctx);
      if (c) {
        geo.w = c.w; geo.h = c.h; geo.dpr = c.dpr;
        c.ctx.clearRect(0, 0, c.w, c.h);
        def.dibuja(c, M.E, M.V);
      }
      if (def.panel) {
        paneles.forEach(p => {
          const cp = ajustaLienzo(p.cv, p.ctx);
          if (!cp) return;
          cp.ctx.clearRect(0, 0, cp.w, cp.h);
          def.panel(cp, p.def.id, M.E, M.V);
        });
      }
    }

    /* ---- el bucle, a demanda: solo corre mientras algo se mueve ---- */
    function pide() {
      if (!raf && vivo && visible) raf = win.requestAnimationFrame(fotograma);
    }
    function fotograma(ts) {
      raf = 0;
      if (!vivo || !visible) { previo = 0; return; }
      const dt = previo ? Math.min(0.1, (ts - previo) / 1000) : 1 / 60;
      previo = ts;
      const sigue = M.paso(dt);
      pintaYa();
      if (sigue) pide(); else previo = 0;
    }

    /* ---- lo que depende del estado y no de cada fotograma: textos, mandos, lectura ---- */
    const pasoBotones = Array.prototype.slice.call(cont.querySelectorAll('.a2d-paso'));
    const leyendas = Array.prototype.slice.call(cont.querySelectorAll('.a2d-ley:not(.a2d-sonda)'));
    const sondas = Array.prototype.slice.call(cont.querySelectorAll('.a2d-sonda'));
    const anuncio = $('[data-anuncio]');
    const ctls = Array.prototype.slice.call(cont.querySelectorAll('[data-mando]'));

    // Un texto solo se reescribe si cambió: reescribir el mismo HTML recrea los nodos, y pasar el puntero por encima
    // del mapa llama a esto en cada barrio. Las leyendas de todos los pasos se escriben (están apiladas: la celda mide
    // lo que la más larga), y se anuncia solo el título del paso al que se llega, no cada cambio de su texto.
    const ult = { leyendas: [], sondas: [], paso: null, lectura: null, estado: null };

    // El estado con que se escribe la leyenda de un paso que NO es el actual: el que ese paso pondría. Así la celda
    // mide lo mismo vaya uno al paso que vaya (con el estado actual, la del paso 2 escrita con k = 70 era más larga
    // que escrita con k = 1, y el mapa se movía 24 px al llegar al paso 4).
    function estadoDelPaso(p, E) {
      const est = typeof p.estado === 'function' ? p.estado(E) : (p.estado || {});
      return Object.assign({}, E, def.normaliza ? def.normaliza(Object.assign({}, est), E) : est);
    }

    // LA LEYENDA NO ENCOGE MIENTRAS NO CAMBIE EL ANCHO. Las de todos los pasos van apiladas, pero el texto del paso
    // actual cambia con el estado (una frase condicional, una cifra con más dígitos) y empujaba el mapa dentro de un
    // mismo paso hasta 73 px; arrastrando el borde del círculo, el lienzo se movía bajo el puntero. Ahora la celda
    // guarda el mayor alto que ha tenido, y lo olvida solo cuando cambia el ancho (el ResizeObserver).
    const leyendaCaja = $('.a2d-leyenda');
    let altoLeyenda = 0, anchoLeyenda = 0;
    function fijaLeyenda() {
      const w = leyendaCaja.clientWidth;
      if (w !== anchoLeyenda) { anchoLeyenda = w; altoLeyenda = 0; leyendaCaja.style.minHeight = ''; }
      const h = leyendaCaja.offsetHeight;
      if (h > altoLeyenda) { altoLeyenda = h; leyendaCaja.style.minHeight = h + 'px'; }
    }

    function sincroniza() {
      if (!vivo) return;
      const E = M.E;
      (def.pasos || []).forEach((p, i) => {
        const Ei = i + 1 === E.paso ? E : estadoDelPaso(p, E);
        const tit = typeof p.titulo === 'function' ? p.titulo(Ei) : p.titulo;
        const html = typeof p.texto === 'function' ? p.texto(Ei) : p.texto;
        const el = leyendas[i];
        if (ult.leyendas[i] !== tit + '|' + html) {
          ult.leyendas[i] = tit + '|' + html;
          el.querySelector('h5').textContent = tit;
          el.querySelector('p').innerHTML = html;
        }
        if (i + 1 === E.paso) el.removeAttribute('aria-hidden'); else el.setAttribute('aria-hidden', 'true');
        // las sondas: la misma leyenda escrita con los estados que la alargan, oculta, solo para que la celda mida eso
        (def.sondas || []).forEach((s, k) => {
          const Es = Object.assign({}, Ei, def.normaliza ? def.normaliza(Object.assign({}, s), Ei) : s);
          const ts = typeof p.titulo === 'function' ? p.titulo(Es) : p.titulo, hs = typeof p.texto === 'function' ? p.texto(Es) : p.texto;
          const q = i * def.sondas.length + k, sd = sondas[q];
          if (ult.sondas[q] !== ts + '|' + hs) { ult.sondas[q] = ts + '|' + hs; sd.querySelector('h5').textContent = ts; sd.querySelector('p').innerHTML = hs; }
        });
      });
      if (ult.paso !== E.paso) {
        const p = (def.pasos || [])[E.paso - 1];
        if (ult.paso !== null && p) anuncio.textContent = 'Paso ' + E.paso + ': ' + (typeof p.titulo === 'function' ? p.titulo(E) : p.titulo);
        ult.paso = E.paso;
      }
      pasoBotones.forEach((b, i) => { if (i + 1 === E.paso) b.setAttribute('aria-current', 'step'); else b.removeAttribute('aria-current'); });
      ctls.forEach(el => {
        const m = def.mandos[+el.dataset.mando];
        el.hidden = !!(m.visible && !m.visible(E));
        if (m.tipo === 'deslizador') {
          const inp = el.querySelector('input');
          if (+inp.value !== E[m.id]) inp.value = E[m.id];
          const txt = m.salida ? m.salida(E[m.id], E) : String(E[m.id]);
          el.querySelector('output').textContent = txt;
          inp.setAttribute('aria-valuetext', txt);            // la etiqueta ya la lee el <label>: repetirla la decía dos veces
        } else if (m.tipo === 'botones') {
          el.querySelectorAll('.a2d-btn').forEach(b => b.setAttribute('aria-pressed', String(m.opciones[+b.dataset.j][0] === E[m.id])));
        } else {
          el.querySelector('.a2d-ciclo-txt').textContent = m.texto(E[m.id], E);
        }
      });
      if (def.lectura) {
        const html = def.lectura(E).map(l => `<span><span class="a2d-r">${l[0]}</span> <b>${l[1]}</b></span>`).join('');
        if (ult.lectura !== html) { ult.lectura = html; $('.a2d-lectura').innerHTML = html; }
      }
      if (def.alt) {
        const t = def.alt(E);
        if (ult.estado !== t) { ult.estado = t; $('#' + ID + '-estado').textContent = t; }
      }
      fijaLeyenda();
    }

    /* ---- los mandos: cualquier gesto del usuario interrumpe el guion (lo hace `poner`) ---- */
    ctls.forEach(el => {
      const m = def.mandos[+el.dataset.mando];
      if (m.tipo === 'deslizador') {
        el.querySelector('input').addEventListener('input', e => M.poner({ [m.id]: +e.target.value }, { corte: true }));   // se arrastra: sin transición
      } else if (m.tipo === 'botones') {
        el.addEventListener('click', e => {
          const b = e.target.closest('.a2d-btn');
          if (b) M.poner({ [m.id]: m.opciones[+b.dataset.j][0] });
        });
      } else {
        el.addEventListener('click', e => {
          const b = e.target.closest('.a2d-btn');
          if (b) M.poner({ [m.id]: cicla(m, M.E, +b.dataset.sentido) });
        });
      }
    });
    pasoBotones.forEach(b => b.addEventListener('click', () => { M.pausar(); M.ir(+b.dataset.paso); }));
    botonPlay.addEventListener('click', () => { if (M.guion.activo) M.pausar(); else M.reproducir(); });
    $('[data-reinicia]').addEventListener('click', () => M.reinicia());

    /* ---- el puntero y el teclado sobre el lienzo ---- */
    const gesto = gestos((ev, E, V, c) => def.puntero(ev, E, V, c));
    function despacha(tipo, e) {
      if (!def.puntero) return;
      const r = lienzo.getBoundingClientRect();
      const res = gesto({ tipo, x: e.clientX - r.left, y: e.clientY - r.top, tactil: e.pointerType === 'touch' }, M.E, M.V, geo);
      if (!res) return;
      if (res.cursor !== undefined) lienzo.style.cursor = res.cursor;
      if (res.poner) M.poner(res.poner, { desdeGuion: !res.interrumpe, corte: res.corte });
      if (tipo === 'abajo' && res.captura) {
        try { lienzo.setPointerCapture(e.pointerId); } catch (_) { /* el puntero ya no está activo */ }
      }
    }
    lienzo.addEventListener('pointerdown', e => { if (e.button === 0 || e.pointerType === 'touch') despacha('abajo', e); });
    lienzo.addEventListener('pointermove', e => despacha('mueve', e));
    lienzo.addEventListener('pointerup', e => despacha('arriba', e));
    lienzo.addEventListener('pointercancel', e => despacha('cancela', e));
    lienzo.addEventListener('pointerleave', e => despacha('sale', e));
    lienzo.addEventListener('keydown', e => {
      if (!def.tecla || e.altKey || e.ctrlKey || e.metaKey) return;
      const r = def.tecla({ key: e.key, shiftKey: e.shiftKey }, M.E, M.V);
      if (r) { e.preventDefault(); M.poner(r, { corte: true }); }   // una tecla mantenida es un arrastre: sin transición
    });

    /* ---- tamaño, visibilidad, impresión ---- */
    const ro = win.ResizeObserver ? new win.ResizeObserver(() => { pintaYa(); fijaLeyenda(); }) : null;
    if (ro) { ro.observe($('.a2d-lienzo')); paneles.forEach(p => ro.observe(p.cv)); }
    const io = win.IntersectionObserver ? new win.IntersectionObserver(es => {
      visible = es[es.length - 1].isIntersecting;         // un lote puede traer varias: vale la última
      if (visible) pide(); else M.pausar();
    }) : null;
    if (io) io.observe(cont);
    // Imprimir pone el paso de impresión y, al acabar, devuelve lo que había: quien imprime a mitad de explorar
    // no pierde su estado.
    let antesDeImprimir = null;
    const alImprimir = () => {
      antesDeImprimir = Object.assign({}, M.E);
      M.pausar(); M.ir(def.pasoImpresion || (def.pasos || []).length, { corte: true }); pintaYa();
    };
    const trasImprimir = () => {
      if (!antesDeImprimir) return;
      M.poner(antesDeImprimir, { corte: true, desdeGuion: true });
      antesDeImprimir = null;
      pintaYa();
    };
    win.addEventListener('beforeprint', alImprimir);
    win.addEventListener('afterprint', trasImprimir);

    function destruir() {
      vivo = false;
      if (raf) win.cancelAnimationFrame(raf);
      raf = 0;
      if (ro) ro.disconnect();
      if (io) io.disconnect();
      win.removeEventListener('beforeprint', alImprimir);
      win.removeEventListener('afterprint', trasImprimir);
      cont.innerHTML = '';
      cont.classList.remove('a2d');
    }

    // Si el primer dibujo o la primera lectura fallan, los observadores y los oyentes de impresión ya están puestos:
    // se quitan todos antes de dejar subir el error (quien monta devuelve su texto de reserva). Antes quedaban vivos,
    // también tras cambiar de módulo, y cada impresión lanzaba dos excepciones.
    try {
      sincroniza();
      pide();
    } catch (e) {
      destruir();
      throw e;
    }
    // El lienzo no se redibuja solo cuando llega una fuente: si Montserrat o Fira Code tardan, el primer dibujo
    // sale con la de reserva y se quedaría así.
    if (doc.fonts && doc.fonts.ready) doc.fonts.ready.then(() => { if (vivo) pintaYa(); });
    // Una API destruida no hace nada (antes `ir()` lanzaba un TypeError sobre el DOM ya vacío).
    const vive = f => (...a) => vivo ? f(...a) : undefined;
    return armaApi({
      destruir,
      ir: vive(n => M.ir(n)),
      poner: vive((p, o) => M.poner(p, o)),
      reproducir: vive(M.reproducir),
      pausar: vive(M.pausar),
      avanza: vive(s => M.avanza(s)),
      reinicia: vive(M.reinicia),
      get estado() { return Object.assign({}, M.E); },
      get visual() { return Object.assign({}, M.V); }
    });
  }

  const Anim2D = { monta, estilos, maquina, gestos, cicla, UMBRAL_TOQUE, CLAVES, armaApi, sinAnimacion };
  global.Anim2D = Anim2D;
  if (typeof module === 'object' && module.exports) module.exports = Anim2D;
})(typeof window !== 'undefined' ? window : globalThis);
