#!/usr/bin/env python3
"""
ensambla_proyecto.py — Construye la guía del proyecto integrador del Corte III.

Material de Estadística Espacial 2026-II (20929). Ver PLAN_Proyecto_Integrador.md.

Parte de `plantilla/plantilla-capitulo.html` y SUSTITUYE regiones concretas,
como `ensambla_preparcial2.py`, y su forma —prosa con marcadores, cifras en un
`datos.py`, tablas generadas— es la del proyecto aplicado de Diseño de
Experimentos, que se publicó el 9 oct y se auditó el 20 oct de 2026.

    python3 precalculo/ensambla_proyecto.py             → escribe la guía y copia la plantilla .Rmd
    python3 precalculo/ensambla_proyecto.py --revisar   → todas las comprobaciones, sin escribir

DE DÓNDE SALE CADA COSA
  · La prosa: `proyecto/modulos/m*.html`, con marcadores `@@CLAVE@@`.
  · Las cifras —fechas, pesos, rúbrica, tope, N mínimo, réplicas—:
    `proyecto/datos.py`, y SOLO de ahí. La tabla de potencia, de
    `proyecto/potencia.json`, que escribe `proyecto/potencia.R`.
  · Las tablas se generan aquí desde `datos.py`: una tabla tecleada en la
    prosa sería la segunda copia de una cifra, y la que nadie miraría al
    cambiarla.
  · La rúbrica va dos veces y desde el mismo dato: una tabla de criterios y
    puntos, que se lee y se imprime, y el componente `.rubrica` de la
    plantilla con los descriptores, que es para lo que se injertó (D8 del
    plan maestro).

LAS REGLAS DE LA CONJUNTA NO ESTÁN AQUÍ. Viven en el módulo 8 de la guía de
Series de Tiempo, y el módulo 8 de esta guía solo las enlaza (DE10). El
auditor (frente H) prohíbe que aparezcan copiadas.

Reejecutable: dos ejecuciones producen el mismo archivo.
"""
from __future__ import annotations

import html as _html
import json
import pathlib
import re
import shutil
import sys

AQUI = pathlib.Path(__file__).resolve().parent
RAIZ = AQUI.parent
PLANTILLA = RAIZ / "plantilla" / "plantilla-capitulo.html"
FUENTES = RAIZ / "proyecto"
SITIO = RAIZ / "Htmls_Espacial"
DESTINO = SITIO / "proyecto-integrador-corte-iii.html"
RMD_FUENTE = FUENTES / "plantilla-informe.Rmd"
RMD_DESTINO = SITIO / "proyecto-integrador-plantilla.Rmd"

sys.path.insert(0, str(FUENTES))
sys.path.insert(0, str(AQUI))
import datos as D  # noqa: E402
from pon_boton_indice import aplica as aplica_boton  # noqa: E402

TITULO = "Proyecto integrador · Corte III"
PRESUPUESTO_KB = 600

# Los diez módulos: (n, título, duración, fuente, objetivo).
MODULOS = [
    (1, "Cómo funciona el proyecto", "10 min", "m1-como-funciona.html",
     "Saber qué se te pide, cuándo y cuánto pesa cada cosa, antes de elegir el territorio."),
    (2, "Qué datos valen", "12 min", "m2-que-datos-valen.html",
     "Reconocer si un territorio y una variable dan para un proyecto antes de escribir la ficha."),
    (3, "El repositorio en GitHub", "8 min", "m3-repositorio.html",
     "Montar el repositorio donde vive todo el proyecto y saber qué cuenta como entrega."),
    (4, "Hito 1 · Ficha del tema", "5 min", "m4-ficha.html",
     "Proponer el territorio y la pregunta en una ficha corta, a tiempo para cambiarlos."),
    (5, "Hito 2 · Preregistro", "15 min", "m5-preregistro.html",
     "Dejar fijado el protocolo de inferencia espacial antes de calcular un solo Moran."),
    (6, "Hito 3 · Avance", "8 min", "m6-avance.html",
     "Entregar la unión, el mapa y la W cuando todavía se puede arreglar lo que salió mal."),
    (7, "Hito 4 · Informe y código", "12 min", "m7-informe.html",
     "Contar el análisis entero en un informe que se reproduce de principio a fin."),
    (8, "La opción conjunta con Series de Tiempo", "4 min", "m8-conjunta.html",
     "Saber dónde están las reglas del proyecto conjunto y cómo califica Espacial su mitad."),
    (9, "La exposición", "6 min", "m9-exposicion.html",
     "Contar el proyecto en el tiempo justo y defender cada decisión."),
    (10, "La rúbrica", "10 min", "m10-rubrica.html",
     "Saber con qué se califica cada entrega, y qué separa un nivel de otro."),
]
MODULO_RUBRICA = next(n for n, t, *_ in MODULOS if t == "La rúbrica")


