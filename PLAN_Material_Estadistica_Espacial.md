# Plan de implementación: Material de estudio — Estadística Espacial 2026-II

**Estado:** 🟢 **T2.4–T2.6 HECHAS el 2026-08-05: EL CAPÍTULO 3 ESTÁ EN PIE y con él se cierra el
Corte I (semanas 1–4). Siguiente: Checkpoint 2 y la Fase 3 (capítulos 4 y 5, patrones puntuales).**
✅ **T2.4 + T2.4b + T2.5 + T2.6 (2026-08-05)** — **el capítulo 3 está precalculado, ensamblado,
auditado y verificado en el navegador.** `Htmls_Espacial/capitulo-3-cartografia-maup.html`,
**621 KB**: 12 módulos, 10 simuladores, 9 mapas, 8 preguntas y 4 ejercicios —**vuelta al molde**,
porque el capítulo cubre una sola semana—, 9+9 bloques R/Python con **116 de 116 cifras verificadas
contra la salida real**. Auditoría: `audita_cap3.py` **354/0 (2 saltadas declaradas)**, arnés
**56/56**, `audita_texto_cap3.py` **130/0** con arnés **20/20**, reproducible byte a byte, consola
limpia en los doce módulos, sin desbordamiento a 1 280, 375 ni **318 px**.
· **El `.geomapa` estrena capas, codificación por diferencias, capas superpuestas y el
CONMUTADOR DE DALTONISMO, que es del motor y alcanza a los capítulos 1 y 2.** Los dos capítulos
anteriores se regeneraron y se verificaron sin regresión.
· **Y el presupuesto de geometría no daba: 1 122 municipios no caben en 120 KB con ninguna
tolerancia.** Bajado de 653 a 199,6 KB por tres vías medidas; el capítulo declara **200 KB**.
· **Veinte defectos reales**, y los más caros los encontró una herramienta sobre trabajo que ya
daba verde. Ver **A.14**.
· **Checkpoint 1 cerrado el 2026-08-04.**
✅ **T2.1 + T2.2 + T2.3 (2026-08-04)** — **el capítulo 2 está precalculado, ensamblado, auditado y
verificado en el navegador.** `Htmls_Espacial/capitulo-2-crs-georreferenciacion.html`, **481 KB**:
12 módulos, 10 simuladores, 7 mapas, **12 preguntas** (8 del quiz + 4 «trampas de CRS» a mitad de
capítulo) y **5 ejercicios guiados** —las dos desviaciones del molde, decididas por Javier porque el
capítulo cubre dos semanas—, más **11+11 bloques R/Python con 66 cifras anunciadas, todas
verificadas contra la salida real**. La geometría pesa **100,6 KB** de los 120 del presupuesto.
El `.geomapa` estrena **la indicatriz de Tissot**: `geo_tissot()` mide h, k, a, b, ω y la escala de
área por diferencias finitas y **descomposición en valores singulares**, y el navegador dibuja las
elipses. **Doce defectos reales, y cinco los encontró una herramienta sobre trabajo que ya daba
verde.** Ver **A.13**.
· **Checkpoint 1 cerrado el 2026-08-04.**
✅ **T1.2 + T1.3 (2026-08-04)** — **el capítulo 1 está ensamblado, auditado y verificado en el
navegador.** `Htmls_Espacial/capitulo-1-datos-espaciales.html`, **492 KB**: 12 módulos, 9
simuladores, 9 mapas, 16 preguntas —8 de la diagnóstica de entrada y 8 de la autoevaluación, de los
cuatro tipos—, 4 ejercicios guiados y 8+8 bloques R/Python con **26 cifras anunciadas**. Lo escribe
`precalculo/ensambla_cap1.py`, así que **D10 deja de ser disciplina y pasa a ser imposible de
violar**: no hay HTML hasta que el guion lo genera desde el JSON. Nuevos: `audita_texto_cap1.py`
(**138 comprobaciones, 0 fallos**) y las inyecciones del capítulo en `prueba_texto.py` (**30/30**).
El **`.geomapa` ya pinta capas** —polilíneas de fondo, segunda capa con símbolo propio, resaltado y
color por marca—, con el **tipo de la marca declarado desde R** y no adivinado en JS; retropropagado
a la plantilla y a `prueba-geomapa.html`. **Ocho defectos reales, y seis estaban en herramientas que
ya daban verde.** Ver **A.12**.
· **T1.1 hecha el 2026-08-04.**
✅ **T1.1 (2026-08-04)** — **el precálculo del capítulo 1 está hecho, auditado y es reproducible
byte a byte.** `genera_cap1.R` (12 módulos, **20 anclas** contra la literatura que **paran** el
script si fallan), `genera_soluciones.R` (los 4 ejercicios guiados con solución calculada),
`audita_cap1.py` (**836 comprobaciones, 0 fallos, 3 saltadas declaradas**, recalculando en
**Python** con geopandas/libpysal/esda para que el control no comparta entorno con lo auditado) y
`prueba_auditor_cap1.py` (**49 inyecciones, 49 cazadas**). Salidas: `cap1_datos.json` 36 KB,
`cap1_mapas.json` 102 KB (**geografía 75,1 KB** + rejillas simuladas 27,0 KB, las dos dentro del
presupuesto), `cap1_soluciones.json` 8,4 KB, más cinco CSV que las pestañas de Python del capítulo
necesitarán. **Cinco defectos reales encontrados y corregidos, tres de ellos en trabajo propio ya
escrito** — y uno es una discrepancia R↔Python que se convierte en el caso trabajado del cap. 6.
Ver **A.11**.
· **Fase 0 cerrada el 2026-08-03. Checkpoint 0 completo.**
✅ **T0.1 (2026-08-03)** — entorno reproducible. `precalculo/instala.R`, `entorno.R`, `entorno.py`,
`versiones.json`, `versiones_py.json`. **15 de 15 paquetes de R** instalados (binarios, ninguno
compiló) y la familia PySAL añadida al entorno `geo_env` que ya existía. Prueba de humo que
**calcula, no solo importa**: **29/29 en R** y **17/17 en Python**. Verificación cruzada R↔Python
sobre el mismo `nc.shp`: **8 de 9 coinciden** (Moran I, ρ del SAR y λ del SEM cuadran a 6
decimales) y la novena es una **discrepancia documentada que se convierte en caso trabajado del
capítulo 3** — ver el anexo del final.
✅ **T0.2 (2026-08-03)** — plantilla del curso en `plantilla/plantilla-capitulo.html`, **193 KB**.
Partiendo de la de Diseño de Experimentos: textos meta, cabecera, pie y bibliografía del syllabus
de Estadística Espacial; **`.glosario-notacion` y `.rubrica` injertados** desde Muestreo y un
**módulo 5 de demostración** que los ejercita. **157 selectores** (133 de DOE + 24 nuevos),
**ninguno perdido**. Verificado: `node --check` limpio, consola sin errores, KaTeX con 18 nodos y
0 `$` sin resolver, CSS aplicado de verdad (medido con `getComputedStyle`), la rúbrica conmuta de
criterio, **0 gráficos huérfanos** tras 6 ciclos de módulo y **sin desbordamiento** ni a 1280 px
ni a 375 px. El glosario **hubo que generalizarlo** — ver A.4.
✅ **T0.3 (2026-08-03)** — **el componente `.geomapa` funciona en sus cinco modos.** Lado de R en
`precalculo/geo.R` (proyectar → simplificar → cuantizar → serializar) y `genera_demo_geomapa.R`;
lado del navegador en la plantilla (**168 selectores**) y capítulo de prueba en
`Htmls_Espacial/prueba-geomapa.html`. Verificado: **escala en x idéntica a la de y hasta 1e-9**
(el criterio duro: no hay deformación), los 6 mapas con tinta, cada lienzo **ceñido a la forma de
su dato** (Colombia 1,38 · pinos 1,00 · Carolina del Norte 0,38), `aria-label` en todos, los
controles cambian el mapa, **0 fugas de ResizeObserver** tras 8 ciclos de módulo, 0 gráficos
huérfanos, consola limpia y sin desbordar ni a 1280 px ni a 375 px. El JSON de demostración bajó
de **531 KB a 166 KB**. Tres fallos reales encontrados y corregidos — ver A.5.
🟡 **T0.4 (2026-08-03) — PARCIAL.** Los **límites administrativos están descargados y
verificados**: `datos/procesado/colombia_adm1.gpkg` (**33 departamentos**) y `colombia_adm2.gpkg`
(**1 122 municipios**), las dos cifras oficiales exactas, **0 geometrías inválidas**, proyectados a
**EPSG:9377** (MAGNA-SIRGAS / Origen Nacional) y con `procedencia.json`. Origen: **MGN del DANE**
vía geoBoundaries gbOpen, **CC BY 4.0**, URL **fijada por commit** `9469f09`. **Queda abierto** el
código DIVIPOLA y, con él, la variable estadística a mapear, más el patrón puntual y los puntos
geoestadísticos — ver A.6.
✅ **T0.4a (2026-08-03)** — **la llave DIVIPOLA está resuelta y la capa de área, lista.**
Javier eligió hilo de **dos escalas** (nacional + Bogotá), variable principal **deserción escolar**
y **falacia ecológica con microdatos reales** de Saber 11. `precalculo/llave_divipola.R` empareja
geoBoundaries con el MEN por etapas: **1 121 de 1 122 (99,9 %)**, con **100 % de coherencia** en una
validación independiente por código de departamento. El único que falta —Mapiripana, Guainía— no
está en el archivo del MEN y queda declarado como vacío de la fuente, con NA. *(Su código se
recupera después, en el cierre de T0.4; y la salida pasa de un GeoPackage a
`datos/procesado/municipios_llave.csv` — ver A.9.)* **Validado como material didáctico:**
deserción con media 3,42 %, sd 1,77, recorrido 0–14,81, y **I de Moran = 0,3809** (p ≈ 6·10⁻¹⁰¹;
por permutación con 999 réplicas, p = 0,001). La cobertura neta da I = 0,2250, un contraste útil.
Y el dato trae **2 islas y 3 subgrafos** de regalo: el caso de `zero.policy` del capítulo 6 sale
solo. Ver A.7.
✅ **T0.4 CERRADA (2026-08-03)** — **el hilo colombiano está completo: los tres tipos de dato
espacial del curso salen de datos abiertos colombianos verificados.** Javier decidió estaciones
del IDEAM para el capítulo 9, patrón puntual **con marcas** y **las dos ventanas** de observación.
- **Patrón puntual:** `bogota_colegios.gpkg`, **2 209 sedes** (SED de Bogotá, CC BY-SA 4.0, versión
  12.25 fijada por UUID de recurso). Dos ventanas congeladas: perímetro urbano (**370,1 km²**,
  λ = **5,6932**/km²) y D.C. completo (**1 633,1 km²**, λ = **1,3520**/km²). **La ventana cambia λ
  por 4,21**: el módulo 1 del capítulo 4 deja de afirmarlo y pasa a medirlo.
- **Geoestadística:** `colombia_estaciones_clima.gpkg`, **361 estaciones** del IDEAM con
  temperatura media anual 1991-2020 y **altitud**. corr = **−0,9791**, gradiente **−5,56 °C/1 000 m**
  —dentro del rango físico—, y quitar la altitud **divide la meseta del variograma por 23**. El
  módulo 10 (deriva externa) sale del propio dato.
- **Microdatos:** Saber 11 20224 del ICFES, **1 065 436 registros**. Falacia ecológica medida:
  educación de la madre da **+0,3627 → +0,3037 → +0,5126** (individuo → municipio → departamento),
  estable frente al umbral. El **estrato** se congela como **caso de aviso**.
  ⚠️ *Cifras **corregidas en T0.5**. Las publicadas el 2026-08-03 (+0,3068 → +0,2940 → +0,5650)
  estaban calculadas con **295 724 estudiantes caídos en silencio** por un fallo de codificación —
  ver **A.10**. La escalera sigue en pie; los números no eran los que aquí decía.*
- **La llave DIVIPOLA queda en 1 122 de 1 122**, y **1 121 de ellos los reconoce el DIVIPOLA oficial
  del DANE** (`gdxc-w37w`), que es la validación autoritativa.
- **Colombia como material:** la capa trae el `tipo` de entidad — **1 103 municipios, 18 áreas no
  municipalizadas, 1 isla**. Brecha de **53,94 puntos (1,04 sd)** entre municipio y área no
  municipalizada, y **7 de las 18** no aportan un solo estudiante. **Belén de Bajirá** y
  **Mapiripana** quedan documentados en `casos_territoriales.json` como caso trabajado del cap. 3.
- **Geometría guardada una sola vez:** atributos en CSV unidos por `shapeID` con
  `carga_municipios()`. `datos/procesado/` pasa de **242 MB a 86 MB**.
- **Auditoría: 90 de 90 comprobaciones**, y el arnés de inyección **caza 17 de 17** defectos.
- Hoja de procedencia en `precalculo/FUENTES.md`. Una fuente **descartada** con causa.
  Ver **A.8** y **A.9**.
✅ **T0.5 (2026-08-03)** — **el arnés de auditoría está montado y probado, y al estrenarse encontró
un defecto real en T0.4.** Núcleo compartido `audita_texto_base.py` (10 familias) + espec corta por
capítulo; `verifica_bloques.py` con el R y el Python correctos y **un capítulo sin `#>` declarado
fallo**; `prueba_texto.py` con **36 inyecciones, 36 cazadas y cero familias sin probar**;
`cuenta_sitio.py`; `mide_punto_ciego.py`. Banco de pruebas propio: `prueba-auditoria.html`,
6 módulos con cifras espaciales reales, reproducible byte a byte. **El defecto:** `Rscript`
arrancaba con `LC_CTYPE=C` y las categorías acentuadas de Saber 11 no emparejaban —**295 724
estudiantes, el 27,7 % de la cohorte y justo los niveles educativos más altos, caían en NA sin
ruido**—. Las cifras de la falacia ecológica del cap. 3 quedan corregidas, T0.4 regenerada y de
vuelta en 90/90, y `utf8.R` + `rscript.sh` cierran la trampa de raíz. Ver **A.10**.
· **Creado:** 2026-08-03
**Curso:** ESTADÍSTICA ESPACIAL (código 20929), Facultad de Ciencias, programa de Estadística,
semestre 7, 2 créditos, 4 h/semana, 63 h presenciales + 32 h independientes.
**Syllabus fuente:** `Bosque 2026/Syllabus/20929_Syllabus_Estadistica_Espacial_2026-II.docx`
**Plan del syllabus:** `Bosque 2026/Syllabus/PLAN_Estadistica_Espacial_2026-II.md`
**Formato de referencia:** `Bosque 2026/Muestreo/sitio/muestreo/capitulo-1-encuestas-sesgos.html`
**Plantilla base (la más reciente):** `Bosque 2026/Diseno de experimentos/plantilla/plantilla-capitulo.html`
**Carpeta del proyecto:** `Bosque 2026/Estadistica espacial/`

> **Nota sobre la ruta que diste.** Pediste el formato de
> `Muestreo/Htmls_Muestreo/capitulo-1-introduccion.html`. Esa carpeta ya no existe: el material de
> Muestreo se movió a `Muestreo/sitio/muestreo/` y el capítulo 1 se renombró a
> `capitulo-1-encuestas-sesgos.html`. Es el archivo que se toma como referencia.

---

## 1. Resumen

Construir, desde cero, el material de estudio autónomo de Estadística Espacial en el formato
interactivo de la casa: **10 capítulos HTML autocontenidos**, uno por bloque temático del
cronograma, con teoría, fórmulas KaTeX, código R y Python en pestañas, simuladores, autoevaluación
y ejercicios guiados con solución calculada.

Es un curso **nuevo**, no una migración: no hay material previo que reutilizar. Y trae una
dificultad que ningún curso anterior tuvo: **este material necesita dibujar mapas**, y el stack
actual (Chart.js sobre canvas) no dibuja mapas. La Fase 0 resuelve eso con un componente nuevo
antes de escribir el primer capítulo.

El curso cubre los tres tipos de datos espaciales —patrones puntuales, datos de área y datos
geoestadísticos— y cierra con aprendizaje automático espacial. La columna vertebral pedagógica es
una sola idea, repetida en los diez capítulos: **la dependencia espacial no es un estorbo, es
información, y ninguna herramienta que suponga independencia sirve aquí**.

---

## 2. Decisiones de arquitectura

Las cuatro primeras las aprobaste el 2026-08-03; el resto se derivan de ellas o del formato ya
establecido. **No reabrir sin motivo.**

| # | Decisión | Elección | Por qué |
|---|---|---|---|
| D1 | Número de capítulos | **10**, alineados semana a semana con el cronograma | Un bloque temático mayor por capítulo, 12 módulos internos cada uno; es la escala de Diseño de Experimentos |
| D2 | Motor de mapas | **Componente propio en canvas** (`.geomapa`), GeoJSON proyectado y simplificado en R e incrustado como JSON | Mantiene la autocontención (sin CDN nuevo, sin red) y permite mapas *interactivos*: el mapa es un simulador, no una ilustración |
| D3 | Paquetes | **Stack de R completo + stack geoespacial de Python** | Los binarios arm64 existen para todo; habilita pestañas R/Python en todo el material y el syllabus ya promete puentes a GeoPandas/PySAL |
| D4 | Datos | **Mixto**: canónicos de la literatura + un hilo colombiano de datos abiertos | Los canónicos permiten al estudiante contrastar cifras con Bivand, Baddeley y Anselin; el hilo colombiano sostiene el proyecto integrador |
| D5 | Lenguaje principal | **R**, con Python en `.code-tabs` en todos los bloques donde exista equivalente real | El syllabus fija R (`sf`, `spatstat`, `spdep`, `gstat`, `tmap`) como eje |
| D6 | Nombre del componente de mapas | **`.geomapa` / `iniciarGeomapas`** | `iniciarMapasEstacionales` **ya existe** en la plantilla (el mapa mes × año de Series de Tiempo). Usar `mapa` colisiona |
| D7 | Plantilla de partida | La de **Diseño de Experimentos** (176 KB, 133 selectores) | Es la más reciente: trae `.rejilla-*` y `.arbol-*`, que la de Series de Tiempo no tiene |
| D8 | Componentes a injertar | **`.glosario-notacion`** y **`.rubrica`**, desde Muestreo | La notación espacial es densa (s, D, Z(s), λ, W, γ(h), C(h), I, G\*) y el proyecto integrador del cap. 10 necesita rúbrica |
| D9 | Cómputo pesado | **Siempre en R**, nunca en el navegador | Ajustes `ppm`, kriging, GWR, envolventes de simulación y CV por bloques son minutos de cómputo |
| D10 | Cifras del material | **Ninguna escrita a mano**: todas salen del JSON del precálculo | Regla heredada; en Muestreo fallaron cinco cifras escritas de memoria mientras se corregía justamente ese problema |
| D11 | Publicación | **Repo propio: `https://github.com/JotaMao1985/Un_Bosque_Estadistica_Espacial.git`** | ✅ **DECISIÓN DE JAVIER (2026-08-04)**, cierra la pregunta 1 del §10. No va al paraguas `UnBosque_Teor` donde vive Muestreo: sigue el patrón de **Series de Tiempo** y de Diseño de Experimentos, que tienen repo propio. Detalles de estructura en la Fase 7 |

---

## 3. Inventario del entorno (verificado hoy, no supuesto)

**R.** Hay dos instalaciones y solo una sirve. La del `PATH` es Homebrew 4.6.0 y **no tiene ni
`sf`**. La buena es:

```
/Library/Frameworks/R.framework/Versions/4.4-arm64/Resources/bin/Rscript
```

R 4.4.1, con **GDAL 3.13.0, GEOS 3.8.5 y PROJ 9.5.1** ya instalados y funcionando (`st_read` sobre
el shapefile `nc` de `sf` devuelve los 100 condados con CRS NAD27). Que la capa de sistema esté
resuelta es la buena noticia: es la parte difícil.

| Paquete | Estado hoy | Binario arm64 en CRAN |
|---|---|---|
| `sf`, `terra`, `sp`, `units`, `jsonlite`, `MASS` | ✅ instalados | — |
| `spdep` | ❌ falta | ✅ 1.4-2 |
| `gstat` | ❌ falta | ✅ 2.1-5 |
| `spatstat` (+ `.explore`, `.model`) | ❌ falta | ✅ 3.5-1 / 3.8-0 / 3.6-1 |
| `tmap` | ❌ falta | ✅ 4.2 |
| `spatialreg` | ❌ falta | ✅ 1.4-3 |
| `spData` | ❌ falta | ✅ 2.3.4 |
| `sfdep` | ❌ falta | ✅ 0.2.5 |
| `stars` | ❌ falta | ✅ 0.7-1 |
| `blockCV` | ❌ falta | ✅ 3.2-0 |
| `GWmodel` | ❌ falta | ✅ 2.4-1 |
| `classInt` (cortes de clase: Jenks, cuantiles…) | ❌ falta | ✅ 0.4-11 |
| `rmapshaper` (simplificación de geometría) | ❌ falta | ✅ 0.6-0 |
| `spatstat.data` | ❌ falta | ✅ 3.1-9 |
| `HistData` (datos de Snow) | ❌ falta | ✅ 1.0.0 |
| `spatialsample`, `RColorBrewer` | ❌ faltan | ✅ 0.6.1 / 1.1-3 |
| `spDataLarge` | ❌ falta | ⚠️ **sin binario** — se instala desde el repo de r-spatial o se prescinde |

**Dónde vive cada dato — comprobado contra el `data/` de cada paquete, no de memoria:**

| Dato | Paquete real | Nota |
|---|---|---|
| `meuse` | **`sp`** (155 obs, 14 col.) — *no* `gstat` | Verificado ejecutando `data(meuse, package="sp")` |
| `jura` | **`gstat`** — *no* `sp` | Junto a `coalash`, `walker`, `sic97`, `oxford`, `fulmar`, `wind` |
| `columbus` | **`spData`** *y* `spdep` | En `spdep` está además **`oldcol`** (`COL.OLD`, `COL.nb`), que es el que usan los ejemplos de Anselin |
| `boston`, `us_states`, `nc.sids`, `getisord`, `auckland`, `baltimore`, `house`, `world` | **`spData`** | `getisord` y `auckland` son los datos canónicos de Getis-Ord y de LISA |
| `bei`, `japanesepines`, `cells`, `redwood`, `swedishpines`, `lansing`, `chorley` | **`spatstat.data`** | |
| `nc` (SIDS) | **`sf`**, como shapefile | Ya verificado: 100 condados, CRS NAD27 |
| `Snow.deaths`, `Snow.pumps`, `Snow.streets` | **`HistData`** | |

**Python.** `/opt/homebrew/Caskroom/mambaforge/base/bin/python3` tiene numpy, pandas, matplotlib y
scipy; **no tiene nada geoespacial**: faltan `geopandas`, `shapely`, `pyproj`, `libpysal`, `esda`,
`spreg`, `pointpats`, `skgstat`, `rasterio`.

**Geodatos locales:** ninguno. Cero `.shp`, `.gpkg`, `.geojson` o `.kml` en todo `Bosque 2026`.

