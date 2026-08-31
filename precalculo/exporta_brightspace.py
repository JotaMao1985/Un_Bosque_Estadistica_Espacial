#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Banco de la Biblioteca de Preguntas de Brightspace desde un documento publicado.

Lee las preguntas del HTML **publicado** —la misma superficie que audita
`audita_preparcial1.py`, y por el mismo motivo: lo que se exporta tiene que ser
lo que el estudiante vio, no lo que un JSON dice que vio— y escribe un paquete
QTI 1.2 con las extensiones `d2l_2p0` que exige D2L.

Cuatro tipos de pregunta y cuatro destinos distintos:

    opcion    ->  Multiple Choice
    multiple  ->  Multi-Select
    grafico   ->  Multiple Choice, con el gráfico convertido a PNG
    numerica  ->  Multiple Choice, SOLO si el precálculo trae distractores

El último es el que obliga a este guion a decir que no. La Biblioteca de
Preguntas **no importa respuesta numérica**, así que una `numerica` solo puede
viajar convertida en opción múltiple, y para eso hacen falta tres distractores
que sean errores concretos. Dos de las siete los tienen calculados en
`preparcial1_datos.json`. Las otras cinco nombran el error en prosa —«si te
salió un porcentaje bastante menor»— sin cifra, y **inventarles una aquí sería
escribir a mano un número del material**, que es justo lo que este repositorio
no hace. Se quedan fuera, y el informe las nombra una a una.

Uso:

    precalculo/exporta_brightspace.py \
        --html Htmls_Espacial/preparcial-corte-1.html \
        --datos precalculo/salidas/preparcial1_datos.json \
        --prefijo EE_C1 --titulo "Estadística Espacial · Corte I" \
        --salida parcial/brightspace --sonda

La salida NO se versiona ni se publica: `parcial/` queda fuera de la lista
blanca del `.gitignore` a propósito.
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
import random
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "precalculo"))

# El analizador de literales de JavaScript vive en el auditor del preparcial y
# de ahí se importa. Copiarlo aquí sería el defecto que `puntual.R` documenta
# en el anexo A.18 del plan: dos copias de un convenio se desincronizan sin que
# nada falle, y la de este guion fallaría en silencio exportando de menos.
from audita_preparcial1 import lee_autoevaluaciones  # noqa: E402


# =====================================================================
# LOCALIZAR d2l_items.py, que es de la skill y no de este repositorio
# =====================================================================
CANDIDATOS_SKILL = [
    Path.home() / ".claude/skills/brightspace-elbosque/scripts",
    Path.home() / ".claude/plugins/cache/brightspace-elbosque/scripts",
]


def carga_d2l(ruta_skill: str | None):
    rutas = [Path(ruta_skill)] if ruta_skill else CANDIDATOS_SKILL
    for r in rutas:
        if (r / "d2l_items.py").exists():
            sys.path.insert(0, str(r))
            import d2l_items  # noqa: PLC0415
            return d2l_items, r
    sys.exit(
        "PARADO: no encuentro `d2l_items.py`, que es de la skill "
        "`brightspace-elbosque` y no de este repositorio.\n"
        "        Busqué en:\n          " + "\n          ".join(str(r) for r in rutas) +
        "\n        Pásame su carpeta con --skill <ruta>/scripts."
    )


# =====================================================================
# LOS SEIS GRÁFICOS
#
# El dato sale del precálculo; lo que se declara aquí es SOLO presentación
# —qué serie va en qué eje, con qué rótulo y con qué trazo—, copiada de la
# función de dibujo que el documento publica.
#
# Y no se copia a ciegas: `comprueba_grafico()` contrasta esta declaración
# contra el `dibujar` real. El día que el material añada una serie a un
# gráfico, este guion para en vez de exportar una imagen que ya no es la que
# el estudiante vio. Es el único defecto de los seis que no daría ningún
# síntoma: la pregunta seguiría importando bien, con la figura equivocada.
# =====================================================================
PRIMARIO, SECUNDARIO, GRIS = "#012820", "#FF6600", "#94a3b8"

