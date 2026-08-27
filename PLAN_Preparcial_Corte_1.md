# Plan · Preparcial del Corte I

Estadística Espacial 2026-II (20929) · Universidad El Bosque

Instrumento **formativo, sin nota y repetible** con el que el estudiante comprueba, antes del
parcial, si tiene el Corte I: procedimientos, conceptos, interpretación y lectura de gráficos y
mapas. No es un taller —no se califica, no se individualiza— y no es un capítulo —no enseña
contenido nuevo—. Es una tercera cosa, y por eso se lleva su propio cubo en el recuento y su propio
bucle en el arnés.

**Estado:** 🟢 **El auditor ya existe y el preparcial pasa sus 112 comprobaciones.**
Lo siguiente es **P3.0, la auditoría de contenido** —la única que ninguna herramienta puede hacer,
porque todo el arnés comprueba la forma y no la verdad—; después **P1.3** (el arnés de inyección),
**P2.4** (los ejercicios guiados) y el resto de la fase 3. El parcial es el 1 de septiembre. El
historial, en orden:

**P0.1 y P1.1 (2026-08-25).**
`alcance_preparcial1.py` (30 módulos leídos del HTML publicado, 6 anclas de numeración) con su arnés
en **8/8**, y `genera_preparcial1.R` → `preparcial1_datos.json`, **29,2 KB**: **119 cifras
reutilizadas sobre los 30 módulos**, 4 cálculos nuevos con distractores calculados, 6 series de
gráfico, 10 errores catalogados y **14 anclas** que paran el guion. Reproducible byte a byte. Cinco
guardas verificadas por inyección.
· **Dos hallazgos que cambian contenido del preparcial**, no solo código: `st_distance` sobre
EPSG:4326 **no mide sobre el elipsoide** —usa s2, sobre una esfera— y esa es la columna «esfera»
del capítulo 2; y los capítulos 2 y 3 **publican tildes rotas**. Ver §12.
✅ **P2.1 hecha (2026-08-25).** `ensambla_preparcial1.py` → `Htmls_Espacial/preparcial-corte-1.html`,
**276 KB**: el esqueleto, el módulo del alcance —los 30 módulos nombrados uno a uno, con enlace, y los
3 que quedan fuera dichos por su nombre— y el catálogo de los **10 errores** con su cifra medida.
Consola limpia, sin desbordamiento a 1 280, 375 ni 318, `sin_aritmetica` y `campos_vivos` en verde.
· **Media P3.2 adelantada** por un motivo de fuera del plan: la sesión que arregla las tildes iba a
encontrarse `cuenta_sitio.py` en rojo por mi archivo sin clasificar. Cubo de preparciales y enlace
desde la portada, hechos. El bucle de `audita_todo.sh` y el README siguen pendientes.
✅ **P2.2 hecha (2026-08-25).** **22 preguntas** —11 del capítulo 1 y 11 del capítulo 2, una por
módulo—, de los cuatro tipos y con retroalimentación en las 72 opciones. El documento va por **319
KB** y **22 de los 30 módulos** ya tienen pregunta propia. Verificado respondiendo los dos bloques
enteros en el navegador: consola limpia, los dos lienzos con tinta y con `aria-label`, y el resumen
del bloque A mandando a **«Cap. 1 · módulo 1 — El mapa que cambió la epidemiología»** con el enlace
puesto.
· **Media P0.2 adelantada, porque P2.2 no podía esquivarla.** Ver §12.3.
· **La familia de sincronía se estrenó sola, y cazó algo el mismo día.** Ver §12.4.
✅ **P2.3 hecha (2026-08-26).** El bloque C (8 preguntas, cap. 3 m1–m8), los **seis
procedimientos con salida ejecutada** y el bloque D (6 preguntas que cruzan capítulos). El documento
va por **373 KB** y **7 módulos**, con **36 preguntas** que cubren **30 de los 30 módulos** del
alcance: 16 `opcion`, 7 `multiple`, 7 `numerica` y 6 `grafico`. `verifica_bloques.py` ejecuta los
doce bloques y cuadra **71 de 71** cifras anunciadas; encadenado con los cuatro capítulos y el
taller, **461 de 461**. Ninguno marcado `arranque`.
· Cinco cosas aparecieron escribiéndolo. Una cambia lo que una pregunta afirma —la curva del
efecto escala cruza la línea del valor individual y la primera versión decía que no—, y otra es un
defecto de la plantilla que se midió aquí y queda levantado. Ver §12.5.
✅ **P1.2 hecha (2026-08-26).** `audita_preparcial1.py`, con el intérprete de `geo_env`:
**112 comprobaciones, 0 fallos, 0 saltadas**, repartidas en las cinco familias y con el recuento
por familia impreso. Recalcula las cuatro cifras nuevas **desde la fuente primaria** —el CSV de
municipios, el GeoPackage de las 361 estaciones, el de condados— y **con pyproj y mapclassify en
vez de lwgeom, s2 y classInt**; vuelve a resolver las **119 rutas** contra `capN_datos.json`; y lee
las **36 preguntas del HTML publicado** con un analizador propio, porque los enunciados no están en
el JSON. Probado envenenando `cap3_datos.json`: la familia 2 se pone en rojo y nombra la ruta, la
cifra del capítulo y la del preparcial.
· **Y encontró dos cosas de contenido el mismo día.** La grave: **la respuesta correcta caía la
primera en las 29 preguntas con opciones**, así que el preparcial se aprobaba marcando siempre la
(a). Ver §12.6.
✅ **P3.0 hecha (2026-08-26), revisada y aprobada por Javier.** La auditoría de contenido, en
**seis pasadas**: los cuatro bloques, los seis procedimientos y los dos módulos que enmarcan.
**36 de 36 preguntas contestadas a ciegas**, 6 de 6 gráficos contrastados contra su serie, 116 de
116 retroalimentaciones y los 29 comentarios de código leídos. **32 hallazgos, los 32 aplicados**
—también los del cubo D, por decisión de Javier—, y **cinco de ellos bloqueaban repartir con todo el
arnés en verde**. El informe es `AUDITORIA_CONTENIDO_P30.md`.
· **Lo que el arnés no podía ver, y ahora está escrito como método:** seis vías de defecto, cada una
cazada por una comprobación distinta y ninguna sustituible por otra. Ver §12.7.
· El precálculo pasó de **119 a 126 cifras reutilizadas**; el ensamblador ganó **una guarda nueva**,
probada por inyección. Cadena entera en verde: 112/112 del auditor, 71/71 cifras `#>`, **461/461**
encadenado con los cuatro capítulos y el taller.
✅ **P1.3 hecha (2026-08-26).** `prueba_auditor_preparcial1.py`, 615 líneas: **87 inyecciones,
87 cazadas**, sobre las tres superficies que el auditor lee —el JSON (56), el HTML publicado (23) y
los tres capítulos (8)—. Y no se conforma con «87 de 87»: **95 de 95 tipos de comprobación se han
visto fallar**, y los tres que no están en listas separadas con su motivo. **Checkpoint 1 cerrado.**
· **Salió en rojo cuatro veces, y las cuatro por defectos del arnés**, no del auditor. La peor: el
reordenador de opciones producía JavaScript roto y **el auditor moría al analizar** — código de
salida ≠ 0, así que el arnés lo contaba como cazado. De ahí nace `revento()`. Ver §6.
Siguiente: **P2.4** (los seis ejercicios guiados), que es lo que queda de la fase 2.

---

## 0. Cómo retomar esto en otra sesión

**Cómo arrancar la conversación nueva:** abrirla en esta misma carpeta
(`Bosque 2026/Estadistica espacial/`) y pedir que lea **este archivo** antes de tocar nada. Todo lo
que sigue está pensado para que no haga falta reconstruir nada de memoria.

### 0.1 · Estado al 2026-08-26, por la tarde

**El parcial es el martes 1 de septiembre de 2026.** Este estado se escribió el **miércoles 26**,
con seis días por delante; el preparcial tiene que estar repartido antes, realistamente el **viernes
28** o el **sábado 29**. Antes de nada, mirar qué día es hoy: si esto se lee el domingo 30, el §9
—la ruta corta— deja de ser una opción y pasa a ser el plan.

| Tarea | Estado |
|---|---|
| P0.1 · el alcance verificable | ✅ hecha, arnés 8/8 |
| P0.2 · el motor | 🟡 **mitad hecha**: el resumen ya sabe apuntar a otro documento y está retropropagado a los cinco documentos. Falta el **enlace profundo** (`#mN`) |
| P1.1 · `genera_preparcial1.R` | ✅ hecha, 14 anclas, reproducible |
| P1.2 · `audita_preparcial1.py` | ✅ hecha, 112 comprobaciones en 5 familias, 0 fallos |
| P1.3 · arnés de inyección del auditor | ✅ **hecha (2026-08-26)**: 87 inyecciones, 87 cazadas, **95 de 95 tipos vistos fallar** |
| P2.1 · esqueleto y los dos módulos marco | ✅ hecha |
| P2.2 · bloques A y B, 22 preguntas | ✅ hecha |
| P2.3 · bloque C, procedimientos y bloque D | ✅ hecha, 36 preguntas, 30/30 módulos, 71/71 cifras `#>` |
| P2.4 · los seis ejercicios guiados | ⛔ **no empezada — es la que queda de la fase 2** |
| P3.0 · **auditoría de contenido** | ✅ **hecha (2026-08-26)**, revisada y aprobada por Javier. 32 hallazgos, los 32 aplicados. Informe en `AUDITORIA_CONTENIDO_P30.md` |
| P3.1 · `audita_texto_preparcial1.py` | ⛔ no empezada. Ver §12.4: hay una clase de defecto que hoy solo caza leer |
| P3.2 · cubo, bucle, lista blanca, portada | ✅ **hecha (2026-08-26, noche)**: los 5 criterios. El bucle descubre solo —probado con un preparcial 2 falso: 19 → 22 pasos— y el README está al día |
| P3.3 · verificación y cierre | ✅ **hecha (2026-08-26, noche)**: los 6 criterios en verde y 1 hallazgo aplicado. El sello llegó con P3.2: `ARNÉS COMPLETO EN VERDE`, 19 pasos, 0 rojos |

**Lo publicado ahora mismo:** `Htmls_Espacial/preparcial-corte-1.html`, **379,1 KiB**, **7 módulos**,
**36 preguntas** que cubren **los 30 módulos** del alcance, y **6 pares R/Python** verificados
ejecutándolos. Lo que falta para cerrar la fase 2 son los seis ejercicios guiados (P2.4), que entran
entre el bloque D y el catálogo de errores y renumeran solos el módulo de cierre del 7 al 8.

**Y esto es lo primero que hay que mirar al abrir una sesión nueva: NADA DE ESTO ESTÁ COMITEADO.**
`git status` enseña seis cosas, y conviene saber qué es cada una antes de tocarlas:

| | Qué es |
|---|---|
| `M Htmls_Espacial/preparcial-corte-1.html` | el documento publicado, con los 32 arreglos de P3.0 dentro |
| `M precalculo/ensambla_preparcial1.py` | los arreglos de P3.0 y **una guarda de salida nueva** (el nombre del catálogo atado a `len(ERRORES)`) |
| `M precalculo/genera_preparcial1.R` | 7 claves reutilizadas nuevas y 5 campos `que` corregidos |
| `M precalculo/salidas/preparcial1_datos.json` | el precálculo regenerado: **126 cifras**, eran 119 |
| `M PLAN_Preparcial_Corte_1.md` | este archivo |
| `?? precalculo/prueba_auditor_preparcial1.py` | **el arnés de P1.3, sin rastrear** |

