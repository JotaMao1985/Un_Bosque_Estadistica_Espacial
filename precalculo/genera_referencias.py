#!/usr/bin/env python3
"""
genera_referencias.py — las citas y las listas de referencias, generadas

Material de Estadística Espacial 2026-II (20929). Portado de Series de Tiempo
(20948). Diferencia: aquí todo capítulo se ENSAMBLA (`precalculo/ensambla_capN.py`),
así que `genera()` se llama desde el ensamblador antes de escribir el HTML, y
este guion, sobre el HTML publicado, solo sirve con `--comprobar`.

Nadie escribe a mano «(Cleveland et al., 1990, §2)» ni una entrada de la lista
de referencias: quien redacta deja en el HTML solo la clave de la obra y el
localizador, y este guion escribe el resto con pandoc `--citeproc` y el estilo
APA 7 en español (`bibliografia/apa-es.csl`) a partir de
`bibliografia/referencias.json`, que a su vez sale de Zotero.

Lo que escribe quien redacta:

    <cite class="cita" data-ref="cleveland1990stl" data-loc="§2"></cite>

  · `data-ref`   clave de la obra en referencias.json
  · `data-loc`   localizador, tal como debe leerse: «§3.6», «p. 15», «cap. 2»
  · `data-modo`  `parentesis` (por defecto) → (Cleveland et al., 1990, §2)
                 `narrativa`               → Cleveland et al. (1990, §2)
                 `suelta`                  → Cleveland et al., 1990, §2

Y tres pares de marcadores, que este guion rellena:

    <!--FUENTES-MODULO:inicio-->  … <!--FUENTES-MODULO:fin-->
        dentro de un <template id="module-N">: las obras citadas en ese módulo.
        Cada cita enlaza aquí, porque solo el módulo abierto está en el DOM.
    <!--REFERENCIAS-CAPITULO:inicio--> … <!--REFERENCIAS-CAPITULO:fin-->
        todas las obras citadas en el capítulo.
    <!--PIE-REFERENCIAS:inicio--> … <!--PIE-REFERENCIAS:fin-->
        la bibliografía básica del curso (rol `basica` en zotero.lock.json),
        más lo que declare `bibliografia/pie.json` (ver «EL PIE», abajo).

EL PIE (R4 · T4.3, 2026-11-23). El pie «Referencias Bibliográficas» lo llevan
TODOS los documentos, porque viene de `plantilla/plantilla-capitulo.html`. Por
eso este guion se pasa sobre la PLANTILLA MISMA:

    python3 precalculo/genera_referencias.py plantilla/plantilla-capitulo.html

y después se reensambla cada documento, que hereda el pie ya escrito. Hacerlo
en cada ensamblador habría sido tocar doce guiones para escribir doce veces el
mismo bloque, y la plantilla —que también se abre en el navegador— se habría
quedado con el pie vacío. `audita_citas.py` (F15) comprueba que la plantilla y
cada documento publicado llevan exactamente el pie que este guion escribiría.

Zotero decide QUÉ obras son básicas y CÓMO se escribe cada una. Lo que Zotero
no puede decir vive en `bibliografia/pie.json`, declarado y con su motivo:

  · `orden`        en qué orden salen (el texto guía, primero);
  · `adicionales`  obras que entran al pie sin ser de rol `basica`;
  · `anotaciones`  lo que el pie dice de una obra y APA no trae: que es el
                   texto guía, su versión de lectura libre, su licencia;
  · `sin_alta`     líneas FIJAS de obras que no están en Zotero, con el motivo
                   y lo que falta para darlas de alta;
  · `congelados`   documentos repartidos que no se reensamblan y conservan el
                   pie con que se repartieron;
  · `vetados`      lo que el pie no puede volver a decir.

Sin `pie.json` el pie son las básicas, por orden alfabético y sin más.

Es idempotente: volver a correrlo sobre un archivo ya generado no cambia nada.
`audita_citas.py` (F02) se apoya en eso para comprobar que el HTML publicado
es exactamente el que este guion escribiría.

Uso:  python3 precalculo/genera_referencias.py                 # los capítulos
      python3 precalculo/genera_referencias.py plantilla/plantilla-capitulo.html   # el pie
      python3 precalculo/genera_referencias.py ruta/al.html …
      python3 precalculo/genera_referencias.py --comprobar     # no escribe

Los capítulos 3–6 se ensamblan: ahí el guion hay que pasarlo sobre las fuentes
de `ensamblado/capN/` y reensamblar, no sobre el HTML final.
"""
from __future__ import annotations

