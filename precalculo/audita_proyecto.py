#!/usr/bin/env python3
"""audita_proyecto.py — Audita la guía del proyecto integrador sobre el ARTEFACTO.

No mira la intención del ensamblador: lee
`Htmls_Espacial/proyecto-integrador-corte-iii.html` y vuelve a calcular por su
cuenta cada cosa que afirma. Ocho frentes (PLAN_Proyecto_Integrador.md, T5):

  A · Calendario   cada fecha impresa tiene el día de la semana que le toca en
                   2026 y cae en la semana del curso que se le atribuye (ancla:
                   la semana 10 empieza el lunes 5 de octubre); los hitos son
                   los del proyecto de Series (F1), van en orden, ninguno cae en
                   festivo, y no hay fechas sueltas.
  B · Pesos        la rúbrica suma 100 en la tabla y en el componente, y cada
                   hito lo que dice la tabla de pesos; los puntos de cada nivel
                   son puntos × nivel / 5; proyecto + quices = 100 % del corte;
                   la tabla del tope y la del retraso se recalculan.
  C · Decisiones   DE1–DE12 y PE1–PE4 dicen lo que se decidió: parejas, datos
                   que no valen, N mínimo, examen final y Talleres 4 y 5 solo
                   para decir que no los hay, el canal, el guion de minutos.
  D · Estructura   CSS de la plantilla, ids únicos, tablas con caption, enlaces
                   locales que resuelven y sin ancla, courseData igual a los h2,
                   botón al índice, sin mojibake ni «<» sin escapar en el código.
  E · Código R     cada bloque de R de la guía corre en un R limpio; la plantilla
                   publicada es la de la fuente y se renderiza con los datos de
                   ejemplo y con un `datos/unidades.gpkg` propio.
  F · Contenido    cada «módulo N del capítulo C» citado existe y se llama como
                   dice la guía; la tabla de potencia es la del JSON y la prosa
                   que la lee dice lo que la tabla.
  G · Exigencias   cada exigencia de los caps. 2, 3, 6 y 7 tiene su criterio y
                   su descriptor la nombra; la regla de las réplicas es la del
                   cap. 7 (nsim + 1 > 40·N) y nada la contradice.
  H · Conjunta     el enlace al módulo 8 de la guía de Series es exacto, la guía
                   dice que las reglas viven allí y NO copia ninguna; los
                   criterios que cambian de variable llevan su descriptor.

    python3 precalculo/audita_proyecto.py

Variables de entorno (las usa el arnés `prueba_auditor_proyecto.py`):
  PROYECTO_HTML    ruta del HTML a auditar (por defecto, el publicado)
  PROYECTO_SIN_R   si vale 1, se salta el frente E (tarda medio minuto)
  PROYECTO_RMD     la plantilla .Rmd que renderiza el frente E (por defecto, la fuente)
"""
from __future__ import annotations

import html as _html
import json
import os
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import date, timedelta
from itertools import combinations_with_replacement

AQUI = pathlib.Path(__file__).resolve().parent
RAIZ = AQUI.parent
SITIO = RAIZ / "Htmls_Espacial"
PUBLICADO = SITIO / "proyecto-integrador-corte-iii.html"
RUTA = pathlib.Path(os.environ.get("PROYECTO_HTML", PUBLICADO))
RMD_FUENTE = RAIZ / "proyecto" / "plantilla-informe.Rmd"
RMD_PUBLICADO = SITIO / "proyecto-integrador-plantilla.Rmd"
RMD_PRUEBA = pathlib.Path(os.environ.get("PROYECTO_RMD", RMD_FUENTE))
PLANTILLA = RAIZ / "plantilla" / "plantilla-capitulo.html"
POTENCIA = RAIZ / "proyecto" / "potencia.json"
RSCRIPT = "/Library/Frameworks/R.framework/Versions/4.4-arm64/Resources/bin/Rscript"

sys.path.insert(0, str(RAIZ / "proyecto"))
import datos as D  # noqa: E402

# Los módulos se buscan por el título de su h2, no por su número.
N_MODULOS = 10
T_COMO, T_QUE_VALE = "Cómo funciona el proyecto", "Qué datos valen"
T_REPOSITORIO, T_FICHA = "El repositorio en GitHub", "Hito 1 · Ficha del tema"
T_PREREGISTRO, T_AVANCE = "Hito 2 · Preregistro", "Hito 3 · Avance"
T_INFORME, T_CONJUNTA = "Hito 4 · Informe y código", "La opción conjunta con Series de Tiempo"
T_EXPOSICION, T_RUBRICA = "La exposición", "La rúbrica"

# El calendario, recalculado aquí y no importado: un auditor que usara
# `D.semana_del_curso` comprobaría que datos.py coincide consigo mismo.
ANCLA_SEMANA_10 = date(2026, 10, 5)
DIAS = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]
MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto",
         "septiembre", "octubre", "noviembre", "diciembre"]
# F1: las fechas del proyecto de Series, tal como las cerró su plan (§5). Si la
# guía de Series ya tiene su `datos.py`, se cotejan también contra él.
FECHAS_SERIES = {"ficha": date(2026, 10, 27), "preregistro": date(2026, 11, 3),
                 "avance": date(2026, 11, 10), "informe": date(2026, 11, 15)}
# La carpeta del curso de Series, hermana de la de Espacial. Desde un worktree,
# RAIZ.parent es `.claude/worktrees`: se sube hasta encontrarla.
SERIES = next((p / "Series de tiempo" for p in RAIZ.parents if (p / "Series de tiempo").is_dir()),
              RAIZ.parent / "Series de tiempo")
