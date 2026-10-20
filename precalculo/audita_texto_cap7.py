#!/usr/bin/env python3
"""
audita_texto_cap7.py — auditor de prosa del capítulo 7

Material de Estadística Espacial 2026-II (20929). T4.6.

Copiado del molde de `audita_texto_cap6.py`. Toda la maquinaria vive en
`audita_texto_base.py` y aquí solo se declara **qué** comprobar, más una
familia propia que el núcleo no puede ver:

  · que **toda cifra de la prosa** esté en `cap7_datos.json` o en
    `cap7_soluciones.json`, incluidas las de dentro de KaTeX;
  · que cada celda de las cinco tablas de solución diga lo que su JSON dice;
  · que el capítulo cubra los doce módulos que el §6 del plan le asigna;
  · que cite sus fuentes y sostenga las afirmaciones que tiene que hacer —las
    que deciden A.28 y A.29: el p del capítulo, el suelo, la GAL, las islas—;
  · accesibilidad del marcado, los `.geomapa`, la codificación y los enlaces;
  · y LA CAPA CATEGÓRICA (familia propia, `capas_categoricas`). Los mapas del
    capítulo entran como UNA constante, `MAPAS_CAP7`, y los registros la
    referencian: el núcleo no puede leer una fuente que no es un literal, así
    que aquí se comprueba que la constante incrustada sea byte a byte el JSON
    del precálculo, que cada capa categórica traiga un código válido por
    rasgo y un color por nivel, y que cada registro pida una capa que existe.
    Un `capa: 'lisa_bonferoni'` mal escrito no da error: el motor cae en la
    primera capa y pinta CRIME donde el texto dice Bonferroni.

EL TOPE DE PESO ES 820 KB, y la aritmética va escrita:

  · el documento pesa **778 KB**: la plantilla (~310), los 184 de
    `cap7_mapas.json` (la geometría municipal es 179 y se carga una vez para
    los cuatro módulos que la usan), los 48 de `cap7_datos.json` (las 999
    réplicas del módulo 3 y los 1 121 puntos del diagrama), 36 de nombres de
    municipio y el resto de prosa, código y simuladores;
  · la cota que ata esta comprobación a su arnés es **por encima del tamaño
    del documento y por debajo de ese tamaño + 312 KB**, porque
    `prueba_texto.py` la tumba inyectando 320 000 bytes: 778 < 820 < 1090;
  · 820 deja ~40 KB de margen: sitio para una revisión, no para un
    ensamblado desbocado.

Uso:  python3 precalculo/audita_texto_cap7.py
Devuelve 1 si algo falla.
"""
from __future__ import annotations

import html
import json
import re
import sys

from audita_texto_base import Auditor, SALIDAS

# El tope de peso de ESTE capítulo. La aritmética, en el encabezado.
TOPE_CAP7_KB = 820.0

# Cifras que NO son resultados: identificadores, años, páginas y versiones.
ESTRUCTURALES = {
    "20929",                                   # el código de la asignatura
    # Los años de las citas: Geary, Anselin, Getis y Ord, Benjamini y
    # Hochberg, de Jong et al., Assunção y Reis; el de SIDS en nc y el del dato
    "2026", "2025", "2024", "1999", "1996", "1995", "1992", "1988", "1984",
    "1979", "1970", "1954",
    # Los de la bibliografía que trae la plantilla
    "2019", "2014", "2013", "1993",
    # Los cuantiles bilaterales de la normal al 90, 95 y 99 %: los cortes del
    # mapa de Gi* de la rejilla (módulo 11). Son constantes, no cifras del dato.
    "1.645", "1.96", "2.576",
    "267",                                     # la página de Getis y Ord (1996)
    "4.0",                                     # CC BY-NC-ND 4.0
    "0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12",
}

