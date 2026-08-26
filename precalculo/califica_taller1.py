#!/usr/bin/env python3
"""
califica_taller1.py — la mitad de atrás del Taller 1

Estadística Espacial 2026-II (20929) · corte I.
Ver PLAN_Taller_1_Caps_1_2.md (el taller) y el plan del calificador.

PARA QUÉ EXISTE

El taller se publicó sin solucionario y con una rúbrica de cinco
dimensiones sobre siete tareas: 35 celdas y una suma ponderada por
estudiante, más ~22 cifras que hay que contrastar contra una variante
distinta cada vez, más una defensa que puede RECALIFICAR lo ya entregado.
Nada de eso se hace de cabeza doce veces seguidas sin equivocarse una.

LO QUE ESTA HERRAMIENTA **NO** HACE, y es la parte importante

  · NO pone notas. Las 35 celdas y las cuatro de la defensa las escribe
    Javier. Esto compara cifras, hace la aritmética y presenta la
    evidencia.
  · La comprobación de cifras **no alimenta ninguna nota**. La rúbrica
    publicada dice que «un informe con todas las cifras correctas puede
    quedarse a mitad de tabla»; convertir el ✓/✗ en puntos contradiría lo
    que el estudiante leyó. Entra al reporte como evidencia y nada más.
  · NO recalcula cifras. Las lee del JSON que produce
    `verifica_taller1.R --json`, porque en este proyecto las cifras nacen
    en R y en ningún otro sitio. Si algún día las dos mitades discrepan,
    la discrepancia es de esta herramienta y no de dos implementaciones
    que se separaron por su cuenta.
  · NO duplica el material publicado. Los pesos de las siete tareas, la
    rúbrica entera y el banco de la defensa se DERIVAN de
    `ensambla_taller1.py`, que es lo que el estudiante tiene delante. Si
    alguno cambiara, esto para en el arranque en vez de calificar contra
    una rúbrica que ya no existe.

EL GUION SE VERSIONA; LO QUE ESCRIBE, NO. Aquí dentro no hay ni una cifra
esperada, ni una semilla, ni un nombre: todo eso se lee en tiempo de
ejecución de `calificacion/`, que la lista blanca `/*` de la raíz ya
ignora. Lo que sale por el otro lado —las hojas y los dos reportes— sí
lleva nombres, notas y, vía el JSON de R, la familia del patrón, que es la
respuesta de T1. Por eso `exige_ignorado()` comprueba con
`git check-ignore` que el destino esté fuera del repositorio ANTES de
escribir, y para si no lo está.

La versión anterior de este párrafo decía «no se versiona» sin decir el
qué, y se leía como si hablara del guion. Dejaba sin decidir algo que sí
había que decidir, y la decisión —tomada el 2026-08-26— es que la
herramienta se versiona: es la única forma de que el arnés que la vigila
signifique algo para quien venga después.

CÓMO SE USA, desde la carpeta `Estadistica espacial/`:

  # 1. las cifras esperadas, que las produce R
  precalculo/rscript.sh precalculo/verifica_taller1.R --lista calificacion/curso.txt \
      --json calificacion/esperado/

  # 2. la hoja de cada estudiante, prellenada
  python precalculo/califica_taller1.py --nuevo --lista calificacion/curso.txt

  # 3. ... se editan las hojas a mano ...

  # 4. los reportes
  python precalculo/califica_taller1.py
"""
from __future__ import annotations

import argparse
import json
import os
import pathlib
import math
import re
import subprocess
import sys
import unicodedata

AQUI = pathlib.Path(__file__).resolve().parent
RAIZ = AQUI.parent
sys.path.insert(0, str(AQUI))

import ensambla_taller1 as E  # noqa: E402  (el material publicado, como fuente)

# La raíz se puede redirigir con `CALIFICA_RAIZ`, mismo convenio que el
# `_ruta()` de los ensambladores: es lo que permite que el arnés de
# inyección monte un curso entero de mentira y lo rompa a gusto sin
# acercarse a las notas de verdad. Sin esta variable, la única forma de
# probar el calificador sería sobre las hojas reales.
CALIFICACION = pathlib.Path(os.environ.get("CALIFICA_RAIZ") or (RAIZ / "calificacion"))
ESPERADO = CALIFICACION / "esperado"
HOJAS = CALIFICACION / "hojas"
REPORTES = CALIFICACION / "reportes"

PESO_ESCRITO = 0.60
PESO_DEFENSA = 0.40
N_PREGUNTAS_DEFENSA = 3


class Parado(SystemExit):
    """Lo que para el guion. Calificar con una cuenta que no cuadra es peor
    que no calificar: el error se lo lleva el estudiante."""

    def __init__(self, mensaje: str) -> None:
        super().__init__(f"\nPARADO: {mensaje}\n")


def ancla(condicion: bool, mensaje: str) -> None:
    if not condicion:
        raise Parado(mensaje)


# =====================================================================
# 1. Lo que se DERIVA del material publicado
#
# Ni los pesos ni la rúbrica ni el banco se escriben aquí. Se leen de
# `ensambla_taller1.py`, que es el archivo que construye lo que el
# estudiante lee. Duplicarlos habría creado exactamente el problema que
# este curso enseña a detectar: dos copias de la misma cifra que se
# separan sin que nadie se entere.
# =====================================================================
def _pesos_de_las_tareas() -> dict[str, int]:
    """Los siete pesos, del marcado que construye el ensamblador."""
    crudos = [int(x) for x in re.findall(r'class="badge-peso">(\d+)&nbsp;%', E.MODULOS)]
    ancla(len(crudos) == 7,
          f"se encontraron {len(crudos)} pesos de tarea en el ensamblador y se esperaban 7. "
          "El taller cambió de forma y esta herramienta calificaría contra otro reparto")
    ancla(sum(crudos) == 100,
          f"los pesos de las siete tareas suman {sum(crudos)} y no 100")
    return {f"T{i + 1}": p for i, p in enumerate(crudos)}


def _rubrica_publicada() -> list[dict]:
    """Las cinco dimensiones con sus cuatro niveles, de RUBRICA_JS."""
    cabeceras = re.findall(r"clave: '([A-E])', nombre: '([^']+)', puntos: (\d+)", E.RUBRICA_JS)
    ancla(len(cabeceras) == 5,
          f"se encontraron {len(cabeceras)} dimensiones en la rúbrica publicada y se esperaban 5")
    ancla(sum(int(c[2]) for c in cabeceras) == 100,
          "las cinco dimensiones de la rúbrica no suman 100 puntos")

    niveles = re.findall(r"\{ nombre: '([^']+)', rango: '(\d+)[\u2013-](\d+)'", E.RUBRICA_JS)
    ancla(len(niveles) == 20,
          f"se encontraron {len(niveles)} niveles y se esperaban 20 (cinco dimensiones por cuatro)")

    dims = []
    for i, (clave, nombre, puntos) in enumerate(cabeceras):
        misninveles = [{"nombre": n, "lo": int(lo), "hi": int(hi)}
                       for n, lo, hi in niveles[i * 4:(i + 1) * 4]]
        tope = max(n["hi"] for n in misninveles)
        ancla(tope == int(puntos),
              f"la dimensión {clave} vale {puntos} puntos pero su nivel más alto llega a {tope}")
        dims.append({"clave": clave, "nombre": nombre, "puntos": int(puntos),
                     "niveles": misninveles})
    return dims


TAREAS = _pesos_de_las_tareas()
RUBRICA = _rubrica_publicada()
BANCO = list(E.BANCO_DEFENSA)
ancla(len(BANCO) >= N_PREGUNTAS_DEFENSA,
      f"el banco de la defensa trae {len(BANCO)} preguntas y se sacan {N_PREGUNTAS_DEFENSA}")


def nivel_de(dim: dict, valor: float) -> str:
    """En qué nivel de la rúbrica cae una puntuación."""
    for n in dim["niveles"]:
        if n["lo"] <= valor <= n["hi"]:
            return n["nombre"]
    return "fuera de rango"


