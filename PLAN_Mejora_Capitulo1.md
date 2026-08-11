# Plan de mejora — Capítulo 1 · Datos espaciales y la primera ley

**Fecha:** 2026-08-05 · **Estado:** propuesto, pendiente de tu aprobación
**Objetivo:** cerrar dos deudas del capítulo 1 — cifras y conclusiones sin procedencia
visible, y gráficos que el texto anuncia como manipulables pero son estáticos — sin
romper la cadena de reproducibilidad ni reabrir lo que el Checkpoint 2 dio por cerrado.

---

## 0. La restricción que ordena todo el plan

**El HTML es un artefacto de compilación, no una fuente.** Ninguna tarea de este plan
edita `Htmls_Espacial/capitulo-1-datos-espaciales.html` directamente: se perdería en la
siguiente pasada del ensamblador.

```
datos primarios ──► precalculo/genera_cap1.R ──► salidas/cap1_datos.json
                    precalculo/genera_soluciones.R  salidas/cap1_soluciones.json
                                                    salidas/cap1_mapas.json
                                                          │
                    plantilla/plantilla-capitulo.html ────┤
                                                          ▼
                                       precalculo/ensambla_cap1.py
                                                          │
                                                          ▼
                              Htmls_Espacial/capitulo-1-datos-espaciales.html
                                                          │
                          ┌───────────────────────────────┤
                          ▼                               ▼
              precalculo/audita_cap1.py      precalculo/audita_texto_cap1.py
              (recalcula desde las fuentes)  (toda cifra de la prosa está en el JSON)
```

De ahí salen tres reglas que ninguna tarea puede saltarse:

| Regla | Consecuencia práctica |
|---|---|
| **D10** — ninguna cifra a mano | Toda explicación nueva que estrene un número exige tocar `genera_cap1.R` primero |
| **D9** — cómputo pesado en R | Un deslizador puede evaluar `n/(1+(n−1)ρ)` en el navegador; no puede ajustar un variograma |
| **Auditor de prosa** | Una cifra redondeada en el texto que no case con el JSON hace **fallar** la auditoría |

Un componente nuevo (deslizador, control de mapa, panel de derivación) se **retropropaga
a `plantilla/plantilla-capitulo.html`** y a `prueba-geomapa.html`, que es la regla ya
establecida en el Checkpoint 2.

---

## 1. Decisiones de esta ronda

| # | Decisión | Elección |
|---|---|---|
| M1 | Precálculo | **Cadena completa**: se puede tocar `genera_cap1.R` y re-ejecutar R → JSON → ensamblador → auditores |
| M2 | Interactividad | **Promesas rotas + los seis mapas del módulo 2**, al nivel que ya tienen los capítulos 2 y 3 |
| M3 | Derivaciones | **Paneles plegables «De dónde sale»**, reutilizando el patrón `.ejercicio-panel` |
| M4 | Decimales | **Revisada** (ver abajo): arreglar el error de tipo, conservar los cinco decimales medidos, publicar incertidumbre |

### M4, revisada — y por qué

La pregunta original ofrecía «redondear a cifras significativas, global». Al leer
`precalculo/mide_punto_ciego.py` aparece que **los cinco decimales están medidos, no
elegidos**: por debajo de cinco, el índice de comparaciones del auditor absorbe las
perturbaciones de un dígito (8,65 % con cuatro decimales, 63 % con uno, 4,63 % con
cinco). Y `audita_texto_cap1.py` exige que toda cifra de la prosa exista en el JSON.
Redondear globalmente rompería el auditor y degradaría una capacidad medida.

El defecto real es más estrecho y más fácil:

- **Error de tipo.** `359.00000` muertes, `1121.00000` municipios, `33.00000`
  departamentos, `361.00000` estaciones, `1113.00000` municipios. El JSON ya distingue
  `int` de `float`; el ensamblador aplica `n()` a los dos. Corrección en una línea.
- **Los cinco decimales sobre medidas se quedan**, y se explican en el capítulo.
- **Falta incertidumbre, no redondeo**, en los cocientes derivados (`182.12490 %`,
  `29.77633 %`, `8.07439 veces`). El capítulo ya publica `± 0.00726` en dos sitios.

---

## 2. Inventario de defectos (verificado, no supuesto)

### 2.1 · Gráficos que el texto promete manipulables y no lo son

| Simulador | Módulo | El texto dice | El JS hace | Ref. |
|---|---|---|---|---|
| ~~`n-efectivo`~~ | 5 | ~~«**Mueve ρ** y mira cuánto aporta pasar de 25 a 1 000»~~ | ~~**Ningún control**: `.simulador-controles` queda vacío~~ ✅ **cerrado en T1.1** (y la serie de 25 tampoco existía: el gráfico empezaba en 50) | `:4168` vs `:7957` |
| ~~`ee-ingenuo`~~ | 4 | ~~«**Mueve** el alcance y mira **las dos curvas**»~~ | ~~Botones, no deslizador; las curvas **nunca cambian**~~ ✅ **cerrado en T1.2** | `:3999` vs `:7916` |
| ~~`una-realizacion`~~ | 6 | ~~«el variograma **de cada realización**»~~ | ~~El botón cambia el mapa; el variograma dibuja siempre `v.una`~~ ✅ **cerrado en T1.3** — y el diagnóstico se quedaba corto: `v.una` **no era el variograma de ninguno de los tres mapas**. Eran dos simulaciones distintas (16×16 y 28×28, semillas distintas) emparejadas por el índice | `:4253` vs `:7982` |
| ~~`correlograma`~~ | 3 | — | ~~`.simulador-controles` vacío, gráfico fijo~~ ✅ **cerrado en T1.4** | `:7890` |
| ~~`snow-serie`~~ | 1 | ~~«con la retirada del mango **marcada**»~~ | ~~`.simulador-controles` vacío, gráfico fijo — **y la marca dibujaba 0 píxeles de 385 990**: un punto suelto con `pointRadius: 0`, vivo solo en la leyenda~~ ✅ **cerrado en T1.4** | `:7867` |
| 6 `.geomapa` | 2 | — | Lienzos estáticos, sin controles ni *hover* | `:3659–3679` |

**Contexto que agrava:** el motor `.geomapa` del capítulo 1 **no registra un solo
`addEventListener`**. La clase `.geomapa-controles` está definida en CSS y usada **0
veces** aquí, frente a **8 en el capítulo 2** y **5 en el 3**. El capítulo 1 va por
detrás de sus propios hermanos, y D2 del plan dice: *«el mapa es un simulador, no una
ilustración»*.

**A favor:** las fábricas `crearControles` (deslizadores), `crearSelector` y
`crearInterruptores` ya existen en el archivo (`:5451`, `:5578`, `:5609`) y **no se usan
en ningún capítulo**. La infraestructura está montada; falta cablearla.

### 2.2 · Cifras y conclusiones sin procedencia

| # | Módulo | Defecto |
|---|---|---|
| ~~P1~~ | 5 | ✅ **cerrado en T2.1**, publicando los dos ρ y su discrepancia. El titular del módulo («1 121 municipios informan como 64.52155, el 5.75571 %») **no decía con qué ρ**. ~~Ese ρ ≈ 0.03146 solo asoma en la solución del ejercicio 3~~ → **el diagnóstico era falso, corregido en T1.1.b:** no hay ningún ρ detrás de esa cifra. `genera_cap1.R:556` la calcula como `n_muni × (ee_iid/ee_blq)²`, un **cociente de varianzas bootstrap**, sin ρ por medio. Y el 0.03146 del ejercicio 3 es el de las **361 estaciones del IDEAM**: con n = 361 da 29.29, no 64.52. El defecto no es que el ρ esté escondido, es que **no existe**, y T2.1 tiene que decidir cuál publicar |
| ~~P2~~ | 4 | ~~No se muestra el puente de φ = 4 al factor 7.85798; ni que 0.77880 = e^(−1/4); ni que «unas 61.7» es 7.85798²~~ ✅ **cerrada en T2.2** — y el diagnóstico se quedaba corto por cuarta vez en este plan: el «61.7» **se calculaba en el ensamblador** y no existía en ningún JSON, y el módulo llamaba «la información» a un cociente (61.74778) que **no es** el que el módulo 5 divide (49.63003). El puente que faltaba tenía tres tramos, no uno |
| P3 | 5 | `n_eff = n/(1+(n−1)ρ)` se enuncia sin derivarla de la fórmula de varianza del módulo 4, que está dos módulos antes y la da servida |
| P4 | 1 | El «8.07439 veces» compara contra un reparto uniforme entre 13 bombas — línea base que ignora densidad de población y área de captación, y no se declara. No hay contraste de aleatorización, teniendo el capítulo esa maquinaria en el módulo 3 |
| P5 | 7 | «base teórica 0.36» aparece sin origen |
| P6 | 3 | El gradiente de −5.56388 °C/1 000 m se llama «exactamente el rango físico esperable» sin fuente |
| P7 | 3 | «la última banda ya no se distingue del valor esperado bajo independencia» se **afirma**; el control permutado está en el gráfico pero no como banda nula |
| P8 | 10 | El R² = −0.02735 depende de si se calcula con la media global o por pliegue, y no se dice. Los pliegues van «de 1 a 64 estaciones» y se promedia igual |
| P9 | 6 | «el análisis ingenuo declararía significativa la media en el 82 %» — ¿qué contraste, a qué α? No se dice. La anchura de banda se da «en el rezago 4» sin decir por qué ese rezago |
| P10 | 4 | El remuestreo por departamentos se presenta como «el honesto» sin señalar que 33 bloques son pocos y que la partición departamental es justo el MAUP que denuncia el módulo 7 |
| P11 | — | ~~`359.00000` muertes, `1121.00000` municipios, `33.00000` departamentos (error de tipo)~~ ✅ **cerrado en T0.2** |
| P12 | 4 | El texto describe la simulación como **16×16 = 256 celdas** —de donde salen todas las cifras— y enseña debajo un mapa que es de **28×28**. La elección está razonada en R (`genera_cap1.R:1292`: legibilidad y presupuesto), pero **el capítulo no la declara**, así que el lector toma el mapa por el campo simulado. Encontrado el 2026-08-05 al estrenar la verificación visual |
| P12b | 6 | **Segunda instancia, encontrada en T1.3 y cerrada allí.** El módulo 6 tenía el mismo desajuste y era peor: no callaba la rejilla, la **decía mal** —tomaba prestado el `k` del módulo 4 para describir su propia figura, «sobre 16×16 celdas», sobre un mapa de 28×28—. Cerrada por construcción: los mapas son ahora de 16×16 y una guarda de compilación ata `nx`/`ny` a `una_realizacion.k`. **Esa guarda es el molde para P12**, que sigue abierta y es de T2.4 |

---

## 3. Lista de tareas

### Fase 0 — Línea base y rebanada vertical de prueba

---

#### T0.1 · Reproducir la cadena sin tocar nada

**Descripción:** ejecutar el precálculo, el ensamblador y los dos auditores tal como
están hoy, y confirmar que el capítulo se regenera idéntico. Es lo primero porque si la
cadena no reproduce hoy, **todo lo demás está bloqueado** y conviene saberlo en la
primera hora, no en la quinta.

**Criterios de aceptación:**
- [x] `genera_cap1.R` y `genera_soluciones.R` corren sin error con el R 4.4-arm64 de ruta absoluta
- [x] El HTML regenerado es idéntico al actual, o toda diferencia queda explicada por escrito
- [x] `audita_cap1.py` y `audita_texto_cap1.py` devuelven 0

**Verificación:** `bash precalculo/audita_todo.sh` · `diff` contra una copia previa del HTML

**Dependencias:** ninguna · **Archivos:** ninguno (solo lectura) · **Alcance:** S

> ✅ **CERRADA el 2026-08-05.** La cadena reproduce. El diff son 3 bloques, todos
> explicados, y ningún control se perdió: 836 = 836 y 140 = 140 comprobaciones. Encontró
> además que el capítulo publicado **no salía del árbol de fuentes actual**. Informe
> completo en el Anexo T0.1.

---

#### T0.2 · El error de tipo en los enteros

**Descripción:** `ejercicio()` aplica `n()` (cinco decimales) a todos los valores no
textuales, incluidos los enteros. El JSON ya los tipa correctamente. Es la rebanada
vertical más barata que recorre la cadena entera, y por eso va aquí: valida el bucle de
trabajo con un cambio de una línea antes de arriesgar uno grande.

**Criterios de aceptación:**
- [x] Las tablas de solución muestran `359`, `1 121`, `33`, `361`, `1 113` como enteros
- [x] Ninguna cifra real pierde sus cinco decimales
- [x] Decidido y documentado el caso borde del factor entero `1` del ejercicio 1 (¿`1` o `1.00000`?)
- [x] **Añadido:** el arreglo no deja ninguna cifra peor auditada que antes

**Verificación:** los dos auditores en verde · inspección de las cuatro tablas de solución

**Dependencias:** T0.1 · **Archivos:** `precalculo/ensambla_cap1.py` (~`:1353`) · **Alcance:** XS

> ✅ **CERRADA el 2026-08-05, y creció.** Resultó ser XS en el arreglo y S en las
> consecuencias. El defecto también estaba en el capítulo 2 (15 celdas). Y la prueba de
> inyección destapó que escribir `1 121` en vez de `1121.00000` movía seis cifras del
> régimen protegido al mal protegido: hubo que **cerrar ese hueco con una comprobación
> nueva** antes de poder dar la tarea por buena. Informe en el Anexo T0.2.

---

---

#### T0.3 · La misma deriva en el capítulo 2 *(nueva, salida de T0.1)*

**Descripción:** los 3 mapas publicados del capítulo 2 tampoco llevan el campo
`codificacion` que `geo.R` escribe hoy (los 7 del capítulo 3 sí). Mismo caso que el
capítulo 1, mismo impacto —ninguno—, misma solución: regenerar y volver a auditar.
Conviene cerrarlo antes de que el capítulo 4 estrene una tercera variante del formato.

**Criterios de aceptación:**
- [x] `cap2_mapas.json` y el HTML del capítulo 2 salen del árbol de fuentes actual
- [x] `audita_cap2.py` y `audita_texto_cap2.py` siguen en verde con las mismas cuentas
- [x] El diff queda explicado por escrito, como el de T0.1

**Verificación:** `audita_todo.sh --rapido` · `diff` contra el respaldo

**Dependencias:** ninguna · **Archivos:** ninguno (solo regenerar) · **Alcance:** XS

> ✅ **CERRADA el 2026-08-05.** Predicción escrita antes de ejecutar —3 mapas de polígonos,
> +84 bytes— y cumplida al byte. 445 = 445 y 128 = 128 comprobaciones, 7/7 mapas con tinta.
> Informe en el Anexo T0.3.

---

### ✅ Checkpoint 0 — CERRADO (2026-08-05)

> **Cierre con el arnés COMPLETO, no con el rápido.** `audita_todo.sh` sin `--rapido`,
> **33 min 45 s**, salida 0, **ARNÉS COMPLETO EN VERDE**: los 13 pasos en OK, incluidos los
> cuatro arneses de inyección que el `--rapido` se salta.
>
> | Auditor | Comprobaciones | Fallos |
> |---|---:|---:|
> | `audita_cap1.py` | 836 | 0 (3 saltadas declaradas) |
> | `audita_cap2.py` | 445 | 0 (2 saltadas) |
> | `audita_cap3.py` | 356 | 0 (2 saltadas) |
> | `audita_texto_demo.py` | 77 | 0 |
> | `audita_texto_cap1.py` | **141** *(140 + la familia nueva)* | 0 |
> | `audita_texto_cap2.py` | **129** *(128 + la familia nueva)* | 0 |
> | `audita_texto_cap3.py` | 130 | 0 |
> | **Total** | **2 114** | **0** |
>
> Y los arneses de inyección, que son los que dan sentido al verde:
> `prueba_auditor_cap1/2/3.py` en OK y `prueba_texto.py` con **110 defectos inyectados,
> 110 detectados** (cap1 30/30, cap2 24/24, cap3 20/20, fixture 36/36). Ninguna
> comprobación preexistente se perdió al tocar `audita_texto_base.py`.
>
> Lienzos con `aria-label`: 7/7, 17/17, 19/19 y 3/3.
- [x] La cadena reproduce y los auditores dan verde con un cambio real dentro — T0.2 metió
      un cambio de contenido en 21 celdas de dos capítulos y el arnés lo acompañó
- [x] **El arnés no solo da verde: demuestra que puede ponerse rojo.** T0.2 le inyectó
      cuatro defectos y los cazó los cuatro, tres de ellos ciegos antes
- [x] Los tres capítulos escritos salen del mismo árbol de fuentes (T0.1 y T0.3)
- [x] Sé cuánto tarda una pasada completa — **1 min 25 s** el bucle del capítulo 1
      (R 1:12 + ensamblador 0,05 s + los dos auditores 11 s); **4 min 14 s** el arnés de los
      tres capítulos; más de 10 min con los arneses de inyección. Detalle en el Anexo T0.1

---

### Fase 1 — Ninguna promesa sin su control

> Esta fase va antes que la de contenido a propósito: es la deuda que un estudiante
> detecta en el primer minuto, y la que hace desconfiar de todo lo demás.

---

#### T1.1 · `n-efectivo`: el deslizador de ρ que el texto promete ✅ **CERRADA**

**Descripción:** el módulo 5 dice «Mueve ρ» y no hay nada que mover. `n_eff = n/(1+(n−1)ρ)`
es aritmética cerrada: se evalúa en el navegador sin violar D9. Cablear `crearControles`
—que ya existe y nadie usa— con un deslizador de ρ que redibuja las curvas y la lectura,
y el techo 1/ρ como línea de referencia móvil.

**Criterios de aceptación:**
- [x] Un deslizador de ρ (0 a 0.3) redibuja curvas, techo y lectura numérica en vivo
- [x] En ρ = 0.01 y ρ = 0.10 los valores coinciden **exactamente** con los del JSON (`90.99181`, `9.91080`)
- [x] El punto de Colombia (~~ρ estimado~~ → 64.52155) queda marcado sobre la curva —
      **reinterpretado, porque ese ρ no existe**: el criterio pedía un puente que no está en
      las fuentes. Se marca el punto con las dos cifras del JSON y el capítulo declara de
      dónde sale de verdad. Ver T1.1.b
- [x] **Añadido:** el eje x pasa a ser n y se transpone el gráfico — con ρ en el eje no hay
      curva que redibujar ni techo que mover
- [x] **Añadido:** las dos guardas —compilación y ejecución— probadas por inyección, 14 de 14

**Verificación:** abrir el capítulo, mover el deslizador, comprobar los dos anclajes ·
consola limpia · auditores en verde

**Dependencias:** T0.1 · **Archivos:** `ensambla_cap1.py` (bloque JS + prosa de intro),
`plantilla/plantilla-capitulo.html` (si el deslizador necesita CSS) · **Alcance:** M

> ✅ **CERRADA el 2026-08-06.** El deslizador recorre **301 posiciones** y las 301 cuadran; en
> los 7 ρ de la rejilla la lectura es **idéntica al JSON**, con 7 huellas de píxeles distintas.
> El gráfico se transpuso: ahora el eje x es n y el techo 1/ρ es una recta que se mueve.
> **La plantilla no se tocó** —sí se usó `crearControles`, la fábrica que T1.2 había
> descartado— así que los capítulos 2 y 3 no se re-ensamblaron. Dos hallazgos que cambian el
> plan: **el ρ del titular del módulo 5 no existe** (afecta a P1 y a T2.1) y **el tope de peso
> era el riesgo equivocado** — retirado como criterio de aceptación. Informe en el Anexo T1.1.

---

#### T1.2 · `ee-ingenuo`: el mapa contradice a la lectura ✅ **CERRADA**

> ### ⚠️ Esta tarea dejó de ser cosmética
>
> La verificación visual del 2026-08-05 —posible solo desde que hay servidor HTTP—
> encontró que **el mapa del campo gaussiano está desplazado en uno para los cinco
> botones**. `capitulo-1:7616` hace `fuente: () => MAPAS_SIM.campos[campoIdx]`, pero
> `campoIdx` es el índice en `inferencia.rejilla` (**7** entradas: φ = 0, 0.5, 1, 2, 4, 8,
> 16) y `campos` tiene **5** (φ = 0.5, 1, 2, 4, 8):
>
> | Botón | Mapa que dibuja | Lectura que muestra |
> |---|---|---|
> | φ = 0.5 | φ = **1** | φ = 0.5 |
> | φ = 1 | φ = **2** | φ = 1 |
> | φ = 2 | φ = **4** | φ = 2 |
> | φ = 4 | φ = **8** | φ = 4 |
> | φ = 8 | `undefined`, se sale del array | φ = 8 |
>
> **El campo que el estudiante ve nunca es el que dicen los números de al lado**, y siempre
> está más correlacionado de lo que la etiqueta promete. El módulo entero trata de
> «cuánto miente el error estándar según la correlación», así que el mapa desmiente
> visualmente la lección que ilustra.
>
> Ningún auditor podía verlo: las cifras del JSON son correctas, la prosa es correcta, y
> el desajuste solo existe **en tiempo de ejecución**, entre dos índices paralelos.
>
> **La ironía útil:** el comentario del propio simulador dice *«Se mapea el índice para que
> el mapa y la lectura no se descuadren»*. La intención estaba escrita; el mapeo se hizo en
> la dirección contraria.
>
> **Arreglo propuesto** — quitar el acoplamiento entre índices paralelos, que es la clase de
> defecto, no solo esta instancia:
> ```js
> fuente: () => MAPAS_SIM.campos.find(
>     c => c.phi === DATOS_CAP1.inferencia.rejilla[campoIdx].phi)
> ```
> Busca por φ en vez de por posición: si mañana cambia cualquiera de las dos rejillas, no
> se descuadra en silencio.

**Descripción:** además del defecto anterior, el texto promete curvas que se mueven; el
gráfico ya tiene φ en el eje x, así que **las curvas son la respuesta completa** y no
tienen por qué moverse. Hay dos salidas honestas y hay que elegir una:

- **(a) Barata y correcta:** reescribir la prosa —«recorre el alcance y mira dónde se
  cruza la cobertura con el 0,95 prometido»— y convertir la botonera en un deslizador
  que mueve un **marcador vertical** sobre las curvas, además del mapa del campo y la
  lectura. Sin tocar R.
- **(b) Cara:** rejilla de φ más densa en `genera_cap1.R` y un segundo panel que dibuje
  la distribución muestral de la media en el φ elegido.

**Recomendación: (a).** La (b) añade superficie de auditoría para enseñar lo mismo.

**Criterios de aceptación:**
- [x] **El mapa dibuja el φ que dice su botón**, comprobado en el navegador botón a botón
- [x] El quinto botón no se sale del array
- [x] Ninguna frase promete un movimiento que el gráfico no hace
- [x] El marcador vertical, el mapa del campo y la lectura se mueven con el control
- [x] La búsqueda es por φ y no por posición, para que ninguna de las dos rejillas pueda
      descuadrarse en silencio si mañana cambia
- [x] **Añadido:** el defecto tiene ahora dos guardas que se ponen rojas — una en tiempo de
      compilación y otra en tiempo de ejecución— y las dos se probaron por inyección

**Verificación:** recorrer el control de extremo a extremo · auditores en verde

**Dependencias:** T0.1 · **Archivos:** `ensambla_cap1.py` · **Alcance:** M

> ✅ **CERRADA el 2026-08-05, opción (a) y luego un trozo de la (b).** El defecto era **peor**
> de lo descrito: el estado inicial enseñaba **tres φ distintos a la vez** (botón 0.5, mapa 4,
> lectura 2) y el quinto botón no «se salía del array» de forma visible, sino que **se
> congelaba en silencio** — excepción tragada por el manejador, mapa y lectura quietos en
> φ = 4 con el botón diciendo φ = 8. La botonera es ahora un deslizador de **siete
> posiciones** con marcador sobre las curvas: `genera_cap1.R` estrena los campos de **φ = 0
> —el ruido puro, la imagen de la independencia— y φ = 16**, que faltaban. Y la primera
> guarda que escribí **dio verde con el defecto reinyectado**: era tautológica. Informe
> completo en el Anexo T1.2.

---

#### T1.3 · `una-realizacion`: un variograma por realización ✅ **CERRADA**

> ### ⚠️ No era una curva quieta: era la curva de otro campo
>
> Los tres mapas salían de una simulación **aparte** —28×28, semilla `SEMILLA+700`,
> `genera_cap1.R:1336`— y la curva, la banda y **todas** las cifras del módulo, de otra
> —16×16, semilla `SEMILLA+300`, `genera_cap1.R:605`—. Rehecho el variograma desde el `zq`
> de cada mapa:
>
> ```
> mapa 1 (28×28)  : 0.2512  0.4334  0.5768  0.7228  …
> mapa 2 (28×28)  : 0.2509  0.4115  0.5485  0.6797  …
> mapa 3 (28×28)  : 0.2543  0.4199  0.5225  0.5769  …
> `v.una` dibujado: 0.2506  0.3746  0.4548  0.5540  …
> ```
>
> **La curva publicada no era la de ninguno de los tres**, y la intro anunciaba «sobre 16×16
> celdas» sobre un mapa de 28×28 (**P12b**). Ningún auditor podía verlo, por tercera vez en
> este plan: cada JSON era correcto por su cuenta y el defecto vivía en el hueco entre los dos.

**Descripción:** el botón cambia el mapa, pero el variograma dibuja siempre la misma
realización. Con eso, la tesis del módulo —«de una realización no se puede saber si lo
que ves es el proceso o el azar»— **no se demuestra: se afirma**. Es la única tarea de
esta fase que exige tocar R: hay que exportar el variograma de las tres realizaciones
mostradas, no solo de una.

**Criterios de aceptación:**
- [x] `cap1_datos.json` trae el variograma de las tres realizaciones visibles
- [x] Cambiar de realización cambia la curva «una realización» sobre la banda 5–95 %
- [x] La lectura numérica y el mapa siguen sincronizados con la curva
- [x] **Añadido:** mapa, lectura, curva y banda salen del **mismo lote de 1 000** — se borra la
      simulación aparte de 28×28, y con ella P12b
- [x] **Añadido:** las tres capas de guarda —compilación, ejecución y auditoría— probadas por
      inyección, **25 de 25**

**Verificación:** ~~las tres realizaciones dan tres curvas distintas y las tres caen dentro
de la banda~~ → **las tres curvas se separan 0.10286 y las tres caen dentro de la banda, `0 de
8` rezagos fuera cada una — pero eso se publica, no se promete.** El criterio pedía una
propiedad que el módulo no controla, y forzarla habría sido escoger las realizaciones. Lo que
se publica y se audita es **cuánto se aparta cada una del teórico**: 0.13802, 0.25488 y
0.32751 veces su valor · `audita_cap1.py` recalcula los tres variogramas **desde el `zq` del
mapa que se dibuja**, no desde el JSON de cifras

**Dependencias:** T0.1 · **Archivos:** `genera_cap1.R`, `ensambla_cap1.py`,
`audita_cap1.py`, `prueba_auditor_cap1.py` · **Alcance:** M

> ✅ **CERRADA el 2026-08-06, y cierra la Fase 1.** Las **3 posiciones** correctas, con 3 curvas,
> 3 huellas de gráfico y 3 huellas de mapa distintas, y consola limpia. Cuatro hallazgos: la curva
> no era de ninguno de los tres mapas; la intro mentía sobre la rejilla (**P12b**, cerrada aquí,
> y su guarda es el molde para P12); **el comentario de R que justificaba publicar `V[, 1]`
> era falso** —decía que se salía de la banda «en algún lag» y no se salía en ninguno—; y **el
> botón discrepaba del mapa al volver al módulo**, defecto anterior a la tarea que estaba
> también en `snow-mapa` y que deja un criterio transversal nuevo. Y dos
> errores míos, los dos cazados por la inyección y **ninguno por el repaso del código**: dos
> comprobaciones que se **estrellaban** en vez de informar, devolviendo código 1 sin una sola
> línea de diagnóstico. Informe completo en el Anexo T1.3.

---

#### T1.4 · `correlograma` y `snow-serie`: dos gráficos mudos ✅ **CERRADA**

**Descripción:** los dos tienen su `.simulador-controles` vacío. El correlograma gana con
conmutar series (real / sin altitud / permutado) para que la comparación sea del
estudiante y no del autor. La curva del brote gana con diario ↔ acumulado, que es
justamente donde se ve que el 90 % de los ataques ya había ocurrido antes del mango —el
argumento del módulo—; el acumulado se calcula en el navegador desde la serie diaria.

**Criterios de aceptación:**
- [x] Correlograma: interruptores que muestran y ocultan cada serie, con E[I] siempre visible
- [x] Snow: conmutador diario/acumulado, con la retirada del mango marcada en los dos —
      **y el hallazgo:** la marca del modo diario **no dibujaba un solo píxel**, 0 de 385 990.
      Era un punto suelto con `pointRadius: 0`, vivo solo en la leyenda. Ver T1.4.b
- [x] Ninguna cifra nueva en la prosa (el acumulado es derivado, no publicado)
- [x] **Añadido:** la lectura numérica también responde a los controles, y «cuánto de la I era
      altitud» solo aparece con las dos series que compara encendidas
- [x] **Añadido:** la leyenda de Chart.js se redirige al interruptor, para que no haya dos
      mandos sobre un mismo estado que puedan discrepar
- [x] **Añadido:** las dos guardas —compilación y ejecución— probadas por inyección, 26 de 26

**Verificación:** los dos controles responden · consola limpia · auditores en verde

**Dependencias:** T0.1 · **Archivos:** `ensambla_cap1.py` · **Alcance:** M

> ✅ **CERRADA el 2026-08-06.** Las **2 posiciones** de Snow y las **8 combinaciones** del
> correlograma, todas correctas, con 2 y 8 huellas de píxeles distintas. **Cierra el segundo
> criterio del Checkpoint 1: quedan 0 `.simulador-controles` vacíos.** Tres hallazgos: la marca
> del mango llevaba dibujando cero píxeles; el arnés destapó un hueco propio —recortar la serie
> por la cola no movía ningún total y pasaba entera, ahora atada a `n_dias_con_fecha`—; y la
> guarda de la leyenda **desmintió el comentario que la justificaba**, así que se retiró una
> línea de código que yo había explicado mal. **R no se tocó y los tres JSON son byte a byte los
> mismos.** Informe completo en el Anexo T1.4.

---

### ✅ Checkpoint 1 — CERRADO (2026-08-06) · el texto no promete lo que no da
- [x] Recorridos los 12 módulos con la consola abierta, sin errores — **repetido en T1.3.k con
      T1.3 dentro:** 0 errores, 0 excepciones, 0 `.simulador-controles` vacíos, 17/17 lienzos
      con tinta y los 17 con `aria-label`
- [x] Ningún `.simulador-controles` queda vacío — **0**, contados en el navegador módulo a
      módulo. Eran 2 y los cerró T1.4 *(T1.4.h, reconfirmado en T1.3.k)*
- [x] Ninguna frase de intro promete un control inexistente — **`una-realizacion` reescrita en
      T1.3** («Cambia de realización y mira moverse las tres cosas a la vez»), y ahora la
      promesa se cumple; las de los módulos 1, 3, 4 y 5 ya estaban
- [x] **T1.3 cerrada**, la única tarea de la fase que toca R
- [x] **Arnés de los tres capítulos en verde con T1.3 dentro:** `audita_todo.sh --rapido`,
      código 0, los seis auditores OK · `audita_cap1.py` **901** comprobaciones (eran 836) y
      `audita_texto_cap1.py` **141**, las dos sin fallos
- [x] **Tu revisión** — validada por Javier el 2026-08-06

---

### Fase 2 — De dónde sale cada número

---

#### T2.1 · El ρ invisible del módulo 5 (P1) ✅ **CERRADA** — *reencuadrada por T1.1*

> ⚠️ **La verificación de T1.1 ya contestó el segundo criterio, y la respuesta es «no».** No
> hay un ρ escondido: **no hay ρ**. El 64.52155 sale de `n_muni × (ee_iid/ee_blq)²`, el
> cociente de los dos remuestreos del módulo 4, y el 0.03146 del ejercicio 3 pertenece a las
> 361 estaciones del IDEAM. Así que esta tarea ya no es «publicar el ρ» sino **elegir cuál**,
> y son decisiones distintas:
>
> - **(a) El ρ retro-transformado**, `(n/n_eff − 1)/(n−1)` = **0.01462**: el ρ que la
>   equicorrelación necesitaría para explicar la inflación medida. Barato, honesto y encaja
>   con el rombo que T1.1 dejó en el gráfico. No es una estimación de la correlación espacial
>   de Colombia y hay que decirlo.
> - **(b) El ρ estimado por bandas**, con el método del ejercicio 3 sobre los 1 121
>   municipios. Es una estimación de verdad, y **casi seguro no reproducirá 64.52155** — con
>   lo que el módulo tendría dos cifras que hay que reconciliar. Más caro y más instructivo.
>
> El capítulo ya está preparado para las dos: la prosa que escribió T1.1 declara que el
> 64.52155 no viene de un ρ, y el deslizador deja **buscar** el ρ cuya curva pasa por el
> rombo. Con (a) se publicaría el número que el estudiante encuentra a mano.

**Descripción:** el titular del módulo se apoya en un ρ que no aparece. Publicarlo, decir
cómo se estimó y dejar que el lector rehaga la cuenta. Es el defecto de procedencia más grave
del capítulo: **su cifra estrella no tiene entrada visible.**

