#!/usr/bin/env python3
"""
mide_duraciones_cap1.py — cuánto se tarda en leer cada módulo del capítulo 1

Material de Estadística Espacial 2026-II (20929). R3 · T3.4 (H-08, D8).

POR QUÉ EXISTE. Las duraciones de la barra de navegación eran una cifra
escrita a mano y retocada a ojo ronda tras ronda («un minuto por cada 200
palabras añadidas», desde la duración que el módulo tenía al cerrar R1). La
lectura de estudiante de 2026-11-13 (H-08) midió el capítulo y encontró el
módulo 2 a 11 minutos de lo declarado y el 3 a otros 11. Una duración es una
promesa al estudiante sobre su semana, y una promesa sin medida detrás es una
cifra a mano. Este guion la mide desde el HTML ENSAMBLADO —no desde el
ensamblador—, de forma determinista, y `ensambla_cap1.py` se detiene si una
duración declarada se sale de ±15 % de lo que aquí sale (el criterio de
aceptación del plan de mejora, fase 1).

LAS TASAS. Son los supuestos de H-08, cada uno fijado en UN valor:

  · PROSA: 200 palabras por minuto. Es la cifra de H-08 para lectura de
    estudio, no de lectura corrida. Cuentan todas las palabras visibles del
    módulo —párrafos, cajas, títulos, pies, celdas de tabla, entradillas de
    los simuladores—, sin las fórmulas, sin el código y sin lo oculto.
  · FÓRMULA: ×1.4 sobre las palabras de cada bloque (párrafo, elemento de
    lista, celda, pie) que lleve al menos una fórmula, \\(…\\) o $$…$$. H-08
    daba ×1.4–1.5; se fija el extremo bajo porque el factor se aplica a TODO
    bloque con una fórmula, también a los que solo nombran una letra, y con
    ×1.5 esos bloques ligeros quedarían sobrecargados. Las fórmulas en sí no
    suman palabras: su coste es el factor sobre el texto que las lee.
  · SIMULADOR: 2.5 minutos por cada `data-simulador`, el punto medio de los
    2–3 de H-08. Cubre mover los mandos y leer la lectura que el JavaScript
    escribe, que no está en el HTML. Lo que va dentro del simulador —su mapa,
    su lienzo, su tabla— no se cuenta otra vez; su entradilla sí, como prosa.
  · MAPA, TABLA O FIGURA SUELTA: 1 minuto por cada `.geomapa`, `<table>`,
    `<canvas>` o glosario que no esté dentro de un simulador. Es el tiempo de
    mirarlo; las palabras de sus celdas ya cuentan como prosa.
  · CÓDIGO: 7.5 líneas por minuto, el punto medio de las 7–8 de H-08. Se leen
    las líneas no vacías de cada `<pre>` visible: en un par de pestañas R y
    Python solo está visible la de R, y es la que se cuenta. Las pestañas se
    leen una, no las dos.
  · PREGUNTA DE AUTOEVALUACIÓN: 1.2 minutos cada una, leída, contestada y con
    su retroalimentación. Se cuentan las entradas `tipo:` de su
    `AUTOEVALUACIONES[...]`.

QUÉ ES CAMINO PRINCIPAL Y QUÉ NO. La duración de la barra es la del camino
principal: lo que el módulo enseña sin abrir nada. Aparte, y nunca en la
barra:

  · cada panel plegable de deducción (`.derivacion-panel`), con su tiempo;
  · la pista y la solución de cada ejercicio del módulo 12 (`.ejercicio-panel`):
    el módulo 12 se mide como leer el cuestionario, hacerlo y leer los
    enunciados de los ejercicios. Resolverlos no cuenta: ni se mide ni se
    publica, porque un tiempo de resolución sería una cifra sin nada detrás;
  · lo demás que arranca oculto (la pestaña de Python, los pies que aparecen
    al pulsar un mando) no cuenta;
  · la lista de referencias del módulo 12 (`ul.lista-fuentes`, la que escribe
    genera_referencias.py) tampoco: una bibliografía se consulta, no se lee
    de corrido. Las «Lecturas de este capítulo», que son prosa, sí cuentan.

EL GLOSARIO SÍ SE LEE ENTERO, Y LA BIBLIOGRAFÍA NO (decisión de la ronda 2 de
T3.4, V-15). Los dos son material de consulta, pero no ocupan el mismo sitio:
el glosario es el módulo 11, con duración propia en la barra, y quien abre ese
módulo va a leer la notación del curso fila a fila —es su contenido, no un
anexo—, así que sus filas cuentan como prosa con fórmula (las pinta el
JavaScript desde `GLOSARIOS[…]`, y de ahí se leen) más un minuto de tabla. La
bibliografía es un apéndice del módulo 12, que trata de otra cosa: contarla
alargaría el cuestionario con una lista que nadie lee de corrido.

LO QUE NO MIDE, para que nadie lo lea de más: el tiempo de un estudiante
concreto. Mide el documento con unas tasas declaradas; cambiar una tasa cambia
todas las duraciones a la vez, y por eso están aquí arriba y en un solo sitio.

Uso:  python3 precalculo/mide_duraciones_cap1.py [ruta.html]
      (por defecto, Htmls_Espacial/capitulo-1-datos-espaciales.html)
"""
from __future__ import annotations

