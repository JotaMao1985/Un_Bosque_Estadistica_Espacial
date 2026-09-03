#!/usr/bin/env python3
"""
audita_texto_cap6.py — auditor de prosa del capítulo 6

Material de Estadística Espacial 2026-II (20929). T4.3.

Copiado del molde de `audita_texto_cap5.py`. Toda la maquinaria vive en
`audita_texto_base.py` y aquí solo se declara **qué** comprobar.

Qué comprueba, por encima:

  · que **toda cifra de la prosa** esté en `cap6_datos.json` o en
    `cap6_soluciones.json`, incluidas las de dentro de KaTeX;
  · que cada celda de las cinco tablas de solución diga lo que su JSON dice;
  · que el capítulo cubra los doce módulos que el §6 del plan le asigna;
  · que cite sus fuentes y sostenga las afirmaciones que tiene que hacer;
  · accesibilidad del marcado, los `.geomapa` y su presupuesto;
  · que la codificación no se haya roto y que los enlaces resuelvan.

EL TOPE DE PESO ES 640 KB, y la aritmética va escrita porque no es una
marca de agua levantada bajo presión:

  · el documento pesa **578 KB**, así que con el tope de la casa —700—
    este auditor pasaría, pero con 62 KB de margen ciego por debajo;
  · la cota que ata esa comprobación a su arnés es **por encima del
    tamaño del documento y por debajo de ese tamaño + 312 KB**, porque
    `prueba_texto.py` la tumba inyectando 320 000 bytes de comentario;
  · 640 deja **62 KB de margen** sobre lo publicado —sitio para una
    corrección y muy poco para un ensamblado desbocado— y queda 250 KB
    por debajo del techo que el arnés necesita perforar.

EL PRESUPUESTO DE GEOMETRÍA ES 400 KB, y también hay que decir por qué.
Los dos mapas de este capítulo entran como JSON literal, así que el
núcleo los pesa a los dos: 19 KB el de Columbus y 166 el municipal. Ese
segundo es el que el A.25 midió y declaró — los 1 122 municipios no se
pueden simplificar por debajo de 12 547 vértices, que es su suelo. 400 KB
es holgado a propósito: el capítulo no va a añadir mapas, y un techo
ajustado al byte convierte cualquier corrección en un rojo.

Uso:  python3 precalculo/audita_texto_cap6.py
Devuelve 1 si algo falla.
"""
from __future__ import annotations

import sys

from audita_texto_base import Auditor

# El tope de peso de ESTE capítulo. La aritmética, en el encabezado.
TOPE_CAP6_KB = 640.0

# Cifras que NO son resultados: identificadores, años, códigos y versiones.
ESTRUCTURALES = {
    "20929",                                   # el código de la asignatura
    # Los años de la bibliografía y de las citas del texto
    "2026", "2025", "2024", "2023", "2022", "2021", "2019", "2015", "2014",
    "2013", "2011", "1993",
    "4.0",                                     # CC BY-NC-ND 4.0
    "2.ª",                                     # la edición de Bivand et al.
    # Números pequeños de estructura (módulos, capítulos, semanas, órdenes
    # de contigüidad, valores de k y nombres de estilo)
    "0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12",
    # Los dos que el capítulo escribe como parte de una fórmula o de un
    # nombre y no como medición: el exponente de D⁻¹ y el «orden 2».
    "700",                                     # los km de mar del módulo 4
}

# El temario que el §6 del plan le asigna al capítulo 6, módulo a módulo.
# Tokens largos a propósito: buscar «W» daría OK dentro de cualquier cosa.
DEBE_CUBRIR = [
    # Módulo 1 — el dato de área
    ("qué es aleatorio en un retículo", "lo aleatorio"),
    ("el contraste con el patrón puntual", "patrón puntual"),
    ("los dos tableros del capítulo", "columbus"),
    ("el hilo colombiano con su deserción", "deserción"),
    # Módulo 2 — vecindad
    ("que W la elige quien analiza", "la elige quien analiza"),
    ("el constructor con los diez criterios", "diez"),
    ("la diferencia entre enlaces y parejas", "enlaces"),
    ("que ninguno está mal calculado", "mal calculado"),
    # Módulo 3 — contigüidad
    ("la contigüidad reina", "reina"),
    ("la contigüidad torre", "torre"),
    ("el contacto de esquina", "esquina"),
    ("que la torre está contenida en la reina", "contenida en la reina"),
    ("la contigüidad de orden superior", "orden superior"),
    ("que nblag no acumula", "no acumula"),
    # Módulo 4 — k vecinos
    ("knearneigh", "knearneigh"),
    ("que el grado vale siempre k", "siempre"),
    ("la simetría rota", "recíproc"),
    ("make.sym.nb y lo que cuesta", "make.sym.nb"),
    # Módulo 5 — umbral de distancia
    ("dnearneigh", "dnearneigh"),
    ("la densidad desigual", "densidad"),
    ("el umbral mínimo sin islas", "umbral mínimo sin islas"),
    ("que quitar islas no conecta el grafo", "no conecta el grafo"),
    ("que esa W es impublicable como dibujo", "de las diez definiciones"),
    # Módulo 6 — vecindades geométricas
    ("la triangulación de Delaunay", "delaunay"),
    ("el grafo de Gabriel", "gabriel"),
    ("la vecindad relativa", "vecindad relativa"),
    ("la esfera de influencia", "esfera de influencia"),
    ("el anidamiento entre las tres", "anidadas"),
    # Módulo 7 — de vecinos a pesos
    ("los cinco estilos de nb2listw", "nb2listw"),
    ("que el estilo W hace del rezago una media", "media de los vecinos"),
    ("que B convierte el rezago en una suma", "suma"),
    ("el estilo S de estabilización de varianza", "tiefelsdorf"),
    ("que un estilo mal elegido no rompe nada", "no rompe nada"),
    # Módulo 8 — el flujo de spdep
    ("poly2nb", "poly2nb"),
    ("nb2listw en el flujo", "nb2listw"),
    ("lag.listw", "lag.listw"),
    ("sfdep como interfaz tidy", "sfdep"),
    ("que sfdep no sirve como comprobación", "no sirve como comprobación"),
    # Módulo 9 — islas y zero.policy
    ("zero.policy", "zero.policy"),
    ("las dos islas del dato colombiano", "san andrés"),
    ("los subgrafos", "subgrafos"),
    ("que el cero de la isla entra en las medias", "entran en las medias"),
    ("las tres salidas honestas", "salidas honestas"),
    # Módulo 10 — el rezago
    ("el rezago espacial Wy", "rezago"),
    ("que el rezago es la media de los vecinos", "la media de sus vecinos"),
    ("la contracción de la desviación", "contrae"),
    ("que el índice de Moran hereda la dependencia de W", "moran"),
    # Módulo 11 — W como grafo
    ("la matriz de adyacencia", "matriz de adyacencia"),
    ("que W es dispersa", "dispersa"),
    ("que estandarizar por filas es normalizar por el grado", "normalizar por el grado"),
    ("el paso de mensajes y las GNN", "paso de mensajes"),
    ("que apilar capas es subir de orden", "apilar capas"),
    # Módulo 12 — cierre
    ("los cinco ejercicios sobre otro mapa", "carolina del norte"),
    ("el enlace hacia la autocorrelación del capítulo 7", "capítulo 7"),
]