def _prellenado_aceptable() -> dict[str, int]:
    """El punto medio del nivel «Aceptable» de cada dimensión.

    Prellenar no es poner la nota: es que la hoja se pueda calificar
    tecleando SOLO lo que se desvía. Con 35 celdas por estudiante y doce
    estudiantes, una hoja en blanco se rellena mal o no se rellena.
    """
    salida = {}
    for dim in RUBRICA:
        acep = [n for n in dim["niveles"] if n["nombre"].lower().startswith("acept")]
        ancla(len(acep) == 1,
              f"la dimensión {dim['clave']} no tiene un nivel «Aceptable» y el prellenado depende de él")
        salida[dim["clave"]] = (acep[0]["lo"] + acep[0]["hi"]) // 2
    return salida


ACEPTABLE = _prellenado_aceptable()


# =====================================================================
# 2. Las cifras de la hoja del estudiante
#
# El orden y las etiquetas son los de `entrega/plantilla_taller1.tex`,
# porque la hoja de calificación se lee EN PARALELO con la página 2 del
# informe. Las claves son las que escribe `verifica_taller1.R --json`.
# =====================================================================
CIFRAS = [
    # (clave del JSON, etiqueta, tarea)
    ("T1.n",             "n (número de puntos)",                    "T1"),
    ("T1.area",          "área de la ventana",                      "T1"),
    ("T1.lambda",        "intensidad lambda",                       "T1"),
    ("T1.d_min",         "d_min observada",                         "T1"),
    ("T1.d_azar",        "d_min que daría el azar",                 "T1"),
    ("T1.R",             "R de Clark-Evans",                        "T1"),
    ("T1.R_donnelly",    "R corregido por borde (Donnelly)",        "T1"),

    ("T2.digito",        "dígito de verificación (suma altitudes)", "T2"),
    ("T2.media",         "media de temperatura (°C)",               "T2"),
    ("T2.sd",            "desviación estándar",                     "T2"),
    ("T2.ee",            "error estándar clásico",                  "T2"),
    ("T2.ic_bajo",       "IC clásico · extremo inferior",           "T2"),
    ("T2.ic_alto",       "IC clásico · extremo superior",           "T2"),
    ("T2.rho",           "rho (I de Moran, k = 1)",                 "T2"),
    ("T2.n_eff",         "n efectivo",                              "T2"),
    ("T2.ee_corregido",  "error estándar corregido",                "T2"),
    ("T2.icc_bajo",      "IC corregido · extremo inferior",         "T2"),
    ("T2.icc_alto",      "IC corregido · extremo superior",         "T2"),

    ("T4.area_4326",     "4326 · área (km²)",                       "T4"),
    ("T4.ancho_4326",    "4326 · ancho de la caja (m)",             "T4"),
    ("T4.buffer_4326",   "4326 · cuánto mide un buffer de 500 m",   "T4"),
    ("T4.area_3857",     "3857 · área (km²)",                       "T4"),
    ("T4.ancho_3857",    "3857 · ancho de la caja (m)",             "T4"),
    ("T4.buffer_3857",   "3857 · cuánto mide un buffer de 500 m",   "T4"),
    ("T4.area_3116",     "3116 · área (km²)",                       "T4"),
    ("T4.ancho_3116",    "3116 · ancho de la caja (m)",             "T4"),
    ("T4.buffer_3116",   "3116 · cuánto mide un buffer de 500 m",   "T4"),
    ("T4.area_9377",     "9377 · área (km²)",                       "T4"),
    ("T4.ancho_9377",    "9377 · ancho de la caja (m)",             "T4"),
    ("T4.buffer_9377",   "9377 · cuánto mide un buffer de 500 m",   "T4"),

    ("T5.d_real_km",     "distancia real entre sus 2 primeras (km)", "T5"),
    ("T5.d_declarada_m", "la misma, mal declarada («metros»)",      "T5"),
    ("T5.factor",        "factor entre las dos",                    "T5"),
    ("T5.sin_dep_mal",   "sin departamento · join mal declarado",   "T5"),
    ("T5.sin_dep_ok",    "sin departamento · join correcto",        "T5"),
]

# Cifras que el JSON trae y la plantilla NO pide: se citan en la prosa de
# T5(a) pero no van en la hoja de cifras, así que no se califican. Viajan
# al reporte como contexto.
CIFRAS_APOYO = ["T2.n", "T5.caja_m2", "T5.en_buffer"]

ancla(len(CIFRAS) == 35,
      f"la hoja declara {len(CIFRAS)} cifras y la plantilla de entrega pide 35")


# =====================================================================
# 3. Guardas de disco
# =====================================================================
def exige_ignorado(ruta: pathlib.Path) -> None:
    """Nada de lo que escribe esta herramienta puede acabar en el repositorio.

    Lleva nombres, notas y la familia del patrón. La comprobación se hace
    con git y no con una lista de carpetas escrita a mano, porque la lista
    escrita a mano es la que se queda vieja.
    """
    r = subprocess.run(["git", "check-ignore", "-q", str(ruta)],
                       cwd=RAIZ, capture_output=True)
    if r.returncode == 1:
        raise Parado(
            f"«{ruta}» NO está ignorada por git, y aquí van nombres, notas y la respuesta "
            f"de T1. Escribe dentro de `calificacion/`, que la lista blanca `/*` de la raíz "
            f"ya ignora.")


def corta(ruta: pathlib.Path) -> str:
    """La ruta relativa a la raíz cuando se puede, y la entera cuando no.

    Con `CALIFICA_RAIZ` apuntando fuera del repositorio —que es como corre
    el arnés— `relative_to` levanta ValueError. Lo encontró
    `prueba_califica_taller1.py` a la primera pasada, y es exactamente
    para eso que existe.
    """
    try:
        return str(ruta.relative_to(RAIZ))
    except ValueError:
        return str(ruta)


def sanea(texto: str) -> str:
    """Un nombre propio convertido en trozo de nombre de archivo."""
    plano = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", plano.lower())).strip("-") or "sin-nombre"


# =====================================================================
# 4. `--nuevo`: la hoja prellenada
# =====================================================================
def carga_esperado(variante: int) -> dict:
    ruta = ESPERADO / f"{variante:03d}.json"
    if not ruta.exists():
        raise Parado(
            f"no existe {ruta}. Las cifras las produce R, no esta herramienta:\n\n"
            f"  precalculo/rscript.sh precalculo/verifica_taller1.R <documento> "
            f"--json calificacion/esperado/\n")
    d = json.loads(ruta.read_text(encoding="utf-8"))
    faltan = [c for c, _, _ in CIFRAS if c not in d["cifras"]]
    ancla(not faltan,
          f"a {ruta.name} le faltan {len(faltan)} cifras que la hoja necesita: "
          f"{', '.join(faltan[:5])}. ¿Se generó con una versión vieja de verifica_taller1.R?")
    return d


def variante_de(documento: str) -> int:
    """Los tres últimos dígitos, la misma regla que R y que el navegador."""
    doc = documento.strip()
    if not re.fullmatch(r"[0-9][0-9.\-]*[0-9]", doc):
        raise Parado(f"«{documento}» no parece un número de documento")
    digitos = re.sub(r"\D", "", doc)
    if not 3 <= len(digitos) <= 15:
        raise Parado(f"«{documento}» tiene {len(digitos)} dígitos: de ahí no sale una variante fiable")
    return int(digitos[-3:])


def formatea(valor) -> str:
    if isinstance(valor, bool):
        return str(valor)
    if isinstance(valor, int) or (isinstance(valor, float) and valor == int(valor) and abs(valor) >= 1000):
        return f"{int(valor)}"
    if isinstance(valor, float):
        return f"{valor:.5f}".rstrip("0").rstrip(".") if abs(valor) < 1e6 else f"{valor:.5f}"
    return str(valor)


