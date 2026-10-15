#!/usr/bin/env python3
"""
prueba_ensambla_cap5.py — el capítulo 5 abre el módulo que pide la URL, y la
prueba sabe fallar

Material de Estadística Espacial 2026-II (20929).

POR QUÉ EXISTE. Los enlaces «Leer en el material» de las diapositivas de clase
terminan en `capitulo-5-intensidad-nucleos.html#modulo-N`, y la plantilla no
lee el fragmento: arrancaba siempre en el módulo 1. Nada lo vio. Los trece
enlaces cargaban sin un error en consola, el módulo 1 es una página válida, y
solo `#modulo-1` acertaba —de casualidad—. Se descubrió abriendo el sitio ya
publicado. `ensambla_cap5.py` lo arregla (ver «El arranque de la página»), y
esta prueba es la que hace que el arreglo no se pueda perder en silencio.

QUÉ COMPRUEBA, sobre el capítulo YA ENSAMBLADO (no toca nada: solo lee):

  1. **El arranque ejecutado, no solo leído.** Del HTML publicado se saca el
     `courseData` y el bloque de arranque (`moduloDeLaUrl`, el oyente de
     `DOMContentLoaded` y el de `hashchange`) y se ejecutan en Node con
     `loadModule`, `renderNavigation` y compañía sustituidas por testigos.
     Cada fragmento da el módulo que debe: `#modulo-1`…`#modulo-13`, y el 1
     para todo lo demás (sin fragmento, `#modulo-99`, `#modulo-0`, `#fn1`,
     `#module-5`, `#xmodulo-5`…). Y con la página ya abierta, `hashchange`
     cambia de módulo solo cuando el fragmento es `#modulo-N` de otro módulo:
     ni un ancla cualquiera, ni un módulo que no existe, ni el mismo otra vez
     (que repintaría la página).
  2. **El contrato con las diapositivas.** Cada enlace «Leer en el material»
     de las dos sesiones apunta a `#modulo-N`, N existe en el capítulo, el
     arranque lo resuelve a N, y el título de ese módulo es la etiqueta del
     enlace (que pone el título del módulo al que lleva).
  3. **La llamada fija ya no está.** Una segunda llamada detrás de
     `loadModule(1)` también dejaría los enlaces en el módulo correcto, pero
     marcaría como visto y construiría un módulo que nadie abrió.

LA PRUEBA TAMBIÉN SE PRUEBA. Un `OK` que nadie ha visto fallar puede estar bien
escrito o puede ser incapaz de dispararse (la lección de T0.5, que este
proyecto ya pagó dos veces). Por eso 11 mutantes en memoria del propio
arranque —la llamada fija de vuelta, sin el 1 por omisión, la expresión sin
anclar, sin comprobar que el módulo existe, N como texto, N desplazado, un
`hashchange` que manda al 1 con cualquier ancla…— y todos tienen que fallar.
Un mutante que no cambia el texto (la cadena a mutar ya no está) también es un
fallo: sería inerte.

Uso:  python3 precalculo/prueba_ensambla_cap5.py
      (necesita `node`; sale con 0 solo si todo está en verde)
`audita_todo.sh` la recoge sola: busca `prueba_ensambla_cap${N}.py`.
"""
from __future__ import annotations

import html as _html
import json
import pathlib
import re
import subprocess
import sys

RAIZ = pathlib.Path(__file__).resolve().parent.parent
CAPITULO = RAIZ / "Htmls_Espacial" / "capitulo-5-intensidad-nucleos.html"
DECKS = [RAIZ / "Htmls_Espacial" / "diapositivas" / f"capitulo-5-intensidad-nucleos-sesion-{s}.html"
         for s in (1, 2)]

RE_COURSE = re.compile(r"    const courseData = \{.*?\n    \};\n", re.S)
RE_ARRANQUE = re.compile(
    r"    function moduloDeLaUrl\(\) \{.*?window\.addEventListener\('hashchange', .*?\n    \}\);\n", re.S)

