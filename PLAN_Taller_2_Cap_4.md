# Plan · Taller 2 — Capítulo 4 (patrones puntuales)

Estadística Espacial 2026-II (20929) · **Corte II** · Universidad El Bosque

Taller teórico-práctico sobre *Patrones puntuales: descripción, CSR y funciones de resumen*
(cap. 4, **los once módulos de contenido**), aplicado en la **semana 10** como cierre del Corte II
y preparación del parcial 2. Evalúa **apropiación de conceptos, interpretación
de resultados y comprensión de procedimientos**, no ejecución de código.

**Fecha del plan:** 2026-09-09 (miércoles, semana 6) · **Calendario revisado el 2026-09-09**
**Entrega:** martes **6 de octubre de 2026** · **Sustentación:** jueves **8 de octubre**
**Reparto:** propuesto el lunes 21 de septiembre (§2.2) — pendiente de confirmar

---

## 0. Cómo retomar esto en otra sesión

**Estado al 2026-09-09: C1 HECHA (C1a + C1b). Defensa en UNA sesión (decidido).**
`precalculo/genera_taller2.R` corre en verde con **41 anclas** en **11,5 s**, es **reproducible
byte a byte** (dos corridas, mismos `sha256`) y escribe `taller2_datos.json` (531,0 KB) y
`taller2_mapas.json` (167,5 KB). Nueve secciones: A fuentes · B las 16 localidades · C el defecto
del bounding box · D los patrones generados · E el σ sembrado de T5 · F las envolventes de T4(b) ·
G el sesgo de borde · H las 1000 variantes · I la escritura.
**Ninguna respuesta viaja**: la convención es que todo campo cuyo nombre empieza por punto es una
respuesta, `sin_puntos()` los quita y `revisa_publicable()` vuelve a mirar el resultado; además una
guarda rechaza el JSON si contiene «agregado», «aleatorio», «regular», «Thomas», «rSSI» o
«familia».
**La construcción corrigió al plan SIETE veces**: **M-2 corregida**, **M-6**, **M-7**, **M-8**,
**M-9**, **M-10** y **M-11**. Las dos más caras: M-6 invalidaba una tabla ya escrita aquí, y M-10
tumbó el diseño de T4(b) que este plan daba por bueno.
**C2b HECHA**: `datos_taller2.R` escribe `entrega/datos/taller2_{sedes,localidades}.gpkg` y
`taller2_patrones.csv`, verificados **abriéndolos desde fuera del repositorio** con `sf` y con
geopandas, y ya en la lista blanca del `.gitignore`. Comprueba además que **las 60 curvas del CSV
cuadran con las del JSON**: sin eso, una desincronización entre el reparto y el enunciado sería
invisible —los dos correrían en verde y el estudiante calcularía sobre otros puntos—.
**C3 HECHA**: `audita_taller2.py`, **146 comprobaciones, 0 fallos, 0 saltadas**, recalculando en
Python con geopandas/scipy. **Cazó una fuga en su primera pasada**: el JSON publicaba el campo
`sigma_sembrado`, cuyo nombre le anuncia al estudiante que ese ancho está plantado. Renombrado a
`sigma_informe`.
**Y antes, leyendo el JSON a ojo, apareció otra**: los tríos viajaban siempre en el orden
(agregado, aleatorio, regular) y la posición 1 tenía la G mayor en **12 de 12**. `unname()` quita
los nombres, no la posición. Barajado, con guarda en el generador y comprobación propia en el
auditor.
**C4 HECHA**: `prueba_auditor_taller2.py`, **46 inyecciones, 46 cazadas, TIPOS 31 de 31** —todas
las comprobaciones del auditor se han visto fallar alguna vez—, con los dos controles limpios y
cero fallos del propio arnés. **Encontró tres agujeros que 146 comprobaciones en verde no podían
delatar**: el auditor **moría en vez de informar** ante seis inyecciones (y el mismo `.iloc[0]` sin
guardar estaba **dos veces** — guardar una aparición y no la otra es la trampa de alcance del
Taller 1); **faltaba una comprobación entera** —renombrar el campo `localidad` sin tocar su clave
pasaba limpio—; y **una comprobación cuyo `detalle` cambia entre pasar y fallar es invisible para
el recuento por tipos**, porque produce dos nombres distintos. El auditor pasa de 146 a **180
comprobaciones**.
**C5a HECHA (2026-09-09)**: `precalculo/ensambla_taller2.py` →
`Htmls_Espacial/taller-2-cap-4.html` (1 067 KB, de los que 698 son los dos JSON incrustados,
M-11). Trae el esqueleto, la cabecera y el pie, el CSS propio, el **buscador del §5.2** y **T1 y
T2**. Verde: el auditor sigue en **180 · 0 · 0**, `sin_aritmetica.py` y `campos_vivos.py` limpios,
consola sin errores y **sin desbordamiento a 1 280, 375 y 318 px** en los tres módulos; seis
ciclos de módulo dejan **0 gráficos huérfanos**. **Los cuatro bloques de código se ejecutaron de
verdad** —no solo se escribieron—, y ahí aparecieron dos de los tres hallazgos de abajo.
**C5b sigue**: T3, T4, T5 y las dos rúbricas. Las anclas y los mecanismos, en el §7.1.

**M-13 · LA CAJA DE T1 ES LA DEL POLÍGONO, NO LA DE LOS PUNTOS. El criterio de C2 estaba
equivocado.** C2 dice «la ventana de caja sale de `owin(range(x), range(y))`». Medido el
2026-09-09 sobre las dieciséis, con la convención de dos colas: con la caja del **polígono** salen
**exactamente** las cifras de M-2 —Antonio Nariño 0,4536 sobre el polígono y < 0,0001 sobre la
caja, Barrios Unidos **0,0106**, Los Mártires **0,0605**, Tunjuelito 0,0006— y el recorrido de
T1(a) —Kennedy **32,8 %**, Usme **61,7 %**—. Con la caja de los **puntos** no sale ninguna de las
dos cosas, y **el conjunto que vuelca cambia**: pasa a ser Antonio Nariño, Rafael Uribe y **Los
Mártires** en vez de Barrios Unidos. Es M-6 otra vez, con otra convención. **Manda el polígono**,
que es además el error natural —tienes el polígono y tomas su extensión— y es lo que el enunciado
publica. C2 queda corregido por esta línea.

**M-14 · `Fest()` ESTÁ ROTO EN ESTA INSTALACIÓN DE R, Y LAS 60 CURVAS F DEL JSON NO SON LA
FUNCIÓN DE ESPACIO VACÍO. BLOQUEA T2.** Con `spatstat.geom` 3.7.2 y `spatstat.explore` 3.8.0,
`distmap.ppp()` devuelve distancias **al cuadrado**, y `Fest()` las lee como distancias. La prueba
cabe en dos líneas: un **solo punto** en el centro del cuadrado unidad tiene F(0,1) = π·0,01 =
**0,0314**, y `Fest()` publica **0,40204**; y `max(distmap())` de ese punto vale **0,4922**, que es
0,7071 **al cuadrado**. El efecto sobre lo publicado está medido: **las 36 F de los tríos llegan a
0,99 entre r = 0,010 y r = 0,140** —la mayoría en el segundo o tercer nodo de 51— y **las tres F de
un mismo trío se separan entre sí 0,045 y 0,078, contra 0,35 a 0,60 que se separan las tres G**.
Es decir: en la pantalla las tres F son la misma curva, y T2(a) —«empareja con lo que mira cada
función»— se queda sin la mitad de su evidencia.
**Por qué no lo vio nadie:** `audita_taller2.py` recalcula **G y solo G** contra el CSV, y la
sección C de `datos_taller2.R` compara **solo G** contra el JSON. F no la comprueba nada.
**El capítulo 4 se salvó por casualidad y conviene saber por qué**: `genera_cap4.R` **no usa
`Fest()`** —calcula F a mano sobre una rejilla de 400 × 400 sondas, `f_sitios: 160000`— y su
`f_obs` sigue a su `f_teo` decimal a decimal. G, K, L y g del Taller 2 **están sanas**:
comprobado que en cada trío una K/πr² ronda 1, otra queda por debajo y otra por encima.
**Qué hay que hacer, y no es en el ensamblador:** rehacer F en `genera_taller2.R` y en
`datos_taller2.R` con el camino del capítulo 4 (rejilla de sondas + `nncross`), **añadir la
comprobación de F al auditor** —es el agujero que permitió esto— y regenerar. Se puede: el taller
**no se ha repartido**. Hasta entonces **T2 no se publica**; el ensamblador ya está escrito y
pintará las curvas buenas en cuanto el JSON las traiga.

**FUGA · `precalculo/datos_taller2.R` está versionado, ya está en `origin/main` y REVELA LAS
FAMILIAS.** El `.gitignore` ignora `genera_taller2.R` precisamente porque «construye los patrones
puntuales SABIENDO de qué familia es cada uno, que es lo que la tarea T2 pide clasificar» — y deja
pasar `datos_taller2.R`, que hace lo mismo: `set.seed(20262)`, `genera_agregado()` = `rThomas`,
`genera_aleatorio()` = `rpoispp`, `genera_regular()` = `rSSI`, `ps <- list(agregado = …,
aleatorio = …, regular = …)` y `trios[[i]] <- ps[o]`. Su propia sección C **demuestra** que
reproduce los patrones publicados: compara las 60 curvas contra el JSON y para si difieren. Correr
ese guion e imprimir `names(trios[[i]])` es la respuesta de T2 entera. La guarda que tiene solo
mira los **identificadores** (`p01`, `t03a`), no los **nombres de las variables**.
**Y de paso deja ver una cosa que el §3 daba por otra**: los **24 patrones «propios» son todos
agregados** —`propios[[i]] <- genera_agregado()`—, así que «clasifica el régimen de el tuyo» tiene
la misma respuesta para los doce; y el trío **no contiene** el patrón propio, son tres patrones
aparte. Por eso **T2 se escribió sobre el trío** (los tres regímenes, que es el módulo 3) y el
patrón propio se deja a T3, que es donde el propio plan ya presupone la agregación —«di en qué r
ocurre **de verdad** la agregación»—: pedir en T2 que clasifiquen lo que T3 les cuenta era regalar
el literal.
**Decisión pendiente de Javier**, porque tiene tres salidas y ninguna es gratis: ignorar el guion
ahora (no borra el historial público), reescribirlo para que no genere nada (tampoco borra el
historial), o **regenerar con otra semilla** aprovechando que no se ha repartido —que es lo único
que cierra la fuga de verdad, y que hay que hacer de todas formas por M-14—.

**Tres decisiones del enunciado que traje por precedente del Taller 1 y hay que confirmar antes de
publicar**, porque este plan no las fija en ninguna parte: el canal y el nombre del archivo
(**Brightspace**, `T2_Apellido_TuDocumento.pdf`), que **no hay plantilla LaTeX** —el Taller 1 sí la
tenía, `entrega/plantilla_taller1.tex`, y aquí no existe ni hay tarea que la construya— y que **no
se publica límite de páginas**, que preferí omitir antes que inventarlo. La hora límite del martes
6 tampoco está fijada.