# ---------------------------------------------------------------------------
# 1. Utilidades
# ---------------------------------------------------------------------------
def lee(ruta: pathlib.Path) -> str:
    if not ruta.exists():
        sys.exit(f"PARADO: falta {ruta}")
    return ruta.read_text(encoding="utf-8")


def sustituye(texto: str, ancla: str, nuevo: str, que: str) -> str:
    veces = texto.count(ancla)
    if veces != 1:
        sys.exit(f"PARADO: el ancla de «{que}» aparece {veces} veces, no 1.\n        {ancla[:90]!r}")
    print(f"  OK   {que}")
    return texto.replace(ancla, nuevo, 1)


def reemplaza_region(texto, abre, cierra, nuevo, que, max_lineas, min_lineas=0):
    """Sustituye entre `abre` y el primer `cierra` posterior, con DOS topes (de
    `ensambla_taller1.py`): sustituir de más se llevó 270 líneas del motor con
    el informe en verde, y de menos dejó vivos dos simuladores de demostración."""
    if texto.count(abre) != 1:
        sys.exit(f"PARADO: el ancla de apertura de «{que}» aparece {texto.count(abre)} veces, no 1")
    i = texto.index(abre)
    j = texto.index(cierra, i) + len(cierra)
    n_lineas = texto[i:j].count("\n")
    if n_lineas > max_lineas:
        sys.exit(f"PARADO: la región de «{que}» ocupa {n_lineas} líneas y el tope es {max_lineas}")
    if n_lineas < min_lineas:
        sys.exit(f"PARADO: la región de «{que}» ocupa solo {n_lineas} líneas y el mínimo es {min_lineas}")
    print(f"  OK   {que}  ({n_lineas} líneas sustituidas)")
    return texto[:i] + nuevo + texto[j:]


def e(t: str) -> str:
    return _html.escape(t, quote=False)


def cierra(h: dict) -> str:
    return f"{D.frase_fecha(h['fecha'])} a las {D.HORA_ENTREGA}"


def tabla(caption: str, cabecera: list[str], filas: list[list[str]]) -> str:
    th = "".join(f'<th scope="col">{c}</th>' for c in cabecera)
    cuerpo = "\n".join("          <tr>" + "".join(f"<td>{c}</td>" for c in f) + "</tr>" for f in filas)
    return f"""      <table>
        <caption>{caption}</caption>
        <thead>
          <tr>{th}</tr>
        </thead>
        <tbody>
{cuerpo}
        </tbody>
      </table>"""


# ---------------------------------------------------------------------------
# 2. Las tablas, desde datos.py
# ---------------------------------------------------------------------------
def tabla_hitos() -> str:
    filas = []
    for h in D.HITOS:
        peso = "sin nota" if h["id"] == "ficha" else f"{D.puntos_de(h['id'])} %"
        filas.append([str(h["n"]), f"<strong>{e(h['nombre'])}</strong>", e(h["entrega"]),
                      D.frase_fecha(h["fecha"]), str(h["semana"]), peso])
    filas.append(["5", "<strong>Exposición</strong>",
                  f"{D.MINUTOS_EXPOSICION} minutos por equipo y {D.MINUTOS_PREGUNTAS} de preguntas, en clase",
                  "se acuerda en clase", str(D.SEMANA_EXPOSICION), f"{D.puntos_de('exposicion')} %"])
    return tabla(f"Los hitos del proyecto. Las entregas cierran a las {D.HORA_ENTREGA} del día indicado; "
                 "el peso es sobre la nota del proyecto.",
                 ["#", "Hito", "Qué entregas", "Cierra", "Semana", "Peso"], filas)