import html
import json
import pathlib
import re
import sys
from html.parser import HTMLParser

RAIZ = pathlib.Path(__file__).resolve().parent.parent
CAPITULO = RAIZ / "Htmls_Espacial" / "capitulo-1-datos-espaciales.html"

PALABRAS_POR_MIN = 200.0
FACTOR_FORMULA = 1.4
MIN_SIMULADOR = 2.5
MIN_MAPA_O_TABLA = 1.0
LINEAS_CODIGO_POR_MIN = 7.5
MIN_PREGUNTA = 1.2

# Cuánto puede apartarse la duración declarada de la medida (criterio del plan).
TOLERANCIA = 0.15

_BLOQUES = {"p", "li", "td", "th", "caption", "h1", "h2", "h3", "h4", "h5", "h6",
            "div", "summary", "figcaption", "blockquote", "dt", "dd", "button"}
_VACIOS = {"br", "img", "input", "hr", "meta", "link", "source", "wbr", "col"}
_FORMULA = re.compile(r"\\\(.+?\\\)|\$\$.+?\$\$", re.S)


class _Lector(HTMLParser):
    """Recorre un `<template>` y reparte lo que encuentra por «cubos».

    El cubo «principal» es la barra de navegación; cada panel de deducción y
    cada panel de ejercicio tiene el suyo; lo oculto restante va a «oculto».
    """

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.pila: list[dict] = []
        self.cubos: dict[str, dict] = {}
        self.texto: list[str] = []

    # -- dónde estamos ------------------------------------------------------
    def _cubo_actual(self) -> str:
        for e in reversed(self.pila):
            if e.get("cubo"):
                return e["cubo"]
        return "principal"

    def _dentro(self, clave: str) -> bool:
        return any(e.get(clave) for e in self.pila)

    def _cubo(self, nombre: str) -> dict:
        return self.cubos.setdefault(nombre, {
            "palabras": 0, "palabras_formula": 0, "simuladores": 0, "mapas_tablas": 0,
            "lineas_codigo": 0, "preguntas": 0, "quizzes": []})

    def _vacia(self):
        """Cierra el bloque de texto en curso y lo cuenta en su cubo."""
        t = "".join(self.texto)
        self.texto = []
        if self._dentro("pre"):
            return
        con_formula = bool(_FORMULA.search(t))
        palabras = len(_FORMULA.sub(" ", t).split())
        if not palabras:
            return
        c = self._cubo(self._cubo_actual())
        c["palabras_formula" if con_formula else "palabras"] += palabras

    # -- el recorrido -------------------------------------------------------
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        clases = (a.get("class") or "").split()
        if tag in _BLOQUES:
            self._vacia()
        e = {"tag": tag}
        if "derivacion-panel" in clases:
            e["cubo"] = "panel:" + a.get("id", "?")
        elif "ejercicio-panel" in clases:
            e["cubo"] = "ejercicio:" + a.get("id", "?")
        elif "hidden" in a:
            e["cubo"] = "oculto"
        elif "lista-fuentes" in clases:
            # La lista de referencias se consulta, no se lee de corrido.
            e["cubo"] = "consulta"
        if tag in ("script", "style"):
            e["cubo"] = "oculto"
        if tag == "pre":
            e["pre"] = True
            e["lineas"] = []
        cubo = e.get("cubo") or self._cubo_actual()
        en_sim = self._dentro("sim")
        if a.get("data-simulador") is not None:
            if not en_sim:
                self._cubo(cubo)["simuladores"] += 1
            e["sim"] = True
        elif not en_sim and ((a.get("data-geomapa") is not None and "geomapa" in clases)
                             or tag in ("table", "canvas") or a.get("data-glosario") is not None):
            self._cubo(cubo)["mapas_tablas"] += 1
        if a.get("data-quiz") is not None:
            self._cubo(cubo)["quizzes"].append(a["data-quiz"])
        if a.get("data-glosario") is not None:
            self._cubo(cubo).setdefault("glosarios", []).append(a["data-glosario"])
        if tag not in _VACIOS:
            self.pila.append(e)

    def handle_endtag(self, tag):
        if tag in _VACIOS:
            return
        if tag in _BLOQUES:
            self._vacia()
        # Sacar hasta la etiqueta que cierra (tolera un cierre implícito).
        for i in range(len(self.pila) - 1, -1, -1):
            if self.pila[i]["tag"] == tag:
                e = self.pila[i]
                del self.pila[i:]
                if e.get("pre"):
                    lineas = [l for l in "".join(e["lineas"]).splitlines() if l.strip()]
                    cubo = e.get("cubo") or self._cubo_actual()
                    self._cubo(cubo)["lineas_codigo"] += len(lineas)
                return

    def handle_data(self, data):
        for e in reversed(self.pila):
            if e.get("pre"):
                e["lineas"].append(data)
                return
        self.texto.append(data)

    def close(self):
        super().close()
        self._vacia()


