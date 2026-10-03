#!/usr/bin/env python3
"""
audita_texto_apendicea.py — auditor de prosa del apéndice A

Material de Estadística Espacial 2026-II (20929). Apéndice A.

Copiado del molde de `audita_texto_cap5.py`. Toda la maquinaria vive en
`audita_texto_base.py` y aquí solo se declara **qué** comprobar.

Qué comprueba, por encima:

  · que **toda cifra de la prosa** esté en `apendicea_datos.json` o en
    `apendicea_soluciones.json`, incluidas las de dentro de KaTeX y los
    rótulos de la figura del plano (el SVG del módulo 4);
  · que cada celda de las diez tablas de solución diga lo que su JSON dice,
    y que cada respuesta esté en su panel;
  · que el apéndice cubra su temario, cite sus fuentes y sostenga las
    afirmaciones que lo justifican —las cuatro cosas que el documento
    original no decía y que se midieron al construirlo—;
  · accesibilidad, codificación, enlaces, decimales con punto y títulos sin
    acentos graves (las dos guardas que el capítulo 5 aprendió);
  · **que el motor de los simuladores sea el de hoy**: el documento lleva
    `densidad1d.js` en línea, y una copia vieja dibujaría con una matemática
    que la prueba contra R ya no cubre. Es la lección de la animación del
    capítulo 5, cuyo capítulo llegó a publicarse con un motor anterior.

LA BIBLIOGRAFÍA NO SE AUDITA COMO CIFRAS. Sus años, volúmenes, páginas y
DOI no son resultados de nada. En vez de copiarlos a mano en una lista —que
se desfasaría con la primera referencia nueva—, se LEEN del bloque de
lecturas y se declaran estructurales. Solo se exime lo que está ahí dentro:
un número de la prosa que coincida con uno de la bibliografía sale exento,
y por eso la lista se imprime.

EL TOPE DE PESO ES 760 KB. El documento pesa 661 —el motor y los catorce
simuladores van en línea, y la muestra de los simuladores también—; la cota
que ata la comprobación a su arnés es por encima del tamaño y por debajo de
ese tamaño + 312 KB (`prueba_texto.py` la tumba inyectando 320 000 bytes).
760 deja unos 100 KB de margen y queda más de 200 por debajo del techo.

Uso:  python3 precalculo/audita_texto_apendicea.py
Devuelve 1 si algo falla.
"""
from __future__ import annotations

import json
import re
import sys

from audita_texto_base import Auditor, SALIDAS, busca_capitulo

# El tope es una ALARMA contra un ensamblado desbocado, no un presupuesto
# (ver `audita_texto_base.py`). La revisión 2 (2026-10-02) subió el documento
# de 683 a 755 KB —el cuestionario pasó de 12 a 17 preguntas, cada ejercicio
# ganó su pista y cuatro simuladores ganaron curvas y mandos— y el tope sube
# con él, por debajo de tamaño + 312 KB para que `prueba_texto.py` no quede
# ciego.
TOPE_KB = 840.0
DOCUMENTO = "apendice-a-densidad.html"
MOTOR = SALIDAS.parent / "densidad1d.js"

ESTRUCTURALES = {
    "20929",                                  # el código de la asignatura
    "2026",                                   # el semestre y la semilla
    # Las constantes de la tabla 3.1 del texto guía: 15/16 del biweight y
    # 35/32 del triweight. Son coeficientes de una fórmula, no resultados.
    "15", "16", "35", "32",
}


def estructurales_de_la_bibliografia() -> set[str]:
    doc = busca_capitulo(DOCUMENTO).read_text(encoding="utf-8")
    m = re.search(r'<div class="references">(.*?)</div>', doc, re.S)
    if not m:
        return set()
    texto = re.sub(r"<[^>]+>", " ", m.group(1))
    return set(re.findall(r"\d+(?:\.\d+)?", texto))


