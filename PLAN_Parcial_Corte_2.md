# Plan · Parcial del Corte II servido por página propia

Estadística Espacial 2026-II (20929) · Universidad El Bosque

**Fecha del plan:** 2026-08-30 · **Blanco:** el **parcial 2, semana 11**
**Encargo:** sacar el parcial del cuestionario del LMS para poder preguntar sobre
**mapas y simuladores**, que es lo único que Brightspace no sabe mostrar y lo único
que este curso tiene y otros no.
**Estado:** 🟡 **el camino de aborto ya existe** (§8, 2026-08-30): el banco de
Brightspace del Corte I está construido, auditado por dos vías y listo para subir.
Las tres compuertas de §0.3 siguen sin abrir, y hasta que se abran no se escribe
nada de las fases 1 a 6.

> **Este plan no escribe ni una pregunta del parcial del 1 de septiembre**, y sigue
> sin escribirla. El preparcial ya está publicado y cumple su papel, y ese día se
> usa además **como medición**: es la única oportunidad de ver la sala, los equipos
> y los navegadores antes de decidir nada. Ver **T0.2**.
>
> Lo que sí acabó dándole al parcial 1, el **2026-08-31**, es el banco de este §8:
> un segundo paquete sin pistas y cuatro *question pools* que reparten un examen
> distinto a cada estudiante. Está en el **§8.6**. Era el camino de aborto del
> parcial 2 y **sirvió antes al parcial 1**, que es lo que P6 anticipaba.

---

## 0. Decisiones y veredicto

### 0.1 Lo decidido (2026-08-30)

| Pregunta | Respuesta | Consecuencia |
|---|---|---|
| Qué parcial | **el 2, semana 11** | el 1 está a dos días: no cabe, y no por poco |
| Camino | **B · HTML individualizado, sin servidor** | no hay VPS, no hay app, no hay caída posible el día del examen |
| Camino de aborto | **A · banco QTI en Brightspace** | cierra además la §10.3 del plan del material, se elija lo que se elija |
| El 1 de septiembre | **medición, no construcción** | el D1 de LPF («visitar la sala») aquí sale gratis |

### 0.2 Veredicto

**Es viable, y por una razón distinta a la de Lógica de Programación.**

Allí la app era cara porque tenía que **renderizar** el examen: el material vive como
componentes React que se transpilan en el navegador, y servirlos exigía un servidor.
Aquí no. `ensambla_*.py` ya produce una página autocontenida con sus mapas, sus
simuladores y su motor de quiz dentro, sin una sola petición a la red. **La mitad cara
del problema de LPF aquí ya está resuelta y en producción desde hace un mes.**

Lo que hay que construir es más pequeño de lo que parece:

- un **modo examen** del motor de quiz, que hoy lleva la respuesta en la página (H1);
- **captura y exportación** de las respuestas, sin servidor (H9, H10);
- un **calificador**, que es una extensión de `califica_taller1.py` y no una
  reimplementación de nada (H4);
- y —esto es lo que LPF no tuvo que pagar— un **auditor con su arnés de inyección**,
  porque este repositorio no admite artefactos sin auditor (H8).

Lo que **no** hay que construir, y en LPF sí: individualización por estudiante,
comparación de cifras, reportes imprimibles sin red, y la disciplina de que ninguna
cifra se escriba a mano. Todo eso existe, está auditado y ya se usó para calificar
un taller real.

### 0.3 Las tres compuertas — ninguna se programa, y las tres pueden matar el plan

- **G1 · Aval.** Un parcial que se responde en una página propia y **se entrega como
  archivo por Brightspace**. La entrega sigue pasando por el LMS —es más suave que lo
  que pidió LPF, que sacaba el examen entero de él—, pero hay que preguntarlo antes
  de escribir una línea. Si la respuesta tarda más de lo que queda, la respuesta es no.
- **G2 · Sesión para el simulacro.** ¿Hay una sesión con el curso completo, en la
  misma sala y con los mismos equipos, antes de la semana 11? **Si no la hay, el
  parcial va por Brightspace.** Con 12 personas la prueba de carga sobra, pero el
  ensayo general no: el día del parcial no puede ser la primera vez que alguien
  distinto de ti abre esa página. Ver la Fase 5, que ya tiene vehículo.
- **G3 · El blueprint lleva ítems de mapa o de simulador.** Es la compuerta propia de
  este curso y la más fácil de olvidar. Si al escribir el blueprint resulta que las
  preguntas son de opción múltiple y numéricas y ninguna necesita el motor
  `.geomapa`, **entonces todo este plan es trabajo para obtener lo que un cuestionario
  de Brightspace ya da**, y hay que irse por A sin discutirlo. Ver H7.

### 0.4 El recorte, explícito

**Entra:** el banco del Corte II —capítulos 4 y 5— con variante por estudiante ·
el motor de quiz en modo examen · ítems de mapa y de simulador · autoguardado en el
navegador con reanudación · exportación de respuestas a un archivo · calificador con
reportes · auditor y arnés de inyección · un ítem abierto que se califica a mano.

**No entra, y se dice ahora para no discutirlo en la semana 10:** servidor, login,
monitoreo en vivo y cronómetro de servidor (H10) · ejecución de código del estudiante ·
preguntas de capítulos del Corte I —el parcial 2 es del Corte II— · versión móvil ·
cualquier pulido visual que no afecte a responder.

---

## 1. Estado medido (2026-08-30)

Todo lo de esta sección está contado o leído del repositorio, no recordado.

| Pieza | Estado | Dónde |
|---|---|---|
| Capítulo 4 · patrones puntuales | ✅ publicado, 425/0 en su auditor | `Htmls_Espacial/capitulo-4-patrones-puntuales.html` |
| Capítulo 5 · intensidad y procesos | 🟡 **en vuelo**, sin publicar | `genera_cap5.R`, `audita_cap5.py`, `cap5_*.json` sin versionar |
| Motor de quiz con retro por opción | ✅ en producción | `AUTOEVALUACIONES`, 4 tipos: `opcion`, `multiple`, `numerica`, `grafico` |
| Motor de mapas `.geomapa` | ✅ en producción, con arnés propio | `prueba-geomapa.html` |
| Individualización por documento | ✅ probada con 12 estudiantes reales | `verifica_taller1.R --lista`, 38 cifras por variante |
| Calificador con reportes sin red | ✅ 59 KB, arnés de 23 inyecciones | `califica_taller1.py`, `prueba_califica_taller1.py` |
| Lectura del alcance desde el HTML publicado | ✅ 30 módulos, 6 anclas | `alcance_preparcial1.py` |
| Arnés de 8 pasos con 3 bucles que descubren por convención | ✅ | `audita_todo.sh` |
| Recursos externos por página | 🟡 **10 archivos, 4 dominios** | `cdn.tailwindcss.com`, `cdn.jsdelivr.net`, `cdnjs.cloudflare.com`, `fonts.googleapis.com` |
| Página del parcial en modo examen | ❌ no existe | — |
| Captura y exportación de respuestas | ❌ no existe | — |

**El curso son 12 matriculados** (grupo 269314, periodo 20262), transcritos en
`calificacion/curso.txt`. No 30, no 45. Esa cifra cambia el cálculo de casi todo:
hace innecesaria la prueba de carga, hace barato el respaldo en papel, y hace que
el monitoreo en vivo —la ventaja que más costó en LPF— valga muy poco.

---

## 2. Hallazgos

### H1 · El motor de quiz lleva la respuesta en la página · **obliga a un modo examen**

