#!/usr/bin/env python3
"""
prueba_auditor_preparcial1.py — le rompe el preparcial al auditor (P1.3)

Material de Estadística Espacial 2026-II (20929). Ver PLAN_Preparcial_Corte_1.md.

POR QUÉ EXISTE. `audita_preparcial1.py` informó **112 comprobaciones, 0
fallos** el día que nació, y ese número no significa nada por sí solo: un
auditor cuyo silencio no se ha interrogado no es un auditor verificado.
Es la lección de `A.3` del plan del material, y este proyecto ya la pagó
—cinco auditores de DOE que jamás miraron dentro de KaTeX, y dos
comprobaciones de T0.5 que eran **incapaces de fallar**—.

Y ahora hay mucho que proteger: el auditor encontró dos defectos de
contenido el día que nació (§12.6) y P3.0 encontró treinta y dos más.

LO QUE ESTE ARNÉS TIENE DE PROPIO, y por qué no se parece al del taller:

  **Tres superficies, no una.** El JSON del preparcial, el HTML con las 36
  preguntas y la carpeta de los capítulos. Las familias 3, 4 y 5 solo se
  pueden romper tocando el HTML —las preguntas no están en el JSON—, y la
  familia 2 solo se rompe DE VERDAD moviendo un capítulo: la
  desincronización que existe en la realidad (§12.4) no la provoca este
  documento, la provoca que un capítulo se regenere debajo. Envenenar el
  preparcial prueba esa familia por el lado que nunca falla solo.

  **Las inyecciones del HTML son sobre texto.** Las preguntas viajan como
  literales de JavaScript, no como JSON, así que se sustituyen cadenas.

LAS DOS REGLAS DEL ARNÉS, heredadas de `prueba_auditor_taller1.py`:

  1. Cada tanda empieza y acaba con un CONTROL sin inyectar nada. Si el
     auditor no sale limpio sobre el original, cualquier «acierto»
     posterior es falso.
  2. «N de N» no basta: se cuenta también cuántas comprobaciones
     DISTINTAS se han visto fallar alguna vez, que es lo que destapa una
     familia entera incapaz de fallar.

  Y una tercera, la trampa de `A.3`: **ninguna inyección puede ser
  inerte**. Si la mutación no cambia el archivo, el arnés lo dice y no
  cuenta el acierto — un «no detectado» que es culpa del arnés y no del
  auditor se distingue de uno que sí lo es.

Uso:  python3 precalculo/prueba_auditor_preparcial1.py
Devuelve 1 si algún defecto se cuela.
"""
from __future__ import annotations

import json
import math
import os
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile

RAIZ = pathlib.Path(__file__).resolve().parent.parent
PRECALCULO = RAIZ / "precalculo"
SALIDAS = PRECALCULO / "salidas"
HTMLS = RAIZ / "Htmls_Espacial"
AUDITOR = PRECALCULO / "audita_preparcial1.py"

DATOS = SALIDAS / "preparcial1_datos.json"
HTML = HTMLS / "preparcial-corte-1.html"
CAPS = ["cap1_datos.json", "cap2_datos.json", "cap3_datos.json"]

# El intérprete de geo_env: el auditor necesita geopandas, pyproj y
# mapclassify. Se lee de versiones_py.json en vez de darse por sabido.
PY = json.loads((PRECALCULO / "versiones_py.json").read_text(
    encoding="utf-8"))["ejecutable"]

# Comprobaciones que este arnés NO PUEDE atacar, y no es una laguna:
# contrastan una fuente primaria contra otra —el CSV contra el
# GeoPackage, numpy contra mapclassify— sin que el JSON del preparcial
# intervenga. Envenenar el JSON no las mueve, y romperlas exigiría tocar
# las fuentes, que es justo lo que un arnés no debe hacer. Se listan
# aparte para no contarlas como deuda ni esconderlas como cubiertas.
# La primera versión de esta lista tenía CINCO entradas, y cuatro estaban
# mal: «los condados del CSV» compara el CSV contra `N3["n"]`, que sí está
# en el JSON, y lo mismo las otras tres. Ponerlas aquí sin comprobarlo las
# escondía como cubiertas — que es exactamente lo que esta lista existe
# para no hacer. Queda una, y ésa sí: compara el CSV contra el GeoPackage
# fila a fila, sin que el JSON intervenga en ningún lado.
SOLO_FUENTES = {
    "N4: el CSV es el GeoPackage redondeado, fila a fila",
}

# Y una segunda lista, por un motivo distinto: estas dos no se pueden
# atacar por como están escritas, no por dónde viven.
FUERA_DE_ALCANCE = {
    # Resuelve el `<template id="module-N">` dentro del HTML del CAPÍTULO,
    # que no está detrás de ninguna de las tres variables de entorno.
    # Romperla exigiría escribir en Htmls_Espacial/.
    "y cada destino existe en su capítulo",
}

# Y una tercera, que es una observación sobre el auditor y no sobre este
# arnés: hay una comprobación cuyo NOMBRE lleva dentro la cifra que mide
# —«hay 36 preguntas publicadas en 4 bloques»—. Si la cifra cambia, cambia
# el nombre, así que jamás puede verse fallar BAJO EL MISMO NOMBRE; y su
# condición es `total > 0`, que solo es falsa cuando ya ha explotado todo
# lo demás. Queda dicho: no es una laguna del arnés, es una comprobación
# que casi no puede fallar.
NOMBRE_VARIABLE = re.compile(r"^hay \d+ preguntas publicadas en \d+ bloques$")

