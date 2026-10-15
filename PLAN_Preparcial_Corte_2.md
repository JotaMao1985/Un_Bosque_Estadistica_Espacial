# Plan · Preparcial del Corte II

Estadística Espacial 2026-II (20929) · Universidad El Bosque

Instrumento **formativo, sin nota y repetible** con el que el estudiante comprueba, antes del
Parcial 2, si tiene el Corte II —patrones puntuales: los capítulos 4 y 5—: procedimientos,
conceptos, interpretación, lectura de gráficos y, esta vez, también **producir**: cinco ejercicios
guiados sobre un patrón que ningún documento del curso ha usado. Es el hermano del preparcial del
Corte I (`PLAN_Preparcial_Corte_1.md`) y hereda su maquinaria, sus reglas y sus lecciones.

**Estado:** 🟡 **construido, integrado y con cuatro rondas de auditoría de contenido aplicadas
(2026-10-05); falta la comprobación de la cuarta ronda y el cierre (P3.3).** Ver §0.1 y la
bitácora (§11). Hay un defecto del capítulo 5 que decide Javier (§11, cuarta ronda).

---

## 0. Cómo retomar esto en otra sesión

Abrir la conversación en la carpeta `Estadistica espacial/` y pedir que lea **este archivo** antes de
tocar nada. El trabajo vive en el worktree `.claude/worktrees/preparcial2`, rama
`claude/preparcial-corte-2`, que sale de `main` en `a1afe22`. **Un worktree nuevo nace sin `datos/` ni
`precalculo/cache/`**: hay que copiarlos de la copia principal (memoria
`worktrees-datos-estadistica-espacial`).

### 0.1 · Estado

| Tarea | Estado |
|---|---|
| P0.1 · `alcance_preparcial2.py` + su arnés | ✅ 22 dentro, 4 fuera, 10 anclas + recuento de módulos; arnés 8/8 |
| P1.1 · `genera_preparcial2.R` → `preparcial2_datos.json` | ✅ 133 cifras reutilizadas, 17 cálculos nuevos, 6 gráficos, 15 errores, 5 ejercicios, 24 anclas (≈ 6 min) |
| P1.2 · `audita_preparcial2.py` | ✅ 194 comprobaciones en 7 familias, 0 fallos |
| P1.3 · `prueba_auditor_preparcial2.py` | ✅ 90 de 90 defectos cazados, 75 de 75 tipos vistos fallar, cada inyección contra su comprobación |
| P2.1 · esqueleto, módulo del alcance y catálogo de errores | ✅ (catálogo de **quince**, no doce: §11) |
| P2.2 · bloques A y B (22 preguntas) | ✅ |
| P2.3 · rutinas y bloque C | ✅ `verifica_bloques`: 78 de 78 cifras `#>` |
| P2.4 · los cinco ejercicios guiados | ✅ toda demanda con respuesta; toda cifra de las respuestas en el JSON |
| P3.0 · auditoría de contenido (§9) | 🟡 cuatro rondas aplicadas (la cuarta, siete vías, 2026-10-05); comprobación de la cuarta en curso |
| P3.2 · cubo, portada, enlace en el cap. 5, README | ✅ |
| P3.3 · navegador, teléfono y cierre | ⛔ |

### 0.2 · Lo primero que hay que saber

Las once reglas del §0.2 del plan del Corte I valen aquí tal cual. Las que más cuestan, resumidas:

1. **R con el envoltorio** (`precalculo/rscript.sh`), nunca `Rscript` a pelo.
2. **Los módulos se numeran solos** desde `CONSTRUCTORES`; no hay números escritos.
3. **Ninguna cifra a mano.** Una cifra de un capítulo no se copia: se **referencia** (archivo +
   ruta + `que`) en `reutilizado`, y el auditor la vuelve a resolver. **Si se regenera el capítulo 4
   o el 5, hay que volver a correr la cadena de este preparcial.**
4. **Las glosas verbales son cifras a mano** («trece veces», «la mitad»): o se citan por su clave o
   no se dicen.