**Criterios de aceptación:**
- [x] Elegida y declarada la opción (a) o (b) de arriba → **las dos**, por decisión de Javier
      del 2026-08-06: publicar el implícito, el medido y su discrepancia
- [x] El módulo 5 publica el ρ y su método, diciendo si es una estimación o una
      retro-transformación
- [x] ~~Verificado que es **el mismo** ρ del titular y del ejercicio 3~~ → **no lo es, y queda
      declarado.** Hallazgo de T1.1.b, adelantado dos fases
- [x] Si se elige (a): `n/(1+(n−1)ρ)` con el ρ publicado reproduce 64.52155. Si se elige
      (b): la discrepancia entre el ρ estimado y el implícito se **publica**, no se esconde
      → **las dos cosas**: 0.0146197 reproduce el titular y el medido 0.0021243 se publica con
      su factor de 6.88226
- [x] El rombo del simulador de T1.1 pasa a caer **sobre** la curva en el ρ publicado, y la
      guarda de ejecución lo comprueba — **más la afirmación simétrica**: que la curva del ρ
      medido **no** pasa por él, porque la prosa publica esa discrepancia
- [x] **Añadido:** el correlograma se rehace en Python desde el GeoPackage, y las 7 bandas
      cuadran en pares e islas; la I necesita convertir la convención `moran_islas`, y por eso
      se publica `islas` por banda
- [x] **Añadido:** 16 inyecciones nuevas, 16 cazadas, en las tres capas

**Verificación:** cuenta a mano con el ρ publicado · `audita_texto_cap1.py` acepta la
cifra nueva desde el JSON

**Dependencias:** Checkpoint 0 · **Archivos:** `genera_cap1.R`, `ensambla_cap1.py`,
`audita_cap1.py`, `prueba_auditor_cap1.py`, `prueba_ensambla_cap1.py` · **Alcance:** ~~S~~ → **M**
(subió al hacer las dos opciones)

> ✅ **CERRADA el 2026-08-06.** Los dos ρ publicados y su discrepancia medida: **6.88226** en ρ y
> **5.14152** en información. La advertencia que el capítulo ya hacía —«la equicorrelación es
> falsa en el espacio»— **pasa de afirmación a cociente**, y el correlograma enseña por qué: la
> I vale 0.28820 entre vecinos y se vuelve **negativa** a media distancia, donde están 312 508 de
> los 573 306 pares. El rombo del simulador deja de flotar. Tres hallazgos de método: la
> discrepancia `moran_islas` **cambia la segunda cifra**, no la cuarta, en la banda de 0–25 km
> (156 islas de 1 121), y solo publicando `islas` por banda es auditable desde Python; tres
> tolerancias hubo que **medirlas** porque el redondeo se amplifica; y se retiraron dos índices
> mágicos de `cuadra()` antes de añadir series. Informe completo en el Anexo T2.1.

---

#### T2.2 · El puente de φ = 4 al factor 7.86 (P2) ✅ **CERRADA**

> ### ⚠️ No faltaba el camino: sobraba un número con dos nombres
>
> El «61.7» no era una cifra sin derivación. Era una cifra **calculada en el
> ensamblador** —`n(r4['factor'] ** 2, 1)`, línea 721— que no existía en ningún JSON, y
> que pasaba el auditor de prosa **por coincidencia**: `61.7` está entre los 114 307
> valores del índice; `61.75` y `61.748` no. Sobrevivía por tener **un solo decimal**, que
> es justo el régimen que `mide_punto_ciego.py` midió como el peor (se cuela el 63 % de las
> perturbaciones de un dígito, frente al 4,63 % con cinco).
>
> Y al tirar del hilo apareció lo de fondo: **el capítulo llamaba «la información» a dos
> cocientes distintos.**
>
> ```
> efecto de diseño   n/n_eff  = 49.63003     ← lo que el módulo 5 divide
> factor²                     = 61.74778     ← lo que el módulo 4 llamaba «la información»
>                               1.24416 veces de diferencia
> ```
>
> Difieren porque **`s²` también se encoge** con la correlación:
> `E[s²] = σ²(n/(n−1))(1−1/n_eff) = 0.80929·σ²`. El módulo 4 decía «la información se
> divide por unas 61.7»; el ejercicio 4 del mismo capítulo publica que *n* efectivo pasa de
> 256 a **5.15817**, que es dividir por **49.63**. Un estudiante que hiciera 256/61.7 = 4.15
> no llegaba a la cifra que el capítulo publica dos módulos después.

**Descripción:** la fórmula de la varianza está y el número está; falta el camino.
Publicar ρ_vecino = e^(−1/4) = 0.77880, que h se mide en pasos de retícula, y que «unas
61.7» es 7.85798² — porque el error estándar entra al cuadrado en la varianza.

**Criterios de aceptación:**
- [x] El módulo declara la escala de h y el modelo de correlación completo — distancia
      euclídea entre centros de celda en pasos de retícula, σ² = 1, y el *jitter* de 10⁻⁹,
      que estaba en el JSON desde siempre pero la prosa no decía
- [x] Se muestra que 0.77880 = e^(−1/4) y que 61.7 = 7.85798² → **61.74778**, con sus cinco
      decimales, ya no con uno
- [x] Toda cifra nueva viene del JSON — y la vieja también: se retiró la única cifra de la
      prosa que se calculaba en el ensamblador
- [x] **Añadido, por decisión de Javier del 2026-08-07:** se publican **los dos** cocientes
      con nombre propio y se explica por qué no coinciden, en vez de arreglar solo la etiqueta
- [x] **Añadido:** `ρ_diagonal = e^(−√2/4) = 0.70219`, que es lo único que distingue «h es
      distancia» de «h es adyacencia» — sin ella, declarar la escala no sería comprobable
- [x] **Añadido:** retirado el índice mágico `inf["rejilla"][4]`, que es el defecto de T1.2
      en su versión de compilación
- [x] **Añadido:** las tres capas —compilación, auditoría y navegador— probadas por
      inyección, **19 de 19** en las dos automáticas

**Verificación:** ~~auditores en verde · las tres cuentas rehechas a mano~~ → **cinco cuentas,
las cinco cuadran** · `audita_cap1.py` pasa de 937 a **986** comprobaciones · el deslizador
recorrido en las **7 posiciones**, con 7 huellas de píxeles distintas, y también **al volver**

**Dependencias:** Checkpoint 0 · **Archivos:** `genera_cap1.R`, `ensambla_cap1.py`,
`audita_cap1.py`, `prueba_auditor_cap1.py`, `prueba_ensambla_cap1.py` · **Alcance:** ~~S~~ → **M**

> ✅ **CERRADA el 2026-08-07.** El módulo 4 publica ahora el camino entero en tres pasos, y los
> dos cocientes dejan de llamarse igual: **49.63003** es cuánto se ensancha la varianza
> verdadera —y es el puente literal al 5.15817 del módulo 5, o sea que **P3 queda medio
> pavimentada**—; **61.74778** es cuánto se queda corta la que el programa declara. Tres
> hallazgos: el 61.7 **no tenía respaldo, solo coincidencia**; la desigualdad entre los dos
> cocientes **no vale para los siete alcances** —en φ = 0 y 0.5 se invierte, medido, y una
> guarda universal habría puesto rojo un capítulo correcto—; y **el arnés de guardas leía mal
> los paros duros**: `sys.exit("mensaje")` lleva una cadena en `e.code` y el arnés lo contaba
> como código 0, así que cantó «SE COLÓ» de un defecto que el ensamblador había parado en seco.
> Con eso arreglado, el inventario pasa de 53 a **60 guardas** y los **6 paros duros
> preexistentes sin cubrir** salen a la luz en vez de no existir. Informe en el Anexo T2.2.

---

#### T2.2b · Los seis paros duros sin inyectar ✅ **CERRADA**

> **Se escribe entera para que se pueda hacer en una sesión limpia, sin el contexto de T2.2.**
> Todo lo que hace falta está aquí: las firmas de las seis guardas, la sustitución exacta de
> cada una y lo que tiene que salir por pantalla.

**Descripción:** `ensambla_cap1.py` para de dos formas. `problemas.append(…)` acumula y sigue
—53 guardas, todas inyectadas—; `sys.exit("PARADO: …")` no puede seguir y para en seco —**7
guardas, y solo 1 inyectada**, la que estrenó T2.2—. T2.2 arregló el arnés para que las viera
(antes ni las inventariaba, y leía su código de salida como 0); falta cubrirlas.

**Estado de partida:** ~~`54 de 60`~~ → **actualizado el 2026-08-10 por T2.7**, que le añadió
12 guardas al ensamblador y sus 12 inyecciones. Hoy `prueba_ensambla_cap1.py` informa
**`66 de 72 guardas se han visto disparar`** y lista las mismas 6 que faltan —los seis paros
duros, ninguna nueva—. Al acabar esta tarea tiene que decir **72 de 72**. *(Ojo si el número
vuelve a moverse: lo que manda no es la cifra sino que la lista «Sin ver disparar» quede
vacía.)*

**Las seis, con su inyección.** Las guardas se identifican por su **firma** —el trozo literal
más largo de su mensaje, que es como las inventaría `inventario()`— y no por su línea, que se
mueve:

| # | Firma de la guarda | Superficie | Sustitución | Qué tiene que salir |
|---|---|---|---|---|
| 1 | `el ancla de apertura de «` | **plantilla** | duplicar la línea `    const courseData = {`, para que aparezca 2 veces | `PARADO: el ancla de apertura de «courseData + DATOS_CAP1» aparece 2 veces, no 1` |
| 2 | `se encontró DEMASIADO LEJOS; la plantilla ha cambiado.` | ensamblador | `max_lineas=600` → `max_lineas=5` | la región de «los doce módulos» se pasa del tope |
| 3 | `se encontró DEMASIADO PRONTO` | ensamblador | en la llamada de `courseData`, `max_lineas=20)` → `max_lineas=20, min_lineas=99)` | la región se queda corta |
| 4 | `veces, no 1.` *(la de `sustituye`)* | ensamblador | `<title>Plantilla de capítulo — Estadística Espacial</title>` → el mismo texto con una letra cambiada | `el ancla de «título» aparece 0 veces, no 1` |
| 5 | `registros de GEOMAPAS['demo-mapa'], se esperaba 1` | **plantilla** | duplicar la línea que empieza por `    GEOMAPAS['demo-mapa'] =` | `PARADO: 2 registros de GEOMAPAS['demo-mapa'], se esperaba 1` |
| 6 | `PARADO: falta` *(la de `ruta()`)* | **maquinaria nueva** | ver abajo | `PARADO: falta …/no_existe.json` |

**La sexta necesita algo que el arnés no sabe hacer**, y es el único trabajo de diseño de la
tarea. Las dos formas de inyección que hay hoy —mutar un JSON (`obj`) o parchear texto
(`txt`)— **escriben un archivo roto**; ésta necesita lo contrario: que el archivo **no exista**.
Un tercer tipo, `falta`, de unas seis líneas en el bucle de `main()`:

```python
elif tipo == "falta":
    rutas[superficie] = tmp / "no_existe.json"   # y NO se crea
```

Con la comprobación de inercia al revés: en vez de «¿cambió el archivo?», **«¿de verdad no
existe?»**, porque un temporal que sobreviviera de una inyección anterior dejaría la prueba
sin sujeto y se leería igual que un acierto.

**Un aviso que la propia tarea desmiente, y hay que corregirlo al pasar.** La cabecera de
`prueba_ensambla_cap1.py` dice que la plantilla «se redirige pero no se envenena: **no es
alcanzable**». Eso vale para lo que el ensamblador *sustituye* —sus `<template>` y sus
lienzos, que se van y por eso no llegan al marcado—, pero **es falso para las anclas**: las
inyecciones 1 y 5 envenenan la plantilla y llegan. Hay que reescribir ese párrafo con la
distinción, o quedará avisando de lo contrario de lo que la tarea demuestra.

**Criterios de aceptación:**
- [x] `prueba_ensambla_cap1.py` deja **vacía** la lista «Sin ver disparar» (hoy, 72 de 72)
- [x] Las seis salen como `CAZADO`, no como `REVIENTA` ni como `INERTE`
- [x] El tipo `falta` comprueba la ausencia del archivo, no su contenido — *y la comprobación
      nueva se probó por inyección contra el propio arnés (T2.2b.d)*
- [x] La cabecera del arnés deja de decir que la plantilla no es alcanzable, y distingue las
      dos cosas
- [x] `audita_todo.sh --rapido` en verde, y los tres capítulos sin regresión

**Verificación:** `python3 precalculo/prueba_ensambla_cap1.py` · la lista «Sin ver disparar»
tiene que quedar **vacía**

**Dependencias:** T2.2 *(que arregló el `DRIVER`, `males()` e `inventario()`; sin eso estas
seis se informan como coladas aunque el ensamblador las cace)* · **Archivos:**
`prueba_ensambla_cap1.py` · **Alcance:** S

> **Por qué no se hizo en T2.2.** Es un agujero anterior a esa tarea —los 6 llevaban ahí desde
> que se escribieron— y meterlo dentro habría mezclado dos cosas: cerrar P2 y cubrir el arnés.
> T2.2 hizo lo imprescindible: **volverlos visibles**. Cerrarlos es esto.
>
> **Y hay una razón para no dejarlo para el final.** Cuatro de los seis viven en `region()` y
> `sustituye()`, que es exactamente la maquinaria que **T4.1 va a mover** al retropropagar el
> motor `.geomapa` a la plantilla y a los tres capítulos. Tenerlas cubiertas antes convierte
> ese cambio en uno vigilado; después, en uno que se comprueba a ojo.

---

#### T2.3 · La línea base del 8.07× de Snow (P4)

**Descripción:** repartir 578 muertes entre 13 bombas por igual supone que las bombas
tienen la misma población alrededor, que es falso y no se dice. Dos correcciones: (i)
declarar el supuesto y su dirección de sesgo; (ii) añadir un contraste de aleatorización
—reasignar las muertes al azar sobre las calles y ver dónde cae el 62,11 % en la
distribución nula—, que es la misma técnica que el módulo 3 ya usa y que convierte el
argumento en medida.

**Criterios de aceptación:**
- [ ] El supuesto de la línea base uniforme queda declarado con su dirección de sesgo
- [ ] Contraste de aleatorización calculado en R, con su n de permutaciones y su semilla
- [ ] La advertencia existente («lo que el mapa NO demuestra») se conecta con el contraste nuevo, sin duplicarse

**Verificación:** `audita_cap1.py` recalcula el contraste desde `HistData` · el resultado
es reproducible con la semilla publicada

**Dependencias:** Checkpoint 0 · **Archivos:** `genera_cap1.R`, `ensambla_cap1.py`,
`audita_cap1.py` · **Alcance:** M

---

#### T2.4 · Cinco procedencias sueltas (P5, P6, P8, P9, P12)

**Descripción:** cinco huecos pequeños que se cierran juntos porque comparten patrón —un
número o una conclusión sin su entrada:
- **P12** que el mapa del módulo 4 es de 28×28 y la simulación de la que salen las cifras
  es de 16×16. Una frase basta, y de paso enseña algo: la resolución de una figura es una
  decisión de presentación y no tiene por qué coincidir con la del cálculo;
- **P5** el origen de «base teórica 0.36» del módulo 7;
- **P6** la fuente del gradiente térmico del módulo 3 (el gradiente adiabático ambiental
  típico ronda los 6,5 °C/km: citarlo o dejar de llamarlo «esperable»);
- **P8** cómo se calcula el R² por bloques —media global o por pliegue— y el efecto de
  pliegues de 1 a 64 estaciones;
- **P9** qué contraste y a qué α produce el 82 % del módulo 6, y por qué el rezago 4.

**Criterios de aceptación:**
- [ ] Los cuatro tienen su origen declarado en el texto
- [ ] P6 cita fuente o se reformula
- [ ] P8 nombra el convenio de R² explícitamente

**Verificación:** auditores en verde · repaso de los cuatro pasajes

**Dependencias:** Checkpoint 0 · **Archivos:** `genera_cap1.R`, `ensambla_cap1.py` · **Alcance:** M

---

#### T2.5 · La banda nula del correlograma (P7)

**Descripción:** «la última banda ya no se distingue de la independencia» se afirma. El
control permutado ya está en el gráfico, pero como una línea, no como **banda**. Con una
envolvente de permutaciones (5 %–95 %) la afirmación se ve en vez de leerse — y es la
misma figura que el capítulo 4 usará para las funciones K y G, así que enseña dos veces.

**Criterios de aceptación:**
- [ ] Envolvente de permutaciones por banda, calculada en R con semilla declarada
- [ ] La banda se dibuja tras la serie real, sin taparla
- [ ] El texto pasa de «ya no se distingue» a la lectura de la envolvente

**Verificación:** `audita_cap1.py` recalcula la envolvente · la serie real sale de la
banda en las bandas cortas y entra en las largas

**Dependencias:** ~~T1.4~~ ✅ **cerrada** (comparte el simulador) · **Archivos:** `genera_cap1.R`,
`ensambla_cap1.py`, `audita_cap1.py` · **Alcance:** M

> **Lo que T1.4 le deja montado, y una decisión que tomar de entrada.** El simulador ya tiene
> `SERIES` —una sola lista de la que salen el trazo, el interruptor y las filas de la lectura— y
> `DEBE`, el emparejamiento rótulo↔serie del JSON que la guarda usa **por segunda vez y aparte**,
> para que comprobar el trazo no sea tautológico. La envolvente es una serie más: **si lleva
> interruptor entra en las dos listas; si es fondo de la permutada, va atada a la casilla de
> esta**. Y las tres series comparten rejilla de bandas por una guarda de compilación nueva, así
> que la envolvente tendrá que traer las mismas siete bandas o el ensamblador para. Anexo T1.4.d.

---

#### T2.6 · La incertidumbre de los cocientes, y la convención de los cinco decimales

**Descripción:** cierra M4 y el defecto P10. (i) Publicar el error de Monte Carlo o el
intervalo *bootstrap* junto a los cocientes derivados que hoy salen con cinco decimales
desnudos; (ii) declarar en el módulo 4 que 33 bloques son pocos y que la partición
departamental es la misma decisión que el módulo 7 denuncia —el capítulo se contradice
suavemente y conviene que sea él quien lo diga—; (iii) una nota que explique por qué todo
el material lleva cinco decimales, citando la medición del punto ciego.

**Criterios de aceptación:**
- [ ] Los cocientes derivados llevan su incertidumbre donde exista
- [ ] El módulo 4 declara la limitación de 33 bloques y la enlaza con el módulo 7
- [ ] La nota sobre los cinco decimales explica la razón medida, no la costumbre

**Verificación:** auditores en verde · las incertidumbres nuevas se recalculan desde R

**Dependencias:** T0.2 · **Archivos:** `genera_cap1.R`, `ensambla_cap1.py` · **Alcance:** M

---

### ✅ Checkpoint 2 — ninguna cifra sin entrada visible
- [ ] Los once defectos de procedencia, cerrados o declarados por escrito
- [ ] Los dos auditores en verde y la cadena reproducible de cero
- [ ] **Tu revisión antes de seguir**

---

### Fase 3 — Las derivaciones, en paneles plegables

---

#### T3.1 · El componente `.derivacion`

**Descripción:** un panel plegable con el mismo comportamiento que `.ejercicio-panel`
—que ya existe, con su `aria-expanded` y su `aria-controls`— pero con identidad propia,
para no confundir «solución de un ejercicio» con «de dónde sale esta fórmula». Se
retropropaga a la plantilla en cuanto exista, que es la regla de la casa.

**Criterios de aceptación:**
- [ ] Plegable, accesible por teclado, con `aria-expanded` correcto
- [ ] Presente en `plantilla/plantilla-capitulo.html` y en `prueba-geomapa.html`
- [ ] KaTeX renderiza dentro del panel al abrirlo (ojo: contenido oculto en la primera pasada)

**Verificación:** navegación por teclado · una fórmula dentro del panel se ve bien al abrir

**Dependencias:** Checkpoint 2 · **Archivos:** `plantilla/plantilla-capitulo.html`,
`ensambla_cap1.py`, `Htmls_Espacial/prueba-geomapa.html` · **Alcance:** M

---

#### T3.2 · Tres derivaciones (P3, P2, y el mecanismo del módulo 7)

**Descripción:** el álgebra que el capítulo salta, en tres paneles:
1. **Var(Z̄) → n_eff** (módulos 4→5): bajo equicorrelación, `Var(Z̄) = σ²/n · [1+(n−1)ρ]`,
   y n_eff es el n que daría esa varianza sin correlación. Son tres líneas y cierran P3.
2. **De ρ(h) = e^(−h/φ) al factor 7.86** (módulo 4): ~~cierra P2~~ → **P2 ya está cerrada
   por T2.2**, que publicó los tres tramos con sus cifras y sus nombres. Lo que queda para
   el panel es **la suma explícita** —desarrollar `1'R1` sobre las 256 celdas hasta el
   49.63003— y la derivación de `E[s²] = σ²(n/(n−1))(1−1/n_eff)`, que T2.2 publica como
   fórmula y como medida pero no demuestra. El panel hereda las cifras; solo tiene que
   poner el álgebra.
3. **Gehlke–Biehl algebraico** (módulo 7): descomposición en componente compartido + ruido
   blanco, y qué le pasa a cada varianza al promediar m celdas. La versión actual es
   cualitativa y correcta; la algebraica hace visible **por qué la condición es que el
   ruido no tenga estructura espacial**, que es justo lo que el módulo dice que se omite.

**Criterios de aceptación:**
- [ ] Las tres derivaciones son autocontenidas y rehacibles con lápiz
- [ ] Cada una termina en la cifra que el módulo publica
- [ ] Ninguna cifra nueva fuera del JSON

**Verificación:** rehacer las tres a mano hasta la cifra publicada · auditores en verde

**Dependencias:** T3.1 · **Archivos:** `ensambla_cap1.py` · **Alcance:** M

---

#### T3.3 · La derivación de E[I] = −1/(n−1)

**Descripción:** el módulo 3 dice que I no vale cero bajo la nula y lo explica como «el
artefacto de comparar cada unidad consigo misma excluida» — que es una pista, no una
explicación. Un panel con el argumento de permutación lo cierra, y ese argumento es el
mismo que sostiene la banda nula de T2.5 y las envolventes del capítulo 4.

**Criterios de aceptación:**
- [ ] La derivación llega a −1/(n−1) desde la esperanza bajo permutación aleatoria
- [ ] Enlazada con la envolvente de T2.5 y con el capítulo 7
- [ ] Con n = 361 reproduce el −0.002778 publicado

**Verificación:** la cuenta con n = 361 da la cifra del texto · auditores en verde

**Dependencias:** T3.1 · **Archivos:** `ensambla_cap1.py` · **Alcance:** S

---

### ✅ Checkpoint 3 — el álgebra está, y no estorba
- [ ] Los cuatro paneles abren, cierran y renderizan KaTeX
- [ ] El capítulo no ha crecido a la vista
- [ ] **Tu revisión antes de seguir**

---

### Fase 4 — Los seis mapas del módulo 2

> Va la última a propósito: es la que toca el **motor**, y el motor lo comparten los
> capítulos 2 y 3, que están cerrados. Se hace cuando todo lo demás esté verde.

---

#### T4.1 · Controles y *hover* en el motor `.geomapa`

**Descripción:** el motor de este capítulo no registra un solo `addEventListener`. Los
capítulos 2 y 3 sí usan `.geomapa-controles`, así que el patrón existe y hay que **traerlo,
no inventarlo**. Añadir además *hover* con lectura del rasgo bajo el cursor, que es lo que
convierte un coropleto en algo explorable — y decidir de entrada si eso vive en el motor
(y se retropropaga a los tres capítulos) o solo aquí.

**Criterios de aceptación:**
- [ ] `.geomapa-controles` funciona en el capítulo 1 igual que en el 2
- [ ] *Hover* muestra la etiqueta y el valor del rasgo, sin romper el presupuesto de peso que audita `audita_texto_base.geomapas()`
- [ ] Alternativa por teclado, o el *hover* es estrictamente decorativo y se declara
- [ ] Retropropagado a la plantilla y a `prueba-geomapa.html`
- [ ] **Los capítulos 2 y 3 se re-ensamblan y se re-auditan: cero regresiones**

**Verificación:** los tres capítulos recorridos módulo a módulo, consola limpia, todos los
mapas con tinta · los seis auditores en verde

**Dependencias:** Checkpoint 3 · **Archivos:** `plantilla/plantilla-capitulo.html`,
`ensambla_cap1.py`, `ensambla_cap2.py`, `ensambla_cap3.py`, `prueba-geomapa.html` · **Alcance:** L

---

#### T4.2 · Cablear los seis mapas del módulo 2

**Descripción:** pinos, Bogotá, nc, deserción, meuse e IDEAM están hoy como seis lienzos
sueltos. Con controles, el módulo pasa de «mira estos seis mapas» a «comprueba tú que la
diferencia no está en el aspecto». La pregunta que reparte el curso —«¿qué es aleatorio
aquí?»— se puede **contestar sobre el mapa** en vez de leerla debajo.

**Criterios de aceptación:**
- [ ] Los tres pares (puntual / área / geoestadístico) comparten control, para que la comparación sea del mismo gesto
- [ ] Cada mapa expone lo que enseña su tipo: ventana en los puntuales, cortes de clase en los de área, valor medido en los geoestadísticos
- [ ] La nota de la ventana (5.69321 vs 1.35200 sedes/km²) se puede **provocar desde el mapa**
- [ ] Ninguna cifra nueva fuera del JSON

**Verificación:** los seis mapas responden · presupuesto de peso dentro de límite ·
auditores en verde

**Dependencias:** T4.1 · **Archivos:** `ensambla_cap1.py`, `genera_cap1.R` (si hace falta
exportar la ventana alternativa) · **Alcance:** M

---

### ✅ Checkpoint 4 — capítulo cerrado
- [ ] Los 12 módulos recorridos, consola limpia, todos los mapas con tinta
- [ ] Cadena reproducible desde cero; los seis auditores de los tres capítulos en verde
- [ ] Sin regresión en los capítulos 2 y 3
- [ ] **Tu revisión final**

---

## 4. Riesgos

| Riesgo | Impacto | Mitigación |
|---|---|---|
| ~~La cadena no reproduce hoy~~ | ~~Alto~~ | ✅ **Descartado en T0.1.** Reproduce; la única deriva era un campo de metadatos declarado, ya corregido |
| **Una reescritura borra una frase de `AFIRMACIONES` y tumba el auditor** | **Alto** | **Nuevo, de T0.1.d.** Criterio de aceptación en todas las tareas de las fases 2 y 3: conservar la frase o actualizar la lista del auditor en el mismo cambio |
| ~~El capítulo revienta el tope de 560 KB, que es fallo duro~~ | ~~Alto~~ | ✅ **Retirado en T1.1, y era el riesgo equivocado.** El tope no era un presupuesto diseñado: empezó en 550, subió a 560 y a 680 según qué capítulo chocaba, y en T1.1 llegó a **decidir el material** —iba a recortar comentarios del código para ganar 1,3 KB—. Un capítulo es un HTML que se descarga una vez y sus tres CDN pesan más que él. Ahora es una **alarma contra un ensamblado desbocado** con un tope de casa de 700 KB, y el margen del capítulo 1 pasó de 29,9 a **169,9 KB (76 % del tope)**. La cota que lo hace no arbitrario: `prueba_texto.py` tumba la comprobación con +312 KB, así que subirlo de más pone **rojo el arnés**. Anexo T1.1.g |
| T4.1 toca el motor y rompe los capítulos 2 y 3 | **Alto** | Va la última, con los tres capítulos re-auditados como criterio de aceptación |
| Una cifra redondeada en la prosa hace fallar el auditor de texto | Medio | M4 revisada: no se redondea nada; el arreglo es de tipo, no de precisión |
| El capítulo crece hasta ser inmanejable | Medio | M3: derivaciones en paneles plegables, no en línea |
| ~~Las cifras nuevas alargan el precálculo~~ | Bajo | ✅ **Medido en T0.1.a:** el bucle completo del capítulo 1 cuesta 1 min 25 s, no 10 min. T2.3 y T2.5 son asequibles |
| Los paneles plegables rompen KaTeX (contenido oculto al renderizar) | Bajo | Criterio explícito en T3.1; es un fallo conocido de este patrón |
| El *hover* deja fuera a quien navegue por teclado | Bajo | Criterio de accesibilidad en T4.1: alternativa o decorativo declarado |
| No hay verificación visual real: el panel sirve `file://` con ancho 0 | Bajo | T0.1.f lo declara. Si importa, montar un servidor HTTP local (pregunta abierta 2 del anexo) |

---

## 5. Preguntas abiertas (no bloquean el arranque)

1. ~~**T1.2** — ¿opción (a), barata y honesta, o (b), con rejilla densa en R?~~ → **(a)**, y
   después **los campos de φ = 0 y φ = 16** que faltaban, por 8,5 KB. El deslizador recorre
   los siete alcances de la rejilla de cifras. Cerrada; Anexo T1.2.j.
2. **T0.2** — el factor entero `1` del ejercicio 1: ¿`1` o `1.00000`? Como factor,
   `1.00000` comunica mejor «no se movió nada».
3. **T4.1** — ¿el *hover* entra en el motor (y con él en los capítulos 2 y 3) o se queda
   en el 1? Meterlo en el motor es más caro ahora y más barato en los siete capítulos que faltan.
4. ~~**Nueva, de T1.3** — las guardas de compilación del ensamblador no tienen arnés
   permanente. ¿Lo montamos antes de la Fase 2 o se deja para el final?~~ → **antes**, decidido
   por Javier el 2026-08-06 y **hecho**: `prueba_ensambla_cap1.py`, paso 3 de `audita_todo.sh`.
   Y no eran cinco familias sino **41 guardas**: **40 inyecciones, 40 cazadas, 41/41 guardas
   vistas disparar**, en 2,3 s. Cerrada; Anexo T1.3.n. **Queda vivo lo de los otros capítulos:**
   `ensambla_cap2.py` tiene 7 guardas y `ensambla_cap3.py` 5, todas sin arnés, y el bucle de
   `audita_todo.sh` las recogerá solas en cuanto existan los dos guiones.
5. **T2.3** — el contraste de aleatorización de Snow necesita un modelo nulo. ¿Uniforme
   sobre la ventana, o condicionado a las 528 calles? El segundo es más defendible y más caro.
6. ¿Este plan se incorpora como una fase del `PLAN_Material_Estadistica_Espacial.md`
   principal, o vive aparte hasta cerrarse?
7. ~~**Nueva, de T2.2** — los 6 paros duros sin cubrir del ensamblador~~ → **contestada y
   convertida en tarea: T2.2b**, escrita entera —las seis firmas, la sustitución de cada una
   y el tipo `falta` que hay que añadir al arnés— para poder ejecutarse en una sesión limpia.
   Va **antes** de T4.1 y no después: cuatro de las seis viven en `region()` y `sustituye()`,
   que es la maquinaria que T4.1 mueve.
8. **Nueva, de T2.2 — y ya contestada, se deja escrita porque la respuesta importa.** ¿El
   punto ciego del `sys.exit` con cadena está también en los otros arneses? **No.**
   `prueba_auditor_cap1/2/3.py` y `prueba_texto.py` leen `res.returncode` del subproceso, y
   ahí el 1 de un `sys.exit("mensaje")` llega intacto. El fallo era **estructural y único de
   `prueba_ensambla_cap1.py`**: es el único que ejecuta el objetivo *en proceso*, con
   `runpy`, porque lo necesita para trazar la cobertura con `sys.settrace` — y por eso tiene
   que reconstruir a mano un código de salida que los demás reciben del sistema
   operativo. **Lo que sí queda vivo** es que `ensambla_cap2.py` y `ensambla_cap3.py` seguirán
   sin arnés (pregunta 4), y el suyo, cuando exista, nacerá de este molde: hay que copiarlo
   **después** del arreglo, no antes.

---

## 6. Resumen de alcance

| Fase | Tareas | Alcance | Toca R | Toca el motor | Estado |
|---|---|---|---|---|---|
| 0 · Línea base | 3 | S + XS + XS | no | no | **✅ CERRADA (T0.1, T0.2, T0.3)** |
| 1 · Interactividad prometida | 4 | M×4 | solo T1.3 | no | **✅ CERRADA (T1.1, T1.2, T1.3, T1.4)** |
| 2 · Procedencia | ~~6~~ **7** | ~~S~~ **M**, ~~S~~ **M**, **S** *(T2.2b)*, M, M, M, M | sí | no | **T2.1 ✅ · T2.2 ✅ · T2.2b ✅ · faltan T2.3–T2.6** |
| 3 · Derivaciones | 3 | M, M, S | no | plantilla | pendiente |
| 4 · Mapas del módulo 2 | 2 | L + M | quizá | **sí** | pendiente |

Ninguna tarea toca más de cinco archivos salvo T4.1, que es L y por eso va aislada al
final, detrás de tres revisiones tuyas.

**Presupuesto de tiempo, ya no estimado sino medido (T0.1.a):** cada iteración sobre el
capítulo 1 —tocar R, regenerar, ensamblar, auditar— cuesta **1 min 25 s**. Un checkpoint
con el arnés de los tres capítulos, **4 min 14 s**. El arnés completo con inyección, más de
10 min, y por eso se reserva para el cierre de cada fase y no para cada cambio.