Y **`AUDITORIA_CONTENIDO_P30.md` no aparece en `git status`**: la lista blanca de la raíz lo atrapa
(`.gitignore:8:/*`). Para versionarlo hace falta un `!/AUDITORIA_CONTENIDO_P30.md`, como el que ya
tiene este plan en la línea 126. **Es una decisión de Javier, no del guion, y sigue sin tomarse.**

### 0.2 · Lo primero que hay que saber, antes de tocar nada

1. **R se invoca SIEMPRE con el envoltorio.** `precalculo/rscript.sh`, nunca `Rscript` a pelo: el
   del PATH es el de Homebrew y no tiene `sf`, y arranca en `LC_CTYPE=C`, donde `jsonlite` escribe
   las tildes rotas **sin fallar**.
2. **Los módulos del preparcial se numeran solos.** No hay números escritos: `CONSTRUCTORES`, al
   final de `ensambla_preparcial1.py`, es una lista ordenada y de la posición salen el número, la
   cabecera y la entrada de navegación. Los siete de hoy salieron así, y los ejercicios guiados de
   P2.4 entran insertando `mod_ejercicios` entre `mod_bloque_d` y `mod_errores`: el módulo de cierre
   pasa solo del 7 al 8 y **no hay que renumerar nada**. El motor exige que la navegación
   declare exactamente los módulos que existen, del 1 al N sin huecos: un botón que abre un
   `template` inexistente deja el panel en blanco **sin un solo error en consola**.
3. **Ninguna cifra a mano, y hay una segunda regla propia:** una cifra reutilizada de un capítulo no
   se copia, se **referencia**. Cada entrada de `reutilizado` guarda archivo y ruta de origen. Si se
   regenera cualquier capítulo, **hay que volver a correr el generador y el ensamblador del
   preparcial**, porque las cifras pueden haberse movido — ya pasó el mismo día, ver §12.4.
4. **Las glosas verbales son cifras a mano.** «Un 7 % más», «tres veces mejor», «Son 140 KB»: no
   pasan por ningún formateador, así que `sin_aritmetica.py` no las ve y envejecen mal. Se cazaron
   diecisiete escribiendo P2.2, dos más escribiendo P2.3 y **una quincena más en P3.0**. Al
   redactar cualquier cosa nueva, **no reformular una cifra en palabras**: o se cita por su clave, o
   no se dice. **Y la regla tiene dos mitades:** cuando la primera no se puede —el rótulo de un
   lienzo vive dentro de JavaScript y un bloque de código no se interpola, regla 6— la que queda es
   la segunda, quitar el número. Y cuando citarla empeora el texto —«Los **10** errores que se
   repiten» es peor que «los diez», porque el título es un nombre y no un recuento— se mecaniza por
   fuera: hay una guarda en el ensamblador que ata el nombre a `len(ERRORES)`.
5. **Las opciones se barajan solas, y por eso ninguna retroalimentación puede nombrar una
   posición.** El ensamblador reordena las opciones de cada pregunta con una semilla derivada del
   JSON y de la identidad de la pregunta —reproducible byte a byte—, porque escritas de una en una
   las 29 tenían la correcta la primera y el preparcial se aprobaba marcando siempre la (a) (§12.6).
   Consecuencia al redactar: «las correctas son las dos primeras» es falso y **se lee bien**, que es
   lo peligroso. Lo rechazan `POSICIONALES` en el ensamblador y la familia 5 del auditor.
6. **Un bloque de código no se interpola, se concatena.** El intérprete del proyecto es Python
   3.10, y una f-string no admite una barra invertida dentro de su expresión: `tabs(...)` con un
   `\n` dentro va como `""" + tabs(...) + f"""`, igual que en `ensambla_cap1.py`. El error que da
   Python señala la línea 53 y no se parece en nada a la causa.
7. **El auditor no arranca con `python3` a secas.** Necesita geopandas, pyproj y mapclassify: el
   intérprete es el de `geo_env`, y su ruta está en `precalculo/versiones_py.json`.
8. **El plan ya se versiona** (`!/PLAN_Preparcial_Corte_1.md` en el `.gitignore`, línea 126). Nada
   de esto está comiteado todavía: la decisión del commit es de Javier. `AUDITORIA_CONTENIDO_P30.md`
   **sigue fuera** de la lista blanca, y también es decisión suya.
9. **El campo `que` de una cifra reutilizada NO es documentación interna: se publica.** El comentario
   del generador lo llama «lo que el redactor de la pregunta lee para no volver al capítulo», y el
   catálogo de errores del módulo 7 lo imprime literal —cada `<li>` es `cifra(clave) — que(clave)`—.
   Cinco de esos campos tenían defectos y ninguna pasada sobre preguntas podía verlos. **Y el nombre
   de la ruta no describe lo que mide:** `m2.r_conteo_tasa` correlaciona el conteo con el *puntaje
   medio*, no con una tasa, y escribir el `que` leyendo el nombre publicó esa confusión (P3.0, A-4).
10. **El `descripcionGrafico` es contenido, no metadato.** Es el `aria-label` del lienzo y la **única**
   descripción que recibe quien usa lector de pantalla. Un rótulo que existe y no está vacío cuenta
   como accesible para el arnés, y **ninguna comprobación mira si dice la verdad ni si basta para
   contestar la pregunta**. Las dos cosas hay que preguntárselas a mano: uno decía que Mercator
   destruye el área más que ninguna —y es la tercera de seis— y otro describía la estructura de un
   gráfico de barras sin una sola magnitud, con una pista que mandaba a comparar barras (P3.0).
11. **El arnés de P1.3 falla del revés que un auditor.** Si `prueba_auditor_preparcial1.py` se pone en
   rojo, la primera hipótesis es que el defecto está **en la inyección**, no en el auditor: salió en
   rojo cuatro veces y las cuatro fue así. La regla: **cambiar el archivo no es mover la
   comprobación** — una inyección puede no ser «inerte» y seguir sin probar nada.

### 0.3 · La cadena, en orden

```
precalculo/rscript.sh precalculo/genera_preparcial1.R    # el precálculo (segundos)
python3 precalculo/ensambla_preparcial1.py               # el HTML
python3 precalculo/alcance_preparcial1.py                # los 30 módulos, para mirarlos
python3 precalculo/prueba_alcance_preparcial1.py         # el arnés del alcance (8/8)
python3 precalculo/verifica_bloques.py --html Htmls_Espacial/preparcial-corte-1.html
<geo_env>/python precalculo/audita_preparcial1.py        # el auditor independiente (112/112)
python3 precalculo/sin_aritmetica.py                     # ninguna cifra de la prosa fuera de R
python3 precalculo/campos_vivos.py                       # el contrato dato ↔ quien lo pinta
python3 precalculo/cuenta_sitio.py                       # los totales y el enlace de portada
```

Y **aparte, porque tarda minutos y no es para cada cambio** —son 89 invocaciones del auditor,
cada una releyendo los GeoPackage—:

```
python3 precalculo/prueba_auditor_preparcial1.py         # el arnés de inyección (87/87)
python3 precalculo/verifica_bloques.py --todos           # los 461 bloques del sitio entero
```

El segundo hay que correrlo **siempre que se toque un bloque de código del preparcial**: los bloques
de R del sitio se ejecutan en una sola sesión y el estado de `sf_use_s2()` es global (§12.5).

**`audita_todo.sh` ya conoce el preparcial** (P3.2, 2026-08-26): tercer bucle propio, que corre el
auditor, el arnés del alcance —también con `--rapido`, cuesta 0,06 s— y, cuando exista, el de la
prosa. Así que para dar algo por cerrado basta con:

```
precalculo/audita_todo.sh --rapido    # 19 pasos, segundos
precalculo/audita_todo.sh             # + los arneses de inyección, minutos
```

La lista de nueve órdenes de arriba sigue sirviendo para trabajar —es más rápida y dice más de cada
paso—, pero ya no es la única forma de pasar el arnés entero. El intérprete de `geo_env` sale de
`precalculo/versiones_py.json`; `python3` a secas no tiene geopandas ni pyproj y el auditor no
arranca.

### 0.4 · Qué hacer a continuación, y en qué orden

✅ **P3.0 ya está hecha, revisada y aprobada (2026-08-26).** Se puso por delante de P1.3 a
propósito —«una clave equivocada llega a los estudiantes; un auditor sin probar, no»— y la decisión
se pagó sola: **cinco defectos bloqueaban repartir y los cinco pasaban las 112 comprobaciones del
auditor**. El informe es `AUDITORIA_CONTENIDO_P30.md` y las seis vías por las que se cazaron están en
**§12.7**, que es lo que hay que leer antes de auditar cualquier cosa nueva de este documento.

✅ **P1.3 hecha (2026-08-26), y con ella el Checkpoint 1.**
`prueba_auditor_preparcial1.py`: **87 inyecciones, 87 cazadas**, y **95 de 95 tipos de comprobación
vistos fallar**. El detalle está en el §6; lo que conviene saber antes de tocarlo:

- **Envenena tres superficies**, y hacen falta las tres: el JSON (56 inyecciones), el HTML publicado
  con las 36 preguntas (23) y los tres `capN_datos.json` (8). Las familias 3, 4 y 5 solo se rompen
  tocando el HTML —las preguntas no están en el JSON—, y la 2 solo se rompe **de verdad** moviendo
  un capítulo debajo, que es la forma que el defecto tiene en la realidad (§12.4).
- **Tarda unos minutos.** Son 89 invocaciones del auditor, cada una releyendo los GeoPackage. No es
  para la cadena rápida.
- **Salió en rojo cuatro veces y las cuatro fueron culpa del arnés**, no del auditor. Si se vuelve a
  poner en rojo, la primera hipótesis es ésa. La regla que resume las cuatro: **cambiar el archivo
  no es mover la comprobación** — una inyección puede no ser «inerte» y seguir sin probar nada.

**Y P2.4**, los seis ejercicios guiados, que es lo que queda de la fase 2. El andamiaje está
montado: se inserta `mod_ejercicios` en `CONSTRUCTORES` entre `mod_bloque_d` y `mod_errores` y la
numeración sale sola. **Sus ejercicios pasan por el protocolo de P3.0 igual que las preguntas**: no
se audita ahora lo que aún no existe, pero tampoco nace fuera de la auditoría.

Si la fecha aprieta, el §9 dice qué se suelta y qué cuesta cada recorte. Lo que **no** se suelta:
la cobertura de los 30 módulos, la retroalimentación por opción, la familia de sincronía y el enlace
desde la portada.

### 0.5 · Qué falta para repartir, en orden de urgencia

**Quedan seis días y el preparcial ya se puede repartir tal como está.** Conviene decirlo así de
claro, porque las cuatro tareas que faltan **no son todas iguales de urgentes** y el §9 —la ruta
corta— existe justo para no confundirlas:

| | Qué es | ¿Bloquea repartir? |
|---|---|---|
| **La lectura de Javier** | los cuatro bloques enteros, como los lee un estudiante | **Sí.** Es la mitad del Checkpoint 2 que P3.0 no puede sustituir |
| ~~**P3.2** · el bucle y el README~~ | ✅ hecha: `audita_todo.sh` ya conoce el preparcial | **Ya no** |
| **P2.4** · los 6 ejercicios guiados | la dimensión de *producir*, no solo reconocer | No. El §9 lo da por soltable |
| **P3.1** · `audita_texto_preparcial1.py` | mecaniza las cifras de la prosa | No. Protege el **futuro**, no este reparto |
| ~~**P3.3** · navegador y cierre~~ | ✅ hecha salvo el sello, que es de P3.2 | **Ya no**, salvo por el sello |