def escribe_hoja(documento: str, nombre: str) -> pathlib.Path:
    v = variante_de(documento)
    esp = carga_esperado(v)
    ruta = HOJAS / f"T1_{v:03d}_{sanea(nombre or documento)}.txt"
    exige_ignorado(ruta)
    if ruta.exists():
        return None

    mun, pat = esp["municipio"], esp["patron"]
    L = []
    A = L.append
    A("# " + "=" * 68)
    A(f"#  Taller 1 · {nombre or '(sin nombre)'}")
    A(f"#  documento {documento} · variante {v:03d}")
    A(f"#  {mun['nombre']} ({mun['departamento']}) · patrón {pat['indice']:02d} · "
      f"dígito de verificación {esp['cifras']['T2.digito']}")
    A("#")
    A("#  Generado por califica_taller1.py --nuevo. Edita SOLO lo que se desvíe")
    A("#  y vuelve a correr `python precalculo/califica_taller1.py`.")
    A("#  Las líneas que empiezan por # son comentarios y se ignoran.")
    A("# " + "=" * 68)
    A("")
    A(f"estudiante: {nombre}")
    A(f"documento:  {documento}")
    A(f"variante:   {v:03d}")
    A("")
    A("entrega: a tiempo          # a tiempo | tarde | no entregada")
    A("paginas: -                 # el límite son 13 sin contar el anexo")
    A("")
    A("# --- CIFRAS " + "-" * 57)
    A("# La columna del medio es la CORRECTA y no se toca. En la derecha:")
    A("#   ok    la que entregó coincide")
    A("#   -     no la puso")
    A("#   <su cifra>   si escribió otra")
    A("# Coincide si cabe en la precisión que él escribió: 1.16 vale por 1.15764.")
    tarea_actual = None
    for clave, etiqueta, tarea in CIFRAS:
        if tarea != tarea_actual:
            A(f"#   · {tarea}")
            tarea_actual = tarea
        A(f"cifra  {clave:<18} {formatea(esp['cifras'][clave]):<22} ok")
    A("")
    A("# --- RÚBRICA " + "-" * 56)
    A("# Las cinco dimensiones sobre CADA tarea, como dice el módulo 9.")
    for dim in RUBRICA:
        rangos = " · ".join(f"{n['nombre']} {n['lo']}-{n['hi']}" for n in dim["niveles"])
        A(f"#   {dim['clave']} {dim['nombre']} (0-{dim['puntos']}): {rangos}")
    A("# Prellenado en el punto medio de «Aceptable». Cambia lo que se desvíe.")
    A("#             " + "".join(f"{d['clave']}/{d['puntos']:<4}" for d in RUBRICA))
    for t in sorted(TAREAS, key=lambda k: int(k[1:])):
        celdas = "".join(f"{ACEPTABLE[d['clave']]:<6}" for d in RUBRICA)
        A(f"rubrica {t}    {celdas}# {TAREAS[t]} % del escrito")
    A("")
    A("# --- COMENTARIOS · van al reporte del estudiante " + "-" * 21)
    for t in sorted(TAREAS, key=lambda k: int(k[1:])):
        A(f"nota {t}:")
    A("")
    A("# --- DEFENSA " + "-" * 56)
    A(f"# Tres preguntas del banco (número 1-{len(BANCO)}) y su nota 0-100, más")
    A("# «decisiones»: si sostuvo lo que entregó por escrito. Las cuatro pesan igual.")
    for _ in range(N_PREGUNTAS_DEFENSA):
        A("defensa pregunta  -     0")
    A("defensa decisiones      0")
    A("defensa comentario:")
    A("")
    A("# --- RECALIFICACIONES " + "-" * 47)
    A("# Una línea por decisión que no supo sostener. La tarea se recalifica")
    A("# ENTERA, sobre 100, y el reporte enseña el antes, el después y el motivo.")
    A("# recalifica T4  40  no supo decir dónde está el origen de 3116")
    A("")
    A("# --- EL BANCO, para elegir las tres " + "-" * 34)
    for i, (tema, preg) in enumerate(BANCO, 1):
        A(f"#  {i:2d}. [{tema}] {preg}")
    A("")

    ruta.parent.mkdir(parents=True, exist_ok=True)
    ruta.write_text("\n".join(L), encoding="utf-8")
    return ruta


def lee_curso(archivo: pathlib.Path) -> list[tuple[str, str]]:
    """Un documento por línea, con un nombre opcional detrás de una coma."""
    filas = []
    for linea in archivo.read_text(encoding="utf-8").splitlines():
        linea = linea.strip()
        if not linea or linea.startswith("#"):
            continue
        partes = re.split(r"[,;\t]", linea, maxsplit=1)
        filas.append((partes[0].strip(), partes[1].strip() if len(partes) > 1 else ""))
    return filas


def avisa_colisiones(filas: list[tuple[str, str]]) -> None:
    """Dos documentos con los mismos tres dígitos reciben la MISMA variante."""
    porvar: dict[int, list[str]] = {}
    for doc, nom in filas:
        porvar.setdefault(variante_de(doc), []).append(f"{doc}{f' ({nom})' if nom else ''}")
    choques = {v: q for v, q in porvar.items() if len(q) > 1}
    if not choques:
        print(f"  {len(filas)} documento(s), {len(porvar)} variante(s): sin colisiones.")
        return
    raise Parado(
        "hay colisiones de variante y eso se resuelve ANTES de calificar, no después:\n"
        + "\n".join(f"    variante {v:03d} la comparten: {' · '.join(q)}" for v, q in choques.items()))


def manda_nuevo(args) -> int:
    if args.lista:
        filas = lee_curso(pathlib.Path(args.lista))
    else:
        filas = []
        for a in args.documentos:
            p = a.split(":", 1)
            filas.append((p[0].strip(), p[1].strip() if len(p) > 1 else ""))
    if not filas:
        raise Parado("--nuevo necesita documentos, o un --lista con ellos")

    avisa_colisiones(filas)
    escritas, saltadas = [], []
    for doc, nom in filas:
        r = escribe_hoja(doc, nom)
        (escritas if r is not None else saltadas).append(r or f"{variante_de(doc):03d}")
    print()
    for r in escritas:
        print(f"  hoja -> {corta(r)}")
    if saltadas:
        print(f"\n  {len(saltadas)} hoja(s) ya existían y NO se tocaron "
              f"(variantes {', '.join(saltadas)}): regenerar una hoja calificada borraría el "
              f"trabajo. Bórrala a mano si de verdad quieres empezar de cero.")
    if not escritas:
        print("\n  Nada nuevo que escribir.\n")
        return 0
    print(f"\n  {len(escritas)} hoja(s) nueva(s). Edítalas y vuelve a correr sin --nuevo.\n")
    return 0


# =====================================================================
# 5. Leer una hoja ya calificada
#
# Formato de línea, sin dependencias: `palabra_clave campos…`. `tomllib`
# solo existe en el Python de geo_env (3.11) y el del PATH es 3.10; una
# herramienta que falla según con qué intérprete se la invoque es peor
# que una sin dependencias.
#
# Los comentarios en línea se recortan SOLO en las líneas de cifra, de
# rúbrica y de defensa. En `nota T1:`, en el comentario de la defensa y en
# el motivo de una recalificación el texto llega hasta el final: ahí una
# almohadilla es una almohadilla, y recortarla se comería media frase sin
# avisar.
# =====================================================================
CLAVES_LIBRES = ("estudiante:", "documento:", "variante:", "entrega:", "paginas:")


def _num(txt: str, donde: str) -> float:
    try:
        return float(txt.replace(",", "."))
    except ValueError:
        raise Parado(f"{donde}: «{txt}» no es un número")


