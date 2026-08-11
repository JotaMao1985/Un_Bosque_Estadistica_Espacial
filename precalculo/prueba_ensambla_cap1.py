#!/usr/bin/env python3
"""
prueba_ensambla_cap1.py — le rompe las guardas de compilación al ensamblador
y exige que las cace

Material de Estadística Espacial 2026-II (20929). T1.3.n.

POR QUÉ EXISTE. `ensambla_cap1.py` tiene **41 guardas de compilación** que no
comprueba nadie. Nacieron de defectos reales —el mapa desplazado de T1.2, la
serie recortada de T1.4, el variograma ajeno de T1.3— y cada tarea las probó
con un guion de sesión que se perdió al cerrarla. Un `MAL` que nadie ha visto
salir puede estar bien escrito o puede ser incapaz de dispararse, y desde
fuera se ven igual: es la lección de T0.5, y este proyecto ya la pagó dos
veces.

LO QUE LAS HACE DISTINTAS DEL AUDITOR. `audita_cap1.py` mira **archivos**;
estas guardas miran **el hueco entre archivos**, y entre el dato y el
cableado que lo dibuja. Por eso no bastan las tres familias del arnés del
auditor: hay que poder envenenar tres superficies distintas.

  · **los JSON** — cuando la guarda vigila el dato o la coherencia entre dos
    archivos que R escribe por separado;
  · **el propio ensamblador**, parcheado EN COPIA — cuando vigila sus propios
    literales (cuántos módulos, los tipos de pregunta del quiz, el tope del
    deslizador). Y es el modelo de amenaza correcto: esas guardas existen
    justo para el día en que alguien edite el ensamblador.
  · **la plantilla**, también en copia — cuando la guarda cuenta un ancla
    suya. Lo que sigue explica por qué esa vía existe y las otras de la
    plantilla no.

LA PLANTILLA SE ENVENENA, PERO SOLO POR UN LADO. Esta cabecera decía lo
contrario —«no es alcanzable», sin matiz— hasta que T2.2b entró justamente por
ahí. La distinción es entre lo que la guarda cuenta y CUÁNDO lo cuenta:

  · **Sus ANCLAS sí son alcanzables.** Las guardas de `reemplaza_region` y
    `sustituye` cuentan el ancla en el documento EN CURSO, antes de haber
    sustituido nada, así que un ancla duplicada en la plantilla —un
    `const courseData = {` de más, un segundo registro de
    `GEOMAPAS['demo-mapa']`— llega entera y para el ensamblado en seco. Dos de
    las seis inyecciones de T2.2b entran por esta puerta.
  · **Su CONTENIDO sustituido no lo es.** Se midió. El ensamblador sustituye
    los cinco módulos de demostración de la plantilla por los doce del
    capítulo, así que ni sus `<template>` ni sus siete lienzos llegan al
    marcado que las guardas cuentan: quitarle un `</template>` o un
    `aria-label` deja el ensamblado *limpio*. Ése sigue siendo un hueco de las
    guardas, no del arnés, y conviene tenerlo presente en T3.1 y T4.1, que
    **sí** tocan la plantilla y la retropropagan a los tres capítulos. Quien
    quiera cerrarlo tendrá que añadir una guarda que mire la plantilla ANTES
    de sustituirla; el día que exista, este arnés la inventariará solo.

NADA DE ESTO TOCA LO PUBLICADO. Las cinco variables de entorno de
`ensambla_cap1.py` —`CAP1_DATOS`, `CAP1_MAPAS`, `CAP1_SOLUCIONES`,
`CAP1_PLANTILLA` y `CAP1_DESTINO`— redirigen entradas y salida a un
directorio temporal. Importa que la SALIDA también se redirija: el
ensamblador escribe el HTML **antes** de correr sus guardas, así que un arnés
que solo redirigiera la entrada dejaría el capítulo publicado construido con
datos rotos en cada inyección. Al final se verifica byte a byte.

LAS DOS REGLAS DEL ARNÉS, heredadas de `prueba_auditor_cap1.py`:

  1. **Cada tanda empieza y acaba con un CONTROL sin inyectar nada.** Si el
     ensamblador no sale limpio sobre el original, cualquier «acierto»
     posterior es falso.
  2. **«N de N» no basta.** Se cuenta también **cuántas guardas se han visto
     disparar**, y se imprime la lista de las que no. Una guarda que nunca ha
     fallado puede estar bien escrita o puede ser inalcanzable, y desde fuera
     se ven igual.

Y dos más, propias, que costaron sendos errores míos el día que se escribió:

  3. **Una inyección que no cambia nada no es una inyección.** Toda sustitución
     comprueba que de verdad modificó el archivo y, si no, se informa como
     `INERTE` —avería DEL ARNÉS— y no como guarda que se coló. Sin esto, una
     guarda intacta y un literal que cambió de sitio se ven exactamente igual.
     El tipo `falta`, que inyecta AUSENCIA, hace la misma comprobación del
     revés: no «¿cambió el archivo?» sino «¿de verdad no está?».

  4. **La cobertura se MIDE, no se deduce del mensaje.** La primera versión
     emparejaba el texto del `MAL` con el trozo literal más largo de cada
     `problemas.append`, y dijo «sin ver disparar» de una guarda que acababa de
     dispararse: la inyección que la prueba reescribe el marcador que su
     mensaje nombra. Ahora se traza la ejecución con `sys.settrace` y cada
     guarda se identifica por su **ordinal** —no por su línea, que una
     sustitución de texto desplaza en la copia—. Un arnés cuya cobertura se
     equivoca es peor que uno sin cobertura: invita a añadir inyecciones que
     sobran y a dar por cubierto lo que no lo está.

Uso:  python3 precalculo/prueba_ensambla_cap1.py
Devuelve 1 si algún defecto se cuela o si alguna inyección resulta inerte.
"""
from __future__ import annotations