# El radio con el que se construye la columna esférica de comparación. El
# de s2 es 6 371 010,0; el MEDIO del WGS84 —(2a+b)/3— es 6 371 008,8, y es
# «la respuesta que parece» (§12.6). Una de las comprobaciones del auditor
# exige que el medio NO reproduzca la columna, y para atacarla hay que
# construir esa columna con él.
RADIO_MEDIO_WGS84 = 6371008.8


def esfera(radio: float, lat: float) -> float:
    """Un grado de longitud sobre una esfera, en metros.

    Geodésica entre (0, lat) y (1, lat): 2R·asin(cos φ · sen(Δλ/2)). Con
    el radio de s2 reproduce la columna publicada a 5·10⁻¹¹ m, así que la
    fórmula es la buena y lo que se inyecta es el radio.
    """
    dl = math.radians(1.0)
    return radio * 2 * math.asin(math.cos(math.radians(lat)) * math.sin(dl / 2))


def defectos() -> list[tuple[str, str, str, object]]:
    """(nombre, destino, tipo, acción).

    destino ∈ {'datos', 'html', 'cap1_datos.json', 'cap2_datos.json',
               'cap3_datos.json'}
    tipo    ∈ {'obj', 'txt'} — mutar el objeto JSON, o sustituir texto.
    """
    D: list[tuple[str, str, str, object]] = []

    def obj(nombre, destino, f):
        D.append((nombre, destino, "obj", f))

    def txt(nombre, destino, busca, pone):
        D.append((nombre, destino, "txt", (busca, pone)))

    def fn(nombre, destino, f):
        """Para lo que no cabe en una sustitución: f(texto) -> texto."""
        D.append((nombre, destino, "fn", f))

    # =================================================================
    # FAMILIA 0 · Formato: sin NaN, con holgura, sin mojibake
    # =================================================================
    txt("un NaN escondido en el precálculo", "datos",
        '"graficos"', '"colado": NaN, "graficos"')
    txt("un infinito escondido en el precálculo", "datos",
        '"errores"', '"colado": Infinity, "errores"')
    obj("un flotante con más precisión de la escrita", "datos",
        lambda o: o["nuevo"]["n_efectivo"].__setitem__(
            "correcto", 64.52154543321234567))
    obj("una tilde rota se cuela en una cadena reutilizada", "datos",
        lambda o: o["reutilizado"]["snow_pct_broad"].__setitem__(
            "que", "Porcentaje de muertes en Bogot<U+00E1>"))
    obj("meta miente sobre cuántas cifras reutiliza", "datos",
        lambda o: o["meta"].__setitem__("n_reutilizadas", 999))
    obj("meta miente sobre cuántos cálculos nuevos hay", "datos",
        lambda o: o["meta"].__setitem__("n_nuevas", 7))
    obj("meta miente sobre cuántos errores cataloga", "datos",
        lambda o: o["meta"].__setitem__("n_errores", 12))
    obj("el alcance que declara meta deja de ser el del contrato", "datos",
        lambda o: o["meta"]["alcance"].append("cap3.m9"))
    obj("meta miente sobre cuántos gráficos hay", "datos",
        lambda o: o["meta"].__setitem__("n_graficos", 3))
    obj("meta miente sobre el tamaño del alcance", "datos",
        lambda o: o["meta"].__setitem__("n_modulos_alcance", 27))
    obj("la fecha del parcial deja de ser una fecha", "datos",
        lambda o: o["meta"].__setitem__("fecha_parcial", "el martes que viene"))

    # =================================================================
    # FAMILIA 1 · Las cuatro cifras nuevas, desde la fuente primaria.
    # Se envenena el JSON y el auditor lo recalcula con pandas, pyproj y
    # mapclassify: son los dos caminos que tienen que coincidir.
    # =================================================================
    obj("N1: el n efectivo publicado deja de ser n/(1+(n-1)rho)", "datos",
        lambda o: o["nuevo"]["n_efectivo"].__setitem__("correcto", 71.4321))
    obj("N1: los municipios con deserción dejan de ser los que cuenta pandas", "datos",
        lambda o: o["nuevo"]["n_efectivo"].__setitem__("n", 1097))
    obj("N1: el distractor de la resta lineal se mueve", "datos",
        lambda o: o["nuevo"]["n_efectivo"]["distractores"][0].__setitem__(
            "valor", 1101.2345678901))
    obj("N1: dos distractores dejan de distinguirse a 2 decimales", "datos",
        lambda o: o["nuevo"]["n_efectivo"]["distractores"][1].__setitem__(
            "valor", o["nuevo"]["n_efectivo"]["correcto"] + 0.001))
    obj("N2: el grado de longitud deja de ser el que da pyproj", "datos",
        lambda o: o["nuevo"]["grado_longitud"].__setitem__(
            "correcto", 110123.4567891011))
    obj("N2: lo que s2 se queda corto cambia de signo", "datos",
        lambda o: o["nuevo"]["grado_longitud"].__setitem__(
            "dif_s2_m", -o["nuevo"]["grado_longitud"]["dif_s2_m"]))
    obj("N2: el distractor de la esfera deja de ser el de s2", "datos",
        lambda o: o["nuevo"]["grado_longitud"]["distractores"][0].__setitem__(
            "valor", 110777.7777777777))
    obj("N3: los cortes dejan de ser los del capítulo 3", "datos",
        lambda o: o["nuevo"]["convenio_intervalo"].__setitem__(
            "cortes", [0, 2, 4, 5, 10, 44]))
    obj("N3: el reparto con [a, b) deja de ser el que rehace numpy", "datos",
        lambda o: o["nuevo"]["convenio_intervalo"].__setitem__(
            "tam_r", [14, 24, 13, 26, 23]))
    obj("N3: los condados que mueve el convenio dejan de ser 24-13", "datos",
        lambda o: o["nuevo"]["convenio_intervalo"].__setitem__("movidos_primera", 9))
    obj("N4: los pares de estaciones dejan de ser n(n-1)/2", "datos",
        lambda o: o["nuevo"]["euclidea_grados"].__setitem__("n_pares", 64979))
    obj("N4: el error medio deja de ser el que da pyproj", "datos",
        lambda o: o["nuevo"]["euclidea_grados"].__setitem__(
            "error_med_pct", 0.7123456789))
    obj("N4: el método ingenuo deja de pasarse en TODOS los pares", "datos",
        lambda o: o["nuevo"]["euclidea_grados"].__setitem__("pct_sobreestima", 97))
    obj("N1: la nota del n pequeño con (n-1) se mueve", "datos",
        lambda o: o["nuevo"]["n_efectivo"]["nota_n_menos_1"].__setitem__(
            "con_n_menos_1_25", 19.8765432109))
    obj("N1: la nota del n pequeño con n se mueve", "datos",
        lambda o: o["nuevo"]["n_efectivo"]["nota_n_menos_1"].__setitem__(
            "con_n_25", 21.1234567890))
    obj("N2: el distractor que olvida el coseno se mueve", "datos",
        lambda o: o["nuevo"]["grado_longitud"]["distractores"][1].__setitem__(
            "valor", 111444.5555666677))
    obj("N2: el distractor del radio meridional se mueve", "datos",
        lambda o: o["nuevo"]["grado_longitud"]["distractores"][2].__setitem__(
            "valor", 109888.7777666655))
    obj("N2: dos distractores dejan de distinguirse a 1 decimal", "datos",
        lambda o: o["nuevo"]["grado_longitud"]["distractores"][2].__setitem__(
            "valor", o["nuevo"]["grado_longitud"]["distractores"][1]["valor"] + 0.01))
    obj("N2: el arco de paralelo de la nota se mueve", "datos",
        lambda o: o["nuevo"]["grado_longitud"]["nota_arco"].__setitem__(
            "valor", 110950.1234567891))
    obj("N2: lo que el arco se separa de la geodésica deja de cuadrar", "datos",
        lambda o: o["nuevo"]["grado_longitud"]["nota_arco"].__setitem__(
            "dif_m", 0.0777888999))
    obj("N3: el reparto de R deja de sumar los 100 condados", "datos",
        lambda o: o["nuevo"]["convenio_intervalo"].__setitem__(
            "tam_r", [13, 25, 13, 26, 22]))
    obj("N3: el reparto de Python deja de sumar los 100 condados", "datos",
        lambda o: o["nuevo"]["convenio_intervalo"].__setitem__(
            "tam_python", [24, 27, 11, 19, 18]))
    obj("N4: el error del peor par se mueve", "datos",
        lambda o: o["nuevo"]["euclidea_grados"].__setitem__(
            "error_max_pct", 3.1234567891))
    obj("N4: el error del mejor par se mueve", "datos",
        lambda o: o["nuevo"]["euclidea_grados"].__setitem__(
            "error_min_pct", 0.0212345678))
    obj("N4: la geodésica del peor par se mueve", "datos",
        lambda o: o["nuevo"]["euclidea_grados"]["peor_par"].__setitem__(
            "d_geodesica_km", 1099.8765432109))
    obj("N4: lo que el método ingenuo atribuye al peor par se mueve", "datos",
        lambda o: o["nuevo"]["euclidea_grados"]["peor_par"].__setitem__(
            "d_ingenua_km", 1077.1234567890))
    obj("N4: el peor par deja de ser el que encuentra pyproj", "datos",
        lambda o: o["nuevo"]["euclidea_grados"]["peor_par"].__setitem__("a", 7))
    obj("N4: los km por grado dejan de ser los del capítulo 2", "datos",
        lambda o: o["nuevo"]["euclidea_grados"].__setitem__(
            "km_por_grado", 111.9876543210))
    obj("N4: la segunda estación del peor par deja de serlo", "datos",
        lambda o: o["nuevo"]["euclidea_grados"]["peor_par"].__setitem__("b", 99))
    obj("N3: los condados que declara el cálculo dejan de ser los del CSV", "datos",
        lambda o: o["nuevo"]["convenio_intervalo"].__setitem__("n", 97))
    obj("N4: las estaciones que declara el cálculo dejan de ser las del CSV", "datos",
        lambda o: o["nuevo"]["euclidea_grados"].__setitem__("n_estaciones", 358))
    # La columna esférica NO se lee del capítulo: se lee de la copia que el
    # preparcial guarda en `reutilizado`. Por eso envenenar cap2 dispara la
    # familia 2 y no ésta, y hacen falta las dos inyecciones.
    obj("la copia de la columna esférica deja de ser la que da s2", "datos",
        lambda o: o["reutilizado"]["grad_lon_esfera"]["valor"].__setitem__(
            4, 96500.123456789))
    obj("la copia de la columna elipsoidal deja de ser la que da pyproj", "datos",
        lambda o: o["reutilizado"]["grad_lon_elip"]["valor"].__setitem__(
            6, 79000.987654321))
    obj("N1: el (n-1) deja de pesar más con n pequeño", "datos",
        lambda o: o["nuevo"]["n_efectivo"]["nota_n_menos_1"].__setitem__(
            "con_n_25", o["nuevo"]["n_efectivo"]["nota_n_menos_1"]["con_n_menos_1_25"]
            + 0.001))
    obj("el gráfico del grado deja de dibujar la columna del capítulo 2", "datos",
        lambda o: o["graficos"]["g_grado"]["elipsoide"].__setitem__(
            2, 108000.135792468))
    obj("un módulo del alcance se queda sin ninguna cifra", "datos",
        lambda o: [o["reutilizado"][k].__setitem__("modulo", 1)
                   for k in ("eco_gdal", "eco_geos", "eco_proj")])

    # =================================================================
    # FAMILIA 2 · Sincronía. La mitad importante NO se prueba envenenando
    # el preparcial: se prueba moviendo el CAPÍTULO debajo, que es la
    # forma que el defecto tiene en la realidad (§12.4).
    # =================================================================
    obj("el capítulo 1 mueve una cifra que el preparcial cita", "cap1_datos.json",
        lambda o: o["snow"].__setitem__("pct_mas_cerca_broad", 59.4321098765))
    obj("el capítulo 2 mueve una razón de tamaño de archivo", "cap2_datos.json",
        lambda o: o["formatos"]["gpkg"].__setitem__("razon_sobre_shp", 1.2345678901))
    obj("el capítulo 3 mueve la correlación del efecto escala", "cap3_datos.json",
        lambda o: o["m8"].__setitem__("r_departamento", 0.4987654321))
    obj("el capítulo 1 mueve un elemento de un vector citado", "cap1_datos.json",
        lambda o: o["tobler"]["ideam"]["bandas"][0].__setitem__("I", 0.7123456789))
    obj("una ruta desaparece del capítulo del que salía", "cap1_datos.json",
        lambda o: o["snow"].pop("razon_sobre_uniforme"))
    obj("una cifra reutilizada apunta a una ruta que no existe", "datos",
        lambda o: o["reutilizado"]["snow_muertes"].__setitem__(
            "ruta", "snow.n_muertes_inventado"))
    obj("una cifra reutilizada se queda sin capítulo", "datos",
        lambda o: o["reutilizado"]["ce_redwood"].__setitem__("doc", "cap9"))
    obj("una cifra reutilizada habla de un módulo fuera del alcance", "datos",
        lambda o: o["reutilizado"]["c3m1_pct"].__setitem__("modulo", 10))
    obj("una cifra reutilizada se queda sin pie que la explique", "datos",
        lambda o: o["reutilizado"]["neff_pct"].__setitem__("que", ""))
    obj("un gráfico mezcla series de largos distintos", "datos",
        lambda o: o["graficos"]["g_cobertura"].__setitem__(
            "cobertura", o["graficos"]["g_cobertura"]["cobertura"][:5]))
    obj("un gráfico habla de un módulo fuera del alcance", "datos",
        lambda o: o["graficos"]["g_escala"].__setitem__("modulo", "cap3.m11"))
    obj("la curva del efecto escala deja de ser la del capítulo 3", "datos",
        lambda o: o["graficos"]["g_escala"]["media"].__setitem__(0, 0.4123456789))
    obj("un error del catálogo cita una clave que no existe", "datos",
        lambda o: o["errores"][0]["claves"].append("clave_inventada"))
    obj("el capítulo 2 mueve la columna esférica que s2 tiene que reproducir",
        "cap2_datos.json",
        lambda o: o["grados"]["lon_m_esfera"].__setitem__(3, 104000.123456789))
    obj("el capítulo 2 mueve la columna elipsoidal que pyproj reproduce",
        "cap2_datos.json",
        lambda o: o["grados"]["lon_m_elipsoide"].__setitem__(5, 85000.987654321))
    obj("el capítulo 3 mueve un par del gráfico de discordancia", "cap3_datos.json",
        lambda o: o["m4"]["pares"][0].__setitem__("pct_cambian", 44.4444444444))
    # El HTML incrusta su propia copia del JSON. Regenerar el precálculo y
    # no reensamblar deja esa copia atrás, que es lo que pasó el 2026-08-25
    # (§12.4). Se ataca la copia INCRUSTADA, no la prosa: una cifra mal
    # escrita en un enunciado es otra comprobación, y la escribe P3.1.
    txt("el HTML lleva un precálculo anterior al del JSON", "html",
        'const DATOS_PRE1 = {"meta": {"documento": "preparcial-corte-1"',
        'const DATOS_PRE1 = {"meta": {"documento": "preparcial-corte-0"')

    # =================================================================
    # FAMILIA 3 · Cobertura: los 30 módulos, y el repaso resuelto.
    # Solo se puede romper tocando el HTML: las preguntas no están en el
    # JSON.
    # =================================================================
    txt("una pregunta desaparece del bloque A", "html",
        '        tipo: "opcion",\n        repaso: { etiqueta: "Cap. 1 · módulo 11',
        '        tipo: "opcion",\n        BORRADA: { etiqueta: "Cap. 1 · módulo 11')
    txt("una pregunta manda a repasar un módulo fuera del alcance", "html",
        'etiqueta: "Cap. 3 · módulo 8 — MAUP I · el efecto escala", href: '
        '"capitulo-3-cartografia-maup.html" },\n        pregunta: "El gráfico traza la '
        'correlación media',
        'etiqueta: "Cap. 3 · módulo 10 — La falacia ecológica", href: '
        '"capitulo-3-cartografia-maup.html" },\n        pregunta: "El gráfico traza la '
        'correlación media')
    txt("el rótulo del repaso deja de ser el título que publica el capítulo", "html",
        'etiqueta: "Cap. 1 · módulo 5 — Tamaño de muestra efectivo"',
        'etiqueta: "Cap. 1 · módulo 5 — Tamaño de muestra aproximado"')
    txt("el enlace del repaso lleva a otro capítulo", "html",
        'etiqueta: "Cap. 2 · módulo 6 — Medir sobre la Tierra", href: "capitulo-2-crs-georreferenciacion.html"',
        'etiqueta: "Cap. 2 · módulo 6 — Medir sobre la Tierra", href: "capitulo-4-patrones-puntuales.html"')
    txt("dos preguntas del bloque B caen en el mismo módulo", "html",
        'etiqueta: "Cap. 2 · módulo 9 — Error posicional, y quién lo paga", href: '
        '"capitulo-2-crs-georreferenciacion.html" },\n        pregunta: "Geocodificando',
        'etiqueta: "Cap. 2 · módulo 8 — De un CSV a un objeto sf", href: '
        '"capitulo-2-crs-georreferenciacion.html" },\n        pregunta: "Geocodificando')
    # D5 es la ÚNICA pregunta del bloque D que apunta al capítulo 3. La
    # primera versión de esta inyección movía D3, y no quitaba nada: cap2
    # seguía cubierto por D4 y D6, así que el bloque seguía cruzando los
    # tres. Una inyección que cambia el archivo y no mueve la comprobación
    # es tan inútil como una inerte, y más difícil de ver.
    # La comprobación cuenta las marcas «\n + ocho espacios + tipo: » y las
    # compara con lo que devuelve el analizador. Un `tipo:` dentro de una
    # cadena no la mueve —lo probó la primera versión de esta inyección—:
    # tiene que ir donde el analizador NO mire y el contador SÍ, y ese
    # sitio es el cuerpo del `dibujar`, que `_opaco()` se salta entero.
    txt("un `tipo:` de más despista al analizador de preguntas", "html",
        "dibujar: canvas => {\n            const g = DATOS_PRE1.graficos.g_cobertura;",
        "dibujar: canvas => {\n        tipo: 0,\n            const g = "
        "DATOS_PRE1.graficos.g_cobertura;")
    txt("un cuestionario registrado se queda sin su contenedor", "html",
        'data-quiz="bloque-c"', 'data-quiz="bloque-inventado"')
    txt("una tilde rota llega al HTML publicado", "html",
        "Reconocer, en el enunciado", "Reconocer, en el enunci<U+00E1>do")
    # La comprobación que faltaba —«y cada destino existe en su capítulo»—
    # resuelve el `<template id="module-N">` dentro del HTML del CAPÍTULO,
    # que no está detrás de ninguna de las tres variables de entorno. No se
    # puede atacar sin escribir en `Htmls_Espacial/`, que es justo lo que un
    # arnés no debe hacer. Va a FUERA_DE_ALCANCE, comprobado y no supuesto.
    obj("la columna esférica pasa a ser la del radio MEDIO del WGS84", "datos",
        lambda o: o["reutilizado"]["grad_lon_esfera"].__setitem__(
            "valor", [esfera(RADIO_MEDIO_WGS84, la)
                      for la in o["reutilizado"]["grad_lat"]["valor"]]))
    fn("una pregunta desaparece del bloque A de verdad", "html", borra_una_pregunta)
    # La comprobación exige DOS capítulos o más, así que quitar uno solo no
    # la mueve. Ésta costó dos intentos: primero se movió D3 —y cap2 seguía
    # cubierto por D4 y D6—, luego D5 —y quedaban cap1 y cap2, que ya
    # bastan—. Hay que dejar el bloque en UN capítulo, y eso son cinco
    # repasos, no uno. La lección cabe en una línea: cambiar el archivo no
    # es mover la comprobación.
    fn("el bloque D deja de cruzar capítulos", "html", bloque_d_a_un_capitulo)

    # =================================================================
    # FAMILIA 4 · Retroalimentación completa, y las correctas que toca
    # =================================================================
    txt("una opción se queda sin retroalimentación", "html",
        'retro: "Confunde «bomba más cercana» con «bomba usada».',
        'retro: "", basura: "Confunde «bomba más cercana» con «bomba usada».')
    txt("dos hermanas comparten la misma retroalimentación", "html",
        'retro: "La proximidad no es exposición.',
        'retro: "Confunde «bomba más cercana» con «bomba usada». El mapa mide distancias, no conductas: es la primera traducción que hay que negarse a hacer." , sobra: "La proximidad no es exposición.')
    txt("una pregunta de opción única se queda con dos correctas", "html",
        '{ texto: "Que el agua de esa bomba causó los casos.", correcta: false,',
        '{ texto: "Que el agua de esa bomba causó los casos.", correcta: true,')
    txt("una pregunta de opción única se queda sin ninguna correcta", "html",
        '{ texto: "Que la distribución de las muertes no es compatible con trece bombas intercambiables.", correcta: true,',
        '{ texto: "Que la distribución de las muertes no es compatible con trece bombas intercambiables.", correcta: false,')
    txt("una «varias respuestas» se queda con una sola correcta", "html",
        '{ texto: "Un valor por debajo de 1 indica agregación.", correcta: true,',
        '{ texto: "Un valor por debajo de 1 indica agregación.", correcta: false,')
    txt("un bloque pierde uno de los cuatro tipos", "html",
        '        tipo: "grafico",\n        repaso: { etiqueta: "Cap. 1 · módulo 4',
        '        tipo: "opcion",\n        repaso: { etiqueta: "Cap. 1 · módulo 4')
    txt("un bloque se inventa un tipo que el motor no sabe pintar", "html",
        '        tipo: "numerica",\n        repaso: { etiqueta: "Cap. 1 · módulo 5',
        '        tipo: "abierta",\n        repaso: { etiqueta: "Cap. 1 · módulo 5')

    # =================================================================
    # FAMILIA 5 · No filtración: ni el enunciado, ni la pista, ni la
    # posición. La última nació de un defecto real (§12.6).
    # =================================================================
    txt("el enunciado copia literalmente el texto de su opción correcta", "html",
        'pista: "Distingue entre lo que el patrón descarta y lo que el patrón explica."',
        'pista: "Recuerda: Que la distribución de las muertes no es compatible con trece bombas intercambiables."')
    txt("una retroalimentación nombra una posición", "html",
        'retro: "Los vecinos están más cerca de lo que la aleatoriedad predice',
        'retro: "Las correctas son las dos primeras. Los vecinos están más cerca de lo que la aleatoriedad predice')
    txt("una pista nombra la opción por su letra", "html",
        'pista: "R compara la distancia media al vecino más cercano con la esperada bajo CSR. Son dos."',
        'pista: "Mira la opción c) y la opción d): son dos."')
    txt("un retroFallo nombra una posición", "html",
        'retroFallo: "Se sostienen la lectura del valor por debajo de 1',
        'retroFallo: "Se sostienen las dos primeras. La lectura del valor por debajo de 1')
    # Ésta no cabe en una sustitución: hay que REORDENAR las opciones de
    # once preguntas. Y es la inyección que más importa del arnés, porque
    # reproduce un defecto que ocurrió de verdad: escritas de una en una,
    # las 29 preguntas con opciones tenían la correcta la primera y el
    # preparcial se aprobaba marcando siempre la (a) (§12.6). Las cinco
    # familias que ya había miraban UNA pregunta, y ninguna podía verlo.
    fn("la correcta vuelve a caer la primera en las 22 de respuesta única",
       "html", correcta_delante)

    return D


