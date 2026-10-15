#!/usr/bin/env python3
"""
construye_nucleo3d.py — estampa la página independiente de la animación 3D

Material de Estadística Espacial 2026-II (20929). Capítulo 5, módulos 1 y 4.

EL MOTOR VIVE EN `precalculo/nucleo3d/nucleo3d.js` y ESTE ARCHIVO NO LO
DUPLICA: lo lee y lo estampa en una página autocontenida,

    Htmls_Espacial/animaciones/nucleo-3d.html

que es lo que cargan las diapositivas (en un `<iframe>`, con `?modo=clase`) y
a lo que se puede apuntar directamente. El capítulo 5 no usa esa página:
inyecta el mismo motor en línea (`ensambla_cap5.py`), porque un capítulo es un
solo HTML. Las dos salidas son artefactos y no se editan a mano.

  · three.js llega de un CDN, FIJADO por versión y con su huella SRI. Los otros
    capítulos ya cargan Tailwind, KaTeX, Chart.js y Prism de CDN; esto no
    añade una clase de dependencia nueva, pero sí una versión que alguien tiene
    que acordarse de no subir en silencio: la r149 es la última con `three.min.js`
    sin el aviso de obsolescencia (la r150 lo estrena y la r160 lo quita).
  · `?modo=clase` quita el encabezado, agranda la letra y hace que las flechas
    se reenvíen al visor de diapositivas. Sin parámetro es una página normal.
  · `?escena=borde` monta la escena del módulo 4 (la corrección de borde) en vez de la
    del módulo 1 (del conteo a la superficie): el mismo motor, otra animación.

    python3 precalculo/construye_nucleo3d.py            # escribe la página
    python3 precalculo/construye_nucleo3d.py --comprueba  # sale con 1 si está desactualizada
"""
from __future__ import annotations

import pathlib
import sys

RAIZ = pathlib.Path(__file__).resolve().parent.parent
from pon_boton_indice import aplica as aplica_boton
MOTOR = RAIZ / "precalculo" / "nucleo3d" / "nucleo3d.js"
DESTINO = RAIZ / "Htmls_Espacial" / "animaciones" / "nucleo-3d.html"
# El capítulo 5 lleva el motor EN LÍNEA (`ensambla_cap5.py`): si se edita el motor y no se reensambla, el capítulo publica
# una versión vieja y ningún auditor de cifras lo ve. `--comprueba` lo mira.
CAPITULO = RAIZ / "Htmls_Espacial" / "capitulo-5-intensidad-nucleos.html"

# La huella se calculó sobre el archivo descargado de esa misma URL:
#   curl -s URL | openssl dgst -sha384 -binary | openssl base64 -A
THREE_URL = "https://cdn.jsdelivr.net/npm/three@0.149.0/build/three.min.js"
THREE_SRI = "sha384-RRHfJ6w1mTlKUBMYT/hvnRiOzEB/vyRV3DrQOseb6oYfvaZSfdd0byS4bHps0k2R"

TITULO = "Del conteo a la superficie · estimación por núcleos"
TITULO_BORDE = "Lo que se escapa por el borde · estimación por núcleos"


def leer_motor() -> str:
    """El motor tal cual, para estamparlo en línea. Un `</script>` dentro lo
    cerraría a media función: se avisa en vez de escaparlo en silencio."""
    js = MOTOR.read_text(encoding="utf-8")
    if "</script" in js.lower():
        sys.exit("PARADO: el motor contiene «</script» y cerraría su propia etiqueta")
    return js