**Criterios de aceptación transversales, añadidos tras T0.1 y T0.2.** Toda tarea de las
fases 2 y 3 los hereda:

> - [ ] Las frases de `AFIRMACIONES`, `DEBE_CUBRIR` y `FUENTES` que toca el pasaje
>       reescrito siguen presentes, o se actualiza la lista de `audita_texto_cap1.py`
>       **en el mismo cambio**, diciendo por qué. *(de T0.1.d)*
> - [ ] ~~El capítulo sigue por debajo de 560 KB~~ → **el peso ya no es un criterio de
>       aceptación.** Manda el contenido: la comprobación quedó como alarma contra un
>       ensamblado desbocado, con 169,9 KB de margen. Ninguna tarea de las fases 2 a 4 tiene
>       que medir bytes ni justificar un dato nuevo por su tamaño. *(decisión de Javier del
>       2026-08-06, en T1.1; el razonamiento vive en `audita_texto_base.TOPE_KB`)*
> - [ ] **En el código, el titular; en el anexo, la historia.** La regla se queda, pero
>       fundada en otra cosa: no en los bytes —ya no cuentan— sino en que un comentario de
>       quince líneas dentro de una función se deja de leer. Explica *qué* decisión se tomó y
>       por qué en dos o tres líneas, y apunta al anexo para el relato.
>       *(de T1.2, refundada en T1.1)*
> - [ ] **Inyectado al menos un defecto del tipo que este cambio hace posible, y el auditor
>       lo detecta.** Si no lo detecta, la tarea no está terminada: falta la comprobación,
>       no sobra el defecto. *(de T0.2.g — los dos auditores dieron verde con un agujero
>       abierto, y solo la inyección lo encontró)*
> - [ ] **Toda guarda de compilación nueva entra en `prueba_ensambla_capN.py` en el mismo
>       cambio.** El arnés inventaria las guardas con `ast` y **mide** cuáles se han visto
>       disparar, así que una guarda añadida y no inyectada aparece sola en la lista de «sin
>       ver disparar» de la siguiente pasada. No hay que acordarse: hay que no ignorarlo.
>       *(de T1.3.n)*

**Y tres más para toda tarea que cablee un control** —nacieron en la Fase 1, pero la que
más las va a necesitar es la **Fase 4**, que cablea siete mapas— de T0.4.d, T1.2.d y T1.3.f:

> - [ ] Cada control probado **botón a botón / posición a posición** en el navegador,
>       comprobando que lo dibujado coincide con lo que dice la lectura. Un simulador con
>       dos índices paralelos es culpable hasta que se demuestre lo contrario: así estaba
>       `ee-ingenuo`, con los dos auditores en verde.
> - [ ] **La guarda nueva, probada reinyectando el defecto que viene a cazar** — y leyendo de
>       dónde saca el dato. En T1.2 la primera versión buscaba el campo *por su cuenta* en vez
>       de leer la fuente que invoca el motor: comprobaba que el dato existía, no que fuera el
>       dibujado, y **dio verde con el defecto original dentro**. La inyección la encontró; el
>       repaso del código, no. *(de T1.2.d)*
> - [ ] **Cada control probado también AL VOLVER**, no solo al llegar: elegir una posición,
>       salir del módulo, entrar otra vez y comprobar que el mando sigue diciendo lo que el
>       gráfico dibuja. El estado que sobrevive a `loadModule` es una dimensión más del
>       simulador y no estaba en ninguna lista: `una-realizacion` y `snow-mapa` volvían con el
>       botón marcando el primero y el mapa en el que el estudiante había elegido, y la prueba
>       posición a posición no puede verlo porque nunca sale del módulo. *(de T1.3.f)*

**Cómo abrir el navegador** (T0.4.e): `preview_start {name:"espacial"}` →
`http://localhost:8931/Htmls_Espacial/…` → **`resize_window {width:1280, height:900}`**,
que es imprescindible: el preset «desktop» deja el viewport en 0 y todo Chart.js sale vacío.

---
---

# Anexo T0.1 — La línea base, y lo que destapó

**Ejecutada:** 2026-08-05 · **Resultado:** cerrada en verde · **Fallos encontrados:** 0
**Hallazgos que cambian el plan:** 3

## T0.1.a · Qué se ejecutó, y cuánto costó

El dato que el Checkpoint 0 pedía —cuánto tarda una pasada completa— resultó tener dos
respuestas muy distintas, y la diferencia importa para planificar el resto:

| Paso | Tiempo | Salida |
|---|---:|---|
| `genera_cap1.R` | **1 min 12 s** | 0 · 20 anclas contra la literatura verificadas |
| `genera_soluciones.R` | **2,4 s** | 0 · solo rehace el capítulo 1 |
| `ensambla_cap1.py` | **0,05 s** | 0 · 9 sustituciones, ensamblado limpio |
| `audita_cap1.py` | **10,8 s** | 0 · 836 comprobaciones |
| `audita_texto_cap1.py` | **0,27 s** | 0 · 140 comprobaciones |
| **`audita_todo.sh --rapido`** (los 3 capítulos) | **4 min 14 s** | 0 · 2 112 comprobaciones |
| `audita_todo.sh` completo (con inyección) | **> 10 min** | — · cortado por tiempo |

**Consecuencia para el plan:** el bucle de trabajo real —tocar R, regenerar, ensamblar y
auditar el capítulo 1— cuesta **~1 min 25 s**, no los diez minutos que hacían temer los
arneses de inyección. Las tareas que tocan `genera_cap1.R` (T1.3, T2.1–T2.6) son mucho
más baratas de lo presupuestado. El arnés completo con inyección se reserva para los
checkpoints, no para cada iteración.

`verifica_bloques.py` —que **ejecuta de verdad** los bloques R/Python de los tres
capítulos y contrasta sus `#>`— es el 85 % de esos 4 min 14 s.

## T0.1.b · Hallazgo 1: el capítulo publicado no salía del árbol de fuentes actual

**Lo que se esperaba.** Que el HTML regenerado difiriera solo en `meta.generado`, la
excepción que `prueba_reproducible.sh` ya declara. Predicción escrita antes de ejecutar:
**exactamente 2 líneas, la 5115 y la 5116.**

**Lo que salió.** Tres bloques, no dos. Los dos previstos, y además las líneas 7583 y
7594 — los literales de los mapas `nc` y `desercion`—, cada una con una inserción:

```
, "codificacion": "absoluta"
```

28 caracteres × 2 mapas = **+56 bytes exactos**, que es toda la diferencia de tamaño del
archivo (522 783 → 522 839). El número de líneas no cambió: 8 505 antes y después.

**Por qué.** `geo.R` ganó la codificación de geometría por diferencias durante el
capítulo 3, y `geo_poligonos()` escribe desde entonces el campo `codificacion` siempre,
con valor `"absoluta"` cuando no se usa delta. El propio código lo dice, y la decisión
está razonada (`geo.R:122-126`):

> *«Va como OPCIÓN y no por defecto, y eso es deliberado: los capítulos 1 y 2 ya están
> publicados y verificados con la codificación absoluta, y cambiarles el JSON por debajo
> obligaría a regenerarlos y volver a auditarlos para ahorrar unos kilobytes que no les
> hacen falta.»*

La decisión fue correcta. El efecto secundario **no estaba anotado**: desde entonces el
capítulo 1 publicado es un artefacto que el árbol de fuentes ya no reproduce.

**Impacto: nulo.** El motor del capítulo 1 lee el campo en la línea 6865 —
`if (d.codificacion !== 'delta') return d.geom;` — así que el campo ausente y el valor
`"absoluta"` se comportan idénticamente. **Ni un byte de geometría cambió**: `caja`, `q`,
`geom`, `valor`, `cortes`, `clase` y `etiquetas` son idénticos, verificado campo a campo.

**Estado:** resuelto. El capítulo publicado es ahora el que produce el árbol de fuentes.
Se hereda una tarea nueva.

> **T0.3 (nueva) · El capítulo 2 tiene la misma deriva.** Sus 3 mapas publicados tampoco
> llevan `codificacion` (los 7 del capítulo 3 sí). No es urgente y el efecto es el mismo
> —ninguno—, pero conviene cerrarlo antes de que el capítulo 4 añada una tercera variante.
> **Alcance: XS.**

## T0.1.c · Hallazgo 2: quedan 49,5 KB, y el tope es un fallo duro

`audita_texto_cap1.py:166` declara `a.peso(560)`, y `Auditor.peso()` lo aplica con
`exige()` —fallo, no aviso—. El capítulo está en **511 KB, el 91 % del presupuesto**.
Que el capítulo 3 ya necesitara subir su tope a 680 KB dice que el margen no es teórico.

| Parte | KB | % |
|---|---:|---:|
| JS en línea (incl. los mapas) | 321,7 | 63,0 |
| contenido de los 12 módulos | 95,8 | 18,8 |
| literales de `.geomapa` | 88,8 | 17,4 |
| CSS | 81,5 | 16,0 |

**Consecuencia para el plan.** La Fase 3 es prosa y álgebra: caben de sobra. La Fase 4 es
la que hay que vigilar — pero midiendo los nueve mapas aparece que sale barata:

| Mapa | KB | n | ¿etiquetas? |
|---|---:|---:|---|
| bogota | 26,1 | 2 209 | no |
| snow | 24,4 | 578 | no |
| desercion | 15,1 | 33 | **sí** |
| nc | 13,1 | 100 | **sí** |
| ideam | 6,5 | 361 | no |
| meuse | 2,7 | 155 | no |
| japanesepines / redwood / cells | 2,4 | 169 | no |

Los dos mapas de polígonos —los únicos que necesitan etiquetas para un *hover*— **ya las
traen**. Los de puntos no las necesitan: su lectura se deriva de coordenadas que ya están
en el JSON. **La Fase 4 puede costar casi 0 KB.**

## T0.1.d · Hallazgo 3: el auditor exige frases literales

`audita_texto_cap1.py` lleva una lista `AFIRMACIONES` de **12 frases que el capítulo está
obligado a contener**, comprobadas por subcadena. Varias caen justo en los pasajes que las
fases 2 y 3 van a reescribir:

| Frase exigida | Tarea que la pisa |
|---|---|
| `"no tenga estructura espacial"` | T3.2 (derivación Gehlke–Biehl) |
| `"no es «la buena» siempre"` (comillas angulares) | T2.4 (P8, la CV por bloques) |
| `"geométrico"` | T2.3 (la línea base de Snow) |
| `"equicorrelación"` | T2.1 (el ρ del módulo 5) |
| `"no es la estimación, es"` | T2.6 (sesgo vs. confianza) |
| `"es del capítulo 10"` | T2.4 |

Y hay tres listas más que restringen igual: `DEBE_CUBRIR` (24 temas), `FUENTES` (14
autores e instituciones) y `CADENAS` (28 caracteres y palabras que delatan si se rompe la
codificación).

**Consecuencia para el plan.** Se añade a **todas** las tareas de las fases 2 y 3 este
criterio de aceptación:

> - [ ] Las frases de `AFIRMACIONES`, `DEBE_CUBRIR` y `FUENTES` que toca el pasaje
>       reescrito siguen presentes, o se actualiza la lista del auditor **en el mismo
>       cambio** y se dice por qué.

La segunda mitad importa tanto como la primera: si una reescritura mejora una frase, lo
correcto es cambiarla en los dos sitios a la vez, no rodear al auditor.

## T0.1.e · Hallazgo menor: el capítulo 3 no puede ser reproducible

`genera_soluciones.R:1241` escribe `format(Sys.time(), "%Y-%m-%dT%H:%M:%S")` en
`cap3_soluciones.json`, mientras las líneas 376 y 868 usan `Sys.Date()` para los capítulos
1 y 2. Con segundos dentro, el capítulo 3 no es reproducible byte a byte **ni ejecutándolo
dos veces el mismo minuto**, y `prueba_reproducible.sh` solo sabe perdonar el campo
`"generado"` cuando la diferencia es la fecha.

Fuera del alcance de esta tarea y del capítulo 1. Anotado para quien cierre el capítulo 3.

## T0.1.f · Verificación

Lo que se comprobó, y con qué:

- **Ningún control se perdió en silencio.** `audita_cap1.py`: **836 = 836** comprobaciones,
  0 fallos, 3 saltadas. `audita_texto_cap1.py`: **140 = 140**, 0 fallos. Comparados línea a
  línea: **un solo veredicto cambió de texto**, el presupuesto de geometría (88,7 → 88,8 KB),
  que son los +56 bytes del campo nuevo. Los dos siguen en OK.
- **El arnés completo.** `audita_todo.sh --rapido` antes y después: **9 pasos OK, 0 fallos,
  salida 0** las dos veces, con las siete cuentas de comprobaciones idénticas
  (836, 445, 356, 77, 140, 128, 130 = **2 112**).
- **Las 20 anclas contra la literatura** de `genera_cap1.R` pasaron: Snow 578/13/528, los
  patrones de spatstat 65/62/42, nc 100 condados y 667 muertes, meuse 155, y las cifras
  titulares salieron idénticas (62,11 % · cobertura 0,1970 · factor 7,8580 · n_eff 64,52 ·
  I 0,3809 → 0,0636 · RMSE +75,34 %).
- **En el navegador.** Consola limpia salvo el aviso conocido del CDN de Tailwind. Chart.js
  y KaTeX cargan. Los 12 módulos recorridos: los **9 `.geomapa` con tinta**, los 8 gráficos
  instanciados con datos reales (m1 3 series/87 puntos, m3 4/28, m4 4/28, m5 4/35, m6 5/40,
  m7 2/10, m10 1/2) y **9/9 lecturas numéricas rellenas**.

**Lo que NO se pudo verificar, y se dice:**

- El conteo de píxeles de los lienzos de Chart.js. El panel de vista previa sirve los
  `file://` como instantánea estática con `window.innerWidth === 0`, y Chart.js es
  responsivo: sus lienzos salen de ancho 0. Se sustituyó por una comprobación más fuerte
  —que cada gráfico esté cableado a sus series y puntos— pero no es lo mismo que ver el
  dibujo. Para una verificación visual de verdad haría falta servir la carpeta por HTTP.
- `prueba_reproducible.sh` (ejecutar el generador dos veces seguidas). Se omitió a
  propósito: el JSON regenerado hoy coincide con el del **2026-08-04** salvo la fecha y el
  campo declarado, lo que es evidencia de determinismo **entre días**, más fuerte que dos
  ejecuciones del mismo minuto. Cuesta 2,5 min si se quiere de todos modos.
- Los arneses de inyección (`prueba_auditor_cap1.py`, `prueba_texto.py`). El primero salió
  **OK** en la corrida inicial completa; el segundo salió OK en el arnés completo previo.
  Ninguno de los dos depende de nada que T0.1 haya tocado.

## T0.1.g · Cambios en disco

| Archivo | Cambio |
|---|---|
| `precalculo/salidas/cap1_datos.json` | `meta.generado` 08-04 → 08-05 |
| `precalculo/salidas/cap1_soluciones.json` | `meta.generado` 08-04 → 08-05 |
| `precalculo/salidas/cap1_mapas.json` | +52 B: `codificacion` en `nc` y `desercion` |
| `Htmls_Espacial/capitulo-1-datos-espaciales.html` | +56 B, 3 bloques, 8 505 líneas |

Ningún otro archivo del proyecto se tocó: los JSON de los capítulos 2 y 3 son idénticos
byte a byte, verificado. Respaldo del estado previo en el directorio de trabajo de la
sesión.

## T0.1.h · Preguntas abiertas que deja *(1 resuelta, ver Anexos T0.2 y T0.3)*

1. ~~**T0.3** (la deriva del capítulo 2): ¿ahora, o cuando toque el capítulo 2 por otra
   cosa?~~ → **ahora**. Cerrada; Anexo T0.3.
2. ~~¿Merece la pena montar un servidor HTTP local?~~ → **sí**, y resultó que
   `.claude/launch.json` **ya existía** con la configuración exacta que iba a proponer
   (`python3 -m http.server 8931`): no había que crear nada, solo arrancarlo. Anexo T0.4.
3. ~~La marca de tiempo del capítulo 3~~ → **alineada a `Sys.Date()`**. El capítulo 3 ya es
   reproducible byte a byte. Anexo T0.5.

---
---

# Anexo T0.3 — La deriva del capítulo 2, cerrada

**Ejecutada:** 2026-08-05 · **Resultado:** cerrada en verde · **Alcance real:** XS, como se preveía

## Predicción, escrita antes de ejecutar

El campo `codificacion` solo lo escribe `geo_poligonos()`. El capítulo 2 tiene **3 mapas de
polígonos** de sus 7 (`error_3116`, `sesgo_localidades`, `geohash`; los otros cuatro son
`proyeccion` y `puntos`). Luego: **+3 × 28 = +84 bytes** en el HTML, más el cambio de fecha,
que no altera la longitud.

## Lo que salió

| | Predicho | Real |
|---|---|---|
| Mapas que ganan el campo | 3, los de polígonos | 3, los de polígonos ✓ |
| Bytes del HTML | +84 | **+84** ✓ |
| Bloques del diff | 3 mapas + fechas | 4 bloques: 5168, 5169, 7612, 7632, 7637 ✓ |
| Líneas del archivo | sin cambio | 8 464 → 8 464 ✓ |

Verificado carácter a carácter: en las tres líneas de mapa el único cambio es una inserción
de `, "codificacion": "absoluta"`; en las dos de fecha, un `'4'` que pasa a `'5'`.

`genera_cap2.R` corrió en **1 min 23 s** con sus **29 anclas** contra la literatura
verificadas.

## Un susto propio, y era mío

Al comprobar si `cap2_soluciones.json` tenía una segunda deriva, mi guion informó
*«DIFIERE en algo que no es la fecha»*. No era cierto: yo buscaba el campo en la raíz del
JSON, y en el capítulo 2 vive bajo `meta`. La comparación byte a byte lo zanjó — **difiere
exactamente 1 byte**, el dígito de la fecha, en la posición 15 388.

Es la misma clase de error que este proyecto persigue en el material: un control mal
apuntado que informa de un fallo inexistente. Se anota porque el resto del plan va a
escribir muchos controles más.

## Verificación

- `audita_cap2.py`: **445 = 445** comprobaciones, 0 fallos, 2 saltadas.
- `audita_texto_cap2.py`: **128 = 128** comprobaciones, 0 fallos.
- En el navegador: **7/7 mapas con tinta**, incluidos los tres que cambiaron
  (`cap2-error-3116`, `cap2-sesgo`, `cap2-geohash`), 12 módulos recorridos.

## Lo que queda

El capítulo 3 ya usa el formato nuevo (7/7 mapas con `codificacion`), así que **los tres
capítulos escritos salen ahora del mismo árbol de fuentes**. El capítulo 4 no estrenará una
tercera variante.

---
---

# Anexo T0.2 — El error de tipo, y el punto ciego que destapó

**Ejecutada:** 2026-08-05 · **Resultado:** cerrada en verde
**Alcance:** XS en el arreglo, S en las consecuencias

## T0.2.a · El arreglo

`ensambla_cap1.py` formateaba los pasos de solución con
`p['valor'] if isinstance(p['valor'], str) else n(p['valor'])`. Ese `else` metía por el
mismo embudo dos cosas distintas —una medida y un conteo— y el capítulo publicaba:

| Fila | Antes | Ahora |
|---|---|---|
| Muertes cuya bomba más próxima es Broad Street | `359.00000` | `359` |
| Municipios con dato de cobertura | `1121.00000` | `1 121` |
| Departamentos (bloques del remuestreo) | `33.00000` | `33` |
| Estaciones | `361.00000` | `361` |
| Municipios con las dos variables | `1113.00000` | `1 113` |
| Y las demás muertes, cuánto se alejan (factor) | `1.00000` | `1` |

El JSON ya traía la distinción hecha —`jsonlite` escribe `359` para un entero y
`1.611682076` para un doble—, así que la corrección es despachar por tipo. **No se toca la
regla de los cinco decimales**, que está medida: se deja de aplicar a lo que no es una
medida.

**El caso borde, decidido.** El factor del ejercicio 1 vale exactamente 1 —quitar la bomba
de Broad Street no mueve a quien ya tenía otra más cerca— y ahora se publica `1`. Es lo
correcto: no es una medida que redondeó bonito, es una identidad por construcción, y
escribirla sin decimales dice justo eso.

## T0.2.b · El capítulo 2 tenía el mismo defecto

Al buscar si era un caso aislado aparecieron **15 celdas** en el capítulo 2, incluida la más
delatora de todas: `0.00000` **falsos positivos**. El capítulo 3 no lo tiene porque formatea
en R. Arreglado igual, con la variante que además maneja listas.

Queda un `0.00000` en el capítulo 2 y **es correcto**: es la columna *«Máximo
desplazamiento»* de `st_set_crs()`, una medida que vale cero. La columna de conteo de al
lado dice `0` y `57 840`. Que las dos convivan en la misma tabla es justamente la prueba de
que la distinción por tipo funciona.

## T0.2.c · El hallazgo: el arreglo abrió un agujero, y la inyección lo cazó

Con los dos auditores en verde, la tarea parecía cerrada. **No lo estaba.** Al inyectar
defectos en una copia —que es lo único que demuestra que un verde significa algo—:

| Defecto inyectado | Antes de arreglar | Después de arreglar |
|---|---|---|
| `361` → `362` (conteo simple) | detectado | detectado |
| `1 121` → `1 122` (conteo con separador) | detectado | **CIEGO** |
| factor `1` → `2` | detectado | **CIEGO** |

Escribir `1121.00000` protegía la cifra sin querer. Escribir `1 121` la desprotegía.

**Mi primer diagnóstico fue erróneo y conviene dejarlo escrito**: supuse que el espacio
fino de millar (U+202F) rompía la extracción de números. No es eso. El auditor colapsa los
separadores correctamente (`audita_texto_base.py:231`), `\s` sí casa U+202F, y `2309` se
extrae bien. Lo que pasa es que **`2309` está en el índice de cifras conocidas**, absorbido
por las mantisas y las comparaciones derivadas que `_indexa_comparaciones` mete ahí. Es
decir: es el punto ciego que `mide_punto_ciego.py` ya había medido y documentado —4,63 % de
absorción con cinco decimales, ~63 % con un entero pelado—, no un fallo nuevo. El propio
auditor lo avisa en cada corrida: *«14 cifras con menos de 5 decimales en la prosa»*.

## T0.2.d · La salida: no volver atrás, comprobar exacto

Volver a `359.00000` habría cambiado un defecto visible por uno invisible. La salida es
dejar de depender de un índice para algo que se puede comprobar **exacto**.

Familia nueva en `audita_texto_base.py`, llamada por los auditores de los capítulos 1 y 2:

```
a.soluciones("capN_soluciones.json")
```

Lee cada celda de cada tabla de solución, la empareja con su paso, reinterpreta el número
publicado y lo contrasta con el del JSON, uno a uno. Dos decisiones de diseño:

- **Va de ida y vuelta, no re-genera el formato.** Si replicara aquí la regla del
  ensamblador se estaría comprobando a sí misma y daría verde ante cualquier transcripción
  rota.
- **La tolerancia se lee de la celda.** Cuenta los decimales publicados y exige que el valor
  del JSON, redondeado a esos mismos, salga idéntico. Con una tolerancia fija se colaba un
  `1.61169` escrito donde tocaba `1.61168`, por ocho millonésimas. Ese caso está en la
  batería.

**Y una nota sobre por qué el índice no era la única red.** `audita_cap1.py` ya recalcula
esas seis cifras de forma independiente, en Python y desde las fuentes primarias
(`E1: las muertes de Broad St … 359.00000000 359.00000000`, `E2: municipios con cobertura
… 1121.00000000`, `E3: las mismas estaciones … 361.00000000`, `E1: quitar la bomba NO mueve
a las demás … 1.00000000`). Lo que faltaba no era verificar el **valor**, sino su
**transcripción del JSON al HTML**. Eso es lo que cubre la familia nueva.

## T0.2.e · Verificación

**La batería de inyección, después del arreglo:**

| Defecto | Salida | Veredicto |
|---|---|---|
| `1 121` → `1 122` (conteo con separador) | 1 | **lo detecta** |
| `361` → `362` (conteo simple) | 1 | **lo detecta** |
| factor `1` → `2` | 1 | **lo detecta** |
| `1.61168` → `1.61169` (última cifra de una medida) | 1 | **lo detecta** |

Los tres primeros eran ciegos antes de la familia nueva.

**Sobre los archivos reales:**

| Auditor | Antes | Ahora |
|---|---|---|
| `audita_texto_cap1.py` | 140 · 0 fallos | **141** · 0 fallos · 20/20 celdas contrastadas |
| `audita_texto_cap2.py` | 128 · 0 fallos | **129** · 0 fallos · 19/19 celdas contrastadas |
| `audita_cap1.py` | 836 · 0 fallos | 836 · 0 fallos |
| `audita_cap2.py` | 445 · 0 fallos | 445 · 0 fallos |

Enteros con cinco decimales que quedan en las tablas de solución: **0** en el capítulo 1 y
**0** en el 2 (el `0.00000` superviviente es una medida, T0.2.b).

**Y el arnés del propio proyecto, que es lo que valida el cambio al núcleo compartido.**
`prueba_texto.py` inyecta su batería completa sobre los tres capítulos y el fixture:

```
  cap1: 30 de 30   cap2: 24 de 24   cap3: 20 de 20   demo: 36 de 36
  110 defectos inyectados · 110 detectados
```

Ninguna de las 110 comprobaciones que ya existían se perdió al añadir la familia nueva. Es
la condición que hacía falta para tocar `audita_texto_base.py`, que lo comparten tres
capítulos y el fixture.

**Peso, que era el riesgo alto de T0.1.c.** El arreglo *devuelve* bytes en vez de gastarlos:
capítulo 1 **+26 B netos** en la sesión (los +56 de `codificacion` menos los 30 que ahorran
las seis celdas) y capítulo 2 **−39 B** (los +84 de `codificacion` menos los 123 de sus
quince celdas). Los tres capítulos siguen bajo presupuesto: 91,2 %, 87,7 % y 91,5 %.

## T0.2.f · Cambios en disco

| Archivo | Cambio |
|---|---|
| `precalculo/ensambla_cap1.py` | `valor_paso()` nueva; `ejercicio()` la usa |
| `precalculo/ensambla_cap2.py` | ídem, con el caso de las listas |
| `precalculo/audita_texto_base.py` | familia `soluciones()` nueva |
| `precalculo/audita_texto_cap1.py` | la llama |
| `precalculo/audita_texto_cap2.py` | la llama |
| `Htmls_Espacial/capitulo-1-datos-espaciales.html` | 6 celdas |
| `Htmls_Espacial/capitulo-2-crs-georreferenciacion.html` | 15 celdas |

`audita_texto_cap3.py` y `audita_texto_demo.py` **no** llaman a la familia nueva: el
capítulo 3 formatea sus pasos en R y el fixture no tiene tablas de solución. Se dejan
intactos a propósito, para no meter una comprobación sin sujeto.

## T0.2.g · La lección, que vale para las fases 2, 3 y 4

Este plan va a reescribir prosa y a publicar cifras nuevas en casi todas las tareas que
quedan. T0.2 dice cómo hay que hacerlo:

> **Un auditor en verde después de un cambio no prueba nada si no se le inyecta el defecto
> que ese cambio hacía posible.** Los dos auditores dieron verde con el agujero abierto. Lo
> encontró preguntarles por el defecto concreto, no correrlos otra vez.

Se añade como criterio de aceptación a toda tarea de las fases 2 y 3:

> - [ ] Inyectado al menos un defecto del tipo que este cambio hace posible, y el auditor
>       lo detecta. Si no lo detecta, la tarea no está terminada: falta la comprobación.

## T0.2.h · Preguntas abiertas

1. `audita_texto_cap3.py` no tiene esta red. ¿Le doy tablas de solución comprobables
   —cambiando su ensamblador para que formatee en Python como los otros dos— o lo dejo con
   el formateo en R y sin la comprobación?
2. El aviso de *«14 cifras con menos de 5 decimales en la prosa»* sigue ahí, y ahora sé que
   señala cifras realmente poco protegidas **fuera** de las tablas de solución. ¿Las reviso
   una a una en una tarea aparte?

---
---

# Anexo T0.4 — La verificación visual, y lo que encontró en cinco minutos

**Ejecutada:** 2026-08-05 · **Resultado:** capacidad habilitada · **Defectos encontrados: 1 grave, 1 de procedencia**

## T0.4.a · No había que crear nada

La pregunta 2 de T0.1 estaba mal planteada por mi parte: pregunté si montar un
`.claude/launch.json` «que sería un archivo nuevo en tu proyecto». **Ya existía**, del
2026-08-03, con exactamente la configuración que iba a proponer:

```json
{"name": "espacial", "runtimeExecutable": "python3",
 "runtimeArgs": ["-m", "http.server", "8931"], "port": 8931}
```

Lección de método, y es la misma que T0.1: **mirar antes de proponer**. Pregunté por el
coste de una cosa que no tenía coste.

## T0.4b · El diagnóstico de T0.1 también estaba incompleto

En T0.1.f escribí que la verificación visual fallaba porque *«el panel sirve los `file://`
como instantánea estática»*. **No era eso.** Servido por HTTP, `window.innerWidth` seguía
valiendo 0. Lo que faltaba era llamar a `resize_window` con dimensiones **explícitas**: el
preset «desktop» devuelve el tamaño nativo, que en este panel es 0. Con `1280×900` a mano,
todo funciona.

Es decir: la verificación visual **se podría haber hecho desde el principio**, también sobre
`file://`. La atribuí a la fuente equivocada. Queda escrito porque una causa mal atribuida
es peor que un problema sin resolver: cierra la investigación.

## T0.4.c · Lo primero que se ve al mirar de verdad

Con viewport real, **17/17 lienzos con tinta** en los 12 módulos —incluidos los siete de
Chart.js que en T0.1 quedaron sin verificar—. Ese era el objetivo.

Y luego, al probar que un control cambia algo —que es la capacidad que la Fase 1
necesita—, apareció el defecto de `ee-ingenuo`: **el mapa está desplazado en uno para los
cinco botones**, y el quinto se sale del array. El detalle está en la ficha de T1.2.

Lo que importa aquí no es el defecto sino **qué clase de defecto es**:

> Las cifras del JSON son correctas. La prosa es correcta. Los 836 + 141 controles de los
> dos auditores pasan. El desajuste solo existe **en tiempo de ejecución**, entre dos
> índices paralelos, y ninguna herramienta del arnés mira ahí.

`audita_texto_base.geomapas()` comprueba los cortes, el `n` y el peso de un mapa **cuya
fuente sea un literal**. `cap1-campo` registra su fuente como una **función**
(`() => MAPAS_SIM.campos[campoIdx]`), justo el caso que el propio ensamblador documenta
como no auditable. El punto ciego estaba declarado; lo que faltaba era alguien mirando la
pantalla.

## T0.4.d · Lo que esto cambia en el plan

1. **T1.2 deja de ser cosmética.** Era «que el texto y el gráfico digan lo mismo»; ahora
   arregla un error que contradice visualmente la lección del módulo.
2. **P12 nuevo** (mapa de 28×28 frente a simulación de 16×16, sin declarar), a T2.4.
3. **Criterio transversal para la Fase 1**, que sustituye al «consola limpia» de siempre:

> - [ ] Cada control probado **botón a botón / posición a posición** en el navegador,
>       comprobando que lo que se dibuja coincide con lo que dice la lectura. Un simulador
>       con dos índices paralelos es culpable hasta que se demuestre lo contrario.

4. **Sospechosos que quedan por revisar**, porque comparten el patrón de índices paralelos:
   `una-realizacion` (`MAPAS_SIM.realizaciones[realIdx]` contra `D1.realizaciones_vistas`)
   y `snow-mapa` (`snowModo` contra las tres vistas). Se revisan al entrar en T1.3 y T1.4.

## T0.4.e · Cómo se usa, para la próxima sesión

```
preview_start {name: "espacial"}                    → sirve la carpeta en :8931
navigate  http://localhost:8931/Htmls_Espacial/…    → el capítulo
resize_window {width: 1280, height: 900}            → IMPRESCINDIBLE; el preset da 0
```

---
---

# Anexo T0.5 — La marca de tiempo del capítulo 3

**Ejecutada:** 2026-08-05 · **Resultado:** cerrada en verde · **Alcance:** una línea

## Qué era

`genera_soluciones.R:1241` escribía `format(Sys.time(), "%Y-%m-%dT%H:%M:%S")` para
`cap3_soluciones.json`, mientras las líneas 376 y 868 usan `Sys.Date()` para los capítulos
1 y 2. Con los segundos dentro, el capítulo 3 **no podía ser reproducible byte a byte ni
ejecutándolo dos veces el mismo minuto**, y `prueba_reproducible.sh` solo sabe perdonar el
campo `generado` cuando la diferencia es la fecha.

## Por qué ahora y no cuando tocara el capítulo 3

Es la lección de T0.1 y T0.3 aplicada por adelantado: `geo.R` se extendió durante el
capítulo 3 y los capítulos 1 y 2 quedaron a la deriva **sin que nadie lo anotara**, y eso
costó dos tareas. El capítulo 4 va a nacer copiando a su antecesor. Alinear una línea ahora
cuesta cinco minutos; heredarla cuesta otra ronda de arqueología.