# El temario que el §6 del plan le asigna al capítulo 7, módulo a módulo.
# Tokens largos a propósito: buscar «I» daría OK dentro de cualquier cosa.
DEBE_CUBRIR = [
    # Módulo 1 — la pregunta
    ("la pregunta de la autocorrelación", "más de lo que cabría esperar por azar"),
    ("la hipótesis nula por reparto de valores", "repartidos al azar entre las"),
    ("el simulador con autocorrelación controlada", "autocorrelación que tú controlas"),
    ("la GAL de Anselin como W del laboratorio", "gal"),
    # Módulo 2 — el I de Moran
    ("la fórmula con n/S0", "s_0"),
    ("E[I] = -1/(n-1) y su porqué", "por qué e[i] no es cero"),
    ("el rango real no es [-1, 1]", "el rango real no es [−1, 1]"),
    ("los valores propios de de Jong et al.", "valores propios"),
    # Módulo 3 — inferencia
    ("normalidad", "normalidad"),
    ("aleatorización y curtosis", "curtosis"),
    ("permutación de Monte Carlo", "permutación"),
    ("el suelo del p de permutación", "el suelo del p"),
    ("la potencia frente a ρ y a n", "potencia"),
    # Módulo 4 — el diagrama de Moran
    ("los cuatro cuadrantes", "bajo-alto"),
    ("la pendiente de MCO es I", "la pendiente es el i de moran"),
    ("el diagrama clicable", "el diagrama de moran, clicable"),
    ("los puntos influyentes", "influyentes"),
    # Módulo 5 — Geary
    ("la c de Geary", "geary"),
    ("E[c] = 1 y el sentido inverso", "c por debajo de 1 es autocorrelación positiva"),
    ("el barrio disparado", "un barrio disparado"),
    # Módulo 6 — correlograma y join count
    ("el correlograma por órdenes", "órdenes de contigüidad"),
    ("el join count", "join count"),
    ("el gradiente como lectura de lo negativo", "gradiente"),
    # Módulo 7 — sensible a W
    ("once W sobre el mismo dato", "once"),
    ("la sensibilidad es de magnitud", "de magnitud, no"),
    ("las reglas de honestidad", "elegir w antes de ver el i"),
    # Módulo 8 — local
    ("LISA", "lisa"),
    ("la permutación condicional", "condicional"),
    ("no_repeat_in_row = TRUE en todas las llamadas", "no_repeat_in_row = true en todas sus llamadas"),
    # Módulo 9 — el mapa LISA
    ("alto-alto", "alto-alto"),
    ("bajo-bajo", "bajo-bajo"),
    ("alto-bajo", "alto-bajo"),
    ("las islas en el mapa LISA", "las islas no son bajo-bajo"),
    # Módulo 10 — multiplicidad
    ("Bonferroni", "bonferroni"),
    ("FDR", "fdr"),
    ("las réplicas mínimas para Bonferroni", "el suelo iguala al umbral"),
    ("la tasa nula del p plegado, medida", "el plegado al 5 % es un test al 10 %"),
    ("qué p se corrige", "qué p se está corrigiendo"),
    # Módulo 11 — Getis-Ord
    ("Gi y Gi*", "g_i^*"),
    ("intensidad, no similitud", "intensidad"),
    ("la rejilla de Getis y Ord", "rejilla"),
    ("los atípicos del color de su vecindad", "del color de su vecindad"),
    ("la unidad dentro de la permutación de Gi*", "fix_i_in_gstar_permutations"),
    # Módulo 12 — cierre
    ("los cinco ejercicios sobre nc", "carolina del norte"),
    ("el enlace hacia el capítulo 8", "capítulo 8"),
]

# Tokens largos: los cortos caben dentro de otras palabras.
FUENTES = [
    "anselin", "geary", "getis", "benjamini", "hochberg",
    "de jong", "assunção", "tobler",
]