**Siguiente: C5b**, y va con las notas del §7.1.
**El calendario se movió el 2026-09-09**: la entrega pasa del 18 de septiembre al **6 de octubre**
y la sustentación al **8**. Eso mueve el taller de la semana 7 a la **semana 10** y le cambia el
papel: ver **§2.2**, que es lo primero que hay que leer si vienes del plan anterior. Este archivo es la fuente de verdad del
Taller 2, igual que `PLAN_Taller_1_Caps_1_2.md` lo es del primero. Lleva el estado de cada paso
(C1…C10), las decisiones ya tomadas y las cuatro mediciones que las sostienen. **Leerlo entero
antes de proponer nada.**

**Lo primero que hay que saber, antes de tocar nada:**

1. **`precalculo/genera_taller2.R` tiene que quedar en `.gitignore`**, por la misma razón que el
   del Taller 1: reproducirlo revela **la familia de cada patrón generado**, que es exactamente
   lo que T2 pide clasificar. Igual `verifica_taller2.R`, que imprime las respuestas. Se versionan
   después de calificar, si Javier lo decide.
2. **Este archivo también queda ignorado** por la lista blanca `/*` de la raíz. Si debe viajar,
   hay que añadir `!/PLAN_Taller_2_Cap_4.md` al `.gitignore` — como ya se hizo con
   `!/PLAN_Preparcial_Corte_1.md` y `!/PLAN_Parcial_Corte_2.md`.
3. **NO volver a ejecutar `genera_taller2.R` después de repartir.** Reasigna las 1000 variantes y
   a cada estudiante le cambia la localidad y el patrón. Para corregir el enunciado se toca el
   **ensamblador**, nunca el precálculo. Es la lección más cara del Taller 1.
4. **El Taller 2 NO reutiliza cifras de otros documentos.** El preparcial del Corte I sí lo hace
   —es el único del sitio que lo hace— y por eso regenerar un capítulo obliga a rehacerlo. Este
   taller calcula lo suyo desde las fuentes, así que **regenerar el capítulo 4 no lo invalida**.
   Esa independencia es deliberada; si alguna tarea empieza a citar una cifra del capítulo, se
   pierde y hay que declararlo aquí.
5. **El banco de este taller se PUBLICA, y el parcial 2 cubre el mismo temario.** El
   `PLAN_Parcial_Corte_2.md` dice en su línea 80 que entra «el banco del Corte II —capítulos 4 y
   5—». Cualquier pregunta que se reutilice entre los dos documentos **es una respuesta ya
   publicada**. Los dos se construyen en la misma ventana —este del 10 al 20 de septiembre, el
   parcial del 21 en adelante— y **ninguno de los dos planes mencionaba al otro** hasta el
   2026-09-09. La guarda va en los dos sentidos y está en el §10 y en C6.

6. **El capítulo 4 ya está cerrado y publicado** (547 KB en el momento de su cierre, **559,7 KB** hoy):
   `Htmls_Espacial/capitulo-4-patrones-puntuales.html`, 12 módulos, 12 preguntas y **5 ejercicios
   guiados**. Tres de esos cinco ejercicios son vecinos peligrosos de tres tareas de este taller.
   Ver **§3.5** y **§3.7**, que son las secciones que hay que leer antes de escribir un solo
   enunciado — y que ahora cubren **dos capítulos**, porque T5 sale del 5.

**La cadena, en orden** (aún no existe ningún archivo de esta lista):

```
precalculo/rscript.sh precalculo/genera_taller2.R      # el precálculo (NO tras repartir)
precalculo/rscript.sh precalculo/datos_taller2.R       # el dato que se descarga el estudiante
python3 precalculo/ensambla_taller2.py                 # el HTML
<geo_env>/python precalculo/audita_taller2.py          # el auditor independiente
python3 precalculo/prueba_auditor_taller2.py           # el arnés de inyección
cd precalculo && python3 audita_texto_taller2.py       # las cifras de la prosa
precalculo/audita_todo.sh --rapido                     # todo junto

precalculo/rscript.sh precalculo/verifica_taller2.R 1012345678   # calificar (C10)
```

`<geo_env>` sale de `precalculo/versiones_py.json`:
`/opt/homebrew/Caskroom/mambaforge/base/envs/geo_env/bin/python`.

---

## 1. El encuadre: qué se evalúa y contra qué se diseña

Mismas tres palancas que el Taller 1 —la restricción no es «que no usen IA», es que **la respuesta
del modelo no sea el entregable**—, pero con **los pesos invertidos**:

| Palanca | Cómo se implementa aquí | Qué neutraliza |
|---|---|---|
| **Dato propio** | Semilla por documento: **su localidad de Bogotá** (ventana real) y **su patrón generado** (familia desconocida) | Copiar de un compañero, o del ejemplo canónico que el modelo ya vio |
| **Refutar, no responder** | Un defecto que el estudiante **produce él mismo** ejecutando el código dado; un informe de un modelo citado literal; una envolvente recortada después de mirar | Preguntar «¿está bien esto?» a un modelo, que contesta que sí |
| **Sostenerlo en vivo** | **Defensa de 60 %** sobre un banco publicado que barre los once módulos | Delegar el informe completo |

Lo que **no** se evalúa: escribir código desde cero, memorizar fórmulas, producir mapas bonitos.
Lo que **sí**: decidir con una cifra en la mano, decir qué *no* prueba un resultado, y detectar un
procedimiento equivocado cuyo resultado se ve perfectamente razonable.

**La diferencia de fondo con el Taller 1** es el 60/40. Allí el escrito llevaba el peso y la
defensa lo confirmaba; aquí la defensa **es** el instrumento y el escrito es la evidencia que se
defiende. Eso tiene tres consecuencias que hay que construir, no suponer:

- el **banco tiene que ser el artefacto más trabajado del taller**, no un anexo;
- el escrito baja a **cuatro tareas**, y cada una debe producir una **decisión defendible**, no
  una respuesta;
- la **rúbrica de la defensa se publica** con el mismo detalle que la del escrito.

---

## 2. Decisiones tomadas (2026-09-09)

| Decisión | Elección | Consecuencia |
|---|---|---|
| **Alcance** | **El capítulo 4 entero: los 11 módulos de contenido** | Corrige el encargo inicial («hasta el módulo 9»). Entran borde (10) y envolventes (11), y con ellos las tres tareas que la pregunta sobre corrección de borde intentaba esquivar |
| **Dato propio** | **Los dos: localidad real + patrón generado** | Dos catálogos y dos auditorías. Es la única forma de cubrir 1–11: la ventana real sostiene 1, 2, 5, 6, 10; el patrón generado es el **único** que sostiene el contraste K–g del módulo 9 (medido, §2.2) |
| **Formato** | **Escrito 40 % + defensa oral 60 %** | Invierte el molde del Taller 1. El banco pasa a ser el instrumento principal |
| ~~Reparto semana 6, entrega viernes 18~~ | **REVISADO (2026-09-09): entrega martes 6 de octubre, sustentación jueves 8** | Mueve el taller a la **semana 10** y le cambia el papel (§2.2). La construcción pasa de 2 días a **27**, y con ella se cae el riesgo que dominaba el §10 |
| Individualización | Por número de documento, **tres últimos dígitos**, 1000 variantes | Igual que el Taller 1, **más el anclaje nuevo del §5.2** |
| Modalidad | Individual, en casa + defensa en clase | La individualización por documento pierde sentido en grupo |
| **Capítulo 5** | **Entra por UNA tarea (T5), no por el banco** (2026-09-09) | El escrito pasa a **cinco tareas del 8 %**. El parcial 2 cubre los capítulos 4 y 5, así que sin T5 media evaluación llegaba sin ensayo. Restringida a los módulos 1–3 por calendario (§10) |
| **Control intermedio** | **Semana 9, tres cifras en clase** (2026-09-09) | Lo hace posible el plazo de 15 días. Atrapa la variante ajena el día 7 en vez del día 30 (§5.3) |
| **Bitácora** | **Obligatoria, media página en la portada** (2026-09-09) | «Comunicación y honestidad» deja de ser un criterio sin artefacto (§6) |
| **Defensa** | **Una sola sesión** (2026-09-09) | 12 × 8 min ≤ 120 min. Cierra la única pregunta que bloqueaba publicar el enunciado, y **obliga al sorteo sin reemplazo del §4.5**: en una sesión nadie sale del aula |

### 2.1 ~~Una consecuencia del alcance~~ · **RESUELTA POR EL CALENDARIO (2026-09-09)**

El plan anterior advertía que, repartiendo en la semana 6, el taller **empujaría** la lectura de
los módulos 10 y 11 antes de verlos en clase, y que el enunciado tendría que decirlo.

**Con la entrega el 6 de octubre esa objeción desaparece**: el capítulo 4 cierra en la semana 7
(18 de septiembre) y el taller se entrega en la 10. Los once módulos están vistos cuando el
estudiante los necesita, y el enunciado no tiene que pedir disculpas por nada. **Es la mejora más
grande que trae el calendario nuevo**, y es gratis.

### 2.2 Dónde cae ahora el taller, y qué le cambia eso

| Semana | Fechas | Qué pasa |
|---|---|---|
| 5 | 31 ago – 4 sep | **Parcial 1** (martes 1) |
| 6 | 7 – 11 sep | capítulo 4 · *hoy* |
| 7 | 14 – 18 sep | capítulo 4 (cierra) |
| 8 | 21 – 25 sep | capítulo 5 · **reparto propuesto: lunes 21** |
| 9 | 28 sep – 2 oct | capítulo 5 |
| 10 | 5 – 9 oct | capítulo 5 (cierra) · **ENTREGA martes 6** · **SUSTENTACIÓN jueves 8** |
| 11 | 12 – 16 oct | **Parcial 2** |

Tres consecuencias, y la tercera es una pregunta abierta que no puedo cerrar yo:

1. **El taller pasa a ser la preparación del parcial 2**, exactamente el papel que el Taller 1 tuvo
   para el parcial 1 (semana 4, parcial en la 5). La sustentación es el jueves 8 y el parcial 2 cae
   en la semana siguiente —**su fecha exacta no está fijada en ningún plan del repositorio**, solo
   «semana 11»—, así que el margen es de al menos cuatro días. Cabe, y el enunciado puede decirlo
   en cuanto la fecha se sepa.
2. **La sustentación ya no es el mismo día que la entrega, son dos días después.** El plan anterior
   no podía suponerlo y ahora sí: **el bloque «su variante» mejora solo**, porque el profesor elige
   qué decisión defiende cada estudiante **habiendo leído su escrito**, en vez de al azar. Recogido
   en el §4.1.
3. **El taller se entrega cuando el capítulo 5 ya se ha visto entero**, y cubre solo el 4. Eso deja
   el capítulo 5 íntegro al parcial 2. **Puede ser lo que quieres o puede no serlo**; es la
   pregunta 6 del §11 y hay que decidirla antes de C1, porque cambia el catálogo de variantes.

### 2.2 Las cuatro mediciones que sostienen el diseño

Ninguna de estas cifras está supuesta. Se midieron el 2026-09-09 sobre
`datos/procesado/bogota_colegios.gpkg` (2 209 sedes, EPSG:9377) y
`bogota_localidades.gpkg` (20 localidades), con el intérprete de `geo_env`.