import argparse
import copy
import html
import json
import pathlib
import re
import subprocess
import sys
import tempfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from fuentes_config import BIB, RAIZ, SITIO  # noqa: E402
CAPITULOS = sorted(SITIO.glob("capitulo-*.html"))

RE_CITA = re.compile(r'<cite class="cita"(?P<atributos>[^>]*)>(?P<dentro>.*?)</cite>', re.S)
RE_ATRIBUTO = re.compile(r'(data-[a-z]+)="([^"]*)"')
RE_MODULO = re.compile(
    r'(?P<abre><template id="module-(?P<n>\d+)"[^>]*>)(?P<cuerpo>.*?)(?P<cierra></template>)', re.S
)
MODOS = ("parentesis", "narrativa", "suelta")


def marcadores(nombre: str) -> re.Pattern:
    return re.compile(
        rf"(?P<abre><!--{nombre}:inicio-->)(?P<dentro>.*?)(?P<cierra><!--{nombre}:fin-->)", re.S
    )


RE_FUENTES_MODULO = marcadores("FUENTES-MODULO")
RE_REFS_CAPITULO = marcadores("REFERENCIAS-CAPITULO")
RE_PIE = marcadores("PIE-REFERENCIAS")
PIE_CAMPOS = ("orden", "adicionales", "anotaciones", "sin_alta", "congelados", "vetados")


class ErrorDeCita(Exception):
    pass


# --------------------------------------------------------------------------- #
# Biblioteca
# --------------------------------------------------------------------------- #
def carga_biblioteca() -> tuple[dict[str, dict], dict[str, dict]]:
    referencias = json.loads((BIB / "referencias.json").read_text("utf-8"))
    candado = json.loads((BIB / "zotero.lock.json").read_text("utf-8"))["obras"]
    return {r["id"]: r for r in referencias}, candado


def para_pandoc(obras: list[dict]) -> list[dict]:
    """Copia de las obras con el rango de páginas en raya corta (3–73)."""
    salida = copy.deepcopy(obras)
    for o in salida:
        # (20929) Crossref escribe edition-number 0 o 1 en libros de primera edición
        # (Baddeley et al., 2015; Pebesma y Bivand, 2023), y APA no pone «1.ª ed.».
        if str(o.get("edition", "")).strip() in ("0", "1"):
            o.pop("edition")
        if isinstance(o.get("page"), str):
            o["page"] = re.sub(r"(?<=\d)\s*-+\s*(?=\d)", "–", o["page"])
    return salida


def pandoc(biblioteca: dict[str, dict], claves: list[str]) -> tuple[dict, dict, dict]:
    """Devuelve ({clave: autores}, {clave: año}, {clave: entrada HTML}).

    Todas las claves van en UNA pasada para que la desambiguación de citeproc
    (1990a, 1990b) sea la misma en las citas y en la lista.
    """
    if not claves:
        return {}, {}, {}
    obras = para_pandoc([biblioteca[c] for c in claves])
    cuerpo = "\n\n".join(f"@{c}\n\n[-@{c}]" for c in claves)
    documento = f'---\nlang: es\nnocite: "@*"\n---\n\n{cuerpo}\n'
    # (20929) Temporal fuera del repo: aquí `bibliografia/` entera está en la
    # lista blanca de .gitignore, y un `_local/` dentro se versionaría.
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as tmp:
        tmp.write(json.dumps(obras, ensure_ascii=False))
    ruta_json = pathlib.Path(tmp.name)
    proceso = subprocess.run(
        ["pandoc", "-f", "markdown", "-t", "html", "--wrap=none", "--citeproc",
         "--bibliography", str(ruta_json), "--csl", str(BIB / "apa-es.csl")],
        input=documento, capture_output=True, text=True,
    )
    ruta_json.unlink()
    if proceso.returncode != 0:
        raise ErrorDeCita(f"pandoc falló: {proceso.stderr.strip()}")
    salida = proceso.stdout

    spans = re.findall(r'<span class="citation" data-cites="([^"]+)">(.*?)</span>', salida, re.S)
    autores, anios = {}, {}
    for clave, texto in spans:
        m = re.fullmatch(r"\((.*)\)", texto.strip(), re.S)
        if m:                                   # [-@clave] → «(1990)»
            anios[clave] = m.group(1)
        else:                                   # @clave → «Cleveland et al. (1990)»
            autores[clave] = re.sub(r"\s*\([^()]*\)\s*$", "", texto.strip())
    entradas = dict(re.findall(
        r'<div id="ref-([^"]+)" class="csl-entry"[^>]*>\s*(.*?)\s*</div>', salida, re.S
    ))
    faltan = [c for c in claves if c not in autores or c not in anios or c not in entradas]
    if faltan:
        raise ErrorDeCita(f"pandoc no devolvió cita o entrada para: {', '.join(faltan)}")
    return autores, anios, entradas


