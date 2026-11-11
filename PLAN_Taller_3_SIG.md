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
  décima, y el máximo al 1–2 % (las rejillas de píxeles no están alineadas).
- **EPSG:3857 infla el área un 1,4 % en Bogotá**, no el 0,65 % de 1/cos²φ: Web Mercator aplica
  fórmulas de esfera a latitudes del elipsoide. El enunciado no adelanta la cifra.
- **El índice de vecino más próximo se mueve en los dos sentidos** al corregir el área (la caja de
  los puntos puede ser mayor o menor que la localidad). El enunciado no adelanta el sentido.
- Los nombres de las herramientas son los de `qgis_es.qm` de la 3.44.15, con sus erratas.

## §4 Órdenes de validación

```sh
# Docker (Linux)
docker run --rm --platform linux/amd64 -e QT_QPA_PLATFORM=offscreen -v "$CARPETA":/t \
  qgis/qgis:3.44.15 python3 /t/claves_qgis_taller3.py /t/datos /t/qgis/taller3_espacial /t/claves_linux.json
# macOS, con el Python de la aplicación
A=/Applications/QGIS-LTR.app/Contents
QT_QPA_PLATFORM=offscreen PYTHONHOME="$A/Frameworks" QGIS_PREFIX_PATH="$A/MacOS" \
PYTHONPATH="$A/Resources/python3.11/site-packages:$A/Resources/qgis/python:$A/Resources/qgis/python/plugins" \
  $A/MacOS/python3.12 precalculo/claves_qgis_taller3.py entrega/datos entrega/qgis/taller3_espacial claves_mac.json
```

`$CARPETA` lleva `datos/`, `qgis/taller3_espacial/` y el guion.

## §5 Pendiente y riesgos

- Windows: en comprobación en la VM de UTM (ver el informe de la sesión).
- Recorrido completo en la **interfaz** de QGIS, no solo por consola.
- `audita_taller3.py` independiente, auditor de prosa y arnés de inyección.
- Corte III: decir en la guía del proyecto que el Taller 3 es uno de los quices; tarjeta en la portada.
- Riesgo: calendario. Se publica el jueves 12 para dar cinco días; el informe del proyecto vence el domingo 15.
- No verificado: QGIS 4.x (el complemento está escrito para que cargue, pero no se probó).
