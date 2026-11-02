#!/usr/bin/env python3
"""
describe_mapa.py — las guardas de la descripción larga de los mapas

Material de Estadística Espacial 2026-II (20929). 2026-11-02.

POR QUÉ EXISTE. Cada `.geomapa` lleva desde esta fecha una `descripcion`:
lo que se VE en el mapa —dónde está lo alto, cuántas manchas, en qué
localidad—, que el motor pone en «Describir el mapa» y enlaza al lienzo
para el lector de pantalla. La etiqueta (`aria-label`) dice qué es el mapa;
la descripción, qué enseña. Sin ella, quien no ve el lienzo se queda con el
nombre del mapa y sin el mapa.

Las cifras y los nombres de esas descripciones los publica R (D10). Aquí
viven las comprobaciones que comparten los siete ensambladores, para que no
haya siete copias que se separen:

  · `revisa_textos`: que cada mapa que el documento usa tenga su
    descripción, que no sea corta, que no repita la etiqueta, que no lleve el
    circunflejo combinante (ver la memoria del sombrero: en negrita se pierde)
    y que un mapa que cambia de estado tenga un texto por estado;
  · `zona_dibujada`: la zona («norte», «suroccidente»…) de una celda de un
    ráster PUBLICADO, contada sobre el dibujo —fila 0 arriba, como lo pinta
    `geomapaPintaRejilla`—. Sirve para comprobar que la palabra que R escribe
    sobre las coordenadas dice lo mismo que el mapa que se ve: el capítulo 5
    publicó diez rásteres volteados norte-sur hasta el 2026-10-27;
  · `lista_y`: «Suba, Kennedy y Bosa».

No calcula ninguna cifra que se publique: devuelve palabras, índices y
problemas. `sin_aritmetica.py` no lo mira porque no formatea números.

Uso:  python3 precalculo/describe_mapa.py --prueba   (la guarda se rompe a sí misma)
      y, como módulo, desde cada `ensambla_capN.py`.
"""
from __future__ import annotations

import json
import re

# Por debajo de esto una «descripción» es otra etiqueta: medido sobre las 56
# etiquetas de main 63edbd1, la mediana es de 100 caracteres.
MINIMO = 120

ZONAS = ("noroccidente", "norte", "nororiente", "occidente", "centro", "oriente",
         "suroccidente", "sur", "suroriente")


def lista_y(nombres: list[str]) -> str:
    """«A», «A y B», «A, B y C»."""
    nombres = list(nombres)
    if len(nombres) <= 1:
        return "".join(nombres)
    return ", ".join(nombres[:-1]) + " y " + nombres[-1]


def zona_por_tercios(fx: float, fy_desde_arriba: float) -> str:
    """La zona de un punto por tercios, con x de occidente a oriente y y de norte a sur."""
    eo = ("occidente", "", "oriente")[min(2, int(fx * 3))]
    ns = ("norte", "", "sur")[min(2, int(fy_desde_arriba * 3))]
    if not ns and not eo:
        return "centro"
    if not ns:
        return eo
    if not eo:
        return ns
    return {"norte": "nor", "sur": "sur"}[ns] + eo


def zona_dibujada(g: dict, celda: int) -> str:
    """La zona de la celda `celda` (índice plano, fila 0 = norte) de un ráster publicado."""
    nx, ny = g["nx"], g["ny"]
    f, c = divmod(celda, nx)
    return zona_por_tercios((c + 0.5) / nx, (f + 0.5) / ny)


def celda_maxima(g: dict) -> int:
    """El índice de la celda más alta del ráster publicado (cuantizado)."""
    zq = g["zq"]
    return max(range(len(zq)), key=lambda i: (zq[i] if zq[i] is not None and zq[i] >= 0 else -1))


def registrados(js: str) -> dict[str, str]:
    """{id: cuerpo} de cada `GEOMAPAS['id'] = { … };` del bloque de JavaScript.

    El cuerpo llega hasta el `};` que cierra el registro al nivel de sangría
    con el que se abrió, que es como lo escriben los siete ensambladores.
    """
    out = {}
    for m in re.finditer(r"^( *)GEOMAPAS\['([^']+)'\]\s*=\s*\{", js, re.M):
        sangria, ident = m.group(1), m.group(2)
        fin = js.find("\n" + sangria + "};", m.end())
        una_linea = js.find("};", m.end())
        corte = js.find("\n", m.end())
        # Registro de una línea: `GEOMAPAS['x'] = { fuente: … };`
        if una_linea != -1 and (corte == -1 or una_linea < corte):
            out[ident] = js[m.end():una_linea]
        else:
            out[ident] = js[m.end():fin if fin != -1 else len(js)]
    return out


def etiqueta_de(cuerpo: str) -> str:
    """La `etiqueta` fija de un registro, si la trae como literal; si no, cadena vacía."""
    m = re.search(r'etiqueta:\s*("(?:[^"\\]|\\.)*")', cuerpo)
    if m:
        return json.loads(m.group(1))
    m = re.search(r"etiqueta:\s*'((?:[^'\\]|\\.)*)'\s*[,}\n]", cuerpo)
    return m.group(1) if m else ""