## Verificación

- Solo cambia la marca de tiempo: `'2026-08-05T12:44:21'` → `'2026-08-05'`, resto
  **idéntico**, −9 bytes.
- **Dos ejecuciones seguidas dan un archivo idéntico byte a byte.** Es la primera vez que el
  capítulo 3 pasa esa prueba.
- HTML re-ensamblado: **1 bloque, 1 línea** de diff, −9 bytes.
- `audita_cap3.py` **356 = 356** comprobaciones, 0 fallos, 2 saltadas.
  `audita_texto_cap3.py` **130 = 130**, 0 fallos.

## Lo que queda sin alinear, y se dice

El campo vive en la **raíz** de `cap3_soluciones.json` y bajo **`meta`** en los capítulos 1
y 2. Eso no se ha tocado: mover el campo cambiaría la estructura del JSON y obligaría a
tocar el ensamblador y el auditor del capítulo 3, que es más de lo que esta pregunta pedía.
Se anota porque ya me hizo dar un diagnóstico equivocado una vez (Anexo T0.3, «un susto
propio»).

---
---

# Anexo T1.2 — El mapa que contradecía a la lectura

**Ejecutada:** 2026-08-05 · **Resultado:** cerrada en verde · **Opción elegida:** (a), sin tocar R
**Alcance real:** M, como se preveía · **Defectos encontrados de más:** 3

## T1.2.a · El defecto, medido antes de tocar nada

Lo primero fue reproducirlo en el navegador y **anotar el estado real**, no el previsto. La
tabla del plan describía el desplazamiento de uno; lo que hay en pantalla es esto:

| Paso | Botón resaltado | Título del mapa | Lectura φ |
|---|---|---|---|
| **al abrir** | φ = 0.5 | rango = **4** | **2** |
| clic φ = 0.5 | φ = 0.5 | rango = **1** | 0.5 |
| clic φ = 1 | φ = 1 | rango = **2** | 1 |
| clic φ = 2 | φ = 2 | rango = **4** | 2 |
| clic φ = 4 | φ = 4 | rango = **8** | 4 |
| clic φ = 8 | φ = 8 | rango = **8** ← congelado | **4** ← congelado |

## T1.2.b · Tres cosas que el plan no había visto

**1 · El estado inicial enseñaba tres φ a la vez.** `botonera()` resalta siempre el primer
botón (`i === 0`), pero `campoIdx` arrancaba en 3. Resultado: el botón decía φ = 0.5, la
lectura φ = 2 y el mapa φ = 4. **Tres números distintos en la misma pantalla antes de que
nadie tocara nada.** La tabla del plan solo cubría los estados posteriores al clic.

**2 · El quinto botón no «se salía del array»: se congelaba en silencio.** La predicción era
`undefined` y un mapa roto. Lo que pasa es peor: `dibuja()` lanza
`TypeError: Cannot read properties of undefined (reading 'leyenda')` dentro del manejador del
clic, la excepción **aborta el manejador antes de `lee()`**, y el navegador se la traga.
Mapa y lectura se quedan en φ = 4 mientras el botón dice φ = 8. Un estudiante que pulse el
último botón ve **que no pasa nada** y concluye que φ = 8 se parece a φ = 4. Es la forma
más cara de fallar: sin síntoma.

**3 · La etiqueta accesible del mapa ya mentía.** Decía *«el alcance de la correlación se
controla con el deslizador»* cuando lo que había era una botonera. La opción (a) la vuelve
cierta, que es un argumento más a su favor.

## T1.2.c · El arreglo

**El emparejamiento, por φ y no por posición.** `campoIdx` es siempre el índice en
`inferencia.rejilla` —la rejilla de cifras, siete alcances— y el mapa se busca:

```js
GEOMAPAS['cap1-campo'] = { fuente: () => campoDePhi(D1.inferencia.rejilla[campoIdx].phi), … }
```

**Las posiciones del control se derivan, no se escriben.** El deslizador ofrece la
intersección de las dos rejillas, calculada en el navegador: si R exporta un campo más
aparece solo, y si quita uno desaparece solo. Lo que ya no puede pasar es que el control
ofrezca una posición sin campo detrás. *(En la primera ronda eran cinco posiciones, las
que tenían campo; en la segunda —§T1.2.j— pasaron a siete sin tocar una línea de este
código, que es la prueba de que la derivación funciona.)*

**La botonera pasa a deslizador,** con marcador vertical sobre las curvas y punto engordado
en las tres series que dependen de φ. Arranca en φ = 4, que es el caso del que habla la
prosa justo debajo — y que además es el mapa que ya se veía al abrir, así que el estado
visual inicial no cambia: solo dejan de contradecirlo los números.

**Dos decisiones de implementación que conviene dejar escritas:**

- **No se usa `crearControles`,** la fábrica del motor que el plan proponía cablear. Aquella
  mapea un parámetro numérico *continuo* y escribe el valor crudo del control en su
  `<output>`; aquí el valor es una posición —0, 1, 2…— y lo que hay que enseñar es el φ, que
  ni es el mismo número ni va a saltos regulares (0.5, 1, 2, 4, 8). Pasar por la fábrica
  obligaba a repintar a mano el `<output>` que la fábrica acababa de escribir. Se escribió
  un `deslizador()` local, hermano de `botonera()`, que **sí reutiliza el CSS**
  `.control-slider` de la plantilla. **La plantilla no se ha tocado**, así que los capítulos
  2 y 3 no necesitan re-ensamblarse.
- **El marcador vertical es un plugin de Chart.js de quince líneas,** registrado en el
  propio capítulo. Chart.js 4.4.1 no dibuja una recta vertical sobre un eje de categorías
  sin el plugin de anotaciones, que no está en el CDN; traerlo por dos rayas no compensa. El
  plugin es inerte mientras nadie ponga `$marcadorX`: comprobado módulo a módulo, está
  activo en **1 de los 8 gráficos** del capítulo.

**La prosa.** «Mueve el alcance y mira las dos curvas» prometía un movimiento que no ocurre.
Ahora dice que las curvas **no** se mueven y por qué —el alcance ya es el eje horizontal—, y
manda mirar dónde la cobertura se despega del 95 % prometido. Ninguna cifra nueva: el «95»
ya estaba en `ESTRUCTURALES`.

## T1.2.d · El hallazgo: mi primera guarda dio verde con el defecto dentro

Escribí una comprobación en tiempo de ejecución para que este defecto dejara de ser
invisible, y **la probé reinyectando el defecto original. Salió verde.** Cero errores en las
cinco posiciones.

Estaba escrita así:

```js
const campo = campoDePhi(f.phi);              // ← busca otra vez, por su cuenta
if (!campo || Math.abs(campo.rho_vecino - f.rho_vecino) > 1e-6) console.error(…)
```

Comprobaba que **existe** un campo con ese φ, que es cierto siempre. Nunca miraba **el que
el mapa dibuja**. Es exactamente el fallo que T0.2.g describe —*una comprobación que no
puede ponerse roja no comprueba nada*— cometido mientras escribía la comprobación que iba a
evitarlo. La corrección es de una línea, y toda la diferencia está en de dónde sale el dato:

```js
const campo = GEOMAPAS['cap1-campo'].fuente();   // ← la MISMA fuente que invoca el motor
```

Ahora `rho_vecino` del campo dibujado y `rho_vecino` de la fila leída son dos cifras que R
calcula por separado, y solo coinciden si el cableado empareja bien.

**La lección, y vale para todo lo que queda:** el arnés de inyección no es un trámite de
cierre. Aquí encontró un defecto **en la propia red de seguridad**, y lo encontró en el
único momento en que era barato arreglarlo.

## T1.2.e · Las dos guardas, probadas por inyección

**En tiempo de ejecución** (`ensambla_cap1.py`, la función `cuadra()`) — se reinyectaron los
cableados rotos y se recorrieron todas las posiciones. La tabla es la de la segunda ronda,
ya con siete; la de cinco está comentada en §T1.2.j porque su lectura cambió:

| Cableado | Avisadas | Excepciones | Lecturas congeladas |
|---|---|---|---|
| **por φ (el actual)** | **0 de 7** | 0 | 0 |
| por posición, con las dos rejillas alineadas | 0 de 7 | 0 | 0 |
| **por posición + R deja de exportar el campo de φ = 2** | **4 de 7** | 0 | 0 |
| por φ, con el campo de φ = 2 ausente | 1 de 7 | 0 | 0 |
| por φ, pero del alcance siguiente | 6 de 7 | 0 | 0 |
| siempre el primer campo (control congelado) | 6 de 7 | 0 | 0 |

El mensaje nombra las dos cifras: *«la fila dice phi = 2 y el campo phi = 4»*. Las dos
columnas de la derecha son de la segunda ronda y valen tanto como la primera: **cero
excepciones y cero lecturas congeladas en todos los casos**, incluidos aquellos en que el
campo directamente no existe. Antes, ese caso lanzaba dentro del motor y se llevaba por
delante el resto del manejador — que es exactamente como se congelaba el quinto botón.
Por eso `cuadra()` se llama **antes** de repintar y el repintado se salta si no cuadra.

**En tiempo de compilación** (`ensambla_cap1.py`, guardas de salida). Empareja las dos
rejillas por φ y contrasta la `rho_vecino` que cada una trae por su cuenta:

| JSON inyectado | Salida | Veredicto |
|---|---|---|
| un campo con φ = 3, que no está en la rejilla de cifras | 1 | **lo caza** |
| el campo de φ = 4 con la `rho_vecino` del de φ = 8 | 1 | **lo caza** |
| +1e-5 sobre una `rho_vecino` | 1 | **lo caza** |
| +1e-9 — el redondeo legítimo del JSON de mapas | **0** | **no salta**: la tolerancia está calibrada |

La tolerancia es 1e-6 y no es arbitraria: `cap1_mapas.json` redondea `rho_vecino` a ocho
decimales y `cap1_datos.json` trae diez, así que la diferencia legítima ronda 3e-9; entre
dos alcances vecinos hay 0.10 largo. `cap1_mapas.json` se restauró idéntico byte a byte
(sha256 `2633e49b4e4b7fae`, 104 859 B).

## T1.2.f · Verificación

**Posición a posición**, que es el criterio transversal de la Fase 1 (T0.4.d). Estado final,
con las siete:

| Pos. | `<output>` | Título del mapa | Lectura φ | ρ vecino | Cobertura | De 256 informan | Marcador |
|---|---|---|---|---|---|---|---|
| 0 | phi = 0 | rango = 0 | 0 | 0.00000 | **0.95300** | **256.00000** | φ = 0 |
| 1 | phi = 0.5 | rango = 0.5 | 0.5 | 0.13534 | 0.84733 | 135.25346 | φ = 0.5 |
| 2 | phi = 1 | rango = 1 | 1 | 0.36788 | 0.58700 | 45.75118 | φ = 1 |
| 3 | phi = 2 | rango = 2 | 2 | 0.60653 | 0.33500 | 14.16323 | φ = 2 |
| 4 | phi = 4 | rango = 4 | 4 | 0.77880 | 0.19700 | 5.15817 | φ = 4 |
| 5 | phi = 8 | rango = 8 | 8 | 0.88250 | 0.12233 | 2.51771 | φ = 8 |
| 6 | phi = 16 | rango = 16 | 16 | 0.93941 | 0.07533 | 1.63282 | φ = 16 |

Siete de siete, y el punto engordado cae en el índice correcto en las tres series. Las siete
ρ son las de \\(e^{-1/\phi}\\) con h en pasos de retícula. Abre en φ = 4.

**Que además se dibuje, y se dibuje distinto.** Huella de píxeles del lienzo del mapa en cada
posición: **7 huellas distintas de 7**, con 667 489 px de tinta en todas. Y a ojo se ve lo
que el módulo enseña, ahora de extremo a extremo: **φ = 0 es ruido puro** —el punto de
partida literal, porque R usa el mismo ruido blanco para los siete alcances— y **φ = 16 es
una sola mancha**. Con el cableado viejo, pulsar «φ = 0.5» enseñaba el campo de φ = 1,
**visiblemente más liso de lo que la etiqueta prometía**.

**Teclado.** `<label for>` asociado al control, foco por tabulador, flechas en los dos
sentidos, y `aria-valuetext` que anuncia *«alcance de la correlación: phi = 2»* en vez del
«3 de 5» que diría un deslizador desnudo. Se detiene en los dos extremos sin salirse.

**Los doce módulos, con la consola abierta.** 0 errores y 0 excepciones. **17/17 lienzos con
tinta** (16 al cargar + el del gráfico de la autoevaluación del módulo 12, que Chart.js
dibuja un tick más tarde), todos con `aria-label`. El plugin del marcador activo en 1 de los
8 gráficos.

**Los auditores:**

| Auditor | Antes de T1.2 | Ahora |
|---|---|---|
| `audita_cap1.py` | 836 · 0 fallos · 3 saltadas | **848 · 0 · 3** |
| `audita_texto_cap1.py` | 141 · 0 fallos | **141 · 0** |

Las **12 comprobaciones nuevas** son las de los dos campos que estrena la segunda ronda:
seis cada uno —modo, celdas declaradas, rango de la cuantización, rango no degenerado,
ρ vecino y que I sea un I—. Más dato, más controles, que es la dirección correcta.
Y `el I de los campos crece con el rango` sigue en OK con los siete:
−0.0067 < 0.0818 < 0.2739 < 0.5067 < 0.6969 < 0.8083 < 0.8538.

**El arnés COMPLETO, no el rápido**, porque la segunda ronda tocó `audita_cap1.py` y un
auditor cambiado sin su arnés de inyección no vale nada: **ARNÉS COMPLETO EN VERDE**, salida
0, **los 13 pasos en OK**.

| Auditor | Comprobaciones | Fallos | Su arnés de inyección |
|---|---:|---:|---|
| `audita_cap1.py` | **848** *(836 + los dos campos)* | 0 | **49 de 49 cazados** |
| `audita_cap2.py` | 445 | 0 | 91 de 91 |
| `audita_cap3.py` | 356 | 0 | 56 de 56 |
| `audita_texto_demo.py` | 77 | 0 | — |
| `audita_texto_cap1.py` | 141 | 0 | *(prueba_texto)* |
| `audita_texto_cap2.py` | 129 | 0 | *(prueba_texto)* |
| `audita_texto_cap3.py` | 130 | 0 | *(prueba_texto)* |
| **Total** | **2 126** | **0** | |

Y `prueba_texto.py`, que es el que este cambio podía romper porque reescribe un párrafo:
**110 defectos inyectados, 110 detectados** (cap1 30/30, cap2 24/24, cap3 20/20, fixture
36/36). Ninguna comprobación se perdió. Cero regresiones en los capítulos 2 y 3.

*(El arnés completo se pasó antes de un último endurecimiento de dos líneas —el arranque del
deslizador, §T1.2.j—; después se repitieron los tres pasos que ese cambio podía tocar:
`audita_cap1.py` 848·0, `audita_texto_cap1.py` 141·0 y `prueba_texto.py` 110/110.)*

**Peso**, que es el riesgo alto de T0.1.c: 511 → **524,3 KB (94 %)**, +14 065 B en total.
Margen restante **35,7 KB**. El desglose importa porque no todo se gastó igual:

| Concepto | Bytes |
|---|---:|
| el cableado, el deslizador y el marcador (1.ª ronda, ya recortada) | +6 821 |
| **los dos campos de φ = 0 y φ = 16** (`MAPAS_SIM`: 34 138 → 42 652 B) | **+8 514** |
| recorte de los comentarios del JS a titular | −1 865 |
| `cuadra()` antes del repintado, y el arranque que no puede discrepar | +595 |
| **total** | **+14 065** |

**Es el primer cambio de este plan que gasta presupuesto de verdad.** A partir de aquí la
historia larga vive en este anexo y en el código va solo el titular con un puntero — regla
de esta ronda, aplicada ya retroactivamente a todo lo que T1.2 escribió.

## T1.2.g · Cambios en disco

| Archivo | Cambio |
|---|---|
| `precalculo/ensambla_cap1.py` | `campoDePhi()`, `deslizador()`, el plugin `marcadorX`, el simulador reescrito con `cuadra()`, la prosa del módulo 4 y la guarda de salida nueva |
| `precalculo/genera_cap1.R` | `PHIS_VER` pasa de 5 a 7 alcances, con φ = 0 despachado como caso límite |
| `precalculo/audita_cap1.py` | φ = 0 en la comprobación de ρ vecino: `math.exp(-1/0)` no da 0, lanza `ZeroDivisionError` |
| `precalculo/salidas/cap1_mapas.json` | +8 510 B: dos campos nuevos. **Todo lo demás, byte a byte idéntico**, verificado clave a clave — incluidos los cinco campos que ya estaban |
| `Htmls_Espacial/capitulo-1-datos-espaciales.html` | +14 065 B · 8 506 → 8 624 líneas |

`cap1_datos.json` y `cap1_soluciones.json` **no cambiaron** (sha256 `5215b28207…` y
`e539cf603c…`, iguales antes y después de re-ejecutar R). **La plantilla tampoco se tocó**,
así que los capítulos 2 y 3 no se re-ensamblaron.

## T1.2.h · Los otros dos sospechosos de T0.4.d, descartados

T0.4.d dejó anotados dos simuladores por compartir el patrón de índices paralelos. Se
revisaron aprovechando el navegador abierto:

- **`una-realizacion`** (`MAPAS_SIM.realizaciones` contra `D1.realizaciones_vistas`): las dos
  listas tienen **3 entradas y el mismo orden**. Botón «Realización 2» → mapa «Realización 2»
  → lectura «2» con media −0.00065, que es la del JSON. **No está roto.** Sigue acoplado por
  posición, eso sí: la fragilidad está, el síntoma no. T1.3 va a tocar ese simulador de todos
  modos y puede desacoplarlo de paso, gratis.
- **`snow-mapa`**: no hace aritmética de índices —`snowModo` es una cadena que leen tres
  captadores—, así que no puede descuadrarse por construcción. Los tres botones dan **3
  huellas de píxeles distintas** y la lectura cambia con cada uno; «Sin las calles» baja la
  tinta de 93 450 a 35 739 px, que es justo el fondo de calles desapareciendo. **No está roto.**

Es decir: de los tres sospechosos, **solo `ee-ingenuo` lo era**. Lo que T1.3 y T1.4 tienen
delante es añadir controles que faltan, no reparar cableados torcidos.

## T1.2.j · Segunda ronda: los siete alcances, y lo que eso le hizo a la guarda

Las dos preguntas de la primera ronda se resolvieron **las dos que sí**: se generan los
campos de φ = 0 y φ = 16, y a partir de aquí el código lleva titular y el anexo lleva la
historia.

**φ = 0 no es un valor más, es el caso límite.** ρ(h) = e^(−h/φ) no está definida ahí:
`exp(-D/0)` da `NaN` en la diagonal. El límite es R = I, y como `genera_cap1.R` usa **el
mismo ruido blanco para los siete alcances** —decisión previa, para que entre un mapa y el
siguiente solo cambie la correlación—, el campo de φ = 0 **es literalmente el punto de
partida de los otros seis**. Es la mejor imagen que podía tener el módulo y salía gratis.
Se despacha aparte en R, y `audita_cap1.py` necesitó el mismo cuidado: `math.exp(-1/0)` no
devuelve 0, lanza `ZeroDivisionError`.

**El efecto secundario que hay que decir en voz alta.** Con las dos rejillas ya del mismo
tamaño y el mismo orden, **el defecto original ya no puede manifestarse**: indexar por
posición sobre `campos` acierta hoy por hoy. La reinyección lo confirma —caso «por posición
con las rejillas alineadas»: **0 de 7 avisadas**—. Eso no vuelve inútil el emparejamiento
por φ; lo vuelve **cinturón además de tirantes**, y quien lo demuestra es el caso siguiente:
si mañana R deja de exportar un campo por peso, la versión por posición se descuadra en
silencio otra vez y la guarda avisa **4 de 7 veces**, mientras la versión por φ sigue
dibujando bien. La alineación de hoy es una propiedad **de los datos**; el emparejamiento
por φ es una propiedad **del código**, y solo la segunda sobrevive al próximo cambio.

**Y dos agujeros de la primera ronda, cerrados.**

El primero lo destapó la reinyección de «falta el campo de φ = 2»: la guarda hablaba
*después* de repintar, así que `dibuja()` lanzaba dentro del motor y se llevaba por delante
`lee()` — el aviso no llegaba a la consola y la lectura se quedaba congelada, **la misma
forma de fallar que el quinto botón original**. La guarda —ahora `cuadra()`— se llama antes
del repintado, y el repintado se salta si no cuadra. Resultado: **cero excepciones y cero
lecturas congeladas en los seis cableados probados**, incluidos los dos en que el campo
directamente no existe.

El segundo apareció releyendo el código, no ejecutándolo: el deslizador arrancaba en
`conCampo.findIndex(p => p[0] === campoIdx)`, y si ese alcance no tuviera campo, `findIndex`
devuelve **−1**, el `<input type=range>` lo redondea a 0 sin quejarse, y volveríamos a tener
el control diciendo una cosa y el estado otra — el defecto de esta tarea, reinventado en su
propio arreglo. Ahora el control manda: la posición se acota y `campoIdx` se toma **de
ella**, no al revés.

## T1.2.i · Preguntas abiertas que deja

Ninguna. Las dos de la primera ronda se cerraron en §T1.2.j. ~~Queda anotado, para quien
mire el presupuesto: el capítulo va al **94 %** del tope duro con **35,7 KB** de margen, y
las fases 2 a 4 aún no han empezado a gastar.~~

> **Anotación de T1.1:** ese párrafo era la última vez que este plan se preocupó por el peso.
> El tope se retiró como criterio de aceptación el 2026-08-06 y el margen pasó a 169,9 KB.
> Anexo T1.1.g.

---
---

# Anexo T1.1 — El deslizador de ρ, y las dos cosas que el criterio daba por ciertas

**Ejecutada:** 2026-08-06 · **Resultado:** cerrada en verde · **Alcance real:** M, como se preveía
**Hallazgos que cambian el plan:** 2 · **Defectos de más encontrados:** 2

## T1.1.a · Lo que había, medido antes de tocar nada

Primero reproducir y anotar el estado real, que es el método que T1.2 dejó establecido. El
módulo 5 estaba así:

| Qué | Estado |
|---|---|
| `.simulador-controles` | **0 hijos.** Vacío, como decía el inventario |
| Eje x del gráfico | **ρ**, con las nueve posiciones de la rejilla como categorías |
| Series | `n = 50`, `n = 250`, `n = 1 000` y el techo `1/ρ` |
| Lectura | 5 filas **fijas**, idénticas en cada carga |
| Huella de píxeles | 57 983 px de tinta, **una sola**: sin controles no hay nada que cambie |

**Y un defecto que el inventario no tenía.** La prosa prometía «cuánto aporta pasar de **25**
a 1 000 observaciones» y **la serie de 25 no existía**: el código dibuja
`ne.rejilla.filter((_, i) => i % 2 === 1)`, que son los índices 1, 3 y 5 — o sea 50, 250 y
1 000. La promesa fallaba dos veces: no había control que mover y tampoco estaba el extremo
del que hablaba.

## T1.1.b · Hallazgo 1: el ρ del criterio de aceptación no existe

El tercer criterio pedía marcar «el punto de Colombia (**ρ estimado** → 64.52155)». Al buscar
ese ρ para poder situar el punto, no aparece. Y no está escondido: **no está.**

`genera_cap1.R:556` calcula la cifra así:

```r
n_eff = r10(n_muni * (ee_iid / ee_blq)^2)
```

Es el **cociente entre los dos remuestreos** del módulo 4 —bootstrap i.i.d. contra bootstrap
por departamentos— leído al revés. No interviene ninguna correlación: es una razón de
varianzas. Recorrido `cap1_datos.json` clave a clave, los únicos ρ que hay son
`inferencia.rejilla[].rho_vecino` (del campo **simulado**) y `n_efectivo.rhos` (la rejilla
**teórica** del simulador). Para los 1 121 municipios no hay ninguno.

**Y el 0.03146 que P1 citaba es de otro conjunto de datos.** El plan decía que «asoma en la
solución del ejercicio 3». Asoma, sí, pero ahí es la correlación media entre pares de las
**361 estaciones del IDEAM**, y su n_eff es **29.29233**, publicado en la misma solución. Con
n = 361 y ρ = 0.03146 no sale 64.52155 por ninguna cuenta, y con n = 1 121 tampoco: daría
30.94.

El ρ que la equicorrelación necesitaría para reproducir el titular es
`(n/n_eff − 1)/(n−1)` = **0.01462**, menos de la mitad del que P1 le atribuía.

**Lo que esto cambia.** El plan había previsto la posibilidad —T2.1 decía *«si no lo es, es un
hallazgo y se declara»*— así que aquí está, dos fases antes de lo esperado. T2.1 deja de ser
«publicar el ρ» y pasa a ser **elegir cuál**, con las dos opciones escritas en su ficha.

**Cómo se cerró el criterio, y por qué así.** Consultado y decidido: se marca el punto con las
**dos cifras que ya están publicadas** —`desercion_n` = 1 121 y `desercion_municipal` =
64.52155— sin estrenar ninguna. El rombo no cae sobre ninguna curva, y eso pasa a ser lo que
el módulo enseña: la prosa declara que ese 64.52155 **no sale de un ρ estimado** y manda
buscar el ρ cuya curva pase por él. El defecto de procedencia queda **a la vista** en vez de
tapado con un número inventado para la ocasión, y T2.1 lo hereda mejor planteado.

La alternativa —publicar 0.01462 desde R— se descartó por dos razones: mete a la Fase 1 a
tocar R, que no le toca, y si T2.1 acaba estimando el ρ municipal por bandas saldrá **otro**
número y el capítulo tendría dos ρ compitiendo.

## T1.1.c · El arreglo: transponer, no añadir un control

Con ρ en el eje x, un deslizador de ρ **no puede redibujar nada**: es el mismo caso que T1.2
descubrió en `ee-ingenuo`, donde φ ya era el eje. Y el criterio pedía además que el techo
`1/ρ` fuera «línea de referencia móvil», que solo tiene sentido si ρ es un parámetro. Así que
el gráfico se transpone:

| | Antes | Ahora |
|---|---|---|
| Eje x | ρ, nueve categorías | **n**, logarítmico de 20 a 1 346 |
| Series | tres n fijos + techo | **la curva del ρ elegido**, el techo `1/ρ`, la diagonal sin correlación y el rombo de Colombia |
| Techo | una curva más | **una recta horizontal que se mueve** con el deslizador |
| Lectura | 5 filas fijas | 7 filas en vivo |

**Los dos extremos del eje se derivan, no se escriben:**
`XMAX = ceil(max(enes[último], desercion_n) × 1.2)`. Si mañana cambia el número de municipios
o la rejilla de n, el rombo **no puede salirse del lienzo en silencio** — que es la clase de
defecto que T1.2 persiguió. Por eso la guarda de ejecución no comprueba que el punto esté
dentro del rango: con la derivación no puede no estarlo, y una comprobación que no puede
fallar no comprueba nada.

**Sí se usa `crearControles`,** la fábrica de la plantilla que el plan proponía cablear y que
T1.2 acabó descartando. La razón de aquel descarte no se aplica aquí y conviene dejarlo
escrito: en `ee-ingenuo` el valor del control era una **posición** (0, 1, 2…) y lo que había
que enseñar era el φ, así que pasar por la fábrica obligaba a repintar a mano el `<output>`
que la fábrica acababa de escribir. Aquí el valor del control **es ρ**, que es exactamente lo
que hay que leer. La fábrica encaja sin pelearse, y por lo mismo **no hace falta
`aria-valuetext`**: un lector de pantalla que anuncia «correlación rho, 0.01» ya dice la
magnitud, no una posición. **La plantilla no se ha tocado** —solo una línea que estira el
control a las dos columnas de la rejilla—, así que los capítulos 2 y 3 no se re-ensamblaron.

**Dos detalles de presentación que resultaron ser de contenido.** Los ticks del eje x son
**los `enes` de R**, no los que elija Chart.js: el estudiante ve la rejilla publicada y no una
escala paralela. Y se formatean con el espacio fino de la casa, porque el formato por omisión
de Chart.js escribe **`1,000`**, que en español se lee como uno — en un gráfico cuyo eje es
justamente el tamaño de muestra.

**La etiqueta accesible del lienzo mentía, igual que en T1.2.** Decía «para varios valores de
la correlación», que era cierto del gráfico viejo. Reescrita.

## T1.1.d · Hallazgo 2: el defecto que el arnés entero no veía

La guarda de compilación comprueba que las anclas que la prosa nombra sigan en el índice que
el texto da por sabido. Suena a paranoia hasta que se inyecta: **RHOS reordenado**, de forma
consistente —rejilla incluida, como saldría de R si alguien cambiara el vector—, de modo que
`rhos[1]` pase a ser 0.02 en vez de 0.01.

| Herramienta | Con el defecto dentro |
|---|---|
| `ensambla_cap1.py` sin la guarda nueva | salida **0**, ningún MAL |
| `audita_cap1.py` | **848 comprobaciones · 0 fallos · salida 0** |
| `audita_texto_cap1.py` | **141 comprobaciones · 0 fallos · salida 0** |

**Verde de punta a punta.** Y lo que el capítulo publicaría, extraído del HTML defectuoso:

```
Con \(n = 1\,000\) y \(\rho = 0.02\) el tamaño efectivo es …
```

dos párrafos por debajo de una frase que sigue diciendo, escrita a mano en la plantilla:

```
Con \(\rho = 0{,}01\) … ese techo son 100 observaciones
```

Los dos auditores están en verde porque **cada cifra por separado sale del JSON**: el 0.02
existe, el 47.66444 que le corresponde existe. Lo que no existe es la coherencia entre el
párrafo interpolado y el párrafo escrito a mano, y ahí no mira nadie. El deslizador arrancaría
en 0.02 mientras el texto de encima habla de 0.01.

Es la misma familia que T0.2.g: *un auditor en verde después de un cambio no prueba nada si no
se le inyecta el defecto que ese cambio hacía posible.*

## T1.1.e · Las dos guardas, probadas por inyección

**En tiempo de compilación** (`ensambla_cap1.py`, guardas de salida). Seis inyecciones, seis
cazadas:

| Defecto inyectado | Salida | Veredicto |
|---|---|---|
| RHOS reordenado: `rhos[1]` deja de ser 0.01 | 1 | **lo caza** *(ciego antes, §T1.1.d)* |
| `RHO_MAX = 0.35`, que no está en la rejilla | 1 | **lo caza** |
| `RHO_MAX = 0.05`: no alcanza el ancla de 0.1 | 1 | **lo caza** |
| desaparece `RHO_MAX` del JS | 1 | **lo caza** |
| Colombia por encima de la diagonal (`n_eff > n`) | 1 | **lo caza** |
| `enes` y `rejilla` desalineados | 1 | **lo caza** |

La guarda **lee el valor de `RHO_MAX` del propio JS** con una expresión regular, en vez de
repetir el número en Python. Así no hay dos literales que puedan separarse: si el tope del
deslizador deja de ser un ρ de la rejilla, el extremo del control sería una cifra sin auditar
y el ensamblador para.

**En tiempo de ejecución** (`cuadra()`). El navegador **evalúa** `n/(1+(n−1)ρ)` —D9 lo
autoriza por escrito— así que la rejilla 6×9 de R pasa a ser la referencia contra la que ese
cómputo se contrasta. Ocho variantes servidas por HTTP y recorridas en sus 7 posiciones de
rejilla:

| Cableado inyectado | Avisadas | Excepciones | Lecturas congeladas |
|---|---|---|---|
| **sin inyectar (control)** | **0 de 7** | 0 | 0 |
| la fórmula mal escrita: `n/(1+n·ρ)` | **6 de 7** | 0 | 0 |
| la curva dibujada con ρ + un paso del control | **7 de 7** | 0 | 0 |
| el rombo cableado a `desercion_pct` en vez de `desercion_municipal` | **7 de 7** | 0 | 0 |
| el rombo escrito a mano y redondeado: `(1121, 64.52)` | **7 de 7** | 0 | 0 |
| el eje pierde los `enes` de R: la curva ya no pasa por las anclas | **7 de 7** | 0 | 0 |
| la rejilla de R desviada **1e-10** (el redondeo legítimo) | **0 de 7** | 0 | 0 |
| la rejilla de R desviada **1e-8** | **7 de 7** | 0 | 0 |

Tres cosas que merecen comentario:

- **El caso de la fórmula avisa 6 de 7 y está bien así.** En ρ = 0 las dos fórmulas coinciden
  —`n/(1+0)` da n de cualquier manera—, así que ahí no hay nada que cazar. Es matemática, no
  un hueco.
- **El rombo a mano es el caso más afilado.** `64.52` en vez de `64.5215456118`: exactamente la
  violación de D10 que este proyecto persigue, y el mensaje la nombra —*«el rombo dibuja
  (1121, 64.52) y el JSON dice (1121, 64.5215456118)»*—.
- **La tolerancia está calibrada, no elegida.** 1e-10 no salta y 1e-8 sí; la guarda usa 1e-9.
  R escribe con diez decimales, así que la diferencia legítima no pasa de 5e-11 —veinte veces
  por debajo del umbral— y entre dos celdas vecinas de la rejilla hay unidades enteras.

