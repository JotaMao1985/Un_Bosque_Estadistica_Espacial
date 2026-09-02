#!/usr/bin/env python3
"""
audita_texto_cap2.py — auditor de prosa del capítulo 2

Material de Estadística Espacial 2026-II (20929). T2.2c.

Copiado de `audita_texto_cap1.py`, que es el molde. Fíjate en lo corto que
es: toda la maquinaria vive en `audita_texto_base.py` y aquí solo se
declara **qué** comprobar, no **cómo**. En Diseño de Experimentos cada
auditor eran entre 370 y 677 líneas con el contenido cableado, y por eso un
fallo del núcleo —retirar las fórmulas de KaTeX antes de extraer los
números— sobrevivió en cinco auditores a la vez informando «limpio».

Qué comprueba, por encima:

  · que **toda cifra de la prosa** —incluidas las de dentro de las
    fórmulas— esté en `cap2_datos.json` o en `cap2_soluciones.json`;
  · que el capítulo cubra los temas que el §6 del plan le asigna;
  · que cite sus fuentes y sostenga las afirmaciones que tiene que hacer;
  · accesibilidad del marcado, los `.geomapa` y su presupuesto;
  · que la codificación no se haya roto (las tildes son el canario);
  · que los enlaces relativos existan.

Uso:  python3 precalculo/audita_texto_cap2.py
Devuelve 1 si algo falla.
"""
from __future__ import annotations

import sys

from audita_texto_base import Auditor

# Cifras que NO son resultados: identificadores, años, códigos, versiones y
# referencias bibliográficas. Se declaran para que el auditor no denuncie
# el «4326» de un CRS como una cifra sin respaldo.
ESTRUCTURALES = {
    "20929",                                  # el código de la asignatura
    "2026", "2025", "2024", "2020", "2018", "2011", "1998", "1987", "1975",
    "1859", "1980",                           # Tissot, el datum viejo, el shapefile
    # Los códigos EPSG que el capítulo nombra. Son identificadores, no
    # medidas: exigirles respaldo numérico sería absurdo.
    "4326", "3857", "3116", "9377", "4686", "4218", "8857", "32119", "32618",
    "9", "10", "12", "1", "2", "3", "4", "5", "6", "7", "8", "11",
    "0.9992", "0.99840064",                   # el factor de escala de 9377 y su cuadrado
    "1.2", "4.4", "0.05", "0.01", "95", "90", "99", "100",
    "1.0.22", "3.5.1", "1.4.2", "2.1.5", "4.2", "0.4.11", "0.2.5",
    "3.8.5", "3.13.0", "9.5.1", "4.4.1",      # GDAL, GEOS, PROJ y R
    "4.0",                                    # CC BY 4.0
    "19125",                                  # la norma ISO de Simple Features
    "20", "24",                               # pp. 20-24 de Snyder
    "73", "74",                               # los meridianos centrales, en grados enteros
    "50", "150", "500", "200", "1000",        # los sigma y radios nominales del enunciado
    "25", "1854",
    # Los años de la bibliografía que la plantilla trae de serie. No son
    # resultados de nada: son referencias, y exigirles respaldo numérico
    # denunciaría un capítulo correcto.
    "2013", "2015", "2019", "2023", "2022", "2021", "2016", "2010",
}

# El temario que el §6 del plan le asigna al capítulo 2. Los tokens son
# largos a propósito: buscar «crs» daría OK dentro de cualquier cosa.
DEBE_CUBRIR = [
    # El temario del syllabus abre con la sigla, y el capítulo la daba por
    # sabida: hasta el 2026-08-14 «SIG» solo aparecía en el título. Estas
    # cuatro entradas existen para que no se pueda volver a caer.
    ("qué es un SIG", "sistema de información geográfica"),
    ("el estándar Simple Features", "simple features"),
    ("el modelo vectorial frente al ráster", "ráster"),
    ("por qué el SIG del curso se escribe y no se pulsa", "qgis"),
    ("el geoide y el elipsoide", "elipsoide"),
    ("el datum y su desplazamiento", "datum"),
    ("MAGNA-SIRGAS", "magna-sirgas"),
    ("cuánto mide un grado de longitud", "grado de longitud"),
    ("que los grados no son metros", "no son metros"),
    ("las tres familias de proyección", "equidistante"),
    ("la indicatriz de Tissot", "indicatriz"),
    ("la deformación angular", "deformación angular"),
    ("la escala de área", "escala de área"),
    ("Web Mercator y sus pecados", "web mercator"),
    ("el factor de escala de una transversa de Mercator", "factor de escala"),
    ("st_transform frente a st_set_crs", "st_set_crs"),
    ("el archipiélago de San Andrés", "san andrés"),
    ("s2 frente al elipsoide", "s2"),
    ("las limitaciones del shapefile", "shapefile"),
    ("el GeoPackage", "geopackage"),
    ("la trampa del orden lon/lat", "invert"),
    ("la coma decimal", "coma decimal"),
    ("el error posicional", "error posicional"),
    ("el sesgo de la geocodificación", "geocodific"),
    ("la validación topológica", "st_is_valid"),
    ("los predicados DE-9IM", "de-9im"),
    ("el buffer y el CRS", "buffer"),
    ("los índices espaciales", "índice espacial"),
    ("la unión espacial", "st_join"),
    ("el geohash", "geohash"),
]