**M-1 · Las localidades son 20, pero solo 16 sirven.** Excluidas por degeneradas:
La Candelaria (n = 19), Sumapaz (n = 24 sobre 779 km², λ = 0,03/km², rural),
Chapinero (n = 26) y Santa Fe (n = 29). Las 16 restantes van de **n = 35** (Los Mártires) a
**n = 356** (Suba), y de **λ = 0,50/km²** (Usme) a **λ = 8,76/km²** (Rafael Uribe Uribe).
Ese recorrido de 17 veces en λ es lo que hace que dos estudiantes no puedan copiarse una frase.

**M-2 · El defecto del *bounding box* cambia el veredicto en 3 de las 16.**
⚠️ **CORREGIDA AL CONSTRUIR C1 (2026-09-09). La primera versión de esta tabla era de UNA cola y el
estudiante verá DOS.** Ver M-6. Estas son las cifras que da R, con la pertenencia geométrica de M-7
y rejilla 5×5:

| Localidad | p sobre la caja | p sobre el polígono | ¿cambia el veredicto? |
|---|---|---|---|
| Antonio Nariño | < 0,0001 | **0,4536** | **sí** |
| Rafael Uribe Uribe | < 0,0001 | **0,1926** | **sí** |
| Barrios Unidos | 0,0106 | **0,0936** | **sí** |
| Los Mártires | 0,0605 | 0,9801 | no — **la caja tampoco rechaza** |
| Tunjuelito | < 0,0001 | 0,0006 | no |
| Suba, Kennedy, Engativá, … | < 0,0001 | < 0,0001 | no |

**Consecuencia de diseño, que no cambia:** T1 no puede pedir «¿cambió el veredicto?» como si fuera
la pregunta —solo le toca a tres—; la pregunta es **cuánto se movió el χ²** y qué dice el supuesto.
El cambio de veredicto es el caso extremo, y hace que T1(d) —«un compañero dice que a él también le
rechazó»— tenga sustancia real en el aula.

**M-3 · El supuesto del χ² se cae, y se cae de forma distinta para cada estudiante.** Con
rejilla 5×5 sobre **una** localidad, la fracción de celdas con esperanza menor que 5 va del
**14 % en Suba** (3 de 22, n = 356) al **100 % en cuatro localidades** —Barrios Unidos,
Teusaquillo, Antonio Nariño y Los Mártires—, donde **ninguna celda llega a 5** y el χ² no es
interpretable en absoluto. La esperanza media por celda va de **16,2** (Suba) a **1,7** (Los
Mártires), y en **siete de las 16** hay alguna celda con esperanza ≈ 0.

| Localidad | n | celdas | esperanza < 5 | esperanza media |
|---|---|---|---|---|
| Suba | 356 | 22 | 3 (14 %) | 16,2 |
| Engativá | 258 | 19 | 6 (32 %) | 13,6 |
| Usaquén | 130 | 22 | 8 (36 %) | 5,9 |
| Tunjuelito | 68 | 19 | 10 (53 %) | 3,6 |
| Teusaquillo | 56 | 20 | **20 (100 %)** | 2,8 |
| Los Mártires | 35 | 20 | **20 (100 %)** | 1,7 |

**Consecuencia:** para cuatro de los estudiantes la respuesta correcta de T1 es *«ninguno de los
dos p-valores es interpretable con esta rejilla»* —ni el de la caja ni el del polígono—, y para
Suba el 5×5 es defendible. De ahí sale sola la cadena módulo 5 (supuestos) → módulo 6 (tamaño de
celda) → módulo 1 (la ventana forma parte del estimador). **Es el mejor hallazgo de la medición**,
y hay que escribir T1 alrededor de él y no alrededor del cambio de veredicto, que solo le toca a
tres (M-2).

**M-4 · El contraste K–g del módulo 9 NO existe sobre el dato real, y sí sobre el generado.**
Medido con referencia por simulación de CSR **dentro de la propia ventana** (60 réplicas), sobre
las seis localidades grandes: los colegios se agrupan a **todas** las escalas —λ no es homogénea—
y K y g dicen lo mismo. Solo Teusaquillo muestra el contraste (g = 0,70 en r = 1 000 m mientras
K = 1,34). Sobre procesos de Thomas generados, en cambio, el contraste es limpio y reproducible:

| σ del cúmulo | n | g máximo | g vuelve a ~1 en | K en r = 0,20 | g en r = 0,20 |
|---|---|---|---|---|---|
| 0,02 | 148 | 15,44 | r = 0,070 | **1,43** | **0,84** |
| 0,03 | 178 | 6,22 | r = 0,085 | **1,24** | **1,07** |
| 0,05 | 222 | 2,62 | r = 0,165 | **1,28** | **0,93** |

**Consecuencia:** el módulo 9 se evalúa sobre el patrón generado, y el dato real sirve para la
otra mitad de la lección —«aquí sí hay agregación a toda escala, y la razón es que λ no es
constante», que es el módulo 2 y el puente al capítulo 5—.

**M-6 · R y Python dan p-valores distintos sobre el MISMO χ², y R es quien manda aquí.**
Encontrado al construir C1: el cruce R↔Python del generador reventó su ancla. Sobre Antonio Nariño
los dos calculan **χ² = 12,1443 con 16 g.l.**, con las mismas 17 esperadas y las mismas observadas
—dígito a dígito—, y publican **p = 0,4536 (R) y p = 0,7340 (Python)**. Ninguno está mal:
`quadrat.test()` de spatstat es de **dos colas por defecto** y el `1 - chi2.cdf()` de scipy es la
cola superior. `2 × min(0,266, 0,734) = 0,532`, y sobre el n geométrico, 0,4536.

**Manda R**, por dos razones que no son de gusto: el estudiante corre R, y **el capítulo 4 llama a
`quadrat.test()` con el defecto en sus cuatro apariciones**, así que el taller tiene que decir lo
mismo que el capítulo. Y no es un decimal: **el conjunto que vuelca cambia con la convención** —a
dos colas son Antonio Nariño, Rafael Uribe y Barrios Unidos; a una eran Antonio Nariño, Rafael
Uribe y **Los Mártires**—. Si esto se hubiera colado, tres estudiantes habrían defendido una
respuesta que su propio R contradice.

**M-7 · Siete sedes de 2 209 no están en la localidad que su `cod_loca` dice.** Seis caen dentro de
**otra** localidad y una no cae dentro de ninguna, a distancias de **0,57 m a 219,20 m** (mediana
11,28). Ninguna está sobre dos polígonos a la vez.

**La regla del taller es GEOMÉTRICA** —«tus sedes son las que caen dentro del polígono de tu
localidad»— porque es la que el estudiante obtiene: él construye el `ppp` con el polígono como
ventana y `ppp()` descarta lo de fuera. Nueve localidades cambian de n, y **Antonio Nariño gana
una** (42 → 43), lo que mueve su χ² y su p. Si el enunciado publicara el n del atributo, la primera
cifra del taller no le cuadraría al estudiante y el resto se leería con desconfianza.

**M-8 · T4(a) tiene contraste de sobra.** El cociente perímetro/área va de **0,507 km⁻¹ en Usme** a
**2,479 en Antonio Nariño**, un factor de **4,9**. El par de contraste de cada estudiante sale de
ahí y no de un sorteo: se empareja con la localidad más lejana en ese cociente.

**M-5 (de regalo) · Los duplicados exactos son reales y están mal repartidos.** Sedes que
comparten coordenada exacta con otra: **22 en Suba**, 17 en Engativá, 8 en Usaquén y en Bosa,
6 en Kennedy, **0 en San Cristóbal, Antonio Nariño y Los Mártires**. Es G(0) > 0 y es un problema
del dato, no del modelo. Es la reserva de T1 si la adyacencia con `e3` resulta demasiado estrecha
(§3.5).

**M-9 · El estadístico de T5 que el plan tenía escrito no servía, y el buscador se pegaba al borde.**
El plan decía «un informe afirma que hay N focos». Medido: contar componentes conexas es un
**entero grosero** —en San Cristóbal vale 1 con los cuatro selectores y con casi cualquier σ, y lo
mismo en Antonio Nariño y Los Mártires, así que allí no hay nada que refutar—; y maximizar la
separación empujaba σ al extremo inferior y hacía que el informe afirmara **41 focos en Suba**, un
número que nadie escribiría.

Sustituido por **pico / intensidad media**, que es continuo, está siempre definido y lo separan los
cuatro selectores en las dieciséis —de **1,45 en Teusaquillo a 5,83 en Fontibón**—. Y con una
segunda corrección: **el σ sembrado tiene que caer DENTRO del rango de los cuatro selectores**. Si
cae fuera, el defecto se descarta de un vistazo; dentro, el informe usó un ancho que cualquier
selector habría devuelto, y la refutación pasa a ser la buena —«entre anchos igualmente defendibles
la cifra se mueve por un factor de X»—, que es el módulo 2 del capítulo 5. Los candidatos incluyen
los propios σ de los selectores, y con eso **el informe queda contradicho por al menos 2 de los 4
en las dieciséis**.

**M-10 · El diseño de T4(b) que este plan daba por bueno NO funciona.** Decía: dos envolventes del
mismo patrón, la completa y una con el rango de r recortado *post hoc*, y que la segunda saliera
significativa. Medido sobre **30 patrones de CSR con nsim = 39** y **15 con nsim = 999**: el recorte
posterior **no fabrica significancia de forma fiable** —con 39 el p de `dclf.test` es discreto con
suelo 1/40 y nunca bajó de 0,05; con 999 tampoco se consiguió en 120 intentos—. Se comprobó aparte
que **`rinterval` sí se respeta** (el estadístico y el p cambian con el intervalo): el diseño era el
equivocado, no la implementación.

**Se activó el repuesto que este plan ya tenía escrito.** Con nsim = 39 y nrank = 1 la banda es
puntual al 5 %, y **17 de 30 patrones de CSR se salen de ella en algún nodo**. El informe lee esa
salida como «significativo»; el estudiante cuenta los nodos, los compara con los esperados y corre
el test global —que **no rechaza en ninguna de las 12 envolventes publicadas**, con p de 0,350 a
1,000—. Es la inspección múltiple del módulo 11, medida y no afirmada, y nsim = 39 es además lo que
usa el propio módulo 11 del capítulo 4.

**M-11 · El peso, medido y declarado.** Los dos JSON suman **698,5 KB**: 531,0 de datos —296 de
envolventes, 131 de las 1000 variantes, 98 de los tríos, 65 de los patrones— y 167,5 de mapas.
Bajó de 924 KB por **dos vías que no tocan el contenido**: seis decimales en vez de diez en las
curvas de envolvente —el décimo decimal de una K en la ventana unidad es ruido de coma flotante— y
**600 vértices por localidad en vez de 8 000**, que es el presupuesto pensado para los 1 122
municipios y no para dieciséis contornos pequeños. Lo que queda es contenido: las envolventes van
en la rejilla de 513 nodos de spatstat porque el recuento de nodos fuera de banda que T4(b) pide
contar se hace sobre ella.