def correcta_delante(texto: str) -> str:
    """Reordena cada pregunta para que su opción correcta salga la primera.

    El defecto de §12.6 en estado puro. Se reconstruye el bloque
    `opciones: [...]` de cada pregunta poniendo delante la que lleva
    `correcta: true`, sin tocar ninguna otra cosa: siguen siendo las
    mismas opciones, con las mismas retroalimentaciones y una sola
    correcta, así que las cinco familias que miran UNA pregunta la dan
    por buena. Solo la sexta —la que mira el montón— puede verlo.

    El cierre del bloque se ancla a SU SANGRÍA —ocho espacios y `]`— y no
    al primer `]` que aparezca: la retro de C3 contiene «[a, b)» y «(a,
    b]», y una expresión perezosa cortaba ahí y dejaba JavaScript roto.
    El auditor entonces reventaba al analizar, que es «cazar» el defecto
    por el camino equivocado: un arnés que confunde un fallo del
    analizador con la comprobación que quería probar no prueba nada.
    """
    ABRE = "opciones: [\n"
    CIERRA = "\n        ]"

    def una(m: re.Match) -> str:
        opciones = re.split(r"\n(?=          \{ texto: )", m.group(1))
        # Cada opción arrastra la coma que la separa de la siguiente, y la
        # última NO la lleva. Reordenar sin normalizar deja a la última en
        # medio, sin coma, y el JavaScript se rompe: el auditor entonces
        # muere al analizar en vez de informar del defecto, que es «cazarlo»
        # por el camino equivocado.
        opciones = [o.rstrip().rstrip(",") for o in opciones]
        buenas = [o for o in opciones if "correcta: true" in o]
        malas = [o for o in opciones if "correcta: true" not in o]
        if not buenas or not malas:
            return m.group(0)
        return ABRE + ",\n".join(buenas + malas) + CIERRA

    return re.sub(re.escape(ABRE) + r"(.*?)" + re.escape(CIERRA),
                  una, texto, flags=re.S)