import ast
import json
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile

RAIZ = pathlib.Path(__file__).resolve().parent.parent
PRECALCULO = RAIZ / "precalculo"
SALIDAS = PRECALCULO / "salidas"
ENSAMBLADOR = PRECALCULO / "ensambla_cap1.py"
PLANTILLA = RAIZ / "plantilla" / "plantilla-capitulo.html"
PUBLICADO = RAIZ / "Htmls_Espacial" / "capitulo-1-datos-espaciales.html"

# superficie -> (variable de entorno, archivo de origen)
SUPERFICIES = {
    "datos":       ("CAP1_DATOS", SALIDAS / "cap1_datos.json"),
    "mapas":       ("CAP1_MAPAS", SALIDAS / "cap1_mapas.json"),
    "soluciones":  ("CAP1_SOLUCIONES", SALIDAS / "cap1_soluciones.json"),
    # Se copia, se redirige y SÍ se envenena, pero solo por sus anclas: lo
    # que el ensamblador sustituye no llega al marcado. Ver la cabecera.
    "plantilla":   ("CAP1_PLANTILLA", PLANTILLA),
    "ensamblador": (None, ENSAMBLADOR),      # se parchea la copia y se ejecuta
}


# =====================================================================
# El inventario de guardas, leído del código y no de una lista a mano
#
# A mano se queda desactualizado en la primera tarea que añada una guarda
# —y esa es justo la tarea que más necesita saber si la ha probado—. Con
# `ast` la cuenta la lleva el propio archivo.
# =====================================================================
def inventario(ruta: pathlib.Path = ENSAMBLADOR) -> list[tuple[int, str]]:
    arbol = ast.parse(ruta.read_text(encoding="utf-8"))
    guardas = []

    def firma_de(arg) -> str:
        # El trozo literal más largo del mensaje: lo único que sobrevive a
        # las llaves de la f-string y sirve para reconocerlo por pantalla.
        lits = [n.value for n in ast.walk(arg)
                if isinstance(n, ast.Constant) and isinstance(n.value, str)]
        return max(lits, key=len).strip() if lits else ""

    for nodo in ast.walk(arbol):
        if not (isinstance(nodo, ast.Call) and nodo.args):
            continue
        f = nodo.func
        acumula = (isinstance(f, ast.Attribute) and f.attr == "append"
                   and isinstance(f.value, ast.Name) and f.value.id == "problemas")
        # Los PAROS DUROS también son guardas, y hasta T2.2 no se contaban.
        # El ensamblador para con `sys.exit("PARADO: …")` cuando no puede
        # seguir —una ancla que no aparece, la fila de phi = 4 que falta—, y
        # esas siete quedaban fuera del inventario: ni se medía su cobertura
        # ni una nueva aparecía sola en «sin ver disparar», que es
        # justamente lo que el criterio transversal de T1.3.n promete. Se
        # exige que el argumento sea texto para dejar fuera el
        # `sys.exit(main())` del final, que no es una guarda.
        para = (isinstance(f, ast.Attribute) and f.attr == "exit"
                and isinstance(f.value, ast.Name) and f.value.id == "sys"
                and isinstance(nodo.args[0], (ast.Constant, ast.JoinedStr))
                and firma_de(nodo.args[0]))
        if acumula or para:
            guardas.append((nodo.lineno, firma_de(nodo.args[0])))
    return sorted(guardas)


