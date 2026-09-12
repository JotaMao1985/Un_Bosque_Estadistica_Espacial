# Plan · Taller 2 — Capítulo 4 (patrones puntuales)

Estadística Espacial 2026-II (20929) · **Corte II** · Universidad El Bosque

Taller teórico-práctico sobre *Patrones puntuales: descripción, CSR y funciones de resumen*
(cap. 4, **los once módulos de contenido**), aplicado en la **semana 10** como cierre del Corte II
y preparación del parcial 2. Evalúa **apropiación de conceptos, interpretación
de resultados y comprensión de procedimientos**, no ejecución de código.

**Fecha del plan:** 2026-09-09 (miércoles, semana 6) · **Calendario revisado el 2026-09-09 y otra vez el 2026-09-11**
**Entrega:** domingo **11 de octubre de 2026, a más tardar a las 13:00** · **Sustentación:** martes **13 de octubre**, presencial, en el espacio de la clase
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
FUNCIÓN DE ESPACIO VACÍO. BLOQUEA T2.** ✅ **CERRADA EL 2026-09-10 — ver el final del §0.**
Lo que sigue es el diagnóstico tal como se escribió; el arreglo y la medición de lo que
costaba están abajo. Con `spatstat.geom` 3.7.2 y `spatstat.explore` 3.8.0,
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
FAMILIAS.** ✅ **CERRADA EL 2026-09-10 — ver el final del §0.** El `.gitignore` ignora `genera_taller2.R` precisamente porque «construye los patrones
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
se publica límite de páginas**, que preferí omitir antes que inventarlo. La hora límite quedó fijada el
2026-09-11: **13:00 del domingo 11 de octubre**, y ya está publicada.

**C5b HECHA (2026-09-10)**: el mismo `ensambla_taller2.py` añade **T3, T4, T5 y las dos
rúbricas**. El HTML pasa a **1 124 KB** y a **siete módulos**, con **5 tareas al 8 %** —los pesos
suman el 40 % del escrito y el ensamblador lo comprueba—, **6 tiras de variante** (todas menos la
de rúbricas), **8 lienzos con `aria-label`** y **2 rúbricas de 100 puntos**. Verde otra vez:
auditor **180 · 0 · 0**, `sin_aritmetica.py` y `campos_vivos.py` limpios, **0 desbordamientos a
1 280, 375 y 318 px en los siete módulos**, **24 fórmulas KaTeX** y **0 gráficos huérfanos tras
seis ciclos** (42 cargas de módulo). Consola sin errores.
**Los tres informes que las tareas ponen a auditar se RENDERIZAN, no se escriben**: cada uno cita
cifras de la variante de quien lee. Nace de una comprobación: la primera versión del informe de
T4 decía «se sale en prácticamente todos los nodos» y **era falsa en media docena de las doce**
—en la primera envolvente son 16 de 159—. Un informe con la premisa falsa hunde la tarea, porque
el estudiante refuta la aritmética y no llega nunca al error, que es de razonamiento. Ahora los
tres dicen cifras ciertas y sacan de ellas conclusiones que no se siguen.
**Falta C6**: el banco de 36 y las 12 afirmaciones falsas, que van en el módulo 7.

**M-15 · T4(a) NO PUEDE «ENTREGAR EL SESGO YA MEDIDO»: no está publicado.** El JSON publica de
cada localidad **solo** identidad, n, área y λ —el auditor lo exige así—, de modo que ni el sesgo
de borde ni el cociente perímetro/área viajan. T4(a) reescrita: el estudiante los **calcula**, con
el bloque que se le da, y eso sigue sin repetir el ejercicio `e5` porque no pide las tres
correcciones sino dos, sobre **dos** ventanas de forma opuesta. Medido el 2026-09-10 a **r = 1 km**:
el déficit de la K sin corregir va del **8,8 % en Usme** (perímetro/área 0,507) al **45,5 % en
Antonio Nariño** (2,479), y **ordena monótonamente por perímetro/área** en la muestra medida — es
decir, T4(b) tiene respuesta y con holgura. *(M-12 daba 20,3 %–33,9 %: es la misma cosa medida a
otra escala de r, no una contradicción.)* **Matiz de M-20 (2026-09-10):** «monótonamente» vale
para la muestra, no para las dieciséis — sobre las 120 parejas hay **9 invertidas** a r = 1 km,
todas entre formas con razón de perímetro/área menor que 1,4. Por eso el contraste exige razón ≥ 2.

**M-16 · T4(b) NO PUEDE PEDIR EL TEST GLOBAL: el patrón de la envolvente no se publica.** La
envolvente viaja como curvas —`r`, `obs`, `lo`, `hi`, `teo`— y las coordenadas que la produjeron no
están ni en el JSON ni en el CSV, así que el estudiante no puede correr `dclf.test` como el plan
preveía. Lo que **sí** puede es contar los nodos fuera de banda, comparar el recuento con lo que
esperaría de una banda puntual al 5 % y decir **por qué el recuento tampoco decide** —que los 513
nodos de una K acumulada no son independientes—. Eso es el módulo 11 y no lo cubre ninguna
superficie publicada. Medido: los recuentos van de **3 de 513 (0,6 %)** a **219 de 513 (42,7 %)**,
así que la comparación con el 5 % esperado da conversación en las dos direcciones.

**M-17 · EL RECUENTO DE FOCOS DE T5 NO ES REPRODUCIBLE SIN LA REJILLA, y el JSON no la publica.**
Contar componentes conexas por encima de un umbral depende del ráster sobre el que se dibuje la
superficie. Barrido el 2026-09-10 sobre las dieciséis: con `dimyx = 64/128/256/512` cuadran
15/12/14/13 recuentos, y probando además `diggle = TRUE`, `edge = FALSE` y la media como `n/área`,
**ninguna combinación reproduce las dieciséis**; el error del `pico_informe` no baja del **3,7 %**
en el mejor caso. Con la mejor —`dimyx = 256`, media de la superficie— **catorce de dieciséis
recuentos coinciden exactamente y dos se van por uno** (Usme 2→3, Barrios Unidos 3→4), y el pico se
reproduce con un error de hasta 3,6 % (Teusaquillo).
**No bloquea T5**, y la razón está en el propio plan: M-9 ya cambió el estadístico de «contar
componentes» a **pico / intensidad media** justamente porque el entero es grosero. Así que el
enunciado **fija la rejilla en el bloque de código** (`dimyx = 256`), el instrumento de la tarea es
el cociente pico/media, y el recuento se pide como observación —«si no te coincide, dilo y explica
de qué depende ese entero»—, que además es el tercer mando de la misma familia que T1 y T5(c).
Comprobado de punta a punta sobre San Cristóbal: pico 4,8213 contra 4,8137 publicado, 1 foco contra
1, y los cuatro selectores dan σ de **296 a 1 696** —un factor 5,7— con pico/media de **3,34 a
8,03**. La refutación de M-9 —«entre anchos igualmente defendibles la cifra se mueve por un factor
de X»— está viva.

**UN DUPLICADO MÁS, y este contra los EJERCICIOS.** Cotejando T3, T4 y T5 antes de cerrar apareció
que **T4(a) preguntaba «¿en qué dirección empuja el sesgo, y por qué siempre en la misma?»**, que es
**literalmente lo que pide el ejercicio guiado 5** del capítulo —y que además roza la pregunta 10—.
El §3.5 había mirado ese ejercicio y había concluido que la diferencia estaba en «no pedir las tres
correcciones»: miró el *procedimiento* y no la *pregunta*. Corregido: T4(a) pregunta ahora **cuál de
las dos ventanas sufre más y por cuánto**, T4(b) por qué lo predice perímetro/área, y el enunciado
**dice en voz alta** que la dirección del sesgo ya se trabajó en `e5` y aquí no se vuelve a
preguntar. Es el tercer duplicado que este taller encuentra cotejando, y el primero contra los
ejercicios: los dos anteriores fueron contra las preguntas. **La regla del §3.7 se amplía**: no
basta con cotejar contra las dos superficies, hay que cotejar **la pregunta**, no el procedimiento.

**T3(b) · «el r donde g alcanza su máximo» es una cifra degenerada.** Medido sobre los 24: vale
**r = 0,005 en 23 de ellos** —el primer nodo de la rejilla— porque en un proceso agregado g decrece
desde el origen, así que ese literal pedía a los doce la misma respuesta y encima un artefacto de
resolución. Sustituido por **cuánto vale g en su máximo**, que va de **2,01 a 11,41** y sí es suya.
Las otras dos cifras del literal se conservan y también separan: g vuelve a 1 entre **r = 0,070 y
r = 0,170**, y K allí vale entre **1,46 y 3,41 veces** πr².
**Y la premisa del informe de T3 se comprobó antes de escribirla**: L − r es positiva en r = 0,20
en **los 24**, así que el informe dice una verdad sobre el patrón de cada quien y de ella saca una
conclusión falsa para todos. Eso es lo que la tarea necesita.

**Los cuatro bloques nuevos se ejecutaron.** El de T3 reproduce K, L y g del enunciado con error
**5·10⁻⁹**; el de T4(a) da los déficits de arriba; el de T5 reproduce pico y focos. Y el de T1 y
el de T2 siguen corriendo. **Ocho de los ocho bloques del taller se han ejecutado de verdad**, que
es lo que `verifica_bloques.py` no puede hacer aquí: sin línea `#>` no hay cifra anunciada que
contrastar, y en un taller no puede haberla.

**C6 HECHA (2026-09-10)**: el módulo 7 publica las **36 preguntas** del banco y las **12
afirmaciones falsas**. El HTML queda en **1 138 KB**. El ensamblador **imprime la tabla de
cobertura y para** si el reparto no cuadra: `1:3 2:3 3:3 4:6 5:3 6:3 7:3 8:3 9:3 10:3 11:3`, con
el módulo 4 al doble por el §3.6. Comprueba además que **12 × 3 agotan el banco sin repetir
ninguna** —sobre doce documentos ficticios, no razonado sobre el papel—, que las doce afirmaciones
son distintas, que **ningún módulo se queda sin afirmación falsa** y que ninguna pregunta está
redactada como si tuviera opciones. La **lista legible desde fuera** se escribe en cada
construcción: `precalculo/salidas/taller2_banco.md`, con el aviso de para qué existe.

**EL COTEJO SE HIZO ANTES DE ESCRIBIR, y descartó seis candidatas del banco** — entre ellas «¿qué
distingue G de F?» (es la pregunta 7), «¿cuáles son las dos propiedades de CSR?» (la 5), «¿por qué
K sigue por encima si la agregación es a 20 m?» (la 9) y «¿en qué dirección empuja el sesgo de
borde?» (el ejercicio 5). Quedan escritas en el encabezado del banco para que no vuelvan a entrar.

**Y RELEER LAS DOCE AFIRMACIONES FALSAS TUMBÓ SEIS**, que es el hallazgo de C6 y merece quedar
escrito porque las razones son de cuatro tipos distintos:
1. **Dos eran preguntas de este mismo banco**, palabra por palabra —«dos realizaciones de CSR
   tienen el mismo n» y «el índice de dispersión vale 1 siempre»—. Al mismo estudiante le podían
   tocar la pregunta y su afirmación.
2. **Una publicaba la respuesta de T3**: «L − r por encima de cero significa agregación a esa
   distancia» es, literalmente, lo que afirma el informe que T3 manda refutar.
3. **Otra publicaba la de T4** y además era la pregunta 11 del capítulo: «se sale de la banda en
   algún r, luego p < 0,05».
4. **Y una no era falsa.** «Cambiar la ventana cambia λ pero no cambia el veredicto del test» se
   escribió pensando en T1 — y M-2 dice que **el veredicto vuelca en 3 de las 16 localidades**, de
   modo que para las otras trece la afirmación *se cumple*. Una afirmación «falsa» que resulta
   cierta para tres cuartas partes del curso no es una refutación: es una trampa, y habría estallado
   en voz alta delante de doce personas. **El criterio «falsa de forma verificable, no discutible»
   hay que aplicarlo con la medición en la mano, no con la intuición.**

**UNA DECISIÓN QUE EL PLAN NO TOMABA: las doce afirmaciones falsas SE PUBLICAN**, igual que el
banco. Razón: lo que el §4.5 quiere evitar es que el duodécimo tenga ventaja sobre el primero, y
eso lo resuelven las **doce distintas**, no el secreto; y publicarlas es coherente con el banco,
que se publica «a propósito: no se trata de sorprenderte, se trata de que llegues sabiendo».
Reversible en un minuto: se retira el bloque del módulo 7 y el catálogo se queda solo en
`salidas/taller2_banco.md`. **Si Javier prefiere lo contrario, es un cambio de tres líneas.**

**Falta C7** (las cifras de la prosa), **C8** (navegador), **C9** (integración) y **C10** (el
calificador). Y siguen vivos **M-14** —que bloquea la publicación de T2 hasta regenerar las curvas
F— y la fuga de `datos_taller2.R`.

**C7 HECHA (2026-09-10)**: `precalculo/audita_texto_taller2.py`, **84 comprobaciones, 0 fallos**,
y `prueba_texto.py` lo adopta como **sujeto nuevo con 20 inyecciones, 20 cazadas**.
`audita_todo.sh` lo descubre solo por el nombre: su bucle `for N in 1 2 3 4` ya buscaba
`audita_texto_taller${N}.py`, que es exactamente para lo que el §7 dice que los nombres no son
negociables.