def tabla_pesos() -> str:
    filas = []
    for b in D.RUBRICA:
        p = D.puntos_de(b["hito"])
        filas.append([e(b["titulo"]), ", ".join(c["id"] for c in b["criterios"]), f"{p} %",
                      f"<strong>{D.pct(p * D.PROYECTO_DEL_CORTE / 100)} %</strong>"])
    return tabla("Reparto de la nota del proyecto. La última columna es sobre la nota del Corte III.",
                 ["Hito", "Criterios", "Del proyecto", "Del corte"], filas)


def tabla_tope() -> str:
    filas = [[e(f["situacion"]), D.nota(f["escrito"]), D.nota(f["exposicion"]), D.nota(f["preguntas"]),
              D.nota(f["sin_tope"]), f"<strong>{D.nota(f['con_tope'])}</strong>"] for f in D.filas_tope()]
    p_esc = sum(D.puntos_de(h) for h in D.HITOS_ESCRITOS)
    return tabla(f"Qué cambia el tope. Lo escrito vale {p_esc} puntos del proyecto, la exposición (E1) "
                 f"{D.CRITERIOS['E1']['puntos']} y las preguntas (E2) {D.CRITERIOS['E2']['puntos']}; "
                 "todo en la escala de 5.",
                 ["Situación", "Escrito", "Exposición (E1)", "Preguntas (E2)", "Sin tope", "Con tope"], filas)


def tabla_retraso() -> str:
    filas = [[str(f["sesiones"]), f"{f['descuento']} %", D.nota(f["nota"])] for f in D.filas_retraso()]
    return tabla(f"El descuento por entrega tardía, sobre una entrega que a tiempo habría sacado "
                 f"{D.nota(D.EJEMPLO_RETRASO)}.",
                 ["Sesiones de retraso", "Descuento", "La nota queda en"], filas)


def tabla_niveles() -> str:
    return tabla("Lo que vale cada nivel, en la escala de 5.", ["Nivel", "Vale"],
                 [[n.capitalize(), D.nota(v)] for n, v in D.NIVELES])


def tabla_potencia() -> str:
    Ns = sorted({f["N"] for f in D.POTENCIA["filas"]})
    rhos = sorted({f["rho"] for f in D.POTENCIA["filas"]})
    filas = [[str(N)] + [f"{D.decimal(100 * D.potencia(N, r), 1)} %" for r in rhos] for N in Ns]
    cab = ["Unidades (N)"] + [("ρ = 0 (tamaño)" if r == 0 else f"ρ = {D.decimal(r, 1)}") for r in rhos]
    return tabla(f"De cada 100 territorios con esa dependencia, en cuántos el Moran por permutación la "
                 f"detecta al 5 %. Simulación con {D.miles(D.POTENCIA['replicas'])} réplicas por casilla.",
                 cab, filas)


def tabla_exigencias() -> str:
    filas = [[f'<a href="{arch}">Capítulo {cap}</a>, módulo {m}', titulo, que,
              ", ".join(crits)] for cap, arch, m, titulo, que, crits in D.EXIGENCIAS]
    # Los títulos llevan `zero.policy` entre comillas invertidas, como en el
    # capítulo; en la tabla van como código.
    for f in filas:
        f[1] = re.sub(r"`([^`]+)`", r"<code>\1</code>", f[1])
    return tabla("Lo que el material ya enseñó y en qué criterio de la rúbrica se califica.",
                 ["Dónde", "Módulo", "Lo que se exige", "Criterios"], filas)


def tabla_rubrica() -> str:
    filas = []
    for b in D.RUBRICA:
        for c in b["criterios"]:
            quien = " <em>(individual)</em>" if c.get("individual") else ""
            filas.append([e(b["titulo"]), f"<strong>{c['id']}</strong>", e(c["nombre"]) + quien,
                          str(c["puntos"])])
    filas.append(["<strong>Total</strong>", "", "", f"<strong>{sum(D.puntos_de(b['hito']) for b in D.RUBRICA)}</strong>"])
    return tabla("Los criterios de la rúbrica y sus puntos sobre 100.",
                 ["Hito", "Criterio", "Qué se califica", "Puntos"], filas)


