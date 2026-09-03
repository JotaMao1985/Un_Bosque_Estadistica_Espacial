# Plan · Revisión del capítulo 5, módulo por módulo

Estadística Espacial 2026-II (20929) · Universidad El Bosque

**Fecha del plan:** 2026-09-02 · **Blanco:** `Htmls_Espacial/capitulo-5-intensidad-nucleos.html`
**Encargo:** antes de arrancar el capítulo 6, leer el 5 como lo lee un estudiante y revisar
cuatro cosas que **ninguna herramienta del repositorio mira**: ortografía, redacción y
narrativa, calidad y pertinencia de las figuras, y pertinencia y funcionamiento de los
simuladores.
**Estado:** ✅ **CERRADO el 2026-09-02.** Las tres fases y los dos checkpoints. Javier decidió
en el Checkpoint A **barajar los cinco capítulos** y **arreglar los tres hallazgos**; hecho,
verificado y con dos gemelos más encontrados al hacerlo. El informe, con lo aplicado en su §5,
es [`AUDITORIA_CONTENIDO_CAP5.md`](AUDITORIA_CONTENIDO_CAP5.md).

**Lo que queda en pie, y no es de esta tanda:** la deuda **A.23.2** —los capítulos 3 y 4
escriben `respuesta` donde el motor lee `retro`, y sus **68** explicaciones por opción no se
dibujan— sigue viva y ahora es más barata que nunca: es una palabra por opción, y los dos
capítulos ya se regeneran limpios. Y **N1, N2, N3, N4 y N5** se quedan anotados, que es lo que
el alcance decidió.

### Las dos decisiones de Javier (2026-09-02)

| Pregunta | Respuesta | Consecuencia |
|---|---|---|
| Alcance de la Fase 2 | **corregir, no rediseñar** | ortografía, redacción, párrafos de entrada y salida, `aria-label`. Un simulador que resulte ser adorno o una figura mal pensada **se anotan con su porqué** y se deciden aparte: no se rehacen en esta tanda |
| Ortografía | **instalar diccionario español** | `hunspell` con `es_CO`, en vez de fiarlo a mi criterio sobre la cola larga. R0.1 cambia de forma |

Q3 —publicar al cerrar la Fase 2 o acumular para el capítulo 6— sigue abierta, y no bloquea
nada: por defecto **no se hace `push` sin decirlo**.

---

## 0. Por qué esto no es redundante con el arnés

El capítulo 5 salió publicado el 2026-08-30 con `audita_cap5.py` en 297/0/0, su arnés en
151/151, `audita_texto_cap5.py` en 213/0 con 50 inyecciones cazadas, `verifica_bloques.py`
con 133 de 133 cifras verificadas ejecutando el código, y la consola limpia en los doce
módulos. **Nada de eso mira lo que esta revisión mira.**

Hay tres precedentes recientes que lo demuestran, y los tres se encontraron leyendo o
moviendo, no auditando:

- **A.23.1** — el único simulador que el capítulo tenía escrito **llevaba muerto desde que
  se escribió**: llamaba a cuatro nombres que no existen. El auditor en verde, la consola
  limpia.
- **A.23.2** — la retroalimentación por opción de los capítulos 3 y 4 **no se dibuja
  nunca**: escribieron `respuesta` donde el motor lee `retro`. 68 explicaciones publicadas
  que no ve nadie.
- **§13 del preparcial** — cuatro `alt` de figura eran **la clave parafraseada**, y un
  agente contestó los seis ítems de gráfico sin ver una sola imagen. Los cuatro auditores
  mecánicos estaban en verde antes y después.

La regla del **§9.1 del plan del material** ya lo dice desde el 2026-08-04: *el ritmo no lo
caza ninguna comprobación automática; hay que leer el módulo como lo lee un estudiante.*

## 0.1 · El momento es este, y no después

El censo del banco (`censo_banco.py`, 2026-08-31) midió que **23 de los 24 ítems del Corte
II beben del precálculo**. Cualquier arreglo de esta revisión que mueva una cifra regenera
`cap5_datos.json` y con él el capítulo — y si el banco del parcial 2 ya estuviera escrito,
lo dejaría mintiendo en silencio, que es exactamente la familia de defectos que obligó a
darle auditor propio al preparcial. **Revisar antes de escribir el banco cuesta cero;
después, cuesta el banco.**

---

## 1. Lo que hay, medido (2026-09-02)