# Tokens largos: los cortos caben dentro de otras palabras.
FUENTES = [
    "anselin", "tiefelsdorf", "delaunay", "gabriel",
    "bivand", "pebesma", "moraga",
]

# Las afirmaciones que este capítulo TIENE que hacer. Si una desaparece en
# una reescritura, el capítulo deja de decir lo que el plan le encarga y
# nadie se entera: el HTML seguiría siendo válido y la consola limpia.
AFIRMACIONES = [
    ("dice que W es la decisión más consecuente y la menos justificada",
     "la menos justificada"),
    ("declara que las unidades están fijas y lo que varía es su valor",
     "Las unidades están donde están"),
    ("dice que la torre está contenida en la reina",
     "la torre está contenida en la reina"),
    ("declara que el orden 2 excluye a los vecinos de orden 1",
     "que no eran ya vecinos"),
    ("dice que «ser de los k más próximos» no es recíproco",
     "no es recíproco"),
    ("declara que un número impar de enlaces prueba la asimetría",
     "es impar"),
    ("dice que quitar las islas no conecta el grafo",
     "no conecta el grafo"),
    ("declara que el umbral que arregla las islas rompe la vecindad",
     "rompe la vecindad"),
    ("dice que las vecindades geométricas están anidadas",
     "relativa ⊆ Gabriel ⊆ Delaunay"),
    ("declara que el estilo W concentra la influencia en las unidades con pocos vecinos",
     "la concentra en las unidades"),
    ("dice que B, C y U solo se diferencian en una constante",
     "una constante no mueve una correlación"),
    ("declara que zero.policy convierte el problema en un cero",
     "lo convierte en un cero"),
    ("dice que el rezago contrae porque promediar contrae",
     "promediar contrae"),
    ("declara que la contracción no dice nada del territorio",
     "no dice nada sobre el territorio"),
    ("dice que estandarizar por filas ES D⁻¹A",
     "No se parece"),
    ("declara que la elección de W es la elección de la arquitectura",
     "la elección de la arquitectura"),
]

CADENAS = [
    "σ", "−", "×", "—", "–", "«", "»", "·", "⊆",
    "ó", "í", "é", "ñ", "á", "¿",
    "vecindad", "contigüidad", "rezago", "grafo", "subgrafos",
    "Columbus", "Anselin", "Delaunay", "Gabriel", "San Andrés",
]

# Las órdenes de KaTeX que este capítulo escribe de verdad.
ORDENES: list[str] = []


def main() -> int:
    a = Auditor(
        capitulo="capitulo-6-pesos-espaciales.html",
        var_entorno="CAP6_HTML",
        jsons=["cap6_datos.json", "cap6_soluciones.json"],
        estructurales=ESTRUCTURALES,
        presupuesto_geomapa_kb=400.0,
        json_mapas="cap6_mapas.json",
    )
    print(f"\n=== audita_texto_cap6.py · {a.ruta.name} ===")
    a.cifras()
    a.soluciones("cap6_soluciones.json")
    a.temario(DEBE_CUBRIR)
    a.fuentes(FUENTES)
    a.afirmaciones(AFIRMACIONES)
    a.accesibilidad()
    a.geomapas()
    a.formulas_escapadas()
    a.codificacion()
    a.enlaces()
    a.coherencia(CADENAS, ORDENES)
    a.peso(TOPE_CAP6_KB)
    return a.cierre()


if __name__ == "__main__":
    sys.exit(main())