---

## 4. El componente nuevo: `.geomapa`

Es la pieza que decide si este material funciona. Se construye **entera en la Fase 0**, antes del
capítulo 1, y se prueba con los cinco modos que van a hacer falta.

**Cómo funciona.** En R se proyecta la geometría al CRS adecuado, se simplifica con
`st_simplify`/`rmapshaper` hasta un presupuesto de vértices, se normaliza a coordenadas de lienzo y
se serializa a JSON. En el navegador, `iniciarGeomapas` pinta sobre `<canvas>` con Path2D. Sin
Leaflet, sin teselas, sin red.

| Modo | Para qué | Aparece en |
|---|---|---|
| `poligonos` | Coropletos con escala de color y leyenda | caps. 3, 6, 7, 8 |
| `puntos` | Patrones puntuales sobre su ventana de observación | caps. 1, 4, 5 |
| `grafo` | Grafo de vecindad: nodos en los centroides, aristas según W | caps. 6, 7, 8 |
| `rejilla` | Superficies continuas: KDE, predicción y varianza de kriging | caps. 5, 9, 10 |
| `proyeccion` | El mismo territorio bajo distintos CRS, con la distorsión medida | cap. 2 |

**Requisitos no negociables.**
- **Relación de aspecto fija.** Un mapa con la escala x ≠ escala y es un mapa mal dibujado. Se
  respeta el *bounding box* proyectado, con letterboxing dentro del canvas.
- **Leyenda con la escala real**, incluidos los cortes de clase; los cortes los calcula R, no JS.
- **Reactivo.** El mapa se redibuja cuando cambia un control del simulador (número de clases,
  criterio de W, ancho de banda…) sin recrear el canvas.
- **Se destruye al cambiar de módulo**, igual que los Chart.js, o se acumulan.
- **Accesible:** `role="img"` con `aria-label` que resume qué muestra el mapa, más una tabla de
  respaldo plegable con los valores cuando el mapa es la única vía al dato.

**Presupuesto de peso.** Los capítulos actuales pesan 300–530 KB. La geometría inline no debe
superar **~120 KB por capítulo** (≈ 8 000 vértices). Los 1 122 municipios de Colombia sin simplificar
no caben; simplificados a tolerancia visual, sí. Lo verifica T0.3.

---

## 5. Del cronograma a los capítulos

| Cap. | Título | Semanas | Módulo del syllabus | Corte |
|---|---|---|---|---|
| 1 | Datos espaciales y la primera ley de la geografía | 1 | I | I |
| 2 | SIG, sistemas de referencia y georreferenciación con `sf` | 2–3 | I | I |
| 3 | Cartografía estadística y el MAUP | 4 | I | I |
| 4 | Patrones puntuales: descripción, CSR y funciones de resumen | 6–7 | II | II |
| 5 | Intensidad por núcleos y modelamiento de procesos puntuales | 8–10 | II | II |
| 6 | Datos de área y la matriz de pesos espaciales | 11 | III | III |
| 7 | Autocorrelación espacial global y local | 12–13 | III | III |
| 8 | Econometría espacial: SAR, SEM, SDM y GWR | 14 | III | III |
| 9 | Geoestadística: variograma y kriging | 15 | III | III |
| 10 | ML espacial, datos espacio-temporales y proyecto integrador | 16 | Cierre | III |

La **semana 5** es el parcial 1 y no consume capítulo. La **semana 10** (aplicaciones de patrones
puntuales + formulación del proyecto integrador) cierra el cap. 5, con el enunciado del proyecto
remitido al cap. 10, donde vive la rúbrica. La **semana 11** combina el parcial 2 con la apertura
del Módulo III (*spatial weights lab*), que es exactamente el cap. 6.
**Cobertura: 16 de 16 semanas, sin huecos.**

---

## 6. Contenido capítulo por capítulo

Cada capítulo: **12 módulos**, el último siempre autoevaluación + ejercicios guiados. Objetivo por
capítulo: **8–12 simuladores, 8 preguntas de los cuatro tipos con retroalimentación por opción,
4 ejercicios guiados, 20–30 pares de pestañas R/Python**.

---

### Capítulo 1 — Datos espaciales y la primera ley de la geografía · semana 1

**Idea que sostiene el capítulo:** la independencia es un supuesto, no un hecho, y en el espacio es
casi siempre falso.

| # | Módulo | Contenido clave |
|---|---|---|
| 1 | El mapa que cambió la epidemiología | Snow, Broad Street 1854: el patrón puntual como argumento causal |
| 2 | Los tres tipos de dato espacial | Patrón puntual, dato de área, dato geoestadístico: **qué es aleatorio en cada uno** |
| 3 | La primera ley de Tobler | Formulación, evidencia y contraejemplos |
| 4 | Por qué se rompe la inferencia clásica | El e.e. ingenuo bajo autocorrelación: cuánto se subestima, **medido** |
| 5 | Tamaño de muestra efectivo | Cuánta información hay de verdad en n observaciones correlacionadas |
| 6 | Estacionariedad e isotropía | Y el problema fundamental: **una sola realización** del proceso |
| 7 | Escala, soporte y agregación | Primera pincelada del MAUP (se desarrolla en el cap. 3) |
| 8 | El ecosistema de R espacial | `sf`, `spatstat`, `spdep`, `gstat`, `tmap`: qué hace cada uno y cuándo |
| 9 | Anatomía de un objeto `sf` | Geometría + atributos; `sfg` / `sfc` / `sf`; y el `ppp` de spatstat |
| 10 | Dependencia espacial en ciencia de datos | Por qué la CV aleatoria infla el desempeño; H3 y geohash |
| 11 | Glosario de notación del curso | `.glosario-notacion` — la notación unificada de los 10 capítulos |
| 12 | Autoevaluación y ejercicios guiados | 8 preguntas + 4 ejercicios |

**Simuladores (8):** los tres tipos de dato lado a lado · campo gaussiano con correlación
regulable · e.e. ingenuo vs. correcto en función de ρ · tamaño efectivo de muestra · Snow
(`.geomapa` modo puntos) · una realización vs. muchas · agregación y escala · árbol de decisión del
curso (`.arbol-*`).

**Datos:** `HistData::Snow.deaths` / `Snow.pumps` / `Snow.streets` / `Snow.polygons` /
`Snow.dates` · `spatstat.data` `bei`, `japanesepines`, `redwood`, `cells` · `sf::nc` ·
**`sp::meuse`** · **y el trío colombiano de T0.4** (sedes de Bogotá, deserción municipal,
estaciones del IDEAM). *Decisión de Javier del 2026-08-04:* el módulo 2 presenta **cada tipo de
dato dos veces**, con su canónico y su gemelo colombiano, para que el hilo del país arranque en la
semana 1 y el estudiante pueda además contrastar los canónicos contra Baddeley, Bivand y Cressie.

**Fórmulas:** Tobler · Cov(Z(sᵢ), Z(sⱼ)) = C(h) · Var(Z̄) con correlación · n_eff · condiciones de
estacionariedad de segundo orden e intrínseca.

**Riesgo propio:** el módulo 4 tiene que **medir** la subestimación del e.e., no afirmarla. Va con
simulación de Monte Carlo y error de Monte Carlo publicado.

---

### Capítulo 2 — SIG, sistemas de referencia y georreferenciación con `sf` · semanas 2–3

**Idea que sostiene el capítulo:** un CRS mal puesto no da error, da un resultado equivocado con
buena cara.

| # | Módulo | Contenido clave |
|---|---|---|
| 1 | La Tierra no es plana ni una esfera | **Qué es un SIG** (Simple Features, vector vs. ráster, por qué `sf` y no QGIS); geoide, elipsoide, datum; WGS84 vs. MAGNA-SIRGAS |
| 2 | Latitud y longitud no son coordenadas cartesianas | Un grado de longitud en Bogotá, en Oslo y en el ecuador |
| 3 | Proyectar es elegir qué destruir | Conforme, equivalente, equidistante; indicatriz de Tissot |
| 4 | EPSG en la práctica | 4326 · 3857 y sus pecados · **3116 y 9377 para Colombia** |
| 5 | `st_transform` vs. `st_set_crs` | Reproyectar ≠ reetiquetar. **El error nº 1 de los LLM** (syllabus, sem. 13) |
| 6 | Medir sobre la Tierra | `st_area`, `st_distance`, geodésicas vs. euclídeas; s2 vs. GEOS |
| 7 | Formatos vectoriales | Shapefile y sus cinco limitaciones · GeoPackage · GeoJSON |
| 8 | De un CSV a un objeto `sf` | `st_as_sf`; **la trampa del orden lon/lat** |
| 9 | Geocodificación por dirección | Tasas de acierto y **el sesgo de la geocodificación**: no acierta igual en todos los barrios |
| 10 | Validación topológica | `st_is_valid`, `st_make_valid`, autointersecciones; predicados DE-9IM |
| 11 | Ingeniería de datos geoespaciales | Índices espaciales, `st_join`, H3/geohash en flujos masivos |
| 12 | Autoevaluación y ejercicios guiados | |

**Simuladores (10):** el mundo bajo 6 proyecciones con **distorsión de área y de ángulo medida**
(`.geomapa` modo proyeccion) · indicatriz de Tissot · longitud de un grado según la latitud ·
distancia euclídea sobre lon/lat vs. geodésica, con el error en km · `st_set_crs` mal usado, sobre
el mapa · lon/lat invertidos (el punto que aterriza en el océano) · polígono con autointersección
antes y después de `st_make_valid` · el buffer que cambia de tamaño según el CRS · predicados
DE-9IM interactivos · join espacial paso a paso.

**Datos:** `spData::world` · `sf::nc` · **límites de Colombia (hilo colombiano, entra aquí)**.