PAGINA = """<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>@@TITULO@@</title>
  <!-- ARTEFACTO: lo estampa precalculo/construye_nucleo3d.py desde precalculo/nucleo3d/nucleo3d.js. No se edita a mano. -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700&family=Fira+Code:wght@400;500;600&display=swap" rel="stylesheet">
  <style>
    html, body { margin: 0; min-height: 100%; background: #f8fafc; }
    body { font-family: 'Montserrat', 'Helvetica Neue', Helvetica, Arial, sans-serif; color: #1e293b; }
    .pagina { max-width: 1180px; margin: 0 auto; padding: 1.25rem 1.25rem 2rem; }
    .pagina h1 { margin: 0 0 .25rem; font-size: 1.35rem; color: #012820; }
    .pagina .sub { margin: 0 0 1rem; color: #475569; font-size: .9rem; }
    /* en una diapositiva: sin marco, fondo transparente, aprovecha todo el iframe */
    body.clase { background: transparent; overflow: hidden; }
    body.clase .pagina { max-width: none; padding: .35rem .6rem; }
    body.clase .pagina > header { display: none; }
  </style>
</head>
<body>
  <div class="pagina">
    <header>
      <h1 id="titulo">Del conteo a la superficie</h1>
      <p class="sub" id="subtitulo">Cómo el estimador por núcleos convierte un conjunto de puntos en una superficie de intensidad. Capítulo 5 · Estadística Espacial.</p>
    </header>
    <div id="animacion"></div>
    <noscript>Esta animación necesita JavaScript. El capítulo 5 dice lo mismo con palabras: en el módulo 1, cada punto levanta una loma de ancho σ y la superficie de intensidad es la suma de todas las lomas; en el módulo 4, la parte del núcleo que cae fuera de la ventana no la recoge nadie, y las dos correcciones de borde se distinguen por dónde dividen.</noscript>
  </div>
  <script src="@@THREE_URL@@" integrity="@@THREE_SRI@@" crossorigin="anonymous"></script>
  <script>
@@MOTOR@@
  </script>
  <script>
    (function () {
      var q = new URLSearchParams(location.search);
      var clase = q.get('modo') === 'clase';
      var escena = q.get('escena') === 'borde' ? 'borde' : 'conteo';
      if (clase) document.body.classList.add('clase');
      if (escena === 'borde') {
        document.title = '@@TITULO_BORDE@@';
        document.getElementById('titulo').textContent = 'Lo que se escapa por el borde';
        document.getElementById('subtitulo').textContent = 'Qué le hace el borde de la ventana a una estimación por núcleos y qué hacen las dos correcciones de spatstat. Capítulo 5 · Estadística Espacial.';
      }
      window.animacion = Nucleo3D.montar(document.getElementById('animacion'), { modo: clase ? 'clase' : 'pagina', escena: escena });
    })();
  </script>
</body>
</html>
"""


def construye() -> str:
    return (PAGINA.replace("@@TITULO@@", TITULO)
            .replace("@@TITULO_BORDE@@", TITULO_BORDE)
            .replace("@@THREE_URL@@", THREE_URL)
            .replace("@@THREE_SRI@@", THREE_SRI)
            .replace("@@MOTOR@@", leer_motor()))


def main() -> int:
    html = construye()
    html = aplica_boton(html, DESTINO, RAIZ, "franja")
    if "--comprueba" in sys.argv:
        al_dia = DESTINO.exists() and DESTINO.read_text(encoding="utf-8") == html
        print(f"{DESTINO.relative_to(RAIZ)}: {'al día' if al_dia else 'DESACTUALIZADO'}")
        cap_al_dia = CAPITULO.exists() and leer_motor() in CAPITULO.read_text(encoding="utf-8")
        print(f"{CAPITULO.relative_to(RAIZ)}: {'lleva el motor actual' if cap_al_dia else 'LLEVA UN MOTOR VIEJO (hay que correr ensambla_cap5.py)'}")
        return 0 if al_dia and cap_al_dia else 1
    DESTINO.parent.mkdir(parents=True, exist_ok=True)
    DESTINO.write_text(html, encoding="utf-8")
    print(f"{DESTINO.relative_to(RAIZ)}  {len(html) / 1024:.0f} KB")
    return 0


if __name__ == "__main__":
    sys.exit(main())
