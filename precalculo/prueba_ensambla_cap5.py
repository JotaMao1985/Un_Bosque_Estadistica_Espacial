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

  4. **Las guardas del módulo 3 saben parar** (2026-11-03). El módulo enseña la
     curva del criterio de cada selector y abre con dos sedes de Kennedy, y lo que
     sus frases afirman de la forma («la apiñada pide un σ menor», «la suma de
     bw.CvL sube sin vaivenes», «bw.diggle no vuelve a subir»…) lo comprueba
     `ensambla_cap5.py` contra el dato. Aquí el ensamblador se ejecuta en copia,
     con `CAP5_DESTINO` fuera de lo publicado, con UN dato que deja una frase en
     falso cada vez, y cada copia tiene que salir con error y nombrar la frase.

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
import os
import pathlib
import re
import subprocess
import sys
import tempfile

RAIZ = pathlib.Path(__file__).resolve().parent.parent
CAPITULO = RAIZ / "Htmls_Espacial" / "capitulo-5-intensidad-nucleos.html"
ENSAMBLADOR = RAIZ / "precalculo" / "ensambla_cap5.py"
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


# LAS GUARDAS DEL MÓDULO 3 (2026-11-03). Cada mutante inyecta un dato justo
# después de que el ensamblador arme sus atajos a `m3.curvas`, y deja en falso
# UNA frase del módulo; la guarda tiene que parar y nombrarla. (nombre, dato
# inyectado, lo que la salida tiene que decir.)
TRAS_LOS_ATAJOS = ('            key=lambda i: abs(_CK["cvl"]["nodos16_m"][i] - SEL_K["CvL"]))\n')
MUTANTES_MODULO3 = [
    ("la apiñada marca algo con los dos anchos más pequeños",
     '_API["marca16_km2"][1] = 5.0', "ni siquiera ella marca"),
    ("la marca de la apiñada no baja con σ grande",
     '_API["marca16_km2"][-1] = 36.0', "su marca baja"),
    ("la aislada marca algo lejos de su vecina",
     '_AIS["marca16_km2"][5] = 1.0', "marca casi cero"),
    ("las dos marcas no se juntan con σ de kilómetros",
     '_AIS["marca16_km2"][-1] = 1.0', "se juntan"),
    ("la apiñada pide más que la suma",
     '_API["pide_m"] = 900.0', "la apiñada pide un σ menor"),
    ("la aislada con vecinas a menos de 300 m",
     '_AIS["vecinas_300m"] = 2', "a menos de 300 m"),
    ("piden un σ distinto más sedes de las que hay",
     '_EJ["piden_mas"] = 200', "más sedes de las que hay"),
    ("un -inf en medio de la rejilla",
     '_CK["ppl"]["cv16"][5] = None', "no tienen nota"),
    ("menos sedes piden el mínimo que gemelas hay",
     '_EJ["piden_el_minimo"] = 3', "las gemelas"),
    ("la suma de bw.CvL baja en un ancho",
     '_CK["cvl"]["suma16_km2"][8] = 1.0', "sin vaivenes"),
    ("bw.CvL devuelve un ancho lejos del cruce",
     '_ICVL = 3', "el que más se acerca"),
    ("bw.diggle vuelve a subir sobre Kennedy",
     '_CK["diggle"]["subida_final_pct"] = 12.0', "no vuelve a subir"),
    ("bw.diggle no sube sobre la ciudad",
     '_CC["diggle"]["subida_final_pct"] = 5.0', "la curva sí sube"),
    ("el mínimo de bw.diggle fuera de la sierra",
     '_CK["diggle"]["meseta_desde_m"] = 400', "diente de la sierra"),
    ("la nota de los pinos baja en un ancho",
     '_PN["cv16"][9] = 100.0', "hasta el último"),
    ("con el intervalo ampliado devuelve otra cosa",
     '_PN["ampliado"]["devuelve"] = 1.5', "otra vez el final"),
    ("la ciudad elige un ancho de -inf",
     '_CC["ppl"]["infinito_hasta_m"] = 300.0', "elige entre los que quedan"),
]