def rubrica_js() -> str:
    """RUBRICAS['proyecto-integrador'] para el componente `.rubrica`.

    Los niveles van de mayor a menor (el componente colorea por índice), y el
    `rango` de cada uno son los puntos que aporta el criterio en ese nivel:
    puntos × nivel / 5. El componente le añade «pts» y el % de la nota."""
    criterios = []
    for b in D.RUBRICA:
        for c in b["criterios"]:
            foco = c["foco"] + (f" <strong>En la conjunta:</strong> {c['conjunta'][len('En la conjunta, '):]}"
                                if c.get("conjunta") else "")
            niveles = [dict(nombre=n.capitalize(),
                            rango=D.decimal(c["puntos"] * v / 5, 1),
                            observa=c["solido" if n == "sólido" else n])
                       for n, v in reversed(D.NIVELES)]
            criterios.append(dict(clave=c["id"], nombre=c["nombre"], puntos=c["puntos"],
                                  foco=f"{b['titulo']}. {foco}", niveles=niveles))
    spec = dict(titulo="Rúbrica del proyecto integrador", total=100,
                intro="Quince criterios en cuatro bloques: preregistro, avance, informe y exposición. "
                      "Cada nivel aporta los puntos que dice su banda.",
                nota="Cada criterio se califica por separado. Lo escrito es de la pareja; E2 es de "
                     "cada persona y acota lo escrito con el tope del módulo 1.",
                criterios=criterios)
    return ("    RUBRICAS['proyecto-integrador'] = "
            + json.dumps(spec, ensure_ascii=False, indent=2).replace("\n", "\n    ") + ";\n")