GRAFICOS = {
    "g_cobertura": {
        "clase": "linea",
        "x": "phi",
        "titulo_x": "φ",
        "series": [
            {"label": "Cobertura real", "campo": "cobertura",
             "color": PRIMARIO, "trazo": "-", "puntos": True},
            {"label": "Nominal 95 %", "constante": 0.95,
             "color": SECUNDARIO, "trazo": "--", "puntos": False},
        ],
    },
    "g_variograma": {
        "clase": "linea",
        "x": "lags",
        "titulo_x": "Retardo",
        "series": [
            {"label": "Teórico", "campo": "teorico",
             "color": PRIMARIO, "trazo": "--", "puntos": False},
            {"label": "Media de las realizaciones", "campo": "media",
             "color": SECUNDARIO, "trazo": "-", "puntos": True},
            {"label": "Percentil 5", "campo": "q05",
             "color": GRIS, "trazo": "-", "puntos": False},
            {"label": "Percentil 95", "campo": "q95",
             "color": GRIS, "trazo": "-", "puntos": False},
        ],
    },
    "g_grado": {
        "clase": "linea",
        "x": "lat",
        "titulo_x": "Latitud (°)",
        "series": [
            {"label": "Metros por grado de longitud", "campo": "elipsoide",
             "color": PRIMARIO, "trazo": "-", "puntos": True},
            {"label": "El valor del ecuador", "primero_de": "elipsoide",
             "color": SECUNDARIO, "trazo": "--", "puntos": False},
        ],
    },
    "g_escala": {
        "clase": "linea",
        "x": "zonas",
        "titulo_x": "Número de zonas",
        "series": [
            {"label": "Correlación media entre zonas", "campo": "media",
             "color": PRIMARIO, "trazo": "-", "puntos": True},
            {"label": "Sobre estudiantes individuales",
             "reutilizado": "c3m8_r_ind",
             "color": SECUNDARIO, "trazo": "--", "puntos": False},
        ],
    },
    "g_proyecciones": {
        "clase": "barras",
        "x": "nombre",
        "y": "razon_max",
        "titulo_x": "Proyección",
        "etiqueta": "Razón de área máxima",
    },
    "g_discordancia": {
        "clase": "barras",
        "x": "etiqueta",
        "y": "pct",
        "titulo_x": "Par de esquemas comparados",
        "etiqueta": "% de municipios que cambian de clase",
        "abrevia": {"Intervalos iguales": "Iguales", "Fisher-Jenks": "Fisher",
                    "Desviación estándar": "Desv. est."},
        "parte_por": " / ",
    },
}


def comprueba_grafico(clave: str, dibujar: str) -> None:
    """La declaración de arriba contra el `dibujar` que publica el documento."""
    spec = GRAFICOS[clave]
    campos_usa = set(re.findall(r"\bg\.(\w+)", dibujar))
    if spec["clase"] == "linea":
        declara = {spec["x"]}
        for s in spec["series"]:
            for k in ("campo", "primero_de"):
                if k in s:
                    declara.add(s[k])
        rotulos_usa = re.findall(r"label:\s*'([^']*)'", dibujar)
        rotulos_dec = [s["label"] for s in spec["series"]]
        if rotulos_usa != rotulos_dec:
            sys.exit(f"PARADO: {clave} dibuja las series {rotulos_usa} y aquí "
                     f"están declaradas {rotulos_dec}")
    else:
        declara = {spec["x"], spec["y"]}
    if campos_usa != declara:
        sys.exit(f"PARADO: {clave} usa los campos {sorted(campos_usa)} y aquí "
                 f"están declarados {sorted(declara)}")
    # Cualquier dato de fuera de `graficos` tiene que estar declarado.
    fuera = set(re.findall(r"DATOS_PRE1\.reutilizado\.(\w+)", dibujar))
    declara_fuera = {s["reutilizado"] for s in spec.get("series", [])
                     if "reutilizado" in s}
    if fuera != declara_fuera:
        sys.exit(f"PARADO: {clave} lee de `reutilizado` {sorted(fuera)} y aquí "
                 f"está declarado {sorted(declara_fuera)}")