**M-12 · T4(a) tiene respuesta, y por poco.** El déficit de K sin corregir va del **20,3 % en
Usaquén al 33,9 % en Engativá**, y siempre en la misma dirección —las dieciséis—. Su correlación
con perímetro/área es **0,586**: predice, pero no con holgura. La guarda del guion para por debajo
de 0,5, así que si al regenerar bajara, T4(a) habría que reescribirla.

---

## 3. Diseño del escrito: cinco tareas · 40 %

### T1 · La ventana que no declaraste · 8 % · mód. 1, 2, 5, 6

El estudiante **produce el defecto él mismo** —la palanca de T5 del Taller 1, que fue la que mejor
funcionó—. Se le da el código que construye el `ppp` de las sedes de **su** localidad con una
ventana rectangular sobre el rango de coordenadas, y el mismo código con el polígono. Corre los dos
tests de cuadrantes. Nadie le dice qué está mal.

- (a) λ bajo las dos ventanas, y **qué fracción de tu caja cae fuera de tu localidad** (medido sobre
      las 16: del **32,8 % en Kennedy al 61,7 % en Usme**). ¿De qué es intensidad la cifra de la caja, si no
      es de tu localidad?
- (b) Los dos χ² y los dos p. Nombra el síntoma **antes** de arreglarlo.
- (c) Comprueba el supuesto **antes** de leer ningún p-valor: cuenta cuántas de tus celdas tienen
      esperanza menor que 5 y da el porcentaje. Después decide **con esa cifra tuya** si tu
      p-valor se puede leer o no, y si no se puede, encuentra la rejilla más fina con la que sí, y
      di qué veredicto da. (Medido: va de 3 de 22 en Suba a 20 de 20 en Los Mártires — a cuatro
      estudiantes les toca responder que **no hay p-valor legible** con la rejilla que se les da.)
- (d) Un compañero dice: «a mí también me rechazó con la caja, así que el error no importa».
      Refútalo con **su** cifra y con la tuya.
- (e) ¿Por qué este defecto **no** se vería mirando el mapa?

> **Dónde muerde la IA:** preguntada «¿está bien este test de cuadrantes?», dice que sí. Y (c) y
> (d) tienen **respuestas distintas según la localidad** (M-2, M-3): quien copie, se delata.

### T2 · El régimen que las dos funciones no ven igual · 8 % · mód. 3, 7

Sobre **su patrón generado**, de familia desconocida. Se le entregan G y F —suyas y de dos patrones
señuelo— junto a los **tres mapas sin etiquetar**.

- (a) Empareja cada par (G, F) con su mapa. Justifica con lo que mira cada función, no con el
      parecido de las curvas.
- (b) Clasifica el régimen de **el tuyo** y di a qué escala lo estás afirmando.
- (c) G y F pueden no decir lo mismo. Si en el tuyo discrepan, explica por qué; si coinciden,
      construye el caso en que discreparían.

> **Dónde muerde la IA:** el emparejamiento exige leer tres pares de curvas contra tres mapas, y
> ninguna de las seis figuras existe fuera de este taller.

### T3 · Dónde está la estructura · 8 % · mód. 8, 9

Mismo patrón generado. Se le entregan K, L − r y g. Y se le entrega, **citado literal**, un informe
de un modelo de lenguaje que concluye: *«la curva L − r es positiva hasta r = 0,20, luego el patrón
está agregado hasta esa distancia»*.

- (a) ¿Es cierta esa conclusión? Refútala o confírmala **con g**, y di en qué r ocurre de verdad
      la agregación.
- (b) Da **las dos cifras** de tu patrón: el r donde g alcanza su máximo y el r donde g vuelve a
      1, y el valor de K en ese segundo r. Con esas tres cifras, escribe la frase que el informe
      tendría que haber escrito.
- (c) Ahora sobre **tu localidad real**: K y g dicen lo mismo a todas las escalas. ¿Contradice eso
      lo que acabas de responder? (No: es λ inhomogénea, y eso es el módulo 2.)

> Medido en M-4: en el generado, g ya volvió a ~1 donde K sigue en 1,24–1,43. En el real, no.
> La tarea vale porque el estudiante tiene **los dos casos en la mano**.

### T4 · El borde y la banda · 8 % · mód. 4, 10, 11

Dos mitades, las dos de refutación.

- (a) **El borde.** Se le da el sesgo de K sin corregir, medido en **su** localidad y en una de
      forma opuesta (una compacta y una alargada). ¿En qué dirección empuja el sesgo, y por qué
      siempre en la misma? ¿Por qué el cociente perímetro/área predice cuál de las dos sufre más?
- (b) **La banda.** Se le dan **dos** envolventes del mismo patrón con las mismas simulaciones: la
      completa, y una con el rango de r **recortado después de mirar la curva**. La segunda «sale»
      de la banda; la primera no. Di qué está mal y por qué el p-valor de la segunda no es un
      p-valor.
- (c) La envolvente simula CSR. De las dos propiedades que definen CSR, **¿cuál de las dos está
      usando `envelope()` cuando genera cada réplica con el mismo n que tu patrón, y cuál está
      dando por buena sin comprobarla?**

> **Dónde muerde la IA:** en (b), preguntada por la envolvente recortada, la lee como significativa.

### T5 · El mismo problema con otro mando · 8 % · cap. 5, mód. 1–3

**La tarea que cierra el hilo del MAUP, y la única que sale del capítulo 4.** El estudiante lleva
tres capítulos encontrándose la misma pregunta con tres nombres: el tamaño de la unidad en el
capítulo 3, el tamaño del cuadrante en el módulo 6 del capítulo 4, y ahora el ancho de banda.

Recibe un informe que afirma: *«en tu localidad hay N focos de concentración de sedes»*, sostenido
con un mapa de intensidad por núcleos hecho con un σ **que alguien eligió**. El σ va en el
enunciado, así que **el estudiante reproduce el mapa él mismo** — la palanca de T1, y aquí además
sale gratis en peso: el taller no publica ninguna superficie.

- (a) Reproduce el mapa. ¿Ves los N focos?
- (b) Vuelve a estimarlo con los cuatro selectores del módulo 3. ¿Cuántos focos hay ahora? ¿La
      afirmación del informe sobrevive a alguno de los cuatro?
- (c) **En T1 elegiste una rejilla y aquí un ancho.** ¿Cuál de las dos decisiones movió más tu
      conclusión, y por qué son **la misma decisión** con dos nombres?
- (d) Elige el σ que defenderías ante la Secretaría de Educación y sostén la elección. «El que
      da bw.diggle» no puntúa si no dices qué optimiza.

> **Por qué esta y no la del ancho de banda a secas:** el capítulo 5 ya publica `e1` sobre los
> cuatro selectores y tres preguntas más sobre el ancho (§3.7). Lo que **ningún** documento del
> curso hace es **juntar los dos mandos**, y menos aún contra la decisión que el propio estudiante
> tomó en T1. Esa referencia a su propia respuesta anterior es indelegable por construcción.

> **Por qué los módulos 1–3 y no más:** el capítulo 5 va por las semanas 8–10 y la entrega es el
> **martes 6 de octubre**, el segundo día de la semana 10. Los módulos tardíos del capítulo 5 —la
> K inhomogénea vive en el **módulo 10**— no están garantizados a esa fecha. T5 se queda en lo que
> con seguridad se ha visto al cerrar la semana 9. Ver el riesgo en el §10.

### T-todas · La bitácora · requisito de entrega, no tarea

Media página, obligatoria, en la portada: **qué consultó con IA, qué verificó y cómo**. Hoy la
rúbrica pide honestidad en su dimensión de Comunicación (10 %) y **no pide ningún artefacto donde
calificarla**. Con quince días de plazo —tiempo de sobra para delegar bien y pulir— esa dimensión
necesita algo que se pueda leer y contrastar en la sustentación. Sin bitácora, la entrega está
incompleta.

### 3.5 Los tres vecinos peligrosos — leer antes de redactar

El capítulo 4 publica cinco ejercicios guiados. **Tres de ellos rozan tres de estas cuatro
tareas**, y una tarea que repita un ejercicio ya resuelto no evalúa nada:

| Ejercicio del capítulo | Tarea vecina | En qué se diferencian — y qué hay que vigilar |
|---|---|---|
| **e3 · El cuadrante que rechaza por el motivo equivocado** (rejillas 2×2 a 20×20 sobre las sedes de **toda** Bogotá, urbano vs. D.C.; pide contar celdas vacías y esperanzas < 5) | **T1** | e3 compara **dos ventanas legítimas** y barre el tamaño de rejilla; T1 compara **una ventana correcta contra un defecto de procedimiento** sobre **una** localidad individual. **Es la adyacencia más estrecha del taller.** La reserva que este plan tenía escrita —los duplicados exactos— **no sirve tal cual**: es la pregunta 8 del quiz del propio capítulo (§3.7). Si T1 hay que rehacerlo, la reserva buena es la **fracción de la caja que cae fuera** (31 % a 67 %, M-2), que no aparece en ningún ejercicio ni en ninguna pregunta |
| **e5 · El borde empuja siempre hacia el mismo lado** (pide calcular K con `none`, `border` y `translate`, y comparar Clark-Evans con Donnelly) | **T4(a)** | e5 pide **calcular** las tres correcciones; T4(a) **entrega el sesgo ya medido** y pregunta por la **forma de la ventana** —perímetro/área— que e5 no toca. T4(a) NO debe pedir calcular las tres correcciones |
| **e4 · La envolvente dice una cosa y el test otra** (999 simulaciones, cuenta nodos fuera de la banda, dclf sobre K y sobre L, con r restringido al 20 % y al 40 %) | **T4(b)** | **e4 ya restringe el rango de r.** La diferencia es que en e4 la restricción es **declarada de antemano** y en T4(b) es **post hoc, después de mirar la curva**, que es el pecado del módulo 11. Es una diferencia real pero fina. **El repuesto que este plan tenía escrito —el `nsim` de 39 a 999— tampoco sirve: es la pregunta 12 del quiz** (§3.7). Si T4(b) se cae, el repuesto es **la inspección múltiple entre los doce**: con doce estudiantes probando cada uno su localidad al 5 %, ¿cuántos «encontrarían algo» aunque no hubiera nada? |

| **`e1` del capítulo 5 · El selector que no seleccionó** (los cuatro selectores sobre tres patrones canónicos; encontrar el que devolvió el extremo del intervalo) | **T5(b)** | e1 pide **detectar un selector roto** sobre patrones canónicos; T5(b) usa los cuatro selectores como **instrumento para refutar una afirmación** sobre su propia localidad. Adyacente y vigilada: T5 **no** debe pedir encontrar el selector que falló |

Los otros dos del capítulo 4 —e1 (las tres ventanas de Bogotá, λ) y e2 (el χ² ciego,
`swedishpines`)— no tienen tarea vecina. Y **ninguna de las 12 preguntas de autoevaluación del capítulo** debe reaparecer en el
banco de la defensa; hay que cotejarlas una a una en C6.

### 3.7 El cotejo contra las 12 preguntas del capítulo — **lo que el §3.5 no miraba**

