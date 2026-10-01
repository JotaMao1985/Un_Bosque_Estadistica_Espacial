/* =====================================================================
   nucleo3d.js — «Del conteo a la superficie»: la estimación por núcleos en 3D

   Material de Estadística Espacial 2026-II (20929). Capítulo 5, módulo 1.

   UN SOLO MOTOR PARA DOS SITIOS. El capítulo lo inyecta en línea
   (`ensambla_cap5.py`) y lo registra como `SIMULADORES['cap5-nucleo3d']`;
   las diapositivas lo cargan desde `Htmls_Espacial/animaciones/nucleo-3d.html`,
   que `construye_nucleo3d.py` estampa desde este mismo archivo. Se edita AQUÍ
   y nada más: los otros dos son artefactos.

   QUÉ CUENTA. El estimador del módulo 1,

         λ̂(u) = (1 / e(u)) · Σᵢ k_σ(u − xᵢ),

   en cinco pasos: los puntos · contar en cajas · una loma por punto · sumar
   las lomas · leer la altura en un sitio. Hay dos mandos que son las dos
   decisiones del módulo 2 —el ancho σ y la forma del núcleo— y la lección
   del módulo 2 sale sola al moverlos: el núcleo casi no cambia el mapa y σ
   lo cambia todo.

   LO QUE NO CUENTA, A PROPÓSITO. La corrección de borde, e(u), es el
   módulo 4: aquí los puntos viven lejos del borde y la ventana es todo el
   suelo, así que e(u) = 1 y el factor desaparece. Decirlo es parte del
   contrato: la pantalla no lo pinta, la leyenda del paso 4 lo avisa.

   LOS PUNTOS SON INVENTADOS. Es una ilustración, no un dato, como el
   «juguete» unidimensional de las diapositivas. Por eso las cifras que
   escribe en pantalla (n, el conteo máximo, el pico, λ̂(u)) las calcula esta
   misma matemática sobre esos puntos: ninguna viene de una fuente y
   ninguna se escribe a mano.

   LA MATEMÁTICA ES PURA Y SE PRUEBA CONTRA R. Las cuatro funciones de peso son
   las de `density.ppp` de spatstat —con la convención que el módulo 2
   advierte: «al mismo σ» es a la misma DESVIACIÓN TÍPICA, no al mismo soporte—,
   y `prueba_nucleo3d.py` las compara con `density()` de R. Las constantes
   (√6, √8, 2) no se recuerdan, se midieron: masa 1 y σ por coordenada en los
   cuatro núcleos (`prueba_nucleo3d.py`, bloque 1).

   LA ESCALA VERTICAL NO SE NORMALIZA POR SUPERFICIE. Es la advertencia del
   módulo 2 («una sola escala de color»): cada superficie contra su propio
   máximo saldría igual de alta y el mapa afirmaría lo contrario de lo que
   demuestra. Alto y color son fijos, y por eso al ensanchar σ la superficie
   baja y se abre: cada loma reparte su peso —un punto— en más terreno.

   Three.js (r149, UMD) llega aparte: `montar(contenedor, { THREE })`.
   ===================================================================== */
