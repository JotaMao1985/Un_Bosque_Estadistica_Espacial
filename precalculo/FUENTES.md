# Hoja de procedencia — el hilo colombiano de datos abiertos

Material de estudio de **Estadística Espacial 2026-II (20929)** · tarea **T0.4** · 2026-08-03

Todo lo que aparece aquí está **verificado ejecutando**, no leído de una ficha de metadatos.
Las cifras las escribe `datos/procesado/procedencia.json`, que generan los scripts de
`precalculo/`; esta hoja es su versión legible. Ninguna cifra de este archivo está escrita a mano.

**Reproducir todo, en este orden:**

```bash
R=/Library/Frameworks/R.framework/Versions/4.4-arm64/Resources/bin/Rscript
$R precalculo/datos_colombia.R && $R precalculo/llave_divipola.R && \
$R precalculo/datos_bogota.R && $R precalculo/datos_clima.R && \
$R precalculo/datos_saber11.R && $R precalculo/verifica_t04.R
```

El orden importa: `llave_divipola.R` produce `municipios_llave.csv`, del que dependen los tres que
vienen detrás a través de `carga_municipios()`.

---

## 1. Las cinco fuentes

| # | Qué | Fuente | Licencia | Fijada por | Uso |
|---|---|---|---|---|---|
| 1 | Límites municipales y departamentales | **DANE**, Marco Geoestadístico Nacional, vía geoBoundaries (gbOpen) | CC BY 4.0 | commit `9469f09` | caps. 3, 6, 7, 8 |
| 1b | **DIVIPOLA oficial** — códigos y tipo de entidad | **DANE** (`gdxc-w37w`, datos.gov.co) | CC BY-SA 4.0 | SHA-256 | valida la llave; da la columna `tipo` |
| 2 | Deserción y cobertura neta 2024 | **MEN** (`nudc-7mev`, datos.gov.co) | CC BY-SA 4.0 | SHA-256 | caps. 6, 7, 8 |
| 3 | Colegios de Bogotá + perímetro urbano + localidades | **SED** y **SDP**, vía Datos Abiertos Bogotá / IDECA | CC BY-SA 4.0 · CC BY 4.0 | UUID de recurso (versión 12.25) + SHA-256 | caps. 4, 5 |
| 4 | Normales climatológicas 1991-2020 | **IDEAM** (`nsz2-kzcq`, datos.gov.co) | CC BY-SA 4.0 | SHA-256 | cap. 9 |
| 5 | Microdatos Saber 11, periodo 20224 | **ICFES** (`kgxf-xxbe`, datos.gov.co) | CC BY-SA 4.0 | SHA-256 | caps. 3, 4, 5, 6, 7, 8 |

**Por qué la huella SHA-256.** geoBoundaries se puede fijar por commit; datos.gov.co no.
Sus conjuntos se reemplazan en sitio y la URL sigue siendo la misma. Sin huella, una fuente
que cambia bajo los pies pasa desapercibida y el material deja de cuadrar en silencio.
Con huella, la reejecución lo canta.

---

## 2. Las capas congeladas

**La geometría se guarda UNA vez.** Las capas municipales pesaban 78 MB cada una porque cada una
arrastraba su propia copia de los 1 122 polígonos sin simplificar: 156 MB de duplicación. Ahora la
geometría vive solo en `colombia_adm2.gpkg` y los atributos en CSV de ~60–120 KB, unidos por
`shapeID` —la identidad estable que trae geoBoundaries, no la posición de fila ni el nombre—.
`carga_municipios()` de `precalculo/fuentes.R` rehace la unión en una línea:

```r
source("precalculo/fuentes.R")
muni <- carga_municipios()                 # geometría + llave + MEN + Saber 11
muni <- carga_municipios(saber11 = FALSE)  # solo llave + MEN
```

| Archivo | Contenido | n | CRS |
|---|---|---|---|
| `colombia_adm1.gpkg` | departamentos | 33 | 9377 |
| `colombia_adm2.gpkg` | municipios — **la única copia de la geometría municipal** | 1 122 | 9377 |
| `municipios_llave.csv` | llave DIVIPOLA, tipo de entidad, deserción y cobertura del MEN | 1 122 | — |
| `municipios_saber11.csv` | agregados de Saber 11 | 1 113 | — |
| `casos_territoriales.json` | Belén de Bajirá y Mapiripana, documentados | 2 | — |
| `bogota_colegios.gpkg` | sedes educativas (patrón puntual) | 2 209 | 9377 |
| `bogota_colegios_saber11.gpkg` | las mismas, **marcadas** con el puntaje | 2 209 | 9377 |
| `bogota_ventana_urbana.gpkg` | ventana A — perímetro urbano | 370,09 km² | 9377 |
| `bogota_ventana_dc.gpkg` | ventana B — D.C. completo | 1 633,14 km² | 9377 |
| `bogota_localidades.gpkg` | localidades | 20 | 9377 |
| `colombia_estaciones_clima.gpkg` | estaciones con T media anual y altitud | 361 | 9377 |