El §3.5 cotejaba las tareas contra los **cinco ejercicios guiados**. Faltaba la otra superficie:
las **12 preguntas de autoevaluación**, que también están publicadas y también son respuestas que
el estudiante ya tiene. Hecho el cotejo el 2026-09-09, aparecieron **dos duplicados literales** y
tres adyacencias. Los dos literales ya están corregidos arriba; queda el registro para que no
vuelvan:

| Pregunta del capítulo | Chocaba con | Veredicto y qué se hizo |
|---|---|---|
| **5** · «¿Cuáles son las DOS propiedades que definen CSR?» | **T4(c)**, que pedía enunciarlas | **Duplicado literal.** T4(c) reescrita: ya no pide enunciarlas, pide **cuál de las dos usa `envelope()` al simular y cuál da por buena sin comprobar** |
| **9** · «K(r) sigue por encima a 500 m aunque la agregación ocurre a 20 m. ¿Por qué?» | **T3(b)**, que pedía el mecanismo | **Duplicado literal.** T3(b) reescrita: ya no pide el mecanismo, pide **tres cifras de su propio patrón** y la frase que el informe tendría que haber escrito |
| **8** · «G(0) = 0,037494 en la ventana urbana. ¿Cuántas sedes comparten coordenada exacta?» | La **reserva** de T1 (duplicados exactos) | **La reserva no servía.** Sustituida por la fracción de la caja que cae fuera —32,8 % a 61,7 % según la localidad— (§3.5) |
| **12** · «De 39 a 999 simulaciones, ¿qué le pasa a la banda?» | El **repuesto** de T4(b) | **El repuesto no servía.** Sustituido por la inspección múltiple entre los doce (§3.5) |
| **1** · «5,7 colegios por km², ¿qué le falta?» | **T1(a)** | Adyacente, y además solapaba con `e1`. T1(a) reescrita para pedir **la fracción de caja fuera de la localidad**, que es una cifra suya y no una pregunta retórica |
| **4** · «rechaza con 5×5 y no con 2×2, ¿qué se hace?» | **T1(c)** | Adyacente. T1(c) anclada a **su** porcentaje de celdas con esperanza < 5 y a encontrar la rejilla que sí sirve, que exige el dato propio |
| **3**, **7**, **10**, **11** | T1(d), T2, T4(a), T4(b) | Adyacencias aceptables: el quiz pide reconocer, la tarea pide **decidir con una cifra propia** |

**El mismo cotejo, hecho para T5 contra el capítulo 5 (2026-09-09).** La regla de abajo se aplicó
a sí misma en cuanto apareció T5, y **cambió el diseño de la tarea antes de escribirla**:

| Superficie del capítulo 5 | Qué ocupa | Efecto sobre T5 |
|---|---|---|
| **`e1` · El selector que no seleccionó** | los cuatro selectores de ancho | T5 los usa como instrumento, no como objeto |
| **Pregunta 1** · «una usó `bw.diggle` y la otra `bw.scott`, ¿qué se concluye?» | **el ángulo que T5 iba a tener** | **Mató el primer diseño de T5.** Era «el ancho que decide el mapa», que es esta pregunta con más palabras |
| **Pregunta 7** · núcleo vs. ancho, cuál mueve más el mapa | la comparación **dentro** del capítulo 5 | T5(c) compara **entre capítulos** —rejilla del cap. 4 contra ancho del cap. 5—, que no hace nadie |
| **Pregunta 8** · un selector devuelve exactamente el extremo | el mismo terreno que `e1` | vigilado |
| **Pregunta 9** · cuál de los tres mapas es «la demanda» | el módulo 5 | T5 no entra ahí |

**Cuatro superficies sobre el ancho de banda ya publicadas.** Por eso T5 acabó siendo la unión de
los dos mandos contra la decisión que el propio estudiante tomó en T1, que es lo único de ese
terreno que nadie ha publicado — y que **no se puede duplicar por construcción**, porque cita su
respuesta anterior.

**La regla que sale de esto, y vale para el banco de C6:** en este repositorio, antes de escribir
un enunciado hay que cotejarlo contra **dos** superficies publicadas, no una — los ejercicios
guiados **y** las preguntas de autoevaluación—. El §3.5 solo miraba la primera y por eso dejó pasar
dos duplicados literales y dos repuestos muertos. C6 lo hereda como criterio de aceptación.

---

### 3.6 Cobertura del temario

| Módulo | Escrito | Defensa |
|---|---|---|
| 1 · Qué es un proceso puntual (la ventana) | **T1** | sí |
| 2 · La intensidad λ | **T1**, T3(c) | sí |
| 3 · Los tres regímenes | **T2** | sí |
| 4 · CSR | T4(c) — **solo de refilón** | **núcleo del banco** |
| 5 · El test de cuadrantes | **T1** | sí |
| 6 · El tamaño del cuadrante (MAUP) | **T1** | sí |
| 7 · Las funciones G y F | **T2** | sí |
| 8 · La función K de Ripley | **T3** | sí |
| 9 · La correlación de pares g(r) | **T3** | sí |
| 10 · Efectos de borde | **T4(a)** | sí |
| 11 · Envolventes de simulación | **T4(b)** | sí |
| **cap. 5** · 1–3 (KDE, ancho de banda, selectores) | **T5** | solo en «su variante» |

Los once módulos del capítulo 4 entran en el escrito, **más los módulos 1–3 del capítulo 5 por
T5**. El banco de la defensa se queda **íntegramente en el capítulo 4** (§4.2): diluirlo debilitaría
la profundidad sobre el capítulo del que va el taller, y T5 queda defendible igual por el bloque
«su variante», que es el 30 % de la sustentación.
**El módulo 4 del capítulo 4 es el único que el escrito apenas toca**, y es
deliberado: es el más conceptual, el más fácil de responder con una frase memorizada y el que mejor
se evalúa en vivo. El banco lo cubre a fondo.

---

## 4. La defensa · 60 %

Con la defensa al 60 % deja de ser una confirmación y pasa a ser **el instrumento**. Eso obliga a
tres cosas que el Taller 1 no necesitaba:

**4.1 · Estructura fija, publicada en el enunciado. Una sola sesión, el jueves 8 de octubre**
(decidida el 2026-09-09; fecha fijada el mismo día).

Los **dos días** entre la entrega (martes 6) y la sustentación (jueves 8) no son holgura: son lo
que hace que el bloque «su variante» sea una defensa y no una lotería. Doce escritos leídos en dos
días es trabajo real y hay que contarlo — es la tarea **C11** del §8.

La asignatura tiene **4 h/semana** (2 créditos, 63 h presenciales), es decir **sesiones de 2 h**.
La restricción es aritmética y hay que escribirla, porque de ella sale todo lo demás:

```
12 estudiantes × (7 min de defensa + 1 min de transición) = 96 min
120 min de sesión − 96 = 24 min de margen para apertura, cierre e imprevistos
```

**Siete minutos por estudiante**, no nueve. El plan preveía 9 y no caben: 12 × 10 = 120 no deja
margen ninguno. Los tres bloques se conservan y se conservan sus pesos; lo que se acorta es cada
uno:

| Bloque | Tiempo | Qué es | Peso dentro de la defensa |
|---|---|---|---|
| **Su variante** | 2 min | Defiende **una** decisión de su escrito, elegida por el profesor **habiendo leído el escrito** (§2.2, punto 2) | 30 % |
| **Banco** | 3 min | **Tres** preguntas de un banco de 36 publicado, ~1 min cada una | 45 % |
| **Refutación en vivo** | 2 min | Se le lee una afirmación falsa sobre el capítulo; dice por qué lo es | 25 % |

**Las tres preguntas del banco se conservan**, y son lo primero que habría sido tentador recortar.
No se recorta porque son el 45 % de la defensa y la defensa es el 60 % del taller: bajar a dos
preguntas deja el 27 % de la nota del curso colgando de **dos** preguntas sacadas de 36. Lo que se
acorta es el tiempo por pregunta, que para preguntas conceptuales de un banco publicado —que el
estudiante ha podido preparar— es suficiente.

> **Si la sesión resulta ser de 90 min y no de 120**, la aritmética no da: 12 × 8 = 96 > 90. En ese
> caso el bloque de **refutación en vivo pasa al escrito** como quinta tarea corta, la defensa baja
> a 5 min (2 + 3) y son 72 min. Se decide **antes** de publicar, porque la estructura va dentro del
> enunciado.

**4.2 · El banco: 36 preguntas, publicado con el taller.** El número **no es redondo por gusto**:
es 12 × 3, que es lo que exige el sorteo sin reemplazo del §4.5. Reparto por módulo, con el módulo
4 sobre-representado por el §3.6:

| Módulos | Preguntas cada uno | Total |
|---|---|---|
| **4 · CSR** (el que el escrito apenas toca) | **6** | 6 |
| 1, 2, 3, 5, 6, 7, 8, 9, 10, 11 | 3 | 30 |
| | | **36** |

Ninguna puede repetir una de las **12 preguntas de autoevaluación** del capítulo ni uno de sus
**5 ejercicios guiados** — las dos superficies del §3.7, que es donde este plan ya se equivocó una
vez.

**4.3 · La regla que le da dientes al conjunto**, igual que en el Taller 1 y ahora con más peso:
**una decisión entregada por escrito que no se puede sostener en la defensa se recalifica.**
Va en el enunciado, no en el correo.

**4.4 · Rúbrica propia de la defensa**, publicada, con cuatro niveles por bloque.

**4.5 · El problema que crea la sesión única, y su solución exacta.**

Con **una sola sesión nadie sale del aula**: el duodécimo estudiante ha oído las preguntas de los
once anteriores. Con un banco de 30 y tres preguntas por estudiante son **36 extracciones sobre 30
preguntas**, así que la repetición no es probable, es **segura** — y el que defiende al final tiene
una ventaja que no se ha ganado.

**La solución es aritmética, no disciplinaria: banco de 36 y sorteo SIN REEMPLAZO entre los doce.**
36 = 12 × 3. Cada estudiante recibe tres preguntas que **no le han hecho a nadie antes**, el banco
se agota exactamente al terminar, y el orden dentro de la sesión deja de importar para ese bloque.

Los otros dos bloques ya eran inmunes y conviene decir por qué: **«su variante» es individualizado
por construcción** —cada uno defiende su localidad y su patrón— y **la refutación en vivo** usa una
afirmación falsa distinta por estudiante, extraída de un segundo catálogo de 12. Eso hay que
construirlo en C6: **no basta con una lista de afirmaciones falsas, hacen falta doce.**

Consecuencia operativa para el día de la defensa: **el sorteo se hace antes de la sesión, no
durante**, y queda registrado. Sortear en vivo sin reemplazo con doce estudiantes es una fuente de
error humano en el peor momento posible.

---

## 5. La individualización

### 5.1 El reparto

R precalcula **1000 variantes**, indexadas por los **tres últimos dígitos** del documento. El
navegador **no calcula nada**: el estudiante escribe su documento y el componente busca la fila.
Cada variante fija cuatro cosas:

1. **su localidad** — una de las **16** usables (M-1);
2. **su patrón generado** — uno de ~24, con familia desconocida;
3. **su localidad de contraste** para T4(a) — de forma opuesta a la suya (perímetro/área);
4. **el recorte de r** de la envolvente de T4(b).