**El `TOPE_KB` propio, con su aritmética escrita en la cabecera.** El de la casa vale 700 y este
documento pesa **1 141 KB**, así que necesita el suyo — y no como marca de agua sino como cota con
dos extremos: por abajo el tamaño de hoy, y **por arriba la ceguera del arnés**, que tumba esa
comprobación inyectando **+312 KB**. Si el tope pasara de 1 141 + 312 = **1 453**, la inyección ya
no lo rebasaría y la comprobación quedaría verde para siempre. **1 250** deja 109 KB de
crecimiento y 203 de margen contra el punto ciego. Está escrito ahí para que quien lo suba sepa
que hay que mirar las dos cosas.

**HALLAZGO · `formulas_escapadas()` llevaba pasando POR VACUIDAD en tres documentos publicados.**
Miraba **solo** `$$…$$`, y el Taller 2 no tiene ninguna: sus **48** fórmulas son todas `\(…\)`.
Igual el **Taller 1 (18 en línea, 0 de bloque)** y el **capítulo 2 (22 y 0)**. La comprobación
existe por un defecto que el capítulo 5 destapó en T3.6 —un `<` crudo dentro de una fórmula se come
el HTML hasta el siguiente `>`, y con él **cualquier cifra inventada que venga detrás**, que es el
punto ciego de la familia 1 reapareciendo por otra puerta— y para tres documentos salía verde sin
haber mirado una sola fórmula suya. **Ampliada a las dos formas** en `audita_texto_base.py`, con la
medición que la hace segura: **ninguno de los doce documentos del sitio tiene un `<` crudo en una
fórmula en línea**, así que no rompe a nadie. Y ahora imprime cuántas mira de cada clase —«0 de
bloque, 48 en línea»—, para que la vacuidad se vea en vez de esconderse detrás de un OK.

**DOS INYECCIONES MAL ESCRITAS, y el arnés me las cazó a mí en vez de al auditor**, que es para lo
que está: «chi2» como sustituto de χ² **ya existía** en el bloque de Python de T1
(`from scipy.stats import chi2`) y el arnés lo rechaza —un valor inyectado que ya está no prueba
nada—; y sustituir χ² **solo en su primera aparición** dejaba las otras dos, con el defecto
inyectado y el documento todavía correcto. La segunda es la que enseña: **el cuarto campo
`en_todas` no es opcional cuando la cadena aparece más de una vez.** Lo mismo con la fila del
catálogo de refutaciones: reescribir su contenido dejaba la fila en pie y el recuento seguía dando
12; hay que **retirarla**.

**LO QUE LA VERIFICACIÓN DE C7 ENCONTRÓ FUERA DEL TALLER.** El arnés de prosa completo da **236 de
238**, y los dos que faltan **no son míos ni del Taller 2**: son del **capítulo 4**, y fallan con
«el texto a sustituir no aparece». Es imposible que los cause el cambio de arriba —ese fallo ocurre
**antes** de correr el auditor—. Causa: el commit `449792b` reescribió los ejercicios guiados del
capítulo 4 y sus soluciones dejaron de viajar en un `<td>`; ahora las pinta el JavaScript desde el
JSON incrustado. `prueba_texto.py` **no se ha tocado desde entonces**, así que dos de sus treinta
inyecciones llevan **inertes** desde aquel commit: el arnés informa «no detectado» cuando en
realidad nunca llegó a inyectar nada. Queda como tarea aparte; no es de este taller y el capítulo 4
está publicado.

**El Taller 1 sigue fuera del arnés de prosa.** `audita_texto_taller1.py` existe y
`audita_todo.sh` lo corre, pero `prueba_texto.py` no lo tiene como sujeto: **ninguna de sus
comprobaciones se ha visto fallar nunca**. El Taller 2 es el primer taller que entra. Anotado aquí
porque es justo la duda que el propio arnés imprime al final de cada corrida.

**Coste declarado:** el sujeto nuevo añade unos **2 minutos** a `prueba_texto.py` completo. Cada
pasada del auditor indexa el JSON de 530 KB y tarda **6 s**; los capítulos, con JSON de ~100 KB,
tardan menos de uno.

**C8 y C9 HECHAS (2026-09-10).**

**C8 · el navegador**, con sus cuatro puntos cerrados: **0 desbordamientos a 1 280, 375 y 318 px**
en los siete módulos; el **buscador con cinco documentos distintos** —1012345678, 52987341,
1030512004, 80123456 y 1098765432— resuelve cinco variantes distintas, con cinco localidades,
cinco patrones y cinco tríos; **las curvas pintan tinta de verdad**, medida contando píxeles no
blancos del lienzo —unos 14 000 de 171 396 en cada uno de los tres de T3, que es lo que distingue
un gráfico dibujado de un gráfico vacío que se ve igual de bien en una captura—; y **los tres
archivos descargables responden 200** servidos desde el sitio. Más lo que ya se venía comprobando
en cada paso: consola sin errores, 0 gráficos huérfanos tras seis ciclos y `aria-label` en los
ocho lienzos del marcado.

**Y una medición de regalo, sobre el reparto:** las 1000 variantes usan **los 24 patrones propios y
los 12 tríos**, con un mínimo de 32 y 48 filas respectivamente, y las **12 envolventes se reparten
entre 77 y 84 filas cada una**. Ninguna se queda sin salir, que es lo que haría que una envolvente
publicada no la viera nadie.

**C9 · la integración, y el arnés lo descubrió todo solo.** `audita_todo.sh --rapido` termina en
**ARNÉS COMPLETO EN VERDE** y nombra el taller 2 en **cinco** sitios distintos sin que se haya
tocado una línea de ese guion: `audita_taller2.py` por el bucle del §7, `ensambla_taller2.py` en
`sin_aritmetica.py`, `taller-2-cap-4.html` en `campos_vivos.py` y en `comentarios_cerrados.py`, y
`audita_texto_taller2.py` por su propio bucle. Eso es exactamente lo que el §7 pedía comprobar —«la
comprobación de C9 no es añadirlo, es verificar que el arnés lo encontró»—.
`cuenta_sitio.py` lo clasifica en el cubo de talleres (7 módulos, 5 ejercicios, 2 rúbricas, 7
geomapas, 4 simuladores) y ahora dice **«los 9 archivos del curso están enlazados»**, porque
`index.html` lleva su tarjeta junto a la del Taller 1. `README.md` actualizado. Y el `.gitignore`
ya estaba: se escribió **antes** de que los archivos existieran, a propósito, y
`git check-ignore` confirma las dos caras — `genera_taller2.R` y `verifica_taller2.R` **no viajan**,
y los tres `entrega/datos/taller2_*`, el plan y `salidas/taller2_banco.md` **sí**.

**LO QUE C9 SIGNIFICA, Y HAY QUE DECIRLO ANTES DE FUSIONAR:** la tarjeta de `index.html` hace el
taller **alcanzable desde la portada**, y la portada es lo que despliega en Pages. Mientras esto
viva en la rama no publica nada; **el día que se fusione, se publica un taller cuya T2 descansa
sobre curvas F que no son la función de espacio vacío (M-14)**. La rama está lista; la decisión de
fusionarla no lo está.
> **Actualización del 2026-09-10:** M-14 está cerrada y las F son las buenas, así que este párrafo
> ya no bloquea la fusión. Lo que queda antes de publicar es **M-18** —el estudiante no puede
> reproducir el pico/media del informe de T5— y la **fuga de `datos_taller2.R`**. Ninguno de los
> dos hace falso el enunciado; el primero lo hace contradictorio consigo mismo y el segundo
> regala la respuesta de T2 a quien clone el repositorio.
> **Y del 2026-09-11:** M-18, la fuga y M-20 están cerradas, así que no queda nada de lo que este
> párrafo pedía antes de publicar. La rama se fusionó en `main` ese día — ver el final del §0.

**Nota para quien retome esto en un worktree:** el arnés general dio un paso en rojo por una razón
que no era del material — a un worktree le faltan `datos/` y `precalculo/cache/`, que están
ignorados y viven en la copia principal. `verifica_bloques.py` mata la sesión de R al no encontrar
`cache/dep_disuelto_1122.rds` y reporta 47 bloques con discrepancias, que es un falso rojo
espectacular. Se arregla enlazando o copiando esas dos carpetas desde la copia principal.

**C10 HECHA (2026-09-10)** · `precalculo/verifica_taller2.R`, **1 321 líneas, fuera de git a
propósito** (`.gitignore:149`, comprobado con `git check-ignore`): imprime el régimen de los tres
patrones de cada trío, que es T2(a) y T2(b) enteras. Molde: `verifica_taller1.R`, estructura
copiada — `ancla()`, `arranque()`, una hoja por tarea, `--lista`, `avisa_colisiones()`,
`exige_ignorado()` antes de escribir un byte. **No entra en el arnés**, y `audita_todo.sh` no lo
recoge: nombra a `verifica_bloques.py` explícitamente y no hay ningún glob que lo alcance.

```
precalculo/rscript.sh precalculo/verifica_taller2.R 1012345678
precalculo/rscript.sh precalculo/verifica_taller2.R --lista curso.txt      # documento, nombre, portada
precalculo/rscript.sh precalculo/verifica_taller2.R --patrones             # los 60 y su régimen
precalculo/rscript.sh precalculo/verifica_taller2.R --localidades          # la clave de T1 y de T1(d)
precalculo/rscript.sh precalculo/verifica_taller2.R 1012345678 --json calificacion/esperado/
```

**Lo que deduce en vez de recordar**, que es lo que hace que la herramienta signifique algo: las
familias salen del CSV publicado por Clark-Evans, y la prueba de que la deducción es la buena es
que encuentra **un patrón de cada régimen en cada uno de los doce tríos** y **los 24 propios
agregados**, sin que eso esté escrito en ninguna parte. Márgenes reales, impresos en cada pasada:
agregado hasta **R = 0,8260**, aleatorio de **0,9661 a 1,1236**, regular desde **1,3883**.
**Lo que no duplica:** el orden de los mapas de T2 se **lee del HTML publicado**
(`ORDEN_MAPAS_T2`), no se copia — si el ensamblador cambiara la permutación y el calificador no se
enterara, el emparejamiento impreso sería falso y nadie lo notaría.
**143 anclas** en el arranque, todas en pie: las 16 localidades rehechas desde el GeoPackage (peor
desvío en área 5,0e-9 km²), los 60 dibujos contra el CSV (1,22e-4, que es el medio paso de
cuantización), las 60 G, K, L y g contra el JSON (**5,04e-9**) y los 12 recuentos de nodos fuera de
banda. Probado sobre **36 documentos** que cubren las 16 localidades, los 12 tríos, las 12
envolventes y todos los contrastes: 36 hojas, cero errores, 100 s.

**M-14, confirmado por tercera vez y con la cifra más dura hasta ahora.** Medido contra
`ppp_F_borde()` —la F del capítulo 4, sobre rejilla de sondas y `nncross`—: el peor desacuerdo
sobre los 60 patrones es **0,9662**, sobre una función que vive en [0, 1]. Dicho de la forma en que
lo ve un estudiante, para el trío 03: **la F publicada llega a 0,99 en r = 0,010, donde la de
verdad vale 0,046**. Por eso `hoja_t2()` **se niega** a imprimir cualquier lectura apoyada en F y
declara T2 no calificable, mientras imprime el emparejamiento —que sale de las coordenadas y sí es
correcto—.

**M-18 · NUEVO, y lo encontró este guion: el pico/media publicado sale de una rejilla que no es la
del enunciado.** ✅ **CERRADA EL 2026-09-10 — ver el final del §0.** `genera_taller2.R` calcula `t5` con `DIMYX <- 80L`; el bloque de código de T5 le
fija al estudiante `dimyx = 256`. Medido sobre las 16: con 80 el cociente publicado se reproduce
**exacto** (peor desvío 0,000000) y los 16 recuentos de focos cuadran; con 256 el peor desvío es
**0,680577** —Ciudad Bolívar, 18,33 publicado contra 17,65— y **15 de los 16 difieren ya en el
segundo decimal**, que es la precisión a la que el informe lo publica («un pico de X veces»).
Los recuentos con 256 fallan en 2 de 16 (Usme 2→3, Barrios Unidos 3→4), que es el 14 de 16 de M-17.
**Por qué importa y no es cosmético:** M-9 eligió el cociente pico/media *precisamente* por ser
continuo y estable, y es el instrumento con el que T5 se califica; el enunciado avisa de que el
**entero** de los focos depende del ráster y **del cociente no dice nada**. El estudiante cuidadoso
que siga el bloque al pie de la letra reportará una discrepancia que el taller le dice que no
debería existir. **Dos salidas, y son de Javier:** (1) el enunciado extiende el aviso del ráster al
cociente —es una frase, y de paso es la lección de T5(c)—, o (2) el precálculo regenera `t5` con
`dimyx = 256`. Mientras tanto la hoja imprime **las dos cifras** y avisa variante por variante.
**No se tocó el ensamblador**: la decisión probablemente se la come la regeneración de M-14.