def dibuja(clave: str, datos: dict, alto: int) -> bytes:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    spec = GRAFICOS[clave]
    g = datos["graficos"][clave]
    fig, ax = plt.subplots(figsize=(7.6, alto / 100), dpi=200)

    if spec["clase"] == "linea":
        x = list(range(len(g[spec["x"]])))
        for s in spec["series"]:
            if "campo" in s:
                y = g[s["campo"]]
            elif "constante" in s:
                y = [s["constante"]] * len(x)
            elif "primero_de" in s:
                y = [g[s["primero_de"]][0]] * len(x)
            else:
                y = [datos["reutilizado"][s["reutilizado"]]["valor"]] * len(x)
            ax.plot(x, y, color=s["color"], linestyle=s["trazo"],
                    linewidth=2 if s["puntos"] else 1.5, label=s["label"],
                    marker="o" if s["puntos"] else None, markersize=3.5)
        ax.set_xticks(x)
        ax.set_xticklabels([str(v) for v in g[spec["x"]]], fontsize=8)
        ax.legend(fontsize=8, frameon=False)
    else:
        etiquetas = g[spec["x"]]
        if "parte_por" in spec:
            ab = spec.get("abrevia", {})
            etiquetas = ["\n".join(ab.get(p, p) for p in e.split(spec["parte_por"]))
                         for e in etiquetas]
        x = list(range(len(etiquetas)))
        ax.bar(x, g[spec["y"]], color=PRIMARIO, width=0.4)
        ax.set_xticks(x)
        ax.set_xticklabels(etiquetas, fontsize=7)
        ax.set_ylabel(spec["etiqueta"], fontsize=8)

    ax.set_xlabel(spec.get("titulo_x", ""), fontsize=8)
    ax.tick_params(labelsize=8)
    ax.grid(axis="y", color=GRIS, alpha=0.35, linewidth=0.6)
    ax.set_axisbelow(True)
    for lado in ("top", "right"):
        ax.spines[lado].set_visible(False)
    fig.tight_layout()
    buf = io.BytesIO()
    fig.savefig(buf, format="png")
    plt.close(fig)
    return buf.getvalue()


# =====================================================================
# LAS NUMÉRICAS
# =====================================================================
_RE_NUM_PROSA = re.compile(r"\d[\d.,]*")


def _numeros(texto: str):
    for m in _RE_NUM_PROSA.finditer(texto.replace("&nbsp;", " ")):
        t = m.group(0).rstrip(".,")
        try:
            yield t, float(t)
        except ValueError:
            continue


def decimales_del_material(q: dict) -> int:
    """Con cuántos decimales escribe el propio documento la respuesta.

    No se elige aquí: se lee de la retroalimentación de acierto, que es donde
    el material ya decidió cómo se escribe ese número. Elegirlo aquí sería
    publicar en el banco una cifra con un formato que el estudiante no vio.
    """
    for t, v in _numeros(q["retroAcierto"]):
        if abs(v - q["respuesta"]) <= q["tolerancia"]:
            return len(t.split(".")[1]) if "." in t else 0
    sys.exit("PARADO: la retroalimentación de acierto de una numérica no "
             f"contiene su propia respuesta ({q['respuesta']})")