**Checkpoint 2 · el preparcial completo.** Las 36 preguntas y los 30 de 30 módulos están, y **P3.0
está hecha y aprobada**: el contenido queda auditado afirmación por afirmación. Falta **P2.4** —y sus
ejercicios pasan por el protocolo del §8 con las seis vías del §12.7 delante— y falta **la lectura de
Javier**: el ritmo no lo caza nada de lo que hay montado, y ahora que las opciones van barajadas
conviene mirar si alguna pregunta quedó rara al reordenarse.

**Checkpoint 3 · listo para repartir.** Arnés completo en verde, enlazado desde la portada, leído
entero, y la pregunta de cierre: **¿qué quedó dicho y no mostrado?**

**Si la fecha aprieta**, el orden que yo seguiría es: **P3.3** (media hora, y caza cosas que solo se
ven en el navegador) → **la lectura de Javier** → **P3.2** (el bucle) → y P2.4 y P3.1 después del
parcial, si es que llegan.

---

## 0.6 · Las cuatro decisiones que ya están tomadas

Contestadas por Javier el 2026-08-25, antes de escribir esto:

| # | Decisión | Elegido | Lo que descarta |
|---|---|---|---|
| D1 | **Alcance** | Capítulos 1 y 2 completos + capítulo 3 **módulos 1–8** (hasta «MAUP I · efecto escala») | Zonificación, falacia ecológica y ética (cap. 3, m9–m11) quedan **fuera** y el material tiene que decirlo |
| D2 | **Ubicación** | Página propia `Htmls_Espacial/preparcial-corte-1.html` | No se inserta como módulo 9 del cap. 3: eso renumeraba m9→m10…m12→m13, rompía el molde de 12 y obligaba a re-auditar el capítulo entero para alojar algo que evalúa **tres** capítulos |
| D3 | **Carácter** | Formativo, repetible, con retroalimentación por opción | Sin variantes por estudiante, sin `verifica_*.R`, sin cronómetro. La maquinaria de 1000 variantes del Taller 1 existe para la anticopia, que aquí no aplica |
| D4 | **Brightspace** | Solo el HTML por ahora | El banco QTI queda para después; sale de estas mismas preguntas sin volver a redactarlas, con la retroalimentación por opción ya escrita |

**Sobre D1, y es lo primero que hay que escribir bien.** Tu frase fue «las unidades I, II y la unidad
III hasta el módulo 8». La traducción al material es: unidad I = capítulo 1, unidad II = capítulo 2,
unidad III = capítulo 3. El corte en el módulo 8 cae en un sitio limpio —«MAUP I · efecto escala»
cierra la parte medible del MAUP y lo que sigue es zonificación y sus consecuencias—, pero **un
estudiante no puede adivinar dónde está la frontera**. El módulo 1 del preparcial la dibuja
explícitamente: los 30 módulos que entran, y los tres del capítulo 3 que no.

---

## 1. Lo que hay que saber antes de tocar nada

1. **La regla que gobierna el repositorio también rige aquí: ninguna cifra a mano.** Toda cifra de
   un enunciado, de una opción o de una retroalimentación la calcula R y viaja en un JSON. Lo
   vigilan `audita_preparcial1.py` (el resultado) y `sin_aritmetica.py` (la causa, con `ast`).
2. **Hay una regla nueva, propia de este documento: ninguna cifra reutilizada puede
   desincronizarse.** El preparcial cita cifras que ya calcularon `genera_cap1.R`, `genera_cap2.R` y
   `genera_cap3.R`. El día que un capítulo se regenere y una de esas cifras cambie, la pregunta del
   preparcial queda mintiendo **sin que nada lo diga**: su JSON sigue siendo internamente coherente.
   Esa es la familia de auditoría que ni los capítulos ni el taller tienen, y es la razón principal
   de que este documento necesite auditor propio.
3. **`cuenta_sitio.py` se pone en rojo con un HTML sin clasificar.** Su comentario nombra el caso
   —«un archivo con un nombre nuevo, `parcial-1.html`, digamos»— porque ya pasó con el Taller 1
   antes de C9. Hay que abrirle el cuarto cubo, y en la misma tarea enlazarlo desde `index.html`:
   comprueba también eso.
4. **`.gitignore` es lista blanca de raíz.** Este archivo de plan no se versiona hasta que se añada
   `!/PLAN_Preparcial_Corte_1.md`, y hay que comprobarlo con `git check-ignore -v`.
5. **El HTML es un artefacto.** No se edita a mano: se edita `ensambla_preparcial1.py` y se vuelve
   a ensamblar.

**La cadena, en orden:**

```
precalculo/rscript.sh precalculo/genera_preparcial1.R    # el precálculo
python3 precalculo/ensambla_preparcial1.py               # el HTML
<geo_env>/python precalculo/audita_preparcial1.py        # el auditor independiente
python3 precalculo/prueba_auditor_preparcial1.py         # el arnés de inyección
cd precalculo && python3 audita_texto_preparcial1.py     # las cifras de la prosa
precalculo/audita_todo.sh --rapido                       # todo junto
```

---

## 2. Qué evalúa, módulo por módulo

Los **30 módulos evaluables**. Los m12 de los capítulos 1 y 2 no aparecen: son la autoevaluación del
capítulo, no contenido.

| Origen | Módulos | Qué tiene que quedar comprobado |
|---|---|---|
| Cap. 1 | m1–m11 | Los tres tipos de dato y qué es aleatorio en cada uno · Tobler · por qué se rompe la inferencia clásica y **en qué dirección** · n efectivo · estacionariedad e isotropía · una sola realización · escala y soporte · el ecosistema de R · anatomía de un `sf` y de un `ppp` · CV aleatoria inflada · notación |
| Cap. 2 | m1–m11 | Geoide/elipsoide/datum · lat-lon no son cartesianas · qué destruye cada proyección · EPSG 4326/3857/3116/9377 · **`st_transform` vs. `st_set_crs`** · medir sobre la Tierra · formatos · CSV→`sf` y el orden lon/lat · geocodificación y su sesgo · validez topológica · índices y `st_join` |
| Cap. 3 | m1–m8 | Decisiones dentro de un coropleto · conteo vs. tasa · los cinco esquemas de clasificación · el mismo dato en cinco mapas · color y daltonismo · `tmap` · más allá del coropleto · **MAUP efecto escala** |

**Regla de cobertura, mecanizada:** cada uno de los 30 módulos toca **al menos una** pregunta o
ejercicio, y **ninguna** pregunta apunta fuera de esos 30. Lo comprueba `audita_preparcial1.py`, no
la memoria de quien escribe.

---

## 3. Estructura del documento — 8 módulos

Se respeta la **regla del ritmo** (§9.1 del plan del material): ningún módulo abre pidiendo trabajo,
todo componente va con su párrafo de entrada y el de salida, y el encabezado es un contrato.

| # | Módulo | Contenido | Componentes |
|---|---|---|---|
| 1 | **Qué entra en el parcial, y qué no** | El mapa de los 30 módulos con enlace a cada uno; la frontera del cap. 3 dicha explícitamente; cómo leer la retroalimentación y por qué se puede repetir | tabla de alcance, sin quiz |
| 2 | **Bloque A · Datos espaciales y la primera ley** | 11 preguntas, una por módulo del cap. 1 | quiz de los 4 tipos |
| 3 | **Bloque B · CRS y georreferenciación** | 11 preguntas, una por módulo del cap. 2 | quiz + 1 `.geomapa` de lectura |
| 4 | **Bloque C · Cartografía y MAUP I** | 8 preguntas, una por módulo del cap. 3 | quiz + 1 `.geomapa` de lectura |
| 5 | **Procedimientos: seis rutinas que el parcial puede pedir** | 6 pares R/Python con **salida real** verificada, no ilustrativa | `.code-tabs` con `#>` |
| 6 | **Bloque D · Integración** | 6 preguntas que cruzan capítulos —el tipo de pregunta que un parcial hace y una autoevaluación de capítulo no puede hacer— | quiz |
| 7 | **Ejercicios guiados** | 6, con solución **calculada en R**, sobre procedimiento e interpretación | `.ejercicio-guiado` |
| 8 | **Ruta de repaso y los errores que se repiten** | El consolidado de los cuatro bloques y el catálogo de errores frecuentes con su cifra medida | resumen consolidado |

**Total: 36 preguntas** (11 + 11 + 8 + 6) **y 6 ejercicios guiados.** Reparto por tipo, con mínimo
de uno de cada tipo por bloque: ~14 `opcion`, ~7 `multiple`, ~7 `numerica`, ~8 `grafico`.

**Toda opción lleva su `retro`, también las incorrectas** —y las incorrectas son las que enseñan—.
Es la regla del motor y aquí se mecaniza: el auditor rechaza una opción sin retroalimentación, con
retroalimentación vacía o con la misma retroalimentación que otra opción de la misma pregunta.

---

## 4. Dependencias

```
P0.1 alcance verificable ─────┐
                              ├──► P1.1 genera_preparcial1.R ──► P1.2 audita ──► P1.3 arnés
P0.2 motor: repaso entre      │                                       │
     documentos + enlace      │                                       ▼
     profundo ────────────────┘                          P2.1 esqueleto (m1, m8)
                                                                      │
                                              ┌───────────┬───────────┴───────────┐
                                              ▼           ▼                       ▼
                                        P2.2 bloques  P2.3 bloque C,        P2.4 ejercicios
                                            A y B      procedimientos            guiados
                                              └───────────┴───────────┬───────────┘
                                                                      ▼
                                            P3.1 prosa ──► P3.2 cubo, bucle, portada ──► P3.3 cierre
```

Se construye de abajo arriba y **cada paso deja un HTML que abre y funciona**: la navegación declara
solo los módulos que existen, como hizo el Taller 1 en C5a. Un preparcial a medio construir se puede
leer entero sin botones que lleven a un módulo vacío.

---

## 5. Fase 0 — El contrato y el motor

### ✅ P0.1 — El alcance, escrito una vez y verificable · **HECHA (2026-08-25)**

`precalculo/alcance_preparcial1.py` + `precalculo/prueba_alcance_preparcial1.py` (**8/8 inyecciones
cazadas, control en verde**). Los 30 módulos salen con su título leído del `courseData` publicado.

**Lo que se encontró al probarlo, y no lo habría visto nadie leyendo el código:** las anclas de
numeración se comprobaban recorriendo los módulos presentes, y **un ancla sobre un módulo que
desaparece no falla, deja de existir**. Quitándole el glosario al capítulo 1, la autoevaluación subía
al módulo 11, el ancla del 12 no se comprobaba porque ya no había 12, y el alcance devolvía sus 30
módulos **con la autoevaluación del capítulo dentro**, cuadrando y sin decir nada. Ahora se itera
sobre las anclas, no sobre los módulos: que el módulo anclado exista es parte de lo que el ancla
afirma.

**Descripción.** Un módulo de Python, `precalculo/alcance_preparcial1.py`, que declara los 30
módulos evaluables y **lee sus títulos del HTML publicado de cada capítulo**, no de una copia. Lo
consumen el generador, el ensamblador y el auditor, así que la lista existe en un solo sitio.

**Criterios de aceptación:**
- [ ] Devuelve 30 entradas `{doc, modulo, titulo, archivo}` con los títulos leídos de `courseData.modules` de los tres capítulos publicados.
- [ ] Aborta si un capítulo publicado tiene menos módulos de los que el alcance pide (el día que alguien renumere el cap. 3, esto para).
- [ ] No contiene ningún título escrito a mano.