**M-19 · la clave de T1(c) es sistemáticamente gruesa, y hay que saberlo antes de corregir.** La
rejilla más fina en que **ninguna** celda baja de 5 es **k = 2 en nueve de las dieciséis**, **k = 3
en cuatro** y **no existe en tres** (Usme, Tunjuelito, Los Mártires). No es un defecto —el
enunciado ya contempla «si no existe ninguna, dilo y sostenlo»—, es que con una ventana poligonal
casi cualquier k deja una astilla de área minúscula y esa astilla **es** una celda. Un k = 2 no se
puede marcar como error de bulto. Y de los trece que sí tienen rejilla legible, **cuatro no
rechazan en ella** (Rafael Uribe, Fontibón, Barrios Unidos, Antonio Nariño) habiendo rechazado con
el 5×5 ilegible: ahí está la sustancia de la tarea.

**Una trampa del `.geomapa` que costó un ancla rota y conviene dejar escrita.** El encuadre de un
geomapa cuantiza sobre el **lado mayor** de la caja, centrado —`r = max(rx, ry)`, ver
`geomapaCajaQ()` en la plantilla y `geo_partes()` en R—, **no eje por eje**. Decodificar por ejes,
que es lo primero que uno escribe, desplaza el eje corto hasta **6e-2** y hace saltar el ancla del
dibujo. Saltó, y por eso está escrito aquí.

**Lo que C10 NO hace, y va dicho en la cabecera del guion:** no pone notas —compara cifras y
presenta la evidencia—, no ejecuta `genera_taller2.R`, y **no para** por M-14 ni por M-18. Esa
última es una decisión, no un descuido: `ancla()` para ante lo que no se sabe, y estos dos están
medidos y escritos aquí esperando una decisión; convertirlos en un `stop()` habría sido una forma
elegante de no escribir la herramienta. Lo que hace en su lugar es gritarlos en cada pasada, con la
cifra, y negarse a imprimir la clave que dependa de ellos.

**M-14 CERRADA (2026-09-10) · las F regeneradas, y T2 vuelve a tener su evidencia.**

Lo que se hizo, y en este orden:

1. **`genera_taller2.R`**: `Fest()` fuera. La F sale de `ppp_F_borde()` (en `puntual.R`), que es
   el camino que ya usaba `genera_cap4.R` — rejilla de 400 × 400 sondas, `nncross` para la
   distancia al punto más cercano y `bdist.points` para descartar las sondas a menos de r del
   borde. Las tres son exactas; `distmap()` no. Devuelve la curva ya en la rejilla de publicación,
   así que la F ni siquiera se interpola.
2. **`datos_taller2.R`**: la misma decisión, para que las dos mitades no se separen. Y su
   sección C **pasa de comparar una columna a comparar las cinco**: `300 curvas comparadas contra
   el JSON (60 patrones × 5 columnas), todas cuadran`. Comparar solo G fue el agujero.
3. **`audita_taller2.py`**: tres comprobaciones nuevas. La que importa **no reimplementa nada** —
   es la **cota de la unión**: los discos de radio r alrededor de n puntos cubren como mucho
   n·πr² de área, así que F(r) ≤ n·πr²/|W₋ᵣ|. Una F que la viole no es una F, venga de donde
   venga. Las otras dos son la monotonía y la curva entera recalculada con `cKDTree` en vez de
   `nncross`, que sí son dos implementaciones distintas.
4. **Regenerar.** 16,8 s, 41 anclas verdes.

**La regeneración no movió NADA más, y está comprobado campo a campo:** el diff del JSON viejo
contra el nuevo son **2 239 valores de F y la fecha de generación**, y **una sola diferencia fuera
de la columna F** (`meta/generado`). El CSV de los patrones sale **byte a byte idéntico**. Es
decir: las 1000 variantes, las 16 localidades, los 24 propios, los 12 tríos, las 12 envolventes y
la sección t5 siguen exactamente donde estaban, y con ellos C1, C2b y todos los anclajes del plan.
La semilla no se tocó — quitar una llamada a `Fest()` no consume números aleatorios.

**Lo que estaba roto era peor de lo que decía M-14, y ahora se puede medir.** La cifra que importa
para T2(a) es el hueco **G − F en r = 0,05**, que es la firma con la que se distingue un régimen de
otro. Doce patrones de cada régimen:

| régimen | con la F rota | con la F buena |
|---|---|---|
| agregado | **+0,012** [−0,053, +0,099] | **+0,662** [+0,486, +0,775] |
| aleatorio | **−0,261** [−0,462, −0,128] | **−0,005** [−0,117, +0,099] |
| regular | −1,000 [−1,000, −0,780] | −0,732 [−0,857, −0,479] |

No era «media evidencia perdida»: **era evidencia que apuntaba al revés**. Con la F rota el
agregado —cuya firma es G ≫ F— daba +0,01, indistinguible de cero, y el aleatorio —cuya firma es
G ≈ F— daba −0,26, que es lo que debería dar un regular. **Un estudiante que razonara
correctamente sobre las curvas publicadas habría clasificado el agregado como aleatorio y el
aleatorio como regular.** Con la F buena los tres rangos **no se solapan** y van en la dirección
del libro. Y de paso: la F rota ya estaba en 0,99 en una mediana de **44 de sus 51 nodos** —el
86 % de la curva dibujada era una recta plana—; la buena, en 18 de 51.

**Verde en toda la cadena**, y cada cosa comprobada donde se puede ver:
`audita_taller2.py` **183 · 0 · 0** (eran 180; las tres nuevas son las de la F) ·
`audita_texto_taller2.py` **84 · 0** · `sin_aritmetica.py` y `campos_vivos.py` limpios ·
`cuenta_sitio.py` con los nueve enlazados · HTML reensamblado a **1 146 KB**, 7 módulos, 5 tareas.
En el navegador, con la variante 678 cargada: consola sin errores, los tres mapas del trío con
n = 162/149/162 —que es el emparejamiento que el calificador predice—, los tres lienzos de curvas
con 11 000–12 200 píxeles de tinta y **0 desbordamientos a 1 280, 375 y 318 px en los siete
módulos con los bloques de código DESPLEGADOS**, que es el caso duro y no se había probado antes.

**Y la confirmación que más tranquiliza, porque venía escrita de antes:** `verifica_taller2.R` —el
calificador de C10, escrito ayer sin saber cómo iba a quedar esto— dice ahora
`F publicada contra la honesta: 5.05e-09 — M-14 RESUELTO, se puede calificar T2`, y su hoja de T2
ha dejado de negarse a imprimir la clave. Tres implementaciones independientes de F —R por sondas,
scipy por `cKDTree` y la del calificador— coinciden en 5e-9, que es el redondeo a diez decimales
del JSON.

**Lo que el arnés obligó a añadir.** `prueba_auditor_taller2.py` declaró las tres comprobaciones
nuevas como «tipos que todavía no ataca», que en este proyecto es el mismo estado que «no se sabe
si pueden fallar» — y es exactamente así como la F se coló la primera vez. Se le añadieron **tres
inyecciones**: una F que satura enseguida (M-14 reproducido tal cual, y viola la cota por un factor
de cuarenta), una F que baja en un nodo, y una que se aparta de la verdadera **sin** violar la cota
— esta última existe para que la comprobación de las sondas tenga que demostrar algo por su
cuenta. Con ellas el arnés pasa de **46 a 49 inyecciones, 49 de 49 cazadas**, y —lo que importa—
de **31 de 34 tipos vistos fallar a 34 de 34**, que es la primera vez que este arnés no deja
ninguna comprobación sin demostrar. El arnés además señaló que dos rótulos míos pasaban de 58
caracteres y falseaban su recuento de cobertura; acortados.
> Quedan **5 rótulos largos que no son de este trabajo** —cuatro son «<localidad>: su campo
> `localidad` coincide con su clave <localidad>» y uno el de los campos publicados—. Falsean el
> recuento de cobertura del auditor entero, no solo el de la F. No se tocaron aquí.

**Lo que sigue abierto y NO lo toca esto:** **M-18** (el pico/media de T5 sale de `dimyx = 80` y el
enunciado pide 256) —la puerta estaba abierta al regenerar y se dejó pasar a propósito, porque
tiene dos salidas y la buena puede ser la de prosa, que es además la lección de T5(c)— y **la fuga
de `datos_taller2.R`**, que solo se cierra cambiando la semilla, y cambiar la semilla ya no es
gratis: rehace las 1000 variantes y con ellas todos los anclajes que esta regeneración acaba de
dejar intactos.

**M-18 CERRADA (2026-09-10) · las dos rejillas son la misma, y ahora hay tres sitios donde
cuadra.** Se eligió la salida (2) —regenerar `t5` con `dimyx = 256`— y no la de prosa, por dos
razones y ninguna es la consistencia:

1. **256 es la rejilla correcta en sus propios términos.** 80 está por debajo del `dimyx` por
   defecto de `density.ppp` (128) y deja unos 200 m de píxel en las localidades grandes: **menos de
   tres píxeles por σ**, que es una superficie infrarresuelta. Con 256 son unos nueve.
2. **La otra salida ensuciaba la señal de T5.** Dejar el desajuste obligaba al enunciado a
   confesar que el informe usó otro ráster, y entonces el estudiante ya no puede atribuir su
   desacuerdo con el informe a lo que T5 discute —el σ que alguien eligió sin declararlo—, porque
   hay un segundo desacuerdo metido de matute. El ráster sigue siendo el **tercer mando** y el
   enunciado lo sigue diciendo; lo que ya no hace es inyectarlo en la premisa.

**Qué movió, exactamente:** el diff del JSON son **20 valores, todos dentro de `/t5`** — 16 picos,
2 σ (Rafael Uribe 301→300, Puente Aranda 300→250) y 2 recuentos de focos (Usme 2→3, Barrios
Unidos 3→4, que son justamente los dos que M-17 había medido como discrepantes). **Cero cambios
fuera de `/t5`**: patrones, curvas, variantes, envolventes y localidades intactos. Las dos guardas
duras del generador aguantaron —dispersión mínima **1,47** ≥ 1,40 (Teusaquillo) y **mínimo 2 de 4
selectores** contradicen al informe (Kennedy)—, así que T5 conserva su filo: el cociente sigue
moviéndose entre selectores de **1,47 a 5,79 veces**.

**Lo que el arreglo dejó desfasado, y también se arregló** —porque una prosa que describe un
desajuste que ya no existe es el mismo defecto que M-18 al revés—:

- el comentario de MOD6 en `ensambla_taller2.py` decía «medido con `dimyx = 256`, catorce de los
  dieciséis recuentos se reproducen y dos se van por uno». Ya no: se reproducen los dieciséis, y el
  comentario ahora explica **por qué las tres constantes tienen que ser la misma**;
- **T5(a)** decía «si tu recuento no coincide con el del informe, dilo y explica de qué depende ese
  entero» — un condicional que ya no se dispara nunca. Ahora **promete** lo contrario y lo
  convierte en autocomprobación: «las dos cifras tienen que darte *exactamente* las del informe:
  si no te dan, algo cambiaste respecto del bloque —y lo más probable es que sea la rejilla—. Di
  qué fue, y de paso ya tienes media respuesta a (c)». Es mejor tarea que antes: pasa de anticipar
  un fallo a dar un anclaje que se puede verificar, como el `stopifnot` de T1;
- la nota de la rejilla ahora dice que de `dimyx` dependen **las dos** cifras, no solo el entero.

**Y el calificador cambió de forma, no solo de constante.** `verifica_taller2.R` ya no compara «la
del precálculo contra la del bloque» —eso era andamiaje de un defecto abierto—: comprueba lo único
que manda, **que el cociente publicado se reproduzca con la rejilla que el enunciado fija**, y solo
si falla paga el cálculo con la rejilla vieja, para decir cuál de las tres constantes se movió.
Dice ahora `T5 · pico/media con dimyx = 256: peor desvío 4.97e-09 — M-18 RESUELTO`, y su hoja de T5
ha pasado de avisar de que no se puede penalizar la diferencia a explicar que una diferencia
**significa** que el estudiante cambió el bloque.

**Verde otra vez:** auditor **183 · 0 · 0** · texto **84 · 0** · `sin_aritmetica.py` y
`campos_vivos.py` limpios · portada con los nueve enlazados. En el navegador, el informe de San
Cristóbal dice ahora «1 foco · pico de 4.82 veces» y el bloque a 256 da **4.8213 · 1 foco**: el
estudiante lo reproduce exacto. El precálculo tarda ahora **66 s** en vez de 17 (256² son diez
veces los píxeles de 80²), que es un precio razonable para algo que se corre una vez.

**LA FUGA CERRADA (2026-09-10), y con ella la fase 1 entera.** Tenía tres salidas y se hicieron
las dos que sirven, porque cada una cierra una mitad distinta:

**1. El guion deja de saber generar.** `datos_taller2.R` se versiona —tiene que hacerlo: es lo que
permite reconstruir el dato del enunciado desde fuera, que es la lección del Taller 1— y hasta hoy
repetía dentro los sesenta sorteos con `set.seed(20262)` y las tres funciones generadoras, metidas
en una lista cuyos **nombres** eran los tres regímenes. Publicaba, sin que nadie lo mirara, cuántas
familias hay, cómo se llaman, **que cada trío trae una de cada** —lo que convierte la clasificación
de T2 en un emparejamiento— y, corriéndolo, cuál es cuál.
Ahora las coordenadas las escribe el precálculo, que no viaja, y ese guion solo las **copia y las
comprueba**. Pierde la capacidad de regenerar por su cuenta, que es exactamente lo que se quería
que perdiera, y su sección C queda **más fuerte**: en vez de «regenero y me da lo mismo» dice «lo
que se entrega reproduce las curvas publicadas», que es la propiedad que importa y no necesita
saber la semilla. Sigue en **300 comprobaciones** (60 × 5 columnas).