def numerica_a_opciones(q: dict, nuevo: dict, dec: int):
    """Cuatro opciones desde el precálculo, o `None` si no hay distractores.

    El emparejamiento va por MÓDULO y por valor, y no solo por valor. Emparejar
    por valor a secas funcionó mientras hubo dos ítems con distractores y dejó
    de funcionar en cuanto hubo siete: la reducción del índice espacial vale
    11,10608 con tolerancia 0,2 y los condados que se mueven de clase valen 11
    con tolerancia 0,5, así que **cada uno cae dentro de la tolerancia del
    otro**. Sin el módulo, una de las dos preguntas se habría llevado los
    distractores de la otra —tres cifras plausibles, explicaciones que hablan
    de otra cosa— sin que nada fallara.
    """
    # `repaso.orden` es 105 para cap1.m5 y 211 para cap2.m11.
    orden = q["repaso"]["orden"]
    modulo = f"cap{orden // 100}.m{orden % 100}"
    candidatos = [
        k for k, v in nuevo.items()
        if v.get("distractores") and v.get("modulo") == modulo
        and v.get("correcto") is not None
        and abs(v["correcto"] - q["respuesta"]) <= q["tolerancia"]
    ]
    if len(candidatos) > 1:
        sys.exit(f"PARADO: {modulo} tiene {len(candidatos)} cálculos nuevos que "
                 f"encajan con la misma pregunta: {candidatos}")
    if not candidatos:
        return None, None
    clave = candidatos[0]

    fmt = lambda x: f"{x:.{dec}f}"                                    # noqa: E731
    prosa = q["retroFallo"].replace("&nbsp;", " ")
    correcto = fmt(nuevo[clave]["correcto"])
    ops = [{"texto": correcto, "correcta": True, "retro": q["retroAcierto"]}]
    for d in nuevo[clave]["distractores"]:
        texto = fmt(d["valor"])
        # Si el banco escribiera un distractor que la prosa del documento no
        # nombra, el estudiante leería una explicación que no corresponde a
        # ninguna cifra que haya visto nunca.
        if texto not in prosa:
            sys.exit(f"PARADO: el distractor {texto} de «{clave}» no aparece "
                     "en la retroalimentación de fallo del documento")
        ops.append({"texto": texto, "correcta": False,
                    "retro": f"Sale de {d['error']}. La respuesta es {correcto}."})
    return ops, clave


# =====================================================================
# EL ENUNCIADO
# =====================================================================
def enunciado(q: dict, con_pista: bool, img: str | None) -> str:
    partes = [f"<p>{q['pregunta']}</p>"]
    if img:
        partes.append(
            f'<p><img src="images/{img}" alt="{q["descripcionGrafico"]}" '
            'style="max-width:100%;height:auto;"></p>')
    if con_pista and q.get("pista"):
        partes.append(f"<p><em>Pista:</em> {q['pista']}</p>")
    if q["tipo"] == "multiple":
        partes.append("<p><strong>Marca todas las que apliquen.</strong></p>")
    return "\n".join(partes)