def lee_hoja(ruta: pathlib.Path) -> dict:
    h = {"ruta": ruta, "cabecera": {}, "cifras": [], "rubrica": {}, "notas": {},
         "defensa": {"preguntas": [], "decisiones": None, "comentario": ""},
         "recalificaciones": []}
    for i, cruda in enumerate(ruta.read_text(encoding="utf-8").splitlines(), 1):
        linea = cruda.strip()
        donde = f"{ruta.name}:{i}"
        if not linea or linea.startswith("#"):
            continue

        bajo = linea.lower()
        if any(bajo.startswith(k) for k in CLAVES_LIBRES):
            clave, _, valor = linea.partition(":")
            h["cabecera"][clave.strip().lower()] = valor.split("#")[0].strip()
            continue

        if bajo.startswith("cifra "):
            campos = linea.split("#")[0].split()
            ancla(len(campos) == 4,
                  f"{donde}: una línea de cifra son cuatro campos "
                  f"(cifra, clave, esperado, entregado) y hay {len(campos)}")
            h["cifras"].append({"clave": campos[1], "esperado_txt": campos[2],
                                "entregado": campos[3], "linea": i})
            continue

        if bajo.startswith("rubrica "):
            campos = linea.split("#")[0].split()
            ancla(len(campos) == 7,
                  f"{donde}: una línea de rúbrica son la tarea y las cinco dimensiones "
                  f"(siete campos) y hay {len(campos)}")
            tarea = campos[1].upper()
            ancla(tarea in TAREAS, f"{donde}: «{tarea}» no es una de las siete tareas")
            ancla(tarea not in h["rubrica"], f"{donde}: {tarea} aparece dos veces en la rúbrica")
            h["rubrica"][tarea] = [_num(c, donde) for c in campos[2:]]
            continue

        if bajo.startswith("nota "):
            cabeza, _, texto = linea.partition(":")
            partes = cabeza.split()
            ancla(len(partes) == 2, f"{donde}: se esperaba «nota T1: …»")
            tarea = partes[1].upper()
            ancla(tarea in TAREAS, f"{donde}: «{tarea}» no es una de las siete tareas")
            h["notas"][tarea] = texto.strip()
            continue

        if bajo.startswith("defensa "):
            resto = linea[len("defensa "):].strip()
            if resto.lower().startswith("comentario"):
                h["defensa"]["comentario"] = resto.partition(":")[2].strip()
            elif resto.lower().startswith("decisiones"):
                campos = resto.split("#")[0].split()
                ancla(len(campos) == 2, f"{donde}: se esperaba «defensa decisiones <0-100>»")
                h["defensa"]["decisiones"] = _num(campos[1], donde)
            elif resto.lower().startswith("pregunta"):
                campos = resto.split("#")[0].split()
                ancla(len(campos) == 3,
                      f"{donde}: una pregunta de la defensa son su número (o «-») y su nota")
                h["defensa"]["preguntas"].append(
                    {"n": None if campos[1] == "-" else int(campos[1]),
                     "nota": _num(campos[2], donde), "linea": i})
            else:
                raise Parado(f"{donde}: «defensa {resto.split()[0]}» no se entiende")
            continue

        if bajo.startswith("recalifica "):
            campos = linea.split(None, 3)
            ancla(len(campos) >= 3,
                  f"{donde}: una recalificación son la tarea, la nota nueva sobre 100 y el motivo")
            tarea = campos[1].upper()
            ancla(tarea in TAREAS, f"{donde}: «{tarea}» no es una de las siete tareas")
            h["recalificaciones"].append(
                {"tarea": tarea, "nueva": _num(campos[2], donde),
                 "motivo": campos[3].strip() if len(campos) > 3 else "", "linea": i})
            continue

        raise Parado(f"{donde}: «{linea.split()[0]}» no es ninguna de las palabras que esta "
                     f"hoja entiende (cifra, rubrica, nota, defensa, recalifica)")
    return h


# =====================================================================
# 6. Comparar una cifra con la que tenía que dar
#
# La tolerancia es la precisión que escribió EL ESTUDIANTE, acotada por
# tres cifras significativas. Así 1.16 vale por 1.15764 —redondear bien no
# es un error— y 1.2 no vale, aunque su propia precisión declarada lo
# permitiría.
# =====================================================================
def compara_cifra(esperado: float, entregado: str) -> dict:
    if entregado.lower() in ("ok", "si", "sí"):
        return {"estado": "coincide", "valor": esperado}
    if entregado in ("-", "--", "?"):
        return {"estado": "no la puso", "valor": None}
    try:
        v = float(entregado.replace(",", "."))
    except ValueError:
        return {"estado": "ilegible", "valor": None, "crudo": entregado}

    dec = len(entregado.partition(".")[2]) if "." in entregado else 0
    tol_suya = 0.5 * 10 ** (-dec)
    if esperado == 0:
        tol_3sig = 0.5e-3
    else:
        tol_3sig = 0.5 * 10 ** -(2 - math.floor(math.log10(abs(esperado))))
    tol = min(tol_suya, tol_3sig)

    dif = abs(v - esperado)
    if dif <= 0.5e-5:
        return {"estado": "coincide", "valor": v}
    if dif <= tol:
        return {"estado": "redondeada", "valor": v, "dif": dif}
    return {"estado": "no coincide", "valor": v, "dif": dif}


# =====================================================================
# 7. La aritmética
#
#   score_t = A+B+C+D+E                    (0..100 por tarea)
#   escrito = Σ (peso_t / 100) · score_t   (0..100)
#   defensa = media de las tres preguntas y de «decisiones»
#   final   = 0.60 · escrito + 0.40 · defensa
#
# Una recalificación SUSTITUYE el score de su tarea. El reporte enseña el
# antes y el después: la regla publicada tiene dientes solo si deja rastro.
# =====================================================================
ENTREGAS = ("a tiempo", "tarde", "no entregada")


def califica(h: dict, esp: dict) -> dict:
    ruta = h["ruta"]
    cab = h["cabecera"]

    doc = cab.get("documento", "")
    ancla(bool(doc), f"{ruta.name}: la hoja no dice de qué documento es")
    v_doc = variante_de(doc)
    ancla(cab.get("variante", "").lstrip("0") in (str(v_doc), "") and
          int(cab.get("variante", "-1") or -1) == v_doc,
          f"{ruta.name}: la hoja dice variante {cab.get('variante')} y el documento {doc} "
          f"resuelve la {v_doc:03d}")
    ancla(esp["variante"] == v_doc,
          f"{ruta.name}: las cifras esperadas son de la variante {esp['variante']:03d} "
          f"y la hoja es de la {v_doc:03d}")

    entrega = cab.get("entrega", "").lower()
    ancla(entrega in ENTREGAS,
          f"{ruta.name}: «entrega: {entrega}» no es ninguna de {', '.join(ENTREGAS)}")

    # --- cifras --------------------------------------------------------
    claves = {c for c, _, _ in CIFRAS}
    vistas = [c["clave"] for c in h["cifras"]]
    faltan = [c for c, _, _ in CIFRAS if c not in vistas]
    sobran = [c for c in vistas if c not in claves]
    ancla(not faltan, f"{ruta.name}: faltan {len(faltan)} cifras de la hoja: {', '.join(faltan[:6])}")
    ancla(not sobran, f"{ruta.name}: hay cifras que no son de esta hoja: {', '.join(sobran[:6])}")
    ancla(len(vistas) == len(set(vistas)), f"{ruta.name}: alguna cifra aparece dos veces")

    cifras = []
    for c in h["cifras"]:
        real = esp["cifras"][c["clave"]]
        # La columna del medio se compara con el JSON de R. Si alguien la
        # editó —o la hoja es de una versión anterior del precálculo—, se
        # estaría calificando contra una cifra inventada.
        ancla(abs(float(c["esperado_txt"]) - real) <= max(5e-5, abs(real) * 1e-7),
              f"{ruta.name}:{c['linea']}: la columna de la cifra correcta dice "
              f"{c['esperado_txt']} y R dice {real}. Esa columna no se edita")
        etiqueta, tarea = next((e, t) for k, e, t in CIFRAS if k == c["clave"])
        cifras.append({"clave": c["clave"], "etiqueta": etiqueta, "tarea": tarea,
                       "esperado": real, **compara_cifra(real, c["entregado"])})

    # --- rúbrica -------------------------------------------------------
    faltan_t = [t for t in TAREAS if t not in h["rubrica"]]
    ancla(not faltan_t, f"{ruta.name}: la rúbrica no tiene fila para {', '.join(sorted(faltan_t))}")
    for tarea, valores in h["rubrica"].items():
        for dim, valor in zip(RUBRICA, valores):
            ancla(0 <= valor <= dim["puntos"],
                  f"{ruta.name}: {tarea} tiene {valor:g} en la dimensión {dim['clave']} "
                  f"({dim['nombre']}), que va de 0 a {dim['puntos']}")

    scores = {t: sum(h["rubrica"][t]) for t in TAREAS}
    scores_previos = dict(scores)

    # --- recalificaciones ----------------------------------------------
    recals = []
    for r in h["recalificaciones"]:
        ancla(0 <= r["nueva"] <= 100,
              f"{ruta.name}:{r['linea']}: una recalificación va de 0 a 100 y dice {r['nueva']:g}")
        ancla(bool(r["motivo"]),
              f"{ruta.name}:{r['linea']}: una recalificación sin motivo escrito no se puede "
              f"sostener ante un reclamo")
        recals.append({**r, "antes": scores[r["tarea"]]})
        scores[r["tarea"]] = r["nueva"]

    escrito_previo = sum(TAREAS[t] / 100 * scores_previos[t] for t in TAREAS)
    escrito = sum(TAREAS[t] / 100 * scores[t] for t in TAREAS)
    if entrega != "a tiempo":
        escrito_previo = escrito = 0.0

    # --- defensa -------------------------------------------------------
    d = h["defensa"]
    ancla(len(d["preguntas"]) == N_PREGUNTAS_DEFENSA,
          f"{ruta.name}: la defensa son {N_PREGUNTAS_DEFENSA} preguntas y hay "
          f"{len(d['preguntas'])}")
    ancla(d["decisiones"] is not None,
          f"{ruta.name}: falta la línea «defensa decisiones», que es el 25 % de la defensa "
          f"y la que ata lo escrito con lo oral")
    for q in d["preguntas"]:
        ancla(0 <= q["nota"] <= 100,
              f"{ruta.name}:{q['linea']}: una pregunta de la defensa va de 0 a 100")
        ancla(q["n"] is None or 1 <= q["n"] <= len(BANCO),
              f"{ruta.name}:{q['linea']}: la pregunta {q['n']} no está en el banco "
              f"(va de 1 a {len(BANCO)})")
    ancla(0 <= d["decisiones"] <= 100, f"{ruta.name}: «decisiones» va de 0 a 100")
    nums = [q["n"] for q in d["preguntas"] if q["n"] is not None]
    ancla(len(nums) == len(set(nums)),
          f"{ruta.name}: la misma pregunta del banco aparece dos veces en la defensa")

    partes = [q["nota"] for q in d["preguntas"]] + [d["decisiones"]]
    defensa = sum(partes) / len(partes)
    final = PESO_ESCRITO * escrito + PESO_DEFENSA * defensa

    return {
        "hoja": h, "esperado": esp, "entrega": entrega,
        "nombre": cab.get("estudiante", "") or doc, "documento": doc, "variante": v_doc,
        "cifras": cifras, "scores": scores, "scores_previos": scores_previos,
        "recalificaciones": recals,
        "escrito": escrito, "escrito_previo": escrito_previo,
        "defensa": defensa, "final": final, "nota5": round(final / 20, 1),
    }