Todo en **EPSG:9377** (MAGNA-SIRGAS / Origen Nacional) y en **GeoPackage**, no en shapefile:
el shapefile trunca los nombres de campo a 10 caracteres y no lleva el CRS de forma fiable.
Es además lo que enseña el módulo 7 del capítulo 2.

**0 geometrías inválidas en las capas.** Verificado con `st_is_valid` sobre todas, no supuesto.

---

## 2b. El ordenamiento territorial colombiano — verificado contra el DIVIPOLA oficial

La llave se validó primero por prefijo de departamento, que es una comprobación **interna**: valida
los códigos contra la geometría, no contra quien los define. Contrastarla contra el **DIVIPOLA
oficial del DANE** es lo que la convierte en autoritativa — y es lo que destapó lo que sigue.

| | |
|---|---|
| DIVIPOLA oficial | **1 122 entidades** = 1 103 municipios + **18 áreas no municipalizadas** + 1 isla |
| Nuestros códigos que reconoce | **1 121 de 1 122** |

**Colombia no está hecha solo de municipios.** 18 de las 1 122 unidades son **áreas no
municipalizadas** —territorios de Amazonas, Guainía y Vaupés que no están erigidos en municipio— y
1 es isla. La distinción no es un tecnicismo administrativo: **el tipo de entidad predice tanto si
hay dato como cuál es el dato.**

| Tipo | Unidades | Con Saber 11 | Estudiantes | Puntaje medio |
|---|---|---|---|---|
| Municipio | 1 102 | 1 100 (**99,8 %**) | 1 063 702 | **250,19** |
| Isla (San Andrés) | 1 | 1 (100 %) | 1 048 | 239,52 |
| Área no municipalizada | 18 | 11 (**61,1 %**) | 362 | **196,25** |

**Brecha de 53,94 puntos — 1,04 desviaciones típicas** del puntaje global. Y **7 de las 18 áreas no
municipalizadas no aportan un solo estudiante** a la cohorte.

> **Cómo se mide esta brecha, y por qué así.** A nivel de **estudiante**, no promediando medias de
> unidad. Las áreas no municipalizadas tienen entre **2 y 24** estudiantes cada una: la media de
> medias la domina el ruido de las unidades diminutas, que es exactamente la trampa en la que este
> mismo precálculo ya cayó una vez con el estrato (§3). A nivel de individuo el tamaño de la unidad
> no entra en la cuenta.

### Los dos casos territoriales, documentados en `casos_territoriales.json`

**Belén de Bajirá — tres entidades del Estado, tres respuestas.** Territorio en disputa entre Chocó
y Antioquia. El **DIVIPOLA lo reconoce** como municipio, con el nombre «NUEVO BELÉN DE BAJIRÁ» y el
código **27493**. El **ICFES** codifica a sus **290 estudiantes** bajo **27086**, que el DIVIPOLA no
lista. Y el **Marco Geoestadístico Nacional no tiene polígono** para él. Consecuencia concreta y
comprobada: esos 290 estudiantes **no caen en ningún polígono** — existen en la tabla y no existen
en el mapa.

**Mapiripana — el caso espejo.** Aquí la cartografía **sí** tiene el polígono, pero el DIVIPOLA
vigente ya **retiró el código**: el territorio quedó dentro de Barrancominas (`94343`), que además
está como polígono aparte en la misma capa. El ICFES de 2022 seguía usando el código antiguo
`94663`, y de ahí se recuperó la llave. Se conserva, **marcado como código histórico** en la
columna `divipola_estado`.

Los dos son material del capítulo 3: el módulo 9 (efecto zonificación del MAUP) y el 11
(cartografía y ética). Que una unidad territorial exista para una entidad del Estado y no para otra
no es una anécdota administrativa: **es la unidad de análisis siendo una decisión política**, que es
justo lo que el MAUP dice y lo que el material tiene que poder mostrar con un caso propio.

---

## 3. Lo que cada conjunto enseña — medido, no prometido

Un dato que cuadra no basta: tiene que dar clase. Esto es lo que se comprobó antes de congelarlo.