**Verificación:** `python3 -c "import alcance_preparcial1 as a; print(len(a.ALCANCE))"` da 30 · los 30 títulos aparecen literalmente en los HTML de origen.
**Dependencias:** ninguna. **Archivos:** 1. **Alcance: XS.**

---

### P0.2 — El motor aprende a devolver al módulo exacto de otro documento

**Descripción.** Hoy el resumen del quiz resuelve `courseData.modules[m-1]`: módulos **del propio
archivo**. En un preparcial que evalúa tres capítulos, ese resumen apuntaría a sus propios bloques,
que es exactamente lo contrario de lo que un preparcial tiene que hacer. Se añade al motor un campo
`repaso: {doc, modulo}` que imprime «Cap. 2 · módulo 5 — `st_transform` vs. `st_set_crs`» **con
enlace**, y se le enseña a la plantilla el enlace profundo `#mN` que ese enlace necesita, porque hoy
no existe: `loadModule()` no mira el hash y no lo escribe.

**Criterios de aceptación:**
- [ ] `capitulo-2-crs-georreferenciacion.html#m5` abre directamente en el módulo 5, con la barra lateral marcándolo.
- [ ] Navegar entre módulos actualiza el hash; atrás y adelante del navegador funcionan.
- [ ] Un hash inválido (`#m99`, `#basura`) cae al módulo 1 y avisa por consola, sin romper la carga.
- [ ] El resumen del quiz acepta `repaso` además del `modulo` numérico de siempre, y los capítulos ya escritos siguen funcionando con el numérico.
- [ ] **Retropropagado**: plantilla + los 4 capítulos + el Taller 1 regenerados, sin regresión (regla fija del §9 del plan del material).

**Verificación:** `precalculo/audita_todo.sh --rapido` en verde · `campos_vivos.py` y `comentarios_cerrados.py` en verde · en el navegador, los cinco documentos abren con consola limpia y el `diff` de los HTML regenerados se limita al bloque del motor.
**Dependencias:** ninguna. **Archivos:** plantilla + 5 ensambladores. **Alcance: M.**

> **Ésta es la tarea que se puede recortar si aprieta la fecha.** Sin ella el preparcial funciona, y
> lo que se pierde es concreto: el resumen diría «módulo 5» sin decir de qué capítulo y sin llevar a
> él. La sustituta barata es una tabla estática módulo→enlace en el módulo 8. Pierde el *quién falló
> en qué*, que es lo que convierte un cuestionario en un preparcial.

---

### ✅ Checkpoint 0 — el contrato en pie
- [ ] `alcance_preparcial1.py` devuelve 30 módulos leídos, no escritos.
- [ ] El enlace profundo funciona en los cinco documentos publicados.
- [ ] `audita_todo.sh --rapido` en verde con los capítulos regenerados.
- [ ] **Revisión de Javier antes de seguir**: sin esto, todo lo demás se construye sobre una frontera de temario que puede no ser la suya.

---

## 6. Fase 1 — El precálculo

### ✅ P1.1 — `genera_preparcial1.R` · **HECHA (2026-08-25)**

`preparcial1_datos.json`, 29,2 KB: 119 cifras reutilizadas (30/30 módulos, de 1 a 5 por módulo), 4
cálculos nuevos, 6 series de gráfico, 10 errores y 14 anclas. Reproducible byte a byte salvo la marca
de tiempo. Cinco guardas, las cinco vistas fallar por inyección: ruta inexistente, módulo del alcance
sin cifras, cifra de un módulo fuera del alcance, codificación rota y distractor indistinguible.

**La guarda que no estaba en el plan y hubo que escribir.** Dos distractores «razonables» no
evaluaban nada: el (n-1) contra el n del tamaño efectivo (64,52 contra 64,47 con n = 1121) y el arco
de paralelo contra la geodésica (9 mm en 111 km). Los dos nombran un error real y ninguno se
distingue de la respuesta: preguntan por el redondeo y castigan a quien entendió. La regla quedó
mecanizada —**redondeados a la precisión con que se presentan, todos los valores tienen que ser
distintos**— y los dos casos se conservan como cifras de la prosa, que es donde sí enseñan.

**Descripción.** Calcula en R, con semilla 2026, todo lo que el preparcial dice. Tres bloques
distintos y **hay que no mezclarlos**: `reutilizado` (cifras que ya viven en `capN_datos.json`,
guardadas **con su ruta de origen**, no copiadas a ciegas), `nuevo` (lo que ninguna pregunta previa
calculó) y `graficos` (las series que dibuja cada pregunta de tipo `grafico`).

**Criterios de aceptación:**
- [ ] `salidas/preparcial1_datos.json` con `meta` (semilla, versiones de R y paquetes, alcance, fecha), `reutilizado`, `nuevo`, `graficos` y `errores`.
- [ ] Cada entrada de `reutilizado` guarda `{origen, ruta, valor}` y el script **aborta** si el valor no coincide con el del JSON del capítulo.
- [ ] Al menos **8 anclas** contra la literatura o contra los capítulos que **paran** el script si fallan.
- [ ] Reproducible byte a byte en dos ejecuciones seguidas.

**Verificación:** dos pasadas y `diff` del JSON · las 8 anclas se ven fallar al perturbarlas a mano.
**Dependencias:** P0.1. **Archivos:** 1 + 1 salida. **Alcance: M.**

### ✅ P1.2 — `audita_preparcial1.py`, y las tres familias que nadie más tiene · **HECHA (2026-08-26)**

**Descripción.** Recalcula en Python, sin compartir entorno con lo auditado: geopandas para el
GeoPackage de estaciones, **pyproj** donde R usó lwgeom y s2, **mapclassify** donde R usó classInt,
y pandas/numpy para los CSV. Cinco familias, más un preámbulo de formato.

1. **Cifras nuevas** — las cuatro de `nuevo`, desde la fuente primaria.
2. **Sincronía** — las 119 `reutilizado` contra su ruta en `capN_datos.json`. *La que impide que el preparcial envejezca en silencio.*
3. **Cobertura** — los 30 módulos tocados, ninguna pregunta fuera del alcance, todas con `repaso`.
4. **Retroalimentación completa** — toda opción con `retro` no vacía y distinta de sus hermanas.
5. **No filtración** — el enunciado no contiene literalmente el texto de la opción correcta (familia heredada del Taller 1, adaptada).

**Tres cosas que el plan no había previsto y hubo que decidir.**

1. **Las preguntas no están en el JSON.** Los enunciados, las opciones y la retroalimentación solo
   existen en el HTML publicado, así que las familias 3, 4 y 5 no tenían nada que auditar en
   `preparcial1_datos.json`. El auditor lee las cuatro autoevaluaciones del documento con un
   **analizador propio** —objetos, listas, cadenas JSON, números; la función de dibujo se salta
   sola contando llaves— y no con expresiones regulares: una regular que se deje una pregunta no
   falla, informa de menos, y la cobertura sale verde con una pregunta menos vigilada. El
   analizador se comprueba a sí mismo contra el mismo recuento que usa `cuenta_sitio.py`.
2. **La sincronía tiene un segundo piso.** El HTML lleva su propia copia del JSON incrustada, así
   que regenerar el precálculo y **no reensamblar** deja las preguntas citando cifras viejas con el
   JSON del disco ya corregido — que es exactamente lo que pasó el 2026-08-25 (§12.4). Se comparan
   el uno contra el otro, y el aviso dice qué clave se movió.
3. **La familia 5 creció, y por eso encontró lo que encontró.** La versión del plan miraba el
   enunciado; esta mira además la pista, y sobre todo **la posición de la respuesta correcta en el
   documento entero**. Ver §12.6.

**Criterios de aceptación:**
- [x] Las cinco familias corren y el auditor imprime el recuento por familia: 11 · 49 · 23 · 16 · 9 · 4 comprobaciones.
- [x] **112 comprobaciones, 0 fallos, 0 saltadas** sobre el precálculo real. No hay ninguna saltada que declarar: todo lo que se propuso comprobar se comprueba.
- [x] Estropear a mano una cifra de `cap3_datos.json` pone la familia 2 en rojo, y nombra la ruta, el valor del capítulo y el del preparcial. Se probó con dos a la vez —`m8.r_departamento` y `m5.n_comparaciones_cvd`— sobre copias, con `PREPARCIAL1_CAPS`.

**Verificación:** `<geo_env>/python precalculo/audita_preparcial1.py` · la prueba manual de la familia 2, por los dos lados: moviendo el capítulo y moviendo el preparcial.
**Dependencias:** P1.1. **Archivos:** 1. **Alcance: M.**

### ✅ P1.3 — `prueba_auditor_preparcial1.py` · **HECHA (2026-08-26)**

**Descripción.** Le inyecta defectos al auditor para probar que sabe fallar. Sin esto, el verde de
P1.2 no significa nada: es la lección de `A.3` del plan del material.

**Criterios de aceptación — los tres, con margen:**
- [x] **≥ 40 inyecciones, 40 cazadas**, con al menos 5 por familia. **87 y 87**, repartidas 11 · 36 · 17 · 11 · 7 · 5.
- [x] Ninguna cifra inyectada existe ya en el archivo (la trampa de `A.3`). Y **una vuelta más**: se comprueba que la copia cambió *y* que el auditor **informó** en vez de morir.
- [x] Escribe sobre copias, nunca sobre lo publicado. Los **cinco** archivos —el JSON, el HTML y los tres capítulos— se comparan byte a byte al cerrar.
- [x] **Añadido:** 95 de 95 tipos de comprobación se han visto fallar. Los 3 que no, con su motivo escrito y en listas separadas.

**Lo que ya está puesto para que esto se pueda escribir:** el auditor lee por
`PREPARCIAL1_DATOS` (el JSON), `PREPARCIAL1_HTML` (las preguntas) y `PREPARCIAL1_CAPS` (la carpeta
de los `capN_datos.json`). La tercera hace falta y las otras dos no bastaban: la desincronización
que existe de verdad no la provoca el preparcial, la provoca que un capítulo se mueva debajo, y sin
poder mover el capítulo esa familia solo se prueba por el lado que nunca falla solo.

**Lo que costó, y es lo que este archivo enseña.** El arnés salió en rojo **cuatro veces**, y
**las cuatro por defectos del arnés, no del auditor**:

| Intento | Qué pasó |
|---|---|
| 51/53 | `meta["n_reutilizado"]` en vez de `n_reutilizadas`: la inyección **añadía una clave nueva**. Cambiaba el archivo —así que no era «inerte»— y no movía la comprobación |
| 51/53 | el reordenador de opciones producía JavaScript roto y **el auditor moría al analizar**. El código de salida era ≠ 0, así que el arnés lo contaba como cazado |
| 75/77 | el bloque D con **dos** capítulos seguía pasando: el umbral es `>= 2`. Costó dos intentos ver que había que dejarlo en uno |
| 86/87 | `SOLO_FUENTES` declaraba cinco comprobaciones «imposibles de atacar» y **cuatro sí lo eran**: las escondía como cubiertas, que es lo que esa lista existe para no hacer |

De ahí salen las tres cosas que este arnés tiene y el del taller no: **`revento()`**, que distingue
«el auditor informó» de «el auditor murió»; la regla de que **cambiar el archivo no es mover la
comprobación**; y **tres listas separadas** en vez de una, porque «no lo he atacado», «no puedo
atacarlo» y «no puede fallar» son tres cosas y mezclarlas es cómo se esconde una laguna.