| m | Título | Palabras | Lienzos | Geomapas | Simuladores |
|---|---|---:|---:|---:|---:|
| 1 | De contar a suavizar | 646 | 1 | 1 | 0 |
| 2 | El ancho de banda lo es todo | 507 | 2 | 1 | 1 |
| 3 | Selectores de ancho de banda | 626 | 1 | 0 | 1 |
| 4 | Corrección de borde en la KDE | 638 | 1 | 0 | 1 |
| 5 | La KDE como mapa de calor | 674 | 3 | 2 | 1 |
| 6 | Intensidad relativa | 848 | 3 | 2 | 1 |
| 7 | Covariables | 554 | 1 | 0 | 1 |
| 8 | El Poisson inhomogéneo | 552 | 1 | 0 | 1 |
| 9 | Ajustar con `ppm` | 694 | 1 | 0 | 1 |
| 10 | Diagnóstico del ajuste | 774 | 1 | 0 | 1 |
| 11 | Conglomerado y autoexcitación | 991 | 2 | 0 | 2 |
| 12 | Autoevaluación y ejercicios | 1 314 | 0 | 0 | 0 |
| | **TOTAL** | **8 818** | **17** | **6** | **11** |

Más 12 preguntas de autoevaluación y 5 ejercicios guiados en el módulo 12, y 12 pares de
bloques R/Python repartidos por el capítulo. Vocabulario de la prosa: **1 548 palabras
distintas, 809 de ellas una sola vez** — que es donde vive una errata.

**Los módulos son `<template id="module-N">`**: el navegador solo tiene montado el que se
está viendo. Una revisión de pantalla hay que hacerla módulo a módulo, y por eso los lotes
de la Fase 1 son de tres.

---

## 2. Decisiones de método

1. **La Fase 1 no toca ningún archivo.** Produce una lista de hallazgos con módulo,
   dimensión, gravedad y evidencia. Arreglar mientras se lee convierte la revisión en una
   reescritura, y entonces nadie sabe qué se revisó.
2. **Dos superficies por módulo, no una.** El texto ensamblado —leído como estudiante— y la
   página movida —cada mando de cada simulador—. A.23.1 solo existe en la segunda.
3. **El HTML es un artefacto.** Todo arreglo de prosa va a `ensambla_cap5.py`; todo arreglo
   que mueva una cifra va a `genera_cap5.R` y vuelve por el precálculo. Ninguna cifra se
   escribe a mano, ni siquiera para corregir otra.
4. **Rúbricas prestadas, no inventadas.** Narrativa: las tres reglas del §9.1. Figuras: la
   lección de los `alt` del §13.4 del preparcial —la descripción cita los datos y deja la
   lectura por hacer— más los dos defectos que allí quedaron sin arreglar (barras de altura
   cero, series indistinguibles). Simuladores: ¿enseña algo que la prosa no puede decir?

---

## 3. Las tareas

### Fase 0 — Las dos pasadas mecánicas (antes de leer)

#### ✅ R0.1 · La pasada de ortografía sobre el vocabulario · **S** · hecha 2026-09-02
**Resultado: 0 erratas.** `hunspell` + `es_CO`, 137 desconocidas → 2 tras
`precalculo/lexico_espacial.txt`, y las 2 son el hallazgo N1 (los nombres de sede sin tilde).

**Descripción.** Extraer la prosa de los doce módulos —sin código, sin fórmulas—, sacar el
vocabulario con frecuencias y revisar la cola larga. Una errata casi siempre aparece una
sola vez; el léxico técnico legítimo se declara en una lista para que la pasada se pueda
repetir tal cual en el capítulo 6.

**Criterios de aceptación**
- [x] El vocabulario revisado — con diccionario, que es mejor que la cola larga: las 137 que
      `es_CO` no reconoce, leídas una a una en su frase.
- [x] Cada errata anotada con módulo y frase, sin corregirse todavía (N1).
- [x] El léxico aceptado queda en `precalculo/lexico_espacial.txt`, no en la cabeza de la sesión.

**Verificación:** la pasada se vuelve a correr y da la misma lista. **Depende de:** nada.
**Archivos:** `precalculo/lexico_espacial.txt` (nuevo), scratchpad.

#### ✅ R0.2 · Los doce módulos movidos en el navegador · **M** · hecha 2026-09-02
**Consola limpia, 17 lienzos con tinta y con `aria-label`, y todos los mandos de los once
simuladores movidos a sus extremos.** Dos hallazgos: uno sin mandos (H4) y uno que anuncia un
mando que no existe (H3). El método —viewport emulado y figura fijada arriba, porque el panel
oculto no repinta lo que se descubre— está en el §3 del informe.