**Y la lección de T1.2.d, aplicada por adelantado.** `cuadra()` lee
`g.data.datasets[0].data` —lo que el gráfico tiene dentro— y no una segunda evaluación propia
de la fórmula. Si recalculara por su cuenta comprobaría que su aritmética coincide consigo
misma, que es lo que le pasó a la primera guarda de T1.2: dio verde con el defecto dentro. Los
casos de «la fórmula mal escrita» y «la curva con ρ corrido» son precisamente los que una
guarda tautológica no vería.

**Un detalle de orden, al revés que en T1.2.** Allí `cuadra()` se llamaba **antes** de
repintar, porque con el campo ausente `dibuja()` lanzaba dentro del motor y se llevaba por
delante el resto del manejador. Aquí va **después** de `pinta()`, porque lo que comprueba es
lo ya dibujado y nada puede lanzar: las ocho variantes dan **cero excepciones y cero lecturas
congeladas**, incluida la que deja la curva con `undefined` en las anclas.

**Ninguna de las siete inyecciones de ejecución la caza el ensamblador** (las ocho salieron
con salida 0). Es lo esperado y es el argumento de la guarda: viven solo en tiempo de
ejecución, que es el punto ciego que T0.4.c declaró.

## T1.1.f · Verificación

**Posición a posición**, que es el criterio transversal de la Fase 1. Las **301** posiciones
del deslizador, comprobando en cada una cinco cosas: que el `<output>` del control y la fila
«rho» de la lectura digan lo mismo; que el techo **dibujado** valga 1/ρ (o no exista en ρ = 0);
que la lectura del techo coincida con lo dibujado; que la **curva** en n = 25 y n = 1 000
coincida con lo que dice la lectura; y que el rombo no se mueva.

> **301 posiciones recorridas · 301 correctas · 0 avisos de consola.**

Y el detalle en los **7 ρ de la rejilla**, que son los que R audita:

| ρ | `<output>` | techo 1/ρ | n = 25 | n = 1 000 | curva | lo que aporta |
|---|---|---|---|---|---|---|
| 0 | 0.000 | *sin correlación no hay techo* | 25.00000 =JSON | 1000.00000 =JSON | = lectura | 975.00000 |
| 0.01 | 0.010 | 100.00000 | 20.16129 =JSON | **90.99181** =JSON | = lectura | 70.83052 |
| 0.02 | 0.020 | 50.00000 | 16.89189 =JSON | 47.66444 =JSON | = lectura | 30.77255 |
| 0.05 | 0.050 | 20.00000 | 11.36364 =JSON | 19.62709 =JSON | = lectura | 8.26345 |
| 0.10 | 0.100 | 10.00000 | 7.35294 =JSON | **9.91080** =JSON | = lectura | 2.55786 |
| 0.20 | 0.200 | 5.00000 | 4.31034 =JSON | 4.98008 =JSON | = lectura | 0.66973 |
| 0.30 | 0.300 | 3.33333 | 3.04878 =JSON | 3.32557 =JSON | = lectura | 0.27679 |

Los dos anclajes del criterio, **90.99181** y **9.91080**, salen idénticos al JSON — y no por
casualidad: el navegador los calcula y `cuadra()` los contrasta. El techo en ρ = 0.01 da
**100.00000**, que es la cifra que la frase escrita a mano del bloque de definición promete
dos párrafos arriba.

**La última columna es lo que el módulo enseña, ahora medible.** Con ρ = 0.10, pasar de 25 a
1 000 observaciones —**cuarenta veces más datos**— aporta **2.55786** observaciones efectivas.
Eso antes había que creérselo; ahora se lee moviendo un control.

**Que además se dibuje, y se dibuje distinto.** Huella de píxeles del lienzo en cada ρ de la
rejilla: **7 huellas distintas de 7**, con entre 41 794 y 51 694 px de tinta. Y a ojo se ve el
argumento: en ρ = 0.01 la curva naranja se despega de la diagonal gris y se aplasta contra el
techo de 100; en ρ = 0.10 es **una recta plana en 10** mientras la diagonal sube hasta 1 000.
El rombo de Colombia queda **por debajo** de la curva en ρ = 0.01 y **por encima** en ρ = 0.10,
así que el estudiante acota su correlación equivalente entre las dos sin que nadie se la diga.

**Teclado.** `<label for>` asociado al control, foco por tabulador, flechas en los dos
sentidos, y los dos topes se sostienen sin salirse (0 y 0.3). El nombre accesible es
«correlación rho» y el valor anunciado es ρ, no una posición — por eso no lleva
`aria-valuetext`, §T1.1.c.

**Los doce módulos, con la consola abierta.** **0 errores y 0 excepciones.** **17/17 lienzos
con tinta**, todos con `aria-label` (16 al cargar y el de la autoevaluación del módulo 12 un
tick más tarde, como en T1.2). `.simulador-controles` vacíos: **2**, y los dos son de T1.4
—`snow-serie` en el módulo 1 y `correlograma` en el 3—. El del módulo 5 ya no está.

**Los auditores:**

| Auditor | Antes de T1.1 | Ahora |
|---|---|---|
| `audita_cap1.py` | 848 · 0 fallos · 3 saltadas | **848 · 0 · 3** |
| `audita_texto_cap1.py` | 141 · 0 fallos | **141 · 0** |

Las cuentas no se mueven porque T1.1 **no estrena ni un dato**: todo lo que dibuja sale de
cifras que ya estaban auditadas. El arnés de los tres capítulos, `audita_todo.sh --rapido`, en
**4 min 16 s**: salida 0, 9 pasos OK, **2 126 comprobaciones · 0 fallos**, las mismas siete
cuentas que tras T1.2 (848, 445, 356, 77, 141, 129, 130). **Cero regresiones en los capítulos 2
y 3.**

`prueba_texto.py`, que es el que este cambio podía romper porque reescribe un párrafo:
**110 defectos inyectados · 110 detectados** (cap1 30/30, cap2 24/24, cap3 20/20, fixture
36/36).

**Sobre el arnés completo con inyección.** No se pasó, y se dice por qué: T1.1 **no toca ningún
auditor de precálculo**, que es lo que obligó a T1.2 a pasarlo. Sí se pasó `prueba_texto.py`,
que es el arnés del auditor que este cambio podía romper, y las catorce inyecciones propias de
la tarea. Queda para el cierre de la Fase 1.

## T1.1.g · Hallazgo 3, y el que más va a cambiar lo que queda: el peso era el riesgo equivocado

T1.1 gastó **+5 963 B** y dejó el capítulo en 530,1 KB — el **94,7 %** del tope de 560, con
29,9 KB de margen. Siguiendo el guion del plan, empecé a recortar los comentarios del
simulador para devolver 1,3 KB.

**Ahí estaba el error, y no era mío solo: era del plan.** Un número arbitrario había llegado a
decidir cuánto se explica en el código. Consultado con Javier, la respuesta fue directa:
*«ayúdame a eliminar el problema del peso, lo importante son los contenidos»*.

**Qué era ese tope, mirado de cerca.** Cinco llamadas con cuatro números distintos: 550 para el
fixture, **560** para el capítulo 1, **560** para el 2, **680** para el 3. No es un presupuesto
diseñado: es una **marca de agua que se fue levantando cada vez que un capítulo chocaba con
ella**. Y no defendía nada real — un capítulo es un HTML autocontenido que se descarga una
vez, y los tres CDN que carga pesan más que él.

**Lo que sí hacía, y por eso no se retiró la comprobación.** En T0.5 el ensamblador escribió un
archivo más grande que la plantilla, con el motor mutilado, e informó «limpio». La
comprobación es la alarma contra eso. Así que cambia **lo que es**, no si existe: de
presupuesto de contenido a **alarma contra un ensamblado desbocado**, con un tope de casa único
en `audita_texto_base.TOPE_KB` y el razonamiento escrito ahí.

**Y el número no se eligió a ojo, que era justo el vicio anterior.** `prueba_texto.py` tumba
esta comprobación inyectando **+312 KB** de comentario, así que el tope tiene que quedar **por
encima del tamaño actual y por debajo de tamaño + 312 KB** o el arnés se queda ciego. Subirlo a
900, que fue mi primer impulso, habría dejado **dos casos de inyección sin cazar**. Esa cota es
lo que hace que 700 no sea arbitrario, y lo mejor es que **la vigila el propio arnés**: quien
lo suba de más lo pondrá rojo.

| Archivo | Tamaño | Tope | Margen | Con el defecto inyectado | ¿Lo caza? |
|---|---:|---:|---:|---:|---|
| capítulo 1 | 530,1 KB | 700 | **169,9 KB** | 842,6 KB | **sí** |
| capítulo 2 | 491,0 KB | 700 | 209,0 KB | 803,5 KB | **sí** |
| capítulo 3 | 622,0 KB | 700 | 78,0 KB | 934,5 KB | **sí** |
| fixture | 271,5 KB | 550 *(propio)* | 278,5 KB | 584,0 KB | **sí** |

El fixture conserva tope propio y más bajo: su archivo es la mitad que un capítulo, y con el de
la casa el arnés dejaría de tumbarlo.

**Verificado después del cambio:** los cuatro auditores de prosa en verde con las **mismas
cuentas** (141, 129, 130, 77) y `prueba_texto.py` en **110 de 110**. El capítulo 1 pasó del
95 % al **76 %** del tope.

**Lo que esto le hace al resto del plan.** El peso deja de ser criterio de aceptación de
cualquier tarea, sale de la tabla de riesgos y las fases 2 a 4 ya no tienen que justificar un
dato nuevo por su tamaño. La regla *«en el código el titular, en el anexo la historia»* se
queda —un comentario de quince líneas dentro de una función se deja de leer— pero **fundada en
la legibilidad y no en los bytes**, que es lo que la hacía peligrosa.

## T1.1.h · Cambios en disco

| Archivo | Cambio |
|---|---|
| `precalculo/ensambla_cap1.py` | `SIMULADORES['n-efectivo']` reescrito con `nEff()`, `cuadra()`, eje derivado y `crearControles`; la prosa y la etiqueta accesible del módulo 5; la guarda de salida del módulo 5 |
| `Htmls_Espacial/capitulo-1-datos-espaciales.html` | +5 963 B · 4 bloques de diff, todos en el módulo 5 |
| `precalculo/audita_texto_base.py` | `TOPE_KB` nueva y `peso()` con tope por omisión *(T1.1.g)* |
| `precalculo/audita_texto_cap1.py`, `cap2`, `cap3` | `a.peso(560/560/680)` → `a.peso()` |
| `precalculo/audita_texto_demo.py` | conserva su tope propio, ahora comentado |

**`genera_cap1.R` no se tocó y los tres JSON del capítulo 1 son byte a byte los mismos**: T1.1
no estrena ni una cifra. **La plantilla tampoco**, así que los capítulos 2 y 3 no se
re-ensamblaron. Comprobado con `find -newermt`: los únicos archivos del árbol que cambiaron son
los de la tabla.

**Sobre el método de inyección.** Las catorce variantes defectuosas se construyeron en una
**copia completa del árbol** en el directorio de trabajo de la sesión, verificada primero por
`sha256` contra el capítulo real —`a6d69db77ef3e26e…`, idéntico— para saber que la copia
reproducía. Las siete variantes de ejecución se sirvieron por HTTP bajo nombres temporales y se
borraron al terminar; el capítulo publicado conserva el mismo `sha256` que antes de empezar el
arnés.

## T1.1.i · Preguntas abiertas que deja

1. **T2.1 tiene que elegir el ρ**, y su ficha ya lleva las dos opciones con sus costes: la
   retro-transformación (0.01462, barata y honesta, encaja con el rombo) o la estimación por
   bandas (de verdad, y casi seguro **no** reproduce 64.52155). No bloquea nada de la Fase 1.
2. **El margen del capítulo 3 es de 78 KB**, el más ajustado de los tres. No es un problema
   hoy —está cerrado— pero T4.1 lo va a re-ensamblar con los controles del motor. Si alguna vez
   se acerca, la salida ya no es recortar contenido: es subir `TOPE_KB` **y ajustar de paso los
   +312 KB de `prueba_texto.py`**, que es la cota que lo ata.
3. **El eje y llega hasta 1 346 pero su última línea de rejilla es 1 000**, así que sobra un
   poco de aire arriba. Cosmético; se deja anotado por si alguien afina el gráfico.

---
---

# Anexo T1.4 — Dos gráficos mudos, y la promesa que llevaba dibujando cero píxeles

**Ejecutada:** 2026-08-06 · **Resultado:** cerrada en verde · **Alcance real:** M, como se preveía
**Hallazgos que cambian el plan:** 1 · **Defectos de más encontrados:** 2 · **Errores míos que el arnés cazó:** 2

## T1.4.a · Lo que había, medido antes de tocar nada

El método que dejó establecido T1.2: reproducir y anotar el estado real antes de escribir
una línea.

| | `snow-serie` (módulo 1) | `correlograma` (módulo 3) |
|---|---|---|
| `.simulador-controles` | **0 hijos** | **0 hijos** |
| Series | Ataques, Muertes, «Retirada del mango» | real, residuos, permutado, E[I] |
| Lectura | **4 filas fijas** | **5 filas fijas** |
| Huella de píxeles | una sola: no hay nada que cambiar | una sola |

Eran los **dos últimos** `.simulador-controles` vacíos del capítulo, contados en el navegador
por T1.1.f y no de memoria.

## T1.4.b · Hallazgo 1: la marca del mango llevaba dibujando cero píxeles

El segundo criterio de la tarea pedía «la retirada del mango marcada en los dos». Al ir a
comprobar dónde estaba la marca del modo diario para replicarla en el acumulado, resultó que
**no estaba**.

La serie se declaraba así: 43 valores, **uno solo no nulo**, con `pointRadius: 0`.

```js
{ label: 'Retirada del mango (1854-09-08)',
  data: s.serie_fecha.map((_, i) => i === iMango ? Math.max(...s.serie_ataques) : null),
  borderColor: COLORES_GRAFICO.terciario, borderDash: [5, 4], pointRadius: 0, spanGaps: false }
```

Un punto suelto **no tiene vecinos con los que formar segmento**, y con radio 0 tampoco se
dibuja a sí mismo. El `borderDash` no llega a aplicarse a nada. Medido con diferencia de
píxeles del área de trazado, ocultando el conjunto y comparando:

> **0 píxeles de 385 990.** La serie existía **solo como entrada de leyenda**.

Y la intro decía, desde que se escribió el capítulo, *«con la retirada del mango marcada»*.

**Ningún auditor podía verlo,** por la misma razón que el descuadre de T1.2: las cifras del
JSON son correctas, la prosa es correcta, y lo que falla es lo que el navegador **pinta**.

**El arreglo sale gratis:** el plugin `marcadorX` que T1.2 registró para el deslizador de
`ee-ingenuo` hace exactamente esto —banda vertical sobre un eje de categorías— y estaba
inerte en 7 de los 8 gráficos. Ahora está activo en 2 de 8. Comprobado del mismo modo:
**11 890 píxeles en 41 columnas de dispositivo**, centradas en la columna del mango. La serie
de mentira se retiró.

> **Aviso de método, porque estuve a punto de publicarlo mal.** Mi primera medición del área
> de trazado usó `chart.chartArea`, que va en píxeles CSS, contra `getImageData`, que va en
> píxeles del lienzo —aquí el doble, `devicePixelRatio` 2—. Muestreaba el cuadrante
> equivocado y el marcador nuevo también daba 0. La conclusión inicial resultó ser correcta,
> pero **por casualidad**: la volví a medir sobre el respaldo del capítulo anterior, servido
> por HTTP, con la región corregida. Una medición que da el resultado esperado por el motivo
> equivocado es indistinguible de una buena hasta que deja de serlo.

## T1.4.c · El acumulado, y por qué en porcentaje

Consultado con Javier antes de escribir nada, entre acumulado **en casos** y acumulado **en %
del total**: se eligió el porcentaje. La razón es que el módulo argumenta que *el
{pct_ataques_antes_mango} % de los ataques había ocurrido antes del día del mango*, y con el
eje en porcentaje **esa frase se lee del gráfico**: la curva llega a la banda vertical por
90,4. Con el eje en casos habría que dividir 516 entre 571 de cabeza, y el 571 no está en
ninguna parte del dibujo.

El acumulado **se suma en el navegador** desde la serie diaria —D9 lo autoriza: es una suma— y
**no estrena ni una cifra en la prosa**. Lo que sí estrena es un anclaje afiladísimo para la
guarda, y ese es el segundo motivo de la elección: la víspera del mango, la curva que suma el
navegador tiene que dar **exactamente** el porcentaje que R calculó por su cuenta.

## T1.4.d · El correlograma: interruptores, y el segundo mando que había que cerrar

`crearInterruptores` es la tercera fábrica de la plantilla que nadie usaba. Aquí encaja sin
pelearse: tres casillas, una por serie, y **E[I] sin casilla** porque es la referencia contra
la que se leen las otras tres, no una serie más.

**El rótulo de la casilla es el mismo texto que el de la leyenda**, y es deliberado por dos
razones: el estudiante ve qué trazo apaga cada casilla, y la guarda puede emparejarlos **sin
una tabla de traducción** que pueda desincronizarse — que es la clase de defecto de T1.2, no
su instancia.

**La lectura numérica responde también** (decisión de Javier): apagar «permutado» le quita su
fila. Y la fila «cuánto de la I era altitud» **solo sale con las dos series encendidas**,
porque es una comparación entre ellas: publicarla con una apagada sería enseñar la conclusión
de un contraste que el estudiante no tiene delante.

**Y un mando de más que había que cerrar.** La leyenda de Chart.js oculta trazos al pulsarla.
Con las casillas puestas habría **dos mandos sobre el mismo estado**, y pulsar la leyenda
dejaría la casilla diciendo una cosa y el gráfico otra — el defecto de T1.2, resembrado en su
propio arreglo. La leyenda se redirige a la casilla, que queda como estado único; E[I], sin
casilla, no responde a su leyenda, que es lo que se quiere.

## T1.4.e · Hallazgo 2: la guarda desmintió el comentario que la justificaba

Al cablear el redirigido observé que asignar `g.options.plugins.legend.onClick` **no llegaba**
a la leyenda: Chart.js resuelve las opciones de sus plugins aparte de `chart.options`. Probé
un `update()` completo, funcionó, y escribí la línea con su comentario:

> *«Completo y no `'none'`: es el que vuelve a resolver las opciones de los plugins.»*

Añadí además una guarda de ejecución que comprueba que el redirigido **haya llegado**. Y al
inyectar el defecto para probarla —quitando ese `g.update()`— **la guarda no saltó**, porque
**no había defecto**: el `update('none')` de `pinta()` propaga el manejador igual de bien. Lo
que yo había observado era «asignar sin ningún update no propaga», no «hace falta el completo».

Conclusión: **la línea sobraba y su comentario era falso.** Las dos cosas se retiraron, la
guarda se quedó —es lo que probó que sobraba— y la inyección pasó a ser la de verdad: quitar
la asignación del redirigido. Entonces sí salta.

Es la lección de T0.2.g aplicándose al revés de lo habitual: el arnés no encontró un hueco en
la comprobación, encontró **una línea de código que yo había justificado con una explicación
que no se sostenía**, y la encontró en el único momento en que era barato retirarla.

## T1.4.f · Hallazgo 3: el arnés encontró un hueco de verdad

En la primera pasada de las inyecciones de compilación, **15 de 16**. La que no saltaba:

| Inyectado | Salida | |
|---|---|---|
| **la serie pierde el último día** | **0** | **no lo caza** |

Y no era un fallo de la comprobación sino un agujero real: los últimos días de la serie traen
**cero ataques y cero muertes**, así que recortar por la cola **no mueve ningún total**, y
todas las comprobaciones que había escrito miran totales. El eje del gráfico perdía un día y
la prosa cambiaba su fecha final —«del 1854-08-19 al …»— con los dos auditores en verde,
porque la fecha nueva también sale del JSON.

El hilo que faltaba es el que ata el **largo de la serie** a una cifra publicada, y estaba a
mano: el capítulo publica `n_dias_con_fecha` = 43 y `n_dias_tabla` = 44. Tres comprobaciones
nuevas —las tres series miden lo mismo, el largo es `n_dias_con_fecha`, y con `n_dias_sin_fecha`
suman `n_dias_tabla`— y el caso pasa a cazarse. **16 de 16.**

## T1.4.g · Las guardas, probadas por inyección

**En tiempo de compilación** (`ensambla_cap1.py`, guardas de salida). Dieciséis variantes del
JSON, construidas sobre una **copia completa del árbol** verificada primero por sha256 —el
capítulo se reproduce byte a byte desde ella— y restaurada al terminar:

| Defecto inyectado | Salida | Veredicto |
|---|---|---|
| sin inyectar (control) | 0 | — |
| la serie pierde el último día | 1 | **lo caza** *(ciego antes, §T1.4.f)* |
| la serie pierde el primer día | 1 | **lo caza** |
| el mango cae el primer día: sin víspera que acumular | 1 | **lo caza** |
| el mango no está en la serie | 1 | **lo caza** |
| `ataques_antes_mango` desviado en 1 | 1 | **lo caza** |
| `pct_ataques_antes_mango` desviado **1e-8** | 1 | **lo caza** |
| `pct_ataques_antes_mango` desviado **1e-11** (redondeo legítimo) | **0** | **no salta**: calibrada |
| `muertes_tabla` desviada en 2 | 1 | **lo caza** |
| `fecha_pico` movida | 1 | **lo caza** |
| `ataques_dia_mango` desviado en 1 | 1 | **lo caza** |
| las bandas del permutado se mueven | 1 | **lo caza** |
| a los residuos les falta una banda | 1 | **lo caza** |
| `esperado` de los residuos distinto del de ideam | 1 | **lo caza** |
| `caida_por_altitud_pct` desviada 0.01 | 1 | **lo caza** |
| `caida_por_altitud_pct` desviada **1e-9** (redondeo legítimo) | **0** | **no salta**: calibrada |

Las dos tolerancias no están elegidas, están acotadas: el JSON redondea a diez decimales, así
que la diferencia legítima no pasa de 5e-11 y el umbral de 5e-10 queda veinte veces por encima
de ella y órdenes de magnitud por debajo de cualquier descuadre real.

**En tiempo de ejecución** (`cuadra()`). Diez variantes defectuosas del capítulo, servidas por
HTTP bajo nombres temporales y recorridas en sus **2 posiciones del módulo 1 y sus 8
combinaciones del módulo 3**:

| Cableado inyectado | Avisadas | Excepciones | Lecturas congeladas |
|---|---|---|---|
| **sin inyectar (control)** | **0** | 0 | 0 |
| el acumulado corrido un día | 1 de 2 | 0 | 0 |
| el acumulado dividido por el total equivocado | 1 de 2 | 0 | 0 |
| el acumulado en fracción y no en % | 1 de 2 | 0 | 0 |
| la banda del mango un día a la derecha | 3 de 3 | 0 | 0 |
| ataques y muertes intercambiadas | 3 de 3 | 0 | 0 |
| el modo ignorado: siempre acumulado | 2 de 2 | 0 | 0 |
| el interruptor apaga el trazo del vecino | 10 de 10 | 0 | 0 |
| «dato real» alimentado con las I del permutado | 15 de 15 | 0 | 0 |
| E[I] oculto | 15 de 15 | 0 | 0 |
| la leyenda sin redirigir al interruptor | 15 de 15 | 0 | 0 |

Los mensajes nombran las dos cifras, que es lo que los hace utilizables: *«la víspera del mango
la curva va por 85.46409807355516 % y R publica 90.3677758319 %»*, *««Temperatura (dato real)»
dibuja -0.0253357115 en la primera banda y su serie del JSON trae 0.606348194»*.

**Cero excepciones y cero lecturas congeladas en las once variantes**, que es el otro criterio
que T1.2 dejó: un simulador que se congela en silencio es peor que uno que avisa.

**Y la lección de T1.2.d, aplicada donde tocaba.** La comprobación de que cada trazo dibuja lo
que dice su rótulo **no puede contrastarse contra la misma casilla de la que sale el trazo**, o
sería tautológica. La escribí primero así y lo era: `SERIES` daba el dato y `SERIES` daba la
referencia, de modo que cambiar la serie dentro de `SERIES` habría dado verde. Ahora `cuadra()`
lleva su **propio** emparejamiento rótulo↔serie del JSON, dicho por segunda vez y aparte, y el
caso «dato real alimentado con el permutado» —el que la versión tautológica se habría comido—
avisa 15 de 15.

## T1.4.h · Verificación

**Posición a posición**, que es el criterio transversal de la Fase 1.

`snow-serie`, las dos posiciones:

| Modo | eje y | banda | curva en el mango | curva la víspera | lectura |
|---|---|---|---|---|---|
| Casos por día | casos por día | 1854-09-08 | **12** = JSON | 28 | pico, mango, 90.36778 %, 91.60839 % |
| Acumulado, % del total | % del total acumulado, 0–100 | 1854-09-08 | 92.46935 % | **90.36778 %** = JSON | 516 de 571, 90.36778 %, 81.16883 %, 55 de 571 |

El **90.36778 %** de la víspera lo calcula el navegador sumando 43 números y coincide con el
que R publica hasta el último decimal que el JSON trae. Dos huellas de píxeles distintas de dos.

`correlograma`, **las 8 combinaciones de los tres interruptores**:

> **8 de 8 correctas · 8 huellas de píxeles distintas de 8 · 0 avisos de consola.**

En las ocho, lo que Chart.js dice que dibuja (`isDatasetVisible`) coincide con lo que dice la
casilla, **E[I] se dibuja en las ocho** —incluida la de las tres apagadas, que enseña el
correlograma desnudo con solo su referencia— y la lectura va de **1 fila a 6** siguiendo a los
interruptores.

**Teclado.** Las casillas son `<input type="checkbox">` dentro de su `<label>`: foco por
tabulador, espacio para conmutar, y el rótulo es el texto de la leyenda. Los dos botones del
módulo 1 son `<button type="button">`, como los de `snow-mapa`.

**Los doce módulos, con la consola abierta.** **0 errores y 0 excepciones.** **17/17 lienzos con
tinta**, los 17 con `aria-label`. Y el criterio del Checkpoint 1:

> **`.simulador-controles` vacíos: 0.** Eran 2 al empezar y eran los dos últimos del capítulo.

**Los auditores:**

| Auditor | Antes de T1.4 | Ahora |
|---|---|---|
| `audita_cap1.py` | 848 · 0 fallos · 3 saltadas | **848 · 0 · 3** |
| `audita_texto_cap1.py` | 141 · 0 fallos | **141 · 0** |

Las cuentas no se mueven porque T1.4 **no estrena ni un dato**: el acumulado es derivado y no
publicado, como pedía el tercer criterio. El arnés de los tres capítulos,
`audita_todo.sh --rapido`, en **3 min 58 s**: salida 0, **ARNÉS COMPLETO EN VERDE**,
**2 126 comprobaciones · 0 fallos**, las mismas siete cuentas que tras T1.1 y T1.2
(848, 445, 356, 77, 141, 129, 130). **Cero regresiones en los capítulos 2 y 3.**

`prueba_texto.py`, que es el arnés del auditor que este cambio podía romper porque reescribe
dos párrafos: **110 defectos inyectados · 110 detectados** (cap1 30/30, cap2 24/24, cap3 20/20,
fixture 36/36). Ninguna comprobación se perdió.

**Sobre el arnés completo con inyección.** No se pasó, y se dice por qué, con el mismo criterio
que T1.1: T1.4 **no toca ningún auditor de precálculo**. Sí se pasaron `prueba_texto.py` y las
**26 inyecciones propias** de la tarea. Queda para el cierre de la Fase 1.

**Peso**, que ya no es criterio de aceptación: 530,1 → **540,3 KB**, +10 467 B, **77 % de la
alarma de 700 KB**.

## T1.4.i · Un límite de la verificación, declarado

**El clic automatizado no llega a la leyenda de Chart.js en este arnés.** Al ir a comprobar el
redirigido pulsando la leyenda de verdad, el clic aterriza dentro de la caja —medido:
`offsetX` 159, `offsetY` 17, contra una caja de 73–244 × 10–22— y no pasa nada.

Antes de culpar a mi código monté el **control**: la misma prueba sobre `ee-ingenuo`, un
gráfico que T1.4 no toca y que conserva el manejador **de fábrica** de Chart.js. Tampoco
responde. Es la herramienta, no la página.

Así que el redirigido está verificado **una capa por debajo**, llamando a
`g.legend.handleEvent({type:'click', x, y})`, que es exactamente lo que Chart.js invoca desde
su `afterEvent`: la casilla se desmarca, el trazo desaparece y la lectura baja de 6 filas a 3,
los tres a la vez. Y la guarda comprueba en cada cambio que el redirigido siga instalado.

Lo que **no** puedo afirmar es haberlo probado con un clic de ratón de verdad de punta a punta.
Queda anotado, como T0.1.f anotó lo del `file://`.

## T1.4.j · Cambios en disco

| Archivo | Cambio |
|---|---|
| `precalculo/ensambla_cap1.py` | `SIMULADORES['snow-serie']` reescrito con `acumPct()`, `cuadra()`, el marcador y la botonera; `SIMULADORES['correlograma']` reescrito con `SERIES`, `DEBE`, `cuadra()`, `crearInterruptores` y el redirigido de la leyenda; las dos intros; las guardas de salida de los módulos 1 y 3 |
| `Htmls_Espacial/capitulo-1-datos-espaciales.html` | +10 467 B · 8 725 → 8 914 líneas · **6 bloques de diff**: 2 de prosa y 4 de JS |

**`genera_cap1.R` no se tocó y los tres JSON del capítulo 1 son byte a byte los mismos**
(`cap1_datos.json` sigue en `5215b28207…` y `cap1_soluciones.json` en `e539cf603c…`, los mismos
que registró T1.2). **La plantilla tampoco**, así que los capítulos 2 y 3 no se re-ensamblaron.
Comprobado con `find -newermt`: los únicos archivos del árbol que cambiaron son los dos de la
tabla.

Las diez variantes defectuosas se sirvieron bajo el prefijo `_t14_` y se borraron al terminar;
`Htmls_Espacial/` vuelve a tener sus cinco archivos y el capítulo conserva su sha256.

## T1.4.k · Preguntas abiertas que deja

1. **El acumulado se detiene en el 100 % desde el 09/20 largo**, porque los últimos catorce días
   traen ceros. Es fiel al dato y enseña que el brote se acabó, pero deja un tercio del eje en
   una recta plana. Si alguien quiere recortar la ventana, que sea **en R y publicando el
   recorte**, no en el navegador: las tres comprobaciones nuevas de §T1.4.f atan el largo de la
   serie a `n_dias_con_fecha` justamente para que ese recorte no pueda hacerse en silencio.
2. **T2.5 hereda este simulador** para meterle la banda nula de permutaciones, y hereda con él
   `SERIES` y `DEBE`. La envolvente será una serie más: si lleva interruptor, entra en las dos
   listas; si es fondo de la permutada, va atada a su casilla. Conviene decidirlo al escribir
   T2.5 y no después.

---
---

# Anexo T1.3 — El variograma que no era de ningún mapa

**Ejecutada:** 2026-08-06 · **Resultado:** cerrada en verde · **Alcance real:** M, como se preveía
**Hallazgos:** 4 —uno de ellos anterior a la tarea y presente en un segundo simulador— · **Errores míos que la inyección cazó:** 2

## T1.3.a · Lo que había, medido antes de tocar nada

El método de T1.2 y T1.4: reproducir el estado real antes de escribir una línea. Y aquí el
estado real no era el que el plan describía.

| | Lo que decía el plan | Lo que había |
|---|---|---|
| El defecto | «el variograma dibuja siempre `v.una`» | cierto, **y además `v.una` no es el variograma de ninguno de los tres mapas** |
| Los tres mapas | tres realizaciones del proceso | rejilla **28×28**, semilla `SEMILLA+700`, `genera_cap1.R:1336` |
| La curva, la banda y **todas** las cifras | del mismo proceso | rejilla **16×16**, semilla `SEMILLA+300`, `genera_cap1.R:605` |
| La intro | — | anunciaba «sobre **16×16** celdas» sobre un mapa de **28×28** |

Eran **dos simulaciones distintas**, emparejadas por el índice del botón.

## T1.3.b · Hallazgo 1: no era una curva quieta, era la curva de otro campo

Esto no se dedujo del código: se midió. `cap1_mapas.json` guarda el campo cuantizado de cada
mapa en su `zq`, así que se puede rehacer el variograma **del campo que el estudiante ve** y
compararlo con el publicado.

```
variograma del mapa 1 (28×28), rehecho :  0.2512  0.4334  0.5768  0.7228  …
variograma del mapa 2 (28×28), rehecho :  0.2509  0.4115  0.5485  0.6797  …
variograma del mapa 3 (28×28), rehecho :  0.2543  0.4199  0.5225  0.5769  …
`v.una`, la curva que se dibujaba      :  0.2506  0.3746  0.4548  0.5540  …
```

> **La curva publicada no era la de ninguno de los tres.** El botón no «dejaba quieta» una de
> las tres curvas: dibujaba una cuarta, de un campo que no estaba en la página.

Y la desviación era **sistemática, no aleatoria**: un campo de 28×28 tiene más pares por
rezago que uno de 16×16, así que su variograma empírico varía menos. Las tres curvas de los
mapas caían cómodamente dentro de una banda calculada para 256 celdas, y el módulo —cuya
tesis es *cuánto puede desviarse una realización*— enseñaba el caso favorable sin decirlo.