### Patrón puntual — **la ventana decide el resultado**

| Ventana | Área | n | λ |
|---|---|---|---|
| Perímetro urbano | 370,1 km² | 2 107 | **5,6932** colegios/km² |
| Bogotá D.C. completo | 1 633,1 km² | 2 208 | **1,3520** colegios/km² |

El mismo dato, dos ventanas, **λ cambia por un factor de 4,21**. El módulo 1 del capítulo 4
(«por qué la ventana de observación importa tanto») deja de afirmarlo y pasa a medirlo.
La causa es Sumapaz: rural, enorme y casi sin colegios.

### Geoestadística — **el kriging ordinario está mal planteado aquí**

| | |
|---|---|
| corr(altitud, temperatura) | **−0,9791** (R² = 0,9587) |
| Gradiente térmico | **−5,56 °C por cada 1 000 m** |
| Variograma del dato crudo | pepita 0,000 · meseta 28,863 · rango 118,9 km |
| Variograma de los residuos (quitada la altitud) | pepita 0,502 · **meseta 1,270** · rango 252,3 km |
| Distancia al vecino más próximo | mediana 18,2 km (mín. 3,3 · máx. 603,9) |

El gradiente cae dentro del rango físico de referencia (−5 a −7 °C/1 000 m): el dato
**reproduce la ley que debe reproducir**, y eso es evidencia de que está sano. Quitar la altitud
divide la meseta por **23**, que es la demostración con dato real de por qué el capítulo 9
necesita su módulo 10 (kriging universal y con deriva externa) y no le basta el 9.

### Falacia ecológica y MAUP — **la misma pareja de variables a tres niveles**

Educación de la madre (0–9) contra puntaje global, 680 360 estudiantes:

| Nivel | r |
|---|---|
| Estudiante | **+0,3068** |
| Municipio (n ≥ 30, sin ponderar) | +0,2940 |
| Municipio (ponderado por n) | +0,6372 |
| Departamento | **+0,5650** |

Estable frente al umbral de tamaño (+0,2898 sin umbral, +0,2940 con n ≥ 30) y creciente al
agregar. El **13,5 %** de la varianza del puntaje vive entre municipios; el 86,5 % restante es
justo lo que la agregación tira a la basura.

> **El caso de aviso, que también se congela.** Con el **estrato** en vez de la educación de la
> madre, la correlación municipal **sin ponderar y sin umbral es −0,0577** — negativa — y sube
> hasta **+0,6313** con n ≥ 1 000. No es la inversión de signo de Robinson: son municipios
> diminutos, uno de ellos con **dos estudiantes** y estrato medio 6,00 tirando del extremo alto.
> Publicar el −0,06 a secas habría sido enseñar un artefacto como si fuera un fenómeno.
> Además, con el estrato la ausencia del dato **no es inocente**: corr(cobertura del estrato,
> puntaje medio del municipio) = **+0,5952**, frente a **−0,0177** con la educación de la madre.
> Las dos escaleras van al material: una es el fenómeno y la otra es la trampa.

---

## 4. Vacíos y excepciones — declarados, nunca disimulados

| Qué | Cuántos | Decisión |
|---|---|---|
| Sedes con geometría centinela ±DBL_MAX en el origen | 2 | Se descartan y se nombran en el registro. No son NA: `st_is_valid` las da por buenas |
| **RURAL EL TABACO** (Sumapaz) | 1 | Cae **219 m fuera** del distrito según **las dos** delineaciones independientes. Se conserva en la capa con `en_ventana_dc = FALSE` |
| Sedes coincidentes en la misma coordenada | 43 | Reales (misma sede, varias jornadas). Se declaran: `spatstat` las rechaza al construir el `ppp` |
| Colegios sin puntaje de Saber 11 | 1 105 de 2 209 | **No es un fallo de unión**: la capa trae sedes de preescolar y primaria, que no presentan una prueba de grado 11 |
| Sedes de Saber 11 sin punto en la capa | 39 (2 136 estudiantes, **1,4 %** de Bogotá) | Declaradas |
| **Belén de Bajirá** (ICFES `27086`, DIVIPOLA `27493`, 290 estudiantes) | 1 | Sin polígono en el MGN. **No es solo un vacío**: es un caso trabajado — ver §2b |
| **Mapiripana** (`94663`) | 1 | Código retirado del DIVIPOLA vigente; se conserva marcado en `divipola_estado` — ver §2b |
| Registros sin código de municipio del colegio | 2 | `divipola = NA`; fuera de todo agregado. `sprintf("%05d", NA)` devuelve la **cadena** `"000NA"`, que no falla y viaja como si fuera un código |
| Municipios sin Saber 11 en la capa | 9 | Van con **NA**, nunca con 0. Un cero ahí sería un dato inventado |
| Estaciones fuera del territorio al proyectar | 3 | Aeropuertos costeros; la fuente da 2 decimales (~1,1 km) y a esa resolución cruzan la línea de costa. Se conservan con `en_territorio = FALSE` |
| Estaciones en coordenada repetida | 1 | Se conserva la primera: `gstat` aborta el variograma si hay dos |
| Sin estrato utilizable | 111 348 (**10,45 %**) | NA |
| Sin educación de la madre utilizable | 385 076 (**36,14 %**) | NA. «No sabe» y «No Aplica» **no** son cero: no saber no es no tener estudios |