(function (global) {
  'use strict';

  /* ===================================================================
     1 · MATEMÁTICA. Sin DOM y sin THREE: es lo que Node prueba contra R.
     =================================================================== */
  // h²/σ² de cada núcleo de soporte finito, MEDIDO en `density.ppp` (el
  // soporte de «σ = 1» llega a √6, √8 y 2). Una sola vez, porque el radio con
  // el que se dibuja la loma y el que usa la función de peso tienen que ser el
  // mismo: escritos por separado, cambiar uno dejaba al otro mintiendo.
  const H2 = { epanechnikov: 6, quartic: 8, disc: 4 };

  // k(r², σ): la densidad radial de cada núcleo, que integra 1 sobre el plano
  // y tiene desviación típica σ en cada coordenada. `alcance` es el radio del
  // círculo que se dibuja alrededor de un sitio (el soporte, en los tres que
  // lo tienen; 2σ en el gaussiano, que no); `corte` es hasta dónde se dibuja
  // una loma (el gaussiano se trunca a 4σ, donde vale el 0.03 % de su pico).
  const NUCLEOS = {
    gaussian: {
      nombre: 'Gaussiano',
      alcance: s => 2 * s, corte: s => 4 * s,
      k: (r2, s) => Math.exp(-r2 / (2 * s * s)) / (2 * Math.PI * s * s)
    },
    epanechnikov: {
      nombre: 'Epanechnikov',
      alcance: s => Math.sqrt(H2.epanechnikov) * s, corte: s => Math.sqrt(H2.epanechnikov) * s,
      k: (r2, s) => { const h2 = H2.epanechnikov * s * s; return r2 < h2 ? 2 / (Math.PI * h2) * (1 - r2 / h2) : 0; }
    },
    quartic: {
      nombre: 'Cuártico',
      alcance: s => Math.sqrt(H2.quartic) * s, corte: s => Math.sqrt(H2.quartic) * s,
      k: (r2, s) => {
        const h2 = H2.quartic * s * s;
        if (r2 >= h2) return 0;
        const u = 1 - r2 / h2;
        return 3 / (Math.PI * h2) * u * u;
      }
    },
    disc: {
      nombre: 'Disco',
      alcance: s => Math.sqrt(H2.disc) * s, corte: s => Math.sqrt(H2.disc) * s,
      k: (r2, s) => { const h2 = H2.disc * s * s; return r2 < h2 ? 1 / (Math.PI * h2) : 0; }
    }
  };
  const ORDEN_NUCLEOS = ['gaussian', 'epanechnikov', 'quartic', 'disc'];

  // La ventana es el cuadrado [-V, V]². Sin corrección de borde: ver arriba.
  const V = 5;
  const CELDA = 2.5;                  // la rejilla del paso 2: 4 × 4 celdas cuando no está desplazada
  const DESPLAZA_MAX = CELDA / 2;     // «moverla media celda cambia los conteos»
  const SIGMA = { min: 0.5, max: 2.2, ini: 0.8 };
  // Unidades de mundo que alcanza el pico del GAUSSIANO con el σ más estrecho: ese pico
  // fija la escala vertical. No es el más alto posible: el disco, con ese σ, llega a
  // una cuarta parte más (su altura es 1/(π h²), sin cola que la reparta). El encuadre
  // de la cámara usa `techo`, que sí cubre el peor caso de los cuatro núcleos.
  const ALTO_MAX = 4.2;

  // Diecinueve posiciones inventadas: tres grupos, dos puntos pegados a una
  // línea de la rejilla y cuatro sueltos. Con la rejilla en su sitio cada grupo
  // cabe en UNA celda (5, 5 y 3 puntos) y al desplazarla la línea los parte:
  // es el efecto de la rejilla que el paso 2 quiere enseñar. Los grupos son lo
  // bastante abiertos para que un σ estrecho los resuelva en puntos sueltos y
  // uno ancho los funda en una sola loma. Ninguno queda a menos de 0.7 del borde.
  const PATRON = [
    [-4.3, 2.0], [-3.4, 2.2], [-2.9, 1.4], [-4.0, 0.7], [-3.3, 1.0],
    [0.3, -0.6], [1.9, -0.4], [1.2, -1.4], [0.4, -2.0], [2.1, -1.9],
    [3.0, 3.1], [3.9, 3.8], [3.5, 2.8],
    [2.3, -3.5], [2.7, -3.2],
    [0.4, 0.8], [-1.4, -2.9], [-1.8, 3.4], [4.3, -0.4]
  ];

  function intensidadEn(nucleo, pts, s, x, y) {
    const k = NUCLEOS[nucleo].k;
    let t = 0;
    for (let i = 0; i < pts.length; i++) {
      const dx = x - pts[i][0], dy = y - pts[i][1];
      t += k(dx * dx + dy * dy, s);
    }
    return t;
  }

  // Los aportes de cada punto a un sitio: k_σ(u − xᵢ), uno por punto.
  function aportes(nucleo, pts, s, x, y) {
    const k = NUCLEOS[nucleo].k;
    return pts.map(p => { const dx = x - p[0], dy = y - p[1]; return k(dx * dx + dy * dy, s); });
  }

  // Intensidad sobre una rejilla de n × n vértices que cubre la ventana,
  // fila a fila desde y = −V. Devuelve el máximo.
  function superficie(nucleo, pts, s, n, salida) {
    const k = NUCLEOS[nucleo].k, paso = 2 * V / (n - 1);
    let max = 0;
    for (let j = 0; j < n; j++) {
      const y = -V + j * paso;
      for (let i = 0; i < n; i++) {
        const x = -V + i * paso;
        let t = 0;
        for (let q = 0; q < pts.length; q++) {
          const dx = x - pts[q][0], dy = y - pts[q][1];
          t += k(dx * dx + dy * dy, s);
        }
        salida[j * n + i] = t;
        if (t > max) max = t;
      }
    }
    return max;
  }

  // El test de cuadrantes con la rejilla desplazada `d` en x y en y. Las celdas
  // de la orilla quedan recortadas por la ventana y se dividen por su área
  // RECORTADA, que es lo que hace `quadratcount` con una ventana que no es una
  // caja. Medio paso de celda es el tope: más allá aparecerían astillas.
  //
  // UN PUNTO SOBRE UNA LÍNEA tiene que ir siempre a la misma celda. El patrón
  // tiene coordenadas de un decimal y el deslizador avanza de 0.05 en 0.05, así
  // que en 11 de sus 26 posiciones algún punto cae EXACTAMENTE sobre una arista.
  // Dos cosas lo deciden y las dos se fijan aquí: (1) la convención de los
  // extremos, que es la de `quadratcount` —intervalos (a, b]—, y (2) el ruido de
  // coma flotante: las aristas NO se acumulan sumando (0.3 + 2.5 + 2.5 daba
  // 0.2999999999999998 y el punto en 0.3 se iba a la celda de la derecha), se
  // calculan desde la base y se redondean a nueve decimales.
  function cuadrantes(pts, d) {
    const base = -V - CELDA + d, aristas = [];
    const arista = k => +(base + k * CELDA).toFixed(9) + 0;       // «+ 0» borra el −0
    for (let k = 0; base + k * CELDA < V - 1e-9; k++) aristas.push(arista(k));
    aristas.push(arista(aristas.length));
    const dentro = (v, a, b, primera) => (primera ? v >= a : v > a) && v <= b;
    const celdas = [];
    for (let j = 0; j + 1 < aristas.length; j++) {
      for (let i = 0; i + 1 < aristas.length; i++) {
        const x0 = Math.max(aristas[i], -V), x1 = Math.min(aristas[i + 1], V);
        const y0 = Math.max(aristas[j], -V), y1 = Math.min(aristas[j + 1], V);
        if (x1 - x0 < 1e-9 || y1 - y0 < 1e-9) continue;
        let n = 0;
        for (const p of pts) {
          if (dentro(p[0], aristas[i], aristas[i + 1], i === 0) && dentro(p[1], aristas[j], aristas[j + 1], j === 0)) n++;
        }
        celdas.push({ i, j, x0, x1, y0, y1, n, area: (x1 - x0) * (y1 - y0) });
      }
    }
    return { celdas, aristas };
  }

  // Las constantes de escala SE DERIVAN de la matemática, no se escriben: el
  // alto (4.2) lo alcanza el gaussiano con el σ más estrecho; el color satura
  // donde el σ de partida deja sus picos; y `techo` es el pico más alto que
  // puede dibujarse con cualquier núcleo y cualquier σ, para que la cámara
  // encuadre SIEMPRE lo mismo y no «respire» al mover los mandos.
  function escalas(pts) {
    const n = 61, tmp = new Float32Array(n * n);
    const pico = (k, s) => superficie(k, pts, s, n, tmp);
    const alto = ALTO_MAX / pico('gaussian', SIGMA.min);
    const techo = alto * Math.max.apply(null, ORDEN_NUCLEOS.map(k => pico(k, SIGMA.min)));
    return { alto, color: 1.25 * pico('gaussian', SIGMA.ini), techo };
  }

  // Paleta secuencial «naranja» de la casa (GEOMAPA_PALETAS.naranja).
  const PALETA = ['#fff0e0', '#ffd2a3', '#ffab5c', '#ff8420', '#d95f00', '#8a3d00'];
  const hexRgb = h => [1, 3, 5].map(i => parseInt(h.slice(i, i + 2), 16) / 255);
  const PALETA_RGB = PALETA.map(hexRgb);
  function colorDe(t, fuera) {
    const q = Math.min(1, Math.max(0, t)) * (PALETA_RGB.length - 1);
    const i = Math.min(PALETA_RGB.length - 2, Math.floor(q)), f = q - i;
    for (let c = 0; c < 3; c++) fuera[c] = PALETA_RGB[i][c] * (1 - f) + PALETA_RGB[i + 1][c] * f;
    return fuera;
  }

  const MATEMATICA = {
    NUCLEOS, ORDEN_NUCLEOS, PATRON, V, CELDA, DESPLAZA_MAX, SIGMA,
    intensidadEn, aportes, superficie, cuadrantes, escalas, colorDe, PALETA
  };

  /* ===================================================================
     2 · TEXTOS. Los pasos de la animación y lo que dice cada uno.
     =================================================================== */
  const PASOS = [
    { corto: 'Los puntos',
      titulo: 'Partimos de posiciones, no de una superficie',
      texto: 'Cada punto es una sede: es lo único que tenemos. Un solo número —<em>n</em> entre el área de la ventana— dice cuántas hay por unidad de área, pero no <em>dónde</em>: es el plano gris. Para saber dónde hay más hay que estimar la intensidad <em>en cada sitio</em>.' },
    { corto: 'Contar en cajas',
      titulo: 'Contar en celdas ya es estimar la intensidad local',
      texto: 'La altura de cada barra es el conteo de su celda dividido por su área. Desplaza la rejilla: los puntos no se mueven y los conteos sí. Un punto al otro lado de una línea no le aporta nada a la celda vecina, aunque esté pegado a ella.' },
    { corto: 'Una loma por punto',
      titulo: 'En vez de una caja, cada punto reparte su peso alrededor',
      texto: 'Cada punto levanta una loma centrada en él: su peso <em>k</em><sub>σ</sub>(<em>u</em> − <em>x</em><sub><em>i</em></sub>) decae con la distancia. Todas encierran lo mismo —un punto—, así que al abrir σ bajan y se ensanchan. Mueve σ y cambia de núcleo.' },
    { corto: 'Sumar las lomas',
      titulo: 'El mapa es la suma de todas las lomas',
      texto: 'En cada sitio se suman las alturas de las lomas: λ̂(<em>u</em>) = Σ <em>k</em><sub>σ</sub>(<em>u</em> − <em>x</em><sub><em>i</em></sub>). Donde se solapan, la superficie sube. La escala vertical no cambia con σ: al ensanchar, cada loma reparte su peso en más terreno y el mapa baja.' },
    { corto: 'Leer un sitio',
      titulo: 'La altura en u es una suma de pesos',
      texto: 'Arrastra la esfera naranja. Cada hilo une <em>u</em> con un punto y su grosor es el peso <em>k</em><sub>σ</sub>(<em>u</em> − <em>x</em><sub><em>i</em></sub>); la columna apila esos pesos y su altura es λ̂(<em>u</em>). Fuera del círculo, un punto pesa poco o nada.' }
  ];

  const AYUDA = 'Arrastra el fondo para girar · arrastra un punto para moverlo';
  const AYUDA_TECLADO = 'Con el lienzo enfocado, las flechas giran la vista; en el paso 5, Mayús con las flechas mueve el sitio u. ' +
                        'Los mandos de debajo cambian σ, el núcleo y la rejilla.';
  let contador = 0;                  // para que cada instancia tenga sus propios id

  /* ===================================================================
     3 · ESTILOS. Un <style> propio, con prefijo n3d-, para no pelear con el
         host (el capítulo) ni depender de él (la página de las diapositivas).
     =================================================================== */
  const CSS = `
.n3d{--n3d-tinta:#012820;--n3d-verde:#1a7358;--n3d-naranja:#FF6600;--n3d-gris:#475569;--n3d-linea:#cbd5e1;
  container-type:inline-size;font-family:'Montserrat','Helvetica Neue',Helvetica,Arial,sans-serif;color:#1e293b;
  font-size:.9375rem;line-height:1.5;text-align:left}
.n3d *,.n3d *::before,.n3d *::after{box-sizing:border-box}
.n3d-rejilla{display:grid;gap:.75rem 1.25rem;grid-template-columns:minmax(0,1fr);
  grid-template-areas:"pasos" "leyenda" "escena" "mandos" "lectura" "pie"}
.n3d-pasos{grid-area:pasos;display:flex;flex-wrap:wrap;gap:.4rem;align-items:center}
.n3d-paso{display:inline-flex;align-items:center;gap:.45rem;font:inherit;font-size:.8125rem;font-weight:600;cursor:pointer;
  padding:.3rem .8rem .3rem .35rem;border:1px solid var(--n3d-linea);border-radius:999px;background:#fff;color:var(--n3d-gris);
  transition:background .2s,border-color .2s,color .2s}
.n3d-paso:hover{border-color:var(--n3d-naranja);color:var(--n3d-tinta)}
.n3d-paso:focus-visible,.n3d-btn:focus-visible,.n3d-nuc:focus-visible,.n3d-play:focus-visible{outline:2px solid var(--n3d-naranja);outline-offset:2px}
.n3d-num{display:inline-grid;place-items:center;width:1.45rem;height:1.45rem;border-radius:50%;background:#e8eeeb;
  color:var(--n3d-tinta);font-size:.75rem;font-weight:700;font-family:'Fira Code',monospace}
.n3d-paso[aria-current="step"]{background:linear-gradient(135deg,#0f172a 0%,#1e293b 100%);border-color:transparent;color:#fff}
.n3d-paso[aria-current="step"] .n3d-num{background:var(--n3d-naranja);color:#fff}
.n3d-play{margin-left:auto;display:inline-flex;align-items:center;gap:.4rem;font:inherit;font-size:.8125rem;font-weight:600;
  cursor:pointer;padding:.3rem .9rem;border:1px solid var(--n3d-naranja);border-radius:999px;background:#fff;color:#b34700}
.n3d-play:hover{background:rgba(255,102,0,.08)}
.n3d-play[data-activo="true"]{background:var(--n3d-naranja);color:#fff}
.n3d-leyenda{grid-area:leyenda;min-height:6.6em}
.n3d-leyenda h5{margin:0 0 .25rem;font-size:1.0625rem;font-weight:700;color:var(--n3d-tinta);line-height:1.3}
.n3d-leyenda p{margin:0;color:#334155}
.n3d-leyenda sub{font-size:.75em;line-height:0}
.n3d-escena{grid-area:escena;position:relative;min-width:0}
.n3d-lienzo{position:relative;aspect-ratio:16/10;min-height:260px;border:1px solid #e5e7eb;border-radius:.6rem;overflow:hidden;
  background:radial-gradient(120% 95% at 50% 18%,#ffffff 0%,#f4f8f6 55%,#e4ece8 100%);touch-action:pan-y pinch-zoom;
  user-select:none;-webkit-user-select:none;-webkit-tap-highlight-color:transparent}
.n3d-lienzo canvas{position:absolute;inset:0;width:100%;height:100%;display:block;cursor:grab;outline:none}
.n3d-lienzo canvas:focus-visible{outline:2px solid var(--n3d-naranja);outline-offset:-3px}
.n3d-lienzo canvas.n3d-agarra{cursor:grabbing}
.n3d-lienzo canvas.n3d-sobre{cursor:pointer}
.n3d-etiquetas{position:absolute;inset:0;pointer-events:none;overflow:hidden;font-family:'Fira Code',monospace}
.n3d-et{position:absolute;transform:translate(-50%,-50%);font-size:.75rem;font-weight:600;color:#012820;white-space:nowrap;
  text-shadow:0 0 3px #fff,0 0 3px #fff,0 0 6px #fff}
.n3d-et.n3d-nota{font-family:'Montserrat',sans-serif;font-size:.6875rem;font-weight:600;color:#475569;transform:translate(-50%,-100%)}
.n3d-ayuda{position:absolute;left:.7rem;bottom:.55rem;margin:0;font-size:.6875rem;color:#64748b;pointer-events:none;
  transition:opacity .6s;max-width:75%}
.n3d-ayuda.n3d-oculta{opacity:0}
.n3d-panel{margin-top:.75rem;padding:.55rem .7rem;border:1px solid #d6e2dc;border-radius:.5rem;background:rgba(255,255,255,.94);font-size:.75rem}
.n3d-panel[hidden]{display:none}
.n3d-panel h6{margin:0 0 .3rem;font-size:.6875rem;font-weight:700;letter-spacing:.04em;text-transform:uppercase;color:var(--n3d-gris)}
.n3d-ap{display:grid;grid-template-columns:2.6rem 1fr 2.6rem;align-items:center;gap:.4rem;margin:.18rem 0;font-family:'Fira Code',monospace}
.n3d-ap sub{font-size:.7em;line-height:0}
.n3d-ap-barra{height:.5rem;border-radius:.25rem;background:#eef2f0;overflow:hidden}
.n3d-ap-barra i{display:block;height:100%;background:var(--n3d-verde);border-radius:.25rem}
.n3d-ap b{color:var(--n3d-tinta);font-weight:600;text-align:right}
.n3d-ap-total{margin-top:.35rem;padding-top:.3rem;border-top:1px solid #d6e2dc;display:flex;justify-content:space-between;
  font-family:'Fira Code',monospace;font-weight:700;color:#b34700}
.n3d-mandos{grid-area:mandos;align-self:start;display:flex;flex-wrap:wrap;gap:.75rem 1.5rem;align-items:flex-end}
.n3d-ctl{display:flex;flex-direction:column;gap:.25rem;min-width:11rem;flex:1 1 13rem}
.n3d-ctl[hidden]{display:none}
.n3d-ctl label{display:flex;justify-content:space-between;align-items:center;gap:.5rem;font-size:.8125rem;font-weight:600;color:#374151}
.n3d-ctl output{font-family:'Fira Code',monospace;font-size:.8125rem;font-weight:600;color:#fff;background:var(--n3d-tinta);
  border-radius:.375rem;padding:.1rem .5rem;min-width:3.25rem;text-align:center}
.n3d-ctl input[type=range]{width:100%;accent-color:var(--n3d-naranja);cursor:pointer}
.n3d-grupo{display:flex;flex-direction:column;gap:.3rem}
.n3d-grupo[hidden]{display:none}
.n3d-grupo>span{font-size:.8125rem;font-weight:600;color:#374151}
.n3d-botones{display:flex;flex-wrap:wrap;gap:.35rem}
.n3d-nuc,.n3d-btn{font:inherit;font-size:.8rem;font-weight:500;cursor:pointer;padding:.3rem .7rem;border:1px solid #d8e6e0;border-radius:6px;
  background:#fff;color:var(--n3d-tinta);transition:background .15s,border-color .15s}
.n3d-nuc:hover,.n3d-btn:hover{background:rgba(255,102,0,.07)}
.n3d-nuc[aria-pressed="true"],.n3d-btn[aria-pressed="true"]{background:var(--n3d-tinta);border-color:var(--n3d-tinta);color:#fff}
.n3d-perfilcaja{margin-top:.75rem;display:flex;flex-direction:column;gap:.3rem}
.n3d-perfilcaja[hidden]{display:none}
.n3d-perfilcaja>span{font-size:.8125rem;font-weight:600;color:#374151}
.n3d-perfil{display:block;width:13rem;height:4.75rem;border:1px solid #e5e7eb;border-radius:.4rem;background:#fff}
.n3d-lectura{grid-area:lectura;align-self:start;display:flex;flex-wrap:wrap;gap:.35rem 1.5rem;font-family:'Fira Code',monospace;font-size:.8125rem;color:#1e293b}
.n3d-lectura b{color:var(--n3d-tinta);font-weight:600}
.n3d-lectura .n3d-r{color:#64748b;font-family:'Montserrat',sans-serif;font-size:.75rem}
.n3d-pie{grid-area:pie;margin:0;font-size:.75rem;color:#64748b}
.n3d-sr{position:absolute;width:1px;height:1px;margin:-1px;padding:0;border:0;overflow:hidden;clip:rect(0,0,0,0);white-space:nowrap}
.n3d-cargando{margin:0;min-height:14rem;display:grid;place-items:center;text-align:center;padding:1rem;color:#64748b;font-size:.875rem;
  border:1px dashed #cbd5e1;border-radius:.6rem;background:#fff}
.n3d-sin-webgl{padding:1rem;border:1px dashed #cbd5e1;border-radius:.5rem;background:#fff;color:#475569;font-size:.875rem}
@container (min-width:920px){
  .n3d-rejilla{grid-template-columns:minmax(0,1.7fr) minmax(0,1fr);
    grid-template-areas:"pasos pasos" "escena leyenda" "escena mandos" "escena lectura" "pie pie";grid-template-rows:auto auto auto 1fr auto;align-content:start;align-items:start}
  /* las tarjetas flotan sobre el lienzo; su sitio es el del lienzo y no el de la rejilla */
  .n3d-panel{position:absolute;top:.6rem;right:.6rem;margin:0;z-index:2;width:min(15.5rem,46%);pointer-events:none}
  .n3d-perfilcaja{position:absolute;bottom:.6rem;right:.6rem;margin:0;z-index:2;padding:.35rem .5rem .45rem;border:1px solid #d6e2dc;border-radius:.5rem;background:rgba(255,255,255,.92);pointer-events:none}
  .n3d-perfilcaja>span{font-size:.6875rem;color:#475569}
  .n3d-perfil{width:11rem;height:4rem;border:0}
  .n3d-lienzo{aspect-ratio:auto;min-height:0;height:clamp(380px,54cqw,620px)}
  .n3d-mandos{flex-direction:column;align-items:stretch}
  .n3d-ctl{flex:0 0 auto}
  .n3d-leyenda{min-height:0}
}
@container (max-width:560px){
  .n3d-paso:not([aria-current="step"]) .n3d-rot{display:none}
  .n3d-paso:not([aria-current="step"]){padding-right:.35rem}
  .n3d-lienzo{aspect-ratio:1/.8}
  .n3d-ayuda{display:none}
}
.n3d-clase{font-size:1rem}
.n3d-clase .n3d-rejilla{gap:.6rem 1.1rem}
.n3d-clase .n3d-leyenda h5{font-size:1.2rem;margin-bottom:.2rem}
.n3d-clase .n3d-leyenda p{font-size:1rem;line-height:1.42}
.n3d-clase .n3d-paso,.n3d-clase .n3d-play{font-size:.95rem}
.n3d-clase .n3d-ctl label,.n3d-clase .n3d-grupo>span{font-size:.95rem}
.n3d-clase .n3d-nuc,.n3d-clase .n3d-btn{font-size:.9rem;padding:.28rem .6rem}
.n3d-clase .n3d-ctl output{font-size:.9rem}
.n3d-clase .n3d-lectura{font-size:.9rem}
.n3d-clase .n3d-num{width:1.65rem;height:1.65rem;font-size:.85rem}
.n3d-clase .n3d-et{font-size:.95rem}
.n3d-clase .n3d-pie{display:none}
.n3d-clase .n3d-lienzo{height:calc(100vh - 3.9rem)}
.n3d-clase .n3d-panel{font-size:.85rem;width:min(16rem,46%)}
.n3d-clase .n3d-perfil{width:13rem;height:4.6rem}
.n3d-clase .n3d-mandos{gap:.55rem 1rem}
@media (prefers-reduced-motion:reduce){.n3d *{transition:none!important}}
@media print{.n3d-play,.n3d-mandos,.n3d-pasos,.n3d-ayuda{display:none}}
`;

  function inyectaCSS(doc) {
    if (doc.getElementById('n3d-css')) return;
    const st = doc.createElement('style');
    st.id = 'n3d-css';
    st.textContent = CSS;
    doc.head.appendChild(st);
  }

  /* ===================================================================
     4 · EL MONTAJE: interfaz + escena. `montar` devuelve { destruir, ir }.
     =================================================================== */
  const HTML = `
<div class="n3d-rejilla">
  <div class="n3d-pasos" role="group" aria-label="Pasos de la animación">
    ${PASOS.map((p, i) => `<button type="button" class="n3d-paso" data-paso="${i + 1}" aria-label="Paso ${i + 1}: ${p.corto}"><span class="n3d-num">${i + 1}</span><span class="n3d-rot">${p.corto}</span></button>`).join('')}
    <button type="button" class="n3d-play" data-activo="false"><span class="n3d-play-ico" aria-hidden="true">▶</span><span class="n3d-play-txt">Reproducir</span></button>
  </div>
  <div class="n3d-leyenda" aria-live="polite"><h5></h5><p></p></div>
  <div class="n3d-escena">
    <div class="n3d-lienzo">
      <canvas role="img" aria-describedby="@@ID@@-ayuda" aria-label="Escena tridimensional con ${PATRON.length} puntos inventados sobre un plano, y la superficie de intensidad que resulta de sumar una loma por punto. El texto y la lectura numérica dicen lo mismo con palabras."></canvas>
      <div class="n3d-etiquetas" aria-hidden="true"></div>
      <p class="n3d-ayuda" aria-hidden="true">${AYUDA}</p>
    </div>
    <p class="n3d-sr" id="@@ID@@-ayuda">${AYUDA_TECLADO}</p>
    <div class="n3d-panel" aria-hidden="true" hidden><h6>Aportes a λ̂(u)</h6><div class="n3d-ap-lista"></div><div class="n3d-ap-total"><span>λ̂(u)</span><span class="n3d-ap-suma"></span></div></div>
    <div class="n3d-perfilcaja" data-ctl="perfil" hidden><span>Los cuatro núcleos, al mismo σ</span><canvas class="n3d-perfil" role="img" aria-label="Perfil radial de los cuatro núcleos con la misma desviación típica: el gaussiano decae sin cortarse; el de Epanechnikov, el cuártico y el disco tienen soporte finito."></canvas></div>
  </div>
  <div class="n3d-mandos">
    <div class="n3d-ctl" data-ctl="rejilla" hidden><label>Desplazar la rejilla <output></output></label><input type="range" min="0" max="${DESPLAZA_MAX}" step="0.05" value="0" aria-label="Desplazar la rejilla"></div>
    <div class="n3d-ctl" data-ctl="sigma" hidden><label>Ancho de banda σ <output></output></label><input type="range" min="${SIGMA.min}" max="${SIGMA.max}" step="0.05" value="${SIGMA.ini}" aria-label="Ancho de banda sigma"></div>
    <div class="n3d-grupo" data-ctl="nucleo" hidden><span>Núcleo</span><div class="n3d-botones">
      ${ORDEN_NUCLEOS.map(k => `<button type="button" class="n3d-nuc" data-nucleo="${k}" aria-pressed="false" title="${k}">${NUCLEOS[k].nombre}</button>`).join('')}
    </div></div>
    <div class="n3d-grupo"><span>Vista</span><div class="n3d-botones">
      <button type="button" class="n3d-btn" data-vista="inclinada" aria-pressed="true">Inclinada</button>
      <button type="button" class="n3d-btn" data-vista="cenital" aria-pressed="false">Desde arriba</button>
      <button type="button" class="n3d-btn" data-reinicia>Reiniciar</button>
    </div></div>
  </div>
  <div class="n3d-lectura" role="group" aria-label="Lectura numérica de la escena"></div>
  <p class="n3d-pie">Ilustración con ${PATRON.length} puntos inventados, no un dato. Aquí no se corrige el borde: con σ grande parte de cada loma queda fuera de la ventana, y de eso trata el módulo 4.</p>
</div>`;

  const clamp = (x, a, b) => Math.min(b, Math.max(a, x));
  const suave = t => t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;   // easeInOutCubic
  const sale = t => 1 - Math.pow(1 - t, 3);                                          // easeOutCubic
  const f2 = x => x.toFixed(2);

  // Sin WebGL (o sin three.js) el texto de los cinco pasos sigue ahí: es el mismo
  // contenido sin el lienzo, y la prosa del módulo lo repite. El objeto que
  // devuelve tiene la MISMA interfaz que el real, inerte, para que quien lo use
  // (el capítulo, las pruebas, las diapositivas) no tenga que preguntar cuál es.
  function sinAnimacion(cont, causa) {
    cont.innerHTML = '<div class="n3d-sin-webgl"><strong>' + causa + '</strong> ' +
      'Dice lo mismo que la fórmula del módulo 1: cada punto levanta una loma de ancho σ, y la superficie de intensidad es la suma de todas las lomas. ' +
      'El módulo 2 mide qué pasa al cambiar la forma de la loma (casi nada) y su ancho (todo).</div>';
    const nada = () => {};
    return { destruir() { cont.innerHTML = ''; cont.classList.remove('n3d', 'n3d-clase'); }, ir: nada, poner: nada, reproducir: nada,
             pausar: nada, avanza: nada, fijaVista: nada, estado: {}, _: {} };
  }

  function montar(cont, opc) {
    opc = opc || {};
    const THREE = opc.THREE || global.THREE;
    const doc = cont.ownerDocument;
    const clase = opc.modo === 'clase';
    inyectaCSS(doc);
    cont.classList.add('n3d');
    if (clase) cont.classList.add('n3d-clase');

    // El contexto de la sonda se SUELTA en el acto: el navegador solo aguanta unos dieciséis vivos,
    // y cada vez que se vuelve a este módulo se monta de nuevo.
    const pruebaGl = doc.createElement('canvas').getContext('webgl2') || doc.createElement('canvas').getContext('webgl');
    if (pruebaGl) { const ext = pruebaGl.getExtension('WEBGL_lose_context'); if (ext) ext.loseContext(); }
    if (!THREE || !pruebaGl) {
      return sinAnimacion(cont, !THREE ? 'No se pudo cargar la biblioteca gráfica (three.js).' : 'Esta animación necesita WebGL y no está disponible.');
    }

    cont.innerHTML = HTML.replace(/@@ID@@/g, 'n3d' + (++contador));
    const $ = s => cont.querySelector(s);
    const $$ = s => Array.from(cont.querySelectorAll(s));
    const reducido = !!(global.matchMedia && global.matchMedia('(prefers-reduced-motion: reduce)').matches);

    /* ---------------- estado ---------------- */
    const ESC = escalas(PATRON);
    const N = PATRON.length;
    const puntos = PATRON.map(p => p.slice());
    const estado = { paso: 1, sigma: SIGMA.ini, nucleo: 'gaussian', desp: 0, sonda: [-2.5, 1.0] };
    // Lo que se anima (cada valor viaja hacia su objetivo con una curva suave).
    const A = { cajas: 0, lomasH: 0, lomasO: 0.85, suma: 0, sonda: 0, media: 0, az: 0, pol: 0.12, r: 1 };
    const OBJETIVO = [
      null,
      { cajas: 0, lomasH: 0, lomasO: 0.85, suma: 0, sonda: 0, media: 1 },
      { cajas: 1, lomasH: 0, lomasO: 0.85, suma: 0, sonda: 0, media: 0 },
      { cajas: 0, lomasH: 1, lomasO: 0.85, suma: 0, sonda: 0, media: 0 },
      { cajas: 0, lomasH: 1, lomasO: 0.22, suma: 1, sonda: 0, media: 0 },
      { cajas: 0, lomasH: 1, lomasO: 0.22, suma: 1, sonda: 1, media: 0 }
    ];
    const VISTAS = { inclinada: { az: 0.62, pol: 1.1, r: 1 }, cenital: { az: 0, pol: 0.03, r: 1 } };
    let vista = 'inclinada';
    let sucio = true, vivo = true, pendiente = false, visible = true, ultimo = 0, raf = 0;
    let arrastre = null, orbita = null, tocoAlgo = false;
    const tweens = [];

    function tween(clave, hasta, dur, retraso) {
      for (let i = tweens.length - 1; i >= 0; i--) if (tweens[i].k === clave) tweens.splice(i, 1);
      if (reducido || dur <= 0) { A[clave] = hasta; return; }
      tweens.push({ k: clave, a: A[clave], b: hasta, t: -(retraso || 0), dur });
    }
    // Orbitar con el ratón o las flechas toma el mando de la CÁMARA; los demás tweens (las barras que
    // suben, las lomas que crecen, la suma) son de la escena y tienen que terminar.
    function sinTweensDeCamara() {
      for (let i = tweens.length - 1; i >= 0; i--) if (tweens[i].k === 'az' || tweens[i].k === 'pol' || tweens[i].k === 'r') tweens.splice(i, 1);
    }
    function avanzaTweens(dt) {
      for (let i = tweens.length - 1; i >= 0; i--) {
        const w = tweens[i];
        w.t += dt;
        if (w.t < 0) continue;
        const p = clamp(w.t / w.dur, 0, 1);
        A[w.k] = w.a + (w.b - w.a) * suave(p);
        if (p >= 1) tweens.splice(i, 1);
      }
      return tweens.length > 0;
    }

    /* ---------------- escena ---------------- */
    const lienzo = $('.n3d-lienzo canvas');
    const caja = $('.n3d-lienzo');
    let cw = Math.max(1, caja.clientWidth), ch = Math.max(1, caja.clientHeight);   // el tamaño se lee UNA vez (ajustaTamano), no en cada cuadro
    // La sonda de arriba pasó y aun así el constructor puede lanzar (límite de contextos, atributos que el equipo no da).
    let renderer;
    try {
      renderer = new THREE.WebGLRenderer({ canvas: lienzo, antialias: true, alpha: true, preserveDrawingBuffer: true });
    } catch (_) {
      return sinAnimacion(cont, 'No se pudo iniciar WebGL.');
    }
    renderer.setClearColor(0x000000, 0);
    renderer.setPixelRatio(Math.min(global.devicePixelRatio || 1, 2));
    const escena = new THREE.Scene();
    const camara = new THREE.PerspectiveCamera(32, 1.6, 0.1, 120);
    escena.add(new THREE.HemisphereLight(0xffffff, 0xdfe7e3, 0.95));
    const sol = new THREE.DirectionalLight(0xffffff, 0.75);
    sol.position.set(-6, 11, 5);
    escena.add(sol);

    const desechables = [];            // todo lo que hay que liberar al destruir
    const reg = o => { desechables.push(o); return o; };
    const Z = y => -y;                 // la y de los datos es la −z del mundo: el «norte» queda arriba

    // El suelo: papel con una cuadrícula casi invisible y el marco de la ventana.
    function texturaSuelo() {
      const c = doc.createElement('canvas'); c.width = c.height = 1024;
      const g = c.getContext('2d');
      g.fillStyle = '#fdfcf8'; g.fillRect(0, 0, 1024, 1024);
      g.strokeStyle = '#e4ebe7'; g.lineWidth = 2;
      for (let i = 0; i <= 10; i++) {
        const t = i * 102.4;
        g.beginPath(); g.moveTo(t, 0); g.lineTo(t, 1024); g.stroke();
        g.beginPath(); g.moveTo(0, t); g.lineTo(1024, t); g.stroke();
      }
      const tx = new THREE.CanvasTexture(c);
      tx.anisotropy = 4;
      return reg(tx);
    }
    const suelo = new THREE.Mesh(reg(new THREE.PlaneGeometry(2 * V, 2 * V)),
      reg(new THREE.MeshBasicMaterial({ map: texturaSuelo() })));
    suelo.rotation.x = -Math.PI / 2;
    escena.add(suelo);
    const sombra = new THREE.Mesh(reg(new THREE.PlaneGeometry(2 * V + 1.6, 2 * V + 1.6)),
      reg(new THREE.MeshBasicMaterial({ color: 0xcfdad5, transparent: true, opacity: 0.28, depthWrite: false })));
    sombra.rotation.x = -Math.PI / 2; sombra.position.y = -0.06;
    escena.add(sombra);
    const marco = new THREE.LineLoop(
      reg(new THREE.BufferGeometry().setFromPoints([[-V, -V], [V, -V], [V, V], [-V, V]].map(p => new THREE.Vector3(p[0], 0.004, Z(p[1]))))),
      reg(new THREE.LineBasicMaterial({ color: 0x012820, transparent: true, opacity: 0.55 })));
    escena.add(marco);

    // La alfombra: el mapa de calor visto desde arriba, pintado sobre el suelo.
    // Es la misma superficie, y es lo que el estudiante ve en el módulo 2.
    const NG = 96;
    const valores = new Float32Array(NG * NG);
    const cAlfombra = doc.createElement('canvas'); cAlfombra.width = cAlfombra.height = NG;
    const gAlfombra = cAlfombra.getContext('2d');
    const imgAlfombra = gAlfombra.createImageData(NG, NG);
    const texAlfombra = reg(new THREE.CanvasTexture(cAlfombra));
    texAlfombra.magFilter = THREE.LinearFilter; texAlfombra.minFilter = THREE.LinearFilter;
    const alfombra = new THREE.Mesh(reg(new THREE.PlaneGeometry(2 * V, 2 * V)),
      reg(new THREE.MeshBasicMaterial({ map: texAlfombra, transparent: true, opacity: 0, depthWrite: false,
                                         polygonOffset: true, polygonOffsetFactor: -1, polygonOffsetUnits: -1 })));
    alfombra.rotation.x = -Math.PI / 2; alfombra.position.y = 0.003;
    escena.add(alfombra);

    // La superficie λ̂: una malla de NG × NG vértices coloreada por su altura.
    const grupoSup = new THREE.Group();
    escena.add(grupoSup);
    const geoSup = reg(new THREE.BufferGeometry());
    const pos = new Float32Array(NG * NG * 3), col = new Float32Array(NG * NG * 3);
    for (let j = 0; j < NG; j++) for (let i = 0; i < NG; i++) {
      const q = (j * NG + i) * 3;
      pos[q] = -V + 2 * V * i / (NG - 1); pos[q + 2] = Z(-V + 2 * V * j / (NG - 1));
    }
    const idx = new Uint16Array((NG - 1) * (NG - 1) * 6);
    for (let j = 0, k = 0; j < NG - 1; j++) for (let i = 0; i < NG - 1; i++) {
      const a = j * NG + i, b = a + 1, c = a + NG, d = c + 1;
      // el orden hace que la cara mire hacia arriba con z = −y
      idx[k++] = a; idx[k++] = b; idx[k++] = c; idx[k++] = b; idx[k++] = d; idx[k++] = c;
    }
    const atrPos = new THREE.BufferAttribute(pos, 3), atrCol = new THREE.BufferAttribute(col, 3);
    geoSup.setAttribute('position', atrPos); geoSup.setAttribute('color', atrCol);
    geoSup.setIndex(new THREE.BufferAttribute(idx, 1));
    // Transparente DESDE EL PRINCIPIO, con opacidad 1: three compila el shader de un
    // material opaco con `OPAQUE` (alfa forzado a 1), y volverlo transparente en caliente
    // no lo recompila. La sonda del paso 5 baja la opacidad y no se vería.
    const matSup = reg(new THREE.MeshStandardMaterial({ vertexColors: true, roughness: 0.92, metalness: 0,
      transparent: true, polygonOffset: true, polygonOffsetFactor: 1, polygonOffsetUnits: 1 }));
    const malla = new THREE.Mesh(geoSup, matSup);
    malla.renderOrder = 1;
    grupoSup.add(malla);
    // La red de la superficie: cada 4 vértices, compartiendo el atributo de posición.
    const lin = [];
    for (let j = 0; j < NG; j += 4) for (let i = 0; i < NG - 1; i++) lin.push(j * NG + i, j * NG + i + 1);
    for (let i = 0; i < NG; i += 4) for (let j = 0; j < NG - 1; j++) lin.push(j * NG + i, (j + 1) * NG + i);
    const geoRed = reg(new THREE.BufferGeometry());
    geoRed.setAttribute('position', atrPos);
    geoRed.setIndex(new THREE.BufferAttribute(new Uint16Array(lin), 1));
    const red = new THREE.LineSegments(geoRed, reg(new THREE.LineBasicMaterial({ color: 0x7a3a0a, transparent: true, opacity: 0.16 })));
    grupoSup.add(red);

    // El plano de la media: «un solo número para toda la ventana».
    const media = new THREE.Mesh(reg(new THREE.PlaneGeometry(2 * V, 2 * V)),
      reg(new THREE.MeshBasicMaterial({ color: 0x5e8c7c, transparent: true, opacity: 0, side: THREE.DoubleSide, depthWrite: false })));
    media.rotation.x = -Math.PI / 2;
    escena.add(media);
    const bordeMedia = new THREE.LineLoop(
      reg(new THREE.BufferGeometry().setFromPoints([[-V, -V], [V, -V], [V, V], [-V, V]].map(p => new THREE.Vector3(p[0], 0, Z(p[1]))))),
      reg(new THREE.LineBasicMaterial({ color: 0x2f5a4a, transparent: true, opacity: 0 })));
    escena.add(bordeMedia);

    // Las lomas: una malla polar por núcleo, a σ = 1; cada punto la escala a su σ.
    const geoLoma = {}, matLoma = {};
    function crearLoma(nombre) {
      const R = NUCLEOS[nombre].corte(1), NR = 40, NA = 56, k = NUCLEOS[nombre].k;
      const pico = k(0, 1), p = [0, pico, 0], q = [];
      // Cada vértice lleva su color y su opacidad según la altura RELATIVA a su
      // pico: más profundo y opaco arriba, claro y transparente en el pie. Así
      // 19 lomas solapadas se leen como relieve y no como 19 discos, y la forma
      // del núcleo se ve aunque, a σ grande, la loma sea casi plana.
      const vc = h => {
        const t = Math.min(1, Math.max(0, h / pico)), u = Math.min(1, t / 0.22);
        return [0.45 - 0.40 * Math.pow(t, 0.7), 0.75 - 0.37 * Math.pow(t, 0.7), 0.66 - 0.37 * Math.pow(t, 0.7), u * u * (3 - 2 * u)];
      };
      const c = vc(pico);
      for (let a = 1; a <= NR + 1; a++) {
        const r = a <= NR ? R * a / NR : R, h = a <= NR ? k(r * r, 1) : 0;
        for (let b = 0; b < NA; b++) {
          const t = 2 * Math.PI * b / NA;
          p.push(r * Math.cos(t), h, r * Math.sin(t));
          c.push.apply(c, vc(h));
        }
      }
      for (let b = 0; b < NA; b++) q.push(0, 1 + b, 1 + (b + 1) % NA);
      for (let a = 0; a < NR; a++) for (let b = 0; b < NA; b++) {
        const u0 = 1 + a * NA + b, u1 = 1 + a * NA + (b + 1) % NA, v0 = u0 + NA, v1 = u1 + NA;
        q.push(u0, v0, u1, u1, v0, v1);
      }
      const g = reg(new THREE.BufferGeometry());
      g.setAttribute('position', new THREE.Float32BufferAttribute(p, 3));
      g.setAttribute('color', new THREE.Float32BufferAttribute(c, 4));
      g.setIndex(q);
      g.computeVertexNormals();
      return g;
    }
    ORDEN_NUCLEOS.forEach(nombre => {
      geoLoma[nombre] = crearLoma(nombre);
      matLoma[nombre] = reg(new THREE.MeshStandardMaterial({ vertexColors: true, roughness: 0.7, metalness: 0, transparent: true,
        opacity: 0.8, depthWrite: false, side: THREE.DoubleSide, flatShading: nombre === 'disc' }));
    });
    const lomas = puntos.map(() => {
      const m = new THREE.Mesh(geoLoma.gaussian, matLoma.gaussian);
      m.renderOrder = 2;
      escena.add(m);
      return m;
    });

    // Las barras del paso 2 (a lo más 25 celdas).
    const matBarra = [];
    const geoBarra = reg(new THREE.BoxGeometry(1, 1, 1)); geoBarra.translate(0, 0.5, 0);
    const geoBorde = reg(new THREE.EdgesGeometry(geoBarra));
    const matBorde = reg(new THREE.LineBasicMaterial({ color: 0x4a2400, transparent: true, opacity: 0.4 }));
    const barras = [];
    for (let i = 0; i < 25; i++) {
      const m = reg(new THREE.MeshStandardMaterial({ color: 0xffab5c, roughness: 0.8, metalness: 0, transparent: true, opacity: 0.8 }));
      matBarra.push(m);
      const b = new THREE.Mesh(geoBarra, m);
      b.add(new THREE.LineSegments(geoBorde, matBorde));
      b.visible = false;
      escena.add(b);
      barras.push(b);
    }
    // Un solo atributo, del tamaño máximo (a lo más cuatro aristas interiores con CELDA = 2.5 en una
    // ventana de 10; sobra margen), que se reescribe: crear uno nuevo en cada recálculo dejaba un
    // buffer de GPU huérfano por cada movimiento del deslizador.
    const geoRej = reg(new THREE.BufferGeometry());
    const attrRej = new THREE.BufferAttribute(new Float32Array(8 * 12), 3);
    geoRej.setAttribute('position', attrRej);
    geoRej.setDrawRange(0, 0);
    const lineasRej = new THREE.LineSegments(geoRej, reg(new THREE.LineBasicMaterial({ color: 0x012820, transparent: true, opacity: 0 })));
    lineasRej.frustumCulled = false;      // la esfera envolvente se calcularía sobre ceros
    escena.add(lineasRej);

    // Los puntos: una esfera, su tallo y su pie en el suelo. Y una esfera de
    // captura más grande, invisible, que es la que recibe el puntero.
    const geoEsf = reg(new THREE.SphereGeometry(0.17, 20, 14));
    const matPunto = reg(new THREE.MeshStandardMaterial({ color: 0x012820, roughness: 0.35, metalness: 0.1 }));
    const geoPie = reg(new THREE.CircleGeometry(0.2, 20)); geoPie.rotateX(-Math.PI / 2);
    const matPie = reg(new THREE.MeshBasicMaterial({ color: 0x012820, transparent: true, opacity: 0.22, depthWrite: false }));
    const geoCaptura = reg(new THREE.SphereGeometry(0.42, 8, 6));
    const matCaptura = reg(new THREE.MeshBasicMaterial({ visible: false }));
    const matTallo = reg(new THREE.LineBasicMaterial({ color: 0x012820, transparent: true, opacity: 0.5 }));
    const marcas = puntos.map(() => {
      const g = new THREE.Group();
      const esfera = new THREE.Mesh(geoEsf, matPunto);
      const pie = new THREE.Mesh(geoPie, matPie); pie.position.y = 0.006;
      const tallo = new THREE.Line(reg(new THREE.BufferGeometry().setFromPoints([new THREE.Vector3(), new THREE.Vector3(0, 1, 0)])), matTallo);
      const cap = new THREE.Mesh(geoCaptura, matCaptura);
      g.add(esfera, tallo, cap);
      escena.add(g);
      escena.add(pie);
      return { g, esfera, tallo, cap, pie, pieOwn: pie };
    });

    // La sonda del paso 5: círculo de alcance, hilos, columna apilada y asa.
    const grupoSonda = new THREE.Group(); grupoSonda.visible = false;
    escena.add(grupoSonda);
    const aro = new THREE.Mesh(reg(new THREE.RingGeometry(0.975, 1, 64).rotateX(-Math.PI / 2)),
      reg(new THREE.MeshBasicMaterial({ color: 0xFF6600, transparent: true, opacity: 0.85, depthWrite: false, side: THREE.DoubleSide })));
    const disco = new THREE.Mesh(reg(new THREE.CircleGeometry(1, 64).rotateX(-Math.PI / 2)),
      reg(new THREE.MeshBasicMaterial({ color: 0xFF6600, transparent: true, opacity: 0.09, depthWrite: false, side: THREE.DoubleSide })));
    aro.position.y = disco.position.y = 0.01;
    grupoSonda.add(aro, disco);
    const geoSeg = reg(new THREE.CylinderGeometry(0.13, 0.13, 1, 16)); geoSeg.translate(0, 0.5, 0);
    const matSeg = [0x1a7358, 0x2f9a78].map(c => reg(new THREE.MeshStandardMaterial({ color: c, roughness: 0.6, metalness: 0 })));
    const segmentos = [];
    for (let i = 0; i < N; i++) { const m = new THREE.Mesh(geoSeg, matSeg[i % 2]); m.visible = false; grupoSonda.add(m); segmentos.push(m); }
    const asa = new THREE.Mesh(reg(new THREE.SphereGeometry(0.24, 24, 16)),
      reg(new THREE.MeshStandardMaterial({ color: 0xFF6600, roughness: 0.4, metalness: 0.05 })));
    const capAsa = new THREE.Mesh(reg(new THREE.SphereGeometry(0.5, 8, 6)), matCaptura);
    asa.add(capAsa);
    grupoSonda.add(asa);
    const hilos = [];               // un objeto Line por punto: el grosor se simula con cilindros finos
    const geoHilo = reg(new THREE.CylinderGeometry(1, 1, 1, 8)); geoHilo.translate(0, 0.5, 0); geoHilo.rotateX(Math.PI / 2);
    const matHilo = reg(new THREE.MeshBasicMaterial({ color: 0x0b3d2e, transparent: true, opacity: 0.9, depthWrite: false }));
    for (let i = 0; i < N; i++) {
      const h = new THREE.Mesh(geoHilo, matHilo); h.visible = false; h.position.y = 0.02; grupoSonda.add(h); hilos.push(h);
    }

    /* ---------------- etiquetas HTML sobre la escena ---------------- */
    const capaEt = $('.n3d-etiquetas');
    // Escribir en el DOM solo cuando algo cambia: el bucle pasa por aquí en cada cuadro, y cada
    // asignación (aunque el valor sea el mismo) es una mutación que el host —el capítulo carga
    // Tailwind, que observa el documento— tiene que procesar.
    const muestra = (el, v) => { const d = v ? '' : 'none'; if (el._d !== d) { el._d = d; el.style.display = d; } };
    const escribe = (el, t) => { if (el._t !== t) { el._t = t; el.textContent = t; } };
    const etBarras = [];
    for (let i = 0; i < 25; i++) { const e = doc.createElement('div'); e.className = 'n3d-et'; muestra(e, false); capaEt.appendChild(e); etBarras.push(e); }
    const etMedia = doc.createElement('div'); etMedia.className = 'n3d-et n3d-nota'; muestra(etMedia, false);
    etMedia.innerHTML = 'n / |W| — un solo número'; capaEt.appendChild(etMedia);
    const etU = doc.createElement('div'); etU.className = 'n3d-et'; muestra(etU, false); etU.textContent = 'u'; etU.style.fontStyle = 'italic';
    etU.style.fontFamily = "'Montserrat',sans-serif"; etU.style.fontSize = '.9rem'; capaEt.appendChild(etU);

    /* ---------------- recálculo (cuando cambia algo de los datos) ---------------- */
    let pico = 0, cuad = null, ap = null, mediaAlto = 0;
    const tmpC = [0, 0, 0];
    function recalcula() {
      const nuc = estado.nucleo, s = estado.sigma;
      pico = superficie(nuc, puntos, s, NG, valores);
      for (let q = 0; q < NG * NG; q++) {
        pos[q * 3 + 1] = valores[q] * ESC.alto;
        colorDe(valores[q] / ESC.color, tmpC);
        col[q * 3] = tmpC[0]; col[q * 3 + 1] = tmpC[1]; col[q * 3 + 2] = tmpC[2];
        const p = q * 4, c = colorDe(Math.pow(valores[q] / ESC.color, 0.9), tmpC);
        imgAlfombra.data[p] = c[0] * 255; imgAlfombra.data[p + 1] = c[1] * 255; imgAlfombra.data[p + 2] = c[2] * 255; imgAlfombra.data[p + 3] = 255;
      }
      atrPos.needsUpdate = true; atrCol.needsUpdate = true;
      geoSup.computeVertexNormals(); geoSup.computeBoundingSphere();
      // La alfombra se dibuja con la fila y = −V abajo: el lienzo 2D va de arriba a abajo.
      for (let j = 0; j < NG; j++) {
        const fila = NG - 1 - j;
        for (let i = 0; i < NG; i++) {
          const a = (fila * NG + i) * 4, b = (j * NG + i) * 4;
          if (j < fila) for (let c = 0; c < 4; c++) { const t = imgAlfombra.data[a + c]; imgAlfombra.data[a + c] = imgAlfombra.data[b + c]; imgAlfombra.data[b + c] = t; }
        }
      }
      gAlfombra.putImageData(imgAlfombra, 0, 0); texAlfombra.needsUpdate = true;

      mediaAlto = (N / ((2 * V) * (2 * V))) * ESC.alto;
      media.position.y = mediaAlto; bordeMedia.position.y = mediaAlto;

      cuad = cuadrantes(puntos, estado.desp);
      recalculaBarras();

      lomas.forEach((l, i) => {
        l.geometry = geoLoma[nuc]; l.material = matLoma[nuc];
        l.position.set(puntos[i][0], 0, Z(puntos[i][1]));
      });
      recalculaSonda();
      pintaPerfil();
      pintaLectura();
    }

    // Las barras guardan su altura final; la animación solo las escala.
    function recalculaBarras() {
      const celdas = cuad.celdas;
      barras.forEach((b, i) => {
        const c = celdas[i];
        if (!c) { b.visible = false; b.userData.c = null; return; }
        b.userData.c = c;
        b.userData.h = (c.n / c.area) * ESC.alto;
        b.position.set((c.x0 + c.x1) / 2, 0, Z((c.y0 + c.y1) / 2));
        b.userData.w = c.x1 - c.x0; b.userData.d = c.y1 - c.y0;
        colorDe((c.n / c.area) / ESC.color, tmpC);
        matBarra[i].color.setRGB(tmpC[0], tmpC[1], tmpC[2]);
      });
      const ps = [];
      for (const a of cuad.aristas) {
        if (a > -V && a < V) { ps.push(a, 0.01, Z(-V), a, 0.01, Z(V)); ps.push(-V, 0.01, Z(a), V, 0.01, Z(a)); }
      }
      attrRej.array.set(ps.slice(0, attrRej.array.length));
      attrRej.needsUpdate = true;
      geoRej.setDrawRange(0, Math.min(ps.length, attrRej.array.length) / 3);
    }

    function recalculaSonda() {
      const [x, y] = estado.sonda;
      ap = aportes(estado.nucleo, puntos, estado.sigma, x, y);
    }

    /* ---------------- aplicar lo animado a la escena ---------------- */
    const v3 = new THREE.Vector3();
    function alturaEn(x, y) {   // altura de la superficie bajo (x, y), por interpolación bilineal de la malla
      const fx = clamp((x + V) / (2 * V) * (NG - 1), 0, NG - 1.001), fy = clamp((y + V) / (2 * V) * (NG - 1), 0, NG - 1.001);
      const i = Math.floor(fx), j = Math.floor(fy), tx = fx - i, ty = fy - j;
      const a = valores[j * NG + i], b = valores[j * NG + i + 1], c = valores[(j + 1) * NG + i], d = valores[(j + 1) * NG + i + 1];
      return ((a * (1 - tx) + b * tx) * (1 - ty) + (c * (1 - tx) + d * tx) * ty) * ESC.alto;
    }

    function aplica() {
      const suma = suave(clamp(A.suma, 0, 1));
      grupoSup.visible = suma > 0.002;
      grupoSup.scale.y = Math.max(suma, 0.001);
      alfombra.material.opacity = suma * (0.9 - 0.45 * A.sonda);
      // con la sonda activa la superficie se vuelve de cristal: la columna y los hilos viven DENTRO de ella
      matSup.opacity = 1 - 0.45 * A.sonda;
      media.material.opacity = 0.38 * A.media; bordeMedia.material.opacity = 0.9 * A.media;
      media.visible = bordeMedia.visible = A.media > 0.002;

      // lomas: cada una crece con su retraso, de una en una
      const s = estado.sigma;
      lomas.forEach((l, i) => {
        const p = sale(clamp(A.lomasH * 1.9 - 0.9 * i / N, 0, 1));
        l.visible = p > 0.002;
        l.scale.set(s, Math.max(p * ESC.alto / (s * s), 1e-4), s);
      });
      // la loma se diluye al abrir σ: su opacidad sigue su altura real, no solo su forma
      matLoma[estado.nucleo].opacity = A.lomasO * clamp(NUCLEOS[estado.nucleo].k(0, s) / NUCLEOS[estado.nucleo].k(0, SIGMA.ini), 0.3, 1);

      // barras: crecen en oleada desde la esquina
      const mostrarEt = A.cajas > 0.6;
      barras.forEach((b, i) => {
        const c = b.userData.c;
        if (!c) { b.visible = false; muestra(etBarras[i], false); return; }
        const p = sale(clamp(A.cajas * 1.7 - 0.7 * i / 25, 0, 1));
        b.visible = p > 0.002;
        b.scale.set(Math.max(b.userData.w - 0.06, 0.01), Math.max(b.userData.h * p, 1e-4), Math.max(b.userData.d - 0.06, 0.01));
        muestra(etBarras[i], mostrarEt && c.n > 0);
        escribe(etBarras[i], String(c.n));
      });
      lineasRej.material.opacity = 0.35 * clamp(A.cajas * 1.5, 0, 1);
      lineasRej.visible = A.cajas > 0.002;

      // puntos: sobre el suelo, o sobre la superficie cuando existe
      const [px, py] = estado.sonda;
      puntos.forEach((p, i) => {
        const m = marcas[i];
        const propia = NUCLEOS[estado.nucleo].k(0, s) * ESC.alto * sale(clamp(A.lomasH * 1.9 - 0.9 * i / N, 0, 1));
        const alto = 0.17 + Math.max(propia, suma * alturaEn(p[0], p[1]));
        m.g.position.set(p[0], alto, Z(p[1]));
        m.esfera.position.y = 0;
        m.tallo.scale.y = 1; m.tallo.position.y = -alto; m.tallo.scale.set(1, alto, 1);
        m.pieOwn.position.set(p[0], 0.006, Z(p[1]));
      });

      // sonda
      const hs = A.sonda;
      grupoSonda.visible = hs > 0.002;
      if (grupoSonda.visible) {
        const al = NUCLEOS[estado.nucleo].alcance(estado.sigma);
        aro.scale.set(al, 1, al); disco.scale.set(al, 1, al);
        aro.material.opacity = 0.85 * hs; disco.material.opacity = 0.09 * hs;
        grupoSonda.position.set(px, 0, Z(py));
        // columna: los aportes de mayor a menor, apilados
        const orden = ap.map((w, i) => i).sort((a, b) => ap[b] - ap[a]);
        let h = 0;
        segmentos.forEach(sg => { sg.visible = false; });
        orden.forEach((i, rank) => {
          const w = ap[i] * ESC.alto * suma;
          if (ap[i] * ESC.alto < 0.004) return;
          const sg = segmentos[rank];
          sg.visible = true; sg.material = matSeg[rank % 2];
          sg.position.set(0, h, 0);
          sg.scale.set(hs, Math.max(w, 1e-4), hs);
          h += w;
        });
        asa.position.set(0, h + 0.1, 0); asa.scale.setScalar(hs);
        // hilos: del sitio a cada punto, con el grosor del peso
        const wmax = Math.max.apply(null, ap) || 1;
        puntos.forEach((p, i) => {
          const hl = hilos[i], dx = (p[0] - px), dz = Z(p[1]) - Z(py), L = Math.hypot(dx, dz);
          const t = ap[i] / wmax;
          if (t < 0.01 || L < 1e-6) { hl.visible = false; return; }
          hl.visible = true;
          hl.position.set(0, 0.025, 0);
          hl.scale.set(0.035 + 0.11 * Math.sqrt(t), 0.035 + 0.11 * Math.sqrt(t), L);
          hl.rotation.set(0, Math.atan2(dx, dz), 0);
        });
        // los puntos que pesan se oscurecen; los que no, se apagan
        puntos.forEach((p, i) => { marcas[i].esfera.scale.setScalar(1); });
      }
    }

    /* ---------------- cámara ---------------- */
    // La distancia se calcula para que la ventana ENTERA quepa, sea cual sea el formato del
    // lienzo (una diapositiva, el capítulo en el teléfono), la dirección desde la que se mire
    // y el núcleo o el σ elegidos; `A.r` es solo un factor de zoom. Una estimación ortográfica
    // da el punto de partida y la perspectiva lo corrige: la esquina más cercana se ve más
    // grande de lo que dice esa cuenta (a 1.6 de proporción se salía por abajo), así que se
    // proyectan las ocho esquinas de la caja —el suelo y el techo del relieve— y se escala la
    // distancia hasta que la más exterior cae al 93 % del semilado (el margen de siempre).
    const objetivo = new THREE.Vector3(), tmpP = new THREE.Vector3();
    const esquinas = [];
    [-V, V].forEach(x => [-V, V].forEach(z => [0, ESC.techo].forEach(y => esquinas.push(new THREE.Vector3(x, y, z)))));
    function ponCamara(r) {
      camara.position.set(objetivo.x + r * Math.sin(A.pol) * Math.sin(A.az),
                          objetivo.y + r * Math.cos(A.pol),
                          objetivo.z + r * Math.sin(A.pol) * Math.cos(A.az));
      camara.lookAt(objetivo);
      camara.updateMatrixWorld();
    }
    function colocaCamara() {
      const th = Math.tan(camara.fov * Math.PI / 360), tw = th * Math.max(0.4, cw / ch);
      const ext = 2 * V * (Math.abs(Math.cos(A.az)) + Math.abs(Math.sin(A.az)));   // ancho del cuadrado visto de lado
      const extV = ext * Math.cos(A.pol) + (ESC.techo + 0.4) * Math.sin(A.pol);      // y su alto en pantalla, con el relieve
      objetivo.set(0, 0.5 + 1.1 * Math.sin(A.pol), 0);
      let r = 1.07 * Math.max((ext / 2) / tw, (extV / 2) / th);
      for (let k = 0; k < 3; k++) {
        ponCamara(r);
        let m = 0;
        esquinas.forEach(e => { tmpP.copy(e).project(camara); m = Math.max(m, Math.abs(tmpP.x), Math.abs(tmpP.y)); });
        r *= m / 0.93;
      }
      ponCamara(r * A.r);
    }
    function ajustaTamano() {
      if (!vivo) return;
      cw = Math.max(1, caja.clientWidth); ch = Math.max(1, caja.clientHeight);
      renderer.setPixelRatio(Math.min(global.devicePixelRatio || 1, 2));     // el zoom del navegador lo cambia
      renderer.setSize(cw, ch, false);
      camara.aspect = cw / ch; camara.updateProjectionMatrix();
      // setSize BORRA el lienzo, y el observador de tamaño corre después de los cuadros de animación:
      // pedir otro cuadro dejaba uno en blanco en pantalla. Se vuelve a pintar en el acto.
      tick(0);
    }

    /* ---------------- etiquetas: de 3D a pantalla ---------------- */
    function proyecta(x, y, z, el, dx, dy) {
      v3.set(x, y, z).project(camara);
      if (v3.z > 1) { muestra(el, false); return; }
      el.style.left = ((v3.x * 0.5 + 0.5) * cw + (dx || 0)) + 'px';
      el.style.top = ((-v3.y * 0.5 + 0.5) * ch + (dy || 0)) + 'px';
    }
    function etiquetas() {
      barras.forEach((b, i) => {
        const c = b.userData.c;
        if (!c || etBarras[i]._d === 'none') return;
        proyecta((c.x0 + c.x1) / 2, b.scale.y + 0.32, Z((c.y0 + c.y1) / 2), etBarras[i]);
      });
      const vm = A.media > 0.4;
      muestra(etMedia, vm);
      if (vm) { proyecta(V - 2.4, mediaAlto + 0.1, Z(-V + 0.2), etMedia); etMedia.style.opacity = A.media; }
      const vu = A.sonda > 0.6;
      muestra(etU, vu);
      if (vu) proyecta(estado.sonda[0], 0, Z(estado.sonda[1]), etU, 0, 16);
    }

    /* ---------------- interfaz: textos, lecturas, perfil ---------------- */
    const leyH = $('.n3d-leyenda h5'), leyP = $('.n3d-leyenda p');
    const lect = $('.n3d-lectura');
    let ultimaLectura = '', ultimoPanel = '', pasoLey = 0;
    const panel = $('.n3d-panel'), panelLista = $('.n3d-ap-lista'), panelSuma = $('.n3d-ap-suma');

    function pintaLectura() {
      const s = estado.sigma, nuc = NUCLEOS[estado.nucleo];
      let h;
      if (estado.paso === 1) {
        h = [['puntos', N], ['ventana', (2 * V) + ' × ' + (2 * V)], ['intensidad media n/|W|', f2(N / (4 * V * V)) + ' por unidad de área']];
      } else if (estado.paso === 2) {
        const max = Math.max.apply(null, cuad.celdas.map(c => c.n));
        const vac = cuad.celdas.filter(c => c.n === 0).length;
        h = [['celda más llena', max + (max === 1 ? ' punto' : ' puntos')], ['celdas vacías', vac + ' de ' + cuad.celdas.length]];
      } else if (estado.paso === 3) {
        h = [['σ', f2(s)], ['altura de una loma', f2(nuc.k(0, s))], ['volumen de cada loma', '1 punto']];
      } else if (estado.paso === 4) {
        h = [['σ', f2(s)], ['núcleo', nuc.nombre], ['intensidad máxima', f2(pico) + ' por unidad de área']];
      } else {
        const suma = ap.reduce((a, b) => a + b, 0), al = nuc.alcance(s);
        const dentro = puntos.filter(p => Math.hypot(p[0] - estado.sonda[0], p[1] - estado.sonda[1]) < al).length;
        h = [['σ', f2(s)], ['λ̂(u)', f2(suma)], ['puntos dentro del círculo', dentro + ' de ' + N]];
      }
      const html = h.map(p => `<span><span class="n3d-r">${p[0]}</span> <b>${p[1]}</b></span>`).join('');
      if (html !== ultimaLectura) { ultimaLectura = html; lect.innerHTML = html; }
      // el panel de aportes del paso 5
      if (estado.paso === 5) {
        const orden = ap.map((w, i) => i).sort((a, b) => ap[b] - ap[a]);
        const total = ap.reduce((a, b) => a + b, 0) || 1;
        const top = orden.slice(0, 5).filter(i => ap[i] >= 0.005);
        const resto = total - top.reduce((a, i) => a + ap[i], 0);
        const htmlPanel = top.map((i, r) =>
          `<div class="n3d-ap"><span><em>x</em><sub>${i + 1}</sub></span><span class="n3d-ap-barra"><i style="width:${(100 * ap[i] / (ap[orden[0]] || 1)).toFixed(0)}%"></i></span><b>${f2(ap[i])}</b></div>`).join('') +
          (resto > 0.005 ? `<div class="n3d-ap"><span>otros</span><span class="n3d-ap-barra"><i style="width:${(100 * resto / (ap[orden[0]] || 1)).toFixed(0)}%;background:#8fb5a6"></i></span><b>${f2(resto)}</b></div>` : '');
        if (htmlPanel !== ultimoPanel) { ultimoPanel = htmlPanel; panelLista.innerHTML = htmlPanel; }
        panelSuma.textContent = f2(total);
      }
    }

    const perfil = $('.n3d-perfil'), gp = perfil.getContext('2d');
    function pintaPerfil() {
      const w = perfil.clientWidth, h = perfil.clientHeight, dpr = Math.min(global.devicePixelRatio || 1, 2);
      if (!w || !h) return;
      if (perfil.width !== Math.round(w * dpr)) { perfil.width = Math.round(w * dpr); perfil.height = Math.round(h * dpr); }
      gp.setTransform(dpr, 0, 0, dpr, 0, 0);
      gp.clearRect(0, 0, w, h);
      const m = { l: 6, r: 6, t: 8, b: 14 }, X = r => m.l + (w - m.l - m.r) * r / 3.6;
      const ymax = NUCLEOS.gaussian.k(0, 1), Y = v => h - m.b - (h - m.t - m.b) * v / ymax;
      gp.strokeStyle = '#cbd5e1'; gp.lineWidth = 1;
      gp.beginPath(); gp.moveTo(m.l, h - m.b + 0.5); gp.lineTo(w - m.r, h - m.b + 0.5); gp.stroke();
      gp.fillStyle = '#64748b'; gp.font = '10px Montserrat,sans-serif'; gp.textAlign = 'center';
      [0, 1, 2, 3].forEach(r => { gp.fillText(r === 0 ? '0' : r + 'σ', X(r), h - 2); });
      ORDEN_NUCLEOS.forEach(k => {
        const sel = k === estado.nucleo;
        gp.beginPath();
        for (let q = 0; q <= 120; q++) {
          const r = 3.6 * q / 120, v = NUCLEOS[k].k(r * r, 1);
          q === 0 ? gp.moveTo(X(r), Y(v)) : gp.lineTo(X(r), Y(v));
        }
        gp.strokeStyle = sel ? '#FF6600' : '#94a3b8'; gp.lineWidth = sel ? 2.2 : 1.1; gp.globalAlpha = sel ? 1 : 0.8;
        gp.stroke(); gp.globalAlpha = 1;
      });
    }

    // En la disposición apilada la leyenda reserva el alto de su texto MÁS LARGO: sin eso la
    // escena salta arriba y abajo al cambiar de paso, justo cuando se la está manejando.
    // Se mide en una COPIA oculta: la leyenda real es una región `aria-live`, y escribir en
    // ella los cinco textos en cada cambio de tamaño la hacía anunciar cinco pasos que nadie pidió.
    function fijaAlturaLeyenda() {
      const ley = $('.n3d-leyenda');
      if (cont.clientWidth >= 920) { if (ley.style.minHeight) ley.style.minHeight = ''; return; }
      const medidor = doc.createElement('div');
      medidor.className = 'n3d-leyenda';
      medidor.setAttribute('aria-hidden', 'true');
      medidor.style.cssText = 'position:absolute;visibility:hidden;pointer-events:none;min-height:0;width:' + ley.clientWidth + 'px';
      medidor.innerHTML = '<h5></h5><p></p>';
      ley.parentNode.appendChild(medidor);
      const h5 = medidor.firstChild, par = medidor.lastChild;
      let max = 0;
      PASOS.forEach(q => { h5.textContent = q.titulo; par.innerHTML = q.texto; max = Math.max(max, medidor.offsetHeight); });
      ley.parentNode.removeChild(medidor);
      const v = max + 'px';
      if (ley.style.minHeight !== v) ley.style.minHeight = v;
    }

    function pintaControles() {
      $$('.n3d-paso').forEach((b, i) => { b.setAttribute('aria-current', i + 1 === estado.paso ? 'step' : 'false'); });
      $$('.n3d-paso').forEach(b => { if (b.getAttribute('aria-current') === 'false') b.removeAttribute('aria-current'); });
      const mostrar = { rejilla: estado.paso === 2, sigma: estado.paso >= 3, nucleo: estado.paso >= 3, perfil: estado.paso >= 3 };
      Object.keys(mostrar).forEach(k => { const e = $(`[data-ctl="${k}"]`); if (e) e.hidden = !mostrar[k]; });
      $$('.n3d-nuc').forEach(b => b.setAttribute('aria-pressed', String(b.dataset.nucleo === estado.nucleo)));
      $$('[data-vista]').forEach(b => b.setAttribute('aria-pressed', String(b.dataset.vista === vista)));
      const rs = $('[data-ctl="rejilla"]'), ss = $('[data-ctl="sigma"]');
      rs.querySelector('output').textContent = f2(estado.desp); rs.querySelector('input').value = estado.desp;
      ss.querySelector('output').textContent = f2(estado.sigma); ss.querySelector('input').value = estado.sigma;
      const sv = ss.querySelector('input'); sv.setAttribute('aria-valuetext', 'sigma ' + f2(estado.sigma));
      if (pasoLey !== estado.paso) {          // la leyenda es `aria-live`: solo se toca al cambiar de paso, no con cada deslizador
        pasoLey = estado.paso;
        const p = PASOS[estado.paso - 1];
        leyH.textContent = p.titulo; leyP.innerHTML = p.texto;
      }
      panel.hidden = estado.paso !== 5;
      panel.setAttribute('aria-hidden', String(estado.paso !== 5));
    }

    /* ---------------- pasos ---------------- */
    function ir(n, instantaneo) {
      if (!vivo) return;
      n = clamp(n, 1, PASOS.length);
      estado.paso = n;
      const o = OBJETIVO[n], d = instantaneo ? 0 : 1.2;
      tween('cajas', o.cajas, d);
      tween('lomasH', o.lomasH, o.lomasH > A.lomasH ? 1.6 : 0.8);
      tween('lomasO', o.lomasO, d);
      tween('suma', o.suma, o.suma > A.suma ? 1.5 : 0.8);
      tween('sonda', o.sonda, d, o.sonda > A.sonda ? 0.5 : 0);
      tween('media', o.media, d);
      pintaControles(); pintaLectura();
      sucio = true; pide();
    }

    function fijaVista(nombre, instantaneo) {
      if (!vivo) return;
      vista = nombre;
      const v = VISTAS[nombre], d = instantaneo ? 0 : 1.1;
      A.az = ((A.az + Math.PI) % (2 * Math.PI) + 2 * Math.PI) % (2 * Math.PI) - Math.PI;    // tras varias vueltas, por el camino corto
      tween('az', v.az, d); tween('pol', v.pol, d); tween('r', v.r, d);
      $$('[data-vista]').forEach(b => b.setAttribute('aria-pressed', String(b.dataset.vista === nombre)));
      pide();
    }

    // Fija valores desde fuera (las pruebas y los guiones de clase): lo mismo que mover los mandos.
    function poner(v) {
      if (!vivo) return;
      Object.keys(v).forEach(k => { if (k in estado) estado[k] = v[k]; });
      estado.sigma = clamp(estado.sigma, SIGMA.min, SIGMA.max);
      estado.desp = clamp(estado.desp, 0, DESPLAZA_MAX);
      sucio = true; pintaControles(); pintaLectura(); pide();
    }

    /* ---------------- el guion: la reproducción automática ---------------- */
    // El σ del guion es una onda entre el mínimo del deslizador y 1.5 que ARRANCA en el σ de
    // partida y vuelve a él: sin salto al empezar ni al acabar. (La anterior, 0.8 + 0.7·sen, bajaba
    // a 0.1 —por debajo del mínimo, donde la escala vertical no está calibrada— y sacaba la
    // superficie de la pantalla.)
    const ONDA = { medio: (SIGMA.min + 1.5) / 2, ampl: (1.5 - SIGMA.min) / 2 };
    ONDA.fase = Math.asin((SIGMA.ini - ONDA.medio) / ONDA.ampl);
    const sigmaOnda = q => ONDA.medio + ONDA.ampl * Math.sin(q + ONDA.fase);
    const GUION = [
      { paso: 1, dur: 5 },
      { paso: 2, dur: 9, f: (t, d) => { estado.desp = DESPLAZA_MAX * (0.5 - 0.5 * Math.cos(2 * Math.PI * t / d)); } },
      { paso: 3, dur: 9, f: (t, d) => { estado.sigma = sigmaOnda(2 * Math.PI * t / d); } },
      { paso: 4, dur: 10, f: (t, d) => {
          if (t < d * 0.5) estado.sigma = sigmaOnda(2 * Math.PI * t / (d * 0.5));
          else { estado.sigma = SIGMA.ini; estado.nucleo = ORDEN_NUCLEOS[Math.min(3, Math.floor((t - d * 0.5) / (d * 0.125)) % 4)]; }
        } },
      { paso: 5, dur: 14, f: (t, d) => {
          const q = 2 * Math.PI * t / d;
          estado.sonda = [clamp(3.2 * Math.cos(q) - 0.2, -4.4, 4.4), clamp(2.8 * Math.sin(q), -4.4, 4.4)];
        } }
    ];
    const guion = { activo: false, i: 0, t: 0 };
    function sincronizaMandos() {
      pintaControles();
    }
    function guionIr(i) {
      guion.i = i; guion.t = 0;
      ir(GUION[i].paso);
      sincronizaMandos();
    }
    function reproducir() {
      if (!vivo || guion.activo) return;
      guion.activo = true;
      $('.n3d-play').dataset.activo = 'true';
      $('.n3d-play-ico').textContent = '❚❚'; $('.n3d-play-txt').textContent = 'Pausar';
      guionIr(0); pide();
    }
    function pausar() {
      if (!guion.activo) return;
      guion.activo = false;
      $('.n3d-play').dataset.activo = 'false';
      $('.n3d-play-ico').textContent = '▶'; $('.n3d-play-txt').textContent = 'Reproducir';
    }
    function guionTick(dt) {
      const g = GUION[guion.i];
      guion.t += dt;
      if (g.f) {
        g.f(guion.t, g.dur);
        estado.sigma = clamp(estado.sigma, SIGMA.min, SIGMA.max); estado.desp = clamp(estado.desp, 0, DESPLAZA_MAX);   // por si un guion futuro se pasa
        sucio = true;
      }
      if (guion.t >= g.dur) {
        if (guion.i + 1 < GUION.length) guionIr(guion.i + 1);
        else { pausar(); fijaVista('inclinada'); }
      }
      // la lectura y los mandos siguen lo que el guion mueve
      if (g.f) {
        const rs = $('[data-ctl="rejilla"]'), ss = $('[data-ctl="sigma"]');
        rs.querySelector('output').textContent = f2(estado.desp); rs.querySelector('input').value = estado.desp;
        ss.querySelector('output').textContent = f2(estado.sigma); ss.querySelector('input').value = estado.sigma;
        $$('.n3d-nuc').forEach(b => b.setAttribute('aria-pressed', String(b.dataset.nucleo === estado.nucleo)));
      }
    }

    /* ---------------- el bucle ---------------- */
    // `tick` es un paso de animación sin reloj: lo usan el bucle de pantalla y
    // `avanza` (las capturas y la impresión necesitan el estado de llegada, no
    // esperar a que el navegador reparta cuadros).
    function tick(dt) {
      let activo = avanzaTweens(dt);
      if (guion.activo) { guionTick(dt); activo = true; }
      if (sucio) { recalcula(); sucio = false; }
      aplica();
      colocaCamara();
      renderer.render(escena, camara);
      etiquetas();
      return activo;
    }
    function cuadro(ts) {
      pendiente = false;
      if (!vivo) return;
      const dt = Math.min(0.05, ts && ultimo ? (ts - ultimo) / 1000 : 0.016);
      ultimo = ts;
      if (tick(dt) || arrastre || orbita) pide(); else ultimo = 0;
    }
    function pide() {
      if (pendiente || !vivo || !visible) return;
      pendiente = true;
      raf = global.requestAnimationFrame(cuadro);
    }
    function avanza(seg) {
      if (!vivo) return;
      for (let t = 0; t < seg; t += 0.05) tick(0.05);
      tick(0);
    }

    /* ---------------- el puntero ---------------- */
    const rayo = new THREE.Raycaster(), ndc = new THREE.Vector2();
    const v4 = new THREE.Vector3();
    const MARGEN = 0.4;                  // lo más cerca del borde a lo que se puede llevar un punto
    // Cuánto se perdona al apuntar, en píxeles: la esfera de captura mide ~10 px de radio, que con un
    // ratón basta y con un dedo no. Con un dedo (o un lápiz) vale el objeto más cercano en la pantalla.
    // No más: dentro de ese radio el toque NO desplaza la página, y con 19 puntos en un lienzo de
    // teléfono una tolerancia mayor dejaba casi la mitad del lienzo sin poder pasar de largo.
    const TOLERANCIA = { touch: 16, pen: 10, mouse: 0 };
    function aNdc(e) {
      const r = lienzo.getBoundingClientRect();
      ndc.set(((e.clientX - r.left) / r.width) * 2 - 1, -((e.clientY - r.top) / r.height) * 2 + 1);
      rayo.setFromCamera(ndc, camara);
    }
    function capturados() {
      const l = [];
      if (A.sonda > 0.5) l.push(capAsa);
      marcas.forEach(m => l.push(m.cap));
      return l;
    }
    function masCercano(e, tol) {
      const r = lienzo.getBoundingClientRect();
      let mejor = null, dmin = tol;
      const prueba = (obj, pos) => {
        v3.copy(pos).project(camara);
        const d = Math.hypot((v3.x * 0.5 + 0.5) * r.width - (e.clientX - r.left), (-v3.y * 0.5 + 0.5) * r.height - (e.clientY - r.top));
        if (d < dmin) { dmin = d; mejor = obj; }
      };
      if (A.sonda > 0.5) prueba(capAsa, asa.getWorldPosition(v4));
      marcas.forEach(m => prueba(m.cap, m.g.position));
      return mejor;
    }
    function quienEs(e) {
      aNdc(e);
      const g = rayo.intersectObjects(capturados(), false);
      let o = g.length ? g[0].object : null;
      const tol = TOLERANCIA[e.pointerType || 'mouse'] || 0;
      if (!o && tol > 0) o = masCercano(e, tol);
      if (!o) return null;
      return o === capAsa ? { tipo: 'sonda' } : { tipo: 'punto', i: marcas.findIndex(m => m.cap === o) };
    }
    // La altura a la que se dibuja lo que se arrastra, en (x, y): la MISMA cuenta que `aplica`.
    // El punto arrastrado se evalúa EN su sitio nuevo (la superficie de la malla aún no lo sabe).
    function alturaDe(a, x, y) {
      const suma = suave(clamp(A.suma, 0, 1));
      if (a.tipo === 'punto') {
        const p = puntos[a.i], px = p[0], py = p[1];
        p[0] = x; p[1] = y;
        const sup = intensidadEn(estado.nucleo, puntos, estado.sigma, x, y) * ESC.alto;
        p[0] = px; p[1] = py;
        const propia = NUCLEOS[estado.nucleo].k(0, estado.sigma) * ESC.alto * sale(clamp(A.lomasH * 1.9 - 0.9 * a.i / N, 0, 1));
        return 0.17 + Math.max(propia, suma * sup);
      }
      return intensidadEn(estado.nucleo, puntos, estado.sigma, x, y) * ESC.alto * suma + 0.1;
    }
    // Dónde queda lo que se arrastra: el primer punto del rayo del cursor que se hunde bajo la altura
    // del objeto. Se marcha el rayo de arriba abajo y se afina por bisección. (Intersectar con un
    // plano a la altura del agarre no sirve: al subir a un pico el objeto flotaba decenas de píxeles
    // lejos del cursor; y corregirlo con una iteración de punto fijo diverge donde la superficie es
    // empinada, porque con la cámara inclinada un desnivel desplaza el rayo ~2 veces su valor.)
    function sobreLaSuperficie(a) {
      const o = rayo.ray.origin, d = rayo.ray.direction;
      if (d.y > -1e-6) return null;
      const H = t => { const x = clamp(o.x + d.x * t, -V + MARGEN, V - MARGEN), y = clamp(-(o.z + d.z * t), -V + MARGEN, V - MARGEN); return alturaDe(a, x, y); };
      const g = t => (o.y + d.y * t) - H(t);
      const tSuelo = -o.y / d.y, tTecho = Math.min(tSuelo, Math.max(0, (ESC.techo + 0.6 - o.y) / d.y));
      let t0 = tTecho, t1 = tSuelo;
      for (let k = 1; k <= 90; k++) {
        const t = tTecho + (tSuelo - tTecho) * k / 90;
        if (g(t) <= 0) { t1 = t; break; }
        t0 = t;
      }
      for (let k = 0; k < 10; k++) { const m = (t0 + t1) / 2; if (g(m) <= 0) t1 = m; else t0 = m; }
      const t = (t0 + t1) / 2;
      return [clamp(o.x + d.x * t, -V + MARGEN, V - MARGEN), clamp(-(o.z + d.z * t), -V + MARGEN, V - MARGEN)];
    }
    // Al agarrar se guarda, en píxeles, dónde cayó el dedo o el cursor respecto del centro del objeto:
    // sin esto el punto salta hasta el radio de su esfera de captura (y, con la tolerancia de un dedo, más).
    function agarra(e) {
      const r = lienzo.getBoundingClientRect();
      const pos = arrastre.tipo === 'punto' ? marcas[arrastre.i].g.position : asa.getWorldPosition(v4);
      v3.copy(pos).project(camara);
      arrastre.ox = (v3.x * 0.5 + 0.5) * r.width + r.left - e.clientX;
      arrastre.oy = (-v3.y * 0.5 + 0.5) * r.height + r.top - e.clientY;
    }
    function lleva(e) {
      aNdc({ clientX: e.clientX + arrastre.ox, clientY: e.clientY + arrastre.oy });
      const xy = sobreLaSuperficie(arrastre);
      if (!xy) return;
      if (arrastre.tipo === 'punto') { puntos[arrastre.i][0] = xy[0]; puntos[arrastre.i][1] = xy[1]; }
      else estado.sonda = xy;
      sucio = true;
    }
    const alguna = () => { tocoAlgo = true; $('.n3d-ayuda').classList.add('n3d-oculta'); if (guion.activo) pausar(); };

    lienzo.addEventListener('pointerdown', e => {
      if (e.button !== 0 && e.pointerType === 'mouse') return;
      alguna();
      const q = quienEs(e);
      try { lienzo.setPointerCapture(e.pointerId); } catch (_) { /* el puntero ya no está activo */ }
      if (q) { arrastre = q; agarra(e); lienzo.classList.add('n3d-agarra'); lleva(e); }
      else orbita = { x: e.clientX, y: e.clientY, az: A.az, pol: A.pol };
      pide();
    });
    lienzo.addEventListener('pointermove', e => {
      if (arrastre) { lleva(e); pide(); }
      else if (orbita) {
        sinTweensDeCamara();
        A.az = orbita.az - (e.clientX - orbita.x) * 0.006;
        A.pol = clamp(orbita.pol - (e.clientY - orbita.y) * 0.005, 0.03, 1.38);
        vista = 'libre';
        $$('[data-vista]').forEach(b => b.setAttribute('aria-pressed', 'false'));
        pide();
      } else if (e.pointerType === 'mouse') {
        lienzo.classList.toggle('n3d-sobre', !!quienEs(e));
      }
    });
    const suelta = e => {
      if (arrastre || orbita) { try { lienzo.releasePointerCapture(e.pointerId); } catch (_) { /* ya soltado */ } }
      arrastre = null; orbita = null; lienzo.classList.remove('n3d-agarra');
      if (clase) devuelveElFoco();
    };
    lienzo.addEventListener('pointerup', suelta);
    lienzo.addEventListener('pointercancel', suelta);
    // En el teléfono el dedo sobre un punto lo mueve; en cualquier otro sitio, el desplazamiento de la página sigue siendo suyo.
    lienzo.addEventListener('touchstart', e => {
      if (e.touches.length !== 1) return;
      const t = e.touches[0];
      if (quienEs({ clientX: t.clientX, clientY: t.clientY, pointerType: 'touch' })) e.preventDefault();
    }, { passive: false });

    // Si el sistema le quita el contexto a la página (iOS con poca memoria) y luego lo devuelve, el
    // bucle bajo demanda no sabe que el lienzo quedó en blanco: hay que pedir un cuadro.
    lienzo.addEventListener('webglcontextrestored', () => { if (vivo) { sucio = true; pide(); } });

    // Teclado: las flechas giran la vista; con Mayús, en el paso 5, mueven el sitio u (sin esto
    // el paso 5 —leer la altura en un sitio— no se podía hacer sin ratón).
    lienzo.tabIndex = clase ? -1 : 0;
    lienzo.addEventListener('keydown', e => {
      const q = { ArrowLeft: [0.12, 0], ArrowRight: [-0.12, 0], ArrowUp: [0, 0.1], ArrowDown: [0, -0.1] }[e.key];
      if (!q) return;
      e.preventDefault(); alguna();
      if (e.shiftKey && estado.paso === 5) {
        const m = V - MARGEN;
        estado.sonda = [clamp(estado.sonda[0] - Math.sign(q[0]) * 0.25, -m, m), clamp(estado.sonda[1] + Math.sign(q[1]) * 0.25, -m, m)];
        sucio = true; pide();
        return;
      }
      sinTweensDeCamara();
      A.az += q[0]; A.pol = clamp(A.pol + q[1], 0.03, 1.38);
      vista = 'libre'; $$('[data-vista]').forEach(b => b.setAttribute('aria-pressed', 'false'));
      pide();
    });

    /* ---------------- mandos ---------------- */
    $$('.n3d-paso').forEach(b => b.addEventListener('click', () => { alguna(); ir(+b.dataset.paso); if (clase) devuelveElFoco(); }));
    $('.n3d-play').addEventListener('click', () => { if (guion.activo) pausar(); else reproducir(); if (clase) devuelveElFoco(); });
    const rej = $('[data-ctl="rejilla"] input'), sig = $('[data-ctl="sigma"] input');
    rej.addEventListener('input', () => { alguna(); estado.desp = +rej.value; sucio = true; pintaControles(); pide(); });
    sig.addEventListener('input', () => { alguna(); estado.sigma = +sig.value; sucio = true; pintaControles(); pide(); });
    $$('.n3d-nuc').forEach(b => b.addEventListener('click', () => {
      alguna(); estado.nucleo = b.dataset.nucleo; sucio = true; pintaControles(); pide(); if (clase) devuelveElFoco();
    }));
    $$('[data-vista]').forEach(b => b.addEventListener('click', () => { alguna(); fijaVista(b.dataset.vista); if (clase) devuelveElFoco(); }));
    $('[data-reinicia]').addEventListener('click', () => {
      alguna();
      PATRON.forEach((p, i) => { puntos[i][0] = p[0]; puntos[i][1] = p[1]; });
      estado.sigma = SIGMA.ini; estado.nucleo = 'gaussian'; estado.desp = 0; estado.sonda = [-2.5, 1.0];
      fijaVista('inclinada'); ir(estado.paso, true); sucio = true; pintaControles(); pide();
      if (clase) devuelveElFoco();
    });
    [rej, sig].forEach(el => { ['change', 'pointerup'].forEach(ev => el.addEventListener(ev, () => { if (clase) devuelveElFoco(); })); });

    /* ---------------- en una diapositiva ---------------- */
    // Dentro de un iframe, las flechas son del presentador y no de un deslizador: se reenvían al
    // visor y el foco vuelve a la página. El mensaje lleva solo el NOMBRE de una tecla, así que
    // `'*'` como destino no filtra nada (con `file://` el origen es opaco y no hay otro): el
    // que sí tiene que comprobar de quién viene es el oyente del visor (`e.source`).
    // Fuera de un marco no se reenvía nada ni se secuestra ninguna tecla.
    const enMarco = !!global.parent && global.parent !== global;
    const TECLAS_VISOR = new Set(['ArrowRight', 'ArrowLeft', 'ArrowDown', 'ArrowUp', ' ', 'PageDown', 'PageUp', 'Enter', 'Backspace', 'Escape',
                                  'Home', 'End', 'm', 'n', 'p', 'f', 'b', 'h', '.', '?']);
    function devuelveElFoco() {
      if (!enMarco) return;
      try { global.parent.postMessage({ nucleos: 'foco' }, '*'); } catch (_) { /* sin padre */ }
    }
    let alTeclear = null;
    if (clase && enMarco) {
      alTeclear = e => {
        if (e.metaKey || e.ctrlKey || e.altKey || !(TECLAS_VISOR.has(e.key) || TECLAS_VISOR.has(e.key.toLowerCase()) || /^[0-9]$/.test(e.key))) return;
        e.preventDefault();
        try { global.parent.postMessage({ nucleos: 'tecla', key: e.key, shiftKey: e.shiftKey }, '*'); } catch (_) { /* sin padre */ }
      };
      doc.addEventListener('keydown', alTeclear, true);
    }

    /* ---------------- vida del componente ---------------- */
    const ro = global.ResizeObserver ? new global.ResizeObserver(() => { ajustaTamano(); pintaPerfil(); fijaAlturaLeyenda(); }) : null;
    if (ro) { ro.observe(caja); ro.observe(cont); }
    const io = global.IntersectionObserver ? new global.IntersectionObserver(es => {
      visible = es.some(x => x.isIntersecting);
      if (visible) pide();
    }, { rootMargin: '120px' }) : null;
    if (io) io.observe(caja);
    const alImprimir = () => { avanza(3); };
    global.addEventListener('beforeprint', alImprimir);

    function destruir() {
      vivo = false;
      global.cancelAnimationFrame(raf);
      if (ro) ro.disconnect();
      if (io) io.disconnect();
      global.removeEventListener('beforeprint', alImprimir);
      if (alTeclear) doc.removeEventListener('keydown', alTeclear, true);      // si no, al volver a montar cada tecla llegaba dos veces
      desechables.forEach(o => { try { o.dispose(); } catch (_) { /* ya liberado */ } });
      matBarra.forEach(m => m.dispose());
      Object.keys(matLoma).forEach(k => matLoma[k].dispose());
      renderer.dispose();
      try { renderer.forceContextLoss(); } catch (_) { /* sin extensión */ }
      cont.innerHTML = '';
      cont.classList.remove('n3d', 'n3d-clase');
    }

    // arranque: todo calculado ANTES del primer paso (la lectura del paso 5 lee los aportes),
    // y la cámara baja de la vista cenital a la inclinada
    recalcula(); sucio = false;
    colocaCamara();
    ajustaTamano();
    ir(1, true);
    fijaAlturaLeyenda();
    fijaVista('inclinada', false);
    if (reducido) { A.az = VISTAS.inclinada.az; A.pol = VISTAS.inclinada.pol; A.r = VISTAS.inclinada.r; }
    pide();

    return { destruir, ir, poner, reproducir, pausar, avanza, fijaVista, estado,
             _: { A, puntos, ESC, escena, camara, renderer, grupoSup, grupoSonda, segmentos, hilos, asa, matSup } };
  }

  const API = { montar, estilos: inyectaCSS, matematica: MATEMATICA, PASOS };
  if (typeof module !== 'undefined' && module.exports) module.exports = API;
  else global.Nucleo3D = API;
})(typeof window !== 'undefined' ? window : globalThis);
