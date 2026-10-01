# Registro de cifras · Capítulo 4 · Patrones puntuales

Generado por `verifica_cifras.py` a partir de `capitulo_4.md`. **No se edita a mano**: se regenera.

## Cómo se comprobó cada cifra

| Estado | Qué significa |
|---|---|
| VERIFICADA · recómputo independiente | La cifra sale del JSON de R **y** se recalculó desde los puntos crudos (`precalculo/salidas/*.csv`) con scipy, sin pasar por R ni por spatstat, y coincide. |
| VERIFICADA · aritmética sobre el JSON | Se recompone con una cuenta a partir de otras cifras del JSON. |
| CONTRASTADA · salida de R (JSON) | Coincide con `cap4_datos.json` / `cap4_soluciones.json`, redondeada a los decimales que se muestran. No se pudo recalcular aquí (depende de la geometría de la ventana, que no se versiona, o de estimadores internos de spatstat). |
| CONTRASTADA · texto del capítulo | Solo figura en la prosa del capítulo publicado; la frase existe en el HTML. |
| PARÁMETRO de diseño | Rejillas, semillas, niveles: decisiones del capítulo, cotejadas con el JSON cuando el JSON las trae. |
| REFERENCIA externa cotejada | Año, revista y páginas de una referencia; cotejados por búsqueda web el 2026-09-29 (URL en el detalle). |
| **[SIN VERIFICAR]** | No se pudo comprobar aquí. Lleva la marca en la diapositiva y no se presenta como dato confirmado. |

Los enteros 0, 1 y 2 usados como constantes de definición («R < 1», «1 − G») no se registran: no son mediciones.

## Resumen

- 312 apariciones de cifras en 35 diapositivas; 173 cifras distintas.
- CONTRASTADA · salida de R (JSON): 108
- VERIFICADA · recómputo independiente: 82
- VERIFICADA · aritmética sobre el JSON: 52
- REFERENCIA externa cotejada: 31
- PARÁMETRO de diseño: 23
- CONTRASTADA · texto del capítulo: 13
- [SIN VERIFICAR]: 3

## Hallazgos en el material del capítulo

Discrepancias que aparecieron al cotejar. No son errores de la presentación: se dicen aquí y en las notas, y no se corrigen en silencio.

- **Sitios con sedes coincidentes.** El módulo 7 dice que las 79 sedes coincidentes están «repartidas en 40 sitios». Recomputado con las coordenadas de `cap4_bogota_urbana.csv`: son **39** sitios (38 con dos sedes y 1 con tres). El 40 es `n − distintos` = 2 107 − 2 067, el número de sedes «sobrantes» (`m7.duplicados.repetidos`), no el de sitios. La diapositiva no cita el número de sitios.
- **«Tres decisiones» frente a «cuatro».** El módulo 1 llama a la ventana «la primera de las tres decisiones que este capítulo obliga a declarar»; los módulos 11 y 12 hablan de «cuatro piezas» y «cuatro cosas» (ventana, escala, borde, referencia). La presentación no dice un número en el módulo 1 y usa las cuatro en la tesis.
- **Sesgo máximo de K sin corregir.** El módulo 10 da 29.60530 % (`m10.sesgo_max_pct`) y la solución del ejercicio 5, 29.60510 % (`e5.solucion.sesgo_max_pct`). Se miden en rejillas distintas; las dos redondean a 29.6 %, que es lo que se proyecta.
- **Tasas de salida de la banda con cinco decimales.** El módulo 11 escribe 52.25230 %, 52.15220 % y 51.05110 %. El JSON guarda 52.2523, 52.1522 y 51.0511 (cuatro decimales) y los valores exactos son 522/999 = 52.25225…, 521/999 = 52.15215… y 510/999 = 51.05105…: el cero final es relleno. La diapositiva usa cuatro decimales.
- **Desvío máximo de L − r en los pinos japoneses.** El JSON publica −0.01473; el recómputo exacto con los puntos crudos da −0.01485 (misma r = 0.1475). No es un error: la curva se publica en una rejilla de 101 nodos re-muestreada desde la nativa de spatstat (513 nodos) y los pinos tienen coordenadas a dos decimales, con muchas parejas exactamente sobre un nodo. Coinciden en signo, en r y a dos cifras (−0.015).

## Cifra por cifra

### Diapositiva 1 · Portada

| Cifra | Dónde | Contexto | Comprobación | Estado |
|---|---|---|---|---|
| `90` | cuerpo | …etiqueta: Clase magistral · 90 min objetivo: En un patrón pu… | duración de la clase pedida por el docente (90 min); no es un dato del capítulo | PARÁMETRO de diseño |

### Diapositiva 3 · Cómo leer esta clase

| Cifra | Dónde | Contexto | Comprobación | Estado |
|---|---|---|---|---|
| `0.82371` | notas | …ué diferencia hay entre decir «R vale 0.82371» y decir «las sedes se a… | datos › m3.bogota.clark_evans = 0.8237083333; recómputo independiente «ce:bogota» = 0.8237083333 | VERIFICADA · recómputo independiente |

### Diapositiva 4 · Cada cifra trae su fuente y cada afirmación, su etiqueta

| Cifra | Dónde | Contexto | Comprobación | Estado |
|---|---|---|---|---|
| `3.5.1` | cuerpo | …y es , generados con R (spatstat 3.5.1) en . El cotejo de cada cifr… | datos › meta.paquetes.spatstat = 3.5.1 | CONTRASTADA · salida de R (JSON) |

### Diapositiva 6 · La ventana forma parte del estimador

| Cifra | Dónde | Contexto | Comprobación | Estado |
|---|---|---|---|---|
| `2209` | cuerpo | …> Tenemos 2 209 sedes educativas de Bogotá y… | datos › m1.sedes_total = 2209 \| sedes dentro + fuera de la ventana urbana = 2209 | VERIFICADA · aritmética sobre el JSON |

### Diapositiva 7 · En un patrón puntual lo aleatorio es el dónde, y la ventana forma parte del estimador

| Cifra | Dónde | Contexto | Comprobación | Estado |
|---|---|---|---|---|
| `2209` | cuerpo | …según la ventana. **De dónde sale:** 2 209 sedes georreferenciadas y e… | datos › m1.sedes_total = 2209 \| sedes dentro + fuera de la ventana urbana = 2209 | VERIFICADA · aritmética sobre el JSON |
| `12.25` | cuerpo | …atos Abiertos Bogotá / IDECA, versión 12.25). **Por qué importa:** es … | datos › m3.bogota.fuente = SED Bogotá 12.25, ventana urbana \| versión de la fuente (FUENTES.md, fuente 3) | CONTRASTADA · salida de R (JSON) |

### Diapositiva 8 · Misma ciudad, mismo dato, dos ventanas: 5.69321 sedes/km² contra 1.35200

| Cifra | Dónde | Contexto | Comprobación | Estado |
|---|---|---|---|---|
| `5.69321` | titulo | …sma ciudad, mismo dato, dos ventanas: 5.69321 sedes/km² contra 1.35200… | datos › m1.urbana.lambda_km2 = 5.693212583; recómputo independiente «lam_urb» = 5.693212582 | VERIFICADA · recómputo independiente |
| `1.35200` | titulo | …os ventanas: 5.69321 sedes/km² contra 1.35200… | datos › m1.dc.lambda_km2 = 1.351996437 \| n / área del D.C. = 1.351996437 | VERIFICADA · aritmética sobre el JSON |
| `2107` | cuerpo | …---\|---\|---\|---\| \| Perímetro urbano \| 2 107 \| 370.08982 \| 5.69… | datos › m1.urbana.n = 2107; recómputo independiente «n_bog» = 2107 | VERIFICADA · recómputo independiente |
| `370.08982` | cuerpo | …---\|---\| \| Perímetro urbano \| 2 107 \| 370.08982 \| 5.69321 \| \| … | datos › m1.urbana.area_km2 = 370.0898165 | CONTRASTADA · salida de R (JSON) |
| `5.69321` | cuerpo | …erímetro urbano \| 2 107 \| 370.08982 \| 5.69321 \| \| Distrito Capita… | datos › m1.urbana.lambda_km2 = 5.693212583; recómputo independiente «lam_urb» = 5.693212582 | VERIFICADA · recómputo independiente |
| `2208` | cuerpo | …8982 \| 5.69321 \| \| Distrito Capital \| 2 208 \| 1633.14040 \| 1.352… | datos › m1.dc.n = 2208 \| soluciones › e1.solucion.dc.n = 2208 | CONTRASTADA · salida de R (JSON) |
| `1633.14040` | cuerpo | ….69321 \| \| Distrito Capital \| 2 208 \| 1633.14040 \| 1.35200 \| Las… | datos › m1.dc.area_km2 = 1633.140399 | CONTRASTADA · salida de R (JSON) |
| `1.35200` | cuerpo | …strito Capital \| 2 208 \| 1633.14040 \| 1.35200 \| Las dos intensidad… | datos › m1.dc.lambda_km2 = 1.351996437 \| n / área del D.C. = 1.351996437 | VERIFICADA · aritmética sobre el JSON |
| `4.21097` | cuerpo | …intensidades se llevan un factor de **4.21097**. ::: ::: warn Criterio… | datos › m1.factor_lambda = 4.21096715 \| λ urbana / λ D.C. = 4.21096715 | VERIFICADA · aritmética sobre el JSON |
| `4.79355` | notas | …l cambio: el numerador sube apenas un 4.79355 %, porque el suelo rural… | datos › m1.aumento_n_pct = 4.793545325 \| (n D.C. − n urbana) / n urbana · 100 = 4.793545325 | VERIFICADA · aritmética sobre el JSON |
| `4.41282` | notas | …s, y el denominador se multiplica por 4.41282. Ninguna de las dos cifr… | datos › m1.cociente_area = 4.412821769 \| área D.C. / área urbana = 4.412821769 | VERIFICADA · aritmética sobre el JSON |

### Diapositiva 9 · Un informe dice «5,7 colegios por km²»: ¿qué le falta para estar completo?

| Cifra | Dónde | Contexto | Comprobación | Estado |
|---|---|---|---|---|
| `5.7` | titulo | …Un informe dice «5,7 colegios por km²»: ¿qué le fa… | 5,7 = λ urbana (5.6932) redondeada a 1 decimal = 5.693212583 | VERIFICADA · aritmética sobre el JSON |
| `5.6932` | cuerpo | …ventana Con el perímetro urbano salen 5.6932 sedes/km²; con el Distrit… | datos › m1.urbana.lambda_km2 = 5.693212583 | CONTRASTADA · salida de R (JSON) |
| `1.3520` | cuerpo | …/km²; con el Distrito Capital entero, 1.3520: mismo dato, factor 4.21.… | datos › m1.dc.lambda_km2 = 1.351996437 | CONTRASTADA · salida de R (JSON) |
| `4.21` | cuerpo | …al entero, 1.3520: mismo dato, factor 4.21. Dar el total no arregla na… | datos › m1.factor_lambda = 4.21096715 | CONTRASTADA · salida de R (JSON) |
| `4.8` | cuerpo | …egla nada: el recuento apenas sube un 4.8 % entre las dos ventanas y l… | datos › m1.aumento_n_pct = 4.793545325 | CONTRASTADA · salida de R (JSON) |
| `0.0569` | notas | …porque en hectáreas la misma cifra es 0.0569 y sigue dependiendo de la… | datos › m2.lambda_urbana_ha = 0.0569321258 | CONTRASTADA · salida de R (JSON) |

### Diapositiva 10 · Con λ = 5.6932 sedes/km² no basta: ese número solo sirve si λ es constante