En `Htmls_Espacial/preparcial-corte-1.html:7351`, cada opción se declara así:

```js
{ texto: "Que esa misma proporción de enfermos bebió de esa bomba.", correcta: false, retro: "…" }
```

En material de estudio **es lo correcto**: comprobar sin servidor es exactamente la
gracia de una página autocontenida, y la retroalimentación por opción es lo mejor que
tiene este material. En un examen calificado significa que la nota se saca abriendo
el inspector.

Es el H9 de LPF, pero con más superficie: allí era **un componente**, aquí es **el
motor entero**, y lo usan los cuatro capítulos, el taller y el preparcial.

**La adaptación es acotada, y no se toca `AUTOEVALUACIONES`.** Se añade un
`QUIZ_EXAMEN` al lado, con cuatro diferencias y ninguna más:

1. Las opciones llegan **sin `correcta` y sin `retro`**. La clave se queda en la
   máquina del profesor.
2. Sin botón «Comprobar», sin resumen del bloque, sin el enlace al módulo que falló.
3. Las respuestas se acumulan en `localStorage` y se exportan (H9).
4. La calificación es de fuera de la página, con la misma función que califica el resto.

El material en producción no puede romperse por una necesidad del parcial. Lo dice
LPF y aquí vale igual.

### H2 · La individualización existe, y su llave no sirve para un examen

`verifica_taller1.R` reparte variante por **los tres últimos dígitos del documento**,
y el `LEEME.md` de `calificacion/` avisa de las colisiones porque las tiene: «dos
documentos con los mismos tres últimos dígitos reciben la misma variante, y eso hay
que saberlo antes de calificar».

Para un taller que se lleva a casa, es una convención transparente y hasta simpática:
cada quien sabe cuál es la suya. Para un parcial tiene dos defectos:

- **Es adivinable.** Quien vea el documento del vecino sabe qué variante le tocó.
- **Colisiona.** Dos personas con la misma variante ven el mismo examen, y en una
  sala de 12 eso es una probabilidad que no conviene correr.

**Consecuencia:** para el parcial, `semilla = HMAC(pepper, documento)`, con el
*pepper* en variable de entorno, y la tabla `documento → variante` se queda offline
—donde ya vive `calificacion/`, que la lista blanca del `.gitignore` no deja pasar—.
Es el H4 de LPF, que además cubre la Ley 1581 de 2012, y aquí sale casi gratis
porque el sitio donde guardar esa tabla ya existe y ya está ignorado.

### H3 · Es el primer artefacto de este repositorio que se construye y **no se publica**

Todo lo demás aquí termina en `Htmls_Espacial/` y en GitHub Pages: capítulos,
talleres, preparciales y los dos bancos de prueba del motor. `cuenta_sitio.py` los
cuenta en cuatro tablas y **se pone en rojo si aparece un HTML que no encaja en
ninguna**. Ya pasó una vez: la §P3.2 del plan del preparcial cuenta que hubo que
adelantar media tarea porque un archivo sin clasificar iba a dejar el recuento en
rojo en la sesión siguiente.

Un examen calificado no puede vivir ahí. El sitio es público.

**Consecuencia:** carpeta `parcial/` **fuera de la lista blanca** del `.gitignore`
—se versionan los guiones, nunca las salidas—, y `cuenta_sitio.py` tiene que aprender
a no buscar ahí en vez de tropezarse. Se comprueba con `git check-ignore -v`, como
manda la cabecera del propio `.gitignore`.

### H4 · Aquí no hay `exams_eval()` que respetar, y eso abarata el calificador

LPF eligió Shiny sobre Streamlit por una razón concreta: calificar fuera de R
significaba reimplementar la tolerancia `extol` y el crédito parcial de R/exams, y
reimplementarlos mal produce discrepancias que se reclaman.

**Aquí ese argumento no existe.** No hay banco de R/exams: las preguntas son datos de
Python —`preg(tipo, doc, modulo, …)` y `op(texto, correcta, retro)` en
`ensambla_preparcial1.py:381`— y la semántica de calificación de este curso ya está
escrita, en Python, en `califica_taller1.py`, con su arnés de 23 inyecciones.

El calificador del parcial **extiende lo que hay**. Y hereda de paso la regla más
importante que ese archivo aprendió: los pesos y la rúbrica no se escriben en el
calificador, **se leen del ensamblador**, que es lo que el estudiante tuvo delante.
Si alguno cambiara, la herramienta para en el arranque en vez de calificar contra una
rúbrica que ya no existe.

### H5 · La lectura de números es un problema resuelto en el otro repositorio, y hay que traérselo

`PLAN_PARCIAL1_APP.md` §D3 (2026-08-30) lo dejó cerrado con 41 pruebas: `10.368.000`,
`10,5`, `1.234,56`, `$ 24.000.000` y `64,8 %` se leen todos bien, y cuando la escritura
es **genuinamente ambigua** —`1.500` puede ser mil quinientos o uno coma cinco— se
evalúan las dos lecturas y se acepta si alguna cae en la tolerancia, dejando constancia
de cuál se usó.

Este curso publica sus cifras con coma decimal y separador de miles en punto. Un ítem
numérico que marque mal un `0,58` escrito `0.58` genera un reclamo justificado, y lo
genera **el día que ya repartiste notas**. La regla se copia con su motivo, no se
vuelve a descubrir.

### H6 · El reparto de puntos solo se ve al calificar · lección prestada de LPF §H16

Calificando un examen real, LPF encontró que 9 de sus 21 ejercicios tenían un solo
sub-ítem, y como el blueprint repartía puntos **por ejercicio**, un número suelto valía
15 de 100 mientras cada casilla de otro valía 3,33. Factor 4,5× entre el dato más caro
y el más barato, y **no es un defecto del código: es una consecuencia del blueprint que
solo aparece al calificar**.

Aquí el riesgo es idéntico y con una vuelta de tuerca: un ítem de mapa —«di qué zona
concentra la intensidad»— es una sola respuesta y cuesta minutos de lectura, mientras
un `numerica` de tres cifras se responde con la calculadora. **El blueprint debe
declarar los puntos por ítem, no por bloque**, y T1.1 tiene que simular el reparto
antes de escribir una sola pregunta.

### H7 · El motor `.geomapa` es la única ventaja real, y por eso es la compuerta G3

Brightspace sabe hacer opción múltiple, múltiple respuesta y numéricas con tolerancia.
El banco QTI del camino A las da en dos o tres días y encima registra la nota solo.
**Todo el coste de este plan se paga por lo que el LMS no puede hacer**, y en este
curso eso es exactamente una cosa:

- un mapa de intensidad que el estudiante **lee** en vez de mirar como imagen fija;
- un simulador cuyo control se **mueve** para responder qué le pasa a la estimación;
- un gráfico que se redibuja, no un PNG.

El capítulo 5 —intensidad por núcleos— es el terreno natural de eso: el ancho de banda
es un control, no un párrafo. Si el blueprint acaba sin ítems así, el plan no se
justifica. Está escrito aquí para que la pregunta se haga en T1.1 y no en la semana 10.

### H8 · Este repositorio no admite artefactos sin auditor, y ese es el coste que LPF no pagó

`audita_todo.sh` corre en ocho pasos con **tres bucles que descubren por convención**:
capítulos, talleres y preparciales. Cada familia tiene `audita_X.py` y
`prueba_auditor_X.py`, y el preparcial tiene además `prueba_alcance_preparcial1.py`
porque su alcance se lee del HTML publicado y puede cambiar en silencio.