# ---------------------------------------------------------------------------
# 3. Los marcadores de la prosa
# ---------------------------------------------------------------------------
def marcadores() -> dict[str, str]:
    H = D.HITO
    ej0 = D.filas_tope()[0]
    (si_nombre, si_n), (no_nombre, no_n) = D.UNIDADES_EJEMPLO
    tam = [f["potencia"] for f in D.POTENCIA["filas"] if f["rho"] == 0]
    criterios_conjunta = [c["id"] for b in D.RUBRICA for c in b["criterios"] if c.get("conjunta")]
    m = {
        "TABLA_HITOS": tabla_hitos(),
        "TABLA_PESOS": tabla_pesos(),
        "TABLA_TOPE": tabla_tope(),
        "TABLA_NIVELES": tabla_niveles(),
        "TABLA_RETRASO": tabla_retraso(),
        "TABLA_POTENCIA": tabla_potencia(),
        "TABLA_EXIGENCIAS": tabla_exigencias(),
        "TABLA_RUBRICA": tabla_rubrica(),
        "DESCUENTO": str(D.DESCUENTO_POR_SESION),
        "USUARIO_DOCENTE": D.USUARIO_DOCENTE,
        "NOMBRE_REPO": D.NOMBRE_REPO,
        "ETIQUETAS": ", ".join(f"<code>{D.ETIQUETA[h['id']]}</code>" for h in D.HITOS[:-1])
                     + f" e <code>{D.ETIQUETA[D.HITOS[-1]['id']]}</code>",
        "DIA_EXPOSICION": D.DIA_EXPOSICION,
        "CLASE_EXPO_1": D.frase_fecha(D.CLASES_EXPOSICION[0]),
        "CLASE_EXPO_2": D.frase_fecha(D.CLASES_EXPOSICION[1]),
        "HORA_ENTREGA": D.HORA_ENTREGA,
        "CANAL_ENTREGA": D.CANAL_ENTREGA,
        "DUDAS_EN": D.DUDAS_EN,
        "TUTORIAS": D.tutorias_en(),
        "SEMANA_EXPOSICION": str(D.SEMANA_EXPOSICION),
        "SEMANA_EXPOSICION_FRASE": D.frase_semana(D.SEMANA_EXPOSICION),
        "MINUTOS_EXPOSICION": str(D.MINUTOS_EXPOSICION),
        "MINUTOS_PREGUNTAS": str(D.MINUTOS_PREGUNTAS),
        "PROYECTO_DEL_CORTE": str(D.PROYECTO_DEL_CORTE),
        "QUICES_DEL_CORTE": str(D.QUICES_DEL_CORTE),
        "CORTE_III_DEL_CURSO": str(D.CORTE_III_DEL_CURSO),
        "PROYECTO_DEL_CURSO": D.pct(D.PROYECTO_DEL_CURSO),
        "NIVELES": " · ".join(f"<strong>{n}</strong>" for n, _ in D.NIVELES),
        "UMBRAL": D.nota(D.UMBRAL_TOPE),
        "UMBRAL_DIV": D.divisor(D.UMBRAL_TOPE),
        "EJ0_SIN": D.nota(ej0["sin_tope"]),
        "EJ0_CON": D.nota(ej0["con_tope"]),
        "ACEPTABLE_DIV": D.divisor(D.VALOR_NIVEL["aceptable"]).replace(".", "{,}"),
        "EJ_PUNTOS": D.decimal(7 * D.VALOR_NIVEL["aceptable"] / 5, 1).replace(",", "{,}"),
        "PALABRAS_FICHA": str(D.PALABRAS_FICHA),
        "PAGINAS_PREREGISTRO": str(D.PAGINAS_PREREGISTRO),
        "PAGINAS_INFORME": str(D.PAGINAS_INFORME),
        "PLANTILLA_RMD": RMD_DESTINO.name,
        "RESPUESTA_FICHA": D.frase_fecha(D.RESPUESTA_FICHA),
        "N_MINIMO": str(D.N_MINIMO),
        "UNIDAD_SI_NOMBRE": si_nombre, "UNIDAD_SI_N": str(si_n),
        "UNIDAD_NO_NOMBRE": no_nombre, "UNIDAD_NO_N": str(no_n),
        "POT_MIN_05": str(round(100 * D.potencia(D.N_MINIMO, 0.5))),
        "POT_NSIM": str(D.POTENCIA["nsim"]),
        "POT_REPLICAS": D.miles(D.POTENCIA["replicas"]),
        "TAM_MIN": D.decimal(100 * min(tam), 1), "TAM_MAX": D.decimal(100 * max(tam), 1),
        "N_EJEMPLO_NSIM": str(D.N_EJEMPLO_NSIM),
        "NSIM_EJEMPLO": D.miles(D.nsim_minimo_bonferroni(D.N_EJEMPLO_NSIM)),
        "NSIM_HABITUAL": str(D.NSIM_HABITUAL),
        "NSIM_CAPITULO": D.miles(D.NSIM_CAPITULO),
        "N_MAX_NSIM_CAPITULO": D.miles(max(N for N in range(1, 5000)
                                           if D.nsim_minimo_bonferroni(N) <= D.NSIM_CAPITULO)),
        "SERIES_ENLACE": D.SERIES_ENLACE_CONJUNTA,
        "SERIES_MODULO": str(D.SERIES_MODULO_CONJUNTA),
        "MODULO_RUBRICA": str(MODULO_RUBRICA),
        "CRITERIOS_CONJUNTA": ", ".join(criterios_conjunta[:-1]) + " e " + criterios_conjunta[-1],
    }
    for clave, h in (("FICHA", H["ficha"]), ("PREREGISTRO", H["preregistro"]),
                     ("AVANCE", H["avance"]), ("INFORME", H["informe"])):
        m[f"{clave}_CIERRA"] = cierra(h)
        m[f"{clave}_SEMANA"] = str(h["semana"])
        m[f"ETIQUETA_{clave}"] = D.ETIQUETA[h["id"]]
        if h["id"] != "ficha":
            m[f"PESO_{clave}"] = str(D.puntos_de(h["id"]))
    m["PESO_EXPOSICION"] = str(D.puntos_de("exposicion"))
    return m


def resuelve(texto: str, m: dict[str, str], usados: set, fuente: str) -> str:
    def rep(mo):
        clave = mo.group(1)
        if clave not in m:
            sys.exit(f"PARADO: {fuente} usa el marcador desconocido @@{clave}@@")
        usados.add(clave)
        return m[clave]
    return re.sub(r"@@([A-Z0-9_]+)@@", rep, texto)


def cabecera_modulo(n: int, titulo: str, objetivo: str) -> str:
    return f"""  <!-- ============================================================ -->
  <!-- MÓDULO {n} · {titulo[:52]:<52} -->
  <!-- ============================================================ -->
  <template id="module-{n}">
    <div class="animate-fade-in">
      <div class="border-b border-gray-100 pb-6 mb-6">
        <div class="flex items-center space-x-2 text-sm text-secondary font-semibold mb-2 uppercase tracking-wide">
          <span>Módulo {n}</span>
        </div>
        <h2 class="text-3xl font-bold text-gray-900 mb-4" style="border:none; padding:0;">{titulo}</h2>
        <div class="bg-gray-50 rounded-lg p-4 border border-gray-200 flex items-start gap-3">
          <span class="text-xl">🎯</span>
          <div>
            <h3 class="font-bold text-gray-800 text-sm" style="margin:0;">Objetivo</h3>
            <p class="text-gray-600 text-sm" style="margin:0;">{objetivo}</p>
          </div>
        </div>
      </div>
"""


