#!/usr/bin/env python3
"""
audita_texto_cap5.py — auditor de prosa del capítulo 5

Material de Estadística Espacial 2026-II (20929). T3.6.

Copiado del molde de `audita_texto_cap4.py`. Toda la maquinaria vive en
`audita_texto_base.py` y aquí solo se declara **qué** comprobar.

Qué comprueba, por encima:

  · que **toda cifra de la prosa** esté en `cap5_datos.json` o en
    `cap5_soluciones.json`, incluidas las de dentro de KaTeX;
  · que cada celda de las cinco tablas de solución diga lo que su JSON dice;
  · que el capítulo cubra los doce módulos que el §6 del plan le asigna;
  · que cite sus fuentes y sostenga las afirmaciones que tiene que hacer;
  · accesibilidad del marcado, los `.geomapa` y su presupuesto;
  · que la codificación no se haya roto y que los enlaces resuelvan;
  · **dos comprobaciones propias**, que el núcleo no puede hacer y que se
    escriben aquí en vez de tocarlo. Ver abajo.

EL TOPE DE PESO ES 820 KB Y NO LOS 700 DE LA CASA, y la aritmética va
escrita porque no es una marca de agua levantada bajo presión:

  · el documento pesa **754 KB**, así que con el tope de la casa este
    auditor daría rojo sobre un capítulo correcto;
  · subir `TOPE_KB` para todos NO vale. La cota que ata esa comprobación
    a su arnés es **por encima del tamaño del documento y por debajo de
    ese tamaño + 312 KB** —`prueba_texto.py` la tumba inyectando 320 000
    bytes de comentario—, así que un tope de 820 para todos dejaría
    CIEGO al capítulo 2, que pesa 515;
  · 820 deja **66 KB de margen** sobre lo publicado, que es sitio para
    una corrección de T3.6 y muy poco para un ensamblado desbocado, y
    queda 243 KB por debajo del techo que el arnés necesita perforar.

`peso()` acepta el tope por argumento desde T0.5 justamente para esto, y
el fixture de demostración ya lo usa así.

Y EL PRESUPUESTO DE GEOMETRÍA ES 200 KB, con un punto ciego declarado.
El núcleo suma el peso de los mapas cuyo `fuente` es un JSON literal, y
los cinco de este capítulo pesan **157 KB**. Los otros siete —las
superficies del deslizador de σ— entran por una FUNCIÓN, así que
`geomapas()` los salta con un «---» y sus 174 KB no entran en esa cuenta.
No quedan sin auditar —`audita_cap5.py` los recalcula uno a uno desde
T3.4b, y el modo `rejilla` cruza el núcleo desde A.22— pero sí quedan
fuera del presupuesto, y eso se dice en vez de dejar que el 157 de 200 se
lea como si fuera todo. La comprobación propia `familia()` de abajo les
pone su propio techo.

Uso:  python3 precalculo/audita_texto_cap5.py
Devuelve 1 si algo falla.
"""
from __future__ import annotations

import json
import re
import sys

from audita_texto_base import SALIDAS, Auditor

# El tope de peso de ESTE capítulo. La aritmética, en el encabezado.
TOPE_CAP5_KB = 820.0
# El techo de las siete superficies del deslizador, que el núcleo no ve.
TOPE_FAMILIA_KB = 200.0

# Cifras que NO son resultados: identificadores, años, códigos y versiones.
ESTRUCTURALES = {
    "20929",                                   # el código de la asignatura
    # Los años de la bibliografía y de las citas del texto
    "2026", "2025", "2024", "2023", "2022", "2021", "2019", "2015", "2014",
    "2013", "2011", "1993",
    "4.0",                                     # CC BY-NC-ND 4.0
    "2.ª",                                     # la edición de Bivand et al.
    # Números pequeños de estructura (módulos, capítulos, semanas)
    "0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12",
    # La regla de Scott lleva su exponente en la prosa, y es una fórmula,
    # no una medición: −1/6 en dos dimensiones.
    "1/6",
    # El nivel de una banda puntual y el nsim pequeño que el módulo 10
    # contrasta con el de 999, los dos escritos como aritmética a la vista.
    "39", "95",
}