def borra_una_pregunta(texto: str) -> str:
    """Quita entera la última pregunta del bloque A.

    Renombrar una clave no basta: la pregunta sigue ahí y el recuento no
    se mueve. Hay que borrar el objeto completo, y el corte se hace en la
    coma que separa dos preguntas —seis espacios, llave— porque es el
    único sitio donde la estructura es inequívoca.
    """
    abre = "AUTOEVALUACIONES['bloque-a'] = ["
    i = texto.index(abre)
    j = texto.index("\n    ];", i)
    cuerpo = texto[i + len(abre):j]
    corte = cuerpo.rindex("\n      },\n      {")
    return texto[:i + len(abre)] + cuerpo[:corte] + "\n      }" + texto[j:]


def bloque_d_a_un_capitulo(texto: str) -> str:
    """Deja todo el bloque D apuntando al mismo capítulo.

    Los cinco módulos que se reescriben están cubiertos además por su
    bloque propio —A2, A6, B9, B11 y C8—, así que la cobertura de los 30
    no se mueve y la única comprobación que puede caer es la que mira si
    el bloque de integración integra algo.
    """
    abre = "AUTOEVALUACIONES['bloque-d'] = ["
    i = texto.index(abre)
    j = texto.index("\n    ];", i)
    destino = ('etiqueta: "Cap. 2 · módulo 2 — Latitud y longitud no son cartesianas", '
               'href: "capitulo-2-crs-georreferenciacion.html"')
    cuerpo = re.sub(r'etiqueta: "Cap\. [123] · módulo \d+ — [^"]*", href: "[^"]*"',
                    destino, texto[i:j])
    return texto[:i] + cuerpo + texto[j:]