CIERRE_MODULO = "    </div>\n  </template>\n"

VACIO_SIMULADORES = """    // Sin simuladores: la guía no enseña contenido. El registro se deja vacío a
    // propósito, para que cuenta_sitio.py no cuente los de demostración de la
    // plantilla como si fueran de este documento.

"""


def selectores(t: str) -> set:
    return set(re.findall(r"^\s*(\.[a-zA-Z][\w-]*)", t[:t.index("</style>")], re.M))


# ---------------------------------------------------------------------------
# 4. El ensamblado
# ---------------------------------------------------------------------------
def ensambla() -> tuple[str, list[str], set]:
    doc = lee(PLANTILLA)
    sel_plantilla = selectores(doc)
    demos = sorted(set(re.findall(r"[A-Z_]+\['(demo[^']*)'\]", doc))
                   | set(re.findall(r'data-[a-z-]+="(demo[^"]*)"', doc)))
    print(f"plantilla: {len(doc) / 1024:.0f} KB · componentes de demostración: {len(demos)}\n")

    doc = sustituye(doc, "<title>Plantilla de capítulo — Estadística Espacial</title>",
                    f"<title>{TITULO} — Estadística Espacial</title>", "título")
    doc = sustituye(
        doc,
        'content="Plantilla base para los capítulos del material de estudio interactivo de Estadística '
        'Espacial (Universidad El Bosque): cajas, código R/Python en pestañas, simuladores con Chart.js, '
        'mapas interactivos, autoevaluación y ejercicios guiados."',
        'content="Guía del proyecto integrador del Corte III de Estadística Espacial (Universidad El '
        'Bosque): un territorio real con datos abiertos, el protocolo de inferencia preregistrado, Moran '
        'y LISA con su corrección, la rúbrica y una plantilla de informe en R."',
        "meta description")
    doc = sustituye(
        doc,
        'content="estadística espacial, autocorrelación espacial, índice de Moran, LISA, patrones puntuales, '
        'kriging, variograma, econometría espacial, SAR, GWR, MAUP, sf, spdep, gstat, spatstat, material de '
        'estudio, simulador, autoevaluación, R, Python, UnBosque"',
        'content="estadística espacial, proyecto integrador, preregistro, matriz de pesos, índice de Moran, '
        'LISA, multiplicidad, potencia, MAUP, datos abiertos, rúbrica, sf, spdep, tmap, R, UnBosque"',
        "meta keywords")
    doc = sustituye(doc, "PLANTILLA BASE •\n              5 MÓDULOS DE DEMOSTRACIÓN • UNBOSQUE 2026-II",
                    "PROYECTO INTEGRADOR • CORTE III •\n"
                    f"              {D.PROYECTO_DEL_CORTE}&nbsp;% DEL CORTE • UNBOSQUE 2026-II",
                    "subtítulo de la cabecera")
    doc = sustituye(doc, "Estadística Espacial (20929) • Plantilla de\n          capítulo • UnBosque 2026-II",
                    "Estadística Espacial (20929) • Proyecto integrador •\n"
                    "          Corte III • UnBosque 2026-II", "pie")

    mods = ",\n".join(f'        {{ id: {n}, title: "{t}", duration: "{d}" }}' for n, t, d, *_ in MODULOS)
    doc = reemplaza_region(doc, "    const courseData = {", "\n    };\n",
                           "    const courseData = {\n      modules: [\n" + mods + "\n      ]\n    };\n\n"
                           "    // La guía no incrusta datos: sus cifras se imprimen en el marcado desde\n"
                           "    // proyecto/datos.py (precalculo/ensambla_proyecto.py).\n",
                           "courseData", max_lineas=20)

    doc = sustituye(
        doc,
        "    // PLANTILLA BASE. Punto de partida para un capítulo de un curso\n"
        "    // NUEVO. Para un capítulo más de un curso ya empezado, copia su\n"
        "    // último capítulo, que lleva los datos y el contexto ya montados.\n"
        "    //\n"
        "    // Al añadir un componente nuevo a un capítulo, añádelo también aquí\n"
        "    // en la misma sesión: esta plantilla ya se quedó atrás una vez.\n",
        "    // GUÍA DEL PROYECTO INTEGRADOR DEL CORTE III. Ensamblada por\n"
        "    // precalculo/ensambla_proyecto.py desde plantilla/plantilla-capitulo.html.\n"
        "    // NO SE EDITA A MANO: la prosa vive en proyecto/modulos/ y las cifras\n"
        "    // en proyecto/datos.py.\n",
        "comentario de cabecera del script")

    m = marcadores()
    usados: set = set()
    piezas = []
    for n, titulo, _dur, fuente, objetivo in MODULOS:
        cuerpo = resuelve(lee(FUENTES / "modulos" / fuente), m, usados, fuente)
        piezas.append(cabecera_modulo(n, titulo, objetivo) + cuerpo.rstrip() + "\n" + CIERRE_MODULO)
    sobran = sorted(set(m) - usados)
    if sobran:
        sys.exit(f"PARADO: marcadores que ninguna prosa usa: {sobran}")
    doc = reemplaza_region(
        doc,
        "  <!-- ============================================================ -->\n"
        "  <!-- MÓDULO 1 · Cajas y tipografía",
        "\n  <script>", "\n".join(piezas) + "\n  <script>",
        f"los {len(MODULOS)} módulos", max_lineas=600)

    doc = reemplaza_region(doc, "    MAPAS_ESTACIONALES['demo-mapa'] = function () {",
                           "\n    };\n", "", "el mapa estacional de demostración", max_lineas=40)
    doc = reemplaza_region(doc, "    GLOSARIOS['demo-notacion'] = {", "\n    };\n",
                           "", "el glosario de demostración", max_lineas=40)
    doc = reemplaza_region(doc, "    RUBRICAS['demo-rubrica'] = {", "\n    };\n",
                           rubrica_js(), "la rúbrica del proyecto", max_lineas=40)
    vieja = [l for l in doc.splitlines() if l.startswith("    GEOMAPAS['demo-mapa'] =")]
    if len(vieja) != 1:
        sys.exit(f"PARADO: {len(vieja)} registros de GEOMAPAS['demo-mapa'], se esperaba 1")
    doc = sustituye(doc, vieja[0], "", "el mapa de demostración")
    doc = reemplaza_region(
        doc,
        "    // --- Deslizadores sobre un gráfico de línea ----------------------\n"
        "    SIMULADORES['demo-deslizadores'] = function (raiz) {",
        "    // ================================================================\n"
        "    // Autoevaluación de demostración: una pregunta de cada tipo\n",
        VACIO_SIMULADORES
        + "    // ================================================================\n"
          "    // Autoevaluación de demostración: una pregunta de cada tipo\n",
        "los simuladores de demostración", max_lineas=140, min_lineas=100)
    doc = reemplaza_region(doc, "    TABLAS_RANKING['demo'] = function () {", "\n    };\n",
                           "", "la tabla de ranking de demostración", max_lineas=40)
    doc = reemplaza_region(doc, "    AUTOEVALUACIONES['demo'] = [", "\n    ];\n",
                           "", "la autoevaluación de demostración", max_lineas=90)
    doc = reemplaza_region(doc, "    SIMULACROS['demo'] = {", "\n    };\n",
                           "", "el simulacro de demostración", max_lineas=40)

    doc = aplica_boton(doc, DESTINO, RAIZ, "franja")
    return doc, demos, sel_plantilla