# El temario que el §6 del plan le asigna al capítulo 5, módulo a módulo.
# Tokens largos a propósito: buscar «k» daría OK dentro de cualquier cosa.
#
# OJO CON LOS NOMBRES DE `spatstat.data`: el §6 nombra `bei` y `chorley`
# por su identificador, y este capítulo SÍ los escribe en la prosa (dentro
# de `<code>`, que `texto_con_codigo` conserva). `redwood` y
# `japanesepines`, en cambio, solo aparecen dentro de bloques `<pre>` o de
# las soluciones, así que no se exigen: pedir lo que el capítulo no dice
# da MAL sobre un capítulo que sí cubre el tema.
DEBE_CUBRIR = [
    # Módulo 1 — de contar a suavizar
    ("el estimador núcleo de la intensidad", "estimador núcleo"),
    ("el puente desde el conteo por cuadrantes", "cuadrantes"),
    ("que la vecindad se solapa y no tiene bordes rectos", "se solapa"),
    ("la ventana de trabajo y por qué se baja a una localidad", "kennedy"),
    ("el término de corrección de borde e(u), aunque sea para aplazarlo", "corrección de borde"),
    # Módulo 2 — el núcleo importa poco, el ancho lo es todo
    ("los cuatro núcleos comparados al mismo σ", "epanechnikov"),
    ("que «al mismo σ» es a la misma desviación típica", "desviación típica"),
    ("que las cuatro superficies correlacionan casi 1", "correlacionan"),
    ("el ancho de banda como la decisión que manda", "ancho de banda"),
    ("la escala de color común a las siete superficies", "una sola escala de color"),
    # Módulo 3 — selectores de ancho de banda
    ("bw.diggle", "bw.diggle"),
    ("bw.ppl", "bw.ppl"),
    ("bw.CvL", "bw.cvl"),
    ("bw.scott", "bw.scott"),
    ("qué optimiza cada uno", "validación cruzada"),
    ("el criterio de Cronie y van Lieshout", "cronie"),
    ("el selector que devuelve el extremo de su intervalo", "intervalo de búsqueda"),
    # Módulo 4 — corrección de borde en la KDE
    ("la identidad que la comprueba: la integral vale n", "integral"),
    ("la corrección de Diggle, que conserva el conteo", "diggle = true"),
    ("que la corrección por defecto se pasa", "se pasa"),
    ("que sin corregir la masa se escapa", "se escapa"),
    ("que aquí corregir el borde no cuesta nada", "cuestan lo mismo"),
    # Módulo 5 — la KDE como mapa de calor
    ("el mapa de calor y lo que se le atribuye", "mapa de calor"),
    ("la oferta de sedes", "oferta"),
    ("las sedes con grado 11", "grado 11"),
    ("la demanda pesada por los evaluados de Saber 11", "saber 11"),
    ("que la resolución de la rejilla acaba eligiendo selector", "resolución"),
    # Módulo 6 — intensidad relativa y riesgo relativo
    ("el riesgo relativo", "riesgo relativo"),
    ("que es un cociente de dos intensidades", "cociente de dos intensidades"),
    ("el casos-controles de chorley", "chorley"),
    # La frase la pone el JSON —«cáncer de pulmón, no población sana»— y no
    # el ensamblador, así que el token es el suyo. La versión anterior
    # exigía «no ES población sana», que era una segunda frase mía diciendo
    # lo mismo dos renglones después; al quitar el tartamudeo, este auditor
    # lo cazó en el acto.
    ("que los controles no son población sana", "no población sana"),
    ("que lo colombiano es proporción de tipo y no riesgo", "proporción de tipo"),
    ("que relrisk devuelve el segundo nivel del factor", "segundo nivel"),
    # Módulo 7 — covariables
    ("rhohat", "rhohat"),
    ("la covariable definida en toda la ventana", "covariable"),
    ("bei y su elevación", "elevación"),
    ("la pendiente del terreno", "pendiente"),
    ("que el titular de una curva rhohat lo domina su cola", "cola"),
    ("el bulto entre los percentiles 5 y 95", "bulto"),
    # Módulo 8 — el Poisson inhomogéneo
    ("el proceso de Poisson inhomogéneo", "poisson inhomogéneo"),
    ("su verosimilitud", "verosimilitud"),
    ("la aproximación de Berman-Turner", "berman"),
    ("la cuadratura y sus puntos ficticios", "puntos ficticios"),
    ("que el AIC depende de la cuadratura", "aic"),
    ("que la EMV homogénea es n entre el área", "n/|w|"),
    # Módulo 9 — ppm y la lectura de los coeficientes
    ("el ajuste con ppm", "ppm"),
    ("la lectura de los coeficientes", "coeficientes"),
    ("los errores estándar que no salen", "errores estándar"),
    ("la información de Fisher singular", "singular"),
    ("el número de condición", "condición"),
    ("centrar y escalar como arreglo", "centrar"),
    # Módulo 10 — diagnóstico del ajuste
    ("los residuos de un ppm y qué son de verdad", "residuos"),
    ("la K inhomogénea", "k inhomogénea"),
    ("las envolventes sobre el modelo ajustado", "modelo ajustado"),
    ("que la referencia es la media de las simulaciones", "media de las simulaciones"),
    # Módulo 11 — conglomerado y autoexcitación
    ("los procesos de conglomerado", "conglomerado"),
    ("el proceso de Thomas", "thomas"),
    ("el de Matérn", "matérn"),
    ("el Cox log-gaussiano", "log-gaussiano"),
    ("kppm y el contraste mínimo", "contraste mínimo"),
    ("que kppm elige su corrección sin decirlo", "statargs"),
    ("el proceso de Hawkes", "hawkes"),
    ("la razón de ramificación", "razón de ramificación"),
    ("la conexión con fraude", "fraude"),
    ("la conexión con sismología", "sísmic"),
    ("el efecto medido de los duplicados", "duplicados"),
    # Módulo 12 — cierre
    ("el proyecto integrador, formulado", "proyecto integrador"),
    ("el enlace hacia los datos de área del capítulo 6", "datos de área"),
]