def carga_pie(directorio: pathlib.Path | None = None) -> dict:
    """`pie.json` de esa bibliografía, o un pie sin nada declarado si no existe.

    Es JSON y no YAML porque los ensambladores corren con el Python de geo_env,
    que no trae PyYAML; por eso los motivos van como campos y no como comentarios.
    """
    ruta = (directorio or BIB) / "pie.json"
    dato = json.loads(ruta.read_text("utf-8")) if ruta.exists() else {}
    return {campo: dato.get(campo) or ([] if campo in ("orden", "vetados") else {})
            for campo in PIE_CAMPOS}


def claves_del_pie(biblioteca: dict[str, dict], candado: dict[str, dict], pie: dict) -> list[str]:
    """Las claves del pie, en su orden. Las de `sin_alta` no están en Zotero."""
    if pie["orden"]:
        return list(pie["orden"])
    return [c for c, o in candado.items() if o["rol"] == "basica"]


def problemas_del_pie(biblioteca: dict[str, dict], candado: dict[str, dict], pie: dict) -> list[str]:
    """Lo que hace que `pie.json` no se pueda aplicar. Vacío si está bien.

    Lo que se vigila es que nada entre o salga del pie EN SILENCIO: una obra
    que Zotero pasa a básica y nadie ordenó, una línea fija de una obra que ya
    tiene alta, una anotación sobre una obra que ya no está.
    """
    p: list[str] = []
    basicas = {c for c, o in candado.items() if o["rol"] == "basica"}
    adicionales, sin_alta = set(pie["adicionales"]), set(pie["sin_alta"])
    for c in sorted(adicionales):
        if c not in biblioteca:
            p.append(f"pie.json: la adicional «{c}» no está en referencias.json")
        elif c in basicas:
            p.append(f"pie.json: «{c}» ya es de rol `basica` en Zotero; sobra en `adicionales`")
        if not str((pie["adicionales"][c] or {}).get("motivo", "")).strip():
            p.append(f"pie.json: la adicional «{c}» no dice su `motivo`")
    for c in sorted(sin_alta):
        ficha = pie["sin_alta"][c] or {}
        if c in biblioteca:
            p.append(f"pie.json: «{c}» ya está en referencias.json; su línea fija de `sin_alta` sobra")
        for campo in ("html", "motivo", "para_el_alta"):
            if not str(ficha.get(campo, "")).strip():
                p.append(f"pie.json: la línea sin alta «{c}» no trae `{campo}`")
    if pie["orden"]:
        orden = pie["orden"]
        if len(set(orden)) != len(orden):
            p.append("pie.json: `orden` repite una clave")
        debidas = basicas | adicionales | sin_alta
        for c in sorted(debidas - set(orden)):
            p.append(f"pie.json: «{c}» tiene que estar en el pie y no aparece en `orden`")
        for c in sorted(set(orden) - debidas):
            p.append(f"pie.json: «{c}» está en `orden` y no es básica, ni adicional, ni línea sin alta")
    elif adicionales or sin_alta:
        p.append("pie.json: hay `adicionales` o `sin_alta` y falta `orden`")
    for c, nota in sorted(pie["anotaciones"].items()):
        if c not in biblioteca or c not in claves_del_pie(biblioteca, candado, pie):
            p.append(f"pie.json: la anotación de «{c}» es de una obra que no está en el pie")
        nota = nota or {}
        if not (nota.get("destacado") or nota.get("url")):
            p.append(f"pie.json: la anotación de «{c}» no dice nada (`destacado` o `url`)")
        if nota.get("url") and not (nota.get("rotulo") and nota.get("visible")):
            p.append(f"pie.json: el enlace de la anotación de «{c}» pide `rotulo` y `visible`")
    for veto in pie["vetados"]:
        try:
            re.compile(veto["patron"])
        except (KeyError, TypeError, re.error):
            p.append(f"pie.json: un `vetados` no trae un `patron` que sea expresión regular: {veto!r}")
        if not str((veto or {}).get("motivo", "") if isinstance(veto, dict) else "").strip():
            p.append(f"pie.json: un `vetados` no dice su `motivo`: {veto!r}")
    return p