Con 16 localidades y 12 estudiantes hay colisión segura de localidad entre algunos; **eso está
bien**, porque la variante es el par (localidad, patrón) y esos sí son 1000 distintos. Lo que
`verifica_taller2.R` debe comprobar antes de repartir es que **no haya dos de los 12 con la misma
fila**, exactamente como en el Taller 1.

**Criterio de no degeneración** para C1: ninguna variante con n < 35, ninguna con λ fuera del rango
medido, y ningún patrón generado cuya G y F sean indistinguibles de las de otro del mismo trío de
T2.

### 5.2 El anclaje nuevo · la lección del 2026-09-03

Al calificar el Taller 1, **tres estudiantes de doce resolvieron una variante que no era la suya**
—Jerónimo tecleó 102 en vez de 480, López 181, Páez 103— cada uno de forma coherente de punta a
punta. El dígito de verificación **no atrapa ese error**: le cuadra a quien resolvió otra variante
entera. La causa raíz es que el estudiante **nunca veía su propio documento reflejado**: escribía
tres dígitos y recibía un municipio.

**Corrección para este taller, y es barata:**

- el buscador pide el **documento completo**, no los tres últimos dígitos, y **lo imprime en
  pantalla tal como se tecleó**, junto a la localidad y el patrón asignados;
- el enunciado exige que **esa línea completa se copie literal en la portada del informe**;
- `verifica_taller2.R` compara la línea de la portada contra el documento **de la lista del curso**
  y **para** si no cuadran, antes de calificar nada.

Un estudiante que teclee 102 en vez de 480 verá **su propio documento mal escrito** en la portada
que él mismo copia. Eso sí se ve. No es infalible, pero mueve la detección de *después de
calificar* a *antes de entregar*, que es donde sirve.

### 5.3 El control de la semana 9 · **lo que el calendario nuevo hace posible**

Con siete días de plazo no cabía. Con **quince**, sí: en una clase de la **semana 9** (28 sep – 2
oct), cada estudiante enseña **tres cifras** —su localidad, su n y su λ— y nada más. Cinco minutos
para los doce, quince contando las preguntas.

Sirve para tres cosas, y ninguna la resuelve el §5.2 solo:

1. **Atrapa la variante ajena el día 7 en vez del día 30.** Basta con cotejar doce pares
   (documento, localidad) contra la lista. El desastre del Taller 1 —tres de doce— se habría
   detenido aquí.
2. **Atrapa al que no ha empezado**, con tiempo de reaccionar.
3. **Atrapa un fallo del taller**, si lo hay: doce estudiantes leyendo su asignación a la vez son
   la primera prueba de campo del buscador de variantes.

Es la tarea **C10b** del §8. No se califica: es un control, no un entregable.

### 5.4 Lo que el JSON publicado NO puede contener

El ensamblador incrusta el JSON entero en el HTML, así que **todo lo que el precálculo publique es
legible en el código fuente de la página**. Por lo tanto el JSON lleva enunciados, asignaciones,
curvas y salidas a auditar, y **ninguna respuesta**: ni la palabra «familia», ni el régimen de
ningún patrón, ni cuál de las dos ventanas de T1 es la correcta, ni cuál envolvente de T4(b) es la
recortada. Lo comprueba `audita_taller2.py` con una guarda explícita, y también contra el JSON ya
incrustado en el HTML.

---

## 6. Rúbrica del escrito

Se publica **dentro** del taller. Misma estructura que la del Taller 1 —que ya funcionó— con una
dimensión repesada por el 60/40:

| Dimensión | Peso | Qué distingue el nivel alto |
|---|---|---|
| Apropiación conceptual | 20 % | Usa el concepto para decidir, no para definir |
| Interpretación de resultados | 25 % | Dice qué significa **y qué no** significa la cifra |
| Comprensión del procedimiento | 20 % | Explica por qué el procedimiento hace lo que hace |
| Auditoría y refutación | 25 % | Detecta el defecto con evidencia interna |
| Comunicación y honestidad | 10 % | **La bitácora** (§3, «T-todas»): declara qué consultó con IA, qué verificó y cómo — y lo sostiene en la sustentación |

«Auditoría y refutación» sube de 20 a 25 % porque **cuatro de las cinco** tareas son de refutación.
Y «Comunicación y honestidad» deja de ser un criterio sin artefacto: se califica sobre la
**bitácora**, que es media página obligatoria en la portada. Sin ella la entrega está incompleta —
con quince días de plazo, una dimensión de honestidad que no se apoya en nada legible no se puede
calificar.
**Y es la dimensión donde se descuenta resolver la variante ajena**, con piso de 6 para que la
penalización no empuje ninguna celda a «No logrado» — el precedente que fijó Javier el 2026-09-03.

---

## 7. Arquitectura de construcción

Misma cadena que un capítulo, para que herede el arnés en lugar de estrenar uno:

```
precalculo/genera_taller2.R        → salidas/taller2_datos.json + taller2_mapas.json
                                     (catálogo del cap. 4 + el σ sembrado de T5, del cap. 5)
precalculo/datos_taller2.R         → entrega/datos/taller2_*.gpkg   (lo que descarga el estudiante)
precalculo/ensambla_taller2.py     → Htmls_Espacial/taller-2-cap-4.html
precalculo/audita_taller2.py       → recalcula el precálculo en Python (geo_env)
precalculo/audita_texto_taller2.py → las cifras de la prosa (usa audita_texto_base)
precalculo/prueba_auditor_taller2.py → el arnés de inyección
precalculo/verifica_taller2.R      → NO se despliega: recalcula un documento para calificar
```

**Nada de esta cadena hay que enchufarlo a mano, y por eso los nombres no son negociables.**
`cuenta_sitio.py` clasifica `taller-*.html` en su propio cubo, así que `taller-2-cap-4.html` entra
solo. Y `audita_todo.sh` ya tiene **tres bucles propios** que recorren `N in 1 2 3 4` buscando
`salidas/taller${N}_datos.json`, `audita_taller${N}.py`, `prueba_auditor_taller${N}.py` y
`audita_texto_taller${N}.py`: su comentario dice literalmente *«el día que haya un taller 2, lo
hereda sin tocar nada»*. **Consecuencia:** si un archivo se llama de otra forma —`audita_t2.py`,
`taller2_cap4_datos.json`— el taller **nace fuera del arnés en silencio**, sin que ningún paso se
ponga en rojo. La comprobación de C9 no es «añadirlo», es **verificar que el arnés lo encontró**.

---

### 7.1 Los mecanismos del ensamblador, leídos el 2026-09-09

C5 no estrena nada: `ensambla_taller1.py` (1 357 líneas) ya resolvió el molde y **conviene copiarle
la estructura entera antes de escribir prosa**. Lo que hay que saber, y que no se deduce del
plan:

- **Se parte en C5a y C5b, y el Taller 1 lo hizo así por una razón que se declara en su encabezado:**
  *«cada paso deja un HTML que ABRE Y FUNCIONA»*, con la navegación declarando solo los módulos que
  existen. C5a = esqueleto + buscador de variante + T1 y T2; C5b = T3 a T5, las dos rúbricas y el
  banco (que es C6).
- **El ensamblador no escribe HTML: sustituye regiones de la plantilla.** Dos funciones,
  `reemplaza_region(texto, abre, cierra, nuevo, que, max_lineas)` y `sustituye(texto, ancla, nuevo,
  que)`, y las dos **paran** si el ancla no aparece o si la región cambia de tamaño más de lo
  previsto. Las anclas de la plantilla son literales: `const courseData = {`, el comentario
  `MÓDULO 1 · Cajas y tipografía`, `RUBRICAS['demo-rubrica'] = {`, `GEOMAPAS['demo-mapa'] =`,
  `SIMULADORES['demo-deslizadores']` y `AUTOEVALUACIONES['demo'] = [`.
- **La variante vive en `localStorage`**, y no es una comodidad: `loadModule()` vacía `mainContent`
  en cada salto de módulo, así que sin eso el mapa de T2 no sabría qué patrón pintar.
- **El mapa de la variante se registra como FUNCIÓN, no como literal**, y eso tiene un coste que hay
  que declarar igual que lo declara el Taller 1: `audita_texto_base.geomapas()` solo sabe mirar
  dentro de un `.geomapa` cuyo origen sea un literal, así que esa familia del auditor de prosa se
  queda sin nada que comprobar. No es un descuido —el mapa **tiene** que ser dinámico— y no queda
  sin cubrir: `audita_taller2.py` audita los mapas contra el JSON, uno por uno.
- **Y la corrección del §5.2 vive aquí**: el buscador pide el documento COMPLETO y lo imprime tal
  como se tecleó. El JSON ya guarda lo necesario. **Escrito en C5a con un diente más**: por debajo
  de **seis dígitos no resuelve nada** y lo dice en pantalla. Si tecleando tres dígitos saliera un
  resultado, estaríamos reconstruyendo el agujero por el que en el Taller 1 tres de doce
  resolvieron la variante ajena.
- **AÑADIDO EN C5a · los tres mapas del trío van en un orden distinto al de las tres curvas.**
  Medido antes de escribir: en el JSON `trios[i][k]` y `MAPAS_T2.trios[i][k]` son el mismo patrón
  en las tres posiciones de los doce tríos, así que enseñarlos en el mismo orden convertía T2(a) en
  «A con 1, B con 2, C con 3» y acertaba todo el mundo sin mirar. La permutación vive en
  `ORDEN_MAPAS`, una fila por trío, y el ensamblador **para** si alguna es la identidad. Coste
  declarado: quien lea el código fuente puede deshacerla — y no es evitable, porque las
  coordenadas viajan en el CSV y el emparejamiento **siempre** es recalculable. Por eso T2(a) dice
  en el enunciado que un emparejamiento sin argumento no puntúa.
- **AÑADIDO EN C5a · los bloques de código llevan el dato del estudiante VACÍO y dos guardas que
  paran.** `MI_LOCALIDAD <- ""` y `MI_N <- 0`, con `stopifnot(nrow(mia) == 1)` y
  `stopifnot(npoints(p_poly) == MI_N)`. La primera versión traía `"Suba"` de ejemplo, y un
  ejemplo que corre es un ejemplo que alguien entrega: es la familia de fallo del §5.2 otra vez,
  por la puerta del bloque de código.

**Lo que C5 NO puede escribir:** ninguna cifra a mano, y **ninguna respuesta**. El JSON entero viaja
dentro del HTML porque el buscador lo necesita, así que todo lo interpolado es legible con «ver
código fuente». `audita_taller2.py` vuelve a mirarlo ahí, ya incrustado.

---

## 8. Plan de construcción

### Fase 1 · Datos y variantes

**C1 · Las 1000 variantes y sus cifras** — `precalculo/genera_taller2.R`
> **PARTIDA EL 2026-09-09 en C1a y C1b**, usando la salida que este mismo plan dejaba abierta
> («si crece más, se parte»). **C1a — las 16 localidades, el defecto del bounding box, el supuesto
> del χ² y el par de contraste de T4(a) — está HECHA**: secciones A, B y C del guion, 31 anclas en
> verde, y cuatro correcciones al plan (M-2, M-6, M-7, M-8). **C1b — los patrones generados, el σ
> sembrado de T5, las envolventes de T4(b) y el reparto de las 1000 filas — está pendiente.**
- **Descripción:** 16 localidades usables, ~24 patrones generados con familia conocida solo por el
  guion, y 1000 filas que emparejan localidad, patrón, localidad de contraste, recorte de r **y el
  σ sembrado de T5**.