def _preguntas(doc: str, ident: str) -> int:
    i = doc.find(f"AUTOEVALUACIONES['{ident}'] = [")
    if i < 0:
        raise SystemExit(f"mide_duraciones_cap1: no encuentro AUTOEVALUACIONES['{ident}']")
    j = doc.find("\n    ];", i)
    return len(re.findall(r"\btipo: '", doc[i:j]))


def _palabras_glosario(doc: str, ident: str) -> int:
    """Palabras de las filas del glosario, que pinta el JavaScript y no están en el HTML."""
    m = re.search(rf"GLOSARIOS\['{re.escape(ident)}'\] = (\{{.*?\}});\n", doc)
    if not m:
        raise SystemExit(f"mide_duraciones_cap1: no encuentro GLOSARIOS['{ident}']")
    g = json.loads(m.group(1))
    total = 0
    for fila in g["filas"]:
        for v in fila.values():
            if isinstance(v, str):
                total += len(_FORMULA.sub(" ", html.unescape(re.sub(r"<[^>]+>", " ", v))).split())
    return total


def minutos(c: dict) -> float:
    return (c["palabras"] / PALABRAS_POR_MIN
            + c["palabras_formula"] * FACTOR_FORMULA / PALABRAS_POR_MIN
            + c["simuladores"] * MIN_SIMULADOR
            + c["mapas_tablas"] * MIN_MAPA_O_TABLA
            + c["lineas_codigo"] / LINEAS_CODIGO_POR_MIN
            + c["preguntas"] * MIN_PREGUNTA)