# Tokens largos: los cortos caben dentro de otras palabras. «cox» NO está
# —cabe en cualquier sitio— y por eso se cita como «log-gaussiano» arriba.
FUENTES = [
    "diggle", "berman", "turner", "loader", "cronie", "lieshout",
    "scott", "ogata", "hawkes", "thomas", "matérn",
    "baddeley", "rubak", "pebesma", "bivand", "moraga", "giraldo",
]

# Las afirmaciones que este capítulo TIENE que hacer. Si una desaparece en
# una reescritura, el capítulo deja de decir lo que el plan le encarga y
# nadie se entera: el HTML seguiría siendo válido y la consola limpia.
AFIRMACIONES = [
    ("dice que el peso del núcleo decae con la distancia y ocupa el lugar del tamaño de celda",
     "ocupa el lugar del tamaño de celda"),
    ("declara que la rejilla de cuadrantes la puso alguien",
     "la rejilla la puso alguien"),
    ("dice que comparar núcleos al mismo σ es compararlos a la misma desviación típica",
     "no al mismo soporte"),
    ("declara que sin esa escala la tabla demostraría lo contrario",
     "lo contrario de lo que demuestra"),
    ("dice que una celda más ancha que el núcleo dibuja la rejilla y no el núcleo",
     "dibuja su propia rejilla"),
    ("declara que «el ancho óptimo» no es una propiedad del patrón",
     "no es una propiedad del patrón"),
    ("dice que un óptimo que coincide con el borde del intervalo no es un óptimo",
     "no es un óptimo"),
    ("declara que el aviso va a la consola y el número a la variable",
     "el número va a la variable"),
    ("dice que la corrección por defecto divide donde se estima y la de Diggle donde está el dato",
     "donde está el dato"),
    ("declara que las tres correcciones dan mapas igual de plausibles",
     "los tres salen plausibles"),
    ("dice que la misma palabra nombra una operación gratis y una carísima",
     "una operación gratis y una carísima"),
    ("declara que llamar «demanda» a uno de los tres mapas es una decisión",
     "es una decisión, no una descripción"),
    ("dice que la resolución del ráster acabó eligiendo el selector",
     "aquí ha elegido selector"),
    ("declara que la corrección de borde se cancela en un cociente",
     "se cancela"),
    ("avisa de que relrisk pinta el segundo nivel del factor",
     "segundo nivel"),
    ("declara que la guarda que caza eso es comprobar la orientación contra el dato",
     "orientación contra el dato"),
    ("dice que lo oficial está concentrado y qué significa eso",
     "es mayoría en poca superficie"),
    ("declara que contar puntos y mirar el mapa contestan preguntas distintas",
     "contestan preguntas distintas"),
    ("dice que el titular de una rhohat es casi siempre su cola",
     "donde apenas hay puntos"),
    ("declara que publicar covariables que no funcionan es la mitad de la lección",
     "es la mitad de la lección"),
    ("dice que dos ppm con cuadraturas distintas no se comparan por AIC",
     "no son comparables"),
    ("declara que la cuadratura viaja con el modelo",
     "viaja con el modelo"),
    ("dice que el ajuste crudo devuelve coeficientes plausibles y ningún error estándar",
     "toda la pinta de serlo"),
    ("declara que vcov() no falla, avisa y devuelve NULL",
     "avisa y devuelve"),
    ("dice que lo que decide es que haya un error estándar por coeficiente",
     "un error estándar por coeficiente"),
    ("declara que una z pequeña es ausencia de relación LOG-LINEAL y no de relación",
     "no hay relación log-lineal"),
    ("dice que un modelo no ve lo que no puede escribir",
     "no ve lo que no puede escribir"),
    ("declara qué es un residuo en un proceso puntual",
     "no hay un residuo por observación"),
    ("dice por qué el residuo suavizado queda ciego a la interacción",
     "reproduce por construcción la tendencia"),
    ("da el veredicto del diagnóstico",
     "no explica que los colegios estén cerca"),
    ("declara que cambiar la corrección de kppm no es un acelerón sino otra respuesta",
     "es otra respuesta"),
    ("dice que el contraste mínimo ajusta el modelo a una estimación de K",
     "lo ajusta a una estimación de k"),
    ("declara que un ajuste de conglomerado sin su estimación de K está incompleto",
     "está incompleto"),
    ("dice que la hipótesis sobre los duplicados se midió y salió falsa",
     "la hipótesis es falsa"),
    ("declara que la fuente del caso trabajado no llegó y por eso no se escribe",
     "la fuente no llegó"),
]