DEBE_CUBRIR = [
    ("densidad frente a intensidad", "intensidad"),
    ("el histograma de densidad", "histograma de densidad"),
    ("la regla de Sturges", "sturges"),
    ("la regla de Freedman y Diaconis", "freedman"),
    ("el MAUP en el histograma", "zonificación"),
    ("el histograma desplazado promediado", "histograma desplazado promediado"),
    ("la malla extendida del ASH", "malla extendida"),
    ("el estimador ingenuo k/(nV)", "estimador ingenuo"),
    ("la maldición de la dimensión", "maldición de la dimensión"),
    ("las ventanas de Parzen", "ventanas de parzen"),
    ("el núcleo de Epanechnikov", "epanechnikov"),
    ("la eficiencia de los núcleos", "eficiencia"),
    ("la convención de density()", "density()"),
    ("los k vecinos más cercanos", "vecinos más cercanos"),
    ("los estimadores balloon", "balloon"),
    ("el sesgo y la varianza", "varianza"),
    ("el ECIP o MISE", "ecip"),
    ("el AMISE", "amise"),
    ("la regla de referencia normal", "referencia normal"),
    ("bw.nrd0 y bw.nrd", "bw.nrd0"),
    ("la validación cruzada", "validación cruzada"),
    ("UCV y LCV", "lcv"),
    ("Sheather y Jones", "bw.sj"),
    ("el Monte Carlo de los selectores", "monte carlo"),
    ("el borde en cero", "reflejar"),
    ("la corrección de Diggle", "diggle"),
    ("las parejas recíprocas", "recíprocas"),
    ("los empates", "empates"),
    ("nndensity", "nndensity"),
    ("bw.scott", "bw.scott"),
    ("bw.ppl", "bw.ppl"),
    ("bw.diggle", "bw.diggle"),
]

FUENTES = [
    "rosenblatt", "parzen", "epanechnikov", "silverman", "scott", "terrell",
    "sheather", "wand", "diggle", "berman", "cronie", "lieshout", "clark", "evans",
    "cox", "freedman", "diaconis", "loader",
]

# Las afirmaciones que el apéndice TIENE que hacer: las que justifican que
# exista, porque el documento del que nace no las decía y se midieron al
# construirlo. Si una reescritura las pierde, el apéndice vuelve a ser un
# resumen de densidades y deja de ser un repaso para el capítulo 5.
AFIRMACIONES = [
    ("dice que la altura de un histograma de densidad no es una probabilidad",
     "no es una probabilidad"),
    ("dice que una moda que se mueve con el origen es de la rejilla",
     "no es una propiedad del dato"),
    ("descubre que el ASH es un núcleo triangular",
     "núcleo triangular de semiancho"),
    ("dice que el error del ASH frente al triangular baja como 1/m",
     "el error baja como"),
    ("dice que con el mismo soporte el mismo número no es el mismo suavizado",
     "el mismo número ya no es el mismo suavizado"),
    ("dice que los dientes del k-NN son de la fórmula",
     "tiene dientes por construcción"),
    ("dice que el k-NN no integra 1",
     "no es una densidad"),
    ("declara que bw.scott es la regla de referencia normal del plano",
     "el factor vale exactamente 1"),
    ("declara que el «silverman» de scipy no es el de R",
     "no es el de r"),
    ("caracteriza a la UCV como un selector de alta varianza",
     "selector de alta varianza"),
    ("dice que con la corrección e(x) un dato del borde aporta ln 2",
     "un dato en el mismo borde aporta exactamente"),
    ("dice que las parejas recíprocas son geometría",
     "son geometría, no agrupamiento"),
    ("dice que sobre distancias al vecino la UCV no tiene mínimo",
     "la ucv no tiene mínimo"),
    ("explica qué rompe la validación cruzada",
     "deja dentro a su gemelo"),
    # Las conclusiones que cambió la revisión 2 (2026-10-02): si una edición
    # futura las borra, vuelve el error que corrigieron.
    ("dice que el mínimo de la UCV de las erupciones es local",
     "pero ese mínimo de la ucv es local"),
    ("dice que en r = 0 mandan los ceros, que son un átomo",
     "son un átomo"),
    ("dice que el máximo de la reflejada en el borde lo ponen los ceros",
     "ese máximo en el borde lo ponen enteros los"),
    ("dice que la UCV se equivoca de dispersión y no de centro",
     "no se equivoca de centro"),
    ("dice que la rugosidad de una curva estimada lleva ruido del ancho",
     "lleva dentro un término de ruido"),
    ("dice que el signo de la UCV no delata el colapso",
     "el signo del criterio no dice nada por sí solo"),
    ("dice que la banda del módulo 4 mide la desviación típica",
     "mide la desviación típica"),
    ("explica la ventaja del núcleo por estar centrado",
     "está centrada en el punto que estima"),
]

