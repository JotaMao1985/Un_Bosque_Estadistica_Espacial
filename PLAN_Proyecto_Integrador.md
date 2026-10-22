---
tipo: plan
curso: "[[20929 Estadística Espacial]]"
capitulo: 10
fecha: 2026-10-21
estado: CONSTRUIDA (2026-10-21) — auditor en verde; falta fusionar el PR, que publica en Pages
---

# Plan · Guía del proyecto integrador — Corte III

Estadística Espacial 2026-II (20929) · Corte III · Universidad El Bosque

El sílabo pone en el Corte III un **proyecto integrador sobre un territorio real con datos abiertos**:
propuesta en la semana 10, sustentación en la 16, **20 % del Corte III**. La semana 10 pasó sin que se
publicara nada, y el plan maestro remite el enunciado y la rúbrica al módulo 11 del capítulo 10, que no
existe (T6.4). Esta ronda publica la guía como documento propio del sitio,
`Htmls_Espacial/proyecto-integrador-corte-iii.html`, más una plantilla `.Rmd` descargable, con **las mismas
fechas, el mismo peso y el mismo canal que el proyecto de Series de Tiempo** (20948), porque cinco
estudiantes cursan las dos materias y pueden presentar un solo proyecto conjunto.

## 0. Estado

- 2026-10-21: plan propuesto. **Nada construido.** Las decisiones DE1–DE12 (§3) son propuestas por defecto;
  casi todas heredan del proyecto de Series, que hereda del de Diseño. **PE1–PE4 (§4) son de Javier** y
  bloquean la rúbrica y el módulo 1.
- 2026-10-21: **Javier aprueba el plan con PE1–PE4 tal como se proponen** («Apruebo el plan con PE1–PE4 como
  los propones. Construye la guía»): el otro 50 % son quices en clase, sin examen final ni Talleres 4 y 5; solo
  datos de área como núcleo; N ≥ 25; la rúbrica de §6. DE1–DE12 quedan aprobadas con el plan. Lo siguiente es T1.
- 2026-10-21, al construir: **la regla de `nsim` de DE7 estaba mal en una unidad.** El cap. 7 (M10) dice que
  Bonferroni bilateral pide nsim + 1 > 40·N, es decir **nsim ≥ 40·N** (N = 33 pide 1 320, no 1 319). Corregido
  aquí y en §2; la guía y el auditor usan la del capítulo.
- 2026-10-21: **construida, auditada y verificada; pendiente de fusionar** (rama `claude/proyecto-integrador`).
  - La tabla de potencia se rehízo con 2 000 réplicas (`proyecto/potencia.R` → `proyecto/potencia.json`) y con
    N = 49 y 100 además: con N = 25 y ρ = 0,5 detecta el 46 %; con 64, el 79 %; con 100, el 91 %. §2 tiene ahora
    esas cifras.
  - `precalculo/ensambla_proyecto.py`: 10 módulos, 357 KB, el CSS de la plantilla (197 selectores), la rúbrica en
    una tabla y en el componente `.rubrica`, sin restos de demostración.
  - `precalculo/audita_proyecto.py`: 203 comprobaciones, 0 fallos, con el frente E corriendo los tres bloques de R
    y la plantilla con datos de ejemplo y con datos propios. `precalculo/prueba_auditor_proyecto.py`: 51 defectos,
    51 cazados por su frente, controles limpios antes y después.
  - Navegador por HTTP: los diez módulos sin errores de consola (solo el aviso de Tailwind), KaTeX sin errores,
    la rúbrica con sus 15 criterios, 375 px sin scroll horizontal; la tarjeta de la portada abre la guía y la
    plantilla responde 200.
  - Portada con su tarjeta (sección «Proyecto integrador»), `cuenta_sitio.py` con un sexto cubo (`proyecto-*`) y
    `audita_todo.sh` con su bloque.
  - **El enlace al módulo 8 de Series da 404 hasta que se publique la guía de Series** (§11). El frente H
    comprueba la forma del enlace y, cuando la guía de Series esté en su árbol, que su módulo 8 sea el de la
    conjunta.

## 1. Lo que ya no se discute (cerrado en el plan de Series, 2026-10-21)

Viene de `../Series de tiempo/PLAN_Proyecto_Pronostico.md` (§4, §5 y §7) y no se reabre aquí:

| | Qué | Dónde se decidió |
|---|---|---|
| F1 | **Fechas**: ficha mar 27 oct, preregistro mar 3 nov, avance mar 10 nov, informe dom 15 nov, todo a las **11:00**; exposición en la semana 16 (16–21 nov) | Series P1 y §5 |
| F2 | **El proyecto vale el 50 % del Corte III** de Espacial, como en Series | Series P3 |
| F3 | **Canal**: un repositorio privado de GitHub por equipo, con el docente (`JotaMao1985`) como colaborador; una release por hito (`ficha`, `preregistro`, `avance`, `informe`); cuenta la hora en que GitHub la publica | Series D8 |
| F4 | **El tope de las preguntas**: lo escrito de cada persona × min(1, preguntas / 3,0) | Series D7 |
| F5 | **La conjunta** solo admite (a) Moran y LISA sobre los MASE por unidad y (b) el rezago espacial Wy como exógena con rezago ≥ h. La (c), de kriging, está retirada | Series P3 |
| F6 | **Las reglas de la conjunta viven solo en el módulo 8 de la guía de Series.** Esta guía las enlaza y no las copia | Series D12 |

## 2. Restricciones verificadas antes de planear

- **Días de clase de Espacial: martes y jueves.** El Taller 2 se sustentó el martes 13 de octubre en el espacio
  de la clase y el Parcial 2 fue el jueves 15 (`PLAN_Taller_2_Cap_4.md`, `PLAN_Preparcial_Corte_2.md` D4). En la
  semana 16 quedan el **martes 17 y el jueves 19 de noviembre** (el lunes 16 es festivo). Las cinco fechas de F1
  son las de Series y no dependen de los días de clase de Espacial: las releases se publican a una hora, no en
  clase.
- **El sílabo de Espacial reparte el Corte III así**: examen final 50 · proyecto 20 · Talleres 4 y 5, 10 cada uno ·
  Quiz 3, 10. Con el proyecto al 50 % (F2), ese reparto ya no suma: **el otro 50 % es PE1**. Del Corte III no hay
  nada construido: ni el Quiz 3, ni los talleres, ni el examen.
- **Lo que la guía puede exigir ya está publicado**: caps. 1–7. El 7 (Moran, Geary, LISA, Gi\*, la trampa de la
  multiplicidad) salió el 2026-10-20. **Faltan el 8 (econometría, semana 14), el 9 (geoestadística, semana 15) y
  el 10 (ML espacial, semana 16).** El informe se entrega el domingo 15 de noviembre: lo que dependa del cap. 9
  llega al cierre de la misma semana en que se enseña, y lo del 10, después de la entrega.
- **El material ya le enseña al estudiante las decisiones que la rúbrica va a pedir**, y la guía no puede
  contradecirlas (frente G del auditor, §9):
  - cap. 2: un CRS proyectado y declarado antes de medir una distancia;
  - cap. 3: tasas y no conteos en el coroplético, la clasificación declarada y el MAUP como decisión;
  - cap. 6: W es la decisión más consecuente y la menos justificada; islas y `zero.policy` (M9);
  - cap. 7: inferencia por permutación con `nsim` declarado (M3); **el mismo dato con otra W da otra conclusión**
    (M7); el p de cada LISA es el bilateral por rangos (convención del capítulo); **el mapa LISA sin corrección
    de multiplicidad miente** (M10), y el bilateral no baja de 2/(nsim + 1), así que Bonferroni sobre N unidades
    pide **nsim + 1 > 40·N, es decir nsim ≥ 40·N**; Gi\* mide intensidad y no similitud (M11).
- **La potencia del Moran con N pequeño, medida hoy** (rejilla reina, W por filas, SAR con ρ dado, 2 000 réplicas
  de `moran.mc` con 499 permutaciones, unilateral al 5 %; guion en el anexo A):

  | N | ρ = 0 (tamaño) | ρ = 0,3 | ρ = 0,5 |
  |---|---|---|---|
  | 25 | 0,057 | 0,240 | 0,460 |
  | 36 | 0,053 | 0,304 | 0,579 |
  | 49 | 0,050 | 0,353 | 0,682 |
  | 64 | 0,064 | 0,421 | 0,792 |
  | 100 | 0,053 | 0,548 | 0,913 |

  (2 000 réplicas por casilla, rehecha al construir; la primera medición, con 400, daba 0,448 en N = 25 y ρ = 0,5.)
  Con N = 25, un proceso con ρ = 0,5 pasa sin detectar más de la mitad de las veces. **Un Moran no significativo
  con N chico no prueba que no haya estructura**, y la guía lo tiene que decir (DE3).
