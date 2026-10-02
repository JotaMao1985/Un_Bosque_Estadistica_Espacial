# Registro de cifras · Capítulo 5 · Sesión 1

Generado por `verifica_cifras_cap5.py` a partir de `capitulo_5_sesion_1.md`. **No se edita a mano**: se regenera.

Recómputo en R del 2026-10-01 (R version 4.4.1 (2024-06-14); spatstat 3.5.1, spatstat.explore 3.8.0, spatstat.model 3.6.1), con `recomputa_cap5.R`.

## Cómo se comprobó cada cifra

| Estado | Qué significa |
|---|---|
| VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo | Se volvió a calcular en R con el mismo código del capítulo y coincide con `cap5_datos.json`, redondeada a los decimales que se muestran. |
| VERIFICADA · re-ejecutada en R | Se calculó en R (`recomputa_cap5.R`); el JSON del capítulo no la trae. |
| VERIFICADA · aritmética sobre cifras verificadas | Se recompone con una cuenta a partir de otras cifras ya verificadas. |
| CONTRASTADA · salida de R (JSON del capítulo) | Coincide con `cap5_datos.json`; no se volvió a calcular aquí. |
| CONTRASTADA · texto del capítulo | Solo figura en la prosa del capítulo publicado o en `FUENTES.md`: la frase existe. |
| REFERENCIA · ficha de ayuda del paquete | Dato de un conjunto o de una referencia (año, n, tamaño de la parcela), cotejado con la ayuda de `spatstat.data`. |
| MEDIDA · depende de la máquina | Un tiempo: se vuelve a medir y se acepta con tolerancia. |
| PARÁMETRO de diseño | Rejillas, semillas, σ elegido, duración: decisiones del capítulo o del docente. |
| **[SIN VERIFICAR]** | No se pudo comprobar. Lleva la marca en la diapositiva y no se presenta como dato confirmado. |

Los enteros 0, 1 y 2 usados como constantes de definición no se registran: no son mediciones.

## Resumen

- 355 apariciones de cifras en 36 diapositivas; 180 cifras distintas.
- VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo: 205
- VERIFICADA · re-ejecutada en R: 54
- PARÁMETRO de diseño: 41
- VERIFICADA · aritmética sobre cifras verificadas: 20
- CONTRASTADA · salida de R (JSON del capítulo): 14
- CONTRASTADA · texto del capítulo: 12
- REFERENCIA · ficha de ayuda del paquete: 6
- MEDIDA · depende de la máquina (con tolerancia): 3

## Hallazgos en el material del capítulo

Discrepancias que aparecieron al cotejar. No son errores de la presentación: se dicen aquí y en las notas, y no se corrigen en silencio.

- **Los mapas ráster salen invertidos verticalmente.** El mapa de calor de Kennedy por σ (módulo 2), la oferta y los estudiantes (módulo 5) y P(oficial) (módulo 6) se dibujan con el sur arriba, mientras los mapas de puntos (módulos 1 y 6) van con el norte arriba. Causa: `geo_rejilla()` (`precalculo/geo.R`) guarda la fila 0 en el sur —la de `spatstat`— y `geomapaPintaRejilla()` (`plantilla-capitulo.html`) pinta la fila 0 arriba; el comentario de `geo_rejilla()` dice «de arriba a abajo, como lo espera el navegador», pero no voltea las filas. Comprobado de dos formas: con las coordenadas de las 2 107 sedes (la superficie vale más donde hay sedes solo si la fila 0 es el sur: 545 contra 457 en la oferta) y midiendo píxeles en la página servida (el punto más alto del ráster está en x = 0.46 y el del mapa de puntos en x = 0.90). El texto del módulo 5 («en el norte y en el suroccidente») es geográficamente correcto, pero el lector del capítulo ve el norte abajo. Estas diapositivas dibujan los mapas de nuevo, con el norte arriba (`recursos/cap5/genera_figuras_s1.R`). El capítulo no se modificó.
- **«0.0 y 24.9 sedes por km²» en la rejilla de 8 × 8.** El módulo 1 (y la retroalimentación de la primera pregunta de la autoevaluación) dice que los cuadrantes dan «entre 0.0 y 24.9 sedes por km²». `genera_cap5.R` calcula `conteo / (A_KEN / 64)`, o sea divide por el área media por celda de la ventana (38.51 / 64 = 0.602 km²). Pero la celda con 15 sedes es una celda interior y mide 0.895 km² (la caja entre 64): son 16.8 sedes por km² (`intensity(cuad)` da 16.757). El 24.9 no es la intensidad de ninguna celda. Además, de las 64 celdas de la rejilla, 7 caen fuera de la ventana y `quadratcount` devuelve 57. Las diapositivas solo dicen «de 0 a 15 sedes por celda».
- **«Por encima de 0.965».** El módulo 2 dice que las superficies de los cuatro núcleos «correlacionan por encima de 0.965 con la gaussiana». El mínimo es el del disco, 0.9647 (0.964743…), que redondea a 0.965 pero está por debajo. Las diapositivas dicen «por encima de 0.96».
- **«Mayoritariamente de ese tipo».** El módulo 6 dice que, donde el mapa es máximo, «los vecinos tienen que ser mayoritariamente de ese tipo». En `chorley` son el 8 % (4 de 50), y la guarda de `genera_cap5.R` compara contra la proporción global (5.6 %), no contra la mitad. Las diapositivas dicen «más que en todo el conjunto».
- **La mediana no mide «en qué fracción de la ciudad son mayoría».** El módulo 6 resume la mediana de la superficie P(oficial) como la respuesta a «¿en qué fracción de la ciudad son mayoría?». La mediana es el valor de la proporción en el punto típico de la ciudad (0.3086), no una fracción del área en la que las oficiales son mayoría. Las diapositivas dicen lo primero.
- **Los tiempos de la KDE están escritos a mano en el generador.** `genera_cap5.R` publica `coste_segundos = list(defecto = 0.15, sin_corregir = 0.14, diggle = 0.15)` como constantes (vienen de la medición A.21 del plan, sobre la ventana urbana a 128 × 128). Se volvieron a medir y dan lo mismo (0.146, 0.138 y 0.150 s), así que la cifra es cierta; solo que el generador no la mide. Aclaración que falta en el módulo 4: son tiempos de la ciudad, no de Kennedy (en Kennedy, a 99 × 96 celdas, son del orden de 0.01 s).
- **Los valores de `bw.ppl` y `bw.CvL` son nodos de una rejilla de 16 anchos, no óptimos (módulo 3).** El módulo 3 presenta `bw.ppl` y `bw.CvL` como selectores que optimizan; en realidad evalúan su criterio en `ns = 16` anchos de una rejilla geométrica y devuelven el mejor de ellos (`recomputo › selectores.ns_ppl`), y `bw.ppl` usa además `shortcut = TRUE`. Con 256 anchos, `bw.ppl` da 326 m en Kennedy y 350 m en la ciudad (no 374.9 y 235.9) y `bw.CvL`, 640 y 877 m (no 556.7 y 720.4) (`recomputo › selectores_fino`). Consecuencias: el cruce entre `bw.ppl` y `bw.diggle` que el capítulo comenta (375 contra 347 m en Kennedy, 236 contra 373 m en la ciudad) es un efecto de la rejilla, porque con rejilla fina `bw.ppl` queda por debajo de `bw.diggle` en las dos ventanas; y las razones 1.83 y 5.30, que usan esos nodos, son del orden de 2.0 y 3.6. Las diapositivas conservan las cifras del capítulo y dicen que son valores por defecto, no repiten «ni el orden se conserva» y llaman a σ = 720 m «el valor por defecto de `bw.CvL`», no «el óptimo». El capítulo no se modificó.
- **«El ancho mueve 13 veces lo que el núcleo» (módulo 2).** La razón 66.3 / 5.1 ≈ 13 compara cuatro formas de núcleo a un solo σ (400 m) con siete σ que abarcan un factor 8, y el 5.1 % no es una constante: a otros σ el núcleo mueve el máximo más o menos. Las diapositivas dan las dos cifras por separado y no la razón.
- **«Si no da n, el estimador pierde o inventa sedes» (módulo 4).** La integral de la intensidad es el número esperado de sedes, no el n de la muestra. Con 300 patrones al azar de 262 sedes en la ventana de Kennedy, la corrección por defecto se desvía de n en promedio +0.017 % (σ = 400 m) y +0.039 % (σ = 800 m), dentro de su error estándar (`recomputo › bordes_csr`): no es sesgada. Sin corregir se pierde un 10.3 % y un 19.6 %. El +3.19 % del patrón real (σ = 800 m) queda a más de cuatro desviaciones típicas de lo que da el azar: es del patrón, no de la corrección. Diggle conserva n por construcción. Las diapositivas dicen que la prueba mide qué conserva cada corrección, no cuál acierta.
- **«Las correlaciones de la versión de Python salen 0.9391, 0.8555 y 0.9155: otra discretización» (módulo 5).** Con la corrección de borde por defecto de `density`, R da exactamente 0.9391, 0.8555 y 0.9155 (`recomputo › capas_defecto`); la versión de Python divide por e(u), que es la corrección por defecto. Las cifras y los mapas del capítulo usan `diggle = TRUE` (0.943, 0.862, 0.919). No es otra discretización: son dos correcciones de borde, ambas correctas. Las diapositivas lo dicen.
- **El máximo de `chorley` vive en la cola (módulo 6).** El capítulo lee el máximo de P(laringe), 0.3389, como titular («uno de cada tres cánceres registrados es de laringe»). El píxel del máximo está a 4.6 km del punto más cercano, con σ = 1 km (el vecino 50.º, a 8.2 km): es el cociente de dos masas casi nulas. La comprobación de los 50 vecinos (4 casos de 50) detecta un mapa invertido, pero no valida el máximo. Las diapositivas no lo leen como riesgo y la figura usa la escala fija de 0 a 1.
- **La corrección de borde «se cancela» en el cociente (módulo 6).** Solo con la corrección por defecto, donde el mismo e(u) divide numerador y denominador; con `diggle = TRUE` cada sede se divide por su propio e(x_i) y no se cancela. Las diapositivas lo dicen así.
- **Los tiempos «555 veces» y «1.07» (módulo 4).** El cociente 122.655 / 0.221 = 555 es una medición de tiempo y depende de la máquina y del momento (al volver a medir salen cientos de veces, no exactamente 555), y el 1.07 sale de dos cifras redondeadas a centésimas (0.15 / 0.14). Las diapositivas dicen «cientos de veces» y «del mismo orden».
- **Kennedy no está contenida en la ventana urbana (módulo 1).** 3 de las 262 sedes de Kennedy y el 9.8 % de su área caen fuera del perímetro urbano (`recomputo › kennedy`): son capas con ventanas distintas, de modo que «Kennedy dentro de la ciudad» es aproximado. Va en las notas.
- **El Quiz 2 cubre los módulos 1 a 4 (módulo 13).** El módulo 13 dice que las preguntas de este capítulo en el Quiz 2 son de los módulos 1 a 4. Las notas de la primera versión de las diapositivas decían que el módulo 5 entraba «en lo que toca a la resolución de la rejilla» y que las ocho preguntas del módulo 12 eran para hacerlas antes del Quiz 2 (cuatro de ellas son de la sesión 2). Corregido en las notas.

## Afirmaciones que no son una cifra, y cómo se comprobaron

Cada una se vuelve a evaluar con el recómputo en R cada vez que se corre el verificador.

- ✓ El máximo de la oferta cae en Suba y el de estudiantes, en Bosa
- ✓ `bw.ppl(japanesepines)` devuelve exactamente la mitad del diámetro de la ventana (el tope de su intervalo)
- ✓ R avisa de que el criterio se maximizó en el extremo derecho del intervalo
- ✓ Con el intervalo ampliado a 2, `bw.ppl` devuelve 2 (otra pared) y el criterio sigue subiendo
- ✓ Con los valores por defecto, `bw.ppl` queda por encima de `bw.diggle` en Kennedy y por debajo en la ciudad (el cruce que comenta el capítulo)
- ✓ Con 256 anchos, `bw.ppl` queda por debajo de `bw.diggle` en las dos ventanas: el cruce es un efecto de la rejilla de 16 anchos
- ✓ `bw.ppl` y `bw.CvL` evalúan su criterio en 16 anchos (`ns = 16`) y `bw.ppl` usa `shortcut = TRUE`
- ✓ El abanico de los selectores se abre más en la ciudad que en Kennedy, también con 256 anchos
- ✓ Sobre 300 patrones al azar de 262 sedes, la corrección por defecto conserva n en promedio (desviación media menor que 0.1 % en valor absoluto) y sin corregir se pierde más del 10 %
- ✓ El +3.19 % de la corrección por defecto en Kennedy (σ = 800 m) queda a más de 3 desviaciones típicas de lo que da el azar
- ✓ Las correlaciones de la versión de Python (0.9391, 0.8555, 0.9155) son las de la corrección de borde por defecto
- ✓ El píxel del máximo de P(laringe) queda a más de 3 km del punto más cercano (con σ = 1 km): es la cola
- ✓ Las oficiales son mayoría (P > 0.5) en menos de una quinta parte del área
- ✓ Kennedy no está contenida en la ventana urbana: parte de sus sedes y de su área caen fuera del perímetro
- ✓ Sobre la ciudad, `bw.diggle` y `bw.ppl` quedan por debajo de 3 celdas (550 m) y `bw.CvL` y `bw.scott`, por encima
- ✓ `bw.CvL` es el más estrecho de los dos selectores que la rejilla de la ciudad puede dibujar
- ✓ Sin corregir, la masa queda por debajo de n y la fuga crece con σ; por defecto, queda por encima y el exceso crece con σ; con diggle es n
- ✓ El pico baja al no corregir (σ = 800 m)
- ✓ Los tres tiempos de la KDE sobre la ciudad son del mismo orden (cociente máximo / mínimo menor que 1.3)
- ✓ La fórmula de Diggle a mano coincide con spatstat (menos de 3 %) y la del defecto, usada en su lugar, no (más de 50 %)
- ✓ La caja que enmarca a Kennedy no es la ventana: su área (7.5 × 7.7 km) es mayor que la de la ventana
- ✓ Sin fijar el orden de niveles, el mapa de chorley es P(pulmón) y el de Bogotá, P(privado): la mediana es el complemento
- ✓ En el máximo de P(laringe) los casos pesan más que en el conjunto, sin ser mayoría (8 % contra 5.6 %)
- ✓ En el máximo de P(oficial) las oficiales pesan más que en el conjunto (64 % contra 33.65 %)
- ✓ La mediana de la superficie P(oficial) queda por debajo de la proporción de los puntos
- ✓ Las tres correlaciones de las capas son menores que 1 y la menor es la de oferta con estudiantes
- ✓ La integral de la KDE ponderada por evaluados da el total de evaluados
- ✓ Ilustración de la lámina 8 (seis puntos, núcleo gaussiano, σ de 0.35 a 1.2): el máximo de la suma baja, en el valle entre los dos grupos sube, y el 10 % más alto baja y la mitad más baja sube
- ✓ Animación del módulo 1 (19 puntos, σ de 0.5 a 2.2, sin corregir el borde), con los cuatro núcleos: del σ más estrecho al más ancho el 10 % más alto de la superficie baja y la mitad más baja sube
- ✓ Animación del módulo 1: con el gaussiano, el epanechnikov y el cuártico el máximo no sube en ningún paso del deslizador de σ; con el disco sube en algunos
- ✓ Con el disco, el máximo sube justo en los pasos en que el mejor círculo alcanza un punto más (el conteo máximo de puntos dentro del círculo aumenta)