def resumen_cifras(c: dict) -> dict:
    cuenta: dict[str, int] = {}
    for x in c["cifras"]:
        cuenta[x["estado"]] = cuenta.get(x["estado"], 0) + 1
    return cuenta


def imprime_cuentas(c: dict) -> None:
    esp = c["esperado"]
    print("=" * 72)
    print(f"  {c['nombre']} · documento {c['documento']} · variante {c['variante']:03d}")
    print(f"  {esp['municipio']['nombre']} ({esp['municipio']['departamento']}) · "
          f"patrón {esp['patron']['indice']:02d} ({esp['patron']['familia']})")
    print("=" * 72)

    print("\n  CIFRAS  " + " · ".join(f"{v} {k}" for k, v in sorted(resumen_cifras(c).items())))
    for x in c["cifras"]:
        if x["estado"] == "coincide":
            continue
        suya = "—" if x["valor"] is None else f"{x['valor']:g}"
        print(f"     {x['estado']:<12} {x['etiqueta']:<42} suya {suya:<13} "
              f"correcta {x['esperado']:g}")
    print("     (esto NO puntúa: es evidencia para las dimensiones B y C, no una nota)")

    print("\n  RÚBRICA")
    print("     tarea  peso   " + "   ".join(f"{d['clave']}/{d['puntos']}" for d in RUBRICA)
          + "    score")
    for t in sorted(TAREAS, key=lambda k: int(k[1:])):
        celdas = "  ".join(f"{v:>4.0f}" for v in c["hoja"]["rubrica"][t])
        marca = (f"   -> recalificada a {c['scores'][t]:.0f}"
                 if c["scores"][t] != c["scores_previos"][t] else "")
        print(f"     {t}    {TAREAS[t]:>3} %  {celdas}   {c['scores_previos'][t]:>5.0f}{marca}")

    if c["recalificaciones"]:
        print("\n  RECALIFICACIONES")
        for x in c["recalificaciones"]:
            print(f"     {x['tarea']}: {x['antes']:.0f} -> {x['nueva']:.0f} · {x['motivo']}")

    print("\n  DEFENSA")
    for q in c["hoja"]["defensa"]["preguntas"]:
        tema = BANCO[q["n"] - 1][0] if q["n"] else "(sin registrar)"
        print(f"     pregunta {str(q['n'] or '-'):>2}   {tema:<30} {q['nota']:>5.0f}")
    print(f"     decisiones sostenidas{'':<26} {c['hoja']['defensa']['decisiones']:>5.0f}")

    print("\n  " + "-" * 68)
    if c["entrega"] != "a tiempo":
        print(f"  ENTREGA «{c['entrega']}»: el escrito NO se califica "
              f"(módulo 1: no se aceptan entregas tarde)")
    if c["escrito"] != c["escrito_previo"]:
        print(f"  escrito antes de la defensa   {c['escrito_previo']:6.2f}")
    print(f"  escrito  {c['escrito']:6.2f}  x {PESO_ESCRITO:.2f}  = {PESO_ESCRITO * c['escrito']:6.2f}")
    print(f"  defensa  {c['defensa']:6.2f}  x {PESO_DEFENSA:.2f}  = {PESO_DEFENSA * c['defensa']:6.2f}")
    print(f"  FINAL    {c['final']:6.2f} / 100      =  {c['nota5']:.1f} / 5.0")
    print()


def carga_y_califica(ruta: pathlib.Path) -> dict:
    h = lee_hoja(ruta)
    doc = h["cabecera"].get("documento", "")
    ancla(bool(doc), f"{ruta.name}: la hoja no dice de qué documento es")
    return califica(h, carga_esperado(variante_de(doc)))


def hojas_en_disco(cual: str | None) -> list[pathlib.Path]:
    if cual:
        p = pathlib.Path(cual)
        if not p.exists():
            p = HOJAS / cual
        ancla(p.exists(), f"no existe la hoja «{cual}»")
        return [p]
    ancla(HOJAS.exists(), f"no existe {corta(HOJAS)}: empieza por --nuevo")
    hs = sorted(HOJAS.glob("T1_*.txt"))
    ancla(bool(hs), f"no hay ninguna hoja en {corta(HOJAS)}: empieza por --nuevo")
    return hs


# =====================================================================
# 8. Los reportes HTML
#
# Autocontenidos y sin una sola petición a la red: se abren desde el
# disco, se imprimen a PDF y se suben a Brightspace sin depender de nada.
# Usan el verde institucional del `.tex` de entrega —RGB(0,102,51)— y no
# la librería de capítulo: esos 270 KB están hechos para geomapas,
# simuladores y autoevaluaciones, y un reporte de notas no tiene ninguna
# de las tres.
# =====================================================================
VERDE = "#006633"
COLOR_NIVEL = {
    "Excelente":    ("#0b7a3b", "#e6f4ec"),
    "Aceptable":    ("#1d5fa8", "#e8f0fa"),
    "Insuficiente": ("#9a6b06", "#fdf3e0"),
    "No logrado":   ("#a32020", "#fbeaea"),
}
COLOR_CIFRA = {
    "coincide":    ("#0b7a3b", "#e6f4ec"),
    "redondeada":  ("#1d5fa8", "#e8f0fa"),
    "no coincide": ("#a32020", "#fbeaea"),
    "no la puso":  ("#6b7280", "#f1f3f5"),
    "ilegible":    ("#9a6b06", "#fdf3e0"),
}