El parcial es un **cuarto cubo**, y trae dos comprobaciones que hoy no existen en
ningún sitio del repositorio:

- **La separación clave/enunciado.** Que ningún examen repartido contenga la respuesta.
  Es la comprobación que justifica el auditor ella sola: es la única que, al fallar,
  invalida el parcial entero y **no produce ningún síntoma visible**. Una página con la
  clave dentro se ve exactamente igual que una sin ella.
- **La ausencia de colisiones de variante** sobre la lista real del curso, antes de repartir.

El bucle nuevo se escribe una vez y hereda: el día que haya un parcial del Corte III,
entra sin tocar una línea de `audita_todo.sh`.

### H9 · El autoguardado sin servidor ya está en producción, y lo probaron 12 estudiantes

El H8 de LPF —«el autoguardado no es una mejora, es lo que hace viable todo lo demás»—
vale igual aquí, pero la pieza no hay que inventarla. El Taller 1 guarda la variante en
`localStorage`: «Se queda guardada en este navegador, así que aparece resuelta en cada
tarea» (`taller-1-caps-1-2.html:3822`). El mecanismo existe, se usó con el curso real y
nadie lo reportó roto.

Extenderlo de una variante a un mapa de respuestas es trabajo de una tarde, y cubre el
caso que de verdad importa: el navegador se cierra, el equipo se reinicia, alguien
recarga sin querer. **Con servidor o sin él, ese es el fallo probable.** El servidor
protege contra un fallo distinto —que el equipo entero se muera y haya que cambiar de
puesto—, que con 12 personas y una hora de examen se resuelve con un USB.

### H10 · Sin servidor no hay cronómetro fiable, y se dice en vez de fingirlo

El camino B tiene una limitación real y conviene escribirla antes que descubrirla: el
reloj de la página es el del cliente, y el cliente se puede mover. Un cronómetro
dibujado en la esquina es decorativo.

**El cronómetro del parcial es el del profesor**, en el tablero, como en un examen en
papel. La página registra su hora de inicio y de fin en el archivo de respuestas —lo
que sirve para detectar una anomalía después—, pero no impide nada. Con 12 personas en
una sala vigilada, eso es suficiente; si algún día no lo fuera, ese es el argumento
para el camino C y no otro.

Y el modelo de integridad, dicho igual de claro: **vigilancia, más la clave ausente de
la página**. Es el modelo del examen en papel, ni más fuerte ni más débil. No resiste a
alguien con la consola abierta en una sala sin vigilar, y no se va a pretender que sí.

### H11 · El parcial 2 depende de que el capítulo 5 esté publicado, y hoy está en vuelo

`alcance_parcial2.py` tiene que leer los módulos **del HTML publicado**, como hace
`alcance_preparcial1.py`, porque una lista escrita a mano se desincroniza en silencio
el día que un capítulo publique un módulo más. Eso significa que **no hay alcance hasta
que el capítulo 5 exista en `Htmls_Espacial/`**.

Hoy `cap5_datos.json`, `genera_cap5.R`, `audita_cap5.py` y su arnés están sin
versionar, en la rama `cierre-capitulo-4`. El plan del material le da al capítulo 5 las
semanas 8–10 y pone el parcial en la 11. **El orden cuadra, pero sin holgura**: si el
capítulo 5 se corre una semana, la Fase 1 de este plan se corre con él, y la Fase 5
—el simulacro— es lo primero que alguien va a querer recortar. No se recorta.

---

## 3. Arquitectura

```
  TU MÁQUINA (offline)                      LA SALA (semana 11)
  ────────────────────                      ───────────────────
  calificacion/curso.txt  (documento, nombre)
        │  HMAC(pepper)  → semilla
        ▼
  precalculo/genera_parcial2.R                 parcial/salida/<var>.html
    ├─ alcance leído del HTML publicado          ├─ abierta desde USB o carpeta local
    │  de los capítulos 4 y 5   (H11)            ├─ CERO peticiones a la red  (T2.4)
    ├─ cifras por variante                       ├─ mapas y simuladores vivos  (H7)
    └─ parcial2_datos.json ──┐                   ├─ QUIZ_EXAMEN, sin clave  (H1)
                             │                   ├─ autoguarda en localStorage  (H9)
  precalculo/ensambla_parcial2.py                └─ exporta respuestas_<var>.json
    ├─ parcial/salida/<var>.html  (SIN clave) ──────────────┐
    ├─ parcial/claves/<var>.json  (la clave, se queda)      │
    └─ parcial/papel/<var>.pdf    (plan B impreso)          ▼
                                                    Brightspace (entrega)
  precalculo/califica_parcial2.py  ◄────────────────────────┘
    ├─ compara contra parcial/claves/
    ├─ el ítem abierto NO se autocalifica  (H6)
    └─ reportes HTML sin red, uno por estudiante + curso.html
                             │
                             ▼
                   nota → Brightspace
```

Tres caminos de entrega —archivo, papel impreso, y el banco QTI si algo se cae— que
salen de la **misma generación**. Cambiar de camino no cambia el examen. Es la propiedad
que LPF puso en el centro de su arquitectura y aquí se conserva entera.

---

## 4. Fases y tareas

Cada tarea declara **qué deja terminado**, **cómo se comprueba** y **de qué depende**.
Alcance: **P** ≤ 2 archivos · **M** 3–5 · **G** más de 5, y una G es una señal de que
hay que partirla.

---

### Fase 0 · Compuertas y medición · *sin escribir código*

#### T0.1 — Abrir G1, G2 y G3
**Deja terminado:** las tres compuertas de §0.3 respondidas por escrito en este archivo.
**Criterios de aceptación**
- [ ] G1 respondida por quien pueda responderla en la facultad, no supuesta.
- [ ] G2 con **fecha y sala** concretas, o declarada cerrada.
- [ ] G3 respondida con un borrador de blueprint delante, no de memoria.

**Verificación:** §0.3 de este archivo, editado con la fecha y la respuesta.
**Dependencias:** ninguna. **Alcance:** P.

> **Si G2 está cerrada, este plan termina aquí y se ejecuta el camino A.** Escrito
> ahora precisamente para no negociarlo en la semana 10.

#### T0.2 — Medir la sala el 1 de septiembre
**Deja terminado:** la información que el D1 de LPF no pudo obtener desde el escritorio.
**Criterios de aceptación**
- [ ] Número de equipos, navegador y versión, y si el proxy deja salir a internet.
- [ ] Si se puede abrir un archivo HTML local desde USB o carpeta compartida.
- [ ] Cuánto tarda una página de 500 KB con mapas en pintar **en un equipo de la sala**,
      no en tu Mac.

**Verificación:** §1 de este archivo, con una fila nueva por cada dato medido.
**Dependencias:** ninguna — es el día del parcial 1. **Alcance:** P.

---

### Fase 1 · El contenido · *lo caro de verdad, y lo que no se puede automatizar*

#### T1.1 — Blueprint del parcial 2
**Deja terminado:** `parcial/blueprint.yml` con alcance, ítems, tipos, puntos y minutos.
**Criterios de aceptación**
- [ ] Puntos declarados **por ítem**, no por bloque, con el reparto simulado sobre un
      examen perfecto y uno en blanco (H6).
- [ ] Al menos un ítem de **mapa** y uno de **simulador**, o G3 queda cerrada y se va por A (H7).
- [ ] Un ítem abierto para lo que no se autocalifica, con su rúbrica (H6 de LPF, §H5).