**2. La semilla pasa de 20262 a 20263, y eso desactiva la copia que ya está en `origin/main`.**
Reescribir el archivo hoy no borra el historial: cualquiera puede sacar la versión vieja con
`git show`. Lo que sí se puede es **hacerla inútil**. Comprobado corriéndola contra el material
nuevo: para en su propia sección C con
`PARADO: la G del propio 1 no cuadra con el JSON (dif 2.53e-01). El dato entregado y el enunciado
describen patrones DISTINTOS`. Es decir: quien la desentierre y la ejecute obtiene sesenta patrones
que **no son los del taller**, y el guion se lo dice. Se pudo hacer porque **no se ha repartido**;
después de repartir, esta línea no se toca (§9).

**Lo que NO cierra ninguna de las dos, y hay que decirlo:** el historial sigue enseñando el
**diseño** —que hay tres regímenes, cómo se llaman y que cada trío trae uno de cada—. Eso sobrevive
a cualquier semilla y solo lo borra reescribir la historia de un repositorio público. **Es decisión
de Javier y no se tocó.** El enunciado sigue sin decirlo, que era el objetivo: «el enunciado no dice
cuántas familias hay, ni cómo se llaman, ni que en cada trío haya una de cada».

**La guarda que faltaba, en dos sitios.** Dentro del propio guion —se lee a sí mismo y **para** si
vuelve a llevar `rThomas(`, `rpoispp(`, `rSSI(` o `set.seed(` fuera de un comentario; los literales
van partidos para que la guarda no se cace a sí misma— y en `audita_taller2.py`, sección nueva
**«Lo que un estudiante puede leer en el repositorio»**, que es la que faltaba: el auditor vigilaba
el JSON y nunca los guiones que sí viajan. Las dos comprobaciones **se probaron a mano** —añadiendo
al final del guion una línea con `rpoispp(…)` y otra con `list(agregado = …, aleatorio = …,
regular = …)`, y las dos se pusieron en rojo con el defecto exacto entre corchetes— y después se
declararon `INATACABLES` en el arnés, porque leen **texto de código** y el arnés envenena JSON.
Atacarlas desde el arnés exigiría que `prueba_auditor_base.py` sustituyera también archivos de
código, y ese archivo lo comparten los siete capítulos.

**Y la resembrada destapó un defecto de verdad, que llevaba latente todo el tiempo.**
`audita_taller2.py` se puso en rojo en dos envolventes: recontaba **70** nodos fuera de banda donde
el JSON publicaba **71**. La causa: el generador contaba a precisión completa y publicaba las
curvas **redondeadas a seis decimales**, así que un nodo que se salía por menos de 5e-7 entraba en
el recuento publicado y **no** en el que el estudiante puede hacer — y T4(d) le pide contar los
nodos fuera de banda **sobre la banda que tiene delante**. Con la semilla 20262 las dos cuentas
coincidían por suerte. Arreglado invirtiendo el orden: se redondea primero y se cuenta después, así
que el recuento publicado es por construcción el que sale de las tres columnas publicadas. **El
auditor hizo su trabajo; lo que faltaba eran datos que ejercitaran la comprobación.**

**Qué se movió, y qué no.** Cambian los 60 patrones, las 12 envolventes y las 1000 variantes —todo
lo que depende de la semilla—. **No cambia nada de las 16 localidades ni de `t5`**: M-1, M-2, M-3 y
M-6 siguen palabra por palabra, porque salen del dato de Bogotá y no del sorteo. Las guardas del
generador aguantaron todas: **42 anclas verdes** (una más, la del CSV nuevo), 24 propios agregados,
un régimen de cada en cada trío, dispersión de T5 de 1,47 a 5,79 y mínimo 2 de 4 selectores
contradiciendo al informe. Márgenes de clasificación con la semilla nueva: agregado hasta
**R = 0,8155**, aleatorio de **0,9491 a 1,0868**, regular desde **1,3590** — siguen sin solaparse.

**Verde en toda la cadena:** auditor **185 · 0 · 0** (dos más, las de la fuga) · arnés **49 de 49**
y **34 de 34 tipos** · texto **84 · 0** · `sin_aritmetica.py` y `campos_vivos.py` limpios ·
`cuenta_sitio.py` con los nueve enlazados · calificador con sus **143 anclas** en pie, M-14 y M-18
resueltos, y su clave de T2 coincidiendo punto por punto con lo que dibuja el navegador (mapas
A/B/C con n = 100/169/102 para la variante 678, y los tres regímenes separados otra vez en G − F).
**0 desbordamientos a 318 px en los siete módulos** con los bloques desplegados, consola limpia.

**C10b · EL INSTRUMENTO HECHO (2026-09-10), y el §5.3 corregido de camino.** El control es una
actividad de aula del 28 de septiembre al 2 de octubre, así que lo único construible hoy es la hoja
que Javier se lleva a clase: `verifica_taller2.R --control curso.txt > control.txt`. Una fila por
estudiante con lo que tiene que leer en voz alta y una casilla que marcar; debajo, la línea
completa de su portada para cotejarla carácter a carácter cuando una fila no cuadre; aviso de
colisiones **antes** de entrar al aula; y una guarda que **para** si la hoja llevara una sola
respuesta —probada inyectándole una—.

**Y al construirla se cayó el §5.3.** Decía que cada quien lee «su localidad, su n y su λ», y esas
tres **no identifican una variante**: n y λ son función de la localidad, así que las tres llevan un
solo dato. Medido sobre **200 000 sorteos** de doce documentos:

| lo que se lee en voz alta | listas con dos indistinguibles |
|---|---|
| localidad, n y λ *(el §5.3 original)* | **99,66 %** |
| … + la localidad de contraste | **99,66 %** — no añadía nada; con M-20 cerrada, **67,31 %** |
| … + el patrón | 10,81 % |
| **localidad, n, λ, patrón y trío** | **0,00 %** |

Es decir: el control tal como estaba escrito **habría dado verde a dos estudiantes que hubieran
intercambiado documentos dentro de la misma localidad**, que es exactamente el fallo que existe
para cazar — y con 16 localidades y 12 personas eso pasa casi siempre. Una lista de doce sorteada
al azar para probar la hoja salió con **cuatro en Puente Aranda y tres en Bosa**. Ahora se leen
cinco cosas, y no coincide nadie.

**M-20 · LA LOCALIDAD DE CONTRASTE DE T4(a) NO INDIVIDUALIZA: hay DOS en las dieciséis.** ✅ **CERRADA EL 2026-09-10 — ver el final del §0.** Salió al
ver que el contraste no aportaba nada al control. Medido: **Antonio Nariño en 13 de las 16
localidades y Usme en las otras 3**, es decir **el 81,4 % de las 1000 variantes comparte
contraste**. La causa es la regla misma —«la de forma opuesta por perímetro/área»— y que Antonio
Nariño es el extremo de esa columna, así que es «la opuesta» de casi todo el mundo.
**Qué significa y qué no.** La tarea sigue siendo correcta: T4(a) pide cuál de las dos ventanas
sufre más y por qué el cociente lo predice, y ese razonamiento es de cada quien. Lo que **no** es
cierto es que el contraste individualice: el §5.1 lo vende como una de las cuatro cosas que fija la
variante, y en la práctica fija una de dos. **Consecuencia práctica: el déficit y el
perímetro/área de la localidad de contraste son la MISMA pareja de cifras para once o doce de los
doce**, y eso es un literal compartible en una tarea diseñada para que no los haya.
**Se deja como está y es decisión de Javier**, porque tiene dos lecturas legítimas y no es un
defecto: un patrón de referencia **común** para toda la clase es defendible —todos comparan contra
el mismo extremo, y lo que se califica es la comparación—, y cambiarlo obliga a tocar la regla del
generador y a regenerar otra vez. Si se quisiera individualizar, el arreglo es barato: en vez de
«la más opuesta», tomar la k-ésima más opuesta con k rotando por variante.

**C11 · EL INSTRUMENTO HECHO (2026-09-10).** Como C10b, la tarea ocurre en octubre y lo
construible hoy es la herramienta:
`verifica_taller2.R --sustentacion curso.txt > sorteo.txt`.

Hace lo que el §4.5 pide **con fecha** —«el sorteo se hace antes de la sesión, no durante, y queda
registrado»—: reparte las 36 preguntas del banco entre los doce **sin reemplazo**, asigna a cada
uno una de las 12 afirmaciones falsas, y **comprueba las tres cosas que hacen que el sorteo
signifique algo** (36 extracciones, 36 distintas, el banco agotado exactamente); si alguna falla,
para y no se usa. Por estudiante imprime además sus tres preguntas con el texto entero, su
afirmación, las casillas de **portada cotejada** y **bitácora leída**, y las seis decisiones
candidatas de su variante con un hueco para la elegida y su razón — **la elección es de Javier
habiendo leído el escrito**, y la herramienta no lo intenta.

**Reproducible sin tener que acordarse de un número:** la semilla sale del contenido de la lista
del curso y se imprime en la hoja, así que la misma lista da siempre el mismo sorteo —comprobado
byte a byte— y `--semilla N` lo fuerza cuando haya que volver a sortear a propósito.
**Y el banco no se copia:** se lee de `salidas/taller2_banco.md` y se **coteja contra el HTML
publicado**; si uno de los dos está rancio, para. Probado quitándole una pregunta al `.md`.
Detalle que costó una medición: la expresión que cuenta las filas del HTML tiene que ser laxa en el
texto de la celda, porque la pregunta 18 lleva `<code>` dentro y una expresión estricta daba 35 de
36 para siempre.

**⚠️ Y sale un riesgo operativo que el plan no tenía escrito: el §4.5 supone EXACTAMENTE doce.**
36 = 12 × 3. Con once sobran tres preguntas, con trece faltan tres, y en los dos casos el sorteo
sin reemplazo deja de cuadrar. El guion **para** con la aritmética delante en vez de sortear con
repetición en silencio — probado con una lista de once. Si el curso cambia de tamaño hay que
decidirlo **antes** del martes 13, y es barato: sobran y no pasa nada, o faltan y hay que escribir
tres preguntas más.

**M-20 CERRADA (2026-09-10) · el contraste rota, y el umbral que lo permite está medido.**

Javier eligió individualizar. Lo que se hizo, y lo que salió al medir **antes** de tocar la regla:

1. **La primera medición daba un defecto que no existía.** Comparando el déficit **máximo** de cada
   localidad, dos parejas de la regla vieja «ordenaban mal» (Engativá y Bosa contra Antonio Nariño)
   y la correlación con perímetro/área era 0,586. Es un artefacto: `Kest()` elige un rmax distinto
   para cada ventana —de **621 m** en Antonio Nariño a **4590 m** en Usme—, así que el máximo
   compara dos localidades a dos escalas. El bloque publicado y `verifica_taller2.R` fijan
   `r = seq(0, 2000, by = 50)` y leen **r = 1000 en las dos**; ahí la correlación es **0,949**
   (Spearman 0,962) y la regla vieja no invierte ninguna pareja. **La tarea estaba bien; lo que
   medía otra cosa era la guarda del generador**, y se cambió de paso.
2. **El orden NO es monótono entre formas parecidas**, y eso es lo que obliga a poner un umbral. A
   r = 1 km hay **9 parejas invertidas de 120** —Bosa y Rafael Uribe, Fontibón y Puente Aranda,
   Tunjuelito y Los Mártires, entre otras—, todas con razón de perímetro/área **menor que 1,4**:

   | razón de perímetro/área | parejas | invertidas a r = 1 km | factor de déficit mínimo |
   |---|---|---|---|
   | ≥ 1,3 | 87 | 1 | 1,07 |
   | ≥ 1,4 | 74 | 0 | 1,24 |
   | **≥ 2,0** | **38** | **0** | **1,38** |

   Se toma **2** y no 1,4 porque con 2 las 38 parejas ordenan bien **en todo el rango de r que
   comparten las dos ventanas**, no solo en el r del bloque — y T4(a) dice «en un r que declares».
3. **La regla nueva** (`genera_taller2.R`, §C y §H): cada localidad recibe la lista de las que le
   doblan o le parten el cociente, de la más opuesta a la menos, y el contraste **rota** por esa
   lista con `k %/% 16`. De **2** candidatas (Engativá) a **11** (Tunjuelito y Antonio Nariño).

   | | regla vieja | regla nueva |
   |---|---|---|
   | localidades que salen de contraste | 2 | **16** |
   | la más repetida | Antonio Nariño, **81,4 %** | Antonio Nariño, **21,2 %** |
   | mayor grupo con el mismo contraste en doce (media de 200 000 sorteos) | **9,78** | **3,72** |
   | contrastes distintos entre los doce (media) | 1,92 | 6,76 |

   No llega a cero y no puede: con 16 localidades y la condición de doblar el cociente, entre doce
   siempre se repite alguna. Pero deja de ser **el** literal de la clase.