def esc(x) -> str:
    return (str(x).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            .replace('"', "&quot;"))


CSS = """
:root { --verde: %s; --tinta: #1E293B; --tenue: #64748B; --linea: #E2E8F0; }
* { box-sizing: border-box; }
body { margin: 0; background: #F8FAFC; color: var(--tinta); line-height: 1.55;
  font-family: 'Montserrat', 'Helvetica Neue', Helvetica, Arial, sans-serif;
  font-size: 15px; }
.hoja { max-width: 1000px; margin: 0 auto; background: #fff; padding: 0 0 3rem; }
header { background: var(--verde); color: #fff; padding: 1.8rem 2.2rem; }
header h1 { margin: 0 0 .2rem; font-size: 1.55rem; font-weight: 700; }
header .sub { opacity: .88; font-size: .95rem; }
header .curso { opacity: .7; font-size: .8rem; letter-spacing: .09em;
  text-transform: uppercase; margin-bottom: .5rem; }
main { padding: 0 2.2rem; }
h2 { font-size: 1.05rem; text-transform: uppercase; letter-spacing: .06em;
  color: var(--verde); border-bottom: 2px solid var(--linea); padding-bottom: .4rem;
  margin: 2.4rem 0 1rem; }
table { border-collapse: collapse; width: 100%%; font-size: .88rem; }
th, td { padding: .45rem .6rem; border-bottom: 1px solid var(--linea); text-align: left;
  vertical-align: top; }
th { font-weight: 600; font-size: .78rem; text-transform: uppercase;
  letter-spacing: .04em; color: var(--tenue); }
td.n, th.n { text-align: right; font-variant-numeric: tabular-nums; }
.marco { display: flex; gap: 1rem; flex-wrap: wrap; margin: 1.6rem 0 0; }
.caja { flex: 1 1 170px; border: 1px solid var(--linea); border-radius: 10px;
  padding: .8rem 1rem; background: #fff; }
.caja .et { font-size: .72rem; text-transform: uppercase; letter-spacing: .05em;
  color: var(--tenue); }
.caja .v { font-size: 1.7rem; font-weight: 700; font-variant-numeric: tabular-nums;
  line-height: 1.2; }
.caja.final { background: var(--verde); border-color: var(--verde); color: #fff; }
.caja.final .et { color: rgba(255,255,255,.8); }
.pildora { display: inline-block; padding: .1rem .5rem; border-radius: 999px;
  font-size: .74rem; font-weight: 600; white-space: nowrap; }
.aviso { border-left: 4px solid #a32020; background: #fbeaea; padding: .8rem 1rem;
  border-radius: 0 8px 8px 0; margin: 1rem 0; font-size: .9rem; }
.nota { border-left: 4px solid var(--verde); background: #f2f8f4; padding: .7rem 1rem;
  border-radius: 0 8px 8px 0; margin: .5rem 0 1.2rem; font-size: .9rem; }
.tenue { color: var(--tenue); font-size: .85rem; }
.mono { font-family: 'Fira Code', ui-monospace, SFMono-Regular, Menlo, monospace;
  font-size: .84rem; }
.celda { text-align: center; font-variant-numeric: tabular-nums; font-weight: 600; }
footer { margin: 3rem 2.2rem 0; padding-top: 1rem; border-top: 1px solid var(--linea);
  color: var(--tenue); font-size: .8rem; }
@media print {
  body { background: #fff; font-size: 11.5px; }
  .hoja { max-width: none; }
  h2 { page-break-after: avoid; }
  table, .marco { page-break-inside: avoid; }
}
""" % VERDE


def _envuelve(titulo: str, cuerpo: str, extra_css: str = "") -> str:
    return f"""<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(titulo)}</title>
<style>{CSS}{extra_css}</style>
</head>
<body>
<div class="hoja">
{cuerpo}
</div>
</body>
</html>
"""


def _pildora(texto: str, colores) -> str:
    fg, bg = colores
    return f'<span class="pildora" style="color:{fg};background:{bg}">{esc(texto)}</span>'