- **Las unidades que más va a usar quien elija la conjunta son los departamentos**: 32 más Bogotá, **N = 33**, con
  paneles mensuales abiertos del DANE. Las 20 localidades de Bogotá no llegan a 25, y la red de calidad del aire
  de Bogotá (RMCAB) tampoco. Un umbral de 36 dejaría fuera a los departamentos.
- **El repositorio es público y va a Pages desde `main`** (la raíz del repositorio es la carpeta del curso). La guía
  no lleva clave ni secreto, así que este plan se versiona. Publicar es fusionar el PR, y **lo fusiona Javier**: el
  modo automático niega el push a `main` y `gh pr merge` (memoria `apendice-a-densidad`).
- **La guía de Series todavía no existe.** Se construye en otra sesión con el mismo calendario. El enlace al módulo 8
  es `https://jotamao1985.github.io/Series-de-Tiempo_Un_Bosque/proyecto-pronostico-corte-iii.html#modulo-8`; la
  plantilla de Series lee el `#modulo-N` (la de Espacial, no: solo el ensamblado del cap. 5 lo arregla). Si esta
  guía sale antes que la de Series, el enlace da 404 hasta que la otra se publique (§11).

## 3. Decisiones de esta ronda — propuestas por defecto

Todo lo que lleva cifra vivirá en `proyecto/datos.py`, como en Diseño y en Series.

