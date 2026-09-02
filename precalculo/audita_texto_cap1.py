#!/usr/bin/env python3
"""
audita_texto_cap1.py — auditor de prosa del capítulo 1

Material de Estadística Espacial 2026-II (20929). T1.2.

Copiado de `audita_texto_demo.py`, que es el molde. Fíjate en lo corto que
es: toda la maquinaria vive en `audita_texto_base.py` y aquí solo se
declara **qué** comprobar, no **cómo**. En Diseño de Experimentos cada
auditor eran entre 370 y 677 líneas con el contenido cableado, y por eso un
fallo del núcleo —retirar las fórmulas de KaTeX antes de extraer los
números— sobrevivió en cinco auditores a la vez informando «limpio».

Qué comprueba, por encima:

  · que **toda cifra de la prosa** —incluidas las de dentro de las
    fórmulas— esté en `cap1_datos.json` o en `cap1_soluciones.json`;
  · que el capítulo cubra los temas que el §6 del plan le asigna;
  · que cite sus fuentes y sostenga las afirmaciones que tiene que hacer;
  · accesibilidad del marcado, los `.geomapa` y su presupuesto;
  · que la codificación no se haya roto (las tildes son el canario);
  · que los enlaces relativos existan.

Uso:  python3 precalculo/audita_texto_cap1.py
Devuelve 1 si algo falla.
"""
from __future__ import annotations

import sys

from audita_texto_base import Auditor

# Cifras que NO son resultados: identificadores, años, códigos, versiones y
# referencias bibliográficas. Se declaran para que el auditor no denuncie
# el «1854» de Snow como una cifra sin respaldo.
ESTRUCTURALES = {
    "20929",                                  # el código de la asignatura
    "2026", "2025", "2024", "2023", "2022", "2020", "2019", "2015", "2014",
    "2013", "2011", "1998", "1993", "1992", "1988", "1977", "1975", "1970",
    "1961", "1955", "1954", "1950", "1934", "1854",   # el brote de Soho
    # Clark y Evans (1954) y Donnelly (1978), las dos citas del índice del
    # módulo 3. El 1954 llevaba desde su párrafo pasando SIN estar
    # declarado: lo dejaba pasar el índice de comparaciones, que con más de
    # cien mil entradas absorbe una cifra de cuatro dígitos por azar. El
    # 1978 no tuvo esa suerte y por eso se vio. Es el punto ciego que
    # mide `mide_punto_ciego.py`, y la respuesta es declarar, no ampliar la
    # tolerancia. (2026-08-10)
    "1978",
    "9377", "4326", "3857", "3116", "32617", "28992", "4267", "32119",
    "1.2", "4.4", "0.05", "0.01", "95", "90", "99",
    "1.0.22", "3.5.1", "1.4.2", "2.1.5", "4.2", "1.4.3", "1.8.80", "0.7.1",
    "0.4.11", "0.2.5",                        # versiones de los paquetes
    "3.8.5", "3.13.0", "9.5.1", "4.4.1",      # GDAL, GEOS, PROJ y R
    "4.0",                                    # CC BY 4.0 / CC BY-SA 4.0
    "0.5", "0.2", "0.3", "0.4", "1.1", "1.3", "8.1", "8.4", "9.2", "9.3",
    "9.4",                                    # secciones del texto guía
    "46", "234", "240",                       # la referencia de Tobler (1970)
    "12.25",                                  # la versión del dato de la SED
}

# El temario que el §6 del plan le asigna al capítulo 1. Los tokens son
# largos a propósito: buscar «ley» daría OK dentro de «lejos» y la
# comprobación pasaría siempre. Una comprobación que no puede fallar no
# comprueba nada — es la lección de T0.5.
DEBE_CUBRIR = [
    ("el mapa de Snow y el cólera", "snow"),
    ("el patrón puntual como tipo de dato", "patrón puntual"),
    ("el dato de área", "dato de área"),
    ("el dato geoestadístico", "geoestadístico"),
    ("la primera ley de Tobler", "tobler"),
    ("el índice de Moran", "moran"),
    ("el correlograma por bandas", "correlograma"),
    ("por qué se rompe el error estándar", "error estándar"),
    ("la cobertura del intervalo de confianza", "cobertura"),
    ("el tamaño de muestra efectivo", "efectivo"),
    ("la estacionariedad", "estacionariedad"),
    ("la isotropía", "isotropía"),
    ("el problema de la realización única", "una sola realización"),
    ("el variograma", "variograma"),
    ("la escala y el MAUP", "maup"),
    ("el efecto Gehlke y Biehl", "gehlke"),
    ("el ecosistema de paquetes", "ecosistema"),
    ("la anatomía de un objeto sf", "sfg"),
    ("la ventana de observación de un ppp", "ventana de observación"),
    ("la validación cruzada espacial", "validación cruzada"),
    ("la fuga de información entre pliegues", "fuga de información"),
    ("el glosario de notación", "notación"),
    ("las discrepancias declaradas entre R y Python", "discrepancia"),
    ("que los cortes los calcula classInt", "classint"),
    ("la ventana cambia lambda", "ventana"),
]

