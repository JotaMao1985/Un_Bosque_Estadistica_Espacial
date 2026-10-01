# Registro de cifras · Capítulo 5 · Sesión 2

Generado por `verifica_cifras_cap5.py` a partir de `capitulo_5_sesion_2.md`. **No se edita a mano**: se regenera.

Recómputo en R del 2026-10-01 (R version 4.4.1 (2024-06-14); spatstat 3.5.1, spatstat.explore 3.8.0, spatstat.model 3.6.1), con `recomputa_cap5_s2.R`.

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

- 474 apariciones de cifras en 41 diapositivas; 245 cifras distintas.
- VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo: 229
- VERIFICADA · re-ejecutada en R: 87
- VERIFICADA · aritmética sobre cifras verificadas: 76
- CONTRASTADA · salida de R (JSON del capítulo): 41
- PARÁMETRO de diseño: 26
- CONTRASTADA · texto del capítulo: 12
- REFERENCIA · ficha de ayuda del paquete: 3

## Hallazgos en el material del capítulo

Discrepancias que aparecieron al cotejar. No son errores de la presentación: se dicen aquí y en las notas, y no se corrigen en silencio.

- **La ayuda de `bei` habla de 3605 árboles; el conjunto trae 3 604.** La ficha de ayuda de `bei` (spatstat.data) dice «the locations of 3605 trees», pero `npoints(bei)` es 3604 (`recomputo › m7.bei.n`), que es la cifra del capítulo. Las diapositivas usan 3 604 y lo advierten en las notas.
- **«entre 21.12 y 21.14» (módulo 7).** El comentario del bloque de `rhohat` dice que la razón de la elevación «se mueve entre 21.12 y 21.14» sin tocar el dato. Con 20 semillas distintas (`recomputo › m7_semillas`) va de 21.10 a 21.15 (y con las semillas 2001 a 2020, de 21.0996 a 21.1592, según la auditoría). La conclusión (hay que fijar la semilla) no cambia; el intervalo sí. Las diapositivas dicen de 21.10 a 21.15.
- **El comentario del bloque de `rhohat`: «usa una cuadratura muestreada» (módulo 7).** Lo aleatorio de `rhohat` no es una cuadratura muestreada: es el `jitter = TRUE` por defecto, que añade ruido a los valores de la covariable en los puntos (ficha de ayuda, sección Randomisation). Con `jitter = FALSE` el resultado es idéntico en cada corrida y no consume el generador (`recomputo › m7b_jitter`). Las diapositivas dicen el mecanismo correcto y ofrecen `jitter = FALSE`.
- **«El máximo y el mínimo viven casi siempre en los extremos» (módulo 7).** El módulo 7 dice que el máximo y el mínimo de una curva `rhohat` «viven casi siempre en los extremos, donde apenas hay puntos». Medido sobre sus tres curvas (`datos › m7.*.rho_max`, `rho_min`, `rho_max_bulto`, `rho_min_bulto`): el mínimo cae fuera del bulto en las tres; el máximo, solo en la pendiente de `bei` (en la elevación y en la distancia de Bogotá coincide con el máximo del bulto). Lo que infla la razón es, sobre todo, un mínimo diminuto estimado en la cola. Las diapositivas dicen lo que se midió.
- **La pregunta de `rhohat`: el ancho del núcleo también mueve el titular (módulo 7).** La autoevaluación descarta que el 36.1 se deba a un núcleo demasiado estrecho. Con `adjust` (`jitter = FALSE`) la razón total de Bogotá es 3063 con la mitad del ancho, 36.04 con el defecto, 11.95 con el doble y 2.39 con cuatro veces, y la del bulto, de 2.10 a 1.11 (`recomputo › m7b_adjust`). La cola infla la razón a cualquier ancho, pero el ancho es parte de la historia. Las diapositivas lo dicen.
- **Aclaración: el 1.794e-10 es el condicionamiento de la matriz de diseño, no el de la información de Fisher (módulo 9).** El capítulo lo escribe bien («la matriz de diseño queda con número de condición recíproco 1.794e-10»), pero el texto que sigue habla de la información de Fisher y se puede leer como si fuera el mismo número. La información tiene un condicionamiento del orden del cuadrado (2.7e-20, `recomputo › m9b_info`), por debajo de la tolerancia de `solve` (2.2e-16); con 1.794e-10 `solve` no se quejaría. Las diapositivas distinguen los dos y avisan de los mensajes «Error in solve.default(M)» de la consola.
- **Las cifras de la envolvente del módulo 10 son de una semilla (62 %, 7.7 %, 38.53854 veces, 3638.23 m).** El módulo 10 las publica con cinco decimales, pero con la semilla 5028 salen 62 radios fuera de 100, 77 de 999 curvas que cruzan la banda (7.70771 %), 38.53854 veces el nivel puntual y un tramo que acaba en 3638.23 m. Con ocho semillas más (`recomputo › m10b_sem_1` a `m10b_sem_8`): 64 a 67 radios, de 53 a 78 curvas (5.3 a 7.8 %), 26.5 a 39 veces el nivel, un tramo que acaba entre 3.76 y 3.93 km, y p del MAD de 0.001 a 0.004. El 0.2 % del nivel puntual no cambia. Las diapositivas dicen «entre el 5 y el 8 %», «unas 30 veces» y dan el rango de las semillas.
- **«A menos de 0.64 %» (módulo 10).** El módulo 10 dice que la media de las 999 simulaciones queda «a menos de 0.64 %» de π r² en los 101 nodos. El máximo, sin redondear, es 0.64499 % con la semilla del capítulo (`datos › m10.mmean_vs_teorica_pct`) y llega a 0.82 % con otras (`recomputo › m10b_sem_4`). Las diapositivas dicen «a menos de 1 %». Además, son 100 radios informativos (r = 0 vale 0 en las dos curvas).
- **«El exceso de parejas está en las escalas cortas y medias; a escala de kilómetros el modelo ya da cuenta» (módulo 10).** La K es acumulada: cuenta todas las parejas a menos de r, de modo que un exceso a escalas cortas la mantiene fuera de la banda a escalas mayores. Los 3638.23 m son donde la K vuelve a entrar en la banda, no donde acaba el exceso por escala. La g inhomogénea (`recomputo › m10b_pcf`, 199 simulaciones) sale de su banda sin interrupción hasta 2.2 km y vale 1.20 a 1 km y 1.06 a 2 km. «Hasta dónde llega lo que el modelo no explica» es, entonces, unos 2 km, y no 3.6 km. Las diapositivas lo dicen así.
- **«La intensidad variable no explica la agregación» (módulo 10): se probó un plano, no «la intensidad variable».** La envolvente del módulo 10 es la de `ppm(~ xc + yc)`: un plano log-lineal en x e y (3 parámetros). Con una tendencia polinómica más flexible (`recomputo › m10b_flex`) los tests globales dejan de rechazar: grado 10 (66 parámetros), DCLF p = 0.055 y MAD 0.215; grado 12 (91 parámetros), DCLF 0.135 a 0.22 y MAD 0.345 a 0.415 (199 simulaciones). Esa curva llega a 208 sedes por km² y a casi cero en otros sitios: imita los grupos con la tendencia, y con un solo patrón tendencia y agrupación no se separan. El exceso por debajo de unos 2 km sobrevive (de 32 a 43 % de los radios siguen fuera). Las diapositivas acotan el veredicto a «un plano en x e y» y lo explican.
- **«Comparten manzana, predio y edificio» (módulo 10).** Es la explicación del capítulo para la agregación y no se comprobó con datos de predios. Lo medido (`recomputo › m11b_dups`): hay 79 sedes que comparten sitio exacto (39 sitios) y el 29.8 % de las sedes tiene otra a menos de 100 m, contra 16.3 % (sd 1.2) en 99 patrones simulados del modelo con tendencia. Las diapositivas la dan como explicación plausible no comprobada.
- **«Tres verosimilitudes distintas tardan lo mismo» (módulo 11).** `kppm` ajusta por contraste mínimo (`method = "mincon"`, el defecto, según la ayuda), y no evalúa ninguna verosimilitud; el propio capítulo lo dice un párrafo después. Tardan lo mismo porque el contraste solo evalúa su K teórica, que es barata: lo que se paga es estimar la K isotrópica (`Kest` isotrópica tarda casi todo el tiempo del ajuste, `recomputo › m11b_kemp`). Las diapositivas lo dicen así.
- **«El valle que el contraste mínimo está minimizando es casi plano» (módulo 11).** No se sostiene (`recomputo › m11b_valle`): evaluado cada contraste en los parámetros del otro ajuste, sube 178 % y 195 % sobre su mínimo, y con κ reoptimizado el de traslación sube 57 % en σ = 932 m: cada K empírica tiene su propio mínimo bien marcado. Lo que ocurre es otra cosa: κσ² (lo que fija la K a r corto) es casi igual (0.183 y 0.190), por eso las dos K coinciden hasta 1 km, pero κ lo fija el exceso K − π r² a r grande, una resta de números grandes: la K isotrópica queda hasta 5.5 % por debajo de la de traslación y 1/κ cambia ×1.93. Las diapositivas dan esta explicación.
- **«40 sitios con sedes repetidas» (módulo 11).** Son 40 sedes sobrantes en 39 sitios: 38 sitios con dos sedes y 1 con tres, 79 sedes implicadas (`recomputo › m11b_dups`). Las diapositivas dicen «40 sedes repetidas».
- **El μ de `kppm` hereda el +0.33 % del `ppm` forzado (módulo 11).** `kppm` ajusta por dentro un `ppm` con `forcefit = TRUE` y calcula μ = λ̂ / κ con ese λ̂: κ · μ = 5.7121 sedes por km², no 5.6932. Con n / |W| serían 27.0 y 52.2, y no 27.1 y 52.3. Las diapositivas conservan lo que devuelve `kppm` y lo advierten en las notas.
- **Los errores estándar de `vcov(kppm)` usan una aproximación rápida (módulo 11).** Con una cuadratura de 6247 puntos `vcov` da lo mismo que `fast = TRUE`, que la ayuda dice que subestima las varianzas. Con `fast = FALSE` el efecto de diseño es 26.1 y no 26.03409, y las 2 107 sedes valen 80.6 y no 80.93235 (`recomputo › m11b_vcov`). Las diapositivas dicen «unas 26» y «unas 80».
- **El índice de dispersión del Hawkes no tiene cinco decimales (módulo 11).** El 5.15454 es de una simulación y de 200 intervalos de 20 unidades: con 200 réplicas el índice tiene media 5.04 y desviación 0.57, y para la misma simulación va de 9.9 con 20 intervalos a 2.9 con 2000 (`recomputo › m11b_hawkes`). «5.4 veces más agregado» es de esa simulación. Las diapositivas dan 5.15 y 0.96, el tamaño del intervalo y el rango entre réplicas.
- **Los kppm con tendencia no son los de `~ 1` (módulo 11).** La tabla de errores estándar usa `kppm(~ xc + yc)`, que ajusta la K inhomogénea: sus parámetros de grupo cambian (Thomas con K de traslación, κ = 1.59e-07 y σ = 1067 m, contra 1.09e-07 y 1320 m con `~ 1`; `recomputo › m11b_trend`). El capítulo no lo dice. Las notas de las diapositivas sí.
- **Los tiempos del módulo 11 dependen de la máquina.** El capítulo publica 126.5 s contra 0.47 s para Thomas; al volver a ajustar aquí salen 128.8 s contra 0.48 s, y el cociente, 267.3 contra el 267.52220 del JSON. No es un error: son mediciones de tiempo. Se aceptan con tolerancia (MEDIDA) y las diapositivas dicen que los tiempos dependen de la máquina y «unas 270 veces».

## Afirmaciones que no son una cifra, y cómo se comprobaron

Cada una se vuelve a evaluar con el recómputo en R cada vez que se corre el verificador.

- ✓ En las tres curvas `rhohat` el mínimo cae fuera del bulto; el máximo, solo en la pendiente de `bei`
- ✓ Por el titular (razón en todo el rango) el orden es Bogotá, elevación, pendiente; por el bulto, el inverso
- ✓ `ppm(pu ~ 1)` es exacto y, con `forcefit = TRUE`, ajusta con `glm`
- ✓ Con `nd = 300` el modelo constante sigue siendo exacto y con el mismo AIC
- ✓ El AIC baja de nd = 50 a 100, queda casi quieto de 100 a 200 y sube a 300
- ✓ El AIC sigue a la ciudad sin contar en sentido inverso: a más área sin contar, menos AIC
- ✓ Con la integral bien hecha el constante gana a `dcen` por 0.07 y, por la misma cuadratura, por 0.51644; con los AIC de `ppm`, `dcen` gana por 13.44572
- ✓ La ventaja de `dcen` con los AIC de `ppm` es el AIC del constante exacto menos el de `dcen` por defecto
- ✓ El ajuste crudo no da errores estándar: `vcov()` es NULL, `sqrt(diag(NULL))` mide 0 × 0 y no hay un error estándar por coeficiente
- ✓ El ajuste crudo y el centrado tienen el mismo AIC (es el mismo modelo)
- ✓ Centrar y pasar a kilómetros mejora el condicionamiento
- ✓ Con errores estándar de Poisson, `xc` pasa de 1.96 en valor absoluto; `yc` y `dcen`, no
- ✓ Los 62 radios fuera de la banda (de 100) están todos por encima; ninguno por debajo
- ✓ El tramo fuera de la banda es contiguo, va de 58.68 a 3638.23 m y los 38 nodos que siguen están dentro
- ✓ La peor desviación del patrón (MAD) cae dentro del tramo; las 3 simulaciones que la superan están pasado su final
- ✓ Con 39 simulaciones el p mínimo posible es 1/(39 + 1) y DCLF y MAD lo alcanzan; con 999, el DCLF alcanza 1/(999 + 1)
- ✓ Leída entera, la banda se cruza más veces que su nivel puntual (7.7 % contra 0.2 %, 38.53854 veces)
- ✓ La media de las 999 simulaciones queda a menos de 0.65 % de π r² y no a menos de 0.64 %
- ✓ Los tres tiempos con K isotrópica son del mismo orden (cociente máximo / mínimo menor que 1.05) y los de traslación son más de 100 veces menores
- ✓ Con K de traslación, en Thomas κ baja y la escala y μ suben
- ✓ La escala de Matérn es casi el doble de la de Thomas con cualquiera de las dos correcciones (cociente entre 1.8 y 2.0): son parámetros distintos y no se comparan
- ✓ `kppm` es determinista: dos corridas con semillas distintas dan el mismo ajuste
- ✓ Sin los 40 duplicados, la escala de Thomas pasa de 1320 a 1373 m (4.0 %) y el mayor cambio de todos los parámetros de los tres modelos es 6.2 %
- ✓ Con conglomerados, los seis errores estándar superan el de Poisson y ninguna |z| llega a 1.96; con K isotrópica el error crece menos que con la de traslación
- ✓ Hawkes: la dispersión supera 1, la del Poisson de su misma tasa queda por debajo de 1 y la tasa simulada queda a menos de 3 % de la teórica
- ✓ Con la misma envolvente, el plano (grado 1) es rechazado por los dos tests globales y una tendencia de grado 12 (91 parámetros) no lo es, aunque el DCLF queda al borde con el grado 10
- ✓ La tendencia de grado 12 llega a más de 200 sedes por km² y a casi cero en otros sitios (imita los grupos), y su AIC con la integral fina es unos 490 puntos menor que el del plano
- ✓ El 29.8 % de las sedes tiene otra a menos de 100 m, casi el doble que bajo el modelo con tendencia (16.3 %, sd 1.2); hay 79 sedes en 39 sitios con más de una sede y 40 sedes sobrantes
- ✓ Cambiar de familia (Thomas a Matérn) mueve κ y μ menos de 0.3 %; cambiar de estimador (isotrópica a traslación), 48.2 % y 93.2 %
- ✓ κ · μ de `kppm` es el λ̂ del `ppm` forzado por la cuadratura (5.71211), no n / |W| (5.69321)
- ✓ κσ² es casi igual en los dos ajustes de Thomas (diferencia menor que 5 %) y 1/κ cambia casi el doble; la K isotrópica queda por debajo de la de traslación en todo r > 250 m, hasta 5.5 %
- ✓ La g inhomogénea sale de su banda sin interrupción hasta 2.2 km (89 radios seguidos) y vale 1.20 a 1 km y 1.06 a 2 km, mientras la K sigue fuera de la banda hasta 3.6 km (5028) o más
- ✓ `rhohat` con `jitter = FALSE` da lo mismo en cada corrida y no consume el generador; con `jitter = TRUE` difiere y sí lo consume
- ✓ El ancho del núcleo mueve el titular de Bogotá (de 3 063 con la mitad del ancho a 2.39 con cuatro veces) y el bulto (de 2.10 a 1.11), pero la cola infla la razón a cualquier ancho
- ✓ El condicionamiento de la matriz de diseño cruda (1.794e-10) es mayor que la tolerancia de `solve` (2.2e-16) y el de la información de Fisher (2.7e-20) es menor; `solve` falla con ella
- ✓ Con `fast = FALSE` el efecto de diseño de Thomas con K de traslación (26.1) y las 2 107 sedes (80.6 efectivas) casi no cambian respecto de la aproximación por defecto (26.03409 y 80.93235)
- ✓ Los `kppm` con tendencia (`~ xc + yc`) tienen otros parámetros de grupo que los de `~ 1`: Thomas con K de traslación, κ = 1.59e-07 y σ = 1067 m contra 1.09e-07 y 1320 m
- ✓ El índice de dispersión del Hawkes cambia con el tamaño del intervalo (de 9.9 con 20 intervalos a 2.9 con 2000) y entre realizaciones (media 5.0, sd 0.6 en 200 réplicas); la tasa simulada está a media desviación de una réplica de la teórica
- ✓ Evaluado cada contraste mínimo de Thomas en los parámetros del otro ajuste sube casi el triple (178 % y 195 % sobre su mínimo) y, con κ reoptimizado, el de traslación ya sube más de la mitad en σ = 932 m: no es un valle casi plano; el objetivo propio coincide con el de spatstat (×513)
- ✓ `kppm` ajusta por contraste mínimo por defecto (no evalúa una verosimilitud) y `vcov(kppm)` con esta cuadratura da lo mismo que `fast = TRUE`, que la ayuda dice que subestima las varianzas
- ✓ Los óptimos propios del contraste (κ y σ de Thomas con cada K) coinciden con los de `kppm` con tres cifras