4. **Lo que se movió, y lo que no.** Cambian **765 valores de `contraste` de 1000** y la fecha del
   `meta`, y nada más: **ningún otro campo de ninguna variante**, y `taller2_mapas.json` y el CSV
   **idénticos byte a byte** —el contraste no consume el generador aleatorio—. Las 16 localidades
   ya tenían mapa, así que el `.geomapa` de contraste no necesitó nada. **50 anclas en verde**
   (eran 42): las parejas y el mínimo del §C, el déficit a 1 km en Antonio Nariño (**45,47 %**) y
   Usme (**8,85 %**), **la guarda pareja a pareja** —ninguna de las 38 invierte el orden, factor
   mínimo 1,38— y las del reparto (salen las 16, ninguna es la propia, la más repetida ≤ 30 %).
5. **El enunciado dice la promesa en voz alta**: «una de las dos tiene al menos el **doble** de
   perímetro/área que la otra. *Cuál de las dos* no te lo dice el enunciado — lo dice tu cálculo».
   Y los dos bloques de código avisan de que `mide("Suba")` y `mide("Antonio Narino")` son un
   **ejemplo**: con la regla vieja ese ejemplo **era la respuesta** de cuatro de cada cinco, que lo
   podían correr sin tocar una letra — otra cara de M-20 que no estaba escrita.
6. **`audita_taller2.py` · siete comprobaciones nuevas (192)**, sin fiarse del generador:
   perímetro y área se rehacen con geopandas desde el GeoPackage. Razón mínima **2,033** en las
   1000 variantes; salen las 16; ninguna pasa del tercio; ninguna localidad con contraste único; y
   **el mecanismo que T4(b) pide nombrar**, con un buffer negativo: la franja de 100 m es
   **0,92–0,98 de r·perímetro/área** en las dieciséis y ordena igual que el cociente en las 38
   parejas. **Arnés 53 de 53 y 39 de 39 tipos**: cuatro inyecciones nuevas —una forma casi igual,
   la regresión exacta a «la más opuesta», una localidad que nunca sale, un contraste fijo— y las
   dos de la franja en `INATACABLES` con su prueba a mano (franja a 3000 m → [0,13 – 0,57]; el
   polígono de Usme bajo el nombre de Antonio Nariño → 21 parejas invertidas).
7. **Y el arnés cazó un defecto mío.** El primer borrador del bloque indexaba `pa[v["localidad"]]`
   a pelo, y **cinco inyecciones que ya existían mataban al auditor con `KeyError`** en vez de
   dejarle informar —la lección de C4, escrita veinte líneas más arriba en el mismo archivo—.
   Reescrito para que una pareja sin resolver no lo tumbe, con una comprobación que las cuenta.

**§5.3 rehecho con la regla nueva** (otra muestra de 200 000 listas de doce variantes distintas,
por eso 99,69 y no 99,66):

| lo que se lee en voz alta | regla vieja | regla nueva |
|---|---|---|
| localidad (+ n y λ) | 99,69 % | 99,69 % |
| localidad + contraste | 99,69 % | **67,31 %** |
| localidad + patrón + trío | 0,00 % | 0,00 % |

El contraste **ya distingue**, pero el control **sigue leyendo cinco cosas y no seis**: con patrón
y trío ya da 0,00 %, y una sexta cifra alarga los quince minutos sin comprar nada. Si el curso
creciera y las cinco dejaran de bastar, es la siguiente — así queda escrito en `verifica_taller2.R`.

**Verde en toda la cadena:** generador **50 anclas** · auditor **192 · 0 · 0** · arnés **53 de 53**
y **39 de 39 tipos**, cero reventones · texto **84 · 0** · `sin_aritmetica.py` y `campos_vivos.py`
limpios · calificador con sus **143 anclas** en pie y su clave de T4 siguiendo la regla nueva
(Bosa, que antes iba contra Antonio Nariño, va ahora contra Usme: 21,4 % contra 8,8 %, con 2,82
veces el perímetro/área) · **0 desbordamientos a 1280, 375 y 318 px en los siete módulos**,
consola limpia. `genera_taller2.R` y `verifica_taller2.R` sincronizados con la copia principal.

**FUSIONADA EN `main` (2026-09-11) · el Taller 2 se publica diez días antes de repartirse.**

Fusión `c95cc2a`, con `main` como primer padre —como la del capítulo 5—, construida en este
worktree sobre `origin/main` y empujada desde aquí. **La copia principal no se tocó**, porque la
otra sesión trabaja en ella: sigue en `be68325`, limpia, y se pone al día con
`git pull --ff-only`. Hasta entonces el HTML del taller no existe allí, así que `verifica_taller2.R`
no se corre desde esa copia.

- **Siete commits de `main` entraron sin un conflicto**: la segunda revisión del capítulo 5, el
  precálculo en Windows, el README de descarga de datos y la fuente #2. Solo `README.md` lo tocaban
  los dos lados, y en secciones distintas.
- **Los que tocan archivos que el Taller 2 usa no le cambian una cifra.** En `geo.R` cambió solo
  `geo_rejilla()` —el taller no publica rásteres y `genera_taller2.R` no la llama—; en `utf8.R`,
  solo el mensaje de parada fuera de UTF-8; y `entorno.R` no lo carga ningún guion del taller. Por
  eso **no se regeneró nada**, y la prueba es que el HTML reensamblado sobre el árbol fusionado
  sale **idéntico byte a byte** al comiteado.
- **El README tenía dos frases que la fusión habría publicado falsas**, corregidas en el commit que
  sale con ella: decía que T2 «no se puede publicar todavía» por las F de M-14, y que
  `datos_taller2.R` escribe el CSV de patrones — lo hacía hasta que se cerró la fuga; ahora lo
  escribe `genera_taller2.R` (línea 1005) y `datos_taller2.R` solo lo lee y lo coteja.
- **Verde sobre el árbol fusionado:** auditor **192 · 0 · 0** · texto **84 · 0** · calificador con
  sus **143 anclas** en pie · `cuenta_sitio.py` con los **nueve** archivos del curso enlazados y el
  Taller 2 en su tabla · `audita_todo.sh --rapido` en **ARNÉS COMPLETO EN VERDE**, con los nueve archivos del curso enlazados y ninguno de los publicados anunciado como pendiente.

**Lo que publicar hoy cambia del calendario.** La regla era «no se regenera después de repartir»,
y el reparto sigue siendo el lunes 21. Pero desde hoy el taller está en Pages y el buscador
funciona para cualquiera con el enlace: una regeneración antes del 21 sigue siendo posible, pero
**ya no es invisible** — cambiaría la variante de quien lo haya abierto. En la práctica la fecha
de congelación se adelanta a hoy, salvo decisión expresa.

**EL CALENDARIO SE MOVIÓ OTRA VEZ (2026-09-11), el mismo día de la fusión, y el empuje esperó.**
Entrega **domingo 11 de octubre de 2026, a más tardar a las 13:00**; sustentación **martes 13 de
octubre, presencial, en el espacio de la clase**. El control de la semana 9 no se mueve.

- **Llegó con la fusión hecha y el arnés corriendo, antes de empujar**, y por eso el calendario viejo
  no llegó a publicarse: el HTML fusionado decía «martes 6» y «jueves 8».
- **Las fechas estaban escritas a mano en cuatro sitios de la prosa** —dos en el módulo 1 y dos en
  el 7— y la hora en ninguno. Ahora viven en cuatro constantes de `ensambla_taller2.py`
  (`ENTREGA`, `HORA_LIMITE`, `SUSTENTACION`, `CONTROL`), y `audita_texto_taller2.py` tiene una
  sección nueva que **exige las tres nuevas y prohíbe las seis viejas**, con el dígito aislado para
  que «6 de octubre» no case dentro de «16 de octubre». Texto **94 · 0** (eran 84).
- **Y al tocar esos párrafos salió un defecto mío de C10b.** El enunciado seguía diciendo que al
  control se traen **«tres cifras: tu localidad, su n y su λ»**, cuando la hoja de `--control` pide
  **cinco** desde que el §5.3 midió que tres no distinguen a nadie — y el auditor de texto hasta lo
  exigía, con `("el control de la semana 9", "tres cifras")`. Arreglé el plan y el calificador y
  me dejé el enunciado: los doce habrían llegado al aula con tres cifras y se les habrían pedido
  cinco. Corregido en los dos párrafos y en el auditor.
- **Arnés de texto: 23 de 23**, con tres inyecciones nuevas —vuelve una fecha vieja, se pierde la
  hora, el control vuelve a pedir menos—. **Y la primera pasada dio 22 de 23, con razón**: la
  inyección del control solo alcanzó una de las dos menciones —la del módulo 1 está partida en dos
  líneas en el HTML— y el auditor, que exigía que «cinco cosas» *apareciera*, pasó en verde con el
  enunciado diciendo cinco en un módulo y tres en el otro. Es el fallo exacto de este cambio —una
  copia al día y la otra atrás—, así que se cerró en el auditor y no en la inyección: **toda frase
  que dice qué se trae al control tiene que decir «cinco cosas»**.

**Lo que el calendario nuevo mueve, y dos cosas que no puedo cerrar yo:**

1. **La sustentación cae en la semana 11, que es la del parcial 2.** El §2.2 contaba con «al menos
   cuatro días» entre las dos; ese margen ya no existe, y **la fecha del parcial 2 sigue sin estar
   escrita en ningún plan del repositorio**. Si es el jueves 15, quedan dos días; si fuera el mismo
   martes, no cabe.
2. **«En el espacio de la clase» vuelve concreta la comprobación que el §10 dejó viva**: que la
   sesión del martes 13 sea de **2 h** y no de 1,5. Con 2 h, 12 × 8 = 96 min caben con 24 de margen
   (§4.1); con 1,5, la refutación tiene que pasar al escrito.
3. **La lectura de C11 va del domingo a las 13:00 al martes**: día y medio útil —la tarde del
   domingo y el lunes—, algo menos que los dos días del calendario anterior.
4. **T5 podría abarcar más del capítulo 5, y no se toca.** Se quedó en los módulos 1–3 porque la
   entrega caía el segundo día de la semana 10; ahora cae después de cerrarla. La restricción deja
   de ser necesaria, pero el taller se reparte el 21 tal como está: ensanchar una tarea ya publicada
   es peor que dejarla estrecha. Si Javier quiere ensancharla, la ventana es antes del 21.

**Siguiente: el reparto del lunes 21.** La fase de construcción queda cerrada — C1…C11 tienen
hecho todo lo que se puede hacer antes de repartir, no hay ningún defecto abierto sobre el
material, y **M-20 se cerró** individualizando el contraste. Lo único vivo es una decisión y no un
fallo: las **tres logísticas de entrega** del §0 que siguen sin confirmar —canal y nombre del
archivo, que no hay plantilla LaTeX, y que no se publica límite de páginas; la hora quedó fijada el
2026-09-11—. Y cualquier
regeneración tiene que caer **antes** del lunes 21: después, `genera_taller2.R` no se vuelve a
correr (§9).
**Y OTRA VEZ EL 2026-09-11** —entrega el domingo 11 a las 13:00, sustentación el martes 13 en
clase—: ver la nota del final del §0. **El calendario se movió el 2026-09-09**: la entrega pasa del 18 de septiembre al **6 de octubre**
y la sustentación al **8**. Eso mueve el taller de la semana 7 a la **semana 10** y le cambia el
papel: ver **§2.2**, que es lo primero que hay que leer si vienes del plan anterior. Este archivo es la fuente de verdad del
Taller 2, igual que `PLAN_Taller_1_Caps_1_2.md` lo es del primero. Lleva el estado de cada paso
(C1…C10), las decisiones ya tomadas y las cuatro mediciones que las sostienen. **Leerlo entero
antes de proponer nada.**

**AUDITORÍA DE CONTENIDO (2026-09-11 y 12): T1 ARREGLADA, Y EL AUDITOR DE TEXTO YA LEE EL CÓDIGO.**
El arnés mira que las cifras cuadren; no mira si el enunciado pregunta lo que quiere preguntar.
Eso lo audita `AUDITORIA_CONTENIDO_TALLER2.md`, con su plan al lado en
`PLAN_Auditoria_Taller_2.md` —los dos **fuera de git**, porque contienen respuestas—. El método es
resolver cada tarea **a ciegas**, solo desde la página publicada, y cotejar **después** con
`verifica_taller2.R`; al revés, la clave contamina la lectura. Hechas **A0** (contra qué se mide) y
**A1** (T1 entera); **A2…A10** siguen.

- **Siete arreglos aplicados a T1, ninguno en el JSON**: la tarea es la misma y las 1000 variantes
  no se tocan. El más grave, **T1-1**: (c) pedía «la rejilla más fina en la que ninguna celda baje
  de 5» y **no excluía k = 1**, que cumple siempre —una celda, esperanza *n*—. En **Usme,
  Tunjuelito y Los Mártires** era la única, y `quadrat.test(nx = 1, ny = 1)` devuelve X2 = 0 con
  **0 grados de libertad** y «p-value < 2.2e-16»: un rechazo rotundo que es un artefacto. Tres de
  las dieciséis daban un veredicto falso siguiendo la letra, y el calificador —que buscaba entre 2
  y 12 sin decirlo— lo daba por mal. Ahora el enunciado **acota a k = 2, 3, 4 y 5, prohíbe k = 1 y
  dice por qué**. Medido sobre las dieciséis el 2026-09-12: **ninguna tiene rejilla legible por
  encima de k = 5**, así que la horquilla publicada es la búsqueda entera y las dos superficies no
  se pueden desmentir.
