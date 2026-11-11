# Taller 3 · Los capítulos 1 a 5 en un SIG de escritorio (QGIS)

Estadística Espacial 2026-II (20929) · Corte III. Abierto el 2026-11-10.

## §0 Cómo retomar esto en otra sesión

1. Rama `claude/taller3-sig-qgis`. La página es `Htmls_Espacial/taller-3-sig-caps-1-5.html`; se
   edita `precalculo/ensambla_taller3.py` y se reensambla, nunca el HTML.
2. Un worktree nuevo no trae `datos/` ni `precalculo/cache/`: copiarlos de la copia principal.
3. Cadena, en este orden:
   - `precalculo/rscript.sh precalculo/datos_taller3.R` → `entrega/datos/taller3.gpkg` y
     `taller3_sedes_3857.geojson`.
   - `precalculo/rscript.sh precalculo/genera_taller3.R` → `precalculo/salidas/taller3_datos.json`
     (público) y `precalculo/cache/taller3_claves_r.json` (clave de T5, fuera de git).
   - `precalculo/claves_qgis_taller3.py` con el Python de QGIS → `precalculo/cache/taller3_claves_qgis_*.json`
     (las cifras de control de T1 a T4, fuera de git). Órdenes exactas en §4.
   - `python3 precalculo/ensambla_taller3.py`.
4. **Una vez repartido, `genera_taller3.R` no se vuelve a correr**: el buscador está vivo en Pages.
5. Las claves para calificar son los dos JSON de `precalculo/cache/`. Se indexan por localidad y,
   dentro, por el valor de la variante (`cuadrantes/NX`, `gf/r`, `kl/r`, `calor/radio`).

## §1 Decisiones de Javier (2026-11-10)

| Decisión | Valor |
|---|---|
| Herramienta | QGIS 3.44.15 LTR, nativo. ArcGIS descartado: solo Windows, sin licencia confirmada, y solo añadiría la K de Ripley |
| G, F, K/L y envolvente | Herramientas propias en Python dentro de QGIS (complemento `taller3_espacial`), sin dependencias |
| Lo que QGIS no hace | Selector de ancho de banda, corrección de borde del mapa de calor y `ppm`: en R, y se contrasta (T5) |
| Entorno | QGIS nativo; Docker Ubuntu (`qgis/qgis:3.44.15`) para validar sin ventana |
| Nota | Uno de los quices del Corte III |
| Formato | Guiado, con variante por documento, sin defensa |
| Entrega | Martes 17 de noviembre de 2026 |

Supuestos de la sesión, sin confirmar: hora límite 11:00; pesa como un quiz más.

## §2 Qué evalúa cada tarea

| Tarea | Peso | Capítulos | En QGIS | Lo que QGIS hace sin decirlo |
|---|---|---|---|---|
| T1 | 15 | 1–2 | Reproyectar, asignar proyección, área en dos SRC | `$area` y las distancias obedecen al elipsoide del proyecto |
| T2 | 20 | 3 | Contar en polígono, densidad, cuantiles y Jenks, rejillas de 2 y 4 km | La rejilla cubre la caja del perímetro, no la ciudad |
| T3 | 30 | 4 | Cuadrantes, vecino más próximo nativo, G/F, K/L con envolvente | El vecino más próximo usa la caja de los puntos como área, sin borde |
| T4 | 20 | 5 (m1–5) | Mapa de calor, estadísticas del ráster y de zona | Sin corrección de borde; «radio» no es σ (σ = radio/√8 en el cuártico) |
| T5 | 15 | 5 (m3, 4, 8, 9) | — (bloque de R dado) | Selector, borde y modelo: no existen en QGIS |

La variante fija: localidad (16 elegibles, n ≥ 35), NX ∈ {3, 4, 5}, radio de G y F ∈ {100, 150, 200} m,
radio de L ∈ {200, 300, 400} m, radio del mapa de calor ∈ {600, 800, 1000} m.

## §3 Lo medido al construirlo

- **El núcleo coincide con `spatstat`**: G y F por muestra reducida idénticas a `ppp_G_borde` y
  `ppp_F_borde` (10⁻¹⁵); K con `correction = "border"` a 10⁻¹⁰ relativo; χ² de cuadrantes a 10⁻⁷
  (el recorte de celdas lo hace GEOS y no `spatstat`). Kennedy, Teusaquillo y Santa Fe.
- **Las cifras de control son las mismas en dos plataformas**: QGIS 3.44.15 en Docker (Linux amd64,
  numpy 2.3.5) y nativo en macOS arm64 (numpy 2.5.2): 1 443 cifras, diferencia relativa máxima
  3,7·10⁻¹⁰. La banda de 99 simulaciones incluida: `default_rng` es reproducible entre plataformas.