## Cifra por cifra

### Diapositiva 1 · Portada

| Cifra | Dónde | Contexto | Comprobación | Estado |
|---|---|---|---|---|
| `90` | cuerpo | …etiqueta: de 2 · 90 min subtitulo: Estimar la int… | duración de la clase pedida por el docente (90 min), decisión D1; no es un dato del capítulo | PARÁMETRO de diseño |

### Diapositiva 3 · De contar a suavizar

| Cifra | Dónde | Contexto | Comprobación | Estado |
|---|---|---|---|---|
| `13` | notas | …Unos 13 minutos. Abrir con la pregunt… | minutos que se asignan a cada bloque de la sesión: decisión del docente, no un dato del capítulo | PARÁMETRO de diseño |
| `5.69` | notas | …o con la definición: ¿qué le falta a «5.69 sedes por km²»? Dejar que d… | recomputo › urbana.lambda_km2 = 5.693212582 \| texto del capítulo: «5.6932» | VERIFICADA · re-ejecutada en R |
| `90` | notas | …del Quiz 2. Presupuesto de la sesión (90 min): este módulo, 13 min; nú… | duración de la clase pedida por el docente (90 min), decisión D1; no es un dato del capítulo | PARÁMETRO de diseño |
| `13` | notas | …o de la sesión (90 min): este módulo, 13 min; núcleo y ancho, 11; sele… | minutos que se asignan a cada bloque de la sesión: decisión del docente, no un dato del capítulo | PARÁMETRO de diseño |
| `11` | notas | …este módulo, 13 min; núcleo y ancho, 11; selectores, 11; corrección d… | minutos que se asignan a cada bloque de la sesión: decisión del docente, no un dato del capítulo | PARÁMETRO de diseño |
| `11` | notas | …min; núcleo y ancho, 11; selectores, 11; corrección de borde, 14; map… | minutos que se asignan a cada bloque de la sesión: decisión del docente, no un dato del capítulo | PARÁMETRO de diseño |
| `14` | notas | …selectores, 11; corrección de borde, 14; mapa de calor, 10; intensida… | minutos que se asignan a cada bloque de la sesión: decisión del docente, no un dato del capítulo | PARÁMETRO de diseño |
| `10` | notas | …rrección de borde, 14; mapa de calor, 10; intensidad relativa, 13; cie… | minutos que se asignan a cada bloque de la sesión: decisión del docente, no un dato del capítulo | PARÁMETRO de diseño |
| `13` | notas | …pa de calor, 10; intensidad relativa, 13; cierre y práctica, 4. El res… | minutos que se asignan a cada bloque de la sesión: decisión del docente, no un dato del capítulo | PARÁMETRO de diseño |
| `4` | notas | …idad relativa, 13; cierre y práctica, 4. El resto es margen para preg… | minutos que se asignan a cada bloque de la sesión: decisión del docente, no un dato del capítulo | PARÁMETRO de diseño |

### Diapositiva 4 · Una sola cifra para toda la ciudad no dice dónde hay más sedes