- **Y (c) pide ahora la tabla de los cuatro, no la primera que pase.** En **Engativá** el conjunto
  legible **no es contiguo** —k = 2 no pasa (4,70), k = 3 sí (6,03)—: quien buscara subiendo y
  parara en el primer fallo concluía «ninguna». La pista decía además que bajar el k sube las
  esperadas; es verdad de la media y **no de la mínima**, que es la que manda.
- **(d) dice qué se refuta.** «A mí también me rechazó con la caja» daba por hecho lo que a Los
  Mártires no le pasa (su caja no rechaza, p = 0,0605), y «no todas las localidades se comportan
  igual» empujaba a buscar un **veredicto que cambiara**, que solo tienen tres de dieciséis. Lo que
  se refuta es **«el error no importa»**, y eso se refuta desde cualquiera de las dieciséis. El
  calificador ya aceptaba las dos vías; ahora lo dice en voz alta y prohíbe bajar nota por la
  segunda.
- **El bloque de R decía cuál de las dos ventanas es la buena.** «las esperadas del *contraste
  bueno*», tres párrafos después de prometer que «nadie te va a decir cuál de las dos está mal».
  **El agujero era del auditor, no del redactor**: `audita_texto_taller2.py` prohibía «la ventana
  buena es» en la prosa y `texto_plano` tira los `<pre>`, así que los **92 comentarios** de los diez
  bloques quedaban fuera de todas las guardas. Ahora la misma lista pasa también por ellos, más una
  familia de patrones que caza al que adjudica —«el contraste bueno», «la ventana correcta»—.
  Texto **116 · 0** (eran 94) y arnés **25 de 25** (eran 23), con dos inyecciones nuevas dentro de
  un comentario.
- **El bloque de Python no imprimía nada corrido como guion**, no calculaba λ ni las áreas —que es
  todo (a)— y tiraba las esperanzas con `[:3]`, que es lo que necesita (c). Ahora da las mismas
  cifras que R, **comprobado dígito a dígito en Rafael Uribe y Engativá**, y el recuento de
  esperanzas bajas se imprime **una vez y sobre la misma ventana que R**: si Python contara también
  las de la caja, (c) tendría dos respuestas distintas según el lenguaje.
- Y dos de redacción: «el defecto de `spatstat`» quería decir «el valor por defecto», en una tarea
  cuyo verbo es «nombra el defecto»; y el taller citaba el capítulo 5 con un título que no es el
  publicado.
- **Lo que queda anotado y no arreglado:** (c) no dice de qué ventana son «tus celdas». Los dos
  bloques lo cierran calculándolo sobre el polígono y el calificador espera esa, así que en la
  práctica no hay ambigüedad; en el texto la hay. Es decisión de Javier, y está en el informe.
- El calificador (`verifica_taller2.R`, fuera de git, sincronizado en las dos copias) se puso al día
  con las dos superficies: **143 anclas, todas en pie**.

**Y A2 (T2, 2026-09-12) ENCONTRÓ LO QUE M-14 SE DEJÓ: EL BLOQUE QUE CORRE EL ESTUDIANTE.**
Siete arreglos más, y el primero es el hallazgo más caro de toda la auditoría.

- **🔴 El bloque de R de T2 calculaba la F con `Fest()`.** M-14 —`distmap()` devuelve distancias al
  cuadrado y `Fest()` las lee como distancias— se cerró el 2026-09-10 sacando `Fest()` del
  generador, de `datos_taller2.R` y del auditor. **El bloque publicado se escribió el día antes y
  nadie volvió a mirarlo**, porque los bloques del taller son de `arranque` y
  `verifica_bloques.py` no los ejecuta: son diez bloques que ninguna comprobación automática toca.
  Medido sobre los **36 patrones**: la G del bloque coincide con la publicada **exactamente** en
  los 36; su F se aparta hasta **0,9710**, y **nunca menos de 0,6258**. Para t03a daba
  F(0,005) = 0,8756 donde la curva del enunciado vale 0,0078. Y el comentario prometía que «las
  cifras coinciden». Ahora la F sale de la muestra reducida escrita a mano —`nncross` y
  `bdist.points`, las dos exactas—, y reproduce la curva publicada con **5 × 10⁻⁹** en los 36. El
  bloque de Python hace lo mismo: su F pasa de apartarse 0,22 a apartarse 5 × 10⁻⁹.
  **Y hay guarda**: `audita_texto_taller2.py` prohíbe ahora que cualquier bloque llame a `Fest(` o
  a `distmap(`, con su inyección en el arnés. Texto **118 · 0**, arnés **26 de 26**.
- **🟠 «¿Discrepan G y F?» (c) tenía dos lecturas y una rama muerta en cada una.** Con la del
  calificador —se separan— las tienen todos los tríos y la rama «construye el caso» no se abre
  nunca; con la de manual —apuntan a regímenes distintos— no la tiene ninguno de los 36 y la que no
  se abre es la otra. Y con la primera lectura la respuesta está literal en el módulo 7 del
  capítulo. Ahora (c) pide comparar cada curva **con su CSR** y decir a qué régimen apunta cada
  una: la rama se decide midiendo. La construcción que vale está comprobada por simulación —grumos
  apretados con los **centros regulares**: discrepan entre r = 0,050 y r = 0,065, y con los centros
  al azar la discrepancia desaparece—, así que el calificador puntúa el razonamiento y no la
  simulación.
- **🟠 (b) pedía «el \(r\) en el que tu curva decide» y el aleatorio no decide en ninguno.** En
  **11 de los 12** aleatorios ninguna curva se aparta de su CSR más de 0,10 en todo el rango. Misma
  forma que T1-1, y misma salida: «si alguna no decide en ningún \(r\), dilo y sostenlo».
- **🟠 El desplegable de coordenadas no publica los puntos del CSV**, aunque el enunciado decía que
  eran los mismos: publica el patrón **encajado en el recuadro del dibujo** (escala 1,0029) y
  redondeado a cuatro decimales. Reconstruida la transformación reproduce la tabla del navegador
  punto por punto. Una G calculada desde la tabla se aparta hasta **0,075** de la del CSV. Y la
  tabla la puso el ensamblador porque «para quien no ve el mapa, la tabla ES el mapa», así que el
  peor dato le tocaba a quien usa lector de pantalla. El enunciado ya lo dice y manda al CSV.
- **🟡 Y dos que no son defectos y hay que saber al calificar:** en los doce regulares F se aparta
  de la CSR **0,09 a 0,19** frente al **0,54 a 0,74** de G —la simetría del módulo 7 no es
  simétrica—, y los tríos **no se reparten por igual**: 96 variantes para los tríos 1–8, 88 para el
  9 y **48** para el 10, 11 y 12. Lo primero está en el calificador; lo segundo se mide en A6.

**Y A3 (T3, 2026-09-12): UN PATRÓN DE LOS 24 CONTESTA AL REVÉS QUE LA CLAVE.**

- **🔴 p24 no tiene ningún \(r\) en el que \(g\) vuelva a 1.** Su \(g\) baja hasta **1,0687** en
  \(r = 0{,}140\) y **remonta a 1,1982** en el último nodo, así que en todo el rango publicado hay
  más vecinos de los que daría la CSR. Toda T3 se apoya en lo contrario: (a) refuta al informe
  porque \(g\) vuelve a 1 mientras \(K\) no, y (b) pide ese \(r\) y el \(K\) que hay en él.
  Para p24 la conclusión del informe —«la agregación se extiende a lo largo de todo ese rango»— es
  la que hay que **confirmar**, y dos de las tres cifras de (b) no existen. **El calificador
  imprimía «g vuelve a 1 en r = NA»** y daba por buena la refutación; y el comentario de diseño de
  este ensamblador afirmaba que «g ha vuelto a 1 entre r = 0,070 y r = 0,170» **en los 24**, que es
  la medición sobre la que se escribió el enunciado. **Le toca a 32 de las 1000 variantes: en una
  clase de doce, un 32 % de que alguien la tenga.** Arreglado en la letra y en la clave, sin
  regenerar: (a) y (b) admiten ahora «no vuelve a 1 en el rango», igual que T1(c) admite «no hay
  rejilla legible», y el calificador tiene rama propia para p24.
- **🟠 «En qué \(r\) vuelve \(g\) a 1» era ambiguo**: en **14 de los 24** la curva vuelve a asomar
  por encima de 1 después de su primer regreso —hasta **1,988** en p13—, y T3, a diferencia de T4,
  **no publica banda** con la que separar el ruido. Ahora se pide la **primera** vez, con el aviso,
  y el calificador imprime hasta dónde remonta y no baja nota a quien elija otro \(r\) y lo
  justifique.
- **🟡 (b) pedía el máximo de \(g\) y en 23 de los 24 está en \(r = 0\)**, que es el nodo del que
  el módulo 9 del capítulo dice «no es una escala característica: es donde empieza a mirarse». El
  calificador ya lo avisaba; el enunciado no, así que la mejor respuesta posible no tenía dónde
  ponerse. Ahora (b) pregunta **dónde** cae ese punto y remite al módulo 9.
- **🟠 El bloque de Python prometía lo único que no puede dar**: decía que su \(g\) sirve «para ver
  dónde vuelve a 1», y ese \(r\) **no coincide con la tabla en 13 de los 24** —hasta 0,020 en
  p21— y en p24 **señala un regreso que no existe**. Su \(K\), en cambio, se aparta menos de 0,001
  en los 24. Escribir la \(g\) con núcleo de Epanechnikov y ancho de Stoyan —lo que hace
  `spatstat`— mejora a 5 de 24 y sigue sin coincidir, así que no compensa: se arregla declarando
  bien.
- **Lo que salió limpio:** la premisa del informe se renderiza por variante y es cierta en los 24
  (p16 → 0,210, p24 → 0,250); (c) es contestable en las dieciséis, con `pcf()` funcionando en todas
  y un \(r_{\max}\) que va de **621 m** en Antonio Nariño a **4 590 m** en Usme; y el módulo 2 sí
  dice lo que (c) pide nombrar.

**Y A4 (T4, 2026-09-12): EL INFORME DE T4(c) DECÍA «0 DE 0 NODOS» Y LUEGO QUE LA CURVA SE SALE.**

- **🔴 Dos campos del mismo precálculo, redondeados distinto.** `r` va a **seis** decimales
  (`0.005859`) y `tramo` a **ocho** (`0.00585938`), y las tres superficies que los cruzan usaban una
  comparación estricta que deja fuera el nodo del que salió el tramo. Cuando el tramo es **un solo
  nodo**, el informe publicaba «se sale de la banda del 95 % en **0 de 0 nodos evaluados**» y a
  renglón seguido «como la curva abandona la banda… p < 0,05»; el panel derecho de la figura salía
  **vacío**; su tabla decía «0 nodos»; y la hoja del calificador, «0 nodos, 0 fuera (NaN)». Le pasa
  a las envolventes **3 y 10** = **168 de las 1000 variantes**, o sea un **89 %** de que le toque a
  alguien en una clase de doce. Y no era solo el caso extremo: las otras diez perdían los nodos de
  los bordes —la 1 decía «69 de 161» cuando son **70 de 162**— y con ello se rompía en silencio la
  identidad que hace la tarea, que **todos** los nodos fuera de banda del rango caen dentro del
  tramo. Con medio paso de tolerancia se cumple en las doce. Arreglado con un único ayudante
  `dentroTramoT2()` que usan el informe, el gráfico y la tabla, y la misma regla en el calificador.
- **Guardas nuevas, porque el `tramo` no lo miraba nadie**: `audita_taller2.py` comprueba que cada
  tramo contenga al menos un nodo y que recoja todos los que se salen —**216 · 0 · 0**, eran 192—,
  con dos inyecciones nuevas en el arnés: **55 de 55**.
- **🟡 En ocho de las doce envolventes se sale MENOS de lo que el 5 % esperaría** (0,19 % en dos de
  ellas, frente a los 25,7 nodos que darían 513 × 5 %). (d) está bien escrita —dice «tampoco
  decide»—, pero el calificador daba por hecho el exceso; ahora avisa de la dirección.
- **🟡 En Antonio Nariño y Los Mártires el déficit sale `NA` a partir de r = 1800 m.** (a) deja
  declarar el \(r\), así que conviene que el calificador lo sepa. Con el r del bloque (1000 m) no
  pasa en ninguna de las dieciséis.
- **Lo que aguantó, y es lo más importante de T4:** la promesa del enunciado —«una de las dos tiene
  al menos el doble de perímetro/área»— se cumple en las **76 parejas**, con razón mínima **2,0331**
  (Teusaquillo contra Tunjuelito) y mediana 2,50; y la de (b) —que el cociente predice cuál sufre
  más— **no se invierte en ninguna de las 76 parejas ni en ninguno de los 40 valores de \(r\) del
  bloque**, así que el estudiante puede declarar el \(r\) que quiera. M-20 aguanta.