**Verificación:** leerlo en voz alta contra el cronograma del §5 del plan del material:
los módulos que cita tienen que ser de los capítulos 4 y 5 y de ningún otro.
**Dependencias:** T0.1. **Alcance:** P.

#### T1.2 — `alcance_parcial2.py`
**Deja terminado:** los módulos del parcial leídos **del HTML publicado**, con anclas que paran.
**Criterios de aceptación**
- [ ] Lee `capitulo-4-*.html` y `capitulo-5-*.html`, no una lista escrita a mano.
- [ ] Declara por su nombre los módulos que quedan **fuera** del parcial.
- [ ] Para si el número de módulos no coincide con el ancla.

**Verificación:** `prueba_alcance_parcial2.py`, calcado del que ya existe para el
preparcial: inyecta un módulo de más y otro de menos y exige que las dos paren.
**Dependencias:** T1.1 y **el capítulo 5 publicado** (H11). **Alcance:** P.

#### T1.3 — `genera_parcial2.R`
**Deja terminado:** `parcial2_datos.json` con las cifras por variante, reproducible byte a byte.
**Criterios de aceptación**
- [ ] `semilla = HMAC(pepper, documento)`; el documento **no** aparece en la salida (H2).
- [ ] Cero colisiones de variante sobre `calificacion/curso.txt`, y para si las hay.
- [ ] Todas las cifras salen de R con anclas que paran; ninguna se escribe a mano.

**Verificación:** dos ejecuciones seguidas dan el mismo archivo (`diff`), y
`precalculo/rscript.sh` lo corre sin depender de `LANG`.
**Dependencias:** T1.2. **Alcance:** M.

#### T1.4 — El banco de preguntas
**Deja terminado:** las preguntas del parcial en `ensambla_parcial2.py`, con su clave aparte.
**Criterios de aceptación**
- [ ] Toda opción lleva su retroalimentación —también las correctas—, que se usará en la
      devolución aunque no se muestre en el examen.
- [ ] La correcta **no cae siempre en la misma letra**: el preparcial ya se dejó aprobar
      marcando la (a) las 29 veces, y lo cazó su auditor, no una lectura (§12.6 de su plan).
- [ ] Las preguntas citan cifras del precálculo, nunca literales.

**Verificación:** responder el examen entero a ciegas, como la P3.0 del preparcial.
Es la única comprobación que ninguna herramienta puede hacer.
**Dependencias:** T1.3. **Alcance:** M.

> ### ⏸ Punto de control 1 — El examen existe como contenido
> El blueprint cuadra, las preguntas están escritas y contestadas a ciegas.
> **Si esto pasa, el parcial ya se puede repartir por Brightspace aunque nada más se
> construya** — el camino A sigue abierto sin haber perdido nada.

---

### Fase 2 · La página en modo examen

#### T2.1 — `QUIZ_EXAMEN` en la plantilla
**Deja terminado:** el motor de quiz sin clave, al lado del de estudio y sin tocarlo (H1).
**Criterios de aceptación**
- [ ] Las opciones llegan sin `correcta` y sin `retro`.
- [ ] Sin botón de comprobar, sin resumen de bloque, sin enlace al módulo.
- [ ] `AUTOEVALUACIONES` intacto: los cuatro capítulos y el preparcial siguen en verde.

**Verificación:** `audita_todo.sh --rapido` sin regresión, y buscar `correcta` en el
HTML del examen: **cero apariciones dentro de los datos del quiz**.
**Dependencias:** Punto de control 1. **Alcance:** M.

#### T2.2 — Autoguardado y reanudación
**Deja terminado:** las respuestas sobreviven a cerrar el navegador (H9).
**Criterios de aceptación**
- [ ] Se guarda al salir de cada campo y cada 20 s.
- [ ] Al reabrir la página, el examen aparece como se dejó.
- [ ] La clave de `localStorage` incluye la variante: dos exámenes distintos no se pisan.

**Verificación:** guion de sabotaje — responder la mitad, matar el navegador, reabrir,
recargar a la fuerza, y comprobar que no se perdió nada en los tres casos.
**Dependencias:** T2.1. **Alcance:** P.

#### T2.3 — Exportación de respuestas
**Deja terminado:** `respuestas_<variante>.json`, que es lo que se sube a Brightspace.
**Criterios de aceptación**
- [ ] Lleva variante, huella del enunciado, hora de inicio y de fin (H10).
- [ ] Se descarga con un botón, y la página dice en letra grande que **hay que subirlo**.
- [ ] Segundo camino: un resumen imprimible, por si la descarga falla en la sala.

**Verificación:** exportar, borrar `localStorage`, y que `califica_parcial2.py` lea el
archivo y produzca la misma nota.
**Dependencias:** T2.2. **Alcance:** P.

#### T2.4 — Vendorizar los recursos externos
**Deja terminado:** la página se pinta con la red desconectada.
**Criterios de aceptación**
- [ ] Los 10 archivos de los 4 dominios, servidos desde la propia carpeta.
- [ ] Las referencias **dentro** de los CSS también —las tipografías de Google Fonts se
      le escaparon a LPF por no acabar en `.css`, y no habrían dado ningún error—.
- [ ] Fuera lo que el examen no usa; la página no tiene por qué cargar lo que no pinta.

**Verificación:** abrir con el wifi apagado, consola limpia y pestaña de red **sin una
sola petición que salga de la carpeta**.
**Dependencias:** T2.1. **Alcance:** M.

> ### ⏸ Punto de control 2 — Un examen completo, una persona · **criterio de aborto**
> Presentas el parcial entero en local, de principio a fin, sin red, y el archivo
> exportado se califica bien. **Si al terminar la Fase 2 esto no funciona, el parcial va
> por Brightspace**: lo que queda hay que gastarlo en el simulacro, no en terminar
> funcionalidad.

---

### Fase 3 · El calificador

#### T3.1 — `califica_parcial2.py`
**Deja terminado:** la nota, sobre lo que ya hace `califica_taller1.py` (H4).
**Criterios de aceptación**
- [ ] Los pesos y la rúbrica se **leen de `ensambla_parcial2.py`**, y para si cambiaron.
- [ ] El ítem abierto sale como pendiente y la nota se marca **provisional**.
- [ ] Reportes HTML autocontenidos, sin una petición a la red, más el `curso.html`.

**Verificación:** `prueba_califica_parcial2.py`, calcado del que existe: inyecciones que
tienen que parar, más un examen perfecto, uno en blanco y uno mixto.
**Dependencias:** Punto de control 2. **Alcance:** M.

#### T3.2 — Lectura de números a la colombiana
**Deja terminado:** que `0,58`, `0.58` y `58 %` no cuesten un reclamo (H5).
**Criterios de aceptación**
- [ ] Coma decimal, punto de miles, símbolo de porcentaje y espacios.
- [ ] Cuando la escritura es genuinamente ambigua, se evalúan **las dos lecturas** y se
      deja constancia de cuál se usó.
- [ ] Vacío e ilegible se distinguen de incorrecto en el reporte.

**Verificación:** la batería de LPF §D3, traída entera: 41 casos.
**Dependencias:** T3.1. **Alcance:** P.

---

### Fase 4 · El auditor · *el cuarto cubo*

#### T4.1 — `audita_parcial2.py`
**Deja terminado:** el precálculo recalculado en Python, independiente de R (H8).
**Criterios de aceptación**
- [ ] Recalcula las cifras nuevas **desde la fuente primaria**, con librerías distintas
      de las que usó R, como hizo el del preparcial con pyproj y mapclassify.