# =====================================================================
# Los defectos
#
# Tres formas. Dos vienen del arnés del auditor —mutar el objeto ya parseado
# (los tres JSON) o sustituir texto (el ensamblador, la plantilla)— y las dos
# escriben un archivo ROTO. La tercera, `falta`, hace lo contrario: deja la
# ruta apuntando a un archivo que NO EXISTE, que es la única manera de llegar
# a la guarda que se dispara antes de que haya nada que leer. (T2.2b)
# =====================================================================
def defectos() -> list[tuple[str, str, str, object]]:
    """(nombre, superficie, tipo, acción). tipo ∈ {'obj', 'txt', 'falta'}."""
    D: list[tuple[str, str, str, object]] = []

    def obj(nombre, superficie, f):
        D.append((nombre, superficie, "obj", f))

    def falta(nombre, superficie):
        """La superficie se redirige a un temporal que no se crea.

        No lleva acción: lo que inyecta es la AUSENCIA del archivo, y quien
        comprueba que de verdad falta es el bucle de `main()`.
        """
        D.append((nombre, superficie, "falta", None))

    def txt(nombre, superficie, *pares, veces=1):
        """`pares` son (viejo, nuevo) sueltos o varios seguidos.

        `veces=0` sustituye TODAS las apariciones: hace falta para las guardas
        que cuentan, donde cambiar una sola no mueve el contador. Y varios
        pares hacen falta cuando el mismo marcador vive escapado y crudo en
        sitios distintos del ensamblador.
        """
        it = iter(pares)
        D.append((nombre, superficie, "txt",
                  [(v, n, veces) for v, n in zip(it, it)]))

    # --- Estructura del documento (superficie: el ensamblador) ----------
    txt("los doce módulos dejan de ser doce", "ensamblador",
        '<template id="module-{num}">', '<template id="modulos-{num}">')
    txt("los ejercicios guiados dejan de ser cuatro", "ensamblador",
        '<div class="ejercicio-guiado">', '<div class="ejercicio-guiada">')
    txt("las dos autoevaluaciones se quedan en una", "ensamblador",
        'data-quiz="cap1-diagnostica"', 'data-quiz="cap1"')
    txt("un lienzo se queda sin aria-label", "ensamblador",
        'aria-label="Variograma de una realización frente al teórico, con la banda '
        'del 5 al 95 por ciento sobre mil realizaciones" role="img"', 'role="img"')
    txt("una plantilla abre y no cierra", "ensamblador",
        "</template>\n", "\n")
    txt("un tipo de pregunta que el motor no conoce", "ensamblador",
        "tipo: 'grafico'", "tipo: 'diagrama'")
    txt("un .geomapa usado sin registrar", "ensamblador",
        'data-geomapa="cap1-realizacion"', 'data-geomapa="cap1-inventado"')
    # Cuenta apariciones, así que hay que quitarlas todas: con una menos el
    # contador sigue muy por encima del umbral y la guarda no se entera.
    # Esta hay que hacerla con cuidado, y el primer intento salió mal: el
    # marcador que la guarda cuenta es el MISMO literal que ella usa para
    # contarlo, así que un `replace` global reescribía la propia línea
    # `cifras = doc.count(...)` y el contador pasaba a contar otra cosa —97
    # en vez de 28, y verde—. Se aparta la línea de la guarda, se vacían los
    # marcadores del contenido y se devuelve la guarda intacta. Una inyección
    # que modifica la comprobación que quiere probar no prueba nada.
    txt("los bloques de código pierden sus líneas de salida esperada", "ensamblador",
        'cifras = doc.count("#&gt;") + doc.count("#>")',
        'cifras = doc.count("@@ESC@@") + doc.count("@@CRU@@")',
        "#&gt;", "#  ",
        "#>", "# ",
        '@@ESC@@', '#&gt;',
        '@@CRU@@', '#>',
        veces=0)
    txt("un espacio fino se cuela dentro de una fórmula", "ensamblador",
        "\\\\(\\\\phi = {ur['phi']}\\\\)", "\\\\(\\\\phi = 4\\u202f000\\\\)")

    # --- Módulo 5: el deslizador de rho (T1.1) --------------------------
    txt("el tope del deslizador deja de ser legible", "ensamblador",
        "const RHO_MAX = 0.3;", "const RHO_TOPE = 0.3;")
    txt("el deslizador ya no alcanza el ancla de rho = 0.1", "ensamblador",
        "const RHO_MAX = 0.3;", "const RHO_MAX = 0.05;")
    obj("un ancla de rho se mueve bajo los pies de la prosa", "datos",
        lambda o: o["n_efectivo"]["rhos"].__setitem__(1, 0.011))
    obj("el tope del deslizador deja de estar en la rejilla", "datos",
        lambda o: o["n_efectivo"]["rhos"].__setitem__(6, 0.31))
    obj("enes y rejilla del módulo 5 se desordenan", "datos",
        lambda o: o["n_efectivo"]["enes"].__setitem__(-1, 999))
    obj("el rombo de Colombia se sube por encima de la diagonal", "datos",
        lambda o: o["n_efectivo"].__setitem__("desercion_municipal", 2000.0))

    # --- Módulo 5: los dos rho del titular (T2.1) -----------------------
    obj("el rho implícito deja de reproducir el titular", "datos",
        lambda o: o["n_efectivo"]["rho_del_titular"].__setitem__("implicito", 0.02))
    obj("el rho medido supera al implícito y la prosa queda del revés", "datos",
        lambda o: o["n_efectivo"]["rho_del_titular"].__setitem__("estimado", 0.05))
    obj("el rho del titular habla de otros municipios", "datos",
        lambda o: o["n_efectivo"]["rho_del_titular"].__setitem__("n", 1113))
    obj("una banda que la prosa nombra cambia de distancia", "datos",
        lambda o: o["n_efectivo"]["rho_del_titular"]["bandas"][0].__setitem__("d2", 30))
    obj("las bandas del correlograma dejan un hueco", "datos",
        lambda o: o["n_efectivo"]["rho_del_titular"]["bandas"][2].__setitem__("d2", 120))
    obj("la correlación deja de ser negativa a media distancia", "datos",
        lambda o: o["n_efectivo"]["rho_del_titular"]["bandas"][4].__setitem__("I", 0.017394))

    # --- Módulo 4: las dos rejillas del campo gaussiano (T1.2) ----------
    obj("un campo simulado se queda sin fila de cifras", "mapas",
        lambda o: o["campos"].append(dict(o["campos"][0], phi=99.0)))
    obj("el campo y su fila dejan de traer la misma rho_vecino", "mapas",
        lambda o: o["campos"][3].__setitem__("rho_vecino", 0.4173941))

    # --- Módulo 4: el puente de phi al factor (T2.2) --------------------
    #
    # Las cifras del recuadro «De dónde sale el destrozo» salen ahora de R,
    # no del ensamblador, y su lectura del simulador estrena dos filas. Si
    # R dejara de publicar un campo, la prosa imprimiría `NaN` y los dos
    # auditores seguirían en verde: ninguno mira el cableado.
    obj("una fila del módulo 4 pierde una cifra del puente", "datos",
        lambda o: o["inferencia"]["rejilla"][2].pop("efecto_diseno"))
    obj("la inflación de varianza deja de ser el factor al cuadrado", "datos",
        lambda o: o["inferencia"]["rejilla"][5].__setitem__(
            "inflacion_varianza", 41.739417))
    obj("el efecto de diseño deja de ser n/n_eff", "datos",
        lambda o: o["inferencia"]["rejilla"][1].__setitem__(
            "efecto_diseno", 41.739417))
    obj("con phi=4 los dos cocientes se cruzan y la prosa queda del revés", "datos",
        lambda o: o["inferencia"]["rejilla"][4].__setitem__(
            "inflacion_varianza", 30.417394))
    obj("E[s^2] deja de ser menor que sigma^2 y la explicación se cae", "datos",
        lambda o: o["inferencia"]["rejilla"][4].__setitem__("s2_esperada", 1.4173941))
    obj("la varianza marginal declarada deja de ser 1", "datos",
        lambda o: o["inferencia"].__setitem__("sigma", 4.1739))
    obj("la escala de h se queda en blanco", "datos",
        lambda o: o["inferencia"].__setitem__("escala_h", "   "))
    # La fila de phi = 4 es de la que sale TODO el módulo. Sin ella el
    # ensamblador tiene que parar diciendo qué falta, no reventar con un
    # StopIteration pelado — que es el error de T1.3.i.
    obj("la rejilla se queda sin la fila de phi = 4", "datos",
        lambda o: o["inferencia"].__setitem__(
            "rejilla", [f for f in o["inferencia"]["rejilla"] if f["phi"] != 4]))

    # --- Módulo 6: mapa, curva y lectura (T1.3) -------------------------
    obj("falta el mapa de una realización", "mapas",
        lambda o: o.__setitem__("realizaciones", o["realizaciones"][:2]))
    obj("las dos listas del módulo 6 van en distinto orden", "mapas",
        lambda o: o["realizaciones"][2].__setitem__("id", 1))
    obj("el mapa de una realización no es el de su fila", "mapas",
        lambda o: o["realizaciones"][0].__setitem__("media_espacial", 0.4173941))
    obj("la sd del mapa no es la de su fila", "mapas",
        lambda o: o["realizaciones"][1].__setitem__("sd_espacial", 0.4173941))
    obj("un mapa del módulo 6 vuelve a la rejilla de 28×28", "mapas",
        lambda o: o["realizaciones"][0].__setitem__("nx", 28))
    obj("una curva del módulo 6 pierde un rezago", "datos",
        lambda o: o["realizaciones_vistas"][1].__setitem__(
            "variograma", o["realizaciones_vistas"][1]["variograma"][:7]))
    obj("una realización se sale de la banda y la prosa no se entera", "datos",
        lambda o: o["realizaciones_vistas"][1].__setitem__("lags_fuera_banda", 2))
    obj("ya no son las tres primeras del lote", "datos",
        lambda o: o["una_realizacion"]["medias_muestra"].__setitem__(0, 0.4173941))
    obj("las tres curvas se vuelven la misma", "datos",
        lambda o: [r.__setitem__("variograma",
                                 list(o["realizaciones_vistas"][0]["variograma"]))
                   for r in o["realizaciones_vistas"]])

    # --- Módulo 1: la serie del brote (T1.4) ----------------------------
    obj("las tres series del brote dejan de medir lo mismo", "datos",
        lambda o: o["snow"].__setitem__("serie_ataques", o["snow"]["serie_ataques"][:-1]))
    obj("la serie se recorta por la cola", "datos",
        lambda o: (o["snow"].__setitem__("serie_fecha", o["snow"]["serie_fecha"][:-1]),
                   o["snow"].__setitem__("serie_ataques", o["snow"]["serie_ataques"][:-1]),
                   o["snow"].__setitem__("serie_muertes", o["snow"]["serie_muertes"][:-1])))
    obj("los días con y sin fecha dejan de sumar los de la tabla", "datos",
        lambda o: o["snow"].__setitem__("n_dias_sin_fecha",
                                        o["snow"]["n_dias_sin_fecha"] + 1))
    obj("el día del mango se queda sin víspera", "datos",
        lambda o: o["snow"].__setitem__("fecha_mango", o["snow"]["serie_fecha"][0]))
    obj("los ataques anteriores al mango dejan de ser los de la serie", "datos",
        lambda o: o["snow"].__setitem__("ataques_antes_mango",
                                        o["snow"]["ataques_antes_mango"] + 5))
    obj("los ataques del día del mango no son los de la serie", "datos",
        lambda o: o["snow"].__setitem__("ataques_dia_mango",
                                        o["snow"]["ataques_dia_mango"] + 1))
    obj("antes y desde el mango dejan de sumar el total", "datos",
        lambda o: o["snow"].__setitem__("ataques_desde_mango",
                                        o["snow"]["ataques_desde_mango"] + 3))
    obj("las muertes de la serie no son las de la tabla", "datos",
        lambda o: o["snow"].__setitem__("muertes_tabla",
                                        o["snow"]["muertes_tabla"] + 2))
    obj("el porcentaje que dibuja el acumulado no es su cociente", "datos",
        lambda o: o["snow"].__setitem__("pct_ataques_antes_mango", 50.0))
    obj("el pico publicado no es el de la serie", "datos",
        lambda o: o["snow"].__setitem__("ataques_pico", o["snow"]["ataques_pico"] + 1))

    # --- Módulo 3: las tres series del correlograma (T1.4) --------------
    obj("dos series del correlograma dejan de compartir rejilla", "datos",
        lambda o: o["tobler"]["permutado"]["bandas"][0].__setitem__(
            "d2", o["tobler"]["permutado"]["bandas"][0]["d2"] + 1))
    obj("E[I] deja de ser una sola recta para las tres", "datos",
        lambda o: o["tobler"]["residuos_altitud"].__setitem__("esperado", -0.5))
    obj("la caída por altitud no es la de las dos series que compara", "datos",
        lambda o: o["tobler"].__setitem__("caida_por_altitud_pct", 12.34567))

    # --- T2.4 · el mapa del módulo 7 y el caso que señala ---------------
    #
    # El defecto que estas guardas persiguen es el más silencioso del
    # capítulo: el mapa sale igualmente bonito señalando el condado de al
    # lado, resaltando otras celdas o escribiendo los cinco números en el
    # orden equivocado. Ninguno de esos tres rompe el HTML ni deja rastro en
    # la consola, y el auditor de prosa —que mira cifras— los daría por
    # buenos porque las cifras siguen siendo las de R.
    obj("el mapa resalta un condado y el precálculo señala otro", "mapas",
        lambda o: o["agregacion"].__setitem__("resaltado", 67))
    obj("una celda resaltada del mapa no es la que publica el precálculo", "mapas",
        lambda o: o["agregacion"]["lineas_resaltadas"].__setitem__(0, 43))
    obj("la rejilla del mapa pierde rectángulos", "mapas",
        lambda o: o["agregacion"].__setitem__("n_lineas", 96))
    # La rejilla se construyó sobre el State Plane. Con el mapa en otro CRS
    # las dos capas serían de dos Carolinas del Norte distintas.
    obj("el mapa del módulo 7 se va a otra proyección", "mapas",
        lambda o: o["agregacion"].__setitem__("crs", 32617))
    # El orden. Los rótulos de las celdas se emparejan POR POSICIÓN, así que
    # invertir el reparto escribe los cinco números correctos en cinco sitios
    # equivocados — y el mapa no se queja.
    obj("el reparto y las celdas tocadas van en distinto orden", "datos",
        lambda o: o["agregacion_soporte"]["nc"]["condado_caso"].__setitem__(
            "reparto", list(reversed(
                o["agregacion_soporte"]["nc"]["condado_caso"]["reparto"]))))
    obj("una celda se queda sin su fila de reparto", "datos",
        lambda o: o["agregacion_soporte"]["nc"]["condado_caso"].__setitem__(
            "reparto", o["agregacion_soporte"]["nc"]["condado_caso"]["reparto"][:4]))
    obj("lo que aporta el condado deja de ser k por su conteo", "datos",
        lambda o: o["agregacion_soporte"]["nc"]["condado_caso"].__setitem__(
            "aporte_predicado", 176))
    obj("el exceso deja de ser lo que aporta de más", "datos",
        lambda o: o["agregacion_soporte"]["nc"]["condado_caso"].__setitem__(
            "exceso", 100))
    obj("los excesos dejan de sumar la inflación del titular", "datos",
        lambda o: o["agregacion_soporte"]["nc"]["condado_caso"].__setitem__(
            "exceso_total", 1904))
    obj("el condado del caso pasa a tocar una sola celda", "datos",
        lambda o: o["agregacion_soporte"]["nc"]["condado_caso"].__setitem__(
            "n_celdas_toca", 1))
    obj("la celda del roce deja de ser un roce", "datos",
        lambda o: o["agregacion_soporte"]["nc"]["condado_caso"].__setitem__(
            "roce_pct", 14.1739417))
    obj("el reparto deja de cubrir el condado entero", "datos",
        lambda o: o["agregacion_soporte"]["nc"]["condado_caso"].__setitem__(
            "fraccion_total_pct", 96.4173941))

    # --- El presupuesto de geometría ------------------------------------
    obj("la geometría se sale del presupuesto de 120 KB", "mapas",
        lambda o: o["nc"].__setitem__("relleno", "x" * 70_000))

    # --- Los seis paros duros (T2.2b) -----------------------------------
    #
    # El ensamblador para de dos formas. `problemas.append(…)` acumula y
    # sigue: son las guardas que miran el RESULTADO, y el informe las junta
    # todas antes de rendirse. `sys.exit("PARADO: …")` no puede seguir: son
    # las que miran el ENSAMBLADO MISMO —que el ancla exista, que la región
    # no se pase ni se quede corta, que el archivo de entrada esté— y sin
    # ellas lo que sale no es un capítulo con un defecto sino un capítulo a
    # medio construir. Ése es el fallo de T0.5: el ancla de cierre encontrada
    # 270 líneas más abajo se llevó `renderNavigation`, el archivo salió MÁS
    # GRANDE que la plantilla y el informe, en verde.
    #
    # Llevaban ahí desde que se escribieron y ninguna se había visto
    # disparar. Cuatro viven en `reemplaza_region()` y `sustituye()`, que es
    # la maquinaria que T4.1 va a mover al retropropagar el motor `.geomapa`:
    # cubrirlas antes convierte ese cambio en uno vigilado.

    # (1) y (5) ENVENENAN LA PLANTILLA, y pueden porque estas dos guardas
    # cuentan su ancla en el documento en curso, antes de sustituir nada. Es
    # la distinción que la cabecera explica.
    txt("el ancla de apertura de courseData aparece dos veces", "plantilla",
        "    const courseData = {",
        "    const courseData = {\n    const courseData = {")

    # El tope MÁXIMO: el cierre encontrado DEMASIADO LEJOS. Se aprieta el tope
    # en vez de mover el ancla de cierre —es la misma avería vista desde el
    # otro lado, y no depende de qué haya hoy en la plantilla.
    txt("la región de los doce módulos se pasa del tope", "ensamblador",
        "max_lineas=600", "max_lineas=5")

    # El tope MÍNIMO: el cierre encontrado DEMASIADO PRONTO, que es el fallo
    # de T1.2 —el `\n    };\n` que casó con el final del primer simulador de
    # demostración y dejó vivos los otros dos, con el archivo bien formado y
    # la consola limpia—. La región de `courseData` no llega a 99 líneas.
    txt("la región de courseData se queda corta", "ensamblador",
        "max_lineas=20)", "max_lineas=20, min_lineas=99)")

    # El ancla que NO aparece, la hermana de la (1) en `sustituye`. Se le
    # cambia una letra al literal que busca —«capítulo» sin tilde—, que es
    # exactamente lo que pasa el día que alguien retoca la plantilla y no el
    # ensamblador. Se parchea el ENSAMBLADOR y no la plantilla a propósito:
    # así la guarda cuenta 0, no 2, y se prueba el otro lado del `!= 1`.
    txt("el ancla del título ya no está en la plantilla", "ensamblador",
        "<title>Plantilla de capítulo — Estadística Espacial</title>",
        "<title>Plantilla de capitulo — Estadística Espacial</title>")

    txt("el mapa de demostración se registra dos veces", "plantilla",
        "    GEOMAPAS['demo-mapa'] = { fuente:",
        "    GEOMAPAS['demo-mapa'] = null;\n"
        "    GEOMAPAS['demo-mapa'] = { fuente:")

    # (6) La única que no se puede probar escribiendo un archivo roto: se
    # dispara en `_ruta()`, al arrancar, cuando la ruta que apunta una de las
    # variables de entorno no existe. Es la guarda que sostiene el convenio
    # de redirección entero —el que permite que este arnés sea de solo
    # lectura sobre el árbol de verdad—, así que probarla es probar que un
    # `CAP1_DATOS` mal escrito para en seco en vez de ensamblar en silencio
    # con los datos publicados.
    falta("el JSON de datos no está donde apunta la variable de entorno", "datos")

    return D