| | Decisión | Origen | Coste / consecuencia |
|---|---|---|---|
| **DE1** | **Individual o en parejas** (máximo 2) | Series D1 | Hasta 12 proyectos en Espacial; 5 de los 12 pueden ir a la conjunta |
| **DE2** | **Qué datos valen** (PE2 decide el tipo). Un territorio real con **datos abiertos**: la geometría de una fuente pública (DANE MGN, geoBoundaries, IDECA, Datos Abiertos Colombia u otra citable) y la variable de otra, con fuente, fecha de descarga y la llave con que se unen. **No valen** los datos del material ni de los talleres (`oldcol`/Columbus, `nc`, `auckland`, `getisord`, `meuse`, la deserción municipal de los caps. 6–7, las sedes de Bogotá de los caps. 4–5, los de los Talleres 1 y 2), ni los simulados. La geometría municipal sí vale con otra variable | Nueva (el «Qué serie vale» de Series) | Hay que enseñar a unir sin perder unidades: la unión se cuenta antes y después (cap. 2) |
| **DE3** | **N ≥ 25 unidades** (áreas, o estaciones tratadas como retículo con W por k vecinos o por distancia). Con N < 64, la guía exige leer un Moran no significativo con la tabla de potencia de §2, no como «no hay estructura» | La propuesta de Series (§7.2), medida en §2 | Admite departamentos (33), municipios de un departamento y UPZ; deja fuera localidades (20) y RMCAB |
| **DE4** | **Variable**: una tasa, una proporción o una medida por unidad, nunca un conteo bruto en el coroplético. Si es una tasa de eventos raros, se declara el problema de los números pequeños (cap. 3) | cap. 3 | Un criterio del avance (A1) lo mide |
| **DE5** | **Hitos, exposición, tope, canal y retraso: los de Series**, sin cambiar nada: ficha sin nota; reparto interno **15 · 10 · 45 · 30**; tres niveles 1,0 · 3,5 · 5,0; −15 % por sesión de retraso desde el cierre; exposición de 10 + 5 min (15 + 10 en la conjunta). El repositorio se llama `proyecto-ee-apellido1-apellido2` (`proyecto-st-ee-…` en la conjunta) | Series D3–D9 | La misma estructura en las dos materias es lo que deja calificar la conjunta con dos rúbricas sobre una release |
| **DE6** | **El preregistro congela el protocolo de inferencia espacial** antes de calcular un solo Moran: la unidad y su escala (y por qué esa, MAUP), la variable y su normalización, el CRS, **la W principal** (criterio y estilo) y **las W alternativas** para la sensibilidad, `nsim`, el nivel, la corrección de multiplicidad y la hipótesis. Cambiarlo después se permite **si se declara** en la sección de desviaciones del informe; cambiarlo en silencio se sanciona (I7) | Nueva: es el cap. 7, M7, llevado al proyecto | **Elegir W después de ver el p-valor es la fuga de este curso**, como la métrica elegida después lo es en Series. La guía lo dice en un recuadro |
| **DE7** | **`nsim` suficiente para la corrección elegida**: con Bonferroni bilateral, nsim + 1 > 40·N, es decir nsim ≥ 40·N (N = 33 pide 1 320). La guía da la cuenta y el auditor la recalcula | cap. 7, M10 | Con las 999 de siempre y N ≥ 25, Bonferroni no deja pasar ninguna unidad, haya o no conglomerados |
| **DE8** | **Lo que no está publicado no se exige, y no se aprueba como núcleo en la ficha**: la econometría (cap. 8), el kriging (cap. 9) y la CV espacial (cap. 10). Pueden entrar como complemento declarado, sin puntos propios | Series §11 (la (c) retirada) | El informe se entrega antes de que el cap. 9 esté en clase entero |
| **DE9** | **Documento propio, con prefijo `proyecto-*`**, construido como el de Diseño: `proyecto/datos.py`, módulos con `@@CLAVE@@`, `precalculo/ensambla_proyecto.py` con `--revisar` sobre `plantilla/plantilla-capitulo.html`, `precalculo/audita_proyecto.py` y su arnés `precalculo/prueba_auditor_proyecto.py` (nombres de Espacial) | Diseño D5, Series D5 | Tarjeta en el Corte III de `index.html`, la guía en `cuenta_sitio.py` y en `audita_todo.sh` |
| **DE10** | **La conjunta se enlaza, no se copia** (F6). El módulo 8 de esta guía dice quién puede elegirla y remite al módulo 8 de Series para todo lo demás. Lo único propio de Espacial que vive aquí son **los descriptores de la parte espacial en la conjunta** (en (a), la variable espacial es el MASE de cada unidad; en (b), la ganancia de MASE por unidad al añadir Wy), porque la rúbrica es de Espacial | Series D12 | El auditor prohíbe que la guía repita las reglas (frente H): si una regla aparece aquí, es una copia que puede quedarse vieja |
| **DE11** | **IA permitida y declaración obligatoria** (I8), con un ejemplo verificable. La semana 13 del sílabo es el *AI-assisted spatial analysis workshop*: la guía remite a él y a sus errores típicos (CRS y matrices de vecindad) | Series D14 y el sílabo | Como en Diseño y Series, se mide la resistencia a la IA (T8) |
| **DE12** | **Día de la exposición en la semana 16**: martes 17 o jueves 19 de noviembre; el día exacto se acuerda en clase. La defensa de la conjunta es una sola, y dónde y cuándo lo dice el módulo 8 de Series | Series D4 y F6 | Si la conjunta se defiende en la clase de Series, Espacial no la repite |

## 4. Pendientes de Javier — bloquean

| | Pregunta | Por qué bloquea | Propuesta por defecto |
|---|---|---|---|
| **PE1** | **¿Cómo se reparte el otro 50 % del Corte III?** | Fija la tabla de pesos del módulo 1 y lo que el auditor exige que sume 100 | **Quices en clase al 50 %, sin examen final ni Talleres 4 y 5**, como Series y Diseño. Para los cinco de la conjunta, las dos materias quedan con la misma forma. Los quices cubren los caps. 7–9 en las semanas 12–15 y son los que evalúan la econometría y el kriging, que el proyecto no exige. Alternativas: (b) examen final al 50 % en la semana 16, que choca con las exposiciones y concentra los caps. 8–9 en una prueba; (c) quices 25 + Taller 4 25 (el *workshop* de IA de la semana 13 como taller) |
| **PE2** | **¿Qué tipo de dato vale como núcleo?** | Fija la rúbrica: con dos tipos, I3 e I4 necesitan dos juegos de descriptores | **Solo datos de área (o estaciones tratadas como retículo)**, con Moran global y un análisis local. Un patrón de puntos entra **agregado a áreas** (conteos convertidos en tasas por unidad) o como covariable. Es el contenido del Corte III, mantiene una sola rúbrica y es lo que usa la conjunta. Alternativa: aceptar también un patrón de puntos (n ≥ 50 eventos en una ventana real; CSR con envolvente global, intensidad y `ppm`) con descriptores propios en I3 e I4. Es más instructivo pero duplica la rúbrica y lo evaluado en el Corte II (Taller 2 y Parcial 2) |
| **PE3** | **¿N ≥ 25 o más?** | Fija DE3 | **N ≥ 25**, con la lectura de potencia obligatoria. Es lo que propone el plan de Series y admite los 33 departamentos. Subir a 30 no cambia la potencia (§2); subir a 36 o más deja fuera los departamentos, que son casi la única unidad con paneles mensuales abiertos para la conjunta |
| **PE4** | **¿La rúbrica de §6 tal cual?** | Hay que publicarla antes del martes 3 de noviembre | Sí. El plan maestro proponía 6 criterios × 4 niveles (T6.4); se cambia a la forma de Series (tres hitos, tres niveles) para que la conjunta se califique igual en las dos materias. Los seis criterios del plan maestro están todos dentro (§6, última columna) |