- [ ] **La comprobación que justifica el auditor:** ningún examen de `parcial/salida/`
      contiene la clave. Ni `correcta`, ni `retro`, ni el valor de una respuesta.
- [ ] Cero colisiones de variante sobre la lista real, antes de repartir.

**Verificación:** envenenar `cap5_datos.json` y exigir que el auditor nombre la ruta, la
cifra del capítulo y la del parcial.
**Dependencias:** Fase 3. **Alcance:** M.

#### T4.2 — `prueba_auditor_parcial2.py`
**Deja terminado:** la prueba de que el auditor sabe fallar.
**Criterios de aceptación**
- [ ] Una inyección por cada tipo de comprobación, y las que no se puedan probar,
      **declaradas en una lista aparte con su motivo**.
- [ ] Una inyección que **mate** al auditor no cuenta como cazada — la lección de
      `revento()`, §6 del plan del preparcial.
- [ ] Entre ellas: meter la clave a mano en un examen y exigir que pare.

**Verificación:** el propio arnés, en verde y con el recuento por familia impreso.
**Dependencias:** T4.1. **Alcance:** M.

#### T4.3 — El cuarto bucle de `audita_todo.sh`
**Deja terminado:** el parcial dentro del arnés, descubierto por convención.
**Criterios de aceptación**
- [ ] `for N in 1 2 3 4`, con los mismos `[ -f … ] || continue` de los otros tres.
- [ ] `cuenta_sitio.py` no se pone en rojo por la carpeta `parcial/` (H3).
- [ ] `git check-ignore -v` sobre las salidas: **ninguna se versiona**.

**Verificación:** `audita_todo.sh --rapido` entero, en verde, con el bucle nuevo contando.
**Dependencias:** T4.2. **Alcance:** P.

> ### ⏸ Punto de control 3 — El artefacto cumple el estándar del repositorio
> Cadena entera en verde con el cubo nuevo dentro. A partir de aquí, regenerar un
> capítulo del Corte II **avisa** si mueve una cifra del parcial, que es exactamente la
> desincronización que el preparcial ya cazó una vez.

---

### Fase 5 · El simulacro · *el día que decide*

**Tiene vehículo, y es la ventaja que LPF no tuvo.** El preparcial del Corte II —que
este repositorio ya sabe construir, con su bucle propio y su auditor— es **formativo,
sin nota y repetible**. Servirlo por la misma página, con el mismo motor en modo examen
y la misma exportación, es un ensayo general **sin nada que perder**: si falla, falló un
instrumento que se puede repetir mañana.

#### T5.1 — El preparcial del Corte II como simulacro
**Criterios de aceptación**
- [ ] Curso completo, misma sala, mismos equipos, misma hora del día.
- [ ] Guion de sabotaje deliberado: cerrar el navegador a mitad, recargar, quitar la red,
      cambiar de equipo. En los cuatro casos las respuestas siguen ahí.
- [ ] Los 12 archivos exportados se califican sin intervención manual.

**Verificación:** el `curso.html` del calificador con 12 de 12, y las incidencias
anotadas en §1 de este archivo.
**Dependencias:** Punto de control 3 y **G2**. **Alcance:** M.

> ### ⏸ Punto de control 4 — Luz verde o luz roja
> **Criterio de aborto, fijado por escrito antes del simulacro:** si más de **una**
> de las 12 personas no pudo abrir la página o perdió respuestas, **el parcial va por
> Brightspace**. Con 12 estudiantes, una es el 8 %. Se escribe ahora para no
> renegociarlo bajo presión el mismo día.

---

### Fase 6 · El parcial

#### T6.1 — Cierre de obra
- [ ] Corregir **solo** lo que rompió el simulacro. Nada nuevo.
- [ ] Runbook de una página: cómo se reparte, qué hacer si alguien no puede abrir, si
      la descarga falla, si un equipo muere.
- [ ] Generar los exámenes definitivos y **verificar tres al azar** contra su clave.
- [ ] Imprimir los `parcial/papel/<var>.pdf` y llevarlos. Con 12 son 12 hojas.

#### T6.2 — El día y lo que sigue
- [ ] Recoger las 12 entregas de Brightspace y calificar.
- [ ] El ítem abierto, a mano.
- [ ] **Devolución**: cada quien recibe su examen con la retroalimentación por opción que
      ya se escribió en T1.4 y que el examen no mostró. Es la mitad del valor del
      instrumento y es gratis.
- [ ] Archivar examen, clave y respuestas: es la evidencia ante un reclamo.
- [ ] Post-mortem en este archivo.

---

## 5. Riesgos

| # | Riesgo | Prob. | Impacto | Mitigación |
|---|---|---|---|---|
| R1 | El capítulo 5 se corre y arrastra la Fase 1 | **alta** | alto | H11; la Fase 5 no se recorta, se recorta contenido |
| R2 | La clave se filtra en la página | alta si no se atiende | **crítico** | H1 + la comprobación de T4.1, que es la razón del auditor |
| R3 | G2 no se resuelve y no hay simulacro | media | **crítico** | se decide en T0.1, antes de escribir código |
| R4 | Un equipo de la sala no abre la página | media | medio | T0.2 lo mide el 1 de septiembre, no el día del parcial |
| R5 | La descarga del archivo falla en la sala | media | alto | T2.3 con segundo camino imprimible + papel de T6.1 |
| R6 | Alguien manipula sus respuestas con la consola | baja, es presencial | alto | H10: el modelo es el del papel, y se declara |
| R7 | El reparto de puntos resulta injusto al calificar | media | alto | H6: se simula en T1.1, no se descubre al calificar |
| R8 | Se acaba construyendo lo que Brightspace ya daba | media | alto | G3: si no hay ítems de mapa, se aborta y se gana tiempo |
| R9 | Colisión de variantes en 12 personas | baja | alto | H2: HMAC, y T4.1 lo comprueba antes de repartir |

---

## 6. Supuestos declarados

1. **Presencial y vigilado.** Si cambiara a remoto, el modelo de integridad de H10 se
   cae entero y hay que rehacer la decisión, no el código.
2. **Temario: capítulos 4 y 5**, que es el Corte II según el §5 del plan del material.
3. **12 estudiantes.** Por encima de 25 vuelven a valer los argumentos de LPF sobre
   monitoreo y prueba de carga.
4. **La nota oficial termina en Brightspace pase lo que pase.** La página es
   instrumento, no registro.
5. **La semana 11 cae a mediados de octubre** —el parcial 1 es el 1 de septiembre en la
   semana 5—, pero la fecha exacta está sin confirmar. Ver P1.

---

## 7. Preguntas abiertas

- **P1 · ¿Qué día exacto es el parcial 2?** Define si hay seis semanas o cuatro.
- **P2 · G1: ¿hay aval para entregar el parcial como archivo por Brightspace?** (§0.3)
- **P3 · G2: ¿hay sesión con el curso completo antes de la semana 11?** (§0.3)
- **P4 · ¿Cuántos ítems de mapa o simulador?** Uno prueba el mecanismo; tres lo
  convierten en el corazón del parcial. Cada uno cuesta redacción y precálculo, no
  programación (H7).
- **P5 · ¿El parcial 2 incluye algo del Corte I?** El §0.4 dice que no. Si el syllabus
  dice otra cosa, cambia el alcance de T1.2 y el capítulo 5 deja de ser la dependencia
  crítica.
- ~~**P6 · ¿Se hace el banco QTI de todos modos?**~~ ✅ **CERRADA el 2026-08-30: sí, y
  se hizo primero.** Ver §8. Queda abierta su continuación para el Corte II, que es el
  mismo guion sobre el documento del Corte II cuando exista.