- **El mapa de calor «Escalado» integra n** (masa total = n exacto), y **radio R ≡ σ = R/√8** con
  núcleo cuártico: la masa dentro de la localidad coincide con `density(..., edge = FALSE)` a la
  décima (hasta 0,54 %), y el máximo hasta el 4,2 % (Usaquén, 600 m). La causa la midió el auditor
  independiente: QGIS desplaza cada punto hasta ±25 m en y al pasarlo a la rejilla (cuenta la fila
  desde arriba y la fracción de píxel desde abajo), y su pico queda hasta 2,5 % sobre el exacto;
  `density()` también reparte los puntos en píxeles. El enunciado no da ninguna de estas cifras.
- **El «Jenks» de QGIS 3.44.15 no es el Fisher–Jenks óptimo** sobre estas 20 densidades: su tercer
  corte es 5,44103 y el óptimo, 6,11232 (`mapclassify.NaturalBreaks` reproduce a QGIS, `FisherJenks`
  da el óptimo). La clave es lo que muestra QGIS, que es lo que ve el estudiante: 5 localidades
  cambian de clase; con el óptimo serían 6. Cuatro de las cinco están justo en un corte.
- **EPSG:3857 infla el área un 1,4 % en Bogotá**, no el 0,65 % de 1/cos²φ: Web Mercator aplica
  fórmulas de esfera a latitudes del elipsoide. El enunciado no adelanta la cifra.
- **El índice de vecino más próximo se mueve en los dos sentidos** al corregir el área (la caja de
  los puntos puede ser mayor o menor que la localidad). El enunciado no adelanta el sentido.
- Los nombres de las herramientas son los de `qgis_es.qm` de la 3.44.15, con sus erratas.

## §3b Los auditores

- `audita_taller3.py` (geo_env): 1 980 comprobaciones; rehace T1 a T4 sin `nucleo.py` ni QGIS y las
  contrasta con las claves de `precalculo/cache/`. Sin claves (clon limpio) audita solo lo público y
  lo dice: 128 comprobaciones y 12 bloques SALTADOS.
- `prueba_auditor_taller3.py`: 144 de 144 defectos inyectados cazados.
- `audita_texto_taller3.py`: 130 comprobaciones (fechas contra el `.tex` y el PDF, enlaces, tope de
  520 KB, identificadores y parámetros del enunciado contra los que corrió el guion de las claves,
  el ZIP con los mismos bytes que la carpeta, la huella de datos, ninguna cifra de control en la página).

## §4 Órdenes de validación

```sh
# Docker (Linux)
docker run --rm --platform linux/amd64 -e QT_QPA_PLATFORM=offscreen -v "$CARPETA":/t \
  qgis/qgis:3.44.15 python3 /t/claves_qgis_taller3.py /t/datos /t/qgis/taller3_espacial /t/claves_linux.json
# macOS, con el Python de la aplicación
A=/Applications/QGIS-LTR.app/Contents
QT_QPA_PLATFORM=offscreen PYTHONHOME="$A/Frameworks" QGIS_PREFIX_PATH="$A/MacOS" \
PROJ_DATA="$A/Resources/qgis/proj" GDAL_DATA="$A/Resources/qgis/gdal" \
PYTHONPATH="$A/Resources/python3.11/site-packages:$A/Resources/qgis/python:$A/Resources/qgis/python/plugins" \
  $A/MacOS/python3.12 precalculo/claves_qgis_taller3.py entrega/datos entrega/qgis/taller3_espacial claves_mac.json
```

`$CARPETA` lleva `datos/`, `qgis/taller3_espacial/` y el guion.

## §5 Pendiente y riesgos

- Windows: en comprobación en la VM de UTM (ver el informe de la sesión).
- Riesgo: calendario. Se publica el jueves 12 para dar cinco días; el informe del proyecto vence el domingo 15.
- **Sin auditoría independiente**, y dicho en `audita_taller3.py`: `bw.diggle`, `bw.ppl` y los
  coeficientes de `ppm` (reimplementarlos sería copiar `spatstat`) y los cortes de Jenks de QGIS.
- **Sin recorrido con clics** en la interfaz de QGIS: no se concedió el control de la aplicación. Los
  nombres de menús, herramientas y opciones salen de `qgis_es.qm`; una variante entera la resolvió a
  ciegas un lector que solo tenía la página, con `qgis_process`, y sus 34 cifras coincidieron.
- No verificado: QGIS 4.x (el complemento está escrito para que cargue, pero no se probó).