# =====================================================================
# EL BANCO DE PRUEBAS
#
# Todo ocurre sobre copias en un directorio temporal. Los cinco
# publicados —el JSON, el HTML y los tres capítulos— se leen al arrancar
# y se comprueban byte a byte al terminar: si el arnés escribiera sobre
# lo publicado, dejaría el sitio con un defecto inyectado dentro.
# =====================================================================
def corre(datos: pathlib.Path, html: pathlib.Path,
          caps: pathlib.Path) -> tuple[int, str]:
    entorno = dict(os.environ)
    entorno["PREPARCIAL1_DATOS"] = str(datos)
    entorno["PREPARCIAL1_HTML"] = str(html)
    entorno["PREPARCIAL1_CAPS"] = str(caps)
    res = subprocess.run([PY, str(AUDITOR)], capture_output=True, text=True,
                         cwd=str(RAIZ), env=entorno)
    return res.returncode, res.stdout + res.stderr


def resumen(salida: str) -> str:
    m = re.search(r"(\d+) comprobaciones · (\d+) fallos", salida)
    if m:
        return m.group(0)
    for linea in salida.strip().splitlines()[::-1]:
        if linea.strip().startswith(("PARADO", "ValueError", "KeyError")):
            return "REVENTÓ · " + linea.strip()[:80]
    return "(sin resumen — el auditor ni siquiera llegó al cierre)"