def reporte_estudiante(c: dict) -> str:
    esp = c["esperado"]
    h = c["hoja"]
    B = []
    A = B.append

    A('<header>')
    A('  <div class="curso">Estadística Espacial (20929) · Taller 1 · Capítulos 1 y 2</div>')
    A(f'  <h1>{esc(c["nombre"])}</h1>')
    A(f'  <div class="sub">documento {esc(c["documento"])} · variante {c["variante"]:03d} · '
      f'{esc(esp["municipio"]["nombre"])} ({esc(esp["municipio"]["departamento"])}) · '
      f'patrón {esp["patron"]["indice"]:02d}</div>')
    A('</header>')
    A('<main>')

    # --- las cuatro cajas ------------------------------------------------
    A('<div class="marco">')
    A(f'  <div class="caja"><div class="et">Escrito · 60 %</div>'
      f'<div class="v">{c["escrito"]:.2f}</div></div>')
    A(f'  <div class="caja"><div class="et">Defensa · 40 %</div>'
      f'<div class="v">{c["defensa"]:.2f}</div></div>')
    A(f'  <div class="caja final"><div class="et">Final</div>'
      f'<div class="v">{c["nota5"]:.1f}</div>'
      f'<div class="et">{c["final"]:.2f} / 100</div></div>')
    A('</div>')

    if c["entrega"] != "a tiempo":
        A(f'<div class="aviso"><strong>Entrega «{esc(c["entrega"])}».</strong> El módulo 1 dice '
          f'que lo que no esté en Brightspace a la hora no se califica, así que el escrito '
          f'cuenta 0. La defensa sí se calificó y aporta su 40 %.</div>')

    if c["recalificaciones"]:
        A('<div class="aviso">')
        A(f'  <strong>La defensa recalificó {len(c["recalificaciones"])} tarea(s).</strong> '
          f'El escrito pasó de <strong>{c["escrito_previo"]:.2f}</strong> a '
          f'<strong>{c["escrito"]:.2f}</strong>. Es la regla del módulo 9: una decisión '
          f'entregada por escrito que no se sostiene en la defensa se recalifica.')
        A('  <ul style="margin:.5rem 0 0">')
        for r in c["recalificaciones"]:
            A(f'    <li><strong>{r["tarea"]}</strong>: {r["antes"]:.0f} &rarr; '
              f'{r["nueva"]:.0f} sobre 100 · {esc(r["motivo"])}</li>')
        A('  </ul></div>')

    # --- la rúbrica ------------------------------------------------------
    A('<h2>La rúbrica, dimensión por dimensión y tarea por tarea</h2>')
    A('<div class="nota">Las cinco dimensiones se puntúan sobre <strong>cada</strong> tarea y la '
      'nota del escrito es la suma ponderada por el peso de la tarea. Una tarea que pesa el 20 % '
      'mueve el doble que una que pesa el 10 %, con las mismas celdas.</div>')
    A('<table><thead><tr><th>Tarea</th><th class="n">Peso</th>')
    for d in RUBRICA:
        A(f'<th class="n" title="{esc(d["nombre"])}">{d["clave"]} · {d["puntos"]}</th>')
    A('<th class="n">Score</th><th class="n">Aporta</th></tr></thead><tbody>')
    for t in sorted(TAREAS, key=lambda k: int(k[1:])):
        A(f'<tr><td><strong>{t}</strong></td><td class="n">{TAREAS[t]} %</td>')
        for d, v in zip(RUBRICA, h["rubrica"][t]):
            fg, bg = COLOR_NIVEL.get(nivel_de(d, v), ("#000", "#fff"))
            A(f'<td class="celda" style="color:{fg};background:{bg}" '
              f'title="{esc(nivel_de(d, v))}">{v:g}</td>')
        if c["scores"][t] != c["scores_previos"][t]:
            sc = (f'<s style="opacity:.55">{c["scores_previos"][t]:.0f}</s> &rarr; '
                  f'<strong>{c["scores"][t]:.0f}</strong>')
        else:
            sc = f'<strong>{c["scores"][t]:.0f}</strong>'
        A(f'<td class="n">{sc}</td>'
          f'<td class="n">{TAREAS[t] / 100 * c["scores"][t]:.2f}</td></tr>')
    A(f'<tr><td colspan="{2 + len(RUBRICA) + 1}" style="text-align:right"><strong>Escrito'
      f'</strong></td><td class="n"><strong>{c["escrito"]:.2f}</strong></td></tr>')
    A('</tbody></table>')
    A('<p class="tenue">' + ' · '.join(
        f'<strong>{d["clave"]}</strong> {esc(d["nombre"])}' for d in RUBRICA) + '</p>')

    # --- comentarios -----------------------------------------------------
    conletra = [(t, h["notas"].get(t, "")) for t in sorted(TAREAS, key=lambda k: int(k[1:]))
                if h["notas"].get(t, "").strip()]
    if conletra:
        A('<h2>Tarea por tarea</h2>')
        A('<table><tbody>')
        for t, texto in conletra:
            A(f'<tr><td style="width:4rem"><strong>{t}</strong><br>'
              f'<span class="tenue">{TAREAS[t]} %</span></td><td>{esc(texto)}</td></tr>')
        A('</tbody></table>')

    # --- cifras ----------------------------------------------------------
    r = resumen_cifras(c)
    A('<h2>Las cifras de tu hoja</h2>')
    A('<div class="nota">Tu variante tiene sus propias cifras y estas son las que tenían que dar. '
      '<strong>Esta comprobación no puntúa por sí sola</strong>: la rúbrica dice que un informe '
      'con todas las cifras correctas puede quedarse a mitad de tabla. Entra como evidencia de '
      'las dimensiones B (interpretación) y C (procedimiento).</div>')
    A('<p>' + ' '.join(_pildora(f'{v} {k}', COLOR_CIFRA.get(k, ("#000", "#eee")))
                       for k, v in sorted(r.items())) + '</p>')
    A('<table><thead><tr><th>Tarea</th><th>Cifra</th><th class="n">La tuya</th>'
      '<th class="n">La correcta</th><th>Estado</th></tr></thead><tbody>')
    for x in c["cifras"]:
        suya = "—" if x["valor"] is None else f'{x["valor"]:g}'
        if x["estado"] == "ilegible":
            suya = esc(x.get("crudo", "?"))
        A(f'<tr><td class="tenue">{x["tarea"]}</td><td>{esc(x["etiqueta"])}</td>'
          f'<td class="n mono">{suya}</td><td class="n mono">{x["esperado"]:g}</td>'
          f'<td>{_pildora(x["estado"], COLOR_CIFRA.get(x["estado"], ("#000", "#eee")))}</td></tr>')
    A('</tbody></table>')

    # --- defensa ---------------------------------------------------------
    A('<h2>La defensa</h2>')
    A('<table><thead><tr><th>#</th><th>Pregunta</th><th class="n">Nota</th></tr>'
      '</thead><tbody>')
    for q in h["defensa"]["preguntas"]:
        if q["n"]:
            tema, texto = BANCO[q["n"] - 1]
            celda = f'<strong>{esc(tema)}</strong><br><span class="tenue">{esc(texto)}</span>'
            num = str(q["n"])
        else:
            celda, num = '<span class="tenue">(no se registró cuál salió)</span>', "—"
        A(f'<tr><td class="n">{num}</td><td>{celda}</td>'
          f'<td class="n"><strong>{q["nota"]:.0f}</strong></td></tr>')
    A(f'<tr><td class="n">—</td><td><strong>Sostener las decisiones entregadas por escrito'
      f'</strong><br><span class="tenue">Es la regla que ata las dos mitades: una decisión que '
      f'no se sostiene recalifica su tarea.</span></td>'
      f'<td class="n"><strong>{h["defensa"]["decisiones"]:.0f}</strong></td></tr>')
    A(f'<tr><td colspan="2" style="text-align:right"><strong>Defensa</strong> '
      f'<span class="tenue">(las cuatro pesan igual)</span></td>'
      f'<td class="n"><strong>{c["defensa"]:.2f}</strong></td></tr>')
    A('</tbody></table>')
    if h["defensa"]["comentario"]:
        A(f'<div class="nota">{esc(h["defensa"]["comentario"])}</div>')

    A('</main>')
    A('<footer>')
    A(f'Escrito {c["escrito"]:.2f} &times; 0.60 + defensa {c["defensa"]:.2f} &times; 0.40 = '
      f'<strong>{c["final"]:.2f}</strong> sobre 100, equivalente a '
      f'<strong>{c["nota5"]:.1f}</strong> sobre 5.0.')
    A('<br>Las cifras correctas las produce <span class="mono">verifica_taller1.R</span> sobre los '
      'mismos tres GeoPackages que descargaste; la rúbrica es la que está publicada en el módulo 9 '
      'del taller.')
    A('</footer>')
    return _envuelve(f'Taller 1 · {c["nombre"]}', "\n".join(B))


CSS_CURSO = """
tr.fila:hover { background: #f1f5f9; }
th.orden { cursor: pointer; user-select: none; }
th.orden:hover { color: var(--verde); }
.barra { height: 7px; background: var(--linea); border-radius: 4px; overflow: hidden; }
.barra > i { display: block; height: 100%; background: var(--verde); }
"""