def lista_pie(entradas: dict[str, str], claves: list[str], pie: dict, sangria: str) -> str:
    """El `<ul>` del pie, con el marcado que el pie ha tenido siempre.

    No es `lista()`: el pie va sobre el verde oscuro de `.usta-header`, y ahí
    un enlace con el color por defecto no se lee. Título y enlaces van en
    `text-gold`; `min-w-0 break-words` deja partir un DOI en el teléfono.
    La clase `pie-referencias` no tiene CSS: es el asa con que el auditor de
    prosa (`audita_texto_base.py`) saca el pie de lo que lee como cifras, igual
    que saca `ul.lista-fuentes`. Sin ella los dígitos de cada DOI salían como
    cifras sin respaldo en los doce documentos.
    """
    s = sangria
    filas = []
    for c in claves:
        fija = c in pie["sin_alta"]
        cuerpo = pie["sin_alta"][c]["html"].strip() if fija else entradas[c]
        cuerpo = cuerpo.replace("<em>", '<em class="text-gold">')
        cuerpo = cuerpo.replace('<a href="', '<a class="underline text-gold" target="_blank" rel="noopener" href="')
        nota = pie["anotaciones"].get(c) or {}
        if nota.get("destacado"):
            cuerpo += f' <strong>{html.escape(nota["destacado"], quote=False)}</strong>'
        if nota.get("url"):
            cuerpo += (f' {html.escape(nota["rotulo"], quote=False)} <a class="underline text-gold" target="_blank" '
                       f'rel="noopener" href="{html.escape(nota["url"], quote=True)}">'
                       f'{html.escape(nota["visible"], quote=False)}</a>.')
        marca = " data-sin-alta" if fija else ""
        filas.append(
            f'\n{s}  <li id="pie-{c}" class="flex items-start gap-2"{marca}>'
            f'\n{s}    <i class="fas fa-bookmark text-secondary mt-1" aria-hidden="true"></i>'
            f'\n{s}    <span class="min-w-0 break-words">{cuerpo}</span>'
            f'\n{s}  </li>'
        )
    return f'\n{s}<ul class="pie-referencias space-y-3 text-white/90 text-sm">{"".join(filas)}\n{s}</ul>\n{s}'


def genera_pie(biblioteca: dict[str, dict], candado: dict[str, dict], sangria: str,
               pie: dict | None = None) -> str:
    """Lo que va entre los dos marcadores del pie."""
    pie = carga_pie() if pie is None else pie
    problemas = problemas_del_pie(biblioteca, candado, pie)
    if problemas:
        raise ErrorDeCita("; ".join(problemas))
    claves = claves_del_pie(biblioteca, candado, pie)
    en_zotero = [c for c in claves if c not in pie["sin_alta"]]
    _, _, entradas = pandoc(biblioteca, en_zotero)
    if not pie["orden"]:
        claves = sorted(claves, key=lambda c: re.sub(r"<[^>]+>", "", entradas[c]).lower())
    return lista_pie(entradas, claves, pie, sangria)


def enlaces_nuevos(entrada: str) -> str:
    """Los enlaces de una entrada abren en pestaña nueva."""
    return entrada.replace('<a href="', '<a target="_blank" rel="noopener" href="')


# --------------------------------------------------------------------------- #
# Citas
# --------------------------------------------------------------------------- #
def atributos_de(texto: str) -> dict[str, str]:
    return {k: html.unescape(v) for k, v in RE_ATRIBUTO.findall(texto)}


def texto_cita(autores: str, anio: str, loc: str, modo: str,
               via: tuple[str, str] | None = None) -> str:
    """El texto visible. Con `via` (cita de segunda mano, norma común v1.1) el
    localizador es de la obra LEÍDA: «(Cressie, 1993, citado en Baddeley et
    al., 2015, p. 4)». La obra original no lleva localizador propio."""
    cola = f", {html.escape(loc, quote=False)}" if loc else ""
    if via:
        cola = f", citado en {via[0]}, {via[1]}{cola}"
    if modo == "narrativa":
        return f"{autores} ({anio}{cola})"
    if modo == "suelta":
        return f"{autores}, {anio}{cola}"
    return f"({autores}, {anio}{cola})"


def claves_citadas(texto: str) -> list[str]:
    vistas: list[str] = []
    for m in RE_CITA.finditer(texto):
        a = atributos_de(m.group("atributos"))
        for clave in (a.get("data-ref", ""), a.get("data-via", "")):
            if clave and clave not in vistas:
                vistas.append(clave)
    return vistas


