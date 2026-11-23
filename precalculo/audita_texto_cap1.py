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

EL TOPE DE PESO ES 1000 KB desde el 2026-11-14, por orden de Javier: lo que
importa es la calidad de la información y de las explicaciones, no el tamaño.
La historia, para no repetirla: 700 de la casa, 730 el 2026-11-02 (los mapas
descritos) y, con la reescritura del módulo 5 (R1 · T1.1: dos deducciones, la
tabla de rellenar frente a ampliar), el capítulo llegó a 720 KB. Subirlo de
treinta en treinta convertía el tope en un presupuesto que cada ronda del
plan de mejora tendría que negociar, y eso es justo lo que no es:

  · es la alarma contra un ensamblado desbocado (T0.5), nada más;
  · la cota que la ata a su arnés es **por encima del tamaño y por debajo de
    ese tamaño + 312 KB**, porque `prueba_texto.py` la tumba inyectando
    320 000 bytes: 720 < 1000 < 1033. Como el capítulo ya pasa de 688 KB,
    crecer no deja ciego al arnés: solo lo hace bajar el tope por debajo del
    tamaño, o adelgazar el capítulo por debajo de 688 KB con el tope aquí.
  · Si un día el capítulo se acerca a 1000, se vuelve a subir con la misma
    cuenta: el contenido manda.