# ---------------------------------------------------------------------------
# 5. Las comprobaciones, sobre el artefacto
# ---------------------------------------------------------------------------
def comprueba(doc: str, demos: list[str], sel_plantilla: set) -> list[str]:
    print("\ncomprobaciones sobre el resultado:")
    fallos: list[str] = []
    marcado = "".join(re.findall(r'<template id="module-.*?</template>', doc, re.S))

    def exige(cond: bool, que: str) -> None:
        print(f"  {'OK ' if cond else 'MAL'}  {que}")
        if not cond:
            fallos.append(que)

    exige(doc.count('<template id="module-') == len(MODULOS), f"las {len(MODULOS)} plantillas de módulo")
    exige(all(f'<template id="module-{n}">' in doc for n, *_ in MODULOS),
          f"los módulos van del 1 al {len(MODULOS)} sin huecos")
    exige("@@" not in doc, "ningún marcador @@ sin resolver")
    tablas = marcado.count("<table>")
    exige(tablas == marcado.count("<caption"), f"las {tablas} tablas llevan su caption")
    ids = re.findall(r' id="([^"]+)"', marcado)
    repes = sorted({i for i in ids if ids.count(i) > 1})
    exige(not repes, f"identificadores únicos{'' if not repes else ': ' + ', '.join(repes)}")
    vacias = [c for c in ("note", "warning", "definition", "tip-box", "diagram", "formula")
              if re.search(rf'<div class="{c}">\s*</div>', marcado)]
    exige(not vacias, f"ninguna caja vacía{'' if not vacias else ': ' + ', '.join(vacias)}")
    exige("undefined" not in marcado, "ningún «undefined» impreso en el marcado")
    restos = sorted(d for d in demos if f"'{d}'" in doc or f'"{d}"' in doc)
    exige(not restos, f"ningún componente de demostración{'' if not restos else ': ' + ', '.join(restos)}")
    exige("PLANTILLA BASE" not in doc and "Cajas y tipografía" not in doc, "ningún rótulo de la plantilla")
    exige(selectores(doc) == sel_plantilla, f"el CSS es el de la plantilla ({len(sel_plantilla)} selectores)")
    exige(marcado.count('data-rubrica="') == 1 and "RUBRICAS['proyecto-integrador'] = " in doc,
          "la rúbrica: un contenedor y su registro")
    exige("<U+" not in doc, "sin codificación rota (<U+…>)")
    locales = [h for h in re.findall(r'href="([^"#:]+)"', marcado)]
    rotos = sorted({h for h in locales if h != RMD_DESTINO.name and not (SITIO / h).exists()})
    exige(not rotos, f"los {len(locales)} enlaces locales resuelven" + ("" if not rotos else ": " + ", ".join(rotos)))
    exige(not re.search(r'href="(?!https?:)[^"#]+\.html#', marcado),
          "ningún enlace local con ancla profunda (la plantilla de Espacial no lee el #)")
    exige(f'href="{D.SERIES_ENLACE_CONJUNTA}"' in marcado, "el enlace al módulo de la conjunta de Series")
    exige(RMD_FUENTE.exists(), "la plantilla .Rmd existe en la fuente")
    kb = len(doc.encode("utf-8")) / 1024
    exige(kb < PRESUPUESTO_KB, f"pesa {kb:.0f} KB (presupuesto {PRESUPUESTO_KB} KB)")
    return fallos