# Fragmentos que NO son #modulo-N de un módulo que existe: la página tiene que abrir el 1.
NO_VALIDOS = ["", "#", "#modulo-", "#modulo-0", "#modulo-14", "#modulo-99", "#modulo--1", "#modulo-5x",
              "#modulo-5/", "#modulo-1e1", "#modulo- 5", "#fn1", "#module-5", "#Modulo-5", "#xmodulo-5",
              "#a-modulo-5", "#a#modulo-5", "#modulo-5#"]

# Con la página abierta: (fragmento nuevo, llamadas a loadModule que debe provocar). El módulo
# actual arranca en el 1 y cada `loadModule` lo actualiza, como en la página.
SECUENCIA_HASHCHANGE = [
    ("#modulo-7", ["load:7"]),
    ("#modulo-7", []),            # el mismo otra vez: no repinta
    ("#fn1", []),                 # un ancla cualquiera no cambia de módulo (tampoco al 1)
    ("#modulo-99", []),           # un módulo que no existe, tampoco
    ("#modulo-3", ["load:3"]),
    ("", []),                     # sin fragmento (ir atrás hasta la entrada inicial): se queda donde está
    ("#modulo-13", ["load:13"]),
    ("#modulo-1", ["load:1"]),
]

PROGRAMA_NODE = r"""
const vm = require('vm');
const [courseSrc, arranqueSrc, hashes, secuencia] = JSON.parse(require('fs').readFileSync(0, 'utf8'));
function nuevo() {
  const llamadas = [], oyentes = { doc: {}, win: {} };
  const ctx = { location: { hash: '' }, currentModuleId: 1, llamadas, oyentes };
  ctx.renderNavigation = () => llamadas.push('nav');
  ctx.loadModule = id => { llamadas.push('load:' + id); ctx.currentModuleId = id; };
  ctx.setupEventListeners = () => llamadas.push('setup');
  ctx.document = { addEventListener: (ev, fn) => { oyentes.doc[ev] = fn; } };
  ctx.window = { addEventListener: (ev, fn) => { oyentes.win[ev] = fn; } };
  vm.createContext(ctx);
  vm.runInContext(courseSrc + '\n' + arranqueSrc, ctx);
  return ctx;
}
const sal = { modulos: null, carga: [], cambios: [], errores: [] };
try {
  const base = nuevo();
  sal.modulos = vm.runInContext('courseData.modules.map(m => ({ id: m.id, title: m.title }))', base);
  for (const h of hashes) {
    const ctx = nuevo();
    ctx.location.hash = h;
    const f = ctx.oyentes.doc['DOMContentLoaded'];
    if (!f) { sal.carga.push({ hash: h, error: 'sin oyente de DOMContentLoaded' }); continue; }
    f();
    sal.carga.push({ hash: h, llamadas: ctx.llamadas.slice() });
  }
  const ctx = nuevo();
  ctx.location.hash = '';
  ctx.oyentes.doc['DOMContentLoaded']();
  ctx.llamadas.length = 0;
  for (const [h] of secuencia) {
    ctx.location.hash = h;
    const f = ctx.oyentes.win['hashchange'];
    if (!f) { sal.cambios.push({ hash: h, error: 'sin oyente de hashchange' }); continue; }
    ctx.llamadas.length = 0;
    f();
    sal.cambios.push({ hash: h, llamadas: ctx.llamadas.slice() });
  }
} catch (e) { sal.errores.push(String(e)); }
process.stdout.write(JSON.stringify(sal));
"""


def norma(s: str) -> str:
    s = _html.unescape(re.sub(r"<[^>]+>", "", _html.unescape(s or "")))
    return re.sub(r"\s+", " ", s).strip()