**Y dos cosas del auditor que el arnés destapó, y que no son defectos:**
· `col_esf` —la columna con la que se comprueba el radio de s2— **no se lee del capítulo, se lee de
la copia de `reutilizado`**. Envenenar `cap2_datos.json` dispara la familia 2 y **no** esa
comprobación: hacen falta las dos inyecciones, y están las dos.
· La comprobación **«hay 36 preguntas publicadas en 4 bloques»** lleva la cifra dentro del nombre,
así que **no puede verse fallar bajo el mismo nombre**; y su condición es `total > 0`, falsa solo
cuando ya explotó todo lo demás.

**Verificación:** `python3 precalculo/prueba_auditor_preparcial1.py` → **87 de 87 · TIPOS 95 de 95**.
Tarda unos minutos: son 89 invocaciones del auditor, cada una releyendo los GeoPackage.
**Dependencias:** P1.2. **Archivos:** 1 (615 líneas). **Alcance: S** — se quedó en M.

### ✅ Checkpoint 1 — el precálculo, y el auditor que sabe fallar · **CERRADO (2026-08-26)**
- [x] Reproducible byte a byte · auditor en verde (112/112) · **arnés 87/87, y 95 de 95 tipos**.

---

## 7. Fase 2 — El ensamblado

### ✅ P2.1 — Esqueleto y los dos módulos que enmarcan · **HECHA (2026-08-25)**

**Una corrección al propio plan.** Esta tarea decía «el módulo 1 y el 8». No se puede: el motor exige
que la navegación declare exactamente los módulos que existen y que vayan del 1 al N **sin huecos**,
porque un botón que abre un `template` inexistente deja el panel en blanco sin un solo error en
consola. Así que el módulo de cierre es hoy el **2**. Para que eso no cueste nada, los módulos se
construyen desde una **lista ordenada de constructores** y el número, la cabecera y la entrada de
navegación salen de la posición: insertar los cuatro bloques entre el primero y el último los
renumera solos.

**Tres defectos encontrados mirando la página montada, no el código:**

1. **Los pies de las cifras estaban escritos como nota para quien redacta, no como pie para el
   estudiante.** «Lo mismo en %» se entiende debajo de su hermana; en el catálogo de errores cada
   cifra se lee suelta, y ese pie acabó rotulando como porcentaje de una distancia lo que es una
   diferencia de área. Catorce pies reescritos y una guarda que rechaza los que empiezan por «Lo
   mismo», «La misma»… y los que empiezan por el símbolo de la unidad que el valor ya lleva puesta.
2. **Un error del catálogo citaba cifras que miden otra cosa.** «Medir distancias euclídeas sobre
   grados» estaba cableado a `medir.distancias`, que compara esfera contra elipsoide. Lo que mide ese
   error es N4, calculado justamente para eso: los errores pueden citar ahora los cálculos nuevos, y
   el catálogo dice **0.59887 %** de error medio sobre los 64 980 pares, **2.50648 %** el peor, y
   **100 %** de los pares sobreestimados —el error no se cancela al promediar—.
3. **La guarda de componentes de demostración llevaba la lista escrita a mano** y dejó vivo
   `MAPAS_ESTACIONALES['demo-mapa']` en el documento publicado: ocho registros conocidos, nueve
   existentes, y verde sobre los ocho que sabía mirar. Ahora los identificadores se **leen de la
   plantilla**.

**Descripción.** `ensambla_preparcial1.py`: la plantilla, el `courseData`, la navegación que declara
solo los módulos existentes, el módulo 1 (alcance) y el 8 (ruta de repaso). Abre y funciona.

**Criterios de aceptación:**
- [x] El módulo 1 lista los 30 módulos con enlace y **dice qué queda fuera**: cap. 3 m9–m11, con su nombre. *(Enlace a la portada del capítulo, no profundo: P0.2 está aplazada y todos los enlaces pasan por `enlace_modulo()`, así que añadir el `#mN` será una línea.)*
- [x] `courseData` no declara ningún campo que nadie lea (`campos_vivos.py`: 9 documentos, esquema sin divergencias).
- [x] La página abre con consola limpia y sin módulos vacíos en la navegación.
- [x] Sin desbordamiento horizontal a 1 280, 375 ni 318 px; la tabla ancha scrollea dentro de su caja.

**Verificación:** navegador + `campos_vivos.py` + `comentarios_cerrados.py`.
**Dependencias:** P0.1, P0.2, P1.1. **Archivos:** 1. **Alcance: M.**

### ✅ P2.2 — Bloques A y B (22 preguntas) · **HECHA (2026-08-25)**

**Criterios de aceptación:**
- [x] 11 + 11 preguntas, una por módulo del cap. 1 y del cap. 2, cada una con su `repaso`.
- [x] Al menos una de cada uno de los cuatro tipos en cada bloque (13 `opcion`, 4 `numerica`, 3 `multiple`, 2 `grafico`).
- [x] Toda opción con su `retro`; las incorrectas explican **dónde falla el razonamiento**. Mecanizado: el ensamblador rechaza una opción sin retroalimentación, con retroalimentación vacía o con la misma que una hermana.
- [x] Ninguna geometría nueva: los dos gráficos leen series ya precalculadas de `preparcial1_datos.json`.
- [x] `cuenta_sitio.py` informa **22 preguntas**.
- [x] Cinco familias de guarda sobre las preguntas: tipos completos por bloque, número de respuestas correctas según el tipo, retroalimentación presente y distinta, enunciado que no copia literalmente la opción correcta, y contenedor de cuestionario sin registro.

**Lo que no estaba previsto y hubo que decidir.** Una pregunta de las 22 —la del tamaño efectivo—
usa como distractores los tres valores calculados en P1.1, y la retroalimentación de fallo los nombra
uno a uno: «si te salió 1104.61 descontaste la correlación linealmente; si te salió 3.46 usaste el
Moran de la primera banda como si fuera el ρ medio». Es la forma que toma en la práctica la decisión
de calcular los distractores en vez de inventarlos, y es lo que hace que fallar enseñe algo.

**Verificación:** `audita_preparcial1.py` familias 3–5 en verde · `cuenta_sitio.py` informa 22 preguntas.
**Dependencias:** P2.1. **Archivos:** 1. **Alcance: M.**

### ✅ P2.3 — Bloque C, procedimientos y bloque D · **HECHA (2026-08-26)**

**Criterios de aceptación:**
- [x] 8 preguntas del cap. 3 (m1–m8) y 6 de integración que **cruzan capítulos**. La prueba de que cruzan no es la intención de quien las escribió: fallando el bloque D entero, el resumen manda a **seis módulos distintos de los tres capítulos** —cap. 1 m2 y m6, cap. 2 m2, m9 y m11, cap. 3 m8—, y ninguno es el bloque que se acaba de hacer.
- [x] 6 pares R/Python con salida real: **71 de 71** cifras anunciadas aparecen en la salida real, y **461 de 461** encadenando el documento con los cuatro capítulos y el taller.
- [x] Ningún bloque marcado `arranque`: los 8 que declara `verifica_bloques.py` son todos del Taller 1.
- [x] Los cuatro tipos en los dos bloques nuevos, y **30 de 30 módulos** del alcance con pregunta propia.

**Verificación:** `verifica_bloques.py --todos` en 461/461 · `sin_aritmetica.py --prueba`, `campos_vivos.py`, `comentarios_cerrados.py` y `cuenta_sitio.py` en verde · navegador: consola limpia, los cuatro lienzos nuevos con tinta y con `aria-label`, `labelRotation` a 0 en los diez rótulos del gráfico de discordancia, sin desbordamiento horizontal a 1 280, 375 ni 318 px, y los dos bloques recorridos fallando a propósito.
**Dependencias:** P2.1. **Archivos:** 1. **Alcance: M.**

### P2.4 — Los seis ejercicios guiados

**Criterios de aceptación:**
- [ ] 6 ejercicios (2 por capítulo) con solución **calculada en R** en `salidas/preparcial1_soluciones.json`.
- [ ] Cada solución trae el procedimiento, no solo el resultado: qué se hace, en qué orden y por qué.
- [ ] Ninguna cifra de la solución escrita en el ensamblador (`sin_aritmetica.py`).

**Verificación:** `sin_aritmetica.py --prueba` en verde · las 6 soluciones reproducibles.
**Dependencias:** P1.1, P2.1. **Archivos:** 2. **Alcance: M.**

### ✅ Checkpoint 2 — el preparcial completo, sin publicar
- [ ] 36 preguntas, 6 ejercicios, 30 módulos cubiertos, 0 preguntas fuera de alcance.
- [ ] **Lectura de Javier de los cuatro bloques enteros**, como los lee un estudiante. El ritmo no lo caza ninguna herramienta.

---

## 8. Fase 3 — El arnés y la publicación

### ✅ P3.0 — La auditoría de contenido · **HECHA (2026-08-26), revisada y aprobada**

**Por qué existe, y por qué no es «revisar por encima».** Todo el arnés de este documento comprueba
**la forma**: que haya exactamente una correcta, que toda opción lleve retroalimentación distinta de
sus hermanas, que ninguna cifra citada se haya movido, que cada `#>` cuadre con la salida real. Nada
de eso sabe si lo que la opción correcta **dice** es verdad. Ya se cobró una: la opción correcta de
C8 afirmaba que la correlación se aleja del valor individual «siempre hacia arriba» y la curva
publicada cruza esa línea entre 400 y 700 zonas (§12.6). La cazó leer la serie. **Este es el único
punto ciego que la maquinaria tiene por construcción**, y por eso esta tarea no es opcional aunque
todo salga verde.

**La superficie, medida:** 36 enunciados, 36 pistas, **116 opciones con sus 116 retroalimentaciones**,
28 `retroAcierto`/`retroFallo`, 6 gráficos, 12 bloques de código, 10 fichas de error y 82 párrafos de
prosa. Unas 330 afirmaciones, y ninguna la ha comprobado nadie por su contenido.

**El protocolo, y el primer paso es el que hace que esto funcione.**

1. **Contestar el preparcial a ciegas, antes de mirar la clave.** Leer una pregunta con la respuesta
   marcada delante no es auditarla: es confirmarla. Se extraen las 36 preguntas **sin la marca
   `correcta`** —`lee_autoevaluaciones()` de `audita_preparcial1.py` ya devuelve el objeto entero, así
   que quitar la marca es una línea—, se contestan, y solo entonces se compara. **Cada discrepancia
   entre la respuesta propia y la marcada es un hallazgo hasta que se demuestre lo contrario**, en un
   sentido o en el otro.
2. **Por cada pregunta, dos preguntas y no una:** ¿la marcada es cierta? y —la que más duele—
   ¿**algún distractor es también defendiblemente cierto**? Un distractor verdadero castiga
   justamente a quien más sabe, y ninguna guarda puede verlo.
3. **Los seis gráficos, contra la serie del JSON y no a ojo.** La afirmación de la opción correcta
   se comprueba calculando sobre `graficos.*` en `preparcial1_datos.json`: monotonías, cruces,
   máximos, signos. Es como se encontró lo de C8 y es reproducible.
4. **Las 116 retroalimentaciones, una a una.** Son donde vive la enseñanza y donde no ha mirado
   nadie. Dos criterios: que digan algo **cierto**, y que expliquen **dónde falla el razonamiento**
   en vez de asegurar que falla.
5. **Los seis procedimientos:** que las dos pestañas hagan de verdad lo mismo, que los comentarios
   digan la verdad —ahí ya apareció uno: la esfera de s2 no era el radio medio del WGS84— y que un
   estudiante pueda seguirlos sin el capítulo delante.
6. **Ortografía y convenios de la casa:** tildes, «comillas angulares», raya (—) frente a guion,
   separador de millar fino y `&nbsp;` antes de la unidad, punto decimal y no coma.

**Cómo se clasifica cada hallazgo**, porque una lista de 200 cosas sin jerarquía no se puede usar a
seis días del parcial:

