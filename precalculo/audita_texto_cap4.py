#!/usr/bin/env python3
"""
audita_texto_cap4.py — auditor de prosa del capítulo 4

Material de Estadística Espacial 2026-II (20929). T3.3.

Copiado de `audita_texto_cap3.py`, que a su vez copia el molde del
capítulo 1. Toda la maquinaria vive en `audita_texto_base.py` y aquí solo
se declara **qué** comprobar, no **cómo**.

Qué comprueba, por encima:

  · que **toda cifra de la prosa** esté en `cap4_datos.json` o en
    `cap4_soluciones.json`;
  · que cada celda de las cinco tablas de solución diga lo que su JSON dice;
  · que el capítulo cubra los doce módulos que el §6 del plan le asigna;
  · que cite sus fuentes y sostenga las afirmaciones que tiene que hacer;
  · accesibilidad del marcado, los `.geomapa` y su presupuesto;
  · que la codificación no se haya roto (las tildes son el canario);
  · que los enlaces relativos existan.

EL PRESUPUESTO DE ESTE CAPÍTULO ES 150 KB DE GEOMETRÍA, NO 120, y es una
desviación declarada en T3.1 con una razón distinta de la del capítulo 3.
Allí eran 1 122 municipios de geometría de fondo que ninguna tolerancia
bajaba de 12 547 vértices. Aquí los 2 107 + 2 208 puntos **son el dato**:
un patrón puntual no se puede simplificar sin dejar de ser el patrón que
el capítulo 1 publicó. El archivo real usa 60,2 KB, el 40 % de lo
declarado — el presupuesto sobra, y aun así se comprueba, porque lo que
vigila no es el gasto de hoy sino el del día que alguien añada un mapa.

POR QUÉ ESTE CAPÍTULO SÍ LLAMA A `soluciones()` Y EL DEL 3 NO.
El capítulo 3 no la llama, y no es una decisión: es un olvido de T2.6 que
se ve desde aquí. Sus cuatro ejercicios publican tablas de paso con el
mismo marcado que las de los capítulos 1, 2 y 4, así que la comprobación
tiene sujeto y debería estar corriendo sobre ellas. Queda anotado en el
plan; arreglarlo es tocar el capítulo 3, que está cerrado y verificado, y
eso no cabe en T3.3.

Uso:  python3 precalculo/audita_texto_cap4.py
Devuelve 1 si algo falla.
"""
from __future__ import annotations

import sys

from audita_texto_base import Auditor

# Cifras que NO son resultados: identificadores, años, códigos y versiones.
ESTRUCTURALES = {
    "20929",                                   # el código de la asignatura
    # Los años de la bibliografía y de las citas del texto
    "2026", "2025", "2024", "2023", "2022", "2021", "2019", "2015", "2014",
    "2013", "2011", "1993",
    "4.0",                                     # CC BY-NC-ND 4.0
    "2.ª",                                     # la edición de Bivand et al.
    # La máquina del precálculo, que el módulo 10 declara al publicar tiempos
    "4.4.1", "20",                             # R 4.4.1 · aarch64-apple-darwin20
    # Números pequeños de estructura (módulos, capítulos, semanas, k)
    "0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12",
}