CADENAS = [
    "σ", "λ", "²", "−", "×", "—", "–", "«", "»", "·",
    "ó", "í", "é", "ñ", "á", "ú", "¿",
    "núcleo", "intensidad", "densidad", "histograma", "vecinos", "validación",
    "Bogotá", "Kennedy", "Epanechnikov", "Silverman", "Diggle",
]

ORDENES = [r"\hat f", r"\frac", r"\sum", r"\int", r"\sigma", r"\lambda",
           r"\mu_2", r"\operatorname{Var}", r"\phi", r"\text{AMISE}"]

COMA_DECIMAL = re.compile(r"(?<![\d.,])\d+,\d+(?!\d|[.,]\d)")
PUNTO_A_COMA = re.compile(r"""\.replace\(\s*(?:(['"])\.\1|/\\\./g?)\s*,\s*(['"]),\2\s*\)""")


def respuestas_publicadas(a: Auditor) -> None:
    """CADA RESPUESTA DEL JSON, EN SU PANEL, Y NINGUNA DE MÁS (lección M5 del cap. 5)."""
    print("\n=== Las respuestas de los ejercicios, en su panel ==========")
    S = json.loads((SALIDAS / "apendicea_soluciones.json").read_text(encoding="utf-8"))
    for k in range(1, S["meta"]["n_ejercicios"] + 1):
        resp = S[f"e{k}"]["solucion"].get("respuestas") or []
        m = re.search(rf'id="apa-e{k}-sol".*?</div>', a.doc, re.S)
        if not a.exige(m is not None, f"el panel de la solución {k} está en el documento"):
            continue
        panel = m.group(0)
        n_pub = panel.count('class="ejercicio-respuesta"')
        a.exige(n_pub == len(resp) and len(resp) > 0,
                f"la solución {k} publica todas sus respuestas", f"{n_pub} de {len(resp)}")
        faltan = [r["pide"] for r in resp
                  if re.sub(r"`([^`]+)`", r"<code>\1</code>", r["respuesta"]) not in panel]
        a.exige(not faltan, f"la solución {k} publica cada respuesta entera", "; ".join(faltan))


def decimales_con_punto(a: Auditor) -> None:
    """UN SOLO SEPARADOR DECIMAL, EL PUNTO (regla M6 del capítulo 5)."""
    print("\n=== Los decimales, con punto =================================")
    comas = [a.prosa_txt[max(0, m.start() - 30):m.end() + 5].strip()
             for m in COMA_DECIMAL.finditer(a.prosa_txt)]
    a.exige(not comas, "la prosa no escribe ningún decimal con coma",
            " · ".join(f"«{c}»" for c in comas[:3]))
    guiones = "\n".join(re.findall(r"<script[^>]*>(.*?)</script>", a.doc, re.S))
    cambios = [guiones[max(0, m.start() - 50):m.end()].strip().splitlines()[-1]
               for m in PUNTO_A_COMA.finditer(guiones)]
    a.exige(not cambios, "ningún formateador cambia el punto por coma", " · ".join(cambios[:2]))


def titulos_sin_acento_grave(a: Auditor) -> None:
    """UN TÍTULO DE MÓDULO NO PUBLICA MARKDOWN (lección del módulo 9 del cap. 5)."""
    print("\n=== Los títulos de los módulos, sin acentos graves ==========")
    h2 = re.findall(r'<template id="module-(\d+)">.*?<h2\b[^>]*>(.*?)</h2>', a.doc, re.S)
    cd = re.search(r"const courseData = \{\s*modules: \[(.*?)\n\s*\]\s*\};", a.doc, re.S)
    entradas = re.findall(r"\{ id: (\d+), (.*?) \},?$", cd.group(1), re.M) if cd else []
    a.exige(0 < len(h2) == len(entradas), "un h2 y una entrada del índice por módulo, leídos",
            f"{len(h2)} h2 y {len(entradas)} entradas")
    malos = [f"{k}: «{' '.join(re.sub(r'<[^>]+>', '', t).split())}»" for k, t in h2 if "`" in t]
    a.exige(not malos, "ningún h2 de módulo lleva un acento grave", " · ".join(malos))


