#!/usr/bin/env python3
"""
audita_texto_cap3.py — auditor de prosa del capítulo 3

Material de Estadística Espacial 2026-II (20929). T2.6.

Copiado de `audita_texto_cap1.py`, que es el molde. Toda la maquinaria vive
en `audita_texto_base.py` y aquí solo se declara **qué** comprobar, no
**cómo**.

Qué comprueba, por encima:

  · que **toda cifra de la prosa** esté en `cap3_datos.json` o en
    `cap3_soluciones.json`;
  · que el capítulo cubra los temas que el §6 del plan le asigna;
  · que cite sus fuentes y sostenga las afirmaciones que tiene que hacer;
  · accesibilidad del marcado, los `.geomapa` y su presupuesto;
  · que la codificación no se haya roto (las tildes son el canario);
  · que los enlaces relativos existan.

EL PRESUPUESTO DE ESTE CAPÍTULO ES 200 KB DE GEOMETRÍA, NO 120, y es una
desviación declarada (A.14 del plan): 1 122 municipios no bajan de 12 547
vértices con ninguna tolerancia, porque el suelo de `ms_simplify` con
`keep_shapes = TRUE` es estructural. Los capítulos 1 y 2 nunca lo tocaron
porque usan la capa departamental, de 33 rasgos.

Uso:  python3 precalculo/audita_texto_cap3.py
Devuelve 1 si algo falla.
"""
from __future__ import annotations

import sys

from audita_texto_base import Auditor

# Cifras que NO son resultados: identificadores, años, códigos y versiones.
ESTRUCTURALES = {
    "20929",                                   # el código de la asignatura
    "2026", "2025", "2024", "2023", "2022", "2021", "2020", "2019", "2018",
    "2016", "2015", "2013", "2011", "2010",
    "1996", "1985", "1976", "1974", "1978", "1950", "1940", "1935",
    # Códigos EPSG y versiones de paquete que el capítulo nombra
    "4326", "3116", "9377", "32119",
    "4.2", "4.0.2", "1.0.22", "0.4.11", "0.3.0", "2.1.2", "1.4.2",
    # Números pequeños de estructura (módulos, k, número de familias…)
    "0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12",
    "13", "20", "25", "30", "33", "50", "60", "100", "120", "200",
    "300", "400", "700", "1000",
    "8", "5",                                  # el 8 % de daltonismo, k = 5
    "4.0",                                     # CC BY 4.0
    # El DOI y el volumen de la referencia de Lum & Isaac
    "1740", "9713", "00960", "13",
    "2009", "1993",   # Machado et al. y ColorBrewer
}

# El temario que el §6 del plan le asigna al capítulo 3. Tokens largos a
# propósito: buscar «color» daría OK dentro de cualquier cosa.
DEBE_CUBRIR = [
    ("las decisiones que hay dentro de un coropleto", "coropleto"),
    ("conteos frente a tasas", "conteo"),
    ("que el mapa de conteos es el de la población", "dónde hay gente"),
    ("los intervalos iguales", "intervalos iguales"),
    ("los cuantiles", "cuantiles"),
    ("Fisher-Jenks", "fisher-jenks"),
    ("la desviación estándar como esquema", "desviación estándar"),
    ("head/tails", "head/tails"),
    ("la discrepancia de clasificación entre R y Python", "mapclassify"),
    ("el lado cerrado del intervalo", "lado cerrado"),
    ("cuántas unidades cambian de clase", "cambian de clase"),
    ("las paletas secuenciales", "secuencial"),
    ("las divergentes", "divergente"),
    ("las cualitativas", "cualitativ"),
    ("el daltonismo", "daltonismo"),
    ("la luminosidad como salvavidas", "luminosidad"),
    ("la gramática de tmap", "tmap"),
    ("los símbolos proporcionales", "símbolos proporcionales"),
    ("el dot density", "dot density"),
    ("el hexbin", "hexbin"),
    ("los cartogramas", "cartograma"),
    ("el MAUP", "maup"),
    ("el efecto escala", "efecto escala"),
    ("el efecto zonificación", "zonificación"),
    ("el gerrymandering", "gerrymandering"),
    ("la falacia ecológica", "falacia ecológica"),
    ("Robinson", "robinson"),
    ("la estratificación socioeconómica", "estratificación"),
    ("el redlining", "redlining"),
    ("la vigilancia predictiva", "predictiva"),
]

# Tokens largos: «men» daría OK dentro de «momento».
FUENTES = [
    "robinson", "olson", "dorling", "dougenik", "machado",
    "icfes", "saber 11", "holc", "lum", "brewer",
]