**Ningún auditor podía verlo**, por tercera vez en este plan y por la misma razón que en T1.2
y T1.4: cada JSON era correcto por su cuenta y el defecto vivía **en el hueco entre los dos**.

## T1.3.c · Hallazgo 2: la intro mentía, y es P12 otra vez

`inf['k']` es el `k` del **módulo 4**, y el módulo 6 lo usaba prestado para describir su
propia figura. P12 registra este defecto para el módulo 4 —donde el texto **calla** la
resolución del mapa— y no registraba esta segunda instancia, donde el texto **no calla: se
equivoca**. Queda cerrada por construcción: los mapas son ahora de 16×16 y una guarda de
compilación ata `nx`/`ny` a `una_realizacion.k`, que es el `k` del propio módulo (nuevo en el
JSON). La instancia del módulo 4 sigue abierta y es de T2.4.

## T1.3.d · La decisión, consultada antes de tocar R

Se le plantearon a Javier dos formas de reunir las dos simulaciones, y dentro de la elegida,
dos formas de escoger las tres realizaciones. Eligió las dos recomendadas:

- **Los tres mapas pasan a ser tres de las 1 000**, en su rejilla de 16×16. Se borra la
  simulación aparte (`SEMILLA+700`, `R8`, `L8`) y `MAPAS$realizaciones` se dibuja desde
  `CAMPOS[, 1:3]`, el mismo lote que produce la banda, la sd de las medias y el 82 % de
  rechazo. La alternativa —calcular una segunda banda a 28×28— dejaba el módulo con dos
  lotes y la coherencia con el módulo 4 atada al primero: el mismo divorcio, mejor
  disimulado.
- **Las tres primeras, sin elegir, y el capítulo lo dice.** La alternativa —mín/mediana/máx
  de la media— es más vistosa, pero deja de ser «tres tiradas del mismo proceso» y pasa a ser
  «tres extremos escogidos», que es otra lección y menos honesta bajo el mismo rótulo.

Consecuencia agradable: `medias_muestra`, que R exportaba y **nadie usaba**, pasa a ser el
control de esa decisión. Si el capítulo dejara de enseñar las tres primeras sin declararlo,
la guarda de compilación lo dice.

## T1.3.e · Hallazgo 3: el comentario de R que justificaba la elección era falso

`genera_cap1.R` explicaba por qué se publicaba `V[, 1]`:

> *«Una realización cualquiera: la primera. Su variograma se sale de la banda en algún lag, y
> eso es lo que hay que enseñar.»*

**No se salía en ninguno.** `v.una` caía dentro del 5–95 % en los ocho rezagos, y las tres
que se publican ahora también: `0 de 8` las tres. El comentario describía una figura que el
dato no daba, y llevaba ahí desde que se escribió el módulo.

El arreglo no es forzar una realización que se salga —eso sería escoger— sino **publicar la
cifra en vez de afirmarla**. Cada realización trae ahora cuánto se aparta del teórico y en
qué rezago, y cuántos rezagos se le salen de la banda:

| | media espacial | se aparta del teórico | en el rezago | rezagos fuera de banda |
|---|---:|---:|---:|---:|
| Realización 1 | 0.10488 | 0.13802 | 3 | 0 de 8 |
| Realización 2 | 0.47008 | 0.25488 | 1 | 0 de 8 |
| Realización 3 | 0.19523 | 0.32751 | 8 | 0 de 8 |

Que las tres estén dentro de la banda **no debilita el módulo: lo precisa**. La banda del
5–95 % es el recorrido de las mil; apartarse del teórico un tercio de su valor sin salirse de
ella es exactamente el problema que el módulo enseña.

**Detalle que vale la pena:** la curva de la posición 1 **no cambió ni un decimal**. Era
`V[, 1]` y sigue siéndolo. Lo único que cambió es que ahora el mapa de debajo es el campo que
la produjo.

## T1.3.f · Hallazgo 4: el botón podía discrepar de todo lo demás

Lo encontró la propia verificación, comprobando algo que no estaba en ningún criterio: **salir
del módulo y volver**.

```
                        botón        mapa            curva       lectura
al entrar               Realización 1  Realización 3   la de la 3  3
```

`realIdx` vive **fuera** de la función del simulador —en la línea de estado que comparten
`snowModo`, `campoIdx` y `realIdx`— y sobrevive a `loadModule`. La botonera, en cambio, se
reconstruía marcando **siempre la primera**. El estudiante volvía al módulo y encontraba el
botón diciendo una cosa y el mapa, la curva y la lectura diciendo otra.

Es exactamente el defecto que T1.4.e cerró para la leyenda de Chart.js —**dos mandos sobre un
mismo estado que pueden discrepar**— y **es anterior a T1.3**: estaba desde que se escribió la
botonera. Lo que cambió es que ahora se nota mucho más, porque antes el botón solo movía el
mapa y ahora mueve tres cosas.

`botonera()` acepta ahora un valor inicial y marca el botón que corresponde al estado, con
respaldo al primero si el valor no está entre las opciones —el mismo patrón que `deslizador()`
usa desde T1.2—. Sin ese argumento se comporta como antes, así que las tres botoneras de
estado **local** (`agregacion`, `cv-espacial` y `snow-serie`) no se enteran: se reinician con
su función y ya eran coherentes.

**Y arreglaba de paso un segundo simulador.** `snow-mapa` tiene el mismo patrón con `snowModo`
y el mismo defecto. Comprobados los dos en el navegador:

| | tras volver al módulo | botón | lo dibujado |
|---|---|---|---|
| `una-realizacion` | con la 3 elegida | **Realización 3** | Realización 3 |
| `snow-mapa` | con «Sin las calles» | **Sin las calles** | sin las calles |

> **La lección de método, que es la de toda la fase.** Los tres botones «funcionaban» en la
> prueba posición a posición, porque esa prueba nunca sale del módulo. El estado que sobrevive
> a la navegación es una dimensión más del simulador, y no estaba en ninguna lista de
> comprobación. Ahora sí: **probar cada control también al volver**, no solo al llegar.

## T1.3.g · Las tres capas de guarda, y qué ve cada una

Ninguna de las tres puede ver lo de las otras dos, y por eso son tres:

| Capa | Dónde | Qué comprueba | Qué **no** puede ver |
|---|---|---|---|
| **Compilación** | `ensambla_cap1.py` | las dos listas se emparejan por `id`, `media` y `sd`; `nx = ny = k`; una curva por rezago; las tres curvas se separan; las medias son las de `medias_muestra` | si la curva es la del campo de su mapa |
| **Ejecución** | `cuadra()` en el JS | que el mapa **que el motor dibuja** sea el de la fila que da la curva | el contenido de la curva (D9 no deja ajustar un variograma en el navegador) |
| **Auditoría** | `audita_cap1.py` | rehace media, sd y variograma **desde el `zq` del mapa dibujado** | nada del cableado: solo mira archivos |

`cuadra()` pide el mapa a la **misma `fuente()`** que invoca el motor y lo compara por
`media_espacial` —que R calcula con `mean(z)` sobre el vector del mapa— contra `media` —que
calcula con `colMeans()` sobre la matriz de las mil—. Dos rutas, una cifra. Comparar el `id`
consigo mismo no habría comprobado nada, porque `fuente()` ya busca por `id`: es la lección
de T1.2.d, aplicada de entrada esta vez.

## T1.3.h · Las guardas, probadas por inyección

**25 defectos inyectados, 25 cazados**, en las tres capas:

| Capa | Inyecciones | Cazadas | Dónde vive el arnés |
|---|---:|---:|---|
| Auditoría (`audita_cap1.py`) | 14 | **14** | `prueba_auditor_cap1.py`, **familia 14 nueva**, permanente |
| Compilación (`ensambla_cap1.py`) | 8 | **8** | guion de sesión que restaura los JSON y comprueba el sha256 del HTML |
| Ejecución (`cuadra()`) | 3 | **3** | en el navegador, sobre el capítulo publicado |

La familia 14 ataca **por los dos lados** a propósito —cambiando la curva publicada con el
mapa quieto, y cambiando el campo del mapa con la curva quieta—: una comprobación que solo
mirase uno de los dos archivos pasaría la mitad de ellas.

La octava inyección de compilación no vigila una cifra sino **una frase**. La prosa afirma que
las tres caben dentro de la banda en los ocho rezagos, y esa afirmación no sale de ningún
número del JSON: sale de una propiedad de los datos. Ninguno de los dos auditores podría verla
caducar —el de cifras no la mira porque no lleva números, y el de prosa comprueba que las
cifras existan, no que la afirmación siga siendo cierta—. Con una realización fuera de la
banda, el ensamblador ahora para y dice qué frase hay que reescribir.

La inyección de ejecución reprodujo el defecto original desplazando los `id` de los mapas en
uno, y dejó a la vista **por qué se ocultó tanto tiempo**:

```
              lectura sin defecto        lectura con el defecto dentro
Realización 1   1 / 0.10488                1 / 0.10488
Realización 2   2 / 0.47008                2 / 0.47008
Realización 3   3 / 0.19523                3 / 0.19523
```

**La lectura es idéntica.** Lo único que cambia es el mapa, y no hay nada en la página con
qué compararlo. Las tres `console.error` de la guarda son la única diferencia observable:

```
una-realizacion: el mapa dibujado no es el de la curva. La fila es la realización 1,
de media 0.1048800029, y el mapa tiene media 0.47008258
```

Antes y después de la inyección, los tres botones en silencio.

## T1.3.i · Dos errores míos, y los dos los encontró la inyección

Los dos son la misma falta: **una comprobación que se estrella en vez de informar**. El
código de salida es distinto de cero igual, así que el arnés las dio por cazadas —y lo
estaban, en el sentido inútil—.

1. **`audita_cap1.py` reventaba con un `nx` incoherente.** Con `nx = 28` y 256 celdas, la
   reconstrucción de la retícula lanzaba `IndexError` a media auditoría: se perdía el informe
   de las 900 comprobaciones restantes. Ahora lo dice y sigue: `888 comprobaciones · 3 fallos`
   en vez de `(sin resumen)`.
2. **`ensambla_cap1.py` reventaba con una fila sin variograma.** El cálculo de la separación
   entre curvas hacía `KeyError` antes de que el bucle de arriba pudiera imprimir su `MAL`:
   código 1 y **ni una línea de informe**. Ahora la separación se calcula solo sobre las
   curvas completas.

> **Cazar no es fallar: es fallar diciendo qué.** Un auditor que se estrella deja de informar
> del resto, y desde fuera —código 1— se ve igual que uno que diagnostica. Las dos
> comprobaciones que faltaban están ahora en la familia 14, permanentes.

## T1.3.j · Una tolerancia que hubo que medir, no deducir

La reconstrucción desde `zq` no es exacta y necesita tolerancia. La escribí primero en 1e-3
razonando el sesgo del redondeo: paso = rango/1000 ≈ 0.0047, sesgo = paso²/12 ≈ 2e-6. **El
razonamiento era correcto y la tolerancia estaba mal**, porque ese no es el término que
manda: sobre 256 celdas —y sobre pares que comparten celda— el término cruzado entre el campo
y su error de redondeo no se promedia a cero. Medido:

| | peor residuo | tolerancia | margen |
|---|---:|---:|---:|
| media espacial | 6.58e-05 | 2e-3 | 30× |
| sd espacial | 1.25e-04 | 2e-3 | 16× |
| variograma | **2.80e-04** | 5e-3 | **17.9×** |

Y por el otro lado: dos de estas curvas se separan **0.10286** en el rezago que más las
distingue, o sea **21×** la tolerancia. Entre el ruido y la señal hay sitio de sobra, y ese
margen es lo que hace que la comprobación distinga una curva de otra en vez de aceptarlas
todas. El ensamblador imprime esa separación en cada pasada.

## T1.3.k · Verificación

**En el navegador**, posición a posición, sobre el capítulo final y con el viewport en
1280×900:

| | curva (rezagos 1 y 8) | lectura | huella del gráfico | huella del mapa |
|---|---|---|---|---|
| Realización 1 | 0.25056 … 0.91358 | 1 / 0.10488 / 0.93781 | `47e01bf1` | `374ea433` |
| Realización 2 | 0.27758 … 0.90125 | 2 / 0.47008 / 0.90967 | `8c7b73cf` | `18a7de28` |
| Realización 3 | 0.24907 … 1.14785 | 3 / 0.19523 / 1.07391 | `816e35f3` | `c8ab7010` |

**Tres curvas distintas, tres huellas de gráfico distintas y tres huellas de mapa distintas**,
las nueve cifras de la lectura son las del JSON y el botón activo es el que corresponde en las
tres. **0 errores de consola.** Y saliendo del módulo con la 3 elegida y volviendo: botón
**Realización 3**, lectura **3** (hallazgo 4).

> El valor absoluto de una huella no significa nada —es un hash de píxeles muestreados, y
> cambia si cambia el muestreo—. Lo único que se lee de esa columna es que **las tres son
> distintas**, que es lo que un gráfico congelado no puede dar.

**Los doce módulos recorridos** con el capturador de `console.error` y de `window.onerror`
puestos antes del primero: **0 errores, 0 excepciones, 0 `.simulador-controles` vacíos**,
17 lienzos y los 17 con tinta y con `aria-label`.

> **Aviso de método.** El recorrido dio primero `16 de 17` con tinta: el lienzo de la
> autoevaluación del módulo 12 se mide en el instante en que Chart.js aún no lo ha
> dimensionado —`width = 0`— y una lectura síncrona lo cuenta como vacío. Medido de nuevo con
> el módulo asentado: **46 072 píxeles con tinta de 529 308**, y su `aria-label` presente. El
> defecto estaba en mi medición, no en el capítulo, pero conviene dejarlo escrito porque el
> recorrido de cada checkpoint lo va a repetir.

**Los auditores**, antes y después:

| | antes de T1.3 | después |
|---|---:|---:|
| `audita_cap1.py` | 836 · 0 fallos | **901** · 0 fallos, 3 saltadas |
| `audita_texto_cap1.py` | 141 · 0 fallos | **141** · 0 fallos |
| `prueba_auditor_cap1.py` | 49 de 49 | **63 de 63** |

**Y el arnés de los tres capítulos**, `audita_todo.sh --rapido`, código 0, **ARNÉS COMPLETO EN
VERDE**:

| Auditor | Comprobaciones | Fallos |
|---|---:|---:|
| `audita_cap1.py` | **901** *(eran 836)* | 0 (3 saltadas) |
| `audita_cap2.py` | 445 | 0 (2 saltadas) |
| `audita_cap3.py` | 356 | 0 (2 saltadas) |
| `audita_texto_demo.py` | 77 | 0 |
| `audita_texto_cap1.py` | 141 | 0 |
| `audita_texto_cap2.py` | 129 | 0 |
| `audita_texto_cap3.py` | 130 | 0 |
| **Total** | **2 179** *(eran 2 114)* | **0** |

Los 65 de más son exactamente los del módulo 6. **Ninguna comprobación preexistente se perdió**,
y los capítulos 2 y 3 no se tocaron: T1.3 no entra en la plantilla ni en el motor.

## T1.3.l · Cambios en disco

| Archivo | Qué |
|---|---|
| `genera_cap1.R` | sección **F.1 nueva** (las tres vistas, con su variograma y sus desvíos); **M.5 reescrita**: se borran `SEMILLA+700`, `R8` y `L8` y los mapas salen de `CAMPOS[, 1:3]`; `una_realizacion.k` nuevo; `variograma.una` retirado |
| `ensambla_cap1.py` | prosa del módulo 6 (rejilla propia, la declaración de «las tres primeras», los desvíos medidos, un recuadro de método); el simulador redibuja la curva y estrena `cuadra()`; `fuente()` busca por `id`; **guarda de compilación del módulo 6**, con la que vigila la frase de la banda |
| `audita_cap1.py` | rehace media, sd y variograma de las tres **desde el `zq` del mapa**, más las cuatro cifras derivadas y la separación entre curvas |
| `prueba_auditor_cap1.py` | **familia 14**, 14 defectos, permanente |
| `ensambla_cap1.py`, otra vez | `botonera()` acepta un valor inicial (hallazgo 4). Toca también **`snow-mapa`**, del módulo 1, que tenía el mismo defecto |
| `cap1_datos.json` | 36 389 → **37 116** bytes |
| `cap1_mapas.json` | 111 733 → **105 419** bytes (los mapas de 16×16 pesan menos que los de 28×28) |
| `capitulo-1-datos-espaciales.html` | 553 304 → **552 571** bytes · 540 KB, 77 % del tope de casa |

El diff del capítulo son **7 bloques**, contados: **cinco del módulo 6** —los dos párrafos de
prosa, el `DATOS_CAP1` incrustado, el registro del `.geomapa` y el simulador— y **dos del
hallazgo 4**: la función `botonera()` y la llamada de `snow-mapa`, que es el otro simulador
que tenía el defecto. Y el diff estructurado de los tres JSON
no toca nada fuera de `realizaciones_vistas`, `una_realizacion` y `mapas.realizaciones` —salvo
la fecha de `meta.generado`—.

## T1.3.m · Lo que deja abierto

1. **P12 sigue abierta para el módulo 4.** Su instancia del módulo 6 se cierra aquí y con una
   guarda; la del módulo 4 —mapa de 28×28, cifras de 16×16, el texto callado— es de T2.4. La
   guarda nueva es el molde: atar `nx`/`ny` al `k` que publica el módulo.
2. **Las guardas de compilación no tienen arnés permanente.** Las del módulo 6 se probaron
   con un guion de sesión que restaura los JSON byte a byte y comprueba que el HTML vuelve a
   su sha256; las de T1.2 y T1.4 se probaron igual. Un `prueba_ensambla_cap1.py` que hiciera
   eso con las cinco familias de guarda que ya hay valdría lo que cuesta, y no es de esta
   tarea.
3. **`variograma.una` desapareció del JSON.** Si algún capítulo posterior quisiera reutilizar
   «una realización de referencia», ahora se llama `realizaciones_vistas[0].variograma`.
4. **El estado que sobrevive a la navegación no lo comprueba nadie más.** El hallazgo 4 se
   arregló en los dos simuladores del capítulo 1 que lo tenían, pero **`crearControles`,
   `crearSelector` y `crearInterruptores` viven en la plantilla** y los usan los capítulos 2 y
   3. Si alguno guarda su estado fuera de la función, tendrá el mismo desajuste. Es barato de
   mirar y encaja de lleno en **T4.1**, que ya toca el motor y re-audita los tres capítulos.

## T1.3.n · `prueba_ensambla_cap1.py`, el arnés que faltaba *(añadido a petición de Javier, 2026-08-06)*

La pregunta abierta nº 4 se contestó «móntalo antes de la Fase 2». Al ir a montarlo, la
primera medición ya corrigió mi propio diagnóstico: **no eran cinco familias de guarda, eran
41 guardas**, contadas por `ast` sobre el código y no de memoria. Las de cableado —las que yo
recordaba— son solo una parte; el resto vigilan la estructura del documento, los tipos de
pregunta del quiz, los espacios finos dentro de KaTeX y el presupuesto de geometría.

### Lo que hizo falta antes: que el arnés no pueda romper nada

El ensamblador **escribe el HTML antes de correr sus guardas**. Un arnés que solo redirigiera
la entrada dejaría el capítulo publicado construido con datos rotos en cada inyección, y si el
arnés muriera a mitad, lo dejaría así. Por eso `ensambla_cap1.py` estrena cinco variables de
entorno con el convenio que ya usaban los auditores —`CAP1_DATOS`, `CAP1_MAPAS`,
`CAP1_SOLUCIONES`, `CAP1_PLANTILLA` y, la que importa, **`CAP1_DESTINO`**—. Sin ellas se
comporta exactamente igual que antes; con ellas el arnés es de solo lectura sobre el árbol de
verdad, y lo comprueba byte a byte al terminar.

### Tres superficies, porque una no llega

| Superficie | Para qué guardas | Cómo | Inyecciones |
|---|---|---|---:|
| **Los JSON** | el dato, y la coherencia entre dos archivos que R escribe por separado | mutar el objeto parseado | 29 |
| **El propio ensamblador**, en copia | sus literales: cuántos módulos, los tipos de pregunta, el tope del deslizador | sustituir texto y ejecutar la copia | 11 |

La segunda no es una trampa: esas guardas existen **justo para el día en que alguien edite el
ensamblador**, así que inyectar ahí es el modelo de amenaza correcto. Y solo es posible porque
las cinco variables permiten ejecutar una copia desde cualquier sitio.

### Un hueco que apareció al intentar usar la tercera superficie

Había previsto **la plantilla** como tercera superficie y no está: **no es alcanzable, y se
midió antes de afirmarlo**. El ensamblador sustituye los cinco módulos de demostración de la
plantilla por los doce del capítulo, así que ni sus `<template>` ni sus siete lienzos llegan al
marcado que las guardas cuentan. Quitarle un `</template>` o un `aria-label` a la plantilla
deja el ensamblado **limpio**.

> **Las guardas de compilación del capítulo 1 no ven la plantilla.** Es un hueco de las
> guardas, no del arnés, y toca justo donde va a doler: **T3.1 y T4.1 tocan la plantilla y la
> retropropagan a los tres capítulos**. Cerrarlo pide una guarda que mire la plantilla *antes*
> de sustituirla; el día que exista, el arnés la inventaría sola.

### Resultado

```
40 de 40 defectos cazados
41 de 41 guardas se han visto disparar
```

Y la prueba que el arnés le exige a los demás, aplicada a sí mismo: desactivando **una** guarda
a mano —la del rombo de Colombia— devuelve código 1, marca `SE COLÓ` ese defecto exacto, baja
la cobertura a 40/41 y **nombra la línea** de la guarda que se quedó muda. El ensamblador queda
restaurado byte a byte.

### Dos errores míos, y los dos los encontró el propio arnés

1. **La inyección que reescribía la guarda que quería probar.** Para la guarda «pocas líneas
   `#>`» quité todos los marcadores del ensamblador… incluida la línea
   `cifras = doc.count("#&gt;") + doc.count("#>")`, que **es la que cuenta**. El contador pasó a
   contar `#  ` por todo el documento: 97 en vez de 28, y verde. Se arregla apartando la línea
   de la guarda antes del barrido y devolviéndola después. *Una inyección que modifica la
   comprobación que quiere probar no prueba nada*, y esta salió `SE COLÓ` en vez de dar un
   falso verde solo porque el arnés distingue «cazado» de «no cazado» por el `MAL`, no por el
   código de salida.
2. **La cobertura se medía por el mensaje, y mentía.** Emparejaba el texto del `MAL` con el
   trozo literal más largo de cada `problemas.append`. Funcionó hasta esa misma inyección: como
   reescribe el marcador que el mensaje nombra, el informe dijo «sin ver disparar» de una
   guarda que **acababa de dispararse**. Ahora la cobertura se **mide**: `sys.settrace` anota
   qué líneas del ensamblador se pisan y cuáles de ellas son un `problemas.append`. Cada guarda
   se identifica por su **ordinal** y no por su número de línea, porque una sustitución de texto
   se las desplaza a la copia.

> **Un arnés cuya cobertura se equivoca es peor que no tener cobertura**, porque invita a añadir
> inyecciones que ya sobran y a dar por descubierto lo que no lo está. Las dos veces, el error
> estaba en el instrumento y no en lo medido — igual que el `chartArea` en píxeles CSS de
> T1.4.b.

Y una regla nueva, propia de este arnés: **una inyección que no cambia nada no es una
inyección**. Toda sustitución comprueba que de verdad modificó el archivo y, si no, se informa
como `INERTE` —avería del arnés— y no como guarda que se coló. Sin eso, una guarda intacta y un
literal que cambió de sitio se ven exactamente igual desde fuera.

### Dónde vive

Paso **3** de `audita_todo.sh`, y **corre también con `--rapido`**: cuesta **2,3 s**, porque el
ensamblador tarda 0,05 s y 40 inyecciones trazadas siguen siendo más baratas que *una* pasada
del auditor del precálculo. Gatearlo habría servido para no correrlo nunca.

El bucle lo busca por nombre, así que `prueba_ensambla_cap2.py` y `prueba_ensambla_cap3.py`
entrarán solos el día que existan. **Y hacen falta:** `ensambla_cap2.py` tiene **7** guardas y
`ensambla_cap3.py` **5**, todas sin arnés hoy.

### Cambios en disco

| Archivo | Qué |
|---|---|
| `precalculo/prueba_ensambla_cap1.py` | **nuevo**, 464 líneas · inventario por `ast`, 40 inyecciones, cobertura trazada |
| `precalculo/ensambla_cap1.py` | cinco variables de entorno (`_ruta()`), y `relative_to` tolerante cuando el destino sale del árbol. **Sin ellas se comporta igual que antes** |
| `precalculo/audita_todo.sh` | paso 3 nuevo, dentro del bucle por capítulo y **fuera** de `--rapido` |
| `PLAN_Mejora_Capitulo1.md` | este anexo, la pregunta 4 cerrada y un criterio transversal nuevo |

Ninguna cifra del capítulo cambia y el HTML publicado sale **byte a byte idéntico** de todo
esto: el arnés no escribe en el árbol de verdad, y se comprueba al final de cada pasada.

---
---

# Anexo T2.1 — Los dos ρ, y la advertencia que pasó a ser un cociente

**Ejecutada:** 2026-08-06 · **Resultado:** cerrada en verde · **Alcance real:** M *(se preveía S; subió al elegir las dos opciones)*
**Decisión de Javier:** hacer **(a) y (b)** y publicar la discrepancia

## T2.1.a · Lo que había, y por qué la pregunta estaba mal planteada

El titular del módulo 5 dice que 1 121 municipios informan como 64.52155 y no dice con qué ρ.
El plan lo llamaba «el ρ escondido». **T1.1.b ya había demostrado que no hay ninguno:** ese
64.52155 es `n · (ee_iid/ee_bloques)²`, el cociente de los dos remuestreos del módulo 4, y la
equicorrelación no interviene en ningún paso. Así que la tarea no era destapar un ρ sino
**elegir cuál publicar** — y se publican los dos.

| | ρ | n efectivo | Qué es |
|---|---:|---:|---|
| **Implícito** | 0.0146197 | 64.52155 | El que la equicorrelación *necesitaría*. Se despeja de la fórmula, así que reproduce el titular por construcción. **No estima nada** |
| **Medido** | 0.0021243 | 331.73877 | La correlación media entre pares, sobre el mapa, con el método del ejercicio 3 |

Se separan un factor **6.88226** en ρ y **5.14152** en información.

## T2.1.b · Por qué hacer las dos era mejor que elegir una

El capítulo **ya afirmaba** —y `audita_texto_cap1.py` lo exige como `AFIRMACIÓN`— que
*«la fórmula supone equicorrelación, y eso es falso en el espacio»*. Publicar solo el implícito
habría sido nombrar un ρ que existe únicamente bajo un supuesto que el propio capítulo llama
falso. Con los dos, **esa advertencia deja de ser una afirmación y pasa a ser un cociente**, que
es el movimiento que este capítulo lleva premiando desde T1.2.

Y el correlograma explica el mecanismo sin que haya que creérselo:

| banda | I de Moran | pares | islas |
|---|---:|---:|---:|
| 0–25 km | **0.28820** | 3 482 | 156 |
| 25–50 km | 0.28707 | 9 756 | 47 |
| 50–100 km | 0.18104 | 31 482 | 13 |
| 100–175 km | 0.07582 | 63 507 | 3 |
| 175–300 km | **−0.05289** | 127 896 | 2 |
| 300–500 km | **−0.05491** | 184 612 | 2 |
| 500–800 km | 0.02491 | 152 571 | 0 |

Entre vecinos la correlación es **0.28820**; a media distancia se vuelve **negativa**, y ahí
están **312 508 de los 573 306** pares. La equicorrelación obliga a resumir todo eso en *un*
número y el promedio se hunde hacia cero. Por eso el ρ que haría falta es 6.9 veces el que se
mide: **no es que la medición falle, es que el supuesto no cabe en el dato.**

## T2.1.c · El simulador: el rombo deja de flotar

T1.1 dejó el rombo de Colombia sin curva que lo tocara, y la intro pedía al estudiante
*«busca el ρ cuya curva pase por él»*. Ahora hay **dos curvas fijas**: la del ρ implícito, que
pasa por el rombo porque de ahí se despeja, y la del medido, que pasa **5.14 veces por encima**.
La distancia entre las dos es la lección, dibujada.

La guarda de ejecución creció con dos afirmaciones nuevas, las dos leídas de **lo dibujado**:
que la curva implícita pasa por el rombo y que **la del medido no**. La segunda existe porque
la prosa publica una discrepancia: si algún día coincidieran, el texto estaría describiendo
algo que ya no pasa.

> **Y de paso se retiraron dos índices mágicos.** `cuadra()` leía `datasets[0]` y `datasets[3]`
> a mano. Meter series nuevas entre ellas es exactamente el descuadre silencioso de T1.2, así
> que cada serie pasó a tener nombre en el código antes de añadir ninguna.

## T2.1.d · La auditoría, y la convención que no se podía esquivar

`audita_cap1.py` rehace el correlograma **desde el GeoPackage original** con geopandas y
libpysal, sin pasar por R. Los pares y las islas coinciden **exactamente**, banda a banda. Las
I no — y no por un error:

> `spdep::moran.test` con `zero.policy = TRUE` toma **n = unidades con vecinos** y `esda.Moran`
> toma **n = todas**. Es la discrepancia `moran_islas` que el módulo 7 ya declara. En la banda
> de 0 a 25 km son **156 islas de 1 121**, así que aquí no cambia la cuarta cifra: cambia la
> segunda (0.28820 contra 0.33479).

Las dos convenciones se convierten exactamente una en otra —`I_esda = I_spdep · n/(n − islas)`—
y **por eso el capítulo publica `islas` por banda**. Sin ese entero esta comprobación sería
imposible y habría que declararla saltada; con él, la conversión cuadra con un error de
**5e-11** y la auditoría es real.

## T2.1.e · Las tolerancias, medidas y no estimadas

Tres comprobaciones dieron rojo al primer intento, y ninguna era un defecto: era el redondeo a
diez decimales **amplificado**. El ρ medido vale 0.0021, así que 5e-11 en la undécima cifra es
un error relativo de 2e-8, y multiplicado por 331 de n_eff son cuatro millonésimas.

| | residuo medido | tolerancia | margen |
|---|---:|---:|---:|
| despeje del implícito | 4.3e-11 | 1e-9 | 23× |
| vuelta al n_eff del titular | 1.8e-07 | 1e-5 | 56× |
| razón entre los dos ρ | 1.4e-07 | 1e-5 | 72× |
| n_eff con el ρ medido | 4.0e-06 | 1e-3 | 247× |

Escribir 1e-6 en la última habría puesto **rojo un capítulo correcto**, que es la forma más
rápida de enseñar a ignorar el informe.

## T2.1.f · Guardas e inyección

| Capa | Qué vigila | Inyecciones |
|---|---|---:|
| **Compilación** | que el implícito reproduzca el titular, que supere al medido, que las bandas que la prosa nombra por su posición sigan ahí, que no dejen huecos y que la I siga siendo negativa a media distancia | **6** |
| **Ejecución** | que la curva implícita pase por el rombo y la del medido **no** | *(recorrida en el navegador)* |
| **Auditoría** | los dos ρ, las siete bandas rehechas desde el GeoPackage, pares, islas, el promedio ponderado y las cuatro cifras derivadas | **10** |

**16 de 16 cazadas**, todas con diagnóstico y ninguna por excepción. Las guardas de compilación
pasan de 41 a **47**, y el arnés de T1.3.n las recogió **solas**: el inventario por `ast` no hay
que actualizarlo.

## T2.1.g · Verificación

**En el navegador**, 31 posiciones del deslizador de las 301: **31 huellas de píxeles
distintas**, la curva implícita **no se mueve** con el control, la lectura estrena tres filas y
**0 errores de consola**. Y las dos afirmaciones del gráfico, medidas:

```
curva del rho implícito en n = 1 121 : 64.5215454   (rombo: 64.5215456 · dif 1.8e-7)
curva del rho medido    en n = 1 121 : 331.7387760  (5.1415× el rombo)
```

**Los auditores:** `audita_cap1.py` pasa de 901 a **937** comprobaciones, 0 fallos;
`audita_texto_cap1.py` sigue en **141**, 0 fallos — todas las cifras nuevas de la prosa salen
del JSON.

## T2.1.h · Criterios del plan, uno a uno

| Criterio | Estado |
|---|---|
| Elegida y declarada la opción (a) o (b) | **las dos**, por decisión de Javier |
| El módulo publica el ρ y su método, diciendo si es estimación o retro-transformación | sí, y lo dice con esas palabras |
| Verificado que es el mismo ρ del titular y del ejercicio 3 | ya cerrado en T1.1.b: **no lo es**, y queda declarado |
| Con (a): el ρ publicado reproduce 64.52155 · con (b): la discrepancia se publica | **las dos**, y las dos con guarda |
| El rombo cae **sobre** la curva en el ρ publicado, y la guarda de ejecución lo comprueba | sí, más la afirmación simétrica de que el medido **no** pasa |

---
---

# Anexo T2.2 — El puente que faltaba tenía tres tramos, y uno sobraba