def mide(doc: str) -> list[dict]:
    """Una entrada por módulo: el camino principal y, aparte, cada panel."""
    salida = []
    k = 1
    while True:
        m = re.search(rf'<template id="module-{k}">(.*?)</template>', doc, re.S)
        if not m:
            break
        lector = _Lector()
        lector.feed(m.group(1))
        lector.close()
        cubos = lector.cubos
        for c in cubos.values():
            c["preguntas"] = sum(_preguntas(doc, q) for q in c["quizzes"])
            for g in c.get("glosarios", []):
                # Las filas del glosario definen símbolos: se leen como prosa con fórmula.
                c["palabras_formula"] += _palabras_glosario(doc, g)
        principal = cubos.get("principal") or lector._cubo("principal")
        salida.append({
            "modulo": k,
            "principal": principal,
            "min_principal": minutos(principal),
            "paneles": {n.split(":", 1)[1]: minutos(c) for n, c in cubos.items() if n.startswith("panel:")},
            "ejercicios": {n.split(":", 1)[1]: minutos(c) for n, c in cubos.items()
                           if n.startswith("ejercicio:")},
        })
        k += 1
    return salida


def declaradas(doc: str) -> list[int]:
    """Las duraciones que la barra de navegación publica, en el orden de los módulos."""
    i = doc.find("const courseData = {")
    j = doc.find("\n    };", i)
    return [int(x) for x in re.findall(r'duration: "(\d+) min"', doc[i:j])]


def main(argv: list[str]) -> int:
    ruta = pathlib.Path(argv[0]) if argv else CAPITULO
    doc = ruta.read_text(encoding="utf-8")
    med = mide(doc)
    dec = declaradas(doc)
    print(f"mide_duraciones_cap1.py · {ruta.name}")
    print(f"tasas: {PALABRAS_POR_MIN:g} palabras/min · ×{FACTOR_FORMULA:g} con fórmula · "
          f"{MIN_SIMULADOR:g} min/simulador · {MIN_MAPA_O_TABLA:g} min/mapa o tabla · "
          f"{LINEAS_CODIGO_POR_MIN:g} líneas/min · {MIN_PREGUNTA:g} min/pregunta\n")
    print(" M  palabras  (con fórm.)  sim  map/tab  líneas  preg   medido  declarado    Δ      paneles")
    tot_p = tot_d = tot_pan = 0.0
    fuera = 0
    for e, d in zip(med, dec + [None] * (len(med) - len(dec))):
        c = e["principal"]
        pan = sum(e["paneles"].values())
        tot_p += e["min_principal"]
        tot_pan += pan
        tot_d += d or 0
        rel = (d - e["min_principal"]) / e["min_principal"] if d else float("nan")
        marca = "" if d and abs(rel) <= TOLERANCIA else "  ← fuera de ±15 %"
        fuera += bool(marca)
        print(f"{e['modulo']:>2}  {c['palabras']:>8}  {c['palabras_formula']:>11}  {c['simuladores']:>3}  "
              f"{c['mapas_tablas']:>7}  {c['lineas_codigo']:>6}  {c['preguntas']:>4}   "
              f"{e['min_principal']:6.1f}  {d if d else '—':>9}  {rel:+6.1%}  {pan:6.1f}{marca}")
        for pid, t in e["paneles"].items():
            print(f"      panel {pid}: {t:.1f} min")
        for pid, t in e["ejercicios"].items():
            print(f"      {pid}: {t:.1f} min (fuera de la barra)")
    print(f"\ncamino principal: {tot_p:.1f} min · declarado: {tot_d:.0f} min · "
          f"paneles: {tot_pan:.1f} min · con paneles: {tot_p + tot_pan:.1f} min")
    return 1 if fuera else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