# La copia vive en un directorio temporal: sus dos rutas relativas a
# `__file__` se fijan al árbol de verdad, y la salida va a `CAP5_DESTINO`.
RUTAS_DE_LA_COPIA = [
    ("RAIZ = pathlib.Path(__file__).resolve().parent.parent",
     f"RAIZ = pathlib.Path({str(RAIZ)!r})"),
    ("sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))",
     f"sys.path.insert(0, {str(RAIZ / 'precalculo')!r})"),
]


def ensambla_en_copia(fuente: str, tmp: pathlib.Path) -> tuple[int, str]:
    for viejo, nuevo in RUTAS_DE_LA_COPIA:
        fuente = fuente.replace(viejo, nuevo)
    copia = tmp / "ensambla_cap5.py"
    copia.write_text(fuente, encoding="utf-8")
    entorno = dict(os.environ, CAP5_DESTINO=str(tmp / "salida.html"),
                   PYTHONPATH=str(RAIZ / "precalculo"))
    r = subprocess.run([sys.executable, str(copia)], cwd=RAIZ, env=entorno,
                       capture_output=True, text=True, timeout=600)
    return r.returncode, r.stdout + r.stderr


def prueba_modulo3() -> tuple[int, list[str], list[str]]:
    """(cazados, colados, inertes) de los mutantes de las guardas del módulo 3."""
    fuente = ENSAMBLADOR.read_text(encoding="utf-8")
    cazados, colados, inertes = 0, [], []
    for viejo, _ in RUTAS_DE_LA_COPIA:
        if fuente.count(viejo) != 1:
            print(f"  MAL  la copia del ensamblador no se puede fijar al árbol: «{viejo}» "
                  f"aparece {fuente.count(viejo)} veces")
            return 0, ["la copia"], []
    if fuente.count(TRAS_LOS_ATAJOS) != 1:
        print(f"  INERTE  el punto donde se inyectan los datos aparece {fuente.count(TRAS_LOS_ATAJOS)} veces")
        return 0, [], [m[0] for m in MUTANTES_MODULO3]
    with tempfile.TemporaryDirectory(prefix="prueba_ensambla_cap5_") as d:
        tmp = pathlib.Path(d)
        # Control: la copia sin mutar sale limpia. Si no, un «cazado» no diría nada.
        cod, sal = ensambla_en_copia(fuente, tmp)
        if cod != 0:
            print("  MAL  la copia del ensamblador SIN mutar no sale limpia; los mutantes no medirían nada")
            print("       " + sal[-400:].replace("\n", "\n       "))
            return 0, ["el control"], []
        print("  OK   control: la copia sin mutar ensambla limpia fuera de lo publicado")
        for nombre, dato, espera in MUTANTES_MODULO3:
            cod, sal = ensambla_en_copia(fuente.replace(TRAS_LOS_ATAJOS, TRAS_LOS_ATAJOS + dato + "\n"), tmp)
            linea = next((l.strip() for l in sal.splitlines() if espera in l), None)
            if cod != 0 and linea:
                cazados += 1
                print(f"  OK   mutante «{nombre}» para el ensamblado: {linea[:90]}")
            else:
                colados.append(nombre)
                print(f"  MAL  mutante «{nombre}» NO para el ensamblado (código {cod}; "
                      f"la salida no dice «{espera}»)")
    return cazados, colados, inertes


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

    print("\n  Módulo 3: las guardas de la forma de las curvas, rotas de una en una")
    publicado_antes = CAPITULO.read_bytes()
    m_cazados, m_colados, m_inertes = prueba_modulo3()
    if CAPITULO.read_bytes() != publicado_antes:
        malos.append("el capítulo publicado cambió durante los mutantes: CAP5_DESTINO no lo protegió")
        print(f"  MAL  {malos[-1]}")

    print("\n" + "=" * 70)
    print(f"  {cazados} de {len(MUTANTES)} mutantes del arranque cazados"
          + (f" · {len(inertes)} inerte(s)" if inertes else "") + (f" · {len(colados)} colado(s)" if colados else ""))
    print(f"  {m_cazados} de {len(MUTANTES_MODULO3)} mutantes del módulo 3 paran el ensamblado"
          + (f" · {len(m_inertes)} inerte(s)" if m_inertes else "")
          + (f" · {len(m_colados)} colado(s)" if m_colados else ""))
    print("=" * 70)
    ok = not malos and not colados and not inertes and not m_colados and not m_inertes
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