**Descripción.** Servir el sitio con `preview_start` (`.claude/launch.json`, puerto 8931),
recorrer los doce módulos y **mover todos los mandos de los once simuladores**: cada
deslizador a sus dos extremos y a un punto intermedio, cada botón, cada selector.

**Criterios de aceptación**
- [x] Consola sin un solo error en los doce módulos.
- [x] Los 17 lienzos con tinta —medida píxel a píxel, ninguno en blanco— y con su `aria-label`.
- [x] Cada mando de cada simulador movido a sus extremos, comparando **hash del lienzo** y texto
      de la lectura antes y después. Los dos que no mueven el dibujo son de diseño (N3) o
      están dichos en su párrafo (N2).
- [~] **Capturas: 5 de los 17 lienzos** (m1, m2, m3, m4, m9). Los otros doce se juzgaron por su
      dato —tipo, ejes, series, escala, censo de colores— y no por su pinta, que es más fiable
      para lo que se estaba buscando y más barato. Si algún hallazgo de la Fase 2 obliga a mirar
      una figura concreta, se captura entonces.
- [x] Sin desbordamiento horizontal: 12 módulos a 375 px y los 6 más pesados a 318 px, todos
      `scrollWidth == clientWidth`.

**Verificación:** la lista de capturas tiene 17 entradas y el registro dice, mando a mando,
qué cambió. **Depende de:** nada. **Archivos:** ninguno (solo lectura).

---

### Fase 1 — La lectura, en cuatro lotes de tres módulos

Los cuatro lotes tienen los **mismos criterios**, aplicados a sus tres módulos:

- [ ] **§9.1 regla 1** · ningún módulo abre pidiendo trabajo: antes del primer simulador o
      pregunta hay prosa que sitúa.
- [ ] **§9.1 regla 2** · cada componente interactivo tiene su párrafo de entrada **y el de
      salida**, que es el que se olvida. El módulo 2 y el 9 ya lo perdieron una vez en T3.6.
- [ ] **§9.1 regla 3** · el título y el objetivo del encabezado son un contrato, y el módulo
      lo cumple.
- [ ] **Redacción** · frases que hay que releer, párrafos sin verbo principal, conectores que
      prometen una relación que no está, repeticiones a menos de tres líneas.
- [ ] **Ortografía** · lo que la pasada R0.1 señaló en estos módulos, confirmado en su frase.
- [ ] **Figura** · legible sin ampliar; ninguna serie indistinguible de otra; ningún rótulo
      solapado; ninguna barra de altura cero; escala honesta. Y el `aria-label` **describe
      los datos sin regalar la lectura**.
- [ ] **Simulador** · ¿qué enseña que la prosa no puede decir? Si la respuesta es «lo mismo
      que el párrafo de arriba», es un adorno y se dice.
- [ ] Cada hallazgo con módulo, dimensión, gravedad (bloqueante / mejora / nota) y la cita
      exacta o la captura.

| Tarea | Módulos | Palabras | Lienzos | Simuladores | Tamaño |
|---|---|---:|---:|---:|---|
| **R1.1** | 1–3 · de contar a suavizar, ancho de banda, selectores | 1 779 | 4 | 2 | M |
| **R1.2** | 4–6 · borde, mapa de calor, intensidad relativa | 2 160 | 7 | 3 | M |
| **R1.3** | 7–9 · covariables, Poisson inhomogéneo, `ppm` | 1 800 | 3 | 3 | M |
| **R1.4** | 10–12 · diagnóstico, Hawkes, autoevaluación y ejercicios | 3 079 | 3 | 3 | M |

**R1.4 lleva además lo suyo:** las 12 preguntas y los 5 ejercicios. Se les aplica lo que el
§13 del preparcial ya midió y costó dieciséis arreglos: que la clave no se adivine por la
forma —la más larga, la más matizada—, que ninguna pista mate a sus propios distractores,
que ningún distractor sea verdadero en una pregunta de «marca todo lo cierto», y que el
enunciado no pida una cosa y la clave conteste otra.

**Dependen de:** R0.1 y R0.2 (la lectura usa sus dos salidas). Entre ellas, ninguna.