## Cifra por cifra

### Diapositiva 1 · Portada

| Cifra | Dónde | Contexto | Comprobación | Estado |
|---|---|---|---|---|
| `90` | cuerpo | …etiqueta: de 2 · 90 min subtitulo: Modelar la int… | duración de la clase pedida por el docente (90 min), decisión D1; no es un dato del capítulo | PARÁMETRO de diseño |

### Diapositiva 3 · De estimar a modelar

| Cifra | Dónde | Contexto | Comprobación | Estado |
|---|---|---|---|---|
| `90` | notas | …Presupuesto de los 90 min: apertura (portada, hoja… | duración de la clase pedida por el docente (90 min), decisión D1; no es un dato del capítulo | PARÁMETRO de diseño |
| `6` | notas | …tada, hoja de ruta, tesis y ejemplo), 6 min; covariables, 12 min; Poi… | minutos de la apertura (portada, hoja de ruta, tesis y ejemplo): decisión del docente, no un dato del capítulo | PARÁMETRO de diseño |
| `12` | notas | …tesis y ejemplo), 6 min; covariables, 12 min; Poisson inhomogéneo, 20… | minutos que se asignan a cada bloque de la sesión: decisión del docente, no un dato del capítulo | PARÁMETRO de diseño |
| `20` | notas | …riables, 12 min; Poisson inhomogéneo, 20 min; , 12 min; diagnóstico d… | minutos que se asignan a cada bloque de la sesión: decisión del docente, no un dato del capítulo | PARÁMETRO de diseño |
| `12` | notas | …min; Poisson inhomogéneo, 20 min; , 12 min; diagnóstico del ajuste,… | minutos que se asignan a cada bloque de la sesión: decisión del docente, no un dato del capítulo | PARÁMETRO de diseño |
| `14` | notas | …n; , 12 min; diagnóstico del ajuste, 14 min; conglomerados, 17 min; c… | minutos que se asignan a cada bloque de la sesión: decisión del docente, no un dato del capítulo | PARÁMETRO de diseño |
| `17` | notas | …co del ajuste, 14 min; conglomerados, 17 min; cierre y práctica, 5 min… | minutos que se asignan a cada bloque de la sesión: decisión del docente, no un dato del capítulo | PARÁMETRO de diseño |
| `5` | notas | …lomerados, 17 min; cierre y práctica, 5 min. Suman 86; los 4 restante… | minutos que se asignan a cada bloque de la sesión: decisión del docente, no un dato del capítulo | PARÁMETRO de diseño |
| `86` | notas | …min; cierre y práctica, 5 min. Suman 86; los 4 restantes son margen p… | suma de los minutos asignados a los bloques de la sesión = 86 | VERIFICADA · aritmética sobre cifras verificadas |
| `4` | notas | …erre y práctica, 5 min. Suman 86; los 4 restantes son margen para pre… | los 90 min menos los 86 asignados = 4 | VERIFICADA · aritmética sobre cifras verificadas |

### Diapositiva 4 · Un modelo que ajusta no es un modelo que se pueda leer

| Cifra | Dónde | Contexto | Comprobación | Estado |
|---|---|---|---|---|
| `36.1` | cuerpo | …io y engaña: - una curva que varía 36.1 veces en total y 1.58 donde h… | datos › m7.bogota.curva.razon = 36.0759; recomputo › m7.bogota.total = 36.07589681 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `1.58` | cuerpo | …rva que varía 36.1 veces en total y 1.58 donde hay datos - un AIC (el… | datos › m7.bogota.curva.razon_bulto = 1.58183; recomputo › m7.bogota.bulto = 1.581834466 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `9.2` | cuerpo | …que se comparan modelos) que se mueve 9.2 puntos sin que el modelo cam… | datos › m8.cuadratura.rango_aic = 9.199466457; recomputo › m8_nd.rango_aic = 9.199466457 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `0.2` | cuerpo | …ningún error estándar - una banda «de 0.2 %» que el propio modelo cruz… | datos › m10.nivel_puntual_pct = 0.2; recomputo › m10.nivel_puntual_pct = 0.2 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `5` | cuerpo | …» que el propio modelo cruza entre el 5 y el 8 % de las veces - un co… | mínimo de la tasa de salida de la banda entera con nueve semillas (5.31 %), hacia abajo = 5 | VERIFICADA · aritmética sobre cifras verificadas |
| `8` | cuerpo | …l propio modelo cruza entre el 5 y el 8 % de las veces - un conglomer… | máximo de la tasa de salida de la banda entera con nueve semillas (7.81 %), hacia arriba = 8 | VERIFICADA · aritmética sobre cifras verificadas |
| `27.1` | cuerpo | …8 % de las veces - un conglomerado de 27.1 sedes o de 52.3, según cómo… | datos › m11.ajustes[0].mu = 27.09650952; recomputo › m11_Thomas.iso.mu = 27.09650952 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `52.3` | cuerpo | …- un conglomerado de 27.1 sedes o de 52.3, según cómo se estime K Fue… | datos › m11.ajustes[1].mu = 52.34765759; recomputo › m11_Thomas.translate.mu = 52.34765759 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |

### Diapositiva 5 · El ejemplo que nos acompaña sigue siendo el de la sesión 1: las sedes de Bogotá

| Cifra | Dónde | Contexto | Comprobación | Estado |
|---|---|---|---|---|
| `12.25` | cuerpo | …D, vía Datos Abiertos Bogotá, versión 12.25): 2 209 sedes, de las que … | texto del capítulo: «versión 12.25» | CONTRASTADA · texto del capítulo |
| `2209` | cuerpo | …atos Abiertos Bogotá, versión 12.25): 2 209 sedes, de las que **2 107*… | recomputo › urbana.n_capa = 2209 | VERIFICADA · re-ejecutada en R |
| `2107` | cuerpo | …ión 12.25): 2 209 sedes, de las que **2 107** caen dentro del perímetr… | datos › m5.capas.oferta.n = 2107; recomputo › urbana.n_urbana = 2107 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `22` | cuerpo | …del perímetro urbano (una ventana de 22 piezas); coordenadas en metro… | recomputo › m11_ventana.piezas = 22 | VERIFICADA · re-ejecutada en R |
| `9377` | cuerpo | …piezas); coordenadas en metros (EPSG:9377). **Por qué importa:** es el… | texto del capítulo: «EPSG:9377» | CONTRASTADA · texto del capítulo |
| `2107` | cuerpo | …fórmula: \hat\lambda = 2\,107 / 370.09\ \text{km}^2 = 5.69… | datos › m5.capas.oferta.n = 2107; recomputo › urbana.n_urbana = 2107 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `370.09` | cuerpo | …fórmula: \hat\lambda = 2\,107 / 370.09\ \text{km}^2 = 5.69… | recomputo › urbana.area_km2 = 370.0898165 | VERIFICADA · re-ejecutada en R |
| `5.69` | cuerpo | …fórmula: \hat\lambda = 2\,107 / 370.09\ \text{km}^2 = 5.69… | recomputo › urbana.lambda_km2 = 5.693212582 \| texto del capítulo: «5.6932» | VERIFICADA · re-ejecutada en R |
| `2107` | notas | …. En el código, es el patrón de las 2 107 sedes y , su ventana. Los 5.… | datos › m5.capas.oferta.n = 2107; recomputo › urbana.n_urbana = 2107 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `5.69` | notas | …las 2 107 sedes y , su ventana. Los 5.69 son la intensidad ingenua n e… | recomputo › urbana.lambda_km2 = 5.693212582 \| texto del capítulo: «5.6932» | VERIFICADA · re-ejecutada en R |

### Diapositiva 6 · Covariables

| Cifra | Dónde | Contexto | Comprobación | Estado |
|---|---|---|---|---|
| `12` | notas | …Unos 12 minutos. Cuatro piezas: qué h… | minutos que se asignan a cada bloque de la sesión: decisión del docente, no un dato del capítulo | PARÁMETRO de diseño |

### Diapositiva 7 · `rhohat` dibuja la intensidad como función de una covariable, sin suponer ninguna forma

| Cifra | Dónde | Contexto | Comprobación | Estado |
|---|---|---|---|---|
| `3604` | cuerpo | …Los 3 604 árboles de bei sobre la eleva… | datos › m7.bei.n = 3604; recomputo › m7.bei.n = 3604 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `3604` | cuerpo | …dónde sale:** y (spatstat.data): 3 604 árboles en 1000 m por 500 m;… | datos › m7.bei.n = 3604; recomputo › m7.bei.n = 3604 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `1000` | cuerpo | …y (spatstat.data): 3 604 árboles en 1000 m por 500 m; la elevación va… | recomputo › m7.bei.ventana_x_m = 1000 | VERIFICADA · re-ejecutada en R |
| `500` | cuerpo | …at.data): 3 604 árboles en 1000 m por 500 m; la elevación va de 119.81… | recomputo › m7.bei.ventana_y_m = 500 | VERIFICADA · re-ejecutada en R |
| `119.81` | cuerpo | …1000 m por 500 m; la elevación va de 119.81 a 159.48 m. **Por qué impo… | recomputo › m7.bei.elevacion_min_m = 119.81 | VERIFICADA · re-ejecutada en R |
| `159.48` | cuerpo | …or 500 m; la elevación va de 119.81 a 159.48 m. **Por qué importa:** s… | recomputo › m7.bei.elevacion_max_m = 159.48 | VERIFICADA · re-ejecutada en R |
| `3605` | notas | …km² en Bogotá. La ayuda de habla de 3605 árboles; el conjunto trae 3 6… | ayuda de spatstat.data (recomputo › m7.bei.ayuda): «3605 trees» | REFERENCIA · ficha de ayuda del paquete |
| `3604` | notas | …bla de 3605 árboles; el conjunto trae 3 604, que es la cifra del capít… | datos › m7.bei.n = 3604; recomputo › m7.bei.n = 3604 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |

### Diapositiva 8 · La curva `rhohat` de Bogotá sube 36.1 veces de mínimo a máximo. ¿De dónde sale?

| Cifra | Dónde | Contexto | Comprobación | Estado |
|---|---|---|---|---|
| `36.1` | titulo | …La curva de Bogotá sube 36.1 veces de mínimo a máximo. ¿De… | datos › m7.bogota.curva.razon = 36.0759; recomputo › m7.bogota.total = 36.07589681 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `2107` | cuerpo | …la distancia al centro de masa de las 2 107 sedes urbanas. De que la d… | datos › m5.capas.oferta.n = 2107; recomputo › urbana.n_urbana = 2107 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `5` | cuerpo | …si no hay datos Entre los percentiles 5 y 95 de la distancia observad… | percentil inferior del bulto: parámetro de diseño del capítulo (entre los percentiles 5 y 95) | PARÁMETRO de diseño |
| `95` | cuerpo | …o hay datos Entre los percentiles 5 y 95 de la distancia observada, la… | percentil superior del bulto: parámetro de diseño del capítulo (entre los percentiles 5 y 95) | PARÁMETRO de diseño |
| `1.58` | cuerpo | …ancia observada, la misma curva varía 1.58 veces: la cola infla la raz… | datos › m7.bogota.curva.razon_bulto = 1.58183; recomputo › m7.bogota.bulto = 1.581834466 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `22.8` | cuerpo | …ía 1.58 veces: la cola infla la razón 22.8 veces. es la lectura del ti… | datos › m7.bogota.curva.cola_infla = 22.8064; recomputo › m7.bogota.infla = 22.80636664 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `3063` | cuerpo | …el ancho del núcleo mueve el titular (3 063 con la mitad del ancho, 2.… | recomputo › m7b_adjust.total[0] = 3062.96715 | VERIFICADA · re-ejecutada en R |
| `2.39` | cuerpo | …itular (3 063 con la mitad del ancho, 2.39 con cuatro veces el ancho) … | recomputo › m7b_adjust.total[3] = 2.385632847 | VERIFICADA · re-ejecutada en R |
| `2.10` | cuerpo | …cuatro veces el ancho) y el bulto (de 2.10 a 1.11), pero con cualquier… | recomputo › m7b_adjust.bulto[0] = 2.10341324 | VERIFICADA · re-ejecutada en R |
| `1.11` | cuerpo | …veces el ancho) y el bulto (de 2.10 a 1.11), pero con cualquier ancho … | recomputo › m7b_adjust.bulto[3] = 1.105741282 | VERIFICADA · re-ejecutada en R |

### Diapositiva 9 · Donde hay datos, la curva de Bogotá varía 1.58 veces y no 36.1

| Cifra | Dónde | Contexto | Comprobación | Estado |
|---|---|---|---|---|
| `1.58` | titulo | …e hay datos, la curva de Bogotá varía 1.58 veces y no 36.1… | datos › m7.bogota.curva.razon_bulto = 1.58183; recomputo › m7.bogota.bulto = 1.581834466 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `36.1` | titulo | …curva de Bogotá varía 1.58 veces y no 36.1… | datos › m7.bogota.curva.razon = 36.0759; recomputo › m7.bogota.total = 36.07589681 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `5` | cuerpo | …Gris: el bulto (percentiles 5 y 95). Banda clara: confianza… | percentil inferior del bulto: parámetro de diseño del capítulo (entre los percentiles 5 y 95) | PARÁMETRO de diseño |
| `95` | cuerpo | …Gris: el bulto (percentiles 5 y 95). Banda clara: confianza del… | percentil superior del bulto: parámetro de diseño del capítulo (entre los percentiles 5 y 95) | PARÁMETRO de diseño |
| `95` | cuerpo | …s 5 y 95). Banda clara: confianza del 95 %. Marcas del eje: dónde hay… | percentil superior del bulto: parámetro de diseño del capítulo (entre los percentiles 5 y 95) | PARÁMETRO de diseño |
| `9.0` | cuerpo | …::: info Dato La cola infla la razón 9.0 (elevación), 2.5 (pendiente)… | datos › m7.bei.elevacion.cola_infla = 8.96907; recomputo › m7.elevacion.infla = 8.969072247 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `2.5` | cuerpo | …cola infla la razón 9.0 (elevación), 2.5 (pendiente) y 22.8 veces (Bog… | datos › m7.bei.pendiente.cola_infla = 2.50636; recomputo › m7.pendiente.infla = 2.506362504 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `22.8` | cuerpo | …ón 9.0 (elevación), 2.5 (pendiente) y 22.8 veces (Bogotá): con ella, B… | datos › m7.bogota.curva.cola_infla = 22.8064; recomputo › m7.bogota.infla = 22.80636664 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `3.34` | notas | …ltima, y la pendiente de manda más (3.34) que su elevación (2.36) y qu… | datos › m7.bei.pendiente.razon_bulto = 3.34267; recomputo › m7.pendiente.bulto = 3.342673276 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `2.36` | notas | …manda más (3.34) que su elevación (2.36) y que la distancia al centro… | datos › m7.bei.elevacion.razon_bulto = 2.35639; recomputo › m7.elevacion.bulto = 2.356391328 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `1.58` | notas | …(2.36) y que la distancia al centro (1.58): el orden se invierte. Crit… | datos › m7.bogota.curva.razon_bulto = 1.58183; recomputo › m7.bogota.bulto = 1.581834466 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |

### Diapositiva 10 · `rhohat` es aleatorio: se fija la semilla y se mide el bulto antes de publicar una razón

| Cifra | Dónde | Contexto | Comprobación | Estado |
|---|---|---|---|---|
| `20` | cuerpo | …te: del capítulo (R, spatstat); las 20 semillas, en el recómputo.… | recomputo › m7_semillas.n_semillas = 20 | VERIFICADA · re-ejecutada en R |
| `20` | cuerpo | …l recómputo. \|\|\| ::: info Dato Con 20 semillas distintas, la razón… | recomputo › m7_semillas.n_semillas = 20 | VERIFICADA · re-ejecutada en R |
| `21.10` | cuerpo | …, la razón de la elevación de va de 21.10 a 21.15. ::: ::: warn Criter… | recomputo › m7_semillas.min = 21.10121409 | VERIFICADA · re-ejecutada en R |
| `21.15` | cuerpo | …ón de la elevación de va de 21.10 a 21.15. ::: ::: warn Criterio Sin… | recomputo › m7_semillas.max = 21.14845797 | VERIFICADA · re-ejecutada en R |
| `20` | notas | …elevación depende de la semilla: con 20 semillas va de 21.10 a 21.15,… | recomputo › m7_semillas.n_semillas = 20 | VERIFICADA · re-ejecutada en R |
| `21.10` | notas | …de la semilla: con 20 semillas va de 21.10 a 21.15, y el capítulo escr… | recomputo › m7_semillas.min = 21.10121409 | VERIFICADA · re-ejecutada en R |
| `21.15` | notas | …emilla: con 20 semillas va de 21.10 a 21.15, y el capítulo escribe «en… | recomputo › m7_semillas.max = 21.14845797 | VERIFICADA · re-ejecutada en R |
| `21.12` | notas | …a 21.15, y el capítulo escribe «entre 21.12 y 21.14» (ver el registro)… | texto del capítulo: «entre 21.12 y 21.14» | CONTRASTADA · texto del capítulo |
| `21.14` | notas | …y el capítulo escribe «entre 21.12 y 21.14» (ver el registro). La de B… | texto del capítulo: «entre 21.12 y 21.14» | CONTRASTADA · texto del capítulo |
| `36.1` | notas | …Bogotá depende además del suavizador: 36.1 es lo que da este. Cotejo: … | datos › m7.bogota.curva.razon = 36.0759; recomputo › m7.bogota.total = 36.07589681 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |

### Diapositiva 11 · El Poisson inhomogéneo

| Cifra | Dónde | Contexto | Comprobación | Estado |
|---|---|---|---|---|
| `20` | notas | …Unos 20 minutos: la parte más técnica… | minutos que se asignan a cada bloque de la sesión: decisión del docente, no un dato del capítulo | PARÁMETRO de diseño |

### Diapositiva 13 · En el máximo, el modelo reparte por la ventana exactamente tantas sedes como hay

| Cifra | Dónde | Contexto | Comprobación | Estado |
|---|---|---|---|---|
| `7.44e-16` | cuerpo | …r km², con una diferencia relativa de 7.44e-16. ::: ::: warn Criterio … | datos › m8.homogeneo.dif_relativa = 7.44e-16; recomputo › m8_homogeneo.dif_relativa = 7.438971714e-16 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `5.6932` | cuerpo | …ngenua del . ::: ::: info Dato da 5.6932 sedes por km², con una difere… | datos › m8.homogeneo.lambda_km2 = 5.693212583; recomputo › m8_homogeneo.lambda_km2 = 5.693212582 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `7.44e-16` | notas | …cha deja de valer n. La diferencia de 7.44e-16 es ruido de coma flotan… | datos › m8.homogeneo.dif_relativa = 7.44e-16; recomputo › m8_homogeneo.dif_relativa = 7.438971714e-16 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |

### Diapositiva 14 · Berman y Turner cambian la integral por una suma sobre las sedes y 4 140 puntos ficticios

| Cifra | Dónde | Contexto | Comprobación | Estado |
|---|---|---|---|---|
| `4140` | titulo | …tegral por una suma sobre las sedes y 4 140 puntos ficticios… | datos › m8.cuadratura.defecto_ficticios = 4140; recomputo › m8_nd.ficticios_por_defecto = 4140 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `100` | cuerpo | …sta con . ::: ::: info Dato Con = 100 (el defecto) hay 4 140 fictic… | datos › m8.cuadratura.defecto_nd = 100 | CONTRASTADA · salida de R (JSON del capítulo) |
| `4140` | cuerpo | …nfo Dato Con = 100 (el defecto) hay 4 140 ficticios, además de las 2 1… | datos › m8.cuadratura.defecto_ficticios = 4140; recomputo › m8_nd.ficticios_por_defecto = 4140 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `2107` | cuerpo | …o) hay 4 140 ficticios, además de las 2 107 sedes. ::: ::: warn Criter… | datos › m5.capas.oferta.n = 2107; recomputo › urbana.n_urbana = 2107 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |

### Diapositiva 15 · Por la cuadratura, el modelo constante pasa de 5.69321 a 5.71211 sedes por km²

| Cifra | Dónde | Contexto | Comprobación | Estado |
|---|---|---|---|---|
| `5.69321` | titulo | …adratura, el modelo constante pasa de 5.69321 a 5.71211 sedes por km²… | datos › m8.homogeneo.lambda_km2 = 5.693212583; recomputo › m8_homogeneo.lambda_km2 = 5.693212582 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `5.71211` | titulo | …el modelo constante pasa de 5.69321 a 5.71211 sedes por km²… | datos › m8.forzado.lambda_km2 = 5.712107067; recomputo › m8_homogeneo.forzado.lambda_km2 = 5.712107068 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `0.33` | cuerpo | …info Dato Forzado por la cuadratura: 0.33 % más que el cálculo exacto.… | datos › m8.forzado.exceso_pct = 0.331877385; recomputo › m8_homogeneo.forzado.exceso_pct = 0.331877385 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `368.86563` | cuerpo | …ue el cálculo exacto. Los pesos suman 368.86563 km² y la ciudad mide 3… | datos › m8.forzado.suma_pesos_km2 = 368.8656349; recomputo › m8_homogeneo.forzado.suma_pesos_km2 = 368.8656349 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `370.08982` | cuerpo | …suman 368.86563 km² y la ciudad mide 370.08982. ::: ::: tip Interpreta… | datos › m8.forzado.area_km2 = 370.0898165; recomputo › m8_homogeneo.area_km2 = 370.0898165 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `5.69321` | notas | …se calcula, y el campo lo declara (5.69321 sedes por km², el mismo n e… | datos › m8.homogeneo.lambda_km2 = 5.693212583; recomputo › m8_homogeneo.lambda_km2 = 5.693212582 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `5.71211` | notas | …rlo con sobre la cuadratura, y sale 5.71211. Se quitó del bloque del c… | datos › m8.forzado.lambda_km2 = 5.712107067; recomputo › m8_homogeneo.forzado.lambda_km2 = 5.712107068 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `2107` | notas | …es la evidencia de la Interpretación: 2 107 entre 368.86563 km² da lo … | datos › m5.capas.oferta.n = 2107; recomputo › urbana.n_urbana = 2107 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `368.86563` | notas | …cia de la Interpretación: 2 107 entre 368.86563 km² da lo mismo que el… | datos › m8.forzado.suma_pesos_km2 = 368.8656349; recomputo › m8_homogeneo.forzado.suma_pesos_km2 = 368.8656349 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |

### Diapositiva 16 · La cuadratura deja sin contar 1.22418 km² de ciudad: 201 teselas del borde sin puntos

| Cifra | Dónde | Contexto | Comprobación | Estado |
|---|---|---|---|---|
| `1.22418` | titulo | …La cuadratura deja sin contar 1.22418 km² de ciudad: 201 teselas de… | datos › m8.cuadratura.tabla[1].sin_contar_km2 = 1.224181623; recomputo › m8_homogeneo.forzado.faltan_km2 = 1.224181623 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `201` | titulo | …eja sin contar 1.22418 km² de ciudad: 201 teselas del borde sin puntos… | datos › m8.cuadratura.tabla[1].teselas_vacias = 201; recomputo › m8_homogeneo.forzado.teselas_vacias = 201 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `100x100` | cuerpo | …ato Los pesos salen de una rejilla de 100 × 100 teselas: de las 4 345 … | datos › m8.cuadratura.tabla[1].rejilla_pesos = 100 \| recomputo › m8_homogeneo.ntile = [100, 100] | VERIFICADA · re-ejecutada en R |
| `200x200` | cuerpo | …coloca los ficticios sobre píxeles de 200 × 200 y ningún píxel tiene s… | datos › m8.cuadratura.tabla[1].pixeles = 200 \| recomputo › m8_homogeneo.npix = [200, 200] | VERIFICADA · re-ejecutada en R |
| `201` | cuerpo | …201 teselas vacías en el borde de… | datos › m8.cuadratura.tabla[1].teselas_vacias = 201; recomputo › m8_homogeneo.forzado.teselas_vacias = 201 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `4345` | cuerpo | …n de una rejilla de teselas: de las 4 345 que tocan la ciudad, **201**… | datos › m8.cuadratura.tabla[1].teselas_tocan = 4345; recomputo › m8_homogeneo.forzado.teselas_tocan = 4345 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `201` | cuerpo | …: de las 4 345 que tocan la ciudad, **201** quedan sin ningún punto y … | datos › m8.cuadratura.tabla[1].teselas_vacias = 201; recomputo › m8_homogeneo.forzado.teselas_vacias = 201 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `1.22418` | cuerpo | …01** quedan sin ningún punto y faltan 1.22418 km² de 370.08982. ::: ::… | datos › m8.cuadratura.tabla[1].sin_contar_km2 = 1.224181623; recomputo › m8_homogeneo.forzado.faltan_km2 = 1.224181623 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `370.08982` | cuerpo | …ningún punto y faltan 1.22418 km² de 370.08982. ::: ::: tip Interpreta… | datos › m8.forzado.area_km2 = 370.0898165; recomputo › m8_homogeneo.area_km2 = 370.0898165 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `235` | notas | …tramo ampliado cada tesela mide unos 235 por 400 m (la caja de la ciud… | recomputo › m8_homogeneo.tesela_m[0] = 234.7246293 | VERIFICADA · re-ejecutada en R |
| `400` | notas | …mpliado cada tesela mide unos 235 por 400 m (la caja de la ciudad entr… | recomputo › m8_homogeneo.tesela_m[1] = 399.9692573 | VERIFICADA · re-ejecutada en R |
| `100` | notas | …por 400 m (la caja de la ciudad entre 100 en cada eje); en rojo, las q… | datos › m8.cuadratura.tabla[1].rejilla_pesos = 100 | CONTRASTADA · salida de R (JSON del capítulo) |

### Diapositiva 17 · Un modelo, cuatro cuadraturas: el AIC se mueve 9.2 puntos

| Cifra | Dónde | Contexto | Comprobación | Estado |
|---|---|---|---|---|
| `9.2` | titulo | …, cuatro cuadraturas: el AIC se mueve 9.2 puntos… | datos › m8.cuadratura.rango_aic = 9.199466457; recomputo › m8_nd.rango_aic = 9.199466457 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `50` | cuerpo | …n hecha \| \|---\|---\|---\|---\|---\|---\| \| 50 \| 1 099 \| 0.75800 … | datos › m8.cuadratura.tabla[0].nd = 50 | CONTRASTADA · salida de R (JSON del capítulo) |
| `1099` | cuerpo | …ha \| \|---\|---\|---\|---\|---\|---\| \| 50 \| 1 099 \| 0.75800 \| 55… | datos › m8.cuadratura.tabla[0].ficticios = 1099; recomputo › m8_nd.filas[0].ficticios = 1099 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `0.75800` | cuerpo | …-\|---\|---\|---\|---\|---\| \| 50 \| 1 099 \| 0.75800 \| 55097.08 \| … | datos › m8.cuadratura.tabla[0].sin_contar_km2 = 0.7579985595; recomputo › m8_nd.filas[0].sin_contar_km2 = 0.7579985595 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `55097.08` | cuerpo | …---\|---\|---\| \| 50 \| 1 099 \| 0.75800 \| 55097.08 \| −27546.54 \| … | datos › m8.cuadratura.tabla[0].aic = 55097.0816; recomputo › m8_nd.filas[0].aic = 55097.0816 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `-27546.54` | cuerpo | …\| \| 50 \| 1 099 \| 0.75800 \| 55097.08 \| −27546.54 \| −27550.65 \| … | datos › m8.cuadratura.tabla[0].logver_ppm = -27546.5408; recomputo › m8_nd.filas[0].logver_ppm = -27546.5408 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `-27550.65` | cuerpo | …99 \| 0.75800 \| 55097.08 \| −27546.54 \| −27550.65 \| \| 100 \| 4 140… | datos › m8.cuadratura.tabla[0].logver_exacta = -27550.65207; recomputo › m8_nd.filas[0].logver_exacta = -27550.65207 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `100` | cuerpo | …55097.08 \| −27546.54 \| −27550.65 \| \| 100 \| 4 140 \| 1.22418 \| 55… | datos › m8.cuadratura.defecto_nd = 100 | CONTRASTADA · salida de R (JSON del capítulo) |
| `4140` | cuerpo | ….08 \| −27546.54 \| −27550.65 \| \| 100 \| 4 140 \| 1.22418 \| 55091.8… | datos › m8.cuadratura.defecto_ficticios = 4140; recomputo › m8_nd.ficticios_por_defecto = 4140 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `1.22418` | cuerpo | …7546.54 \| −27550.65 \| \| 100 \| 4 140 \| 1.22418 \| 55091.81 \| −275… | datos › m8.cuadratura.tabla[1].sin_contar_km2 = 1.224181623; recomputo › m8_homogeneo.forzado.faltan_km2 = 1.224181623 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `55091.81` | cuerpo | …−27550.65 \| \| 100 \| 4 140 \| 1.22418 \| 55091.81 \| −27543.91 \| −2… | datos › m8.cuadratura.tabla[1].aic = 55091.81223; recomputo › m8_nd.filas[1].aic = 55091.81223 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `-27543.91` | cuerpo | …\| 100 \| 4 140 \| 1.22418 \| 55091.81 \| −27543.91 \| −27550.66 \| \|… | datos › m8.cuadratura.tabla[1].logver_ppm = -27543.90611; recomputo › m8_nd.filas[1].logver_ppm = -27543.90611 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `-27550.66` | cuerpo | …40 \| 1.22418 \| 55091.81 \| −27543.91 \| −27550.66 \| \| 200 \| 15 76… | datos › m8.cuadratura.tabla[1].logver_exacta, m8.cuadratura.tabla[2].logver_exacta = [-27550.6626902924, -27550.6615108904]; recomputo › m8_nd.filas[1].logver_exacta, m8_nd.filas[2].logver_exacta = [-27550.6626902925, -27550.66151 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `200` | cuerpo | …55091.81 \| −27543.91 \| −27550.66 \| \| 200 \| 15 764 \| 1.22418 \| 5… | datos › m8.cuadratura.tabla[2].nd = 200 | CONTRASTADA · salida de R (JSON del capítulo) |
| `15764` | cuerpo | ….81 \| −27543.91 \| −27550.66 \| \| 200 \| 15 764 \| 1.22418 \| 55091.… | datos › m8.cuadratura.tabla[2].ficticios = 15764; recomputo › m8_nd.filas[2].ficticios = 15764 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `1.22418` | cuerpo | …543.91 \| −27550.66 \| \| 200 \| 15 764 \| 1.22418 \| 55091.80 \| −275… | datos › m8.cuadratura.tabla[1].sin_contar_km2 = 1.224181623; recomputo › m8_homogeneo.forzado.faltan_km2 = 1.224181623 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `55091.80` | cuerpo | …27550.66 \| \| 200 \| 15 764 \| 1.22418 \| 55091.80 \| −27543.90 \| −2… | datos › m8.cuadratura.tabla[2].aic = 55091.79592; recomputo › m8_nd.filas[2].aic = 55091.79592 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `-27543.90` | cuerpo | …\| 200 \| 15 764 \| 1.22418 \| 55091.80 \| −27543.90 \| −27550.66 \| \… | datos › m8.cuadratura.tabla[2].logver_ppm = -27543.89796; recomputo › m8_nd.filas[2].logver_ppm = -27543.89796 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `-27550.66` | cuerpo | …64 \| 1.22418 \| 55091.80 \| −27543.90 \| −27550.66 \| \| 300 \| 35 49… | datos › m8.cuadratura.tabla[1].logver_exacta, m8.cuadratura.tabla[2].logver_exacta = [-27550.6626902924, -27550.6615108904]; recomputo › m8_nd.filas[1].logver_exacta, m8_nd.filas[2].logver_exacta = [-27550.6626902925, -27550.66151 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `300` | cuerpo | …55091.80 \| −27543.90 \| −27550.66 \| \| 300 \| 35 495 \| 0.38996 \| 5… | datos › m8.cuadratura.tabla[3].nd = 300 | CONTRASTADA · salida de R (JSON del capítulo) |
| `35495` | cuerpo | ….80 \| −27543.90 \| −27550.66 \| \| 300 \| 35 495 \| 0.38996 \| 55101.… | datos › m8.cuadratura.tabla[3].ficticios = 35495; recomputo › m8_nd.filas[3].ficticios = 35495 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `0.38996` | cuerpo | …543.90 \| −27550.66 \| \| 300 \| 35 495 \| 0.38996 \| 55101.00 \| −275… | datos › m8.cuadratura.tabla[3].sin_contar_km2 = 0.3899552221; recomputo › m8_nd.filas[3].sin_contar_km2 = 0.3899552221 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `55101.00` | cuerpo | …27550.66 \| \| 300 \| 35 495 \| 0.38996 \| 55101.00 \| −27548.50 \| −2… | datos › m8.cuadratura.tabla[3].aic = 55100.99538; recomputo › m8_nd.filas[3].aic = 55100.99538 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `-27548.50` | cuerpo | …\| 300 \| 35 495 \| 0.38996 \| 55101.00 \| −27548.50 \| −27550.64 \| :… | datos › m8.cuadratura.tabla[3].logver_ppm = -27548.49769; recomputo › m8_nd.filas[3].logver_ppm = -27548.49769 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `-27550.64` | cuerpo | …95 \| 0.38996 \| 55101.00 \| −27548.50 \| −27550.64 \| ::: info Dato C… | datos › m8.cuadratura.tabla[3].logver_exacta = -27550.6368; recomputo › m8_nd.filas[3].logver_exacta = -27550.6368 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `50` | cuerpo | …on (distancia al centro), entre = 50 y 300: el coeficiente se muev… | datos › m8.cuadratura.tabla[0].nd = 50 | CONTRASTADA · salida de R (JSON del capítulo) |
| `300` | cuerpo | …(distancia al centro), entre = 50 y 300: el coeficiente se mueve 0.12… | datos › m8.cuadratura.tabla[3].nd = 300 | CONTRASTADA · salida de R (JSON del capítulo) |
| `0.12895` | cuerpo | …= 50 y 300: el coeficiente se mueve 0.12895 errores estándar; el AIC, … | datos › m8.cuadratura.rango_pendiente_en_ee = 0.1289480457; recomputo › m8_nd.rango_pendiente_en_ee = 0.1289529956 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `9.2` | cuerpo | …eve 0.12895 errores estándar; el AIC, 9.2 puntos; la ℓ de , 4.59973; l… | datos › m8.cuadratura.rango_aic = 9.199466457; recomputo › m8_nd.rango_aic = 9.199466457 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `4.59973` | cuerpo | …ándar; el AIC, 9.2 puntos; la ℓ de , 4.59973; la ℓ con la integral bie… | datos › m8.cuadratura.rango_logver_ppm = 4.599733228; recomputo › m8_nd.rango_logver_ppm = 4.599733228 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `0.03` | cuerpo | …973; la ℓ con la integral bien hecha, 0.03. ::: ::: warn Criterio El A… | datos › m8.cuadratura.rango_logver_exacta = 0.0258914607; recomputo › m8_nd.rango_logver_exacta = 0.02589146071 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `100` | notas | …a de logaritmos en las sedes; con = 100 el modelo espera 2113.76 sede… | datos › m8.cuadratura.defecto_nd = 100 | CONTRASTADA · salida de R (JSON del capítulo) |
| `2113.76` | notas | …s sedes; con = 100 el modelo espera 2113.76 sedes sobre la ciudad, y h… | datos › m8.cuadratura.tabla[1].integral_exacta = 2113.756576; recomputo › m8_nd.filas[1].sedes_esperadas = 2113.756576 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `2107` | notas | …2113.76 sedes sobre la ciudad, y hay 2 107. Los cuatro ajustes son el … | datos › m5.capas.oferta.n = 2107; recomputo › urbana.n_urbana = 2107 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `0.03` | notas | …ien hecha su log-verosimilitud cambia 0.03 de un extremo a otro; la de… | datos › m8.cuadratura.rango_logver_exacta = 0.0258914607; recomputo › m8_nd.rango_logver_exacta = 0.02589146071 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `4.59973` | notas | …de un extremo a otro; la de cambia 4.59973, y todo lo que sobra es la … | datos › m8.cuadratura.rango_logver_ppm = 4.599733228; recomputo › m8_nd.rango_logver_ppm = 4.599733228 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `100` | notas | …ueda quieto y vuelve a subir. Con = 100 y 200 se pierde la misma área… | datos › m8.cuadratura.defecto_nd = 100 | CONTRASTADA · salida de R (JSON del capítulo) |
| `200` | notas | …uieto y vuelve a subir. Con = 100 y 200 se pierde la misma área, porq… | datos › m8.cuadratura.tabla[2].nd = 200 | CONTRASTADA · salida de R (JSON del capítulo) |
| `300` | notas | …xeles, y el AIC es casi el mismo; con 300 se pierde la que menos y su … | datos › m8.cuadratura.tabla[3].nd = 300 | CONTRASTADA · salida de R (JSON del capítulo) |

### Diapositiva 18 · La distancia gana al constante por 13.44572 puntos de AIC. ¿Y con la integral bien hecha?

| Cifra | Dónde | Contexto | Comprobación | Estado |
|---|---|---|---|---|
| `13.44572` | titulo | …La distancia gana al constante por 13.44572 puntos de AIC. ¿Y con la i… | datos › m8.comparacion.gana_distancia_ppm = 13.44571705; recomputo › m8_nd.gana_distancia_ppm = 13.44571705 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `13.4` | cuerpo | …Sigue ganando por 13.4 puntos: el AIC de es el AIC… | datos › m8.comparacion.gana_distancia_ppm = 13.44571705; recomputo › m8_nd.gana_distancia_ppm = 13.44571705 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `0.07` | cuerpo | …el AIC. Empatan: la diferencia cae a 0.07 puntos, y a favor del consta… | datos › m8.comparacion.gana_constante_exacta = 0.067434246; recomputo › m8_nd.gana_constante_exacta = 0.0674342461 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `13.4` | cuerpo | …del constante. Gana el constante por 13.4 puntos: la comparación estab… | datos › m8.comparacion.gana_distancia_ppm = 13.44571705; recomputo › m8_nd.gana_distancia_ppm = 13.44571705 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `0.07` | cuerpo | …atura. ::: respuesta : empatan, con 0.07 puntos a favor del constante… | datos › m8.comparacion.gana_constante_exacta = 0.067434246; recomputo › m8_nd.gana_constante_exacta = 0.0674342461 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `1.22418` | cuerpo | …, la cuadratura por defecto, que deja 1.22418 km² sin contar. Con la i… | datos › m8.cuadratura.tabla[1].sin_contar_km2 = 1.224181623; recomputo › m8_homogeneo.forzado.faltan_km2 = 1.224181623 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `0.07` | cuerpo | …en hecha en los dos, la diferencia es 0.07; forzando al constante por … | datos › m8.comparacion.gana_constante_exacta = 0.067434246; recomputo › m8_nd.gana_constante_exacta = 0.0674342461 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `0.51644` | cuerpo | …al constante por la misma cuadratura, 0.51644, también a favor del con… | datos › m8.comparacion.gana_constante_misma = 0.5164401208; recomputo › m8_nd.gana_constante_misma = 0.5164401208 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |

### Diapositiva 19 · Ajustar con ppm

| Cifra | Dónde | Contexto | Comprobación | Estado |
|---|---|---|---|---|
| `12` | notas | …Unos 12 minutos. Cuatro piezas: el aj… | minutos que se asignan a cada bloque de la sesión: decisión del docente, no un dato del capítulo | PARÁMETRO de diseño |

### Diapositiva 20 · `ppm(pu ~ x + y)` ajusta y devuelve tres coeficientes, pero ningún error estándar

| Cifra | Dónde | Contexto | Comprobación | Estado |
|---|---|---|---|---|
| `1.794e-10` | cuerpo | …n recíproco de la matriz de diseño es 1.794e-10; devuelve y es una mat… | datos › m9.crudo.cond_reciproco = 1.794e-10; recomputo › m9.crudo.cond = 1.794201778e-10 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `2.7e-20` | cuerpo | …dicionamiento del orden del cuadrado (2.7e-20), por debajo de lo que t… | recomputo › m9b_info.rcond_info_crudo = 2.728819881e-20 | VERIFICADA · re-ejecutada en R |
| `2.2e-16` | cuerpo | …e-20), por debajo de lo que tolera (2.2e-16): queda numéricamente sing… | recomputo › m9b_info.tolerancia_solve = 2.220446049e-16 | VERIFICADA · re-ejecutada en R |
| `9377` | cuerpo | …\|\|\| ::: info Dato Con x e y en EPSG:9377 el número de condición rec… | texto del capítulo: «EPSG:9377» | CONTRASTADA · texto del capítulo |
| `0x0` | notas | …vuelve NULL; devuelve una matriz de 0 × 0 sin quejarse, y un sobre ce… | recomputo › m9.crudo.dim_sqrt_diag_null = [0, 0] | VERIFICADA · re-ejecutada en R |
| `2.7e-20` | notas | …cuadrado del de la matriz de diseño (2.7e-20), menor que la tolerancia… | recomputo › m9b_info.rcond_info_crudo = 2.728819881e-20 | VERIFICADA · re-ejecutada en R |
| `2.2e-16` | notas | …7e-20), menor que la tolerancia de (2.2e-16, el épsilon de la máquina)… | recomputo › m9b_info.tolerancia_solve = 2.220446049e-16 | VERIFICADA · re-ejecutada en R |
| `1.794e-10` | notas | …lar aunque aceptaría una matriz con 1.794e-10. En la consola de R sale… | datos › m9.crudo.cond_reciproco = 1.794e-10; recomputo › m9.crudo.cond = 1.794201778e-10 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `117.038` | notas | …istancias y áreas. El intercepto sale 117.038, con toda la pinta de se… | datos › m9.crudo.coef[0] = 117.038021; recomputo › m9.crudo.coef[0] = 117.038021 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `4900000` | notas | …del lo reproduce con desplazado 4 900 000 unidades. Cotejo: , , , ,… | texto del capítulo: «4 900 000 unidades» | CONTRASTADA · texto del capítulo |

### Diapositiva 21 · Centrar y pasar a kilómetros: 6.567e+08 veces mejor condicionado, y el mismo AIC

| Cifra | Dónde | Contexto | Comprobación | Estado |
|---|---|---|---|---|
| `6.567e+08` | titulo | …Centrar y pasar a kilómetros: 6.567e+08 veces mejor condicionado, y e… | datos › m9.mejora_condicion = 656700000; recomputo › m9.mejora_condicion = 656692738.8 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `1.794e-10` | cuerpo | …ión recíproco de la matriz de diseño: 1.794e-10 con las coordenadas cr… | datos › m9.crudo.cond_reciproco = 1.794e-10; recomputo › m9.crudo.cond = 1.794201778e-10 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `0.1178` | cuerpo | …iseño: con las coordenadas crudas y 0.1178 centradas. El AIC es 55055.… | datos › m9.centrado.cond_reciproco = 0.1178; recomputo › m9.centrado.cond = 0.1178239279 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `55055.1` | cuerpo | …crudas y 0.1178 centradas. El AIC es 55055.1 en los dos. La última lín… | datos › m9.centrado.aic = 55055.05383; recomputo › m9.centrado.aic = 55055.05383 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `6.567e+08` | notas | …que usa el y la tabla siguiente. El 6.567e+08 sale del cociente de los… | datos › m9.mejora_condicion = 656700000; recomputo › m9.mejora_condicion = 656692738.8 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `6.566e+08` | notas | …redondear: con las redondeadas daría 6.566e+08. Python: el módulo mide… | 0.1178 / 1.794e-10 con las cifras redondeadas = 656633221.9 | VERIFICADA · aritmética sobre cifras verificadas |

### Diapositiva 22 · Habría evidencia del gradiente este-oeste, no del norte-sur: el condicional va a propósito

| Cifra | Dónde | Contexto | Comprobación | Estado |
|---|---|---|---|---|
| `-6.6091e-06` | cuerpo | …1978 \| 0.00306347 \| −1.70 \| \| \| \| −6.6091e-06 \| 5.4394e-06 \| −… | datos › m9.distancia.coef[1] = -6.6091e-06; recomputo › m9.distancia.coef[1] = -6.609111524e-06 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `5.4394e-06` | cuerpo | …347 \| −1.70 \| \| \| \| −6.6091e-06 \| 5.4394e-06 \| −1.22 \| Fuente:… | datos › m9.distancia.ee[1] = 5.4394e-06; recomputo › m9.distancia.ee[1] = 5.439447156e-06 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `-0.0242564` | cuerpo | …\| z \| \|---\|---\|---\|---\|---\| \| \| \| −0.0242564 \| 0.00503338 … | datos › m9.centrado.coef[1] = -0.0242564078; recomputo › m9.centrado.coef[1] = -0.02425640783 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `0.00503338` | cuerpo | …-\|---\|---\|---\| \| \| \| −0.0242564 \| 0.00503338 \| −4.82 \| \| \|… | datos › m9.centrado.ee[1] = 0.0050333841; recomputo › m9.centrado.ee[1] = 0.005033384126 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `-4.82` | cuerpo | …\| \| \| \| −0.0242564 \| 0.00503338 \| −4.82 \| \| \| \| −0.00521978 … | datos › m9.centrado.z[1] = -4.819105242; recomputo › m9.centrado.z[1] = -4.819105242 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `-0.00521978` | cuerpo | …42564 \| 0.00503338 \| −4.82 \| \| \| \| −0.00521978 \| 0.00306347 \| … | datos › m9.centrado.coef[2] = -0.0052197831; recomputo › m9.centrado.coef[2] = -0.00521978308 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `0.00306347` | cuerpo | …3338 \| −4.82 \| \| \| \| −0.00521978 \| 0.00306347 \| −1.70 \| \| \| … | datos › m9.centrado.ee[2] = 0.0030634652; recomputo › m9.centrado.ee[2] = 0.003063465234 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `-1.70` | cuerpo | …\| \| \| \| −0.00521978 \| 0.00306347 \| −1.70 \| \| \| \| \| \| −1.22… | datos › m9.centrado.z[2] = -1.703881938; recomputo › m9.centrado.z[2] = -1.703881938 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `-1.22` | cuerpo | ….00306347 \| −1.70 \| \| \| \| \| \| −1.22 \| Fuente: del capítulo (R… | datos › m9.distancia.z[1] = -1.215033685; recomputo › m9.distancia.z[1] = -1.215033685 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `1.96` | cuerpo | …ntre su error estándar; se lee contra 1.96. ::: ::: tip Interpretación… | datos › m11.tendencia.z_critico = 1.959963985 | CONTRASTADA · salida de R (JSON del capítulo) |
| `-4.82` | cuerpo | …rpretación (km al este) llega a z = −4.82; , a −1.70. La z de no enc… | datos › m9.centrado.z[1] = -4.819105242; recomputo › m9.centrado.z[1] = -4.819105242 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `-1.70` | cuerpo | …(km al este) llega a z = −4.82; , a −1.70. La z de no encuentra una r… | datos › m9.centrado.z[2] = -1.703881938; recomputo › m9.centrado.z[2] = -1.703881938 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `1.96` | notas | …r separado, no el uno con el otro. Un 1.96 es el valor con que se lee … | datos › m11.tendencia.z_critico = 1.959963985 | CONTRASTADA · salida de R (JSON del capítulo) |
| `-1.22` | notas | …distancia al centro de masa: su z de −1.22 no dice que la distancia no… | datos › m9.distancia.z[1] = -1.215033685; recomputo › m9.distancia.z[1] = -1.215033685 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `1.58` | notas | …ón log-lineal, y la curva ya mostró 1.58 veces en el bulto, con una fo… | datos › m7.bogota.curva.razon_bulto = 1.58183; recomputo › m7.bogota.bulto = 1.581834466 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `3` | notas | …integral bien hecha, un cuadrático (3 parámetros) mejora el AIC del… | recomputo › m9b_dcen.k_cuadratico = 3 | VERIFICADA · re-ejecutada en R |
| `56.4` | notas | …etros) mejora el AIC del constante en 56.4 puntos. El pone a prueba el… | recomputo › m9b_dcen.dif_aic = 56.35692468 | VERIFICADA · re-ejecutada en R |

### Diapositiva 23 · Para la misma distancia, `rhohat` da 36.1 veces y el `ppm`, z = −1.22. ¿Se contradicen?

| Cifra | Dónde | Contexto | Comprobación | Estado |
|---|---|---|---|---|
| `36.1` | titulo | …Para la misma distancia, da 36.1 veces y el , z = −1.22. ¿Se… | datos › m7.bogota.curva.razon = 36.0759; recomputo › m7.bogota.total = 36.07589681 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `-1.22` | titulo | …istancia, da 36.1 veces y el , z = −1.22. ¿Se contradicen?… | datos › m9.distancia.z[1] = -1.215033685; recomputo › m9.distancia.z[1] = -1.215033685 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `36` | cuerpo | …ue quedarse con su z. No: la razón de 36 es casi toda cola, y en el bu… | datos › m7.bogota.curva.razon = 36.0759; recomputo › m7.bogota.total = 36.07589681 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `1.58` | cuerpo | …es casi toda cola, y en el bulto vale 1.58. Sí: uno de los dos está ma… | datos › m7.bogota.curva.razon_bulto = 1.58183; recomputo › m7.bogota.bulto = 1.581834466 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `5` | cuerpo | …ción log-lineal Entre los percentiles 5 y 95 la curva varía 1.58 vece… | percentil inferior del bulto: parámetro de diseño del capítulo (entre los percentiles 5 y 95) | PARÁMETRO de diseño |
| `95` | cuerpo | …log-lineal Entre los percentiles 5 y 95 la curva varía 1.58 veces; la… | percentil superior del bulto: parámetro de diseño del capítulo (entre los percentiles 5 y 95) | PARÁMETRO de diseño |
| `1.58` | cuerpo | …los percentiles 5 y 95 la curva varía 1.58 veces; la cola infla el tit… | datos › m7.bogota.curva.razon_bulto = 1.58183; recomputo › m7.bogota.bulto = 1.581834466 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `22.8` | cuerpo | …1.58 veces; la cola infla el titular 22.8 veces. El supone una forma,… | datos › m7.bogota.curva.cola_infla = 22.8064; recomputo › m7.bogota.infla = 22.80636664 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |

### Diapositiva 24 · Diagnóstico del ajuste

| Cifra | Dónde | Contexto | Comprobación | Estado |
|---|---|---|---|---|
| `14` | notas | …Unos 14 minutos. Seis piezas: los tre… | minutos que se asignan a cada bloque de la sesión: decisión del docente, no un dato del capítulo | PARÁMETRO de diseño |
| `39` | notas | …a la envolvente del , el código con 39 simulaciones, la envolvente d… | nsim = 2 / nivel puntual − 1, con nivel puntual 2 / (nsim + 1) = 39 | VERIFICADA · aritmética sobre cifras verificadas |
| `999` | notas | …con 39 simulaciones, la envolvente de 999, lo que promete y lo que cum… | datos › m10.nsim = 999; recomputo › m10.nsim = 999 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |

### Diapositiva 25 · Tres cambios respecto a la envolvente del capítulo 4

| Cifra | Dónde | Contexto | Comprobación | Estado |
|---|---|---|---|---|
| `999` | cuerpo | …imula desde el modelo Cada una de las 999 simulaciones es una realizac… | datos › m10.nsim = 999; recomputo › m10.nsim = 999 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `999` | cuerpo | …s dos casi coinciden: la media de las 999 simulaciones queda a menos d… | datos › m10.nsim = 999; recomputo › m10.nsim = 999 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `100` | cuerpo | …ones queda a menos de 1 % de en los 100 radios que dibuja el simulado… | recomputo › m10.simulador.nodos = 100 | VERIFICADA · re-ejecutada en R |
| `0.64` | notas | …a justa. El capítulo dice «a menos de 0.64 %»; con las cifras sin redo… | texto del capítulo: «a menos de 0.64 %» | CONTRASTADA · texto del capítulo |
| `0.64499` | notas | …las cifras sin redondear el máximo es 0.64499 % con la semilla del cap… | datos › m10.mmean_vs_teorica_pct = 0.6449876748; recomputo › m10.mmean_vs_teorica_pct = 0.6449876748 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `0.82` | notas | …con la semilla del capítulo y llega a 0.82 % con otras, de modo que «a… | máximo de \|media − π r²\| / π r² (%) con las ocho semillas nuevas = 0.82 | VERIFICADA · aritmética sobre cifras verificadas |
| `999` | notas | …ación porque con la isotrópica serían 999 veces unos dos minutos ( ). … | datos › m10.nsim = 999; recomputo › m10.nsim = 999 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |

### Diapositiva 26 · La envolvente se simula desde el modelo; con 39 simulaciones el p mínimo es 0.025

| Cifra | Dónde | Contexto | Comprobación | Estado |
|---|---|---|---|---|
| `39` | titulo | …lvente se simula desde el modelo; con 39 simulaciones el p mínimo es 0… | nsim = 2 / nivel puntual − 1, con nivel puntual 2 / (nsim + 1) = 39 | VERIFICADA · aritmética sobre cifras verificadas |
| `0.025` | titulo | …o; con 39 simulaciones el p mínimo es 0.025… | recomputo › m10_e39.dclf = 0.025 \| recomputo › m10_e39.mad = 0.025 | VERIFICADA · re-ejecutada en R |
| `39` | cuerpo | …, spatstat). \|\|\| ::: info Dato Con 39 simulaciones el nivel puntual… | nsim = 2 / nivel puntual − 1, con nivel puntual 2 / (nsim + 1) = 39 | VERIFICADA · aritmética sobre cifras verificadas |
| `0.0500` | cuerpo | …modelo se salga en un radio dado) es 0.0500 y el patrón queda fuera en… | recomputo › m10_e39.nivel_puntual = 0.05 | VERIFICADA · re-ejecutada en R |
| `78.5156` | cuerpo | …0.0500 y el patrón queda fuera en el 78.5156 % de los radios. DCLF y M… | recomputo › m10_e39.pct_fuera = 78.515625 | VERIFICADA · re-ejecutada en R |
| `0.025` | cuerpo | …6 % de los radios. DCLF y MAD dan p = 0.025, el mínimo posible: 1/(39 … | recomputo › m10_e39.dclf = 0.025 \| recomputo › m10_e39.mad = 0.025 | VERIFICADA · re-ejecutada en R |
| `39` | cuerpo | …dan p = 0.025, el mínimo posible: 1/(39 + 1). ::: ::: tip Interpreta… | nsim = 2 / nivel puntual − 1, con nivel puntual 2 / (nsim + 1) = 39 | VERIFICADA · aritmética sobre cifras verificadas |
| `0.2` | cuerpo | …o afina la banda: le cambia el nivel, 0.2 % con 999. :::… | datos › m10.nivel_puntual_pct = 0.2; recomputo › m10.nivel_puntual_pct = 0.2 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `999` | cuerpo | …banda: le cambia el nivel, 0.2 % con 999. :::… | datos › m10.nsim = 999; recomputo › m10.nsim = 999 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `999` | notas | …l de Python, que lee la envolvente de 999 que el precálculo dejó en un… | datos › m10.nsim = 999; recomputo › m10.nsim = 999 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `39` | notas | …de «maximum absolute deviation». Con 39 simulaciones esto tarda unos… | nsim = 2 / nivel puntual − 1, con nivel puntual 2 / (nsim + 1) = 39 | VERIFICADA · aritmética sobre cifras verificadas |
| `999` | notas | …segundos; el capítulo publica una de 999, precalculada. guarda las c… | datos › m10.nsim = 999; recomputo › m10.nsim = 999 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `39` | notas | …tests globales reutilicen las mismas 39. Con 39, el p más pequeño pos… | nsim = 2 / nivel puntual − 1, con nivel puntual 2 / (nsim + 1) = 39 | VERIFICADA · aritmética sobre cifras verificadas |
| `39` | notas | …lobales reutilicen las mismas 39. Con 39, el p más pequeño posible es… | nsim = 2 / nivel puntual − 1, con nivel puntual 2 / (nsim + 1) = 39 | VERIFICADA · aritmética sobre cifras verificadas |
| `39` | notas | …on 39, el p más pequeño posible es 1/(39 + 1), y es justo el que sale:… | nsim = 2 / nivel puntual − 1, con nivel puntual 2 / (nsim + 1) = 39 | VERIFICADA · aritmética sobre cifras verificadas |

### Diapositiva 27 · El patrón se sale de la banda de su modelo en el 62 % de los radios, siempre por arriba

| Cifra | Dónde | Contexto | Comprobación | Estado |
|---|---|---|---|---|
| `62` | titulo | …e sale de la banda de su modelo en el 62 % de los radios, siempre por… | datos › m10.pct_r_fuera_de_banda = 62; recomputo › m10.pct_fuera = 62 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `999` | cuerpo | …dia de su modelo, con la banda de las 999 simulaciones Fuente: del… | datos › m10.nsim = 999; recomputo › m10.nsim = 999 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `62` | cuerpo | …y figura propia. \|\|\| ::: info Dato 62 de los 100 radios quedan sobr… | datos › m10.pct_r_fuera_de_banda = 62; recomputo › m10.pct_fuera = 62 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `100` | cuerpo | …ropia. \|\|\| ::: info Dato 62 de los 100 radios quedan sobre la banda… | datos › m8.cuadratura.defecto_nd = 100 | CONTRASTADA · salida de R (JSON del capítulo) |
| `58.68` | cuerpo | …e la banda y ninguno bajo ella: desde 58.68 hasta 3638.23 m; los 38 no… | datos › m10.primer_r_fuera_m = 58.68115733; recomputo › m10.primer_r_fuera_m = 58.68115733 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `3638.23` | cuerpo | …ninguno bajo ella: desde 58.68 hasta 3638.23 m; los 38 nodos restantes… | datos › m10.ultimo_r_fuera_m = 3638.231754; recomputo › m10.ultimo_r_fuera_m = 3638.231754 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `38` | cuerpo | …lla: desde 58.68 hasta 3638.23 m; los 38 nodos restantes, hasta 5868.1… | datos › m10.nodos_dentro_tras_el_tramo = 38; recomputo › m10.nodos_dentro_tras_el_tramo = 38 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `5868.12` | cuerpo | …8.23 m; los 38 nodos restantes, hasta 5868.12 m, quedan dentro. Son ci… | datos › m10.r_max_m = 5868.115733; recomputo › m10.r_max_m = 5868.115733 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `62` | cuerpo | …as de una semilla: con otras salen de 62 a 67 radios y un tramo que ll… | mínimo de radios fuera de 100 con nueve semillas = 62 | VERIFICADA · aritmética sobre cifras verificadas |
| `67` | cuerpo | …una semilla: con otras salen de 62 a 67 radios y un tramo que llega a… | máximo de radios fuera de 100 con nueve semillas = 67 | VERIFICADA · aritmética sobre cifras verificadas |
| `3.6` | cuerpo | …62 a 67 radios y un tramo que llega a 3.6–3.9 km. ::: ::: tip Interpre… | último radio fuera (km), mínimo con nueve semillas = 3.6 | VERIFICADA · aritmética sobre cifras verificadas |
| `3.9` | cuerpo | …67 radios y un tramo que llega a 3.6–3.9 km. ::: ::: tip Interpretaci… | último radio fuera (km), máximo con nueve semillas = 3.9 | VERIFICADA · aritmética sobre cifras verificadas |
| `2.2` | cuerpo | …e parejas por escala llega hasta unos 2.2 km: la g inhomogénea, que mi… | hasta dónde llega la primera racha de radios fuera de la banda de la g inhomogénea (km) = 2.2 | VERIFICADA · aritmética sobre cifras verificadas |
| `1.20` | cuerpo | …e mira cada escala por separado, vale 1.20 a 1 km y 1.06 a 2 km. La K … | recomputo › m10b_pcf.g_1000.g_obs = 1.201131082 | VERIFICADA · re-ejecutada en R |
| `1.06` | cuerpo | …cala por separado, vale 1.20 a 1 km y 1.06 a 2 km. La K acumula, y por… | recomputo › m10b_pcf.g_2000.g_obs = 1.059823252 | VERIFICADA · re-ejecutada en R |
| `3.6` | cuerpo | …la, y por eso la banda se cruza hasta 3.6–3.9 km. :::… | último radio fuera (km), mínimo con nueve semillas = 3.6 | VERIFICADA · aritmética sobre cifras verificadas |
| `3.9` | cuerpo | …y por eso la banda se cruza hasta 3.6–3.9 km. :::… | último radio fuera (km), máximo con nueve semillas = 3.9 | VERIFICADA · aritmética sobre cifras verificadas |
| `3638.23` | notas | …uera de la banda a escalas mayores, y 3638.23 m es donde la K vuelve a… | datos › m10.ultimo_r_fuera_m = 3638.231754; recomputo › m10.ultimo_r_fuera_m = 3638.231754 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `199` | notas | …(la g inhomogénea, medida aparte con 199 simulaciones, sale de su band… | recomputo › m10b_pcf.nsim = 199 | VERIFICADA · re-ejecutada en R |
| `2.2` | notas | …le de su banda sin interrupción hasta 2.2 km). El capítulo lee los dos… | hasta dónde llega la primera racha de radios fuera de la banda de la g inhomogénea (km) = 2.2 | VERIFICADA · aritmética sobre cifras verificadas |
| `3.8` | notas | …ocho semillas el tramo termina entre 3.8 y 3.9 km y la fracción de rad… | último radio fuera (km), mínimo con las ocho semillas nuevas = 3.8 | VERIFICADA · aritmética sobre cifras verificadas |
| `3.9` | notas | …semillas el tramo termina entre 3.8 y 3.9 km y la fracción de radios f… | último radio fuera (km), máximo con las ocho semillas nuevas = 3.9 | VERIFICADA · aritmética sobre cifras verificadas |
| `64` | notas | …m y la fracción de radios fuera va de 64 a 67 de los 100 radios. La fi… | mínimo de radios fuera de 100 con las ocho semillas nuevas = 64 | VERIFICADA · aritmética sobre cifras verificadas |
| `67` | notas | …a fracción de radios fuera va de 64 a 67 de los 100 radios. La figura… | máximo de radios fuera de 100 con las ocho semillas nuevas = 67 | VERIFICADA · aritmética sobre cifras verificadas |
| `100` | notas | …de radios fuera va de 64 a 67 de los 100 radios. La figura divide la K… | datos › m10.tasa_salida.nodos_r_simulador = 100 | CONTRASTADA · salida de R (JSON del capítulo) |
| `58.68` | notas | …un contraste hecho en cada radio. Los 58.68 m son el primer nodo no nu… | datos › m10.primer_r_fuera_m = 58.68115733; recomputo › m10.primer_r_fuera_m = 58.68115733 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `101` | notas | …primer nodo no nulo de la rejilla de 101 radios del simulador; en la r… | datos › m10.n_nodos = 101; recomputo › m10.n_nodos = 101 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `512` | notas | …simulador; en la rejilla nativa de (512 radios no nulos) la separació… | datos › m10.tasa_salida.nodos_r = 512; recomputo › m10.nativa.nodos = 512 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `11.46` | notas | …os no nulos) la separación empieza en 11.46 m, el primer radio. Son 10… | primer radio no nulo de la rejilla nativa: r máximo (5868.12 m) entre los 512 radios no nulos = 11.46116354 | VERIFICADA · aritmética sobre cifras verificadas |
| `100` | notas | …ieza en 11.46 m, el primer radio. Son 100 radios informativos porque e… | recomputo › m10.simulador.nodos = 100 | VERIFICADA · re-ejecutada en R |

### Diapositiva 28 · La banda promete un 0.2 % por radio, pero leída entera se cruza entre el 5 y el 8 %

| Cifra | Dónde | Contexto | Comprobación | Estado |
|---|---|---|---|---|
| `0.2` | titulo | …La banda promete un 0.2 % por radio, pero leída enter… | datos › m10.nivel_puntual_pct = 0.2; recomputo › m10.nivel_puntual_pct = 0.2 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `5` | titulo | …, pero leída entera se cruza entre el 5 y el 8 %… | mínimo de la tasa de salida de la banda entera con nueve semillas (5.31 %), hacia abajo = 5 | VERIFICADA · aritmética sobre cifras verificadas |
| `8` | titulo | …leída entera se cruza entre el 5 y el 8 %… | máximo de la tasa de salida de la banda entera con nueve semillas (7.81 %), hacia arriba = 8 | VERIFICADA · aritmética sobre cifras verificadas |
| `0.2` | cuerpo | …::: tarjetas ### Nivel puntual: 0.2 % Con 999 simulaciones y la b… | datos › m10.nivel_puntual_pct = 0.2; recomputo › m10.nivel_puntual_pct = 0.2 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `999` | cuerpo | …rjetas ### Nivel puntual: 0.2 % Con 999 simulaciones y la banda por d… | datos › m10.nsim = 999; recomputo › m10.nsim = 999 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `5` | cuerpo | …un radio dado**. ### La banda entera: 5–8 % Leída como curva, es **en… | mínimo de la tasa de salida de la banda entera con nueve semillas (5.31 %), hacia abajo = 5 | VERIFICADA · aritmética sobre cifras verificadas |
| `8` | cuerpo | …radio dado**. ### La banda entera: 5–8 % Leída como curva, es **en c… | máximo de la tasa de salida de la banda entera con nueve semillas (7.81 %), hacia arriba = 8 | VERIFICADA · aritmética sobre cifras verificadas |
| `999` | cuerpo | …va, es **en cualquier radio**: de las 999 curvas del modelo, entre 53 … | datos › m10.nsim = 999; recomputo › m10.nsim = 999 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `53` | cuerpo | …: de las 999 curvas del modelo, entre 53 y 78 (según la semilla) cruza… | mínimo de curvas que cruzan la banda de las otras, con nueve semillas = 53 | VERIFICADA · aritmética sobre cifras verificadas |
| `78` | cuerpo | …las 999 curvas del modelo, entre 53 y 78 (según la semilla) cruzan la… | máximo de curvas que cruzan la banda de las otras, con nueve semillas = 78 | VERIFICADA · aritmética sobre cifras verificadas |
| `30` | cuerpo | …a) cruzan la banda de las otras, unas 30 veces el nivel puntual. ### T… | mediana (32.0) de las veces que la banda entera supera el nivel puntual, con nueve semillas, a la decena = 30 | VERIFICADA · aritmética sobre cifras verificadas |
| `0.001` | cuerpo | …l nivel puntual. ### Test global: p = 0.001 El DCLF da p = 0.001, el m… | datos › m10.test_global.dclf_p = 0.001; recomputo › m10.dclf_p = 0.001 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `0.001` | cuerpo | …Test global: p = 0.001 El DCLF da p = 0.001, el mínimo que 999 simulac… | datos › m10.test_global.dclf_p = 0.001; recomputo › m10.dclf_p = 0.001 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `999` | cuerpo | …1 El DCLF da p = 0.001, el mínimo que 999 simulaciones permiten; el MA… | datos › m10.nsim = 999; recomputo › m10.nsim = 999 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `0.001` | cuerpo | …999 simulaciones permiten; el MAD, de 0.001 a 0.004 según la semilla. … | datos › m10.test_global.dclf_p = 0.001; recomputo › m10.dclf_p = 0.001 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `0.004` | cuerpo | …laciones permiten; el MAD, de 0.001 a 0.004 según la semilla. Ninguno … | máximo del p del MAD con nueve semillas = 0.004 | VERIFICADA · aritmética sobre cifras verificadas |
| `0.2` | cuerpo | …erio Lo que no se sostiene es leer el 0.2 % como la seguridad de la cu… | datos › m10.nivel_puntual_pct = 0.2; recomputo › m10.nivel_puntual_pct = 0.2 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `999` | notas | …sin simular nada más: cada una de las 999 curvas del propio modelo se … | datos › m10.nsim = 999; recomputo › m10.nsim = 999 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `512` | notas | …con la banda de las otras, sobre los 512 radios con que spatstat calcu… | datos › m10.tasa_salida.nodos_r = 512; recomputo › m10.nativa.nodos = 512 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `100` | notas | …es se encuentra una salida (sobre los 100 radios que dibuja el simulad… | recomputo › m10.simulador.nodos = 100 | VERIFICADA · re-ejecutada en R |
| `4.30430` | notas | …r, con la semilla del capítulo, es el 4.30430 %). Con la semilla del c… | recomputo › m10.simulador.pct = 4.304304304 | VERIFICADA · re-ejecutada en R |
| `77` | notas | …0 %). Con la semilla del capítulo son 77 curvas, el 7.70771 %, o 38.53… | datos › m10.tasa_salida.fuera = 77; recomputo › m10.nativa.fuera = 77 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `7.70771` | notas | …emilla del capítulo son 77 curvas, el 7.70771 %, o 38.53854 veces el n… | datos › m10.tasa_salida.pct = 7.707707708; recomputo › m10.nativa.pct = 7.707707708 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `38.53854` | notas | …pítulo son 77 curvas, el 7.70771 %, o 38.53854 veces el nivel puntual;… | datos › m10.tasa_salida.veces_el_nivel = 38.53853854; recomputo › m10.veces_el_nivel = 38.53853854 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `53` | notas | …puntual; con otras ocho semillas, de 53 a 78 curvas, del 5.3 al 7.8 %… | mínimo de curvas que cruzan la banda de las otras, con nueve semillas = 53 | VERIFICADA · aritmética sobre cifras verificadas |
| `78` | notas | …ual; con otras ocho semillas, de 53 a 78 curvas, del 5.3 al 7.8 %, de… | máximo de curvas que cruzan la banda de las otras, con nueve semillas = 78 | VERIFICADA · aritmética sobre cifras verificadas |
| `5.3` | notas | …ocho semillas, de 53 a 78 curvas, del 5.3 al 7.8 %, de 26.5 a 39 veces… | mínimo de la tasa de salida (%) con nueve semillas = 5.3 | VERIFICADA · aritmética sobre cifras verificadas |
| `7.8` | notas | …millas, de 53 a 78 curvas, del 5.3 al 7.8 %, de 26.5 a 39 veces: son c… | máximo de la tasa de salida (%) con nueve semillas = 7.8 | VERIFICADA · aritmética sobre cifras verificadas |
| `26.5` | notas | …53 a 78 curvas, del 5.3 al 7.8 %, de 26.5 a 39 veces: son cifras de Mo… | mínimo de las veces el nivel puntual con nueve semillas = 26.5 | VERIFICADA · aritmética sobre cifras verificadas |
| `39` | notas | …8 curvas, del 5.3 al 7.8 %, de 26.5 a 39 veces: son cifras de Monte Ca… | nsim = 2 / nivel puntual − 1, con nivel puntual 2 / (nsim + 1) = 39 | VERIFICADA · aritmética sobre cifras verificadas |
| `1959.86` | notas | …la peor desviación del patrón está en 1959.86 m, dentro del tramo; sim… | datos › m10.test_global.r_mad_observada_m = 1959.858966; recomputo › m10.r_mad_observada_m = 1959.858966 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `5650.35` | notas | …iones que la superan lo hacen pasados 5650.35 m, donde el abanico de K… | datos › m10.test_global.r_min_mad_superan_m = 5650.353626; recomputo › m10.r_min_mad_superan_m = 5650.353626 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |

### Diapositiva 29 · La K inhomogénea sale de la banda del modelo en el 62 % de los radios. ¿Qué se concluye?

| Cifra | Dónde | Contexto | Comprobación | Estado |
|---|---|---|---|---|
| `62` | titulo | …nea sale de la banda del modelo en el 62 % de los radios. ¿Qué se conc… | datos › m10.pct_r_fuera_de_banda = 62; recomputo › m10.pct_fuera = 62 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `999` | cuerpo | …banda es demasiado estrecha por usar 999 simulaciones. ::: respuesta… | datos › m10.nsim = 999; recomputo › m10.nsim = 999 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `40` | cuerpo | …que estén cerca unos de otros. : hay 40 sedes repetidas, pero quitarl… | datos › m11.duplicados.repetidos = 40 | CONTRASTADA · salida de R (JSON del capítulo) |
| `6.2` | cuerpo | …as mueve los parámetros como mucho un 6.2 %. : la K inhomogénea ya des… | datos › m11.duplicados.cambio_maximo_pct = 6.152204768 | CONTRASTADA · salida de R (JSON del capítulo) |
| `12` | cuerpo | …a; solo una curva muy flexible (grado 12, 91 parámetros) deja de recha… | recomputo › m10b_flex.12.grado = 12 | VERIFICADA · re-ejecutada en R |
| `91` | cuerpo | …olo una curva muy flexible (grado 12, 91 parámetros) deja de rechazar,… | recomputo › m10b_flex.12.k = 91 | VERIFICADA · re-ejecutada en R |
| `999` | cuerpo | …atrón no se separan. : al revés; con 999 el nivel puntual es 0.2 %, má… | datos › m10.nsim = 999; recomputo › m10.nsim = 999 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `0.2` | cuerpo | …al revés; con 999 el nivel puntual es 0.2 %, más exigente que el 5 % d… | datos › m10.nivel_puntual_pct = 0.2; recomputo › m10.nivel_puntual_pct = 0.2 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `5` | cuerpo | …puntual es 0.2 %, más exigente que el 5 % de una envolvente de 39. ::… | 100 × el nivel puntual de la envolvente de 39 (0.05) = 5 | VERIFICADA · aritmética sobre cifras verificadas |
| `39` | cuerpo | …gente que el 5 % de una envolvente de 39. ::: Fuente: del capítulo… | nsim = 2 / nivel puntual − 1, con nivel puntual 2 / (nsim + 1) = 39 | VERIFICADA · aritmética sobre cifras verificadas |
| `12` | notas | …) y una tendencia polinómica de grado 12, ningún test global rechaza;… | recomputo › m10b_flex.12.grado = 12 | VERIFICADA · re-ejecutada en R |
| `200` | notas | …echaza; pero esa curva llega a más de 200 sedes por km² y a casi cero … | datos › m8.cuadratura.tabla[2].nd = 200 | CONTRASTADA · salida de R (JSON del capítulo) |

