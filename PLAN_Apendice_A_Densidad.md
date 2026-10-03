# Apéndice A · La densidad en una dimensión

## §0 — Estado y lo que cambió al medir (2026-10-02)

Construido en el worktree `.claude/worktrees/apendice-a`, rama `claude/apendice-a-densidad`
desde `origin/main` (a000631). El plan aprobado está debajo, sin tocar; aquí van las
desviaciones, cada una con su causa medida.

1. **Los ejercicios viven en `genera_apendicea.R`, no en `genera_soluciones.R`.** Ese guion
   elige la sección por número de capítulo (`as.integer(args)`) y el apéndice no lo tiene. La
   maquinaria es la misma (`responde()` anclado al enunciado, `sin_contestar()` con la regla de
   los dos puntos del capítulo 5).
2. **La UCV sobre distancias al vecino no tiene mínimo, y por dos causas.** El plan hablaba
   solo de las parejas recíprocas. Medido: las parejas solas (sin los ceros) dejan
   `bw.ucv` en 3.39 m, y los ceros solos (una distancia por pareja, ceros dentro) en 3.94 m;
   solo sin las dos cosas vuelve a 20.42 m, junto a SJ (20.34). Y hay teoría detrás, que entró
   en el módulo 12 con su derivación: con E parejas empatadas la UCV se va a −∞ cuando
   E/n > R(K)/(4K(0) − 2R(K)) ≈ 0.2735, y las parejas recíprocas de un patrón al azar ya dan
   0.3108 (Cox, 1981: la fracción recíproca es 6π/(8π+3√3) = 0.6215).
3. **El ejercicio 10 (Kennedy) cambió de pregunta.** Allí `bw.ucv` con todas las distancias
   devuelve 30.34 m SIN aviso, una cifra plausible, mientras el criterio exacto con h = 0.001 m
   es negativo: es un mínimo local dentro del intervalo de búsqueda. El ejercicio pide
   reconocer eso: un número sin aviso no garantiza que el criterio tenga mínimo.
4. **La corrección e(x) no «se pasa» siempre.** Un dato en el borde aporta exactamente ln 2
   (forma cerrada en una dimensión) y uno a 1.59 anchos, 1.072. El total depende del patrón:
   en Bogotá se queda en 0.991. Es el hallazgo del módulo 4 del capítulo 5, ahora con fórmula.
   **Y esa cifra la corrigió el auditor independiente**: la primera versión publicaba 0.949,
   porque `integrate()` sobre [0, ∞) no encontraba la loma de las sedes lejanas (hasta 122
   anchos del borde) y 89 de ellas aportaban 0 en vez de 1. `audita_apendicea.py`, que integra
   por otro camino, dio 0.99140; el generador integra ahora sobre [d − 12, d + 12].
5. **Los dientes del k-NN son de la fórmula.** La guarda esperaba «pocas modas con k
   grande»; con k = 80 quedan 72. d_k(x) es lineal a trozos y tiene un mínimo cada vez que el
   k-ésimo vecino cambia de lado. La prosa dice «continuo y no derivable».
6. **El borde usa el ancho de SJ sobre una distancia por pareja y sin ceros** (20.34 m), y
   la masa negativa es 2.72 % (el 2.4 % de la sesión de diseño era con SJ sobre todas).
7. **R y Python desempatan distinto entre sedes coincidentes.** `nnwhich` de spatstat elige
   la vecina de índice MAYOR; con el desempate de `cKDTree` la fracción recíproca sale 59.5 %
   y no 61.3 %. La pestaña de Python replica la regla de R y lo dice en un comentario.
8. **`verifica_bloques.py --todos` encadena una sola sesión de R**, y el apéndice va antes
   que el capítulo 1: un `area()` del módulo 7 tapaba la `area()` de spatstat y tumbó todos los
   bloques de R detrás. Se renombraron `area` → `area_knn`, `D` → `dif` y `q` → `quien`.
9. **La caja `.formula` es solo para la fórmula** (la plantilla la pinta centrada y en
   monoespaciada). Los párrafos explicativos salieron de ella.
10. **La figura del plano son dos SVG**, que se apilan en el teléfono: lado a lado, a 375 px
    los rótulos quedaban a unos cinco píxeles.
11. **La simulación de CSR estaba sesgada.** Exigir «borde > 3 × distancia al vecino»
    selecciona los puntos con vecinos cercanos (0.628 sobre 20 semillas, contra 0.6215). Ahora
    usa un margen fijo; lo midió el auditor independiente.