**Ejecutada:** 2026-08-07 · **Resultado:** cerrada en verde · **Fallos encontrados:** 4
**Hallazgos que cambian el plan:** 3

## T2.2.a · Lo que había, medido antes de tocar nada

El plan describía P2 como tres cosas que faltaban. Medidas una a una, el reparto era otro:

| Lo que el plan decía que faltaba | Lo que había de verdad |
|---|---|
| «no se muestra que 0.77880 = e^(−1/4)» | La cifra **sí se publicaba** (`:707`), y salía del JSON. Lo que faltaba era **decir qué es h**: el capítulo escribía ρ(h) = e^(−h/φ) sin declarar en qué se mide h, así que el lector no podía llegar al e^(−1/4) por su cuenta |
| «no se muestra el puente de φ = 4 al factor 7.85798» | Cierto, y era el tramo más largo |
| «ni que ‹unas 61.7› es 7.85798²» | **El 61.7 no era una cifra sin derivación: era una cifra sin origen.** Se calculaba en el ensamblador, `n(r4['factor'] ** 2, 1)`, y no existía en ningún JSON |

Esa última línea es la que convirtió la tarea de S en M.

## T2.2.b · Hallazgo 1: el 61.7 pasaba el auditor por coincidencia

D10 dice «ninguna cifra a mano», y `audita_texto_cap1.py` existe para hacerlo cumplir: toda
cifra de la prosa tiene que estar en el JSON. El 61.7 llevaba meses violándolo **con el
auditor en verde**. Medido antes de tocar nada:

```
tamaño del índice de conocidos: 114 307
  '61.7'      en el índice: True
  '61.75'     en el índice: False
  '61.748'    en el índice: False
  '7.85798'   en el índice: True
  '0.77880'   en el índice: True
```

Es decir: **sobrevivía por tener un solo decimal**. Con cinco habría caído. Y ese es
exactamente el régimen que `mide_punto_ciego.py` midió como el peor —con un decimal se cuela
el 63 % de las perturbaciones de un dígito, frente al 4,63 % con cinco—, el mismo que T0.2
destapó al escribir `1 121` en vez de `1121.00000`.

**La lección, que vale para las cuatro tareas que quedan:** el auditor de prosa no comprueba
que una cifra *venga* del JSON. Comprueba que *exista* en un índice enorme de valores y
cocientes derivados. Con pocos decimales, eso no es una comprobación: es una lotería que casi
siempre sale bien. `audita_cap1.py`, que recalcula, sí lo habría visto — pero nadie le había
dicho que mirara ahí.

## T2.2.c · Hallazgo 2: el capítulo llamaba «la información» a dos números distintos

Al escribir el segundo tramo del puente —de la correlación al número— aparece que hay **dos**
cocientes, y que el capítulo usaba la palabra del uno para el valor del otro:

```
efecto de diseño   n/n_eff  = 49.63003     Var(Z̄) real  /  (σ²/n)
factor²                     = 61.74778     Var(Z̄) real  /  varianza DECLARADA
                              1.24416 veces de diferencia
```

Los dos son correctos; miden cosas distintas. El primero es cuánto se ensancha la varianza
**verdadera** de la media. El segundo es cuánto se queda corta la que **el programa imprime**,
y es mayor porque hay una segunda mordida: `s²` también se encoge con la correlación.

```
E[s²] = σ² · (n/(n−1)) · (1 − 1/n_eff) = 0.80929 · σ²
```

**Por qué importa y no es una sutileza.** El módulo 4 decía «la información se divide por unas
61.7». El ejercicio 4 del mismo capítulo publica que *n* efectivo pasa de 256 a **5.15817**,
que es dividir por **49.63**. Un estudiante que hiciera 256/61.7 = 4.15 no llegaba a la cifra
que el capítulo publica dos módulos después, y no tenía cómo saber por qué. Es la cuarta vez
en este plan que el defecto vive **en el hueco entre dos piezas correctas** —como T1.2, T1.3 y
P12b—, y otra vez ningún auditor podía verlo: cada JSON era correcto por su cuenta.

## T2.2.d · La decisión, consultada antes de tocar R

Tres salidas, con su coste:

| | Qué hace | Coste |
|---|---|---|
| **(a)** | Publicar los dos con nombre propio y explicar la brecha | 5 cifras nuevas en R, un recuadro reescrito |
| (b) | Dejar el 61.74778 pero dejar de llamarlo «la información» | Una frase. El lector sigue sin poder llegar al 5.15817 |
| (c) | Sustituirlo por 49.63003 | Tira la medida de cuánto miente el software, que es la tesis del módulo |

**Javier eligió (a) el 2026-08-07.** Y resultó ser la barata en la moneda que importa: el
49.63003 es **el puente literal al módulo 5**, así que T2.2 deja **P3 medio pavimentada** sin
haberla tocado.

## T2.2.e · El arreglo

**En R** (`genera_cap1.R`, bloque D.1). Cinco campos nuevos por alcance y tres copias de
cierre, más la escala declarada:

| Campo | Qué es | Por qué |
|---|---|---|
| `escala_h` | «distancia euclídea entre centros de celda, medida en pasos de retícula» | Vivía solo en un comentario de R. El capítulo lo publica ahora en negrita |
| `sigma` | 1 | La varianza marginal, que el módulo escribía sin declarar |
| `rho_diagonal` | e^(−√2/φ) | **Lo único que hace comprobable la escala.** Con adyacencia en vez de distancia valdría lo mismo que `rho_vecino`; publicando las dos, el lector ve que h es distancia |
| `efecto_diseno` | 1'R1/n = n/n_eff | El primer cociente |
| `inflacion_varianza` | factor² | El segundo, ya no calculado en el ensamblador |
| `s2_esperada` | σ²(n/(n−1))(1−1/n_eff) | La identidad que explica la brecha |
| `s2_medida` | media de las s² del Monte Carlo | Para no afirmar la identidad: medirla |

Y un **control** que para R si las dos últimas se separan más del 6 %. La tolerancia está
medida, no elegida: se simuló antes de escribirla y el peor de los siete alcances es **2,03 %
en φ = 8**, así que 0,06 —la misma del control del e.e. que ya existía— deja holgura de tres
veces sin volverse decorativa.

**En la prosa** (`ensambla_cap1.py`, MOD4). El párrafo de apertura declara el modelo entero
—σ² = 1, ρ(h) = e^(−h/φ), h en pasos de retícula, y el *jitter* de 10⁻⁹—. Precisión sobre el
*jitter*, porque la distinción es justo la de la familia P: **no era una cifra escondida**,
`inferencia.jitter` lleva desde siempre en el JSON y el capítulo lo incrusta entero. Lo que
pasaba es que **la prosa no lo decía**, así que estaba publicado y no dicho, que para un
lector es lo mismo que no estar. Y el recuadro pasa de un párrafo a **tres pasos**:

```
Uno  · de φ a la correlación        e^(−1/4) = 0.77880 · diagonal 0.70219
Dos  · al efecto de diseño          49.63003 → las 256 informan como 5.15817
Tres · y el software declara menos  E[s²] = 0.80929 σ² → 61.74778 = 7.85798²
```

**Una cosa que el recuadro NO dice, a propósito.** La descomposición
`inflación ≈ efecto × (1/E[s²])` no es exacta: da 1.24416 frente a 1.23564, un 0,69 % de
separación —hueco de Jensen, porque `ee_ingenuo` promedia *s* y no *s²*, más el ruido de Monte
Carlo—. Así que la prosa dice «no son el mismo número porque no miden lo mismo» y **no escribe
un `=` entre ellos**. Publicar una identidad que no cierra a la quinta cifra, en un capítulo
que audita a cinco decimales, habría sido peor que no publicarla.

## T2.2.f · Hallazgo 3: la desigualdad no vale para los siete alcances

La primera guarda que escribí decía «la inflación supera siempre al efecto de diseño». Antes
de darla por buena la medí sobre los siete alcances, y es falsa:

```
  phi       efecto    inflacion  infl>efec    s2_esp
    0      1.00000      0.98354      False   1.00000
  0.5      1.89274      1.89065      False   0.99650
    1      5.59548      5.90224       True   0.98198
    4     49.63003     61.74778       True   0.80929
   16    156.78425    419.82759       True   0.38908
```

En φ = 0 y 0.5 la `s²` casi no se encoge —0.99650 de σ²— y quien decide el signo es el ruido
de Monte Carlo. La guarda quedó acotada al φ que el módulo destaca, que es el único alcance
del que la prosa afirma la desigualdad. **Escribirla para los siete habría puesto rojo un
capítulo correcto**, que es la forma más rápida de enseñar a ignorar el informe — la misma
lección que T2.1.e ya había pagado con las tolerancias.

## T2.2.g · Hallazgo 4: el arnés de guardas leía mal los paros duros

Este no es del capítulo: es del arnés que T1.3.n montó, y salió porque T2.2 fue la primera
tarea en inyectar contra un `sys.exit`.

El ensamblador para de dos formas. `problemas.append(…)` acumula y sigue; `sys.exit("PARADO:
…")` no puede seguir y para en seco. `prueba_ensambla_cap1.py` ejecuta el objetivo **en
proceso** —con `runpy`, porque lo necesita para trazar la cobertura con `sys.settrace`— y por
eso tiene que reconstruir a mano el código de salida:

```python
except SystemExit as e:
    codigo = e.code if isinstance(e.code, int) else 0
```

`sys.exit("mensaje")` lleva una **cadena** en `e.code`. Python sale con código 1 y escribe el
mensaje por stderr; el arnés lo leía como **0** y cantaba `[ SE COLÓ ]` de un defecto que el
ensamblador había parado en seco, con su diagnóstico y todo. Y había un segundo tramo del
mismo agujero: `inventario()` solo contaba `problemas.append`, así que **los 7 paros duros del
ensamblador no estaban inventariados** — ni se medía su cobertura ni una guarda nueva de esa
clase aparecía sola en «sin ver disparar», que es justo lo que el criterio transversal de
T1.3.n promete.

Arreglado en tres sitios: el `DRIVER` distingue los tres casos de `e.code` y **imprime** el
mensaje que antes se tragaba; `males()` reconoce `PARADO:` como diagnóstico, para que un paro
en seco cuente como cazado y no como `REVIENTA`; e `inventario()` cuenta también los
`sys.exit` con texto, dejando fuera el `sys.exit(main())` del final. Resultado:

```
antes:  53 guardas inventariadas · 53 de 54 defectos cazados
ahora:  60 guardas inventariadas · 54 de 54 defectos cazados
        y 6 paros duros preexistentes SIN CUBRIR, ahora visibles
```

Los 6 son `:85` (falta un archivo de entrada), cuatro de `region()` y uno de `GEOMAPAS`. No se
cubren en T2.2 —es un agujero anterior a esta tarea— pero **se dejan en la lista impresa en
vez de en ninguna parte**, y en la pregunta abierta 7. `region()` es justo lo que T4.1 va a
tocar de lleno.

**Y una comprobación que hice antes de generalizar el susto:** el mismo fallo *no* está en
`prueba_auditor_cap1/2/3.py` ni en `prueba_texto.py`. Esos leen `res.returncode` del
subproceso, donde el 1 llega intacto. El defecto era **estructural y único** del arnés que
ejecuta en proceso.

## T2.2.h · Un índice mágico menos

`r4 = inf["rejilla"][4]`. Todas las cifras del módulo 4 salían de ahí, y con un índice fijo
reordenar `PHIS` en R la habría dejado apuntando a otro alcance con la prosa leyéndose
perfectamente. Es el defecto de T1.2 en su versión de compilación, y T2.1 ya había retirado
dos iguales de `cuadra()`. Ahora busca por φ.

Con `next(…)` a secas, una rejilla sin φ = 4 habría reventado con un `StopIteration` pelado
—código 1 sin una línea de diagnóstico, que es el error que la inyección de T1.3.i cazó dos
veces—, así que para diciendo qué falta y qué alcances quedan. Es la única guarda nueva de
T2.2 que es un paro duro, y por eso hizo falta arreglar el arnés antes de poder probarla.

## T2.2.i · Guardas e inyección

| Capa | Qué vigila | Inyecciones |
|---|---|---:|
| **Compilación** | que las cinco cifras del puente estén en las siete filas, que la inflación sea factor², que el efecto de diseño sea n/n_eff, que en φ = 4 la desigualdad se sostenga, que E[s²] < σ², que σ² siga siendo 1, que la escala esté declarada, y que la fila de φ = 4 exista | **8** |
| **Auditoría** | ρ diagonal contra e^(−√2/φ), el efecto de diseño **rehecho desde la matriz de correlación** con la escala que el capítulo declara, la inflación contra factor², E[s²] contra su fórmula y contra su medida, y las tres copias de cierre | **11** |
| **Ejecución** | mapa, lectura y mando de acuerdo en las 7 posiciones | *(recorrida en el navegador)* |

**19 de 19 cazadas**, todas con diagnóstico. Los totales de los dos arneses: `54 de 54` en el
del ensamblador y `84 de 84` en el del auditor.

La inyección que más justifica su coste es **«n_eff y el efecto de diseño se mueven juntos y
siguen cuadrando»**: mueve las dos cifras a la vez dejándolas consistentes entre sí. Contra
una comprobación que solo dividiera `n/n_eff` pasaría limpia, porque la división sigue
cuadrando. Solo la reconstrucción de `1'R1` desde cero puede verla — y por eso el auditor
levanta la matriz de 256×256 con numpy en vez de fiarse del JSON.

## T2.2.j · Verificación

**Las cinco cuentas, rehechas a mano** (el plan pedía tres):

```
e^(-1/4)                              0.77880  =  0.77880   sí
e^(-sqrt(2)/4)                        0.70219  =  0.70219   sí
7.857975732^2                        61.74778  = 61.74778   sí
256 / 5.1581674595                   49.63003  = 49.63003   sí
(256/255)(1 - 1/5.1581674595)         0.80929  =  0.80929   sí
```

**En el navegador**, las **7 posiciones** del deslizador: en las 7 el φ del mapa es el de la
lectura, las 7 leen del JSON las cuatro cifras que muestran, y salen **7 huellas de píxeles
distintas**. El criterio de T1.3.f —**al volver**, no solo al llegar— también: elegido φ = 16,
salida al módulo 6 y vuelta, el mando sigue en la posición 6 y mapa, lectura y control siguen
de acuerdo. **0 errores de consola**, **16 fórmulas KaTeX renderizadas y 0 errores** en el
recuadro nuevo.

**Los auditores.** `audita_cap1.py` pasa de 937 a **986** comprobaciones;
`audita_texto_cap1.py` sigue en **141** — y esta vez el 141 significa algo más que antes,
porque la cifra que lo violaba en silencio ya no está. `audita_todo.sh --rapido` cierra con
**ARNÉS COMPLETO EN VERDE** y código 0:

| Auditor | Comprobaciones | Fallos |
|---|---:|---:|
| `audita_cap1.py` | **986** *(eran 937)* | 0 (3 saltadas declaradas) |
| `audita_cap2.py` | 445 | 0 (2 saltadas) |
| `audita_cap3.py` | 356 | 0 (2 saltadas) |
| `audita_texto_cap1.py` | 141 | 0 |
| `audita_texto_cap2.py` | 129 | 0 |
| `audita_texto_cap3.py` | 130 | 0 |
| **Total** | **2 187** | **0** |

Los capítulos 2 y 3 salen con las mismas cuentas que en el Checkpoint 1, que es lo esperable:
T2.2 no toca la plantilla ni el motor, así que no se re-ensamblaron.

## T2.2.k · Criterios del plan, uno a uno

| Criterio | Estado |
|---|---|
| El módulo declara la escala de h y el modelo de correlación completo | sí, y también el *jitter*, que no estaba pedido |
| Se muestra que 0.77880 = e^(−1/4) y que 61.7 = 7.85798² | sí, y el 61.7 pasa a **61.74778**: cinco decimales en vez de uno |
| Toda cifra nueva viene del JSON | sí — **y la vieja también**, que era el defecto de verdad |
| *(añadido)* los dos cocientes publicados con nombre propio | sí, por decisión de Javier |
| *(añadido)* ρ diagonal, para que la escala sea comprobable | sí |
| *(añadido)* índice mágico retirado | sí |
| *(añadido)* las tres capas probadas por inyección | 19 de 19 |

## T2.2.l · Cambios en disco

| Archivo | Qué |
|---|---|
| `precalculo/genera_cap1.R` | 5 campos por alcance, 3 copias de cierre, `escala_h`, `sigma` y un control nuevo |
| `precalculo/ensambla_cap1.py` | prosa del módulo 4, 2 filas en la lectura, 6 guardas nuevas + 1 paro duro, índice mágico retirado |
| `precalculo/audita_cap1.py` | la matriz de correlación rehecha con numpy y 7 familias de comprobación nuevas |
| `precalculo/prueba_auditor_cap1.py` | 11 inyecciones |
| `precalculo/prueba_ensambla_cap1.py` | 8 inyecciones · `inventario()`, `DRIVER` y `males()` arreglados |
| `salidas/cap1_datos.json` | 38 700 → 40 262 B · **40 claves nuevas, 0 perdidas**, y el único valor movido es `meta.generado` |
| `salidas/cap1_mapas.json` | regenerado, **mismo tamaño y sin marca de tiempo dentro** |
| `Htmls_Espacial/capitulo-1-datos-espaciales.html` | 558 908 → 562 974 B (+4 066) · **6 bloques de diff, los 6 previstos** · 550 KB, el 79 % de la alarma de 700 KB |

Y en la segunda ronda (T2.2.n):

| Archivo | Qué |
|---|---|
| `precalculo/sin_aritmetica.py` | **nuevo** · el lint de la causa, con su autoprueba |
| `precalculo/audita_todo.sh` | un paso más, antes de los auditores de prosa |
| `precalculo/audita_texto_base.py` | `self.brutos` y el triaje de las cifras de pocos decimales |
| `precalculo/genera_cap2.R` | `formatos$gpkg$razon_sobre_shp`, que faltaba |
| `precalculo/ensambla_cap2.py` | la división retirada de la prosa |
| `salidas/cap2_datos.json` | **1 clave nueva, 0 perdidas**, solo `meta.generado` movido |
| `Htmls_Espacial/capitulo-2-crs-georreferenciacion.html` | **1 bloque de diff**, el JSON incrustado · la prosa **no cambia** |

`genera_soluciones.R` no se tocó y `cap1_soluciones.json` no se regeneró: T2.2 no cambia
ningún ejercicio.

**Coste:** R 1 min 12 s · ensamblador 0,05 s · `audita_cap1.py` 14,7 s ·
`prueba_ensambla_cap1.py` 3,2 s · `prueba_auditor_cap1.py` **18 min 26 s** (84 inyecciones ×
un auditor que ahora hace 986 comprobaciones). Ese último es el que empieza a pesar y conviene
tenerlo presente en T2.3 y T2.5, que también tocan R.

## T2.2.n · Segunda ronda: las 135 cifras de pocos decimales *(mismo día, a petición de Javier)*

T2.2 cerró con una duda escrita: si el 61.7 llevaba meses violando D10 con los dos auditores
en verde, ¿cuántas más hay? Se midió, y **135** en los tres capítulos. Un recuento no es una
pista, así que se triaron.

**El triaje.** Para cada cifra de pocos decimales: ¿hay algún valor **bruto** del JSON que,
redondeado a los decimales publicados, dé exactamente esta cifra? El índice de `cifras()`
mezcla los valores de R con razones y diferencias derivadas —a propósito, porque el texto
compara todo el rato—, y es esa mezcla la que deja pasar un número de un decimal. Preguntando
solo contra los valores brutos, la pregunta se vuelve estricta:

| Capítulo | Pocos decimales | Redondean un valor del JSON | Solo algo derivado |
|---|---:|---:|---:|
| 1 | 13 | 10 | **3** |
| 2 | 50 | 48 | **2** |
| 3 | 72 | 70 | **2** |
| **Total** | **135** | **128** | **7** |

**De 135 renglones a 7.** Y de los 7, cinco son artefactos del extractor: `3.13`, `3.8` y
`9.5` son trozos de «GEOS 3.13.0», «GDAL 3.8.5» y «PROJ 9.5.1», y `10.1111` y `9713.2016` son
trozos del DOI `10.1111/j.1740-9713.2016.00960.x`. Se dejan sin declarar como estructurales a
propósito: meter «3.8» o «9.5» en la lista blanca los haría **permanentemente inauditables**, y
un 3.8 sí puede ser un resultado mañana. Quedan dos de verdad, y una era un defecto.

**El defecto: `1.070×` en el capítulo 2.** El mismo del 61.7, calculado en el ensamblador:

```python
{firma(n(fo['gpkg']['bytes'] / _sh['bytes'], 3), '×')} lo que el shapefile. El GeoJSON
es el más pesado de los tres, {firma(n(fo['geojson']['razon_sobre_shp'], 3), '×')} el
```

La línea de al lado hace lo correcto. R publicaba `razon_sobre_shp` para el GeoJSON y **no
para el GeoPackage**, así que el ensamblador dividía a mano. Cerrado publicándolo en
`genera_cap2.R`: el JSON gana **una clave**, no pierde ninguna, y **la prosa no cambia** —
`n(1.0701353711, 3)` da exactamente el `1.070` que producía la división—. Un solo bloque de
diff en el capítulo 2, y es el JSON incrustado.

**El otro: `111.32` en el capítulo 2**, no cerrado y declarado. Es la conversión de kilómetros
a grados en el ecuador, y aparece en dos **enunciados de ejercicio** como parámetro que el
estudiante teclea, no como resultado. No es un defecto de esta familia —no lo calcula nadie—
pero es **una constante física sin fuente**, que es P6 en el capítulo 2. Se anota; cerrarlo es
citar de dónde sale.

**Y la comprobación que hace innecesario repetir esto: `sin_aritmetica.py`.** El triaje mira el
resultado; esto mira **la causa**, y con `ast` la detección es exacta —o hay aritmética dentro
de un formateador, o no—: sin índice, sin azar, sin tolerancia. Barre los tres ensambladores,
los **descubre solos** por `glob` (así el capítulo 4 lo hereda sin tocar nada) y trae su
autoprueba dentro:

```
  OK   ensambla_cap1.py   0 en la prosa · 0 exenta(s) en bloques de código
  OK   ensambla_cap2.py   0 en la prosa · 1 exenta(s) en bloques de código
  OK   ensambla_cap3.py   0 en la prosa · 0 exenta(s) en bloques de código
  OK   control · ensambla_cap1.py sale limpio sin inyectar nada
  OK   «una división en la prosa» → cazado
  OK   «un cuadrado en la prosa» → cazado
  OK   «la misma aritmética DENTRO de un bloque de código» → exento
```

**La exención es de fondo, no una comodidad.** Dentro de un bloque de código el ensamblador
**sí puede** calcular: ahí la línea `#>` no es una afirmación del autor sino la salida que el
lector va a obtener, y `verifica_bloques.py` **ejecuta de verdad** los 67 bloques de los tres
capítulos y contrasta **297 de 297** cifras anunciadas contra la salida real. Eso es más
fuerte que el JSON, no más flojo. En la prosa no hay nada que ejecute, y por eso ahí la regla
es absoluta. Las exenciones se cuentan y se imprimen, para que no sean tácitas — hoy es una,
el `k45^2` del Mercator del capítulo 2.

**Dos decisiones de sitio, y las dos se movieron sobre la marcha.** La comprobación empezó
dentro de `audita_texto_base.py`, y de ahí salió por dos razones: mira el **fuente** del
ensamblador y no el HTML publicado, y el arnés de los auditores de prosa solo sabe envenenar
el HTML, así que la comprobación habría nacido **sin poder inyectarse**. El siguiente sitio
—una guarda de compilación dentro de cada `ensambla_capN.py`— era inyectable pero exigía **tres
copias** de la misma comprobación, cinco cuando lleguen los capítulos 4 y 5, que es la
duplicación que este proyecto lleva dos tareas evitando. Guion propio con autoprueba dentro:
uno solo, inyectable y descubierto por `glob`.

Entra en `audita_todo.sh` **antes** de los auditores de prosa, y cuesta 0,1 s.

**Lo que da confianza de que no es un juguete:** se le reinyectó el defecto histórico real
—la línea tal y como estaba en `ensambla_cap2.py`— y lo cazó con su archivo y su línea.

## T2.2.m · Lo que deja abierto

1. ~~**Los 6 paros duros sin inyectar**~~ → **especificados como T2.2b**, con las seis
   sustituciones exactas y el tipo `falta` que hay que añadirle al arnés. Escrito para poder
   ejecutarse sin el contexto de esta sesión.
2. **T3.2 hereda las cifras.** El panel 2 de la Fase 3 ya no tiene que cerrar P2: tiene que
   poner el álgebra —desarrollar `1'R1` hasta el 49.63003 y demostrar
   `E[s²] = σ²(n/(n−1))(1−1/n_eff)`, que T2.2 publica y mide pero no deriva—.
3. **P3 queda medio pavimentada.** El 49.63003 es el puente al `n_eff` del módulo 5, y ahora
   está dicho con esas palabras en el módulo 4.
4. **La duda que deja el hallazgo 1**, y no es pequeña: si el 61.7 llevaba meses violando D10
   con los dos auditores en verde, ¿cuántas más hay? El auditor de prosa ya las cuenta —pero
   no dice cuáles ni las contrasta—, así que se midió antes de cerrar la tarea:

   | Capítulo | Cifras con menos de 5 decimales en la prosa |
   |---|---:|
   | 1 | **13** |
   | 2 | **50** |
   | 3 | **72** |
   | **Total** | **135** |

   ✅ **HECHO el mismo día, a petición de Javier.** No hizo falta mirar 135 renglones: el
   triaje contra los valores **brutos** del JSON deja **7**, de los que cinco son trozos de
   versiones y de un DOI. De los dos reales, uno era **el mismo defecto del 61.7 en el
   capítulo 2** —`1.070×`, dividido en el ensamblador— y está cerrado; el otro, `111.32`, es
   una constante física sin fuente en dos enunciados, y se declara. Y para no repetir esto
   nunca más, `sin_aritmetica.py` mira la **causa** con `ast`, barre los tres ensambladores y
   se autoprueba. Detalle en el Anexo T2.2.n.

---

# Anexo T2.7 — El mapa que le faltaba al módulo 7

**Ejecutada:** 2026-08-10 · **Resultado:** cerrada en verde, los 15 pasos
**Hallazgos que cambian el plan:** 2 · **Umbrales subidos deliberadamente:** 1

> El encargo de esta tarea —escrito el 2026-08-09 y sin ejecutar hasta hoy— se conserva
> íntegro en los apartados T2.7.a a T2.7.f. Lo que se hizo, y lo que se encontró al hacerlo,
> va después, de T2.7.g en adelante. Se dejan los dos porque el encargo acertó en el
> diagnóstico y falló en un detalle que resultó ser el más instructivo de la tarea.

---

## T2.7.a · Qué falta y por qué importa

El módulo 7 publica el error de agregación más caro del capítulo: sumar las muertes de
`nc` sobre una rejilla de 100 rectángulos emparejando por «se tocan» da **2 621** donde
había **667**, un **292,95 %** más. La causa está **dicha**:

> «Un condado toca cuatro rectángulos y aporta su conteo *entero* a los cuatro, porque
> "intersecta" es cierto cuatro veces.»

Y no está **mostrada**. Es una frase que se entiende de golpe con una imagen y a medias con
un párrafo — el hueco de comprensión más claro que dejó T2.3. La pregunta al cerrar un
módulo no es «¿cabe?» sino «¿qué quedó dicho y no mostrado?».

## T2.7.b · El hallazgo técnico, medido antes de encargar la tarea

**`geo_poligonos()` no sabe dibujar líneas hoy.** Se comprobaron las tres vías aparentes y
ninguna sirve tal cual:

| Vía | Qué es en realidad | ¿Sirve? |
|---|---|---|
| `capas =` | varias **variables sobre la misma geometría** (selector de variable, `geo.R:210`) | ❌ no es una segunda geometría |
| `superpuestos =` | capa de **puntos**, `modo` ∈ {`simbolo`, `densidad`} (`geo.R:310`) | ❌ una rejilla no son puntos |
| `geo_puntos(lineas = )` | polilíneas de fondo — las calles de Soho (`geo.R:360`, `402`) | ⚠️ existe, pero está en `geo_puntos`, no en `geo_poligonos` |

**Conclusión: la tarea es una extensión de `geo.R`,** no un mapa más. Hay que llevar a
`geo_poligonos()` la capacidad de polilíneas que ya tiene `geo_puntos()`, replicando su
cuantización —contra la **misma caja** del mapa, que es lo que garantiza que la rejilla
caiga encima de los condados y no desplazada.

**Y `geo.R` es compartido por los tres capítulos.** De ahí las dos condiciones duras:

1. **Retrocompatible**: quien no pase el argumento nuevo obtiene exactamente el JSON de hoy.
2. **`audita_todo.sh` entero en verde**, no solo el capítulo 1. Los capítulos 2 y 3 usan
   `geo.R` y tienen sus propios auditores e inyecciones.

Además hay que enseñar al navegador a pintarlo: el componente vive en
`plantilla/plantilla-capitulo.html`.

## T2.7.c · Lo que ya está hecho y no hay que rehacer

- **El dato.** `D$agregacion_soporte$nc` ya trae `total_condados`, `n_celdas`,
  `total_rectangulos`, `inflacion_pct` y `total_por_area`, medidos en R y recalculados de
  forma independiente en `audita_cap1.py` (sección «2b bis»).
- **La rejilla.** Es `st_make_grid(st_transform(nc, 2264))` — 10×10 sobre el bbox, las
  mismas 100 celdas que ya usa el precálculo y que el auditor reconstruye a mano en Python.
- **La prosa.** El módulo 7 ya tiene el párrafo y el bloque ejecutable. Solo falta el mapa.

## T2.7.d · Idea de diseño, para que el mapa demuestre y no decore

Un mapa bonito de rejilla sobre condados no enseña nada por sí solo. Lo que convierte la
cifra en evidencia es **resaltar un condado concreto y las celdas que toca**: se ve que cae
en cuatro, y que su conteo entero se suma cuatro veces. Sin ese resalte, el lector ve dos
capas superpuestas y sigue sin ver el doble conteo.

Vale la pena considerar un segundo estado del mismo mapa con el reparto por área, donde el
condado aporta a cada celda **una fracción** — es el contraste que el módulo ya explica con
`st_interpolate_aw` y que devuelve 667 exactas.

## T2.7.e · Criterios de aceptación

- [ ] `precalculo/audita_todo.sh` en verde, **los 15 pasos** (los tres capítulos).
- [ ] `geo.R` retrocompatible: los mapas existentes producen el mismo JSON byte a byte.
- [ ] Ninguna cifra a mano (D10). Si el mapa estrena un número, va primero a
      `genera_cap1.R` y `audita_cap1.py` lo recalcula.
- [ ] El mapa se registra con su **JSON literal**, no con una función: es la única forma en
      que `audita_texto_base.geomapas()` puede comprobarle cortes, `n` y peso.
- [ ] `<canvas>` con `aria-label` y `role="img"` — lo exige la guarda de salida del
      ensamblador y lo comprueba el auditor de prosa.

**Presupuesto de geometría:** `cap1_mapas.json` va por **102,9 KB** de 120 KB, y 100
rectángulos son ~400 puntos: no hay problema de espacio. Si algún día lo hubiera, se sube el
presupuesto deliberadamente — no se recorta el material (ver `Criterio de contenido`).

## T2.7.f · Por dónde empezar

1. Leer `geo.R:335-410` (`geo_puntos`, el manejo de `lineas`) — es el precedente literal.
2. Leer `geo.R:225-330` (`geo_poligonos`) — dónde encaja el argumento nuevo.
3. Ver cómo lo pinta hoy el navegador: `plantilla/plantilla-capitulo.html`, el registro
   `GEOMAPAS[...]` y el modo `puntos` con `lineas`.
4. `genera_cap1.R`, sección G.1b, es donde ya vive la rejilla del módulo 7.

---

# Lo que se hizo, y lo que apareció al hacerlo

## T2.7.g · Hallazgo 1: el condado no tocaba cuatro rectángulos

El encargo daba por buena la frase del módulo —«un condado toca **cuatro** rectángulos»— y
proponía dibujarla. Medido, el «cuatro» era un número redondo escrito a mano: sobre las 100
celdas de `st_make_grid`, los condados de `nc` tocan entre 1 y 6 rectángulos, y la
distribución no tiene ningún cuatro privilegiado.

| Celdas que toca un condado | 1 | 2 | 3 | 4 | 5 | 6 |
|---|--:|--:|--:|--:|--:|--:|
| Condados | 2 | 29 | 19 | 26 | 16 | 8 |

O sea que el mapa no podía «ilustrar la frase»: **había que elegir un condado, y elegirlo es
una decisión que hay que poder defender**. Elegir «uno que toque cuatro, para que cuadre con
lo escrito» habría sido escribir el dato para que se pareciera a la prosa, que es exactamente
lo que D10 prohíbe por el otro lado.

**El criterio que se adoptó, y por qué es el correcto:** el condado que **más infla el
total**. El exceso que aporta cada condado es \(k_i - 1\) veces su conteo —una vez de más por
cada celda extra en la que cae—, y ese criterio no es una preferencia estética: sale de la
propia cifra que el módulo publica. Gana **Mecklenburg**, sin empate:

| | |
|---|---|
| muertes súbitas (SID74) | **44**, el máximo del estado |
| celdas que toca | **5** |
| lo que aporta por «se tocan» | **220** |
| de más | **176** |
| parte de la inflación total | **9,00716 %** de las 1 954 que sobran |

Y trae de regalo una **identidad exacta**, que ahora es una comprobación en R, otra en Python
y una guarda de compilación:

$$\sum_i (k_i - 1)\, y_i \;=\; 2\,621 - 667 \;=\; 1\,954$$

La prosa del módulo se reescribió contra el dato: donde decía «cuatro» ahora dice
Mecklenburg, sus cinco celdas y sus 220. **Una palabra menos escrita a mano.**

## T2.7.h · Hallazgo 2: la celda del roce, que no estaba en el encargo

Al medir el reparto por área celda a celda apareció lo que ha acabado siendo el remate del
módulo. De las cinco celdas que toca Mecklenburg, **una recibe el 0,0023 % del condado** —un
roce de esquina, 0,0010 muertes si se repartiera— y «se tocan» **le entrega las 44 enteras,
igual que a la celda donde el condado tiene su núcleo**.

Eso es el predicado explicado sin explicarlo: `st_intersects` no mide cuánto solapa, contesta
sí o no. En el mapa se ve de un golpe al conmutar de estado —la celda pasa de decir `44` a
decir `0.00`—, y el recuadro de prosa que sigue al mapa lo nombra con sus dos cifras. No
estaba en el encargo; salió de medir.

## T2.7.i · La extensión de `geo.R`, y qué se decidió no hacer

El diagnóstico del encargo era correcto: no había forma de dibujar una segunda geometría
sobre un coropleto. Se añadieron a `geo_poligonos()` tres argumentos, los tres opcionales:

| Argumento | Qué es |
|---|---|
| `lineas` | polilíneas **sobre** el coropleto, con el mismo formato plano que las calles de Soho en `geo_puntos()` |
| `lineas_resaltadas` | índices 1-basados de las que se destacan (relleno + borde grueso) |
| `resaltado` | índice 1-basado del rasgo del coropleto que se destaca |

**Lo que costó pensarlo, y no es la parte del código:**

1. **La cuantización va contra la `q` del mapa, no contra QMAX.** `geo_puntos()` usa QMAX
   porque no tiene otra; `geo_poligonos()` tiene `q` por mapa desde T2.4 del capítulo 3.
   Mezclarlas dibujaría las dos capas a escalas distintas y el mapa saldría **con su leyenda
   y sus colores**, con la rejilla encima de unos condados que no son los suyos. Es el mismo
   modo de fallo que `geo_qxy` existe para evitar en las indicatrices de Tissot.
2. **La caja tiene que ser la del dato SIN simplificar.** `geo_simplifica` mueve vértices y
   encoge el bbox de los condados unos metros; deducir la caja de ahí dejaba la rejilla —que
   no se simplifica— asomando por fuera del encuadre, con el borde exterior recortado. El
   generador pasa `caja = geo_caja(rej_nc)` y lo dice en un comentario.
3. **Dos convenios de índice conviviendo, dicho en voz alta.** El navegador ya tenía una
   opción `resaltado` **0-basada** (muerta: ningún capítulo la usaba). Lo que viene de R es
   1-basado en todo `geo.R` —`aristas`, `resaltado2`, ahora `lineas_resaltadas`—. Unificarlos
   por dentro habría movido en silencio el resalte de quien usara la opción, así que conviven
   y el comentario del motor explica cuál es cuál.
4. **Lo que NO se hizo:** tocar el CSS de `.lectura-etiqueta`. El componente de lectura pega
   el rótulo y el valor sin separador —«la regla» + «emparejar por…» se lee «la
   reglaemparejar»— y eso es así en los tres capítulos publicados. Arreglarlo es una mejora
   real, pero cambia el aspecto de todas las lecturas del material y no es de esta tarea. Se
   esquivó redactando los valores para que empiecen por cifra o por comilla angular, y queda
   anotado abajo.

**Retrocompatibilidad, comprobada y no supuesta.** Se regeneraron los capítulos 2 y 3
enteros con el `geo.R` nuevo y se comparó byte a byte contra lo publicado:

```
cap2_mapas.json   IDÉNTICO
cap3_mapas.json   idéntico salvo la marca de tiempo (1 línea)
cap2/3_datos.json idénticos salvo la marca de tiempo
```

Después se restauraron sus salidas, para no dejar los JSON adelantados respecto de sus HTML.

**Y la otra mitad de «compartido», que casi se me escapa: la plantilla.** `geo.R` no es el
único archivo de los tres capítulos — `plantilla-capitulo.html` también lo es, y el motor del
`.geomapa` vive ahí. Tocarlo y reensamblar **solo** el capítulo 1 habría dejado tres HTML con
tres versiones distintas del mismo motor, que es justo la divergencia que este proyecto
persigue en todo lo demás. Se reensamblaron los tres y se comprobó qué cambió:

```
cap2: marcado idéntico = True · 490 -> 497 KB
cap3: marcado idéntico = True · 621 -> 628 KB
```

Es decir: **todo lo que el lector ve es byte a byte lo mismo**; lo único que crece son los
7 KB del motor. Los capítulos 2 y 3 se llevan las polilíneas sin estrenarlas.

## T2.7.j · Lo que el mapa comprueba de sí mismo

La lección de T1.2 y T1.3 es que los defectos de este proyecto viven **en el hueco entre
archivos**: cada uno correcto por su cuenta, el conjunto torcido. Un resalte es el candidato
perfecto —el lienzo sale igual de bonito señalando el condado de al lado— así que la cadena
tiene **dos eslabones y se rompen los dos por separado**:

- **el del cableado**, en `ensambla_cap1.py`: 12 guardas nuevas que emparejan
  `cap1_mapas.json` con `cap1_datos.json` —el resaltado, las celdas, el **orden** del reparto
  (los rótulos van por posición), el CRS de la rejilla y las tres identidades que la prosa
  afirma en vez de citar—;
- **el geométrico**, en `audita_cap1.py`: se **deshace la cuantización** de los rectángulos
  que el lienzo dibuja y se pregunta por el terreno. Los cinco anillos resaltados vuelven a
  coordenadas del State Plane y se comprueba que son exactamente las celdas que Mecklenburg
  toca, y que el polígono pintado de naranja cae **dentro** del condado del caso.

Sin el segundo, dos JSON que se muevan de acuerdo pasarían. Sin el primero, la tabla de
respaldo podría hablar de unas celdas mientras el mapa pinta otras.

**Un hueco que se encontró revisando, no ejecutando.** La primera versión comprobaba
`n_lineas` contra las 100 celdas de la rejilla, pero no contra el **largo real** del array:
un array truncado a 96 con el contador quieto en 100 habría dibujado una rejilla incompleta
con todo lo demás cuadrando. Es la misma comprobación que el auditor ya le hacía a `n` contra
`geom`, y faltaba por el mismo motivo por el que suelen faltar: la cifra declarada y la cosa
declarada se parecen mucho sobre un informe. Cerrado, con su inyección.

**Arneses, todos verdes:**

| Arnés | Antes | Ahora |
|---|---|---|
| `audita_cap1.py` | 1 022 comprobaciones | **1 058** (36 nuevas, todas sobre el módulo 7) |
| `prueba_auditor_cap1.py` | 79 defectos | **100 de 100 cazados** (21 nuevos) |
| `prueba_ensambla_cap1.py` | 60 guardas | **72 guardas · 66 de 66 defectos cazados** |
| guardas sin ver disparar | 6 | **6** — las mismas seis estructurales de siempre, ninguna nueva |

## T2.7.k · El presupuesto, subido a propósito

El encargo lo anticipaba y acertó. Con el mapa dentro:

| | Antes | Ahora | Presupuesto |
|---|--:|--:|---|
| geometría (§4) | 88,8 KB | **106,0 KB** | 120 KB |
| rejillas simuladas | 33,9 KB | 33,9 KB | 120 KB |
| `cap1_mapas.json` entero | 102,9 KB | **117,3 KB** | *era* 120 KB |
| HTML publicado | 580 KB | **612 KB** | 700 KB |

Las dos partidas reales están cómodas —al 88 % y al 28 % de las suyas—, pero el **total**
iba al **97,7 %** de un listón que valía 120 solo porque era el mismo número. O sea que el
mapa siguiente lo habría decidido esa línea y no el §4: **exactamente el fallo que T1.1
diagnosticó** con el tope de 560 KB del HTML, que llegó a querer recortar comentarios del
código para ganar 1,3 KB.

**Decisión, deliberada y escrita en el código:** la alarma del total sube de 120 a **160 KB**.
No es un presupuesto de contenido —los dos presupuestos juntos suman 240, así que 160 sigue
alarmando de verdad ante un ensamblado desbocado—; es una alarma, y vuelve a comportarse como
tal. Los 120 KB de geometría del §4 **no se tocan**. Ver `Vault/Estandar/Criterio de
contenido.md`.

## T2.7.l · Criterios de aceptación

- [x] `precalculo/audita_todo.sh` en verde, **los 15 pasos** (los tres capítulos).
- [x] `geo.R` retrocompatible: los mapas de los capítulos 2 y 3 salen byte a byte iguales.
- [x] Ninguna cifra a mano (D10). Las 12 cifras nuevas salen de `genera_cap1.R`, viajan en
      `cap1_datos.json` y `audita_cap1.py` las recalcula en Python — incluido el 100 % del
      pie de la tabla de respaldo, que era la tentación obvia de cablear.
- [x] El mapa se registra con su **JSON literal**; lo único que cambia con el botón son los
      rótulos y el texto accesible, que son opciones.
- [x] `<canvas>` con `aria-label` y `role="img"`, y el texto alternativo **cambia con el
      estado**: describe el mapa que hay, no el que el dato permitiría.

**Y dos comprobaciones visuales que no exigía el encargo pero que este mapa sí pedía:**

- **La tabla de respaldo es el mapa para quien no lo ve.** No repite el coropleto —eso ya lo
  da `cap1-nc`—: da las dos reglas una al lado de la otra, celda a celda, con la fila del
  roce (`0.0023 %` → `0.0010` frente a `44`) y un pie que contrasta **220 contra 44** sin una
  sola palabra.
- **Daltonismo.** El mapa apuesta naranja sobre verde, que es justo lo que el módulo 5 del
  capítulo 3 enseña a no hacer a ciegas. Comprobado con el conmutador del propio motor: bajo
  deuteranopía el resalte **sigue leyéndose**, porque no descansa solo en el tono —el condado
  cambia de color respecto de una rampa que pasa a gris, y las celdas llevan además borde
  grueso y relleno—.

## T2.7.m · Lo que deja abierto

1. **El CSS de `.lectura-etiqueta`.** Rótulo y valor se pegan en las lecturas de los tres
   capítulos. Es una línea de CSS y una mejora real de legibilidad, pero cambia el aspecto de
   todo el material publicado: **es tarea propia, no un efecto colateral de ésta.**
2. **Los otros dos capítulos heredan las polilíneas.** `geo_poligonos(lineas = )` está
   disponible para el 2 y el 3 sin tocar nada. El candidato inmediato es el capítulo 3, que
   habla de MAUP con rejillas.
3. **La regla del encargo que conviene retener**, porque es la que salvó esta tarea: cuando la
   prosa trae un número redondo sin origen —«cuatro rectángulos»—, **no se ilustra: se mide**.
   Ese «cuatro» ya estaba en el capítulo publicado antes de esta tarea y **ningún auditor
   podía verlo**, porque un entero pequeño no entra en el índice de cifras (el corte está en
   12, por el propio diseño de `audita_texto_base.cifras`). Es primo hermano del 61.7 de T2.2.

4. ~~**Dos etiquetas «T2.4» distintas.**~~ ✅ **Resuelto el mismo día.** El encargo venía
   nombrado T2.4 y el §3 del plan ya tenía una tarea **T2.4 · Cinco procedencias sueltas (P5,
   P6, P8, P9, P12)**, pendiente y sin relación con este mapa. Se renombró **este anexo a
   T2.7** —el siguiente libre de Fase 2— y no la tarea, porque el §2 la referencia por sus
   cinco defectos y esas referencias son las caras de romper. Propagado a los comentarios de
   `geo.R` y `plantilla-capitulo.html`, y los tres capítulos reensamblados.

5. **De dónde salió el módulo 7 no consta.** `D$agregacion_soporte`, la prosa de «Escala,
   soporte y agregación» y su bloque ejecutable existen en el código y **no tienen tarea ni
   anexo en este plan**. El encargo de esta tarea se lo atribuía a T2.3, pero T2.3 es la línea base
   del 8.07× de Snow y **no está ejecutada** —`D$snow` no trae ningún contraste de
   aleatorización—. Es un hueco de registro, no de código: el material está auditado. Pero
   conviene cerrarlo antes de que alguien lo dé por hecho.

---

# Anexo T2.2b — Los seis paros duros, y la cabecera que avisaba de lo contrario

**Cerrada el 2026-08-10.** Tarea de arnés: no toca el capítulo, ni R, ni el ensamblador. Lo
único que cambia en disco es `prueba_ensambla_cap1.py`, y las cinco superficies salen de ella
byte a byte igual que entraron.

## T2.2b.a · Lo que había, medido antes de tocar nada

La primera pasada, antes de escribir una línea, dio exactamente lo que el §3 predecía —que ya
es una comprobación, porque la especificación se escribió en otra sesión y contra otro estado
del ensamblador—:

```
  66 de 66 defectos cazados
  66 de 72 guardas se han visto disparar

  Sin ver disparar (6):
    · ensambla_cap1.py:85    PARADO: falta
    · ensambla_cap1.py:3569  PARADO: el ancla de apertura de «
    · ensambla_cap1.py:3575  se encontró DEMASIADO LEJOS; la plantilla ha cambiado.
    · ensambla_cap1.py:3579  se encontró DEMASIADO PRONTO: quedaría dentro del archivo…
    · ensambla_cap1.py:3590  veces, no 1.
    · ensambla_cap1.py:3628  registros de GEOMAPAS['demo-mapa'], se esperaba 1
```

Las mismas seis firmas del §3 y ninguna nueva. Que la cifra fuera 72 y no 60 —T2.7 metió 12
guardas y sus 12 inyecciones por el camino— no movió nada: `inventario()` las cuenta sola y la
lista de las descubiertas siguió siendo la misma. Es la propiedad que T1.3.n prometió, y la
primera vez que se la ve cumplirse a través de dos tareas ajenas.

## T2.2b.b · Las seis, una a una

Ninguna necesitó tocar el ensamblador de verdad. Cuatro se prueban apretándole a **él** un
literal en la copia —cambiar un tope es la misma avería que mover un ancla, vista desde el otro
lado, y no depende de qué haya hoy en la plantilla— y dos, envenenando **la plantilla**:

| # | Guarda | Superficie | Inyección | Lo que salió |
|---|---|---|---|---|
| 1 | ancla de apertura ≠ 1 (`reemplaza_region`) | plantilla | `const courseData = {` duplicado | `PARADO: el ancla de apertura de «courseData + DATOS_CAP1» aparece 2 veces, no 1` |
| 2 | tope MÁXIMO | ensamblador | `max_lineas=600` → `5` | `PARADO: la región de «los doce módulos» ocupa 462 líneas y el tope es 5.` |
| 3 | tope MÍNIMO | ensamblador | `max_lineas=20)` → `max_lineas=20, min_lineas=99)` | `PARADO: la región de «courseData + DATOS_CAP1» ocupa solo 10 líneas y el mínimo es 99.` |
| 4 | ancla ≠ 1 (`sustituye`) | ensamblador | «capítulo» sin tilde en el `<title>` que busca | `PARADO: el ancla de «título» aparece 0 veces, no 1.` |
| 5 | registros de `GEOMAPAS['demo-mapa']` ≠ 1 | plantilla | la línea del registro, duplicada | `PARADO: 2 registros de GEOMAPAS['demo-mapa'], se esperaba 1` |
| 6 | `_ruta()`: el archivo de entrada no está | datos | la ruta apunta a un temporal que no se crea | `PARADO: falta …/no_existe.json` |

Las seis salieron **`CAZADO`**: código distinto de cero **y** una línea que dice qué pasa.
Ninguna como `REVIENTA` —salir mal sin decir por qué, la lección de T1.3.i— ni como `INERTE`.

Un detalle de la (4) que no es cosmético: se parchea **el ensamblador** y no la plantilla a
propósito. Duplicar el `<title>` habría hecho contar 2, y la (1) ya prueba ese lado del
`!= 1`; quitarle el ancla a lo que el ensamblador busca hace contar **0**, que además es el
caso que de verdad ocurre —alguien retoca la plantilla y no el ensamblador—. Las dos mitades
de la misma desigualdad, cubiertas por separado.

## T2.2b.c · El tipo `falta`, y la comprobación de inercia al revés

La sexta era el único trabajo de diseño. Las dos formas de inyectar que había —mutar el JSON
ya parseado (`obj`) o sustituir texto (`txt`)— **escriben un archivo roto**, y esta guarda se
dispara en `_ruta()`, al arrancar, cuando **no hay nada que leer**. Un tercer tipo, de seis
líneas:

```python
if tipo == "falta":
    roto = tmp / "no_existe.json"       # y NO se crea
```

Lo que no es de seis líneas es la comprobación que lo acompaña. La regla 3 del arnés dice que
una inyección que no cambia nada no es una inyección, y por eso toda sustitución comprueba que
de verdad modificó el archivo. Aquí la pregunta va **al revés**: no «¿cambió?» sino «¿de
verdad no está?». Un temporal que sobreviviera a otra inyección dejaría esta prueba sin sujeto
—el ensamblador saldría limpio— y el arnés lo cantaría como `SE COLÓ` de una guarda que nunca
tuvo nada que cazar: culpando al ensamblador de una avería del arnés, que es exactamente lo
que la regla 3 existe para no hacer.

## T2.2b.d · La guarda nueva, probada por inyección contra el propio arnés

Una comprobación que nadie ha visto fallar puede estar bien escrita o puede ser incapaz de
dispararse, y desde fuera se ven igual —es la lección de T0.5, y la razón de ser de este
arnés—. La de arriba es nueva, así que se le inyectó: copia del arnés con una línea de más
(`roto.write_text("{}")`, el archivo **sí** existe) y a correr.

```
[ INERTE ] el JSON de datos no está donde apunta la variable de entorno
      no_existe.json SÍ existe en el temporal — la inyección se queda sin ausencia que probar

  71 de 71 defectos cazados · 1 inyección(es) INERTE(s)
  71 de 72 guardas se han visto disparar
  Sin ver disparar (1):  ensambla_cap1.py:85  PARADO: falta
```

Código de salida 1. Y lo que importa no es el `INERTE` sino las dos líneas de abajo: la guarda
`:85` **vuelve a la lista de las no vistas** en vez de contarse por buena. El arnés dice «no he
probado esto» en lugar de «esto se coló», que son los dos diagnósticos que la regla 3 separa.
La copia se borró al acabar.

## T2.2b.e · Hallazgo: la cabecera avisaba de lo contrario de lo que la tarea demuestra

El §3 lo anticipaba y estaba en lo cierto. `prueba_ensambla_cap1.py` abría con un párrafo en
mayúsculas: **LA PLANTILLA SE REDIRIGE PERO NO SE ENVENENA, y no por pereza: no es
alcanzable**. Se midió en su día y era verdad *de lo que se midió*; el problema es que decía
más de lo que había medido. La distinción que faltaba no es entre superficies, sino entre **lo
que la guarda cuenta y cuándo lo cuenta**:

- **Las anclas sí son alcanzables.** `reemplaza_region` y `sustituye` cuentan su ancla en el
  documento **en curso**, antes de haber sustituido nada. Un ancla duplicada en la plantilla
  llega entera y para el ensamblado en seco: por ahí entran las inyecciones 1 y 5.
- **El contenido sustituido no lo es.** Eso sigue siendo cierto y sigue siendo un hueco: el
  ensamblador cambia los cinco módulos de demostración por los doce del capítulo, así que
  quitarle un `</template>` o un `aria-label` a la plantilla deja el ensamblado limpio.

Reescrito con las dos mitades, y conservando el aviso para T3.1 y T4.1 en la que sigue
abierta. De paso, la lista de superficies envenenables de la cabecera pasa de «dos» a **tres**
—los JSON, el ensamblador y la plantilla— y se corrige el comentario de
`SUPERFICIES["plantilla"]`, que repetía el aviso viejo a diez líneas de la inyección que lo
desmiente.

Y conviene decir por qué esto es un defecto y no una errata. Un comentario que declara algo
**inalcanzable** no informa: instruye. Es el que hace que la próxima tarea no lo intente. Éste
llevaba desde T1.3.n desaconsejando exactamente las dos inyecciones que hoy cierran la lista.

## T2.2b.f · Verificación

```
python3 precalculo/prueba_ensambla_cap1.py

  72 guardas inventariadas en ensambla_cap1.py (leídas del código, no de una lista)
  OK   control de entrada · el ensamblador sale limpio sin inyectar nada
  … 72 × [ CAZADO ] …
  OK   control de salida · el arnés no dejó nada tocado
  OK   los archivos fuente siguen byte a byte igual
  OK   el capítulo publicado no se ha tocado

  72 de 72 defectos cazados
  72 de 72 guardas se han visto disparar
```

**La lista «Sin ver disparar» ya no se imprime**, que es el criterio de la tarea. Los dos
controles en verde y las cinco superficies intactas byte a byte: el arnés sigue siendo de solo
lectura sobre el árbol de verdad.

`audita_todo.sh --rapido`, **11 de 11 pasos en verde** — con testigo, ver T2.2b.h:

| | |
|---|---|
| `audita_cap1.py` | 1 064 comprobaciones · 0 fallos · 3 saltadas |
| `prueba_ensambla_cap1.py` | **72 guardas · 72 de 72 defectos · 0 sin ver disparar** |
| `audita_cap2.py` · `audita_cap3.py` | 445 y 356 comprobaciones · 0 fallos |
| auditores de prosa (demo + 3 caps.) | 77 · 149 · 129 · 130 comprobaciones · 0 fallos |
| `sin_aritmetica.py` · `verifica_bloques.py` | en verde |

*(Las 1 064 comprobaciones de `audita_cap1.py` son 6 más que las 1 058 del cierre de T2.7, y
no son de esta tarea: son de la sesión paralela que menciona T2.2b.h. T2.2b no toca R ni el
ensamblador ni ningún dato.)*

## T2.2b.g · Cambios en disco

| Archivo | Qué |
|---|---|
| `precalculo/prueba_ensambla_cap1.py` | 598 → 701 líneas · 6 inyecciones nuevas · el tipo `falta` con su inercia invertida · la cabecera y el comentario de `SUPERFICIES`, reescritos |

Y nada más. `genera_cap1.R`, `ensambla_cap1.py`, los tres JSON de `salidas/`, la plantilla y
los tres capítulos publicados **no se tocan**: es una tarea de arnés, y el propio arnés lo
comprueba byte a byte al acabar.

Reparto de las 72 inyecciones: 55 `obj` sobre los JSON (43 datos, 12 mapas), 14 `txt` sobre el
ensamblador, **2 `txt` sobre la plantilla** y **1 `falta`**. Las tres últimas son de esta
tarea, igual que las dos vías nuevas de llegar a una guarda.

**Coste:** el arnés entero, 4,5 s para 72 inyecciones trazadas con `sys.settrace`. Sigue
cabiendo de sobra en `--rapido`, que es la razón por la que `audita_todo.sh` no lo gatea.

## T2.2b.h · La trampa que costó la verificación: dos sesiones sobre la misma carpeta

La primera pasada de `audita_todo.sh --rapido` salió con un rojo que no era mío:

```
  OK   control de salida · el arnés no dejó nada tocado
  MAL  los archivos fuente siguen byte a byte igual
```

**Había otras dos sesiones corriendo `audita_todo.sh` sobre esta misma carpeta**, y una de
ellas reescribió `ensambla_cap1.py` y republicó el capítulo **a mitad de mi pasada** —18:16:08
y 18:16:12, dentro de la ventana entre la foto de entrada y la de salida del arnés—. Corrido
en solitario, el mismo arnés daba 72 de 72 y las cinco superficies intactas.

El arnés no falló: **cazó una contaminación real**. Es la trampa de los JSON de `salidas/` que
ya estaba anotada, en su versión grande: no un archivo regenerado a destiempo, sino otro agente
trabajando el mismo capítulo.

Esperar no convergía —al terminar las dos, la otra sesión encadenó una tercera—, así que la
verificación se hizo **con testigo**: huella `shasum` de los 63 archivos del árbol antes y
después de la pasada. Es sólido porque los pasos de `--rapido` son de **solo lectura** sobre el
árbol —se comprobó uno a uno: todas sus escrituras van a temporales—, de modo que la única
contaminación posible es una edición ajena, y eso es justo lo que la huella detecta. Resultado:

```
== superficies vigiladas: 63 archivos ==
== EXIT=0 ==
TESTIGO LIMPIO: ningun archivo del arbol se movio durante la pasada.
  ARNÉS COMPLETO EN VERDE
```

Si nada se movió, el verde vale igual que sobre un árbol quieto; y si algo se hubiera movido,
se sabría **qué**, en vez de tener que adivinar entre un defecto y un vecino. La regla nueva
está en «Las trampas del entorno»; el guion, en el scratchpad de la sesión.

## T2.2b.i · Lo que deja abierto

1. **El contenido sustituido de la plantilla sigue sin guarda.** Quitarle un `</template>` o
   un `aria-label` a `plantilla-capitulo.html` deja el ensamblado limpio, porque eso se
   sustituye antes de que nadie lo cuente. Cerrarlo pide una guarda que mire la plantilla
   ANTES de sustituirla; el día que exista, el arnés la inventaría solo. Es de **T3.1 o T4.1**,
   que son las que tocan la plantilla y la retropropagan a los tres capítulos.
2. **La cabecera del arnés todavía dice «41 guardas de compilación».** Es prosa histórica —el
   porqué de su existencia— y hoy son 72. No se tocó: no es de esta tarea, y el número que
   manda lo imprime `inventario()` en cada pasada. Pero si alguien lo lee como inventario, se
   equivoca.

---

# Punto de partida — para la sesión siguiente *(escrito el 2026-08-10, al cerrar T2.7; actualizado al cerrar T2.2b)*

> **Esto no es una tarea: es el estado del proyecto.** Se escribe para que la sesión siguiente
> arranque sin el contexto de ésta. La tarea que tocaba —**T2.2b**— está **cerrada** (anexo
> T2.2b); la que sigue es **T2.3**. Aquí va lo que ha cambiado alrededor y lo que hay que
> saber antes de tocar nada.

## Estado, medido y no recordado

`precalculo/audita_todo.sh` cerró **en verde los 15 pasos** el 2026-08-10, con los tres
capítulos reensamblados. Las cifras de esa pasada:

| | |
|---|---|
| `audita_cap1.py` | 1 058 comprobaciones · 0 fallos · 3 saltadas |
| `prueba_auditor_cap1.py` | 100 de 100 defectos cazados |
| `prueba_ensambla_cap1.py` | 72 guardas · 66 de 66 defectos · **6 sin ver disparar** |
| capítulos 2 y 3 | 91 de 91 y 56 de 56 |
| auditores de prosa | 110 de 110 defectos cazados |
| peso | cap. 1 en 612 KB de 700 · geometría 106,0 KB de 120 |

**Esas 6 guardas sin ver disparar son justamente el sujeto de T2.2b.** No son un defecto
nuevo: son los seis `sys.exit("PARADO: …")` que llevan ahí desde que se escribieron.

> **Actualizado el 2026-08-10, al cerrar T2.2b.** Las seis están cubiertas: el arnés dice
> **`72 de 72 guardas se han visto disparar`** y la lista «Sin ver disparar» ya no se
> imprime. La tabla de arriba es la foto de la pasada de T2.7 y se deja como estaba, que
> para eso es una medición fechada. Anexo T2.2b.

## Fase 2, al día

| Tarea | Estado | Cómo se comprobó |
|---|---|---|
| T2.1 · Los dos ρ | ✅ cerrada | anexo T2.1 |
| T2.2 · El puente de φ = 4 | ✅ cerrada | anexo T2.2 |
| T2.2b · Los seis paros duros | ✅ cerrada *(2026-08-10)* | anexo T2.2b · la lista «Sin ver disparar», vacía |
| T2.3 · La línea base de Snow | pendiente | `D$snow` no trae ningún campo de aleatorización |
| T2.4 · Cinco procedencias sueltas | pendiente | — |
| T2.5 · La banda nula del correlograma | pendiente | `tobler.permutado.bandas` trae una `I` por banda, no una envolvente `q05`/`q95` |
| T2.6 · La incertidumbre de los cocientes | pendiente | hay `ic_iid` e `ic_bloques` sobre la media, pero `razon` e `inflacion_pct` van sin intervalo |
| T2.7 · El mapa del módulo 7 | ✅ cerrada | anexo T2.7 |

Luego, el **Checkpoint 2**, cuyo tercer punto es «tu revisión antes de seguir».

## Lo que T2.7 movió y hay que saber antes de tocar nada

1. **`geo_poligonos()` sabe dibujar polilíneas.** Tres argumentos nuevos y opcionales
   —`lineas`, `lineas_resaltadas`, `resaltado`—, cuantizados contra la caja y la `q` **del
   mapa**. Los capítulos 2 y 3 los heredan sin estrenarlos.
2. **La plantilla es compartida, igual que `geo.R`.** Tocar
   `plantilla/plantilla-capitulo.html` obliga a **reensamblar los tres capítulos**, o quedan
   con tres versiones del mismo motor. Se comprueba con un diff del marcado: tiene que salir
   idéntico y crecer solo el `<script>`.
3. **La alarma del peso total de `cap1_mapas.json` está en 160 KB**, no en 120. Los 120 KB de
   geometría del §4 no se tocaron. El porqué, en T2.7.k.
4. **El ensamblador tiene 72 guardas**, no 60. Si añades una, el arnés la inventaría sola.

## Las trampas del entorno, que cuestan una sesión cada una

- **R se invoca con `precalculo/rscript.sh`.** El `Rscript` del PATH es Homebrew y no tiene
  `sf`; además arranca en `LC_CTYPE=C` y `jsonlite` escribe las tildes mal sin fallar.
- **El HTML es un artefacto de compilación.** Nunca se edita `Htmls_Espacial/*.html`: se
  editan `precalculo/genera_capN.R` y `precalculo/ensambla_capN.py`.
- **No toques los JSON de `precalculo/salidas/` mientras corre un arnés de inyección.** Cada
  uno los fotografía al empezar y compara byte a byte al acabar; regenerarlos a mitad pone en
  rojo una pasada correcta. *(Pasó en esta sesión.)*
- **Y la versión grande de la anterior: una sola sesión por carpeta.** Dos agentes a la vez
  sobre este árbol se ponen en rojo el uno al otro sin que ninguno tenga un defecto. Le pasó a
  T2.2b: `MAL los archivos fuente siguen byte a byte igual`, y la causa era otra sesión
  reescribiendo `ensambla_cap1.py` y republicando el capítulo **a mitad de la pasada**. El
  arnés funcionaba: cazó una contaminación real. Comprueba con `ps -ax | grep audita_todo`
  antes de empezar, y si no queda más remedio que compartir, corre con **testigo** —huella
  `shasum` del árbol antes y después—: si nada se movió, el verde vale igual que sobre un
  árbol quieto, y si algo se movió sabes qué en vez de adivinar. *(El guion de T2.2b sirve de
  modelo.)*
- **D10:** ninguna cifra a mano. Todo número sale de R, viaja en el JSON y `audita_capN.py` lo
  recalcula por su cuenta en Python. `sin_aritmetica.py` vigila la causa con `ast`.

## Lo que queda abierto y no es de T2.2b

1. **El CSS de `.lectura-etiqueta`.** Rótulo y valor se pegan en las lecturas de los tres
   capítulos («la regla» + «emparejar…» se lee «la reglaemparejar»). Una línea de CSS, pero
   cambia el aspecto de todo el material publicado: **tarea propia**, no efecto colateral.
2. **El módulo 7 no tiene padre registrado.** `D$agregacion_soporte`, la prosa de «Escala,
   soporte y agregación» y su bloque ejecutable existen y están auditados, pero **no tienen
   tarea ni anexo en este plan**. Hueco de registro, no de código.
3. ~~**T2.2b es dependencia blanda de T4.1.**~~ **Saldada el 2026-08-10.** Los cuatro paros
   duros de `reemplaza_region()` y `sustituye()` —la maquinaria que T4.1 va a mover al
   retropropagar el motor `.geomapa`— están cubiertos por inyección. Ese cambio llega ya
   vigilado: si T4.1 desplaza un ancla o cambia un tope, el arnés lo dice por su nombre.

## Cómo arrancar

**T2.2b está cerrada** (anexo T2.2b). La que sigue en la fase 2 es **T2.3 · La línea base del
8.07× de Snow**, especificada en el §3; después T2.4, T2.5 y T2.6, y luego el Checkpoint 2,
cuyo tercer punto es «tu revisión antes de seguir».

> **Antes de arrancar, mira si hay otra sesión trabajando en esta carpeta** —`ps -ax | grep
> audita_todo` — y no la pises. Es la cuarta trampa del entorno, y la descubrió T2.2b: ver
> más abajo.