- **Criterios de aceptación:**
  - [ ] 1000 filas, ninguna degenerada (n ≥ 35; λ dentro del rango medido; sin patrones gemelos)
  - [ ] reproducible byte a byte con semilla fija
  - [ ] el JSON **no contiene** la palabra «familia» ni el régimen de ningún patrón
  - [ ] anclas que **paran** el guion: las cifras de M-1 a M-5 de este plan se recalculan y se
        comparan; si alguna se movió, el guion no escribe nada
- **Verificación:** reejecutar produce un JSON idéntico byte a byte · `grep` de las palabras
  prohibidas sobre el JSON · la tabla de M-2 sale igual
- **Dependencias:** ninguna · **Tamaño: L** (es la tarea más grande del plan; si crece más, se
  parte en C1a *localidades* y C1b *patrones generados*)

**C2 · Las salidas sembradas** — mismo guion
- **Descripción:** los cuatro artefactos defectuosos se generan **ejecutando el procedimiento
  equivocado** sobre datos reales, no escribiendo cifras plausibles.
- **Criterios de aceptación:**
  - [ ] T1 · la ventana de caja sale de `owin(range(x), range(y))`, y la buena del polígono; la
        correcta y la defectuosa salen de **la misma función**, que difiere en un argumento
  - [ ] T3 · el informe del modelo se **cita literal** y su afirmación es falsa de forma
        verificable con g
  - [ ] T4(a) · el sesgo de borde se mide, no se afirma, y las dos localidades del par difieren en
        perímetro/área por un factor declarado
  - [ ] T4(b) · el recorte de r se hace **después** de mirar la curva y con las **mismas**
        simulaciones que la envolvente completa
  - [ ] **T5 · el σ sembrado se elige BUSCANDO los N focos**, no al azar: se barre σ sobre la
        localidad y se toma el que produce el número de focos que el informe afirma. Y se
        comprueba que **al menos uno de los cuatro selectores lo desmiente** — si los cuatro dan lo
        mismo, esa variante no sirve y hay que rehacerla
  - [ ] **el taller NO publica ninguna superficie de KDE**: el capítulo 5 midió 39,8 KB por
        superficie, y dieciséis serían 640 KB. Se publica el σ y la afirmación; la superficie la
        calcula el estudiante
  - [ ] cada defecto queda documentado en el comentario con su síntoma
- **Verificación:** cada defecto se reproduce cambiando un argumento y se anota cuál ·
  para cada uno de los 12 estudiantes reales, comprobar que la respuesta correcta **no es la misma
  para todos** (es lo que M-2 y M-3 hacen posible)
- **Dependencias:** C1 · **Tamaño: M**

**C2b · El dato que descarga el estudiante** — `precalculo/datos_taller2.R`
- **Descripción:** GeoPackage con las sedes y los polígonos de las 16 localidades, más los patrones
  generados en un formato que `spatstat` lea.
- **Criterios de aceptación:**
  - [ ] se abre **fuera de este equipo** (es el fallo que el Taller 1 descubrió el 2026-08-18: el
        dato apuntaba a una carpeta que da 404)
  - [ ] no contiene ninguna columna que revele la familia del patrón
  - [ ] queda dentro de `entrega/datos/` y **añadido a la lista blanca del `.gitignore`**
- **Verificación:** abrirlo desde una ruta distinta con `sf::st_read` y con `geopandas` ·
  `git check-ignore` confirma que **sí** viaja
- **Dependencias:** C1 · **Tamaño: S**

### Checkpoint A
- [ ] El JSON reproduce byte a byte
- [ ] Ninguna respuesta dentro del JSON
- [ ] **Revisión de Javier: cinco variantes al azar**, mirando el mapa y las curvas
- [ ] Las cuatro respuestas correctas **difieren** entre al menos dos de los 12 estudiantes

### Fase 2 · Auditoría del precálculo

**C3 · El auditor independiente** — `precalculo/audita_taller2.py`
- **Descripción:** recalcula el precálculo **en Python** (geopandas, pointpats, scipy) para que el
  control no comparta entorno con lo auditado. Es la disciplina de los siete capítulos.
- **Criterios de aceptación:**
  - [ ] recalcula λ, χ², G, F, K, L, g y el sesgo de borde de una muestra de variantes
  - [ ] guarda explícita: el JSON no lleva respuestas (también contra el JSON incrustado en el HTML)
  - [ ] guarda de la §5.4: ni «familia» ni régimen ni cuál ventana es la correcta
  - [ ] declara sus saltadas, si las hay, con el motivo
- **Verificación:** ejecuta en verde sobre el JSON real; sembrar a mano un error en el JSON lo pone
  en rojo
- **Dependencias:** C1, C2 · **Tamaño: L**

**C4 · El arnés de inyección** — `precalculo/prueba_auditor_taller2.py`
- **Descripción:** inyecta defectos en el JSON y comprueba que C3 los caza. Sin esto, el auditor
  es una opinión.
- **Criterios de aceptación:**
  - [ ] ≥ 40 inyecciones, **todas cazadas**, y todas contadas como **tipos** vistos fallar (no
        instancias: es el hueco del núcleo que encontró el capítulo 5)
  - [ ] cero reventones contados como capturas (el otro hueco del capítulo 5)
  - [ ] al menos una inyección por cada guarda de la §5.4 (lo que el JSON no puede contener)
- **Verificación:** el informe imprime tipos vistos fallar / tipos totales
- **Dependencias:** C3 · **Tamaño: M**

### Fase 3 · El HTML

**C5 · El enunciado** — `precalculo/ensambla_taller2.py`
> **PARTIDA EN C5a Y C5b, como el Taller 1 y por la razón de su encabezado: cada paso deja un HTML
> que ABRE Y FUNCIONA. C5a — esqueleto, cabecera y pie, CSS propio, buscador del §5.2, T1 y T2 —
> está HECHA (2026-09-09)**; ver el §0, que trae también los dos defectos que la construcción
> encontró (**M-13**, la caja de T1, y **M-14**, `Fest()`) y la fuga de `datos_taller2.R`.
> **C5b — T3, T4, T5 y las dos rúbricas — está pendiente.**
- **Descripción:** el HTML autocontenido con la librería del material: enunciado de las cuatro
  tareas, buscador de variante **con el documento reflejado (§5.2)**, mapas, curvas, rúbrica del
  escrito y rúbrica de la defensa.
- **Criterios de aceptación:**
  - [ ] ninguna cifra escrita a mano: todas vienen del JSON
  - [ ] el buscador imprime el documento tal como se tecleó
  - [ ] la retroalimentación por opción usa la clave `retro`, **no** `respuesta` (el defecto que
        dejó 68 explicaciones invisibles en los capítulos 3 y 4)
  - [ ] sin desbordamiento a 1 280, 375 **y 318 px**
- **Verificación:** `sin_aritmetica.py` sin cifras en la prosa · `campos_vivos.py` en verde ·
  `verifica_bloques.py` sobre los bloques R/Python
- **Dependencias:** C1, C2, C2b · **Tamaño: L**

**C6 · El banco de la defensa y el catálogo de refutaciones** — dentro de C5
- **Descripción:** **36** preguntas con el reparto del §4.2 (6 del módulo 4, 3 de cada uno de los
  otros diez), **12 afirmaciones falsas** para el bloque de refutación en vivo —una por
  estudiante—, y la rúbrica de la defensa.
- **Criterios de aceptación:**
  - [ ] **36 exactas**, porque 36 = 12 × 3 y el sorteo del §4.5 es sin reemplazo
  - [ ] las 36 cotejadas una a una contra **las 12 preguntas de autoevaluación** del capítulo 4:
        ninguna repetida
  - [ ] las 36 cotejadas contra los **5 ejercicios guiados**: ninguna repite un ejercicio
        *(las dos superficies del §3.7 — cotejar solo contra una es el error que este plan ya
        cometió)*
  - [ ] los 11 módulos representados, con **6** preguntas del módulo 4
  - [ ] **12 afirmaciones falsas, no una**: con sesión única, repetir la refutación se la regala al
        que defiende al final
  - [ ] cada afirmación falsa es **falsa de forma verificable** con el material, no discutible
  - [ ] ninguna pregunta nombra una posición de opción («las dos primeras»): las opciones se barajan
  - [ ] **las 36 quedan en una lista legible desde fuera de este taller**, para que el *blueprint*
        del parcial 2 (`PLAN_Parcial_Corte_2.md`, T1.1) pueda evitarlas o reutilizarlas **a
        propósito**. Publicadas, cualquier coincidencia no declarada es una respuesta regalada
- **Verificación:** el ensamblador imprime la tabla de cobertura módulo × pregunta y **falla** si
  el total no es 36 o si algún módulo queda a cero · un reparto de prueba sobre 12 documentos
  ficticios agota el banco exactamente y no repite ninguna
- **Dependencias:** C5 · **Tamaño: M**

**C7 · Las cifras de la prosa** — `precalculo/audita_texto_taller2.py`
- **Criterios de aceptación:** toda cifra del texto tiene respaldo en el JSON · `TOPE_KB` propio
  con su aritmética escrita en el encabezado · inyecciones añadidas a `prueba_texto.py`
- **Verificación:** verde, y el arnés de prosa entero sin regresión sobre los demás sujetos
- **Dependencias:** C5 · **Tamaño: S**

### Checkpoint B
- [ ] **Javier lee el enunciado completo**, de principio a fin, como lo leería un estudiante
- [ ] Consola limpia, 0 gráficos huérfanos tras 6 ciclos, `aria-label` en todos los lienzos
- [ ] Las cuatro tareas se pueden responder **solo** con lo que el capítulo publica

### Fase 4 · Cierre

**C8 · Verificación en el navegador** — **Tamaño: S**
- [ ] los tres anchos · el buscador con cinco documentos distintos · las curvas con tinta ·
      el dato descargable se abre

**C9 · Integración en el repositorio** — **Tamaño: S**
- [ ] `audita_todo.sh --rapido` **nombra el taller 2 en su salida** (no se edita: lo descubre por
      los nombres del §7; si no aparece, el nombre está mal) · `cuenta_sitio.py` en verde ·
      `index.html` con la tarjeta nueva, junto a la del Taller 1 · `README.md` actualizado ·
      `.gitignore`: `!/PLAN_Taller_2_Cap_4.md`, `!/entrega/datos/taller2_*.gpkg`, y
      **`genera_taller2.R` y `verifica_taller2.R` ignorados**
- [ ] `git check-ignore` confirma los dos que NO deben viajar

**C10 · El calificador** — `precalculo/verifica_taller2.R` — **Tamaño: M**
- [ ] recalcula las cifras esperadas de **un** documento · `--lista curso.txt` para los 12 ·
      **para** si la portada no cuadra con la lista (§5.2) · **no entra en el arnés**, porque
      imprime las respuestas y el arnés deja registro