### Diapositiva 30 · Un plano en x e y no explica que los colegios estén cerca unos de otros

| Cifra | Dónde | Contexto | Comprobación | Estado |
|---|---|---|---|---|
| `29.8` | cuerpo | …. Lo medido apunta en ese sentido: el 29.8 % de las sedes tiene otra a… | recomputo › m11b_dups.pct_vecino_menos_100m = 29.80541054 | VERIFICADA · re-ejecutada en R |
| `100` | cuerpo | …% de las sedes tiene otra a menos de 100 m; bajo el modelo con tendenc… | distancia de 100 m con que se mide el vecino más próximo (decisión de la medición) | PARÁMETRO de diseño |
| `16.3` | cuerpo | …0 m; bajo el modelo con tendencia, el 16.3 %. Y el veredicto alcanza h… | recomputo › m11b_dups.pct_vecino_menos_100m_modelo = 16.34208656 | VERIFICADA · re-ejecutada en R |
| `2107` | cuerpo | …a de tumbar. Con las sedes en grupos, 2 107 sedes no son 2 107 observa… | datos › m5.capas.oferta.n = 2107; recomputo › urbana.n_urbana = 2107 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `2107` | cuerpo | …s sedes en grupos, 2 107 sedes no son 2 107 observaciones independient… | datos › m5.capas.oferta.n = 2107; recomputo › urbana.n_urbana = 2107 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `3` | notas | …robó es un plano log-lineal en x e y (3 parámetros); con una tendenci… | recomputo › m10b_flex.1.k = 3 | VERIFICADA · re-ejecutada en R |
| `12` | notas | …con una tendencia polinómica de grado 12 (91 parámetros) ningún test g… | recomputo › m10b_flex.12.grado = 12 | VERIFICADA · re-ejecutada en R |
| `91` | notas | …una tendencia polinómica de grado 12 (91 parámetros) ningún test globa… | recomputo › m10b_flex.12.k = 91 | VERIFICADA · re-ejecutada en R |
| `79` | notas | …con datos de predios. Lo medido: hay 79 sedes que comparten sitio exa… | recomputo › m11b_dups.sedes_en_esos_sitios = 79 | VERIFICADA · re-ejecutada en R |
| `39` | notas | …sedes que comparten sitio exacto (en 39 sitios), y el 29.8 % de las s… | nsim = 2 / nivel puntual − 1, con nivel puntual 2 / (nsim + 1) = 39 | VERIFICADA · aritmética sobre cifras verificadas |
| `29.8` | notas | …ten sitio exacto (en 39 sitios), y el 29.8 % de las sedes tiene otra a… | recomputo › m11b_dups.pct_vecino_menos_100m = 29.80541054 | VERIFICADA · re-ejecutada en R |
| `100` | notas | …% de las sedes tiene otra a menos de 100 m, contra 16.3 % (sd 1.2) en… | distancia de 100 m con que se mide el vecino más próximo (decisión de la medición) | PARÁMETRO de diseño |
| `16.3` | notas | …s tiene otra a menos de 100 m, contra 16.3 % (sd 1.2) en 99 patrones s… | recomputo › m11b_dups.pct_vecino_menos_100m_modelo = 16.34208656 | VERIFICADA · re-ejecutada en R |
| `1.2` | notas | …a a menos de 100 m, contra 16.3 % (sd 1.2) en 99 patrones simulados de… | recomputo › m11b_dups.pct_vecino_menos_100m_modelo_sd = 1.163633301 | VERIFICADA · re-ejecutada en R |
| `99` | notas | …s de 100 m, contra 16.3 % (sd 1.2) en 99 patrones simulados del modelo… | recomputo › m11b_dups.simulaciones_modelo = 99 | VERIFICADA · re-ejecutada en R |

