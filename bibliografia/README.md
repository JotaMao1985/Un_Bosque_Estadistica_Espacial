# Bibliografía del curso · ninguna cita de memoria

El material tiene una norma para las cifras —ninguna se escribe a mano, todas salen de R— y
desde el 2026-11-12 tiene la misma para las fuentes: **ninguna cita se escribe de memoria**.
Toda afirmación que el capítulo atribuye a una obra apunta a un pasaje que alguien leyó en un
ejemplar local, y un guion lo comprueba.

Sigue la norma común de los cursos de El Bosque, `Bosque 2026/Vault/Estandar/Capa de fuentes.md`
(v1.1). La implementación se portó de Series de Tiempo (20948); lo que cambia aquí está marcado
con **(20929)**.

## Dónde vive cada dato

| Dato | Vive en | Lo escribe |
|---|---|---|
| Metadatos de la obra y su PDF | Zotero, `Docencia › 20929 Estadística Espacial` | los traductores de Zotero, desde un DOI o un ISBN |
| Instantánea de la biblioteca | `referencias.json` (CSL-JSON), `claves.json`, `zotero.lock.json` | `precalculo/exporta_zotero.py` |
| Lo que Zotero no trajo | `enmiendas.yml`, cada una con su evidencia | a mano, con URL y fecha |
| Lo que el pie lleva y Zotero no dice **(20929)** | `pie.json`: orden, obras adicionales, anotaciones, líneas sin alta, documentos congelados, vetos | a mano, cada entrada con su `motivo` |
| Cómo se encontró cada identificador | `obras.tsv` | la búsqueda en Crossref, Open Library o la editorial |
| Obras que faltan y cómo conseguirlas | `por_conseguir.md` | quien dirige la fase |
| Ejemplar leído (huella, portada) | `ejemplares.yml` | `precalculo/extrae_fuente.py` + una mirada a la portada |
| Páginas web leídas (URL, fecha, huella) | `instantaneas.yml` | `precalculo/extrae_fuente.py --web` |
| Afirmación ↔ pasaje leído | `contraste/capN.yml` | quien dirige la ronda, con lo que devuelve el verificador |
| Línea base de menciones en la prosa | `linea_base.json` | `precalculo/linea_base_citas.py` |
| Contrato curso → vault | `uso_fuentes.json`: lo único que el vault lee de este curso | `precalculo/audita_citas.py --uso` |
| PDF y texto por página **(20929)** | `~/Documents/Trabajo 2026/Fuentes/20929/` — **fuera del repo y de los worktrees** | `precalculo/extrae_fuente.py` |
| Estilo de cita | `apa-es.csl` (APA 7 en español, el mismo de Series) | copiado de Series |

Zotero es la puerta de entrada. El repo guarda lo que el auditor necesita para no depender de
que Zotero esté abierto. El vault de Obsidian (`Bosque 2026/Vault/Fuentes/`) es navegación y
notas de lectura, nunca dato primario. Las rutas están en `precalculo/fuentes_config.py`.

**(20929)** El corpus no vive en `bibliografia/_local/` como en Series sino en
`Trabajo 2026/Fuentes/20929/`: así lo ve cualquier worktree sin copiarlo (un worktree nuevo no
trae lo ignorado).

## Dar de alta una obra

1. Buscar su DOI o ISBN **en la red** (Crossref, la editorial, Open Library), no de memoria, y
   anotarlo en `obras.tsv` con la URL que lo demuestra.
2. Antes de la primera escritura del día: respaldo de `~/Zotero/zotero.sqlite` y conteo de todas
   las colecciones por la API local. Un solo escritor a la vez: otras sesiones (Muestreo, Series,
   Diseño, TdR) también usan Zotero.
3. En Zotero, seleccionar la subcolección (`1 Básica`, `2 Complementaria`, `3 Fuentes primarias`,
   `4 Datos y software`) y usar **Añadir por identificador**. Los ISBN se envían aparte de los DOI.
4. `python3 precalculo/exporta_zotero.py` (Zotero abierto, con la API local activada).
5. Si falta un campo que la editorial sí publica, añadirlo a `enmiendas.yml` con su evidencia.
6. Si hay ejemplar: adjuntarlo en Zotero o dejarlo en `Fuentes/20929/pdf/<clave>.pdf`; correr
   `python3 precalculo/extrae_fuente.py` y llenar en `ejemplares.yml` lo que diga la portada
   (`edicion_comprobada`, `desfase`, `procedencia`).

Una obra sin DOI ni ISBN se da de alta a mano copiando la portada y se anota `origen: portada`.

## Una obra sin ejemplar local

Solo puede aparecer de dos maneras:

- como **lectura recomendada**, sin localizador (`<cite class="cita" data-ref="clave"></cite>` sin
  `data-loc`, o en una lista de lecturas);
- como **cita de segunda mano**: `data-via="clave_leida"`, y el localizador es el de la obra que
  sí se leyó («citado en…»).

Nunca con página, sección o tabla propias. El auditor lo comprueba.