# =====================================================================
def main() -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--html", required=True)
    p.add_argument("--datos", required=True)
    p.add_argument("--salida", default="parcial/brightspace")
    p.add_argument("--prefijo", required=True,
                   help="raíz del identificador estable, p. ej. EE_C1")
    p.add_argument("--titulo", required=True)
    p.add_argument("--skill", default=None, help="carpeta scripts/ de la skill")
    p.add_argument("--sin-pista", action="store_true")
    p.add_argument("--sonda", action="store_true",
                   help="paquete extra con un ítem de cada forma, para probar "
                        "la importación antes de subir el banco entero")
    a = p.parse_args()

    d2l, ruta_skill = carga_d2l(a.skill)
    html = Path(a.html).read_text(encoding="utf-8")
    datos = json.loads(Path(a.datos).read_text(encoding="utf-8"))
    bloques = lee_autoevaluaciones(html)
    if not bloques:
        sys.exit(f"PARADO: {a.html} no publica ninguna autoevaluación")

    crudos, imagenes, fuera, resumen = [], {}, [], []
    for nombre, preguntas in bloques.items():
        letra = nombre.split("-")[-1].upper()
        for i, q in enumerate(preguntas, 1):
            qid = f"{a.prefijo}_{letra}{i:02d}"
            titulo = q["repaso"]["etiqueta"]
            tipo, img = q["tipo"], None

            if tipo == "numerica":
                dec = decimales_del_material(q)
                ops, clave = numerica_a_opciones(q, datos.get("nuevo", {}), dec)
                if ops is None:
                    fuera.append((qid, titulo,
                                  "el precálculo no trae distractores calculados"))
                    continue
                resumen.append(f"{qid} · numérica convertida desde «{clave}»")
            else:
                ops = [{"texto": o["texto"], "correcta": bool(o["correcta"]),
                        "retro": o.get("retro", "")} for o in q["opciones"]]

            if tipo == "grafico":
                serie = re.search(r"DATOS_PRE1\.graficos\.(\w+)", q["dibujar"])
                if not serie or serie.group(1) not in GRAFICOS:
                    sys.exit(f"PARADO: {qid} dibuja una serie que este guion no "
                             "sabe convertir a imagen")
                clave = serie.group(1)
                comprueba_grafico(clave, q["dibujar"])
                img = f"{clave}.png"
                imagenes[f"images/{img}"] = dibuja(clave, datos, q.get("alto", 250))

            # El orden se baraja con semilla derivada del qid: estable entre
            # exportaciones —el mismo banco dos veces da el mismo ZIP— y
            # distinto de la posición en que lo escribió el documento, que en
            # este preparcial llegó a ser SIEMPRE la primera (§12.6 de su plan).
            random.Random(int(hashlib.sha256(qid.encode()).hexdigest()[:8], 16)).shuffle(ops)

            # Se guardan los ARGUMENTOS, no el ítem: `construye_item`
            # devuelve el XML ya cerrado, y la sonda necesita volver a
            # numerar las páginas —el auditor las exige de 1 a N sin huecos,
            # y las del banco no son contiguas al quedarse tres.
            crudos.append({
                "qid": qid, "titulo": titulo,
                "enunciado_html": enunciado(q, not a.sin_pista, img),
                "opciones": ops,
                "tipo": d2l.MS if tipo == "multiple" else d2l.MC,
                "_img": img is not None})

    if not crudos:
        sys.exit("PARADO: cero ítems. Un banco vacío se importa sin protestar "
                 "y deja el cuestionario sin preguntas.")

    def arma(seleccion):
        return [d2l.construye_item(
            qid=c["qid"], enunciado_html=c["enunciado_html"],
            opciones=c["opciones"], titulo=c["titulo"], pagina=n, tipo=c["tipo"])
            for n, c in enumerate(seleccion, 1)]

    items = arma(crudos)

    salida = Path(a.salida)
    salida.mkdir(parents=True, exist_ok=True)
    zip_banco = salida / "banco_brightspace.zip"
    d2l.escribe_paquete(str(zip_banco), items, a.titulo, imagenes=imagenes)

    zip_sonda = None
    if a.sonda:
        # Una de cada forma. El Multi-Select es el que hay que probar: la skill
        # avisa de que su estructura no está validada en importaciones reales.
        elegidos, vistos = [], set()
        for c in crudos:
            marca = (c["tipo"], c["_img"])
            if marca not in vistos:
                vistos.add(marca)
                elegidos.append(c)
        elegidos = arma(elegidos)
        # Solo las imágenes que la sonda cita: un paquete que declara seis y
        # usa una importa bien y no prueba nada de las otras cinco.
        img_sonda = {r: b for r, b in imagenes.items()
                     if any(r in it for it in elegidos)}
        zip_sonda = salida / "sonda_brightspace.zip"
        d2l.escribe_paquete(str(zip_sonda), elegidos, a.titulo + " · sonda",
                            imagenes=img_sonda)

    print(f"\nBanco: {zip_banco}  ({zip_banco.stat().st_size / 1024:.0f} KB)")
    if zip_sonda:
        print(f"Sonda: {zip_sonda}  ({zip_sonda.stat().st_size / 1024:.0f} KB)")
    print(f"Ítems: {len(items)}   Imágenes: {len(imagenes)}")
    for r in resumen:
        print(f"  · {r}")
    if fuera:
        print(f"\nFUERA DEL BANCO — {len(fuera)}, y se nombran para que el "
              "recorte no pase por silencio:")
        for qid, titulo, motivo in fuera:
            print(f"  · {qid}  {titulo}\n      {motivo}")
    print(f"\nAudita con:\n  python3 {ruta_skill / 'audita_paquete.py'} "
          f"--zip {zip_banco}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