# Las afirmaciones que este capítulo TIENE que hacer. Si una desaparece en
# una reescritura, el capítulo deja de decir lo que el plan le encarga y
# nadie se entera: el HTML seguiría siendo válido y la consola limpia.
AFIRMACIONES = [
    ("dice que elegir el mapa es una decisión de modelado",
     "decisión de modelado"),
    ("advierte de que una clase puede quedarse vacía sin avisar",
     "sin avisar"),
    ("dice que el mapa de conteos es el de la población",
     "dónde hay gente"),
    ("declara que la tasa trae su propio problema",
     "su propio problema"),
    ("nombra la causa de la discrepancia R/Python",
     "lado cerrado del intervalo"),
    ("dice que Fisher-Jenks sí coincide",
     "coincide exactamente"),
    ("declara que el esquema y el k son parte del resultado",
     "parte del resultado"),
    ("dice qué salva a una paleta bajo daltonismo",
     "recorrido de luminosidad"),
    ("advierte de que tmap 4 rompió la API de tmap 3",
     "no corren"),
    ("dice que el área del símbolo, no el radio, es proporcional al valor",
     "no el radio"),
    ("declara que el dot density depende de la semilla",
     "depende de la semilla"),
    ("dice que el cartograma contiguo no puede ser exacto",
     "conservar la topología"),
    ("explica el efecto escala por la varianza que se destruye",
     "solo sobrevive"),
    ("dice que la partición real no tiene nada de especial",
     "nada de especial"),
    ("explica por qué las zonas arbitrarias dan correlaciones más altas",
     "es lo contrario de lo que casi todo el mundo espera"),
    ("declara que el ponderador es parte del trazado",
     "parte del trazado"),
    ("dice que una correlación ecológica no habla de personas",
     "no como afirmación sobre personas"),
    ("declara que el signo del estrato depende del filtro",
     "decide un puñado de municipios diminutos"),
    ("dice quién falta del mapa",
     "no salen en el mapa"),
    ("nombra la obligación de declarar la unidad y el esquema",
     "decir quién falta"),
    ("remite el MAUP al capítulo 4",
     "tamaño del cuadrante"),
]

# Si la codificación se rompe, las tildes no desaparecen: se convierten en
# otra cosa. Se exigen cadenas CONCRETAS que este capítulo usa de verdad.
CADENAS = [
    # Sin «−» (U+2212): los negativos del capítulo salen del formateador
    # con guion ASCII, así que exigirlo fallaría sobre un capítulo intacto.
    "×", "—", "–", "«", "»", "§", "≥",
    "ó", "í", "é", "ñ", "á", "¿",
    "clasificación", "cartografía", "geográfica", "estratificación",
    "Bogotá", "Antioquia", "Belén de Bajirá", "deserción",
]

# Solo órdenes de KaTeX que el capítulo escribe. Este capítulo es de
# decisiones, no de álgebra: no lleva fórmulas, así que la lista va vacía
# A PROPÓSITO y no por olvido. Exigir `\dfrac` aquí daría MAL sobre un
# capítulo intacto, que es la trampa que el auditor del capítulo 2 dejó
# anotada — y en la que volvió a caer.
ORDENES: list[str] = []


def main() -> int:
    a = Auditor(
        capitulo="capitulo-3-cartografia-maup.html",
        var_entorno="CAP3_HTML",
        jsons=["cap3_datos.json", "cap3_soluciones.json"],
        estructurales=ESTRUCTURALES,
        # LA DESVIACIÓN DECLARADA (A.14): 200 KB, no 120.
        presupuesto_geomapa_kb=200.0,
        json_mapas="cap3_mapas.json",
    )
    print(f"\n=== audita_texto_cap3.py · {a.ruta.name} ===")
    a.cifras()
    # LA DEUDA DE T2.6, SALDADA EN T3.6. Este auditor no llamaba a
    # `soluciones()`, y no era una decisión: era un olvido que se vio desde
    # el capítulo 4 y quedó anotado en el plan. Los cuatro ejercicios del
    # capítulo 3 publican sus tablas de paso con el mismo marcado que los
    # de los capítulos 1, 2, 4 y 5, así que la comprobación tenía sujeto y
    # debía estar corriendo sobre ellas desde el principio. Añadirla NO
    # toca el capítulo, que sigue cerrado y byte a byte como estaba: lo
    # que cambia es cuánto se le mira.
    a.soluciones("cap3_soluciones.json")
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