## 5. Calendario (F1)

| Hito | Semana | Fecha | Hora | Qué se entrega |
|---|---|---|---|---|
| Ficha (sin nota) | 13 | martes 27 de octubre | 11:00 | Unas 150 palabras: territorio, unidades y N, fuente de la geometría y de la variable, la pregunta y si es conjunta |
| Preregistro | 14 | martes 3 de noviembre | 11:00 | El protocolo de DE6 congelado, más las descargas crudas con su fecha |
| Avance | 15 | martes 10 de noviembre | 11:00 | Unión verificada, cartografía exploratoria, W construida y descrita, Moran global con la W principal |
| Informe y código | 15 | **domingo 15 de noviembre** | 11:00 | El informe reproducible desde el repositorio |
| Exposición | 16 | martes 17 o jueves 19 de noviembre | en clase | El día exacto se acuerda en clase |

- La ficha recibe respuesta en la clase del **jueves 29 de octubre**.
- El material llega a tiempo: Moran, LISA y la multiplicidad (cap. 7) están publicados desde el 20 de octubre y el
  sílabo los da en las semanas 12–13, antes del preregistro.
- La guía tiene que estar publicada **antes del viernes 23 de octubre** para que la ficha tenga su semana, y **la
  rúbrica antes del martes 3 de noviembre** sin excepción.

## 6. La rúbrica de la parte espacial (propuesta: criterios y puntos; descriptores en T1)

| Hito | Criterio | Puntos | Lo que el material ya enseña | Criterio del plan maestro (T6.4) |
|---|---|---|---|---|
| Preregistro (15) | P1 · El territorio y sus datos: fuentes, fechas de descarga, N, llave de unión, CRS | 4 | cap. 2 | Reproducibilidad |
| | P2 · El protocolo de inferencia: escala y su porqué, variable y normalización, W principal y alternativas, `nsim` suficiente, nivel, corrección de multiplicidad | 7 | caps. 3, 6 y 7 (M7, M10) | Pertinencia del método |
| | P3 · Las hipótesis espaciales y el plan de análisis | 4 | cap. 7, M1 | Pertinencia del método |
| Avance (10) | A1 · Unión verificada y cartografía exploratoria: unidades antes y después de unir, tasa y no conteo, clasificación declarada | 5 | caps. 2–3 | Calidad cartográfica |
| | A2 · La W construida y descrita: vecinos por unidad, islas y `zero.policy`, componentes conexos; Moran global con la W principal y las desviaciones del plan | 5 | cap. 6 (M8–M9) | Corrección técnica |
| Informe (45) | I1 · Pertinencia: el método responde la pregunta y la escala está justificada (MAUP) | 5 | cap. 3 | Pertinencia del método |
| | I2 · Corrección técnica en R (`sf`, `spdep`): CRS, unión, W, permutación | 7 | caps. 2 y 6 | Corrección técnica en R |
| | I3 · Autocorrelación global: Moran por permutación con `nsim` declarado, diagrama de Moran, sensibilidad a las W preregistradas y lectura de la potencia si no es significativo | 8 | cap. 7 (M2–M4, M7) | Corrección técnica · interpretación |
| | I4 · Análisis local: LISA con corrección de multiplicidad y `nsim` que la permita; Gi\* si se usa, leído como intensidad | 7 | cap. 7 (M8–M11) | Corrección técnica · interpretación |
| | I5 · Calidad cartográfica: CRS, clasificación y leyenda declaradas, categorías LISA con sus colores, sin conteos en el coroplético | 6 | caps. 3 y 7 | Calidad cartográfica |
| | I6 · Interpretación en el lenguaje del territorio, con sus límites (MAUP, falacia ecológica, potencia) | 5 | caps. 3 y 7 | Interpretación |
| | I7 · Fidelidad al preregistro y reproducibilidad desde el repositorio | 4 | — | Reproducibilidad |
| | I8 · Declaración de uso de IA con un ejemplo verificado | 3 | sílabo, semana 13 | Declaración del uso de IA |
| Exposición (30) | E1 · La exposición | 12 | | |
| | E2 · Las preguntas (individual; en la conjunta, solo las de Espacial) | 18 | | |
| **Total** | | **100** | | |

