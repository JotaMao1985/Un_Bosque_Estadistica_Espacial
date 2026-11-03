#!/usr/bin/env python3
"""
cuenta_sitio.py — cuenta lo que hay DE VERDAD en los capítulos

Material de Estadística Espacial 2026-II (20929). Portado de Muestreo en T0.5.

Los totales del `index.html` y del README se escriben a mano en las fases
finales, y este proyecto ya sabe cómo acaba eso. Esta herramienta los
cuenta sobre los propios archivos publicados. Los objetivos del §8 del
plan —10 capítulos, 120 módulos, ~99 simuladores, ~35 mapas, 80 preguntas,
40 ejercicios— se contrastan contra esta salida, no contra la memoria.

Cambios respecto a la versión de Muestreo:

  · Cuenta los **`.geomapa`**, que allí no existían y aquí son ~35 del
    objetivo, con su desglose por modo. Un capítulo que prometa un mapa
    en modo `grafo` y no lo tenga se ve aquí.
  · Separa los **preparciales** (`preparcial-*.html`), que no son ni una
    cosa ni la otra: no enseñan contenido nuevo, así que sus módulos no van
    contra los 120 del §8, pero sí tienen autoevaluación, que es lo que un
    taller no tiene. Sin su propio cubo, el primero que se publicó dejó este
    contador en rojo el 2026-08-25 — que es exactamente lo que el aviso de
    «archivo sin clasificar» existe para hacer.
  · Separa los **capítulos** de los **bancos de prueba** (`prueba-*.html`):
    el fixture de T0.5 y el del `.geomapa` no son material del curso y
    sumarlos a los totales sería inflarlos.
  · Y de los **talleres** (`taller-*.html`), que sí son material pero no
    son capítulos: no tienen autoevaluación, sus «ejercicios» son las
    tareas calificables, y sus módulos no cuentan contra los 120 del §8.
    Sin este tercer cubo el Taller 1 no aparecía en ninguna tabla —ni en
    la de capítulos ni en la de bancos—, así que un contador escrito
    justamente para no fiarse de la memoria informaba de un sitio con
    tres archivos cuando ya tenía cuatro. Se vio en C9 del Taller 1.
  · Cuenta las líneas `#>`, que son las cifras que `verifica_bloques.py`
    contrasta: un capítulo con muchos bloques y pocos `#>` está
    publicando código que nadie comprueba.
  · Y comprueba las cifras de la PORTADA (2026-11-03). Desde que la portada
    lleva el estilo de la de Diseño de Experimentos, cada tarjeta trae su
    fila de cifras —módulos, simuladores, mapas, bloques, preguntas— y el
    bloque de entrada los totales de los capítulos. La portada se sigue
    escribiendo a mano, así que esas cifras se contrastan aquí contra lo
    contado; con `--prueba`, la guarda se rompe a sí misma.

    python3 precalculo/cuenta_sitio.py [--prueba]
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
CARPETAS = [RAIZ / "sitio" / "estadistica-espacial", RAIZ / "Htmls_Espacial"]

CAMPOS = [
    ("módulos",     lambda h, m: h.count('<template id="module-')),
    ("simulad.",    lambda h, m: len(re.findall(r"\n    SIMULADORES\['", h))),
    ("geomapas",    lambda h, m: len(re.findall(r'data-geomapa="', m))),
    ("t-ranking",   lambda h, m: len(re.findall(r"\n    TABLAS_RANKING\['", h))),
    ("preguntas",   lambda h, m: len(re.findall(r"\n        tipo: ", h))),
    ("ejercicios",  lambda h, m: m.count('class="ejercicio-guiado"')),
    # La clase EXACTA no, prefijo: el Taller 1 marca sus bloques de
    # arranque `class="language-r arranque"` y con `="language-r"` a secas
    # el contador informaba de **cero** bloques de R en un archivo que
    # tiene cuatro. Es la misma trampa que C8 le encontró a
    # `verifica_bloques.py`, y por el mismo motivo se arregla igual: un
    # bloque invisible es peor que uno mal contado.
    ("bloq. R",     lambda h, m: len(re.findall(r'class="language-r[" ]', h))),
    ("bloq. Py",    lambda h, m: len(re.findall(r'class="language-python[" ]', h))),
    # Las DOS formas: los bloques de R escriben `#&gt;` escapado y los de
    # Python `#>` a pelo. Contar solo una daba 14 donde hay 26, y un
    # contador que informa de menos es tan inútil como uno que informa de
    # más: los totales del §8 del plan se cuentan, no se recuerdan.
    ("cifras #>",   lambda h, m: len(re.findall(r"#&gt;", h)) + len(re.findall(r"#>", h))),
]
COMPONENTES = [
    ("glosario", 'data-glosario="'),
    ("rúbrica",  'data-rubrica="'),
    # El árbol no se cablea con `data-arbol`: vive DENTRO de un simulador
    # como `<div class="arbol">`, que es como lo estrenó el capítulo 4 de
    # Diseño de Experimentos. Buscando el atributo, el contador informaba
    # 0 árboles sobre un capítulo que tiene uno.
    ("árbol",    'class="arbol"'),
    ("ciclo",    'data-ciclo="'),
    ("diagrama", 'data-diagrama="'),
]
MODOS = ["poligonos", "puntos", "grafo", "rejilla", "proyeccion"]


def marcado(h: str) -> str:
    """Solo lo que hay DENTRO de los <template> de los módulos.

    El comentario de documentación de cada motor escribe también
    `data-x="id"`, y contarlo duplicaba el total. Es la corrección que ya
    llevaba la versión de Muestreo, y se conserva por el mismo motivo.
    """
    return "".join(re.findall(r'<template id="module-.*?</template>', h, re.S))


def tabla(titulo: str, rutas: list[Path]) -> list[int]:
    cab = ["archivo"] + [n for n, _ in CAMPOS] + [n for n, _ in COMPONENTES]
    anchos = [22] + [max(len(n), 9) for n in cab[1:]]
    print(f"\n{titulo}")
    print("  ".join(c.rjust(a) for c, a in zip(cab, anchos)))
    totales = [0] * (len(CAMPOS) + len(COMPONENTES))
    for p in rutas:
        h = p.read_text(encoding="utf-8")
        m = marcado(h)
        vals = [f(h, m) for _, f in CAMPOS] + [m.count(c) for _, c in COMPONENTES]
        totales = [t + v for t, v in zip(totales, vals)]
        etiqueta = p.stem[:22]
        print("  ".join(x.rjust(a) for x, a in
                        zip([etiqueta] + [str(v) for v in vals], anchos)))
    print("  ".join(x.rjust(a) for x, a in
                    zip(["TOTAL"] + [str(t) for t in totales], anchos)))
    kb = sum(p.stat().st_size for p in rutas) / 1024
    print(f"  {len(rutas)} archivo(s) · {kb:.0f} KB"
          + (f" · {kb/len(rutas):.0f} KB de media" if rutas else ""))
    return totales


def cuenta(p: Path) -> dict[str, int]:
    """Los CAMPOS de un archivo, por nombre: lo que la portada tiene que decir."""
    h = p.read_text(encoding="utf-8")
    m = marcado(h)
    return {n: f(h, m) for n, f in CAMPOS}


# La fila de cifras de cada tarjeta de la portada y el campo que la respalda.
# «bloques R/Python» promete PARES: solo vale si R y Python coinciden, y por
# eso no tiene un campo propio sino los dos.
ROTULOS_TARJETA = {"módulo": "módulos", "simulador": "simulad.", "mapa": "geomapas",
                   "pregunta": "preguntas"}
ROTULOS_HERO = {"simuladores": "simulad.", "mapas": "geomapas", "módulos": "módulos"}


def revisa_portada(texto: str, cuentas: dict[str, dict[str, int]],
                   capitulos: list[str]) -> tuple[list[str], list[str]]:
    """Lo que la portada dice frente a lo que hay. Devuelve (informe, problemas).

    `cuentas` lleva los CAMPOS de cada archivo del curso (los bancos de prueba
    no: no se enlazan porque no son del curso) y `capitulos`, cuáles de ellos
    son capítulos, que son los que suma el bloque de entrada. Es una función
    pura para que `--prueba` pueda dársela rota sin tocar el archivo.
    """
    informe: list[str] = []
    problemas: list[str] = []

    # ¿Se llega a lo publicado desde la portada? El Taller 1 estuvo
    # ensamblado, auditado y en verde durante toda una fase siendo
    # **inalcanzable**: existía el archivo y no lo enlazaba nadie. Un
    # capítulo que no se enlaza no está publicado, está subido, y esa
    # diferencia no la ve ningún auditor de cifras.
    huerfanos = [n for n in cuentas if n not in texto]
    for n in huerfanos:
        informe.append(f"⚠ {n} — publicado y SIN enlace desde la portada")
    if huerfanos:
        problemas.append(f"{len(huerfanos)} página(s) sin enlace desde la portada")
    else:
        informe.append(f"los {len(cuentas)} archivos del curso están enlazados")

    # Las tarjetas. Si no hay ninguna, la guarda está CIEGA, y eso es rojo: la
    # versión anterior buscaba `bosque-card` y `card-number`, y con la marca de
    # Diseño habría encontrado cero tarjetas y dicho «ninguno de los 0
    # publicados sigue pendiente» en verde.
    tarjetas = re.findall(r"<article\b([^>]*)>(.*?)</article>", texto, re.S)
    tarjetas = [(a, c) for a, c in tarjetas if re.search(r'class="tarjeta\b', a)]
    if not tarjetas:
        informe.append('⚠ ninguna tarjeta `<article class="tarjeta…">`: la guarda no ve nada')
        problemas.append("la portada no tiene tarjetas que comprobar")
        return informe, problemas

    # Y LA OTRA MITAD de los huérfanos: un capítulo publicado NO puede seguir
    # anunciado como «Próximamente» en otra tarjeta.
    #
    # Existe porque pasó TRES VECES seguidas. La portada se mantiene a
    # mano, y al publicar los capítulos 4, 5 y 6 se añadió la tarjeta
    # nueva sin quitar la vieja: durante semanas el estudiante abría el
    # capítulo 4 desde arriba y lo encontraba abajo con un reloj y un
    # «Próximamente». El enlace estaba —así que la comprobación de
    # huérfanos daba verde— y el defecto vivía en la MISMA página, tres
    # secciones más abajo. Se encontró leyendo la portada, no contándola.
    publicadas: set[str] = set()
    pendientes: set[str] = set()
    for atributos, cuerpo in tarjetas:
        num = re.search(r'data-capitulo="(\d+)"', atributos)
        if not num:
            continue
        if "tarjeta-pendiente" in atributos:
            pendientes.add(num.group(1))
            if "href=" in cuerpo:
                informe.append(f"⚠ el capítulo {num.group(1)} está «En preparación» y lleva un enlace")
                problemas.append(f"capítulo {num.group(1)} pendiente con enlace")
        else:
            publicadas.add(num.group(1))
    if not publicadas | pendientes:
        informe.append("⚠ ninguna tarjeta lleva `data-capitulo`: no se puede ver "
                       "qué capítulos salen publicados y cuáles pendientes")
        problemas.append("ninguna tarjeta con data-capitulo")
    dobles = sorted(publicadas & pendientes, key=int)
    for n in dobles:
        informe.append(f"⚠ el capítulo {n} sale como publicado Y como «En preparación» "
                       "en la misma portada")
    if dobles:
        problemas.append(f"{len(dobles)} capítulo(s) anunciados a la vez como publicados y pendientes")
    else:
        informe.append(f"y ninguno de los {len(publicadas)} publicados sigue anunciado como pendiente")

    # Las cifras de cada tarjeta, contra lo contado en el archivo que enlaza su
    # título. Ninguna se escribe sin que alguien la haya contado antes, y el
    # día que se reensamble un capítulo con un módulo más, la portada no puede
    # seguir diciendo el número viejo en verde.
    vistas = 0
    malas = 0
    for atributos, cuerpo in tarjetas:
        enlace = re.search(r'class="tarjeta-titulo[^"]*">\s*<a href="([^"]+)"', cuerpo)
        if not enlace:
            continue
        nombre = enlace.group(1).split("/")[-1]
        if nombre not in cuentas:
            continue
        c = cuentas[nombre]
        fila = re.search(r'class="tarjeta-meta[^"]*">(.*?)</div>', cuerpo, re.S)
        # El plural va aparte («simulador» + «es», «mapa» + «s») para poder
        # comprobar también que «1 simuladores» no se cuela.
        cifras = re.findall(r">(\d+) (módulo|simulador|mapa|pregunta|bloques R/Python)(e?s)?<",
                            fila.group(1) if fila else "")
        if not any(base == "módulo" for _, base, _ in cifras):
            informe.append(f"⚠ {nombre}: su tarjeta no dice cuántos módulos tiene")
            problemas.append(f"{nombre} sin fila de cifras")
        for numero, base, plural in cifras:
            n = int(numero)
            rotulo = base + plural
            vistas += 1
            if base == "bloques R/Python":
                real = c["bloq. R"]
                if c["bloq. R"] != c["bloq. Py"]:
                    informe.append(f"⚠ {nombre}: «bloques R/Python» promete pares y tiene "
                                   f"{c['bloq. R']} de R y {c['bloq. Py']} de Python")
                    problemas.append(f"{nombre} sin bloques pareados")
                    malas += 1
                    continue
            else:
                real = c[ROTULOS_TARJETA[base]]
                if (n == 1) == bool(plural):
                    informe.append(f"⚠ {nombre}: «{numero} {rotulo}» no concuerda en número")
                    problemas.append(f"{nombre}: «{numero} {rotulo}» no concuerda en número")
                    malas += 1
            if n != real:
                informe.append(f"⚠ {nombre}: la portada dice {n} {rotulo} y tiene {real}")
                problemas.append(f"{nombre}: {rotulo} {n} ≠ {real}")
                malas += 1

    # El bloque de entrada: los totales de los CAPÍTULOS, no del sitio entero.
    hero = re.search(r'<section class="hero[^"]*">(.*?)</section>', texto, re.S)
    totales = re.findall(r">(\d+) (capítulos|simuladores|mapas|bloques en R y Python|módulos)<",
                         hero.group(1) if hero else "")
    if not totales:
        informe.append("⚠ el bloque de entrada no tiene cifras que comprobar")
        problemas.append("bloque de entrada sin cifras")
    suma = {campo: sum(cuentas[n][campo] for n in capitulos) for campo in cuentas[capitulos[0]]} \
        if capitulos else {}
    for numero, rotulo in totales:
        n = int(numero)
        vistas += 1
        if rotulo == "capítulos":
            real = len(capitulos)
        elif rotulo == "bloques en R y Python":
            real = suma.get("bloq. R", 0)
            if suma.get("bloq. R") != suma.get("bloq. Py"):
                informe.append("⚠ el bloque de entrada promete pares de R y Python y no los hay")
                problemas.append("bloque de entrada sin bloques pareados")
                malas += 1
                continue
        else:
            real = suma.get(ROTULOS_HERO[rotulo], 0)
        if n != real:
            informe.append(f"⚠ el bloque de entrada dice {n} {rotulo} y los capítulos suman {real}")
            problemas.append(f"bloque de entrada: {rotulo} {n} ≠ {real}")
            malas += 1
    if not malas:
        informe.append(f"y sus {vistas} cifras coinciden con lo contado")
    return informe, problemas


def prueba(texto: str, cuentas: dict[str, dict[str, int]], capitulos: list[str]) -> int:
    """Se rompe a sí misma. Una comprobación que nadie ha visto fallar puede
    estar bien escrita o ser incapaz de fallar, y desde fuera se ven igual."""
    print("\n=== Autoprueba: se le inyectan defectos a la portada ===")
    if revisa_portada(texto, cuentas, capitulos)[1]:
        print("  MAL  el control no está limpio: la portada ya viene rota")
        return 1
    print("  OK   control · la portada sale limpia sin inyectar nada")
    casos = [
        ("una cifra de tarjeta que no es la contada", "12 módulos<", "11 módulos<", "≠"),
        ("un total del bloque de entrada que no suma", "77 simuladores<", "78 simuladores<", "entrada"),
        ("un capítulo publicado y pendiente a la vez",
         'tarjeta-pendiente p-5" data-capitulo="8"', 'tarjeta-pendiente p-5" data-capitulo="1"', "a la vez"),
        ("una página publicada sin enlace", 'href="Htmls_Espacial/taller-2-cap-4.html"', 'href="#"', "sin enlace"),
        ("una cifra en singular con plural", ">1 simulador<", ">1 simuladores<", "número"),
        ("una portada sin tarjetas (la marca cambió)", "<article", "<div", "tarjetas"),
    ]
    fallos = 0
    for nombre, viejo, nuevo, clave in casos:
        roto = texto.replace(viejo, nuevo) if viejo == "<article" else texto.replace(viejo, nuevo, 1)
        if roto == texto:
            print(f"  MAL  INERTE · «{nombre}» no cambió la portada")
            fallos += 1
            continue
        problemas = revisa_portada(roto, cuentas, capitulos)[1]
        cazado = any(clave in p for p in problemas)
        print(f"  {'OK ' if cazado else 'MAL'}  «{nombre}» → "
              + ("cazado" if cazado else f"pasa ({problemas or 'sin problemas'})"))
        fallos += 0 if cazado else 1
    return fallos


def main() -> None:
    carpeta = next((d for d in CARPETAS if d.exists() and any(d.glob("*.html"))), None)
    if carpeta is None:
        raise SystemExit(f"ABORTA: no hay .html en {[str(d) for d in CARPETAS]}")
    print(f"Fuente: {carpeta.relative_to(RAIZ)}")

    caps = sorted(carpeta.glob("capitulo-*.html"))
    bancos = sorted(carpeta.glob("prueba-*.html"))
    talleres = sorted(carpeta.glob("taller-*.html"))
    preparciales = sorted(carpeta.glob("preparcial-*.html"))
    apendices = sorted(carpeta.glob("apendice-*.html"))
    proyectos = sorted(carpeta.glob("proyecto-*.html"))

    # Nada publicado puede quedarse fuera de los cubos sin que se
    # diga. Un archivo con un nombre nuevo —`parcial-1.html`, digamos—
    # no debe desaparecer del recuento en silencio: eso es exactamente lo
    # que le pasó al Taller 1 antes de C9.
    clasificados = {p.name for p in caps + bancos + talleres + preparciales + apendices + proyectos}
    sueltos = [p for p in sorted(carpeta.glob("*.html")) if p.name not in clasificados]

    if caps:
        t = tabla("CAPÍTULOS DEL CURSO", caps)
        # Los objetivos del §8 del plan, para ver la distancia sin
        # tener que ir a buscarlos.
        objetivos = {"módulos": 120, "simulad.": 99, "geomapas": 35,
                     "preguntas": 80, "ejercicios": 40}
        print("\n  Contra los objetivos del §8 del plan:")
        for (nombre, _), valor in zip(CAMPOS, t):
            if nombre in objetivos:
                o = objetivos[nombre]
                print(f"    {nombre:<12} {valor:>4} de {o:>4}  ({100*valor/o:.0f} %)")
    else:
        print("\nCAPÍTULOS DEL CURSO: todavía ninguno "
              "(la Fase 1 escribe el primero).")

    if talleres:
        # Su tabla es la misma, y así se ven las columnas que un taller
        # deja en cero a propósito: sin autoevaluación (`preguntas`) y con
        # `ejercicios` que aquí son las tareas calificables. Los totales
        # NO se suman a los del §8: un taller no es un capítulo.
        tabla("TALLERES (material del curso, fuera de los objetivos del §8)", talleres)
        # Y por qué su columna `cifras #>` es cero sin que eso sea una
        # denuncia: los bloques de un taller son código de ARRANQUE —con
        # marcadores por rellenar— y no llevan salida esperada. Se dice
        # aquí para que nadie lea el cero como «publica código que nadie
        # comprueba», que es lo que ese cero significa en un capítulo.
        arr = sum(len(re.findall(r'class="language-\w+ arranque"',
                                 p.read_text(encoding="utf-8"))) for p in talleres)
        print(f"    de ellos {arr} bloque(s) de arranque: sin línea `#>` a propósito, "
              "y `verifica_bloques.py` los declara en vez de ejecutarlos")

    if preparciales:
        # El cuarto cubo. Un preparcial no es capítulo —no enseña contenido
        # nuevo, y sus módulos no van contra los 120 del §8— y tampoco es
        # taller —no se califica, no se individualiza y sí tiene
        # autoevaluación, que es justo lo que un taller no tiene—. Su columna
        # `preguntas` es la que importa y la de `ejercicios` acompaña; las de
        # simuladores y mapas pueden quedarse en cero sin que eso denuncie
        # nada, porque un preparcial reutiliza los del capítulo en vez de
        # estrenar los suyos.
        tabla("PREPARCIALES (material del curso, fuera de los objetivos del §8)",
              preparciales)

    if apendices:
        # El quinto cubo, que nace con el apéndice A (2026-10-02). Un apéndice
        # SÍ enseña contenido —tiene módulos, simuladores, autoevaluación y
        # ejercicios, como un capítulo—, pero no es temario de ninguna semana:
        # repasa lo que un capítulo da por sabido. Sumarlo a los 120 módulos
        # del §8 inflaría el avance del temario con material que no lo cubre.
        tabla("APÉNDICES (material del curso, fuera de los objetivos del §8)", apendices)

    if proyectos:
        # El sexto cubo, que nace con la guía del proyecto integrador
        # (2026-10-21). Se califica, como un taller, pero no tiene tareas ni
        # variante: es una guía de hitos con su rúbrica. Sus columnas de
        # simuladores, mapas y preguntas son cero a propósito.
        tabla("PROYECTOS (material del curso, fuera de los objetivos del §8)", proyectos)

    if bancos:
        tabla("BANCOS DE PRUEBA (no son material del curso)", bancos)

    # Los dos hallazgos que NO son estadística sino defecto, y que por eso
    # tumban el paso en `audita_todo.sh` en vez de imprimir un aviso que
    # nadie mira. Contar de menos y publicar algo inalcanzable son las dos
    # formas de que este contador diga que el sitio está bien cuando no.
    problemas = []

    if sueltos:
        print("\n  ⚠ HTML publicado que no cae en ningún cubo "
              "(ni capítulo, ni taller, ni preparcial, ni apéndice, ni proyecto, ni banco de prueba):")
        for p in sueltos:
            print(f"    · {p.name} — no se está contando en ninguna tabla")
        problemas.append(f"{len(sueltos)} archivo(s) sin clasificar")

    # La portada: que enlace todo lo publicado, que no anuncie como pendiente
    # un capítulo que ya está, y que sus cifras sean las contadas. Los bancos
    # de prueba quedan fuera a propósito: no se enlazan porque no son del curso.
    portada = RAIZ / "index.html"
    autoprueba = 0
    if portada.exists():
        texto = portada.read_text(encoding="utf-8")
        cuentas = {p.name: cuenta(p) for p in caps + talleres + preparciales + apendices + proyectos}
        informe, malos = revisa_portada(texto, cuentas, [p.name for p in caps])
        print("\n  La portada (index.html):")
        for linea in informe:
            print(f"    {linea}")
        problemas += malos
        if "--prueba" in sys.argv[1:]:
            autoprueba = prueba(texto, cuentas, [p.name for p in caps])
            if autoprueba:
                problemas.append(f"la autoprueba de la portada falla en {autoprueba} caso(s)")

    # Desglose de los modos del .geomapa: el §4 del plan reparte los cinco
    # entre los capítulos, y así se ve cuáles siguen sin estrenarse.
    #
    # Se cuenta el `"modo"` del JSON incrustado, NO el `data-geomapa="…"`:
    # el identificador del contenedor puede llamarse como quiera, y en el
    # capítulo de prueba del .geomapa coincide con el modo solo por
    # casualidad. Contar por el nombre del contenedor habría dado una
    # tabla que parece correcta y no mide lo que dice medir.
    print("\n  Modos del .geomapa en uso (leídos del JSON incrustado):")
    textos = [p.read_text(encoding="utf-8")
              for p in caps + talleres + preparciales + apendices + proyectos + bancos]
    for modo in MODOS:
        n = sum(len(re.findall(r'"modo":\s*"' + modo + '"', t)) for t in textos)
        print(f"    {modo:<12} {n}")

    if problemas:
        raise SystemExit("\n  CUENTA_SITIO EN ROJO: " + " · ".join(problemas))


if __name__ == "__main__":
    main()