---

## 8. El camino de aborto, construido primero · **HECHO (2026-08-30)**

Se ejecutó antes que nada por lo que dice P6: es la única pieza que **quita riesgo de
encima de todo lo demás**. A partir de hoy, si las compuertas se cierran o el simulacro
sale mal, el Corte I ya está en Brightspace y no hay conversación que tener.

### 8.1 Lo que hay

| | |
|---|---|
| `precalculo/exporta_brightspace.py` | lee el HTML **publicado** y escribe el paquete QTI 1.2 con las extensiones `d2l_2p0` |
| `precalculo/audita_brightspace.py` | contrasta el ZIP contra el documento del que salió |
| `parcial/brightspace/banco_brightspace.zip` | **36 ítems** · 29 Multiple Choice, 7 Multi-Select · 144/144 opciones con explicación · 6 imágenes · 249 KB |
| `parcial/brightspace/sonda_brightspace.zip` | 3 ítems, uno de cada forma, 32 KB — **se sube primero** |

```bash
precalculo/exporta_brightspace.py --html Htmls_Espacial/preparcial-corte-1.html \
    --datos precalculo/salidas/preparcial1_datos.json \
    --prefijo EE_C1 --titulo "Estadística Espacial · Corte I" \
    --salida parcial/brightspace --sonda
```

La salida **no se versiona ni se publica**: `parcial/` está fuera de la lista blanca del
`.gitignore`, que es lo que pedía H3, y se comprobó con `git check-ignore -v`. Los dos
guiones sí, porque son herramienta.

**Reproducible byte a byte:** dos ejecuciones dan las mismas huellas SHA-256 en las ocho
entradas del ZIP. El barajado de opciones va con semilla derivada del identificador, no
del reloj.

> **Desde el 2026-08-31 los bancos son dos**, y esta sección describe solo el primero. El
> segundo —el del parcial del Corte I, sin pistas y con otros identificadores— está en el
> **§8.6**. Ese día el exportador cambió los títulos, así que **este ZIP se reexportó**: pesa
> 244 KB y su huella es `022c48d…`, no la que tuviera antes. Ver §8.6.4.

### 8.2 Las dos auditorías, y por qué hacen falta las dos

`audita_paquete.py` (de la skill) da **429 de 429**: el paquete es coherente como
paquete D2L. Pero un ZIP puede pasar sus 374 comprobaciones **con la clave equivocada**,
porque dentro del ZIP no hay nada con qué contrastarla.

`audita_brightspace.py` da **173 de 173** y es el que mira eso: vuelve a leer el HTML,
lee el ZIP con un analizador de XML —no con el código que lo escribió— y enfrenta el
texto de cada opción, qué opciones puntúan, y **que la retroalimentación de cada opción
sea la suya**, que es el defecto que la skill avisa que nadie nota hasta después de
calificar. Es la misma pareja de auditores que el resto del repositorio: uno mira la
forma, otro mira la verdad.

Comprueba además dos cosas propias de este banco:

- **Ningún distractor de una numérica cae dentro de la tolerancia** de su pregunta. Uno
  que cayera dentro haría la pregunta imposible: dos opciones serían la respuesta y solo
  una puntuaría.
- **El reparto de la correcta**: 1: 8 · 2: 2 · 3: 10 · 4: 9 de 29. El preparcial llegó a
  publicar la correcta siempre la primera (§12.6 de su plan) y esa no se repite.

### 8.3 · H12 · Cinco preguntas numéricas no podían viajar · **RESUELTO (2026-08-30)**

La Biblioteca de Preguntas **no importa respuesta numérica**. Una `numerica` solo puede
ir convertida en opción múltiple, y para eso hacen falta tres distractores que sean
errores concretos, no ruido. De las siete, dos los tenían calculados y **cinco nombraban
el error en prosa sin cifra** —«si te salió un porcentaje bastante menor»—. El banco
salió con 31 ítems y esas cinco declaradas fuera.

**Ya están dentro.** `genera_preparcial1.R` calcula los **quince distractores** que
faltaban, y el banco pasa a **36 de 36 preguntas**.

| Ítem | Módulo | Los tres errores que ahora tienen nombre y cifra |
|---|---|---|
| `cv_inflacion` | cap1.m10 | tomar como base el error por bloques · dar la razón y no el incremento · comparar MSE donde la pregunta dice RMSE |
| `indice_espacial` | cap2.m11 | dividir al revés · olvidar los pares que quedan por comparar · dar el porcentaje en vez de las veces |
| `convenio_intervalo` | cap3.m3 | no restar · dar la primera clase de R · contar los empates de los cinco cortes y no los del primero |
| `caida_color` | cap3.m5 | dar lo que queda · dar la diferencia en unidades y no en porcentaje · dividir por la distancia de llegada |
| `efecto_escala` | cap3.m8 | tomar como base la correlación agregada · dar la razón · agregar a municipio, donde **baja** |

**Nada se escribió a mano.** Los quince salen de cifras que el precálculo ya publicaba, y
cada bloque lleva un **ancla que recalcula la respuesta publicada desde sus ingredientes**
antes de construir sus distractores. No es ceremonia: un distractor se apoya en lo que esa
cifra *significa* —cuál es la base del porcentaje, en qué sentido va la razón—, y si la
interpretación fuera falsa el distractor sería otro número perfectamente plausible. El
ancla comprueba la interpretación, no la aritmética.

**Y la retroalimentación mejoró como efecto secundario.** Las cinco `retroFallo` decían
«si te salió un porcentaje bastante menor»; ahora dicen la cifra. Quien se equivocó se
reconoce en el número, que era el estándar que ya cumplían las otras dos.

El resto del precálculo es **idéntico**: `reutilizado`, `graficos` y `errores` no se
mueven ni un bit. Las preguntas, sus respuestas y sus tolerancias tampoco. El documento
pasa de 373 a 381 KB, todo de retroalimentación.

#### Los dos defectos que aparecieron al hacerlo

**El emparejamiento del exportador era ambiguo, y en silencio.** Casaba la pregunta con su
cálculo **por valor**, lo que bastaba con dos ítems y dejó de bastar con siete: la
reducción del índice espacial vale 11,10608 con tolerancia 0,2 y los condados que se mueven
de clase valen 11 con tolerancia 0,5, así que **cada uno cae dentro de la tolerancia del
otro**. Una de las dos preguntas se habría llevado los distractores de la otra —tres cifras
plausibles con explicaciones que hablan de otra cosa— sin que nada fallara. Ahora empareja
por **módulo y valor**, y para si un módulo tiene más de un candidato.

**Los quince distractores nacían sin auditor.** El auditor seguía en 112 comprobaciones
después de publicarlos: quince cifras nuevas que nadie miraba. Ahora son **145**, con una
familia que recalcula cada distractor por su fórmula y comprueba que la explicación
corresponda al valor —un distractor mal emparejado con su error manda al estudiante a
buscar una equivocación que no cometió—. La independencia aquí es **menor** que la de N1 a
N4 y está dicha en el código: no salen de la fuente primaria sino de cifras que el propio
auditor ya verificó contra ella en la familia 2.

Y el recorrido de la comprobación de separación pasó de una **lista escrita a mano**
—`("N1", N1), ("N2", N2)`— a recorrer todo lo que tenga distractores. Esa lista es
exactamente cómo los quince llegaron a publicarse sin que nada los mirara.