def revento(salida: str) -> bool:
    """Distingue «el auditor informó de un fallo» de «el auditor murió».

    Las dos cosas devuelven código distinto de cero y desde fuera se ven
    igual, y no son lo mismo: un analizador que revienta ante un HTML
    malformado no prueba que la comprobación que se quería atacar
    funcione. Este arnés ya se dejó engañar una vez —el reordenador de
    opciones producía JavaScript roto y el auditor moría al analizarlo—,
    y por eso ahora se comprueba.
    """
    return "Traceback (most recent call last)" in salida


def nombres(salida: str, estado: str) -> set[str]:
    fuera = set()
    for linea in salida.splitlines():
        m = re.match(r"\s{2}" + re.escape(estado) + r"\s{2,}(\S.*?)\s{2,}", linea + "  ")
        if m:
            fuera.add(m.group(1).strip())
    return fuera


def main() -> int:  # noqa: C901
    faltan = [p for p in [DATOS, HTML] + [SALIDAS / c for c in CAPS]
              if not p.exists()]
    if faltan:
        print("PARADO: faltan archivos publicados:")
        for p in faltan:
            print(f"        {p}")
        print("        Ejecuta antes precalculo/rscript.sh precalculo/"
              "genera_preparcial1.R y precalculo/ensambla_preparcial1.py")
        return 1

    originales = {p: p.read_bytes() for p in [DATOS, HTML] + [SALIDAS / c for c in CAPS]}

    tmp = pathlib.Path(tempfile.mkdtemp(prefix="prueba_auditor_preparcial1_"))
    limpio_datos, limpio_html = tmp / DATOS.name, tmp / HTML.name
    limpio_caps = tmp / "caps"
    limpio_caps.mkdir()
    shutil.copy(DATOS, limpio_datos)
    shutil.copy(HTML, limpio_html)
    for c in CAPS:
        shutil.copy(SALIDAS / c, limpio_caps / c)

    print("=" * 74)
    print("  prueba_auditor_preparcial1.py — el arnés de inyección del preparcial")
    print("=" * 74)
    print("  los publicados no se tocan: se comprueba byte a byte al cerrar")

    codigo, salida = corre(limpio_datos, limpio_html, limpio_caps)
    print(f"\n  {'OK ' if codigo == 0 else 'MAL'}  control de entrada · sin inyectar nada")
    print(f"        {resumen(salida)}")
    if codigo != 0:
        print("\n  PARADO: el control falla, así que el arnés no prueba nada.")
        for linea in salida.strip().splitlines():
            if linea.strip().startswith(("MAL", "- ")):
                print(f"        {linea.strip()}")
        return 1

    todas = nombres(salida, "OK ")
    vistas_fallar: set[str] = set()

    lista = defectos()
    cazados = inertes = reventados = 0
    print(f"\n  {len(lista)} defectos que inyectar\n" + "-" * 74)

    for nombre_d, destino, tipo, accion in lista:
        datos_r, html_r, caps_r = limpio_datos, limpio_html, limpio_caps

        if destino in ("datos", "html"):
            origen = limpio_datos if destino == "datos" else limpio_html
            roto = tmp / f"roto_{origen.name}"
        else:
            caps_r = tmp / "caps_rotos"
            if caps_r.exists():
                shutil.rmtree(caps_r)
            shutil.copytree(limpio_caps, caps_r)
            origen = roto = caps_r / destino

        if tipo == "obj":
            o = json.loads(origen.read_text(encoding="utf-8"))
            antes = json.dumps(o, ensure_ascii=False, sort_keys=True)
            accion(o)
            if json.dumps(o, ensure_ascii=False, sort_keys=True) == antes:
                # La trampa de A.3. Una inyección inerte registraría un
                # «no detectado» que es culpa del arnés y no del auditor,
                # y las dos cosas se ven igual si no se dicen.
                print(f"  MAL  {nombre_d}\n        INERTE · la mutación no cambió el archivo")
                inertes += 1
                continue
            roto.write_text(json.dumps(o, ensure_ascii=False, indent=1), encoding="utf-8")
        else:
            t = origen.read_text(encoding="utf-8")
            if tipo == "txt":
                busca, pone = accion
                if busca not in t:
                    print(f"  MAL  {nombre_d}\n        INERTE · no aparece el texto: "
                          f"{busca[:52]!r}")
                    inertes += 1
                    continue
                nuevo = t.replace(busca, pone, 1)
            else:
                nuevo = accion(t)
            if nuevo == t:
                print(f"  MAL  {nombre_d}\n        INERTE · la sustitución no cambió nada")
                inertes += 1
                continue
            roto.write_text(nuevo, encoding="utf-8")

        if destino == "datos":
            datos_r = roto
        elif destino == "html":
            html_r = roto

        codigo, salida = corre(datos_r, html_r, caps_r)
        murio = revento(salida)
        ok = codigo != 0 and not murio
        cazados += ok
        reventados += murio
        marca = "MAL" if murio else ("OK " if ok else "MAL")
        print(f"  {marca}  {nombre_d}")
        print(f"        {'REVENTÓ · el auditor murió, no informó' if murio else resumen(salida)}")
        vistas_fallar |= nombres(salida, "MAL")

    codigo, salida = corre(limpio_datos, limpio_html, limpio_caps)
    print("-" * 74)
    print(f"  {'OK ' if codigo == 0 else 'MAL'}  control de salida · el arnés no dejó nada tocado")
    intactos = all(p.read_bytes() == b for p, b in originales.items())
    print(f"  {'OK ' if intactos else 'MAL'}  los publicados siguen byte a byte igual "
          f"({len(originales)} archivos)")

    # «N de N» no dice nada sobre las comprobaciones que ninguna inyección
    # tocó: una que jamás ha fallado puede estar bien escrita o ser
    # incapaz de fallar, y desde fuera se ven igual. Se listan enteras:
    # son la lista de trabajo del próximo que abra este arnés.
    def tipo_de(n: str) -> str:
        n = re.sub(r"^g_\w+:", "un gráfico:", n)
        n = re.sub(r"^bloque-[abcd]", "un bloque", n)
        return n

    tipos_todos = ({tipo_de(x) for x in todas} - SOLO_FUENTES - FUERA_DE_ALCANCE
                   - {x for x in todas if NOMBRE_VARIABLE.match(x)})
    tipos_vistos = {tipo_de(x) for x in vistas_fallar} & tipos_todos
    tipos_nunca = sorted(tipos_todos - tipos_vistos)

    print("\n" + "=" * 74)
    print(f"  {cazados} de {len(lista)} defectos cazados"
          + (f"  ({inertes} inertes)" if inertes else "")
          + (f"  ({reventados} reventaron al auditor)" if reventados else ""))
    print(f"  instancias: {len(vistas_fallar)} de {len(todas)} se han visto fallar")
    print(f"  TIPOS:      {len(tipos_vistos)} de {len(tipos_todos)} se han visto fallar")
    print(f"  ({len(SOLO_FUENTES)} solo falla si cambian las fuentes primarias · "
          f"{len(FUERA_DE_ALCANCE)} vive fuera de las tres variables de entorno · "
          f"1 lleva su cifra en el nombre y no puede verse fallar con él)")
    if tipos_nunca:
        print(f"\n  {len(tipos_nunca)} tipo(s) que este arnés todavía no ataca:")
        for t in tipos_nunca:
            print(f"      · {t}")
    print("=" * 74)

    shutil.rmtree(tmp, ignore_errors=True)
    bien = (cazados == len(lista) and not inertes and not reventados
            and codigo == 0 and intactos)
    print(f"\n  {'Auditor del preparcial verificado.' if bien else 'ARNÉS EN ROJO.'}")
    return 0 if bien else 1


if __name__ == "__main__":
    sys.exit(main())