12. **La revisión independiente de la prosa encontró 16 errores, todos corregidos.** Los de
    fondo: la brecha de la varianza del módulo 8 la causa el término −(E f̂)²/n que la fórmula
    descarta, no «que cada punto mira pocos datos»; la reflexión no es una de las correcciones
    del capítulo 5; la animación 3D del capítulo 5 no está en `main` y no se cita; `density.ppp`
    divide por e(u) por defecto; la lección del ejercicio 5 la contradecían sus pasos (ahora
    calcula las dos escalas y pregunta en cuál se parecen los núcleos); el ejercicio 3 afirmaba
    que el k-NN sobreestima en el valle y con k = 10 casi acierta; el cero de SJ en la cola es por
    construcción; los capítulos 8 y 10 se citan en futuro porque están en preparación.
13. **La nota en el capítulo 5 sigue pendiente**, a propósito: espera a que se fusionen los
    PR #8 y #9, que tocan ese capítulo.
14. **Revisión 2 (2026-10-02, a petición de Javier): seis revisores en paralelo** —prosa en
    tres tramos, autoevaluación y ejercicios, simuladores, arco y notación— y unos 150 hallazgos.
    Los que cambiaban una conclusión:
    - **los histogramas de los módulos 1 y 2 se dibujaban corridos un intervalo** a la izquierda
      (`stepped: 'after'` de Chart.js pinta cada tramo con la altura del punto siguiente); ningún
      auditor lo veía, y lo midió un revisor leyendo píxeles;
    - **la UCV de las erupciones tampoco tiene mínimo**: 126 valores distintos entre 272 dan 1.15
      parejas empatadas por dato, por encima del umbral del módulo 12; el 0.102 es un mínimo local
      (estable: rompiendo los empates con medio segundo de ruido sigue en 0.101–0.105);
    - la tabla de sesgo y varianza del módulo 10 metía R(f̂″) como si fuera R(f″), y su orden
      contradecía al MISE exacto del 11: ahora enseña el término de ruido R(K″)/(nh⁵), que es lo
      que BCV resta y lo que motiva el *plug-in* (SJ y dpik, que no se explicaban);
    - «la UCV tiende a infrasuavizar» era falso en promedio: se equivoca de dispersión y hacia un
      lado (las 52 réplicas en que pierde por más del doble eligieron todas menos de 0.10);
    - en r = 0 del módulo 12 más de la mitad de la altura la ponen los 79 ceros (un átomo), y el
      máximo que la reflejada enseña en el borde es entero de ellos: sin los ceros arranca abajo y
      sube (lo midió la segunda pasada, que corrigió una primera corrección que decía que reflejar
      lo «fabricaba»);
    - el promedio de 30 curvas del módulo 8 tenía más error de Monte Carlo que el sesgo que quería
      enseñar: la curva verde es ahora el valor esperado exacto;
    - el módulo 6 nombraba el núcleo equivocado (con el mismo soporte se alejan la caja y el
      biweight, no el triangular) y su tesis «la forma no cambia lo que dice» era falsa sobre la
      unimodal (9 y 27 máximos locales contra 1);
    - el ejercicio 7 explicaba una coincidencia casual con una simetría que no existe.
    La autoevaluación pasó a 17 preguntas, al menos una por módulo, con `modulo` para el resumen
    de repaso, opciones de longitud pareja (en 6 de 8 la correcta era la más larga) y una de
    lectura de gráfico; la sal del barajado se eligió entre 28 por reparto parejo (3, 4, 4, 4).
    Los diez ejercicios ganaron pista y la etiqueta de los módulos que practican; el E9 cambió su
    pregunta («el menor k» repetía el E8) por la interpretativa del Rmd. Una **segunda pasada**
    de tres revisores sobre lo reescrito encontró once errores más, ya corregidos; entre ellos,
    uno de la primera corrección (el máximo de la reflejada), la meseta del E9 (va a 175, no a
    174), la causa del valle de `bw.ucv` en el E10 (es la búsqueda local de `optimize`, no el
    agrupado: sobre el criterio exacto también cae en 30.01 m), que en x = 0 no se ve el efecto de
    centrar la ventana (sí en x = 0.5: 1.33 frente a 1.53) y una figura que recortaba el margen y
    pintaba de un solo color las sedes que cuentan dos círculos. Generador: 93 guardas; auditor:
    1 072 comprobaciones, y su arnés caza 139 de 139 defectos. `audita_todo.sh --rapido` cazó
    un lector más del `f_valle` del k-NN, que pasó del nodo de la rejilla a 7.5 exacto:
    `prueba_densidad1d.py`, que lo evalúa ahora en `valle_x`. Quedan como propuesta, sin hacer, tres animaciones (el ASH
    que promedia orígenes, la loma que se desliza, la ventana del k-NN) y reordenar los
    ejercicios por dificultad: renumerarlos arrastra las claves `e1…e10` por R, JSON, auditor
    y arnés, y la etiqueta de módulos cubre la mitad del problema.