def motor_al_dia(a: Auditor) -> None:
    """EL MOTOR EN LÍNEA ES EL DE HOY, BYTE A BYTE.

    `prueba_densidad1d.py` prueba `precalculo/densidad1d.js` contra R. Si el
    documento llevara una copia anterior, la prueba estaría cubriendo un
    archivo que nadie dibuja. Se busca el archivo entero dentro del HTML.
    """
    print("\n=== El motor de los simuladores, al día =====================")
    motor = MOTOR.read_text(encoding="utf-8")
    a.exige(motor in a.doc, "el documento lleva densidad1d.js tal como está hoy",
            f"{len(motor) / 1024:.1f} KB")
    regs = set(re.findall(r"SIMULADORES\['(apa-[a-z]+)'\] = function", a.doc))
    marc = a.doc[:a.doc.rindex("\n  <script>")]
    ids = set(re.findall(r'data-simulador="([^"]+)"', marc))
    a.exige(ids == regs and len(ids) == 14,
            "cada simulador del marcado tiene su registro y viceversa", f"{len(ids)} y {len(regs)}")


def figura_del_plano(a: Auditor) -> None:
    """LA FIGURA DEL MÓDULO 4 DIBUJA LOS TRES SITIOS QUE LA TABLA DESCRIBE.

    `cifras()` ya contrasta los rótulos del SVG contra el JSON, pero no sabe
    si están en el panel que les toca. Aquí se lee cada panel: el de radio
    fijo tiene que rotular conteos de sedes y el de k fijo, radios.
    """
    print("\n=== La figura del plano ======================================")
    D = json.loads((SALIDAS / "apendicea_datos.json").read_text(encoding="utf-8"))
    sitios = D["m4"]["plano"]["sitios"]
    fig = re.search(r'<figure[^>]*>.*?</figure>', a.doc, re.S)
    if not a.exige(fig is not None and "apa-panel-fijo" in fig.group(0),
                   "el documento lleva la figura del plano"):
        return
    trozos = re.split(r'(?=<svg class="apa-panel-)', fig.group(0))
    paneles = {re.match(r'<svg class="(apa-panel-[a-z]+)"', z).group(1): z
               for z in trozos if z.startswith('<svg class="apa-panel-')}
    a.exige(set(paneles) == {"apa-panel-fijo", "apa-panel-k"}, "la figura tiene sus dos paneles",
            f"{sorted(paneles)}")
    if len(paneles) != 2:
        return
    # Los rótulos van debajo del cuadro, «✚ denso: 12 sedes dentro»: dentro de
    # él tapaban las sedes que contaban (revisión 2).
    izq = re.findall(r": (\d+) sedes? dentro<", paneles["apa-panel-fijo"])
    der = re.findall(r": radio ([\d.]+) km<", paneles["apa-panel-k"])
    a.exige(izq == [str(s["parzen_conteo"]) for s in sitios],
            "el panel de radio fijo rotula los conteos de los tres sitios", f"{izq}")
    a.exige(der == [f"{s['knn_radio']:.2f}" for s in sitios],
            "el panel de k fijo rotula los radios de los tres sitios", f"{der}")
    a.exige(all('aria-label="' in z[:200] for z in paneles.values()),
            "cada panel tiene su texto alternativo")


def main() -> int:
    bib = estructurales_de_la_bibliografia()
    a = Auditor(
        capitulo=DOCUMENTO,
        var_entorno="APENDICEA_HTML",
        jsons=["apendicea_datos.json", "apendicea_soluciones.json"],
        estructurales=ESTRUCTURALES | bib,
    )
    print(f"\n=== audita_texto_apendicea.py · {a.ruta.name} ===")
    print(f"  ---  {len(bib)} cifras de la bibliografía declaradas estructurales: "
          f"{sorted(bib, key=lambda s: (len(s), s))[:12]}…")
    a.cifras()
    a.soluciones("apendicea_soluciones.json")
    a.temario(DEBE_CUBRIR)
    a.fuentes(FUENTES)
    a.afirmaciones(AFIRMACIONES)
    a.accesibilidad()
    respuestas_publicadas(a)
    decimales_con_punto(a)
    titulos_sin_acento_grave(a)
    motor_al_dia(a)
    figura_del_plano(a)
    a.formulas_escapadas()
    a.codificacion()
    a.enlaces()
    a.coherencia(CADENAS, ORDENES)
    a.peso(TOPE_KB)
    return a.cierre()


if __name__ == "__main__":
    sys.exit(main())