| Cubo | Qué es | ¿Bloquea repartir? |
|---|---|---|
| **A · error de hecho** | la clave está mal, un distractor es verdadero, una retro afirma algo falso | **Sí** |
| **B · ambigüedad** | dos opciones defendibles, enunciado que no se puede contestar con lo que da | **Sí** |
| **C · redacción / ortografía** | se entiende, pero está mal escrito o se lee mal | No |
| **D · sugerencia** | mejoraría, y es opinión | No |

**Criterios de aceptación — los siete, cumplidos:**
- [x] Las 36 preguntas contestadas a ciegas y las discrepancias con la clave, resueltas una a una. **36 de 36; una discrepancia, y era un hallazgo.**
- [x] Por cada pregunta, dicho explícitamente que **ningún distractor es cierto**. Con **ocho salvedades razonadas** —distractores de premisa cierta y conclusión falsa—, todas revisadas y aceptadas.
- [x] Las 6 de gráfico, contrastadas **contra la serie**, con el cálculo escrito. **6 de 6, y dos dieron hallazgo.**
- [x] Las 116 retroalimentaciones y los 28 comentarios generales, leídos. **116 de 116**, más los 29 comentarios de los bloques de código.
- [x] Los 12 bloques de código: equivalencia entre pestañas y comentarios ciertos. **Ningún comentario falso; dos pestañas que no calculaban lo mismo.**
- [x] Cada hallazgo en su cubo, y **todo A y B llevado a `ensambla_preparcial1.py`**. **32 de 32 aplicados**, incluidos los del cubo D.
- [x] La cadena entera en verde **después** de los arreglos. 112/112, 71/71, **461/461** encadenado.

**Se hace por bloques, no de una pasada.** Un informe escrito del tirón sobre 330 afirmaciones
pierde fidelidad hacia el final, y esto se puede interrumpir: A, B, C, D, procedimientos, y los dos
módulos que enmarcan.

**Lo que se hizo, y no fue una pasada:** seis, en el orden del §8 —bloques A, B, C, D, los seis
procedimientos y los dos módulos que enmarcan—. El informe entero, con el razonamiento de cada
hallazgo y lo que se revisó **sin** encontrar nada, está en **`AUDITORIA_CONTENIDO_P30.md`** (raíz).

**Los cinco que bloqueaban repartir, y que todo el arnés daba por buenos:**

| | Qué estaba mal |
|---|---|
| **B-1** · A10 | el enunciado y la pista pedían lo contrario que la clave: 42.97 % contra 75.34 %, con tolerancia 1.0 |
| **A-1** · B3 | la opción correcta decía que Mercator destruye el área más que ninguna de las seis, y es **la tercera** |
| **A-2** · B7 | «los mismos 20 rasgos» contra `n_rasgos` = 60, y ni eran «los mismos» |
| **B-2** · C4 | el `aria-label` no daba una sola magnitud: con lector de pantalla la pregunta era incontestable |
| **A-3** · D2 | el veredicto era correcto y **la razón que lo sostenía, falsa** |
| **A-4** · módulo 7 | el catálogo llamaba «tasa» a un puntaje medio, contradiciendo a C2 y al capítulo 3 |

**Tres decisiones de Javier al abrir la tarea**, y quedan como precedente: el informe vive en la raíz;
**entran los 82 párrafos de prosa de los módulos que enmarcan**, no solo el cuestionario; y **los
hallazgos del cubo D se aplican**, no solo se anotan.

**Verificación:** el informe por cubos · la cadena del §0.3 en verde · y la lectura de Javier, hecha
y conforme (2026-08-26).
**Dependencias:** P2.3. **Archivos:** 3 (`genera_preparcial1.R`, `ensambla_preparcial1.py`, el informe). **Alcance: L.**

### P3.1 — `audita_texto_preparcial1.py` y sus inyecciones

**Criterios de aceptación:**
- [ ] Toda cifra de la prosa, de los enunciados, de las opciones y de las retroalimentaciones existe en el precálculo, **incluidas las de dentro de KaTeX**.
- [ ] Las inyecciones del preparcial añadidas a `prueba_texto.py`, todas cazadas.

**Verificación:** `cd precalculo && python3 audita_texto_preparcial1.py` · `python3 precalculo/prueba_texto.py`.
**Dependencias:** Fase 2. **Archivos:** 2. **Alcance: S.**

### P3.2 — El cuarto cubo, el bucle nuevo, la lista blanca y la portada

**Descripción.** Lo que impide que el preparcial nazca fuera del arnés, que es justo el defecto que
C8 del Taller 1 existe para no repetir.

**Criterios de aceptación** (los cinco cerrados el 2026-08-26 por la noche):
- [x] `cuenta_sitio.py` abre el cubo `preparcial-*.html`, con su tabla y su nota. Ya estaba, del adelanto del 25.
- [x] `audita_todo.sh` gana su bucle propio, y **descubre solo**. Probado por inyección: con un `preparcial2_datos.json` y un `audita_preparcial2.py` falsos, el guion pasa de **19 a 22 pasos** —auditor, alcance y prosa— sin tocar una línea. Los ficheros falsos se retiraron.
- [x] `index.html` enlaza el preparcial en su propia sección. Ya estaba; `cuenta_sitio.py` confirma «los 6 archivos del curso están enlazados».
- [x] `!/PLAN_Preparcial_Corte_1.md` en `.gitignore`: `git check-ignore -v` no devuelve nada sobre este archivo, que es lo que se buscaba.
- [x] `README.md` al día. **Y llevaba un capítulo de retraso, cosa que este criterio no preveía:** decía «Tres de los diez capítulos» y contaba 36 módulos, 30 simuladores y 13 ejercicios. El capítulo 4 se cerró en `cec913c` y está enlazado en la portada sin distintivo. Corregido a los totales que imprime `cuenta_sitio.py` —48 módulos, 40 simuladores, 36 mapas, 48 preguntas, 18 ejercicios, 41 bloques por lenguaje—, comprobados contra su salida y no copiados de memoria.

**Tres decisiones de diseño del bucle, por si hay un Corte II:**
1. **Es un tercer bucle, no una rama del de talleres.** Un preparcial no enseña contenido nuevo (no es capítulo) y no se califica ni se individualiza (no es taller). Meterlo en cualquiera de los dos le habría exigido fingir que es lo que no es — el mismo argumento de C8 del Taller 1.
2. **El arnés del alcance corre también con `--rapido`**, por la razón que el propio guion aplica a `prueba_ensambla_capN`: cuesta **0,06 s**, y gatearlo solo serviría para no correrlo nunca. Es lo único que vigila que la frontera del temario (D1) siga donde el plan la puso.
3. **El bucle de la prosa está escrito y hoy no encuentra nada.** `audita_texto_preparcial1.py` es P3.1 y no existe; el bucle se salta entero y en silencio. Está puesto ya para que el día que nazca entre al arnés sin que nadie tenga que acordarse de volver aquí. **Esto es lo que desbloquea la dependencia de P3.1:** ya no hace falta que P3.1 exista para que P3.2 esté completa.

**Verificación:** ✅ `ARNÉS COMPLETO EN VERDE`, código de salida 0, **19 pasos, 0 en rojo**, sin ningún «archivo sin clasificar» ni huérfano de portada.
**Dependencias:** ~~P3.1~~ — ver el punto 3. **Archivos:** 5 → **se tocaron 2** (`audita_todo.sh`, `README.md`); los otros tres ya estaban. **Alcance: M.**

### P3.3 — Verificación en el navegador y cierre

**Criterios de aceptación** (recorridos el 2026-08-26 por la noche; los 8 módulos son **7**
mientras P2.4 no exista, y el octavo habrá que re-verificarlo cuando nazca):
- [x] Consola limpia en los 7 módulos. Único mensaje: el aviso de `cdn.tailwindcss.com`, que sale en todo el sitio y es de diseño.
- [x] Sin desbordamiento horizontal a 1 280, 375 y **318 px**. 21 medidas —7 módulos × 3 anchos—, ninguna desborda.
- [x] Todo lienzo con tinta y con `aria-label`; 0 gráficos huérfanos. **6 de 6**, y son exactamente las 6 preguntas de tipo `grafico`.
- [x] Los cuatro bloques recorridos **fallando a propósito**: **36 de 36** dan pista al primer fallo, retroalimentación marcada `mal` al segundo y revelan la respuesta. El resumen sale en los cuatro. **Y aquí salió el hallazgo, ver abajo.**
- [x] Peso medido: **388 161 bytes = 379,1 KiB**, 99,9 KiB comprimido. (El ensamblador imprime «376 KB» porque mide **caracteres**, no bytes: 3 370 de diferencia son las tildes. Las dos cifras son correctas y miden cosas distintas.)
- [x] **¿Qué quedó dicho y no mostrado?** Recorrido hecho. Una cosa, y es la de siempre: **el enlace de repaso promete un módulo y entrega un capítulo** (ver abajo).
- [x] El sello `audita_todo.sh` en `ARNÉS COMPLETO EN VERDE` — **llegó con P3.2**, la misma noche: 19 pasos, 0 rojos, código de salida 0.

**El hallazgo, y es de los que solo se ven en el navegador.** Fallando el bloque A entero, la lista
de «vale la pena volver» salía **«módulo 1, módulo 10, módulo 11, módulo 2, módulo 3…»**. El motor
ordena con `(a.orden || 0) - (b.orden || 0) || localeCompare(etiqueta)` y **ninguna de las 36
preguntas declaraba `orden`**: las 36 claves valían 0, ganaba el desempate alfabético y «10» va
antes que «2». Lo veía cualquier estudiante que fallara más de dos preguntas de A o de B —los dos
bloques de 11 módulos— y también el D, que además desordenaba entre capítulos.
· **Ninguna de las 112 comprobaciones del auditor podía verlo**, y no por descuido: el orden lo
decide el motor **en tiempo de ejecución**, y el auditor lee el JSON y el HTML, que son correctos.
Es la séptima vía del §12.7, y la única que hasta hoy no tenía ejemplo.
· **Arreglado en `ensambla_preparcial1.py`, una línea:** `repaso` lleva ahora
`orden: capítulo × 100 + módulo`, que ordena también el bloque D cruzando los tres capítulos.
Verificado en el navegador: A da 1→11, B da 1→11, C da 1→8 y D da cap1 m2, cap1 m6, cap2 m2,
cap2 m9, cap2 m11, cap3 m8. **No se tocó el motor**, así que no hay retropropagación que hacer.
· Cadena entera repasada después: 112/112, 71/71, `sin_aritmetica` y `campos_vivos` en verde.

**Lo dicho y no mostrado, que NO se arregló aquí porque es P0.2.** El resumen escribe «Cap. 1 ·
módulo 5 — Tamaño de muestra efectivo» y el enlace lleva a **la cabecera del capítulo**, no al
módulo 5. Comprobado el porqué: **los tres capítulos no tienen una sola ancla `id="mN"`** —sus
módulos se cargan desde `<template>` con JavaScript—, así que el enlace profundo no es añadir
`#m5` a un `href`: pide motor. Es exactamente la mitad que le falta a P0.2 y el §9 ya la da por
soltable. **El sustituto que nombra el §9 ya está puesto** y verificado: la tabla estática «La ruta
de repaso completa» del módulo 7, que lista los 30 módulos en orden.

**Verificación:** `precalculo/audita_todo.sh` completo en `ARNÉS COMPLETO EN VERDE`.
**Dependencias:** P3.2. **Archivos:** 0–2 → **se tocó 1** (`ensambla_preparcial1.py`). **Alcance: S.**