SERIES_DATOS = SERIES / "proyecto" / "datos.py"
FESTIVOS = {date(2026, 11, 2), date(2026, 11, 16)}
CLASE = {"martes", "jueves"}
URL_SERIES_M8 = ("https://jotamao1985.github.io/Series-de-Tiempo_Un_Bosque/"
                 "proyecto-pronostico-corte-iii.html#modulo-8")
NIVEL = {"insuficiente": 1.0, "aceptable": 3.5, "sólido": 5.0}


class Auditoria:
    def __init__(self):
        self.ok, self.fallos = 0, []

    def check(self, frente: str, cond: bool, que: str, detalle: str = "") -> None:
        print(f"  {'OK ' if cond else 'MAL'} [{frente}] {que}"
              + ("" if cond or not detalle else f"  {detalle}"))
        if cond:
            self.ok += 1
        else:
            self.fallos.append((frente, que, detalle))


def texto_visible(t: str) -> str:
    t = re.sub(r"<(script|style)\b.*?</\1>", " ", t, flags=re.S)
    t = re.sub(r"<[^>]+>", " ", t)
    return re.sub(r"\s+", " ", _html.unescape(t)).strip()


def semana(d: date) -> int:
    return 10 + (d - ANCLA_SEMANA_10).days // 7


def frase(d: date) -> str:
    return f"{DIAS[d.weekday()]} {d.day} de {MESES[d.month - 1]}"


def selectores(t: str) -> set:
    return set(re.findall(r"^\s*(\.[a-zA-Z][\w-]*)", t[:t.index("</style>")], re.M)) \
        if "</style>" in t else set()


def numero(s: str) -> float:
    return float(s.replace(",", ".").replace(" ", "").replace(" ", ""))


def nota5(x: float) -> str:
    s = f"{x:.2f}"
    return (s[:-1] if s.endswith("0") else s).replace(".", ",")


def titulos_capitulo(archivo: str) -> dict[int, str]:
    p = SITIO / archivo
    if not p.exists():
        return {}
    t = p.read_text(encoding="utf-8")
    i = t.index("const courseData")
    return {int(a): b for a, b in re.findall(r'id: (\d+), title: "([^"]+)"', t[i:i + 4000])}