# Tokens largos: «men» daría OK dentro de «momento».
FUENTES = [
    "pebesma", "bivand", "baddeley", "cressie", "tobler", "moraga",
    "gómez-rubio", "numata", "ripley", "burrough",
    "ideam", "ministerio de educación nacional",
    "secretaría de educación del distrito", "ncgia",
]

# Las afirmaciones que este capítulo TIENE que hacer. Si una desaparece en
# una reescritura, el capítulo deja de decir lo que el plan le encarga y
# nadie se entera: el HTML seguiría siendo válido y la consola limpia.
AFIRMACIONES = [
    ("dice que lo aleatorio es distinto en cada tipo de dato",
     "qué es aleatorio"),
    ("advierte de que el argumento de Snow es geométrico, no epidemiológico",
     "geométrico"),
    ("dice que la ventana forma parte del estimador",
     "la ventana es parte del dato"),
    ("distingue sesgo de la estimación de sesgo de la confianza",
     "no es la estimación, es"),
    ("advierte de que n_eff supone equicorrelación y eso es falso en el espacio",
     "equicorrelación"),
    ("dice que hay un techo en la información",
     "techo"),
    ("dice que agregar NO siempre infla la correlación",
     "no siempre"),
    ("declara la condición del efecto Gehlke-Biehl",
     "no tenga estructura espacial"),
    ("dice que la unidad de análisis es una decisión de modelado",
     "decisión de modelado"),
    ("advierte de que la CV por bloques no es «la buena» siempre",
     "no es «la buena» siempre"),
    ("declara que una discrepancia sin explicar es un fallo",
     "sin explicar"),
    ("declara la frontera con el capítulo 10",
     "es del capítulo 10"),
]

# Si la codificación se rompe, las tildes no desaparecen: se convierten en
# otra cosa. Se exigen cadenas CONCRETAS que este capítulo usa de verdad,
# no una lista aspiracional de símbolos: un «σ» que el capítulo no escribe
# daría MAL siempre y acabaría enseñando a ignorar el informe.
CADENAS = [
    # Solo caracteres que el capítulo usa DE VERDAD. La primera versión de
    # esta lista pedía «ρ», «μ», «σ²», «≥» y «≠», que el capítulo escribe en
    # KaTeX (\rho, \mu) y no como carácter suelto: daban MAL sobre un
    # capítulo intacto. Una comprobación que falla siempre acaba enseñando a
    # ignorar el informe, que es exactamente lo que el auditor no puede
    # permitirse. Los capítulos 8 y 9 añadirán los suyos cuando los usen.
    "λ", "γ", "−", "×", "²", "±", "°", "«", "»", "—", "–", "§",
    "ó", "í", "é", "ñ", "ü", "¿",
    "Deserción", "autocorrelación", "estacionariedad", "isotropía",
    "realización", "cólera", "Bogotá", "Soho",
]

ORDENES = [r"\frac", r"\lambda", r"\rho", r"\gamma", r"\sum", r"\text",
           r"\operatorname", r"\mathbb", r"\bar", r"\lVert"]


def main() -> int:
    a = Auditor(
        capitulo="capitulo-1-datos-espaciales.html",
        var_entorno="CAP1_HTML",
        jsons=["cap1_datos.json", "cap1_soluciones.json"],
        estructurales=ESTRUCTURALES,
        presupuesto_geomapa_kb=120.0,
        # Los cortes de clase que el HTML incrusta salen de AQUÍ, no del
        # JSON de cifras. Va por su propio parámetro para que sus decenas de
        # miles de coordenadas no entren en el índice de la prosa.
        json_mapas="cap1_mapas.json",
    )
    print(f"\n=== audita_texto_cap1.py · {a.ruta.name} ===")
    a.cifras()
    a.soluciones("cap1_soluciones.json")
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