### ✅ Checkpoint A — la lista completa, antes de tocar nada · cerrado 2026-09-02
- [x] Los doce módulos leídos y las cuatro dimensiones cubiertas en cada uno.
- [x] Hallazgos clasificados, con su evidencia: **H1** (la correcta es la primera en las 51
      preguntas de los cinco capítulos), **H2** (el contorno que el módulo 1 promete y no
      dibuja), **H3** (el párrafo del módulo 8 manda mover `nd`, que no es un mando),
      **H4** (el simulador sin mandos del módulo 11) y cuatro notas.
- [x] **Javier decidió:** barajar **los cinco capítulos** y arreglar **los tres hallazgos**.

**Las cuatro decisiones que el Checkpoint A necesitaba, y cómo quedaron**
0. **H1 → los cinco.** Con sus 6 retroalimentaciones posicionales reescritas.
   **H2 → el texto** (opción 1). **H4 → figura sin marco de simulador** (opción 1).
   **N2 y N3 → anotados**, sin frase nueva.
1. **H1**, que es el que importa: ¿se baraja **solo el capítulo 5** o **los cinco**? Barajar los
   cinco regenera cuatro capítulos cerrados y obliga a reescribir 12 retroalimentaciones que
   nombran posiciones —3 aquí, 6 en el 1, 1 en el 2, 2 en el 4—.
2. **H2**: ¿se corrige el texto (barato, dentro del alcance) o se dibuja el contorno (lo que el
   módulo quiere, y toca R)?
3. **H4**: ¿figura sin marco de simulador, o se le da un mando de verdad? Lo segundo es
   rediseño.
4. **N2 y N3**: ¿se anotan y se quedan, o entran como frase?

---

### Fase 2 — Los arreglos

#### R2.1 · Lo que solo toca prosa · **M**
Redacción, ortografía, párrafos de entrada y salida que falten, `aria-label` que regalen la
lectura. Todo en `ensambla_cap5.py`.

- [ ] Ningún arreglo introduce una cifra: `sin_aritmetica.py` en 0.
- [ ] `audita_texto_cap5.py` sigue en 213/0 y el arnés de prosa en 191/191.
- [ ] El documento se reensambla y el recuento del ensamblador cuadra.

#### R2.2 · Lo que mueve una cifra o una figura · **M · condicional**
Solo si la Fase 1 encuentra algo así. Va a `genera_cap5.R` con su ancla, se regenera el
precálculo y se vuelve a auditar.

- [ ] `audita_cap5.py` 297/0/0 (o más comprobaciones, nunca menos) y su arnés en 151/151.
- [ ] `verifica_bloques.py` vuelve a cuadrar las 133 cifras.
- [ ] Reproducible byte a byte: dos ejecuciones, el mismo JSON.

#### R2.3 · La cadena entera, y el cierre · **S**
- [ ] `audita_todo.sh --rapido` en verde, y los pasos del capítulo 5 sin `--rapido`.
- [ ] `cuenta_sitio.py` en verde y el README recontado si cambió alguna cifra.
- [ ] Commit con los hallazgos dichos, y `git push` solo con el visto bueno.

### ✅ Checkpoint B — publicar o esperar
- [ ] Todo arreglo aceptado está dentro y verificado.
- [ ] Lo que se decidió NO arreglar queda escrito con su porqué, como el §13.6.

---

## 4. Riesgos

| Riesgo | Impacto | Mitigación |
|---|---|---|
| La lectura se convierte en reescritura | alto | La Fase 1 no toca archivos; el Checkpoint A es la puerta |
| Un arreglo mueve una cifra y descuadra el capítulo | alto | R2.2 pasa por R y por el auditor; nunca por el ensamblador |
| «Está en verde, luego está bien» | alto | Es el §12.7 del preparcial: los cuatro auditores estaban en verde antes y después de los diecinueve arreglos |
| El lote 4 es el más pesado (3 079 palabras + quiz + ejercicios) | medio | Va el último, con el criterio del §13 ya practicado en los tres anteriores |
| Retrasa el capítulo 6 | medio | Cuatro lotes de lectura y dos de arreglo; y hacerlo después del banco del Corte II cuesta el banco |

---

## 5. Preguntas abiertas

- **Q1 · ¿El alcance es corregir, o puede cambiar contenido?** Si un simulador resulta ser
  un adorno, ¿se quita, se rehace, o solo se anota? Cambia el tamaño de la Fase 2.
- **Q2 · La ortografía.** No hay corrector instalado (`aspell`/`hunspell` no están). ¿Vale
  la pasada por vocabulario de R0.1, o instalo un diccionario español?
- **Q3 · ¿Se publica al cerrar la Fase 2, o se acumula para el commit del capítulo 6?**