# Si la codificación se rompe, las tildes no desaparecen: se convierten en
# otra cosa. Se exigen cadenas CONCRETAS que este capítulo usa de verdad.
#
# El «≤» NO va: el capítulo no lo escribe nunca como carácter suelto.
# El «−» (U+2212) SÍ: el módulo 3 publica el exponente −1/6 de Scott.
CADENAS = [
    "σ", "λ", "ρ", "²", "−", "×", "—", "–", "«", "»", "·",
    "ó", "í", "é", "ñ", "á", "¿",
    "núcleos", "intensidad", "envolvente", "conglomerado", "función",
    "Bogotá", "Kennedy", "Saber 11", "Cronie", "Matérn", "Berman",
]

# Las órdenes de KaTeX que este capítulo escribe de verdad. Son cinco
# fórmulas y son suyas; si una reescritura las convierte en imagen o en
# texto plano, esto lo dice.
ORDENES = [
    r"\hat\lambda", r"\frac", r"\sum", r"\int", r"\exp",
    r"\sigma", r"\mu", r"\beta", r"\rho", r"\text{Poisson}",
]


def familia(a: Auditor) -> None:
    """LAS SIETE SUPERFICIES DEL DESLIZADOR, que el núcleo no ve.

    `geomapas()` suma el peso de los mapas cuyo `fuente` es un JSON
    literal. El de `cap5-familia` es una FUNCIÓN —así es como el motor
    deja que un deslizador cambie lo pintado, y así lo hace el capítulo 1
    con sus siete campos de φ—, de modo que el núcleo lo salta con un
    «---» y sus siete superficies quedan fuera de todas sus cuentas.

    No quedan sin auditar: `audita_cap5.py` las recalcula una a una desde
    T3.4b. Pero «no es del núcleo» no es lo mismo que «no es de nadie».

    Y TODO LO DE AQUÍ SE LEE DEL DOCUMENTO, NO DEL PRECÁLCULO. Escrito al
    revés la primera vez —comparando dos archivos de `salidas/` entre
    sí— y lo destapó el arnés al ir a inyectarle defectos: una
    comprobación que no mira el HTML **no se puede tumbar tocando el
    HTML**, así que habría entrado en la lista de las que nadie ha visto
    fallar. Peor: tampoco protegía. El ensamblador podía empaquetar mal
    las siete superficies, o dejarse una, y estas líneas habrían seguido
    dando OK sobre el JSON intacto de al lado. Lo que se audita es lo que
    se publica.

      · que las siete viajen dentro del documento y declaren su σ, que es
        la CLAVE con la que el deslizador las busca —emparejar por índice
        descuadró dos listas en silencio en T1.2 y en T1.3—;
      · que esos σ sean exactamente los del JSON de cifras, carácter a
        carácter: se escriben en dos archivos con precisiones distintas, y
        ahí el `find()` devolvería `undefined` sin avisar;
      · que la escala de color declarada sea la MISMA en las siete, que es
        de lo que depende la tesis del módulo 2 —normalizada cada una
        contra su propio máximo, el mapa diría lo contrario que la tabla—;
      · que cada una traiga sus cortes y su rejilla empaquetada;
      · y que quepan en su propio techo de peso.
    """
    print("\n=== Las siete superficies del deslizador ==================")
    D = json.loads((SALIDAS / "cap5_datos.json").read_text(encoding="utf-8"))
    sig_dato = D["m2"]["familia"]["sigmas_m"]
    n_esperado = D["meta"]["rejilla"]["familia_n"]

    m = re.search(r"const FAM5 = (\[.*?\]);\n", a.doc, re.S)
    if not a.exige(m is not None, "el documento lleva dentro la familia del deslizador"):
        return
    try:
        fam = json.loads(m.group(1))
    except json.JSONDecodeError as e:
        a.exige(False, "la familia del deslizador es JSON válido", str(e)[:60])
        return

    a.exige(len(fam) == n_esperado, "el deslizador trae sus superficies",
            f"{len(fam)} de {n_esperado}")

    sig_doc = [g.get("sigma_m") for g in fam]
    a.exige(all(s is not None for s in sig_doc),
            "cada superficie declara el σ con que se estimó",
            f"{sum(s is not None for s in sig_doc)} de {len(fam)}")

    a.exige(sig_doc == sig_dato,
            "los σ del documento y los del precálculo casan uno a uno",
            "" if sig_doc == sig_dato else f"{sig_doc[:2]}… contra {sig_dato[:2]}…")

    escalas = {tuple(g.get("escala_comun") or ()) for g in fam}
    a.exige(len(escalas) == 1 and all(escalas),
            "las siete comparten una sola escala de color",
            f"{len(escalas)} escala(s) distinta(s)")

    con_cortes = sum(bool(g.get("cortes")) for g in fam)
    a.exige(con_cortes == len(fam), "cada superficie trae sus cortes calculados en R",
            f"{con_cortes} de {len(fam)}")

    # EMPAQUETADAS, que es como viajan: máscara en tiradas (`zqm`) y
    # diferencias por fila (`zqd`). Si alguna llegara con el array `zq`
    # entero, el decodificador de la plantilla la dibujaría en blanco.
    empacadas = sum(("zqd" in g and "zqm" in g and "zq" not in g) for g in fam)
    a.exige(empacadas == len(fam), "las siete viajan empaquetadas y ninguna cruda",
            f"{empacadas} de {len(fam)}")

    celdas = {(g.get("nx"), g.get("ny")) for g in fam}
    a.exige(len(celdas) == 1, "las siete comparten rejilla", f"{celdas}")

    kb = len(m.group(1).encode("utf-8")) / 1024
    a.exige(kb <= TOPE_FAMILIA_KB, "las siete caben en su propio presupuesto",
            f"{kb:.1f} KB de {TOPE_FAMILIA_KB:.0f} KB, tal como viajan")


def main() -> int:
    a = Auditor(
        capitulo="capitulo-5-intensidad-nucleos.html",
        var_entorno="CAP5_HTML",
        jsons=["cap5_datos.json", "cap5_soluciones.json"],
        estructurales=ESTRUCTURALES,
        # 200 KB para los CINCO mapas que el núcleo sabe pesar. Las siete
        # superficies del deslizador van por función y tienen su propio
        # techo en `familia()`; el encabezado lo explica.
        presupuesto_geomapa_kb=200.0,
        json_mapas="cap5_mapas.json",
    )
    print(f"\n=== audita_texto_cap5.py · {a.ruta.name} ===")
    a.cifras()
    a.soluciones("cap5_soluciones.json")
    a.temario(DEBE_CUBRIR)
    a.fuentes(FUENTES)
    a.afirmaciones(AFIRMACIONES)
    a.accesibilidad()
    a.geomapas()
    familia(a)
    a.formulas_escapadas()
    a.codificacion()
    a.enlaces()
    a.coherencia(CADENAS, ORDENES)
    a.peso(TOPE_CAP5_KB)
    return a.cierre()


if __name__ == "__main__":
    sys.exit(main())