def revisa_textos(marcado: str, js: str, textos: dict[str, list[str]],
                  etiquetas: dict[str, str] | None = None) -> list[str]:
    """Los problemas de las descripciones de un documento; lista vacía si no hay.

    `marcado`: el HTML de los módulos (donde están los `data-geomapa`).
    `js`: el bloque donde se registran los mapas.
    `textos`: {id: [texto, …]} — uno por estado del mapa, todos los que el
        documento puede llegar a mostrar.
    `etiquetas`: {id: aria-label fijo}, cuando el registro lo trae.
    """
    problemas = []
    usados = sorted(set(re.findall(r'data-geomapa="([^"]+)"', marcado)))
    reg = registrados(js)
    for ident in usados:
        cuerpo = reg.get(ident)
        if cuerpo is None:
            problemas.append(f"{ident}: se usa y no está registrado")
            continue
        if not re.search(r"\bdescripcion\s*:", cuerpo):
            problemas.append(f"{ident}: el registro no trae `descripcion`")
        lista = textos.get(ident)
        if not lista:
            problemas.append(f"{ident}: sin textos declarados para la guarda")
            continue
        for k, t in enumerate(lista):
            que = f"{ident}[{k}]" if len(lista) > 1 else ident
            if len(t) < MINIMO:
                problemas.append(f"{que}: descripción de {len(t)} caracteres (mínimo {MINIMO})")
            if "̂" in t:
                problemas.append(f"{que}: lleva el circunflejo combinante U+0302")
            if re.search(r"[{}]|\bNone\b|\bnan\b", t):
                problemas.append(f"{que}: lleva restos de plantilla («{t[:60]}…»)")
            etq = (etiquetas or {}).get(ident) or etiqueta_de(cuerpo)
            if etq and (t.strip() == etq.strip() or etq.strip() in t):
                problemas.append(f"{que}: la descripción repite la etiqueta")
        if len(set(lista)) != len(lista):
            problemas.append(f"{ident}: dos estados con la misma descripción")
    for ident in textos:
        if ident not in usados:
            problemas.append(f"{ident}: hay descripción para un mapa que el documento no usa")
    return problemas


# =====================================================================
# LA GUARDA TAMBIÉN SE PRUEBA. Un «OK» que nadie ha visto fallar puede ser
# incapaz de dispararse (T0.5). Cada mutante rompe UNA cosa de un documento
# de juguete que pasa limpio, y la guarda tiene que nombrarla.
# =====================================================================
def prueba() -> int:
    largo = "Lo alto cae en el norte y lo bajo en el sur; " * 4
    otro = "Con el otro estado lo alto cae en el oriente; " * 4
    marcado = '<div data-geomapa="a"></div><div data-geomapa="b"></div>'
    js = ("    GEOMAPAS['a'] = { fuente: X, etiqueta: \"Mapa A de prueba\", descripcion: \"…\" };\n"
          "    GEOMAPAS['b'] = {\n      fuente: () => Y,\n      descripcion: () => D[i]\n    };\n")
    textos = {"a": [largo], "b": [largo + "uno", otro]}
    limpio = revisa_textos(marcado, js, textos)
    if limpio:
        print("  MAL  el documento de juguete no pasa limpio:", limpio)
        return 1
    mutantes = [
        ("un mapa usado sin registro", marcado + '<div data-geomapa="c"></div>', js, textos, "no está registrado"),
        ("un registro sin `descripcion`", marcado, js.replace(", descripcion: \"…\"", ""), textos, "no trae"),
        ("una descripción corta", marcado, js, {**textos, "a": ["Corto."]}, "caracteres"),
        ("el circunflejo combinante", marcado, js, {**textos, "a": [largo + "λ̂"]}, "U+0302"),
        ("restos de plantilla", marcado, js, {**textos, "a": [largo + "{n(x)}"]}, "restos"),
        ("la etiqueta repetida", marcado, js, {**textos, "a": [largo + "Mapa A de prueba"]}, "repite la etiqueta"),
        ("dos estados con el mismo texto", marcado, js, {**textos, "b": [otro, otro]}, "misma descripción"),
        ("un mapa sin textos para la guarda", marcado, js, {"a": [largo]}, "sin textos"),
        ("una descripción de un mapa ausente", marcado, js, {**textos, "z": [largo]}, "no usa"),
    ]
    malos = 0
    for nombre, m, j, t, espera in mutantes:
        p = revisa_textos(m, j, t)
        if any(espera in x for x in p):
            print(f"  OK   mutante «{nombre}» cazado")
        else:
            malos += 1
            print(f"  MAL  mutante «{nombre}» NO cazado: {p}")
    print(f"\n  {len(mutantes) - malos} de {len(mutantes)} mutantes cazados")
    return 1 if malos else 0


if __name__ == "__main__":
    import sys
    if sys.argv[1:] == ["--prueba"]:
        sys.exit(prueba())
    sys.exit("Uso: python3 precalculo/describe_mapa.py --prueba")