**Un vacío que se cerró.** T0.4a dejó **Mapiripana (Guainía)** sin código DIVIPOLA porque el MEN
no la reporta en 2024. Los microdatos de Saber 11 sí la traen (`94663`, 32 estudiantes), y el
código se recupera de ahí y se **valida con la misma comprobación independiente** que el resto:
sus dos primeros dígitos contra el departamento obtenido por unión espacial. La llave queda
en **1 122 de 1 122**. Las variables del MEN siguen en NA, que es lo honesto: un código
verificado y unas variables ausentes no son lo mismo.

---

## 5. Una fuente descartada, y por qué

**`x5ay-984n` — MEN, sedes educativas de preescolar, básica y media (nacional).**
Era el candidato obvio para el patrón puntual: trae `cod_dane_municipio`, `total_matricula` y
coordenadas de todas las sedes del país. **No sirve.** Sus coordenadas tienen **exactamente
2 decimales** — 1,1 km de resolución — y en Bogotá las 2 403 sedes con coordenada colapsan en
**398 posiciones distintas**. Eso no es un patrón puntual: es una retícula de redondeo, y
cualquier K, G o F mediría el redondeo y no el patrón. Además el rango está corrompido
(longitudes de −7,4·10¹⁵). Se descarta.

Es el mismo motivo por el que T0.4a descartó `finiterank/mapa-colombia-js`: **no se construye
material docente sobre una fuente cuyas coordenadas no se sostienen.**

---

## 6. Auditoría

`precalculo/verifica_t04.R` abre las capas congeladas, las vuelve a medir y **recalcula desde
el crudo** por un camino distinto al del generador — un verificador que repite el cálculo del
generador solo comprueba que R es determinista.

```
90 de 90 comprobaciones OK
```

Y `precalculo/prueba_verifica_t04.R` le rompe el dato a propósito, defecto a defecto, porque
un verificador que nunca falla y uno que no comprueba nada dan la misma salida:

```
17 de 17 defectos inyectados cazados (100%)
```

Los defectos inyectados imitan fallos que ya ocurrieron en este proyecto: la coordenada centinela,
el hueco en la llave DIVIPOLA, el cero donde debía ir NA, el vacío contado como «No», una
discrepancia con el DIVIPOLA que nadie explicó, y **la geometría volviendo a duplicarse** en 78 MB
por capa.

---

## 7. Nota para la Fase 7 (publicación) — el peso, medido

| Carpeta | Peso | Lo que la infla |
|---|---|---|
| `datos/crudo/` | **345 MB** | `COL_ADM2.geojson` 201 MB · `saber11_20224.csv` 130 MB |
| `datos/procesado/` | **86 MB** | `colombia_adm2.gpkg` 78 MB — la **única** copia de la geometría municipal |

`datos/procesado/` pesaba **242 MB** antes de guardar la geometría una sola vez; los atributos
municipales, que eran dos GeoPackage de 78 MB, son ahora dos CSV de **116 KB y 66 KB**. El auditor
comprueba que no vuelvan a aparecer: hay una inyección dedicada a ello.

**Ninguna de las dos carpetas debe entrar al repositorio**, y conviene saberlo ahora y no cuando el
`.gitignore` de lista blanca de T7.2 se las trague sin avisar.

**Nada de esto llega al material publicado.** Los capítulos no incrustan estas capas: incrustan la
salida de `precalculo/geo.R`, que proyecta, simplifica y cuantiza hasta el presupuesto de
**≤ 120 KB por capítulo** fijado en el §4 del plan. Lo que se versiona es el *código* que reproduce
los datos, más `procedencia.json`, `municipios_llave.csv`, `municipios_saber11.csv`,
`casos_territoriales.json` y los JSON de cifras — todo junto, menos de 300 KB.