#### El tercer defecto, que es el mismo de siempre por cuarta vez

Generalizar aquella lista renombró la comprobación, y el nombre nuevo
—`grado_longitud: los distractores se distinguen a 1 decimales`— mide **60
caracteres**. `Auditoria.cierto()` rellena el rótulo hasta 58 antes del detalle, así que
uno de 58 o más se queda pegado a su detalle por un solo espacio, y `nombres()` corta por
dos: el rótulo que sale MAL deja de ser el mismo que salió OK. **La comprobación se ataca,
falla, y el arnés no la cuenta como cubierta.** Nada falla; lo que se corrompe es el
recuento de qué se ha visto fallar, en silencio.

`audita_base.py` ya lleva escrito el presupuesto —57 caracteres— y la frase «va por la
TERCERA vez». Ésta es la cuarta.

Lo que la hizo posible es que **el detector existía y no miraba aquí**.
`avisa_rotulos_largos()` subió al núcleo en `3754728` y lo llama `arnes()`, por donde
pasan los cuatro capítulos y el taller. El arnés del preparcial tiene su propio `main()`
y era el único sin ese ojo encima. Ahora lo llama: acortar el rótulo arregla la instancia
—y ya se acortaron cinco en T0.5, uno en C5b y dos más en 2026-08-24—; engancharlo es lo
que hace que no vuelva.

Con la familia nueva atacada, el arnés pasa de 87 a **106 inyecciones**: cuatro formas de
romper cada ítem —mover los tres valores, renombrar un identificador, poner una opción que
no se distingue del correcto, y mover la respuesta de la que cuelgan todos—, que son los
cuatro modos reales de equivocarse al añadir un ítem nuevo.

Resultado: **106 de 106 defectos cazados y 128 de 128 tipos vistos fallar.** La lista de
«tipos que este arnés todavía no ataca» desaparece entera.

**Y el detector, al engancharlo, cazó a la primera un rótulo que no era de esta sesión:**
`5. No filtración: ni el enunciado, ni la pista, ni la posición`, 62 caracteres, el
resumen de la familia 5. Se comprobó que no fuera un falso positivo —esa línea se emite
como comprobación y su detalle es `4 compr. 0 fallos 0 saltadas`, que **cambia** entre la
pasada limpia y la rota—, así que arrastraba el defecto entero y su rótulo no podía verse
cubierto nunca. Acortado a 53.

De paso, el título de la familia 1 decía «Las cuatro cifras nuevas, desde la fuente
primaria» cuando ya son ocho y solo las cuatro primeras salen de la fuente primaria. Ahora
dice lo que hay.

### 8.3.1 · La cadena entera, medida el 2026-08-30

| Comprobación | Antes | Ahora |
|---|---|---|
| `audita_preparcial1.py` | 112 | **145** · 0 fallos, 0 saltadas |
| `prueba_auditor_preparcial1.py` | 87 inyecciones · 34 tipos sin atacar | **106** · **128/128 tipos** |
| `prueba_alcance_preparcial1.py` | 8/8 | 8/8 |
| `sin_aritmetica.py` | limpio | limpio · 7 ensambladores |
| `campos_vivos.py` | limpio | limpio · 10 documentos |
| `verifica_bloques.py` | 71/71 | 71/71 |
| `audita_paquete.py` (skill) | 374/374 · 31 ítems | **429/429 · 36 ítems** |
| `audita_brightspace.py` | 158/158 | **173/173** |

> Medido otra vez el **2026-08-31**, `audita_paquete.py` da **431** sobre este mismo banco.
> No cambió nada aquí: la skill trae dos comprobaciones más. Se anota para que la
> diferencia contra el 429 de esta tabla no se lea como una regresión.

### 8.4 Lo que queda por hacer, y es de Brightspace, no de aquí

Los tres pasos valen igual para los dos bancos; el orden entre ellos lo fija el **§8.6**.

1. **Subir primero `sonda_brightspace.zip`** —3 ítems— y comprobar en la Biblioteca que
   el Multi-Select se ve y se califica como Multi-Select. La skill avisa de que esa forma
   no está validada en importaciones reales tanto como la de opción única.
2. Si la sonda entra bien, subir `banco_brightspace.zip`.
3. Comprobar **en Brightspace**, no aquí: que las seis figuras se pintan, que los acentos
   están, y que al fallar una opción se lee la explicación **de esa** opción.

### 8.5 Una decisión declarada: el banco no entra en `audita_todo.sh`

Tendría su quinto bucle sin esfuerzo, y aun así se queda fuera: `exporta_brightspace.py`
depende de `d2l_items.py`, que es de la skill y no de este repositorio. Meterlo en el
arnés haría que `audita_todo.sh` fallara en cualquier máquina sin la skill instalada, y
el arnés tiene que poder correr entero desde un clon limpio. Se audita a mano, con los
dos comandos de §8.2, y esta línea existe para que la ausencia no se lea como olvido.

---

### 8.6 · El banco del parcial del Corte I, y un examen distinto por estudiante · **HECHO (2026-08-31)**

Este plan dice en su cabecera que no toca el parcial del 1 de septiembre. Lo sigue sin
tocar: **no se escribió ni una pregunta nueva**. Lo que se hizo fue contestar una pregunta
que llegó el 31 —cómo dar un examen distinto a cada estudiante con el banco que ya
existe— y dejar el banco en condiciones de responderla. El §8 se escribió como camino de
aborto del parcial 2; **acabó sirviendo primero al parcial 1**, que es exactamente lo que
P6 decía que pasaría.

#### 8.6.1 La decisión: individualizar por SELECCIÓN, no por datos

`censo_banco.py` ya planteaba la disyuntiva para el parcial 2 —selección o datos— y aquí
se resolvió sola, por aritmética y por calendario:

- **Por datos** habría que pasar por `genera_preparcial1.R` y por el documento publicado,
  porque aquí ninguna cifra se escribe a mano. Es el trabajo de la Fase 1 entera, y el
  parcial era al día siguiente.
- **Por selección** no cuesta nada: son cuatro *question pools* del cuestionario sobre el
  banco ya importado.

| pool | de dónde | saca |
|---|---|---|
| Cap. 1 | `A01`–`A11` (11 ítems) | 4 |
| Cap. 2 | `B01`–`B11` (11) | 4 |
| Cap. 3 | `C01`–`C08` (8) | 3 |
| Transferencia | `D01`–`D06` (6) | 3 |

**14 preguntas · 121 968 000 formas.** Con 12 estudiantes, la probabilidad de que dos
reciban el mismo examen es **5×10⁻⁷**. El solape esperado entre dos exámenes es de **5,5
preguntas de 14 (40 %)**, y no importa tanto como parece: las opciones ya van con
`shuffle="yes"` en los 36 ítems, así que una pregunta compartida le sale a cada uno en
otra posición y con las opciones en otro orden. Si se quisiera menos solape, `3+3+2+2` lo
baja al 28 % a cambio de un examen de 10 preguntas — menos copia y menos medición.

**Por qué los pools son cuatro y no tres.** El bloque `D` no es un capítulo: son las
preguntas de transferencia y de cálculo, y **seis de ellas caen sobre módulos que `A`,
`B` o `C` ya tocan** —`A02`/`D01` y `A06`/`D02` en el capítulo 1; `B02`/`D04`,
`B09`/`D03`, `B11`/`D06` en el 2; `C08`/`D05` en el 3—. No son formas paralelas de la
misma pregunta y no se pueden intercambiar: `C08` pide leer un gráfico y `D05` calcular
un porcentaje sobre las mismas cifras. Van en su propio pool porque mezclarlas con las
conceptuales repartiría dificultad al azar.