Sumas: 4 + 7 + 4 = 15 · 5 + 5 = 10 · 5 + 7 + 8 + 7 + 6 + 5 + 4 + 3 = 45 · 12 + 18 = 30. El auditor las recalcula.

**En la conjunta** la rúbrica es la misma y cambia de qué variable se habla: en (a), la variable espacial es el
MASE por origen móvil de cada unidad; en (b), la ganancia de MASE al añadir Wy. P2, A2, I3 e I4 llevan un
descriptor propio para la conjunta. Lo temporal (el protocolo de pronóstico, el origen móvil, Diebold–Mariano) lo
califica Series y aquí no puntúa: si falta la parte temporal, cae la nota de Series y no la de Espacial.

## 7. La opción conjunta (módulo 8 de la guía): lo que dice y lo que no

Dice, en un párrafo y un recuadro:

1. Que existe, que es para quien curse las dos materias y que **la única fuente de sus reglas es el módulo 8 de la
   guía de Series**, con el enlace.
2. Que la parte espacial se califica con la rúbrica del módulo 10 de esta guía, con los descriptores de la conjunta.
3. Que es la **única** situación en que un mismo trabajo cuenta en dos cursos; fuera de ella, es autoplagio.

No dice (el auditor lo prohíbe, frente H): las preguntas (a) y (b) en detalle, los tamaños (páginas, minutos),
quién puede formar pareja, hasta cuándo se puede cambiar de opción, ni cómo se reparte la defensa. Todo eso está en
Series y una copia aquí se quedaría vieja al primer cambio.

## 8. Estructura de la guía (10 módulos)

| Módulo | Título | Origen |
|---|---|---|
| m1 | Cómo funciona: hitos, entrega tardía, pesos, el tope | Series m1, con las cifras de Espacial y PE1 |
| m2 | Qué datos valen | Nuevo (DE2–DE4, DE8), con la tabla de potencia |
| m3 | El repositorio en GitHub | Series m3, casi tal cual |
| m4 | La ficha | Series m4, adaptado |
| m5 | El preregistro: el protocolo de inferencia espacial | Nuevo (DE6–DE7), con el código de `poly2nb`/`knn2nb`, `nb2listw` y la cuenta de `nsim` |
| m6 | El avance | Nuevo: la unión contada, el mapa exploratorio, la W descrita |
| m7 | El informe: estructura, que corra entero, declaración de IA, los errores que más cuestan | Diseño m7, con los errores de Espacial: distancias en grados, conteos en el coroplético, LISA sin corrección, W elegida después, islas sin declarar |
| m8 | La opción conjunta con Series de Tiempo | §7: el enlace, no las reglas |
| m9 | La exposición | Series m9 |
| m10 | La rúbrica | Desde `datos.py`, con el componente `.rubrica` de la plantilla |

## 9. Tareas