Uso:  python3 precalculo/audita_texto_cap1.py
Devuelve 1 si algo falla.
"""
from __future__ import annotations

import re
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
    # R1 · T1.4: lo que sustituye a las frases retiradas tiene que estar.
    ("dice que el factor entre las dos intensidades mide la inhomogeneidad",
     "inhomogeneidad"),
    ("da la condición de media de la estacionariedad intrínseca",
     "que su media sea cero"),
    ("dice que la referencia del variograma es el teórico promediado en la clase",
     "promediada sobre esos mismos pares"),
    ("dice que sin ponderar la media solo es insesgada con probabilidades iguales",
     "solo es insesgada cuando todas las probabilidades son iguales"),
    ("compara la red con una referencia de puntos uniformes",
     "de manera uniforme sobre el país"),
    ("distingue sesgo de la estimación de sesgo de la confianza",
     "no es la estimación, es"),
    # R1 · T1.6: lo que sustituye a las imprecisiones retiradas.
    ("llama ingenuo al reparto por igual entre bombas y dice qué ignora (módulo 1)",
     "el reparto es ingenuo porque ignora"),
    ("dice que la intensidad es del proceso y que n/|W| la estima (módulo 2)",
     "es una propiedad del proceso"),
    ("dice que en el tipo geoestadístico lo aleatorio es el campo (módulo 2)",
     "lo aleatorio es el propio campo"),
    ("dice que agregación y repulsión pueden cancelarse en la media de R (módulo 3)",
     "pueden cancelarse en la media"),
    ("dice bajo qué nula vale E[I] = −1/(n − 1) (módulo 3)",
     "hipótesis nula de permutación"),
    ("nombra el supuesto del remuestreo por departamentos (módulo 4)",
     "departamentos como independientes entre sí"),
    ("dice que la media de una réplica por bloques es un estimador de razón (módulo 4)",
     "estimador de razón"),
    ("dice que el recorrido sin un departamento es sensibilidad, no incertidumbre (módulo 4)",
     "mide la sensibilidad a un solo departamento"),
    ("dice que con 33 bloques el tamaño efectivo se conoce en orden de magnitud (módulo 4)",
     "se conoce solo en orden de magnitud"),
    ("condiciona a la homogeneidad que la intensidad no dependa del borde (módulo 2)",
     "si el proceso es homogéneo, su intensidad"),
    ("dice que −1/(n′ − 1) es la convención del programa (módulo 3)",
     "es la convención del programa"),
    ("dice que la z departamental mezcla efecto y potencia (módulo 7)",
     "mucha menos potencia"),
    ("nombra la prueba del módulo 6",
     "bilateral y con"),
    ("dice que la z sitúa cada I en su propia nula (módulo 7)",
     "sitúa cada i en su propia nula"),
    ("dice que entre dos correlaciones de signo opuesto lo que crece es el valor absoluto (módulo 7)",
     "lo único que crece es el valor absoluto"),
    # R2 · T2.4: lo que las tres gráficas nuevas obligan a decir. Una prueba
    # de aleatorización sin lo que su nula controla, una envolvente sin decir
    # que es puntual y cien intervalos confundidos con la cobertura son tres
    # formas de dibujar bien y enseñar mal.
    ("dice lo que la nula de la aleatorización no controla (módulo 1)",
     "la nula no sabe cuánta gente vivía en cada tramo"),
    ("da el valor p de la aleatorización como cota y no como cero (módulo 1)",
     "se da como cota y no como cero"),
    ("dice que la envolvente del correlograma es puntual (módulo 3)",
     "cada banda tiene su propio"),
    ("dice que la última banda no se distingue de un reparto al azar (módulo 3)",
     "ya no se distingue de un reparto al azar"),
    ("comenta la banda negativa del correlograma (módulo 3)",
     "se parecen menos que dos tomadas al azar"),
    ("distingue el recuento de los cien intervalos de la cobertura (módulo 4)",
     "no es la cobertura del módulo"),
    ("dice que lo que falla en los cien intervalos es el error estándar (módulo 4)",
     "lo que estaba mal era el largo del segmento"),
    # R2 · T2.4, segunda ronda.
    ("dice que la parte de calle depende del marco del plano (módulo 1)",
     "depende de hasta dónde llega el plano"),
    ("dice que el rechazo no cambia con el marco (módulo 1)",
     "lo que no cambia con el marco es el rechazo"),
    ("dice que hay parejas más allá del eje del correlograma (módulo 3)",
     "y la red no"),
    ("dice que con bandas cortas positivas tiene que haber bandas negativas (módulo 3)",
     "tiene que haber bandas negativas"),
    ("distingue el cociente de semianchos del factor del recuadro (módulo 4)",
     "ese cociente no es el"),
    ("dice que la binomial es la fórmula de la misma nula que se simula (módulo 1)",
     "es la fórmula de esta misma"),
    ("dice que la fórmula de n_eff con la correlación media es una identidad",
     "es una identidad"),
    ("dice que hay un techo en la información",
     "hay un techo"),
    ("y que el techo depende de cómo se añadan los datos",
     "depende de cómo se añadan los datos"),
    ("dice que la correlación media no se puede medir directamente sobre el mapa",
     "para cualquier conjunto de datos"),
    ("advierte de que la fórmula de n_eff vale para la media y no para otro estimador",
     "es para la media, y solo para ella"),
    ("dice que agregar NO siempre infla la correlación",
     "no siempre"),
    ("dice que el cambio de signo del estrato no aguanta el barrido",
     "no que le dé la vuelta"),
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
    # R3 · T3.3: lo que sustituye a las frases retiradas.
    ("dice que la estacionariedad hace falta pero no basta (módulo 6)",
     "y hace falta, pero no basta"),
    ("dice que al promediar sube el valor absoluto de la correlación (módulo 7)",
     "así que sube su valor absoluto"),
    # R3 · T3.3, ronda 2 (🔴 de la verificación): la ergodicidad es del proceso.
    # El del módulo 6 ES ergódico; el contraejemplo de que la estacionariedad no
    # basta es Z(s) = Y; y la región grande es una condición práctica, no parte
    # de la definición.
    ("dice que el proceso del módulo 6 es ergódico (definición)",
     "en cambio, es ergódico"),
    ("da el contraejemplo estacionario que no es ergódico (módulo 6)",
     "que no se acerca a la del proceso por mucho que crezca la región"),
    ("dice que la región grande no es parte de la definición de ergodicidad (módulo 6)",
     "no parte de la definición"),
    ("cierra el panel diciendo que el proceso es ergódico (módulo 6)",
     "el proceso es estacionario y ergódico"),
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

# Lo que el capítulo NO puede volver a decir. Hasta la ronda R1 el módulo 5
# enseñaba cuatro cosas falsas, y una reescritura descuidada las devuelve
# con todas las cifras en regla, porque ninguna es una cifra:
#
#   · que n_eff = n/(1+(n-1)rho) «supone equicorrelación». Con rho la
#     correlación MEDIA entre pares es una identidad de Var(Zbar);
#   · que por eso solo sirve de «orden de magnitud»;
#   · que hay un rho «medido» o «estimado» sobre el mapa: el promedio
#     centrado de todos los pares vale -1/(n-1) con cualquier dato;
#   · el título «De dónde sale ese 5 %», con la cifra escrita a mano.
#
# Se busca en el DOCUMENTO ENTERO y no solo en la prosa: la mitad de esas
# frases vivía en el JavaScript —la leyenda y la lectura del simulador— y
# en el JSON incrustado, que la extracción de prosa descarta. El patrón del
# rho tolera lo que el marcado mete entre la letra y el adjetivo: el cierre
# de la fórmula, espacios y una etiqueta.
#
# Dos acotaciones, las dos a la vista:
#
#   · «orden de magnitud» se busca SOLO en el módulo 5. Fuera de él es una
#     expresión corriente —un comentario de un bloque de código la usa con
#     razón— y «órdenes de magnitud», en plural, es otra frase.
#   · La LECTURA del ejercicio 3 estuvo exenta mientras su solución usó
#     el método que R1 retiró del módulo (un correlograma por bandas y «la
#     fórmula de equicorrelación»). T1.2 rehízo el ejercicio sobre el
#     remuestreo por bloques y la exención se quitó: estas guardas leen ya
#     el documento entero, la lectura y el JSON incrustado incluidos.

PROHIBIDAS = [
    ("no dice que la fórmula de n_eff supone equicorrelación", "todo",
     r"equicorrelaci"),
    ("no rebaja la fórmula de n_eff a un orden de magnitud", "modulo5",
     r"orden de magnitud"),
    ("no publica un rho «medido» o «estimado» sobre el mapa", "todo",
     r"(?:rho|ρ)(?:\}|\\\)|\s|</?[a-z]+>)*(?:medid|estimad)"),
    ("no vuelve el título «De dónde sale ese…»", "todo",
     r"de dónde sale ese\b"),
    # --- R1 · T1.4: seis frases falsas más, de los módulos 2, 6 y 10 y de
    # la pregunta del gráfico. Como las de arriba, ninguna es una cifra:
    #   · el perímetro urbano SÍ es una ventana (una subregión de una región
    #     exhaustiva es exhaustiva); el factor entre las dos intensidades
    #     mide la inhomogeneidad, no «ventana frente a recorte»;
    #   · el movimiento browniano tiene varianza finita en cada punto: lo
    #     que no es, es estacionario de segundo orden;
    #   · con probabilidades de inclusión desiguales la media muestral está
    #     sesgada, y la incorrelación de dos extracciones es del diseño;
    #   · las celdas de Thiessen de puntos uniformes NO son parecidas;
    #   · «la media está cada vez peor estimada» es CIERTO en precisión, así
    #     que no puede ser un distractor, y «sigue bien estimada» confunde
    #     insesgadez con precisión.
    # --- R2 · T2.3 (ronda 2): la respuesta de los puntuales decía que la
    # ventana «se fija antes de mirar, y por eso» cambiarla cambia λ̂. Lo
    # segundo no se sigue de lo primero: λ̂ cambia porque es n/|W|. Y el
    # rectángulo que ciñe a los puntos se rotulaba «ventana», cuando lo eligen
    # los datos.
    ("no atribuye el cambio de λ̂ a que la ventana se fije antes de mirar (módulo 2)", "todo",
     r"se fija antes de mirar, y por eso"),
    ("no rotula como ventana el rectángulo que ciñe a los puntos (módulo 2)", "todo",
     r"'ventana: ' \+ pinos1_nombre\[pinosventana\]|<span>ventana: el rectángulo"),
    ("no llama «recorte» al perímetro urbano (módulo 2)", "todo",
     r"no es una ventana sino un recorte|la otra la de un recorte"),
    ("no dice que el browniano no tiene varianza finita (módulo 6)", "todo",
     r"el movimiento browniano lo es|intrínseco sin tener varianza finita"),
    ("no dice que la media muestral estima la poblacional «y punto» (módulo 10)", "todo",
     r"media poblacional, y punto"),
    ("no dice sin más que dos observaciones vecinas no están correlacionadas (módulo 10)", "todo",
     r"vecinas (?:<em>)?no(?:</em>)? están correlacionadas"),
    ("no dice que las áreas de Thiessen serían parecidas con igual probabilidad (módulo 10)",
     "todo", r"áreas serían parecidas"),
    # El IC de la mediana de la referencia es de la mediana de la
    # DISTRIBUCIÓN, no un intervalo donde caería la de otra semilla; y
    # ponderar «por la inversa» sin más describe la media ponderada (Hájek),
    # que solo es aproximadamente insesgada.
    ("no presenta el IC de la mediana como lo que movería otra semilla (módulo 10)", "todo",
     r"otra semilla (?:la|esa mediana se) mover"),
    ("no describe Horvitz–Thompson como una media ponderada (módulo 10)", "todo",
     r"basta ponderar cada observación por la inversa"),
    # La banda del variograma no se abre por falta de pares: en esta rejilla
    # los pares CRECEN con el rezago (preparcial 1; aquí, por si vuelve).
    ("no atribuye la dispersión del variograma a que haya menos pares", "todo",
     r"menos pares que promediar"),
    ("no usa como distractor una frase cierta, ni llama «bien estimada» a una media imprecisa",
     "todo", r"la media está cada vez peor estimada|la media sigue bien estimada"),
    # --- R1 · T1.6: las imprecisiones de los módulos 1, 2, 3, 4, 6, 7 y 10 y
    # de la diagnóstica. Cada una es una frase que decía de más o de menos:
    #   · que el 90 % de los ataques precediera a la retirada del mango no
    #     «dice otra cosa» ni «contradice» nada: no permite atribuirle el
    #     final del brote, que es menos;
    #   · λ es del proceso y n/|W| su estimador; en un patrón puntual no hay
    #     Z(s), y en el geoestadístico lo aleatorio (marco del curso) es el
    #     campo, no «dónde lo miramos»;
    #   · las manchas SÍ pesan en R (suben la densidad local): no «apenas
    #     pesa», ni R es «ciego» a ellas;
    #   · lo que no vale cero bajo la nula es E[I], y por el centrado;
    #   · el corchete vale 1 cuando la SUMA de las correlaciones se anula;
    #   · las réplicas por bloques no están centradas en la media muestral,
    #     y el remuestreo por departamentos no es «el honesto» sin más;
    #   · «declararía significativa» sin nombrar la prueba; el porcentaje de
    #     caída entre dos I con pesos y n distintos no es una magnitud;
    #   · el error de la validación por bloques no es «el real»;
    #   · con correlación NEGATIVA el error estándar clásico sale grande.
    # Y dos que no eran de contenido: la crónica de producción del módulo 7
    # y una línea de código muerto en el bloque del correlograma.
    ("no dice que el dato «dice otra cosa» o «contradice» la retirada del mango (módulo 1)",
     "todo", r"el dato dice otra cosa|el dato la contradice"),
    ("no escribe λ = n/|W| ni llama aleatorio al «conjunto de índices» (módulo 2)", "todo",
     r"\$\$\\lambda = \\frac\{n\}|propio conjunto de índices|en los tres casos hay un proceso"),
    ("no dice que en el tipo geoestadístico lo aleatorio es dónde se mira (módulo 2)", "todo",
     r"dónde lo miramos|dónde miramos"),
    ("no dice que la agregación «apenas pesa» en R ni que R es ciego a ella (módulo 3)", "todo",
     r"apenas\s+pesa|ciego a todo lo que pase"),
    ("no dice que I «no vale cero» bajo la nula ni lo explica por la diagonal (módulo 3)", "todo",
     r"no vale cero bajo|consigo misma excluida"),
    ("no deja código muerto en el bloque del correlograma (módulo 3)", "todo",
     r"as\.numeric\(st_distance"),
    ("no dice que el corchete vale 1 solo si todas las correlaciones se anulan (módulo 4)", "todo",
     r"solo si todas las correlaciones"),
    ("no dice que los dos remuestreos están centrados en el mismo sitio (módulo 4 y ejercicio 2)",
     "todo", r"centrados en el mismo sitio|tienen que dar la misma media"),
    ("no llama «honesto» sin más al intervalo o al error estándar por bloques", "todo",
     r"intervalo honesto|error estándar honesto"),
    ("no dice «declararía significativa» sin nombrar la prueba (módulo 6)", "todo",
     r"declararía significativa"),
    ("no presenta la caída de la I como una magnitud (módulo 7)", "todo",
     r"una caída del\s*<strong>"),
    ("no cuenta la crónica de producción del módulo 7", "todo",
     r"iba a publicar|es una cicatriz|cociente entre dos ceros"),
    ("no llama «real» al error de la validación por bloques (módulo 10)", "todo",
     r"el error real|rmse real"),
    ("no afirma sin signo que con datos correlacionados el e.e. clásico sale pequeño", "todo",
     r"datos espaciales correlacionados"),
    # --- R1 · T1.6, segunda ronda: lo que la primera escribió de más.
    #   · el recorrido de «un departamento menos» NO mide la incertidumbre
    #     (los cálculos comparten casi todos sus bloques): es sensibilidad;
    #   · las z de dos I con n distinto tampoco se comparan sin más: la z
    #     crece con n, y mezcla efecto y potencia;
    #   · −1/(n′ − 1) es lo que imprime moran.test, no la esperanza por
    #     permutación de la I que publica, que es −n′/(n(n − 1));
    #   · que la intensidad no dependa del borde solo vale si el proceso es
    #     homogéneo;
    #   · el intervalo se centra en la media muestral porque es el
    #     estimador, no «por» el desvío de las réplicas;
    #   · «varía N veces más» por «su desviación estándar es N veces».
    ("no dice que quitar un departamento «mide» la incertidumbre (módulo 5)", "todo",
     r"la mide quitando un departamento"),
    ("no dice que las z de las dos I «sí se pueden comparar» (módulo 7)", "todo",
     r"eso sí se puede comparar"),
    ("no dice que la I «varía N veces más» (módulo 7)", "todo",
     r"varía [\d.]+ veces más"),
    ("no presenta −1/(n′ − 1) como la referencia de la banda (módulo 3)", "todo",
     r"la referencia de esa banda es"),
    ("no dice sin condición que la intensidad no se entera del borde (módulo 2)", "todo",
     r"la intensidad del proceso no se entera"),
    ("no hace del desvío «la razón» de que el intervalo se centre en la media (módulo 4)", "todo",
     r"es la\s+razón de que el intervalo se centre"),
    ("no llama «honesto» al intervalo en el enunciado del ejercicio 2", "todo",
     r"y el honesto no"),
    # --- R2 · T2.4. Dos frases que las gráficas nuevas hacen fáciles de
    # escribir y que serían falsas:
    #   · un valor p «de cero». Con B recolocaciones y ninguna que alcance al
    #     dato, lo que se sabe es p < 1/(B + 1), no p = 0;
    #   · una envolvente «simultánea» o «global». La del correlograma se
    #     calcula banda a banda: su 95 % vale para cada banda, no para las
    #     siete a la vez.
    ("no da un valor p de cero en la prueba de aleatorización (módulo 1)", "todo",
     r"valor p (?:es|vale|de|igual a) (?:0|cero)\b|valor p nulo|p-valor (?:es|vale|de) (?:0|cero)\b"),
    ("no llama simultánea ni global a la envolvente del correlograma (módulo 3)", "todo",
     r"(?:envolvente|franja) (?:simultánea|global)"),
    # --- R2 · T2.4, segunda ronda: cinco frases de la primera que el
    # verificador tumbó.
    #   · la calle explica «una parte pequeña»: cuánta, depende del marco del
    #     plano (de 3.0 a 7.2 veces);
    #   · la conclusión de la prueba «es exacta»: depende de la nula;
    #   · la banda negativa «en parte es obligada»: que haya bandas negativas
    #     es obligado del todo; lo que decide el dato es cuáles;
    #   · p < 1/(B + 1): el p de Monte Carlo es (0 + 1)/(B + 1), así que es ≤;
    #   · la línea de E[I] es «el centro» de la franja: es su media, y la
    #     franja es asimétrica.
    ("no dice que la calle explica «una parte pequeña» de la concentración (módulo 1)", "todo",
     r"es una parte pequeña"),
    ("no llama «exacta» a la conclusión de la prueba de aleatorización (módulo 1)", "todo",
     r"una cosa, y es exacta"),
    ("no dice que la banda negativa es obligada solo «en parte» (módulo 3)", "todo",
     r"en parte es obligado"),
    ("no escribe el valor p de Monte Carlo con desigualdad estricta (módulo 1)", "todo",
     r"p (?:&lt;|<) 1/\(b \+ 1\)|'valor p', '< '"),
    ("no llama «centro» de la franja a la línea de E[I] (módulo 3)", "todo",
     r"es su centro, e\[i\]"),
    # --- R2 · T2.4, tercera ronda. La binomial no «descansa en la
    # independencia» más que la simulación: es la fórmula de la misma nula,
    # que también recoloca cada muerte por separado. Lo que la hace
    # impublicable es la precisión que aparenta, no un supuesto que la
    # simulación no tenga.
    ("no dice que la binomial descansa en una independencia que la simulación no supone (módulo 1)",
     "todo", r"descansa entera en que las muertes"),
    # --- R2 · T2.2: lo que las gráficas y los mapas dejaron de decir.
    #   · el mapa del Mosa dibuja el río: su descripción ya no puede decir
    #     que no;
    #   · el campo del módulo 4 va en la retícula de la simulación, y phi es
    #     el alcance, no el rango (en un modelo exponencial el rango práctico
    #     es unas tres veces phi);
    #   · los trece pares reales no están «al lado» de la simulación: se
    #     llega a ellos con un botón; y no se dibuja su cambio relativo, que
    #     cerca de 0 no significa nada;
    #   · la cobertura y los errores estándar no comparten lienzo con dos
    #     ejes verticales.
    ("no dice que el mapa del Mosa no dibuja el río (módulo 2)", "todo",
     r"el mapa no lo dibuja"),
    ("no vuelve la retícula de 28 por 28 al campo del módulo 4", "todo",
     r"28 por 28 celdas|28\s?×\s?28"),
    ("no llama «rango» al alcance del campo (módulo 4)", "todo",
     r"campo gaussiano, rango"),
    ("no dice que los pares reales están «al lado» de la simulación (módulo 7)", "todo",
     r"y al lado, los"),
    ("no dibuja el cambio relativo de una correlación (módulo 7)", "todo",
     r"cambio de la correlación al agregar \(%\)|cambio al agregar \(%\)"),
    ("no vuelve el doble eje al gráfico del módulo 4", "todo",
     r"yaxisid:\s*'y2'"),
    # --- R2 · T2.2, segunda ronda. «8 suben y 5 bajan» cuenta el valor
    # absoluto de la correlación, y el gráfico de pesas tiene un eje con
    # signo: una correlación negativa que «baja» se ve moverse a la derecha.
    # Los pares se alejan del cero o se acercan a él.
    ("no cuenta los pares reales como «suben» y «bajan» (módulo 7)", "todo",
     r"suben\b.{0,60}\bbajan\b|agregar no siempre sube la correlación"),
    # --- R3 · T3.2: la notación (D6). Las formas retiradas que eran erróneas,
    # no solo de estilo:
    #   · la matriz de pesos con la misma W que la ventana;
    #   · ρ en el glosario como solo el coeficiente del SAR, cuando en este
    #     capítulo es siempre una correlación;
    #   · «el I de Moran», que convivía con «la I»;
    #   · los «rezagos» del variograma, que chocaban con el rezago espacial
    #     W y del glosario: son clases de distancia;
    #   · la distancia al vecino llamada D, la letra del dominio, y el conteo
    #     N(A), con la A de los datos de área;
    #   · la D del dominio convertida en la ventana a mitad del párrafo;
    #   · el correlograma de Moran leído como la caída de una correlación;
    #   · la R de la matriz de correlaciones, que es la letra de Clark-Evans
    #     y no estaba definida.
    ("no escribe la matriz de pesos sin negrita (D6)", "todo",
     r"matriz de pesos \\\(w\\\)"),
    ("no le da a ρ en el glosario solo el sentido del SAR (D6)", "todo",
     r'"nombre": "coeficiente de retardo espacial \(sar\)'),
    ("no escribe «el I de Moran» (D6)", "todo",
     r"\b(?:el|del|al|un|este|ese|aquel|otro|mismo|primer|último) i\b(?![-_^=(\w]|\.\w)"),
    ("no llama «rezago» a una clase de distancia del variograma (módulo 6)", "todo",
     r"en el rezago (?:\d|\\\(k)|rezago \(pasos de retícula\)|rezagos fuera de la banda|en cada rezago|"
     r"peor rezago|los ocho rezagos"),
    ("no llama D a la distancia al vecino ni N(A) al conteo (módulo 3)", "todo",
     r"p\(d (?:>|&gt;) r\)|e\[d\] =|n\(a\) \\sim"),
    ("no convierte el dominio D en la ventana (módulo 2)", "todo",
     r"dentro de \\\(d\\\) —que aquí es fijo"),
    ("no lee el correlograma de Moran como la caída de una correlación (módulo 5)", "todo",
     r"distancia, como en el correlograma del módulo 3"),
    ("no escribe la matriz de correlaciones con la R de Clark-Evans (módulo 4)", "todo",
     r"\^\\top r\\,"),
    # --- R3 · T3.3: dos frases falsas que los paneles nuevos sustituyen.
    #   · con una realización la estacionariedad NO es «la única salida» que
    #     basta: es necesaria, y hace falta además ergodicidad (C1-22);
    #   · la correlación no es «el cociente entre lo que sobrevive y lo que
    #     había»: es covarianza entre desviaciones típicas, y lo que sube al
    #     promediar es |r| (C1-28).
    ("no dice que con una realización basta suponer estacionariedad (módulo 6)", "todo",
     r"solo hay una salida:\s*suponer"),
    ("no describe la correlación como lo que sobrevive entre lo que había (módulo 7)", "todo",
     r"cociente entre lo que sobrevive"),
    # --- R3 · T3.3, ronda 2: la ergodicidad es una propiedad del proceso. Ni la
    # región grande va dentro de su definición, ni el proceso del módulo 6 —con
    # correlación que decae, ergódico— se presenta como el que no lo es.
    ("no mete la región grande en la definición de ergodicidad (módulo 6 y quiz)", "todo",
     r"ergodicidad[^.]{0,60}\b(?:pide|es que)\b[^.]{0,80}región (?:sea )?grande"),
    ("no presenta el proceso del módulo 6 como no ergódico", "todo",
     r"no son lo mismo: el proceso de arriba|(?:proceso de arriba|este proceso|el proceso del módulo)"
     r" no es ergódico|no ha tenido sitio para converger"),
]

# Lo que el DOCUMENTO ENTERO tiene que decir, también fuera de la prosa: la
# retroalimentación del cuestionario vive en el JavaScript, que la extracción de
# prosa descarta (R3 · T3.3, ronda 2).
AFIRMACIONES_DOC = [
    ("la retroalimentación del quiz dice que la estacionariedad no basta, por dos razones (módulo 6)",
     "hace falta, pero no basta, y por dos razones distintas"),
    ("la retroalimentación del quiz separa la región grande de la ergodicidad (módulo 6)",
     "la otra es del mapa"),
]


def prohibidas(a: Auditor) -> None:
    print("\n=== Lo que el capítulo no puede volver a decir ============")
    doc = a.doc.lower()
    ini = doc.find('<template id="module-5">')
    fin = doc.find("</template>", ini)
    a.exige(ini >= 0 and fin > ini, "el módulo 5 se puede aislar para leerlo")
    ambitos = {"todo": doc, "modulo5": doc[ini:fin] if ini >= 0 else ""}
    for que, ambito, patron in PROHIBIDAS:
        m = re.search(patron, ambitos[ambito])
        a.exige(m is None, que,
                "" if m is None else "aparece: «"
                + ambitos[ambito][max(0, m.start() - 30):m.end() + 20].replace("\n", " ") + "»")
    for que, clave in AFIRMACIONES_DOC:
        a.exige(clave in doc, que)


# El tope de peso de ESTE capítulo. La aritmética, en el encabezado.
TOPE_CAP1_KB = 1000.0

ORDENES = [r"\frac", r"\lambda", r"\rho", r"\gamma", r"\sum", r"\text",
           r"\operatorname", r"\mathbb", r"\bar", r"\lVert"]


def main() -> int:
    a = Auditor(
        capitulo="capitulo-1-datos-espaciales.html",
        var_entorno="CAP1_HTML",
        jsons=["cap1_datos.json", "cap1_soluciones.json"],
        estructurales=ESTRUCTURALES,
        # 135 KB desde R2 · T2.3, el mismo tope y por la misma cuenta que
        # `PRESUPUESTO_GEO_KB` del ensamblador: los tres bordes de Bogotá y el
        # borde de cada sede dejan la geometría incrustada en 127.7 KB, medida
        # aquí registro a registro.
        presupuesto_geomapa_kb=135.0,
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
    prohibidas(a)
    a.accesibilidad()
    a.geomapas()
    a.decimales_con_punto()
    a.formulas_escapadas()
    a.codificacion()
    a.enlaces()
    a.coherencia(CADENAS, ORDENES)
    a.peso(TOPE_CAP1_KB)
    return a.cierre()


if __name__ == "__main__":
    sys.exit(main())