#### 8.6.2 Lo que hubo que arreglar para que el banco sirviera de parcial

**Las pistas.** Los 36 enunciados llevaban su `Pista:` dentro — correcto en un preparcial,
regalado en un parcial. El exportador ya tenía `--sin-pista` sin usar.

**El prefijo, escrito a mano en el auditor.** El banco del parcial tiene que llevar
identificadores distintos: `qmd_globalid` es `uuid5(qid)`, así que dos bancos con los
mismos `qid` llegan a la Biblioteca con el mismo identificador global. Pero
`audita_brightspace.py` tenía `EE_C1_` escrito dentro (su familia 1), y un banco con otro
prefijo **se habría quedado sin auditor** — no fallando, sino declarando ausentes los 36
ítems. Ahora es `--prefijo`, con `EE_C1` por defecto para que el comando del §8.2 siga
igual, y con una guarda que **para** si ningún ítem del ZIP empieza por el prefijo pedido,
en vez de escupir 36 líneas rojas que no dicen qué pasó. Es la misma clase de defecto que
el §8.3 documenta dos veces: un convenio escrito a mano en dos sitios.

**Los títulos duplicados.** El título salía de `q["repaso"]["etiqueta"]`, el rótulo del
módulo, así que los seis pares de arriba llegaban a la Biblioteca **con nombre idéntico**.
Quien arma los pools elige por ese nombre: `D01` habría podido entrar en el pool
conceptual del capítulo 1 sin que nada avisara. Ahora el identificador va delante —`A02 ·
Cap. 1 · módulo 2 — …`—, los 36 títulos son únicos, y de paso los cuatro bloques quedan
contiguos al ordenar por nombre, que convierte el armado de cada pool en una selección de
un tirón.

> **El rótulo del módulo sí se sigue repitiendo, y tiene que repetirse.** `C08 · Cap. 3 ·
> módulo 8 — MAUP I · el efecto escala` y `D05 · Cap. 3 · módulo 8 — MAUP I · el efecto
> escala` no son la misma pregunta duplicada: son dos preguntas **sobre el mismo módulo**,
> y el rótulo dice de qué módulo se responde, que es lo que hace falta para repasar y para
> calificar. Lo que estaba mal era que ese rótulo fuera el nombre *entero*; el
> identificador delante es lo que las distingue. `C08` pide leer el gráfico del efecto
> escala; `D05` pide calcular en qué porcentaje sube la correlación al agregar. Los seis
> pares del §8.6.1 son todos así.

#### 8.6.3 Lo que hay, medido

| | |
|---|---|
| `parcial/brightspace_parcial/banco_brightspace.zip` | **36 ítems** · 29 MC, 7 MS · 144/144 opciones con explicación · 6 imágenes · 242 KB |
| `parcial/brightspace_parcial/sonda_brightspace.zip` | 3 ítems, uno de cada forma · 32 KB |
| prefijo · título | `EE_P1` · «Estadística Espacial · Parcial I» |

```bash
precalculo/exporta_brightspace.py --html Htmls_Espacial/preparcial-corte-1.html \
    --datos precalculo/salidas/preparcial1_datos.json \
    --prefijo EE_P1 --titulo "Estadística Espacial · Parcial I" \
    --salida parcial/brightspace_parcial --sin-pista --sonda

<geo_env>/python precalculo/audita_brightspace.py \
    --html Htmls_Espacial/preparcial-corte-1.html \
    --datos precalculo/salidas/preparcial1_datos.json \
    --zip parcial/brightspace_parcial/banco_brightspace.zip --prefijo EE_P1
```

| comprobación | |
|---|---|
| `audita_brightspace.py` · banco del parcial | **173/173** · 0 fallos, 0 saltadas |
| `audita_brightspace.py` · banco del preparcial (regresión) | **173/173** · comando del §8.2 sin tocar |
| `audita_paquete.py` (skill) · banco | **431/431** |
| `audita_paquete.py` (skill) · sonda | **53/53** |

Y tres cosas comprobadas, no supuestas: **0 apariciones de «Pista:»** frente a las 36 del
banco del preparcial · **0 identificadores globales compartidos** entre los dos bancos ·
**reproducible byte a byte** en dos ejecuciones seguidas
(`9777249…` el banco, `a3c9c31…` la sonda). La carpeta nueva queda fuera del `.gitignore`
como la otra, comprobado con `git check-ignore`.

#### 8.6.4 La deriva del ZIP del preparcial · **CERRADA (2026-08-31)**

El cambio de títulos vive en el exportador, y el ZIP guardado en `parcial/brightspace/` se
había escrito antes: reexportarlo daba otra huella —`c84fa1b…` el guardado contra
`022c48d…` el nuevo—. No era un defecto del banco, cuyas 173 y 431 seguían limpias; era
que el §8.1 presumía de reproducir byte a byte un ZIP que ya no reproducía.

**Se cerró por la vía barata: reexportar.** No había nada subido a Brightspace todavía,
así que no costó nada, y los dos bancos llevan ahora el mismo convenio de títulos — que es
lo que hace que la Biblioteca se pueda leer con los dos dentro.

```bash
precalculo/exporta_brightspace.py --html Htmls_Espacial/preparcial-corte-1.html \
    --datos precalculo/salidas/preparcial1_datos.json \
    --prefijo EE_C1 --titulo "Estadística Espacial · Corte I" \
    --salida parcial/brightspace --sonda
```

| | |
|---|---|
| `parcial/brightspace/banco_brightspace.zip` | 36 ítems · 244 KB · `022c48d…` |
| `parcial/brightspace/sonda_brightspace.zip` | 3 ítems · 32 KB · `d7c0a99…` |
| `audita_brightspace.py` | **173/173** · 0 fallos, 0 saltadas |
| `audita_paquete.py` (skill) · banco y sonda | **431/431** y **53/53** |

La huella nueva es **exactamente la que este apartado predijo** antes de reexportar, que es
la comprobación de que la deriva era la de los títulos y no otra cosa. Vuelve a reproducir
byte a byte, los 36 títulos son únicos en los dos bancos, el del preparcial **conserva sus
36 pistas** —las pierde solo el del parcial— y los dos siguen sin compartir un solo
identificador global.

#### 8.6.5 Lo que esto no compra, y se dice ahora

Las 36 preguntas son las autoevaluaciones del preparcial, **publicado con su respuesta
correcta y la retroalimentación de cada opción**. Los pools impiden copiarse del vecino;
no impiden llegar con las respuestas memorizadas. Si el parcial mide preparación sobre el
preparcial, está bien — pero es una decisión, no un efecto secundario, y por eso queda
escrita. Preguntas nuevas exigirían la Fase 1 de este plan, que es justo lo que este
camino de aborto existe para no tener que improvisar.

#### 8.6.6 El orden de subida, con dos bancos

1. `parcial/brightspace_parcial/sonda_brightspace.zip` — los tres pasos del §8.4.
2. Si entra, `parcial/brightspace_parcial/banco_brightspace.zip`.
3. Los cuatro pools del §8.6.1 en el cuestionario.
4. El banco del preparcial (`EE_C1`) **solo si se va a usar como repaso dentro del LMS**.
   Ya está reexportado con el convenio de títulos nuevo (§8.6.4), así que los dos pueden
   convivir en la Biblioteca: no comparten un solo identificador global, y cada pregunta se
   lee por su bloque y su número sin tener que abrirla.