**LA CARGA DEL ESCRITO, contra las 5 h que Javier fija (2026-09-12).** Medido sobre la resolución
propia, contando solo hacer las cuentas y decidir, **sin redactar**: T1 de 1 h a 1 h 30 · T2 de 1 h
a 1 h 30 · T3 de 45 min a 1 h · T4 unos 1 h 15 · T5 pendiente de A5. **Las cuatro primeras suman de
4 h a 5 h 15**, así que las cinco horas se agotan antes de T5, de la bitácora y de escribir el
informe —que en un taller cuyo 40 % es el escrito no es el resto, es la mitad—. La estimación total
va de **7 a 9 h**. Las sugerencias, al cerrar A5.

**Y A5 (T5, 2026-09-12): EL BLOQUE CONTABA UN FOCO DONDE NO HAY NINGUNO.**

- **🔴 `focos()` devolvía 1 con la región vacía.** Cuando el ancho aplana tanto la superficie que
  **ningún píxel supera el doble de la media** —comprobado en Antonio Nariño con el σ de Scott:
  **0 de 25 312 píxeles**—, `solutionset()` da una región vacía y `connected()` sobre una región
  vacía devuelve una imagen con **un nivel**. El bloque publicaba «focos = 1». No reventaba: mentía.
  Pasa en **7 de las 64** combinaciones (16 localidades × 4 selectores) y toca a **Engativá —tres de
  sus cuatro—, Fontibón, Tunjuelito y Antonio Nariño**: **249 de las 1000 variantes**, un **96 %**
  de que le toque a alguien en una clase de doce. Y pega justo en (b): con la cifra falsa, Engativá
  parecía conservar el foco del informe con tres selectores cuando la verdad es que **con tres no
  hay ninguno**, que es la refutación más fuerte que la tarea admite. **El calificador ya lo hacía
  bien** (`if (is.empty(s)) 0L`) y **el bloque de Python también** (`label` devuelve 0): era el de R,
  solo. Misma forma que T1-1.
- **🟠 El mapa de (a) dibujaba las sedes del resto de Bogotá.** `ppp()` descarta las de fuera —el
  idioma de T1— pero se las guarda en `attr(p, "rejects")`, y `plot.ppp()` las pinta encima: **1 951
  cruces grises** alrededor del polígono y sobre la barra de color, con un aviso que parece un
  error. Las cifras no cambiaban; la figura, que es el entregable de (a), sí.
- **🟡 La columna del cuarto selector se llamaba `scott.sigma.x`** — `bw.scott(p)[1]` conserva el
  nombre. `unname()`.
- **H2 resuelta, y al revés de lo que parecía.** El comentario prometía que decir por qué se toma
  uno de los dos anchos de `bw.scott` «es parte de (d)», y (d) no lo pide. Añadirlo a (d) habría
  sido **duplicar el módulo 3 del capítulo 5**, que ya lo explica entero. Se arregló el comentario.
- **Lo que salió limpio:** (a) reproduce el pico/media y el recuento del informe **exactos en las
  dieciséis**; los cuatro selectores corren **64 de 64** sin un error; y hay materia en todas las
  variantes —el cociente se mueve entre selectores por un factor de **1,47 a 5,79**—.

**LA CARGA DEL ESCRITO, CERRADA (2026-09-12).** Medido sobre la resolución de las cinco: **cálculo y
decisión, 5 h 20 – 6 h 35**; escribir los cinco apartados, 1 h 30 – 2 h 30; la bitácora, 30 min.
**Total 7 h 20 – 9 h 35**, entre 1,5 y 2 veces el tope de 5 h que Javier fijó. Tres sugerencias, en
el §9 del informe de auditoría: (1) mover al bloque el trabajo que no se evalúa —la tabla de
rejillas de T1(c) y el bucle de los tres patrones de T2—, que ahorra 50–70 min y no toca la rúbrica;
(2) decir en el enunciado cuántas horas se esperan; y (3) la decisión de Javier, bajar de cinco
tareas al 8 % a **cuatro al 10 %**, con **T3** como candidata —la más barata, la más cercana al
capítulo y ya cubierta por el banco—, que **no toca el JSON ni las variantes**.

**SUGERENCIA 1 APLICADA (2026-09-12) · los bloques asumen lo que no se califica.** Dos sitios:
**T1(c)** imprime ahora la tabla de \(k = 2, 3, 4, 5\) con la esperanza mínima de cada uno —y de
paso enseña el caso no contiguo de Engativá de un vistazo—, y **T2** calcula **los tres** patrones
del trío en una pasada, los dibuja y tabula \(G\) y \(F\) en \(r = 0{,}02\), \(0{,}05\) y
\(0{,}10\). En los dos, R y Python dan los mismos decimales; las sondas de la \(F\) se calculan una
vez para los tres, así que T2 no tarda más. Lo que sigue siendo trabajo del estudiante es lo que la
rúbrica mide: **decidir** con la tabla, y **emparejar y argumentar** con las curvas. **Ahorro
estimado 50–70 min**: el cálculo baja a 4 h 20 – 5 h 30 y el total a 6 h 20 – 8 h 30, todavía por
encima de las 5 h.

**A6 (2026-09-12) · LA EQUIDAD, MEDIDA.** Las 1000 variantes son **únicas ya por (localidad,
patrón, trío)** y el control de la semana 9 identifica al **100 %** con sus cinco cosas —con
localidad y contraste solos identificaría a **ninguno**, que es lo que el §5.3 midió—. Los ejes:
localidad 62–63 (razón 1,02), envolvente 77–84, propio 32–48, **trío 48–96 (2,00)** y **contraste
12–212 (17,67)**, que es el precio de la promesa del doble de perímetro/área —las localidades
extremas se emparejan con casi todas y las del medio con pocas— y se queda en 21,2 %, por debajo
del 30 % que M-20 se puso.

**Lo que el §5.1 daba por bueno sin cifra, y ahora la tiene.** Simulando 10 000 clases de doce:
el **99,6 %** tiene un par que comparte localidad —**T1 y T5 enteras, el 16 % del escrito**, más la
mitad propia de T4(a)—, con **3,35 estudiantes de doce** afectados de media; el **100 %** comparte
trío o envolvente; y el **26,3 %** tiene un par que comparte localidad **y** trío, o sea el **24 %
del escrito palabra por palabra**. La decisión sigue siendo correcta —la defensa es el 60 % y es
individual—, pero al calificar hay que saberlo: **dos informes con las mismas cifras no son señal de
nada**. `verifica_taller2.R --lista` lo imprime ahora antes de las hojas.

**Y los ocho casos particulares que A1–A5 midieron se reparten así:** cero focos en T5, 249
variantes (96,8 % de que le toque a alguien en una clase de doce) · el veredicto que vuelca, 187 ·
sin rejilla legible, 186 · la envolvente de un nodo, 168 · el agregado más flojo, 96 · la rejilla no
contigua, 63 · la caja que no rechaza, 62 · la \(g\) que no vuelve, 32. **El 36,4 % de las
variantes no tiene ninguno y el 6,9 % tiene tres o cuatro**; seis juntan cuatro. **Ya no es
desigualdad de dificultad**: antes de la auditoría cinco de los ocho llevaban a una respuesta
bloqueada o marcada mal, y hoy los ocho tienen respuesta — en cinco de ellos, la más instructiva del
taller. Lo que hay que aceptar es que **el escrito no mide lo mismo en las 1000**, y que la rúbrica
puntúe «no hay» tan alto como una cifra, que es lo que las claves ya dicen.

**A7 (2026-09-12) · LAS DOS RÚBRICAS: LA ARITMÉTICA LIMPIA, Y DOS CONTABILIDADES DEL MISMO 40 %.**

- **La aritmética está bien**, comprobada a máquina: las dos rúbricas suman 100 y **sus 32 bandas
  cubren su rango sin un hueco ni un solape**.
- **🔴 El escrito tenía dos contabilidades del mismo 40 % y no decía cómo se juntan.** El módulo 1
  dice «las cinco tareas valen 8 % cada una» —y cada tarea lleva su distintivo de 8 %—, y la rúbrica
  dice que sus cinco dimensiones «se aplican al informe completo, **no tarea por tarea**». Cinco por
  ocho es cuarenta: hablan del mismo 40 %. Quien entregue cuatro tareas no sabía qué le cuesta, y
  quien califica tenía que reconciliarlo doce veces. Dicho ya: **las tareas pesan lo mismo dentro
  del informe** y la nota sale de las dimensiones sobre el informe entero; saltarse una resta en las
  dimensiones que alimentaba, y son varias.
- **🟠 A0-1 cerrada.** «Pertinencia», «corrección técnica», «interpretación de los resultados» y
  «syllabus» aparecían **cero veces** en el HTML. Ahora el módulo 1 publica el mapa: **P → A y C**,
  **T → C** (y el taller la exige además pidiendo que las cifras reproduzcan las del bloque), **I →
  B**, y **D y E son de este taller**. Resultó ser coste 1 y no 2: bastaba publicar el mapa.
- **🟠 La dimensión D pedía, con las mismas palabras, lo que T1(b) prohíbe.** D·Excelente: «dice qué
  habría que haber hecho en su lugar»; T1(b): «no qué habría que hacer en su lugar». Las dos son
  satisfacibles —la rúbrica mira el informe entero y T3(b) sí lo pide—, pero coinciden palabra por
  palabra en sentidos opuestos. Aclarado en el foco de D, sin tocar ninguna banda.
- **🟡 A·Excelente pide «nombrar el módulo» y solo T3(c) lo pide.** No es inalcanzable —los
  enunciados los nombran todos—, pero un informe que conteste exactamente lo pedido y no cite
  ninguno se queda en Aceptable, y son hasta 7 de 100. Dicho también en el foco de A.
- **La matriz dimensión × tarea:** A la alimentan 7 apartados, B 10, C 6, D 6 y E solo la bitácora.
  Ninguna dimensión queda huérfana —era lo que H4 temía—. **T2 es la única tarea que no toca D** y
  **T3 la única que no toca C**; cada tarea mueve entre 65 y 90 de los 100 puntos.
- **Los niveles se distinguen donde importa:** el salto Excelente↔Aceptable es decidible en las ocho
  dimensiones, siempre por un recuento o por la presencia de algo con nombre. El salto de abajo se
  apoya en un adverbio de grado en tres —A «predomina», C «implícito», E «razonable»—: ahí es donde
  dos lectores se separarían. **No lo he tocado: cambiar una banda publicada es decisión de Javier.**
- **Lo que A7 no pudo hacer:** el plan de auditoría pide «la concordancia entre calificadores
  medida, no estimada», y eso necesita un segundo lector humano (P2, sin contestar). Queda
  declarado como **no medido**.
- **Y el calificador tiene ya dónde anotar.** Daba las respuestas y ni una casilla: ahora cada hoja
  termina con **las dos rúbricas impresas** —requisitos de entrega primero, bandas publicadas,
  apartados que alimentan cada dimensión y los dos avisos de arriba—, con el hueco para escribir.

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
| ~~Reparto semana 6, entrega viernes 18~~ | **REVISADO (2026-09-09): entrega martes 6 de octubre, sustentación jueves 8** · **y otra vez (2026-09-11): entrega domingo 11 a las 13:00, sustentación martes 13** | Mueve el taller a la **semana 10** y le cambia el papel (§2.2). La construcción pasa de 2 días a **27**, y con ella se cae el riesgo que dominaba el §10 |
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
| 10 | 5 – 9 oct | capítulo 5 (cierra) · ~~entrega martes 6 · sustentación jueves 8~~ · **ENTREGA domingo 11, 13:00** |
| 11 | 12 – 16 oct | **SUSTENTACIÓN martes 13**, en clase · **Parcial 2** (fecha sin fijar) |

Tres consecuencias, y la tercera es una pregunta abierta que no puedo cerrar yo:

1. **El taller pasa a ser la preparación del parcial 2**, exactamente el papel que el Taller 1 tuvo
   para el parcial 1 (semana 4, parcial en la 5). La sustentación es el jueves 8 y el parcial 2 cae
   en la semana siguiente —**su fecha exacta no está fijada en ningún plan del repositorio**, solo
   «semana 11»—, así que el margen es de al menos cuatro días. Cabe, y el enunciado puede decirlo
   en cuanto la fecha se sepa.
   > **Actualización del 2026-09-11:** la sustentación pasa al martes 13, que ES la semana 11. El
   > margen de «al menos cuatro días» ya no existe — ver el final del §0.
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
- (b) Da **las dos cifras** de tu patrón: ~~el r donde g alcanza su máximo~~ **cuánto vale g en su
      máximo** (corregido en C5b: el r del máximo vale 0,005 en 23 de los 24 — ver §0) y el r donde
      g vuelve a 1, y el valor de K en ese segundo r. Con esas tres cifras, escribe la frase que el
      informe tendría que haber escrito.
- (c) Ahora sobre **tu localidad real**: K y g dicen lo mismo a todas las escalas. ¿Contradice eso
      lo que acabas de responder? (No: es λ inhomogénea, y eso es el módulo 2.)

> Medido en M-4: en el generado, g ya volvió a ~1 donde K sigue en 1,24–1,43. En el real, no.
> La tarea vale porque el estudiante tiene **los dos casos en la mano**.

### T4 · El borde y la banda · 8 % · mód. 4, 10, 11