5. **Las opciones se barajan solas**: ninguna retro puede nombrar una posición (`POSICIONALES`).
6. **Un bloque de código no se interpola, se concatena** (Python 3.10 no admite `\` dentro de una
   expresión de f-string).
7. **El auditor corre con el Python de `geo_env`** (`precalculo/versiones_py.json`).
8. **El `que` de una cifra se publica** (lo imprime el catálogo de errores).
9. **El `descripcionGrafico` es contenido**: es lo único que recibe quien no ve el lienzo; tiene que
   ser cierto **y suficiente** para contestar.
10. Si el arnés de inyección sale en rojo, la primera hipótesis es que el defecto está **en la
    inyección**.

Y cuatro propias de este documento:

11. **El nombre de una ruta no dice lo que mide; el `.R` sí.** Ya pasó escribiendo este plan:
    `m2.urbana_hist.teorico` parece la referencia «con las celdas recortadas» y es **una Poisson de
    media común** (`genera_cap4.R:360`). Antes de redactar sobre una cifra, abrir el generador.
12. **La clave no puede ser sistemáticamente la opción más larga.** El banco del Corte I se
    contestaba al 92 % sin saber nada por esa sola heurística (§13.3 de su plan). Aquí nace con
    guarda: `len(clave) − max(len(distractores)) > 20` para el ensamblado.
13. **Superficies publicadas que un enunciado nuevo puede duplicar: cinco, no una** (§3).
14. **Murchison es de los ejercicios.** Ninguna pregunta ni rutina puede adelantar una solución de
    los ejercicios guiados.

### 0.3 · La cadena, en orden

```
precalculo/rscript.sh precalculo/genera_preparcial2.R    # el precálculo
python3 precalculo/ensambla_preparcial2.py               # el HTML
python3 precalculo/prueba_alcance_preparcial2.py         # el arnés del alcance
python3 precalculo/verifica_bloques.py --html Htmls_Espacial/preparcial-corte-2.html
<geo_env>/python precalculo/audita_preparcial2.py        # el auditor independiente
python3 precalculo/sin_aritmetica.py
python3 precalculo/campos_vivos.py
python3 precalculo/cuenta_sitio.py
precalculo/audita_todo.sh --rapido                       # lo descubre todo por el nombre
```

`audita_todo.sh` **no se edita**: su bucle de preparciales descubre `preparcial2_datos.json`,
`audita_preparcial2.py`, `prueba_alcance_preparcial2.py` y `prueba_auditor_preparcial2.py` por el
nombre. Un nombre distinto hace nacer el preparcial fuera del arnés **en silencio**.

---

## 0.6 · Las decisiones de Javier (2026-10-03)

| # | Decisión | Elegido | Lo que descarta |
|---|---|---|---|
| D1 | **Alcance** | Capítulos 4 y 5, **módulos 1–11** de cada uno (22) | Las autoevaluaciones (m12) y los simulacros de quiz (m13): no son contenido. 3.9–3.11 tampoco: el syllabus pone el Parcial 2 sobre el Módulo II |
| D2 | **Ubicación** | Página propia `Htmls_Espacial/preparcial-corte-2.html` | Un módulo 14 del cap. 5: evaluaría dos capítulos desde uno y obligaría a reauditarlo entero |
| D3 | **Carácter** | Formativo, repetible, con retroalimentación por opción; **el parcial va aparte** | Que sus preguntas sean el banco del parcial, como pasó en el Corte I (§8.6 de `PLAN_Parcial_Corte_2.md`) |
| D4 | **Fecha del parcial** | **Jueves 15 de octubre de 2026** | — |
| D5 | **Ejercicios guiados** | **Cinco, sobre datos nuevos**, con solución calculada en R | Calcarlos del Corte I, que los dejó sin hacer (P2.4) |
| D6 | **Enlace en el cap. 5** | **Al cierre de los módulos 12 y 13** (recuadro en «Dónde sigue esto» y una línea al final del simulacro) + tarjeta en la portada | Un solo enlace |

**«Publicarse al final del capítulo 5»** se entiende como D2 + D6: el preparcial es un documento
propio y el capítulo 5 termina mandando a él.

---

## 1. Qué evalúa, módulo por módulo

| Origen | Módulos | Lo que tiene que quedar comprobado |
|---|---|---|
| Cap. 4 | m1–m11 | La ventana es parte del estimador · λ = n/|W| y cuándo describe el patrón · los tres regímenes y Clark-Evans · las dos propiedades de CSR y cuánto se mueve el azar · el χ² de cuadrantes y lo que no ve · el tamaño de la celda y el supuesto del χ² · G, F y J · K y L · g · el borde · envolventes, test global y nsim |
| Cap. 5 | m1–m11 | De contar a suavizar · núcleo frente a ancho · los cuatro selectores y el que no seleccionó · la corrección de borde de la KDE y la masa · tres mapas que no son el mismo · intensidad relativa · rhohat y su cola · el Poisson inhomogéneo, su verosimilitud y la cuadratura · leer un `ppm` · el diagnóstico contra el modelo · conglomerados, la corrección de `kppm`, el efecto de diseño y Hawkes |

**Regla de cobertura, mecanizada:** cada uno de los 22 módulos toca al menos una pregunta, y ninguna
pregunta apunta fuera de ellos. La comprueban el ensamblador y el auditor.

---

## 2. Estructura del documento — 7 módulos

| # | Módulo | Contenido | Componentes |
|---|---|---|---|
| 1 | **Qué entra en el parcial, y qué no** | Los 22 módulos con enlace, los cuatro que no entran por su nombre, la fecha y cómo se usa | tablas, sin quiz |
| 2 | **Bloque A · capítulo 4** | 11 preguntas, una por módulo | quiz de los cuatro tipos |
| 3 | **Bloque B · capítulo 5** | 11 preguntas, una por módulo | quiz de los cuatro tipos |
| 4 | **Seis rutinas que el parcial puede pedir** | Seis pares R/Python con salida real y una línea que comprueba | `.code-tabs` con `#>` |
| 5 | **Bloque C · los dos capítulos a la vez** | 6 preguntas que solo se contestan cruzando el 4 y el 5 | quiz |
| 6 | **Cinco ejercicios sobre el oro de Murchison** | El patrón entero, de la ventana al modelo, con solución calculada | `.ejercicio-guiado` |
| 7 | **Los doce errores que se repiten** | Cada uno con su cifra medida y el módulo al que volver, y la ruta de repaso | tarjetas + tabla |

**28 preguntas** (11 + 11 + 6), **6 rutinas**, **5 ejercicios**, **12 errores**. Reparto por tipo
con al menos uno de cada en cada bloque: ~11 `opcion`, ~6 `multiple`, ~6 `numerica`, ~5 `grafico`.

---

## 3. Las superficies publicadas que un enunciado nuevo puede duplicar

La lección del Taller 2 (§3.7 de su plan) fue que había **dos**; para el Corte II son **cinco**, y
el inventario está hecho (2026-10-03):

| Superficie | Dónde | Cuántas |
|---|---|---|
| Autoevaluaciones | cap. 4 m6 (`cap4-trampas`, 4) y m12 (`cap4-quiz`, 8); cap. 5 m6 (`cap5-trampas`, 4) y m12 (`cap5-quiz`, 8) | 24 |
| Ejercicios guiados | cap. 4 m12 y cap. 5 m12 | 10 |
| Simulacros de quiz | cap. 4 m13 (`cap4_simulacro.json`, 10) y cap. 5 m13 (`cap5_simulacro.json`, 11) | 21 |
| Banco de la defensa del Taller 2 | `ensambla_taller2.py`, `BANCO_DEFENSA` | 36 |
| Afirmaciones falsas del Taller 2 | `ensambla_taller2.py`, `AFIRMACIONES_FALSAS` | 12 |

**El criterio no es «ningún concepto repetido»** —con 22 módulos y 103 ítems publicados eso es
imposible y además no es deseable: un preparcial repasa—, sino **ningún ítem repetido**. Cada
pregunta tiene que aportar uno de estos tres: un ángulo que ningún ítem publicado pide, una
transferencia a datos o a una situación nueva, o un cruce entre los dos capítulos. Donde una
pregunta toca un concepto ya publicado, el blueprint (§4) dice cuál y por qué no lo duplica.

Prohibido además, porque son claves publicadas: preguntar la tasa media del Hawkes (quiz cap. 5, P2),
el átomo de la G (quiz cap. 4, P4), el σ mínimo con la mitad de columnas (trampas cap. 5, P3), las
piezas de K̂ a mano sobre una pareja de recuentos (simulacro cap. 5, P3), la integral del
semiplano (simulacro cap. 5, P10) y la intensidad en un punto con tres sedes (simulacro cap. 5, P7).

---

## 4. El blueprint de las 28 preguntas

Las cifras van por su ruta en `capN_datos.json`; las marcadas **[nuevo]** las calcula
`genera_preparcial2.R`. El blueprint es un contrato de **qué** evalúa cada pregunta, no de su
redacción, que es P2.2/P2.3 y pasa por la auditoría de contenido.

### 4.1 Bloque A · capítulo 4

| # | Mód. | Tipo | Qué evalúa | Cifras | Por qué no duplica |
|---|---|---|---|---|---|
| A1 | 4.1 | numerica | **La intensidad del resto del Distrito** (D.C. menos perímetro urbano, con su n y su |W|): la urbana es 71.2 veces la del resto, y la λ del D.C. no describe ninguno de los dos regímenes | [nuevo] `resto_dc` (por geometría) | *(reescrita en P3.0: la versión del factor 4.21 era casi el simulacro 5 del cap. 4)* nadie pregunta por la ventana que queda al restar |
| A2 | 4.2 | grafico | Leer barras contra la línea de referencia **sabiendo que esa línea es una Poisson de media común**, y que con celdas recortadas un Poisson homogéneo ya daría un índice de 15.23: el patrón explica lo que sobra | `m2.urbana_hist.*`, `m2.urbana.dispersion`, `dispersion_nula` | el simulador del módulo no pregunta; el banco del Taller 2 lo pide abierto |
| A3 | 4.3 | opcion | Las mismas sedes con la ventana del D.C. dan una R mucho menor: R divide por la distancia del azar **con la λ de esa ventana** | [nuevo] `ce_dc` (R ingenua en el D.C.), `m3.bogota.clark_evans` | ningún ítem cruza Clark-Evans con la ventana |
| A4 | 4.4 | multiple | **Diez veces más puntos en el mismo cuadrado**: el sesgo de R se encoge (1.058 → 1.017) pero el azar de R también, y la proporción bajo 1 apenas cambia (21.9 % → 21.7 %); la varianza del conteo crece con λ | [nuevo] `denso` (2000 × λ = 650) | *(reescrita: sus dos claves eran dos preguntas del banco del módulo 4)* nadie pregunta cómo escala el sesgo |
| A5 | 4.5 | opcion | El χ² de redwood y su rebarajado son idénticos con 5×5 **y dejan de serlo con 10×10**: la rejilla es la escala a la que el test mira | `m5.*`, [nuevo] `chi2_10x10` de los dos | trampas P2 pide qué se concluye de dos χ² iguales; esto pide qué pasa al cambiar la escala |
| A6 | 4.6 | grafico | La esperanza mínima por rejilla, **ventana urbana contra un rectángulo de la misma área** (n/k²): lo que los separa es la geometría, no el número de sedes ni su patrón (la esperanza no mira dónde están) | `m6.bogota.*` + serie `rectangulo` | *(reescrita: la versión anterior era la solución del ejercicio guiado 3 del cap. 4)* |
| A7 | 4.7 | multiple | **G frente a F en los pinos suecos**, con las tres medianas del módulo 7 (G 0.825 m, F 0.488 m, CSR 0.546 m): las dos apuntan a la regularidad, ninguna dice si es más que el azar, y una J sobre 1 en las 34 distancias tampoco | [nuevo] `gf_suecos` (funciones de `puntual.R`) | *(ronda 4: la versión de J sobre los pinos japoneses no comprobaba el núcleo del 4.7, y el enunciado decía que eran aleatorios)* el quiz P3 pide la definición; nadie lee las medianas sobre un patrón nuevo |
| A8 | 4.8 | multiple | Ventajas y límites de K: más allá del primer vecino, referencia sin λ, no identifica el proceso (Baddeley-Silverman), ciega a la dirección, alcance limitado por la ventana | `m8.bogota.vecino_max`, `m8.abanico.*` | quiz P5 es la acumulación; esto es el balance entero |
| A9 | 4.9 | grafico | **Qué afirma g a unos 3 km** (1.149): un anillo, no un disco (K/πr² vale 1.20 ahí), ni una lectura de G, ni un conteo de vecinas | `m9.bogota.*`, `m11.bogota.obs/teo` | *(reescrita: era el banco «Un máximo en el borde izquierdo», y afirmaba exceso en el último nodo, que cabe en el azar)* |
| A10 | 4.10 | multiple | **El peso de traslación** |W|/|W ∩ (W+v)| sobre la ventana urbana: depende solo de v (longitud y dirección: 98.24 % hacia el este, 98.36 % hacia el norte), nunca vale 1, crece con la distancia | [nuevo] `traslacion` (solape exacto) | *(reescrita: un distractor copiaba la afirmación falsa n.º 8 y las claves eran del banco)* |
| A11 | 4.11 | numerica | Con nsim = 199, qué `nrank` da un contraste puntual al 5 %: 2k/(nsim+1) = 0.05 | [nuevo] `nrank_199` | quiz P8 es el ensanchamiento; 199 no aparece en ningún documento |

### 4.2 Bloque B · capítulo 5

| # | Mód. | Tipo | Qué evalúa | Cifras | Por qué no duplica |
|---|---|---|---|---|---|
| B1 | 5.1 | opcion | **A qué tiende la KDE corregida de Kennedy con σ enorme**: a n/\|W\| = 6.80, contar con una vecindad que lo abarca todo | `m1.ventana.*`, [nuevo] `limite` | *(ronda 4: atributo contra geometría era un recuadro del 5.1, no su núcleo)* |
| B2 | 5.2 | grafico | **Un informe con una escala por mapa** concluye que el ancho no cambia la intensidad: la curva del pico lo desmiente | `m2.familia.*` | *(ronda 4: la versión anterior se contestaba recordando la frase del capítulo)* |
| B3 | 5.3 | numerica | El tope de `bw.ppl`: la mitad del diámetro de la ventana. Sobre un rectángulo nuevo, cuánto devuelve si choca; la regla va solo en la retro | [nuevo] `tope_ppl` | quiz P4 da el valor y pide qué es; aquí hay que saber dónde está la pared *(ronda 4: el enunciado y la pista daban la regla)* |
| B4 | 5.4 | opcion | Diagnóstico al revés: la integral te da 270.36 con n = 262. ¿Qué corrección usaste? La de por defecto pone masa de más; sin corregir faltaría | `m4.tabla[3].*` | trampas P2 y el E2 del cap. piden qué corrección conserva n; esto pide reconocerla por el síntoma |
| B5 | 5.5 | multiple | Tres capas: la unidad de la pesada son evaluados por km²; la pareja que menos se parece es edificios contra estudiantes; un estudiante cuenta donde estudia | `m5.*` | quiz P5 pide cuál es «la demanda»; esto pide qué mide cada capa |
| B6 | 5.6 | numerica | Probabilidad de caso frente a riesgo relativo: en el máximo de chorley, P = 0.33885 → r = p/(1−p) | `m6.chorley.p_max` → [nuevo] `rr_max` | trampas P4 es el orden de niveles; nadie pide pasar de una escala a la otra |
| B7 | 5.7 | opcion | Por qué la covariable tiene que venir de fuera del patrón: si sale de los puntos, la curva se contesta sola | `m7.bei.n` | quiz P6 es la cola; esto es la condición de la covariable |
| B8 | 5.8 | numerica | **La identidad del intercepto con la cuadratura dentro**: `ppm(X ~ 1, forcefit = TRUE)` sobre Kennedy da n/Σw = 6.813, no n/\|W\| = 6.803 | [nuevo] `forzado` | *(ronda 4: la versión de ∫λ̂ = n traía la respuesta en el enunciado)* el módulo 8 lo mide sobre la ciudad |
| B9 | 5.9 | opcion | Qué autoriza la tabla de `~ xc + yc`: un gradiente hacia el este **si las sedes fueran independientes**, un 2.40 % menos por km (lectura multiplicativa); sobre el norte-sur, nada | `m9.centrado.*`, [nuevo] `ebeta` | quiz P7 es la singularidad y el AIC |
| B10 | 5.10 | grafico | La K inhomogénea dividida por la media del modelo: el exceso está en las escalas cortas y medias, de 59 m a unos 3.6 km | `m10.curva.*`, `primer_r_fuera_m`, `ultimo_r_fuera_m` | quiz P8 es el veredicto; esto es **dónde** |
| B11 | 5.11 | multiple | `kppm` y su corrección: con la isotrópica la escala de Thomas es 932 m y con traslación 1320 m; el estimador de K mueve las sedes por conglomerado un 93 %. **Distractor nuevo:** «Matérn, 1 782 m, saca conglomerados del doble de ancho» — σ y R no son la misma magnitud (distancia media 1 168 frente a 1 188 m) | `m11.ajustes[*]`, [nuevo] `escalas` | el E5 del cap. lo pide sobre redwood; *(P3.0: el distractor viejo era defendible con la tabla del capítulo)* |

### 4.3 Bloque C · los dos capítulos a la vez

| # | Repaso | Tipo | Qué evalúa | Cifras |
|---|---|---|---|---|
| C1 | 5.10 | grafico | **Qué parte del exceso contra CSR se llevó la intensidad variable**: poco a distancias cortas (7.7 % del exceso en el primer nodo) y todo a las largas; las dos bandas son de mínimo y máximo, al 0.2 % | serie `g_dos` y su `forma` | *(reescrita: era el quiz P8 del cap. 5)* |
| C2 | 5.4 | multiple | «Corrección de borde» en K y en la KDE: misma expresión, otra operación. Cara en K (por perímetro), gratis en la KDE (por píxel); en K faltan vecinos y la KDE pierde masa; `kppm` elige la cara sin decirlo | `m10.coste.veces_isotropica_sobre_traslacion` (4), `m4.coste_segundos.*` (5) |
| C3 | 5.10 | opcion | 52 % de simulaciones de CSR fuera de su banda (cap. 4) frente a 7.7 % de las del modelo (cap. 5): lo explica sobre todo el **nivel puntual** —una banda al 95 % por cuantiles contra el mínimo-máximo, al 0.2 %— | `m11.bogota.tasa_salida.*` (4), `m10.tasa_salida.*` (5) — **verificado en los dos generadores** |
| C4 | 5.2 | opcion | Tamaño del cuadrante y ancho de banda: los dos fijan la escala y ninguno lo dicta la teoría; el núcleo además solapa vecindades y no impone bordes rectos | `m6.redwood_rechazos` (4), `m2.familia.caida_pct` (5) |
| C5 | 5.11 | numerica | El efecto de diseño: con Thomas, la varianza de xc se multiplica por 26.03; ¿a cuántas sedes independientes equivalen las 2107? | `m11.tendencia.efecto_diseno`, `n` → `n_efectivo` |
| C6 | 5.8 | multiple | La ventana entra en cada estimador del Corte II: en λ̂, en los sitios de F, en los pesos de K, en e(u) de la KDE y en la cuadratura de `ppm` (1.22 km² sin contar) | `m7.bogota.f_sitios` (4), `m8.forzado.*` (5) |

---

## 5. Las seis rutinas

Con salida **ejecutada** y una línea que comprueba al final de cada una. Pares R/Python; cuando
Python no puede reproducir la cifra de R (otro generador, otra discretización), comprueba la
**propiedad** y lo dice en un comentario, como hacen los capítulos. Todas sobre datos que el
estudiante ya tiene (Bogotá, Kennedy, los canónicos); **ninguna sobre Murchison**.

1. **Del archivo al `ppp`, con la ventana declarada** — `as.owin`, puntos descartados, λ en km².
   Comprueba: `npoints + descartados == filas`.
2. **El test de cuadrantes con su supuesto** — `quadrat.test` y la esperanza mínima de la rejilla.
   Comprueba: `min(expected) >= 5` antes de leer el p.
3. **Envolvente y test global, con nsim declarado** — `envelope` + `dclf.test` sobre las mismas
   simulaciones. Comprueba: el p no baja de 1/(nsim+1).
4. **El ancho, la pared y la masa** — los cuatro selectores, la comprobación del tope, y
   `diggle = TRUE` integrando a n. Comprueba: `abs(integral − n)`.
5. **Un `ppm` que se puede leer** — coordenadas centradas y en km, un error estándar por coeficiente.
   Comprueba: `length(ee) == length(coef)`.
6. **`kppm` con la corrección escrita** — las dos correcciones y la diferencia de parámetros.
   Comprueba: la corrección viaja en el objeto.

---

## 6. Los cinco ejercicios: el oro de Murchison

**Por qué `murchison`.** Es el patrón canónico de yacimientos de oro de Australia Occidental
(spatstat.data): 255 yacimientos, las fallas geológicas como segmentos y el afloramiento de
*greenstone* como ventana. **Ningún documento del curso lo usa** —ni capítulos, ni taller, ni los
dos quices—. Y la exploración del 2026-10-03 enseñó que reproduce, sobre datos nuevos, casi todas las
trampas de los dos capítulos, varias con el veredicto al revés que en Bogotá, que es lo que obliga a
razonar en vez de recordar. Cifras de la exploración (**todavía no ancladas**; las fija P1.1):

| Lo medido | Valor |
|---|---|
| Ventana | rectángulo de 329.8 × 401.7 km, 132 497 km² |
| Greenstone | 9.2 % del área, **115 piezas** y 18 agujeros (133 anillos), 7 176 vértices, 5 005 km de perímetro; contiene **219 de los 255** yacimientos |
| Cociente de intensidades dentro/fuera del greenstone | 59.87 (exacto) |
| Clark-Evans en el rectángulo | 0.308 |
| Clark-Evans dentro del greenstone | **0.969 sin corregir · 0.621 corregida** |
| K̂ a 10 km dentro del greenstone | sin corregir 282.6 < πr² = 311.5 < traslación 496.0 |
| Selectores (km) | diggle 2.34 · ppl 5.95 · CvL 83.7 · scott 25.6 / 41.2: **×36** |
| Masa a σ = 83.7 km | sin corregir 181.3 · defecto 268.4 · Diggle 255.00 |
| `ppm(~ x + y)` en metros | **información de Fisher singular** (como Bogotá en EPSG:9377) |
| `rhohat` sobre la distancia a la falla | razón total **infinita**; en el bulto, 26.2: aquí la covariable sí manda |
| `ppm(~ greenstone)` | e^β = 53.5 con la cuadratura por defecto (nd = 40), 59.56 con nd = 400, frente a **59.87 exacto** |
| Kinhom contra `ppm(~ falla)` | 38 % de radios fuera, DCLF p = 0.01 (el mínimo con 99) |
| Kinhom contra `ppm(~ greenstone + falla)` | 14 % fuera, DCLF p = 0.11 |
| `kppm(~ falla, Thomas)` | ee ×3.6; z de −12.9 a −3.6: **el coeficiente sobrevive** (en Bogotá no) |

| Ejercicio | Módulos | Lo que pide decidir |
|---|---|---|
| **E1 · Dónde se buscó el oro** | 4.1, 4.2, 4.5, 4.6 | Dos ventanas defendibles; λ en cada una; el χ² con su supuesto rejilla por rejilla; qué dice un rechazo y qué no |
| **E2 · El borde que da la vuelta al régimen** | 4.3, 4.4, 4.8, 4.10 | Clark-Evans y K dentro del greenstone, con y sin corrección; por qué el sesgo tiene siempre el mismo signo, y cuál creer |
| **E3 · Cuatro anchos para el mismo oro** | 5.1–5.4 | Los selectores, la comprobación de la pared, la masa con las tres correcciones; qué σ se publica y cómo se declara |
| **E4 · La falla, el greenstone y la cuadratura** | 5.7–5.9 | `rhohat` total y en el bulto; `ppm` en metros y en km; el coeficiente del greenstone contra su valor exacto y la cuadratura que los separa |
| **E5 · ¿Explican las covariables la agregación?** | 5.10–5.11 | Envolventes contra dos modelos; `kppm` con la corrección declarada; qué autoriza un «no rechaza» |

Formato del cap. 5 tras M5 de su segunda revisión: **cada demanda del enunciado se contesta bajo
su propio fragmento literal**, y una guarda (`sin_contestar`) exige que todo «di», «explica»,
«calcula», «decide» y «¿…?» tenga respuesta. Un campo en el JSON no cuenta como respuesta.

---

## 7. Los doce errores que se repiten

Doce y no diez porque el Corte II cubre dos capítulos de tres semanas. Cada uno con su cifra medida
(por clave), el módulo al que volver y la frase de lo que **no** da error:

1. Publicar λ sin su ventana (4.1) · 2. Leer el índice de dispersión contra 1 con celdas recortadas
(4.2) · 3. Tomar «no rechaza cuadrantes» por CSR (4.5) · 4. Elegir rejilla sin mirar el supuesto
(4.6) · 5. Leer «exceso de parejas» como atracción (4.8, 4.9) · 6. Ignorar el borde (4.10) · 7. Leer
la banda puntual como contraste de la curva entera (4.11) · 8. Publicar la pared como ancho óptimo
(5.3) · 9. Creer que la corrección por defecto conserva n (5.4) · 10. El `relrisk` del revés (5.6) ·
11. Leer el titular de una `rhohat` (5.7) · 12. Comparar AIC de `ppm` con cuadraturas distintas y
leer la z de un Poisson con datos agrupados (5.8, 5.11).

El nombre «Los doce errores» se ata a `len(ERRORES)` con la guarda del Corte I.

---

## 8. Fases y tareas

Cada una deja un HTML que abre y funciona (la navegación declara solo los módulos que existen).

### P0.1 — `alcance_preparcial2.py` y su arnés
Calcado de `alcance_preparcial1.py`: los títulos se leen del `courseData` publicado, con anclas que
paran. **Anclas:** cap. 4 m11 «envolventes», m12 «autoevaluación», m13 «simulacro»; cap. 5 m4
«borde», m9 «ppm», m12 «autoevaluación», m13 «simulacro». `FUERA` = m12 y m13 de los dos.
**Acepta:** 22 módulos; `prueba_alcance_preparcial2.py` con un módulo de más, uno de menos y un
título movido, y las tres paran.

### P1.1 — `genera_preparcial2.R`
`reutilizado` (con `que` que se publica), `nuevo` (A3, A5, A11, B3, B6, B8, C5 y las soluciones de
los cinco ejercicios), `graficos`, `errores`, anclas que paran. Exporta los datos de Murchison a
`precalculo/salidas/preparcial2_murchison_*.csv` para que el auditor rehaga en Python lo que se pueda.
**Acepta:** reproducible byte a byte (dos corridas, `diff`); toda cifra con ancla o con recálculo en
el auditor; las 22 rutas de módulo cubiertas.

### P1.2 — `audita_preparcial2.py` · seis familias
1. **Cifras nuevas** rehechas en Python desde la fuente (los CSV de Murchison, los `.gpkg` de
   Bogotá, `cap4_datos.json` para el rebarajado). Lo que solo sabe hacer spatstat (selectores,
   `ppm`, `kppm`, envolventes) va anclado en R por dos caminos y se declara así, sin fingir
   independencia.
2. **Sincronía** — `reutilizado` contra los capítulos; el JSON incrustado contra el del disco.
3. **Cobertura** — 22 de 22, `repaso` resuelto contra el capítulo publicado.
4. **Retroalimentación completa.**
5. **No filtración** — enunciado y pista no regalan la clave; posición; **longitud de la clave**
   (§0.2, regla 12).
6. **Ejercicios** — toda demanda contestada bajo su fragmento literal; toda cifra de la solución
   presente en el JSON.

### P1.3 — `prueba_auditor_preparcial2.py`
Una inyección por tipo de comprobación como mínimo, sobre las tres superficies (JSON, HTML,
capítulos), y el recuento de tipos vistos fallar.

### P2.1 a P2.4 — el documento
Esqueleto + alcance + errores (P2.1); bloques A y B (P2.2); rutinas y bloque C (P2.3); ejercicios
(P2.4). Cada uno pasa `verifica_bloques`, el auditor y las guardas del ensamblador antes de pasar al
siguiente.

### P3.0 — Auditoría de contenido (§9)

### P3.2 — Integración
`cuenta_sitio.py` (el cubo de preparciales ya existe), tarjeta en `index.html`, enlace en los
módulos 12 y 13 del cap. 5 (`ensambla_cap5.py`, reensamblar y pasar `audita_cap5.py`,
`audita_texto_cap5.py` y `prueba_texto.py`), README, `.gitignore` (`!/PLAN_Preparcial_Corte_2.md`).
**Ojo:** los PR #8 y #9 tocan el HTML del cap. 5; quien llegue segundo reensambla.

### P3.3 — Navegador y cierre
Escritorio y 375 px; consola limpia; los cuatro tipos respondidos; el resumen manda al módulo
exacto; los lienzos con tinta y `aria-label`. Arnés completo en verde. **La pregunta de cierre:
¿qué quedó dicho y no mostrado?**

---

## 9. La auditoría de contenido

Las once vías de los §12.7 y §13.5 del plan del Corte I, con agentes de una vía cada uno y la regla de
que **los ciegos escriben sus respuestas antes de abrir la clave**:

| Vía | Qué caza |
|---|---|
| Contestar solo por la forma | la clave se adivina sin saber (la más larga, la más matizada, el eco) |
| Contestar como experto sin el curso | ítems que no exigen el material, claves ambiguas |
| Calcular sobre la serie | que la correcta sea cierta **sobre estos datos** |
| Leer las retros como afirmaciones | razones falsas detrás de veredictos correctos |
| Leer el distractor buscando si es verdad | opciones ciertas en «marca todo lo cierto» |
| ¿La pista mata al distractor? | pistas que nombran la operación |
| ¿Qué recibe quien no ve el gráfico? | `aria-label` falso o insuficiente |
| Contar los comentarios de cada pestaña | rutinas que en R enseñan y en Python solo calculan |
| Leer el `que` como texto publicado | descripciones de cifras mal nombradas |
| Abrir el `.R` antes de aceptar un nombre | la cifra no mide lo que su nombre dice |
| Cotejar contra las cinco superficies | ítems duplicados |

Y **resolver los cinco ejercicios a ciegas desde la página publicada**, cotejando después con el
JSON —al revés, la clave contamina la lectura (método de la auditoría del Taller 2)—.

---

## 10. Riesgos

| # | Riesgo | Mitigación |
|---|---|---|
| R1 | Se regenera el cap. 4 o el 5 y el preparcial miente en silencio | familia 2 del auditor; regla 3 del §0.2 |
| R2 | Una pregunta repite un ítem publicado | §3 y la vía de cotejo |
| R3 | La clave se adivina por la forma | guarda de longitud + agente ciego de forma |
| R4 | Un ejercicio pide algo que su solución no contesta | `sin_contestar` y la familia 6 |
| R5 | Los PR #8/#9 chocan con el enlace del cap. 5 | se reensambla; el preparcial no depende de ellos |
| R6 | La fecha: el preparcial tiene que estar fuera la semana del 5 de octubre | el orden de §8 deja un HTML útil desde P2.2 |

---

## 11. Bitácora

**2026-10-03 · El plan.** Lectura completa de los dos capítulos y de las cinco superficies; las seis
decisiones; la exploración de Murchison. Primer hallazgo antes de escribir una línea: la «referencia»
del histograma del módulo 4.2 no tiene en cuenta las celdas recortadas (regla 11).

**2026-10-03 · La construcción, y lo que apareció.**

- **La corrección por defecto de la KDE no se pasa siempre.** Con los pinos japoneses y σ = 0.1 se
  queda corta (63.998 con n = 65). El PR #9 (sin fusionar) ya corrige la frase del cap. 5 que lo
  daba por ley; el preparcial dice lo correcto en la pregunta 5.4, en la rutina 4 y en el E3.
- **`Kest` y las parejas justo en el corte.** Sobre `redwood` hay 32 parejas ordenadas exactamente a
  0.1, y la L a 0.1 no cuadra entre R y Python. *Corregido en P3.0:* no es «un convenio» que las deje
  fuera; `Kest` cuenta unas sí y otras no según el redondeo de cada distancia y hasta según la
  rejilla de r (0.07272 o 0.07213 entre 0.06543 y 0.07514). La rutina 3 coteja en 0.11 y ahora lo
  dice así.
- **`quadrat.test` es bilateral**: su p es el doble de la cola superior. El auditor lo destapó al
  comparar en log10 (diferencia constante de log10 2).
- **Sobre una ventana poligonal, la corrección de traslación de `Kest` aproxima el solape con
  píxeles**: dentro del greenstone, K̂(10 km) da 499.70 en R y 487.48 con solapes exactos (shapely).
  El ejercicio publica la de R; el auditor exige < 3 % y el orden sin corregir < πr² < corregida.
- **Murchison invierte varias lecciones de Bogotá**, que es por lo que se eligió: el coeficiente de
  la falla sobrevive o no según el modelo (z de −5.78 a −1.54 con Thomas en `~ G + D`), la covariable
  sí manda en el bulto (razón 26.2) y el Poisson `~ G + D` no se rechaza con el rango por defecto
  (DCLF p = 0.11). *Corregido en P3.0:* sobre r ≤ 20 km sí se rechaza, con las diez semillas.
- **El AIC del mismo `ppm` en metros y en km difiere 2n·ln(10⁶)**: dos AIC solo se comparan con las
  mismas unidades. Entra en la respuesta del E4.
- **El catálogo pasó de doce a quince** errores: la z de un Poisson con datos agrupados, la
  corrección no declarada de `kppm` y las coordenadas de siete cifras son errores de primera fila.
- **Dos defectos que solo vio el arnés de inyección**: el auditor buscaba «está en la página» en todo
  el HTML, que lleva el JSON incrustado (no podía fallar), y comparaba p-valores de 1e-110 contra un
  suelo absoluto (tampoco). Y el arnés daba por cazada toda inyección en el JSON porque fallaba
  siempre la sincronía con el HTML: ahora reescribe también el JSON incrustado.
- **El `aria-label` de los lienzos publicaba «&amp;nbsp;» literal**: las entidades no se decodifican
  en un atributo asignado desde JavaScript. La descripción se emite como texto plano y el auditor lo
  vigila.

**2026-10-03 · P3.0, primera ronda: ocho vías y lo que cambió.** Ocho agentes de una vía cada uno,
con los ciegos escribiendo antes de abrir la clave: forma, experto sin el curso, verdad del cap. 4,
verdad del cap. 5, los cinco ejercicios resueltos a ciegas, prosa/rutinas/catálogo, duplicados contra
las cinco superficies y registro. Informes en el scratchpad de la sesión (`p30/informe_*.md`).
Ningún hallazgo dejó una clave falsa sin remedio, pero dos BLOQUEA y mucho más de fondo:

- **BLOQUEA · C3.** La clave decía que «la banda del capítulo 4» contrasta al 5 %. La que el capítulo
  **dibuja** es la del mínimo y el máximo (0.2 %, `nrank = 1` en la caché); el 52 % se midió contra
  otra, de cuantiles al 95 %, que `tasa_salida()` construye por dentro y nunca se dibuja. El
  enunciado y la retro lo dicen ahora así, y C1 declara que sus dos bandas son de mínimo y máximo.
- **BLOQUEA · B11.** El distractor «cambiar de modelo mueve los parámetros más que cambiar de
  corrección» era defendible con la tabla del capítulo (932 → 1 782 m al pasar a Matérn), porque la
  escala de Thomas es una σ y la de Matérn un radio. Pasa a ser el distractor que enseña eso, con la
  distancia media al centro calculada (1 168 frente a 1 188 m).
- **Cuatro duplicados de ítems publicados** (A4, A6, A9, A10: dos preguntas del banco, la solución de
  un ejercicio guiado, una afirmación falsa copiada palabra por palabra) y dos casi-duplicados
  (A1, C1) cambian de ángulo: §4. Los demás «casi» se quedan como transferencia a datos, que el §3
  admite; el banco del Taller 2 pregunta en abstracto.
- **Forma: 22 de 22 adivinadas sin saber.** Pistas con las palabras de la correcta, pistas de las
  múltiples que repartían los temas, absolutos solo en los distractores, la correcta como única con
  salvedad, textos alternativos con la conclusión y fugas cruzadas (C1 citaba la clave de A9; B11
  desmentía un distractor de C2). Reescritas las 22: pistas que apuntan al razonamiento, «Son N.» en
  las múltiples, distractores con salvedad, arranques iguales, textos alternativos con valores y sin
  lectura. La guarda de longitud saltó con la reescritura (la correcta, la más larga en 11 de 15) y
  se reequilibró a 5 de 15.
- **E5 casi BLOQUEA.** «No hay evidencia contra el modelo» solo valía con el rango por defecto de r,
  82 km; sobre r ≤ 20 km el DCLF rechaza `~ G + D` con las diez semillas (0.01–0.04). Ahora el
  enunciado fija los dos tramos de antemano, todo el ejercicio va con `nd = 400` (la cuadratura que
  el E4 deja buena: la fracción de radios fuera pasaba del 1 % al 14 % solo por la malla, y se quitó)
  y una guarda repite el veredicto con diez semillas. Pide `set.seed(2026)` «justo antes de cada
  `envelope`», porque con una sola semilla las cifras cambiaban.
- **Los otros ejercicios.** E1: «fuera del greenstone» por `setminus.owin` pierde el yacimiento 246,
  que está sobre el borde derecho del rectángulo (35 y no 36); el enunciado fija el convenio y la
  respuesta enseña la trampa. E2: la subpregunta del sesgo, publicada en el ejercicio guiado 5 del
  cap. 4, se cambia por medir cuánto borde hay (66.7 % de los yacimientos más cerca del borde que de
  su vecino, frente al 4.7 % de las sedes). E3: la respuesta ahora **decide** (bw.ppl, 5.95 km, con
  Diggle) y la rejilla pasa a `dimyx = 1024`, porque con 128 × 128 las celdas miden ~3 km y ni el σ de
  bw.diggle ni el de bw.ppl cubren las tres celdas que el cap. 5 pide; con el σ de bw.diggle la
  corrección por defecto **se queda corta** (254.80), otra prueba de que no es una ley. E4: la razón
  «infinita» se explica bien (ρ vale cero exacto en 138 de 512 valores, no en todo el tramo), el
  bloque metros/km pasa a preguntar por el AIC, y se concilia con el quiz P7 (β cambia un 2.7 %).
- **Prosa.** `ppp()` no descarta «en silencio»: avisa (estaba en A1, en el catálogo y en el E1). La
  rutina 6 proponía «leer la corrección del objeto», y con la llamada por defecto el objeto no la
  guarda (`NULL`): ahora la rutina lo muestra. Las `que` del catálogo se reescribieron donde la cifra
  no decía lo que medía (el 0.08 de chorley, el 7.7 % sin su nivel, «9 rejillas rechazan» cuando 8 de
  9 rompen el supuesto, el último nodo de g sin su radio).
- **Defectos de los CAPÍTULOS, que el preparcial ya no repite pero que siguen allí** (para Javier):
  el módulo 11 del cap. 4 llama «intervalo al 95 %» a una banda de mínimo y máximo; el módulo 2 del
  cap. 4 rotula la línea del histograma como «lo que daría una intensidad constante» (es una Poisson
  de media común); el módulo 9 del cap. 4 afirma exceso «en cada anillo, también a escala de
  kilómetros» cuando el último nodo cabe en el azar; el módulo 10 del cap. 5 dice que «a escala de
  kilómetros el modelo ya da cuenta», falso entre 1 y 3.6 km; el módulo 11 del cap. 5 compara escalas
  de Thomas y Matérn como si fueran la misma magnitud y no publica la μ de Matérn; el módulo 5 del
  cap. 5 da correlaciones distintas en R y Python sin decirlo; y `genera_cap5.R` escribe a mano los
  segundos de la KDE que el JSON presenta como medidos (el preparcial dejó de citarlos).

**2026-10-03 · P3.0, segunda y tercera ronda.** Experto sin el curso contra los capítulos (28 de 28
con la clave) y dos vías de forma. El experto dejó un BLOQUEA —A04 decía «a menos puntos se les
escapa el vecino», falso en número— y cuatro IMPORTANTE (B09-b y A05-a defendibles, la retro de
C01-d, la nota del rótulo del capítulo en A02); la forma seguía en 22 de 22. La tercera ronda puso
cifras reales en los distractores, igualó los arranques y quitó el cruce de C01 a C03.

**2026-10-05 · P3.0, cuarta ronda: siete vías a petición de Javier («revisa redacción, coherencia
narrativa, pertinencia, gráficos, planteamiento, barajado y que evalúen lo que deben»).** Siete
agentes sobre una copia fija de la página: forma, estudiante con el curso, pertinencia, verdad de
cada afirmación, redacción y narrativa, gráficos (Chrome sin ventana por CDP, 1280 y 375 px) y
ejercicios y rutinas (resueltos a ciegas en R). Informes en el scratchpad de la sesión
(`p40/informe_*.md`). Lo que cambió:

- **Un defecto del CAPÍTULO 5 que nadie había visto (para Javier).** `genera_cap5.R` llama
  `envelope(f_centr, Kinhom, …)` sin `lambda`, y entonces `Kinhom` no divide por la intensidad del
  modelo: estima λ̂ en cada patrón —el dato y cada simulación— por núcleo, con el σ por defecto de
  `density.ppp`, un octavo del lado corto del marco (2 934 m en la ventana urbana). El generador del
  preparcial lo comprueba ahora contra la curva publicada (diferencia 7e-13). Con `lambda = f_centr`
  la curva queda fuera de la banda en los 100 nodos (199 simulaciones, DCLF p = 0.005): el «pasados
  3.6 km el modelo de intensidad ya da cuenta» del módulo 10 lo pone el núcleo, no el gradiente. El
  preparcial dejó de atribuírselo al gradiente (B10, C01, el catálogo) y lo dice; el capítulo sigue
  igual hasta que Javier decida. El E5 tenía el mismo convenio (σ = 41.2 km): ahora lo dice y da los
  p con la intensidad del modelo, que no cambian el veredicto (0.08 y 0.02).
- **Forma: 19 de 28 se acertaban sin saber** (al azar, 4.5). Patrones de fondo: la clave estaba en
  el par de opciones gemelas (6 de 6), dentro del par ganaba la que se abstiene o no culpa al
  procedimiento (4 de 4), cada par contradictorio de una múltiple tenía una clave (3 de 3) y en las
  múltiples la más corta era la clave (5 de 7). Fugas cruzadas: C06 se resolvía con A02, A06, A08 y
  A10; la pista de B07 era su clave. Reescritos los distractores y las pistas afectadas; las siete
  pistas «Son N» pasan a ser de contenido (el motor ya da el recuento al primer fallo).
- **Pertinencia: B03 no evaluaba su módulo** (enunciado y pista daban la regla y la definición:
  quedaba un Pitágoras) y cinco preguntas se acertaban con la propia hoja (A02, A07, A10, B03, B08).
  Cambian de ángulo: A07 pasa a leer G frente a F en los pinos suecos con las tres medianas del
  módulo 7 (el núcleo del 4.7 no lo comprobaba nadie); B01, a qué tiende la KDE con σ enorme
  (n/|W|); B02, una transferencia (un informe con escala por mapa); B08, la identidad del intercepto
  con la cuadratura dentro (`forcefit` sobre Kennedy: λ̂ = n/Σw = 6.813 frente a 6.803); B09 añade la
  lectura multiplicativa (−2.40 % por km). El módulo 1 ya no invita a leer primero el catálogo, que
  publica claves.
- **Verdad.** B09-b y A05-a eran verdaderas o defendibles (z de la diferencia −2.76); «ninguna pareja
  pesa 1» fallaba con las 40 sedes repetidas; el 15.22998 es un cociente de esperanzas y la media
  simulada es 15.219 (se publica «unos 15.2»); «60 o más» era «más de 60»; la retro de B11 daba un
  mecanismo falso (`kppm` pide `correction = "best"`, no la de por defecto) y la rutina 6 decía que
  el objeto no guarda la corrección (la guarda en el nombre de la columna, `iso`).
- **Ejercicios: 81 de 81 cifras reproducidas a ciegas, y un BLOQUEA.** El E2 explicaba el vuelco con
  «el vecino de verdad puede estar al otro lado del borde, donde nadie miró», y fuera del greenstone
  sí se miró: solo 11 de 219 tienen su vecino fuera. La cifra sin corregir está bien medida y mal
  comparada; contra 199 repartos al azar dentro del greenstone (K̂ ≈ 167, R ≈ 1.44) el oro sin
  corregir también se agrupa. El E1 ahora simula 99 Poisson que solo saben del greenstone (rechazan
  todos, y el χ² del oro supera a los 99), el E3 pide lo que su solución usa y el E1 crea `oro`,
  `fallas` y `greenstone`.
- **Gráficos.** Ejes de r en kilómetros con una línea por kilómetro (A09, B10, C01), las diez
  rejillas rotuladas (A06), la línea del 1 despegada del marco (A09), una marca en el radio donde la
  curva vuelve a la banda (B10), la «verde» de C01 que se veía negra, una leyenda que se medía antes
  de que el lienzo existiera (siempre a 10 px), referencias con contraste 4.8:1 y etiquetas
  flotantes con la unidad del radio.
- **Redacción.** El módulo 1 cuenta el recorrido de los siete módulos y liga las cuatro cosas que
  evalúa el parcial a las partes que las entrenan; cuatro contradicciones entre superficies (A02 con
  el capítulo, A03 b con c, A07 con el E2, C06 con B08); porcentajes con uno o dos decimales, signo
  menos tipográfico y la respuesta revelada con los decimales que pide el enunciado.

**2026-10-05 · P3.0, quinta ronda: la comprobación de la cuarta.** Tres vías sobre la página ya
corregida (`p41/`): gráficos otra vez en Chrome sin ventana, forma a ciegas, y verdad con
redacción (esta última se cayó por el límite de uso y se relanzó en `p42/`). Lo que cambió:

- **Gráficos: lo pedido estaba, y quedaban las etiquetas emergentes.** En el teléfono se cortaban
  en cuatro de los seis gráficos (hasta 307 px en un lienzo de 206): ahora la letra, el relleno y la
  caja se encogen con el ancho real, y cada conjunto trae un rótulo corto; la más ancha mide 132 px.
  La marca vertical de B10, que era un conjunto de datos, se colaba en la etiqueta del modo `index`
  («r = 3 638 m: 0.600» con el ratón a 59 m) y dejaba un círculo suelto: ahora la dibuja un
  complemento (`marcaVertical`) y la leyenda la nombra con un conjunto vacío. El borde alto de cada
  banda sale con su nombre («Borde alto», no «Banda del modelo»); valores con las cifras que hacen
  falta («5» y no «5.000», «0.0017» y no «0.002»); leyenda y etiqueta en el orden del enunciado; un
  título con contexto en cada etiqueta («De 31 a 35 sedes», «Rejilla 20 × 20», «σ = 1 320 m»); en
  C01 la banda de CSR va sin relleno y con bordes que pasan el 3:1, y la verde se ve verde; en A06
  se leen «12 15 20» en el teléfono; el título de B02 ya no se aplasta; los miles del lienzo con
  espacio duro, que se ve (el fino medía 1.5 px).
- **Forma: la reescritura de la cuarta ronda no había bajado el acierto sin saber** (19 en el
  recuento estricto, igual que antes): aparecieron pistas que nombraban la clave (B01, B05, B07,
  B11, C02, C06), siete de las ocho múltiples tenían exactamente dos claves, la clave seguía siendo
  la única que se abstenía en A07 y B09, y A03 regalaba las cifras del A01. Pistas de contenido en
  esas seis y en A10 y B08; abstenciones falsas junto a las buenas (A07, B09); un origen falso para
  el 15.2 de la gemela de A02; C03 con un distractor de hechos y mecanismo ciertos y dirección
  equivocada (el 7.7 % frente al 52.25 %); A08 gana una tercera clave (el alcance de K, que antes
  era el distractor «absoluto»), y la más corta de una múltiple ya es clave en 3 de 8 y no en 5.
  B11 conserva sus dos claves: la página la anuncia como «Varias respuestas».
- **Verdad (`p42/verdad/`): un BLOQUEA en la clave que la forma acababa de crear.** A08 b decía
  que más allá de 5 868 m «ninguna corrección deja a K fiable: los pesos se disparan». En las sedes
  no es así: el peso medio de traslación pasa de 1.68 justo antes del alcance a 1.79 justo después,
  ninguna pareja supera 3, y bajo CSR la desviación típica de K/πr² no salta en 5 868 m. La regla de
  Ripley es práctica, no un umbral, y por eso no sirve ni de clave ni de distractor. La clave nueva
  dice por qué `Kest` se detiene ahí, y la retro da los pesos del capítulo (1.08, 1.68, 3.31 y 9.7).
  La retro de B01 a describía la superficie sin corregir: con la corrección por defecto el máximo
  se va al borde. La retro de C02 a refutaba «todas dan la misma curva» con la K sin corregir, que
  no es una corrección: ahora da la diferencia entre la isotrópica y la de traslación (5.2 %, cifra
  nueva que el auditor rehace) y la cruza con el 93.2 % de B11. Además: la F de A07 es la corregida
  por muestra reducida, la escala de Thomas es por eje, A06 baja de 5 ya con la 3 × 3, `covered_by`
  en la rutina 2, y B03 con la regla y sus excepciones.
- **Redacción (`p42/redaccion/`): ningún BLOQUEA, y la forma pasa de 19 a 13 de 28 en el
  recuento estricto** (azar, 4). La entrada del bloque C decía «cinco» y enumeraba cuatro; C04
  copiaba una retro de B01; C06 seguía saliendo por los absolutos (ahora una verdadera lleva «solo»
  y una falsa no lleva ninguno); A07 d tenía 220 caracteres; la rutina 1 daba 102 sedes fuera y A01,
  101 rurales, sin explicar la que cae fuera del Distrito (tres cifras más del capítulo 4). Las
  numéricas con unidad la muestran junto a la casilla; los ejercicios llevan signo menos y miles
  con espacio fino; «nodo» pasa a «radio del barrido»; el catálogo ya no cita una «B3» que la
  página no muestra.
- **Quedan para Javier, en los capítulos:** el «contaría cada pareja por varias» del 4.8 exagera
  cerca del alcance (el mismo error de A08 b); y en el primer radio la curva naranja de C01 y del
  4.11 divide por un πr² interpolado que se pasa un 0.4 % (2.501 frente a 2.5115; la verde lleva el
  mismo sesgo, y ninguna conclusión cambia).
- **La pista de los pares, rota a petición de Javier (2026-10-06).** En las múltiples, de cada par
  de opciones que se contradicen una era clave (7 de 8 pares). Ahora A04, A10 y C06 llevan además un
  par que se contradice con las dos falsas («la varianza se reduce» y «se queda igual»; «pesan
  igual» y «pesan más las norte-sur»; «la ventana entra igual en todas» y «en K no hace falta»), y la
  J de A07 deja de negar la clave de la envolvente: falla por su sentido (J < 1 «como en un patrón
  regular»). Solo A07 conserva pares con clave. Las lecciones que salieron con las opciones viejas
  (la franja del borde, en número más y en fracción menos; el peso que crece con la distancia)
  pasan a las retros. De paso se equilibró la longitud: la más larga de una múltiple es clave en 2
  de 8 y la más corta en 3 de 8.
  Una revisión a ciegas (`p45/revision/`) acertó por la forma 3 de los 8 conjuntos exactos, y la
  regla del par falló justo en los tres pares nuevos; las cinco opciones nuevas, falsas sin
  ambigüedad. Encontró dos cosas más: B05 d era defendible («pintan casi lo mismo» es cierto; la
  falsedad va ahora en la escala de color) y la retro de A10 c decía que el largo de la ciudad «no
  basta», cuando bien razonado da la dirección (lo que no da es el tamaño). La opción c de A10 tiene
  ahora su guarda en el generador y en el auditor, con su inyección en el arnés.

### Sexta ronda (2026-10-06/07, `p46/`) · nueve revisores sobre lo publicado

Tras publicarse (PR #16) se volvió a revisar entero, con un brief común y nueve informes: verdad de
cada bloque (A, B, C con las rutinas, ejercicios con el catálogo), redacción, gráficos en Chrome sin
ventana, forma a ciegas, resolución experta a ciegas y pertinencia. El experto a ciegas, con los
capítulos y R pero sin las claves, acertó las 28, conjuntos de las múltiples incluidos: ninguna
pregunta tenía dos respuestas defendibles. Lo que sí apareció:

- **B10 enseñaba la lectura que el capítulo 4 prohíbe (BLOQUEA).** Preguntaba «¿en qué distancias
  está lo que el modelo no explica?» y la clave contestaba con el tramo en que la K se sale de la
  banda, 59 a 3 638 m. K acumula: su mayor separación de la media del modelo está a 1 960 m
  (`m10.test_global.r_mad_observada_m`), y de ahí en adelante la observada suma menos parejas que el
  modelo; anillo a anillo, el exceso acaba hacia 1.6 km. La clave nueva dice que la curva enseña
  dónde empieza y no hasta dónde llega; la vieja queda como distractor, con la memoria de K en la
  retro. La retro de C01 b decía lo mismo y se corrigió. B10 d contaba «77 de las 999 la cruzan»
  contra una banda hecha con ellas mismas (imposible) y sobre los 512 radios de spatstat: ahora son
  43, contra la banda de las otras 998, en los radios del gráfico. **El capítulo 5, m10, conserva
  la lectura vieja: queda para Javier.**
- **Verdad, en las rutinas.** La 1 fallaba justo cuando todo va bien (`attr(p, "rejects")` es
  `NULL` sin descartes); la 3 leía el tramo de la envolvente y no el del test, y comparaba el p en
  coma flotante contra la ayuda de `dclf.test`, y su prosa llamaba «cota superior» al suelo de
  1/(nsim + 1); la 6 comprobaba el argumento que se le pasó, no la K con que se ajustó, y además
  `kppm(..., correction = "translate")` sin `statargs` se ignora sin avisar (comprobado: κ 23.55 en
  vez de 18.99), que ahora la rutina enseña. Y `verifica_bloques.py` solo cotejaba números:
  `#> [1] TRUE` y `#> [1] FALSE` daban la misma lista. Ahora coteja también los lógicos y las cadenas.
- **Verdad, en los ejercicios y el catálogo.** E3 no fijaba la rejilla en su último paso; E4 decía
  que el coeficiente «se mueve más» que en Bogotá, cierto solo en errores estándar (0.59 frente a
  0.13, cifras nuevas); E5 atribuía el «no rechaza» solo al tramo de r, y con `Linhom` el tramo por
  defecto rechaza (0.03; 7 de 10 semillas): la solución lo dice, como el ejercicio del 4.12; el p de
  ~ D es el mínimo de 99 simulaciones y ya se dice; y la causa «la ventana es irregular» no estaba
  medida. El error 7 se medía con el 62 % de radios fuera de banda, la lectura que el error 6
  desautoriza: pasa al DCLF. El error 3 no traía ningún «no rechaza»: trae el 2 × 2 de las
  secuoyas (p = 0.178). E1 y E5 piden ahora decidir la ventana y el modelo, que el módulo 6
  prometía. E2 se titula «El borde que da la vuelta al régimen».
- **Forma.** C06 salía sin saber nada (las dos falsas eran las dos generales): la b pasa a ser
  concreta y con cifra. «porque» delataba la falsa (14 de 64 frente a 1 de 32): ahora 9 de 64 y
  5 de 32, con guarda. La cifra calculada delataba la clave en B02, C03, A10 y A04. La clave A08 b
  le sacaba 56 caracteres a su falsa y la guarda de longitud no miraba las múltiples, ni contaba
  `&nbsp;` como un carácter: las dos cosas, arregladas. `giro` en A05 y C01: la «b» era clave en 4
  de 6 gráficos y en 0 de 8 opciones únicas. B08 dejó de copiar en su retro la clave de C06 d.
- **Gráficos.** La leyenda escondía un solo borde de cada banda y la marca de B10 no obedecía a su
  entrada (`grupo` y `conjunto`); las descripciones dan el borde bajo del último radio, donde la
  clave dice «dentro»; en el teléfono C01 dice «Contra modelo» y no «Modelo», que en B10 es la
  línea del 1.
- **Redacción y pertinencia.** A03 b era cierta en su primera mitad (las rurales, contra su
  propia λ, sí están más agrupadas: R = 0.749); A02 b salvaba con «el margen» un p que el módulo 6
  no deja defender; B03 pegaba 2 500 m a la diagonal; B05 a contradecía la frase del capítulo; B06
  no usaba su distractor 0.34 ni decía la referencia del cociente (58/978; el máximo es 8.64 veces
  eso); A01 no explicaba el 70.5 de quien toma las 102; C04 apuntaba al m2 del capítulo 5 y su clave
  está en el m1; el módulo 1 prometía retros que el motor no enseña, y no decía que Hawkes no tiene
  pregunta.
- **Para Javier, en los capítulos:** el cap. 4 m7 y el cap. 5 m11 dicen «40 sitios» de sedes
  repetidas, y son 39 (40 sedes sobran); el cap. 5 m10 lee el tramo de K fuera de banda como el
  alcance del exceso; el cap. 5 m5 dice que con correlación 1 «daría igual cuál se publica».
  **Y de diseño:** si el parcial tendrá mapas, coincidencias o un ítem abierto (el preparcial no los
  ensaya), y si el módulo 4 debería llevar dos o tres preguntas de «qué línea lo comprueba».
- **Tras la forma, verdad (`p46/verdad-cambios/`).** Un revisor solo de lo cambiado no encontró
  ninguna etiqueta falsa, y sí que B10 c, la falsa, es la frase del cap. 5 m10 al que manda el
  repaso: su retro dice ahora que el capítulo lo resume así y se queda corto. La clave de B10 ya no
  niega lo que su retro saca de K, y la «mayor separación» de 1 960 m se dice en m² (en el cociente
  que dibuja el gráfico, la mayor está a 59 m). C04 a deja de contradecir el «aquí ha elegido
  selector» del cap. 5 m5; la rutina 1 en Python cuenta las geometrías nulas además de las vacías;
  en E2 la K sin corregir supera πr² desde 1.55 km, no desde 2; en E5 «explican la geografía» se
  apoyaba en un test que no rechaza.