# =====================================================================
# Qué guarda ha disparado: MEDIDO, no deducido del mensaje
#
# La primera versión emparejaba el texto del `MAL` con el trozo literal más
# largo de cada `problemas.append`. Funcionaba hasta que una inyección tocó el
# mensaje de la propia guarda —la de las líneas `#>` reescribe el marcador que
# la guarda nombra— y el informe dijo «sin ver disparar» de una guarda que
# acababa de dispararse. Un arnés cuya cobertura se equivoca es peor que uno
# sin cobertura, porque invita a añadir inyecciones que ya sobran.
#
# Ahora se traza la EJECUCIÓN: `sys.settrace` anota qué líneas del ensamblador
# se pisan, y de ellas las que son un `problemas.append`. Se identifica cada
# guarda por su ORDINAL —la enésima del archivo— y no por su número de línea,
# porque una inyección de texto puede desplazar las líneas de la copia.
DRIVER = '''
import json, pathlib, runpy, sys
OBJETIVO, LINEAS, DESTINO = sys.argv[1], set(json.loads(sys.argv[2])), sys.argv[3]
vistas = set()
def traza(marco, evento, arg):
    if marco.f_code.co_filename != OBJETIVO:
        return None
    if evento == "line" and marco.f_lineno in LINEAS:
        vistas.add(marco.f_lineno)
    return traza
sys.argv = [OBJETIVO]
codigo = 0
sys.settrace(traza)
try:
    runpy.run_path(OBJETIVO, run_name="__main__")
except SystemExit as e:
    # `sys.exit("mensaje")` sale con codigo 1 y escribe el mensaje por
    # stderr — asi paran las guardas de ancla del ensamblador. Con un
    # `isinstance(e.code, int)` a secas se leian como 0 y el arnes cantaba
    # SE COLO de un defecto que el ensamblador habia parado en seco.
    # Encontrado en T2.2, con la primera inyeccion que llego a una de ellas.
    if e.code is None:
        codigo = 0
    elif isinstance(e.code, int):
        codigo = e.code
    else:
        print(e.code, file=sys.stderr)
        codigo = 1
finally:
    sys.settrace(None)
    pathlib.Path(DESTINO).write_text(json.dumps(sorted(vistas)))
sys.exit(codigo)
'''