Dos mitades, las dos de refutación.

- (a) **El borde.** ~~Se le da el sesgo de K sin corregir~~ **lo calcula él** (M-15: no está
      publicado), en **su** localidad y en una de forma opuesta (una compacta y una alargada).
      ~~¿En qué dirección empuja el sesgo, y por qué siempre en la misma?~~ **Eso es literalmente
      el ejercicio `e5` y se retiró en C5b — ver §0.** ¿Cuál de las dos sufre más, y por qué el
      cociente perímetro/área lo predice?
- (b) **La banda.** Se le dan **dos** envolventes del mismo patrón con las mismas simulaciones: la
      completa, y una con el rango de r **recortado después de mirar la curva**. Di qué está mal y
      por qué el p-valor de la segunda no es un p-valor. **Y cuenta los nodos fuera de banda en
      todo el rango, y dice por qué el recuento tampoco decide** (M-16: el test global no lo puede
      correr, porque el patrón de la envolvente no se publica — ver §0).
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
> **Con la entrega del domingo 11 (2026-09-11)** el capítulo 5 ya está cerrado al entregar: la
> restricción deja de ser necesaria, y no se toca — ver el final del §0.

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

**4.1 · Estructura fija, publicada en el enunciado. Una sola sesión, el martes 13 de octubre**
(decidida el 2026-09-09; fecha fijada el mismo día y movida el 2026-09-11: presencial, en el espacio de la clase).

Los **dos días** entre la entrega (martes 6) y la sustentación (jueves 8) —**día y medio** desde el
2026-09-11: del domingo 11 a las 13:00 al martes 13— no son holgura: son lo
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
3. **su localidad de contraste** para T4(a) — de forma opuesta a la suya: al menos el **doble** de
   perímetro/área, o la mitad, **rotando** entre las que lo cumplen (M-20; hasta el 2026-09-10 era
   siempre «la más opuesta», y eso daba dos contrastes para toda la clase);
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
oct), cada estudiante enseña unas pocas cifras de su variante y nada más. Cinco minutos para los
doce, quince contando las preguntas.

> ⚠️ **CORREGIDO AL CONSTRUIR C10b (2026-09-10): NO son tres cifras, son cinco.** Este párrafo
> decía «su localidad, su n y su λ», y esas tres **no identifican una variante**: n y λ son
> *función* de la localidad, así que las tres llevan un solo dato. Medido sobre **200 000 sorteos**
> de doce documentos: **el 99,66 % de las listas deja a dos estudiantes indistinguibles**. El
> control habría dado verde a dos que hubieran intercambiado documentos dentro de la misma
> localidad — que es exactamente el fallo que existe para cazar. Y la localidad de contraste
> tampoco ayudaba: había **una sola por localidad** (M-20; desde que se cerró sí distingue
> —67,31 %—, pero con las cinco de abajo no hace falta). Añadiendo el **patrón** y el **trío** la
> cifra baja a **0,00 %** en 100 000 sorteos. Por eso se leen **cinco**: localidad, n, λ, patrón y
> trío. Lo emite `verifica_taller2.R --control`.

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
        perímetro/área por un factor declarado — **el factor es 2** (M-20), y el generador comprueba
        pareja a pareja que el déficit a r = 1 km ordena igual
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
> que ABRE Y FUNCIONA. LAS DOS ESTÁN HECHAS**: C5a el 2026-09-09 —esqueleto, cabecera y pie, CSS
> propio, buscador del §5.2, T1 y T2— y C5b el 2026-09-10 —T3, T4, T5 y las dos rúbricas—. Ver el
> §0, que trae los **cinco** defectos que la construcción encontró (**M-13** la caja de T1,
> **M-14** `Fest()`, **M-15** el sesgo que no viaja, **M-16** el test global que no se puede correr
> y **M-17** la rejilla de los focos), el duplicado con el ejercicio `e5` y la fuga de
> `datos_taller2.R`. **Queda C6**, que va dentro del módulo 7 que ya existe.
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
> **HECHA (2026-09-10).** Las 36 y las 12 viven en `ensambla_taller2.py` y se publican en el
> módulo 7; la lista legible desde fuera es `precalculo/salidas/taller2_banco.md`. El ensamblador
> imprime la cobertura y para si el reparto no cuadra. Ver el §0: releer las doce afirmaciones
> falsas tumbó seis, y una de ellas **no era falsa**.
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
> **HECHA (2026-09-10).** 84 comprobaciones · 0 fallos, y 20 inyecciones nuevas en
> `prueba_texto.py`, 20 cazadas. Ver el §0: el tope propio y su aritmética, y el hallazgo de que
> `formulas_escapadas()` pasaba por vacuidad en tres documentos publicados.
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
> **HECHA (2026-09-10).** Ver el §0.
- [x] los tres anchos · el buscador con cinco documentos distintos · las curvas con tinta ·
      el dato descargable se abre

**C9 · Integración en el repositorio** — **Tamaño: S**
> **HECHA (2026-09-10).** `audita_todo.sh --rapido` en **ARNÉS COMPLETO EN VERDE**, y nombra el
> taller 2 en cinco sitios sin haberlo tocado. Ver el §0, incluida la advertencia sobre lo que
> significa fusionar la rama.
- [ ] `audita_todo.sh --rapido` **nombra el taller 2 en su salida** (no se edita: lo descubre por
      los nombres del §7; si no aparece, el nombre está mal) · `cuenta_sitio.py` en verde ·
      `index.html` con la tarjeta nueva, junto a la del Taller 1 · `README.md` actualizado ·
      `.gitignore`: `!/PLAN_Taller_2_Cap_4.md`, `!/entrega/datos/taller2_*.gpkg`, y
      **`genera_taller2.R` y `verifica_taller2.R` ignorados**
- [ ] `git check-ignore` confirma los dos que NO deben viajar

**C10 · El calificador** — `precalculo/verifica_taller2.R` — **Tamaño: M** — **HECHA (2026-09-10)**
- [x] recalcula las cifras esperadas de **un** documento · `--lista curso.txt` para los 12 ·
      **para** si la portada no cuadra con la lista (§5.2) · **no entra en el arnés**, porque
      imprime las respuestas y el arnés deja registro
- [x] 1 321 líneas · 143 anclas en el arranque · 55 cifras por hoja · probado sobre 36 documentos
      que cubren las 16 localidades, los 12 tríos, las 12 envolventes y todos los contrastes
- [x] el §5.2 comprobado con el caso real del Taller 1 —el que tecleó 102 en vez de 480—: para
      antes de imprimir una sola cifra y dice cuál es cuál
- [x] `--json` se niega a escribir en una ruta que git no ignore, y lo comprueba **antes** de
      crear el directorio
- [x] deduce las familias en vez de recordarlas, y lee `ORDEN_MAPAS_T2` del HTML publicado en vez
      de copiarlo
- **Encontró dos cosas que no estaban:** **M-18** (el pico/media de T5 sale de `dimyx = 80` y el
  enunciado pide `dimyx = 256`) y **M-19** (la clave de T1(c) es k = 2 en nueve de las dieciséis y
  no existe en tres). Las dos en el §0.

**C10b · El control de la semana 9** — en clase, entre el 28 de septiembre y el 2 de octubre — **Tamaño: S**
- **Descripción:** los doce leen en voz alta ~~su localidad, su n y su λ~~ **su localidad, su n, su
  λ, su patrón y su trío** (§5.3, corregido). No se califica.
- **EL INSTRUMENTO ESTÁ HECHO (2026-09-10)**, que es lo único de C10b que se puede construir antes
  de repartir: `precalculo/rscript.sh precalculo/verifica_taller2.R --control curso.txt > control.txt`
  - [x] una fila por estudiante con las cinco cosas y una casilla `[ ]` que marcar
  - [x] debajo, la **línea completa de la portada** de cada uno, para cotejarla carácter a carácter
        cuando una fila no cuadre (§5.2)
  - [x] **avisa de las colisiones** —dos con la misma variante— antes de entrar al aula, porque a
        esos dos el control no los puede distinguir
  - [x] **no lleva ni una respuesta, y lo comprueba antes de imprimir**: la hoja se genera en
        memoria, se busca en ella «agregado», «aleatorio», «regular», «familia», «régimen»,
        «thomas», «chi2» y «p-valor», y **para** si aparece alguna. Probado inyectando una.
  - [x] el arranque escribe por `message()` (stderr), así que el `>` deja en el archivo la hoja
        y nada más
- **Criterios de aceptación, para el día** (28 sep – 2 oct):
  - [ ] los doce cotejados contra la lista del curso **en el aula**
  - [ ] quien tenga una discrepancia se corrige **ahí**, con 4 días aún por delante
- **Dependencias:** el taller repartido · **Tamaño: S**

**C11 · La lectura de los doce escritos** — entre el 11 y el 13 de octubre — **Tamaño: M**
- **Descripción:** leer las doce entregas y elegir, para cada estudiante, **la decisión que va a
  defender** en el bloque de 2 min. Es lo que los dos días de margen compran.
- **EL INSTRUMENTO ESTÁ HECHO (2026-09-10)**, que es lo construible antes de la entrega:
  `precalculo/rscript.sh precalculo/verifica_taller2.R --sustentacion curso.txt > sorteo.txt`
  - [x] **el sorteo sin reemplazo hecho y registrado**, que es lo que el §4.5 pide con fecha: 36
        extracciones, 36 preguntas distintas, el banco agotado exactamente, y **para** si alguna
        de esas tres cosas no se cumple
  - [x] **una afirmación falsa distinta por estudiante**, del catálogo de 12
  - [x] **reproducible sin acordarse de nada**: la semilla sale del contenido de la lista, se
        imprime en la hoja, y `--semilla N` la fuerza para volver a sortear a propósito.
        Comprobado: la misma lista da un sorteo idéntico byte a byte, y `--semilla` otro distinto
  - [x] el banco **no se copia**: se lee de `salidas/taller2_banco.md`, que escribe el ensamblador,
        y se **coteja contra el HTML publicado** — si uno de los dos está rancio, para. Probado
        quitándole una pregunta al `.md`
  - [x] por estudiante, la casilla de **portada cotejada** (§5.2) y **bitácora leída** (§6), y las
        seis decisiones candidatas que su variante le obligó a tomar, con un hueco para la elegida
        y otro para la razón. **La elección la hace Javier habiendo leído el escrito**: eso no lo
        puede hacer una herramienta y no lo intenta
- **⚠️ EL §4.5 SUPONE EXACTAMENTE DOCE, y el guion lo hace explícito.** 36 = 12 × 3. Con once
  estudiantes sobran tres preguntas y con trece faltan tres, y en los dos casos el sorteo sin
  reemplazo deja de cuadrar. El guion **para** con la aritmética delante en vez de sortear con
  repetición en silencio. Si el curso cambia de tamaño hay que decidir —sobran y no pasa nada, o
  faltan y hay que escribir tres preguntas más— y decidirlo **antes** del martes 13.
- **Criterios de aceptación, para los días** (11 – 13 de octubre):
  - [ ] una decisión elegida y anotada por estudiante, con la razón
  - [ ] **la bitácora de cada uno leída** (§6): es lo que se contrasta en la sustentación
  - [ ] comprobado que la portada de cada uno cuadra con su documento (§5.2): quien resolvió una
        variante ajena se detecta **aquí**, antes de la sustentación, no al calificar
  - [x] el sorteo sin reemplazo del banco (§4.5) hecho y registrado **antes** del jueves
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
| 21 sep – 11 oct | *(el estudiante trabaja)* · **C10** | El calificador se escribe mientras, sin prisa |
| **28 sep – 2 oct** | **C10b · control de la semana 9** | Cinco cosas por estudiante en clase (§5.3). Atrapa la variante ajena con nueve días de margen |
| **dom 11 oct, 13:00** | **Entrega** | Movida el 2026-09-11 desde el martes 6 |
| 11 – 13 oct | **C11** · lectura de los doce escritos | Día y medio útil: la tarde del domingo y el lunes |
| **mar 13 oct** | **Sustentación** | Presencial, en el espacio de la clase. Una sesión, 7 min por estudiante (§4.1) |

**Lo que el calendario nuevo NO cambia:** C3 y C4 siguen teniendo que ir en paralelo con C5. Tener
doce días en vez de dos hace que quepan cómodamente; no hace que puedan ir después.

---

## 10. Riesgos

| Riesgo | Impacto | Mitigación |
|---|---|---|
| **Regenerar el precálculo después de repartir** | **Alto** | Reasigna las 1000 variantes. Una vez publicado, `genera_taller2.R` no se vuelve a ejecutar; el enunciado se corrige por el ensamblador. Es la lección del Taller 1 |
| **El JSON publicado filtra la familia del patrón** | **Alto** | Guarda explícita en C1 y comprobación doble en C3, también contra el JSON ya incrustado en el HTML |
| ~~La defensa al 60 % no cabe en una sesión~~ **RESUELTO (2026-09-09)** | — | **Una sesión, 7 min por estudiante**: 12 × 8 = 96 min sobre los 120 de la sesión (§4.1). Lo que queda vivo es la comprobación de que la sesión es de 2 h y no de 1,5 —**y desde el 2026-09-11 es concreta: la clase del martes 13**— si es de 1,5, la refutación pasa al escrito |
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
