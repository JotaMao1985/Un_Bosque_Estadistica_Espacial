# Estadística Espacial · Universidad El Bosque

Material de estudio interactivo del curso **Estadística Espacial (20929)**, programa de
Estadística, 2026-II.

**→ [Ver el material publicado](https://jotamao1985.github.io/Un_Bosque_Estadistica_Espacial/)**

Cada capítulo es una página HTML autocontenida —sin servidor, sin dependencias que instalar—
con mapas, simuladores, autoevaluación y el mismo análisis resuelto en R y en Python.

---

## Estado

Seis de los diez capítulos del plan están publicados, y con ellos el **Taller 1** y el
**preparcial del Corte I**, que no son capítulos y se cuentan aparte.

| # | Capítulo | Semana | Estado |
|---|---|---|---|
| 1 | Datos espaciales y la primera ley de la geografía | 1 | Publicado |
| 2 | SIG, sistemas de referencia y georreferenciación con `sf` | 2–3 | Publicado |
| 3 | Cartografía estadística y el MAUP | 4–5 | Publicado |
| 4 | Patrones puntuales: CSR y funciones de resumen | 6–7 | Publicado |
| 5 | Intensidad por núcleos y procesos puntuales | 8–10 | Publicado |
| 6 | Datos de área y la matriz de pesos espaciales | 10–11 | Publicado |
| 7 | Autocorrelación espacial global y local | 12–13 | En preparación |
| 8 | Econometría espacial: SAR, SEM, SDM y GWR | 14 | En preparación |
| 9 | Geoestadística: variograma y kriging | 15 | En preparación |
| 10 | ML espacial, datos espacio-temporales y proyecto | 16 | En preparación |

Los seis capítulos suman 72 módulos, 57 simuladores, 44 mapas, 73 preguntas de
autoevaluación, 28 ejercicios guiados y 64 bloques de código en cada lenguaje. Fuera de esa
cuenta van el Taller 1 —9 módulos y 7 ejercicios— y el preparcial del Corte I —7 módulos y
36 preguntas que cubren los 30 módulos de los capítulos 1 a 3 que entran en el parcial—.

El capítulo 6 es **el primero que publica grafos**, y su presupuesto lo decidió una medición: las
diez definiciones de vecindad que el temario pide pesan **465 KB sobre los 1 122 municipios** y
**18,9 sobre los 49 barrios de Columbus**. Por eso el capítulo tiene dos tableros y cada uno hace
lo suyo — el laboratorio, donde las diez caben y las cifras son las canónicas de Anselin; y el caso
real, con una sola vecindad y las patologías que solo trae un dato de verdad: dos islas y tres
subgrafos.

El capítulo 5 es **el primero que publica superficies** en vez de geometría, y eso le cambia el
presupuesto: sus diez rásteres de intensidad pesan 296 KB empaquetados —máscara aparte y
diferencias por fila, el 49 % del crudo— de los 755 KB del documento. Un contorno se simplifica sin
perder contenido; **un ráster no se simplifica, se muestrea**, y muestrear menos es dibujar la
rejilla en vez del núcleo. Por eso ahí el peso deja de ser un objetivo y pasa a ser una cifra que se
declara.

Ninguna de esas cifras está escrita de memoria: las cuenta `cuenta_sitio.py`, que es también
quien avisa si aparece un HTML que no encaja en ninguna de sus cuatro tablas.

---

## La regla que gobierna el repositorio

**Ninguna cifra del material está escrita a mano.**

Todo número que aparece en el texto lo calcula R desde las fuentes primarias, viaja al
navegador dentro de un JSON, y un arnés independiente lo recalcula en Python antes de
publicar. Si las dos vías no coinciden, el capítulo no sale.

No es una aspiración: está mecanizada por partida doble.

- `audita_capN.py` mira **el resultado** — ¿existe esta cifra en el precálculo?
- `sin_aritmetica.py` mira **la causa** — ¿algún número de la prosa se calcula en el
  ensamblador en vez de en R? Lo detecta con `ast`, no con heurística.

Las dos existen porque una sola no bastó. Un `61.7` del capítulo 1 vivió meses en el
material: lo calculaba el ensamblador, no existía en ningún JSON, y el auditor de
resultados lo dejaba pasar porque su índice tiene más de cien mil entradas y una cifra
de pocos decimales cae dentro por azar. Se encontró mirando el código que escribe las
cifras, no las cifras.

Los bloques de código tampoco se creen a sí mismos: `verifica_bloques.py` los **ejecuta**
y contrasta la salida real contra el `#>` que anuncian.

Y hay una tercera cosa que ni los resultados ni las causas destapan: **el dato que se
declara y no lo pinta nadie**. `courseData` traía tres campos que la barra lateral no leía,
y como no producían comportamiento, ninguna comprobación de comportamiento podía verlos —ni
el arnés, ni la consola del navegador—. Bajo esa cobertura el esquema llegó a partirse en
dos entre el capítulo 1 y el 2 sin que nada lo dijera. `campos_vivos.py` compara la
declaración contra la lectura, documento por documento, y exige además que el esquema no
diverja.

---

## Cómo se construye un capítulo

```
datos/ (no versionado)
   │
   ├── datos_*.R ................ descarga y fija las fuentes por SHA-256
   │
   ▼
genera_capN.R .................... calcula TODO en R, con semilla 2026
   │                               y anclas contra la literatura
   ▼
precalculo/salidas/*.json ........ el precálculo, versionado
   │
   ├──► audita_capN.py ........... lo recalcula en Python, independiente
   │
   ▼
ensambla_capN.py ................. interpola la prosa e inyecta el JSON
   │                               en la plantilla
   ▼
Htmls_Espacial/capitulo-N-*.html . lo que se publica
```

El HTML **es un artefacto**: no se edita a mano. Para cambiar una palabra del capítulo 1
se edita `precalculo/ensambla_cap1.py` y se vuelve a ensamblar.

---

## Reproducir

Requiere R 4.4 (compilación *framework*, no la de Homebrew: esa no trae `sf`) y el
entorno `geo_env` de Python. Las versiones exactas con las que se generó el material
están congeladas en `precalculo/versiones.json` y `versiones_py.json`.

```bash
precalculo/rscript.sh precalculo/genera_cap1.R
python3 precalculo/ensambla_cap1.py
```

`rscript.sh` no es un atajo: resuelve dos trampas del entorno —el `Rscript` del `PATH`
es el de Homebrew y no tiene `sf`, y `Rscript` arranca en `LC_CTYPE=C`, donde `jsonlite`
escribe las tildes rotas **sin fallar**—.

### En Windows

```powershell
.\precalculo\rscript.ps1 precalculo\genera_cap1.R
python precalculo\ensambla_cap1.py
```

`rscript.ps1` es el hermano del `.sh`, y **no hace lo mismo**: de las dos trampas, allí
una cambia de forma y la otra desaparece. La del R equivocado sigue, pero al revés —el
problema no es que sobren R, es que `Rscript.exe` no está en el `PATH` (el instalador de
CRAN no lo añade) y que cada versión instalada tiene su propia biblioteca de usuario, así
que arrancar la 4.6 cuando `sf` se instaló bajo la 4.4 da «there is no package called
'sf'» sin decir por qué—. Por eso el envoltorio busca el R y prefiere la versión que
`versiones.json` declara.

La de la codificación, en cambio, **no existe en Windows**: desde R 4.2 la compilación
UCRT usa UTF-8 como codificación nativa. Y si la máquina fuera vieja, el envoltorio no
podría arreglarlo —`LC_ALL=es_ES.UTF-8` no es sintaxis de allí, y apuntar a una regional
inexistente devuelve a R a `C` en silencio—, así que allí el remedio es la versión de R y
no un envoltorio. `utf8.R` lo dice con esas palabras cuando para, porque mandar a alguien
desde Windows a `rscript.sh` es mandarlo a un archivo que no existe.

Todo esto está **medido en un Windows 11 real**, no deducido: R arranca allí en
`LC_CTYPE = English_United States.utf8` con `l10n_info()$`UTF-8`` en `TRUE`, y `huella()` sin
`digest` cae en `certutil` y devuelve el mismo SHA-256 que `shasum` en macOS. Esa prueba
destapó tres cosas que ninguna lectura del código habría dado:

- **El instalador de CRAN en silencio no escribe la clave del registro**, y además cae en
  `Program Files (x86)` porque su Inno Setup es de 32 bits. Con el registro vacío y sin `PATH`,
  la única vía que le queda al envoltorio es recorrer las carpetas — por eso las recorre.
- **`rscript.ps1` tiene que guardarse en UTF-8 CON BOM.** Windows PowerShell 5.1 —el que trae
  Windows de serie— lee los `.ps1` como Windows-1252 si no lo encuentra, y cada tilde de sus
  mensajes sale rota sin que nada falle. El archivo lleva una guarda que lo dice en voz alta si
  el BOM se pierde al editarlo desde un Mac.
- **Y el BOM solo arregla la mitad.** La consola de Windows sigue escribiendo en una página de
  códigos heredada, así que «aquí» pasó de `aquA-` a `aqu?`: dos fallos distintos con el mismo
  aspecto. Hace falta fijar también `[Console]::OutputEncoding`.

**Lo que en Windows todavía no corre es el arnés.** `audita_todo.sh` es un guion de shell
y `verifica_bloques.py` codifica `rscript.sh` en una constante, así que la cadena de
generación es portable y la de verificación no. Reproducir el material en Windows sirve
para volver a calcular; para dar el visto bueno hace falta la máquina de siempre.

Para verificarlo todo:

```bash
precalculo/audita_todo.sh
```

Son ocho pasos: el precálculo recalculado en Python, un arnés que le inyecta defectos a
ese auditor para probar que sabe fallar, otro que hace lo mismo con las guardas del
ensamblador, la ejecución real de los bloques de código, el contrato entre el dato y quien
lo pinta, las cifras de la prosa, un arnés para el auditor de prosa y el recuento del
sitio. Tarda unas cuatro horas y media —la mayor parte en los arneses de inyección, que
arrancan el auditor entero una vez por defecto— y termina en `ARNÉS COMPLETO EN VERDE` o
no termina. Con `--rapido` se salta esos arneses y baja a unos minutos.

---

## Los datos

Sobre todo colombianos, junto a los casos canónicos de la literatura para que cada número
se pueda contrastar contra el libro de texto.

| Fuente | Qué aporta | Licencia |
|---|---|---|
| DANE (vía geoBoundaries) | Límites municipales y departamentales | CC BY 4.0 |
| DANE · DIVIPOLA | Códigos oficiales de entidad | CC BY-SA 4.0 |
| MEN | Deserción y cobertura neta 2024 | CC BY-SA 4.0 |
| SED y SDP Bogotá | Sedes educativas y perímetro urbano | CC BY-SA 4.0 · CC BY 4.0 |
| IDEAM | Normales climatológicas 1991-2020 | CC BY-SA 4.0 |
| ICFES | Microdatos Saber 11 | CC BY-SA 4.0 |

Cada conjunto está fijado por huella SHA-256 —o por *commit*, cuando la fuente lo
permite—. `datos.gov.co` reemplaza sus conjuntos en sitio conservando la URL: sin huella,
una fuente que cambia bajo los pies deja el material descuadrado en silencio.

La procedencia completa, verificada ejecutando y no leída de una ficha de metadatos, está
en [`precalculo/FUENTES.md`](precalculo/FUENTES.md).

### Descargar los datos

**Los 431 MB de `datos/` no se versionan** —345 MB de crudo y 86 MB de procesado—, así que
en un clon recién hecho esa carpeta no existe. La reconstruyen los `datos_*.R`, que descargan
cada fuente de su portal oficial, comprueban su huella SHA-256 y dejan las capas listas en
`datos/procesado/`.

**Antes:** hace falta R 4.4 y los paquetes del stack. Se instalan de una vez, y desde la
carpeta del curso:

```bash
precalculo/rscript.sh precalculo/instala.R
```

```powershell
.\precalculo\rscript.ps1 precalculo\instala.R
```

**Después, la descarga.** Es una sola orden; en macOS:

```bash
for g in datos_colombia llave_divipola datos_bogota datos_clima datos_saber11 verifica_t04; do precalculo/rscript.sh "precalculo/$g.R" || { echo "PARADO en $g"; break; }; done
```

Y en Windows, con PowerShell:

```powershell
foreach ($g in 'datos_colombia','llave_divipola','datos_bogota','datos_clima','datos_saber11','verifica_t04') { .\precalculo\rscript.ps1 "precalculo\$g.R"; if ($LASTEXITCODE -ne 0) { Write-Host "PARADO en $g"; break } }
```

Las dos paran en el primer guion que falle en vez de seguir con los datos a medias.

**El orden no es decorativo.** `llave_divipola.R` produce `municipios_llave.csv`, del que
dependen los tres siguientes a través de `carga_municipios()`. Y `verifica_t04.R` va al final
porque no genera nada: **vuelve a abrir los archivos ya escritos y los remide por un camino
distinto al del generador**, y sale con estado distinto de cero si alguna cifra no cuadra. Un
verificador que repitiera el cálculo del generador solo comprobaría que R es determinista.

**Tres cosas que conviene saber antes de lanzarlo:**

- **Se corre desde la carpeta del curso**, no desde `precalculo/`. Los guiones resuelven sus
  rutas contra la raíz del repositorio, así que desde dentro de `precalculo/` fallan con «no se
  puede abrir la conexión» sobre un archivo que sí existe. El envoltorio de PowerShell lo
  comprueba y lo dice; el de macOS todavía no.
- **Volver a lanzarlo no vuelve a descargar.** `descarga()` reutiliza el archivo si ya está en
  `datos/crudo/`, así que reintentar tras un corte de red retoma donde se quedó. Lo que sí se
  recalcula, y se reescribe, es todo `datos/procesado/`.
- **En Windows, la primera vez PowerShell se negará** a ejecutar el `.ps1`: es la directiva de
  ejecución, no un fallo del archivo. `Unblock-File .\precalculo\rscript.ps1` o invocarlo con
  `powershell -ExecutionPolicy Bypass -File ...`. El encabezado del guion lo explica.

Lo más pesado son `COL_ADM2.geojson` (201 MB, los 1 122 municipios) y `saber11_20224.csv`
(130 MB, los microdatos del ICFES). El resto son megas sueltos.

**Los datos del taller no hay que reconstruirlos**: `entrega/datos/` sí está versionado —es la
única excepción a la regla— porque una tarea que manda ejecutar código necesita que su dato sea
alcanzable desde fuera de la máquina que lo construyó. `datos_taller1.R` y `datos_taller2.R`
solo se corren si se cambia el taller.

---

## Qué hay en cada carpeta

| Carpeta | Qué contiene |
|---|---|
| `Htmls_Espacial/` | Los capítulos publicados, los talleres y los preparciales, más dos bancos de prueba del motor |
| `precalculo/` | Los guiones de R que calculan, los de Python que ensamblan y todos los auditores |
| `precalculo/salidas/` | El precálculo: los JSON y CSV que consume el navegador |
| `entrega/` | Lo que el estudiante se descarga de un taller: la plantilla LaTeX y sus datos |
| `plantilla/` | La plantilla base de la que salen todos los capítulos |
| `index.html` | La portada del sitio |

Los archivos `prueba-auditoria.html` y `prueba-geomapa.html` son bancos de prueba del
motor, no material del curso. `cuenta_sitio.py` los cuenta aparte por esa razón, y por la
razón contraria cuenta los `taller-*.html` en su propia tabla: son material, pero no son
capítulos —no tienen autoevaluación y sus módulos no van contra los 120 del plan—.

Los talleres se construyen con la misma cadena (`genera_taller1.R` → `ensambla_taller1.py`
→ `audita_taller1.py`) y corren por su propio bucle dentro de `audita_todo.sh`.

**Y hay un cuarto cubo, el de los `preparcial-*.html`.** Un preparcial no es un capítulo
—no enseña contenido nuevo— ni un taller —no se califica, no se individualiza y se puede
repetir—, así que sus totales tampoco van contra los 120 módulos del plan: mezclarlos
inflaría el avance del temario con material que no enseña temario. Se construye con la
cadena de siempre (`genera_preparcial1.R` → `ensambla_preparcial1.py` →
`audita_preparcial1.py`) y corre por su **tercer bucle** dentro de `audita_todo.sh`.

Ese bucle vigila dos cosas que no existen en ningún otro sitio del repositorio:

- **El alcance.** Qué módulos entran en el parcial y cuáles no, leído del HTML publicado de
  los capítulos y no de una lista escrita a mano. Si un capítulo publica un módulo más, el
  alcance cambia en silencio y `prueba_alcance_preparcial1.py` lo para.
- **La sincronía.** Un preparcial no recalcula: **cita** cifras que ya calcularon los
  capítulos, y guarda de cada una el archivo y la ruta de la que salió. El día que se
  regenere un capítulo y una de esas cifras se mueva, la pregunta queda mintiendo sin que
  nada más lo diga, porque el JSON del preparcial sigue siendo internamente coherente. Esa
  familia es la razón principal de que tenga auditor propio.

Los tres bucles descubren por convención: un preparcial del Corte II entra al arnés sin
tocar una línea de `audita_todo.sh`.

`entrega/datos/` es la única excepción a la regla de que `datos/` no se versiona, y existe
por un motivo que ningún auditor de cifras podía ver: **una tarea que manda ejecutar código
necesita que su dato sea alcanzable desde fuera de la máquina que lo construyó.** Tres tareas
del Taller 1 apuntaban a `datos/procesado/`, que da 404 en Pages. Son 10,9 MB —las 361
estaciones del IDEAM, los 60 municipios asignados y los 33 departamentos, sin simplificar,
porque simplificar la geometría cambiaría las cifras de las variantes ya repartidas—, los
produce `precalculo/datos_taller1.R` y el `.gitignore` los deja pasar de uno en uno.

---

## Licencia

Los datos conservan la licencia de su fuente, según la tabla de arriba.

El código y el material propio **todavía no tienen licencia declarada**. Sin un archivo
`LICENSE`, por defecto no se conceden derechos de uso a terceros aunque el repositorio
sea público.

---

Universidad El Bosque · Facultad de Ciencias · Estadística