def reporte_curso(cs: list[dict], esperados: int | None) -> str:
    B = []
    A = B.append
    A('<header>')
    A('  <div class="curso">Estadística Espacial (20929) · Corte I</div>')
    A('  <h1>Taller 1 · el curso</h1>')
    n = len(cs)
    falta = "" if esperados is None else (
        f' · faltan <strong>{esperados - n}</strong> de {esperados}' if esperados > n
        else f' · las {esperados} del curso')
    A(f'  <div class="sub">{n} hoja(s) calificada(s){falta}</div>')
    A('</header><main>')

    if esperados is not None and esperados > n:
        A(f'<div class="aviso"><strong>Este reporte no está completo.</strong> Se leyeron {n} '
          f'hojas de {esperados}. Las medias de abajo son de lo que hay, no del curso.</div>')

    finales = [c["final"] for c in cs]
    A('<div class="marco">')
    for et, v in (("Media final", sum(finales) / n), ("Mínimo", min(finales)),
                  ("Máximo", max(finales)),
                  ("Aprueban (≥ 3.0)", sum(1 for c in cs if c["nota5"] >= 3.0))):
        A(f'  <div class="caja"><div class="et">{et}</div><div class="v">'
          f'{v:.2f}</div></div>' if "Aprueban" not in et else
          f'  <div class="caja"><div class="et">{et}</div><div class="v">{int(v)}/{n}</div></div>')
    A('</div>')

    # --- la tabla --------------------------------------------------------
    A('<h2>Uno por uno</h2>')
    A('<table id="tabla"><thead><tr>'
      '<th class="orden" onclick="ordena(0,0)">Estudiante</th>'
      '<th class="orden n" onclick="ordena(1,1)">Var.</th>'
      '<th>Municipio</th>'
      '<th class="orden n" onclick="ordena(3,1)">Escrito</th>'
      '<th class="orden n" onclick="ordena(4,1)">Defensa</th>'
      '<th class="orden n" onclick="ordena(5,1)">Final</th>'
      '<th class="orden n" onclick="ordena(6,1)">/ 5.0</th>'
      '<th class="n">Recal.</th><th class="n">Cifras mal</th>'
      '</tr></thead><tbody>')
    for c in sorted(cs, key=lambda x: x["nombre"].lower()):
        r = resumen_cifras(c)
        mal = r.get("no coincide", 0) + r.get("no la puso", 0) + r.get("ilegible", 0)
        A(f'<tr class="fila"><td>{esc(c["nombre"])}</td><td class="n">{c["variante"]:03d}</td>'
          f'<td class="tenue">{esc(c["esperado"]["municipio"]["nombre"])}</td>'
          f'<td class="n">{c["escrito"]:.2f}</td><td class="n">{c["defensa"]:.2f}</td>'
          f'<td class="n"><strong>{c["final"]:.2f}</strong></td>'
          f'<td class="n">{c["nota5"]:.1f}</td>'
          f'<td class="n">{len(c["recalificaciones"]) or ""}</td>'
          f'<td class="n">{mal or ""}</td></tr>')
    A('</tbody></table>')

    # --- medias por dimensión y por tarea --------------------------------
    A('<h2>Dónde se gana y dónde se pierde</h2>')
    A('<table><thead><tr><th>Tarea</th><th class="n">Peso</th>')
    for d in RUBRICA:
        A(f'<th class="n" title="{esc(d["nombre"])}">{d["clave"]}</th>')
    A('<th class="n">Score medio</th></tr></thead><tbody>')
    for t in sorted(TAREAS, key=lambda k: int(k[1:])):
        A(f'<tr><td><strong>{t}</strong></td><td class="n">{TAREAS[t]} %</td>')
        for j, d in enumerate(RUBRICA):
            m = sum(c["hoja"]["rubrica"][t][j] for c in cs) / n
            A(f'<td class="n">{m:.1f}<br><span class="tenue">{100 * m / d["puntos"]:.0f} %</span></td>')
        sm = sum(c["scores"][t] for c in cs) / n
        A(f'<td class="n"><strong>{sm:.1f}</strong></td></tr>')
    A('<tr><td colspan="2" style="text-align:right"><strong>Media por dimensión</strong></td>')
    for j, d in enumerate(RUBRICA):
        m = sum(c["hoja"]["rubrica"][t][j] for c in cs for t in TAREAS) / (n * len(TAREAS))
        A(f'<td class="n"><strong>{100 * m / d["puntos"]:.0f} %</strong></td>')
    A('<td></td></tr></tbody></table>')
    A('<p class="tenue">' + ' · '.join(
        f'<strong>{d["clave"]}</strong> {esc(d["nombre"])}' for d in RUBRICA) + '</p>')
    if any(c["recalificaciones"] for c in cs):
        A('<p class="tenue">Las cinco columnas son las celdas de la rúbrica, que una '
          'recalificación <strong>no</strong> toca; el score medio sí la incorpora. Por eso en una '
          'tarea recalificada las dos cifras no cuadran entre sí, y las dos son correctas.</p>')

    # --- qué cifras falló más gente --------------------------------------
    fallos: dict[str, dict] = {}
    for c in cs:
        for x in c["cifras"]:
            if x["estado"] in ("coincide", "redondeada"):
                continue
            f = fallos.setdefault(x["clave"], {"etiqueta": x["etiqueta"], "tarea": x["tarea"],
                                               "n": 0})
            f["n"] += 1
    A('<h2>Qué cifra falló más gente</h2>')
    if not fallos:
        A('<p class="tenue">Ninguna: las 35 cifras cuadran en todas las hojas leídas.</p>')
    else:
        A('<div class="nota">Esto no es una nota de nadie: es lo que dice qué volver a enseñar. '
          'Una cifra que falla media clase es un enunciado ambiguo o un paso que no se explicó.</div>')
        A('<table><thead><tr><th>Tarea</th><th>Cifra</th><th class="n">Falla en</th>'
          '<th style="width:30%">&nbsp;</th></tr></thead><tbody>')
        for clave, f in sorted(fallos.items(), key=lambda kv: -kv[1]["n"]):
            A(f'<tr><td class="tenue">{f["tarea"]}</td><td>{esc(f["etiqueta"])}</td>'
              f'<td class="n">{f["n"]} de {n}</td>'
              f'<td><div class="barra"><i style="width:{100 * f["n"] / n:.0f}%"></i></div></td></tr>')
        A('</tbody></table>')

    # --- recalificaciones -------------------------------------------------
    recs = [(c, r) for c in cs for r in c["recalificaciones"]]
    A('<h2>Recalificaciones de la defensa</h2>')
    if not recs:
        A('<p class="tenue">Ninguna: todo el mundo sostuvo lo que entregó.</p>')
    else:
        A('<table><thead><tr><th>Estudiante</th><th>Tarea</th><th class="n">Antes</th>'
          '<th class="n">Después</th><th>Motivo</th></tr></thead><tbody>')
        for c, r in recs:
            A(f'<tr><td>{esc(c["nombre"])}</td><td><strong>{r["tarea"]}</strong></td>'
              f'<td class="n">{r["antes"]:.0f}</td><td class="n">{r["nueva"]:.0f}</td>'
              f'<td>{esc(r["motivo"])}</td></tr>')
        A('</tbody></table>')

    A('</main><footer>')
    A('Generado por <span class="mono">califica_taller1.py</span>. Las cifras esperadas vienen de '
      '<span class="mono">verifica_taller1.R --json</span>; los pesos, la rúbrica y el banco de la '
      'defensa se leen del propio taller publicado, no se copian aquí.')
    A('</footer>')
    A("""<script>
function ordena(col, num) {
  const t = document.getElementById('tabla').tBodies[0];
  const fs = [...t.rows];
  const dir = t.dataset.col == col && t.dataset.dir == '1' ? -1 : 1;
  fs.sort((a, b) => {
    const x = a.cells[col].innerText.trim(), y = b.cells[col].innerText.trim();
    return dir * (num ? (parseFloat(x) || 0) - (parseFloat(y) || 0) : x.localeCompare(y, 'es'));
  });
  fs.forEach(f => t.appendChild(f));
  t.dataset.col = col; t.dataset.dir = dir == 1 ? '1' : '0';
}
</script>""")
    return _envuelve("Taller 1 · el curso", "\n".join(B), CSS_CURSO)


def escribe_reportes(cs: list[dict], esperados: int | None) -> list[pathlib.Path]:
    exige_ignorado(REPORTES)
    REPORTES.mkdir(parents=True, exist_ok=True)
    salidas = []
    for c in cs:
        r = REPORTES / f"T1_{c['variante']:03d}_{sanea(c['nombre'])}.html"
        r.write_text(reporte_estudiante(c), encoding="utf-8")
        salidas.append(r)
    r = REPORTES / "curso.html"
    r.write_text(reporte_curso(cs, esperados), encoding="utf-8")
    salidas.append(r)
    return salidas



def main() -> int:
    ap = argparse.ArgumentParser(
        prog="califica_taller1.py",
        description="Califica el Taller 1: hojas prellenadas y reportes HTML.")
    ap.add_argument("--nuevo", action="store_true",
                    help="escribe la hoja prellenada de cada estudiante")
    ap.add_argument("--lista", metavar="ARCHIVO",
                    help="un documento por línea, nombre opcional tras una coma")
    ap.add_argument("--cuentas", nargs="?", const="", metavar="HOJA",
                    help="imprime la aritmética de una hoja (o de todas) sin generar HTML")
    ap.add_argument("documentos", nargs="*", metavar="DOC[:Nombre]")
    args = ap.parse_args()

    print(f"\n=== califica_taller1.py ===")
    print(f"  rúbrica: {len(RUBRICA)} dimensiones ({'+'.join(str(d['puntos']) for d in RUBRICA)}"
          f" = {sum(d['puntos'] for d in RUBRICA)}) · tareas: "
          f"{'+'.join(str(p) for p in TAREAS.values())} = {sum(TAREAS.values())}")
    print(f"  banco de la defensa: {len(BANCO)} preguntas · prellenado «Aceptable»: "
          f"{'/'.join(str(ACEPTABLE[d['clave']]) for d in RUBRICA)} = {sum(ACEPTABLE.values())}\n")

    if args.nuevo:
        return manda_nuevo(args)

    if args.cuentas is not None:
        for ruta in hojas_en_disco(args.cuentas or None):
            imprime_cuentas(carga_y_califica(ruta))
        return 0

    cs = [carga_y_califica(r) for r in hojas_en_disco(None)]
    esperados = len(lee_curso(pathlib.Path(args.lista))) if args.lista else None
    for r in escribe_reportes(cs, esperados):
        print(f"  {corta(r)}")
    media = sum(c['final'] for c in cs) / len(cs)
    print(f"\n  {len(cs)} estudiante(s) · media {media:.2f} / 100\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