def main() -> int:
    revisar = "--revisar" in sys.argv
    print(f"\n=== ensambla_proyecto.py{' --revisar' if revisar else ''} ===")
    doc, demos, sel = ensambla()
    fallos = comprueba(doc, demos, sel)
    if fallos:
        print(f"\nPARADO: {len(fallos)} comprobaciones fallidas. No se escribió nada.")
        return 1
    if revisar:
        actual = DESTINO.read_text(encoding="utf-8") if DESTINO.exists() else None
        rmd = RMD_DESTINO.read_bytes() if RMD_DESTINO.exists() else None
        print(f"\n--revisar: no se escribe nada.\n"
              f"  {'NUEVO ' if actual is None else ('igual ' if actual == doc else 'CAMBIA')} "
              f"{DESTINO.relative_to(RAIZ)}\n"
              f"  {'NUEVO ' if rmd is None else ('igual ' if rmd == RMD_FUENTE.read_bytes() else 'CAMBIA')} "
              f"{RMD_DESTINO.relative_to(RAIZ)}")
        return 0
    DESTINO.write_text(doc, encoding="utf-8")
    shutil.copyfile(RMD_FUENTE, RMD_DESTINO)
    print(f"\nEscrito {DESTINO.relative_to(RAIZ)}  ({DESTINO.stat().st_size / 1024:.0f} KB)")
    print(f"Copiado {RMD_DESTINO.relative_to(RAIZ)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