## Context

Javier tiene un documento propio, `Usta 2026II/Colsultoria/densidades/JMS_Densidades.Rmd`
(3 425 líneas, ya corregido y pasado por 11 revisores). Recorre histograma, ASH, la
formulación k/(nV), Parzen, k-NN, KDE y núcleos, y luego ECM/ECI/ECIP y el estimador
adaptativo/*balloon*. Cierra con los selectores (Silverman, Scott, UCV, LCV, BCV, SJ) aplicados
a `faithful`, con EM y Monte Carlo, y con 9 ejercicios resueltos más 5 preguntas con clave.

Quiere convertirlo en un **apéndice del material de Estadística Espacial** que dé a los
estudiantes conocimiento, interpretabilidad y apropiación. El hueco es real, porque el
capítulo 5 (intensidad por núcleos) no tiene nada en una dimensión:

- no nombra el sesgo ni la varianza, ni el MISE, ni a Silverman;
- usa σ, cuatro núcleos, `bw.diggle`, `bw.ppl`, `bw.CvL`, `bw.scott` y la corrección de borde
  sin la teoría de la que salen;
- su módulo 7 usa `1.06·sd·n^(-1/5)` en un bloque de Python sin explicarla.

**Decisiones de Javier (2026-10-02):**
- **Formato:** documento completo por la cadena del repo (R → JSON → ensamblador → auditores),
  con simuladores, código R y Python, autoevaluación y ejercicios.
- **Enfoque:** puente al espacio. Cada módulo cierra con su gemelo espacial, y hay una tabla
  1D↔2D al final.
- **Datos:** `faithful`, más las distancias al vecino más cercano de las 2 107 sedes de
  Bogotá, más los ejemplos de juguete del Rmd para el cálculo a mano.
- **Enlaces:** una tarjeta en la portada y una nota en el capítulo 5. La nota va después de que
  se fusionen los PR #8 y #9, que también tocan ese capítulo.

## Hallazgos medidos en esta sesión (R 4.4 del proyecto, spatstat 3.5.1, Python geo_env)

Los seis entran como contenido. El generador los recalcula: aquí solo se fijan.

1. **El ASH es un KDE triangular disfrazado.** Con h = 0.6 sobre `faithful$eruptions`, la
   distancia máxima entre el ASH y el KDE triangular de semiancho h baja como 1/m:
   0.222 (m=1), 0.058 (4), 0.016 (16), 0.0039 (64), 0.00093 (256). El Rmd no lo dice, y es el
   puente literal entre el histograma y el núcleo.
2. **`bw.scott` de spatstat es la regla de referencia normal en d dimensiones.** Su código es
   `sd · n^(-1/(d+4))`. El factor (4/(d+2))^(1/(d+4)) vale 1.059 en d = 1 (el 1.06 de `bw.nrd`)
   y exactamente 1 en d = 2. Una sola fórmula une el apéndice con el σ del capítulo 5.
3. **Las distancias al vecino más cercano no son iid.** Sobre las 2 107 sedes de
   `precalculo/salidas/cap5_bogota_urbana.csv`:
   - hay 79 distancias iguales a 0 (sedes coincidentes, el «átomo» de G del cap. 4 M7);
   - el 61.3 % de las relaciones de vecino son recíprocas (59 % bajo CSR), así que las
     distancias vienen en parejas repetidas;
   - `bw.ucv` colapsa a 3.4 m con el aviso «minimum occurred at one end»;
   - sobre las distancias únicas, `bw.ucv` da 20.3 m, igual que `bw.SJ` (20.3).
4. **Borde en x ≥ 0.** El KDE con `bw.SJ` de esas distancias deja 2.4 % de la masa en
   distancias negativas. Renormalizar en 1D es lo mismo que el e(u) de Diggle del cap. 5 M4.
5. **Las convenciones de R y Python no coinciden.**
   - `density(kernel="epanechnikov", bw=1)` de R tiene soporte ±√5 = ±2.236, porque `bw` es la
     desviación típica del núcleo. En `KernelDensity` de sklearn, `bandwidth` es el radio del
     soporte. El mismo número significa cosas distintas.
   - El `"silverman"` de `scipy.gaussian_kde` es (4/3)^(1/5)·sd·n^(-1/5): `bw.nrd` sin el
     IQR, y no `bw.nrd0`.
6. **spatstat tiene un gemelo 2D para cada estimador 1D:** `nndensity`, que es k-NN;
   `adaptive.density` y `densityAdaptiveKernel`, que son adaptativos; `bw.ppl`, que es LCV de
   proceso puntual; y `bw.diggle`, que es un criterio de ECM por validación cruzada.

## El apéndice: 13 módulos

Cada módulo lleva, como los capítulos:
- una cabecera con el 🎯 objetivo y una pregunta que lo motiva;
- prosa con cifras interpoladas desde el JSON y una caja `.formula`;
- un simulador con un «predice antes de mover» y su lectura;
- un bloque de código en pestañas R y Python con `#>` verificables;
- un recuadro **«Cómo se lee»** (interpretación) y otro **«En el plano»** (`.tip-box`), que es
  el puente al capítulo concreto;
- cuando haga falta, un `.warning` con una **trampa** del Rmd convertida en lección.

| # | Módulo | Datos | Simulador | En el plano |
|---|---|---|---|---|
| 1 | Densidad e intensidad: el área es la probabilidad | cafetería bimodal (60 + 40) | arrastrar un intervalo [a, b]: el área es la proporción; la altura no es una probabilidad | λ = n·f; ∫λ = número esperado de sedes, no 1 |
| 2 | El histograma: dos perillas | `faithful` | h y origen; cuenta las modas | origen = efecto de zonificación del MAUP (cap. 3); h = efecto de escala; cuadrantes (cap. 4 M2–M6); «desplazar la rejilla» (cap. 5 M1) |
| 3 | El ASH: promediar los orígenes | ejemplo a mano {2,3,3,5,7,8,9,10}; `faithful` | m de 1 a 64 con h fijo, con el KDE triangular superpuesto y su distancia | promediar rejillas desplazadas es el remedio 1D de la zonificación |
| 4 | Contar en una ventana: k/(nV) | N(0,1), muchas muestras | «una ventana, muchas muestras»: la media de k/(nV) se aleja (sesgo) y su nube se abre (varianza) | V es un área en el plano: conteo/área = intensidad; maldición de la dimensión: n^(-4/(4+d)), 2.4× más datos en d = 1 y 2.8× en d = 2 para bajar el error a la mitad |
| 5 | El estimador de núcleo: una loma por punto | {1..5} uniforme; {2,3,4,5,7} gaussiano | h mueve las lomas y su suma; número de modas | `density.ppp` es esta suma sin el 1/n; mismo vocabulario que la animación 3D del cap. 5 M1 |
| 6 | La forma del núcleo importa poco, la escala mucho | unimodal y trimodal | los 6 núcleos al mismo σ o al mismo soporte | cap. 5 M2 «al mismo σ»; h²/σ² = 5 (Epanechnikov 1D) frente a 6 (2D) |
| 7 | k vecinos: el radio se adapta | {20..40} en x = 30; mezcla bimodal | k: modas, área ≠ 1, empates | `nndensity`; G (cap. 4 M7); k-NN es un *balloon* uniforme; `adaptive.density`; GWR adaptativo (cap. 8) |
| 8 | Sesgo, varianza y error integrado | N(0,1), n = 100 | nube de 30 KDE con su media y la verdad, más las curvas sesgo², varianza y ECM según h | nombra lo que el cap. 5 M2 describe: focos sueltos (varianza) frente a una sola mancha (sesgo) |
| 9 | Reglas de referencia | `faithful` | — (tabla + figura) | `bw.scott` = n^(-1/6) en d = 2; explica el 1.06 del cap. 5 M7; trampa: 3.5·sd·n^(-1/3) es la regla del histograma |
| 10 | Validación cruzada | `faithful` | curvas UCV(h) y LCV(h) junto al KDE | `bw.ppl` = LCV; `bw.diggle` ≈ UCV; aviso «minimum at one end» = el «selector que no seleccionó» del cap. 5 M3 |
| 11 | Una verdad conocida: ¿qué selector acierta? | mezcla EM; 1 000 réplicas | ISE de cada selector en cada réplica; quién gana y cuántas veces pierde por mucho | «el ancho óptimo no es una propiedad del patrón» (cap. 5 M3), ahora medido; error de Monte Carlo ±1.5 pp |
| 12 | Del renglón al plano: las sedes de Bogotá | distancias al vecino de las 2 107 sedes | KDE sin corregir / reflejado / renormalizado; UCV con todas las distancias o solo las únicas | borde = e(u) de Diggle (cap. 5 M4); la densidad de esas distancias es G′(r) frente a la de CSR; datos no iid (cap. 10); tabla final 1D↔2D |
| 13 | Autoevaluación y ejercicios | — | — | — |

**Del Rmd** se conservan las cifras canónicas, recalculadas, y las trampas, que pasan a cajas
`.warning`:
- `truehist` no es un ASH;
- las ventanas solapadas no integran 1 (1.18);
- con `right = FALSE` cambia la casilla consultada;
- `density()` reescala la caja a ±√3·h;
- `bw.bcv` no es LCV;
- el *balloon* no integra 1;
- |u| ≤ 1 frente a |u| < 1 cambia el valor en un punto (0.3 frente a 0.1).

**Se condensa:** los cuatro ejemplos resueltos del ASH quedan en uno a mano, el pseudocódigo y
un ejercicio. **Se retiran:** la sección del k-NN que «reemplaza alturas del histograma», la
analogía del gasto familiar (su sitio lo ocupa el k-NN visto como *balloon*) y la figura de
hipercubos (la sustituye la de círculos Parzen/k-NN dibujada sobre sedes reales).

**Autoevaluación, 12 preguntas** (tipos `opcion`, `multiple`, `numerica` y `grafico`, todas
con su retro):
- las 5 del Rmd adaptadas;
- 7 nuevas de interpretación: el área entre dos tiempos; qué efecto del MAUP es mover el
  origen; el semiancho de la caja con `bw = 0.6`; qué significa el aviso de `bw.ucv`; por qué
  las distancias al vecino no son iid; por qué `bw.scott` usa n^(-1/6); y una de leer un ISE
  de Monte Carlo.

**Ejercicios guiados:** los 9 del Rmd con pista y solución, más un **E10 espacial**. El E10 toma
las sedes de una localidad: calcular sus distancias al vecino, estimar con reflexión, comparar
UCV con todas las distancias y con las únicas, e interpretar.

## Construcción (cadena de la casa)

**Dónde:** un worktree nuevo `.claude/worktrees/apendice-a`, rama `claude/apendice-a-densidad`
desde `origin/main` (a000631). No hace falta `datos/` para generar, porque los datos son
`faithful` y `cap5_bogota_urbana.csv`, que está versionado. Para `audita_todo.sh --rapido` sí
hay que copiar `datos/procesado` y `precalculo/cache` (memoria de worktrees).

**Archivos nuevos:**
- `precalculo/genera_apendicea.R`:
  - calcula **toda** cifra con la semilla 2026 de `entorno.R`; las cifras del Rmd que salían de
    otras semillas cambian y se releen;
  - guardas en R contra cada afirmación de forma (la UCV de `faithful` da 3 modas y las demás
    2; ASH → triangular monótono en m; el colapso de UCV con las distancias repetidas);
  - escribe `precalculo/salidas/apendicea_datos.json`, `apendicea_soluciones.json` y un CSV
    por réplica del Monte Carlo (h e ISE, 1000×5) con las muestras de unas 20 réplicas.
- `precalculo/audita_apendicea.py` (sobre `audita_base.Auditoria`, Python de geo_env), que
  recalcula por su cuenta:
  - conteos, ASH, KDE y constantes de los núcleos (μ₂, R(K), eficiencias) por integración
    numérica;
  - ECM exacto, EM y MISE cerrado de la mezcla;
  - UCV/LCV en numpy y SJ propio, con tolerancia por el binado de R;
  - los resúmenes del Monte Carlo desde el CSV, y h e ISE de las réplicas muestreadas;
  - las distancias de Bogotá con `cKDTree`: ceros, recíprocas, masa negativa y reflexión.
- `precalculo/prueba_auditor_apendicea.py`: inyecta defectos y comprueba que el auditor falla.
- `precalculo/densidad1d.js`: matemática pura de los simuladores (histograma, ASH, KDE con los
  6 núcleos en la convención de R, k-NN), inyectada en línea.
  - **Probado contra R** con `node` en `precalculo/prueba_densidad1d.py`, con mutaciones, como
    `prueba_nucleo3d.py`.
  - Las cifras de la prosa salen siempre del JSON. Lo que se precalcula en R se lee de ahí:
    curvas de criterio, ECM por h y Monte Carlo.
- `precalculo/ensambla_apendicea.py`:
  - patrón y ayudantes de `ensambla_cap6.py` (`cabecera`, `tabs`, `sim`, `quiz_html`,
    `ejercicio`, `reemplaza_region`, `sustituye`), sobre `plantilla/plantilla-capitulo.html`
    y con `baraja_opciones`;
  - escribe `Htmls_Espacial/apendice-a-densidad.html`;
  - post-chequeos de canvas con `aria-label`, bloques R = bloques Python y 13 módulos.
- `precalculo/audita_texto_apendicea.py` (sobre `audita_texto_base.Auditor`, con
  `afirmaciones` para los hallazgos 1–4). El tope de peso se mide y se declara: no es un
  presupuesto.
- `genera_soluciones.R`: `solucion_apendicea()` con `responde()` anclado a un trozo literal de
  cada enunciado (lección M5 del cap. 5).
- `PLAN_Apendice_A_Densidad.md`: este plan versionado; la lista blanca admite `PLAN_*`.

**Archivos que cambian:**
- `precalculo/cuenta_sitio.py`: una quinta tabla, `apendice-*.html`. Hoy cualquier HTML sin
  clasificar lo pone en rojo (líneas 121–131 y 184–189), y la comprobación de enlace desde la
  portada (línea 201) también tiene que verlo.
- `precalculo/audita_todo.sh`: dos bucles `for L in a b c`, uno de precálculo e inyecciones
  tras la línea 141 y otro de texto tras la 203, más `prueba_densidad1d.py`.
- `precalculo/prueba_texto.py`: la entrada `"apendicea"` en `SUJETOS`.
- `index.html`: la sección «Apéndices», entre Preparciales y En preparación, con la tarjeta
  `card-number` «A».
- `README.md`: el estado y las cuentas que imprima `cuenta_sitio.py`.
- **Después de fusionar los PR #8 y #9, en un PR aparte:** en `ensambla_cap5.py`, una nota
  «Repaso en una dimensión» en el M1, remisiones puntuales en el M2 (→ A8) y en el M3
  (→ A9–A11) y una línea en «Dónde sigue esto». Luego reensamblar el cap. 5 y pasar sus dos
  auditores.

**Riesgo conocido:** `verifica_bloques.py --todos` encadena **una** sesión de R y otra de
Python para todos los HTML, y `apendice-…` va antes que `capitulo-1`. Cada bloque del
apéndice será autónomo y fijará su propia semilla. Verde quiere decir que los capítulos siguen
pasando con el apéndice delante.

## Verificación

1. `precalculo/rscript.sh precalculo/genera_apendicea.R`: las guardas en R pasan.
2. `audita_apendicea.py` (geo_env) en verde, y `prueba_auditor_apendicea.py` caza todas sus
   inyecciones (filtrar con `grep "defectos cazados"`, nunca con `tail`).
3. `prueba_densidad1d.py`: el JS coincide con `hist`, el ASH y `density()` de R, y caza sus
   mutaciones.
4. `python3 precalculo/ensambla_apendicea.py`, luego `audita_texto_apendicea.py`,
   `prueba_texto.py apendicea`, `sin_aritmetica.py`, `campos_vivos.py`,
   `comentarios_cerrados.py` y `cuenta_sitio.py`.
5. `verifica_bloques.py --html Htmls_Espacial/apendice-a-densidad.html`, y después `--todos`.
6. `precalculo/audita_todo.sh --rapido` en el worktree, con el árbol aún sin commit.
7. **En el navegador** (preview con `.claude/launch.json`):
   - cada simulador a 1280 y a 375 px;
   - KaTeX dentro de las tablas, la consola sin errores, el cuestionario y los ejercicios;
   - capturas como prueba.
   - Después, una revisión independiente de un agente con la lente de
     `prosa-comprimida-se-vuelve-criptica`: cada leyenda explicada antes de usarse, y ninguna
     regla que su propio ejemplo desmienta.
8. Commits locales en tres pasos: infraestructura y cálculo, documento, portada y README. El
   push y el PR, cuando Javier lo pida.