# Las afirmaciones que este capítulo TIENE que hacer. Si una desaparece en
# una reescritura, el capítulo deja de decir lo que el plan le encarga —A.28 y
# A.29 las deciden— y nadie se entera.
AFIRMACIONES = [
    # La promesa del capítulo 1 («el capítulo 7 lo desarrolla»)
    ("explica E[I] por la diagonal que W no tiene", "w no tiene diagonal"),
    ("dice que I se compara con E[I] y no con 0", "se compara con \\(e[i]\\) y no con 0"),
    ("dice que el máximo de I puede pasar de 1", "el máximo puede pasar de 1"),
    ("dice que B, C y U dan el mismo I", "b, c y u son la misma"),
    # Módulo 3: el suelo y el supuesto que nadie ve
    ("dice que el p de permutación no baja de 1/(nsim+1)", "no puede bajar de"),
    ("dice que el suelo no es un efecto más débil", "no es que el efecto sea menor"),
    ("dice que las tres inferencias suponen intercambiabilidad",
     "cualquier valor podría haber caído en cualquier unidad"),
    ("dice que un test que no rechaza con pocas unidades no prueba ausencia",
     "no dice que no haya autocorrelación"),
    # Módulo 4
    ("dice que con W por filas la pendiente ES I", "no una aproximación"),
    ("dice que los influyentes de moran.plot no son todos los que mueven la recta", "la palabra engaña"),
    ("dice que el rango sin centrar son cotas", "sin centrar salen cotas"),
    ("dice que con islas la identidad vale sobre todas las unidades",
     "la identidad se cumple sobre todas"),
    # Módulo 5
    ("dice que el extremo hunde a I y sube c por razones distintas",
     "pero la razón no es la misma en los dos índices"),
    ("dice que una discrepancia I / 1 − c tiene dos sospechosos", "hay dos sospechosos"),
    ("explica el convenio de signo de la z de Geary en esda", "con el signo cambiado"),
    # Módulo 6
    ("dice que significación no es magnitud", "significación no es magnitud"),
    ("dice que las uniones de spdep con W por filas se pesan", "no se cuentan, se pesan"),
    # Módulo 7
    ("dice en qué difieren la GAL y la reina", "en los que la lista de anselin y los polígonos"),
    ("dice que el borde del umbral a medias era del convenio de islas", "el borde era del convenio de islas"),
    ("declara las tres reglas de honestidad sobre W", "no elegir la w que da el resultado más llamativo"),
    # Módulo 8
    ("dice que la media de los I locales es I", "la media de los \\(i_i\\) es el i de moran"),
    ("dice que un I local grande no es un I local significativo", "un \\(i_i\\) grande no es un \\(i_i\\) significativo"),
    ("dice que con islas la suma de los I locales da el I de esda", "que es exactamente el i que calcula"),
    # Módulo 9
    ("dice que el rojo marca centros, no zonas", "señala centros; no dibuja fronteras"),
    ("dice que alto y bajo se refieren solo al signo", "se refieren solo al signo"),
    ("dice que un rezago cero sin vecinos no es un cuadrante", "no es un cuadrante: es una ausencia"),
    # Módulo 10
    ("dice que con 999 réplicas nadie puede pasar Bonferroni", "ningún barrio ni municipio puede pasar"),
    ("dice que el p plegado marca el doble", "el plegado al 5 % es un test al 10 %"),
    ("dice que la corrección empieza por saber qué p se corrige",
     "empieza por saber qué p se está corrigiendo"),
    ("dice que localmoran_perm no da el p analítico", "y ninguno es el analítico"),
    # Módulo 11
    ("dice que un punto caliente lo es a una escala", "un punto caliente lo es a una escala"),
    ("dice que los atípicos salen del color de su vecindad", "salen pintados del color de su vecindad"),
    ("dice que la permutación de Gi* decide qué contesta", "la decisión sobre la permutación decide qué pregunta"),
    ("declara que la z de Gi* de esda por filas está mal", "sale mal"),
    ("declara que el capítulo no puede separar el problema de los números pequeños",
     "no puede separar aquí"),
]

# Lo que el CÓDIGO del capítulo no puede dejar de decir: los comentarios son
# texto que el estudiante lee, y `afirmaciones()` no entra en los <pre>.
AFIRMACIONES_CODIGO = [
    ("el bloque de R del módulo 1 reordena Columbus por POLYID", "match(col.old$polyid, col0$polyid)"),
    ("el bloque de Python del módulo 1 avisa de que el columbus.gal de libpysal no es la GAL",
     "no es la gal de anselin"),
    ("el bloque de R del módulo 8 fija no_repeat_in_row", "no_repeat_in_row = true"),
    ("el bloque de Python del módulo 8 explica el factor n/(n - 1) de esda", "las sumas difieren en n / (n - 1)"),
    ("el bloque de Python del módulo 11 avisa de la z de Gi* de esda por filas", "para gi*, binarios"),
]

CADENAS = [
    "ρ", "×", "—", "–", "«", "»", "·", "⁻",
    "ó", "í", "é", "ñ", "á", "¿",
    "autocorrelación", "vecindad", "rezago", "conglomerado", "Columbus", "Anselin",
    "Geary", "Getis", "Bonferroni", "San Andrés",
]

# Las órdenes de KaTeX que el capítulo escribe de verdad. Si una reescritura
# las vuelve texto plano, esto lo dice.
ORDENES: list[str] = [
    r"\frac", r"\sum", r"\begin{aligned}", r"\begin{gathered}", r"\text",
]