def lista(entradas: dict[str, str], claves: list[str], prefijo: str, sangria: str) -> str:
    orden = sorted(claves, key=lambda c: re.sub(r"<[^>]+>", "", entradas[c]).lower())
    filas = "".join(
        f'\n{sangria}  <li id="{prefijo}{c}">{enlaces_nuevos(entradas[c])}</li>' for c in orden
    )
    return f'\n{sangria}<ul class="lista-fuentes">{filas}\n{sangria}</ul>\n{sangria}'


def sangria_de(texto: str, posicion: int) -> str:
    inicio = texto.rfind("\n", 0, posicion) + 1
    return re.match(r"[ \t]*", texto[inicio:posicion]).group(0)


def genera(texto: str, biblioteca: dict[str, dict], candado: dict[str, dict]) -> str:
    """El HTML con citas, listas de módulo, lista de capítulo y pie regenerados."""
    citadas = claves_citadas(texto)
    desconocidas = [c for c in citadas if c not in biblioteca]
    if desconocidas:
        raise ErrorDeCita(f"claves que no están en referencias.json: {', '.join(desconocidas)}")
    autores, anios, entradas = pandoc(biblioteca, citadas)

    def modulo(m: re.Match) -> str:
        n, cuerpo = m.group("n"), m.group("cuerpo")

        def cita(c: re.Match) -> str:
            a = atributos_de(c.group("atributos"))
            clave, loc = a.get("data-ref", ""), a.get("data-loc", "")
            modo = a.get("data-modo", "parentesis")
            if modo not in MODOS:
                raise ErrorDeCita(f"data-modo desconocido en la cita de {clave}: «{modo}»")
            titulo = html.escape(re.sub(r"<[^>]+>", "", entradas[clave]).strip(), quote=True)
            via = a.get("data-via")
            if via and via not in entradas:
                raise ErrorDeCita(f"data-via «{via}» no está en referencias.json")
            visible = texto_cita(autores[clave], anios[clave], loc, modo,
                                 (autores[via], anios[via]) if via else None)
            return (f'<cite class="cita"{c.group("atributos")}>'
                    f'<a href="#ref-m{n}-{clave}" title="{titulo}">{visible}</a></cite>')

        cuerpo = RE_CITA.sub(cita, cuerpo)
        del_modulo = claves_citadas(cuerpo)

        def fuentes(f: re.Match) -> str:
            if not del_modulo:
                return f.group("abre") + f.group("cierra")
            s = sangria_de(cuerpo, f.start())
            return (f.group("abre") + lista(entradas, del_modulo, f"ref-m{n}-", s)
                    + f.group("cierra"))

        cuerpo = RE_FUENTES_MODULO.sub(fuentes, cuerpo)
        return m.group("abre") + cuerpo + m.group("cierra")

    texto = RE_MODULO.sub(modulo, texto)

    def capitulo(m: re.Match) -> str:
        if not citadas:
            return m.group("abre") + m.group("cierra")
        s = sangria_de(texto, m.start())
        return m.group("abre") + lista(entradas, citadas, "ref-", s) + m.group("cierra")

    texto = RE_REFS_CAPITULO.sub(capitulo, texto)

    if RE_PIE.search(texto):
        def pie(m: re.Match) -> str:
            s = sangria_de(texto, m.start())
            return m.group("abre") + genera_pie(biblioteca, candado, s) + m.group("cierra")

        texto = RE_PIE.sub(pie, texto)
    return texto


# --------------------------------------------------------------------------- #
def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    ap.add_argument("archivos", nargs="*", type=pathlib.Path)
    ap.add_argument("--comprobar", action="store_true",
                    help="no escribe; sale con 1 si algún archivo quedaría distinto")
    args = ap.parse_args()

    biblioteca, candado = carga_biblioteca()
    falla = False
    for ruta in (args.archivos or CAPITULOS):
        original = ruta.read_text("utf-8")
        try:
            nuevo = genera(original, biblioteca, candado)
        except ErrorDeCita as e:
            print(f"FALLA  {ruta.name}: {e}")
            falla = True
            continue
        n = len(RE_CITA.findall(nuevo))
        if nuevo == original:
            print(f"OK     {ruta.name}: {n} citas, sin cambios")
        elif args.comprobar:
            print(f"FALLA  {ruta.name}: las citas o las listas no están regeneradas")
            falla = True
        else:
            ruta.write_text(nuevo, "utf-8")
            print(f"OK     {ruta.name}: {n} citas, regenerado")
    return 1 if falla else 0


if __name__ == "__main__":
    sys.exit(main())