| | Tarea | Tamaño | Depende de |
|---|---|---|---|
| T0 | Cerrar PE1–PE4 con Javier | — | — |
| T1 | `proyecto/datos.py`: calendario, canal, pesos, rúbrica con descriptores, tope, retraso, N mínimo y la tabla de potencia | M | T0 |
| T2 | Los diez módulos en `proyecto/modulos/` | L | T1 |
| T3 | `proyecto/plantilla-informe.Rmd`: secciones que siguen la rúbrica; esqueleto con `sf`, `spdep` y `tmap` (los del material), la unión contada, la W principal y las alternativas, `moran.mc`, `localmoran_perm` con `p.adjust` | M | T1 |
| T4 | `precalculo/ensambla_proyecto.py` sobre la plantilla, con `--revisar` | M | T2 |
| T5 | `precalculo/audita_proyecto.py` y `precalculo/prueba_auditor_proyecto.py`: frentes A (calendario igual al de Series; ningún hito en festivo), B (pesos y sumas; proyecto + PE1 = 100 % del corte), C (decisiones), D (estructura), E (el R de la guía corre en un R limpio y la plantilla renderiza), F (contenido), **G** (cada exigencia de los caps. 2, 3, 6 y 7 tiene su criterio y nada la contradice: `nsim` ≥ 40·N, bilateral, la potencia) y **H** (la conjunta: el enlace al m8 de Series existe y es exacto, y ninguna regla de Series aparece copiada) | L | T4 |
| T6 | Tarjeta en el Corte III de `index.html`, la guía en `cuenta_sitio.py` y en `audita_todo.sh` | S | T4 |
| T7 | Navegador por HTTP: los diez módulos sin errores de consola, KaTeX compuesto, 375 px sin scroll horizontal | S | T5 |
| T8 | Prueba de resistencia a la IA: una entrega fabricada, calificada en frío. El producto **no** se versiona | M | T5 |
| T9 | PR a `main`; **Javier lo fusiona** y con eso queda en Pages; comprobar en el sitio | S | T7 |
| T10 | Avisar a la sesión de Series cuando esté publicada, para que el m8 de Series enlace de vuelta | S | T9 |

## 10. Criterios de aceptación

- `audita_proyecto.py` en verde y el arnés caza todos sus defectos, cada uno con su frente.
- Ninguna cifra de la guía está escrita a mano: todas salen de `datos.py`, y el R de la guía se ejecuta.
- La guía enlaza al módulo 8 de la de Series y no copia sus reglas (frente H).
- La rúbrica está en Pages antes del martes 3 de noviembre.
- `audita_todo.sh` sigue en verde con la guía dentro (salvo el rojo previo del cap. 2, «dprtmnt», que no es de
  esta ronda).

## 11. Riesgos

- **La guía de Series puede salir después.** Si esta guía se publica primero, el enlace al m8 da 404 unos días. Se
  mitiga publicando las dos el mismo día si es posible; si no, el frente H comprueba la forma del enlace y la
  comprobación en vivo se repite cuando Series publique.
- **El tiempo.** Dos días hábiles hasta el viernes 23. Si no se llega, se corre la ficha y no se recorta la
  auditoría; la rúbrica tiene su propio plazo (3 de noviembre).
- **Datos fabricados o reciclados del material.** El docente puede volver a descargar en la fecha de corte
  declarada; DE2 nombra los conjuntos del curso que no valen.
- **Sesiones concurrentes.** El checkout principal está en `claude/diapositivas-cap5` con otra historia; esta ronda
  trabaja en el worktree `.claude/worktrees/proyecto-integrador` (rama `claude/proyecto-integrador`, desde
  `origin/main` 6bf9055). Un worktree nuevo no tiene `datos/` ni `precalculo/cache/` (memoria
  `worktrees-datos-estadistica-espacial`); la guía no los necesita.

## 12. Enlaces

- Series: `../Series de tiempo/PLAN_Proyecto_Pronostico.md` (§4, §5, §7)
- Modelo: `../Diseno de experimentos/PLAN_Proyecto_Aplicado.md` · `../Diseno de experimentos/proyecto/README.md`
- Sílabo: `../Syllabus/20929_Syllabus_Estadistica_Espacial_2026-II.pdf` (semanas 10–16)
- `PLAN_Material_Estadistica_Espacial.md` (D8, T6.4, cap. 10 M11)

## Anexo A · La potencia de §2

```r
library(spdep); set.seed(20929)
pot <- function(lado, rho, R = 400, nsim = 499) {
  lw <- nb2listw(cell2nb(lado, lado, type = "queen"), style = "W")
  A <- solve(diag(lado^2) - rho * listw2mat(lw))
  mean(replicate(R, moran.mc(A %*% rnorm(lado^2), lw, nsim,
                             alternative = "greater")$p.value <= 0.05))
}
```

R 4.4.1 arm64, spdep del proyecto. El tamaño en ρ = 0 oscila entre 0,04 y 0,07 por el error de Monte Carlo de
400 réplicas (±0,02). La tabla publicada sale de `proyecto/potencia.R`, con 2 000 réplicas y N = 25, 36, 49, 64 y 100.