### Diapositiva 31 · Conglomerado y autoexcitación

| Cifra | Dónde | Contexto | Comprobación | Estado |
|---|---|---|---|---|
| `17` | notas | …Unos 17 minutos. Ocho piezas: tres fa… | minutos que se asignan a cada bloque de la sesión: decisión del docente, no un dato del capítulo | PARÁMETRO de diseño |

### Diapositiva 32 · Tres familias de conglomerado tardan unos 127 s: lo que se paga es la estimación de K

| Cifra | Dónde | Contexto | Comprobación | Estado |
|---|---|---|---|---|
| `127` | titulo | …familias de conglomerado tardan unos 127 s: lo que se paga es la estim… | promedio de los tres tiempos con K isotrópica del capítulo (126.5, 126.7 y 127.1 s) = 126.7703333 | VERIFICADA · aritmética sobre cifras verificadas |
| `932` | cuerpo | …--\|---\| \| Thomas \| hijos gaussianos \| 932 → 1320 m \| 126.5 / 0.4… | datos › m11.ajustes[0].parametros.scale = 932.133891; recomputo › m11_Thomas.iso.parametros.scale = 932.133891 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `1320` | cuerpo | …\| \| Thomas \| hijos gaussianos \| 932 → 1320 m \| 126.5 / 0.47 \| \|… | datos › m11.ajustes[1].parametros.scale = 1319.703255; recomputo › m11_Thomas.translate.parametros.scale = 1319.703255 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `126.5` | cuerpo | …s \| hijos gaussianos \| 932 → 1320 m \| 126.5 / 0.47 \| \| Matérn \| … | datos › m11.ajustes[0].segundos = 126.538 \| recomputo › m11_Thomas.iso.segundos = 128.84 (tolerancia ±5) | CONTRASTADA · salida de R (JSON del capítulo) |
| `0.47` | cuerpo | …s gaussianos \| 932 → 1320 m \| 126.5 / 0.47 \| \| Matérn \| hijos en … | datos › m11.ajustes[1].segundos = 0.473 \| recomputo › m11_Thomas.translate.segundos = 0.482 (tolerancia ±0.5) | CONTRASTADA · salida de R (JSON del capítulo) |
| `1782` | cuerpo | …0.47 \| \| Matérn \| hijos en un disco \| 1782 → 2522 m \| 126.7 / 0.4… | datos › m11.ajustes[2].parametros.scale = 1781.943778; recomputo › m11_MatClust.iso.parametros.scale = 1781.943778 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `2522` | cuerpo | …\| Matérn \| hijos en un disco \| 1782 → 2522 m \| 126.7 / 0.43 \| \| … | datos › m11.ajustes[3].parametros.scale = 2522.165511; recomputo › m11_MatClust.translate.parametros.scale = 2522.165511 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `126.7` | cuerpo | …\| hijos en un disco \| 1782 → 2522 m \| 126.7 / 0.43 \| \| Cox log-ga… | datos › m11.ajustes[2].segundos = 126.695 \| recomputo › m11_MatClust.iso.segundos = 128.07 (tolerancia ±5) | CONTRASTADA · salida de R (JSON del capítulo) |
| `0.43` | cuerpo | …en un disco \| 1782 → 2522 m \| 126.7 / 0.43 \| \| Cox log-gaussiano \… | datos › m11.ajustes[3].segundos = 0.427 \| recomputo › m11_MatClust.translate.segundos = 0.472 (tolerancia ±0.5) | CONTRASTADA · salida de R (JSON del capítulo) |
| `1296` | cuerpo | …og-gaussiano \| intensidad aleatoria \| 1296 → 1927 m \| 127.1 / 0.88 … | datos › m11.ajustes[4].parametros.scale = 1296.044276; recomputo › m11_LGCP.iso.parametros.scale = 1296.044276 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `1927` | cuerpo | …siano \| intensidad aleatoria \| 1296 → 1927 m \| 127.1 / 0.88 \| ::: … | datos › m11.ajustes[5].parametros.scale = 1926.939487; recomputo › m11_LGCP.translate.parametros.scale = 1926.939487 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `127.1` | cuerpo | …ntensidad aleatoria \| 1296 → 1927 m \| 127.1 / 0.88 \| ::: info Dato … | datos › m11.ajustes[4].segundos = 127.078 \| recomputo › m11_LGCP.iso.segundos = 129.09 (tolerancia ±5) | CONTRASTADA · salida de R (JSON del capítulo) |
| `0.88` | cuerpo | …d aleatoria \| 1296 → 1927 m \| 127.1 / 0.88 \| ::: info Dato ajusta p… | datos › m11.ajustes[5].segundos = 0.88 \| recomputo › m11_LGCP.translate.segundos = 0.962 (tolerancia ±0.5) | CONTRASTADA · salida de R (JSON del capítulo) |
| `127` | cuerpo | …trópica. Con la de traslación baja de 127 s a 0.47 s: más de 200 veces… | promedio de los tres tiempos con K isotrópica del capítulo (126.5, 126.7 y 127.1 s) = 126.7703333 | VERIFICADA · aritmética sobre cifras verificadas |
| `0.47` | cuerpo | …Con la de traslación baja de 127 s a 0.47 s: más de 200 veces más rápi… | datos › m11.ajustes[1].segundos = 0.473 \| recomputo › m11_Thomas.translate.segundos = 0.482 (tolerancia ±0.5) | CONTRASTADA · salida de R (JSON del capítulo) |
| `200` | cuerpo | …lación baja de 127 s a 0.47 s: más de 200 veces más rápido. ::: ::: ti… | datos › m8.cuadratura.tabla[2].nd = 200 | CONTRASTADA · salida de R (JSON del capítulo) |
| `555` | notas | …, la que el capítulo dice que costaba 555 veces la alternativa (una me… | cap4_datos.json › m10.coste.veces_isotropica_sobre_traslacion = 555 | CONTRASTADA · salida de R (JSON del capítulo) |
| `267.52220` | notas | …aslación, una fracción de segundo; el 267.52220 del capítulo sale de l… | datos › m11.divergencia[0].veces_mas_rapido = 267.5221987 \| cociente de los dos tiempos recalculados = 267.31 (tolerancia ±5) | CONTRASTADA · salida de R (JSON del capítulo) |
| `200` | notas | …y por eso la diapositiva dice «más de 200 veces». Las escalas no son e… | datos › m8.cuadratura.tabla[2].nd = 200 | CONTRASTADA · salida de R (JSON del capítulo) |
| `129` | notas | …a máquina salen del mismo orden (unos 129 s y menos de un segundo). Co… | segundos del ajuste de Thomas con K isotrópica en esta máquina (128.8) = 128.844 | VERIFICADA · aritmética sobre cifras verificadas |

### Diapositiva 33 · Con otra estimación de K, μ pasa de 27.1 a 52.3 sedes

| Cifra | Dónde | Contexto | Comprobación | Estado |
|---|---|---|---|---|
| `27.1` | titulo | …Con otra estimación de K, μ pasa de 27.1 a 52.3 sedes… | datos › m11.ajustes[0].mu = 27.09650952; recomputo › m11_Thomas.iso.mu = 27.09650952 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `52.3` | titulo | …tra estimación de K, μ pasa de 27.1 a 52.3 sedes… | datos › m11.ajustes[1].mu = 52.34765759; recomputo › m11_Thomas.translate.mu = 52.34765759 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `27.1` | cuerpo | …::: info Dato Con K isotrópica: μ = 27.1 y escala 932 m; con K de tras… | datos › m11.ajustes[0].mu = 27.09650952; recomputo › m11_Thomas.iso.mu = 27.09650952 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `932` | cuerpo | …o Con K isotrópica: μ = 27.1 y escala 932 m; con K de traslación: 52.3… | datos › m11.ajustes[0].parametros.scale = 932.133891; recomputo › m11_Thomas.iso.parametros.scale = 932.133891 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `52.3` | cuerpo | …y escala 932 m; con K de traslación: 52.3 y 1320 m. κ baja 48.2 %, la … | datos › m11.ajustes[1].mu = 52.34765759; recomputo › m11_Thomas.translate.mu = 52.34765759 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `1320` | cuerpo | …la 932 m; con K de traslación: 52.3 y 1320 m. κ baja 48.2 %, la escala… | datos › m11.ajustes[1].parametros.scale = 1319.703255; recomputo › m11_Thomas.translate.parametros.scale = 1319.703255 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `48.2` | cuerpo | …de traslación: 52.3 y 1320 m. κ baja 48.2 %, la escala sube 41.6 % y μ… | datos › m11.divergencia[0].parametros.kappa = 48.24478178; 100 × (1 − κ de traslación / κ isotrópica) = 48.23739826 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `41.6` | cuerpo | …1320 m. κ baja 48.2 %, la escala sube 41.6 % y μ, 93.2 %. De Thomas a … | datos › m11.divergencia[0].parametros.scale = 41.57872247; 100 × (escala de traslación / escala isotrópica − 1) = 41.57872247 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `93.2` | cuerpo | …ja 48.2 %, la escala sube 41.6 % y μ, 93.2 %. De Thomas a Matérn, κ y … | datos › m11.divergencia[0].mu_pct = 93.189671; 100 × (μ de traslación / μ isotrópica − 1) = 93.189671 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `0.13` | cuerpo | …Thomas a Matérn, κ y μ se mueven solo 0.13 % (isotrópica) y 0.29 % (tr… | cambio relativo de κ de Thomas a Matérn con K isotrópica (%) = 0.1325036423 \| cambio relativo de μ de Thomas a Matérn con K isotrópica (%) = 0.1326794474 | VERIFICADA · aritmética sobre cifras verificadas |
| `0.29` | cuerpo | …se mueven solo 0.13 % (isotrópica) y 0.29 % (traslación). :::… | cambio relativo de κ de Thomas a Matérn con K de traslación (%) = 0.2923554266 \| cambio relativo de μ de Thomas a Matérn con K de traslación (%) = 0.2932126497 | VERIFICADA · aritmética sobre cifras verificadas |
| `0.13` | notas | …y de μ: de Thomas a Matérn se mueven 0.13 % y 0.29 %, y de la K isotró… | cambio relativo de κ de Thomas a Matérn con K isotrópica (%) = 0.1325036423 \| cambio relativo de μ de Thomas a Matérn con K isotrópica (%) = 0.1326794474 | VERIFICADA · aritmética sobre cifras verificadas |
| `0.29` | notas | …de Thomas a Matérn se mueven 0.13 % y 0.29 %, y de la K isotrópica a l… | cambio relativo de κ de Thomas a Matérn con K de traslación (%) = 0.2923554266 \| cambio relativo de μ de Thomas a Matérn con K de traslación (%) = 0.2932126497 | VERIFICADA · aritmética sobre cifras verificadas |
| `48.2` | notas | …e la K isotrópica a la de traslación, 48.2 % y 93.2 %. La escala no se… | datos › m11.divergencia[0].parametros.kappa = 48.24478178; 100 × (1 − κ de traslación / κ isotrópica) = 48.23739826 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `93.2` | notas | …otrópica a la de traslación, 48.2 % y 93.2 %. La escala no se compara … | datos › m11.divergencia[0].mu_pct = 93.189671; 100 × (μ de traslación / μ isotrópica − 1) = 93.189671 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `5.7121` | notas | …n la cuadratura forzada ( ): κ·μ vale 5.7121 sedes por km², no 5.6932;… | κ · μ (sedes por km²) de kppm con K isotrópica: el λ̂ del ppm forzado = 5.712107068 | VERIFICADA · aritmética sobre cifras verificadas |
| `5.6932` | notas | …): κ·μ vale 5.7121 sedes por km², no 5.6932; con n entre el área sería… | datos › m8.homogeneo.lambda_km2 = 5.693212583; recomputo › m8_homogeneo.lambda_km2 = 5.693212582 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `27.0` | notas | …no 5.6932; con n entre el área serían 27.0 y 52.2. En este material la… | μ con n / \|W\| en vez del λ̂ forzado: (n / \|W\|) / κ, K isotrópica = 27.00687979 | VERIFICADA · aritmética sobre cifras verificadas |
| `52.2` | notas | …32; con n entre el área serían 27.0 y 52.2. En este material la correc… | μ con n / \|W\| en vez del λ̂ forzado: (n / \|W\|) / κ, K de traslación = 52.17450221 | VERIFICADA · aritmética sobre cifras verificadas |

### Diapositiva 34 · No es una rareza de la ventana de 22 piezas: con `redwood`, μ también pasa de 2.63 a 3.27

| Cifra | Dónde | Contexto | Comprobación | Estado |
|---|---|---|---|---|
| `22` | titulo | …No es una rareza de la ventana de 22 piezas: con , μ también pasa… | recomputo › m11_ventana.piezas = 22 | VERIFICADA · re-ejecutada en R |
| `2.63` | titulo | …e 22 piezas: con , μ también pasa de 2.63 a 3.27… | recomputo › m11_redwood.iso.mu = 2.632856432 \| texto del capítulo: «μ = 2.63 contra 3.27» | VERIFICADA · re-ejecutada en R |
| `3.27` | titulo | …ezas: con , μ también pasa de 2.63 a 3.27… | recomputo › m11_redwood.translate.mu = 3.265142009 \| texto del capítulo: «μ = 2.63 contra 3.27» | VERIFICADA · re-ejecutada en R |
| `62` | cuerpo | …**De dónde sale:** (spatstat.data): 62 plántulas y árboles jóvenes d… | recomputo › m11_redwood.n = 62 | VERIFICADA · re-ejecutada en R |
| `1975` | cuerpo | …venes de sequoia gigante, de Strauss (1975), subregión de Ripley (1977… | ayuda de spatstat.data (recomputo › ayuda_b.redwood): «Strauss (1975)» | REFERENCIA · ficha de ayuda del paquete |
| `1977` | cuerpo | …Strauss (1975), subregión de Ripley (1977) reescalada al cuadrado unid… | ayuda de spatstat.data (recomputo › ayuda_b.redwood): «Ripley (1977)» | REFERENCIA · ficha de ayuda del paquete |
| `22` | cuerpo | …sa en un cuadrado, no es culpa de las 22 piezas de la ventana urbana.… | recomputo › m11_ventana.piezas = 22 | VERIFICADA · re-ejecutada en R |
| `2.63` | cuerpo | …ana urbana. ::: ::: info Dato μ vale 2.63 con la K isotrópica y 3.27 c… | recomputo › m11_redwood.iso.mu = 2.632856432 \| texto del capítulo: «μ = 2.63 contra 3.27» | VERIFICADA · re-ejecutada en R |
| `3.27` | cuerpo | …ato μ vale 2.63 con la K isotrópica y 3.27 con la de traslación: un 24… | recomputo › m11_redwood.translate.mu = 3.265142009 \| texto del capítulo: «μ = 2.63 contra 3.27» | VERIFICADA · re-ejecutada en R |
| `24.0` | cuerpo | …ópica y 3.27 con la de traslación: un 24.0 % más. :::… | 100 × (μ de traslación / μ isotrópica − 1) en redwood = 24.01519388 \| texto del capítulo: «un 24.0 %» | VERIFICADA · aritmética sobre cifras verificadas |
| `22` | notas | …on. La ventana urbana de Bogotá tiene 22 piezas (es un multipolígono),… | recomputo › m11_ventana.piezas = 22 | VERIFICADA · re-ejecutada en R |

### Diapositiva 35 · Con `redwood`, `kppm` da μ = 2.63 con una K y 3.27 con la otra. ¿Cuál es el correcto?

| Cifra | Dónde | Contexto | Comprobación | Estado |
|---|---|---|---|---|
| `2.63` | titulo | …Con , da μ = 2.63 con una K y 3.27 con la otra.… | recomputo › m11_redwood.iso.mu = 2.632856432 \| texto del capítulo: «μ = 2.63 contra 3.27» | VERIFICADA · re-ejecutada en R |
| `3.27` | titulo | …Con , da μ = 2.63 con una K y 3.27 con la otra. ¿Cuál es el corr… | recomputo › m11_redwood.translate.mu = 3.265142009 \| texto del capítulo: «μ = 2.63 contra 3.27» | VERIFICADA · re-ejecutada en R |

### Diapositiva 36 · Dos conglomerados distintos dan casi la misma K, y los duplicados no son la causa

| Cifra | Dónde | Contexto | Comprobación | Estado |
|---|---|---|---|---|
| `0.6` | cuerpo | …parámetros de cada corrección difiere 0.6 % a 500 m, 0.9 % a 1000 m y … | diferencia relativa de la K de Thomas con los dos juegos de parámetros a 500 m (forma cerrada) = 0.5561566474 | VERIFICADA · aritmética sobre cifras verificadas |
| `500` | cuerpo | …os de cada corrección difiere 0.6 % a 500 m, 0.9 % a 1000 m y 4.8 % a … | texto del capítulo: «(500.0, 1000.0, 2000.0)» | CONTRASTADA · texto del capítulo |
| `0.9` | cuerpo | …ada corrección difiere 0.6 % a 500 m, 0.9 % a 1000 m y 4.8 % a 2000 m.… | diferencia relativa de la K de Thomas con los dos juegos de parámetros a 1000 m (forma cerrada) = 0.909160134 | VERIFICADA · aritmética sobre cifras verificadas |
| `1000` | cuerpo | …ección difiere 0.6 % a 500 m, 0.9 % a 1000 m y 4.8 % a 2000 m. ::: Fue… | texto del capítulo: «(500.0, 1000.0, 2000.0)» | CONTRASTADA · texto del capítulo |
| `4.8` | cuerpo | …fiere 0.6 % a 500 m, 0.9 % a 1000 m y 4.8 % a 2000 m. ::: Fuente: d… | diferencia relativa de la K de Thomas con los dos juegos de parámetros a 2000 m (forma cerrada) = 4.808787188 | VERIFICADA · aritmética sobre cifras verificadas |
| `2000` | cuerpo | …6 % a 500 m, 0.9 % a 1000 m y 4.8 % a 2000 m. ::: Fuente: del capítu… | texto del capítulo: «(500.0, 1000.0, 2000.0)» | CONTRASTADA · texto del capítulo |
| `0.183` | cuerpo | …y σ se compensan: κσ² es casi igual (0.183 y 0.190), y por eso las dos… | κ σ² de Thomas con K isotrópica = 0.1831637752 | VERIFICADA · aritmética sobre cifras verificadas |
| `0.190` | cuerpo | …compensan: κσ² es casi igual (0.183 y 0.190), y por eso las dos K coin… | κ σ² de Thomas con K de traslación = 0.1900429056 | VERIFICADA · aritmética sobre cifras verificadas |
| `5.5` | cuerpo | …eros grandes: una diferencia de hasta 5.5 % entre las dos K empíricas … | recomputo › m11b_kemp.dif_max_pct = 5.54373963 | VERIFICADA · re-ejecutada en R |
| `1.93` | cuerpo | …K empíricas es casi el doble en 1/κ (×1.93). ::: ::: info Dato La hipó… | κ isotrópica / κ de traslación (= 1/κ de traslación entre 1/κ isotrópica) = 1.93189671 | VERIFICADA · aritmética sobre cifras verificadas |
| `40` | cuerpo | …plicados se midió y es falsa: sin las 40 sedes repetidas, la escala pa… | datos › m11.duplicados.repetidos = 40 | CONTRASTADA · salida de R (JSON del capítulo) |
| `1320` | cuerpo | …40 sedes repetidas, la escala pasa de 1320 a 1373 m (4.0 %); el cambio… | datos › m11.ajustes[1].parametros.scale = 1319.703255; recomputo › m11_Thomas.translate.parametros.scale = 1319.703255 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `1373` | cuerpo | …s repetidas, la escala pasa de 1320 a 1373 m (4.0 %); el cambio máximo… | datos › m11.duplicados.efecto[0].sin_duplicados.scale = 1372.827634; recomputo › m11_Thomas.sin_duplicados.parametros.scale = 1372.827634 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `4.0` | cuerpo | …das, la escala pasa de 1320 a 1373 m (4.0 %); el cambio máximo, en tod… | datos › m11.duplicados.efecto[0].cambio_pct.scale = 4.025479147; 100 × (escala sin duplicados / escala con duplicados − 1), Thomas con K de traslación = 4.025479147 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `6.2` | cuerpo | …o máximo, en todos los parámetros, es 6.2 %. :::… | datos › m11.duplicados.cambio_maximo_pct = 6.152204768 | CONTRASTADA · salida de R (JSON del capítulo) |
| `932` | notas | …lación ya sube más de la mitad en σ = 932 m: cada K empírica tiene su … | datos › m11.ajustes[0].parametros.scale = 932.133891; recomputo › m11_Thomas.iso.parametros.scale = 932.133891 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `4` | notas | …forma cerrada: π r² más (1 − exp(−r²/(4 σ²)))/κ. A r corto el exceso… | constante de la forma cerrada de la K de Thomas: π r² + (1 − exp(−r²/(4 σ²)))/κ | PARÁMETRO de diseño |
| `4` | notas | …σ²)))/κ. A r corto el exceso vale r²/(4 κ σ²) y solo fija el producto… | constante de la forma cerrada de la K de Thomas: π r² + (1 − exp(−r²/(4 σ²)))/κ | PARÁMETRO de diseño |
| `0.183` | notas | …o κσ², casi igual en los dos ajustes (0.183 y 0.190): por eso las dos … | κ σ² de Thomas con K isotrópica = 0.1831637752 | VERIFICADA · aritmética sobre cifras verificadas |
| `0.190` | notas | …asi igual en los dos ajustes (0.183 y 0.190): por eso las dos K coinci… | κ σ² de Thomas con K de traslación = 0.1900429056 | VERIFICADA · aritmética sobre cifras verificadas |
| `5.5` | notas | …r debajo de la de traslación hasta un 5.5 % (a unos 2 km), una diferen… | recomputo › m11b_kemp.dif_max_pct = 5.54373963 | VERIFICADA · re-ejecutada en R |
| `1.93` | notas | …exceso es casi el doble: 1/κ cambia ×1.93. La hipótesis de que los dup… | κ isotrópica / κ de traslación (= 1/κ de traslación entre 1/κ isotrópica) = 1.93189671 | VERIFICADA · aritmética sobre cifras verificadas |
| `3` | notas | …ste se midió, y es falsa. La decisión 3 del conservó las 40 sedes r… | texto del capítulo: «decisión 3 de aquel capítulo» | CONTRASTADA · texto del capítulo |
| `40` | notas | …lsa. La decisión 3 del conservó las 40 sedes repetidas (en 39 sitios… | datos › m11.duplicados.repetidos = 40 | CONTRASTADA · salida de R (JSON del capítulo) |
| `39` | notas | …conservó las 40 sedes repetidas (en 39 sitios); este capítulo ajusta… | nsim = 2 / nivel puntual − 1, con nivel puntual 2 / (nsim + 1) = 39 | VERIFICADA · aritmética sobre cifras verificadas |

### Diapositiva 37 · Con conglomerados, el error estándar se multiplica por 3.96 a 5.32 y la z no pasa de 1.22

| Cifra | Dónde | Contexto | Comprobación | Estado |
|---|---|---|---|---|
| `3.96` | titulo | …, el error estándar se multiplica por 3.96 a 5.32 y la z no pasa de 1.… | datos › m11.tendencia.ajustes[0].inflacion[0] = 3.961772345; recomputo › m11_Thomas.tendencia.iso.inflacion[1] = 3.961772345 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `5.32` | titulo | …ror estándar se multiplica por 3.96 a 5.32 y la z no pasa de 1.22… | datos › m11.tendencia.ajustes[5].inflacion[0] = 5.317884318; recomputo › m11_LGCP.tendencia.translate.inflacion[1] = 5.317884318 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `1.22` | titulo | …ica por 3.96 a 5.32 y la z no pasa de 1.22… | datos › m11.tendencia.z_xc_abs_max = 1.216401353; máximo de \|z\| del coeficiente de xc en los seis ajustes = 1.216401353 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `0.00503338` | cuerpo | …n \| \|---\|---\|---\|---\| \| Poisson ( ) \| 0.00503338 \| −4.82 \| —… | datos › m9.centrado.ee[1] = 0.0050333841; recomputo › m9.centrado.ee[1] = 0.005033384126 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `-4.82` | cuerpo | …---\|---\| \| Poisson ( ) \| 0.00503338 \| −4.82 \| — \| \| Thomas, K … | datos › m9.centrado.z[1] = -4.819105242; recomputo › m9.centrado.z[1] = -4.819105242 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `0.0199411` | cuerpo | …−4.82 \| — \| \| Thomas, K isotrópica \| 0.0199411 \| −1.22 \| 3.96 \|… | datos › m11.tendencia.ajustes[0].ee[0] = 0.019941122; recomputo › m11_Thomas.tendencia.iso.ee[1] = 0.01994112203 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `-1.22` | cuerpo | …\| Thomas, K isotrópica \| 0.0199411 \| −1.22 \| 3.96 \| \| Thomas, K … | datos › m11.tendencia.ajustes[0].z[0] = -1.216401353; recomputo › m11_Thomas.tendencia.iso.z[1] = -1.216401353 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `3.96` | cuerpo | …s, K isotrópica \| 0.0199411 \| −1.22 \| 3.96 \| \| Thomas, K de trasl… | datos › m11.tendencia.ajustes[0].inflacion[0] = 3.961772345; recomputo › m11_Thomas.tendencia.iso.inflacion[1] = 3.961772345 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `0.0256821` | cuerpo | …\| 3.96 \| \| Thomas, K de traslación \| 0.0256821 \| −0.94 \| 5.10 \|… | datos › m11.tendencia.ajustes[1].ee[0] = 0.0256821437; recomputo › m11_Thomas.tendencia.translate.ee[1] = 0.02568214368 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `-0.94` | cuerpo | …Thomas, K de traslación \| 0.0256821 \| −0.94 \| 5.10 \| \| Matérn, K … | datos › m11.tendencia.ajustes[1].z[0], m11.tendencia.ajustes[3].z[0] = [-0.9444853252, -0.9386481783]; recomputo › m11_Thomas.tendencia.translate.z[1], m11_MatClust.tendencia.translate.z[1] = [-0.944485325185255, -0.93864817832643 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `5.10` | cuerpo | …K de traslación \| 0.0256821 \| −0.94 \| 5.10 \| \| Matérn, K isotrópi… | datos › m11.tendencia.ajustes[1].inflacion[0] = 5.102361163; recomputo › m11_Thomas.tendencia.translate.inflacion[1] = 5.102361163 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `0.0199819` | cuerpo | ….94 \| 5.10 \| \| Matérn, K isotrópica \| 0.0199819 \| −1.21 \| 3.97 \… | datos › m11.tendencia.ajustes[2].ee[0] = 0.01998194; recomputo › m11_MatClust.tendencia.iso.ee[1] = 0.01998194004 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `-1.21` | cuerpo | …\| Matérn, K isotrópica \| 0.0199819 \| −1.21 \| 3.97 \| \| Matérn, K … | datos › m11.tendencia.ajustes[2].z[0] = -1.213916556; recomputo › m11_MatClust.tendencia.iso.z[1] = -1.213916556 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `3.97` | cuerpo | …n, K isotrópica \| 0.0199819 \| −1.21 \| 3.97 \| \| Matérn, K de trasl… | datos › m11.tendencia.ajustes[2].inflacion[0] = 3.969881801; recomputo › m11_MatClust.tendencia.iso.inflacion[1] = 3.969881801 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `0.0258419` | cuerpo | …\| 3.97 \| \| Matérn, K de traslación \| 0.0258419 \| −0.94 \| 5.13 \|… | datos › m11.tendencia.ajustes[3].ee[0] = 0.0258418526; recomputo › m11_MatClust.tendencia.translate.ee[1] = 0.02584185256 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `-0.94` | cuerpo | …Matérn, K de traslación \| 0.0258419 \| −0.94 \| 5.13 \| \| Cox log-ga… | datos › m11.tendencia.ajustes[1].z[0], m11.tendencia.ajustes[3].z[0] = [-0.9444853252, -0.9386481783]; recomputo › m11_Thomas.tendencia.translate.z[1], m11_MatClust.tendencia.translate.z[1] = [-0.944485325185255, -0.93864817832643 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `5.13` | cuerpo | …K de traslación \| 0.0258419 \| −0.94 \| 5.13 \| \| Cox log-gaussiano,… | datos › m11.tendencia.ajustes[3].inflacion[0] = 5.134091083; recomputo › m11_MatClust.tendencia.translate.inflacion[1] = 5.134091083 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `0.0209735` | cuerpo | …\| \| Cox log-gaussiano, K isotrópica \| 0.0209735 \| −1.16 \| 4.17 \|… | datos › m11.tendencia.ajustes[4].ee[0] = 0.020973499; recomputo › m11_LGCP.tendencia.iso.ee[1] = 0.020973499 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `-1.16` | cuerpo | …gaussiano, K isotrópica \| 0.0209735 \| −1.16 \| 4.17 \| \| Cox log-ga… | datos › m11.tendencia.ajustes[4].z[0] = -1.156526521; recomputo › m11_LGCP.tendencia.iso.z[1] = -1.156526521 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `4.17` | cuerpo | …o, K isotrópica \| 0.0209735 \| −1.16 \| 4.17 \| \| Cox log-gaussiano,… | datos › m11.tendencia.ajustes[4].inflacion[0] = 4.166878282; recomputo › m11_LGCP.tendencia.iso.inflacion[1] = 4.166878282 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `0.026767` | cuerpo | …Cox log-gaussiano, K de traslación \| 0.026767 \| −0.91 \| 5.32 \| Fue… | datos › m11.tendencia.ajustes[5].ee[0] = 0.0267669545; recomputo › m11_LGCP.tendencia.translate.ee[1] = 0.02676695451 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `-0.91` | cuerpo | …ussiano, K de traslación \| 0.026767 \| −0.91 \| 5.32 \| Fuente: del c… | datos › m11.tendencia.ajustes[5].z[0] = -0.9062072347; recomputo › m11_LGCP.tendencia.translate.z[1] = -0.9062072347 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `5.32` | cuerpo | …K de traslación \| 0.026767 \| −0.91 \| 5.32 \| Fuente: del capítulo (… | datos › m11.tendencia.ajustes[5].inflacion[0] = 5.317884318; recomputo › m11_LGCP.tendencia.translate.inflacion[1] = 5.317884318 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `3.96` | cuerpo | …. \|\|\| ::: info Dato Error de : de 3.96 a 5.32 veces el de Poisson. … | datos › m11.tendencia.ajustes[0].inflacion[0] = 3.961772345; recomputo › m11_Thomas.tendencia.iso.inflacion[1] = 3.961772345 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `5.32` | cuerpo | …::: info Dato Error de : de 3.96 a 5.32 veces el de Poisson. Con Thom… | datos › m11.tendencia.ajustes[5].inflacion[0] = 5.317884318; recomputo › m11_LGCP.tendencia.translate.inflacion[1] = 5.317884318 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `26` | cuerpo | …ón la varianza se multiplica por unas 26: 2 107 sedes valen unas 80. :… | efecto de diseño con la aproximación por defecto, redondeado = 26 \| efecto de diseño con fast = FALSE, redondeado = 26 | VERIFICADA · aritmética sobre cifras verificadas |
| `2107` | cuerpo | …a varianza se multiplica por unas 26: 2 107 sedes valen unas 80. ::: :… | datos › m5.capas.oferta.n = 2107; recomputo › urbana.n_urbana = 2107 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `80` | cuerpo | …a por unas 26: 2 107 sedes valen unas 80. ::: ::: tip Interpretación… | n efectivo con la aproximación por defecto, a la decena = 80 \| n efectivo con fast = FALSE, a la decena = 80 | VERIFICADA · aritmética sobre cifras verificadas |
| `2107` | cuerpo | …onfía de un error estándar que cuenta 2 107 sedes independientes: resp… | datos › m5.capas.oferta.n = 2107; recomputo › urbana.n_urbana = 2107 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `1.59e-07` | notas | …; con Thomas y K de traslación, κ = 1.59e-07 y σ = 1067 m (con , 1.09e… | recomputo › m11b_trend.translate.kappa = 1.591085223e-07 | VERIFICADA · re-ejecutada en R |
| `1.09e-07` | notas | …ón, κ = 1.59e-07 y σ = 1067 m (con , 1.09e-07 y 1320 m). La corrección… | recomputo › m11_Thomas.translate.parametros.kappa = 1.091186756e-07 | VERIFICADA · re-ejecutada en R |
| `2107` | notas | …icional. Un error estándar que cuenta 2 107 sedes independientes es el… | datos › m5.capas.oferta.n = 2107; recomputo › urbana.n_urbana = 2107 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `1.21640` | notas | …. En ninguno de los seis la z pasa de 1.21640 en valor absoluto, lejos… | datos › m11.tendencia.z_xc_abs_max = 1.216401353; máximo de \|z\| del coeficiente de xc en los seis ajustes = 1.216401353 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `1.96` | notas | …1.21640 en valor absoluto, lejos del 1.96 con que se lee. Los errores … | datos › m11.tendencia.z_critico = 1.959963985 | CONTRASTADA · salida de R (JSON del capítulo) |
| `26.1` | notas | …rianzas: con el efecto de diseño es 26.1 y las 2 107 sedes valen 80.6,… | recomputo › m11b_vcov.efecto_exacto = 26.13602837 | VERIFICADA · re-ejecutada en R |
| `2107` | notas | …n el efecto de diseño es 26.1 y las 2 107 sedes valen 80.6, y por eso … | datos › m5.capas.oferta.n = 2107; recomputo › urbana.n_urbana = 2107 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `80.6` | notas | …iseño es 26.1 y las 2 107 sedes valen 80.6, y por eso la diapositiva d… | recomputo › m11b_vcov.n_efectivo_exacto = 80.6166863 | VERIFICADA · re-ejecutada en R |
| `26` | notas | …, y por eso la diapositiva dice «unas 26» y «unas 80» (el capítulo da… | efecto de diseño con la aproximación por defecto, redondeado = 26 \| efecto de diseño con fast = FALSE, redondeado = 26 | VERIFICADA · aritmética sobre cifras verificadas |
| `80` | notas | …la diapositiva dice «unas 26» y «unas 80» (el capítulo da 26.03409 y 8… | n efectivo con la aproximación por defecto, a la decena = 80 \| n efectivo con fast = FALSE, a la decena = 80 | VERIFICADA · aritmética sobre cifras verificadas |
| `26.03409` | notas | …«unas 26» y «unas 80» (el capítulo da 26.03409 y 80.93235). Estos llev… | datos › m11.tendencia.efecto_diseno = 26.03408944; inflación del error estándar de xc con Thomas y K de traslación, al cuadrado = 26.03408944 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `80.93235` | notas | …«unas 80» (el capítulo da 26.03409 y 80.93235). Estos llevan la tenden… | datos › m11.tendencia.n_efectivo = 80.93234853; n / efecto de diseño = 80.93234853 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `1067` | notas | …Thomas y K de traslación, κ = y σ = 1067 m (con , y 1320 m). La cor… | recomputo › m11b_trend.translate.scale = 1066.833128 | VERIFICADA · re-ejecutada en R |
| `1320` | notas | …ación, κ = y σ = 1067 m (con , y 1320 m). La corrección vuelve a mo… | datos › m11.ajustes[1].parametros.scale = 1319.703255; recomputo › m11_Thomas.translate.parametros.scale = 1319.703255 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |

### Diapositiva 38 · Hawkes: cada evento sube la intensidad del siguiente

| Cifra | Dónde | Contexto | Comprobación | Estado |
|---|---|---|---|---|
| `20` | cuerpo | …Eventos por intervalo de 20 unidades: Hawkes y Poisson de… | recomputo › m11b_hawkes.por_intervalos[3].ancho = 20 | VERIFICADA · re-ejecutada en R |
| `4577` | cuerpo | …n de la misma tasa ::: info Dato Con 4 577 eventos en 200 intervalos d… | datos › m11.hawkes.n_eventos = 4577; recomputo › m11_hawkes.n_eventos = 4577 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `200` | cuerpo | …a ::: info Dato Con 4 577 eventos en 200 intervalos de 20 unidades, el… | datos › m8.cuadratura.tabla[2].nd = 200 | CONTRASTADA · salida de R (JSON del capítulo) |
| `20` | cuerpo | …on 4 577 eventos en 200 intervalos de 20 unidades, el índice de disper… | recomputo › m11b_hawkes.por_intervalos[3].ancho = 20 | VERIFICADA · re-ejecutada en R |
| `5.15` | cuerpo | …ianza entre media; 1 bajo Poisson) es 5.15 en el Hawkes y 0.96 en el P… | índice de dispersión del Hawkes, a dos decimales = 5.15 | VERIFICADA · aritmética sobre cifras verificadas |
| `0.96` | cuerpo | …bajo Poisson) es 5.15 en el Hawkes y 0.96 en el Poisson, unas 5 veces … | índice de dispersión del Poisson, a dos decimales = 0.96 | VERIFICADA · aritmética sobre cifras verificadas |
| `5` | cuerpo | …el Hawkes y 0.96 en el Poisson, unas 5 veces más agregado. Con otras… | veces más agregado (5.38), redondeado = 5 | VERIFICADA · aritmética sobre cifras verificadas |
| `5.0` | cuerpo | …gregado. Con otras simulaciones ronda 5.0 (sd 0.6). ::: \|\|\| ::: def… | media del índice de dispersión del Hawkes en 200 réplicas = 5 | VERIFICADA · aritmética sobre cifras verificadas |
| `0.6` | cuerpo | …Con otras simulaciones ronda 5.0 (sd 0.6). ::: \|\|\| ::: definicion P… | desviación típica del índice de dispersión del Hawkes en 200 réplicas = 0.6 | VERIFICADA · aritmética sobre cifras verificadas |
| `5030` | cuerpo | …on datos: , , y , con la semilla 5030. **Por qué importa:** con =… | datos › meta.semillas.hawkes = 5030 | CONTRASTADA · salida de R (JSON del capítulo) |
| `0.5714` | cuerpo | …la 5030. **Por qué importa:** con = 0.5714 el proceso no explota, y ju… | datos › m11.hawkes.razon_ramificacion = 0.5714285714; recomputo › m11_hawkes.razon_ramificacion = 0.5714285714 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `0.5` | cuerpo | …fórmula: \mu = 0.5… | recomputo › m11_hawkes.mu = 0.5 | VERIFICADA · re-ejecutada en R |
| `0.8` | cuerpo | …fórmula: \alpha = 0.8… | recomputo › m11_hawkes.alpha = 0.8 | VERIFICADA · re-ejecutada en R |
| `1.4` | cuerpo | …fórmula: \beta = 1.4… | recomputo › m11_hawkes.beta = 1.4 | VERIFICADA · re-ejecutada en R |
| `4000` | cuerpo | …fórmula: T = 4000… | recomputo › m11_hawkes.T = 4000 | VERIFICADA · re-ejecutada en R |
| `0.5714` | notas | …ida se usa varias veces seguidas. Con 0.5714 el proceso no explota. Es… | datos › m11.hawkes.razon_ramificacion = 0.5714285714; recomputo › m11_hawkes.razon_ramificacion = 0.5714285714 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `1.1667` | notas | …de la tasa no se cita: se comprueba (1.1667 contra 1.14425), y esa sim… | datos › m11.hawkes.tasa_teorica = 1.166666667; recomputo › m11_hawkes.tasa_teorica = 1.166666667 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `1.14425` | notas | …se cita: se comprueba (1.1667 contra 1.14425), y esa simulación es una… | datos › m11.hawkes.tasa_simulada = 1.14425; recomputo › m11_hawkes.tasa_simulada = 1.14425 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `200` | notas | …mulación es una sola realización: con 200 réplicas la tasa media es 1.… | datos › m8.cuadratura.tabla[2].nd = 200 | CONTRASTADA · salida de R (JSON del capítulo) |
| `1.1653` | notas | …ón: con 200 réplicas la tasa media es 1.1653. El índice de dispersión … | recomputo › m11b_hawkes.tasa_media = 1.16533 | VERIFICADA · re-ejecutada en R |
| `9.9` | notas | …o del intervalo con que se cuente (de 9.9 con 20 intervalos a 2.9 con … | recomputo › m11b_hawkes.por_intervalos[0].hawkes = 9.887089912 | VERIFICADA · re-ejecutada en R |
| `20` | notas | …tervalo con que se cuente (de 9.9 con 20 intervalos a 2.9 con 2000) y… | recomputo › m11b_hawkes.por_intervalos[0].k = 20 | VERIFICADA · re-ejecutada en R |
| `2.9` | notas | …se cuente (de 9.9 con 20 intervalos a 2.9 con 2000) y de la realizació… | recomputo › m11b_hawkes.por_intervalos[6].hawkes = 2.948499703 | VERIFICADA · re-ejecutada en R |
| `2000` | notas | …e (de 9.9 con 20 intervalos a 2.9 con 2000) y de la realización (5.0 d… | recomputo › m11b_hawkes.por_intervalos[6].k = 2000 | VERIFICADA · re-ejecutada en R |
| `5.0` | notas | …a 2.9 con 2000) y de la realización (5.0 de media y 0.6 de desviación… | media del índice de dispersión del Hawkes en 200 réplicas = 5 | VERIFICADA · aritmética sobre cifras verificadas |
| `0.6` | notas | …) y de la realización (5.0 de media y 0.6 de desviación en 200 réplica… | desviación típica del índice de dispersión del Hawkes en 200 réplicas = 0.6 | VERIFICADA · aritmética sobre cifras verificadas |
| `200` | notas | …(5.0 de media y 0.6 de desviación en 200 réplicas), así que el 5.4 del… | datos › m8.cuadratura.tabla[2].nd = 200 | CONTRASTADA · salida de R (JSON del capítulo) |
| `5.4` | notas | …sviación en 200 réplicas), así que el 5.4 del capítulo no tiene esos d… | datos › m11.hawkes.veces_mas_agregado = 5.381119831; recomputo › m11_hawkes.veces_mas_agregado = 5.381119831 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `200` | notas | …les: es de esta simulación y de estos 200 intervalos. Cotejo: , , ,… | datos › m8.cuadratura.tabla[2].nd = 200 | CONTRASTADA · salida de R (JSON del capítulo) |

### Diapositiva 39 · Adelgazamiento de Ogata: entre eventos la intensidad solo baja, y su valor en t es la cota

| Cifra | Dónde | Contexto | Comprobación | Estado |
|---|---|---|---|---|
| `1.14425` | cuerpo | …a: se comprueba contra la simulación (1.14425 contra 1.16667). :::… | datos › m11.hawkes.tasa_simulada = 1.14425; recomputo › m11_hawkes.tasa_simulada = 1.14425 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `1.16667` | cuerpo | …contra la simulación (1.14425 contra 1.16667). :::… | datos › m11.hawkes.tasa_teorica = 1.166666667; recomputo › m11_hawkes.tasa_teorica = 1.166666667 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `5030` | notas | …a el índice de dispersión. La semilla 5030 es la del capítulo. Los par… | datos › meta.semillas.hawkes = 5030 | CONTRASTADA · salida de R (JSON del capítulo) |
| `0.5` | notas | …s la del capítulo. Los parámetros μ = 0.5, α = 0.8 y β = 1.4 también; … | recomputo › m11_hawkes.mu = 0.5 | VERIFICADA · re-ejecutada en R |
| `0.8` | notas | …capítulo. Los parámetros μ = 0.5, α = 0.8 y β = 1.4 también; lo que im… | recomputo › m11_hawkes.alpha = 0.8 | VERIFICADA · re-ejecutada en R |
| `1.4` | notas | …Los parámetros μ = 0.5, α = 0.8 y β = 1.4 también; lo que importa de e… | recomputo › m11_hawkes.beta = 1.4 | VERIFICADA · re-ejecutada en R |
| `0.5714` | notas | …lo que importa de ellos es que α/β = 0.5714 es menor que 1 y el proces… | datos › m11.hawkes.razon_ramificacion = 0.5714285714; recomputo › m11_hawkes.razon_ramificacion = 0.5714285714 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |

### Diapositiva 40 · El proyecto integrador y la práctica

| Cifra | Dónde | Contexto | Comprobación | Estado |
|---|---|---|---|---|
| `5` | notas | …Unos 5 minutos. El enunciado complet… | minutos que se asignan a cada bloque de la sesión: decisión del docente, no un dato del capítulo | PARÁMETRO de diseño |

### Diapositiva 41 · El proyecto integrador declara por escrito cinco decisiones antes de la primera figura

| Cifra | Dónde | Contexto | Comprobación | Estado |
|---|---|---|---|---|
| `2209` | cuerpo | …ventana \| por qué esa \| la capa trae 2 209 sedes y 2 107 caen dentro… | recomputo › urbana.n_capa = 2209 | VERIFICADA · re-ejecutada en R |
| `2107` | cuerpo | …qué esa \| la capa trae 2 209 sedes y 2 107 caen dentro del perímetro … | datos › m5.capas.oferta.n = 2107; recomputo › urbana.n_urbana = 2107 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `66.3` | cuerpo | …r qué ninguno \| el pico del mapa baja 66.3 % al abrir σ de 233 a 1867… | datos › m2.familia.caida_pct = 66.2912081; recomputo › anchos.caida_pct = 66.2912081 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `233` | cuerpo | …co del mapa baja 66.3 % al abrir σ de 233 a 1867 m \| \| La corrección… | datos › m2.familia.sigmas_m[0] = 233.3949; recomputo › anchos.sigmas_m[0] = 233.3949 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `1867` | cuerpo | …mapa baja 66.3 % al abrir σ de 233 a 1867 m \| \| La corrección de bor… | datos › m2.familia.sigmas_m[6] = 1867.1589; recomputo › anchos.sigmas_m[6] = 1867.1589 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `800` | cuerpo | …\| qué conserva \| en Kennedy, con σ = 800 m, 270.36 sedes por defecto… | datos › m4.sigmas_m = [200, 400, 800] | CONTRASTADA · salida de R (JSON del capítulo) |
| `270.36` | cuerpo | …conserva \| en Kennedy, con σ = 800 m, 270.36 sedes por defecto y 262.… | datos › m4.tabla[2].masa_defecto = 270.3619071; recomputo › bordes.800.masa_defecto = 270.3619071 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `262.00` | cuerpo | …σ = 800 m, 270.36 sedes por defecto y 262.00 con \| \| La cuadratura \… | datos › m4.tabla[2].masa_diggle = 262; recomputo › bordes.800.masa_diggle = 262 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `9.2` | cuerpo | …qué y qué teselas \| el AIC se mueve 9.2 puntos \| \| La estimación de… | datos › m8.cuadratura.rango_aic = 9.199466457; recomputo › m8_nd.rango_aic = 9.199466457 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `27.1` | cuerpo | …ción de K \| con qué corrección \| μ de 27.1 o 52.3 sedes por conglome… | datos › m11.ajustes[0].mu = 27.09650952; recomputo › m11_Thomas.iso.mu = 27.09650952 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `52.3` | cuerpo | …K \| con qué corrección \| μ de 27.1 o 52.3 sedes por conglomerado \| … | datos › m11.ajustes[1].mu = 52.34765759; recomputo › m11_Thomas.translate.mu = 52.34765759 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |

### Diapositiva 42 · Lo que se llevan hoy

| Cifra | Dónde | Contexto | Comprobación | Estado |
|---|---|---|---|---|
| `36.1` | cuerpo | …r su titular: la cola infla la razón (36.1 contra 1.58) - La **cuadrat… | datos › m7.bogota.curva.razon = 36.0759; recomputo › m7.bogota.total = 36.07589681 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `1.58` | cuerpo | …: la cola infla la razón (36.1 contra 1.58) - La **cuadratura** viaja … | datos › m7.bogota.curva.razon_bulto = 1.58183; recomputo › m7.bogota.bulto = 1.581834466 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |
| `62` | cuerpo | …ntra el modelo, no contra el azar: el 62 % de los radios fuera, y la b… | datos › m10.pct_r_fuera_de_banda = 62; recomputo › m10.pct_fuera = 62 | VERIFICADA · re-ejecutada en R y coincide con el JSON del capítulo |

### Diapositiva 43 · Práctica: tres ejercicios guiados, la autoevaluación y el proyecto

| Cifra | Dónde | Contexto | Comprobación | Estado |
|---|---|---|---|---|
| `4900000` | cuerpo | …no se puede leer** — : desplazado 4 900 000 unidades; ¿cuál no da erro… | texto del capítulo: «4 900 000 unidades» | CONTRASTADA · texto del capítulo |