# El temario que el §6 del plan le asigna al capítulo 4, módulo a módulo.
# Tokens largos a propósito: buscar «k» daría OK dentro de cualquier cosa.
#
# OJO CON `japanesepines`: el §6 nombra los tres canónicos por su nombre de
# `spatstat.data`, pero la PROSA de este capítulo los llama «pinos
# japoneses» y el identificador solo aparece dentro de los bloques `<pre>`,
# que el auditor retira antes de buscar. Exigir el identificador daría MAL
# sobre un capítulo que sí cubre el tema. Se busca lo que el capítulo dice.
DEBE_CUBRIR = [
    # Módulo 1 — qué es un proceso puntual
    ("qué es un proceso puntual", "proceso puntual"),
    ("el objeto ppp", "ppp"),
    ("la ventana de observación", "ventana de observación"),
    ("las dos ventanas del patrón colombiano", "perímetro urbano"),
    ("el descarte silencioso de puntos fuera de la ventana", "quedan"),
    # Módulo 2 — la intensidad
    ("la intensidad λ", "intensidad"),
    ("el estimador por conteo", "n entre el área"),
    ("que λ puede no ser constante", "no tiene una sola"),
    # Módulo 3 — los tres regímenes
    ("el régimen aleatorio", "aleatorio"),
    ("el régimen regular", "regular"),
    ("el régimen agregado", "agregado"),
    ("los pinos japoneses", "pinos japoneses"),
    ("las células de cells", "cells"),
    ("las secuoyas de redwood", "redwood"),
    ("el índice de Clark-Evans", "clark-evans"),
    # Módulo 4 — CSR
    ("CSR y su nombre completo", "complete spatial randomness"),
    ("el proceso de Poisson homogéneo", "poisson homogéneo"),
    ("las dos propiedades definitorias", "dos propiedades"),
    ("que n cambia entre realizaciones", "no tienen el mismo n"),
    # Módulo 5 — el test de cuadrantes
    ("el test de cuadrantes", "test de cuadrantes"),
    ("el estadístico χ² y sus grados de libertad", "grados de libertad"),
    ("su supuesto de esperanza por celda", "esperanza menor que 5"),
    ("los dos patrones con el mismo χ²", "el mismo reparto por celda"),
    # Módulo 6 — el tamaño del cuadrante
    ("el índice de dispersión", "índice de dispersión"),
    ("que esto es el MAUP otra vez", "maup"),
    ("el efecto de escala del capítulo 3", "efecto de escala"),
    # Módulo 7 — G y F
    ("la función G", "g(r)"),
    ("la función F del espacio vacío", "espacio vacío"),
    ("la distancia al vecino más próximo", "vecino más próximo"),
    ("los puntos coincidentes del patrón colombiano", "puntos coincidentes"),
    ("el convenio de Kaplan-Meier en r = 0", "kaplan-meier"),
    # Módulo 8 — la K de Ripley
    ("la función K de Ripley", "ripley"),
    ("la transformación L de Besag", "besag"),
    ("que bajo CSR K vale πr²", "parábola"),
    # Módulo 9 — la correlación de pares
    ("la correlación de pares g(r)", "correlación de pares"),
    ("que K es acumulativa y arrastra", "acumulativa"),
    ("que g mira el anillo y no el disco", "anillo"),
    # Módulo 10 — efectos de borde
    ("los efectos de borde", "efectos de borde"),
    ("la corrección de borde", "corrección de borde"),
    ("la corrección de traslación", "traslación"),
    ("la corrección isotrópica de Ripley", "isotrópica"),
    ("qué pasa si el borde se ignora", "sin corregir"),
    ("el coste medido de cada corrección", "segundos"),
    # Módulo 11 — envolventes
    ("las envolventes de simulación", "envolvente"),
    ("el número de simulaciones", "nsim"),
    ("qué NO es el p-valor de una envolvente", "banda puntual"),
    ("el test de desviación global", "desviación global"),
    ("el test dclf y el MAD", "dclf"),
    ("el p-valor mínimo 1/(nsim+1)", "1/(nsim+1)"),
    ("el nivel de la banda por defecto, 2/(nsim+1)", "2/(nsim+1)"),
    # Módulo 12 — cierre
    ("la envolvente convexa como ventana del ejercicio 1", "envolvente convexa"),
    ("la corrección de Donnelly que el dato real no admite", "donnelly"),
    ("el enlace hacia el suavizado del capítulo 5", "suavizado"),
]

# Tokens largos: «ford» solo daría OK dentro de «Oxford», pero aquí no hay
# ninguna; «mad» sí es peligroso —cabe en «madre»— y por eso no está.
FUENTES = [
    "ripley", "besag", "clark-evans", "diggle", "loosmore", "ford",
    "kaplan-meier", "donnelly",
    "baddeley", "cressie", "pebesma", "bivand", "moraga", "giraldo",
    "spatstat",
]