### ✅ Checkpoint 3 — listo para repartir
- [ ] Arnés completo en verde · enlazado desde la portada · leído entero.

---

## 9. La ruta corta, si la fecha aprieta

No sé cuándo es el parcial —es la pregunta 1 del §11—. Si no cabe el plan entero, esto es lo que se
puede soltar y **lo que cuesta cada recorte**, para que el recorte sea una decisión y no un
accidente:

| Se suelta | Se ahorra | Se pierde |
|---|---|---|
| **P0.2** (motor y enlace profundo) | ~1 sesión | El resumen dice «módulo 5» sin capítulo y sin llevar a él. Sustituto: tabla estática en el módulo 8 |
| **P1.3** (arnés de inyección) | horas de reloj, no de trabajo | El verde del auditor deja de estar probado. Es el paso que el propio repositorio identifica como el más caro de saltarse |
| **P2.4** (ejercicios guiados) | ~1 sesión | Se queda solo la dimensión de reconocer, sin la de producir |
| **Bloque D** (integración) | ~½ sesión | Desaparece justo el tipo de pregunta que un parcial hace y una autoevaluación de capítulo no |

Lo que **no** se suelta: la cobertura de los 30 módulos, la retroalimentación por opción, la familia
de sincronía del auditor, el enlace desde la portada y **la auditoría de contenido (P3.0)**. Sin la
primera el preparcial no cubre lo que promete; sin la segunda no enseña; sin la tercera envejece
mintiendo; sin la cuarta no existe; y sin la quinta puede estar enseñando al revés con todo el arnés
en verde, que es la única forma de fallo que este material no ha sabido ver nunca por sí solo.

---

## 10. Riesgos

| Riesgo | Impacto | Mitigación |
|---|---|---|
| **El preparcial se desincroniza del capítulo que evalúa** | **Alto** | Familia 2 de `audita_preparcial1.py`: cada cifra reutilizada se compara contra su ruta de origen, no se copia |
| Preguntas escritas de memoria, con cifras plausibles | **Alto** | D10 + `audita_texto_preparcial1.py` + `sin_aritmetica.py`. En Muestreo se colaron tres cifras mientras se corregía justamente ese problema |
| **La frontera del temario queda implícita** y el estudiante estudia de más o de menos | Alto | El módulo 1 la dibuja con nombres; el auditor prohíbe preguntas fuera del alcance |
| El HTML nace fuera del arnés | Alto | P3.2 antes del cierre, y el bucle descubre por convención |
| Retroalimentación que dice «incorrecto» y no enseña | Medio | El auditor exige `retro` en toda opción, no vacía y distinta de sus hermanas; la lectura de Javier en el Checkpoint 2 |
| El enunciado filtra su respuesta | Medio | Familia 5, heredada del Taller 1 |
| Tocar el motor rompe los capítulos publicados | Medio | Retropropagación obligatoria en la misma sesión (regla fija del §9) y `diff` acotado al bloque del motor |
| 36 preguntas con retroalimentación por opción es mucha redacción | Medio | Se reparte en tres tareas (P2.2, P2.3), cada una deja el archivo abriendo y funcionando |

---

## 11. Preguntas abiertas

1. ~~**¿Qué día es el parcial?**~~ ✅ **CERRADA: el 1 de septiembre de 2026.** Quedan siete días
   desde el arranque, y el preparcial tiene que estar repartido antes. Decide el §9.
2. **¿El preparcial se reparte antes o después de la última clase del Corte I?** Si es antes, el
   módulo 8 no puede dar por vistos los módulos 9–11 del capítulo 3 ni siquiera de pasada.
3. **¿Quieres el catálogo de errores frecuentes del módulo 8 con cifra medida** —cuántos confunden
   `st_transform` con `st_set_crs`, por ejemplo— o basta con nombrarlos? Medirlo exige datos de
   respuestas que no existen todavía; nombrarlos, no.
4. **¿Un preparcial por corte?** Si la respuesta es sí, conviene que el bucle de `audita_todo.sh` y
   el cubo de `cuenta_sitio.py` nazcan ya genéricos —está previsto así en P3.2—.

---

## 12. Lo que apareció construyendo el precálculo

### 12.1 · `st_distance` sobre EPSG:4326 no mide sobre el elipsoide

Se descubrió porque un ancla de N2 no cuadraba **por nueve milímetros** en ciento once kilómetros
—8,6·10⁻⁸ relativo—, que es justo el `(Δλ)²sen²φ/24` que separa el arco de paralelo de la geodésica.
Tirando de ahí:

| Lo que se mide | Qué lo da | Columna del capítulo 2 |
|---|---|---|
| Geodésica sobre el **elipsoide** WGS84 | `lwgeom::st_geod_distance`, o `st_distance` con `sf_use_s2(FALSE)` | `grados.lon_m_elipsoide` |
| Geodésica sobre una **esfera** de 6 371 008,8 m | `st_distance` **tal cual**, porque sf usa s2 por defecto | `grados.lon_m_esfera` |
| Arco de paralelo `(π/180)·N·cos φ` | la fórmula de libro | ninguna |

Las tres coinciden en el ecuador y se separan al subir en latitud: en Bogotá, s2 se queda **126,5 m
cortos por grado**. Verificado a cuatro decimales contra las dos columnas del capítulo.

**No es un detalle de implementación: es el contenido del módulo 6 del capítulo 2** —s2 contra
GEOS— y ahora es el primer distractor de la pregunta del grado de longitud. Un distractor que no
nombra un error hipotético: **es la respuesta que da la orden que el estudiante va a escribir**.

La primera versión del ancla afirmaba lo contrario —que `st_distance` reproduce la columna
elipsoidal— y habría publicado un preparcial que enseña al revés. La cazó el propio ancla al fallar.

### 12.2 · Los capítulos 2 y 3 publican las tildes rotas

`capitulo-3-cartografia-maup.html` tiene 13 apariciones de la forma `<U+00E1>` y
`capitulo-2-crs-georreferenciacion.html` 5, y algunas están en marcado que el estudiante ve: la tabla
de conteo contra tasa del módulo 2 dice «Bogot<U+00E1>, D.C.» y «Atl<U+00E1>ntico»; el módulo 4 del
capítulo 2, «La Guadalupe (Guain<U+00ED>a)».

Entra por los CSV del precálculo —`cap2_areas.csv` 581 líneas, `cap3_desercion.csv` 586,
`cap3_municipios_conteo_tasa.csv` 574, `cap3_departamentos.csv` 11—, no por `jsonlite`, que es lo que
`utf8.R` vigila. Por eso `audita_todo.sh` pasa entero en verde con esto publicado: **su prueba de
humo usa un literal del propio archivo, que sí se parsea bien.**

Se arregla en su sitio, no aquí: está levantado como tarea aparte. Lo que hace este plan es
**negarse a propagarlo**: `genera_preparcial1.R` para si una cadena reutilizada trae `<U+`, y la
guarda se ha visto fallar sobre el nombre real de Bogotá.

### 12.3 · El resumen del cuestionario no sabía salir de su propio documento

P2.2 no podía escribirse sin tocar esto, así que la mitad de P0.2 entró aquí.

El motor resolvía la ruta de repaso con `courseData.modules[m - 1]`: los módulos **del documento que
se está leyendo**. En un capítulo es lo correcto. En un preparcial que evalúa tres capítulos, ese
resumen mandaba a repasar **el bloque que el estudiante acababa de terminar**.

Se añadió a la plantilla un campo opcional `repaso: {etiqueta, href}` que convive con el `modulo`
numérico de siempre. Los cuatro capítulos y el taller siguen funcionando exactamente igual: el
cambio es aditivo.

Y de paso salió un defecto latente del propio motor. La rama de «acertaste todo al primer intento»
se decidía por si la lista de repaso había salido vacía, no por si había fallos. Eran lo mismo
mientras **toda** pregunta declarara `modulo`; con un campo opcional de por medio, una pregunta sin
ninguno de los dos habría producido «Resultado: 5 de 11» seguido de «acertaste todo», que es la
clase de contradicción que nadie prueba porque nadie la provoca a propósito. Ahora la rama se decide
por los fallos.

**Retropropagación pendiente, y declarada.** La plantilla lleva el motor nuevo; los cuatro capítulos
y el taller llevan el viejo, que funciona igual porque el cambio es compatible hacia atrás. No se
regeneraron **porque otra sesión está reconstruyendo en paralelo los capítulos 2 y 3** para arreglar
las tildes (§12.2), y rehacer cinco documentos mientras otro proceso rehace dos invita a no saber
quién escribió qué. Comprobado que el cambio no rompe nada: reconstruido el Taller 1 a un destino
temporal, su ensamblador cierra limpio y el `diff` contra lo publicado queda acotado al bloque del
resumen. Al regenerar los capítulos aparecerá también un retoque de redacción —«vale la pena volver»
en vez de «vale la pena volver a ellos», «puedes seguir adelante» en vez de «puedes pasar al
siguiente capítulo»—, que es intencionado: el texto ya no puede dar por hecho que lo que se repasa
está en este documento.

**El enlace profundo sigue sin hacerse.** `enlace_modulo()` lleva a la portada del capítulo y nombra
el módulo en el texto. Añadir el `#mN` es una línea en esa función más el manejador del hash en la
plantilla, y sigue siendo lo primero que se recorta si la fecha aprieta.

### 12.4 · La desincronización llegó a los veinte minutos de estar prevista

La razón de que este preparcial tenga generador propio en vez de copiar cifras —§1, regla 2— es
que una cifra reutilizada envejece **en silencio**: el JSON del preparcial sigue siendo coherente
consigo mismo aunque el capítulo del que salió haya cambiado. Es el tipo de argumento que suena
prudente y tarda meses en cobrarse.

Tardó una tarde.

Mientras se escribía P2.2, la sesión que arregla las tildes (§12.2) regeneró el precálculo de los
capítulos 2 y 3. El arreglo tocaba **cadenas**, no cifras, así que era razonable esperar que nada
más se moviera. Se movieron dos:

| Cifra | Antes | Después | Origen |
|---|---|---|---|
| `form_gpkg_razon` | 1.07014 | 1.03945 | `cap2_datos.json:formatos.gpkg.razon_sobre_shp` |
| `form_geojson_razon` | 3.34109 | 3.33206 | `cap2_datos.json:formatos.geojson.razon_sobre_shp` |

Y tiene todo el sentido en cuanto se ve: son **razones de tamaño de archivo**, y escribir bien las
tildes cambia cuántos bytes ocupa el shapefile. Nadie lo habría predicho, y nadie lo habría notado:
la pregunta B7 cita las dos, y el documento publicado siguió afirmando 1.07014 hasta que se volvió
a ensamblar.

**Y de paso destapó una clase de defecto que la regla D10 no cubría.** La retroalimentación de esa
pregunta decía «Pesa 1.07014 veces: **un 7 % más**». Ese «7 %» es una cifra escrita a mano: no pasa
por ningún formateador, así que `sin_aritmetica.py` no puede verla, y con la cifra nueva habría
quedado diciendo 7 donde toca 4. Buscándolas aparecieron **diecisiete** más del mismo tipo,
repartidas por los dos bloques: «tres veces mejor», «cincuenta y seis veces», «Son 140 KB»,
«explicar dos tercios de la varianza», «medio kilómetro», «ocho diezmilmillonésimas»… Todas
reformulaban en palabras una cifra del precálculo, y todas eran correctas el día que se
escribieron.

Las diecisiete están reescritas para no repetir la magnitud, o para citarla por su clave. **La
mecanización de esto es P3.1** (`audita_texto_preparcial1.py`), que es justo la herramienta que
mira las cifras de la prosa incluidas las de dentro de KaTeX. Hasta que exista, esta clase de
defecto solo la caza leer.