def corre(tmp: pathlib.Path, guion: pathlib.Path,
          rutas: dict[str, pathlib.Path]) -> tuple[int, str, set[int]]:
    entorno = dict(os.environ)
    for superficie, ruta in rutas.items():
        var = SUPERFICIES[superficie][0]
        if var:
            entorno[var] = str(ruta)
    entorno["CAP1_DESTINO"] = str(tmp / "salida.html")
    # Los ordinales de la COPIA, que es la que se ejecuta: una sustitución de
    # texto puede haberle movido las líneas respecto del original.
    orden = {ln: i for i, (ln, _) in enumerate(inventario(guion))}
    driver = tmp / "_driver.py"
    driver.write_text(DRIVER, encoding="utf-8")
    marcas = tmp / "_marcas.json"
    marcas.unlink(missing_ok=True)
    res = subprocess.run(
        [sys.executable, str(driver), str(guion),
         json.dumps(sorted(orden)), str(marcas)],
        capture_output=True, text=True, cwd=str(RAIZ), env=entorno)
    pisadas = set()
    if marcas.exists():
        pisadas = {orden[ln] for ln in json.loads(marcas.read_text()) if ln in orden}
    return res.returncode, res.stdout + res.stderr, pisadas


def males(salida: str) -> list[str]:
    """Las líneas de diagnóstico, de las dos formas que tiene el ensamblador.

    `MAL ` es la guarda que acumula y sigue; `PARADO:` es la que no puede
    seguir y para en seco. Las dos DICEN qué pasa, que es lo que separa
    cazar de reventar (T1.3.i). Hasta T2.2 solo se reconocía la primera, y
    un paro duro se contaba como defecto colado.
    """
    return [l.strip()[5:].strip() if l.strip().startswith("MAL ") else l.strip()
            for l in salida.splitlines()
            if l.strip().startswith("MAL ") or l.strip().startswith("PARADO:")]


