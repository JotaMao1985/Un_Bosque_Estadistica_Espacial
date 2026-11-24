# Obras por conseguir · Estadística Espacial (20929)

Estado al 2026-11-24 (63 obras en Zotero). Mientras una obra no tenga **ejemplar local** (PDF propio o de biblioteca, o
instantánea web registrada), la norma común solo la deja aparecer como lectura recomendada, sin
localizador, o como cita de segunda mano (`data-via`). El auditor lo hace cumplir (F14).

## Con ejemplar hoy

| Clave | Ejemplar | Nota |
|---|---|---|
| `baddeley2015spatial` | PDF de la biblioteca personal de Javier, 830 pp., desfase 19 | Se cita **2016** (año de copyright; decisión de Javier, 2026-11-12). La clave conserva el 2015 |
| `pebesma2023spatial` | Instantánea de r-spatial.org/book (17 capítulos) | Se cita por sección, nunca por página |
| `moraga2019geospatial` | Instantánea de 5 capítulos de paulamoraga.com/book-geospatial | Ídem |
| `snow1855mode` | Escaneo de la Wellcome Library (archive.org), dominio público | OCR con erratas; desfase variable por las láminas |
| `mas2018analisis` | PDF de acceso abierto de la editorial | Desfase 10 |
| `cressie1993statistics` | PDF entregado por Javier el 2026-11-23, ed. revisada de 1993, 908 pp. | Desfase variable: se cita por la página impresa; `tramos` en `ejemplares.yml` |
| `friendly2009histdata`, `baddeley2017spatstatdata`, `pebesma2005sp` | Ayuda local de R (HistData 1.0.0, spatstat.data 3.1.9, sp 2.2.0), 2026-11-23 | Instantáneas sin secciones: `sin_secciones` en el registro. Alta en Zotero por DOI de CRAN |
| `pebesma2016sf`, `dunnington2016s2` | Página de CRAN y README, 2026-11-23 | Ídem. La instantánea de CRAN es la versión de ese día (sf 1.1-3, s2 1.1.13), no la instalada |

## Prioridad para el capítulo 1

| Obra | Por qué | Vía sugerida |
|---|---|---|
| Tobler (1970), `tobler1970computer` | La primera ley, módulo 3; la caja de lecturas opina sobre su «contexto original» | JSTOR por la biblioteca |
| Clark y Evans (1954), `clark1954distance` | Índice R del módulo 6 | JSTOR por la biblioteca |
| Bivand, Pebesma y Gómez-Rubio (2013), `bivand2013applied` | Lecturas del cap. 1 | SpringerLink por la biblioteca |

| Roberts et al. (2017), `roberts2017crossvalidation` | Validación cruzada por bloques, m10 | Acceso cerrado (OpenAlex, 2026-11-23): biblioteca (Wiley) |
| Documentación de `venv` (Python) | Recuadro del entorno, m8 (PowerShell) | Ya está en Zotero (otro curso): falta añadirla a la colección 20929 (arrastre en Zotero) |

## Citadas de segunda mano o nombradas sin cita (R4, cap. 1)

El capítulo las nombra apoyándose en la obra leída, sin `data-via` propio, porque no tienen alta. Darlas de alta
permitiría citarlas con `data-via`:
Donnelly (1978) · Numata (1964) · Brody et al. (2000) · Cliff y Ord (1981) · Hall (1985) · Openshaw y Taylor (1979) ·
Openshaw (1984) · Yule y Kendall (1950) · Atkinson (1978) · Symons et al. (1983) · Ripley (1981) · Brus (2021) ·
Horvitz y Thompson (año por leer) · Hansen et al. (1983) · Rikken y Van Rijn (1993). Los años son los que dan las obras leídas.

## Resto del curso

| Obra | Capítulos | Vía sugerida |
|---|---|---|
| Anselin y Rey (2014) | syllabus (básica) | Compra (GeoDa Press); no hay versión de biblioteca conocida |
| Giraldo Henao (2011) | syllabus (básica) | **Sin alta**: no tiene ISBN ni DOI y el repositorio de la UNAL no devolvió el PDF. Javier: ¿tienes copia? Se transcribe de la portada |
| Waller y Gotway (2004), Peng y Dominici (2008) | syllabus | Biblioteca (Wiley, SpringerLink) |
| Rey, Arribas-Bel y Wolf (2023) | syllabus | Acceso abierto: geographicdata.science/book (instantánea cuando un capítulo la necesite) |
| Roberts et al. (2017) | syllabus; cap. 10 | Comprobar acceso abierto en *Ecography* |
| Artículos de los caps. 4, 5 y 7 (Getis y Ord, Anselin, Geary, Moran, Benjamini y Hochberg, van Lieshout y Baddeley…) | 4, 5, 7 | Biblioteca, uno por uno cuando llegue el plan de cada capítulo |
| Silverman (1986), Scott (2015), Wand y Jones (1995), Sheather y Jones (1991)… | apéndice A | Biblioteca |

## Sin alta en Zotero (no resuelve ningún identificador)

Se transcriben de la portada (`origen: portada`) cuando haya ejemplar, o de la ficha del editor:

- **Donnelly (1978)**: capítulo en Hodder (ed.), *Simulation Studies in Archaeology* (ISBN del libro 9780521220255).
- **Numata (1961)**: *Bulletin of Choshi Marine Laboratory*, en japonés, sin identificador.
- **Anselin (1996)**: capítulo de *Spatial Analytical Perspectives on GIS*; el DOI que existe es de la reimpresión de 2019.
- **Getis y Ord (1996)**: capítulo de Longley y Batty (eds.), pp. 261–277 según el manual de `spdep`; el curso cita su p. 267.
- **R Core Team**: el lenguaje R como obra de `4 Datos y software` (`citation()` no da DOI).

## Hallazgos de la búsqueda que tocan el contenido (para los planes de cada capítulo)

- **Cap. 1, lecturas:** Baddeley «caps. 3 y 5» para la ventana y la intensidad, pero en el índice
  general del ejemplar el cap. 5 es *Point Process Methods* y la intensidad es el cap. 6. Pebesma y
  Bivand «cap. 3» para la anatomía de `sf`, pero el cap. 3 es *Geometries* y `sf` es el cap. 7. Lo
  confirma el piloto.
- **Cap. 3:** Machado, Oliveira y Fernandes (2009) tiene una fe de erratas (10.1109/tvcg.2010.10):
  comprobar que las matrices de simulación de daltonismo usen los valores corregidos.
- **Apéndice A:** «Cox (1981)» es T. F. Cox, «Reflexive nearest neighbours» (*Biometrics*), no una
  obra de densidad.
- **Cap. 5:** «Diggle recoge en 2010» no corresponde a ninguna edición: las de Diggle son 1983, 2003 y
  2013; en 2010 solo hay un capítulo en el *Handbook of Spatial Statistics*.
- **Años en conflicto en la prosa:** Snow 1854 (brote) frente a 1855 (libro), que es correcto si se
  dice así; Scott 1979, 1985 y 2015 son tres obras distintas; Getis y Ord 1992, Ord y Getis 1995 y
  Getis y Ord 1996 también.

## Pie de referencias de la plantilla

El pie «Referencias Bibliográficas» de `plantilla/plantilla-capitulo.html` está escrito a mano y se
estampa en todos los documentos: todavía dice Baddeley et al. (2015), y no sale del catálogo.
Pasarlo a `<!--PIE-REFERENCIAS-->` generado (rol `basica`) toca los trece documentos: va con el
reensamblado general, no con el piloto.