def main() -> int:
    A = Auditoria()
    if not RUTA.exists():
        print(f"!! no existe {RUTA}")
        return 1
    H = RUTA.read_text(encoding="utf-8")
    M = "".join(re.findall(r'<template id="module-.*?</template>', H, re.S))
    modulos = re.findall(r'<template id="module-(\d+)">(.*?)</template>', H, re.S)
    por_modulo = {int(n): cuerpo for n, cuerpo in modulos}
    h2 = {int(a): b.strip() for a, b in
          re.findall(r'<template id="module-(\d+)">.*?<h2[^>]*>([^<]+)</h2>', H, re.S)}
    numero_de = {b: a for a, b in h2.items()}

    def mod(titulo: str) -> str:
        return por_modulo.get(numero_de.get(titulo, -1), "")

    V = texto_visible(M)
    rub = re.search(r"RUBRICAS\['proyecto-integrador'\] = (\{.*?\n    \});", H, re.S)
    try:
        R = json.loads(rub.group(1)) if rub else None
    except json.JSONDecodeError:
        R = None

    # ------------------------------------------------------------------ A
    print("\n=== A · Calendario ===")
    fechas = re.findall(r"\b(" + "|".join(DIAS) + r") (\d{1,2}) de (" + "|".join(MESES) + r")\b", V)
    A.check("A", len(fechas) > 0, "el documento imprime fechas", f"({len(fechas)})")
    for dia, n, mes in sorted(set(fechas)):
        d = date(2026, MESES.index(mes) + 1, int(n))
        A.check("A", DIAS[d.weekday()] == dia, f"«{dia} {n} de {mes}» es {dia} en 2026",
                f"(es {DIAS[d.weekday()]})")
    l16 = ANCLA_SEMANA_10 + timedelta(weeks=6)
    permitidas = {h["fecha"] for h in D.HITOS} | set(D.CLASES_EXPOSICION) \
        | {D.RESPUESTA_FICHA, l16 + timedelta(days=5)}
    impresas = {date(2026, MESES.index(m) + 1, int(n)) for _d, n, m in fechas}
    sueltas = sorted(impresas - permitidas)
    A.check("A", not sueltas, "ninguna fecha suelta", f"({', '.join(map(str, sueltas))})")
    en_festivo = sorted(impresas & FESTIVOS)
    A.check("A", not en_festivo, "ninguna fecha impresa cae en festivo", f"({', '.join(map(str, en_festivo))})")
    for h in D.HITOS:
        f = h["fecha"]
        A.check("A", f == FECHAS_SERIES[h["id"]], f"{h['nombre']}: es la fecha del proyecto de Series (F1)",
                f"({f} frente a {FECHAS_SERIES[h['id']]})")
        A.check("A", semana(f) == h["semana"], f"{h['nombre']}: el {frase(f)} cae en la semana {h['semana']}",
                f"(cae en la {semana(f)})")
        A.check("A", f not in FESTIVOS, f"{h['nombre']}: no cae en festivo")
        fila = re.search(rf"<strong>{re.escape(h['nombre'])}</strong></td>.*?</tr>", M, re.S)
        A.check("A", bool(fila) and frase(f) in fila.group(0) and f"<td>{h['semana']}</td>" in fila.group(0),
                f"{h['nombre']}: su fila de la tabla dice «{frase(f)}» y la semana {h['semana']}")
    for titulo, hid in ((T_FICHA, "ficha"), (T_PREREGISTRO, "preregistro"),
                        (T_AVANCE, "avance"), (T_INFORME, "informe")):
        h = D.HITO[hid]
        cierre = f"{frase(h['fecha'])} a las {D.HORA_ENTREGA}"
        txt = texto_visible(mod(titulo))
        A.check("A", cierre in txt and f"semana {h['semana']}" in txt,
                f"«{titulo}» dice que cierra el «{cierre}», en la semana {h['semana']}")
    if SERIES_DATOS.exists():
        txt = SERIES_DATOS.read_text(encoding="utf-8")
        de_series = {date(int(a), int(b), int(c)) for a, b, c in
                     re.findall(r"date\((2026), (\d{1,2}), (\d{1,2})\)", txt)}
        A.check("A", set(FECHAS_SERIES.values()) <= de_series,
                "las cuatro fechas están también en el datos.py de la guía de Series")
    else:
        print("  ·   [A] la guía de Series aún no tiene proyecto/datos.py: se coteja con su plan")
    orden = [h["fecha"] for h in D.HITOS]
    A.check("A", orden == sorted(orden) and len(set(orden)) == len(orden), "los hitos van en orden")
    for d in D.CLASES_EXPOSICION:
        A.check("A", semana(d) == 16 and DIAS[d.weekday()] in CLASE and d not in FESTIVOS,
                f"la exposición puede ir el {frase(d)}: semana 16, día de clase, no festivo")
    rf = D.RESPUESTA_FICHA
    A.check("A", DIAS[rf.weekday()] in CLASE and D.HITO["ficha"]["fecha"] < rf < D.HITO["preregistro"]["fecha"],
            f"la ficha vuelve el {frase(rf)}: día de clase, entre la ficha y el preregistro")
    frase16 = f"del lunes {l16.day} al sábado {(l16 + timedelta(days=5)).day} de {MESES[l16.month - 1]}"
    A.check("A", V.count(frase16) >= 2 and "semana 16" in V,
            f"la exposición: «semana 16» y «{frase16}» en dos módulos")
    fila_expo = re.search(r"<strong>Exposición</strong></td>.*?</tr>", M, re.S)
    A.check("A", D.DIA_EXPOSICION in texto_visible(por_modulo.get(1, ""))
            and D.DIA_EXPOSICION in texto_visible(mod(T_EXPOSICION))
            and bool(fila_expo) and "<td>se acuerda en clase</td>" in fila_expo.group(0),
            "el día de la exposición se acuerda en clase (módulo 1, su módulo y la tabla)")
    horas = set(re.findall(r"a las (\d{1,2}:\d{2})", V))
    A.check("A", horas == {"11:00"}, "todas las entregas cierran a las 11:00", f"({sorted(horas)})")

    # ------------------------------------------------------------------ B
    print("\n=== B · Pesos ===")
    filas_rub = re.findall(r"<tr><td>([^<]+)</td><td><strong>([A-Z]\d)</strong></td><td>.*?</td><td>(\d+)</td></tr>",
                           mod(T_RUBRICA))
    puntos = {c: int(p) for _h, c, p in filas_rub}
    por_hito: dict[str, int] = {}
    for hito, _c, p in filas_rub:
        por_hito[hito] = por_hito.get(hito, 0) + int(p)
    total = re.search(r"<td><strong>Total</strong></td><td></td><td></td><td><strong>(\d+)</strong></td>",
                      mod(T_RUBRICA))
    A.check("B", len(puntos) == 15, "la tabla de la rúbrica tiene 15 criterios", f"({len(puntos)})")
    A.check("B", sum(puntos.values()) == 100 and bool(total) and int(total.group(1)) == 100,
            "la rúbrica suma 100 y su fila de total lo dice", f"(suma {sum(puntos.values())})")
    pesos = dict((h, int(p)) for h, p in re.findall(
        r"<tr><td>([^<]+)</td><td>[A-Z0-9, ]+</td><td>(\d+) %</td><td><strong>[\d,]+ %</strong></td></tr>",
        por_modulo.get(1, "")))
    A.check("B", pesos == por_hito, "la tabla de pesos del módulo 1 dice lo mismo que la rúbrica",
            f"({pesos} frente a {por_hito})")
    for hito, p, c in re.findall(r"<tr><td>([^<]+)</td><td>[A-Z0-9, ]+</td><td>(\d+) %</td><td><strong>([\d,]+) %</strong></td></tr>",
                                 por_modulo.get(1, "")):
        A.check("B", abs(numero(c) - int(p) * 0.5) < 1e-9, f"{hito}: {p} % del proyecto es {c} % del corte")
    hitos_tabla = dict(re.findall(r"<td><strong>(Preregistro|Avance|Informe y código|Exposición)</strong></td>"
                                  r".*?<td>(\d+) %</td>\s*</tr>", M, re.S))
    A.check("B", {k: int(v) for k, v in hitos_tabla.items()} == {"Preregistro": por_hito.get("Preregistro"),
                                                                 "Avance": por_hito.get("Avance"),
                                                                 "Informe y código": por_hito.get("Informe y código"),
                                                                 "Exposición": por_hito.get("Exposición")},
            "la tabla de hitos da a cada hito el peso de la rúbrica", f"({hitos_tabla})")
    A.check("B", R is not None, "el componente de la rúbrica está registrado y es JSON válido")
    if R:
        crit = R["criterios"]
        A.check("B", R.get("total") == 100 and sum(c["puntos"] for c in crit) == 100,
                "el componente suma 100 y declara 100")
        A.check("B", {c["clave"]: c["puntos"] for c in crit} == puntos,
                "el componente y la tabla dan los mismos puntos a cada criterio")
        malos = [c["clave"] for c in crit
                 if [n["nombre"].lower() for n in c["niveles"]] != ["sólido", "aceptable", "insuficiente"]
                 or any(abs(numero(n["rango"]) - c["puntos"] * NIVEL[n["nombre"].lower()] / 5) > 0.051
                        for n in c["niveles"])]
        A.check("B", not malos, "cada nivel aporta puntos × nivel / 5, de mayor a menor", f"({malos})")
    corte = re.search(r"proyecto vale el (\d+) % de la nota del Corte III, y los quices que se hacen en clase, "
                      r"el otro (\d+) %", texto_visible(por_modulo.get(1, "")))
    A.check("B", bool(corte) and int(corte.group(1)) + int(corte.group(2)) == 100 and corte.group(1) == "50",
            "proyecto 50 % + quices = 100 % del Corte III")
    A.check("B", "el proyecto es el 20 % de tu nota final" in texto_visible(por_modulo.get(1, "")),
            "el 50 % de un corte del 40 % es el 20 % del curso")
    A.check("B", "50 % DEL CORTE" in H.replace("&nbsp;", " "), "la cabecera dice el mismo 50 %")
    p_esc = por_hito.get("Preregistro", 0) + por_hito.get("Avance", 0) + por_hito.get("Informe y código", 0)
    e1, e2 = puntos.get("E1", 0), puntos.get("E2", 0)
    alcanzables_q = {round(sum(c) / k, 4) for k in (1, 2, 3) for c in combinations_with_replacement(NIVEL.values(), k)}
    for fila in re.findall(r"<tr><td>([^<]+)</td><td>([\d,]+)</td><td>([\d,]+)</td><td>([\d,]+)</td>"
                           r"<td>([\d,]+)</td><td><strong>([\d,]+)</strong></td></tr>", por_modulo.get(1, "")):
        s, esc, x, q, sin, con = fila
        esc, x, q = numero(esc), numero(x), numero(q)
        sin_c = round((p_esc * esc + e1 * x + e2 * q) / 100, 2)
        con_c = round((p_esc * esc * min(1, q / 3) + e1 * x + e2 * q) / 100, 2)
        A.check("B", nota5(sin_c) == sin and nota5(con_c) == con, f"tope · «{s[:40]}…» se recalcula",
                f"({sin}/{con} frente a {nota5(sin_c)}/{nota5(con_c)})")
        A.check("B", round(q, 4) in alcanzables_q and x in NIVEL.values(),
                f"tope · «{s[:40]}…» usa valores alcanzables")
    for ses, desc, n in re.findall(r"<tr><td>(\d)</td><td>(\d+) %</td><td>([\d,]+)</td></tr>", por_modulo.get(1, "")):
        A.check("B", int(desc) == 15 * int(ses) and nota5(round(4.0 * (1 - 0.15 * int(ses)), 2)) == n,
                f"retraso · {ses} sesiones: −{desc} % y queda en {n}")

    # ------------------------------------------------------------------ C
    print("\n=== C · Decisiones ===")
    v1 = texto_visible(por_modulo.get(1, ""))
    A.check("C", "individual o en parejas" in v1 and "no hay tríos" in v1, "DE1 · individual o en parejas")
    vq = texto_visible(mod(T_QUE_VALE))
    for nombre in ("oldcol", "nc", "auckland", "getisord", "meuse", "deserción", "Saber 11", "simulados"):
        A.check("C", nombre in vq, f"DE2 · «{nombre}» está entre lo que no vale")
    A.check("C", "La geometría municipal sí vale" in vq, "DE2 · la geometría municipal sí vale")
    A.check("C", f"al menos {D.N_MINIMO} unidades" in vq and f"menos de {D.N_MINIMO} unidades"
            in texto_visible(mod(T_FICHA)), f"DE3 · N ≥ {D.N_MINIMO} en el módulo 2 y en la ficha")
    for nombre, n in D.UNIDADES_EJEMPLO:
        dice = re.search(rf"{re.escape(nombre)} \({n}\)", vq)
        A.check("C", bool(dice), f"DE3 · nombra «{nombre}» con su N = {n}")
    si = re.search(r"Con (.+?) \((\d+)\) se cumple; con (.+?) \((\d+)\), no", vq)
    A.check("C", bool(si) and int(si.group(2)) >= D.N_MINIMO > int(si.group(4)),
            "DE3 · el ejemplo que cumple cumple y el que no, no")
    A.check("C", "Un patrón de puntos entra agregado" in vq and "Datos de área" in vq,
            "PE2 · el núcleo son datos de área; los puntos, agregados")
    A.check("C", "una tasa, no un conteo" in vq.lower(), "DE4 · tasa y no conteo")
    examen = [m.start() for m in re.finditer(r"examen final", V)]
    A.check("C", len(examen) == 1 and "no tiene examen final" in V,
            "PE1 · el examen final solo se nombra para decir que no lo hay")
    talleres = re.findall(r"[^.]*Talleres 4 y 5[^.]*", V)
    A.check("C", len(talleres) == 1 and "ni Talleres 4 y 5" in talleres[0],
            "PE1 · los Talleres 4 y 5 solo se nombran para decir que no los hay")
    vr = texto_visible(mod(T_REPOSITORIO))
    A.check("C", "repositorio privado de GitHub" in V and D.USUARIO_DOCENTE in vr and D.NOMBRE_REPO in vr,
            "F3 · repositorio privado, con el docente invitado y su nombre")
    A.check("C", all(f"<code>{h}</code>" in mod(T_REPOSITORIO) for h in ("ficha", "preregistro", "avance", "informe")),
            "F3 · una release por hito, con sus cuatro etiquetas")
    A.check("C", "15 %" in v1 and "sobre la nota original" in v1, "DE5 · −15 % por sesión sobre la nota original")
    mins = [int(x) for x in re.findall(r"<tr><td>[^<]+</td><td>(\d+)</td></tr>", mod(T_EXPOSICION))]
    A.check("C", sum(mins) == D.MINUTOS_EXPOSICION, f"el guion de la exposición suma {D.MINUTOS_EXPOSICION} minutos",
            f"({sum(mins)})")
    A.check("C", "declaración de uso es obligatoria" in v1 and "Es obligatoria" in texto_visible(mod(T_INFORME)),
            "DE11 · la declaración de IA es obligatoria")
    A.check("C", "no se aprueba como núcleo" in vq and all(f"capítulo {c}" in vq for c in (8, 9, 10)),
            "DE8 · los caps. 8, 9 y 10 no se exigen ni son núcleo")

    # ------------------------------------------------------------------ D
    print("\n=== D · Estructura ===")
    A.check("D", len(modulos) == N_MODULOS and sorted(por_modulo) == list(range(1, N_MODULOS + 1)),
            f"{N_MODULOS} módulos numerados sin huecos")
    nav = re.findall(r'\{ id: (\d+), title: "([^"]+)"', H[H.index("const courseData"):H.index("const courseData") + 3000])
    A.check("D", {int(a): b for a, b in nav} == h2, "courseData dice los mismos títulos que los h2")
    A.check("D", PLANTILLA.exists() and selectores(H) == selectores(PLANTILLA.read_text(encoding="utf-8")),
            "el CSS es el de la plantilla")
    ids = re.findall(r' id="([^"]+)"', M)
    A.check("D", len(ids) == len(set(ids)), "identificadores únicos en los módulos")
    A.check("D", M.count("<table>") == M.count("<caption>"), "cada tabla lleva su caption")
    locales = re.findall(r'href="([^"#:]+)"', M)
    rotos = sorted({h for h in locales if not (SITIO / h).exists()})
    A.check("D", not rotos, f"los {len(locales)} enlaces locales resuelven", f"({rotos})")
    A.check("D", not re.search(r'href="(?!https?:)[^"#]+#', M), "ningún enlace local con ancla")
    A.check("D", "Ã" not in H and "<U+" not in H and "â€" not in H, "sin mojibake")
    codigo = re.findall(r'<pre><code class="language-r">(.*?)</code></pre>', M, re.S)
    A.check("D", len(codigo) == 3 and not any("<" in c or ">" in c.replace("&gt;", "") for c in codigo),
            "tres bloques de R, sin «<» ni «>» sin escapar")
    A.check("D", "boton-indice:inicio" in H and 'href="../index.html"' in H, "el botón «← Índice» lleva a la portada")
    A.check("D", "PLANTILLA BASE" not in H and not re.search(r"\['demo", H), "sin restos de la plantilla")
    kb = len(H.encode("utf-8")) / 1024
    A.check("D", kb < 600, f"pesa {kb:.0f} KB (presupuesto 600)")

    # ------------------------------------------------------------------ E
    print("\n=== E · Código R ===")
    A.check("E", RMD_PUBLICADO.exists() and RMD_PUBLICADO.read_bytes() == RMD_FUENTE.read_bytes(),
            "la plantilla .Rmd publicada es la de la fuente")
    A.check("E", f'href="{RMD_PUBLICADO.name}" download' in M, "la guía enlaza la plantilla para descargarla")
    if os.environ.get("PROYECTO_SIN_R") == "1":
        print("  ·   [E] PROYECTO_SIN_R=1: no se corre R")
    elif not pathlib.Path(RSCRIPT).exists():
        A.check("E", False, "hay un Rscript con sf y spdep", RSCRIPT)
    else:
        for i, c in enumerate(codigo, 1):
            with tempfile.TemporaryDirectory() as tmp:
                (pathlib.Path(tmp) / "bloque.R").write_text(_html.unescape(c), encoding="utf-8")
                r = subprocess.run([RSCRIPT, "--vanilla", "bloque.R"], cwd=tmp, capture_output=True,
                                   text=True, timeout=600)
                A.check("E", r.returncode == 0, f"el bloque de R n.º {i} corre en un R limpio",
                        r.stderr.strip().splitlines()[-1] if r.returncode else "")
        for caso in ("ejemplo", "propio"):
            with tempfile.TemporaryDirectory() as tmp:
                shutil.copyfile(RMD_PRUEBA, pathlib.Path(tmp) / "informe.Rmd")
                if caso == "propio":
                    prep = ('library(sf); dir.create("datos"); x <- st_read(system.file("shape/nc.shp", '
                            'package = "sf"), quiet = TRUE); x$nombre <- x$NAME; '
                            'x$tasa <- 1000 * x$NWBIR79 / x$BIR79; st_write(x, "datos/unidades.gpkg", quiet = TRUE); '
                            'write.csv(data.frame(geometria = 101, variable = 100, unidas = 100), '
                            '"datos/conteo-union.csv", row.names = FALSE)')
                    subprocess.run([RSCRIPT, "--vanilla", "-e", prep], cwd=tmp, capture_output=True, timeout=120)
                r = subprocess.run([RSCRIPT, "--vanilla", "-e", 'rmarkdown::render("informe.Rmd", quiet = TRUE)'],
                                   cwd=tmp, capture_output=True, text=True, timeout=600)
                salida = pathlib.Path(tmp) / "informe.html"
                html_out = salida.read_text(encoding="utf-8") if salida.exists() else ""
                # El comentario de la cabecera del .Rmd también dice «DATOS DE
                # EJEMPLO» y pasa al HTML: el aviso es el h2, no la palabra.
                aviso = "Este informe usa los DATOS DE EJEMPLO" in html_out
                A.check("E", r.returncode == 0 and salida.exists() and aviso == (caso == "ejemplo"),
                        f"la plantilla se renderiza con {'los datos de ejemplo' if caso == 'ejemplo' else 'datos propios'} y "
                        + ("avisa que son de ejemplo" if caso == "ejemplo" else "no avisa de ejemplo"),
                        (r.stderr.strip().splitlines() or [""])[-1] if r.returncode else "")
                if caso == "ejemplo":
                    A.check("E", not (pathlib.Path(tmp) / "datos").exists(),
                            "con los datos de ejemplo no escribe nada en datos/")
                else:
                    A.check("E", "traía 101 unidades" in texto_visible(html_out),
                            "con datos propios, el conteo de la unión sale del csv por R en línea")

    # La plantilla, leída: los colores del LISA son los del capítulo 7 y las
    # islas van aparte (revisión de contenido del 21 oct 2026).
    rmd = RMD_PRUEBA.read_text(encoding="utf-8")
    cap7 = (SITIO / "capitulo-7-autocorrelacion.html").read_text(encoding="utf-8")
    pal = re.search(r'"m9": \{"niveles": \[[^\]]+\], "colores": \[([^\]]+)\]', cap7)
    colores7 = re.findall(r'"(#[0-9a-fA-F]{6})"', pal.group(1)) if pal else []
    A.check("E", len(colores7) == 5 and all(c in rmd for c in colores7),
            "la plantilla pinta el LISA con los cinco colores del capítulo 7", f"({colores7})")
    # El p de una isla es NA: lo que la manda aparte es la prueba de is.na(p), no el rótulo.
    A.check("E", re.search(r'ifelse\(is\.na\(p\),\s*"Isla \(sin vecinos\)"', rmd) is not None
            and re.search(r'ifelse\(is\.na\(p\),\s*"Isla \(sin vecinos\)"', _html.unescape(M)) is not None,
            "las islas van aparte en la plantilla y en el código de la guía")
    A.check("E", "lisa_sin" in rmd and "anexo-p" in rmd, "la plantilla trae el mapa sin corregir y la tabla de p")
    A.check("E", "copia aquí" not in rmd.lower(), "la plantilla no pide copiar cifras a mano")

    # ------------------------------------------------------------------ F
    print("\n=== F · Contenido ===")
    # Con enlace o sin él: «módulo 10 del capítulo 7» cuenta igual que con <a>.
    archivo_de = {int(p.name.split("-")[1]): p.name for p in SITIO.glob("capitulo-*.html")}
    citas = re.findall(r'módulos?\s+(\d+)(?:\s+y\s+(\d+))?\s+del\s+(?:<a href="([^"]+)">)?capítulo\s+(\d+)'
                       r'(?:</a>)?(?:,\s*«([^»]+)»)?', M)
    A.check("F", len(citas) >= 12, "la guía cita módulos de los capítulos", f"({len(citas)})")
    for m1, m2, arch, cap, tit in citas:
        if arch:
            A.check("F", arch == archivo_de.get(int(cap)), f"«capítulo {cap}» enlaza su archivo ({arch})")
        arch = arch or archivo_de.get(int(cap), "")
        t = titulos_capitulo(arch)
        for mm in filter(None, (m1, m2)):
            A.check("F", int(mm) in t, f"el capítulo {cap} tiene módulo {mm}")
        if tit:
            real = _html.unescape(re.sub(r"<[^>]+>", "", t.get(int(m1), ""))).replace("`", "")
            A.check("F", re.sub(r"\s+", " ", _html.unescape(re.sub(r"<[^>]+>", "", tit))) == real,
                    f"el módulo {m1} del capítulo {cap} se llama «{real}»", f"(la guía dice «{tit}»)")
    # Los temas atribuidos, por palabra clave: la guía cita para esto, y el módulo lo trata.
    for cap, arch, mm, clave in ((6, "capitulo-6-pesos-espaciales.html", 4, "vecinos"),
                                 (6, "capitulo-6-pesos-espaciales.html", 5, "Umbral"),
                                 (3, "capitulo-3-cartografia-maup.html", 8, "MAUP"),
                                 (2, "capitulo-2-crs-georreferenciacion.html", 2, "Latitud"),
                                 (7, "capitulo-7-autocorrelacion.html", 10, "multiplicidad")):
        A.check("F", clave in titulos_capitulo(arch).get(mm, ""), f"el módulo {mm} del capítulo {cap} trata «{clave}»")
    P = json.loads(POTENCIA.read_text(encoding="utf-8"))
    tabla_pot = re.search(r"<caption>De cada 100 territorios.*?</table>", mod(T_QUE_VALE), re.S)
    filas = re.findall(r"<tr><td>(\d+)</td>((?:<td>[\d,]+ %</td>)+)</tr>", tabla_pot.group(0) if tabla_pot else "")
    rhos = sorted({f["rho"] for f in P["filas"]})
    leidas = {(int(n), r): numero(v) / 100 for n, celdas in filas
              for r, v in zip(rhos, re.findall(r"<td>([\d,]+) %</td>", celdas))}
    del_json = {(f["N"], f["rho"]): f["potencia"] for f in P["filas"]}
    A.check("F", bool(leidas) and all(abs(leidas.get(k, -1) - v) < 1e-9 for k, v in del_json.items()),
            "la tabla de potencia es la del JSON, casilla a casilla")
    A.check("F", P["replicas"] >= 2000, f"la potencia sale de {P['replicas']} réplicas (el plan pedía 2 000)")
    lectura = re.search(r"Con (\d+) unidades y una dependencia de ρ = 0,5, que no es poca, la prueba la detecta "
                        r"(\d+) veces de cada 100", vq)
    A.check("F", bool(lectura) and round(100 * del_json.get((int(lectura.group(1)), 0.5), -1)) == int(lectura.group(2))
            and int(lectura.group(1)) == D.N_MINIMO, "la prosa lee bien la tabla en N mínimo y ρ = 0,5")
    tam = sorted(v for (n, r), v in del_json.items() if r == 0)
    rango = re.search(r"aquí va del ([\d,]+) al ([\d,]+) %", vq)
    A.check("F", bool(rango) and abs(numero(rango.group(1)) - 100 * tam[0]) < 0.051
            and abs(numero(rango.group(2)) - 100 * tam[-1]) < 0.051, "el tamaño que dice la prosa es el de la tabla")
    A.check("F", all(abs(v - 0.05) < 0.02 for v in tam), "el tamaño simulado ronda el 5 % en todas las N")
    A.check("F", all(del_json[(n, 0.3)] < del_json[(n, 0.5)] for n in {k[0] for k in del_json}),
            "la potencia crece con ρ en cada N")

    # ------------------------------------------------------------------ G
    print("\n=== G · Exigencias del material ===")
    exig = re.search(r"<caption>Lo que el material ya enseñó.*?</table>", mod(T_INFORME), re.S)
    filas_ex = re.findall(r'<tr><td><a href="([^"]+)">Capítulo (\d+)</a>, módulo (\d+)</td><td>(.*?)</td>'
                          r'<td>(.*?)</td><td>([A-Z0-9, ]+)</td></tr>', exig.group(0) if exig else "")
    A.check("G", len(filas_ex) >= 10, "la tabla de exigencias tiene sus filas", f"({len(filas_ex)})")
    descriptores = {c["clave"]: " ".join([c["foco"]] + [n["observa"] for n in c["niveles"]]) for c in (R or {}).get("criterios", [])}
    # Lo que cada módulo enseña, en la palabra que su criterio tiene que decir.
    CLAVES = {"Latitud y longitud no son cartesianas": "CRS", "Normalizar o mentir": "tasa",
              "Esquemas de clasificación": "clasificación", "MAUP I · el efecto escala": "escala",
              "La falacia ecológica": "falacia ecológica", "Islas y zero.policy": "islas",
              "Inferencia": "permutación", "Moran es sensible a W": "alternativas",
              "La trampa de la multiplicidad": "corrección", "Getis-Ord Gi y Gi*": "intensidad"}
    for arch, cap, mm, tit, que, crits in filas_ex:
        real = re.sub(r"<[^>]+>", "", titulos_capitulo(arch).get(int(mm), "")).replace("`", "")
        A.check("G", re.sub(r"<[^>]+>", "", tit) == real, f"cap. {cap}, módulo {mm}: «{real}»", f"(dice «{tit}»)")
        clave = CLAVES.get(real)
        A.check("G", clave is not None, f"el auditor sabe qué palabra pide «{real}»")
        for c in [x.strip() for x in crits.split(",")]:
            A.check("G", c in descriptores and clave is not None and clave.lower() in descriptores[c].lower(),
                    f"«{re.sub(r'<[^>]+>', '', que)[:45]}…» → {c} lo nombra ({clave})")
    vp = texto_visible(mod(T_PREREGISTRO))
    n_ej = re.search(r"Con las (\d+) unidades de los departamentos y Bogotá, nsim ≥\s+([\d  ]+)", vp)
    if n_ej:
        N = int(n_ej.group(1))
        minimo = next(k for k in range(1, 10 ** 6) if 2 * N < 0.05 * (k + 1))
        A.check("G", int(numero(n_ej.group(2))) == minimo, f"N = {N} pide nsim ≥ {minimo} (2/(nsim+1) < 0,05/N)",
                f"(la guía dice {n_ej.group(2)})")
    else:
        A.check("G", False, "el preregistro da el ejemplo de nsim con los departamentos")
    A.check("G", r"\text{nsim} + 1 &gt; 40\,N" in mod(T_PREREGISTRO) or r"\text{nsim} + 1 > 40\,N" in mod(T_PREREGISTRO),
            "la fórmula es la del cap. 7: nsim + 1 > 40 N")
    A.check("G", not re.search(r"40\s*[·*]?\s*N\s*[−-]\s*1", V), "nada dice «40·N − 1»")
    # El capítulo 2 (módulo 12, ejercicio 4): el vecino más próximo aguanta en
    # grados porque spdep mide sobre la esfera; lo que se rompe son las
    # coordenadas sueltas y el umbral. La guía no puede decir lo contrario.
    A.check("G", not re.search(r"vecinos en grados|knearneigh\(\) mide distancias", V),
            "nada dice que los k vecinos salgan mal en grados")
    A.check("G", "st_coordinates()" in vp and "kilómetros" in vp,
            "el preregistro dice dónde está la trampa: coordenadas sueltas y el umbral en kilómetros")
    A.check("G", "no significativo nunca se lee" in vq and "menos de 64" not in vq,
            "un Moran no significativo nunca prueba ausencia, con ningún N")
    hab = re.search(r"Las (\d+) de GeoDa y de esda no alcanzan desde (\d+) unidades", vp)
    A.check("G", bool(hab) and not (2 * int(hab.group(2)) < 0.05 * (int(hab.group(1)) + 1))
            and 2 * (int(hab.group(2)) - 1) < 0.05 * (int(hab.group(1)) + 1),
            "las 999 dejan de alcanzar justo en N mínimo")
    cap7 = re.search(r"Las ([\d  ]+) del capítulo 7 alcanzan hasta ([\d  ]+) unidades", vp)
    if cap7:
        ns, nmax = int(numero(cap7.group(1))), int(numero(cap7.group(2)))
        A.check("G", 2 * nmax < 0.05 * (ns + 1) and not 2 * (nmax + 1) < 0.05 * (ns + 1),
                f"{ns} réplicas alcanzan hasta N = {nmax} y no más")
    else:
        A.check("G", False, "el preregistro dice hasta cuántas unidades alcanzan las réplicas del capítulo 7")
    A.check("G", "bilateral" in vp and "bilateral" in texto_visible(mod(T_INFORME)),
            "el p del LISA es el bilateral, en el preregistro y en el informe")
    A.check("G", "plegado" in texto_visible(mod(T_INFORME)) and "10 %" in texto_visible(mod(T_INFORME)),
            "el informe avisa del p plegado de GeoDa")
    A.check("G", 'p[, "Pr(z != E(Ii)) Sim"]' in _html.unescape(M) or 'lp[, "Pr(z != E(Ii)) Sim"]' in _html.unescape(M),
            "el código usa la columna del p bilateral")

    # ------------------------------------------------------------------ H
    print("\n=== H · La conjunta ===")
    vc = texto_visible(mod(T_CONJUNTA))
    A.check("H", f'href="{URL_SERIES_M8}"' in mod(T_CONJUNTA), "el módulo de la conjunta enlaza el módulo 8 de Series")
    A.check("H", M.count(URL_SERIES_M8) == 1 and len(re.findall(r"Series-de-Tiempo_Un_Bosque", M)) == 1,
            "y es el único enlace a la guía de Series")
    A.check("H", "solo ese módulo" in vc and "manda el de Series" in vc, "dice que las reglas viven solo allí")
    # La conjunta con Series y un acuerdo individual por escrito son las dos únicas vías
    # para que un trabajo cuente en dos cursos (J4 de Javier, 21 oct: la conjunta de
    # Diseño y Espacial es un acuerdo individual, fuera de la guía). Ninguna de las dos
    # puede desaparecer ni volver la «única excepción», que contradiría el acuerdo.
    A.check("H", "autoplagio" in vc and "acuerdo individual por escrito" in vc
            and "única excepción" not in vc,
            "dice que fuera de la conjunta y de un acuerdo individual por escrito es autoplagio")
    COPIAS = [(r"proyecto-st-ee", "el nombre del repositorio conjunto"),
              (r"1,5 veces", "el tamaño de la conjunta"),
              (r"\b15 páginas", "las páginas de la conjunta"),
              (r"\b15 min", "los minutos de la conjunta"),
              (r"parejas? mixtas?", "las parejas mixtas"),
              (r"tres preguntas de cada materia", "las preguntas por materia"),
              (r"rezago\s*(≥|>=|mayor o igual)", "el rezago ≥ h de la pregunta (b)"),
              (r"\(a\)|\(b\)|\(c\)", "las preguntas (a), (b) o (c) por su letra"),
              (r"cambiar de opción hasta", "hasta cuándo se cambia de opción"),
              (r"Diebold", "el protocolo temporal de Series")]
    for patron, que in COPIAS:
        A.check("H", not re.search(patron, V), f"no copia {que}")
    if R:
        con = {c["clave"] for c in R["criterios"] if "En la conjunta:" in c["foco"]}
        A.check("H", con == {"P2", "A2", "I3", "I4"}, "P2, A2, I3 e I4 llevan su descriptor de la conjunta", f"({sorted(con)})")
        e2 = next((c for c in R["criterios"] if c["clave"] == "E2"), {})
        A.check("H", "solo las preguntas de Estadística Espacial" in e2.get("foco", ""),
                "E2 cuenta en la conjunta solo las preguntas de Espacial")
    serie_html = SERIES / "Htmls_Series" / "proyecto-pronostico-corte-iii.html"
    if serie_html.exists():
        t = serie_html.read_text(encoding="utf-8")
        m8 = re.search(r'<template id="module-8">.*?<h2[^>]*>([^<]+)</h2>', t, re.S)
        A.check("H", bool(m8) and "Espacial" in m8.group(1), "el módulo 8 de la guía de Series es el de la conjunta",
                f"({m8.group(1).strip() if m8 else 'sin módulo 8'})")
    else:
        print("  ·   [H] la guía de Series aún no está en su árbol: se comprueba solo la forma del enlace")

    print(f"\n{A.ok} comprobaciones en verde, {len(A.fallos)} fallos")
    for f, q, d in A.fallos:
        print(f"  ✗ [{f}] {q} {d}")
    return 1 if A.fallos else 0


if __name__ == "__main__":
    sys.exit(main())