| Cifra | Dónde | Contexto | Comprobación | Estado |
|---|---|---|---|---|
| `2209` | cuerpo | …ito (SED, vía Datos Abiertos Bogotá): 2 209 sedes, de las que **2 107*… | recomputo › urbana.n_capa = 2209 | VERIFICADA · re-ejecutada en R |
| `2107` | cuerpo | …os Bogotá): 2 209 sedes, de las que **2 107** caen dentro del perímetr… | datos › m5.capas.oferta.n = 2107; recomputo › urbana.n_urbana = 2107 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `2107` | cuerpo | …fórmula: \hat\lambda = \frac{n}{\|W\|} = \frac{2\,107}{370.09\ \text{k… | datos › m5.capas.oferta.n = 2107; recomputo › urbana.n_urbana = 2107 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `370.09` | cuerpo | …fórmula: \hat\lambda = \frac{n}{\|W\|} = \frac{2\,107}{370.09\ \text{k… | recomputo › urbana.area_km2 = 370.0898165 | VERIFICADA · re-ejecutada en R |
| `5.69` | cuerpo | …fórmula: \hat\lambda = \frac{n}{\|W\|} = \frac{2\,107}{370.09\ \text{k… | recomputo › urbana.lambda_km2 = 5.693212582 \| texto del capítulo: «5.6932» | VERIFICADA · re-ejecutada en R |
| `2209` | notas | …: n entre el área de la ventana. Los 2 209 menos los 2 107 son sedes q… | recomputo › urbana.n_capa = 2209 | VERIFICADA · re-ejecutada en R |
| `2107` | notas | …ea de la ventana. Los 2 209 menos los 2 107 son sedes que caen fuera d… | datos › m5.capas.oferta.n = 2107; recomputo › urbana.n_urbana = 2107 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `12.25` | notas | …rural del D.C. La capa es la versión 12.25 de la SED y las coordenadas… | texto del capítulo: «versión 12.25» | CONTRASTADA · texto del capítulo |
| `9377` | notas | …a SED y las coordenadas están en EPSG:9377. Pregunta para el grupo: ¿q… | texto del capítulo: «EPSG:9377» | CONTRASTADA · texto del capítulo |

### Diapositiva 5 · Kennedy: 262 sedes en 38.51 km², con un contorno y no con una caja

| Cifra | Dónde | Contexto | Comprobación | Estado |
|---|---|---|---|---|
| `262` | titulo | …Kennedy: 262 sedes en 38.51 km², con un co… | datos › m1.ventana.n = 262; recomputo › kennedy.n = 262 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `38.51` | titulo | …Kennedy: 262 sedes en 38.51 km², con un contorno y no con… | datos › m1.ventana.area_km2 = 38.51281483; recomputo › kennedy.area_km2 = 38.51281483 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `262` | cuerpo | …ige después. ::: ::: info Dato = **262** · = **38.51 km²** · = 2… | datos › m1.ventana.n = 262; recomputo › kennedy.n = 262 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `38.51` | cuerpo | …:: ::: info Dato = **262** · = **38.51 km²** · = 262 / 38.51 = **6… | datos › m1.ventana.area_km2 = 38.51281483; recomputo › kennedy.area_km2 = 38.51281483 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `262` | cuerpo | …= **262** · = **38.51 km²** · = 262 / 38.51 = **6.80** por km². :… | datos › m1.ventana.n = 262; recomputo › kennedy.n = 262 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `38.51` | cuerpo | …262** · = **38.51 km²** · = 262 / 38.51 = **6.80** por km². ::: :::… | datos › m1.ventana.area_km2 = 38.51281483; recomputo › kennedy.area_km2 = 38.51281483 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `6.80` | cuerpo | …= **38.51 km²** · = 262 / 38.51 = **6.80** por km². ::: ::: warn Crit… | datos › m1.ventana.lambda_km2 = 6.802930432; recomputo › kennedy.lambda_km2 = 6.802930431 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `7.5` | notas | …a. La caja que enmarca a Kennedy mide 7.5 7.7 km; la ventana es el con… | datos › m1.ventana.caja_x_km = 7.468635735; recomputo › kennedy.caja_x_km = 7.468635735 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `7.7` | notas | …a caja que enmarca a Kennedy mide 7.5 7.7 km; la ventana es el contorn… | datos › m1.ventana.caja_y_km = 7.670678398; recomputo › kennedy.caja_y_km = 7.670678398 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `261` | notas | …, no la caja. Por el atributo salen 261 sedes y por la geometría, 262… | datos › m1.frontera.n_atributo = 261; recomputo › kennedy.n_atributo = 261 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `262` | notas | …salen 261 sedes y por la geometría, 262: las tres sedes de diferencia… | datos › m1.ventana.n = 262; recomputo › kennedy.n = 262 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `87` | notas | …sedes de diferencia están a menos de 87 m del borde («Debora Arango P… | datos › m1.frontera.dist_max_m = 86.55737769 | CONTRASTADA · salida de R (JSON del capítulo) |
| `3` | notas | …está contenida en la ventana urbana: 3 de sus 262 sedes y el 9.8 % d… | recomputo › kennedy.sedes_fuera_de_la_urbana = 3 | VERIFICADA · re-ejecutada en R |
| `262` | notas | …tenida en la ventana urbana: 3 de sus 262 sedes y el 9.8 % de su área … | datos › m1.ventana.n = 262; recomputo › kennedy.n = 262 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `9.8` | notas | …ntana urbana: 3 de sus 262 sedes y el 9.8 % de su área caen fuera del … | recomputo › kennedy.area_fuera_de_la_urbana_pct = 9.8417205 | VERIFICADA · re-ejecutada en R |

### Diapositiva 6 · Contar en cuadrantes ya estima la intensidad local, con dos defectos

| Cifra | Dónde | Contexto | Comprobación | Estado |
|---|---|---|---|---|
| `8x8` | cuerpo | …Kennedy con una rejilla de 8 × 8 y con la misma rejilla movida… | datos › m1.cuadrantes.nx = 8 \| recomputo › cuadrantes.nx = 8 | VERIFICADA · re-ejecutada en R |
| `8x8` | cuerpo | …opia. \|\|\| ::: info Dato Rejilla de 8 × 8: de **0** a **15** sedes p… | datos › m1.cuadrantes.nx = 8 \| recomputo › cuadrantes.nx = 8 | VERIFICADA · re-ejecutada en R |
| `15` | cuerpo | …info Dato Rejilla de : de **0** a **15** sedes por celda. Movida en… | datos › m1.cuadrantes.conteo_max = 15; recomputo › cuadrantes.conteo_max = 15 \| recomputo › cuadrantes.rango_desplazados[0] = 15 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `16` | cuerpo | …celda. Movida en pasos de ¼ de celda (16 posiciones), la celda más lle… | recomputo › cuadrantes.desplazamientos = 16 | VERIFICADA · re-ejecutada en R |
| `15` | cuerpo | …es), la celda más llena tiene entre **15 y 21**. ::: ::: tip Interpre… | datos › m1.cuadrantes.conteo_max = 15; recomputo › cuadrantes.conteo_max = 15 \| recomputo › cuadrantes.rango_desplazados[0] = 15 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `21` | cuerpo | …la celda más llena tiene entre **15 y 21**. ::: ::: tip Interpretació… | recomputo › cuadrantes.rango_desplazados[1] = 21 | VERIFICADA · re-ejecutada en R |
| `15` | cuerpo | …l moverla, la celda más llena pasa de 15 a 21. **2.** Una línea corta… | datos › m1.cuadrantes.conteo_max = 15; recomputo › cuadrantes.conteo_max = 15 \| recomputo › cuadrantes.rango_desplazados[0] = 15 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `21` | cuerpo | …erla, la celda más llena pasa de 15 a 21. **2.** Una línea corta la ve… | recomputo › cuadrantes.rango_desplazados[1] = 21 | VERIFICADA · re-ejecutada en R |
| `10` | cuerpo | …a línea corta la vecindad: una sede a 10 m, al otro lado, no aporta. :… | distancia ilustrativa del texto del capítulo («aunque esté a diez metros») \| texto del capítulo: «a diez metros» | CONTRASTADA · texto del capítulo |
| `64` | notas | …lo, el bloque del usa y . De las 64 celdas de la rejilla, 7 caen… | datos › m1.cuadrantes.n_celdas = 64; recomputo › cuadrantes.celdas_rejilla = 64 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `7` | notas | …y . De las 64 celdas de la rejilla, 7 caen fuera de la ventana. El… | 64 celdas de la rejilla − 57 con ventana = 7 | VERIFICADA · aritmética sobre cifras verificadas |
| `15` | notas | …jilla, 7 caen fuera de la ventana. El 15 sale dos veces. La cifra «ent… | datos › m1.cuadrantes.conteo_max = 15; recomputo › cuadrantes.conteo_max = 15 \| recomputo › cuadrantes.rango_desplazados[0] = 15 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `15` | notas | …El 15 sale dos veces. La cifra «entre 15 y 21» no está en el capítulo:… | datos › m1.cuadrantes.conteo_max = 15; recomputo › cuadrantes.conteo_max = 15 \| recomputo › cuadrantes.rango_desplazados[0] = 15 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `21` | notas | …sale dos veces. La cifra «entre 15 y 21» no está en el capítulo: se m… | recomputo › cuadrantes.rango_desplazados[1] = 21 | VERIFICADA · re-ejecutada en R |
| `21` | notas | …en y, y contando de nuevo; el máximo, 21, lo da un desplazamiento de m… | recomputo › cuadrantes.rango_desplazados[1] = 21 | VERIFICADA · re-ejecutada en R |

### Diapositiva 8 · Cada sede pone una loma; el mapa es su suma, y σ decide qué tan anchas son

| Cifra | Dónde | Contexto | Comprobación | Estado |
|---|---|---|---|---|
| `1.2` | cuerpo | …siciones inventadas en una dimensión (1.2, 1.9, 2.3, 6.5, 7.9 y 8.4), … | genera_figuras_s1.R › x_j = [1.2, 1.9, 2.3, 6.5, 7.9, 8.4] | PARÁMETRO de diseño |
| `1.9` | cuerpo | …nes inventadas en una dimensión (1.2, 1.9, 2.3, 6.5, 7.9 y 8.4), con n… | genera_figuras_s1.R › x_j = [1.2, 1.9, 2.3, 6.5, 7.9, 8.4] | PARÁMETRO de diseño |
| `2.3` | cuerpo | …nventadas en una dimensión (1.2, 1.9, 2.3, 6.5, 7.9 y 8.4), con núcleo… | genera_figuras_s1.R › x_j = [1.2, 1.9, 2.3, 6.5, 7.9, 8.4] | PARÁMETRO de diseño |
| `6.5` | cuerpo | …adas en una dimensión (1.2, 1.9, 2.3, 6.5, 7.9 y 8.4), con núcleo gaus… | genera_figuras_s1.R › x_j = [1.2, 1.9, 2.3, 6.5, 7.9, 8.4] | PARÁMETRO de diseño |
| `7.9` | cuerpo | …en una dimensión (1.2, 1.9, 2.3, 6.5, 7.9 y 8.4), con núcleo gaussiano… | genera_figuras_s1.R › x_j = [1.2, 1.9, 2.3, 6.5, 7.9, 8.4] | PARÁMETRO de diseño |
| `8.4` | cuerpo | …dimensión (1.2, 1.9, 2.3, 6.5, 7.9 y 8.4), con núcleo gaussiano. **Por… | genera_figuras_s1.R › x_j = [1.2, 1.9, 2.3, 6.5, 7.9, 8.4] | PARÁMETRO de diseño |

### Diapositiva 10 · ¿Qué dos cosas le arregla el estimador por núcleos al conteo por cuadrantes?

| Cifra | Dónde | Contexto | Comprobación | Estado |
|---|---|---|---|---|
| `15` | cuerpo | …rejilla cambió la celda más llena de 15 a 21; el núcleo no tiene reji… | datos › m1.cuadrantes.conteo_max = 15; recomputo › cuadrantes.conteo_max = 15 \| recomputo › cuadrantes.rango_desplazados[0] = 15 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `21` | cuerpo | …lla cambió la celda más llena de 15 a 21; el núcleo no tiene rejilla,… | recomputo › cuadrantes.rango_desplazados[1] = 21 | VERIFICADA · re-ejecutada en R |

### Diapositiva 11 · Núcleo y ancho de banda: dos decisiones

| Cifra | Dónde | Contexto | Comprobación | Estado |
|---|---|---|---|---|
| `11` | notas | …Unos 11 minutos. Este módulo es mater… | minutos que se asignan a cada bloque de la sesión: decisión del docente, no un dato del capítulo | PARÁMETRO de diseño |

### Diapositiva 12 · Antes de medir: ¿cuánto mueve el máximo cambiar el núcleo, y cuánto cambiar el ancho?

| Cifra | Dónde | Contexto | Comprobación | Estado |
|---|---|---|---|---|
| `262` | cuerpo | …Mismas 262 sedes de Kennedy. Cambiamos *… | datos › m1.ventana.n = 262; recomputo › kennedy.n = 262 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `400` | cuerpo | …- **el núcleo**: , , y , con = 400 m fijo; - **el ancho**: un so… | datos › m2.sigma_m = 400; recomputo › nucleos.sigma_m = 400 \| datos › m4.sigmas_m = [200, 400, 800] | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `233` | cuerpo | …o núcleo ( ) y siete valores de , de 233 a 1867 m. Los dos igual: cada… | datos › m2.familia.sigmas_m[0] = 233.3949; recomputo › anchos.sigmas_m[0] = 233.3949 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `1867` | cuerpo | …eo ( ) y siete valores de , de 233 a 1867 m. Los dos igual: cada decis… | datos › m2.familia.sigmas_m[6] = 1867.1589; recomputo › anchos.sigmas_m[6] = 1867.1589 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `30` | cuerpo | …decisión mueve el máximo en torno al 30 %. El núcleo mueve el máximo… | opciones de la apuesta que se le pide al grupo antes de revelar (órdenes de magnitud); no son datos | PARÁMETRO de diseño |
| `60` | cuerpo | …al 30 %. El núcleo mueve el máximo un 60 % y el ancho, un 5 %. El núcl… | opciones de la apuesta que se le pide al grupo antes de revelar (órdenes de magnitud); no son datos | PARÁMETRO de diseño |
| `5` | cuerpo | …ueve el máximo un 60 % y el ancho, un 5 %. El núcleo mueve el máximo… | opciones de la apuesta que se le pide al grupo antes de revelar (órdenes de magnitud); no son datos | PARÁMETRO de diseño |
| `5` | cuerpo | …un 5 %. El núcleo mueve el máximo un 5 % y el ancho, un 60 %. Ningun… | opciones de la apuesta que se le pide al grupo antes de revelar (órdenes de magnitud); no son datos | PARÁMETRO de diseño |
| `60` | cuerpo | …mueve el máximo un 5 % y el ancho, un 60 %. Ninguna de las dos pasa de… | opciones de la apuesta que se le pide al grupo antes de revelar (órdenes de magnitud); no son datos | PARÁMETRO de diseño |
| `10` | cuerpo | …un 60 %. Ninguna de las dos pasa del 10 %. ::: respuesta : el ancho… | opciones de la apuesta que se le pide al grupo antes de revelar (órdenes de magnitud); no son datos | PARÁMETRO de diseño |
| `5.1` | cuerpo | …iapositivas siguientes: el núcleo, un 5.1 %; el ancho, un 66.3 %. :::… | datos › m2.nucleos.max_dif_pct = 5.061632935; recomputo › nucleos.dif_pct = 5.061632935 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `66.3` | cuerpo | …es: el núcleo, un 5.1 %; el ancho, un 66.3 %. ::: Fuente: del capítu… | datos › m2.familia.caida_pct = 66.2912081; recomputo › anchos.caida_pct = 66.2912081 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |

### Diapositiva 13 · Cambiar el núcleo mueve el máximo solo un 5.1 %

| Cifra | Dónde | Contexto | Comprobación | Estado |
|---|---|---|---|---|
| `5.1` | titulo | …iar el núcleo mueve el máximo solo un 5.1 %… | datos › m2.nucleos.max_dif_pct = 5.061632935; recomputo › nucleos.dif_pct = 5.061632935 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `262` | cuerpo | …::: info Dato · Kennedy, 262 sedes \| Núcleo (σ = 400 m) \|… | datos › m1.ventana.n = 262; recomputo › kennedy.n = 262 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `400` | cuerpo | …to · Kennedy, 262 sedes \| Núcleo (σ = 400 m) \| Máximo (por km²) \| C… | datos › m2.sigma_m = 400; recomputo › nucleos.sigma_m = 400 \| datos › m4.sigmas_m = [200, 400, 800] | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `18.45` | cuerpo | …on el gaussiano \| \|---\|---\|---\| \| \| 18.45 \| — \| \| \| 17.51 \… | datos › m2.nucleos.max_km2.gaussian = 18.44827687; recomputo › nucleos.max_km2.gaussian = 18.44827687 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `17.51` | cuerpo | …\|---\|---\|---\| \| \| 18.45 \| — \| \| \| 17.51 \| 0.9911 \| \| \| 1… | datos › m2.nucleos.max_km2.epanechnikov = 17.51449282; recomputo › nucleos.max_km2.epanechnikov = 17.51449282 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `0.9911` | cuerpo | …\|---\| \| \| 18.45 \| — \| \| \| 17.51 \| 0.9911 \| \| \| 17.69 \| 0.… | datos › m2.nucleos.cor_con_gaussiano.epanechnikov = 0.9910989206; recomputo › nucleos.cor_gauss.epanechnikov = 0.9910989206 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `17.69` | cuerpo | …45 \| — \| \| \| 17.51 \| 0.9911 \| \| \| 17.69 \| 0.9958 \| \| \| 17.… | datos › m2.nucleos.max_km2.quartic = 17.69000883; recomputo › nucleos.max_km2.quartic = 17.69000883 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `0.9958` | cuerpo | …\| \| 17.51 \| 0.9911 \| \| \| 17.69 \| 0.9958 \| \| \| 17.88 \| 0.964… | datos › m2.nucleos.cor_con_gaussiano.quartic = 0.9957546096; recomputo › nucleos.cor_gauss.quartic = 0.9957546096 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `17.88` | cuerpo | …0.9911 \| \| \| 17.69 \| 0.9958 \| \| \| 17.88 \| 0.9647 \| (18.45 − 1… | datos › m2.nucleos.max_km2.disc = 17.88081906; recomputo › nucleos.max_km2.disc = 17.88081906 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `0.9647` | cuerpo | …\| \| 17.69 \| 0.9958 \| \| \| 17.88 \| 0.9647 \| (18.45 − 17.51) / 18… | datos › m2.nucleos.cor_con_gaussiano.disc = 0.964743573; recomputo › nucleos.cor_gauss.disc = 0.964743573 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `18.45` | cuerpo | …9 \| 0.9958 \| \| \| 17.88 \| 0.9647 \| (18.45 − 17.51) / 18.45 = **5.… | datos › m2.nucleos.max_km2.gaussian = 18.44827687; recomputo › nucleos.max_km2.gaussian = 18.44827687 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `17.51` | cuerpo | …58 \| \| \| 17.88 \| 0.9647 \| (18.45 − 17.51) / 18.45 = **5.1 %**: má… | datos › m2.nucleos.max_km2.epanechnikov = 17.51449282; recomputo › nucleos.max_km2.epanechnikov = 17.51449282 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `18.45` | cuerpo | …\| 17.88 \| 0.9647 \| (18.45 − 17.51) / 18.45 = **5.1 %**: máximo meno… | datos › m2.nucleos.max_km2.gaussian = 18.44827687; recomputo › nucleos.max_km2.gaussian = 18.44827687 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `5.1` | cuerpo | …0.9647 \| (18.45 − 17.51) / 18.45 = **5.1 %**: máximo menos mínimo, so… | datos › m2.nucleos.max_dif_pct = 5.061632935; recomputo › nucleos.dif_pct = 5.061632935 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `0.96` | cuerpo | …perficies correlacionan por encima de 0.96 con la gaussiana: para quie… | la menor de las tres correlaciones (0.9647) supera 0.96 = 0.96 | VERIFICADA · aritmética sobre cifras verificadas |
| `18.4483` | notas | …Cifras del (18.4483, 17.5145, 17.6900 y 17.8808 p… | datos › m2.nucleos.max_km2.gaussian = 18.44827687; recomputo › nucleos.max_km2.gaussian = 18.44827687 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `17.5145` | notas | …Cifras del (18.4483, 17.5145, 17.6900 y 17.8808 por km²; e… | datos › m2.nucleos.max_km2.epanechnikov = 17.51449282; recomputo › nucleos.max_km2.epanechnikov = 17.51449282 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `17.6900` | notas | …Cifras del (18.4483, 17.5145, 17.6900 y 17.8808 por km²; el 5.1 % e… | datos › m2.nucleos.max_km2.quartic = 17.69000883; recomputo › nucleos.max_km2.quartic = 17.69000883 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `17.8808` | notas | …as del (18.4483, 17.5145, 17.6900 y 17.8808 por km²; el 5.1 % es 5.061… | datos › m2.nucleos.max_km2.disc = 17.88081906; recomputo › nucleos.max_km2.disc = 17.88081906 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `5.1` | notas | …7.5145, 17.6900 y 17.8808 por km²; el 5.1 % es 5.0616 % sin redondear)… | datos › m2.nucleos.max_dif_pct = 5.061632935; recomputo › nucleos.dif_pct = 5.061632935 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `5.0616` | notas | …7.6900 y 17.8808 por km²; el 5.1 % es 5.0616 % sin redondear). El capí… | datos › m2.nucleos.max_dif_pct = 5.061632935; recomputo › nucleos.dif_pct = 5.061632935 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `0.965` | notas | …ear). El capítulo dice «por encima de 0.965», pero el disco da 0.9647:… | texto del capítulo: «por encima de 0.965» | CONTRASTADA · texto del capítulo |
| `0.9647` | notas | …or encima de 0.965», pero el disco da 0.9647: aquí se dice 0.96. La ad… | datos › m2.nucleos.cor_con_gaussiano.disc = 0.964743573; recomputo › nucleos.cor_gauss.disc = 0.964743573 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `0.96` | notas | …pero el disco da 0.9647: aquí se dice 0.96. La advertencia del recuadr… | la menor de las tres correlaciones (0.9647) supera 0.96 = 0.96 | VERIFICADA · aritmética sobre cifras verificadas |
| `5.1` | notas | …na sola sede y cada uno integra 1. El 5.1 % es a un solo σ, 400 m: a o… | datos › m2.nucleos.max_dif_pct = 5.061632935; recomputo › nucleos.dif_pct = 5.061632935 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `400` | notas | …o integra 1. El 5.1 % es a un solo σ, 400 m: a otros σ el núcleo mueve… | datos › m2.sigma_m = 400; recomputo › nucleos.sigma_m = 400 \| datos › m4.sigmas_m = [200, 400, 800] | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |

### Diapositiva 14 · El ancho sí manda: el máximo cae de 29.5 a 9.9 sedes por km² al abrir σ

| Cifra | Dónde | Contexto | Comprobación | Estado |
|---|---|---|---|---|
| `29.5` | titulo | …El ancho sí manda: el máximo cae de 29.5 a 9.9 sedes por km² al abrir… | datos › m2.familia.max_km2[0] = 29.50660117; recomputo › anchos.picos_km2[0] = 29.50660117 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `9.9` | titulo | …cho sí manda: el máximo cae de 29.5 a 9.9 sedes por km² al abrir σ… | datos › m2.familia.max_km2[6] = 9.946318785; recomputo › anchos.picos_km2[6] = 9.946318785 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `96x99` | cuerpo | …Fuente: del capítulo · rejilla de 96 × 99 celdas de 78 m.… | datos › m2.familia.nx × ny = 96x99 | PARÁMETRO de diseño |
| `262` | cuerpo | …de banda \|\|\| ::: info Dato Kennedy, 262 sedes, núcleo gaussiano, si… | datos › m1.ventana.n = 262; recomputo › kennedy.n = 262 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `233` | cuerpo | …es, núcleo gaussiano, siete anchos de 233 a 1867 m (de uno a otro, ×8)… | datos › m2.familia.sigmas_m[0] = 233.3949; recomputo › anchos.sigmas_m[0] = 233.3949 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `1867` | cuerpo | …cleo gaussiano, siete anchos de 233 a 1867 m (de uno a otro, ×8). (29.… | datos › m2.familia.sigmas_m[6] = 1867.1589; recomputo › anchos.sigmas_m[6] = 1867.1589 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `8` | cuerpo | …chos de 233 a 1867 m (de uno a otro, ×8). (29.507 − 9.946) / 29.507 =… | 100 × orientación del máximo de chorley = 8 \| 100 × vecinos casos / 50 = 8 | VERIFICADA · aritmética sobre cifras verificadas |
| `29.507` | cuerpo | …de 233 a 1867 m (de uno a otro, ×8). (29.507 − 9.946) / 29.507 = **66.… | datos › m2.familia.max_km2[0] = 29.50660117; recomputo › anchos.picos_km2[0] = 29.50660117 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `9.946` | cuerpo | …1867 m (de uno a otro, ×8). (29.507 − 9.946) / 29.507 = **66.3 %**. El… | datos › m2.familia.max_km2[6] = 9.946318785; recomputo › anchos.picos_km2[6] = 9.946318785 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `29.507` | cuerpo | …e uno a otro, ×8). (29.507 − 9.946) / 29.507 = **66.3 %**. El núcleo, … | datos › m2.familia.max_km2[0] = 29.50660117; recomputo › anchos.picos_km2[0] = 29.50660117 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `66.3` | cuerpo | …o, ×8). (29.507 − 9.946) / 29.507 = **66.3 %**. El núcleo, a σ = 400 m… | datos › m2.familia.caida_pct = 66.2912081; recomputo › anchos.caida_pct = 66.2912081 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `400` | cuerpo | …29.507 = **66.3 %**. El núcleo, a σ = 400 m, movía un 5.1 %. ::: ::: w… | datos › m2.sigma_m = 400; recomputo › nucleos.sigma_m = 400 \| datos › m4.sigmas_m = [200, 400, 800] | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `5.1` | cuerpo | …%**. El núcleo, a σ = 400 m, movía un 5.1 %. ::: ::: warn Criterio Ele… | datos › m2.nucleos.max_dif_pct = 5.061632935; recomputo › nucleos.dif_pct = 5.061632935 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `78` | cuerpo | …del capítulo · rejilla de celdas de 78 m.… | datos › m2.familia.celda_m = 77.7982889; recomputo › anchos.celda_x_m = 77.7982889 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `29.5` | notas | …s están en el bloque de R del módulo (29.5, 21.6, 16.8, 13.8, 11.9, 10… | datos › m2.familia.max_km2[0] = 29.50660117; recomputo › anchos.picos_km2[0] = 29.50660117 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `21.6` | notas | …n en el bloque de R del módulo (29.5, 21.6, 16.8, 13.8, 11.9, 10.9, 9.… | datos › m2.familia.max_km2[1] = 21.58264186; recomputo › anchos.picos_km2[1] = 21.58264186 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `16.8` | notas | …l bloque de R del módulo (29.5, 21.6, 16.8, 13.8, 11.9, 10.9, 9.9) y c… | datos › m2.familia.max_km2[2] = 16.84157429; recomputo › anchos.picos_km2[2] = 16.84157429 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `13.8` | notas | …ue de R del módulo (29.5, 21.6, 16.8, 13.8, 11.9, 10.9, 9.9) y cada an… | datos › m2.familia.max_km2[3] = 13.83396896; recomputo › anchos.picos_km2[3] = 13.83396896 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `11.9` | notas | …R del módulo (29.5, 21.6, 16.8, 13.8, 11.9, 10.9, 9.9) y cada ancho es… | datos › m2.familia.max_km2[4] = 11.94975374; recomputo › anchos.picos_km2[4] = 11.94975374 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `10.9` | notas | …módulo (29.5, 21.6, 16.8, 13.8, 11.9, 10.9, 9.9) y cada ancho es √2 ve… | datos › m2.familia.max_km2[5] = 10.85733774; recomputo › anchos.picos_km2[5] = 10.85733774 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `9.9` | notas | …(29.5, 21.6, 16.8, 13.8, 11.9, 10.9, 9.9) y cada ancho es √2 veces el… | datos › m2.familia.max_km2[6] = 9.946318785; recomputo › anchos.picos_km2[6] = 9.946318785 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `66.3` | notas | …ada ancho es √2 veces el anterior. El 66.3 % es 66.291 % sin redondear… | datos › m2.familia.caida_pct = 66.2912081; recomputo › anchos.caida_pct = 66.2912081 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `66.291` | notas | …es √2 veces el anterior. El 66.3 % es 66.291 % sin redondear; con las … | datos › m2.familia.caida_pct = 66.2912081; recomputo › anchos.caida_pct = 66.2912081 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `66.4` | notas | …fras redondeadas a un decimal saldría 66.4 %, por eso la cuenta usa tr… | recomputo › anchos.caida_con_redondeo_1dec = 66.44067797 | VERIFICADA · re-ejecutada en R |
| `8` | notas | …lo σ y el ancho abarca un abanico de ×8. El capítulo dice que el anch… | 100 × orientación del máximo de chorley = 8 \| 100 × vecinos casos / 50 = 8 | VERIFICADA · aritmética sobre cifras verificadas |
| `13` | notas | …El capítulo dice que el ancho mueve «13 veces» lo que el núcleo; esa… | recomputo › anchos.veces_el_nucleo = 13.09680274 | VERIFICADA · re-ejecutada en R |

### Diapositiva 15 · Con σ pequeño ves sedes concretas; con σ grande, una sola mancha

| Cifra | Dónde | Contexto | Comprobación | Estado |
|---|---|---|---|---|
| `233` | cuerpo | …Kennedy con σ = 233, 660 y 1867 m \|\|\| ::: tip I… | datos › m2.familia.sigmas_m[0] = 233.3949; recomputo › anchos.sigmas_m[0] = 233.3949 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `660` | cuerpo | …Kennedy con σ = 233, 660 y 1867 m \|\|\| ::: tip Interp… | datos › m2.familia.sigmas_m[3] = 660.1404; recomputo › anchos.sigmas_m[3] = 660.1404 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `1867` | cuerpo | …Kennedy con σ = 233, 660 y 1867 m \|\|\| ::: tip Interpretació… | datos › m2.familia.sigmas_m[6] = 1867.1589; recomputo › anchos.sigmas_m[6] = 1867.1589 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `233` | cuerpo | …\|\|\| ::: tip Interpretación Con σ = 233 m los focos son sedes concre… | datos › m2.familia.sigmas_m[0] = 233.3949; recomputo › anchos.sigmas_m[0] = 233.3949 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `660` | cuerpo | …m los focos son sedes concretas; con 660 m aparecen zonas; con 1867 m… | datos › m2.familia.sigmas_m[3] = 660.1404; recomputo › anchos.sigmas_m[3] = 660.1404 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `1867` | cuerpo | …cretas; con 660 m aparecen zonas; con 1867 m queda una mancha que no d… | datos › m2.familia.sigmas_m[6] = 1867.1589; recomputo › anchos.sigmas_m[6] = 1867.1589 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `233` | cuerpo | …una mancha que no distingue barrios. 233 m son **tres celdas** de 78 m… | datos › m2.familia.sigmas_m[0] = 233.3949; recomputo › anchos.sigmas_m[0] = 233.3949 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `78` | cuerpo | …barrios. 233 m son **tres celdas** de 78 m: el mínimo para ver el núcl… | datos › m2.familia.celda_m = 77.7982889; recomputo › anchos.celda_x_m = 77.7982889 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `262` | cuerpo | …:: Fuente: del capítulo. Kennedy, 262 sedes, **una sola escala de c… | datos › m1.ventana.n = 262; recomputo › kennedy.n = 262 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |

### Diapositiva 16 · Selectores de ancho de banda

| Cifra | Dónde | Contexto | Comprobación | Estado |
|---|---|---|---|---|
| `11` | notas | …Unos 11 minutos. Materia del Quiz 2.… | minutos que se asignan a cada bloque de la sesión: decisión del docente, no un dato del capítulo | PARÁMETRO de diseño |

### Diapositiva 17 · Cada selector le pregunta algo distinto al patrón (y uno, nada)

| Cifra | Dónde | Contexto | Comprobación | Estado |
|---|---|---|---|---|
| `262` | cuerpo | …::: info Dato · Kennedy (262 sedes) y ciudad (2 107 sedes)… | datos › m1.ventana.n = 262; recomputo › kennedy.n = 262 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `2107` | cuerpo | …Dato · Kennedy (262 sedes) y ciudad (2 107 sedes) Ancho de banda elegi… | datos › m5.capas.oferta.n = 2107; recomputo › urbana.n_urbana = 2107 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `347.1` | cuerpo | …ón cruzada · **mira la superficie** \| 347.1 \| 373.2 \| \| \| la vero… | datos › m3.kennedy.sigmas_m.diggle = 347.1234808; recomputo › selectores.kennedy.sigmas_m.diggle = 347.1234808 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `373.2` | cuerpo | …da · **mira la superficie** \| 347.1 \| 373.2 \| \| \| la verosimilitu… | datos › m3.urbana.sigmas_m.diggle = 373.2167541; recomputo › selectores.ciudad.sigmas_m.diggle = 373.2167541 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `374.9` | cuerpo | …uera cada vez · **mira los puntos** \| 374.9 \| 235.9 \| \| \| que la … | datos › m3.kennedy.sigmas_m.ppl = 374.8988349; recomputo › selectores.kennedy.sigmas_m.ppl = 374.8988349 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `235.9` | cuerpo | …a vez · **mira los puntos** \| 374.9 \| 235.9 \| \| \| que la suma de … | datos › m3.urbana.sigmas_m.ppl = 235.899711; recomputo › selectores.ciudad.sigmas_m.ppl = 235.899711 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `556.7` | cuerpo | …ea de la ventana · **mira el área** \| 556.7 \| 720.4 \| \| \| nada: r… | datos › m3.kennedy.sigmas_m.CvL = 556.7370108; recomputo › selectores.kennedy.sigmas_m.CvL = 556.7370108 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `720.4` | cuerpo | …ventana · **mira el área** \| 556.7 \| 720.4 \| \| \| nada: regla de r… | datos › m3.urbana.sigmas_m.CvL = 720.3691455; recomputo › selectores.ciudad.sigmas_m.CvL = 720.3691455 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `633.6` | cuerpo | …r · **mira solo la dispersión y n** \| 633.6 \| 1251.3 \| ::: ::: tip … | datos › m3.kennedy.sigmas_m.scott = 633.5581067; recomputo › selectores.kennedy.sigmas_m.scott = 633.5581067 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `1251.3` | cuerpo | …ra solo la dispersión y n** \| 633.6 \| 1251.3 \| ::: ::: tip Interpre… | datos › m3.urbana.sigmas_m.scott = 1251.284373; recomputo › selectores.ciudad.sigmas_m.scott = 1251.284373 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `16` | notas | …e un continuo; evalúan su criterio en 16 anchos de una rejilla geométr… | recomputo › selectores.ns_ppl = 16 | VERIFICADA · re-ejecutada en R |
| `256` | notas | …e esa rejilla y no óptimos finos: con 256 anchos, da 326 m en Kennedy… | recomputo › selectores_fino.ns = 256 | VERIFICADA · re-ejecutada en R |
| `326` | notas | …o óptimos finos: con 256 anchos, da 326 m en Kennedy y 350 m en la ci… | recomputo › selectores_fino.kennedy.ppl = 326.0628978 | VERIFICADA · re-ejecutada en R |
| `350` | notas | …n 256 anchos, da 326 m en Kennedy y 350 m en la ciudad, y , 640 y 87… | recomputo › selectores_fino.ciudad.ppl = 349.8187355 | VERIFICADA · re-ejecutada en R |
| `640` | notas | …en Kennedy y 350 m en la ciudad, y , 640 y 877 m (ver el registro). Py… | recomputo › selectores_fino.kennedy.CvL = 640.1220688 | VERIFICADA · re-ejecutada en R |
| `877` | notas | …nedy y 350 m en la ciudad, y , 640 y 877 m (ver el registro). Python:… | recomputo › selectores_fino.ciudad.CvL = 877.2289011 | VERIFICADA · re-ejecutada en R |

### Diapositiva 18 · Por defecto, los selectores discrepan 1.83 veces en Kennedy y 5.30 en la ciudad

| Cifra | Dónde | Contexto | Comprobación | Estado |
|---|---|---|---|---|
| `1.83` | titulo | …Por defecto, los selectores discrepan 1.83 veces en Kennedy y 5.30 en … | datos › m3.kennedy.razon = 1.825166379; recomputo › selectores.kennedy.razon = 1.825166379 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `5.30` | titulo | …res discrepan 1.83 veces en Kennedy y 5.30 en la ciudad… | datos › m3.urbana.razon = 5.304306511; recomputo › selectores.ciudad.razon = 5.304306511 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `633.6` | cuerpo | …ventanas \|\|\| ::: info Dato Kennedy: 633.6 / 347.1 = **1.83**. Ciuda… | datos › m3.kennedy.sigmas_m.scott = 633.5581067; recomputo › selectores.kennedy.sigmas_m.scott = 633.5581067 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `347.1` | cuerpo | …\|\|\| ::: info Dato Kennedy: 633.6 / 347.1 = **1.83**. Ciudad: 1251.3… | datos › m3.kennedy.sigmas_m.diggle = 347.1234808; recomputo › selectores.kennedy.sigmas_m.diggle = 347.1234808 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `1.83` | cuerpo | …info Dato Kennedy: 633.6 / 347.1 = **1.83**. Ciudad: 1251.3 / 235.9 = … | datos › m3.kennedy.razon = 1.825166379; recomputo › selectores.kennedy.razon = 1.825166379 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `1251.3` | cuerpo | …dy: 633.6 / 347.1 = **1.83**. Ciudad: 1251.3 / 235.9 = **5.30**. devue… | datos › m3.urbana.sigmas_m.scott = 1251.284373; recomputo › selectores.ciudad.sigmas_m.scott = 1251.284373 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `235.9` | cuerpo | …/ 347.1 = **1.83**. Ciudad: 1251.3 / 235.9 = **5.30**. devuelve **dos*… | datos › m3.urbana.sigmas_m.ppl = 235.899711; recomputo › selectores.ciudad.sigmas_m.ppl = 235.899711 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `5.30` | cuerpo | …**1.83**. Ciudad: 1251.3 / 235.9 = **5.30**. devuelve **dos** anchos,… | datos › m3.urbana.razon = 5.304306511; recomputo › selectores.ciudad.razon = 5.304306511 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `634` | cuerpo | …devuelve **dos** anchos, uno por eje: 634 y 580 m en Kennedy; 1251 y 2… | datos › m3.kennedy.sigmas_m.scott = 633.5581067; recomputo › selectores.kennedy.sigmas_m.scott = 633.5581067 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `580` | cuerpo | …ve **dos** anchos, uno por eje: 634 y 580 m en Kennedy; 1251 y 2197 m … | datos › m3.kennedy.scott_y_m = 579.5082212; recomputo › selectores.kennedy.scott_y_m = 579.5082212 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `1251` | cuerpo | …uno por eje: 634 y 580 m en Kennedy; 1251 y 2197 m en la ciudad. Las r… | datos › m3.urbana.sigmas_m.scott = 1251.284373; recomputo › selectores.ciudad.sigmas_m.scott = 1251.284373 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `2197` | cuerpo | …r eje: 634 y 580 m en Kennedy; 1251 y 2197 m en la ciudad. Las razones… | datos › m3.urbana.scott_y_m = 2197.047343; recomputo › selectores.ciudad.scott_y_m = 2197.047343 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `1.67` | notas | …cho del eje y de las razones serían 1.67 en Kennedy y 9.31 en la ciuda… | cociente máximo / mínimo de los selectores de Kennedy con el ancho del eje y de `bw.scott` = 1.66945843 | VERIFICADA · aritmética sobre cifras verificadas |
| `9.31` | notas | …las razones serían 1.67 en Kennedy y 9.31 en la ciudad. El abanico dep… | cociente máximo / mínimo de los selectores de la ciudad con el ancho del eje y de `bw.scott` = 9.313480434 | VERIFICADA · aritmética sobre cifras verificadas |
| `16` | notas | …cto de y (nodos de una rejilla de 16 anchos, ver la diapositiva an… | recomputo › selectores.ns_ppl = 16 | VERIFICADA · re-ejecutada en R |
| `326` | notas | …por debajo de en las dos ventanas (326 contra 347 m en Kennedy; 350… | recomputo › selectores_fino.kennedy.ppl = 326.0628978 | VERIFICADA · re-ejecutada en R |
| `347` | notas | …de en las dos ventanas (326 contra 347 m en Kennedy; 350 contra 373… | datos › m3.kennedy.sigmas_m.diggle = 347.1234808; recomputo › selectores.kennedy.sigmas_m.diggle = 347.1234808 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `350` | notas | …entanas (326 contra 347 m en Kennedy; 350 contra 373 m en la ciudad), … | recomputo › selectores_fino.ciudad.ppl = 349.8187355 | VERIFICADA · re-ejecutada en R |
| `373` | notas | …6 contra 347 m en Kennedy; 350 contra 373 m en la ciudad), de modo que… | datos › m3.urbana.sigmas_m.diggle = 373.2167541; recomputo › selectores.ciudad.sigmas_m.diggle = 373.2167541 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `550` | notas | …olo puede dibujar núcleos de al menos 550 m. Cotejo: , , .… | datos › m5.rejilla.sigma_minimo_dibujable_m = 550.13585; recomputo › capas.sigma_minimo_m = 550.13585 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |

### Diapositiva 19 · Un selector que devuelve el borde de su intervalo no seleccionó nada

| Cifra | Dónde | Contexto | Comprobación | Estado |
|---|---|---|---|---|
| `65` | cuerpo | …**De dónde sale:** (spatstat.data): 65 pinos jóvenes en un cuadrado… | recomputo › japanesepines.n = 65 \| ayuda de spatstat.data (recomputo › japanesepines.ayuda): «65 tree sapling» | VERIFICADA · re-ejecutada en R |
| `5.7` | cuerpo | …): 65 pinos jóvenes en un cuadrado de 5.7 m (Numata, 1961), reescalado… | ayuda de spatstat.data (recomputo › japanesepines.ayuda): «5.7 x 5.7 metre square» | REFERENCIA · ficha de ayuda del paquete |
| `1961` | cuerpo | …enes en un cuadrado de 5.7 m (Numata, 1961), reescalado a la unidad. *… | ayuda de spatstat.data (recomputo › japanesepines.ayuda): «Numata (1961)» | REFERENCIA · ficha de ayuda del paquete |
| `0.7071` | notas | …do unidad es la mitad de la diagonal, 0.7071. R sí avisa («criterion w… | datos › m3.topes[0].sigma = 0.7071067812; recomputo › japanesepines.bw_ppl = 0.7071067812 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `20` | notas | …otra pared. En el del se amplía a 20 y devuelve 20; ahí la conclus… | texto del capítulo: «con el tope subido a 20» | CONTRASTADA · texto del capítulo |
| `20` | notas | …el del se amplía a 20 y devuelve 20; ahí la conclusión es que par… | texto del capítulo: «con el tope subido a 20» | CONTRASTADA · texto del capítulo |

### Diapositiva 20 · Mismo patrón, dos mapas distintos: ¿quién se equivocó, `bw.diggle` o `bw.scott`?

| Cifra | Dónde | Contexto | Comprobación | Estado |
|---|---|---|---|---|
| `236` | cuerpo | …a ciudad los cuatro selectores dan de 236 a 1251 m, porque cada uno pr… | datos › m3.urbana.sigmas_m.ppl = 235.899711; recomputo › selectores.ciudad.sigmas_m.ppl = 235.899711 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `1251` | cuerpo | …ad los cuatro selectores dan de 236 a 1251 m, porque cada uno pregunta… | datos › m3.urbana.sigmas_m.scott = 1251.284373; recomputo › selectores.ciudad.sigmas_m.scott = 1251.284373 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |

### Diapositiva 22 · Corrección de borde en la KDE

| Cifra | Dónde | Contexto | Comprobación | Estado |
|---|---|---|---|---|
| `14` | notas | …Unos 14 minutos. Materia del Quiz 2.… | minutos que se asignan a cada bloque de la sesión: decisión del docente, no un dato del capítulo | PARÁMETRO de diseño |

### Diapositiva 23 · El núcleo de una sede pegada al borde se sale de la ventana

| Cifra | Dónde | Contexto | Comprobación | Estado |
|---|---|---|---|---|
| `69` | cuerpo | …borde: dentro de la ventana queda el 69 % \|\|\| ::: info Dato Ilustra… | 100 × Φ(0.5): la fracción del núcleo de una sede a 0.5 σ del borde que queda dentro de la ventana = 69.14624613 | VERIFICADA · aritmética sobre cifras verificadas |
| `0.5` | cuerpo | …stración en una dimensión: una sede a 0.5 σ del borde, con σ = 1. Se q… | distancia de la sede al borde, en unidades de σ, en la ilustración en una dimensión | PARÁMETRO de diseño |
| `69` | cuerpo | …orde, con σ = 1. Se queda dentro el **69 %** de su núcleo ( = 0.69) y… | 100 × Φ(0.5): la fracción del núcleo de una sede a 0.5 σ del borde que queda dentro de la ventana = 69.14624613 | VERIFICADA · aritmética sobre cifras verificadas |
| `0.69` | cuerpo | …dentro el **69 %** de su núcleo ( = 0.69) y se sale el **31 %**. :::… | Φ(0.5) = 0.6914624613 | VERIFICADA · aritmética sobre cifras verificadas |
| `31` | cuerpo | …e su núcleo ( = 0.69) y se sale el **31 %**. ::: ::: tip Interpretac… | 100 × (1 − Φ(0.5)): lo que se sale = 30.85375387 | VERIFICADA · aritmética sobre cifras verificadas |
| `0.69` | notas | …da a un lado del borde, a media σ, es 0.69 (la función de distribución… | Φ(0.5) = 0.6914624613 | VERIFICADA · aritmética sobre cifras verificadas |
| `0.5` | notas | …(la función de distribución normal en 0.5), y se sale el resto. En Ken… | distancia de la sede al borde, en unidades de σ, en la ilustración en una dimensión | PARÁMETRO de diseño |

### Diapositiva 24 · Lo que el mapa no deja ver: ¿la integral de λ̂ devuelve n?

| Cifra | Dónde | Contexto | Comprobación | Estado |
|---|---|---|---|---|
| `262` | cuerpo | …exto del capítulo). Ejemplo: Kennedy, 262 sedes.… | datos › m1.ventana.n = 262; recomputo › kennedy.n = 262 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `300` | notas | …ión hecha para esta presentación: con 300 patrones al azar de 262 sede… | recomputo › bordes_csr.patrones = 300 | VERIFICADA · re-ejecutada en R |
| `262` | notas | …entación: con 300 patrones al azar de 262 sedes en la ventana de Kenne… | datos › m1.ventana.n = 262; recomputo › kennedy.n = 262 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `0.04` | notas | …defecto se desvía de n en promedio un +0.04 % con σ = 800 m (conserva … | recomputo › bordes_csr.media_pct.defecto_800 = 0.03906442241 | VERIFICADA · re-ejecutada en R |
| `800` | notas | …a de n en promedio un +0.04 % con σ = 800 m (conserva el conteo en pro… | datos › m4.sigmas_m = [200, 400, 800] | CONTRASTADA · salida de R (JSON del capítulo) |
| `-19.6` | notas | …promedio) y sin corregir se pierde un −19.6 %; el +3.19 % del patrón r… | recomputo › bordes_csr.media_pct.sin_800 = -19.59688469 | VERIFICADA · re-ejecutada en R |
| `3.19` | notas | …sin corregir se pierde un −19.6 %; el +3.19 % del patrón real es de es… | datos › m4.tabla[2].exceso_defecto_pct = 3.191567581; recomputo › bordes.800.pct_defecto = 3.191567581 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |

### Diapositiva 25 · Medido sobre Kennedy: tres correcciones, tres comportamientos

| Cifra | Dónde | Contexto | Comprobación | Estado |
|---|---|---|---|---|
| `262` | cuerpo | …::: info Dato · Kennedy, 262 sedes Masa integrada por cada… | datos › m1.ventana.n = 262; recomputo › kennedy.n = 262 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `262` | cuerpo | …ntre paréntesis, su desviación de n = 262: \| σ (m) \| Sin corregir \|… | datos › m1.ventana.n = 262; recomputo › kennedy.n = 262 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `200` | cuerpo | …Por defecto \| \| \|---\|---\|---\|---\| \| 200 \| 255.08 (−2.64 %) \|… | datos › m4.sigmas_m = [200, 400, 800] | CONTRASTADA · salida de R (JSON del capítulo) |
| `255.08` | cuerpo | …fecto \| \| \|---\|---\|---\|---\| \| 200 \| 255.08 (−2.64 %) \| 263.3… | datos › m4.tabla[0].masa_sin_corregir = 255.0829323; recomputo › bordes.200.masa_sin = 255.0829323 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `-2.64` | cuerpo | …\| \|---\|---\|---\|---\| \| 200 \| 255.08 (−2.64 %) \| 263.30 (+0.50 … | datos › m4.tabla[0].fuga_sin_corregir_pct = -2.640102193; recomputo › bordes.200.pct_sin = -2.640102193 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `263.30` | cuerpo | …-\|---\|---\| \| 200 \| 255.08 (−2.64 %) \| 263.30 (+0.50 %) \| 262.00… | datos › m4.tabla[0].masa_defecto = 263.2977368; recomputo › bordes.200.masa_defecto = 263.2977368 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `0.50` | cuerpo | …-\| \| 200 \| 255.08 (−2.64 %) \| 263.30 (+0.50 %) \| 262.00 (0.0000 %… | datos › m4.tabla[0].exceso_defecto_pct = 0.4953193737; recomputo › bordes.200.pct_defecto = 0.4953193737 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `262.00` | cuerpo | …255.08 (−2.64 %) \| 263.30 (+0.50 %) \| 262.00 (0.0000 %) \| \| 400 \|… | datos › m4.tabla[0].masa_diggle = 262; recomputo › bordes.200.masa_diggle = 262 \| datos › m4.tabla[2].masa_diggle = 262; recomputo › bordes.800.masa_diggle = 262 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `0.0000` | cuerpo | …−2.64 %) \| 263.30 (+0.50 %) \| 262.00 (0.0000 %) \| \| 400 \| 245.86 … | datos › m4.tabla[0].error_diggle_pct = 0; recomputo › bordes.200.pct_diggle = -6.77236045e-13 \| datos › m4.tabla[2].error_diggle_pct = 0; recomputo › bordes.800.pct_diggle = -2.220446049e-13 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `400` | cuerpo | ….30 (+0.50 %) \| 262.00 (0.0000 %) \| \| 400 \| 245.86 (−6.16 %) \| 26… | datos › m2.sigma_m = 400; recomputo › nucleos.sigma_m = 400 \| datos › m4.sigmas_m = [200, 400, 800] | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `245.86` | cuerpo | …0.50 %) \| 262.00 (0.0000 %) \| \| 400 \| 245.86 (−6.16 %) \| 265.80 (… | datos › m4.tabla[1].masa_sin_corregir = 245.856354; recomputo › bordes.400.masa_sin = 245.856354 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `-6.16` | cuerpo | …\| 262.00 (0.0000 %) \| \| 400 \| 245.86 (−6.16 %) \| 265.80 (+1.45 %)… | datos › m4.tabla[1].fuga_sin_corregir_pct = -6.161696952; recomputo › bordes.400.pct_sin = -6.161696953 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `265.80` | cuerpo | ….0000 %) \| \| 400 \| 245.86 (−6.16 %) \| 265.80 (+1.45 %) \| 262.00 (… | datos › m4.tabla[1].masa_defecto = 265.7985659; recomputo › bordes.400.masa_defecto = 265.7985659 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `1.45` | cuerpo | …\| \| 400 \| 245.86 (−6.16 %) \| 265.80 (+1.45 %) \| 262.00 (0.0000 %)… | datos › m4.tabla[1].exceso_defecto_pct = 1.449834295; recomputo › bordes.400.pct_defecto = 1.449834295 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `262.00` | cuerpo | …245.86 (−6.16 %) \| 265.80 (+1.45 %) \| 262.00 (0.0000 %) \| \| 800 \|… | datos › m4.tabla[0].masa_diggle = 262; recomputo › bordes.200.masa_diggle = 262 \| datos › m4.tabla[2].masa_diggle = 262; recomputo › bordes.800.masa_diggle = 262 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `0.0000` | cuerpo | …−6.16 %) \| 265.80 (+1.45 %) \| 262.00 (0.0000 %) \| \| 800 \| 224.41 … | datos › m4.tabla[0].error_diggle_pct = 0; recomputo › bordes.200.pct_diggle = -6.77236045e-13 \| datos › m4.tabla[2].error_diggle_pct = 0; recomputo › bordes.800.pct_diggle = -2.220446049e-13 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `800` | cuerpo | ….80 (+1.45 %) \| 262.00 (0.0000 %) \| \| 800 \| 224.41 (−14.35 %) \| 2… | datos › m4.sigmas_m = [200, 400, 800] | CONTRASTADA · salida de R (JSON del capítulo) |
| `224.41` | cuerpo | …1.45 %) \| 262.00 (0.0000 %) \| \| 800 \| 224.41 (−14.35 %) \| 270.36 … | datos › m4.tabla[2].masa_sin_corregir = 224.4064737; recomputo › bordes.800.masa_sin = 224.4064737 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `-14.35` | cuerpo | …\| 262.00 (0.0000 %) \| \| 800 \| 224.41 (−14.35 %) \| 270.36 (+3.19 %… | datos › m4.tabla[2].fuga_sin_corregir_pct = -14.34867416; recomputo › bordes.800.pct_sin = -14.34867416 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `270.36` | cuerpo | …0000 %) \| \| 800 \| 224.41 (−14.35 %) \| 270.36 (+3.19 %) \| 262.00 (… | datos › m4.tabla[2].masa_defecto = 270.3619071; recomputo › bordes.800.masa_defecto = 270.3619071 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `3.19` | cuerpo | …\| \| 800 \| 224.41 (−14.35 %) \| 270.36 (+3.19 %) \| 262.00 (0.0000 %… | datos › m4.tabla[2].exceso_defecto_pct = 3.191567581; recomputo › bordes.800.pct_defecto = 3.191567581 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `262.00` | cuerpo | …24.41 (−14.35 %) \| 270.36 (+3.19 %) \| 262.00 (0.0000 %) \| ::: ::: t… | datos › m4.tabla[0].masa_diggle = 262; recomputo › bordes.200.masa_diggle = 262 \| datos › m4.tabla[2].masa_diggle = 262; recomputo › bordes.800.masa_diggle = 262 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `0.0000` | cuerpo | …14.35 %) \| 270.36 (+3.19 %) \| 262.00 (0.0000 %) \| ::: ::: tip Inter… | datos › m4.tabla[0].error_diggle_pct = 0; recomputo › bordes.200.pct_diggle = -6.77236045e-13 \| datos › m4.tabla[2].error_diggle_pct = 0; recomputo › bordes.800.pct_diggle = -2.220446049e-13 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `17.54` | notas | …o corregir y corregir por defecto hay 17.54 puntos porcentuales a σ = … | datos › m4.horquilla_pct = 17.54024174; recomputo › bordes.horquilla_pp_800 = 17.54024174 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `800` | notas | …o hay 17.54 puntos porcentuales a σ = 800 m. Lo que se ve aquí es el c… | datos › m4.sigmas_m = [200, 400, 800] | CONTRASTADA · salida de R (JSON del capítulo) |

### Diapositiva 26 · ¿Se distingue cuál es cuál mirando el mapa?

| Cifra | Dónde | Contexto | Comprobación | Estado |
|---|---|---|---|---|
| `800` | cuerpo | …Tres correcciones de borde con σ = 800 m, sin nombre: A, B y C \|\|\|… | datos › m4.sigmas_m = [200, 400, 800] | CONTRASTADA · salida de R (JSON del capítulo) |
| `262` | cuerpo | …, sin nombre: A, B y C \|\|\| Kennedy, 262 sedes, σ = 800 m, la misma … | datos › m1.ventana.n = 262; recomputo › kennedy.n = 262 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `800` | cuerpo | …, B y C \|\|\| Kennedy, 262 sedes, σ = 800 m, la misma escala de color… | datos › m4.sigmas_m = [200, 400, 800] | CONTRASTADA · salida de R (JSON del capítulo) |
| `270.4` | cuerpo | …lo dice la integral (A, por defecto, 270.4; B, sin corregir, 224.4; C,… | datos › m4.tabla[2].masa_defecto = 270.3619071; recomputo › bordes.800.masa_defecto = 270.3619071 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `224.4` | cuerpo | …por defecto, 270.4; B, sin corregir, 224.4; C, Diggle, 262.0). Sí se v… | datos › m4.tabla[2].masa_sin_corregir = 224.4064737; recomputo › bordes.800.masa_sin = 224.4064737 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `262.0` | cuerpo | …4; B, sin corregir, 224.4; C, Diggle, 262.0). Sí se ven diferencias —a… | datos › m4.tabla[2].masa_diggle = 262; recomputo › bordes.800.masa_diggle = 262 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `12.66` | cuerpo | …cias —al no corregir el pico baja, de 12.66 a 11.54 sedes por km²—, pe… | datos › m4.tabla[2].max_km2_defecto = 12.65984977; recomputo › bordes.800.max_defecto = 12.65984977 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `11.54` | cuerpo | …no corregir el pico baja, de 12.66 a 11.54 sedes por km²—, pero ningun… | datos › m4.tabla[2].max_km2_sin_corregir = 11.5397454; recomputo › bordes.800.max_sin = 11.5397454 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |

### Diapositiva 27 · Diggle divide donde está el dato; la de por defecto, donde se estima

| Cifra | Dónde | Contexto | Comprobación | Estado |
|---|---|---|---|---|
| `3` | notas | …gle coincide con spatstat (a menos de 3 % por la discretización de la… | el error de ambas fórmulas contra spatstat (2.87 % y 2.54 %) es menor que 3 % = 3 | VERIFICADA · aritmética sobre cifras verificadas |
| `88` | notas | …o, usada en su lugar, se aparta hasta 88 % en el peor de los puntos de… | recomputo › diggle_identidad.cruce_pct = 88.40951558 | VERIFICADA · re-ejecutada en R |

### Diapositiva 28 · La integral de la KDE: 270.36 por defecto, 262.00 con Diggle

| Cifra | Dónde | Contexto | Comprobación | Estado |
|---|---|---|---|---|
| `270.36` | titulo | …La integral de la KDE: 270.36 por defecto, 262.00 con Diggl… | datos › m4.tabla[2].masa_defecto = 270.3619071; recomputo › bordes.800.masa_defecto = 270.3619071 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `262.00` | titulo | …tegral de la KDE: 270.36 por defecto, 262.00 con Diggle… | datos › m4.tabla[0].masa_diggle = 262; recomputo › bordes.200.masa_diggle = 262 \| datos › m4.tabla[2].masa_diggle = 262; recomputo › bordes.800.masa_diggle = 262 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `96x99` | cuerpo | …sedes Con σ = 800 m y una rejilla de 96 × 99 píxeles, la masa integrad… | datos › m2.familia.nx × ny = 96x99 | PARÁMETRO de diseño |
| `262` | cuerpo | …\|\|\| ::: info Dato · Kennedy, 262 sedes Con σ = 800 m y una rej… | datos › m1.ventana.n = 262; recomputo › kennedy.n = 262 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `800` | cuerpo | …nfo Dato · Kennedy, 262 sedes Con σ = 800 m y una rejilla de píxeles,… | datos › m4.sigmas_m = [200, 400, 800] | CONTRASTADA · salida de R (JSON del capítulo) |
| `270.3619` | cuerpo | …, la masa integrada es: por defecto **270.3619**, **262.0000**, sin co… | datos › m4.tabla[2].masa_defecto = 270.3619071; recomputo › bordes.800.masa_defecto = 270.3619071 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `262.0000` | cuerpo | …ada es: por defecto **270.3619**, **262.0000**, sin corregir **224.406… | datos › m4.tabla[2].masa_diggle = 262; recomputo › bordes.800.masa_diggle = 262 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `224.4065` | cuerpo | …619**, **262.0000**, sin corregir **224.4065**; n = 262. ::: ::: warn … | datos › m4.tabla[2].masa_sin_corregir = 224.4064737; recomputo › bordes.800.masa_sin = 224.4064737 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `262` | cuerpo | …000**, sin corregir **224.4065**; n = 262. ::: ::: warn Criterio Integ… | datos › m1.ventana.n = 262; recomputo › kennedy.n = 262 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `128x128` | notas | …ntras que aquí corregir o no la KDE a 128 × 128 sobre la ciudad cuesta… | datos › meta.rejilla.nx_ciudad = 128 | PARÁMETRO de diseño |
| `122.655` | notas | …veces la alternativa (la isotrópica, 122.655 s; la de traslación, 0.22… | cap4_datos.json › m10.correcciones[3].segundos = 122.655 | CONTRASTADA · salida de R (JSON del capítulo) |
| `0.221` | notas | …trópica, 122.655 s; la de traslación, 0.221 s), mientras que aquí corr… | cap4_datos.json › m10.correcciones[2].segundos = 0.221 | CONTRASTADA · salida de R (JSON del capítulo) |
| `0.14` | notas | …a sobre la ciudad cuesta lo mismo: 0.14 contra 0.15 s, del mismo orde… | datos › m4.coste_segundos.sin_corregir = 0.14 | CONTRASTADA · salida de R (JSON del capítulo) |
| `0.15` | notas | …a ciudad cuesta lo mismo: 0.14 contra 0.15 s, del mismo orden. Son tie… | datos › m4.coste_segundos.defecto = 0.15 \| datos › m4.coste_segundos.diggle = 0.15 | CONTRASTADA · salida de R (JSON del capítulo) |
| `0.155` | notas | …áquina: se volvieron a medir en esta (0.155, 0.147 y 0.161 s) y salen … | recomputo › tiempos.ciudad_128.defecto = 0.152 (tolerancia ±0.02) | MEDIDA · depende de la máquina (con tolerancia) |
| `0.147` | notas | …se volvieron a medir en esta (0.155, 0.147 y 0.161 s) y salen del mism… | recomputo › tiempos.ciudad_128.sin_corregir = 0.145 (tolerancia ±0.02) | MEDIDA · depende de la máquina (con tolerancia) |
| `0.161` | notas | …ieron a medir en esta (0.155, 0.147 y 0.161 s) y salen del mismo orden… | recomputo › tiempos.ciudad_128.diggle = 0.158 (tolerancia ±0.02) | MEDIDA · depende de la máquina (con tolerancia) |

### Diapositiva 29 · La KDE como mapa de calor

| Cifra | Dónde | Contexto | Comprobación | Estado |
|---|---|---|---|---|
| `10` | notas | …Unos 10 minutos. Este módulo no entra… | minutos que se asignan a cada bloque de la sesión: decisión del docente, no un dato del capítulo | PARÁMETRO de diseño |

### Diapositiva 30 · Tres mapas de Bogotá se parecen mucho y responden tres preguntas distintas

| Cifra | Dónde | Contexto | Comprobación | Estado |
|---|---|---|---|---|
| `11` | cuerpo | …urbano (SED) y los evaluados en Saber 11, periodo 20224 (ICFES); el mi… | grado 11: el último grado de la educación media colombiana, el que evalúa la prueba Saber 11 | PARÁMETRO de diseño |
| `20224` | cuerpo | …y los evaluados en Saber 11, periodo 20224 (ICFES); el mismo σ = 720 m… | texto del capítulo: «periodo 20224» | CONTRASTADA · texto del capítulo |
| `720` | cuerpo | …, periodo 20224 (ICFES); el mismo σ = 720 m (el valor por defecto de )… | datos › m5.sigma_m = 720.3691455; recomputo › capas.sigma_m = 720.3691455 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `1062` | cuerpo | …eerá como demanda. ::: ::: info Dato 1 062 de las 2 107 sedes (50.4 %)… | datos › m5.capas.grado_11.n = 1062; recomputo › capas.n_grado11 = 1062 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `2107` | cuerpo | …anda. ::: ::: info Dato 1 062 de las 2 107 sedes (50.4 %) tienen grado… | datos › m5.capas.oferta.n = 2107; recomputo › urbana.n_urbana = 2107 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `50.4` | cuerpo | …: info Dato 1 062 de las 2 107 sedes (50.4 %) tienen grado 11; son 145… | datos › m5.capas.grado_11.pct_de_las_sedes = 50.40341718; recomputo › capas.pct_grado11 = 50.40341718 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `11` | cuerpo | …las 2 107 sedes (50.4 %) tienen grado 11; son 145 362 evaluados. Corre… | grado 11: el último grado de la educación media colombiana, el que evalúa la prueba Saber 11 | PARÁMETRO de diseño |
| `145362` | cuerpo | …7 sedes (50.4 %) tienen grado 11; son 145 362 evaluados. Correlaciones… | datos › m5.capas.estudiantes.total = 145362; recomputo › capas.evaluados = 145362 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `0.943` | cuerpo | …Correlaciones: oferta–bachillerato **0.943**, oferta–estudiantes **0.8… | datos › m5.cor_oferta_grado11 = 0.9428514584; recomputo › capas.cor_of_11 = 0.9428514584 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `0.862` | cuerpo | …erato **0.943**, oferta–estudiantes **0.862**, bachillerato–estudiante… | datos › m5.cor_oferta_estudiantes = 0.8616257893; recomputo › capas.cor_of_es = 0.8616257893 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `0.919` | cuerpo | …**0.862**, bachillerato–estudiantes **0.919**. :::… | datos › m5.cor_grado11_estudiantes = 0.9185657089; recomputo › capas.cor_11_es = 0.9185657089 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `11` | notas | …ia no tiene undécimo. Pesar por Saber 11 sin decirlo convertiría un ma… | grado 11: el último grado de la educación media colombiana, el que evalúa la prueba Saber 11 | PARÁMETRO de diseño |
| `14.5` | notas | …a a su propia escala. Los máximos son 14.5 sedes por km² (oferta), 9.5… | datos › m5.capas.oferta.max_km2 = 14.5361525; recomputo › capas.max_oferta = 14.5361525 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `9.5` | notas | …imos son 14.5 sedes por km² (oferta), 9.5 (bachillerato) y 1579 evalua… | datos › m5.capas.grado_11.max_km2 = 9.544418978; recomputo › capas.max_grado11 = 9.544418979 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `1579` | notas | …or km² (oferta), 9.5 (bachillerato) y 1579 evaluados por km² (estudian… | datos › m5.capas.estudiantes.max_km2 = 1578.806516; recomputo › capas.max_estudiantes = 1578.806516 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `0.9391` | notas | …aciones de la versión de Python salen 0.9391, 0.8555 y 0.9155: no es o… | texto del capítulo: «0.9391, 0.8555, 0.9155» | CONTRASTADA · texto del capítulo |
| `0.8555` | notas | …de la versión de Python salen 0.9391, 0.8555 y 0.9155: no es otra disc… | texto del capítulo: «0.9391, 0.8555, 0.9155» | CONTRASTADA · texto del capítulo |
| `0.9155` | notas | …sión de Python salen 0.9391, 0.8555 y 0.9155: no es otra discretizació… | texto del capítulo: «0.9391, 0.8555, 0.9155» | CONTRASTADA · texto del capítulo |
| `11` | notas | …recciones distintas. «Sedes con grado 11» son las sedes con al menos u… | grado 11: el último grado de la educación media colombiana, el que evalúa la prueba Saber 11 | PARÁMETRO de diseño |
| `20224` | notas | …on al menos un evaluado en el periodo 20224. Cotejo: , , , , , , .… | texto del capítulo: «periodo 20224» | CONTRASTADA · texto del capítulo |

### Diapositiva 31 · Donde las manchas no coinciden, el edificio y el estudiante dejan de ser lo mismo

| Cifra | Dónde | Contexto | Comprobación | Estado |
|---|---|---|---|---|
| `128x218` | cuerpo | …l valor por defecto de ), rejilla de 128 × 218 celdas de 183 m, **cada… | datos › m5.rejilla.nx × ny = 128x218 | PARÁMETRO de diseño |
| `720` | cuerpo | …gura propia. \|\|\| ::: info Dato σ = 720 m (el valor por defecto de )… | datos › m5.sigma_m = 720.3691455; recomputo › capas.sigma_m = 720.3691455 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `183` | cuerpo | …defecto de ), rejilla de celdas de 183 m, **cada mapa a su escala**.… | datos › m5.rejilla.celda_m = 183.3786167; recomputo › capas.celda_x_m = 183.3786167 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `14.5` | cuerpo | …escala**. El máximo de la **oferta** (14.5 por km²) está en **Suba**; … | datos › m5.capas.oferta.max_km2 = 14.5361525; recomputo › capas.max_oferta = 14.5361525 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `1579` | cuerpo | …á en **Suba**; el de **estudiantes** (1579 por km²), en **Bosa**. ::: … | datos › m5.capas.estudiantes.max_km2 = 1578.806516; recomputo › capas.max_estudiantes = 1578.806516 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `2107` | cuerpo | …bian dos cosas: qué sedes entran (las 2 107, o solo las 1 062 con grad… | datos › m5.capas.oferta.n = 2107; recomputo › urbana.n_urbana = 2107 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `1062` | cuerpo | …é sedes entran (las 2 107, o solo las 1 062 con grado 11) y cuánto pes… | datos › m5.capas.grado_11.n = 1062; recomputo › capas.n_grado11 = 1062 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `11` | cuerpo | …las 2 107, o solo las 1 062 con grado 11) y cuánto pesa cada una (1, o… | grado 11: el último grado de la educación media colombiana, el que evalúa la prueba Saber 11 | PARÁMETRO de diseño |
| `0.919` | cuerpo | …ara bachillerato con estudiantes (r = 0.919). :::… | datos › m5.cor_grado11_estudiantes = 0.9185657089; recomputo › capas.cor_11_es = 0.9185657089 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |

### Diapositiva 32 · Con celdas de 183 m, la ciudad no puede dibujar un σ menor que 550 m

| Cifra | Dónde | Contexto | Comprobación | Estado |
|---|---|---|---|---|
| `183` | titulo | …Con celdas de 183 m, la ciudad no puede dibujar… | datos › m5.rejilla.celda_m = 183.3786167; recomputo › capas.celda_x_m = 183.3786167 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `550` | titulo | …iudad no puede dibujar un σ menor que 550 m… | datos › m5.rejilla.sigma_minimo_dibujable_m = 550.13585; recomputo › capas.sigma_minimo_m = 550.13585 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `128x218` | cuerpo | …ventana urbana 370.09 km², rejilla de 128 × 218 celdas de 183 m. Regla… | datos › m5.rejilla.nx × ny = 128x218 | PARÁMETRO de diseño |
| `370.09` | cuerpo | …::: info Dato · ventana urbana 370.09 km², rejilla de celdas de 1… | recomputo › urbana.area_km2 = 370.0898165 | VERIFICADA · re-ejecutada en R |
| `183` | cuerpo | …na 370.09 km², rejilla de celdas de 183 m. Regla práctica: celda ≤ σ/… | datos › m5.rejilla.celda_m = 183.3786167; recomputo › capas.celda_x_m = 183.3786167 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `3` | cuerpo | …s de 183 m. Regla práctica: celda ≤ σ/3, o sea 3 celdas dentro de σ;… | datos › meta.rejilla.celdas_por_sigma = 3 | CONTRASTADA · salida de R (JSON del capítulo) |
| `3` | cuerpo | …m. Regla práctica: celda ≤ σ/3, o sea 3 celdas dentro de σ; con 183.4… | datos › meta.rejilla.celdas_por_sigma = 3 | CONTRASTADA · salida de R (JSON del capítulo) |
| `183.4` | cuerpo | …σ/3, o sea 3 celdas dentro de σ; con 183.4 m por celda, σ mínimo = 3 ×… | datos › m5.rejilla.celda_m = 183.3786167; recomputo › capas.celda_x_m = 183.3786167 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `3` | cuerpo | …σ; con 183.4 m por celda, σ mínimo = 3 × 183.4 = **550 m**. \| Selec… | el error de ambas fórmulas contra spatstat (2.87 % y 2.54 %) es menor que 3 % = 3 | VERIFICADA · aritmética sobre cifras verificadas |
| `183.4` | cuerpo | …con 183.4 m por celda, σ mínimo = 3 × 183.4 = **550 m**. \| Selector \… | datos › m5.rejilla.celda_m = 183.3786167; recomputo › capas.celda_x_m = 183.3786167 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `550` | cuerpo | …m por celda, σ mínimo = 3 × 183.4 = **550 m**. \| Selector \| σ sobre … | datos › m5.rejilla.sigma_minimo_dibujable_m = 550.13585; recomputo › capas.sigma_minimo_m = 550.13585 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `3` | cuerpo | …sobre la ciudad \| ¿Cumple la regla de 3 celdas? \| \|---\|---\|---\| … | el error de ambas fórmulas contra spatstat (2.87 % y 2.54 %) es menor que 3 % = 3 | VERIFICADA · aritmética sobre cifras verificadas |
| `373` | cuerpo | …la de 3 celdas? \| \|---\|---\|---\| \| \| 373 m \| No: menor que 550 … | datos › m3.urbana.sigmas_m.diggle = 373.2167541; recomputo › selectores.ciudad.sigmas_m.diggle = 373.2167541 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `550` | cuerpo | …\|---\|---\| \| \| 373 m \| No: menor que 550 m \| \| \| 236 m \| No: … | datos › m5.rejilla.sigma_minimo_dibujable_m = 550.13585; recomputo › capas.sigma_minimo_m = 550.13585 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `236` | cuerpo | …\| 373 m \| No: menor que 550 m \| \| \| 236 m \| No: menor que 550 m … | datos › m3.urbana.sigmas_m.ppl = 235.899711; recomputo › selectores.ciudad.sigmas_m.ppl = 235.899711 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `550` | cuerpo | …e 550 m \| \| \| 236 m \| No: menor que 550 m \| \| \| **720 m** \| Sí… | datos › m5.rejilla.sigma_minimo_dibujable_m = 550.13585; recomputo › capas.sigma_minimo_m = 550.13585 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `720` | cuerpo | …236 m \| No: menor que 550 m \| \| \| **720 m** \| Sí: el más estrecho… | datos › m5.sigma_m = 720.3691455; recomputo › capas.sigma_m = 720.3691455 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `1251` | cuerpo | …el más estrecho de los que sí \| \| \| 1251 m \| Sí \| ::: \|\|\| ::: … | datos › m3.urbana.sigmas_m.scott = 1251.284373; recomputo › selectores.ciudad.sigmas_m.scott = 1251.284373 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `183` | cuerpo | …Sí \| ::: \|\|\| ::: tip Interpretación 183 m es la celda más fina que… | datos › m5.rejilla.celda_m = 183.3786167; recomputo › capas.celda_x_m = 183.3786167 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `78` | cuerpo | …iudad usa , y Kennedy, con celdas de 78 m, puede bajar a 233 m. :::… | datos › m2.familia.celda_m = 77.7982889; recomputo › anchos.celda_x_m = 77.7982889 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `233` | cuerpo | …dy, con celdas de 78 m, puede bajar a 233 m. ::: ::: warn Criterio Pri… | datos › m2.familia.sigmas_m[0] = 233.3949; recomputo › anchos.sigmas_m[0] = 233.3949 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |

### Diapositiva 33 · ¿Cuál de los tres mapas es «el mapa de la demanda educativa»?

| Cifra | Dónde | Contexto | Comprobación | Estado |
|---|---|---|---|---|
| `11` | cuerpo | …a completa. El de las sedes con grado 11, porque restringe a quien pue… | grado 11: el último grado de la educación media colombiana, el que evalúa la prueba Saber 11 | PARÁMETRO de diseño |

### Diapositiva 34 · Intensidad relativa

| Cifra | Dónde | Contexto | Comprobación | Estado |
|---|---|---|---|---|
| `13` | notas | …Unos 13 minutos. Cierra la mitad desc… | minutos que se asignan a cada bloque de la sesión: decisión del docente, no un dato del capítulo | PARÁMETRO de diseño |

### Diapositiva 36 · Chorley: 58 casos de laringe contra 978 controles de pulmón

| Cifra | Dónde | Contexto | Comprobación | Estado |
|---|---|---|---|---|
| `58` | titulo | …Chorley: 58 casos de laringe contra 978 c… | datos › m6.chorley.casos = 58; recomputo › chorley.n_laringe = 58 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `978` | titulo | …Chorley: 58 casos de laringe contra 978 controles de pulmón… | datos › m6.chorley.controles = 978; recomputo › chorley.n_pulmon = 978 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `58` | cuerpo | …escala de 0 a 1 ::: info Dato Global 58 / 1 036 = **0.0560**; mediana… | datos › m6.chorley.casos = 58; recomputo › chorley.n_laringe = 58 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `1036` | cuerpo | …a de 0 a 1 ::: info Dato Global 58 / 1 036 = **0.0560**; mediana de la… | recomputo › chorley.n = 1036 | VERIFICADA · re-ejecutada en R |
| `0.0560` | cuerpo | …::: info Dato Global 58 / 1 036 = **0.0560**; mediana de la superficie… | datos › m6.chorley.prop_global = 0.055984556; recomputo › chorley.global = 0.05598455598 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `0.0482` | cuerpo | …*0.0560**; mediana de la superficie **0.0482**; máximo **0.3389**, don… | datos › m6.chorley.p_mediana = 0.0481849481; recomputo › chorley.mediana = 0.04818494813 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `0.3389` | cuerpo | …de la superficie **0.0482**; máximo **0.3389**, donde casi no hay punt… | datos › m6.chorley.p_max = 0.3388509631; recomputo › chorley.maximo = 0.3388509631 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `4` | cuerpo | …**0.3389**, donde casi no hay puntos: 4 de sus 50 vecinos más próximo… | recomputo › chorley.vecinos_casos = 4 | VERIFICADA · re-ejecutada en R |
| `50` | cuerpo | …*, donde casi no hay puntos: 4 de sus 50 vecinos más próximos son caso… | recomputo › chorley.vecinos_k = 50 | VERIFICADA · re-ejecutada en R |
| `58` | cuerpo | …**De dónde sale:** (spatstat.data): 58 casos de laringe y 978 de pul… | datos › m6.chorley.casos = 58; recomputo › chorley.n_laringe = 58 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `978` | cuerpo | …spatstat.data): 58 casos de laringe y 978 de pulmón, Lancashire, 1974–… | datos › m6.chorley.controles = 978; recomputo › chorley.n_pulmon = 978 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `1974` | cuerpo | …laringe y 978 de pulmón, Lancashire, 1974–1983, en 315.16 km². **Por q… | ayuda de spatstat.data (recomputo › chorley.ayuda): «between 1974 and 1983» | REFERENCIA · ficha de ayuda del paquete |
| `1983` | cuerpo | …nge y 978 de pulmón, Lancashire, 1974–1983, en 315.16 km². **Por qué i… | ayuda de spatstat.data (recomputo › chorley.ayuda): «between 1974 and 1983» | REFERENCIA · ficha de ayuda del paquete |
| `315.16` | cuerpo | …de pulmón, Lancashire, 1974–1983, en 315.16 km². **Por qué importa:** … | recomputo › chorley.area_km2 = 315.1553 | VERIFICADA · re-ejecutada en R |
| `1990` | cuerpo | ….16 km². **Por qué importa:** Diggle (1990) buscaba más cáncer de lari… | ayuda de spatstat.data (recomputo › chorley.ayuda): «Diggle (1990)» | REFERENCIA · ficha de ayuda del paquete |
| `1990` | notas | …Datos de spatstat.data (Diggle, 1990). El propósito original, segú… | ayuda de spatstat.data (recomputo › chorley.ayuda): «Diggle (1990)» | REFERENCIA · ficha de ayuda del paquete |
| `0.3389` | notas | …rador, solo el cociente. El máximo de 0.3389 cae donde casi no hay pun… | datos › m6.chorley.p_max = 0.3388509631; recomputo › chorley.maximo = 0.3388509631 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `4` | notas | …casi no hay puntos: en el máximo solo 4 de los 50 vecinos más próximo… | recomputo › chorley.vecinos_casos = 4 | VERIFICADA · re-ejecutada en R |
| `50` | notas | …ay puntos: en el máximo solo 4 de los 50 vecinos más próximos son caso… | recomputo › chorley.vecinos_k = 50 | VERIFICADA · re-ejecutada en R |
| `4.6` | notas | …ás cercano al píxel del máximo está a 4.6 km (con σ = 1 km). Es la col… | recomputo › chorley.max_dist_punto_mas_cercano_km = 4.596178586 | VERIFICADA · re-ejecutada en R |

### Diapositiva 37 · Los casos se llaman `larynx` y los controles `lung`. ¿Qué probabilidad pinta `relrisk`?

| Cifra | Dónde | Contexto | Comprobación | Estado |
|---|---|---|---|---|
| `0.9518` | cuerpo | …pa de es P(pulmón): la mediana sale 0.9518 en vez de 0.0482. σ cambia … | recomputo › chorley.mediana_sin_fijar_niveles = 0.9518150519 | VERIFICADA · re-ejecutada en R |
| `0.0482` | cuerpo | …ón): la mediana sale 0.9518 en vez de 0.0482. σ cambia lo suave que sa… | datos › m6.chorley.p_mediana = 0.0481849481; recomputo › chorley.mediana = 0.04818494813 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `0.9518` | notas | …sitiva siguiente sea su respuesta. El 0.9518 se comprobó en R. Cotejo:… | recomputo › chorley.mediana_sin_fijar_niveles = 0.9518150519 | VERIFICADA · re-ejecutada en R |

### Diapositiva 38 · La trampa: todo corre, nada avisa y el mapa sale al revés

| Cifra | Dónde | Contexto | Comprobación | Estado |
|---|---|---|---|---|
| `0.9518` | cuerpo | …e es **P(pulmón)**: la mediana sale 0.9518 en vez de 0.0482. Con el or… | recomputo › chorley.mediana_sin_fijar_niveles = 0.9518150519 | VERIFICADA · re-ejecutada en R |
| `0.0482` | cuerpo | …)**: la mediana sale 0.9518 en vez de 0.0482. Con el orden fijado, en … | datos › m6.chorley.p_mediana = 0.0481849481; recomputo › chorley.mediana = 0.04818494813 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `50` | cuerpo | …Con el orden fijado, en el máximo los 50 vecinos más próximos son caso… | recomputo › chorley.vecinos_k = 50 | VERIFICADA · re-ejecutada en R |
| `8` | cuerpo | …ecinos más próximos son casos en un **8 %** (4 de 50) contra **5.6 %*… | 100 × orientación del máximo de chorley = 8 \| 100 × vecinos casos / 50 = 8 | VERIFICADA · aritmética sobre cifras verificadas |
| `4` | cuerpo | …más próximos son casos en un **8 %** (4 de 50) contra **5.6 %** en el… | recomputo › chorley.vecinos_casos = 4 | VERIFICADA · re-ejecutada en R |
| `50` | cuerpo | …róximos son casos en un **8 %** (4 de 50) contra **5.6 %** en el conju… | recomputo › chorley.vecinos_k = 50 | VERIFICADA · re-ejecutada en R |
| `5.6` | cuerpo | …asos en un **8 %** (4 de 50) contra **5.6 %** en el conjunto. ::: :::… | 100 × proporción global de chorley = 5.5984556 | VERIFICADA · aritmética sobre cifras verificadas |
| `50` | notas | …a primera; la segunda se hace con los 50 vecinos más próximos al máxim… | recomputo › chorley.vecinos_k = 50 | VERIFICADA · re-ejecutada en R |
| `8` | notas | …itariamente» de ese tipo; en son el 8 %, así que la comprobación qu… | 100 × orientación del máximo de chorley = 8 \| 100 × vecinos casos / 50 = 8 | VERIFICADA · aritmética sobre cifras verificadas |

### Diapositiva 39 · En Bogotá no es riesgo, es proporción de tipo: nadie «contrae» ser oficial

| Cifra | Dónde | Contexto | Comprobación | Estado |
|---|---|---|---|---|
| `2107` | cuerpo | …ndo otra cosa. **De dónde sale:** las 2 107 sedes urbanas por sector (… | datos › m5.capas.oferta.n = 2107; recomputo › urbana.n_urbana = 2107 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `720` | cuerpo | …7 sedes urbanas por sector (SED); σ = 720 m (el valor por defecto de )… | datos › m5.sigma_m = 720.3691455; recomputo › capas.sigma_m = 720.3691455 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `709` | cuerpo | …sos y controles. ::: ::: info Dato **709** oficiales + **1 398** priva… | datos › m6.bogota.oficiales = 709; recomputo › oficial.n_oficiales = 709 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `1398` | cuerpo | …::: info Dato **709** oficiales + **1 398** privadas = 2 107. Escala f… | datos › m6.bogota.privadas = 1398; recomputo › oficial.n_privadas = 1398 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `2107` | cuerpo | …09** oficiales + **1 398** privadas = 2 107. Escala fija de 0 a 1: mar… | datos › m5.capas.oferta.n = 2107; recomputo › urbana.n_urbana = 2107 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `50` | cuerpo | …ales. En el máximo de P(oficial), los 50 vecinos más próximos son ofic… | recomputo › chorley.vecinos_k = 50 | VERIFICADA · re-ejecutada en R |
| `64` | cuerpo | …os más próximos son oficiales en un **64 %** (32 de 50) contra **33.65… | 100 × orientación del máximo de Bogotá = 64 \| 100 × vecinos oficiales / 50 = 64 | VERIFICADA · aritmética sobre cifras verificadas |
| `32` | cuerpo | …róximos son oficiales en un **64 %** (32 de 50) contra **33.65 %** en… | recomputo › oficial.vecinos_oficiales = 32 | VERIFICADA · re-ejecutada en R |
| `50` | cuerpo | …s son oficiales en un **64 %** (32 de 50) contra **33.65 %** en el con… | recomputo › chorley.vecinos_k = 50 | VERIFICADA · re-ejecutada en R |
| `33.65` | cuerpo | …es en un **64 %** (32 de 50) contra **33.65 %** en el conjunto. :::… | 100 × proporción global de oficiales = 33.64973897 | VERIFICADA · aritmética sobre cifras verificadas |

### Diapositiva 40 · Contar puntos da 0.3365; mirar el mapa da 0.3086: son dos preguntas distintas

| Cifra | Dónde | Contexto | Comprobación | Estado |
|---|---|---|---|---|
| `0.3365` | titulo | …Contar puntos da 0.3365; mirar el mapa da 0.3086: son… | datos › m6.bogota.prop_global = 0.3364973897; recomputo › oficial.global = 0.3364973897 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `0.3086` | titulo | …ar puntos da 0.3365; mirar el mapa da 0.3086: son dos preguntas distin… | datos › m6.bogota.p_mediana = 0.3086251338; recomputo › oficial.mediana = 0.3086251338 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `2107` | cuerpo | …los puntos \|\|\| ::: info Dato · las 2 107 sedes urbanas 709 / 2 107 … | datos › m5.capas.oferta.n = 2107; recomputo › urbana.n_urbana = 2107 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `709` | cuerpo | …: info Dato · las 2 107 sedes urbanas 709 / 2 107 = **0.3365** (contan… | datos › m6.bogota.oficiales = 709; recomputo › oficial.n_oficiales = 709 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `2107` | cuerpo | …Dato · las 2 107 sedes urbanas 709 / 2 107 = **0.3365** (contando punt… | datos › m5.capas.oferta.n = 2107; recomputo › urbana.n_urbana = 2107 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `0.3365` | cuerpo | …s 2 107 sedes urbanas 709 / 2 107 = **0.3365** (contando puntos). Medi… | datos › m6.bogota.prop_global = 0.3364973897; recomputo › oficial.global = 0.3364973897 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `0.3086` | cuerpo | …diana de la superficie P(oficial) = **0.3086** (contando área). Las of… | datos › m6.bogota.p_mediana = 0.3086251338; recomputo › oficial.mediana = 0.3086251338 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `0.5` | cuerpo | …iciales son mayoría, con P(oficial) > 0.5, en el **17.5 %** del área. … | umbral de mayoría de P(oficial): más de la mitad | PARÁMETRO de diseño |
| `17.5` | cuerpo | …ayoría, con P(oficial) > 0.5, en el **17.5 %** del área. ::: ::: tip I… | recomputo › oficial.area_mayoria_oficial_pct = 17.45933385 | VERIFICADA · re-ejecutada en R |
| `0.028` | cuerpo | …untos, pero la diferencia es pequeña (0.028) y las dos cifras contesta… | \|mediana − global\| en el JSON = 0.0278722558 \| recomputo › oficial.brecha = 0.02787225584 | VERIFICADA · re-ejecutada en R |
| `17.5` | cuerpo | …ción de la ciudad son mayoría?» es el 17.5 %. ::: Fuente: del capítu… | recomputo › oficial.area_mayoria_oficial_pct = 17.45933385 | VERIFICADA · re-ejecutada en R |
| `0.028` | notas | …La diferencia es pequeña (0.028) pero tiene signo. Un informe… | \|mediana − global\| en el JSON = 0.0278722558 \| recomputo › oficial.brecha = 0.02787225584 | VERIFICADA · re-ejecutada en R |
| `17.5` | notas | …ión de área con mayoría oficial es el 17.5 %. La misma desigualdad apa… | recomputo › oficial.area_mayoria_oficial_pct = 17.45933385 | VERIFICADA · re-ejecutada en R |
| `0.0482` | notas | …. La misma desigualdad aparece con (0.0482 contra 0.0560): es en parte… | datos › m6.chorley.p_mediana = 0.0481849481; recomputo › chorley.mediana = 0.04818494813 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `0.0560` | notas | …igualdad aparece con (0.0482 contra 0.0560): es en parte un rasgo de c… | datos › m6.chorley.prop_global = 0.055984556; recomputo › chorley.global = 0.05598455598 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |

### Diapositiva 44 · Práctica: dos ejercicios guiados, el simulacro del Quiz 2 y la próxima sesión

| Cifra | Dónde | Contexto | Comprobación | Estado |
|---|---|---|---|---|
| `0.5` | cuerpo | …La masa que se escapa** — , con σ = 0.5, 1 y 2: la integral de las tr… | texto del capítulo: «sigma = 0.5, 1 y 2» | CONTRASTADA · texto del capítulo |