# Las afirmaciones que este capítulo TIENE que hacer. Si una desaparece en
# una reescritura, el capítulo deja de decir lo que el plan le encarga y
# nadie se entera: el HTML seguiría siendo válido y la consola limpia.
AFIRMACIONES = [
    ("dice que la ventana forma parte del estimador y no lo acompaña",
     "forma parte de él"),
    ("declara que una λ sin su ventana no es verdadera ni falsa, sino incompleta",
     "ni verdadera ni falsa"),
    ("avisa de que ppp() descarta puntos con un aviso que nadie lee",
     "nadie lee"),
    ("dice que un solo número describe el patrón solo si λ es constante",
     "si λ es constante"),
    ("nombra la firma de Poisson: media y varianza valen lo mismo",
     "firma de poisson"),
    ("declara que una R sola, sin saber cuánto se mueve el azar, no dice nada",
     "no dice nada"),
    ("dice exactamente qué es lo que el χ² no mira",
     "dentro de su celda"),
    ("declara la ceguera del χ² por debajo del tamaño de celda",
     "menor que el cuadrante"),
    ("dice que pasar el test de cuadrantes no certifica aleatoriedad",
     "no certifica aleatoriedad"),
    ("repite la lección del capítulo 3: la escala es parte del resultado",
     "parte del resultado"),
    ("distingue G, que mira desde los puntos",
     "mira desde los puntos"),
    ("de F, que mira desde el espacio vacío",
     "mira desde el espacio vacío"),
    ("declara que un patrón con duplicados no es un proceso puntual simple",
     "no es un proceso puntual simple"),
    ("dice que Kaplan-Meier vale cero en r = 0 por convenio, no por el dato",
     "por convenio"),
    ("explica que g mira el anillo y no el disco",
     "no el disco"),
    ("dice que ignorar el borde no añade ruido sino dirección",
     "no añade ruido"),
    ("da la razón del signo del sesgo",
     "faltan vecinos, nunca sobran"),
    ("dice hacia dónde empuja ese sesgo",
     "más regular de lo que es"),
    ("declara que lo caro de la isotrópica es el borde y no el número de puntos",
     "lo que se paga es el borde, no n"),
    ("declara la corrección elegida en vez de abaratarla en silencio",
     "no es un atajo silencioso"),
    ("dice que la banda de la envolvente es puntual, r por r",
     "para cada r por separado"),
    ("mide cuántas simulaciones nulas se salen de su propia banda",
     "todas eran nulas por construcción"),
    ("dice que el p-valor mínimo es aritmética y no convención",
     "es aritmética"),
    ("declara que subir nsim con la banda por defecto cambia de contraste",
     "cambia de contraste"),
    ("dice que por eso la banda se ensancha en vez de estrecharse",
     "se ensancha"),
    ("declara que el estadístico y el rango de r son decisiones del analista",
     "una decisión del analista"),
    ("avisa de que la envolvente convexa decide y además lo esconde",
     "el borde lo ponen los puntos más extremos"),
    ("dice que la corrección canónica de Donnelly no existe para esta ventana",
     "no está disponible aquí"),
]

# Si la codificación se rompe, las tildes no desaparecen: se convierten en
# otra cosa. Se exigen cadenas CONCRETAS que este capítulo usa de verdad.
#
# El «−» (U+2212) SÍ va aquí, al revés que en el capítulo 3: este publica
# «L(r) − r» en la prosa, así que el signo largo existe en el documento. El
# «≤» NO va: el capítulo lo escribe como `\leq` dentro de KaTeX y nunca
# como carácter suelto, así que exigirlo daría MAL sobre un capítulo
# intacto — la trampa que el auditor del capítulo 2 dejó anotada.
CADENAS = [
    "λ", "χ²", "√", "²", "−", "×", "—", "–", "«", "»", "·",
    "ó", "í", "é", "ñ", "á", "¿",
    "aleatoriedad", "isotrópica", "traslación", "envolvente", "función",
    "Bogotá", "Distrito Capital", "Sumapaz", "Clark-Evans", "Kaplan-Meier",
]

# Las órdenes de KaTeX que este capítulo escribe de verdad. Aquí la lista
# NO va vacía —al contrario que en el capítulo 3, que es de decisiones y no
# lleva álgebra—: éste publica cinco fórmulas y son suyas. Si una
# reescritura las convierte en imagen o en texto plano, esto lo dice.
ORDENES = [
    r"\hat{\lambda}", r"\frac", r"\sum", r"\sqrt", r"\pi",
    r"\chi^2", r"\mathbf{1}", r"\leq", r"\bar{d}",
]


def main() -> int:
    a = Auditor(
        capitulo="capitulo-4-patrones-puntuales.html",
        var_entorno="CAP4_HTML",
        jsons=["cap4_datos.json", "cap4_soluciones.json"],
        estructurales=ESTRUCTURALES,
        # LA DESVIACIÓN DECLARADA (T3.1): 150 KB, no 120. Los puntos del
        # patrón son el dato, no geometría de fondo simplificable.
        presupuesto_geomapa_kb=150.0,
        # Los cortes de clase que el HTML incrusta salen de AQUÍ, no del
        # JSON de cifras. Va por su propio parámetro para que sus decenas de
        # miles de coordenadas no entren en el índice de la prosa.
        json_mapas="cap4_mapas.json",
    )
    print(f"\n=== audita_texto_cap4.py · {a.ruta.name} ===")
    a.cifras()
    a.soluciones("cap4_soluciones.json")
    a.temario(DEBE_CUBRIR)
    a.fuentes(FUENTES)
    a.afirmaciones(AFIRMACIONES)
    a.accesibilidad()
    a.geomapas()
    a.codificacion()
    a.enlaces()
    a.coherencia(CADENAS, ORDENES)
    a.peso()
    return a.cierre()


if __name__ == "__main__":
    sys.exit(main())