# Tokens largos: «men» daría OK dentro de «momento».
FUENTES = [
    "tissot", "snyder", "igac", "ideam", "ogc",
    "secretaría de educación del distrito", "ministerio de educación nacional",
    "epsg", "proj", "gdal",
]

# Las afirmaciones que este capítulo TIENE que hacer. Si una desaparece en
# una reescritura, el capítulo deja de decir lo que el plan le encarga y
# nadie se entera: el HTML seguiría siendo válido y la consola limpia.
AFIRMACIONES = [
    ("declara que la posición es un atributo de primera clase",
     "atributo de primera"),
    ("dice que una capa sin CRS declarado no es una capa",
     "no es una capa"),
    ("dice que un CRS mal puesto no da error",
     "no da error"),
    ("advierte de que el achatamiento cambia el tamaño de las cosas",
     "achatamiento"),
    ("dice que la constancia del grado de latitud sobre la esfera es el artefacto",
     "es el artefacto"),
    ("declara que ninguna proyección es conforme y equivalente a la vez",
     "conforme y equivalente"),
    ("explica que es un teorema y no una limitación tecnológica",
     "no es una casualidad"),
    ("dice que la razón de área mínima de una TM es k al cuadrado",
     "exactamente"),
    ("declara que el archipiélago da la vuelta a la recomendación",
     "da la vuelta"),
    ("dice que la pregunta del CRS no tiene respuesta sin decir para qué",
     "no tiene respuesta sin decir"),
    ("distingue reetiquetar de reproyectar",
     "conserva los números y cambia el sitio"),
    ("advierte de que no toda etiqueta equivocada hace daño",
     "no toda etiqueta equivocada"),
    ("declara sobre qué superficie mide cada camino",
     "sobre qué superficie"),
    ("dice que el shapefile desfigura los nombres, no los trunca",
     "no los trunca"),
    ("declara que ninguna estación invertida cae en Colombia",
     "ninguna cae en colombia"),
    ("dice que el sesgo posicional es geométrico y no socioeconómico",
     "no hay patrón monótono"),
    ("nombra el modo de fallo dominante del curso",
     "valor plausible en vez de fallar"),
    ("dice que la proximidad en geohash no es la del espacio",
     "no es la proximidad en el"),
    ("remite el MAUP al capítulo 3",
     "es el maup otra vez"),
]

# Si la codificación se rompe, las tildes no desaparecen: se convierten en
# otra cosa. Se exigen cadenas CONCRETAS que este capítulo usa de verdad.
CADENAS = [
    # Solo caracteres que el capítulo usa DE VERDAD. La primera versión de
    # esta lista pedía «φ», «π» y «ü», que el capítulo escribe en KaTeX
    # (\varphi, \pi) o no escribe: daban MAL sobre un capítulo intacto.
    # Es exactamente el aviso que dejó escrito el auditor del capítulo 1 —
    # una comprobación que falla siempre acaba enseñando a ignorar el
    # informe— y aun así volví a caer en él.
    "ω", "−", "×", "²", "°", "«", "»", "—", "–", "§",
    "ó", "í", "é", "ñ", "¿",
    "elipsoide", "proyección", "geodésica", "Bogotá", "San Andrés",
    "topológica", "índice", "área",
]

# Mismo criterio: solo órdenes que el capítulo escribe. `\text` no lo usa.
ORDENES = [r"\dfrac", r"\varphi", r"\sin", r"\arcsin", r"\omega"]


def main() -> int:
    a = Auditor(
        capitulo="capitulo-2-crs-georreferenciacion.html",
        var_entorno="CAP2_HTML",
        jsons=["cap2_datos.json", "cap2_soluciones.json"],
        estructurales=ESTRUCTURALES,
        presupuesto_geomapa_kb=120.0,
        # Los cortes de clase que el HTML incrusta salen de AQUÍ, no del
        # JSON de cifras. Va por su propio parámetro para que sus decenas de
        # miles de coordenadas no entren en el índice de la prosa.
        json_mapas="cap2_mapas.json",
    )
    print(f"\n=== audita_texto_cap2.py · {a.ruta.name} ===")
    a.cifras()
    a.soluciones("cap2_soluciones.json")
    a.temario(DEBE_CUBRIR)
    a.fuentes(FUENTES)
    a.afirmaciones(AFIRMACIONES)
    a.accesibilidad()
    a.geomapas()
    a.formulas_escapadas()
    a.codificacion()
    a.enlaces()
    a.coherencia(CADENAS, ORDENES)
    a.peso()
    return a.cierre()


if __name__ == "__main__":
    sys.exit(main())