def enlaces_de_las_diapositivas() -> list[tuple[str, str, int | None, str]]:
    sal = []
    for d in DECKS:
        if not d.exists():
            continue
        t = d.read_text(encoding="utf-8")
        for a in re.findall(r'<a class="enlace-material"[^>]*>.*?</a>', t, flags=re.S):
            href = re.search(r'href="([^"]+)"', a).group(1)
            m = re.fullmatch(r"\.\./capitulo-5-intensidad-nucleos\.html#modulo-(\d+)", href)
            etiqueta = norma(a).replace("Leer en el material:", "").strip()
            sal.append((d.name, href, int(m.group(1)) if m else None, etiqueta))
    return sal


def ejecuta(doc: str, hashes: list[str]):
    """Ejecuta en Node el arranque del documento. Devuelve (salida, defectos de extracción)."""
    mc, ma = RE_COURSE.search(doc), RE_ARRANQUE.search(doc)
    if not mc:
        return None, ["no encuentro el `const courseData = {…};` del capítulo"]
    if not ma:
        return None, ["no encuentro el bloque de arranque (moduloDeLaUrl + DOMContentLoaded + hashchange)"]
    entrada = json.dumps([mc.group(0), ma.group(0), hashes, SECUENCIA_HASHCHANGE])
    r = subprocess.run(["node", "-e", PROGRAMA_NODE], input=entrada, capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit(f"PARADO: node falló\n{r.stderr}")
    return json.loads(r.stdout), []


def defectos(doc: str, enlaces) -> list[str]:
    malos: list[str] = []
    if doc.count("function moduloDeLaUrl()") != 1:
        malos.append(f"`function moduloDeLaUrl()` aparece {doc.count('function moduloDeLaUrl()')} veces y debe ser 1")
    if re.search(r"renderNavigation\(\);\s*loadModule\(1\);", doc):
        malos.append("el arranque sigue llamando a `loadModule(1)` a pelo")
    mc = RE_COURSE.search(doc)
    ids = sorted({int(i) for i in re.findall(r"\{ id: (\d+), title:", mc.group(0))}) if mc else []
    validos = [f"#modulo-{k}" for k in ids]
    hashes = validos + NO_VALIDOS + [f"#modulo-{n}" for (_, _, n, _) in enlaces if n is not None]
    salida, previos = ejecuta(doc, hashes)
    if previos:
        return malos + previos
    for e in salida["errores"]:
        malos.append(f"al ejecutar el arranque: {e}")
    if not ids:
        malos.append("el `courseData` no trae módulos")
    # 1. cada fragmento, con el capítulo recién cargado
    for r in salida["carga"]:
        h = r["hash"]
        if "error" in r:
            malos.append(f"carga con «{h}»: {r['error']}")
            continue
        esperado = int(h.rsplit("-", 1)[1]) if h in validos else 1
        if r["llamadas"] != ["nav", f"load:{esperado}", "setup"]:
            malos.append(f"carga con «{h}»: llamó a {r['llamadas']} y debía abrir el módulo {esperado} "
                         f"(['nav', 'load:{esperado}', 'setup'])")
    # 2. con la página abierta
    for (h, esperado), r in zip(SECUENCIA_HASHCHANGE, salida["cambios"]):
        if "error" in r:
            malos.append(f"hashchange a «{h}»: {r['error']}")
        elif r["llamadas"] != esperado:
            malos.append(f"hashchange a «{h}»: llamó a {r['llamadas']} y debía llamar a {esperado}")
    # 3. el contrato con las diapositivas
    titulos = {m["id"]: norma(m["title"]) for m in (salida["modulos"] or [])}
    resueltos = {r["hash"]: r.get("llamadas") for r in salida["carga"]}
    for deck, href, n, etiqueta in enlaces:
        if n is None:
            malos.append(f"{deck}: el enlace «{href}» ya no tiene la forma ../capitulo-5-…html#modulo-N")
        elif n not in titulos:
            malos.append(f"{deck}: {href} apunta a un módulo que el capítulo no tiene")
        else:
            if resueltos.get(f"#modulo-{n}") != ["nav", f"load:{n}", "setup"]:
                malos.append(f"{deck}: {href} no abre el módulo {n} ({resueltos.get(f'#modulo-{n}')})")
            if etiqueta != titulos[n]:
                malos.append(f"{deck}: {href} dice «{etiqueta}» y el módulo {n} se titula «{titulos[n]}»")
    return malos


# (nombre, texto que aparece UNA vez en el arranque, su sustituto)
MUTANTES = [
    ("la llamada fija de la plantilla, de vuelta",
     "loadModule(moduloDeLaUrl() || 1);", "loadModule(1);"),
    ("sin el 1 por omisión",
     "loadModule(moduloDeLaUrl() || 1);", "loadModule(moduloDeLaUrl());"),
    ("dos llamadas: la fija y la del fragmento",
     "loadModule(moduloDeLaUrl() || 1);", "loadModule(1);\n      loadModule(moduloDeLaUrl() || 1);"),
    ("expresión regular sin anclar",
     r"/^#modulo-(\d+)$/", r"/#modulo-(\d+)/"),
    ("sin comprobar que el módulo existe",
     "return courseData.modules.some(mod => mod.id === id) ? id : 0;", "return id;"),
    ("N como texto (el === de los ids nunca acierta)",
     "Number(m[1])", "m[1]"),
    ("N desplazado en uno",
     "Number(m[1])", "Number(m[1]) + 1"),
    ("hashchange que no comprueba el fragmento",
     "if (id && id !== currentModuleId) loadModule(id);", "loadModule(id);"),
    ("hashchange que repinta el mismo módulo",
     "if (id && id !== currentModuleId) loadModule(id);", "if (id) loadModule(id);"),
    ("hashchange que manda al 1 con cualquier ancla",
     "const id = moduloDeLaUrl();\n      if (id && id !== currentModuleId) loadModule(id);",
     "const id = moduloDeLaUrl() || 1;\n      if (id !== currentModuleId) loadModule(id);"),
    ("sin oyente de hashchange",
     "window.addEventListener('hashchange', () => {", "window.addEventListener('resize', () => {"),
]


def main() -> int:
    if not CAPITULO.exists():
        sys.exit(f"PARADO: no existe {CAPITULO.relative_to(RAIZ)}; ensámblalo con ensambla_cap5.py")
    doc = CAPITULO.read_text(encoding="utf-8")
    enlaces = enlaces_de_las_diapositivas()
    print("=== prueba_ensambla_cap5.py — el capítulo 5 abre el módulo que pide la URL ===")
    print(f"  {len(enlaces)} enlaces «Leer en el material» en {len(DECKS)} sesiones"
          + ("" if enlaces else " (no hay diapositivas que cotejar)"))

    malos = defectos(doc, enlaces)
    for m in malos:
        print(f"  MAL  {m}")
    if not malos:
        print("  OK   el capítulo publicado: el arranque lee #modulo-N, lo ejecuta bien en todos los casos y "
              "cumple con los enlaces")

    cazados, colados, inertes = 0, [], []
    for nombre, viejo, nuevo in MUTANTES:
        if doc.count(viejo) != 1:
            inertes.append(nombre)
            print(f"  INERTE  «{nombre}»: la cadena a mutar aparece {doc.count(viejo)} veces y debía ser 1")
            continue
        mutado = doc.replace(viejo, nuevo)
        falla = defectos(mutado, enlaces)
        if falla:
            cazados += 1
            print(f"  OK   mutante «{nombre}» cazado ({len(falla)} defecto(s); p. ej.: {falla[0][:70]}…)")
        else:
            colados.append(nombre)
            print(f"  MAL  mutante «{nombre}» NO se cazó: la prueba no distingue ese defecto")

    print("\n" + "=" * 70)
    print(f"  {cazados} de {len(MUTANTES)} mutantes cazados"
          + (f" · {len(inertes)} inerte(s)" if inertes else "") + (f" · {len(colados)} colado(s)" if colados else ""))
    print("=" * 70)
    ok = not malos and not colados and not inertes
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