### 12.5 · Lo que apareció escribiendo P2.3

**El estado de `sf_use_s2()` es global, y el `#>` de un bloque depende de él.** El procedimiento 3
publica las dos distancias entre Bogotá y Medellín: la que devuelve `st_distance()` tal cual y la
del elipsoide. Pero `verifica_bloques.py --todos` ejecuta **todos los bloques de R del sitio en una
sola sesión**, y el capítulo 2 la deja con s2 apagado. Sin tocar nada, el bloque del preparcial
habría anunciado la cifra esférica y devuelto la elipsoidal —o al revés, según el orden alfabético
de los archivos—, y el mismo bloque habría dado dos resultados distintos según se verificara solo o
con los demás. El bloque guarda el estado, lo fija a lo que quiere enseñar y lo restaura:

```r
previo <- sf_use_s2()
sf_use_s2(TRUE)
...
invisible(sf_use_s2(previo))
```

Es §12.1 convertido en código ejecutable, y de paso deja el entorno como estaba para el taller, que
en el orden alfabético va después del preparcial.

**La curva del efecto escala cruza la línea del valor individual, y la primera versión de la
pregunta decía que no.** La opción correcta de C8 afirmaba que con menos zonas la correlación se
aleja del valor individual «y siempre hacia arriba». Con 700 zonas la media es **0.33760** y el
valor sobre estudiantes es **0.36272**: por debajo. Lo cazó leer la serie del JSON antes de dar la
opción por buena. **Vale la pena anotarlo como clase de defecto**, porque es la que menos vigilancia
tiene: en una pregunta de lectura de gráfico, la opción correcta es una afirmación sobre unos datos
que **ningún guion comprueba**. El auditor sabe contar cuántas correctas hay; no sabe si lo que
dicen es verdad. Lo mismo pasó con dos glosas verbales —«no llega a la quinta parte», «mueve el
tercer decimal»—, que eran cifras a mano de las que describe §12.4 y se sustituyeron por las
latitudes tabuladas del capítulo 2.

**Diez pares de esquemas con su nombre completo no caben en un lienzo.** El gráfico de discordancia
tiene rótulos como «Intervalos iguales / Desviación estándar»: puestos enteros, Chart.js los rota y
se solapan justo en la parte que hay que leer. Van abreviados y en dos líneas —el nombre completo de
los cinco esquemas está en el enunciado y en el `aria-label`, así que no se pierde nada—, y la
comprobación no es mirar la captura sino preguntárselo al gráfico: `chart.scales.x.labelRotation`
vale **0** y los diez rótulos siguen ahí.

**Un bloque de código con una barra invertida no se puede interpolar en una f-string.** El
intérprete del proyecto es 3.10, y `{tabs(..., "cat(sprintf(\"...\\n\"))", ...)}` no compila. El
idioma de la casa ya lo resolvía —`ensambla_cap1.py` cierra la cadena, suma `tabs(...)` y abre
otra—, pero el error que da Python (`from __future__ imports must occur at the beginning of the
file`, señalando la línea 53) no se parece en nada a la causa.

**Y una que no es del preparcial, pero se midió aquí.** A 375 px los `<pre>` de la plantilla llevan
`overflow-x: hidden`, así que una línea larga de código **se recorta** en vez de scrollear dentro de
su caja. No es de este documento: el capítulo 3 publicado hace exactamente lo mismo —655 px de
contenido en 303 de caja—, y las líneas del preparcial están dentro del presupuesto de la casa
(máximo 83, p95 72, contra 82–84 y 70–77 de los cuatro capítulos). Arreglarlo toca la plantilla y
obliga a regenerar cinco documentos publicados, así que queda **levantado y no hecho**.

### 12.6 · Lo que encontró el auditor el día que nació

**La respuesta correcta caía la primera en las 29 preguntas con opciones.** Las cuatro sin opciones
son numéricas; en las otras veintinueve —los cuatro bloques, los cuatro tipos, tres sesiones de
redacción distintas— la correcta era la (a), y en las `multiple` eran la (a) y la (b). El preparcial
entero se aprobaba marcando siempre la primera, sin leer una palabra, que es la negación exacta de
lo que este documento existe para hacer.

**Y ninguna de las guardas que ya había podía verlo.** El ensamblador tiene cinco familias sobre
las preguntas y las cinco son correctas; lo que pasa es que **las cinco miran una pregunta**. Cada
una de las 29 era impecable por separado: cuatro opciones distintas, una sola correcta, cuatro
retroalimentaciones distintas, ninguna filtración en el enunciado. El defecto solo existe en el
agregado, y en el agregado no miraba nadie. Es la misma forma que tenían los diecisiete «un 7 %
más» de §12.4 —cada uno correcto el día que se escribió— y merece quedar dicho como clase: **hay
defectos que no están en ninguna pieza y están en el montón**.

Se arregló barajando, no reordenando a mano. Un orden escrito a mano hay que mantenerlo, y la
pregunta que se escriba mañana nacerá otra vez con la correcta delante: es lo natural, primero se
piensa la respuesta y luego los distractores. La semilla sale del propio JSON y de la identidad de
la pregunta —bloque, número, capítulo y módulo—, así que el documento sigue siendo reproducible
byte a byte y añadir un bloque no reordena los demás. La correcta quedó repartida **2 · 8 · 7 · 5**
sobre las 22 de respuesta única, y las siete `multiple` en cinco combinaciones distintas.

**Lo que el barajado obliga a cambiar, y es lo interesante.** Catorce retroalimentaciones decían
«Las correctas son las dos primeras». Con las opciones barajadas eso es falso, y falso de la peor
manera: **sigue leyéndose bien**. Se reescribieron para nombrar las opciones por lo que dicen, que
además es mejor —el motor ya nombraba cada opción mal juzgada por su texto en el desglose de las
`multiple`, así que la frase posicional no aportaba nada— y hay una guarda nueva, en el ensamblador
y en el auditor, que rechaza cualquier retroalimentación que nombre una posición. Con un matiz que
costó una pasada: «las dos primeras **clases**» y «la **primera** banda de distancia» hablan del
contenido y tienen que seguir pudiendo escribirse, así que el patrón exige que la posición vaya
sola o nombre opciones.

**La esfera de s2 no es el radio medio del WGS84.** El bloque de código del módulo 5 —el que mide
Bogotá–Medellín sobre las dos superficies— construía la esfera con **6 371 008,8 m**, que es
(2a+b)/3 y es la respuesta que parece. s2 usa **6 371 010,0 m**. Con ese, y solo con ese, pyproj
reproduce la columna `grados.lon_m_esfera` del capítulo 2 entera a 4·10⁻¹¹ m; con el otro se separa
2 cm por grado. `verifica_bloques.py` no podía verlo porque el bloque publica la distancia
redondeada a metros y las dos esferas dan 237 921 m. Lo vio el auditor porque compara contra una
columna de once latitudes con diez decimales, no contra una cifra sola. El bloque está corregido y
la comprobación quedó puesta por los dos lados: el radio de s2 **tiene** que reproducir la columna,
y el radio medio **no tiene** que reproducirla.

**Dos hallazgos menores, y los dos son sobre cómo se miden las cosas.**

*La holgura de decimales tiene dos regímenes.* Los cinco auditores del sitio comprueban «ningún
flotante pasa de diez decimales» y les basta porque todas sus cifras son de orden 1. Aquí tres no
lo son, y `toJSON(digits = 10)` de jsonlite recorta a diez **decimales** por encima de 1 y a once
cifras **significativas** por debajo —medido, no supuesto—. Con la regla heredada tal cual, tres
cifras perfectamente escritas salían en rojo. La regla buena distingue los dos casos.

*El n efectivo no se puede reproducir a 10⁻⁹, y no es un defecto.* El capítulo 1 calculó su n
efectivo con el ρ sin redondear; lo único que el preparcial puede leer es el ρ ya escrito en el
JSON con diez cifras. Los dos caminos se separan 1,8·10⁻⁷ sobre 64,5. La tolerancia es la del ancla
del propio generador —1e-6— y queda dicho por qué: apretarla sería exigirle al preparcial que
reprodujera un número que no tiene forma de ver.

### 12.7 · Las seis vías por las que un defecto de contenido llega a verse

Lo más reutilizable que dejó P3.0, y la razón de que el protocolo del §8 tenga los pasos que tiene.
**Cada uno de los seis defectos graves lo cazó una comprobación distinta, y ninguna habría cazado a
los otros cinco.** Los seis pasaron las 112 comprobaciones del auditor sin despeinarse.

| Vía | Qué caza | El caso |
|---|---|---|
| **Contestar a ciegas** | que la clave sea la respuesta a la pregunta que se hizo | **A10**: enunciado y pista pedían la caída relativa al error por bloques; la clave la calculaba sobre el aleatorio |
| **Calcular sobre la serie** | que la opción correcta sea cierta *sobre estos datos* | **B3**: «Mercator destruye el área más que ninguna» es lo que predice la enseñanza estándar, y aquí es la tercera de seis |
| **Preguntar qué recibe quien no ve el gráfico** | que el `aria-label` sea cierto **y suficiente** | **C4**: describía la estructura y ni una magnitud, con una pista que manda a comparar barras |
| **Leer las retros como afirmaciones** | que la razón que sostiene un veredicto correcto también lo sea | **D2**: «la media sigue al teórico en todo el recorrido» — en el primer retardo va un 16 % por encima |
| **Contar los comentarios de cada pestaña** | que las dos enseñen lo mismo, no solo que devuelvan lo mismo | **Procedimientos**: 14 comentarios en R contra 6 en Python, con dos rutinas sin ninguno en Python |
| **Leer el `que` como texto publicado** | que la descripción de una cifra la nombre bien | **Módulo 7**: el catálogo imprime `cifra — que`, y cinco `que` tenían defectos |

**Y dos clases que merecen nombre propio, porque se repetirán:**

**El nombre de una ruta no es una descripción de lo que mide.** El capítulo 3 bautizó su cifra
`m2.r_conteo_tasa` por el *concepto* que ilustra —el contraste conteo/tasa del módulo «Normalizar o
mentir»—. Quien escribió el `que` del preparcial leyó el nombre de la ruta en vez de mirar la cifra, y
el documento acabó llamando «tasa» a un puntaje medio, contradiciendo a su propia pregunta C2 y al
capítulo del que salía.

**La regla D10 tiene dos mitades, y a veces toca la segunda.** «O se cita por su clave, o no se dice»
se aplicó por la primera casi siempre. Dos veces no se pudo, por motivos distintos: el «mil» del
rótulo de un lienzo **no se puede citar** —vive dentro de JavaScript y un bloque de código no se
interpola (§0.2, regla 6)—, así que se quitó el número; y «Los diez errores que se repiten» sí se
podía citar, y citarlo lo empeoraba —«Los 10 errores» se lee peor porque **el título es un nombre, no
un recuento**—, así que se mecanizó por fuera: **una guarda nueva** en el ensamblador ata el nombre a
`len(ERRORES)`, y se ha visto fallar.

**Lo que sigue sin poder mecanizarse.** P3.1 puede cazar la mayoría de las cifras de la prosa, y P3.0
le deja una veintena de casos de prueba reales. Lo que **no** puede: si lo que una opción correcta
*dice* es verdad, si un enunciado pide lo que su clave contesta, si una retro explica o solo asegura,
si un `aria-label` alcanza, y si las dos pestañas enseñan lo mismo. Por eso el §9 no suelta P3.0
aunque apriete la fecha, y por eso **P2.4 nace pasando por este protocolo**.