## Contrastar una afirmación

1. Quien redacta marca la afirmación en la prosa de `precalculo/ensambla_capN.py` con
   `data-afirma="c1-m3-01"` (capítulo, módulo, número) y, si va a llevar cita visible, deja dentro
   `<cite class="cita" data-ref="clave" data-loc="§3.6"></cite>`. **(20929)** El ensamblador
   llama a `genera_referencias.genera()` antes de escribir el HTML: el texto de la cita y las
   listas no se teclean nunca.
2. Un verificador **que no es quien redactó** recibe la afirmación y el texto de la fuente —no el
   veredicto esperado— y devuelve el veredicto y una cita literal de 25 palabras como mucho.
3. La entrada se escribe en `contraste/capN.yml`. La huella de la prosa sale de
   `python3 precalculo/audita_citas.py --huella c1-m3-01`.
4. Se reensambla el capítulo y `python3 precalculo/audita_citas.py` tiene que salir en verde.

Localizadores (vocabulario cerrado de la norma): `§3.4` · `cap. 3` · `p. 15` · `pp. 15–17` ·
`tabla 3.1` · `fig. 3.1` · `ec. 3.3` · `ejemplo 3.2` · `ejercicio 3.12` · `problema 2.28` ·
`ap. A`; varios se separan con «; ». La edición nunca va en el localizador: va en la clave.

Veredictos: `respaldada` · `con-matiz` (la `nota` dice en qué difiere) · `discrepa` (solo lo
cierra Javier) · `propia` (se deduce en el material o sale de R) · `pendiente` (con `motivo`) ·
`por-reverificar` (la prosa cambió). Solo las dos primeras admiten cita visible.

**Exigen fuente:** hechos del mundo que el precálculo no calcula, resultados u opiniones
atribuidos, umbrales y reglas prácticas, datos o ejercicios tomados de una obra, resultados con
nombre que el capítulo no demuestra. **No la exigen:** lo demostrado en el propio texto, las
cifras del precálculo, los escenarios inventados (declarados como tales). Un epónimo (índice de
Moran, función K de Ripley) no es una cita.

## El pie «Referencias Bibliográficas» **(20929)**

Lo llevan todos los documentos, porque viene de `plantilla/plantilla-capitulo.html`. Desde el
2026-11-23 no se teclea: `genera_referencias.py` lo escribe **en la plantilla**, entre
`<!--PIE-REFERENCIAS:inicio-->` y `<!--PIE-REFERENCIAS:fin-->`, y cada documento lo hereda al
reensamblarse.

- **Qué obras:** las de rol `basica` de Zotero (subcolección `1 Básica`), más las `adicionales`
  de `pie.json`. El texto de cada una es el de `referencias.json`, en APA 7.
- **Lo que APA no trae** («Texto guía del curso», la versión de lectura libre, la licencia) va en
  `anotaciones`. Un enlace tiene que ser el de una instantánea de `instantaneas.yml`, y una
  licencia lleva su `evidencia`: el literal que el auditor busca en esa instantánea.
- **Una obra sin alta en Zotero** va en `sin_alta` como línea fija, con el `motivo` y lo que
  falta `para_el_alta`. El día que su clave aparece en `referencias.json`, el generador para
  hasta que se borre la línea fija.
- **Los documentos repartidos** que no se reensamblan (los tres talleres) están en `congelados`
  y conservan el pie con que se repartieron.

Al cambiar una básica en Zotero, una enmienda o `pie.json`:

1. `python3 precalculo/exporta_zotero.py` (si el cambio fue en Zotero);
2. `python3 precalculo/genera_referencias.py plantilla/plantilla-capitulo.html`;
3. reensamblar todos los documentos que salen de la plantilla, menos los congelados, y
   `python3 precalculo/sincroniza_prueba_geomapa.py` para el banco del `.geomapa`;
4. `python3 precalculo/audita_citas.py`: F15 compara la plantilla y cada documento publicado con
   lo que el guion escribiría, y no deja pasar lo vetado («Baddeley … (2015)»).

## Los guiones

| Guion | Qué hace |
|---|---|
| `precalculo/fuentes_config.py` | las rutas, una sola vez |
| `precalculo/exporta_zotero.py` | Zotero → `referencias.json`. `--comprobar` no escribe |
| `precalculo/extrae_fuente.py` | PDF y páginas web → texto en el corpus, y su huella |
| `precalculo/genera_referencias.py` | escribe las citas y las listas de fuentes (lo llama el ensamblador) y el pie (sobre la plantilla) |
| `precalculo/audita_citas.py` | la cita literal está en la fuente, la edición es la leída, quien verifica no redactó, la prosa no cambió, ninguna obra sin ejemplar lleva localizador, el pie de todo documento es el generado (F15)… |
| `precalculo/prueba_audita_citas.py` | inyecta defectos y exige que cada uno salte con su código |
| `precalculo/linea_base_citas.py` | clasifica las menciones de autor y año que ya están en la prosa |