def capas_categoricas(a: Auditor) -> None:
    """La familia propia del capítulo: la capa categórica del `.geomapa`."""
    print("\n=== La capa categórica de los mapas ======================")
    m = re.search(r"const MAPAS_CAP7 = (\{.*?\});\n", a.doc, flags=re.S)
    a.exige(m is not None, "el capítulo incrusta MAPAS_CAP7 como una constante")
    if not m:
        return
    try:
        incrustado = json.loads(m.group(1))
    except json.JSONDecodeError as e:
        a.exige(False, "MAPAS_CAP7 es JSON válido", str(e)[:60])
        return
    fuente = json.loads((SALIDAS / "cap7_mapas.json").read_text(encoding="utf-8"))
    a.exige(incrustado == fuente, "MAPAS_CAP7 es exactamente cap7_mapas.json",
            "" if incrustado == fuente else "el mapa incrustado y el precálculo difieren")

    n_cat = 0
    for ident, mapa in incrustado.items():
        for cp in mapa.get("capas") or []:
            if cp.get("tipo") != "categoria":
                continue
            n_cat += 1
            niv, col, val = cp.get("niveles") or [], cp.get("colores") or [], cp.get("valor") or []
            a.exige(len(col) == len(niv) >= 2, f"'{ident}/{cp['id']}' trae un color por nivel",
                    f"{len(niv)} niveles, {len(col)} colores")
            a.exige(len(val) == mapa.get("n"), f"  y un código por rasgo",
                    f"{len(val)} códigos, n = {mapa.get('n')}")
            fuera = [v for v in val if v is not None and not (isinstance(v, int) and 1 <= v <= len(niv))]
            a.exige(not fuera, f"  y todos sus códigos caen en 1..{len(niv)} o son nulos",
                    "" if not fuera else f"{len(fuera)} fuera")
            tam = [sum(1 for v in val if v == k + 1) for k in range(len(niv))]
            a.exige(tam == cp.get("tam") and cp.get("n_sin_dato") == sum(v is None for v in val),
                    f"  y su recuento por nivel es el de sus códigos", f"{tam}")
    a.exige(n_cat >= 8, "las capas categóricas del capítulo están todas", f"{n_cat} capas")

    # Cada registro que pide una capa por nombre, que la pida bien.
    pedidas = re.findall(r"GEOMAPAS\['(cap7-[^']+)'\][^;]*?capa: '([a-z_]+)'", a.doc, flags=re.S)
    pedidas += [("(estado)", c) for c in re.findall(r"E7\.(?:m9capa|multCapa) = [^;]*?'([a-z_]+)'", a.doc)]
    ids = {cp["id"] for mapa in incrustado.values() for cp in mapa.get("capas") or []}
    malas = sorted({c for _, c in pedidas if c not in ids})
    a.exige(pedidas and not malas, "cada capa que el capítulo pide por nombre existe",
            f"{len(pedidas)} peticiones" + ("" if not malas else f" · NO EXISTEN: {malas}"))

    # Y el motor: la rama categórica tiene que estar en la plantilla que viaja.
    a.exige("cp.tipo === 'categoria'" in a.doc and "geomapaRayado" in a.doc,
            "el motor del documento pinta la capa categórica")


def main() -> int:
    a = Auditor(
        capitulo="capitulo-7-autocorrelacion.html",
        var_entorno="CAP7_HTML",
        jsons=["cap7_datos.json", "cap7_soluciones.json"],
        estructurales=ESTRUCTURALES,
        presupuesto_geomapa_kb=400.0,
        json_mapas="cap7_mapas.json",
    )
    print(f"\n=== audita_texto_cap7.py · {a.ruta.name} ===")
    a.cifras()
    a.soluciones("cap7_soluciones.json")
    a.temario(DEBE_CUBRIR)
    a.fuentes(FUENTES)
    a.afirmaciones(AFIRMACIONES)
    codigo = html.unescape(a.cuerpo).lower()
    for que, clave in AFIRMACIONES_CODIGO:
        a.exige(clave in codigo, que)
    a.accesibilidad()
    a.geomapas()
    capas_categoricas(a)
    a.formulas_escapadas()
    a.codificacion()
    a.enlaces()
    a.coherencia(CADENAS, ORDENES)
    a.peso(TOPE_CAP7_KB)
    return a.cierre()


if __name__ == "__main__":
    sys.exit(main())