**C10b · El control de la semana 9** — en clase, entre el 28 de septiembre y el 2 de octubre — **Tamaño: S**
- **Descripción:** los doce leen en voz alta su localidad, su n y su λ (§5.3). No se califica.
- **Criterios de aceptación:**
  - [ ] los doce pares (documento, localidad) cotejados contra la lista del curso **en el aula**
  - [ ] quien tenga una discrepancia se corrige **ahí**, con 4 días aún por delante
- **Dependencias:** el taller repartido · **Tamaño: S**

**C11 · La lectura de los doce escritos** — entre el 6 y el 8 de octubre — **Tamaño: M**
- **Descripción:** leer las doce entregas y elegir, para cada estudiante, **la decisión que va a
  defender** en el bloque de 2 min. Es lo que los dos días de margen compran.
- **Criterios de aceptación:**
  - [ ] una decisión elegida y anotada por estudiante, con la razón
  - [ ] **la bitácora de cada uno leída** (§6): es lo que se contrasta en la sustentación
  - [ ] comprobado que la portada de cada uno cuadra con su documento (§5.2): quien resolvió una
        variante ajena se detecta **aquí**, antes de la sustentación, no al calificar
  - [ ] el sorteo sin reemplazo del banco (§4.5) hecho y registrado **antes** del jueves
- **Dependencias:** el taller entregado · **Tamaño: M**

### Checkpoint C
- [ ] Javier lee la rúbrica y el banco
- [ ] Las cinco preguntas abiertas del §11 cerradas
- [ ] Commit y publicación

---

## 9. Orden y paralelismo

```
C1 ──┬── C2 ──┬── C3 ── C4
     │        │
     └── C2b ─┴── C5 ──┬── C6
                       └── C7
```

**Secuencial de verdad:** C1 → todo. Nada se puede escribir antes de que existan las variantes.
**Se pueden solapar:** C3+C4 (auditoría) con C5+C6 (HTML), en cuanto C2 esté cerrada.
**C10 es independiente** de la fase 3 y se puede escribir mientras se audita.

El camino crítico es **C1 → C2 → C5 → C8 → C9**. Con el calendario revisado hay **27 días** hasta
la entrega y el reparto propuesto para el lunes 21 deja **once días de construcción** (10 a 20 de
septiembre), no dos:

| Fechas | Qué | Por qué ahí |
|---|---|---|
| 10 – 13 sep | **C1**, **C2**, **C2b** | El precálculo primero: nada se escribe antes de que existan las variantes |
| 14 – 17 sep | **C3** y **C4** ‖ **C5** y **C6** | La auditoría **en paralelo** con el HTML, no después |
| 18 – 20 sep | **C7**, **C8**, Checkpoint B | Queda el fin de semana para la lectura completa del enunciado |
| **lun 21 sep** | **C9 · reparto** | El capítulo 4 cerró el viernes 18: el taller sale con el capítulo recién terminado |
| 21 sep – 6 oct | *(el estudiante trabaja)* · **C10** | El calificador se escribe mientras, sin prisa |
| **28 sep – 2 oct** | **C10b · control de la semana 9** | Tres cifras por estudiante en clase (§5.3). Atrapa la variante ajena con cuatro días de margen |
| **mar 6 oct** | **Entrega** | |
| 6 – 8 oct | **C11** · lectura de los doce escritos | Lo que compra la separación entrega/sustentación |
| **jue 8 oct** | **Sustentación** | Una sesión, 7 min por estudiante (§4.1) |

**Lo que el calendario nuevo NO cambia:** C3 y C4 siguen teniendo que ir en paralelo con C5. Tener
doce días en vez de dos hace que quepan cómodamente; no hace que puedan ir después.

---

## 10. Riesgos

| Riesgo | Impacto | Mitigación |
|---|---|---|
| **Regenerar el precálculo después de repartir** | **Alto** | Reasigna las 1000 variantes. Una vez publicado, `genera_taller2.R` no se vuelve a ejecutar; el enunciado se corrige por el ensamblador. Es la lección del Taller 1 |
| **El JSON publicado filtra la familia del patrón** | **Alto** | Guarda explícita en C1 y comprobación doble en C3, también contra el JSON ya incrustado en el HTML |
| ~~La defensa al 60 % no cabe en una sesión~~ **RESUELTO (2026-09-09)** | — | **Una sesión, 7 min por estudiante**: 12 × 8 = 96 min sobre los 120 de la sesión (§4.1). Lo que queda vivo es la comprobación de que la sesión es de 2 h y no de 1,5 — si es de 1,5, la refutación pasa al escrito |
| **La sesión única regala ventaja al que defiende al final** | **Medio** | Nace de la decisión de hoy: nadie sale del aula. Sorteo **sin reemplazo** sobre un banco de **36 = 12 × 3**, más **12** afirmaciones falsas distintas para la refutación (§4.5, C6). El sorteo se hace **antes** de la sesión y queda registrado |
| **T1 se solapa con el ejercicio e3 del capítulo** | **Medio** | §3.5, y la reserva medida de M-5 (duplicados exactos, de 0 a 22 según la localidad) |
| **T4(b) se solapa con el ejercicio e4** | **Medio** | La diferencia —recorte declarado vs. post hoc— es real pero fina. Si no se sostiene al redactar, T4(b) se sustituye por el `nsim` y la banda por defecto |
| ~~Tres o cuatro días de construcción~~ **CAÍDO (2026-09-09)** | — | El calendario nuevo da **12 días de construcción** en vez de 2 (§9). Lo único que sobrevive de este riesgo es que **C3 y C4 sigan yendo en paralelo con C5**, no después |
| **El taller cubre solo el capítulo 4 y se entrega con el 5 ya visto** | **Medio** | Lo trae el calendario nuevo (§2.2, punto 3). Deja el capítulo 5 íntegro al parcial 2. Es una decisión, no un defecto — pero hay que tomarla **antes de C1**, porque incluir el capítulo 5 cambiaría el catálogo de variantes y el reparto del banco. Pregunta 6 del §11 |
| **El banco publicado del taller choca con el del parcial 2** | **Alto** | Los dos cubren el capítulo 4 y se construyen con un mes de diferencia. Una pregunta repetida es una respuesta publicada. Guarda en C6 (lista legible desde fuera) y nota cruzada en `PLAN_Parcial_Corte_2.md`. **Ninguno de los dos planes veía al otro** hasta hoy |
| **T5 pide capítulo 5 y la entrega cae el segundo día de la semana 10** | **Medio** | El capítulo 5 va por las semanas 8–10 y su K inhomogénea vive en el **módulo 10**. T5 se restringe a los **módulos 1–3**, cerrados con seguridad al acabar la semana 9. Si el capítulo 5 se retrasa una semana, **T5 es la primera que se cae** — y el escrito vuelve a cuatro tareas del 10 % sin tocar nada más |
| **Los doce escritos no se leen a tiempo entre el martes y el jueves** | Bajo | C11 lo cuenta como tarea con tamaño M en vez de suponer que es gratis. Si no cabe, el bloque «su variante» vuelve a elegirse al azar y pierde poco |
| El taller nace fuera del arnés | Medio | C4 va **antes** del cierre, no después |
| **El taller cubre los módulos 10 y 11 antes de verlos en clase** | Medio | Deliberado (§2.1) y **dicho en el enunciado**. Si no gusta, T4 se mueve a la defensa |
| El estudiante resuelve la variante ajena | Medio | El anclaje del §5.2, que mueve la detección a antes de entregar. Y el precedente de calificación del 2026-09-03 sigue vigente |
| Los estudiantes entregan texto de IA sin entenderlo | Bajo aquí | Con la defensa al 60 % esta es la palanca dominante, no un parche |

---

## 11. Preguntas abiertas

1. ~~**¿Una sesión de defensa o dos?**~~ ✅ **CERRADA (2026-09-09): una sesión.** De ahí salen los
   7 min por estudiante del §4.1, el banco de 36 y el sorteo sin reemplazo del §4.5.
   **Queda una comprobación, no una decisión:** confirmar que la sesión es de **2 h**. Con 4 h
   semanales repartidas en dos bloques lo es, pero si fueran bloques de 1,5 h la aritmética no da
   (12 × 8 = 96 > 90) y la refutación en vivo pasa al escrito. Es lo único del §4.1 que puede
   cambiar, y tiene que cambiar **antes** de publicar.
2. **Peso del Taller 2 dentro del Corte II**, y su relación con el parcial de la semana 11.
3. **¿Es el único taller del Corte II** o el primero de dos? Si hay un segundo sobre el capítulo 5,
   este puede soltar el módulo 11 y ganar aire.
4. **¿`verifica_taller2.R` se versiona después de calificar?** En el Taller 1 la respuesta fue que
   no —resuelve el taller—, y `califica_taller1.py` sí se versionó el 2026-08-26.
5. **¿Hace falta un `califica_taller2.py`** como el del Taller 1, o se califica a mano siendo doce?
   Con la defensa al 60 % la hoja de cálculo tiene que llevar los dos instrumentos, no solo el
   escrito.

6. **¿Entra el capítulo 5?** — **la trae el calendario nuevo, y bloquea C1.** El taller se entrega
   el 6 de octubre, cuando el capítulo 5 (semanas 8–10) ya se ha visto entero, y cubre solo el 4.
   Tres salidas:
   - **dejarlo como está** — el taller es del capítulo 4 y el capítulo 5 va entero al parcial 2;
   - **añadir una quinta tarea del capítulo 5** —intensidad por núcleos, que es la continuación
     natural de T3(c): «λ no es constante en tu localidad» es literalmente la pregunta que abre el
     capítulo 5— y subir el escrito de 4 tareas a 5;
   - **ampliar solo el banco** de la defensa con los módulos del capítulo 5, dejando el escrito
     intacto. Es la salida barata y aprovecha que la defensa pesa el 60 %.

   ✅ **CERRADA (2026-09-09): la segunda.** Entra **T5** sobre los módulos 1–3 del capítulo 5 y el
   escrito pasa a **cinco tareas del 8 %**; **el banco se queda íntegro en el capítulo 4**. Razón:
   el parcial 2 cubre los capítulos 4 y 5, así que sin T5 la mitad del parcial llegaba sin ensayo
   formativo; y diluir el banco habría debilitado la profundidad sobre el capítulo del que va el
   taller. T5 queda defendible por el bloque «su variante».

7. **Confirmar el reparto del lunes 21 de septiembre** (§2.2). Es la fecha que deja el taller salir
   con el capítulo 4 recién cerrado y da 15 días al estudiante. Adelantarlo al viernes 18 es
   posible pero obliga a terminar C8 ese mismo día.

8. **¿En qué clase de la semana 9 cabe el control de C10b?** Son quince minutos y no se califica,
   pero hay que reservarlos: la semana 9 es capítulo 5 a plena carga.

9. **La coordinación con el parcial 2 hay que hacerla, no solo declararla.** El §10 la marca como
   riesgo alto y C6 deja la lista legible, pero alguien tiene que **leerla desde el otro plan**
   cuando se escriba su *blueprint* (T1.1). Queda una nota en `PLAN_Parcial_Corte_2.md`.