**Riesgo propio:** este capítulo es el más propenso a afirmaciones plausibles y falsas ("el error es
pequeño"). Toda comparación de distancias y áreas se calcula, se tabula y se cita.

---

### Capítulo 3 — Cartografía estadística y el MAUP · semana 4

**Idea que sostiene el capítulo:** el mismo dato produce mapas que dicen cosas opuestas, y elegir el
mapa es una decisión de modelado, no de presentación.

| # | Módulo | Contenido clave |
|---|---|---|
| 1 | Del dato al mapa | Qué decisiones hay dentro de un coropleto |
| 2 | Normalizar o mentir | Conteos vs. tasas: **el mapa de conteos es siempre el mapa de la población** |
| 3 | Esquemas de clasificación | Intervalos iguales, cuantiles, Jenks/Fisher, desviación estándar, head/tails |
| 4 | El mismo dato, cinco mapas | Comparación directa de los cinco esquemas sobre un mismo mapa |
| 5 | Color | Secuencial, divergente, cualitativo; ColorBrewer; daltonismo |
| 6 | `tmap` | Gramática de mapas temáticos; equivalencia con `ggplot2` y con GeoPandas |
| 7 | Más allá del coropleto | Símbolos proporcionales, cartogramas, dot density, hexbin |
| 8 | MAUP I — efecto escala | La correlación **cambia** al cambiar el nivel de agregación |
| 9 | MAUP II — efecto zonificación | Misma escala, distinta partición, distinto resultado; *gerrymandering* |
| 10 | La falacia ecológica | Robinson (1950): correlación entre agregados ≠ correlación entre individuos |
| 11 | Cartografía y ética | *Redlining*, mapas de riesgo, vigilancia predictiva ← **RAC dimensión Compromiso/Valoración** |
| 12 | Autoevaluación y ejercicios guiados | |

**Simuladores (10):** **clasificador de coropletos** (5 esquemas × k clases sobre el mismo mapa —
el simulador estrella del capítulo) · conteos vs. tasas · paletas y simulación de daltonismo ·
MAUP efecto escala · MAUP efecto zonificación con **distribución de la correlación sobre 1 000
particiones aleatorias** · falacia ecológica (nube individual vs. nube agregada) · cartograma ·
dot density vs. coropleto · símbolos proporcionales · *gerrymandering* con partición manual.

**Riesgo propio:** el módulo 11 tiene que ser análisis, no editorial. Casos documentados con fuente,
y la lección técnica —el sesgo entra por la unidad geográfica— por delante del juicio.

---

### Capítulo 4 — Patrones puntuales: descripción, CSR y funciones de resumen · semanas 6–7

| # | Módulo | Contenido clave |
|---|---|---|
| 1 | Qué es un proceso puntual | El objeto `ppp` y **por qué la ventana de observación importa tanto** |
| 2 | Intensidad λ | Homogénea vs. inhomogénea; el estimador por conteo |
| 3 | Los tres regímenes | Aleatorio, regular, agregado: `japanesepines`, `cells`, `redwood` |
| 4 | CSR | El proceso de Poisson homogéneo y sus dos propiedades definitorias |
| 5 | Test de cuadrantes | χ², sus supuestos y **su ceguera**: dos patrones distintos con el mismo χ² |
| 6 | El tamaño del cuadrante | Índice de dispersión; **esto es el MAUP otra vez** |
| 7 | Distancias al vecino más próximo | Función G y función F (espacio vacío); qué distingue a cada una |
| 8 | La función K de Ripley | Y su transformación L; qué mide realmente |
| 9 | La correlación de pares g(r) | Por qué g es más legible que K: K es acumulativa y arrastra |
| 10 | Efectos de borde | Correcciones isotrópica, de traslación y de Ripley; qué pasa si se ignoran |
| 11 | Envolventes de simulación | **Qué NO es un p-valor de envolvente**; inspección múltiple y test de desviación global |
| 12 | Autoevaluación y ejercicios guiados | |

**Simuladores (11):** generador de patrones (Poisson / Strauss / Thomas con parámetros) que muestra
**G, F, K y g en vivo** · cuadrantes con tamaño regulable y su χ² · dos patrones con el mismo χ² ·
G/F sobre los tres regímenes · K vs. L · K vs. g sobre el mismo patrón · corrección de borde
activable · envolventes con `nsim` regulable · el p-valor de la envolvente vs. el test global ·
efecto de la ventana sobre λ̂ · patrón colombiano (`.geomapa` modo puntos).

**Datos:** `spatstat.data`: `japanesepines`, `cells`, `redwood`, `swedishpines`, `bei`, `lansing`,
`chorley` · + el patrón puntual colombiano del hilo.

**Riesgo propio:** las envolventes son caras. Todas se precalculan en R y se incrustan; el simulador
interpola entre valores precalculados de `nsim`, no simula en el navegador.

---

### Capítulo 5 — Intensidad por núcleos y modelamiento de procesos puntuales · semanas 8–9

| # | Módulo | Contenido clave |
|---|---|---|
| 1 | De contar a suavizar | El estimador núcleo de la intensidad |
| 2 | El núcleo importa poco, el ancho de banda lo es todo | Comparación directa |
| 3 | Selectores de ancho de banda | `bw.diggle`, `bw.ppl`, `bw.scott`, `bw.CvL`: **qué optimiza cada uno** |
| 4 | Corrección de borde en la KDE | Y el problema de la ventana otra vez |
| 5 | KDE como mapa de calor | Análisis de demanda y localización de servicios ← caso Demirel et al. (sem. 13) |
| 6 | Intensidad relativa y riesgo relativo | Casos y controles; el cociente de intensidades |
| 7 | Covariables | `rhohat`: la intensidad como función de una covariable |
| 8 | El proceso de Poisson inhomogéneo | El modelo y su verosimilitud |
| 9 | `ppm` | Ajuste por Berman–Turner; lectura de los coeficientes |
| 10 | Diagnóstico del ajuste | Residuos, K inhomogénea, envolventes **sobre el modelo ajustado** |
| 11 | Procesos de conglomerado y autoexcitados | Thomas, Matérn, Cox log-gaussiano; **Hawkes en fraude y sismología** (conexión DS) |
| 12 | Autoevaluación y ejercicios guiados | |

**Simuladores (10):** KDE con ancho de banda deslizante (`.geomapa` modo rejilla) · los cuatro
selectores sobre el mismo patrón · núcleo gaussiano vs. Epanechnikov · corrección de borde
activable · riesgo relativo casos/controles · `rhohat` sobre la elevación de `bei` · Poisson
inhomogéneo simulado desde una covariable · residuos del `ppm` · Thomas con κ, σ, μ regulables ·
Hawkes unidimensional (llegada de eventos autoexcitados).

---

### Capítulo 6 — Datos de área y la matriz de pesos espaciales · semanas 10–11

**Idea que sostiene el capítulo:** W es la decisión más consecuente y la menos justificada del
análisis de datos de área.

| # | Módulo | Contenido clave |
|---|---|---|
| 1 | El dato de área | Qué se observa y qué es aleatorio en un retículo |
| 2 | Vecindad | La decisión que condiciona todo lo que viene después |
| 3 | Contigüidad | Torre y reina; contigüidad de orden superior |
| 4 | k vecinos más próximos | Siempre k, **simetría rota**, y qué implica |
| 5 | Umbral de distancia | Islas, densidad desigual y el umbral mínimo conexo |
| 6 | Vecindades geométricas | Delaunay, esfera de influencia, grafo de Gabriel |
| 7 | De vecinos a pesos | Estilos B, W, S, C, U: **qué cambia en la interpretación**, no solo en el número |
| 8 | El flujo de `spdep` | `poly2nb`, `knn2nb`, `dnearneigh`, `nb2listw`; y `sfdep` como interfaz tidy |
| 9 | Islas y `zero.policy` | Qué hace R con una unidad sin vecinos y por qué a veces engaña |
| 10 | El rezago espacial Wy | La media de los vecinos; interpretación y mapa |
| 11 | **W es la matriz de adyacencia de un grafo** | GNN, paso de mensajes; estandarizar por filas = normalizar por grado (conexión DS) |
| 12 | Autoevaluación y ejercicios guiados | |

**Simuladores (10):** **constructor de W** — elegir criterio y ver el grafo dibujado sobre el mapa
(`.geomapa` modo grafo), con histograma del número de vecinos · reina vs. torre, dónde difieren ·
k variable · umbral de distancia y el umbral mínimo conexo · Delaunay/Gabriel/esfera ·
comparador de estilos B/W/S · Wy sobre el mapa · islas y `zero.policy` · conectividad y
componentes · W como matriz (retícula de la matriz junto al mapa).

**Datos:** **`spdep::oldcol`** (`COL.OLD` + `COL.nb`, el de los ejemplos de Anselin) · `sf::nc` ·
`spData::us_states`, `spData::auckland` · + los polígonos colombianos del hilo.

---

### Capítulo 7 — Autocorrelación espacial global y local · semanas 12–13

| # | Módulo | Contenido clave |
|---|---|---|
| 1 | La pregunta | ¿Lo cercano se parece más de lo que cabría esperar por azar? |
| 2 | El índice de Moran I | Fórmula, E[I] = −1/(n−1), y **su rango real no es [−1, 1]** |
| 3 | Inferencia | Normalidad, aleatorización y permutación de Monte Carlo: cuál usar y cuándo |
| 4 | El diagrama de dispersión de Moran | Cuatro cuadrantes; **la pendiente de MCO de Wz sobre z ES I** — con z tipificada y W estandarizada por filas |
| 5 | La c de Geary | Qué mide distinto; relación inversa con I y cuándo discrepan |
| 6 | Correlograma y join count | I por orden de vecindad; el caso de la variable binaria |
| 7 | Moran es sensible a W | El mismo dato con distintas W da conclusiones distintas: **honestidad metodológica** |
| 8 | Del global al local | La descomposición de Anselin; LISA |
| 9 | El mapa de clústeres LISA | Alto-alto, bajo-bajo, alto-bajo, bajo-alto |
| 10 | **La trampa de la multiplicidad** | Bonferroni y FDR: el mapa LISA "significativo" por defecto **miente** |
| 11 | Getis-Ord Gᵢ y Gᵢ\* | Miden **intensidad**, no similitud; puntos calientes y fríos; en qué difieren de LISA |
| 12 | Autoevaluación y ejercicios guiados | |

**Simuladores (11):** Moran con autocorrelación controlada + su diagrama de dispersión · histograma
de I bajo H₀ por permutación, con `nsim` regulable · normalidad vs. aleatorización vs. permutación ·
el diagrama de Moran clicable (señalar un punto → resaltar la unidad en el mapa) · Geary vs. Moran
cuando discrepan · correlograma · **el mismo dato bajo 6 W distintas**, con I y su p-valor ·
LISA con **corrección de multiplicidad conmutable** (el mapa cambia al conmutar) · Gᵢ\* vs. LISA
lado a lado · join count · potencia del test frente a ρ y a n.

**Datos:** **`spData::getisord`** (los datos originales del artículo de Getis-Ord) ·
`spData::auckland` (el canónico de LISA) · `spdep::oldcol` · `sf::nc` · + el hilo colombiano.

**Riesgo propio:** el módulo 10 es el que más fácil sale mal. Se implementa contra
`spdep::localmoran_perm` con `p.adjust.method`, y las cifras se contrastan con las de GeoDa
documentadas en Anselin & Rey.

---

### Capítulo 8 — Econometría espacial: SAR, SEM, SDM y GWR · semana 14

**Idea que sostiene el capítulo:** en un modelo con Wy, **β no es el efecto marginal**. Es el punto
que más se enseña mal en todo el curso.

| # | Módulo | Contenido clave |
|---|---|---|
| 1 | Por qué MCO falla | Residuos autocorrelacionados, e.e. subestimados, inferencia rota |
| 2 | Diagnóstico | Moran sobre los residuos de MCO |
| 3 | Tres orígenes de la dependencia | Interacción sustantiva · variable omitida espacial · error de medida y escala. **Cada uno lleva a un modelo distinto** |
| 4 | El modelo de retardo espacial (SAR/SLM) | y = ρWy + Xβ + ε; endogeneidad de Wy; por qué MCO es inconsistente; ML e IV |
| 5 | El modelo de error espacial (SEM) | u = λWu + ε; qué se pierde y qué se conserva |
| 6 | El modelo de Durbin (SDM) | y = ρWy + Xβ + WXθ + ε; por qué LeSage & Pace lo proponen como punto de partida |
| 7 | La estrategia LM | LMerr, LMlag y sus versiones robustas; el árbol de decisión de Anselin (`.arbol-*`) |
| 8 | **Efectos directos, indirectos y totales** | El multiplicador (I − ρW)⁻¹; el efecto de retroalimentación sobre uno mismo |
| 9 | Comparar y validar | AIC, verosimilitud, Moran de los residuos del modelo espacial |
| 10 | Heterogeneidad espacial | Los coeficientes no tienen por qué ser constantes; regímenes espaciales; test de Chow espacial |
| 11 | GWR | Ancho de banda fijo vs. adaptativo, CV y AICc; **y sus críticas**: multicolinealidad local e inferencia dudosa |
| 12 | Autoevaluación y ejercicios guiados | |

**Simuladores (10):** datos generados con ρ conocido → **el sesgo de MCO medido** · Moran de los
residuos · árbol LM interactivo · SAR vs. SEM vs. SDM sobre el mismo dato · **el multiplicador
espacial**: un choque en una unidad propagándose por el mapa, orden a orden (`.geomapa`) · efectos
directo/indirecto/total según ρ · el sesgo de leer β como efecto marginal · GWR con ancho de banda
deslizante → mapa de coeficientes · GWR vs. regímenes espaciales · multicolinealidad local de la GWR.

**Datos:** **`spdep::oldcol`** (el canónico de Anselin, cifras contrastables contra el libro) ·
`spData::boston` · `spData::house`, `spData::baltimore` · + el hilo colombiano.

---

### Capítulo 9 — Geoestadística: variograma y kriging · semana 15

| # | Módulo | Contenido clave |
|---|---|---|
| 1 | El dato geoestadístico | Z(s) existe en todo punto y se observa en n |
| 2 | Estacionariedad de 2.º orden e intrínseca | Covarianza y semivariograma |
| 3 | γ(h) = C(0) − C(h) | Y por qué el variograma es más general que la covarianza |
| 4 | El variograma empírico | Nube, agrupamiento por lag; Matheron vs. el robusto de Cressie–Hawkins |
| 5 | Pepita, meseta y rango | Qué significa cada uno; **la pepita = error de medida + microescala** |
| 6 | Anisotropía | Geométrica y zonal; variograma direccional y mapa de variograma |
| 7 | Modelos teóricos válidos | Esférico, exponencial, gaussiano, Matérn; **por qué no vale cualquier función** |
| 8 | Ajuste | Mínimos cuadrados ponderados (`fit.variogram`); y por qué el ajuste a ojo sigue siendo defendible |
| 9 | Kriging ordinario | El sistema, el multiplicador de Lagrange, BLUP; **la varianza de kriging no depende de los valores observados** |
| 10 | Kriging universal y con deriva externa | La tendencia como parte del modelo |
| 11 | Validación cruzada y procesos gaussianos | LOO, z estandarizado; **kriging = regresión por procesos gaussianos** (conexión DS) |
| 12 | Autoevaluación y ejercicios guiados | |

**Simuladores (11):** constructor de variograma (modelo + pepita/meseta/rango → curva) ·
variograma empírico con ancho de lag regulable · Matheron vs. Cressie–Hawkins con un atípico ·
variograma direccional y mapa de variograma · **kriging interactivo**: mover parámetros → mapa de
predicción y **mapa de varianza** lado a lado (`.geomapa` modo rejilla) · la varianza de kriging no
mira los datos (demostración) · efecto de la pepita sobre el suavizado · kriging ordinario vs.
universal · kriging vs. IDW vs. vecino más próximo por CV · anisotropía sobre el mapa · el
variograma de un proceso gaussiano simulado con rango conocido.

**Datos:** **`sp::meuse`** (el canónico, 155 obs) · **`gstat::jura`**, `gstat::coalash`,
`gstat::walker` · + estaciones colombianas del hilo.

---

### Capítulo 10 — ML espacial, datos espacio-temporales y proyecto integrador · semana 16

| # | Módulo | Contenido clave |
|---|---|---|
| 1 | La CV aleatoria miente | Con datos espaciales, el desempeño estimado está inflado. **Medido, no afirmado** |
| 2 | Por qué | Autocorrelación → fuga de información entre entrenamiento y prueba |
| 3 | CV espacial | Bloques, clústeres, buffer/LOO espacial; `blockCV` y `spatialsample` |
| 4 | El tamaño del bloque | **El rango del variograma como guía** — cierra el círculo con el cap. 9 |
| 5 | Extrapolación espacial | Área de aplicabilidad: predecir donde no hay datos |
| 6 | Predictores espaciales | Coordenadas, distancias a rasgos, buffers, RF espacial, *regression kriging* |
| 7 | Datos espacio-temporales | El cubo; `stars`; el variograma espacio-temporal |
| 8 | Modelos espacio-temporales | Separables y no separables; pincelada de INLA/SPDE |
| 9 | Síntesis del curso | El árbol de decisión completo: qué método, para qué pregunta, con qué dato (`.arbol-*`) |
| 10 | Ética y cierre | Sesgo espacial en sistemas de decisión; el MAUP como decisión de modelado; declaración del uso de IA |
| 11 | **El proyecto integrador** | Enunciado completo + **rúbrica analítica** (`.rubrica`) |
| 12 | Autoevaluación final y ejercicios guiados | Repaso transversal de los 10 capítulos |

**Simuladores (8):** CV aleatoria vs. por bloques, con **la diferencia de RMSE medida** · tamaño de
bloque vs. rango del variograma · las tres estrategias de CV espacial sobre el mapa (`.geomapa`) ·
área de aplicabilidad · *regression kriging* vs. RF a secas · el cubo espacio-temporal · variograma
espacio-temporal · árbol de decisión final del curso.

---

## 7. Fases y tareas

Convención de tareas de capítulo, heredada de Diseño de Experimentos: **T*n*.1 precálculo →
T*n*.2 ensamblado → T*n*.3 verificación y publicación**.

---

### Fase 0 — Fundamentos (nada de contenido todavía)

**T0.1 — Entorno y arnés de reproducibilidad** · *Alcance: S* · *Dependencias: ninguna*
Instalar en R 4.4-arm64 los **18 paquetes** que faltan (todos con binario arm64 verificado, ninguno
compila) y crear el entorno de Python geoespacial en mamba. Escribir `precalculo/entorno.R` y
`precalculo/entorno.py`, que fijan semilla, imprimen y **congelan las versiones** en
`precalculo/versiones.json`.
- **Criterios:** los 18 paquetes de R cargan; los 9 de Python importan; `versiones.json` registra R,
  GDAL, GEOS, PROJ y cada paquete con su versión. `spDataLarge` resuelto o declarado descartado.
- **Verificación:** un script que carga todo y ejecuta un cálculo mínimo por paquete
  (`poly2nb`, `variogram`, `Kest`, `errorsarlm`, `gwr.basic`, `cv_spatial`) sobre datos de juguete.
- **Trampa conocida:** el `Rscript` del `PATH` **no sirve**. Todo el precálculo invoca la ruta
  absoluta de R 4.4-arm64.

**T0.2 — Plantilla del curso** · *Alcance: M* · *Dependencias: T0.1*
Copiar la plantilla de Diseño de Experimentos, cambiar textos meta (título, cabecera, pie,
keywords, paleta), e **injertar `.glosario-notacion` y `.rubrica`** desde los capítulos 1 y 8 de
Muestreo.
- **Criterios:** la plantilla abre sin errores de consola; los 133 selectores de la de DOE siguen
  presentes; los dos componentes injertados se pintan sobre un div vacío.
- **Verificación:** `node --check` sobre el JS extraído; comparación del **conjunto de selectores**
  contra la plantilla de origen; apertura en el navegador con los dos componentes de prueba.

**T0.3 — El componente `.geomapa`** · *Alcance: L — es la tarea de más riesgo del plan* · *Dep.: T0.2*
Escribir el pintor de canvas con sus cinco modos, más `precalculo/geo.R`: la cadena
proyectar → simplificar → normalizar → serializar, con presupuesto de vértices.
- **Criterios:** los cinco modos pintan; la **relación de aspecto se respeta** (verificada midiendo
  el lienzo); la leyenda muestra los cortes que calculó R; el mapa se redibuja al mover un control
  sin recrear el canvas; se destruye al cambiar de módulo; `role="img"` con `aria-label` y tabla de
  respaldo; geometría ≤ 120 KB por capítulo.
- **Verificación:** capítulo de prueba con los cinco modos; consola limpia; `getBoundingClientRect`
  confirma la relación de aspecto y que no hay desbordamiento a 375 px ni a 1 280 px; 0 gráficos
  huérfanos tras 20 cambios de módulo.
- **Y además:** actualizar la plantilla en la misma tarea. Un componente no está terminado hasta
  que está en la plantilla.

**T0.4 — El hilo colombiano de datos** · *Alcance: M* · *Dependencias: T0.1* · ✅ **HECHA (2026-08-03)**
Elegir, descargar, verificar y congelar los datos abiertos colombianos: **un conjunto de polígonos**
(candidatos: municipios del MGN del DANE, o UPZ / sectores catastrales de Bogotá), **un patrón
puntual** y **un conjunto de puntos con un valor continuo** para geoestadística.
- **Entregado:** 1 122 municipios + 33 departamentos (MGN/DANE) · 2 209 sedes educativas de Bogotá
  con **dos ventanas** de observación (SED/SDP) · 361 estaciones del IDEAM con temperatura y
  altitud · 1 065 436 microdatos de Saber 11 (ICFES). Scripts: `datos_colombia.R`,
  `llave_divipola.R`, `datos_bogota.R`, `datos_clima.R`, `datos_saber11.R`, más `fuentes.R`
  (con `carga_municipios()`: geometría única + atributos en CSV).
  Procedencia en `precalculo/FUENTES.md` y `datos/procesado/procedencia.json`.
- **Auditoría:** `verifica_t04.R` **90/90**; `prueba_verifica_t04.R` caza **17/17** defectos
  inyectados. Ver **A.8** y **A.9**.
- **Criterios:** cada fuente con URL, licencia, fecha de corte y fecha de descarga **documentadas en
  el material**; ninguna fuente sin verificar; los polígonos leen sin geometrías inválidas (o se
  declara cómo se repararon); el conjunto de área tiene **n ≥ 50 unidades** (por debajo de eso,
  Moran y SAR no enseñan nada).
- **Verificación:** `st_is_valid` sobre todo; `precalculo/datos_colombia.R` reproduce los archivos
  desde el crudo; hoja de procedencia en `precalculo/FUENTES.md`.
- **Riesgo:** si ninguna fuente aguanta la verificación, se cae al plan B —solo datos canónicos— y
  **se avisa**, no se inventa.

**T0.5 — Arnés de auditoría** · *Alcance: M* · *Dependencias: T0.3* · ✅ **HECHA (2026-08-03)**
Portar de Diseño de Experimentos: `verifica_bloques.py`, `audita_texto.py`, `prueba_texto.py` y
`cuenta_sitio.py`. **Ninguno se pudo portar tal cual** — ver A.10.
- **Entregado:** `verifica_bloques.py` (R 4.4-arm64 + `geo_env`, y **un capítulo sin `#>` es fallo,
  no aprobado**) · **`audita_texto_base.py`**, núcleo compartido de 10 familias, + una espec corta
  por capítulo (`audita_texto_demo.py` es el molde) · `prueba_texto.py` con **36 inyecciones** ·
  `cuenta_sitio.py` con desglose de modos del `.geomapa` · `mide_punto_ciego.py` ·
  **`utf8.R` + `rscript.sh`**, que cierran de raíz las dos trampas del entorno ·
  **regla de publicación: toda cifra de la que el texto argumenta lleva ≥ 5 decimales** ·
  `audita_todo.sh` como punto de entrada único.
- **Banco de pruebas:** `genera_demo_auditoria.R` → `ensambla_demo_auditoria.py` →
  `Htmls_Espacial/prueba-auditoria.html`, capítulo-fixture de 6 módulos con cifras espaciales
  **reales** (Moran, λ de las dos ventanas, gradiente del IDEAM, Columbus, `nc`). Reproducible
  **byte a byte**.
- **Resultados:** `verifica_bloques` **37/37** · `audita_texto` **76 comprobaciones, 0 fallos** ·
  `prueba_texto` **36/36**, y **ninguna familia de comprobación queda sin una instancia probada** ·
  sin desbordamiento a 375 ni a 1 280 px, 0 gráficos huérfanos, consola limpia.
- **Y encontró un defecto real en trabajo ya auditado:** T0.4 corría con `LC_CTYPE=C` y
  **295 724 estudiantes desaparecían en silencio** de la falacia ecológica. T0.4 regenerada y de
  vuelta en **90/90**. Ver **A.10**.
- **Criterios:** los cuatro corren sobre la plantilla sin falsos positivos; el arnés de inyección
  detecta **el 100 %** de las cifras falsas inyectadas.
- **Verificación:** inyectar 10 cifras falsas —**que no existan ya en el archivo**— y comprobar que
  las 10 se cazan. Un verificador permisivo da falsa calma; es la lección de Muestreo.

### ✅ Checkpoint 0 — CERRADO (2026-08-03)
- [x] Este plan aprobado por Javier · [x] entorno reproducible (T0.1) · [x] plantilla del curso
  (T0.2) · [x] `.geomapa` funcionando en sus cinco modos (T0.3) · [x] **datos colombianos
  verificados** (T0.4: los tres tipos de dato, 90/90 en la auditoría, plan B **no** hizo falta)
  · [x] **auditores con inyección al 100 %** (T0.5: 36/36, con el fixture como sujeto y sin
  familias sin probar)

**La Fase 0 está cerrada. Arranca el capítulo 1 (T1.1).**

---

### Fase 1 — Capítulo 1 y validación del formato

**T1.1 — Precálculo del capítulo 1** · *Alcance: M* · *Dep.: Fase 0* · ✅ **HECHA (2026-08-04)**
`precalculo/genera_cap1.R` + los 4 ejercicios guiados en `genera_soluciones.R` + `audita_cap1.py` +
`prueba_auditor_cap1.py`.
- **Criterios:** todas las cifras del capítulo salen del JSON; el auditor cubre ≥ 300 comprobaciones;
  el arnés de inyección caza el 100 % de los defectos.
- **Verificación:** ejecutar `genera_cap1.R` dos veces y comparar los JSON byte a byte (semilla fija).
- **Cumplido:** cifras **todas** del JSON (D10) · auditor **836** comprobaciones, 0 fallos ·
  arnés **49/49** · los tres JSON **idénticos byte a byte** en dos ejecuciones
  (`prueba_reproducible.sh`, nuevo).
- **Cuatro decisiones que tomó Javier el 2026-08-04**, y que ensanchan el capítulo respecto del §6:
  1. **El hilo colombiano entra ya en el capítulo 1.** El módulo 2 presenta cada tipo de dato
     **dos veces**: el canónico de la literatura y su gemelo colombiano.
  2. **El módulo 4 mide por dos frentes**: Monte Carlo sobre campo gaussiano *y* réplica por
     remuestreo sobre la deserción municipal real.
  3. **El módulo 10 mide un caso pequeño aquí** y remite el desarrollo al capítulo 10.
     **Frontera repartida y declarada dentro del propio JSON** (`cv_espacial.frontera`), no solo
     en este plan: blockCV, `spatialsample`, tamaño de bloque guiado por el rango del variograma y
     área de aplicabilidad son del capítulo 10.
  4. **La prueba diagnóstica de la sesión 1 va DENTRO del capítulo 1**, como autoevaluación de
     entrada sin nota, aparte del quiz de 8 del módulo 12. Cierra la pregunta abierta nº 2 del §10.
- **Herramientas nuevas que quedan para todo el proyecto:**
  - `precalculo/prueba_reproducible.sh` — ejecuta un generador dos veces y compara byte a byte,
    con la única excepción declarada (`meta.generado`, la fecha).
  - `precalculo/audita_todo.sh` ampliado: ahora recorre los capítulos con precálculo y pasa su
    auditor y su arnés **antes** que los de prosa (auditar un texto contra un JSON equivocado es
    auditar nada), y acepta `--rapido` para saltarse los arneses de inyección.
  - `geo_puntos()` de `geo.R` acepta `lineas`, `puntos2`, `etiquetas2` y `resaltado2`.
    **Retrocompatible verificado:** `demo_geomapa.json` de T0.3 sale idéntico salvo la fecha.

> **⚠️ LO QUE T1.1 LE DEJA A T1.2, y hay que hacerlo antes de ensamblar el módulo 1.**
> El lado del navegador **no pinta todavía** lo que el mapa de Snow necesita:
> `geomapaPintaPuntos` (plantilla, ~línea 5548) dibuja `d.pts` de un solo color e **ignora
> `marcas`**, y no conoce `lineas` ni `puntos2`. Hay que añadir: capa de polilíneas de fondo (las
> 528 calles de Soho), segunda capa de puntos con símbolo propio (las 13 bombas), resaltado de una
> de ellas (Broad Street) y color por marca categórica (la celda de Thiessen de cada muerte).
> **Regla del §9: en la misma sesión hay que retropropagarlo a la plantilla y a
> `Htmls_Espacial/prueba-geomapa.html`.**

**T1.2 — Ensamblado del capítulo 1** · *Alcance: L* · *Dep.: T1.1* · ✅ **HECHA (2026-08-04)**
Los 12 módulos, 8 simuladores, 8 preguntas, 4 ejercicios guiados, glosario de notación.
- **Entregado:** `precalculo/ensambla_cap1.py` (2 474 líneas) →
  `Htmls_Espacial/capitulo-1-datos-espaciales.html`, **492 KB**. **9** simuladores (uno más de los 8
  del §6: el árbol de decisión y el correlograma entran los dos), **9** mapas, **16** preguntas de
  los **cuatro** tipos, 4 ejercicios guiados con su solución calculada en R, glosario de notación de
  13 símbolos y hoja de procedencia de los 9 conjuntos de datos.
- **El `.geomapa` terminado:** `lineas`, `puntos2` con símbolo propio y resaltado, `marcas`
  categóricas y numéricas con su leyenda, `marcas_tipo` declarado desde R. Retropropagado a la
  plantilla y a `prueba-geomapa.html`, que estrena dos casos permanentes.
- **Componente nuevo de la plantilla:** `envolverTablas()`, que envuelve cada tabla en un contenedor
  desplazable con `role="region"` — sin él, una tabla de seis columnas desbordaba la página a 375 px.

**T1.3 — Verificación y publicación del capítulo 1** · *Alcance: M* · *Dep.: T1.2* · ✅ **HECHA (2026-08-04)**
- **Criterios:** `verifica_bloques.py` **al 100 %**; `audita_texto_cap1.py` sin discrepancias;
  consola limpia; KaTeX sin avisos; los simuladores responden **también en valores extremos**;
  0 gráficos huérfanos; sin desbordamiento horizontal a 375 px.
- **Verificación:** recorrer **los 12 módulos** con la consola instrumentada. Un componente puede
  romperse en un solo módulo y dejar los otros perfectos.
- **Cumplido:** los 12 módulos recorridos con la consola instrumentada —**y ahí salió el defecto
  nº 2 de A.12**, que solo rompía el módulo 1—; consola limpia y KaTeX sin avisos en los doce;
  `geomapasVivos` nunca por encima del número de lienzos en **60 cambios de módulo**; sin
  desbordamiento a 1 280 px ni con el contenedor forzado a **318 px**; `audita_texto_cap1.py`
  **139/0** y su arnés **29/29**.

### ✅ Checkpoint 1 — CERRADO (2026-08-04)
**Javier revisó el capítulo 1 y lo aprobó en bloque**, después de la corrección de ritmo del módulo 1
del §9.1: «me parece bien como está el material». Los cuatro puntos que había que decidir quedan
aprobados tal como están:
- [x] Nivel de la explicación — el patrón «concreto → formal» se queda como está; **no hay que
      retropropagar nada**, a diferencia de Muestreo, donde hubo que rehacer 22 módulos
- [x] Densidad de simuladores y de mapas — **9 y 9** en doce módulos
- [x] El `.geomapa` se ve y se entiende como esperaba
- [x] Proporción R/Python — **8 bloques de cada uno**

**Consecuencias, y hay que respetarlas al escribir los capítulos 2–10:**
- **El capítulo 1 es el molde.** Los nueve siguientes copian su estructura, su densidad y su reparto
  de lenguajes; desviarse de ahí es una decisión que hay que declarar, no una elección libre.
- **El paso de ritmo interno de los doce módulos NO se hace.** Estaba declarado como pendiente en el
  §9.1 y esta aprobación lo cierra: el módulo 1 se queda con su alternancia actual. Lo que sí sigue
  vigente para todos los capítulos son las tres reglas del §9.1.
- **Queda desbloqueada la Fase 2.**

---

### Fase 2 — Corte I: capítulos 2 y 3

**T2.1 — Precálculo del capítulo 2** · *Alcance: L* · *Dep.: Checkpoint 1* · ✅ **HECHA (2026-08-04)**
`precalculo/genera_cap2.R` (12 módulos, **29 anclas** contra la literatura que **paran** el script),
la sección del capítulo 2 en `genera_soluciones.R` (**5** ejercicios), `audita_cap2.py`
(**426 comprobaciones, 0 fallos, 2 saltadas declaradas**, recalculando en Python con
pyproj/geopandas/shapely) y `prueba_auditor_cap2.py` (**91 inyecciones, 91 cazadas**).
- **Componente nuevo en `geo.R`: `geo_tissot()`**, que mide la indicatriz por diferencias finitas y
  SVD, con **tres anclas matemáticas que paran** (Mercator ω = 0, Mollweide s = 1, equirrectangular
  h = 1 y k = sec φ). El auditor la recalcula **con la trigonometría de Snyder**, que es el camino
  largo: dos implementaciones distintas de la misma matemática.
- **Salidas:** `cap2_datos.json` 17,4 KB, `cap2_mapas.json` **100,6 KB** (dentro del presupuesto de
  120), `cap2_soluciones.json` 15,1 KB, más tres CSV. **Reproducible byte a byte.**

**T2.2 — Ensamblado del capítulo 2** · *Alcance: L* · *Dep.: T2.1* · ✅ **HECHA (2026-08-04)**
`precalculo/ensambla_cap2.py` → `Htmls_Espacial/capitulo-2-crs-georreferenciacion.html`, **481 KB**.
- **Las dos desviaciones del molde, declaradas** (Checkpoint 1 exige declararlas): **12 preguntas**
  en vez de 8 —el quiz de 8 más un bloque de 4 «trampas de CRS» tras el módulo 6— y **5 ejercicios
  guiados** en vez de 4. Motivo: el capítulo cubre **dos semanas** de clase.
- **Retropropagado:** la capa de indicatrices en la plantilla y en `prueba-geomapa.html`, cuyo
  `demo_geomapa.json` estrena dos casos con Tissot; y **el capítulo 1 estrena su enlace al 2**.
- **Herramienta nueva: `precalculo/sincroniza_prueba_geomapa.py`**, que copia el motor de la
  plantilla al banco de pruebas y le repega el JSON. La regla del §9 dejaba de depender de que
  alguien se acordara.

**T2.3 — Verificación del capítulo 2** · *Alcance: M* · *Dep.: T2.2* · ✅ **HECHA (2026-08-04)**
- **Cumplido:** los 12 módulos recorridos con la consola instrumentada, **cero errores**;
  `verifica_bloques.py` **66 de 66 cifras** anunciadas presentes en la salida real;
  `audita_texto_cap2.py` **128/0** y su arnés **24/24**; sin desbordamiento horizontal a 1 280, 375
  ni **318 px**; `geomapasVivos` y `graficosActivos` acotados tras **40 cambios de módulo**; y la
  lectura de ritmo del §9.1 sobre los doce módulos.

**T2.4–T2.6 — Capítulo 3** (cartografía y MAUP) · *Alcance: L* · ✅ **HECHAS (2026-08-05)**

**Las cuatro decisiones de Javier del 2026-08-05**, tomadas antes de escribir una línea, y las
cuatro sobre la recomendación:

1. **Los módulos 8, 9 y 10 van sobre UN SOLO dato: los microdatos de Saber 11.** Es el único
   conjunto del proyecto con nivel individual, y sin nivel individual la falacia ecológica se
   afirma en vez de medirse. Habilita el simulador que da sentido al módulo 9: la partición
   departamental **real** contra 1 000 particiones aleatorias de los mismos 1 122 municipios en
   33 zonas — misma escala, distinta zonificación.
2. **Se instala `cartogram`** (0.3.0, primera dependencia nueva desde T0.1) **y además se
   implementan dos cartogramas a mano**: el no contiguo de Olson y el de Dorling, que tienen una
   propiedad *exacta* —el área resultante es proporcional al valor por construcción— y por tanto
   admiten una prueba que puede fallar. El contiguo de Dougenik sale del paquete.
3. **El módulo 11 lleva la estratificación socioeconómica colombiana como caso ancla**, más
   *redlining* y vigilancia predictiva como casos internacionales citados. La lección técnica va
   medida y por delante; el juicio, después.
4. **La simulación de daltonismo vive en el motor `.geomapa`**, no en un simulador suelto, y se
   **retropropaga** a la plantilla, a `prueba-geomapa.html` y a los capítulos 1 y 2.

**T2.4 — Precálculo del capítulo 3** · *Alcance: L* · ✅ **HECHA**
`precalculo/genera_cap3.R` (12 módulos, anclas que **paran**), la sección del capítulo 3 en
`genera_soluciones.R` (**4** ejercicios — vuelta al molde del capítulo 1, porque el 3 cubre **una
sola semana**), y cuatro piezas nuevas en `geo.R`.
- **Criterios:** todas las cifras salen del JSON (D10); el auditor cubre ≥ 300 comprobaciones; el
  arnés caza el 100 % de los defectos inyectados; los tres JSON salen idénticos byte a byte.
- **Verificación:** `prueba_reproducible.sh` sobre el generador; contraste R↔Python en `audita_cap3.py`.

**T2.4b — Auditor del precálculo y su arnés** · *Alcance: M* · ✅ **HECHA** — 354/0 y 56/56
`audita_cap3.py` sobre `audita_base.py`, recalculando en Python con geopandas, mapclassify y numpy;
`prueba_auditor_cap3.py`. La discrepancia de cuantiles R↔Python del **anexo A.2** entra como
discrepancia **declarada**, no como fallo.

**T2.5 — Ensamblado** · *Alcance: L* · ✅ **HECHA** — 621 KB
`precalculo/ensambla_cap3.py` → `Htmls_Espacial/capitulo-3-cartografia-maup.html`: 12 módulos,
~10 simuladores, **8 preguntas y 4 ejercicios** (el molde), 20–30 pares de pestañas R/Python.
Retropropagación del conmutador de daltonismo y de las capas nuevas del `.geomapa`.

**T2.6 — Verificación y cierre del Corte I** · *Alcance: M* · ✅ **HECHA** — 130/0 y 20/20
`audita_texto_cap3.py` + su arnés en `prueba_texto.py`; `verifica_bloques.py` al 100 %;
`audita_todo.sh` entero; los 12 módulos con la consola instrumentada **forzando `chart.draw()`**
(la trampa de A.13); sin desbordamiento a 1 280, 375 ni 318 px; lectura de ritmo del §9.1.

> **⚠️ DESVIACIÓN DE PRESUPUESTO, medida y declarada (2026-08-05).** El §4 fija ~120 KB de
> geometría por capítulo y afirma que «los 1 122 municipios simplificados a tolerancia visual» caben.
> **No caben, y ningún capítulo lo había probado**: el de Muestreo y los capítulos 1 y 2 usan la capa
> **departamental** (33 rasgos, 1 180 vértices). El suelo de `ms_simplify` con `keep_shapes = TRUE`
> es **estructural** —cada polígono conserva su anillo mínimo—, así que 1 122 rasgos no bajan de
> **12 500 vértices ≈ 150 KB**, con cualquier tolerancia. Ver **A.14**.

### ✅ Checkpoint 2 — Corte I cerrado (2026-08-05), a falta de tu revisión de contenido
- [x] **Semanas 1–4 cubiertas** — capítulos 1, 2 y 3 en pie
- [x] **Los tres capítulos comparten el mismo motor**: los capítulos 1 y 2 se regeneraron desde la
      plantilla con el `.geomapa` nuevo y se verificaron sin regresión (12 y 12 módulos recorridos,
      consola limpia, todos los mapas con tinta)
- [x] **Todo componente nuevo retropropagado** a la plantilla, a `prueba-geomapa.html` —que estrena
      un módulo 8 permanente con capas, diferencias y superpuestos— y a los dos capítulos hechos
- [ ] **Tu revisión de contenido del capítulo 3** — es lo único que queda

---

### Fase 3 — Corte II: capítulos 4 y 5 (patrones puntuales)

**T3.1–T3.3 — Capítulo 4** · *Alcance: L* — el precálculo de envolventes es el más caro del curso
**T3.4–T3.6 — Capítulo 5** · *Alcance: L*

### ✅ Checkpoint 3 — Módulo II cerrado
- [ ] Semanas 6–9 cubiertas · [ ] las envolventes precalculadas y sus `nsim` documentados

---

### Fase 4 — Corte III (1.ª parte): capítulos 6 y 7 (datos de área)

**T4.1–T4.3 — Capítulo 6** (matriz W) · *Alcance: L*
**T4.4–T4.6 — Capítulo 7** (Moran, Geary, LISA, G\*) · *Alcance: L*

### ✅ Checkpoint 4 — autocorrelación cerrada
- [ ] Cifras de LISA contrastadas contra las de GeoDa publicadas en Anselin & Rey
- [ ] El mapa LISA con y sin corrección de multiplicidad, ambos presentes en el material

---

### Fase 5 — Corte III (2.ª parte): capítulos 8 y 9

**T5.1–T5.3 — Capítulo 8** (SAR/SEM/SDM/GWR) · *Alcance: L*
**T5.4–T5.6 — Capítulo 9** (variograma y kriging) · *Alcance: L*

### ✅ Checkpoint 5
- [ ] Los efectos directos/indirectos calculados con `spatialreg::impacts`, no a mano
- [ ] Kriging verificado por dos vías (`gstat` ↔ el sistema resuelto explícitamente)

---

### Fase 6 — Cierre: capítulo 10 y proyecto integrador

**T6.1–T6.3 — Capítulo 10** · *Alcance: L*
**T6.4 — Enunciado y rúbrica del proyecto integrador** · *Alcance: M*
Rúbrica analítica de 6 criterios × 4 niveles, en la línea de la de Muestreo, alineada con lo que el
syllabus evalúa: pertinencia del método espacial elegido, corrección técnica en R, interpretación,
calidad cartográfica, reproducibilidad y declaración del uso de IA.

---

### Fase 7 — Sitio y publicación

**EL REPOSITORIO, decidido por Javier el 2026-08-04:**
`https://github.com/JotaMao1985/Un_Bosque_Estadistica_Espacial.git` — **propio**, no el paraguas
`UnBosque_Teor` de Muestreo. Cierra la pregunta 1 del §10 y fija D11.

**EL PATRÓN ES EL DE SERIES DE TIEMPO** — ✅ **confirmado por Javier el 2026-08-04**, no es una
inferencia. Había dos precedentes incompatibles entre sus cursos y este cierra cuál manda: **NO se
sigue el de Diseño de Experimentos**, cuyo repo cuelga de `Htmls/`. Series de Tiempo ya está en vivo
y tiene exactamente esta forma (leída de su repo, no supuesta):

- **La raíz del repositorio es la carpeta del curso** (`Estadistica espacial/`), no `Htmls_Espacial/`.
  Es lo que hace falta para que el `.gitignore` de lista blanca de T7.2 pueda excluir `datos/`, y es
  distinto de Diseño de Experimentos, donde el repo cuelga de `Htmls/`.
- **Dos ramas.** `main` lleva el material entero —plan, `precalculo/`, `plantilla/`, los HTML—;
  **`gh-pages` lleva SOLO el sitio publicado y en su raíz**: los diez `capitulo-*.html`, `index.html`,
  `.nojekyll` y `README.md`. Nada de `precalculo/` ni de `datos/` en la rama publicada.
- **URL en vivo prevista:** `https://jotamao1985.github.io/Un_Bosque_Estadistica_Espacial/`.

**T7.1 — Portada** (`index.html` con 10 tarjetas, base: la de Muestreo) · *Alcance: M*
- Al existir `index.html` al lado de los capítulos, **la comprobación de enlaces de
  `audita_texto_base.enlaces()` se arma sola** y empieza a exigir que cada capítulo enlace con el
  sitio. Está escrita así a propósito para no tener que acordarse. Ver A.12.
**T7.2 — `README.md`, `.nojekyll`, `.gitignore` de lista blanca, `git init` + `git remote add`** ·
*Alcance: S*
- **El `.gitignore` ya está escrito y verificado** (2026-08-05), en la raíz del curso. Sigue el molde
  de lista blanca de Muestreo —`/*` y luego `!/carpeta/`—, no el de Series de Tiempo, que es una
  lista negra. Se comprobó en un repositorio de ensayo que imita este árbol: `git add -A --dry-run`
  recoge **exactamente** `.gitignore`, `.nojekyll`, `README.md`, `index.html`, los dos `PLAN_*.md`,
  `Htmls_Espacial/`, `plantilla/`, `precalculo/` y `ensamblado/`, y **nada más**. Al hacer `git init`,
  reejecutar la comprobación contra el árbol definitivo, que para entonces tendrá `index.html` y los
  diez capítulos.
- **Trampa conocida:** el `.gitignore` de lista blanca se traga cualquier carpeta nueva sin su
  `!/carpeta/`. Comprobar con `git check-ignore -v`.
- **Trampa inversa, la que de verdad muerde:** lo reactivado con `!/carpeta/` vuelve a entrar
  ENTERO. Por eso el archivo excluye aparte tres cosas que caen dentro de `precalculo/`:
  `precalculo/cache/` y `*.rds` (33 MB de caché de cómputo del capítulo 3, que `genera_cap3.R`
  rehace solo si faltan), `__pycache__/` y la familia del shapefile.
- **Los shapefiles sueltos.** El 2026-08-05 había cuatro archivos `prueba.{shp,dbf,prj,shx}` —3,1 MB—
  en la raíz del curso, residuo de una versión vieja del módulo 7 del capítulo 2 (60 rasgos con la
  tabla de atributos entera; el generador de hoy escribe 20 rasgos y 5 columnas). **El generador ya
  es correcto**: `genera_cap2.R:567` escribe en `file.path(tempdir(), "fmt")`, así que no hay nada
  que arreglar ahí; los cuatro archivos se borraron. Lo que sí se hizo permanente es la exclusión
  `*.shp *.shx *.dbf *.prj *.cpg *.sbn *.sbx *.gpkg *.geojson`, que cubre el caso de ejecutar ese
  bloque a mano desde la raíz. Sin esas líneas, `!/precalculo/` y `!/Htmls_Espacial/` los dejarían
  pasar.
- **Lo que NO entra al repositorio:** `datos/crudo/` (345 MB) y `datos/procesado/` (86 MB). Y por el
  precedente de Series de Tiempo, **tampoco los PDF de los textos guía**: el repo es público y subir
  un libro escaneado es redistribución no autorizada, además de inflar el historial. `*.pdf` se lleva
  de paso el `Rplots.pdf` de 8 MB que Rscript deja en la raíz al abrir un dispositivo gráfico sin
  nombre de archivo.
**T7.3 — Publicación y verificación en vivo** · *Alcance: S*
- **Trampa conocida:** comprobar `chmod 644` en los HTML publicados; en `gh-pages` un archivo en
  600 es un 404.
**T7.4 — Auditoría final independiente** (subagente) · *Alcance: M*
Lectura completa del material por un auditor que no lo escribió: cifras, fórmulas, cobertura del
syllabus y accesibilidad.

### ✅ Checkpoint 6 — listo para los estudiantes
- [ ] 10 capítulos en vivo · [ ] 16/16 semanas cubiertas · [ ] auditoría sin hallazgos objetivos
  abiertos · [ ] revisión de contenido tuya

---

## 8. Totales objetivo

| Métrica | Objetivo |
|---|---|
| Capítulos | 10 |
| Módulos | 120 |
| Simuladores | ~99 |
| Mapas interactivos (`.geomapa`) | ~35 |
| Preguntas de autoevaluación | 80, de los 4 tipos, **cada opción con su retroalimentación** |
| Ejercicios guiados | 40, con solución **calculada en R** |
| Pares de pestañas R/Python | 200–300 |
| Peso por capítulo | 350–550 KB |

Los totales finales **no se escriben a mano**: los cuenta `precalculo/cuenta_sitio.py` sobre los
archivos publicados.

---

## 9. Riesgos

| Riesgo | Impacto | Mitigación |
|---|---|---|
| **El `.geomapa` es un componente nuevo y no trivial** | **Alto** | Se construye entero y se prueba en T0.3, **antes** del capítulo 1; cinco modos con criterios de aceptación explícitos |
| La geometría inline infla los capítulos por encima de 1 MB | Medio | Presupuesto de 120 KB por capítulo, simplificación con tolerancia medida y verificación en T0.3 |
| Los datos abiertos colombianos no se verifican o la fuente cae | Medio | T0.4 los resuelve antes de escribir; plan B (solo canónicos) declarado, no improvisado |
| Cifras escritas de memoria | **Alto** | D10 + `audita_texto.py` con cobertura dentro de KaTeX; en Muestreo se colaron tres cifras **mientras se corregía justamente ese problema** |
| Un verificador permisivo da falsa calma | Alto | Arnés de inyección en T0.5 y en cada capítulo; la cifra inyectada **no puede existir ya en el archivo** |
| Precálculos caros (envolventes, GWR, CV por bloques) alargan las fases | Medio | Todo en R con caché de resultados; el navegador solo interpola valores ya calculados |
| `spDataLarge` sin binario | Bajo | Se resuelve en T0.1 o se prescinde: ningún capítulo depende de él |
| Saturación de conexiones con ciencia de datos | Medio | Máximo **un módulo de DS por capítulo**, el que ya está marcado en §6 |
| Clonar un capítulo con `sed` deja el `DESTINO` viejo | Medio | Leer siempre el nombre que imprime el ensamblador; en Muestreo el cap. 7 sobrescribió el 6 |
| Deriva entre capítulos (un componente nuevo en el cap. 7 y no en los anteriores) | Medio | Regla fija: componente nuevo → **retropropagar a los ya hechos y a la plantilla en la misma sesión** |
| Un bloque interactivo cortando el texto sin transición | Medio | **Regla del ritmo** (abajo): ningún módulo abre pidiendo trabajo, y todo componente va con su prosa de entrada y de salida |

### 9.1 · La regla del ritmo

Añadida el **2026-08-04** por un defecto real del módulo 1 del capítulo 1: la diagnóstica de entrada
estaba pegada al encabezado del módulo y se saltaba de la octava pregunta a «Londres, verano de 1854»
sin una palabra por medio. Dos defectos en uno —al lector se le pedía producir antes de haberle dado
nada, y el corte del cuestionario al relato no lo amortiguaba nadie—, y ninguna de las herramientas
lo veía: el ensamblador daba «limpio», el auditor de prosa 138/0 y la consola estaba impecable. **El
ritmo no lo caza ninguna comprobación automática; hay que leer el módulo como lo lee un estudiante.**

Tres reglas, para los diez capítulos:

1. **Ningún módulo abre pidiendo trabajo.** Antes del primer cuestionario, simulador o ejercicio va
   la prosa que sitúa al lector. Recibe antes de producir.
2. **Todo componente interactivo va con dos párrafos**: el que lo motiva —qué mirar y por qué— y el
   que lo cierra y entrega lo siguiente. El de salida es el que se olvida, y es el que se nota.
3. **El encabezado del módulo es un contrato.** Si el título y el objetivo prometen Snow, el módulo
   no puede dedicar su primer tercio a un diagnóstico de todo el curso sin avisar.

Y una restricción propia de las diagnósticas de entrada: **la apertura no puede regalar ninguna
respuesta**. En el capítulo 1 eso significó enunciar el supuesto que se rompe —que una observación no
dice nada sobre la siguiente— sin decir en qué dirección se rompe el error estándar (pregunta 2), ni
que la ventana forma parte del estimador (pregunta 8), ni cuáles son los tres tipos (pregunta 1).

~~**Pendiente declarado:**~~ ✅ **RESUELTO el 2026-08-04 en el Checkpoint 1.** El resto del módulo 1
sigue alternando prosa y componente cada dos párrafos cortos —cinco bloques en doce latidos—, y
**Javier lo aprobó así**: el paso de ritmo interno de los doce módulos **no se hace**. Las tres reglas
de arriba sí rigen para los capítulos 2–10.

---

## 10. Preguntas abiertas (no bloquean el arranque)

1. ~~**Publicación.**~~ ✅ **CERRADA el 2026-08-04: repo propio,**
   `https://github.com/JotaMao1985/Un_Bosque_Estadistica_Espacial.git`. No va al paraguas
   `UnBosque_Teor` de Muestreo. La estructura —raíz en la carpeta del curso, `main` + `gh-pages` con
   el sitio en la raíz de la rama publicada— está en la Fase 7 y copia la de Series de Tiempo.
2. ~~**Prueba diagnóstica.**~~ ✅ **CERRADA el 2026-08-04:** va **dentro del capítulo 1**, como
   autoevaluación de entrada sin nota (6–8 preguntas con retroalimentación por opción), aparte del
   quiz de 8 del módulo 12. No necesita precálculo; se redacta en T1.2.
3. **Banco de Brightspace.** Diseño de Experimentos tiene banco de preguntas del Corte I con la
   skill `brightspace-elbosque`. ¿Lo quieres también aquí? Si sí, entra como fase paralela, no
   dentro de estas.
4. **QGIS.** El plan del syllabus menciona puentes a QGIS. Este material es HTML: puede *explicar*
   QGIS con capturas, pero no ejecutarlo. Propongo dejarlo fuera y cubrirlo en clase.
5. **`Demirel et al. (2026)`** es la lectura de la semana 13 y está verificada como real. El
   capítulo 5 (KDE, localización comercial) es donde encaja; ¿lo quieres como caso trabajado?

---

## Anexo A — Hallazgos de la Fase 0

### A.1 · Los dos entornos ya existían a medias (T0.1)

Dos correcciones al inventario del §3, que estaba hecho mirando el sitio equivocado:

- **Python no había que crearlo.** El primer sondeo miró
  `/opt/homebrew/Caskroom/mambaforge/base/bin/python3` —el entorno **base**— y concluyó que no había
  nada geoespacial. Pero existe un entorno **`geo_env`** (Python 3.11.14) con geopandas 1.1.1,
  shapely, pyproj, rasterio, folium, mapclassify y scikit-learn ya montados. Lo que faltaba era solo
  la familia PySAL. Se **amplió** ese entorno en vez de crear uno nuevo.
- **La biblioteca de R vive en el directorio del usuario**
  (`~/Library/R/arm64/4.4/library`), **no** dentro del framework. Codificar la ruta de `nc.shp` a
  mano en el `.py` se rompe. `entorno.R` la escribe ahora en `versiones.json` y `entorno.py` la lee
  de ahí.

Añadidos al §3: `sp` hay que cargarlo **explícitamente** aunque se use `gstat` — `coordinates<-` es
suyo y `gstat` no lo adjunta al buscarlo. Y los paquetes están compilados bajo R 4.4.3 corriendo
sobre 4.4.1: avisos benignos dentro de la serie 4.4, pero conviene saberlo.

### A.2 · Clasificar por cuantiles NO da lo mismo en R y en Python — y Fisher-Jenks sí

El hallazgo más aprovechable de la fase, y va **al capítulo 3 como caso trabajado**. Sobre el mismo
`nc.shp`, mismo `SID74`, mismas 5 clases:

| | R (`classInt`) | Python (`mapclassify`) | ¿Igual? |
|---|---|---|---|
| **Fisher-Jenks**, tamaños de clase | 32, 34, 19, 11, 4 | 32, 34, 19, 11, 4 | **Sí, idénticos** |
| **Fisher-Jenks**, cortes impresos | 0 · 2,5 · 6,5 · 12,5 · 26 · 44 | 2 · 6 · 12 · 23 · 44 | No |
| **Cuantiles**, tamaños de clase | 13, 25, 13, 26, 23 | **24, 27, 11, 19, 19** | **No** |
| **Cuantiles**, cortes impresos | 0 · 1 · 4 · 5 · 10 · 44 | 1 · 4 · 5 · 10 · 44 | Sí (salvo el mínimo) |

**Fisher-Jenks: la partición es la misma; lo que cambia es cómo se imprime la frontera.** `classInt`
pone el corte en el **punto medio** entre el máximo de una clase y el mínimo de la siguiente
(2,5 = (2+3)/2; 26 = (23+29)/2) y antepone el mínimo global, de modo que da *n+1* = 6 cortes.
`mapclassify` da el **máximo real** de cada clase, *n* = 5 cortes. Mismos mínimos y máximos por
clase en las dos. **El mapa sale idéntico**; comparar los cortes impresos habría dado un falso
negativo.

**Cuantiles: la partición sí difiere de verdad, y no por el algoritmo.** La causa es el lado cerrado
del intervalo: `classInt` clasifica con **[a, b)** y `mapclassify` con **(a, b]**. `SID74` tiene
**39 condados empatados justo en los cortes** (11 valen 1, 13 valen 4, 11 valen 5, 4 valen 10). Solo
en la primera clase eso mueve 11 condados: R deja los 13 ceros y Python mete ceros y unos
(13 + 11 = 24). **Dos mapas visiblemente distintos del mismo dato, los dos rotulados «clasificación
por cuantiles».** Verificado contando los empates, no deducido.

Es el mismo tipo de trampa que los nueve convenios de `qrule` del material de Muestreo, y encaja
exactamente en el módulo 3 del capítulo 3 («esquemas de clasificación») y en el 4 («el mismo dato,
cinco mapas»).

**Consecuencia para el arnés:** las comprobaciones cruzadas comparan **la partición** (cuántas
unidades caen en cada clase), no los cortes impresos. Y `cruza()` distingue ahora entre
discrepancia **documentada** —material didáctico, no tumba la tarea— y **sin explicar** —fallo, con
salida distinta de cero—. Que una se disfrace de la otra es justo lo que hay que impedir.

### A.3 · Un arnés de pruebas puede mentir en la dirección contraria

La primera versión de `entorno.py` marcó **17 de 17 comprobaciones como FALLO** y ninguna lo era: el
ayudante `prueba(nombre, fn)` recibía el valor ya evaluado y luego intentaba invocarlo. En R el
equivalente funciona porque `expr` se evalúa de forma perezosa. Ahora `prueba()` **rechaza con
`TypeError` cualquier argumento que no sea invocable**, para que el descuido no pueda repetirse en
silencio. Es la contracara de la lección de Muestreo: allí un verificador permisivo dio falsa calma;
aquí uno roto dio falsa alarma.

### A.4 · El glosario venía con las columnas cableadas (T0.2)

`iniciarGlosarios` traía en el HTML las cabeceras **«Lohr»** y **«Gutiérrez»** y leía los campos
`f.lohr` y `f.gutierrez`. Copiado tal cual a este curso habría pintado una tabla de notación
espacial con dos columnas rotuladas con los textos de Muestreo. Se **generalizó**: ahora el registro
acepta

```js
GLOSARIOS['id'] = { titulo, nota, columnas, filas }
// columnas: [{ clave, titulo, tipo }] con tipo en 'texto' | 'mate' | 'codigo'
```

y si `columnas` no viene usa cuatro por defecto (Concepto · Este material · Texto guía · En R). Así
el capítulo 4 puede rotular la columna «Baddeley», el 8 «Anselin & Rey» y el 9 «Cressie», que es lo
que corresponde a cada tema. Es una **mejora del componente**, no un parche: la versión de Muestreo
solo servía en Muestreo.

**Trampa de medición, confirmada otra vez.** El panel del navegador renderiza los archivos de fuera
de la carpeta del proyecto como instantánea estática: `innerWidth`, `clientWidth` y
`getBoundingClientRect()` devuelven **0**, y con eso el chequeo de desbordamiento da un falso
positivo. Hay que servir por HTTP (`.claude/launch.json` con `python3 -m http.server`, puerto 8931)
y **comprobar `innerWidth > 1024` antes de medir nada**. La prueba de geometría lleva ahora esa
guarda dentro.

### A.5 · Tres fallos reales del `.geomapa`, y cómo salieron (T0.3)

**1. La bisección de `geo_simplifica` moría diciendo que el presupuesto era inalcanzable cuando no
lo era.** El corte por cercanía (`abs(n - presupuesto) < 3 %`) no comprobaba que el candidato fuera
*admisible*: con un presupuesto de 1 400 y un candidato de 1 403 vértices —que se pasa— rompía el
bucle dejando el mejor resultado en `NULL`. Se añadió la guarda `!is.null(mejor) && …`. De paso:
un fallo de `ms_simplify` estrechaba por el lado equivocado, y el **suelo estructural** de
`keep_shapes = TRUE` (cada polígono conserva un anillo mínimo; con 177 países son ~1 117 vértices
por mucho que se insista) ahora se **avisa con la cifra real** en vez de morir.

**2. El lienzo cuadrado desperdiciaba media caja.** La cuantización sobre un encuadre cuadrado es
lo que garantiza que no haya deformación, pero mapear ese cuadrado entero al lienzo dejaba Carolina
del Norte —ancha y plana— flotando en un marco cuadrado. Ahora se encaja **la caja del dato** con un
**único factor de escala para los dos ejes**, y el lienzo toma la forma del dato: si no cabe a lo
alto, se estrecha. Verificado midiendo que la escala en x y la escala en y coinciden hasta 1e-9.
Un descuido colateral: `iniciarGeomapas` imponía `spec.alto || 320`, lo que anulaba en silencio todo
el cálculo y devolvía cada mapa a un lienzo cuadrado.

**3. La leyenda se quedaba congelada al cambiar de dato — el más grave.** `dibuja()` repintaba el
lienzo pero no la leyenda, que se construía una sola vez al iniciar. En el KDE de `bei` los cortes
van de 0,130 con σ = 10 a 0,0198 con σ = 80 —un factor de 6,5— así que **el mapa cambiaba y los
rótulos de las clases mentían**. Habría afectado a los simuladores de los capítulos 5, 9 y 10.
Ahora `dibuja()` refresca leyenda, título y `aria-label`.

> **Cómo salió el fallo 3, que es la lección.** La primera comprobación contaba píxeles con alfa
> para ver si el mapa cambiaba. La rejilla rellena siempre el mismo rectángulo, así que ese conteo
> era **idéntico** conmutara lo que conmutara: la prueba daba «sin cambio» y el componente estaba
> bien; luego, con una firma de color, daba «cambia» y la leyenda estaba mal. **Una métrica ciega
> falla en las dos direcciones.** Las comprobaciones del componente usan ahora firma de color, no
> recuento de tinta.

**Costes medidos por modo** (para presupuestar los capítulos): polígonos de 100 condados **32 KB** ·
patrón puntual **0,8 KB** · grafo con 3 variantes **17,7 KB** (compartiendo geometría; sin compartir
eran 47) · rejilla de 96×48 **20 KB** · las 5 vistas del mundo **84 KB**. El presupuesto de 120 KB
por capítulo es holgado si el grafo comparte geometría y la rejilla va cuantizada.

**Optimización que hubo que inventar sobre la marcha:** `geo_grafo_multi()`. `geo_grafo` repetía los
polígonos en cada variante; con las ~10 definiciones de **W** del capítulo 6 habrían sido cientos de
KB de pura duplicación. Ahora la geometría va una vez y cada variante aporta solo aristas y grados.

**Cifras que ya sirven de material:** la contigüidad reina de Columbus da **118 aristas y grado
medio 4,8163**, la torre **100 y 4,0816** — las canónicas de Anselin. Y Web Mercator sobre los 177
países del mundo tiene **razón de área mediana 1,216**, con un recorrido de **1,002 a 65,026**: el
peor país sale **64 veces** más estirado que el mejor. El efecto Groenlandia, medido.

### A.6 · El hilo colombiano: lo que hay y lo que falta (T0.4)

**Resuelto y verificado — la capa de polígonos.** Es la pieza que sostiene los capítulos 3, 6, 7 y 8
y la que más podía torcerse, y está limpia:

| Capa | Rasgos | Cifra oficial | Geometrías inválidas | CRS |
|---|---|---|---|---|
| `colombia_adm1.gpkg` | 33 departamentos | 32 + Bogotá D.C. = **33** ✓ | 0 | EPSG:9377 |
| `colombia_adm2.gpkg` | 1 122 municipios | **1 122** ✓ | 0 | EPSG:9377 |

Procedencia completa en `datos/procesado/procedencia.json`: **Marco Geoestadístico Nacional del
DANE**, redistribuido por **geoBoundaries (gbOpen)** bajo **CC BY 4.0**, con la URL **fijada por el
commit `9469f09`** — una URL «current» cambia bajo los pies y el material dejaría de reproducirse.
Se guarda en **GeoPackage y no en shapefile**, que trunca los nombres de campo a 10 caracteres: es
además lo que enseña el módulo 7 del capítulo 2.

**Abierto: geoBoundaries no trae el código DIVIPOLA.** Solo `shapeName`. Y en Colombia hay
municipios homónimos en departamentos distintos, así que unir por nombre una variable estadística es
frágil. Sin código no hay variable, y sin variable no hay coropleto ni Moran ni SAR sobre Colombia.

**Un candidato descartado, y por qué.** `finiterank/mapa-colombia-js` trae los 1 122 municipios
**con el código DIVIPOLA correcto** (44847 = La Guajira/Uribia). Pero su bloque `transform` de
TopoJSON sitúa el país entre las latitudes **33 y 52 °N** —Colombia va de −4,2 a 13,4— y la unión
espacial contra geoBoundaries devuelve **0 coincidencias de 1 122**. El sistema de coordenadas está
roto o no es estándar. Se descarta: no se construye material docente sobre una fuente cuyas
coordenadas no caen en el país. Es justo lo que la regla «nada sin verificar» existe para impedir.

**Lo que queda de T0.4**, para retomar:
1. **Código DIVIPOLA + una variable municipal.** Buscar una fuente que lleve el código de forma
   nativa (servicios ArcGIS del geoportal del DANE, o un conjunto de datos.gov.co con `cod_dane`).
   La variable puede decidirse al escribir el capítulo 3; lo que hace falta ya es la **llave**.
2. **Patrón puntual colombiano** para los capítulos 4 y 5.
3. **Puntos con valor continuo** (estaciones) para el capítulo 9.

Nada de esto bloquea T0.5 ni el capítulo 1, que se apoya en datos canónicos.

### A.7 · Unir dos fuentes por el nombre: cómo se hizo y qué se rompió (T0.4a)

El problema de fondo: **geoBoundaries da la geometría pero no el código DIVIPOLA**, y el MEN da los
indicadores con el código pero no la geometría. La unión tenía que pasar por los nombres, y los
nombres no coinciden.

**Emparejamiento por etapas, de estricto a laxo**, con un diccionario explícito para lo que ninguna
regla resuelve:

| Etapa | Empareja |
|---|---|
| exacta (normalizada + diccionario) | 1 081 |
| sin paréntesis aclaratorios | +33 |
| sin espacios | +7 |
| **total** | **1 121 de 1 122 — 99,9 %** |

**La validación es lo que da confianza, no el porcentaje.** Los dos primeros dígitos del DIVIPOLA
son el departamento, y se comprueban contra el departamento obtenido por **unión espacial**. Esa
comprobación **no mira nombres**, así que no puede equivocarse del mismo modo que el emparejamiento:
**1 121 de 1 121 coherentes**.

**Cuatro trampas, todas verificadas:**

1. **En macOS `iconv(x, to = "ASCII//TRANSLIT")` devuelve `NA` para toda cadena acentuada.** No
   falla ruidosamente: convierte «Sonsón» en `NA` y el municipio deja de emparejar. Hundía el
   resultado al **87,5 %** y el síntoma parecía «hay muchos nombres distintos». Se usa
   `stringi::stri_trans_general(s, "Latin-ASCII")`.
2. **El diccionario tenía que llevar el departamento.** «Santuario» existe en Antioquia —que el MEN
   llama «El Santuario»— y en Risaralda —que llama igual que geoBoundaries—. Un diccionario indexado
   solo por municipio arreglaba Antioquia y **rompía Risaralda, que ya estaba bien**.
3. **`sin_parentesis` iba después de normalizar, y normalizar ya se come los paréntesis.** La etapa
   emparejaba **0** municipios y el síntoma se leía como «no quedan casos de paréntesis». Al ponerla
   sobre el nombre crudo, emparejó 33.
4. **geoBoundaries trae el nombre de Barranquilla truncado en la propia fuente**, asterisco incluido:
   `Distrito Especial, Industrial Y Portuario De Barr*`.

**Un vacío de la fuente, declarado y no disimulado:** **Mapiripana (Guainía)** está en geoBoundaries
y **no está en el archivo del MEN de 2024** (Guainía reporta 8 municipios). Queda con `NA`, nunca
con 0: un cero ahí sería un dato inventado. El script distingue «sin pareja no declarado» —que
aborta la escritura— de «vacío declarado de la fuente» —que la permite—.

**Y el dato enseña.** No basta con que cuadre:

| | |
|---|---|
| Deserción | media **3,42 %**, sd 1,77, recorrido 0–14,81, 6 ceros exactos |
| **I de Moran (deserción)** | **0,3809** · E[I] = −0,00089 · p ≈ 6·10⁻¹⁰¹ · permutación (999): p = 0,001 |
| I de Moran (cobertura neta) | 0,2250 · p ≈ 10⁻³⁶ — contraste útil: dos variables del mismo dominio con autocorrelación distinta |
| Vecindad reina | grado medio **5,854**, **2 islas**, **3 subgrafos** |

Un I de 0,38 es lo bastante fuerte para ser inequívoco y lo bastante moderado para no ser trivial.
Y las **2 islas y 3 subgrafos** son un regalo: el módulo 9 del capítulo 6 (`zero.policy`, qué hace R
con una unidad sin vecinos y por qué a veces engaña) **sale del propio dato**, sin fabricar el caso.

### A.8 · El hilo colombiano, completo: lo que se rompió por el camino (T0.4)

Los tres tipos de dato espacial del curso salen ya de datos abiertos colombianos verificados.
Lo que sigue es lo que costó, porque casi todo el trabajo fue **descartar**.

**Una fuente descartada, y no era la mala a primera vista.** `x5ay-984n` —MEN, sedes educativas
de todo el país— era el candidato obvio: trae `cod_dane_municipio`, `total_matricula` y
coordenadas de cada sede. Y no sirve. Sus coordenadas tienen **exactamente 2 decimales**, o sea
1,1 km de resolución: en Bogotá las **2 403 sedes con coordenada colapsan en 398 posiciones
distintas**. Eso no es un patrón puntual, es una retícula de redondeo, y K, G y F medirían el
redondeo. El rango estaba además corrompido (longitudes de −7,4·10¹⁵). Es el mismo motivo por el
que T0.4a tumbó `finiterank/mapa-colombia-js`: **una fuente cuyas coordenadas no se sostienen no
se usa**, por conveniente que sea el resto de sus campos.

**La ventana de observación, medida en vez de afirmada.** Bogotá D.C. incluye Sumapaz: rural,
enorme y casi sin colegios. Se congelan **las dos** ventanas y el contraste es el caso trabajado
del módulo 1 del capítulo 4:

| Ventana | Área | n | λ |
|---|---|---|---|
| Perímetro urbano | 370,1 km² | 2 107 | **5,6932** colegios/km² |
| Bogotá D.C. completo | 1 633,1 km² | 2 208 | **1,3520** colegios/km² |

**Factor 4,21 en λ, con el mismo dato.** Y el dato trae sus propias excepciones, todas declaradas
en la capa y no maquilladas: **2 geometrías centinela ±DBL_MAX** (que `st_is_valid` da por buenas
porque no son NA), **43 sedes coincidentes** —reales: misma sede, varias jornadas, y `spatstat`
las rechaza— y **RURAL EL TABACO**, que cae 219 m fuera del distrito según **las dos**
delineaciones independientes, así que no es el fallo de una capa.

**Por qué el capítulo 9 lleva estaciones y no el valor del suelo.** El valor de referencia del
suelo de Bogotá existe y es accesible (IDECA, 427 839 manzanas), pero se publica **por manzana**:
es dato de **área**. Krigearlo obliga a bajar a centroides y arrastra el problema de cambio de
soporte, que es lo contrario de lo que el capítulo quiere enseñar. Las **361 estaciones** del
IDEAM son dato geoestadístico de verdad, y traen el módulo 10 de regalo:

| | |
|---|---|
| corr(altitud, temperatura) | **−0,9791** · R² = 0,9587 |
| Gradiente térmico | **−5,56 °C por 1 000 m** — dentro del rango físico de −5 a −7 |
| Variograma del crudo | pepita 0,000 · meseta **28,863** · rango 118,9 km |
| Variograma de los residuos | pepita 0,502 · meseta **1,270** · rango 252,3 km |

Que el gradiente reproduzca la ley que debe reproducir es **evidencia de que el dato está sano**,
no un adorno. Y quitar la altitud **divide la meseta por 23**: la demostración, con dato real, de
que el kriging ordinario está mal planteado aquí.

**El error que casi se publica, y es el hallazgo de la tarea.** La primera versión midió la
falacia ecológica con el **estrato** y obtuvo individuo **+0,1448** → municipio **−0,0577**.
Inversión de signo: exactamente Robinson (1950), listo para el módulo 10. **Y era mío, no del
mundo.** Barriendo por tamaño del municipio:

| Umbral | n municipios | r |
|---|---|---|
| sin umbral | 1 114 | **−0,0577** |
| n ≥ 30 | 1 086 | +0,0146 |
| n ≥ 300 | 449 | +0,3886 |
| n ≥ 1 000 | 129 | **+0,6313** |
| ponderado por n | 1 114 | +0,5611 |

El signo lo ponía un puñado de municipios diminutos —hay uno con **dos estudiantes** y estrato
medio 6,00 tirando del extremo alto—. **Publicar el −0,06 a secas habría sido enseñar un
artefacto como si fuera un fenómeno**, y con una cita de Robinson encima. Lo que salvó la tarea
fue barrer el umbral en vez de publicar una sola cifra.

Con la **educación de la madre** la escalera sí es limpia y **estable frente al umbral**:

> ⚠️ **Tabla corregida en T0.5.** Las cifras de la izquierda son las que este anexo publicó el
> 2026-08-03 y **están mal**: se calcularon con las cuatro categorías acentuadas de
> `fami_educacionmadre` sin emparejar, o sea con **295 724 estudiantes convertidos en NA** —y no
> unos cualesquiera, sino los de los niveles educativos más altos—. Ver **A.10**.

| Nivel | r publicado (mal) | r correcto | n |
|---|---|---|---|
| Estudiante | +0,3068 | **+0,3627** | 975 956 (antes 680 360) |
| Municipio, n ≥ 30, sin ponderar | +0,2940 | **+0,3037** | 1 092 |
| Municipio, ponderado | +0,6372 | **+0,6746** | 1 114 |
| Departamento | +0,5650 | **+0,5126** | 33 |

**El fenómeno sobrevive a la corrección y la escalera sigue siendo material didáctico**: el
agregado departamental infla la correlación un **41 %** respecto de la individual. Lo que cambia es
la magnitud, y una diferencia de 0,1499 en vez de 0,2582 obligó además a recalibrar un umbral del
auditor de T0.4 que se había fijado contra las cifras sesgadas — ver A.10.

Las **dos** escaleras van al material: una es el fenómeno (módulo 10) y la otra
es la trampa (módulo 2, «normalizar o mentir»). Con el estrato la ausencia del dato tampoco es
inocente: corr(cobertura del estrato, puntaje medio) = **+0,5952**, frente a **+0,2223** con la
educación de la madre (también recalculado en T0.5).

**Un segundo fallo real, de código.** Los agregados municipales calculaban
`mean(fami_tieneinternet == "Si", na.rm = TRUE)`. En R **`"" == "Si"` es `FALSE`, no `NA`**, así
que cada respuesta vacía contaba como «no tiene» y el `na.rm` no protegía de nada porque no
había ningún NA que quitar. La cobertura nacional pasaba del **72,60 % real al 68,29 %**, y el
sesgo se concentraba justo en los municipios con más ausencia, que son los rurales. Es el primo
del `iconv` de T0.4a: **la comparación que devuelve un valor plausible en vez de fallar**.

**Un vacío cerrado.** T0.4a dejó **Mapiripana (Guainía)** con `divipola = NA` porque el MEN no la
reporta. Saber 11 sí la trae (`94663`, 32 estudiantes) y el código se recupera de ahí, **validado
con la misma comprobación independiente**: sus dos primeros dígitos contra el departamento
obtenido por unión espacial. La llave queda en **1 122 de 1 122**. Las variables del MEN siguen en
NA: un código verificado y unas variables ausentes no son lo mismo. **Belén de Bajirá** (`27086`,
290 estudiantes) sigue sin polígono —territorio en disputa Chocó/Antioquia, no está en el MGN— y
queda declarado como vacío real de la fuente.

**Cómo se descarga un millón de registros de datos.gov.co**, porque hay tres caminos y dos no
sirven: el endpoint de exportación (`/api/views/ID/rows.csv?accessType=DOWNLOAD`) **ignora
`$select` y `$where`** y devuelve los 7 109 704 registros y las 51 columnas —2,8 GB en 11
minutos—; el endpoint SoQL con `$order` obliga a ordenar el millón de filas y expira. Lo que
funciona: `/resource/ID.csv` con `$where` y `$select`, **sin `$order`** y con un `$limit` por
encima del total, en **una sola petición**.

**El auditor, y la comprobación que mentía por estricta.** `verifica_t04.R` no repite el cálculo
del generador —eso solo comprobaría que R es determinista—: recalcula desde el crudo por otro
camino. Da **75 de 75**. Una comprobación falló al principio y no era el dato: exigía
`st_covered_by(ventana_urbana, ventana_dc)`, y el desborde eran **141 astillas que suman
0,0000 km²**, la mayor de medio metro, sin ningún colegio dentro. El predicado exacto decía «no
está contenida», y era verdad en el sentido literal y falso en el que importa. **Una comprobación
demasiado estricta miente igual que una permisiva**, solo que hacia el otro lado — la contracara
de A.3. Ahora se mide por área, con tolerancia declarada.

Y como 75 en verde no prueba nada por sí solo, `prueba_verifica_t04.R` le rompe el dato a
propósito: **12 de 12 defectos cazados**, todos imitando fallos que ya ocurrieron de verdad en
este proyecto (la coordenada centinela, el hueco en la llave, el cero donde debía ir NA, el vacío
contado como «No»).

**Peso, para la Fase 7:** `datos/crudo/` **345 MB** y `datos/procesado/` **242 MB** — ninguna de
las dos debe entrar al repositorio, y el `.gitignore` de lista blanca de T7.2 tiene que excluirlas
explícitamente. Las tres capas municipales pesan **78 MB cada una** porque cada una arrastra su
propia copia de la geometría sin simplificar: 156 MB de duplicación, dejada a propósito para que
ningún script de capítulo tenga que hacer uniones, pero revisable. Nada de esto llega al material:
los capítulos incrustan la salida de `geo.R`, con su presupuesto de ≤ 120 KB.

### A.9 · Geometría única, y Colombia como material (T0.4, segunda pasada)

Dos encargos de Javier tras cerrar T0.4: guardar la geometría una sola vez, y tratar Belén de
Bajirá como material del curso y no como una nota al pie. El segundo obligó a mirar el dato otra
vez, y lo que apareció es mejor de lo que había.

**Geometría única.** Las tres capas municipales pesaban **78 MB cada una** porque cada una
arrastraba su copia de los 1 122 polígonos sin simplificar. Ahora la geometría vive solo en
`colombia_adm2.gpkg` y los atributos en CSV: `municipios_llave.csv` (**116 KB**) y
`municipios_saber11.csv` (**66 KB**). La unión va por **`shapeID`** —la identidad estable de
geoBoundaries, fijada por el commit—, no por posición de fila ni por nombre, y la rehace
`carga_municipios()` de `fuentes.R` en una línea. **`datos/procesado/` pasa de 242 MB a 86 MB.**
El auditor tiene una inyección dedicada a que la duplicación no vuelva.

**Y la validación contra la fuente autoritativa, que faltaba.** Hasta aquí la llave se validaba por
prefijo de departamento: una comprobación **interna**, que contrasta los códigos contra la
geometría pero no contra quien los define. El **DIVIPOLA oficial del DANE** (`gdxc-w37w`, CC BY-SA
4.0) es esa lista, y contrastar contra ella da **1 121 de 1 122** — y destapa las dos discrepancias
que ahora son el caso trabajado.

**Colombia no está hecha solo de municipios.** El DIVIPOLA declara **1 103 municipios + 18 áreas no
municipalizadas + 1 isla**. La columna `tipo` entra a la capa, y no es un adorno administrativo:

| Tipo | Unidades | Con Saber 11 | Estudiantes | Puntaje medio |
|---|---|---|---|---|
| Municipio | 1 102 | 1 100 (**99,8 %**) | 1 063 702 | **250,19** |
| Isla (San Andrés) | 1 | 1 (100 %) | 1 048 | 239,52 |
| Área no municipalizada | 18 | 11 (**61,1 %**) | 362 | **196,25** |

**Brecha de 53,94 puntos — 1,04 desviaciones típicas.** Y **7 de las 18 áreas no municipalizadas no
aportan un solo estudiante**. El tipo de entidad predice tanto si hay dato como cuál es el dato.
Medido a nivel de **estudiante**, no promediando medias de unidad: con unidades de 2 a 24
estudiantes, la media de medias la dominaría el ruido — la misma trampa del estrato en A.8, y esta
vez se vio venir.

**Belén de Bajirá: tres entidades del Estado, tres respuestas.** En A.8 quedó como «vacío real de
la fuente». Era verdad y era incompleto:

| Entidad | Qué dice |
|---|---|
| DIVIPOLA (DANE) | Existe: municipio **27493**, «NUEVO BELÉN DE BAJIRÁ», Chocó |
| ICFES | Existe, pero con el código **27086** — que el DIVIPOLA no lista |
| Marco Geoestadístico Nacional | **No tiene polígono** para él |

Consecuencia comprobada: sus **290 estudiantes** existen en la tabla y **no caen en ningún
polígono**. Y **Mapiripana** es el caso espejo: la cartografía sí tiene su polígono, pero el
DIVIPOLA ya retiró el código —el territorio quedó dentro de Barrancominas (`94343`), que está
además como polígono aparte en la misma capa— mientras el ICFES de 2022 seguía usando `94663`.

Los dos van a `casos_territoriales.json` y son material del **capítulo 3**: módulo 9 (efecto
zonificación del MAUP) y módulo 11 (cartografía y ética). Que una unidad territorial exista para
una entidad del Estado y no para otra no es una anécdota: **es la unidad de análisis siendo una
decisión política**, que es justo lo que el MAUP afirma y lo que el material puede ahora mostrar con
un caso propio y verificado, en vez de con el *gerrymandering* de manual.

**Dos fallos más, encontrados en esta pasada:**
1. **`s11_n` mentía por su nombre.** Contaba solo estudiantes **con estrato**, no estudiantes. En
   Belén de Bajirá eso eran 216 en vez de 290. Un capítulo que leyera «s11_n» habría entendido otra
   cosa. Ahora `s11_n` es el conteo real y lo que depende del estrato se llama `s11_n_estrato`.
2. **`sprintf("%05d", NA_integer_)` devuelve la cadena `"000NA"`**, que no falla y viaja como si
   fuera un código de municipio. Había 2 registros sin código de colegio en la cohorte. Es la
   tercera vez en esta tarea que aparece el mismo patrón —después del `iconv` de A.7 y del
   `"" == "Si"` de A.8—: **la operación que devuelve algo plausible en vez de fallar**.

**Auditoría tras la segunda pasada: 90 de 90 comprobaciones, y 17 de 17 defectos inyectados
cazados.** Las inyecciones nuevas cubren la discrepancia con el DIVIPOLA sin ficha, el caso
territorial sin documentar, la columna `tipo` mutilada, la brecha que no reproduce el crudo y la
geometría volviendo a duplicarse.

### A.10 · El arnés de auditoría, y lo que destapó al estrenarse (T0.5)

Cuatro guiones que parecían un porte mecánico. Ninguno se pudo portar tal cual, y el primero que
funcionó encontró un defecto grande en trabajo que ya estaba dado por auditado.

**Ninguno de los cuatro servía copiado.**

| Guion | Por qué no |
|---|---|
| `verifica_bloques.py` | Invocaba el `Rscript` del PATH —Homebrew 4.6.0, **sin `sf`**— y `python3` a secas en vez del `geo_env`. Verificar con ellos habría dado un fallo masivo que no era del material |
| `audita_texto_capN.py` | No es un guion: son **ocho**, de 370 a 677 líneas, con el contenido cableado. Y aquí no había capítulo |
| `prueba_texto.py` | Sus defectos son literales del contenido de DOE |
| `cuenta_sitio.py` | Apuntaba a `sitio/muestreo/` y no sabía contar `.geomapa` |

**Y no había nada que auditar.** La plantilla del curso tiene cinco bloques de código y **cero
líneas `#>`**: `verifica_bloques.py` sobre ella habría informado «0 de 0 cifras» **en verde**. Ese
verde es exactamente la falsa calma que T0.5 existe para impedir, así que ahora **un documento con
bloques y sin ninguna `#>` es un fallo**, no un aprobado. Y hubo que fabricarle al arnés un sujeto:
`prueba-auditoria.html`, un capítulo de mentira con cifras de verdad —Moran de la deserción, λ de
las dos ventanas de Bogotá, gradiente del IDEAM, Columbus, `nc`— todas salidas de
`genera_demo_auditoria.R` y ninguna escrita a mano. Se queda como prueba de regresión permanente.

**Núcleo compartido en vez de diez copias.** En DOE, copiar el auditor por capítulo hizo que
**cinco de ellos retiraran las fórmulas de KaTeX antes de extraer los números**: entre el 18 % y el
29 % de los decimales publicados no se auditaban, y los cinco informaban «limpio». Aquí la
maquinaria vive en `audita_texto_base.py` y cada capítulo aporta una espec de ~90 líneas que
declara **qué** comprobar, no **cómo**. `audita_texto_demo.py` es el molde de `audita_texto_cap1.py`.

---

#### El hallazgo grande: `LC_CTYPE=C`, y 295 724 estudiantes que desaparecían sin ruido

`Rscript` arranca con `LC_CTYPE=C` salvo que el entorno diga otra cosa. En ese estado R **no sabe
que sus cadenas son UTF-8**, y `jsonlite` escribe los bytes crudos entre corchetes angulares:

```
Sys.getlocale("LC_CTYPE")      #> "C"
nchar("Deserción")             #> 10   (bytes, no caracteres)
jsonlite::toJSON("Deserción")  #> ["Deserci<c3><b3>n"]
```

**Sin fallar.** El JSON es válido, el script termina con éxito, y la tilde llega al navegador
convertida en `<c3><b3>`. Salió porque la leyenda del mapa del fixture decía
`Deserci<c3><b3>n escolar` y el rótulo de la escala `desercin (%)`.

Y ya había hecho daño. `saber11_20224_cifras.json`, publicado en **T0.4**, llevaba cuatro etiquetas
corrompidas. Pero eso era lo cosmético. Lo grave es que la escala ordinal de la educación de la
madre empareja **por el texto de la categoría**, y bajo `LC_CTYPE=C` las cuatro categorías con
tilde no emparejan con nada:

| | Empareja | r individual |
|---|---|---|
| `LC_CTYPE=C` — lo publicado en T0.4 | 680 650 | **0,3068** |
| UTF-8 — correcto | 976 374 | **0,3627** |

`EM[x]` devuelve **`NA`** para una categoría que no encuentra, así que **295 724 estudiantes —el
27,7 % de la cohorte— salían del cálculo en silencio**. Y no una muestra cualquiera: exactamente
los cuatro niveles educativos **más altos** (educación profesional y técnica/tecnológica, completa
e incompleta), que son los que más puntúan. La falacia ecológica del cap. 3 estaba medida sobre un
dato mutilado por arriba.

**Es el mismo patrón por cuarta vez** —después del `iconv` de A.7, el `"" == "Si"` de A.8 y el
`sprintf("%05d", NA)` de A.9—: *la operación que devuelve algo plausible en vez de fallar*. Ya no
es una anécdota: es **el** modo de fallo de este proyecto.

**Por qué el auditor de T0.4 no lo vio, que es la lección metodológica.** `verifica_t04.R` no
repite el cálculo del generador: recalcula desde el crudo por otro camino. Pero **los dos caminos
corrían en el mismo locale roto**, así que los dos se equivocaban igual y el contraste daba 90/90.
Un control independiente que comparte el entorno con lo que audita no es independiente: **hay que
variar también el entorno.** Lo destapó T0.5 solo porque su envoltorio `rscript.sh` cambió el
locale y el auditor de T0.4, corriendo por primera vez en UTF-8, pasó a 87/90.

**Cómo queda cerrado.** `precalculo/utf8.R` es una guarda que **para** en vez de reparar — y esto
también costó descubrirlo: la primera versión llamaba a `Sys.setlocale(...)` y se autoaprobaba,
porque **R parsea el archivo entero antes de ejecutar su primera línea** y los literales acentuados
del script que la llamó ya estaban leídos mal. Una guarda que se aprueba a sí misma es peor que no
tener guarda. Ahora comprueba el estado **de arranque**, para si no es UTF-8, y remite a
`precalculo/rscript.sh`, que fija de una vez las dos trampas del entorno: el R correcto y la
regional. Los cinco generadores de T0.4 y su auditor cargan la guarda. **T0.4 regenerada, 90/90 y
17/17 en su arnés de inyección.**

Un umbral hubo que recalibrar y se declara: `r_departamental − r_individual ≥ 0,15` se había fijado
contra las cifras sesgadas (diferencia 0,2582). Con el dato entero la diferencia es **0,1499** —el
agregado sigue inflando la correlación un **41 %**, o sea el fenómeno está y es fuerte— pero el
umbral heredado la dejaba fuera por una diezmilésima. Se baja a 0,10 y se publica el porcentaje.
Es A.8 en la otra dirección: **una comprobación demasiado estricta miente igual que una permisiva**.

---

#### El punto ciego del auditor, medido en vez de supuesto

`mide_punto_ciego.py` cuantifica lo que `prueba_texto.py` no puede: qué defectos **no** se
inyectaron porque no se le ocurrieron a nadie. El auditor indexa las razones y los excesos
porcentuales entre cifras publicadas —sin eso habría cientos de falsos positivos—, y ese conjunto
absorbe perturbaciones por azar. Perturbando un dígito de las cifras **realmente publicadas**:

| Decimales en el texto | Se cuelan | Cifras |
|---|---|---|
| 1 | **63,16 %** | 11 |
| 2 | 0,00 % | 1 |
| 4 | **8,65 %** | 38 |
| 6 | 0,00 % | 4 |

Las peor protegidas son las de **un decimal** y las que llevan **ceros de relleno** (`1.7100`): la
normalización del auditor recorta los ceros finales y las colapsa contra otras cifras.

**Javier fijó el listón en CINCO decimales** (2026-08-03; el borrador de esta tarea proponía
cuatro). Con el fixture reescrito a esa regla, **toda cifra de la prosa tiene ya 5 o 6 decimales** y
la medición queda así:

| Decimales en el texto | Se cuelan | Perturbaciones | Cifras |
|---|---|---|---|
| **5** | **4,63 %** | 389 | 45 |
| 6 | **0,00 %** | 45 | 4 |

El decimal de más baja la absorción de 8,65 % a 4,63 %. Lo que queda son las cifras con **ceros de
relleno** —`1.71000`, `1.35200`, `0.19800`—, que la normalización del auditor colapsa; es una
limitación conocida y declarada, no un descuido.

**Aplicar la regla destapó dos cosas más, y las dos se arreglaron:**

1. **Doble redondeo.** El generador guardaba el JSON con `round(x, 6)` y el ensamblador formateaba
   a 5: la prosa decía `3.95446` mientras el bloque de código del propio capítulo —que calcula
   `round(x, 5)` sobre el valor sin redondear— imprimía `3.95447`. Una diezmilésima de desacuerdo
   entre un capítulo y su propio código, que `verifica_bloques.py` cazó al primer intento. Con la
   regla en cuatro decimales no se veía porque sobraban dos de margen. **Regla nueva: el JSON se
   guarda con holgura por debajo de lo que se publica** — ahora 10 decimales.
2. **`mide_punto_ciego.py` medía con otra configuración.** Construía su propio `Auditor` sin pasarle
   la lista de estructurales, así que contaba como «cifra peor protegida» el `4.0` de «CC BY 4.0» y
   el `0.5` de «T0.5». Medir con una configuración distinta de la que se audita es medir otra cosa.

*(La primera versión de esta medición daba 15,8 % a cuatro decimales y no significaba nada:
formateaba a cuatro decimales cifras que no los tenían y perturbaba ceros de relleno, que no es una
errata que nadie vaya a cometer. Una métrica ciega falla en las dos direcciones — A.5 otra vez.)*

---

#### Dos fallos propios de esta tarea, y los dos son del mismo tipo

**1. El ensamblador se comió 276 líneas del motor y dijo «limpio».** Para recortar el bloque
`courseData` buscaba su cierre con `doc.index("];")`, y encontró un `];` que estaba **dentro de un
comentario** 270 líneas más abajo (`return [chart];`). Se llevó `renderNavigation` y `loadModule`.
El archivo salió **más grande** que la plantilla, todas las anclas siguientes se encontraron y el
informe fue en verde; solo abrirlo en el navegador —contenido en blanco— lo destapó. Ahora
`reemplaza_region()` exige un **tope de líneas** para cada región que sustituye.

**2. Dos comprobaciones mías eran incapaces de fallar.** El auditor preguntaba
`"tabla:" in doc` y `"etiqueta:" in doc` para el `.geomapa`. Las dos cadenas aparecen en el
**comentario de documentación del motor** (`GEOMAPAS['id'] = { fuente, alto, paleta, etiqueta,
tabla }`), así que daban OK pasara lo que pasara — y sobre el informe se leían igual que las que sí
comprueban algo. Ahora miran solo dentro del registro.

**Y lo destapó una métrica que hubo que inventar.** «36 de 36» no dice nada sobre las
comprobaciones que el arnés nunca ejercitó, así que `prueba_texto.py` publica ahora **cuántas
comprobaciones se han visto fallar**: al principio eran **14 de 76**. Clasificando las 62 restantes
por familia salieron cinco mecanismos sin **ninguna** instancia probada, y de ahí salieron las
inyecciones de la segunda y la tercera tanda. Estado final: **36 inyecciones, 33 de 76
comprobaciones vistas fallar, y cero familias sin probar** — las 43 que faltan son otras instancias
de mecanismos ya demostrados (otra fuente, otro tema, otro símbolo).

---

#### La familia nueva: auditar el `.geomapa`

Punto ciego que DOE no tenía. Los cortes de clase, la leyenda y la geometría de un mapa viven en
JSON **dentro del `<script>`**, y el auditor de prosa corta el documento antes de ahí. En T0.3 eso
ya se cobró una pieza: `dibuja()` repintaba el lienzo y no la leyenda, así que **el mapa cambiaba y
los rótulos mentían**, con el componente pareciendo perfecto. Ahora se comprueba que cada
`data-geomapa` tenga registro, que **los cortes sean los que calculó R** (no unos recalculados en
JS, que además introducirían un tercer convenio de empates junto a los dos de A.2), que el `n`
declarado cuadre con la geometría, que haya etiqueta accesible y tabla de respaldo, y que la
geometría quepa en los 120 KB.

#### Herramientas nuevas que quedan para todo el proyecto

| Archivo | Para qué |
|---|---|
| `precalculo/rscript.sh` | **El único modo correcto de invocar R aquí**: R 4.4-arm64 + regional UTF-8. Resuelve las dos trampas del entorno en un sitio |
| `precalculo/utf8.R` | Guarda de codificación que **para** si el proceso no arrancó en UTF-8 |
| `precalculo/audita_texto_base.py` | El núcleo de 10 familias de comprobación |
| `precalculo/audita_todo.sh` | Punto de entrada único: los cuatro guiones en orden |
| `precalculo/mide_punto_ciego.py` | Qué NO protege el auditor, por número de decimales |

#### Lo que queda abierto

- **`casos_territoriales.json` sigue sin tildes** («Belen de Bajira», «Choco»). No es un fallo
  ahora mismo —el archivo es válido— pero era un síntoma disfrazado de decisión: se escribió así
  para esquivar el problema de codificación. Con la guarda puesta se puede escribir bien, y
  conviene hacerlo cuando el capítulo 3 lo use.
- **Las 43 comprobaciones sin instancia probada** son otras instancias de familias ya demostradas.
  No urge, pero cada capítulo nuevo debería añadir una inyección de la familia que estrene.

### A.11 · El precálculo del capítulo 1: lo que midió y lo que se rompió (T1.1)

Primer capítulo con contenido. Doce módulos de cifras, cuatro ejercicios guiados, un auditor nuevo
y su arnés. **Cinco defectos reales, y tres estaban en trabajo mío ya escrito** — que es la
proporción que este proyecto viene teniendo y conviene no olvidar.

**Lo que el capítulo mide, en vez de afirmar.** Ninguna de estas cifras está escrita a mano; todas
salen de `cap1_datos.json` y las recalcula `audita_cap1.py` desde las fuentes primarias.

| Módulo | Lo que se mide | Cifra |
|---|---|---|
| 1 · Snow | Muertes cuya bomba más próxima es Broad Street | **359 de 578 = 62,11073 %**, frente al 7,69231 % que daría el reparto uniforme entre las 13 bombas: **8,07439 veces** |
| 1 · Snow | La historia del mango de la bomba, contrastada | El **90,36778 %** de los ataques ocurrió **antes** del 8 de septiembre, y ese día ya habían caído un **91,60839 %** desde el pico del 1 de septiembre |
| 3 · Tobler | Correlograma del IDEAM por bandas | I = **0,60635** (0–25 km) → **−0,00343** (500–800 km) |
| 3 · Tobler | Los tres regímenes por Clark-Evans | redwood **0,61865** < japanesepines **1,06400** < cells **1,67168** |
| 4 · Inferencia | Cobertura real de un IC nominal al 95 % | **0,95300** sin correlación → **0,19700 ± 0,00726** con rango 4 |
| 4 · Inferencia | El e.e. subestimado, sobre dato real | bootstrap i.i.d. **0,05269** frente a por bloques **0,21962**: factor **4,16822** |
| 5 · n efectivo | Los 1 121 municipios, ¿cuántos son de verdad? | **64,52155** — el **5,75571 %** de la información |
| 6 · Una realización | Realizaciones que engañarían al análisis ingenuo | **82,00000 % ± 1,21491** (debería ser el 5 %) |
| 7 · Escala | El I de Moran al agregar | **0,38091** (1 121 municipios) → **0,06360** (33 dptos): cae el **83,30410 %** |
| 10 · CV | RMSE con CV aleatoria frente a por bloques | **3,16307** → **5,54619**: infla el **75,34221 %**. R² pasa de **0,66585** a **−0,02735** |

Dos cosas que no estaban en el guion y salieron del propio dato. **El caso de Snow es geométrico,
no epidemiológico**: el patrón demuestra una concentración alrededor de un punto, y lo que lo
convierte en evidencia sobre el agua es el mecanismo que Snow ya sospechaba. Eso engancha con el
capítulo 3 (falacia ecológica) y el 8 (los tres orígenes de la dependencia). Y **la autocorrelación
de la temperatura del IDEAM era en buena parte una covariable disfrazada**: quitarle la altitud baja
la I de la primera banda de 0,60635 a **0,42580**, un **29,77633 %** menos. Es el capítulo 9 (deriva
externa) anunciándose desde la semana 1, medido con dos líneas de R.

---

#### El hallazgo grande: `spdep` y `esda` no dan el mismo I de Moran, y la culpa es de las islas

Lo destapó el auditor de Python al recalcular la cifra estrella del capítulo. Sobre **el mismo
grafo** —mismo número de aristas, mismo grado medio, mismas 2 islas, mismos 3 subgrafos—:

| | I municipal | I departamental |
|---|---|---|
| `spdep::moran.test(zero.policy = TRUE)` | **0,38091** | **0,06360** |
| `esda.Moran` (libpysal) | **0,38159** | **0,06558** |

**La causa, verificada reconstruyendo la fórmula a mano:** con `zero.policy = TRUE`, `spdep` calcula
`I = (n/S0)·Σ z·Wz / Σ z²` tomando **n = unidades CON vecinos** (1 119 de 1 121), mientras `esda`
toma **n = todas**. Reproducir el valor de R desde el de Python es exactamente multiplicar por
1 119/1 121, y así lo comprueba el auditor.

Ninguna de las dos está mal: son dos convenios sobre qué es una unidad sin vecinos. Pero **comparar
0,3809 con 0,3816 sin saber esto parece un error de cálculo**, y un estudiante que siga el capítulo
con las pestañas de Python se va a encontrar la diferencia. Se publican **las dos** y se declara la
causa, igual que con los cuantiles de A.2. Y es, de regalo, **el caso trabajado que el módulo 9 del
capítulo 6 (`zero.policy`, «qué hace R con una unidad sin vecinos y por qué a veces engaña») tenía
encargado**: sale del propio dato, sin fabricarlo.

Una tercera discrepancia, más pequeña y del mismo tipo: **sf informa `MULTIPOLYGON` para los 100
condados de `nc`** porque ése es el tipo declarado de la capa, mientras **shapely mira cada
geometría y solo 6 tienen más de una parte**. La geometría es idéntica; lo que difiere es qué se
considera el tipo de un rasgo. Va al módulo 9 del capítulo 1.

**Las tres viven en `cap1_datos.json` bajo `discrepancias`, con sus dos valores, su causa y el
capítulo al que van. Y el auditor las lee:** si encuentra una diferencia que está en la lista, la da
por material didáctico; si encuentra una que no está, falla. Que una discrepancia documentada y una
sin explicar se lean igual sobre un informe es lo que convierte un auditor en un adorno.

---

#### Tres defectos míos, y los tres del mismo tipo: publicar un artefacto como si fuera un fenómeno

**1. Casi publico «la correlación sube un 345 % al agregar».** El módulo 7 tenía que enseñar el
efecto escala de Gehlke y Biehl (1934) sobre dato colombiano, y la primera versión lo hizo con
deserción y cobertura: r municipal **0,02111**, r departamental **−0,09405**. Son **dos valores de
ruido con signos opuestos**, y el «345 %» era el cociente entre ellos. Es **el fallo de A.8 otra
vez** —allí el estrato municipal dio −0,0577 y parecía Robinson (1950)—, y lo salvó la misma
receta que aquel anexo dejó escrita: **en vez de una cifra sola, el barrido entero**.

Ocho variables, los 13 pares con correlación municipal apreciable, a las dos escalas. Y el
resultado es mejor material que el que buscaba: **8 pares suben, 5 bajan y 1 invierte el signo.**
Agregar cambia la correlación, pero **no siempre en la misma dirección** — que es una lección más
honesta y más útil que «agregar infla». El par principal (puntaje de Saber 11 frente a hogares con
internet) va de **0,50202** a **0,80560**, y su barrido por tamaño de municipio confirma que la
cifra municipal **no la ponen los municipios diminutos**: entre todos y los de al menos 30
estudiantes se mueve **0,01243**. El que invierte el signo es el **estrato**, que T0.4 ya había
congelado como caso de aviso; se enseña como advertencia, no como fenómeno.

**2. La simulación de agregación no mostraba nada, y yo iba a explicarla igual.** El módulo
necesitaba una versión controlada del mismo efecto, y la primera daba **0,38016 → 0,35949**: plano,
incluso ligeramente a la baja. El montaje estaba mal: construí el componente independiente de cada
variable **también como campo suave**, así que promediar celdas se llevaba señal y ruido por igual.
**Que el ruido NO tenga estructura espacial no es un detalle del montaje, es la condición del
fenómeno.** Con ruido blanco, la correlación va de **0,35075** (base teórica 0,36) a **0,98954**
al agregar en bloques de 16×16: **+182,12490 %**. El generador lleva ahora un `stop()` que aborta
si el efecto no aparece — publicar un montaje roto explicándolo como fenómeno es peor que no
publicarlo.

**3. Los módulos 4 y 6 medían lo mismo y no cuadraban.** El módulo 6 decía que el **87,5 %** de las
realizaciones engañaría al análisis ingenuo; el módulo 4 decía que la cobertura con ese mismo rango
era del 19,70 %, o sea un **80,3 %** de rechazo. Es **el mismo número visto del derecho y del
revés**, y el capítulo iba a publicar los dos a dos módulos de distancia. Eran solo 200
realizaciones: subidas a 1 000, sale **82,00000 % ± 1,21491** frente a **80,30000 % ± 0,72631**,
o sea **1,2 errores de Monte Carlo**. Ahora el generador **comprueba la coherencia entre los dos
módulos y para** si se separan más de tres errores de Monte Carlo conjuntos.

---

#### El arnés encontró tres fallos del auditor, y los tres son el mismo

`audita_cap1.py` informó **818 comprobaciones, 0 fallos** la primera vez. `prueba_auditor_cap1.py`
le inyectó 49 defectos y cazó **46**. Los tres que se colaron eran **la misma clase de error**:

| Se coló | Por qué |
|---|---|
| «la estabilidad ante unidades pequeñas se declara sin serlo» | El auditor leía la bandera `estable_ante_unidades_pequenas` **del propio archivo que audita** |
| «E4: la r deja de crecer con el tamaño de la unidad» | Igual, con la bandera `monotona` |
| «un corte de clase del mapa de nc cambia» | Los cortes se comprobaban ordenados, cubriendo el recorrido y sumando n — pero **nunca contra la asignación de clase**, que es lo único que los ata al dato |

Los dos primeros son **la trampa de T0.5 con otra cara**: allí dos comprobaciones eran incapaces de
fallar porque buscaban una cadena que estaba en un comentario del propio archivo; aquí eran
incapaces de fallar porque **creían la autodeclaración del archivo**. Un JSON que dice de sí mismo
que es monótono no es evidencia de que lo sea. Las tres banderas se recalculan ahora desde los datos
que las justifican, y los cortes se confrontan con la clase de cada unidad respetando el convenio
`[a, b)` de `classInt` (A.2). Estado final: **836 comprobaciones, 0 fallos, 49 de 49 inyecciones
cazadas, 74 comprobaciones vistas fallar**.

**Las 3 comprobaciones SALTADAS se dicen en voz alta**, y ésa es la otra mitad de la independencia
del auditor. `HistData`, `spatstat.data` y `sp` no existen en Python, así que sobre Snow, los
patrones canónicos y `meuse` el auditor verifica **el análisis, no la lectura del paquete**; la
lectura la ancla `genera_cap1.R` contra las cifras que publican las fuentes y **para** si no
cuadran (20 anclas). Para `nc.shp`, los GeoPackage colombianos y los CSV de municipios la
independencia es total: geopandas los lee del original. Callar una comprobación que no se hace la
convierte en una comprobación imaginaria, que sobre el informe se lee igual que una que sí corrió.

Y una verificación cruzada que salió redonda y conviene registrar: la asignación de cada muerte a
su bomba más próxima, calculada con `cKDTree`, coincide con **los 578 de 578** de los polígonos de
Thiessen que Tobler distribuye con el dato. Dos construcciones distintas de la misma idea, y
coinciden.

---

#### Presupuesto, y una separación que hubo que declarar

`cap1_mapas.json` pesa **102,1 KB**, y el §4 presupuesta 120 KB de **geometría** por capítulo. Pero
dentro hay dos cosas distintas: **geografía 75,1 KB** (Snow con sus 528 calles, los tres patrones
canónicos, `nc`, `meuse`, las 2 209 sedes de Bogotá, los 33 departamentos, las 361 estaciones) y
**rejillas simuladas 27,0 KB** (los campos gaussianos de los simuladores, que no son territorio).
La primera versión se iba a **165,5 KB**. Se recortó donde no se nota —`nc` de 1 500 a 900
vértices, los departamentos de 2 000 a 1 200, las rejillas de 32×32 a 28×28, y fuera la marca del
mapa de Bogotá, que es del capítulo 4— y el generador **comprueba las dos cosas contra el mismo
listón de 120 KB**, para no ir gastando por la puerta de atrás lo que se ahorra por la de delante.

### A.12 · El ensamblado del capítulo 1: lo que se rompió (T1.2 y T1.3)

Primer capítulo publicable. Doce módulos, nueve simuladores, nueve mapas, dieciséis preguntas y
cuatro ejercicios guiados, todo generado por un guion. **Ocho defectos reales, y seis estaban en
herramientas que ya habían dado verde** — el arnés, el auditor, el contador—, que es la proporción
que este proyecto viene teniendo y conviene no olvidar.

**Cuatro decisiones que tomó Javier antes de empezar:** patrón «concreto → formal» desde el módulo 1
(cada módulo abre con un caso medido y solo después formaliza) · la diagnóstica de entrada en un
bloque propio al principio del módulo 1, ocho preguntas sin nota, con la retroalimentación remitiendo
al módulo que responde cada una · **ensamblador** en vez de HTML escrito a mano · T1.2 y T1.3 en la
misma sesión.

---

#### El ensamblador, y por qué D10 deja de ser disciplina

En Diseño de Experimentos D10 era una regla que había que recordar: se copiaban los números del JSON
y el auditor los contrastaba después. En Muestreo esa disciplina falló —se colaron tres cifras
escritas de memoria **mientras se corregía justamente ese problema**—. `ensambla_cap1.py` la convierte
en imposible: **el HTML no existe hasta que el guion lo escribe**, y cada cifra está interpolada desde
`cap1_datos.json`, `cap1_mapas.json` o `cap1_soluciones.json`.

El reparto interno también es deliberado:

| Qué | Dónde vive | Por qué |
|---|---|---|
| La prosa | f-strings de Python | Es lo que audita `audita_texto_cap1.py` |
| El JavaScript | cadenas planas que leen `DATOS_CAP1` con `n5()` | Las llaves de JS no pelean con las de los f-strings, y **una pregunta del quiz no puede quedarse con una cifra vieja porque no tiene ninguna cifra escrita** |
| Los mapas estáticos | registrados con su JSON **literal**, no con una función | `audita_texto_base.geomapas()` solo puede comprobar cortes, `n` y peso de un mapa cuya fuente sea un literal. Registrarlos todos como función —que es lo cómodo— habría dejado esa familia entera del auditor sin nada que mirar, **informando en verde** |

---

#### El `.geomapa` aprende a pintar capas, y el tipo de la marca lo declara R

Era lo que T1.1 dejó bloqueando. `geomapaPintaPuntos` dibujaba una nube de un color sobre nada;
ahora pinta **polilíneas de fondo** (las 528 calles de Soho), una **segunda capa** con símbolo propio
(las 13 bombas en rombo, no en círculo: dos capas que solo se distinguen por el color desaparecen en
una impresión en gris), **una de ellas resaltada** y **color por marca**.

**Y la decisión que importa: el tipo de la marca lo declara el dato, no lo adivina el navegador.**
Sobre el JSON, las trece bombas de Snow y las temperaturas del IDEAM llegaban las dos como un vector
de números. Un navegador que decida por el aspecto acierta hoy —trece enteros pequeños *parecen*
categorías— y falla el día en que una marca categórica tenga cien niveles o una numérica tome tres
valores enteros: mapa bien dibujado, mal coloreado, sin avisar. Es el modo de fallo de siempre.
`geo_puntos()` emite ahora `marcas_tipo` y, para las categóricas, sus `niveles`.

Coste: regenerar el precálculo. **`cap1_datos.json` salió idéntico** —cero diferencias— y
`cap1_mapas.json` cambió **solo** en los cuatro campos declarados. Los seis modos de
`demo_geomapa.json` salen **idénticos byte a byte**, así que T0.3 no se movió.

**Y de ahí salió material didáctico que no estaba en el guion.** Una paleta cualitativa deja de
funcionar por encima de ocho o nueve clases, y trece bombas están por encima. Así que la vista por
defecto del mapa **no** es «un color por bomba» sino «Broad Street contra el resto», y conmutar entre
las dos *enseña* la limitación: con dos colores la pregunta de Snow se responde de un vistazo y con
trece el mapa es bonito y no se lee. Es el módulo 5 del capítulo 3 aplicado al propio componente.

Retropropagado en la misma sesión (regla del §9) a `plantilla-capitulo.html` y a
`prueba-geomapa.html`, que estrena dos casos permanentes —marca categórica con capas y marca numérica
con rampa—, los dos generados por `genera_demo_geomapa.R` y no fabricados a mano.

**Verificado con firma de color, no con recuento de tinta** (lección de A.5): las tres vistas dan
96, 287 y 173 colores distintos, y apagar las calles baja la tinta de 65 549 a 28 888 píxeles. Un
recuento habría dado lo mismo en las tres.

---

#### Ocho defectos, y seis estaban en herramientas que ya daban verde

**1. El ensamblador sustituyó DE MENOS, y salió en verde.** El ancla de cierre `\n    };\n` casó con
el final del **primer** simulador de demostración y dejó vivos los otros dos. Archivo bien formado,
consola limpia, informe limpio; los dos simuladores zombis solo se veían en la línea «registrados y
no usados» del propio informe. Es el **fallo simétrico** del que se llevó 276 líneas en T0.5:
*sustituir de menos es tan silencioso como sustituir de más*. `reemplaza_region()` tiene ahora
**tope mínimo además de máximo**.

**2. Un tipo de pregunta que el motor no conoce se lleva por delante media página.** Escribí cinco
preguntas `tipo: 'vf'` y el motor solo entiende cuatro tipos. No da error de sintaxis: revienta
dentro de `iniciarAutoevaluaciones()`, y `loadModule()` llama a `iniciarGeomapas()` **después**, así
que el mapa de Snow no se pintaba —en **un módulo de doce**, con los otros once perfectos—. Se
descubrió recorriendo los doce con la consola instrumentada, que es exactamente lo que T1.3 pide y la
razón por la que lo pide. Las cinco se convirtieron en `opcion` con Verdadero/Falso —que además gana
retroalimentación por opción— y una en `grafico`, el cuarto tipo, que faltaba. El ensamblador
comprueba ahora que **no haya tipos inventados y que estén los cuatro**.

**3. Un espacio fino dentro de una fórmula.** `\(n = 1 000\)` con U+202F: KaTeX avisa
«Unrecognized Unicode character (8239)» y deja un hueco sin métrica. El aviso salía en la consola de
**un módulo entre doce**. Se añadió `ent_mate()` —que usa `\,`— y un guarda en el ensamblador que
recorre todas las fórmulas buscando espacios que KaTeX no entiende.

**4. Desbordamiento horizontal a 375 px, y `overflow-x` sobre un `<table>` no lo arregla.** La tabla
de seis columnas del módulo 2 empujaba el documento a **417 px** aunque el propio `<table>` declarara
`overflow-x: auto` y midiera 303. `overflow` sobre una caja de tabla es una de esas propiedades que el
motor puede ignorar, y la ignoraba. La alternativa —`display: block` sobre la tabla— sí desplaza pero
**le quita el rol de tabla a los lectores de pantalla**, y ése es un precio que este material no paga.
Se resuelve con `envolverTablas()`, que envuelve **cada** tabla en un contenedor propio con
`role="region"`, `aria-label` y `tabindex` —sin el `tabindex`, quien navega sin ratón no llegaría a
las columnas de la derecha—. Va en el JS y no en el marcado para que valga también para las tablas que
fabrica un componente. Verificado forzando el contenedor a **318 px**: los doce módulos dentro.

**5. El auditor de prosa miraba solo la PRIMERA autoevaluación.** El capítulo 1 tiene dos —la
diagnóstica y la del cierre— y `accesibilidad()` usaba `re.search`. Se le rompió el marcado del
segundo quiz y el auditor informó **0 fallos**. Lo destapó el arnés de inyección, no una lectura. Es
la trampa de alcance de T0.5 con otra cara: *comprobar el primero y dar por buenos los demás*.

**6. El colapso de millares del auditor fallaba si el número iba pegado a una letra.** Tras quitar los
espacios normales, «4 096 celdas» queda como `4<fino>096celdas`, y el `\b` final de la expresión no
encuentra frontera después del `096`. El auditor denunciaba `096`, `632` y `056` como cifras sin
respaldo: **tres falsos positivos sobre un capítulo correcto**, que es la forma más rápida de que
alguien deje de leer el informe. Es un defecto del **núcleo compartido**, así que estaba en todos los
capítulos que vengan.

**7. La comprobación de cortes de clase no tenía sujeto posible.** Los cortes del HTML salen de
`cap1_mapas.json`, y el auditor solo indexaba el JSON de cifras: la comprobación «cada corte está en
el precálculo» **no podía pasar nunca**. Pero el archivo de geometría tampoco puede entrar por la
puerta principal —sus decenas de miles de coordenadas cuantizadas convertirían casi cualquier número
de cuatro dígitos de la prosa en «respaldado»—. Entra por un parámetro propio, `json_mapas`, del que
se indexan **solo los cortes**.

**8. Y el arnés decidía por el NOMBRE del defecto.** Para quitar un tema de todas partes había que
llamar al defecto «se cae…»; con cualquier otra redacción se sustituía solo la primera aparición y el
tema seguía en el documento. El capítulo 1 perdió así **cinco inyecciones de golpe**, y el arnés las
apuntó como «no detectadas» cuando el auditor no tenía la culpa. Ahora se declara con un cuarto campo.

**Dos cuentas más que estaban mal, las dos en `cuenta_sitio.py`:** contaba solo las `#>` escapadas
—14 donde hay 26— y buscaba el árbol por `data-arbol`, que no es como se cablea: informaba **0
árboles** sobre un capítulo que tiene uno. Un contador que informa de menos es tan inútil como uno que
informa de más, y el §8 del plan dice que los totales se cuentan y no se recuerdan.

---

#### La comprobación que hubo que AFINAR en vez de aflojar

`geomapas()` exigía cortes de clase a **todo** mapa. Valía mientras el único sujeto era un coropleto
de demostración; con el capítulo 1 deja de valer, porque un patrón puntual coloreado por una marca
**categórica** no clasifica nada y no debe traer cortes. Exigírselos habría dado MAL sobre un mapa
correcto — y un auditor que denuncia lo que está bien se acaba desactivando, que es la peor manera de
perderlo (es la contracara de A.3 y de la comprobación demasiado estricta de A.8).

La regla se afina en vez de aflojarse, y **ningún mapa se queda sin nada que comprobar**:

| Modo | Qué se le exige |
|---|---|
| `poligonos`, `rejilla` | los cortes de clase, calculados por `classInt` en R |
| `puntos` con marca **numérica** | que declare `marcas_tipo`; los cortes solo si los trae |
| `puntos` con marca **categórica** | que declare `marcas_tipo` **y** sus `niveles`, y que **cada código caiga dentro del rango** |
| `puntos` sin marca | nada que comprobar, y se dice |

Además, el `n` declarado de un mapa de puntos se compara ahora contra `pts` —antes la comprobación
pasaba por `real == 0`, o sea **no comprobaba nada** sobre los seis mapas de puntos del capítulo— y se
exige **una marca por punto**.

---

#### Lo que el capítulo mide, y con qué se verificó

| | |
|---|---|
| `ensambla_cap1.py` | 12 módulos · 9 simuladores · 9 mapas · 16 preguntas · 4 ejercicios · 8+8 bloques R/Python · **26 cifras anunciadas** |
| `audita_cap1.py` (precálculo, en Python) | **836 comprobaciones, 0 fallos, 3 saltadas declaradas** |
| `prueba_auditor_cap1.py` (inyección al precálculo) | **49 de 49** |
| `verifica_bloques.py --todos` | **115 de 115 cifras anunciadas** aparecen en la salida real, 0 bloques con discrepancias |
| `audita_texto_cap1.py` (prosa, 171 líneas) | **138 comprobaciones, 0 fallos** |
| `prueba_texto.py` (inyección a la prosa) | **cap1 30 de 30 · demo 36 de 36** (sin regresión en el fixture de T0.5) |
| `prueba_reproducible.sh` | los tres JSON **idénticos byte a byte** en dos ejecuciones, tras haber tocado `geo.R` y `genera_cap1.R` |
| Navegador, los 12 módulos | consola **limpia**, KaTeX **sin avisos**, `geomapasVivos` nunca por encima de los lienzos en **60 cambios de módulo**, los **9 simuladores** con todos sus controles pulsados dos veces y el árbol recorrido rama a rama sin una sola excepción, sin desbordamiento a 1 280 ni con el contenedor forzado a 318 px |
| Peso | **492 KB**, dentro del rango 350–550 del §8 · geometría 88,7 KB de 120 |

**`precalculo/audita_todo.sh` completo: ARNÉS EN VERDE**, los siete pasos. Tarda ~20 min; ahora
recorre también los `audita_texto_capN.py` que existan, así que sirve igual conforme se añadan
capítulos.

**Cuatro familias de inyección nuevas**, todas alrededor de la marca de un mapa de puntos:
`marcas_tipo` que desaparece, `niveles` que desaparece, un código fuera de rango y una marca de menos.

---

#### Los enlaces locales: una comprobación sin sujeto, y cómo se arma sola

El capítulo 1 no tiene enlaces **locales** —todas sus referencias son externas—, y `enlaces()` hacía
`exige(not rotos)`: con la lista vacía, **pasaba en verde sin haber comprobado nada**. Sobre el
informe eso se lee exactamente igual que una comprobación que sí verificó algo.

Y el motivo de que no los haya es legítimo: **el sitio no existe todavía**, la portada es T7.1. El
problema no es del capítulo, es que la comprobación no tenía sujeto.

Poner un mínimo a mano —«exige al menos un enlace»— habría obligado a acordarse de subirlo en la
Fase 7, y lo que hay que recordar se olvida. En vez de eso **la comprobación mira la carpeta**: hoy
declara en voz alta que no hay nada con lo que enlazar, y **en cuanto aparezca al lado un
`index.html` o el capítulo 2 exige que este capítulo enlace a alguno**, sin que nadie toque una
línea. Verificado creando un hermano de mentira: el auditor pasa de 0 fallos a 1.

**Y la exclusión simétrica, que se me olvidó y cazó el arnés.** La primera versión excluía los
bancos de prueba como *destino* pero no como *sujeto*, así que en cuanto existió el capítulo 1 el
fixture de T0.5 empezó a fallar su control — y **con el control caído, sus 36 inyecciones dejaron de
probar nada**: el arnés informó `demo: 0 de 36`. Un banco de pruebas no es material del curso y no
tiene que enlazar con el sitio.

Se añade además la inyección de la familia 7, que nunca se había ejercitado aquí: **un enlace local
que no resuelve**, fabricado convirtiendo una referencia externa en local. El arnés del capítulo pasa
de 29 a **30 de 30**, y el total a **66 de 66**. La otra rama —la que se arma sola— **no tiene
inyección permanente y se dice**: fabricar un archivo hermano no cabe en un arnés que sustituye texto
sin tocar el proyecto, así que **su inyección entra en T7.1**.

*(Decisión de Javier: no se adelanta un `index.html` provisional. La comprobación ya no se puede
olvidar, y T7.1 escribirá la portada de verdad.)*

**Hallazgo colateral, en otro curso:** los **8 capítulos publicados de Muestreo no tienen enlace de
vuelta al índice** —el índice lleva a ellos y son callejones sin salida—, mientras que los **10 de
Diseño de Experimentos sí lo tienen**. Anotado en la memoria de Muestreo como pendiente; no se toca
desde aquí.

---

#### Una lección de contenido, no de herramientas

El módulo 4 mide por dos frentes porque uno solo no basta, y las cifras lo justifican: la simulación
da un factor de **7,85798** con una correlación que elegimos nosotros, y el dato colombiano real da
**4,16822** con la que tiene Colombia. El primero demuestra el mecanismo; el segundo, que ocurre.
Publicar solo el primero sería enseñar un montaje, y publicar solo el segundo dejaría la duda de si el
efecto es otra cosa. La misma receta —**dos caminos hasta el mismo sitio**— es la que salvó la falacia
ecológica en A.8 y el barrido de los 13 pares en A.11.

---

### A.13 · El capítulo 2: la indicatriz de Tissot y doce defectos (T2.1–T2.3)

#### Las cuatro decisiones de Javier, y las cuatro se aceptaron

Del 2026-08-04, antes de escribir una línea: **el módulo 9 degrada a propósito las coordenadas
buenas** en vez de fingir un geocodificador · **`geo_tissot()` mide el ángulo además del área** y el
`.geomapa` dibuja las indicatrices · **el geohash se implementa a mano**, sin instalar `h3jsr` ·
y el capítulo se **densifica a 12 preguntas y 5 ejercicios** porque cubre dos semanas.

#### El hallazgo grande: la referencia de área estaba mal, y lo delató una propiedad exacta

`geo_proyeccion()` comparaba el área proyectada contra `st_area()` **con s2 encendido**, es decir
contra una **esfera**. Sobre los 1122 municipios de Colombia esa esfera infla
el área un **0.43657 %** de mediana, y ese porcentaje
se colaba entero dentro de la razón.

Lo que lo destapó no fue una intuición: **EPSG:3116 tiene k = 1, así que su razón de área NO PUEDE
bajar de 1**, y con la referencia esférica salía **0,9962**. Un número plausible, con buena cara y
falso. Corregido —la referencia es el elipsoide, vía lwgeom— las dos propiedades teóricas salen
exactas: **9377 da 1.000000 = 0,9992²** y **3116 da
1.006747 = 1²**.

**Y esto corrige cifras de T0.3 que estaban publicadas.** El `demo_geomapa.json` cambia: Web
Mercator sobre 177 países pasa de razón mediana **1,215908 a 1,218503** y de estiramiento **64,9034
a 64,0927**; Equal Earth pasa de 0,996101 a **0,999029**, que es lo que una equivalente debe dar.
La vista «4326 sin proyectar» daba exactamente 1,000000 porque **se comparaba consigo misma**: era
una comprobación incapaz de fallar.

#### El archipiélago da la vuelta a la recomendación, y casi publico lo contrario

Iba a escribir que 9377 minimiza el peor caso nacional, que es para lo que el IGAC le puso
k = 0,9992. **Sobre el país entero el dato dice lo contrario**: gana 3116, porque el peor caso de
los dos es San Andrés y el archipiélago está 700 km mar adentro, más cerca del meridiano de 3116
(−74,08) que del de 9377 (−73). Separando continente e islas se ve lo que de verdad pasa:

| | peor caso | mediana |
|---|---|---|
| **Continente** (1120 municipios) | 9377 **0.94901 %** < 3116 1.55012 % | 3116 **0.04425 %** < 9377 0.13369 % |
| **Con el archipiélago** | 3116 **1.72424 %** < 9377 2.08895 % | — |

**Dos municipios de 1122 cambian la respuesta**, y eso es mejor material que
la frase que yo tenía preparada. El ejercicio 1 lo convierte en el problema: elige con tres
municipios continentales, y después añade San Andrés a ver si tu recomendación aguanta.

#### Dos ejercicios que había que rehacer porque su respuesta era CERO

- **E2** preguntaba por un buffer de 5 km sobre las 361 estaciones del IDEAM, y la respuesta era que
  no cambiaba **ninguna** cuenta: Colombia está casi sobre el ecuador y 5/111,32 grados mide 4,98 km.
  Cierto y didácticamente inútil. Rehecho sobre las 2 209 sedes de Bogotá, que están mil veces más
  juntas: a 500 m de radio cambian **161 sedes
  (7.28837 %)** y a 1 km,
  **399**. El caso ecuatorial no se tiró: es la última
  pregunta del enunciado.
- **E4** preguntaba a cuántas estaciones les cambia el vecino más próximo al medir en grados, y la
  respuesta era **cero** —cerca del ecuador un grado de longitud mide el
  0.99548 de uno de latitud y el orden no se altera—. El cero no se
  escondió: **se convirtió en la mitad del ejercicio**, contra un umbral de vecindad, que sí falla
  (107 pares a 200 km). *El vecino más próximo es una
  pregunta de ORDEN y sobrevive; el umbral es una pregunta de MAGNITUD y no.* Es la decisión que
  abre el capítulo 6: `dnearneigh` contra `knearneigh`.

#### Y una medida que era una anécdota

El sesgo del módulo 9 se midió al principio con **una sola realización** del ruido. Daba
correlaciones de 0,38 o de 0,72 según la semilla, y localidades con «20,00 %» que eran cuatro sedes
de veinte. Con **200 réplicas** pasa a ser una medida: tasa
global **3.03395 %** ± 0.02160,
de **0.22165 %** a
**12.42857 %** según la localidad, con correlación
**0.62435** (Pearson) y
**0.68382** (Spearman) contra perímetro/área. **El sesgo es
geométrico y predecible antes de tener el dato**; por estrato no hay patrón monótono, y eso también
se publica porque es la lectura que un lector esperaría encontrar.

#### El ancla externa que valida la simulación

Degradar las coordenadas buenas a dos decimales deja
**360 posiciones** para
2209 sedes, o sea 6.1361 sedes
por posición. La fuente del MEN que T0.4 descartó traía dos decimales **de verdad** y allí eran
2403/398 =
6.0377. La simulación reproduce la fuente
real, y el generador **para** si dejaran de parecerse.

#### Doce defectos, y cinco los encontró una herramienta sobre trabajo que ya daba verde

1. **La referencia de área esférica** (arriba). La cazó una propiedad exacta, no una revisión.
2. **`geo_tissot` sobre un CRS geográfico medía grados por metro.** Con 4326 la «proyección» es la
   identidad, la jacobiana salía del orden de 1e-7, la escala de área daba 0,000 y **las elipses se
   dibujaban con radio cero**. Los ángulos sí estaban bien —ω no depende del factor global—, así que
   el informe parecía casi correcto. Lo cazó **el banco de pruebas**, que es para lo que existe.
   Arreglado declarando la interpretación: dibujar lon/lat en un plano **es** la plate carrée.
3. **Y con ella, las unidades del radio base.** La caja de una vista geográfica está en grados y el
   radio en metros: `rq` salía en millones. `geo_tissot()` devuelve ahora el factor para deshacerlo.
4. **`registrarGrafico` no existe.** El contrato del motor es *devolver* los gráficos. Escribir de
   memoria una función que no existe costó un `ReferenceError` que se llevó por delante
   `iniciarSimuladores()` **entero** — el mismo modo de fallo del defecto nº 2 de A.12.
5. **Una clase de CSS inventada.** El lienzo iba en un `.simulador-lienzo` que no existe: medía cero
   de alto, Chart.js creaba el gráfico sin quejarse y **los diez simuladores salían en blanco**, con
   la consola limpia. Solo se ve midiendo la tinta del lienzo.
6. **El `<div class="quiz-container">` no es el marcado que el motor espera**, y `renderAutoevaluacion`
   reventaba con un TypeError que tumbaba todo lo que `loadModule()` llama después.
7. **Tres huecos del auditor de precálculo**, encontrados por el arnés: las cifras publicadas del
   archipiélago no se contrastaban contra el recálculo (solo su relación); la comprobación de
   codificación buscaba **la presencia de la cadena buena** en vez de **la huella de la corrupción**,
   y como «Bogotá» aparece muchas veces, corromper una no la hacía fallar; y el tope de decimales es
   **incapaz de fallar** sobre magnitudes de siete cifras enteras, porque un `double` no puede
   llevar más de diez decimales ahí. Declarado con `salta()`.
8. **Once fallos del auditor de prosa sobre el capítulo recién escrito**: cifras sin respaldo, tres
   fuentes sin citar, los ejercicios sin botones accesibles, ningún mapa con tabla de respaldo, y
   **el capítulo sin enlazar al 1**.
9. **La comprobación de enlaces se armó sola.** En cuanto apareció el capítulo 2 al lado, `enlaces()`
   pasó a exigir que **el capítulo 1** enlazara a alguno, y falló. La rama que A.12 dejó declarada
   como hueco ya tiene sujeto, y nadie tuvo que acordarse: está escrita para eso.
10. **Publiqué ω con tres decimales**, por debajo de la regla de los cinco. La perturbación del
    último dígito la absorbía el índice, y lo destapó el arnés de prosa.
11. **Escribí `0{,}9992` dentro de una fórmula de KaTeX.** Con esa convención el número queda
    **invisible** para `cifras()`: una cifra falsa ahí se publicaría sin que nadie la viera. El
    capítulo escribe los decimales con punto dentro de las fórmulas, como el capítulo 1.
12. **Seis `#>` anunciaban decimales que el código no imprime.** R imprime siete cifras
    significativas, así que `round(111319.49, 2)` sale como `111319.5`. Los bloques se ejecutan
    encadenados —como los leería un estudiante— y `verifica_bloques.py` los cazó todos.

**Y tres «vectores canónicos» de geohash que escribí de memoria y eran falsos.** De seis, tres no
cuadraban. La implementación era correcta: lo demuestra el **round-trip**, que comprueba que cada
punto cae dentro de la caja de su propia celda —**11045
de 11045**— y los dos vectores que sí están
publicados (`ezs42` de Wikipedia y `9q8yyk8y` de San Francisco). Los otros tres los había inventado.
**Verificar por decodificación, no por memoria.**

#### Dos herramientas nuevas que quedan para los ocho capítulos que faltan

- **`audita_base.py` y `prueba_auditor_base.py`.** El contador, el registro de fallos, el formato del
  informe y la maquinaria de inyección se sacaron de `audita_cap1.py`, que los llevaba dentro. Con
  dos copias todavía se puede arreglar un fallo en un sitio; con diez, no — es la lección que
  `audita_texto_base.py` ya había aprendido en T0.5. **Verificado sin regresión: el capítulo 1 sigue
  dando 836/0 y su arnés 49/49.**
- **`sincroniza_prueba_geomapa.py`**, arriba.

#### Una trampa nueva del entorno, y hay que anotarla

Ya sabíamos que **el panel del navegador miente cuando está oculto** (`innerWidth` y `clientWidth` se
desacoplan). Ahora sabemos más: **con el panel oculto `requestAnimationFrame` no dispara**, así que
**Chart.js nunca pinta** y todos sus lienzos miden cero tinta. Los `.geomapa` sí pintan, porque
dibujan de forma sincrónica. Para verificar un gráfico hay que **forzar `chart.draw()`**; medir sin
forzarlo da un falso negativo perfecto.

#### Lo que el capítulo mide

| | |
|---|---|
| Datum Bogotá 1975 leído como WGS84 | **490.68 m** de media |
| Un grado de longitud, del ecuador a 80° | 111319.49 → **19393.25 m** |
| Web Mercator: ω máxima (NO es conforme) | **0.38485°** |
| Conformes y equivalentes a la vez, de 6 | **0** (teorema de Tissot, comprobado) |
| La esfera de s2 infla Colombia | **0.43850 %** = 4,991 km² |
| `st_set_crs` mueve | **0** vértices de 57,840 |
| Campos que el shapefile desfigura | **5 de 9** (no los trunca: les quita vocales) |
| Estaciones invertidas que caen en Colombia | **0** de 361 (355 en la Antártida) |
| Sedes con el vecino en otra celda de geohash 7 | **78.49706 %** |
| El índice reduce los pares a evaluar | **11.11×** |

### A.14 · El capítulo 3: el MAUP medido, y el presupuesto que no daba (T2.4–T2.6)

#### Las cuatro decisiones de Javier, y las cuatro se aceptaron

Del 2026-08-05, antes de escribir una línea: **los módulos 8, 9 y 10 sobre un solo dato** (Saber 11,
el único con nivel individual) · **`cartogram` instalado y además dos cartogramas propios** ·
**la estratificación colombiana como caso ancla** del módulo de ética · y **la simulación de
daltonismo dentro del motor `.geomapa`**, no en un simulador suelto.

#### El hallazgo grande: 1 122 municipios NO caben en 120 KB, y nadie lo había probado

El §4 fija ~120 KB de geometría por capítulo y afirma que «los 1 122 municipios simplificados a
tolerancia visual» caben. **No caben con ninguna tolerancia.** El suelo de `ms_simplify` con
`keep_shapes = TRUE` es **estructural** —cada polígono conserva su anillo mínimo—, así que 1 122
rasgos no bajan de **12 547 vértices ≈ 150 KB**. Los capítulos 1 y 2 nunca lo tocaron porque su
mapa «municipal» es en realidad **departamental**: 33 rasgos y 1 180 vértices.

El primer ensamblado pesaba **653 KB de geometría**. Se bajó a **199,6 KB** por tres vías medidas,
y el presupuesto de este capítulo queda declarado en **200 KB**:

1. **Capas: una geometría, cuatro variables.** El capítulo pinta el mapa municipal cuatro veces
   —deserción, conteo, tasa y presencia en la cohorte—. `geo_poligonos()` acepta ahora `capas`, y
   los valores van alineados a los 1 122 rasgos **con NA donde no hay dato**, lo que además permite
   que capas de distinta cobertura compartan geometría y que el mapa *enseñe* dónde falta el dato.
   **−367 KB.**
2. **Cuantización por mapa.** El mapa municipal va a `q = 1024` en vez de 4096: sobre un lienzo de
   900 px el error pasa de 0,22 a 0,88 px —menos de un píxel— y cada coordenada pierde un carácter.
3. **Codificación por diferencias.** `codificacion: "delta"` guarda incrementos en vez de
   coordenadas absolutas: **−33 %** medido, con round-trip exacto (son enteros). Va como **opción**
   y no por defecto, para no obligar a regenerar y reauditar los capítulos 1 y 2.

**Y el mismo error reapareció una capa más arriba:** al registrar los mapas en el JS, la geometría
municipal se incrustaba **tres veces**, una por cada `div` que la usa. El capítulo pesaba 954 KB.
Solo se ve mirando el tamaño del archivo.

#### `jsonlite` escribe los NA como la CADENA "NA"

`na = "null"` no es opcional, y `null = "null"` **no lo cubre**: gobierna los NULL, no los NA. Sin
él el navegador recibe texto donde espera un número, y en JS eso no revienta —`"NA" >= 1` es
`false` y la aritmética da `NaN`—, así que el municipio saldría sin color con la consola limpia.
Los capítulos 1 y 2 nunca lo pisaron porque filtraban los NA antes de construir el mapa. Ahora hay
una guarda que **para**.

Y su gemelo en el navegador: **`isFinite(null)` es `true`** en JS, porque `Number(null)` es 0. El
pintor daba a los municipios sin dato la clase 0 —un color de la rampa— dejándolos indistinguibles
de la clase más baja.

#### La pareja «a igual luminosidad» no estaba a igual luminosidad

El módulo 5 iba a publicar que el rojo y el verde de Tableau (`#D62728`, `#2CA02C`) están a la
misma luminosidad. **No lo están:** L* 46.85 y 57.90, once puntos. La afirmación
era falsa y además le quitaba fuerza al argumento, porque parte de la distancia que sobrevive es
luminosidad. Lo cazó el auditor, que **mide** el L* en vez de creérselo. La pareja se construye
ahora en HCL, donde la luminosidad es un parámetro, y una guarda comprueba la construcción: la
caída bajo deuteranopía pasa a ser del **94.41686 %**.

#### El resultado que salió al revés de lo que yo esperaba

Predije que las particiones **contiguas** darían correlaciones más altas que las arbitrarias. El
dato dice lo contrario: contiguas **0.54182** de media, arbitrarias
**0.68834**. En vez de contar una historia, se midió el mecanismo:
cada partición se calcula **dos veces**, con el ponderador y sin él. Al quitarlo la brecha pasa de
0.14652 a
0.29065 y las contiguas caen a
-0.01758. **La causa es el ponderador**: una zona arbitraria
la fija el municipio grande que le tocó. *El ponderador es parte del trazado aunque no se dibuje.*

#### El ancla que destapó a quién le falta el mapa

`r_de_zona()` sobre la partición departamental real daba 0.50763943 y la escalera publicaba
0.51260969. El ancla paró el generador. La diferencia son los
**262 estudiantes** cuyo municipio no tiene polígono
—Belén de Bajirá—. No se parcheó: hay **dos escaleras**, la de todos y la cartográfica, los módulos
8 y 9 usan la segunda porque es la que cubre la misma población que las particiones aleatorias, y
**la diferencia se publica** como la medida del módulo 11.

#### Otros defectos que hay que recordar porque se repetirán

1. **Uní dos capas por el NOMBRE** y los nombres no coinciden («Bogota Capital District» contra
   «Bogotá, D.C.», «Quindío» contra «Quindio»). Los departamentos se **derivan disolviendo** los
   municipios por su código, que además es lo que el capítulo enseña; se contrasta contra la capa
   oficial por área (0.060690 % de diferencia).
2. **Agrupé por el VALOR en vez de por un identificador** en el reparto del hexbin. Funcionaba solo
   porque los 33 conteos resultan ser distintos entre sí.
3. **`fread` lee `divipola` como ENTERO** y «05667» pasa a 5667: el `sprintf("%05d")` de T0.4 al
   revés. Se lee siempre con `colClasses = c(divipola = "character")`.
4. **Dos agregados municipales con cobertura distinta** daban r = 0,103 y 0,100 para «lo mismo». Se
   escriben los dos CSV con el sufijo que declara su cobertura.
5. **La caja compartida del módulo 7 no cubría el hexbin**: vértices en −144 y 4262 con q = 4096.
   Lo cazó una comprobación **nueva** de `audita_base`, que decodifica las diferencias y mira dónde
   caen los vértices de verdad.
6. **Escribí las cifras del bloque de código desde una sonda sobre departamentos**, no sobre los
   1 121 municipios. `verifica_bloques.py` las cazó: es exactamente la violación de D10 para la que
   existe.
7. **`pd` sin importar** en un bloque de Python: como los bloques se ejecutan encadenados, mató la
   sesión entera y **todos** los bloques de Python de aguas abajo salieron vacíos. 63 de 113.
8. **`n5` no lo trae la plantilla**, lo define cada capítulo. Suponerlo costó un `ReferenceError`
   que se llevó `iniciarSimuladores()` — el mismo modo de fallo del defecto nº 4 de A.13.
9. **Publiqué un percentil con 2 decimales**, dentro del punto ciego del auditor. Lo destapó el
   arnés de prosa, igual que en A.13.
10. **Tres defectos de MARCADO INVENTADO, los tres del mismo tipo que la `.simulador-lienzo` de
    A.13** —marcado plausible que no existe, sin ningún error en consola—, y los tres solo se ven
    pulsando o contando:
    · los ejercicios usaban `data-ejercicio` y `.ejercicio-solucion` en vez de `.ejercicio-guiado`
      y `.ejercicio-panel`, así que `cuenta_sitio.py` informaba de **cero ejercicios** sobre un
      capítulo que tiene cuatro, y el desplegable no se cableaba;
    · las preguntas iban en la misma línea que su llave, y el contador —que busca `\n        tipo: `—
      daba **cero preguntas** sobre las ocho que hay;
    · **los controles de los mapas iban DENTRO del div del mapa**, y `iniciarGeomapas()` reescribe
      ese `innerHTML`: se los llevaba por delante. Van como HERMANO, como en el banco de pruebas.
11. **`cablearCap3()` estaba definida y no se llamaba.** El capítulo se veía perfecto y los botones
    no escuchaban nada. Se engancha al ciclo de carga, justo detrás de `iniciarGeomapas()`.
12. **El conmutador de daltonismo no alcanzaba al modo `proyeccion`**: dieciséis colores del motor
    no pasaban por el filtro, entre ellos el **rojo contra verde oscuro de las islas del grafo**,
    que es justo la pareja que el módulo 5 enseña que colapsa. Y `geomapaTinta` **descartaba el
    canal alfa**, así que las capas translúcidas se volvían opacas al conmutar.

#### Lo que queda para los siete capítulos que faltan

- **`geo_poligonos()` sabe hacer cuatro cosas nuevas**: `capas`, `vistas`, `superpuestos`,
  `caja` explícita, `q` por mapa y `delta`. Todas retrocompatibles.
- **`geo_carto_ncont()` y `geo_carto_dorling()`**, con propiedad exacta —corr(área, valor) = 1— y
  contraste externo contra `cartogram`, cuya normalización difiere en un **factor global**
  (cv = 0e+00).
- **`geo_cvd()`**, verificada contra `colorspace` en 153 comparaciones,
  y su gemela en JS verificada contra las anclas del JSON: **153 de 153 hexadecimales idénticos**.
- **El conmutador de daltonismo es del MOTOR**, así que alcanza a los mapas de los capítulos 1 y 2.
- **`audita_base.audita_geomapa()`** ya no cablea `q = 4096`: comprueba que la cuantización sea una
  de las declaradas **y que los vértices caigan dentro**, decodificando las diferencias.

#### Trampa nueva del entorno

Ya sabíamos que con el panel oculto `requestAnimationFrame` no dispara y Chart.js no pinta (A.13).
Ahora sabemos más: **el ancho del lienzo sale 0**, así que no basta con forzar `chart.draw()` —hay
que **forzar un ancho al contenedor y llamar a `chart.resize()`** antes—. Sin eso, los diez
simuladores miden cero tinta sobre un capítulo perfecto.

#### Lo que el capítulo mide

| | |
|---|---|
| Configuraciones de esquema × k, y mapas realmente distintos | 35 → **24** |
| Municipios que cambian de clase entre los dos esquemas más discordantes | **80.01784 %** |
| Municipios con la misma clase en los cinco esquemas | **224** de 1121 |
| En la clase más alta, según el esquema | **2 / 225 / 48 / 1 / 0** |
| Solape de los top-20 por conteo y por tasa | **1** de 20 |
| Condados de `nc` empatados justo en un corte de cuantiles | **39** |
| Rojo/verde a igual luminosidad, bajo deuteranopía | **94.41686 %** menos |
| Olson y Dorling propios: corr(área, valor) | **1,000000** exacta |
| Dougenik con 60 iteraciones | **0.816941** |
| Escalera: individuo → municipio → departamento | **0.36272 → 0.30333 → 0.51261** |
| Varianza del puntaje que sobrevive al agregar a municipio | **14.88168 %** |
| Recorrido de r sobre 1 000 zonificaciones contiguas | **0.70922** |
| Percentil del trazado departamental real | **25.80000** |
| Gerrymandering: escaños de A con el 64.00 % de los votos | **2 a 4** de 5 |
| El estrato invierte el signo con el umbral | **-0.05765 → 0.63128** |
| Estudiantes sin polígono en el mapa | **290** |

---

### A.15 · La sigla que solo estaba en el título: la entrada sobre el SIG (2026-08-14)

**Cómo salió.** Preguntando dónde cubre el material el primer tema del syllabus —«Sistemas de
información geográfica (SIG); sistemas de referencia de coordenadas y proyecciones; distorsión y
criterios de elección»—. Las dos últimas partes estaban de sobra: la distorsión, **medida**, en el
módulo 3 (seis proyecciones, indicatriz de Tissot, ω y la razón de área), y los criterios de
elección en el módulo 4, con el archipiélago dando la vuelta a la recomendación. La primera, no.

`grep -o "Sistemas de [Ii]nformación [Gg]eográfica"` sobre todo el sitio: **cero resultados**. La
sigla aparecía en el título del capítulo, en el `<title>` y en el metadato del JSON, y en ninguna
línea de prosa. El capítulo entraba directo al elipsoide. El syllabus, en cambio, no solo nombra el
tema: le pone estrategia —«Exposición de SIG y sistemas de referencia; laboratorio de manejo de
geometrías con `sf`»—. Estaba el laboratorio y faltaba la exposición.

**Por qué se coló.** El §6 de este plan no le dio módulo propio, y el auditor de prosa solo puede
denunciar lo que su `DEBE_CUBRIR` declara: los veintisiete temas de la lista estaban todos, así que
el informe daba verde sobre un capítulo con un hueco. Es la misma forma de fallo que A.10 —el
arnés solo ve lo que se le enseña a ver—, aplicada al temario en vez de a las cifras.

**Qué se hizo.** Cinco párrafos y una caja `.definition` al abrir el módulo 1, antes del geoide:

1. qué es un SIG, y por qué la definición de manual («capturar, almacenar, analizar, representar»)
   describe igual de bien a una hoja de cálculo — lo que separa a un SIG de una tabla es que **la
   posición es un atributo de primera clase**;
2. las tres piezas que convierten una tabla en una capa —geometría con tipo, CRS declarado,
   operaciones que respetan la geometría—, anclada en las 20 localidades de Bogotá y sus 57 840
   vértices, que son datos del propio capítulo;
3. **Simple Features** (OGC, ISO 19125) como el estándar que hace que R, Python, PostGIS y QGIS
   entiendan la misma geometría, y de dónde viene el nombre del paquete `sf`;
4. vectorial contra ráster, y que este curso vive casi entero en el vectorial;
5. por qué el SIG del curso se escribe y no se pulsa —**un clic no deja rastro**—, con GDAL, GEOS y
   PROJ nombrados como los motores compartidos con QGIS;
6. y el reparto del capítulo: módulos 1–6, el sistema de referencia; 7–11, el dato y sus
   operaciones. Cierra con la frase que el auditor ahora exige: **una capa sin sistema de referencia
   declarado no es una capa**.

**Dónde NO se puso, y por qué.** No en un módulo 13. Renumerar habría arrastrado el `modulo:` de las
doce preguntas del quiz y las remisiones «Módulo N» repartidas por la prosa y por la
retroalimentación, a cambio de nada: lo que faltaba era encuadre, no una unidad de trabajo. El
objetivo del módulo 1 se amplió en la misma edición, porque el encabezado es un contrato (§9.1).

**Lo que se cerró detrás.** Cuatro entradas nuevas en `DEBE_CUBRIR` (`sistema de información
geográfica`, `simple features`, `ráster`, `qgis`) y dos en `AFIRMACIONES` (`atributo de primera` y
`no es una capa`), más `19125` en `ESTRUCTURALES`. Sin eso, el hueco se reabre en la siguiente
reescritura y nadie se entera. Arnés completo después: **135 comprobaciones de prosa sin fallos**,
110 de 110 defectos inyectados cazados, 72 de 72 guardas del ensamblador, ninguna cifra calculada
fuera de R, consola limpia y KaTeX intacto.

**Lección para los capítulos que faltan.** El `DEBE_CUBRIR` de un capítulo se escribe **desde el
temario del syllabus**, no desde el índice de módulos que uno acaba de redactar. Redactado desde el
índice, el auditor confirma que el capítulo dice lo que dice — que es justo lo que no hace falta
comprobar.