| Cifra | Dónde | Contexto | Comprobación | Estado |
|---|---|---|---|---|
| `5.6932` | titulo | …Con λ = 5.6932 sedes/km² no basta: ese númer… | datos › m1.urbana.lambda_km2 = 5.693212583 | CONTRASTADA · salida de R (JSON) |
| `10x10` | cuerpo | …su área. \|\|\| ::: info Dato Rejilla 10×10: **65** celdas «vivas» (co… | rejilla 10×10 del módulo 2 = [10] | PARÁMETRO de diseño |
| `65` | cuerpo | …rea. \|\|\| ::: info Dato Rejilla : **65** celdas «vivas» (con algo de… | datos › m2.urbana.celdas = 65 | CONTRASTADA · salida de R (JSON) |
| `32.41538` | cuerpo | …n algo de área dentro de la ventana), 32.41538 sedes por celda de prom… | datos › m2.urbana.media = 32.41538462 \| sedes / celdas vivas = 32.41538462 | VERIFICADA · aritmética sobre el JSON |
| `96` | cuerpo | …a de promedio; la más poblada tiene **96** y **9** están vacías. :::… | datos › m2.urbana.maximo = 96 | CONTRASTADA · salida de R (JSON) |
| `9` | cuerpo | …edio; la más poblada tiene **96** y **9** están vacías. ::: ::: tip… | datos › m2.urbana.vacios = 9 | CONTRASTADA · salida de R (JSON) |
| `2107` | cuerpo | …fórmula: \begin{aligned}\hat{\lambda} &= \frac{n}{\|W\|} = \frac{2\,10… | datos › m1.urbana.n = 2107; recómputo independiente «n_bog» = 2107 | VERIFICADA · recómputo independiente |
| `370.09` | cuerpo | …fórmula: \begin{aligned}\hat{\lambda} &= \frac{n}{\|W\|} = \frac{2\,10… | datos › m1.urbana.area_km2 = 370.0898165 | CONTRASTADA · salida de R (JSON) |
| `5.6932` | cuerpo | …fórmula: \begin{aligned}\hat{\lambda} &= \frac{n}{\|W\|} = \frac{2\,10… | datos › m1.urbana.lambda_km2 = 5.693212583 | CONTRASTADA · salida de R (JSON) |
| `5.6932` | notas | …e se puede escribir en tres unidades: 5.6932 por km², 0.05693 por ha o… | datos › m1.urbana.lambda_km2 = 5.693212583 | CONTRASTADA · salida de R (JSON) |
| `0.05693` | notas | …bir en tres unidades: 5.6932 por km², 0.05693 por ha o 0.0000056932 po… | datos › m2.lambda_urbana_ha = 0.0569321258 | CONTRASTADA · salida de R (JSON) |
| `0.0000056932` | notas | …des: 5.6932 por km², 0.05693 por ha o 0.0000056932 por m². El CRS del … | datos › m2.lambda_urbana_m2 = 5.6932e-06 | CONTRASTADA · salida de R (JSON) |
| `25.90966` | notas | …a además que el índice de dispersión (25.90966) no se compara con 1 si… | datos › m2.urbana.dispersion = 25.90966125 | CONTRASTADA · salida de R (JSON) |
| `15.22998` | notas | …5.90966) no se compara con 1 sino con 15.22998, porque la ventana reco… | datos › m2.urbana.dispersion_nula = 15.22998113 | CONTRASTADA · salida de R (JSON) |

### Diapositiva 12 · Los tres regímenes canónicos de la literatura se distinguen a simple vista

| Cifra | Dónde | Contexto | Comprobación | Estado |
|---|---|---|---|---|
| `42` | cuerpo | …ulas biológicas (Crick y Ripley), n = 42 **Regular** ::: tip Interpr… | datos › m3.cells.n = 42; recómputo independiente «n:cells» = 42 | VERIFICADA · recómputo independiente |
| `1961` | cuerpo | …s. ::: \|\|\| Pinos japoneses (Numata, 1961), n = 65 **Aleatorio** :::… | Numata (1961): saplings de pino negro japonés, `japanesepines`; 65 puntos · https://www.quantargo.com/help/r/latest/packages/spatstat.data/2.1-0/japanesepines | REFERENCIA externa cotejada |
| `65` | cuerpo | …Pinos japoneses (Numata, 1961), n = 65 **Aleatorio** ::: tip Inter… | datos › m3.japanesepines.n = 65; recómputo independiente «n:japanesepines» = 65 | VERIFICADA · recómputo independiente |
| `1975` | cuerpo | …\|\|\| Plántulas de secuoya (Strauss, 1975; Ripley, 1977), n = 62 **Ag… | Strauss (1975): `redwood`; 62 plántulas (subconjunto de Ripley) · https://rdrr.io/cran/spatstat.data/man/redwood.html | REFERENCIA externa cotejada |
| `1977` | cuerpo | …as de secuoya (Strauss, 1975; Ripley, 1977), n = 62 **Agregado** ::: t… | Ripley (1977): subconjunto de `redwood` reescalado al cuadrado unidad · https://rdrr.io/cran/spatstat.data/man/redwood.html | REFERENCIA externa cotejada |
| `62` | cuerpo | …ya (Strauss, 1975; Ripley, 1977), n = 62 **Agregado** ::: tip Interp… | datos › m3.redwood.n = 62; recómputo independiente «n:redwood» = 62 | VERIFICADA · recómputo independiente |
| `1961` | notas | …y Ripley; pinos japoneses de Numata, 1961; secuoyas de Strauss, 1975, … | Numata (1961): saplings de pino negro japonés, `japanesepines`; 65 puntos · https://www.quantargo.com/help/r/latest/packages/spatstat.data/2.1-0/japanesepines | REFERENCIA externa cotejada |
| `1975` | notas | …de Numata, 1961; secuoyas de Strauss, 1975, en el subconjunto de Riple… | Strauss (1975): `redwood`; 62 plántulas (subconjunto de Ripley) · https://rdrr.io/cran/spatstat.data/man/redwood.html | REFERENCIA externa cotejada |
| `1977` | notas | …s, 1975, en el subconjunto de Ripley, 1977). Por qué importan: son los… | Ripley (1977): subconjunto de `redwood` reescalado al cuadrado unidad · https://rdrr.io/cran/spatstat.data/man/redwood.html | REFERENCIA externa cotejada |

### Diapositiva 13 · Clark-Evans: R < 1 indica agregación y R > 1, regularidad

| Cifra | Dónde | Contexto | Comprobación | Estado |
|---|---|---|---|---|
| `42` | cuerpo | …---\|---\| \| Células \| Crick y Ripley \| 42 \| **1.67168** \| regula… | datos › m3.cells.n = 42; recómputo independiente «n:cells» = 42 | VERIFICADA · recómputo independiente |
| `1.67168` | cuerpo | …\| \| Células \| Crick y Ripley \| 42 \| **1.67168** \| regular \| \| … | datos › m3.cells.clark_evans = 1.671679515; recómputo independiente «ce:cells» = 1.671679515 | VERIFICADA · recómputo independiente |
| `1972` | cuerpo | …\| regular \| \| Pinos suecos \| Strand (1972) \| 71 \| **1.36008** \|… | Strand (1972): `swedishpines`; 71 árboles en una parcela de 9.6 × 10 m · https://rdrr.io/cran/spatstat.data/man/swedishpines.html | REFERENCIA externa cotejada |
| `71` | cuerpo | …ar \| \| Pinos suecos \| Strand (1972) \| 71 \| **1.36008** \| regular… | datos › m3.swedishpines.n = 71; recómputo independiente «n:swedishpines» = 71 | VERIFICADA · recómputo independiente |
| `1.36008` | cuerpo | …Pinos suecos \| Strand (1972) \| 71 \| **1.36008** \| regular \| \| Pi… | datos › m3.swedishpines.clark_evans = 1.360081651; recómputo independiente «ce:swedishpines» = 1.360081651 | VERIFICADA · recómputo independiente |
| `1961` | cuerpo | …regular \| \| Pinos japoneses \| Numata (1961) \| 65 \| **1.06400** \|… | Numata (1961): saplings de pino negro japonés, `japanesepines`; 65 puntos · https://www.quantargo.com/help/r/latest/packages/spatstat.data/2.1-0/japanesepines | REFERENCIA externa cotejada |
| `65` | cuerpo | …\| \| Pinos japoneses \| Numata (1961) \| 65 \| **1.06400** \| aleator… | datos › m3.japanesepines.n = 65; recómputo independiente «n:japanesepines» = 65 | VERIFICADA · recómputo independiente |
| `1.06400` | cuerpo | …os japoneses \| Numata (1961) \| 65 \| **1.06400** \| aleatorio \| \| … | datos › m3.japanesepines.clark_evans = 1.064002055; recómputo independiente «ce:japanesepines» = 1.064002055 | VERIFICADA · recómputo independiente |
| `1975` | cuerpo | …* \| aleatorio \| \| Secuoyas \| Strauss (1975) \| 62 \| **0.61865** \… | Strauss (1975): `redwood`; 62 plántulas (subconjunto de Ripley) · https://rdrr.io/cran/spatstat.data/man/redwood.html | REFERENCIA externa cotejada |
| `62` | cuerpo | …torio \| \| Secuoyas \| Strauss (1975) \| 62 \| **0.61865** \| agregad… | datos › m3.redwood.n = 62; recómputo independiente «n:redwood» = 62 | VERIFICADA · recómputo independiente |
| `0.61865` | cuerpo | …\| Secuoyas \| Strauss (1975) \| 62 \| **0.61865** \| agregado \| \| S… | datos › m3.redwood.clark_evans = 0.6186501573; recómputo independiente «ce:redwood» = 0.6186501573 | VERIFICADA · recómputo independiente |
| `12.25` | cuerpo | …gregado \| \| Sedes de Bogotá \| SED, v. 12.25 \| 2 107 \| **0.82371**… | datos › m3.bogota.fuente = SED Bogotá 12.25, ventana urbana \| versión de la fuente (FUENTES.md, fuente 3) | CONTRASTADA · salida de R (JSON) |
| `2107` | cuerpo | …\| \| Sedes de Bogotá \| SED, v. 12.25 \| 2 107 \| **0.82371** \| agre… | datos › m1.urbana.n = 2107; recómputo independiente «n_bog» = 2107 | VERIFICADA · recómputo independiente |
| `0.82371` | cuerpo | …de Bogotá \| SED, v. 12.25 \| 2 107 \| **0.82371** \| agregado \| ::: … | datos › m3.bogota.clark_evans = 0.8237083333; recómputo independiente «ce:bogota» = 0.8237083333 | VERIFICADA · recómputo independiente |
| `1972` | notas | …s filas nuevas. Pinos suecos (Strand, 1972; 71 árboles): entran como s… | Strand (1972): `swedishpines`; 71 árboles en una parcela de 9.6 × 10 m · https://rdrr.io/cran/spatstat.data/man/swedishpines.html | REFERENCIA externa cotejada |
| `71` | notas | …s nuevas. Pinos suecos (Strand, 1972; 71 árboles): entran como segundo… | datos › m3.swedishpines.n = 71; recómputo independiente «n:swedishpines» = 71 | VERIFICADA · recómputo independiente |
| `9600` | notas | …entana no es el cuadrado unidad: mide 9 600 unidades², de ahí que sus … | datos › m3.swedishpines.area = 9600 | CONTRASTADA · salida de R (JSON) |

### Diapositiva 14 · CSR es un modelo con dos propiedades, y la primera es la que siempre se olvida

| Cifra | Dónde | Contexto | Comprobación | Estado |
|---|---|---|---|---|
| `65` | notas | …tiene una realización de CSR con λ = 65 en el cuadrado unidad? No hay… | datos › m4.lambda = 65 | CONTRASTADA · salida de R (JSON) |

### Diapositiva 15 · Dos mil realizaciones de CSR: n varía de 41 a 95, y media y varianza casi coinciden

| Cifra | Dónde | Contexto | Comprobación | Estado |
|---|---|---|---|---|
| `41` | titulo | …mil realizaciones de CSR: n varía de 41 a 95, y media y varianza casi… | datos › m4.conteo_min = 41; recómputo independiente «pois:min» = 41 | VERIFICADA · recómputo independiente |
| `95` | titulo | …realizaciones de CSR: n varía de 41 a 95, y media y varianza casi coin… | datos › m4.conteo_max = 95; recómputo independiente «pois:max» = 95 | VERIFICADA · recómputo independiente |
| `2000` | cuerpo | …2 000 realizaciones simuladas de CS… | datos › m4.n_realizaciones = 2000; recómputo independiente «pois:n» = 2000 | VERIFICADA · recómputo independiente |
| `4026` | cuerpo | …alizaciones simuladas de CSR (semilla 4026): conteos frente a la Poiss… | datos › meta.semillas.csr = 4026 | PARÁMETRO de diseño |
| `65` | cuerpo | …oisson teórica ::: info Dato Con λ = 65 en el cuadrado unidad: media… | datos › m4.lambda = 65 | CONTRASTADA · salida de R (JSON) |
| `64.979` | cuerpo | …λ = 65 en el cuadrado unidad: media **64.979**, varianza **67.673**, r… | datos › m4.conteo_media = 64.979; recómputo independiente «pois:media» = 64.979 | VERIFICADA · recómputo independiente |
| `67.673` | cuerpo | …unidad: media **64.979**, varianza **67.673**, recorrido de 41 a 95 pu… | datos › m4.conteo_var = 67.6733957; recómputo independiente «pois:var» = 67.6733957 | VERIFICADA · recómputo independiente |
| `41` | cuerpo | …**, varianza **67.673**, recorrido de 41 a 95 puntos. ::: ::: tip Int… | datos › m4.conteo_min = 41; recómputo independiente «pois:min» = 41 | VERIFICADA · recómputo independiente |
| `95` | cuerpo | …arianza **67.673**, recorrido de 41 a 95 puntos. ::: ::: tip Interpre… | datos › m4.conteo_max = 95; recómputo independiente «pois:max» = 95 | VERIFICADA · recómputo independiente |
| `2000` | notas | …na realización a otra. De dónde sale: 2 000 realizaciones simuladas co… | datos › m4.n_realizaciones = 2000; recómputo independiente «pois:n» = 2000 | VERIFICADA · recómputo independiente |
| `4026` | notas | …ladas con de spatstat en R, semilla 4026, no es un dato observado. Por… | datos › meta.semillas.csr = 4026 | PARÁMETRO de diseño |

### Diapositiva 16 · Una R de 0.95 en una realización de CSR: ¿qué se concluye?

| Cifra | Dónde | Contexto | Comprobación | Estado |
|---|---|---|---|---|
| `0.95` | titulo | …Una R de 0.95 en una realización de CSR: ¿q… | R = 0.95 es el valor hipotético del enunciado del cuestionario del capítulo | CONTRASTADA · texto del capítulo |
| `2000` | cuerpo | …de lo que el azar produce a menudo En 2 000 realizaciones de azar puro… | datos › m4.n_realizaciones = 2000; recómputo independiente «pois:n» = 2000 | VERIFICADA · recómputo independiente |
| `0.83013` | cuerpo | …aciones de azar puro, R recorrió de **0.83013** a **1.34170** (95 % ce… | datos › m4.R_csr.min = 0.8301277262 | CONTRASTADA · salida de R (JSON) |
| `1.34170` | cuerpo | …r puro, R recorrió de **0.83013** a **1.34170** (95 % central: 0.91306… | datos › m4.R_csr.max = 1.341696623 | CONTRASTADA · salida de R (JSON) |
| `95` | cuerpo | …ecorrió de **0.83013** a **1.34170** (95 % central: 0.91306 a 1.20460)… | intervalo central del 95 % (cuantiles 0.025 y 0.975 de R bajo CSR) = 95 | PARÁMETRO de diseño |
| `0.91306` | cuerpo | ….83013** a **1.34170** (95 % central: 0.91306 a 1.20460) y **438** que… | datos › m4.R_csr.q025 = 0.913064206 | CONTRASTADA · salida de R (JSON) |
| `1.20460` | cuerpo | …**1.34170** (95 % central: 0.91306 a 1.20460) y **438** quedaron por d… | datos › m4.R_csr.q975 = 1.204598272 | CONTRASTADA · salida de R (JSON) |
| `438` | cuerpo | …(95 % central: 0.91306 a 1.20460) y **438** quedaron por debajo de 1. … | datos › m4.R_csr.bajo_1 = 438 | CONTRASTADA · salida de R (JSON) |
| `1.05843` | cuerpo | …* quedaron por debajo de 1. La media, 1.05843, no es 1: es sesgo de bo… | datos › m4.R_csr.media = 1.058425578 | CONTRASTADA · salida de R (JSON) |
| `1.06400` | cuerpo | …rregido, los pinos japoneses bajan de 1.06400 a 1.00751. ::: ::: warn … | datos › m3.japanesepines.clark_evans = 1.064002055; recómputo independiente «ce:japanesepines» = 1.064002055 | VERIFICADA · recómputo independiente |
| `1.00751` | cuerpo | …os pinos japoneses bajan de 1.06400 a 1.00751. ::: ::: warn Criterio U… | datos › m3.japanesepines.clark_evans_donnelly = 1.007507243 | CONTRASTADA · salida de R (JSON) |
| `1.05843` | notas | …ber cuánto se mueve el azar. La media 1.05843 y los pinos japoneses (1… | datos › m4.R_csr.media = 1.058425578 | CONTRASTADA · salida de R (JSON) |
| `1.06400` | notas | …media 1.05843 y los pinos japoneses (1.06400) casi coinciden: el «alea… | datos › m3.japanesepines.clark_evans = 1.064002055; recómputo independiente «ce:japanesepines» = 1.064002055 | VERIFICADA · recómputo independiente |

### Diapositiva 18 · El χ² de cuadrantes contrasta el Poisson homogéneo entero, no solo «λ constante»

| Cifra | Dónde | Contexto | Comprobación | Estado |
|---|---|---|---|---|
| `10^-59.5` | cuerpo | …de libertad y un p-valor del orden de 10<sup>-59.5</sup>. El test **re… | datos › m2.urbana.p_log10 = -59.4967268 | CONTRASTADA · salida de R (JSON) |
| `10x10` | cuerpo | …:: info Dato Sedes de Bogotá, rejilla 10×10: χ² = **456.12** con **64*… | rejilla 10×10 del módulo 2 = [10] | PARÁMETRO de diseño |
| `456.12` | cuerpo | …to Sedes de Bogotá, rejilla : χ² = **456.12** con **64** grados de lib… | datos › m2.urbana.chi2 = 456.1208855 | CONTRASTADA · salida de R (JSON) |
| `64` | cuerpo | …otá, rejilla : χ² = **456.12** con **64** grados de libertad y un p-v… | datos › m2.urbana.gl = 64 | CONTRASTADA · salida de R (JSON) |
| `12` | cuerpo | …l orden de . El test **rechaza**. **12** de las 65 celdas vivas espe… | datos › m2.urbana.celdas_esperanza_baja = 12 | CONTRASTADA · salida de R (JSON) |
| `65` | cuerpo | …. El test **rechaza**. **12** de las 65 celdas vivas esperan menos de… | datos › m2.urbana.celdas = 65 | CONTRASTADA · salida de R (JSON) |
| `5` | cuerpo | …las 65 celdas vivas esperan menos de 5 puntos: el χ² se apoya en un… | regla del capítulo: al menos 5 puntos esperados por celda | CONTRASTADA · texto del capítulo |
| `12` | notas | …omogéneo del . La advertencia de las 12 celdas la cobra el , dos dia… | datos › m2.urbana.celdas_esperanza_baja = 12 | CONTRASTADA · salida de R (JSON) |

### Diapositiva 19 · Dos patrones con el mismo χ² hasta el último decimal: 64.612903

| Cifra | Dónde | Contexto | Comprobación | Estado |
|---|---|---|---|---|
| `64.612903` | titulo | …el mismo χ² hasta el último decimal: 64.612903… | datos › m5.original.chi2 = 64.61290323; recómputo independiente «chi2:redwood:5» = 64.61290323 \| datos › m5.rebarajado.chi2 = 64.61290323 \| recómputo independiente «chi2:celdas_reb» = 64.61290323 | VERIFICADA · recómputo independiente |
| `5x5` | cuerpo | …oyas rebarajadas dentro de cada celda 5×5.… | rejilla 5×5 del módulo 5 = [5] | PARÁMETRO de diseño |
| `24` | cuerpo | …al \| Rebarajado \| \|---\|---\|---\| \| χ² (24 gl) \| 64.612903 \| 64… | datos › m5.original.gl = 24 \| gl = celdas − 1 = 5² − 1 = 24 | VERIFICADA · aritmética sobre el JSON |
| `64.612903` | cuerpo | …rajado \| \|---\|---\|---\| \| χ² (24 gl) \| 64.612903 \| 64.612903 \|… | datos › m5.original.chi2 = 64.61290323; recómputo independiente «chi2:redwood:5» = 64.61290323 \| datos › m5.rebarajado.chi2 = 64.61290323 \| recómputo independiente «chi2:celdas_reb» = 64.61290323 | VERIFICADA · recómputo independiente |
| `64.612903` | cuerpo | …-\|---\|---\| \| χ² (24 gl) \| 64.612903 \| 64.612903 \| \| Distancia … | datos › m5.original.chi2 = 64.61290323; recómputo independiente «chi2:redwood:5» = 64.61290323 \| datos › m5.rebarajado.chi2 = 64.61290323 \| recómputo independiente «chi2:celdas_reb» = 64.61290323 | VERIFICADA · recómputo independiente |
| `0.03928` | cuerpo | …12903 \| \| Distancia media al vecino \| 0.03928 \| 0.05755 \| \| R de… | datos › m5.nn_original = 0.0392843243; recómputo independiente «nn:redwood» = 0.03928432427 | VERIFICADA · recómputo independiente |
| `0.05755` | cuerpo | …Distancia media al vecino \| 0.03928 \| 0.05755 \| \| R de Clark-Evans… | datos › m5.nn_rebarajado = 0.0575452955; recómputo independiente «nn:reb» = 0.05754529554 | VERIFICADA · recómputo independiente |
| `0.61865` | cuerpo | …3928 \| 0.05755 \| \| R de Clark-Evans \| 0.61865 \| 0.90622 \| ::: ::… | datos › m3.redwood.clark_evans = 0.6186501573; recómputo independiente «ce:redwood» = 0.6186501573 | VERIFICADA · recómputo independiente |
| `0.90622` | cuerpo | …5755 \| \| R de Clark-Evans \| 0.61865 \| 0.90622 \| ::: ::: tip Inter… | datos › m5.ce_rebarajado = 0.9062242202; recómputo independiente «ce:reb» = 0.9062242204 | VERIFICADA · recómputo independiente |
| `5x5` | notas | …los conteos por celda de una rejilla 5×5 conservados y los puntos repa… | rejilla 5×5 del módulo 5 = [5] | PARÁMETRO de diseño |
| `1975` | notas | …De dónde sale: las secuoyas (Strauss, 1975; Ripley, 1977) con los cont… | Strauss (1975): `redwood`; 62 plántulas (subconjunto de Ripley) · https://rdrr.io/cran/spatstat.data/man/redwood.html | REFERENCIA externa cotejada |
| `1977` | notas | …las secuoyas (Strauss, 1975; Ripley, 1977) con los conteos por celda d… | Ripley (1977): subconjunto de `redwood` reescalado al cuadrado unidad · https://rdrr.io/cran/spatstat.data/man/redwood.html | REFERENCIA externa cotejada |
| `4027` | notas | …s al azar dentro de su celda, semilla 4027: es un patrón construido a … | datos › meta.semillas.ciego = 4027 | PARÁMETRO de diseño |
| `1.46484` | notas | …distancia al vecino se multiplica por 1.46484. Pasar el test de cuadra… | datos › m5.nn_cociente = 1.46484117 \| nn rebarajado / nn original = 1.464841168 | VERIFICADA · aritmética sobre el JSON |

### Diapositiva 20 · El veredicto cambia con el tamaño de la celda, pero solo cuando el patrón está en el filo

| Cifra | Dónde | Contexto | Comprobación | Estado |
|---|---|---|---|---|
| `2x2` | cuerpo | …Secuoyas: χ² por lado de rejilla, de 2×2 a 20×20. Gris: no rechaza al… | rejillas barridas en el módulo 6 = [2, 3, 4, 5, 6, 8, 10, 12, 15, 20] | PARÁMETRO de diseño |
| `20x20` | cuerpo | …yas: χ² por lado de rejilla, de 2×2 a 20×20. Gris: no rechaza al 5 %. … | rejillas barridas en el módulo 6 = [2, 3, 4, 5, 6, 8, 10, 12, 15, 20] | PARÁMETRO de diseño |
| `2x2` | cuerpo | …que no rechaza en las secuoyas es el 2×2: con cuatro celdas no hay res… | rejillas barridas en el módulo 6 = [2, 3, 4, 5, 6, 8, 10, 12, 15, 20] | PARÁMETRO de diseño |
| `5` | cuerpo | …ejilla, de a . Gris: no rechaza al 5 %. Naranja: rechaza. Pálido:… | nivel de significancia del 5 % = 5 | PARÁMETRO de diseño |
| `5` | cuerpo | …Pálido: alguna celda espera menos de 5 puntos ::: info Dato Rejilla… | regla del capítulo: al menos 5 puntos esperados por celda | CONTRASTADA · texto del capítulo |
| `10` | cuerpo | …: info Dato Rejillas que rechazan, de 10 tamaños: secuoyas **9**, pino… | número de tamaños de rejilla barridos = 10 | VERIFICADA · aritmética sobre el JSON |
| `9` | cuerpo | …e rechazan, de 10 tamaños: secuoyas **9**, pinos japoneses **0**, sed… | datos › m6.redwood_rechazos = 9 | CONTRASTADA · salida de R (JSON) |
| `10` | cuerpo | …os japoneses **0**, sedes de Bogotá **10**. ::: ::: tip Interpretació… | soluciones › e3.solucion.rechazos_urbana = 10 | CONTRASTADA · salida de R (JSON) |
| `10` | notas | …ente aleatorio (pinos japoneses: 0 de 10) o claramente inhomogéneo (Bo… | número de tamaños de rejilla barridos = 10 | VERIFICADA · aritmética sobre el JSON |
| `10` | notas | …10) o claramente inhomogéneo (Bogotá: 10 de 10), la elección no lo mue… | número de tamaños de rejilla barridos = 10 | VERIFICADA · aritmética sobre el JSON |
| `10` | notas | …claramente inhomogéneo (Bogotá: 10 de 10), la elección no lo mueve. Co… | número de tamaños de rejilla barridos = 10 | VERIFICADA · aritmética sobre el JSON |

### Diapositiva 21 · Afinar la rejilla rompe el supuesto del χ²: con 400 celdas el p-valor deja de mejorar

| Cifra | Dónde | Contexto | Comprobación | Estado |
|---|---|---|---|---|
| `400` | titulo | …rejilla rompe el supuesto del χ²: con 400 celdas el p-valor deja de me… | celdas de la rejilla 20×20 = 400 | VERIFICADA · aritmética sobre el JSON |
| `2x2` | cuerpo | …illa \| χ² \| p-valor \| \|---\|---\|---\| \| 2×2 \| 6.52 \| 0.17806 \… | rejillas barridas en el módulo 6 = [2, 3, 4, 5, 6, 8, 10, 12, 15, 20] | PARÁMETRO de diseño |
| `5x5` | cuerpo | …-\|---\|---\| \| 2×2 \| 6.52 \| 0.17806 \| \| 5×5 \| 64.61 \| 0.00003 … | rejilla 5×5 del módulo 5 = [5] | PARÁMETRO de diseño |
| `10x10` | cuerpo | …0.17806 \| \| 5×5 \| 64.61 \| 0.00003 \| \| 10×10 \| 202.52 \| 0.00000… | rejillas barridas en el módulo 6 = [2, 3, 4, 5, 6, 8, 10, 12, 15, 20] | PARÁMETRO de diseño |
| `20x20` | cuerpo | …0003 \| \| 10×10 \| 202.52 \| 0.00000 \| \| 20×20 \| 505.74 \| 0.00045… | rejillas barridas en el módulo 6 = [2, 3, 4, 5, 6, 8, 10, 12, 15, 20] | PARÁMETRO de diseño |
| `3x3` | cuerpo | …a que lo respeta *y* rechaza es la de 3×3: una de diez. ::: tip Interp… | rejillas barridas en el módulo 6 = [2, 3, 4, 5, 6, 8, 10, 12, 15, 20] | PARÁMETRO de diseño |
| `10` | cuerpo | …: info Dato · secuoyas, cuatro de las 10 rejillas \| Rejilla \| χ² \| … | número de tamaños de rejilla barridos = 10 | VERIFICADA · aritmética sobre el JSON |
| `6.52` | cuerpo | …\| χ² \| p-valor \| \|---\|---\|---\| \| \| 6.52 \| 0.17806 \| \| \| 6… | datos › m6.redwood.chi2 (nx = 2) = 6.516129032; recómputo independiente «chi2:redwood:2» = 6.516129032 | VERIFICADA · recómputo independiente |
| `0.17806` | cuerpo | …p-valor \| \|---\|---\|---\| \| \| 6.52 \| 0.17806 \| \| \| 64.61 \| 0… | datos › m6.redwood.p_valor (nx = 2) = 0.178057; recómputo independiente «p:redwood:2» = 0.178057161 | VERIFICADA · recómputo independiente |
| `64.61` | cuerpo | …---\|---\| \| \| 6.52 \| 0.17806 \| \| \| 64.61 \| 0.00003 \| \| \| 20… | datos › m6.redwood.chi2 (nx = 5) = 64.61290323; recómputo independiente «chi2:redwood:5» = 64.61290323 | VERIFICADA · recómputo independiente |
| `0.00003` | cuerpo | …\| \| 6.52 \| 0.17806 \| \| \| 64.61 \| 0.00003 \| \| \| 202.52 \| 0.0… | datos › m6.redwood.p_valor (nx = 5) = 2.77398e-05; recómputo independiente «p:redwood:5» = 2.773979396e-05 | VERIFICADA · recómputo independiente |
| `202.52` | cuerpo | …17806 \| \| \| 64.61 \| 0.00003 \| \| \| 202.52 \| 0.00000 \| \| \| 50… | datos › m6.redwood.chi2 (nx = 10) = 202.516129; recómputo independiente «chi2:redwood:10» = 202.516129 | VERIFICADA · recómputo independiente |
| `0.00000` | cuerpo | …\| 64.61 \| 0.00003 \| \| \| 202.52 \| 0.00000 \| \| \| 505.74 \| 0.00… | datos › m6.redwood.p_valor (nx = 10) = 8.4482e-09; recómputo independiente «p:redwood:10» = 8.4482e-09 (\|Δ\| ≤ 1e-06 respecto de 8.4482e-09) | VERIFICADA · recómputo independiente |
| `505.74` | cuerpo | …0003 \| \| \| 202.52 \| 0.00000 \| \| \| 505.74 \| 0.00045 \| ::: Solo… | datos › m6.redwood.chi2 (nx = 20) = 505.7419355; recómputo independiente «chi2:redwood:20» = 505.7419355 | VERIFICADA · recómputo independiente |
| `0.00045` | cuerpo | …\| 202.52 \| 0.00000 \| \| \| 505.74 \| 0.00045 \| ::: Solo las dos re… | datos › m6.redwood.p_valor (nx = 20) = 0.000449415; recómputo independiente «p:redwood:20» = 0.0004494149746 | VERIFICADA · recómputo independiente |
| `5` | cuerpo | …illas más gruesas respetan **al menos 5 puntos esperados por celda**,… | regla del capítulo: al menos 5 puntos esperados por celda | CONTRASTADA · texto del capítulo |
| `400` | cuerpo | …de diez. ::: tip Interpretación Con 400 celdas y 62 plántulas cada es… | celdas de la rejilla 20×20 = 400 | VERIFICADA · aritmética sobre el JSON |
| `62` | cuerpo | …: tip Interpretación Con 400 celdas y 62 plántulas cada esperanza es m… | datos › m3.redwood.n = 62; recómputo independiente «n:redwood» = 62 | VERIFICADA · recómputo independiente |
| `1975` | notas | …De dónde sale: las secuoyas (Strauss, 1975; Ripley, 1977), 62 puntos e… | Strauss (1975): `redwood`; 62 plántulas (subconjunto de Ripley) · https://rdrr.io/cran/spatstat.data/man/redwood.html | REFERENCIA externa cotejada |
| `1977` | notas | …las secuoyas (Strauss, 1975; Ripley, 1977), 62 puntos en el cuadrado u… | Ripley (1977): subconjunto de `redwood` reescalado al cuadrado unidad · https://rdrr.io/cran/spatstat.data/man/redwood.html | REFERENCIA externa cotejada |
| `62` | notas | …cuoyas (Strauss, 1975; Ripley, 1977), 62 puntos en el cuadrado unidad.… | datos › m3.redwood.n = 62; recómputo independiente «n:redwood» = 62 | VERIFICADA · recómputo independiente |

### Diapositiva 22 · Sobre las secuoyas el test rechaza con 5×5 y no con 2×2: ¿qué se hace con eso?

| Cifra | Dónde | Contexto | Comprobación | Estado |
|---|---|---|---|---|
| `5x5` | titulo | …obre las secuoyas el test rechaza con 5×5 y no con 2×2: ¿qué se hace c… | rejilla 5×5 del módulo 5 = [5] | PARÁMETRO de diseño |
| `2x2` | titulo | …oyas el test rechaza con 5×5 y no con 2×2: ¿qué se hace con eso?… | rejillas barridas en el módulo 6 = [2, 3, 4, 5, 6, 8, 10, 12, 15, 20] | PARÁMETRO de diseño |
| `2x2` | notas | …porque respeta el supuesto, pero con 2×2 no se rechaza un patrón clara… | rejillas barridas en el módulo 6 = [2, 3, 4, 5, 6, 8, 10, 12, 15, 20] | PARÁMETRO de diseño |

### Diapositiva 26 · En los patrones de libro las medianas de G y F se separan de la de CSR como dice la teoría

| Cifra | Dónde | Contexto | Comprobación | Estado |
|---|---|---|---|---|
| `0.13036` | cuerpo | …--\|---\|---\|---\| \| Células (regular) \| 0.13036 \| 0.05959 \| 0.07… | datos › m7.cells.g_mediana = 0.130361 | CONTRASTADA · salida de R (JSON) |
| `0.05959` | cuerpo | …\|---\| \| Células (regular) \| 0.13036 \| 0.05959 \| 0.07248 \| \| Pi… | datos › m7.cells.f_mediana = 0.0595948 | CONTRASTADA · salida de R (JSON) |
| `0.07248` | cuerpo | …lulas (regular) \| 0.13036 \| 0.05959 \| 0.07248 \| \| Pinos japoneses… | datos › m7.cells.csr_mediana = 0.0724792; recómputo independiente «csrmed:cells» = 0.07247915959 | VERIFICADA · recómputo independiente |
| `0.06403` | cuerpo | …248 \| \| Pinos japoneses (aleatorio) \| 0.06403 \| 0.05964 \| 0.05826… | datos › m7.japanesepines.g_mediana = 0.0640312 | CONTRASTADA · salida de R (JSON) |
| `0.05964` | cuerpo | …nos japoneses (aleatorio) \| 0.06403 \| 0.05964 \| 0.05826 \| \| Secuo… | datos › m7.japanesepines.f_mediana = 0.0596449 | CONTRASTADA · salida de R (JSON) |
| `0.05826` | cuerpo | …ses (aleatorio) \| 0.06403 \| 0.05964 \| 0.05826 \| \| Secuoyas (agreg… | datos › m7.japanesepines.csr_mediana = 0.0582614; recómputo independiente «csrmed:japanesepines» = 0.05826142676 | VERIFICADA · recómputo independiente |
| `0.02828` | cuerpo | …4 \| 0.05826 \| \| Secuoyas (agregado) \| 0.02828 \| 0.07769 \| 0.0596… | datos › m7.redwood.g_mediana = 0.0282843 | CONTRASTADA · salida de R (JSON) |
| `0.07769` | cuerpo | …6 \| \| Secuoyas (agregado) \| 0.02828 \| 0.07769 \| 0.05965 \| ::: ::… | datos › m7.redwood.f_mediana = 0.077688 | CONTRASTADA · salida de R (JSON) |
| `0.05965` | cuerpo | …oyas (agregado) \| 0.02828 \| 0.07769 \| 0.05965 \| ::: ::: tip Interp… | datos › m7.redwood.csr_mediana = 0.0596543; recómputo independiente «csrmed:redwood» = 0.05965432685 | VERIFICADA · recómputo independiente |

### Diapositiva 27 · En Bogotá G y F dicen «agregado», pero no dicen por qué

| Cifra | Dónde | Contexto | Comprobación | Estado |
|---|---|---|---|---|
| `145.52` | cuerpo | …ogotá, ventana urbana Mediana de G: **145.52** m. Mediana de F: **222.… | datos › m7.bogota.g_mediana = 145.523 | CONTRASTADA · salida de R (JSON) |
| `222.83` | cuerpo | …a de G: **145.52** m. Mediana de F: **222.83** m. Bajo CSR las dos ser… | datos › m7.bogota.f_mediana = 222.833 | CONTRASTADA · salida de R (JSON) |
| `196.86` | cuerpo | …222.83** m. Bajo CSR las dos serían **196.86** m. F usa 160 000 sitios… | datos › m7.bogota.csr_mediana = 196.861; recómputo independiente «csrmed:bogota» = 196.8609488 | VERIFICADA · recómputo independiente |
| `160000` | cuerpo | …R las dos serían **196.86** m. F usa 160 000 sitios y solo **62 762** … | datos › m7.bogota.f_rejilla = 160000 | CONTRASTADA · salida de R (JSON) |
| `62762` | cuerpo | …6** m. F usa 160 000 sitios y solo **62 762** caen dentro de la ventan… | datos › m7.bogota.f_sitios = 62762 | CONTRASTADA · salida de R (JSON) |

### Diapositiva 28 · La G sin corregir vale 0.037494 en r = 0: ¿cuántas sedes comparten coordenada con otra?

| Cifra | Dónde | Contexto | Comprobación | Estado |
|---|---|---|---|---|
| `0.037494` | titulo | …La G sin corregir vale 0.037494 en r = 0: ¿cuántas sedes comp… | datos › m7.bogota.g_emp_en_cero = 0.0374941; recómputo independiente «g0:bogota» = 0.03749406739 | VERIFICADA · recómputo independiente |
| `2107` | cuerpo | …Sedes de Bogotá, ventana urbana (2 107 sedes). En los tres patrones… | datos › m1.urbana.n = 2107; recómputo independiente «n_bog» = 2107 | VERIFICADA · recómputo independiente |
| `79` | cuerpo | …e 0 en r = 0; aquí no. ::: respuesta 79 sedes Es el **3.74941 %** de… | datos › m7.bogota.coincidentes = 79; recómputo independiente «dup:sedes» = 79 | VERIFICADA · recómputo independiente |
| `3.74941` | cuerpo | …í no. ::: respuesta 79 sedes Es el **3.74941 %** de las sedes, y hay s… | datos › m7.bogota.coincidentes_pct = 3.749406739; recómputo independiente «dup:pct» = 3.749406739 | VERIFICADA · recómputo independiente |
| `3` | cuerpo | …e las sedes, y hay sitios con hasta **3** sedes. Son sedes distintas… | datos › m7.duplicados.maximo_por_sitio = 3; recómputo independiente «dup:max» = 3 | VERIFICADA · recómputo independiente |
| `0.037494` | notas | …n un vecino a distancia cero, así que 0.037494 por 2 107 da 79. Ojo, d… | datos › m7.bogota.g_emp_en_cero = 0.0374941; recómputo independiente «g0:bogota» = 0.03749406739 | VERIFICADA · recómputo independiente |
| `2107` | notas | …distancia cero, así que 0.037494 por 2 107 da 79. Ojo, discrepancia en… | datos › m1.urbana.n = 2107; recómputo independiente «n_bog» = 2107 | VERIFICADA · recómputo independiente |
| `79` | notas | …a cero, así que 0.037494 por 2 107 da 79. Ojo, discrepancia en el mate… | datos › m7.bogota.coincidentes = 79; recómputo independiente «dup:sedes» = 79 | VERIFICADA · recómputo independiente |
| `79` | notas | …cia en el material: el dice que las 79 sedes están «repartidas en 40… | datos › m7.bogota.coincidentes = 79; recómputo independiente «dup:sedes» = 79 | VERIFICADA · recómputo independiente |
| `40` | notas | …que las 79 sedes están «repartidas en 40 sitios». Recomputado con las… | datos › m7.duplicados.repetidos = 40 \| recómputo independiente «dup:sobrantes» = 40 | VERIFICADA · recómputo independiente |
| `39` | notas | …con las coordenadas crudas de , son 39 sitios: 38 con dos sedes y 1… | recómputo independiente «dup:sitios» = 39 | VERIFICADA · recómputo independiente |
| `38` | notas | …ordenadas crudas de , son 39 sitios: 38 con dos sedes y 1 con tres. E… | recómputo independiente «dup:sitios2» = 38 | VERIFICADA · recómputo independiente |
| `40` | notas | …os: 38 con dos sedes y 1 con tres. El 40 es 2 107 − 2 067, el número d… | datos › m7.duplicados.repetidos = 40 \| recómputo independiente «dup:sobrantes» = 40 | VERIFICADA · recómputo independiente |
| `2107` | notas | …con dos sedes y 1 con tres. El 40 es 2 107 − 2 067, el número de sedes… | datos › m1.urbana.n = 2107; recómputo independiente «n_bog» = 2107 | VERIFICADA · recómputo independiente |
| `2067` | notas | …sedes y 1 con tres. El 40 es 2 107 − 2 067, el número de sedes «sobran… | datos › m7.duplicados.distintos = 2067 \| recómputo independiente «dup:distintos» = 2067 | VERIFICADA · recómputo independiente |

### Diapositiva 29 · J junta G y F en una curva con referencia plana, pero J = 1 no certifica CSR

| Cifra | Dónde | Contexto | Comprobación | Estado |
|---|---|---|---|---|
| `0.29192` | cuerpo | …nos japoneses (aleatorios): J va de **0.29192** a **1.50037**. Bogotá:… | datos › m7.japanesepines.j_min = 0.291919 | CONTRASTADA · salida de R (JSON) |
| `1.50037` | cuerpo | …(aleatorios): J va de **0.29192** a **1.50037**. Bogotá: J queda por d… | datos › m7.japanesepines.j_max = 1.50037 | CONTRASTADA · salida de R (JSON) |
| `67` | cuerpo | …otá: J queda por debajo de 1 en las **67** distancias. ::: ::: tip In… | datos › m7.bogota.j_bajo_1 = 67 | CONTRASTADA · salida de R (JSON) |
| `1997` | cuerpo | …o prueba CSR: Bedford y van den Berg (1997) construyeron, sobre la rec… | Bedford y van den Berg (1997), Advances in Applied Probability 29, 19–25: procesos con J ≡ 1 · https://www.cambridge.org/core/journals/advances-in-applied-probability/article/abs/remark-on-the-van-lieshout-and-baddeley-jfunction-f | REFERENCIA externa cotejada |
| `1996` | cuerpo | …e: · . J: van Lieshout y Baddeley (1996).… | van Lieshout y Baddeley (1996), Statistica Neerlandica 50(3), 344–361: la función J · https://arxiv.org/pdf/1008.4504 | REFERENCIA externa cotejada |
| `1996` | notas | …liográficas: van Lieshout y Baddeley (1996), Statistica Neerlandica 50… | van Lieshout y Baddeley (1996), Statistica Neerlandica 50(3), 344–361: la función J · https://arxiv.org/pdf/1008.4504 | REFERENCIA externa cotejada |
| `50` | notas | …ddeley (1996), Statistica Neerlandica 50(3), 344–361; Bedford y van de… | volumen, número y páginas de las dos referencias de la diapositiva de J (cotejados por búsqueda web) · https://arxiv.org/pdf/1008.4504 | REFERENCIA externa cotejada |
| `3` | notas | …ley (1996), Statistica Neerlandica 50(3), 344–361; Bedford y van den… | volumen, número y páginas de las dos referencias de la diapositiva de J (cotejados por búsqueda web) · https://arxiv.org/pdf/1008.4504 | REFERENCIA externa cotejada |
| `344` | notas | …(1996), Statistica Neerlandica 50(3), 344–361; Bedford y van den Berg … | volumen, número y páginas de las dos referencias de la diapositiva de J (cotejados por búsqueda web) · https://arxiv.org/pdf/1008.4504 | REFERENCIA externa cotejada |
| `361` | notas | …6), Statistica Neerlandica 50(3), 344–361; Bedford y van den Berg (199… | volumen, número y páginas de las dos referencias de la diapositiva de J (cotejados por búsqueda web) · https://arxiv.org/pdf/1008.4504 | REFERENCIA externa cotejada |
| `1997` | notas | …(3), 344–361; Bedford y van den Berg (1997), Advances in Applied Proba… | Bedford y van den Berg (1997), Advances in Applied Probability 29, 19–25: procesos con J ≡ 1 · https://www.cambridge.org/core/journals/advances-in-applied-probability/article/abs/remark-on-the-van-lieshout-and-baddeley-jfunction-f | REFERENCIA externa cotejada |
| `29` | notas | …997), Advances in Applied Probability 29, 19–25. J es un cociente, y c… | volumen, número y páginas de las dos referencias de la diapositiva de J (cotejados por búsqueda web) · https://arxiv.org/pdf/1008.4504 | REFERENCIA externa cotejada |
| `19` | notas | …, Advances in Applied Probability 29, 19–25. J es un cociente, y cuand… | volumen, número y páginas de las dos referencias de la diapositiva de J (cotejados por búsqueda web) · https://arxiv.org/pdf/1008.4504 | REFERENCIA externa cotejada |
| `25` | notas | …dvances in Applied Probability 29, 19–25. J es un cociente, y cuando F… | volumen, número y páginas de las dos referencias de la diapositiva de J (cotejados por búsqueda web) · https://arxiv.org/pdf/1008.4504 | REFERENCIA externa cotejada |
| `0.9` | notas | …se dibuja solo mientras F no pase de 0.9. En Bogotá J arranca en 0.962… | datos › m7.j_umbral_f = 0.9 | CONTRASTADA · salida de R (JSON) |
| `0.962506` | notas | …o pase de 0.9. En Bogotá J arranca en 0.962506, que es 1 menos la frac… | datos › m7.bogota.j_en_cero = 0.962506; recómputo independiente «j0:bogota» = 0.9625059326 | VERIFICADA · recómputo independiente |

### Diapositiva 31 · K cuenta vecinos en discos crecientes; bajo CSR vale πr², sea cual sea λ

| Cifra | Dónde | Contexto | Comprobación | Estado |
|---|---|---|---|---|
| `42` | cuerpo | …a no depende de la densidad: células (42 puntos), pinos japoneses (65)… | datos › m3.cells.n = 42; recómputo independiente «n:cells» = 42 | VERIFICADA · recómputo independiente |
| `65` | cuerpo | …células (42 puntos), pinos japoneses (65) y secuoyas (62) comparten la… | datos › m3.japanesepines.n = 65; recómputo independiente «n:japanesepines» = 65 | VERIFICADA · recómputo independiente |
| `62` | cuerpo | …os), pinos japoneses (65) y secuoyas (62) comparten la misma curva teó… | datos › m3.redwood.n = 62; recómputo independiente «n:redwood» = 62 | VERIFICADA · recómputo independiente |

### Diapositiva 32 · A 1 km la sede típica tiene 25.87 vecinas y el azar le daría 17.88

| Cifra | Dónde | Contexto | Comprobación | Estado |
|---|---|---|---|---|
| `25.87` | titulo | …A 1 km la sede típica tiene 25.87 vecinas y el azar le daría 17… | datos › m8.piezas.vecinas = 25.8713 \| suma de pesos / n = 25.87133365 | VERIFICADA · aritmética sobre el JSON |
| `17.88` | titulo | …iene 25.87 vecinas y el azar le daría 17.88… | datos › m8.piezas.vecinas_csr = 17.8773 \| (n − 1)/\|W\| · π · (1 km)² = 17.87725723 | VERIFICADA · aritmética sobre el JSON |
| `1.45` | cuerpo | …etación A 1 km la sede típica tiene **1.45** veces las vecinas que dar… | datos › m8.piezas.cociente = 1.44716 \| K̂ / πr² = 1.447165289 | VERIFICADA · aritmética sobre el JSON |
| `50368` | cuerpo | …-\|---\| \| Parejas ordenadas a ≤ 1 km \| 50 368 \| \| Suma con sus pe… | datos › m8.piezas.parejas_r = 50368; recómputo independiente «pares1km» = 50368 | VERIFICADA · recómputo independiente |
| `54511` | cuerpo | …km \| 50 368 \| \| Suma con sus pesos \| 54 511 \| \| Vecinas por sede… | datos › m8.piezas.suma_pesos = 54510.9 | CONTRASTADA · salida de R (JSON) |
| `25.87` | cuerpo | …pesos \| 54 511 \| \| Vecinas por sede \| 25.87 \| \| Vecinas bajo CSR… | datos › m8.piezas.vecinas = 25.8713 \| suma de pesos / n = 25.87133365 | VERIFICADA · aritmética sobre el JSON |
| `17.88` | cuerpo | …r sede \| 25.87 \| \| Vecinas bajo CSR \| 17.88 \| \| K̂(1 km) \| 4.54… | datos › m8.piezas.vecinas_csr = 17.8773 \| (n − 1)/\|W\| · π · (1 km)² = 17.87725723 | VERIFICADA · aritmética sobre el JSON |
| `4.5464` | cuerpo | …cinas bajo CSR \| 17.88 \| \| K̂(1 km) \| 4.5464 km² \| \| πr² \| 3.14… | datos › m8.piezas.k_km2 = 4.5464 \| \|W\|/(n(n−1)) · suma de pesos = 4.546401648 | VERIFICADA · aritmética sobre el JSON |
| `3.1416` | cuerpo | …8 \| \| K̂(1 km) \| 4.5464 km² \| \| πr² \| 3.1416 km² \| ::: Fuente: … | datos › m8.piezas.pir2_km2 = 3.14159 \| π · (1 km)² = 3.141592654 | VERIFICADA · aritmética sobre el JSON |
| `23.91` | notas | …las vecinas que el borde le escondía: 23.91 sin pesos, 25.87 con ellos… | datos › m8.piezas.vecinas_crudas = 23.9051 \| parejas a ≤ 1 km / n = 23.9051; recómputo independiente «crudas1km» = 23.90507831 | VERIFICADA · recómputo independiente |
| `25.87` | notas | …l borde le escondía: 23.91 sin pesos, 25.87 con ellos.… | datos › m8.piezas.vecinas = 25.8713 \| suma de pesos / n = 25.87133365 | VERIFICADA · aritmética sobre el JSON |

### Diapositiva 33 · L − r pone CSR en el eje: su signo dice hacia dónde se aparta, no si importa

| Cifra | Dónde | Contexto | Comprobación | Estado |
|---|---|---|---|---|
| `-0.08463` | cuerpo | …vío \| \|---\|---\| \| Células (regular) \| −0.08463 \| \| Pinos japon… | datos › m8.cells.desvio_con_signo = -0.0846278; recómputo independiente «Lr:cells» = -0.08462772744 | VERIFICADA · recómputo independiente |
| `-0.01473` | cuerpo | …463 \| \| Pinos japoneses (aleatorio) \| −0.01473 \| \| Secuoyas (agre… | datos › m8.japanesepines.desvio_con_signo = -0.0147323; recómputo independiente «Lr:japanesepines» = -0.014846 (\|Δ\| ≤ 0.0002 respecto de -0.014732) | VERIFICADA · recómputo independiente |
| `0.05581` | cuerpo | …\| −0.01473 \| \| Secuoyas (agregado) \| +0.05581 \| \| Sedes de Bogot… | datos › m8.redwood.desvio_con_signo = 0.0558102; recómputo independiente «Lr:redwood» = 0.05581022356 | VERIFICADA · recómputo independiente |
| `331.67` | cuerpo | …ado) \| +0.05581 \| \| Sedes de Bogotá \| +331.67 m, a 5105 m \| ::: :… | datos › m8.bogota.max_desvio = 331.674 | CONTRASTADA · salida de R (JSON) |
| `5105` | cuerpo | …81 \| \| Sedes de Bogotá \| +331.67 m, a 5105 m \| ::: ::: tip Interpr… | datos › m8.bogota.r_max_desvio = 5105.26 | CONTRASTADA · salida de R (JSON) |
| `0.30000` | cuerpo | …Sobre los pinos el test global da p = 0.30000: nada que rechazar. ::: … | datos › m11.test_global.dclf_japanesepines_p = 0.3 | CONTRASTADA · salida de R (JSON) |
| `331.67` | notas | …horizontal no. En Bogotá el máximo es 331.67 m; que esté por encima de… | datos › m8.bogota.max_desvio = 331.674 | CONTRASTADA · salida de R (JSON) |

### Diapositiva 34 · K sigue por encima a 500 m aunque la agregación ocurre a 20 m: ¿por qué?

| Cifra | Dónde | Contexto | Comprobación | Estado |
|---|---|---|---|---|
| `500` | titulo | …K sigue por encima a 500 m aunque la agregación ocurre… | distancias hipotéticas del enunciado del cuestionario | CONTRASTADA · texto del capítulo |
| `20` | titulo | …a 500 m aunque la agregación ocurre a 20 m: ¿por qué?… | distancias hipotéticas del enunciado del cuestionario | CONTRASTADA · texto del capítulo |
| `20` | cuerpo | …ta : K es acumulativa Los vecinos de 20 m siguen contados dentro del… | distancias hipotéticas del enunciado del cuestionario | CONTRASTADA · texto del capítulo |
| `500` | cuerpo | …m siguen contados dentro del disco de 500 m. Lo arregla g(r), que mira… | distancias hipotéticas del enunciado del cuestionario | CONTRASTADA · texto del capítulo |
| `20` | cuerpo | …::: Fuente: , . Las distancias de 20 m y 500 m son las del enuncia… | distancias hipotéticas del enunciado del cuestionario | CONTRASTADA · texto del capítulo |
| `500` | cuerpo | …uente: , . Las distancias de 20 m y 500 m son las del enunciado de la… | distancias hipotéticas del enunciado del cuestionario | CONTRASTADA · texto del capítulo |

### Diapositiva 35 · g mira solo el anillo: vuelve a 1 en r = 0.1450 mientras K sigue por encima

| Cifra | Dónde | Contexto | Comprobación | Estado |
|---|---|---|---|---|
| `0.1450` | titulo | …ira solo el anillo: vuelve a 1 en r = 0.1450 mientras K sigue por enci… | datos › m9.redwood.r_vuelve_a_1 = 0.145 | CONTRASTADA · salida de R (JSON) |
| `3.27862` | cuerpo | …::: info Dato Secuoyas: g alcanza **3.27862** en r = **0.02250** y vue… | datos › m9.redwood.g_max = 3.27862 | CONTRASTADA · salida de R (JSON) |
| `0.02250` | cuerpo | …uoyas: g alcanza **3.27862** en r = **0.02250** y vuelve a 1 en r = **… | datos › m9.redwood.r_g_max = 0.0225 | CONTRASTADA · salida de R (JSON) |
| `0.1450` | cuerpo | …r = **0.02250** y vuelve a 1 en r = **0.1450**; K sigue por encima de … | datos › m9.redwood.r_vuelve_a_1 = 0.145 | CONTRASTADA · salida de R (JSON) |
| `1.60833` | notas | …as). En Bogotá, g no tiene pico: vale 1.60833 en el primer nodo, 59 m,… | datos › m9.bogota.g_max = 1.60833 | CONTRASTADA · salida de R (JSON) |
| `59` | notas | …pico: vale 1.60833 en el primer nodo, 59 m, y en el último, 5868 m, to… | datos › m9.bogota.r_g_max = 58.6812 | CONTRASTADA · salida de R (JSON) |
| `5868` | notas | …el primer nodo, 59 m, y en el último, 5868 m, todavía vale 1.01105; no… | datos › m10.r_sesgo_max = 5868.12 \| un cuarto del lado corto de la ventana = 5868.125 | VERIFICADA · aritmética sobre el JSON |
| `1.01105` | notas | …y en el último, 5868 m, todavía vale 1.01105; no regresa a 1 en ningún… | último nodo de m9.bogota.g_obs (r = 5868 m) = 1.01105 | VERIFICADA · aritmética sobre el JSON |

### Diapositiva 36 · K mira todas las escalas, pero acumula, supone λ constante y no mira lejos

| Cifra | Dónde | Contexto | Comprobación | Estado |
|---|---|---|---|---|
| `2495` | cuerpo | …: ninguna sede tiene el suyo a más de 2495 m; K sigue hasta 5868 m. - … | datos › m3.bogota.nn_max = 2494.980499 \| recómputo independiente «nnmax:bogota» = 2494.980499 | VERIFICADA · recómputo independiente |
| `5868` | cuerpo | …l suyo a más de 2495 m; K sigue hasta 5868 m. - Una curva para todas l… | datos › m10.r_sesgo_max = 5868.12 \| un cuarto del lado corto de la ventana = 5868.125 | VERIFICADA · aritmética sobre el JSON |
| `5868` | cuerpo | …cuarto del lado corto de la ventana (5868 m en Bogotá). - No identific… | datos › m10.r_sesgo_max = 5868.12 \| un cuarto del lado corto de la ventana = 5868.125 | VERIFICADA · aritmética sobre el JSON |
| `1984` | cuerpo | …ica el proceso: Baddeley y Silverman (1984) construyeron uno que no es… | Baddeley y Silverman (1984), Biometrics 40, 1089–1094: el «cell process» con K = πr² · https://www.rdocumentation.org/packages/spatstat/versions/1.64-1/topics/rcell | REFERENCIA externa cotejada |
| `1984` | notas | …ima desventaja: Baddeley y Silverman (1984), Biometrics 40, 1089–1094;… | Baddeley y Silverman (1984), Biometrics 40, 1089–1094: el «cell process» con K = πr² · https://www.rdocumentation.org/packages/spatstat/versions/1.64-1/topics/rcell | REFERENCIA externa cotejada |
| `40` | notas | …ddeley y Silverman (1984), Biometrics 40, 1089–1094; construyeron un «… | volumen y páginas de Baddeley y Silverman (1984), cotejados por búsqueda web · https://www.rdocumentation.org/packages/spatstat/versions/1.64-1/topics/rcell | REFERENCIA externa cotejada |
| `1089` | notas | …ey y Silverman (1984), Biometrics 40, 1089–1094; construyeron un «cell… | volumen y páginas de Baddeley y Silverman (1984), cotejados por búsqueda web · https://www.rdocumentation.org/packages/spatstat/versions/1.64-1/topics/rcell | REFERENCIA externa cotejada |
| `1094` | notas | …Silverman (1984), Biometrics 40, 1089–1094; construyeron un «cell proc… | volumen y páginas de Baddeley y Silverman (1984), cotejados por búsqueda web · https://www.rdocumentation.org/packages/spatstat/versions/1.64-1/topics/rcell | REFERENCIA externa cotejada |

### Diapositiva 37 · Cinco resúmenes miran el vecino o las cajas, y en Bogotá los cinco caen del lado agregado

| Cifra | Dónde | Contexto | Comprobación | Estado |
|---|---|---|---|---|
| `0.82371` | cuerpo | …ia al vecino, sobre la del azar \| R = 0.82371 \| \| χ² de cuadrantes … | datos › m3.bogota.clark_evans = 0.8237083333; recómputo independiente «ce:bogota» = 0.8237083333 | VERIFICADA · recómputo independiente |
| `10` | cuerpo | …rente a los del azar \| rechaza en las 10 rejillas \| \| G(r) \| Punto… | soluciones › e3.solucion.rechazos_urbana = 10 | CONTRASTADA · salida de R (JSON) |
| `145.52` | cuerpo | …ntos con vecino a r o menos \| mediana 145.52 m (CSR: 196.86 m) \| \| … | datos › m7.bogota.g_mediana = 145.523 | CONTRASTADA · salida de R (JSON) |
| `196.86` | cuerpo | …a r o menos \| mediana 145.52 m (CSR: 196.86 m) \| \| F(r) \| Sitios c… | datos › m7.bogota.csr_mediana = 196.861; recómputo independiente «csrmed:bogota» = 196.8609488 | VERIFICADA · recómputo independiente |
| `222.83` | cuerpo | …nto a r o menos: los huecos \| mediana 222.83 m \| \| J(r) \| (1 − G) … | datos › m7.bogota.f_mediana = 222.833 | CONTRASTADA · salida de R (JSON) |
| `67` | cuerpo | …1 − G) / (1 − F) \| por debajo de 1 en 67 distancias \| ::: ::: tip In… | datos › m7.bogota.j_bajo_1 = 67 | CONTRASTADA · salida de R (JSON) |

### Diapositiva 38 · K, L − r y g también dicen «agregado»; ninguno dice por qué

| Cifra | Dónde | Contexto | Comprobación | Estado |
|---|---|---|---|---|
| `1.45` | cuerpo | …inos a r o menos, entre λ: el disco \| 1.45 veces CSR a 1 km \| \| L(r… | datos › m8.piezas.cociente = 1.44716 \| K̂ / πr² = 1.447165289 | VERIFICADA · aritmética sobre el JSON |
| `331.67` | cuerpo | …\| \| L(r) − r \| K en la escala de r \| +331.67 m, a 5105 m \| \| g(r… | datos › m8.bogota.max_desvio = 331.674 | CONTRASTADA · salida de R (JSON) |
| `5105` | cuerpo | …\| K en la escala de r \| +331.67 m, a 5105 m \| \| g(r) \| Parejas po… | datos › m8.bogota.r_max_desvio = 5105.26 | CONTRASTADA · salida de R (JSON) |
| `1.01105` | cuerpo | …105 m \| \| g(r) \| Parejas por anillo \| 1.01105 a 5868 m: no regresa… | último nodo de m9.bogota.g_obs (r = 5868 m) = 1.01105 | VERIFICADA · aritmética sobre el JSON |
| `5868` | cuerpo | …g(r) \| Parejas por anillo \| 1.01105 a 5868 m: no regresa a 1 \| ::: … | datos › m10.r_sesgo_max = 5868.12 \| un cuarto del lado corto de la ventana = 5868.125 | VERIFICADA · aritmética sobre el JSON |
| `1.01105` | notas | …tonces, «exceso de parejas». En g, el 1.01105 del último nodo (5868 m)… | último nodo de m9.bogota.g_obs (r = 5868 m) = 1.01105 | VERIFICADA · aritmética sobre el JSON |
| `5868` | notas | …s». En g, el 1.01105 del último nodo (5868 m) no es un cruce: g no reg… | datos › m10.r_sesgo_max = 5868.12 \| un cuarto del lado corto de la ventana = 5868.125 | VERIFICADA · aritmética sobre el JSON |
| `1.60833` | notas | …ingún punto del barrido, y su máximo, 1.60833 a 59 m, cae en el borde … | datos › m9.bogota.g_max = 1.60833 | CONTRASTADA · salida de R (JSON) |
| `59` | notas | …o del barrido, y su máximo, 1.60833 a 59 m, cae en el borde izquierdo,… | datos › m9.bogota.r_g_max = 58.6812 | CONTRASTADA · salida de R (JSON) |

### Diapositiva 40 · Ignorar el borde añade dirección: siempre hacia «más regular»

| Cifra | Dónde | Contexto | Comprobación | Estado |
|---|---|---|---|---|
| `29.6` | cuerpo | …to La K sin corregir queda hasta un **29.6 %** por debajo de la correg… | datos › m10.sesgo_max_pct = 29.6053 \| soluciones › e5.solucion.sesgo_max_pct = 29.6050985 | CONTRASTADA · salida de R (JSON) |
| `5868` | cuerpo | …de la corregida; el máximo, en r = **5868** m. La isotrópica cuesta **… | datos › m10.r_sesgo_max = 5868.12 \| un cuarto del lado corto de la ventana = 5868.125 | VERIFICADA · aritmética sobre el JSON |
| `555` | cuerpo | …= **5868** m. La isotrópica cuesta **555** veces más que la de traslac… | datos › m10.coste.veces_isotropica_sobre_traslacion = 555 | [SIN VERIFICAR] |
| `4.4.1` | notas | …el capítulo los declara medidos en R 4.4.1 sobre un Mac de 12 núcleos … | datos › m10.coste.medido_en = R 4.4.1, aarch64-apple-darwin20 | CONTRASTADA · salida de R (JSON) |
| `22` | notas | …eso w_ij. Sobre la ventana de Bogotá (22 piezas, 5 agujeros, 13 767 vé… | datos › m10.ventana.piezas = 22 | CONTRASTADA · salida de R (JSON) |
| `5` | notas | …obre la ventana de Bogotá (22 piezas, 5 agujeros, 13 767 vértices) la… | datos › m10.ventana.agujeros = 5 | CONTRASTADA · salida de R (JSON) |
| `13767` | notas | …ana de Bogotá (22 piezas, 5 agujeros, 13 767 vértices) la isotrópica t… | datos › m10.ventana.vertices = 13767 | CONTRASTADA · salida de R (JSON) |
| `13767` | notas | …eja, un círculo contra un contorno de 13 767 vértices: lo que se paga … | datos › m10.ventana.vertices = 13767 | CONTRASTADA · salida de R (JSON) |
| `0.22` | notas | …paga es el borde, no n. Los tiempos (0.22 s la de traslación y 122.66 … | tiempo de una estimación de K con corrección de traslación: medido por el autor, depende de la máquina = 0.221 | [SIN VERIFICAR] |
| `122.66` | notas | …os tiempos (0.22 s la de traslación y 122.66 s la isotrópica por estim… | tiempo de una estimación de K con corrección isotrópica: medido por el autor, depende de la máquina = 122.655 | [SIN VERIFICAR] |
| `12` | notas | …eclara medidos en R sobre un Mac de 12 núcleos y aquí no se pudieron… | datos › m10.coste.nucleos = 12 | CONTRASTADA · salida de R (JSON) |
| `29.60530` | notas | …a marca. El material da el sesgo como 29.60530 % en el ( ) y como 29.6… | datos › m10.sesgo_max_pct = 29.6053 | CONTRASTADA · salida de R (JSON) |
| `29.60510` | notas | …go como 29.60530 % en el ( ) y como 29.60510 % en la solución del ( ):… | soluciones › e5.solucion.sesgo_max_pct = 29.6050985 | CONTRASTADA · salida de R (JSON) |
| `29.6` | notas | …en que se mide, y las dos redondean a 29.6, que es lo que va en la dia… | datos › m10.sesgo_max_pct = 29.6053 \| soluciones › e5.solucion.sesgo_max_pct = 29.6050985 | CONTRASTADA · salida de R (JSON) |

### Diapositiva 41 · Una banda al 95 % por punto no contrasta la curva: la mitad del azar puro se sale

| Cifra | Dónde | Contexto | Comprobación | Estado |
|---|---|---|---|---|
| `95` | titulo | …Una banda al 95 % por punto no contrasta la c… | nivel puntual de la banda = 0.95 = 95 | VERIFICADA · aritmética sobre el JSON |
| `999` | cuerpo | …inos japoneses (aleatorios): banda de 999 simulaciones de CSR y K obse… | datos › m11.nsim = 999 | CONTRASTADA · salida de R (JSON) |
| `999` | cuerpo | …e CSR y K observada ::: info Dato De 999 simulaciones de CSR puro, se… | datos › m11.nsim = 999 | CONTRASTADA · salida de R (JSON) |
| `52.2523` | cuerpo | …o, se salen de su banda en algún r: **52.2523 %** en las sedes, **52.1… | datos › m11.tasa_salida_bogota.pct = 52.2523 \| fuera / nsim · 100 = 52.25225… = 52.25225225 | VERIFICADA · aritmética sobre el JSON |
| `52.1522` | cuerpo | …lgún r: **52.2523 %** en las sedes, **52.1522 %** en las secuoyas y **… | datos › m11.tasa_salida_redwood.pct = 52.1522 \| fuera / nsim · 100 = 52.15215… = 52.15215215 | VERIFICADA · aritmética sobre el JSON |
| `51.0511` | cuerpo | …es, **52.1522 %** en las secuoyas y **51.0511 %** en los pinos. En los… | datos › m11.japanesepines.tasa_salida.pct = 51.0511 \| fuera / nsim · 100 = 51.05105… = 51.05105105 | VERIFICADA · aritmética sobre el JSON |
| `513` | cuerpo | …ión La tasa la pone el procedimiento —513 distancias con una banda al … | datos › m11.tasa_salida_bogota.nodos_r = 513 | CONTRASTADA · salida de R (JSON) |
| `95` | cuerpo | …ento —513 distancias con una banda al 95 % en cada una—, no el dato. :… | nivel puntual de la banda = 0.95 = 95 | VERIFICADA · aritmética sobre el JSON |
| `52.25230` | notas | …ribe estas tasas con cinco decimales (52.25230, 52.15220 y 51.05110), … | cifra tal como la escribe el capítulo (cinco decimales); el JSON guarda cuatro: 52.2523 | CONTRASTADA · texto del capítulo |
| `52.15220` | notas | …tasas con cinco decimales (52.25230, 52.15220 y 51.05110), pero el JSO… | cifra tal como la escribe el capítulo (cinco decimales); el JSON guarda cuatro: 52.1522 | CONTRASTADA · texto del capítulo |
| `51.05110` | notas | …cinco decimales (52.25230, 52.15220 y 51.05110), pero el JSON solo gua… | cifra tal como la escribe el capítulo (cinco decimales); el JSON guarda cuatro: 51.0511 | CONTRASTADA · texto del capítulo |
| `522` | notas | …ro y el valor exacto de la primera es 522/999 = 52.25225…: el cero fin… | datos › m11.tasa_salida_bogota.fuera = 522 | CONTRASTADA · salida de R (JSON) |
| `999` | notas | …el valor exacto de la primera es 522/999 = 52.25225…: el cero final es… | datos › m11.nsim = 999 | CONTRASTADA · salida de R (JSON) |
| `52.25225` | notas | …lor exacto de la primera es 522/999 = 52.25225…: el cero final es rell… | 522 / 999 · 100 = 52.25225225 | VERIFICADA · aritmética sobre el JSON |
| `62` | notas | …les. Tres patrones sin nada en común —62 plántulas y 65 pinos en un cu… | datos › m3.redwood.n = 62; recómputo independiente «n:redwood» = 62 | VERIFICADA · recómputo independiente |
| `65` | notas | …nes sin nada en común —62 plántulas y 65 pinos en un cuadrado, 2 107 s… | datos › m3.japanesepines.n = 65; recómputo independiente «n:japanesepines» = 65 | VERIFICADA · recómputo independiente |
| `2107` | notas | …plántulas y 65 pinos en un cuadrado, 2 107 sedes en una ventana de 22 … | datos › m1.urbana.n = 2107; recómputo independiente «n_bog» = 2107 | VERIFICADA · recómputo independiente |
| `22` | notas | …adrado, 2 107 sedes en una ventana de 22 piezas— y casi la misma tasa.… | datos › m10.ventana.piezas = 22 | CONTRASTADA · salida de R (JSON) |
| `0.05` | notas | …ir «se sale en algún sitio, luego p < 0.05» es hacer un centenar de co… | umbral convencional de significancia (p < 0.05) = 0.05 | PARÁMETRO de diseño |

### Diapositiva 42 · El test global resume la curva en un número y obliga a declarar estadístico y rango

| Cifra | Dónde | Contexto | Comprobación | Estado |
|---|---|---|---|---|
| `0.00100` | cuerpo | …::: info Dato DCLF y MAD dan p = **0.00100** sobre Bogotá y **0.30000*… | datos › m11.test_global.dclf_bogota_p = 0.001 | CONTRASTADA · salida de R (JSON) |
| `0.30000` | cuerpo | …dan p = **0.00100** sobre Bogotá y **0.30000** y **0.31800** sobre los… | datos › m11.test_global.dclf_japanesepines_p = 0.3 | CONTRASTADA · salida de R (JSON) |
| `0.31800` | cuerpo | …0100** sobre Bogotá y **0.30000** y **0.31800** sobre los pinos. Con 9… | datos › m11.test_global.mad_japanesepines_p = 0.318 | CONTRASTADA · salida de R (JSON) |
| `999` | cuerpo | …** y **0.31800** sobre los pinos. Con 999 simulaciones, el p mínimo po… | datos › m11.nsim = 999 | CONTRASTADA · salida de R (JSON) |
| `0.00100` | cuerpo | …aciones, el p mínimo posible es = **0.00100**. ::: ::: tip Interpretac… | datos › m11.p_minimo = 0.001 \| 1 / (nsim + 1) = 0.001 | VERIFICADA · aritmética sobre el JSON |
| `999` | cuerpo | …\|\|\| ::: info Dato · células, mismas 999 simulaciones \| DCLF sobre…… | datos › m11.nsim = 999 | CONTRASTADA · salida de R (JSON) |
| `0.08100` | cuerpo | …\| \|---\|---\| \| K, todo el rango de r \| 0.08100 \| \| K, r hasta e… | soluciones › e4.solucion.tramos[2].dclf_p = 0.081 | CONTRASTADA · salida de R (JSON) |
| `20` | cuerpo | …ango de r \| 0.08100 \| \| K, r hasta el 20 % \| 0.04900 \| \| K, r ha… | fracción del rango de r del primer tramo (20 %) = 20 | VERIFICADA · aritmética sobre el JSON |
| `0.04900` | cuerpo | …r \| 0.08100 \| \| K, r hasta el 20 % \| 0.04900 \| \| K, r hasta el 4… | soluciones › e4.solucion.tramos[0].dclf_p = 0.049 | CONTRASTADA · salida de R (JSON) |
| `40` | cuerpo | …a el 20 % \| 0.04900 \| \| K, r hasta el 40 % \| 0.00500 \| \| L, todo… | fracción del rango de r del segundo tramo (40 %) = 40 | VERIFICADA · aritmética sobre el JSON |
| `0.00500` | cuerpo | …% \| 0.04900 \| \| K, r hasta el 40 % \| 0.00500 \| \| L, todo el rang… | soluciones › e4.solucion.tramos[1].dclf_p = 0.005 | CONTRASTADA · salida de R (JSON) |
| `0.00100` | cuerpo | …40 % \| 0.00500 \| \| L, todo el rango \| 0.00100 \| ::: ::: warn Crit… | soluciones › e4.solucion.dclf_L = 0.001 | CONTRASTADA · salida de R (JSON) |
| `42` | notas | …s células biológicas (Crick y Ripley; 42 puntos), 999 simulaciones de… | datos › m3.cells.n = 42; recómputo independiente «n:cells» = 42 | VERIFICADA · recómputo independiente |
| `999` | notas | …ológicas (Crick y Ripley; 42 puntos), 999 simulaciones de CSR con corr… | datos › m11.nsim = 999 | CONTRASTADA · salida de R (JSON) |
| `0.08100` | notas | …ahoga. Es el del : de no rechazar (0.08100) a rechazar al máximo (0.00… | soluciones › e4.solucion.tramos[2].dclf_p = 0.081 | CONTRASTADA · salida de R (JSON) |
| `0.00100` | notas | …hazar (0.08100) a rechazar al máximo (0.00100) sin cambiar el patrón n… | soluciones › e4.solucion.dclf_L = 0.001 | CONTRASTADA · salida de R (JSON) |
| `999` | notas | …la observada quedó más lejos que las 999 simulaciones y el p ya no pod… | datos › m11.nsim = 999 | CONTRASTADA · salida de R (JSON) |

### Diapositiva 43 · De 39 a 999 simulaciones, sin tocar nada más: ¿qué le pasa a la banda por defecto?

| Cifra | Dónde | Contexto | Comprobación | Estado |
|---|---|---|---|---|
| `39` | titulo | …De 39 a 999 simulaciones, sin tocar… | valores de nsim barridos en el módulo 11 = [19, 39, 99, 999] | VERIFICADA · aritmética sobre el JSON |
| `999` | titulo | …De 39 a 999 simulaciones, sin tocar nada… | datos › m11.nsim = 999 | CONTRASTADA · salida de R (JSON) |
| `39` | cuerpo | …na. ::: respuesta : se ensancha Con 39 simulaciones el nivel puntual… | valores de nsim barridos en el módulo 11 = [19, 39, 99, 999] | VERIFICADA · aritmética sobre el JSON |
| `0.05000` | cuerpo | …39 simulaciones el nivel puntual es **0.05000**; con 999, **0.00200**:… | nivel puntual por defecto = 2 / (nsim + 1) con nsim = 39 = 0.05 | VERIFICADA · aritmética sobre el JSON |
| `999` | cuerpo | …el nivel puntual es **0.05000**; con 999, **0.00200**: son contrastes… | datos › m11.nsim = 999 | CONTRASTADA · salida de R (JSON) |
| `0.00200` | cuerpo | …el puntual es **0.05000**; con 999, **0.00200**: son contrastes distin… | nivel puntual por defecto = 2 / (nsim + 1) con nsim = 999 = 0.002 | VERIFICADA · aritmética sobre el JSON |
| `19` | cuerpo | …istintos. En el barrido entero, desde 19 simulaciones, la banda se ens… | valores de nsim barridos en el módulo 11 = [19, 39, 99, 999] | VERIFICADA · aritmética sobre el JSON |
| `1.84853` | cuerpo | …simulaciones, la banda se ensancha ×**1.84853**. Con el nivel fijo al … | datos › m11.escala_resumen.veces_defecto = 1.84853 | CONTRASTADA · salida de R (JSON) |
| `5` | cuerpo | …ha ×**1.84853**. Con el nivel fijo al 5 % sí se estrecha: ×**1.29989*… | nivel de significancia del 5 % = 5 | PARÁMETRO de diseño |
| `1.29989` | cuerpo | …nivel fijo al 5 % sí se estrecha: ×**1.29989** entre 39 y 999. ::: :::… | datos › m11.escala_resumen.veces_5pct_alcanzable = 1.29989 | CONTRASTADA · salida de R (JSON) |
| `39` | cuerpo | …% sí se estrecha: ×**1.29989** entre 39 y 999. ::: ::: warn Criterio… | valores de nsim barridos en el módulo 11 = [19, 39, 99, 999] | VERIFICADA · aritmética sobre el JSON |
| `999` | cuerpo | …se estrecha: ×**1.29989** entre 39 y 999. ::: ::: warn Criterio Elegi… | datos › m11.nsim = 999 | CONTRASTADA · salida de R (JSON) |

### Diapositiva 46 · Cinco ejercicios, cinco decisiones que hay que defender

| Cifra | Dónde | Contexto | Comprobación | Estado |
|---|---|---|---|---|
| `5.7` | cuerpo | …que decides \| ¿Qué ventana respalda «5,7 colegios por km²», y qué hab… | 5,7 = λ urbana (5.6932) redondeada a 1 decimal = 5.693212583 | VERIFICADA · aritmética sobre el JSON |
| `1972` | cuerpo | …Ejemplo del : pinos suecos (Strand, 1972).… | Strand (1972): `swedishpines`; 71 árboles en una parcela de 9.6 × 10 m · https://rdrr.io/cran/spatstat.data/man/swedishpines.html | REFERENCIA externa cotejada |
