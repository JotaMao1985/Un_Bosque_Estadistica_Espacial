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
# nombre de la inyección -> trozo del mensaje de la guarda que TIENE que
# dispararse. Las guardas de `guardas_de_t22()` no son `problemas.append` y
# el inventario de arriba no las cuenta: para ellas no basta con que el
# ensamblado pare, tiene que parar diciendo ESO. Sin esto, una inyección
# que cazaba otra guarda anterior daba por probada una que nunca se disparó
# (verificación de R2 · T2.2: tres casos).
ESPERA: dict[str, str] = {}


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
        'aria-label="Variograma de una realización frente al teórico promediado en cada rezago, con la banda '
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
    txt("un espacio fino de LaTeX se cuela en la prosa", "ensamblador",
        "{ent(ne['enes'][0])} a {ent(ne['enes'][-1])} observaciones",
        "{ent_mate(ne['enes'][0])} a {ent_mate(ne['enes'][-1])} observaciones")

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

    # --- Módulo 5: lo que su prosa afirma (R1) ---------------------------
    #
    # Una inyección por guarda. Lo que se ataca no son cifras sueltas —eso es
    # de los auditores— sino las FRASES que las unen: «pasa por el rombo», «son
    # el mismo número», «el mismo número en todas», «más que el valor que
    # busca», «no sube». Y que el rho «medido» por bandas, retirado en esta
    # ronda, no pueda volver al JSON sin que el ensamblador pare.
    ne5 = lambda o: o["n_efectivo"]                                   # noqa: E731
    obj("el rho medio de Colombia deja de reproducir el titular", "datos",
        lambda o: ne5(o)["rho_del_titular"].__setitem__("implicito", 0.02))
    obj("el rho del titular habla de otros municipios", "datos",
        lambda o: ne5(o)["rho_del_titular"].__setitem__("n", 1113))
    obj("vuelve un rho «medido» sobre el mapa al JSON", "datos",
        lambda o: ne5(o)["rho_del_titular"].__setitem__("estimado", 0.0021195))
    obj("el n_eff de la fórmula deja de imprimirse igual que el exacto", "datos",
        lambda o: ne5(o)["exacto_campo"][4].__setitem__("n_eff_formula", 5.2))
    obj("el n_eff exacto del módulo 5 se queda sin la fila de phi = 4", "datos",
        lambda o: ne5(o)["exacto_campo"][4].__setitem__("phi", 5))
    obj("la demostración del centrado cambia de réplicas", "datos",
        lambda o: ne5(o)["centrado"].__setitem__("nrep", 500))
    obj("el rho medio verdadero no es el de la fila de phi = 4", "datos",
        lambda o: ne5(o)["centrado"].__setitem__("rho_medio_verdadero", 0.17394))
    obj("el promedio centrado deja de ser el mismo en todas las réplicas", "datos",
        lambda o: ne5(o)["centrado"].__setitem__("centrado_max", 0.0021195))
    obj("sobre la deserción el promedio centrado no es -1/(n-1)", "datos",
        lambda o: ne5(o)["centrado"]["colombia"].__setitem__("centrado", 0.0021195))
    obj("con la media verdadera el promedio ya no apunta al rho medio", "datos",
        lambda o: ne5(o)["centrado"]["con_media_verdadera"].__setitem__("media", 0.05))
    obj("la dispersión entre réplicas baja del rho medio", "datos",
        lambda o: ne5(o)["centrado"]["con_media_verdadera"].__setitem__("sd", 0.1))
    obj("el proceso simulado deja de tener varianza 1", "datos",
        lambda o: o["inferencia"].__setitem__("sigma", 2))
    obj("la tabla del techo pierde la fila de la retícula del módulo 4", "datos",
        lambda o: ne5(o)["techo"]["rejilla"][1].__setitem__("k", 17))
    obj("la tabla del techo cambia de alcance", "datos",
        lambda o: ne5(o)["techo"].__setitem__("phi", 8))
    obj("factor_n deja de ser el cociente de los extremos de la tabla", "datos",
        lambda o: ne5(o)["techo"].__setitem__("factor_n", 16))
    obj("al rellenar el último salto deja de ser pequeño", "datos",
        lambda o: ne5(o)["techo"].__setitem__("ultimo_salto_pct", 3.0))
    obj("la última fila del relleno se queda lejos de su techo", "datos",
        lambda o: ne5(o)["techo"].__setitem__("falta_techo_pct", 2.0))
    obj("una fila del relleno supera 1/rho_inf", "datos",
        lambda o: ne5(o)["techo"]["rejilla"][0]["relleno"].__setitem__("n_eff", 5.5))
    obj("techo_inf deja de ser el inverso de rho_inf", "datos",
        lambda o: ne5(o)["techo"].__setitem__("rho_inf", 0.25))
    obj("el techo del ejemplo del módulo 5 deja de ser 1/rhos[1]", "datos",
        lambda o: ne5(o)["caso_quiz"].__setitem__("techo_otro", 50))
    # Una fórmula escrita con UNA barra invertida en el ensamblador: Python la
    # convierte en un carácter de control y el HTML sale con las cifras bien
    # y la fórmula rota. Pasó de verdad al reescribir este módulo.
    txt("una fórmula del módulo 5 se escribe con una sola barra invertida", "ensamblador",
        "Hay dos maneras de pasar de", "Hay dos \\bar maneras de pasar de")
    obj("la corrección por s² del rho de Colombia deja de ser una rebaja", "datos",
        lambda o: ne5(o)["rho_del_titular"].__setitem__("implicito_con_s2", 0.02))
    obj("al ampliar el rho medio deja de caer", "datos",
        lambda o: ne5(o)["techo"]["rejilla"][3]["ampliacion"].__setitem__("rho_medio", 0.5))

    # --- Ejercicio 3: el n efectivo al revés (R1 · T1.2) -----------------
    #
    # El ejercicio se rehízo sobre el archivo público del Taller 1 y el
    # remuestreo por bloques. Sus guardas leen lo que la lectura AFIRMA —«la
    # red actual ya la supera», «siempre entre 25 y 50»— y que el ejercicio
    # se pueda hacer desde fuera. Una inyección por guarda.
    e3g = lambda o: o["e3"]["solucion"]       # noqa: E731
    obj("el ejercicio 3 enlaza un archivo que no está en el repo", "soluciones",
        lambda o: e3g(o).__setitem__("archivo", "entrega/datos/no_existe.gpkg"))
    obj("el ejercicio 3 vuelve a leer el dato que no se publica", "soluciones",
        lambda o: e3g(o).__setitem__("archivo",
                                     "precalculo/salidas/cap1_soluciones.json"))
    txt("el ejercicio 3 pierde el enlace de descarga", "ensamblador",
        "{ejercicio(3, S['e3'], datos=E3_DATOS, codigo=E3_CODIGO)}",
        "{ejercicio(3, S['e3'], codigo=E3_CODIGO)}")
    obj("ejercicio 3: el remuestreo por bloques deja de ensanchar", "soluciones",
        lambda o: e3g(o).__setitem__("n_eff", 417.39417))
    obj("ejercicio 3: vuelve el rho de las bandas", "soluciones",
        lambda o: e3g(o).__setitem__("rho_medio", 0.0314555721))
    obj("ejercicio 3: la bandera dice que 50 independientes se alcanzan", "soluciones",
        lambda o: e3g(o).__setitem__("objetivo_50_alcanzable", True))
    obj("ejercicio 3: con otra semilla el techo pasa de 50", "soluciones",
        lambda o: e3g(o)["otras_semillas"].__setitem__("techo_max", 51.73941))
    obj("ejercicio 3: las estaciones para 25 se redondean hacia abajo", "soluciones",
        lambda o: e3g(o).__setitem__("estaciones_para_25", 56))
    obj("ejercicio 3: la lectura cita un techo que no es el del JSON", "soluciones",
        lambda o: e3g(o).__setitem__("techo", 44.1739417))
    obj("ejercicio 3: el promedio centrado sale positivo", "soluciones",
        lambda o: e3g(o).__setitem__("centrado_todos_los_pares", 0.0027777778))
    obj("ejercicio 3: la lectura vuelve a la fórmula de equicorrelación", "soluciones",
        lambda o: o["e3"].__setitem__(
            "lectura", o["e3"]["lectura"] + " Es la fórmula de equicorrelación."))
    obj("ejercicio 3: vuelve el correlograma por bandas al JSON", "soluciones",
        lambda o: e3g(o).__setitem__("moran_por_banda", [0.41739, 0.21739]))
    # Segunda vuelta: el jackknife, los pesos por filas y los residuos. El
    # archivo sin versionar lo dispara ya el primer mutante de esta familia
    # (un archivo que no existe tampoco está en git).
    jkg = lambda o: e3g(o)["jackknife"]       # noqa: E731
    obj("ejercicio 3: el jackknife pierde un departamento", "soluciones",
        lambda o: jkg(o)["por_departamento"].pop(3))
    obj("ejercicio 3: el máximo del jackknife no es el de su lista", "soluciones",
        lambda o: jkg(o)["maximo"].__setitem__("techo", 61.73941))
    obj("ejercicio 3: ningún departamento voltea ya la respuesta", "soluciones",
        lambda o: (jkg(o)["maximo"].__setitem__("techo", 47.9),
                   [d.__setitem__("techo", 47.9) for d in jkg(o)["por_departamento"]
                    if d["departamento"] == jkg(o)["maximo"]["departamento"]],
                   jkg(o).__setitem__("n_sobre_objetivo", 0)))
    obj("ejercicio 3: el techo de la red sale del recorrido del jackknife", "soluciones",
        lambda o: (jkg(o)["minimo"].__setitem__("techo", 20.5),
                   [d.__setitem__("techo", 20.5) for d in jkg(o)["por_departamento"]
                    if d["departamento"] == jkg(o)["minimo"]["departamento"]]))
    obj("ejercicio 3: la semilla mueve el techo más que el dato", "soluciones",
        lambda o: e3g(o)["otras_semillas"].__setitem__("techo_min", 30.17394))
    obj("ejercicio 3: la lectura nombra un departamento y el JSON otro", "soluciones",
        lambda o: jkg(o)["minimo"].__setitem__("departamento", "Santander"))
    obj("ejercicio 3: la tabla pierde el techo sin el departamento que voltea", "soluciones",
        lambda o: o["e3"].__setitem__(
            "pasos", [p for p in o["e3"]["pasos"]
                      if not p["paso"].endswith("sin " + jkg(o)["maximo"]["departamento"])]))
    obj("ejercicio 3: el promedio con pesos por filas sale negativo", "soluciones",
        lambda o: e3g(o)["pesos_filas"]["promedio"].__setitem__(0, -0.0027777778))
    obj("ejercicio 3: la lectura cita un promedio por filas que no es el del JSON", "soluciones",
        lambda o: e3g(o)["pesos_filas"]["promedio"].__setitem__(2, 0.0241739))
    obj("ejercicio 3: el techo de los residuos deja de pasar de 50", "soluciones",
        lambda o: (e3g(o)["residuos"].__setitem__("techo", 48.17394),
                   e3g(o)["residuos"].__setitem__("objetivo_50_alcanzable", False)))
    obj("ejercicio 3: la correlación de los residuos no se despeja de su n_eff", "soluciones",
        lambda o: e3g(o)["residuos"].__setitem__("rho_medio", 0.0201739))
    obj("ejercicio 3: las estaciones para 50 con los residuos, mal redondeadas", "soluciones",
        lambda o: e3g(o)["residuos"].__setitem__(
            "estaciones_para_50", e3g(o)["residuos"]["estaciones_para_50"] + 2))
    obj("ejercicio 3: la lectura cita una caída de la correlación que no es la del JSON",
        "soluciones", lambda o: e3g(o)["residuos"].__setitem__("caida_rho_pct", 31.73941))
    obj("ejercicio 3: la altitud deja de explicar casi toda la temperatura", "soluciones",
        lambda o: e3g(o)["residuos"].__setitem__("r2", 0.4173941))
    obj("ejercicio 3: el enunciado pierde el apartado (d)", "soluciones",
        lambda o: o["e3"].__setitem__("enunciado", o["e3"]["enunciado"].replace("(d) ", "")))

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

    # --- R1 · T1.4: módulos 2, 6 y 10 y la pregunta del gráfico ----------
    # Una inyección por guarda nueva. Todas entran por el JSON de cifras:
    # lo que vigilan es que la FRASE siga siendo cierta si el dato cambia.
    obj("el perímetro urbano deja de caber en el Distrito", "datos",
        lambda o: o["colombia"]["puntual"].__setitem__(
            "n_urbana", o["colombia"]["puntual"]["n_dc"]))
    obj("lo que el Distrito añade al perímetro deja de estar casi vacío", "datos",
        lambda o: o["colombia"]["puntual"].__setitem__(
            "area_dc_km2", o["colombia"]["puntual"]["area_urbana_km2"] + 10))
    obj("la intensidad del perímetro deja de superar a la del Distrito", "datos",
        lambda o: o["colombia"]["puntual"].__setitem__("factor_lambda", 0.9173941))
    obj("el teórico de la clase pierde un rezago", "datos",
        lambda o: o["una_realizacion"]["variograma"].__setitem__(
            "teorico_clase", o["una_realizacion"]["variograma"]["teorico_clase"][:7]))
    obj("el teórico de la clase 1 vuelve a ser gamma(1)", "datos",
        lambda o: o["una_realizacion"]["variograma"]["teorico_clase"].__setitem__(
            0, o["una_realizacion"]["variograma"]["teorico"][0]))
    obj("la media de las realizaciones cae sobre gamma(1) y no sobre la clase", "datos",
        lambda o: o["una_realizacion"]["variograma"]["media"].__setitem__(
            0, o["una_realizacion"]["variograma"]["teorico"][0]))
    obj("un desvío publicado vuelve a medirse contra gamma en h entero", "datos",
        lambda o: o["realizaciones_vistas"][1].__setitem__(
            "desvio_rel_max",
            max(abs(v - t) / t for v, t in zip(
                o["realizaciones_vistas"][1]["variograma"],
                o["una_realizacion"]["variograma"]["teorico"]))))
    obj("la referencia uniforme no usa tantos puntos como estaciones", "datos",
        lambda o: o["diseno_modelo"]["referencia_uniforme"].__setitem__("n_puntos", 360))
    obj("los cuantiles de la referencia uniforme se desordenan", "datos",
        lambda o: o["diseno_modelo"]["referencia_uniforme"].__setitem__("razon_p05", 91.73941))
    obj("la red deja de estar muy por encima de la referencia uniforme", "datos",
        lambda o: o["diseno_modelo"].__setitem__("razon_areas", 917.3941))
    obj("«veces la mediana» deja de ser el cociente de sus dos cifras", "datos",
        lambda o: o["diseno_modelo"]["referencia_uniforme"].__setitem__(
            "red_sobre_mediana", 41.73941))
    obj("el promedio de las medias deja de estar sobre la media verdadera", "datos",
        lambda o: o["una_realizacion"].__setitem__("media_de_las_medias", 0.2173941))
    obj("el e.e. real deja de crecer con el alcance", "datos",
        lambda o: o["inferencia"]["rejilla"][-1].__setitem__("ee_real", 0.0717394))

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

    # --- R1 · T1.6: lo que afirman los módulos 3, 4, 6 y 7 y el ejercicio 2 --
    #
    # Una inyección por guarda nueva. Como en el módulo 5, lo que se ataca son
    # las frases que unen las cifras: «solo N de las 361», «por encima», «no
    # es ruido», «muy desiguales», «el extremo lo pone», «bastante menos»,
    # «inequívoca», «varía N veces más», «por debajo».
    SERIES3 = ("ideam", "residuos_altitud", "permutado")

    def banda3(o, i, n_con, esperado=None, programa=None):
        """La misma banda, en las tres series: así no salta la guarda de la rejilla común."""
        n_ = o["colombia"]["geo"]["n"]
        for nombre in SERIES3:
            b = o["tobler"][nombre]["bandas"][i]
            b["n_con_vecinos"] = n_con
            b["esperado"] = -n_con / (n_ * (n_ - 1)) if esperado is None else esperado
            b["esperado_programa"] = -1 / (n_con - 1) if programa is None else programa
    obj("la E[I] por banda de una serie deja de ser la de las otras", "datos",
        lambda o: o["tobler"]["residuos_altitud"]["bandas"][0].__setitem__("n_con_vecinos", 251))
    obj("la E[I] de una banda deja de ser -n'/(n(n - 1))", "datos",
        lambda o: banda3(o, 2, o["tobler"]["ideam"]["bandas"][2]["n_con_vecinos"], -0.0031))
    obj("la esperanza que imprime el programa deja de ser -1/(n' - 1)", "datos",
        lambda o: banda3(o, 2, o["tobler"]["ideam"]["bandas"][2]["n_con_vecinos"], programa=-0.0031))
    obj("las permutaciones pasan a respaldar la convención del programa", "datos",
        lambda o: o["tobler"]["permutacion_banda1"].__setitem__(
            "media", o["tobler"]["ideam"]["bandas"][0]["esperado_programa"]))
    obj("en la primera banda todas las estaciones tienen vecinos", "datos",
        lambda o: banda3(o, 0, o["colombia"]["geo"]["n"]))
    obj("en la última banda alguna estación se queda sin vecinos", "datos",
        lambda o: banda3(o, -1, o["colombia"]["geo"]["n"] - 3))
    ir4 = lambda o: o["inferencia_real"]                              # noqa: E731

    def replicas_abajo(o):
        r = ir4(o)["replicas"]
        r["desvio_esperanza"] = -abs(r["desvio_esperanza"])
        r["esperanza_bloques"] = ir4(o)["media"] + r["desvio_esperanza"]
    obj("la esperanza de las réplicas por bloques pasa a quedar por debajo de la media muestral",
        "datos", replicas_abajo)
    obj("el desvío de la esperanza pasa a ser ruido", "datos",
        lambda o: ir4(o)["replicas"].__setitem__("emc_esperanza", 0.01))
    obj("las réplicas de la tabla se salen de su ruido alrededor de la esperanza", "datos",
        lambda o: ir4(o)["replicas"].__setitem__("media_bloques", 3.48))
    obj("el error estándar jackknife no sale de la lista ni supera a medio recorrido", "datos",
        lambda o: ir4(o)["sin_un_departamento"].__setitem__("ee_jackknife_factor", 0.3))
    obj("el tamaño efectivo, con tres e.e. jackknife, deja de quedar muy lejos de los municipios", "datos",
        lambda o: ir4(o)["sin_un_departamento"].__setitem__("ee_jackknife_n_eff", 80.0))
    obj("el e.e. jackknife del tamaño efectivo baja del 25 % de la cifra", "datos",
        lambda o: ir4(o)["sin_un_departamento"].__setitem__("ee_jackknife_n_eff_pct", 20.0))
    obj("la z de una I departamental igual a la municipal se sale de entre las dos z", "datos",
        lambda o: o["escala"].__setitem__("z_departamental_si_igual", 25.0))
    obj("el ejercicio 3 publica un e.e. jackknife que su lectura no cita", "soluciones",
        lambda o: o["e3"]["solucion"]["jackknife"].__setitem__("ee_techo", 5.0))
    obj("las réplicas i.i.d. se separan de la media muestral", "datos",
        lambda o: ir4(o)["replicas"].__setitem__("desvio_iid", 0.002))
    obj("los departamentos dejan de ser de tamaños muy desiguales", "datos",
        lambda o: ir4(o)["replicas"].__setitem__("bloque_min", 20))
    obj("la lista de un departamento menos no cuadra con el módulo", "datos",
        lambda o: ir4(o)["sin_un_departamento"].__setitem__("n_departamentos_quedan", 33))
    obj("el recorrido sin un departamento no es el de su lista", "datos",
        lambda o: ir4(o)["sin_un_departamento"].__setitem__("factor_min", 3.5))
    obj("el extremo que la prosa nombra es otro departamento", "datos",
        lambda o: ir4(o)["sin_un_departamento"].__setitem__(
            "extremo", dict(ir4(o)["sin_un_departamento"]["por_departamento"][0])))
    obj("sin el departamento del extremo el factor ya no baja", "datos",
        lambda o: ir4(o).__setitem__("factor", 3.0))
    obj("el titular del módulo se sale del recorrido sin un departamento", "datos",
        lambda o: ir4(o).__setitem__("n_eff", 50.0))
    obj("cambiar de semilla mueve tanto como quitar un departamento", "datos",
        lambda o: ir4(o)["otras_semillas"].update(n_eff_min=40.0, n_eff_max=80.0))
    obj("el alfa de la prueba del módulo 6 no es el porcentaje que debería rechazar", "datos",
        lambda o: o["inferencia"].__setitem__("alfa", 0.01))
    obj("la I municipal deja de ser inequívoca", "datos",
        lambda o: o["escala"].__setitem__("z_municipal", 1.2))
    obj("la I departamental deja de variar más que la municipal", "datos",
        lambda o: o["escala"].update(razon_ee=0.8, ee_departamental=0.8 * o["escala"]["ee_municipal"]))
    obj("un intervalo del ejercicio 2 deja de estar centrado en la media", "soluciones",
        lambda o: o["e2"]["solucion"]["ic_bloques"].__setitem__(
            1, o["e2"]["solucion"]["ic_bloques"][1] + 0.4))

    def e2_al_otro_lado(o):
        e = o["e2"]["solucion"]
        e["desvio_esperanza"] = -e["desvio_esperanza"]
        e["esperanza_replicas_bloques"] = e["media"] + e["desvio_esperanza"]
    obj("las réplicas del ejercicio 2 caen al otro lado de lo que dice la lectura", "soluciones",
        e2_al_otro_lado)

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

    # --- R2 · T2.4: las tres gráficas nuevas ------------------------------
    #
    # Una inyección por guarda, como en R1. Se atacan las frases que la prosa
    # pone entre las cifras —«ninguna llega», «la reproducen», «algo más»,
    # «muy por encima», «ya no se distingue», «en ninguna», «casi la misma»,
    # «una muestra de ella», «a un lado y a otro»— y el cableado de lo que el
    # navegador dibuja: el histograma, la franja y los cien segmentos.
    al_ = lambda o: o["snow"]["aleatorizacion"]                      # noqa: E731
    ev_ = lambda o: o["tobler"]["envolvente"]                        # noqa: E731
    ci_ = lambda o: o["inferencia"]["cien_ic"]                       # noqa: E731
    # Módulo 1.
    obj("T2.4 m1: el histograma de la nula deja de sumar las recolocaciones", "datos",
        lambda o: al_(o)["hist_frec"].__setitem__(0, al_(o)["hist_frec"][0] + 1))
    obj("T2.4 m1: la media publicada de la nula no es la del histograma", "datos",
        lambda o: al_(o).__setitem__("media_nula_pct", al_(o)["media_nula_pct"] + 0.5))
    obj("T2.4 m1: el máximo de la nula en porcentaje no es el de su recuento", "datos",
        lambda o: al_(o).__setitem__("max_nula_pct", 13.5))
    obj("T2.4 m1: una recolocación pasa a alcanzar al observado", "datos",
        lambda o: al_(o).__setitem__("n_mayor_o_igual", 1))
    obj("T2.4 m1: las recolocaciones dejan de reproducir la parte de calle", "datos",
        lambda o: al_(o).__setitem__("emc_media_pct", 0.001))
    obj("T2.4 m1: las partes de calle dejan de sumar la calle entera", "datos",
        lambda o: al_(o)["pct_calle_por_bomba"].__setitem__(0, al_(o)["pct_calle_por_bomba"][0] + 1))
    obj("T2.4 m1: a Broad St le toca menos calle que el reparto ingenuo", "datos",
        lambda o: al_(o).__setitem__("pct_calle_broad", 7.0))
    obj("T2.4 m1: «veces lo que le tocaría por calle» deja de ser su cociente", "datos",
        lambda o: al_(o).__setitem__("razon_sobre_calle", 6.5))
    obj("T2.4 m1: el observado deja de quedar lejísimos de la nula", "datos",
        lambda o: al_(o).__setitem__("z_observado", 4.0))
    # Módulo 3.
    obj("T2.4 m3: la envolvente deja de ir sobre las bandas del correlograma", "datos",
        lambda o: ev_(o)["ideam"][0].__setitem__("d2", 26))
    obj("T2.4 m3: la posición publicada de una banda no es la de su I", "datos",
        lambda o: ev_(o)["ideam"][6].__setitem__("posicion", "debajo"))
    obj("T2.4 m3: la envolvente deja de estar centrada en E[I]", "datos",
        lambda o: ev_(o)["ideam"][2].__setitem__("media", ev_(o)["ideam"][2]["media"] + 0.01))
    # El paro duro: sin banda por debajo no hay párrafo que escribir.
    obj("T2.4 m3: la temperatura se queda sin banda por debajo de la franja", "datos",
        lambda o: ev_(o)["ideam"][5].__setitem__("posicion", "dentro"))
    obj("T2.4 m3: la banda negativa ya no queda bajo todas las permutaciones", "datos",
        lambda o: ev_(o)["ideam"][5].__setitem__("min", -0.09))
    obj("T2.4 m3: la primera banda deja de quedar «muy por encima»", "datos",
        lambda o: ev_(o)["ideam"][0].__setitem__("hi", 0.3))
    obj("T2.4 m3: los residuos dejan de leerse «dentro» entre 175 y 300 km", "datos",
        lambda o: ev_(o)["residuos_altitud"][4].__setitem__("posicion", "encima"))
    obj("T2.4 m3: el recuento de bandas fuera no es el de las posiciones", "datos",
        lambda o: ev_(o).__setitem__("n_fuera_ideam", 5))
    obj("T2.4 m3: la permutación suelta se sale de la franja", "datos",
        lambda o: ev_(o).__setitem__("n_fuera_permutado", 1))
    obj("T2.4 m3: los residuos se leen distinto contra la franja de la temperatura", "datos",
        lambda o: ev_(o)["ideam"][4].__setitem__("lo", -0.01))
    obj("T2.4 m3: las dos envolventes dejan de ser «casi la misma»", "datos",
        lambda o: ev_(o)["residuos_altitud"][0].__setitem__("hi", 0.12))
    obj("T2.4 m3: los cuantiles del pie de la tabla no son los del nivel", "datos",
        lambda o: ev_(o).__setitem__("cuantil_lo_pct", 5))
    # Módulo 4.
    obj("T2.4 m4: los cien intervalos pasan a ser de otro alcance", "datos",
        lambda o: ci_(o).__setitem__("phi", 2))
    obj("T2.4 m4: el recuento publicado no es el de los intervalos dibujados", "datos",
        lambda o: ci_(o).__setitem__("n_cubren_ingenuo", 30))
    obj("T2.4 m4: los cien dejan de ser una muestra de la cobertura publicada", "datos",
        lambda o: next(f for f in o["inferencia"]["rejilla"] if f["phi"] == 4).__setitem__(
            "cobertura", 0.5))
    obj("T2.4 m4: el cociente de los dos semianchos deja de cuadrar", "datos",
        lambda o: ci_(o).__setitem__("razon_semianchos", 6.0))
    obj("T2.4 m4: con el e.e. verdadero la cobertura ya no es la prometida", "datos",
        lambda o: ci_(o).__setitem__("cobertura_exacto", 0.90))
    obj("T2.4 m4: las cien medias caen todas del mismo lado del cero", "datos",
        lambda o: ci_(o).__setitem__("media", [abs(x) for x in ci_(o)["media"]]))
    # Segunda ronda de T2.4: el marco del plano, lo que el eje deja fuera, la
    # suma por bandas, «no es raro», y los dos cocientes del módulo 4.
    obj("T2.4 r2 m1: la tabla de marcos no acaba en las cifras del titular", "datos",
        lambda o: al_(o)["marcos"][-1].__setitem__("pct_calle_broad", 8.7))
    obj("T2.4 r2 m1: en un marco la razón no es el observado entre su parte", "datos",
        lambda o: al_(o)["marcos"][1].__setitem__("razon_sobre_calle", 4.5))
    obj("T2.4 r2 m1: la parte de calle deja de bajar al ensanchar el marco", "datos",
        lambda o: al_(o)["marcos"][0].__setitem__("pct_longitud", 60.0))
    obj("T2.4 r2 m1: con el marco estrecho el dato deja de quedar lejos", "datos",
        lambda o: al_(o)["marcos"][0].__setitem__("z_binomial", 4.0))
    ma_ = lambda o: o["tobler"]["mas_alla"]                          # noqa: E731
    su_ = lambda o: o["tobler"]["sumas"]                             # noqa: E731
    obj("T2.4 r2 m3: las parejas de más allá del eje pasan a quedar dentro", "datos",
        lambda o: ma_(o).__setitem__("posicion", "dentro"))
    obj("T2.4 r2 m3: las sumas por banda dejan de dar -1", "datos",
        lambda o: su_(o).__setitem__("mas_alla", -1.9))
    obj("T2.4 r2 m3: las parejas cortas no son las bandas por encima", "datos",
        lambda o: su_(o).__setitem__("cortas", 11.0))
    obj("T2.4 r2 m3: una banda corta pasa a sumar en negativo", "datos",
        lambda o: (su_(o)["bandas"][0].__setitem__("suma", -1.0),
                   su_(o)["bandas"][1].__setitem__("suma", su_(o)["bandas"][1]["suma"]
                                                   + 1.0 + 1.6567309834)))
    obj("T2.4 r2 m3: casi ninguna permutación se sale en alguna banda", "datos",
        lambda o: ev_(o).__setitem__("pct_alguna_fuera", 4.0))
    obj("T2.4 r2 m4: el cociente de semianchos pasa a ser el factor del recuadro", "datos",
        lambda o: ci_(o).__setitem__(
            "razon_semianchos", next(f for f in o["inferencia"]["rejilla"] if f["phi"] == 4)["factor"]))
    obj("T2.4 r2 m4: el nivel escrito deja de ser el de alfa", "datos",
        lambda o: o["inferencia"].__setitem__("nivel_pct", 90))

    # --- R2 · T2.2: las gráficas y los mapas propios (guardas_de_t22) ----
    txt("T2.2: la banda del marcador vuelve a medirse en píxeles", "ensamblador",
        "const x0 = Math.max(a.left, eje.getPixelForValue(i - medio));",
        "const x0 = x - 10;")
    obj("T2.2: una bomba de Snow se queda sin celda", "mapas",
        lambda o: o["snow"]["celdas"].pop())
    obj("T2.2: dos bombas de Snow se cambian la celda", "mapas",
        lambda o: o["snow"]["celdas"].__setitem__(slice(5, 7), o["snow"]["celdas"][5:7][::-1]))
    obj("T2.2: el mapa de Snow vuelve a llevar pie de leyenda", "mapas",
        lambda o: o["snow"].__setitem__("leyenda", "bomba más próxima"))
    txt("T2.2: la paleta de la plantilla pierde el bermellón", "plantilla",
        "'#E69F00', '#56B4E9', '#009E73', '#B8860B', '#0072B2', '#D55E00',",
        "'#E69F00', '#56B4E9', '#009E73', '#B8860B', '#0072B2', '#D55F00',")
    txt("T2.2: la paleta de la plantilla ya trae el naranja del acento", "plantilla",
        "'#CC79A7', '#525252', '#8B4513', '#6A3D9A', '#00868B', '#C71585',",
        "'#CC79A7', '#525252', '#FF6600', '#6A3D9A', '#00868B', '#C71585',")
    obj("T2.2: la rampa del zinc vuelve a ser lineal", "mapas",
        lambda o: o["meuse"].pop("marcas_escala"))
    obj("T2.2: el Mosa pierde una orilla", "mapas",
        lambda o: o["meuse"]["lineas"].pop())
    obj("T2.2: un punto del Mosa se corre diez metros", "mapas",
        lambda o: o["meuse"]["pts"].__setitem__(0, o["meuse"]["pts"][0] + 10))
    obj("T2.2: un pino se corre una centésima", "mapas",
        lambda o: o["japanesepines"]["pts"].__setitem__(0, o["japanesepines"]["pts"][0] + 41))
    txt("T2.2: la rampa de la temperatura deja de ir de oscuro a claro", "ensamblador",
        '"#cc4778", "#ed7953"', '"#ed7953", "#cc4778"')
    txt("T2.2: la plantilla ya trae una paleta termica", "plantilla",
        "      grises:   ['#f5f5f5',", "      termica: ['#000000', '#ffffff'],\n      grises:   ['#f5f5f5',")
    obj("T2.2: el mapa del IDEAM pierde el contorno", "mapas",
        lambda o: o["ideam"].pop("lineas"))
    obj("T2.2: las franjas de altitud no suman las estaciones", "datos",
        lambda o: o["visto"]["ideam"]["por_altitud"][0].__setitem__("n", 149))
    obj("T2.2: un campo pierde el centro", "mapas",
        lambda o: o["campos"][3].pop("centro"))
    obj("T2.2: una realización va con escala propia", "mapas",
        lambda o: o["realizaciones"][1].__setitem__("rango", [-2.0, 2.0]))
    obj("T2.2: el recuento por clase de un campo no suma", "mapas",
        lambda o: o["campos"][0]["tam"].__setitem__(0, 99))
    # 32 × 8 y no 28 × 28: las celdas siguen siendo 256, así que `tam` sigue
    # sumando y la única guarda que puede saltar es la de la retícula.
    obj("T2.2: el campo vuelve a la rejilla de 28", "mapas",
        lambda o: [(g.__setitem__("nx", 32), g.__setitem__("ny", 8)) for g in o["campos"]])
    obj("T2.2: el campo destacado no es la réplica 1", "mapas",
        lambda o: o["campos"][4].__setitem__("media_espacial", 0.5))
    obj("T2.2: el título del campo vuelve a decir «rango»", "mapas",
        lambda o: o["campos"][4].__setitem__("titulo", "Campo gaussiano, rango = 4"))
    obj("T2.2: la ventana del acercamiento se sale del mapa", "mapas",
        lambda o: o["agregacion"]["zoom"]["caja"].__setitem__(2, o["agregacion"]["caja"][2] + 5000))
    obj("T2.2: el acercamiento declara celdas que no son columnas por filas", "mapas",
        lambda o: o["agregacion"]["zoom"].__setitem__("n_celdas", 21))
    obj("T2.2: una celda del caso queda fuera del acercamiento", "mapas",
        lambda o: o["agregacion"]["zoom"]["caja"].__setitem__(0, o["agregacion"]["zoom"]["caja"][0] + 400000))
    obj("T2.2: el porcentaje de rechazos ya no cabe en un decimal", "datos",
        lambda o: o["una_realizacion"].__setitem__("pct_rechaza_ingenuo", 82.04))
    # Se mueve UN par, no el recuento: con `n_suben` cambiado paraba antes el
    # `PARADO` que exige que los dos recuentos sumen los pares.
    obj("T2.2: los pares que se alejan del 0 no son los que cuenta R", "datos",
        lambda o: next(p for p in o["escala_correlacion"]["pares"]
                       if 0 < p["r_departamental"] < p["r_municipal"] and not p["invierte_signo"])
        .__setitem__("r_departamental", 0.95))
    obj("T2.2: un pliegue se queda sin estaciones", "mapas",
        lambda o: o["ideam"].__setitem__("pliegue_aleatorio",
                                         [1 if v == 10 else v for v in o["ideam"]["pliegue_aleatorio"]]))
    obj("T2.2: los bloques del mapa no tienen los tamaños publicados", "datos",
        lambda o: o["cv_espacial"]["tam_pliegues"].__setitem__(0, 3))
    obj("T2.2: la vecina más próxima ya no separa los dos repartos", "datos",
        lambda o: o["cv_espacial"].__setitem__("vecina_en_su_pliegue_aleatoria", 200))
    obj("T2.2: la barra de los bloques ya no supera la desviación típica", "datos",
        lambda o: o["cv_espacial"].__setitem__("sd_variable", 6.0))
    txt("T2.2: el deslizador de rho pierde el de Colombia", "ensamblador",
        ".concat([0.001, 0.002, 0.005, 0.03, 0.075, 0.15, rt.implicito]))].sort(",
        ".concat([0.001, 0.002, 0.005, 0.03, 0.075, 0.15]))].sort(")
    obj("T2.2: el rho de Colombia cae sobre otra posición del deslizador", "datos",
        lambda o: o["n_efectivo"]["rho_del_titular"].__setitem__("implicito", 0.02))
    txt("T2.2: la cobertura vuelve al lienzo de los errores estándar", "ensamblador",
        'canvas data-panel="cobertura"', 'canvas data-panel="otro"')

    obj("T2.2: los dos recuentos de pares dejan de sumar los pares", "datos",
        lambda o: o["escala_correlacion"].__setitem__("n_suben", 9))
    txt("T2.2: el acento de la plantilla deja de ser el naranja", "plantilla",
        "const GEOMAPA_ACENTO = '#FF6600';", "const GEOMAPA_ACENTO = '#FF6601';")
    txt("T2.2: la plantilla pierde el ámbar que se cambia por amarillo", "plantilla",
        "'#E69F00', '#56B4E9',", "'#E69F01', '#56B4E9',")
    obj("T2.2: las estaciones de San Andrés caen dentro del contorno", "mapas",
        lambda o: o["ideam"]["lineas"].append([0, 3000, 1000, 3000, 1000, 4096, 0, 4096, 0, 3000]))
    obj("T2.2: un par sin estrato deja de acercarse al cero", "datos",
        lambda o: o["escala_correlacion"]["caso_aviso"]["bajan_sin_estrato"][0]
        .__setitem__("r_departamental_n30", -0.5))
    # --- R2 · T2.3 ---
    obj("T2.3: el mapa de Bogotá pierde un borde", "mapas",
        lambda o: o["bogota"]["bordes"].pop("distrito"))
    obj("T2.3: el Distrito sale más denso que el perímetro urbano", "datos",
        lambda o: o["colombia"]["puntual"].__setitem__("lambda_dc", 6.5))
    obj("T2.3: una intensidad de Bogotá no es sus sedes entre su área", "datos",
        lambda o: o["colombia"]["puntual"].__setitem__("area_caja_km2", 4000.0))
    obj("T2.3: el rectángulo de las sedes cabe en el Distrito", "datos",
        lambda o: o["colombia"]["puntual"].__setitem__("pct_caja_fuera_dc", 0.0))
    obj("T2.3: el rectángulo dibujado en Bogotá no ciñe a las sedes", "mapas",
        lambda o: o["bogota"]["bordes"]["caja"][0].__setitem__(0, o["bogota"]["bordes"]["caja"][0][0] - 200))
    obj("T2.3: la lectura de Bogotá pone una sede urbana en el resto del Distrito", "mapas",
        lambda o: o["bogota"]["dentro"].__setitem__(o["bogota"]["dentro"].index(2), 1))
    obj("T2.3: con el rectángulo de los pinos la intensidad baja", "datos",
        lambda o: o["puntual_canonico"]["japanesepines"].__setitem__("lambda_caja", 60.0))
    txt("T2.3: un mapa del módulo 2 pierde su mando de la pregunta", "ensamblador",
        "controles: [interruptorAleatorio('meuse')],", "controles: [],")
    txt("T2.3: el capítulo vuelve a escribir en la paleta del motor", "ensamblador",
        "      const lista = GEOMAPA_CUALITATIVA.slice();",
        "      const lista = GEOMAPA_CUALITATIVA; GEOMAPA_CUALITATIVA[0] = '#F0E442';")
    txt("T2.3: el título de Bogotá se copia con Object.assign y se congela", "ensamblador",
        "    Object.defineProperties(GEOMAPAS['cap1-bogota'], Object.getOwnPropertyDescriptors({",
        "    Object.assign(GEOMAPAS['cap1-bogota'], {",
        "      descripcion: () => DESC1_BOGOTA[bogotaVentana]\n    }));",
        "      descripcion: () => DESC1_BOGOTA[bogotaVentana]\n    });")
    # --- R2 · T2.3, ronda 2: lo que escriben las lecturas, los títulos y las respuestas
    # (las diez del verificador, A–J, más las de R1, N1, N3 y los tercios).
    txt("T2.3b: las tres frases del borde de Bogotá, en orden invertido", "ensamblador",
        "const BOGOTA1_DONDE = ['fuera del Distrito Capital', 'en el Distrito Capital, fuera del perímetro urbano',\n                           'dentro del perímetro urbano, y por tanto del Distrito Capital'];",
        "const BOGOTA1_DONDE = ['dentro del perímetro urbano, y por tanto del Distrito Capital', 'en el Distrito Capital, fuera del perímetro urbano',\n                           'fuera del Distrito Capital'];")
    txt("T2.3b: «entra / no entra» cruzado entre perímetro y Distrito", "ensamblador",
        "(bogotaVentana === 'distrito' ? k >= 1 : k === 2)", "(bogotaVentana === 'distrito' ? k === 2 : k >= 1)")
    txt("T2.3b: la respuesta de Carolina del Norte, la de los puntuales", "ensamblador",
        'id="aleatorio-nc" hidden style="font-size:0.9rem;color:#012820;margin:0.25rem 0 1rem 0;"><strong>Lo aleatorio es el valor de cada unidad.</strong>',
        'id="aleatorio-nc" hidden style="font-size:0.9rem;color:#012820;margin:0.25rem 0 1rem 0;"><strong>Lo aleatorio es dónde.</strong>')
    txt("T2.3b: la clase se lee con los cortes de la siguiente", "ensamblador",
        "de ${n5(d.cortes[k - 1], 2)} a `\n        + `${n5(d.cortes[k], 2)}", "de ${n5(d.cortes[k], 2)} a `\n        + `${n5(d.cortes[k + 1], 2)}")
    txt("T2.3b: el título del perímetro urbano con las sedes del Distrito", "ensamblador",
        "Con el perímetro urbano por ventana: ${miles1(p.n_urbana)}", "Con el perímetro urbano por ventana: ${miles1(p.n_dc)}")
    txt("T2.3b: el zinc del punto vecino", "ensamblador",
        "${miles1(d.marcas[i])} ppm de zinc", "${miles1(d.marcas[(i + 1) % d.n])} ppm de zinc")
    txt("T2.3b: el título de los pinos con la intensidad de la otra ventana", "ensamblador",
        "intensidad estimada ${cifra(p.lambda_caja, 5)}", "intensidad estimada ${cifra(p.lambda, 5)}")
    txt("T2.3b: Snow lee la bomba con los niveles corridos", "ensamblador",
        "d.niveles[d.marcas[i] - 1]", "d.niveles[d.marcas[i] % d.niveles.length]")
    txt("T2.3b: la prosa da al rectángulo de los pinos el área de la ventana", "ensamblador",
        "{n(pc['japanesepines']['area_caja'], 3)} y", "{n(pc['japanesepines']['area'], 3)} y")
    txt("T2.3b: Bogotá rotula su rectángulo como ventana", "ensamblador",
        "etiqueta: PUESTO1(bogotaVentana === 'caja') + BOGOTA1_NOMBRE[bogotaVentana]",
        "etiqueta: 'ventana: ' + BOGOTA1_NOMBRE[bogotaVentana]")
    txt("T2.3b: los pinos rotulan su rectángulo como ventana", "ensamblador",
        "etiqueta: PUESTO1(pinosVentana === 'caja') + PINOS1_NOMBRE[pinosVentana]",
        "etiqueta: 'ventana: ' + PINOS1_NOMBRE[pinosVentana]")
    txt("T2.3b: la respuesta de los pinos deja de decir por qué el rectángulo no vale", "ensamblador",
        "El rectángulo que ciñe a los puntos no es una ventana: lo dibujan",
        "El rectángulo que ciñe a los puntos también sirve: lo dibujan")
    txt("T2.3b: la lectura de Bogotá vuelve a escribir «de el»", "ensamblador",
        "' en la cuenta ' + DE1(BOGOTA1_NOMBRE[bogotaVentana])", "' en la cuenta de ' + BOGOTA1_NOMBRE[bogotaVentana]")
    txt("T2.3b: los siete mapas vuelven a la etiqueta del motor", "ensamblador",
        "Object.keys(ETIQUETA1).forEach(k => { GEOMAPAS[k].etiqueta = ETIQUETA1[k]; });", "")
    obj("T2.3b: el perímetro urbano baja del corte de los tercios", "datos",
        lambda o: o["visto"]["bogota"].__setitem__("margen_urbano_m", -3.0))
    obj("T2.3b: las sedes de fuera del Distrito no cuadran por tercio", "datos",
        lambda o: o["visto"]["bogota"]["fuera_dc"].__setitem__(1, 0))
    for _nombre, _mensaje in (
            ("T2.3: el título de Bogotá se copia con Object.assign y se congela", "no siguen a su mando"),
            ("T2.3b: las tres frases del borde de Bogotá, en orden invertido", "no dicen el borde o la cuenta"),
            ("T2.3b: «entra / no entra» cruzado entre perímetro y Distrito", "no dicen el borde o la cuenta"),
            ("T2.3b: la respuesta de Carolina del Norte, la de los puntuales", "no es la de su tipo de dato"),
            ("T2.3b: la clase se lee con los cortes de la siguiente", "no dan el valor o la clase"),
            ("T2.3b: el título del perímetro urbano con las sedes del Distrito", "el título no da las sedes"),
            ("T2.3b: el zinc del punto vecino", "no dan el zinc"),
            ("T2.3b: el título de los pinos con la intensidad de la otra ventana", "no da el área y la intensidad de ese borde"),
            ("T2.3b: Snow lee la bomba con los niveles corridos", "no dan la bomba"),
            ("T2.3b: la prosa da al rectángulo de los pinos el área de la ventana", "la prosa no da el área"),
            ("T2.3b: Bogotá rotula su rectángulo como ventana", "se rotula como ventana"),
            ("T2.3b: los pinos rotulan su rectángulo como ventana", "se rotula como ventana"),
            ("T2.3b: la respuesta de los pinos deja de decir por qué el rectángulo no vale", "no dice por qué el rectángulo"),
            ("T2.3b: la lectura de Bogotá vuelve a escribir «de el»", "«de el»"),
            ("T2.3b: los siete mapas vuelven a la etiqueta del motor", "la etiqueta accesible no es"),
            ("T2.3b: el perímetro urbano baja del corte de los tercios", "ya no cabe en el tercio norte"),
            ("T2.3b: las sedes de fuera del Distrito no cuadran por tercio", "no cuadran con las del dato"),
            ("T2.3: el mapa de Bogotá pierde un borde", "no trae los tres bordes"),
            ("T2.3: la lectura de Bogotá pone una sede urbana en el resto del Distrito", "no cuadra con las sedes de cada ventana"),
            ("T2.3: el Distrito sale más denso que el perímetro urbano", "ya no bajan del perímetro urbano"),
            ("T2.3: una intensidad de Bogotá no es sus sedes entre su área", "no es sus sedes entre su área"),
            ("T2.3: el rectángulo de las sedes cabe en el Distrito", "ya no se sale del Distrito"),
            ("T2.3: el rectángulo dibujado en Bogotá no ciñe a las sedes", "no es el que ciñe a las sedes"),
            ("T2.3: con el rectángulo de los pinos la intensidad baja", "la intensidad ya no sube"),
            ("T2.3: un mapa del módulo 2 pierde su mando de la pregunta", "sin el mando que la enseña"),
            ("T2.3: el capítulo vuelve a escribir en la paleta del motor", "vuelve a escribir en la paleta"),
            ("T2.2: el acento de la plantilla deja de ser el naranja", "el acento de la plantilla ya no es el naranja"),
            ("T2.2: la plantilla pierde el ámbar que se cambia por amarillo", "ya no trae el ámbar"),
            ("T2.2: las estaciones de San Andrés caen dentro del contorno", "se ven sobre el mar"),
            ("T2.2: un par sin estrato deja de acercarse al cero", "ya no «se acercan al cero»"),
            ('T2.2: la banda del marcador vuelve a medirse en píxeles', 'marcador:'),
            ('T2.2: una bomba de Snow se queda sin celda', 'no hay una celda por bomba'),
            ('T2.2: dos bombas de Snow se cambian la celda', 'fuera de la celda de la bomba'),
            ('T2.2: el mapa de Snow vuelve a llevar pie de leyenda', 'pie de leyenda'),
            ('T2.2: la paleta de la plantilla pierde el bermellón', 'ya no es la que el cambio de color'),
            ('T2.2: la paleta de la plantilla ya trae el naranja del acento', 'ya trae el naranja del acento'),
            ('T2.2: la rampa del zinc vuelve a ser lineal', 'ya no recorre el logaritmo'),
            ('T2.2: el Mosa pierde una orilla', 'las dos orillas'),
            ('T2.2: un punto del Mosa se corre diez metros', 'Mosa: la tabla de respaldo'),
            ('T2.2: un pino se corre una centésima', 'japanesepines: la tabla de respaldo'),
            ('T2.2: la rampa de la temperatura deja de ir de oscuro a claro', 'de oscuro a claro'),
            ('T2.2: la plantilla ya trae una paleta termica', 'ya trae una paleta «termica»'),
            ('T2.2: el mapa del IDEAM pierde el contorno', 'no trae el contorno'),
            ('T2.2: las franjas de altitud no suman las estaciones', 'franjas de altitud'),
            ('T2.2: un campo pierde el centro', 'simétrica y centrada en 0'),
            ('T2.2: una realización va con escala propia', 'ya no comparten escala'),
            ('T2.2: el recuento por clase de un campo no suma', '`tam` no reparte'),
            ('T2.2: el campo vuelve a la rejilla de 28', 'ya no va en la retícula de la simulación'),
            ('T2.2: el campo destacado no es la réplica 1', 'ya no es la réplica 1'),
            ('T2.2: el título del campo vuelve a decir «rango»', 'vuelve a llamar «rango»'),
            ('T2.2: la ventana del acercamiento se sale del mapa', 'se sale de la caja'),
            ('T2.2: el acercamiento declara celdas que no son columnas por filas', 'no son columnas por filas'),
            ('T2.2: una celda del caso queda fuera del acercamiento', 'queda fuera del acercamiento'),
            ('T2.2: el porcentaje de rechazos ya no cabe en un decimal', 'ya no cabe en un decimal'),
            ('T2.2: los pares que se alejan del 0 no son los que cuenta R', 'ya no cuentan lo que R publica'),
            ('T2.2: un pliegue se queda sin estaciones', 'no reparte las estaciones en los pliegues'),
            ('T2.2: los bloques del mapa no tienen los tamaños publicados', 'no tienen los tamaños publicados'),
            ('T2.2: la vecina más próxima ya no separa los dos repartos', '«casi nunca» y «casi siempre»'),
            ('T2.2: la barra de los bloques ya no supera la desviación típica', 'ya no supera la desviación típica'),
            ('T2.2: el deslizador de rho pierde el de Colombia', 'ya no salen de la rejilla de R'),
            ('T2.2: el rho de Colombia cae sobre otra posición del deslizador', 'coincide con otra posición'),
            ('T2.2: la cobertura vuelve al lienzo de los errores estándar', 'vuelven a compartir lienzo'),
    ):
        ESPERA[_nombre] = _mensaje

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
    entorno["ESPACIAL_RAIZ"] = str(RAIZ)   # la bibliografía real, no la de la copia
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

    # Los módulos que el ensamblador importa viajan con él, y NO son
    # superficies: no se envenenan, porque no son entrada del capítulo sino
    # parte de la herramienta. Sin esta copia el arnés muere en el control de
    # entrada con un ModuleNotFoundError, que es un rojo que no dice nada del
    # ensamblador. Lo estrenó `baraja_opciones.py` el 2026-09-02; el 2026-11-02 se
    # sumó `describe_mapa.py`, las guardas de «Describir el mapa», y el 2026-11-12 los
    # de la capa de fuentes: el ensamblador escribe las citas con `genera_referencias.genera()`.
    for auxiliar in ("baraja_opciones.py", "pon_boton_indice.py", "describe_mapa.py",
                     "genera_referencias.py", "fuentes_config.py"):
        origen = ENSAMBLADOR.parent / auxiliar
        if not origen.exists():
            print(f"PARADO: falta {origen}")
            return 1
        shutil.copy(origen, tmp / auxiliar)

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
        if cod != 0 and ms and nombre in ESPERA and not any(ESPERA[nombre] in m for m in ms):
            # Paró, pero no la guarda que esta inyección existe para probar.
            colados += 1
            etiqueta = "OTRA"
            print(f"      se esperaba un MAL con «{ESPERA[nombre]}»")
        elif cod != 0 and ms:
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

    # --- LAS GUARDAS DE «DESCRIBIR EL MAPA» (2026-11-02) --------------
    # No son `problemas.append` del inventario —viven en
    # `guardas_de_las_descripciones()` y en `revisa_textos`—, así que el
    # recuento de arriba no las ve. Se rompen aquí una a una, en una copia
    # del ensamblador, y cada copia tiene que parar nombrando el defecto.
    print("\n  «Describir el mapa»: las guardas de las descripciones, rotas de una en una")
    fuente = ENSAMBLADOR.read_text(encoding="utf-8")
    ANTES = "DESCRIPCIONES = {\n"
    MUT_DESC = [
        ("los pinos sin `descripcion` en el registro",
         '''geomapa("cap1-pinos", "japanesepines", tabla=TABLA_PUNTOS,
              extra="      descripcion: " + json.dumps(DESC_PINOS, ensure_ascii=False))''',
         '''geomapa("cap1-pinos", "japanesepines", tabla=TABLA_PUNTOS)''', "no trae `descripcion`"),
        ("la descripción de Bogotá, corta", ANTES, 'DESC_BOGOTA_V["urbano"] = "Corto."\n' + ANTES, "caracteres"),
        ("Snow deja de apiñarse en Broad Street", ANTES, '_SN["pct_mas_cerca_broad"] = 30\n' + ANTES, "Snow:"),
        ("la deserción más alta, en el norte", ANTES, '_DS["mayores"][0]["zona"] = "norte"\n' + ANTES, "deserción:"),
        ("el campo deja de crecer con el alcance", ANTES, 'M["campos"][3]["rho_vecino"] = 0.99\n' + ANTES, "campo:"),
        ("la agregación con dos celdas iguales", ANTES, "_apor[0] = _apor[1]\n" + ANTES, "agregación:"),
        ("las estaciones frías, repartidas", ANTES, '_FR["n"][0] = 10\n' + ANTES, "IDEAM:"),
        ("el zinc alto, del otro lado de la nube", ANTES,
         'M["meuse"]["marcas"] = [-z for z in M["meuse"]["marcas"]]\n' + ANTES, "borde noroeste"),
    ]
    d_colados = 0
    for nombre_m, viejo, nuevo, espera in MUT_DESC:
        if fuente.count(viejo) != 1:
            d_colados += 1
            print(f"  INERTE  «{nombre_m}»: la cadena aparece {fuente.count(viejo)} veces y debía ser 1")
            continue
        copia = tmp / "ensambla_cap1_desc.py"
        copia.write_text(fuente.replace(viejo, nuevo), encoding="utf-8")
        cod_m, sal_m, _ = corre(tmp, copia, dict(limpias))
        linea = next((l.strip() for l in sal_m.splitlines() if espera in l), None)
        if cod_m != 0 and linea:
            print(f"  OK   «{nombre_m}» para el ensamblado: {linea[:84]}")
        else:
            d_colados += 1
            print(f"  MAL  «{nombre_m}» NO para el ensamblado (código {cod_m})")
    igual_html = igual_html and (publicado_antes is None or PUBLICADO.read_bytes() == publicado_antes)

    print("\n" + "=" * 70)
    print(f"  {len(MUT_DESC) - d_colados} de {len(MUT_DESC)} mutantes de las descripciones paran el ensamblado")
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
    ok = (colados == 0 and inertes == 0 and cod == 0 and intactos and igual_html and d_colados == 0)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