# =====================================================================
def main() -> int:
    for _, origen in SUPERFICIES.values():
        if not origen.exists():
            print(f"PARADO: falta {origen}")
            return 1

    guardas = inventario()
    originales = {n: o.read_bytes() for n, (_, o) in SUPERFICIES.items()}
    publicado_antes = PUBLICADO.read_bytes() if PUBLICADO.exists() else None

    tmp = pathlib.Path(tempfile.mkdtemp(prefix="prueba_ensambla_cap1_"))
    limpias = {}
    for nombre, (_, origen) in SUPERFICIES.items():
        limpias[nombre] = tmp / origen.name
        shutil.copy(origen, limpias[nombre])

    print("=" * 70)
    print("  prueba_ensambla_cap1.py — el arnés de las guardas de compilación")
    print("=" * 70)
    print(f"  {len(guardas)} guardas inventariadas en {ENSAMBLADOR.name} "
          f"(leídas del código, no de una lista)")

    # --- CONTROL DE ENTRADA -------------------------------------------
    cod, sal, _ = corre(tmp, limpias["ensamblador"], dict(limpias))
    if cod != 0:
        print("\n  PARADO: el ensamblador no sale limpio sobre el original.")
        print("  Cualquier acierto posterior sería falso.\n")
        for m in males(sal):
            print(f"    {m}")
        if not males(sal):
            print(sal[-2000:])
        return 1
    print("  OK   control de entrada · el ensamblador sale limpio sin inyectar nada\n")

    vistas: set[int] = set()   # ordinales de guarda que se han visto disparar
    cazados = inertes = colados = 0

    for nombre, superficie, tipo, accion in defectos():
        rutas = dict(limpias)
        roto = tmp / ("roto_" + SUPERFICIES[superficie][1].name)
        if tipo == "falta":
            # La inyección es la AUSENCIA: no se escribe nada, solo se
            # redirige la superficie a un temporal que no se crea.
            roto = tmp / "no_existe.json"
            # Y la comprobación de inercia, AL REVÉS que en las otras dos.
            # Allí la pregunta es «¿de verdad cambió el archivo?»; aquí es
            # «¿de verdad no está?». Un temporal que sobreviviera a otra
            # inyección dejaría esta prueba sin sujeto: el ensamblador
            # saldría limpio y el arnés lo cantaría como «SE COLÓ» de una
            # guarda que nunca tuvo nada que cazar. Es la regla 3, leída de
            # derecha a izquierda.
            if roto.exists():
                print(f"[ INERTE ] {nombre}")
                print(f"      {roto.name} SÍ existe en el temporal — la "
                      f"inyección se queda sin ausencia que probar")
                inertes += 1
                continue
        elif tipo == "obj":
            o = json.loads(limpias[superficie].read_text(encoding="utf-8"))
            accion(o)
            roto.write_text(json.dumps(o, ensure_ascii=False), encoding="utf-8")
        else:
            texto = limpias[superficie].read_text(encoding="utf-8")
            # Una sustitución que no sustituye nada dejaría el archivo intacto
            # y el ensamblador saldría limpio: el arnés informaría «SE COLÓ»
            # de una guarda que nunca llegó a tener nada que cazar. Eso es una
            # avería del arnés, y se dice como tal.
            # La comprobación va PASO A PASO y no toda de golpe contra el
            # texto original: en las inyecciones de varios pares, los pares
            # intermedios trabajan sobre marcadores que el paso anterior acaba
            # de poner y que en el original no existen.
            ausente = None
            for viejo, nvo, veces in accion:
                if viejo not in texto:
                    ausente = viejo
                    break
                texto = (texto.replace(viejo, nvo) if veces == 0
                         else texto.replace(viejo, nvo, veces))
            if ausente is not None:
                print(f"[ INERTE ] {nombre}")
                print(f"      no está en {SUPERFICIES[superficie][1].name}: "
                      f"{ausente[:60]!r} — la inyección no prueba nada")
                inertes += 1
                continue
            roto.write_text(texto, encoding="utf-8")
        rutas[superficie] = roto

        cod, sal, pisadas = corre(tmp, rutas["ensamblador"], rutas)
        vistas |= pisadas
        ms = males(sal)
        if cod != 0 and ms:
            cazados += 1
            etiqueta = "CAZADO"
        elif cod != 0:
            # Salió mal sin decir por qué: excepción, no diagnóstico. Cuenta
            # como colado, porque una guarda que revienta deja de informar del
            # resto — la lección de T1.3.i.
            colados += 1
            etiqueta = "REVIENTA"
        else:
            colados += 1
            etiqueta = "SE COLÓ"
        print(f"[{etiqueta:^9}] {nombre}   ({superficie})")
        for m in ms[:2]:
            print(f"      {m[:120]}")
        if etiqueta == "REVIENTA":
            ultima = [l for l in sal.splitlines() if l.strip()][-1]
            print(f"      sin línea MAL · {ultima.strip()[:120]}")


    # --- CONTROL DE SALIDA --------------------------------------------
    print()
    cod, sal, _ = corre(tmp, limpias["ensamblador"], dict(limpias))
    print(f"  {'OK  ' if cod == 0 else 'MAL '} control de salida · el arnés no dejó "
          f"nada tocado")
    intactos = all(origen.read_bytes() == originales[n]
                   for n, (_, origen) in SUPERFICIES.items())
    print(f"  {'OK  ' if intactos else 'MAL '} los archivos fuente siguen byte a byte igual")
    igual_html = (publicado_antes is None
                  or PUBLICADO.read_bytes() == publicado_antes)
    print(f"  {'OK  ' if igual_html else 'MAL '} el capítulo publicado no se ha tocado")

    print("\n" + "=" * 70)
    print(f"  {cazados} de {cazados + colados} defectos cazados"
          + (f" · {inertes} inyección(es) INERTE(s)" if inertes else ""))
    sin_ver = [(l, f) for i, (l, f) in enumerate(guardas) if i not in vistas]
    print(f"  {len(vistas)} de {len(guardas)} guardas se han visto disparar")
    if sin_ver:
        print(f"\n  Sin ver disparar ({len(sin_ver)}). Se imprimen para que nadie tenga")
        print("  que fiarse de que están bien escritas:")
        for l, f in sin_ver:
            print(f"    · {ENSAMBLADOR.name}:{l}  {f[:78]}")
    print("=" * 70)

    shutil.rmtree(tmp, ignore_errors=True)
    ok = (colados == 0 and inertes == 0 and cod == 0 and intactos and igual_html)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
