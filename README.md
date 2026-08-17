# Estadística Espacial · Universidad El Bosque

Material de estudio interactivo del curso **Estadística Espacial (20929)**, programa de
Matemáticas y Ciencia de Datos, 2026-II.

**→ [Ver el material publicado](https://jotamao1985.github.io/Un_Bosque_Estadistica_Espacial/)**

Cada capítulo es una página HTML autocontenida —sin servidor, sin dependencias que instalar—
con mapas, simuladores, autoevaluación y el mismo análisis resuelto en R y en Python.

---

## Estado

Tres de los diez capítulos del plan están publicados.

| # | Capítulo | Semana | Estado |
|---|---|---|---|
| 1 | Datos espaciales y la primera ley de la geografía | 1 | Publicado |
| 2 | SIG, sistemas de referencia y georreferenciación con `sf` | 2–3 | Publicado |
| 3 | Cartografía estadística y el MAUP | 4–5 | Publicado |
| 4 | Patrones puntuales: CSR y funciones de resumen | 6–7 | En preparación |
| 5 | Intensidad por núcleos y procesos puntuales | 8–9 | En preparación |
| 6 | Datos de área y la matriz de pesos espaciales | 10–11 | En preparación |
| 7 | Autocorrelación espacial global y local | 12–13 | En preparación |
| 8 | Econometría espacial: SAR, SEM, SDM y GWR | 14 | En preparación |
| 9 | Geoestadística: variograma y kriging | 15 | En preparación |
| 10 | ML espacial, datos espacio-temporales y proyecto | 16 | En preparación |

Lo publicado suma 36 módulos, 30 simuladores, 29 mapas, 36 preguntas de autoevaluación,
13 ejercicios guiados y 30 bloques de código en cada lenguaje.

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

Para verificarlo todo:

```bash
precalculo/audita_todo.sh
```

Son siete pasos: el precálculo recalculado en Python, un arnés que le inyecta defectos a
ese auditor para probar que sabe fallar, otro que hace lo mismo con las guardas del
ensamblador, la ejecución real de los bloques de código, las cifras de la prosa, un arnés
para el auditor de prosa y el recuento del sitio. Tarda unos 40 minutos y termina en
`ARNÉS COMPLETO EN VERDE` o no termina.

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

**Los 431 MB de `datos/` no se versionan.** Se reconstruyen con los `datos_*.R`, en el
orden que documenta `FUENTES.md`.

---

## Qué hay en cada carpeta

| Carpeta | Qué contiene |
|---|---|
| `Htmls_Espacial/` | Los capítulos publicados y los talleres, más dos bancos de prueba del motor |
| `precalculo/` | Los guiones de R que calculan, los de Python que ensamblan y todos los auditores |
| `precalculo/salidas/` | El precálculo: los JSON y CSV que consume el navegador |
| `plantilla/` | La plantilla base de la que salen todos los capítulos |
| `index.html` | La portada del sitio |

Los archivos `prueba-auditoria.html` y `prueba-geomapa.html` son bancos de prueba del
motor, no material del curso. `cuenta_sitio.py` los cuenta aparte por esa razón, y por la
razón contraria cuenta los `taller-*.html` en su propia tabla: son material, pero no son
capítulos —no tienen autoevaluación y sus módulos no van contra los 120 del plan—.

Los talleres se construyen con la misma cadena (`genera_taller1.R` → `ensambla_taller1.py`
→ `audita_taller1.py`) y corren por su propio bucle dentro de `audita_todo.sh`.

---

## Licencia

Los datos conservan la licencia de su fuente, según la tabla de arriba.

El código y el material propio **todavía no tienen licencia declarada**. Sin un archivo
`LICENSE`, por defecto no se conceden derechos de uso a terceros aunque el repositorio
sea público.

---

Universidad El Bosque · Facultad de Ciencias · Matemáticas y Ciencia de Datos
